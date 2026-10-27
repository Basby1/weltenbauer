package de.basby.weltenbauer.arbeit;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.HoverEvent;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.server.ServerLifecycleHooks;

import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * Führt immer genau einen Auftrag gleichzeitig aus, verteilt auf die Server-Ticks,
 * zeigt den Fortschritt an und kümmert sich um Rückgängig/Wiederholen.
 */
public final class Auftragsverwaltung {

    /** So viel Zeit pro Tick (in Millisekunden) darf Weltenbauer höchstens arbeiten. */
    private static final long MS_PRO_TICK = 15;
    /** Ab so vielen Chunks wird vorher nachgefragt. */
    public static final int NACHFRAGEN_AB_CHUNKS = 400;

    private static Auftrag aktuell;
    private static int ticks;

    private record Ausstehend(Supplier<Auftrag> auftrag, int ablaufTick) {
    }

    private static final Map<UUID, Ausstehend> AUSSTEHEND = new HashMap<>();

    private Auftragsverwaltung() {
    }

    public static boolean laeuft() {
        return aktuell != null;
    }

    public static Auftrag aktuell() {
        return aktuell;
    }

    /** Startet einen Auftrag sofort. */
    public static void starte(Auftrag auftrag) {
        aktuell = auftrag;
        ticks = 0;
        melde(auftrag.besitzer(), Component.literal("Weltenbauer: ").withStyle(ChatFormatting.GOLD)
                .append(Component.literal(auftrag.titel() + " gestartet – " + zahl(auftrag.chunksGesamt())
                        + " Chunks. Fortschritt siehst du über der Schnellleiste.").withStyle(ChatFormatting.WHITE)), false);
    }

    /** Merkt sich einen großen Auftrag, bis der Spieler ihn bestätigt. */
    public static void nachfragen(ServerPlayer spieler, Supplier<Auftrag> auftrag, String beschreibung, int chunks) {
        MinecraftServer server = spieler.getServer();
        int ablauf = (server != null ? server.getTickCount() : 0) + 20 * 60;
        AUSSTEHEND.put(spieler.getUUID(), new Ausstehend(auftrag, ablauf));
        MutableComponent text = Component.literal("Weltenbauer: ").withStyle(ChatFormatting.GOLD)
                .append(Component.literal(beschreibung + " betrifft ca. " + zahl(chunks)
                        + " Chunks und kann einige Minuten dauern. ").withStyle(ChatFormatting.WHITE))
                .append(knopf("[Bestätigen]", "/wb bestaetigen", "Jetzt starten", ChatFormatting.GREEN))
                .append(Component.literal(" "))
                .append(knopf("[Abbrechen]", "/wb abbrechen", "Doch nicht", ChatFormatting.RED));
        spieler.sendSystemMessage(text);
    }

    /** Führt den ausstehenden Auftrag des Spielers aus. @return false, wenn nichts aussteht */
    public static boolean bestaetigen(ServerPlayer spieler) {
        Ausstehend a = AUSSTEHEND.remove(spieler.getUUID());
        MinecraftServer server = spieler.getServer();
        if (a == null || server == null || server.getTickCount() > a.ablaufTick()) {
            return false;
        }
        starte(a.auftrag().get());
        return true;
    }

    public static boolean ausstehendVerwerfen(ServerPlayer spieler) {
        return AUSSTEHEND.remove(spieler.getUUID()) != null;
    }

    /** Wird jeden Server-Tick aufgerufen. */
    public static void tick() {
        if (aktuell == null) {
            return;
        }
        aktuell.arbeite(System.nanoTime() + MS_PRO_TICK * 1_000_000L);
        ticks++;
        if (ticks % 20 == 0 && !aktuell.fertig()) {
            ServerPlayer spieler = spieler(aktuell.besitzer());
            if (spieler != null) {
                spieler.displayClientMessage(Component.literal(aktuell.titel() + " … " + aktuell.anteilProzent()
                        + " %  (" + zahl(aktuell.chunksFertig()) + " / " + zahl(aktuell.chunksGesamt())
                        + " Chunks, " + zahl(aktuell.geaendert()) + " Blöcke geändert)").withStyle(ChatFormatting.GOLD), true);
            }
        }
        if (aktuell.fertig()) {
            abschliessen(aktuell);
            aktuell = null;
        }
    }

    /** Bricht den laufenden Auftrag ab; schon Geändertes bleibt rückgängig machbar. */
    public static boolean abbrechen() {
        if (aktuell == null) {
            return false;
        }
        aktuell.abbrechen();
        abschliessen(aktuell);
        aktuell = null;
        return true;
    }

    public static void serverStoppt() {
        if (aktuell != null) {
            aktuell.abbrechen();
            abschliessen(aktuell);
            aktuell = null;
        }
        AUSSTEHEND.clear();
    }

    private static void abschliessen(Auftrag auftrag) {
        MinecraftServer server = auftrag.level().getServer();
        UUID wer = auftrag.besitzer();
        boolean gespeichert = true;

        if (auftrag instanceof WiederherstellAuftrag w) {
            // Rückgängig → das Gegenteil wandert auf den Wiederholen-Stapel und umgekehrt
            Verlauf.Stapel ziel = w.richtung() == WiederherstellAuftrag.Richtung.RUECKGAENGIG
                    ? Verlauf.Stapel.WIEDERHOLEN : Verlauf.Stapel.RUECKGAENGIG;
            gespeichert = Verlauf.ablegen(server, wer, ziel, auftrag.protokoll());
        } else if (!auftrag.protokoll().istLeer()) {
            gespeichert = Verlauf.ablegen(server, wer, Verlauf.Stapel.RUECKGAENGIG, auftrag.protokoll());
            Verlauf.leeren(server, wer, Verlauf.Stapel.WIEDERHOLEN);
        }

        MutableComponent text = Component.literal("Weltenbauer: ").withStyle(ChatFormatting.GOLD);
        String wort = auftrag.wurdeAbgebrochen() ? " abgebrochen" : " fertig";
        text.append(Component.literal(auftrag.titel() + wort + " – " + zahl(auftrag.geaendert())
                + " Blöcke geändert.").withStyle(ChatFormatting.WHITE));
        if (auftrag.geschuetzt() > 0) {
            text.append(Component.literal(" " + zahl(auftrag.geschuetzt())
                    + " Blöcke mit Inhalt (Truhen, Maschinen …) wurden geschützt.").withStyle(ChatFormatting.GRAY));
        }
        if (auftrag.nichtWiederherstellbar() > 0) {
            text.append(Component.literal(" " + zahl(auftrag.nichtWiederherstellbar())
                    + " Blöcke konnten nicht umgewandelt werden und blieben unverändert.").withStyle(ChatFormatting.GRAY));
        }
        if (auftrag.chunksUebersprungen() > 0) {
            text.append(Component.literal(" " + zahl(auftrag.chunksUebersprungen())
                    + " Chunks konnten nicht geladen werden.").withStyle(ChatFormatting.GRAY));
        }
        if (auftrag.protokoll().istVoll()) {
            text.append(Component.literal(" Achtung: Die Aktion war so groß, dass nur ein Teil rückgängig gemacht werden kann.")
                    .withStyle(ChatFormatting.RED));
        }
        if (!gespeichert) {
            text.append(Component.literal(" Der Rückgängig-Verlauf konnte nicht gespeichert werden.").withStyle(ChatFormatting.RED));
        }
        if (auftrag.geaendert() > 0) {
            text.append(Component.literal(" "));
            if (auftrag instanceof WiederherstellAuftrag w && w.richtung() == WiederherstellAuftrag.Richtung.RUECKGAENGIG) {
                text.append(knopf("[Wiederholen]", "/wb wiederholen", "Die Änderung erneut ausführen", ChatFormatting.AQUA));
            } else {
                text.append(knopf("[Rückgängig]", "/wb rueckgaengig", "Die Änderung zurücknehmen", ChatFormatting.AQUA));
            }
        }
        melde(wer, text, false);
    }

    // ------------------------------------------------------------------ Hilfen

    private static ServerPlayer spieler(UUID id) {
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        return server == null ? null : server.getPlayerList().getPlayer(id);
    }

    private static void melde(UUID wer, Component text, boolean aktionsleiste) {
        ServerPlayer spieler = spieler(wer);
        if (spieler != null) {
            if (aktionsleiste) {
                spieler.displayClientMessage(text, true);
            } else {
                spieler.sendSystemMessage(text);
            }
        }
    }

    public static MutableComponent knopf(String text, String befehl, String hinweis, ChatFormatting farbe) {
        return Component.literal(text).withStyle(stil -> stil.withColor(farbe)
                .withClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND, befehl))
                .withHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, Component.literal(hinweis))));
    }

    public static String zahl(long n) {
        return String.format(Locale.GERMANY, "%,d", n);
    }
}

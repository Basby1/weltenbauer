package de.basby.weltenbauer.befehle;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.builder.ArgumentBuilder;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.mojang.brigadier.exceptions.SimpleCommandExceptionType;
import de.basby.weltenbauer.Auswahl;
import de.basby.weltenbauer.Weltenbauer;
import de.basby.weltenbauer.arbeit.Aktionen;
import de.basby.weltenbauer.arbeit.Auftrag;
import de.basby.weltenbauer.arbeit.Auftragsverwaltung;
import de.basby.weltenbauer.arbeit.BlockAuftrag;
import de.basby.weltenbauer.arbeit.GlaettAuftrag;
import de.basby.weltenbauer.arbeit.Bereich;
import de.basby.weltenbauer.arbeit.Protokoll;
import de.basby.weltenbauer.arbeit.Verlauf;
import de.basby.weltenbauer.arbeit.WiederherstellAuftrag;
import de.basby.weltenbauer.vorlagen.VorlagenBefehle;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandBuildContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.blocks.BlockInput;
import net.minecraft.commands.arguments.blocks.BlockStateArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.Vec3;

import java.util.function.Supplier;

/**
 * Alle Befehle von Weltenbauer. Sie beginnen mit /wb.
 *
 * Erlaubt für Operatoren (Cheats an) und – im Einzelspieler – immer für den Besitzer der Welt,
 * damit man z. B. den Schnee auch in einer Survival-Welt ohne Cheats entfernen kann.
 */
public final class WbBefehle {

    private static final int MAX_RADIUS = 3000;

    private static final SimpleCommandExceptionType KEINE_AUSWAHL = new SimpleCommandExceptionType(
            Component.literal("Es ist noch kein Bereich markiert. Nimm den Terraforming-Stab (/wb stab): "
                    + "Rechtsklick = Ecke 1, Schleichen + Rechtsklick = Ecke 2."));
    private static final SimpleCommandExceptionType ANDERE_DIMENSION = new SimpleCommandExceptionType(
            Component.literal("Die markierte Auswahl liegt in einer anderen Dimension."));

    private WbBefehle() {
    }

    @FunctionalInterface
    private interface MitBereich {
        int los(CommandContext<CommandSourceStack> ctx, Bereich bereich) throws CommandSyntaxException;
    }

    public static void registrieren(CommandDispatcher<CommandSourceStack> dispatcher, CommandBuildContext kontext) {
        dispatcher.register(Commands.literal("wb")
                .requires(WbBefehle::darf)
                .executes(WbBefehle::hilfe)
                .then(Commands.literal("hilfe").executes(WbBefehle::hilfe))

                // /wb schnee entfernen <radius>|auswahl [alles]
                .then(Commands.literal("schnee").then(Commands.literal("entfernen")
                        .then(Commands.argument("radius", IntegerArgumentType.integer(1, MAX_RADIUS))
                                .executes(c -> schnee(c, kreis(c), false))
                                .then(Commands.literal("alles").executes(c -> schnee(c, kreis(c), true))))
                        .then(Commands.literal("auswahl")
                                .executes(c -> schnee(c, auswahl(c), false))
                                .then(Commands.literal("alles").executes(c -> schnee(c, auswahl(c), true))))))

                // /wb eis auftauen <radius>|auswahl
                .then(Commands.literal("eis").then(mitBereich(Commands.literal("auftauen"),
                        (c, b) -> starte(c, "Eis auftauen", b, Aktionen.eisAuftauen()))))

                // /wb laub aufraeumen <radius>|auswahl
                .then(Commands.literal("laub").then(mitBereich(Commands.literal("aufraeumen"),
                        (c, b) -> starte(c, "Laub aufräumen", b, Aktionen.laubAufraeumen()))))

                // /wb entfernen <block> <radius>|auswahl
                .then(Commands.literal("entfernen").then(mitBereich(
                        Commands.argument("block", BlockStateArgument.block(kontext)),
                        (c, b) -> {
                            Block sorte = BlockStateArgument.getBlock(c, "block").getState().getBlock();
                            return starte(c, "Entfernen (" + sorte.getName().getString() + ")", b, Aktionen.entfernen(sorte));
                        })))

                // /wb ersetzen <von> <zu> <radius>|auswahl
                .then(Commands.literal("ersetzen").then(Commands.argument("von", BlockStateArgument.block(kontext))
                        .then(mitBereich(Commands.argument("zu", BlockStateArgument.block(kontext)),
                                (c, b) -> {
                                    Block von = BlockStateArgument.getBlock(c, "von").getState().getBlock();
                                    BlockInput zu = BlockStateArgument.getBlock(c, "zu");
                                    return starte(c, "Ersetzen (" + von.getName().getString() + " → "
                                                    + zu.getState().getBlock().getName().getString() + ")", b,
                                            Aktionen.ersetzen(von, zu.getState(), zu.getDefinedProperties()));
                                }))))

                // /wb glaetten <radius>|auswahl [staerke]
                .then(Commands.literal("glaetten")
                        .then(Commands.argument("radius", IntegerArgumentType.integer(3, 256))
                                .executes(c -> glaetten(c, kreis(c), 3))
                                .then(Commands.argument("staerke", IntegerArgumentType.integer(1, 10))
                                        .executes(c -> glaetten(c, kreis(c), IntegerArgumentType.getInteger(c, "staerke")))))
                        .then(Commands.literal("auswahl")
                                .executes(c -> glaetten(c, auswahl(c), 3))
                                .then(Commands.argument("staerke", IntegerArgumentType.integer(1, 10))
                                        .executes(c -> glaetten(c, auswahl(c), IntegerArgumentType.getInteger(c, "staerke"))))))

                // Vorlagen (Bäume, Ruinen, Felsen, Schildkröten-Insel …)
                .then(VorlagenBefehle.knoten())

                // Verlauf
                .then(Commands.literal("rueckgaengig").executes(WbBefehle::rueckgaengig))
                .then(Commands.literal("undo").executes(WbBefehle::rueckgaengig))
                .then(Commands.literal("wiederholen").executes(WbBefehle::wiederholen))
                .then(Commands.literal("redo").executes(WbBefehle::wiederholen))

                // Steuerung
                .then(Commands.literal("bestaetigen").executes(WbBefehle::bestaetigen))
                .then(Commands.literal("abbrechen").executes(WbBefehle::abbrechen))
                .then(Commands.literal("status").executes(WbBefehle::status))

                // Stab & Auswahl
                .then(Commands.literal("stab").executes(WbBefehle::stab))
                .then(Commands.literal("auswahl")
                        .executes(WbBefehle::auswahlZeigen)
                        .then(Commands.literal("leeren").executes(WbBefehle::auswahlLeeren)))
        );
    }

    /** Hängt an einen Knoten die beiden Varianten „<radius>" und „auswahl" an. */
    private static ArgumentBuilder<CommandSourceStack, ?> mitBereich(ArgumentBuilder<CommandSourceStack, ?> knoten,
                                                                     MitBereich ausfuehrung) {
        return knoten
                .then(Commands.argument("radius", IntegerArgumentType.integer(1, MAX_RADIUS))
                        .executes(c -> ausfuehrung.los(c, kreis(c))))
                .then(Commands.literal("auswahl")
                        .executes(c -> ausfuehrung.los(c, auswahl(c))));
    }

    // ------------------------------------------------------------------ Berechtigung & Bereiche

    private static boolean darf(CommandSourceStack quelle) {
        if (quelle.hasPermission(2)) {
            return true;
        }
        MinecraftServer server = quelle.getServer();
        return server.isSingleplayer() && quelle.getEntity() instanceof ServerPlayer spieler
                && server.isSingleplayerOwner(spieler.getGameProfile());
    }

    private static Bereich kreis(CommandContext<CommandSourceStack> c) {
        ServerLevel level = c.getSource().getLevel();
        Vec3 p = c.getSource().getPosition();
        int radius = IntegerArgumentType.getInteger(c, "radius");
        return new Bereich.Kreis((int) Math.floor(p.x), (int) Math.floor(p.z), radius,
                level.getMinBuildHeight(), level.getMaxBuildHeight() - 1);
    }

    private static Bereich auswahl(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        ServerPlayer spieler = c.getSource().getPlayerOrException();
        Auswahl.Ecken e = Auswahl.von(spieler);
        if (e == null || !e.vollstaendig()) {
            throw KEINE_AUSWAHL.create();
        }
        if (!e.dimension().equals(spieler.level().dimension())) {
            throw ANDERE_DIMENSION.create();
        }
        return Bereich.Quader.aus(e.ecke1(), e.ecke2());
    }

    // ------------------------------------------------------------------ Aufträge starten

    private static int schnee(CommandContext<CommandSourceStack> c, Bereich bereich, boolean alles) throws CommandSyntaxException {
        return starte(c, alles ? "Schnee entfernen (inkl. Schneeblöcke)" : "Schnee entfernen", bereich, Aktionen.schnee(alles));
    }

    private static int starte(CommandContext<CommandSourceStack> c, String titel, Bereich bereich,
                              BlockAuftrag.Aktion aktion) throws CommandSyntaxException {
        CommandSourceStack quelle = c.getSource();
        if (Auftragsverwaltung.laeuft()) {
            quelle.sendFailure(Component.literal("Es läuft schon: " + Auftragsverwaltung.aktuell().titel()
                    + ". Warte, bis es fertig ist, oder brich es mit /wb abbrechen ab."));
            return 0;
        }
        ServerPlayer spieler = quelle.getPlayerOrException();
        ServerLevel level = quelle.getLevel();
        int chunks = bereich.chunks().size();
        Supplier<Auftrag> auftrag = () -> new BlockAuftrag(level, spieler.getUUID(), titel, bereich, aktion);
        if (chunks > Auftragsverwaltung.NACHFRAGEN_AB_CHUNKS) {
            Auftragsverwaltung.nachfragen(spieler, auftrag, titel + " " + bereich.beschreibung(), chunks);
        } else {
            Auftragsverwaltung.starte(auftrag.get());
        }
        return 1;
    }

    private static int glaetten(CommandContext<CommandSourceStack> c, Bereich bereich, int staerke)
            throws CommandSyntaxException {
        CommandSourceStack quelle = c.getSource();
        if (Auftragsverwaltung.laeuft()) {
            quelle.sendFailure(Component.literal("Es läuft schon: " + Auftragsverwaltung.aktuell().titel()
                    + ". Warte, bis es fertig ist, oder brich es mit /wb abbrechen ab."));
            return 0;
        }
        ServerPlayer spieler = quelle.getPlayerOrException();
        ServerLevel level = quelle.getLevel();
        GlaettAuftrag auftrag = GlaettAuftrag.planen(level, spieler.getUUID(), bereich, staerke);
        if (auftrag == null) {
            quelle.sendFailure(Component.literal("Hier gibt es nichts zu glätten (oder die Chunks sind nicht geladen – "
                    + "stell dich näher an die Stelle)."));
            return 0;
        }
        quelle.sendSuccess(() -> Component.literal("Weltenbauer: ").withStyle(ChatFormatting.GOLD)
                .append(Component.literal(Auftragsverwaltung.zahl(auftrag.saeulen()) + " Geländesäulen werden geglättet "
                        + bereich.beschreibung() + " (Stärke " + staerke + "). Mit /wb rueckgaengig nimmst du es zurück.")
                        .withStyle(ChatFormatting.WHITE)), false);
        Auftragsverwaltung.starte(auftrag);
        return 1;
    }

    // ------------------------------------------------------------------ Verlauf

    private static int rueckgaengig(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        return verlauf(c, Verlauf.Stapel.RUECKGAENGIG, WiederherstellAuftrag.Richtung.RUECKGAENGIG,
                "Es gibt nichts zum Rückgängigmachen.");
    }

    private static int wiederholen(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        return verlauf(c, Verlauf.Stapel.WIEDERHOLEN, WiederherstellAuftrag.Richtung.WIEDERHOLEN,
                "Es gibt nichts zum Wiederholen.");
    }

    private static int verlauf(CommandContext<CommandSourceStack> c, Verlauf.Stapel stapel,
                               WiederherstellAuftrag.Richtung richtung, String leer) throws CommandSyntaxException {
        CommandSourceStack quelle = c.getSource();
        if (Auftragsverwaltung.laeuft()) {
            quelle.sendFailure(Component.literal("Es läuft gerade noch: " + Auftragsverwaltung.aktuell().titel() + "."));
            return 0;
        }
        ServerPlayer spieler = quelle.getPlayerOrException();
        MinecraftServer server = quelle.getServer();
        Protokoll protokoll = Verlauf.nehmen(server, spieler.getUUID(), stapel);
        if (protokoll == null) {
            quelle.sendFailure(Component.literal(leer));
            return 0;
        }
        ServerLevel level = server.getLevel(protokoll.dimension());
        if (level == null) {
            quelle.sendFailure(Component.literal("Die Dimension dieser Änderung gibt es nicht mehr."));
            return 0;
        }
        Auftragsverwaltung.starte(new WiederherstellAuftrag(level, spieler.getUUID(), protokoll, richtung));
        return 1;
    }

    // ------------------------------------------------------------------ Steuerung

    private static int bestaetigen(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        CommandSourceStack quelle = c.getSource();
        if (Auftragsverwaltung.laeuft()) {
            quelle.sendFailure(Component.literal("Es läuft noch ein anderer Auftrag."));
            return 0;
        }
        if (!Auftragsverwaltung.bestaetigen(quelle.getPlayerOrException())) {
            quelle.sendFailure(Component.literal("Es wartet nichts auf eine Bestätigung (oder die Minute ist abgelaufen)."));
            return 0;
        }
        return 1;
    }

    private static int abbrechen(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        CommandSourceStack quelle = c.getSource();
        boolean ausstehend = quelle.getEntity() instanceof ServerPlayer sp && Auftragsverwaltung.ausstehendVerwerfen(sp);
        if (Auftragsverwaltung.abbrechen()) {
            return 1;
        }
        if (ausstehend) {
            quelle.sendSuccess(() -> Component.literal("Okay, nichts gestartet.").withStyle(ChatFormatting.GRAY), false);
            return 1;
        }
        quelle.sendFailure(Component.literal("Gerade läuft nichts."));
        return 0;
    }

    private static int status(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        CommandSourceStack quelle = c.getSource();
        Auftrag a = Auftragsverwaltung.aktuell();
        ServerPlayer spieler = quelle.getPlayerOrException();
        int rueck = Verlauf.anzahl(quelle.getServer(), spieler.getUUID(), Verlauf.Stapel.RUECKGAENGIG);
        int wieder = Verlauf.anzahl(quelle.getServer(), spieler.getUUID(), Verlauf.Stapel.WIEDERHOLEN);
        String text = (a == null ? "Gerade läuft nichts." : "Läuft: " + a.titel() + " – " + a.anteilProzent() + " %.")
                + " Rückgängig möglich: " + rueck + " Schritt(e), Wiederholen: " + wieder + ".";
        quelle.sendSuccess(() -> Component.literal(text).withStyle(ChatFormatting.GOLD), false);
        return 1;
    }

    // ------------------------------------------------------------------ Stab & Auswahl

    private static int stab(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        ServerPlayer spieler = c.getSource().getPlayerOrException();
        ItemStack stab = new ItemStack(Weltenbauer.STAB.get());
        if (!spieler.getInventory().add(stab)) {
            spieler.drop(stab, false);
        }
        c.getSource().sendSuccess(() -> Component.literal("Hier ist dein Terraforming-Stab. Rechtsklick = Ecke 1, "
                + "Schleichen + Rechtsklick = Ecke 2.").withStyle(ChatFormatting.GOLD), false);
        return 1;
    }

    private static int auswahlZeigen(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        ServerPlayer spieler = c.getSource().getPlayerOrException();
        Auswahl.Ecken e = Auswahl.von(spieler);
        String text;
        if (e == null) {
            text = "Noch nichts markiert.";
        } else {
            text = "Ecke 1: " + (e.ecke1() == null ? "–" : e.ecke1().toShortString())
                    + "   Ecke 2: " + (e.ecke2() == null ? "–" : e.ecke2().toShortString())
                    + "   " + Auswahl.beschreibung(spieler);
        }
        c.getSource().sendSuccess(() -> Component.literal(text).withStyle(ChatFormatting.GOLD), false);
        return 1;
    }

    private static int auswahlLeeren(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        Auswahl.leeren(c.getSource().getPlayerOrException());
        c.getSource().sendSuccess(() -> Component.literal("Auswahl gelöscht.").withStyle(ChatFormatting.GRAY), false);
        return 1;
    }

    // ------------------------------------------------------------------ Hilfe

    private static int hilfe(CommandContext<CommandSourceStack> c) {
        MutableComponent t = Component.literal("— Weltenbauer —").withStyle(ChatFormatting.GOLD);
        zeile(t, "/wb schnee entfernen <Radius>", "Schneeschichten weg (+ „alles“: auch Schneeblöcke)");
        zeile(t, "/wb eis auftauen <Radius>", "zugefrorenes Wasser wird wieder Wasser");
        zeile(t, "/wb laub aufraeumen <Radius>", "schwebende Blätter ohne Stamm entfernen");
        zeile(t, "/wb entfernen <Block> <Radius>", "eine Blocksorte entfernen");
        zeile(t, "/wb ersetzen <Block> <Block> <Radius>", "eine Blocksorte austauschen");
        zeile(t, "/wb glaetten <Radius> [Stärke 1-10]", "kantiges Gelände weich ausblenden und an die Umgebung anpassen");
        zeile(t, "/wb vorlage", "Vorlagen-Katalog: Bäume, Ruinen, Felsen, Inseln …");
        zeile(t, "/wb vorlage setzen <Name> [Drehung] [spiegeln]", "Vorlage dorthin setzen, wohin du schaust");
        zeile(t, "/wb vorlage zeigen <Name>", "Umriss anzeigen, bevor du setzt");
        zeile(t, "/wb vorlage create <Name>", "als Schematic für Create/Litematica speichern");
        zeile(t, "/wb rueckgaengig · /wb wiederholen", "letzte Änderung zurück / erneut");
        zeile(t, "/wb abbrechen · /wb status", "laufende Aktion stoppen / Stand anzeigen");
        zeile(t, "/wb stab · /wb auswahl", "Stab holen / markierten Bereich anzeigen");
        t.append(Component.literal("\nStatt <Radius> geht überall auch „auswahl“ (mit dem Stab markiert). "
                + "Truhen und Maschinen werden nie angefasst.").withStyle(ChatFormatting.GRAY));
        c.getSource().sendSuccess(() -> t, false);
        return 1;
    }

    private static void zeile(MutableComponent t, String befehl, String erklaerung) {
        t.append(Component.literal("\n" + befehl).withStyle(ChatFormatting.YELLOW))
                .append(Component.literal("  " + erklaerung).withStyle(ChatFormatting.GRAY));
    }
}

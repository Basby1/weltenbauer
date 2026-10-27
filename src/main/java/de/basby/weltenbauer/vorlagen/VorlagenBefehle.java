package de.basby.weltenbauer.vorlagen;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.builder.ArgumentBuilder;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.mojang.brigadier.suggestion.SuggestionProvider;
import de.basby.weltenbauer.arbeit.Auftragsverwaltung;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.HoverEvent;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Random;

/** /wb vorlage … – Vorlagen anzeigen, setzen, als Umriss zeigen und für Create speichern. */
public final class VorlagenBefehle {

    private static final Random ZUFALL = new Random();

    private static final SuggestionProvider<CommandSourceStack> NAMEN =
            (c, b) -> SharedSuggestionProvider.suggest(Vorlagen.namen(), b);
    private static final SuggestionProvider<CommandSourceStack> KATEGORIEN =
            (c, b) -> SharedSuggestionProvider.suggest(Vorlagen.kategorien().keySet(), b);
    private static final SuggestionProvider<CommandSourceStack> DREHUNGEN =
            (c, b) -> SharedSuggestionProvider.suggest(List.of("0", "90", "180", "270", "zufall"), b);

    private VorlagenBefehle() {
    }

    @FunctionalInterface
    private interface MitVorlage {
        int los(CommandContext<CommandSourceStack> c, Rotation drehung, Mirror spiegel) throws CommandSyntaxException;
    }

    public static ArgumentBuilder<CommandSourceStack, ?> knoten() {
        return Commands.literal("vorlage")
                .executes(VorlagenBefehle::kategorienZeigen)
                .then(Commands.literal("liste")
                        .executes(VorlagenBefehle::kategorienZeigen)
                        .then(Commands.argument("kategorie", StringArgumentType.word()).suggests(KATEGORIEN)
                                .executes(VorlagenBefehle::liste)))
                .then(mitDrehung(Commands.literal("setzen"), VorlagenBefehle::setzen))
                .then(mitDrehung(Commands.literal("zeigen"), VorlagenBefehle::zeigen))
                .then(Commands.literal("create")
                        .then(Commands.argument("name", StringArgumentType.word()).suggests(NAMEN)
                                .executes(VorlagenBefehle::fuerCreate)))
                .then(Commands.literal("ordner").executes(VorlagenBefehle::ordner))
                .then(Commands.literal("drucken")
                        .then(Commands.argument("name", StringArgumentType.word()).suggests(NAMEN)
                                .then(Commands.argument("x", IntegerArgumentType.integer())
                                        .then(Commands.argument("y", IntegerArgumentType.integer())
                                                .then(Commands.argument("z", IntegerArgumentType.integer())
                                                        .then(Commands.argument("drehung", IntegerArgumentType.integer(0, 3))
                                                                .then(Commands.argument("spiegel", IntegerArgumentType.integer(0, 2))
                                                                        .executes(VorlagenBefehle::drucken))))))))
                .then(Commands.literal("waehlen")
                        .then(Commands.argument("name", StringArgumentType.word()).suggests(NAMEN)
                                .executes(VorlagenBefehle::waehlen)));
    }

    private static ArgumentBuilder<CommandSourceStack, ?> mitDrehung(ArgumentBuilder<CommandSourceStack, ?> knoten,
                                                                     MitVorlage aktion) {
        return knoten.then(Commands.argument("name", StringArgumentType.word()).suggests(NAMEN)
                .executes(c -> aktion.los(c, Rotation.NONE, Mirror.NONE))
                .then(Commands.argument("drehung", StringArgumentType.word()).suggests(DREHUNGEN)
                        .executes(c -> aktion.los(c, drehung(c), Mirror.NONE))
                        .then(Commands.literal("spiegeln")
                                .executes(c -> aktion.los(c, drehung(c), Mirror.FRONT_BACK)))));
    }

    private static Rotation drehung(CommandContext<CommandSourceStack> c) {
        String d = StringArgumentType.getString(c, "drehung").toLowerCase(Locale.ROOT);
        return switch (d) {
            case "90" -> Rotation.CLOCKWISE_90;
            case "180" -> Rotation.CLOCKWISE_180;
            case "270" -> Rotation.COUNTERCLOCKWISE_90;
            case "zufall", "random" -> Rotation.values()[ZUFALL.nextInt(4)];
            default -> Rotation.NONE;
        };
    }

    // ------------------------------------------------------------------ Liste

    private static int kategorienZeigen(CommandContext<CommandSourceStack> c) {
        MutableComponent t = Component.literal("— Weltenbauer-Vorlagen —").withStyle(ChatFormatting.GOLD);
        Map<String, Integer> anzahl = new LinkedHashMap<>();
        Map<String, String> namen = Vorlagen.kategorien();
        for (Vorlagen.Eintrag e : Vorlagen.alle()) {
            anzahl.merge(e.kategorie(), 1, Integer::sum);
        }
        for (Map.Entry<String, String> k : namen.entrySet()) {
            t.append(Component.literal("\n  "));
            t.append(Auftragsverwaltung.knopf("[" + k.getValue() + "]", "/wb vorlage liste " + k.getKey(),
                    "Vorlagen dieser Kategorie anzeigen", ChatFormatting.AQUA));
            t.append(Component.literal(" " + anzahl.getOrDefault(k.getKey(), 0)).withStyle(ChatFormatting.GRAY));
        }
        t.append(Component.literal("\nEigene .nbt-Dateien: Ordner weltenbauer/vorlagen und schematics (Create). "
                + "Gesetzt wird dort, wohin du schaust.").withStyle(ChatFormatting.GRAY));
        c.getSource().sendSuccess(() -> t, false);
        return 1;
    }

    private static int liste(CommandContext<CommandSourceStack> c) {
        String kat = StringArgumentType.getString(c, "kategorie");
        // Titel -> (Größe -> Gruppe)
        Map<String, Map<String, Vorlagen.Eintrag>> gruppen = new LinkedHashMap<>();
        String katName = kat;
        for (Vorlagen.Eintrag e : Vorlagen.alle()) {
            if (!e.kategorie().equals(kat)) {
                continue;
            }
            katName = e.kategorieName();
            gruppen.computeIfAbsent(e.titel(), k -> new LinkedHashMap<>()).putIfAbsent(e.groesse(), e);
        }
        if (gruppen.isEmpty()) {
            c.getSource().sendFailure(Component.literal("Keine Vorlagen in „" + kat + "“."));
            return 0;
        }
        MutableComponent t = Component.literal("— " + katName + " —").withStyle(ChatFormatting.GOLD);
        for (Map.Entry<String, Map<String, Vorlagen.Eintrag>> g : gruppen.entrySet()) {
            t.append(Component.literal("\n" + g.getKey() + ": ").withStyle(ChatFormatting.YELLOW));
            for (Map.Entry<String, Vorlagen.Eintrag> groesse : g.getValue().entrySet()) {
                Vorlagen.Eintrag e = groesse.getValue();
                String hover = e.beschreibung() + "\nKlick: auf den Bauwerk-Stab legen\n(Rechtsklick mit dem Stab = setzen)"
                        + (e.hinweis() != null ? "\nTipp: " + e.hinweis() : "");
                t.append(Component.literal("[" + groesse.getKey() + "]").withStyle(s -> s
                        .withColor(ChatFormatting.AQUA)
                        .withClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND,
                                "/wb vorlage waehlen " + e.gruppe()))
                        .withHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, Component.literal(hover)))));
                t.append(Component.literal(" "));
            }
            Vorlagen.Eintrag erster = g.getValue().values().iterator().next();
            t.append(Auftragsverwaltung.knopf("[Umriss]", "/wb vorlage zeigen " + erster.gruppe(),
                    "Zeigt 15 Sekunden lang, wo die Vorlage landen würde", ChatFormatting.DARK_GRAY));
        }
        c.getSource().sendSuccess(() -> t, false);
        return 1;
    }

    // ------------------------------------------------------------------ Setzen & Zeigen

    public static BlockPos ziel(ServerPlayer spieler) {
        HitResult treffer = spieler.pick(160.0, 1.0f, true);
        if (treffer instanceof BlockHitResult b && treffer.getType() == HitResult.Type.BLOCK) {
            return b.getBlockPos();
        }
        return spieler.blockPosition().below();
    }

    private static Vorlagen.Vorlage laden(CommandContext<CommandSourceStack> c) {
        String name = StringArgumentType.getString(c, "name");
        Vorlagen.Eintrag e = Vorlagen.finden(name);
        if (e == null) {
            c.getSource().sendFailure(Component.literal("Unbekannte Vorlage „" + name + "“. Liste: /wb vorlage"));
            return null;
        }
        try {
            return Vorlagen.laden(e, false);
        } catch (IOException | RuntimeException fehler) {
            c.getSource().sendFailure(Component.literal("Die Vorlage konnte nicht gelesen werden: " + fehler.getMessage()));
            return null;
        }
    }

    private static int setzen(CommandContext<CommandSourceStack> c, Rotation drehung, Mirror spiegel)
            throws CommandSyntaxException {
        CommandSourceStack quelle = c.getSource();
        if (Auftragsverwaltung.laeuft()) {
            quelle.sendFailure(Component.literal("Es läuft schon: " + Auftragsverwaltung.aktuell().titel()
                    + ". Warte kurz oder brich es mit /wb abbrechen ab."));
            return 0;
        }
        ServerPlayer spieler = quelle.getPlayerOrException();
        Vorlagen.Vorlage v = laden(c);
        if (v == null) {
            return 0;
        }
        BlockPos ziel = ziel(spieler);
        Auftragsverwaltung.starte(VorlageAuftrag.erstellen(spieler.serverLevel(), spieler.getUUID(), v, ziel,
                drehung, spiegel));
        if (v.unbekannt() > 0) {
            quelle.sendSuccess(() -> Component.literal(v.unbekannt() + " Blocksorte(n) aus fehlenden Mods werden "
                    + "übersprungen.").withStyle(ChatFormatting.GRAY), false);
        }
        if (v.eintrag().hinweis() != null) {
            quelle.sendSuccess(() -> Component.literal("Tipp: " + v.eintrag().hinweis()).withStyle(ChatFormatting.GRAY),
                    false);
        }
        return 1;
    }

    private static int zeigen(CommandContext<CommandSourceStack> c, Rotation drehung, Mirror spiegel)
            throws CommandSyntaxException {
        ServerPlayer spieler = c.getSource().getPlayerOrException();
        Vorlagen.Vorlage v = laden(c);
        if (v == null) {
            return 0;
        }
        BlockPos ziel = ziel(spieler);
        BlockPos[] k = VorlageAuftrag.kasten(v.groesse(), v.anker(), ziel, spiegel, drehung);
        Umriss.zeigen(spieler, k[0], k[1], ziel, 15);
        String name = StringArgumentType.getString(c, "name");
        MutableComponent t = Component.literal(v.eintrag().beschreibung() + " – Umriss für 15 Sekunden. ")
                .withStyle(ChatFormatting.GOLD)
                .append(Auftragsverwaltung.knopf("[Hier setzen]", "/wb vorlage setzen " + name,
                        "Jetzt an diese Stelle setzen (rückgängig machbar)", ChatFormatting.GREEN));
        c.getSource().sendSuccess(() -> t, false);
        return 1;
    }

    /** Exakt platzieren (vom Bauwerk-Stab nach dem Ausrichten gesendet). */
    private static int drucken(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        CommandSourceStack quelle = c.getSource();
        if (Auftragsverwaltung.laeuft()) {
            quelle.sendFailure(Component.literal("Es wird noch gebaut: " + Auftragsverwaltung.aktuell().titel()));
            return 0;
        }
        ServerPlayer spieler = quelle.getPlayerOrException();
        Vorlagen.Vorlage v = laden(c);
        if (v == null) {
            return 0;
        }
        BlockPos ziel = new BlockPos(IntegerArgumentType.getInteger(c, "x"), IntegerArgumentType.getInteger(c, "y"),
                IntegerArgumentType.getInteger(c, "z"));
        Rotation drehung = Rotation.values()[IntegerArgumentType.getInteger(c, "drehung")];
        Mirror spiegel = Mirror.values()[IntegerArgumentType.getInteger(c, "spiegel")];
        Auftragsverwaltung.starte(VorlageAuftrag.erstellen(spieler.serverLevel(), spieler.getUUID(), v, ziel, drehung,
                spiegel));
        return 1;
    }

    private static int waehlen(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
        ServerPlayer spieler = c.getSource().getPlayerOrException();
        String name = StringArgumentType.getString(c, "name");
        Vorlagen.Eintrag e = Vorlagen.erster(name);
        if (e == null) {
            c.getSource().sendFailure(Component.literal("Unbekannte Vorlage „" + name + "“."));
            return 0;
        }
        BauwerkStab.waehlen(spieler, name, e);
        return 1;
    }

    // ------------------------------------------------------------------ Create / Ordner

    private static int fuerCreate(CommandContext<CommandSourceStack> c) {
        String name = StringArgumentType.getString(c, "name");
        Vorlagen.Eintrag e = Vorlagen.finden(name);
        if (e == null) {
            c.getSource().sendFailure(Component.literal("Unbekannte Vorlage „" + name + "“."));
            return 0;
        }
        Path ordner = Vorlagen.createOrdner();
        Path ziel = ordner.resolve("weltenbauer_" + e.id() + ".nbt");
        try (InputStream in = Vorlagen.oeffnen(e)) {
            Files.createDirectories(ordner);
            Files.copy(in, ziel, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException fehler) {
            c.getSource().sendFailure(Component.literal("Speichern fehlgeschlagen: " + fehler.getMessage()));
            return 0;
        }
        c.getSource().sendSuccess(() -> Component.literal("Gespeichert als „" + ziel.getFileName()
                + "“ im Ordner schematics. Im Create-Schematictisch (und in Litematica unter „Vanilla-Strukturen“) "
                + "kannst du sie jetzt auswählen und mit der Schematic-Kanone bauen.").withStyle(ChatFormatting.GOLD), false);
        return 1;
    }

    private static int ordner(CommandContext<CommandSourceStack> c) {
        try {
            Files.createDirectories(Vorlagen.eigenerOrdner());
        } catch (IOException ignoriert) {
            // Anzeige trotzdem
        }
        List<String> zeilen = new ArrayList<>();
        zeilen.add("Eigene Vorlagen (.nbt): " + Vorlagen.eigenerOrdner().toAbsolutePath());
        zeilen.add("Create-Schematics (.nbt): " + Vorlagen.createOrdner().toAbsolutePath());
        zeilen.add("Neue Dateien erscheinen sofort in /wb vorlage.");
        c.getSource().sendSuccess(() -> Component.literal(String.join("\n", zeilen)).withStyle(ChatFormatting.GOLD), false);
        return 1;
    }
}

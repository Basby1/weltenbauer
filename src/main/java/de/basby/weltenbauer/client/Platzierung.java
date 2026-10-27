package de.basby.weltenbauer.client;

import de.basby.weltenbauer.vorlagen.BauwerkStab;
import de.basby.weltenbauer.vorlagen.VorlageAuftrag;
import de.basby.weltenbauer.vorlagen.Vorlagen;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Was der Spieler mit dem Bauwerk-Stab gerade platziert – wie bei Create-Schematics:
 * Geisterbild folgt dem Blick, Rechtsklick setzt es ab, danach mit Werkzeugen ausrichten und bestätigen.
 */
public final class Platzierung {

    public enum Werkzeug {
        VERSCHIEBEN("Verschieben"), HOEHE("Höhe"), DREHEN("Drehen"), SPIEGELN("Spiegeln"), VARIANTE("Variante"),
        SCHICHT("Schicht"), MODUS("Modus");
        public final String name;

        Werkzeug(String name) {
            this.name = name;
        }
    }

    public enum Modus { DRUCKEN, BLAUPAUSE }

    private static final Random ZUFALL = new Random();
    public static Modus modus = Modus.DRUCKEN;

    // Auswahl
    static String gruppe;
    static List<Vorlagen.Eintrag> varianten = new ArrayList<>();
    static int variante;
    static Vorlagen.Vorlage vorlage;

    // Lage
    static BlockPos ziel;
    static boolean abgesetzt;
    static Rotation drehung = Rotation.NONE;
    static Mirror spiegel = Mirror.NONE;
    static int schicht; // 0 = alle, sonst Höhe (1 = unterste Schicht)
    static int werkzeug;

    // Darstellung
    private static final Geist GEIST = new Geist();
    private static BlockPos geistUrsprung = BlockPos.ZERO;
    private static boolean neuBauen;

    private Platzierung() {
    }

    public static boolean aktiv() {
        return vorlage != null;
    }

    public static Werkzeug werkzeug() {
        return Werkzeug.values()[werkzeug];
    }

    public static Vorlagen.Eintrag eintrag() {
        return vorlage == null ? null : vorlage.eintrag();
    }

    // ------------------------------------------------------------------ Tick

    static void tick() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null) {
            zuruecksetzen();
            return;
        }
        ItemStack stack = mc.player.getMainHandItem();
        if (!(stack.getItem() instanceof BauwerkStab)) {
            return; // Stab nicht in der Hand: nichts tun, Geisterbild wird nicht gezeichnet
        }
        String gewaehlt = BauwerkStab.vorlage(stack);
        if (gewaehlt == null) {
            if (gruppe != null) {
                zuruecksetzen();
            }
            return;
        }
        if (!gewaehlt.equals(gruppe)) {
            waehlen(gewaehlt);
        }
        if (vorlage == null) {
            return;
        }
        if (!abgesetzt) {
            BlockPos neu = blickZiel(mc);
            if (neu != null) {
                ziel = neu;
            }
        }
        if (neuBauen && ziel != null) {
            geistBauen();
        }
    }

    private static BlockPos blickZiel(Minecraft mc) {
        HitResult treffer = mc.player.pick(160.0, 1.0f, true);
        if (treffer instanceof BlockHitResult b && treffer.getType() == HitResult.Type.BLOCK) {
            return b.getBlockPos();
        }
        return null;
    }

    private static void waehlen(String name) {
        zuruecksetzen();
        gruppe = name;
        varianten.clear();
        for (Vorlagen.Eintrag e : Vorlagen.alle()) {
            if (e.id().equals(name) || e.gruppe().equals(name)) {
                varianten.add(e);
            }
        }
        if (varianten.isEmpty()) {
            return;
        }
        variante = ZUFALL.nextInt(varianten.size());
        laden();
    }

    private static void laden() {
        try {
            vorlage = Vorlagen.laden(varianten.get(variante), false);
        } catch (Exception fehler) {
            vorlage = null;
            meldung("Vorlage konnte nicht geladen werden: " + fehler.getMessage());
        }
        neuBauen = true;
    }

    static void zuruecksetzen() {
        gruppe = null;
        vorlage = null;
        varianten.clear();
        abgesetzt = false;
        drehung = Rotation.NONE;
        spiegel = Mirror.NONE;
        schicht = 0;
        GEIST.schliessen();
    }

    private static void geistBauen() {
        neuBauen = false;
        Vorlagen.Vorlage v = vorlage;
        Long2ObjectOpenHashMap<BlockState> alle = new Long2ObjectOpenHashMap<>();
        List<Geist.Teil> teile = new ArrayList<>();
        // Geist relativ zum Nullpunkt bauen; verschoben wird erst beim Zeichnen
        for (int i = 0; i < v.positionen().size(); i++) {
            BlockState s = v.zustaende().get(i).mirror(spiegel).rotate(drehung);
            if (s.isAir()) {
                continue;
            }
            BlockPos p = VorlageAuftrag.weltPosition(v.positionen().get(i), v.anker(), BlockPos.ZERO, spiegel, drehung);
            alle.put(p.asLong(), s);
            if (schicht == 0 || v.positionen().get(i).getY() == schicht - 1) {
                teile.add(new Geist.Teil(p, s, 0));
            }
        }
        geistUrsprung = BlockPos.ZERO;
        GEIST.bauen(teile, alle, geistUrsprung);
    }

    static Geist geist() {
        return GEIST;
    }

    /** Wird gezeichnet, solange der Stab mit Auswahl in der Hand ist. */
    public static boolean sichtbar() {
        Minecraft mc = Minecraft.getInstance();
        return vorlage != null && ziel != null && mc.player != null
                && mc.player.getMainHandItem().getItem() instanceof BauwerkStab;
    }

    // ------------------------------------------------------------------ Eingaben

    /** Rechtsklick mit dem Stab. @return true = verarbeitet */
    static boolean rechtsklick(boolean schleichen) {
        Minecraft mc = Minecraft.getInstance();
        if (vorlage == null) {
            ItemStack stack = mc.player.getMainHandItem();
            if (stack.getItem() instanceof BauwerkStab && BauwerkStab.vorlage(stack) == null) {
                if (schleichen && Blaupausen.entfernenImBlick()) {
                    return true;
                }
                mc.setScreen(new VorlagenMenue());
                return true;
            }
            return false;
        }
        if (schleichen) {
            if (abgesetzt) {
                abgesetzt = false;
                meldung("Abgebrochen – das Geisterbild folgt wieder deinem Blick.");
            } else if (!Blaupausen.entfernenImBlick()) {
                mc.setScreen(new VorlagenMenue());
            }
            return true;
        }
        if (ziel == null) {
            return true;
        }
        if (!abgesetzt) {
            abgesetzt = true;
            werkzeug = Werkzeug.VERSCHIEBEN.ordinal();
            meldung("Abgesetzt. Mit Mausrad ausrichten, Rechtsklick zum "
                    + (modus == Modus.DRUCKEN ? "Bauen." : "Behalten als Blaupause."));
            return true;
        }
        bestaetigen();
        return true;
    }

    private static void bestaetigen() {
        Minecraft mc = Minecraft.getInstance();
        Vorlagen.Eintrag e = vorlage.eintrag();
        if (modus == Modus.DRUCKEN) {
            mc.player.connection.sendCommand("wb vorlage drucken " + e.id() + " " + ziel.getX() + " " + ziel.getY() + " "
                    + ziel.getZ() + " " + drehung.ordinal() + " " + spiegel.ordinal());
        } else {
            Blaupausen.hinzufuegen(e, ziel, drehung, spiegel);
            meldung("Blaupause steht – bau sie nach! Fertige Blöcke verschwinden, falsche leuchten rot.");
        }
        abgesetzt = false;
        if (varianten.size() > 1) {
            variante = ZUFALL.nextInt(varianten.size());
            laden();
        }
    }

    /** Mausrad. @return true = verarbeitet (Hotbar nicht wechseln) */
    static boolean mausrad(double delta, boolean strg) {
        if (vorlage == null) {
            return strg && Blaupausen.schichtImBlick(delta);
        }
        int schritt = delta > 0 ? 1 : -1;
        if (strg) {
            int n = Werkzeug.values().length;
            werkzeug = Math.floorMod(werkzeug - schritt, n);
            return true;
        }
        if (!abgesetzt) {
            return false;
        }
        Minecraft mc = Minecraft.getInstance();
        switch (werkzeug()) {
            case VERSCHIEBEN -> {
                Direction d = mc.player.getDirection();
                ziel = ziel.relative(d, schritt);
            }
            case HOEHE -> ziel = ziel.above(schritt);
            case DREHEN -> {
                drehung = drehung.getRotated(schritt > 0 ? Rotation.CLOCKWISE_90 : Rotation.COUNTERCLOCKWISE_90);
                neuBauen = true;
            }
            case SPIEGELN -> {
                spiegel = Mirror.values()[Math.floorMod(spiegel.ordinal() + schritt, Mirror.values().length)];
                neuBauen = true;
            }
            case VARIANTE -> {
                if (varianten.size() > 1) {
                    variante = Math.floorMod(variante + schritt, varianten.size());
                    laden();
                }
            }
            case SCHICHT -> {
                int hoehe = vorlage.groesse().getY();
                schicht = Math.floorMod(schicht + schritt, hoehe + 1);
                neuBauen = true;
            }
            case MODUS -> modus = modus == Modus.DRUCKEN ? Modus.BLAUPAUSE : Modus.DRUCKEN;
        }
        return true;
    }

    public static String wertText(Werkzeug w) {
        return switch (w) {
            case VERSCHIEBEN -> ziel == null ? "–" : ziel.getX() + " " + ziel.getZ();
            case HOEHE -> ziel == null ? "–" : "Y " + ziel.getY();
            case DREHEN -> switch (drehung) {
                case NONE -> "0°";
                case CLOCKWISE_90 -> "90°";
                case CLOCKWISE_180 -> "180°";
                case COUNTERCLOCKWISE_90 -> "270°";
            };
            case SPIEGELN -> switch (spiegel) {
                case NONE -> "aus";
                case LEFT_RIGHT -> "links-rechts";
                case FRONT_BACK -> "vorne-hinten";
            };
            case VARIANTE -> (variante + 1) + "/" + Math.max(1, varianten.size());
            case SCHICHT -> schicht == 0 ? "alle" : schicht + "/" + (vorlage == null ? 0 : vorlage.groesse().getY());
            case MODUS -> modus == Modus.DRUCKEN ? "Drucken" : "Blaupause";
        };
    }

    public static boolean abgesetzt() {
        return abgesetzt;
    }

    public static BlockPos ziel() {
        return ziel;
    }

    public static Rotation drehung() {
        return drehung;
    }

    public static Mirror spiegel() {
        return spiegel;
    }

    static void meldung(String text) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null) {
            mc.player.displayClientMessage(Component.literal(text).withStyle(s -> s.withColor(0xE8B04A)), true);
        }
    }
}

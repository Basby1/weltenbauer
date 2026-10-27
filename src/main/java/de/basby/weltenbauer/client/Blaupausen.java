package de.basby.weltenbauer.client;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import de.basby.weltenbauer.vorlagen.VorlageAuftrag;
import de.basby.weltenbauer.vorlagen.Vorlagen;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.LevelResource;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.fml.loading.FMLPaths;

import java.io.Reader;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Stehende Blaupausen zum Nachbauen. Sie werden pro Welt gespeichert, zeigen nur noch fehlende Blöcke
 * (falsche rot) und liefern die Materialliste für das HUD.
 */
public final class Blaupausen {

    /** Gespeicherte Daten einer Blaupause. */
    public static final class Blaupause {
        String vorlage;
        String dimension;
        int x, y, z;
        int drehung, spiegel, schicht;

        transient Vorlagen.Vorlage geladen;
        transient Geist geist = new Geist();
        transient BlockPos min, max;
        transient Map<Block, Integer> fehlend = new LinkedHashMap<>();
        transient int fertig, gesamt, falsch;
        transient long signatur = Long.MIN_VALUE;
        transient boolean neu = true;

        BlockPos ziel() {
            return new BlockPos(x, y, z);
        }

        Rotation rotation() {
            return Rotation.values()[Math.floorMod(drehung, 4)];
        }

        Mirror mirror() {
            return Mirror.values()[Math.floorMod(spiegel, 3)];
        }

        public String titel() {
            return geladen == null ? vorlage : geladen.eintrag().titel();
        }

        public int fertig() {
            return fertig;
        }

        public int gesamt() {
            return gesamt;
        }

        public int falsch() {
            return falsch;
        }

        public int schicht() {
            return schicht;
        }

        public int hoehe() {
            return geladen == null ? 0 : geladen.groesse().getY();
        }

        public Map<Block, Integer> fehlend() {
            return fehlend;
        }
    }

    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final List<Blaupause> LISTE = new ArrayList<>();
    private static String schluessel;
    private static ClientLevel letzteWelt;
    private static int ticks;

    private Blaupausen() {
    }

    // ------------------------------------------------------------------ Laden / Speichern

    private static String weltSchluessel(Minecraft mc) {
        String name;
        if (mc.getSingleplayerServer() != null) {
            name = mc.getSingleplayerServer().getWorldPath(LevelResource.ROOT).toAbsolutePath().normalize()
                    .getFileName().toString();
        } else if (mc.getCurrentServer() != null) {
            name = "server_" + mc.getCurrentServer().ip;
        } else {
            name = "unbekannt";
        }
        return name.replaceAll("[^A-Za-z0-9_.-]", "_");
    }

    private static Path datei() {
        return FMLPaths.GAMEDIR.get().resolve("weltenbauer").resolve("blaupausen").resolve(schluessel + ".json");
    }

    private static void laden() {
        for (Blaupause b : LISTE) {
            b.geist.schliessen();
        }
        LISTE.clear();
        try {
            Path d = datei();
            if (Files.exists(d)) {
                try (Reader r = Files.newBufferedReader(d, StandardCharsets.UTF_8)) {
                    List<Blaupause> l = GSON.fromJson(r, new TypeToken<List<Blaupause>>() { }.getType());
                    if (l != null) {
                        for (Blaupause b : l) {
                            b.geist = new Geist();
                            b.fehlend = new LinkedHashMap<>();
                            b.signatur = Long.MIN_VALUE;
                            b.neu = true;
                            LISTE.add(b);
                        }
                    }
                }
            }
        } catch (Exception ignoriert) {
            // kaputte Datei: einfach ohne Blaupausen weiter
        }
    }

    private static void speichern() {
        try {
            Path d = datei();
            Files.createDirectories(d.getParent());
            try (Writer w = Files.newBufferedWriter(d, StandardCharsets.UTF_8)) {
                GSON.toJson(LISTE, w);
            }
        } catch (Exception ignoriert) {
            // nicht kritisch
        }
    }

    // ------------------------------------------------------------------ Verwaltung

    static void hinzufuegen(Vorlagen.Eintrag e, BlockPos ziel, Rotation drehung, Mirror spiegel) {
        Minecraft mc = Minecraft.getInstance();
        Blaupause b = new Blaupause();
        b.vorlage = e.id();
        b.dimension = mc.level.dimension().location().toString();
        b.x = ziel.getX();
        b.y = ziel.getY();
        b.z = ziel.getZ();
        b.drehung = drehung.ordinal();
        b.spiegel = spiegel.ordinal();
        LISTE.add(b);
        speichern();
    }

    static void entfernen(Blaupause b) {
        b.geist.schliessen();
        LISTE.remove(b);
        speichern();
    }

    /** Entfernt die Blaupause, auf die der Spieler schaut. */
    static boolean entfernenImBlick() {
        Blaupause b = imBlick();
        if (b == null) {
            return false;
        }
        entfernen(b);
        Platzierung.meldung("Blaupause „" + b.titel() + "“ entfernt.");
        return true;
    }

    /** Strg + Mausrad ohne Auswahl: Schicht der Blaupause im Blick bzw. der nächsten wechseln. */
    static boolean schichtImBlick(double delta) {
        Blaupause b = imBlick();
        if (b == null) {
            b = naechste(48);
        }
        if (b == null || b.geladen == null) {
            return false;
        }
        b.schicht = Math.floorMod(b.schicht + (delta > 0 ? 1 : -1), b.hoehe() + 1);
        b.signatur = Long.MIN_VALUE;
        speichern();
        Platzierung.meldung("Blaupause: Schicht " + (b.schicht == 0 ? "alle" : b.schicht + "/" + b.hoehe()));
        return true;
    }

    static Blaupause imBlick() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null) {
            return null;
        }
        HitResult t = mc.player.pick(160.0, 1.0f, false);
        if (!(t instanceof BlockHitResult bt) || t.getType() != HitResult.Type.BLOCK) {
            return null;
        }
        BlockPos p = bt.getBlockPos();
        for (Blaupause b : LISTE) {
            if (b.min != null && sichtbarHier(b) && p.getX() >= b.min.getX() - 1 && p.getX() <= b.max.getX() + 1
                    && p.getY() >= b.min.getY() - 1 && p.getY() <= b.max.getY() + 1
                    && p.getZ() >= b.min.getZ() - 1 && p.getZ() <= b.max.getZ() + 1) {
                return b;
            }
        }
        return null;
    }

    /** Die nächste Blaupause in dieser Dimension (für das HUD). */
    public static Blaupause naechste(double maxAbstand) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null) {
            return null;
        }
        Blaupause beste = null;
        double bester = maxAbstand * maxAbstand;
        for (Blaupause b : LISTE) {
            if (!sichtbarHier(b) || b.min == null) {
                continue;
            }
            double cx = (b.min.getX() + b.max.getX()) / 2.0, cy = (b.min.getY() + b.max.getY()) / 2.0,
                    cz = (b.min.getZ() + b.max.getZ()) / 2.0;
            double d = mc.player.distanceToSqr(cx, cy, cz);
            if (d < bester) {
                bester = d;
                beste = b;
            }
        }
        return beste;
    }

    public static List<Blaupause> alle() {
        return LISTE;
    }

    private static boolean sichtbarHier(Blaupause b) {
        Minecraft mc = Minecraft.getInstance();
        return mc.level != null && mc.level.dimension().location().toString().equals(b.dimension);
    }

    // ------------------------------------------------------------------ Tick & Zeichnen

    static void tick() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level != letzteWelt) {
            letzteWelt = mc.level;
            if (mc.level != null) {
                schluessel = weltSchluessel(mc);
                laden();
            } else {
                for (Blaupause b : LISTE) {
                    b.geist.schliessen();
                }
                LISTE.clear();
            }
        }
        if (mc.level == null || mc.player == null || LISTE.isEmpty()) {
            return;
        }
        if (++ticks % 20 != 0) {
            return;
        }
        for (Blaupause b : new ArrayList<>(LISTE)) {
            if (!sichtbarHier(b)) {
                continue;
            }
            if (b.geladen == null) {
                Vorlagen.Eintrag e = Vorlagen.erster(b.vorlage);
                if (e == null) {
                    continue;
                }
                try {
                    b.geladen = Vorlagen.laden(e, false);
                } catch (Exception fehler) {
                    continue;
                }
                BlockPos[] k = VorlageAuftrag.kasten(b.geladen.groesse(), b.geladen.anker(), b.ziel(), b.mirror(),
                        b.rotation());
                b.min = k[0];
                b.max = k[1];
            }
            double cx = (b.min.getX() + b.max.getX()) / 2.0, cz = (b.min.getZ() + b.max.getZ()) / 2.0;
            double weite = Math.max(b.max.getX() - b.min.getX(), b.max.getZ() - b.min.getZ()) / 2.0 + 96;
            if (Math.abs(mc.player.getX() - cx) > weite || Math.abs(mc.player.getZ() - cz) > weite) {
                if (!b.geist.leer()) {
                    b.geist.schliessen();
                    b.signatur = Long.MIN_VALUE;
                }
                continue;
            }
            aktualisieren(b, mc.level);
        }
    }

    private static void aktualisieren(Blaupause b, ClientLevel level) {
        Vorlagen.Vorlage v = b.geladen;
        BlockPos ziel = b.ziel();
        Long2ObjectOpenHashMap<BlockState> alle = new Long2ObjectOpenHashMap<>();
        List<Geist.Teil> teile = new ArrayList<>();
        Map<Block, Integer> fehlend = new LinkedHashMap<>();
        int fertig = 0, gesamt = 0, falsch = 0;
        long sig = b.schicht * 31L;
        for (int i = 0; i < v.positionen().size(); i++) {
            BlockState soll = v.zustaende().get(i).mirror(b.mirror()).rotate(b.rotation());
            if (soll.isAir()) {
                continue;
            }
            BlockPos p = VorlageAuftrag.weltPosition(v.positionen().get(i), v.anker(), ziel, b.mirror(), b.rotation());
            alle.put(p.asLong(), soll);
            gesamt++;
            if (!level.hasChunkAt(p)) {
                continue;
            }
            BlockState ist = level.getBlockState(p);
            if (ist.getBlock() == soll.getBlock()) {
                fertig++;
                continue;
            }
            boolean leer = ist.isAir() || ist.canBeReplaced() || !ist.getFluidState().isEmpty();
            fehlend.merge(soll.getBlock(), 1, Integer::sum);
            if (!leer) {
                falsch++;
            }
            boolean inSchicht = b.schicht == 0 || v.positionen().get(i).getY() == b.schicht - 1;
            if (inSchicht) {
                teile.add(new Geist.Teil(p, soll, leer ? 0 : 1));
                sig = sig * 31 + p.asLong() * (leer ? 1 : 7);
            }
        }
        b.fertig = fertig;
        b.gesamt = gesamt;
        b.falsch = falsch;
        b.fehlend = sortiert(fehlend);
        if (sig != b.signatur) {
            b.signatur = sig;
            b.geist.bauen(teile, alle, ziel);
        }
    }

    private static Map<Block, Integer> sortiert(Map<Block, Integer> m) {
        Map<Block, Integer> r = new LinkedHashMap<>();
        m.entrySet().stream().sorted((a, c) -> c.getValue() - a.getValue()).forEach(e -> r.put(e.getKey(), e.getValue()));
        return r;
    }

    static void zeichnen(com.mojang.blaze3d.vertex.PoseStack ps, org.joml.Matrix4f proj, net.minecraft.world.phys.Vec3 kam) {
        for (Blaupause b : LISTE) {
            if (sichtbarHier(b)) {
                b.geist.zeichnen(ps, proj, kam, b.ziel());
            }
        }
    }

    // ------------------------------------------------------------------ Befehle (/wbblaupause)

    static int drucken() {
        Blaupause b = imBlick();
        if (b == null) {
            b = naechste(64);
        }
        if (b == null) {
            Platzierung.meldung("Keine Blaupause in der Nähe.");
            return 0;
        }
        Minecraft.getInstance().player.connection.sendCommand("wb vorlage drucken " + b.vorlage + " " + b.x + " " + b.y
                + " " + b.z + " " + b.drehung + " " + b.spiegel);
        entfernen(b);
        return 1;
    }

    static int entfernenNaechste() {
        Blaupause b = imBlick();
        if (b == null) {
            b = naechste(64);
        }
        if (b == null) {
            Platzierung.meldung("Keine Blaupause in der Nähe.");
            return 0;
        }
        entfernen(b);
        Platzierung.meldung("Blaupause „" + b.titel() + "“ entfernt.");
        return 1;
    }

    static int alleEntfernen() {
        for (Blaupause b : LISTE) {
            b.geist.schliessen();
        }
        int n = LISTE.size();
        LISTE.clear();
        speichern();
        Platzierung.meldung(n + " Blaupause(n) entfernt.");
        return n;
    }
}

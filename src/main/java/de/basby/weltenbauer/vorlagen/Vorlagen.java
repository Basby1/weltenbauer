package de.basby.weltenbauer.vorlagen;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import de.basby.weltenbauer.Weltenbauer;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.fml.loading.FMLPaths;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Random;
import java.util.stream.Stream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

/**
 * Kennt alle Vorlagen: die eingebauten (im Mod-Jar unter data/weltenbauer/structures) und
 * eigene Dateien aus den Ordnern {@code weltenbauer/vorlagen} und {@code schematics} (Create).
 */
public final class Vorlagen {

    private static final Logger LOG = LoggerFactory.getLogger("Weltenbauer");
    private static final Random ZUFALL = new Random();
    private static List<Eintrag> eingebaut;

    private Vorlagen() {
    }

    /**
     * @param id        eindeutiger Name (z. B. eiche_gross_1)
     * @param gruppe    Varianten-Gruppe (z. B. eiche_gross) – damit kann man eine zufällige Variante setzen
     * @param quelle    Pfad im Jar (eingebaut) oder Datei auf der Festplatte
     * @param anker     Punkt der Vorlage, der auf dem angeklickten Block landet (null = unten Mitte, darüber)
     */
    public record Eintrag(String id, String gruppe, String titel, String kategorie, String kategorieName,
                          String groesse, boolean eingebaut, String quelle, int[] anker, int[] masse, int bloecke,
                          String hinweis) {
        public String beschreibung() {
            return titel + " (" + groesse + ", " + masse[0] + "×" + masse[1] + "×" + masse[2] + ")";
        }
    }

    /** Eine geladene Vorlage: Blöcke relativ zur Vorlagen-Ecke. */
    /**
     * @param folgen      null = starr; sonst je Block: Index in folgeAnker (Gruppe folgt dem Gelände an diesem Punkt),
     *                    -1 = folgt dem Gelände der eigenen Spalte (Boden, Pflanzen), -2 = starr
     * @param folgeAnker  x/z-Paare (relativ zur Vorlage), z. B. Stammfüße der Bäume eines Waldstücks
     */
    public record Vorlage(Eintrag eintrag, BlockPos groesse, BlockPos anker, List<BlockPos> positionen,
                          List<BlockState> zustaende, List<CompoundTag> daten, int unbekannt, int[] folgen,
                          int[] folgeAnker) {
    }

    // ------------------------------------------------------------------ Liste

    public static synchronized List<Eintrag> eingebaute() {
        if (eingebaut == null) {
            eingebaut = new ArrayList<>();
            try (InputStream in = Weltenbauer.class.getResourceAsStream("/data/weltenbauer/vorlagen.json")) {
                if (in != null) {
                    JsonObject wurzel = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8))
                            .getAsJsonObject();
                    for (JsonElement el : wurzel.getAsJsonArray("vorlagen")) {
                        JsonObject o = el.getAsJsonObject();
                        eingebaut.add(ausJson(o, "/data/weltenbauer/" + o.get("datei").getAsString()));
                    }
                }
            } catch (Exception fehler) {
                LOG.error("Weltenbauer: Vorlagen-Liste konnte nicht gelesen werden", fehler);
            }
        }
        return eingebaut;
    }

    /** Eigene Vorlagen: weltenbauer/vorlagen/*.nbt und schematics/*.nbt im Spielordner. */
    private static List<Eintrag> eigeneCache;
    private static long eigeneZeit;

    public static synchronized List<Eintrag> eigene() {
        long jetzt = System.currentTimeMillis();
        if (eigeneCache != null && jetzt - eigeneZeit < 5000) {
            return eigeneCache;
        }
        List<Eintrag> liste = new ArrayList<>();
        sammeln(eigenerOrdner(), "eigene", "Eigene Vorlagen", liste);
        sammeln(createOrdner(), "create", "Create-Schematics", liste);
        eigeneCache = liste;
        eigeneZeit = jetzt;
        return liste;
    }

    private static Eintrag ausJson(JsonObject o, String quelle) {
        return new Eintrag(o.get("id").getAsString(), o.get("gruppe").getAsString(),
                o.get("titel").getAsString(), o.get("kategorie").getAsString(),
                o.get("kategorie_name").getAsString(), o.get("groesse").getAsString(), true,
                quelle, ints(o.getAsJsonArray("anker")), ints(o.getAsJsonArray("masse")), o.get("bloecke").getAsInt(),
                o.has("hinweis") ? o.get("hinweis").getAsString() : null);
    }

    // ------------------------------------------------------------------ Vorlagen-Pakete (Zip im Ordner weltenbauer/pakete)

    private static List<Eintrag> paketCache;
    private static long paketZeit;
    private static final Map<String, String[]> PAKET_BILDER = new HashMap<>();

    public static Path paketOrdner() {
        return FMLPaths.GAMEDIR.get().resolve("weltenbauer").resolve("pakete");
    }

    /** Nach einem Download: Pakete beim nächsten Zugriff neu einlesen. */
    public static synchronized void paketeNeuLesen() {
        paketCache = null;
    }

    public static synchronized List<Eintrag> pakete() {
        long jetzt = System.currentTimeMillis();
        if (paketCache != null && jetzt - paketZeit < 5000) {
            return paketCache;
        }
        List<Eintrag> liste = new ArrayList<>();
        Map<String, String[]> bilder = new HashMap<>();
        Path ordner = paketOrdner();
        if (Files.isDirectory(ordner)) {
            List<Path> zips;
            try (Stream<Path> s = Files.list(ordner)) {
                zips = s.filter(p -> p.getFileName().toString().toLowerCase(Locale.ROOT).endsWith(".zip")).sorted()
                        .toList();
            } catch (IOException fehler) {
                zips = List.of();
            }
            for (Path zip : zips) {
                try (ZipFile z = new ZipFile(zip.toFile(), StandardCharsets.UTF_8)) {
                    ZipEntry j = z.getEntry("paket.json");
                    if (j == null) {
                        continue;
                    }
                    JsonObject wurzel;
                    try (InputStream in = z.getInputStream(j)) {
                        wurzel = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
                    }
                    for (JsonElement el : wurzel.getAsJsonArray("vorlagen")) {
                        JsonObject o = el.getAsJsonObject();
                        Eintrag e = ausJson(o, "zip:" + zip + "!" + o.get("datei").getAsString());
                        liste.add(e);
                        String bild = "bilder/" + e.gruppe() + ".png";
                        if (!bilder.containsKey(e.gruppe()) && z.getEntry(bild) != null) {
                            bilder.put(e.gruppe(), new String[]{zip.toString(), bild});
                        }
                    }
                } catch (Exception fehler) {
                    LOG.warn("Weltenbauer: Paket {} konnte nicht gelesen werden", zip, fehler);
                }
            }
        }
        paketCache = liste;
        paketZeit = jetzt;
        PAKET_BILDER.clear();
        PAKET_BILDER.putAll(bilder);
        return liste;
    }

    /** Vorschaubild (PNG) einer Gruppe aus einem Paket oder null. */
    public static synchronized byte[] paketBild(String gruppe) {
        pakete();
        String[] q = PAKET_BILDER.get(gruppe);
        if (q == null) {
            return null;
        }
        try (ZipFile z = new ZipFile(new java.io.File(q[0]), StandardCharsets.UTF_8)) {
            ZipEntry e = z.getEntry(q[1]);
            try (InputStream in = z.getInputStream(e)) {
                return in.readAllBytes();
            }
        } catch (Exception fehler) {
            return null;
        }
    }

    public static List<Eintrag> alle() {
        List<Eintrag> liste = new ArrayList<>(eingebaute());
        liste.addAll(pakete());
        liste.addAll(eigene());
        return liste;
    }

    public static Path eigenerOrdner() {
        return FMLPaths.GAMEDIR.get().resolve("weltenbauer").resolve("vorlagen");
    }

    public static Path createOrdner() {
        return FMLPaths.GAMEDIR.get().resolve("schematics");
    }

    private static void sammeln(Path ordner, String kategorie, String kategorieName, List<Eintrag> liste) {
        if (!Files.isDirectory(ordner)) {
            return;
        }
        try (Stream<Path> dateien = Files.list(ordner)) {
            dateien.filter(p -> p.getFileName().toString().toLowerCase(Locale.ROOT).endsWith(".nbt"))
                    .sorted()
                    .forEach(p -> {
                        String datei = p.getFileName().toString();
                        String name = datei.substring(0, datei.length() - 4);
                        String id = kategorie + "_" + name.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9_]", "_");
                        liste.add(new Eintrag(id, id, name, kategorie, kategorieName, "eigene", false,
                                p.toString(), null, new int[]{0, 0, 0}, 0, null));
                    });
        } catch (IOException fehler) {
            LOG.warn("Weltenbauer: Ordner {} konnte nicht gelesen werden", ordner, fehler);
        }
    }

    /** Kategorien in fester Reihenfolge mit Anzeigenamen. */
    public static Map<String, String> kategorien() {
        Map<String, String> k = new LinkedHashMap<>();
        for (Eintrag e : alle()) {
            k.putIfAbsent(e.kategorie(), e.kategorieName());
        }
        return k;
    }

    /** Sucht eine Vorlage per ID oder – bei einem Gruppennamen – eine zufällige Variante. */
    public static Eintrag finden(String name) {
        List<Eintrag> alle = alle();
        for (Eintrag e : alle) {
            if (e.id().equals(name)) {
                return e;
            }
        }
        List<Eintrag> gruppe = new ArrayList<>();
        for (Eintrag e : alle) {
            if (e.gruppe().equals(name)) {
                gruppe.add(e);
            }
        }
        return gruppe.isEmpty() ? null : gruppe.get(ZUFALL.nextInt(gruppe.size()));
    }

    /** Wie finden(), aber bei Gruppen immer die erste Variante (für die Vorschau). */
    public static Eintrag erster(String name) {
        Eintrag zufall = null;
        for (Eintrag e : alle()) {
            if (e.id().equals(name)) {
                return e;
            }
            if (zufall == null && e.gruppe().equals(name)) {
                zufall = e;
            }
        }
        return zufall;
    }

    private static final Map<String, BlockPos[]> MASSE = new java.util.HashMap<>();

    /** Größe und Anker einer Vorlage (eingebaute aus der Liste, eigene einmal aus der Datei gelesen). */
    public static BlockPos[] masse(Eintrag e) {
        if (e.eingebaut()) {
            return new BlockPos[]{new BlockPos(e.masse()[0], e.masse()[1], e.masse()[2]),
                    new BlockPos(e.anker()[0], e.anker()[1], e.anker()[2])};
        }
        return MASSE.computeIfAbsent(e.quelle(), q -> {
            try {
                Vorlage v = laden(e, false);
                return new BlockPos[]{v.groesse(), v.anker()};
            } catch (IOException | RuntimeException fehler) {
                return null;
            }
        });
    }

    /** Alle IDs und Gruppennamen (für die Tab-Vervollständigung). */
    public static List<String> namen() {
        List<String> n = new ArrayList<>();
        for (Eintrag e : alle()) {
            if (!n.contains(e.gruppe())) {
                n.add(e.gruppe());
            }
            if (!e.id().equals(e.gruppe())) {
                n.add(e.id());
            }
        }
        Collections.sort(n);
        return n;
    }

    // ------------------------------------------------------------------ Laden

    public static InputStream oeffnen(Eintrag e) throws IOException {
        if (e.quelle().startsWith("zip:")) {
            int trenner = e.quelle().lastIndexOf('!');
            try (ZipFile z = new ZipFile(new java.io.File(e.quelle().substring(4, trenner)), StandardCharsets.UTF_8)) {
                ZipEntry eintrag = z.getEntry(e.quelle().substring(trenner + 1));
                if (eintrag == null) {
                    throw new IOException("Vorlage fehlt im Paket: " + e.quelle());
                }
                try (InputStream in = z.getInputStream(eintrag)) {
                    return new ByteArrayInputStream(in.readAllBytes());
                }
            }
        }
        if (e.eingebaut()) {
            InputStream in = Weltenbauer.class.getResourceAsStream(e.quelle());
            if (in == null) {
                throw new IOException("Vorlage fehlt im Mod: " + e.quelle());
            }
            return in;
        }
        return Files.newInputStream(Path.of(e.quelle()));
    }

    public static Vorlage laden(Eintrag e, boolean mitLuft) throws IOException {
        CompoundTag t;
        try (InputStream in = oeffnen(e)) {
            t = NbtIo.readCompressed(in);
        }
        ListTag groesseTag = t.getList("size", Tag.TAG_INT);
        BlockPos groesse = new BlockPos(groesseTag.getInt(0), groesseTag.getInt(1), groesseTag.getInt(2));
        ListTag paletteTag = t.contains("palette", Tag.TAG_LIST) ? t.getList("palette", Tag.TAG_COMPOUND)
                : t.getList("palettes", Tag.TAG_LIST).getList(0);
        List<BlockState> palette = new ArrayList<>();
        int unbekannt = 0;
        for (int i = 0; i < paletteTag.size(); i++) {
            CompoundTag p = paletteTag.getCompound(i);
            BlockState s = NbtUtils.readBlockState(BuiltInRegistries.BLOCK.asLookup(), p);
            if (s.isAir() && !p.getString("Name").equals("minecraft:air")) {
                unbekannt++;   // Block aus einer Mod, die fehlt
                s = null;
            }
            palette.add(s);
        }
        ListTag bloecke = t.getList("blocks", Tag.TAG_COMPOUND);
        List<BlockPos> pos = new ArrayList<>(bloecke.size());
        List<BlockState> zust = new ArrayList<>(bloecke.size());
        List<CompoundTag> daten = new ArrayList<>(bloecke.size());
        boolean folgt = t.contains("wb_anker", Tag.TAG_INT_ARRAY);
        int[] folgeAnker = folgt ? t.getIntArray("wb_anker") : null;
        List<Integer> folgen = new ArrayList<>();
        boolean luftErlaubt = mitLuft || e.eingebaut();
        for (int i = 0; i < bloecke.size(); i++) {
            CompoundTag b = bloecke.getCompound(i);
            int idx = b.getInt("state");
            BlockState s = idx >= 0 && idx < palette.size() ? palette.get(idx) : null;
            if (s == null || s.is(Blocks.STRUCTURE_VOID) || (s.isAir() && !luftErlaubt)) {
                continue;
            }
            ListTag p = b.getList("pos", Tag.TAG_INT);
            pos.add(new BlockPos(p.getInt(0), p.getInt(1), p.getInt(2)));
            zust.add(s);
            daten.add(b.contains("nbt", Tag.TAG_COMPOUND) ? b.getCompound("nbt") : null);
            if (folgt) {
                folgen.add(b.contains("wb_f", Tag.TAG_INT) ? b.getInt("wb_f") : -2);
            }
        }
        BlockPos anker = e.anker() != null
                ? new BlockPos(e.anker()[0], e.anker()[1], e.anker()[2])
                // eigene Schematics: unten in der Mitte, die unterste Schicht landet ÜBER dem angeklickten Block
                : new BlockPos(groesse.getX() / 2, -1, groesse.getZ() / 2);
        int[] f = folgt ? folgen.stream().mapToInt(Integer::intValue).toArray() : null;
        return new Vorlage(e, groesse, anker, pos, zust, daten, unbekannt, f, folgeAnker);
    }

    private static int[] ints(JsonArray a) {
        int[] r = new int[a.size()];
        for (int i = 0; i < r.length; i++) {
            r[i] = a.get(i).getAsInt();
        }
        return r;
    }
}

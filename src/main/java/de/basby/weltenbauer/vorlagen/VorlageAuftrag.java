package de.basby.weltenbauer.vorlagen;

import de.basby.weltenbauer.arbeit.Auftrag;
import de.basby.weltenbauer.arbeit.GlaettAuftrag;
import it.unimi.dsi.fastutil.ints.IntArrayList;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraft.world.level.material.FluidState;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.UUID;

/**
 * Setzt eine Vorlage Chunk für Chunk in die Welt – gedreht/gespiegelt, mit Rückgängig-Protokoll.
 * Blöcke mit Inhalt (Truhen, Maschinen …) werden nie überschrieben.
 */
public class VorlageAuftrag extends Auftrag {

    private final long[] positionen;
    private final BlockState[] zustaende;
    private final CompoundTag[] daten;
    private final Long2ObjectOpenHashMap<IntArrayList> nachChunk;

    private VorlageAuftrag(ServerLevel level, UUID besitzer, String titel, List<ChunkPos> chunks, long[] positionen,
                           BlockState[] zustaende, CompoundTag[] daten, Long2ObjectOpenHashMap<IntArrayList> nachChunk) {
        super(level, besitzer, titel, chunks);
        this.positionen = positionen;
        this.zustaende = zustaende;
        this.daten = daten;
        this.nachChunk = nachChunk;
    }

    /** Wo der Block (relativ zur Vorlage) nach Drehen/Spiegeln in der Welt landet. */
    public static BlockPos weltPosition(BlockPos rel, BlockPos anker, BlockPos ziel, Mirror spiegel, Rotation drehung) {
        BlockPos p = StructureTemplate.transform(rel.subtract(anker), spiegel, drehung, BlockPos.ZERO);
        return ziel.offset(p);
    }

    /** Umgebender Kasten (min, max) der gedrehten Vorlage in der Welt. */
    public static BlockPos[] kasten(BlockPos groesse, BlockPos anker, BlockPos ziel, Mirror spiegel, Rotation drehung) {
        int minX = Integer.MAX_VALUE, minY = Integer.MAX_VALUE, minZ = Integer.MAX_VALUE;
        int maxX = Integer.MIN_VALUE, maxY = Integer.MIN_VALUE, maxZ = Integer.MIN_VALUE;
        for (int i = 0; i < 8; i++) {
            BlockPos ecke = new BlockPos((i & 1) == 0 ? 0 : groesse.getX() - 1, (i & 2) == 0 ? 0 : groesse.getY() - 1,
                    (i & 4) == 0 ? 0 : groesse.getZ() - 1);
            BlockPos w = weltPosition(ecke, anker, ziel, spiegel, drehung);
            minX = Math.min(minX, w.getX());
            minY = Math.min(minY, w.getY());
            minZ = Math.min(minZ, w.getZ());
            maxX = Math.max(maxX, w.getX());
            maxY = Math.max(maxY, w.getY());
            maxZ = Math.max(maxZ, w.getZ());
        }
        return new BlockPos[]{new BlockPos(minX, minY, minZ), new BlockPos(maxX, maxY, maxZ)};
    }

    public static VorlageAuftrag erstellen(ServerLevel level, UUID besitzer, Vorlagen.Vorlage v, BlockPos ziel,
                                           Rotation drehung, Mirror spiegel) {
        int n = v.positionen().size();
        long[] pos = new long[n];
        BlockState[] zust = new BlockState[n];
        CompoundTag[] dat = new CompoundTag[n];
        Long2ObjectOpenHashMap<IntArrayList> karte = new Long2ObjectOpenHashMap<>();
        // Geländefolgend (z. B. Waldstücke): jede Gruppe wird auf die echte Geländehöhe an ihrem Fußpunkt gesetzt
        int[] ankerVersatz = null;
        Long2ObjectOpenHashMap<Integer> spalten = new Long2ObjectOpenHashMap<>();
        if (v.folgen() != null && v.folgeAnker() != null) {
            int m = v.folgeAnker().length / 2;
            ankerVersatz = new int[m];
            for (int a = 0; a < m; a++) {
                BlockPos fuss = weltPosition(new BlockPos(v.folgeAnker()[2 * a], v.anker().getY(),
                        v.folgeAnker()[2 * a + 1]), v.anker(), ziel, spiegel, drehung);
                ankerVersatz[a] = versatz(level, fuss.getX(), fuss.getZ(), ziel.getY());
            }
        }
        int k = 0;
        for (int i = 0; i < n; i++) {
            BlockPos w = weltPosition(v.positionen().get(i), v.anker(), ziel, spiegel, drehung);
            if (ankerVersatz != null) {
                int f = v.folgen()[i];
                int d;
                if (f >= 0 && f < ankerVersatz.length) {
                    d = ankerVersatz[f];
                } else if (f == -1) {
                    long sp = ChunkPos.asLong(w.getX(), w.getZ());
                    Integer gemerkt = spalten.get(sp);
                    if (gemerkt == null) {
                        gemerkt = versatz(level, w.getX(), w.getZ(), ziel.getY());
                        spalten.put(sp, gemerkt);
                    }
                    d = gemerkt;
                } else {
                    d = 0;
                }
                if (d == Integer.MIN_VALUE) {
                    continue;   // Wasser oder kein Boden – hier nichts setzen
                }
                w = w.above(d);
            }
            if (level.isOutsideBuildHeight(w)) {
                continue;
            }
            pos[k] = w.asLong();
            zust[k] = v.zustaende().get(i).mirror(spiegel).rotate(drehung);
            dat[k] = v.daten().get(i);
            karte.computeIfAbsent(ChunkPos.asLong(w.getX() >> 4, w.getZ() >> 4), c -> new IntArrayList()).add(k);
            k++;
        }
        List<ChunkPos> chunks = new ArrayList<>();
        for (long c : karte.keySet()) {
            chunks.add(new ChunkPos(c));
        }
        ChunkPos mitte = new ChunkPos(ziel);
        chunks.sort(Comparator.comparingInt(c -> c.getChessboardDistance(mitte)));
        String titel = "Vorlage „" + v.eintrag().titel() + "“";
        return new VorlageAuftrag(level, besitzer, titel, chunks, pos, zust, dat, karte);
    }

    /** Höhenunterschied zwischen dem Gelände an (x, z) und der Zielhöhe; MIN_VALUE bei Wasser. */
    private static int versatz(ServerLevel level, int x, int z, int zielY) {
        int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z) - 1;
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos(x, y, z);
        int untergrenze = Math.max(level.getMinBuildHeight(), y - 48);
        for (; y > untergrenze; y--) {
            BlockState s = level.getBlockState(p.setY(y));
            if (!s.getFluidState().isEmpty()) {
                return Integer.MIN_VALUE;
            }
            if (GlaettAuftrag.istGelaende(s) || s.is(Blocks.SNOW_BLOCK)) {
                return y - zielY;
            }
        }
        return 0;
    }

    @Override
    protected boolean erzeugeFehlende() {
        return true;
    }

    @Override
    protected void bearbeite(LevelChunk chunk) {
        IntArrayList liste = nachChunk.remove(chunk.getPos().toLong());
        if (liste == null) {
            return;
        }
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        for (int j = 0; j < liste.size(); j++) {
            int i = liste.getInt(j);
            p.set(positionen[i]);
            BlockState alt = level.getBlockState(p);
            BlockState neu = zustaende[i];
            if (alt == neu) {
                continue;
            }
            if (alt.hasBlockEntity()) {
                geschuetzt++;
                continue;
            }
            if (!level.setBlock(p, neu, Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE)) {
                continue;
            }
            protokoll.merke(p.asLong(), alt, null);
            geaendert++;
            if (daten[i] != null) {
                BlockEntity inhalt = level.getBlockEntity(p);
                if (inhalt != null) {
                    CompoundTag t = daten[i].copy();
                    t.putInt("x", p.getX());
                    t.putInt("y", p.getY());
                    t.putInt("z", p.getZ());
                    inhalt.load(t);
                    inhalt.setChanged();
                }
            }
            FluidState fluessig = neu.getFluidState();
            if (!fluessig.isEmpty()) {
                // Wasser soll fließen (z. B. Wasserfälle)
                level.scheduleTick(p.immutable(), fluessig.getType(), fluessig.getType().getTickDelay(level));
            }
        }
    }
}

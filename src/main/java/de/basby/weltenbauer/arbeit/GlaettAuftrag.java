package de.basby.weltenbauer.arbeit;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.levelgen.Heightmap;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Glättet die Geländeoberfläche: Kanten und Treppenstufen werden weich ausgeblendet, zum Rand hin
 * geht die Wirkung sanft in das unveränderte Gelände über. Bäume, Wasser, Gebäude und Truhen bleiben
 * unberührt. Steile Hänge bekommen das Gestein aus der Tiefe, flache Stellen behalten ihre Oberfläche.
 *
 * Die Höhen werden beim Start einmal aus den geladenen Chunks gelesen und berechnet, danach wird
 * Chunk für Chunk geändert (mit Rückgängig-Protokoll).
 */
public class GlaettAuftrag extends Auftrag {

    private record Saeule(int x, int z, int alt, int neu, BlockState decke, BlockState unter, BlockState grund,
                          boolean steil) {
    }

    private final Map<Long, List<Saeule>> plan;
    private final int saeulen;

    private GlaettAuftrag(ServerLevel level, UUID besitzer, String titel, Map<Long, List<Saeule>> plan,
                          List<ChunkPos> chunks, int saeulen) {
        super(level, besitzer, titel, chunks);
        this.plan = plan;
        this.saeulen = saeulen;
    }

    /** Anzahl der Säulen, deren Höhe oder Oberfläche sich ändert. */
    public int saeulen() {
        return saeulen;
    }

    // ------------------------------------------------------------------ Planung

    public static boolean istGelaende(BlockState s) {
        if (s.isAir() || !s.getFluidState().isEmpty() || s.hasBlockEntity()) {
            return false;
        }
        if (s.is(BlockTags.LEAVES) || s.is(BlockTags.LOGS) || s.is(BlockTags.PLANKS) || s.is(BlockTags.WOOL)
                || s.is(BlockTags.FENCES) || s.is(BlockTags.WALLS) || s.is(BlockTags.DOORS)
                || s.is(Blocks.GLASS) || s.is(BlockTags.IMPERMEABLE)) {
            return false;
        }
        return s.blocksMotion();
    }

    private static boolean istGras(BlockState s) {
        return s.is(Blocks.GRASS_BLOCK) || s.is(Blocks.PODZOL) || s.is(Blocks.MYCELIUM) || s.is(Blocks.DIRT_PATH)
                || s.is(Blocks.MOSS_BLOCK);
    }

    /**
     * @param staerke 1 (leicht) … 10 (sehr weich)
     * @return der fertig geplante Auftrag oder null, wenn nichts zu tun ist
     */
    public static GlaettAuftrag planen(ServerLevel level, UUID besitzer, Bereich bereich, int staerke) {
        // Ausdehnung in x/z aus den Chunks
        int bx0 = Integer.MAX_VALUE, bz0 = Integer.MAX_VALUE, bx1 = Integer.MIN_VALUE, bz1 = Integer.MIN_VALUE;
        for (ChunkPos c : bereich.chunks()) {
            bx0 = Math.min(bx0, c.getMinBlockX());
            bz0 = Math.min(bz0, c.getMinBlockZ());
            bx1 = Math.max(bx1, c.getMaxBlockX());
            bz1 = Math.max(bz1, c.getMaxBlockZ());
        }
        if (bx0 > bx1) {
            return null;
        }
        int r = 2;                       // Radius des Weichzeichners pro Durchgang
        int durchgaenge = Math.max(1, staerke);
        int rand = r * durchgaenge + 2;  // Umfeld, das mitgelesen (aber nicht verändert) wird
        int x0 = bx0 - rand, z0 = bz0 - rand;
        int nx = bx1 - bx0 + 1 + 2 * rand, nz = bz1 - bz0 + 1 + 2 * rand;
        double[] h = new double[nx * nz];
        BlockState[] decke = new BlockState[nx * nz];
        BlockState[] unter = new BlockState[nx * nz];
        BlockState[] grund = new BlockState[nx * nz];
        BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
        int minY = level.getMinBuildHeight();
        for (int i = 0; i < nx; i++) {
            for (int j = 0; j < nz; j++) {
                int x = x0 + i, z = z0 + j;
                int k = i * nz + j;
                h[k] = Double.NaN;
                if (level.getChunkSource().getChunkNow(x >> 4, z >> 4) == null) {
                    continue;
                }
                int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z) - 1;
                for (int schritt = 0; schritt < 64 && y > minY; schritt++, y--) {
                    BlockState s = level.getBlockState(pos.set(x, y, z));
                    if (!s.getFluidState().isEmpty()) {
                        break;                                   // Wasser: diese Säule nicht anfassen
                    }
                    if (istGelaende(s)) {
                        h[k] = y;
                        decke[k] = s;
                        BlockState u = level.getBlockState(pos.set(x, y - 1, z));
                        unter[k] = istGelaende(u) ? u : s;
                        BlockState g = level.getBlockState(pos.set(x, y - 4, z));
                        grund[k] = istGelaende(g) && !istGras(g) ? g : (istGras(unter[k]) ? Blocks.STONE.defaultBlockState() : unter[k]);
                        if (istGras(unter[k])) {
                            unter[k] = Blocks.DIRT.defaultBlockState();
                        }
                        break;
                    }
                }
            }
        }
        // Weichzeichnen (getrennt in x und z, Lücken werden ausgelassen)
        double[] s = h.clone();
        double[] tmp = new double[s.length];
        for (int d = 0; d < durchgaenge; d++) {
            for (int richtung = 0; richtung < 2; richtung++) {
                for (int i = 0; i < nx; i++) {
                    for (int j = 0; j < nz; j++) {
                        int k = i * nz + j;
                        if (Double.isNaN(s[k])) {
                            tmp[k] = Double.NaN;
                            continue;
                        }
                        double summe = 0, gewicht = 0;
                        for (int o = -r; o <= r; o++) {
                            int ii = richtung == 0 ? i + o : i, jj = richtung == 0 ? j : j + o;
                            if (ii < 0 || jj < 0 || ii >= nx || jj >= nz) {
                                continue;
                            }
                            double v = s[ii * nz + jj];
                            if (!Double.isNaN(v)) {
                                double gw = 1.0 - Math.abs(o) / (r + 1.0);
                                summe += v * gw;
                                gewicht += gw;
                            }
                        }
                        tmp[k] = summe / gewicht;
                    }
                }
                double[] t = s;
                s = tmp;
                tmp = t;
            }
        }
        // Zielhöhen mit weichem Übergang zum Rand
        double ausblend = Math.max(3, Math.min(14, Math.min(bx1 - bx0, bz1 - bz0) * 0.22));
        int[] neu = new int[h.length];
        boolean[] aktiv = new boolean[h.length];
        for (int i = 0; i < nx; i++) {
            for (int j = 0; j < nz; j++) {
                int k = i * nz + j;
                int x = x0 + i, z = z0 + j;
                if (Double.isNaN(h[k]) || !bereich.enthaelt(x, bereich.minY(), z)) {
                    neu[k] = Double.isNaN(h[k]) ? Integer.MIN_VALUE : (int) h[k];
                    continue;
                }
                double abstand;
                if (bereich instanceof Bereich.Kreis kr) {
                    abstand = kr.radius() - Math.hypot(x - kr.mitteX(), z - kr.mitteZ());
                } else if (bereich instanceof Bereich.Quader q) {
                    abstand = Math.min(Math.min(x - q.x0(), q.x1() - x), Math.min(z - q.z0(), q.z1() - z));
                } else {
                    abstand = ausblend;
                }
                double t = Math.max(0, Math.min(1, abstand / ausblend));
                double w = t * t * (3 - 2 * t);
                double zittern = (rauschen(x, z) - 0.5) * 0.7 * w;   // bricht Höhenlinien auf, wirkt natürlicher
                neu[k] = (int) Math.round(h[k] + w * (s[k] - h[k]) + zittern);
                aktiv[k] = true;
            }
        }
        Map<Long, List<Saeule>> plan = new HashMap<>();
        int anzahl = 0;
        for (int i = 1; i < nx - 1; i++) {
            for (int j = 1; j < nz - 1; j++) {
                int k = i * nz + j;
                if (!aktiv[k]) {
                    continue;
                }
                int maxDiff = 0;
                for (int[] o : new int[][]{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}) {
                    int kn = (i + o[0]) * nz + j + o[1];
                    if (neu[kn] != Integer.MIN_VALUE) {
                        maxDiff = Math.max(maxDiff, Math.abs(neu[kn] - neu[k]));
                    }
                }
                boolean steil = maxDiff >= 3;
                int alt = (int) h[k];
                boolean grasAufSteil = steil && istGras(decke[k]);
                if (neu[k] == alt && !grasAufSteil) {
                    continue;
                }
                int x = x0 + i, z = z0 + j;
                plan.computeIfAbsent(ChunkPos.asLong(x >> 4, z >> 4), c -> new ArrayList<>())
                        .add(new Saeule(x, z, alt, neu[k], decke[k], unter[k], grund[k], steil));
                anzahl++;
            }
        }
        if (plan.isEmpty()) {
            return null;
        }
        List<ChunkPos> chunks = new ArrayList<>();
        for (long c : plan.keySet()) {
            chunks.add(new ChunkPos(c));
        }
        int mx = (bx0 + bx1) / 2, mz = (bz0 + bz1) / 2;
        chunks.sort(Comparator.comparingLong(c -> {
            long dx = c.getMiddleBlockX() - mx, dz = c.getMiddleBlockZ() - mz;
            return dx * dx + dz * dz;
        }));
        return new GlaettAuftrag(level, besitzer, "Gelände glätten", plan, chunks, anzahl);
    }

    private static double rauschen(int x, int z) {
        long n = x * 73428767L ^ z * 912931L;
        n = (n << 13) ^ n;
        return ((n * (n * n * 15731L + 789221L) + 1376312589L) & 0x7fffffffL) / (double) 0x7fffffffL;
    }

    // ------------------------------------------------------------------ Ausführung

    @Override
    protected void bearbeite(LevelChunk chunk) {
        List<Saeule> liste = plan.get(chunk.getPos().toLong());
        if (liste == null) {
            return;
        }
        BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
        for (Saeule s : liste) {
            BlockState oben = s.steil() && istGras(s.decke()) ? s.grund() : s.decke();
            if (s.neu() < s.alt()) {
                for (int y = s.alt() + 1; y > s.neu(); y--) {
                    pos.set(s.x(), y, s.z());
                    BlockState alt = level.getBlockState(pos);
                    if (alt.isAir() || alt.hasBlockEntity() || alt.is(BlockTags.LOGS) || !alt.getFluidState().isEmpty()) {
                        continue;
                    }
                    if (istGelaende(alt) || alt.canBeReplaced()) {
                        setze(pos, alt, Blocks.AIR.defaultBlockState());
                    }
                }
                pos.set(s.x(), s.neu(), s.z());
                BlockState alt = level.getBlockState(pos);
                if (istGelaende(alt)) {
                    setze(pos, alt, oben);
                }
            } else if (s.neu() > s.alt()) {
                pos.set(s.x(), s.alt(), s.z());
                BlockState altOben = level.getBlockState(pos);
                if (istGras(altOben)) {
                    setze(pos, altOben, s.unter());
                }
                for (int y = s.alt() + 1; y <= s.neu(); y++) {
                    pos.set(s.x(), y, s.z());
                    BlockState alt = level.getBlockState(pos);
                    if (!(alt.isAir() || (alt.canBeReplaced() && alt.getFluidState().isEmpty()))) {
                        continue;
                    }
                    BlockState ziel = y == s.neu() ? oben : (y >= s.neu() - 2 ? s.unter() : s.grund());
                    setze(pos, alt, ziel);
                }
                pos.set(s.x(), s.neu() + 1, s.z());
                BlockState darueber = level.getBlockState(pos);
                if (!darueber.isAir() && darueber.canBeReplaced() && darueber.getFluidState().isEmpty()
                        && !darueber.hasBlockEntity()) {
                    setze(pos, darueber, Blocks.AIR.defaultBlockState());
                }
            } else {
                pos.set(s.x(), s.alt(), s.z());
                BlockState alt = level.getBlockState(pos);
                if (istGras(alt)) {
                    setze(pos, alt, oben);
                    pos.set(s.x(), s.alt() + 1, s.z());
                    BlockState pflanze = level.getBlockState(pos);
                    if (!pflanze.isAir() && pflanze.canBeReplaced() && pflanze.getFluidState().isEmpty()) {
                        setze(pos, pflanze, Blocks.AIR.defaultBlockState());
                    }
                }
            }
        }
    }

    private void setze(BlockPos pos, BlockState alt, BlockState neu) {
        if (alt == neu) {
            return;
        }
        if (level.setBlock(pos, neu, Block.UPDATE_CLIENTS)) {
            protokoll.merke(pos.asLong(), alt, null);
            geaendert++;
        }
    }
}

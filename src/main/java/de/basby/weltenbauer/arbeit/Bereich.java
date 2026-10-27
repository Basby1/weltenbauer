package de.basby.weltenbauer.arbeit;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/** Der Bereich, in dem ein Befehl wirkt: ein Umkreis um den Spieler oder eine markierte Auswahl. */
public interface Bereich {

    boolean enthaelt(int x, int y, int z);

    int minY();

    int maxY();

    /** Alle betroffenen Chunks, die nächsten zuerst. */
    List<ChunkPos> chunks();

    String beschreibung();

    /** Umkreis (Kreis von oben gesehen) über die ganze Welthöhe. */
    record Kreis(int mitteX, int mitteZ, int radius, int minY, int maxY) implements Bereich {
        @Override
        public boolean enthaelt(int x, int y, int z) {
            long dx = x - mitteX;
            long dz = z - mitteZ;
            return dx * dx + dz * dz <= (long) radius * radius && y >= minY && y <= maxY;
        }

        @Override
        public List<ChunkPos> chunks() {
            List<ChunkPos> liste = new ArrayList<>();
            int cx0 = (mitteX - radius) >> 4, cx1 = (mitteX + radius) >> 4;
            int cz0 = (mitteZ - radius) >> 4, cz1 = (mitteZ + radius) >> 4;
            long r2 = (long) radius * radius;
            for (int cx = cx0; cx <= cx1; cx++) {
                for (int cz = cz0; cz <= cz1; cz++) {
                    // nächster Punkt des Chunks zur Mitte
                    int nx = Math.max(cx << 4, Math.min(mitteX, (cx << 4) + 15));
                    int nz = Math.max(cz << 4, Math.min(mitteZ, (cz << 4) + 15));
                    long dx = nx - mitteX, dz = nz - mitteZ;
                    if (dx * dx + dz * dz <= r2) {
                        liste.add(new ChunkPos(cx, cz));
                    }
                }
            }
            sortiere(liste, mitteX, mitteZ);
            return liste;
        }

        @Override
        public String beschreibung() {
            return "im Umkreis von " + radius + " Blöcken";
        }
    }

    /** Quader zwischen zwei markierten Ecken. */
    record Quader(int x0, int y0, int z0, int x1, int y1, int z1) implements Bereich {
        public static Quader aus(BlockPos a, BlockPos b) {
            return new Quader(Math.min(a.getX(), b.getX()), Math.min(a.getY(), b.getY()), Math.min(a.getZ(), b.getZ()),
                    Math.max(a.getX(), b.getX()), Math.max(a.getY(), b.getY()), Math.max(a.getZ(), b.getZ()));
        }

        @Override
        public boolean enthaelt(int x, int y, int z) {
            return x >= x0 && x <= x1 && y >= y0 && y <= y1 && z >= z0 && z <= z1;
        }

        @Override
        public int minY() {
            return y0;
        }

        @Override
        public int maxY() {
            return y1;
        }

        @Override
        public List<ChunkPos> chunks() {
            List<ChunkPos> liste = new ArrayList<>();
            for (int cx = x0 >> 4; cx <= x1 >> 4; cx++) {
                for (int cz = z0 >> 4; cz <= z1 >> 4; cz++) {
                    liste.add(new ChunkPos(cx, cz));
                }
            }
            sortiere(liste, (x0 + x1) / 2, (z0 + z1) / 2);
            return liste;
        }

        @Override
        public String beschreibung() {
            return "in der Auswahl (" + (x1 - x0 + 1) + " × " + (y1 - y0 + 1) + " × " + (z1 - z0 + 1) + ")";
        }
    }

    private static void sortiere(List<ChunkPos> liste, int mx, int mz) {
        liste.sort(Comparator.comparingLong(c -> {
            long dx = ((long) c.x << 4) + 8 - mx;
            long dz = ((long) c.z << 4) + 8 - mz;
            return dx * dx + dz * dz;
        }));
    }
}

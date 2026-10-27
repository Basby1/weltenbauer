package de.basby.weltenbauer.vorlagen;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.server.ServerLifecycleHooks;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;

/** Zeigt einem Spieler für ein paar Sekunden mit Partikeln, wo eine Vorlage landen würde. */
public final class Umriss {

    private record Kasten(ServerLevel level, BlockPos min, BlockPos max, BlockPos anker, int bisTick) {
    }

    private static final Map<UUID, Kasten> AKTIV = new HashMap<>();

    private Umriss() {
    }

    public static void zeigen(ServerPlayer spieler, BlockPos min, BlockPos max, BlockPos anker, int sekunden) {
        MinecraftServer server = spieler.getServer();
        int jetzt = server == null ? 0 : server.getTickCount();
        AKTIV.put(spieler.getUUID(), new Kasten(spieler.serverLevel(), min, max, anker, jetzt + sekunden * 20));
    }

    public static void tick() {
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null) {
            return;
        }
        int jetzt = server.getTickCount();
        if (jetzt % 5 != 0) {
            return;
        }
        Iterator<Map.Entry<UUID, Kasten>> it = AKTIV.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<UUID, Kasten> e = it.next();
            Kasten k = e.getValue();
            ServerPlayer sp = server.getPlayerList().getPlayer(e.getKey());
            if (sp == null || jetzt > k.bisTick() || sp.serverLevel() != k.level()) {
                it.remove();
                continue;
            }
            zeichnen(sp, k);
        }
    }

    /** Zeichnet einen Umriss einmalig (für die Live-Vorschau des Bauwerk-Stabs). */
    public static void einmal(ServerPlayer sp, BlockPos min, BlockPos max, BlockPos anker) {
        zeichnen(sp, new Kasten(sp.serverLevel(), min, max, anker, 0));
    }

    private static void zeichnen(ServerPlayer sp, Kasten k) {
        double x0 = k.min().getX(), y0 = k.min().getY(), z0 = k.min().getZ();
        double x1 = k.max().getX() + 1, y1 = k.max().getY() + 1, z1 = k.max().getZ() + 1;
        double laengste = Math.max(x1 - x0, Math.max(y1 - y0, z1 - z0));
        double schritt = Math.max(1.0, laengste / 40.0);
        ParticleOptions p = ParticleTypes.END_ROD;
        double[][] ecken = {{x0, y0, z0}, {x1, y0, z0}, {x0, y1, z0}, {x1, y1, z0},
                {x0, y0, z1}, {x1, y0, z1}, {x0, y1, z1}, {x1, y1, z1}};
        int[][] kanten = {{0, 1}, {2, 3}, {4, 5}, {6, 7}, {0, 2}, {1, 3}, {4, 6}, {5, 7}, {0, 4}, {1, 5}, {2, 6}, {3, 7}};
        for (int[] kante : kanten) {
            double[] a = ecken[kante[0]], b = ecken[kante[1]];
            double laenge = Math.sqrt(Math.pow(b[0] - a[0], 2) + Math.pow(b[1] - a[1], 2) + Math.pow(b[2] - a[2], 2));
            int n = (int) Math.ceil(laenge / schritt);
            for (int i = 0; i <= n; i++) {
                double t = n == 0 ? 0 : (double) i / n;
                k.level().sendParticles(sp, p, true, a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
                        a[2] + (b[2] - a[2]) * t, 1, 0, 0, 0, 0);
            }
        }
        // Ankerpunkt: kleine Flammensäule
        for (int i = 0; i < 4; i++) {
            k.level().sendParticles(sp, ParticleTypes.FLAME, true, k.anker().getX() + 0.5, k.anker().getY() + 1 + i * 0.5,
                    k.anker().getZ() + 0.5, 1, 0, 0, 0, 0);
        }
    }
}

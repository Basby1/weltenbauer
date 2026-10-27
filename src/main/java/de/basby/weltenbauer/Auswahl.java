package de.basby.weltenbauer;

import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** Merkt sich pro Spieler die zwei mit dem Stab markierten Ecken. */
public final class Auswahl {

    public record Ecken(ResourceKey<Level> dimension, BlockPos ecke1, BlockPos ecke2) {
        public boolean vollstaendig() {
            return ecke1 != null && ecke2 != null;
        }
    }

    private static final Map<UUID, Ecken> AUSWAHL = new HashMap<>();

    private Auswahl() {
    }

    public static void setze(ServerPlayer spieler, BlockPos pos, boolean zweite) {
        ResourceKey<Level> dim = spieler.level().dimension();
        Ecken alt = AUSWAHL.get(spieler.getUUID());
        if (alt == null || !alt.dimension().equals(dim)) {
            alt = new Ecken(dim, null, null);
        }
        AUSWAHL.put(spieler.getUUID(), zweite
                ? new Ecken(dim, alt.ecke1(), pos.immutable())
                : new Ecken(dim, pos.immutable(), alt.ecke2()));
    }

    public static Ecken von(ServerPlayer spieler) {
        return AUSWAHL.get(spieler.getUUID());
    }

    public static void leeren(ServerPlayer spieler) {
        AUSWAHL.remove(spieler.getUUID());
    }

    public static String beschreibung(ServerPlayer spieler) {
        Ecken e = AUSWAHL.get(spieler.getUUID());
        if (e == null || !e.vollstaendig()) {
            return "(noch eine Ecke fehlt)";
        }
        int dx = Math.abs(e.ecke1().getX() - e.ecke2().getX()) + 1;
        int dy = Math.abs(e.ecke1().getY() - e.ecke2().getY()) + 1;
        int dz = Math.abs(e.ecke1().getZ() - e.ecke2().getZ()) + 1;
        return "(Auswahl " + dx + " × " + dy + " × " + dz + ")";
    }
}

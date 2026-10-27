package de.basby.weltenbauer.arbeit;

import com.mojang.logging.LogUtils;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.storage.LevelResource;
import org.slf4j.Logger;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.Comparator;
import java.util.UUID;

/**
 * Rückgängig- und Wiederholen-Verlauf pro Spieler. Wird auf der Festplatte im Weltordner gespeichert
 * (weltenbauer/verlauf/…), damit er auch nach einem Neustart erhalten bleibt und keinen
 * Arbeitsspeicher belegt.
 */
public final class Verlauf {
    private static final Logger LOG = LogUtils.getLogger();
    private static final int MAX_SCHRITTE = 10;
    private static long zaehler;

    private Verlauf() {
    }

    public enum Stapel { RUECKGAENGIG, WIEDERHOLEN }

    private static File ordner(MinecraftServer server, UUID spieler, Stapel stapel) {
        File basis = server.getWorldPath(LevelResource.ROOT).toFile();
        return new File(basis, "weltenbauer/verlauf/" + spieler + "/"
                + (stapel == Stapel.RUECKGAENGIG ? "rueckgaengig" : "wiederholen"));
    }

    private static File[] dateien(File ordner) {
        File[] liste = ordner.listFiles((d, name) -> name.endsWith(".dat"));
        if (liste == null) {
            return new File[0];
        }
        Arrays.sort(liste, Comparator.comparing(File::getName));
        return liste;
    }

    /** Legt ein Protokoll oben auf den Stapel. Gibt false zurück, wenn das Speichern fehlschlug. */
    public static boolean ablegen(MinecraftServer server, UUID spieler, Stapel stapel, Protokoll protokoll) {
        if (protokoll.istLeer()) {
            return true;
        }
        File ordner = ordner(server, spieler, stapel);
        String name = String.format("%016d-%04d.dat", System.currentTimeMillis(), (zaehler++) % 10000);
        try {
            protokoll.speichern(new File(ordner, name));
        } catch (IOException fehler) {
            LOG.error("Weltenbauer: Verlauf konnte nicht gespeichert werden", fehler);
            return false;
        }
        File[] alle = dateien(ordner);
        for (int i = 0; i < alle.length - MAX_SCHRITTE; i++) {
            if (!alle[i].delete()) {
                LOG.warn("Weltenbauer: alte Verlaufsdatei konnte nicht gelöscht werden: {}", alle[i]);
            }
        }
        return true;
    }

    /** Nimmt das oberste Protokoll vom Stapel (oder null, wenn leer). */
    public static Protokoll nehmen(MinecraftServer server, UUID spieler, Stapel stapel) {
        File[] alle = dateien(ordner(server, spieler, stapel));
        if (alle.length == 0) {
            return null;
        }
        File oben = alle[alle.length - 1];
        try {
            Protokoll p = Protokoll.laden(oben);
            if (!oben.delete()) {
                LOG.warn("Weltenbauer: Verlaufsdatei konnte nicht gelöscht werden: {}", oben);
            }
            return p;
        } catch (IOException | RuntimeException fehler) {
            LOG.error("Weltenbauer: Verlaufsdatei ist beschädigt und wird entfernt: {}", oben, fehler);
            oben.delete();
            return null;
        }
    }

    public static int anzahl(MinecraftServer server, UUID spieler, Stapel stapel) {
        return dateien(ordner(server, spieler, stapel)).length;
    }

    public static void leeren(MinecraftServer server, UUID spieler, Stapel stapel) {
        for (File f : dateien(ordner(server, spieler, stapel))) {
            f.delete();
        }
    }
}

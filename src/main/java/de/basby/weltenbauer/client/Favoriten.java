package de.basby.weltenbauer.client;

import de.basby.weltenbauer.vorlagen.Vorlagen;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

/** Favoriten: per Rechtsklick markierte Vorlagen (Gruppen-IDs), gespeichert in weltenbauer/favoriten.txt. */
public final class Favoriten {

    private static Set<String> menge;

    private Favoriten() {
    }

    private static Path datei() {
        return Vorlagen.paketOrdner().getParent().resolve("favoriten.txt");
    }

    private static synchronized Set<String> menge() {
        if (menge == null) {
            menge = new LinkedHashSet<>();
            try {
                Path d = datei();
                if (Files.exists(d)) {
                    for (String z : Files.readAllLines(d, StandardCharsets.UTF_8)) {
                        if (!z.isBlank()) {
                            menge.add(z.trim());
                        }
                    }
                }
            } catch (IOException ignoriert) {
                // ohne Datei einfach leer
            }
        }
        return menge;
    }

    public static boolean ist(String gruppe) {
        return menge().contains(gruppe);
    }

    public static boolean leer() {
        return menge().isEmpty();
    }

    /** Schaltet um; gibt den neuen Zustand zurück. */
    public static synchronized boolean umschalten(String gruppe) {
        Set<String> m = menge();
        boolean an = !m.remove(gruppe);
        if (an) {
            m.add(gruppe);
        }
        try {
            Path d = datei();
            Files.createDirectories(d.getParent());
            Files.write(d, new ArrayList<>(m), StandardCharsets.UTF_8);
        } catch (IOException ignoriert) {
            // Speichern fehlgeschlagen – bleibt für diese Sitzung erhalten
        }
        return an;
    }

    public static List<String> alle() {
        return new ArrayList<>(menge());
    }
}

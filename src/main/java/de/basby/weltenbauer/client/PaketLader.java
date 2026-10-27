package de.basby.weltenbauer.client;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import de.basby.weltenbauer.vorlagen.Vorlagen;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

/**
 * Lädt neue Vorlagen-Pakete von GitHub in den Ordner weltenbauer/pakete – ohne die Mod neu zu installieren.
 * Es werden nur Pakete geladen, die fehlen oder sich geändert haben.
 */
public final class PaketLader {

    private static final Logger LOG = LoggerFactory.getLogger("Weltenbauer");
    private static final String BASIS = "https://github.com/Basby1/weltenbauer/releases/download/vorlagen-pakete/";

    private static volatile String status;
    private static volatile boolean laeuft;
    private static volatile boolean neuGeladen;

    private PaketLader() {
    }

    public static String status() {
        return status;
    }

    public static boolean laeuft() {
        return laeuft;
    }

    /** true genau einmal, nachdem neue Pakete angekommen sind (das Menü baut sich dann neu auf). */
    public static boolean neuGeladen() {
        boolean b = neuGeladen;
        neuGeladen = false;
        return b;
    }

    public static void starten() {
        if (laeuft) {
            return;
        }
        laeuft = true;
        status = "Suche nach neuen Vorlagen …";
        Thread t = new Thread(PaketLader::laden, "Weltenbauer-Pakete");
        t.setDaemon(true);
        t.start();
    }

    private static HttpRequest anfrage(String url) {
        return HttpRequest.newBuilder(URI.create(url)).timeout(Duration.ofMinutes(5))
                .header("User-Agent", "Weltenbauer-Mod").GET().build();
    }

    private static void laden() {
        try {
            HttpClient http = HttpClient.newBuilder().followRedirects(HttpClient.Redirect.ALWAYS)
                    .connectTimeout(Duration.ofSeconds(20)).build();
            HttpResponse<String> antwort = http.send(anfrage(BASIS + "pakete.json"),
                    HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
            if (antwort.statusCode() == 404) {
                status = "Noch keine Pakete online.";
                return;
            }
            if (antwort.statusCode() != 200) {
                throw new IOException("Server antwortet mit " + antwort.statusCode());
            }
            JsonObject index = JsonParser.parseString(antwort.body()).getAsJsonObject();
            Path ordner = Vorlagen.paketOrdner();
            Files.createDirectories(ordner);
            Path stand = ordner.resolve("installiert.json");
            JsonObject installiert = Files.exists(stand)
                    ? JsonParser.parseString(Files.readString(stand, StandardCharsets.UTF_8)).getAsJsonObject()
                    : new JsonObject();
            List<JsonObject> neu = new ArrayList<>();
            for (JsonElement el : index.getAsJsonArray("pakete")) {
                JsonObject p = el.getAsJsonObject();
                String datei = p.get("datei").getAsString();
                if (!datei.matches("[a-z0-9_\\-]+\\.zip")) {
                    continue;
                }
                String version = p.get("version").getAsString();
                boolean aktuell = Files.exists(ordner.resolve(datei)) && installiert.has(datei)
                        && installiert.get(datei).getAsString().equals(version);
                if (!aktuell) {
                    neu.add(p);
                }
            }
            if (neu.isEmpty()) {
                status = "Alles aktuell – du hast schon alle Vorlagen.";
                return;
            }
            int i = 0;
            String letzterName = "";
            for (JsonObject p : neu) {
                i++;
                String datei = p.get("datei").getAsString();
                letzterName = p.has("name") ? p.get("name").getAsString() : datei;
                double mb = p.has("groesse") ? p.get("groesse").getAsLong() / 1e6 : 0;
                status = String.format("Lade „%s“ (%d/%d, %.1f MB) …", letzterName, i, neu.size(), mb);
                Path teil = ordner.resolve(datei + ".teil");
                HttpResponse<Path> r = http.send(anfrage(BASIS + datei), HttpResponse.BodyHandlers.ofFile(teil));
                if (r.statusCode() != 200) {
                    Files.deleteIfExists(teil);
                    throw new IOException(letzterName + ": Server antwortet mit " + r.statusCode());
                }
                Files.move(teil, ordner.resolve(datei), StandardCopyOption.REPLACE_EXISTING);
                installiert.addProperty(datei, p.get("version").getAsString());
                Files.writeString(stand, installiert.toString(), StandardCharsets.UTF_8);
            }
            Vorlagen.paketeNeuLesen();
            neuGeladen = true;
            status = neu.size() == 1 ? "Neu geladen: „" + letzterName + "“" : neu.size() + " Pakete neu geladen.";
        } catch (Exception fehler) {
            LOG.warn("Weltenbauer: Pakete konnten nicht geladen werden", fehler);
            String text = fehler.getMessage() == null ? fehler.getClass().getSimpleName() : fehler.getMessage();
            status = "Laden fehlgeschlagen: " + text;
        } finally {
            laeuft = false;
        }
    }
}

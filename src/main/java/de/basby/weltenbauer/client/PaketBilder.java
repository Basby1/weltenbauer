package de.basby.weltenbauer.client;

import com.mojang.blaze3d.platform.NativeImage;
import de.basby.weltenbauer.vorlagen.Vorlagen;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.resources.ResourceLocation;

import java.io.ByteArrayInputStream;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/** Vorschaubilder aus Vorlagen-Paketen als Texturen bereitstellen. */
public final class PaketBilder {

    private static final Map<String, ResourceLocation> GELADEN = new HashMap<>();
    private static final Set<String> FEHLT = new HashSet<>();

    private PaketBilder() {
    }

    /** Textur für die Gruppe aus einem Paket oder null, wenn das Paket kein Bild dafür hat. */
    public static ResourceLocation bild(String gruppe) {
        ResourceLocation rl = GELADEN.get(gruppe);
        if (rl != null || FEHLT.contains(gruppe)) {
            return rl;
        }
        byte[] daten = Vorlagen.paketBild(gruppe);
        if (daten == null) {
            FEHLT.add(gruppe);
            return null;
        }
        try {
            NativeImage bild = NativeImage.read(new ByteArrayInputStream(daten));
            rl = new ResourceLocation("weltenbauer", "paket/" + gruppe.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9_]", "_"));
            Minecraft.getInstance().getTextureManager().register(rl, new DynamicTexture(bild));
            GELADEN.put(gruppe, rl);
            return rl;
        } catch (Exception fehler) {
            FEHLT.add(gruppe);
            return null;
        }
    }

    public static boolean istPaketBild(ResourceLocation rl) {
        return GELADEN.containsValue(rl);
    }

    /** Nach neuen Paketen: alles neu einlesen. */
    public static void leeren() {
        for (ResourceLocation rl : GELADEN.values()) {
            Minecraft.getInstance().getTextureManager().release(rl);
        }
        GELADEN.clear();
        FEHLT.clear();
    }
}

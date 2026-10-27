package de.basby.weltenbauer.client;

import de.basby.weltenbauer.vorlagen.Vorlagen;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Das Vorlagen-Menü: Reiter je Kategorie, darunter Karten mit Vorschaubild.
 * Klick = auf den Bauwerk-Stab legen, Shift-Klick = sofort setzen, Strg-Klick = Umriss zeigen.
 */
public class VorlagenMenue extends Screen {

    // Farben
    private static final int HINTERGRUND = 0xE6141619;
    private static final int RAHMEN = 0xFF3B3F48;
    private static final int GOLD = 0xFFE8B04A;
    private static final int TEXT = 0xFFE6E2D8;
    private static final int GRAU = 0xFF9A9A9A;
    private static final int KARTE = 0xFF232730;
    private static final int KARTE_HOVER = 0xFF323845;
    private static final int REITER = 0xFF2A2E37;
    private static final int REITER_AKTIV = 0xFF4A3A1C;

    private static final int KARTE_B = 68, KARTE_H = 86, BILD = 60, LUECKE = 5;

    private static String letzteKategorie;
    private static final Map<ResourceLocation, Boolean> BILD_DA = new HashMap<>();

    private record Karte(Vorlagen.Eintrag eintrag, int varianten, ResourceLocation bild) {
    }

    private record Reiter(String id, String name, int x, int y, int b) {
    }

    private final Map<String, String> kategorien = new LinkedHashMap<>();
    private final List<Reiter> reiter = new ArrayList<>();
    private final List<Karte> karten = new ArrayList<>();
    private String aktiv;
    private EditBox suche;
    private double scroll;
    private int px0, py0, px1, py1, gx0, gy0, gx1, gy1, spalten;

    public VorlagenMenue() {
        super(Component.literal("Weltenbauer – Vorlagen"));
    }

    @Override
    protected void init() {
        kategorien.clear();
        kategorien.putAll(Vorlagen.kategorien());
        if (aktiv == null) {
            aktiv = letzteKategorie != null && kategorien.containsKey(letzteKategorie) ? letzteKategorie
                    : kategorien.keySet().stream().findFirst().orElse("");
        }
        px0 = 10;
        py0 = 8;
        px1 = width - 10;
        py1 = height - 8;
        String alterText = suche != null ? suche.getValue() : "";
        suche = new EditBox(font, px1 - 150, py0 + 4, 142, 14, Component.literal("Suche"));
        suche.setHint(Component.literal("Suchen …"));
        suche.setValue(alterText);
        suche.setResponder(t -> {
            scroll = 0;
            neuAufbauen();
        });
        addRenderableWidget(suche);

        // Reiter (bei Bedarf in mehreren Zeilen)
        reiter.clear();
        int x = px0 + 6, y = py0 + 24;
        for (Map.Entry<String, String> k : kategorien.entrySet()) {
            int b = font.width(k.getValue()) + 14;
            if (x + b > px1 - 6) {
                x = px0 + 6;
                y += 18;
            }
            reiter.add(new Reiter(k.getKey(), k.getValue(), x, y, b));
            x += b + 3;
        }
        gx0 = px0 + 6;
        gy0 = y + 22;
        gx1 = px1 - 10;
        gy1 = py1 - 18;
        spalten = Math.max(1, (gx1 - gx0 + LUECKE) / (KARTE_B + LUECKE));
        neuAufbauen();
    }

    private void neuAufbauen() {
        karten.clear();
        String filter = suche == null ? "" : suche.getValue().trim().toLowerCase(Locale.ROOT);
        Map<String, Karte> nachGruppe = new LinkedHashMap<>();
        for (Vorlagen.Eintrag e : Vorlagen.alle()) {
            boolean passt = filter.isEmpty() ? e.kategorie().equals(aktiv)
                    : (e.titel() + " " + e.gruppe() + " " + e.kategorieName()).toLowerCase(Locale.ROOT).contains(filter);
            if (!passt) {
                continue;
            }
            Karte alt = nachGruppe.get(e.gruppe());
            if (alt == null) {
                ResourceLocation bild = new ResourceLocation("weltenbauer", "textures/gui/vorschau/" + e.gruppe() + ".png");
                nachGruppe.put(e.gruppe(), new Karte(e, 1, bild));
            } else {
                nachGruppe.put(e.gruppe(), new Karte(alt.eintrag(), alt.varianten() + 1, alt.bild()));
            }
        }
        karten.addAll(nachGruppe.values());
    }

    private boolean bildVorhanden(ResourceLocation rl) {
        return BILD_DA.computeIfAbsent(rl, r -> Minecraft.getInstance().getResourceManager().getResource(r).isPresent());
    }

    private int maxScroll() {
        int zeilen = (karten.size() + spalten - 1) / spalten;
        return Math.max(0, zeilen * (KARTE_H + LUECKE) - (gy1 - gy0));
    }

    // ------------------------------------------------------------------ Zeichnen

    @Override
    public void render(GuiGraphics g, int mx, int my, float partial) {
        renderBackground(g);
        g.fill(px0, py0, px1, py1, HINTERGRUND);
        g.renderOutline(px0, py0, px1 - px0, py1 - py0, RAHMEN);
        g.drawString(font, "Weltenbauer", px0 + 8, py0 + 7, GOLD, true);
        g.drawString(font, "· Vorlagen", px0 + 8 + font.width("Weltenbauer "), py0 + 7, TEXT, false);

        boolean suchModus = !suche.getValue().isBlank();
        for (Reiter r : reiter) {
            boolean an = !suchModus && r.id().equals(aktiv);
            boolean hover = mx >= r.x() && mx < r.x() + r.b() && my >= r.y() && my < r.y() + 15;
            g.fill(r.x(), r.y(), r.x() + r.b(), r.y() + 15, an ? REITER_AKTIV : hover ? KARTE_HOVER : REITER);
            if (an) {
                g.fill(r.x(), r.y() + 13, r.x() + r.b(), r.y() + 15, GOLD);
            }
            g.drawString(font, r.name(), r.x() + 7, r.y() + 4, an ? GOLD : TEXT, false);
        }

        // Karten
        scroll = Mth.clamp(scroll, 0, maxScroll());
        g.enableScissor(gx0, gy0, gx1, gy1);
        Karte unterMaus = null;
        for (int i = 0; i < karten.size(); i++) {
            int x = gx0 + (i % spalten) * (KARTE_B + LUECKE);
            int y = gy0 + (i / spalten) * (KARTE_H + LUECKE) - (int) scroll;
            if (y + KARTE_H < gy0 || y > gy1) {
                continue;
            }
            Karte k = karten.get(i);
            boolean hover = mx >= x && mx < x + KARTE_B && my >= y && my < y + KARTE_H && my >= gy0 && my < gy1;
            if (hover) {
                unterMaus = k;
            }
            g.fill(x, y, x + KARTE_B, y + KARTE_H, hover ? KARTE_HOVER : KARTE);
            g.renderOutline(x, y, KARTE_B, KARTE_H, hover ? GOLD : RAHMEN);
            int bx = x + (KARTE_B - BILD) / 2, by = y + 4;
            if (bildVorhanden(k.bild())) {
                g.blit(k.bild(), bx, by, BILD, BILD, 0f, 0f, 128, 128, 128, 128);
            } else {
                g.fill(bx, by, bx + BILD, by + BILD, 0xFF1A1D23);
                g.drawCenteredString(font, ".nbt", bx + BILD / 2, by + BILD / 2 - 4, GRAU);
            }
            String titel = font.plainSubstrByWidth(k.eintrag().titel(), KARTE_B - 6);
            g.drawCenteredString(font, titel, x + KARTE_B / 2, y + BILD + 6, TEXT);
            String unter = font.plainSubstrByWidth(k.eintrag().groesse()
                    + (k.varianten() > 1 ? " · " + k.varianten() + "×" : ""), KARTE_B - 4);
            g.drawCenteredString(font, unter, x + KARTE_B / 2, y + BILD + 16, GRAU);
        }
        g.disableScissor();

        // Bildlaufleiste
        int max = maxScroll();
        if (max > 0) {
            int hoehe = gy1 - gy0;
            int griff = Math.max(20, hoehe * hoehe / (hoehe + max));
            int gy = gy0 + (int) ((hoehe - griff) * (scroll / max));
            g.fill(px1 - 7, gy0, px1 - 4, gy1, 0xFF22252C);
            g.fill(px1 - 7, gy, px1 - 4, gy + griff, GOLD);
        }

        if (karten.isEmpty()) {
            g.drawCenteredString(font, suchModus ? "Nichts gefunden." : "Keine Vorlagen in dieser Kategorie.",
                    (gx0 + gx1) / 2, gy0 + 30, GRAU);
        }
        g.drawString(font, "Klick: auf den Bauwerk-Stab   Shift-Klick: sofort setzen   Strg-Klick: Umriss zeigen",
                px0 + 8, py1 - 13, GRAU, false);

        super.render(g, mx, my, partial);

        if (unterMaus != null) {
            Vorlagen.Eintrag e = unterMaus.eintrag();
            List<Component> zeilen = new ArrayList<>();
            zeilen.add(Component.literal(e.titel()).withStyle(s -> s.withColor(GOLD & 0xFFFFFF)));
            if (e.masse()[0] > 0) {
                zeilen.add(Component.literal("Größe: " + e.groesse() + " – " + e.masse()[0] + " × " + e.masse()[1]
                        + " × " + e.masse()[2] + " Blöcke"));
            }
            if (unterMaus.varianten() > 1) {
                zeilen.add(Component.literal(unterMaus.varianten() + " Varianten (jedes Setzen zufällig)"));
            }
            if (e.hinweis() != null) {
                zeilen.add(Component.literal("Tipp: " + e.hinweis()));
            }
            g.renderComponentTooltip(font, zeilen, mx, my);
        }
    }

    // ------------------------------------------------------------------ Eingaben

    @Override
    public boolean mouseClicked(double mx, double my, int taste) {
        if (super.mouseClicked(mx, my, taste)) {
            return true;
        }
        for (Reiter r : reiter) {
            if (mx >= r.x() && mx < r.x() + r.b() && my >= r.y() && my < r.y() + 15) {
                aktiv = r.id();
                letzteKategorie = aktiv;
                suche.setValue("");
                scroll = 0;
                neuAufbauen();
                return true;
            }
        }
        if (my < gy0 || my >= gy1) {
            return false;
        }
        for (int i = 0; i < karten.size(); i++) {
            int x = gx0 + (i % spalten) * (KARTE_B + LUECKE);
            int y = gy0 + (i / spalten) * (KARTE_H + LUECKE) - (int) scroll;
            if (mx >= x && mx < x + KARTE_B && my >= y && my < y + KARTE_H) {
                String gruppe = karten.get(i).eintrag().gruppe();
                String befehl;
                if (hasShiftDown()) {
                    befehl = "wb vorlage setzen " + gruppe;
                } else if (hasControlDown()) {
                    befehl = "wb vorlage zeigen " + gruppe;
                } else {
                    befehl = "wb vorlage waehlen " + gruppe;
                }
                Minecraft mc = Minecraft.getInstance();
                if (mc.player != null) {
                    mc.player.connection.sendCommand(befehl);
                }
                onClose();
                return true;
            }
        }
        return false;
    }

    @Override
    public boolean mouseScrolled(double mx, double my, double delta) {
        scroll = Mth.clamp(scroll - delta * 30, 0, maxScroll());
        return true;
    }

    @Override
    public boolean keyPressed(int taste, int scancode, int mods) {
        if (!suche.isFocused() && WeltenbauerClient.MENUE_TASTE.matches(taste, scancode)) {
            onClose();
            return true;
        }
        return super.keyPressed(taste, scancode, mods);
    }

    @Override
    public void onClose() {
        letzteKategorie = aktiv;
        super.onClose();
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}

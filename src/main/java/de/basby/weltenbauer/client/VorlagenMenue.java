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
 * Klick = auf den Bauwerk-Stab legen, Shift-Klick = sofort setzen, Rechtsklick = Favorit an/aus.
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

    /** Ein Eintrag im Reiter „Befehle“: Überschrift (befehl == null) oder Befehl mit Erklärung. */
    private record Befehl(String befehl, String erklaerung, String vorbelegung) {
    }

    private static final String BEFEHLE = "befehle";
    private static final String FAVORITEN = "favoriten";
    private static final int ZEILE = 13;
    private static final List<Befehl> BEFEHLSLISTE = List.of(
            new Befehl(null, "Aufräumen", null),
            new Befehl("/wb schnee entfernen <Radius>", "Schneeschichten entfernen (+ „alles“: auch Schneeblöcke)",
                    "/wb schnee entfernen 50"),
            new Befehl("/wb eis auftauen <Radius>", "zugefrorenes Wasser wird wieder Wasser", "/wb eis auftauen 50"),
            new Befehl("/wb laub aufraeumen <Radius>", "schwebende Blätter ohne Stamm entfernen", "/wb laub aufraeumen 50"),
            new Befehl("/wb entfernen <Block> <Radius>", "eine Blocksorte entfernen", "/wb entfernen "),
            new Befehl("/wb ersetzen <Block> <Block> <Radius>", "eine Blocksorte austauschen", "/wb ersetzen "),
            new Befehl("/wb glaetten <Radius> [Stärke]", "kantiges Gelände glätten und weich an die Umgebung anpassen (Stärke 1–10, Standard 3)",
                    "/wb glaetten "),
            new Befehl(null, "Bereich statt Radius", null),
            new Befehl("/wb stab", "Terraforming-Stab holen (Rechtsklick Ecke 1, Schleichen Ecke 2)", "/wb stab"),
            new Befehl("… auswahl", "statt <Radius> überall „auswahl“ schreiben, z. B. /wb schnee entfernen auswahl",
                    "/wb schnee entfernen auswahl"),
            new Befehl("/wb auswahl [leeren]", "markierten Bereich anzeigen / löschen", "/wb auswahl"),
            new Befehl(null, "Rückgängig & Steuerung", null),
            new Befehl("/wb rueckgaengig", "letzte Änderung zurücknehmen (bis zu 10 Schritte)", "/wb rueckgaengig"),
            new Befehl("/wb wiederholen", "zurückgenommene Änderung erneut ausführen", "/wb wiederholen"),
            new Befehl("/wb abbrechen", "laufende Aktion stoppen", "/wb abbrechen"),
            new Befehl("/wb status", "zeigt, was gerade läuft", "/wb status"),
            new Befehl(null, "Vorlagen", null),
            new Befehl("/wb vorlage setzen <Name> [Drehung] [spiegeln]", "Vorlage dorthin bauen, wohin du schaust",
                    "/wb vorlage setzen "),
            new Befehl("/wb vorlage create <Name>", "als Schematic für Create / Litematica speichern",
                    "/wb vorlage create "),
            new Befehl("/wb vorlage ordner", "Ordner für eigene .nbt-Vorlagen anzeigen", "/wb vorlage ordner"),
            new Befehl(null, "Blaupausen", null),
            new Befehl("/wbblaupause drucken", "nächste Blaupause fertig bauen lassen", "/wbblaupause drucken"),
            new Befehl("/wbblaupause schicht <Nr>", "nur eine Schicht anzeigen (0 = alle) – oder Strg+Mausrad",
                    "/wbblaupause schicht "),
            new Befehl("/wbblaupause entfernen", "nächste Blaupause entfernen", "/wbblaupause entfernen"),
            new Befehl("/wbblaupause alle_entfernen", "alle Blaupausen dieser Welt entfernen",
                    "/wbblaupause alle_entfernen"));

    private final Map<String, String> kategorien = new LinkedHashMap<>();
    private final List<Reiter> reiter = new ArrayList<>();
    private final List<Karte> karten = new ArrayList<>();
    private String aktiv;
    private EditBox suche;
    private double scroll;
    private int px0, py0, px1, py1, gx0, gy0, gx1, gy1, spalten, modusX;

    public VorlagenMenue() {
        super(Component.literal("Weltenbauer – Vorlagen"));
    }

    @Override
    protected void init() {
        kategorien.clear();
        kategorien.put(FAVORITEN, "★ Favoriten");
        kategorien.putAll(Vorlagen.kategorien());
        kategorien.put(BEFEHLE, "Befehle");
        if (aktiv == null) {
            aktiv = letzteKategorie != null && kategorien.containsKey(letzteKategorie) ? letzteKategorie
                    : !Favoriten.leer() ? FAVORITEN
                    : kategorien.keySet().stream().skip(1).findFirst().orElse("");
        }
        px0 = 10;
        py0 = 8;
        px1 = width - 10;
        py1 = height - 8;
        String alterText = suche != null ? suche.getValue() : "";
        suche = new EditBox(font, px1 - 150, py0 + 4, 142, 14, Component.literal("Suche"));
        modusX = px1 - 150 - 8 - font.width("Drucken") - font.width("Blaupause") - 30;
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
            boolean passt = filter.isEmpty()
                    ? (FAVORITEN.equals(aktiv) ? Favoriten.ist(e.gruppe()) : e.kategorie().equals(aktiv))
                    : (e.titel() + " " + e.gruppe() + " " + e.kategorieName()).toLowerCase(Locale.ROOT).contains(filter);
            if (!passt) {
                continue;
            }
            Karte alt = nachGruppe.get(e.gruppe());
            if (alt == null) {
                ResourceLocation bild = PaketBilder.bild(e.gruppe());
                if (bild == null) {
                    bild = new ResourceLocation("weltenbauer", "textures/gui/vorschau/" + e.gruppe() + ".png");
                }
                nachGruppe.put(e.gruppe(), new Karte(e, 1, bild));
            } else {
                nachGruppe.put(e.gruppe(), new Karte(alt.eintrag(), alt.varianten() + 1, alt.bild()));
            }
        }
        karten.addAll(nachGruppe.values());
    }

    private boolean bildVorhanden(ResourceLocation rl) {
        if (PaketBilder.istPaketBild(rl)) {
            return true;
        }
        return BILD_DA.computeIfAbsent(rl, r -> Minecraft.getInstance().getResourceManager().getResource(r).isPresent());
    }

    private static final String LADEN = "Neue Vorlagen laden";

    private int ladenX0() {
        return px1 - 10 - (font.width(LADEN) + 12);
    }

    private boolean ueberLaden(double mx, double my) {
        return mx >= ladenX0() && mx < px1 - 10 && my >= py1 - 16 && my < py1 - 3;
    }

    private boolean befehlsReiter() {
        return BEFEHLE.equals(aktiv) && suche.getValue().isBlank();
    }

    private int maxScroll() {
        if (befehlsReiter()) {
            return Math.max(0, BEFEHLSLISTE.size() * ZEILE + 10 - (gy1 - gy0));
        }
        int zeilen = (karten.size() + spalten - 1) / spalten;
        return Math.max(0, zeilen * (KARTE_H + LUECKE) - (gy1 - gy0));
    }

    // ------------------------------------------------------------------ Zeichnen

    @Override
    public void render(GuiGraphics g, int mx, int my, float partial) {
        if (PaketLader.neuGeladen()) {
            PaketBilder.leeren();
            rebuildWidgets();
        }
        renderBackground(g);
        g.fill(px0, py0, px1, py1, HINTERGRUND);
        g.renderOutline(px0, py0, px1 - px0, py1 - py0, RAHMEN);
        g.drawString(font, "Weltenbauer", px0 + 8, py0 + 7, GOLD, true);
        g.drawString(font, "· Vorlagen", px0 + 8 + font.width("Weltenbauer "), py0 + 7, TEXT, false);

        // Modus: Drucken | Blaupause
        int bx0 = modusX, bw1 = font.width("Drucken") + 12, bw2 = font.width("Blaupause") + 12;
        boolean drucken = Platzierung.modus == Platzierung.Modus.DRUCKEN;
        g.drawString(font, "Modus:", bx0 - font.width("Modus: ") - 2, py0 + 7, GRAU, false);
        g.fill(bx0, py0 + 4, bx0 + bw1, py0 + 18, drucken ? 0xFF2E6B3A : REITER);
        g.drawString(font, "Drucken", bx0 + 6, py0 + 7, drucken ? 0xFFFFFFFF : GRAU, false);
        g.fill(bx0 + bw1 + 2, py0 + 4, bx0 + bw1 + 2 + bw2, py0 + 18, !drucken ? 0xFF2C5A8A : REITER);
        g.drawString(font, "Blaupause", bx0 + bw1 + 8, py0 + 7, !drucken ? 0xFFFFFFFF : GRAU, false);
        boolean ueberModus = my >= py0 + 4 && my < py0 + 18 && mx >= bx0 && mx < bx0 + bw1 + 2 + bw2;

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

        scroll = Mth.clamp(scroll, 0, maxScroll());
        Karte unterMaus = null;
        if (befehlsReiter()) {
            g.enableScissor(gx0, gy0, gx1, gy1);
            int y = gy0 + 4 - (int) scroll;
            for (Befehl b : BEFEHLSLISTE) {
                if (b.befehl() == null) {
                    g.drawString(font, b.erklaerung(), gx0 + 4, y + 2, GOLD, false);
                    g.fill(gx0 + 4, y + 11, gx1 - 8, y + 12, RAHMEN);
                } else {
                    boolean hover = my >= y && my < y + ZEILE && mx >= gx0 && mx < gx1 && my >= gy0 && my < gy1;
                    if (hover) {
                        g.fill(gx0 + 2, y, gx1 - 6, y + ZEILE, KARTE_HOVER);
                    }
                    g.drawString(font, b.befehl(), gx0 + 10, y + 3, hover ? GOLD : TEXT, false);
                    g.drawString(font, b.erklaerung(), gx0 + 10 + Math.max(200, font.width(b.befehl()) + 12), y + 3,
                            GRAU, false);
                }
                y += ZEILE;
            }
            g.disableScissor();
        }
        // Karten
        g.enableScissor(gx0, gy0, gx1, gy1);
        for (int i = 0; i < (befehlsReiter() ? 0 : karten.size()); i++) {
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
            if (Favoriten.ist(k.eintrag().gruppe())) {
                g.drawString(font, "★", x + KARTE_B - 10, y + 3, GOLD, true);
            }
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

        if (karten.isEmpty() && !befehlsReiter()) {
            g.drawCenteredString(font, suchModus ? "Nichts gefunden."
                            : FAVORITEN.equals(aktiv) ? "Noch keine Favoriten – Rechtsklick auf eine Vorlage merkt sie hier."
                            : "Keine Vorlagen in dieser Kategorie.",
                    (gx0 + gx1) / 2, gy0 + 30, GRAU);
        }
        String status = PaketLader.status();
        g.drawString(font, status != null ? status : befehlsReiter() ? "Klick: Befehl in den Chat übernehmen"
                        : "Klick: auf den Stab legen  ·  Shift-Klick: sofort bauen  ·  Rechtsklick: Favorit ★",
                px0 + 8, py1 - 13, status != null ? GOLD : GRAU, false);
        boolean ladenHover = ueberLaden(mx, my);
        boolean laeuft = PaketLader.laeuft();
        g.fill(ladenX0(), py1 - 16, px1 - 10, py1 - 3, laeuft ? REITER : ladenHover ? 0xFF3A7A48 : 0xFF2E6B3A);
        g.drawString(font, laeuft ? "Lädt …" : LADEN, ladenX0() + 6, py1 - 13, 0xFFFFFFFF, false);

        super.render(g, mx, my, partial);

        if (ladenHover) {
            g.renderComponentTooltip(font, List.of(
                    Component.literal("Lädt neue Vorlagen-Pakete aus dem Internet"),
                    Component.literal("in den Ordner weltenbauer/pakete – ohne die Mod neu zu installieren.")), mx, my);
        } else if (ueberModus) {
            g.renderComponentTooltip(font, List.of(
                    Component.literal("Drucken: Vorlage wird beim Bestätigen gebaut"),
                    Component.literal("Blaupause: Geisterbild bleibt stehen zum Nachbauen")), mx, my);
        } else if (unterMaus != null) {
            Vorlagen.Eintrag e = unterMaus.eintrag();
            List<Component> zeilen = new ArrayList<>();
            zeilen.add(Component.literal(e.titel()).withStyle(s -> s.withColor(GOLD & 0xFFFFFF)));
            if (e.masse()[0] > 0) {
                zeilen.add(Component.literal("Größe: " + e.groesse() + " – " + e.masse()[0] + " × " + e.masse()[1]
                        + " × " + e.masse()[2] + " Blöcke"));
            }
            zeilen.add(Component.literal(Favoriten.ist(e.gruppe()) ? "★ Favorit – Rechtsklick entfernt"
                    : "Rechtsklick: zu den Favoriten").withStyle(s -> s.withColor(GRAU & 0xFFFFFF)));
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
        if (ueberLaden(mx, my)) {
            PaketLader.starten();
            return true;
        }
        int bw1 = font.width("Drucken") + 12, bw2 = font.width("Blaupause") + 12;
        if (my >= py0 + 4 && my < py0 + 18) {
            if (mx >= modusX && mx < modusX + bw1) {
                Platzierung.modus = Platzierung.Modus.DRUCKEN;
                return true;
            }
            if (mx >= modusX + bw1 + 2 && mx < modusX + bw1 + 2 + bw2) {
                Platzierung.modus = Platzierung.Modus.BLAUPAUSE;
                return true;
            }
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
        if (befehlsReiter()) {
            int y = gy0 + 4 - (int) scroll;
            for (Befehl b : BEFEHLSLISTE) {
                if (b.befehl() != null && my >= y && my < y + ZEILE) {
                    Minecraft.getInstance().setScreen(new net.minecraft.client.gui.screens.ChatScreen(b.vorbelegung()));
                    return true;
                }
                y += ZEILE;
            }
            return false;
        }
        for (int i = 0; i < karten.size(); i++) {
            int x = gx0 + (i % spalten) * (KARTE_B + LUECKE);
            int y = gy0 + (i / spalten) * (KARTE_H + LUECKE) - (int) scroll;
            if (mx >= x && mx < x + KARTE_B && my >= y && my < y + KARTE_H) {
                String gruppe = karten.get(i).eintrag().gruppe();
                if (taste == 1) {
                    Favoriten.umschalten(gruppe);
                    if (FAVORITEN.equals(aktiv) && suche.getValue().isBlank()) {
                        neuAufbauen();
                    }
                    return true;
                }
                String befehl;
                if (hasShiftDown()) {
                    befehl = "wb vorlage setzen " + gruppe;
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

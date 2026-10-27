package de.basby.weltenbauer.client;

import de.basby.weltenbauer.TerraformingStab;
import de.basby.weltenbauer.vorlagen.BauwerkStab;
import de.basby.weltenbauer.vorlagen.Vorlagen;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.client.gui.overlay.ForgeGui;

import java.util.Map;

/** HUD: Werkzeugleiste des Bauwerk-Stabs, Tastenhinweise und Materialliste der nächsten Blaupause. */
public final class Hud {

    private static final int GOLD = 0xFFE8B04A, TEXT = 0xFFE6E2D8, GRAU = 0xFFA0A0A0, ROT = 0xFFE05050;
    private static final int KASTEN = 0xC0141619, KASTEN_AN = 0xE04A3A1C, RAHMEN = 0xFF3B3F48;

    private Hud() {
    }

    public static void zeichnen(ForgeGui gui, GuiGraphics g, float partial, int breite, int hoehe) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.options.hideGui || mc.screen != null) {
            return;
        }
        Font font = mc.font;
        ItemStack hand = mc.player.getMainHandItem();
        int unten = hoehe - (mc.player.isCreative() ? 50 : 66);

        if (hand.getItem() instanceof BauwerkStab) {
            if (!Platzierung.aktiv()) {
                hinweis(g, font, breite, unten, "Rechtsklick: Vorlagen-Menü öffnen");
            } else {
                werkzeugleiste(g, font, breite, unten);
            }
        } else if (hand.getItem() instanceof TerraformingStab) {
            hinweis(g, font, breite, unten, "Rechtsklick: Ecke 1   ·   Schleichen + Rechtsklick: Ecke 2   ·   Befehle: Taste B → Befehle");
        }
        materialliste(g, font, breite, hoehe);
    }

    private static void hinweis(GuiGraphics g, Font font, int breite, int y, String text) {
        int w = font.width(text) + 12;
        int x = (breite - w) / 2;
        g.fill(x, y, x + w, y + 13, KASTEN);
        g.drawString(font, text, x + 6, y + 3, GRAU, false);
    }

    private static void werkzeugleiste(GuiGraphics g, Font font, int breite, int unten) {
        Vorlagen.Eintrag e = Platzierung.eintrag();
        boolean ab = Platzierung.abgesetzt();
        Platzierung.Werkzeug[] alle = Platzierung.Werkzeug.values();
        int kb = 58, kh = 22, abstand = 2;
        int gesamt = alle.length * (kb + abstand) - abstand;
        int x0 = (breite - gesamt) / 2;
        int y0 = unten - kh - 14;

        // Kopfzeile: Name und Modus
        String kopf = e.titel() + " · " + e.groesse();
        String modus = Platzierung.modus == Platzierung.Modus.DRUCKEN ? "DRUCKEN" : "BLAUPAUSE";
        int kw = font.width(kopf) + font.width(modus) + 26;
        int kx = (breite - kw) / 2;
        g.fill(kx, y0 - 15, kx + kw, y0 - 2, KASTEN);
        g.drawString(font, kopf, kx + 6, y0 - 12, TEXT, false);
        int mx = kx + 6 + font.width(kopf) + 8;
        g.fill(mx - 3, y0 - 14, mx + font.width(modus) + 3, y0 - 3,
                Platzierung.modus == Platzierung.Modus.DRUCKEN ? 0xFF2E6B3A : 0xFF2C5A8A);
        g.drawString(font, modus, mx, y0 - 12, 0xFFFFFFFF, false);

        // Werkzeuge
        for (int i = 0; i < alle.length; i++) {
            Platzierung.Werkzeug w = alle[i];
            int x = x0 + i * (kb + abstand);
            boolean an = ab && Platzierung.werkzeug() == w;
            g.fill(x, y0, x + kb, y0 + kh, an ? KASTEN_AN : KASTEN);
            g.renderOutline(x, y0, kb, kh, an ? GOLD : RAHMEN);
            int farbeName = !ab ? 0xFF707070 : an ? GOLD : TEXT;
            g.drawCenteredString(font, w.name, x + kb / 2, y0 + 3, farbeName);
            String wert = font.plainSubstrByWidth(Platzierung.wertText(w), kb - 4);
            g.drawCenteredString(font, wert, x + kb / 2, y0 + 12, ab ? GRAU : 0xFF606060);
        }

        // Tastenhinweis
        String text = ab
                ? "Strg+Mausrad: Werkzeug   ·   Mausrad: verstellen   ·   Rechtsklick: "
                + (Platzierung.modus == Platzierung.Modus.DRUCKEN ? "bauen" : "als Blaupause behalten")
                + "   ·   Schleichen+Rechtsklick: zurück"
                : "Rechtsklick: hier absetzen   ·   Schleichen+Rechtsklick: Menü";
        hinweis(g, font, breite, y0 + kh + 2, text);
    }

    private static void materialliste(GuiGraphics g, Font font, int breite, int hoehe) {
        Blaupausen.Blaupause b = Blaupausen.naechste(40);
        if (b == null || b.gesamt() == 0) {
            return;
        }
        Map<Block, Integer> fehlend = b.fehlend();
        int zeilen = Math.min(9, fehlend.size());
        int w = 150, h = 34 + zeilen * 17 + (fehlend.size() > 9 ? 10 : 0) + 12;
        int x = breite - w - 6, y = 40;
        g.fill(x, y, x + w, y + h, KASTEN);
        g.renderOutline(x, y, w, h, RAHMEN);
        g.drawString(font, font.plainSubstrByWidth("Blaupause: " + b.titel(), w - 10), x + 5, y + 4, GOLD, false);
        int prozent = (int) (100L * b.fertig() / Math.max(1, b.gesamt()));
        g.drawString(font, b.fertig() + " / " + b.gesamt() + " Blöcke (" + prozent + " %)", x + 5, y + 15, TEXT, false);
        g.fill(x + 5, y + 26, x + w - 5, y + 29, 0xFF2A2E37);
        g.fill(x + 5, y + 26, x + 5 + (w - 10) * prozent / 100, y + 29, GOLD);
        int zy = y + 34;
        int n = 0;
        for (Map.Entry<Block, Integer> m : fehlend.entrySet()) {
            if (n++ >= 9) {
                break;
            }
            ItemStack bild = new ItemStack(m.getKey().asItem());
            if (!bild.isEmpty()) {
                g.renderItem(bild, x + 4, zy);
            }
            String name = font.plainSubstrByWidth(m.getKey().getName().getString(), w - 60);
            g.drawString(font, name, x + 23, zy + 4, TEXT, false);
            String anzahl = "×" + m.getValue();
            g.drawString(font, anzahl, x + w - 6 - font.width(anzahl), zy + 4, GOLD, false);
            zy += 17;
        }
        if (fehlend.size() > 9) {
            g.drawString(font, "… und " + (fehlend.size() - 9) + " weitere", x + 5, zy, GRAU, false);
            zy += 10;
        }
        String unten = b.falsch() > 0 ? b.falsch() + " falsche Blöcke (rot)" : "Schicht: "
                + (b.schicht() == 0 ? "alle" : b.schicht() + "/" + b.hoehe()) + " (Strg+Mausrad)";
        g.drawString(font, font.plainSubstrByWidth(unten, w - 10), x + 5, zy + 1, b.falsch() > 0 ? ROT : GRAU, false);
    }
}

"""Himmelsstadt: schwebende Inseln mit einheitlichem Farbschema zum Kombinieren.

Farbschema (überall gleich):
  Fels unten → oben:  deepslate › cobbled_deepslate › tuff › andesite › stone   (Verlauf)
  Wände:              calcite / smooth_sandstone mit dunklem Eichenrahmen
  Dächer:             Kupfer-Verlauf (dark_prismarine › oxidized cut copper › prismarine bricks › weathered)
  Kanten/Zier:        smooth_sandstone, Laternen an Ketten, Moos und Ranken

Größen: 0 klein · 1 mittel · 2 riesig · 3 gigantisch
Der Anker liegt auf dem Boden unter der Insel – die Insel schwebt darüber (Höhe mit der Werkzeugleiste anpassen).
"""

from __future__ import annotations

import math

import numpy as np

from baeume import birke, eiche, kirschbaum, azaleenbaum
from lib import Rauschen, Verlauf, Welt, einfuegen, laub, ueberwuchern
from riesenbogen import fantasiehaus, haengelaterne, kette, zahnrad

GROESSEN = [(0, "klein", "klein"), (1, "mittel", "mittel"), (2, "riesig", "riesig"), (3, "gigantisch", "gigantisch")]


class Schema:
    def __init__(self, w: Welt):
        self.fels = Verlauf(w, "Fels", ["deepslate", "cobbled_deepslate", "tuff", "andesite", "stone"])
        self.wand = Verlauf(w, "Mauer", ["andesite", "stone_bricks", "calcite", "smooth_quartz"])
        self.dach = Verlauf(w, "Kupferdach", ["dark_prismarine", "waxed_oxidized_cut_copper", "prismarine_bricks",
                                              "waxed_weathered_cut_copper"])
        self.gras, self.erde, self.moos = w.b("grass_block", snowy=False), w.b("dirt"), w.b("moss_block")
        self.kante = w.b("smooth_sandstone")
        self.planke = w.b("dark_oak_planks")
        self.weg = Verlauf(w, "Weg", ["cobblestone", "andesite", "stone_bricks", "polished_andesite"])


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def insel(w: Welt, sch: Schema, rs, cx, top, cz, R, T, flach=0.6, extras=True):
    """Schwebende Insel: zerklüftete Unterseite aus mehreren Felszapfen mit Farbverlauf, Felskante oben,
    dazu (extras) Wasserfall über den Rand, Kristalle und kleine schwebende Begleitbrocken.
    Gibt {(x,z): y_oben} zurück."""
    T = T * 1.5
    zapfen = []
    for k in range(3 + int(w.rng.random() * 4)):
        a = w.rng.random() * 2 * math.pi
        d = R * (0.15 + 0.55 * w.rng.random())
        zapfen.append((cx + math.cos(a) * d, cz + math.sin(a) * d, R * (0.25 + 0.3 * w.rng.random()),
                       T * (0.5 + 0.7 * w.rng.random())))
    oben = {}
    for x in range(int(cx - R) - 3, int(cx + R) + 4):
        for z in range(int(cz - R) - 3, int(cz + R) + 4):
            d = math.hypot(x - cx, z - cz) / R
            d *= 0.88 + 0.3 * rs(x, 0, z)
            if d > 1:
                continue
            tiefe = T * 0.55 * (1 - d) ** 0.9
            for zx, zz, zr, zl in zapfen:
                dz_ = math.hypot(x - zx, z - zz) / zr
                if dz_ < 1:
                    tiefe = max(tiefe, zl * (1 - dz_) ** 1.4)
            tiefe = int(tiefe * (0.8 + 0.4 * rs(x * 1.7, 30, z * 1.7))) + 2
            buckel = 0 if d < flach else int(1.5 * (1 - d) * rs(x, 60, z))
            y0 = top + buckel
            # Felskante am Rand
            kante = d > 0.86 and rs(x * 2, 90, z * 2) > 0.55
            if kante:
                y0 += 1 + int(rs(x * 3, 91, z * 3) * 2.5)
            oben[(x, z)] = y0
            for y in range(y0 - tiefe, y0 + 1):
                if y == y0 and not kante:
                    b = sch.gras
                elif y > y0 - 3 and not kante:
                    b = sch.erde
                else:
                    anteil = (y - (y0 - tiefe)) / max(1, tiefe)
                    b = sch.fels(anteil * 4.2 + (rs(x * 2, y * 2, z * 2) - 0.5) * 0.9, x, y, z)
                w.setze(x, y, z, b)
    if extras:
        _dramatik(w, sch, rs, oben, cx, cz, top, R, T)
    return oben


def _dramatik(w: Welt, sch: Schema, rs, oben, cx, cz, top, R, T):
    # Wasserfall über den Rand
    if w.rng.random() < 0.75 and oben:
        a = w.rng.random() * 2 * math.pi
        rand = max(oben, key=lambda p: (p[0] - cx) * math.cos(a) + (p[1] - cz) * math.sin(a))
        x, z = rand
        wasser = w.b("water", level=0)
        quelle = (int(cx + (x - cx) * 0.6), int(cz + (z - cz) * 0.6))
        n = max(abs(x - quelle[0]), abs(z - quelle[1])) + 1
        for i in range(n):
            px = round(quelle[0] + (x - quelle[0]) * i / max(1, n - 1))
            pz = round(quelle[1] + (z - quelle[1]) * i / max(1, n - 1))
            if (px, pz) in oben:
                w.setze(px, oben[(px, pz)], pz, wasser)
        w.vorschau_extra = getattr(w, "vorschau_extra", {})
        nx, nz = x + round(math.cos(a)), z + round(math.sin(a))
        for yy in range(1, oben[rand] + 1):
            w.vorschau_extra[(nx, yy, nz)] = wasser
    # Leuchtende Kristalle an der Unterseite
    fels = set(sch.fels.ids)
    kristall = w.b("amethyst_cluster", facing="down", waterlogged=False)
    for (x, y, z), b in list(w.bloecke.items()):
        if b in fels and w.frei(x, y - 1, z) and w.rng.random() < 0.015:
            w.setze(x, y, z, w.b("amethyst_block"))
            w.setze(x, y - 1, z, kristall)
    # kleine schwebende Begleitbrocken
    for _ in range(2 + int(R / 5)):
        a = w.rng.random() * 2 * math.pi
        d = R * (1.25 + 0.6 * w.rng.random())
        rr = max(1.5, R * (0.08 + 0.1 * w.rng.random()))
        insel(w, sch, rs, cx + math.cos(a) * d, int(top - T * (0.1 + 0.5 * w.rng.random())),
              cz + math.sin(a) * d, rr, rr * 1.2, extras=False)


def unterseite(w: Welt, sch: Schema, anteil=0.08):
    """Hängende Wurzeln, Höhlenranken und Moos unter den Inseln."""
    fels = set(sch.fels.ids) | {sch.erde}
    wurzel = w.b("hanging_roots", waterlogged=False)
    rank, spitze = w.b("cave_vines_plant", berries=False), w.b("cave_vines", age=25, berries=True)
    for (x, y, z), b in list(w.bloecke.items()):
        if b not in fels or not w.frei(x, y - 1, z):
            continue
        u = w.rng.random()
        if u < anteil:
            w.setze(x, y - 1, z, wurzel)
        elif u < anteil * 1.6:
            n = 2 + int(w.rng.random() * 6)
            for k in range(1, n):
                if not w.frei(x, y - k, z):
                    break
                w.setze(x, y - k, z, rank if k < n - 1 else spitze)


def boden(oben, x, z, default):
    return oben.get((x, z), default)


def flaeche(oben, x0, z0, B, T, default):
    return max(boden(oben, x, z, default) for x in range(x0, x0 + B) for z in range(z0, z0 + T))


def weg(w: Welt, sch: Schema, oben, punkte, breite=1):
    """Gepflasterter Weg zwischen Punkten (auf der Grasoberfläche)."""
    for (ax, az), (bx, bz) in zip(punkte, punkte[1:]):
        n = max(abs(bx - ax), abs(bz - az)) + 1
        for i in range(n):
            x = round(ax + (bx - ax) * i / max(1, n - 1))
            z = round(az + (bz - az) * i / max(1, n - 1))
            for dx in range(-breite, breite + 1):
                for dz in range(-breite, breite + 1):
                    p = (x + dx, z + dz)
                    if p in oben and w.hole(p[0], oben[p], p[1]) == sch.gras:
                        w.setze(p[0], oben[p], p[1], sch.weg(1.5 + w.rng.random() * 1.5, p[0], 0, p[1]))


def laternenpfahl(w: Welt, x, y, z):
    zaun = w.b("dark_oak_fence", north=False, south=False, east=False, west=False, waterlogged=False)
    for k in range(1, 4):
        w.setze(x, y + k, z, zaun)
    w.setze(x, y + 4, z, w.b("lantern", hanging=False, waterlogged=False))


def turm(w: Welt, sch: Schema, cx, y0, cz, R, H, spitze=True):
    """Runder Turm mit Fensterbändern, Galerie und Kupfer-Spitzdach."""
    for y in range(y0 - 3, y0 + H + 1):
        for x in range(cx - R - 1, cx + R + 2):
            for z in range(cz - R - 1, cz + R + 2):
                d = math.hypot(x - cx, z - cz)
                if d > R + 0.4:
                    continue
                if y < y0 or d > R - 0.8:
                    fenster = y > y0 + 2 and (y - y0) % 6 in (3, 4) and (x == cx or z == cz) and d > R - 0.8
                    if fenster:
                        w.setze(x, y, z, w.b("glass_pane", east=x == cx, west=x == cx, north=z == cz, south=z == cz,
                                             waterlogged=False))
                    else:
                        w.setze(x, y, z, sch.wand(0.8 + 2.4 * (y - y0) / H + (w.rng.random() - 0.5) * 0.6, x, y, z))
                else:
                    w.setze(x, y, z, 0)
    # Galerie
    yg = y0 + H
    for x in range(cx - R - 2, cx + R + 3):
        for z in range(cz - R - 2, cz + R + 3):
            d = math.hypot(x - cx, z - cz)
            if R - 0.5 < d <= R + 1.6:
                w.setze(x, yg, z, sch.kante)
    if spitze:
        for k in range(0, int(R * 2.6) + 2):
            r = (R + 1.2) * (1 - k / (R * 2.6 + 1))
            for x in range(cx - R - 2, cx + R + 3):
                for z in range(cz - R - 2, cz + R + 3):
                    d = math.hypot(x - cx, z - cz)
                    if d <= r and (d > r - 1.2 or k == 0):
                        w.setze(x, yg + 1 + k, z, sch.dach(0.5 + 3 * k / (R * 2.6), x, yg + k, z))
        top = yg + int(R * 2.6) + 3
        w.setze(cx, top, cz, sch.kante)
        w.setze(cx, top + 1, cz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    haengelaterne(w, cx + R + 1, yg - 1, cz, 1)
    haengelaterne(w, cx - R - 1, yg - 1, cz, 1)


def windmuehle(w: Welt, sch: Schema, cx, y0, cz, H=10):
    for y in range(y0, y0 + H):
        r = 3 - y // max(1, (H // 2)) * 0.5
        for x in range(cx - 3, cx + 4):
            for z in range(cz - 3, cz + 4):
                d = math.hypot(x - cx, z - cz)
                if d <= r:
                    w.setze(x, y, z, sch.wand(1.5, x, y, z) if d > r - 1 else 0)
    for k in range(4):
        r = 3 - k * 0.8
        for x in range(cx - 4, cx + 5):
            for z in range(cz - 4, cz + 5):
                if math.hypot(x - cx, z - cz) <= r:
                    w.setze(x, y0 + H + k, z, sch.dach(1 + k, x, y0 + H + k, z))
    # Flügel (vorne, Richtung +z)
    hz = cz + 4
    yh = y0 + H - 1
    w.setze(cx, yh, hz - 1, w.b("dark_oak_log", axis="z"))
    w.setze(cx, yh, hz, w.b("dark_oak_log", axis="z"))
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for k in range(1, 9):
            x, y = cx + dx * k, yh + dy * k
            w.setze(x, y, hz, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                  waterlogged=False) if k < 2 else w.b("dark_oak_log", axis="x" if dx else "y"))
            if k >= 3:
                qx, qy = (0, 1) if dx else (1, 0)
                for q in (1, 2):
                    w.setze(x + qx * q * (1 if dy >= 0 else -1), y + qy * q * (1 if dx <= 0 else -1), hz,
                            w.b("white_wool"))


def haengebruecke_teil(w: Welt, x0, y0, z, laenge, durchhang=3):
    """Hängebrücke entlang x mit Ketten und Laternen."""
    planke, stufe = w.b("dark_oak_planks"), w.b("dark_oak_slab", type="bottom", waterlogged=False)
    for i in range(laenge + 1):
        t = i / laenge
        dy = -durchhang * 4 * t * (1 - t)
        y = y0 + dy
        for dz in (-1, 0, 1):
            w.setze(x0 + i, int(math.floor(y)), z + dz, stufe if (y - math.floor(y)) > 0.5 else planke)
        for dz in (-2, 2):
            w.setze(x0 + i, int(math.floor(y)) + 1, z + dz, w.b("chain", axis="x", waterlogged=False))
        if i % 6 == 0:
            for dz in (-2, 2):
                for k in range(1, 3):
                    w.setze(x0 + i, int(math.floor(y)) + k, z + dz, w.b("dark_oak_fence", north=False, south=False,
                                                                          east=False, west=False, waterlogged=False))
                w.setze(x0 + i, int(math.floor(y)) + 3, z + dz, w.b("lantern", hanging=False, waterlogged=False))


# ============================================================================ Inseltypen


def wohninsel(seed, g=1):
    """Insel mit Häusern, Wegen, Laternen und Bäumen."""
    w = _welt(seed)
    sch = Schema(w)
    rs = Rauschen(w, 4)
    R = [8, 13, 20, 30][g]
    T = [10, 15, 22, 32][g]
    top = int(T * 1.9) + [10, 14, 18, 24][g]
    oben = insel(w, sch, rs, 0, top, 0, R, T)
    n_haus = [1, 2, 4, 7][g]
    plaetze = []
    for i in range(n_haus):
        a = i * 2 * math.pi / max(1, n_haus) + w.rng.random() * 0.5
        d = 0 if n_haus == 1 else R * 0.45
        plaetze.append((int(math.cos(a) * d), int(math.sin(a) * d)))
    for i, (px, pz) in enumerate(plaetze):
        B, Tt = [7, 7, 9, 9][g] + (i % 2) * 2, [6, 6, 7, 7][g]
        x0, z0 = px - B // 2, pz - Tt // 2
        y0 = flaeche(oben, x0, z0, B, Tt, top) + 1
        tuer = "south" if pz <= 0 else "north"
        fantasiehaus(w, x0, y0, z0, B=B, T=Tt, H=[4, 5, 5, 6][g], stil="kupfer" if i % 3 != 2 else "terrakotta",
                     fundament=6, tuer=tuer, sockel_bloecke=["stone_bricks", "andesite", "cobblestone"])
    if n_haus > 1:
        weg(w, sch, oben, plaetze + [plaetze[0]])
    for _ in range([1, 3, 6, 10][g]):
        a = w.rng.random() * 2 * math.pi
        d = R * (0.75 + 0.15 * w.rng.random())
        x, z = int(math.cos(a) * d), int(math.sin(a) * d)
        if (x, z) in oben and w.frei(x, oben[(x, z)] + 1, z):
            if w.rng.random() < 0.5:
                laternenpfahl(w, x, oben[(x, z)], z)
            else:
                einfuegen(w, (kirschbaum if w.rng.random() < 0.5 else azaleenbaum)(seed + x, 0), x, oben[(x, z)], z)
    unterseite(w, sch)
    ueberwuchern(w, None, ranken=0.08, pflanzen=0.35, buesche=0.04)
    return w


def turminsel(seed, g=1):
    """Schlanke Insel mit hohem Kupferturm."""
    w = _welt(seed)
    sch = Schema(w)
    rs = Rauschen(w, 4)
    R = [6, 9, 14, 22][g]
    T = [9, 14, 20, 30][g]
    top = int(T * 1.9) + [10, 14, 18, 24][g]
    oben = insel(w, sch, rs, 0, top, 0, R, T)
    turm(w, sch, 0, top + 1, 0, [2, 3, 5, 7][g], [12, 18, 30, 46][g])
    if g >= 2:
        for a in range(4):
            x, z = int(math.cos(a * math.pi / 2 + 0.6) * R * 0.7), int(math.sin(a * math.pi / 2 + 0.6) * R * 0.7)
            turm(w, sch, x, boden(oben, x, z, top) + 1, z, 2, [10, 16][g - 2])
    unterseite(w, sch)
    ueberwuchern(w, None, ranken=0.08, pflanzen=0.3, buesche=0.03)
    return w


def garteninsel(seed, g=1):
    """Grüne Insel mit Teich, Wasserfall über den Rand, Bäumen und Blumen."""
    w = _welt(seed)
    sch = Schema(w)
    rs = Rauschen(w, 4)
    R = [8, 12, 18, 28][g]
    T = [10, 14, 20, 30][g]
    top = int(T * 1.9) + [10, 14, 18, 24][g]
    oben = insel(w, sch, rs, 0, top, 0, R, T, flach=0.3)
    wasser = w.b("water", level=0)
    w.vorschau_extra = {}
    # Teich und Bach zum Rand (+z)
    pr = R * 0.3
    for (x, z), y in oben.items():
        if math.hypot(x - R * 0.1, z + R * 0.1) < pr:
            w.setze(x, y, z, wasser)
            w.setze(x, y - 1, z, w.b("clay"))
    bach = [(int(R * 0.1), z) for z in range(int(-R * 0.1), R + 3)]
    letzter = None
    for (x, z) in bach:
        if (x, z) in oben:
            w.setze(x, oben[(x, z)], z, wasser)
            letzter = (x, oben[(x, z)], z)
    if letzter:
        x, y, z = letzter
        for yy in range(1, y):
            w.vorschau_extra[(x, yy, z + 1)] = wasser
    for _ in range([3, 6, 12, 22][g]):
        a = w.rng.random() * 2 * math.pi
        d = R * (0.35 + 0.5 * w.rng.random())
        x, z = int(math.cos(a) * d), int(math.sin(a) * d)
        if (x, z) in oben and w.hole(x, oben[(x, z)], z) == sch.gras:
            baum = [eiche, kirschbaum, birke, azaleenbaum][int(w.rng.random() * 4)]
            einfuegen(w, baum(seed + x * 7 + z, min(1, g)), x, oben[(x, z)], z)
    unterseite(w, sch, 0.12)
    ueberwuchern(w, None, ranken=0.12, pflanzen=0.7, buesche=0.1)
    return w


def marktinsel(seed, g=1):
    """Marktplatz: gepflasterter Platz, Brunnen, Marktstände mit Wollmarkisen, Laternen."""
    w = _welt(seed)
    sch = Schema(w)
    rs = Rauschen(w, 4)
    R = [9, 13, 20, 30][g]
    T = [10, 14, 20, 30][g]
    top = int(T * 1.9) + [10, 14, 18, 24][g]
    oben = insel(w, sch, rs, 0, top, 0, R, T, flach=0.85)
    for (x, z), y in oben.items():
        if math.hypot(x, z) < R * 0.7:
            w.setze(x, y, z, sch.weg(1 + 2.5 * rs(x * 3, 9, z * 3), x, y, z))
    # Brunnen
    wasser = w.b("water", level=0)
    for x in range(-3, 4):
        for z in range(-3, 4):
            d = math.hypot(x, z)
            y = boden(oben, x, z, top)
            if 2.2 < d <= 3.2:
                w.setze(x, y + 1, z, w.b("stone_bricks"))
            elif d <= 2.2:
                w.setze(x, y + 1, z, wasser)
    for y in range(top + 1, top + 5):
        w.setze(0, y, 0, w.b("stone_bricks"))
    w.setze(0, top + 5, 0, w.b("lantern", hanging=False, waterlogged=False))
    # Stände
    farben = ["red", "yellow", "light_blue", "lime", "orange", "magenta"]
    n = [2, 4, 7, 12][g]
    for i in range(n):
        a = i * 2 * math.pi / n
        cx, cz = int(math.cos(a) * R * 0.5), int(math.sin(a) * R * 0.5)
        y = boden(oben, cx, cz, top)
        f = farben[i % len(farben)]
        for dx in (-1, 1):
            for dz in (-1, 1):
                for k in range(1, 4):
                    w.setze(cx + dx, y + k, cz + dz, w.b("dark_oak_fence", north=False, south=False, east=False,
                                                       west=False, waterlogged=False))
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                w.setze(cx + dx, y + 4, cz + dz, w.b(f"{f}_wool") if (dx + dz) % 2 == 0 else w.b("white_wool"))
        for dx in (-1, 0, 1):
            w.setze(cx + dx, y + 1, cz, w.b("barrel", facing="up", open=False))
    for k in range(n):
        a = (k + 0.5) * 2 * math.pi / n
        x, z = int(math.cos(a) * R * 0.75), int(math.sin(a) * R * 0.75)
        if (x, z) in oben:
            laternenpfahl(w, x, oben[(x, z)], z)
    unterseite(w, sch)
    ueberwuchern(w, None, ranken=0.06, pflanzen=0.25, buesche=0.03)
    return w


def hafeninsel(seed, g=1):
    """Hafen für Luftschiffe: Insel mit langem Steg über den Rand, Kran und Lagerhaus."""
    w = _welt(seed)
    sch = Schema(w)
    rs = Rauschen(w, 4)
    R = [8, 12, 18, 26][g]
    T = [10, 14, 20, 28][g]
    top = int(T * 1.9) + [10, 14, 18, 24][g]
    oben = insel(w, sch, rs, 0, top, 0, R, T)
    # Steg nach +x
    L = [10, 16, 24, 34][g]
    for x in range(int(R * 0.5), int(R * 0.5) + L):
        for z in range(-2, 3):
            w.setze(x, top + 1, z, w.b("dark_oak_planks") if abs(z) < 2 else w.b("dark_oak_slab", type="top",
                                                                                   waterlogged=False))
        if x % 5 == 0:
            for z in (-2, 2):
                laternenpfahl(w, x, top + 1, z)
            kette(w, x, top, top - 6, -2)
    # Stützbalken unter dem Steg
    for x in range(int(R * 0.5), int(R * 0.5) + L, 6):
        for k in range(1, 6):
            w.setze(x - k, top + 1 - k, 0, w.b("dark_oak_log", axis="y"))
    # Kran
    kx = int(R * 0.5) + L - 3
    for y in range(top + 2, top + 12):
        w.setze(kx, y, -3, w.b("dark_oak_log", axis="y"))
    for z in range(-3, 5):
        w.setze(kx, top + 12, z, w.b("dark_oak_log", axis="z"))
    kette(w, kx, top + 11, top + 5, 4)
    w.setze(kx, top + 4, 4, w.b("barrel", facing="up", open=False))
    # Lagerhaus
    B, Tt = [7, 9, 11, 13][g], [6, 7, 8, 9][g]
    x0, z0 = -B // 2 - int(R * 0.15), -Tt // 2
    fantasiehaus(w, x0, flaeche(oben, x0, z0, B, Tt, top) + 1, z0, B=B, T=Tt, H=5, stil="holz", fundament=6,
                 sockel_bloecke=["stone_bricks", "andesite"])
    zahnrad(w, x0 + B // 2, top + 4, z0 - 1, 3) if g >= 2 else None
    unterseite(w, sch)
    ueberwuchern(w, None, ranken=0.06, pflanzen=0.3, buesche=0.03)
    return w


def muehleninsel(seed, g=1):
    w = _welt(seed)
    sch = Schema(w)
    rs = Rauschen(w, 4)
    R = [7, 11, 16, 24][g]
    T = [10, 14, 20, 28][g]
    top = int(T * 1.9) + [10, 14, 18, 24][g]
    oben = insel(w, sch, rs, 0, top, 0, R, T)
    windmuehle(w, sch, 0, top + 1, 0, H=[8, 11, 15, 20][g])
    # Felder
    for (x, z), y in oben.items():
        if math.hypot(x, z) > 4.5 and math.hypot(x, z) < R * 0.75 and x % 3 != 0 and w.rng.random() < 0.9:
            w.setze(x, y, z, w.b("farmland", moisture=7))
            w.setze(x, y + 1, z, w.b("wheat", age=7) if w.rng.random() < 0.7 else w.b("carrots", age=7))
        elif x % 3 == 0 and math.hypot(x, z) < R * 0.75 and math.hypot(x, z) > 4.5:
            w.setze(x, y, z, w.b("water", level=0))
    unterseite(w, sch)
    return w


def zitadelle(seed, g=2):
    """Große Burg-Insel: Mauerring mit Türmen, Haupthalle und Bergfried."""
    w = _welt(seed)
    sch = Schema(w)
    rs = Rauschen(w, 5)
    R = [12, 18, 28, 42][g]
    T = [14, 20, 30, 44][g]
    top = int(T * 1.9) + [12, 16, 20, 26][g]
    oben = insel(w, sch, rs, 0, top, 0, R, T, flach=0.9)
    rm = R * 0.72
    hoehe = [5, 7, 9, 12][g]
    # Mauerring
    for x in range(-int(rm) - 2, int(rm) + 3):
        for z in range(-int(rm) - 2, int(rm) + 3):
            d = math.hypot(x, z)
            if rm - 1.2 < d <= rm:
                y0 = boden(oben, x, z, top)
                for y in range(y0 + 1, y0 + hoehe + 1):
                    w.setze(x, y, z, sch.wand(0.8 + 2.5 * (y - y0) / hoehe, x, y, z))
                if (x + z) % 2 == 0:
                    w.setze(x, y0 + hoehe + 1, z, sch.wand(2.5, x, y, z))
    n = [4, 5, 6, 8][g]
    for i in range(n):
        a = i * 2 * math.pi / n
        x, z = int(math.cos(a) * rm), int(math.sin(a) * rm)
        turm(w, sch, x, boden(oben, x, z, top) + 1, z, [2, 3, 3, 4][g], hoehe + [5, 7, 9, 12][g])
    # Haupthaus und Bergfried
    B, Tt = [9, 11, 15, 19][g], [7, 9, 11, 13][g]
    fantasiehaus(w, -B // 2, top + 1, 2, B=B, T=Tt, H=[5, 6, 8, 9][g], stil="kupfer", fundament=4,
                 sockel_bloecke=["stone_bricks", "andesite"])
    turm(w, sch, 0, top + 1, -int(rm * 0.4), [3, 4, 6, 8][g], [16, 22, 34, 50][g])
    weg(w, sch, oben, [(0, int(rm)), (0, 2 + Tt), (0, -int(rm * 0.4))], 1)
    unterseite(w, sch, 0.06)
    ueberwuchern(w, None, ranken=0.06, pflanzen=0.2, buesche=0.02)
    return w


def felsbrocken_schwebend(seed, g=1):
    """Kleine schwebende Felsbrocken mit Gras und Ranken – als Füllstücke zwischen Inseln."""
    w = _welt(seed)
    sch = Schema(w)
    rs = Rauschen(w, 3)
    n = [3, 5, 8, 12][g]
    for i in range(n):
        a = w.rng.random() * 2 * math.pi
        d = 0 if i == 0 else [6, 10, 16, 24][g] * w.rng.random()
        R = [2.5, 3.5, 5, 7][g] * (0.5 + 0.6 * w.rng.random())
        insel(w, sch, rs, math.cos(a) * d, int([10, 14, 18, 24][g] + w.rng.random() * [6, 10, 14, 20][g]),
              math.sin(a) * d, R, R * 1.6)
    unterseite(w, sch, 0.15)
    ueberwuchern(w, None, ranken=0.15, pflanzen=0.4, buesche=0.05)
    return w


def haengebruecke(seed, g=1):
    """Hängebrücke zum Verbinden zweier Inseln (Länge je Größe)."""
    w = _welt(seed)
    L = [12, 20, 32, 48][g]
    haengebruecke_teil(w, 0, 20, 0, L, durchhang=[2, 3, 5, 7][g])
    w.anker = (0, 0, 0)
    return w


HIMMELSSTADT = {
    "wohninsel": ("Wohninsel", wohninsel),
    "turminsel": ("Turminsel", turminsel),
    "garteninsel": ("Garteninsel mit Wasserfall", garteninsel),
    "marktinsel": ("Marktplatz-Insel", marktinsel),
    "hafeninsel": ("Luftschiff-Hafen", hafeninsel),
    "muehleninsel": ("Windmühlen-Insel", muehleninsel),
    "zitadelle": ("Zitadelle", zitadelle),
    "felsbrocken_schwebend": ("Schwebende Felsbrocken", felsbrocken_schwebend),
    "haengebruecke": ("Hängebrücke", haengebruecke),
}


# ============================================================================ Schwebeberge (Pandora-Stil)

def _berg(w: Welt, rs, cx, cz, y_unten, H, Rt, fels, moos, gras, lianen):
    """Ein senkrechter, schwebender Felsberg mit Rippen, Simsen und Dschungel-Gipfel. Gibt Gipfel-Höhen zurück."""
    oben = {}
    rippen = 5 + int(w.rng.random() * 4)
    phase = w.rng.random() * 6.3
    for y in range(int(y_unten), int(y_unten + H) + 1):
        t = min(1.0, max(0.0, (y - y_unten) / H))
        r = Rt * (0.12 + 0.88 * t ** 0.55)
        if t > 0.92:
            r *= max(0.3, 1 - (t - 0.92) * 2.2)
        sims = 1.0 + 0.12 * (1 if int((y + phase * 7) / 5) % 2 == 0 else 0)
        for x in range(int(cx - Rt * 1.4) - 2, int(cx + Rt * 1.4) + 3):
            for z in range(int(cz - Rt * 1.4) - 2, int(cz + Rt * 1.4) + 3):
                dx, dz = x - cx, z - cz
                d = math.hypot(dx, dz)
                ang = math.atan2(dz, dx)
                rippe = 0.5 + 0.5 * math.sin(ang * rippen + phase + y * 0.04)
                re = r * sims * (0.82 + 0.22 * rippe + 0.18 * (rs(x * 0.6, y * 0.25, z * 0.6) - 0.5))
                if d > re:
                    continue
                streifen = rs(x * 0.9, y * 0.08, z * 0.9)
                if streifen > 0.68 and d > re - 1.5:
                    blk = moos
                else:
                    blk = fels(0.3 + 3.6 * t + (streifen - 0.5) * 1.2, x, y, z)
                w.setze(x, y, z, blk)
                p = (x, z)
                if p not in oben or y > oben[p]:
                    oben[p] = y
    # Gipfel und Simse begrünen
    for (x, z), y in oben.items():
        w.setze(x, y, z, gras)
    for (x, y, z), b in list(w.bloecke.items()):
        if b != gras and b in (moos,) + tuple(fels.ids) and w.frei(x, y + 1, z) and y < y_unten + H * 0.9 \
                and w.rng.random() < 0.55:
            w.setze(x, y, z, gras if w.rng.random() < 0.6 else moos)
    return oben


def _dschungel(w: Welt, oben, seed, dichte, gross):
    from baeume import dschungelriese
    blatt = [laub(w, "jungle"), laub(w, "oak"), laub(w, "azalea")]
    gras = w.b("grass_block", snowy=False)
    pos = sorted(oben.items(), key=lambda kv: w.rng.random())
    baeume = 0
    for (x, z), y in pos:
        if w.hole(x, y, z) != gras or not w.frei(x, y + 1, z):
            continue
        u = w.rng.random()
        if u < dichte * 0.06 and baeume < 2 + gross * 3:
            einfuegen(w, dschungelriese(seed + x * 13 + z, 0 if gross < 2 else 1), x, y, z)
            baeume += 1
        elif u < dichte * 0.3:
            r = 1.2 + w.rng.random() * 1.6
            for dx in range(-2, 3):
                for dy in range(0, 3):
                    for dz in range(-2, 3):
                        if dx * dx + (dy * 1.4) ** 2 + dz * dz <= r * r:
                            w.setze(x + dx, y + 1 + dy, z + dz, blatt[int(w.rng.random() * 3)], ueberschreiben=False)
        elif u < dichte * 0.6:
            w.setze(x, y + 1, z, w.b("fern") if w.rng.random() < 0.5 else w.b("grass"))


def _lianen(w: Welt, traeger, anteil, max_laenge, min_y):
    seiten = [(1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")]
    for (x, y, z), b in list(w.bloecke.items()):
        if b not in traeger:
            continue
        for dx, dz, s in seiten:
            ax, az = x + dx, z + dz
            if not w.frei(ax, y, az) or not w.frei(ax, y + 1, az) and w.hole(ax, y + 1, az) in traeger:
                continue
            if w.rng.random() > anteil:
                continue
            ranke = w.b("vine", **{k: (k == s) for k in ("north", "east", "south", "west")}, up=False)
            for k in range(int(3 + w.rng.random() * max_laenge)):
                if y - k < min_y or not w.frei(ax, y - k, az):
                    break
                w.setze(ax, y - k, az, ranke)


def _wasserfall(w: Welt, oben, cx, cz, y_unten):
    """Quelle am Gipfelrand; im Spiel fällt das Wasser bis zum Boden (Vorschau zeichnet die Säule)."""
    if not oben:
        return
    a = w.rng.random() * 2 * math.pi
    rand = max(oben, key=lambda p: (p[0] - cx) * math.cos(a) + (p[1] - cz) * math.sin(a))
    x, z = rand
    y = oben[rand]
    w.setze(x, y, z, w.b("water", level=0))
    w.vorschau_extra = getattr(w, "vorschau_extra", {})
    nx, nz = x + round(math.cos(a)), z + round(math.sin(a))
    for yy in range(1, y):
        w.vorschau_extra[(nx, yy, nz)] = w.b("water", level=0)


def schwebeberg(seed, g=1, anzahl=1, bogen=False):
    """Schwebende Felsberge im Pandora-Stil: senkrecht, gerippt, oben Dschungel, lange Lianen."""
    w = _welt(seed)
    rs = Rauschen(w, 5)
    fels = Verlauf(w, "Felsberg", ["deepslate", "tuff", "andesite", "stone", "calcite"])
    moos, gras = w.b("moss_block"), w.b("grass_block", snowy=False)
    H = [24, 40, 64, 100][g]
    Rt = [6, 9, 14, 21][g]
    luecke = [8, 12, 18, 26][g]
    gipfel = []
    for i in range(anzahl):
        if i == 0:
            cx, cz, h, r = 0, 0, H, Rt
        else:
            a = i * 2 * math.pi / max(1, anzahl - 1) + w.rng.random() * 0.6
            d = Rt * (2.2 + w.rng.random() * 0.8)
            cx, cz = math.cos(a) * d, math.sin(a) * d
            h, r = H * (0.45 + 0.4 * w.rng.random()), Rt * (0.45 + 0.35 * w.rng.random())
        y_u = luecke + (H - h) * (0.3 + 0.7 * w.rng.random())
        oben = _berg(w, rs, cx, cz, y_u, h, r, fels, moos, gras, None)
        gipfel.append((cx, cz, y_u, h, r, oben))
        _dschungel(w, oben, seed + i, 1.0, g)
        if i == 0:
            _wasserfall(w, oben, cx, cz, y_u)
    if bogen and len(gipfel) >= 2:
        # natürlicher Felsbogen zwischen den ersten beiden Bergen
        (ax, az, ay, ah, ar, _), (bx, bz, by, bh, br, _) = gipfel[0], gipfel[1]
        y1, y2 = ay + ah * 0.6, by + bh * 0.6
        n = int(math.hypot(bx - ax, bz - az) * 2)
        for i in range(n + 1):
            t = i / n
            x, z = ax + (bx - ax) * t, az + (bz - az) * t
            y = y1 + (y2 - y1) * t + 6 * math.sin(math.pi * t)
            dick = 2.2 + 1.2 * abs(0.5 - t)
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    for dz in range(-3, 4):
                        if dx * dx + dy * dy + dz * dz <= dick * dick:
                            w.setze(int(x + dx), int(y + dy), int(z + dz), fels(2.5, int(x), int(y), int(z)))
    # kleine Begleitbrocken
    for k in range([2, 3, 5, 8][g]):
        a = w.rng.random() * 2 * math.pi
        d = Rt * (1.6 + w.rng.random() * 1.5)
        rr = Rt * (0.15 + 0.15 * w.rng.random())
        _berg(w, rs, math.cos(a) * d, math.sin(a) * d, luecke + H * (0.2 + 0.6 * w.rng.random()), rr * 2.5, rr,
              fels, moos, gras, None)
    traeger = set(fels.ids) | {moos, gras}
    _lianen(w, traeger, 0.05, [10, 18, 28, 40][g], min_y=2)
    return w


SCHWEBEBERGE = {
    "schwebeberg": ("Schwebeberg", lambda s, g: schwebeberg(s, g, 1)),
    "schwebeberg_paar": ("Schwebeberge mit Felsbogen", lambda s, g: schwebeberg(s, g, 2, bogen=True)),
    "schwebeberg_gruppe": ("Schwebeberg-Gruppe", lambda s, g: schwebeberg(s, g, 4)),
}

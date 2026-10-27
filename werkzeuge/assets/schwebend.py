"""Schwebende Strukturen: Felssichel mit Ranken, zerbrochene Felsbrocken, Regenbogen-Ring,
Insel-Archipel und Himmelsturm mit Ring.

Der Anker (0, 0, 0) liegt auf dem Boden unter der Struktur – sie schwebt darüber.
Alle Funktionen nehmen (seed, groesse) mit groesse 0 = mittel, 1 = riesig.
"""

from __future__ import annotations

import math

import numpy as np

from baeume import birke, eiche, kirschbaum
from lib import Rauschen, Welt, einfuegen, ueberwuchern


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _haengend(w: Welt, traeger, anteil, max_laenge, beeren=0.0, min_y=1):
    """Leuchtbeeren-/Höhlenranken unter der Unterseite von festen Blöcken."""
    koerper = w.b("cave_vines_plant", berries=False)
    koerper_b = w.b("cave_vines_plant", berries=True)
    spitze = w.b("cave_vines", age=25, berries=False)
    for (x, y, z), b in list(w.bloecke.items()):
        if b not in traeger or not w.frei(x, y - 1, z) or w.rng.random() > anteil:
            continue
        laenge = int(2 + w.rng.random() * max_laenge)
        pos = []
        for k in range(1, laenge + 1):
            if y - k < min_y or not w.frei(x, y - k, z):
                break
            pos.append(y - k)
        if len(pos) < 2:
            continue
        for yy in pos[:-1]:
            w.setze(x, yy, z, koerper_b if w.rng.random() < beeren else koerper)
        w.setze(x, pos[-1], z, spitze)


def _seitenranken(w: Welt, traeger, anteil, max_laenge, min_y=1):
    seiten = [(1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")]
    for (x, y, z), b in list(w.bloecke.items()):
        if b not in traeger:
            continue
        for dx, dz, s in seiten:
            ax, az = x + dx, z + dz
            if not w.frei(ax, y, az) or w.rng.random() > anteil:
                continue
            ranke = w.b("vine", **{k: (k == s) for k in ("north", "east", "south", "west")}, up=False)
            for k in range(int(1 + w.rng.random() * max_laenge)):
                if y - k < min_y or not w.frei(ax, y - k, az):
                    break
                w.setze(ax, y - k, az, ranke)


# --------------------------------------------------------------------------- Felssichel

def felssichel(seed, groesse=1):
    """Schwebende, gebogene Felssichel mit begrünter Oberseite und langen herabhängenden Ranken."""
    w = _welt(seed)
    rs = Rauschen(w, 6)
    stein = [w.b("calcite"), w.b("diorite"), w.b("calcite"), w.b("smooth_stone"), w.b("andesite")]
    gras, moos = w.b("grass_block", snowy=False), w.b("moss_block")
    Rk = [22, 36][groesse]
    spanne = math.radians(115)
    hoehe = [16, 26][groesse]
    Wmax = [6, 9][groesse]
    Dmax = [4, 6][groesse]
    anstieg = [5, 9][groesse]
    a0 = -spanne / 2 + w.rng.random() * 0.3
    t_schritte = int(Rk * spanne / 0.4)
    for i in range(t_schritte + 1):
        t = i / t_schritte
        ang = a0 + spanne * t
        cx, cz = math.cos(ang) * Rk - Rk, math.sin(ang) * Rk
        ny = hoehe + anstieg * math.sin(math.pi * t) + 3 * (t - 0.5)
        nx, nz = math.cos(ang), math.sin(ang)  # radiale Richtung = quer zur Sichel
        form = math.sin(math.pi * t)
        W = Wmax * form ** 0.5 + 1
        D = Dmax * form ** 0.6 + 1.2
        for u in np.arange(-W / 2, W / 2 + 0.01, 0.4):
            x, z = math.floor(cx + nx * u), math.floor(cz + nz * u)
            k = min(1.0, (2 * u / W) ** 2)
            top = int(ny + 0.6 * (1 - k))
            unten = int(ny - D * (1 - k) ** 0.7 - rs(x, 0, z) * 1.5)
            for y in range(unten, top + 1):
                if y == top:
                    blk = gras if rs(x, 40, z) > 0.3 else moos
                else:
                    blk = stein[int(rs(x * 3, y * 3, z * 3) * 4.99)]
                w.setze(x, y, z, blk)
    traeger = set(stein) | {gras, moos}
    _haengend(w, traeger, 0.18, [8, 12][groesse], min_y=hoehe // 2)
    _seitenranken(w, traeger, 0.1, [5, 8][groesse], min_y=hoehe // 2)
    ueberwuchern(w, None, ranken=0.0, pflanzen=0.5, buesche=0.08)
    return w


# --------------------------------------------------------------------------- Zerbrochene Felsbrocken

def felsbrocken(seed, groesse=1):
    """Zerbrochene, geschichtete Felsbrocken, die übereinander schweben – mit blau leuchtendem Kern."""
    w = _welt(seed)
    rs = Rauschen(w, 3)
    weiss = [w.b("calcite"), w.b("diorite"), w.b("white_concrete"), w.b("calcite"), w.b("smooth_quartz")]
    blau = [w.b("light_blue_stained_glass"), w.b("blue_ice"), w.b("light_blue_concrete")]
    hoehe0 = [16, 24][groesse]

    def brocken(cx, cy, cz, rx, ry, rz, schnitte):
        """Ein länglicher Brocken, in Scheiben zerbrochen (Lücken zwischen den Teilen)."""
        grenzen = sorted(w.rng.uniform(-ry * 0.6, ry * 0.6, schnitte))
        for x in range(int(cx - rx) - 2, int(cx + rx) + 3):
            for y in range(int(cy - ry) - 2, int(cy + ry) + 3):
                for z in range(int(cz - rz) - 2, int(cz + rz) + 3):
                    dy = y - cy
                    # waagerechte Schichtkanten
                    lage = 1 + 0.22 * math.sin(y * 1.9 + rs(x, 0, z) * 6)
                    d = math.sqrt(((x - cx) / (rx * lage)) ** 2 + (dy / ry) ** 2 + ((z - cz) / (rz * lage)) ** 2)
                    if d > 0.85 + 0.35 * rs(x, y, z):
                        continue
                    teil = sum(1 for g in grenzen if dy > g)
                    if any(abs(dy - g) < 0.9 for g in grenzen):
                        continue  # Bruchfuge
                    versatz_x = int(teil * 0.7 * (1 if teil % 2 else -1))
                    blk = weiss[int(rs(x * 2, y * 2, z * 2) * 4.99)]
                    if d < 0.55 and rs(x * 1.7, y * 1.7, z * 1.7) > 0.62:
                        blk = blau[int(w.rng.random() * 3)]
                    w.setze(x + versatz_x, y + teil * 2, z, blk)

    rx, ry = [4, 7][groesse], [8, 13][groesse]
    brocken(0, hoehe0 + ry, 0, rx, ry, rx * 0.9, [2, 3][groesse])
    for k in range([2, 3][groesse]):
        a = w.rng.random() * 2 * math.pi
        d = [10, 16][groesse] + w.rng.random() * 4
        r = rx * (0.4 + 0.3 * w.rng.random())
        brocken(math.cos(a) * d, hoehe0 + ry * (0.6 + w.rng.random()), math.sin(a) * d, r, r * 1.6, r, 1)
    # einzelne schwebende Kristallsplitter
    for k in range([3, 5][groesse]):
        a = w.rng.random() * 2 * math.pi
        d = [6, 10][groesse] + w.rng.random() * 6
        x, z = int(math.cos(a) * d), int(math.sin(a) * d)
        y0 = int(hoehe0 + w.rng.random() * ry)
        for y in range(y0, y0 + 2 + int(w.rng.random() * 4)):
            w.setze(x, y, z, blau[0])
    return w


# --------------------------------------------------------------------------- Regenbogen-Ring

REGENBOGEN = ["red", "orange", "yellow", "lime", "green", "cyan", "light_blue", "blue", "purple", "magenta", "pink"]


def ring_zeichnen(w: Welt, cx, cy, cz, R, r, neigung_grad, drehung_grad=0.0, weiss_anteil=0.12):
    rs = Rauschen(w, 3)
    n = math.radians(neigung_grad)
    dr = math.radians(drehung_grad)
    farben = [(w.b(f"{f}_concrete"), w.b(f"{f}_wool")) for f in REGENBOGEN]
    wolke = [w.b("white_wool"), w.b("white_concrete")]
    schritte = int(2 * math.pi * R / 0.35)
    for i in range(schritte):
        phi = 2 * math.pi * i / schritte
        # Mittellinie des Rings, um x geneigt und um y gedreht
        px, py, pz = math.cos(phi) * R, 0.0, math.sin(phi) * R
        py, pz = pz * math.sin(n), pz * math.cos(n)
        px, pz = px * math.cos(dr) - pz * math.sin(dr), px * math.sin(dr) + pz * math.cos(dr)
        anteil = phi / (2 * math.pi) * len(farben)
        dick = r * (0.75 + 0.5 * rs(math.cos(phi) * 9, 0, math.sin(phi) * 9))
        for dx in range(-int(dick) - 1, int(dick) + 2):
            for dy in range(-int(dick) - 1, int(dick) + 2):
                for dz in range(-int(dick) - 1, int(dick) + 2):
                    if dx * dx + dy * dy + dz * dz > dick * dick:
                        continue
                    x, y, z = math.floor(cx + px + dx), math.floor(cy + py + dy), math.floor(cz + pz + dz)
                    if (x, y, z) in w.bloecke:
                        continue
                    if w.rng.random() < weiss_anteil * (1.5 if 6 <= anteil < 7.5 else 0.3):
                        blk = wolke[int(w.rng.random() * 2)]
                    else:
                        k = int(anteil + (w.rng.random() - 0.5) * 1.2) % len(farben)
                        blk = farben[k][0 if w.rng.random() < 0.7 else 1]
                    w.setze(x, y, z, blk)


def regenbogenring(seed, groesse=1):
    """Schwebender, geneigter Regenbogen-Ring."""
    w = _welt(seed)
    R = [14, 26][groesse]
    r = [1.8, 2.8][groesse]
    neigung = 22 + w.rng.random() * 10
    hoehe = R * math.sin(math.radians(neigung)) + [10, 16][groesse]
    ring_zeichnen(w, 0, hoehe, 0, R, r, neigung, w.rng.random() * 360)
    return w


# --------------------------------------------------------------------------- Insel-Archipel

def _insel(w: Welt, rs, cx, sockel, cz, R, T, baum=None, wasserfall=False):
    stein = [w.b("stone"), w.b("andesite"), w.b("tuff"), w.b("cobblestone"), w.b("calcite")]
    erde, gras = w.b("dirt"), w.b("grass_block", snowy=False)
    oben = {}
    for x in range(int(cx - R) - 3, int(cx + R) + 4):
        for z in range(int(cz - R) - 3, int(cz + R) + 4):
            d = math.hypot(x - cx, z - cz) / R
            d *= 0.85 + 0.35 * rs(x, 0, z)
            if d > 1:
                continue
            tiefe = int(T * (1 - d) ** 0.85 * (0.7 + 0.6 * rs(x, 30, z))) + 2
            y_top = sockel + int(2 * (1 - d) * rs(x, 60, z))
            oben[(x, z)] = y_top
            for y in range(y_top - tiefe, y_top + 1):
                b = gras if y == y_top else erde if y > y_top - 3 else stein[int(rs(x, y * 2, z) * 4.99)]
                w.setze(x, y, z, b)
    if wasserfall:
        wasser = w.b("water", level=0)
        rand = max(oben, key=lambda p: p[1] - cz)
        x, z = rand
        for k in range(4):
            if (x, z - k) in oben:
                w.setze(x, oben[(x, z - k)], z - k, wasser)
        w.vorschau_extra = getattr(w, "vorschau_extra", {})
        for y in range(1, oben[rand]):
            w.vorschau_extra[(x, y, z + 1)] = wasser
    if baum is not None:
        mx, mz = int(cx), int(cz)
        einfuegen(w, baum, mx, oben.get((mx, mz), sockel), mz)
    return oben


def archipel(seed, groesse=1):
    """Drei schwebende Inseln auf verschiedenen Höhen, mit Bäumen, Wasserfall und Wurzeln."""
    w = _welt(seed)
    rs = Rauschen(w, 4)
    s = [1.0, 1.6][groesse]
    _insel(w, rs, 0, int(22 * s), 0, 9 * s, 11 * s, eiche(seed, 1 if groesse else 0), wasserfall=True)
    _insel(w, rs, 17 * s, int(14 * s), -6 * s, 5 * s, 6 * s, kirschbaum(seed + 1, 0))
    _insel(w, rs, -12 * s, int(30 * s), 11 * s, 4 * s, 5 * s, birke(seed + 2, 0))
    stein = {w.b(n) for n in ("stone", "andesite", "tuff", "cobblestone", "calcite", "dirt")}
    wurzel = w.b("hanging_roots", waterlogged=False)
    for (x, y, z), b in list(w.bloecke.items()):
        if b in stein and w.frei(x, y - 1, z) and w.rng.random() < 0.08:
            w.setze(x, y - 1, z, wurzel)
    _haengend(w, stein, 0.06, 8)
    ueberwuchern(w, None, ranken=0.15, pflanzen=0.4, buesche=0.05)
    return w


# --------------------------------------------------------------------------- Himmelsturm

def himmelsturm(seed, groesse=1):
    """Weißer Turm mit Rippen und Spitze, Vorplatz mit Treppe, umkreist von einem Regenbogen-Ring."""
    w = _welt(seed)
    H = [48, 80][groesse]
    R0 = [6, 9][groesse]
    weiss = [w.b("smooth_quartz"), w.b("calcite"), w.b("white_concrete")]
    grau = [w.b("light_gray_concrete"), w.b("polished_andesite")]
    dunkel = w.b("gray_concrete")
    glas = w.b("light_blue_stained_glass")
    # Vorplatz
    P = R0 + [6, 9][groesse]
    for x in range(-P, P + 1):
        for z in range(-P, P + 1):
            d = math.hypot(x, z)
            if d <= P:
                w.setze(x, 0, z, w.b("smooth_quartz") if (x + z) % 4 else w.b("polished_diorite"))
                if d > P - 1:
                    w.setze(x, 1, z, w.b("quartz_slab", type="bottom", waterlogged=False))
    # Weg mit gelber Mittellinie nach Süden
    for z in range(P, P + [10, 16][groesse]):
        for x in range(-3, 4):
            w.setze(x, 0, z, w.b("yellow_concrete") if x == 0 else w.b("white_concrete") if abs(x) < 3 else w.b("smooth_stone"))
    # Turmkörper
    for y in range(1, H + 1):
        t = y / H
        r = R0 * (1 - t) ** 1.25 + 0.6
        stufe = int(y / 8)
        r += 0.8 * (1 - (y % 8) / 8) * (1 - t)  # leichte Absätze
        for x in range(-int(r) - 2, int(r) + 3):
            for z in range(-int(r) - 2, int(r) + 3):
                ang = math.atan2(z, x)
                rippe = 0.5 + 0.5 * math.cos(8 * ang)
                re = r * (1 + 0.18 * rippe)
                d = math.hypot(x, z)
                if d > re:
                    continue
                if d > re - 1.2:
                    if rippe > 0.85:
                        blk = grau[stufe % 2]
                    elif y % 8 in (3, 4) and rippe < 0.3 and t < 0.75:
                        blk = glas
                    else:
                        blk = weiss[int(w.rng.random() * 3) if w.rng.random() < 0.3 else 0]
                else:
                    blk = weiss[1]
                w.setze(x, y, z, blk)
    for y in range(H + 1, H + [8, 12][groesse]):
        w.setze(0, y, 0, weiss[0] if y < H + 5 else w.b("end_rod", facing="up"))
    # Portal nach Süden
    pz = int(R0 * 1.15) + 1
    for y in range(1, [8, 11][groesse]):
        for x in range(-2, 3):
            for z in range(pz - 3, pz + 1):
                if abs(x) == 2 or y >= [7, 10][groesse] - 1:
                    w.setze(x, y, z, dunkel)
                else:
                    w.setze(x, y, z, 0 if z > pz - 3 else w.b("black_stained_glass"))
    for x in range(-3, 4):
        w.setze(x, 1, pz + 1, w.b("quartz_stairs", facing="north", half="bottom", shape="straight", waterlogged=False))
    # Seitenflügel mit Fenstern
    for seite in (-1, 1):
        for x in range(R0 + 1, R0 + 7):
            for z in range(-3, 4):
                for y in range(1, 6):
                    rand = abs(z) == 3 or x in (R0 + 1, R0 + 6) or y == 5
                    if not rand:
                        w.setze(seite * x, y, z, 0)
                        continue
                    fenster = z == 3 and y in (2, 3) and x % 2 == 0
                    w.setze(seite * x, y, z, w.b("purple_stained_glass") if fenster else weiss[0])
        for x in range(R0 + 1, R0 + 7):
            w.setze(seite * x, 6, 3, w.b("quartz_slab", type="bottom", waterlogged=False))
    # Bäume an den Seiten (schlanke Zypressen)
    for seite in (-1, 1):
        for k in range(3):
            x, z = seite * (P - 2), P - 4 - k * 5
            for y in range(1, 8 + groesse * 3):
                w.setze(x, y, z, w.b("spruce_log", axis="y"))
            for y in range(3, 10 + groesse * 3):
                rr = 1.6 if y < 8 + groesse * 2 else 0.8
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        if dx * dx + dz * dz <= rr * rr:
                            w.setze(x + dx, y, z + dz, w.b("oak_leaves", persistent=True, distance=7,
                                                          waterlogged=False), ueberschreiben=False)
    # Regenbogen-Ring um die Spitze
    ring_zeichnen(w, 0, H * 0.62, 0, [16, 28][groesse], [1.8, 2.6][groesse], 24, 30)
    return w


SCHWEBEND = {
    "felssichel": ("Schwebende Felssichel", felssichel),
    "felsbrocken": ("Zerbrochene Schwebebrocken", felsbrocken),
    "regenbogenring": ("Regenbogen-Ring", regenbogenring),
    "archipel": ("Schwebendes Archipel", archipel),
    "himmelsturm": ("Himmelsturm mit Ring", himmelsturm),
}

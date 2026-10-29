"""Spektakuläre Bäume II – zwanzig fantastische Riesenbäume: Kristallbaum, Feuerbaum, Eisbaum, Sternenbaum,
Lichterbaum, Spiralbaum, Torbaum, Inselbaum, Quellbaum, Kokonbaum, Moosriese, Wolkenbaum, Herbstriese,
Leuchtrankenweide, Seelenbaum, Goldener Baum, Treppenbaum, Wolkenkiefer, Zwillingsbaum und Bernsteinbaum.

Stammfuß auf (0, 0, 0); g 0 = mittel, 1 = riesig.
"""

from __future__ import annotations

import math

import numpy as np

from baeume import (Pinsel, Wuchs, abzweig, ast, blattwolke, bodenstreu, kugel_f, neue_welt, richtung_aus_winkeln,
                    stamm, verzweigen, wurzeln)
from baeume2 import HolzX, chipped, gelb_laub, jacaranda_laub, orange_laub, rot_laub
from lib import laub

S = [1.0, 1.7]


def _s(g):
    return S[max(0, min(1, g))]


def _krone(w, holz, H, r, st_anteil, bl, cfg, tiefe, wolke, aeste=5, neigung=(25, 50), flach=0.7, luecken=0.08,
           wurzel=(6, 4), stamm_neig=4, stamm_bieg=0.05, min_y_f=0.85):
    """Stamm + verzweigte Krone mit frei wählbaren Holz- und Laubblöcken. Gibt (pinsel, stamm, enden, mitte)."""
    pinsel = Pinsel(w, holz)
    st = stamm(w, pinsel, H * st_anteil, r, r * 0.7, neigung=stamm_neig, biegung=stamm_bieg)
    if wurzel[0]:
        wurzeln(w, pinsel, r, wurzel[0], wurzel[1])
    enden, mitte = [], []
    gabel, gd, gr = st[-1]
    az0 = w.rng.random() * 360
    for i in range(aeste):
        d = abzweig(gd, neigung[0] + w.rng.random() * (neigung[1] - neigung[0]),
                    az0 + i * 360 / aeste + (w.rng.random() - 0.5) * 40)
        k = len(st) - 1 - int(w.rng.random() * len(st) * 0.25) if i else len(st) - 1
        verzweigen(w, pinsel, st[k][0], d, H * (1 - st_anteil) * (0.8 + 0.3 * w.rng.random()), max(0.5, gr * 0.8),
                   tiefe, cfg, enden, mitte)
    unten = int(gabel[1] * min_y_f)
    if bl:
        for p, t in enden:
            rw = wolke * (1.0 if t == 0 else 0.8) * (0.8 + 0.4 * w.rng.random())
            blattwolke(w, p + [0, 0.6, 0], rw, rw * flach, bl, schutz=holz.alle, luecken=luecken, min_y=unten)
        for p in mitte[::3]:
            blattwolke(w, p + [0, 0.5, 0], wolke * 0.6, wolke * 0.36, bl, schutz=holz.alle, luecken=luecken,
                       min_y=unten)
    return pinsel, st, enden, mitte


def _haengen(w, quelle, blk, anteil, laenge, min_y=2):
    """An der Unterseite der Quellblöcke hängende Stränge (Ranken, Lichter, Trauben)."""
    for (x, y, z), b in list(w.bloecke.items()):
        if b in quelle and w.frei(x, y - 1, z) and w.rng.random() < anteil:
            for k in range(1, 1 + int(1 + w.rng.random() * laenge)):
                if y - k < min_y or not w.frei(x, y - k, z):
                    break
                w.setze(x, y - k, z, blk(k) if callable(blk) else blk)


def _boden(w, R, bloecke, anteil=0.6):
    for x in range(-int(R), int(R) + 1):
        for z in range(-int(R), int(R) + 1):
            d = math.hypot(x, z)
            if d < R and w.rng.random() < anteil * (1 - d / R) + 0.15 and w.frei(x, 0, z):
                w.setze(x, 0, z, bloecke[int(w.rng.random() * len(bloecke))])


# ============================================================================ Bäume

def kristallbaum(seed, g=0):
    """Kristallbaum: ein Stamm aus Amethyst, verzweigt wie Glas, die Krone aus violettem und klarem Glas mit
    leuchtenden Kristallknospen, am Fuß wachsen Amethyst-Druse und Kalzit."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "amethyst_block", "amethyst_block")
    bl = [(w.b("purple_stained_glass"), 0.45), (w.b("magenta_stained_glass"), 0.2), (w.b("glass"), 0.15),
          (w.b("amethyst_block"), 0.1), (w.b("pink_stained_glass"), 0.1)]
    cfg = Wuchs(kinder=2, spreizung=(25, 45), laenge=0.66, biegung=0.06, auftrieb=0.05)
    _, st, enden, _ = _krone(w, holz, 16 * s, 1.0 * s, 0.4, bl, cfg, 2, 2.6 * s, aeste=4, flach=0.75,
                             luecken=0.2, wurzel=(5, int(3 * s)))
    for p, t in enden:
        w.setze(int(p[0]), int(p[1]) + 1, int(p[2]), w.b("amethyst_cluster", facing="up", waterlogged=False), False)
    _boden(w, 4 + 3 * s, [w.b("calcite"), w.b("budding_amethyst"), w.b("smooth_basalt"), w.b("amethyst_block")])
    bodenstreu(w, [w.b("amethyst_cluster", facing="up", waterlogged=False),
                   w.b("medium_amethyst_bud", facing="up", waterlogged=False)], int(8 * s), 2, 3 + 3 * s)
    return w


def feuerbaum(seed, g=0):
    """Feuerbaum: verkohlter Schwarzstein-Stamm mit glühenden Magmarissen, die Krone aus karminrotem Warzenlaub,
    Glühpilzlichtern und Feuerkorallen-Tönen, Asche und Basalt ringsum."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "crimson_stem", "crimson_hyphae")
    bl = [(w.b("nether_wart_block"), 0.5), (w.b("shroomlight"), 0.12), (rot_laub(w), 0.2), (orange_laub(w), 0.18)]
    cfg = Wuchs(kinder=2, spreizung=(25, 50), laenge=0.64, biegung=0.14, auftrieb=0.03)
    _krone(w, holz, 15 * s, 1.1 * s, 0.42, bl, cfg, 2, 2.8 * s, aeste=5, flach=0.7, wurzel=(6, int(4 * s)))
    for p, b in list(w.bloecke.items()):
        if b in holz.alle and w.rng.random() < 0.12:
            w.bloecke[p] = w.b("magma_block")
    _haengen(w, {bl[0][0]}, w.b("weeping_vines_plant"), 0.08, 3)
    _boden(w, 4 + 3 * s, [w.b("blackstone"), w.b("basalt", axis="y"), w.b("magma_block"), w.b("crimson_nylium")])
    bodenstreu(w, [w.b("crimson_roots"), w.b("crimson_fungus")], int(8 * s), 2, 3 + 3 * s)
    return w


def eisbaum(seed, g=0):
    """Eisbaum: ein Baum ganz aus Packeis und Blaueis, die Krone aus Eis, Pulverschnee-Kappen und Eiszapfen,
    darunter glitzernder Schnee."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "packed_ice", "blue_ice")
    bl = [(w.b("ice"), 0.35), (w.b("snow_block"), 0.3), (w.b("white_stained_glass"), 0.2),
          (w.b("light_blue_stained_glass"), 0.15)]
    cfg = Wuchs(kinder=3, spreizung=(25, 45), laenge=0.62, biegung=0.1, auftrieb=0.04)
    _krone(w, holz, 14 * s, 1.0 * s, 0.42, bl, cfg, 2, 2.6 * s, aeste=5, flach=0.65, luecken=0.12,
           wurzel=(5, int(3 * s)))
    _haengen(w, {bl[0][0], bl[2][0]}, w.b("ice"), 0.15, 2 + s)
    _boden(w, 4 + 4 * s, [w.b("snow_block"), w.b("powder_snow"), w.b("packed_ice"), w.b("snow_block")])
    return w


def sternenbaum(seed, g=0):
    """Sternenbaum: ein dunkler, schwarzvioletter Stamm, die Krone aus nachtblauem und violettem Laub, darin
    hängen leuchtende Sternfrüchte aus Endstäben und Froschlichtern."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "dark_oak_log", "dark_oak_wood")
    bl = [(jacaranda_laub(w), 0.35), (w.b("blue_stained_glass"), 0.15), (laub(w, "dark_oak"), 0.25),
          (w.b("purple_wool"), 0.1), (w.b("black_stained_glass"), 0.15)]
    cfg = Wuchs(kinder=3, spreizung=(25, 50), laenge=0.63, biegung=0.1, auftrieb=0.04)
    _krone(w, holz, 16 * s, 1.0 * s, 0.4, bl, cfg, 2, 3.0 * s, aeste=5, flach=0.7, wurzel=(6, int(4 * s)))
    _haengen(w, {bl[0][0], bl[2][0]}, lambda k: w.b("end_rod", facing="down") if k < 2 else
             w.b("pearlescent_froglight", axis="y"), 0.04, 2)
    bodenstreu(w, [w.b("end_rod", facing="up"), w.b("blue_orchid")], int(10 * s), 2, 3 + 3 * s)
    return w


def lichterbaum(seed, g=0):
    """Lichterbaum: eine weit ausladende alte Eiche, über und über behängt mit Laternen an Ketten, darunter Bänke
    und ein Teppich aus Lichtpunkten."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "oak_log", "oak_wood")
    bl = [(laub(w, "oak"), 0.75), (laub(w, "azalea"), 0.25)]
    cfg = Wuchs(kinder=3, spreizung=(30, 55), laenge=0.62, biegung=0.12, auftrieb=0.02)
    _krone(w, holz, 15 * s, 1.2 * s, 0.4, bl, cfg, 2, 2.8 * s, aeste=6, neigung=(40, 65), flach=0.65,
           wurzel=(6, int(4 * s)), min_y_f=1.0)
    _haengen(w, {bl[0][0], bl[1][0]}, lambda k: w.b("chain", axis="y", waterlogged=False) if k == 1 else
             w.b("lantern", hanging=True, waterlogged=False), 0.1, 2)
    for k in range(4):
        a = k * 1.57 + 0.4
        x, z = round(math.cos(a) * (3 + 2 * s)), round(math.sin(a) * (3 + 2 * s))
        f = ["north", "east", "south", "west"][k]
        w.setze(x, 1, z, w.b("oak_stairs", facing=f, half="bottom", shape="straight", waterlogged=False), False)
    return w


def spiralbaum(seed, g=0):
    """Spiralbaum: der Stamm windet sich wie eine Schraube in den Himmel, an jeder Windung sitzt ein runder
    Laubballen, oben eine kugelige Krone."""
    w = neue_welt(seed)
    s = _s(g)
    holz = w.b("jungle_wood", axis="y")
    bl = [(laub(w, "jungle"), 0.6), (laub(w, "oak"), 0.25), (laub(w, "flowering_azalea"), 0.15)]
    H = int(22 * s)
    r = 3 * s
    dick = 1.0 * s
    letzte = None
    for i in range(H * 4):
        t = i / (H * 4)
        y = t * H
        a = t * 6.283 * (1.4 + s * 0.3)
        rr = r * (0.25 + 0.75 * math.sin(math.pi * min(1.0, t * 1.3)) ** 0.8) * (1 - 0.3 * t)
        c = (math.cos(a) * rr + 0.5, y + 0.5, math.sin(a) * rr + 0.5)
        kugel_f(w, c, dick * (1 - 0.5 * t) + 0.6, holz)
        if i % int(H * 0.6) == 0 and i > H:
            blattwolke(w, (c[0] * 1.6, c[1] + 0.5, c[2] * 1.6), 2.2 * s, 1.4 * s, bl, luecken=0.05,
                       schutz={holz})
    blattwolke(w, (0.5, H + 1.5, 0.5), 3.2 * s, 2.6 * s, bl, schutz={holz})
    return w


def torbaum(seed, g=0):
    """Torbaum: zwei Stämme wachsen schräg aufeinander zu und verschmelzen oben zu einem Bogen, durch den ein Weg
    führt; eine gemeinsame breite Krone darüber."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "spruce_log", "spruce_wood")
    pinsel = Pinsel(w, holz)
    bl = [(laub(w, "spruce"), 0.4), (laub(w, "oak"), 0.4), (laub(w, "dark_oak"), 0.2)]
    B = 3 * s + 1
    H = 13 * s
    for sx in (-1, 1):
        start = np.array([sx * B + 0.5, 0.5, 0.5])
        ziel = np.array([0.5, H, 0.5])
        d = ziel - start
        ast(w, pinsel, start, d, np.linalg.norm(d), 1.0 * s, 0.8 * s, biegung=0.02, auftrieb=0.02)
        wurzeln(w, pinsel, 0.8 * s, 3, int(2 + 2 * s))
    for k in range(-int(B), int(B) + 1):
        pass
    cfg = Wuchs(kinder=3, spreizung=(30, 55), laenge=0.6, biegung=0.1, auftrieb=0.03)
    enden, mitte = [], []
    for i in range(5):
        d = richtung_aus_winkeln(i * 72 + w.rng.random() * 30, 45 + w.rng.random() * 20)
        verzweigen(w, pinsel, [0.5, H, 0.5], d, 7 * s, 0.7 * s, 2, cfg, enden, mitte)
    for p, t in enden:
        blattwolke(w, p + [0, 0.5, 0], 2.6 * s, 1.7 * s, bl, schutz=holz.alle, min_y=int(H * 0.7))
    for z in range(-int(8 * s), int(8 * s) + 1):
        for x in (-1, 0, 1):
            if w.frei(x, 0, z):
                w.setze(x, 0, z, w.b("dirt_path"))
    return w


def inselbaum(seed, g=0):
    """Inselbaum: ein knorriger Baum steht auf einem schwebenden Felsbrocken, seine Wurzeln hängen weit in die
    Tiefe, ein kleiner Wasserfall rinnt über den Rand."""
    w = neue_welt(seed)
    s = _s(g)
    R = 5 * s + 2
    T = 6 * s + 3
    y0 = int(T + 4)
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            d = math.hypot(x, z) / R
            if d > 1:
                continue
            tief = int(T * (1 - d) ** 0.8)
            for y in range(y0 - tief, y0 + 1):
                blk = "grass_block" if y == y0 else ("dirt" if y > y0 - 2 else
                                                     ["stone", "andesite", "tuff", "cobblestone"][(x + y + z) % 4])
                w.setze(x, y, z, w.b(blk, snowy=False) if blk == "grass_block" else w.b(blk))
    holz = HolzX(w, "oak_log", "oak_wood")
    bl = [(laub(w, "oak"), 0.7), (laub(w, "flowering_azalea"), 0.3)]
    pinsel = Pinsel(w, holz)
    st = ast(w, pinsel, [0.5, y0 + 0.5, 0.5], [0.1, 1, 0.05], 8 * s, 0.8 * s, 0.6 * s, biegung=0.1)
    cfg = Wuchs(kinder=2, spreizung=(30, 55), laenge=0.6, biegung=0.15, auftrieb=0.03)
    enden, mitte = [], []
    for i in range(4):
        d = abzweig(st[-1][1], 40 + w.rng.random() * 20, i * 90)
        verzweigen(w, pinsel, st[-1][0], d, 6 * s, 0.6 * s, 2, cfg, enden, mitte)
    for p, t in enden:
        blattwolke(w, p + [0, 0.5, 0], 2.4 * s, 1.6 * s, bl, schutz=holz.alle, min_y=y0 + 3)
    for k in range(int(6 * s)):
        a = k / (6 * s) * 6.283
        start = [math.cos(a) * R * 0.5, y0 - T * 0.5, math.sin(a) * R * 0.5]
        ast(w, pinsel, start, [math.cos(a) * 0.3, -1, math.sin(a) * 0.3], y0 - 1, 0.45, 0.4, biegung=0.15)
    xr = int(R) - 1
    w.setze(xr, y0, 0, w.b("water", level=0))
    for y in range(y0 - int(T * 0.6), y0):
        w.setze(xr + 1, y, 0, w.b("water", level=8), False)
    return w


def quellbaum(seed, g=0):
    """Quellbaum: aus dem hohlen Stamm eines uralten Baums sprudelt eine Quelle, Wasser fällt in ein moosiges
    Becken mit Seerosen; Farne und Moos wuchern ringsum."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "dark_oak_log", "dark_oak_wood")
    bl = [(laub(w, "dark_oak"), 0.5), (laub(w, "oak"), 0.3), (laub(w, "azalea"), 0.2)]
    cfg = Wuchs(kinder=3, spreizung=(25, 50), laenge=0.62, biegung=0.12, auftrieb=0.03)
    R = 1.6 * s
    _krone(w, holz, 15 * s, R, 0.42, bl, cfg, 2, 2.8 * s, aeste=5, wurzel=(7, int(4 * s)))
    Rb = R + 3 + 2 * s
    for x in range(-int(Rb) - 1, int(Rb) + 2):
        for z in range(-int(Rb) - 1, int(Rb) + 2):
            d = math.hypot(x, z)
            if R + 0.8 < d < Rb and z > 0:
                for y in (0, -1):
                    w.bloecke.pop((x, y + 1, z), None)
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("moss_block"))
                if w.rng.random() < 0.06:
                    w.setze(x, 1, z, w.b("lily_pad"))
            elif Rb <= d < Rb + 1.2 and z > -1:
                w.setze(x, 0, z, w.b("mossy_cobblestone"))
    hy = int(4 * s)
    for y in range(1, hy + 1):
        w.bloecke.pop((0, y, int(R)), None)
    w.setze(0, hy, int(R) + 1, w.b("water", level=0))
    for y in range(1, hy):
        w.setze(0, y, int(R) + 1, w.b("water", level=8), False)
    bodenstreu(w, [w.b("fern"), w.b("moss_carpet")], int(12 * s), R + 1, Rb + 3)
    return w


def kokonbaum(seed, g=0):
    """Kokonbaum: ein bleicher, kahler Baum, an dessen Ästen große weiße Seidenkokons hängen, Spinnfäden
    zwischen den Zweigen."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "birch_log", "birch_wood")
    cfg = Wuchs(kinder=2, spreizung=(30, 55), laenge=0.66, biegung=0.18, auftrieb=0.02)
    _, st, enden, mitte = _krone(w, holz, 15 * s, 0.9 * s, 0.4, None, cfg, 2, 0, aeste=5, wurzel=(4, int(3 * s)))
    for (p, t) in enden[::2]:
        x, y, z = int(p[0]), int(p[1]), int(p[2])
        L = int(2 + 2 * s)
        w.setze(x, y - 1, z, w.b("cobweb"), False)
        for k in range(L):
            rr = 1.2 * s * math.sin((k + 0.5) / L * math.pi)
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if dx * dx + dz * dz <= rr * rr + 0.3:
                        w.setze(x + dx, y - 2 - k, z + dz, w.b("white_wool" if (dx + k) % 3 else "mushroom_stem",
                                                                **({} if (dx + k) % 3 else {
                                                                    "up": True, "down": True, "north": True,
                                                                    "south": True, "east": True, "west": True})),
                                False)
    bodenstreu(w, [w.b("cobweb"), w.b("dead_bush")], int(6 * s), 2, 4 + 3 * s)
    return w


def moosriese(seed, g=0):
    """Moosriese: ein uralter Baum mit gewaltigen Brettwurzeln, Stamm und Äste dick mit Moos überzogen, lange
    hängende Wurzelranken und Farne auf den Ästen."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "mangrove_log", "mangrove_wood")
    bl = [(laub(w, "jungle"), 0.4), (laub(w, "mangrove"), 0.3), (laub(w, "azalea"), 0.3)]
    cfg = Wuchs(kinder=3, spreizung=(30, 55), laenge=0.6, biegung=0.15, auftrieb=0.02)
    _krone(w, holz, 18 * s, 1.8 * s, 0.45, bl, cfg, 2, 3.0 * s, aeste=6, neigung=(40, 65), flach=0.6,
           wurzel=(9, int(6 * s)))
    moos = w.b("moss_block")
    for (x, y, z), b in list(w.bloecke.items()):
        if b in holz.alle and w.frei(x, y + 1, z):
            if w.rng.random() < 0.55:
                w.bloecke[(x, y, z)] = moos
            if w.rng.random() < 0.25:
                w.setze(x, y + 1, z, w.b("fern") if w.rng.random() < 0.5 else w.b("moss_carpet"))
    _haengen(w, {bl[0][0], bl[1][0]}, lambda k: w.b("hanging_roots", waterlogged=False), 0.08, 4)
    _boden(w, 5 + 4 * s, [w.b("moss_block"), w.b("rooted_dirt"), w.b("podzol", snowy=False)])
    return w


def wolkenbaum(seed, g=0):
    """Wolkenbaum: ein schlanker, silbriger Stamm trägt statt Laub flauschige weiße Wolkenballen, aus denen hier
    und da ein Regentropfen aus Glas hängt."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "birch_log", "birch_wood")
    bl = [(w.b("white_wool"), 0.6), (w.b("white_concrete"), 0.15), (w.b("light_gray_wool"), 0.1),
          (w.b("snow_block"), 0.15)]
    cfg = Wuchs(kinder=2, spreizung=(25, 50), laenge=0.65, biegung=0.1, auftrieb=0.05)
    _krone(w, holz, 15 * s, 0.8 * s, 0.45, bl, cfg, 2, 2.8 * s, aeste=4, flach=0.7, luecken=0.0,
           wurzel=(4, int(3 * s)))
    _haengen(w, {bl[0][0]}, w.b("light_blue_stained_glass_pane", north=False, south=False, east=False,
                                west=False, waterlogged=False), 0.03, 2)
    return w


def herbstriese(seed, g=0):
    """Herbstriese: ein gewaltiger Ahorn mit einer Krone, die von innen nach außen von Grün über Gelb und Orange
    zu Rot verläuft, ein bunter Laubteppich darunter."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "dark_oak_log", "dark_oak_wood")
    cfg = Wuchs(kinder=3, spreizung=(25, 50), laenge=0.63, biegung=0.1, auftrieb=0.04)
    _, st, enden, mitte = _krone(w, holz, 18 * s, 1.5 * s, 0.4, None, cfg, 2, 0, aeste=6,
                                 wurzel=(7, int(4 * s)))
    stufen = [laub(w, "oak"), gelb_laub(w), orange_laub(w), rot_laub(w)]
    gabel = st[-1][0]
    rmax = 9 * s
    for p, t in enden:
        rw = 3.0 * s * (0.8 + 0.4 * w.rng.random())
        d = math.hypot(p[0] - gabel[0], p[2] - gabel[2]) / rmax
        k = min(3, int(d * 3.5 + w.rng.random() * 0.8))
        bl = [(stufen[k], 0.7), (stufen[min(3, k + 1)], 0.3)]
        blattwolke(w, p + [0, 0.6, 0], rw, rw * 0.7, bl, schutz=holz.alle, luecken=0.06, min_y=int(gabel[1] * 0.85))
    bodenstreu(w, [w.b("red_carpet"), w.b("orange_carpet"), w.b("yellow_carpet")], int(30 * s), 2, 5 + 5 * s)
    return w


def leuchtrankenweide(seed, g=0):
    """Leuchtrankenweide: eine Weide, deren Vorhänge aus Höhlenranken mit glühenden Leuchtbeeren bestehen, Glow-
    Flechten am Stamm – nachts ein schimmernder Dom."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "oak_log", "oak_wood")
    bl = [(laub(w, "oak"), 0.6), (laub(w, "azalea"), 0.4)]
    cfg = Wuchs(kinder=3, spreizung=(25, 45), laenge=0.6, biegung=0.1, auftrieb=0.0, schwerkraft=0.012)
    _krone(w, holz, 15 * s, 1.1 * s, 0.35, bl, cfg, 2, 2.6 * s, aeste=5, neigung=(15, 32), flach=0.7,
           wurzel=(5, int(3 * s)))

    def ranke(k):
        return w.b("cave_vines_plant", berries=w.rng.random() < 0.4)
    _haengen(w, {bl[0][0], bl[1][0]}, ranke, 0.12, 3 + 3 * s, min_y=3)
    for (x, y, z), b in list(w.bloecke.items()):
        if b in holz.alle:
            for dx, dz, f in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
                if w.frei(x + dx, y, z + dz) and w.rng.random() < 0.05:
                    w.setze(x + dx, y, z + dz, w.b("glow_lichen", **{k: k == f for k in
                                                                     ("north", "south", "east", "west")},
                                                   up=False, down=False, waterlogged=False))
    return w


def seelenbaum(seed, g=0):
    """Seelenbaum: ein türkis schimmernder Baum aus Wirrstielen, die Krone aus Wirrwarzen mit eingestreuten
    Seelenlaternen, Seelensand und blaue Flammen am Fuß."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "warped_stem", "warped_hyphae")
    bl = [(w.b("warped_wart_block"), 0.6), (w.b("shroomlight"), 0.08), (w.b("cyan_stained_glass"), 0.12),
          (w.b("light_blue_stained_glass"), 0.2)]
    cfg = Wuchs(kinder=2, spreizung=(25, 55), laenge=0.65, biegung=0.18, auftrieb=0.03)
    _krone(w, holz, 15 * s, 1.0 * s, 0.4, bl, cfg, 2, 2.7 * s, aeste=5, wurzel=(6, int(4 * s)))
    _haengen(w, {bl[0][0]}, lambda k: w.b("chain", axis="y", waterlogged=False) if k == 1 else
             w.b("soul_lantern", hanging=True, waterlogged=False), 0.03, 2)
    _boden(w, 4 + 3 * s, [w.b("soul_soil"), w.b("soul_sand"), w.b("warped_nylium")])
    bodenstreu(w, [w.b("warped_roots"), w.b("soul_fire")], int(8 * s), 2, 3 + 3 * s)
    return w


def goldbaum(seed, g=0):
    """Goldener Baum: ein weißer Stamm mit goldgelber Krone, darin goldene Früchte, Goldklumpen im Gras – ein
    Baum aus dem Märchen."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "birch_log", "birch_wood")
    bl = [(gelb_laub(w), 0.45), (chipped(w, "golden_oak", "hay_block"), 0.35), (laub(w, "birch"), 0.2)]
    cfg = Wuchs(kinder=3, spreizung=(25, 48), laenge=0.63, biegung=0.1, auftrieb=0.04)
    _krone(w, holz, 15 * s, 1.0 * s, 0.42, bl, cfg, 2, 2.7 * s, aeste=5, wurzel=(5, int(3 * s)))
    _haengen(w, {bl[0][0], bl[1][0]}, w.b("gold_block"), 0.03, 1)
    _boden(w, 3 + 2 * s, [w.b("moss_block"), w.b("grass_block", snowy=False)])
    bodenstreu(w, [w.b("dandelion"), w.b("sunflower", half="lower")], int(10 * s), 2, 4 + 3 * s)
    for (x, y, z), b in list(w.bloecke.items()):
        if b == w.b("sunflower", half="lower"):
            w.setze(x, y + 1, z, w.b("sunflower", half="upper"))
    return w


def treppenbaum(seed, g=0):
    """Treppenbaum: um den mächtigen Stamm windet sich eine hölzerne Wendeltreppe mit Geländer hinauf zu einer
    Aussichtsplattform in der Krone, Laternen an jeder Windung."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "spruce_log", "spruce_wood")
    bl = [(laub(w, "oak"), 0.6), (laub(w, "dark_oak"), 0.4)]
    R = 1.8 * s
    H = 20 * s
    cfg = Wuchs(kinder=3, spreizung=(30, 55), laenge=0.6, biegung=0.1, auftrieb=0.02)
    _, st, enden, mitte = _krone(w, holz, H, R, 0.55, bl, cfg, 2, 2.8 * s, aeste=5, neigung=(45, 70),
                                 wurzel=(6, int(4 * s)), min_y_f=0.95)
    yp = int(H * 0.55) - 1
    rt = R + 1.6
    n = int(yp * 4)
    for i in range(n):
        y = i / 4
        a = i * 0.42
        x, z = math.cos(a) * rt, math.sin(a) * rt
        xi, zi, yi = int(round(x)), int(round(z)), int(y) + 1
        w.setze(xi, yi, zi, w.b("spruce_slab", type="bottom", waterlogged=False))
        xo, zo = int(round(math.cos(a) * (rt + 1))), int(round(math.sin(a) * (rt + 1)))
        w.setze(xo, yi + 1, zo, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                    waterlogged=False), False)
        if i % 16 == 0:
            w.setze(xo, yi + 2, zo, w.b("lantern", hanging=False, waterlogged=False), False)
    rp = int(R + 4)
    for x in range(-rp, rp + 1):
        for z in range(-rp, rp + 1):
            d = math.hypot(x, z)
            if d <= rp:
                if (x, yp, z) not in w.bloecke or w.P.name(w.bloecke[(x, yp, z)]).endswith("leaves"):
                    w.setze(x, yp, z, w.b("spruce_planks"))
                if rp - 1 < d <= rp:
                    w.setze(x, yp + 1, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                              waterlogged=False))
    return w


def wolkenkiefer(seed, g=0):
    """Wolkenkiefer: eine wie ein Bonsai geformte Kiefer mit geschwungenem, schräg ausladendem Stamm und
    flachen, sauber geformten Nadelwolken in Etagen."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "spruce_log", "spruce_wood")
    pinsel = Pinsel(w, holz)
    bl = [(laub(w, "spruce"), 0.6), (laub(w, "jungle"), 0.2), (laub(w, "dark_oak"), 0.2)]
    st = ast(w, pinsel, [0.5, 0.5, 0.5], [0.45, 1, 0.1], 14 * s, 1.0 * s, 0.6 * s, biegung=0.12, auftrieb=0.05)
    for k in range(int(len(st) * 0.25), len(st), max(3, len(st) // 6)):
        p, pd, pr = st[k]
        sx = 1 if (k // 3) % 2 else -1
        d = [sx * 0.9, 0.15, (w.rng.random() - 0.5) * 0.8]
        pkt = ast(w, pinsel, p, d, (3 + 3 * s) * (1 - k / len(st) * 0.5), 0.5, 0.4, biegung=0.08)
        e = pkt[-1][0]
        blattwolke(w, e + [0, 0.6, 0], (2.4 + 0.8 * s), 0.9 + 0.2 * s, bl, schutz=holz.alle, dichte=1.0)
    blattwolke(w, st[-1][0] + [0, 0.6, 0], 2.6 * s, 1.2 * s, bl, schutz=holz.alle, dichte=1.0)
    _boden(w, 3 + 2 * s, [w.b("moss_block"), w.b("gravel"), w.b("mossy_cobblestone")])
    return w


def zwillingsbaum(seed, g=0):
    """Zwillingsbaum: eine Birke und eine Eiche wachsen umeinander gewunden wie ein Zopf empor und teilen sich
    eine zweifarbige Krone."""
    w = neue_welt(seed)
    s = _s(g)
    H = int(16 * s)
    blk = [w.b("birch_wood", axis="y"), w.b("dark_oak_wood", axis="y")]
    for j in range(2):
        for i in range(H * 3):
            t = i / (H * 3)
            a = t * 6.283 * 2 + j * math.pi
            r = 1.3 * s * (1 - 0.4 * t)
            kugel_f(w, (math.cos(a) * r + 0.5, t * H + 0.5, math.sin(a) * r + 0.5), 0.8 * s * (1 - 0.4 * t) + 0.3,
                    blk[j])
    kronen = [[(laub(w, "birch"), 1.0)], [(laub(w, "dark_oak"), 0.7), (laub(w, "oak"), 0.3)]]
    for j in range(2):
        for k in range(4):
            a = k * 1.57 + j * 0.78
            c = (math.cos(a) * 3.5 * s + 0.5, H + 1 + (k % 2), math.sin(a) * 3.5 * s + 0.5)
            blattwolke(w, c, 2.8 * s, 1.8 * s, kronen[(j + k) % 2], schutz=set(blk))
    blattwolke(w, (0.5, H + 2.5, 0.5), 3.0 * s, 2.0 * s, kronen[0] + kronen[1], schutz=set(blk))
    return w


def bernsteinbaum(seed, g=0):
    """Bernsteinbaum: eine knorrige Kiefer, aus deren Rinde goldener Harz in großen Tropfen quillt; in den
    Bernsteinklumpen am Fuß schimmert Licht."""
    w = neue_welt(seed)
    s = _s(g)
    holz = HolzX(w, "jungle_log", "jungle_wood")
    bl = [(laub(w, "spruce"), 0.6), (laub(w, "jungle"), 0.4)]
    cfg = Wuchs(kinder=2, spreizung=(30, 55), laenge=0.6, biegung=0.18, auftrieb=0.02)
    _krone(w, holz, 16 * s, 1.1 * s, 0.5, bl, cfg, 2, 2.4 * s, aeste=5, wurzel=(5, int(3 * s)))
    harz = [w.b("orange_stained_glass"), w.b("honey_block"), w.b("ochre_froglight", axis="y")]
    for (x, y, z), b in list(w.bloecke.items()):
        if b in holz.alle and y < 12 * s:
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if w.frei(x + dx, y, z + dz) and w.rng.random() < 0.04:
                    w.setze(x + dx, y, z + dz, harz[0] if w.rng.random() < 0.6 else harz[1])
                    if w.frei(x + dx, y - 1, z + dz) and y > 1:
                        w.setze(x + dx, y - 1, z + dz, harz[0])
    for k in range(int(5 * s)):
        a = k / (5 * s) * 6.283
        x, z = round(math.cos(a) * (3 + 2 * s)), round(math.sin(a) * (3 + 2 * s))
        w.setze(x, 1, z, harz[k % 3], False)
        w.setze(x, 0, z, w.b("honeycomb_block"))
    return w


SPEKTAKULAER2 = {
    "kristallbaum": ("Kristallbaum", kristallbaum),
    "feuerbaum": ("Feuerbaum", feuerbaum),
    "eisbaum": ("Eisbaum", eisbaum),
    "sternenbaum": ("Sternenbaum", sternenbaum),
    "lichterbaum": ("Lichterbaum", lichterbaum),
    "spiralbaum": ("Spiralbaum", spiralbaum),
    "torbaum": ("Torbaum", torbaum),
    "inselbaum": ("Inselbaum", inselbaum),
    "quellbaum": ("Quellbaum", quellbaum),
    "kokonbaum": ("Kokonbaum", kokonbaum),
    "moosriese": ("Moosriese", moosriese),
    "wolkenbaum": ("Wolkenbaum", wolkenbaum),
    "herbstriese": ("Herbstriese", herbstriese),
    "leuchtrankenweide": ("Leuchtrankenweide", leuchtrankenweide),
    "seelenbaum": ("Seelenbaum", seelenbaum),
    "goldbaum": ("Goldener Baum", goldbaum),
    "treppenbaum": ("Treppenbaum", treppenbaum),
    "wolkenkiefer": ("Wolkenkiefer", wolkenkiefer),
    "zwillingsbaum": ("Zwillingsbaum", zwillingsbaum),
    "bernsteinbaum": ("Bernsteinbaum", bernsteinbaum),
}

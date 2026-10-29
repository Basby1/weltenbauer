"""Himmelsreich II – zwanzig weitere Orte über den Wolken: Wolkenwal, Federhalle, Greifenhorst, Himmelsschaukel,
Windspiel-Pavillon, Sonnenwagen, Regenbogenquelle, Himmelsglocke, Sternenschmiede, Wolkenfähre, Flügeltor,
Mondsichel-Insel, Gewitterwolke, Seifenblasen-Garten, Sonnenscheiben-Altar, Lichtsäulen-Halle, Wolkenschafe,
Wolkenmühle, Himmelswaage und Sternschnuppen-Krater."""

from __future__ import annotations

import math

import numpy as np

from erw_basis import M, S, figur, hoehe
from feinbau import Dachmat, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from himmel import insel, wolke
from leuchtwald2 import bez, kugel, laubball, rohr
from lib import Rauschen
from skulptur import Skulptur, dreh_y, ell, kap, kasten, kegel, kreisrand
from wueste_eis import kuppel


def wolkenfeld(w, R, y=0):
    wolke(w, 0, y, 0, R, flach=0.3, dichte=9)


def marmor(w):
    return M(w, [("smooth_quartz", 3), ("quartz_bricks", 2), ("calcite", 1)])


def saeule(w, x, y0, z, h):
    w.setze(x, y0, z, w.b("chiseled_quartz_block"))
    for y in range(y0 + 1, y0 + h):
        w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    w.setze(x, y0 + h, z, w.b("gold_block"))


def oberkante(w, x, z, bis=40):
    return hoehe(w, x, z, bis, -10)


# ============================================================================ Bauten

def wolkenwal(seed, g=2):
    """Wolkenwal: ein riesiger Wal, ganz aus weißen und hellgrauen Wolkenballen geformt, gleitet über einem Wolken-
    meer, aus seinem Blasloch steigt eine Fontäne aus Licht, kleine Wolkenvögel folgen ihm."""
    w = _neu(seed)
    s = S[g]
    u = 1.0 * s + 0.5
    R = int(12 * u + 6)
    wolkenfeld(w, R)
    Sk = Skulptur(w, u)
    Sk.mat("w", lambda x, y, z, *a: w.b("white_wool") if (x + y * 2 + z) % 4 else w.b("white_concrete"))
    Sk.mat("g", w.b("light_gray_wool"))
    Sk.mat("a", w.b("light_blue_concrete"))
    Sk.plus(ell(0, 0, 0, 9, 3.5, 4), "w")
    Sk.plus(ell(1, -1.6, 0, 8, 2.0, 3.4), "g")
    Sk.plus(kap((-8, 0.5, 0), (-13, 1.8, 0), 2.2, 0.8), "w")
    Sk.plus(lambda X, Y, Z: ((X + 14) ** 2 / 2.5 + (Y - 2.2) ** 2 / 0.5 + Z ** 2 / 14 <= 1), "w")
    for sz in (-1, 1):
        Sk.plus(kap((3, -1.5, sz * 3.2), (0, -3.0, sz * 7.0), 0.9, 0.4), "w")
        Sk.plus(ell(6.5, 0.6, sz * 3.3, 0.4, 0.4, 0.3), "a")
    Sk.rendern((-16, -5, -8), (10, 5, 8), versatz=(0.5, 6 * u + 3, 0.5), dreh=dreh_y(0.4))
    for k in range(int(3 + 2 * s)):
        w.setze(round(2 * u), round(6 * u + 3 + 3.6 * u + k), 0, w.b("end_rod", facing="up") if k % 2 else
                w.b("white_stained_glass"))
    rng = w.rng
    for k in range(3 + g):
        x, y, z = int(-R * 0.6 + k * 3), int(10 * u + rng.random() * 4), int((rng.random() - 0.5) * R)
        for dx, dy in ((0, 0), (-1, 1), (1, 1)):
            w.setze(x + dx, y + dy, z, w.b("white_wool"))
    return w


def federhalle(seed, g=2):
    """Federhalle: eine offene Halle aus weißem Marmor, deren Dach von riesigen, aufrecht stehenden Federn aus
    Quarz und goldenen Kielen getragen wird, auf einem Wolkenplateau mit Freitreppe."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    wolkenfeld(w, R)
    yb = 3
    B, T = int(5 * s + 5), int(3 * s + 4)
    mm = marmor(w)
    for x in range(-B - 1, B + 2):
        for z in range(-T - 1, T + 2):
            w.setze(x, yb, z, mm(x, yb, z))
            for y in range(yb + 1, yb + 12):
                w.bloecke.pop((x, y, z), None)
    H = int(5 * s + 5)
    for x in range(-B, B + 1, 3):
        for sz in (-1, 1):
            z = sz * T
            for y in range(yb + 1, yb + H):
                w.setze(x, y, z, w.b("gold_block") if (y - yb) % H == 1 else w.b("smooth_quartz"))
                breite = round(1.2 * math.sin(math.pi * (y - yb) / H))
                for d in range(1, breite + 1):
                    w.setze(x + d, y, z, w.b("white_concrete") if (y + d) % 3 else w.b("quartz_block"), False)
                    w.setze(x - d, y, z, w.b("white_concrete") if (y + d) % 3 else w.b("quartz_block"), False)
    for x in range(-B - 1, B + 2):
        for z in range(-T - 1, T + 2):
            w.setze(x, yb + H, z, w.b("smooth_quartz_slab", type="bottom", waterlogged=False) if abs(z) < T else
                    w.b("gold_block"))
    for k in range(3):
        for x in (-2, -1, 0, 1, 2):
            w.setze(x, yb - k, T + 2 + k, w.b("quartz_stairs", facing="north", half="bottom", shape="straight",
                                               waterlogged=False))
    return w


def greifenhorst(seed, g=2):
    """Greifenhorst: auf einer schwebenden Felsinsel liegt ein Nest aus goldenen Ästen, in dem ein Greif mit
    Adlerkopf, Löwenleib und mächtigen Schwingen wacht, umgeben von Wolkenschleiern."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    yi = int(8 * s + 6)
    top = insel(w, 0, yi, 0, R * 0.7)
    for x, z in kreisrand(3 * s + 2.5):
        for k in range(2):
            w.setze(x, top + 1 + k, z, w.b("stripped_birch_log", axis="y") if (x + z) % 2 else
                    w.b("yellow_terracotta"))
    gel = w.b("yellow_terracotta")
    br = w.b("brown_wool")
    we = w.b("white_wool")
    teile = [(ell(0, 2.8, 0, 2.4, 1.3, 1.2), gel), (kap((-2.2, 2.8, 0), (-4.2, 1.6, 0), 0.4, 0.2), gel),
             (ell(-4.4, 1.4, 0, 0.5, 0.5, 0.5), br),
             (ell(1.8, 4.2, 0, 1.2, 1.4, 1.1), we), (ell(2.4, 5.6, 0, 0.9, 0.9, 0.8), we),
             (kap((3.0, 5.6, 0), (3.8, 5.0, 0), 0.4, 0.15), w.b("orange_concrete")),
             (ell(2.7, 6.0, 0.55, 0.15, 0.15, 0.1), w.b("black_concrete")),
             (ell(2.7, 6.0, -0.55, 0.15, 0.15, 0.1), w.b("black_concrete"))] + \
            [(kap((sx, 2.2, sz), (sx + 0.4, 0, sz), 0.4), gel) for sx in (-1.6, 1.4) for sz in (-0.7, 0.7)]
    for sz in (-1, 1):
        teile.append((ell(0.4, 4.6, sz * 3.6, 2.6, 1.6, 2.6), br))
        teile.append((ell(-1.0, 5.4, sz * 5.6, 2.4, 0.6, 1.6), we))
    figur(w, 0.8 * s + 0.4, teile, (-5, -1, -7), (5, 8, 7), pos=(0, top + 1, 0), winkel=0.5)
    wolke(w, -int(R * 0.6), yi - 4, int(R * 0.4), 3 + 2 * s, flach=0.4, dichte=5)
    wolke(w, int(R * 0.7), yi - 2, -int(R * 0.3), 2 + 2 * s, flach=0.4, dichte=5)
    return w


def himmelsschaukel(seed, g=2):
    """Himmelsschaukel: von einer großen, schwebenden Wolke hängt an zwei endlos langen, goldenen Ketten eine Schaukel
    mit Blumenranken herab, darunter ein kleineres Wolkenpodest mit Stufen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wolkenfeld(w, R * 0.7)
    H = int(14 * s + 10)
    wolke(w, 0, H, 0, 6 * s + 4, flach=0.45, dichte=8)
    yb = 4
    for sx in (-2, 2):
        for y in range(yb + 1, H - 1):
            w.setze(sx, y, 0, w.b("chain", axis="y", waterlogged=False))
            if y % 3 == 0:
                w.setze(sx + (1 if sx > 0 else -1), y, 0, w.b("flowering_azalea_leaves", persistent=True,
                                                              distance=1, waterlogged=False), False)
    for x in range(-2, 3):
        w.setze(x, yb, 0, w.b("birch_slab", type="top", waterlogged=False))
    for x in range(-2, 3):
        w.setze(x, yb - 1, 0, w.b("gold_block") if abs(x) == 2 else w.b("air"))
    return w


def windspiel_pavillon(seed, g=1):
    """Windspiel-Pavillon: ein filigraner, goldener Rundpavillon auf einer Wolke, unter dessen Kuppel Dutzende Wind-
    spiele aus Glasröhren, Ketten und Glocken hängen; Bänder flattern von der Spitze."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    wolkenfeld(w, R)
    yb = 3
    r = 3 * s + 2.5
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            if math.hypot(x, z) <= r + 0.5:
                w.setze(x, yb, z, w.b("smooth_quartz"))
    H = int(3 * s + 4)
    for i in range(8):
        a = i / 8 * 2 * math.pi
        saeule(w, round(math.cos(a) * r), yb, round(math.sin(a) * r), H)
    kuppel(w, lambda x, y, z, t: w.b("gold_block") if (x + z) % 3 else w.b("yellow_stained_glass"), 0, 0, yb + H + 1,
           r + 0.5, form="zwiebel", spitze="gold_block")
    rng = w.rng
    farben = ["light_blue_stained_glass", "white_stained_glass", "yellow_stained_glass", "pink_stained_glass"]
    for k in range(int(10 * s + 6)):
        a = rng.random() * 6.28
        d = rng.random() * (r - 1)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        L = int(1 + rng.random() * 3)
        for dy in range(1, L + 1):
            w.setze(x, yb + H - dy + 1, z, w.b("chain", axis="y", waterlogged=False), False)
        w.setze(x, yb + H - L, z, w.b(farben[k % 4]) if k % 5 else w.b("bell", attachment="ceiling", facing="north",
                                                                        powered=False), False)
    return w


def sonnenwagen(seed, g=2):
    """Sonnenwagen: ein goldener Streitwagen mit großen Speichenrädern und einer strahlenden Sonnenscheibe hinter dem
    Lenker, gezogen von zwei geflügelten Lichtrössern, auf einer Bahn aus Wolken."""
    w = _neu(seed)
    s = S[g]
    u = 1.1 * s + 0.5
    R = int(12 * u + 6)
    wolkenfeld(w, R * 0.75)
    gold = w.b("gold_block")
    gelb = w.b("yellow_concrete")
    we = w.b("white_concrete")
    teile = [(kasten(-2.0, 2.0, -1.4, 1.0, 3.6, 1.4), gold), (kasten(-1.6, 2.4, -1.0, 0.6, 3.8, 1.0), None),
             (kap((1.0, 2.6, 0), (6.0, 3.0, 0), 0.2), gold)]
    for sz in (-1, 1):
        teile.append((lambda X, Y, Z, sz=sz: (np.abs(np.sqrt((X + 0.5) ** 2 + (Y - 2.0) ** 2) - 1.8) < 0.3) &
                      (np.abs(Z - sz * 1.6) < 0.25), gold))
        teile.append((lambda X, Y, Z, sz=sz: ((np.abs(X + 0.5) < 0.2) | (np.abs(Y - 2.0) < 0.2)) &
                      (np.sqrt((X + 0.5) ** 2 + (Y - 2.0) ** 2) < 1.8) & (np.abs(Z - sz * 1.6) < 0.2), gelb))
    teile.append((lambda X, Y, Z: ((X + 2.4) ** 2 / 0.1 + (Y - 6.0) ** 2 / 9 + Z ** 2 / 9 <= 1), gelb))
    for k, sz in enumerate((-1, 1)):
        hz = sz * 1.0
        pf = w.b("yellow_terracotta")
        teile += [(ell(7.5, 4.0, hz, 1.8, 0.9, 0.7), pf), (kap((8.8, 4.4, hz), (9.6, 6.0, hz), 0.5, 0.4), pf),
                  (ell(10.0, 6.0, hz, 0.8, 0.45, 0.4), pf), (kap((8.6, 5.0, hz), (9.4, 6.8, hz), 0.3), gold)]
        teile += [(kap((sx, 3.6, hz + zz), (sx + 0.6 * (1 if sx > 7.5 else -1), 1.0, hz + zz), 0.25), we)
                  for sx in (6.5, 8.5) for zz in (-0.3, 0.3)]
        teile[-4:] = [(f, pf) for f, _ in teile[-4:]]
        teile.append((ell(7.2, 5.5, hz + sz * 1.6, 1.4, 0.4, 1.2), w.b("yellow_stained_glass")))
    figur(w, u, teile, (-6, -1, -6), (12, 10, 6), pos=(-int(4 * u), 2, 0), winkel=0.3)
    return w


def regenbogenquelle(seed, g=2):
    """Regenbogenquelle: von einer hohen Wolkeninsel stürzt ein Wasserfall in sieben Farben (gestreiftes Glas) in
    ein schimmerndes Becken auf dem Wolkenmeer, umgeben von Lichtkristallen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wolkenfeld(w, R)
    H = int(14 * s + 10)
    top = insel(w, -int(R * 0.35), H, 0, R * 0.4)
    farben = ["red_stained_glass", "orange_stained_glass", "yellow_stained_glass", "lime_stained_glass",
              "light_blue_stained_glass", "blue_stained_glass", "purple_stained_glass"]
    x0 = -int(R * 0.35) + int(R * 0.4) - 1
    for y in range(3, top + 1):
        for i, f in enumerate(farben):
            z = i - 3
            vor = round((top - y) * 0.15)
            w.setze(x0 + 1 + vor, y, z, w.b(f), False)
    for x in range(x0, x0 + int(6 * s + 4)):
        for z in range(-5, 6):
            if math.hypot(x - x0 - 3 * s, z) < 3 * s + 2:
                w.setze(x, 3, z, w.b("water", level=0))
    rng = w.rng
    for _ in range(int(6 * s + 3)):
        a = rng.random() * 6.28
        x, z = round(x0 + 3 * s + math.cos(a) * (3 * s + 3)), round(math.sin(a) * (3 * s + 3))
        w.setze(x, 4, z, w.b("amethyst_cluster", facing="up", waterlogged=False))
    return w


def himmelsglocke(seed, g=2):
    """Himmelsglocke: eine riesige goldene Glocke hängt in einem schwebenden Glockenstuhl aus Marmorbögen zwischen
    zwei Wolkentürmen, darunter ein Klöppel aus Licht und ein Wolkenpodest."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wolkenfeld(w, R)
    H = int(14 * s + 10)
    rg = 3 * s + 2
    for sx in (-1, 1):
        x0 = sx * int(rg + 4)
        for y in range(3, H + 2):
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    w.setze(x0 + dx, y, dz, w.b("smooth_quartz") if y % 4 else w.b("gold_block"))
        wolke(w, x0, 3, 0, 3 + s, flach=0.5, dichte=4)
    for x in range(-int(rg + 4), int(rg + 5)):
        w.setze(x, H + 2, 0, w.b("quartz_bricks"))
        w.setze(x, H + 3, 0, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
    for k in range(int(rg * 2.2)):
        t = k / (rg * 2.2)
        r = rg * (0.35 + 0.65 * t ** 1.6)
        for x, z in kreisrand(max(0.5, r)):
            w.setze(x, H + 1 - k, z, w.b("gold_block") if k % 4 else w.b("yellow_concrete"))
    w.setze(0, H + 1 - int(rg * 2.2), 0, w.b("sea_lantern"))
    w.setze(0, H - int(rg * 2.2), 0, w.b("end_rod", facing="down"))
    return w


def sternenschmiede(seed, g=2):
    """Sternenschmiede: auf einer Wolkeninsel eine offene Schmiede mit Amboss aus Mondstein, in deren Esse Sterne
    geschmiedet werden – leuchtende Kugeln kühlen in einem Becken, fertige Sterne hängen an Ketten am Himmel."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wolkenfeld(w, R)
    yb = 3
    B, T = int(4 * s + 5), int(3 * s + 4)
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            w.setze(x, yb, z, w.b("smooth_quartz") if (x + z) % 2 else w.b("calcite"))
            if abs(x) == B and abs(z) == T:
                for y in range(yb + 1, yb + 6):
                    w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    satteldach(w, -B, -T, B, T, yb + 6, Dachmat(w, ["quartz", "smooth_quartz"]), first_x=True, ue=1, giebel=None,
               traufe="birch")
    for x in range(-2, 3):
        for z in range(-T + 1, -T + 4):
            w.setze(x, yb + 1, z, w.b("calcite"))
            w.setze(x, yb + 2, z, w.b("shroomlight") if abs(x) < 2 else w.b("calcite"))
    w.setze(0, yb + 1, 0, w.b("anvil", facing="east"))
    w.setze(0, yb + 2, 0, w.b("glowstone"))
    for x in range(2, 5):
        w.setze(x, yb + 1, T - 1, w.b("water", level=0))
    w.setze(3, yb + 1, T - 1, w.b("sea_lantern"))
    rng = w.rng
    for k in range(int(5 * s + 3)):
        x, z = int((rng.random() - 0.5) * R * 1.4), int((rng.random() - 0.5) * R * 1.4)
        y = int(12 * s + 8 + rng.random() * 6)
        for d in range(1, 4):
            w.setze(x, y + d, z, w.b("chain", axis="y", waterlogged=False))
        for dx, dy, dz in ((0, 0, 0), (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            w.setze(x + dx, y + dy, z + dz, w.b("glowstone") if (dx, dy, dz) == (0, 0, 0) else
                    w.b("yellow_stained_glass"))
    return w


def wolkenfaehre(seed, g=2):
    """Wolkenfähre: ein weißes Boot mit Schwanenhals-Bug und Segel aus Licht gleitet auf einem Fluss aus Wolken
    zwischen zwei Anlegestegen aus Marmor, an denen Laternen leuchten."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wolkenfeld(w, R)
    L = int(5 * s + 4)
    B = 1.6 * s + 1.4
    y0 = 4
    for i in range(-L, L + 1):
        t = i / (L + 0.5)
        bw = B * math.sqrt(max(0, 1 - t * t))
        for q in range(-int(bw) - 1, int(bw) + 2):
            if abs(q) <= bw:
                w.setze(i, y0, q, w.b("white_concrete"))
                if abs(q) > bw - 1:
                    w.setze(i, y0 + 1, q, w.b("gold_block") if i % 3 == 0 else w.b("white_concrete"))
    for k in range(int(3 * s + 3)):
        w.setze(L + k // 2, y0 + 1 + k, 0, w.b("white_concrete"))
    w.setze(L + int(3 * s + 3) // 2 + 1, y0 + int(3 * s + 3), 0, w.b("orange_concrete"))
    H = int(7 * s + 6)
    for y in range(y0 + 1, y0 + H):
        w.setze(0, y, 0, w.b("birch_log", axis="y"))
    for y in range(y0 + 3, y0 + H - 1):
        bb = round((y - y0 - 2) * 0.5)
        for z in range(-bb, bb + 1):
            w.setze(-1, y, z, w.b("white_stained_glass") if (y + z) % 3 else w.b("yellow_stained_glass"))
    for sx in (-1, 1):
        x0 = sx * (L + 5)
        for x in range(x0 - 2, x0 + 3):
            for z in range(-2, 3):
                w.setze(x, 3, z, w.b("smooth_quartz"))
        for z in (-2, 2):
            for y in range(4, 7):
                w.setze(x0, y, z, w.b("quartz_pillar", axis="y"))
            w.setze(x0, 7, z, w.b("lantern", hanging=False, waterlogged=False))
    return w


def fluegeltor(seed, g=2):
    """Flügeltor: ein gewaltiges Tor, dessen zwei Seiten als riesige, gefiederte Engelsflügel aus weißem Stein und
    goldenen Federkielen geformt sind, die sich oben über einem Lichtstern berühren."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wolkenfeld(w, R * 0.8)
    H = int(18 * s + 12)
    for sx in (-1, 1):
        for k in range(7):
            pts = bez((sx * 2, 3, 0), (sx * (8 + k * 1.0) * s, H * (0.4 + k * 0.06), 0),
                      (sx * (1 + k * 0.5), H - k * s * 1.4, 0))
            for px, py, pz, t in pts:
                for dz in (-1, 0, 1):
                    w.setze(round(px), round(py), dz, w.b("gold_block") if k == 0 and dz == 0 else
                            w.b("white_concrete") if (k + round(py)) % 3 else w.b("smooth_quartz"), False)
    for x in range(-1, 2):
        for y in range(3, 3 + int(H * 0.5)):
            w.bloecke.pop((x, y, 0), None)
    w.setze(0, H + 1, 0, w.b("sea_lantern"))
    for d in range(1, 3):
        for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
            w.setze(dx, H + 1 + dy, 0, w.b("gold_block"))
    return w


def mondsichel_insel(seed, g=2):
    """Mondsichel-Insel: eine schwebende Insel in Form einer schmalen Mondsichel aus hellem Stein, auf deren innerer
    Rundung ein kleiner Mondtempel steht, mit silbernen Bäumen und Laternen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    Ra = 9 * s + 5
    Ri = Ra * 0.75
    yo = int(8 * s + 6)
    for x in range(-int(Ra) - 1, int(Ra) + 2):
        for z in range(-int(Ra) - 1, int(Ra) + 2):
            aus = x * x + z * z <= Ra * Ra
            inn = (x - Ra * 0.38) ** 2 + z * z <= Ri * Ri
            if aus and not inn:
                d = math.hypot(x, z) / Ra
                tief = int(3 + 5 * s * (1 - d))
                for y in range(yo - tief, yo + 1):
                    w.setze(x, y, z, w.b("calcite") if y == yo else w.b("diorite") if (x + y) % 3 else
                            w.b("smooth_quartz"))
    tx = -int(Ra * 0.75)
    for i in range(6):
        a = i / 6 * 2 * math.pi
        saeule(w, tx + round(math.cos(a) * 2), yo + 1, round(math.sin(a) * 2), int(3 + s))
    kuppel(w, w.b("light_blue_stained_glass"), tx, 0, yo + int(4 + s) + 1, 2.5, form="rund", spitze="sea_lantern")
    for k in range(2 + g):
        a = math.pi * (0.6 + 0.8 * k / (1 + g))
        x, z = round(math.cos(a) * Ra * 0.85), round(math.sin(a) * Ra * 0.85)
        for y in range(yo + 1, yo + 4):
            w.setze(x, y, z, w.b("birch_log", axis="y"))
        laubball(w, x, yo + 5, z, 1.6 + 0.5 * s, arten=("white_stained_glass",), dicht=0.8)
    return w


def gewitterwolke(seed, g=2):
    """Gewitterwolke: eine dunkle, aufgetürmte Gewitterwolke schwebt über einer kleinen Felsinsel mit Blitzableiter-
    Turm; gelbe Blitze aus Glas zucken im Zickzack zwischen Wolke und Turmspitze."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    top = insel(w, 0, int(4 * s + 3), 0, R * 0.5)
    H = int(6 * s + 5)
    for y in range(top + 1, top + H):
        for x, z in kreisrand(1.4):
            w.setze(x, y, z, w.b("stone_bricks"))
    for y in range(top + H, top + H + 4):
        w.setze(0, y, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    wy = top + H + int(8 * s + 6)
    Sk = Skulptur(w, 1.0)
    Sk.mat("d", lambda x, y, z, *a: w.b("gray_wool") if (x + y + z) % 3 else w.b("light_gray_wool"))
    Sk.mat("u", w.b("black_wool"))
    rng = w.rng
    for i in range(9):
        a = i * 2.4
        d = R * 0.45 * math.sqrt((i + 0.5) / 9)
        rr = R * (0.3 + 0.2 * rng.random())
        Sk.plus(ell(math.cos(a) * d, rng.random() * rr * 0.6, math.sin(a) * d, rr, rr * 0.6, rr), "d")
    Sk.plus(ell(0, -R * 0.15, 0, R * 0.7, R * 0.12, R * 0.7), "u")
    Sk.rendern((-R, -R * 0.5, -R), (R, R, R), versatz=(0.5, wy, 0.5))
    for k in range(3):
        x, y, z = (k - 1) * int(R * 0.4), wy - int(R * 0.15), (k % 2) * 3
        while y > top + 2:
            w.setze(x, y, z, w.b("yellow_stained_glass"), False)
            y -= 1
            if y % 3 == 0:
                x += 1 if (k + y) % 2 else -1
    return w


def seifenblasen(seed, g=1):
    """Seifenblasen-Garten: ein Wolkengarten mit zierlichen Blumenbeeten, über dem schillernde Seifenblasen aus
    farbigem Glas in allen Größen schweben, eine riesige Blasen-Pfeife steht in der Mitte."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wolkenfeld(w, R)
    rng = w.rng
    for k in range(int(10 * s + 6)):
        x, z = int((rng.random() - 0.5) * R * 1.4), int((rng.random() - 0.5) * R * 1.4)
        y = int(6 + rng.random() * 10 * s)
        r = 0.8 + rng.random() * 2.2 * s
        f = ["light_blue_stained_glass", "pink_stained_glass", "magenta_stained_glass", "lime_stained_glass",
             "white_stained_glass"][k % 5]
        kugel(w, x, y, z, r, w.b(f), hohl=True, ueber=False)
    for k in range(8):
        a = k / 8 * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)
        y = oberkante(w, x, z, 12) + 1
        w.setze(x, y, z, w.b(["pink_tulip", "allium", "azure_bluet", "lilac"][k % 4],
                             **({"half": "lower"} if k % 4 == 3 else {})))
    for y in range(4, 8):
        w.setze(0, y, 0, w.b("gold_block") if y == 7 else w.b("birch_fence"))
    for x, z in kreisrand(1.4, 0, 0):
        w.setze(x, 8, z, w.b("gold_block"))
    return w


def sonnenscheibe(seed, g=2):
    """Sonnenscheiben-Altar: auf einer gestuften Marmorpyramide über den Wolken steht eine riesige, goldene Sonnen-
    scheibe mit Strahlenkranz, getragen von zwei Säulen, vor ihr ein Altar mit ewiger Flamme."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wolkenfeld(w, R)
    mm = marmor(w)
    for k in range(4):
        a = int(5 * s + 5) - k * 2
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                w.setze(x, 3 + k, z, mm(x, 3 + k, z))
    yb = 7
    rs = 4 * s + 3
    yc = yb + int(rs) + 3
    for x in range(-int(rs) - 4, int(rs) + 5):
        for y in range(-int(rs) - 4, int(rs) + 5):
            d = math.hypot(x, y)
            ang = math.atan2(y, x)
            if d <= rs:
                w.setze(x, yc + y, 0, w.b("shroomlight") if d < rs * 0.4 else w.b("gold_block"))
            elif d <= rs + 3.5 and int((ang + math.pi) / (math.pi / 8)) % 2 == 0 and \
                    d <= rs + 3.5 * (1 - abs(((ang + math.pi) % (math.pi / 8)) / (math.pi / 8) - 0.5) * 2):
                w.setze(x, yc + y, 0, w.b("yellow_concrete"))
    for sx in (-1, 1):
        saeule(w, sx * (int(rs) + 2), yb, 1, yc - yb)
    w.setze(0, yb, 3, w.b("chiseled_quartz_block"))
    w.setze(0, yb + 1, 3, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


def lichtsaeulen(seed, g=2):
    """Lichtsäulen-Halle: eine dachlose Halle aus Marmorbögen, in der statt Säulen senkrechte Strahlen aus Licht
    (Endstäbe, Seelaternen, weißes Glas) von Boden zu Himmel reichen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wolkenfeld(w, R)
    B, T = int(6 * s + 5), int(3 * s + 3)
    yb = 3
    mm = marmor(w)
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            w.setze(x, yb, z, mm(x, yb, z))
    H = int(8 * s + 6)
    for x in range(-B, B + 1, 3):
        for sz in (-1, 1):
            z = sz * T
            for y in range(yb + 1, yb + H + 6):
                w.setze(x, y, z, w.b("end_rod", facing="up") if y % 4 == 0 else w.b("white_stained_glass") if y % 4
                        else w.b("sea_lantern"))
        for sz in (-1, 1):
            w.setze(x, yb + 1, sz * T, w.b("sea_lantern"))
    for x in range(-B, B + 1):
        for sz in (-1, 1):
            if x % 3:
                k = x % 3
                w.setze(x, yb + H + (1 if k == 1 or k == 2 else 0), sz * T, w.b("smooth_quartz"))
    return w


def wolkenschafe(seed, g=1):
    """Wolkenschafe: eine Herde flauschiger Schafe aus Wolken grast auf einer Wolkenwiese mit Sternblumen, bewacht
    von einem kleinen Hirtenhäuschen aus Marmor mit goldenem Dach und einem Glockenpfahl."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    insel(w, 0, 3, 0, R * 0.75, tief=4 * s + 3)
    wolke(w, int(R * 0.7), 0, int(R * 0.4), 3 + s, flach=0.4, dichte=5)
    wolke(w, -int(R * 0.7), 1, -int(R * 0.3), 3 + s, flach=0.4, dichte=5)
    rng = w.rng
    we = w.b("white_wool")
    gr = w.b("black_wool")
    for k in range(4 + 2 * g):
        a = rng.random() * 6.28
        d = R * (0.2 + rng.random() * 0.55)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = oberkante(w, x, z, 12) + 1
        teile = [(ell(0, 1.8, 0, 1.4, 1.0, 1.0), we), (ell(-0.6, 2.3, 0.5, 0.8, 0.7, 0.7), we),
                 (ell(0.6, 2.2, -0.5, 0.8, 0.7, 0.7), we), (ell(1.4, 2.2, 0, 0.5, 0.45, 0.4), gr)] + \
                [(kap((sx, 1.0, sz), (sx, 0, sz), 0.2), gr) for sx in (-0.8, 0.8) for sz in (-0.4, 0.4)]
        figur(w, 0.6 * s + 0.5, teile, (-2, -1, -2), (2, 4, 2), pos=(x, y, z), winkel=rng.random() * 6.28)
    hx, hz = -int(R * 0.45), -int(R * 0.35)
    hy = oberkante(w, hx, hz, 12) + 1
    for x in range(hx - 2, hx + 3):
        for z in range(hz - 2, hz + 3):
            w.setze(x, hy - 1, z, w.b("smooth_quartz"))
            if abs(x - hx) == 2 or abs(z - hz) == 2:
                for y in range(hy, hy + 3):
                    w.setze(x, y, z, w.b("quartz_bricks"))
    kegeldach(w, hx, hz, hy + 3, 2, Dachmat(w, ["mcw:yellow_terracotta", "smooth_sandstone"]), form="kegel",
              eckig=True, spitze="gold_block")
    w.bloecke.pop((hx, hy, hz + 2), None)
    w.bloecke.pop((hx, hy + 1, hz + 2), None)
    return w


def wolkenmuehle(seed, g=2):
    """Wolkenmühle: eine weiße Windmühle mit Flügeln aus Segeltuch steht auf einer kleinen Wolkeninsel und mahlt
    Sternenstaub – aus ihr rieselt glitzerndes Licht in Säcke, ein Weg aus Wolkenplatten führt hin."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wolkenfeld(w, R)
    H = int(9 * s + 7)
    for y in range(3, H):
        r = (2.5 * s + 2) * (1 - 0.3 * (y - 3) / H)
        for x, z in kreisrand(r):
            w.setze(x, y, z, w.b("white_concrete") if (x + y) % 6 else w.b("quartz_bricks"))
    kegeldach(w, 0, 0, H, int(2 * s + 1.5), Dachmat(w, ["mcw:light_blue_terracotta", "prismarine"]), form="kegel",
              spitze="gold_block")
    hz = round(2.5 * s + 2) + 1
    for i in range(4):
        a = i * math.pi / 2 + 0.4
        L = int(6 * s + 5)
        for k in range(1, L):
            x, y = round(math.cos(a) * k), H - 2 + round(math.sin(a) * k)
            w.setze(x, y, hz, w.b("birch_fence"), False)
            if k > 2:
                px, py = round(-math.sin(a) * 1), round(math.cos(a) * 1)
                w.setze(x + px, y + py, hz, w.b("white_wool"), False)
                w.setze(x + 2 * px, y + 2 * py, hz, w.b("white_wool"), False)
    for k in range(3):
        w.setze(-int(2.5 * s + 4) + k, 3, 2, w.b("white_wool"))
        w.setze(-int(2.5 * s + 4) + k, 4, 2, w.b("yellow_stained_glass") if k % 2 else w.b("air"))
    return w


def himmelswaage(seed, g=2):
    """Himmelswaage: eine riesige, goldene Balkenwaage schwebt über den Wolken, in der einen Schale eine Feder,
    in der anderen ein Herz aus rotem Glas, perfekt im Gleichgewicht über einem Marmorsockel."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wolkenfeld(w, R)
    H = int(12 * s + 9)
    mm = marmor(w)
    for k in range(3):
        a = int(2 * s + 2) - k
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                w.setze(x, 3 + k, z, mm(x, 3 + k, z))
    for y in range(6, H):
        w.setze(0, y, 0, w.b("gold_block"))
    L = int(6 * s + 4)
    for x in range(-L, L + 1):
        w.setze(x, H, 0, w.b("gold_block"))
    w.setze(0, H + 1, 0, w.b("sea_lantern"))
    for sx in (-1, 1):
        x = sx * L
        for k in range(1, int(4 * s + 3)):
            for dz in (-1, 1):
                w.setze(x + round(dz * k * 0.3), H - k, dz * round(k * 0.3), w.b("chain", axis="y", waterlogged=False),
                        False)
        ys = H - int(4 * s + 3)
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if dx * dx + dz * dz <= 5:
                    w.setze(x + dx, ys, dz, w.b("gold_block"))
        if sx < 0:
            for k in range(3):
                w.setze(x + k - 1, ys + 1 + (k == 1), 0, w.b("white_wool"))
        else:
            w.setze(x, ys + 1, 0, w.b("red_stained_glass"))
            w.setze(x - 1, ys + 2, 0, w.b("red_stained_glass"))
            w.setze(x + 1, ys + 2, 0, w.b("red_stained_glass"))
    return w


def sternschnuppe(seed, g=2):
    """Sternschnuppen-Krater: in eine Wolkeninsel ist ein Stern gestürzt – ein glühender Kristallklumpen in einem
    Krater aus aufgeworfenen Wolkenballen, mit einer langen, verblassenden Leuchtspur am Himmel."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wolkenfeld(w, R)
    rk = 3 * s + 2.5
    for x in range(-int(rk) - 3, int(rk) + 4):
        for z in range(-int(rk) - 3, int(rk) + 4):
            d = math.hypot(x, z)
            if d <= rk:
                for y in range(2, 8):
                    w.bloecke.pop((x, y, z), None)
            elif d <= rk + 2.5:
                for y in range(2, 5 + round(2 * (1 - (d - rk) / 2.5))):
                    w.setze(x, y, z, w.b("white_wool"), False)
    kugel(w, 0, 3, 0, 1.6 + 0.5 * s, w.b("glowstone"))
    for k in range(6):
        a = k / 6 * 2 * math.pi
        for t in range(int(2 + s)):
            w.setze(round(math.cos(a) * (1.8 + t)), 3 + t, round(math.sin(a) * (1.8 + t)), w.b("yellow_stained_glass"))
    L = int(20 * s + 10)
    for k in range(L):
        x = round(k * 0.9)
        y = 4 + round(k * 0.6)
        f = "glowstone" if k < L * 0.2 else "yellow_stained_glass" if k < L * 0.5 else "white_stained_glass"
        for d in range(max(0, 2 - k // (L // 3 + 1))):
            w.setze(x, y + d, 0, w.b(f), False)
        w.setze(x, y, 0, w.b(f), False)
    return w


HIMMEL3 = {
    "wolkenwal": ("Wolkenwal", wolkenwal),
    "federhalle": ("Federhalle", federhalle),
    "greifenhorst": ("Greifenhorst", greifenhorst),
    "himmelsschaukel": ("Himmelsschaukel", himmelsschaukel),
    "windspiel_pavillon": ("Windspiel-Pavillon", windspiel_pavillon),
    "sonnenwagen": ("Sonnenwagen", sonnenwagen),
    "regenbogenquelle": ("Regenbogenquelle", regenbogenquelle),
    "himmelsglocke": ("Himmelsglocke", himmelsglocke),
    "sternenschmiede": ("Sternenschmiede", sternenschmiede),
    "wolkenfaehre": ("Wolkenfähre", wolkenfaehre),
    "fluegeltor": ("Flügeltor", fluegeltor),
    "mondsichel_insel": ("Mondsichel-Insel", mondsichel_insel),
    "gewitterwolke": ("Gewitterwolke", gewitterwolke),
    "seifenblasen": ("Seifenblasen-Garten", seifenblasen),
    "sonnenscheibe": ("Sonnenscheiben-Altar", sonnenscheibe),
    "lichtsaeulen": ("Lichtsäulen-Halle", lichtsaeulen),
    "wolkenschafe": ("Wolkenschafe", wolkenschafe),
    "wolkenmuehle": ("Wolkenmühle", wolkenmuehle),
    "himmelswaage": ("Himmelswaage", himmelswaage),
    "sternschnuppe": ("Sternschnuppen-Krater", sternschnuppe),
}

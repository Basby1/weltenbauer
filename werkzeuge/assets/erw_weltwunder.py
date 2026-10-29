"""Weltwunder II – zwanzig weitere, eigens erdachte Wunderwerke: Gezeitenfontäne, Wurzelkathedrale, Säulenwald der
Riesen, Hängende Stadt, Treppenberg, Elefantenpalast, Händebrücke, Kaskadenpalast, Lichtdom, Doppelhelix-Turm,
Sanduhrturm, Umgekehrte Pyramide, Schalenstadt, Kompassplatz, Regenbogen-Aquädukt, Titanenschwerter, Rad der
Jahreszeiten, Wasserfallfestung, Kristallorgel und Arche auf dem Berg."""

from __future__ import annotations

import math

import numpy as np

from erw_basis import M, S, baum, figur, haus, hoehe, wiese
from feinbau import Dachmat, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, laubball, rohr
from lib import Rauschen
from skulptur import Skulptur, dreh_y, dreh_z, ell, kap, kasten, kegel, kreisrand
from wueste_eis import kuppel

W = [0.7, 1.0, 1.5, 2.3]


def marmor(w):
    return M(w, [("smooth_quartz", 3), ("quartz_bricks", 2), ("calcite", 1)])


def sandst(w):
    return M(w, [("smooth_sandstone", 3), ("cut_sandstone", 2), ("sandstone", 1)])


def saeule(w, x, y0, z, h, r=0.0, mat="quartz_pillar", kap_="chiseled_quartz_block"):
    for y in range(y0, y0 + h):
        if r <= 0.6:
            w.setze(x, y, z, w.b(mat, axis="y") if "pillar" in mat else w.b(mat))
        else:
            for dx, dz in kreisrand(r, x, z):
                w.setze(dx, y, dz, w.b(mat, axis="y") if "pillar" in mat else w.b(mat))
    w.setze(x, y0 + h, z, w.b(kap_))


# ============================================================================ Bauten

def gezeitenfontaene(seed, g=2):
    """Gezeitenfontäne: ein riesiges, gestuftes Rundbecken aus Marmor, aus dessen Mitte eine Säule aus Wasser und Glas
    emporsteigt und sich in vier weiten Bögen in die äußeren Becken ergießt, umringt von Meerespferd-Statuen."""
    w = _neu(seed)
    s = W[g]
    R = int(16 * s + 8)
    wiese(w, R, 0.05, art="kies")
    mm = marmor(w)
    for k in range(3):
        rr = R * (0.85 - k * 0.25)
        y = k * 2 + 1
        for x in range(-int(rr) - 1, int(rr) + 2):
            for z in range(-int(rr) - 1, int(rr) + 2):
                d = math.hypot(x, z)
                if d <= rr:
                    for yy in range(1, y + 1):
                        w.setze(x, yy, z, mm(x, yy, z))
                    w.setze(x, y + 1, z, w.b("water", level=0) if d < rr - 1.2 else w.b("chiseled_quartz_block")
                            if int(math.atan2(z, x) * 8) % 2 else mm(x, y + 1, z))
    H = int(14 * s + 10)
    for y in range(7, H):
        for x, z in kreisrand(1.2 + 0.4 * s):
            w.setze(x, y, z, w.b("light_blue_stained_glass") if y % 3 else w.b("water", level=0))
        w.setze(0, y, 0, w.b("sea_lantern") if y % 4 == 0 else w.b("water", level=0))
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        rb = R * 0.6
        for k in range(int(rb * 3)):
            t = k / (rb * 3)
            x = math.cos(a) * rb * t
            z = math.sin(a) * rb * t
            y = H - 2 + 4 * s * math.sin(math.pi * t) - t * (H - 6)
            w.setze(round(x), round(y), round(z), w.b("light_blue_stained_glass"), False)
            if k % 3 == 0:
                w.setze(round(x), round(y) - 1, round(z), w.b("water", level=0), False)
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.85), round(math.sin(a) * R * 0.85)
        teile = [(kap((0, 0, 0), (0, 3.2, 0.6), 0.9, 0.7), w.b("prismarine_bricks")),
                 (ell(0, 4.0, 1.2, 0.7, 0.8, 1.0), w.b("prismarine_bricks")),
                 (kap((0, 0.5, -0.6), (0, -0.2, -2.4), 0.6, 0.2), w.b("prismarine")),
                 (kap((0, 4.6, 0.4), (0, 5.4, -0.6), 0.25), w.b("dark_prismarine"))]
        figur(w, 0.9 * s + 0.5, teile, (-2, -1, -3), (2, 6, 3), pos=(x, 2, z), winkel=-a - math.pi / 2)
    return w


def wurzelkathedrale(seed, g=2):
    """Wurzelkathedrale: eine Kathedrale, deren Säulen, Rippengewölbe und Spitzbögen ganz aus den gewaltigen,
    lebenden Wurzeln eines Baumriesen gewachsen sind; durch Lücken fällt Licht, Fenster aus buntem Laub."""
    w = _neu(seed)
    s = W[g]
    R = int(15 * s + 8)
    zellen = wiese(w, R, 0.2, art="wald")
    L = int(10 * s + 6)
    B = int(4 * s + 4)
    H = int(10 * s + 8)
    for k in range(-L, L + 1, max(3, int(3 * s))):
        for sz in (-1, 1):
            pts = bez((k, 0, sz * (B + 1)), (k, H * 0.7, sz * (B + 1.5)), (k, H, sz * 1.0), (k, H + 2, 0))
            rohr(w, pts, 1.0 * s + 0.6, 0.6 * s + 0.3, mat=w.b("oak_wood", axis="y"), rauh=0.15)
    for z in (-B - 1, B + 1):
        pts = [(x, H * 0.55 + math.sin(x / 2.5) * 1.5, z, 0) for x in np.linspace(-L, L, 80)]
        rohr(w, pts, 0.5 * s + 0.3, 0.5 * s + 0.3, mat=w.b("oak_wood", axis="y"), rauh=0.1)
    farben = ["flowering_azalea_leaves", "azalea_leaves", "cherry_leaves", "oak_leaves"]
    rng = w.rng
    for x in range(-L, L + 1):
        for z in (-B - 1, B + 1):
            for y in range(2, int(H * 0.5)):
                if w.frei(x, y, z) and rng.random() < 0.6:
                    w.setze(x, y, z, w.b(farben[(x // 3 + y // 3) % 4], persistent=True, distance=1,
                                         waterlogged=False))
    tx = -L - int(4 * s) - 2
    rohr(w, bez((tx, 0, 0), (tx + 1, H, 0.5), (tx, H * 2, 0)), 3 * s + 1.5, 1.8 * s + 1, mat=w.b("oak_log", axis="y"),
         rauh=0.12)
    laubball(w, tx, H * 2 + 2, 0, 7 * s + 3, arten=("oak_leaves", "flowering_azalea_leaves"), dicht=0.85)
    for x in range(-L, L + 1):
        for z in (-1, 0, 1):
            if (x, z) in zellen:
                w.setze(x, zellen[(x, z)], z, w.b("moss_block"))
    for x in range(-L + 2, L - 1, 4):
        w.setze(x, 1, 0, w.b("shroomlight"))
    return w


def saeulenwald(seed, g=2):
    """Säulenwald der Riesen: Hunderte gewaltiger Steinsäulen in strengem Raster, verbunden durch Rundbögen in
    mehreren Ebenen, ein steinerner Wald ohne Dach, in dessen Mitte ein Lichtschacht auf einen Altar fällt."""
    w = _neu(seed)
    s = W[g]
    R = int(15 * s + 8)
    wiese(w, R, 0.05, art="kies")
    st = M(w, [("stone_bricks", 3), ("polished_andesite", 1), ("smooth_stone", 1)])
    a = int(4 + 2 * s)
    H = int(12 * s + 8)
    n = int(R * 0.85 / a)
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, z = i * a, j * a
            if math.hypot(x, z) > R * 0.85:
                continue
            for y in range(1, H):
                w.setze(x, y, z, st(x, y, z))
                if s > 1.2:
                    for dx, dz in ((1, 0), (0, 1), (1, 1)):
                        w.setze(x + dx, y, z + dz, st(x, y, z))
            for lvl in (H * 0.5, H - 1):
                for d in range(1, a):
                    yb = int(lvl + 1.5 * math.sin(math.pi * d / a))
                    w.setze(x + d, yb, z, st(x + d, yb, z))
                    w.setze(x, yb, z + d, st(x, yb, z + d))
    for x in range(-a + 1, a):
        for z in range(-a + 1, a):
            for y in range(1, H + 3):
                if not (abs(x) <= 0 and abs(z) <= 0):
                    pass
    w.setze(0, 1, 0, w.b("chiseled_stone_bricks"))
    w.setze(0, 2, 0, w.b("sea_lantern"))
    for y in range(3, H + 4):
        if y % 3 == 0:
            w.setze(0, y, 0, w.b("end_rod", facing="up"), False)
    return w


def haengende_stadt(seed, g=2):
    """Hängende Stadt: unter einem gewaltigen natürlichen Felsbogen hängen kopfüber Häuser, Türme und Brücken wie
    Tropfsteine, verbunden durch Ketten und Treppen, mit Laternen und Hängegärten."""
    w = _neu(seed)
    s = W[g]
    R = int(15 * s + 8)
    zellen = wiese(w, R, 0.2)
    st = M(w, [("stone", 3), ("andesite", 2), ("tuff", 1)])
    H = int(16 * s + 12)
    Lb = R * 0.9
    pts = [(x, H - (x / Lb) ** 4 * H * 0.9 if abs(x) < Lb else 0, 0, (x + Lb) / (2 * Lb)) for x in
           np.linspace(-Lb, Lb, 120)]
    pts = [(x, max(0, H * (1 - (abs(x) / Lb) ** 3)), 0, t) for x, _, _, t in pts]
    rohr(w, pts, 3 * s + 2, 3 * s + 2, mat=lambda x, y, z, *a: st(x, y, z), rauh=0.25)
    rng = w.rng
    wand = M(w, [("white_terracotta", 2), ("calcite", 1)])
    for k in range(int(6 + 3 * s)):
        x = int((rng.random() - 0.5) * Lb * 1.2)
        yb = H * (1 - (abs(x) / Lb) ** 3) - 3 * s - 1
        if yb < 8:
            continue
        z = int((rng.random() - 0.5) * 4 * s)
        hh = int(3 + rng.random() * 3 * s)
        b = 2 + int(rng.random() * s)
        for y in range(int(yb) - hh, int(yb) + 1):
            for dx in range(-b, b + 1):
                for dz in range(-b, b + 1):
                    if max(abs(dx), abs(dz)) == b:
                        fen = (y + dx + dz) % 3 == 0
                        w.setze(x + dx, y, z + dz, w.b("glass_pane") if fen else wand(x + dx, y, z + dz))
        for k2 in range(b + 2):
            for dx in range(-b + k2 - 1, b - k2 + 2):
                for dz in range(-b + k2 - 1, b - k2 + 2):
                    w.setze(x + dx, int(yb) - hh - 1 - k2, z + dz, treppe(w, "dark_oak", "south", "top") if dz == -b + k2 - 1
                            else w.b("dark_oak_planks"), False)
        w.setze(x, int(yb) - hh - b - 3, z, w.b("lantern", hanging=True, waterlogged=False), False)
    for k in range(int(4 * s)):
        x = int((rng.random() - 0.5) * Lb)
        yb = int(H * (1 - (abs(x) / Lb) ** 3) - 3 * s)
        for y in range(yb - int(4 + rng.random() * 6), yb):
            w.setze(x, y, 2, w.b("chain", axis="y", waterlogged=False), False)
    _ = zellen
    return w


def treppenberg(seed, g=2):
    """Treppenberg: ein ganzer Berg, in den eine einzige, endlos scheinende Prunktreppe gemeißelt ist, gesäumt von
    Statuen und kleinen Schreinen auf jeder Terrasse, oben ein Tempel mit goldenem Dach."""
    w = _neu(seed)
    s = W[g]
    R = int(16 * s + 8)
    rn = Rauschen(w, 5)
    H = int(16 * s + 10)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 2 * rn(x, 0, z):
                continue
            h = int(H * max(0, 1 - d / R) ** 0.9 + rn(x, 3, z) * 2)
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h and h < H * 0.6 else
                        w.b("stone") if (x + y) % 3 else w.b("andesite"))
    sa = sandst(w)
    for z in range(1, R):
        h = int(H * max(0, 1 - abs(z) / R) ** 0.9) + 1
        for x in range(-2 - int(s), 3 + int(s)):
            w.setze(x, h, z, treppe(w, "sandstone", "north") if z % 6 else sa(x, h, z))
            for y in range(h + 1, h + 5):
                w.bloecke.pop((x, y, z), None)
        if z % 6 == 0:
            for sx in (-1, 1):
                x = sx * (4 + int(s))
                for y in range(h, h + 3):
                    w.setze(x, y, z, sa(x, y, z) if y < h + 2 else w.b("lantern", hanging=False, waterlogged=False))
    top = hoehe(w, 0, 0, H + 6)
    A = int(3 * s + 3)
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            w.setze(x, top + 1, z, sa(x, top + 1, z))
            if max(abs(x), abs(z)) == A and (x + z) % 2 == 0:
                for y in range(top + 2, top + int(4 * s + 4)):
                    w.setze(x, y, z, w.b("cut_sandstone"))
    kegeldach(w, 0, 0, top + int(4 * s + 4), A, Dachmat(w, ["mcw:yellow_terracotta", "smooth_sandstone"]),
              form="glocke", eckig=True, spitze="gold_block")
    return w


def elefantenpalast(seed, g=2):
    """Elefantenpalast: eine gewaltige Steinstatue eines stehenden Elefanten mit erhobenem Rüssel trägt auf ihrem
    Rücken einen kleinen Palast mit Zwiebelkuppeln und Bogenfenstern; Treppen führen an den Beinen hinauf."""
    w = _neu(seed)
    s = W[g]
    u = 1.1 * s + 0.6
    R = int(10 * u + 6)
    wiese(w, R, 0.05, art="kies")
    gr = M(w, [("stone", 2), ("andesite", 2), ("polished_andesite", 1)])
    Sk = Skulptur(w, u)
    Sk.mat("g", lambda x, y, z, *a: gr(x, y, z))
    Sk.mat("e", w.b("white_concrete"))
    Sk.mat("d", w.b("red_wool"))
    Sk.plus(ell(0, 9, 0, 7, 4.2, 4.0), "g")
    for sx in (-4.2, 4.2):
        for sz in (-2.4, 2.4):
            Sk.plus(kap((sx, 7, sz), (sx, 0, sz), 1.5, 1.4), "g")
    Sk.plus(ell(7.5, 10.5, 0, 2.8, 2.8, 2.6), "g")
    Sk.plus(kap((9.5, 10, 0), (11, 6, 0), 1.0, 0.8), "g")
    Sk.plus(kap((11, 6, 0), (12.5, 8.5, 0), 0.8, 0.5), "g")
    for sz in (-1, 1):
        Sk.plus(ell(6.8, 11, sz * 3.2, 0.5, 2.6, 2.0), "g")
        Sk.plus(kap((9.6, 9, sz * 1.0), (11.5, 8.8, sz * 1.8), 0.35, 0.12), "e")
    Sk.plus(kap((-7, 10, 0), (-8, 5, 0), 0.4, 0.2), "g")
    Sk.plus(ell(0, 13.2, 0, 6, 0.6, 4.2), "d")
    Sk.rendern((-9, 0, -6), (14, 15, 6), versatz=(0.5, 0, 0.5), dreh=dreh_y(0.3))
    top = int(13.8 * u)
    A = int(3 * u)
    for x in range(-A, A + 1):
        for z in range(-int(A * 0.7), int(A * 0.7) + 1):
            for y in range(top, top + int(3 * u)):
                if max(abs(x) / A, abs(z) / (A * 0.7)) >= 0.95:
                    fen = y == top + 1 and (x + z) % 2 == 0
                    w.setze(x, y, z, w.b("glass_pane") if fen else w.b("smooth_sandstone"))
    for dx, dz, r in ((0, 0, A * 0.6), (-A, 0, A * 0.3), (A, 0, A * 0.3)):
        kuppel(w, lambda x, y, z, t: w.b("gold_block") if (x + z) % 3 else w.b("red_terracotta"), dx, dz,
               top + int(3 * u), max(1.5, r), form="zwiebel", spitze="gold_block")
    return w


def haendebruecke(seed, g=2):
    """Händebrücke: zwei riesige steinerne Hände ragen aus einem Fluss und halten gemeinsam eine schmale Bogen-
    brücke empor, auf der ein Pfad mit Laternen verläuft; Moos und Ranken an den Fingern."""
    w = _neu(seed)
    s = W[g]
    u = 1.0 * s + 0.5
    R = int(12 * u + 6)
    zellen = wiese(w, R, 0.1)
    for z in range(-R - 2, R + 3):
        for x in range(-int(5 * u) - 2, int(5 * u) + 3):
            if (x, z) in zellen and abs(x - math.sin(z / 5) * 2) < 4 * u:
                w.setze(x, 0, z, w.b("water", level=0))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
    st = M(w, [("stone", 3), ("andesite", 1), ("mossy_cobblestone", 1)])
    for sz in (-1, 1):
        Sk = Skulptur(w, u)
        Sk.mat("h", lambda x, y, z, *a: st(x, y, z))
        Sk.plus(kap((0, -2, 0), (0, 6, 0), 1.8, 1.6), "h")
        Sk.plus(ell(0, 7.5, 0, 2.4, 1.8, 1.4), "h")
        for i, dx in enumerate((-1.6, -0.5, 0.6, 1.7)):
            Sk.plus(kap((dx, 8.6, 0), (dx * 1.2, 11.5 + (i % 2) * 0.6, 0.4), 0.45, 0.4), "h")
        Sk.plus(kap((2.2, 7.2, 0), (3.4, 9.0, 0.3), 0.45), "h")
        Sk.rendern((-4, -3, -3), (5, 13, 3), versatz=(0.5, 0, sz * 5 * u + 0.5), dreh=dreh_y(math.pi / 2 if sz > 0
                                                                                              else -math.pi / 2))
    yb = int(12 * u)
    L = int(9 * u + 4)
    for z in range(-L, L + 1):
        y = yb + round(1.5 * u * math.cos(math.pi * z / (2 * L)))
        for x in (-1, 0, 1):
            w.setze(x, y, z, w.b("stone_bricks") if x == 0 else w.b("stone_brick_slab", type="bottom",
                                                                          waterlogged=False))
        if z % 4 == 0:
            for x in (-2, 2):
                w.setze(x, y + 1, z, w.b("stone_brick_wall"))
                w.setze(x, y + 2, z, w.b("lantern", hanging=False, waterlogged=False))
    for z in (-L - 1, L + 1):
        for k in range(yb):
            w.setze(0, yb - k, z + (k if z > 0 else -k), treppe(w, "stone_brick", "south" if z < 0 else "north"))
    return w


def kaskadenpalast(seed, g=2):
    """Kaskadenpalast: ein weißer Palast in mehreren Terrassen über einem Berghang, über dessen Stufen breite Wasser-
    fälle in Becken stürzen; Arkaden, Pavillons und Brücken überspannen die Kaskaden."""
    w = _neu(seed)
    s = W[g]
    R = int(16 * s + 8)
    wiese(w, R, 0.1)
    mm = marmor(w)
    n = 4
    B = int(R * 0.7)
    for k in range(n):
        z0 = -int(R * 0.7) + k * int(R * 1.4 / n)
        h = (n - k) * int(3 * s + 2)
        T = int(R * 1.4 / n)
        for x in range(-B, B + 1):
            for z in range(z0, z0 + T):
                for y in range(1, h + 1):
                    w.setze(x, y, z, mm(x, y, z))
                if abs(x) < 3 + s:
                    w.setze(x, h, z, w.b("water", level=0))
                    if z == z0 + T - 1:
                        for y in range(1, h):
                            w.setze(x, y, z + 1, w.b("water", level=0))
        for x in range(-B, B + 1, 4):
            if abs(x) > 5 + s:
                saeule(w, x, h + 1, z0 + T - 1, int(3 + s))
        for x in range(-B, B + 1):
            if abs(x) > 4 + s:
                w.setze(x, h + int(4 + s) + 1, z0 + T - 1, w.b("smooth_quartz_slab", type="bottom",
                                                               waterlogged=False))
        for x in range(-int(4 + s), int(5 + s)):
            w.setze(x, h + 2, z0 + T // 2, w.b("smooth_quartz"))
    top = n * int(3 * s + 2)
    z0 = -int(R * 0.7)
    for sx in (-1, 1):
        x = sx * int(B * 0.6)
        for y in range(top + 1, top + int(5 * s + 4)):
            for dx, dz in kreisrand(1.5 + 0.5 * s, x, z0 + 3):
                w.setze(dx, y, dz, w.b("smooth_quartz"))
        kuppel(w, w.b("gold_block"), x, z0 + 3, top + int(5 * s + 4), 2 + 0.5 * s, form="zwiebel", spitze="gold_block")
    return w


def lichtdom(seed, g=2):
    """Lichtdom: eine gewaltige Kuppelhalle, deren Kuppel aus Tausenden farbigen Glassegmenten besteht, so dass der
    Innenraum in allen Farben leuchtet; Rippen aus Gold, ein Ring aus Säulen und eine Laterne obenauf."""
    w = _neu(seed)
    s = W[g]
    R = int(15 * s + 8)
    wiese(w, R, 0.05, art="kies")
    rk = 10 * s + 6
    mm = marmor(w)
    for x in range(-int(rk) - 3, int(rk) + 4):
        for z in range(-int(rk) - 3, int(rk) + 4):
            if math.hypot(x, z) <= rk + 3:
                w.setze(x, 1, z, mm(x, 1, z))
    H = int(5 * s + 4)
    n = int(16 + 8 * s)
    for i in range(n):
        a = i / n * 2 * math.pi
        saeule(w, round(math.cos(a) * rk), 2, round(math.sin(a) * rk), H)
    for x, z in kreisrand(rk):
        w.setze(x, H + 3, z, w.b("gold_block"))
    farben = ["red", "orange", "yellow", "lime", "light_blue", "blue", "purple", "magenta"]
    for x in range(-int(rk) - 1, int(rk) + 2):
        for z in range(-int(rk) - 1, int(rk) + 2):
            for y in range(0, int(rk) + 2):
                d = math.sqrt(x * x + y * y + z * z)
                if rk - 1.0 < d <= rk:
                    ang = math.atan2(z, x)
                    rippe = abs((ang * 8 / math.pi) % 1 - 0.5) > 0.44
                    seg = int((ang + math.pi) / (2 * math.pi) * 8) % 8
                    w.setze(x, H + 4 + y, z, w.b("gold_block") if rippe else
                            w.b(f"{farben[(seg + y // 3) % 8]}_stained_glass"))
    top = H + 4 + int(rk)
    for y in range(top, top + int(3 * s + 2)):
        for x, z in kreisrand(1.5):
            w.setze(x, y, z, w.b("gold_block") if y % 2 else w.b("glass"))
    w.setze(0, top + int(3 * s + 2), 0, w.b("sea_lantern"))
    return w


def doppelhelix(seed, g=2):
    """Doppelhelix-Turm: zwei schlanke Türme aus weißem und dunklem Stein winden sich umeinander in den Himmel,
    verbunden durch gläserne Stege wie Sprossen einer Leiter, an der Spitze eine leuchtende Kugel."""
    w = _neu(seed)
    s = W[g]
    R = int(12 * s + 6)
    wiese(w, R, 0.05, art="kies")
    H = int(30 * s + 16)
    rh = 3.5 * s + 2.5
    r = 1.6 * s + 1.2
    for k, mat in enumerate(("smooth_quartz", "polished_deepslate")):
        pts = [(math.cos(t * 4 * math.pi + k * math.pi) * rh, 1 + t * H, math.sin(t * 4 * math.pi + k * math.pi) * rh, t)
               for t in np.linspace(0, 1, 160)]
        rohr(w, pts, r, r * 0.7, mat=w.b(mat), rauh=0.02)
    for i in range(int(H / 3)):
        t = i * 3 / H
        a = t * 4 * math.pi
        x0, z0 = math.cos(a) * rh, math.sin(a) * rh
        y = round(1 + t * H)
        for q in np.linspace(-1, 1, int(rh * 3)):
            w.setze(round(x0 * q), y, round(z0 * q), w.b("light_blue_stained_glass"), False)
    kugel(w, 0, H + 3, 0, 2 + s, w.b("sea_lantern"))
    for x in range(-int(rh) - 3, int(rh) + 4):
        for z in range(-int(rh) - 3, int(rh) + 4):
            if math.hypot(x, z) <= rh + 3:
                w.setze(x, 0, z, w.b("polished_andesite") if (x + z) % 2 else w.b("smooth_quartz"))
    return w


def sanduhrturm(seed, g=2):
    """Sanduhrturm: eine turmhohe Sanduhr aus Glas in einem bronzenen Gestell mit vier gedrehten Säulen; oben ein
    Berg aus goldenem Sand, ein feiner Strahl rieselt in den unteren Kolben, auf einem Sternensockel."""
    w = _neu(seed)
    s = W[g]
    R = int(11 * s + 6)
    wiese(w, R, 0.05, art="kies")
    H = int(22 * s + 12)
    r = 5 * s + 3
    for y in range(3, H):
        t = (y - 3) / (H - 3)
        rr = max(1.0, r * abs(2 * t - 1) ** 0.7)
        for x, z in kreisrand(rr):
            w.setze(x, y, z, w.b("glass"))
        if t < 0.5:
            fill = 0.6
            if t < 0.5 * fill:
                for x in range(-int(rr) + 1, int(rr)):
                    for z in range(-int(rr) + 1, int(rr)):
                        if math.hypot(x, z) < rr - 0.8:
                            w.setze(x, y, z, w.b("sand"), False)
        else:
            if t > 0.5 + 0.4 * (1 - 0.6):
                pass
            if t > 0.88:
                for x in range(-int(rr) + 1, int(rr)):
                    for z in range(-int(rr) + 1, int(rr)):
                        if math.hypot(x, z) < rr - 0.8:
                            w.setze(x, H - y + 3, z, w.b("sand"), False)
    for y in range(int(H * 0.3), int(H * 0.7)):
        w.setze(0, y, 0, w.b("sand"), False)
    for k in range(3):
        a = int(r) + 3 - k
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                w.setze(x, k, z, w.b("waxed_cut_copper"))
                w.setze(x, H + k, z, w.b("waxed_cut_copper"))
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        pts = [(math.cos(a + t * 2) * (r + 2), 3 + t * (H - 3), math.sin(a + t * 2) * (r + 2), t)
               for t in np.linspace(0, 1, 60)]
        rohr(w, pts, 0.7 * s + 0.4, 0.7 * s + 0.4, mat=w.b("waxed_cut_copper"), rauh=0.02)
    return w


def umgekehrte_pyramide(seed, g=2):
    """Umgekehrte Pyramide: über einer Stufenpyramide aus Sandstein schwebt eine zweite, auf der Spitze stehende
    Pyramide aus dunklem Stein, beide berühren sich nur mit einem leuchtenden Kristall in der Mitte."""
    w = _neu(seed)
    s = W[g]
    R = int(14 * s + 8)
    wiese(w, R, 0.05, art="kies")
    A = int(9 * s + 6)
    sa = sandst(w)
    dk = M(w, [("polished_deepslate", 2), ("deepslate_tiles", 2), ("polished_blackstone", 1)])
    for k in range(A + 1):
        a = A - k
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                if max(abs(x), abs(z)) >= a - 1 or k % 3 == 0:
                    w.setze(x, 1 + k, z, sa(x, 1 + k, z))
    yt = A + 2
    kugel(w, 0, yt + 1.5, 0, 1.5 + 0.5 * s, w.b("amethyst_block"))
    w.setze(0, yt + 1, 0, w.b("sea_lantern"))
    for k in range(A + 1):
        a = k
        y = yt + 3 + k
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                if max(abs(x), abs(z)) >= a - 1 or k == A:
                    w.setze(x, y, z, dk(x, y, z))
    for k in range(4):
        a = k * math.pi / 2
        for t in range(int(A * 0.7)):
            w.setze(round(math.cos(a) * (A + 2)), 2 + t * 2, round(math.sin(a) * (A + 2)),
                    w.b("end_rod", facing="up") if t % 2 else w.b("purple_stained_glass"))
    return w


def schalenstadt(seed, g=2):
    """Schalenstadt: eine kleine Stadt mit Türmen und Gassen, erbaut im Inneren einer riesigen, aufrecht stehenden
    Spiralmuschel aus Perlmutt, deren Öffnung zum Meer zeigt; Stege und Boote davor."""
    w = _neu(seed)
    s = W[g]
    R = int(15 * s + 8)
    rn = Rauschen(w, 5)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) <= R + 2 * rn(x, 0, z):
                w.setze(x, -1, z, w.b("sand"))
                w.setze(x, 0, z, w.b("water", level=0) if z > R * 0.3 else w.b("sand"))
    rs = 9 * s + 5
    H = int(rs * 2.2)
    perl = M(w, [("calcite", 2), ("white_terracotta", 2), ("pink_terracotta", 1), ("smooth_quartz", 1)])
    for y in range(0, H):
        t = y / H
        rr = rs * (1 - t) ** 0.8 + 1
        cx = round(math.sin(t * 4 * math.pi) * rs * 0.15 * (1 - t))
        for x, z in kreisrand(rr, cx, -int(R * 0.2)):
            if not (z > -int(R * 0.2) + rr * 0.3 and y < H * 0.35 and abs(x - cx) < rr * 0.6):
                w.setze(x, y + 1, z, perl(x, y, z) if (y + round(math.atan2(z, x) * 3)) % 4 else
                        w.b("pink_terracotta"))
    for k in range(int(3 + 2 * s)):
        x = int((k - 1.5) * 3)
        z = -int(R * 0.2) - 2 + (k % 2) * 3
        hh = int(4 + k % 3 * 2 * s)
        for y in range(1, hh):
            for dx, dz in ((0, 0), (1, 0), (0, 1), (1, 1)):
                w.setze(x + dx, y, z + dz, w.b("white_terracotta") if y % 3 else w.b("light_blue_terracotta"))
        w.setze(x, hh, z, w.b("prismarine_bricks"))
    for z in range(-int(R * 0.2) + int(rs * 0.5), R):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("birch_planks"))
    return w


def kompassplatz(seed, g=2):
    """Kompassplatz: ein riesiger, runder Platz, in dessen Pflaster eine Windrose aus farbigem Stein eingelegt ist,
    die Himmelsrichtungen durch vier hohe Obelisken mit Tierfiguren markiert, in der Mitte ein Globus."""
    w = _neu(seed)
    s = W[g]
    R = int(15 * s + 8)
    wiese(w, R, 0.05, art="kies")
    rp = R * 0.85
    for x in range(-int(rp), int(rp) + 1):
        for z in range(-int(rp), int(rp) + 1):
            d = math.hypot(x, z)
            if d > rp:
                continue
            ang = math.atan2(z, x)
            spitze = min(abs(((ang + math.pi / 4) % (math.pi / 2)) - math.pi / 4) for _ in (0,))
            haupt = d < rp * 0.85 * (1 - spitze / (math.pi / 4)) ** 1.5
            neben_ang = ((ang) % (math.pi / 2)) - math.pi / 4
            neben = d < rp * 0.55 * (1 - abs(neben_ang) / (math.pi / 4)) ** 1.5
            if haupt:
                f = "red_terracotta" if (ang + math.pi / 4) % (math.pi / 2) < math.pi / 4 else "white_terracotta"
            elif neben:
                f = "blue_terracotta" if ang % (math.pi / 2) < math.pi / 4 else "light_blue_terracotta"
            elif abs(d - rp * 0.9) < 0.8:
                f = "gold_block"
            else:
                f = "polished_andesite" if (x + z) % 2 else "smooth_stone"
            w.setze(x, 0, z, w.b(f))
    for i, tierfarbe in enumerate(("white_concrete", "orange_terracotta", "gray_concrete", "brown_terracotta")):
        a = i * math.pi / 2
        x, z = round(math.cos(a) * rp * 0.95), round(math.sin(a) * rp * 0.95)
        H = int(8 * s + 6)
        for y in range(1, H):
            r = 1.0 + 0.5 * s * (1 - y / H)
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if max(abs(dx), abs(dz)) <= r:
                        w.setze(x + dx, y, z + dz, w.b("smooth_quartz"))
        w.setze(x, H, z, w.b("gold_block"))
        w.setze(x, H + 1, z, w.b(tierfarbe))
    kugel(w, 0, 3 + 2 * s, 0, 2 + s, lambda x, y, z: w.b("blue_concrete") if (x * 3 + y + z * 2) % 5 else
          w.b("green_concrete"))
    for y in range(1, 3):
        w.setze(0, y, 0, w.b("gold_block"))
    return w


def regenbogen_aquaedukt(seed, g=2):
    """Regenbogen-Aquädukt: ein dreistöckiger Bogen-Aquädukt aus weißem Stein, dessen Bogenfelder mit Glas in den
    Regenbogenfarben gefüllt sind, oben eine Wasserrinne, die als Wasserfall in einen See mündet."""
    w = _neu(seed)
    s = W[g]
    R = int(16 * s + 8)
    zellen = wiese(w, R, 0.1)
    mm = marmor(w)
    L = int(R * 0.9)
    farben = ["red", "orange", "yellow", "lime", "light_blue", "blue", "purple"]
    ebenen = [(0, int(6 * s + 4), int(3 * s + 2)), (int(6 * s + 4), int(4 * s + 3), int(2 * s + 2)),
              (int(10 * s + 7), int(3 * s + 2), int(1.5 * s + 1))]
    for e, (y0, h, sp) in enumerate(ebenen):
        for x in range(-L, L + 1):
            pos = (x + L) % (2 * sp + 2)
            for y in range(y0 + 1, y0 + h + 1):
                im = 0 < pos <= 2 * sp + 1 and ((pos - sp - 0.5) / (sp + 0.5)) ** 2 + ((y - y0 - 1) / (h - 1.5)) ** 2 < 1
                for z in (-1, 0, 1):
                    if im:
                        if z == 0:
                            w.setze(x, y, z, w.b(f"{farben[((x + L) // (2 * sp + 2) + e) % 7]}_stained_glass"))
                    else:
                        w.setze(x, y, z, mm(x, y, z))
    top = ebenen[-1][0] + ebenen[-1][1] + 1
    for x in range(-L, L + 1):
        w.setze(x, top, 0, w.b("water", level=0))
        w.setze(x, top, -1, mm(x, top, -1))
        w.setze(x, top, 1, mm(x, top, 1))
    for y in range(1, top + 1):
        w.setze(L + 1, y, 0, w.b("water", level=0))
    for x in range(L - 2, L + 6):
        for z in range(-4, 5):
            if math.hypot(x - L - 1, z) < 4.5:
                w.setze(x, 0, z, w.b("water", level=0))
    _ = zellen
    return w


def titanenschwerter(seed, g=2):
    """Titanenschwerter: auf einem kahlen Schlachtfeld-Hügel stecken drei gewaltige Schwerter von Riesen schräg im
    Boden, ihre Klingen verwittert, Parierstangen mit Edelsteinen, Ranken an den Griffen."""
    w = _neu(seed)
    s = W[g]
    R = int(14 * s + 8)
    zellen = wiese(w, R, 0.6, art="kies")
    for k, (dx, dz, neig, rot) in enumerate(((0, 0, 0.15, 0.2), (-R * 0.45, R * 0.2, -0.3, 1.4),
                                            (R * 0.4, -R * 0.25, 0.35, 2.5))):
        u = (1.2 if k == 0 else 0.8) * s + 0.5
        Sk = Skulptur(w, u)
        Sk.mat("k", lambda x, y, z, *a: w.b("iron_block") if (x + y) % 5 else w.b("light_gray_concrete"))
        Sk.mat("p", w.b("gold_block"))
        Sk.mat("g", w.b("brown_terracotta"))
        Sk.mat("e", w.b(["emerald_block", "redstone_block", "lapis_block"][k]))
        Sk.plus(lambda X, Y, Z: (np.abs(X) <= 1.2 * (1 - np.clip((-Y) / 6, 0, 1)) + 0.1) & (np.abs(Z) <= 0.35) &
                (Y >= -6) & (Y <= 14), "k")
        Sk.plus(kasten(-3.5, 14, -0.6, 3.5, 15, 0.6), "p")
        Sk.plus(ell(0, 14.5, 0, 0.6, 0.6, 0.8), "e")
        Sk.plus(kap((0, 15, 0), (0, 19, 0), 0.5), "g")
        Sk.plus(ell(0, 19.6, 0, 0.8, 0.8, 0.8), "p")
        Sk.rendern((-5, -7, -2), (5, 21, 2), versatz=(dx + 0.5, 0, dz + 0.5), dreh=dreh_y(rot) @ dreh_z(neig))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 2 and rng.random() < 0.02 and w.frei(x + 1, y, z):
            for kk in range(1, 4):
                if w.frei(x + 1, y - kk, z):
                    w.setze(x + 1, y - kk, z, w.b("vine", west=True, east=False, north=False, south=False, up=False))
    _ = zellen
    return w


def jahreszeitenrad(seed, g=2):
    """Rad der Jahreszeiten: ein riesiges, senkrecht stehendes Steinrad, dessen vier Viertel Frühling (Blüten),
    Sommer (Grün und Sonne), Herbst (rotes Laub) und Winter (Schnee und Eis) zeigen, auf einem Sockel mit Treppen."""
    w = _neu(seed)
    s = W[g]
    R = int(13 * s + 8)
    wiese(w, R, 0.05)
    Rr = 9 * s + 6
    yc = int(Rr) + 4
    mm = marmor(w)
    for x in range(-int(Rr) - 2, int(Rr) + 3):
        for y in range(-int(Rr) - 2, int(Rr) + 3):
            d = math.hypot(x, y)
            if d > Rr + 1:
                continue
            ang = math.atan2(y, x)
            q = int((ang + math.pi) / (math.pi / 2)) % 4
            if d > Rr - 0.8 or abs(x) <= 0 or abs(y) <= 0 or d < 1.5:
                b = mm(x, y, 0) if d >= 1.5 else w.b("gold_block")
            else:
                if q == 0:
                    b = w.b("flowering_azalea_leaves", persistent=True, distance=1, waterlogged=False) if (x + y) % 3 \
                        else w.b("pink_wool")
                elif q == 1:
                    b = w.b("snow_block") if (x + y) % 3 else w.b("packed_ice")
                elif q == 2:
                    b = w.b("red_terracotta") if (x + y) % 3 else w.b("orange_terracotta")
                else:
                    b = w.b("oak_leaves", persistent=True, distance=1, waterlogged=False) if (x + y) % 4 else \
                        w.b("yellow_concrete")
            for z in (-1, 0, 1):
                w.setze(x, yc + y, z, b)
    for k in range(4):
        a = int(Rr * 0.6) - k
        for x in range(-a, a + 1):
            for z in range(-3 - k, 4 + k):
                if yc - int(Rr) - 1 + k > 0:
                    pass
        for x in range(-a, a + 1):
            for z in range(-4, 5):
                w.setze(x, 1 + k, z, mm(x, 1 + k, z))
    return w


def wasserfallfestung(seed, g=2):
    """Wasserfallfestung: eine Burg, die halb in eine Felswand hinter einem breiten Wasserfall gebaut ist – Türme ragen
    seitlich aus dem Fels, eine Brücke führt durch den Wasservorhang zum Tor."""
    w = _neu(seed)
    s = W[g]
    R = int(15 * s + 8)
    rn = Rauschen(w, 4)
    H = int(16 * s + 10)
    st = M(w, [("stone", 3), ("andesite", 1), ("mossy_cobblestone", 1)])
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            if z < -R * 0.15:
                for y in range(0, H + int(rn(x, 3, z) * 3)):
                    w.setze(x, y, z, st(x, y, z))
            else:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel"))
    zf = -int(R * 0.15)
    Bw = int(5 * s + 4)
    for x in range(-Bw, Bw + 1):
        for y in range(1, H):
            w.setze(x, y, zf + 2, w.b("water", level=0))
    bs = M(w, [("stone_bricks", 3), ("cracked_stone_bricks", 1)])
    for x in range(-Bw + 1, Bw):
        for y in range(1, int(H * 0.6)):
            for z in range(zf - 1, zf + 1):
                w.setze(x, y, z, bs(x, y, z) if not (abs(x) < 2 and y < 4 and z == zf) else w.b("air"))
    for sx in (-1, 1):
        tx = sx * (Bw + 2)
        for y in range(1, H + int(4 * s)):
            for x, z in kreisrand(2 + s, tx, zf + 1):
                w.setze(x, y, z, bs(x, y, z))
        kegeldach(w, tx, zf + 1, H + int(4 * s), int(2 + s), Dachmat(w, ["deepslate_tile"]), form="kegel",
                  spitze="gold_block")
    for z in range(zf + 1, int(R * 0.6)):
        for x in (-1, 0, 1):
            w.setze(x, 2, z, w.b("stone_bricks"))
        if z % 3 == 0:
            for x in (-1, 1):
                for y in range(0, 2):
                    w.setze(x, y, z, w.b("stone_bricks"))
    return w


def kristallorgel(seed, g=2):
    """Kristallorgel: eine riesige Orgel aus Hunderten von Kristallpfeifen unterschiedlicher Höhe in Amethyst, Eis
    und Quarz, in einen Fels gebaut, mit einem Spieltisch auf einer Bühne und Klangschalen davor."""
    w = _neu(seed)
    s = W[g]
    R = int(13 * s + 6)
    wiese(w, R, 0.05, art="kies")
    n = int(14 + 8 * s)
    H = int(16 * s + 10)
    for i in range(n):
        t = i / (n - 1)
        x = round((t - 0.5) * R * 1.4)
        h = int(H * (0.35 + 0.65 * math.sin(math.pi * t) ** 0.8))
        mat = ["amethyst_block", "packed_ice", "smooth_quartz", "purple_stained_glass"][i % 4]
        r = 0.6 + 0.6 * s * math.sin(math.pi * t)
        for y in range(2, 2 + h):
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    if dx * dx + dz * dz <= r * r + 0.3:
                        w.setze(x + dx, y, -int(R * 0.3) + dz, w.b(mat))
        w.setze(x, 2 + h, -int(R * 0.3), w.b("amethyst_cluster", facing="up", waterlogged=False))
    for x in range(-int(R * 0.75), int(R * 0.75) + 1):
        for z in range(-int(R * 0.3) - 2, -int(R * 0.3) + 4):
            w.setze(x, 1, z, w.b("polished_deepslate"))
    for x in range(-3, 4):
        w.setze(x, 2, -int(R * 0.3) + 3, w.b("dark_oak_slab", type="top", waterlogged=False))
    w.setze(0, 2, -int(R * 0.3) + 5, w.b("dark_oak_stairs", facing="south", half="bottom", shape="straight",
                                         waterlogged=False))
    for i in range(5):
        x = -int(R * 0.4) + i * int(R * 0.2)
        w.setze(x, 1, int(R * 0.35), w.b("cauldron"))
    return w


def arche(seed, g=2):
    """Arche auf dem Berg: ein gewaltiges hölzernes Schiff mit Hausaufbau liegt gestrandet auf einem grasigen Bergrücken,
    eine Rampe führt hinab, Tiere-Figuren in Paaren auf der Wiese, ein Regenbogen darüber."""
    w = _neu(seed)
    s = W[g]
    R = int(16 * s + 8)
    rn = Rauschen(w, 5)
    H = int(6 * s + 4)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 2 * rn(x, 0, z):
                continue
            h = int(H * max(0, 1 - (d / R) ** 2) + rn(x, 3, z) * 2)
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else w.b("stone") if y < h - 2 else
                        w.b("dirt"))
    L = int(12 * s + 8)
    B = 3.5 * s + 2.5
    D = int(3 * s + 3)
    y0 = H + 1
    for i in range(-L, L + 1):
        t = i / (L + 0.5)
        bw = B * math.sqrt(max(0, 1 - t ** 6))
        for q in range(-int(bw) - 1, int(bw) + 2):
            if abs(q) <= bw:
                for y in range(y0, y0 + D):
                    rand = abs(q) > bw - 1 or y == y0
                    if rand:
                        w.setze(i, y, q, w.b("spruce_planks") if (y + i) % 4 else w.b("stripped_spruce_log", axis="x"))
                    else:
                        w.bloecke.pop((i, y, q), None)
                w.setze(i, y0 + D, q, w.b("spruce_planks"))
    hb = int(L * 0.6)
    for x in range(-hb, hb + 1):
        for z in range(-int(B * 0.6), int(B * 0.6) + 1):
            for y in range(y0 + D + 1, y0 + D + int(3 * s + 3)):
                if abs(x) == hb or abs(z) == int(B * 0.6):
                    fen = y == y0 + D + 2 and x % 3 == 0
                    w.setze(x, y, z, w.b("glass_pane") if fen else w.b("spruce_planks"))
    satteldach(w, -hb, -int(B * 0.6), hb, int(B * 0.6), y0 + D + int(3 * s + 3), Dachmat(w, ["spruce", "dark_oak"]),
               first_x=True, ue=1, giebel=M(w, [("spruce_planks", 1)]), traufe="spruce")
    for k in range(int(D + H)):
        w.setze(0, y0 + D - k // 2, int(B) + 2 + k, w.b("spruce_slab", type="bottom", waterlogged=False))
    farben = ["white_wool", "brown_wool", "gray_wool", "orange_terracotta"]
    rng = w.rng
    for k in range(4 + 2 * g):
        x, z = int((rng.random() - 0.5) * R * 1.2), int(B + 5 + rng.random() * R * 0.4)
        if math.hypot(x, z) > R - 2:
            continue
        f = w.b(farben[k // 2 % 4])
        teile = [(ell(0, 1.6, 0, 1.2, 0.8, 0.7), f), (ell(1.2, 2.2, 0, 0.5, 0.5, 0.45), f)] + \
                [(kap((sx, 1.2, sz), (sx, 0, sz), 0.22), f) for sx in (-0.7, 0.7) for sz in (-0.35, 0.35)]
        figur(w, 0.6 * s + 0.4, teile, (-2, -1, -2), (2, 3, 2), pos=(x, hoehe(w, x, z, H + 4) + 1, z),
              winkel=rng.random() * 6.28)
    farb = ["red", "orange", "yellow", "lime", "light_blue", "blue", "purple"]
    Rb = R * 0.9
    for k in range(int(Rb * 5)):
        a = math.pi * k / (Rb * 5)
        for i, f in enumerate(farb):
            r = Rb - i
            w.setze(round(math.cos(a) * r), round(H + 6 + math.sin(a) * r * 0.8), -int(R * 0.5),
                    w.b(f"{f}_stained_glass"), False)
    return w


WELTWUNDER3 = {
    "gezeitenfontaene": ("Gezeitenfontäne", gezeitenfontaene),
    "wurzelkathedrale": ("Wurzelkathedrale", wurzelkathedrale),
    "saeulenwald": ("Säulenwald der Riesen", saeulenwald),
    "haengende_stadt": ("Hängende Stadt", haengende_stadt),
    "treppenberg": ("Treppenberg", treppenberg),
    "elefantenpalast": ("Elefantenpalast", elefantenpalast),
    "haendebruecke": ("Händebrücke", haendebruecke),
    "kaskadenpalast": ("Kaskadenpalast", kaskadenpalast),
    "lichtdom": ("Lichtdom", lichtdom),
    "doppelhelix": ("Doppelhelix-Turm", doppelhelix),
    "sanduhrturm": ("Sanduhrturm", sanduhrturm),
    "umgekehrte_pyramide": ("Umgekehrte Pyramide", umgekehrte_pyramide),
    "schalenstadt": ("Schalenstadt", schalenstadt),
    "kompassplatz": ("Kompassplatz", kompassplatz),
    "regenbogen_aquaedukt": ("Regenbogen-Aquädukt", regenbogen_aquaedukt),
    "titanenschwerter": ("Titanenschwerter", titanenschwerter),
    "jahreszeitenrad": ("Rad der Jahreszeiten", jahreszeitenrad),
    "wasserfallfestung": ("Wasserfallfestung", wasserfallfestung),
    "kristallorgel": ("Kristallorgel", kristallorgel),
    "arche": ("Arche auf dem Berg", arche),
}

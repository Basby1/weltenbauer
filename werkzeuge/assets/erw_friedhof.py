"""Friedhof & Spuk II – zwanzig weitere schaurige Orte: Laternenfriedhof, Geisterkutsche, Spukmühle, Kopfloser
Reiter, Vogelscheuchenfeld, Nebelbrücke, Verfallenes Herrenhaus, Hangfriedhof, Glockenstuhl, Sargmacher-Werkstatt,
Grabpyramide, Weinende Statuen, Kolumbarium, Grabhecken-Labyrinth, Seelenlaternen-Weide, Verfluchter Brunnen,
Gespenstertafel, Fledermausturm, Verlassenes Nebeldorf und Steinerne Trauerweide."""

from __future__ import annotations

import math

import numpy as np

from erw_basis import M, S, figur, haus, hoehe, wiese
from feinbau import Dachmat, efeu, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, laubball, rohr
from lib import Rauschen, einfuegen
from skulptur import ell, kap, kasten, kegel, kreisrand

import wald2


def spukboden(w, R, huegel=0.4, dichte=1.0):
    zellen = wiese(w, R, huegel, art="wald", blumen=0.0)
    rng = w.rng
    for (x, z), h in zellen.items():
        q = rng.random() / dichte
        if q < 0.03:
            w.setze(x, h + 1, z, w.b("dead_bush"))
        elif q < 0.05:
            w.setze(x, h, z, w.b("coarse_dirt"))
        elif q < 0.06:
            w.setze(x, h + 1, z, w.b("cobweb"))
    return zellen


def toter_baum(w, x, y, z, seed, H):
    einfuegen(w, _kahl(seed + x * 7 + z, H), x, y, z)


def _kahl(seed, H):
    w = _neu(seed)
    rng = w.rng
    for y in range(int(H)):
        w.setze(0, y, 0, w.b("dark_oak_log", axis="y"))
    for k in range(3 + int(H / 4)):
        a = rng.random() * 6.28
        yb = int(H * (0.4 + rng.random() * 0.5))
        L = 2 + rng.random() * H * 0.35
        pts = bez((0, yb, 0), (math.cos(a) * L * 0.5, yb + L * 0.6, math.sin(a) * L * 0.5),
                  (math.cos(a) * L, yb + L * 0.4, math.sin(a) * L))
        for px, py, pz, _ in pts:
            w.setze(round(px), round(py), round(pz), w.b("dark_oak_wood", axis="y"), False)
    return w


def grab(w, x, y, z, art=0, richtung="south"):
    st = ["mossy_cobblestone", "stone_bricks", "andesite", "cobblestone"]
    if art == 0:
        w.setze(x, y, z, w.b("cobblestone_wall"))
        w.setze(x, y + 1, z, w.b("stone_brick_wall"))
    elif art == 1:
        w.setze(x, y, z, w.b(st[(x + z) % 4]))
        w.setze(x, y + 1, z, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    elif art == 2:
        w.setze(x, y, z, w.b("cobblestone_wall"))
        w.setze(x, y + 1, z, w.b("cobblestone_wall"))
        w.setze(x - 1, y + 1, z, w.b("stone_button", face="wall", facing="west", powered=False))
        w.setze(x + 1, y + 1, z, w.b("stone_button", face="wall", facing="east", powered=False))
    else:
        w.setze(x, y, z, w.b("polished_andesite"))
    dz = 1 if richtung == "south" else -1
    w.setze(x, y - 1, z + dz, w.b("coarse_dirt"))
    w.setze(x, y - 1, z + 2 * dz, w.b("coarse_dirt"))


def gestalt(w, rock="black_wool", haut="white_concrete", kopf=True):
    t = [(kap((0, 0, 0), (0, 2.6, 0), 0.8, 0.5), w.b(rock)), (kap((0, 2.6, 0), (0, 3.6, 0), 0.5, 0.45), w.b(rock))]
    if kopf:
        t.append((ell(0, 4.3, 0, 0.5, 0.55, 0.5), w.b(haut)))
        t.append((ell(0.2, 4.4, 0.25, 0.1, 0.1, 0.05), w.b("black_concrete")))
        t.append((ell(0.2, 4.4, -0.25, 0.1, 0.1, 0.05), w.b("black_concrete")))
    return t


# ============================================================================ Bauten

def laternenfriedhof(seed, g=2):
    """Laternenfriedhof: ein dichter Friedhof, auf dem auf fast jedem Grab eine Laterne oder Kerze brennt, mit
    schmiedeeisernem Zaun, einem Torbogen mit Laterne und einer kahlen Linde in der Mitte."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = spukboden(w, R, 0.2)
    A = int(R * 0.75)
    rng = w.rng
    for x in range(-A + 2, A - 1, 2):
        for z in range(-A + 2, A - 2, 4):
            if abs(x) < 3 and abs(z) < 3:
                continue
            y = zellen.get((x, z), 0) + 1
            grab(w, x, y, z, art=(x * 3 + z) % 4)
            if rng.random() < 0.7:
                w.setze(x, y + 2 if (x * 3 + z) % 4 in (0, 2) else y + 1, z,
                        w.b("soul_lantern" if rng.random() < 0.3 else "lantern", hanging=False, waterlogged=False)
                        if rng.random() < 0.6 else w.b("candle", candles=int(rng.integers(1, 5)), lit=True,
                                                       waterlogged=False), False)
    for x in range(-A, A + 1):
        for z in (-A, A):
            if not (z == A and abs(x) < 2):
                w.setze(x, hoehe(w, x, z, 6) + 1, z, w.b("iron_bars", waterlogged=False))
    for z in range(-A, A + 1):
        for x in (-A, A):
            w.setze(x, hoehe(w, x, z, 6) + 1, z, w.b("iron_bars", waterlogged=False))
    for sx in (-2, 2):
        for y in range(1, 5):
            w.setze(sx, y, A, w.b("stone_bricks"))
    for x in range(-2, 3):
        w.setze(x, 5, A, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    laterne(w, 0, 4, A, kette=1)
    toter_baum(w, 0, 1, 0, seed, 8 + 4 * s)
    return w


def geisterkutsche(seed, g=2):
    """Geisterkutsche: eine schwarze, verzierte Kutsche mit violetten Laternen, gezogen von zwei skelettartigen
    Rappen mit glühenden Augen, auf einem nebligen Hohlweg zwischen kahlen Bäumen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = spukboden(w, R, 0.2)
    for x in range(-R, R + 1):
        for dz in (-2, -1, 0, 1, 2):
            if (x, dz) in zellen:
                w.setze(x, zellen[(x, dz)], dz, w.b("dirt_path") if abs(dz) < 2 else w.b("coarse_dirt"))
    sch = w.b("black_concrete")
    gr = w.b("gray_concrete")
    lila = w.b("purple_stained_glass")
    u = 0.6 * s + 0.5
    teile = [(kasten(-2.5, 1.6, -1.5, 2.5, 5.0, 1.5), sch), (kasten(-2.2, 5.0, -1.3, 2.2, 5.6, 1.3), gr),
             (kasten(-1.0, 2.6, -1.6, 1.0, 4.2, 1.6), lila), (kasten(-0.8, 2.8, -1.7, 0.8, 4.0, 1.7), None),
             (kasten(2.5, 2.0, -1.2, 4.0, 3.0, 1.2), sch)]
    for sx in (-1.6, 1.6):
        for sz in (-1.7, 1.7):
            teile.append((lambda X, Y, Z, sx=sx, sz=sz: (np.abs(np.sqrt((X - sx) ** 2 + (Y - 1.2) ** 2) - 1.0) < 0.3) &
                          (np.abs(Z - sz) < 0.25), gr))
    figur(w, u, teile, (-4, -1, -3), (5, 7, 3), pos=(-int(R * 0.25), 1, 0), winkel=0.0)
    knochen = w.b("bone_block")
    for k, sz in enumerate((-1, 1)):
        rp = [(ell(0, 3.4, 0, 1.8, 0.9, 0.7), sch), (kap((1.5, 3.8, 0), (2.4, 5.4, 0), 0.5, 0.4), sch),
              (ell(2.9, 5.4, 0, 0.8, 0.45, 0.4), knochen), (ell(3.0, 5.6, 0.3, 0.12, 0.12, 0.1), w.b("magenta_concrete")),
              (ell(3.0, 5.6, -0.3, 0.12, 0.12, 0.1), w.b("magenta_concrete"))] + \
             [(kap((sx, 3.0, zz), (sx, 0, zz), 0.25), knochen) for sx in (-1.2, 1.2) for zz in (-0.4, 0.4)] + \
             [(kap((-1.0 + i * 0.5, 3.0, 0.6), (-1.0 + i * 0.5, 3.0, -0.6), 0.12), knochen) for i in range(4)]
        figur(w, u * 1.3, rp, (-3, -1, -2), (4, 7, 2), pos=(-int(R * 0.25) + round(7.5 * u), 1, round(sz * 1.9 * u)),
              winkel=0.0)
    rng = w.rng
    for k in range(4 + 2 * g):
        x = int((rng.random() - 0.5) * R * 1.6)
        z = (1 if k % 2 else -1) * int(4 + rng.random() * R * 0.5)
        if (x, z) in zellen:
            toter_baum(w, x, zellen[(x, z)] + 1, z, seed, 6 + rng.random() * 5 * s)
    return w


def spukmuehle(seed, g=2):
    """Spukmühle: eine verlassene Windmühle mit zerfetzten Flügeln aus Spinnweben, schiefem Turm aus dunklem Holz,
    eingeschlagenen Fenstern mit Kürbislaternen und einem Krähenschwarm auf dem Dach."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = spukboden(w, R, 0.3)
    H = int(9 * s + 7)
    for y in range(1, H):
        r = (2.8 * s + 2) * (1 - 0.3 * y / H)
        neig = y * 0.06
        for x, z in kreisrand(r, round(neig), 0):
            w.setze(x, y, z, w.b("dark_oak_planks") if (x + y) % 5 else w.b("cobblestone") if y < 3 else
                    w.b("stripped_dark_oak_log", axis="y"))
        if y % 4 == 2:
            w.setze(round(neig), y, round(r), w.b("jack_o_lantern", facing="south"))
    top = H
    kegeldach(w, round(H * 0.06), 0, top, int(2 * s + 1.5), Dachmat(w, ["dark_oak", "spruce"]), form="kegel",
              spitze=None)
    hx = round(H * 0.06)
    for i in range(4):
        a = i * math.pi / 2 + 0.3
        L = int(6 * s + 5)
        for k in range(1, L):
            p = (hx + int(2.8 * s + 2) + 1, top - 2 + round(math.sin(a) * k), round(math.cos(a) * k))
            w.setze(*p, w.b("dark_oak_fence"), False)
            if k > 2 and (k + i) % 2 == 0:
                for d in (1, 2):
                    q = (p[0], p[1] + round(math.cos(a) * d * 0.5), p[2] - round(math.sin(a) * d * 0.5))
                    w.setze(*q, w.b("cobweb"), False)
    for k in range(3 + g):
        x = hx - 1 + k % 3
        w.setze(x, top + 2 + k // 3, 0, w.b("black_wool"), False)
    return w


def kopfloser_reiter(seed, g=2):
    """Kopfloser Reiter: die Statue eines Reiters ohne Kopf auf einem sich aufbäumenden Rappen, in der erhobenen Hand
    eine leuchtende Kürbislaterne, auf einem Sockel an einer Wegkreuzung im Nebel."""
    w = _neu(seed)
    s = S[g]
    u = 0.8 * s + 0.4
    R = int(10 * u + 6)
    zellen = spukboden(w, R, 0.2)
    for x in range(-R, R + 1):
        for z in (-1, 0, 1):
            if (x, z) in zellen:
                w.setze(x, zellen[(x, z)], z, w.b("dirt_path"))
            if (z, x) in zellen:
                w.setze(z, zellen[(z, x)], x, w.b("dirt_path"))
    st = M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 1)])
    for x in range(-int(3 * u), int(3 * u) + 1):
        for z in range(-int(2 * u), int(2 * u) + 1):
            for y in range(1, int(1.5 * u) + 2):
                w.setze(x + 4, y, z + 4, st(x, y, z))
    sch = w.b("black_concrete")
    um = w.b("gray_wool")
    teile = [(ell(0, 4.2, 0, 2.2, 1.2, 1.0), sch), (kap((1.6, 4.8, 0), (2.4, 7.2, 0), 0.7, 0.55), sch),
             (ell(2.6, 7.6, 0, 1.0, 0.55, 0.5), sch), (kap((1.2, 5.6, 0), (2.2, 7.6, 0), 0.25), w.b("dark_gray_wool")
                                                        if False else um),
             (kap((-2.0, 4.4, 0), (-2.8, 2.6, 0), 0.35, 0.2), um),
             (kap((-1.4, 3.8, 0.45), (-1.6, 0, 0.45), 0.35), sch), (kap((-1.4, 3.8, -0.45), (-1.6, 0, -0.45), 0.35), sch),
             (kap((1.4, 4.0, 0.45), (2.6, 2.6, 0.45), 0.3), sch), (kap((1.4, 4.0, -0.45), (2.6, 2.6, -0.45), 0.3), sch),
             (kap((0, 5.0, 0), (0.2, 7.4, 0), 0.8, 0.65), um), (kap((0.2, 7.3, 0), (0.6, 7.9, 0), 0.35), um),
             (kap((0.2, 6.8, 0.6), (1.2, 8.6, 1.0), 0.25), um), (ell(1.3, 9.0, 1.1, 0.6, 0.6, 0.6),
                                                                  w.b("jack_o_lantern", facing="south")),
             (lambda X, Y, Z: (np.abs(Z + 0.5 * (X + 0.5)) < 0.15) & (Y > 4.8) & (Y < 7.5) & (X < 0) & (X > -2.6),
              w.b("black_wool"))]
    from skulptur import dreh_z
    from skulptur import Skulptur
    Sk = Skulptur(w, u)
    for i, (f, b) in enumerate(teile):
        Sk.mat(str(i), b)
        Sk.plus(f, str(i))
    Sk.rendern((-4, -1, -2), (4, 10, 2), versatz=(4.5, int(1.5 * u) + 2, 4.5), dreh=dreh_z(0.25))
    for k in range(3 + g):
        a = k * 1.7
        x, z = round(math.cos(a) * R * 0.7), round(math.sin(a) * R * 0.7)
        if (x, z) in zellen:
            toter_baum(w, x, zellen[(x, z)] + 1, z, seed, 6 + 2 * s)
    return w


def vogelscheuchenfeld(seed, g=1):
    """Vogelscheuchenfeld: ein abgeerntetes Feld voller verdorrter Halme, auf dem zerlumpte Vogelscheuchen mit
    Kürbisköpfen stehen, Krähen auf den Querbalken, und eine windschiefe Scheune im Hintergrund."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = spukboden(w, R, 0.1, dichte=0.5)
    for x in range(-R, R + 1):
        for z in range(-R, int(R * 0.4)):
            if (x, z) in zellen and z % 2 == 0:
                w.setze(x, zellen[(x, z)], z, w.b("farmland", moisture=0))
                if (x + z) % 3:
                    w.setze(x, zellen[(x, z)] + 1, z, w.b("wheat", age=7) if (x * z) % 4 else w.b("dead_bush"))
    rng = w.rng
    for k in range(3 + g):
        x, z = -int(R * 0.6) + k * int(R * 1.2 / (2 + g)), -int(R * 0.3) + (k % 2) * 4
        y = zellen.get((x, z), 0) + 1
        for yy in range(y, y + 4):
            w.setze(x, yy, z, w.b("spruce_fence"))
        for dx in (-2, -1, 1, 2):
            w.setze(x + dx, y + 3, z, w.b("spruce_fence"))
        w.setze(x, y + 2, z, w.b(["brown_wool", "orange_wool", "gray_wool"][k % 3]))
        w.setze(x, y + 3, z, w.b(["brown_wool", "orange_wool", "gray_wool"][k % 3]))
        w.setze(x, y + 4, z, w.b("carved_pumpkin" if k % 2 else "jack_o_lantern", facing="south"))
        w.setze(x, y + 5, z, w.b("brown_carpet"))
        if rng.random() < 0.7:
            w.setze(x + 2, y + 4, z, w.b("black_wool"))
    haus(w, int(R * 0.35), int(R * 0.55), int(4 * s + 5) | 1, 5, 1,
         M(w, [("dark_oak_planks", 2), ("stripped_dark_oak_log", 1)]), holz="dark_oak", H=4,
         dach=("dark_oak", "mossy_cobblestone"), tuer_s="north", schorn=False, steil=2)
    return w


def nebelbruecke(seed, g=2):
    """Nebelbrücke: eine schmale, uralte Steinbrücke mit eingestürztem Mittelteil, der nur noch durch morsche Bretter
    verbunden ist, über eine dunkle Schlucht mit Nebelschwaden (weißes Glas) und Seelenlaternen an Ketten."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 4)
    H = int(6 * s + 5)
    st = M(w, [("stone_bricks", 2), ("mossy_stone_bricks", 2), ("cracked_stone_bricks", 1)])
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            if abs(x) < R * 0.3 + rn(0, 2, z) * 2:
                w.setze(x, -H, z, w.b("water", level=0))
                if rn(x * 2, 5, z * 2) > 0.55:
                    w.setze(x, -H + 2 + int(rn(x, 7, z) * 3), z, w.b("white_stained_glass"))
                continue
            for y in range(-H, 1):
                w.setze(x, y, z, w.b("podzol" if y == 0 else "stone" if (y + x) % 4 else "andesite"))
    L = int(R * 0.3) + 2
    for x in range(-L, L + 1):
        mitte = abs(x) < L * 0.35
        for z in (-1, 0, 1):
            if mitte:
                if z == 0 and x % 2 == 0:
                    w.setze(x, 0, z, w.b("dark_oak_slab", type="bottom", waterlogged=False))
            else:
                w.setze(x, 0, z, st(x, 0, z))
                w.setze(x, -1, z, st(x, -1, z))
                if abs(z) == 1 and x % 2 == 0:
                    w.setze(x, 1, z, w.b("stone_brick_wall"))
        if not mitte and abs(x) == L - 2:
            for y in range(-H, 0):
                for z in (-1, 0, 1):
                    w.setze(x, y, z, st(x, y, z))
    for sx in (-1, 1):
        for y in range(1, 5):
            w.setze(sx * L, y, 2, w.b("dark_oak_fence"))
        w.setze(sx * (L - 1), 4, 2, w.b("dark_oak_fence"))
        laterne(w, sx * (L - 1), 3, 2, kette=1, seele=True)
    return w


def herrenhaus(seed, g=2):
    """Verfallenes Herrenhaus: ein zweistöckiges Herrenhaus aus dunklem Stein mit eingestürztem Dachflügel, Erkertürmchen,
    zerbrochenen Fenstern, Efeu, einem verwilderten Garten und einem rostigen Tor."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = spukboden(w, R, 0.2)
    from himmelsstadt2 import haus as haus2, STILE
    import erw_haeuser  # noqa: F401
    B, T = int(6 * s + 8) | 1, int(4 * s + 6) | 1
    try:
        haus2(w, 0, -int(R * 0.15), B, T, 2, stil="schiefer", geschosse=2, tuer_s="south", schorn=True, steil=2)
    except KeyError:
        haus2(w, 0, -int(R * 0.15), B, T, 2, stil="stein", geschosse=2, tuer_s="south", schorn=True, steil=2)
    rn = Rauschen(w, 3)
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 8 and x > 0 and rn(x, y, z) < 0.45:
            w.bloecke.pop((x, y, z), None)
        elif y > 2 and w.P.name(b).endswith("glass_pane") and rn(x * 3, y, z) < 0.5:
            w.bloecke.pop((x, y, z), None)
    ex, ez = -B // 2 - 1, -int(R * 0.15) + T // 2
    for y in range(2, 13):
        for x, z in kreisrand(1.6, ex, ez):
            w.setze(x, y, z, w.b("deepslate_bricks"))
    kegeldach(w, ex, ez, 13, 2, Dachmat(w, ["deepslate_tile"]), form="nadel", spitze="lightning_rod")
    efeu(w, 0.1, 0.4)
    A = int(R * 0.8)
    for x in range(-A, A + 1):
        if abs(x) > 2:
            w.setze(x, hoehe(w, x, A, 4) + 1, A, w.b("iron_bars", waterlogged=False))
    for sx in (-3, 3):
        for y in range(1, 4):
            w.setze(sx, y, A, w.b("stone_bricks"))
    rng = w.rng
    for k in range(3 + g):
        a = rng.random() * 6.28
        x, z = round(math.cos(a) * R * 0.75), round(math.sin(a) * R * 0.75)
        if (x, z) in zellen:
            toter_baum(w, x, zellen[(x, z)] + 1, z, seed, 7 + 3 * s)
    return w


def hangfriedhof(seed, g=2):
    """Hangfriedhof: ein in Terrassen angelegter Bergfriedhof mit Stützmauern, Treppen zwischen den Grabreihen,
    Zypressen, einer kleinen Kapelle oben und weitem Blick ins Tal."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    st = M(w, [("stone_bricks", 2), ("mossy_stone_bricks", 1), ("cobblestone", 1)])
    n = 3 + g
    rng = w.rng
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) > R:
                continue
            k = min(n - 1, max(0, int((R - z) / (2 * R) * n)))
            h = k * 3
            for y in range(-2, h + 1):
                rand = ((R - z) % max(1, int(2 * R / n))) == 0 and y > h - 3
                w.setze(x, y, z, st(x, y, z) if rand else w.b("grass_block", snowy=False) if y == h else w.b("dirt"))
    for k in range(n):
        h = k * 3
        z0 = R - int((k + 0.5) * 2 * R / n)
        for x in range(-R + 3, R - 2, 2):
            if abs(x) < 2:
                continue
            if math.hypot(x, z0) < R - 2:
                grab(w, x, h + 1, z0, art=(x + k) % 4)
        for j in range(4):
            if math.hypot(-1, z0) < R:
                pass
    for zz in range(-R, R):
        k = min(n - 1, max(0, int((R - zz) / (2 * R) * n)))
        for x in (-1, 0, 1):
            w.setze(x, k * 3, zz, w.b("gravel"))
    top = (n - 1) * 3
    haus(w, 0, -R + 4, 5, 5, top + 1, M(w, [("white_terracotta", 1)]), holz="dark_oak", H=4,
         dach=("deepslate_tile", "cobbled_deepslate"), tuer_s="south", schorn=False, steil=2)
    for k in range(4 + g):
        x, z = (R - 3) * (1 if k % 2 else -1), -R + 4 + k * 3
        if math.hypot(x, z) < R:
            y = hoehe(w, x, z, top + 5) + 1
            for yy in range(y, y + int(5 + 2 * s)):
                w.setze(x, yy, z, w.b("spruce_leaves", persistent=True, distance=1, waterlogged=False))
    _ = rng
    return w


def glockenstuhl(seed, g=1):
    """Glockenstuhl: ein freistehender, hölzerner Glockenturm am Rand eines Friedhofs mit großer Totenglocke, einem
    Glockenseil, einer kleinen überdachten Bank und windschiefen Kreuzen ringsum."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = spukboden(w, R, 0.2)
    H = int(6 * s + 6)
    for dx in (-2, 2):
        for dz in (-2, 2):
            for y in range(1, H):
                w.setze(dx, y, dz, w.b("dark_oak_log", axis="y"))
        for y in range(2, H, 3):
            w.setze(dx, y, 0, w.b("dark_oak_fence"))
            w.setze(0, y, dx, w.b("dark_oak_fence"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, H, z, w.b("dark_oak_planks"))
    w.setze(0, H - 1, 0, w.b("bell", attachment="ceiling", facing="north", powered=False))
    for y in range(1, H - 2):
        w.setze(1, y, 0, w.b("tripwire", attached=False, disarmed=False, east=False, west=False, north=True,
                             south=True, powered=False) if False else w.b("chain", axis="y", waterlogged=False))
    kegeldach(w, 0, 0, H + 1, 2, Dachmat(w, ["dark_oak", "spruce"]), form="kegel", eckig=True, spitze="lightning_rod")
    rng = w.rng
    for k in range(6 + 3 * g):
        a = rng.random() * 6.28
        d = 4 + rng.random() * (R - 6)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if (x, z) in zellen:
            y = zellen[(x, z)] + 1
            w.setze(x, y, z, w.b("dark_oak_fence"))
            w.setze(x, y + 1, z, w.b("dark_oak_fence"))
            w.setze(x + 1, y + 1, z, w.b("dark_oak_fence"), False)
    return w


def sargmacher(seed, g=1):
    """Sargmacher-Werkstatt: ein schmales, schwarzes Fachwerkhaus, vor dem aufrecht stehende Särge lehnen, eine
    Hobelbank mit halbfertigem Sarg, Bretterstapel, ein Schild mit Sanduhr und eine Leiterwagen-Totenbahre."""
    w = _neu(seed)
    s = S[g]
    R = int(8 * s + 5)
    zellen = spukboden(w, R, 0.1)
    B, T = int(3 * s + 5) | 1, int(2 * s + 5) | 1
    haus(w, 0, -int(R * 0.3), B, T, 1, M(w, [("black_terracotta", 2), ("gray_terracotta", 1)]), holz="dark_oak",
         H=int(3 + 2 * s), dach=("deepslate_tile", "dark_oak"), tuer_s="south", steil=2)
    z1 = -int(R * 0.3) + T // 2
    for k in range(3):
        x = -B // 2 + k * 2
        for y in (1, 2, 3):
            w.setze(x, y, z1 + 1, w.b("spruce_trapdoor", facing="south", half="bottom", open=True, powered=False,
                                      waterlogged=False) if y < 3 else w.b("spruce_slab", type="bottom",
                                                                            waterlogged=False))
    for x in range(B // 2 + 2, B // 2 + 6):
        w.setze(x, 1, 1, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x, 2, 1, w.b("spruce_trapdoor", facing="north", half="bottom", open=False, powered=False,
                             waterlogged=False))
    for k in range(4):
        w.setze(-B // 2 - 2, 1 + k // 2, -1 + k % 2, w.b("spruce_planks"))
    w.setze(0, 4, z1 + 1, w.b("gold_block") if False else w.b("glass"))
    _ = zellen
    return w


def grabpyramide(seed, g=2):
    """Grabpyramide: eine kleine, steile Pyramide aus dunklem Granitstein als Familiengrab, mit einem Portal aus
    Säulen, Sphinx-artigen Wächterkatzen, Grablichtern und einem verwilderten Rasen davor."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = spukboden(w, R, 0.1)
    A = int(4 * s + 4)
    st = M(w, [("polished_deepslate", 2), ("deepslate_bricks", 2), ("deepslate_tiles", 1)])
    for k in range(int(A * 1.4)):
        a = A - k * 0.7
        if a < 0.5:
            break
        for x in range(-int(a), int(a) + 1):
            for z in range(-int(a), int(a) + 1):
                if max(abs(x), abs(z)) >= int(a) - 1 or k == 0:
                    w.setze(x, 1 + k, z, st(x, k, z))
    w.setze(0, int(A * 1.4) + 1, 0, w.b("gold_block"))
    for sx in (-1, 1):
        for y in range(1, 4):
            w.setze(sx * 2, y, A + 1, w.b("polished_blackstone_wall") if False else w.b("deepslate_brick_wall"))
    for y in (1, 2):
        w.setze(0, y, A, w.b("black_concrete"))
    sch = w.b("black_terracotta")
    for sx in (-1, 1):
        teile = [(ell(0, 1.0, 0, 0.6, 1.0, 1.2), sch), (ell(0, 2.2, 0.8, 0.6, 0.6, 0.55), sch),
                 (kegel(-0.3, 0.8, 2.6, 3.2, 0.25, 0.02), sch), (kegel(0.3, 0.8, 2.6, 3.2, 0.25, 0.02), sch),
                 (ell(-0.25, 2.3, 1.3, 0.12, 0.12, 0.08), w.b("lime_concrete")),
                 (ell(0.25, 2.3, 1.3, 0.12, 0.12, 0.08), w.b("lime_concrete"))]
        figur(w, 0.8 * s + 0.4, teile, (-2, -1, -2), (2, 4, 2), pos=(sx * 4, 1, A + 3), winkel=0.0)
    for k in range(6):
        x = -5 + k * 2
        w.setze(x, 1, A + 6, w.b("candle", candles=2, lit=True, waterlogged=False))
    _ = zellen
    return w


def weinende_statuen(seed, g=2):
    """Weinende Statuen: ein Kreis aus verhüllten, trauernden Steinfiguren mit gesenkten Köpfen und vor das Gesicht
    gelegten Händen, um ein zerbrochenes Grabmal, überwuchert von Moos und Rosen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = spukboden(w, R, 0.1)
    st = M(w, [("stone", 2), ("andesite", 2), ("mossy_cobblestone", 1)])
    n = 5 + g
    for i in range(n):
        a = i / n * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        teile = [(kap((0, 0, 0), (0, 4.0, 0), 1.1, 0.7), lambda X, Y, Z, *q: st(X, Y, Z)),
                 (ell(0.3, 4.6, 0, 0.7, 0.75, 0.7), lambda X, Y, Z, *q: st(X, Y, Z)),
                 (ell(0.1, 4.9, 0, 0.85, 0.65, 0.8), lambda X, Y, Z, *q: st(X, Y, Z)),
                 (kap((0.2, 3.6, 0.5), (0.8, 4.4, 0.25), 0.3), lambda X, Y, Z, *q: st(X, Y, Z)),
                 (kap((0.2, 3.6, -0.5), (0.8, 4.4, -0.25), 0.3), lambda X, Y, Z, *q: st(X, Y, Z)),
                 (kasten(-1.2, 0, -1.2, 1.2, 0.6, 1.2), w.b("mossy_stone_bricks"))]
        figur(w, 0.8 * s + 0.5, teile, (-2, -1, -2), (2, 6, 2), pos=(x, zellen.get((x, z), 0) + 1, z),
              winkel=-a + math.pi)
    for x in range(-2, 3):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("mossy_stone_bricks") if (x + z) % 3 else w.b("cracked_stone_bricks"))
    w.setze(-1, 2, 0, w.b("mossy_stone_bricks"))
    w.setze(-1, 3, 0, w.b("mossy_stone_brick_wall"))
    for x in range(-3, 4):
        w.setze(x, 1, 2, w.b("rose_bush", half="lower"))
        w.setze(x, 2, 2, w.b("rose_bush", half="upper"))
    return w


def kolumbarium(seed, g=2):
    """Kolumbarium: eine halbrunde Wand aus hellem Stein mit Hunderten kleiner Nischen für Urnen (Blumentöpfe,
    Kerzen), einem Säulengang davor, einer Trauerhalle in der Mitte und Zypressen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = spukboden(w, R, 0.05)
    rr = R * 0.7
    H = int(5 * s + 5)
    rng = w.rng
    for k in range(int(rr * 7)):
        a = math.pi + math.pi * k / (rr * 7)
        x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b("smooth_stone") if (y + k) % 2 == 0 or y in (1, H) else
                    w.b("flower_pot") if rng.random() < 0.5 else w.b("candle", candles=1, lit=True, waterlogged=False))
            w.setze(x - round(math.cos(a)), y, z - round(math.sin(a)), w.b("stone_bricks"), False)
        w.setze(x, H + 1, z, w.b("smooth_stone_slab", type="bottom", waterlogged=False))
    for k in range(0, int(rr * 7), 4):
        a = math.pi + math.pi * k / (rr * 7)
        x, z = round(math.cos(a) * (rr - 3)), round(math.sin(a) * (rr - 3))
        for y in range(1, H):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
        w.setze(x, H, z, w.b("smooth_quartz"))
    haus(w, 0, -int(rr * 0.35), 5, 5, 1, M(w, [("smooth_stone", 1)]), holz="dark_oak", H=4,
         dach=("deepslate_tile",), tuer_s="south", schorn=False)
    for sx in (-1, 1):
        x, z = sx * int(rr * 0.9), int(R * 0.3)
        for y in range(1, int(6 + 2 * s)):
            w.setze(x, y, z, w.b("spruce_leaves", persistent=True, distance=1, waterlogged=False))
    _ = zellen
    return w


def grabhecken(seed, g=2):
    """Grabhecken-Labyrinth: ein düsterer Irrgarten aus hohen, dunklen Eibenhecken, an dessen Sackgassen einzelne
    Gräber stehen; in der Mitte ein offenes Grab mit Sarg und eine Kerzenlaterne."""
    w = _neu(seed)
    s = S[g]
    n = 5 + 2 * g
    zelle = 3
    R = n * zelle // 2 + 3
    zellen = spukboden(w, R + 2, 0.0)
    rng = w.rng
    besucht = {(n // 2, n // 2)}
    stapel = [(n // 2, n // 2)]
    offen = set()
    while stapel:
        cx, cz = stapel[-1]
        nb = [(cx + dx, cz + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= cx + dx < n and 0 <= cz + dz < n and (cx + dx, cz + dz) not in besucht]
        if not nb:
            stapel.pop()
            continue
        nx, nz = nb[int(rng.integers(len(nb)))]
        offen.add(frozenset(((cx, cz), (nx, nz))))
        besucht.add((nx, nz))
        stapel.append((nx, nz))
    x0 = -n * zelle // 2
    H = int(2 * s + 3)
    hk = w.b("dark_oak_leaves", persistent=True, distance=1, waterlogged=False)
    grad = {}
    for e in offen:
        for c in e:
            grad[c] = grad.get(c, 0) + 1
    for i in range(n * zelle + 1):
        for j in range(n * zelle + 1):
            ci, ri = divmod(i, zelle)
            cj, rj = divmod(j, zelle)
            if ri == 0 and rj == 0:
                wand = True
            elif ri == 0:
                wand = not (0 < ci < n and frozenset(((ci - 1, cj), (ci, cj))) in offen)
            elif rj == 0:
                wand = not (0 < cj < n and frozenset(((ci, cj - 1), (ci, cj))) in offen)
            else:
                wand = False
            x, z = x0 + i, x0 + j
            if wand and not (j == 0 and abs(i - n * zelle // 2) <= 1):
                for y in range(1, H + 1):
                    w.setze(x, y, z, hk)
            elif ri == 1 and rj == 1 and grad.get((ci, cj), 0) == 1 and (ci, cj) != (n // 2, n // 2):
                grab(w, x, 1, z, art=(ci + cj) % 4)
    m = x0 + (n // 2) * zelle + 1
    for dx in (0, 1):
        w.setze(m + dx, 0, m, w.b("air"))
        w.setze(m + dx, -1, m, w.b("spruce_slab", type="top", waterlogged=False))
    w.setze(m + 1, 1, m + 1, w.b("lantern", hanging=False, waterlogged=False))
    _ = zellen
    return w


def seelenweide(seed, g=2):
    """Seelenlaternen-Weide: eine riesige, gebeugte Trauerweide mit grauem Laub, von deren hängenden Zweigen
    Dutzende Seelenlaternen an Ketten baumeln, über einem kleinen, stillen Teich mit Grabsteinen am Ufer."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = spukboden(w, R, 0.1)
    for x in range(-int(R * 0.5), int(R * 0.5) + 1):
        for z in range(int(R * 0.1), int(R * 0.6)):
            if math.hypot(x, z - R * 0.35) < R * 0.3:
                w.setze(x, 0, z, w.b("water", level=0))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
    H = int(10 * s + 8)
    rohr(w, bez((0, 0, -2), (1, H * 0.5, -1), (0, H, 0)), 1.4 * s + 1, 0.8 * s + 0.5,
         mat=w.b("dark_oak_log", axis="y"), rauh=0.12)
    rng = w.rng
    for k in range(int(10 + 6 * s)):
        a = k / (10 + 6 * s) * 2 * math.pi
        L = (6 + rng.random() * 3) * s + 3
        pts = bez((0, H, 0), (math.cos(a) * L * 0.6, H + 2, math.sin(a) * L * 0.6),
                  (math.cos(a) * L, H - 2, math.sin(a) * L))
        for px, py, pz, t in pts:
            w.setze(round(px), round(py), round(pz), w.b("dark_oak_wood", axis="y") if t < 0.6 else
                    w.b("gray_wool"), False)
        ex, ey, ez, _ = pts[-1]
        for dy in range(1, int(4 + rng.random() * 4 * s)):
            w.setze(round(ex), round(ey) - dy, round(ez), w.b("light_gray_wool") if dy % 2 else w.b("gray_wool"),
                    False)
        if k % 2 == 0:
            ly = round(ey) - 2
            w.setze(round(ex) + 1, ly, round(ez), w.b("chain", axis="y", waterlogged=False), False)
            w.setze(round(ex) + 1, ly - 1, round(ez), w.b("soul_lantern", hanging=True, waterlogged=False), False)
    laubball(w, 0, H + 1, 0, 3 * s + 2, arten=("gray_wool",), dicht=0.6) if False else None
    for k in range(4):
        a = math.pi * 0.2 + k * 0.4
        x, z = round(math.cos(a) * R * 0.45), round(R * 0.35 + math.sin(a) * R * 0.35)
        if (x, z) in zellen:
            grab(w, x, zellen[(x, z)] + 1, z, art=k)
    return w


def verfluchter_brunnen(seed, g=1):
    """Verfluchter Brunnen: ein moosbewachsener Ziehbrunnen mit zerbrochenem Dach und Ketten, aus dem bläuliches
    Seelenfeuer leuchtet, umgeben von einem Kreis aus Totenschädeln auf Pfählen und verdorrten Bäumen."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    zellen = spukboden(w, R, 0.1)
    rb = 1.6 * s + 1.4
    for y in range(-4, 2):
        for x, z in kreisrand(rb):
            w.setze(x, y, z, w.b("mossy_cobblestone" if (x + y) % 2 else "cobblestone"))
    for x in range(-int(rb) + 1, int(rb)):
        for z in range(-int(rb) + 1, int(rb)):
            if math.hypot(x, z) < rb - 0.8:
                for y in range(-3, 2):
                    w.bloecke.pop((x, y, z), None)
                w.setze(x, -4, z, w.b("soul_soil"))
                w.setze(x, -3, z, w.b("soul_fire"))
    for sx in (-1, 1):
        for y in range(2, 5):
            w.setze(sx * round(rb), y, 0, w.b("dark_oak_fence"))
    for x in range(-round(rb), round(rb) + 1):
        w.setze(x, 5, 0, w.b("dark_oak_log", axis="x"))
    for y in range(1, 5):
        w.setze(0, y, 0, w.b("chain", axis="y", waterlogged=False))
    w.setze(-1, 6, 0, treppe(w, "dark_oak", "south"))
    w.setze(1, 6, 1, treppe(w, "dark_oak", "north"))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        y = zellen.get((x, z), 0) + 1
        w.setze(x, y, z, w.b("dark_oak_fence"))
        w.setze(x, y + 1, z, w.b("skeleton_skull", rotation=(i * 2) % 16))
    for k in range(2 + g):
        a = k * 2.3
        x, z = round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8)
        if (x, z) in zellen:
            toter_baum(w, x, zellen[(x, z)] + 1, z, seed, 5 + 2 * s)
    return w


def gespenstertafel(seed, g=1):
    """Gespenstertafel: eine lange Festtafel unter freiem Himmel in einer Ruine, gedeckt mit Kerzenleuchtern,
    verstaubten Kuchen und Kelchen, an der durchscheinende Gespenster-Figuren (weißes Glas) sitzen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = spukboden(w, R, 0.05)
    L = int(4 * s + 4)
    for x in range(-L, L + 1):
        for z in (-1, 0, 1):
            w.setze(x, 1, z, w.b("dark_oak_slab", type="top", waterlogged=False))
            if x % 3 == 0:
                w.setze(x, 2, 0, w.b("candle", candles=3, lit=True, waterlogged=False))
            elif x % 3 == 1:
                w.setze(x, 2, z, w.b("cake") if z == 0 else w.b("air"))
        for sz in (-2, 2):
            w.setze(x, 1, sz, treppe(w, "dark_oak", "south" if sz < 0 else "north"))
    ge = w.b("white_stained_glass")
    for k in range(int(2 * L / 3)):
        x = -L + 1 + k * 3
        for sz in (-1, 1):
            if (k + sz) % 2:
                teile = [(kap((0, 1.0, 0), (0, 3.6, 0), 0.8, 0.55), ge), (ell(0, 4.2, 0, 0.6, 0.6, 0.6), ge),
                         (ell(0.3, 4.3, 0.25, 0.1, 0.12, 0.08), w.b("black_concrete")),
                         (ell(0.3, 4.3, -0.25, 0.1, 0.12, 0.08), w.b("black_concrete"))]
                figur(w, 0.5 * s + 0.3, teile, (-2, -1, -2), (2, 6, 2), pos=(x, 1, sz * 2 + sz),
                      winkel=math.pi / 2 if sz < 0 else -math.pi / 2)
    st = M(w, [("stone_bricks", 2), ("mossy_stone_bricks", 2), ("cracked_stone_bricks", 1)])
    rn = Rauschen(w, 3)
    for x in range(-L - 3, L + 4):
        for z in (-5, 5):
            h = int(2 + rn(x, 0, z) * 5 * s)
            for y in range(1, h):
                w.setze(x, y, z, st(x, y, z))
    _ = zellen
    return w


def fledermausturm(seed, g=2):
    """Fledermausturm: ein schiefer, halb eingestürzter Kirchturm aus schwarzem Stein, aus dessen Schallöffnungen
    Schwärme von Fledermaus-Figuren aufsteigen, mit einer zerbrochenen Uhr und einem Krähennest im Dachstuhl."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = spukboden(w, R, 0.2)
    A = int(2 * s + 2)
    H = int(14 * s + 10)
    st = M(w, [("deepslate_bricks", 3), ("cracked_deepslate_bricks", 1), ("cobbled_deepslate", 1)])
    for y in range(1, H):
        neig = round(y * 0.08)
        for x in range(-A, A + 1):
            for z in range(-A, A + 1):
                if max(abs(x), abs(z)) == A:
                    schall = y > H - 5 and (x == 0 or z == 0)
                    if not schall:
                        w.setze(x + neig, y, z, st(x, y, z))
    neig = round(H * 0.08)
    w.setze(neig, H - 8, A + 1, w.b("white_concrete"))
    w.setze(neig, H - 7, A + 1, w.b("black_concrete"))
    for k in range(A + 1):
        for x in range(-A + k, A + 1 - k):
            for z in range(-A + k, A + 1 - k):
                if max(abs(x), abs(z)) == A - k and (x + z + k) % 3:
                    w.setze(x + neig, H + k, z, w.b("deepslate_tiles"))
    rng = w.rng
    sch = w.b("black_wool")
    for k in range(int(10 * s + 6)):
        a = rng.random() * 6.28
        d = A + 2 + rng.random() * 4 * s
        x, z = round(neig + math.cos(a) * d), round(math.sin(a) * d)
        y = H - 3 + int(rng.random() * 8 * s)
        w.setze(x, y, z, sch)
        w.setze(x + 1, y + 1, z, sch, False)
        w.setze(x - 1, y + 1, z, sch, False)
    _ = zellen
    return w


def nebeldorf(seed, g=2):
    """Verlassenes Nebeldorf: eine Handvoll verfallener Häuser mit eingestürzten Dächern an einer schlammigen
    Gasse, Nebelfetzen (weißes Glas) zwischen den Wänden, ein umgestürzter Karren und ein leerer Brunnen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = spukboden(w, R, 0.1)
    for x in range(-R, R + 1):
        for dz in (-1, 0, 1):
            if (x, dz) in zellen:
                w.setze(x, zellen[(x, dz)], dz, w.b("mud") if (x + dz) % 3 else w.b("coarse_dirt"))
    rn = Rauschen(w, 3)
    wand = M(w, [("dark_oak_planks", 2), ("cobblestone", 1), ("mossy_cobblestone", 1)])
    n = 3 + g
    for k in range(n):
        x = -int(R * 0.7) + k * int(R * 1.4 / max(1, n - 1))
        z = (5 if k % 2 else -5) + (1 if k % 2 else -1) * int(s * 2)
        haus(w, x, z, 7, 6, 1, wand, holz="dark_oak", H=4, dach=("dark_oak", "mossy_cobblestone"),
             tuer_s="north" if k % 2 else "south", schorn=k % 2 == 0)
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 4 and rn(x, y, z) < 0.4:
            w.bloecke.pop((x, y, z), None)
    rng = w.rng
    for _ in range(int(12 * s)):
        x, z = int((rng.random() - 0.5) * R * 1.6), int((rng.random() - 0.5) * R * 1.6)
        if (x, z) in zellen and w.frei(x, zellen[(x, z)] + 2, z):
            w.setze(x, zellen[(x, z)] + 2, z, w.b("white_stained_glass"))
    w.setze(2, 1, 0, w.b("spruce_slab", type="bottom", waterlogged=False))
    w.setze(3, 2, 0, w.b("spruce_trapdoor", facing="west", half="bottom", open=True, powered=False,
                         waterlogged=False))
    return w


def trauerweide_stein(seed, g=2):
    """Steinerne Trauerweide: die Skulptur einer Trauerweide aus grauem Stein, deren herabhängende Zweige wie ein
    Vorhang ein Grabmal umschließen, mit eingemeißelten Blättern und Moos in den Fugen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = spukboden(w, R, 0.1)
    st = M(w, [("stone", 3), ("andesite", 2), ("mossy_cobblestone", 1)])
    H = int(8 * s + 6)
    rohr(w, bez((0, 0, 0), (0.5, H * 0.5, 0), (0, H, 0)), 1.2 * s + 0.8, 0.6 * s + 0.4,
         mat=lambda x, y, z, *a: st(x, y, z), rauh=0.12)
    rk = 5 * s + 3
    rng = w.rng
    for k in range(int(rk * 3)):
        a = k / (rk * 3) * 2 * math.pi + rng.random() * 0.2
        pts = bez((0, H, 0), (math.cos(a) * rk * 0.5, H + 2.5 * s, math.sin(a) * rk * 0.5),
                  (math.cos(a) * rk, H + 0.5, math.sin(a) * rk))
        for px, py, pz, t in pts:
            w.setze(round(px), round(py), round(pz), st(round(px), round(py), round(pz)), False)
        ex, ey, ez, _ = pts[-1]
        L = int(H * (0.4 + rng.random() * 0.45))
        for dy in range(1, L):
            w.setze(round(ex), round(ey) - dy, round(ez), w.b("mossy_stone_brick_wall") if (dy + k) % 3 == 0 else
                    w.b("stone_brick_wall"), False)
    grab(w, 2, 1, 0, art=2)
    _ = zellen
    return w


FRIEDHOF3 = {
    "laternenfriedhof": ("Laternenfriedhof", laternenfriedhof),
    "geisterkutsche": ("Geisterkutsche", geisterkutsche),
    "spukmuehle": ("Spukmühle", spukmuehle),
    "kopfloser_reiter": ("Kopfloser Reiter", kopfloser_reiter),
    "vogelscheuchenfeld": ("Vogelscheuchenfeld", vogelscheuchenfeld),
    "nebelbruecke": ("Nebelbrücke", nebelbruecke),
    "herrenhaus": ("Verfallenes Herrenhaus", herrenhaus),
    "hangfriedhof": ("Hangfriedhof", hangfriedhof),
    "glockenstuhl": ("Glockenstuhl", glockenstuhl),
    "sargmacher": ("Sargmacher-Werkstatt", sargmacher),
    "grabpyramide": ("Grabpyramide", grabpyramide),
    "weinende_statuen": ("Weinende Statuen", weinende_statuen),
    "kolumbarium": ("Kolumbarium", kolumbarium),
    "grabhecken": ("Grabhecken-Labyrinth", grabhecken),
    "seelenweide": ("Seelenlaternen-Weide", seelenweide),
    "verfluchter_brunnen": ("Verfluchter Brunnen", verfluchter_brunnen),
    "gespenstertafel": ("Gespenstertafel", gespenstertafel),
    "fledermausturm": ("Fledermausturm", fledermausturm),
    "nebeldorf": ("Verlassenes Nebeldorf", nebeldorf),
    "trauerweide_stein": ("Steinerne Trauerweide", trauerweide_stein),
}

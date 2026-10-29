"""Schiffe & Steampunk II – zwanzig weitere Dampf- und Messingmaschinen (eigene Entwürfe): Dampflok, Luftschiff-
Werft, Ornithopter, Dampftraktor, Kesselhaus, Wasserturm, Erfinderwerkstatt, Teslaturm, Dampfmech, U-Boot,
Frachtballon, Raddampfer, Dampfkran, Messingteleskop, Bahnhof, Förderturm, Seilbahnstation, Dampfkutsche, Fliegende
Festung und Gasometer."""

from __future__ import annotations

import math

import numpy as np

from feinbau import Dachmat, Mix, fenster, kegeldach, mauer, platte, satteldach, stamm, treppe, tuer, zaun
from leuchtwald2 import bez, kugel, rohr
from riesenbogen import zahnrad
from schiffe import _welt

U = [0.6, 1.0, 1.7, 2.8]


def r_(v, m=1):
    return max(m, int(round(v)))


def kupfer(w):
    return Mix(w, [("waxed_copper_block", 2), ("waxed_cut_copper", 2), ("waxed_exposed_copper", 1)], zelle=1.4)


def eisen(w):
    return Mix(w, [("polished_blackstone", 2), ("iron_block", 1), ("polished_deepslate", 1)], zelle=1.4)


def boden(w, x0, z0, x1, z1, mats=(("gravel", 2), ("cobblestone", 2), ("stone_bricks", 1), ("andesite", 1))):
    M = Mix(w, list(mats), zelle=1.5)
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, 0, z, M(x, 0, z))
            w.setze(x, -1, z, w.b("stone"))


def zylinder(w, a, b, R, mat, hohl=False, nieten=None, abstand=3):
    """Zylinder von a nach b (Punkte), Radius R; optional Nietenringe."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = np.linalg.norm(d)
    d /= L
    lo = np.floor(np.minimum(a, b) - R - 1).astype(int)
    hi = np.ceil(np.maximum(a, b) + R + 1).astype(int)
    for x in range(lo[0], hi[0] + 1):
        for y in range(lo[1], hi[1] + 1):
            for z in range(lo[2], hi[2] + 1):
                p = np.array([x, y, z], float) - a
                t = p @ d
                if t < -0.5 or t > L + 0.5:
                    continue
                q = np.linalg.norm(p - t * d)
                if q <= R + 0.3 and (not hohl or q > R - 1.0 or t < 0.5 or t > L - 0.5):
                    ring = nieten is not None and (int(round(t)) % abstand == 0) and q > R - 1.0
                    w.setze(x, y, z, nieten if ring else (mat(x, y, z) if callable(mat) else mat))


def schornstein(w, x, y, z, H, r=1, mat="bricks", rauch=True):
    for yy in range(y, y + H):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if r == 0 or abs(dx) == r or abs(dz) == r:
                    w.setze(x + dx, yy, z + dz, w.b(mat))
    for dx in range(-r - 1, r + 2):
        for dz in range(-r - 1, r + 2):
            if abs(dx) == r + 1 or abs(dz) == r + 1:
                w.setze(x + dx, y + H, z + dz, w.b("polished_blackstone_brick_slab", type="bottom",
                                                   waterlogged=False))
    if rauch:
        w.setze(x, y + H - 1, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))


def rad(w, cx, cy, cz, R, ebene="xy", reifen="polished_blackstone", speiche="dark_oak_fence"):
    for a in range(-R - 1, R + 2):
        for b in range(-R - 1, R + 2):
            d = math.hypot(a, b)
            blk = None
            if R - 0.6 <= d <= R + 0.45:
                blk = w.b(reifen)
            elif d <= 0.6:
                blk = w.b("iron_block")
            elif d < R - 0.6 and (a == 0 or b == 0 or (abs(a) == abs(b) and R >= 3)):
                blk = w.b("dark_oak_planks")
            if blk is not None:
                if ebene == "xy":
                    w.setze(cx + a, cy + b, cz, blk)
                else:
                    w.setze(cx, cy + b, cz + a, blk)


def propeller(w, x, y, z, R, achse="x"):
    for k in range(-R, R + 1):
        if achse == "x":
            w.setze(x, y + k, z, w.b("spruce_planks"))
            w.setze(x, y, z + k, w.b("spruce_planks"))
        else:
            w.setze(x + k, y, z, w.b("spruce_planks"))
            w.setze(x, y + k, z, w.b("spruce_planks"))
    w.setze(x, y, z, w.b("waxed_copper_block"))


def huelle(w, cx, cy, cz, L, R, mat, achse="x"):
    """Spindelförmige Ballonhülle."""
    for x in range(-int(L / 2) - 1, int(L / 2) + 2):
        t = x / (L / 2)
        if abs(t) > 1:
            continue
        r = R * (1 - abs(t) ** 2.2) ** 0.5
        for y in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(y, z)
                if r - 1.3 < d <= r:
                    p = (cx + x, cy + y, cz + z) if achse == "x" else (cx + z, cy + y, cz + x)
                    w.setze(*p, mat(*p) if callable(mat) else mat)


def gleis(w, x0, x1, z, y=1):
    for x in range(x0, x1 + 1):
        w.setze(x, y, z, w.b("rail", shape="east_west", waterlogged=False))
        if x % 2 == 0:
            for dz in (-1, 0, 1):
                w.setze(x, y - 1, z + dz, w.b("spruce_slab", type="top", waterlogged=False))


# ============================================================================ Maschinen

def dampflok(seed, g=1):
    """Dampflok: eine schwarz-kupferne Lokomotive mit Kessel, Dampfdom, Schornstein, Führerhaus, drei großen
    Treibrädern je Seite und Kohlentender auf Gleisen."""
    w = _welt(seed)
    u = U[g]
    L = r_(14 * u + 6)
    R = r_(2.2 * u + 1, 2)
    boden(w, -L - 4, -R - 3, L // 2 + 6, R + 3)
    for dz in (-R + 1, R - 1):
        gleis(w, -L - 4, L // 2 + 6, dz)
    yk = R + 2 + r_(0.8 * u, 1)
    zylinder(w, (-L * 0.3, yk, 0), (L * 0.45, yk, 0), R, kupfer(w), nieten=w.b("polished_blackstone"), abstand=3)
    kugel(w, L * 0.45, yk, 0, R * 0.95, w.b("polished_blackstone"))
    w.setze(round(L * 0.45) + R, yk, 0, w.b("sea_lantern"))
    schornstein(w, round(L * 0.32), yk + R, 0, r_(2.5 * u + 1, 2), r_(0.5 * u, 0), "polished_blackstone")
    kugel(w, 0, yk + R, 0, r_(0.9 * u, 1), w.b("gold_block"))
    cx0 = round(-L * 0.3) - r_(4 * u, 3)
    for x in range(cx0, round(-L * 0.3) + 1):
        for z in range(-R - 1, R + 2):
            for y in range(2, yk + R + 2):
                rand = x in (cx0, round(-L * 0.3)) or abs(z) == R + 1
                if rand:
                    fen = y in (yk, yk + 1) and abs(z) == R + 1 and x not in (cx0, round(-L * 0.3))
                    w.setze(x, y, z, w.b("glass_pane", north=False, south=False, east=True, west=True,
                                         waterlogged=False) if fen else w.b("dark_oak_planks"))
            w.setze(x, yk + R + 2, z, w.b("polished_blackstone_slab", type="bottom", waterlogged=False))
    for x in range(round(-L * 0.35), round(L * 0.5) + 1):
        for z in range(-R, R + 1):
            w.setze(x, 2, z, w.b("polished_blackstone"))
    rr = r_(1.2 * u + 0.6, 1)
    for k in range(3):
        x = round(-L * 0.2 + k * (L * 0.22))
        for sz in (-R - 1, R + 1):
            rad(w, x, rr + 1, sz, rr, "xy", "iron_block")
    for z in range(-R, R + 1):
        w.setze(round(L * 0.5) + 2, 1, z, treppe(w, "polished_blackstone", "west"))
    tx0, tx1 = cx0 - r_(8 * u, 5), cx0 - 2
    for x in range(tx0, tx1 + 1):
        for z in range(-R, R + 1):
            w.setze(x, 2, z, w.b("polished_blackstone"))
            rand = x in (tx0, tx1) or abs(z) == R
            for y in range(3, 3 + r_(2 * u + 1)):
                if rand:
                    w.setze(x, y, z, w.b("dark_oak_planks"))
                else:
                    w.setze(x, y, z, w.b("coal_block"))
        if (x - tx0) % 4 == 1:
            for sz in (-R - 1, R + 1):
                rad(w, x, 1, sz, 1, "xy")
    return w


def luftschiffwerft(seed, g=2):
    """Luftschiff-Werft: ein genieteter Stahlgitterturm mit Ankermast und Laufsteg, an dem ein kupferbraunes
    Luftschiff mit Holzgondel und Propellern festgemacht ist."""
    w = _welt(seed)
    u = U[g]
    H = r_(16 * u + 8)
    boden(w, -6, -6, r_(22 * u) + 6, 6)
    for (x, z) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False)
                    if y % 4 else w.b("polished_blackstone"))
    for y in range(4, H + 1, 4):
        for k in range(-2, 3):
            for (x, z) in ((k, -2), (k, 2), (-2, k), (2, k)):
                w.setze(x, y, z, w.b("polished_blackstone"))
    for y in range(1, H + 1):
        w.setze(0, y, -2, w.b("ladder", facing="north", waterlogged=False)) if False else None
    Ls = r_(4 * u + 2)
    for x in range(3, 3 + Ls):
        w.setze(x, H, 0, w.b("spruce_planks"))
        w.setze(x, H + 1, -1, zaun(w, "spruce", "x"))
        w.setze(x, H + 1, 1, zaun(w, "spruce", "x"))
    kegeldach(w, 0, 0, H + 1, 2, Dachmat(w, ["mcw:red_terracotta", "brick"]), form="kegel", eckig=True)
    Lh = r_(20 * u + 6)
    Rh = r_(3.5 * u + 1.5, 3)
    cx = 3 + Ls + Lh // 2 + 1
    cy = H + Rh - 1
    braun = Mix(w, [("brown_terracotta", 2), ("orange_terracotta", 1), ("brown_wool", 1)], zelle=2.0)
    huelle(w, cx, cy, 0, Lh, Rh, lambda x, y, z: w.b("waxed_cut_copper") if (x - cx) % 5 == 0 else braun(x, y, z))
    gy = cy - Rh - r_(2 * u + 1)
    for x in range(cx - Lh // 4, cx + Lh // 4 + 1):
        for z in (-1, 0, 1):
            w.setze(x, gy, z, w.b("spruce_planks"))
            if abs(z) == 1:
                w.setze(x, gy + 1, z, zaun(w, "spruce", "x"))
        if (x - cx) % 4 == 0:
            for y in range(gy + 1, cy - Rh + 1):
                w.setze(x, y, 0, w.b("chain", axis="y", waterlogged=False))
    for sz in (-Rh - 2, Rh + 2):
        propeller(w, cx - Lh // 3, cy - Rh // 2, sz, r_(1.5 * u, 1))
        for z in range(min(0, sz), max(0, sz) + 1):
            if abs(z) > Rh - 2:
                w.setze(cx - Lh // 3 + 1, cy - Rh // 2, z, w.b("polished_blackstone"))
    for x in range(3 + Ls, cx - Lh // 2 + 1):
        w.setze(x, H, 0, w.b("chain", axis="x", waterlogged=False))
    return w


def ornithopter(seed, g=1):
    """Ornithopter: eine schlanke Flugmaschine mit Holzrumpf, Glaskanzel, zwei Paar Schlagflügeln aus Segeltuch auf
    Messingrippen und einem Heckpropeller, auf einer Startplattform."""
    w = _welt(seed)
    u = U[g]
    L = r_(12 * u + 5)
    boden(w, -L, -L, L, L, (("smooth_stone", 2), ("polished_andesite", 1)))
    yb = r_(2 * u + 2)
    rohr(w, bez((-L * 0.6, yb, 0), (0, yb + 0.6, 0), (L * 0.5, yb, 0)), 1.6 * u + 0.6, 0.6 * u + 0.4,
         Mix(w, [("spruce_planks", 2), ("waxed_cut_copper", 1)], zelle=1.5))
    kugel(w, L * 0.25, yb + 1.2 * u, 0, 1.3 * u + 0.6, w.b("light_blue_stained_glass"), hohl=True)
    for k, xf in enumerate((0.1, -0.25)):
        x = round(L * xf)
        for sz in (-1, 1):
            spann = r_(L * (0.55 - 0.15 * k))
            for i in range(1, spann + 1):
                hoch = round(i * 0.35 * (1 if k == 0 else -0.3))
                for dx in range(-r_(2 * u, 1), r_(2 * u, 1) + 1):
                    w.setze(x + dx, yb + 1 + hoch, sz * i, w.b("white_wool") if dx else w.b("waxed_cut_copper"))
    propeller(w, round(-L * 0.6) - 1, yb, 0, r_(1.6 * u, 1))
    for (x, z) in ((round(L * 0.2), -1), (round(L * 0.2), 1), (round(-L * 0.3), 0)):
        for y in range(1, yb - r_(0.8 * u, 0)):
            w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
    return w


def dampftraktor(seed, g=1):
    """Dampftraktor: ein schwerer Straßendampfer mit riesigen eisenbeschlagenen Hinterrädern, liegendem Kessel,
    hohem Schornstein, Schwungrad und Fahrerstand mit Dach."""
    w = _welt(seed)
    u = U[g]
    L = r_(10 * u + 4)
    Rh, Rv = r_(3 * u + 1, 2), r_(1.8 * u + 0.6, 1)
    boden(w, -L, -L // 2 - 2, L, L // 2 + 2, (("dirt_path", 2), ("coarse_dirt", 2), ("gravel", 1)))
    B = r_(2 * u + 1, 2)
    for sz in (-B - 1, B + 1):
        rad(w, -L // 3, Rh + 1, sz, Rh, "xy", "polished_blackstone")
        rad(w, L // 2, Rv + 1, sz, Rv, "xy", "polished_blackstone")
    yk = Rh + 1
    zylinder(w, (-L // 3, yk, 0), (L // 2 + 1, yk, 0), B, kupfer(w), nieten=w.b("polished_blackstone"))
    schornstein(w, L // 2, yk + B, 0, r_(4 * u + 2), 0, "polished_blackstone")
    rad(w, 0, yk + B + 2, B + 1, r_(1.5 * u + 0.5, 1), "xy", "iron_block")
    for x in range(-L // 3 - r_(3 * u, 2), -L // 3 + 1):
        for z in range(-B, B + 1):
            w.setze(x, yk - 1, z, w.b("spruce_planks"))
            if (abs(z) == B) and x in (-L // 3 - r_(3 * u, 2), -L // 3):
                for y in range(yk, yk + r_(3 * u + 1)):
                    w.setze(x, y, z, zaun(w, "dark_oak"))
            w.setze(x, yk + r_(3 * u + 1), z, w.b("dark_oak_slab", type="bottom", waterlogged=False))
    return w


def kesselhaus(seed, g=1):
    """Kesselhaus: ein hohes Ziegelgebäude mit Bogenfenstern, durch das offene Tor sieht man große Kupferkessel,
    dicke Rohre führen über das Dach zu zwei rauchenden Schloten."""
    w = _welt(seed)
    u = U[g]
    B, T, H = r_(14 * u + 6), r_(9 * u + 5), r_(7 * u + 4)
    boden(w, -B // 2 - 4, -T // 2 - 4, B // 2 + 4, T // 2 + 4)
    x0, z0, x1, z1 = -B // 2, -T // 2, B // 2, T // 2
    zi = Mix(w, [("bricks", 4), ("mud_bricks", 1), ("granite", 1)])
    mauer(w, x0, z0, x1, z1, 1, H, zi, ecke=w.b("polished_blackstone"))
    for x in range(x0 + 2, x1 - 1, 3):
        for z, s in ((z0, "north"), (z1, "south")):
            fenster(w, x, 2, z, s, holz="dark_oak", hoehe=max(2, H - 3), laeden=False, blumen=0, bogen=True)
    for y in range(1, r_(3 * u + 2)):
        for x in range(-1, 2):
            w.bloecke.pop((x, y, z1), None)
    satteldach(w, x0, z0, x1, z1, H + 1, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]), first_x=True,
               traufe="dark_oak", giebel=zi)
    Rk = r_(1.8 * u + 0.6, 1)
    for k in range(2):
        x = round(-B / 4 + k * B / 2)
        zylinder(w, (x, 1, 0), (x, H - 1, 0), Rk, kupfer(w), nieten=w.b("polished_blackstone"))
    for k, x in enumerate((x0 - 2, x1 + 2)):
        schornstein(w, x, 1, 0, r_(H * 2.2), r_(0.8 * u, 1), "bricks")
        rohr(w, bez((round(-B / 4 + k * B / 2), H - 1, 0), (x * 0.7, H + 5 * u, 0), (x, H + 3, 0)), 0.6 * u + 0.4,
             0.6 * u + 0.4, w.b("waxed_cut_copper"))
    return w


def wasserturm(seed, g=1):
    """Wasserturm: ein genieteter Kupfertank mit spitzem Dach auf vier eisernen Stelzen mit Kreuzverstrebungen,
    Leiter, Umlauf und einem Auslassrohr."""
    w = _welt(seed)
    u = U[g]
    H = r_(10 * u + 5)
    R = r_(3.4 * u + 1.5, 2)
    boden(w, -R - 4, -R - 4, R + 4, R + 4)
    for (x, z) in ((-R + 1, -R + 1), (R - 1, -R + 1), (-R + 1, R - 1), (R - 1, R - 1)):
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                                 west="none", waterlogged=False) if y % 4 else w.b("polished_blackstone"))
    for y in range(4, H, 4):
        for k in range(-R + 1, R):
            for (x, z) in ((k, -R + 1), (k, R - 1), (-R + 1, k), (R - 1, k)):
                w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
    zylinder(w, (0, H + 1, 0), (0, H + r_(5 * u + 2), 0), R, kupfer(w), nieten=w.b("polished_blackstone"))
    for x in range(-R - 1, R + 2):
        for z in range(-R - 1, R + 2):
            if R + 0.3 < math.hypot(x, z) <= R + 1.4:
                w.setze(x, H + 1, z, w.b("spruce_planks"))
                w.setze(x, H + 2, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                         waterlogged=False))
    kegeldach(w, 0, 0, H + r_(5 * u + 2) + 1, R, Dachmat(w, ["mcw:cyan_terracotta", "prismarine_brick",
                                                              "dark_prismarine"]), form="kegel")
    for y in range(1, H + 1):
        w.setze(R, y, 0, w.b("ladder", facing="east", waterlogged=False)) if False else None
    for y in range(2, H + 1):
        w.setze(0, y, 0, w.b("waxed_cut_copper"))
    return w


def erfinderwerkstatt(seed, g=1):
    """Erfinderwerkstatt: ein schiefes Fachwerkhaus mit riesigen Zahnrädern an der Fassade, Kupferrohren, einem
    Glasdach-Atelier und einer knisternden Teslaspule auf dem Dach, Kram im Hof."""
    from feinbau import fachwerk, kamin, kram
    w = _welt(seed)
    u = U[g]
    B, T = r_(9 * u + 4), r_(7 * u + 3)
    boden(w, -B // 2 - 4, -T // 2 - 4, B // 2 + 6, T // 2 + 6)
    x0, z0, x1, z1 = -B // 2, -T // 2, B // 2, T // 2
    mauer(w, x0, z0, x1, z1, 1, 4, Mix(w, [("bricks", 3), ("stone_bricks", 1)]))
    fachwerk(w, x0 - 1, z0 - 1, x1 + 1, z1 + 1, 5, 8, Mix(w, [("white_terracotta", 2), ("calcite", 1)]),
             holz="dark_oak", abstand=2)
    satteldach(w, x0 - 1, z0 - 1, x1 + 1, z1 + 1, 9, Dachmat(w, ["mcw:brown_terracotta", "dark_oak", "spruce"]),
               first_x=True, traufe="dark_oak")
    tuer(w, 0, 1, z1, "south", holz="dark_oak")
    for x in range(x0 + 2, x1 - 1, 3):
        fenster(w, x, 2, z1, "south", holz="dark_oak", blumen=0.2) if abs(x) > 1 else None
    zahnrad(w, x0 + 2, 6, z1 + 2, r_(2.2 * u + 1, 2), "xy", "waxed_cut_copper", "gold_block")
    zahnrad(w, x0 + 2 + r_(4.2 * u + 2, 4), 4, z1 + 2, r_(1.6 * u + 0.6, 1), "xy", "waxed_copper_block",
            "polished_blackstone")
    yt = 9 + r_(B / 2 * 0.8)
    for y in range(yt, yt + r_(4 * u + 2)):
        w.setze(x1 - 2, y, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False) if y > yt + 1
                else w.b("waxed_copper_block"))
    kugel(w, x1 - 2, yt + r_(4 * u + 2), 0, r_(0.8 * u + 0.5, 1), w.b("waxed_cut_copper"))
    kram(w, x1 + 3, 1, z1 + 2, 6)
    rohr(w, bez((x1, 3, z0 + 1), (x1 + 3, 6, z0 + 1), (x1 + 2, 1, z0 + 3)), 0.5, 0.5, w.b("waxed_cut_copper"))
    return w


def teslaturm(seed, g=2):
    """Teslaturm: ein schlanker Gitterturm aus geschwärztem Stahl, umlaufen von Kupferspulen, gekrönt von einer
    großen Kupferkugel mit Blitzableitern, am Fuß ein Generatorhäuschen."""
    w = _welt(seed)
    u = U[g]
    H = r_(20 * u + 8)
    boden(w, -7, -7, 7, 7)
    for y in range(1, H + 1):
        b = max(1, round(3 * (1 - y / H) + 1))
        for (x, z) in ((-b, -b), (b, -b), (-b, b), (b, b)):
            w.setze(x, y, z, w.b("polished_blackstone"))
        if y % 3 == 0:
            for k in range(-b, b + 1):
                for (x, z) in ((k, -b), (k, b), (-b, k), (b, k)):
                    w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                         waterlogged=False))
        if y % 6 == 0:
            for x in range(-b - 1, b + 2):
                for z in range(-b - 1, b + 2):
                    if abs(x) == b + 1 or abs(z) == b + 1:
                        w.setze(x, y, z, w.b("waxed_cut_copper"))
    kugel(w, 0, H + r_(2 * u + 1), 0, r_(2.2 * u + 1, 2), w.b("waxed_copper_block"))
    for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        R = r_(2.2 * u + 1, 2)
        w.setze(dx * (R + 1), H + r_(2 * u + 1), dz * (R + 1), w.b("lightning_rod", facing={(1, 0): "east",
                                                                                           (-1, 0): "west",
                                                                                           (0, 1): "south",
                                                                                           (0, -1): "north"}[(dx, dz)],
                                                                   powered=False, waterlogged=False))
    w.setze(0, H + 2 * r_(2.2 * u + 1, 2) + 1, 0, w.b("lightning_rod", facing="up", powered=False,
                                                       waterlogged=False))
    mauer(w, 3, 3, 7, 7, 1, 3, Mix(w, [("bricks", 1)]))
    satteldach(w, 3, 3, 7, 7, 4, Dachmat(w, ["deepslate_tile"]), first_x=True, traufe="dark_oak")
    return w


def dampfmech(seed, g=2):
    """Dampfmech: ein zweibeiniger Messing-Laufroboter mit vernieteter Kanzel, Bullaugen, Rauchrohren auf dem Rücken,
    Greifarm und Kanone, die Kniegelenke mit Zahnrädern."""
    w = _welt(seed)
    u = U[g]
    boden(w, -r_(8 * u + 4), -r_(8 * u + 4), r_(8 * u + 4), r_(8 * u + 4),
          (("coarse_dirt", 2), ("gravel", 1), ("dirt", 1)))
    K = kupfer(w)
    for sz in (-1, 1):
        z = sz * r_(2.4 * u + 1)
        rohr(w, bez((0, 1, z + sz), (-2 * u, 4 * u + 2, z), (0, 8 * u + 3, z)), 0.9 * u + 0.4, 0.7 * u + 0.4,
             lambda *_: K(*_[:3]))
        kugel(w, -1.6 * u, 4.4 * u + 2, z, 0.9 * u + 0.6, w.b("gold_block"))
        for dx in range(-2, 3):
            for dz in range(-1, 2):
                w.setze(round(dx * u), 1, z + dz + sz, w.b("polished_blackstone"))
    yc = r_(8 * u + 3)
    R = r_(3.2 * u + 1.2, 2)
    kugel(w, 0, yc + R * 0.6, 0, R, lambda x, y, z: K(x, y, z), ry=R * 0.85)
    for k in range(3):
        a = -0.6 + k * 0.6
        w.setze(round(math.cos(a) * R), round(yc + R * 0.7), round(math.sin(a) * R), w.b("light_blue_stained_glass"))
    for k in range(2):
        schornstein(w, round(-R * 0.8), round(yc + R * 1.1), round((k - 0.5) * 2 * u), r_(3 * u + 1), 0,
                    "polished_blackstone")
    rohr(w, bez((0, yc + R * 0.5, -R), (1.5 * u, yc, -R - 2 * u), (4 * u, yc - 1, -R - 1)), 0.6 * u + 0.4,
         0.5 * u + 0.3, w.b("polished_blackstone"))
    rohr(w, bez((0, yc + R * 0.5, R), (2 * u, yc + R * 0.6, R + 1), (5 * u + 2, yc + R * 0.6, R + 1)),
         0.7 * u + 0.4, 0.7 * u + 0.4, w.b("iron_block"))
    return w


def uboot(seed, g=2):
    """U-Boot: ein genietetes Kupfer-Tauchboot mit Rückenflosse, Turm mit Bullaugen und Periskop, seitlichen
    Tiefenrudern und einem großen Heckpropeller, halb aufgetaucht."""
    w = _welt(seed)
    u = U[g]
    L = r_(22 * u + 8)
    R = r_(3 * u + 1.2, 2)
    for x in range(-L, L + 1):
        for z in range(-R * 3, R * 3 + 1):
            for y in (-2, -1, 0):
                w.setze(x, y, z, w.b("water", level=0))
    K = kupfer(w)
    for x in range(-L // 2, L // 2 + 1):
        t = x / (L / 2)
        r = R * max(0.0, 1 - min(1.0, abs(t)) ** 3) ** 0.5
        for y in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(y, z)
                if r - 1.2 < d <= r:
                    w.setze(x, y, z, w.b("polished_blackstone") if x % 4 == 0 else K(x, y, z))
    tx = round(L * 0.1)
    for y in range(R, R + r_(3 * u + 2)):
        for x in range(tx - 2, tx + 3):
            for z in (-1, 0, 1):
                rand = abs(x - tx) == 2 or abs(z) == 1
                if rand:
                    bull = y == R + 1 and z == 0 or (abs(z) == 1 and y == R + 1 and x == tx)
                    w.setze(x, y, z, w.b("light_blue_stained_glass") if bull else K(x, y, z))
    yp = R + r_(3 * u + 2)
    for y in range(yp, yp + 3):
        w.setze(tx, y, 0, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                              west="none", waterlogged=False))
    w.setze(tx + 1, yp + 2, 0, w.b("polished_blackstone"))
    for x in range(-L // 2 + 2, L // 3):
        if x % 5 == 0:
            for sz in (-1, 1):
                w.setze(x, 0, sz * (R), w.b("light_blue_stained_glass"))
    for sz in (-1, 1):
        for k in range(1, r_(2 * u + 1) + 1):
            w.setze(round(L * 0.3), 0, sz * (R + k), w.b("polished_blackstone_slab", type="bottom",
                                                         waterlogged=False))
    propeller(w, -L // 2 - 1, 0, 0, r_(1.8 * u + 0.5, 1))
    for y in range(0, R + r_(1.5 * u, 1) + 1):
        w.setze(-L // 2 + 1, y, 0, K(0, y, 0))
    return w


def frachtballon(seed, g=2):
    """Frachtballon: ein geflickter Heißluftballon mit Seilnetz trägt eine hölzerne Plattform mit Dampfmotor und
    zwei Propellern, darunter baumeln an Ketten Frachtkisten."""
    w = _welt(seed)
    u = U[g]
    R = r_(5 * u + 2, 3)
    yb = r_(12 * u + 6)
    flick = Mix(w, [("brown_wool", 2), ("orange_wool", 1), ("yellow_terracotta", 1), ("white_wool", 1),
                    ("red_wool", 1)], zelle=1.3)
    for x in range(-R - 1, R + 2):
        for y in range(-R - 1, int(R * 1.3) + 2):
            for z in range(-R - 1, R + 2):
                d = math.sqrt(x * x + (y / 1.3 if y > 0 else y / 1.0) ** 2 + z * z)
                if R - 1.1 < d <= R:
                    netz = (x + y) % 4 == 0 or (z - y) % 4 == 0
                    w.setze(x, yb + y, z, w.b("brown_terracotta") if netz else flick(x, y, z))
    yp = yb - R - r_(3 * u + 2)
    P = r_(2.5 * u + 1, 2)
    for x in range(-P, P + 1):
        for z in range(-P, P + 1):
            w.setze(x, yp, z, w.b("spruce_planks"))
            if abs(x) == P or abs(z) == P:
                w.setze(x, yp + 1, z, zaun(w, "spruce"))
    for (x, z) in ((-P, -P), (P, -P), (-P, P), (P, P)):
        for y in range(yp + 1, yb - R + 2):
            w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False))
    w.setze(0, yp + 1, 0, w.b("blast_furnace", facing="south", lit=True))
    w.setze(0, yp + 2, 0, w.b("polished_blackstone"))
    for sz in (-P - 2, P + 2):
        propeller(w, -P, yp + 2, sz, r_(1.4 * u, 1))
        for z in range(min(sz, 0), max(sz, 0) + 1):
            if abs(z) > P:
                w.setze(-P, yp + 2, z, w.b("polished_blackstone"))
    for k, (x, z) in enumerate(((-1, -1), (1, 1), (1, -1))):
        L = 2 + k * 2
        for y in range(yp - L, yp):
            w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False))
        w.setze(x, yp - L - 1, z, w.b("barrel", facing="up", open=False))
    return w


def raddampfer(seed, g=2):
    """Raddampfer: ein weißer Flussdampfer mit zwei Decks, Geländern, zwei hohen schwarzen Schloten mit Krone und
    großen seitlichen Schaufelrädern in Radkästen."""
    w = _welt(seed)
    u = U[g]
    L = r_(20 * u + 8)
    B = r_(3.2 * u + 2, 3)
    for x in range(-L, L + 1):
        for z in range(-B * 3, B * 3 + 1):
            for y in (-2, -1, 0):
                w.setze(x, y, z, w.b("water", level=0))
    for x in range(-L // 2, L // 2 + 1):
        bb = B if x < L // 3 else round(B * (1 - (x - L // 3) / (L / 6 + 1)))
        for z in range(-bb, bb + 1):
            for y in (-1, 0, 1):
                rand = abs(z) == bb or y == -1
                w.setze(x, y, z, w.b("red_terracotta") if y == -1 else w.b("white_concrete") if rand else
                        w.b("spruce_planks"))
            if abs(z) == bb:
                w.setze(x, 2, z, w.b("white_concrete_powder") if False else zaun(w, "birch"))
    for e, (xa, xb, h) in enumerate(((-L // 3, L // 4, 3), (-L // 4, L // 8, 3))):
        y0 = 2 + e * 4
        for x in range(xa, xb + 1):
            for z in range(-B + 1, B):
                for y in range(y0, y0 + h):
                    rand = abs(z) == B - 1 or x in (xa, xb)
                    if rand:
                        w.setze(x, y, z, w.b("glass_pane", north=False, south=False, east=True, west=True,
                                             waterlogged=False) if y == y0 + 1 and x % 2 else w.b("white_concrete"))
                w.setze(x, y0 + h, z, w.b("white_concrete"))
                if abs(z) == B - 1:
                    w.setze(x, y0 + h + 1, z, zaun(w, "birch"))
    for k in range(2):
        schornstein(w, round(-L * 0.05 + k * 3 * u + k), 2 + 8, 0 if True else 0, r_(6 * u + 3), 0,
                    "polished_blackstone") if k == 0 else schornstein(w, round(L * 0.05) + 1, 10, 0, r_(6 * u + 3),
                                                                       0, "polished_blackstone")
    Rr = r_(2.5 * u + 1, 2)
    for sz in (-B - 1, B + 1):
        rad(w, round(-L * 0.05), 1, sz, Rr, "xy", "red_concrete", "dark_oak")
        for x in range(round(-L * 0.05) - Rr - 1, round(-L * 0.05) + Rr + 2):
            w.setze(x, Rr + 2, sz, w.b("white_concrete"))
    return w


def dampfkran(seed, g=2):
    """Dampfkran am Kai: ein Portalkran auf Schienen mit Kesselhäuschen, Schornstein und langem genietetem Ausleger,
    an dem ein Lasthaken mit Kiste hängt, daneben Fässer."""
    from feinbau import kram
    w = _welt(seed)
    u = U[g]
    L = r_(14 * u + 6)
    boden(w, -6, -L, 8, L, (("stone_bricks", 2), ("polished_andesite", 1), ("cobblestone", 1)))
    for x in range(-6, 9):
        for z in range(L - 3, L + 1):
            for y in (0, -1):
                w.setze(x, y, z + 3, w.b("water", level=0))
    H = r_(4 * u + 3)
    for (x, z) in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b("polished_blackstone"))
    for x in range(-3, 4):
        for z in range(-3, 4):
            w.setze(x, H + 1, z, w.b("dark_oak_planks"))
    mauer(w, -2, -2, 2, 2, H + 2, H + 5, Mix(w, [("spruce_planks", 2), ("stripped_spruce_log", 1)]))
    satteldach(w, -2, -2, 2, 2, H + 6, Dachmat(w, ["mcw:red_terracotta", "brick"]), first_x=False, traufe="dark_oak")
    schornstein(w, -1, H + 6, -1, r_(3 * u + 2), 0, "polished_blackstone")
    for z in range(0, L + 1):
        y = H + 3 + round(z * 0.35)
        w.setze(0, y, z, w.b("iron_block") if z % 3 == 0 else w.b("polished_blackstone"))
        if z % 3 == 0:
            for y2 in range(H + 3, y):
                w.setze(0, y2, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                      waterlogged=False)) if z > 2 and y2 < H + 4 else None
    yt = H + 3 + round(L * 0.35)
    for y in range(4, yt):
        w.setze(0, y, L, w.b("chain", axis="y", waterlogged=False))
    w.setze(0, 3, L, w.b("barrel", facing="up", open=False))
    kram(w, 5, 1, -4, 5)
    return w


def messingteleskop(seed, g=2):
    """Messingteleskop: ein riesiges Messingfernrohr auf einem drehbaren Zahnkranz-Gestell erhebt sich über einer
    Ziegelplattform, mit Okular-Kanzel, Treppe und Sternkarten-Pult."""
    w = _welt(seed)
    u = U[g]
    R = r_(5 * u + 3, 4)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                for y in range(0, 3):
                    w.setze(x, y, z, w.b("bricks") if y < 2 or math.hypot(x, z) > R - 1 else
                            w.b("polished_andesite"))
    zahnrad(w, 0, 3, 0, r_(3 * u + 1, 2), "xz" if False else "xy", "waxed_cut_copper", "gold_block") if False else None
    for x in range(-r_(3 * u + 1, 2), r_(3 * u + 1, 2) + 1):
        for z in range(-r_(3 * u + 1, 2), r_(3 * u + 1, 2) + 1):
            d = math.hypot(x, z)
            if r_(3 * u + 1, 2) - 1 < d <= r_(3 * u + 1, 2):
                w.setze(x, 3, z, w.b("waxed_cut_copper") if (x + z) % 2 else w.b("gold_block"))
    for (x, z) in ((-2, 0), (2, 0)):
        for y in range(3, 3 + r_(4 * u + 2)):
            w.setze(x, y, z, w.b("polished_blackstone"))
    ym = 3 + r_(4 * u + 2)
    Lt = 12 * u + 5
    a = 0.6
    p0 = (-math.cos(a) * Lt * 0.35, ym - math.sin(a) * Lt * 0.35, 0)
    p1 = (math.cos(a) * Lt * 0.65, ym + math.sin(a) * Lt * 0.65, 0)
    zylinder(w, p0, p1, 1.4 * u + 0.8, kupfer(w), nieten=w.b("gold_block"), abstand=4)
    kugel(w, p1[0], p1[1], p1[2], 1.6 * u + 0.8, w.b("light_blue_stained_glass"), hohl=True)
    w.setze(round(p0[0]) - 1, round(p0[1]), 0, w.b("gold_block"))
    w.setze(-R + 2, 3, 0, w.b("lectern", facing="east", has_book=True, powered=False))
    return w


def bahnhof(seed, g=2):
    """Bahnhof: eine Bahnsteighalle mit gewölbtem Glasdach auf gusseisernen Bögen, Bahnhofsuhr, Bänken, Laternen
    und zwei Gleisen, daneben das Empfangsgebäude."""
    w = _welt(seed)
    u = U[g]
    L = r_(18 * u + 8)
    B = r_(5 * u + 4, 5)
    boden(w, -L // 2 - 2, -B - 6, L // 2 + 2, B + 2, (("smooth_stone", 2), ("polished_andesite", 1)))
    for dz in (-B + 2, B - 2):
        gleis(w, -L // 2 - 2, L // 2 + 2, dz)
    for x in range(-L // 2, L // 2 + 1):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("smooth_stone_slab", type="bottom", waterlogged=False))
        rippe = x % 4 == 0
        for z in range(-B, B + 1):
            y = r_(5 * u + 3) + round(math.sqrt(max(0, B * B - z * z)) * 0.6)
            w.setze(x, y, z, w.b("polished_blackstone") if rippe else w.b("glass"))
        if rippe:
            for z in (-B, B):
                for y in range(1, r_(5 * u + 3)):
                    w.setze(x, y, z, w.b("polished_blackstone_wall", up=True, north="none", south="none",
                                         east="none", west="none", waterlogged=False))
    for x in range(-L // 2 + 3, L // 2 - 2, 6):
        w.setze(x, 2, 0, treppe(w, "spruce", "north"))
        w.setze(x + 2, 2, 0, w.b("lantern", hanging=False, waterlogged=False))
    w.setze(0, r_(5 * u + 3) - 1, 0, w.b("gold_block"))
    mauer(w, -L // 4, -B - 6, L // 4, -B - 1, 1, 5, Mix(w, [("bricks", 3), ("smooth_sandstone", 1)]))
    satteldach(w, -L // 4, -B - 6, L // 4, -B - 1, 6, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]),
               first_x=True, traufe="dark_oak")
    tuer(w, 0, 1, -B - 1, "south", holz="dark_oak")
    return w


def foerderturm(seed, g=2):
    """Förderturm: ein genietetes Stahlgerüst mit zwei großen Seilscheiben auf der Spitze, schräge Strebe zum
    Maschinenhaus mit Schlot, Förderkorb im Schacht und Loren auf Schienen."""
    w = _welt(seed)
    u = U[g]
    H = r_(14 * u + 6)
    boden(w, -6, -6, r_(10 * u + 8), 6, (("gravel", 2), ("coarse_dirt", 1), ("cobblestone", 1)))
    for (x, z) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b("polished_blackstone"))
    for y in range(3, H + 1, 3):
        for k in range(-2, 3):
            for (x, z) in ((k, -2), (k, 2), (-2, k), (2, k)):
                w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
    Rs = r_(2 * u + 1, 2)
    for sz in (-1, 1):
        rad(w, 0, H + Rs, sz, Rs, "xy", "red_concrete", "dark_oak")
    mx = r_(8 * u + 5)
    for i in range(mx + 1):
        y = round(H - (H - 4) * i / mx)
        w.setze(i, y, 0, w.b("polished_blackstone"))
    mauer(w, mx - 1, -3, mx + 5, 3, 1, 5, Mix(w, [("bricks", 3), ("stone_bricks", 1)]))
    satteldach(w, mx - 1, -3, mx + 5, 3, 6, Dachmat(w, ["deepslate_tile"]), first_x=False, traufe="dark_oak")
    schornstein(w, mx + 5, 1, 0, r_(H * 1.0), 1, "bricks")
    for y in range(1, H):
        w.setze(0, y, 0, w.b("chain", axis="y", waterlogged=False))
    for x in range(-1, 2):
        for z in range(-1, 2):
            w.setze(x, 3, z, w.b("iron_block") if (x or z) else w.b("chain", axis="y", waterlogged=False))
    return w


def seilbahnstation(seed, g=2):
    """Seilbahnstation: ein Holzhaus mit großem Seilrad unter dem Dach, ein Tragseil führt zu einem eisernen Mast,
    daran hängt eine kleine Gondel mit Fenstern."""
    w = _welt(seed)
    u = U[g]
    L = r_(20 * u + 8)
    boden(w, -6, -6, L + 4, 6, (("grass_block", 3), ("coarse_dirt", 1)))
    mauer(w, -4, -4, 4, 4, 1, 5, Mix(w, [("spruce_planks", 2), ("stripped_spruce_log", 1)]))
    satteldach(w, -4, -4, 4, 4, 6, Dachmat(w, ["spruce", "dark_oak"]), first_x=True, traufe="spruce")
    rad(w, 4, 6, 0, 2, "zy" if False else "xy", "polished_blackstone")
    H = r_(10 * u + 6)
    for y in range(1, H + 1):
        w.setze(L, y, 0, w.b("polished_blackstone"))
        if y % 3 == 0:
            for dz in (-1, 1):
                w.setze(L, y, dz, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                      waterlogged=False))
    for i in range(5, L + 1):
        t = (i - 5) / (L - 5)
        y = round(6 + (H - 6) * t - 2 * math.sin(math.pi * t))
        w.setze(i, y, 0, w.b("chain", axis="x", waterlogged=False))
    gx = round(5 + (L - 5) * 0.45)
    t = 0.45
    gy = round(6 + (H - 6) * t - 2 * math.sin(math.pi * t))
    for y in range(gy - 2, gy):
        w.setze(gx, y, 0, w.b("chain", axis="y", waterlogged=False))
    for x in range(gx - 2, gx + 3):
        for z in (-1, 0, 1):
            for y in range(gy - 6, gy - 2):
                rand = abs(x - gx) == 2 or abs(z) == 1 or y in (gy - 6, gy - 3)
                if rand:
                    w.setze(x, y, z, w.b("glass_pane", north=False, south=False, east=True, west=True,
                                         waterlogged=False) if y == gy - 5 and abs(z) == 1 else
                            w.b("red_concrete"))
    return w


def dampfkutsche(seed, g=1):
    """Dampfkutsche: eine elegante Kutsche mit Messingbeschlägen und großen Speichenrädern, hinten ein stehender
    Dampfkessel mit Schlot, vorn eine Laterne und ein Kutschbock."""
    w = _welt(seed)
    u = U[g]
    L = r_(9 * u + 4)
    B = r_(2 * u + 1, 2)
    boden(w, -L, -B - 4, L, B + 4, (("cobblestone", 2), ("stone_bricks", 1)))
    R1, R2 = r_(2 * u + 1, 2), r_(1.4 * u + 0.6, 1)
    for sz in (-B - 1, B + 1):
        rad(w, -L // 3, R1 + 1, sz, R1, "xy", "polished_blackstone")
        rad(w, L // 3, R2 + 1, sz, R2, "xy", "polished_blackstone")
    yb = R1 + 1
    for x in range(-L // 2, L // 3 + 1):
        for z in range(-B, B + 1):
            for y in range(yb, yb + r_(3 * u + 2)):
                rand = abs(z) == B or x in (-L // 2, L // 3)
                if rand:
                    fen = y == yb + 1 and abs(z) == B and x % 2 == 0
                    w.setze(x, y, z, w.b("glass_pane", north=False, south=False, east=True, west=True,
                                         waterlogged=False) if fen else w.b("dark_oak_planks" if y > yb else
                                                                           "waxed_cut_copper"))
            w.setze(x, yb + r_(3 * u + 2), z, w.b("dark_oak_slab", type="bottom", waterlogged=False))
    zylinder(w, (-L // 2 - 2, yb, 0), (-L // 2 - 2, yb + r_(3 * u + 2), 0), B - 0.4, kupfer(w),
             nieten=w.b("gold_block"))
    schornstein(w, -L // 2 - 2, yb + r_(3 * u + 2) + 1, 0, r_(2 * u + 1), 0, "polished_blackstone")
    w.setze(L // 3 + 2, yb + 1, 0, w.b("lantern", hanging=False, waterlogged=False))
    for z in range(-B + 1, B):
        w.setze(L // 3 + 1, yb + 1, z, treppe(w, "dark_oak", "west"))
    return w


def fliegende_festung(seed, g=3):
    """Fliegende Festung: ein gewaltiges Luftschiff mit zwei Hüllen, darunter ein gepanzertes Festungsdeck mit
    Geschütztürmen, Brücke, Schornsteinen und sechs Propellern."""
    w = _welt(seed)
    u = U[g]
    L = r_(26 * u + 10)
    R = r_(4 * u + 2, 3)
    yh = r_(14 * u + 8)
    M = Mix(w, [("light_gray_concrete", 2), ("gray_concrete", 1), ("light_gray_wool", 1)], zelle=2)
    for sz in (-R - 1, R + 1):
        huelle(w, 0, yh, sz, L, R, lambda x, y, z: w.b("waxed_cut_copper") if x % 6 == 0 else M(x, y, z))
    yd = yh - R - 2
    Bd = R + 3
    for x in range(-L // 3, L // 3 + 1):
        for z in range(-Bd, Bd + 1):
            w.setze(x, yd, z, w.b("polished_blackstone") if abs(z) == Bd else w.b("dark_oak_planks"))
            w.setze(x, yd - 1, z, w.b("polished_deepslate"))
            if abs(z) == Bd:
                w.setze(x, yd + 1, z, w.b("polished_blackstone_wall", up=True, north="none", south="none",
                                          east="none", west="none", waterlogged=False))
        if x % 6 == 0:
            for y in range(yd + 1, yh - R + 1):
                for z in (-R - 1, R + 1):
                    w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False))
    for k, x in enumerate((-L // 4, L // 4)):
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                w.setze(x + dx, yd + 1, dz, w.b("polished_blackstone"))
        w.setze(x, yd + 2, 0, w.b("polished_blackstone"))
        for i in range(1, 4):
            w.setze(x + (i if k else -i), yd + 2, 0, w.b("iron_block"))
    mauer(w, -2, -2, 2, 2, yd + 1, yd + 4, Mix(w, [("polished_blackstone_bricks", 2), ("iron_block", 1)]))
    for x in range(-1, 2):
        w.setze(x, yd + 3, -2, w.b("glass"))
        w.setze(x, yd + 3, 2, w.b("glass"))
    schornstein(w, -L // 6, yd + 1, 0, r_(4 * u + 2), 0, "polished_blackstone")
    for k in range(3):
        x = -L // 3 + k * (L // 3)
        for sz in (-Bd - 2, Bd + 2):
            propeller(w, x, yd - 1, sz, r_(1.5 * u, 1))
            for z in range(min(sz, 0), max(sz, 0) + 1):
                if abs(z) > Bd:
                    w.setze(x, yd - 1, z, w.b("polished_blackstone"))
    return w


def gasometer(seed, g=2):
    """Gasometer: ein großer zylindrischer Gasbehälter aus vernieteten Kupferplatten in einem Gerüst aus
    gusseisernen Säulen und Ringen, mit Wendeltreppe und Ventilrädern."""
    w = _welt(seed)
    u = U[g]
    R = r_(6 * u + 3, 4)
    H = r_(10 * u + 5)
    boden(w, -R - 4, -R - 4, R + 4, R + 4)
    zylinder(w, (0, 1, 0), (0, H, 0), R - 1, kupfer(w), nieten=w.b("polished_blackstone"), abstand=3)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d <= R - 1:
                w.setze(x, H + 1, z, w.b("waxed_cut_copper") if d > R - 3 else w.b("waxed_exposed_cut_copper"))
    n = 8 + g * 2
    for k in range(n):
        a = k / n * 6.283
        x, z = round(math.cos(a) * (R + 1)), round(math.sin(a) * (R + 1))
        for y in range(1, H + 4):
            w.setze(x, y, z, w.b("polished_blackstone"))
    for y in (H // 2, H + 3):
        for k in range(int(R * 14)):
            a = k / (R * 14) * 6.283
            w.setze(round(math.cos(a) * (R + 1)), y, round(math.sin(a) * (R + 1)), w.b("iron_block"))
    for i in range(H * 3):
        a = i / (H * 3) * 6.283 * 1.5
        y = 1 + i // 3
        w.setze(round(math.cos(a) * (R + 2)), y, round(math.sin(a) * (R + 2)),
                w.b("polished_blackstone_slab", type="top", waterlogged=False))
    rad(w, R + 2, 2, 0, 1, "xy", "red_concrete")
    return w


STEAMPUNK2 = {
    "dampflok": ("Dampflok mit Tender", dampflok),
    "luftschiffwerft": ("Luftschiff-Werft", luftschiffwerft),
    "ornithopter": ("Ornithopter", ornithopter),
    "dampftraktor": ("Dampftraktor", dampftraktor),
    "kesselhaus": ("Kesselhaus", kesselhaus),
    "wasserturm": ("Wasserturm", wasserturm),
    "erfinderwerkstatt": ("Erfinderwerkstatt", erfinderwerkstatt),
    "teslaturm": ("Teslaturm", teslaturm),
    "dampfmech": ("Dampfmech", dampfmech),
    "uboot": ("Kupfer-U-Boot", uboot),
    "frachtballon": ("Frachtballon", frachtballon),
    "raddampfer": ("Raddampfer", raddampfer),
    "dampfkran": ("Dampfkran am Kai", dampfkran),
    "messingteleskop": ("Messingteleskop", messingteleskop),
    "bahnhof": ("Bahnhof mit Glasdach", bahnhof),
    "foerderturm": ("Förderturm", foerderturm),
    "seilbahnstation": ("Seilbahnstation", seilbahnstation),
    "dampfkutsche": ("Dampfkutsche", dampfkutsche),
    "fliegende_festung": ("Fliegende Festung", fliegende_festung),
    "gasometer": ("Gasometer", gasometer),
}

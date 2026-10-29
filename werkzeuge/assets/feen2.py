"""Feenstadt – Erweiterung auf 20: Teekannenhaus, Eichelhaus, Glockenblumenlaternen, Libellenhafen,
Tautropfenbrunnen, Seerosenmarkt, Kürbiskutsche, Stiefelhaus, Regenbogenquelle, Schmetterlingspavillon,
Moospolsterdorf, Pusteblumenturm."""

from __future__ import annotations

import math

import numpy as np

import pracht as P
from lib import Rauschen, laub
from pracht import Mat, gelaende
from skulptur import Skulptur, dreh_y, dreh_z, ell, kap, kreisrand, scheibe, torus
from weltwunder import bl, hohl, sk

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    from lib import Welt
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


BLUMEN = ["poppy", "dandelion", "allium", "azure_bluet", "pink_tulip", "oxeye_daisy", "cornflower",
          "lily_of_the_valley", "blue_orchid"]


def feenwiese(w, R, cx=0, cz=0, dichte=0.5):
    r1 = Rauschen(w, 3)
    rng = w.rng
    for x, z in scheibe(R, cx, cz):
        v = r1(x, 0, z)
        w.setze(x, 0, z, w.b("moss_block") if v < 0.3 else w.b("grass_block", snowy=False), ueberschreiben=False)
        if w.frei(x, 1, z):
            r = rng.random()
            if r < dichte * 0.35:
                w.setze(x, 1, z, w.b(BLUMEN[int(rng.integers(len(BLUMEN)))]))
            elif r < dichte * 0.5:
                w.setze(x, 1, z, w.b("pink_petals", flower_amount=int(rng.integers(1, 5)), facing="north"))
            elif r < dichte * 0.6:
                w.setze(x, 1, z, w.b("grass"))


def glimmer(w, R, n, y0=2, y1=8, cx=0, cz=0):
    rng = w.rng
    for i in range(n):
        a = rng.random() * 2 * math.pi
        d = rng.random() * R
        w.setze(round(cx + math.cos(a) * d), int(rng.integers(y0, y1 + 1)), round(cz + math.sin(a) * d),
                w.b("end_rod", facing="up") if rng.random() < 0.5 else w.b("glowstone") if rng.random() < 0.3 else
                w.b("pearlescent_froglight", axis="y"))


def tuer_fenster(w, x, y, z, richtung="south", holz="oak"):
    w.setze(x, y, z, w.b(f"{holz}_door", facing=richtung, half="lower", hinge="left", open=False, powered=False))
    w.setze(x, y + 1, z, w.b(f"{holz}_door", facing=richtung, half="upper", hinge="left", open=False, powered=False))


def teekannenhaus(seed, g=1):
    """Teekannenhaus: ein Haus in Form einer riesigen Porzellan-Teekanne mit Blumenmuster, Tülle als Erker, Henkel
    als Treppe und Deckel mit Knauf als Dach; davor Tassen als Sitzplätze."""
    w = _welt(seed)
    u = U[g]
    s = 0.6 * u + 0.4
    feenwiese(w, _r(10 * s + 5))
    farbe = ["white_concrete", "light_blue_concrete", "white_terracotta"] if _stil(seed) == 0 else \
        ["white_concrete", "pink_concrete", "white_terracotta"]
    S = Skulptur(w, s)
    S.mat("k", lambda x, y, z, lx, ly, lz: w.b(farbe[1]) if (abs(ly - 5) < 0.6 or (int(lx + lz + ly) % 7 == 0))
          else w.b(farbe[0]))
    S.mat("d", lambda x, y, z, *_: w.b(farbe[1]))
    S.mat("g", bl(w, "gold_block"))
    S.mat("f", bl(w, "light_blue_stained_glass"))
    S.plus(lambda X, Y, Z: ((X / 7) ** 2 + ((Y - 5) / 5.5) ** 2 + (Z / 7) ** 2 < 1) & (Y >= 0), "k")
    S.minus(lambda X, Y, Z: ((X / 6) ** 2 + ((Y - 5) / 4.5) ** 2 + (Z / 6) ** 2 < 1) & (Y >= 1))
    S.plus(lambda X, Y, Z: (np.sqrt(X * X + Z * Z) < 5.2 - (Y - 10) * 0.8) & (Y >= 10) & (Y < 12.5), "d")
    S.plus(ell(0, 13.2, 0, 1.0, 1.0, 1.0), "g")
    S.plus(kap((6, 4, 0), (11, 9, 0), 1.6, 0.8), "k")
    S.plus(lambda X, Y, Z: (np.abs(np.sqrt((X + 7) ** 2 + (Y - 5) ** 2) - 3.5) < 0.8) & (np.abs(Z) < 0.8) & (X < -6),
           "k")
    for a in range(4):
        ang = a * math.pi / 2 + 0.4
        S.plus(ell(math.cos(ang) * 6.8, 6, math.sin(ang) * 6.8, 0.4, 1.0, 0.8), "f")
    S.rendern((-12, -1, -9), (13, 15, 9), versatz=(0.5, 1.01, 0.5))
    tuer_fenster(w, 0, 1, round(6.5 * s), "south", "birch")
    for i in range(3):
        cx, cz = round((i - 1) * 4 * s), round(10 * s + 2)
        for x, z in kreisrand(1.2, cx, cz):
            w.setze(x, 1, z, w.b(farbe[0]))
        w.setze(cx, 1, cz, w.b("brown_carpet"))
    glimmer(w, 10 * s, 8)
    hohl(w, 2)
    return w


def eichelhaus(seed, g=1):
    """Eichelhaus: eine riesige Eichel mit geschuppter Hütchen-Kappe als Dach, runde Fenster, ein kleiner Stiel als
    Schornstein, umgeben von Eichenlaub und Pilzen."""
    w = _welt(seed)
    u = U[g]
    s = 0.6 * u + 0.4
    feenwiese(w, _r(9 * s + 5))
    S = Skulptur(w, s)
    S.mat("n", lambda x, y, z, *_: w.b("orange_terracotta") if (x + y) % 4 else w.b("terracotta"))
    S.mat("h", lambda x, y, z, lx, ly, lz: w.b("brown_terracotta") if int(ly * 2 + math.atan2(lz, lx) * 3) % 2
          else w.b("dark_oak_planks"))
    S.mat("s", bl(w, "dark_oak_log"))
    S.plus(lambda X, Y, Z: ((X / 5.5) ** 2 + ((Y - 6) / 7) ** 2 + (Z / 5.5) ** 2 < 1) & (Y >= 0) & (Y < 9), "n")
    S.minus(lambda X, Y, Z: ((X / 4.5) ** 2 + ((Y - 6) / 6) ** 2 + (Z / 4.5) ** 2 < 1) & (Y >= 1) & (Y < 9))
    S.plus(lambda X, Y, Z: ((X / 6.6) ** 2 + ((Y - 9) / 4.5) ** 2 + (Z / 6.6) ** 2 < 1) & (Y >= 8.5), "h")
    S.plus(kap((0, 13, 0), (0.6, 16, 0.3), 0.8, 0.6), "s")
    S.rendern((-8, -1, -8), (8, 17, 8), versatz=(0.5, 1.01, 0.5))
    tuer_fenster(w, 0, 1, round(5.2 * s), "south", "spruce")
    for k in range(5):
        a = k / 5 * 2 * math.pi
        w.setze(round(math.cos(a) * (6 * s + 3)), 1, round(math.sin(a) * (6 * s + 3)),
                w.b("red_mushroom") if k % 2 else laub(w, "oak"))
    hohl(w, 2)
    return w


def glockenblumen(seed, g=1):
    """Glockenblumen-Laternen: eine Gruppe übergroßer, nickender Glockenblumen in Blau und Violett, in deren
    Blüten Lichter glimmen; Moos und Farn darunter."""
    w = _welt(seed)
    u = U[g]
    R = _r(6 * u + 5)
    feenwiese(w, R + 2)
    rng = w.rng
    n = 4 + 2 * g
    for i in range(n):
        a = i * 2.39996
        d = R * 0.7 * math.sqrt((i + 0.5) / n)
        cx, cz = math.cos(a) * d, math.sin(a) * d
        H = 5 + rng.random() * 4 * u
        farbe = ["blue_concrete", "light_blue_concrete", "purple_concrete", "magenta_concrete"][i % 4]
        S = Skulptur(w, 1.0)
        S.mat("g", bl(w, "green_concrete"))
        S.mat("b", bl(w, farbe))
        S.mat("l", bl(w, "shroomlight"))
        neig = rng.random() * 2 * math.pi
        top = (math.cos(neig) * 2, H, math.sin(neig) * 2)
        S.plus(kap((0, 0, 0), (0, H * 0.7, 0), 0.4, 0.35), "g")
        S.plus(kap((0, H * 0.7, 0), top, 0.35, 0.3), "g")
        S.plus(lambda X, Y, Z, t=top: (np.sqrt((X - t[0]) ** 2 + (Z - t[2]) ** 2) < 1.0 + (t[1] - Y) * 0.5) &
               (Y < t[1]) & (Y > t[1] - 2.8) & (np.sqrt((X - t[0]) ** 2 + (Z - t[2]) ** 2) > (t[1] - Y) * 0.5 - 0.3), "b")
        S.plus(ell(top[0], top[1] - 1.5, top[2], 0.5, 0.5, 0.5), "l")
        S.rendern((-4, 0, -4), (4, H + 2, 4), versatz=(cx + 0.5, 1.01, cz + 0.5))
    return w


def libellenhafen(seed, g=1):
    """Libellenhafen: Landeplattformen aus Seerosenblättern auf hohen Schilfhalmen über einem Teich, Leitern aus
    Grashalmen und eine Libellen-Skulptur mit gläsernen Flügeln."""
    w = _welt(seed)
    u = U[g]
    R = _r(8 * u + 5)
    feenwiese(w, R + 3)
    for x, z in scheibe(R * 0.75):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("mud"))
        if w.rng.random() < 0.12:
            w.setze(x, 1, z, w.b("lily_pad"))
    for i in range(3 + g):
        a = i / (3 + g) * 2 * math.pi
        cx, cz = round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)
        H = 4 + i % 3 + g
        for y in range(1, H):
            w.setze(cx, y, cz, w.b("lime_concrete") if y % 3 else w.b("green_concrete"))
        for x, z in scheibe(2.2, cx, cz):
            w.setze(x, H, z, w.b("lime_concrete") if (x + z) % 3 else w.b("green_concrete"))
        w.setze(cx, H + 1, cz, w.b("pink_petals", flower_amount=4, facing="north"))
    s = 0.4 * u + 0.25
    S = Skulptur(w, s)
    S.mat("k", lambda x, y, z, *_: w.b("cyan_concrete") if (x + y + z) % 2 else w.b("blue_concrete"))
    S.mat("f", lambda x, y, z, *_: w.b("light_blue_stained_glass") if (x + z) % 3 else w.b("white_stained_glass"))
    S.mat("a", bl(w, "green_concrete"))
    S.plus(kap((-6, 0, 0), (3, 0, 0), 0.5, 0.9), "k")
    S.plus(ell(4, 0, 0, 1.2, 1.0, 1.2), "a")
    for sx in (-0.5, 1.5):
        for sz in (-1, 1):
            S.plus(lambda X, Y, Z, sx=sx, sz=sz: (((X - sx) / 1.4) ** 2 + ((Z - sz * 4.5) / 4.0) ** 2 < 1) &
                   (np.abs(Y - 0.3) < 0.5), "f")
    S.rendern((-7, -2, -6), (6, 3, 6), versatz=(0.5, 8.5 + g, 0.5), dreh=dreh_y(0.6))
    return w


def tautropfenbrunnen(seed, g=1):
    """Tautropfenbrunnen: ein Kleeblatt-Becken aus Moosstein, darüber schweben riesige Tautropfen aus Glas mit
    leuchtendem Kern, die aus einer Blütenschale fallen."""
    w = _welt(seed)
    u = U[g]
    R = 4 * u + 3
    feenwiese(w, _r(R + 5))
    for k in range(3):
        a = k / 3 * 2 * math.pi
        for x, z in scheibe(R * 0.55, round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("prismarine_bricks"))
    for x, z in scheibe(R + 0.5):
        if (x, 0, z) not in w.bloecke or w.P.name(w.bloecke[(x, 0, z)]) != "minecraft:water":
            if math.hypot(x, z) > R - 1.5:
                w.setze(x, 1, z, w.b("mossy_stone_bricks"))
    S = Skulptur(w, 1.0)
    S.mat("g", bl(w, "light_blue_stained_glass"))
    S.mat("l", bl(w, "sea_lantern"))
    S.mat("p", bl(w, "pink_concrete"))
    S.mat("s", bl(w, "green_concrete"))
    Hs = 6 * u + 4
    S.plus(kap((0, 0, 0), (0, Hs, 0), 0.5, 0.5), "s")
    S.plus(lambda X, Y, Z: (np.sqrt(X * X + Z * Z) < 0.5 + (Y - Hs) * 1.2) & (Y > Hs) & (Y < Hs + 2.5) &
           (np.sqrt(X * X + Z * Z) > (Y - Hs) * 1.2 - 0.4), "p")
    for i in range(3 + g):
        a = i * 2.1
        tx, tz, ty = math.cos(a) * R * 0.45, math.sin(a) * R * 0.45, Hs - 1 - i * 1.5
        S.plus(lambda X, Y, Z, tx=tx, ty=ty, tz=tz: ((X - tx) ** 2 + (Z - tz) ** 2 + np.where(Y > ty, ((Y - ty) * 0.6) ** 2,
                                                                                         (Y - ty) ** 2) < 2.6 ** 2), "g")
        S.plus(ell(tx, ty, tz, 0.8, 0.8, 0.8), "l")
    S.rendern((-R - 2, 0, -R - 2), (R + 2, Hs + 4, R + 2), versatz=(0.5, 1.01, 0.5))
    return w


def seerosenmarkt(seed, g=2):
    """Seerosenmarkt: auf riesigen Seerosenblättern in einem Teich stehen kleine Marktstände mit Blütendächern,
    verbunden durch Stege aus Zweigen; Laternen aus Glühwürmchenglas."""
    w = _welt(seed)
    u = U[g]
    R = _r(10 * u + 6)
    feenwiese(w, R + 3)
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("mud"))
    n = 4 + g
    pos = []
    for i in range(n):
        a = i / n * 2 * math.pi + 0.3
        cx, cz = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        rr = 2.5 + u
        for x, z in scheibe(rr, cx, cz):
            if not (abs(math.atan2(z - cz, x - cx) - a - math.pi) < 0.25 and math.hypot(x - cx, z - cz) > 1):
                w.setze(x, 1, z, w.b("lime_concrete") if math.hypot(x - cx, z - cz) > rr - 1 else
                        w.b("green_concrete"))
        farbe = ["pink", "yellow", "light_blue", "magenta", "orange"][i % 5]
        for y in (2, 3, 4):
            for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                w.setze(cx + dx, y, cz + dz, w.b("birch_fence", north=False, south=False, east=False, west=False,
                                                 waterlogged=False))
        for x, z in scheibe(2.0, cx, cz):
            w.setze(x, 5, z, w.b(f"{farbe}_concrete") if (x + z) % 2 else w.b(f"{farbe}_terracotta"))
        w.setze(cx, 2, cz, w.b("barrel", facing="up", open=False))
        pos.append((cx, cz))
    for (ax, az), (bx, bz) in zip(pos, pos[1:] + pos[:1]):
        n2 = max(abs(bx - ax), abs(bz - az))
        for k in range(n2 + 1):
            t = k / n2
            w.setze(round(ax + (bx - ax) * t), 1, round(az + (bz - az) * t), w.b("birch_slab", type="top",
                                                                                 waterlogged=False),
                    ueberschreiben=False)
    w.setze(0, 1, 0, w.b("lily_pad"))
    glimmer(w, R, 10 + 4 * g, 3, 8)
    return w


def kuerbiskutsche(seed, g=1):
    """Kürbiskutsche: eine Kutsche aus einem ausgehöhlten Riesenkürbis mit goldenen Rankenrädern, Laternen, einem
    Kutschbock und Rankenranken."""
    w = _welt(seed)
    u = U[g]
    s = 0.6 * u + 0.4
    feenwiese(w, _r(9 * s + 5))
    S = Skulptur(w, s)
    S.mat("k", lambda x, y, z, lx, ly, lz: w.b("orange_concrete") if int(math.atan2(lz, lx) * 4) % 2 else
          w.b("orange_terracotta"))
    S.mat("g", bl(w, "gold_block"))
    S.mat("s", bl(w, "green_concrete"))
    S.mat("f", bl(w, "yellow_stained_glass"))
    S.plus(ell(0, 6, 0, 6, 5, 5), "k")
    S.minus(ell(0, 6, 0, 5, 4, 4))
    S.minus(lambda X, Y, Z: (np.abs(X) < 2.2) & (Y > 4) & (Y < 9) & (np.abs(Z) > 3))
    S.plus(lambda X, Y, Z: (np.abs(X) < 2.2) & (Y > 4) & (Y < 9) & (np.abs(Z) > 4) & (np.abs(Z) < 4.6), "f")
    S.plus(kap((0, 11, 0), (1.2, 13.5, 0.5), 0.6, 0.4), "s")
    for sx in (-4.5, 4.5):
        for sz in (-5.3, 5.3):
            S.plus(lambda X, Y, Z, sx=sx, sz=sz: (np.abs(np.sqrt((X - sx) ** 2 + (Y - 2.4) ** 2) - 2.2) < 0.45) &
                   (np.abs(Z - sz) < 0.4), "g")
            S.plus(lambda X, Y, Z, sx=sx, sz=sz: ((np.abs(X - sx) < 0.3) | (np.abs(Y - 2.4) < 0.3)) &
                   (np.sqrt((X - sx) ** 2 + (Y - 2.4) ** 2) < 2.2) & (np.abs(Z - sz) < 0.3), "g")
    S.plus(lambda X, Y, Z: (X > 6) & (X < 9) & (Y > 4) & (Y < 5) & (np.abs(Z) < 2), "g")
    S.rendern((-9, -1, -7), (10, 15, 7), versatz=(0.5, 1.01, 0.5))
    glimmer(w, 9 * s, 6)
    hohl(w, 2)
    return w


def stiefelhaus(seed, g=1):
    """Stiefelhaus: ein riesiger alter Lederstiefel als Wohnhaus – Fenster in der Kappe, Schnürsenkel als Leiter,
    ein Schornstein aus dem Schaft und Blumen im Schaftrand."""
    w = _welt(seed)
    u = U[g]
    s = 0.6 * u + 0.4
    feenwiese(w, _r(9 * s + 5))
    S = Skulptur(w, s)
    S.mat("l", lambda x, y, z, *_: w.b("brown_terracotta") if (x + y + z) % 5 else w.b("brown_concrete"))
    S.mat("s", bl(w, "black_concrete"))
    S.mat("w", bl(w, "white_wool"))
    S.mat("f", bl(w, "glass"))
    S.plus(lambda X, Y, Z: (X > -4) & (X < 9) & (Y >= 0) & (Y < 1.2) & (np.abs(Z) < 3.6), "s")
    S.plus(lambda X, Y, Z: (((X - 4) / 5.5) ** 2 + ((Y - 1) / 3.5) ** 2 + (Z / 3.4) ** 2 < 1) & (Y >= 1), "l")
    S.plus(lambda X, Y, Z: (np.sqrt((X + 1) ** 2 + Z * Z) < 3.6) & (Y >= 1) & (Y < 13), "l")
    S.minus(lambda X, Y, Z: (np.sqrt((X + 1) ** 2 + Z * Z) < 2.6) & (Y >= 12))
    for k in range(5):
        S.plus(lambda X, Y, Z, k=k: (np.abs(X - 2.2 + k * 0.4) < 0.4) & (np.abs(Y - 4.2 - k * 1.6) < 0.3) &
               (np.abs(Z) < 3.8), "w")
    S.plus(ell(7, 2.6, 0, 0.5, 0.9, 1.2), "f")
    S.rendern((-6, -1, -5), (11, 15, 5), versatz=(0.5, 1.01, 0.5))
    for x, z in scheibe(2.0 * s, round(-s), 0):
        w.setze(x, round(12 * s) + 1, z, w.b(BLUMEN[(x + z) % len(BLUMEN)]))
    for y in range(round(13 * s), round(13 * s) + 3):
        w.setze(round(-2.5 * s), y, round(2 * s), w.b("bricks"))
    hohl(w, 2)
    return w


def regenbogenquelle(seed, g=1):
    """Regenbogenquelle: aus einem moosigen Felsen sprudelt Wasser in ein Becken, darüber spannt sich ein kleiner
    Regenbogen aus farbigem Glas, Feen-Lichter tanzen im Sprühnebel."""
    w = _welt(seed)
    u = U[g]
    R = _r(6 * u + 4)
    feenwiese(w, R + 4)
    fels = Mat(w, ["mossy_cobblestone", "moss_block", "stone", "andesite"], kontrast=1.2)
    for x, z in scheibe(3 + u, 0, -R // 2):
        hh = int((1 - math.hypot(x, z + R // 2) / (3 + u + 0.5)) * (4 + 2 * u))
        for y in range(1, hh + 1):
            w.setze(x, y, z, fels(x, y, z, y / 6))
    for x, z in scheibe(R * 0.6, 0, 2):
        w.setze(x, 0, z, w.b("water", level=0))
    for y in range(1, 4 + int(2 * u)):
        w.setze(0, y, -R // 2 + 2, w.b("water", level=0 if y == 3 + int(2 * u) else 8))
    farben = ["red", "orange", "yellow", "lime", "light_blue", "blue", "purple"]
    Rb = R * 0.9
    for i, f in enumerate(farben):
        r = Rb - i * 0.9
        for t in np.linspace(0, math.pi, int(r * 6)):
            w.setze(round(math.cos(t) * r), round(math.sin(t) * r * 0.9) + 1, 2, w.b(f"{f}_stained_glass"),
                    ueberschreiben=False)
    glimmer(w, R, 8 + 4 * g, 2, 7)
    return w


def schmetterlingspavillon(seed, g=1):
    """Schmetterlingspavillon: ein runder Pavillon aus Birkenzweigen, dessen Dach aus vier riesigen bunten
    Schmetterlingsflügeln aus Buntglas besteht; Blumenranken an den Säulen."""
    w = _welt(seed)
    u = U[g]
    R = 3 * u + 2.5
    feenwiese(w, _r(R + 6))
    H = _r(3 * u + 3)
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b("birch_log", axis="y") if y % 2 else laub(w, "flowering_azalea"))
    for x, z in scheibe(R + 0.5):
        w.setze(x, H + 1, z, w.b("birch_planks"))
    S = Skulptur(w, 1.0)
    farben = [("orange_stained_glass", "black_stained_glass"), ("light_blue_stained_glass", "blue_stained_glass"),
              ("yellow_stained_glass", "black_stained_glass"), ("pink_stained_glass", "magenta_stained_glass")]
    for k in range(4):
        a = k / 4 * 2 * math.pi + math.pi / 4
        f1, f2 = farben[k]
        S.mat(f"f{k}", lambda x, y, z, lx, ly, lz, f1=f1, f2=f2: w.b(f2) if (abs(lx) + abs(lz)) % 3 < 0.7 else w.b(f1))
        ca, sa = math.cos(a), math.sin(a)
        S.plus(lambda X, Y, Z, ca=ca, sa=sa: ((((X * ca + Z * sa) - R * 0.8) / (R * 0.9)) ** 2 +
                                              ((-X * sa + Z * ca) / (R * 0.7)) ** 2 < 1) &
               (np.abs(Y - (X * ca + Z * sa) * 0.6) < 0.6), f"f{k}")
    S.plus(kap((0, 0, 0), (0, 3, 0), 0.5, 0.4), "f0")
    S.rendern((-R * 2.2, -1, -R * 2.2), (R * 2.2, R * 2, R * 2.2), versatz=(0.5, H + 2.01, 0.5))
    return w


def moospolsterdorf(seed, g=2):
    """Moospolsterdorf: winzige Feenhäuschen mit Blütendächern sitzen auf weichen Moospolstern, verbunden durch
    Kieselpfade, kleine Laternenpilze und ein Brunnen aus einer Schneckenschale."""
    w = _welt(seed)
    u = U[g]
    R = _r(10 * u + 6)
    feenwiese(w, R + 2)
    rng = w.rng
    n = 5 + 2 * g
    for i in range(n):
        a = i * 2.39996
        d = R * 0.8 * math.sqrt((i + 0.5) / n)
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        for x, z in scheibe(2.6, cx, cz):
            hh = 1 + (math.hypot(x - cx, z - cz) < 1.5)
            for y in range(1, hh + 1):
                w.setze(x, y, z, w.b("moss_block"))
        for y in range(3, 5):
            for x, z in kreisrand(1.2, cx, cz):
                w.setze(x, y, z, w.b("white_terracotta") if (x + z + y) % 3 else w.b("birch_planks"))
        farbe = ["pink", "red", "yellow", "light_blue", "magenta"][i % 5]
        for k in range(3):
            for x, z in scheibe(max(0.5, 2.0 - k * 0.7), cx, cz):
                w.setze(x, 5 + k, z, w.b(f"{farbe}_concrete") if (x + z) % 2 else w.b(f"{farbe}_terracotta"))
        w.setze(cx, 3, cz + 1, w.b("oak_trapdoor", facing="south", half="bottom", open=True, powered=False,
                                   waterlogged=False))
    for i in range(int(R * 3)):
        a = rng.random() * 2 * math.pi
        d = rng.random() * R
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if (x, 1, z) not in w.bloecke:
            w.setze(x, 0, z, w.b("gravel") if rng.random() < 0.5 else w.b("dirt_path"))
    glimmer(w, R, 8 + 4 * g, 2, 6)
    return w


def pusteblumenturm(seed, g=2):
    """Pusteblumenturm: ein hoher grüner Stängel mit Wendeltreppe aus Blättern, oben eine riesige weiße
    Pusteblumen-Kugel mit Schirmchen, von der einzelne Samen davonfliegen; ein Aussichtssitz im Kern."""
    w = _welt(seed)
    u = U[g]
    H = _r(16 * u + 8)
    feenwiese(w, _r(6 * u + 6))
    for y in range(1, H):
        for x, z in kreisrand(1.0):
            w.setze(x, y, z, w.b("lime_concrete") if y % 4 else w.b("green_concrete"))
    for i in range(H * 2):
        a = i * 0.5
        y = 1 + i // 2
        if y >= H:
            break
        w.setze(round(math.cos(a) * 2.2), y, round(math.sin(a) * 2.2), w.b("lime_concrete") if i % 2 else
                w.b("green_concrete"))
    R = 4 * u + 3
    S = Skulptur(w, 1.0)
    S.mat("w", lambda x, y, z, *_: w.b("white_wool") if (x + y + z) % 3 else w.b("white_stained_glass"))
    S.mat("k", bl(w, "yellow_concrete"))
    rng = w.rng
    for i in range(int(40 * u)):
        th = math.acos(1 - 2 * (i + 0.5) / int(40 * u))
        ph = i * 2.39996
        dx, dy, dz = math.sin(th) * math.cos(ph), math.cos(th), math.sin(th) * math.sin(ph)
        S.plus(kap((0, 0, 0), (dx * R * 0.85, dy * R * 0.85, dz * R * 0.85), 0.2, 0.2), "w")
        S.plus(ell(dx * R, dy * R, dz * R, 0.9, 0.9, 0.9), "w")
    S.plus(ell(0, 0, 0, 1.5, 1.5, 1.5), "k")
    S.rendern((-R - 2, -R - 2, -R - 2), (R + 2, R + 2, R + 2), versatz=(0.5, H + R * 0.8, 0.5))
    for i in range(6):
        a = rng.random() * 2 * math.pi
        d = R + 3 + rng.random() * 6
        y = H + int(rng.integers(-2, 6))
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        w.setze(x, y, z, w.b("white_wool"))
        w.setze(x, y - 1, z, w.b("end_rod", facing="up"))
    return w


NEU = {
    "teekannenhaus": ("Teekannenhaus", teekannenhaus),
    "eichelhaus": ("Eichelhaus", eichelhaus),
    "glockenblumen": ("Glockenblumen-Laternen", glockenblumen),
    "libellenhafen": ("Libellenhafen", libellenhafen),
    "tautropfenbrunnen": ("Tautropfenbrunnen", tautropfenbrunnen),
    "seerosenmarkt": ("Seerosenmarkt", seerosenmarkt),
    "kuerbiskutsche": ("Kürbiskutsche", kuerbiskutsche),
    "stiefelhaus": ("Stiefelhaus", stiefelhaus),
    "regenbogenquelle": ("Regenbogenquelle", regenbogenquelle),
    "schmetterlingspavillon": ("Schmetterlingspavillon", schmetterlingspavillon),
    "moospolsterdorf": ("Moospolsterdorf", moospolsterdorf),
    "pusteblumenturm": ("Pusteblumenturm", pusteblumenturm),
}

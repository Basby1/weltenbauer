"""Mystik – Paket: Helixturm-Insel, Steinkreis, Sternentor, Dimensionsriss, Kristallsäulen, Mondaltar,
Schwebende Sphäre, Lichtbrunnen und Runenmonolith. Zwei Stile: Stil 1 Mond/Silber/Türkis, Stil 2 Glut/Violett."""

from __future__ import annotations

import math

import numpy as np

from lib import Verlauf, Welt, laub
from skulptur import Skulptur, ell, kap, kegel, kreisrand, platte, scheibe, torus, dreh_x, dreh_z, verbinde

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


class Magie:
    def __init__(self, w, seed):
        self.w = w
        b = w.b
        self.mond = _stil(seed) == 0
        if self.mond:
            self.stein = Verlauf(w, "Mondstein", ["deepslate_tiles", "polished_deepslate", "stone_bricks", "polished_andesite",
                                                  "calcite"])
            self.metall = Verlauf(w, "Patina", ["waxed_oxidized_cut_copper", "waxed_oxidized_copper", "prismarine_bricks"])
            self.glas = [b("light_blue_stained_glass"), b("cyan_stained_glass"), b("white_stained_glass")]
            self.licht = b("sea_lantern")
            self.rune = b("pearlescent_froglight")
            self.kristall = b("prismarine_bricks")
            self.seele = True
        else:
            self.stein = Verlauf(w, "Schattenstein", ["blackstone", "polished_blackstone", "polished_blackstone_bricks",
                                                      "purpur_block", "end_stone_bricks"])
            self.metall = Verlauf(w, "Gold", ["gilded_blackstone", "raw_gold_block", "gold_block"])
            self.glas = [b("purple_stained_glass"), b("magenta_stained_glass"), b("pink_stained_glass")]
            self.licht = b("shroomlight")
            self.rune = b("crying_obsidian")
            self.kristall = b("amethyst_block")
            self.seele = False

    def g(self):
        return self.glas[int(self.w.rng.integers(len(self.glas)))]


def _gras(w, r, cx=0, cz=0):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, w.b("grass_block", snowy=False) if w.rng.random() < 0.8 else w.b("moss_block"),
                ueberschreiben=False)


def _plattform(w, m, R, H=1, cx=0, cz=0):
    for y in range(H):
        for x, z in scheibe(R - y, cx, cz):
            w.setze(x, y, z, m.stein(1 + 2 * w.rng.random(), x, y, z))
    for x, z in kreisrand(R - H + 1, cx, cz):
        w.setze(x, H, z, w.b("polished_deepslate_slab" if m.mond else "polished_blackstone_slab", type="bottom",
                             waterlogged=False))
    return H


# ============================================================================ Helixturm-Insel

def helixturm(seed, g=3):
    """Felsinsel mit Bergen, Wald und Strand. Aus einem achteckigen Schacht windet sich eine Doppelhelix aus
    Schiefer und Patina-Kupfer empor, innen eine leuchtende Wassersäule; Ringe in der Höhe und zwei
    Nebentürme auf den Bergen, verbunden durch Kupferbrücken."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 22 * u + 8
    rng = w.rng
    # Insel: Höhenfeld mit zwei Bergen
    berge = [(-R * 0.55, -R * 0.15, R * 0.38, 15 * u + 6), (R * 0.55, R * 0.1, R * 0.34, 13 * u + 5)]
    hoehe = {}
    n = int(R * 1.2) + 2
    stein = Verlauf(w, "Fels", ["andesite", "stone", "tuff", "calcite"])
    for x in range(-n, n + 1):
        for z in range(-n, n + 1):
            a = math.atan2(z, x)
            rand = R * (1 + 0.12 * math.sin(3 * a + 1) + 0.06 * math.sin(7 * a))
            d = math.hypot(x, z)
            if d > rand:
                continue
            h = 2 + 1.5 * u * (1 - d / rand)
            for bx, bz, br, bh in berge:
                dd = math.hypot(x - bx, z - bz) / br
                if dd < 1:
                    h += bh * (1 - dd) ** 1.6 * (0.8 + 0.2 * math.sin(x * 0.7 + z * 0.5))
            h = int(h)
            hoehe[(x, z)] = h
            strand = d > rand - 2.5 * u - 1
            for y in range(0, h + 1):
                if y == h:
                    blk = w.b("sand") if strand else (stein(1 + y / (12 * u) + rng.random(), x, y, z)
                                                     if h > 4 + 3 * u else w.b("grass_block", snowy=False))
                else:
                    blk = w.b("sandstone") if strand else stein(0.5 + rng.random(), x, y, z)
                w.setze(x, y, z, blk)
    # Bäume
    for i in range(int(14 * u)):
        a = rng.random() * 2 * math.pi
        d = R * (0.25 + 0.6 * rng.random())
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        h0 = hoehe.get((x, z))
        if h0 is None or w.P.name(w.hole(x, h0, z) or 0) != "minecraft:grass_block":
            continue
        th = _r(3 + 2 * rng.random() * u)
        for y in range(h0 + 1, h0 + th + 1):
            w.setze(x, y, z, w.b("spruce_log", axis="y"))
        for k in range(th + 2):
            rr = max(0.5, (1 - k / (th + 2)) * (1.5 + u * 0.6))
            for xx, zz in scheibe(rr, x, z):
                w.setze(xx, h0 + 2 + k, zz, laub(w, "spruce"), ueberschreiben=False)
    # Achteckiger Schacht
    rs = 4.5 * u + 2
    tief = _r(4 * u, 3)
    oben = 2 + int(1.5 * u)

    def okt(x, z):
        return max(abs(x), abs(z), (abs(x) + abs(z)) / math.sqrt(2))
    for x in range(-int(rs) - 3, int(rs) + 4):
        for z in range(-int(rs) - 3, int(rs) + 4):
            d = okt(x, z)
            if d <= rs + 2:
                for y in range(-tief, oben + 3):
                    w.bloecke.pop((x, y, z), None)
                if d > rs:
                    for y in range(-tief, oben + 1):
                        w.setze(x, y, z, w.b("polished_deepslate") if y < oben else w.b("smooth_quartz"))
                    if d > rs + 1:
                        w.setze(x, oben + 1, z, w.b("end_rod", facing="up") if (x + z) % 4 == 0 else
                                w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
                else:
                    stufe = int((rs - d) / max(1, rs / 4))
                    w.setze(x, -tief + stufe, z, w.b("polished_deepslate"))
    # Doppelhelix mit Wassersäule
    H = 46 * u + 12
    Rh = 3.4 * u + 1.6
    dick = 1.0 * u + 0.7
    S = Skulptur(w, 1.0)
    kupfer, schiefer = m.metall, Verlauf(w, "Schiefer", ["deepslate_tiles", "polished_deepslate", "deepslate_bricks"])
    S.mat("strang", lambda x, y, z, lx, ly, lz: kupfer(1 + rng.random(), x, y, z)
          if math.hypot(lx, lz) < Rh - dick * 0.25 else schiefer(1 + rng.random() * 1.5, x, y, z))
    S.mat("wasser", lambda x, y, z, lx, ly, lz: m.licht if math.hypot(lx, lz) < 0.8 else
          (w.b("blue_stained_glass") if (y // 3) % 2 else w.b("light_blue_stained_glass")))
    S.mat("ring", lambda x, y, z, *_: schiefer(1.5, x, y, z) if (x + z) % 5 else kupfer(1.5, x, y, z))
    steig = 2 * math.pi / (14 * u + 6)
    y0 = -tief + 1

    def strang(phase):
        def f(X, Y, Z):
            th = (Y - y0) * steig + phase
            dx, dz = X - Rh * np.cos(th), Z - Rh * np.sin(th)
            return (Y >= y0) & (Y <= y0 + H) & (dx * dx + dz * dz <= dick * dick * 1.3)
        return f
    S.plus(lambda X, Y, Z: (X * X + Z * Z <= (Rh - dick * 0.9) ** 2) & (Y >= y0) & (Y <= y0 + H - 2), "wasser")
    S.plus(strang(0.0), "strang")
    S.plus(strang(math.pi), "strang")
    for f_, rr in ((0.32, Rh + 3.5 * u + 2), (0.97, Rh + 2.5 * u + 1)):
        S.plus(lambda X, Y, Z, f_=f_, rr=rr: (np.abs(Y - (y0 + H * f_)) <= 0.6 * u + 0.4)
               & (np.abs(np.sqrt(X * X + Z * Z) - rr) <= 0.9 * u + 0.5), "ring")
    S.rendern((-Rh - 8 * u - 4, y0, -Rh - 8 * u - 4), (Rh + 8 * u + 4, y0 + H + 2, Rh + 8 * u + 4))
    # Nebentürme auf den Bergen mit Kupferbrücken zum unteren Ring
    yr = y0 + H * 0.32
    rr = Rh + 3.5 * u + 2
    for bx, bz, br, bh in berge:
        tx, tz = round(bx * 0.95), round(bz * 0.95)
        gy = hoehe.get((tx, tz), 4)
        th = int(yr - gy) + _r(3 * u, 2)
        T = Skulptur(w, 1.0)
        T.mat("strang", lambda x, y, z, *_: kupfer(1 + rng.random(), x, y, z) if (x + y + z) % 3 else
              schiefer(1.5, x, y, z))
        T.mat("ring", lambda x, y, z, *_: schiefer(2, x, y, z))
        rt, dt = 1.2 * u + 0.8, 0.5 * u + 0.6
        for phase in (0, math.pi):
            T.plus(lambda X, Y, Z, phase=phase: (Y >= 0) & (Y <= th) &
                   ((X - rt * np.cos(Y * 0.5 + phase)) ** 2 + (Z - rt * np.sin(Y * 0.5 + phase)) ** 2 <= dt * dt * 1.5),
                   "strang")
        T.plus(lambda X, Y, Z: (np.abs(Y - th) <= 0.6) & (X * X + Z * Z <= (rt + 1.6) ** 2), "ring")
        T.rendern((-rt - 3, 0, -rt - 3), (rt + 3, th + 1, rt + 3), versatz=(tx + 0.5, gy + 1, tz + 0.5))
        # Brücke
        a = math.atan2(tz, tx)
        ziel = (round(math.cos(a) * rr), round(math.sin(a) * rr))
        ya = gy + 1 + th
        lang = int(math.hypot(tx - ziel[0], tz - ziel[1]))
        for k in range(lang + 1):
            t = k / max(1, lang)
            x = round(tx + (ziel[0] - tx) * t)
            z = round(tz + (ziel[1] - tz) * t)
            y = round(ya + (yr - ya) * t - math.sin(t * math.pi) * 1.5 * u)
            w.setze(x, y, z, w.b("waxed_oxidized_cut_copper"))
            w.setze(x, y + 1, z, w.b("chain", axis="y", waterlogged=False) if k % 3 == 0 else
                    w.b("waxed_oxidized_cut_copper_slab", type="bottom", waterlogged=False), ueberschreiben=False)
    w.bloecke = {p: b for p, b in w.bloecke.items() if p[1] >= -tief}
    w.anker = (0, 0, 0)
    return w


# ============================================================================ kleinere Mystik-Bauten

def steinkreis(seed, g=1):
    """Kreis aus gewaltigen Steinpfeilern mit Decksteinen, in der Mitte ein Altar mit leuchtendem Runenstein,
    Moos und Ranken."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 9 * u + 4
    _gras(w, R + 4)
    n = max(6, int(10 * u / 1.2) + 4)
    hs = _r(6 * u + 2, 4)
    bs = max(1, int(u))
    st = Verlauf(w, "Megalith", ["mossy_cobblestone", "cobblestone", "andesite", "stone", "tuff"])
    pfeiler = []
    for i in range(n):
        a = i * 2 * math.pi / n
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        pfeiler.append((x, z))
        for y in range(1, hs + 1):
            for dx in range(-bs + 1, bs + 1):
                for dz in range(-bs + 1, bs + 1):
                    w.setze(x + dx, y, z + dz, st(0.5 + 3 * y / hs + w.rng.random(), x, y, z))
        if i % 3 == 1:
            w.setze(x, hs // 2, z, m.rune)
    for i in range(0, n, 2):
        (x1, z1), (x2, z2) = pfeiler[i], pfeiler[(i + 1) % n]
        for t in np.linspace(0, 1, 2 * int(math.hypot(x2 - x1, z2 - z1)) + 2):
            for dy in range(bs):
                w.setze(round(x1 + (x2 - x1) * t), hs + 1 + dy, round(z1 + (z2 - z1) * t), st(3, 0, 0, 0))
    for x, z in scheibe(2 * u + 1):
        w.setze(x, 1, z, m.stein(2, x, 1, z))
    w.setze(0, 2, 0, m.rune)
    w.setze(0, 3, 0, w.b("amethyst_cluster", facing="up", waterlogged=False) if not m.mond else m.licht)
    from lib import ueberwuchern
    ueberwuchern(w, None, ranken=0.3, moos_oben=0.6, pflanzen=0.2, buesche=0.0, max_ranke=3)
    return w


def sternentor(seed, g=1):
    """Leuchtender Kern über einem Podest, umgeben von drei schräg stehenden Kupfer-/Goldringen."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 6 * u + 2
    _gras(w, R + 4)
    H = _plattform(w, m, R * 0.7 + 2, _r(1.5 * u, 1))
    cy = H + R + 2
    S = Skulptur(w, 1.0)
    S.mat("r", lambda x, y, z, *_: m.metall(1 + w.rng.random() * 1.5, x, y, z))
    S.mat("k", m.licht)
    S.mat("g", lambda *a: m.g())
    S.plus(ell(0, 0, 0, 1.6 * u + 0.6, 1.6 * u + 0.6, 1.6 * u + 0.6), "g")
    S.plus(ell(0, 0, 0, 0.9 * u + 0.3, 0.9 * u + 0.3, 0.9 * u + 0.3), "k")
    for i, (ax, az) in enumerate(((0.0, 0.0), (1.0, 0.4), (-0.5, 1.2))):
        rr = R - i * 1.2 * u
        rot = dreh_z(ax) @ dreh_x(az)
        Ri = np.linalg.inv(rot)
        dk = 0.45 * u + 0.4

        def ring(X, Y, Z, Ri=Ri, rr=rr, dk=dk):
            lx = Ri[0, 0] * X + Ri[0, 1] * Y + Ri[0, 2] * Z
            ly = Ri[1, 0] * X + Ri[1, 1] * Y + Ri[1, 2] * Z
            lz = Ri[2, 0] * X + Ri[2, 1] * Y + Ri[2, 2] * Z
            q = np.sqrt(lx * lx + lz * lz) - rr
            return q * q + ly * ly <= dk * dk
        S.plus(ring, "r")
    S.rendern((-R - 2, -R - 2, -R - 2), (R + 2, R + 2, R + 2), versatz=(0.5, cy, 0.5))
    for x, z in kreisrand(R * 0.7 + 1):
        if (x + z) % 4 == 0:
            w.setze(x, H + 1, z, w.b("soul_lantern" if m.seele else "lantern", hanging=False, waterlogged=False))
    return w


def dimensionsriss(seed, g=1):
    """Ein gezackter Riss in der Luft aus schwarzem und farbigem Glas, Splitter schweben umher,
    der Boden darunter ist versengt."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    H = 16 * u + 6
    for x, z in scheibe(5 * u + 3):
        w.setze(x, 0, z, w.b("obsidian") if w.rng.random() < 0.25 else w.b("crying_obsidian") if w.rng.random() < 0.1
                else w.b("blackstone"))
    y0 = 2 + int(u)
    pts = []
    x = 0.0
    for k in range(int(H) + 1):
        x += (w.rng.random() - 0.5) * 1.6
        pts.append(x)
    for k, xc in enumerate(pts):
        y = y0 + k
        breite = (1.2 * u + 0.6) * math.sin(math.pi * k / H) ** 0.8
        for xx in range(int(xc - breite) - 1, int(xc + breite) + 2):
            d = abs(xx - xc)
            if d <= breite:
                w.setze(xx, y, 0, w.b("black_stained_glass") if d < breite * 0.45 else m.g())
            elif d <= breite + 1 and w.rng.random() < 0.6:
                w.setze(xx, y, 0, w.b("crying_obsidian") if w.rng.random() < 0.3 else w.b("end_rod", facing="up"))
    for i in range(int(10 * u) + 4):
        a = w.rng.random() * 2 * math.pi
        d = 2 + w.rng.random() * 4 * u
        y = y0 + w.rng.random() * H
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        w.setze(x, round(y), z, m.g())
        if w.rng.random() < 0.5:
            w.setze(x, round(y) + 1, z, m.g())
    return w


def kristallsaeulen(seed, g=1):
    """Gruppe riesiger sechseckiger Kristallsäulen, schräg aus dem Fels wachsend, mit Leuchtkernen."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 7 * u + 3
    for x, z in scheibe(R + 2):
        w.setze(x, 0, z, m.stein(0.5 + w.rng.random(), x, 0, z))
        if math.hypot(x, z) < R * 0.6 and w.rng.random() < 0.4:
            w.setze(x, 1, z, m.stein(1 + w.rng.random(), x, 1, z))
    S = Skulptur(w, 1.0)
    S.mat("k", lambda x, y, z, lx, ly, lz: m.licht if (x * 7 + y * 3 + z) % 17 == 0 else
          (m.kristall if (x + y + z) % 3 else m.g()))
    for i in range(5 + g):
        a = i * 2.4 + w.rng.random()
        d = R * 0.5 * w.rng.random()
        bx, bz = math.cos(a) * d, math.sin(a) * d
        lang = (6 + 10 * w.rng.random()) * u + 3
        r = (0.8 + 0.8 * w.rng.random()) * u + 0.7
        neig = 0.25 + 0.35 * w.rng.random()
        tx, ty, tz = bx + math.cos(a) * lang * neig, lang, bz + math.sin(a) * lang * neig

        def saeule(X, Y, Z, bx=bx, bz=bz, tx=tx, ty=ty, tz=tz, r=r):
            d = np.array([tx - bx, ty, tz - bz])
            L2 = d @ d
            t = np.clip(((X - bx) * d[0] + Y * d[1] + (Z - bz) * d[2]) / L2, 0, 1)
            qx, qy, qz = X - bx - t * d[0], Y - t * d[1], Z - bz - t * d[2]
            rr = r * np.where(t > 0.85, (1 - t) / 0.15, 1)
            ang = np.arctan2(qz, qx)
            hexr = rr * np.cos(math.pi / 6) / np.cos(np.mod(ang, math.pi / 3) - math.pi / 6)
            return qx * qx + qy * qy + qz * qz <= hexr * hexr
        S.plus(saeule, "k")
    S.rendern((-R - 12 * u, 0, -R - 12 * u), (R + 12 * u, 18 * u + 4, R + 12 * u), versatz=(0.5, 1, 0.5))
    return w


def mondaltar(seed, g=1):
    """Gestufter Altar mit einer großen Mondsichel aus Stein, brennenden Kerzen, Becken und Säulen."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 6 * u + 3
    _gras(w, R + 4)
    stufen = [2, 3, 3, 4][g]
    for k in range(stufen):
        r = R - k * 1.2 * u
        for x, z in scheibe(r):
            w.setze(x, k, z, m.stein(1 + k + w.rng.random(), x, k, z))
    top = stufen
    S = Skulptur(w, 1.0)
    S.mat("s", lambda x, y, z, *_: w.b("smooth_quartz") if m.mond else w.b("gold_block"))
    S.mat("r", m.rune)
    Rm = 4.5 * u + 1.5
    S.plus(lambda X, Y, Z: ((X * X + Y * Y) <= Rm * Rm) & (((X - Rm * 0.45) ** 2 + (Y - Rm * 0.15) ** 2) > (Rm * 0.82) ** 2)
           & (np.abs(Z) <= 0.5 * u + 0.4), "s")
    S.plus(ell(-Rm * 0.35, 0, 0, 0.6 * u + 0.3, 0.6 * u + 0.3, 0.6 * u + 0.6), "r")
    S.rendern((-Rm - 1, -Rm - 1, -2 * u - 1), (Rm + 1, Rm + 1, 2 * u + 1), versatz=(0.5, top + Rm + 1, 0.5))
    for i, (x, z) in enumerate(kreisrand(R - (stufen - 1) * 1.2 * u - 0.8)):
        if i % 3 == 0:
            w.setze(x, top, z, w.b("white_candle" if m.mond else "purple_candle", candles=3, lit=True, waterlogged=False))
    for s in (-1, 1):
        x = s * round(R - 1)
        for y in range(1, _r(4 * u + 1, 3)):
            w.setze(x, y, 0, w.b("quartz_pillar" if m.mond else "polished_blackstone_bricks", axis="y")
                    if m.mond else w.b("polished_blackstone_bricks"))
        w.setze(x, _r(4 * u + 1, 3), 0, w.b("soul_campfire" if m.seele else "campfire", lit=True, signal_fire=False,
                                             facing="north", waterlogged=False))
    return w


def schwebende_sphaere(seed, g=1):
    """Große schwebende Glaskugel mit Leuchtkern und Kupferbändern, an Ketten zu vier Ankersteinen."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 4 * u + 2
    cy = 2 * R + 4 * u + 3
    _gras(w, R * 2 + 4)
    S = Skulptur(w, 1.0)
    S.mat("g", lambda *a: m.g())
    S.mat("k", m.licht)
    S.mat("b", lambda x, y, z, *_: m.metall(1.5, x, y, z))
    S.plus(lambda X, Y, Z: (X * X + Y * Y + Z * Z <= R * R) & (X * X + Y * Y + Z * Z > (R - 1.1) ** 2), "g")
    S.plus(ell(0, 0, 0, R * 0.35, R * 0.35, R * 0.35), "k")
    S.plus(torus(0, 0, 0, R + 0.2, 0.5 * u + 0.4, "y"), "b")
    S.plus(torus(0, 0, 0, R + 0.2, 0.5 * u + 0.4, "z"), "b")
    S.rendern((-R - 2, -R - 2, -R - 2), (R + 2, R + 2, R + 2), versatz=(0.5, cy, 0.5))
    for a in (0.8, 2.4, 3.9, 5.5):
        ax, az = round(math.cos(a) * R * 1.8), round(math.sin(a) * R * 1.8)
        for x, z in scheibe(0.8 * u + 0.6, ax, az):
            for y in range(1, _r(1.5 * u, 1) + 1):
                w.setze(x, y, z, m.stein(2, x, y, z))
        n = int(math.hypot(ax, az) + cy) * 2
        for k in range(n):
            t = k / n
            x = round(ax * (1 - t * 0.7))
            z = round(az * (1 - t * 0.7))
            y = round(_r(1.5 * u, 1) + 1 + (cy - R * 0.7 - _r(1.5 * u, 1)) * t)
            w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False), ueberschreiben=False)
    return w


def lichtbrunnen(seed, g=1):
    """Achteckiger Brunnen, aus dem eine Säule aus Licht und Glas emporsteigt, umkreist von Steinen."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 4 * u + 2.5
    _gras(w, R + 5)
    for x, z in scheibe(R + 1):
        w.setze(x, 0, z, m.stein(1, x, 0, z))
    for x, z in kreisrand(R + 1):
        w.setze(x, 1, z, m.stein(2 + w.rng.random(), x, 1, z))
        w.setze(x, 2, z, w.b("polished_deepslate_slab" if m.mond else "polished_blackstone_slab", type="bottom",
                             waterlogged=False))
    for x, z in scheibe(R):
        w.setze(x, 1, z, w.b("water", level=0))
    H = _r(22 * u + 6, 12)
    rs = 0.9 * u + 0.6
    for y in range(1, H):
        for x, z in scheibe(rs):
            w.setze(x, y, z, m.licht if (x, z) == (0, 0) and y % 3 == 0 else m.g())
        if y > H * 0.7 and w.rng.random() < 0.5:
            w.setze(round((w.rng.random() - 0.5) * 3), y, round((w.rng.random() - 0.5) * 3), w.b("end_rod", facing="up"))
    for i in range(6 + 2 * g):
        a = i * 2 * math.pi / (6 + 2 * g)
        d = R + 2 + u
        y = 3 + int((i % 3) * 2 * u) + int(H * 0.3)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        S = Skulptur(w, u)
        S.mat("s", lambda xx, yy, zz, *_: m.stein(2 + w.rng.random(), xx, yy, zz))
        S.plus(ell(0, 0, 0, 0.9, 0.6, 0.9), "s")
        S.rendern((-2, -2, -2), (2, 2, 2), versatz=(x + 0.5, y, z + 0.5))
    return w


def runenmonolith(seed, g=1):
    """Hoher, sich verjüngender Monolith mit leuchtenden Runenbändern und zwei schwebenden Ringen."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    H = _r(18 * u + 6, 10)
    b0 = 1.6 * u + 1.2
    _gras(w, b0 + 6)
    for y in range(H):
        t = y / H
        h = b0 * (1 - 0.45 * t)
        for x in range(-int(h) - 1, int(h) + 2):
            for z in range(-int(h * 0.7) - 1, int(h * 0.7) + 2):
                if abs(x) <= h and abs(z) <= h * 0.7:
                    rand = abs(x) > h - 1 or abs(z) > h * 0.7 - 1
                    rune = rand and y % 4 == 2 and (x + z) % 2 == 0 and y > 1
                    w.setze(x, y + 1, z, m.rune if rune else m.stein(1 + 3 * t + w.rng.random() * 0.5, x, y, z))
    for k in range(_r(2 * u, 1)):
        w.setze(0, H + 1 + k, 0, m.stein(4, 0, 0, 0))
    S = Skulptur(w, 1.0)
    S.mat("r", lambda x, y, z, *_: m.metall(1 + w.rng.random(), x, y, z))
    for f_, rr in ((0.45, b0 + 2 + u), (0.75, b0 + 1.2 + 0.6 * u)):
        S.plus(torus(0, H * f_, 0, rr, 0.35 * u + 0.4, "y"), "r")
    S.rendern((-b0 - 4 * u - 2, 0, -b0 - 4 * u - 2), (b0 + 4 * u + 2, H + 2, b0 + 4 * u + 2), versatz=(0.5, 1, 0.5))
    return w


MYSTIK = {
    "steinkreis": ("Steinkreis", steinkreis),
    "sternentor": ("Sternentor", sternentor),
    "dimensionsriss": ("Dimensionsriss", dimensionsriss),
    "kristallsaeulen": ("Kristallsäulen", kristallsaeulen),
    "mondaltar": ("Mondaltar", mondaltar),
    "schwebende_sphaere": ("Schwebende Sphäre", schwebende_sphaere),
    "lichtbrunnen": ("Lichtbrunnen", lichtbrunnen),
    "runenmonolith": ("Runenmonolith", runenmonolith),
}
HELIX = {"helixturm": ("Helixturm-Insel", helixturm)}

from mystik2 import NEU as _NEU  # noqa: E402

MYSTIK.update(_NEU)

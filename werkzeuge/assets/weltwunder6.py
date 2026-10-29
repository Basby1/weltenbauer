"""Weltwunder Teil 6 – Spiralzikkurat, Titanenschmiede, Walgebein, Himmelsleiter, Planetarium, Weltenschlange,
Silberbaumstadt, Sphinx, Titanentor, Großes Labyrinth."""

from __future__ import annotations

import math

import numpy as np

import pracht as P
from lib import Rauschen, einfuegen, laub
from motive import figur
from pracht import Mat, gelaende
from skulptur import Skulptur, dreh_y, dreh_z, ell, kap, kreisrand, scheibe, spiegel_x, torus
from weltwunder import U, _r, _stil, bl, hohl, platz, sk, welt
from weltwunder5 import fels, meer
from wueste_eis import kuppel


def spiralzikkurat(seed, g=2):
    """Spiralzikkurat: ein quadratischer Stufenturm, um den sich eine breite Rampe spiralförmig nach oben windet,
    gesäumt von Feuerschalen; oben ein Tempel mit goldenem Dach und hängende Gärten an den Stufen."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    R = _r(36 * u)
    gelaende(w, R + 8, art="sand" if st == 0 else "wiese", dichte=0.2)
    M = Mat(w, ["mud_bricks", "packed_mud", "terracotta", "brown_terracotta"] if st == 0 else
            ["sandstone", "cut_sandstone", "smooth_sandstone", "chiseled_sandstone"], kontrast=0.7)
    n = 6
    hk = _r(6 * u)
    for k in range(n):
        r = _r(R * (1 - k / (n + 0.5)))
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                for y in range(k * hk, (k + 1) * hk):
                    w.setze(x, y, z, M(x, y, z, k / n))
                if max(abs(x), abs(z)) == r and (x + z) % 2 == 0:
                    w.setze(x, (k + 1) * hk, z, laub(w, "jungle" if (x + z) % 4 else "flowering_azalea"))
    seite = 0
    y = 0
    pos = -R
    for k in range(n):
        r = _r(R * (1 - k / (n + 0.5)))
        for t in range(-r, r + 1):
            yy = k * hk + int((t + r) / (2 * r) * hk)
            for b in range(3):
                if seite == 0:
                    p = (t, yy, r + 1 + b)
                elif seite == 1:
                    p = (r + 1 + b, yy, -t)
                elif seite == 2:
                    p = (-t, yy, -r - 1 - b)
                else:
                    p = (-r - 1 - b, yy, t)
                for y2 in range(k * hk, yy + 1):
                    w.setze(p[0], y2, p[2], M(p[0], y2, p[2], 0.5))
            if t % 8 == 0:
                q = {0: (t, yy + 1, r + 3), 1: (r + 3, yy + 1, -t), 2: (-t, yy + 1, -r - 3), 3: (-r - 3, yy + 1, t)}[seite]
                w.setze(*q, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
        seite = (seite + 1) % 4
    yt = n * hk
    st2 = P.Stil(w, wand=M, sockel=M, gesims="sandstone", dach="mcw_gelb", holz="jungle", laeden=False, blumen=0)
    a = _r(R / (n + 0.5) * 0.8, 3)
    P.gebaeude(w, st2, -a, -a, a, a, y0=yt, etagen=1, eh=5, dach="walm", tuer="south", gauben=False, kamine=0)
    hohl(w, 3)
    return w


def titanenschmiede(seed, g=2):
    """Titanenschmiede: eine Esse so groß wie ein Berg – ein gewaltiger Amboss auf Basaltsockel, ein riesiger
    Hammer lehnt daran, Lavaströme fließen aus der Esse, vier Schlote rauchen."""
    w = welt(seed)
    u = U[g]
    R = _r(40 * u)
    gelaende(w, R + 6, art="asche", dichte=0.4)
    M = Mat(w, ["blackstone", "polished_blackstone_bricks", "basalt", "smooth_basalt", "magma_block"], kontrast=0.9)
    for k in range(3):
        for x, z in scheibe(R * 0.6 - k * 3):
            w.setze(x, k, z, M(x, k, z, k / 3))
    s = 2.4 * u
    S = Skulptur(w, s)
    S.mat("e", lambda x, y, z, *_: w.b("iron_block") if (x + y + z) % 5 else w.b("polished_basalt", axis="y"))
    S.mat("h", bl(w, "dark_oak_log"))
    S.mat("g", bl(w, "gold_block"))
    S.plus(lambda X, Y, Z: (np.abs(X) < 4) & (np.abs(Z) < 3) & (Y >= 0) & (Y < 3), "e")
    S.plus(lambda X, Y, Z: (np.abs(X) < 2.2 - 0.25 * (Y - 3)) & (np.abs(Z) < 1.8) & (Y >= 3) & (Y < 6.5), "e")
    S.plus(lambda X, Y, Z: (X > -7) & (X < 6) & (np.abs(Z) < 2.6) & (Y >= 6.5) & (Y < 9.5) &
           ((X < 3) | (Y > 8.0 + (X - 3) * 0.5)), "e")
    S.plus(kap((7, 0, 4), (2, 14, 4), 0.6, 0.6), "h")
    S.plus(lambda X, Y, Z: (np.abs(X - 1.5) < 1.8) & (np.abs(Y - 15) < 1.5) & (np.abs(Z - 4) < 2.5), "e")
    S.plus(lambda X, Y, Z: (np.abs(X - 1.5) < 1.9) & (np.abs(Y - 15) < 0.3) & (np.abs(Z - 4) < 2.6), "g")
    S.rendern((-9, -1, -4), (9, 18, 8), versatz=(0.5, 3.01, 0.5))
    for i in range(4):
        a = i / 4 * 2 * math.pi + math.pi / 4
        cx, cz = round(math.cos(a) * R * 0.75), round(math.sin(a) * R * 0.75)
        for y in range(0, _r(35 * u)):
            for x, z in kreisrand(2.5 * u + 1, cx, cz):
                w.setze(x, y, z, M(x, y, z, y / 40))
        w.setze(cx, _r(35 * u) - 1, cz, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                             waterlogged=False))
        for t in np.linspace(R * 0.2, R * 0.7, int(R)):
            x, z = round(math.cos(a + 0.4) * t), round(math.sin(a + 0.4) * t)
            w.setze(x, 0, z, w.b("lava", level=0))
            w.setze(x, -1, z, w.b("magma_block"))
    hohl(w, 3)
    return w


def walgebein(seed, g=2):
    """Walgebein: das gigantische Skelett eines Urwals liegt am Strand – Rippenbögen hoch wie Kathedralen, ein
    mächtiger Schädel, Wirbelsäule und Flossenknochen; Fischerhütten zwischen den Rippen."""
    w = welt(seed)
    u = U[g]
    L = 60 * u
    R = _r(L * 0.75)
    for x, z in scheibe(R):
        if z > R * 0.35:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("sand"))
        else:
            w.setze(x, 0, z, w.b("sand") if (x + z) % 7 else w.b("gravel"))
    S = Skulptur(w, 1.0)
    S.mat("k", lambda x, y, z, *_: w.b("bone_block", axis="y") if (x + 2 * y + z) % 6 else w.b("calcite"))
    pts = [(-L * 0.5, 2, 0), (-L * 0.25, 4 * u, 0), (0, 5 * u, 0), (L * 0.25, 4 * u, 0), (L * 0.42, 3 * u, 0)]
    for i in range(len(pts) - 1):
        S.plus(kap(pts[i], pts[i + 1], 1.4 * u, 1.2 * u), "k")
    for k in range(11):
        x = -L * 0.3 + k * L * 0.055
        hr = 18 * u * math.sin((k + 1) / 12 * math.pi) + 6
        S.plus(lambda X, Y, Z, x=x, hr=hr: (np.abs(X - x) < 0.8 * u + 0.3) &
               (np.abs(np.sqrt(((Y - 2) / hr) ** 2 + (Z / (hr * 0.65)) ** 2) - 1) < 0.07) & (Y > 0), "k")
    S.plus(ell(L * 0.52, 6 * u, 0, 9 * u, 4 * u, 6 * u), "k")
    S.minus(ell(L * 0.52, 6 * u, 0, 8 * u, 3 * u, 5 * u))
    S.plus(lambda X, Y, Z: (X > L * 0.45) & (X < L * 0.68) & (np.abs(Y - 1.5 * u) < 1.0) & (np.abs(Z) < 5 * u), "k")
    for sz in (-1, 1):
        S.plus(kap((L * 0.15, 3 * u, sz * 3 * u), (L * 0.05, 1, sz * 14 * u), 1.0 * u, 0.6 * u), "k")
    S.rendern((-L * 0.6, -1, -R), (L * 0.75, 26 * u, R), versatz=(0.5, 0.01, 0.5))
    sti = P.Stil(w, wand="holz_hell", sockel="graustein", gesims="stone_brick", dach="mcw_holz", holz="spruce")
    for k in range(2):
        x = round(-L * 0.2 + k * L * 0.25)
        P.gebaeude(w, sti, x - 2, -3, x + 2, 1, y0=1, etagen=1, eh=3, dach="sattel", tuer="south", gauben=False,
                   kamine=1)
    hohl(w, 3)
    return w


def himmelsleiter(seed, g=2):
    """Himmelsleiter: eine freischwebende Marmortreppe windet sich um eine leuchtende Säule durch drei Wolken-
    schichten bis zu einem goldenen Portalring hoch über dem Boden."""
    from himmel import wolke
    w = welt(seed)
    u = U[g]
    H = _r(90 * u)
    R = 9 * u + 3
    gelaende(w, _r(R + 14), art="wiese", dichte=0.2)
    platz(w, _r(R + 6), Mat(w, "marmor"), rand="quartz")
    for y in range(2, H):
        w.setze(0, y, 0, w.b("sea_lantern") if y % 6 == 0 else w.b("end_rod", facing="up") if y % 2 else
                w.b("white_stained_glass"))
    n = H * 4
    for i in range(n):
        a = i / 20 * 2 * math.pi
        y = 2 + i // 4
        if y >= H:
            break
        for rr in np.linspace(R - 2.5, R + 0.5, 4):
            x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
            w.setze(x, y, z, w.b("smooth_quartz") if i % 4 == 0 else w.b("smooth_quartz_slab", type="top",
                                                                             waterlogged=False))
        if i % 10 == 0:
            x, z = round(math.cos(a) * (R + 1.5)), round(math.sin(a) * (R + 1.5))
            w.setze(x, y + 1, z, w.b("lantern", hanging=False, waterlogged=False))
    for k, hf in enumerate((0.3, 0.55, 0.8)):
        wolke(w, round(math.cos(k * 2) * R), round(H * hf), round(math.sin(k * 2) * R), 8 * u + 4, flach=0.35,
              seed_off=k)
    S = Skulptur(w, 1.0)
    S.mat("g", bl(w, "gold_block"))
    S.mat("p", lambda x, y, z, *_: w.b("yellow_stained_glass") if (x + y) % 3 else w.b("white_stained_glass"))
    Rp = 8 * u + 3
    S.plus(lambda X, Y, Z: (np.abs(np.sqrt(X * X + Y * Y) - Rp) < 1.2) & (np.abs(Z) < 1.2), "g")
    S.plus(lambda X, Y, Z: (np.sqrt(X * X + Y * Y) < Rp - 1.2) & (np.abs(Z) < 0.5), "p")
    S.rendern((-Rp - 2, -Rp - 2, -2), (Rp + 2, Rp + 2, 2), versatz=(0.5, H + Rp + 2, 0.5))
    hohl(w, 2)
    return w


def planetarium(seed, g=2):
    """Planetarium der Götter: eine gewaltige Messing-Armillarsphäre auf einem Sternenplatz – leuchtende Sonne in
    der Mitte, Planeten aus Stein, Kupfer, Eis und Gold auf schrägen Bahnen und Ringen."""
    w = welt(seed)
    u = U[g]
    Rp = _r(46 * u)
    M = Mat(w, ["polished_deepslate", "deepslate_tiles", "blue_terracotta", "polished_blackstone"], kontrast=0.6)
    yp = platz(w, Rp, M, rand="deepslate_brick", muster=["lapis_block", "polished_deepslate", "gold_block"],
               akzent="sea_lantern", lichter="lantern")
    rng = w.rng
    for x, z in scheibe(Rp - 2):
        if rng.random() < 0.03:
            w.setze(x, yp - 1, z, w.b("sea_lantern"))
    S = Skulptur(w, 1.0)
    yc = 28 * u
    S.mat("s", lambda x, y, z, *_: w.b("shroomlight") if (x + y + z) % 3 else w.b("glowstone"))
    S.mat("r", lambda x, y, z, *_: w.b("gold_block") if (x + z) % 4 else w.b("raw_gold_block"))
    S.plus(ell(0, yc, 0, 7 * u, 7 * u, 7 * u), "s")
    S.plus(kap((0, 0, 0), (0, yc - 6 * u, 0), 1.5 * u, 1.2 * u), "r")
    planeten = [("stone", 14, 0.2, 2.0), ("waxed_copper_block", 20, -0.3, 3.0), ("packed_ice", 26, 0.15, 3.5),
                ("gold_block", 32, -0.1, 4.0), ("red_terracotta", 38, 0.35, 2.5)]
    for i, (mat, d, nei, pr) in enumerate(planeten):
        D = d * u
        S.plus(lambda X, Y, Z, D=D, nei=nei: (np.abs(np.sqrt(X * X + Z * Z) - D) < 0.6) &
               (np.abs((Y - yc) - X * nei) < 0.6), "r")
        a = i * 1.7
        px, pz = math.cos(a) * D, math.sin(a) * D
        S.mat(f"p{i}", bl(w, mat))
        S.plus(ell(px, yc + px * nei, pz, pr * u, pr * u, pr * u), f"p{i}")
        if mat == "gold_block":
            S.plus(lambda X, Y, Z, px=px, pz=pz, nei=nei: (np.abs(np.sqrt((X - px) ** 2 + (Z - pz) ** 2) - 6 * u) < 0.8)
                   & (np.abs(Y - yc - px * nei) < 0.5), "r")
    S.rendern((-Rp, 0, -Rp), (Rp, yc + 20 * u, Rp), versatz=(0.5, yp + 0.01, 0.5))
    hohl(w, 3)
    return w


def weltenschlange(seed, g=2):
    """Weltenschlange: eine gigantische Schlange windet sich dreimal um einen schroffen Berggipfel und blickt mit
    glühenden Augen über das Land, ihr Schwanz verschwindet im See am Fuß."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    R = _r(40 * u)
    H = 55 * u
    gelaende(w, R + 6, art="wiese", dichte=0.2)
    hoehe = fels(w, R * 0.55, H, spitz=0.5, rauh=0.2)
    for x, z in scheibe(R):
        if math.hypot(x, z) > R * 0.6 and z > R * 0.2:
            w.setze(x, 0, z, w.b("water", level=0))
    farbe = Mat(w, ["green_concrete", "lime_terracotta", "green_terracotta", "moss_block"] if st == 0 else
                ["black_concrete", "purple_terracotta", "blackstone", "gray_concrete"], kontrast=0.8)
    bauch = Mat(w, ["yellow_terracotta", "lime_terracotta"] if st == 0 else ["purple_terracotta", "magenta_terracotta"])
    S = Skulptur(w, 1.0)
    S.mat("s", lambda x, y, z, *_: farbe(x, y, z, 0.5))
    S.mat("b", lambda x, y, z, *_: bauch(x, y, z, 0.5))
    S.mat("a", bl(w, "shroomlight" if st == 0 else "redstone_block"))
    S.mat("h", bl(w, "bone_block"))
    rad = 4.2 * u + 1.5
    n = 120
    pts = []
    for i in range(n + 1):
        t = i / n
        a = t * 3 * 2 * math.pi
        y = 2 + t * H * 0.9
        rr = R * 0.55 * (1 - y / (H * 1.05)) + rad + 1
        pts.append((math.cos(a) * rr, y, math.sin(a) * rr))
    for i in range(n):
        S.plus(kap(pts[i], pts[i + 1], rad * min(1, 0.3 + i / 20), rad * min(1, 0.3 + (i + 1) / 20)), "s")
    hx, hy, hz = pts[-1]
    S.plus(ell(hx, hy + rad, hz, rad * 2.2, rad * 1.4, rad * 1.6), "s")
    S.plus(ell(hx + rad * 1.2, hy + rad * 0.5, hz, rad * 1.6, rad * 0.5, rad * 1.2), "b")
    for sz in (-1, 1):
        S.plus(ell(hx + rad * 0.8, hy + rad * 1.6, hz + sz * rad, rad * 0.4, rad * 0.4, rad * 0.4), "a")
        S.plus(kap((hx + rad * 2.0, hy + rad * 0.2, hz + sz * rad * 0.4), (hx + rad * 2.2, hy - rad * 0.8,
                                                                              hz + sz * rad * 0.4), rad * 0.2, rad * 0.05),
               "h")
    S.rendern((-R, 0, -R), (R, H + 12 * u, R), versatz=(0.5, 0.01, 0.5))
    hohl(w, 3)
    return w


def silberbaumstadt(seed, g=2):
    """Silberbaumstadt: ein riesiger silberweißer Baum, in dessen Ästen auf mehreren Ebenen Elfenhäuser mit
    grünen Kuppeln, Hängebrücken und Laternen sitzen; Wendeltreppe um den Stamm."""
    w = welt(seed)
    u = U[g]
    R = _r(40 * u)
    gelaende(w, R, art="wald", dichte=0.3)
    H = _r(55 * u)
    rs = 5 * u + 2
    S = Skulptur(w, 1.0)
    S.mat("s", lambda x, y, z, *_: w.b("birch_wood", axis="y") if (x + z + y) % 5 else w.b("calcite"))
    S.mat("l", lambda x, y, z, *_: laub(w, "birch") if (x + y + z) % 4 else laub(w, "flowering_azalea"))
    S.plus(kap((0, -1, 0), (0, H * 0.75, 0), rs, rs * 0.55), "s")
    for i in range(7):
        a = i / 7 * 2 * math.pi
        S.plus(kap((0, 2, 0), (math.cos(a) * rs * 2.5, -1, math.sin(a) * rs * 2.5), rs * 0.5, rs * 0.2), "s")
    rng = w.rng
    ebenen = []
    for i in range(6):
        a = i / 6 * 2 * math.pi + 0.3
        y0 = H * (0.35 + 0.08 * i)
        L = 14 * u + 4
        p1 = (math.cos(a) * L, y0 + L * 0.35, math.sin(a) * L)
        S.plus(kap((0, y0, 0), p1, rs * 0.4, rs * 0.2), "s")
        S.plus(lambda X, Y, Z, p=p1: (((X - p[0]) / (8 * u + 2)) ** 2 + ((Y - p[1] - 4 * u) / (4 * u + 1.5)) ** 2 +
                                      ((Z - p[2]) / (8 * u + 2)) ** 2 < 1) & ((X + 2 * Z + 3 * Y) % 3 > 0.6), "l")
        ebenen.append(p1)
    S.plus(ell(0, H * 0.85, 0, 14 * u + 3, 7 * u + 2, 14 * u + 3), "l")
    S.rendern((-R, -2, -R), (R, H + 12 * u, R), versatz=(0.5, 0.01, 0.5))
    for (x, y, z) in ebenen:
        cx, cy, cz = round(x * 0.8), round(y - 1), round(z * 0.8)
        for xx, zz in scheibe(3 * u + 1.5, cx, cz):
            w.setze(xx, cy, zz, w.b("birch_planks"))
        for xx, zz in kreisrand(2 * u + 1, cx, cz):
            for yy in range(cy + 1, cy + 4):
                w.setze(xx, yy, zz, w.b("smooth_quartz") if (xx + zz) % 3 else w.b("glass"))
        kuppel(w, w.b("waxed_oxidized_copper"), cx, cz, cy + 4, 2 * u + 1.5, form="zwiebel", spitze=None)
    for i in range(H * 3):
        a = i / 18 * 2 * math.pi
        y = i // 3
        if y > H * 0.7:
            break
        rr = rs + 1.5 - y / H * rs * 0.4
        w.setze(round(math.cos(a) * rr), y, round(math.sin(a) * rr), w.b("birch_slab", type="top", waterlogged=False))
    hohl(w, 3)
    return w


def sphinx(seed, g=2):
    """Große Sphinx: ein liegender Löwe mit Menschenkopf und gestreiftem Kopftuch aus Sandstein, zwischen den
    Pranken ein Tempelchen, davor eine Allee aus Obelisken und Widderstatuen."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    R = _r(50 * u)
    gelaende(w, R, art="sand", dichte=0.2)
    M = Mat(w, ["sandstone", "smooth_sandstone", "cut_sandstone", "chiseled_sandstone"] if st == 0 else
            ["red_sandstone", "smooth_red_sandstone", "cut_red_sandstone", "orange_terracotta"], kontrast=0.6)
    s = 2.6 * u
    S = Skulptur(w, s)
    S.mat("k", lambda x, y, z, *_: M(x, y, z, 0.5))
    S.mat("t", lambda x, y, z, lx, ly, lz: w.b("blue_terracotta") if int(ly * 1.4) % 2 else w.b("gold_block")
          if st == 0 else w.b("light_blue_terracotta"))
    S.plus(ell(-4, 3.5, 0, 9, 3.6, 4), "k")
    S.plus(ell(3, 5, 0, 4, 5, 3.6), "k")
    for sz in (-1, 1):
        S.plus(kap((4, 1.2, sz * 2.6), (12, 1.0, sz * 2.4), 1.4, 1.2), "k")
        S.plus(kap((-10, 1.5, sz * 3.0), (-6, 1.2, sz * 4.2), 1.6, 1.2), "k")
    S.plus(kap((-12, 2, 0), (-16, 1, 3), 0.8, 0.5), "k")
    S.plus(ell(5.5, 11, 0, 2.6, 3.0, 2.6), "k")
    S.plus(lambda X, Y, Z: (((X - 5) / 3.2) ** 2 + ((Y - 11.5) / 3.6) ** 2 + (Z / 3.4) ** 2 < 1) & (X < 6.8), "t")
    S.plus(lambda X, Y, Z: (X > 3) & (X < 6.5) & (Y > 5) & (Y < 9.5) & (np.abs(Z) < 3.0 - (9.5 - Y) * 0.2), "t")
    S.rendern((-18, -1, -8), (14, 16, 8), versatz=(0.5, 0.01, 0.5), dreh=dreh_y(-math.pi / 2))
    for k in range(5):
        for sx in (-1, 1):
            x, z = round(sx * 10 * u), round(R * 0.35 + k * (R * 0.55 / 5))
            for y in range(0, _r(14 * u)):
                bb = 1 if y < _r(14 * u) - 3 else 0
                for dx in range(-bb, bb + 1):
                    for dz in range(-bb, bb + 1):
                        w.setze(round(x) + dx, y, z + dz, M(x, y, z, y / 14))
            w.setze(round(x), _r(14 * u), z, w.b("gold_block"))
    hohl(w, 3)
    return w


def titanentor(seed, g=2):
    """Titanentor: zwei kolossale Steintitanen stemmen mit erhobenen Armen einen riesigen Torsturz mit Runenfries
    über eine Prachtstraße – ein Tor zwischen zwei Reichen."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    L = _r(50 * u)
    gelaende(w, L, art="wiese", dichte=0.2)
    M = Mat(w, ["stone", "andesite", "polished_andesite", "stone_bricks", "tuff"] if st == 0 else
            ["deepslate", "polished_deepslate", "deepslate_bricks", "tuff"], kontrast=0.8)
    for z in range(-L, L + 1):
        for x in range(-6, 7):
            w.setze(x, 0, z, w.b("stone_bricks") if (x + z) % 4 else w.b("polished_andesite"))
    s = 2.4 * u
    hoehe_figur = 0
    for sx in (-1, 1):
        S = Skulptur(w, s)
        S.mat("k", sk(M, 0, 30 * s))
        S.mat("a", bl(w, "gold_block" if st else "waxed_copper_block"))
        S.mat("d", bl(w, "gray_concrete"))
        S.mat("g", bl(w, "sea_lantern"))
        figur(S, "golem", "arme_hoch")
        S.rendern((-8, -1, -6), (8, 30, 6), versatz=(sx * (9 * s) + 0.5, 0.01, 0.5),
                  dreh=dreh_y(math.pi / 2 * sx))
    top = max(y for (x, y, z) in w.bloecke if abs(x) < 9 * s + 3 and abs(z) < 4)
    for x in range(-_r(13 * s), _r(13 * s) + 1):
        for z in range(-4, 5):
            for y in range(top - 1, top + 4):
                w.setze(x, y, z, M(x, y, z, 0.8) if y != top + 1 or abs(z) != 4 else
                        w.b("gold_block") if x % 3 else w.b("chiseled_stone_bricks"))
    hohl(w, 3)
    return w


def labyrinth(seed, g=2):
    """Großes Labyrinth: ein riesiger quadratischer Irrgarten aus hohen Steinmauern mit Efeu, Fackeln an den
    Ecken, vier Tortürmen und einem goldenen Tempel in der Mitte."""
    w = welt(seed)
    u = U[g]
    n = _r(9 * u + 3)
    zell = 4
    L = n * zell
    gelaende(w, L // 2 + 8, art="wiese", dichte=0.1)
    M = Mat(w, ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "cobblestone"], kontrast=0.8)
    rng = w.rng
    wand = set()
    for i in range(n + 1):
        for k in range(L + 1):
            wand.add((i * zell, k))
            wand.add((k, i * zell))
    besucht = {(0, 0)}
    stack = [(0, 0)]
    while stack:
        cx, cz = stack[-1]
        nb = [(cx + dx, cz + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= cx + dx < n and 0 <= cz + dz < n and (cx + dx, cz + dz) not in besucht]
        if not nb:
            stack.pop()
            continue
        nx, nz = nb[int(rng.integers(len(nb)))]
        if nx != cx:
            xw = max(cx, nx) * zell
            for k in range(1, zell):
                wand.discard((xw, cz * zell + k))
        else:
            zw = max(cz, nz) * zell
            for k in range(1, zell):
                wand.discard((cx * zell + k, zw))
        besucht.add((nx, nz))
        stack.append((nx, nz))
    m = n // 2
    for x in range((m - 1) * zell + 1, (m + 2) * zell):
        for z in range((m - 1) * zell + 1, (m + 2) * zell):
            wand.discard((x, z))
    for k in range(1, zell):
        wand.discard((m * zell + k, 0))
        wand.discard((m * zell + k, L))
    H = 5 + int(u * 2)
    off = -L // 2
    for (x, z) in wand:
        for y in range(1, H + 1):
            w.setze(x + off, y, z + off, M(x, y, z, y / H))
        if rng.random() < 0.15:
            w.setze(x + off, H + 1, z + off, laub(w, "oak"))
    for x in range(L + 1):
        for z in range(L + 1):
            if (x, z) not in wand:
                w.setze(x + off, 0, z + off, w.b("gravel") if (x + z) % 5 else w.b("grass_block", snowy=False))
    st = P.Stil(w, wand="marmor", sockel="kalkstein", gesims="quartz", dach="mcw_gelb", holz="birch")
    a = zell
    P.gebaeude(w, st, -a, -a, a, a, y0=1, etagen=1, eh=6, dach="walm", tuer="south", gauben=False, kamine=0)
    kuppel(w, w.b("gold_block"), 0, 0, 10, a * 0.7, spitze="gold_block")
    for sx in (-1, 1):
        for sz in (-1, 1):
            P.turm(w, st, sx * (L // 2), sz * (L // 2), 1, H + _r(10 * u), 2.4, dach="kegel", krone=True,
                   fahne=None)
    hohl(w, 2)
    return w


TEIL6 = {
    "spiralzikkurat": ("Spiralzikkurat", spiralzikkurat),
    "titanenschmiede": ("Titanenschmiede", titanenschmiede),
    "walgebein": ("Walgebein", walgebein),
    "himmelsleiter": ("Himmelsleiter", himmelsleiter),
    "planetarium": ("Planetarium der Götter", planetarium),
    "weltenschlange": ("Weltenschlange", weltenschlange),
    "silberbaumstadt": ("Silberbaumstadt", silberbaumstadt),
    "sphinx": ("Große Sphinx", sphinx),
    "titanentor": ("Titanentor", titanentor),
    "labyrinth": ("Großes Labyrinth", labyrinth),
}

"""Weltwunder Teil 7 – Glaspalast, Blütenpalast, Kronenberg, Vergessener Koloss, Allsehendes Auge, Krakenriff,
Mondsicheltor, Baumkronenstadt, Sonnenobelisk, Gletscherpalast."""

from __future__ import annotations

import math

import numpy as np

import pracht as P
from lib import Rauschen, einfuegen, laub
from motive import figur
from pracht import Mat, gelaende
from skulptur import Skulptur, dreh_x, dreh_y, dreh_z, ell, kap, kreisrand, scheibe, torus
from weltwunder import U, _r, _stil, bl, hohl, platz, sk, welt
from weltwunder5 import fels, meer
from wueste_eis import kuppel


def glaspalast(seed, g=2):
    """Glaspalast: ein riesiges Gewächshaus aus Eisenrippen und Glas mit hoher Mittelkuppel und zwei Flügeln,
    innen ein Tropengarten mit Palmen und Brunnen, außen ein Barockparterre."""
    import wald2
    w = welt(seed)
    u = U[g]
    L, B = _r(40 * u), _r(14 * u)
    gelaende(w, L + 10, art="wiese", dichte=0.1)
    for x in range(-L, L + 1):
        for z in range(-B, B + 1):
            w.setze(x, 0, z, w.b("polished_andesite") if (x + z) % 2 else w.b("smooth_stone"))
    Hf = _r(10 * u)
    for x in range(-L, L + 1):
        for z in range(-B, B + 1):
            r = abs(z) / B
            hh = int(Hf * math.sqrt(max(0, 1 - r * r))) + 4
            if abs(z) == B or abs(x) == L:
                for y in range(1, hh):
                    w.setze(x, y, z, w.b("iron_block") if x % 5 == 0 or y == 1 else w.b("glass"))
            w.setze(x, hh, z, w.b("iron_block") if x % 5 == 0 else w.b("glass"))
    Rk = B + 4
    for y in range(4, 4 + Rk):
        rr = Rk * math.sqrt(max(0, 1 - ((y - 4) / Rk) ** 2))
        for x, z in kreisrand(rr):
            w.setze(x, y + Hf, z, w.b("iron_block") if (x + z) % 4 == 0 else w.b("glass"))
    for y in range(4, Hf + 4):
        for x, z in kreisrand(Rk):
            w.setze(x, y, z, w.b("iron_block") if (x + z) % 4 == 0 else w.b("glass"))
    w.setze(0, Hf + 4 + Rk, 0, w.b("gold_block"))
    rng = w.rng
    for i in range(6 + 4 * g):
        x, z = int(rng.integers(-L + 3, L - 2)), int(rng.integers(-B + 3, B - 2))
        einfuegen(w, wald2.palme(int(rng.integers(1, 10 ** 6)), H=6 + int(rng.integers(5))), x, 0, z)
    for x, z in scheibe(3):
        w.setze(x, 1, z, w.b("water", level=0))
    from dorf2 import blumenbeet
    for sx in (-1, 1):
        for i in range(3):
            blumenbeet(w, [(sx * (6 + i * 8) + dx, B + 6 + dz) for dx in range(4) for dz in range(3)])
    hohl(w, 2)
    return w


def bluetenpalast(seed, g=2):
    """Blütenpalast der Feenkönigin: ein Palast in Form einer riesigen Blüte – Blütenblätter als geschwungene
    Dächer und Wände, im Kelch ein Thronsaal aus Glas, Staubgefäße als leuchtende Türme."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    R = _r(38 * u)
    gelaende(w, R + 6, art="wiese", dichte=0.6)
    farbe = ["pink_concrete", "magenta_terracotta", "pink_terracotta", "white_concrete"] if st == 0 else \
        ["light_blue_concrete", "blue_terracotta", "light_blue_terracotta", "white_concrete"]
    S = Skulptur(w, 1.0)
    S.mat("p", lambda x, y, z, lx, ly, lz: w.b(farbe[min(3, int(math.hypot(lx, lz) / R * 4))]))
    S.mat("s", lambda x, y, z, *_: w.b("lime_concrete") if (x + z) % 3 else w.b("green_concrete"))
    S.mat("g", lambda x, y, z, *_: w.b("yellow_stained_glass") if (x + y) % 2 else w.b("white_stained_glass"))
    S.mat("l", bl(w, "shroomlight"))
    S.plus(kap((0, 0, 0), (0, 10 * u, 0), 4 * u, 3 * u), "s")
    for i in range(8):
        a = i / 8 * 2 * math.pi
        ca, sa = math.cos(a), math.sin(a)
        S.plus(lambda X, Y, Z, ca=ca, sa=sa: ((((X * ca + Z * sa) - R * 0.45) / (R * 0.5)) ** 2 +
                                              ((-X * sa + Z * ca) / (R * 0.22)) ** 2 < 1) &
               (np.abs(Y - 10 * u - 0.012 * ((X * ca + Z * sa) - R * 0.1) ** 2 * (1.6 / u)) < 1.2), "p")
    S.plus(lambda X, Y, Z: (np.abs(np.sqrt(X * X + Z * Z) - 8 * u) < 0.6) & (Y > 10 * u) & (Y < 22 * u), "g")
    for i in range(6):
        a = i / 6 * 2 * math.pi + 0.3
        px, pz = math.cos(a) * 5 * u, math.sin(a) * 5 * u
        S.plus(kap((px, 10 * u, pz), (px * 1.3, 28 * u, pz * 1.3), 0.7 * u, 0.5 * u), "s")
        S.plus(ell(px * 1.3, 29 * u, pz * 1.3, 1.6 * u, 1.6 * u, 1.6 * u), "l")
    S.rendern((-R - 2, -1, -R - 2), (R + 2, 34 * u, R + 2), versatz=(0.5, 0.01, 0.5))
    hohl(w, 2)
    return w


def kronenberg(seed, g=2):
    """Kronenberg: ein steiler Tafelberg, auf dessen Gipfel eine Festung in Form einer gewaltigen Krone thront –
    zackige goldene Zinnen mit Edelstein-Kuppeln, Serpentinenstraße und Stadttor am Fuß."""
    w = welt(seed)
    u = U[g]
    R = _r(42 * u)
    H = _r(30 * u)
    gelaende(w, R + 6, art="wiese", dichte=0.2)
    hoehe = fels(w, R * 0.8, H, spitz=2.5, rauh=0.15)
    top = H + 1
    Rk = _r(16 * u)
    gold = Mat(w, ["gold_block", "raw_gold_block", "yellow_concrete", "gold_block"], kontrast=0.6)
    for y in range(top, top + _r(12 * u)):
        for x, z in kreisrand(Rk):
            w.setze(x, y, z, gold(x, y, z, 0.5) if (y - top) % 5 else w.b("red_concrete"))
    for i in range(10):
        a = i / 10 * 2 * math.pi
        cx, cz = math.cos(a) * Rk, math.sin(a) * Rk
        zh = _r(12 * u) + _r(10 * u)
        for k in range(_r(10 * u)):
            r = 3.5 * u * (1 - k / (10 * u))
            for x, z in scheibe(max(0.6, r), round(cx), round(cz)):
                w.setze(x, top + _r(12 * u) + k, z, gold(x, 0, z, 0.5))
        edel = ["emerald_block", "diamond_block", "redstone_block", "lapis_block", "amethyst_block"][i % 5]
        for x, z in scheibe(1.6 * u + 0.5, round(cx), round(cz)):
            w.setze(x, top + zh, z, w.b(edel))
    st = P.Stil(w, wand="marmor", sockel="kalkstein", gesims="quartz", dach="mcw_rot", holz="birch")
    P.gebaeude(w, st, -_r(Rk * 0.5), -_r(Rk * 0.4), _r(Rk * 0.5), _r(Rk * 0.4), y0=top, etagen=3, eh=5,
               dach="walm", tuer="south", gauben=True, kamine=2)
    for i in range(int(R * 4)):
        t = i / (R * 4)
        a = t * 2.2 * math.pi
        rr = R * 0.78 * (1 - 0.45 * t)
        x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
        y = hoehe.get((x, z), 0)
        for d in (-1, 0, 1):
            w.setze(x + d, y, z, w.b("gravel") if i % 3 else w.b("stone_bricks"))
    hohl(w, 3)
    return w


def vergessener_koloss(seed, g=2):
    """Vergessener Koloss: der Kopf und eine Hand einer uralten Riesenstatue ragen moosüberwachsen aus dem
    Waldboden, Bäume wachsen auf dem Scheitel, Ranken hängen über die Augen."""
    import wald2
    w = welt(seed)
    u = U[g]
    R = _r(40 * u)
    gelaende(w, R, art="wald", dichte=0.6)
    M = Mat(w, ["mossy_stone_bricks", "mossy_cobblestone", "stone", "andesite", "moss_block"], kontrast=1.0)
    s = 2.4 * u
    S = Skulptur(w, s)
    S.mat("k", lambda x, y, z, *_: M(x, y, z, 0.5))
    S.mat("d", bl(w, "black_concrete"))
    S.plus(ell(0, 3, 0, 6, 8, 6.5), "k")
    S.plus(ell(0, 0.5, 4.5, 3, 2.4, 2.4), "k")
    S.plus(ell(0, 5, 5.8, 1.2, 2.4, 1.4), "k")
    for sz in (-1, 1):
        S.minus(ell(sz * 2.4, 6.5, 5.5, 1.3, 0.9, 1.2))
        S.plus(ell(sz * 6.3, 4.5, 0.5, 1.0, 2.0, 1.2), "k")
    S.plus(lambda X, Y, Z: (np.abs(Y - 11) < 1.5) & (X * X + Z * Z < 36) & ((np.arctan2(Z, X) * 5) % 2 < 1), "k")
    S.rendern((-8, -2, -8), (8, 13, 8), versatz=(0.5, -2 * s, 0.5), dreh=dreh_y(0.4) @ dreh_x(0.25))
    S2 = Skulptur(w, s)
    S2.mat("k", lambda x, y, z, *_: M(x, y, z, 0.5))
    S2.plus(kap((0, -2, 0), (0, 4, 0), 1.8, 1.6), "k")
    for i in range(4):
        S2.plus(kap(((i - 1.5) * 0.9, 4, 0), ((i - 1.5) * 1.1, 8 - abs(i - 1.5) * 0.6, 0.6 * (i % 2)), 0.45, 0.35), "k")
    S2.plus(kap((2, 3, 0), (3.5, 6, 0.4), 0.5, 0.45), "k")
    S2.rendern((-5, -3, -3), (5, 10, 3), versatz=(round(-R * 0.5) + 0.5, -2, round(R * 0.25) + 0.5))
    rng = w.rng
    oben = {}
    for (x, y, z) in w.bloecke:
        if y > oben.get((x, z), -99):
            oben[(x, z)] = y
    for (x, z), y in oben.items():
        if y > 6 and rng.random() < 0.004:
            einfuegen(w, wald2.laubbaum(int(rng.integers(1, 10 ** 6)), "oak", H=8), x, y + 1, z)
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 4 and rng.random() < 0.02 and w.frei(x, y - 1, z):
            for k in range(1, 4):
                if w.frei(x, y - k, z):
                    w.setze(x, y - k, z, w.b("vine", north=True, south=False, east=False, west=False, up=False))
    for i in range(6 + 2 * g):
        a = rng.random() * 2 * math.pi
        d = R * (0.5 + 0.4 * rng.random())
        einfuegen(w, wald2.laubbaum(int(rng.integers(1, 10 ** 6)), "oak", H=10 + int(rng.integers(5))),
                  round(math.cos(a) * d), 0, round(math.sin(a) * d))
    hohl(w, 3)
    return w


def allsehendes_auge(seed, g=2):
    """Allsehendes Auge: ein dreieckiger schwarzer Turm, an dessen Spitze in einem Ring aus Gold ein riesiges
    Auge mit leuchtender Iris schwebt; Runenpfeiler und ein dunkler Platz."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    Rp = _r(36 * u)
    M = Mat(w, ["polished_blackstone_bricks", "blackstone", "polished_deepslate", "obsidian"], kontrast=0.8)
    yp = platz(w, Rp, M, rand="polished_blackstone_brick", muster=["obsidian", "crying_obsidian",
                                                                   "polished_blackstone"],
               akzent="gilded_blackstone", lichter="soul_lantern", pfosten="polished_blackstone_wall")
    H = _r(60 * u)
    B = 12 * u
    for y in range(yp, yp + H):
        r = B * (1 - (y - yp) / H * 0.85)
        for x in range(-_r(r) - 1, _r(r) + 2):
            for z in range(-_r(r) - 1, _r(r) + 2):
                a = math.atan2(z, x)
                d = math.hypot(x, z)
                rr = r / math.cos(((a + math.pi / 2) % (2 * math.pi / 3)) - math.pi / 3)
                if rr - 1.2 < d <= rr:
                    w.setze(x, y, z, M(x, y, z, 0.5) if (y - yp) % 9 else w.b("gilded_blackstone"))
    S = Skulptur(w, 1.0)
    Ra = 9 * u
    S.mat("w", bl(w, "white_concrete"))
    S.mat("i", bl(w, "orange_concrete" if st == 0 else "lime_concrete"))
    S.mat("p", bl(w, "black_concrete"))
    S.mat("l", bl(w, "shroomlight" if st == 0 else "sea_lantern"))
    S.mat("g", bl(w, "gold_block"))
    S.plus(ell(0, 0, 0, Ra * 1.6, Ra * 0.8, Ra * 0.7), "w")
    S.plus(lambda X, Y, Z: (X * X + Y * Y < (Ra * 0.55) ** 2) & (Z > Ra * 0.35), "i")
    S.plus(lambda X, Y, Z: (X * X + Y * Y < (Ra * 0.25) ** 2) & (Z > Ra * 0.45), "p")
    S.plus(lambda X, Y, Z: (X * X + Y * Y < (Ra * 0.38) ** 2) & ((X * X + Y * Y) > (Ra * 0.3) ** 2) & (Z > Ra * 0.4),
           "l")
    S.plus(lambda X, Y, Z: (np.abs(np.sqrt(X * X + Y * Y) - Ra * 1.9) < 1.0) & (np.abs(Z) < 1.0), "g")
    S.rendern((-Ra * 2.2, -Ra * 2.2, -Ra), (Ra * 2.2, Ra * 2.2, Ra), versatz=(0.5, yp + H + Ra * 2.2, 0.5))
    hohl(w, 3)
    return w


def krakenriff(seed, g=2):
    """Krakenriff: aus dem Meer brechen die gewaltigen Fangarme eines Riesenkraken und umschlingen ein
    zerbrochenes Segelschiff, dazwischen Felsen, Strudel und Treibgut."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    R = _r(48 * u)
    meer(w, R)
    rng = w.rng
    for i in range(5):
        a = rng.random() * 2 * math.pi
        d = R * (0.5 + 0.4 * rng.random())
        fels(w, 5 * u + 2, 6 * u, cx=round(math.cos(a) * d), cz=round(math.sin(a) * d))
    haut = ["red_terracotta", "magenta_terracotta", "purple_terracotta"] if st == 0 else \
        ["purple_terracotta", "blue_terracotta", "cyan_terracotta"]
    S = Skulptur(w, 1.0)
    S.mat("t", lambda x, y, z, lx, ly, lz: w.b(haut[int(abs(lx + ly + lz) / 3) % 3]))
    S.mat("n", bl(w, "pink_terracotta" if st == 0 else "light_blue_terracotta"))
    for i in range(8):
        a = i / 8 * 2 * math.pi + rng.random() * 0.3
        r0 = 6 * u + rng.random() * 8 * u
        hmax = 18 * u + rng.random() * 14 * u
        pts = []
        for k in range(14):
            t = k / 13
            rr = r0 + t * 4 * u * math.sin(t * 3 + i)
            pts.append((math.cos(a + t * 1.4) * rr, -2 + hmax * math.sin(t * math.pi * 0.8),
                        math.sin(a + t * 1.4) * rr))
        for k in range(13):
            r1 = (2.6 * u + 0.8) * (1 - k / 14) + 0.4
            r2 = (2.6 * u + 0.8) * (1 - (k + 1) / 14) + 0.4
            S.plus(kap(pts[k], pts[k + 1], r1, r2), "t")
            if k % 2 == 0:
                x, y, z = pts[k]
                S.plus(ell(x, y - r1 * 0.6, z, r1 * 0.4, r1 * 0.4, r1 * 0.4), "n")
    S.rendern((-R, -3, -R), (R, 40 * u, R), versatz=(0.5, 0.01, 0.5))
    from wueste_eis import gestrandetes_schiff
    schiff = gestrandetes_schiff(seed, max(1, g - 1))
    for (x, y, z), b in schiff.bloecke.items():
        name = schiff.P.name(b)
        if "sand" in name or "grass" in name or y < 1:
            continue
        p = (x, y - 1, z)
        if p not in w.bloecke or w.P.name(w.bloecke[p]) == "minecraft:water":
            w.setze(*p, w.b(name[10:], **dict(schiff.P.eintraege[b][1])) if name.startswith("minecraft:") else w.b("spruce_planks"))
    hohl(w, 3)
    return w


def mondsicheltor(seed, g=2):
    """Mondsicheltor: eine riesige schwebende Mondsichel aus Kalzit und Perlmutt-Froschlicht steht als Tor über
    einer Spiegeltreppe, umringt von Sternsäulen mit Endstab-Kronen."""
    w = welt(seed)
    u = U[g]
    Rp = _r(36 * u)
    M = Mat(w, ["calcite", "smooth_quartz", "polished_diorite", "white_concrete"], kontrast=0.5)
    yp = platz(w, Rp, M, rand="quartz", muster=["calcite", "light_blue_terracotta", "sea_lantern"],
               akzent="sea_lantern", lichter="sea_lantern", pfosten="diorite_wall")
    Rm = 26 * u
    S = Skulptur(w, 1.0)
    S.mat("m", lambda x, y, z, *_: w.b("pearlescent_froglight", axis="y") if (x + y + z) % 5 == 0 else M(x, y, z, 0.5))
    S.plus(lambda X, Y, Z: (X * X + Y * Y < Rm * Rm) & ((X - Rm * 0.35) ** 2 + (Y - Rm * 0.15) ** 2 > (Rm * 0.82) ** 2)
           & (np.abs(Z) < 2.5 * u + 1), "m")
    S.rendern((-Rm - 2, -Rm - 2, -6), (Rm + 2, Rm + 2, 6), versatz=(0.5, yp + Rm + 2, 0.5), dreh=dreh_z(0.5))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x, z = round(math.cos(a) * Rp * 0.75), round(math.sin(a) * Rp * 0.75)
        for y in range(yp, yp + _r(14 * u)):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
        for d in ((0, 1, 0), (1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)):
            w.setze(x + d[0], yp + _r(14 * u) + d[1], z + d[2], w.b("end_rod", facing="up"))
    hohl(w, 3)
    return w


def baumkronenstadt(seed, g=2):
    """Baumkronenstadt: fünf Urwaldriesen tragen in ihren Kronen Plattformen mit Holzhäusern, verbunden durch
    Hängebrücken; Strickleitern und Laternen, am Boden Farne und Wurzeln."""
    import wald2
    w = welt(seed)
    u = U[g]
    R = _r(40 * u)
    gelaende(w, R, art="wald", dichte=0.6)
    rng = w.rng
    baeume = [(0, 0)] + [(round(math.cos(i / 4 * 2 * math.pi + 0.4) * R * 0.55),
                          round(math.sin(i / 4 * 2 * math.pi + 0.4) * R * 0.55)) for i in range(4)]
    plattformen = []
    for i, (x, z) in enumerate(baeume):
        H = _r((30 if i == 0 else 24) * u)
        einfuegen(w, wald2.dschungelriese(int(rng.integers(1, 10 ** 6)), H=H), x, 0, z)
        yp = _r(H * 0.55)
        for xx, zz in scheibe(5 * u + 2, x, z):
            w.setze(xx, yp, zz, w.b("jungle_planks") if (xx + zz) % 3 else w.b("stripped_jungle_log", axis="x"))
        for xx, zz in kreisrand(5 * u + 2, x, z):
            w.setze(xx, yp + 1, zz, w.b("jungle_fence", north=True, south=True, east=True, west=True,
                                        waterlogged=False))
        st = P.Stil(w, wand="holz_hell", sockel=["jungle_planks"], gesims="oak", dach="mcw_stroh", holz="jungle",
                    laeden=True, blumen=0.5)
        P.gebaeude(w, st, x + 2, z - 2, x + 2 + _r(3 * u + 2), z + 2, y0=yp + 1, etagen=1, eh=4, dach="sattel",
                   tuer="west", gauben=False, kamine=0, sockel_h=0)
        for y in range(1, yp):
            w.setze(x - _r(5 * u + 2) - 1, y, z, w.b("ladder", facing="west", waterlogged=False))
        plattformen.append((x, yp, z))
    x0, y0, z0 = plattformen[0]
    for (x1, y1, z1) in plattformen[1:]:
        n = max(abs(x1 - x0), abs(z1 - z0))
        for k in range(n + 1):
            t = k / n
            x = round(x0 + (x1 - x0) * t)
            z = round(z0 + (z1 - z0) * t)
            y = round(y0 + (y1 - y0) * t - math.sin(t * math.pi) * 2)
            w.setze(x, y, z, w.b("jungle_slab", type="bottom", waterlogged=False), ueberschreiben=False)
    hohl(w, 2)
    return w


def sonnenobelisk(seed, g=2):
    """Sonnenobelisk: ein himmelhoher Obelisk mit goldener Spitze im Zentrum eines riesigen Sonnenuhr-Platzes,
    zwölf Stundensäulen, Hieroglyphenbänder und ein Wasserbecken mit Lotus."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    Rp = _r(45 * u)
    M = Mat(w, ["smooth_sandstone", "cut_sandstone", "sandstone", "chiseled_sandstone"] if st == 0 else
            ["polished_granite", "granite", "smooth_red_sandstone", "red_sandstone"], kontrast=0.5)
    yp = platz(w, Rp, M, rand="sandstone" if st == 0 else "red_sandstone",
               muster=["smooth_sandstone", "gold_block", "cut_sandstone"] if st == 0 else
               ["polished_granite", "gold_block", "smooth_red_sandstone"], akzent="gold_block", lichter="lantern",
               pfosten="sandstone_wall" if st == 0 else "red_sandstone_wall", strahlen=12)
    H = _r(70 * u)
    B = 4 * u + 1
    for y in range(yp, yp + H):
        b = B * (1 - 0.35 * (y - yp) / H)
        for x in range(-_r(b), _r(b) + 1):
            for z in range(-_r(b), _r(b) + 1):
                rand = max(abs(x), abs(z)) == _r(b)
                glyph = rand and (y + x * 3 + z) % 4 == 0 and (y - yp) % 10 > 2
                w.setze(x, y, z, w.b("blue_terracotta") if glyph else M(x, y, z, 0.5))
    for k in range(_r(B) + 2):
        for x in range(-_r(B * 0.65) + k, _r(B * 0.65) - k + 1):
            for z in range(-_r(B * 0.65) + k, _r(B * 0.65) - k + 1):
                w.setze(x, yp + H + k, z, w.b("gold_block"))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        x, z = round(math.cos(a) * Rp * 0.8), round(math.sin(a) * Rp * 0.8)
        for y in range(yp, yp + _r(6 * u) + 2 * (i % 3 == 0)):
            w.setze(x, y, z, M(x, y, z, 0.7))
        w.setze(x, yp + _r(6 * u) + 2 * (i % 3 == 0), z, w.b("gold_block"))
    for x, z in scheibe(B + 6):
        if math.hypot(x, z) > B + 2:
            w.setze(x, yp - 1, z, w.b("water", level=0))
            if (x + z) % 5 == 0:
                w.setze(x, yp, z, w.b("lily_pad"))
    hohl(w, 3)
    return w


def gletscherpalast(seed, g=2):
    """Gletscherpalast: ein Palast aus Packeis und blauem Eis mit spitzen Kristalltürmen, Schneedächern und
    einem gefrorenen Wasserfall, auf einem verschneiten Felssockel."""
    w = welt(seed)
    u = U[g]
    R = _r(40 * u)
    gelaende(w, R, art="schnee", dichte=0.2)
    fels(w, R * 0.6, 8 * u, M=Mat(w, ["snow_block", "packed_ice", "stone", "snow_block"]), spitz=2.5, rauh=0.1)
    top = _r(8 * u) + 1
    eis = Mat(w, ["packed_ice", "blue_ice", "packed_ice", "snow_block"], kontrast=0.7)
    a, b = _r(12 * u), _r(8 * u)
    st = P.Stil(w, wand=eis, sockel=eis, gesims="quartz", dach=["quartz", "quartz", "diorite"] if False else
                "mcw_weiss", holz="birch", fenster="light_blue_stained_glass_pane" if False else "glass_pane",
                laeden=False, blumen=0, fensterart="bogen")
    P.gebaeude(w, st, -a, -b, a, b, y0=top, etagen=2, eh=6, dach="walm", tuer="south", gauben=True, kamine=0)
    S = Skulptur(w, 1.0)
    S.mat("k", lambda x, y, z, *_: w.b(["blue_ice", "packed_ice", "light_blue_stained_glass", "ice"][(x + y + z) % 4]))
    for i in range(9):
        ang = i / 9 * 2 * math.pi
        d = (a + 3) if i % 2 else (b + 5)
        x, z = math.cos(ang) * d, math.sin(ang) * d
        h = (22 + (i % 3) * 8) * u
        S.plus(kap((x, top - 2, z), (x * 1.05, top + h, z * 1.05), 2.2 * u + 0.8, 0.3), "k")
    S.plus(kap((0, top + 12, 0), (0, top + 50 * u, 0), 4 * u, 0.4), "k")
    S.rendern((-R, 0, -R), (R, top + 55 * u, R), versatz=(0.5, 0.01, 0.5))
    for y in range(1, top):
        for x in range(-3, 4):
            w.setze(x, y, round(R * 0.6) - 1, w.b("blue_ice") if (x + y) % 3 else w.b("packed_ice"))
    hohl(w, 3)
    return w


TEIL7 = {
    "glaspalast": ("Glaspalast", glaspalast),
    "bluetenpalast": ("Blütenpalast", bluetenpalast),
    "kronenberg": ("Kronenberg", kronenberg),
    "vergessener_koloss": ("Vergessener Koloss", vergessener_koloss),
    "allsehendes_auge": ("Allsehendes Auge", allsehendes_auge),
    "krakenriff": ("Krakenriff", krakenriff),
    "mondsicheltor": ("Mondsicheltor", mondsicheltor),
    "baumkronenstadt": ("Baumkronenstadt", baumkronenstadt),
    "sonnenobelisk": ("Sonnenobelisk", sonnenobelisk),
    "gletscherpalast": ("Gletscherpalast", gletscherpalast),
}

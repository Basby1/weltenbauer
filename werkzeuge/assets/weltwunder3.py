"""Weltwunder, Teil 3: Zwergentor, Mondtempel, Sternwarte, Kristallkuppel, Leerenriss."""

from __future__ import annotations

import math

import numpy as np

from lib import Rauschen, Verlauf, laub
import pracht as P
from pracht import Mat, gelaende, treppe
from skulptur import Skulptur, dreh_x, dreh_y, dreh_z, ell, kap, kasten, kegel, kreisrand, ohne, scheibe, spiegel_x, \
    torus, verbinde, zur_mitte
from motive import figur
from weltwunder import U, _r, _stil, bl, hohl, platz, schwebende_splitter, sk, welt


def _wand(w, name, **kw):
    return w.b(name, up=True, north="none", south="none", east="none", west="none", waterlogged=False, **kw)


# ============================================================================ 11 Zwergentor


def zwergentor(seed, g=2):
    """Zwergentor: ein gewaltiges Tor in einer Felswand, flankiert von zwei Zwergenkönigen mit Runenstäben,
    mit gestuftem Torrahmen, Runenband, Feuerbecken und Prunktreppe. Stil 1 Granit und Kupfer,
    Stil 2 Tiefenschiefer und Gold."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    rng = w.rng
    if st == 0:
        F = Mat(w, ["stone", "andesite", "granite", "tuff", "stone", "diorite", "gravel"], kontrast=1.3)
        Fa = Mat(w, ["polished_granite", "granite", "bricks", "polished_granite", "cut_copper" if False else
                     "terracotta"], kontrast=0.7)
        gold, tor, tor2, rand = "waxed_cut_copper", "waxed_weathered_cut_copper", "waxed_oxidized_cut_copper", \
            "polished_granite"
        K = Mat(w, ["polished_andesite", "andesite", "stone", "polished_andesite"], kontrast=0.6)
        bart = "granite"
    else:
        F = Mat(w, ["deepslate", "cobbled_deepslate", "tuff", "blackstone", "deepslate", "smooth_basalt"],
                kontrast=1.3)
        Fa = Mat(w, ["polished_deepslate", "deepslate_bricks", "deepslate_tiles", "polished_blackstone_bricks"],
                 kontrast=0.7)
        gold, tor, tor2, rand = "gold_block", "polished_blackstone_bricks", "gilded_blackstone", "polished_deepslate"
        K = Mat(w, ["polished_deepslate", "deepslate_tiles", "polished_deepslate"], kontrast=0.6)
        bart = "gold_block"
    W = _r(60 * u)
    D = _r(30 * u)
    H = _r(80 * u)
    r_n = Rauschen(w, 9)
    r_k = Rauschen(w, 3)
    F2 = _r(30 * u)     # halbe Fassadenbreite
    for x in range(-W, W + 1):
        for z in range(-D, 1 + _r(6 * u)):
            tx = abs(x) / W
            hh = H * (1 - tx ** 1.8) * (0.75 + 0.35 * r_n(x, 0, z)) - max(0, z + 2) * 3 + (r_k(x, 0, z) - 0.5) * 6
            if abs(x) <= F2 and z > 0:
                continue
            if abs(x) > F2 and z > 0:
                hh = min(hh, (6 * u - z) * 4)
            for y in range(0, int(hh) + 1):
                w.setze(x, y, z, F(x, y, z, y / H))
            if hh > 1 and r_k(x, 5, z) > 0.62 and st == 0:
                w.setze(x, int(hh), z, w.b("grass_block", snowy=False) if hh < H * 0.5 else w.b("snow_block"))
    # Fassade (ebene Fläche bei z = 0) mit Torrahmen
    Ht = _r(30 * u)
    bt = _r(9 * u)
    yf = _r(58 * u)
    for x in range(-F2, F2 + 1):
        for y in range(0, yf):
            d = max(abs(x) - bt, 0)
            bogen = y - Ht + 1 > math.sqrt(max(0, bt * bt - x * x)) * 0.0 and y >= Ht - 0 or abs(x) > bt
            innen = abs(x) <= bt and (y < Ht or (y - Ht) ** 2 + x * x * 0.5 < (bt * 0.7) ** 2)
            for z in range(-2, 1):
                if innen:
                    w.bloecke.pop((x, y, z), None)
                    continue
                rahmen = abs(x) <= bt + 3 and (y < Ht + bt + 3)
                if rahmen:
                    stufe = max(abs(x) - bt, 0)
                    w.setze(x, y, z + (1 if stufe in (1, 2) else 0), Fa(x, y, z, 0.6))
                    w.setze(x, y, z, Fa(x, y, z, 0.6))
                elif (y + abs(x)) % 11 == 0 and y > 3:
                    w.setze(x, y, z, w.b(gold))
                else:
                    w.setze(x, y, z, Fa(x, y, z, 0.3 + 0.5 * y / yf) if y < yf - 3 else F(x, y, z, 0.8))
    # Tor (zweiflügelig, mit Goldrunen)
    for x in range(-bt, bt + 1):
        for y in range(0, Ht + bt):
            innen = (y < Ht or (y - Ht) ** 2 + x * x * 0.5 < (bt * 0.7) ** 2)
            if not innen:
                continue
            z = -3
            if x == 0:
                b = w.b(gold)
            elif (y % 6 == 0) or (abs(x) % 4 == 0 and y % 2 == 0):
                b = w.b(tor2)
            else:
                b = w.b(tor)
            w.setze(x, y, z, b)
    # Runenband über dem Tor
    yr = Ht + bt + 5
    for x in range(-F2 + 2, F2 - 1):
        for y in (yr, yr + 3):
            w.setze(x, y, 1, treppe(w, rand, "north", "top" if y == yr else "bottom"))
        w.setze(x, yr + 1, 0, w.b(gold) if x % 3 else Fa(x, yr + 1, 0, 0.5))
        w.setze(x, yr + 2, 0, w.b("chiseled_deepslate" if st else "chiseled_stone_bricks") if x % 3 == 0 else
                Fa(x, yr + 2, 0, 0.5))
    # Prunktreppe
    br = bt + 4
    for k in range(_r(6 * u)):
        for x in range(-br - k, br + k + 1):
            for zz in range(1, 2 + k * 0 + 1):
                pass
            z = 1 + k
            w.setze(x, _r(6 * u) - 1 - k, z, treppe(w, rand, "north"))
            for y in range(0, _r(6 * u) - 1 - k):
                w.setze(x, y, z, Fa(x, y, z, 0.2))
    plat = _r(6 * u)
    for x in range(-bt, bt + 1):
        for z in range(-2, 1):
            w.setze(x, plat - 1, z, w.b(rand if False else "polished_andesite" if st == 0 else "polished_deepslate"))
    # Zwergenkönige
    for sx in (-1, 1):
        S = Skulptur(w, 3.1 * u)
        S.mat("k", sk(K, plat, plat + 30 * u))
        S.mat("a", bl(w, bart))
        S.mat("d", bl(w, gold))
        S.mat("g", bl(w, "shroomlight" if st == 0 else "sea_lantern"))
        figur(S, "zwerg", "stab")
        cx = sx * (bt + _r(14 * u))
        S.rendern((-7, -1, -5), (7, 22, 7), versatz=(cx + 0.5, plat + 3.01, 7 * u),
                  dreh=dreh_y(0.0) if sx < 0 else dreh_y(0.0) @ np.diag([-1, 1, 1]))
        for x in range(cx - _r(9 * u), cx + _r(9 * u) + 1):
            for z in range(0, _r(14 * u)):
                for y in range(plat, plat + 3):
                    rnd = x in (cx - _r(9 * u), cx + _r(9 * u)) or z in (0, _r(14 * u) - 1)
                    w.setze(x, y, z, w.b(gold) if rnd and y == plat + 1 else Fa(x, y, z, 0.4))
    # Feuerbecken
    for sx in (-1, 1):
        for k in (0, 1):
            x = sx * (br + 3 + k * 8)
            z = _r(8 * u) + k * 4
            for y in range(0, 4):
                w.setze(x, y, z, _wand(w, "polished_blackstone_wall") if y < 3 else
                        w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
            w.setze(x, 0, z, w.b("polished_blackstone"))
    hohl(w, 3)
    return w


# ============================================================================ 12 Mondtempel


def mondtempel(seed, g=2):
    """Mondtempel: runder Elfentempel mit schlanken Säulen, Rippenkuppel, Spiegelbecken und einer schwebenden
    Mondsichel über dem Scheitel. Stil 1 Mond (Silber und Blau), Stil 2 Sonne (Sandstein und Gold)."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    if st == 0:
        M = Mat(w, ["polished_diorite", "calcite", "smooth_quartz", "quartz_bricks", "white_concrete"], kontrast=0.7)
        boden = Mat(w, "marmor")
        saeule, akzent, licht = "quartz_pillar", "light_blue_stained_glass", "sea_lantern"
        rand = "quartz"
        rippe = Mat(w, ["smooth_quartz", "quartz_bricks", "diorite"], kontrast=0.6)
        sym = ["sea_lantern", "white_stained_glass", "light_blue_stained_glass"]
        muster = ["polished_diorite", "quartz_bricks", "lapis_block"]
    else:
        M = Mat(w, ["smooth_sandstone", "cut_sandstone", "sandstone", "smooth_sandstone", "end_stone"], kontrast=0.7)
        boden = Mat(w, "sandstein")
        saeule, akzent, licht = "cut_sandstone", "orange_stained_glass", "shroomlight"
        rand = "smooth_sandstone"
        rippe = Mat(w, ["smooth_sandstone", "cut_sandstone", "gold_block"], kontrast=0.6)
        sym = ["gold_block", "raw_gold_block", "yellow_stained_glass"]
        muster = ["smooth_sandstone", "cut_sandstone", "gold_block"]
    R = 18 * u
    Rp = _r(R + 10 * u)
    y0 = platz(w, Rp, boden, rand=rand, muster=muster, akzent="chiseled_quartz_block" if st == 0 else
               "chiseled_sandstone", lichter="lantern", pfosten="diorite_wall" if st == 0 else "sandstone_wall")
    # Podest mit Stufen
    for k in range(3):
        for x, z in kreisrand(R + 3 - k):
            w.setze(x, y0 + k, z, treppe(w, rand, zur_mitte(x, z)))
        for x, z in scheibe(R + 2 - k):
            if w.frei(x, y0 + k, z):
                w.setze(x, y0 + k, z, M(x, y0 + k, z, 0.2))
    yb = y0 + 3
    # Spiegelbecken mit Sockel
    for x, z in scheibe(R * 0.55):
        d = math.hypot(x, z)
        w.setze(x, yb - 1, z, w.b("water", level=0) if d < R * 0.55 - 1.2 else w.b(muster[1]))
        w.setze(x, yb - 2, z, M(x, yb - 2, z, 0.1))
    for x, z in kreisrand(R * 0.55):
        w.setze(x, yb, z, treppe(w, rand, zur_mitte(x, z), "bottom"))
    # Säulenkranz
    n = 16 if u < 1.3 else 24
    Hs = _r(16 * u)
    for i in range(n):
        a = i / n * 2 * math.pi
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        for y in range(yb, yb + Hs):
            w.setze(x, y, z, w.b(saeule, axis="y") if saeule.endswith("pillar") else w.b(saeule))
        w.setze(x, yb, z, w.b(muster[1]))
        w.setze(x, yb + Hs - 1, z, w.b("chiseled_quartz_block" if st == 0 else "chiseled_sandstone"))
        for dx, dz, f in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
            w.setze(x + dx, yb + Hs - 1, z + dz, treppe(w, rand, f, "top"), ueberschreiben=False)
            w.setze(x + dx, yb, z + dz, treppe(w, rand, f), ueberschreiben=False)
    # Gebälkring
    ye = yb + Hs
    for x, z in scheibe(R + 1.5):
        if math.hypot(x, z) > R - 1.5:
            w.setze(x, ye, z, M(x, ye, z, 0.8))
    for x, z in kreisrand(R + 2):
        w.setze(x, ye, z, treppe(w, rand, zur_mitte(x, z), "top"))
        w.setze(x, ye + 1, z, w.b(f"{rand}_slab", type="bottom", waterlogged=False) if rand != "quartz" else
                w.b("quartz_slab", type="bottom", waterlogged=False))
    for x, z in kreisrand(R):
        w.setze(x, ye + 1, z, w.b(akzent))
    # Rippenkuppel (Bögen, dazwischen offen)
    S = Skulptur(w, 1.0)
    S.mat("r", sk(rippe, ye, ye + R))
    S.mat("l", bl(w, licht))
    nr = 12
    for i in range(nr):
        a = i / nr * math.pi
        S.plus(lambda X, Y, Z, a=a: (np.abs(np.hypot(np.hypot(X, Z), Y - ye) - R) < 0.9 * u + 0.25)
               & (np.abs(-X * math.sin(a) + Z * math.cos(a)) < 0.7 * u + 0.2) & (Y >= ye), "r")
    S.plus(torus(0, ye + R * 0.5, 0, R * 0.866, 0.7 * u + 0.2, achse="y"), "r")
    S.plus(ell(0, ye + R, 0, 2.2 * u, 1.4 * u, 2.2 * u), "l")
    S.rendern((-R - 2, ye, -R - 2), (R + 2, ye + R + 3, R + 2))
    # schwebende Sichel / Sonnenscheibe
    Sm = Skulptur(w, 1.0)
    v = Verlauf(w, "Sym", sym)
    Sm.mat("s", lambda x, y, z, lx, ly, lz: v(min(2, abs(lz) * 1.2 + 0.3 * (1 - abs(ly) / (8 * u))), x, y, z))
    rm = 9 * u
    cy = ye + R + 14 * u
    if st == 0:
        Sm.plus(ohne(lambda X, Y, Z: (X * X + Y * Y <= rm * rm) & (np.abs(Z) < 1.2 * u),
                     lambda X, Y, Z: ((X - rm * 0.45) ** 2 + (Y - rm * 0.15) ** 2 <= (rm * 0.85) ** 2)), "s")
    else:
        Sm.plus(lambda X, Y, Z: (X * X + Y * Y <= (rm * 0.65) ** 2) & (np.abs(Z) < 1.3 * u), "s")
        for k in range(12):
            a = k / 12 * 2 * math.pi
            Sm.plus(kap((math.cos(a) * rm * 0.7, math.sin(a) * rm * 0.7, 0),
                        (math.cos(a) * rm * 1.15, math.sin(a) * rm * 1.15, 0), 0.9 * u, 0.3), "s")
    Sm.rendern((-rm * 1.3, -rm * 1.3, -2 * u), (rm * 1.3, rm * 1.3, 2 * u), versatz=(0, cy, 0), dreh=dreh_y(0.6))
    # Lichtsäule vom Becken zur Sichel (Endstäbe)
    for y in range(yb, int(ye + R - 2)):
        if y % 2 == 0:
            w.setze(0, y, 0, w.b("end_rod", facing="up"))
    for x, z in scheibe(2):
        w.setze(x, yb - 1, z, w.b(licht))
    # Bäume im Platz
    import baeume as B
    for i in range(6):
        a = i / 6 * 2 * math.pi + 0.5
        tx, tz = round(math.cos(a) * (R + 7 * u)), round(math.sin(a) * (R + 7 * u))
        baum = B.ARTEN["kirschbaum" if st == 0 else "akazie"][1](int(w.rng.integers(1, 10 ** 6)), 0)
        from lib import einfuegen
        einfuegen(w, baum, tx, y0 - 1, tz)
    hohl(w, 2)
    return w


# ============================================================================ 13 Sternwarte


def sternwarte(seed, g=2):
    """Große Sternwarte: hoher Turm mit Kuppel und Sehschlitz, ein gewaltiges Fernrohr ragt zum Himmel,
    daneben eine Armillarsphäre aus Goldringen über einem Sternkarten-Platz. Stil 1 Stein und Kupfer,
    Stil 2 Nachtblau und Gold."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    if st == 0:
        stil = P.Stil(w, wand="kalkstein", sockel="graustein", gesims="stone_brick", dach="kupfer", holz="spruce",
                      laeden=False)
        boden = Mat(w, "graustein")
        ring, rohr, licht = "gold_block", "waxed_cut_copper", "lantern"
        muster = ["polished_andesite", "stone_bricks", "gold_block"]
        kuppel = Mat(w, ["waxed_oxidized_cut_copper", "waxed_weathered_cut_copper", "waxed_oxidized_copper"])
    else:
        stil = P.Stil(w, wand="tiefenschiefer", sockel="schwarzstein", gesims="deepslate_brick", dach="blau",
                      holz="dark_oak", laeden=False, fenster="blue_stained_glass_pane")
        boden = Mat(w, "tiefenschiefer")
        ring, rohr, licht = "gold_block", "lapis_block", "soul_lantern"
        muster = ["polished_deepslate", "lapis_block", "gold_block"]
        kuppel = Mat(w, ["lapis_block", "blue_terracotta", "blue_concrete", "lapis_block"])
    Rp = _r(30 * u)
    y0 = platz(w, Rp, boden, rand="stone_brick" if st == 0 else "deepslate_brick", muster=muster,
               akzent="chiseled_stone_bricks" if st == 0 else "chiseled_deepslate", lichter=licht,
               pfosten="stone_brick_wall" if st == 0 else "deepslate_brick_wall", strahlen=12)
    # Sternbilder im Boden (Goldpunkte)
    rng = w.rng
    for _ in range(int(60 * u)):
        a, d = rng.random() * 2 * math.pi, rng.random() * Rp * 0.9
        w.setze(round(math.cos(a) * d), y0 - 1, round(math.sin(a) * d), w.b("gold_block" if rng.random() < 0.6
                                                                             else "sea_lantern"))
    # Turm (rund) mit Kuppel
    tx, tz = round(-Rp * 0.3), round(-Rp * 0.25)
    Rt = 7.5 * u
    Ht = _r(40 * u)
    P.turm(w, stil, tx, tz, y0, Ht, Rt, form="rund", dach="platt", krone=True, fenster=7)
    yk = y0 + Ht + 1
    Sk = Skulptur(w, 1.0)
    Sk.mat("k", sk(kuppel, yk, yk + Rt))
    Rk = Rt + 1.2
    Sk.plus(ohne(ell(0, 0, 0, Rk, Rk, Rk), lambda X, Y, Z: (Y < 0) | ((np.abs(X * 0.7 + Z) < 1.8 * u) & (X - Z * 0.7 > 0))), "k")
    Sk.rendern((-Rk - 1, 0, -Rk - 1), (Rk + 1, Rk + 1, Rk + 1), versatz=(tx + 0.5, yk, tz + 0.5))
    # Fernrohr aus dem Kuppelschlitz
    Sf = Skulptur(w, 1.0)
    Sf.mat("r", bl(w, rohr))
    Sf.mat("g", bl(w, ring))
    Sf.mat("l", bl(w, "light_blue_stained_glass"))
    a0 = np.array([0, Rk * 0.3, 0.0])
    e = np.array([1, 1.25, -0.7]) / np.linalg.norm([1, 1.25, -0.7])
    L = 26 * u
    Sf.plus(kap(tuple(a0 - e * 5), tuple(a0 + e * L), 2.0 * u, 2.8 * u), "r")
    for k in range(4):
        p = a0 + e * (L * (0.2 + 0.25 * k))
        Sf.plus(lambda X, Y, Z, p=p: (np.abs((X - p[0]) * e[0] + (Y - p[1]) * e[1] + (Z - p[2]) * e[2]) < 0.6)
                & (((X - p[0]) ** 2 + (Y - p[1]) ** 2 + (Z - p[2]) ** 2) < (3.0 * u + 0.4) ** 2), "g")
    pe = a0 + e * (L + 0.5)
    Sf.plus(ell(*pe, 2.4 * u, 2.4 * u, 2.4 * u), "l")
    Sf.rendern((-8, -8, -L - 6), (L + 6, L + 6, 8), versatz=(tx + 0.5, yk, tz + 0.5))
    # Armillarsphäre
    ax, az = round(Rp * 0.35), round(Rp * 0.3)
    ys = y0 + _r(6 * u)
    for y in range(y0, ys):
        for x in range(ax - 2, ax + 3):
            for z in range(az - 2, az + 3):
                if abs(x - ax) + abs(z - az) <= 3 - (y - y0 > 1):
                    w.setze(x, y, z, stil.sockel(x, y, z, 0.5))
    Ra = 10 * u
    cy = ys + Ra + 1
    Sa = Skulptur(w, 1.0)
    Sa.mat("g", bl(w, ring))
    Sa.mat("c", bl(w, rohr))
    Sa.mat("l", bl(w, "sea_lantern" if st else "shroomlight"))
    d = 0.55 * u + 0.25
    Sa.plus(torus(0, 0, 0, Ra, d, achse="y"), "g")
    Sa.plus(torus(0, 0, 0, Ra, d, achse="z"), "g")
    Sa.plus(torus(0, 0, 0, Ra, d, achse="x"), "c")
    Sa.plus(lambda X, Y, Z: (np.abs(np.hypot(X, Y * 0.92 + Z * 0.4) - Ra * 0.82) < d)
            & (np.abs(-Y * 0.4 + Z * 0.92) < d), "c")
    Sa.plus(ell(0, 0, 0, 2.6 * u, 2.6 * u, 2.6 * u), "l")
    Sa.plus(kap((0, -Ra - 2, 0), (0, Ra + 2, 0), 0.5), "g")
    Sa.rendern((-Ra - 3, -Ra - 3, -Ra - 3), (Ra + 3, Ra + 3, Ra + 3), versatz=(ax + 0.5, cy, az + 0.5),
               dreh=dreh_z(0.35))
    hohl(w, 2)
    return w


# ============================================================================ 14 Kristallkuppel


def kristallkuppel(seed, g=2):
    """Kristallkuppel: eine riesige Glaskuppel mit Rippen über einem kleinen Stadtgarten – Häuschen, Turm,
    Teiche, Brücken und Bäume. Stil 1 Meereskuppel (Prismarin, Seelaternen, Wasserbecken),
    Stil 2 Gartenkuppel (Weiß und Gold, Blumen und Kirschbäume)."""
    import baeume as B
    from lib import einfuegen
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    rng = w.rng
    R = 36 * u
    if st == 0:
        rib = Mat(w, ["dark_prismarine", "prismarine_bricks", "prismarine"], kontrast=0.6)
        glas = ["light_blue_stained_glass", "cyan_stained_glass", "glass", "light_blue_stained_glass"]
        stil = P.Stil(w, wand="prismarin", sockel="graustein", gesims="prismarine_brick", dach="blau",
                      holz="warped" if False else "dark_oak", laeden=False, fenster="cyan_stained_glass_pane",
                      licht="sea_lantern")
        sockel = Mat(w, "prismarin")
        baum_art = "trauerweide"
    else:
        rib = Mat(w, ["smooth_quartz", "quartz_bricks", "gold_block", "smooth_quartz"], kontrast=0.6)
        glas = ["glass", "white_stained_glass", "glass", "yellow_stained_glass"]
        stil = P.Stil(w, wand="putz", sockel="kalkstein", gesims="quartz", dach="kupfer", holz="birch",
                      laeden=True, fachwerk=False)
        sockel = Mat(w, "marmor")
        baum_art = "kirschbaum"
    vg = Verlauf(w, "Gl", glas)
    # Ringsockel
    for x, z in scheibe(R + 3):
        d = math.hypot(x, z)
        for y in range(0, 4):
            if d > R - 1 or y == 0:
                w.setze(x, y, z, sockel(x, y, z, y / 4))
    for x, z in kreisrand(R + 4):
        w.setze(x, 0, z, treppe(w, "prismarine_brick" if st == 0 else "quartz", zur_mitte(x, z)))
    # Kuppel
    S = Skulptur(w, 1.0)
    S.mat("g", lambda x, y, z, lx, ly, lz: vg((ly / R) * 3, x, y, z))
    S.mat("r", sk(rib, 3, 3 + R))
    S.plus(lambda X, Y, Z: (np.abs(np.sqrt(X * X + Y * Y + Z * Z) - R) < 0.55) & (Y >= 0), "g")
    for i in range(16):
        a = i / 16 * math.pi
        S.plus(lambda X, Y, Z, a=a: (np.abs(np.sqrt(X * X + Y * Y + Z * Z) - R) < 1.2)
               & (np.abs(-X * math.sin(a) + Z * math.cos(a)) < 0.65) & (Y >= 0), "r")
    for hy in (0.35, 0.68, 0.9):
        S.plus(torus(0, R * hy, 0, R * math.sqrt(1 - hy * hy), 0.9, achse="y"), "r")
    S.plus(ell(0, R, 0, 3, 2, 3), "r")
    S.rendern((-R - 2, -1, -R - 2), (R + 2, R + 3, R + 2), versatz=(0, 4, 0))
    # Laterne auf dem Scheitel
    for y in range(int(R) + 6, int(R) + 10):
        w.setze(0, y, 0, w.b("sea_lantern" if st == 0 else "gold_block") if y == int(R) + 9 else
                _wand(w, "prismarine_wall" if st == 0 else "diorite_wall"))
    # Tore (4)
    for a in range(4):
        dx, dz = [(1, 0), (-1, 0), (0, 1), (0, -1)][a]
        for k in range(-2, 3):
            for y in range(4, 10):
                x = round(dx * (R - 0.5) - dz * k * 1)
                z = round(dz * (R - 0.5) + dx * k * 1)
                for t in (-1, 0, 1):
                    w.bloecke.pop((x + dx * t, y, z + dz * t), None)
    # Innen: Garten mit Wegen, Teich, Häusern und Turm
    gelaende(w, R - 2, art="wiese", wege=[((-R, 0), (R, 0)), ((0, -R), (0, R))], dichte=1.2) if False else None
    rg = Rauschen(w, 4)
    for x, z in scheibe(R - 2):
        d = math.hypot(x, z)
        weg = abs(x) <= 1 or abs(z) <= 1 or abs(d - R * 0.45) < 1.2
        teich = math.hypot(x - R * 0.42, z + R * 0.42) < R * 0.18
        y = 3
        if teich:
            w.setze(x, y, z, w.b("water", level=0))
            w.setze(x, y - 1, z, w.b("clay"))
        elif weg:
            w.setze(x, y, z, w.b("polished_andesite" if st == 0 else "smooth_quartz") if (x + z) % 3 else
                    w.b("prismarine_bricks" if st == 0 else "gold_block"))
        else:
            w.setze(x, y, z, w.b("grass_block", snowy=False) if rg(x, 0, z) < 0.75 else w.b("moss_block"))
            r = rng.random()
            if r < 0.3:
                w.setze(x, y + 1, z, w.b("grass"))
            elif r < 0.4:
                w.setze(x, y + 1, z, w.b(["poppy", "azure_bluet", "cornflower", "allium", "oxeye_daisy",
                                          "pink_tulip"][int(rng.integers(6))]))
    for x, z in scheibe(R * 0.18 - 1, round(R * 0.42), round(-R * 0.42)):
        if rng.random() < 0.08:
            w.setze(x, 4, z, w.b("lily_pad"))
    # Häuser
    for (hx, hz, rot) in ((-R * 0.5, -R * 0.35, 0), (-R * 0.55, R * 0.3, 1), (R * 0.4, R * 0.45, 0)):
        hx, hz = int(hx), int(hz)
        P.gebaeude(w, stil, hx - 3, hz - 2, hx + 3, hz + 2, y0=4, etagen=2, eh=4,
                   dach="sattel" if rot == 0 else "walm", tuer="south" if hz < 0 else "north", kamine=0,
                   gauben=False)
    P.turm(w, stil, 0, 0, 4, _r(20 * u), 3.2 * u, dach="zwiebel" if st == 0 else "glocke",
           fahne=["cyan_wool", "white_wool"] if st == 0 else ["yellow_wool", "white_wool"])
    # Bäume
    for (bx, bz) in ((-R * 0.25, -R * 0.62), (R * 0.65, -R * 0.1), (-R * 0.2, R * 0.6), (R * 0.15, -R * 0.22),
                     (-R * 0.7, 0.05 * R)):
        einfuegen(w, B.ARTEN[baum_art][1](int(rng.integers(1, 10 ** 6)), 0), int(bx), 3, int(bz))
    hohl(w, 2)
    return w


# ============================================================================ 15 Leerenriss


def leerenriss(seed, g=2):
    """Leerenriss: zwei geneigte Obsidiantürme spannen einen klaffenden Riss in eine andere Welt auf;
    ringsum schweben Bruchstücke mit Chorusgewächsen und Endstäben. Stil 1 End-Violett,
    Stil 2 Schattenriss in Blutrot."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    rng = w.rng
    if st == 0:
        T = Mat(w, ["obsidian", "crying_obsidian", "obsidian", "purpur_block", "end_stone_bricks"], kontrast=1.1)
        Bo = Mat(w, ["end_stone", "end_stone_bricks", "end_stone", "purpur_block", "obsidian"], kontrast=1.2)
        riss = ["black_concrete", "black_stained_glass", "purple_stained_glass", "magenta_stained_glass",
                "pink_stained_glass"]
        licht = "end_rod"
        boden_art = "stein"
    else:
        T = Mat(w, ["blackstone", "polished_blackstone_bricks", "crying_obsidian", "obsidian", "gilded_blackstone"],
                kontrast=1.1)
        Bo = Mat(w, ["blackstone", "basalt", "netherrack", "crimson_nylium", "soul_soil"], kontrast=1.2)
        riss = ["black_concrete", "black_stained_glass", "red_stained_glass", "orange_stained_glass",
                "yellow_stained_glass"]
        licht = "shroomlight"
        boden_art = "asche"
    H = 56 * u
    abst = 15 * u
    S = Skulptur(w, 1.0)
    S.mat("t", sk(T, 0, H))
    v = Verlauf(w, "Riss", riss)
    r_r = Rauschen(w, 2.5)
    S.mat("r", lambda x, y, z, lx, ly, lz: v(min(4, abs(lx) / (3.6 * u * (1 - abs(ly - H * 0.5) / (H * 0.45)) + 0.6)
                                                 * 4 + (r_r(x, y, z) - 0.5) * 0.8), x, y, z))
    for s in (-1, 1):
        fuss = (s * abst * 1.4, 0, 0)
        spitze = (s * abst * 0.35, H, s * 2)
        S.plus(kap(fuss, spitze, 5.5 * u, 1.2 * u), "t")
        for k in range(4):
            a = rng.random() * 2 * math.pi
            t = 0.2 + k * 0.18
            p = (fuss[0] + (spitze[0] - fuss[0]) * t, H * t, fuss[2] + (spitze[2] - fuss[2]) * t)
            S.plus(kap(p, (p[0] + math.cos(a) * 7 * u, p[1] + 5 * u, p[2] + math.sin(a) * 7 * u), 1.6 * u, 0.3),
                   "t")
    # Riss: zackige Linse zwischen den Türmen
    def riss_f(X, Y, Z):
        t = (Y - H * 0.08) / (H * 0.84)
        breite = 3.8 * u * np.sin(np.clip(t, 0, 1) * np.pi) ** 0.8 * (0.8 + 0.4 * np.sin(Y * 0.7 / u))
        mitte = 2.0 * u * np.sin(Y * 0.18 / u)
        return (t > 0) & (t < 1) & (np.abs(X - mitte) < breite) & (np.abs(Z) < 0.9)
    S.mat("rr", lambda x, y, z, lx, ly, lz: v(min(4, abs(lx - 2.0 * u * math.sin(ly * 0.18 / u)) /
                                                  (3.8 * u + 0.1) * 5.2 + (r_r(x, y, z) - 0.5)), x, y, z))
    S.plus(riss_f, "rr")
    S.rendern((-abst * 1.6 - 8, -1, -10), (abst * 1.6 + 8, H + 4, 10))
    # Boden: aufgerissen, mit Splittern
    gelaende(w, _r(34 * u), art=boden_art, dichte=0.5)
    r_n = Rauschen(w, 3)
    for x, z in scheibe(28 * u):
        hh = (r_n(x, 0, z) - 0.6) * 10 * u
        for y in range(1, int(hh) + 1):
            w.setze(x, y, z, Bo(x, y, z, y / 6), ueberschreiben=False)
    # schwebende Bruchstücke mit Chorus / Pilzen
    schwebende_splitter(w, Bo, 0, H * 0.55, 0, 26 * u, int(14 * u), groesse=2.4 * u, h=H * 0.35)
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 8 and w.frei(x, y + 1, z) and rng.random() < 0.035:
            n = w.P.name(b)
            if st == 0 and "end_stone" in n:
                for k in range(1, int(2 + rng.random() * 4)):
                    w.setze(x, y + k, z, w.b("chorus_plant", up=True, down=True, north=False, south=False,
                                             east=False, west=False))
                w.setze(x, y + k + 1, z, w.b("chorus_flower", age=5))
            elif rng.random() < 0.4:
                w.setze(x, y + 1, z, w.b(licht, facing="up") if licht == "end_rod" else w.b(licht))
    hohl(w, 2)
    return w


TEIL3 = {
    "zwergentor": ("Zwergentor", zwergentor),
    "mondtempel": ("Mond- und Sonnentempel", mondtempel),
    "sternwarte": ("Große Sternwarte", sternwarte),
    "kristallkuppel": ("Kristallkuppel", kristallkuppel),
    "leerenriss": ("Leerenriss", leerenriss),
}

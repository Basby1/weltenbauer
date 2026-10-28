"""Weltwunder – gigantische Prunkstücke als Ankerpunkte für ganze Regionen.

Jedes Wunder gibt es riesig und gigantisch, jeweils in zwei Ausprägungen (Stil 1 / Stil 2).
Alle Flächen haben fleckige Mehrblock-Texturen mit Höhenverlauf, die Innenräume massiver Körper
werden ausgehöhlt (spart Platz, sieht von außen gleich aus).
"""

from __future__ import annotations

import math

import numpy as np

from lib import LUFT, Rauschen, Verlauf, Welt, laub
from pracht import Mat, treppe, gelaende
from skulptur import (Skulptur, dreh_x, dreh_y, dreh_z, ell, kap, kasten, kegel, kreisrand, ohne, scheibe,
                      spiegel_x, torus, und, verbinde, zur_mitte)
from motive import figur

U = {0: 0.6, 1: 0.8, 2: 1.0, 3: 1.6}
GROESSEN = [(2, "riesig", "riesig"), (3, "gigantisch", "gigantisch")]


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


# ============================================================================ Hilfen

NICHT_VOLL = ("stairs", "slab", "wall", "fence", "pane", "glass", "leaves", "lantern", "chain", "bars", "rod",
              "carpet", "torch", "door", "trapdoor", "button", "candle", "vine", "water", "lava", "fire", "snow",
              "sapling", "flower", "grass", "fern", "bud", "cluster", "campfire", "pickle", "coral", "roots",
              "dripstone", "button", "banner", "head", "skull", "ice", "kelp", "seagrass", "lichen")


def hohl(w, dicke=2):
    """Entfernt alle Blöcke, die tiefer als `dicke` im Inneren massiver Körper liegen."""
    if not w.bloecke:
        return
    pal = w.P.eintraege
    voll = np.array([not any(t in n for t in NICHT_VOLL) and n != "minecraft:air" for n, _ in pal])
    pos = np.array(list(w.bloecke.keys()))
    ids = np.array(list(w.bloecke.values()))
    lo = pos.min(0) - 1
    hi = pos.max(0) + 1
    G = np.zeros(tuple(hi - lo + 1), dtype=bool)
    m = voll[ids]
    q = pos[m] - lo
    G[q[:, 0], q[:, 1], q[:, 2]] = True
    E = G.copy()
    for _ in range(dicke):
        N = E.copy()
        N[1:, :, :] &= E[:-1, :, :]
        N[:-1, :, :] &= E[1:, :, :]
        N[:, 1:, :] &= E[:, :-1, :]
        N[:, :-1, :] &= E[:, 1:, :]
        N[:, :, 1:] &= E[:, :, :-1]
        N[:, :, :-1] &= E[:, :, 1:]
        N[0, :, :] = N[-1, :, :] = False
        N[:, 0, :] = N[:, -1, :] = False
        N[:, :, 0] = N[:, :, -1] = False
        E = N
    for x, y, z in np.argwhere(E):
        p = (int(x + lo[0]), int(y + lo[1]), int(z + lo[2]))
        if p[1] > 0:
            w.bloecke.pop(p, None)


def sk(M, y0=0, y1=60):
    """Mat als Skulptur-Material (Höhenverlauf zwischen y0 und y1)."""
    return lambda x, y, z, lx, ly, lz: M(x, y, z, min(1.0, max(0.0, (y - y0) / max(1, y1 - y0))))


def bl(w, name):
    return lambda x, y, z, lx, ly, lz, _b=w.b(name): _b


def mix(w, namen, zelle=1.6):
    r = Rauschen(w, zelle)
    ids = [w.b(n) for n in namen]
    return lambda x, y, z, *a: ids[min(len(ids) - 1, int(r(x, y, z) * len(ids) * 1.0))]


def ring_glas(w, farben, cx, cy, R):
    """Glasverlauf von innen (farben[0]) nach außen."""
    v = Verlauf(w, f"G{id(farben)}", farben)
    return lambda x, y, z, lx, ly, lz: v(min(1, math.hypot(lx - cx, ly - cy) / R) * (len(farben) - 1), x, y, z)


def platz(w, R, M, rand="stone_brick", muster=None, akzent="chiseled_stone_bricks", lichter="lantern",
          pfosten="stone_brick_wall", stufen=2, strahlen=8):
    """Runder Prachtplatz: Mosaikringe, Sternstrahlen, Stufenkante und Lichtsäulen. Gibt Höhe der Fläche zurück."""
    rng = w.rng
    muster = muster or ["polished_andesite", "stone_bricks", "polished_diorite"]
    mids = [w.b(m) for m in muster]
    for k in range(stufen):
        r = R + stufen - k
        for x, z in kreisrand(r):
            w.setze(x, k, z, treppe(w, rand, zur_mitte(x, z)))
        for x, z in scheibe(r - 1):
            if w.frei(x, k, z):
                w.setze(x, k, z, M(x, k, z, 0.1))
    y = stufen
    for x, z in scheibe(R):
        d = math.hypot(x, z)
        a = math.atan2(z, x)
        ring = int(d) % 6
        strahl = abs(math.sin(a * strahlen / 2)) < 0.12 + 0.6 / max(d, 1)
        if d > R - 1.2:
            b = w.b(akzent)
        elif ring == 0:
            b = mids[0]
        elif strahl and d > 3:
            b = mids[2] if int(d) % 2 else mids[1]
        else:
            b = M(x, y - 1, z, 0.35)
        w.setze(x, y - 1, z, b)
    for i in range(strahlen * 2):
        a = i / (strahlen * 2) * 2 * math.pi + 0.2
        x, z = round(math.cos(a) * (R - 2.5)), round(math.sin(a) * (R - 2.5))
        for k in range(3):
            w.setze(x, y + k, z, w.b(pfosten, up=True, north="none", south="none", east="none", west="none",
                                     waterlogged=False) if k < 2 else w.b(akzent))
        w.setze(x, y + 3, z, w.b(lichter, hanging=False, waterlogged=False) if lichter.endswith("lantern")
                else w.b(lichter))
    return y


def schwebende_splitter(w, M, cx, cy, cz, R, n, groesse=2.0, h=6.0):
    """Schwebende Felsbrocken um einen Punkt."""
    rng = w.rng
    r = Rauschen(w, 1.4)
    for i in range(n):
        a = rng.random() * 2 * math.pi
        d = R * (0.8 + 0.4 * rng.random())
        x0, z0 = cx + math.cos(a) * d, cz + math.sin(a) * d
        y0 = cy + (rng.random() - 0.5) * h * 2
        s = groesse * (0.6 + rng.random() * 0.8)
        for x in range(int(x0 - s - 2), int(x0 + s + 3)):
            for y in range(int(y0 - s * 1.6 - 2), int(y0 + s + 2)):
                for z in range(int(z0 - s - 2), int(z0 + s + 3)):
                    dy = (y - y0) / (1.0 if y > y0 else 1.8)
                    dd = math.sqrt((x - x0) ** 2 + dy ** 2 + (z - z0) ** 2) + (r(x, y, z) - 0.5) * 1.4
                    if dd < s:
                        w.setze(x, y, z, M(x, y, z, 0.3 + 0.5 * (y > y0)))


def kohlenbecken(w, x, y, z, mat="polished_blackstone", feuer="campfire"):
    w.setze(x, y, z, w.b(f"{mat}_wall" if not mat.endswith("bricks") else f"{mat[:-1]}_wall", up=True, north="none",
                         south="none", east="none", west="none", waterlogged=False))
    w.setze(x, y + 1, z, w.b("cauldron") if feuer is None else w.b(feuer, lit=True, signal_fire=False,
                                                                   facing="north", waterlogged=False))


# ============================================================================ 1 Sternentor


def sternentor(seed, g=2):
    """Dimensionsportal: gigantischer Steinring mit Runenkranz, schimmernder Portalfläche, Obsidiansäulen,
    schwebenden Splittern und Prachtplatz. Stil 1 Netherportal, Stil 2 Sternentor aus Quarz und Gold."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    R = 20 * u
    if st == 0:
        M = Mat(w, ["obsidian", "crying_obsidian", "obsidian", "blackstone", "polished_blackstone_bricks",
                    "gilded_blackstone"], kontrast=1.3)
        boden = Mat(w, "schwarzstein")
        glas = ["magenta_stained_glass", "purple_stained_glass", "purple_stained_glass", "black_stained_glass"]
        rune, licht, rand = "crying_obsidian", "soul_lantern", "polished_blackstone_brick"
        muster = ["polished_blackstone", "blackstone", "gilded_blackstone"]
        akz = "chiseled_polished_blackstone"
    else:
        M = Mat(w, ["smooth_quartz", "quartz_bricks", "calcite", "quartz_block", "chiseled_quartz_block",
                    "gold_block"], kontrast=0.9)
        boden = Mat(w, "marmor")
        glas = ["white_stained_glass", "light_blue_stained_glass", "cyan_stained_glass", "blue_stained_glass"]
        rune, licht, rand = "sea_lantern", "lantern", "quartz"
        muster = ["polished_diorite", "quartz_bricks", "gold_block"]
        akz = "chiseled_quartz_block"
    Rp = _r(R * 1.35, 16)
    y0 = platz(w, Rp, boden, rand=rand, muster=muster, akzent=akz, lichter=licht,
               pfosten="polished_blackstone_wall" if st == 0 else "diorite_wall")
    cy = y0 + R + 5 * u
    S = Skulptur(w, 1.0)
    S.mat("m", sk(M, y0, cy + R))
    S.mat("rune", bl(w, rune))
    S.mat("glas", ring_glas(w, glas, 0, cy, R))
    dick = 3.2 * u
    S.plus(torus(0, cy, 0, R, dick, achse="z"), "m")
    # gestufter Ringrand (Profil)
    S.plus(torus(0, cy, 0, R + dick * 0.9, dick * 0.45, achse="z"), "m")
    S.plus(torus(0, cy, 0, R - dick * 0.9, dick * 0.4, achse="z"), "m")
    # Runensteine im Kranz
    for i in range(16):
        a = i / 16 * 2 * math.pi
        S.plus(ell(math.cos(a) * (R + dick * 0.6), cy + math.sin(a) * (R + dick * 0.6), 0, 1.2 * u, 1.2 * u,
                   dick * 1.15), "rune")
    # Portalfläche
    S.plus(lambda X, Y, Z: (np.hypot(X, Y - cy) < R - dick * 0.6) & (np.abs(Z) < 0.75), "glas")
    # Sockelfüße
    for s in (-1, 1):
        S.plus(kap((s * R * 0.62, y0, 0), (s * R * 0.5, cy - R * 0.72, 0), 3.4 * u, 2.4 * u, zf=1.3), "m")
    S.plus(kasten(-R * 0.75, y0, -dick * 1.6, R * 0.75, y0 + 3 * u, dick * 1.6), "m")
    lo = (-R - 2 * dick - 3, y0 - 1, -dick * 2 - 2)
    hi = (R + 2 * dick + 3, cy + R + 2 * dick + 2, dick * 2 + 2)
    S.rendern(lo, hi)
    # Treppen zur Portalöffnung
    for k in range(int(3 * u) + 1):
        for x in range(-int(R * 0.4), int(R * 0.4) + 1):
            for zs in (1, -1):
                z = zs * (int(dick * 1.6) + 1 + k)
                w.setze(x, y0 + int(3 * u) - k, z, treppe(w, rand, "north" if zs > 0 else "south"))
    # Obsidian-Wächtersäulen mit Feuern
    saeule = Mat(w, ["obsidian", "crying_obsidian", "obsidian"] if st == 0 else ["quartz_pillar", "smooth_quartz"],
                 kontrast=0.6)
    for i in range(6):
        a = (i + 0.5) / 6 * 2 * math.pi
        sx, sz = round(math.cos(a) * Rp * 0.72), round(math.sin(a) * Rp * 0.72)
        Hs = _r((10 + 4 * (i % 2)) * u, 6)
        for y in range(y0, y0 + Hs):
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if abs(dx) + abs(dz) < 2 or y < y0 + 2 or y > y0 + Hs - 3:
                        w.setze(sx + dx, y, sz + dz, saeule(sx + dx, y, sz + dz, (y - y0) / Hs))
        w.setze(sx, y0 + Hs, sz, w.b("soul_campfire" if st == 0 else "campfire", lit=True, signal_fire=False,
                                     facing="north", waterlogged=False))
        for dx, dz, f in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
            w.setze(sx + dx * 2, y0 + Hs - 1, sz + dz * 2, treppe(w, rand, f, "top"))
    # schwebende Splitter
    schwebende_splitter(w, M, 0, cy + R * 0.6, 0, R * 1.35, int(10 * u), groesse=1.6 * u, h=R * 0.5)
    hohl(w)
    return w


# ============================================================================ 2 Wächterkoloss


def waechterkoloss(seed, g=2):
    """Riesiger Wächter in voller Rüstung, auf sein Schwert gestützt, mit wehendem Umhang, auf einem
    reliefgeschmückten Stufensockel. Stil 1 dunkler Stein mit Gold, Stil 2 grünlich verwitterte Bronze."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    if st == 0:
        K = Mat(w, ["deepslate_tiles", "polished_deepslate", "deepslate_bricks", "polished_basalt" if False else
                    "polished_deepslate", "cobbled_deepslate"], kontrast=0.8)
        akz, dunkel, licht = "gold_block", "polished_blackstone", "sea_lantern"
        umh = Mat(w, ["red_nether_bricks", "nether_wart_block", "red_terracotta", "red_concrete"], kontrast=0.7)
        sockel = Mat(w, "graustein")
        rand = "stone_brick"
    else:
        K = Mat(w, ["waxed_oxidized_copper", "waxed_oxidized_cut_copper", "waxed_weathered_copper",
                    "waxed_weathered_cut_copper", "waxed_exposed_copper"], kontrast=1.2)
        akz, dunkel, licht = "waxed_cut_copper", "waxed_weathered_cut_copper", "shroomlight"
        umh = Mat(w, ["blue_terracotta", "blue_concrete", "lapis_block", "blue_wool"], kontrast=0.6)
        sockel = Mat(w, "marmor")
        rand = "quartz"
    s = 3.2 * u           # Skulptur-Maßstab
    hs = _r(10 * u, 6)
    Rp = _r(13 * u, 10)
    # Stufensockel (quadratisch) mit Relief
    for k in range(3):
        r = Rp + 3 - k
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                if max(abs(x), abs(z)) == r:
                    if abs(x) == r and abs(z) == r:
                        w.setze(x, k, z, sockel(x, k, z, 0.1))
                    else:
                        f = "east" if x == -r else "west" if x == r else "south" if z == -r else "north"
                        w.setze(x, k, z, treppe(w, rand, f))
                else:
                    w.setze(x, k, z, sockel(x, k, z, 0.1))
    hb = int(Rp * 0.7)
    for y in range(3, 3 + hs):
        for x in range(-hb, hb + 1):
            for z in range(-hb, hb + 1):
                rnd = max(abs(x), abs(z)) == hb
                if not rnd:
                    w.setze(x, y, z, sockel(x, y, z, 0.5))
                    continue
                t = (y - 3) / hs
                feld = 2 < (y - 3) < hs - 2 and (abs(x) < hb - 1 and abs(z) < hb - 1 or False)
                eck = abs(x) == hb and abs(z) == hb
                if eck:
                    w.setze(x, y, z, w.b("quartz_pillar" if st else "polished_basalt", axis="y"))
                elif 2 <= (y - 3) < hs - 2 and ((x + z) % 4 == 0):
                    w.setze(x, y, z, w.b(akz))
                else:
                    w.setze(x, y, z, sockel(x, y, z, 0.3 + 0.5 * t))
    top = 3 + hs
    for x in range(-hb - 1, hb + 2):
        for z in range(-hb - 1, hb + 2):
            if max(abs(x), abs(z)) == hb + 1 and not (abs(x) == hb + 1 and abs(z) == hb + 1):
                f = "east" if x < -hb else "west" if x > hb else "south" if z < -hb else "north"
                w.setze(x, top - 1, z, treppe(w, rand, f, "top"))
    for x in range(-hb, hb + 1):
        for z in range(-hb, hb + 1):
            w.setze(x, top, z, w.b(akz) if (x + z) % 2 == 0 and max(abs(x), abs(z)) == hb else sockel(x, top, z, 0.9))
    # Inschrift-Laternen
    for a in (-1, 1):
        for b in (-1, 1):
            w.setze(a * (hb + 2), 3, b * (hb + 2), w.b(licht))
    # Figur
    S = Skulptur(w, s)
    S.mat("k", sk(K, top, top + 22 * s))
    S.mat("a", bl(w, akz))
    S.mat("d", bl(w, dunkel))
    S.mat("g", bl(w, licht))
    S.mat("u", sk(umh, top, top + 22 * s))
    S.mat("b", sk(Mat(w, ["polished_andesite", "iron_block", "polished_diorite", "smooth_stone", "iron_block"],
                      kontrast=0.6), top, top + 12 * s))
    # Beine mit Stiefeln und Kniekacheln
    S.plus(spiegel_x(kap((1.4, 0.6, 0), (1.15, 7.0, 0), 1.15, 1.45)), "k")
    S.plus(spiegel_x(ell(1.4, 0.9, 0.5, 1.35, 1.0, 1.8)), "d")
    S.plus(spiegel_x(ell(1.25, 3.9, 0.7, 1.05, 1.0, 1.0)), "a")
    # Waffenrock und Gürtel
    S.plus(kegel(0, 0, 5.6, 8.6, 3.1, 2.6, zf=0.78), "u")
    S.plus(kegel(0, 0, 8.3, 9.0, 2.75, 2.75, zf=0.8), "a")
    # Rumpf mit Brustgrat und Wappen
    S.plus(kap((0, 8.6, 0), (0, 12.9, 0), 2.4, 3.15, zf=0.72), "k")
    S.plus(ell(0, 11.2, 1.95, 0.45, 2.1, 0.55), "a")
    S.plus(ell(0, 10.6, 1.75, 1.3, 1.5, 0.45), "g")
    # Schulterplatten
    S.plus(spiegel_x(ell(3.25, 12.8, 0, 1.75, 1.25, 1.75)), "k")
    S.plus(spiegel_x(ell(3.35, 13.25, 0, 1.45, 0.55, 1.5)), "a")
    # Arme zum Schwertknauf
    S.plus(spiegel_x(kap((3.2, 12.3, 0.1), (2.7, 9.6, 1.7), 1.05, 0.95)), "k")
    S.plus(spiegel_x(kap((2.7, 9.6, 1.7), (0.95, 10.1, 3.1), 0.95, 0.9)), "k")
    S.plus(spiegel_x(ell(0.75, 10.2, 3.15, 0.95, 0.95, 0.95)), "d")
    # Schwert: Klinge in den Sockel gerammt
    S.plus(lambda X, Y, Z: (np.abs(X) < 0.5 - Y * 0.0) & (Y > -0.5) & (Y < 9.2) & (np.abs(Z - 3.1) < 0.32), "b")
    S.plus(lambda X, Y, Z: (np.abs(X) < 0.16) & (Y > 0.5) & (Y < 8.8) & (np.abs(Z - 3.1) < 0.4), "d")
    S.plus(lambda X, Y, Z: (np.abs(X) < 2.7 - np.abs(Y - 9.35) * 2) & (np.abs(Y - 9.35) < 0.38)
           & (np.abs(Z - 3.1) < 0.48), "a")
    S.plus(lambda X, Y, Z: (np.abs(X) < 0.32) & (Y > 9.6) & (Y < 11.0) & (np.abs(Z - 3.1) < 0.32), "d")
    S.plus(ell(0, 11.3, 3.1, 0.6, 0.6, 0.6), "a")
    # Hals und Topfhelm mit Sehschlitz und Helmbusch
    S.plus(kap((0, 12.8, 0), (0, 14.0, 0), 1.05), "d")
    S.plus(ell(0, 15.3, 0.1, 1.65, 1.95, 1.75), "k")
    S.plus(lambda X, Y, Z: (np.abs(Y - 15.3) < 0.28) & (np.abs(X) < 1.15) & (Z > 1.0) & (Z < 1.95), "d")
    S.plus(lambda X, Y, Z: (np.abs(X) < 0.22) & (Y > 13.6) & (Y < 17.2) & (Z > 1.2) & (Z < 1.95), "a")
    S.plus(kap((0, 16.9, 0.6), (0, 17.9, -1.0), 0.55, 0.45), "u")
    S.plus(kap((0, 17.9, -1.0), (0, 16.4, -3.2), 0.45, 0.25), "u")
    # Umhang
    S.plus(lambda X, Y, Z: (Y > 1.2) & (Y < 13.4) & (Z < -1.4) & (Z > -2.3 - (13.4 - Y) * 0.1)
           & (np.abs(X) < 2.9 + (13.4 - Y) * 0.13), "u")
    kopf = 18.5
    S.rendern((-9, -1, -7), (9, kopf + 1, 7), versatz=(0, top + 0.01, 0))
    hohl(w)
    return w


# ============================================================================ 3 Weltenbaum


def weltenbaum(seed, g=2):
    """Weltenbaum: gewaltiger Stamm aus verdrehten Strängen, riesige Brettwurzeln, weit ausgreifende Äste
    mit Laubwolken, Leuchtfrüchten, Ranken und einer Wendelstiege mit Plattformen. Stil 1 Lebensbaum,
    Stil 2 silberner Mondbaum mit Blütenkrone."""
    import baeume as B
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    rng = w.rng
    art = "dark_oak" if st == 0 else "birch"
    pinsel = B.Pinsel(w, B.Holzart(w, art))
    if st == 0:
        blaetter = [(laub(w, "oak"), 0.45), (laub(w, "azalea"), 0.25), (laub(w, "flowering_azalea"), 0.12),
                    (laub(w, "jungle"), 0.18)]
        frucht = w.b("shroomlight")
    else:
        blaetter = [(laub(w, "cherry"), 0.55), (laub(w, "birch"), 0.25), (laub(w, "flowering_azalea"), 0.2)]
        frucht = w.b("pearlescent_froglight", axis="y")
    H = 34 * u
    r0 = 5.5 * u
    gelaende(w, _r(26 * u), art="wald", dichte=0.7)
    # Stamm aus mehreren verdrillten Strängen
    straenge = 5
    enden = []
    for i in range(straenge):
        a0 = i / straenge * 2 * math.pi
        pts = []
        for k in range(int(H) + 1):
            t = k / H
            a = a0 + t * 1.4
            rr = r0 * (0.7 - 0.4 * t)
            pts.append((math.cos(a) * rr + 0.5, k, math.sin(a) * rr + 0.5))
        pinsel.neu()
        for k, p in enumerate(pts):
            t = k / H
            pinsel.punkt(np.array(p, float), r0 * (0.62 - 0.32 * t) + (1.2 * u * max(0, 1 - k / 6)), np.array([0, 1, 0.0]))
        enden.append(np.array(pts[-1], float))
    # Brettwurzeln
    for i in range(11):
        a = i / 11 * 2 * math.pi + rng.random() * 0.3
        d = np.array([math.cos(a), -0.28, math.sin(a)])
        start = np.array([math.cos(a) * r0 * 0.7 + 0.5, 6.0 * u, math.sin(a) * r0 * 0.7 + 0.5])
        B.ast(w, pinsel, start, d, (14 + 8 * rng.random()) * u, 2.6 * u, 0.6, biegung=0.08, schwerkraft=0.04)
    # Krone: Hauptäste
    cfg = B.Wuchs(kinder=3, spreizung=(25, 50), laenge=0.6, biegung=0.1, auftrieb=0.04)
    blatt_enden, mitte = [], []
    for i in range(7):
        a = i / 7 * 360 + rng.random() * 30
        d = B.richtung_aus_winkeln(a, 55 + rng.random() * 15)
        s = enden[i % straenge] if i < straenge else enden[0]
        B.verzweigen(w, pinsel, np.array([0.5, H * (0.72 + 0.12 * (i % 3) / 2), 0.5]), d, 24 * u, 2.6 * u, 2,
                     cfg, blatt_enden, mitte)
    holz = pinsel.holz.alle
    for p, t in blatt_enden:
        rw = (5.5 + rng.random() * 2.5) * u
        B.blattwolke(w, p + [0, 1.0, 0], rw, rw * 0.7, blaetter, schutz=holz, luecken=0.08)
    for p in mitte[::2]:
        B.blattwolke(w, p + [0, 0.8, 0], 3.5 * u, 2.2 * u, blaetter, schutz=holz, luecken=0.1)
    # Leuchtfrüchte und hängende Ranken unter dem Laub
    unten = [(x, y, z) for (x, y, z), b in list(w.bloecke.items()) if y > H * 0.6 and w.frei(x, y - 1, z)
             and w.P.name(b).endswith("leaves")]
    for (x, y, z) in unten:
        r = rng.random()
        if r < 0.025:
            w.setze(x, y - 1, z, frucht)
        elif r < 0.12:
            for k in range(1, int(2 + rng.random() * 6 * u)):
                if not w.frei(x, y - k, z):
                    break
                w.setze(x, y - k, z, w.b("weeping_vines_plant" if st == 0 else "cave_vines_plant", berries=True)
                        if st == 1 else w.b("vine", north=True, east=False, south=False, west=False, up=False))
    hohl(w, 3)
    return w


# ============================================================================ 4 Arkane Spirale


def arkanspirale(seed, g=2):
    """Arkane Spirale: ein in sich verdrehter Magierturm aus gestapelten Achteck-Scheiben, umkreist von
    schwebenden Runenringen, gekrönt von einem riesigen Kristall. Stil 1 Amethyst, Stil 2 Azur."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    if st == 0:
        M = Mat(w, ["purpur_block", "purpur_pillar", "purpur_block", "amethyst_block", "end_stone_bricks"],
                kontrast=0.9)
        boden = Mat(w, ["purpur_block", "end_stone_bricks", "polished_blackstone_bricks", "obsidian"])
        kristall = ["amethyst_block", "purple_stained_glass", "magenta_stained_glass", "pink_stained_glass"]
        ringmat, licht, rand = "crying_obsidian", "end_rod", "purpur"
        fenster = "magenta_stained_glass"
        muster = ["purpur_block", "end_stone_bricks", "amethyst_block"]
    else:
        M = Mat(w, ["dark_prismarine", "prismarine_bricks", "prismarine", "warped_planks", "quartz_bricks"],
                kontrast=0.9)
        boden = Mat(w, ["prismarine_bricks", "quartz_bricks", "dark_prismarine"])
        kristall = ["sea_lantern", "light_blue_stained_glass", "cyan_stained_glass", "blue_stained_glass"]
        ringmat, licht, rand = "gold_block", "sea_lantern", "prismarine_brick"
        fenster = "cyan_stained_glass"
        muster = ["dark_prismarine", "prismarine_bricks", "sea_lantern"]
    Rp = _r(16 * u, 12)
    y0 = platz(w, Rp, boden, rand=rand, muster=muster, akzent=muster[2], lichter="soul_lantern" if st == 0
               else "lantern", pfosten="end_stone_brick_wall" if st == 0 else "prismarine_wall")
    H = _r(58 * u)
    Rb = 8.5 * u
    r_n = Rauschen(w, 3)
    fen = w.b(fenster)
    for y in range(y0, y0 + H):
        t = (y - y0) / H
        R = Rb * (1 - 0.62 * t) + 1.5 * math.sin(t * math.pi * 6) * u * 0.25
        a = t * math.pi * 2.2
        ca, sa = math.cos(a), math.sin(a)
        n = int(R) + 2
        for x in range(-n, n + 1):
            for z in range(-n, n + 1):
                lx, lz = x * ca + z * sa, -x * sa + z * ca
                d = max(abs(lx), abs(lz), (abs(lx) + abs(lz)) / 1.36)
                if d <= R:
                    rand_ = d > R - 1.0
                    if not rand_:
                        if (y - y0) % 7 == 0:
                            w.setze(x, y, z, M(x, y, z, t))
                        continue
                    fenster_hier = (y - y0) % 7 in (3, 4) and abs(lz) < 0.9 and t < 0.9
                    w.setze(x, y, z, fen if fenster_hier else M(x, y, z, t))
        # Gesimsband alle 7 Ebenen
        if (y - y0) % 7 == 0 and y > y0:
            for x in range(-n - 1, n + 2):
                for z in range(-n - 1, n + 2):
                    lx, lz = x * ca + z * sa, -x * sa + z * ca
                    d = max(abs(lx), abs(lz), (abs(lx) + abs(lz)) / 1.36)
                    if R < d <= R + 1.0:
                        w.setze(x, y, z, w.b(f"{rand}_slab", type="top", waterlogged=False))
    yt = y0 + H
    # Kristallkrone
    S = Skulptur(w, 1.0)
    v = Verlauf(w, "Kr", kristall)
    S.mat("kr", lambda x, y, z, lx, ly, lz: v((1 - min(1, abs(ly - (yt + 6 * u)) / (9 * u))) * 3, x, y, z))
    S.plus(kap((0, yt - 2, 0), (0, yt + 18 * u, 0), 3.4 * u, 0.3), "kr")
    for i in range(5):
        a = i / 5 * 2 * math.pi
        S.plus(kap((0, yt, 0), (math.cos(a) * 5 * u, yt + 9 * u, math.sin(a) * 5 * u), 1.6 * u, 0.2), "kr")
    S.rendern((-8 * u, yt - 3, -8 * u), (8 * u, yt + 20 * u, 8 * u))
    # Schwebende Runenringe
    for i, (hr, rr, nei) in enumerate(((0.3, 13, 0.25), (0.55, 10, -0.3), (0.8, 7.5, 0.35))):
        Sr = Skulptur(w, 1.0)
        Sr.mat("r", bl(w, ringmat))
        Sr.mat("l", bl(w, licht if licht != "end_rod" else "pearlescent_froglight"))
        cy = y0 + H * hr
        Sr.plus(torus(0, 0, 0, rr * u, 0.65 * u + 0.15, achse="y"), "r")
        for k in range(8):
            a = k / 8 * 2 * math.pi
            Sr.plus(ell(math.cos(a) * rr * u, 0, math.sin(a) * rr * u, 1.0, 1.0, 1.0), "l")
        Sr.rendern((-rr * u - 2, -2, -rr * u - 2), (rr * u + 2, 2, rr * u + 2), versatz=(0, cy, 0),
                   dreh=dreh_x(nei) @ dreh_z(nei * 0.6))
    # Eingang
    for y in range(y0, y0 + 4):
        for x in (-1, 0, 1):
            for z in range(int(Rb) - 1, int(Rb) + 2):
                w.bloecke.pop((x, y, z), None)
    for x in (-2, 2):
        for y in range(y0, y0 + 5):
            w.setze(x, y, int(Rb) + 1, w.b(ringmat))
    hohl(w)
    return w


# ============================================================================ 5 Schwebende Zitadelle


def schwebende_zitadelle(seed, g=2):
    """Schwebende Zitadelle: umgedrehter Felsberg mit Wurzeln, Tropfsteinen und Wasserfällen, darauf eine
    Burg mit Türmen; Ketten halten sie an Ankersteinen am Boden. Stil 1 graue Burg, Stil 2 weiße Elfenfeste."""
    import pracht as P
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    rng = w.rng
    R = 22 * u
    hoch = _r(26 * u)          # Unterkante über dem Boden
    tief = 30 * u              # Tiefe des Felskegels
    yo = hoch + int(tief)      # Oberfläche der Insel
    fels = Mat(w, ["stone", "andesite", "tuff", "cobblestone", "deepslate", "dripstone_block"], kontrast=1.3)
    r_n = Rauschen(w, 6)
    r_f = Rauschen(w, 2)
    for x in range(-int(R) - 4, int(R) + 5):
        for z in range(-int(R) - 4, int(R) + 5):
            d = math.hypot(x, z)
            Rr = R * (0.82 + 0.35 * r_n(x, 0, z))
            if d > Rr:
                continue
            t = d / Rr
            unter = yo - tief * (1 - t ** 1.6) * (0.8 + 0.4 * r_f(x, 0, z))
            for y in range(int(unter), yo + 1):
                tt = (y - unter) / max(1, yo - unter)
                if y == yo:
                    w.setze(x, y, z, w.b("grass_block", snowy=False))
                elif y >= yo - 2:
                    w.setze(x, y, z, w.b("dirt") if rng.random() < 0.8 else w.b("rooted_dirt"))
                else:
                    w.setze(x, y, z, fels(x, y, z, 0.2 + 0.8 * tt))
            # Tropfsteine und Wurzeln unten
            if rng.random() < 0.05:
                for k in range(1, int(2 + rng.random() * 5)):
                    w.setze(x, int(unter) - k, z, w.b("pointed_dripstone", vertical_direction="down",
                                                        thickness="tip" if k > 3 else "frustum", waterlogged=False))
            elif rng.random() < 0.04:
                for k in range(1, int(2 + rng.random() * 7)):
                    w.setze(x, int(unter) - k, z, w.b("hanging_roots", waterlogged=False))
    # Wasserfälle über die Kante
    for i in range(3):
        a = rng.random() * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.9), round(math.sin(a) * R * 0.9)
        w.setze(x, yo, z, w.b("water", level=0))
    gelaende(w, R * 0.8, cx=0, cz=0, art="wiese", dichte=0.6) if False else None
    # Burg obenauf
    stil = P.Stil(w, wand="graustein" if st == 0 else "marmor", sockel="graustein" if st == 0 else "kalkstein",
                  gesims="stone_brick" if st == 0 else "quartz", dach="schiefer" if st == 0 else "blau",
                  holz="spruce" if st == 0 else "birch", laeden=False)
    hb = _r(8 * u)
    P.gebaeude(w, stil, -hb, -hb // 2, hb, hb // 2, y0=yo + 1, etagen=3, eh=5, dach="walm", tuer="south")
    for (tx, tz) in ((-hb - 4, -hb), (hb + 4, -hb), (-hb - 4, hb), (hb + 4, hb)):
        P.turm(w, stil, tx, tz, yo + 1, _r(24 * u), 3.0 * u, dach="nadel" if st else "kegel",
               fahne=["red_wool", "yellow_wool"] if st == 0 else ["white_wool", "light_blue_wool"])
    P.turm(w, stil, 0, 0, yo + 16, _r(26 * u), 3.6 * u, dach="nadel", fahne=None)
    # Grasdeko
    for (x, y, z), b in list(w.bloecke.items()):
        if y == yo and w.frei(x, y + 1, z) and w.P.name(b) == "minecraft:grass_block":
            r = rng.random()
            if r < 0.25:
                w.setze(x, y + 1, z, w.b("grass"))
            elif r < 0.29:
                w.setze(x, y + 1, z, w.b(["poppy", "dandelion", "azure_bluet", "cornflower"][int(rng.integers(4))]))
            elif r < 0.30:
                w.setze(x, y + 1, z, laub(w, "azalea"))
    # Ketten zu Ankersteinen
    for i in range(4):
        a = i / 4 * 2 * math.pi + 0.4
        ax, az = round(math.cos(a) * R * 1.25), round(math.sin(a) * R * 1.25)
        ox, oz = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        oben = max((y for (x, y, z) in w.bloecke if (x, z) == (ox, oz)), default=yo) - 4
        unten_y = min((y for (x, y, z) in w.bloecke if (x, z) == (ox, oz)), default=hoch)
        n = int(max(abs(ax - ox), abs(az - oz), unten_y - 3))
        for k in range(n + 1):
            t = k / n
            x = round(ox + (ax - ox) * t)
            z = round(oz + (az - oz) * t)
            y = round(unten_y + (3 - unten_y) * t)
            w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False), ueberschreiben=False)
        for x in range(ax - 2, ax + 3):
            for z in range(az - 2, az + 3):
                for y in range(0, 3):
                    if abs(x - ax) + abs(z - az) + y <= 3:
                        w.setze(x, y, z, fels(x, y, z, 0.3))
        w.setze(ax, 3, az, w.b("chiseled_stone_bricks"))
    hohl(w, 3)
    return w


WELTWUNDER = {
    "sternentor": ("Sternentor", sternentor),
    "waechterkoloss": ("Wächterkoloss", waechterkoloss),
    "weltenbaum": ("Weltenbaum", weltenbaum),
    "arkanspirale": ("Arkane Spirale", arkanspirale),
    "schwebende_zitadelle": ("Schwebende Zitadelle", schwebende_zitadelle),
}

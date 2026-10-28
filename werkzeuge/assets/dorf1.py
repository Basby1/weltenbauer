"""Dschungeltempel, Wikingerdorf, Mittelaltermarkt – drei Pakete."""

from __future__ import annotations

import math

import numpy as np

from bau import Stil, kamin, kasten_haus, satteldach, walmdach, zaun_rechteck
from lib import Verlauf, Welt, laub, ueberwuchern
from skulptur import Skulptur, ell, kap, kreisrand, platte, scheibe, treppe, verbinde, zur_mitte

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _gras(w, r, cx=0, cz=0, blk="grass_block"):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, w.b(blk, snowy=False) if blk in ("grass_block", "podzol") else w.b(blk), ueberschreiben=False)


def _pfosten(w, mat):
    return w.b(mat, north=False, south=False, east=False, west=False, waterlogged=False)


# ============================================================================ Dschungel

class Urwald:
    def __init__(self, w, seed):
        self.w = w
        self.gold = _stil(seed) == 1
        self.stein = Verlauf(w, "Tempelstein", ["mossy_cobblestone", "mossy_stone_bricks", "cracked_stone_bricks",
                                                "stone_bricks", "chiseled_stone_bricks"]) if not self.gold else \
            Verlauf(w, "Goldtempel", ["mossy_cobblestone", "mossy_stone_bricks", "cut_sandstone", "smooth_sandstone",
                                      "chiseled_sandstone"])
        self.tr = "mossy_stone_brick" if not self.gold else "smooth_sandstone"
        self.akzent = w.b("gold_block") if self.gold else w.b("prismarine_bricks")

    def s(self, x, y, z, v=1.5):
        return self.stein(v + self.w.rng.random() * 1.6, x, y, z)


def dschungelbaum(w, x, z, u, y0=1):
    h = _r(8 * u + 4, 6)
    for y in range(y0, y0 + h):
        for dx, dz in ((0, 0), (1, 0), (0, 1), (1, 1)) if u > 1.2 else ((0, 0),):
            w.setze(x + dx, y, z + dz, w.b("jungle_log", axis="y"))
    S = Skulptur(w, max(0.8, u))
    bl = [laub(w, "jungle"), laub(w, "jungle"), laub(w, "oak")]
    S.mat("l", lambda *a: bl[int(w.rng.integers(3))])
    S.plus(lambda X, Y, Z: (X / 3.5) ** 2 + (Y / 2.0) ** 2 + (Z / 3.5) ** 2 <= 1, "l")
    S.rendern((-5, -3, -5), (5, 3, 5), versatz=(x + 0.5, y0 + h, z + 0.5), ueberschreiben=False)
    for k in range(4):
        a = k * math.pi / 2 + 0.3
        vx, vz = round(x + math.cos(a) * 3 * u), round(z + math.sin(a) * 3 * u)
        for kk in range(1, _r(3 * u + 1, 2)):
            w.setze(vx, y0 + h - 1 - kk, vz, w.b("vine", north=True, east=False, south=False, west=False, up=False),
                    ueberschreiben=False)


def stufenpyramide(seed, g=2):
    """Stufenpyramide im Urwald: steile Stufen, breite Mitteltreppe mit Wangen, Tempelhaus mit Dachkamm,
    Feuerschalen, Ranken und Moos."""
    w = _welt(seed)
    k = Urwald(w, seed)
    u = U[g]
    stufen = [4, 5, 7, 9][g]
    sh = _r(1.6 * u + 0.6, 2)
    R = stufen * 2 + _r(3 * u, 2)
    _gras(w, R + 6)
    for st in range(stufen):
        r = R - st * 2
        for y in range(st * sh, (st + 1) * sh):
            for x in range(-r, r + 1):
                for z in range(-r, r + 1):
                    if max(abs(x), abs(z)) >= r - 2 or y == (st + 1) * sh - 1:
                        w.setze(x, y + 1, z, k.s(x, y, z, 0.5 + 3 * st / stufen))
    top = stufen * sh + 1
    for t in range(top):
        z = R + 1 - t * 2 // sh if False else R - (t * 2) // sh
        for x in range(-2, 3):
            w.setze(x, t, z + 1, treppe(w, k.tr, "north"))
            w.setze(x, t, z, k.s(x, t, z))
        for x in (-3, 3):
            w.setze(x, t + 1, z + 1, k.s(x, t, z))
    rt = R - stufen * 2
    th = _r(3 * u + 2, 3)
    for y in range(top, top + th):
        for x in range(-rt, rt + 1):
            for z in range(-rt, rt + 1):
                if max(abs(x), abs(z)) == rt and not (z == rt and abs(x) <= 1 and y < top + 2):
                    w.setze(x, y, z, k.s(x, y, z, 3))
    for x in range(-rt - 1, rt + 2):
        for z in range(-rt - 1, rt + 2):
            w.setze(x, top + th, z, k.s(x, top + th, z, 3.5))
    for x in range(-rt, rt + 1):
        for y in range(top + th + 1, top + th + _r(3 * u, 2) + 1):
            if (x + y) % 2 == 0:
                w.setze(x, y, 0, k.s(x, y, 0, 3.5))
    w.setze(0, top + th + 1, -1, k.akzent)
    for s in (-1, 1):
        w.setze(s * 4, top - sh + 1, R - stufen * 2 + 3, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                             waterlogged=False), ueberschreiben=False)
    ueberwuchern(w, None, ranken=0.45, moos_oben=0.5, pflanzen=0.25, buesche=0.05, max_ranke=4)
    for i in range(2 + g):
        a = i * 2.3 + 0.5
        dschungelbaum(w, round(math.cos(a) * (R + 3)), round(math.sin(a) * (R + 3)), u * 0.8)
    return w


def dschungelruine(seed, g=1):
    """Überwucherte Ruine: Mauerreste, ein Torbogen, umgestürzte Säulen, Dschungelbäume und Ranken."""
    w = _welt(seed)
    k = Urwald(w, seed)
    u = U[g]
    R = _r(8 * u + 4, 6)
    _gras(w, R + 4, blk="podzol")
    for x in range(-R, R + 1):
        for z in (-R, R):
            h = int((2 + 4 * abs(math.sin(x * 0.4 + z))) * u)
            for y in range(1, h + 1):
                w.setze(x, y, z, k.s(x, y, z))
    for z in range(-R, R + 1):
        h = int((1 + 4 * abs(math.cos(z * 0.5))) * u)
        for y in range(1, h + 1):
            w.setze(-R, y, z, k.s(-R, y, z))
    Hb = _r(5 * u + 2, 4)
    for s in (-1, 1):
        for y in range(1, Hb + 1):
            w.setze(s * 2, y, 0, k.s(s * 2, y, 0))
    for x in range(-2, 3):
        w.setze(x, Hb + 1, 0, k.s(x, Hb + 1, 0, 3))
    w.setze(0, Hb + 1, 1, k.akzent)
    for i in range(1 + g):
        x0, z0 = round((w.rng.random() - 0.5) * R), round((w.rng.random() - 0.5) * R)
        for kk in range(_r(3 * u + 1, 2)):
            w.setze(x0 + kk, 1, z0, k.s(x0 + kk, 1, z0))
    for i in range(1 + g):
        a = i * 2.7
        dschungelbaum(w, round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5), u * 0.8)
    ueberwuchern(w, None, ranken=0.6, moos_oben=0.6, pflanzen=0.5, buesche=0.1, max_ranke=4)
    return w


def baumhausdorf(seed, g=2):
    """Baumhausdorf: Hütten auf Plattformen in Urwaldriesen, verbunden durch Hängebrücken, mit Leitern."""
    w = _welt(seed)
    u = U[g]
    n = [2, 3, 4, 6][g]
    R = 6 * u + 3 + n * 2
    _gras(w, R + 4, blk="podzol")
    plattformen = []
    for i in range(n):
        a = i * 2 * math.pi / n
        x, z = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        yp = _r((5 + 2 * (i % 2)) * u + 3, 4)
        dschungelbaum(w, x, z, u * 0.9 + 0.3)
        rp = 2.2 * u + 1.2
        for xx, zz in scheibe(rp, x, z):
            w.setze(xx, yp, zz, w.b("jungle_planks"))
        verbinde(w, [(xx, yp + 1, zz) for xx, zz in kreisrand(rp, x, z)], "jungle_fence")
        hb = max(1, int(rp * 0.6))
        for y in range(yp + 1, yp + 4):
            for xx in range(x - hb, x + hb + 1):
                for zz in range(z - hb, z + hb + 1):
                    if max(abs(xx - x), abs(zz - z)) == hb and not (zz == z + hb and xx == x):
                        w.setze(xx, y, zz, w.b("bamboo_block", axis="y") if (xx + zz) % 2 else w.b("jungle_planks"))
        for kk in range(hb + 2):
            for xx in range(x - hb - 1 + kk, x + hb + 2 - kk):
                for zz in range(z - hb - 1 + kk, z + hb + 2 - kk):
                    if max(abs(xx - x), abs(zz - z)) == hb + 1 - kk:
                        w.setze(xx, yp + 4 + kk, zz, w.b("hay_block", axis="y"))
        for y in range(1, yp):
            w.setze(x + int(rp) + 1, y, z, w.b("ladder", facing="east", waterlogged=False))
        plattformen.append((x, yp, z))
    for i in range(n):
        (x1, y1, z1), (x2, y2, z2) = plattformen[i], plattformen[(i + 1) % n]
        L = int(math.hypot(x2 - x1, z2 - z1))
        for t in range(L + 1):
            f = t / max(1, L)
            x = round(x1 + (x2 - x1) * f)
            z = round(z1 + (z2 - z1) * f)
            y = round(y1 + (y2 - y1) * f - math.sin(f * math.pi) * 1.5)
            w.setze(x, y, z, w.b("jungle_slab", type="bottom", waterlogged=False), ueberschreiben=False)
    return w


def schlangentor(seed, g=1):
    """Tempeltor mit zwei gewundenen Steinschlangen als Pfeiler und Juwelenaugen."""
    w = _welt(seed)
    k = Urwald(w, seed)
    u = U[g]
    _gras(w, 6 * u + 4, blk="podzol")
    S = Skulptur(w, u)
    S.mat("s", lambda x, y, z, lx, ly, lz: k.s(x, y, z, 1 + ly / 6))
    S.mat("a", w.b("emerald_block") if not k.gold else w.b("redstone_block"))
    S.mat("z", k.akzent)
    for sgn in (-1, 1):
        pts = [(sgn * 3 + 0.8 * math.sin(t * 1.6), t, 0.8 * math.cos(t * 1.6)) for t in np.linspace(0, 9, 14)]
        for a, b in zip(pts, pts[1:]):
            S.plus(kap(a, b, 0.9), "s")
        S.plus(ell(sgn * 2.2, 9.6, 0.4, 1.3, 1.0, 1.4), "s")
        S.plus(kap((sgn * 1.4, 9.4, 0.8), (sgn * 0.4, 9.2, 1.6), 0.6, 0.3), "s")
        S.plus(ell(sgn * 2.2, 10.1, 1.3, 0.3, 0.3, 0.3), "a")
    S.plus(lambda X, Y, Z: (np.abs(X) <= 3.4) & (Y >= 10.5) & (Y <= 11.6) & (np.abs(Z) <= 1), "s")
    S.plus(lambda X, Y, Z: (np.abs(X) <= 0.6) & (Y >= 11.6) & (Y <= 12.4) & (np.abs(Z) <= 0.6), "z")
    S.rendern((-6, 0, -3), (6, 13, 3), versatz=(0.5, 1, 0.5))
    ueberwuchern(w, None, ranken=0.4, moos_oben=0.5, pflanzen=0.3, buesche=0.0, max_ranke=3)
    return w


def wasserfallschrein(seed, g=2):
    """Schrein in einer Felswand hinter einem Wasserfall, mit Becken, Trittsteinen und Leuchtsteinen."""
    w = _welt(seed)
    k = Urwald(w, seed)
    u = U[g]
    W, H = _r(8 * u + 4, 6), _r(10 * u + 5, 7)
    _gras(w, W + 5)
    fels = Verlauf(w, "Fels", ["mossy_cobblestone", "stone", "andesite", "moss_block"])
    for x in range(-W, W + 1):
        top = H * (1 - (abs(x) / W) ** 2)
        for z in range(-_r(6 * u + 2, 4), 1):
            for y in range(0, int(top) + 1):
                w.setze(x, y, z, fels(0.3 + 2.5 * y / H + w.rng.random() * 0.6, x, y, z))
    hb, hh = _r(2 * u + 1, 2), _r(3 * u + 2, 3)
    for x in range(-hb, hb + 1):
        for y in range(1, hh + 1):
            for z in range(-_r(3 * u + 1, 2), 1):
                w.setze(x, y, z, 0)
    for x in range(-hb, hb + 1):
        w.setze(x, hh + 1, 0, k.s(x, hh + 1, 0, 3))
    w.setze(0, 1, -_r(3 * u + 1, 2), k.akzent)
    w.setze(0, 2, -_r(3 * u + 1, 2), w.b("sea_lantern"))
    top = int(H) + 1
    w.setze(0, top, -1, w.b("water", level=0))
    for y in range(hh + 2, top):
        w.vorschau_extra = getattr(w, "vorschau_extra", {})
        w.vorschau_extra[(0, y, 1)] = w.b("water", level=0)
    for x, z in scheibe(hb + 2, 0, hb + 3):
        w.setze(x, 0, z, w.b("water", level=0))
    for kk in range(3):
        w.setze(hb + 1, 0, 2 + kk * 2, w.b("mossy_cobblestone"))
    ueberwuchern(w, None, ranken=0.4, moos_oben=0.4, pflanzen=0.3, buesche=0.05, max_ranke=5)
    return w


def steinkopf(seed, g=2):
    """Gewaltiger Steinkopf mit Helm, breiter Nase, wulstigen Lippen und Moos, halb im Boden."""
    w = _welt(seed)
    k = Urwald(w, seed)
    u = U[g]
    _gras(w, 7 * u + 4)
    S = Skulptur(w, u)
    S.mat("s", lambda x, y, z, lx, ly, lz: k.s(x, y, z, 0.8 + ly / 6))
    S.mat("h", lambda x, y, z, *_: k.akzent if (x + y) % 4 == 0 else k.s(x, y, z, 3.5))
    S.plus(ell(0, 3, 0, 4, 5, 3.8), "s")
    S.plus(lambda X, Y, Z: ((X / 4.4) ** 2 + ((Y - 5.5) / 3.2) ** 2 + (Z / 4.2) ** 2 <= 1) & (Y > 6), "h")
    S.plus(kap((0, 4.5, 3.4), (0, 2.7, 4.3), 0.9, 1.3), "s")
    S.plus(ell(0, 1.3, 3.4, 2.0, 0.7, 0.9), "s")
    S.minus(lambda X, Y, Z: (np.abs(np.abs(X) - 1.6) < 0.7) & (np.abs(Y - 5.2) < 0.4) & (Z > 3))
    S.minus(lambda X, Y, Z: (np.abs(X) < 1.8) & (np.abs(Y - 0.9) < 0.25) & (Z > 3.6))
    S.plus(lambda X, Y, Z: (np.abs(np.abs(X) - 1.6) < 0.5) & (np.abs(Y - 5.2) < 0.3) & (Z > 3.0) & (Z < 3.6), "s")
    from skulptur import dreh_y
    S.rendern((-6, -1, -6), (6, 10, 6), versatz=(0.5, -0.5, 0.5), dreh=dreh_y(0.7))
    w.bloecke = {p: b for p, b in w.bloecke.items() if p[1] >= 0}
    ueberwuchern(w, None, ranken=0.35, moos_oben=0.6, pflanzen=0.3, buesche=0.03, max_ranke=4)
    return w


DSCHUNGEL = {
    "stufenpyramide": ("Stufenpyramide", stufenpyramide),
    "dschungelruine": ("Dschungelruine", dschungelruine),
    "baumhausdorf": ("Baumhausdorf", baumhausdorf),
    "schlangentor": ("Schlangentor", schlangentor),
    "wasserfallschrein": ("Wasserfallschrein", wasserfallschrein),
    "steinkopf": ("Steinkopf", steinkopf),
}


# ============================================================================ Wikinger

def langhaus(seed, g=1):
    """Nordisches Langhaus: gebauchte Wände, tief heruntergezogenes Torf-/Schindeldach, gekreuzte
    Giebelbalken mit Drachenköpfen, Rauchloch, Schilde am Eingang."""
    w = _welt(seed)
    u = U[g]
    dunkel = _stil(seed) == 0
    holz = "spruce" if dunkel else "dark_oak"
    dach = Verlauf(w, "Torf", ["moss_block", "mossy_cobblestone", "grass_block"]) if dunkel else \
        Verlauf(w, "Schindel", ["spruce_planks", "dark_oak_planks", "spruce_planks"])
    L = _r(14 * u + 6, 9)
    B = 3 * u + 2
    _gras(w, L // 2 + 6)
    for x in range(-L // 2, L // 2 + 1):
        t = x / (L / 2)
        b = B * (1 - 0.15 * t * t)
        H = _r(2.5 * u + 1, 2)
        for z in range(-int(b) - 1, int(b) + 2):
            if abs(z) <= b:
                w.setze(x, 0, z, w.b(f"{holz}_planks"))
        for s in (-1, 1):
            for y in range(1, H + 1):
                w.setze(x, y, s * int(b), w.b(f"stripped_{holz}_log", axis="y") if x % 3 == 0 else
                        w.b(f"{holz}_planks"))
        for kk in range(int(b) + 3):
            y = H + 1 + int(kk * 0.9)
            for s in (-1, 1):
                z = s * (int(b) + 1 - kk)
                w.setze(x, y, z, dach(1 + w.rng.random() * 1.5, x, y, z))
            if int(b) + 1 - kk <= 0:
                break
    for s in (-1, 1):
        x = s * (L // 2)
        for y in range(1, int(B) + 5):
            for z in range(-int(B), int(B) + 1):
                if w.frei(x, y, z) and abs(z) < (int(B) + 3 - (y - 1) * 0.9):
                    w.setze(x, y, z, w.b(f"{holz}_planks"))
        top = int(B) + _r(2.5 * u + 1, 2) + 2
        for kk in range(_r(2 * u + 1, 2)):
            for sz in (-1, 1):
                w.setze(x + s, top + kk, sz * (kk + 1), w.b(f"stripped_{holz}_log", axis="y"))
        w.setze(x + s, top + _r(2 * u + 1, 2), _r(2 * u + 1, 2) + 1, w.b("gold_block") if not dunkel else
                w.b("dark_oak_planks"))
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(L // 2, y, 0, w.b(f"{holz}_door", facing="east", half=half, hinge="left", open=False, powered=False))
    for z in (-2, 2):
        w.setze(L // 2 + 1, 2, z, w.b("red_wool" if z < 0 else "yellow_wool"))
    w.setze(0, int(B) + _r(2.5 * u + 1, 2) + 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                     waterlogged=False))
    return w


def stabkirche(seed, g=2):
    """Stabkirche: mehrfach gestaffelte Schindeldächer, Dachreiter, geschnitzte Drachenköpfe an den Firsten."""
    w = _welt(seed)
    u = U[g]
    holz = "dark_oak" if _stil(seed) == 0 else "spruce"
    st = Stil(w, Verlauf(w, "Stäbe", [f"{holz}_planks", f"stripped_{holz}_log", f"{holz}_planks"]), holz=holz,
              dach=holz, sockel="cobblestone", fachwerk=False)
    _gras(w, 9 * u + 6)
    h = _r(3.5 * u + 1.5, 3)
    y = 0
    for s in range(3 + (g >= 2)):
        hh = max(1, h - s)
        eh = _r(2.5 * u + 2, 3)
        yt, a, b, c, d = kasten_haus(w, st, -hh, -hh, hh, hh, y, 1, eh=eh, blumen=False, laternen=s == 0)
        satteldach(w, st, a - (s == 0), b - (s == 0), c + (s == 0), d + (s == 0), yt, ue=1, first_x=s % 2 == 0)
        for sx in (-1, 1):
            w.setze(sx * (hh + 2), yt + hh + 1, 0, w.b(f"stripped_{holz}_log", axis="x"))
            w.setze(sx * (hh + 3), yt + hh + 2, 0, w.b("gold_block") if _stil(seed) == 1 else w.b(f"{holz}_planks"))
        y = yt + 1
    top = max(p[1] for p in w.bloecke)
    for kk in range(_r(4 * u + 1, 3)):
        w.setze(0, top + 1 + kk, 0, w.b(f"{holz}_planks") if kk < 2 else w.b(f"{holz}_fence", north=False, south=False,
                                                                               east=False, west=False, waterlogged=False))
    return w


def runenstein(seed, g=1):
    """Runenstein mit eingeritztem Schlangenband in Farbe, auf einem kleinen Steinsockel."""
    w = _welt(seed)
    u = U[g]
    _gras(w, 3 * u + 3)
    H = _r(6 * u + 3, 4)
    b = _r(1.4 * u + 0.6, 1)
    farbe = "red_terracotta" if _stil(seed) == 0 else "blue_terracotta"
    for y in range(1, H + 1):
        bb = b if y < H - 1 else max(0, b - 1)
        for x in range(-bb, bb + 1):
            for z in (0, 1) if u > 1 else (0,):
                band = abs(abs(x) + abs(y - H / 2) * 0.6 - bb * 0.9) < 0.6 and z == 0
                w.setze(x, y, z, w.b(farbe) if band else w.b(["stone", "andesite", "tuff"][(x + y) % 3]))
    for x in range(-b - 1, b + 2):
        w.setze(x, 0, 0, w.b("mossy_cobblestone"))
    return w


def schiffssetzung(seed, g=2):
    """Grabhügel mit Schiffssetzung: Steine in Schiffsform um einen Hügel, Bug- und Achtersteine höher."""
    w = _welt(seed)
    u = U[g]
    L, B = 12 * u + 5, 4 * u + 2
    _gras(w, L + 3)
    for x, z in scheibe(B * 0.9):
        d = math.hypot(x, z) / (B * 0.9)
        for y in range(0, int((1 - d * d) * 3 * u) + 1):
            w.setze(x, y, z, w.b("grass_block", snowy=False) if y == int((1 - d * d) * 3 * u) else w.b("dirt"))
    n = int(16 * u) + 8
    for i in range(n):
        t = i / n * 2 * math.pi
        x = math.cos(t) * L
        z = math.sin(t) * B * abs(math.sin(t)) ** 0.3
        h = 1 + int((abs(math.cos(t)) ** 6) * 3 * u)
        for y in range(1, h + 1):
            w.setze(round(x), y, round(z), w.b(["stone", "mossy_cobblestone", "andesite"][i % 3]))
    return w


def thronhalle(seed, g=2):
    """Große Methalle: Säulenreihen, Feuergrube, Tafeln mit Bänken, Thron auf einem Podest, Schilde an den Wänden."""
    w = _welt(seed)
    u = U[g]
    holz = "spruce" if _stil(seed) == 0 else "dark_oak"
    st = Stil(w, Verlauf(w, "Holz", [f"{holz}_planks", f"stripped_{holz}_log"]), holz=holz, dach=holz,
              sockel="cobblestone", fachwerk=True, balken=f"{holz}_log")
    bx, bz = _r(10 * u + 4, 7), _r(5 * u + 3, 4)
    _gras(w, bx + 4)
    yt, a, b, c, d = kasten_haus(w, st, -bx, -bz, bx, bz, 0, 1, eh=_r(4 * u + 2, 4), fenster_abstand=4,
                                 tuer_seite="east", blumen=False)
    satteldach(w, st, a, b, c, d, yt, ue=2)
    for x in range(-bx + 2, bx - 1):
        w.setze(x, 0, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)
                if x % 4 == 0 else w.b("cobblestone"))
    for x in range(-bx + 3, bx - 2, 2):
        for z in (-2, 2):
            w.setze(x, 1, z, w.b(f"{holz}_fence", north=False, south=False, east=False, west=False, waterlogged=False))
            w.setze(x, 2, z, w.b(f"{holz}_pressure_plate", powered=False))
            w.setze(x, 1, z + (1 if z > 0 else -1), treppe(w, holz, "north" if z > 0 else "south"))
    w.setze(-bx + 1, 1, 0, w.b("gold_block"))
    w.setze(-bx + 1, 2, 0, treppe(w, holz, "west"))
    for x in range(-bx + 2, bx, 3):
        for z in (-bz + 1, bz - 1):
            w.setze(x, 3, z, w.b(["red_wool", "yellow_wool", "blue_wool"][(x // 3) % 3]))
    return w


def palisadendorf(seed, g=2):
    """Palisadendorf: Ring aus angespitzten Stämmen mit Tor, darin kleine Häuser, Feuerstelle und Brunnen."""
    w = _welt(seed)
    u = U[g]
    R = 12 * u + 6
    _gras(w, R + 3)
    for x, z in kreisrand(R):
        h = 3 + int(u) + (x + z) % 2
        if abs(x) <= 1 and z > 0:
            continue
        for y in range(1, h + 1):
            w.setze(x, y, z, w.b("spruce_log", axis="y"))
        w.setze(x, h + 1, z, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    n = [2, 3, 5, 7][g]
    for i in range(n):
        a = i * 2 * math.pi / n + 0.5
        d = R * 0.55
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        st = Stil(w, Verlauf(w, "Holz", ["spruce_planks", "stripped_spruce_log"]), holz="spruce", dach="spruce",
                  sockel="cobblestone", fachwerk=False)
        hx, hz = _r(2 * u + 1, 2), _r(1.6 * u + 1, 2)
        yt, a_, b_, c_, d_ = kasten_haus(w, st, cx - hx, cz - hz, cx + hx, cz + hz, 0, 1, eh=3, blumen=False,
                                         laternen=False)
        satteldach(w, st, a_, b_, c_, d_, yt)
    w.setze(0, 1, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    return w


WIKINGER = {
    "langhaus": ("Langhaus", langhaus),
    "stabkirche": ("Stabkirche", stabkirche),
    "runenstein": ("Runenstein", runenstein),
    "schiffssetzung": ("Schiffssetzung", schiffssetzung),
    "thronhalle": ("Methalle", thronhalle),
    "palisadendorf": ("Palisadendorf", palisadendorf),
}


# ============================================================================ Mittelaltermarkt

STOFFE = ["red_wool", "blue_wool", "yellow_wool", "green_wool", "white_wool", "orange_wool", "purple_wool"]


def marktstand(w, x0, z0, b, t, stoff, waren, holz="spruce"):
    """Stand mit Ladentisch, Stoffdach (gestreift), Waren und Laterne. Front nach +z."""
    for x in (x0, x0 + b):
        for z in (z0, z0 + t):
            for y in range(1, 4):
                w.setze(x, y, z, _pfosten(w, f"{holz}_fence"))
    for x in range(x0, x0 + b + 1):
        for k, z in enumerate(range(z0 - 1, z0 + t + 2)):
            y = 4 + (1 if z0 <= z <= z0 + t - 1 and k < t else 0) - (1 if z == z0 + t + 1 else 0)
            w.setze(x, y, z, w.b(stoff) if (x - x0) % 2 == 0 else w.b("white_wool"))
        w.setze(x, 1, z0 + t, w.b(f"{holz}_slab", type="top", waterlogged=False))
        if 0 < x - x0 < b:
            w.setze(x, 2, z0 + t, waren[(x - x0) % len(waren)])
    w.setze(x0 + b // 2, 3, z0 + t // 2, w.b("lantern", hanging=True, waterlogged=False))


def _waren(w):
    return [w.b("melon"), w.b("pumpkin"), w.b("hay_block", axis="y"), w.b("barrel", facing="up", open=False),
            w.b("decorated_pot", facing="north", waterlogged=False), w.b("cake", bites=0), w.b("flower_pot")]


def marktstaende(seed, g=1):
    """Reihe von Marktständen mit Stoffdächern in verschiedenen Farben und Waren."""
    w = _welt(seed)
    u = U[g]
    n = [2, 3, 5, 8][g]
    L = n * 5
    _gras(w, L // 2 + 5)
    for x in range(-L // 2 - 1, L // 2 + 2):
        for z in range(-2, 6):
            w.setze(x, 0, z, w.b("cobblestone") if (x + z) % 3 else w.b("stone_bricks"))
    for i in range(n):
        marktstand(w, -L // 2 + i * 5, -1, 3, 2, STOFFE[(i + _stil(seed) * 3) % len(STOFFE)], _waren(w))
    return w


def marktbrunnen(seed, g=1):
    """Prunkvoller Marktbrunnen: achteckiges Becken, Säule mit Kapitell, Wasserspeier und Goldkugel."""
    w = _welt(seed)
    u = U[g]
    R = 3.5 * u + 2.5
    stein = "stone_bricks" if _stil(seed) == 0 else "smooth_sandstone"
    _gras(w, R + 4)
    for x, z in scheibe(R + 2.5):
        w.setze(x, 0, z, w.b("cobblestone") if (x + z) % 2 else w.b("stone"))
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b(stein))
        w.setze(x, 1, z, w.b("water", level=0))
    for x, z in kreisrand(R):
        w.setze(x, 1, z, w.b(stein))
        w.setze(x, 2, z, w.b(f"{'stone_brick' if _stil(seed) == 0 else 'smooth_sandstone'}_slab", type="bottom",
                             waterlogged=False))
    H = _r(5 * u + 2, 4)
    for y in range(1, H + 1):
        w.setze(0, y, 0, w.b("quartz_pillar", axis="y") if _stil(seed) == 1 else w.b("chiseled_stone_bricks"))
    for x, z in scheibe(1.3):
        w.setze(x, H + 1, z, w.b(stein))
    w.setze(0, H + 2, 0, w.b("gold_block"))
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        w.setze(dx, H - 1, dz, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                                   waterlogged=False))
    return w


def gauklerzelt(seed, g=2):
    """Großes Gaukler-Zelt mit Streifen, Mittelmast mit Wimpel, Fahnen ringsum und Eingang mit Vordach."""
    w = _welt(seed)
    u = U[g]
    R = 5 * u + 3
    H = _r(4 * u + 2, 3)
    _gras(w, R + 4)
    farben = ["red_wool", "white_wool"] if _stil(seed) == 0 else ["blue_wool", "yellow_wool"]
    for y in range(1, H + 1):
        for i, (x, z) in enumerate(kreisrand(R)):
            if not (z > R - 1.5 and abs(x) <= 1 and y <= 2):
                w.setze(x, y, z, w.b(farben[int((math.atan2(z, x) + math.pi) / (2 * math.pi) * 16) % 2]))
    kh = _r(R * 0.9, 3)
    for kk in range(kh + 1):
        r = R * (1 - kk / (kh + 1))
        for x, z in kreisrand(max(0.3, r)):
            w.setze(x, H + 1 + kk, z, w.b(farben[int((math.atan2(z, x) + math.pi) / (2 * math.pi) * 16) % 2]))
    for y in range(H + kh + 2, H + kh + 2 + _r(2 * u, 2)):
        w.setze(0, y, 0, _pfosten(w, "spruce_fence"))
    for k in range(_r(2 * u + 1, 2)):
        w.setze(1 + k, H + kh + 1 + _r(2 * u, 2), 0, w.b(farben[0]))
    for i, (x, z) in enumerate(kreisrand(R + 2)):
        if i % 6 == 0:
            for y in range(1, 4):
                w.setze(x, y, z, _pfosten(w, "spruce_fence"))
            w.setze(x, 4, z, w.b(STOFFE[i % len(STOFFE)]))
    return w


def turnierplatz(seed, g=2):
    """Turnierplatz: Schranke in der Mitte, Holztribüne mit Baldachin, Wappenfahnen und Zelte."""
    w = _welt(seed)
    u = U[g]
    L, B = _r(16 * u + 6, 10), _r(5 * u + 3, 4)
    _gras(w, L + 3)
    verbinde(w, [(x, 1, z) for x in range(-L, L + 1) for z in (-B, B)] +
             [(x, 1, z) for x in (-L, L) for z in range(-B, B + 1)], "oak_fence")
    for x in range(-L + 3, L - 2):
        w.setze(x, 1, 0, w.b("stripped_oak_log", axis="x"))
        w.setze(x, 2, 0, w.b("oak_fence", north=False, south=False, east=True, west=True, waterlogged=False))
    tb = _r(5 * u + 2, 3)
    for kk in range(3):
        for x in range(-tb, tb + 1):
            w.setze(x, kk + 1, B + 2 + kk, w.b("spruce_planks"))
            w.setze(x, kk + 2, B + 2 + kk, treppe(w, "spruce", "south"))
    for x in range(-tb - 1, tb + 2):
        for z in range(B + 2, B + 6):
            w.setze(x, 6, z, w.b("red_wool" if (x // 2) % 2 else "yellow_wool"))
    for x in (-tb - 1, tb + 1):
        for y in range(1, 6):
            w.setze(x, y, B + 2, _pfosten(w, "spruce_fence"))
            w.setze(x, y, B + 5, _pfosten(w, "spruce_fence"))
    for s in (-1, 1):
        x = s * (L + 3)
        for y in range(1, 5):
            w.setze(x, y, 0, _pfosten(w, "spruce_fence"))
        for k in range(3):
            w.setze(x, 4 - k // 2, 1 + k, w.b("blue_wool" if s < 0 else "red_wool"))
    return w


def ladenzeile(seed, g=2):
    """Ladenzeile: aneinandergebaute Fachwerk-Läden mit Auslagen, Vordächern und hängenden Zunftschildern."""
    w = _welt(seed)
    u = U[g]
    n = [2, 3, 4, 6][g]
    bx = 6
    L = n * (bx + 1)
    _gras(w, L // 2 + 4)
    for i in range(n):
        x0 = -L // 2 + i * (bx + 1)
        farbe = ["white_terracotta", "yellow_terracotta", "light_blue_terracotta", "pink_terracotta"][i % 4]
        st = Stil(w, Verlauf(w, farbe, [farbe]), holz="dark_oak", dach="brick" if i % 2 else "deepslate_tile",
                  dach_voll="bricks" if i % 2 else "deepslate_tiles", sockel="stone_bricks")
        yt, a, b, c, d = kasten_haus(w, st, x0, -4, x0 + bx, 3, 0, 2 + (i % 2), eh=4, jetty=True, fenster_abstand=2)
        satteldach(w, st, a, b, c, d, yt, ue=0, first_x=False)
        for x in range(x0, x0 + bx + 1):
            w.setze(x, 3, 4, w.b("dark_oak_slab", type="bottom", waterlogged=False))
        w.setze(x0 + bx - 1, 3, 5, w.b("dark_oak_fence", north=True, south=False, east=False, west=False,
                                       waterlogged=False))
        w.setze(x0 + bx - 1, 2, 5, w.b("chain", axis="y", waterlogged=False))
        w.setze(x0 + bx - 1, 1, 5, w.b("barrel", facing="south", open=False) if i % 2 else w.b("anvil", facing="north"))
    return w


MARKT = {
    "marktstaende": ("Marktstände", marktstaende),
    "marktbrunnen": ("Marktbrunnen", marktbrunnen),
    "gauklerzelt": ("Gaukler-Zelt", gauklerzelt),
    "turnierplatz": ("Turnierplatz", turnierplatz),
    "ladenzeile": ("Ladenzeile", ladenzeile),
}

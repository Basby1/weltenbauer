"""Wüstenreich und Eisreich – zwei Pakete.
Wüste: Oase, Basar, Kuppelpalast, Lehmhäuser, Sandruine, Karawanserei, Minarett, Lehmfestung.
Eis: Eispalast, Iglu-Dorf, Gletschertor, Eiskristall, gefrorener Wasserfall, Nordhütte, Riesenschneemann,
Eiswachturm."""

from __future__ import annotations

import math

import numpy as np

from lib import Verlauf, Welt, laub
from skulptur import Skulptur, ell, kap, kegel, kreisrand, platte, scheibe, treppe, verbinde, zur_mitte

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _sand(w, r, cx=0, cz=0, rot=False):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, w.b("red_sand" if rot else "sand"), ueberschreiben=False)


def _schnee(w, r, cx=0, cz=0):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, w.b("snow_block"), ueberschreiben=False)


class Wueste:
    def __init__(self, w, seed):
        self.w = w
        self.rot = _stil(seed) == 1
        if not self.rot:
            self.lehm = Verlauf(w, "Sandstein", ["sandstone", "cut_sandstone", "smooth_sandstone", "end_stone"])
            self.tr = "smooth_sandstone"
            self.kuppel = Verlauf(w, "Türkis", ["cyan_terracotta", "waxed_oxidized_copper", "prismarine_bricks",
                                                "light_blue_terracotta"])
            self.zier = "chiseled_sandstone"
        else:
            self.lehm = Verlauf(w, "Rotsandstein", ["red_sandstone", "cut_red_sandstone", "smooth_red_sandstone",
                                                    "terracotta"])
            self.tr = "smooth_red_sandstone"
            self.kuppel = Verlauf(w, "Gold", ["orange_terracotta", "raw_gold_block", "gold_block", "yellow_terracotta"])
            self.zier = "chiseled_red_sandstone"
        self.stoffe = ["red_wool", "orange_wool", "yellow_wool", "purple_wool", "cyan_wool", "blue_wool", "white_wool"]

    def l(self, x, y, z, H=10):
        return self.lehm(0.3 + 2.5 * min(1, y / max(1, H)) + self.w.rng.random() * 0.9, x, y, z)


def palme(w, x, z, u, y0=1):
    """Palme mit gebogenem Stamm, Kokosnüssen und hängenden Wedeln."""
    h = _r(6 * u + 3, 5)
    a = w.rng.random() * 2 * math.pi
    pts = []
    for k in range(h):
        t = k / h
        px, pz = x + math.cos(a) * t * t * 2.5 * u, z + math.sin(a) * t * t * 2.5 * u
        w.setze(round(px), y0 + k, round(pz), w.b("jungle_log", axis="y"))
        pts.append((round(px), y0 + k, round(pz)))
    tx, ty, tz = pts[-1]
    w.setze(tx, ty + 1, tz, laub(w, "jungle"))
    for i in range(7):
        b = i * 2 * math.pi / 7
        lang = (2.5 + w.rng.random()) * u + 2
        for kk in range(int(lang * 2)):
            t = kk / (lang * 2)
            w.setze(round(tx + math.cos(b) * lang * t), round(ty + 1 + 1.2 * math.sin(t * math.pi) - 1.5 * t * t * u),
                    round(tz + math.sin(b) * lang * t), laub(w, "jungle"), ueberschreiben=False)
    w.setze(tx + 1, ty - 1, tz, w.b("cocoa", age=2, facing="west"))


def zwiebelkuppel(w, k, cx, cz, y0, R, mat):
    """Zwiebelkuppel mit Spitze."""
    H = R * 2.6
    for y in range(int(H) + 1):
        t = y / H
        r = R * (1.25 * math.sin(math.pi * min(1, t * 1.15)) ** 0.8) if t < 0.87 else 0
        if t >= 0.87:
            r = R * 0.25 * (1 - (t - 0.87) / 0.13)
        for x, z in scheibe(max(0.3, r), cx, cz):
            w.setze(x, y0 + y, z, mat(1 + 2 * t + w.rng.random() * 0.4, x, y0 + y, z))
    w.setze(cx, y0 + int(H) + 1, cz, w.b("gold_block"))
    w.setze(cx, y0 + int(H) + 2, cz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))


def minarett_bau(w, k, cx, cz, R, H, y0=0):
    for y in range(y0, y0 + H):
        for x, z in kreisrand(R, cx, cz):
            w.setze(x, y, z, w.b(k.zier) if (y - y0) % 6 == 0 else k.l(x, y, z, H))
    for yb in (y0 + int(H * 0.55), y0 + H):
        for x, z in kreisrand(R + 1, cx, cz):
            w.setze(x, yb, z, treppe(w, k.tr, zur_mitte(x, z, cx, cz), "top"))
        verbinde(w, [(x, yb + 1, z) for x, z in kreisrand(R + 1, cx, cz)], "birch_fence")
    zwiebelkuppel(w, k, cx, cz, y0 + H + 2, R * 0.9, k.kuppel)


def _bogen_tor(w, mat, x0, x1, z, y0, h):
    """Spitzbogen-/Hufeisentor (Öffnung) in einer Wand bei z – entfernt Blöcke."""
    m = (x0 + x1) / 2
    hb = (x1 - x0) / 2
    for x in range(x0, x1 + 1):
        for y in range(y0, y0 + h + int(hb) + 1):
            if y < y0 + h or (abs(x - m) / max(0.5, hb)) ** 2 + ((y - y0 - h) / max(0.5, hb * 1.1)) ** 2 <= 1:
                w.bloecke.pop((x, y, z), None)


# ============================================================================ Wüste

def oase(seed, g=1):
    """Oase: Wasserloch mit Schilf und Seerosen, Palmen, Nomadenzelte, Teppiche und Feuerstelle."""
    w = _welt(seed)
    k = Wueste(w, seed)
    u = U[g]
    R = 10 * u + 5
    _sand(w, R + 4, rot=k.rot)
    for x, z in scheibe(R * 0.4 + 1):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("sand"))
        if w.rng.random() < 0.06:
            w.setze(x, 1, z, w.b("lily_pad"))
    for x, z in kreisrand(R * 0.4 + 2):
        w.setze(x, 0, z, w.b("grass_block", snowy=False))
        if w.rng.random() < 0.35:
            w.setze(x, 1, z, w.b("sugar_cane", age=0))
            w.setze(x, 2, z, w.b("sugar_cane", age=0))
    for i in range(3 + 2 * g):
        a = i * 2 * math.pi / (3 + 2 * g) + 0.4
        d = R * (0.5 + 0.15 * (i % 2))
        palme(w, round(math.cos(a) * d), round(math.sin(a) * d), u)
    for s in (-1, 1):
        cx, cz = s * round(R * 0.75), -s * round(R * 0.3)
        b = _r(2 * u + 1, 2)
        for x in range(cx - b, cx + b + 1):
            for zz in range(cz - b, cz + b + 1):
                w.setze(x, 0, zz, w.b(k.stoffe[(x + zz) % len(k.stoffe)].replace("_wool", "_wool")))
            for h in range(b + 1):
                for zz in (cz - b + h, cz + b - h):
                    w.setze(x, 1 + h, zz, w.b("white_wool" if (x // 2) % 2 else k.stoffe[s % 3]))
    w.setze(0, 1, round(R * 0.65), w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


def basar(seed, g=1):
    """Basargasse: Stände mit bunten Sonnensegeln, Teppichen, Krügen, Fässern und Laternen an Seilen."""
    w = _welt(seed)
    k = Wueste(w, seed)
    u = U[g]
    L = _r(12 * u + 6, 8)
    _sand(w, L + 4, rot=k.rot)
    for x in range(-L, L + 1):
        for z in (-1, 0, 1):
            w.setze(x, 0, z, w.b(k.tr))
    for s in (-1, 1):
        x = -L + 1
        while x < L - 3:
            br = 3 + int(w.rng.integers(0, 2))
            stoff = k.stoffe[int(w.rng.integers(len(k.stoffe)))]
            for xx in range(x, x + br + 1):
                for zz in range(s * 2, s * 5, s):
                    w.setze(xx, 0, zz, w.b(stoff.replace("_wool", "_carpet") if False else k.tr))
                    w.setze(xx, 1, zz, w.b(stoff.replace("_wool", "_carpet")) if (xx + zz) % 3 else
                            w.b("barrel", facing="up", open=False))
                for h, zz in enumerate(range(s * 5, s * 1, -s)):
                    w.setze(xx, 4 - (h // 2 if h > 1 else 0), zz, w.b(stoff) if (xx - x) % 2 else w.b("white_wool"))
            for xx in (x, x + br):
                for y in range(1, 4):
                    w.setze(xx, y, s * 2, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                              waterlogged=False))
                    w.setze(xx, y, s * 5, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                              waterlogged=False))
            w.setze(x + 1, 2, s * 4, w.b("decorated_pot", facing="north", waterlogged=False))
            x += br + 2
    for x in range(-L + 2, L - 1, 4):
        w.setze(x, 4, 0, w.b("chain", axis="y", waterlogged=False))
        w.setze(x, 3, 0, w.b("lantern", hanging=True, waterlogged=False))
    return w


def kuppelpalast(seed, g=2):
    """Palast mit großer Zwiebelkuppel, vier Minaretten, Hufeisenbögen, Innenhof mit Brunnen und
    gefliesten Bändern."""
    w = _welt(seed)
    k = Wueste(w, seed)
    u = U[g]
    h = _r(8 * u + 4, 6)
    H = _r(6 * u + 4, 5)
    _sand(w, h + 10, rot=k.rot)
    for y in range(0, H + 1):
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                rand = max(abs(x), abs(z)) == h
                if y == 0:
                    w.setze(x, y, z, w.b(k.tr))
                elif rand:
                    band = y == H - 1
                    w.setze(x, y, z, k.kuppel(1.5, x, y, z) if band else k.l(x, y, z, H))
                elif y == H and max(abs(x), abs(z)) > h - 3:
                    w.setze(x, y, z, w.b(k.tr))
    for x in range(-h, h + 1):
        for z in range(-h, h + 1):
            if max(abs(x), abs(z)) == h and (x + z) % 2 == 0:
                w.setze(x, H + 1, z, k.l(x, H + 1, z, 1))
    for s in (-1, 1):
        for b in range(-h + 2, h - 1, 4):
            for y in range(2, 4 + int(u)):
                w.setze(b, y, s * h, w.b("orange_stained_glass" if k.rot else "light_blue_stained_glass"))
                w.setze(s * h, y, b, w.b("orange_stained_glass" if k.rot else "light_blue_stained_glass"))
    _bogen_tor(w, None, -_r(1.5 * u, 1), _r(1.5 * u, 1), h, 1, _r(2.5 * u + 1, 3))
    Rk = h * 0.55
    for y in range(H + 1, H + 1 + _r(2 * u, 2)):
        for x, z in kreisrand(Rk):
            w.setze(x, y, z, k.l(x, y, z, 1))
    zwiebelkuppel(w, k, 0, 0, H + 1 + _r(2 * u, 2), Rk, k.kuppel)
    for sx in (-1, 1):
        for sz in (-1, 1):
            minarett_bau(w, k, sx * (h + 1), sz * (h + 1), 1.2 * u + 0.8, H + _r(10 * u, 6))
    for x, z in kreisrand(1.6 * u + 0.6, 0, h + 4):
        w.setze(x, 1, z, w.b(k.zier))
    for x, z in scheibe(1.6 * u - 0.4, 0, h + 4):
        w.setze(x, 0, z, w.b("water", level=0))
    return w


def lehmhaeuser(seed, g=1):
    """Gruppe flacher Lehmhäuser auf mehreren Ebenen mit Dachterrassen, Leitern und herausragenden Balken."""
    w = _welt(seed)
    k = Wueste(w, seed)
    k.lehm = Verlauf(w, "Lehm", ["packed_mud", "mud_bricks", "terracotta", "smooth_sandstone"]) if not k.rot else \
        Verlauf(w, "Lehm", ["terracotta", "orange_terracotta", "packed_mud", "brown_terracotta"])
    u = U[g]
    anzahl = [3, 5, 8, 12][g]
    R = 6 * u + 4 + anzahl
    _sand(w, R + 2, rot=k.rot)
    for i in range(anzahl):
        a = i * 2.39996
        d = R * 0.7 * math.sqrt((i + 0.5) / anzahl)
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        bx, bz = _r((2 + w.rng.random() * 2) * u + 1, 2), _r((2 + w.rng.random() * 2) * u + 1, 2)
        H = _r((3 + w.rng.random() * 3) * u + 1, 3)
        for y in range(0, H + 1):
            for x in range(cx - bx, cx + bx + 1):
                for z in range(cz - bz, cz + bz + 1):
                    rand = x in (cx - bx, cx + bx) or z in (cz - bz, cz + bz)
                    if y == H or rand:
                        fen = rand and y == 2 and (x + z) % 3 == 0 and y < H
                        w.setze(x, y, z, w.b("air") if fen and False else (w.b("brown_stained_glass") if fen else
                                                                           k.l(x, y, z, H)))
                        if y == H and rand:
                            w.setze(x, H + 1, z, k.l(x, H + 1, z, H) if (x + z) % 3 else
                                    w.b("flower_pot") if w.rng.random() < 0.1 else k.l(x, H + 1, z, H))
            if y == H - 1:
                for x in range(cx - bx, cx + bx + 1, 2):
                    w.setze(x, y, cz + bz + 1, w.b("spruce_fence", north=True, south=False, east=False, west=False,
                                                    waterlogged=False))
        w.setze(cx, 1, cz + bz, w.b("spruce_door", facing="south", half="lower", hinge="left", open=False,
                                    powered=False))
        w.setze(cx, 2, cz + bz, w.b("spruce_door", facing="south", half="upper", hinge="left", open=False,
                                    powered=False))
        for y in range(1, H + 2):
            w.setze(cx + bx + 1, y, cz, w.b("ladder", facing="east", waterlogged=False))
    return w


def sandruine(seed, g=1):
    """Halb im Sand versunkene Tempelruine: Säulenstümpfe, umgestürzte Säulen, Treppe, Wüstenwächter-Kopf."""
    w = _welt(seed)
    k = Wueste(w, seed)
    u = U[g]
    L, B = _r(10 * u + 5, 7), _r(6 * u + 3, 4)
    _sand(w, L + 5, rot=k.rot)
    for x in range(-L, L + 1, 3):
        for s in (-1, 1):
            h = int((2 + 6 * w.rng.random()) * u) + 1
            for y in range(1, h + 1):
                w.setze(x, y, s * B, w.b(k.zier) if y == h else k.l(x, y, s * B, 8))
    for i in range(1 + g):
        x0, z0 = round((w.rng.random() - 0.5) * L), round((w.rng.random() - 0.5) * B)
        for kk in range(_r(4 * u + 2, 3)):
            w.setze(x0 + kk, 1, z0, k.l(x0 + kk, 1, z0, 2))
    for kk in range(3):
        for x in range(-2, 3):
            w.setze(x, kk, -L // 2 + kk, treppe(w, k.tr, "south") if True else None)
    S = Skulptur(w, u)
    S.mat("k", lambda x, y, z, *_: k.l(x, y, z, 10))
    S.mat("a", w.b("lapis_block") if not k.rot else w.b("gold_block"))
    S.plus(ell(0, 2.5, 0, 2.6, 3.2, 2.6), "k")
    S.plus(kap((0, 3, 2.2), (0, 1.4, 3.1), 0.6, 0.8), "k")
    S.plus(lambda X, Y, Z: (Y > 2.5) & (Y < 6) & (np.abs(X) > 2) & (np.abs(X) < 3.4) & (Z < 1.5) & (Z > -2), "a")
    S.plus(lambda X, Y, Z: (Y > 5) & (Y < 5.8) & (X * X + Z * Z < 9), "a")
    S.rendern((-5, 0, -4), (5, 7, 5), versatz=(L * 0.6 + 0.5, -0.5, 0.5))
    w.bloecke = {p: b for p, b in w.bloecke.items() if p[1] >= 0}
    return w


def karawanserei(seed, g=2):
    """Karawanserei: quadratischer Hof mit Arkaden ringsum, großes Bogentor, Brunnen und Kamel-Tröge."""
    w = _welt(seed)
    k = Wueste(w, seed)
    u = U[g]
    h = _r(9 * u + 4, 6)
    H = _r(4 * u + 2, 4)
    _sand(w, h + 6, rot=k.rot)
    for x in range(-h, h + 1):
        for z in range(-h, h + 1):
            ring = max(abs(x), abs(z))
            w.setze(x, 0, z, w.b(k.tr) if ring > h - 4 else w.b("sand"))
            if ring == h:
                for y in range(1, H + 2):
                    w.setze(x, y, z, k.l(x, y, z, H))
            elif ring == h - 3:
                t = x if abs(z) == h - 3 else z
                if t % 3 == 0:
                    for y in range(1, H + 1):
                        w.setze(x, y, z, k.l(x, y, z, H))
                else:
                    w.setze(x, H, z, k.l(x, H, z, H))
                    w.setze(x, H - 1, z, treppe(w, k.tr, "east" if t % 3 == 1 else "west", "top") if abs(z) == h - 3
                            else treppe(w, k.tr, "south" if t % 3 == 1 else "north", "top"))
            if h - 3 <= ring <= h:
                w.setze(x, H + 1, z, w.b(k.tr))
    _bogen_tor(w, None, -_r(1.5 * u, 1), _r(1.5 * u, 1), h, 1, _r(2.5 * u + 1, 3))
    for x in range(-_r(2 * u + 1), _r(2 * u + 1) + 1):
        for y in range(H + 2, H + 2 + _r(3 * u, 2)):
            w.setze(x, y, h, k.l(x, y, h, H))
    for x, z in kreisrand(1.5 * u + 0.5):
        w.setze(x, 1, z, w.b(k.zier))
    w.setze(0, 0, 0, w.b("water", level=0))
    palme(w, h - 6, h - 6, u * 0.7)
    palme(w, -h + 6, -h + 6, u * 0.7)
    return w


def minarett(seed, g=1):
    """Einzelnes schlankes Minarett mit zwei Balkonen und Zwiebelkuppel."""
    w = _welt(seed)
    k = Wueste(w, seed)
    u = U[g]
    _sand(w, 5 * u + 3, rot=k.rot)
    minarett_bau(w, k, 0, 0, 1.4 * u + 0.8, _r(18 * u + 6, 10))
    return w


def lehmfestung(seed, g=2):
    """Lehmfestung (Kasbah): sich verjüngende Ecktürme mit Zinnen, Mauerring, Wohnturm und Tor mit Holzbalken."""
    w = _welt(seed)
    k = Wueste(w, seed)
    k.lehm = Verlauf(w, "Lehm", ["packed_mud", "mud_bricks", "terracotta", "orange_terracotta"])
    u = U[g]
    h = _r(8 * u + 4, 6)
    Hm = _r(5 * u + 3, 4)
    _sand(w, h + 6, rot=k.rot)
    for x in range(-h, h + 1):
        for z in range(-h, h + 1):
            if max(abs(x), abs(z)) == h:
                for y in range(1, Hm + 1):
                    w.setze(x, y, z, k.l(x, y, z, Hm))
                if (x + z) % 2 == 0:
                    w.setze(x, Hm + 1, z, k.l(x, Hm + 1, z, Hm))
    for sx in (-1, 1):
        for sz in (-1, 1):
            Ht = Hm + _r(5 * u, 3)
            for y in range(1, Ht + 1):
                r = 2 * u + 1 - y * 0.06
                for x in range(-int(r), int(r) + 1):
                    for z in range(-int(r), int(r) + 1):
                        if max(abs(x), abs(z)) == int(r):
                            w.setze(sx * h + x, y, sz * h + z, k.l(x, y, z, Ht))
            for x in range(-int(2 * u + 1), int(2 * u + 1) + 1, 2):
                w.setze(sx * h + x, Ht + 1, sz * h + int(2 * u), k.l(0, Ht, 0, Ht))
    hb = _r(3 * u + 1, 2)
    for y in range(1, Hm + _r(8 * u, 4)):
        for x in range(-hb, hb + 1):
            for z in range(-hb, hb + 1):
                if max(abs(x), abs(z)) == hb:
                    fen = y % 4 == 2 and (x == 0 or z == 0)
                    w.setze(x, y, z, w.b("brown_stained_glass") if fen else k.l(x, y, z, Hm + 8 * u))
    _bogen_tor(w, None, -_r(1.5 * u, 1), _r(1.5 * u, 1), h, 1, _r(2.5 * u + 1, 3))
    return w


WUESTE = {
    "oase": ("Oase", oase),
    "basar": ("Basar", basar),
    "kuppelpalast": ("Kuppelpalast", kuppelpalast),
    "lehmhaeuser": ("Lehmhäuser", lehmhaeuser),
    "sandruine": ("Sandruine", sandruine),
    "karawanserei": ("Karawanserei", karawanserei),
    "minarett": ("Minarett", minarett),
    "lehmfestung": ("Lehmfestung", lehmfestung),
}


# ============================================================================ Eis

class Eis:
    def __init__(self, w, seed):
        self.w = w
        self.polar = _stil(seed) == 1
        self.eis = Verlauf(w, "Eis", ["blue_ice", "packed_ice", "packed_ice", "light_blue_stained_glass",
                                      "white_stained_glass"])
        self.stein = Verlauf(w, "Frostfels", ["deepslate", "cobbled_deepslate", "tuff", "calcite", "snow_block"]) \
            if not self.polar else Verlauf(w, "Frostfels", ["stone", "andesite", "diorite", "calcite", "snow_block"])
        self.licht = w.b("sea_lantern")

    def e(self, x, y, z, v=1.5):
        return self.eis(v + self.w.rng.random() * 1.2, x, y, z)


def eispalast(seed, g=2):
    """Eispalast: Hauptbau aus Packeis mit Bogenfenstern, viele gezackte Eisspitzen-Türme,
    Kristallkrone und gefrorene Freitreppe."""
    w = _welt(seed)
    k = Eis(w, seed)
    u = U[g]
    h = _r(7 * u + 3, 5)
    H = _r(8 * u + 4, 6)
    _schnee(w, h + 10)
    for y in range(0, H + 1):
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                if y == 0 or max(abs(x), abs(z)) == h:
                    fen = 2 <= y <= H - 2 and max(abs(x), abs(z)) == h and (x % 3 == 0 or z % 3 == 0)
                    w.setze(x, y, z, w.b("light_blue_stained_glass") if fen else k.e(x, y, z, 1))
    S = Skulptur(w, 1.0)
    S.mat("e", lambda x, y, z, *_: k.e(x, y, z, 0.8))
    S.mat("k", lambda x, y, z, *_: k.licht if (x + y + z) % 7 == 0 else w.b("light_blue_stained_glass"))
    spitzen = [(0, 0, 3.5 * u + 2, 22 * u + 8)] + \
              [(math.cos(a) * h, math.sin(a) * h, 1.8 * u + 1, (10 + 6 * (i % 2)) * u + 5)
               for i, a in enumerate(np.linspace(0, 2 * math.pi, 8, endpoint=False))]
    for cx, cz, r, hh in spitzen:
        S.plus(lambda X, Y, Z, cx=cx, cz=cz, r=r, hh=hh: (Y >= 0) & (Y <= hh) &
               ((X - cx) ** 2 + (Z - cz) ** 2 <= (r * (1 - Y / hh) ** 0.9 * (0.8 + 0.2 * np.cos(6 * np.arctan2(Z - cz, X - cx))))
                ** 2), "e")
    S.plus(lambda X, Y, Z: (np.abs(np.abs(X) + np.abs(Y - 22 * u - 11) * 0.6 + np.abs(Z)) <= 2.5 * u + 1), "k")
    S.rendern((-h - 4, 0, -h - 4), (h + 4, 26 * u + 16, h + 4), versatz=(0.5, H, 0.5))
    for kk in range(3):
        for x in range(-3, 4):
            w.setze(x, kk, h + 3 - kk, treppe(w, "stone_brick", "north") if kk < 2 else w.b("packed_ice"))
    return w


def iglu_dorf(seed, g=1):
    """Iglu-Dorf: Iglus mit Eingangstunnel und Eisfenster, Feuerstelle, Schlitten und Fischloch."""
    w = _welt(seed)
    k = Eis(w, seed)
    u = U[g]
    anzahl = [1, 3, 5, 8][g]
    R = 4 * u + 3 + anzahl * 2
    _schnee(w, R + 3)
    for i in range(anzahl):
        a = i * 2 * math.pi / max(1, anzahl)
        d = 0 if anzahl == 1 else R * 0.6
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        r = (2.4 + 0.8 * (i % 2)) * u + 1.2
        for y in range(0, int(r) + 1):
            for x, z in scheibe(r + 0.4, cx, cz):
                dd = math.sqrt((x - cx) ** 2 + (z - cz) ** 2 + y * y)
                if r - 1.1 < dd <= r + 0.3:
                    w.setze(x, y + 1, z, w.b("snow_block") if (x + y + z) % 5 else w.b("packed_ice"))
        tx, tz = round(cx + math.cos(a) * r), round(cz + math.sin(a) * r)
        for t in range(2):
            px, pz = tx + round(math.cos(a) * t), tz + round(math.sin(a) * t)
            w.setze(px, 3, pz, w.b("snow_block"))
            w.setze(px + round(math.sin(a)), 2, pz + round(math.cos(a)), w.b("snow_block"))
            w.setze(px - round(math.sin(a)), 2, pz - round(math.cos(a)), w.b("snow_block"))
            w.bloecke.pop((px, 1, pz), None)
            w.bloecke.pop((px, 2, pz), None)
        w.setze(cx, int(r) // 2 + 2, cz - int(r) + 1, w.b("ice"), ueberschreiben=True)
    w.setze(0, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)) if anzahl > 1 \
        else w.setze(int(R * 0.6), 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for x, z in scheibe(1.2, -int(R * 0.5), int(R * 0.6)):
        w.setze(x, 0, z, w.b("water", level=0))
    return w


def gletschertor(seed, g=2):
    """Gewaltiger Bogen aus blauem Gletschereis in verschneitem Fels, mit Eiszapfen."""
    w = _welt(seed)
    k = Eis(w, seed)
    u = U[g]
    R = 9 * u + 5
    d = 3 * u + 2
    _schnee(w, R + 6)
    S = Skulptur(w, 1.0)
    S.mat("e", lambda x, y, z, lx, ly, lz: k.e(x, y, z, 0.2 + ly / R))
    S.mat("f", lambda x, y, z, lx, ly, lz: k.stein(0.4 + 3.5 * ly / (R * 1.2) + w.rng.random() * 0.6, x, y, z))
    S.plus(lambda X, Y, Z: (np.abs(np.sqrt(X * X + Y * Y) - R) <= d * (1 + 0.15 * np.sin(X * 0.6))) & (Y >= 0)
           & (np.abs(Z) <= d * 0.9 + 0.5 * np.sin(Y * 0.4)), "e")
    for s in (-1, 1):
        S.plus(ell(s * R, 0, 0, d * 1.6, R * 0.5, d * 1.4), "f")
    S.rendern((-R - d * 2, 0, -d * 2), (R + d * 2, R + d * 2, d * 2), versatz=(0.5, 1, 0.5))
    for x in range(-int(R), int(R) + 1):
        unten = [p[1] for p in w.bloecke if p[0] == x and p[2] == 0 and p[1] > 2]
        if unten and w.rng.random() < 0.5:
            y0 = min(unten)
            for kk in range(1, int(w.rng.integers(1, 3 + int(u)))):
                w.setze(x, y0 - kk, 0, w.b("pointed_dripstone", vertical_direction="down", thickness="tip",
                                           waterlogged=False) if kk > 1 else w.b("packed_ice"))
    return w


def eiskristall(seed, g=1):
    """Riesiger sternförmiger Eiskristall auf einem Frostfelsen, innen leuchtend."""
    w = _welt(seed)
    k = Eis(w, seed)
    u = U[g]
    R = 7 * u + 3
    _schnee(w, R * 0.6 + 3)
    for x, z in scheibe(R * 0.4 + 1):
        for y in range(0, 2):
            w.setze(x, y, z, k.stein(1 + y, x, y, z))
    S = Skulptur(w, 1.0)
    S.mat("e", lambda x, y, z, lx, ly, lz: k.licht if abs(lx) + abs(ly) < 1.2 else k.e(x, y, z, 1.6))
    for i in range(6):
        a = i * math.pi / 3
        dx, dy = math.cos(a), math.sin(a)
        S.plus(kap((0, 0, 0), (dx * R, dy * R, 0), 0.9 * u + 0.6, 0.3), "e")
        for t in (0.45, 0.7):
            for s in (-1, 1):
                b = a + s * math.pi / 4
                p = (dx * R * t, dy * R * t, 0)
                q = (p[0] + math.cos(b) * R * 0.3, p[1] + math.sin(b) * R * 0.3, 0)
                S.plus(kap(p, q, 0.5 * u + 0.5, 0.25), "e")
    S.plus(ell(0, 0, 0, 1.6 * u + 0.6, 1.6 * u + 0.6, 1.2 * u + 0.6), "e")
    S.rendern((-R - 2, -R - 2, -3), (R + 2, R + 2, 3), versatz=(0.5, R + 2.5, 0.5))
    return w


def gefrorener_wasserfall(seed, g=2):
    """Steile Frostklippe mit einem erstarrten Wasserfall aus Eissäulen und einem zugefrorenen Becken."""
    w = _welt(seed)
    k = Eis(w, seed)
    u = U[g]
    W, H = _r(10 * u + 5, 7), _r(14 * u + 6, 9)
    _schnee(w, W + 6)
    for x in range(-W, W + 1):
        top = H * (1 - (abs(x) / W) ** 2) + 2 * math.sin(x * 0.5)
        for z in range(-_r(6 * u + 2, 4), 1):
            for y in range(0, int(top * (1 + z * 0.02)) + 1):
                w.setze(x, y, z, k.stein(0.3 + 4 * y / H + w.rng.random() * 0.5, x, y, z))
    bw = _r(2.5 * u + 1, 2)
    for x in range(-bw, bw + 1):
        h = int(H * (1 - (abs(x) / W) ** 2))
        for y in range(1, h + 1):
            for z in (1, 2 if abs(x) < bw - 1 and y < h * 0.7 else 1):
                w.setze(x, y, z, k.e(x, y, z, 0.3 + (x * 7 + y) % 3 * 0.5))
    for x, z in scheibe(bw + 3, 0, bw + 4):
        w.setze(x, 0, z, w.b("ice") if w.rng.random() < 0.7 else w.b("packed_ice"))
    return w


def nordhuette(seed, g=1):
    """Verschneite Fichtenhütte mit Schneedach, Rauch, Brennholzstapel, Schlitten und Laterne."""
    w = _welt(seed)
    from bau import Stil, kasten_haus, satteldach
    u = U[g]
    st = Stil(w, Verlauf(w, "Fichte", ["spruce_log"]), holz="spruce", dach="spruce", sockel="cobblestone",
              fachwerk=False)
    bx, bz = [5, 7, 9, 12][g], [4, 6, 7, 9][g]
    _schnee(w, max(bx, bz) + 4)
    x0, z0 = -bx // 2, -bz // 2
    yt, a, b, c, d = kasten_haus(w, st, x0, z0, x0 + bx, z0 + bz, 0, 1 + (g >= 3), eh=4, blumen=False)
    satteldach(w, st, a, b, c, d, yt)
    for (x, y, z), blk in list(w.bloecke.items()):
        if w.P.name(blk) == "minecraft:spruce_stairs" and w.frei(x, y + 1, z):
            w.setze(x, y + 1, z, w.b("snow", layers=2))
    for y in range(1, yt + 5):
        w.setze(c + 1, y, b + 1, w.b("cobblestone"))
    w.setze(c + 1, yt + 5, b + 1, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for kk in range(3):
        for y in range(1, 3):
            w.setze(a - 2, y, b + kk, w.b("spruce_log", axis="x"))
    laterne_pos = (a - 1, 1, d + 2)
    w.setze(*laterne_pos, w.b("lantern", hanging=False, waterlogged=False))
    return w


def riesenschneemann(seed, g=2):
    """Riesiger Schneemann mit Kohleaugen, Karottennase, Schal, Zylinder und Ast-Armen."""
    w = _welt(seed)
    k = Eis(w, seed)
    u = U[g]
    _schnee(w, 6 * u + 4)
    S = Skulptur(w, u)
    S.mat("s", lambda x, y, z, *_: w.b("snow_block") if (x + y + z) % 6 else w.b("powder_snow") if False else w.b("white_concrete"))
    S.mat("k", w.b("coal_block"))
    S.mat("n", w.b("orange_concrete"))
    S.mat("sch", lambda x, y, z, *_: w.b("red_wool") if (y // 1) % 2 else w.b("white_wool"))
    S.mat("hut", w.b("black_wool"))
    S.mat("ast", w.b("dark_oak_log", axis="y"))
    S.plus(ell(0, 4, 0, 4.5, 4.2, 4.5), "s")
    S.plus(ell(0, 10.5, 0, 3.4, 3.1, 3.4), "s")
    S.plus(ell(0, 15.5, 0, 2.5, 2.4, 2.5), "s")
    S.plus(lambda X, Y, Z: (Y > 12.8) & (Y < 14) & (X * X + Z * Z <= 2.9 ** 2), "sch")
    S.plus(kap((2.2, 13.2, 1.6), (3.2, 10.5, 2.5), 0.55), "sch")
    for x in (-0.9, 0.9):
        S.plus(ell(x, 16.2, 2.2, 0.45, 0.45, 0.45), "k")
    S.plus(kap((0, 15.5, 2.3), (0, 15.2, 4.6), 0.45, 0.15), "n")
    for y in (8.5, 10.5, 12.0):
        S.plus(ell(0, y, 3.2, 0.45, 0.45, 0.45), "k")
    S.plus(lambda X, Y, Z: (Y > 17.4) & (Y < 18.2) & (X * X + Z * Z <= 3.2 ** 2), "hut")
    S.plus(lambda X, Y, Z: (Y >= 18.2) & (Y < 21) & (X * X + Z * Z <= 1.9 ** 2), "hut")
    for s in (-1, 1):
        S.plus(kap((s * 3, 11, 0), (s * 6.5, 14, 0.5), 0.35), "ast")
        S.plus(kap((s * 5.5, 13, 0.4), (s * 6.4, 14.6, -0.6), 0.25), "ast")
    S.rendern((-8, 0, -6), (8, 22, 6), versatz=(0.5, 1, 0.5))
    return w


def eiswachturm(seed, g=1):
    """Wachturm aus Frostgestein mit Eisspitze, Schneehaube und Leuchtfeuer."""
    w = _welt(seed)
    k = Eis(w, seed)
    u = U[g]
    R = 2.4 * u + 1.2
    H = _r(13 * u + 5, 8)
    _schnee(w, R + 6)
    for y in range(0, H):
        for x, z in kreisrand(R):
            fen = y % 5 == 3 and (x == 0 or z == 0)
            w.setze(x, y, z, w.b("light_blue_stained_glass") if fen else k.stein(0.4 + 3 * y / H + w.rng.random() * 0.4,
                                                                                x, y, z))
    for x, z in kreisrand(R + 1):
        w.setze(x, H, z, treppe(w, "stone_brick", zur_mitte(x, z), "top"))
    for x, z in scheibe(R + 1):
        w.setze(x, H + 1, z, w.b("snow_block"))
    for kk in range(_r(R * 3, 4)):
        for x, z in scheibe(max(0.3, (R + 0.5) * (1 - kk / (R * 3))), 0, 0):
            w.setze(x, H + 2 + kk, z, k.e(x, H + kk, z, 0.5 + kk * 0.2))
    w.setze(0, H + 2, int(R) + 1, k.licht)
    return w


EISREICH = {
    "eispalast": ("Eispalast", eispalast),
    "iglu_dorf": ("Iglu-Dorf", iglu_dorf),
    "gletschertor": ("Gletschertor", gletschertor),
    "eiskristall": ("Eiskristall", eiskristall),
    "gefrorener_wasserfall": ("Gefrorener Wasserfall", gefrorener_wasserfall),
    "nordhuette": ("Nordhütte", nordhuette),
    "riesenschneemann": ("Riesenschneemann", riesenschneemann),
    "eiswachturm": ("Eiswachturm", eiswachturm),
}

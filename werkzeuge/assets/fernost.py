"""Fernost – Paket: Pagode, Torbogen (einzeln und als Torweg), Teehaus mit Teich, Zen-Garten, Bogenbrücke,
Burg auf Steinsockel, Steinlaterne und Kirschblütenhain. Geschwungene Dächer mit hochgezogenen Ecken.
Stil 1 Rot/Weiß mit dunklen Ziegeln, Stil 2 dunkles Holz mit Patina-Kupferdächern."""

from __future__ import annotations

import math

from lib import Verlauf, Welt, laub
from skulptur import Skulptur, ell, kap, kreisrand, platte, scheibe, treppe, verbinde

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


class Ost:
    def __init__(self, w, seed):
        self.w = w
        b = w.b
        self.patina = _stil(seed) == 1
        if not self.patina:
            self.saeule = b("red_terracotta")
            self.balken = "dark_oak"
            self.wand = Verlauf(w, "Papier", ["white_terracotta", "white_concrete", "smooth_quartz"])
            self.dach_tr = "deepslate_tile"
            self.dach_voll = "deepslate_tiles"
            self.tor = b("red_concrete")
            self.gold = b("gold_block")
        else:
            self.saeule = b("dark_oak_log", axis="y")
            self.balken = "spruce"
            self.wand = Verlauf(w, "Papier", ["birch_planks", "white_terracotta", "calcite"])
            self.dach_tr = "waxed_oxidized_cut_copper"
            self.dach_voll = "waxed_oxidized_copper"
            self.tor = b("red_terracotta")
            self.gold = b("gold_block")


def _boden(w, r, cx=0, cz=0, blk="grass_block"):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, w.b(blk, snowy=False) if blk == "grass_block" else w.b(blk), ueberschreiben=False)


def geschwungenes_dach(w, o, x0, z0, x1, z1, y, ue=2):
    """Walmdach mit weitem Überstand und hochgezogenen Ecken. Gibt die Firsthöhe zurück."""
    k = 0
    while True:
        ax, bx, az, bz = x0 - ue + k, x1 + ue - k, z0 - ue + k, z1 + ue - k
        if ax > bx or az > bz:
            break
        yy = y + k
        for x in range(ax, bx + 1):
            for z in range(az, bz + 1):
                if not (x in (ax, bx) or z in (az, bz)):
                    continue
                if ax == bx or az == bz:
                    w.setze(x, yy, z, w.b(o.dach_voll))
                elif z == az:
                    w.setze(x, yy, z, treppe(w, o.dach_tr, "south"))
                elif z == bz:
                    w.setze(x, yy, z, treppe(w, o.dach_tr, "north"))
                elif x == ax:
                    w.setze(x, yy, z, treppe(w, o.dach_tr, "east"))
                else:
                    w.setze(x, yy, z, treppe(w, o.dach_tr, "west"))
        if k == 0:
            for cx in (ax, bx):
                for cz in (az, bz):
                    w.setze(cx, yy, cz, w.b(o.dach_voll))
                    w.setze(cx, yy + 1, cz, treppe(w, o.dach_tr, "south" if cz == az else "north", "top"))
            for x in range(ax + 1, bx):
                for cz in (az + 1, bz - 1):
                    w.setze(x, yy - 1, cz, treppe(w, o.balken, "south" if cz == az + 1 else "north", "top"),
                            ueberschreiben=False)
        k += 1
    return y + k


def stockwerk(w, o, x0, z0, x1, z1, y0, h, veranda=True):
    """Ein Geschoss: rote Säulen, helle Wände mit Holzgitter, Fenster, umlaufende Veranda mit Geländer."""
    for y in range(y0, y0 + h):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                rx, rz = x in (x0, x1), z in (z0, z1)
                if not (rx or rz):
                    continue
                t = (x - x0) if rz else (z - z0)
                if (rx and rz) or t % 3 == 0:
                    w.setze(x, y, z, o.saeule)
                elif y == y0 + h - 1:
                    w.setze(x, y, z, w.b(f"stripped_{o.balken}_log", axis="x" if rz else "z"))
                elif (y - y0) == h // 2 and t % 3 == 1:
                    w.setze(x, y, z, w.b("glass_pane", east=rz, west=rz, north=rx, south=rx, waterlogged=False))
                else:
                    w.setze(x, y, z, o.wand(1 + w.rng.random() * 1.5, x, y, z))
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            w.setze(x, y0 - 1, z, w.b(f"{o.balken}_planks"))
    if veranda:
        pos = []
        for x in range(x0 - 1, x1 + 2):
            for z in range(z0 - 1, z1 + 2):
                if x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1):
                    w.setze(x, y0 - 1, z, w.b(f"{o.balken}_planks"))
                    pos.append((x, y0, z))
        verbinde(w, pos, f"{o.balken}_fence")


def steinlaterne_bau(w, x, z, y=1, gross=1):
    w.setze(x, y, z, w.b("stone_bricks"))
    w.setze(x, y + 1, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                             waterlogged=False))
    w.setze(x, y + 2, z, w.b("lantern", hanging=False, waterlogged=False) if gross == 1 else w.b("sea_lantern"))
    w.setze(x, y + 3, z, w.b("stone_brick_slab", type="bottom", waterlogged=False))


def _kirschbaum(w, x, z, u):
    h = _r(3 * u + 2, 3)
    for y in range(1, h + 1):
        w.setze(x + (y > h * 0.6), y, z, w.b("cherry_log", axis="y"))
    S = Skulptur(w, max(0.8, u))
    bl = [laub(w, "cherry"), laub(w, "cherry"), laub(w, "flowering_azalea")]
    S.mat("l", lambda *a: bl[int(w.rng.integers(3))])
    S.plus(lambda X, Y, Z: (X / 3.0) ** 2 + (Y / 1.7) ** 2 + (Z / 3.0) ** 2 <= 1, "l")
    S.rendern((-4, -2, -4), (4, 2, 4), versatz=(x + 1.5, h + 1.3, z + 0.5), ueberschreiben=False)
    for xx, zz in scheibe(3 * u + 1, x, z):
        if w.frei(xx, 1, zz) and w.rng.random() < 0.3:
            w.setze(xx, 1, zz, w.b("pink_petals", facing="north", flower_amount=4), ueberschreiben=False)


# ============================================================================ Typen

def pagode(seed, g=2):
    """Mehrstöckige Pagode mit Veranden, geschwungenen Dächern und goldener Spitze mit Ringen."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    stock = [3, 5, 7, 9][g]
    h0 = _r(3.5 * u + 2, 3)
    eh = _r(2.5 * u + 2, 3)
    _boden(w, h0 + 8)
    for x in range(-h0 - 3, h0 + 4):
        for z in range(-h0 - 3, h0 + 4):
            w.setze(x, 0, z, w.b("stone_bricks"))
    y = 2
    for s in range(stock):
        hh = max(1, h0 - s * max(1, h0 // (stock + 1)))
        stockwerk(w, o, -hh, -hh, hh, hh, y, eh, veranda=s > 0 or True)
        y = geschwungenes_dach(w, o, -hh, -hh, hh, hh, y + eh, ue=2 if s == 0 else 1 + (u > 1.5)) - max(1, hh - 1)
        y = max(y, 0)
        y = y + 1
    top = max(p[1] for p in w.bloecke)
    for k in range(_r(4 * u + 2, 3)):
        w.setze(0, top + 1 + k, 0, o.gold if k % 2 == 0 else w.b("chain", axis="y", waterlogged=False))
    w.setze(0, top + 2 + _r(4 * u + 2, 3), 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for s in (-1, 1):
        steinlaterne_bau(w, s * (h0 + 2), h0 + 4, y=0)
    return w


def torbogen(seed, g=1):
    """Tor aus zwei Säulen mit geschwungenem Oberbalken. Größere Varianten als Torweg hintereinander."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    anzahl = [1, 1, 5, 9][g]
    H = _r(6 * u + 3, 5)
    b = _r(3 * u + 1, 2)
    abst = _r(2.5 * u + 2, 3)
    _boden(w, max(b + 4, anzahl * abst // 2 + 4))
    for i in range(anzahl):
        z = (i - anzahl // 2) * abst
        for s in (-1, 1):
            for y in range(1, H + 1):
                w.setze(s * b, y, z, o.tor)
            w.setze(s * b, 0, z, w.b("stone_bricks"))
        for x in range(-b - 2, b + 3):
            w.setze(x, H - 1, z, o.tor)
            schwung = 1 if abs(x) >= b + 1 else 0
            w.setze(x, H + 1 + schwung, z, w.b("black_concrete") if not o.patina else w.b(o.dach_voll))
            w.setze(x, H + 2 + schwung, z, w.b("black_concrete") if (abs(x) > b + 1 and not o.patina) else
                    (w.b(o.dach_voll) if abs(x) > b + 1 else w.b("air")), ueberschreiben=abs(x) > b + 1)
        w.setze(0, H, z, o.tor)
        for x in range(-b, b + 1):
            w.setze(x, H + 1, z, o.tor)
    w.bloecke = {p: v for p, v in w.bloecke.items() if v != 0}
    for z in range(-(anzahl // 2) * abst - 2, (anzahl // 2) * abst + 3):
        for x in (-1, 0, 1):
            w.setze(x, 0, z, w.b("gravel"))
    return w


def teehaus(seed, g=1):
    """Teehaus auf Stelzen am Teich: Schiebewände, Veranda, geschwungenes Dach, Trittsteine, Laternen."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    bx, bz = _r(3.5 * u + 2, 3), _r(2.5 * u + 2, 2)
    _boden(w, bx + 10)
    for x, z in scheibe(bx * 0.9 + 2, bx + 5, 0):
        w.setze(x, 0, z, w.b("water", level=0))
        if w.rng.random() < 0.08:
            w.setze(x, 1, z, w.b("lily_pad"))
    for x in range(-bx - 1, bx + 2, 2):
        for z in (-bz - 1, bz + 1):
            w.setze(x, 1, z, o.saeule)
    stockwerk(w, o, -bx, -bz, bx, bz, 3, _r(2.5 * u + 2, 3))
    geschwungenes_dach(w, o, -bx, -bz, bx, bz, 3 + _r(2.5 * u + 2, 3), ue=2)
    for k in range(4):
        w.setze(-1 + (k % 2), 0, bz + 2 + k, w.b("smooth_stone"))
    steinlaterne_bau(w, -bx - 3, bz + 3)
    steinlaterne_bau(w, bx + 2, -bz - 3)
    _kirschbaum(w, -bx - 5, -bz - 2, u * 0.8)
    return w


def zengarten(seed, g=1):
    """Zen-Garten: geharkter Kies in Wellenringen um Felsen, Mooshügel, Bonsai-Kiefern, Steinlaternen,
    Bambuszaun und Holzsteg."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(9 * u + 4, 6)
    for x in range(-R - 1, R + 2):
        for z in range(-R - 1, R + 2):
            w.setze(x, 0, z, w.b("gravel"))
    felsen = []
    for i in range(2 + g):
        a = i * 2.3 + 0.7
        d = R * (0.2 + 0.5 * ((i * 7) % 5) / 5)
        felsen.append((round(math.cos(a) * d), round(math.sin(a) * d), 1.0 + 0.6 * u * ((i % 3) + 1) / 2))
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            dmin = min(math.hypot(x - fx, z - fz) - fr for fx, fz, fr in felsen)
            if 0 < dmin and int(dmin) % 2 == 0:
                w.setze(x, 0, z, w.b("sand"))
    S = Skulptur(w, 1.0)
    S.mat("f", lambda x, y, z, *_: w.b("mossy_cobblestone") if y >= 2 and w.rng.random() < 0.4 else
          w.b(["andesite", "stone", "tuff"][(x + z) % 3]))
    for fx, fz, fr in felsen:
        S.plus(ell(fx, 0.5, fz, fr, fr * 1.2, fr * 0.9), "f")
    S.rendern((-R, 0, -R), (R, 6 * u + 2, R), versatz=(0.5, 0.5, 0.5))
    for x, z in scheibe(2.5 * u, -R + 3, R - 3):
        w.setze(x, 0, z, w.b("moss_block"))
        w.setze(x, 1, z, w.b("moss_carpet"), ueberschreiben=False)
    for (bx, bz) in ((R - 3, -R + 3), (-R + 3, R - 3)):
        for y in range(1, _r(2 * u + 2, 2)):
            w.setze(bx, y, bz, w.b("spruce_log", axis="y"))
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1)):
            w.setze(bx + dx * 2, _r(2 * u + 2, 2), bz + dz, laub(w, "spruce"))
            w.setze(bx + dx, _r(2 * u + 2, 2) + 1, bz + dz, laub(w, "spruce"))
    steinlaterne_bau(w, R - 2, R - 2)
    verbinde(w, [(x, 1, z) for x in range(-R - 1, R + 2) for z in (-R - 1, R + 1)] +
             [(x, 1, z) for x in (-R - 1, R + 1) for z in range(-R, R + 1)], "bamboo_fence")
    for z in range(-R - 1, R + 2):
        w.setze(R + 2, 0, z, w.b(f"{o.balken}_slab", type="top", waterlogged=False))
    return w


def bogenbruecke(seed, g=1):
    """Rote Bogenbrücke über einen Teich mit Seerosen, Laternen an beiden Enden und Schilf."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    L = _r(8 * u + 4, 6)
    B = _r(1.2 * u + 0.6, 1)
    _boden(w, L + 6)
    for x, z in scheibe(L * 0.8 + 1):
        if abs(x) < L - 1:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("dirt"))
            if w.rng.random() < 0.06:
                w.setze(x, 1, z, w.b("lily_pad"))
    for x in range(-L, L + 1):
        y = int(round((1 - (x / L) ** 2) * (2.5 * u + 1)))
        for z in range(-B, B + 1):
            w.setze(x, y, z, w.b(f"{o.balken}_planks"))
        for s in (-1, 1):
            w.setze(x, y + 1, s * (B + 1), o.tor if x % 3 == 0 else w.b(f"{o.balken}_fence", north=False,
                                                                           south=False, east=True, west=True,
                                                                           waterlogged=False))
            w.setze(x, y, s * (B + 1), o.tor)
    for s in (-1, 1):
        steinlaterne_bau(w, s * (L + 1), B + 2)
    return w


def ostburg(seed, g=2):
    """Burg auf geböschtem Steinsockel: weißer Hauptturm mit mehreren geschwungenen Dachgeschossen,
    Giebeln und goldenen Firstfiguren."""
    w = _welt(seed)
    o = Ost(w, seed)
    o.wand = Verlauf(w, "Weiß", ["white_concrete", "calcite", "smooth_quartz"])
    u = U[g]
    h = _r(5 * u + 3, 4)
    Hs = _r(4 * u + 2, 3)
    _boden(w, h + 10)
    for y in range(0, Hs + 1):
        hh = h + 2 + (Hs - y) // 2
        for x in range(-hh, hh + 1):
            for z in range(-hh, hh + 1):
                if max(abs(x), abs(z)) >= hh - 1 or y == Hs:
                    w.setze(x, y, z, w.b(["cobblestone", "stone", "andesite", "mossy_cobblestone"]
                                         [(x * 3 + y + z * 5) % 4]))
    y = Hs + 1
    stock = [2, 3, 4, 5][g]
    for s in range(stock):
        hh = max(2, h - s)
        eh = _r(2.4 * u + 2, 3)
        stockwerk(w, o, -hh, -hh, hh, hh, y, eh, veranda=False)
        y = geschwungenes_dach(w, o, -hh, -hh, hh, hh, y + eh, ue=1 + (u > 1.5)) - max(1, hh - 1) + 1
    top = max(p[1] for p in w.bloecke)
    for s in (-1, 1):
        w.setze(s * 1, top + 1, 0, o.gold)
    for k in range(Hs + 2):
        for x in range(-1, 2):
            w.setze(x, k, h + 2 + Hs // 2 + 1 + (Hs + 1 - k) - 1, treppe(w, "stone_brick", "north"))
    return w


def steinlaterne(seed, g=1):
    """Große Steinlaterne mit breitem Dachstein, Lichtkammer und Sockel – auch als Wegbeleuchtung."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    S.mat("s", lambda x, y, z, *_: w.b(["stone", "andesite", "stone_bricks", "mossy_stone_bricks"][(x + y + z) % 4]))
    S.mat("l", w.b("shroomlight"))
    S.plus(lambda X, Y, Z: (Y >= 0) & (Y <= 1) & (abs_(X) <= 2) & (abs_(Z) <= 2), "s")
    S.plus(lambda X, Y, Z: (Y > 1) & (Y <= 4) & (X * X + Z * Z <= 0.8), "s")
    S.plus(lambda X, Y, Z: (Y > 4) & (Y <= 5) & (abs_(X) <= 1.6) & (abs_(Z) <= 1.6), "s")
    S.plus(lambda X, Y, Z: (Y > 5) & (Y <= 7) & (abs_(X) <= 1.2) & (abs_(Z) <= 1.2), "l")
    S.plus(lambda X, Y, Z: (Y > 7) & (Y <= 8.4) & (abs_(X) + abs_(Z) <= 3.6 - (Y - 7) * 1.6), "s")
    S.plus(ell(0, 9, 0, 0.6, 0.6, 0.6), "s")
    S.rendern((-4, 0, -4), (4, 10, 4), versatz=(0.5, 1, 0.5))
    _boden(w, 4 * u + 2, blk="moss_block")
    return w


def abs_(a):
    import numpy as np
    return np.abs(a)


def kirschhain(seed, g=1):
    """Kirschblütenhain mit Steinweg, Bank und Laterne."""
    w = _welt(seed)
    u = U[g]
    R = _r(10 * u + 5, 7)
    _boden(w, R + 2)
    for i in range(3 + 3 * g):
        a = i * 2.39996
        d = R * math.sqrt((i + 0.5) / (3 + 3 * g)) * 0.85
        _kirschbaum(w, round(math.cos(a) * d), round(math.sin(a) * d), u * 0.85)
    for z in range(-R, R + 1):
        if w.frei(0, 1, z):
            w.setze(0, 0, z, w.b("smooth_stone" if z % 2 else "gravel"))
    steinlaterne_bau(w, 2, 0)
    return w


FERNOST = {
    "pagode": ("Pagode", pagode),
    "torbogen": ("Torbogen / Torweg", torbogen),
    "teehaus": ("Teehaus am Teich", teehaus),
    "zengarten": ("Zen-Garten", zengarten),
    "bogenbruecke": ("Bogenbrücke", bogenbruecke),
    "ostburg": ("Burg auf Steinsockel", ostburg),
    "steinlaterne": ("Steinlaterne", steinlaterne),
    "kirschhain": ("Kirschblütenhain", kirschhain),
}

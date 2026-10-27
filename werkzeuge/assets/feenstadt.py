"""Feenstadt – Paket: Pilzhäuser, Blütentürme, Feenringe, Laternenbaum, Schneckenhaus, Wurzelbrücke,
Kristallblüte und eine ganze Feenstadt. Stil 1 Frühlingsfeen (rosa/weiß/grün), Stil 2 Mondfeen (violett/blau,
leuchtend)."""

from __future__ import annotations

import math

import numpy as np

from lib import Verlauf, Welt, einfuegen, laub, ueberwuchern
from skulptur import Skulptur, dreh_y, ell, kap, kasten, kegel, kreisrand, platte, scheibe, spiegel_x, torus, und

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


class Feen:
    def __init__(self, w, seed):
        self.w = w
        self.mond = _stil(seed) == 1
        if not self.mond:
            self.hut = [w.b("red_mushroom_block"), w.b("red_concrete"), w.b("red_terracotta")]
            self.punkt = w.b("white_concrete")
            self.blueten = [w.b("pink_wool"), w.b("pink_concrete"), w.b("white_wool"), w.b("magenta_wool")]
            self.blatt = [laub(w, "cherry"), laub(w, "flowering_azalea"), laub(w, "azalea")]
            self.licht = w.b("ochre_froglight")
            self.glas = w.b("yellow_stained_glass")
            self.kristall = [w.b("pink_stained_glass"), w.b("magenta_stained_glass"), w.b("white_stained_glass")]
            self.boden = [w.b("moss_block"), w.b("grass_block", snowy=False), w.b("moss_block")]
        else:
            self.hut = [w.b("purple_concrete"), w.b("blue_concrete"), w.b("purple_terracotta")]
            self.punkt = w.b("light_blue_concrete")
            self.blueten = [w.b("purple_wool"), w.b("light_blue_wool"), w.b("blue_wool"), w.b("magenta_wool")]
            self.blatt = [laub(w, "azalea"), laub(w, "dark_oak"), laub(w, "flowering_azalea")]
            self.licht = w.b("pearlescent_froglight")
            self.glas = w.b("light_blue_stained_glass")
            self.kristall = [w.b("purple_stained_glass"), w.b("light_blue_stained_glass"), w.b("blue_stained_glass")]
            self.boden = [w.b("moss_block"), w.b("mycelium" if False else "moss_block"), w.b("warped_nylium")]
        self.stiel = w.b("mushroom_stem")

    def bodenblock(self):
        return self.boden[int(self.w.rng.integers(len(self.boden)))]


def _boden(w, f, r, cx=0, cz=0):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, f.bodenblock(), ueberschreiben=False)


def _streu(w, f, r, dichte=0.12, cx=0, cz=0):
    """Leuchtpilze, Blumen und Glühwürmchen-Laternen am Boden."""
    for x, z in scheibe(r, cx, cz):
        if w.frei(x, 1, z) and w.rng.random() < dichte:
            k = w.rng.random()
            if k < 0.35:
                w.setze(x, 1, z, w.b("red_mushroom" if not f.mond else "brown_mushroom"))
            elif k < 0.7:
                w.setze(x, 1, z, w.b(["allium", "azure_bluet", "pink_tulip", "lily_of_the_valley", "cornflower"]
                                     [int(w.rng.integers(5))]))
            elif k < 0.85:
                w.setze(x, 1, z, w.b("small_amethyst_bud", facing="up", waterlogged=False) if f.mond
                        else w.b("pink_petals", facing="north", flower_amount=4))
            else:
                w.setze(x, 1, z, w.b("lantern" if not f.mond else "soul_lantern", hanging=False, waterlogged=False))


# ============================================================================ Teile

def pilzhaus(w, f, cx, cz, u, hoehe=1.0):
    """Fliegenpilz-Haus: Stiel mit Tür und runden Fenstern, getupfter Hut, Kamin, Laternen."""
    H = 9 * u * hoehe + 3
    Rs = 2.2 * u + 1
    Rh = 5 * u + 2
    S = Skulptur(w, 1.0)
    S.mat("s", f.stiel)
    S.mat("g", f.glas)

    def hutmat(x, y, z, lx, ly, lz):
        if (x * 7 + z * 13 + y * 5) % 11 == 0:
            return f.punkt
        return f.hut[(x + y + z) % 3]
    S.mat("h", hutmat)
    S.plus(kegel(cx, cz, 0, H, Rs * 1.15, Rs * 0.9), "s")
    S.minus(kegel(cx, cz, 1, H - 1, Rs * 1.15 - 1.2, Rs * 0.9 - 1.2))
    S.plus(lambda X, Y, Z: (((X - cx) ** 2 + (Z - cz) ** 2) / Rh ** 2 + ((Y - H) / (Rh * 0.62)) ** 2 <= 1)
           & (Y >= H - 1 - 0.5 * np.sin(np.arctan2(Z - cz, X - cx) * 6)), "h")
    for a in (0.5, 2.3, 4.0):
        x, z = cx + math.cos(a) * (Rs * 1.05), cz + math.sin(a) * (Rs * 1.05)
        S.plus(ell(x, H * 0.55, z, 0.6, 0.6, 0.6), "g")
    S.rendern((cx - Rh - 2, -1, cz - Rh - 2), (cx + Rh + 2, H + Rh, cz + Rh + 2))
    zt = cz + int(Rs * 1.1)
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(cx, y, zt, w.b("spruce_door", facing="south", half=half, hinge="left", open=False, powered=False))
    for s in (-1, 1):
        w.setze(cx + s * 2, 1, zt + 1, w.b("lantern" if not f.mond else "soul_lantern", hanging=False,
                                           waterlogged=False))
    kx, kz = cx + int(Rh * 0.4), cz - int(Rh * 0.3)
    top = max([p[1] for p in w.bloecke if p[0] == kx and p[2] == kz] + [int(H)])
    for y in range(top + 1, top + 1 + _r(2 * u, 2)):
        w.setze(kx, y, kz, w.b("bricks" if not f.mond else "deepslate_bricks"))
    w.setze(kx, top + 1 + _r(2 * u, 2), kz, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                 waterlogged=False))


def bluetenturm(w, f, cx, cz, u):
    """Riesenblume: geschwungener Stängel mit Blättern, Blütenkelch mit Glaskuppel-Häuschen, leuchtende Pollen."""
    H = 14 * u + 4
    S = Skulptur(w, 1.0)
    S.mat("g", w.b("lime_terracotta" if not f.mond else "green_terracotta"))
    S.mat("b", lambda x, y, z, *_: f.blueten[(x * 3 + z * 5 + y) % len(f.blueten)])
    S.mat("k", f.glas)
    S.mat("l", f.licht)
    S.mat("a", lambda x, y, z, *_: f.blatt[(x + z) % len(f.blatt)])
    pts = [(cx, 0, cz), (cx + 1.5 * u, H * 0.4, cz), (cx - 0.5 * u, H * 0.75, cz + 0.5 * u), (cx, H, cz)]
    for a, b in zip(pts, pts[1:]):
        S.plus(kap(a, b, 1.1 * u + 0.4, 0.9 * u + 0.4), "g")
    for k, (yy, a) in enumerate(((H * 0.3, 0.4), (H * 0.55, 2.6))):
        S.plus(ell(cx + math.cos(a) * 3 * u, yy + 0.8 * u, cz + math.sin(a) * 3 * u, 3.2 * u + 0.5, 0.6 + 0.3 * u,
                   1.6 * u + 0.5), "a")
    Rb = 6 * u + 2.5
    for i in range(7):
        a = i * 2 * math.pi / 7
        S.plus(lambda X, Y, Z, a=a: (((X - cx - math.cos(a) * Rb * 0.55) / (Rb * 0.6)) ** 2
                                     + ((Z - cz - math.sin(a) * Rb * 0.55) / (Rb * 0.32)) ** 2 <= 1)
               & (np.abs(Y - H - 0.5 - 0.35 * np.sqrt((X - cx) ** 2 + (Z - cz) ** 2)) <= 0.7), "b")
    S.plus(lambda X, Y, Z: (((X - cx) ** 2 + (Z - cz) ** 2) <= (2.6 * u + 1) ** 2) & (np.abs(Y - H) <= 0.6), "g")
    S.plus(lambda X, Y, Z: (((X - cx) ** 2 + (Z - cz) ** 2 + (Y - H) ** 2) <= (2.4 * u + 1) ** 2)
           & (((X - cx) ** 2 + (Z - cz) ** 2 + (Y - H) ** 2) > (2.4 * u) ** 2) & (Y > H), "k")
    for i in range(5):
        a = i * 1.3
        S.plus(kap((cx, H, cz), (cx + math.cos(a) * 1.5 * u, H + 2 * u + 1.2, cz + math.sin(a) * 1.5 * u), 0.3, 0.2),
               "g")
        S.plus(ell(cx + math.cos(a) * 1.5 * u, H + 2 * u + 1.6, cz + math.sin(a) * 1.5 * u, 0.5, 0.5, 0.5), "l")
    S.rendern((cx - Rb - 3, -1, cz - Rb - 3), (cx + Rb + 3, H + 6 * u + 3, cz + Rb + 3))


def feenring(w, f, cx, cz, u):
    """Kreis aus Leuchtpilzen um eine Moosfläche, in der Mitte ein Kristall auf einem Wurzelsockel,
    schwebende Lichter darüber."""
    R = 6 * u + 3
    for x, z in scheibe(R + 1, cx, cz):
        w.setze(x, 0, z, w.b("moss_block"))
    for i, (x, z) in enumerate(kreisrand(R, cx, cz)):
        if i % 2 == 0:
            hh = 1 + (i % 3)
            for y in range(1, hh + 1):
                w.setze(x, y, z, f.stiel)
            w.setze(x, hh + 1, z, f.licht if i % 4 == 0 else f.hut[i % 3])
    S = Skulptur(w, u)
    S.mat("w", w.b("mangrove_roots" if not f.mond else "dark_oak_wood" if False else "mangrove_roots"))
    S.mat("k", lambda x, y, z, *_: f.kristall[(x + y + z) % 3])
    S.mat("l", f.licht)
    for i in range(5):
        a = i * 2 * math.pi / 5
        S.plus(kap((math.cos(a) * 2.2, 0, math.sin(a) * 2.2), (0, 2.4, 0), 0.6, 0.4), "w")
    S.plus(lambda X, Y, Z: np.abs(X) + np.abs(Z) + np.abs(Y - 5.2) * 0.45 <= 1.6, "k")
    S.plus(lambda X, Y, Z: np.abs(X) + np.abs(Z) + np.abs(Y - 5.2) * 0.45 <= 0.8, "l")
    S.rendern((-4, -1, -4), (4, 9, 4), versatz=(cx + 0.5, 1, cz + 0.5))
    for i in range(6):
        a = i * 1.05
        w.setze(cx + round(math.cos(a) * R * 0.6), _r(5 * u + 3), cz + round(math.sin(a) * R * 0.6),
                w.b("end_rod", facing="up"))


def laternenbaum(w, f, cx, cz, u):
    """Verdrehter Baum mit Hängelaternen, kleinen Vogelhaus-Wohnungen auf den Ästen und Blütenkrone."""
    H = 13 * u + 4
    S = Skulptur(w, 1.0)
    S.mat("r", Verlauf(w, "Rinde", ["dark_oak_log", "spruce_log", "stripped_spruce_log"]) if not f.mond else
          Verlauf(w, "Rinde", ["mangrove_log", "dark_oak_log", "stripped_mangrove_log"]), basis=1, rausch=1.5)
    S.mat("l", lambda x, y, z, *_: f.blatt[int(w.rng.integers(len(f.blatt)))] if w.rng.random() > 0.04 else f.licht)
    for k in range(3):
        a = k * 2.1
        pts = [(cx + math.cos(a) * 1.2 * u, 0, cz + math.sin(a) * 1.2 * u)]
        for t in np.linspace(0.2, 1, 5):
            pts.append((cx + math.cos(a + t * 2.5) * 1.2 * u * (1 - t * 0.6), H * t * 0.75,
                        cz + math.sin(a + t * 2.5) * 1.2 * u * (1 - t * 0.6)))
        for p0, p1 in zip(pts, pts[1:]):
            S.plus(kap(p0, p1, 1.0 * u + 0.4, 0.8 * u + 0.4), "r")
    enden = []
    for i in range(5):
        a = i * 2 * math.pi / 5 + 0.4
        e = (cx + math.cos(a) * 6.5 * u, H * 0.85 + (i % 2) * u, cz + math.sin(a) * 6.5 * u)
        S.plus(kap((cx, H * 0.7, cz), e, 0.7 * u + 0.3, 0.35 * u + 0.3), "r")
        enden.append(e)
    for e in enden + [(cx, H, cz)]:
        S.plus(ell(e[0], e[1] + 1.2 * u, e[2], 3.6 * u + 0.8, 2.2 * u + 0.6, 3.6 * u + 0.8), "l")
    S.rendern((cx - 12 * u - 4, -1, cz - 12 * u - 4), (cx + 12 * u + 4, H + 5 * u + 3, cz + 12 * u + 4))
    for i, e in enumerate(enden):
        x, z = round(e[0] * 0.7 + cx * 0.3), round(e[2] * 0.7 + cz * 0.3)
        unten = [p[1] for p in w.bloecke if p[0] == x and p[2] == z and p[1] > H * 0.5]
        if unten:
            y = min(unten) - 1
            for k in range(1 + i % 3):
                w.setze(x, y - k, z, w.b("chain", axis="y", waterlogged=False))
            w.setze(x, y - 1 - i % 3, z, w.b("lantern" if not f.mond else "soul_lantern", hanging=True,
                                             waterlogged=False))


def schneckenhaus(w, f, cx, cz, u):
    """Riesiges Schneckenhaus als Wohnhaus: Spiralgehäuse mit Fenstern, Tür im Mündungsbereich, Moosdach."""
    S = Skulptur(w, u)
    farben = [w.b("orange_terracotta"), w.b("white_terracotta"), w.b("brown_terracotta")] if not f.mond else \
        [w.b("purple_terracotta"), w.b("light_blue_terracotta"), w.b("blue_terracotta")]

    def schale(x, y, z, lx, ly, lz):
        a = math.atan2(ly - 5, lx)
        r = math.hypot(lx, ly - 5)
        return farben[int((a / (2 * math.pi) * 3 + r * 0.35) * 2) % 3]
    S.mat("s", schale)
    S.mat("g", f.glas)
    S.mat("m", w.b("moss_block"))

    def spirale(X, Y, Z):
        a = np.arctan2(Y - 5, X)
        r = np.sqrt(X * X + (Y - 5) ** 2)
        t = (a + math.pi) / (2 * math.pi)
        best = np.zeros_like(X, dtype=bool)
        for umlauf in range(3):
            rr = 5.2 * np.exp(-0.35 * (umlauf + 1 - t) * 2)
            best |= (np.abs(r - rr) < rr * 0.42) & (np.abs(Z) < 2.6 * (rr / 5.2) ** 0.5 + 0.6)
        return best & (Y >= 0)
    S.plus(spirale, "s")
    S.plus(lambda X, Y, Z: (np.abs(Y - 5.5) < 0.6) & (np.abs(Z) > 2.0) & (np.abs(Z) < 3.2) & (X > -3) & (X < 3)
           & spirale(X, Y, Z), "g")
    S.plus(kap((5, 0.6, 0), (12, 0.6, 0), 1.6, 0.9, zf=1.4), "m")
    S.rendern((-8, -1, -5), (14, 12, 5), versatz=(cx + 0.5, 0, cz + 0.5), dreh=dreh_y(math.pi / 2))
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(cx, y, cz + _r(5.5 * u, 3), w.b("birch_door", facing="south", half=half, hinge="left", open=False,
                                                powered=False))


def wurzelbruecke(w, f, cx, cz, u):
    """Bogenbrücke aus verschlungenen Wurzeln über einen leuchtenden Bach, mit Blüten und Laternen."""
    L = 9 * u + 4
    S = Skulptur(w, 1.0)
    S.mat("r", Verlauf(w, "Wurzel", ["mangrove_roots", "mangrove_log", "dark_oak_log"]), basis=1, rausch=2)
    S.mat("b", lambda x, y, z, *_: f.blatt[(x + z) % len(f.blatt)])
    for k in range(4):
        off = (k - 1.5) * 0.9
        pts = [(cx - L, 0, cz + off)]
        for t in np.linspace(0, 1, 9)[1:]:
            pts.append((cx - L + 2 * L * t, 6 * u * math.sin(math.pi * t) + 0.5, cz + off + 0.6 * math.sin(t * 7 + k)))
        for p0, p1 in zip(pts, pts[1:]):
            S.plus(kap(p0, p1, 0.75, 0.75), "r")
    S.plus(lambda X, Y, Z: (np.abs(X - cx) < L * 0.8) & (np.abs(Z - cz) <= 1.5)
           & (np.abs(Y - (6 * u * np.sin(np.pi * (X - cx + L) / (2 * L)) + 1.6)) < 0.6), "b")
    S.rendern((cx - L - 2, -1, cz - 4), (cx + L + 2, 6 * u + 3, cz + 4))
    for x in range(int(cx - L * 0.6), int(cx + L * 0.6) + 1):
        for z in range(cz - _r(4 * u, 3), cz + _r(4 * u, 3) + 1):
            if abs(x - cx) < L * 0.55 and abs(z - cz) <= _r(4 * u, 3):
                if w.hole(x, 0, z) is None or w.P.name(w.hole(x, 0, z)).endswith(("moss_block", "grass_block", "nylium")):
                    w.setze(x, 0, z, w.b("water", level=0))
                if w.rng.random() < 0.06:
                    w.setze(x, -1, z, f.licht)
    for s in (-1, 1):
        w.setze(cx + s * int(L), 1, cz + 2, w.b("lantern" if not f.mond else "soul_lantern", hanging=False,
                                               waterlogged=False))


def kristallbluete(w, f, cx, cz, u):
    """Riesige Blüte aus farbigem Glas mit leuchtendem Stempel auf einem Amethyst-Sockel."""
    S = Skulptur(w, u)
    S.mat("k", lambda x, y, z, *_: f.kristall[(x * 2 + y + z * 3) % 3])
    S.mat("l", f.licht)
    S.mat("a", w.b("amethyst_block"))
    S.plus(ell(0, 0.5, 0, 3, 1.5, 3), "a")
    S.plus(kap((0, 1, 0), (0.4, 7, 0.3), 0.6, 0.45), "a")
    for i in range(6):
        a = i * math.pi / 3
        dx, dz = math.cos(a), math.sin(a)
        S.plus(lambda X, Y, Z, dx=dx, dz=dz: (((X * dx + Z * dz) - 3.4) ** 2 / 9 + (X * dz - Z * dx) ** 2 / 2.4
                                             <= 1) & (np.abs(Y - 7.5 - 0.35 * (X * dx + Z * dz)) < 0.55), "k")
    S.plus(ell(0.4, 8, 0.3, 1.2, 1.2, 1.2), "l")
    S.rendern((-8, -1, -8), (8, 12, 8), versatz=(cx + 0.5, 0, cz + 0.5))


# ============================================================================ Vorlagen

def _einzel(fn, radius, streu=True):
    def vorlage(seed, g=1):
        w = _welt(seed)
        f = Feen(w, seed)
        u = U[g]
        _boden(w, f, radius * u + 3)
        fn(w, f, u)
        if streu:
            _streu(w, f, radius * u + 3)
        return w
    return vorlage


def feenstadt(seed, g=2):
    """Ganze Feenstadt: Pilzhäuser verschiedener Größe, Blütentürme, Laternenbaum, Feenring, Bach mit
    Wurzelbrücke und Kristallblüte – verbunden durch Moospfade."""
    w = _welt(seed)
    f = Feen(w, seed)
    u = U[g] * 0.75
    R = 26 * u + 8
    _boden(w, f, R)
    teile = [(pilzhaus, -0.45, -0.35, 1.0), (pilzhaus, 0.15, -0.55, 0.7), (pilzhaus, -0.6, 0.3, 0.8),
             (bluetenturm, 0.45, -0.15, None), (laternenbaum, 0.0, 0.05, None), (feenring, -0.15, 0.6, None),
             (kristallbluete, 0.55, 0.5, None), (pilzhaus, 0.3, 0.3, 0.6)]
    for fn, fx, fz, h in teile:
        x, z = round(fx * R), round(fz * R)
        if fn is pilzhaus:
            fn(w, f, x, z, u, h)
        elif fn is kristallbluete:
            fn(w, f, x, z, u * 0.8)
        else:
            fn(w, f, x, z, u * 0.8)
    for i in range(int(R * 3)):
        a = i * 0.07
        x, z = round(math.cos(a * 3) * R * 0.3 * math.sin(a)), round(math.sin(a * 2) * R * 0.5)
        w.setze(x, 0, z, w.b("dirt_path"))
    _streu(w, f, R, 0.08)
    return w


FEENSTADT = {
    "feenstadt": ("Feenstadt (komplett)", feenstadt),
    "pilzhaus": ("Pilzhaus", _einzel(lambda w, f, u: pilzhaus(w, f, 0, 0, u), 7)),
    "bluetenturm": ("Blütenturm", _einzel(lambda w, f, u: bluetenturm(w, f, 0, 0, u), 8)),
    "feenring": ("Feenring", _einzel(lambda w, f, u: feenring(w, f, 0, 0, u), 8, streu=False)),
    "laternenbaum": ("Laternenbaum", _einzel(lambda w, f, u: laternenbaum(w, f, 0, 0, u), 9)),
    "schneckenhaus": ("Schneckenhaus", _einzel(lambda w, f, u: schneckenhaus(w, f, 0, 0, u), 9)),
    "wurzelbruecke": ("Wurzelbrücke", _einzel(lambda w, f, u: wurzelbruecke(w, f, 0, 0, u), 10)),
    "kristallbluete": ("Kristallblüte", _einzel(lambda w, f, u: kristallbluete(w, f, 0, 0, u), 6)),
}

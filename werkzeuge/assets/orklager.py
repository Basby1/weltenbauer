"""Orklager – Paket: Kriegszelte, Hütten, Palisaden, Wachtürme, Totems, Schmiede, Knochentor,
Häuptlingsthron und ein ganzes Lager. Größen 0–3, Stil 1 Lehm & Rot, Stil 2 Schwarzfels & Seelenfeuer."""

from __future__ import annotations

import math

import numpy as np

from lib import Verlauf, Welt, einfuegen
from skulptur import Skulptur, dreh_y, ell, kap, kasten, kreisrand, platte, scheibe, spiegel_x, treppe, verbinde

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


class Pal:
    """Gemeinsame Farbpalette eines Lagers."""

    def __init__(self, w, seed):
        self.w = w
        if _stil(seed) == 0:
            self.holz = Verlauf(w, "Holz", ["dark_oak_log", "spruce_log", "stripped_spruce_log", "stripped_dark_oak_log"])
            self.fell = ["brown_wool", "brown_terracotta", "red_terracotta", "terracotta"]
            self.banner = ["red_wool", "black_wool"]
            self.boden = Verlauf(w, "Boden", ["coarse_dirt", "rooted_dirt", "dirt", "packed_mud"])
            self.stein = Verlauf(w, "Stein", ["cobblestone", "mossy_cobblestone", "andesite", "stone"])
            self.feuer, self.seele = "campfire", False
        else:
            self.holz = Verlauf(w, "Holz", ["dark_oak_log", "mangrove_log", "stripped_dark_oak_log", "crimson_stem"])
            self.fell = ["black_wool", "gray_wool", "black_terracotta", "gray_terracotta"]
            self.banner = ["black_wool", "red_wool"]
            self.boden = Verlauf(w, "Boden", ["soul_soil", "coarse_dirt", "blackstone", "basalt"])
            self.stein = Verlauf(w, "Stein", ["blackstone", "polished_blackstone", "basalt", "cobbled_deepslate"])
            self.feuer, self.seele = "soul_campfire", True

    def h(self, x, y, z, wert=None):
        return self.holz(1.5 if wert is None else wert + self.w.rng.random(), x, y, z)

    def zaun(self):
        return self.w.b("dark_oak_fence", north=False, south=False, east=False, west=False, waterlogged=False)

    def knochen(self, achse="y"):
        return self.w.b("bone_block", axis=achse)

    def feuerblock(self, signal=True):
        return self.w.b(self.feuer, lit=True, signal_fire=signal, facing="north", waterlogged=False)


def _boden(w, p, r, cx=0, cz=0):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, p.boden(w.rng.random() * 3.5, x, 0, z), ueberschreiben=False)


def _schaedel(w, x, y, z, gross=1.0):
    S = Skulptur(w, gross)
    S.mat("k", w.b("bone_block", axis="y"))
    S.mat("d", w.b("black_concrete"))
    S.plus(ell(0, 0.6, 0, 0.9, 0.8, 0.9), "k")
    S.plus(kasten(-0.5, 0.1, 0.6, 0.5, 0.4, 1.0), "k")
    S.plus(spiegel_x(ell(0.35, 0.7, 0.75, 0.22, 0.22, 0.2)), "d")
    S.plus(spiegel_x(kap((0.7, 1.1, 0), (1.5, 1.9, -0.2), 0.22, 0.08)), "k")
    S.rendern((-2, -1, -2), (2, 3, 2), versatz=(x + 0.5, y, z + 0.5))


# ============================================================================ Einzelteile

def kriegszelt(w, p, cx, cz, u, gross=1.0):
    """Rundes Fellzelt mit Stangen, die oben herausragen, Banner und Schädel am Eingang."""
    R = 3.2 * u * gross + 1.5
    H = _r(4.5 * u * gross + 2, 4)
    for y in range(1, H + 1):
        r = R * (1 - (y - 1) / H) ** 0.9
        for x, z in kreisrand(r, cx, cz):
            if z - cz > r * 0.6 and abs(x - cx) <= 1 and y <= 2:
                continue
            w.setze(x, y, z, w.b(p.fell[(x * 3 + y * 2 + z) % len(p.fell)]))
    for k in range(5):
        a = k * 2 * math.pi / 5 + 0.3
        for t in np.linspace(0, 1, H * 2):
            x = round(cx + math.cos(a) * R * (1 - t) * 0.95)
            z = round(cz + math.sin(a) * R * (1 - t) * 0.95)
            w.setze(x, 1 + int(t * (H + 1)), z, p.h(x, 0, z, 0.5))
        w.setze(round(cx + math.cos(a) * 0.5), H + 2, round(cz + math.sin(a) * 0.5), p.zaun())
    w.setze(cx, H + 3, cz, w.b(p.banner[0]))
    _schaedel(w, cx + 2, 1, cz + int(R) + 1, max(0.8, u * 0.8))
    w.setze(cx - 2, 1, cz + int(R) + 1, p.zaun())
    w.setze(cx - 2, 2, cz + int(R) + 1, p.feuerblock(False))


def orkhuette(w, p, cx, cz, u):
    """Gedrungene Hütte aus Stämmen mit Spitzpfählen auf dem Dach, Hörnern und Knochen."""
    bx, bz = _r(3 * u + 1, 3), _r(2.4 * u + 1, 2)
    H = _r(2.6 * u + 1, 3)
    for x in range(cx - bx, cx + bx + 1):
        for z in range(cz - bz, cz + bz + 1):
            rand = abs(x - cx) == bx or abs(z - cz) == bz
            for y in range(1, H + 1):
                if rand and not (z - cz == bz and x == cx and y <= 2):
                    w.setze(x, y, z, w.b("dark_oak_log" if (x + z) % 2 else "mud_bricks", axis="y")
                            if (x + z) % 2 else w.b("mud_bricks"))
    for k in range(bz + 2):
        for x in range(cx - bx - 1, cx + bx + 2):
            for s in (-1, 1):
                z = cz + s * (bz + 1 - k)
                w.setze(x, H + 1 + k, z, w.b(p.fell[(x + k) % 2]))
        if bz + 1 - k <= 0:
            break
    for x in range(cx - bx - 1, cx + bx + 2, 2):
        for k in range(_r(1.5 * u, 1) + 1):
            w.setze(x, H + bz + 3 + k, cz, p.zaun())
    for s in (-1, 1):
        S = Skulptur(w, max(0.8, u))
        S.mat("k", p.knochen())
        S.plus(kap((0, 0, 0), (s * 1.2, 1.4, 0.3), 0.35, 0.12), "k")
        S.rendern((-2, -1, -1), (2, 2, 1), versatz=(cx + s * 1.5 + 0.5, H + 0.5, cz + bz + 1.5))
    _schaedel(w, cx, H - 1 if H > 3 else H, cz + bz + 1, max(0.7, u * 0.7))


def palisade_ring(w, p, R, u, tor_breite=2, tuerme=True):
    """Kreis aus angespitzten Stämmen mit Tor und zwei Torwachtürmen."""
    h = _r(4 * u + 2, 4)
    for i, (x, z) in enumerate(kreisrand(R)):
        if z > R * 0.7 and abs(x) <= tor_breite:
            continue
        hh = h + (1 if i % 2 else 0)
        for y in range(1, hh + 1):
            w.setze(x, y, z, p.h(x, y, z))
        w.setze(x, hh + 1, z, p.zaun())
    if tuerme:
        for s in (-1, 1):
            wachturm_teil(w, p, s * (tor_breite + 2), int(R) - 1, u, klein=True)
    # Tor mit Querbalken und Schädel
    for x in range(-tor_breite - 1, tor_breite + 2):
        w.setze(x, h + 2, int(R), p.h(x, h + 2, int(R), 2))
    _schaedel(w, 0, h + 3, int(R), max(0.8, u * 0.9))


def wachturm_teil(w, p, cx, cz, u, klein=False):
    H = _r((6 if klein else 11) * u + 3, 6)
    b = 1 if klein or u < 1.5 else 2
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            for y in range(1, H + 1):
                w.setze(cx + s1 * b, y, cz + s2 * b, p.h(cx, y, cz))
    for y in range(3, H, 3):
        for k in range(-b, b + 1):
            w.setze(cx + k, y, cz - b, w.b("dark_oak_fence", east=True, west=True, north=False, south=False,
                                           waterlogged=False))
    for x in range(cx - b - 1, cx + b + 2):
        for z in range(cz - b - 1, cz + b + 2):
            w.setze(x, H + 1, z, w.b("dark_oak_planks"))
            if max(abs(x - cx), abs(z - cz)) == b + 1:
                w.setze(x, H + 2, z, p.zaun() if (x + z) % 2 else p.h(x, H + 2, z))
                if (x + z) % 3 == 0:
                    w.setze(x, H + 3, z, p.zaun())
    for y in range(H + 2, H + 5 + int(2 * u)):
        w.setze(cx, y, cz, p.zaun())
    for k in range(_r(2 * u, 2)):
        w.setze(cx - 1 - k, H + 4 + int(2 * u), cz, w.b(p.banner[k % 2]))
        w.setze(cx - 1 - k, H + 3 + int(2 * u), cz, w.b(p.banner[(k + 1) % 2]))
    w.setze(cx + b, H + 2, cz + b, p.feuerblock())


def totempfahl(w, p, cx, cz, u, hoehe=4):
    """Totempfahl aus gestapelten Fratzen mit Hörnern, Bemalung und Feuerschalen."""
    S = Skulptur(w, u)
    S.mat("h", p.holz, basis=1.5, rausch=1.5)
    S.mat("r", w.b("red_terracotta" if not p.seele else "cyan_terracotta"))
    S.mat("k", p.knochen())
    S.mat("d", w.b("black_concrete"))
    S.mat("e", w.b("shroomlight" if not p.seele else "sea_lantern"))
    for i in range(hoehe):
        y = 1 + i * 3.2
        S.plus(ell(0, y + 1.5, 0, 1.6, 1.6, 1.4), "h")
        S.plus(kasten(-1.0, y + 2.0, 1.0, 1.0, y + 2.4, 1.5), "r")
        S.plus(spiegel_x(ell(0.6, y + 1.8, 1.2, 0.3, 0.3, 0.25)), "e" if i == hoehe - 1 else "d")
        S.plus(kasten(-0.7, y + 0.6, 1.0, 0.7, y + 1.0, 1.5), "d")
        if i % 2 == 0:
            S.plus(spiegel_x(kap((1.4, y + 2, 0), (2.6, y + 3.2, 0), 0.4, 0.12)), "k")
        else:
            S.plus(spiegel_x(kap((1.4, y + 1.5, 0), (2.4, y + 1.0, 0.5), 0.45, 0.2)), "r")
    S.plus(spiegel_x(kap((1.2, 1 + hoehe * 3.2, 0), (3.0, 3 + hoehe * 3.2, 0), 0.5, 0.1)), "k")
    S.rendern((-4, 0, -2), (4, hoehe * 3.2 + 4, 2), versatz=(cx + 0.5, 0, cz + 0.5), dreh=dreh_y(math.pi / 4))
    for s in (-1, 1):
        w.setze(cx + s * _r(2 * u + 1, 2), 1, cz + _r(2 * u + 1, 2), p.zaun())
        w.setze(cx + s * _r(2 * u + 1, 2), 2, cz + _r(2 * u + 1, 2), p.feuerblock(False))


def schmiede(w, p, cx, cz, u):
    """Offene Schmiede: Esse aus Stein mit Glut, Amboss, Wasserbottich, Waffengestell, Schutzdach aus Fell."""
    bx, bz = _r(3 * u + 1, 2), _r(2 * u + 1, 2)
    for x in range(cx - 1, cx + 2):
        for z in range(cz - bz, cz - bz + 2):
            for y in range(1, 3):
                w.setze(x, y, z, p.stein(w.rng.random() * 3, x, y, z))
    w.setze(cx, 3, cz - bz, w.b("magma_block"))
    w.setze(cx, 2, cz - bz + 1, w.b("magma_block"))
    for y in range(3, 3 + _r(4 * u, 3)):
        w.setze(cx, y, cz - bz, p.stein(1, cx, y, cz - bz))
    w.setze(cx, 3 + _r(4 * u, 3), cz - bz, p.feuerblock())
    w.setze(cx + 2, 1, cz, w.b("anvil", facing="north"))
    w.setze(cx - 2, 1, cz, w.b("cauldron"))
    for z in range(cz - 1, cz + 2):
        w.setze(cx + bx, 1, z, w.b("dark_oak_fence", north=z > cz - 1, south=z < cz + 1, east=False, west=False,
                                   waterlogged=False))
        w.setze(cx + bx, 2, z, w.b("iron_bars", north=z > cz - 1, south=z < cz + 1, east=False, west=False,
                                   waterlogged=False))
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            for y in range(1, 4):
                w.setze(cx + s1 * bx, y, cz + s2 * bz, p.h(cx, y, cz))
    for x in range(cx - bx, cx + bx + 1):
        for z in range(cz - bz, cz + bz + 1):
            w.setze(x, 4, z, w.b(p.fell[(x + z) % 3]))


def knochentor(w, p, u, cz=0):
    """Riesiges Tor aus zwei gekreuzten Stoßzähnen mit Schädel in der Mitte."""
    S = Skulptur(w, u)
    S.mat("k", Verlauf(w, "Knochen", ["bone_block", "calcite", "smooth_quartz"]), basis=0.5, rausch=1.5)
    S.mat("r", w.b(p.banner[0]))
    for s in (-1, 1):
        pts = [(s * 5, 0, 0), (s * 5.5, 4, 0.3), (s * 4.5, 8, 0.6), (s * 2, 10.5, 0.8), (-s * 0.8, 11.2, 0.8)]
        for k, (a, b) in enumerate(zip(pts, pts[1:])):
            S.plus(kap(a, b, 1.3 - k * 0.25, 1.3 - (k + 1) * 0.25), "k")
        S.plus(kasten(s * 5 - 0.7, 3, -0.8, s * 5 + 0.7, 3.6, 0.8), "r")
    S.rendern((-8, 0, -2), (8, 13, 3), versatz=(0.5, 1, cz + 0.5))
    _schaedel(w, 0, int(11.5 * u) - 1, cz + 1, max(1.0, u * 1.4))


def thron(w, p, cx, cz, u):
    """Häuptlingsthron: Stufenpodest, Sitz aus Schwarzstein, Rückenlehne aus Stoßzähnen, Banner, Feuerschalen."""
    s = _r(3 * u + 1, 2)
    for k in range(2):
        for x in range(cx - s - 2 + k, cx + s + 3 - k):
            for z in range(cz - s - 2 + k, cz + s + 3 - k):
                w.setze(x, 1 + k, z, p.stein(1 + k, x, 1 + k, z))
    for x in range(cx - 1, cx + 2):
        w.setze(x, 3, cz, w.b("polished_blackstone_stairs", facing="north", half="bottom", shape="straight",
                              waterlogged=False))
        for y in range(3, 6):
            w.setze(x, y, cz - 1, w.b("polished_blackstone"))
    w.setze(cx - 2, 4, cz, w.b("polished_blackstone_slab", type="bottom", waterlogged=False))
    w.setze(cx + 2, 4, cz, w.b("polished_blackstone_slab", type="bottom", waterlogged=False))
    S = Skulptur(w, max(0.8, u))
    S.mat("k", w.b("bone_block", axis="y"))
    for i in range(5):
        a = (i - 2) * 0.35
        S.plus(kap((math.sin(a) * 1.2, 0, 0), (math.sin(a) * 3, 5 + (2 - abs(i - 2)) * 1.2, -0.5), 0.45, 0.12), "k")
    S.rendern((-5, -1, -2), (5, 9, 2), versatz=(cx + 0.5, 5, cz - 1 + 0.5))
    for sx in (-1, 1):
        for y in range(3, 3 + _r(5 * u, 3)):
            w.setze(cx + sx * (s + 1), y, cz - s - 1, p.zaun())
        for k in range(_r(3 * u, 2)):
            w.setze(cx + sx * (s + 1), 3 + _r(5 * u, 3) - k, cz - s, w.b(p.banner[k % 2]))
        w.setze(cx + sx * (s + 1), 3, cz + s + 1, p.feuerblock(False))


# ============================================================================ Vorlagen

def _einzel(fn, radius):
    def vorlage(seed, g=1):
        w = _welt(seed)
        p = Pal(w, seed)
        u = U[g]
        _boden(w, p, radius * u + 3)
        fn(w, p, u)
        return w
    return vorlage


def orklager(seed, g=2):
    """Ganzes Kriegslager: Palisadenring mit Tor und Torwachen, Zelte, Hütten, Schmiede, Totempfahl,
    Häuptlingsthron und ein großes Lagerfeuer in der Mitte."""
    w = _welt(seed)
    p = Pal(w, seed)
    u = U[g]
    R = 16 * u + 7
    _boden(w, p, R + 1)
    palisade_ring(w, p, R, u, tor_breite=_r(1.5 * u, 1))
    for x, z in scheibe(max(1, 1.2 * u)):
        w.setze(x, 1, z, p.feuerblock())
    for x, z in kreisrand(max(1, 1.2 * u) + 1):
        w.setze(x, 1, z, p.stein(1, x, 1, z))
    plaetze = [(-0.5, -0.45), (0.5, -0.45), (-0.62, 0.15), (0.62, 0.15), (0.0, -0.7), (-0.3, 0.55), (0.35, 0.55)]
    for i, (fx, fz) in enumerate(plaetze[: 4 + g]):
        x, z = round(fx * R), round(fz * R)
        if i % 3 == 0:
            orkhuette(w, p, x, z, u * 0.8)
        else:
            kriegszelt(w, p, x, z, u * 0.8)
    schmiede(w, p, round(R * 0.55), round(-R * 0.1) - 3, u * 0.8)
    totempfahl(w, p, round(-R * 0.25), round(R * 0.15), u * 0.8, hoehe=3 + g // 2)
    thron(w, p, 0, round(-R * 0.62), u * 0.8)
    return w


ORKLAGER = {
    "orklager": ("Orklager (komplett)", orklager),
    "kriegszelt": ("Kriegszelt", _einzel(lambda w, p, u: kriegszelt(w, p, 0, 0, u, 1.0), 5)),
    "orkhuette": ("Orkhütte", _einzel(lambda w, p, u: orkhuette(w, p, 0, 0, u), 5)),
    "orkturm": ("Ork-Wachturm", _einzel(lambda w, p, u: wachturm_teil(w, p, 0, 0, u), 4)),
    "totempfahl": ("Totempfahl", _einzel(lambda w, p, u: totempfahl(w, p, 0, 0, u, hoehe=4), 4)),
    "orkschmiede": ("Orkschmiede", _einzel(lambda w, p, u: schmiede(w, p, 0, 0, u), 5)),
    "knochentor": ("Knochentor", _einzel(lambda w, p, u: knochentor(w, p, u), 7)),
    "orkthron": ("Häuptlingsthron", _einzel(lambda w, p, u: thron(w, p, 0, 0, u), 5)),
    "palisade": ("Palisadenring", _einzel(lambda w, p, u: palisade_ring(w, p, 9 * u + 4, u), 10)),
}

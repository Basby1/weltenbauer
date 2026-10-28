"""Friedhof & Spuk, Hexenwerk, Drachenhort, Himmelsreich – vier Pakete."""

from __future__ import annotations

import math

import numpy as np

from bau import Stil, kasten_haus, satteldach
from lib import Verlauf, Welt, laub, ueberwuchern
from skulptur import Skulptur, ell, kap, kegel, kreisrand, platte, scheibe, spiegel_x, treppe, verbinde, zur_mitte

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _boden(w, r, wahl, cx=0, cz=0):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, wahl(x, z), ueberschreiben=False)


def _pf(w, mat):
    return w.b(mat, north=False, south=False, east=False, west=False, waterlogged=False)


def _toter_baum(w, x, z, u, y0=1, holz="dark_oak_log", ast="dark_oak_fence"):
    h = _r(6 * u + 3, 4)
    for y in range(y0, y0 + h):
        w.setze(x + (1 if y > y0 + h * 0.6 else 0), y, z, w.b(holz, axis="y"))
    for i in range(4 + int(u)):
        a = i * 2.3 + w.rng.random()
        yb = y0 + int(h * (0.45 + 0.5 * w.rng.random()))
        lang = (2 + 2 * w.rng.random()) * u + 1
        for t in np.linspace(0, 1, int(lang * 2) + 2):
            w.setze(round(x + math.cos(a) * lang * t), round(yb + lang * 0.7 * t * t),
                    round(z + math.sin(a) * lang * t), _pf(w, ast))
    return y0 + h


# ============================================================================ Friedhof & Spuk

def _grabstein(w, x, z, art, mat):
    if art == 0:
        w.setze(x, 1, z, w.b(f"{mat}_wall", up=True, north="none", south="none", east="none", west="none",
                             waterlogged=False))
    elif art == 1:
        w.setze(x, 1, z, w.b(f"{mat}s" if not mat.endswith("bricks") else mat) if False else w.b("chiseled_stone_bricks"))
        w.setze(x, 2, z, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    else:
        w.setze(x, 1, z, w.b("cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
                             waterlogged=False))
        w.setze(x - 1, 2, z, w.b("cobblestone_wall", up=False, north="none", south="none", east="low", west="none",
                                 waterlogged=False)) if False else None
    w.setze(x, 0, z + 1, w.b("coarse_dirt"))
    w.setze(x, 0, z + 2, w.b("coarse_dirt"))


def friedhof(seed, g=1):
    """Friedhof mit Grabsteinreihen, schmiedeeisernem Zaun, Tor, toten Bäumen, Laternen und Kiesweg."""
    w = _welt(seed)
    u = U[g]
    L = _r(8 * u + 4, 6)
    _boden(w, L * 1.2 + 3, lambda x, z: w.b("podzol", snowy=False) if w.rng.random() < 0.3 else
           w.b("grass_block", snowy=False))
    verbinde(w, [(x, 1, z) for x in range(-L, L + 1) for z in (-L, L) if not (abs(x) <= 1 and z == L)] +
             [(x, 1, z) for x in (-L, L) for z in range(-L + 1, L)], "iron_bars")
    for x in (-2, 2):
        for y in range(1, 4):
            w.setze(x, y, L, w.b("stone_bricks"))
    for z in range(-L + 1, L + 1):
        w.setze(0, 0, z, w.b("gravel"))
    for z in range(-L + 2, L - 2, 4):
        for x in list(range(-L + 2, -1, 2)) + list(range(3, L - 1, 2)):
            _grabstein(w, x, z, (x * 3 + z) % 3, "stone_brick")
    _toter_baum(w, -L + 2, -L + 2, u * 0.8)
    _toter_baum(w, L - 2, -L + 3, u * 0.7)
    for z in range(-L + 3, L, 6):
        w.setze(1, 1, z, w.b("soul_lantern" if _stil(seed) else "lantern", hanging=False, waterlogged=False))
    ueberwuchern(w, None, ranken=0.2, moos_oben=0.3, pflanzen=0.2, buesche=0.0, max_ranke=2)
    return w


def mausoleum(seed, g=1):
    """Mausoleum mit Säulenportikus, Bronzetür, Dreiecksgiebel, Trauerstatue und Kerzen."""
    w = _welt(seed)
    u = U[g]
    stein = Verlauf(w, "Marmor", ["polished_andesite", "stone_bricks", "polished_diorite", "calcite"]) if _stil(seed) == 0 \
        else Verlauf(w, "Dunkel", ["polished_blackstone_bricks", "polished_deepslate", "deepslate_tiles"])
    h = _r(3 * u + 2, 3)
    H = _r(4 * u + 3, 4)
    _boden(w, h + 6, lambda x, z: w.b("grass_block", snowy=False))
    for y in range(0, H + 1):
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                if y == 0 or max(abs(x), abs(z)) == h or y == H:
                    w.setze(x, y, z, stein(0.5 + 2 * y / H + w.rng.random(), x, y, z))
    for y in range(1, 3):
        w.setze(0, y, h, w.b("iron_door", facing="south", half="lower" if y == 1 else "upper", hinge="left", open=False,
                             powered=False))
    for x in range(-h, h + 1, 2):
        for y in range(1, H):
            w.setze(x, y, h + 2, w.b("quartz_pillar", axis="y") if _stil(seed) == 0 else w.b("polished_blackstone_bricks"))
    for x in range(-h - 1, h + 2):
        for z in range(h, h + 3):
            w.setze(x, H, z, stein(2.5, x, H, z))
            w.setze(x, 0, z, stein(1, x, 0, z))
    for kk in range(1, h + 2):
        for x in range(-h - 1 + kk, h + 2 - kk):
            w.setze(x, H + kk, h + 2, stein(3, x, H + kk, h + 2))
    for kk in range(h + 2):
        for x in range(-h - 1 + kk, h + 2 - kk):
            for z in range(-h, h + 2):
                if x in (-h - 1 + kk, h + 1 - kk):
                    w.setze(x, H + 1 + kk, z, stein(3, x, H + kk, z))
    S = Skulptur(w, u * 0.5)
    S.mat("s", lambda x, y, z, *_: w.b("calcite"))
    S.plus(kegel(0, 0, 0, 6, 1.8, 0.9), "s")
    S.plus(ell(0, 7, 0, 0.9, 1.1, 0.9), "s")
    S.plus(spiegel_x(kap((0.8, 5, 0), (3, 7.5, -0.8), 0.4, 0.2)), "s")
    S.rendern((-4, 0, -2), (4, 9, 2), versatz=(0.5, H + h + 2, 0.5))
    for x in (-h - 1, h + 1):
        w.setze(x, 1, h + 4, w.b("white_candle", candles=3, lit=True, waterlogged=False))
    return w


def gruft(seed, g=1):
    """Gruft-Eingang in einem Hügel: Treppe hinab, Schädel-Pfeiler, Gitter, Spinnweben und Seelenfeuer."""
    w = _welt(seed)
    u = U[g]
    R = 6 * u + 3
    for x, z in scheibe(R + 2):
        d = math.hypot(x, z) / (R + 2)
        h = int((1 - d * d) * 4 * u) + 1
        for y in range(0, h + 1):
            w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else w.b("dirt"))
    b = _r(1.5 * u + 0.5, 1)
    for k in range(_r(4 * u, 3)):
        for x in range(-b, b + 1):
            z = int(R * 0.4) + _r(4 * u, 3) - k
            for y in range(k + 1, int(4 * u) + 3):
                w.setze(x, -k + y - 1 if False else 0, z, w.b("air")) if False else None
            for y in range(-k, int(4 * u) + 3):
                w.bloecke.pop((x, y, z), None)
            w.setze(x, -k, z, treppe(w, "stone_brick", "north"))
    for s in (-1, 1):
        x = s * (b + 1)
        for y in range(0, _r(3 * u, 2) + 1):
            w.setze(x, y, int(R * 0.4) + _r(4 * u, 3), w.b("polished_blackstone_bricks"))
        w.setze(x, _r(3 * u, 2) + 1, int(R * 0.4) + _r(4 * u, 3), w.b("skeleton_skull", rotation=0))
        w.setze(x, _r(3 * u, 2) - 1, int(R * 0.4) + _r(4 * u, 3) + 1, w.b("soul_lantern", hanging=False,
                                                                             waterlogged=False))
    for x in range(-b, b + 1):
        w.setze(x, -_r(4 * u, 3), int(R * 0.4) - 1, w.b("iron_bars", north=False, south=False, east=True, west=True,
                                                        waterlogged=False))
        w.setze(x, -_r(4 * u, 3) + 1, int(R * 0.4) - 1, w.b("cobweb"))
    _toter_baum(w, -int(R * 0.6), -int(R * 0.3), u * 0.7, y0=int(3 * u) + 1)
    return w


def spukhaus(seed, g=2):
    """Schiefes Spukhaus: dunkles Holz, zerbrochene Fenster, Türmchen mit spitzem Dach, Spinnweben,
    Kürbisse, toter Baum und rostiger Zaun."""
    w = _welt(seed)
    u = U[g]
    st = Stil(w, Verlauf(w, "Morsch", ["dark_oak_planks", "spruce_planks", "stripped_dark_oak_log", "mossy_cobblestone"]),
              holz="dark_oak", dach="deepslate_tile", dach_voll="deepslate_tiles", sockel="mossy_cobblestone",
              fachwerk=True, glas="gray_stained_glass_pane" if False else "glass_pane")
    bx, bz = [6, 8, 11, 14][g], [5, 7, 8, 10][g]
    et = [1, 2, 3, 3][g]
    _boden(w, max(bx, bz) + 6, lambda x, z: w.b("podzol", snowy=False) if w.rng.random() < 0.5 else
           w.b("coarse_dirt"))
    x0, z0 = -bx // 2, -bz // 2
    yt, a, b, c, d = kasten_haus(w, st, x0, z0, x0 + bx, z0 + bz, 0, et, eh=4, blumen=False, laternen=False)
    top = satteldach(w, st, a, b, c, d, yt, ue=1)
    from bau import turm_rund
    turm_rund(w, st, c, d, 1, 1.4 * u + 1, yt + 2, dach_hoehe=_r(6 * u + 2, 4))
    for p in list(w.bloecke):
        if w.P.name(w.bloecke[p]).endswith("glass_pane") and w.rng.random() < 0.35:
            w.bloecke[p] = w.b("cobweb") if w.rng.random() < 0.5 else 0
    for x in range(a, c + 1, 2):
        if w.rng.random() < 0.4:
            w.setze(x, yt, d + 1, w.b("cobweb"), ueberschreiben=False)
    _toter_baum(w, x0 - 4, z0 + 1, u)
    for k in range(3):
        w.setze(x0 + 1 + k * 2, 1, z0 + bz + 2, w.b("jack_o_lantern", facing="south"))
    verbinde(w, [(x, 1, z0 + bz + 4) for x in range(x0 - 2, x0 + bx + 3) if abs(x - (x0 + bx // 2)) > 1 and
                 w.rng.random() < 0.8], "iron_bars")
    return w


def kraehenbaum(seed, g=2):
    """Riesiger, verdrehter toter Baum mit hängenden Käfigen, Laternen an Ketten und Krähennestern."""
    w = _welt(seed)
    u = U[g]
    _boden(w, 6 * u + 4, lambda x, z: w.b("podzol", snowy=False) if w.rng.random() < 0.5 else w.b("coarse_dirt"))
    S = Skulptur(w, u)
    S.mat("h", lambda x, y, z, *_: w.b("dark_oak_log", axis="y") if (x + z) % 3 else w.b("stripped_dark_oak_log", axis="y"))
    S.plus(kap((0, 0, 0), (0.6, 7, 0.4), 1.6, 0.9), "h")
    for i in range(5):
        a = i * 2 * math.pi / 5 + 0.3
        S.plus(kap((math.cos(a) * 0.6, 0.5, math.sin(a) * 0.6), (math.cos(a) * 3, -0.2, math.sin(a) * 3), 0.9, 0.4), "h")
    enden = []
    for i in range(6):
        a = i * 2 * math.pi / 6 + 0.5
        yb = 4.5 + (i % 3) * 1.3
        e = (math.cos(a) * 6, yb + 3.5, math.sin(a) * 6)
        m = (math.cos(a + 0.4) * 3, yb + 2.5, math.sin(a + 0.4) * 3)
        S.plus(kap((0.5, yb, 0.3), m, 0.6, 0.4), "h")
        S.plus(kap(m, e, 0.4, 0.2), "h")
        enden.append(m)
    S.rendern((-8, -1, -8), (8, 13, 8), versatz=(0.5, 1, 0.5))
    for i, (mx, my, mz) in enumerate(enden):
        x, y, z = round(mx * u), round(my * u) + 1, round(mz * u)
        lang = int(w.rng.integers(2, 4 + int(u)))
        for k in range(1, lang):
            w.setze(x, y - k, z, w.b("chain", axis="y", waterlogged=False), ueberschreiben=False)
        if i % 2 == 0:
            for dy in range(2):
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    w.setze(x + dx, y - lang - dy, z + dz, w.b("iron_bars", north=dz == 0, south=dz == 0, east=dx == 0,
                                                               west=dx == 0, waterlogged=False), ueberschreiben=False)
            w.setze(x, y - lang + 1, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                            waterlogged=False), ueberschreiben=False)
        else:
            w.setze(x, y - lang, z, w.b("soul_lantern" if _stil(seed) else "lantern", hanging=True, waterlogged=False),
                    ueberschreiben=False)
    return w


def totenwaechter(seed, g=2):
    """Kapuzengestalt aus dunklem Stein mit langer Sense, auf einem Sockel zwischen zwei Grablaternen."""
    w = _welt(seed)
    u = U[g]
    _boden(w, 5 * u + 3, lambda x, z: w.b("podzol", snowy=False))
    for x, z in scheibe(2.5 * u + 1):
        for y in range(0, _r(1.5 * u, 1) + 1):
            w.setze(x, y, z, w.b("polished_blackstone_bricks"))
    S = Skulptur(w, u)
    S.mat("m", lambda x, y, z, lx, ly, lz: Verlauf(w, "Mantel", ["blackstone", "polished_blackstone", "deepslate_tiles"])
          (0.3 + ly / 6, x, y, z) if _stil(seed) == 0 else Verlauf(w, "Mantel", ["black_wool", "gray_wool"])(ly / 10, x, y, z))
    S.mat("g", w.b("black_concrete"))
    S.mat("a", w.b("soul_lantern", hanging=False, waterlogged=False) if _stil(seed) else w.b("shroomlight"))
    S.mat("s", lambda x, y, z, *_: w.b("dark_oak_log", axis="y"))
    S.mat("k", w.b("iron_block"))

    def mantel(X, Y, Z):
        r = 2.2 - 1.0 * np.clip(Y / 9, 0, 1)
        a = np.arctan2(Z, X)
        r = r * (1 + 0.08 * np.sin(8 * a))
        return (Y >= 0) & (Y <= 9) & (X * X + Z * Z <= r * r)
    S.plus(mantel, "m")
    S.plus(ell(0, 10, 0, 1.4, 1.6, 1.5), "m")
    S.plus(ell(0, 9.8, 0.8, 0.8, 1.0, 0.8), "g")
    S.plus(spiegel_x(ell(0.35, 10, 1.4, 0.2, 0.15, 0.2)), "a")
    S.plus(kap((2.2, 0, 1.0), (2.2, 13, 1.0), 0.3), "s")
    S.plus(kap((2.2, 13, 1.0), (-1.5, 12.2, 1.8), 0.35, 0.15), "k")
    S.plus(kap((1.4, 7.5, 0.4), (2.2, 7.5, 1.0), 0.5), "m")
    S.rendern((-4, 0, -3), (4, 14, 4), versatz=(0.5, _r(1.5 * u, 1) + 1, 0.5))
    for s in (-1, 1):
        x = s * _r(4 * u + 1, 3)
        for y in range(1, _r(2 * u, 2) + 1):
            w.setze(x, y, 0, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                                 waterlogged=False))
        w.setze(x, _r(2 * u, 2) + 1, 0, w.b("soul_lantern", hanging=False, waterlogged=False))
    return w


FRIEDHOF = {
    "friedhof": ("Friedhof", friedhof),
    "mausoleum": ("Mausoleum", mausoleum),
    "gruft": ("Gruft", gruft),
    "spukhaus": ("Spukhaus", spukhaus),
    "kraehenbaum": ("Krähenbaum", kraehenbaum),
    "totenwaechter": ("Totenwächter", totenwaechter),
}


# ============================================================================ Hexenwerk

class Hexe:
    def __init__(self, w, seed):
        self.w = w
        self.sumpf = _stil(seed) == 1
        self.holz = "dark_oak" if not self.sumpf else "mangrove"
        self.dach = Verlauf(w, "Hexendach", ["purple_terracotta", "black_terracotta", "magenta_terracotta"]) \
            if not self.sumpf else Verlauf(w, "Sumpfdach", ["green_terracotta", "moss_block", "brown_terracotta"])
        self.glas = w.b("purple_stained_glass") if not self.sumpf else w.b("lime_stained_glass")
        self.boden = (lambda x, z: w.b("podzol", snowy=False) if w.rng.random() < 0.5 else w.b("grass_block", snowy=False)) \
            if not self.sumpf else (lambda x, z: w.b("mud") if w.rng.random() < 0.5 else w.b("moss_block"))


def _hexenhut_dach(w, k, cx, cz, y0, R, H, knick=2.0):
    for kk in range(H + 1):
        t = kk / H
        r = (R + 1) * (1 - t) ** 1.3
        ox = t * t * knick
        for x, z in kreisrand(max(0.3, r), 0, 0):
            w.setze(round(cx + x + ox), y0 + kk, cz + z, k.dach(3 * t + w.rng.random() * 0.4, x, y0 + kk, z))
        if kk == 0:
            for x, z in scheibe(r, 0, 0):
                w.setze(round(cx + x), y0, cz + z, k.dach(0.5, x, y0, z))


def hexenhuette(seed, g=1):
    """Schiefe Hexenhütte mit geknicktem Spitzdach, krummem Kamin mit farbigem Rauch, Kessel, Kräuterbündeln
    und Pilzen."""
    w = _welt(seed)
    k = Hexe(w, seed)
    u = U[g]
    R = 3 * u + 2
    H = _r(3.5 * u + 2, 3)
    _boden(w, R + 6, k.boden)
    for y in range(1, H + 1):
        for i, (x, z) in enumerate(kreisrand(R)):
            ox = round(0.15 * y)
            fen = y == 2 and i % 5 == 0
            w.setze(x + ox, y, z, k.glas if fen else w.b(f"{k.holz}_planks") if (i + y) % 4 else
                    w.b(f"stripped_{k.holz}_log", axis="y"))
    for x, z in scheibe(R - 0.5):
        w.setze(x, 0, z, w.b(f"{k.holz}_planks"))
    _hexenhut_dach(w, k, round(0.15 * H), 0, H + 1, R + 0.5, _r(R * 2.4, 5))
    for y in range(1, H + _r(R * 1.5, 3)):
        w.setze(-int(R) - (1 if y > H else 0), y, 1, w.b("cobblestone") if y % 3 else w.b("mossy_cobblestone"))
    w.setze(-int(R) - 1, H + _r(R * 1.5, 3), 1, w.b("soul_campfire" if not k.sumpf else "campfire", lit=True,
                                                    signal_fire=True, facing="north", waterlogged=False))
    w.setze(round(R) + 2, 1, 0, w.b("water_cauldron", level=3))
    w.setze(round(R) + 2, 0, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(0, y, int(R), w.b(f"{k.holz}_door", facing="south", half=half, hinge="left", open=False, powered=False))
    for i in range(6):
        a = w.rng.random() * 2 * math.pi
        x, z = round(math.cos(a) * (R + 2)), round(math.sin(a) * (R + 2))
        w.setze(x, 1, z, w.b("red_mushroom" if i % 2 else "brown_mushroom"), ueberschreiben=False)
    return w


def alchemieturm(seed, g=2):
    """Alchemistenturm: krummer Turm mit Erkern, Laborfenstern, Braustand-Etagen, bunten Rauchschloten
    und gläserner Kuppel."""
    w = _welt(seed)
    k = Hexe(w, seed)
    u = U[g]
    R = 2.6 * u + 1.6
    H = _r(14 * u + 5, 8)
    _boden(w, R + 6, k.boden)
    stein = Verlauf(w, "Turm", ["mossy_cobblestone", "cobblestone", "stone_bricks", "polished_andesite"])
    for y in range(0, H):
        ox = math.sin(y / H * 2.5) * u
        for i, (x, z) in enumerate(kreisrand(R)):
            fen = y % 5 == 3 and i % 4 == 0
            w.setze(round(x + ox), y, z, k.glas if fen else stein(0.3 + 3 * y / H + w.rng.random() * 0.5, x, y, z))
        if y % 5 == 0:
            for x, z in scheibe(R - 0.8):
                w.setze(round(x + ox), y, z, w.b(f"{k.holz}_planks"))
            w.setze(round(ox), y + 1, 0, w.b("brewing_stand", has_bottle_0=True, has_bottle_1=True, has_bottle_2=False))
    oxt = round(math.sin(2.5) * u)
    for y in range(0, _r(R, 2) + 1):
        for x, z in scheibe(max(0.3, R * math.sqrt(max(0, 1 - (y / (R + 0.5)) ** 2)))):
            if math.hypot(x, z) > R * math.sqrt(max(0, 1 - (y / (R + 0.5)) ** 2)) - 1.1:
                w.setze(x + oxt, H + y, z, k.glas)
    for i, farbe in enumerate(("lime", "purple", "orange")):
        a = i * 2.1
        cx, cz = round(math.cos(a) * (R + 1)), round(math.sin(a) * (R + 1))
        yy = int(H * (0.5 + 0.15 * i))
        for y in range(yy, yy + _r(3 * u, 2)):
            w.setze(cx, y, cz, w.b("bricks"))
        w.setze(cx, yy + _r(3 * u, 2), cz, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
        w.setze(cx, yy + _r(3 * u, 2) + 1, cz, w.b(f"{farbe}_stained_glass"))
    return w


def kesselplatz(seed, g=1):
    """Riesiger Hexenkessel über Feuer in einem Steinkreis, mit Besen, Kerzen und blubberndem Trank."""
    w = _welt(seed)
    k = Hexe(w, seed)
    u = U[g]
    R = 2.5 * u + 1.5
    _boden(w, R + 6, k.boden)
    S = Skulptur(w, 1.0)
    S.mat("k", w.b("black_concrete") if not k.sumpf else w.b("polished_blackstone"))
    S.mat("t", k.glas)
    S.mat("f", w.b("magma_block"))
    S.plus(lambda X, Y, Z: ((X * X + Z * Z) ** 0.5 <= R * np.sqrt(np.clip(1 - ((Y - R) / R) ** 2, 0, 1)) + 0.4) &
           ((X * X + Z * Z) ** 0.5 > R * np.sqrt(np.clip(1 - ((Y - R) / R) ** 2, 0, 1)) - 0.8) & (Y >= 0.8) & (Y <= R * 1.5), "k")
    S.plus(lambda X, Y, Z: (np.abs(Y - R * 1.3) < 0.5) & (X * X + Z * Z <= (R * 0.85) ** 2), "t")
    S.plus(lambda X, Y, Z: (Y < 1) & (X * X + Z * Z <= (R * 0.8) ** 2), "f")
    S.rendern((-R - 2, 0, -R - 2), (R + 2, R * 2, R + 2), versatz=(0.5, 1, 0.5))
    for i, (x, z) in enumerate(kreisrand(R + 3)):
        if i % 3 == 0:
            w.setze(x, 1, z, w.b("mossy_cobblestone"))
            w.setze(x, 2, z, w.b("black_candle" if i % 2 else "purple_candle", candles=3, lit=True, waterlogged=False))
    for s in (-1, 1):
        x = s * round(R + 5)
        for y in range(1, 4):
            w.setze(x, y, 0, _pf(w, f"{k.holz}_fence"))
        w.setze(x, 1, 1, w.b("hay_block", axis="y"))
    return w


def hexenbaumhaus(seed, g=2):
    """Knorriger Baum mit einer Hütte im Geäst, Hängebrücke aus Planken, Laternen und Krähenkäfig."""
    w = _welt(seed)
    k = Hexe(w, seed)
    u = U[g]
    _boden(w, 7 * u + 4, k.boden)
    S = Skulptur(w, u)
    S.mat("h", w.b(f"{k.holz}_log" if k.holz != "mangrove" else "mangrove_log", axis="y"))
    S.plus(kap((0, 0, 0), (0.8, 8, 0), 1.6, 1.0), "h")
    for i in range(4):
        a = i * math.pi / 2 + 0.4
        S.plus(kap((0, 1, 0), (math.cos(a) * 3.5, -0.3, math.sin(a) * 3.5), 1.0, 0.4), "h")
        S.plus(kap((0.8, 7, 0), (math.cos(a) * 4.5, 10.5, math.sin(a) * 4.5), 0.5, 0.25), "h")
    S.rendern((-7, -1, -7), (7, 12, 7), versatz=(0.5, 1, 0.5))
    yh = int(7 * u) + 1
    R = 2.2 * u + 1.2
    for x, z in scheibe(R + 1, 1, 0):
        w.setze(x, yh, z, w.b(f"{k.holz}_planks"))
    for y in range(yh + 1, yh + 4):
        for i, (x, z) in enumerate(kreisrand(R, 1, 0)):
            w.setze(x, y, z, k.glas if y == yh + 2 and i % 4 == 0 else w.b(f"{k.holz}_planks"), ueberschreiben=False)
    _hexenhut_dach(w, k, 1, 0, yh + 4, R, _r(R * 2.2, 4), knick=1.5)
    for y in range(1, yh):
        w.setze(1 + int(R) + 1, y, 0, w.b("ladder", facing="east", waterlogged=False))
    w.setze(-int(R), yh - 1, 0, w.b("soul_lantern", hanging=True, waterlogged=False))
    return w


def kraeutergarten(seed, g=1):
    """Hexen-Kräutergarten: Beete mit Pilzen, Beeren und Blumen, Vogelscheuche, Kürbisse und Zaun."""
    w = _welt(seed)
    k = Hexe(w, seed)
    u = U[g]
    L = _r(6 * u + 3, 4)
    _boden(w, L + 3, k.boden)
    pflanzen = ["red_mushroom", "brown_mushroom", "allium", "lily_of_the_valley", "blue_orchid", "fern"]
    for x in range(-L + 1, L):
        for z in range(-L + 1, L):
            if x % 3 == 0:
                w.setze(x, 0, z, w.b("dirt_path"))
            else:
                w.setze(x, 0, z, w.b("podzol", snowy=False))
                w.setze(x, 1, z, w.b(pflanzen[(x + 2 * z) % len(pflanzen)]) if (x + z) % 4 else
                        w.b("sweet_berry_bush", age=3))
    verbinde(w, [(x, 1, z) for x in range(-L, L + 1) for z in (-L, L)] +
             [(x, 1, z) for x in (-L, L) for z in range(-L + 1, L)], f"{k.holz}_fence")
    for y in range(1, 4):
        w.setze(0, y, 0, _pf(w, f"{k.holz}_fence"))
    w.setze(-1, 3, 0, _pf(w, f"{k.holz}_fence"))
    w.setze(1, 3, 0, _pf(w, f"{k.holz}_fence"))
    w.setze(0, 4, 0, w.b("carved_pumpkin", facing="south"))
    for x in (-L + 1, L - 1):
        w.setze(x, 1, L - 1, w.b("pumpkin"))
    return w


def hexenkreis(seed, g=1):
    """Hexenkreis: Ring aus Steinen und Kerzen, eingelegtes Pentagramm-freies Sternmuster aus Glimmstein,
    Totems und ein Altar."""
    w = _welt(seed)
    k = Hexe(w, seed)
    u = U[g]
    R = 5 * u + 3
    _boden(w, R + 3, k.boden)
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("blackstone") if math.hypot(x, z) > R - 1 else w.b("polished_blackstone"))
    for i in range(7):
        a = i * 2 * math.pi / 7
        for t in np.linspace(0, R - 1.5, int(R * 2)):
            w.setze(round(math.cos(a) * t), 0, round(math.sin(a) * t), w.b("crying_obsidian") if not k.sumpf
                    else w.b("verdant_froglight"))
    for i, (x, z) in enumerate(kreisrand(R + 1)):
        if i % 2 == 0:
            w.setze(x, 1, z, w.b("purple_candle" if not k.sumpf else "lime_candle", candles=4, lit=True,
                                 waterlogged=False))
        if i % 9 == 0:
            for y in range(1, _r(3 * u, 2) + 1):
                w.setze(x, y, z, w.b("mossy_cobblestone"))
            w.setze(x, _r(3 * u, 2) + 1, z, w.b("skeleton_skull", rotation=0))
    w.setze(0, 1, 0, w.b("lectern", facing="south", has_book=False, powered=False))
    return w


HEXEN = {
    "hexenhuette": ("Hexenhütte", hexenhuette),
    "alchemieturm": ("Alchemistenturm", alchemieturm),
    "kesselplatz": ("Kesselplatz", kesselplatz),
    "hexenbaumhaus": ("Hexenbaumhaus", hexenbaumhaus),
    "kraeutergarten": ("Kräutergarten", kraeutergarten),
    "hexenkreis": ("Hexenkreis", hexenkreis),
}


# ============================================================================ Drachenhort

def _drache(w, S, schuppe, bauch, horn, auge, haltung="liegend"):
    """Drachenkörper in Einheiten: Kopf bei +x."""
    S.mat("s", schuppe)
    S.mat("b", bauch)
    S.mat("h", horn)
    S.mat("a", auge)
    if haltung == "liegend":
        pts = [(-14, 1.5, 3), (-11, 1.8, 4.5), (-8, 2.8, 3.5), (-5, 4.5, 1), (-1, 5.5, 0), (3, 6, 0), (6, 9, 0), (8, 12, 0)]
    else:
        pts = [(-10, 2, -3), (-7, 4, -1), (-4, 6, 0), (-1, 7, 0), (2, 8, 0), (5, 10, 0), (7, 12.5, 0)]
    radien = [0.4, 0.8, 1.4, 2.3, 2.8, 2.4, 1.4, 1.1]
    for i in range(len(pts) - 1):
        S.plus(kap(pts[i], pts[i + 1], radien[i], radien[i + 1]), "s")
        if i > 1:
            mx = (pts[i][0] + pts[i + 1][0]) / 2
            my = (pts[i][1] + pts[i + 1][1]) / 2 + radien[i] * 0.9
            S.plus(kap((mx, my, 0), (mx - 0.6, my + 1.2, 0), 0.35, 0.1), "h")
    hx, hy, hz = pts[-1]
    S.plus(ell(hx + 1.3, hy + 0.3, hz, 2.0, 1.1, 1.0), "s")
    S.plus(ell(hx + 2.8, hy - 0.2, hz, 1.4, 0.6, 0.8), "s")
    S.plus(ell(hx + 1.5, hy - 0.4, hz, 1.5, 0.4, 0.8), "b")
    for s in (-1, 1):
        S.plus(ell(hx + 1.6, hy + 0.7, hz + s * 0.75, 0.3, 0.25, 0.2), "a")
        S.plus(kap((hx + 0.6, hy + 0.9, hz + s * 0.5), (hx - 1.4, hy + 2.4, hz + s * 1.0), 0.35, 0.1), "h")
    sx, sy, sz = pts[4]
    for s in (-1, 1):
        ell_ = (sx - 1, sy + 7, s * 7)
        S.plus(kap((sx, sy, s * 0.8), ell_, 0.55, 0.35), "s")
        spitzen = [(sx - 3 - 3.2 * f, sy + 5 - 2.4 * f, s * (8 + f * 1.0)) for f in range(4)]
        for sp in spitzen:
            S.plus(kap(ell_, sp, 0.35, 0.15), "s")
        ecken = [(sx, sy + 1)] + [(p[0], p[1]) for p in spitzen]
        for f in range(len(ecken) - 1):
            A, B, C = (ell_[0], ell_[1]), ecken[f], ecken[f + 1]

            def membran(X, Y, Z, A=A, B=B, C=C, s=s):
                d = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1])
                l1 = ((B[1] - C[1]) * (X - C[0]) + (C[0] - B[0]) * (Y - C[1])) / d
                l2 = ((C[1] - A[1]) * (X - C[0]) + (A[0] - C[0]) * (Y - C[1])) / d
                return (l1 >= 0) & (l2 >= 0) & (1 - l1 - l2 >= 0) & (np.abs(Z * s - 7.3) <= 0.6)
            S.plus(membran, "b")
    for (lx, lz) in ((pts[3][0], 2.0), (pts[3][0], -2.0), (pts[5][0], 2.2), (pts[5][0], -2.2)):
        S.plus(kap((lx, pts[4][1] - 1, lz * 0.5), (lx + 0.8, 0.5, lz * 1.4), 0.8, 0.6), "s")
        S.plus(kap((lx + 0.8, 0.5, lz * 1.4), (lx + 2.2, 0.3, lz * 1.5), 0.4, 0.2), "h")


def _drachenfarben(w, seed):
    if _stil(seed) == 0:
        return (Verlauf(w, "Rotschuppe", ["nether_wart_block", "red_concrete", "red_terracotta"]),
                Verlauf(w, "Bauch", ["orange_terracotta", "yellow_terracotta", "smooth_sandstone"]),
                w.b("bone_block", axis="y"), w.b("gold_block"))
    return (Verlauf(w, "Grünschuppe", ["dark_prismarine", "green_concrete", "waxed_oxidized_copper"]),
            Verlauf(w, "Bauch", ["lime_terracotta", "yellow_terracotta", "end_stone"]),
            w.b("bone_block", axis="y"), w.b("sea_lantern"))


def drachenstatue(seed, g=2):
    """Liegender Drache mit gespreizten Flügeln, Rückenstacheln, Hörnern und leuchtenden Augen auf einem Fels."""
    w = _welt(seed)
    u = U[g]
    schuppe, bauch, horn, auge = _drachenfarben(w, seed)
    fels = Verlauf(w, "Fels", ["blackstone", "basalt", "tuff", "andesite"])
    for x, z in scheibe(7 * u + 3):
        h = int((1 - math.hypot(x, z) / (7 * u + 3)) * 2 * u) + 1
        for y in range(0, h + 1):
            w.setze(x, y, z, fels(0.5 + w.rng.random() * 2, x, y, z))
    S = Skulptur(w, u * 0.75)
    _drache(w, S, lambda x, y, z, lx, ly, lz: schuppe(0.4 + w.rng.random() * 1.6 + 0.4 * ((x + z) % 2), x, y, z),
            lambda x, y, z, *_: bauch(1 + w.rng.random(), x, y, z), horn, auge)
    S.rendern((-17, -1, -14), (13, 16, 14), versatz=(0.5, 2 * u + 1, 0.5))
    return w


def drachennest(seed, g=1):
    """Riesiges Nest aus Stämmen und Zweigen auf einem Felsen, mit gefleckten Dracheneiern und Knochen."""
    w = _welt(seed)
    u = U[g]
    R = 6 * u + 3
    for x, z in scheibe(R + 2):
        for y in range(0, 2):
            w.setze(x, y, z, w.b("stone") if (x + z) % 3 else w.b("andesite"))
    for i in range(int(40 * u) + 20):
        a = w.rng.random() * 2 * math.pi
        r = R * (0.75 + 0.3 * w.rng.random())
        y = 2 + int(w.rng.random() * 2.5 * u)
        lang = 2 + int(w.rng.random() * 3 * u)
        for t in range(lang):
            w.setze(round(math.cos(a + t * 0.12) * r), y, round(math.sin(a + t * 0.12) * r),
                    w.b("spruce_log" if i % 2 else "dark_oak_log", axis="x" if abs(math.sin(a)) > 0.7 else "z"))
    for x, z in scheibe(R * 0.75):
        w.setze(x, 2, z, w.b("hay_block", axis="y") if (x + z) % 2 else w.b("coarse_dirt"))
    farben = [("red_terracotta", "yellow_terracotta"), ("green_terracotta", "lime_terracotta"),
              ("purple_terracotta", "magenta_terracotta"), ("blue_terracotta", "light_blue_terracotta")]
    for i in range(2 + g):
        a = i * 2.39996
        d = R * 0.4 * math.sqrt((i + 0.5) / (2 + g))
        cx, cz = math.cos(a) * d, math.sin(a) * d
        f1, f2 = farben[(i + _stil(seed) * 2) % 4]
        S = Skulptur(w, max(0.7, u * 0.6))
        S.mat("e", lambda x, y, z, *_: w.b(f2) if (x * 3 + y * 5 + z) % 7 == 0 else w.b(f1))
        S.plus(lambda X, Y, Z: (X * X + Z * Z) / 1.6 ** 2 + ((Y - 1.8) / (2.2 if True else 2)) ** 2 *
               np.where(Y > 1.8, 1.0, 1.4) <= 1, "e")
        S.rendern((-3, 0, -3), (3, 5, 3), versatz=(cx + 0.5, 2.5, cz + 0.5))
    for i in range(3):
        a = w.rng.random() * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        w.setze(x, 3, z, w.b("bone_block", axis="x"))
    return w


def hortgrotte(seed, g=2):
    """Felsgrotte mit Goldberg, Schatztruhen, Kelchen aus Gold, Knochen und glimmenden Kristallen."""
    w = _welt(seed)
    u = U[g]
    R = 9 * u + 4
    fels = Verlauf(w, "Höhle", ["deepslate", "cobbled_deepslate", "tuff", "stone"])
    S = Skulptur(w, 1.0)
    S.mat("f", lambda x, y, z, *_: fels(0.5 + w.rng.random() * 2.5, x, y, z))
    S.mat("g", lambda x, y, z, *_: [w.b("gold_block"), w.b("raw_gold_block"), w.b("gold_block"),
                                     w.b("yellow_terracotta")][(x * 3 + y + z * 5) % 4])
    S.plus(lambda X, Y, Z: ((X / R) ** 2 + (Y / (R * 0.7)) ** 2 + (Z / R) ** 2 <= 1) & (Y >= 0)
           & (((X / (R - 2)) ** 2 + (Y / (R * 0.7 - 2)) ** 2 + (Z / (R - 2)) ** 2) > 1), "f")
    S.minus(lambda X, Y, Z: (np.abs(X) < R * 0.3) & (Y < R * 0.4) & (Z > R * 0.5))
    S.plus(lambda X, Y, Z: (X / (R * 0.5)) ** 2 + (Y / (R * 0.22)) ** 2 + ((Z + R * 0.2) / (R * 0.45)) ** 2 <= 1, "g")
    S.rendern((-R - 1, 0, -R - 1), (R + 1, R, R + 1), versatz=(0.5, 0, 0.5))
    for i in range(3 + g):
        a = i * 2.1
        x, z = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        w.setze(x, 1, z, w.b("chest", facing="south", type="single", waterlogged=False))
    for i in range(4 + g):
        a = i * 1.7 + 0.4
        x, z = round(math.cos(a) * (R - 2.5)), round(math.sin(a) * (R - 2.5))
        w.setze(x, int(R * 0.35), z, w.b("amethyst_cluster", facing="up", waterlogged=False), ueberschreiben=False)
    for i in range(3):
        w.setze(round(R * 0.3) - i, 1, round(R * 0.3), w.b("bone_block", axis="x"))
    return w


def drachenturm(seed, g=2):
    """Turm mit ausladender Drachenplattform an der Spitze, Krallenspuren, Ketten und Feuerschalen."""
    w = _welt(seed)
    u = U[g]
    from bau import turm_rund
    st = Stil(w, Verlauf(w, "Stein", ["cobbled_deepslate", "deepslate_bricks", "polished_blackstone_bricks",
                                      "deepslate_tiles"]), holz="dark_oak", dach="deepslate_tile",
              dach_voll="deepslate_tiles")
    R = 2.6 * u + 1.6
    H = _r(16 * u + 6, 10)
    _boden(w, R + 8, lambda x, z: w.b("coarse_dirt") if w.rng.random() < 0.4 else w.b("grass_block", snowy=False))
    for y in range(0, H):
        for i, (x, z) in enumerate(kreisrand(R)):
            kralle = (y % 7 in (2, 3, 4)) and i % 9 in (0, 1) and (y - 2 - i % 2) % 2 == 0
            w.setze(x, y, z, w.b("polished_blackstone") if kralle else st.wandblock(x, y, z, 0.5 + 2 * y / H))
    Rp = R + 4 * u + 2
    for x, z in scheibe(Rp):
        w.setze(x, H, z, w.b("polished_blackstone_bricks") if math.hypot(x, z) > Rp - 1.2 else w.b("polished_deepslate"))
    for x, z in kreisrand(Rp + 0.8):
        w.setze(x, H - 1, z, treppe(w, "polished_blackstone_brick", zur_mitte(x, z), "top"))
    for i, (x, z) in enumerate(kreisrand(Rp)):
        if i % 6 == 0:
            for y in range(H + 1, H + 3):
                w.setze(x, y, z, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                                     west="none", waterlogged=False))
            w.setze(x, H + 3, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for i in range(4):
        a = i * math.pi / 2 + 0.4
        for k in range(_r(4 * u, 3)):
            w.setze(round(math.cos(a) * Rp), H - 1 - k, round(math.sin(a) * Rp), w.b("chain", axis="y", waterlogged=False))
    return w


def schaedeltor(seed, g=2):
    """Tor in Form eines gewaltigen Drachenschädels: man geht durch das offene Maul."""
    w = _welt(seed)
    u = U[g]
    _boden(w, 9 * u + 4, lambda x, z: w.b("coarse_dirt") if w.rng.random() < 0.5 else w.b("gravel"))
    S = Skulptur(w, u)
    S.mat("k", lambda x, y, z, *_: w.b("bone_block", axis="y") if (x + y + z) % 5 else w.b("calcite"))
    S.mat("a", w.b("shroomlight") if _stil(seed) == 0 else w.b("sea_lantern"))
    S.plus(ell(0, 7.5, -1, 5, 3.6, 5.5), "k")
    S.plus(lambda X, Y, Z: ((X / 4.2) ** 2 + ((Y - 5.4) / 1.4) ** 2 <= 1) & (Z > 0) & (Z < 7), "k")
    S.plus(lambda X, Y, Z: ((X / 4.0) ** 2 + ((Y - 0.8) / 1.0) ** 2 <= 1) & (Z > 0) & (Z < 6.5), "k")
    S.minus(lambda X, Y, Z: (np.abs(X) < 2.6) & (Y < 4.8) & (Y > 0) & (Z < 9))
    for x in (-3.2, -1.6, 0, 1.6, 3.2):
        S.plus(kap((x, 4.4, 5.8), (x, 3.2, 6.0), 0.35, 0.1), "k")
    for s in (-1, 1):
        S.minus(ell(s * 2.4, 8.5, 3.5, 1.2, 1.0, 1.4))
        S.plus(ell(s * 2.4, 8.5, 2.6, 0.6, 0.5, 0.5), "a")
        S.plus(kap((s * 3.5, 10, -2), (s * 7.5, 14, -5), 1.0, 0.25), "k")
    S.rendern((-9, 0, -8), (9, 15, 9), versatz=(0.5, 1, 0.5))
    return w


def fliegender_drache(seed, g=2):
    """Drache im Steigflug als Statue auf einer gewundenen Felssäule."""
    w = _welt(seed)
    u = U[g]
    schuppe, bauch, horn, auge = _drachenfarben(w, seed)
    fels = Verlauf(w, "Fels", ["blackstone", "basalt", "tuff", "andesite"])
    H = _r(8 * u + 3, 5)
    for y in range(0, H + 1):
        r = (2.5 * u + 1) * (1 - 0.4 * y / H)
        ox = math.sin(y * 0.3) * u
        for x, z in scheibe(r):
            w.setze(round(x + ox), y, z, fels(0.5 + 2 * y / H + w.rng.random() * 0.6, x, y, z))
    S = Skulptur(w, u * 0.75)
    _drache(w, S, lambda x, y, z, *_: schuppe(0.4 + w.rng.random() * 1.6, x, y, z),
            lambda x, y, z, *_: bauch(1 + w.rng.random(), x, y, z), horn, auge, haltung="steigend")
    S.rendern((-13, 0, -14), (12, 18, 14), versatz=(0.5, H - 1.5 * u, 0.5))
    return w


DRACHEN = {
    "drachenstatue": ("Drachenstatue", drachenstatue),
    "drachennest": ("Drachennest", drachennest),
    "hortgrotte": ("Hortgrotte", hortgrotte),
    "drachenturm": ("Drachenturm", drachenturm),
    "schaedeltor": ("Drachenschädel-Tor", schaedeltor),
    "fliegender_drache": ("Fliegender Drache", fliegender_drache),
}


# ============================================================================ Himmelsreich

def wolke(w, cx, cy, cz, r, u=1.0):
    """Bauschige Wolke aus weißer Wolle, weißem Beton und Pulverschnee-Optik."""
    S = Skulptur(w, 1.0)
    S.mat("w", lambda x, y, z, *_: w.b("white_wool") if (x + y * 2 + z) % 4 else w.b("white_concrete"))
    for i in range(7):
        a = i * 2.39996
        d = r * 0.55 * math.sqrt((i + 0.5) / 7)
        rr = r * (0.55 + 0.25 * ((i * 5) % 3) / 2)
        S.plus(ell(math.cos(a) * d, rr * 0.1, math.sin(a) * d, rr, rr * 0.55, rr), "w")
    S.rendern((-r * 2, -r, -r * 2), (r * 2, r, r * 2), versatz=(cx + 0.5, cy, cz + 0.5), ueberschreiben=False)


class Himmel:
    def __init__(self, w, seed):
        self.w = w
        self.sonne = _stil(seed) == 0
        self.stein = Verlauf(w, "Himmelsmarmor", ["polished_diorite", "calcite", "smooth_quartz", "white_concrete"])
        self.gold = w.b("gold_block") if self.sonne else w.b("light_blue_concrete")
        self.akzent = w.b("yellow_stained_glass") if self.sonne else w.b("light_blue_stained_glass")


def himmelstor(seed, g=2):
    """Himmelstor auf Wolken: zwei hohe Marmorsäulen, Goldtor mit Strahlenkranz, Wolkenstufen."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    yw = _r(6 * u + 4, 6)
    wolke(w, 0, yw, 0, 9 * u + 4)
    H = _r(10 * u + 4, 7)
    b = _r(3 * u + 1.5, 3)
    y0 = yw + 2
    for s in (-1, 1):
        for y in range(y0, y0 + H):
            for dx in range(_r(u, 1)):
                w.setze(s * (b + dx), y, 0, w.b("quartz_pillar", axis="y"))
        w.setze(s * b, y0 + H, 0, k.gold)
    for x in range(-b, b + 1):
        for y in range(y0 + H - 2, y0 + H + 1):
            w.setze(x, y, 0, k.stein(2.5, x, y, 0))
    R = b + 1.5
    cy = y0 + H + 1
    for i in range(16):
        a = i * math.pi / 15
        for t in np.linspace(R * 0.5, R * (1.4 if i % 2 else 1.1), int(R)):
            w.setze(round(math.cos(a) * t), round(cy + math.sin(a) * t), 0, k.gold if i % 2 else k.akzent)
    for x in range(-b + 1, b):
        for y in range(y0, y0 + H - 2):
            if (x + y) % 2 == 0:
                w.setze(x, y, 0, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False)
                        if k.sonne else w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
    w.anker = (0, 0, 0)
    return w


def wolkenpalast(seed, g=2):
    """Palast auf einer großen Wolke: weißer Marmor, goldene Kuppeln, Säulengänge und Türmchen."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    yw = _r(8 * u + 4, 6)
    R = 12 * u + 6
    wolke(w, 0, yw, 0, R)
    y0 = yw + int(R * 0.35)
    h = _r(5 * u + 2, 4)
    H = _r(5 * u + 3, 4)
    for y in range(y0, y0 + H + 1):
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                if max(abs(x), abs(z)) == h or y in (y0, y0 + H):
                    fen = max(abs(x), abs(z)) == h and (x % 2 == 0 or z % 2 == 0) and y0 < y < y0 + H - 1
                    w.setze(x, y, z, k.akzent if fen else k.stein(1 + w.rng.random(), x, y, z))
    kuppel = Verlauf(w, "Kuppel", ["gold_block", "yellow_concrete", "gold_block"]) if k.sonne else \
        Verlauf(w, "Kuppel", ["light_blue_concrete", "white_concrete", "light_blue_terracotta"])
    for x in range(-h, h + 1):
        for z in range(-h, h + 1):
            for y in range(0, h + 1):
                d = (x * x + z * z) / h ** 2 + (y / (h * 1.1)) ** 2
                if 0.65 < d <= 1:
                    w.setze(x, y0 + H + 1 + y, z, kuppel(1 + w.rng.random(), x, y, z))
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * (h + 2), sz * (h + 2)
            for y in range(y0, y0 + H + _r(4 * u, 3)):
                for x, z in kreisrand(1.1 * u + 0.6, cx, cz):
                    w.setze(x, y, z, k.stein(1.5, x, y, z))
            for kk in range(_r(2 * u + 1, 2)):
                for x, z in scheibe(max(0.3, 1.1 * u + 0.9 - kk), cx, cz):
                    w.setze(x, y0 + H + _r(4 * u, 3) + kk, z, kuppel(1, x, 0, z))
    w.anker = (0, 0, 0)
    return w


def engelsstatue(seed, g=2):
    """Engelsstatue mit weit geöffneten Flügeln und erhobenem Schwert auf einer Wolke."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    yw = _r(3 * u + 2, 3)
    wolke(w, 0, yw, 0, 6 * u + 3)
    S = Skulptur(w, u)
    S.mat("k", lambda x, y, z, lx, ly, lz: k.stein(0.4 + ly / 8, x, y, z))
    S.mat("f", lambda x, y, z, lx, ly, lz: [w.b("white_concrete"), w.b("smooth_quartz"), w.b("calcite"),
                                             w.b("polished_diorite")][int(abs(ly - 14) / 2) % 4])
    S.mat("g", k.gold)
    S.mat("a", k.akzent)
    dick = S.dicke(0.45)

    def fluegel(X, Y, Z):
        xw = np.abs(X)
        t = np.clip((xw - 1.4) / 10, 0, 1)
        yt = 14 + 6 * np.sin(t * math.pi * 0.8)
        yb = 9 + 6 * t * t - 1.4 * np.abs(np.sin(t * math.pi * 5))
        return (xw > 1.4) & (xw < 11.4) & (Y < yt) & (Y > yb) & (np.abs(Z + 1.6 + 1.2 * t) <= dick)
    S.plus(fluegel, "f")
    S.plus(kegel(0, 0, 0, 10, 2.8, 1.5, zf=0.8), "k")
    S.plus(kap((0, 10, 0), (0, 13.5, 0), 1.6, 1.9, zf=0.7), "k")
    S.plus(ell(0, 15.3, 0, 1.2, 1.4, 1.2), "k")
    S.plus(kap((1.8, 13, 0), (2.4, 16.5, 0.8), 0.7), "k")
    S.plus(kap((2.4, 16.5, 0.8), (2.4, 23, 0.8), 0.3), "a")
    S.plus(kap((1.6, 16.8, 0.8), (3.2, 16.8, 0.8), 0.3), "g")
    S.plus(kap((-1.8, 13, 0), (-1.2, 10, 1.2), 0.65), "k")
    from skulptur import torus
    S.plus(torus(0, 16.4, -0.6, 1.5, S.dicke(0.25), "z"), "g")
    S.rendern((-12, 0, -5), (12, 24, 4), versatz=(0.5, yw + 2, 0.5))
    w.anker = (0, 0, 0)
    return w


def wolkeninsel(seed, g=1):
    """Kleine Wolkeninsel mit Pavillon aus Marmor und Gold und einem Regenbogen darüber."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    yw = _r(6 * u + 4, 5)
    R = 7 * u + 3
    wolke(w, 0, yw, 0, R)
    y0 = yw + int(R * 0.35)
    r = 2 * u + 1.5
    for i, (x, z) in enumerate(kreisrand(r)):
        if i % 3 == 0:
            for y in range(y0, y0 + _r(3 * u + 1, 3)):
                w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    yt = y0 + _r(3 * u + 1, 3)
    for kk in range(int(r) + 2):
        for x, z in kreisrand(max(0.3, (r + 0.8) * (1 - kk / (r + 2)))):
            w.setze(x, yt + kk, z, k.gold)
    farben = ["red_wool", "orange_wool", "yellow_wool", "lime_wool", "light_blue_wool", "blue_wool", "purple_wool"]
    Rb = R * 1.1
    for i, f in enumerate(farben):
        rr = Rb - i * max(1, int(u * 0.6))
        for t in np.linspace(0, math.pi, int(rr * 4)):
            w.setze(round(math.cos(t) * rr), round(yw + math.sin(t) * rr * 0.9), -int(R * 0.4), w.b(f),
                    ueberschreiben=False)
    w.anker = (0, 0, 0)
    return w


def regenbogenbruecke(seed, g=2):
    """Regenbogenbrücke zwischen zwei Wolken – begehbar, mit Geländer aus Glas."""
    w = _welt(seed)
    u = U[g]
    L = _r(16 * u + 6, 10)
    yw = _r(4 * u + 3, 4)
    for s in (-1, 1):
        wolke(w, s * L, yw, 0, 4 * u + 3)
    farben = ["red_concrete", "orange_concrete", "yellow_concrete", "lime_concrete", "light_blue_concrete",
              "blue_concrete", "purple_concrete"]
    for x in range(-L, L + 1):
        y = yw + int(round((1 - (x / L) ** 2) * (5 * u + 2))) + 1
        for i, f in enumerate(farben):
            z = i - 3
            w.setze(x, y, z, w.b(f))
        for z in (-4, 4):
            w.setze(x, y + 1, z, w.b("white_stained_glass_pane" if False else "glass_pane", north=False, south=False,
                                     east=True, west=True, waterlogged=False))
    w.anker = (0, 0, 0)
    return w


def sonnentempel(seed, g=2):
    """Runder Sonnentempel aus Marmor mit Säulenkranz, goldener Sonnenscheibe und Strahlen."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    R = 6 * u + 3
    yw = _r(5 * u + 3, 5)
    wolke(w, 0, yw, 0, R + 4)
    y0 = yw + int((R + 4) * 0.35)
    for x, z in scheibe(R + 1):
        w.setze(x, y0, z, k.stein(1.5, x, y0, z))
    H = _r(5 * u + 3, 4)
    for i, (x, z) in enumerate(kreisrand(R)):
        if i % 3 == 0:
            for y in range(y0 + 1, y0 + H):
                w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    for x, z in kreisrand(R + 0.5):
        w.setze(x, y0 + H, z, k.stein(2.5, x, y0 + H, z))
    Rs = R * 0.55
    cy = y0 + H + Rs + 2
    for x in range(-int(Rs * 1.8), int(Rs * 1.8) + 1):
        for y in range(-int(Rs * 1.8), int(Rs * 1.8) + 1):
            d = math.hypot(x, y)
            a = math.atan2(y, x)
            if d <= Rs:
                w.setze(x, int(cy) + y, 0, k.gold if d > Rs - 1.2 or d < 1 else w.b("yellow_concrete") if k.sonne
                        else w.b("light_blue_concrete"))
            elif d <= Rs * 1.8 and abs(math.sin(a * 6)) < 0.18:
                w.setze(x, int(cy) + y, 0, k.akzent)
    w.anker = (0, 0, 0)
    return w


HIMMEL = {
    "himmelstor": ("Himmelstor", himmelstor),
    "wolkenpalast": ("Wolkenpalast", wolkenpalast),
    "engelsstatue": ("Engelsstatue", engelsstatue),
    "wolkeninsel": ("Wolkeninsel", wolkeninsel),
    "regenbogenbruecke": ("Regenbogenbrücke", regenbogenbruecke),
    "sonnentempel": ("Sonnentempel", sonnentempel),
}

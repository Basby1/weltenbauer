"""Zwergenreich II – zwanzig weitere Zwergenbauten: Lorenbahnhof, Steinerner Zwergenkönig, Edelsteinschleiferei,
Schachtaufzug, Untertage-Markt, Zwergentaverne am Fels, Silberader-Stollen, Runenschmiede, Geodenkeller, Thermen der
Tiefe, Klammhammer, Felsbastion, Archiv der Runen, Königsgruft, Lüftungsschlote, Grottensee mit Fischern, Waffen-
kammer der Clans, Steingolem-Wächter, Tresorkammer und Laternenkluft."""

from __future__ import annotations

import math

import numpy as np

from erw_basis import M, S, figur, haus, hoehe, wiese
from feinbau import Dachmat, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen
from skulptur import Skulptur, dreh_y, ell, kap, kasten, kegel, kreisrand


def zwergstein(w):
    return M(w, [("stone_bricks", 3), ("deepslate_bricks", 2), ("polished_deepslate", 1), ("cracked_stone_bricks", 1)])


def fels(w):
    return M(w, [("stone", 3), ("andesite", 2), ("deepslate", 1), ("tuff", 1)])


def berg(w, R, H, cx=0, cz=0, zf=0):
    """Steile Felswand (hinter z=zf) mit grasbewachsener Kuppe, davor ein flacher Vorplatz; gibt Höhen zurück."""
    rn = Rauschen(w, 5)
    f = fels(w)
    rng = w.rng
    zellen = {}
    for x in range(cx - R - 2, cx + R + 3):
        for z in range(cz - R - 2, cz + R + 3):
            if math.hypot(x - cx, z - cz) > R + 2 * rn(x, 0, z):
                continue
            if z - cz <= zf + round(rn(x, 7, 0) * 1.2):
                rand = 1 - (math.hypot(x - cx, z - cz) / (R + 2)) ** 4
                h = int(H * (0.75 + 0.25 * rand) + rn(x, 3, z) * 3)
            else:
                h = int(rn(x, 3, z) * 1.3)
            for y in range(-1, h + 1):
                if y == h:
                    blk = w.b("grass_block", snowy=False) if rn(x, 9, z) < 0.8 else w.b("coarse_dirt")
                else:
                    blk = f(x, y, z)
                    if h > 3 and rng.random() < 0.025:
                        blk = w.b(["iron_ore", "copper_ore", "coal_ore", "mossy_cobblestone"][int(rng.integers(4))])
                w.setze(x, y, z, blk)
            if h <= 1 and rng.random() < 0.08:
                w.setze(x, h + 1, z, w.b("grass") if rng.random() < 0.8 else w.b("fern"))
            zellen[(x, z)] = h
    return zellen


def halle(w, x0, x1, z0, z1, y0, H, boden=None, gewoelbe=True, front=True, stil=0):
    """Hohlraum (Halle) in den Fels gehauen, vorn (z1) mit Säulenfassade; gibt die Deckenhöhe zurück."""
    st = zwergstein(w)
    boden = boden or M(w, [("polished_deepslate", 2), ("deepslate_tiles", 1)])
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, y0 - 1, z, boden(x, y0, z))
            rel = (x - (x0 + x1) / 2) / ((x1 - x0) / 2 + 0.5)
            hh = int(H * (math.sqrt(max(0, 1 - rel * rel)) if gewoelbe else 1))
            for y in range(y0, y0 + max(3, hh)):
                w.bloecke.pop((x, y, z), None)
            if x in (x0, x1) or z == z0:
                for y in range(y0, y0 + max(3, hh)):
                    w.setze(x, y, z, st(x, y, z))
            w.setze(x, y0 + max(3, hh), z, st(x, y0 + hh, z))
    if front:
        zf = z1 + 1
        Hf = max(3, int(H * 0.75))
        sp, wand, kopf, treppe_ = [(3, "deepslate_brick_wall", "chiseled_deepslate", "deepslate_brick_stairs"),
                                   (4, "stone_brick_wall", "chiseled_stone_bricks", "stone_brick_stairs"),
                                   (5, "polished_blackstone_wall", "gilded_blackstone", "polished_blackstone_stairs"),
                                   (4, "andesite_wall", "polished_andesite", "andesite_stairs")][stil % 4]
        for x in range(x0 - 1, x1 + 2):
            w.setze(x, y0 - 1, zf, w.b("polished_deepslate"))
            if (x - x0) % sp == 0 or x in (x0 - 1, x1 + 1):
                for y in range(y0, y0 + Hf):
                    w.setze(x, y, zf, w.b(wand, up=True, north="none", south="none", east="none",
                                          west="none", waterlogged=False) if 0 < y - y0 < Hf - 1 and
                            x not in (x0 - 1, x1 + 1) else w.b(kopf) if y == y0 else st(x, y, zf))
            for y in range(y0 + Hf, y0 + Hf + 2):
                w.setze(x, y, zf, w.b("chiseled_stone_bricks") if (y - y0 - Hf) == 1 and x % 2 == 0 else
                        st(x, y, zf))
            if (x - x0) % sp and x not in (x0 - 1, x1 + 1):
                w.setze(x, y0 + Hf - 1, zf, w.b(treppe_, facing="north", half="top", shape="straight",
                                                waterlogged=False))
        cx = (x0 + x1) // 2
        for d in range(-1, 2):
            w.setze(cx + d, y0 + Hf + 2, zf, w.b("gold_block") if d == 0 else w.b("chiseled_stone_bricks"))
        w.setze(cx, y0 + Hf + 3, zf, w.b("chiseled_stone_bricks"))
        for sx in (x0 - 1, x1 + 1):
            laterne(w, sx, y0 + Hf, zf + 1, kette=0)
    return y0 + H


def portal(w, cx, z, y0, B, H, mat=None):
    st = mat or zwergstein(w)
    for x in range(cx - B - 2, cx + B + 3):
        for y in range(y0, y0 + H + 3):
            innen = abs(x - cx) <= B and y < y0 + H
            if not innen and (abs(x - cx) <= B + 2):
                w.setze(x, y, z, st(x, y, z))
            elif innen:
                for zz in range(z - 4, z + 1):
                    w.bloecke.pop((x, y, zz), None)
    for x in range(cx - B - 2, cx + B + 3):
        w.setze(x, y0 + H + 3, z, w.b("chiseled_stone_bricks") if (x - cx) % 3 == 0 else w.b("gold_block")
                if x == cx else st(x, y0 + H + 3, z))
    for sx in (-1, 1):
        laterne(w, cx + sx * (B + 1), y0 + H, z + 1, kette=1)


def zwerg(w, bart="orange_wool", rock="blue_wool", helm="iron_block"):
    return [(kap((0, 0, 0), (0, 1.8, 0), 0.75, 0.7), w.b("brown_wool")), (ell(0, 2.4, 0, 0.9, 0.9, 0.8), w.b(rock)),
            (ell(0, 3.5, 0, 0.6, 0.6, 0.6), w.b("white_terracotta")),
            (ell(0.45, 3.0, 0, 0.35, 0.8, 0.45), w.b(bart)), (ell(0, 4.0, 0, 0.62, 0.35, 0.62), w.b(helm)),
            (kap((0, 2.6, 0.9), (0.6, 1.8, 1.2), 0.25), w.b(rock)), (kap((0, 2.6, -0.9), (0.6, 1.8, -1.2), 0.25), w.b(rock))]


# ============================================================================ Bauten

def lorenbahnhof(seed, g=2):
    """Lorenbahnhof: an einem Berghang münden mehrere Stollen mit Gleisen in einen überdachten Bahnhof mit Weichen,
    Prellböcken und Loren voller Erz, ein Stellwerk mit Hebeln und eine Laterne über jedem Tunnel."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    H = int(10 * s + 6)
    zellen = berg(w, R, H)
    zt = 1
    for k in range(3):
        x = -int(R * 0.45) + k * int(R * 0.45)
        portal(w, x, zt, 1, 1, 3)
        for z in range(zt - 3, int(R * 0.6)):
            w.setze(x, 1, z, w.b("rail", shape="north_south", waterlogged=False))
            w.setze(x, 0, z, w.b("polished_andesite"))
        w.setze(x, 1, int(R * 0.6), w.b("stone_bricks"))
        w.setze(x, 2, zt + 3 + k, w.b("raw_iron_block") if k % 2 else w.b("raw_gold_block"))
        w.setze(x, 1, zt + 3 + k, w.b("rail", shape="north_south", waterlogged=False))
    for x in range(-int(R * 0.55), int(R * 0.55) + 1):
        for z in range(zt + 4, zt + 10):
            w.setze(x, 5, z, w.b("spruce_slab", type="bottom", waterlogged=False))
        if x % 4 == 0:
            for z in (zt + 4, zt + 9):
                for y in range(1, 5):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
    sx = int(R * 0.65)
    haus(w, sx, zt + 6, 4, 4, 1, zwergstein(w), holz="spruce", H=3, dach=("deepslate_tile",), tuer_s="west",
         schorn=False)
    for k in range(3):
        w.setze(sx - 1 + k, 1, zt + 9, w.b("lever", face="floor", facing="north", powered=k == 1))
    _ = zellen
    return w


def zwergenkoenig_statue(seed, g=2):
    """Steinerner Zwergenkönig: eine kolossale, sitzende Statue eines bärtigen Zwergenkönigs mit Krone und auf die
    Knie gelegter Kriegsaxt, aus der Bergflanke gemeißelt, zu seinen Füßen ein Treppenplatz mit Feuerschalen."""
    w = _neu(seed)
    s = S[g]
    u = 1.0 * s + 0.6
    R = int(10 * u + 6)
    zellen = berg(w, R, int(18 * u + 5), zf=-int(2 * u))
    for x in range(-int(7 * u) - 1, int(7 * u) + 2):
        for z in range(-int(6 * u) - 1, 1):
            for y in range(1, int(19 * u)):
                if (abs(x) / (7 * u + 1.5)) ** 2 + max(0, y - 12 * u) ** 2 / (7 * u) ** 2 < 1:
                    w.bloecke.pop((x, y, z), None)
    st = M(w, [("stone", 3), ("andesite", 2), ("polished_andesite", 1)])
    Sk = Skulptur(w, u)
    Sk.mat("s", lambda x, y, z, *a: st(x, y, z))
    Sk.mat("b", lambda x, y, z, *a: w.b("polished_andesite") if (x + y) % 2 else w.b("smooth_stone"))
    Sk.mat("g", w.b("gold_block"))
    Sk.mat("e", w.b("iron_block"))
    Sk.plus(kasten(-5, 0, -4, 5, 4, 2), "s")
    Sk.plus(ell(0, 7, -1.5, 3.6, 4, 2.8), "s")
    for sx in (-1, 1):
        Sk.plus(kap((sx * 1.8, 4.5, 0), (sx * 1.8, 4.5, 3.5), 1.4, 1.3), "s")
        Sk.plus(kap((sx * 1.8, 4.5, 3.5), (sx * 1.8, 0.5, 3.8), 1.2, 1.1), "s")
        Sk.plus(ell(sx * 1.8, 0.6, 4.6, 1.2, 0.6, 1.4), "s")
        Sk.plus(kap((sx * 3.6, 9.5, -1.5), (sx * 3.2, 6.0, 2.0), 0.9, 0.8), "s")
        Sk.plus(ell(sx * 2.4, 5.8, 3.0, 0.9, 0.7, 0.8), "s")
    Sk.plus(ell(0, 12.2, -1.0, 2.0, 2.2, 2.0), "s")
    Sk.plus(ell(0, 9.8, 0.4, 2.2, 3.2, 1.4), "b")
    Sk.plus(kap((0, 8.2, 1.0), (0, 5.2, 2.2), 1.0, 0.4), "b")
    Sk.plus(kegel(0, -1.0, 13.8, 15.4, 1.9, 1.6), "g")
    for i in range(5):
        a = i / 5 * 2 * math.pi
        Sk.plus(kegel(math.cos(a) * 1.6, -1.0 + math.sin(a) * 1.6, 15.2, 16.6, 0.35, 0.05), "g")
    Sk.plus(kap((-4.5, 5.6, 3.2), (4.5, 5.6, 3.2), 0.35), "e")
    Sk.plus(lambda X, Y, Z: ((X - 4.6) ** 2 / 0.3 + (Y - 5.6) ** 2 / 4 + (Z - 3.2) ** 2 / 2 <= 1), "e")
    Sk.rendern((-6, -1, -5), (6, 17, 6), versatz=(0.5, 1, -int(1 * u) + 0.5))
    for k in range(3):
        for x in range(-int(5 * u) - 2 + k, int(5 * u) + 3 - k):
            w.setze(x, 1 + k, int(R * 0.35) - k, w.b("stone_brick_stairs", facing="south", half="bottom",
                                                       shape="straight", waterlogged=False))
    for sx in (-1, 1):
        x = sx * int(5 * u + 2)
        w.setze(x, 1, int(R * 0.35), w.b("chiseled_stone_bricks"))
        w.setze(x, 2, int(R * 0.35), w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    _ = zellen
    return w


def schleiferei(seed, g=1):
    """Edelsteinschleiferei: eine in den Fels gebaute Werkstatt mit großen, wasserbetriebenen Schleifscheiben, Werk-
    bänken voller funkelnder Edelsteine (Smaragd, Diamant, Amethyst) und Lupenständern."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    berg(w, R, int(8 * s + 5))
    B = int(4 * s + 4)
    halle(w, -B, B, -int(R * 0.45), 0, 1, int(4 * s + 4), stil=1)
    rng = w.rng
    for k in range(2 + g):
        x = -B + 2 + k * 3
        w.setze(x, 1, -2, w.b("grindstone", face="floor", facing="north"))
        w.setze(x, 1, -1, w.b("water_cauldron", level=3))
    for x in range(-B + 1, B):
        w.setze(x, 1, -int(R * 0.45) + 1, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x, 2, -int(R * 0.45) + 1, w.b(["emerald_block", "diamond_block", "amethyst_cluster", "lapis_block"]
                                              [x % 4], **({"facing": "up", "waterlogged": False} if x % 4 == 2 else {})))
    for k in range(5):
        x, z = int((rng.random() - 0.5) * 2 * B), -int(rng.random() * R * 0.4)
        if w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("amethyst_cluster", facing="up", waterlogged=False))
    for sx in (-1, 1):
        laterne(w, sx * (B - 1), int(4 * s + 3), -2, kette=1)
    return w


def schachtaufzug(seed, g=2):
    """Schachtaufzug: ein hoher, offener Förderkorb-Schacht an einer senkrechten Felswand, mit Holzgerüst, Seilrad oben,
    Gegengewicht und Plattformen auf drei Ebenen, die zu Stollen führen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    H = int(16 * s + 10)
    rn = Rauschen(w, 4)
    f = fels(w)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            h = H + int(rn(x, 3, z) * 3) if z < -2 else int(rn(x, 4, z) * 2)
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else f(x, y, z))
    for y in range(1, H + 4):
        for dx in (-2, 2):
            for dz in (-1, 3):
                w.setze(dx, y, dz, w.b("spruce_log", axis="y"))
        if y % 5 == 0:
            for dx in range(-2, 3):
                w.setze(dx, y, -1, w.b("spruce_planks"))
                w.setze(dx, y, 3, w.b("spruce_planks"))
    from erw_uhrwerk import zahnrad
    zahnrad(w, 0, H + 4, 1, 2 + s, ebene="zy", mat="spruce_planks", zahn="spruce_fence", nabe="iron_block")
    yk = int(H * 0.45)
    for dx in (-1, 0, 1):
        for dz in (0, 1, 2):
            w.setze(dx, yk, dz, w.b("spruce_planks"))
            if abs(dx) == 1:
                w.setze(dx, yk + 1, dz, w.b("iron_bars", waterlogged=False))
    for y in range(yk + 1, H + 3):
        w.setze(0, y, 1, w.b("chain", axis="y", waterlogged=False))
    for lvl in (1, int(H * 0.5), H - 2):
        portal(w, -4, -2, lvl, 1, 3)
        for x in range(-4, -1):
            w.setze(x, lvl - 1, 0, w.b("spruce_planks"))
    return w


def untertagemarkt(seed, g=2):
    """Untertage-Markt: eine gewaltige, von Säulen getragene Höhlenhalle, in der Zwergenhändler an Steinständen Erze,
    Waffen, Pilzbrot und Fässer feilbieten, beleuchtet von hängenden Laternen und einem Lichtschacht."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    berg(w, R, int(12 * s + 6))
    B = int(R * 0.7)
    top = halle(w, -B, B, -int(R * 0.65), 0, 1, int(8 * s + 5), stil=2)
    st = zwergstein(w)
    for x in range(-B + 3, B - 2, 5):
        for z in (-int(R * 0.45), -int(R * 0.15)):
            for y in range(1, top):
                if w.frei(x, y, z):
                    w.setze(x, y, z, st(x, y, z))
    waren = ["raw_iron_block", "barrel", "iron_block", "brown_mushroom_block", "raw_gold_block", "anvil"]
    rng = w.rng
    n = int(4 + 2 * s)
    for k in range(n):
        x = -B + 3 + k * int(2 * B / n)
        z = -int(R * 0.3)
        for dx in (-1, 0, 1):
            w.setze(x + dx, 1, z, w.b("polished_deepslate_slab", type="top", waterlogged=False))
        ware = waren[k % 6]
        pr = {"barrel": {"facing": "up", "open": False}, "anvil": {"facing": "east"},
              "brown_mushroom_block": {"north": True, "south": True, "east": True, "west": True, "up": True,
                                       "down": True}}.get(ware, {})
        w.setze(x, 2, z, w.b(ware, **pr))
        figur(w, 0.45 * s + 0.3, zwerg(w, ["orange_wool", "white_wool", "brown_wool"][k % 3],
                                        ["blue_wool", "red_wool", "green_wool"][k % 3]), (-2, -1, -2), (2, 5, 2),
              pos=(x, 1, z - 2), winkel=math.pi / 2)
    for k in range(int(6 * s)):
        x, z = int((rng.random() - 0.5) * 2 * B), -int(rng.random() * R * 0.6)
        y = top - 1
        while y > 2 and w.frei(x, y, z):
            y -= 1
        laterne(w, x, top - 2, z, kette=2)
    return w


def taverne(seed, g=1):
    """Zwergentaverne am Fels: eine Schänke halb in den Felsen gebaut, mit Steinfront, Rundtür, Fassdaube-Vordach,
    riesigen Bierfässern als Außentische, einem Schild mit Krug und Laternen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    berg(w, R, int(8 * s + 5))
    B = int(3 * s + 4)
    halle(w, -B, B, -int(R * 0.4), 0, 1, int(3 * s + 3), gewoelbe=False, front=False)
    st = zwergstein(w)
    for x in range(-B, B + 1):
        for y in range(1, int(3 * s + 4)):
            w.setze(x, y, 0, st(x, y, 0))
    for y in (1, 2):
        w.bloecke.pop((0, y, 0), None)
    for x in (-2, 2):
        w.setze(x, 2, 0, w.b("glass_pane"))
    for x in range(-B - 1, B + 2):
        w.setze(x, int(3 * s + 4), 1, w.b("spruce_slab", type="bottom", waterlogged=False))
    for k in range(2 + g):
        x = -B + 1 + k * 3
        z = 3 + (k % 2)
        w.setze(x, 1, z, w.b("barrel", facing="up", open=False))
        w.setze(x - 1, 1, z, w.b("spruce_stairs", facing="east", half="bottom", shape="straight", waterlogged=False))
        w.setze(x + 1, 1, z, w.b("spruce_stairs", facing="west", half="bottom", shape="straight", waterlogged=False))
    w.setze(B + 1, 3, 1, w.b("spruce_fence"))
    w.setze(B + 1, 2, 1, w.b("yellow_wool"))
    for sx in (-1, 1):
        laterne(w, sx * (B + 1), int(3 * s + 3), 1, kette=1)
    return w


def silberader(seed, g=2):
    """Silberader-Stollen: ein aufgeschnittener Berg zeigt einen Stollen mit Holzausbau, der einer glitzernden Ader aus
    Eisen-, Gold- und Diamanterz folgt, Spitzhacken-Zwerge, Loren und Stützbalken."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    H = int(10 * s + 6)
    berg(w, R, H, zf=-3)
    rng = w.rng
    erze = ["iron_ore", "gold_ore", "diamond_ore", "deepslate_iron_ore", "copper_ore", "raw_gold_block"]
    L = int(R * 0.62)
    ebenen = [1, int(H * 0.5)]
    for e, y0 in enumerate(ebenen):
        x0, x1 = (-L, L) if e == 0 else (-L + 2, L - 3)
        for x in range(x0, x1 + 1):
            for z in range(-6, -2):
                for y in range(y0, y0 + 3):
                    w.bloecke.pop((x, y, z), None)
                w.setze(x, y0 - 1, z, w.b("gravel") if rng.random() < 0.3 else w.b("stone"))
            w.setze(x, y0, -5, w.b("rail", shape="east_west", waterlogged=False))
            for y in range(y0 - 1, y0 + 4):
                for z in (-7, -2 - 0):
                    pass
            for y in range(y0, y0 + 4):
                if rng.random() < 0.35 and not w.frei(x, y, -7):
                    w.setze(x, y, -7, w.b(erze[int(rng.integers(len(erze)))]))
            if rng.random() < 0.3 and not w.frei(x, y0 + 3, -4):
                w.setze(x, y0 + 3, -4, w.b(erze[int(rng.integers(3))]))
            if (x - x0) % 4 == 0:
                for z in (-6, -3):
                    for y in range(y0, y0 + 3):
                        w.setze(x, y, z, w.b("spruce_log", axis="y"))
                for z in range(-6, -2):
                    w.setze(x, y0 + 3, z, w.b("spruce_log", axis="z"))
            if (x - x0) % 8 == 2:
                w.setze(x, y0 + 2, -6, w.b("wall_torch", facing="south"))
        for k in range(2):
            x = x0 + 3 + k * int((x1 - x0) * 0.55)
            figur(w, 0.4 * s + 0.25, zwerg(w, ["orange_wool", "white_wool"][k], ["blue_wool", "green_wool"][e]),
                  (-2, -1, -2), (2, 5, 2), pos=(x, y0, -4), winkel=math.pi / 2)
        w.setze(x1 - 2, y0, -4, w.b("barrel", facing="up", open=False))
    xs = L - 2
    for y in range(1, ebenen[1] + 3):
        w.bloecke.pop((xs, y, -4), None)
        w.bloecke.pop((xs, y, -5), None)
        w.setze(xs, y, -6, w.b("spruce_planks"))
        w.setze(xs, y, -5, w.b("ladder", facing="south", waterlogged=False))
    return w


def runenschmiede(seed, g=2):
    """Runenschmiede: eine heilige Schmiede in einer Kuppelhöhle mit einem Runenamboss auf einem Podest, glühenden
    Runensteinen in den Wänden, einer Esse aus Basalt und an Ketten hängenden Runenklingen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    berg(w, R, int(10 * s + 6))
    B = int(4 * s + 4)
    top = halle(w, -B, B, -int(R * 0.6), 0, 1, int(6 * s + 4), stil=2)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 1 and z > -int(R * 0.6) - 1 and abs(x) <= B and z <= 0 and not w.frei(x, y, z) and rng.random() < 0.05:
            if any(w.frei(x + dx, y, z + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1))):
                w.setze(x, y, z, w.b("chiseled_deepslate") if rng.random() < 0.5 else w.b("light_blue_glazed_terracotta",
                                                                                            facing="north"))
    for x in range(-1, 2):
        for z in range(-int(R * 0.3) - 1, -int(R * 0.3) + 2):
            w.setze(x, 1, z, w.b("polished_blackstone"))
    w.setze(0, 2, -int(R * 0.3), w.b("anvil", facing="east"))
    w.setze(0, 3, -int(R * 0.3), w.b("soul_lantern", hanging=False, waterlogged=False))
    for x in range(-B + 1, -B + 4):
        for z in range(-int(R * 0.6) + 1, -int(R * 0.6) + 4):
            w.setze(x, 1, z, w.b("basalt", axis="y"))
            w.setze(x, 2, z, w.b("magma_block") if (x, z) != (-B + 2, -int(R * 0.6) + 2) else w.b("basalt", axis="y"))
    for k in range(3):
        x = B - 2 - k
        for y in range(top - 3, top - 1):
            w.setze(x, y, -3, w.b("chain", axis="y", waterlogged=False))
        w.setze(x, top - 4, -3, w.b("light_blue_stained_glass"))
        w.setze(x, top - 5, -3, w.b("light_blue_stained_glass"))
    return w


def geodenkeller(seed, g=2):
    """Geodenkeller: eine riesige, aufgebrochene Kristalldruse im Berg, deren Inneres voller violetter und grüner
    Kristalle funkelt, mit einem Holzsteg hinein und Zwergen, die Kristalle in Körbe sammeln."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    berg(w, R, int(10 * s + 6))
    rg = 5 * s + 3.5
    cz = -int(R * 0.35)
    yc = int(rg) + 1
    for x in range(-int(rg) - 2, int(rg) + 3):
        for y in range(1, int(yc + rg) + 2):
            for z in range(cz - int(rg) - 2, cz + int(rg) + 3):
                d = math.sqrt(x * x + (y - yc) ** 2 + (z - cz) ** 2)
                if d <= rg - 1.2:
                    w.bloecke.pop((x, y, z), None)
                elif d <= rg:
                    w.setze(x, y, z, w.b("amethyst_block") if (x + y + z) % 4 else w.b("budding_amethyst"))
                elif d <= rg + 1.0:
                    w.setze(x, y, z, w.b("calcite"))
                elif d <= rg + 1.8:
                    w.setze(x, y, z, w.b("smooth_basalt"))
    for x in range(-int(rg) - 3, int(rg) + 4):
        for y in range(1, int(yc + rg) + 3):
            for z in range(cz + 1, cz + int(rg) + 4):
                if (x / (rg * 0.8)) ** 2 + ((y - yc) / rg) ** 2 < 1:
                    w.bloecke.pop((x, y, z), None)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b).endswith("amethyst_block") and rng.random() < 0.3:
            for dx, dy, dz, f in ((0, 1, 0, "up"), (0, -1, 0, "down"), (1, 0, 0, "east"), (-1, 0, 0, "west")):
                if w.frei(x + dx, y + dy, z + dz) and math.sqrt((x + dx) ** 2 + (y + dy - yc) ** 2 +
                                                                   (z + dz - cz) ** 2) < rg - 1:
                    w.setze(x + dx, y + dy, z + dz, w.b("amethyst_cluster", facing=f, waterlogged=False))
                    break
    for z in range(cz, int(R * 0.6)):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
    figur(w, 0.45 * s + 0.3, zwerg(w, "white_wool", "purple_wool"), (-2, -1, -2), (2, 5, 2), pos=(2, 2, cz + 2))
    return w


def thermen(seed, g=2):
    """Thermen der Tiefe: eine von Säulen getragene Badehalle im Berg mit dampfenden Becken auf mehreren Stufen,
    warmem Licht aus Glutsteinen unter dem Wasser, Ruhebänken und einem Wasserspeier in Zwergenkopfform."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    berg(w, R, int(10 * s + 6))
    B = int(R * 0.6)
    top = halle(w, -B, B, -int(R * 0.6), 0, 1, int(6 * s + 4), stil=3)
    for k in range(3):
        x0 = -B + 2 + k * int((2 * B - 3) / 3)
        y = 1 + (2 - k)
        for x in range(x0, x0 + int((2 * B - 3) / 3) - 1):
            for z in range(-int(R * 0.5), -2):
                for yy in range(1, y):
                    w.setze(x, yy, z, w.b("polished_deepslate"))
                w.setze(x, y - 1, z, w.b("shroomlight") if (x + z) % 5 == 0 else w.b("polished_deepslate"))
                w.setze(x, y, z, w.b("water", level=0))
                if x == x0 or z in (-int(R * 0.5), -3):
                    w.setze(x, y, z, w.b("chiseled_stone_bricks"))
        w.setze(x0 + 1, y + 1, -int(R * 0.5) + 1, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                      waterlogged=False))
    w.setze(0, top - 2, -int(R * 0.6) + 1, w.b("chiseled_stone_bricks"))
    w.setze(0, top - 3, -int(R * 0.6) + 2, w.b("water", level=0))
    for x in range(-B + 1, B, 3):
        w.setze(x, 1, -1, w.b("stone_brick_stairs", facing="south", half="bottom", shape="straight",
                              waterlogged=False))
    return w


def klammhammer(seed, g=2):
    """Klammhammer: in einer engen Felsklamm treibt ein Wildbach ein Wasserrad, das über eine Welle zwei riesige
    Schmiedehämmer in einer an die Felswand geklebten Hammerschmiede bewegt."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    H = int(10 * s + 6)
    f = fels(w)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            d = abs(z - math.sin(x / 4) * 1.5)
            if d < 2.5 + s:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel"))
                continue
            h = int(min(H if z < 0 else H * 0.35, (d - 2) * 2.5) + rn(x, 3, z) * 2)
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h and h > H - 2 else f(x, y, z))
    from erw_handwerk import wasserrad
    wasserrad(w, 0, 0, int(2 * s + 2), 2 * s + 1.8, achse="z")
    hz = -int(2.5 + s) - 3
    for x in range(-4, 5):
        for z in range(hz - 3, hz + 1):
            for y in range(1, 6):
                w.bloecke.pop((x, y, z), None)
            w.setze(x, 0, z, w.b("polished_andesite"))
    for x in range(-4, 5):
        w.setze(x, 6, hz, w.b("spruce_planks"))
        w.setze(x, 6, hz - 1, w.b("spruce_planks"))
    for k, x in enumerate((-2, 2)):
        w.setze(x, 1, hz - 1, w.b("anvil", facing="north"))
        for y in range(3, 5):
            w.setze(x, y, hz - 1, w.b("iron_block"))
        w.setze(x, 5, hz - 1, w.b("spruce_log", axis="z"))
    for z in range(hz, 1):
        w.setze(0, int(2 * s + 2), z, w.b("spruce_log", axis="z"))
    return w


def felsbastion(seed, g=2):
    """Felsbastion: eine aus der Felswand gehauene Wehrmauer mit Schießscharten, Erkern und einem Wehrgang, dahinter
    die Berghänge, davor ein Graben mit Zugbrücke und Zwergenwappen über dem Tor."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    H = int(12 * s + 8)
    berg(w, R, H)
    st = zwergstein(w)
    zw = 2
    Hw = int(8 * s + 6)
    for x in range(-R, R + 1):
        for y in range(1, Hw + 1):
            for z in (zw, zw - 1):
                if math.hypot(x, z) < R:
                    sch = y in (Hw - 3, Hw - 6) and x % 3 == 0 and z == zw
                    if sch:
                        w.bloecke.pop((x, y, z), None)
                    else:
                        w.setze(x, y, z, st(x, y, z))
        if x % 2 == 0 and math.hypot(x, zw) < R:
            w.setze(x, Hw + 1, zw, st(x, Hw + 1, zw))
    for sx in (-1, 1):
        x0 = sx * int(R * 0.45)
        for y in range(1, Hw + 4):
            for x, z in kreisrand(2 + s * 0.6, x0, zw + 1):
                w.setze(x, y, z, st(x, y, z))
    for x in range(-2, 3):
        for y in range(1, 5):
            for z in range(-5, zw + 1):
                w.bloecke.pop((x, y, z), None)
    for x in range(-R, R + 1):
        for z in range(zw + 2, zw + 5):
            if math.hypot(x, z) < R:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel"))
    for z in range(zw + 1, zw + 6):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
    for x in (-1, 0, 1):
        for y in (Hw - 1, Hw):
            w.setze(x, y, zw + 1, w.b("blue_wool") if x == 0 else w.b("yellow_wool"))
    return w


def runenarchiv(seed, g=2):
    """Archiv der Runen: eine hohe Felsenhalle mit endlosen Regalen aus Stein, gefüllt mit Runentafeln (Bücherregale,
    gemeißelte Platten), Leitern auf Schienen, Lesepulten und einem großen Runenstein im Zentrum."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    berg(w, R, int(12 * s + 6))
    B = int(R * 0.6)
    top = halle(w, -B, B, -int(R * 0.65), 0, 1, int(8 * s + 5), gewoelbe=False, stil=1)
    for x in range(-B + 2, B - 1, 3):
        for z in range(-int(R * 0.6), -3):
            for y in range(1, top - 2):
                w.setze(x, y, z, w.b("bookshelf") if (y + z) % 4 else w.b("chiseled_stone_bricks"))
        w.setze(x + 1, 1, -3, w.b("ladder", facing="south", waterlogged=False))
    for x in range(-1, 2):
        for z in (-1, -2):
            if x == 0:
                w.setze(x, 1, z, w.b("lectern", facing="south", has_book=True, powered=False))
    for y in range(1, int(4 * s + 4)):
        w.setze(0, y, 4, w.b("chiseled_deepslate") if y % 2 else w.b("deepslate_bricks"))
    for k in range(int(4 * s)):
        laterne(w, -B + 3 + k * int(2 * B / (4 * s + 1)), top - 1, -2, kette=2)
    return w


def koenigsgruft(seed, g=2):
    """Königsgruft: ein feierliches Grabgewölbe im Berg, in dem auf Steinsarkophagen die Bildnisse liegender Zwergen-
    könige mit Krone und Axt ruhen, zwischen Säulen mit Seelenfeuern und Goldgaben."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    berg(w, R, int(10 * s + 6))
    B = int(R * 0.6)
    top = halle(w, -B, B, -int(R * 0.6), 0, 1, int(6 * s + 4), stil=0)
    n = 2 + g
    for k in range(n):
        x = -B + 3 + k * int((2 * B - 4) / max(1, n - 1)) if n > 1 else 0
        z0 = -int(R * 0.45)
        for z in range(z0, z0 + 5):
            for dx in (-1, 0, 1):
                w.setze(x + dx, 1, z, w.b("polished_deepslate"))
        figur(w, 0.35 * s + 0.25, zwerg(w, "light_gray_wool", "gray_concrete", "gold_block"), (-2, -2, -2), (2, 5, 2),
              pos=(x, 3, z0 + 2), winkel=0.0)
        w.setze(x, 2, z0 + 5, w.b("gold_block"))
    for x in range(-B + 1, B, 4):
        w.setze(x, 1, -2, w.b("polished_blackstone"))
        w.setze(x, 2, -2, w.b("soul_campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    _ = top
    return w


def lueftungsschlote(seed, g=2):
    """Lüftungsschlote: über dem Gipfel eines Berges ragen mehrere gemauerte Schlote der Zwergenstadt empor, mit
    Rauch und Dampf, Windfahnen, kleinen Wartungsbrücken und einer Wetterstation dazwischen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 5)
    H = int(8 * s + 5)
    f = fels(w)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 2 * rn(x, 0, z):
                continue
            h = int(H * max(0, 1 - (d / R) ** 1.5) + rn(x, 3, z) * 2)
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h and h < H * 0.6 else f(x, y, z))
    st = zwergstein(w)
    pos = []
    for k in range(3 + g):
        a = k / (3 + g) * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.3), round(math.sin(a) * R * 0.3)
        y0 = hoehe(w, x, z, H + 5)
        Hs = int((5 + (k % 3) * 3) * s + 3)
        for y in range(y0, y0 + Hs):
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if abs(dx) == 1 or abs(dz) == 1:
                        w.setze(x + dx, y, z + dz, st(x, y, z))
        w.setze(x, y0 + Hs - 1, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
        pos.append((x, y0 + int(Hs * 0.6), z))
    for (a, b) in zip(pos, pos[1:]):
        n = int(math.hypot(b[0] - a[0], b[2] - a[2]))
        for k in range(n + 1):
            t = k / max(1, n)
            w.setze(round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t), round(a[2] + (b[2] - a[2]) * t),
                    w.b("spruce_slab", type="bottom", waterlogged=False), False)
    return w


def grottensee(seed, g=2):
    """Grottensee mit Fischern: ein unterirdischer See in einer offenen Grotte mit Tropfsteinen, auf dem Zwergen in
    Rundbooten mit Laternen Blindfische angeln, ein Steg und eine Räucherei am Ufer."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    berg(w, R, int(10 * s + 6))
    B = int(R * 0.65)
    top = halle(w, -B, B, -int(R * 0.7), 0, 1, int(7 * s + 4), stil=3)
    for x in range(-B + 1, B):
        for z in range(-int(R * 0.65), -2):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("gravel"))
    rng = w.rng
    for k in range(int(10 * s)):
        x, z = int((rng.random() - 0.5) * 2 * B), -int(rng.random() * R * 0.6)
        y = top - 1
        while y > 2 and w.frei(x, y, z):
            y -= 1
        if y < top - 1:
            for d in range(1, int(1 + rng.random() * 3)):
                if w.frei(x, top - d, z):
                    w.setze(x, top - d, z, w.b("pointed_dripstone", vertical_direction="down", thickness="tip",
                                               waterlogged=False))
    for k in range(2):
        bx, bz = -int(B * 0.4) + k * int(B * 0.8), -int(R * 0.35)
        for x, z in kreisrand(1.4, bx, bz):
            w.setze(x, 1, z, w.b("spruce_planks"))
        w.setze(bx, 0, bz, w.b("spruce_planks"))
        figur(w, 0.35 * s + 0.25, zwerg(w), (-2, -1, -2), (2, 5, 2), pos=(bx, 1, bz))
        laterne(w, bx + 1, 4, bz, kette=1)
    for z in range(-int(R * 0.3), int(R * 0.1)):
        w.setze(B - 2, 1, z, w.b("spruce_planks"))
    return w


def waffenkammer(seed, g=2):
    """Waffenkammer der Clans: eine Rüstkammer im Fels mit Reihen von Rüstungsständern, Äxten und Hämmern in Gestellen,
    Clanschilden in verschiedenen Farben an den Wänden und einer großen Kriegsaxt über dem Eingang."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    berg(w, R, int(9 * s + 6))
    B = int(R * 0.6)
    top = halle(w, -B, B, -int(R * 0.6), 0, 1, int(5 * s + 4), gewoelbe=False, stil=0)
    farben = ["red_wool", "blue_wool", "green_wool", "yellow_wool", "black_wool", "white_wool"]
    for x in range(-B + 1, B):
        w.setze(x, 3, -int(R * 0.6) + 1, w.b(farben[(x + 10) // 2 % 6]))
    for k in range(int(3 + 2 * s)):
        x = -B + 2 + k * 3
        for z in (-int(R * 0.35), -int(R * 0.15)):
            w.setze(x, 1, z, w.b("oak_fence"))
            w.setze(x, 2, z, w.b("iron_block"))
            w.setze(x, 3, z, w.b("iron_block"))
            w.setze(x, 4, z, w.b("iron_bars", waterlogged=False))
    for z in range(-int(R * 0.6) + 2, -1, 2):
        w.setze(B - 1, 1, z, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
        w.setze(B - 1, 2, z, w.b("iron_bars", waterlogged=False))
    for x in range(-3, 4):
        w.setze(x, top, 1, w.b("iron_block") if abs(x) > 1 else w.b("spruce_log", axis="x"))
    return w


def steingolem(seed, g=2):
    """Steingolem-Wächter: ein riesiger, aus Felsblöcken zusammengefügter Golem mit Runen auf der Brust und leuchten-
    den Augen steht vor einem versiegelten Bergtor und hält eine Säule als Keule."""
    w = _neu(seed)
    s = S[g]
    u = 1.0 * s + 0.6
    R = int(10 * u + 6)
    zellen = berg(w, R, int(12 * u + 4))
    portal(w, 0, 1, 1, int(2 * u), int(4 * u))
    for x in range(-int(2 * u), int(2 * u) + 1):
        for y in range(1, int(4 * u) + 1):
            w.setze(x, y, -1, w.b("chiseled_deepslate") if (x + y) % 3 == 0 else
                    w.b("polished_deepslate"))
    st = fels(w)
    teile = [(kasten(-2.5, 6, -1.6, 2.5, 11, 1.6), lambda x, y, z, *a: st(x, y, z)),
             (kasten(-1.4, 11, -1.2, 1.4, 13.4, 1.2), lambda x, y, z, *a: st(x, y, z)),
             (kasten(-0.9, 12, 1.1, -0.3, 12.5, 1.3), w.b("sea_lantern")),
             (kasten(0.3, 12, 1.1, 0.9, 12.5, 1.3), w.b("sea_lantern")),
             (kasten(-0.5, 8, 1.5, 0.5, 10, 1.7), w.b("light_blue_glazed_terracotta")),
             (kasten(-2.2, 0, -1.2, -0.6, 6, 1.2), lambda x, y, z, *a: st(x, y, z)),
             (kasten(0.6, 0, -1.2, 2.2, 6, 1.2), lambda x, y, z, *a: st(x, y, z)),
             (kasten(-4.2, 5, -1.0, -2.5, 10.5, 1.0), lambda x, y, z, *a: st(x, y, z)),
             (kasten(2.5, 6.5, -1.0, 4.2, 10.5, 1.0), lambda x, y, z, *a: st(x, y, z)),
             (kap((3.4, 7, 0), (3.4, 0, 3), 0.8), w.b("stone_bricks"))]
    figur(w, u, teile, (-5, -1, -2), (5, 14, 4), pos=(0, 1, 2 + int(4 * u)), winkel=0.0)
    _ = zellen
    return w


def tresor(seed, g=2):
    """Tresorkammer: eine Felswand mit einer riesigen, runden Tresortür aus Eisen und Gold mit Speichenrad, Bolzen und
    Runenschloss, halb geöffnet, dahinter Gold, Edelsteine und Truhen im Gewölbe."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    berg(w, R, int(10 * s + 6))
    rt = 3 * s + 2.5
    zt = 0
    yc = int(rt) + 1
    halle(w, -int(rt) - 2, int(rt) + 2, zt - int(R * 0.4), zt, 1, int(2 * rt + 2), front=False)
    for x in range(-int(rt) - 1, int(rt) + 2):
        for y in range(1, int(2 * rt) + 3):
            d = math.hypot(x, y - yc)
            if rt - 0.6 < d <= rt + 1.5:
                w.setze(x, y, zt, w.b("polished_blackstone") if d > rt + 0.6 else w.b("gold_block"))
    for k in range(int(rt * 8)):
        a = k / (rt * 8) * 2 * math.pi
        for t in range(int(rt)):
            p = (round(rt + 1 + math.sin(a) * 0), round(yc + math.sin(a) * t), round(zt + 1 + math.cos(a) * t))
            w.setze(round(rt) + 1, p[1], p[2], w.b("iron_block"), False)
    for d in (-1, 0, 1):
        w.setze(round(rt) + 2, yc + d, zt + 1, w.b("gold_block"))
        w.setze(round(rt) + 2, yc, zt + 1 + d, w.b("gold_block"))
    from drachen import gold_haufen
    gold_haufen(w, 0, zt - int(R * 0.25), rt, 1.5 + s, y0=1)
    w.setze(-2, 1, zt - 2, w.b("chest", facing="south", type="single", waterlogged=False))
    w.setze(2, 1, zt - 2, w.b("chest", facing="south", type="single", waterlogged=False))
    return w


def laternenkluft(seed, g=2):
    """Laternenkluft: eine tiefe, schmale Felsspalte, über die sich Dutzende Ketten mit Laternen spannen, ein Netz
    aus Hängestegen verbindet Felsbalkone mit Türen auf beiden Seiten, unten fließt Lava."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    H = int(12 * s + 8)
    f = fels(w)
    sp = 3 + s
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            if abs(z - math.sin(x / 5) * 1.5) < sp:
                w.setze(x, -2, z, w.b("lava", level=0))
                w.setze(x, -3, z, w.b("magma_block"))
                continue
            Hz = H if z < math.sin(x / 5) * 1.5 else int(H * 0.3)
            for y in range(-3, Hz + int(rn(x, 3, z) * 3)):
                w.setze(x, y, z, f(x, y, z))
            w.setze(x, Hz + int(rn(x, 3, z) * 3), z, w.b("grass_block", snowy=False) if rn(x, 8, z) < 0.6 else
                    w.b("coarse_dirt"))
    rng = w.rng
    for k in range(int(8 + 4 * s)):
        x = int((rng.random() - 0.5) * R * 1.6)
        y = int(2 + rng.random() * (H - 4))
        z0 = round(math.sin(x / 5) * 1.5)
        for z in range(z0 - int(sp), z0 + int(sp) + 1):
            w.setze(x, y + round(0.8 * math.cos(math.pi * (z - z0) / (2 * sp))) * 0, z, w.b("chain", axis="z",
                                                                                            waterlogged=False), False)
        w.setze(x, y - 1, z0, w.b("lantern", hanging=True, waterlogged=False), False)
    for k in range(3):
        y = int(H * (0.3 + 0.25 * k))
        x = -int(R * 0.4) + k * int(R * 0.4)
        z0 = round(math.sin(x / 5) * 1.5)
        for z in range(z0 - int(sp) - 1, z0 + int(sp) + 2):
            for dx in (-1, 0, 1):
                w.setze(x + dx, y, z, w.b("spruce_slab", type="bottom", waterlogged=False), False)
        for sz in (-1, 1):
            zb = z0 + sz * (int(sp) + 1)
            if sz > 0:
                for dx in range(-2, 3):
                    for dz in range(0, 4):
                        for yy in range(-3, y + 4):
                            w.setze(x + dx, yy, zb + dz, w.b("stone_bricks") if abs(dx) < 2 and dz < 3 else
                                    w.b("polished_deepslate"))
                w.setze(x, y + 4, zb + 1, w.b("chiseled_stone_bricks"))
            for dx in range(-2, 3):
                for dz in range(0, 3):
                    w.setze(x + dx, y - 1, zb + sz * dz, w.b("stone_bricks"))
                    for yy in range(y, y + 3):
                        w.bloecke.pop((x + dx, yy, zb + sz * dz), None)
            w.setze(x, y, zb + sz * 3, w.b("spruce_door", facing="north" if sz > 0 else "south", half="lower",
                                           hinge="left", open=False, powered=False))
            w.setze(x, y + 1, zb + sz * 3, w.b("spruce_door", facing="north" if sz > 0 else "south", half="upper",
                                               hinge="left", open=False, powered=False))
    return w


ZWERGE3 = {
    "lorenbahnhof": ("Lorenbahnhof", lorenbahnhof),
    "zwergenkoenig_statue": ("Steinerner Zwergenkönig", zwergenkoenig_statue),
    "schleiferei": ("Edelsteinschleiferei", schleiferei),
    "schachtaufzug": ("Schachtaufzug", schachtaufzug),
    "untertagemarkt": ("Untertage-Markt", untertagemarkt),
    "taverne": ("Zwergentaverne am Fels", taverne),
    "silberader": ("Silberader-Stollen", silberader),
    "runenschmiede": ("Runenschmiede", runenschmiede),
    "geodenkeller": ("Geodenkeller", geodenkeller),
    "thermen": ("Thermen der Tiefe", thermen),
    "klammhammer": ("Klammhammer", klammhammer),
    "felsbastion": ("Felsbastion", felsbastion),
    "runenarchiv": ("Archiv der Runen", runenarchiv),
    "koenigsgruft": ("Königsgruft", koenigsgruft),
    "lueftungsschlote": ("Lüftungsschlote", lueftungsschlote),
    "grottensee": ("Grottensee mit Fischern", grottensee),
    "waffenkammer": ("Waffenkammer der Clans", waffenkammer),
    "steingolem": ("Steingolem-Wächter", steingolem),
    "tresor": ("Tresorkammer", tresor),
    "laternenkluft": ("Laternenkluft", laternenkluft),
}

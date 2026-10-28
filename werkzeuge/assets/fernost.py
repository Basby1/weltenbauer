"""Fernost (neu) – 20 Bauten und Gärten im ostasiatischen Stil.

Geschwungene Dächer mit hochgezogenen Ecken und Goldspitzen, Pfosten-Riegel-Fachwerk mit hellen
Papierwänden und Gitterfenstern, Veranden mit Geländern, Torii, Steinlaternen, Koi-Teiche,
geharkte Kiesgärten, Bambus und Kirschbäume.
Stil 1 Japan (dunkles Holz, Schieferdächer, Rot als Akzent), Stil 2 China (rote Säulen,
goldgelbe oder jadegrüne Glasurdächer, Marmorterrassen).
"""

from __future__ import annotations

import math

import pracht as P
from lib import Rauschen, einfuegen, laub
from pracht import Mat, gelaende, treppe
from skulptur import kreisrand, scheibe
from weltwunder import hohl

U = [0.6, 1.0, 1.7, 2.8]
GEGEN = {"north": "south", "south": "north", "east": "west", "west": "east"}


def _welt(seed):
    from lib import Welt
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _richtung(x, z, a):
    return "east" if x == -a else "west" if x == a else "south" if z == -a else "north"


class Ost:
    def __init__(self, w, seed, gruen=False, dach=None):
        self.w = w
        self.japan = _stil(seed) == 0
        b = w.b
        if self.japan:
            self.saeule = b("stripped_dark_oak_log", axis="y")
            self.saeule_rot = b("red_terracotta" if False else "stripped_mangrove_log", axis="y")
            self.balken = "dark_oak"
            self.wand = Mat(w, ["white_terracotta", "smooth_quartz", "white_concrete", "calcite"], kontrast=0.4)
            self.dach = P.Dach(w, ["deepslate_tile", "deepslate_tile", "polished_blackstone_brick", "deepslate_brick"])
            self.gold = "gold_block"
            self.holz = "dark_oak"
            self.sockel = Mat(w, "graustein")
            self.rand = "stone_brick"
            self.licht = "lantern"
            self.terr = Mat(w, ["stone_bricks", "cobblestone", "mossy_cobblestone", "andesite", "stone"])
            if dach == "kupfer":
                self.dach = P.Dach(w, ["waxed_oxidized_cut_copper", "waxed_weathered_cut_copper",
                                       "waxed_oxidized_cut_copper"])
            elif dach == "holz":
                self.dach = P.Dach(w, ["spruce", "dark_oak", "spruce"])
        else:
            self.saeule = b("stripped_mangrove_log", axis="y")
            self.saeule_rot = self.saeule
            self.balken = "mangrove"
            self.wand = Mat(w, ["red_terracotta", "red_concrete", "red_terracotta", "red_nether_bricks"], kontrast=0.4)
            self.dach = P.Dach(w, ["dark_prismarine", "prismarine_brick", "dark_prismarine"]) if gruen else \
                P.Dach(w, ["smooth_sandstone", "sandstone", "end_stone_brick", "smooth_sandstone"])
            self.gold = "gold_block"
            self.holz = "mangrove"
            self.sockel = Mat(w, "marmor")
            self.rand = "quartz"
            self.licht = "lantern"
            self.terr = Mat(w, ["polished_diorite", "calcite", "smooth_quartz", "quartz_bricks"])


# ============================================================================ Bauteile


def ostdach(w, o, x0, z0, x1, z1, y, ue=3, ecken=True, first=True):
    """Geschwungenes Walmdach: flach auslaufender Überstand, steiler zum First, Ecken hochgezogen
    mit Goldspitzen. Gibt die Firsthöhe zurück."""
    D = o.dach
    k = 0
    y_ = y
    while True:
        ax, bx, az, bz = x0 - ue + k, x1 + ue - k, z0 - ue + k, z1 + ue - k
        if ax > bx or az > bz:
            break
        for x in range(ax, bx + 1):
            for z in range(az, bz + 1):
                if not (x in (ax, bx) or z in (az, bz)):
                    continue
                if ax == bx or az == bz:
                    w.setze(x, y_, z, D.voll(x, y_, z))
                elif x in (ax, bx) and z in (az, bz):
                    w.setze(x, y_, z, D.voll(x, y_, z))
                else:
                    f = "south" if z == az else "north" if z == bz else "east" if x == ax else "west"
                    w.setze(x, y_, z, D.platte(x, y_, z) if k < 2 and ue >= 3 else D.treppe(x, y_, z, f))
        if k == 0 and ecken:
            for (cx, cz) in ((ax, az), (bx, az), (ax, bz), (bx, bz)):
                w.setze(cx, y_ + 1, cz, D.voll(cx, y_ + 1, cz))
                w.setze(cx, y_ + 2, cz, w.b(o.gold) if o.japan is False else
                        w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
        # flach: erste zwei Ringe auf gleicher Höhe, danach steigend
        if k >= 1 or ue < 3:
            y_ += 1
        k += 1
    # Traufunterseite
    for x in range(x0 - ue, x1 + ue + 1):
        for z in range(z0 - ue, z1 + ue + 1):
            if (x in (x0 - ue, x1 + ue) or z in (z0 - ue, z1 + ue)) and not (x in (x0 - ue, x1 + ue) and z in (z0 - ue, z1 + ue)):
                w.setze(x, y - 1, z, w.b(f"{o.holz}_slab", type="top", waterlogged=False), ueberschreiben=False)
    return y_


def geschoss(w, o, x0, z0, x1, z1, y0, h, veranda=True, tuer="south", gitter=True):
    """Pfosten-Riegel-Geschoss: Säulen alle 3 Blöcke, helle Wände, Gitterfenster, Riegel oben, Veranda."""
    for y in range(y0, y0 + h):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                rx, rz = x in (x0, x1), z in (z0, z1)
                if not (rx or rz):
                    if y == y0:
                        w.setze(x, y, z, w.b(f"{o.holz}_planks"))
                    continue
                t = (x - x0) if rz else (z - z0)
                if (rx and rz) or t % 3 == 0:
                    w.setze(x, y, z, o.saeule)
                elif y == y0 + h - 1:
                    w.setze(x, y, z, w.b(f"stripped_{o.balken}_log", axis="x" if rz else "z"))
                elif gitter and y - y0 in (1, 2) and t % 3 == 1 + (h > 4):
                    f = "south" if z == z1 else "north" if z == z0 else "east" if x == x1 else "west"
                    w.setze(x, y, z, w.b(f"{o.holz}_trapdoor" if o.holz != "mangrove" else "dark_oak_trapdoor",
                                         facing=f, half="bottom", open=True, powered=False, waterlogged=False)
                            if False else w.b("glass_pane", north=not rz, south=not rz, east=rz, west=rz,
                                              waterlogged=False))
                else:
                    w.setze(x, y, z, o.wand(x, y, z, 0.5))
    if veranda:
        for x in range(x0 - 1, x1 + 2):
            for z in range(z0 - 1, z1 + 2):
                if x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1):
                    w.setze(x, y0 - 1, z, w.b(f"{o.holz}_planks"))
                    if not (x in (x0 - 1, x1 + 1) and z in (z0 - 1, z1 + 1)):
                        n = x in (x0 - 1, x1 + 1)
                        w.setze(x, y0, z, w.b(f"{o.holz}_fence" if o.holz != "mangrove" else "mangrove_fence",
                                              north=n, south=n, east=not n, west=not n, waterlogged=False))
    mx, mz = (x0 + x1) // 2, (z0 + z1) // 2
    tx, tz = {"south": (mx, z1), "north": (mx, z0), "east": (x1, mz), "west": (x0, mz)}[tuer]
    dx, dz = {"south": (0, 1), "north": (0, -1), "east": (1, 0), "west": (-1, 0)}[tuer]
    for d in (-1, 0, 1):
        for y in range(y0, y0 + min(3, h - 1)):
            p = (tx + d, y, tz) if tuer in ("south", "north") else (tx, y, tz + d)
            w.bloecke.pop(p, None)
        p = (tx + dx + d, y0, tz + dz) if tuer in ("south", "north") else (tx + dx, y0, tz + dz + d)
        w.bloecke.pop(p, None)


def steinlaterne(w, x, z, y=1, gross=False):
    w.setze(x, y, z, w.b("stone_bricks"))
    w.setze(x, y + 1, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                             waterlogged=False))
    if gross:
        w.setze(x, y + 2, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                                 waterlogged=False))
        y += 1
    w.setze(x, y + 2, z, w.b("lantern", hanging=False, waterlogged=False))
    w.setze(x, y + 3, z, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    for dx, dz, f in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
        w.setze(x + dx, y + 3, z + dz, w.b("stone_brick_stairs", facing=f, half="top", shape="straight",
                                           waterlogged=False) if False else w.b("stone_button", face="wall", facing=GEGEN[f],
                                                                                powered=False))


def torii(w, o, x, z, breite, hoehe, achse="z"):
    """Torii: zwei rote Pfosten, doppelter Querbalken, oben geschwungen."""
    rot = w.b("red_concrete") if o.japan else w.b("red_terracotta")
    for s in (-1, 1):
        for y in range(1, hoehe + 1):
            p = (x + s * breite, y, z) if achse == "z" else (x, y, z + s * breite)
            w.setze(*p, rot if y > 1 else w.b("black_concrete"))
    for q in range(-breite - 2, breite + 3):
        p1 = (x + q, hoehe - 1, z) if achse == "z" else (x, hoehe - 1, z + q)
        p2 = (x + q, hoehe + 1, z) if achse == "z" else (x, hoehe + 1, z + q)
        if abs(q) <= breite + 1:
            w.setze(*p1, rot)
        w.setze(*p2, w.b("black_concrete") if abs(q) <= breite + 1 else
                w.b("polished_blackstone_brick_slab", type="top", waterlogged=False))
        if abs(q) <= breite:
            w.setze(p2[0], p2[1] - 1, p2[2], rot)
    p = (x, hoehe, z)
    w.setze(*p, w.b("gold_block"))


def teich(w, cx, cz, R, koi=True):
    r_n = Rauschen(w, 3)
    for x, z in scheibe(R + 2, cx, cz):
        d = math.hypot(x - cx, z - cz) / (R * (0.8 + 0.4 * r_n(x, 0, z)))
        if d < 1:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("water", level=0) if d < 0.6 else w.b("clay"))
            w.setze(x, -2, z, w.b("gravel"))
            if w.rng.random() < 0.06:
                w.setze(x, 1, z, w.b("lily_pad"))
        elif d < 1.25:
            w.setze(x, 0, z, w.b(["cobblestone", "mossy_cobblestone", "stone", "andesite"][int(r_n(x, 3, z) * 3.99)]))
            if w.rng.random() < 0.15:
                w.setze(x, 1, z, w.b("mossy_cobblestone"))


def kiesgarten(w, x0, z0, x1, z1, steine=3):
    rng = w.rng
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, 0, z, w.b("gravel") if (x + z) % 2 else w.b("sand"))
    for i in range(steine):
        sx, sz = int(x0 + 2 + rng.random() * (x1 - x0 - 4)), int(z0 + 2 + rng.random() * (z1 - z0 - 4))
        for x in range(sx - 1, sx + 2):
            for z in range(sz - 1, sz + 2):
                w.setze(x, 0, z, w.b("moss_block"))
        w.setze(sx, 1, sz, w.b(["mossy_cobblestone", "andesite", "tuff"][i % 3]))
        if rng.random() < 0.5:
            w.setze(sx + 1, 1, sz, w.b("andesite"))
            w.setze(sx, 2, sz, w.b("stone"))


def kirsche(w, x, z, gross=0):
    import baeume as B
    einfuegen(w, B.ARTEN["kirschbaum"][1](int(w.rng.integers(1, 10 ** 6)), gross), x, 0, z)


def bambus(w, cx, cz, R, dichte=0.35):
    import wald
    w.folgen = {}
    for x, z in scheibe(R, cx, cz):
        if w.rng.random() < dichte:
            w.setze(x, 0, z, w.b("podzol", snowy=False))
            wald.bambus(w, x, 1, z)
    del w.folgen


def terrasse(w, o, x0, z0, x1, z1, h=2):
    for y in range(1, h + 1):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if x in (x0, x1) or z in (z0, z1) or y == h:
                    w.setze(x, y, z, o.terr(x, y, z, 0.4))
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            if (x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1)) and not (x in (x0 - 1, x1 + 1) and z in (z0 - 1, z1 + 1)):
                f = "east" if x == x0 - 1 else "west" if x == x1 + 1 else "south" if z == z0 - 1 else "north"
                w.setze(x, h, z, treppe(w, o.rand, f, "top"))
    return h + 1


# ============================================================================ 1 Pagode


def pagode(seed, g=2):
    """Pagode: fünf bis neun Geschosse mit Veranden und geschwungenen Dächern, Ringspitze, Steinlaternen."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    stock = 3 + g * 2
    h0 = _r(4 * u + 2, 3)
    gelaende(w, h0 + 10, art="wiese")
    y = terrasse(w, o, -h0 - 3, -h0 - 3, h0 + 3, h0 + 3, 2)
    for s in range(stock):
        h = max(2, h0 - s * h0 // (stock + 1))
        eh = 4 if s == 0 else 3
        geschoss(w, o, -h, -h, h, h, y, eh, veranda=s > 0 or True, tuer="south")
        y = ostdach(w, o, -h, -h, h, h, y + eh, ue=3 if s < stock - 1 else 3) - (h - 1) + 1 if s < stock - 1 else \
            ostdach(w, o, -h, -h, h, h, y + eh, ue=3)
    for k in range(_r(6 * u + 3, 4)):
        w.setze(0, y + k, 0, w.b(o.gold) if k % 2 == 0 else w.b("chain", axis="y", waterlogged=False))
    for sx in (-1, 1):
        steinlaterne(w, sx * (h0 + 5), h0 + 5, gross=True)
    hohl(w, 2)
    return w


# ============================================================================ 2 Tempelhalle


def tempelhalle(seed, g=2):
    """Haupthalle eines Tempels: breiter Bau auf Steinterrasse, doppeltes Dach, Freitreppe, Räucherbecken
    und Wächterlaternen."""
    w = _welt(seed)
    o = Ost(w, seed, gruen=True, dach="kupfer")
    u = U[g]
    a, b = _r(7 * u + 3, 5), _r(4 * u + 2, 3)
    gelaende(w, a + 12, art="wiese")
    y = terrasse(w, o, -a - 3, -b - 3, a + 3, b + 3, _r(2 * u + 1, 2))
    geschoss(w, o, -a, -b, a, b, y, _r(3 * u + 3, 4))
    y2 = ostdach(w, o, -a, -b, a, b, y + _r(3 * u + 3, 4), ue=3)
    geschoss(w, o, -a + 2, -b + 1, a - 2, b - 1, y + _r(3 * u + 3, 4) + 2, 3, veranda=False)
    ostdach(w, o, -a + 2, -b + 1, a - 2, b - 1, y + _r(3 * u + 3, 4) + 5, ue=3)
    for k in range(y):
        for x in range(-2, 3):
            w.setze(x, y - 1 - k, b + 4 + k, treppe(w, o.rand, "north"))
    w.setze(0, 1, b + 8, w.b("cauldron"))
    w.setze(0, 2, b + 8, w.b("campfire", lit=False, signal_fire=False, facing="north", waterlogged=False))
    for sx in (-1, 1):
        steinlaterne(w, sx * 4, b + 8, gross=True)
    hohl(w, 2)
    return w


# ============================================================================ 3 Torii-Weg


def toriiweg(seed, g=1):
    """Torii-Weg: viele rote Tore hintereinander über einem Steinpfad, Laternen und ein kleiner Schrein am Ende."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    n = 4 + g * 3
    L = n * 3 + 6
    gelaende(w, L // 2 + 6, art="wald", dichte=0.8)
    for z in range(-L // 2, L // 2 + 1):
        for x in (-1, 0, 1):
            w.setze(x, 0, z, w.b("stone_bricks") if (x + z) % 3 else w.b("mossy_stone_bricks"))
    for i in range(n):
        torii(w, o, 0, -L // 2 + 2 + i * 3, 2, 4 + (g >= 2))
    for z in range(-L // 2, L // 2, 6):
        for sx in (-4, 4):
            steinlaterne(w, sx, z)
    geschoss(w, o, -2, L // 2 + 1, 2, L // 2 + 4, 1, 3, veranda=False, tuer="north")
    ostdach(w, o, -2, L // 2 + 1, 2, L // 2 + 4, 4, ue=2)
    hohl(w, 2)
    return w


# ============================================================================ 4 Teehaus


def teehaus(seed, g=1):
    """Teehaus am Koi-Teich: kleiner Pavillon mit Veranda über dem Wasser, Trittsteine, Ahorn und Laterne."""
    w = _welt(seed)
    o = Ost(w, seed, dach="holz")
    u = U[g]
    a = _r(3 * u + 2, 3)
    gelaende(w, a + 12, art="wiese", dichte=0.6)
    teich(w, a + 5, a + 4, a + 3)
    geschoss(w, o, -a, -a, a, a, 2, 4, tuer="east")
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            w.setze(x, 1, z, w.b(f"{o.holz}_planks"))
            if max(abs(x), abs(z)) == a + 1 and (x + z) % 3 == 0:
                w.setze(x, 0, z, w.b(f"{o.holz}_log", axis="y"))
    ostdach(w, o, -a, -a, a, a, 6, ue=2)
    for k in range(5):
        w.setze(a + 2 + k, 0, k % 2, w.b("smooth_stone_slab", type="top", waterlogged=False) if False else
                w.b("polished_andesite"))
    steinlaterne(w, a + 3, -a - 2)
    kirsche(w, -a - 4, a + 3)
    hohl(w, 2)
    return w


# ============================================================================ 5 Zen-Garten


def zengarten(seed, g=1):
    """Zen-Garten: geharkter Kies mit Felseninseln und Moos, umgeben von einer verputzten Mauer mit Ziegelkappe,
    ein Holzsteg, Kiefern-Bonsai und eine Betrachtungs-Veranda."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    a, b = _r(8 * u + 4, 6), _r(6 * u + 3, 4)
    gelaende(w, a + 6, art="wiese")
    kiesgarten(w, -a + 1, -b + 1, a - 1, b - 1, steine=3 + g * 2)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            if x in (-a, a) or z in (-b, b):
                for y in (1, 2):
                    w.setze(x, y, z, o.wand(x, y, z, 0.5))
                f = "east" if x == -a else "west" if x == a else "south" if z == -b else "north"
                w.setze(x, 3, z, o.dach.voll(x, 3, z))
    geschoss(w, o, -a + 2, -b - 5, a - 2, -b - 1, 1, 4, tuer="south")
    ostdach(w, o, -a + 2, -b - 5, a - 2, -b - 1, 5, ue=2)
    import wald
    einfuegen(w, wald.kiefer(int(w.rng.integers(1, 10 ** 6)), H=6), a - 3, 0, b - 3)
    hohl(w, 2)
    return w


# ============================================================================ 6 Burg (Tenshu)


def ostburg(seed, g=2):
    """Burg auf geböschtem Steinsockel: weißer Hauptturm mit mehreren Dachstufen und Ziergiebeln,
    goldene Firstfische, Mauern mit Wehrgang und Torbau."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    a = _r(8 * u + 4, 5)
    Hs = _r(6 * u + 3, 4)
    gelaende(w, a + 14, art="wiese")
    st = Mat(w, ["stone", "andesite", "cobblestone", "stone_bricks", "tuff", "mossy_cobblestone"], kontrast=1.2)
    for y in range(1, Hs + 1):
        h = a + 2 + (Hs - y) // 2
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                if max(abs(x), abs(z)) >= h - 1 or y == Hs:
                    w.setze(x, y, z, st(x, y, z, y / Hs))
    y = Hs + 1
    w_hell = Mat(w, ["white_concrete", "white_terracotta", "smooth_quartz", "calcite"], kontrast=0.3)
    stufen = 3 + (g >= 2)
    for s in range(stufen):
        h = max(2, a - s * a // (stufen + 1))
        eh = 4
        for yy in range(y, y + eh):
            for x in range(-h, h + 1):
                for z in range(-h, h + 1):
                    if max(abs(x), abs(z)) == h:
                        lang = z if abs(x) == h else x
                        if abs(x) == h and abs(z) == h:
                            w.setze(x, yy, z, o.saeule)
                        elif yy - y == 2 and lang % 3 == 0:
                            w.setze(x, yy, z, w.b("black_concrete"))
                        else:
                            w.setze(x, yy, z, w_hell(x, yy, z, 0.5))
        y = ostdach(w, o, -h, -h, h, h, y + eh, ue=2) - (h - 2) if s < stufen - 1 else ostdach(w, o, -h, -h, h, h,
                                                                                                y + eh, ue=2)
        # Ziergiebel
        if s % 2 == 0 and h >= 3:
            for k in range(3):
                for x in range(-2 + k, 3 - k):
                    w.setze(x, y - 1 + k - (h - 2 if s < stufen - 1 else 0) + 0, h + 1, o.dach.voll(x, 0, h + 1)) if False \
                        else None
    for sx in (-1, 1):
        w.setze(sx, y, 0, w.b(o.gold))
    # Mauer mit Tor
    R = a + 8
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if max(abs(x), abs(z)) == R:
                for yy in range(1, 4):
                    w.setze(x, yy, z, st(x, yy, z, 0.4) if yy < 3 else w_hell(x, yy, z, 0.5))
                w.setze(x, 4, z, o.dach.voll(x, 4, z))
    for x in range(-1, 2):
        for yy in range(1, 4):
            w.bloecke.pop((x, yy, R), None)
    hohl(w, 3)
    return w


# ============================================================================ 7 Glockenpavillon


def glockenpavillon(seed, g=1):
    """Glockenpavillon: offener Pavillon auf vier Säulen mit großer Bronzeglocke und Schlagbalken."""
    w = _welt(seed)
    o = Ost(w, seed, gruen=True, dach="kupfer")
    u = U[g]
    a = _r(2 * u + 1.5, 2)
    gelaende(w, a + 8, art="wiese")
    terrasse(w, o, -a - 1, -a - 1, a + 1, a + 1, 1)
    for sx in (-a, a):
        for sz in (-a, a):
            for y in range(2, 7):
                w.setze(sx, y, sz, o.saeule)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if max(abs(x), abs(z)) == a:
                w.setze(x, 7, z, w.b(f"stripped_{o.balken}_log", axis="x" if abs(z) == a else "z"))
    ostdach(w, o, -a, -a, a, a, 8, ue=2)
    for y in range(4, 7):
        r = 0 if y == 6 else 1
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                w.setze(x, y, z, w.b("waxed_oxidized_copper" if o.japan else "waxed_weathered_copper"))
    w.setze(0, 3, 0, w.b("bell", attachment="floor", facing="north", powered=False))
    for k in range(3):
        w.setze(-a + 1, 4, k - 1, w.b(f"{o.balken}_log", axis="z")) if False else None
    w.setze(a + 2, 5, 0, w.b(f"{o.balken}_log", axis="x"))
    w.setze(a + 2, 6, 0, w.b("chain", axis="y", waterlogged=False))
    hohl(w, 2)
    return w


# ============================================================================ 8 Brückenpavillon


def brueckenpavillon(seed, g=1):
    """Rote Bogenbrücke über einen Teich mit einem Pavillon auf dem Scheitel, Seerosen und Laternen."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    L = _r(9 * u + 5, 6)
    gelaende(w, L + 6, art="wiese", dichte=0.6)
    teich(w, 0, 0, L - 1)
    rot = "mangrove" if not o.japan else "crimson"
    H = _r(L * 0.35, 2)
    for z in range(-L, L + 1):
        y = 1 + int(H * math.cos(z / L * math.pi / 2))
        for x in (-1, 0, 1):
            w.setze(x, y, z, w.b(f"{rot}_planks"))
            w.setze(x, y - 1, z, w.b(f"{rot}_slab", type="top", waterlogged=False), ueberschreiben=False)
        for x in (-2, 2):
            w.setze(x, y, z, w.b(f"{rot}_planks"))
            w.setze(x, y + 1, z, w.b(f"{rot}_fence", north=True, south=True, east=False, west=False, waterlogged=False))
    for z in (-1, 0, 1):
        pass
    a = 2
    for sx in (-a, a):
        for sz in (-a, a):
            for y in range(H + 2, H + 6):
                w.setze(sx, y, sz, w.b("red_concrete" if o.japan else "red_terracotta"))
    ostdach(w, o, -a, -a, a, a, H + 6, ue=2)
    for sz in (-L, L):
        for sx in (-3, 3):
            steinlaterne(w, sx, sz)
    hohl(w, 2)
    return w


# ============================================================================ 9 Bambushain


def bambushain(seed, g=1):
    """Bambushain: dichter Bambuswald mit Steinpfad, kleinem Schrein, Laternen und Bachlauf."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(10 * u + 6, 6)
    gelaende(w, R + 2, art="wald", dichte=0.4)
    bambus(w, 0, 0, R, 0.4)
    for z in range(-R, R + 1):
        x = round(math.sin(z / R * 2) * 2)
        for d in (-1, 0, 1):
            for y in range(1, 18):
                w.bloecke.pop((x + d, y, z), None)
            w.setze(x + d, 0, z, w.b("stone_bricks") if (z + d) % 3 else w.b("mossy_cobblestone"))
    for z in range(-R + 2, R, 6):
        steinlaterne(w, round(math.sin(z / R * 2) * 2) + 3, z)
    for x in range(-2, 3):
        for z in range(-2, 3):
            for y in range(1, 12):
                w.bloecke.pop((x + 5, y, z), None)
    geschoss(w, o, 4, -1, 6, 1, 1, 3, veranda=False, tuer="west")
    ostdach(w, o, 4, -1, 6, 1, 4, ue=1)
    hohl(w, 2)
    return w


# ============================================================================ 10 Kirschgarten


def kirschgarten(seed, g=1):
    """Kirschblütengarten: Kirschbäume um eine Wiese mit Blütenteppich, Steinlaternen, Bank-Pavillon, Bachlauf."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(12 * u + 6)
    gelaende(w, R + 4, art="wiese", dichte=0.6)
    import wald
    w.folgen = {}
    for x, z in scheibe(R):
        if w.rng.random() < 0.2 and w.frei(x, 1, z):
            wald.bluetenblaetter(w, x, 1, z)
    del w.folgen
    n = 5 + g * 3
    for i in range(n):
        a = i / n * 2 * math.pi
        kirsche(w, round(math.cos(a) * R * 0.75), round(math.sin(a) * R * 0.75), 1 if g >= 2 and i % 2 else 0)
    for i in range(4):
        a = i / 4 * 2 * math.pi + 0.4
        steinlaterne(w, round(math.cos(a) * R * 0.4), round(math.sin(a) * R * 0.4))
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in range(1, 4):
                w.setze(sx * 2, y, sz * 2, o.saeule)
    ostdach(w, o, -2, -2, 2, 2, 4, ue=1)
    hohl(w, 2)
    return w


# ============================================================================ 11 Reisterrassen


def reisterrassen(seed, g=2):
    """Reisterrassen am Hang: geschwungene Stufenfelder mit Wasser und Halmen, Erdwälle, ein Bauernhaus und
    Vogelscheuche."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    n = 4 + g
    R = _r(16 * u + 6)
    r_n = Rauschen(w, 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            v = (z + R) / (2 * R) * n + (r_n(x, 0, z) - 0.5) * 1.2 + math.sin(x / R * 3) * 0.6
            k = max(0, min(n - 1, int(v)))
            hh = k * 2
            for y in range(0, hh + 1):
                w.setze(x, y, z, w.b("dirt") if y < hh else w.b("grass_block", snowy=False))
            rand = int(v + 0.12) != k or int(v - 0.12) != k
            if not rand:
                w.setze(x, hh, z, w.b("water", level=0) if (x + z) % 5 else w.b("mud"))
                w.setze(x, hh - 1, z, w.b("mud"))
                if (x + z) % 5 and w.rng.random() < 0.5:
                    w.setze(x, hh + 1, z, w.b("seagrass") if False else w.b("short_grass" if False else "grass"))
    geschoss(w, o, -4, -R - 7, 4, -R - 2, 1, 4, tuer="north")
    for x in range(-5, 6):
        for z in range(-R - 8, -R - 1):
            w.setze(x, 0, z, w.b("dirt_path"))
    ostdach(w, o, -4, -R - 7, 4, -R - 2, 5, ue=2)
    hohl(w, 2)
    return w


# ============================================================================ 12 Bauernhaus (Minka)


def minka(seed, g=1):
    """Bauernhaus mit hohem Strohdach (Gassho), dunklem Holzrahmen, Veranda, Holzstapel und Gemüsegarten."""
    import haeuser as H_
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 9, art="wiese")
    geschoss(w, o, -a, -b, a, b, 1, 4, tuer="south")
    D = P.Dach(w, ["spruce", "oak", "spruce"])
    top = P.satteldach(w, D, -a, -b, a, b, 5, ue=2, first_x=True, wand=o.wand, steil=True)
    for (x, y, z), blk in list(w.bloecke.items()):
        if y > 5 and w.P.name(blk).endswith("_stairs") and w.rng.random() < 0.65:
            w.setze(x, y, z, w.b("hay_block", axis="x"))
    H_.beet(w, a + 3, -b, a + 7, b, "gemuese")
    H_.holzstapel(w, -a - 3, -b, 3, "spruce", "z")
    hohl(w, 2)
    return w


# ============================================================================ 13 Palasthalle


def palasthalle(seed, g=2):
    """Palasthalle: auf dreistufiger Marmorterrasse mit Balustraden und Drachentreppe, rote Säulenhalle,
    doppeltes Walmdach in Goldgelb, Bronze-Kessel und Wächterlöwen."""
    w = _welt(seed)
    o = Ost(w, 21)
    u = U[g]
    a, b = _r(9 * u + 4, 6), _r(5 * u + 3, 4)
    gelaende(w, a + 14, art="wiese")
    y = 1
    for k in range(3):
        y = terrasse(w, o, -a - 6 + k * 2, -b - 6 + k * 2, a + 6 - k * 2, b + 6 - k * 2, 2 + k * 2)
    geschoss(w, o, -a, -b, a, b, y, _r(3 * u + 3, 5))
    yt = y + _r(3 * u + 3, 5)
    ostdach(w, o, -a, -b, a, b, yt, ue=3)
    geschoss(w, o, -a + 3, -b + 2, a - 3, b - 2, yt + 2, 3, veranda=False)
    ostdach(w, o, -a + 3, -b + 2, a - 3, b - 2, yt + 5, ue=3)
    for k in range(y):
        for x in range(-3, 4):
            z = b + 6 + (y - 1 - k)
            w.setze(x, k + 1, z, treppe(w, "quartz", "north") if abs(x) != 0 else w.b("chiseled_quartz_block"))
    for sx in (-1, 1):
        for yy in (1, 2):
            w.setze(sx * 6, yy, b + 10, w.b("waxed_weathered_copper") if yy == 1 else w.b("waxed_copper_block"))
        w.setze(sx * 6, 3, b + 10, w.b("gold_block"))
    hohl(w, 2)
    return w


# ============================================================================ 14 Mondtor-Garten


def mondtor(seed, g=1):
    """Gartenmauer mit rundem Mondtor, Zierfenstern, Ziegelkappe, dahinter Felsgarten, Teich und Pavillon."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    L = _r(10 * u + 5)
    R = _r(2.5 * u + 2, 3)
    gelaende(w, L + 6, art="wiese")
    for x in range(-L, L + 1):
        for y in range(1, 2 * R + 3):
            if math.hypot(x, y - R - 1) <= R + 0.3:
                continue
            w.setze(x, y, 0, o.wand(x, y, 0, 0.5))
        w.setze(x, 2 * R + 3, 0, o.dach.voll(x, 2 * R + 3, 0))
        w.setze(x, 2 * R + 3, 1, o.dach.treppe(x, 2 * R + 3, 1, "north"))
        w.setze(x, 2 * R + 3, -1, o.dach.treppe(x, 2 * R + 3, -1, "south"))
    for x, y in [(x, y) for x in range(-R - 1, R + 2) for y in range(0, 2 * R + 3) if R - 0.5 < math.hypot(x, y - R - 1) <= R + 0.6]:
        w.setze(x, y, 0, w.b("polished_andesite") if y > 0 else w.b("stone_bricks"))
    for sx in (-1, 1):
        x = sx * (R + 5)
        for y in (3, 4):
            w.setze(x, y, 0, w.b("glass_pane", north=True, south=True, east=False, west=False, waterlogged=False))
    teich(w, 4, -L // 2 - 2, L // 3)
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in range(1, 4):
                w.setze(-L // 2 + sx * 2, y, -L // 2 + sz * 2, o.saeule)
    ostdach(w, o, -L // 2 - 2, -L // 2 - 2, -L // 2 + 2, -L // 2 + 2, 4, ue=1)
    hohl(w, 2)
    return w


# ============================================================================ 15 Mauerabschnitt


def mauerabschnitt(seed, g=2):
    """Abschnitt einer großen Mauer: breiter Wehrgang mit Zinnen, die dem Gelände folgen, zwei Wachtürme mit
    Pavillondach und ein Signalfeuer."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    L = _r(24 * u + 8)
    Hm = _r(5 * u + 3, 4)
    st = Mat(w, ["stone_bricks", "cobblestone", "mossy_stone_bricks", "cracked_stone_bricks", "andesite", "stone"],
             kontrast=1.1)
    gelaende(w, L + 4, art="wiese")
    for x in range(-L, L + 1):
        hb = int(3 * math.sin(x / L * math.pi))
        for z in range(-2, 3):
            for y in range(0, Hm + hb + 1):
                w.setze(x, y, z, st(x, y, z, y / (Hm + 3)))
            w.setze(x, Hm + hb, z, w.b("stone_bricks") if (x + z) % 2 else w.b("polished_andesite"))
        for z in (-3, 3):
            for y in range(0, Hm + hb + 1):
                w.setze(x, y, z, st(x, y, z, y / (Hm + 3)))
            w.setze(x, Hm + hb + 1, z, st(x, 0, z, 0.9))
            if x % 2 == 0:
                w.setze(x, Hm + hb + 2, z, st(x, 0, z, 1.0))
    for sx in (-1, 1):
        x0 = sx * _r(L * 0.6)
        hb = int(3 * math.sin(x0 / L * math.pi))
        for y in range(0, Hm + hb + 8):
            for x in range(x0 - 3, x0 + 4):
                for z in range(-4, 5):
                    if max(abs(x - x0), abs(z) * 3 // 4) >= 3 or y < Hm + hb + 1:
                        w.setze(x, y, z, st(x, y, z, y / (Hm + 8)))
        ostdach(w, o, x0 - 3, -4, x0 + 3, 4, Hm + hb + 8, ue=2)
    w.setze(0, Hm + 4, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    hohl(w, 2)
    return w


# ============================================================================ 16 Wasserpavillon


def wasserpavillon(seed, g=1):
    """Achteckiger Wasserpavillon auf Pfählen inmitten eines Lotusteichs, mit Zickzack-Steg."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(12 * u + 6)
    gelaende(w, R + 4, art="wiese")
    teich(w, 0, 0, R - 2)
    a = _r(2.5 * u + 1.5, 2)
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            if abs(x) + abs(z) <= 2 * a + 1:
                w.setze(x, 1, z, w.b(f"{o.holz}_planks"))
                if (x + z) % 3 == 0:
                    w.setze(x, 0, z, w.b(f"{o.holz}_log", axis="y"))
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if abs(x) + abs(z) == 2 * a or (abs(x) == a and abs(z) == a):
                for y in range(2, 6):
                    if (x + z) % 2 == 0:
                        w.setze(x, y, z, o.saeule)
    ostdach(w, o, -a, -a, a, a, 6, ue=2)
    x, z = 0, a + 2
    for i in range(R):
        for d in (0, 1):
            w.setze(x + d, 1, z, w.b(f"{o.holz}_slab", type="bottom", waterlogged=False))
        z += 1
        if i % 4 == 3:
            x += 2 if (i // 4) % 2 == 0 else -2
    hohl(w, 2)
    return w


# ============================================================================ 17 Dojo


def dojo(seed, g=1):
    """Dojo: lange Übungshalle mit Holzboden, Waffenständern, Trainingspfählen im Hof und Eingangstor."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    a, b = _r(6 * u + 3, 5), _r(4 * u + 2, 3)
    gelaende(w, a + 10, art="wiese")
    y = terrasse(w, o, -a - 2, -b - 2, a + 2, b + 2, 1)
    geschoss(w, o, -a, -b, a, b, y, 5, tuer="south")
    ostdach(w, o, -a, -b, a, b, y + 5, ue=2)
    for i in range(4):
        x = -a + 2 + i * 3
        for k in range(3):
            w.setze(x, 1 + k, b + 6, w.b(f"stripped_{o.balken}_log", axis="y") if k < 2 else w.b("hay_block", axis="y"))
    torii(w, o, 0, b + 10, 2, 5)
    hohl(w, 2)
    return w


# ============================================================================ 18 Schrein


def schrein(seed, g=0):
    """Kleiner Bergschrein: Steinsockel, Holzschrein mit Seil und Glocke, Torii, Opferkästchen, Fuchsstatuen."""
    w = _welt(seed)
    o = Ost(w, seed, dach="holz")
    u = U[g]
    gelaende(w, _r(8 * u + 4), art="wald", dichte=0.9)
    y = terrasse(w, o, -3, -3, 3, 3, 2)
    geschoss(w, o, -2, -2, 2, 2, y, 3, veranda=False, tuer="south")
    ostdach(w, o, -2, -2, 2, 2, y + 3, ue=2)
    w.setze(0, y + 2, 3, w.b("bell", attachment="ceiling", facing="north", powered=False))
    torii(w, o, 0, 7, 2, 4)
    for sx in (-2, 2):
        w.setze(sx, 1, 5, w.b("stone_bricks"))
        w.setze(sx, 2, 5, w.b("white_concrete"))
        w.setze(sx, 3, 5, w.b("white_concrete_powder") if False else w.b("bone_block", axis="y"))
    hohl(w, 2)
    return w


# ============================================================================ 19 Paifang-Tor


def paifang(seed, g=1):
    """Paifang: prächtiges Ehrentor mit drei Durchgängen, gestaffelten Dächern, Goldtafel und Wächterlöwen."""
    w = _welt(seed)
    o = Ost(w, 21 if _stil(seed) else 7, gruen=_stil(seed) == 1)
    u = U[g]
    hb = _r(5 * u + 3, 4)
    H = _r(7 * u + 4, 6)
    gelaende(w, hb + 8, art="wiese", wege=[((0, -10), (0, 10))])
    rot = w.b("red_terracotta") if not o.japan else w.b("red_concrete")
    for x in (-hb, -hb // 3, hb // 3, hb):
        hh = H if abs(x) < hb else H - 2
        for y in range(1, hh):
            w.setze(x, y, 0, rot)
        w.setze(x, 0, 0, w.b("polished_andesite"))
        for dz in (-1, 1):
            w.setze(x, 1, dz, w.b("stone_bricks"))
            w.setze(x, 2, dz, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    for x in range(-hb, hb + 1):
        w.setze(x, H - 2, 0, w.b(f"stripped_{o.balken}_log", axis="x"))
        w.setze(x, H - 4, 0, w.b(f"stripped_{o.balken}_log", axis="x") if abs(x) > hb // 3 else rot)
    for x in range(-1, 2):
        w.setze(x, H - 3, 0, w.b("gold_block"))
    ostdach(w, o, -hb // 3, 0, hb // 3, 0, H, ue=2)
    for sx in (-1, 1):
        ostdach(w, o, sx * (2 * hb // 3) - hb // 4, 0, sx * (2 * hb // 3) + hb // 4, 0, H - 2, ue=2)
    for sx in (-1, 1):
        for y in (1, 2, 3):
            w.setze(sx * (hb + 3), y, 3, w.b("polished_andesite") if y == 1 else w.b("andesite_wall", up=True,
                                                                                    north="none", south="none",
                                                                                    east="none", west="none",
                                                                                    waterlogged=False) if y == 2 else
                    w.b("chiseled_stone_bricks"))
    hohl(w, 2)
    return w


# ============================================================================ 20 Laternengasse


def laternengasse(seed, g=2):
    """Laternengasse: zwei Reihen Läden mit Vordächern, rote Lampions an Leinen über der Gasse, Stände und
    ein Tor am Ende – lebt nachts auf."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    n = 2 + g
    gb = 5
    L = n * (gb + 1)
    gelaende(w, L // 2 + 8, art="wiese")
    for z in range(-L // 2 - 2, L // 2 + 3):
        for x in range(-2, 3):
            w.setze(x, 0, z, w.b("stone_bricks") if (x + z) % 3 else w.b("andesite"))
    for sx in (-1, 1):
        for i in range(n):
            z0 = -L // 2 + i * (gb + 1)
            x0, x1 = (3, 8) if sx > 0 else (-8, -3)
            et = 1 + (i + (sx > 0)) % 2
            geschoss(w, o, x0, z0, x1, z0 + gb - 1, 1, 4, veranda=False, tuer="west" if sx > 0 else "east")
            yd = 5
            if et == 2:
                geschoss(w, o, x0, z0, x1, z0 + gb - 1, 5, 3, veranda=False, tuer="west" if sx > 0 else "east")
                yd = 8
            ostdach(w, o, x0, z0, x1, z0 + gb - 1, yd, ue=1)
            xs = x0 - 1 if sx > 0 else x1 + 1
            for z in range(z0, z0 + gb):
                w.setze(xs, 4, z, o.dach.treppe(xs, 4, z, "east" if sx > 0 else "west"))
    for z in range(-L // 2, L // 2 + 1, 3):
        for x in range(-2, 3):
            w.setze(x, 7, z, w.b("chain", axis="x", waterlogged=False) if x else w.b("chain", axis="x", waterlogged=False))
        w.setze(0, 6, z, w.b("shroomlight") if z % 2 else w.b("red_wool"))
        w.setze(-1, 6, z, w.b("lantern", hanging=True, waterlogged=False))
        w.setze(1, 6, z, w.b("lantern", hanging=True, waterlogged=False))
    torii(w, o, 0, L // 2 + 4, 3, 6)
    hohl(w, 2)
    return w


FERNOST = {
    "pagode": ("Pagode", pagode),
    "tempelhalle": ("Tempelhalle", tempelhalle),
    "torbogen": ("Torii-Weg", toriiweg),
    "teehaus": ("Teehaus am Teich", teehaus),
    "zengarten": ("Zen-Garten", zengarten),
    "ostburg": ("Burg auf Steinsockel", ostburg),
    "glockenpavillon": ("Glockenpavillon", glockenpavillon),
    "bogenbruecke": ("Brückenpavillon", brueckenpavillon),
    "bambushain": ("Bambushain", bambushain),
    "kirschhain": ("Kirschblütengarten", kirschgarten),
    "reisterrassen": ("Reisterrassen", reisterrassen),
    "minka": ("Bauernhaus mit Strohdach", minka),
    "palasthalle": ("Palasthalle", palasthalle),
    "mondtor": ("Mondtor-Garten", mondtor),
    "mauerabschnitt": ("Große Mauer", mauerabschnitt),
    "wasserpavillon": ("Wasserpavillon", wasserpavillon),
    "dojo": ("Dojo", dojo),
    "steinlaterne": ("Bergschrein", schrein),
    "paifang": ("Ehrentor", paifang),
    "laternengasse": ("Laternengasse", laternengasse),
}

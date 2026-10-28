"""Uhrwerk & Maschinen – 20 Bauten mit Create-Blöcken (mit Vanilla-Ersatz): Uhrtürme, Dampfmaschinen,
Zahnradtürme, Kraftwerke, Bahnhof, Lok, Fabriken, Bohrturm, Automaton."""

from __future__ import annotations

import math

import numpy as np

import modbloecke as MB
import pracht as P
from lib import Rauschen, laub
from pracht import Mat, gelaende
from skulptur import Skulptur, dreh_y, ell, kap, kreisrand, scheibe
from weltwunder import bl, hohl, platz, sk

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    from lib import Welt
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def cr(w, name, ersatz, eprops=None, **props):
    return MB.mod(w, f"create:{name}", ersatz, eprops, **props)


class Werk:
    """Stil 0: Messing & Backstein (Steampunk). Stil 1: Andesit & Industrie-Eisen (Fabrik)."""

    def __init__(self, w, seed):
        self.w = w
        self.messing = _stil(seed) == 0
        self.casing = (lambda: cr(w, "brass_casing", "stripped_birch_log", {"axis": "y"})) if self.messing else \
            (lambda: cr(w, "andesite_casing", "polished_andesite"))
        self.metall = (lambda: cr(w, "brass_block", "raw_gold_block")) if self.messing else \
            (lambda: cr(w, "industrial_iron_block", "gray_concrete"))
        self.kupfer = lambda: cr(w, "copper_casing", "waxed_cut_copper")
        self.ziegel = lambda: cr(w, "copper_shingles", "waxed_cut_copper")
        self.glas = lambda: cr(w, "framed_glass", "glass") if self.messing else cr(w, "tiled_glass", "glass")
        self.wand = "backstein" if self.messing else "graustein"
        self.dach = "kupfer" if self.messing else "mcw_schiefer"
        self.zahn = "raw_gold_block" if self.messing else "polished_andesite"
        self.rad = "gold_block" if self.messing else "iron_block"

    def stil(self, **extra):
        d = dict(wand=self.wand, sockel="graustein", gesims="brick" if self.messing else "stone_brick",
                 dach=self.dach, holz="dark_oak", laeden=False, blumen=0, fenster="glass_pane")
        d.update(extra)
        return P.Stil(self.w, **d)


def gross_zahnrad(w, cx, cy, cz, R, achse="z", mat="raw_gold_block", nabe="iron_block", zaehne=None, speichen=4):
    """Großes Zahnrad aus Blöcken in der Ebene senkrecht zu achse."""
    zaehne = zaehne or max(8, int(R * 2.2))
    Ri = int(R) + 2
    for a in range(-Ri, Ri + 1):
        for b in range(-Ri, Ri + 1):
            r = math.hypot(a, b)
            phi = math.atan2(b, a)
            zahn = (math.cos(phi * zaehne) > 0.2) and R - 0.3 < r <= R + 1.2
            kranz = R - 1.3 < r <= R - 0.3
            sp = r <= R - 1 and any(abs(math.sin(phi - k * math.pi / speichen)) * r < 0.6 for k in range(speichen))
            n = r < 1.5
            if not (zahn or kranz or sp or n):
                continue
            blk = w.b(nabe) if n else w.b(mat)
            if achse == "z":
                w.setze(cx + a, cy + b, cz, blk)
            elif achse == "x":
                w.setze(cx, cy + b, cz + a, blk)
            else:
                w.setze(cx + a, cy, cz + b, blk)


def uhrblatt(w, cx, cy, cz, R, richtung="south", rand="gold_block", feld="white_concrete", zeiger="black_concrete",
             stunde=3, minute=0):
    """Zifferblatt mit Stundenmarken und zwei Zeigern auf einer senkrechten Wand."""
    dz = {"south": (1, 0), "north": (-1, 0), "east": (0, 1), "west": (0, -1)}[richtung]

    def p(a, b, off=0):
        if richtung in ("south", "north"):
            return (cx + a, cy + b, cz + dz[0] * off)
        return (cx + dz[1] * off, cy + b, cz + a)
    Ri = int(R) + 1
    for a in range(-Ri, Ri + 1):
        for b in range(-Ri, Ri + 1):
            r = math.hypot(a, b)
            if r <= R:
                phi = math.atan2(b, a)
                marke = R - 1.6 < r < R - 0.6 and abs(math.sin(phi * 6)) < 0.25
                w.setze(*p(a, b), w.b(rand) if r > R - 0.8 or marke else w.b(feld))
    for t in np.linspace(0, R * 0.55, int(R) + 2):
        a = math.radians(90 - stunde * 30)
        w.setze(*p(round(math.cos(a) * t), round(math.sin(a) * t), 1), w.b(zeiger))
    for t in np.linspace(0, R * 0.85, int(R * 1.5) + 2):
        a = math.radians(90 - minute * 30)
        w.setze(*p(round(math.cos(a) * t), round(math.sin(a) * t), 1), w.b(zeiger))
    w.setze(*p(0, 0, 1), w.b(rand))


def schornstein(w, x, z, y0, H, mat="bricks", kopf="polished_blackstone_bricks", rauch=True):
    for y in range(y0, y0 + H):
        for xx, zz in kreisrand(1.4, x, z):
            w.setze(xx, y, zz, w.b(kopf) if y > y0 + H - 3 or (y - y0) % 7 == 6 else w.b(mat))
    if rauch:
        w.setze(x, y0 + H - 1, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))


def rohr(w, pts, mat="waxed_copper_block"):
    for (x0, y0, z0), (x1, y1, z1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
        for i in range(n + 1):
            t = i / max(1, n)
            w.setze(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), round(z0 + (z1 - z0) * t),
                    cr(w, "fluid_pipe", mat, up=False, down=False, north=False, south=False, east=False, west=False,
                       waterlogged=False) if False else w.b(mat))


def industrieboden(w, R, cx=0, cz=0):
    rng = w.rng
    r1 = Rauschen(w, 4)
    for x, z in scheibe(R, cx, cz):
        v = r1(x, 0, z)
        w.setze(x, 0, z, w.b("gravel") if v < 0.3 else w.b("cobblestone") if v < 0.45 else
                w.b("stone_bricks") if v < 0.6 else w.b("grass_block", snowy=False) if v > 0.8 else
                w.b("andesite"))
        if w.frei(x, 1, z) and rng.random() < 0.02:
            w.setze(x, 1, z, w.b("barrel", facing="up", open=False) if rng.random() < 0.5 else
                    w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))


# ============================================================================ Bauten


def uhrturm(seed, g=2):
    """Großer Uhrturm: quadratischer Backstein- oder Steinturm mit vier riesigen Zifferblättern, sichtbarem Uhrwerk
    hinter Glas, Glockenstube, Kupferhelm und Zahnrädern an der Fassade."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    a = _r(3 * u + 2, 3)
    H = _r(18 * u + 8)
    industrieboden(w, a + 8)
    st = k.stil()
    P.gebaeude(w, st, -a, -a, a, a, y0=1, etagen=max(2, H // 5), eh=5, dach="walm", tuer="south", gauben=False,
               kamine=0, steil=True)
    top = 1 + 1 + max(2, H // 5) * 5
    yc = top - 4 - a
    for richtung in ("south", "north", "east", "west"):
        off = a + 1
        if richtung == "south":
            uhrblatt(w, 0, yc, off, a, richtung)
        elif richtung == "north":
            uhrblatt(w, 0, yc, -off, a, richtung)
        elif richtung == "east":
            uhrblatt(w, off, yc, 0, a, richtung)
        else:
            uhrblatt(w, -off, yc, 0, a, richtung)
    for sx in (-1, 1):
        gross_zahnrad(w, sx * (a + 1), yc - a - 3, sx * (a - 1), max(2, a * 0.6), achse="x", mat=k.zahn)
    w.setze(0, top - 2, 0, w.b("bell", attachment="ceiling", facing="north", powered=False))
    hohl(w, 2)
    return w


def dampfmaschinenhalle(seed, g=2):
    """Dampfmaschinenhalle: lange Halle mit Bogenfenstern, darin riesige Schwungräder, Kessel mit Dampfpfeifen,
    zwei hohe Schornsteine und Rohrleitungen außen."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    a, b = _r(8 * u + 4), _r(4 * u + 3)
    industrieboden(w, a + 8)
    st = k.stil(fensterart="bogen")
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=_r(5 * u + 4), dach="sattel", tuer="east", gauben=False,
               kamine=0)
    H = _r(5 * u + 4) + 2
    for i in range(2 + (g >= 2)):
        x = -a + 3 + i * max(5, (2 * a - 6) // max(1, 1 + (g >= 2)))
        gross_zahnrad(w, x, 1 + _r(b * 0.6), 0, b * 0.6, achse="x", mat=k.rad, zaehne=6, speichen=3)
    for sx in (-1, 1):
        schornstein(w, sx * (a - 2), -b - 3, 1, _r(18 * u + 6))
    for x in range(-a + 1, a, 3):
        rohr(w, [(x, 1, b + 2), (x, H, b + 2), (x, H, b + 1)])
    for k2 in range(3):
        for xx, zz in kreisrand(1.5, -a + 3 + k2 * 4, b + 5):
            for y in range(1, 5):
                w.setze(xx, y, zz, k.kupfer() if y < 4 else w.b("waxed_cut_copper"))
        w.setze(-a + 3 + k2 * 4, 5, b + 5, cr(w, "steam_whistle", "lightning_rod",
                                               {"facing": "up", "powered": False, "waterlogged": False},
                                               facing="north", powered=False, size="large", wall=False))
    hohl(w, 2)
    return w


def zahnradturm(seed, g=2):
    """Zahnradturm: offener Stahlturm aus Trägern, in dem übereinander riesige Zahnräder greifen, mit Wellen,
    Treppe und einer Uhr an der Spitze."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    H = _r(20 * u + 8)
    B = _r(3 * u + 2, 3)
    industrieboden(w, B + 8)
    for y in range(1, H):
        for sx in (-B, B):
            for sz in (-B, B):
                w.setze(sx, y, sz, cr(w, "metal_girder", "iron_block" if False else "polished_basalt",
                                      {"axis": "y"}, axis="y", top=False, bottom=False, x=False, z=False,
                                      waterlogged=False))
        if y % 6 == 0:
            for t in range(-B, B + 1):
                for (x, z) in ((t, -B), (t, B), (-B, t), (B, t)):
                    w.setze(x, y, z, k.casing())
    n = max(2, H // (2 * B + 4))
    for i in range(n):
        y = 3 + i * (H - 6) // n + B
        gross_zahnrad(w, 0, y, 0, B + (i % 2) * 0.8, achse="z" if i % 2 else "x", mat=k.zahn)
    for y in range(2, H - 2):
        w.setze(0, y, B + 1, MB.welle(w, "y") if False else cr(w, "shaft", "chain", {"axis": "y", "waterlogged": False},
                                                               axis="y", waterlogged=False))
    for x in range(-B, B + 1):
        for z in range(-B, B + 1):
            w.setze(x, H, z, k.casing())
    uhrblatt(w, 0, H + B + 1, 0, B, "south")
    for y in range(H + 1, H + 2 * B + 3):
        for x in range(-B, B + 1):
            w.setze(x, y, -1, k.metall()) if abs(x) == B or y in (H + 1, H + 2 * B + 2) else None
    hohl(w, 2)
    return w


def windkraftwerk(seed, g=2):
    """Windkraftwerk: hoher Holz- und Messingturm mit Windmühlenlager und acht Segeln (Create-Segel), Getriebehaus
    am Fuß und Wellen, die in die Erde führen."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    H = _r(14 * u + 6)
    gelaende(w, _r(12 * u + 6), art="wiese", dichte=0.3)
    for y in range(1, H):
        r = 2.2 * u + 1.5 - y / H * 1.2
        for x, z in kreisrand(max(1.0, r)):
            w.setze(x, y, z, w.b("spruce_planks") if y % 4 else k.casing())
    w.setze(0, H, 0, k.casing())
    w.setze(0, H, 1, cr(w, "windmill_bearing", "dispenser", {"facing": "south", "triggered": False}, facing="south"))
    L = _r(10 * u + 4)
    for i in range(8):
        a = i / 8 * 2 * math.pi
        for t in range(1, L + 1):
            x, y = round(math.cos(a) * t), round(H + math.sin(a) * t)
            w.setze(x, y, 2, w.b("stripped_spruce_log", axis="x" if abs(math.cos(a)) > 0.7 else "y"))
            if t > 2 and i % 2 == 0:
                for q in (1, 2):
                    px = round(math.cos(a) * t - math.sin(a) * q)
                    py = round(H + math.sin(a) * t + math.cos(a) * q)
                    w.setze(px, py, 2, cr(w, "white_sail", "white_wool", facing="south"))
    st = k.stil()
    P.gebaeude(w, st, -3, -_r(H * 0.3) - 6, 3, -_r(H * 0.3) - 1, y0=1, etagen=1, eh=4, dach="sattel",
               tuer="south", gauben=False, kamine=0)
    hohl(w, 2)
    return w


def wasserkraftwerk(seed, g=2):
    """Wasserkraftwerk: eine Reihe von Wasserrädern an einem Kanal, dahinter das Generatorhaus mit Wellen,
    Getrieben und Kupferdach, Schleuse und Steg."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    n = 2 + g
    L = n * 6 + 4
    gelaende(w, L + 4, art="wiese", dichte=0.2)
    for x in range(-L, L + 1):
        for z in range(2, 7):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("stone_bricks"))
        for z in (1, 7):
            w.setze(x, 0, z, w.b("stone_bricks"))
            w.setze(x, 1, z, w.b("stone_brick_wall", up=False, north="none", south="none", east="low", west="low",
                                 waterlogged=False))
    st = k.stil()
    P.gebaeude(w, st, -n * 3 - 2, -8, n * 3 + 2, -1, y0=1, etagen=2, eh=4, dach="sattel", tuer="north",
               gauben=False, kamine=0)
    Rr = 2 + u
    for i in range(n):
        x = -n * 3 + 1 + i * 6
        for a in range(-round(Rr), round(Rr) + 1):
            for b in range(-round(Rr), round(Rr) + 1):
                r = math.hypot(a, b)
                if Rr - 0.7 <= r <= Rr + 0.3 or (r <= Rr and (a == 0 or b == 0)):
                    w.setze(x + a, round(Rr) + b, 4, w.b("spruce_planks") if r > Rr - 0.7 else
                            w.b("stripped_spruce_log", axis="z"))
        w.setze(x, round(Rr), 4, cr(w, "water_wheel", "spruce_log", {"axis": "z"}, facing="south"))
        for z in (3, 2, 1, 0):
            w.setze(x, round(Rr), z, cr(w, "shaft", "chain", {"axis": "z", "waterlogged": False}, axis="z",
                                        waterlogged=False))
        w.setze(x, round(Rr), -1, MB.zahnrad(w, "z", gross=True))
    hohl(w, 2)
    return w


def fabrikhalle(seed, g=2):
    """Fabrikhalle: Backsteinhalle mit Sheddach (Sägezahndach mit Glasflächen), Rolltoren, Ladekränen, Schornstein,
    Laufbändern und Kistenstapeln auf dem Hof."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    a, b = _r(10 * u + 5), _r(6 * u + 4)
    industrieboden(w, a + 6)
    H = _r(4 * u + 4)
    M = Mat(w, ["bricks", "bricks", "mud_bricks", "granite"] if k.messing else
            ["stone_bricks", "polished_andesite", "andesite", "cracked_stone_bricks"])
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            rand = x in (-a, a) or z in (-b, b)
            if rand:
                for y in range(1, H + 1):
                    fen = y in (2, 3) and (x + z) % 4 == 0 and not (x in (-a, a) and z in (-b, b))
                    w.setze(x, y, z, k.glas() if fen else M(x, y, z, y / H))
    zahn = 4
    for x in range(-a, a + 1):
        q = (x + a) % zahn
        for z in range(-b, b + 1):
            y = H + 1 + q
            w.setze(x, y, z, k.ziegel() if q < zahn - 1 else k.glas())
            if q == zahn - 1:
                for yy in range(H + 1, y):
                    w.setze(x, yy, z, k.glas())
    for z in (-b, b):
        for y in range(1, 4):
            for x in range(-2, 3):
                w.setze(x, y, z, w.b("iron_trapdoor", facing="south", half="bottom", open=True, powered=False,
                                     waterlogged=False) if y < 3 else w.b("iron_block"))
    schornstein(w, a + 3, 0, 1, _r(16 * u + 8))
    for x in range(-a, a + 1):
        w.setze(x, 1, b + 3, cr(w, "belt", "smooth_stone_slab", {"type": "bottom", "waterlogged": False},
                                facing="east", slope="horizontal", part="middle" if -a < x < a else
                                ("start" if x == -a else "end"), casing=False, waterlogged=False) if False else
                w.b("smooth_stone_slab", type="bottom", waterlogged=False))
    for i in range(6):
        w.setze(-a + 2 + i * 2, 2, b + 3, MB.ware(w, w.rng) if i % 2 else w.b("barrel", facing="up", open=False))
    hohl(w, 2)
    return w


def bohrturm(seed, g=2):
    """Bohrturm: Fachwerk-Bohrgerüst aus Trägern über einer Grube, mechanischer Bohrkopf, Seilrollen, Erzloren,
    Förderband und Schutthalde."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    H = _r(16 * u + 6)
    B = _r(3 * u + 2, 3)
    industrieboden(w, B + 10)
    for x, z in scheibe(B - 0.5):
        for y in range(-4, 1):
            w.bloecke.pop((x, y, z), None)
    for y in range(1, H):
        bb = max(1, round(B * (1 - 0.6 * y / H)))
        for sx in (-1, 1):
            for sz in (-1, 1):
                w.setze(sx * bb, y, sz * bb, cr(w, "metal_girder", "polished_basalt", {"axis": "y"}, axis="y",
                                                top=False, bottom=False, x=False, z=False, waterlogged=False))
        if y % 4 == 0:
            for t in range(-bb, bb + 1):
                for (x, z) in ((t, -bb), (t, bb), (-bb, t), (bb, t)):
                    w.setze(x, y, z, w.b("iron_bars", north=True, south=True, east=True, west=True, waterlogged=False))
    w.setze(0, H, 0, k.casing())
    for y in range(-3, H):
        w.setze(0, y, 0, cr(w, "shaft", "chain", {"axis": "y", "waterlogged": False}, axis="y", waterlogged=False))
    w.setze(0, -4, 0, cr(w, "mechanical_drill", "iron_block", facing="down", waterlogged=False))
    w.setze(0, H + 1, 0, MB.zahnrad(w, "x", gross=True))
    r_n = Rauschen(w, 3)
    for x, z in scheibe(5 * u + 2, B + 6, 0):
        hh = int((1 - math.hypot(x - B - 6, z) / (5 * u + 2)) * (3 * u + 1) * (0.7 + 0.5 * r_n(x, 0, z)))
        for y in range(1, hh + 1):
            w.setze(x, y, z, w.b(["gravel", "cobblestone", "andesite", "iron_ore", "coal_ore"][(x * 3 + y + z) % 5]))
    for x in range(-B - 6, -B):
        w.setze(x, 1, 0, w.b("rail", shape="east_west", waterlogged=False))
    w.setze(-B - 4, 2, 0, w.b("hopper", facing="down", enabled=True) if False else w.b("raw_iron_block"))
    hohl(w, 2)
    return w


def bahnhof(seed, g=2):
    """Bahnhof: Empfangsgebäude mit Uhr und Bogenhalle aus Glas und Eisen über zwei Gleisen (Create-Schienen),
    Bahnsteige mit Laternen, Bänken und Gepäck."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    L = _r(14 * u + 6)
    industrieboden(w, L + 4)
    for z in (-3, 3):
        for x in range(-L, L + 1):
            w.setze(x, 0, z, w.b("gravel"))
            w.setze(x, 1, z, cr(w, "track", "rail", {"shape": "east_west", "waterlogged": False}, shape="xo",
                                turn=False, waterlogged=False))
    for z in (-6, -5, 0, 5, 6):
        for x in range(-L + 2, L - 1):
            w.setze(x, 1, z, w.b("smooth_stone") if z != 0 else w.b("polished_andesite"))
    Hh = _r(6 * u + 5)
    for x in range(-L + 2, L - 1, 4):
        for z in (-7, 7):
            for y in range(2, Hh):
                w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                     waterlogged=False) if False else cr(w, "metal_girder", "polished_basalt",
                                                                         {"axis": "y"}, axis="y", top=False,
                                                                         bottom=False, x=False, z=False,
                                                                         waterlogged=False))
        for t in range(-7, 8):
            yb = round(Hh + 3 * math.cos(t / 7 * math.pi / 2))
            w.setze(x, yb, t, k.metall())
    for x in range(-L + 2, L - 1):
        for t in range(-7, 8):
            yb = round(Hh + 3 * math.cos(t / 7 * math.pi / 2))
            if (x + L) % 4:
                w.setze(x, yb, t, k.glas())
    st = k.stil(fensterart="bogen")
    P.gebaeude(w, st, -_r(5 * u + 3), -18 - _r(3 * u), _r(5 * u + 3), -9, y0=1, etagen=2, eh=5, dach="walm",
               tuer="south", gauben=True, kamine=0)
    uhrblatt(w, 0, 9, -8, 2 + u * 0.5, "south")
    for x in range(-L + 4, L - 3, 6):
        MB.strassenlampe(w, x, 2, 0)
    hohl(w, 2)
    return w


def dampflok(seed, g=2):
    """Dampflok: eine große Dampflokomotive mit Kessel, Schornstein, Führerhaus, roten Speichenrädern und Tender
    auf einem Gleisstück mit Prellbock."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    s = 0.6 * u + 0.3
    L = _r(16 * s + 6)
    industrieboden(w, L + 3)
    for x in range(-L, L + 1):
        w.setze(x, 0, 0, w.b("gravel"))
        w.setze(x, 1, 0, cr(w, "track", "rail", {"shape": "east_west", "waterlogged": False}, shape="xo",
                            turn=False, waterlogged=False))
    S = Skulptur(w, s)
    farbe = "black_concrete" if k.messing else "green_concrete"
    S.mat("k", bl(w, farbe))
    S.mat("m", bl(w, "raw_gold_block" if k.messing else "iron_block"))
    S.mat("r", bl(w, "red_concrete"))
    S.mat("h", bl(w, "dark_oak_planks"))
    S.mat("g", bl(w, "glass"))
    S.mat("d", bl(w, "gray_concrete"))
    S.plus(kap((-2, 5, 0), (9, 5, 0), 2.6, 2.6), "k")
    S.plus(lambda X, Y, Z: (np.abs(np.sqrt((Y - 5) ** 2 + Z * Z) - 2.7) < 0.35) & (np.mod(X, 3) < 0.6) & (X > -2) &
           (X < 9), "m")
    S.plus(kap((7, 7.5, 0), (7, 10.5, 0), 0.9, 1.3), "k")
    S.plus(ell(3, 8, 0, 1.0, 0.8, 1.0), "m")
    S.plus(lambda X, Y, Z: (X > -7) & (X < -2) & (Y > 2) & (Y < 10) & (np.abs(Z) < 3), "k")
    S.minus(lambda X, Y, Z: (X > -6.4) & (X < -2.6) & (Y > 6) & (Y < 9) & (np.abs(Z) > 2.4))
    S.plus(lambda X, Y, Z: (X > -7.5) & (X < -1.5) & (Y > 9.6) & (Y < 10.6) & (np.abs(Z) < 3.4), "d")
    for wx in (-4.5, 0.5, 4.5):
        for sz in (-1, 1):
            S.plus(lambda X, Y, Z, wx=wx, sz=sz: ((X - wx) ** 2 + (Y - 2.4) ** 2 < 4.4) & (np.abs(Z - sz * 2.4) < 0.5),
                   "r")
    S.plus(lambda X, Y, Z: (X > -16) & (X < -8) & (Y > 2) & (Y < 7) & (np.abs(Z) < 2.6), "k")
    S.plus(lambda X, Y, Z: (X > -15.5) & (X < -8.5) & (Y > 6.5) & (Y < 7.5) & (np.abs(Z) < 2.2), "h")
    for wx in (-14, -10):
        for sz in (-1, 1):
            S.plus(lambda X, Y, Z, wx=wx, sz=sz: ((X - wx) ** 2 + (Y - 1.8) ** 2 < 2.4) & (np.abs(Z - sz * 2.2) < 0.5),
                   "r")
    S.plus(lambda X, Y, Z: (X > 11) & (X < 12) & (Y > 1) & (Y < 3) & (np.abs(Z) < 2.6), "r")
    S.rendern((-17, 0, -4), (13, 12, 4), versatz=(0.5, 1.01, 0.5))
    w.setze(round(7 * s), round(1 + 10.5 * s), 0, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                       waterlogged=False))
    for z in (-1, 1):
        w.setze(L, 1, z, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                             west="none", waterlogged=False))
    w.setze(L, 2, 0, w.b("red_concrete"))
    hohl(w, 2)
    return w


def luftschiffwerft(seed, g=2):
    """Luftschiffwerft: hoher Hangar aus Trägern und Glas, darin ein Luftschiff mit Messinggondel und Propellern
    (Zahnräder), Kräne und Gaszylinder (Tanks)."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    L, B = _r(14 * u + 6), _r(6 * u + 4)
    industrieboden(w, L + 4)
    Hh = _r(10 * u + 6)
    for x in range(-L, L + 1, 4):
        for t in range(-B, B + 1):
            y = round(Hh * math.sqrt(max(0, 1 - (t / B) ** 2)))
            w.setze(x, max(1, y), t, cr(w, "metal_girder", "polished_basalt", {"axis": "y"}, axis="y", top=False,
                                        bottom=False, x=False, z=False, waterlogged=False))
            for yy in range(1, y):
                if abs(t) == B:
                    w.setze(x, yy, t, cr(w, "metal_girder", "polished_basalt", {"axis": "y"}, axis="y", top=False,
                                         bottom=False, x=False, z=False, waterlogged=False))
    for x in range(-L, L + 1):
        if x % 4:
            for t in range(-B, B + 1):
                y = round(Hh * math.sqrt(max(0, 1 - (t / B) ** 2)))
                if abs(t) > B * 0.3:
                    w.setze(x, max(1, y), t, k.glas())
    Lb, Rb = L * 0.7, B * 0.45
    S = Skulptur(w, 1.0)
    S.mat("b", lambda x, y, z, *_: w.b("light_gray_wool") if (x // 3) % 2 else w.b("white_wool"))
    S.mat("g", lambda x, y, z, *_: k.metall())
    S.plus(ell(0, 0, 0, Lb, Rb, Rb), "b")
    S.plus(lambda X, Y, Z: (np.abs(X) < Lb * 0.35) & (Y < -Rb - 0.5) & (Y > -Rb - 3) & (np.abs(Z) < Rb * 0.45), "g")
    S.rendern((-Lb - 1, -Rb - 4, -Rb - 1), (Lb + 1, Rb + 1, Rb + 1), versatz=(0.5, Hh * 0.55, 0.5))
    for sz in (-1, 1):
        w.setze(-round(Lb * 0.3), round(Hh * 0.55 - Rb - 2), sz * round(Rb * 0.6), MB.zahnrad(w, "x", gross=True))
    for i in range(3):
        for xx, zz in kreisrand(1.5, L + 4, -B + i * B):
            for y in range(1, 6):
                w.setze(xx, y, zz, cr(w, "fluid_tank", "waxed_copper_block", bottom=y == 1, top=y == 5,
                                      shape="window" if y in (2, 3, 4) else "plain"))
    hohl(w, 2)
    return w


def tanklager(seed, g=2):
    """Tanklager: große runde Tanks mit Fenstern, verbunden durch Rohrbrücken, Ventilräder, Pumpenhaus und
    Treppen außen an den Tanks."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    R = 10 * u + 5
    industrieboden(w, _r(R + 3))
    n = 3 + g
    pos = []
    for i in range(n):
        a = i / n * 2 * math.pi + 0.3
        d = R * 0.55
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        rr = 2 + 1.2 * u
        H = _r(6 * u + 4 + (i % 2) * 3)
        for y in range(1, H + 1):
            for x, z in kreisrand(rr, cx, cz):
                w.setze(x, y, z, cr(w, "fluid_tank", "waxed_copper_block", bottom=y == 1, top=y == H,
                                    shape="window" if 1 < y < H and (x + z) % 3 == 0 else "plain")
                        if k.messing else w.b("white_concrete") if y % 4 else w.b("light_gray_concrete"))
        for x, z in scheibe(rr, cx, cz):
            w.setze(x, H + 1, z, k.kupfer() if k.messing else w.b("smooth_stone"))
        for t in range(H):
            aa = t * 0.35
            w.setze(round(cx + math.cos(aa) * (rr + 1)), t + 1, round(cz + math.sin(aa) * (rr + 1)),
                    w.b("smooth_stone_slab", type="top", waterlogged=False))
        pos.append((cx, cz, H))
    for (ax, az, ah), (bx, bz, bh) in zip(pos, pos[1:] + pos[:1]):
        yy = min(ah, bh) - 1
        rohr(w, [(ax, yy, az), (bx, yy, az), (bx, yy, bz)])
    st = k.stil()
    P.gebaeude(w, st, -3, -3, 3, 3, y0=1, etagen=1, eh=4, dach="walm", tuer="south", gauben=False, kamine=0)
    hohl(w, 2)
    return w


def werkstatt(seed, g=1):
    """Tüftler-Werkstatt: Fachwerk-Werkstatt mit großem Rolltor, Werkbänken, Werkzeugkästen, Mechanik-Armen
    (Deployer), Depots, Zahnrädern an der Wand und einer Seilwinde."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    a, b = _r(5 * u + 3, 4), _r(4 * u + 2, 3)
    industrieboden(w, a + 7)
    st = k.stil(fachwerk=True, wand="putz" if k.messing else "graustein")
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="sattel", tuer="south", kamine=1)
    for x in range(-a + 1, a, 2):
        w.setze(x, 1, -b + 1, w.b("crafting_table") if x % 4 else cr(w, "depot", "smooth_stone_slab",
                                                                         {"type": "bottom", "waterlogged": False},
                                                                         waterlogged=False))
    farben = ["red", "blue", "yellow", "green", "brown"]
    for i, x in enumerate(range(-a + 1, a, 3)):
        w.setze(x, 1, b - 1, cr(w, f"{farben[i % 5]}_toolbox", "chest", {"facing": "north", "type": "single",
                                                                       "waterlogged": False},
                                facing="north", waterlogged=False))
    for i in range(3):
        w.setze(a + 1, 3 + i, -b + 1 + i * 2, MB.zahnrad(w, "x", gross=i % 2 == 0))
    w.setze(-a - 1, 4, 0, cr(w, "deployer", "dispenser", {"facing": "west", "triggered": False}, facing="west",
                             axis_along_first=True))
    hohl(w, 2)
    return w


def kuckucksuhrhaus(seed, g=1):
    """Kuckucksuhr-Haus: ein Schwarzwaldhaus in Form einer riesigen Kuckucksuhr – geschnitzter Giebel mit Vogel,
    großes Zifferblatt, Pendel und Tannenzapfen-Gewichte an Ketten, Holzschindeldach."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    a, b = _r(4 * u + 3, 4), _r(3 * u + 2, 3)
    gelaende(w, a + 8, art="wald", dichte=0.4)
    st = P.Stil(w, wand="holz_dunkel", sockel="graustein", gesims="stone_brick", dach="mcw_holz", holz="dark_oak",
                laeden=True, blumen=0.7)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="sattel", first_x=False, tuer="east", kamine=0,
               steil=True)
    R = max(2, a - 1)
    uhrblatt(w, 0, 6, b + 1, R, "south", rand="spruce_planks", feld="white_terracotta")
    for y in range(1, 4):
        w.setze(0, 6 - R - y, b + 1, w.b("chain", axis="y", waterlogged=False))
    w.setze(0, 6 - R - 4, b + 1, w.b("gold_block"))
    for sx in (-2, 2):
        for y in range(1, 5):
            w.setze(sx, 6 - R - y, b + 1, w.b("chain", axis="y", waterlogged=False))
        w.setze(sx, 6 - R - 5, b + 1, w.b("spruce_log", axis="y"))
    w.setze(0, 6 + R + 2, b + 1, cr(w, "cuckoo_clock", "spruce_trapdoor",
                                    {"facing": "south", "half": "bottom", "open": False, "powered": False,
                                     "waterlogged": False}, facing="south"))
    w.setze(0, 6 + R + 3, b + 2, w.b("yellow_concrete"))
    hohl(w, 2)
    return w


def kuehlturm(seed, g=2):
    """Kraftwerk mit Kühlturm: hyperbolischer Kühlturm aus Beton, Maschinenhaus, Schornstein und Rohrleitungen,
    Dampf aus dem Kühlturm (Spinnweben-Optik)."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    R0 = 6 * u + 4
    H = _r(16 * u + 8)
    industrieboden(w, _r(R0 * 2 + 4))
    for y in range(1, H + 1):
        t = y / H
        r = R0 * (0.65 + 0.4 * (2 * t - 1.1) ** 2)
        for x, z in kreisrand(r):
            w.setze(x, y, z, w.b("light_gray_concrete") if (y // 3) % 4 else w.b("white_concrete"))
    for i in range(int(R0 * 3)):
        a = w.rng.random() * 2 * math.pi
        d = w.rng.random() * R0 * 0.6
        w.setze(round(math.cos(a) * d), H + 1 + int(w.rng.integers(0, 4)), round(math.sin(a) * d), w.b("cobweb"))
    st = k.stil()
    P.gebaeude(w, st, round(R0) + 3, -5, round(R0 * 2) + 3, 5, y0=1, etagen=2, eh=5, dach="sattel", tuer="east",
               gauben=False, kamine=0)
    schornstein(w, round(R0 * 2) + 6, -6, 1, _r(H * 1.1))
    rohr(w, [(round(R0) + 2, 4, 0), (round(R0) - 1, 4, 0)])
    hohl(w, 2)
    return w


def schwebebahn(seed, g=2):
    """Schwebebahn: eine Hochbahn auf Stahlträger-Stützen in A-Form, eine hängende Gondel aus Messing und Glas,
    Bahnhofsplattform mit Treppe."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    L = _r(18 * u + 8)
    H = _r(8 * u + 6)
    gelaende(w, L + 3, art="wiese", dichte=0.2)
    for x in range(-L, L + 1):
        w.setze(x, H, 0, cr(w, "metal_girder", "polished_basalt", {"axis": "x"}, axis="x", top=False, bottom=False,
                            x=True, z=False, waterlogged=False))
        w.setze(x, H + 1, 0, k.metall() if x % 3 == 0 else w.b("iron_bars", east=True, west=True, north=False,
                                                                south=False, waterlogged=False))
    for x in range(-L, L + 1, max(6, L // 2)):
        for y in range(1, H):
            sp = round((H - y) / H * 3)
            for sz in (-sp, sp):
                w.setze(x, y, sz, cr(w, "metal_girder", "polished_basalt", {"axis": "y"}, axis="y", top=False,
                                     bottom=False, x=False, z=False, waterlogged=False))
    gx = round(L * 0.3)
    for y in range(H - 2, H):
        w.setze(gx, y, 0, w.b("chain", axis="y", waterlogged=False))
    for x in range(gx - 3, gx + 4):
        for z in (-1, 0, 1):
            for y in range(H - 6, H - 2):
                rand = x in (gx - 3, gx + 3) or z in (-1, 1) or y in (H - 6, H - 3)
                if rand:
                    w.setze(x, y, z, k.metall() if y in (H - 6, H - 3) or x in (gx - 3, gx + 3) else k.glas())
    for x in range(-L, -L + 7):
        for z in range(-3, 4):
            w.setze(x, H - 6, z, w.b("smooth_stone"))
    for k2 in range(H - 6):
        w.setze(-L + 7 + k2, H - 6 - k2, 3, w.b("stone_brick_stairs", facing="west", half="bottom", shape="straight",
                                                  waterlogged=False))
    hohl(w, 2)
    return w


def aufzugsturm(seed, g=2):
    """Aufzugsturm: schlanker Stahlturm mit gläserner Aufzugskabine, Seilrolle (Aufzugsrolle) oben,
    Aussichtsplattform und Messinggeländer."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    H = _r(20 * u + 10)
    B = 2
    gelaende(w, _r(8 * u + 4), art="wiese", dichte=0.3)
    for y in range(1, H):
        for sx in (-B, B):
            for sz in (-B, B):
                w.setze(sx, y, sz, cr(w, "metal_girder", "polished_basalt", {"axis": "y"}, axis="y", top=False,
                                      bottom=False, x=False, z=False, waterlogged=False))
        if y % 5 == 0:
            for t in range(-B, B + 1):
                for (x, z) in ((t, -B), (t, B), (-B, t), (B, t)):
                    w.setze(x, y, z, w.b("iron_bars", north=True, south=True, east=True, west=True, waterlogged=False))
    yk = round(H * 0.4)
    for x in range(-1, 2):
        for z in range(-1, 2):
            for y in range(yk, yk + 3):
                if x == 0 and z == 0 and y < yk + 2:
                    continue
                w.setze(x, y, z, k.glas() if 0 < y - yk < 2 else k.metall())
    for y in range(yk + 3, H):
        w.setze(0, y, 0, w.b("chain", axis="y", waterlogged=False))
    w.setze(0, H, 0, cr(w, "elevator_pulley", "iron_block", facing="north"))
    Rp = 3 + u
    for x, z in scheibe(Rp):
        w.setze(x, H + 1, z, w.b("smooth_stone") if (x + z) % 2 else k.metall())
    for x, z in kreisrand(Rp + 0.5):
        w.setze(x, H + 2, z, w.b("iron_bars", north=True, south=True, east=True, west=True, waterlogged=False))
    hohl(w, 2)
    return w


def erntemaschine(seed, g=1):
    """Automatische Farm: Weizenfelder mit einer fahrenden Erntebrücke (Mähwerke, Wellen), Silo und Scheune,
    Wasserkanäle zwischen den Reihen."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    L, B = _r(10 * u + 5), _r(6 * u + 3)
    gelaende(w, L + 6, art="wiese", dichte=0.2)
    for x in range(-L, L + 1):
        for z in range(-B, B + 1):
            if z % 5 == 0:
                w.setze(x, 0, z, w.b("water", level=0))
            else:
                w.setze(x, 0, z, w.b("farmland", moisture=7))
                w.setze(x, 1, z, w.b("wheat", age=7) if (x + z) % 7 else w.b("carrots", age=7))
    xb = round(L * 0.2)
    for z in range(-B - 1, B + 2):
        w.setze(xb, 4, z, k.casing())
        w.setze(xb + 1, 3, z, cr(w, "mechanical_harvester", "iron_trapdoor",
                                 {"facing": "east", "half": "top", "open": False, "powered": False,
                                  "waterlogged": False}, facing="east", waterlogged=False))
    for z in (-B - 1, B + 1):
        for y in range(1, 4):
            w.setze(xb, y, z, k.casing())
    from wueste_eis import kuppel
    for y in range(1, _r(10 * u + 5)):
        for x, z in kreisrand(2.5, -L - 4, 0):
            w.setze(x, y, z, k.kupfer() if y % 3 else w.b("waxed_cut_copper"))
    kuppel(w, w.b("waxed_cut_copper"), -L - 4, 0, _r(10 * u + 5), 2.8, spitze=None)
    hohl(w, 2)
    return w


def blitzturm(seed, g=2):
    """Blitzturm: ein Teslaturm aus Kupferspiralen und Blitzableitern auf einem Basaltsockel, darüber eine
    Kupferkugel, Spulen und Leuchtglas, Gerätehäuschen daneben."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    H = _r(14 * u + 6)
    industrieboden(w, _r(8 * u + 5))
    for k2 in range(3):
        for x, z in scheibe(3 - k2 * 0.8 + u):
            w.setze(x, 1 + k2, z, w.b("polished_basalt", axis="y") if k2 < 2 else w.b("smooth_basalt"))
    for y in range(4, H):
        a = y * 0.7
        for d in (0, math.pi):
            x, z = round(math.cos(a + d) * 1.6), round(math.sin(a + d) * 1.6)
            w.setze(x, y, z, w.b("waxed_copper_block") if y % 2 else w.b("waxed_cut_copper"))
        w.setze(0, y, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False) if y > H - 3 else
                w.b("iron_block"))
    S = Skulptur(w, 1.0)
    S.mat("k", lambda x, y, z, *_: w.b("waxed_copper_block") if (x + y + z) % 3 else w.b("waxed_exposed_copper"))
    S.plus(lambda X, Y, Z: np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (1.6 + u)) < 0.6, "k")
    S.rendern((-5, -5, -5), (5, 5, 5), versatz=(0.5, H + 2 + u, 0.5))
    w.setze(0, H + 2 + round(u), 0, w.b("sea_lantern"))
    for i in range(4):
        a = i / 4 * 2 * math.pi
        x, z = round(math.cos(a) * (4 + u)), round(math.sin(a) * (4 + u))
        for y in range(1, 4 + g):
            w.setze(x, y, z, w.b("waxed_copper_block"))
        w.setze(x, 4 + g, z, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    st = k.stil()
    P.gebaeude(w, st, round(6 * u + 3), -2, round(6 * u + 7), 2, y0=1, etagen=1, eh=4, dach="sattel", tuer="west",
               gauben=False, kamine=0)
    hohl(w, 2)
    return w


def automaton(seed, g=2):
    """Automaton: eine riesige mechanische Figur aus Messing und Eisen, mit Zahnrädern in der Brust, leuchtenden
    Augen, Nieten-Bändern und einem Schraubenschlüssel in der Hand, auf einem Werkplatz."""
    from motive import figur
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    s = 0.55 * u + 0.25
    industrieboden(w, _r(12 * s + 5))
    S = Skulptur(w, s)
    metall = Mat(w, ["raw_gold_block", "gold_block", "waxed_copper_block", "raw_copper_block"] if k.messing else
                 ["iron_block", "polished_andesite", "gray_concrete", "polished_basalt"], kontrast=0.8)
    S.mat("k", sk(metall, 1, 1 + 26 * s))
    S.mat("a", bl(w, "waxed_copper_block"))
    S.mat("d", bl(w, "black_concrete"))
    S.mat("g", bl(w, "redstone_lamp" if False else "shroomlight" if k.messing else "sea_lantern"))
    figur(S, "golem", "schwert")
    S.rendern((-10, -1, -6), (10, 26, 8), versatz=(0.5, 1.01, 0.5))
    yb = round(1 + 13 * s)
    gross_zahnrad(w, 0, yb, round(3.2 * s) + 1, max(1.5, 1.5 * s), achse="z", mat="gold_block" if k.messing else
                  "iron_block", zaehne=8)
    hohl(w, 2)
    return w


def uhrmacher(seed, g=1):
    """Uhrmacherladen: schmales Giebelhaus mit großem Schaufenster voller Uhren (Zifferblätter), einer Standuhr vor
    der Tür, Zahnrad-Aushängeschild und Messingladen im Erdgeschoss."""
    w = _welt(seed)
    k = Werk(w, seed)
    u = U[g]
    a, b = _r(3 * u + 2, 3), _r(4 * u + 2, 3)
    industrieboden(w, a + 7)
    st = k.stil(fachwerk=True, wand="putz" if k.messing else "kalkstein", dach="mcw_schiefer")
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=3, eh=4, dach="sattel", first_x=False, tuer="east", kamine=1,
               steil=True)
    for x in range(-a + 1, a):
        for y in (2, 3):
            w.setze(x, y, b, k.glas())
    for i, x in enumerate(range(-a + 1, a, 2)):
        w.setze(x, 2, b - 1, cr(w, "cuckoo_clock", "spruce_trapdoor", {"facing": "south", "half": "bottom",
                                                                      "open": False, "powered": False,
                                                                      "waterlogged": False}, facing="south"))
    uhrblatt(w, 0, 9, b + 1, max(1.6, a * 0.6), "south")
    for y in range(1, 4):
        w.setze(a + 2, y, b + 2, w.b("dark_oak_planks") if y < 3 else w.b("white_concrete"))
    w.setze(a + 2, 4, b + 2, w.b("dark_oak_slab", type="bottom", waterlogged=False))
    w.setze(a + 1, 5, b + 1, MB.zahnrad(w, "x", gross=True))
    hohl(w, 2)
    return w


UHRWERK = {
    "uhrturm": ("Großer Uhrturm", uhrturm),
    "dampfmaschinenhalle": ("Dampfmaschinenhalle", dampfmaschinenhalle),
    "zahnradturm": ("Zahnradturm", zahnradturm),
    "windkraftwerk": ("Windkraftwerk", windkraftwerk),
    "wasserkraftwerk": ("Wasserkraftwerk", wasserkraftwerk),
    "fabrikhalle": ("Fabrikhalle", fabrikhalle),
    "bohrturm": ("Bohrturm", bohrturm),
    "bahnhof": ("Bahnhof", bahnhof),
    "dampflok": ("Dampflok", dampflok),
    "luftschiffwerft": ("Luftschiffwerft", luftschiffwerft),
    "tanklager": ("Tanklager", tanklager),
    "werkstatt": ("Tüftler-Werkstatt", werkstatt),
    "kuckucksuhrhaus": ("Kuckucksuhr-Haus", kuckucksuhrhaus),
    "kuehlturm": ("Kraftwerk mit Kühlturm", kuehlturm),
    "schwebebahn": ("Schwebebahn", schwebebahn),
    "aufzugsturm": ("Aufzugsturm", aufzugsturm),
    "erntemaschine": ("Automatische Farm", erntemaschine),
    "blitzturm": ("Blitzturm", blitzturm),
    "automaton": ("Automaton", automaton),
    "uhrmacher": ("Uhrmacherladen", uhrmacher),
}

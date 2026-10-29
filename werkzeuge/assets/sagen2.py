"""Sagenlande – Erweiterung auf 20: Seestadt auf Pfählen, Klammfeste, Elfenzuflucht, Adlerhorst, Halle auf dem
Hügel, Flussfurt mit Fährhaus, Hügelgräberfeld, Grenzbrücke, Sternturm am Meer, Königsgrab im Fels, Wegschrein,
Ruinenfeste, Wachfeuerkette."""

from __future__ import annotations

import math

import numpy as np

import modbloecke as MB
import pracht as P
from drachen import felsen
from haeuser import HAUSPOOL
from lib import Rauschen, einfuegen, laub
from motive import figur
from pracht import Mat, gelaende
from skulptur import Skulptur, dreh_y, ell, kap, kreisrand, scheibe
from weltwunder import bl, hohl, platz, sk
from wueste_eis import kuppel

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


def _st(w, pool, **kw):
    d = dict(HAUSPOOL[pool])
    d.update(kw)
    return P.Stil(w, **d)


def see(w, R, cx=0, cz=0, boden="mud"):
    for x, z in scheibe(R, cx, cz):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b(boden) if (x + z) % 4 else w.b("gravel"))


def seestadt(seed, g=2):
    """Seestadt auf Pfählen: Holzhäuser mit steilen Dächern stehen auf Pfahlrosten mitten im See, verbunden durch
    Stege und Brücken, ein Marktplatz-Floß, Boote und das Haus des Bürgermeisters."""
    w = _welt(seed)
    u = U[g]
    R = _r(18 * u + 8)
    see(w, R + 4)
    rng = w.rng
    st = _st(w, "holz_dunkel", dach="schindel_grau" if _stil(seed) else "mcw_holz")
    n = 5 + 3 * g
    pos = []
    for i in range(n):
        a = i * 2.39996
        d = R * 0.75 * math.sqrt((i + 0.5) / n)
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        for x in range(cx - 3, cx + 4):
            for z in range(cz - 3, cz + 4):
                w.setze(x, 1, z, w.b("spruce_planks"))
                if (x - cx) % 3 == 0 and (z - cz) % 3 == 0:
                    for y in (-1, 0):
                        w.setze(x, y, z, w.b("spruce_log", axis="y"))
        P.gebaeude(w, st, cx - 2, cz - 2, cx + 2, cz + 2, y0=2, etagen=1 + (i % 3 == 0), eh=4, dach="sattel",
                   steil=True, tuer="south", gauben=False, kamine=1, sockel_h=0)
        pos.append((cx, cz))
    for (ax, az), (bx, bz) in zip(pos, pos[1:]):
        n2 = max(abs(bx - ax), abs(bz - az))
        for k in range(n2 + 1):
            t = k / n2
            x, z = round(ax + (bx - ax) * t), round(az + (bz - az) * t)
            w.setze(x, 1, z, w.b("spruce_slab", type="top", waterlogged=False), ueberschreiben=False)
            if k % 4 == 0:
                w.setze(x, 0, z, w.b("spruce_log", axis="y"), ueberschreiben=False)
    gross = _st(w, "fachwerk_rot", dach="mcw_ziegel")
    P.gebaeude(w, gross, -4, -4, 4, 4, y0=2, etagen=2, eh=4, dach="walm", tuer="south", gauben=True, kamine=2,
               sockel_h=0)
    for k in range(3):
        bx, bz = round(math.cos(k * 2) * (R + 1)), round(math.sin(k * 2) * (R + 1))
        for dx in range(-2, 3):
            w.setze(bx + dx, 1, bz, w.b("oak_slab", type="bottom", waterlogged=False))
    hohl(w, 2)
    return w


def klammfeste(seed, g=2):
    """Klammfeste: eine gewaltige Talsperrmauer mit Wehrgang riegelt eine Felsenklamm ab, dahinter eine Burg am Fels,
    Wassertor im Mauerfuß und eine Rampe zum Torhaus."""
    w = _welt(seed)
    u = U[g]
    W, H = _r(24 * u + 10), _r(18 * u + 8)
    fm = Mat(w, ["stone", "andesite", "tuff", "cobblestone", "diorite"], kontrast=1.3)
    gelaende(w, _r(W * 1.3), art="wiese", dichte=0.3)
    for z in range(-W, W + 1):
        xm = round(math.sin(z * 0.15) * 1.5)
        for x in range(xm - 2, xm + 3):
            if z > 2 or z < -22:
                w.setze(x, 0, z, w.b("water", level=0))
    for sx in (-1, 1):
        felsen(w, 12 * u + 5, H + 10, cx=sx * W, cz=-4, mat=fm, spitz=1.4, rauh=0.35)
    M = Mat(w, ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "polished_andesite"])
    Hm = _r(H * 0.55)
    for x in range(-W + 4, W - 3):
        for z in range(-2, 3):
            for y in range(0, Hm):
                tor = abs(x) <= 2 and y < 6 and z > -3
                if not tor:
                    w.setze(x, y, z, M(x, y, z, y / Hm))
        if x % 2 == 0:
            w.setze(x, Hm, 2, M(x, Hm, 2, 0.9))
        w.setze(x, Hm, -2, M(x, Hm, -2, 0.9)) if x % 2 == 0 else None
    for y in range(1, 5):
        for x in range(-2, 3):
            w.setze(x, y, 3, w.b("iron_bars", east=True, west=True, north=False, south=False, waterlogged=False))
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="mcw_schiefer", holz="spruce")
    P.turm(w, st, 0, -10, 1, _r(H * 1.1), 4 * u + 2, dach="kegel", krone=True, fahne="green")
    P.gebaeude(w, st, -10, -20, 10, -12, y0=1, etagen=2, eh=5, dach="walm", tuer="south", gauben=True, kamine=2)
    for k in range(Hm):
        for x in (W - 8, W - 7, W - 6):
            w.setze(x, k, 3 + Hm - k, M(x, k, 0, 0.3))
    hohl(w, 3)
    return w


def elfenzuflucht(seed, g=2):
    """Elfenzuflucht: in einem waldigen Tal zwischen Wasserfällen liegen terrassierte Hallen aus weißem Stein mit
    grünen Kuppeln, Galerien und Brücken über den Bach."""
    import wald2
    w = _welt(seed)
    u = U[g]
    R = _r(22 * u + 8)
    gelaende(w, R, art="wald", dichte=0.3)
    fm = Mat(w, ["stone", "andesite", "mossy_cobblestone", "diorite", "calcite"], kontrast=1.2)
    for sx in (-1, 1):
        felsen(w, 10 * u + 4, 14 * u + 6, cx=sx * round(R * 0.65), cz=-round(R * 0.4), mat=fm, spitz=0.7)
    for y in range(1, _r(12 * u + 5)):
        for sx in (-1, 1):
            w.setze(sx * round(R * 0.5), y, -round(R * 0.25), w.b("water", level=0 if y == _r(12 * u + 5) - 1 else 8))
    for z in range(-round(R * 0.25), R):
        x = round(math.sin(z * 0.2) * 2)
        for dx in (-1, 0, 1):
            w.setze(x + dx, 0, z, w.b("water", level=0))
    st = P.Stil(w, wand="marmor", sockel="kalkstein", gesims="quartz", dach="mcw_gruen", holz="birch",
                fensterart="bogen", laeden=False, blumen=0.5)
    for i, (cx, cz, a, b, e) in enumerate(((-8, 2, 5, 4, 2), (9, -2, 5, 4, 2), (0, -12, 7, 4, 3))):
        P.gebaeude(w, st, cx - a, cz - b, cx + a, cz + b, y0=1 + (i == 2) * 2, etagen=e, eh=5, dach="walm",
                   tuer="south", gauben=False, kamine=0)
        top = 1 + (i == 2) * 2 + 1 + e * 5
        kuppel(w, w.b("waxed_oxidized_copper"), cx, cz, top + 2, min(a, b) - 0.5, form="zwiebel", spitze=None)
    for z in (4, 10):
        for x in range(-4, 5):
            w.setze(x, 1, z, w.b("smooth_quartz_slab", type="top", waterlogged=False))
    for i in range(5 + g):
        a = w.rng.random() * 2 * math.pi
        d = R * (0.5 + 0.4 * w.rng.random())
        einfuegen(w, wald2.birke(int(w.rng.integers(1, 10 ** 6))), round(math.cos(a) * d), 0, round(math.sin(a) * d))
    hohl(w, 3)
    return w


def adlerhorst(seed, g=2):
    """Adlerhorst: auf einer einsamen Felsnadel ein riesiges Nest aus Stämmen, darin ein Riesenadler mit gefalteten
    Schwingen; Federn und Knochen auf den Felsvorsprüngen."""
    w = _welt(seed)
    u = U[g]
    H = _r(26 * u + 10)
    gelaende(w, _r(12 * u + 6), art="wiese", dichte=0.2)
    hoehe = felsen(w, 9 * u + 4, H, spitz=0.35, rauh=0.25)
    top = max(hoehe.values())
    rng = w.rng
    R = 5 * u + 3
    for i in range(int(40 * u) + 20):
        a = rng.random() * 2 * math.pi
        r = R * (0.7 + 0.35 * rng.random())
        y = top + 1 + int(rng.random() * 2 * u)
        for t in range(3 + int(rng.random() * 3)):
            aa = a + t * 0.3
            w.setze(round(math.cos(aa) * r), y, round(math.sin(aa) * r),
                    w.b(["spruce_log", "dark_oak_log", "oak_log"][i % 3], axis="x" if abs(math.sin(aa)) > 0.7 else "z"))
    s = 0.7 * u + 0.3
    S = Skulptur(w, s)
    S.mat("f", lambda x, y, z, *_: w.b("brown_terracotta") if (x + y) % 3 else w.b("brown_concrete"))
    S.mat("w", bl(w, "white_concrete"))
    S.mat("g", bl(w, "yellow_concrete"))
    S.plus(ell(0, 4, 0, 3.0, 3.6, 2.6), "f")
    S.plus(ell(0, 8.2, 1.0, 1.6, 1.6, 1.6), "w")
    S.plus(kap((0, 8.2, 2.4), (0, 7.4, 3.8), 0.6, 0.2), "g")
    for sx in (-1, 1):
        S.plus(lambda X, Y, Z, sx=sx: (((X - sx * 2.6) / 1.2) ** 2 + ((Y - 4.5) / 3.8) ** 2 + ((Z + 0.5) / 3.2) ** 2
                                       < 1), "f")
    S.plus(kap((0, 2, -2.5), (0, 0.8, -6), 1.2, 0.5), "f")
    S.rendern((-5, -1, -7), (5, 11, 5), versatz=(0.5, top + 2.01, 0.5))
    hohl(w, 3)
    return w


def huegelhalle(seed, g=2):
    """Halle auf dem Hügel: eine goldgedeckte Königshalle mit geschnitzten Giebelbalken thront auf einem grünen
    Hügel, eine Treppe mit Wasserrinne führt hinauf, Holzhäuser und Palisade am Hang."""
    w = _welt(seed)
    u = U[g]
    R = _r(20 * u + 8)
    gelaende(w, R + 4, art="wiese", dichte=0.4)
    r_n = Rauschen(w, 5)
    Hh = 8 * u + 4
    for x, z in scheibe(R):
        d = math.hypot(x, z) / R
        hh = int(Hh * max(0, 1 - d ** 1.6) * (0.9 + 0.2 * r_n(x, 0, z)))
        for y in range(1, hh + 1):
            w.setze(x, y, z, w.b("grass_block", snowy=False) if y == hh else w.b("dirt"))
    top = int(Hh) + 1
    a, b = _r(7 * u + 3), _r(3 * u + 2)
    st = P.Stil(w, wand=Mat(w, ["dark_oak_planks", "stripped_dark_oak_log", "spruce_planks"]), sockel="graustein",
                gesims="stone_brick", dach=["mcw:yellow_terracotta", "mcw:orange_terracotta", "mcw:yellow_terracotta"]
                if False else "mcw_gelb", holz="dark_oak", laeden=False, blumen=0)
    P.gebaeude(w, st, -b, -a, b, a, y0=top, etagen=1, eh=6, dach="sattel", first_x=False, tuer="south",
               gauben=False, kamine=0, steil=True)
    for k in range(int(Hh)):
        for x in (-1, 0, 1):
            w.setze(x, k + 1, a + 2 + int(Hh) - k, w.b("stone_brick_stairs", facing="north", half="bottom",
                                                       shape="straight", waterlogged=False))
        w.setze(2, k + 1, a + 2 + int(Hh) - k, w.b("water", level=0))
    stb = P.Stil(w, wand="holz_dunkel", sockel="graustein", gesims="stone_brick", dach="mcw_stroh", holz="spruce")
    for i in range(3 + g):
        ang = i / (3 + g) * 2 * math.pi + 0.7
        cx, cz = round(math.cos(ang) * R * 0.7), round(math.sin(ang) * R * 0.7)
        yy = max([y for (x, y, z) in w.bloecke if x == cx and z == cz] + [0])
        P.gebaeude(w, stb, cx - 2, cz - 2, cx + 2, cz + 2, y0=yy + 1, etagen=1, eh=3, dach="sattel", tuer="south",
                   gauben=False, kamine=1)
    hohl(w, 3)
    return w


def flussfurt(seed, g=1):
    """Flussfurt mit Fährhaus: ein breiter Fluss mit Trittsteinen und einer Fähre an einem Seil, am Ufer das Fährhaus
    mit Stall und Laterne, Weiden und Schilf."""
    import wald2
    w = _welt(seed)
    u = U[g]
    L = _r(14 * u + 6)
    gelaende(w, L + 4, art="wiese", dichte=0.4)
    B = _r(4 * u + 3)
    for x in range(-L - 4, L + 5):
        for z in range(-B, B + 1):
            if math.hypot(x, z) > L + 3.5:
                continue
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("gravel") if (x + z) % 3 else w.b("sand"))
    for z in range(-B, B + 1, 2):
        w.setze(-3, 0, z, w.b("mossy_cobblestone"))
    for x in range(0, 4):
        for z in (-1, 0, 1):
            w.setze(x + 3, 1, z, w.b("spruce_planks"))
    for z in range(-B - 2, B + 3):
        w.setze(4, 3, z, MB.seil(w, "z"))
    for sz in (-B - 2, B + 2):
        for y in range(1, 4):
            w.setze(4, y, sz, w.b("spruce_log", axis="y"))
    st = _st(w, "fachwerk_ocker")
    P.gebaeude(w, st, -4, B + 4, 4, B + 10, y0=1, etagen=2, eh=4, dach="sattel", tuer="north", gauben=False,
               kamine=1)
    for i in range(2):
        einfuegen(w, wald2.weide(int(w.rng.integers(1, 10 ** 6))), -L + 3 + i * 2 * L // 3, 0, -B - 5)
    hohl(w, 2)
    return w


def huegelgraeber(seed, g=2):
    """Hügelgräberfeld: mehrere runde Grabhügel mit Steinkränzen und Eingängen, Menhire, Nebel aus Spinnweben und
    ein alter Grabwächterstein."""
    from spuk import spukboden
    w = _welt(seed)
    u = U[g]
    R = _r(18 * u + 8)
    spukboden(w, R, dichte=0.6)
    fm = Mat(w, ["stone", "andesite", "mossy_cobblestone", "tuff"], kontrast=1.2)
    n = 3 + g
    for i in range(n):
        a = i / n * 2 * math.pi
        cx, cz = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        r = (3 + 2 * u) * (0.8 + 0.4 * w.rng.random())
        for x, z in scheibe(r, cx, cz):
            hh = int((1 - (math.hypot(x - cx, z - cz) / r) ** 2) * (2 + 1.5 * u)) + 1
            for y in range(1, hh + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == hh else w.b("dirt"))
        for x, z in kreisrand(r + 1, cx, cz):
            if (x + z) % 2 == 0:
                w.setze(x, 1, z, fm(x, 1, z, 0.3))
        dx, dz = -math.cos(a), -math.sin(a)
        ex, ez = round(cx + dx * r), round(cz + dz * r)
        for y in (1, 2):
            w.bloecke.pop((ex, y, ez), None)
        w.setze(ex, 3, ez, fm(ex, 3, ez, 0.8))
    for i in range(6):
        a = w.rng.random() * 2 * math.pi
        d = w.rng.random() * R * 0.3
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        for y in range(1, 3 + int(w.rng.integers(0, 3))):
            w.setze(x, y, z, fm(x, y, z, 0.5))
    return w


def grenzbruecke(seed, g=2):
    """Grenzbrücke: eine steinerne Bogenbrücke über einen Fluss mit einem Torhaus in der Mitte, Zollschranke,
    Wachstuben und Fahnen beider Reiche."""
    w = _welt(seed)
    u = U[g]
    L = _r(16 * u + 6)
    gelaende(w, L + 4, art="wiese", dichte=0.3)
    for x in range(-L, L + 1):
        for z in range(-L, L + 1):
            if abs(x) < L * 0.45 + math.sin(z * 0.2) * 1.5 and math.hypot(x, z) < L + 3.5:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel"))
    M = Mat(w, ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "andesite"])
    for x in range(-L, L + 1):
        for z in range(-2, 3):
            bog = abs(x % 8 - 4) < 3 and abs(x) < L * 0.45 + 1
            hh = 4 if not bog else 2 + int(abs(x % 8 - 4) * 0.6)
            for y in range(4 - (0 if not bog else (4 - hh)), 5):
                w.setze(x, y, z, M(x, y, z, 0.5))
            if not bog:
                for y in range(0, 5):
                    w.setze(x, y, z, M(x, y, z, y / 5))
        for z in (-3, 3):
            w.setze(x, 5, z, w.b("stone_brick_wall", up=x % 3 == 0, north="none", south="none", east="low",
                                 west="low", waterlogged=False))
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="mcw_schiefer", holz="spruce")
    P.gebaeude(w, st, -3, -4, 3, 4, y0=5, etagen=2, eh=4, dach="walm", tuer="east", gauben=False, kamine=1)
    for x in range(-2, 3):
        for y in range(5, 8):
            w.bloecke.pop((x, y, 0), None) if abs(x) < 2 and False else None
    for sx in (-1, 1):
        for y in range(5, 12):
            w.setze(sx * 5, y, 3, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                      waterlogged=False))
        farbe = ["red_wool", "blue_wool"][sx > 0]
        for k in range(3):
            w.setze(sx * 5 + sx, 11 - k, 3, w.b(farbe))
    hohl(w, 2)
    return w


def sternturm(seed, g=2):
    """Sternturm am Meer: ein schlanker weißer Turm auf einer Klippe über der Brandung, mit Sternwartenkuppel und
    leuchtendem Kristall, eine lange Treppe vom Strand hinauf."""
    w = _welt(seed)
    u = U[g]
    R = _r(18 * u + 8)
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("sand"))
    fm = Mat(w, ["stone", "andesite", "diorite", "calcite"], kontrast=1.2)
    hoehe = felsen(w, R * 0.55, 10 * u + 4, mat=fm, spitz=1.5, rauh=0.2)
    top = int(10 * u + 4) + 1
    H = _r(30 * u + 10)
    for y in range(top, top + H):
        r = 2.6 * u + 1.5 - (y - top) / H * 1.0
        for x, z in kreisrand(r):
            w.setze(x, y, z, w.b("smooth_quartz") if (y // 6) % 2 else w.b("calcite") if (x + z) % 3 else
                    w.b("light_blue_stained_glass"))
    yt = top + H
    kuppel(w, w.b("light_blue_concrete"), 0, 0, yt, 2.6 * u + 1.2, spitze="sea_lantern")
    w.setze(0, yt - 1, 0, w.b("amethyst_block"))
    for i in range(int(R * 3)):
        a = i * 0.25
        rr = R * 0.55 - i * 0.05
        if rr < 3:
            break
        x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
        y = hoehe.get((x, z), 0) + 1
        w.setze(x, y, z, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    hohl(w, 3)
    return w


def felsengrab(seed, g=2):
    """Königsgrab im Fels: eine in die Felswand gehauene Tempelfassade mit Säulen, Giebel und Statuen der Könige,
    Stufen und Feuerschalen davor."""
    from zwerge import Zwerg, bergwand
    w = _welt(seed)
    u = U[g]
    Z = Zwerg(w, seed)
    W, H = 18 * u + 8, 20 * u + 8
    bergwand(w, 0, W, H, Z, D=10)
    gelaende(w, _r(W), art="wiese", dichte=0.2)
    M = Mat(w, ["smooth_sandstone", "cut_sandstone", "sandstone", "chiseled_sandstone"] if _stil(seed) == 0 else
            ["polished_andesite", "stone_bricks", "smooth_stone", "chiseled_stone_bricks"])
    B = _r(8 * u + 4)
    Hf = _r(14 * u + 6)
    for x in range(-B, B + 1):
        for y in range(0, Hf):
            for z in range(-2, 1):
                w.setze(x, y, z, M(x, y, z, y / Hf))
        if x % 3 == 0:
            for y in range(1, Hf - 3):
                w.setze(x, y, 1, M(x, y, 1, 0.5))
    for k in range(B + 1):
        for x in range(-B + k, B - k + 1):
            w.setze(x, Hf + k // 2, 1, M(x, 0, 1, 0.9))
    for y in range(1, 5):
        for x in (-1, 0, 1):
            w.setze(x, y, 0, w.b("black_concrete"))
    for sx in (-1, 1):
        S = Skulptur(w, 0.3 * u + 0.12)
        S.mat("k", sk(M, 0, 30))
        S.mat("a", bl(w, "gold_block"))
        S.mat("d", bl(w, "gold_block"))
        S.mat("g", bl(w, "shroomlight"))
        figur(S, "ritter", "schwert")
        S.rendern((-7, -1, -5), (7, 26, 7), versatz=(sx * (B // 2) + 0.5, 1.01, 2.5))
    for k in range(3):
        for x in range(-B, B + 1):
            w.setze(x, k, 3 + 3 - k, M(x, k, 0, 0.3))
    hohl(w, 3)
    return w


def wegschrein(seed, g=0):
    """Wegschrein: ein kleiner überdachter Schrein an einer Wegkreuzung mit Kerzen, einer Heiligenfigur, Bank und
    Wegweiser, umgeben von Blumen."""
    from haeuser import bank
    w = _welt(seed)
    u = U[g]
    gelaende(w, _r(5 * u + 5), art="wiese", dichte=0.6)
    for k in range(-6, 7):
        for d in (-1, 0, 1):
            w.setze(k, 0, d, w.b("dirt_path") if (k + d) % 3 else w.b("gravel"))
            w.setze(d, 0, k, w.b("dirt_path") if (k + d) % 3 else w.b("gravel"))
    x0, z0 = 3, -4
    for y in range(1, 4):
        w.setze(x0, y, z0, w.b("stone_bricks") if y < 3 else w.b("chiseled_stone_bricks"))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(x0 + dx, 4, z0 + dz, w.b("spruce_slab", type="bottom", waterlogged=False))
    w.setze(x0, 4, z0, w.b("spruce_planks"))
    w.setze(x0, 5, z0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    w.setze(x0, 3, z0 + 1, w.b("candle", candles=3, lit=True, waterlogged=False))
    bank(w, -4, -3, "south")
    for y in range(1, 4):
        w.setze(-2, y, 2, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    for f, d in (("east", (1, 0)), ("south", (0, 1))):
        w.setze(-2 + d[0], 3, 2 + d[1], w.b("spruce_trapdoor", facing=f, half="top", open=True, powered=False,
                                            waterlogged=False))
    return w


def ruinenfeste(seed, g=2):
    """Ruinenfeste auf dem Hügel: ein ringförmiger, halb eingestürzter Mauerkranz auf einer Hügelkuppe, Turmstümpfe,
    eingesunkene Treppen, Gras und Efeu."""
    from veredeln import bewuchs
    w = _welt(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R + 8, art="wiese", dichte=0.4)
    hoehe = felsen(w, R + 6, 6 * u + 3, spitz=1.6, rauh=0.15,
                   mat=Mat(w, ["dirt", "stone", "andesite", "coarse_dirt"], kontrast=1.0))
    top = int(6 * u + 3) + 1
    for (x, z), y in hoehe.items():
        w.setze(x, y, z, w.b("grass_block", snowy=False))
    M = Mat(w, ["mossy_stone_bricks", "cracked_stone_bricks", "stone_bricks", "mossy_cobblestone", "andesite"])
    r_n = Rauschen(w, 3)
    for x, z in kreisrand(R):
        hh = int((4 + 6 * u) * r_n(x, 0, z))
        for y in range(top, top + hh):
            w.setze(x, y, z, M(x, y, z, 0.5))
            w.setze(round(x * 0.92), y, round(z * 0.92), M(x, y, z, 0.5))
    for i in range(4):
        a = i / 4 * 2 * math.pi + 0.4
        cx, cz = round(math.cos(a) * R), round(math.sin(a) * R)
        hh = int((6 + 10 * u) * (0.4 + 0.6 * r_n(cx, 9, cz)))
        for y in range(top, top + hh):
            for x, z in kreisrand(2.5, cx, cz):
                if r_n(x, y, z) > 0.25 or y < top + 3:
                    w.setze(x, y, z, M(x, y, z, 0.5))
    bewuchs(w, moos=0.06, ranken=0.05)
    hohl(w, 3)
    return w


def wachfeuerkette(seed, g=2):
    """Wachfeuerkette: drei Signalfeuer auf Felsgipfeln hintereinander, jedes mit gemauerter Feuerschale,
    Holzvorrat und kleiner Wachhütte – lodern sie, steht das Reich in Gefahr."""
    w = _welt(seed)
    u = U[g]
    L = _r(20 * u + 8)
    gelaende(w, L + 6, art="wiese", dichte=0.2)
    fm = Mat(w, ["stone", "andesite", "tuff", "diorite", "cobblestone"], kontrast=1.3)
    st = P.Stil(w, wand="holz_dunkel", sockel="graustein", gesims="stone_brick", dach="mcw_holz", holz="spruce")
    for i in range(3):
        cx = -L + i * L
        cz = round(math.sin(i * 2) * L * 0.3)
        H = 8 * u + 4 + i * 3 * u
        hoehe = felsen(w, 6 * u + 3, H, cx=cx, cz=cz, mat=fm, spitz=0.6, rauh=0.2)
        top = max(v for (x, z), v in hoehe.items() if abs(x - cx) < 2 and abs(z - cz) < 2)
        for x, z in scheibe(2.2, cx, cz):
            w.setze(x, top + 1, z, w.b("stone_bricks"))
            w.setze(x, top + 2, z, w.b("stone_bricks") if math.hypot(x - cx, z - cz) > 1.3 else
                    w.b("spruce_log", axis="y"))
        w.setze(cx, top + 3, cz, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
        hx = cx + 4
        hy = max([v for (x, z), v in hoehe.items() if abs(x - hx) < 2 and abs(z - cz) < 2] + [0])
        P.gebaeude(w, st, hx - 1, cz - 1, hx + 2, cz + 2, y0=hy + 1, etagen=1, eh=3, dach="sattel", tuer="west",
                   gauben=False, kamine=0, sockel_h=0)
    hohl(w, 3)
    return w


NEU = {
    "seestadt": ("Seestadt auf Pfählen", seestadt),
    "klammfeste": ("Klammfeste", klammfeste),
    "elfenzuflucht": ("Elfenzuflucht", elfenzuflucht),
    "adlerhorst": ("Adlerhorst", adlerhorst),
    "huegelhalle": ("Halle auf dem Hügel", huegelhalle),
    "flussfurt": ("Flussfurt mit Fährhaus", flussfurt),
    "huegelgraeber": ("Hügelgräberfeld", huegelgraeber),
    "grenzbruecke": ("Grenzbrücke", grenzbruecke),
    "sternturm": ("Sternturm am Meer", sternturm),
    "felsengrab": ("Königsgrab im Fels", felsengrab),
    "wegschrein": ("Wegschrein", wegschrein),
    "ruinenfeste": ("Ruinenfeste", ruinenfeste),
    "wachfeuerkette": ("Wachfeuerkette", wachfeuerkette),
}

"""Felsen & Berge II – zwanzig weitere Landschaftsformen: erloschener Vulkan mit Kratersee, Fjord, Canyon,
Karsttürme, Sandsteinwelle, Gletscherzunge, Sinterterrassen, offene Tropfsteinhöhle, rote Felskuppel, Hängetal,
Bergsee im Kar, Cenote, Geysirfeld, erkaltetes Lavafeld, Steilküste, Felsenburg, Schären, Moränenfeld,
Terrakotta-Mesa und Eisberg. Boden y = 0."""

from __future__ import annotations

import math

import numpy as np

import wald2
from berge import GRANIT, KALK, SANDST, bepflanzt, gestein, vol
from flora import _neu, _r, _stil
from gewaesser import Land, gischt
from lib import Rauschen, einfuegen

U = [0.6, 1.0, 1.7, 2.8]
BASALT = ["basalt", "smooth_basalt", "blackstone", "deepslate", "tuff"]
TERRA = ["red_terracotta", "orange_terracotta", "terracotta", "yellow_terracotta", "white_terracotta",
         "brown_terracotta", "light_gray_terracotta"]


def erloschener_vulkan(seed, g=3):
    """Erloschener Vulkan: ein grasbewachsener Kegel mit Basaltrippen und einem tiefen, kreisrunden Kratersee,
    an den Flanken Lavazungen aus erkaltetem Gestein und ein paar Kiefern."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    L = Land(w, R)
    H = 14 * u + 6
    rk = R * 0.28

    def h(x, z, _):
        d = math.hypot(x, z)
        if d < rk:
            return round(H - 4 - (1 - d / rk) * 3)
        return round(H * max(0.0, 1 - (d - rk) / (R - rk)) ** 1.3 + L.rn(x, 0, z) * 1.5)
    L.heben(h)
    L.see(0, 0, rk * 0.92, round(H - 3), tiefe=2)
    L.bauen(fels=BASALT, unten=-2)
    rn = Rauschen(w, 3)
    for (x, z), hh in L.h.items():
        a = math.atan2(z, x)
        if hh > 2 and math.cos(a * 5) > 0.85 and (x, z) not in L.wasser:
            w.setze(x, hh, z, w.b("basalt", axis="y") if rn(x, 0, z) < 0.6 else w.b("smooth_basalt"))
    bepflanzt(w, L, int(4 * u), ("kiefer", "busch"))
    return w


def fjord(seed, g=3):
    """Fjord: ein langer, schmaler Meeresarm zwischen fast senkrechten Felswänden, oben Nadelwald, an der Seite
    stürzt ein schmaler Wasserfall ins dunkle Wasser."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    L = Land(w, R)
    H = round(14 * u + 6)
    B = 4 * u + 3
    L.heben(lambda x, z, h: min(H, max(-4, round((abs(z + math.sin(x * 0.12) * 3 * u) - B) * 2.5))) +
            round(L.rn(x, 0, z) * 2) if abs(z + math.sin(x * 0.12) * 3 * u) > B else -4)
    for (x, z), hh in L.h.items():
        if hh < 0:
            L.wasser[(x, z)] = 0
    L.bauen(fels=["stone", "andesite", "deepslate", "tuff", "cobblestone"], unten=-5)
    bepflanzt(w, L, int(8 * u), ("fichte", "fichte", "kiefer"))
    fx = round(R * 0.2)
    fz = round(B + 2 - math.sin(fx * 0.12) * 3 * u)
    for y in range(0, H + 1):
        w.setze(fx, y, fz, w.b("water", level=0 if y == H else 8))
    gischt(w, fx, 1, fz - 1, 2.0)
    return w


def canyon(seed, g=3):
    """Canyon: eine gewundene Schlucht durch rot-orange gebänderte Felsschichten, unten ein schmaler grüner Fluss,
    Felsterrassen und Wacholder auf den Kanten."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    L = Land(w, R)
    H = round(16 * u + 6)

    def h(x, z, _):
        m = math.sin(x * 0.08) * R * 0.25
        d = abs(z - m)
        stufe = min(H, max(0, int((d - 2 * u) / (2.5 * u + 1)) * 3 + int(L.rn(x, 0, z) * 2)))
        return stufe
    L.heben(h)
    L.fluss([(x, math.sin(x * 0.08) * R * 0.25) for x in range(-R - 2, R + 3, 4)], 1.5 * u + 1, 0, tiefe=1)
    L.bauen(fels=TERRA, unten=-2)
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if "terracotta" in n and y > 0:
            w.bloecke[(x, y, z)] = w.b(TERRA[(y // 2 + (1 if L.rn(x, y, z) > 0.7 else 0)) % len(TERRA)])
    bepflanzt(w, L, int(5 * u), ("busch",), dichte=0.15)
    return w


def karsttuerme(seed, g=3):
    """Karsttürme: eine Gruppe steiler, oben abgerundeter Kalksteintürme, von dichtem Grün bewachsen, die aus
    einem ruhigen Fluss mit Reisfeldern aufragen."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    L = Land(w, R)
    L.fluss([(-R - 2, -R * 0.3), (0, R * 0.1), (R + 2, -R * 0.1)], 2 * u + 1.5, 0, tiefe=2)
    L.bauen(unten=-3)
    L.bepflanzen(0.35)
    rn = Rauschen(w, 2)
    rng = w.rng
    for i in range(4 + g):
        a = i * 2.39996
        d = R * 0.7 * math.sqrt((i + 0.5) / (4 + g))
        cx, cz = math.cos(a) * d, math.sin(a) * d
        if abs(cz - (cx * 0.1)) < 3 * u:
            cz += 6 * u
        H = (10 + rng.random() * 12) * u + 6
        r0 = (2.5 + rng.random() * 1.5) * u + 1.5
        vol(w, (int(cx - r0) - 3, 1, int(cz - r0) - 3), (int(cx + r0) + 3, int(H) + 3, int(cz + r0) + 3),
            lambda X, Y, Z, cx=cx, cz=cz, H=H, r0=r0: np.hypot(X - cx, Z - cz) <
            r0 * (1 - (np.clip(Y / H, 0, 1)) ** 4) * (0.85 + 0.25 * np.sin(Y * 0.5 + X)),
            gestein(KALK, rn))
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 1 and w.frei(x, y + 1, z) and w.P.name(b) in ("minecraft:calcite", "minecraft:diorite",
                                                             "minecraft:stone", "minecraft:andesite",
                                                             "minecraft:smooth_stone", "minecraft:tuff"):
            if rng.random() < 0.45:
                w.bloecke[(x, y, z)] = w.b("moss_block")
                if rng.random() < 0.08:
                    w.setze(x, y + 1, z, w.b("jungle_leaves", persistent=True, distance=1, waterlogged=False))
    return w


def sandsteinwelle(seed, g=2):
    """Sandsteinwelle: glatt geschliffene, wellenförmig geschwungene Sandsteinrücken mit feinen Farbbändern in
    Rot, Orange und Creme – wie eine erstarrte Brandung."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    bander = ["smooth_red_sandstone", "orange_terracotta", "smooth_sandstone", "red_sandstone", "white_terracotta",
              "cut_red_sandstone", "yellow_terracotta"]
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z) / R
            if d > 1:
                continue
            h = int((3 + 4 * math.sin(x * 0.18 + math.sin(z * 0.11) * 2) ** 2) * u * (1 - d ** 3))
            for y in range(-1, h + 1):
                welle = (y + math.sin(x * 0.3 + z * 0.15) * 2.0 + z * 0.08)
                w.setze(x, y, z, w.b(bander[int(welle) % len(bander)]))
    return w


def gletscherzunge(seed, g=3):
    """Gletscherzunge: ein Eisstrom aus Packeis und Blaueis zwischen dunklen Felsflanken, durchzogen von
    Gletscherspalten, vorne ein milchiger Gletschersee mit treibenden Eisbrocken."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    L = Land(w, R)
    H = 16 * u + 6
    L.heben(lambda x, z, h: round(max(0, (x + R) / (2 * R)) * H * 0.9 + abs(z) / R * H * 0.6))
    L.see(round(R * 0.65), 0, R * 0.3, 0, tiefe=2)
    L.bauen(gras="snow_block", fels=["stone", "deepslate", "andesite", "gravel"], unten=-2, schnee_ab=round(H * 0.5))
    rn = Rauschen(w, 3)
    for (x, z), hh in L.h.items():
        bz = (R * 0.25) * (1 - (x + R) / (3 * R))
        if abs(z) < bz and (x, z) not in L.wasser:
            top = hh + round(3 * u * (1 - abs(z) / bz))
            for y in range(hh, top + 1):
                spalte = (x + round(rn(x, 0, z) * 4)) % 7 == 0 and y > hh + 1 and abs(z) < bz * 0.8
                if spalte:
                    continue
                w.setze(x, y, z, w.b("blue_ice" if rn(x, y, z) < 0.3 else "packed_ice"))
            w.setze(x, top + 1, z, w.b("snow", layers=2), False) if rn(x, 5, z) < 0.3 else None
    for (x, z) in list(L.wasser)[::23]:
        w.setze(x, 1, z, w.b("packed_ice"))
    return w


def sinterterrassen(seed, g=2):
    """Sinterterrassen: schneeweiße Kalksinterstufen an einem Hang, in jeder Stufe ein türkisblaues Becken, über
    die Kanten rinnt Wasser, Kalzit-Zapfen hängen an den Rändern."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    stufen = _r(5 * u + 3)
    rn = Rauschen(w, 3)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) > R:
                continue
            t = (z + R) / (2 * R)
            f = t * stufen + 0.35 * math.sin(x * 0.22) + 0.15 * rn(x, 0, z)
            k = int(f)
            h = (stufen - k) * 2
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("calcite" if y > h - 2 else "diorite"))
            rand = f - k > 0.8
            if not rand and k < stufen:
                w.setze(x, h, z, w.b("water", level=0))
                w.setze(x, h - 1, z, w.b("light_blue_terracotta" if (x + z) % 3 else "calcite"))
            elif rand:
                w.setze(x, h + 1, z, w.b("calcite"))
                if w.rng.random() < 0.2:
                    w.setze(x, h - 1, z + 1, w.b("pointed_dripstone", vertical_direction="down", thickness="tip",
                                                 waterlogged=False), False)
    return w


def offene_tropfsteinhoehle(seed, g=2):
    """Offene Tropfsteinhöhle: ein Berg, an einer Seite aufgeschnitten, zeigt eine große Höhle mit Tropfsteinen,
    Säulen, einem unterirdischen See, Leuchtflechten und Moos."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    if True:
        rn = Rauschen(w, 4)
        H = 12 * u + 6
        vol(w, (-R, 0, -R), (R, int(H) + 2, R),
            lambda X, Y, Z: ((X / R) ** 2 + (Y / H) ** 2 + (Z / R) ** 2 < 1) &
            ~(((X / (R * 0.75)) ** 2 + ((Y - 1) / (H * 0.7)) ** 2 + (Z / (R * 0.75)) ** 2 < 1)) & ~(Z > R * 0.35),
            gestein(["stone", "dripstone_block", "andesite", "tuff", "calcite"], rn))
        for x in range(-int(R * 0.7), int(R * 0.7)):
            for z in range(-int(R * 0.7), int(R * 0.35)):
                if math.hypot(x, z) < R * 0.7:
                    w.setze(x, 0, z, w.b("dripstone_block" if (x + z) % 4 else "moss_block"))
        rng = w.rng
        for k in range(int(30 * u)):
            x, z = int(rng.integers(-R * 0.6, R * 0.6)), int(rng.integers(-R * 0.6, R * 0.3))
            ytop = None
            for y in range(int(H), 0, -1):
                if (x, y, z) in w.bloecke and not (x, y - 1, z) in w.bloecke:
                    ytop = y
                    break
            if ytop is None:
                continue
            L = int(1 + rng.random() * 4 * u)
            for k2 in range(1, L + 1):
                w.setze(x, ytop - k2, z, w.b("pointed_dripstone", vertical_direction="down",
                                             thickness="tip" if k2 == L else "middle", waterlogged=False), False)
            if rng.random() < 0.3:
                for y in range(1, 3):
                    w.setze(x, y, z, w.b("pointed_dripstone", vertical_direction="up",
                                         thickness="tip" if y == 2 else "base", waterlogged=False), False)
        for x in range(-3, 4):
            for z in range(-3, 1):
                if x * x + z * z < 9:
                    w.setze(x, 0, z - 2, w.b("water", level=0))
    return w


def rote_felskuppel(seed, g=3):
    """Rote Felskuppel: ein einzelner, gewaltiger, abgerundeter Inselberg aus rotem Sandstein mit senkrechten
    Furchen, Höhlennischen am Fuß und ein paar Wasserlöchern in der Steppe."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    L = Land(w, R)
    L.bauen(gras="red_sand", unten=-1)
    rn = Rauschen(w, 3)
    a, b, H = R * 0.6, R * 0.35, 10 * u + 5
    vol(w, (-int(a) - 2, 1, -int(b) - 2), (int(a) + 2, int(H) + 2, int(b) + 2),
        lambda X, Y, Z: ((X / a) ** 2 + (Z / b) ** 2) ** 2 + (Y / H) ** 6 * 0.9 < 1 - 0.08 * np.sin(X * 1.3) ** 2,
        lambda x, y, z: ["red_terracotta", "terracotta", "orange_terracotta", "red_sandstone"][
            int(y / 3 + rn(x, y, z) * 1.5) % 4])
    for k in range(6):
        x = int(-a * 0.8 + k * a * 0.3)
        for y in range(1, 4):
            for z in (int(b) + 1, int(b), int(b) - 1):
                w.bloecke.pop((x, y, z), None)
    for (x, z) in [(round(R * 0.7), round(R * 0.5)), (-round(R * 0.6), -round(R * 0.6))]:
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if dx * dx + dz * dz < 5:
                    w.setze(x + dx, 0, z + dz, w.b("water", level=0))
    bepflanzt(w, L, int(3 * u), ("busch",), dichte=0.1)
    return w


def haengetal(seed, g=3):
    """Hängetal: ein grünes Hochtal endet abrupt an einer Felskante, von der ein Wasserfall in ein tieferes Tal
    stürzt, unten ein Becken, Nebelgischt und Blumenwiesen."""
    w = _neu(seed)
    u = U[g]
    R = _r(20 * u + 8)
    L = Land(w, R)
    H = round(12 * u + 5)
    L.heben(lambda x, z, h: H if x < 0 else (round(H * max(0, 1 - x / 2.5)) if x < 3 else 0) +
            round(L.rn(x, 0, z) * 1.5))
    L.fluss([(-R - 2, 0), (-1, 0)], 1.5 * u + 1, H, tiefe=1)
    L.see(round(R * 0.25), 0, 4 * u + 3, 0, tiefe=2)
    L.bauen(unten=-2)
    L.bepflanzen(0.5, baeume=int(5 * u), arten=("fichte", "birke", "oak"))
    for z in range(-int(1.5 * u + 1), int(1.5 * u + 1) + 1):
        for y in range(0, H + 1):
            w.setze(0, y, z, w.b("water", level=0 if y == H else 8))
    gischt(w, 2, 1, 0, 2.5)
    return w


def bergsee(seed, g=3):
    """Bergsee im Kar: ein tiefblauer, runder See, halbkreisförmig umschlossen von steilen, schneebedeckten
    Felswänden, am offenen Ufer Lärchen, Felsblöcke und Alpenwiesen."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    L = Land(w, R)
    H = 16 * u + 6

    def h(x, z, _):
        d = math.hypot(x, z) / R
        hinten = max(0.0, -z / R)
        return round(max(0, (d - 0.4) / 0.6) * H * (0.4 + hinten) + L.rn(x, 0, z) * 2)
    L.heben(h)
    L.see(0, 0, R * 0.38, 1, tiefe=3)
    L.bauen(fels=GRANIT, unten=-2, schnee_ab=round(H * 0.55))
    L.steine(int(6 * u), 1.3, im_wasser=False)
    bepflanzt(w, L, int(5 * u), ("fichte", "kiefer"))
    return w


def cenote(seed, g=2):
    """Cenote: ein kreisrundes, tiefes Erdloch im Dschungel, die Wände voller Lianen und Wurzeln, unten
    türkisblaues Wasser, ein Holzsteg führt am Rand hinab."""
    from arena import anheben
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    r = 5 * u + 3
    T = round(8 * u + 4)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d > R:
                continue
            if d <= r:
                for y in range(-T, -T + 3):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -T - 1, z, w.b("sand"))
            else:
                for y in range(-T - 1, 1):
                    w.setze(x, y, z, w.b(["stone", "mossy_cobblestone", "andesite", "dirt"][(x * 3 + y + z) % 4]))
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y < 0 and w.P.name(b) != "minecraft:water":
            for dx, dz, f in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
                q = (x + dx, y, z + dz)
                if q not in w.bloecke and math.hypot(*q[::2]) < r + 0.5 and rng.random() < 0.15:
                    for k in range(int(1 + rng.random() * 4)):
                        if (x + dx, y - k, z + dz) not in w.bloecke and y - k > -T + 2:
                            w.setze(x + dx, y - k, z + dz, w.b("vine", **{s: s == f for s in
                                                                          ("north", "south", "east", "west")},
                                                               up=False))
    for k in range(T - 2):
        a = k * 0.35
        x, z = round(math.cos(a) * (r - 0.5)), round(math.sin(a) * (r - 0.5))
        w.setze(x, -k, z, w.b("jungle_slab", type="bottom", waterlogged=False))
    anheben(w, T + 2)
    for k in range(int(5 * u)):
        a = rng.random() * 6.283
        d = r + 3 + rng.random() * (R - r - 4)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        einfuegen(w, wald2.laubbaum(int(rng.integers(1, 10 ** 6)), "jungle", H=_r(6 * u + 4)), x, T + 2, z)
    return w


def geysirfeld(seed, g=2):
    """Geysirfeld: eine dampfende Ebene aus weißem Sinter, gelben Schwefelkrusten und orangen Bakterienrändern,
    in der Mitte eine Wassersäule über einem Sinterkegel, ringsum blubbernde Becken."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    rn = Rauschen(w, 3)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d > R:
                continue
            v = rn(x, 0, z)
            blk = "calcite" if v < 0.45 else "yellow_terracotta" if v < 0.6 else "orange_terracotta" if v < 0.72 \
                else "white_terracotta" if v < 0.85 else "brown_terracotta"
            w.setze(x, 0, z, w.b(blk))
            w.setze(x, -1, z, w.b("tuff"))
    for (cx, cz, r) in [(0, 0, 2.5 * u + 1)] + [(round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55),
                                                1.5 * u + 1) for a in (0.7, 2.6, 4.4)]:
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for z in range(int(cz - r) - 1, int(cz + r) + 2):
                d = math.hypot(x - cx, z - cz)
                if d <= r:
                    w.setze(x, 0, z, w.b("water", level=0))
                    w.setze(x, -1, z, w.b("light_blue_terracotta"))
                elif d <= r + 1:
                    w.setze(x, 1, z, w.b("calcite"))
    Hg = round(8 * u + 4)
    for y in range(1, Hg):
        w.setze(0, y, 0, w.b("water", level=0 if y == Hg - 1 else 8))
    for k in range(int(6 * u)):
        a = w.rng.random() * 6.283
        d = w.rng.random() * R * 0.8
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        w.setze(x, 1, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False)
                if k % 3 == 0 else w.b("calcite"), False)
    return w


def lavafeld(seed, g=2):
    """Erkaltetes Lavafeld: schwarze, gerunzelte Basaltströme mit tiefen Rissen, in denen noch Magma glüht, dazu
    Aschekegel, erste Flechten und ein einzelner verkohlter Baum."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    rn = Rauschen(w, 3)
    rn2 = Rauschen(w, 1.2)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) > R:
                continue
            h = int(rn(x, 0, z) * 3 * u)
            for y in range(-1, h + 1):
                riss = rn2(x, 0, z) > 0.82 and y == h
                w.setze(x, y, z, w.b("magma_block") if riss else
                        w.b(["basalt", "blackstone", "smooth_basalt", "basalt"][(x + y * 2 + z) % 4],
                            **({"axis": "y"} if (x + y * 2 + z) % 4 in (0, 3) else {})))
            if rn2(x, 3, z) < 0.08:
                w.setze(x, h + 1, z, w.b("moss_carpet"))
    for (cx, cz) in [(round(R * 0.4), -round(R * 0.3)), (-round(R * 0.5), round(R * 0.2))]:
        for y in range(0, round(4 * u + 2)):
            r = (4 * u + 2 - y) * 0.9
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                for z in range(int(cz - r) - 1, int(cz + r) + 2):
                    if r - 1 < math.hypot(x - cx, z - cz) <= r:
                        w.setze(x, y + 1, z, w.b("blackstone" if (x + z) % 2 else "tuff"))
    t = wald2.totholz(seed, "dark_oak")
    einfuegen(w, t, 0, int(rn(0, 0, 0) * 3 * u) + 1, 0)
    return w


def steilkueste(seed, g=3):
    """Steilküste: hohe weiße Kreidefelsen fallen senkrecht ins Meer, mit Brandungshöhlen, abgebrochenen
    Felsbrocken im Wasser und einer Wiese mit Klippenpfad oben."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    L = Land(w, R)
    H = round(14 * u + 6)
    L.heben(lambda x, z, h: H + round(L.rn(x, 0, z) * 2) if z < math.sin(x * 0.1) * 4 * u else -4)
    for (x, z), hh in L.h.items():
        if hh < 0:
            L.wasser[(x, z)] = 0
    L.bauen(fels=["calcite", "diorite", "white_terracotta", "smooth_quartz", "calcite"], unten=-5)
    L.bepflanzen(0.4)
    rng = w.rng
    for k in range(4):
        x = int(-R * 0.7 + k * R * 0.45)
        zk = round(math.sin(x * 0.1) * 4 * u)
        for y in range(0, round(4 * u + 2)):
            for z in range(zk - round(3 * u), zk + 1):
                for dx in (-1, 0, 1):
                    w.bloecke.pop((x + dx, y, z), None)
                    if y == 0:
                        w.setze(x + dx, 0, z, w.b("water", level=0))
    L.steine(int(6 * u), 1.8, im_wasser=True, mat=["calcite", "diorite", "white_terracotta"])
    return w


def felsenburg(seed, g=3):
    """Felsenburg: eine Reihe senkrechter, zerklüfteter Sandsteinfelsen wie Türme einer Burg, verbunden durch eine
    schmale Holzbrücke, mit in den Fels gehauenen Treppen und einer Grotte."""
    w = _neu(seed)
    u = U[g]
    R = _r(20 * u + 6)
    L = Land(w, R)
    L.bauen(unten=-2)
    L.bepflanzen(0.35, baeume=int(4 * u), arten=("kiefer", "birke"))
    rn = Rauschen(w, 2)
    mat = gestein(["sandstone", "smooth_sandstone", "cut_sandstone", "yellow_terracotta", "white_terracotta"], rn)
    spitzen = []
    for i in range(4 + g // 2):
        cx = -R * 0.6 + i * R * 1.2 / (3 + g // 2)
        cz = math.sin(i * 1.7) * 3 * u
        H = (12 + (i % 3) * 5) * u + 5
        rx, rz = (2 + (i % 2)) * u + 1.5, (3 + (i % 3)) * u + 1.5
        vol(w, (int(cx - rx) - 2, 1, int(cz - rz) - 2), (int(cx + rx) + 2, int(H) + 2, int(cz + rz) + 2),
            lambda X, Y, Z, cx=cx, cz=cz, H=H, rx=rx, rz=rz: ((X - cx) / rx) ** 2 + ((Z - cz) / rz) ** 2 <
            (1 - (Y / H) ** 6) * (0.75 + 0.3 * np.sin(Y * 0.45 + Z * 0.6)), mat)
        spitzen.append((round(cx), round(H * 0.85), round(cz)))
    for (a, b) in zip(spitzen[1:3], spitzen[2:4]):
        y = min(a[1], b[1])
        for x in range(a[0], b[0] + 1):
            t = (x - a[0]) / max(1, b[0] - a[0])
            z = round(a[2] + (b[2] - a[2]) * t)
            w.setze(x, y, z, w.b("spruce_planks"))
            w.setze(x, y + 1, z + 1, w.b("spruce_fence", north=False, south=False, east=True, west=True,
                                         waterlogged=False), False)
    cx, cy, cz = spitzen[0]
    for k in range(cy - 1):
        a = k * 0.5
        w.setze(cx + round(math.cos(a) * 2), 1 + k, cz + round(math.sin(a) * 2) + 3, w.b("sandstone_stairs",
                                                                                         facing="north",
                                                                                         half="bottom",
                                                                                         shape="straight",
                                                                                         waterlogged=False))
    return w


def schaeren(seed, g=2):
    """Schären: flache, von Gletschern rund geschliffene Granitbuckel als kleine Inseln im glasklaren Wasser, mit
    Kiefern, Heidekraut, einem roten Bootshaus und einem Steg."""
    w = _neu(seed)
    u = U[g]
    R = _r(20 * u + 6)
    L = Land(w, R)
    rn = Rauschen(w, 5)
    L.heben(lambda x, z, h: round((rn(x, 0, z) - 0.5) * 9 * u))
    for (x, z), hh in L.h.items():
        if hh < 0:
            L.wasser[(x, z)] = 0
    L.bauen(fels=["granite", "polished_granite", "stone", "andesite"], unten=-4)
    for (x, z), hh in L.h.items():
        if hh >= 0 and rn(x, 7, z) < 0.6:
            w.setze(x, hh, z, w.b(["granite", "polished_granite", "stone"][(x + z) % 3]))
    L.bepflanzen(0.2, baeume=int(4 * u), arten=("kiefer",))
    land = [p for p, hh in L.h.items() if hh >= 1 and p not in L.wasser]
    if land:
        x, z = min(land, key=lambda p: abs(p[0]) + abs(p[1]))
        hh = L.h[(x, z)]
        for dx in range(-2, 3):
            for dz in range(-2, 2):
                for y in range(hh + 1, hh + 4):
                    if abs(dx) == 2 or dz in (-2, 1):
                        w.setze(x + dx, y, z + dz, w.b("red_terracotta" if y < hh + 3 else "white_terracotta"))
        for k in range(5):
            w.setze(x + 3 + k, max(0, hh), z, w.b("spruce_planks"))
    return w


def moraene(seed, g=2):
    """Moränenfeld: ein welliges Geröllfeld mit großen, rund geschliffenen Findlingen, Schmelzwassertümpeln,
    Moos und Zwergweiden – zurückgelassen von einem längst verschwundenen Gletscher."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    L = Land(w, R)
    rn = Rauschen(w, 4)
    L.heben(lambda x, z, h: round(rn(x, 0, z) * 3 * u))
    for (x, z), hh in L.h.items():
        if hh == 0 and rn(x, 5, z) < 0.35:
            L.wasser[(x, z)] = 1
    L.bauen(gras="moss_block", fels=["gravel", "cobblestone", "andesite"], unten=-2)
    for (x, z), hh in L.h.items():
        if rn(x, 9, z) < 0.4:
            w.setze(x, hh, z, w.b("gravel" if (x + z) % 3 else "coarse_dirt"))
    L.steine(int(10 * u), 2.2 * u, im_wasser=False, mat=["granite", "andesite", "diorite", "mossy_cobblestone"])
    L.bepflanzen(0.25, baeume=int(3 * u), arten=("busch",))
    return w


def terrakotta_mesa(seed, g=3):
    """Terrakotta-Mesa: ein Tafelberg aus kräftig gebänderter Terrakotta – Weiß, Orange, Rot, Gelb und Braun –
    mit vorgelagerten Felsnadeln und einer roten Sandebene."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    L = Land(w, R)
    H = round(14 * u + 6)
    rn = L.rn
    L.heben(lambda x, z, h: H if math.hypot(x * 0.8, z) < R * 0.5 * (0.85 + 0.3 * rn(x, 0, z)) else 0)
    L.bauen(gras="red_sand", fels=TERRA, unten=-1)
    for (x, y, z), b in list(w.bloecke.items()):
        if "terracotta" in w.P.name(b):
            w.bloecke[(x, y, z)] = w.b(TERRA[(y + (1 if rn(x, y, z) > 0.8 else 0)) % len(TERRA)])
    for (x, z), hh in L.h.items():
        if hh == H:
            w.setze(x, hh, z, w.b("grass_block", snowy=False) if rn(x, 4, z) < 0.5 else w.b("coarse_dirt"))
    for k in range(3):
        a = 0.6 + k * 1.9
        cx, cz = math.cos(a) * R * 0.75, math.sin(a) * R * 0.75
        Hn = H * (0.5 + 0.2 * k)
        vol(w, (int(cx) - 3, 1, int(cz) - 3), (int(cx) + 3, int(Hn), int(cz) + 3),
            lambda X, Y, Z, cx=cx, cz=cz: np.hypot(X - cx, Z - cz) < 2.0 * u * (1 - 0.3 * Y / Hn),
            lambda x, y, z: TERRA[y % len(TERRA)])
    bepflanzt(w, L, int(3 * u), ("busch",), dichte=0.1)
    return w


def eisberg(seed, g=3):
    """Eisberg: ein gewaltiger, zerklüfteter Eisberg treibt im dunklen Meer, mit türkis schimmernden Spalten aus
    Blaueis, einer Schneekuppe und kleinen abgebrochenen Schollen ringsum."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                for y in (-2, -1, 0):
                    w.setze(x, y, z, w.b("water", level=0))
    rn = Rauschen(w, 3)
    a, H = R * 0.55, 14 * u + 5
    vol(w, (-int(a) - 2, -2, -int(a) - 2), (int(a) + 2, int(H) + 2, int(a) + 2),
        lambda X, Y, Z: np.hypot(X, Z) < a * (1 - (np.clip(Y, 0, None) / H) ** 1.4) *
        (0.75 + 0.35 * np.sin(np.arctan2(Z, X) * 5 + Y * 0.3)),
        lambda x, y, z: "snow_block" if y > H * 0.8 else ("blue_ice" if rn(x, y, z) < 0.3 else "packed_ice"))
    rng = w.rng
    for k in range(int(8 * u)):
        ang = rng.random() * 6.283
        d = a + 2 + rng.random() * (R - a - 3)
        x, z = round(math.cos(ang) * d), round(math.sin(ang) * d)
        for dx in range(2):
            for dz in range(2):
                w.setze(x + dx, 0, z + dz, w.b("packed_ice"))
                if rng.random() < 0.4:
                    w.setze(x + dx, 1, z + dz, w.b("snow_block"))
    return w


BERGE2 = {
    "erloschener_vulkan": ("Erloschener Vulkan", erloschener_vulkan),
    "fjord": ("Fjord", fjord),
    "canyon": ("Canyon", canyon),
    "karsttuerme": ("Karsttürme", karsttuerme),
    "sandsteinwelle": ("Sandsteinwelle", sandsteinwelle),
    "gletscherzunge": ("Gletscherzunge", gletscherzunge),
    "sinterterrassen": ("Sinterterrassen", sinterterrassen),
    "offene_tropfsteinhoehle": ("Offene Tropfsteinhöhle", offene_tropfsteinhoehle),
    "rote_felskuppel": ("Rote Felskuppel", rote_felskuppel),
    "haengetal": ("Hängetal mit Wasserfall", haengetal),
    "bergsee": ("Bergsee im Kar", bergsee),
    "cenote": ("Cenote", cenote),
    "geysirfeld": ("Geysirfeld", geysirfeld),
    "lavafeld": ("Erkaltetes Lavafeld", lavafeld),
    "steilkueste": ("Steilküste", steilkueste),
    "felsenburg": ("Felsenburg", felsenburg),
    "schaeren": ("Schären", schaeren),
    "moraene": ("Moränenfeld", moraene),
    "terrakotta_mesa": ("Terrakotta-Mesa", terrakotta_mesa),
    "eisberg": ("Eisberg", eisberg),
}

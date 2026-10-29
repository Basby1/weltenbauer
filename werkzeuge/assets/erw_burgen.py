"""Burgen & Festungen II – zwanzig weitere Wehrbauten: Grenzfeste am Fluss, Inselkastell, Zwingertor,
Wüstenkastell, Schildmauerburg, Jagdschloss, Spornburg, Burghof, Wehrkirche, Rundturm-Kastell, Sechseckfestung,
Vorburg, Nordische Holzburg, Bastionsturm am Meer, Wehrgang mit Pechnasen, Felsenburg, Barockschloss, Grafenburg,
Zaubererburg und Römisches Kastell."""

from __future__ import annotations

import math

import wald2
from fantasie2 import garten
from feinbau import (Dachmat, Mix, balkon, fenster, fensterreihe, kamin, kegeldach, kram, laterne, mauer, platte,
                     satteldach, stamm, treppe, tuer, zaun)
from flora import _neu
from himmelsstadt2 import eckturm, haus, rundturm
import erw_haeuser  # noqa: F401,E402  (Stile ziegel, schiefer, lehm)
from lib import einfuegen

S = [0.6, 1.0, 1.6, 2.5]


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def stein(w, art="grau"):
    return {"grau": M(w, [("stone_bricks", 3), ("cobblestone", 1), ("mossy_stone_bricks", 1), ("andesite", 1)]),
            "sand": M(w, [("smooth_sandstone", 3), ("cut_sandstone", 1), ("sandstone", 1)]),
            "dunkel": M(w, [("deepslate_bricks", 2), ("cobbled_deepslate", 1), ("polished_deepslate", 1)]),
            "hell": M(w, [("calcite", 2), ("smooth_quartz", 1), ("diorite", 1)]),
            "ziegel": M(w, [("bricks", 3), ("stone_bricks", 1)])}[art]


DACH = {"schiefer": ["deepslate_tile", "cobbled_deepslate", "deepslate_brick"],
        "rot": ["mcw:red_terracotta", "brick", "granite"],
        "blau": ["mcw:blue_terracotta", "mcw:light_blue_terracotta", "deepslate_tile"],
        "kupfer": ["waxed_oxidized_cut_copper", "waxed_weathered_cut_copper"],
        "sand": ["smooth_sandstone", "sandstone"]}


def wall(w, punkte, y0, H, st, zinnen=True, wehrgang=True, dicke=2):
    """Mauer entlang eines geschlossenen Polygons (Liste von (x, z))."""
    zellen = set()
    for a, b in zip(punkte, punkte[1:] + punkte[:1]):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for i in range(n + 1):
            t = i / n
            x, z = round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t)
            for dx in range(dicke):
                for dz in range(dicke):
                    zellen.add((x + dx - dicke // 2, z + dz - dicke // 2))
    for (x, z) in zellen:
        for y in range(y0 - 3, y0 + H):
            w.setze(x, y, z, st(x, y, z))
        if zinnen and (x + z) % 2 == 0:
            w.setze(x, y0 + H, z, st(x, y0 + H, z))
    return zellen


def tor(w, x, z, y0, breite=1, hoehe=3, achse="z", gitter=True):
    for d in range(-breite, breite + 1):
        for y in range(y0, y0 + hoehe):
            for k in range(-2, 3):
                p = (x + d, y, z + k) if achse == "z" else (x + k, y, z + d)
                w.bloecke.pop(p, None)
    if gitter:
        for d in range(-breite, breite + 1):
            p = (x + d, y0 + hoehe - 1, z) if achse == "z" else (x, y0 + hoehe - 1, z + d)
            w.setze(*p, w.b("iron_bars", north=achse != "z", south=achse != "z", east=achse == "z",
                            west=achse == "z", waterlogged=False))


def rundturm_einfach(w, cx, cz, y0, r, H, st, dach, form="kegel"):
    for y in range(y0 - 3, y0 + H):
        for x in range(cx - r - 1, cx + r + 2):
            for z in range(cz - r - 1, cz + r + 2):
                d = math.hypot(x - cx, z - cz)
                if d <= r + 0.4 and (d > r - 0.8 or y < y0):
                    luke = y > y0 + 2 and (y - y0) % 4 == 2 and (x == cx or z == cz) and d > r - 0.8
                    w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                         waterlogged=False) if luke else st(x, y, z))
    if dach:
        return kegeldach(w, cx, cz, y0 + H, r, Dachmat(w, DACH[dach]), form=form)
    for x in range(cx - r - 1, cx + r + 2):
        for z in range(cz - r - 1, cz + r + 2):
            d = math.hypot(x - cx, z - cz)
            if d <= r + 0.4:
                w.setze(x, y0 + H - 1, z, st(x, 0, z))
                if d > r - 0.8 and (x + z) % 2 == 0:
                    w.setze(x, y0 + H, z, st(x, 0, z))


def fahne(w, x, y, z, farben=("red_wool", "yellow_wool")):
    for k in range(3):
        w.setze(x, y + k, z, zaun(w, "dark_oak"))
    for k in range(3):
        for d in range(2):
            w.setze(x + 1 + k, y + 2 - d, z, w.b(farben[(k + d) % 2]), False)


def wasser_ring(w, R, breite=3):
    for x in range(-int(R) - breite - 1, int(R) + breite + 2):
        for z in range(-int(R) - breite - 1, int(R) + breite + 2):
            d = max(abs(x), abs(z))
            if R + 1 <= d <= R + breite:
                for y in (-1, 0):
                    w.setze(x, y, z, w.b("water", level=0))
                w.bloecke.pop((x, 1, z), None)


# ============================================================================ Burgen

def grenzfeste(seed, g=2):
    """Grenzfeste am Fluss: eine quadratische Feste mit vier Ecktürmen sichert einen Flussübergang, eine steinerne
    Brücke führt durch ihr Torhaus, Zollhäuschen und Wachfeuer."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 5)
    zl = garten(w, R + 8, seed=seed, baeume=2)
    for (x, z) in zl:
        if R + 2 < z < R + 7:
            for y in (-1, 0):
                w.setze(x, y, z, w.b("water", level=0))
            w.bloecke.pop((x, 1, z), None)
    st = stein(w)
    wall(w, [(-R, -R), (R, -R), (R, R), (-R, R)], 1, int(4 * s + 4), st)
    for (x, z) in ((-R, -R), (R, -R), (-R, R), (R, R)):
        eckturm(w, x, z, 1, 2, int(6 * s + 6), st, Dachmat(w, DACH["schiefer"]), form="kegel")
    eckturm(w, 0, R, 1, 2, int(6 * s + 5), st, None)
    tor(w, 0, R, 1, 1, 4)
    for z in range(R + 2, R + 8):
        for x in range(-1, 2):
            w.setze(x, 1, z, w.b("stone_bricks"))
    haus(w, -R // 2, -R // 3, 7, 5, 1, "stein", geschosse=2, tuer_s="east")
    fahne(w, R, int(6 * s + 6) + 6, R)
    return w


def inselkastell(seed, g=2):
    """Inselkastell: ein trutziges Kastell auf einer Felsinsel im See, mit hohem Bergfried, Ringmauer bis ans
    Wasser, Bootssteg und einem schmalen Damm zum Ufer."""
    w = _neu(seed)
    s = S[g]
    R = int(16 * s + 8)
    rng = w.rng
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d <= R:
                ri = R * 0.45
                if d <= ri:
                    for y in range(-2, 2):
                        w.setze(x, y, z, w.b(["stone", "andesite"][int(rng.random() * 2)]))
                else:
                    for y in (-1, 0):
                        w.setze(x, y, z, w.b("water", level=0))
                    w.setze(x, -2, z, w.b("gravel"))
    a = int(R * 0.38)
    st = stein(w)
    wall(w, [(-a, -a), (a, -a), (a, a), (-a, a)], 2, int(4 * s + 3), st)
    eckturm(w, 0, 0, 2, int(2 * s + 1), int(12 * s + 6), st, Dachmat(w, DACH["schiefer"]), form="glocke")
    for (x, z) in ((-a, -a), (a, a)):
        rundturm_einfach(w, x, z, 2, 2, int(6 * s + 5), st, "schiefer")
    for z in range(a, R + 1):
        for x in range(-1, 2):
            w.setze(x, 1, z, w.b("cobblestone"))
    tor(w, 0, a, 2, 1, 3)
    return w


def zwingertor(seed, g=2):
    """Zwingertor: ein doppeltes Tor mit äußerem und innerem Torturm, dazwischen ein enger Zwinger mit
    Schießscharten auf allen Seiten, Fallgitter und Zugbrücke über einem Graben."""
    w = _neu(seed)
    s = S[g]
    L = int(10 * s + 6)
    zl = garten(w, L + 6, "south", seed=seed)
    st = stein(w)
    B = int(3 * s + 3)
    for z in range(-L, L + 1):
        for sx in (-1, 1):
            for y in range(-2, int(4 * s + 4)):
                w.setze(sx * B, y, z, st(sx * B, y, z))
            if z % 3 == 0:
                w.setze(sx * B, int(4 * s + 3) - 1, z, w.b("iron_bars", north=True, south=True, east=False,
                                                           west=False, waterlogged=False))
    for zt in (-L, L):
        mauer(w, -B - 2, zt - 2, B + 2, zt + 2, 1, int(7 * s + 6), st)
        tor(w, 0, zt, 1, 1, 4, gitter=True)
        kegeldach(w, 0, zt, int(7 * s + 7), B + 2, Dachmat(w, DACH["schiefer"]), form="kegel", eckig=True)
    for x in range(-B - 6, B + 7):
        for z in range(L + 3, L + 6):
            if abs(x) > 1:
                for y in (-1, 0):
                    w.setze(x, y, z, w.b("water", level=0))
                w.bloecke.pop((x, 1, z), None)
            else:
                w.setze(x, 1, z, w.b("spruce_planks"))
    return w


def wuestenkastell(seed, g=2):
    """Wüstenkastell: ein Kastell aus hellem Sandstein mit wuchtigen, nach oben verjüngten Türmen, Zinnen in
    Schwalbenschwanzform, einem Innenhof mit Brunnen und Palmen."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 5)
    for x in range(-R - 6, R + 7):
        for z in range(-R - 6, R + 7):
            w.setze(x, 0, z, w.b("sand"))
            w.setze(x, -1, z, w.b("sandstone"))
    st = stein(w, "sand")
    wall(w, [(-R, -R), (R, -R), (R, R), (-R, R)], 1, int(4 * s + 4), st)
    for (x, z) in ((-R, -R), (R, -R), (-R, R), (R, R)):
        H = int(7 * s + 6)
        for y in range(1, H):
            b = 3 if y < H * 0.6 else 2
            for dx in range(-b, b + 1):
                for dz in range(-b, b + 1):
                    if abs(dx) == b or abs(dz) == b:
                        w.setze(x + dx, y, z + dz, st(x + dx, y, z + dz))
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if (abs(dx) == 2 or abs(dz) == 2) and (dx + dz) % 2 == 0:
                    w.setze(x + dx, H, z + dz, w.b("sandstone_wall", up=True, north="none", south="none",
                                                   east="none", west="none", waterlogged=False))
    tor(w, 0, R, 1, 1, 4)
    for x in range(-1, 2):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("smooth_sandstone") if (x or z) else w.b("water", level=0))
    for k in range(3):
        a = k * 2.094
        einfuegen(w, wald2.palme(seed + k), round(math.cos(a) * R * 0.5), 0, round(math.sin(a) * R * 0.5))
    return w


def schildmauerburg(seed, g=2):
    """Schildmauerburg: eine Höhenburg auf einem Bergsporn, die zur Angriffsseite eine gewaltige, hohe Schildmauer
    zeigt, dahinter Palas und Bergfried geduckt, steiler Fels ringsum."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rng = w.rng
    H0 = int(5 * s + 3)
    for x in range(-R - 3, R + 4):
        for z in range(-R - 3, R + 4):
            d = math.hypot(x, z * 1.3)
            if d <= R + 3:
                h = H0 if d <= R else int(H0 * (1 - (d - R) / 3))
                for y in range(-1, h + 1):
                    w.setze(x, y, z, w.b(["stone", "andesite", "tuff"][int(rng.random() * 3)]) if y < h or d > R
                            else w.b("grass_block", snowy=False))
    st = stein(w)
    zs = -int(R * 0.55)
    for x in range(-int(R * 0.7), int(R * 0.7) + 1):
        for z in range(zs - 2, zs + 1):
            for y in range(H0 + 1, H0 + int(12 * s + 8)):
                w.setze(x, y, z, st(x, y, z))
        if x % 2 == 0:
            w.setze(x, H0 + int(12 * s + 8), zs - 1, st(x, 0, zs))
    haus(w, 0, int(R * 0.15), 9, 6, H0 + 1, "stein", geschosse=2, tuer_s="south")
    eckturm(w, int(R * 0.45), -int(R * 0.15), H0 + 1, 2, int(8 * s + 6), st, Dachmat(w, DACH["schiefer"]),
            form="nadel")
    return w


def jagdschloss(seed, g=2):
    """Jagdschloss: ein zierliches Schlösschen im Wald mit zwei Rundtürmen und Zwiebelhelmen, Hirschgeweih über dem
    Portal, Fachwerk-Obergeschoss, Freitreppe und einem Teich davor."""
    w = _neu(seed)
    s = S[g]
    zl = garten(w, 12 * s + 5, seed=seed, baeume=4)
    B = int(11 * s + 4) | 1
    haus(w, 0, -2, B, 7, 2, "fachwerk", geschosse=2 + (g > 1), tuer_s="south", balk=True)
    for sx in (-1, 1):
        rundturm(w, sx * (B // 2 + 2), -2, 1, 2, int(8 * s + 5), M(w, [("calcite", 2), ("smooth_quartz", 1)]),
                 Dachmat(w, DACH["kupfer"]), form="glocke")
    for k in range(3):
        for x in range(-2 - k, 3 + k):
            w.setze(x, 1, 2 + k, treppe(w, "stone_brick", "north"))
    w.setze(0, 6, 2, w.b("bone_block", axis="x"))
    for sx in (-1, 1):
        w.setze(sx, 7, 2, w.b("bone_block", axis="y"))
        w.setze(sx * 2, 8, 2, w.b("bone_block", axis="y"))
    for (x, z) in zl:
        if math.hypot(x, z - 10 * s) < 3 * s + 1:
            w.setze(x, 0, z, w.b("water", level=0))
            w.bloecke.pop((x, 1, z), None)
    return w


def spornburg(seed, g=2):
    """Spornburg: eine schmale Burg auf einem steil abfallenden Felssporn, die Mauern folgen dem Fels, ein hoher
    Bergfried an der Spitze, ein Halsgraben mit Holzbrücke trennt sie vom Hang."""
    w = _neu(seed)
    s = S[g]
    L = int(16 * s + 8)
    rng = w.rng
    for x in range(-L - 4, L + 5):
        for z in range(-int(L * 0.5) - 3, int(L * 0.5) + 4):
            b = (L * 0.4) * (1 - max(0, x) / (L + 4)) + 2
            if abs(z) <= b or x < -L * 0.6:
                h = int(8 * s + 4 - (abs(z) / b) ** 3 * 6) if abs(z) <= b else int(8 * s + 4)
                for y in range(-2, h + 1):
                    w.setze(x, y, z, w.b(["stone", "andesite", "tuff"][int(rng.random() * 3)]) if y < h else
                            w.b("grass_block", snowy=False))
    yb = int(8 * s + 4) + 1
    st = stein(w)
    for x in range(-int(L * 0.45), -int(L * 0.35)):
        for z in range(-int(L * 0.5) - 3, int(L * 0.5) + 4):
            for y in range(yb - 6, yb):
                w.bloecke.pop((x, y, z), None)
    for x in range(-int(L * 0.45), -int(L * 0.35)):
        w.setze(x, yb - 1, 0, w.b("spruce_planks"))
    pts = [(-int(L * 0.3), -int(L * 0.3)), (int(L * 0.7), -2), (int(L * 0.7), 2), (-int(L * 0.3), int(L * 0.3))]
    wall(w, pts, yb, int(3 * s + 3), st)
    eckturm(w, int(L * 0.6), 0, yb, 2, int(10 * s + 6), st, Dachmat(w, DACH["schiefer"]), form="nadel")
    haus(w, int(L * 0.1), 0, 7, 5, yb, "stein", geschosse=2, tuer_s="west")
    tor(w, -int(L * 0.3), 0, yb, 1, 3, achse="x")
    return w


def burghof(seed, g=2):
    """Burghof: der lebendige Innenhof einer Burg – Ställe, Schmiede, Backhaus, Ziehbrunnen, Waffenständer und
    Strohballen, umgeben von Wehrgängen, ein Tor öffnet sich nach außen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    garten(w, R + 3, seed=seed, baeume=0)
    st = stein(w)
    wall(w, [(-R, -R), (R, -R), (R, R), (-R, R)], 1, int(4 * s + 4), st)
    tor(w, 0, R, 1, 1, 4)
    haus(w, -R + 5, -R + 4, 7, 5, 1, "fachwerk", geschosse=1, tuer_s="south")
    haus(w, R - 5, -R + 4, 7, 5, 1, "ziegel", geschosse=1, tuer_s="south")
    for x in range(-R + 2, -R + 9):
        for z in range(R - 6, R - 2):
            if x in (-R + 2, -R + 8) or z == R - 6:
                for y in range(1, 4):
                    w.setze(x, y, z, stamm(w, "spruce") if y < 3 else w.b("spruce_planks"))
        w.setze(x, 4, R - 6, w.b("spruce_slab", type="bottom", waterlogged=False))
    for x in range(-R + 3, -R + 8):
        w.setze(x, 1, R - 4, w.b("hay_block", axis="x"))
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            w.setze(dx, 1, dz, w.b("cobblestone_wall", up=True, north="none", south="none", east="none",
                                   west="none", waterlogged=False) if (dx or dz) else w.b("water", level=0))
    for (x, z) in ((-1, 0), (1, 0)):
        for y in range(2, 4):
            w.setze(x, y, z, zaun(w, "spruce"))
    for x in range(-1, 2):
        w.setze(x, 4, 0, w.b("spruce_slab", type="bottom", waterlogged=False))
    kram(w, R - 4, 1, R - 4, 6)
    return w


def wehrkirche(seed, g=2):
    """Wehrkirche: eine trutzige Dorfkirche mit massivem Wehrturm, Schießscharten und Zinnen, umgeben von einer
    Kirchhofmauer mit Gaden-Speichern, wie eine kleine Festung."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 5)
    garten(w, R + 3, seed=seed, baeume=1)
    st = stein(w)
    wall(w, [(-R, -R), (R, -R), (R, R), (-R, R)], 1, 3, st, zinnen=False, dicke=1)
    tor(w, 0, R, 1, 0, 3, gitter=False)
    L, B = int(10 * s + 5), int(5 * s + 3)
    mauer(w, -B // 2, -L // 2, B // 2, L // 2, 1, int(5 * s + 4), st)
    satteldach(w, -B // 2, -L // 2, B // 2, L // 2, int(5 * s + 5), Dachmat(w, DACH["schiefer"]), first_x=False,
               traufe="dark_oak", steil=2, giebel=st)
    eckturm(w, 0, -L // 2 - 2, 1, 2, int(12 * s + 6), st, None)
    for x in range(-R + 1, -R + 4):
        for z in range(-R + 2, R - 1, 4):
            for y in range(1, 3):
                w.setze(x, y, z, w.b("spruce_planks"))
    tuer(w, 0, 1, L // 2, "south", holz="dark_oak")
    return w


def rundturmkastell(seed, g=2):
    """Rundturm-Kastell: ein kompaktes Kastell mit vier dicken Rundtürmen an den Ecken, Kegeldächer mit Wetterfahnen,
    ein Torbau mit Erker und ein Innenhof mit Wohnbau."""
    w = _neu(seed)
    s = S[g]
    R = int(8 * s + 5)
    garten(w, R + 5, seed=seed, baeume=2)
    st = stein(w)
    wall(w, [(-R, -R), (R, -R), (R, R), (-R, R)], 1, int(4 * s + 3), st)
    for (x, z) in ((-R, -R), (R, -R), (-R, R), (R, R)):
        rundturm_einfach(w, x, z, 1, int(2 * s + 2), int(7 * s + 6), st, "rot")
    tor(w, 0, R, 1, 1, 3)
    haus(w, 0, -R // 2, R + 3, 5, 1, "stein", geschosse=2, tuer_s="south")
    return w


def sechseckfestung(seed, g=3):
    """Sechseckfestung: eine Festung mit sechseckigem Grundriss, an jeder Ecke ein eckiger Turm, in der Mitte ein
    sechseckiger Donjon mit Glockendach, ein wassergefüllter Graben ringsum."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    garten(w, R + 7, seed=seed, baeume=0)
    for x in range(-R - 6, R + 7):
        for z in range(-R - 6, R + 7):
            if R + 2 < math.hypot(x, z) < R + 5:
                for y in (-1, 0):
                    w.setze(x, y, z, w.b("water", level=0))
                w.bloecke.pop((x, 1, z), None)
    st = stein(w, "grau")
    pts = [(round(math.cos(k / 6 * 6.283) * R), round(math.sin(k / 6 * 6.283) * R)) for k in range(6)]
    wall(w, pts, 1, int(4 * s + 3), st)
    for (x, z) in pts:
        eckturm(w, x, z, 1, 2, int(6 * s + 5), st, Dachmat(w, DACH["blau"]), form="kegel")
    rundturm_einfach(w, 0, 0, 1, int(3 * s + 2), int(10 * s + 6), st, "blau", form="glocke")
    for z in range(R - 1, R + 6):
        for x in range(-1, 2):
            w.setze(x, 1, z, w.b("spruce_planks"))
    tor(w, 0, R, 1, 1, 3)
    return w


def vorburg(seed, g=2):
    """Vorburg: der Wirtschaftshof vor einer Burg mit Scheune, Pferdestall, Brauhaus und Gesindehaus, umgeben von
    einer einfachen Mauer, im Hintergrund ragt der Torturm der Hauptburg."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    garten(w, R + 3, seed=seed, baeume=1)
    st = stein(w)
    wall(w, [(-R, -R), (R, -R), (R, R), (-R, R)], 1, 3, st, zinnen=False)
    tor(w, 0, R, 1, 1, 3, gitter=False)
    haus(w, -R // 2, -R // 2, 9, 6, 1, "fachwerk", geschosse=1, tuer_s="south")
    haus(w, R // 2, -R // 2, 7, 6, 1, "ziegel", geschosse=2, tuer_s="south")
    haus(w, -R // 2, R // 3, 7, 5, 1, "stein", geschosse=1, tuer_s="east")
    eckturm(w, 0, -R, 1, 3, int(10 * s + 6), st, Dachmat(w, DACH["schiefer"]), form="kegel")
    kram(w, R // 2, 1, R // 3, 6)
    return w


def holzburg(seed, g=2):
    """Nordische Holzburg: eine Burg ganz aus Holz – Palisaden mit angespitzten Stämmen, hölzerne Wachtürme mit
    Spitzdächern, eine lange Halle mit Drachenköpfen am Giebel auf einem Erdhügel."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 5)
    garten(w, R + 4, seed=seed, baeume=1)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d <= R * 0.6:
                h = int(3 * (1 - d / (R * 0.6))) + 1
                for y in range(1, h + 1):
                    w.setze(x, y, z, w.b("dirt" if y < h else "grass_block", **({} if y < h else {"snowy": False})))
    for k in range(int(R * 7)):
        a = k / (R * 7) * 6.283
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        if abs(x) <= 1 and z > 0:
            continue
        for y in range(1, int(4 * s) + 4):
            w.setze(x, y, z, w.b("spruce_log", axis="y"))
        w.setze(x, int(4 * s) + 4, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                          waterlogged=False))
    for k in range(4):
        a = k * 1.571 + 0.785
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        for y in range(1, int(7 * s) + 5):
            for (dx, dz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                w.setze(x + dx, y, z + dz, stamm(w, "spruce", geschaelt=False))
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                w.setze(x + dx, int(7 * s) + 5, z + dz, w.b("spruce_planks"))
        kegeldach(w, x, z, int(7 * s) + 7, 2, Dachmat(w, ["dark_oak", "spruce"]), form="kegel", eckig=True)
    from feinbau import fachwerk
    L = int(10 * s + 4)
    fachwerk(w, -3, -L // 2, 3, L // 2, 4, 7, M(w, [("spruce_planks", 2), ("stripped_spruce_log", 1)]),
             holz="dark_oak", abstand=2)
    satteldach(w, -3, -L // 2, 3, L // 2, 8, Dachmat(w, ["dark_oak", "spruce"]), first_x=False, steil=2,
               traufe="dark_oak")
    return w


def bastionsturm(seed, g=2):
    """Bastionsturm am Meer: ein runder, flacher Geschützturm auf einer Klippe mit dicken Mauern, Kanonen in
    Scharten, Fahnenmast und einem Laufgang zur Küstenmauer, Wellen unten."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 6)
    rng = w.rng
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                if z < R * 0.2:
                    h = int(6 * s + 3)
                    for y in range(-2, h + 1):
                        w.setze(x, y, z, w.b(["stone", "andesite"][int(rng.random() * 2)]) if y < h else
                                w.b("grass_block", snowy=False))
                else:
                    for y in (-1, 0):
                        w.setze(x, y, z, w.b("water", level=0))
    st = stein(w, "grau")
    y0 = int(6 * s + 3) + 1
    r = int(4 * s + 3)
    cz = int(R * 0.15)
    for y in range(1, y0 + int(4 * s) + 3):
        for x in range(-r - 1, r + 2):
            for z in range(cz - r - 1, cz + r + 2):
                d = math.hypot(x, z - cz)
                if r - 1.5 < d <= r + 0.4:
                    w.setze(x, y, z, st(x, y, z))
    for k in range(6):
        a = k / 6 * 3.14 + 0.2
        x, z = round(math.cos(a) * r), round(cz + math.sin(a) * r)
        w.setze(x, y0 + int(4 * s) + 1, z, w.b("air"))
        w.setze(x, y0 + int(4 * s), z, w.b("black_concrete"))
    fahne(w, 0, y0 + int(4 * s) + 3, cz, ("blue_wool", "white_wool"))
    for x in range(-R, -r):
        for y in range(y0, y0 + 3):
            w.setze(x, y, cz, st(x, y, cz))
    return w


def pechnasenwehrgang(seed, g=2):
    """Wehrgang mit Pechnasen: ein Abschnitt einer hohen Burgmauer mit überdachtem Wehrgang, vorkragenden Pechnasen,
    einem halbrunden Schalenturm und Treppen vom Hof hinauf."""
    w = _neu(seed)
    s = S[g]
    L = int(16 * s + 8)
    garten(w, L, "north", seed=seed, baeume=1)
    st = stein(w)
    H = int(7 * s + 6)
    for x in range(-L, L + 1):
        for z in range(-1, 2):
            for y in range(1, H + 1):
                w.setze(x, y, z, st(x, y, z))
        if x % 3 == 0:
            w.setze(x, H, 2, st(x, H, 2))
            w.setze(x, H - 1, 2, treppe(w, "stone_brick", "north", "top"))
        w.setze(x, H + 1, 1, st(x, H, 1) if x % 2 == 0 else w.b("air"))
        for z in (-1, 0):
            w.setze(x, H + 3, z, w.b("dark_oak_planks"))
        if x % 4 == 0:
            for y in range(H + 1, H + 3):
                w.setze(x, y, -1, zaun(w, "dark_oak"))
    r = int(3 * s + 2)
    for y in range(1, H + 3):
        for x in range(-r, r + 1):
            for z in range(1, r + 2):
                d = math.hypot(x, z - 1)
                if r - 1 < d <= r + 0.3:
                    w.setze(x, y, z, st(x, y, z))
    for k in range(H):
        for x in (L - 3, L - 2):
            w.setze(x, 1 + k, -2 - k, treppe(w, "stone_brick", "south"))
    return w


def felsenburg(seed, g=2):
    """Felsenburg: eine Burg, die direkt in eine hohe Felsnadel gehauen ist – Fenster, Balkone und Tore im Fels,
    Holzgalerien kleben außen, oben ein Turm mit Spitzdach."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 4)
    rng = w.rng
    garten(w, R + 6, seed=seed, baeume=2)
    H = int(18 * s + 8)
    for y in range(1, H):
        r = R * (1 - 0.35 * y / H)
        for x in range(-int(R) - 1, int(R) + 2):
            for z in range(-int(R) - 1, int(R) + 2):
                if math.hypot(x, z) <= r * (0.9 + 0.2 * rng.random()):
                    w.setze(x, y, z, w.b(["stone", "andesite", "tuff", "calcite"][int(rng.random() * 4)]))
    for y in range(4, H - 2, 4):
        r = int(R * (1 - 0.35 * y / H))
        for (x, z, sname) in ((0, r, "south"), (r, 0, "east"), (-r, 0, "west")):
            fenster(w, x, y, z, sname, holz="dark_oak", blumen=0.3)
        for x in range(-2, 3):
            w.setze(x, y - 1, r + 1, w.b("spruce_planks"))
            w.setze(x, y, r + 2, zaun(w, "spruce"))
    eckturm(w, 0, 0, H, 2, int(5 * s + 4), M(w, [("stone_bricks", 1)]), Dachmat(w, DACH["schiefer"]), form="nadel")
    tuer(w, 0, 1, R, "south", holz="dark_oak")
    for y in (1, 2):
        w.bloecke.pop((0, y, R - 1), None)
    return w


def barockschloss(seed, g=3):
    """Barockschloss: ein symmetrisches, helles Schloss mit Mittelbau unter einer Kupferkuppel, zwei langen
    Flügeln mit Mansarddächern, Ehrenhof, Freitreppe und Springbrunnen."""
    w = _neu(seed)
    s = S[g]
    B = int(18 * s + 8)
    zl = garten(w, B * 0.75 + 4, seed=seed, baeume=0)
    for sx in (-1, 1):
        haus(w, sx * (B // 2), 0, B // 2 + 1, 7, 1, "kupfer", geschosse=2 + (g > 2), tuer_s="south", schorn=False)
    haus(w, 0, -2, 9, 9, 1, "kupfer", geschosse=3 + (g > 2), tuer_s="south", first_x=False, schorn=False)
    from himmelsstadt2 import rundturm as rt
    kegeldach(w, 0, -2, 14 + 4 * (g > 2), 4, Dachmat(w, DACH["kupfer"]), form="glocke")
    for sx in (-1, 1):
        for z in range(4, int(B * 0.7)):
            w.setze(sx * (B // 2 + B // 4 - 1), 1, z, w.b("stone_brick_wall", up=True, north="none", south="none",
                                                          east="none", west="none", waterlogged=False)) if z % 2 \
                else None
    for x in range(-2, 3):
        for z in range(int(B * 0.4) - 2, int(B * 0.4) + 3):
            if math.hypot(x, z - B * 0.4) <= 2.3:
                w.setze(x, 1, z, w.b("water", level=0) if math.hypot(x, z - B * 0.4) < 1.5 else
                        w.b("smooth_quartz"))
    w.setze(0, 2, int(B * 0.4), w.b("water", level=0))
    return w


def grafenburg(seed, g=1):
    """Grafenburg: eine kleine, gemütliche Burg mit einem Wohnturm, Fachwerk-Aufsatz, einer Ringmauer mit
    Torhaus, Gemüsegarten im Hof und Rosen an der Mauer."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    garten(w, R + 4, seed=seed, baeume=1)
    st = stein(w)
    wall(w, [(-R, -R), (R, -R), (R, R), (-R, R)], 1, int(3 * s + 3), st)
    tor(w, 0, R, 1, 0, 3)
    eckturm(w, -R // 2, -R // 2, 1, 2, int(7 * s + 5), st, None)
    haus(w, -R // 2, -R // 2, 5, 5, int(7 * s + 6), "fachwerk", geschosse=1, tuer_s="south", schorn=False)
    for x in range(1, R - 1):
        for z in range(1, R - 1):
            if x % 2:
                w.setze(x, 0, z, w.b("farmland", moisture=7))
                w.setze(x, 1, z, w.b("carrots", age=7))
    return w


def zaubererburg(seed, g=2):
    """Zaubererburg: eine verspielte Burg mit vielen schlanken Türmen unterschiedlicher Höhe, blauen Spitzhelmen
    mit goldenen Sternen, Erkern, Brücken zwischen den Türmen und einem Sternenbanner."""
    w = _neu(seed)
    s = S[g]
    R = int(8 * s + 4)
    garten(w, R + 5, seed=seed, baeume=2)
    st = stein(w, "hell")
    rng = w.rng
    tuerme = [(0, 0, 3, int(16 * s + 8))]
    for k in range(5 + g):
        a = k / (5 + g) * 6.283 + rng.random() * 0.4
        d = R * (0.5 + rng.random() * 0.4)
        tuerme.append((round(math.cos(a) * d), round(math.sin(a) * d), 1 + int(rng.random() * 2),
                       int((7 + rng.random() * 7) * s + 4)))
    for (x, z, r, H) in tuerme:
        rundturm_einfach(w, x, z, 1, r, H, st, "blau", form="nadel")
        w.setze(x + r + 1, H - 2, z, w.b("gold_block"))
    for (a, b) in zip(tuerme[1:], tuerme[2:]):
        y = min(a[3], b[3]) - 3
        n = int(math.dist(a[:2], b[:2]) * 1.5)
        for i in range(n + 1):
            t = i / n
            w.setze(round(a[0] + (b[0] - a[0]) * t), y, round(a[1] + (b[1] - a[1]) * t), w.b("smooth_quartz_slab",
                                                                                              type="bottom",
                                                                                              waterlogged=False),
                    False)
    tuer(w, 0, 1, 3, "south", holz="birch")
    return w


def roemisches_kastell(seed, g=2):
    """Römisches Kastell: ein rechteckiges Legionslager mit abgerundeten Ecken, Holz-Steinmauer, vier Tortürmen,
    geraden Lagerstraßen, Mannschaftsbaracken und dem Stabsgebäude in der Mitte."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    garten(w, R + 4, seed=seed, baeume=0)
    st = stein(w)
    pts = [(-R + 2, -R), (R - 2, -R), (R, -R + 2), (R, R - 2), (R - 2, R), (-R + 2, R), (-R, R - 2), (-R, -R + 2)]
    wall(w, pts, 1, int(3 * s + 3), st)
    for (x, z, ach) in ((0, -R, "z"), (0, R, "z"), (-R, 0, "x"), (R, 0, "x")):
        for dx in (-2, 2):
            p = (x + dx, z) if ach == "z" else (x, z + dx)
            for y in range(1, int(5 * s + 5)):
                for ex in range(-1, 2):
                    for ez in range(-1, 2):
                        w.setze(p[0] + ex, y, p[1] + ez, st(p[0], y, p[1]))
        tor(w, x, z, 1, 1, 3, achse=ach, gitter=False)
    for x in range(-R, R + 1):
        for k in (-1, 0, 1):
            w.setze(x, 0, k, w.b("gravel"))
            w.setze(k, 0, x, w.b("gravel"))
    for k in range(4):
        for sx in (-1, 1):
            for sz in (-1, 1):
                if k < 2:
                    cx, cz = sx * (R // 2 + 1), sz * (R // 4 + k * 3 + 2)
                    mauer(w, cx - R // 3, cz - 1, cx + R // 3, cz + 1, 1, 3, M(w, [("white_terracotta", 2),
                                                                                   ("spruce_planks", 1)]))
                    satteldach(w, cx - R // 3, cz - 1, cx + R // 3, cz + 1, 4, Dachmat(w, DACH["rot"]), first_x=True,
                               ue=0, traufe="spruce", knick=False, firstzier=False, giebelfenster=False)
    mauer(w, -3, -3, 3, 3, 1, 4, M(w, [("smooth_quartz", 1)]))
    satteldach(w, -3, -3, 3, 3, 5, Dachmat(w, DACH["rot"]), first_x=True, traufe="birch")
    return w


BURGEN3 = {
    "grenzfeste": ("Grenzfeste am Fluss", grenzfeste),
    "inselkastell": ("Inselkastell", inselkastell),
    "zwingertor": ("Zwingertor", zwingertor),
    "wuestenkastell": ("Wüstenkastell", wuestenkastell),
    "schildmauerburg": ("Schildmauerburg", schildmauerburg),
    "jagdschloss": ("Jagdschloss", jagdschloss),
    "spornburg": ("Spornburg", spornburg),
    "burghof": ("Burghof", burghof),
    "wehrkirche": ("Wehrkirche", wehrkirche),
    "rundturmkastell": ("Rundturm-Kastell", rundturmkastell),
    "sechseckfestung": ("Sechseckfestung", sechseckfestung),
    "vorburg": ("Vorburg", vorburg),
    "holzburg": ("Nordische Holzburg", holzburg),
    "bastionsturm": ("Bastionsturm am Meer", bastionsturm),
    "pechnasenwehrgang": ("Wehrgang mit Pechnasen", pechnasenwehrgang),
    "felsenburg": ("Felsenburg", felsenburg),
    "barockschloss": ("Barockschloss", barockschloss),
    "grafenburg": ("Grafenburg", grafenburg),
    "zaubererburg": ("Zaubererburg", zaubererburg),
    "roemisches_kastell": ("Römisches Kastell", roemisches_kastell),
}

"""Piraten II – zwanzig weitere Piratenszenen: Lagunenversteck, Strandräuber-Leuchtfeuer, Pulvermagazin,
Piratenwerft, Kompassfelsen, Strandbar, Wrack-Sandbank, Stelzen-Ausguck, Freibeuterdorf, Höhlenhafen, Geisterbucht,
Wrackriff, Hängebrücken-Inseln, Schatzberg, Kielholdock, Meerjungfrauenfelsen, Vulkanversteck, Schmugglerturm,
Kanonenboot und Flaschenpost-Strand. Wasserlinie y = 0."""

from __future__ import annotations

import math

import numpy as np

import wald2
from boote import piratenschiff, ruderboot
from feinbau import Dachmat, Mix, fachwerk, fenster, kegeldach, kram, laterne, mauer, platte, satteldach, stamm, \
    treppe, tuer, zaun
from himmelsstadt2 import eckturm, haus
from lib import Welt, einfuegen
from piraten import _insel, einfuegen_gedreht

S = [0.6, 1.0, 1.6, 2.5]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def meer(w, R, tiefe=3):
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                for y in range(-tiefe + 1, 1):
                    if (x, y, z) not in w.bloecke:
                        w.setze(x, y, z, w.b("water", level=0))
                if (x, -tiefe, z) not in w.bloecke:
                    w.setze(x, -tiefe, z, w.b("sand"))


def palmen(w, hoehen, n, seed, abstand=5):
    rng = w.rng
    kand = [(p, h) for p, h in hoehen.items() if h >= 1]
    rng.shuffle(kand)
    gesetzt = []
    for (x, z), h in kand:
        if len(gesetzt) >= n:
            break
        if any(math.hypot(x - a, z - b) < abstand for a, b in gesetzt) or not w.frei(x, h + 1, z):
            continue
        einfuegen(w, wald2.palme(seed + x * 13 + z), x, h, z)
        gesetzt.append((x, z))


def huette(w, cx, cz, y, B=5, T=4, dach=("spruce", "dark_oak")):
    x0, z0, x1, z1 = cx - B // 2, cz - T // 2, cx - B // 2 + B - 1, cz - T // 2 + T - 1
    for (x, z) in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
        for yy in range(y - 2, y + 3):
            w.setze(x, yy, z, stamm(w, "spruce", geschaelt=False))
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, y - 1, z, w.b("spruce_planks"))
    mauer(w, x0, z0, x1, z1, y, y + 2, M(w, [("spruce_planks", 2), ("stripped_spruce_log", 1), ("oak_planks", 1)]))
    tuer(w, cx, y, z1, "south", holz="spruce", laternen=False)
    fenster(w, x1, y + 1, cz, "east", holz="spruce", hoehe=1, blumen=0)
    satteldach(w, x0, z0, x1, z1, y + 3, Dachmat(w, list(dach)), first_x=True, ue=1, traufe="spruce")


def flagge(w, x, y, z, H=6):
    for yy in range(y, y + H):
        w.setze(x, yy, z, zaun(w, "dark_oak"))
    for dx in range(1, 4):
        for dy in range(0, 2):
            w.setze(x + dx, y + H - 1 - dy, z, w.b("black_wool" if (dx + dy) % 3 else "white_wool"))


def schiff(w, seed, g, x, z, dreh=0.0, kipp=0.0, y=0):
    s = piratenschiff(seed, max(0, g - 1))
    if not dreh and not kipp:
        einfuegen(w, s, x, y, z)
        return
    cd, sd = math.cos(dreh), math.sin(dreh)
    ck, sk = math.cos(kipp), math.sin(kipp)
    Ry = np.array([[cd, 0, -sd], [0, 1, 0], [sd, 0, cd]])
    Rx = np.array([[1, 0, 0], [0, ck, -sk], [0, sk, ck]])
    einfuegen_gedreht(w, s, Ry @ Rx, (x, y, z))


def fels(w, cx, cz, r, h, mats=("stone", "andesite", "tuff", "mossy_cobblestone")):
    rng = w.rng
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            d = math.hypot(x - cx, z - cz) / r
            if d <= 1:
                top = int(h * (1 - d ** 2) ** 0.6 + rng.random())
                for y in range(-3, top + 1):
                    w.setze(x, y, z, w.b(mats[int(rng.random() * len(mats))]))


# ============================================================================ Szenen

def lagunenversteck(seed, g=2):
    """Lagunenversteck: hinter einem Ring aus Felsen und Palmen liegt eine türkise Lagune, in der ein Piratenschiff
    vor Anker liegt, ein schmaler Durchlass führt ins offene Meer."""
    w = _welt(seed)
    s = S[g]
    R = int(18 * s + 10)
    hoehen = {}
    for x in range(-R - 3, R + 4):
        for z in range(-R - 3, R + 4):
            d = math.hypot(x, z)
            a = math.atan2(z, x)
            if R * 0.65 < d <= R and not (abs(a) < 0.18):
                h = int(2 + 4 * s * math.sin(math.pi * (d - R * 0.65) / (R * 0.35)))
                for y in range(-3, h + 1):
                    w.setze(x, y, z, w.b("sand" if y == h and d > R * 0.8 else "stone" if y > 0 else "sandstone"))
                hoehen[(x, z)] = h
    meer(w, R + 3)
    for (x, z), h in list(hoehen.items()):
        if w.P.name(w.bloecke.get((x, h, z), 0)) == "minecraft:sand" and w.rng.random() < 0.4:
            w.setze(x, h, z, w.b("grass_block", snowy=False))
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) < R * 0.6:
                w.setze(x, -3, z, w.b("light_blue_terracotta" if (x + z) % 3 else "sand"))
    schiff(w, seed, g, 0, 0)
    palmen(w, hoehen, 4 + g * 3, seed)
    return w


def strandraeuberfeuer(seed, g=1):
    """Strandräuber-Leuchtfeuer: auf einer Felsnase brennt ein falsches Leuchtfeuer, das Schiffe auf die Klippen
    lockt, darunter liegt ein frisches Wrack, die Räuberhütte versteckt sich in den Felsen."""
    w = _welt(seed)
    s = S[g]
    R = int(12 * s + 6)
    meer(w, int(R * 1.6))
    fels(w, 0, 0, R, 8 * s + 4)
    y = max(h for (x, yy, z) in w.bloecke for h in [yy] if abs(x) <= 1 and abs(z) <= 1 and
            w.P.name(w.bloecke[(x, yy, z)]) != "minecraft:water")
    ht = int(8 * s + 4)
    for yy in range(y + 1, y + ht):
        for (dx, dz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            w.setze(dx, yy, dz, stamm(w, "spruce", geschaelt=False))
    y = y + ht - 5
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(dx, y + 5, dz, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                       waterlogged=False) if (dx or dz) else w.b("campfire", lit=True,
                                                                               signal_fire=True, facing="north",
                                                                               waterlogged=False))
    huette(w, -int(R * 0.4), int(R * 0.3), int(3 * s) + 2)
    schiff(w, seed, max(1, g), int(R * 1.1), int(R * 0.3), dreh=0.4, kipp=0.35, y=-2)
    return w


def pulvermagazin(seed, g=1):
    """Pulvermagazin: ein gedrungener, bombensicherer Steinbau mit gewölbtem Dach und eisenbeschlagener Tür auf einer
    kleinen Insel, umgeben von Kanonenkugel-Pyramiden, Pulverfässern und Wachen-Laternen."""
    w = _welt(seed)
    s = S[g]
    R = int(10 * s + 6)
    hoehen = _insel(w, R, hoehe=int(2 + s))
    meer(w, R + 4)
    st = M(w, [("stone_bricks", 3), ("cobblestone", 1), ("mossy_stone_bricks", 1)])
    B, T = int(4 * s + 3), int(3 * s + 2)
    y = max(hoehen.get((0, 0), 1), 1) + 1
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            for yy in range(y, y + 3):
                if abs(x) == B or abs(z) == T:
                    w.setze(x, yy, z, st(x, yy, z))
            h = int(math.sqrt(max(0, T * T - z * z)) * 0.8)
            for yy in range(y + 3, y + 3 + h + 1):
                if yy == y + 3 + h or abs(x) == B:
                    w.setze(x, yy, z, w.b("cobbled_deepslate"))
    tuer(w, 0, y, T, "south", holz="dark_oak")
    for (cx, cz) in ((B + 3, 2), (-B - 3, -1)):
        hy = hoehen.get((cx, cz), 1)
        for k in range(3):
            for dx in range(-2 + k, 3 - k):
                for dz in range(-2 + k, 3 - k):
                    w.setze(cx + dx, hy + 1 + k, cz + dz, w.b("black_concrete"))
    kram(w, -B + 1, y, T + 3, 6)
    return w


def piratenwerft(seed, g=2):
    """Piratenwerft: an einem Strand liegt auf einer schrägen Helling ein halb fertiges Schiff – nur Kiel und Spanten,
    daneben Holzstapel, ein Kran, eine Teersiederei und die Werkstatthütte."""
    w = _welt(seed)
    s = S[g]
    R = int(16 * s + 8)
    hoehen = _insel(w, R, hoehe=int(2 + s), sand_breite=6)
    meer(w, R + 6)
    L = int(20 * s + 6)
    H = int(4 * s + 2)
    for i in range(L):
        x = -L // 2 + i
        y = 1 + int((L - i) * 0.12)
        w.setze(x, y, 0, w.b("dark_oak_log", axis="x"))
        if i % 3 == 0 and 2 < i < L - 2:
            t = i / L
            b = int((3 * s + 1.5) * math.sin(math.pi * t) + 1)
            for z in range(-b, b + 1):
                hh = int(H * (abs(z) / max(b, 1)) ** 1.5)
                w.setze(x, y + hh, z, w.b("stripped_dark_oak_log", axis="y"))
            for k in range(1, H + 1):
                w.setze(x, y + k, b, w.b("stripped_dark_oak_log", axis="y"))
                w.setze(x, y + k, -b, w.b("stripped_dark_oak_log", axis="y"))
    for k in range(int(6 * s)):
        w.setze(-int(R * 0.5) + k % 3, 2 + k // 3, int(R * 0.5), w.b("spruce_log", axis="x"))
    huette(w, int(R * 0.4), -int(R * 0.5), 3)
    w.setze(-int(R * 0.3), 2, -int(R * 0.4), w.b("cauldron"))
    w.setze(-int(R * 0.3), 1, -int(R * 0.4), w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                 waterlogged=False))
    palmen(w, hoehen, 3 + g, seed)
    return w


def kompassfelsen(seed, g=1):
    """Kompassfelsen: eine flache Felsinsel, in deren Oberfläche eine riesige Windrose aus hellem und dunklem
    Stein eingelegt ist, ein großes rotes X markiert den Schatz, ein Fernrohr-Gestell steht am Rand."""
    w = _welt(seed)
    s = S[g]
    R = int(12 * s + 6)
    meer(w, R + 5)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d <= R:
                for y in range(-3, 2):
                    w.setze(x, y, z, w.b("stone"))
                a = math.atan2(z, x)
                spitze = max(0, math.cos(a * 4)) ** 6
                stern = d < R * 0.85 * (0.3 + 0.7 * spitze) or d < R * 0.25
                ring = abs(d - R * 0.88) < 0.7
                w.setze(x, 1, z, w.b("calcite" if stern and (x > 0) == (z > 0) else "deepslate_tiles" if stern else
                                     "gold_block" if ring else "andesite"))
    for k in range(-2, 3):
        w.setze(k, 2, k, w.b("red_concrete"))
        w.setze(k, 2, -k, w.b("red_concrete"))
    x, z = R - 2, 0
    for y in range(2, 4):
        w.setze(x, y, z, w.b("dark_oak_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(x, 4, z, w.b("waxed_cut_copper"))
    w.setze(x - 1, 5, z, w.b("waxed_cut_copper"))
    return w


def strandbar(seed, g=1):
    """Strandbar: eine Bambushütte mit Palmblattdach und Theke am Sandstrand, Hocker, Rumfässer, Lampions an
    Schnüren, Hängematten zwischen Palmen und ein kleiner Steg."""
    w = _welt(seed)
    s = S[g]
    R = int(12 * s + 6)
    hoehen = _insel(w, R, hoehe=2, sand_breite=R)
    meer(w, R + 5)
    y = 2
    B = int(3 * s + 2)
    for (x, z) in ((-B, -B), (B, -B), (-B, B), (B, B)):
        for yy in range(y, y + 4):
            w.setze(x, yy, z, w.b("bamboo_block", axis="y"))
    for x in range(-B - 1, B + 2):
        for z in range(-B - 1, B + 2):
            w.setze(x, y + 4, z, w.b("hay_block", axis="y") if (x + z) % 2 else w.b("dark_oak_leaves",
                                                                                   persistent=True, distance=1,
                                                                                   waterlogged=False))
    for x in range(-B + 1, B):
        w.setze(x, y, B - 1, w.b("bamboo_planks"))
        w.setze(x, y + 1, B - 1, w.b("bamboo_slab", type="bottom", waterlogged=False))
        w.setze(x, y, B + 1, w.b("bamboo_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False)) if x % 2 == 0 else None
    for x in range(-B + 1, B, 2):
        w.setze(x, y, -B + 1, w.b("barrel", facing="up", open=False))
    farben = ["red_stained_glass", "orange_stained_glass", "yellow_stained_glass", "lime_stained_glass"]
    for k in range(-B - 4, B + 5):
        w.setze(k, y + 5 if abs(k) <= B + 1 else y + 4, B + 3, w.b(farben[abs(k) % 4]) if k % 2 else
                w.b("chain", axis="x", waterlogged=False), False)
    for x in range(R - 3, R + 5):
        for z in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
    palmen(w, hoehen, 3 + g, seed, abstand=6)
    return w


def wracksandbank(seed, g=1):
    """Wrack-Sandbank: eine flache Sandbank mitten im Meer, auf der die Trümmer eines Schiffs verstreut liegen –
    ein gebrochener Mast, Spanten, Kisten, Fässer und eine Möwenkolonie aus Federn."""
    w = _welt(seed)
    s = S[g]
    R = int(12 * s + 5)
    meer(w, int(R * 1.5))
    rng = w.rng
    for x in range(-R, R + 1):
        for z in range(-int(R * 0.5), int(R * 0.5) + 1):
            if (x / R) ** 2 + (z / (R * 0.5)) ** 2 <= 1:
                for y in range(-3, 1):
                    w.setze(x, y, z, w.b("sand"))
    for i in range(int(10 * s) + 4):
        w.setze(-i, 1 + i // 4, int(i * 0.3), w.b("spruce_log", axis="x"))
    for k in range(4):
        x = int(R * 0.3) + k * 2
        for h in range(1, 4 - k // 2):
            w.setze(x, h, 2, w.b("stripped_dark_oak_log", axis="y"))
            w.setze(x, h, -2, w.b("stripped_dark_oak_log", axis="y"))
    for k in range(int(6 * s) + 3):
        x, z = int((rng.random() - 0.5) * R * 1.6), int((rng.random() - 0.5) * R * 0.8)
        if (x / R) ** 2 + (z / (R * 0.5)) ** 2 <= 0.9:
            w.setze(x, 1, z, w.b(["barrel", "chest", "spruce_planks", "white_wool"][int(rng.random() * 4)],
                                 **({"facing": "up", "open": False} if rng.random() < 0 else {})) if False else
                    w.b("barrel", facing="up", open=False) if rng.random() < 0.5 else w.b("spruce_slab", type="bottom",
                                                                                         waterlogged=False))
    return w


def stelzenausguck(seed, g=1):
    """Stelzen-Ausguck: eine Wachhütte auf hohen Holzstelzen im flachen Wasser einer Bucht, mit Leiter, Glocke,
    Fernrohr und Piratenflagge, ein Ruderboot ist angebunden."""
    w = _welt(seed)
    s = S[g]
    meer(w, int(10 * s + 6), tiefe=2)
    for x in range(-int(10 * s + 6), int(10 * s + 7)):
        for z in range(-int(10 * s + 6), int(10 * s + 7)):
            if math.hypot(x, z) <= 10 * s + 6:
                w.setze(x, -2, z, w.b("sand"))
    H = int(8 * s + 6)
    huette(w, 0, 0, H, 5, 5)
    for yy in range(-1, H - 1):
        w.setze(0, yy, 3, w.b("ladder", facing="south", waterlogged=False))
    w.setze(2, H + 1, 2, w.b("bell", attachment="floor", facing="north", powered=False), False)
    flagge(w, -2, H + 5, -2, 4)
    einfuegen(w, ruderboot(seed, 0), 4, 0, 4)
    return w


def freibeuterdorf(seed, g=2):
    """Freibeuterdorf: ein buntes Fischerdorf in einer Bucht – Holzhäuser mit Fachwerk, Netze, Räucherhütte,
    Bootsstege, Fässer und Ruderboote, Palmen und ein Glockenturm."""
    w = _welt(seed)
    s = S[g]
    R = int(16 * s + 8)
    hoehen = _insel(w, R, hoehe=int(3 + s), sand_breite=4)
    meer(w, R + 6)
    n = 3 + g
    stile = ["fachwerk", "terrakotta", "blau", "kupfer"]
    for k in range(n):
        a = k / n * 6.283 + 0.3
        cx, cz = round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)
        y = max(1, max(hoehen.get((cx + dx, cz + dz), 1) for dx in (-3, 0, 3) for dz in (-3, 0, 3))) + 1
        haus(w, cx, cz, 6, 5, y, stile[k % 4], geschosse=1 + (k % 2), tuer_s="south", schorn=k % 2 == 0)
    for k in range(2):
        a = k * 3.14 + 1.6
        x0, z0 = round(math.cos(a) * R * 0.9), round(math.sin(a) * R * 0.9)
        for i in range(int(6 * s) + 3):
            x, z = round(x0 + math.cos(a) * i), round(z0 + math.sin(a) * i)
            for q in (-1, 0, 1):
                w.setze(x + (q if abs(math.sin(a)) > 0.5 else 0), 1, z + (q if abs(math.cos(a)) > 0.5 else 0),
                        w.b("spruce_planks"))
        einfuegen(w, ruderboot(seed + k, 0), x0 + round(math.cos(a) * (6 * s + 4)) + 2, 0,
                  z0 + round(math.sin(a) * (6 * s + 4)))
    palmen(w, hoehen, 3 + g, seed)
    return w


def hoehlenhafen(seed, g=2):
    """Höhlenhafen: ein gewaltiger Meeresfelsen mit einer gewölbten Grotte, in die das Wasser hineinreicht – darin
    liegt ein Piratenschiff an einem Holzkai mit Laternen und Lagerkisten."""
    w = _welt(seed)
    s = S[g]
    R = int(18 * s + 8)
    meer(w, int(R * 1.4))
    fels(w, 0, 0, R, 12 * s + 6)
    hr = 7 * s + 3
    for z in range(-int(R * 0.6), R + 3):
        for y in range(-2, int(hr * 1.2) + 1):
            for x in range(-int(hr) - 1, int(hr) + 2):
                if (y / (hr * 1.2)) ** 2 + (x / hr) ** 2 <= 1:
                    p = (x, y, z)
                    if y <= 0:
                        w.setze(*p, w.b("water", level=0))
                    else:
                        w.bloecke.pop(p, None)
    for z in range(-int(R * 0.4), int(R * 0.6)):
        for x in range(int(hr) - 3, int(hr) + 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
        if z % 5 == 0:
            w.setze(int(hr) - 3, 2, z, w.b("lantern", hanging=False, waterlogged=False))
    kram(w, int(hr) - 1, 2, int(R * 0.3), 6)
    schiff(w, seed, g, -1, int(R * 0.1), dreh=math.pi / 2)
    return w


def geisterbucht(seed, g=2):
    """Geisterbucht: in einer nebligen, dunklen Bucht liegt ein bleiches, zerfetztes Geisterschiff, Seelenlaternen
    flackern türkis, Knochen am Strand und tote Bäume auf den Felsen."""
    w = _welt(seed)
    s = S[g]
    R = int(16 * s + 8)
    hoehen = _insel(w, R, hoehe=int(3 + s), sand_breite=3, gras=False)
    meer(w, R + 8)
    for (x, z), h in hoehen.items():
        if h > 0 and w.rng.random() < 0.5:
            w.setze(x, h, z, w.b(["soul_sand", "gravel", "coarse_dirt"][int(w.rng.random() * 3)]))
    from boote import geisterschiff
    einfuegen(w, geisterschiff(seed, max(0, g - 1)), R + 2, 0, 0)
    rng = w.rng
    for k in range(int(8 * s) + 4):
        (x, z), h = list(hoehen.items())[int(rng.random() * len(hoehen))]
        if h >= 1 and w.frei(x, h + 1, z):
            w.setze(x, h + 1, z, w.b("soul_lantern", hanging=False, waterlogged=False) if rng.random() < 0.4 else
                    w.b("bone_block", axis="x"))
    for k in range(2 + g):
        (x, z), h = list(hoehen.items())[int(rng.random() * len(hoehen))]
        if h >= 1:
            einfuegen(w, wald2.totholz(seed + k, "dark_oak"), x, h, z)
    return w


def wrackriff(seed, g=3):
    """Wrackriff: ein tückisches Korallenriff knapp unter der Oberfläche, an dem gleich drei Schiffe zerschellt
    sind – eines gekentert, eines gebrochen, eines halb versunken."""
    w = _welt(seed)
    s = S[g]
    R = int(22 * s + 10)
    meer(w, R, tiefe=4)
    rng = w.rng
    kor = ["brain_coral_block", "tube_coral_block", "fire_coral_block", "horn_coral_block", "bubble_coral_block"]
    for k in range(int(30 * s)):
        a = rng.random() * 6.283
        d = rng.random() * R * 0.8
        cx, cz = math.cos(a) * d, math.sin(a) * d
        r = 1 + rng.random() * 2.5 * s
        for x in range(int(cx - r), int(cx + r) + 1):
            for z in range(int(cz - r), int(cz + r) + 1):
                if math.hypot(x - cx, z - cz) <= r:
                    for y in range(-4, -1 + int(rng.random() * 2)):
                        w.setze(x, y, z, w.b(kor[int(rng.random() * 5)]))
    for k, (dreh, kipp, y) in enumerate(((0.3, 1.2, -2), (2.2, 0.4, -3), (4.0, 0.15, -4))):
        a = k * 2.1
        schiff(w, seed + k, max(1, g - 1), int(math.cos(a) * R * 0.45), int(math.sin(a) * R * 0.45), dreh, kipp, y)
    return w


def haengebrueckeninseln(seed, g=2):
    """Hängebrücken-Inseln: drei kleine Felsinseln mit Palmen und Piratenhütten, verbunden durch schwankende
    Seilbrücken, auf der größten flattert die Flagge."""
    from himmelsstadt import haengebruecke_teil
    w = _welt(seed)
    s = S[g]
    R = int(8 * s + 4)
    meer(w, int(R * 3.4))
    pos = [(-int(R * 1.8), 0), (int(R * 0.6), -int(R * 1.2)), (int(R * 1.6), int(R * 1.3))]
    alle = {}
    for k, (cx, cz) in enumerate(pos):
        r = R * (1.1 if k == 0 else 0.8)
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for z in range(int(cz - r) - 1, int(cz + r) + 2):
                d = math.hypot(x - cx, z - cz) / r
                if d <= 1:
                    h = int(4 * s * (1 - d ** 2) + 2)
                    for y in range(-3, h + 1):
                        w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h and d < 0.7 else
                                w.b("sand") if y == h else w.b("stone"))
                    alle[(x, z)] = h
        y = int(4 * s + 2) + 1
        huette(w, cx, cz, y, 5, 4)
    flagge(w, pos[0][0] + 3, int(4 * s + 3), pos[0][1] - 3, 6)
    for (a, b) in ((pos[0], pos[1]), (pos[1], pos[2])):
        n = int(math.dist(a, b) * 1.5)
        for i in range(n + 1):
            t = i / n
            x = a[0] + (b[0] - a[0]) * t
            z = a[1] + (b[1] - a[1]) * t
            y = int(4 * s + 2) - 2 * math.sin(math.pi * t)
            w.setze(round(x), round(y), round(z), w.b("spruce_slab", type="bottom", waterlogged=False), False)
    palmen(w, alle, 4 + g, seed, abstand=4)
    return w


def schatzberg(seed, g=1):
    """Schatzberg: auf einem Felsen im Meer türmt sich ein Berg aus Gold, Truhen, Juwelen und Kronen, bewacht von
    zwei Kanonen und einer zerfetzten Flagge."""
    w = _welt(seed)
    s = S[g]
    R = int(9 * s + 5)
    meer(w, R + 6)
    fels(w, 0, 0, R, 3 * s + 2)
    rng = w.rng
    y0 = int(3 * s + 2)
    Rg = R * 0.55
    for x in range(-int(Rg) - 1, int(Rg) + 2):
        for z in range(-int(Rg) - 1, int(Rg) + 2):
            d = math.hypot(x, z) / Rg
            if d <= 1:
                h = int((1 - d ** 2) * 4 * s + 1)
                for y in range(y0, y0 + h + 1):
                    w.setze(x, y, z, w.b(["gold_block", "raw_gold_block", "gold_block", "yellow_concrete"]
                                         [int(rng.random() * 4)]))
                if rng.random() < 0.12:
                    w.setze(x, y0 + h + 1, z, w.b(["chest", "emerald_block", "diamond_block", "amethyst_cluster"]
                                                  [int(rng.random() * 4)],
                                                  **({"facing": "north", "type": "single", "waterlogged": False}
                                                     if False else {})) if rng.random() < 0.5 else
                            w.b("chest", facing="south", type="single", waterlogged=False))
    for sx in (-1, 1):
        x = sx * int(R * 0.8)
        w.setze(x, y0 + 1, 0, w.b("polished_blackstone"))
        w.setze(x - sx, y0 + 1, 0, w.b("polished_blackstone"))
        w.setze(x, y0 + 1, 1, w.b("dark_oak_planks"))
    flagge(w, 0, y0 + int(4 * s) + 2, 0, 5)
    return w


def kielholdock(seed, g=2):
    """Kielholdock: am Strand liegt ein Piratenschiff auf der Seite gekippt zur Reparatur, Gerüste und Leitern am
    Rumpf, Teerkessel, Planken und ein Flaschenzug an einer Palme."""
    w = _welt(seed)
    s = S[g]
    R = int(18 * s + 8)
    hoehen = _insel(w, R, hoehe=2, sand_breite=R)
    meer(w, R + 6)
    schiff(w, seed, g, 0, 0, dreh=0.0, kipp=0.55, y=1)
    for x in range(-int(8 * s), int(8 * s) + 1, 3):
        for y in range(1, int(5 * s) + 2):
            w.setze(x, y, -int(6 * s) - 2, w.b("scaffolding", bottom=False, distance=0, waterlogged=False), False)
    w.setze(int(R * 0.5), 2, int(R * 0.4), w.b("cauldron"))
    w.setze(int(R * 0.5), 1, int(R * 0.4), w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                waterlogged=False))
    palmen(w, hoehen, 3 + g, seed, abstand=7)
    return w


def meerjungfrauenfelsen(seed, g=2):
    """Meerjungfrauenfelsen: ein einsamer Felsen im Meer, auf dem eine Statue einer Meerjungfrau mit langem Haar
    und schimmerndem Fischschwanz sitzt, Muscheln, Perlen und Seetang ringsum."""
    from skulptur import Skulptur, ell, kap
    w = _welt(seed)
    s = S[g]
    R = int(8 * s + 4)
    meer(w, R + 8)
    fels(w, 0, 0, R, 3 * s + 2)
    y0 = int(3 * s + 2)
    S_ = Skulptur(w, s)
    S_.mat("h", w.b("calcite"))
    S_.mat("f", w.b("prismarine"))
    S_.mat("x", w.b("dark_prismarine"))
    S_.mat("a", w.b("gold_block"))
    S_.plus(kap((0, 0.8, -1.5), (3.4, 0.6, 1.0), 1.4, 0.8), "f")
    S_.plus(kap((3.4, 0.6, 1.0), (5.2, 1.6, 2.6), 0.8, 0.3), "f")
    S_.plus(ell(5.6, 2.4, 3.0, 1.2, 0.5, 0.9), "x")
    S_.plus(kap((0, 1.5, -1.5), (0, 5.5, -1.2), 1.3, 1.1), "h")
    S_.plus(ell(0, 6.8, -1.0, 1.0, 1.2, 1.0), "h")
    S_.plus(kap((0, 7.4, -1.6), (0, 3.6, -2.8), 0.9, 0.6), "a")
    S_.plus(kap((1.0, 5.0, -1.2), (2.4, 3.6, 0.2), 0.45), "h")
    S_.plus(kap((-1.0, 5.0, -1.2), (-1.8, 7.4, -0.4), 0.45), "h")
    S_.rendern((-4, 0, -5), (7, 9, 5), versatz=(0.5, y0, 0.5))
    rng = w.rng
    for k in range(int(12 * s)):
        a = rng.random() * 6.283
        d = R + 1 + rng.random() * 4
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        for y in range(-2, -2 + int(rng.random() * 3) + 1):
            w.setze(x, y, z, w.b("kelp_plant") if y < 0 else w.b("kelp", age=20))
    return w


def vulkanversteck(seed, g=2):
    """Vulkanversteck: eine kleine Vulkaninsel mit rauchendem Krater, an ihrem Fuß haben Piraten eine Festung aus
    schwarzem Basalt mit Hafen und Kanonen in den Fels gebaut."""
    w = _welt(seed)
    s = S[g]
    R = int(16 * s + 8)
    meer(w, R + 6)
    rng = w.rng
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z) / R
            if d <= 1:
                h = int((22 * s + 6) * (1 - d) ** 1.3)
                if d < 0.15:
                    h = int((22 * s + 6) * 0.72)
                for y in range(-3, h + 1):
                    w.setze(x, y, z, w.b(["basalt", "blackstone", "tuff", "smooth_basalt"][int(rng.random() * 4)])
                            if not (d < 0.12 and y == h) else w.b("lava", level=0))
    for k in range(3):
        w.setze(int(rng.integers(-2, 3)), int((22 * s + 6) * 0.72) + 1, int(rng.integers(-2, 3)),
                w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    st = M(w, [("polished_blackstone_bricks", 3), ("blackstone", 1)])
    cx = int(R * 0.75)
    for x in range(cx - 4, cx + 5):
        for z in range(-4, 5):
            for y in range(1, 5):
                if abs(x - cx) == 4 or abs(z) == 4:
                    w.setze(x, y, z, st(x, y, z))
                else:
                    w.bloecke.pop((x, y, z), None)
            w.setze(x, 0, z, w.b("polished_blackstone"))
    for z in (-4, 4):
        w.setze(cx + 4, 3, z, w.b("black_concrete"))
    flagge(w, cx, 5, 0, 5)
    return w


def schmugglerturm(seed, g=2):
    """Schmugglerturm: ein alter Steinturm auf einer Klippe mit Holzkran, an dem Kisten zu einem Boot herabgelassen
    werden, geheime Treppe im Fels, Laternen als Signal."""
    w = _welt(seed)
    s = S[g]
    R = int(12 * s + 6)
    meer(w, int(R * 1.6))
    fels(w, 0, 0, R, 8 * s + 4)
    y = int(8 * s + 4) - 1
    st = M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 1), ("cracked_stone_bricks", 1)])
    eckturm(w, 0, 0, y, 2, int(8 * s + 4), st, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]), form="kegel")
    yk = y + int(8 * s + 4) - 2
    for i in range(int(R * 0.8)):
        w.setze(3 + i, yk, 0, w.b("spruce_log", axis="x"))
    xe = 3 + int(R * 0.8)
    for yy in range(2, yk):
        w.setze(xe, yy, 0, w.b("chain", axis="y", waterlogged=False))
    w.setze(xe, 1, 0, w.b("barrel", facing="up", open=False))
    einfuegen(w, ruderboot(seed, 0), xe, 0, 3)
    for k in range(y):
        w.setze(-R + 1 + k // 2, k, -2, treppe(w, "stone_brick", "east"), False)
    return w


def kanonenboot(seed, g=1):
    """Kanonenboot: ein kleines, wendiges Piratenschiff mit einer großen Bugkanone, Lateinersegel mit Totenkopf und
    Pulverfässern an Deck, vor einer winzigen Felsinsel."""
    w = _welt(seed)
    s = S[g]
    meer(w, int(14 * s + 6))
    fels(w, -int(9 * s + 3), 0, 3 * s + 2, 3 * s + 1)
    from boote import _dh, _holz, rumpf2
    from schiffe import dreieckssegel, mast
    u = s * 0.8
    mat = _holz(w, "dark_oak", wand=["black_terracotta", "dark_oak_planks", "black_concrete"], streifen="red_concrete",
                deck="spruce")
    L, B, D, F = 16 * u + 6, 3 * u + 1.2, 1.6 * u + 1, 2 * u + 1
    r = rumpf2(w, L, B, D, F, mat)
    yb = _dh(r, 0) + 1
    mast(w, 0, yb - 1, int(12 * u) + 1, False)
    dreieckssegel(w, (int(L * 0.25), yb + int(12 * u)), (-int(L * 0.3), yb + 2), (1, yb + 1), 0, w.b("black_wool"))
    xb = int(L * 0.35)
    for k in range(int(3 * u) + 1):
        w.setze(xb + k, _dh(r, xb) + 1, 0, w.b("polished_blackstone"))
    w.setze(xb - 1, _dh(r, xb) + 1, 1, w.b("barrel", facing="up", open=False))
    return w


def flaschenpoststrand(seed, g=0):
    """Flaschenpost-Strand: eine winzige Insel mit einer einzelnen Palme, einer Hängematte, einem SOS aus Steinen im
    Sand, einer angespülten Riesen-Flaschenpost und einem Feuer."""
    w = _welt(seed)
    s = S[g]
    R = int(7 * s + 4)
    hoehen = _insel(w, R, hoehe=2, sand_breite=R)
    meer(w, R + 6)
    palmen(w, hoehen, 1, seed)
    for i, ch in enumerate(["S", "O", "S"]):
        x0 = -4 + i * 3
        muster = {"S": [(0, 0), (1, 0), (0, 1), (1, 2), (0, 3), (1, 3)], "O": [(0, 0), (1, 0), (0, 1), (1, 1),
                                                                             (0, 2), (1, 2), (0, 3), (1, 3)]}[ch]
        for (dx, dz) in muster:
            w.setze(x0 + dx, hoehen.get((x0 + dx, dz), 1) + 1, dz + 2, w.b("cobblestone_slab", type="bottom",
                                                                           waterlogged=False))
    for i in range(int(4 * s) + 3):
        w.setze(R - 1 + i, 1, -2, w.b("lime_stained_glass" if i < int(4 * s) + 1 else "oak_planks"))
    w.setze(-2, hoehen.get((-2, -2), 1) + 1, -2, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                     waterlogged=False))
    return w


PIRATEN3 = {
    "lagunenversteck": ("Lagunenversteck", lagunenversteck),
    "strandraeuberfeuer": ("Strandräuber-Leuchtfeuer", strandraeuberfeuer),
    "pulvermagazin": ("Pulvermagazin", pulvermagazin),
    "piratenwerft": ("Piratenwerft", piratenwerft),
    "kompassfelsen": ("Kompassfelsen", kompassfelsen),
    "strandbar": ("Strandbar", strandbar),
    "wracksandbank": ("Wrack-Sandbank", wracksandbank),
    "stelzenausguck": ("Stelzen-Ausguck", stelzenausguck),
    "freibeuterdorf": ("Freibeuterdorf", freibeuterdorf),
    "hoehlenhafen": ("Höhlenhafen", hoehlenhafen),
    "geisterbucht": ("Geisterbucht", geisterbucht),
    "wrackriff": ("Wrackriff", wrackriff),
    "haengebrueckeninseln": ("Hängebrücken-Inseln", haengebrueckeninseln),
    "schatzberg": ("Schatzberg", schatzberg),
    "kielholdock": ("Kielholdock", kielholdock),
    "meerjungfrauenfelsen": ("Meerjungfrauenfelsen", meerjungfrauenfelsen),
    "vulkanversteck": ("Vulkanversteck", vulkanversteck),
    "schmugglerturm": ("Schmugglerturm", schmugglerturm),
    "kanonenboot": ("Kanonenboot", kanonenboot),
    "flaschenpoststrand": ("Flaschenpost-Strand", flaschenpoststrand),
}

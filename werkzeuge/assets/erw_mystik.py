"""Mystik II – zwanzig weitere magische Orte: Mondsichel-Portal, Schwebende Bibliothek, Riesensanduhr,
Seelenbaum, Spiegelsee, Planetenmodell, Runenbrücke, Elementarsäulen, Druidenhain, Zauberkreis, Schwebender Thron,
Alchemistenlabor, Traumfänger, Himmelsleiter, Nebeltor, Seherkugel, Sonnenaltar, Erdgeist-Hügel, Mondphasen-Steine
und Gefrorene Zeit."""

from __future__ import annotations

import math

import numpy as np

import wald2
from feinbau import Dachmat, Mix, kegeldach, laterne, platte, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import einfuegen

S = [0.6, 1.0, 1.6, 2.5]


def M(w, liste, zelle=1.4, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def boden(w, R, art="moos"):
    rng = w.rng
    mats = {"moos": ["moss_block", "grass_block", "mossy_cobblestone", "grass_block"],
            "stein": ["stone", "andesite", "tuff", "mossy_cobblestone"],
            "dunkel": ["deepslate", "tuff", "moss_block", "cobbled_deepslate"]}[art]
    zellen = []
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            if math.hypot(x, z) <= R + rng.random():
                n = mats[int(rng.random() * len(mats))]
                w.setze(x, 0, z, w.b(n, snowy=False) if n == "grass_block" else w.b(n))
                w.setze(x, -1, z, w.b("dirt"))
                zellen.append((x, z))
                if n in ("moss_block", "grass_block") and rng.random() < 0.15:
                    w.setze(x, 1, z, w.b(["fern", "grass", "azure_bluet", "lily_of_the_valley"][int(rng.random() * 4)]))
    return zellen


def ring(w, cx, cy, cz, R, blk, achse="z", dicke=0.6):
    n = int(R * 14) + 8
    for k in range(n):
        a = k / n * 6.283
        for d in np.arange(-dicke, dicke + 0.01, 0.5):
            r = R + d
            if achse == "z":
                p = (round(cx + math.cos(a) * r), round(cy + math.sin(a) * r), cz)
            elif achse == "x":
                p = (cx, round(cy + math.sin(a) * r), round(cz + math.cos(a) * r))
            else:
                p = (round(cx + math.cos(a) * r), cy, round(cz + math.sin(a) * r))
            w.setze(*p, blk(*p) if callable(blk) else blk, False)


def obelisk(w, x, z, y0, H, mat="polished_blackstone", spitze="end_rod"):
    for y in range(y0, y0 + H):
        b = 1 if y < y0 + H * 0.8 else 0
        for dx in range(-b, b + 1):
            for dz in range(-b, b + 1):
                if abs(dx) + abs(dz) <= b:
                    w.setze(x + dx, y, z + dz, w.b(mat))
    w.setze(x, y0 + H, z, w.b(spitze, facing="up") if spitze == "end_rod" else w.b(spitze))


def glyphen(w, x0, x1, y, z, ach="x"):
    for i in range(x0, x1 + 1):
        if i % 2 == 0:
            p = (i, y, z) if ach == "x" else (z, y, i)
            w.setze(*p, w.b("crying_obsidian" if i % 4 == 0 else "amethyst_block"))


# ============================================================================ Orte

def mondsichelportal(seed, g=2):
    """Mondsichel-Portal: eine riesige, aufrecht stehende Mondsichel aus weißem Quarz mit Sternenstaub bildet ein
    Tor, zwischen ihren Spitzen schwebt ein leuchtender Stern, Stufen führen hinauf."""
    w = _neu(seed)
    s = S[g]
    boden(w, 10 * s + 4, "stein")
    R = 8 * s + 3
    yc = R + 2
    for x in range(-int(R) - 1, int(R) + 2):
        for y in range(-int(R) - 1, int(R) + 2):
            d1 = math.hypot(x, y)
            d2 = math.hypot(x - R * 0.45, y + R * 0.1)
            if d1 <= R and d2 > R * 0.85:
                for z in range(-int(1.2 * s), int(1.2 * s) + 1):
                    w.setze(x, round(yc + y), z, w.b("smooth_quartz" if (x * 3 + y) % 9 else "sea_lantern"))
    kugel(w, R * 0.55, yc + 1, 0, 1.2 * s + 0.6, w.b("pearlescent_froglight", axis="y"))
    for k in range(3):
        for x in range(-int(R * 0.6) - k, int(R * 0.6) + k + 1):
            for z in range(-3 - k, 4 + k):
                w.setze(x, 1 + 2 - k, z, w.b("quartz_bricks")) if k < 3 else None
    return w


def schwebende_bibliothek(seed, g=2):
    """Schwebende Bibliothek: um einen schlanken Turm aus Bücherregalen kreisen auf unsichtbaren Bahnen Bücherstapel,
    Lesepulte und Kerzen, eine Wendeltreppe aus schwebenden Stufen führt hinauf."""
    w = _neu(seed)
    s = S[g]
    boden(w, 9 * s + 4, "dunkel")
    H = int(14 * s + 6)
    r = int(1.5 * s + 1.5)
    for y in range(1, H):
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                d = math.hypot(x, z)
                if r - 0.8 < d <= r + 0.3:
                    w.setze(x, y, z, w.b("bookshelf") if y % 4 else w.b("dark_oak_planks"))
    kegeldach(w, 0, 0, H, r, Dachmat(w, ["mcw:purple_terracotta", "purpur", "deepslate_tile"]), form="nadel")
    rng = w.rng
    for k in range(int(12 * s) + 6):
        a = rng.random() * 6.283
        d = r + 3 + rng.random() * 5 * s
        y = 3 + rng.random() * (H - 4)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        for h in range(1 + int(rng.random() * 3)):
            w.setze(x, round(y) + h, z, w.b("bookshelf" if h < 2 else "lectern", **({} if h < 2 else
                                                                                   {"facing": "north",
                                                                                    "has_book": True,
                                                                                    "powered": False})))
        if rng.random() < 0.4:
            w.setze(x, round(y) - 1, z, w.b("candle", candles=3, lit=True, waterlogged=False), False)
    for i in range(H * 2):
        a = i * 0.45
        y = 1 + i // 2
        w.setze(round(math.cos(a) * (r + 2)), y, round(math.sin(a) * (r + 2)), w.b("dark_oak_slab", type="top",
                                                                                     waterlogged=False))
    return w


def sanduhr(seed, g=2):
    """Riesensanduhr: eine gewaltige Sanduhr aus Glas in einem goldenen Gestell mit gedrehten Säulen, oben rieselt
    der Sand durch die Engstelle in den unteren Kolben, umringt von Zahnrädern."""
    from riesenbogen import zahnrad
    w = _neu(seed)
    s = S[g]
    boden(w, 8 * s + 4, "stein")
    R = 4 * s + 2
    H = 10 * s + 4
    for x in range(-int(R) - 2, int(R) + 3):
        for z in range(-int(R) - 2, int(R) + 3):
            if max(abs(x), abs(z)) <= R + 1.5:
                w.setze(x, 1, z, w.b("gold_block"))
                w.setze(x, int(2 * H) + 3, z, w.b("gold_block"))
    for y in range(2, int(2 * H) + 3):
        t = abs(y - 2 - H) / H
        r = max(0.6, R * t ** 0.8)
        for x in range(-int(R) - 1, int(R) + 2):
            for z in range(-int(R) - 1, int(R) + 2):
                d = math.hypot(x, z)
                if r - 0.9 < d <= r + 0.3:
                    w.setze(x, y, z, w.b("glass"))
                elif d <= r - 0.9 and ((y < H * 0.7) or (y > H + 2 and y > 2 * H - H * 0.35)):
                    w.setze(x, y, z, w.b("sand"))
    for y in range(int(H * 0.7), int(H) + 2):
        w.setze(0, y, 0, w.b("sand"))
    for (x, z) in ((-int(R) - 1, -int(R) - 1), (int(R) + 1, -int(R) - 1), (-int(R) - 1, int(R) + 1),
                   (int(R) + 1, int(R) + 1)):
        for y in range(2, int(2 * H) + 3):
            w.setze(x, y, z, w.b("gold_block" if y % 3 else "dark_oak_log", **({} if y % 3 else {"axis": "y"})))
    zahnrad(w, int(R) + 4, int(H) // 2 + 3, 0, int(2 * s + 1), "xy", "gold_block", "polished_blackstone")
    return w


def seelenbaum(seed, g=2):
    """Seelenbaum: ein knorriger, bleicher Baum ohne Blätter, an dessen Zweigen hunderte Seelenlaternen hängen,
    türkises Seelenfeuer lodert zwischen den Wurzeln auf Seelensand."""
    w = _neu(seed)
    s = S[g]
    zl = boden(w, 9 * s + 4, "dunkel")
    from leuchtwald2 import baum_aeste
    enden = baum_aeste(w, 0, 0, 12 * s + 4, 6 + g, 7 * s + 2, "birch", 1.5 * s + 0.6, w.rng, steigung=0.4)
    rng = w.rng
    for (x, y, z) in enden:
        for k in range(2 + g):
            hx, hz = round(x + (rng.random() - 0.5) * 3), round(z + (rng.random() - 0.5) * 3)
            hy = round(y)
            for i in range(1 + int(rng.random() * 3)):
                if w.frei(hx, hy - i, hz):
                    w.setze(hx, hy - i, hz, w.b("chain", axis="y", waterlogged=False))
            hy2 = hy - 1 - int(rng.random() * 3)
            if w.frei(hx, hy2, hz):
                w.setze(hx, hy2, hz, w.b("soul_lantern", hanging=True, waterlogged=False))
    for k in range(int(10 * s) + 4):
        a = rng.random() * 6.283
        d = 2 + rng.random() * 5 * s
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if w.frei(x, 1, z):
            w.setze(x, 0, z, w.b("soul_sand"))
            w.setze(x, 1, z, w.b("soul_fire"))
    return w


def spiegelsee(seed, g=2):
    """Spiegelsee: ein vollkommen runder, stiller See, eingefasst von weißem Marmor, in der Mitte eine kleine Insel
    mit offenem Pavillon, Trittsteine führen hinüber, Kerzen schwimmen auf dem Wasser."""
    w = _neu(seed)
    s = S[g]
    R = 10 * s + 4
    for x in range(-int(R) - 3, int(R) + 4):
        for z in range(-int(R) - 3, int(R) + 4):
            d = math.hypot(x, z)
            if d <= R + 3:
                w.setze(x, -1, z, w.b("dirt"))
                w.setze(x, 0, z, w.b("grass_block", snowy=False) if d > R + 1 else w.b("smooth_quartz")
                        if d > R else w.b("water", level=0))
                if d <= R:
                    w.setze(x, -1, z, w.b("black_concrete"))
    ri = 2 * s + 1.5
    for x in range(-int(ri), int(ri) + 1):
        for z in range(-int(ri), int(ri) + 1):
            if math.hypot(x, z) <= ri:
                w.setze(x, 0, z, w.b("smooth_quartz"))
    for k in range(6):
        a = k / 6 * 6.283
        x, z = round(math.cos(a) * (ri - 0.5)), round(math.sin(a) * (ri - 0.5))
        for y in range(1, 5):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    kegeldach(w, 0, 0, 5, int(ri), Dachmat(w, ["quartz", "smooth_quartz"]), form="glocke")
    for z in range(int(ri) + 2, int(R) + 1, 2):
        w.setze(0, 0, z, w.b("smooth_quartz_slab", type="top", waterlogged=True) if False else w.b("smooth_quartz"))
    rng = w.rng
    for k in range(int(8 * s)):
        a = rng.random() * 6.283
        d = ri + 2 + rng.random() * (R - ri - 3)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        w.setze(x, 1, z, w.b("lily_pad"))
    return w


def planetenmodell(seed, g=2):
    """Planetenmodell: ein riesiges Messing-Orrery – um eine leuchtende Sonne kreisen auf geschwungenen Armen
    Planeten unterschiedlicher Farben, einer mit Ringen, einer mit Mond."""
    w = _neu(seed)
    s = S[g]
    boden(w, 12 * s + 4, "stein")
    H = int(6 * s + 4)
    for y in range(1, H):
        w.setze(0, y, 0, w.b("waxed_cut_copper"))
    kugel(w, 0, H + 2 * s, 0, 2.2 * s + 1, w.b("shroomlight"))
    farben = ["light_blue_concrete", "red_terracotta", "lime_terracotta", "orange_terracotta", "white_concrete",
              "purple_terracotta"]
    n = 4 + g
    for k in range(n):
        a = k * 2.399
        d = (4 + k * 2.2) * s + 2
        y = H + 2 * s + (k % 2) * 2 - 1
        for i in range(int(d)):
            w.setze(round(math.cos(a) * i), round(y - 1), round(math.sin(a) * i), w.b("gold_block") if i % 3 == 0
                    else w.b("waxed_cut_copper"), False)
        px, pz = math.cos(a) * d, math.sin(a) * d
        r = (0.8 + (k % 3) * 0.5) * s + 0.4
        kugel(w, px, y + r * 0.5, pz, r, w.b(farben[k % 6]))
        if k == 3:
            ring(w, round(px), round(y + r * 0.5), round(pz), r + 1.5, w.b("yellow_terracotta"), achse="y")
        if k == 1:
            kugel(w, px + r + 1.5, y + r, pz, 0.6, w.b("light_gray_concrete"))
    return w


def runenbruecke(seed, g=2):
    """Runenbrücke: eine Brücke aus einzelnen, schwebenden Steinplatten mit leuchtenden Runen spannt sich über eine
    Kluft zwischen zwei Felsen, jede Platte leicht versetzt, Lichter darunter."""
    w = _neu(seed)
    s = S[g]
    L = int(16 * s + 8)
    rng = w.rng
    for sx in (-1, 1):
        for x in range(L // 2, L // 2 + int(6 * s) + 4):
            for z in range(-int(5 * s) - 3, int(5 * s) + 4):
                h = int(6 * s + 3 - abs(z) * 0.3 + rng.random())
                for y in range(-3, h + 1):
                    w.setze(sx * x, y, z, w.b(["stone", "andesite", "tuff", "deepslate"][int(rng.random() * 4)]))
    yb = int(6 * s + 3)
    for i in range(-L // 2 + 1, L // 2, 3):
        dy = round(math.sin(i * 0.7) * 0.8)
        for x in range(i, i + 2):
            for z in range(-1, 2):
                w.setze(x, yb + dy, z, w.b("polished_deepslate" if (x + z) % 3 else "crying_obsidian"))
        w.setze(i, yb + dy - 1, 0, w.b("end_rod", facing="down"))
    return w


def elementarsaeulen(seed, g=2):
    """Elementarsäulen: vier hohe Säulen um einen Altar verkörpern die Elemente – eine aus Lava und Magma, eine aus
    Wasser und Prismarin, eine aus Moos und Wurzeln, eine aus Wolken und Glas."""
    w = _neu(seed)
    s = S[g]
    boden(w, 10 * s + 4, "stein")
    H = int(10 * s + 5)
    D = int(5 * s + 3)
    arten = [("magma_block", "lava"), ("prismarine", "water"), ("moss_block", "oak_leaves"),
             ("white_stained_glass", "white_wool")]
    for k, (aussen, innen) in enumerate(arten):
        a = k * 1.571 + 0.785
        cx, cz = round(math.cos(a) * D), round(math.sin(a) * D)
        for y in range(1, H):
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    rand = abs(dx) == 1 or abs(dz) == 1
                    if rand:
                        if (dx + dz + y) % 3 or k == 3:
                            w.setze(cx + dx, y, cz + dz, w.b(aussen))
                    else:
                        blk = w.b(innen, level=0) if innen in ("lava", "water") else w.b(
                            innen, persistent=True, distance=1, waterlogged=False) if "leaves" in innen else w.b(innen)
                        w.setze(cx + dx, y, cz + dz, blk)
        w.setze(cx, H, cz, w.b("chiseled_stone_bricks"))
    for x in range(-1, 2):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("chiseled_stone_bricks"))
    w.setze(0, 2, 0, w.b("beacon"))
    return w


def druidenhain(seed, g=2):
    """Druidenhain: ein Kreis aus mächtigen Eichen, deren Kronen sich zu einem Dach schließen, in der Mitte ein
    moosiger Altarstein mit Mistelzweigen, Steinbänke und Leuchtpilze."""
    w = _neu(seed)
    s = S[g]
    boden(w, 11 * s + 4)
    n = 6 + g
    R = 7 * s + 3
    for k in range(n):
        a = k / n * 6.283
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        einfuegen(w, wald2.laubbaum(seed + k, "oak", H=int(10 * s + 5), dick=g >= 2), x, 0, z)
    for x in range(-2, 3):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("mossy_cobblestone"))
    w.setze(0, 2, 0, w.b("moss_carpet"))
    w.setze(-1, 2, 0, w.b("lime_candle", candles=3, lit=True, waterlogged=False))
    w.setze(1, 2, 0, w.b("white_candle", candles=2, lit=True, waterlogged=False))
    for k in range(4):
        a = k * 1.571
        x, z = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        w.setze(x, 1, z, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    return w


def zauberkreis(seed, g=2):
    """Zauberkreis: ein großer, in den Boden eingelegter Kreis aus leuchtenden Ringen und Glyphen, an den Spitzen
    eines Sterns brennen Kerzen auf Säulchen, in der Mitte schwebt ein Kristall."""
    from kristall import kristall
    w = _neu(seed)
    s = S[g]
    R = 9 * s + 4
    boden(w, R + 2, "dunkel")
    ring(w, 0, 0, 0, R, w.b("crying_obsidian"), achse="y", dicke=0.4)
    ring(w, 0, 0, 0, R - 2, w.b("amethyst_block"), achse="y", dicke=0.3)
    for k in range(7):
        a1 = k / 7 * 6.283
        a2 = ((k + 3) % 7) / 7 * 6.283
        p1 = (math.cos(a1) * (R - 2), math.sin(a1) * (R - 2))
        p2 = (math.cos(a2) * (R - 2), math.sin(a2) * (R - 2))
        n = int(math.dist(p1, p2) * 2)
        for i in range(n + 1):
            t = i / n
            w.setze(round(p1[0] + (p2[0] - p1[0]) * t), 0, round(p1[1] + (p2[1] - p1[1]) * t),
                    w.b("purple_glazed_terracotta" if False else "pearlescent_froglight", axis="y"))
        x, z = round(p1[0]), round(p1[1])
        w.setze(x, 1, z, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                             west="none", waterlogged=False))
        w.setze(x, 2, z, w.b("purple_candle", candles=4, lit=True, waterlogged=False))
    kristall(w, (0, 4 + s, 0), (0, 1, 0), 3 * s + 1.5, 0.8 * s + 0.5, art="amethyst")
    return w


def schwebender_thron(seed, g=2):
    """Schwebender Thron: ein Thron aus dunklem Stein und Gold schwebt auf einem zerbrochenen Felsbrocken über einer
    Plattform, Ketten hängen herab, umkreist von kleinen Steinsplittern."""
    w = _neu(seed)
    s = S[g]
    boden(w, 9 * s + 4, "stein")
    y0 = int(5 * s + 3)
    rng = w.rng
    R = 3 * s + 2
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            d = math.hypot(x, z)
            if d <= R:
                depth = int((R - d) * 1.2 + rng.random() * 1.5)
                for y in range(y0 - depth, y0 + 1):
                    w.setze(x, y, z, w.b(["stone", "andesite", "tuff", "deepslate"][int(rng.random() * 4)]))
    B = int(1.5 * s + 1)
    for x in range(-B, B + 1):
        for y in range(y0 + 1, y0 + 3):
            for z in range(-B, B + 1):
                w.setze(x, y, z, w.b("polished_blackstone"))
        for y in range(y0 + 3, y0 + 3 + int(5 * s + 3)):
            w.setze(x, y, -B, w.b("polished_blackstone_bricks" if abs(x) < B else "gold_block"))
    for sx in (-1, 1):
        for z in range(-B, B + 1):
            w.setze(sx * B, y0 + 3, z, w.b("gold_block"))
    for k in range(4):
        a = k * 1.571 + 0.4
        x, z = round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8)
        for y in range(1, y0 - 2):
            w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False), False)
    for k in range(int(8 * s) + 4):
        a = rng.random() * 6.283
        d = R + 2 + rng.random() * 3
        w.setze(round(math.cos(a) * d), y0 + int(rng.random() * 5), round(math.sin(a) * d),
                w.b(["stone", "andesite", "tuff"][int(rng.random() * 3)]))
    return w


def alchemistenlabor(seed, g=2):
    """Alchemistenlabor: ein gedrungener, runder Steinbau mit Kupferkuppel, aus dem farbiger Rauch steigt, Destillier-
    kolben aus Glas auf dem Dach, Kessel und Braustände im Hof."""
    from himmelsstadt2 import rundturm
    w = _neu(seed)
    s = S[g]
    boden(w, 9 * s + 4)
    r = int(3 * s + 2)
    rundturm(w, 0, 0, 1, r, int(5 * s + 3), M(w, [("stone_bricks", 2), ("mossy_stone_bricks", 1)]),
             Dachmat(w, ["waxed_oxidized_cut_copper", "waxed_weathered_cut_copper"]), form="glocke")
    from feinbau import tuer
    tuer(w, 0, 1, r, "south", holz="dark_oak")
    for k, f in enumerate(["green_stained_glass", "purple_stained_glass", "orange_stained_glass"]):
        x = r + 3 + k * 2
        w.setze(x, 1, -2, w.b("brewing_stand", has_bottle_0=True, has_bottle_1=True, has_bottle_2=False))
        kugel(w, x, 2.5, 1, 0.9, w.b(f))
        w.setze(x, 4, 1, w.b(f))
    w.setze(-r - 2, 1, 0, w.b("cauldron"))
    w.setze(-r - 2, 0, 0, w.b("soul_campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    return w


def traumfaenger(seed, g=2):
    """Traumfänger: ein riesiger Traumfänger aus einem Weidenring mit Netz aus Spinnenseide, Perlen und Federn,
    aufgehängt zwischen zwei Birken, darunter ein Schlafplatz aus Fellen."""
    w = _neu(seed)
    s = S[g]
    boden(w, 9 * s + 4)
    R = 5 * s + 2
    yc = int(R + 5 * s + 3)
    D = int(R + 3)
    for sx in (-1, 1):
        for y in range(1, yc + int(R) + 3):
            w.setze(sx * D, y, 0, w.b("birch_log", axis="y"))
    for x in range(-D, D + 1):
        w.setze(x, yc + int(R) + 2, 0, w.b("birch_log", axis="x"))
    ring(w, 0, yc, 0, R, w.b("stripped_dark_oak_log", axis="y"), dicke=0.5)
    for k in range(9):
        a1 = k / 9 * 6.283
        a2 = (k + 4) / 9 * 6.283
        p1 = (math.cos(a1) * R, math.sin(a1) * R)
        p2 = (math.cos(a2) * R, math.sin(a2) * R)
        n = int(math.dist(p1, p2) * 2)
        for i in range(n + 1):
            t = i / n
            w.setze(round(p1[0] + (p2[0] - p1[0]) * t), round(yc + p1[1] + (p2[1] - p1[1]) * t), 0, w.b("cobweb"),
                    False)
    w.setze(0, yc, 0, w.b("light_blue_stained_glass"))
    for k in range(3):
        x = round((k - 1) * R * 0.6)
        for y in range(yc - int(R) - 3, yc - int(R)):
            w.setze(x, y, 0, w.b("white_stained_glass_pane", north=False, south=False, east=False, west=False,
                                 waterlogged=False), False)
        w.setze(x, yc - int(R) - 4, 0, w.b("white_wool"), False)
        w.setze(x, yc - int(R) - 5, 0, w.b("feather" if False else "white_wool"), False)
    for x in range(-2, 3):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("brown_carpet"))
    return w


def himmelsleiter(seed, g=2):
    """Himmelsleiter: eine endlose Wendeltreppe aus weißem Stein ohne Geländer schraubt sich frei in den Himmel und
    verliert sich in einer Wolke, an den Stufen hängen Laternen."""
    w = _neu(seed)
    s = S[g]
    boden(w, 7 * s + 4)
    H = int(26 * s + 10)
    R = 3 * s + 2
    for i in range(H * 3):
        a = i * 0.35
        y = 1 + i // 3
        for d in np.arange(R - 1.5, R + 0.6, 0.5):
            w.setze(round(math.cos(a) * d), y, round(math.sin(a) * d), w.b("smooth_quartz_slab", type="top",
                                                                             waterlogged=False), False)
        if i % 12 == 0:
            w.setze(round(math.cos(a) * (R + 1)), y - 1, round(math.sin(a) * (R + 1)), w.b("lantern", hanging=True,
                                                                                         waterlogged=False))
    rng = w.rng
    for k in range(int(10 * s) + 5):
        cx, cy, cz = (rng.random() - 0.5) * R * 3, H + rng.random() * 3, (rng.random() - 0.5) * R * 3
        kugel(w, cx, cy, cz, 1.5 + rng.random() * 2 * s, w.b("white_wool"), ry=1.2 + rng.random())
    return w


def nebeltor(seed, g=2):
    """Nebeltor: zwei alte, bemooste Steinpfeiler mit einem Sturz, zwischen denen ein wabernder Vorhang aus
    weißem Nebel hängt – auf der anderen Seite scheint eine andere Welt zu liegen."""
    w = _neu(seed)
    s = S[g]
    boden(w, 9 * s + 4)
    B = int(4 * s + 2)
    H = int(8 * s + 4)
    st = M(w, [("mossy_stone_bricks", 2), ("stone_bricks", 1), ("cracked_stone_bricks", 1)])
    for sx in (-1, 1):
        for y in range(1, H + 1):
            for dx in range(2):
                w.setze(sx * (B + dx), y, 0, st(sx * B, y, 0))
                w.setze(sx * (B + dx), y, 1, st(sx * B, y, 1))
    for x in range(-B - 1, B + 2):
        for z in (0, 1):
            w.setze(x, H + 1, z, st(x, H, z))
    rng = w.rng
    for x in range(-B + 1, B):
        for y in range(1, H + 1):
            w.setze(x, y, 0, w.b("white_stained_glass" if rng.random() < 0.7 else "light_gray_stained_glass"))
    glyphen(w, -B, B, H + 1, 2)
    from feinbau import efeu
    efeu(w, 0.1, laub=0.3)
    return w


def seherkugel(seed, g=1):
    """Seherkugel: eine große Kristallkugel auf einem dreibeinigen Bronzegestell, in ihrem Inneren wirbeln Nebel und
    Lichter, ringsum Sitzkissen, Räucherschalen und Sternkarten."""
    w = _neu(seed)
    s = S[g]
    boden(w, 8 * s + 4, "dunkel")
    H = int(3 * s + 2)
    for k in range(3):
        a = k * 2.094
        pts = bez((math.cos(a) * 2 * s, 0, math.sin(a) * 2 * s), (math.cos(a) * 2.5 * s, H * 0.5, math.sin(a) * 2.5 * s),
                  (math.cos(a) * 0.8 * s, H, math.sin(a) * 0.8 * s))
        rohr(w, pts, 0.4, 0.3, w.b("waxed_oxidized_cut_copper"))
    R = 2.5 * s + 1
    kugel(w, 0, H + R, 0, R, lambda x, y, z: w.b("light_blue_stained_glass" if (x + y + z) % 4 else
                                                 "purple_stained_glass"), hohl=True)
    kugel(w, 0, H + R, 0, max(0.6, R * 0.35), w.b("pearlescent_froglight", axis="y"))
    for k in range(4):
        a = k * 1.571 + 0.785
        x, z = round(math.cos(a) * (R + 3)), round(math.sin(a) * (R + 3))
        w.setze(x, 1, z, w.b(["red_wool", "purple_wool", "blue_wool", "magenta_wool"][k]))
    return w


def sonnenaltar(seed, g=2):
    """Sonnenaltar: auf einer Stufenplattform erhebt sich eine gewaltige goldene Sonnenscheibe mit Strahlenkranz,
    ein Feuer brennt auf dem Altar davor, Obelisken markieren die Himmelsrichtungen."""
    w = _neu(seed)
    s = S[g]
    boden(w, 11 * s + 4, "stein")
    for k in range(3):
        r = 6 * s + 3 - k * 1.5
        for x in range(-int(r), int(r) + 1):
            for z in range(-int(r), int(r) + 1):
                if max(abs(x), abs(z)) <= r:
                    w.setze(x, 1 + k, z, w.b("smooth_sandstone"))
    R = 4 * s + 2
    yc = int(4 + R + 2 * s)
    for x in range(-int(R) - 4, int(R) + 5):
        for y in range(-int(R) - 4, int(R) + 5):
            d = math.hypot(x, y)
            a = math.atan2(y, x)
            strahl = d <= R + 3 * s and abs(math.sin(a * 6)) < 0.25 and d > R
            if d <= R or strahl:
                w.setze(x, yc + y, -2, w.b("gold_block" if d <= R - 1 or strahl else "orange_concrete"))
    w.setze(0, 4, 2, w.b("chiseled_sandstone"))
    w.setze(0, 5, 2, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for k in range(4):
        a = k * 1.571
        obelisk(w, round(math.cos(a) * (8 * s + 4)), round(math.sin(a) * (8 * s + 4)), 1, int(6 * s + 3),
                "smooth_sandstone", "gold_block")
    return w


def erdgeisthuegel(seed, g=2):
    """Erdgeist-Hügel: ein runder, grasbewachsener Hügel, durch den leuchtend grüne Adern ziehen, aus einer
    Felsspalte schaut ein riesiges Gesicht aus Stein und Moos mit glühenden Augen."""
    w = _neu(seed)
    s = S[g]
    R = 10 * s + 4
    rng = w.rng
    boden(w, R + 2)
    H = 6 * s + 3
    for x in range(-int(R), int(R) + 1):
        for z in range(-int(R), int(R) + 1):
            d = math.hypot(x, z) / R
            if d <= 1:
                h = int(H * (1 - d * d))
                for y in range(1, h + 1):
                    ader = abs(math.sin(x * 0.7 + z * 0.4 + y * 0.3)) < 0.06
                    w.setze(x, y, z, w.b("verdant_froglight", axis="y") if ader and y < h else
                            w.b("grass_block", snowy=False) if y == h else w.b("dirt"))
    zf = int(R * 0.78) + 1
    yf = int(H * 0.3) + 1
    for x in range(-3, 4):
        for y in range(yf - 2, yf + 4):
            w.setze(x, y, zf, w.b("mossy_cobblestone" if (x + y) % 3 else "stone"))
    for sx in (-1, 1):
        w.setze(sx * 2, yf + 2, zf + 1, w.b("verdant_froglight", axis="y"))
    for x in range(-1, 2):
        w.setze(x, yf - 1, zf + 1, w.b("black_concrete"))
    w.setze(0, yf + 1, zf + 1, w.b("stone"))
    return w


def mondphasensteine(seed, g=2):
    """Mondphasen-Steine: acht aufrechte Steinplatten im Kreis zeigen die Phasen des Mondes als eingelegte
    leuchtende Scheiben, vom Neumond bis zum Vollmond, in der Mitte ein flacher Mondstein."""
    w = _neu(seed)
    s = S[g]
    R = 8 * s + 4
    boden(w, R + 3)
    H = int(4 * s + 3)
    for k in range(8):
        a = k / 8 * 6.283
        cx, cz = math.cos(a) * R, math.sin(a) * R
        tx, tz = -math.sin(a), math.cos(a)
        for t in range(-int(1.5 * s) - 1, int(1.5 * s) + 2):
            for y in range(1, H + 1):
                w.setze(round(cx + tx * t), y, round(cz + tz * t), w.b("deepslate_tiles"))
        phase = k / 8
        rr = 1.0 * s + 0.6
        for t in range(-int(rr) - 1, int(rr) + 2):
            for dy in range(-int(rr) - 1, int(rr) + 2):
                if t * t + dy * dy <= rr * rr:
                    licht = (t / rr) < math.cos(phase * 6.283) * 1.0
                    w.setze(round(cx + tx * t + math.cos(a)), H // 2 + 1 + dy, round(cz + tz * t + math.sin(a)),
                            w.b("sea_lantern" if licht else "black_concrete"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            if math.hypot(x, z) <= 2.3:
                w.setze(x, 1, z, w.b("smooth_quartz" if math.hypot(x, z) > 1 else "sea_lantern"))
    return w


def gefrorene_zeit(seed, g=2):
    """Gefrorene Zeit: ein Wasserfall, der mitten im Sturz zu Eis erstarrt ist, darin hängen Fische, Tropfen und ein
    kleines Boot reglos in der Luft, Schneeflocken schweben um eine zerbrochene Uhr."""
    w = _neu(seed)
    s = S[g]
    R = 10 * s + 4
    rng = w.rng
    boden(w, R, "stein")
    H = int(12 * s + 5)
    for x in range(-int(R), int(R) + 1):
        for z in range(-int(R), -int(R * 0.3)):
            for y in range(1, H + 2):
                w.setze(x, y, z, w.b(["stone", "andesite", "packed_ice"][int(rng.random() * 3)]))
    for x in range(-int(3 * s) - 1, int(3 * s) + 2):
        for y in range(1, H + 1):
            dz = int(math.sin(y * 0.4 + x) * 0.7)
            w.setze(x, y, -int(R * 0.3) + dz, w.b("blue_ice" if (x + y) % 3 else "ice"))
    for (x, z) in [(x, z) for x in range(-int(R), int(R) + 1) for z in range(-int(R * 0.3), int(R))
                   if math.hypot(x, z + R * 0.1) < R * 0.5]:
        w.setze(x, 0, z, w.b("packed_ice"))
    for k in range(int(8 * s) + 3):
        x, y, z = int((rng.random() - 0.5) * 6 * s), 2 + int(rng.random() * H * 0.7), -int(R * 0.3) + 1 + int(
            rng.random() * 3)
        w.setze(x, y, z, w.b(["orange_terracotta", "light_blue_stained_glass", "white_stained_glass"]
                             [int(rng.random() * 3)]), False)
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx * dx + dy * dy <= 5:
                w.setze(int(R * 0.4) + dx, 4 + dy, 2, w.b("white_concrete" if dx * dx + dy * dy < 4 else
                                                         "gold_block"))
    w.setze(int(R * 0.4) + 1, 5, 3, w.b("black_concrete"))
    return w


MYSTIK3 = {
    "mondsichelportal": ("Mondsichel-Portal", mondsichelportal),
    "schwebende_bibliothek": ("Schwebende Bibliothek", schwebende_bibliothek),
    "sanduhr": ("Riesensanduhr", sanduhr),
    "seelenbaum": ("Seelenbaum", seelenbaum),
    "spiegelsee": ("Spiegelsee", spiegelsee),
    "planetenmodell": ("Planetenmodell", planetenmodell),
    "runenbruecke": ("Runenbrücke", runenbruecke),
    "elementarsaeulen": ("Elementarsäulen", elementarsaeulen),
    "druidenhain": ("Druidenhain", druidenhain),
    "zauberkreis": ("Zauberkreis", zauberkreis),
    "schwebender_thron": ("Schwebender Thron", schwebender_thron),
    "alchemistenlabor": ("Alchemistenlabor", alchemistenlabor),
    "traumfaenger": ("Traumfänger", traumfaenger),
    "himmelsleiter": ("Himmelsleiter", himmelsleiter),
    "nebeltor": ("Nebeltor", nebeltor),
    "seherkugel": ("Seherkugel", seherkugel),
    "sonnenaltar": ("Sonnenaltar", sonnenaltar),
    "erdgeisthuegel": ("Erdgeist-Hügel", erdgeisthuegel),
    "mondphasensteine": ("Mondphasen-Steine", mondphasensteine),
    "gefrorene_zeit": ("Gefrorene Zeit", gefrorene_zeit),
}

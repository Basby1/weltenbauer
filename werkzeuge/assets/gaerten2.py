"""Hängende Gärten II – zwanzig weitere Gärten, aus denen Laub, Blüten und Ranken herabhängen: Gartenzikkurat,
Felsengarten, Gartenturm, Blumenbrücke, Glyzinien-Laubengang, Glyzinien-Pavillon, Ampelbogen, Dachgarten-Haus,
Wasserterrassen, Schwebende Gartenschalen, Grüne Wand, Kaskadengarten, Spiralgarten, Rosenlaube, Kräuterterrassen,
Gartenruine, Baumhausgarten, Orangerie, Aquäduktgarten und Babylonturm."""

from __future__ import annotations

import math

import wald2
from baeume2 import jacaranda_laub
from feinbau import (Dachmat, Mix, balkon, fachwerk, fenster, fensterreihe, kamin, kegeldach, laterne, mauer, platte,
                     satteldach, sockel, stamm, treppe, tuer, zaun)
from flora import _neu
from himmelsstadt import _lianen
from lib import einfuegen

S = [0.6, 1.0, 1.6, 2.5]
BLUMEN = ["poppy", "dandelion", "allium", "azure_bluet", "red_tulip", "pink_tulip", "orange_tulip", "cornflower",
          "oxeye_daisy", "lily_of_the_valley"]
HOCH = ["rose_bush", "peony", "lilac"]


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def laubblock(w, art=None):
    art = art or ["azalea_leaves", "flowering_azalea_leaves", "oak_leaves"][int(w.rng.random() * 3)]
    return w.b(art, persistent=True, distance=1, waterlogged=False)


def bepflanze(w, x, y, z, dichte=0.75):
    """Pflanzt auf (x, y, z) (Erde/Gras bei y) etwas Schönes in y + 1."""
    rng = w.rng
    if not w.frei(x, y + 1, z) or rng.random() > dichte:
        return
    r = rng.random()
    if r < 0.3:
        w.setze(x, y + 1, z, w.b(BLUMEN[int(rng.random() * len(BLUMEN))]))
    elif r < 0.5:
        w.setze(x, y + 1, z, laubblock(w))
    elif r < 0.62 and w.frei(x, y + 2, z):
        n = HOCH[int(rng.random() * 3)]
        w.setze(x, y + 1, z, w.b(n, half="lower"))
        w.setze(x, y + 2, z, w.b(n, half="upper"))
    elif r < 0.8:
        w.setze(x, y + 1, z, w.b("grass" if rng.random() < 0.6 else "fern"))
    else:
        w.setze(x, y + 1, z, w.b(["azalea", "flowering_azalea", "sweet_berry_bush"][int(rng.random() * 3)],
                                 **({"age": 3} if False else {})) if rng.random() < 0.7 else w.b("azalea"))


def beet(w, zellen, y, dichte=0.75, erde="grass_block"):
    for (x, z) in zellen:
        w.setze(x, y, z, w.b(erde, snowy=False) if erde == "grass_block" else w.b(erde))
        bepflanze(w, x, y, z, dichte)


def haengelaub(w, x, y, z, richtung, L, art=None):
    """Laub hängt vor einer Kante (x, y, z) in 'richtung' (dx, dz) L Blöcke herab."""
    dx, dz = richtung
    for k in range(L):
        p = (x + dx, y - k, z + dz)
        if not w.frei(*p) or p[1] < 1:
            break
        w.setze(*p, laubblock(w, art) if not isinstance(art, int) else art)


def kante_behaengen(w, zellen, y, anteil=0.5, Lmax=4, art=None, mitte=(0, 0)):
    """Für Randzellen eines Beets: Laub über die Außenkante hängen lassen."""
    rng = w.rng
    s = set(zellen)
    for (x, z) in zellen:
        for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, z + dz) not in s and w.frei(x + dx, y, z + dz) and rng.random() < anteil:
                haengelaub(w, x, y, z, (dx, dz), 1 + int(rng.random() * Lmax), art)


def glyzinie(w, x, y, z, L):
    """Herabhängender Blütenstrang (Jacaranda-Laub, sonst blühendes Azaleenlaub)."""
    lila = jacaranda_laub(w)
    for k in range(L):
        if not w.frei(x, y - k, z) or y - k < 1:
            break
        w.setze(x, y - k, z, lila if k < L - 1 or w.rng.random() < 0.5 else w.b("purple_stained_glass"))


def ranken(w, ids, anteil=0.06, L=5):
    _lianen(w, set(ids), anteil, L, 1)


def boden(w, R, rund=True):
    rng = w.rng
    zellen = []
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            d = math.hypot(x, z) if rund else max(abs(x), abs(z))
            if d <= R + rng.random() * 1.2:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
                w.setze(x, -1, z, w.b("dirt"))
                w.setze(x, -2, z, w.b("stone"))
                zellen.append((x, z))
    return zellen


def wiese(w, zellen, dichte=0.35):
    rng = w.rng
    for (x, z) in zellen:
        if w.frei(x, 1, z) and w.P.name(w.bloecke.get((x, 0, z), 0)) == "minecraft:grass_block":
            r = rng.random()
            if r < dichte * 0.6:
                w.setze(x, 1, z, w.b("grass"))
            elif r < dichte:
                w.setze(x, 1, z, w.b(BLUMEN[int(rng.random() * len(BLUMEN))]))


def weg(w, punkte, breite=1, mat=None):
    mat = mat or M(w, [("gravel", 2), ("cobblestone", 1), ("stone_bricks", 1), ("dirt_path", 2)], zelle=1.2)
    for (a, b) in zip(punkte, punkte[1:]):
        n = int(math.dist(a, b) * 2) + 1
        for i in range(n + 1):
            t = i / n
            cx, cz = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            for dx in range(-breite, breite + 1):
                for dz in range(-breite, breite + 1):
                    x, z = round(cx + dx), round(cz + dz)
                    w.setze(x, 0, z, mat(x, 0, z))
                    w.bloecke.pop((x, 1, z), None)


def stein(w):
    return M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 2), ("cracked_stone_bricks", 1), ("andesite", 1)])


def sand(w):
    return M(w, [("smooth_sandstone", 3), ("cut_sandstone", 2), ("sandstone", 1)])


def ring_ids(w, mix):
    return [i for i in mix.ids]


# ============================================================================ Gärten

def gartenzikkurat(seed, g=1):
    """Gartenzikkurat: eine Stufenpyramide aus Sandstein, jede Terrasse ein Pflanzbeet, über alle Kanten quellen
    Laub und Blüten, eine Freitreppe führt mittig zum Tempelchen auf der Spitze."""
    w = _neu(seed)
    s = S[g]
    st = sand(w)
    n = 3 + g
    R0 = int(9 * s + 4)
    h = int(3 + 1.6 * s)
    for k in range(n):
        r = R0 - k * int(2 * s + 1.5)
        y0 = k * h
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                for y in range(y0, y0 + h):
                    w.setze(x, y, z, st(x, y, z))
        zellen = [(x, z) for x in range(-r, r + 1) for z in range(-r, r + 1) if max(abs(x), abs(z)) >= r - 1]
        for (x, z) in zellen:
            if abs(x) <= 1 and z > 0:
                continue
            w.setze(x, y0 + h - 1, z, w.b("grass_block", snowy=False))
            bepflanze(w, x, y0 + h - 1, z, 0.85)
        kante_behaengen(w, [(x, z) for (x, z) in zellen if max(abs(x), abs(z)) == r], y0 + h - 1, 0.55, h + 1)
    top = n * h
    rt = max(2, R0 - n * int(2 * s + 1.5) + 1)
    for (x, z) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        for y in range(top, top + 4):
            w.setze(x, y, z, w.b("sandstone_wall", up=True, north="none",
                                 south="none", east="none", west="none", waterlogged=False) if y < top + 3 else
                    w.b("chiseled_sandstone"))
    for x in range(-3, 4):
        for z in range(-3, 4):
            w.setze(x, top + 4, z, platte(w, "smooth_sandstone"))
    w.setze(0, top, 0, w.b("water", level=0))
    return w


def felsengarten(seed, g=1):
    """Hängender Felsengarten: an einer zerklüfteten Felswand kleben übereinander gemauerte Pflanzbalkone, aus
    denen Laub, Ranken und Blüten in langen Vorhängen herabhängen, unten ein Teich."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    B, H = int(12 * s + 6), int(14 * s + 6)
    fels = M(w, [("stone", 3), ("andesite", 2), ("tuff", 1), ("mossy_cobblestone", 1)])
    for x in range(-B, B + 1):
        for y in range(-1, H + 1):
            t = int(3 + 2 * math.sin(x * 0.4 + y * 0.2) + (H - y) * 0.15 + rng.random())
            for z in range(-t - 4, -t + 1):
                w.setze(x, y, z, fels(x, y, z))
    zl = boden(w, B * 0.9)
    for x in range(-int(B * 0.5), int(B * 0.5) + 1):
        for z in range(1, 4):
            w.setze(x, 0, z, w.b("water", level=0))
    st = stein(w)
    for k in range(3 + g):
        bx = int((rng.random() - 0.5) * B * 1.4)
        by = int(3 + k * (H - 4) / (3 + g))
        bw = int(2 + rng.random() * 2 * s + 1)
        zf = max(z for z in range(-12, 4) if (bx, by, z) in w.bloecke) if any((bx, by, z) in w.bloecke
                                                                              for z in range(-12, 4)) else -3
        zellen = []
        for x in range(bx - bw, bx + bw + 1):
            for z in range(zf + 1, zf + 3):
                w.setze(x, by - 1, z, st(x, by, z))
                w.setze(x, by - 2, z, treppe(w, "stone_brick", "north", "top")) if z == zf + 2 else None
                zellen.append((x, z))
        beet(w, zellen, by, 0.9)
        for x in range(bx - bw, bx + bw + 1):
            haengelaub(w, x, by, zf + 2, (0, 1), int(2 + rng.random() * 4 * s))
    ranken(w, fels.ids, 0.07, int(4 + 4 * s))
    wiese(w, zl, 0.4)
    return w


def gartenturm(seed, g=1):
    """Gartenturm: ein runder Steinturm, an jedem Geschoss umläuft ihn ein Pflanzring, aus dem Laub über die
    Ränder quillt, Fenster mit Blumenkästen, oben ein Dachgarten mit Baum."""
    w = _neu(seed)
    s = S[g]
    R = int(3 * s + 2)
    H = int(16 * s + 6)
    st = stein(w)
    zl = boden(w, R + 6 * s + 3)
    wiese(w, zl, 0.4)
    for y in range(0, H):
        for x in range(-R, R + 1):
            for z in range(-R, R + 1):
                d = math.hypot(x, z)
                if R - 0.9 < d <= R + 0.4:
                    w.setze(x, y, z, st(x, y, z))
                elif d <= R - 0.9:
                    w.bloecke.pop((x, y, z), None)
    for e in range(4, H, 5):
        zellen = []
        for x in range(-R - 2, R + 3):
            for z in range(-R - 2, R + 3):
                d = math.hypot(x, z)
                if R + 0.4 < d <= R + 2.2:
                    w.setze(x, e - 1, z, st(x, e, z))
                    zellen.append((x, z))
        for (x, z) in zellen:
            if math.hypot(x, z) > R + 1.4:
                w.setze(x, e, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                     west="none", waterlogged=False) if w.rng.random() < 0.3 else w.b("dirt"))
            else:
                w.setze(x, e, z, w.b("grass_block", snowy=False))
            bepflanze(w, x, e, z, 0.7)
        kante_behaengen(w, [(x, z) for (x, z) in zellen if math.hypot(x, z) > R + 1.4], e - 1, 0.5, 4)
    for (dx, dz, sname) in ((R, 0, "east"), (-R, 0, "west"), (0, R, "south"), (0, -R, "north")):
        for e in range(2, H - 2, 5):
            fenster(w, dx, e, dz, sname, holz="spruce", blumen=0.8, laeden=False)
    tuer(w, 0, 0, R, "south", holz="spruce")
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R + 0.4:
                w.setze(x, H, z, w.b("grass_block", snowy=False))
    einfuegen(w, wald2.laubbaum(seed, "oak", H=5 + g), 0, H, 0)
    return w


def blumenbruecke(seed, g=1):
    """Blumenbrücke: eine steinerne Bogenbrücke über einen Bach, beide Brüstungen sind Pflanzkästen, aus denen
    Blüten und Laub bis zum Wasser herabhängen, Laternen an den Pfeilern."""
    w = _neu(seed)
    s = S[g]
    L = int(16 * s + 8)
    zl = boden(w, L * 0.7)
    for x in range(-int(L * 0.7) - 2, int(L * 0.7) + 3):
        for z in range(-int(3 * s + 2), int(3 * s + 2) + 1):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("gravel"))
    st = stein(w)
    Hb = 4 + 3 * s
    for i in range(-L // 2, L // 2 + 1):
        t = (i + L / 2) / L
        yb = round(Hb * math.sin(math.pi * t)) + 1
        for z in range(-int(3 * s + 4), int(3 * s + 4) + 1):
            x = 0
            pass
        for x in range(-2, 3):
            z = i
            w.setze(x, yb, z, w.b("polished_andesite") if abs(x) < 2 else st(x, yb, z))
            unter = round(Hb * math.sin(math.pi * t) * 0.6)
            for y in range(max(-1, yb - 2 - unter if abs(i) < L // 2 - 2 else -1), yb):
                if abs(i) > L * 0.32 or y >= yb - 1:
                    w.setze(x, y, z, st(x, y, z))
            if abs(x) == 2:
                w.setze(x, yb + 1, z, w.b("grass_block", snowy=False))
                bepflanze(w, x, yb + 1, z, 0.9)
                if w.rng.random() < 0.6:
                    haengelaub(w, x, yb + 1, z, (1 if x > 0 else -1, 0), int(2 + w.rng.random() * (yb + 1)))
        if i % 6 == 0:
            for x in (-3, 3):
                for y in range(yb, yb + 3):
                    w.setze(x, y, i, st(x, y, i))
                laterne(w, x, yb + 4, i, 0) if False else w.setze(x, yb + 3, i, w.b("lantern", hanging=False,
                                                                                      waterlogged=False))
    wiese(w, zl, 0.5)
    return w


def laubengang(seed, g=1):
    """Glyzinien-Laubengang: ein langer Holzgang aus Pfosten und Bögen, über und über mit hängenden violetten
    Blütentrauben bewachsen, darunter ein Kiesweg mit Bänken."""
    w = _neu(seed)
    s = S[g]
    L = int(16 * s + 8)
    zl = boden(w, L * 0.65)
    wiese(w, zl, 0.4)
    weg(w, [(0, -L // 2), (0, L // 2)], 1)
    rng = w.rng
    hb = int(4 + s)
    for z in range(-L // 2, L // 2 + 1):
        if z % 3 == 0:
            for x in (-3, 3):
                for y in range(1, hb + 1):
                    w.setze(x, y, z, stamm(w, "dark_oak", geschaelt=False))
        for x in range(-3, 4):
            y = hb + 1 + (1 if abs(x) < 2 else 0)
            w.setze(x, y, z, w.b("dark_oak_planks") if z % 3 == 0 else w.b("dark_oak_fence", north=True, south=True,
                                                                            east=False, west=False, waterlogged=False))
            if rng.random() < 0.85:
                w.setze(x, y + 1, z, jacaranda_laub(w))
            if rng.random() < 0.45:
                glyzinie(w, x, y - 1, z, int(1 + rng.random() * (hb - 1)))
        for x in (-4, 4):
            if rng.random() < 0.5:
                glyzinie(w, x, hb + 1, z, int(2 + rng.random() * hb))
    for z in range(-L // 2 + 3, L // 2 - 2, 6):
        for x in (-2, 2):
            w.setze(x, 1, z, treppe(w, "spruce", "east" if x < 0 else "west"))
    return w


def glyzinienpavillon(seed, g=1):
    """Glyzinien-Pavillon: ein achteckiger Gartenpavillon mit Glockendach, dessen Traufe von dichten,
    violetten Blütenvorhängen umhüllt ist, innen ein Brunnen."""
    w = _neu(seed)
    s = S[g]
    zl = boden(w, 10 * s + 5)
    wiese(w, zl, 0.45)
    r = int(3 * s + 2)
    for x in range(-r, r + 1):
        for z in range(-r, r + 1):
            if math.hypot(x, z) <= r + 0.5:
                w.setze(x, 0, z, w.b("smooth_stone"))
    hb = int(4 + s)
    for k in range(8):
        a = k / 8 * 6.283
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        for y in range(1, hb + 1):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    for x in range(-r - 1, r + 2):
        for z in range(-r - 1, r + 2):
            if math.hypot(x, z) <= r + 1.2:
                w.setze(x, hb + 1, z, w.b("smooth_quartz"))
    kegeldach(w, 0, 0, hb + 2, r, Dachmat(w, ["mcw:purple_terracotta", "purpur", "deepslate_tile"]), form="glocke")
    rng = w.rng
    for x in range(-r - 2, r + 3):
        for z in range(-r - 2, r + 3):
            d = math.hypot(x, z)
            if r + 0.6 < d <= r + 2.2 and rng.random() < 0.8:
                glyzinie(w, x, hb + 1, z, int(2 + rng.random() * (hb - 1)))
    w.setze(0, 1, 0, w.b("water_cauldron", level=3))
    return w


def ampelbogen(seed, g=1):
    """Ampelbogen: eine Reihe schmiedeeiserner Bögen über einem Gartenweg, an Ketten hängen Blumenampeln mit
    überquellenden Blüten und Ranken."""
    w = _neu(seed)
    s = S[g]
    n = 3 + g * 2
    L = n * 5
    zl = boden(w, L * 0.6)
    wiese(w, zl, 0.4)
    weg(w, [(-L // 2, 0), (L // 2, 0)], 1)
    rng = w.rng
    hb = int(5 + s)
    for k in range(n):
        x = -L // 2 + 2 + k * 5
        for z in range(-3, 4):
            y = hb + round(1.5 * math.cos(z / 3 * 1.4))
            w.setze(x, y, z, w.b("iron_bars", north=True, south=True, east=False, west=False, waterlogged=False))
        for z in (-3, 3):
            for y in range(1, hb + 1):
                w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                     waterlogged=False) if y > 1 else w.b("polished_blackstone"))
        for z in (-2, 2):
            ya = hb + 1
            for kk in range(2):
                w.setze(x, ya - kk, z, w.b("chain", axis="y", waterlogged=False))
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    w.setze(x + dx, ya - 2, z + dz, w.b("moss_block") if abs(dx) + abs(dz) < 2 else
                            laubblock(w))
                    if rng.random() < 0.5:
                        haengelaub(w, x + dx, ya - 2, z + dz, (0, 0) if False else (dx, dz),
                                   int(1 + rng.random() * 3)) if (dx or dz) else None
            w.setze(x, ya - 1, z, w.b(BLUMEN[int(rng.random() * len(BLUMEN))]))
    return w


def dachgartenhaus(seed, g=1):
    """Dachgarten-Haus: ein Stadthaus mit Flachdach, auf dem ein üppiger Garten mit Bäumchen, Pergola und
    Pflanzkübeln wächst, von der Dachkante hängen Ranken die Fassade hinab."""
    w = _neu(seed)
    s = S[g]
    B, T = int(7 + 4 * s), int(6 + 3 * s)
    zl = boden(w, max(B, T) * 0.9 + 2)
    wiese(w, zl, 0.3)
    x0, z0, x1, z1 = -B // 2, -T // 2, -B // 2 + B - 1, -T // 2 + T - 1
    wand = M(w, [("white_terracotta", 3), ("calcite", 1), ("smooth_sandstone", 1)])
    ge = 2 + (g > 1)
    sockel(w, x0, z0, x1, z1, -1, 1, stein(w))
    for k in range(ge):
        y0 = 1 + k * 4
        mauer(w, x0, z0, x1, z1, y0, y0 + 3, wand, ecke=w.b("stone_bricks"))
        fensterreihe(w, x0, z0, x1, z1, y0 + 1, ("north", "south", "east", "west"), abstand=3, holz="spruce",
                     blumen=0.9)
    tuer(w, 0, 1, z1, "south", holz="spruce")
    yd = 1 + ge * 4
    zellen = []
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            rand = x in (x0, x1) or z in (z0, z1)
            w.setze(x, yd, z, w.b("stone_bricks") if rand else w.b("grass_block", snowy=False))
            if rand:
                w.setze(x, yd + 1, z, w.b("grass_block", snowy=False) if (x + z) % 2 else
                        w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                            waterlogged=False))
                zellen.append((x, z))
            elif w.rng.random() < 0.5:
                bepflanze(w, x, yd, z, 0.6)
    for (x, z) in zellen:
        if w.P.name(w.bloecke.get((x, yd + 1, z), 0)) == "minecraft:grass_block":
            bepflanze(w, x, yd + 1, z, 0.9)
    kante_behaengen(w, zellen, yd, 0.6, int(3 + 4 * s))
    einfuegen(w, wald2.laubbaum(seed, "birch" if g < 2 else "oak", H=4 + g), x0 + 2, yd, z0 + 2)
    for x in range(x1 - 3, x1):
        w.setze(x, yd + 4, z1 - 1, w.b("spruce_slab", type="bottom", waterlogged=False))
    for x in (x1 - 3, x1 - 1):
        for y in range(yd + 1, yd + 4):
            w.setze(x, y, z1 - 1, zaun(w, "spruce"))
    return w


def wasserterrassen(seed, g=1):
    """Wasserterrassen: geschwungene, übereinander liegende Terrassen mit Wasserbecken, Seerosen und Schilf,
    Wasser rinnt in kleinen Fällen von Stufe zu Stufe, Laub hängt über die Mauern."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    n = 3 + g
    R0 = 10 * s + 6
    st = stein(w)
    for k in range(n):
        r = R0 * (1 - k / (n + 0.6))
        y0 = k * 2
        zellen = []
        for x in range(-int(R0) - 1, int(R0) + 2):
            for z in range(-int(R0) - 1, int(R0) + 2):
                d = math.hypot(x * 1.0, z * 1.4) + 1.5 * math.sin(math.atan2(z, x) * 5)
                if d <= r:
                    for y in range(-1, y0 + 2):
                        w.setze(x, y, z, st(x, y, z) if y <= y0 else w.b("water", level=0))
                    if d > r - 1.2:
                        w.setze(x, y0 + 1, z, st(x, y0, z))
                        w.setze(x, y0 + 2, z, w.b("grass_block", snowy=False))
                        zellen.append((x, z))
                    elif rng.random() < 0.08:
                        w.setze(x, y0 + 2, z, w.b("lily_pad"))
        for (x, z) in zellen:
            if rng.random() < 0.4:
                bepflanze(w, x, y0 + 2, z, 0.8)
        kante_behaengen(w, zellen, y0 + 2, 0.3, 2)
    for k in range(n - 1):
        y = (k + 1) * 2 + 2
        for yy in range(k * 2 + 2, y):
            w.setze(0, yy, int(R0 * (1 - (k + 1) / (n + 0.6)) / 1.4) + 1, w.b("water", level=0))
    return w


def gartenschalen(seed, g=1):
    """Schwebende Gartenschalen: an einem hohen Holzgerüst hängen an Ketten große, runde Pflanzschalen auf
    verschiedenen Höhen, aus jeder quellen Blumen und Ranken."""
    w = _neu(seed)
    s = S[g]
    zl = boden(w, 10 * s + 5)
    wiese(w, zl, 0.4)
    rng = w.rng
    H = int(10 * s + 5)
    B = int(6 * s + 3)
    for (x, z) in ((-B, -B), (B, -B), (-B, B), (B, B)):
        for y in range(1, H + 1):
            w.setze(x, y, z, stamm(w, "spruce", geschaelt=False))
    for t in range(-B, B + 1):
        for (x, z, ax) in ((t, -B, "x"), (t, B, "x"), (-B, t, "z"), (B, t, "z"), (t, 0, "x"), (0, t, "z")):
            w.setze(x, H + 1, z, stamm(w, "spruce", ax, geschaelt=False))
    for k in range(3 + g * 2):
        cx = round((rng.random() - 0.5) * B * 1.6)
        cz = 0 if k % 2 else round((rng.random() - 0.5) * B * 1.6)
        if k % 2 == 0:
            cx = 0
        y = int(H * (0.25 + 0.55 * rng.random()))
        r = int(1.8 * s + 1.2)
        for yy in range(y + 1, H + 1):
            w.setze(cx, yy, cz, w.b("chain", axis="y", waterlogged=False), False)
        zellen = []
        for dx in range(-r - 1, r + 2):
            for dz in range(-r - 1, r + 2):
                d = math.hypot(dx, dz)
                if d <= r + 0.5:
                    w.setze(cx + dx, y - 1, cz + dz, w.b("terracotta"))
                    if d > r - 0.5:
                        w.setze(cx + dx, y, cz + dz, w.b("terracotta"))
                    else:
                        w.setze(cx + dx, y, cz + dz, w.b("grass_block", snowy=False))
                        zellen.append((cx + dx, cz + dz))
        for (x, z) in zellen:
            bepflanze(w, x, y, z, 0.95)
        for dx in range(-r - 1, r + 2):
            for dz in range(-r - 1, r + 2):
                if r - 0.5 < math.hypot(dx, dz) <= r + 0.5 and rng.random() < 0.5:
                    haengelaub(w, cx + dx, y, cz + dz, (int(math.copysign(1, dx)) if abs(dx) >= abs(dz) else 0,
                                                        int(math.copysign(1, dz)) if abs(dz) > abs(dx) else 0),
                               int(1 + rng.random() * 4))
    return w


def gruene_wand(seed, g=1):
    """Grüne Wand: eine hohe Steinmauer mit Nischen und Pflanzregalen, vollständig bewachsen mit Moos, Laub,
    Farnen und Blüten wie ein senkrechter Garten, davor ein Wasserbecken."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    B, H = int(10 * s + 5), int(10 * s + 5)
    zl = boden(w, B + 3)
    wiese(w, zl, 0.4)
    st = stein(w)
    for x in range(-B, B + 1):
        for y in range(0, H + 1):
            for z in (-2, -1):
                w.setze(x, y, z, st(x, y, z))
    for x in range(-B, B + 1):
        for y in range(1, H + 1):
            r = rng.random()
            if r < 0.35:
                w.setze(x, y, 0, w.b("moss_block"))
            elif r < 0.6:
                w.setze(x, y, 0, laubblock(w))
            elif r < 0.7 and y % 3 == 0:
                w.setze(x, y, 0, platte(w, "stone_brick", "top"))
                if w.frei(x, y + 1, 0):
                    w.setze(x, y + 1, 0, w.b(["potted_fern", "potted_red_tulip", "potted_azure_bluet",
                                              "potted_allium"][int(rng.random() * 4)]))
            elif r < 0.85:
                w.setze(x, y, 0, w.b("vine", north=True, south=False, east=False, west=False, up=False))
    for x in range(-B + 1, B):
        for z in range(2, 4):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("stone_bricks"))
        w.setze(x, 0, 4, w.b("stone_bricks"))
    for x in range(-B, B + 1):
        w.setze(x, H + 1, -1, w.b("grass_block", snowy=False))
        bepflanze(w, x, H + 1, -1, 0.9)
    return w


def kaskadengarten(seed, g=1):
    """Kaskadengarten: eine Wassertreppe stürzt über viele Stufen einen Hang hinab, zu beiden Seiten
    terrassierte Blumenbeete, Zypressen und Laub, das in die Becken hängt."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    n = 5 + g * 2
    B = int(4 * s + 3)
    st = stein(w)
    for k in range(n):
        z0 = -n * 2 + k * 4
        y0 = (n - k) * 1
        for x in range(-B - 5, B + 6):
            for z in range(z0, z0 + 4):
                for y in range(-1, y0 + 1):
                    w.setze(x, y, z, st(x, y, z) if abs(x) <= 1 or y < y0 else w.b("dirt"))
                if abs(x) <= 1:
                    w.setze(x, y0 + 1, z, w.b("water", level=0))
                    w.setze(x, y0, z, w.b("prismarine_bricks"))
                elif abs(x) == 2:
                    w.setze(x, y0 + 1, z, st(x, y0, z))
                else:
                    w.setze(x, y0, z, w.b("grass_block", snowy=False))
                    bepflanze(w, x, y0, z, 0.7)
        for x in range(-1, 2):
            if w.frei(x, y0 + 1, z0 - 1):
                w.setze(x, y0 + 1, z0 - 1, w.b("water", level=0))
    for k in range(2 + g):
        for sx in (-1, 1):
            x = sx * (B + 4)
            z = -n * 2 + 2 + k * 8
            yb = max(y for y in range(-1, 20) if (x, y, z) in w.bloecke)
            einfuegen(w, wald2.fichte(seed + k * 7 + sx, schmal=0.4), x, yb, z)
    return w


def spiralgarten(seed, g=1):
    """Spiralgarten: eine Rampe aus Stein windet sich spiralförmig um einen Hügel nach oben, gesäumt von
    Pflanzkästen, aus denen Laub über die Kante hängt, auf dem Gipfel ein Baum."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    R0 = int(9 * s + 5)
    H = int(10 * s + 4)
    st = stein(w)
    for x in range(-R0 - 2, R0 + 3):
        for z in range(-R0 - 2, R0 + 3):
            d = math.hypot(x, z)
            if d <= R0:
                h = int(H * (1 - d / R0) ** 0.9)
                for y in range(-1, h + 1):
                    w.setze(x, y, z, w.b("dirt") if y < h else w.b("grass_block", snowy=False))
    for i in range(int(R0 * 30)):
        t = i / (R0 * 30)
        a = t * 6.283 * 2.5
        r = R0 * (1 - t * 0.85)
        y = int(H * t)
        for dr in (0, 1, 2):
            x, z = round(math.cos(a) * (r + dr - 1)), round(math.sin(a) * (r + dr - 1))
            w.setze(x, y, z, st(x, y, z) if dr != 2 else w.b("grass_block", snowy=False))
            for yy in range(y + 1, y + 3):
                w.bloecke.pop((x, yy, z), None)
            if dr == 2:
                bepflanze(w, x, y, z, 0.6)
                if rng.random() < 0.3:
                    haengelaub(w, x, y, z, (round(math.cos(a)), round(math.sin(a))), int(1 + rng.random() * 3))
    einfuegen(w, wald2.laubbaum(seed, "oak", H=5 + g * 2), 0, H, 0)
    return w


def rosenlaube(seed, g=1):
    """Rosenlaube: ein Rundgarten mit hohen Rosenbögen über vier Wegen, Rosenbüschen und Hecken, in der Mitte ein
    weißer Pavillon mit Bank."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    R = int(10 * s + 5)
    zl = boden(w, R)
    wiese(w, zl, 0.2)
    for a in range(4):
        dx, dz = [(1, 0), (0, 1), (-1, 0), (0, -1)][a]
        weg(w, [(0, 0), (dx * R, dz * R)], 0)
        for k in range(3, R - 1, 3):
            x, z = dx * k, dz * k
            sx, sz = dz, dx
            for t in range(-2, 3):
                y = 4 + (1 if abs(t) < 2 else 0)
                px, pz = x + sx * t, z + sz * t
                w.setze(px, y, pz, w.b("oak_leaves" if rng.random() < 0.5 else "flowering_azalea_leaves",
                                       persistent=True, distance=1, waterlogged=False))
                if abs(t) == 2:
                    for yy in range(1, y):
                        w.setze(px, yy, pz, w.b("rose_bush", half="lower") if yy == 1 else
                                w.b("rose_bush", half="upper") if yy == 2 else laubblock(w, "oak_leaves"))
    for (x, z) in zl:
        d = math.hypot(x, z)
        if R - 1.5 < d <= R and w.frei(x, 1, z):
            w.setze(x, 1, z, laubblock(w, "oak_leaves"))
            w.setze(x, 2, z, laubblock(w, "oak_leaves"))
        elif 3 < d < R - 1.5 and w.frei(x, 1, z) and w.P.name(w.bloecke.get((x, 0, z), 0)) == \
                "minecraft:grass_block" and rng.random() < 0.3:
            w.setze(x, 1, z, w.b("rose_bush", half="lower"))
            w.setze(x, 2, z, w.b("rose_bush", half="upper"))
    for k in range(6):
        a = k / 6 * 6.283
        x, z = round(math.cos(a) * 2), round(math.sin(a) * 2)
        for y in range(1, 4):
            w.setze(x, y, z, w.b("birch_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    kegeldach(w, 0, 0, 4, 2, Dachmat(w, ["birch", "stone_brick"]), form="glocke")
    return w


def kraeuterterrassen(seed, g=1):
    """Kräuterterrassen: am Hang liegen schmale, von Trockenmauern gestützte Beete mit Kräutern, Gemüse und
    Bienenstöcken, ein Gärtnerhäuschen mit Fachwerk oben am Hang."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    n = 3 + g
    B = int(8 * s + 6)
    st = M(w, [("cobblestone", 3), ("mossy_cobblestone", 2), ("stone", 1)])
    for k in range(n):
        z0 = -n * 2 + k * 4
        y0 = k * 2
        for x in range(-B, B + 1):
            for z in range(z0, z0 + 4):
                for y in range(-1, y0 + 1):
                    w.setze(x, y, z, st(x, y, z) if z == z0 + 3 and y >= y0 - 1 else w.b("dirt"))
                if z < z0 + 3:
                    r = rng.random()
                    w.setze(x, y0, z, w.b("farmland", moisture=7) if z == z0 + 1 else w.b("grass_block",
                                                                                         snowy=False))
                    if z == z0 + 1:
                        w.setze(x, y0 + 1, z, w.b(["carrots", "potatoes", "beetroots", "wheat"][x % 4],
                                                  age=3 if x % 4 == 2 else 7))
                    elif r < 0.5:
                        w.setze(x, y0 + 1, z, w.b(["fern", "grass", "allium", "azure_bluet", "sweet_berry_bush"]
                                                  [int(rng.random() * 5)], **({"age": 3} if False else {})))
        for x in range(-B, B + 1, 7):
            w.setze(x, y0 + 1, z0 + 2, w.b("bee_nest", facing="south", honey_level=5))
    kante = [(x, -n * 2 + k * 4 + 3) for k in range(n) for x in range(-B, B + 1)]
    for (x, z) in kante:
        if rng.random() < 0.3:
            k = (z + n * 2) // 4
            haengelaub(w, x, k * 2 + 0, z, (0, -1) if False else (0, 1), int(1 + rng.random() * 2), "oak_leaves")
    yt = n * 2
    zt = n * 2 + 3
    for x in range(-4, 5):
        for z in range(zt - 3, zt + 4):
            for y in range(-1, yt):
                w.setze(x, y, z, w.b("dirt"))
            w.setze(x, yt - 1, z, w.b("grass_block", snowy=False))
    fachwerk(w, -2, zt - 2, 2, zt + 2, yt, yt + 3, M(w, [("white_terracotta", 1)]), holz="spruce", abstand=2)
    satteldach(w, -2, zt - 2, 2, zt + 2, yt + 4, Dachmat(w, ["spruce", "dark_oak"]), first_x=True, traufe="spruce")
    tuer(w, 0, yt, zt - 2, "north", holz="spruce")
    return w


def gartenruine(seed, g=1):
    """Gartenruine: die Bögen und Säulen eines verfallenen Kreuzgangs, von Efeu, Moos und Blumen
    zurückerobert, Laub hängt aus den Bogenöffnungen, in der Mitte ein moosiger Brunnen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    a = int(6 * s + 4)
    zl = boden(w, a + 4, rund=False)
    wiese(w, zl, 0.6)
    st = M(w, [("mossy_stone_bricks", 3), ("cracked_stone_bricks", 2), ("stone_bricks", 1), ("mossy_cobblestone", 1)])
    hb = int(4 + s)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if max(abs(x), abs(z)) != a:
                continue
            t = (x if abs(z) == a else z) + a
            for y in range(1, hb + 2):
                bogen = t % 4 != 0 and y <= hb - (1 if t % 4 in (1, 3) else 0)
                if not bogen and rng.random() < 0.88 - y * 0.04:
                    w.setze(x, y, z, st(x, y, z))
    for (x, y, z), b in list(w.bloecke.items()):
        if y >= hb and rng.random() < 0.35:
            w.setze(x, y + 1, z, laubblock(w))
    for x in range(-1, 2):
        for z in range(-1, 2):
            w.setze(x, 1, z, st(x, 1, z) if (x or z) else w.b("water", level=0))
    ranken(w, st.ids, 0.12, hb)
    return w


def baumhausgarten(seed, g=1):
    """Baumhausgarten: um einen großen Baum winden sich Holzplattformen in mehreren Höhen, jede ein kleiner Garten
    mit Pflanzkästen, aus denen Laub und Ranken herabhängen, Strickleitern verbinden sie."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    zl = boden(w, 9 * s + 4)
    wiese(w, zl, 0.4)
    H = int(14 * s + 8)
    einfuegen(w, wald2.laubbaum(seed, "oak", H=H, dick=True), 0, 0, 0)
    for k in range(2 + g):
        y = int(4 + k * (H * 0.5) / (2 + g))
        a = k * 2.1
        cx, cz = round(math.cos(a) * 3 * s), round(math.sin(a) * 3 * s)
        r = int(2 * s + 2)
        zellen = []
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if math.hypot(dx, dz) <= r + 0.4:
                    w.setze(cx + dx, y, cz + dz, w.b("spruce_planks"), False)
                    if math.hypot(dx, dz) > r - 0.7:
                        zellen.append((cx + dx, cz + dz))
        for (x, z) in zellen:
            if w.frei(x, y + 1, z):
                w.setze(x, y + 1, z, w.b("grass_block", snowy=False) if rng.random() < 0.6 else zaun(w, "spruce"))
                if w.P.name(w.bloecke[(x, y + 1, z)]) == "minecraft:grass_block":
                    bepflanze(w, x, y + 1, z, 0.9)
                    if rng.random() < 0.5:
                        haengelaub(w, x, y + 1, z, (int(math.copysign(1, x - cx)) if abs(x - cx) >= abs(z - cz) else 0,
                                                    int(math.copysign(1, z - cz)) if abs(z - cz) > abs(x - cx) else 0),
                                   int(1 + rng.random() * 4))
        for yy in range(1, y):
            if w.frei(cx + r + 1, yy, cz):
                w.setze(cx + r + 1, yy, cz, w.b("ladder", facing="east", waterlogged=False))
        for dx in (-1, 0, 1):
            for yy in range(y - 2, y):
                pass
        w.setze(cx, y - 1, cz, w.b("lantern", hanging=True, waterlogged=False), False)
    return w


def orangerie(seed, g=1):
    """Orangerie: eine lange Glashalle mit gewölbtem Dach und weißen Rippen, innen Zitrusbäumchen in Kübeln,
    Kletterpflanzen an den Säulen und ein Springbrunnen, davor ein Parterre."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    L, B = int(14 * s + 8), int(6 * s + 5)
    zl = boden(w, L * 0.7 + 3)
    wiese(w, zl, 0.25)
    x0, x1 = -L // 2, L // 2
    z0, z1 = -B // 2, B // 2
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, 0, z, w.b("smooth_stone") if (x + z) % 2 else w.b("polished_diorite"))
    r = (B) / 2
    hw = int(4 + s)
    for x in range(x0, x1 + 1):
        rippe = (x - x0) % 3 == 0
        for z in range(z0, z1 + 1):
            u = z
            hy = int(math.sqrt(max(0, r * r - u * u)) * 0.8)
            for y in range(1, hw + hy + 1):
                aussen = z in (z0, z1) or y == hw + hy or x in (x0, x1)
                if aussen:
                    w.setze(x, y, z, w.b("white_concrete") if rippe or y <= 1 else w.b("glass"))
    for x in range(x0 + 2, x1 - 1, 3):
        for z in (z0 + 1, z1 - 1):
            w.setze(x, 1, z, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False))
            w.setze(x, 2, z, w.b("oak_log", axis="y"))
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    for dy in (3, 4):
                        if rng.random() < 0.85:
                            w.setze(x + dx, dy, z + dz, w.b("orange_terracotta") if rng.random() < 0.12 else
                                    laubblock(w, "oak_leaves"), False)
    w.setze(0, 1, 0, w.b("water_cauldron", level=3))
    for x in range(x0, x1 + 1):
        for z in range(z1 + 2, z1 + 6):
            if (x + z) % 4 == 0 and w.frei(x, 1, z):
                w.setze(x, 1, z, laubblock(w, "oak_leaves"))
            elif w.frei(x, 1, z):
                w.setze(x, 1, z, w.b(["red_tulip", "white_tulip", "orange_tulip"][abs(x) % 3]))
    return w


def aquaeduktgarten(seed, g=1):
    """Aquäduktgarten: über eine Wiese zieht sich ein Aquädukt mit zwei Bogenreihen, oben fließt Wasser in einer
    Rinne zwischen Pflanzkästen, aus allen Bögen hängen Laub und Blütenranken."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    L = int(20 * s + 10)
    zl = boden(w, L * 0.6)
    wiese(w, zl, 0.4)
    st = M(w, [("smooth_sandstone", 2), ("cut_sandstone", 1), ("stone_bricks", 1)])
    hb = int(5 * s + 3)
    sp = 4
    for x in range(-L // 2, L // 2 + 1):
        t = (x + L // 2) % sp
        for z in range(-2, 3):
            for y in range(1, hb * 2 + 2):
                unten_bogen = y <= hb - 1 and t != 0 and y < hb - abs(t - sp / 2) * 0.5
                oben_bogen = hb + 1 <= y <= hb * 2 - 1 and t != 0 and y < hb * 2 - abs(t - sp / 2) * 0.5
                if not (unten_bogen or oben_bogen):
                    w.setze(x, y, z, st(x, y, z))
        yt = hb * 2 + 2
        w.setze(x, yt, 0, w.b("water", level=0))
        for z in (-2, 2):
            w.setze(x, yt, z, w.b("grass_block", snowy=False))
            bepflanze(w, x, yt, z, 0.8)
        for z in (-1, 1):
            w.setze(x, yt, z, st(x, yt, z))
        for z in (-2, 2):
            if rng.random() < 0.5:
                haengelaub(w, x, yt, z, (0, 1 if z > 0 else -1), int(2 + rng.random() * hb))
    for (x, y, z), b in list(w.bloecke.items()):
        if w.frei(x, y - 1, z) and y > 2 and rng.random() < 0.2 and b in st.ids:
            glyzinie(w, x, y - 1, z, int(1 + rng.random() * 3))
    return w


def babylonturm(seed, g=1):
    """Babylonturm: ein mächtiger, gestufter Turm aus Lehmziegeln, jede Terrasse mit Palmen und Laub bepflanzt,
    das in grünen Vorhängen herabfällt, ein Wasserfall stürzt von der Spitze über die Stufen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    n = 4 + g
    R0 = int(9 * s + 5)
    h = int(3 + s)
    stp = max(2, min(int(1.6 * s + 1.4), (R0 - 3) // n))
    st = M(w, [("mud_bricks", 3), ("packed_mud", 1), ("smooth_sandstone", 1), ("terracotta", 1)])
    for k in range(n):
        r = R0 - k * stp
        y0 = k * h
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                d = max(abs(x), abs(z))
                for y in range(y0, y0 + h):
                    if d == r and y > y0 and (x + z + y) % 4 == 0 and abs(x) != abs(z):
                        w.setze(x, y, z, w.b("air") if y == y0 + h - 2 else st(x, y, z))
                    else:
                        w.setze(x, y, z, st(x, y, z))
        zellen = [(x, z) for x in range(-r, r + 1) for z in range(-r, r + 1)
                  if max(abs(x), abs(z)) >= r - stp + 1]
        for (x, z) in zellen:
            w.setze(x, y0 + h - 1, z, w.b("grass_block", snowy=False))
            bepflanze(w, x, y0 + h - 1, z, 0.7)
        kante_behaengen(w, [(x, z) for (x, z) in zellen if max(abs(x), abs(z)) == r], y0 + h - 1, 0.6, h + 2)
        for j in range(2 + g):
            (x, z) = zellen[int(rng.random() * len(zellen))]
            if all(w.frei(x, y0 + h + q, z) for q in (0, 3, 5)):
                einfuegen(w, wald2.palme(seed + k * 10 + j, H=5 + g), x, y0 + h - 1, z)
    top = n * h
    for k in range(n):
        r = R0 - k * stp
        for y in range(k * h, (k + 1) * h + 1):
            w.setze(0, y, r + 1, w.b("water", level=0))
    w.setze(0, top, 0, w.b("water", level=0))
    return w


GAERTEN2 = {
    "gartenzikkurat": ("Gartenzikkurat", gartenzikkurat),
    "felsengarten": ("Hängender Felsengarten", felsengarten),
    "gartenturm": ("Gartenturm", gartenturm),
    "blumenbruecke": ("Blumenbrücke", blumenbruecke),
    "laubengang": ("Glyzinien-Laubengang", laubengang),
    "glyzinienpavillon": ("Glyzinien-Pavillon", glyzinienpavillon),
    "ampelbogen": ("Ampelbogen", ampelbogen),
    "dachgartenhaus": ("Dachgarten-Haus", dachgartenhaus),
    "wasserterrassen": ("Wasserterrassen", wasserterrassen),
    "gartenschalen": ("Schwebende Gartenschalen", gartenschalen),
    "gruene_wand": ("Grüne Wand", gruene_wand),
    "kaskadengarten": ("Kaskadengarten", kaskadengarten),
    "spiralgarten": ("Spiralgarten", spiralgarten),
    "rosenlaube": ("Rosenlaube", rosenlaube),
    "kraeuterterrassen": ("Kräuterterrassen", kraeuterterrassen),
    "gartenruine": ("Gartenruine", gartenruine),
    "baumhausgarten": ("Baumhausgarten", baumhausgarten),
    "orangerie": ("Orangerie", orangerie),
    "aquaeduktgarten": ("Aquäduktgarten", aquaeduktgarten),
    "babylonturm": ("Babylonturm", babylonturm),
}

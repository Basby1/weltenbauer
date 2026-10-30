"""Sumpf & Moor II – zwanzig weitere Sumpfbauten: Mangrovensteg, Sumpfmühle, Schlammtöpfe, Torfkanal mit Kähnen,
Wollgrasmoor, Moorbirkenhain, Moosbehangene Sumpfeiche, Reusenfischerei, Schildkröteninsel, Libellenweiher, Moorbad,
Vogelbeobachtungshütte, Versunkene Kapelle, Schwimmende Schilfinsel, Sonnentau-Wiese, Floßhaus, Kranichwiese,
Moorfindlinge, Kanuanleger und Erlenbruch."""

from __future__ import annotations

import math

import wald2
from erw_basis import M, S, baum, birke, figur, haus, hoehe
from erw_gewaesser import landschaft
from erw_markt import mensch
from feinbau import laterne
from flora import _neu
from leuchtwald2 import baum_aeste, bez, kugel, laubball, rohr
from lib import Rauschen, einfuegen
from skulptur import ell, kap


def sumpfland(w, R, wasser=0.45, rauh=4.0, torf=False):
    """Flaches Sumpfgelände: Wasserlöcher, Schlamm, Moos, Schilf und Seerosen. Gibt Höhen zurück."""
    rn = Rauschen(w, rauh)

    def hf(x, z):
        return 0 if rn(x, 1, z) < wasser else 1

    hs = landschaft(w, R, hf, wy=0, sand=False, gras_deko=0.0, boden_tief=3)
    rng = w.rng
    rm = Rauschen(w, 2)
    for (x, z), h in hs.items():
        if h <= 0:
            w.setze(x, h, z, w.b("mud") if rm(x, 2, z) < 0.28 else w.b("water", level=0))
            w.setze(x, h - 1, z, w.b("mud"))
            if w.P.name(w.bloecke[(x, h, z)]) == "water" and rng.random() < 0.06:
                w.setze(x, 1, z, w.b("lily_pad"))
        else:
            v = rm(x, 4, z)
            w.setze(x, h, z, w.b("moss_block") if v < 0.3 else w.b("mud") if v > 0.85 else
                    w.b("brown_mushroom_block", north=True, south=True, east=True, west=True, up=True, down=True)
                    if torf and v > 0.7 else w.b("grass_block", snowy=False))
            r = rng.random()
            if r < 0.07:
                for y in (h + 1, h + 2):
                    w.setze(x, y, z, w.b("sugar_cane", age=0))
            elif r < 0.14:
                w.setze(x, h + 1, z, w.b("grass") if r < 0.11 else w.b("fern"))
    return hs


def steg(w, pts, y=1, holz="spruce", gelaender=False, pfosten=3):
    alle = []
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        n = max(abs(bx - ax), abs(bz - az), 1)
        for k in range(n + 1):
            alle.append((round(ax + (bx - ax) * k / n), round(az + (bz - az) * k / n)))
    for i, (x, z) in enumerate(alle):
        for dx in (0, 1):
            w.setze(x + dx, y, z, w.b(f"{holz}_slab", type="top", waterlogged=False))
        if i % pfosten == 0:
            for yy in range(-1, y):
                w.setze(x - 1, yy, z, w.b(f"{holz}_log", axis="y"))
            if gelaender:
                w.setze(x - 1, y, z, w.b(f"{holz}_fence"))
                w.setze(x - 1, y + 1, z, w.b(f"{holz}_fence"))
    return alle


def vogel(w, koerper="light_gray_wool", hals="light_gray_wool", kopf="black_wool", schnabel="yellow_wool", bein=2.4):
    return [(ell(0, bein + 0.8, 0, 1.2, 0.7, 0.6), w.b(koerper)),
            (kap((0.8, bein + 1.1, 0), (1.3, bein + 3.0, 0), 0.22), w.b(hals)),
            (ell(1.4, bein + 3.2, 0, 0.35, 0.28, 0.25), w.b(kopf)),
            (kap((1.6, bein + 3.2, 0), (2.4, bein + 3.0, 0), 0.08), w.b(schnabel)),
            (kap((0, bein + 0.3, 0.2), (0, 0, 0.2), 0.1), w.b("black_wool")),
            (kap((0, bein + 0.3, -0.2), (0.2, 0, -0.3), 0.1), w.b("black_wool")),
            (kap((-1.0, bein + 0.9, 0), (-1.6, bein + 0.6, 0), 0.3), w.b("black_wool"))]


# ============================================================================ Bauten

def mangrovensteg(seed, g=2):
    """Mangrovensteg: ein verwinkelter Holzsteg auf Pfählen führt durch einen dichten Mangrovenwald mit Stelzwurzeln,
    Schlamm und Brackwasser zu einer kleinen Aussichtsplattform mit Dach."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hs = sumpfland(w, R, wasser=0.65)
    rng = w.rng
    for k in range(int(6 + 5 * s)):
        a = rng.random() * 6.28
        r = R * (0.2 + rng.random() * 0.7)
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        if abs(x) < 3:
            continue
        H = 5 + rng.random() * 3 * s
        for j in range(4):
            b = j / 4 * 2 * math.pi + rng.random()
            rohr(w, bez((x + math.cos(b) * 2.5, -1, z + math.sin(b) * 2.5), (x + math.cos(b) * 1.5, 2, z + math.sin(b) * 1.5),
                        (x, 3, z)), 0.45, 0.45, w.b("mangrove_roots", waterlogged=False), rauh=0.0)
        for y in range(3, int(H)):
            w.setze(x, y, z, w.b("mangrove_log", axis="y"))
        laubball(w, x, H + 1, z, 2.5 + s * 0.6, arten=("mangrove_leaves",))
    pts = [(0, R - 1), (0, int(R * 0.3)), (-int(R * 0.3), 0), (-int(R * 0.1), -int(R * 0.4))]
    alle = steg(w, pts, y=2)
    ex, ez = alle[-1]
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            w.setze(ex + dx, 2, ez + dz, w.b("spruce_planks"))
            w.setze(ex + dx, 6, ez + dz, w.b("spruce_slab", type="bottom", waterlogged=False))
    for dx in (-2, 2):
        for dz in (-2, 2):
            for y in range(3, 6):
                w.setze(ex + dx, y, ez + dz, w.b("spruce_log", axis="y"))
    return w


def sumpfmuehle(seed, g=1):
    """Sumpfmühle: eine schiefe, bemooste Wassermühle auf Pfählen an einem träge fließenden Moorbach, mit
    unterschlächtigem Mühlrad, Schilfdach, Säcken am Steg und einem Kahn."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    hs = sumpfland(w, R, wasser=0.4)
    for x in range(-R, R + 1):
        for dz in range(-2, 3):
            z = round(math.sin(x / 5)) + dz
            if (x, z) in hs:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
                w.bloecke.pop((x, 1, z), None)
    wand = M(w, [("spruce_planks", 3), ("mossy_cobblestone", 1), ("stripped_spruce_log", 1)])
    zh = -int(3 + s)
    for dx in (-2, 2):
        for dz in (-2, 2):
            for y in range(-1, 2):
                w.setze(dx, y, zh + dz - 2, w.b("spruce_log", axis="y"))
    haus(w, 0, zh - 2, 5, 5, 2, wand, holz="spruce", H=3, dach=("mcw:thatch", "spruce"), tuer_s="east", schorn=False)
    from erw_handwerk import wasserrad
    wasserrad(w, 0, 0, 2, 2 + 0.6 * s, achse="z")
    for k in range(3):
        w.setze(3 + k, 2, zh, w.b("white_wool"))
    return w


def schlammtoepfe(seed, g=2):
    """Schlammtöpfe: auf einer kahlen, dampfenden Moorfläche blubbern runde Becken voller grauem Schlamm, umrandet von
    Schwefelkrusten in Gelb und Ocker, dazwischen tote Bäume und Dampfsäulen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)

    def hf(x, z):
        return 1 + rn(x, 2, z) * 1.5

    hs = landschaft(w, R, hf, gras_deko=0.0)
    for (x, z), h in hs.items():
        w.setze(x, h, z, w.b("mud") if rn(x, 5, z) < 0.4 else w.b("coarse_dirt") if rn(x, 5, z) < 0.7 else
                w.b("packed_mud"))
    rng = w.rng
    for k in range(int(5 + 3 * s)):
        a = rng.random() * 6.28
        r = rng.random() * R * 0.7
        cx, cz = math.cos(a) * r, math.sin(a) * r
        rt = 1.2 + rng.random() * (1 + s)
        for x in range(int(cx - rt) - 2, int(cx + rt) + 3):
            for z in range(int(cz - rt) - 2, int(cz + rt) + 3):
                d = math.hypot(x - cx, z - cz)
                if (x, z) not in hs:
                    continue
                h = hs[(x, z)]
                if d < rt:
                    w.setze(x, h, z, w.b("gray_concrete_powder") if (x + z) % 3 else w.b("light_gray_concrete_powder"))
                    w.setze(x, h - 1, z, w.b("magma_block"))
                    if rng.random() < 0.15:
                        w.setze(x, h + 1, z, w.b("light_gray_wool"), False) if False else None
                elif d < rt + 1.2:
                    w.setze(x, h, z, w.b("yellow_terracotta") if (x + z) % 2 else w.b("orange_terracotta"))
        w.setze(round(cx), hs.get((round(cx), round(cz)), 1) + 1, round(cz),
                w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False)) if k % 2 == 0 else None
    for k in range(int(2 + 2 * s)):
        a = rng.random() * 6.28
        x, z = round(math.cos(a) * R * 0.75), round(math.sin(a) * R * 0.75)
        h = hs.get((x, z), 1)
        for y in range(h + 1, h + int(4 + 3 * s)):
            w.setze(x, y, z, w.b("stripped_dark_oak_log", axis="y"))
        w.setze(x + 1, h + int(3 + 2 * s), z, w.b("stripped_dark_oak_log", axis="x"))
    return w


def torfkanal(seed, g=2):
    """Torfkanal mit Kähnen: ein schnurgerader, schwarzer Moorkanal, an dem flache Torfkähne mit gestapelten Torf-
    soden liegen; daneben Trockenstapel, ein Torfstecherhaus und Birken am Rand."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hs = sumpfland(w, R, wasser=0.2, torf=True)
    for (x, z), h in hs.items():
        if abs(z) <= 1 + int(s * 0.6):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("mud"))
            for y in range(1, 3):
                w.bloecke.pop((x, y, z), None)
    for k in range(int(1 + s)):
        bx = -int(R * 0.5) + k * int(R * 0.6)
        for dx in range(-3, 4):
            for dz in (-1, 0, 1):
                w.setze(bx + dx, 0, dz, w.b("dark_oak_planks") if abs(dz) == 1 or abs(dx) == 3 else
                        w.b("dark_oak_slab", type="top", waterlogged=False))
            if abs(dx) < 3:
                w.setze(bx + dx, 1, 0, w.b("mud_bricks"))
    for k in range(int(4 + 3 * s)):
        x, z = -int(R * 0.6) + k * 3, int(R * 0.4)
        for dy in range(2):
            for dx in (0, 1):
                w.setze(x + dx, hs.get((x, z), 1) + 1 + dy, z, w.b("packed_mud") if dy == 0 else w.b("mud_bricks"))
    haus(w, int(R * 0.4), -int(R * 0.5), 6, 4, 2, M(w, [("spruce_planks", 2), ("mud_bricks", 1)]), holz="spruce", H=3,
         dach=("mcw:thatch", "spruce"), tuer_s="north")
    for k in range(int(3 + s)):
        x = -int(R * 0.7) + k * 5
        birke(w, x, hs.get((x, -int(R * 0.6)), 1) + 1, -int(R * 0.6), seed + k, 6 + 2 * s)
    return w


def wollgrasmoor(seed, g=2):
    """Wollgrasmoor: eine weite, offene Hochmoorfläche mit Torfmoos in Rot, Grün und Braun, auf der tausende weiße
    Wollgrasbüschel wehen; Bulten und Schlenken, ein einzelner Holzbohlenweg."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hs = sumpfland(w, R, wasser=0.3)
    rng = w.rng
    rm = Rauschen(w, 3)
    for (x, z), h in hs.items():
        if h >= 1:
            v = rm(x, 7, z)
            w.setze(x, h, z, w.b("moss_block") if v < 0.35 else w.b("red_terracotta") if v < 0.45 else
                    w.b("brown_terracotta") if v < 0.55 else w.b("grass_block", snowy=False))
            if rng.random() < 0.35:
                w.setze(x, h + 1, z, w.b("white_carpet") if False else w.b("lily_of_the_valley") if rng.random() < 0.5
                        else w.b("oxeye_daisy"))
            else:
                w.bloecke.pop((x, h + 1, z), None) if w.P.name(w.bloecke.get((x, h + 1, z), 0)) == "sugar_cane" else None
    steg(w, [(-R, 0), (R, 0)], y=1, pfosten=4)
    return w


def moorbirkenhain(seed, g=2):
    """Moorbirkenhain: lichte, krumme Moorbirken stehen in nassem Torfmoos zwischen dunklen Wassertümpeln, dazwischen
    Pfeifengras, Heidelbeeren und ein umgestürzter Stamm."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hs = sumpfland(w, R, wasser=0.35)
    rng = w.rng
    for k in range(int(8 + 6 * s)):
        a = rng.random() * 6.28
        r = rng.random() * R * 0.85
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        if hs.get((x, z), 0) >= 1:
            birke(w, x, hs[(x, z)] + 1, z, seed + k, 5 + rng.random() * 4 * s)
    x0 = -int(R * 0.4)
    for t in range(int(5 + 3 * s)):
        w.setze(x0 + t, 1, 2, w.b("birch_log", axis="x"), False)
    for (x, z), h in hs.items():
        if h >= 1 and rng.random() < 0.05:
            w.setze(x, h + 1, z, w.b("sweet_berry_bush", age=2))
    return w


def sumpfeiche(seed, g=2):
    """Moosbehangene Sumpfeiche: eine uralte, breit ausladende Eiche, deren Äste mit langen Vorhängen aus Moos und
    Ranken behangen sind, steht auf einer Insel mitten im Sumpf; ihre Wurzeln greifen ins Wasser."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hs = sumpfland(w, R, wasser=0.6)
    kugel(w, 0, 0, 0, R * 0.3, w.b("grass_block", snowy=False), ry=1.5)
    rng = w.rng
    H = 9 + 4 * s
    enden = baum_aeste(w, 0, 0, H, 6 + g, 6 + 4 * s, "dark_oak", 1.6 + 0.6 * s, rng, steigung=0.15, start=0.45)
    for (x, y, z) in enden:
        laubball(w, x, y + 1, z, 2.5 + s, arten=("dark_oak_leaves", "oak_leaves"))
        for k in range(int(3 + 2 * s)):
            hx, hz = round(x + (rng.random() - 0.5) * 4), round(z + (rng.random() - 0.5) * 4)
            L = int(2 + rng.random() * 4 * s)
            for d in range(L):
                yy = round(y) - 1 - d
                if yy < 2:
                    break
                w.setze(hx, yy, hz, w.b("moss_block") if d % 3 == 0 else w.b("azalea_leaves", persistent=True,
                                                                               distance=1, waterlogged=False), False)
    for k in range(5):
        b = k / 5 * 2 * math.pi
        rohr(w, bez((0, 1, 0), (math.cos(b) * 2.5, 1, math.sin(b) * 2.5), (math.cos(b) * 4.5, -1, math.sin(b) * 4.5)),
             0.7 + 0.2 * s, 0.4, w.b("dark_oak_wood", axis="y"), rauh=0.1)
    return w


def reusenfischerei(seed, g=1):
    """Reusenfischerei: in einem schilfigen Altwasser stehen Reihen von Weidenreusen auf Pfählen, ein Fischer leert
    eine Reuse vom Kahn aus, am Ufer hängen Netze zum Trocknen an einem Gestell."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    hs = sumpfland(w, R, wasser=0.6)
    for k in range(int(4 + 3 * s)):
        x, z = -int(R * 0.5) + k * 3, -int(R * 0.1) + (k % 2) * 3
        w.setze(x, 0, z, w.b("water", level=0))
        for y in (1, 2):
            w.setze(x, y, z, w.b("spruce_fence"))
        w.setze(x + 1, 1, z, w.b("composter", level=0))
    bx, bz = int(R * 0.25), int(R * 0.2)
    for dx in range(-2, 3):
        for dz in (-1, 0, 1):
            w.setze(bx + dx, 0, bz + dz, w.b("water", level=0))
            if abs(dz) == 1 or abs(dx) == 2:
                w.setze(bx + dx, 1, bz + dz, w.b("spruce_slab", type="bottom", waterlogged=True))
    figur(w, 0.28 * s + 0.22, mensch(w, "brown_wool"), (-2, -1, -2), (2, 6, 2), pos=(bx, 1, bz), winkel=0.0)
    nx, nz = -int(R * 0.4), int(R * 0.55)
    for x in (nx, nx + 4):
        for y in range(1, 4):
            w.setze(x, hs.get((x, nz), 1) + y, nz, w.b("spruce_fence"))
    for x in range(nx, nx + 5):
        w.setze(x, hs.get((nx, nz), 1) + 4, nz, w.b("spruce_fence"))
        w.setze(x, hs.get((nx, nz), 1) + 3, nz, w.b("cobweb")) if x not in (nx, nx + 4) else None
    return w


def schildkroeteninsel(seed, g=1):
    """Schildkröteninsel: ein umgestürzter, bemooster Baumstamm und ein flacher Felsen im Moorteich, auf denen sich
    Sumpfschildkröten aller Größen in der Sonne wärmen; Seerosen und Rohrkolben ringsum."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    hs = sumpfland(w, R, wasser=0.75)
    L = int(6 + 3 * s)
    for t in range(-L, L + 1):
        for dz in (0, 1) if s > 1 else (0,):
            w.setze(t, 1, dz, w.b("dark_oak_log", axis="x"))
        if t % 3 == 0:
            w.setze(t, 2, 0, w.b("moss_carpet"))
    kugel(w, 2, 0.5, 4, 2 + 0.5 * s, w.b("mossy_cobblestone"), ry=1)
    pz = [(-L + 2, 2, 0), (0, 2, 0), (L - 3, 2, 0), (2, 2, 4), (3, 2, 3)]
    for k, (x, y, z) in enumerate(pz[:int(3 + s)]):
        gr = (0.18 + 0.1 * (k % 3)) * s + 0.15
        teile = [(ell(0, 0.6, 0, 1.4, 0.6, 1.1), w.b("green_terracotta")),
                 (ell(0, 0.4, 0, 1.5, 0.3, 1.2), w.b("lime_terracotta")),
                 (ell(1.6, 0.4, 0, 0.5, 0.35, 0.4), w.b("green_terracotta"))]
        figur(w, gr, teile, (-2, -1, -2), (3, 2, 2), pos=(x, y, z), winkel=k * 1.2)
    return w


def libellenweiher(seed, g=1):
    """Libellenweiher: ein klarer, flacher Weiher mit Schwertlilien und Seerosen, über dem große Libellen mit
    gläsern schimmernden Flügeln schweben; ein Steg mit Bank lädt zum Beobachten ein."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    rn = Rauschen(w, 4)

    def hf(x, z):
        return -1 if math.hypot(x, z) + rn(x, 1, z) * 2 < R * 0.55 else 1

    hs = landschaft(w, R, hf, wy=0, sand=False, gras_deko=0.1)
    rng = w.rng
    for (x, z), h in hs.items():
        if h < 0 and rng.random() < 0.07:
            w.setze(x, 1, z, w.b("lily_pad"))
        elif h == 1 and math.hypot(x, z) < R * 0.7 and rng.random() < 0.25:
            w.setze(x, 2, z, w.b("blue_orchid") if rng.random() < 0.5 else w.b("sugar_cane", age=0))
    for k in range(int(4 + 3 * s)):
        a = rng.random() * 6.28
        r = rng.random() * R * 0.5
        cx, cz, cy = math.cos(a) * r, math.sin(a) * r, 3 + rng.random() * 2
        teile = [(kap((-1.2, 0, 0), (1.0, 0, 0), 0.18), w.b(["cyan_concrete", "blue_concrete", "red_concrete"][k % 3])),
                 (ell(0.2, 0.05, 0.9, 0.3, 0.05, 0.8), w.b("light_blue_stained_glass")),
                 (ell(0.2, 0.05, -0.9, 0.3, 0.05, 0.8), w.b("light_blue_stained_glass")),
                 (ell(1.1, 0, 0, 0.25, 0.25, 0.25), w.b("lime_concrete"))]
        figur(w, 0.4 * s + 0.4, teile, (-2, -1, -2), (2, 1, 2), pos=(round(cx), round(cy), round(cz)), winkel=a)
    steg(w, [(0, R - 1), (0, int(R * 0.2))], y=1)
    for dx in (0, 1):
        w.setze(dx - 1, 2, int(R * 0.3), w.b("spruce_stairs", facing="south", half="bottom", shape="straight",
                                             waterlogged=False)) if False else None
    return w


def moorbad(seed, g=2):
    """Moorbad: ein historisches Kurhaus aus Fachwerk am Moorrand, mit hölzernen Badezubern voller braunem Moorschlamm,
    einem überdachten Wandelgang, Liegestühlen und einem Torfstapel für die Bäder."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hs = sumpfland(w, R, wasser=0.3)
    zh = -int(R * 0.45)
    from feinbau import fachwerk
    B, T = int(8 + 3 * s), int(5 + s)
    for x in range(-B // 2 - 1, B // 2 + 2):
        for z in range(zh - T // 2 - 1, zh + T // 2 + 2):
            w.setze(x, 1, z, w.b("cobblestone"))
    haus(w, 0, zh, B, T, 2, M(w, [("white_terracotta", 2), ("calcite", 1)]), holz="dark_oak", H=4,
         dach=("mcw:red_terracotta", "brick"), tuer_s="south")
    zg = zh + T // 2 + 2
    for x in range(-B // 2, B // 2 + 1):
        for z in (zg, zg + 1, zg + 2):
            w.setze(x, 1, z, w.b("spruce_planks"))
            w.setze(x, 5, z, w.b("spruce_slab", type="bottom", waterlogged=False))
        if x % 3 == 0:
            for y in range(2, 5):
                w.setze(x, y, zg + 2, w.b("dark_oak_log", axis="y"))
    for k in range(int(3 + s)):
        x = -B // 2 + 1 + k * 3
        z = zg + 5
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                w.setze(x + dx, 1, z + dz, w.b("spruce_planks") if abs(dx) + abs(dz) else w.b("mud"))
                if abs(dx) == 1 or abs(dz) == 1:
                    w.setze(x + dx, 2, z + dz, w.b("spruce_slab", type="bottom", waterlogged=False))
        w.setze(x, 2, z, w.b("mud"))
    for k in range(4):
        w.setze(B // 2 + 2, 2 + k // 2, zg + k % 2, w.b("packed_mud"))
    return w


def vogelhuette(seed, g=1):
    """Vogelbeobachtungshütte: eine getarnte, schilfgedeckte Hütte auf Stelzen am Rand eines Flachwassers, mit
    Sehschlitzen, einem Steg dorthin und Watvögeln, Reihern und Enten im Wasser davor."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    hs = sumpfland(w, R, wasser=0.55)
    hx, hz = 0, -int(R * 0.2)
    for dx in (-2, 2):
        for dz in (-2, 2):
            for y in range(-1, 3):
                w.setze(hx + dx, y, hz + dz, w.b("spruce_log", axis="y"))
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            w.setze(hx + dx, 3, hz + dz, w.b("spruce_planks"))
            if max(abs(dx), abs(dz)) == 2:
                for y in (4, 5):
                    w.setze(hx + dx, y, hz + dz, w.b("spruce_planks") if not (y == 5 and dz == 2 and abs(dx) < 2)
                            else w.b("air") if False else w.b("spruce_trapdoor", facing="south", half="top",
                                                                open=True, powered=False, waterlogged=False))
    from feinbau import satteldach, Dachmat
    satteldach(w, hx - 3, hz - 3, hx + 3, hz + 3, 6, Dachmat(w, ["mcw:thatch", "spruce"]), first_x=True)
    steg(w, [(hx, -R + 1), (hx, hz - 3)], y=1)
    for k in range(int(2 + s)):
        x, z = -int(R * 0.4) + k * int(R * 0.4), int(R * 0.35)
        figur(w, 0.3 * s + 0.25, vogel(w, "light_gray_wool", "white_wool", "light_gray_wool", "yellow_wool"),
              (-2, -1, -2), (3, 6, 2), pos=(x, 1, z), winkel=k)
    for k in range(3):
        figur(w, 0.2 * s + 0.15, vogel(w, "brown_wool", "green_wool", "green_wool", "yellow_wool", bein=0.2),
              (-2, -1, -2), (3, 4, 2), pos=(int(R * 0.3) + k * 2, 1, int(R * 0.15)), winkel=k)
    return w


def versunkene_kapelle(seed, g=2):
    """Versunkene Kapelle: eine kleine Feldsteinkapelle ist schief im Moor versunken, Wasser steht bis zu den Fenstern,
    das Glockentürmchen neigt sich, Efeu und Moos überziehen das Mauerwerk."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    hs = sumpfland(w, R, wasser=0.6)
    st = M(w, [("mossy_cobblestone", 3), ("cobblestone", 2), ("mossy_stone_bricks", 1)])
    B, T = int(3 + s), int(5 + 2 * s)
    neig = 0.18
    H = int(5 + 2 * s)
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            for y in range(-3, H):
                sx = x + round(y * neig)
                rand = abs(x) == B or abs(z) == T
                if rand:
                    fen = y == 2 and z % 3 == 0 and abs(x) == B
                    w.setze(sx, y, z, w.b("gray_stained_glass") if fen else st(sx, y, z))
                elif y > 0:
                    w.bloecke.pop((sx, y, z), None)
    for k in range(B + 2):
        for z in range(-T - 1, T + 2):
            y = H + k
            for xx in (-B - 1 + k, B + 1 - k):
                w.setze(xx + round(y * neig), y, z, w.b("cobbled_deepslate_stairs" if False else "cobblestone"))
    tz = T
    for y in range(H, H + int(4 + 2 * s)):
        for dx in (-1, 0, 1):
            for dz in (-1, 0):
                if abs(dx) == 1 or dz == -1:
                    w.setze(dx + round(y * neig * 1.5), y, tz + dz, st(dx, y, tz))
    yb = H + int(3 + 2 * s)
    w.setze(round(yb * neig * 1.5), yb - 1, tz, w.b("bell", attachment="ceiling", facing="north", powered=False))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 1 and rng.random() < 0.06 and "cobble" in w.P.name(b):
            if w.frei(x, y, z + 1):
                w.setze(x, y, z + 1, w.b("vine", north=True, south=False, east=False, west=False, up=False), False)
    return w


def schwimmende_insel(seed, g=1):
    """Schwimmende Schilfinsel: auf einem See treibt eine aus Schilfbündeln geflochtene Insel mit zwei kleinen
    Rundhütten aus Schilf, einem Trockengestell und einem Schilfboot mit hochgezogenem Bug."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)

    def hf(x, z):
        return -3

    landschaft(w, R, hf, wy=0, sand=False)
    ri = R * 0.55
    for x in range(-int(ri) - 1, int(ri) + 2):
        for z in range(-int(ri) - 1, int(ri) + 2):
            if math.hypot(x, z * 1.2) <= ri:
                w.setze(x, 0, z, w.b("hay_block", axis="x" if (x + z) % 2 else "z"))
                w.setze(x, 1, z, w.b("yellow_carpet")) if (x * 3 + z) % 7 == 0 else None
    for k, (cx, cz) in enumerate(((-int(ri * 0.4), 0), (int(ri * 0.35), -1))):
        r = 1.5 + 0.6 * s
        H = int(3 + s)
        for y in range(1, H + int(r) + 2):
            rr = r if y <= H else r * (1 - (y - H) / (r + 1.5))
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                for z in range(int(cz - r) - 1, int(cz + r) + 2):
                    d = math.hypot(x - cx, z - cz)
                    if rr - 0.8 < d <= rr + 0.3:
                        w.setze(x, y, z, w.b("hay_block", axis="y"))
        for y in (1, 2):
            w.bloecke.pop((round(cx), y, round(cz + r)), None)
    bx, bz = 0, round(ri) + 3
    for dx in range(-3, 4):
        w.setze(bx + dx, 0, bz, w.b("hay_block", axis="x"))
        w.setze(bx + dx, 0, bz + 1, w.b("hay_block", axis="x")) if abs(dx) < 2 else None
    w.setze(bx + 4, 1, bz, w.b("hay_block", axis="y"))
    w.setze(bx + 4, 2, bz, w.b("hay_block", axis="y"))
    return w


def sonnentauwiese(seed, g=1):
    """Sonnentau-Wiese: ein nasses Torfmoospolster voller übergroßer, fleischfressender Sonnentaupflanzen mit roten,
    glitzernden Tentakeln, dazwischen Moosbeeren und kleine Wasserlöcher."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    hs = sumpfland(w, R, wasser=0.25)
    rng = w.rng
    for k in range(int(6 + 5 * s)):
        a = rng.random() * 6.28
        r = rng.random() * R * 0.8
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        h = hs.get((x, z), 0)
        if h < 1:
            continue
        rp = 1 + 0.4 * s
        for j in range(int(5 + 2 * s)):
            b = j / (5 + 2 * s) * 2 * math.pi
            for t in range(1, int(rp * 2) + 1):
                px, pz = round(x + math.cos(b) * t * 0.6), round(z + math.sin(b) * t * 0.6)
                py = h + 1 + (1 if t > rp else 0)
                w.setze(px, py, pz, w.b("red_terracotta") if t < rp * 2 else w.b("red_stained_glass"), False)
            w.setze(round(x + math.cos(b) * rp * 1.4), h + 2, round(z + math.sin(b) * rp * 1.4),
                    w.b("pink_stained_glass"), False)
        w.setze(x, h + 1, z, w.b("crimson_roots"))
    return w


def flosshaus(seed, g=1):
    """Floßhaus: ein kleines Holzhaus auf einem großen Floß aus Baumstämmen, verankert in einem stillen Moorsee, mit
    Veranda, Angelruten, Wäscheleine, Kräutertöpfen und einem Beiboot."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)

    def hf(x, z):
        return -3 if math.hypot(x, z) < R * 0.85 else 1

    hs = landschaft(w, R, hf, wy=0, sand=False)
    A, B = int(4 + 1.5 * s), int(3 + s)
    for x in range(-A, A + 1):
        for z in range(-B, B + 1):
            w.setze(x, 0, z, w.b("spruce_log", axis="x"))
    haus(w, -1, -1, int(5 + s) | 1, int(4 + s * 0.5), 1, M(w, [("spruce_planks", 2), ("stripped_spruce_log", 1)]),
         holz="spruce", H=3, dach=("spruce", "dark_oak"), tuer_s="south")
    for x in range(-A, A + 1, 2):
        w.setze(x, 1, B, w.b("spruce_fence"))
    w.setze(A, 1, B - 1, w.b("spruce_fence"))
    w.setze(A, 2, B - 1, w.b("spruce_fence"))
    w.setze(A + 1, 2, B - 1, w.b("tripwire", attached=True, disarmed=False, powered=False, east=True, west=True,
                                 north=False, south=False))
    for k in range(3):
        w.setze(-A + k, 1, -B, w.b(["potted_fern", "potted_poppy", "potted_blue_orchid"][k]))
    bx, bz = A + 3, 0
    for dx in range(-2, 3):
        for dz in (-1, 1):
            w.setze(bx + dx, 0, bz + dz, w.b("spruce_slab", type="top", waterlogged=True))
    return w


def kranichwiese(seed, g=2):
    """Kranichwiese: eine nasse, offene Moorwiese im Herbst, auf der eine Schar grauer Kraniche mit roten Kappen
    steht und tanzt; Schilfgürtel, Wasserflächen und einzelne Weiden am Rand."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hs = sumpfland(w, R, wasser=0.35)
    rng = w.rng
    kranich = vogel(w, "light_gray_wool", "white_wool", "red_wool", "gray_wool", bein=3.0)
    for k in range(int(5 + 4 * s)):
        a = rng.random() * 6.28
        r = rng.random() * R * 0.7
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        if hs.get((x, z), 0) >= 1 and w.frei(x, hs[(x, z)] + 1, z):
            figur(w, 0.45 * s + 0.35, kranich, (-2, -1, -2), (3, 7, 2), pos=(x, hs[(x, z)] + 1, z), winkel=a)
    for k in range(int(2 + s)):
        a = k * 2.5
        x, z = round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8)
        if (x, z) in hs:
            einfuegen(w, wald2.weide(seed + k, H=int(6 + 2 * s)), x, hs[(x, z)] + 1, z)
    return w


def moorfindlinge(seed, g=2):
    """Moorfindlinge: im Moor liegen riesige, eiszeitliche Granitfindlinge, mit Flechten und Moos bewachsen, einige
    zu einem rätselhaften Halbkreis gestellt; Heide und Glockenblumen dazwischen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hs = sumpfland(w, R, wasser=0.25)
    rng = w.rng
    gr = M(w, [("granite", 3), ("polished_granite", 1), ("diorite", 1), ("mossy_cobblestone", 1)])
    for k in range(int(5 + 2 * s)):
        a = math.pi + k / (4 + 2 * s) * math.pi
        x, z = math.cos(a) * R * 0.45, math.sin(a) * R * 0.45
        r = 1.2 + rng.random() * (0.8 + 0.8 * s)
        kugel(w, x, r * 0.6, z, r, gr, ry=r * (1.1 + rng.random() * 0.5))
        top = hoehe(w, round(x), round(z), 20)
        w.setze(round(x), top + 1, round(z), w.b("moss_carpet"), False)
    for k in range(int(2 + s)):
        a = rng.random() * 6.28
        x, z = math.cos(a) * R * 0.2, math.sin(a) * R * 0.2
        kugel(w, x, 1, z, 2 + s, gr, ry=1.5 + 0.5 * s)
    for (x, z), h in hs.items():
        if h >= 1 and rng.random() < 0.06 and w.frei(x, h + 1, z):
            w.setze(x, h + 1, z, w.b("allium") if rng.random() < 0.5 else w.b("cornflower"))
    return w


def kanuanleger(seed, g=1):
    """Kanuanleger: ein Holzsteg mit Pfahlkopf-Laternen ragt in einen ruhigen Moorsee; daneben liegen bunte Kanus
    am Ufer und im Wasser, ein Paddelgestell und ein kleiner Unterstand mit Bank."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    rn = Rauschen(w, 4)

    def hf(x, z):
        return -2 if z > -R * 0.1 + rn(x, 1, 0) * 2 else 1

    hs = landschaft(w, R, hf, wy=0, sand=False)
    steg(w, [(0, -int(R * 0.2)), (0, int(R * 0.6))], y=1, gelaender=False)
    for z in range(0, int(R * 0.6), 4):
        laterne(w, -1, 3, z, kette=0)
        w.setze(-1, 2, z, w.b("spruce_fence"))
    farben = ["red_concrete", "yellow_concrete", "green_concrete", "orange_concrete"]
    for k in range(int(2 + s)):
        x = 3 + k * 3
        z = int(R * 0.15) + (k % 2) * 4
        for dz in range(-2, 3):
            w.setze(x, 0, z + dz, w.b(farben[k % 4]))
        w.setze(x, 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    for k in range(2):
        x = -5 - k * 3
        for dz in range(-2, 3):
            w.setze(x, 2, -int(R * 0.5) + dz, w.b(farben[(k + 2) % 4]))
    for dx in (-2, 2):
        for y in range(2, 5):
            w.setze(dx + 6, y, -int(R * 0.45), w.b("spruce_log", axis="y"))
    for dx in range(-2, 3):
        w.setze(dx + 6, 5, -int(R * 0.45), w.b("spruce_slab", type="bottom", waterlogged=False))
    return w


def erlenbruch(seed, g=2):
    """Erlenbruch: ein dunkler, nasser Bruchwald, in dem Erlen auf hohen Wurzelstelzen über schwarzem Wasser stehen;
    Farne auf den Bulten, Totholz, Moos und ein Knüppelpfad durch die Mitte."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hs = sumpfland(w, R, wasser=0.65)
    rng = w.rng
    for k in range(int(8 + 6 * s)):
        a = rng.random() * 6.28
        r = rng.random() * R * 0.85
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        if abs(x) < 2:
            continue
        kugel(w, x, 0.5, z, 1.4, w.b("moss_block"), ry=1)
        w.setze(x + 1, 2, z, w.b("fern"), False)
        H = int(6 + rng.random() * 4 * s)
        for y in range(1, H):
            w.setze(x, y, z, w.b("dark_oak_log", axis="y"))
        laubball(w, x, H + 1, z, 2 + s * 0.6, arten=("dark_oak_leaves", "oak_leaves"))
    for z in range(-R, R + 1):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_log", axis="x"), False)
    return w


SUMPF3 = {
    "mangrovensteg": ("Mangrovensteg", mangrovensteg),
    "sumpfmuehle": ("Sumpfmühle", sumpfmuehle),
    "schlammtoepfe": ("Schlammtöpfe", schlammtoepfe),
    "torfkanal": ("Torfkanal mit Kähnen", torfkanal),
    "wollgrasmoor": ("Wollgrasmoor", wollgrasmoor),
    "moorbirkenhain": ("Moorbirkenhain", moorbirkenhain),
    "sumpfeiche": ("Moosbehangene Sumpfeiche", sumpfeiche),
    "reusenfischerei": ("Reusenfischerei", reusenfischerei),
    "schildkroeteninsel": ("Schildkröteninsel", schildkroeteninsel),
    "libellenweiher": ("Libellenweiher", libellenweiher),
    "moorbad": ("Moorbad", moorbad),
    "vogelhuette": ("Vogelbeobachtungshütte", vogelhuette),
    "versunkene_kapelle": ("Versunkene Kapelle", versunkene_kapelle),
    "schwimmende_insel": ("Schwimmende Schilfinsel", schwimmende_insel),
    "sonnentauwiese": ("Sonnentau-Wiese", sonnentauwiese),
    "flosshaus": ("Floßhaus", flosshaus),
    "kranichwiese": ("Kranichwiese", kranichwiese),
    "moorfindlinge": ("Moorfindlinge", moorfindlinge),
    "kanuanleger": ("Kanuanleger", kanuanleger),
    "erlenbruch": ("Erlenbruch", erlenbruch),
}

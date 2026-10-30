"""Riesenpflanzen & Dschungelflora II – zwanzig weitere Pflanzen: Drachenbaum, Affenbrotbaum, Fächerpalme,
Säulenkaktus-Hain, Aloe-Garten, Agave mit Blütenschaft, Fackelingwer, Riesenrhabarber, Schraubenbaum, Epiphytenbaum,
Kokospalmen am Strand, Schachtelhalm-Urwald, Bougainvillea-Mauer, Feigenkaktus, Flaschenbaum, Regenbaum,
Wasserhyazinthen-Teich, Tillandsienvorhang, Jadewein-Laube und Seidenbaum."""

from __future__ import annotations

import math

import wald2
from blumen import bluete
from erw_basis import M, S, figur, hoehe, wiese
from flora import _neu, blatt, bogen, linie
from leuchtwald2 import baum_aeste, bez, kugel, laubball, rohr
from lib import Rauschen, einfuegen

GRUEN = ["green_concrete", "green_terracotta", "lime_terracotta"]


def stamm(w, pts, r0, r1, holz, rauh=0.15):
    rohr(w, pts, r0, r1, w.b(holz, axis="y") if not callable(holz) else holz, rauh=rauh)


def rosette(w, c, n, L, B, farben, steig=0.6, haeng=0.5, form="lanze", dreh=0.0, kipp=0.1, rng=None):
    for k in range(n):
        a = dreh + k / n * 2 * math.pi + (rng.random() * 0.3 if rng else 0)
        blatt(w, c, a, L * (0.8 + (rng.random() * 0.4 if rng else 0.2)), B, steig=steig, haeng=haeng, farben=farben,
              mitte=farben[-1], form=form, kipp=kipp)


def boden(w, s, art="wald", R=None, blumen=0.02):
    R = R or int(7 * s + 5)
    return wiese(w, R, huegel=0.15, art=art, blumen=blumen)


# ============================================================================ Pflanzen

def drachenbaum(seed, g=2):
    """Drachenbaum: ein dicker, mehrfach gegabelter Stamm trägt eine dichte, schirmförmige Krone aus steifen,
    schwertförmigen Blattbüscheln an den Astenden – wie ein umgedrehter Schirm über einer Felsküste."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    boden(w, s, art="kies")
    H = 5 + 3 * s
    stamm(w, bez((0, 0, 0), (0, H * 0.5, 0), (0, H, 0)), 1.2 + 0.5 * s, 1.0 + 0.4 * s, "stripped_birch_log")
    enden = []
    for k in range(int(5 + 2 * s)):
        a = k / (5 + 2 * s) * 2 * math.pi + rng.random() * 0.3
        L = 3 + 2.5 * s
        e = (math.cos(a) * L, H + L * 0.7, math.sin(a) * L)
        m = (math.cos(a) * L * 0.4, H + L * 0.15, math.sin(a) * L * 0.4)
        stamm(w, bez((0, H, 0), m, e), 0.7 + 0.2 * s, 0.4 + 0.1 * s, "stripped_birch_log")
        for j in range(2):
            b = a + (j - 0.5) * 0.6
            e2 = (e[0] + math.cos(b) * 1.5 * s, e[1] + 1.2 * s, e[2] + math.sin(b) * 1.5 * s)
            linie(w, e, e2, w.b("stripped_birch_log", axis="y"))
            enden.append(e2)
    for e in enden:
        rosette(w, e, 8, 1.6 * s + 1, 0.4 + 0.15 * s, ["green_terracotta", "cyan_terracotta", "green_concrete"],
                steig=0.6, haeng=0.3, rng=rng)
    return w


def baobab(seed, g=2):
    """Affenbrotbaum: ein gewaltiger, flaschenförmig angeschwollener Stamm mit glatter, grauer Rinde, oben eine
    kleine Krone aus wurzelartig verzweigten Ästen mit spärlichem Laub, darunter trockene Savanne."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    zellen = boden(w, s, art="strand", R=int(9 * s + 5))
    for (x, z), h in zellen.items():
        if rng.random() < 0.2:
            w.setze(x, h, z, w.b("coarse_dirt") if rng.random() < 0.5 else w.b("grass_block", snowy=False))
            if rng.random() < 0.3:
                w.setze(x, h + 1, z, w.b("dead_bush") if rng.random() < 0.4 else w.b("grass"))
    H = 7 + 5 * s
    rb = 2.5 + 1.5 * s
    for y in range(0, int(H) + 1):
        t = y / H
        r = rb * (1 + 0.35 * math.sin(t * math.pi * 0.9)) * (1 - 0.35 * t)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                if math.hypot(x, z) <= r:
                    w.setze(x, y, z, w.b("light_gray_terracotta") if (x + y) % 5 else w.b("gray_terracotta"))
    for k in range(int(6 + 2 * s)):
        a = k / (6 + 2 * s) * 2 * math.pi
        L = 3 + 3 * s
        pts = bez((0, H, 0), (math.cos(a) * L * 0.4, H + L * 0.5, math.sin(a) * L * 0.4),
                  (math.cos(a) * L, H + L * 0.6, math.sin(a) * L))
        stamm(w, pts, 0.8 + 0.2 * s, 0.35, lambda *_: w.b("light_gray_terracotta"), rauh=0.05)
        e = pts[-1]
        laubball(w, e[0], e[1] + 0.5, e[2], 1.2 + 0.5 * s, arten=("acacia_leaves", "oak_leaves"), dicht=0.6)
    return w


def faecherpalme(seed, g=2):
    """Fächerpalme: ein schlanker, geringelter Stamm trägt eine Kugel aus riesigen, runden Fächerblättern in Silber-
    blau, unten hängt ein Rock aus vertrockneten, braunen Wedeln."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    boden(w, s, art="strand")
    H = 8 + 5 * s
    for y in range(0, int(H)):
        r = 0.6 + 0.4 * s
        for x in range(-2, 3):
            for z in range(-2, 3):
                if math.hypot(x, z) <= r:
                    w.setze(x, y, z, w.b("stripped_spruce_log", axis="y") if y % 2 else w.b("spruce_log", axis="y"))
    for k in range(int(10 + 4 * s)):
        a = k / (10 + 4 * s) * 2 * math.pi
        el = 0.9 - (k % 3) * 0.5
        L = 2.5 + 1.5 * s
        base = (math.cos(a) * L * math.cos(el), H + math.sin(el) * L, math.sin(a) * L * math.cos(el))
        linie(w, (0, H, 0), base, w.b("green_terracotta"))
        n = (math.cos(a) * math.cos(el), math.sin(el), math.sin(a) * math.cos(el))
        bluete(w, base, n, 9, 1.4 * s + 0.8, 0.35 * s + 0.25, cup=0.1, farben=["green_concrete", "cyan_concrete",
                                                                              "lime_terracotta"])
    for k in range(10):
        a = k / 10 * 2 * math.pi
        linie(w, (0, H - 1, 0), (math.cos(a) * 1.8, H - 3 - s, math.sin(a) * 1.8), w.b("brown_terracotta"))
    return w


def saguarohain(seed, g=2):
    """Säulenkaktus-Hain: in einer roten Wüste stehen hohe, gerippte Säulenkakteen mit erhobenen Armen, manche mit
    weißen Blüten auf dem Scheitel, dazwischen Kugelkakteen, Steine und ausgeblichene Knochen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    R = int(10 * s + 6)
    zellen = wiese(w, R, huegel=0.3, art="strand", blumen=0.0)
    for (x, z), h in zellen.items():
        w.setze(x, h, z, w.b("red_sand") if rng.random() < 0.7 else w.b("terracotta"))
    for k in range(int(3 + 2 * s)):
        a = k * 2.4
        r = 0 if k == 0 else R * (0.3 + 0.4 * rng.random())
        x0, z0 = round(math.cos(a) * r), round(math.sin(a) * r)
        H = int((5 + rng.random() * 4) * s + 4)
        rr = 0.7 + 0.3 * s
        y0 = zellen.get((x0, z0), 0) + 1
        for y in range(y0, y0 + H):
            for x in range(-2, 3):
                for z in range(-2, 3):
                    if math.hypot(x, z) <= rr:
                        w.setze(x0 + x, y, z0 + z, w.b("green_concrete") if (x + z) % 2 else w.b("green_terracotta"))
        for j in range(int(1 + rng.random() * 2)):
            b = rng.random() * 6.28
            ya = y0 + int(H * (0.35 + 0.25 * rng.random()))
            L = 2 + s
            ex, ez = x0 + math.cos(b) * L, z0 + math.sin(b) * L
            linie(w, (x0, ya, z0), (ex, ya, ez), w.b("green_concrete"), 0.5 * s)
            linie(w, (ex, ya, ez), (ex, ya + H * 0.35, ez), w.b("green_concrete"), 0.5 * s)
        if k % 2 == 0:
            w.setze(x0, y0 + H, z0, w.b("white_wool"))
    for k in range(int(4 + 3 * s)):
        a = rng.random() * 6.28
        x, z = math.cos(a) * R * 0.7, math.sin(a) * R * 0.7
        kugel(w, x, 1, z, 0.8 + 0.3 * s, w.b("lime_terracotta"))
    w.setze(2, 1, 3, w.b("bone_block", axis="x"))
    return w


def aloegarten(seed, g=1):
    """Aloe-Garten: zwischen hellen Kieseln wachsen riesige Aloe-Rosetten mit dicken, gezähnten, graugrünen Blättern,
    aus denen lange Blütenstände mit orangeroten Röhrenblüten ragen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    zellen = boden(w, s, art="kies")
    for k in range(int(2 + s)):
        a = k * 2.2
        r = 0 if k == 0 else 4 * s
        x0, z0 = math.cos(a) * r, math.sin(a) * r
        rosette(w, (x0, 1, z0), 12, (2.5 + rng.random()) * s + 1, 0.5 * s + 0.3,
                ["cyan_terracotta", "light_gray_terracotta", "green_terracotta"], steig=1.0, haeng=0.4, rng=rng)
        H = int(5 * s + 4)
        linie(w, (x0, 1, z0), (x0 + 0.5, H, z0), w.b("brown_terracotta"))
        for y in range(int(H * 0.65), H + 1):
            for b in range(3):
                c = b / 3 * 2 * math.pi + y
                w.setze(round(x0 + 0.5 + math.cos(c) * 0.8), y, round(z0 + math.sin(c) * 0.8),
                        w.b("orange_concrete") if y < H - 1 else w.b("red_concrete"), False)
    return w


def agave(seed, g=2):
    """Agave mit Blütenschaft: eine riesige, blaugraue Agavenrosette mit spitzen, stacheligen Blättern, aus deren Mitte
    ein mastartiger Blütenschaft emporschießt, an dem waagrechte Äste goldgelbe Blütenbüschel tragen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    boden(w, s, art="kies")
    rosette(w, (0, 1, 0), 14, 4 * s + 2, 0.8 * s + 0.4, ["cyan_terracotta", "light_blue_terracotta",
                                                         "light_gray_terracotta"], steig=0.9, haeng=0.2, rng=rng)
    H = int(14 * s + 8)
    linie(w, (0, 1, 0), (0, H, 0), w.b("stripped_oak_log", axis="y"), 0.4 * s)
    for k in range(int(5 + 2 * s)):
        y = H * 0.45 + k * H * 0.5 / (5 + 2 * s)
        a = k * 2.4
        L = (2.5 - k * 0.2) * s + 1
        e = (math.cos(a) * L, y + 1, math.sin(a) * L)
        linie(w, (0, y, 0), e, w.b("stripped_oak_log", axis="y"))
        kugel(w, e[0], e[1] + 0.5, e[2], 0.8 + 0.3 * s, w.b("yellow_wool") if k % 2 else w.b("yellow_concrete"))
    return w


def fackelingwer(seed, g=1):
    """Fackelingwer: aus hohen Blattschäften mit langen, glänzenden Blättern erheben sich auf eigenen Stielen leuchtend
    rote, zapfenförmige Blüten aus wachsartigen Hochblättern – wie brennende Fackeln."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    boden(w, s)
    for k in range(int(4 + 2 * s)):
        a = k * 1.4
        r = (1.5 + rng.random() * 2) * s
        x0, z0 = math.cos(a) * r, math.sin(a) * r
        H = (6 + rng.random() * 3) * s + 3
        linie(w, (x0, 1, z0), (x0, H, z0), w.b("green_terracotta"))
        for j in range(4):
            blatt(w, (x0, H * (0.5 + j * 0.12), z0), a + j * 1.6, (3 + rng.random()) * s, 0.8 * s, steig=0.3,
                  haeng=0.6, farben=GRUEN, mitte="lime_concrete", form="lanze")
    for k in range(int(2 + s)):
        a = k * 2.3 + 0.7
        x0, z0 = math.cos(a) * 1.5 * s, math.sin(a) * 1.5 * s
        H = (4 + k) * s + 3
        linie(w, (x0, 1, z0), (x0, H, z0), w.b("lime_terracotta"))
        for lage in range(3):
            L = (1.6 - lage * 0.4) * s + 0.6
            bluete(w, (x0, H + lage * 0.6 * s, z0), (0, 1, 0), 8 + lage, L, L * 0.5, cup=0.9 + lage * 0.4,
                   farben=["red_concrete", "red_terracotta", "pink_concrete"], dreh=lage * 0.4)
        kugel(w, x0, H + 1.8 * s + 0.5, z0, 0.5 * s + 0.3, w.b("red_concrete"))
    return w


def riesenrhabarber(seed, g=2):
    """Riesenrhabarber: an einem Bachufer wachsen gigantische, rundliche, tief eingeschnittene Blätter auf stacheligen,
    rötlichen Stielen, so groß wie Schirme; dazwischen zapfenförmige Blütenkolben."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    zellen = boden(w, s)
    for (x, z), h in zellen.items():
        if abs(z - 4 * s - math.sin(x / 3)) < 1.3:
            w.setze(x, h, z, w.b("water", level=0))
            w.bloecke.pop((x, h + 1, z), None)
    for k in range(int(5 + 2 * s)):
        a = k / (5 + 2 * s) * 2 * math.pi
        L = (3 + rng.random()) * s + 2
        H = (2.5 + rng.random() * 2) * s + 1
        top = (math.cos(a) * L * 0.5, H, math.sin(a) * L * 0.5)
        linie(w, (0, 1, 0), top, w.b("red_terracotta"), 0.3 * s)
        blatt(w, top, a, L, L * 0.6, steig=0.2, haeng=0.5, farben=["green_concrete", "green_terracotta"],
              mitte="red_terracotta", form="rund", schlitze=5, kipp=0.2)
    for k in range(int(1 + s)):
        a = k * 2.5 + 0.3
        x, z = math.cos(a) * 1.2, math.sin(a) * 1.2
        for y in range(1, int(3 * s + 3)):
            r = max(0.4, (1 - y / (3 * s + 3)) * (0.9 + 0.3 * s))
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if math.hypot(dx, dz) <= r:
                        w.setze(round(x) + dx, y, round(z) + dz, w.b("brown_terracotta") if (dx + dz + y) % 2 else
                                w.b("red_terracotta"))
    return w


def schraubenbaum(seed, g=2):
    """Schraubenbaum: ein Baum, der auf schräg gestellten Stelzwurzeln über dem Sand steht, mit verzweigtem Stamm und
    spiralig angeordneten, langen Blattschöpfen und großen, ananasartigen Fruchtständen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    boden(w, s, art="strand")
    yb = int(2 + 2 * s)
    for k in range(int(6 + 2 * s)):
        a = k / (6 + 2 * s) * 2 * math.pi
        L = 2 + 1.5 * s
        linie(w, (math.cos(a) * L, 0, math.sin(a) * L), (0, yb + 1, 0), w.b("stripped_jungle_log", axis="y"),
              0.3 * s)
    H = yb + 4 + 4 * s
    stamm(w, bez((0, yb, 0), (0.5, H * 0.7, 0), (0, H, 0)), 0.7 + 0.3 * s, 0.5 + 0.2 * s, "jungle_log")
    for k in range(3):
        a = k * 2.1
        L = 2 + 2 * s
        e = (math.cos(a) * L, H + L * 0.6, math.sin(a) * L)
        stamm(w, bez((0, H, 0), (math.cos(a) * L * 0.5, H + L * 0.1, math.sin(a) * L * 0.5), e), 0.5 + 0.1 * s, 0.35,
              "jungle_log")
        rosette(w, e, 10, 2.2 * s + 1, 0.3 * s + 0.25, ["green_concrete", "lime_terracotta", "green_terracotta"],
                steig=0.8, haeng=0.9, rng=rng)
        kugel(w, e[0] + 0.5, e[1] - 1.2, e[2], 0.6 + 0.3 * s, w.b("orange_terracotta"))
    return w


def epiphytenbaum(seed, g=2):
    """Epiphytenbaum: ein moosbedeckter Urwaldriese, auf dessen breiten Ästen ganze Gärten wachsen – Bromelien in
    Rot und Gelb, Farne, Orchideen und Moospolster, von denen Luftwurzeln herabhängen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    boden(w, s)
    H = 10 + 5 * s
    enden = baum_aeste(w, 0, 0, H, 5 + g, 6 + 4 * s, "jungle", 1.3 + 0.5 * s, rng, steigung=0.2, start=0.45)
    for (x, y, z) in enden:
        laubball(w, x, y + 2, z, 2.5 + s, arten=("jungle_leaves", "oak_leaves"), dicht=0.7)
        for t in range(3):
            p = (x * (0.4 + 0.2 * t), H * (0.45 + 0.1 * t) + (y - H * 0.5) * 0.3 * t, z * (0.4 + 0.2 * t))
            w.setze(round(p[0]), round(p[1]) + 1, round(p[2]), w.b("moss_block"), False)
            r = rng.random()
            if r < 0.4:
                rosette(w, (p[0], p[1] + 2, p[2]), 6, 1.0 * s + 0.6, 0.35 * s + 0.2,
                        [["red_concrete", "red_terracotta", "lime_terracotta"],
                         ["yellow_concrete", "orange_concrete", "lime_terracotta"]][t % 2], steig=1.0, haeng=0.3,
                        rng=rng)
            elif r < 0.7:
                w.setze(round(p[0]), round(p[1]) + 2, round(p[2]), w.b("fern"), False)
            else:
                w.setze(round(p[0]), round(p[1]) + 2, round(p[2]), w.b("pink_wool"), False)
            for d in range(int(2 + rng.random() * 4 * s)):
                w.setze(round(p[0]) + 1, round(p[1]) - d, round(p[2]), w.b("brown_wool") if d % 3 else
                        w.b("hanging_roots", waterlogged=False), False)
    return w


def kokospalmen(seed, g=2):
    """Kokospalmen am Strand: drei elegant zum Meer geneigte Kokospalmen mit Nussbündeln über einem hellen Sandstrand,
    angespülte Nüsse, Treibholz und eine Hängematte zwischen zwei Stämmen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, huegel=0.1, art="strand", blumen=0.0)
    for (x, z), h in zellen.items():
        if z > R * 0.45:
            w.setze(x, h, z, w.b("water", level=0))
            w.setze(x, h - 1, z, w.b("sand"))
    pos = [(-int(R * 0.4), -int(R * 0.2)), (0, -int(R * 0.35)), (int(R * 0.35), -int(R * 0.1))]
    for k, (x, z) in enumerate(pos):
        einfuegen(w, wald2.palme(seed + k * 13, H=int(9 + 3 * s)), x, zellen.get((x, z), 0) + 1, z)
    for k in range(4):
        w.setze(-2 + k * 2, 1, int(R * 0.3), w.b("brown_terracotta"))
    for t in range(int(3 + s)):
        w.setze(int(R * 0.1) + t, 1, int(R * 0.2), w.b("stripped_oak_log", axis="x"))
    (ax, az), (bx, bz) = pos[0], pos[1]
    n = abs(bx - ax) + abs(bz - az)
    for k in range(1, max(2, n)):
        t = k / n
        x, z = round(ax + (bx - ax) * t), round(az + (bz - az) * t)
        w.setze(x, 3 - round(math.sin(t * math.pi) * 1), z, w.b("white_wool") if k % 2 else w.b("orange_wool"), False)
    return w


def schachtelhalmwald(seed, g=2):
    """Schachtelhalm-Urwald: ein Wald aus baumhohen, gegliederten Schachtelhalmen mit quirlständigen Nadelwirteln an
    jedem Knoten, wie in der Urzeit; dazwischen Riesenfarne, Moos und ein dampfender Tümpel."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    R = int(10 * s + 6)
    zellen = wiese(w, R, huegel=0.2, art="moor")
    for k in range(int(8 + 6 * s)):
        a = rng.random() * 6.28
        r = rng.random() * R * 0.85
        x0, z0 = round(math.cos(a) * r), round(math.sin(a) * r)
        H = int((5 + rng.random() * 5) * s + 4)
        y0 = zellen.get((x0, z0), 0) + 1
        for y in range(y0, y0 + H):
            knoten = (y - y0) % 3 == 0
            w.setze(x0, y, z0, w.b("lime_terracotta") if knoten else w.b("green_concrete"))
            if knoten and y > y0 + 1:
                for b in range(8):
                    c = b / 8 * 2 * math.pi
                    L = 1 + (1 - (y - y0) / H) * 1.5 * s
                    linie(w, (x0, y, z0), (x0 + math.cos(c) * L, y - 0.6, z0 + math.sin(c) * L),
                          w.b("green_terracotta"))
        w.setze(x0, y0 + H, z0, w.b("brown_terracotta"))
    for k in range(int(3 + 2 * s)):
        a = rng.random() * 6.28
        x, z = math.cos(a) * R * 0.5, math.sin(a) * R * 0.5
        rosette(w, (x, zellen.get((round(x), round(z)), 0) + 1, z), 6, 2.5 * s + 1, 0.6 * s, GRUEN, steig=0.9,
                haeng=0.7, form="lanze", rng=rng)
    return w


def bougainvillea(seed, g=1):
    """Bougainvillea-Mauer: eine weiß gekalkte Gartenmauer mit Rundbogentor, über die sich eine üppige Bougainvillea in
    leuchtendem Magenta und Orange ergießt, Blütenblätter liegen auf den Terrakottafliesen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    R = int(8 * s + 6)
    zellen = wiese(w, R, huegel=0.0, blumen=0.0)
    L = int(R * 0.8)
    Hm = int(4 + 2 * s)
    for x in range(-L, L + 1):
        for y in range(1, Hm + 1):
            tor = abs(x) <= 1 and (y < Hm - 1 or (y == Hm - 1 and abs(x) == 0))
            if not tor:
                w.setze(x, y, 0, w.b("white_concrete") if (x + y) % 6 else w.b("white_terracotta"))
        w.setze(x, Hm + 1, 0, w.b("smooth_sandstone_slab", type="bottom", waterlogged=False))
        for z in range(1, 5):
            w.setze(x, 0, z, w.b("terracotta") if (x + z) % 2 else w.b("orange_terracotta"))
    for k in range(int(80 * s + 40)):
        x = round((rng.random() - 0.5) * 2 * L)
        y = round(Hm + 1 - rng.random() ** 2 * Hm)
        z = 1 if rng.random() < 0.6 else -1
        if abs(x) <= 1 and y < Hm:
            continue
        w.setze(x, y, z, w.b("magenta_concrete") if rng.random() < 0.6 else w.b("pink_wool") if rng.random() < 0.6
                else w.b("orange_wool"), False)
        if rng.random() < 0.3:
            w.setze(x, y + 1 if y < Hm + 1 else y, 0 if y > Hm else z, w.b("jungle_leaves", persistent=True,
                                                                           distance=1, waterlogged=False), False)
    for k in range(int(5 + 3 * s)):
        w.setze(round((rng.random() - 0.5) * 2 * L), 1, 1 + int(rng.random() * 3), w.b("pink_carpet"), False)
    return w


def feigenkaktus(seed, g=1):
    """Feigenkaktus: ein ausladender Kaktus aus übereinander gewachsenen, ovalen Flachgliedern, besetzt mit gelben
    Blüten und roten Kaktusfeigen an den Rändern, auf trockenem Hang mit Steinen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    boden(w, s, art="kies")

    def glied(c, a, kipp, r):
        e1 = (math.cos(a), 0, math.sin(a))
        for i in range(-int(r * 1.2) - 1, int(r * 1.2) + 2):
            for j in range(-int(r * 1.6) - 1, int(r * 1.6) + 2):
                if (i / (r * 1.0)) ** 2 + (j / (r * 1.4)) ** 2 <= 1:
                    p = (c[0] + e1[0] * i + math.sin(kipp) * j * e1[0] * 0.2, c[1] + j * math.cos(kipp),
                         c[2] + e1[2] * i + math.sin(kipp) * j)
                    w.setze(round(p[0]), round(p[1]), round(p[2]), w.b("lime_terracotta") if (i + j) % 4 else
                            w.b("green_concrete"))
        top = (c[0], c[1] + r * 1.4 * math.cos(kipp), c[2] + r * 1.4 * math.sin(kipp))
        return top

    stufen = [((0, 1 + 1.4 * s, 0), 0.0, 0.0)]
    r = 1.2 + 0.6 * s
    for gen in range(int(2 + s)):
        neu = []
        for (c, a, k) in stufen:
            top = glied(c, a, k, r)
            if gen < int(1 + s):
                for b in (-0.6, 0.7):
                    neu.append(((top[0] + math.cos(a + b) * r * 0.5, top[1] + r, top[2] + math.sin(a + b) * r * 0.5),
                                a + b * 1.5, b * 0.4))
            else:
                w.setze(round(top[0]), round(top[1]) + 1, round(top[2]),
                        w.b("yellow_wool") if rng.random() < 0.5 else w.b("red_terracotta"))
        stufen = neu
    return w


def flaschenbaum(seed, g=2):
    """Flaschenbaum: ein Baum mit einem bauchigen, grün gestreiften Flaschenstamm, aus dessen Hals sich wenige Äste
    mit feinem, hellgrünem Laub und rosa Blütenwolken verzweigen, in einem steinigen Trockengarten."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    boden(w, s, art="kies")
    H = 6 + 4 * s
    rb = 1.8 + 1.2 * s
    for y in range(0, int(H)):
        t = y / H
        r = rb * (0.5 + 1.2 * math.sin(math.pi * min(1, t * 1.3)) ** 0.7) * (1 - 0.6 * t) + 0.4
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                if math.hypot(x, z) <= r:
                    w.setze(x, y, z, w.b("lime_terracotta") if (math.atan2(z, x) * 4) % 2 < 1 else
                            w.b("green_terracotta"))
    for k in range(int(4 + 2 * s)):
        a = k / (4 + 2 * s) * 2 * math.pi
        L = 3 + 2 * s
        e = (math.cos(a) * L, H + L * 0.6, math.sin(a) * L)
        stamm(w, bez((0, H, 0), (math.cos(a) * L * 0.3, H + L * 0.4, math.sin(a) * L * 0.3), e), 0.45, 0.3,
              lambda *_: w.b("green_terracotta"), rauh=0.0)
        laubball(w, e[0], e[1] + 0.5, e[2], 1.5 + 0.6 * s, arten=("flowering_azalea_leaves", "cherry_leaves",
                                                                  "azalea_leaves"), dicht=0.7)
    return w


def regenbaum(seed, g=2):
    """Regenbaum: ein mächtiger Baum mit kurzem Stamm und einer extrem breiten, flachen Schirmkrone aus feinem
    Fiederlaub mit rosa Pinselblüten, deren Schatten eine ganze Wiese mit Bänken bedeckt."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    zellen = boden(w, s, R=int(11 * s + 6), blumen=0.03)
    H = 5 + 3 * s
    enden = baum_aeste(w, 0, 0, H, 7 + g, 7 + 5 * s, "oak", 1.2 + 0.5 * s, rng, steigung=0.25, start=0.55)
    for (x, y, z) in enden:
        for j in range(3):
            dx, dz = (rng.random() - 0.5) * 3, (rng.random() - 0.5) * 3
            for xx in range(-3, 4):
                for zz in range(-3, 4):
                    if xx * xx + zz * zz <= (2.2 + s) ** 2 and rng.random() < 0.8:
                        w.setze(round(x + dx + xx), round(y + 1 + (xx * xx + zz * zz) * -0.05), round(z + dz + zz),
                                w.b("oak_leaves", persistent=True, distance=1, waterlogged=False)
                                if rng.random() > 0.08 else w.b("pink_wool"), False)
    for k in range(3):
        a = k * 2.1 + 0.4
        x, z = round(math.cos(a) * 4 * s), round(math.sin(a) * 4 * s)
        w.setze(x, zellen.get((x, z), 0) + 1, z, w.b("oak_stairs", facing="north", half="bottom", shape="straight",
                                                    waterlogged=False))
    return w


def wasserhyazinthen(seed, g=1):
    """Wasserhyazinthen-Teich: ein stiller Tropenteich, dessen Oberfläche dicht mit schwimmenden Rosetten aus
    glänzenden, aufgeblähten Blättern bedeckt ist, aus denen lavendelblaue Blütenähren ragen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    R = int(9 * s + 6)
    zellen = wiese(w, R, huegel=0.1)
    for (x, z), h in zellen.items():
        if math.hypot(x, z) < R * 0.75:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("water", level=0))
            w.setze(x, -2, z, w.b("mud"))
            w.bloecke.pop((x, 1, z), None)
    for k in range(int(10 + 8 * s)):
        a = rng.random() * 6.28
        r = rng.random() * R * 0.68
        x, z = math.cos(a) * r, math.sin(a) * r
        rosette(w, (x, 1, z), 6, 0.9 * s + 0.6, 0.45 * s + 0.3, ["green_concrete", "lime_concrete"], steig=0.6,
                haeng=0.2, form="rund", rng=rng)
        if rng.random() < 0.5:
            for y in range(2, int(2 + 1.5 * s) + 1):
                w.setze(round(x), y, round(z), w.b("light_blue_wool") if y % 2 else w.b("purple_wool"))
    return w


def tillandsienvorhang(seed, g=2):
    """Tillandsienvorhang: von den waagrechten Ästen eines alten Baumes hängen lange, silbergraue Bärte aus
    Tillandsien wie Vorhänge herab, durchsetzt mit kleinen rosa Blüten."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    boden(w, s, R=int(10 * s + 6))
    H = 6 + 4 * s
    enden = baum_aeste(w, 0, 0, H, 6 + g, 6 + 4 * s, "dark_oak", 1.1 + 0.4 * s, rng, steigung=0.1, start=0.6)
    for (x, y, z) in enden:
        laubball(w, x, y + 1.5, z, 1.5 + 0.6 * s, arten=("oak_leaves",), dicht=0.6)
        for t in range(int(6 + 4 * s)):
            q = rng.random()
            px, pz = x * q, z * q
            py = H * 0.6 + (y - H * 0.6) * q
            L = int(2 + rng.random() * 4 * s)
            for d in range(L):
                w.setze(round(px), round(py) - 1 - d, round(pz), w.b("light_gray_wool") if d % 4 else
                        w.b("white_wool") if rng.random() < 0.8 else w.b("pink_wool"), False)
    return w


def jadewein(seed, g=2):
    """Jadewein-Laube: über einer Pergola aus Bambus hängt eine Kletterpflanze mit unzähligen, krallenförmigen Blüten
    in einem leuchtenden Jade-Türkis, in langen Trauben zum Boden hin."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    boden(w, s, R=int(8 * s + 5))
    A = int(3 + 2 * s)
    H = int(4 + 1.5 * s)
    for sx in (-A, A):
        for sz in (-A, A):
            for y in range(1, H + 1):
                w.setze(sx, y, sz, w.b("bamboo_block", axis="y"))
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            if x % 2 == 0 or z in (-A, A):
                w.setze(x, H + 1, z, w.b("bamboo_block", axis="x"))
            if rng.random() < 0.3:
                w.setze(x, H + 2, z, w.b("jungle_leaves", persistent=True, distance=1, waterlogged=False), False)
            if rng.random() < 0.3:
                L = int(1 + rng.random() * (H - 1))
                for d in range(L):
                    w.setze(x, H - d, z, w.b("cyan_concrete") if d % 2 else w.b("light_blue_terracotta")
                            if rng.random() < 0.5 else w.b("cyan_terracotta"), False)
    return w


def seidenbaum(seed, g=2):
    """Seidenbaum: ein Baum mit flaschengrünem, von dicken Dornen besetztem Stamm, dessen kahle Krone voller großer,
    rosafarbener Blüten steht, aus deren Fruchtkapseln weiße Seidenwolle quillt."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    boden(w, s, R=int(9 * s + 6))
    H = 8 + 4 * s
    rb = 1.2 + 0.6 * s
    for y in range(0, int(H * 0.6)):
        r = rb * (1.2 - 0.4 * y / H)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(x, z)
                if d <= r:
                    w.setze(x, y, z, w.b("green_terracotta") if (x + y) % 3 else w.b("lime_terracotta"))
                elif d <= r + 1 and rng.random() < 0.06:
                    w.setze(x, y, z, w.b("pointed_dripstone", vertical_direction="up", thickness="tip",
                                         waterlogged=False), False) if False else \
                        w.setze(x, y, z, w.b("brown_terracotta"), False)
    enden = baum_aeste(w, 0, 0, H, 5 + g, 4 + 3 * s, "jungle", 0.8 + 0.3 * s, rng, steigung=0.5, start=0.55)
    for (x, y, z) in enden:
        for k in range(int(3 + s)):
            c = (x + (rng.random() - 0.5) * 3, y + rng.random() * 1.5, z + (rng.random() - 0.5) * 3)
            L = 0.9 * s + 0.6
            bluete(w, c, (0, 1, 0), 5, L, L * 0.4, cup=0.4, farben=["pink_concrete", "pink_wool", "magenta_wool"],
                   innen="white_wool")
        kugel(w, x + 1, y - 1, z, 0.7 + 0.2 * s, w.b("white_wool"))
    return w


FLORA3 = {
    "drachenbaum": ("Drachenbaum", drachenbaum),
    "baobab": ("Affenbrotbaum", baobab),
    "faecherpalme": ("Fächerpalme", faecherpalme),
    "saguarohain": ("Säulenkaktus-Hain", saguarohain),
    "aloegarten": ("Aloe-Garten", aloegarten),
    "agave": ("Agave mit Blütenschaft", agave),
    "fackelingwer": ("Fackelingwer", fackelingwer),
    "riesenrhabarber": ("Riesenrhabarber", riesenrhabarber),
    "schraubenbaum": ("Schraubenbaum", schraubenbaum),
    "epiphytenbaum": ("Epiphytenbaum", epiphytenbaum),
    "kokospalmen": ("Kokospalmen am Strand", kokospalmen),
    "schachtelhalmwald": ("Schachtelhalm-Urwald", schachtelhalmwald),
    "bougainvillea": ("Bougainvillea-Mauer", bougainvillea),
    "feigenkaktus": ("Feigenkaktus", feigenkaktus),
    "flaschenbaum": ("Flaschenbaum", flaschenbaum),
    "regenbaum": ("Regenbaum", regenbaum),
    "wasserhyazinthen": ("Wasserhyazinthen-Teich", wasserhyazinthen),
    "tillandsienvorhang": ("Tillandsienvorhang", tillandsienvorhang),
    "jadewein": ("Jadewein-Laube", jadewein),
    "seidenbaum": ("Seidenbaum", seidenbaum),
}

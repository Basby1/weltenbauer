"""Pilzwelten II – zwanzig weitere Pilzbauten und Pilzarten: Pilzleuchtturm, Pilzmühle, Baumschwamm-Treppe,
Pilzkarussell, Pilzbäckerei, Pilzschloss, Schneckenweide, Sporenlabor, Pilzpagode, Trüffelgarten, Bovist-Siedlung,
Pilz-Teehaus, Pilzlaternen-Allee, Pilzfelsen, Tintenfischpilz, Krause Glucke, Rotkappe, Lila Lacktrichter,
Pilzbaumhaus und Pilzgondel."""

from __future__ import annotations

import math

from erw_basis import M, S, figur, hoehe, wiese
from erw_markt import mensch
from feinbau import laterne
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen
from pilze import hut, kleine, pblk, stiel
from skulptur import ell, kap


def pilzboden(w, R, myzel=0.3):
    zellen = wiese(w, R, huegel=0.25, art="wald")
    rn = Rauschen(w, 3)
    for (x, z), h in zellen.items():
        if rn(x, 4, z) < myzel:
            w.setze(x, h, z, w.b("mycelium", snowy=False))
            w.bloecke.pop((x, h + 1, z), None)
    kleine(w, int(R * 1.5), R * 0.9, w.rng)
    return zellen


def fenster_rund(w, cx, y, cz, r, n=4, glas="yellow_stained_glass"):
    for k in range(n):
        a = k / n * 2 * math.pi + 0.4
        w.setze(round(cx + math.cos(a) * r), y, round(cz + math.sin(a) * r), w.b(glas))


def tuer_rund(w, cx, y, cz, r, a):
    x, z = round(cx + math.cos(a) * r), round(cz + math.sin(a) * r)
    for yy in (y, y + 1):
        w.setze(x, yy, z, w.b("spruce_planks") if yy == y + 1 else w.b("brown_wool"))
    return x, z


# ============================================================================ Bauten

def pilzleuchtturm(seed, g=2):
    """Pilzleuchtturm: ein hoher, schlanker Pilz mit rot-weiß geringeltem Stiel steht auf einem Uferfelsen; unter seinem
    Hut sitzt eine verglaste Laterne mit Leuchtpilzen, eine Wendeltreppe windet sich um den Stiel."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = pilzboden(w, R, 0.15)
    for (x, z), h in zellen.items():
        if z > R * 0.25:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("sand"))
            for y in range(1, 3):
                w.bloecke.pop((x, y, z), None)
    kugel(w, 0, 0, 0, 3 + s, w.b("mossy_cobblestone"), ry=2)
    H = int(12 * s + 8)
    r = 1.5 + 0.5 * s
    top = stiel(w, 0, 0, 2, H, r + 0.4, r, mat=lambda x, y, z: "red_mushroom_block" if (y // 3) % 2 else
                "mushroom_stem")
    for y in range(top[1], top[1] + 3):
        for x in range(-2, 3):
            for z in range(-2, 3):
                if max(abs(x), abs(z)) == 2:
                    w.setze(x, y, z, w.b("glass"))
                elif (x, z) == (0, 0):
                    w.setze(x, y, z, w.b("shroomlight"))
    hut(w, 0, top[1] + 3, 0, 4 + 1.5 * s, 2 + s, form="kuppel", farbe="red_mushroom_block", punkte="white_wool")
    for k in range(H * 3):
        a = k * 0.4
        y = 2 + k // 3
        if y >= top[1]:
            break
        w.setze(round(math.cos(a) * (r + 1.6)), y, round(math.sin(a) * (r + 1.6)), w.b("spruce_slab", type="top",
                                                                                     waterlogged=False), False)
    return w


def pilzmuehle(seed, g=1):
    """Pilzmühle: eine runde Mühle mit dickem Pilzstiel als Turm und braunem Hut als Dach, an dem vier Flügel aus
    Lamellenblättern sitzen; Mehlsäcke und ein Karren mit Sporenkorn stehen davor."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    pilzboden(w, R, 0.2)
    H = int(6 * s + 6)
    r = 2.5 + s
    top = stiel(w, 0, 0, 1, H, r + 0.5, r, mat="mushroom_stem")
    for y in range(2, H, 3):
        fenster_rund(w, 0, y, 0, r + 0.3, 4)
    tuer_rund(w, 0, 1, 0, r + 0.5, math.pi / 2)
    hut(w, 0, top[1], 0, r + 2.5, 2 + s, form="polster", farbe="brown_mushroom_block", lamellen="white_terracotta")
    hy = top[1] - 1
    hz = round(r + 3)
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.3
        for t in range(1, int(4 + 3 * s)):
            for q in (0, 1):
                x = round(math.cos(a) * t - math.sin(a) * q)
                y = round(hy + math.sin(a) * t + math.cos(a) * q)
                w.setze(x, y, hz, w.b("white_wool") if q else w.b("mushroom_stem", **{k2: True for k2 in
                                                                                      ("north", "south", "east",
                                                                                       "west", "up", "down")}),
                        False)
    w.setze(0, hy, hz - 1, w.b("brown_mushroom_block", **{k2: True for k2 in ("north", "south", "east", "west",
                                                                              "up", "down")}))
    for k in range(3):
        w.setze(round(r) + 3, 1, -1 + k, w.b("white_wool"))
    return w


def baumschwammtreppe(seed, g=2):
    """Baumschwamm-Treppe: um einen uralten, abgestorbenen Riesenstamm wachsen Konsolenpilze in einer Spirale wie
    Treppenstufen hinauf zu einer Plattform im hohlen Wipfel."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    pilzboden(w, R, 0.25)
    H = int(14 * s + 8)
    r = 2.5 + 0.8 * s
    rohr(w, bez((0, -1, 0), (0.5, H * 0.5, 0.3), (0, H, 0)), r, r * 0.8, M(w, [("dark_oak_wood", 2),
                                                                                  ("stripped_dark_oak_wood", 1)],
                                                                            axis="y"), rauh=0.25)
    for x in range(-int(r), int(r) + 1):
        for z in range(-int(r), int(r) + 1):
            if math.hypot(x, z) < r - 1.2:
                for y in range(H - 3, H + 2):
                    w.bloecke.pop((x, y, z), None)
                w.setze(x, H - 3, z, w.b("moss_block"))
    for k in range(int(H / 1.2)):
        a = k * 0.7
        y = 1 + round(k * 1.2)
        cx, cz = math.cos(a) * (r + 1.2), math.sin(a) * (r + 1.2)
        rk = 1.3 + 0.3 * s
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                px, pz = cx + dx, cz + dz
                if math.hypot(dx, dz) <= rk and math.hypot(px, pz) > r - 0.5:
                    w.setze(round(px), y, round(pz), w.b("brown_mushroom_block", **{k2: True for k2 in
                                                                                    ("north", "south", "east",
                                                                                     "west", "up", "down")})
                            if (dx + dz) % 3 else w.b("orange_terracotta"), False)
    for dx in range(-int(r) - 1, int(r) + 2):
        for dz in range(-int(r) - 1, int(r) + 2):
            if r - 0.5 < math.hypot(dx, dz) <= r + 0.6 and (dx + dz) % 2 == 0:
                w.setze(dx, H + 1, dz, w.b("dark_oak_fence"))
    return w


def pilzkarussell(seed, g=1):
    """Pilzkarussell: ein Jahrmarktkarussell, dessen Dach ein großer, rot gepunkteter Pilzhut ist; an Stangen hängen
    kleine Pilzsitze und Schnecken zum Reiten, Lampions schmücken den Rand."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    pilzboden(w, R, 0.1)
    rr = 3.5 + 1.5 * s
    for x in range(-int(rr) - 1, int(rr) + 2):
        for z in range(-int(rr) - 1, int(rr) + 2):
            d = math.hypot(x, z)
            if d <= rr:
                w.setze(x, 1, z, w.b("red_wool") if int(math.atan2(z, x) * 8 / math.pi) % 2 else w.b("white_wool"))
    H = int(5 + 2 * s)
    top = stiel(w, 0, 0, 2, H, 1.2, 1.0, mat="mushroom_stem")
    hut(w, 0, top[1], 0, rr + 1, 2 + s, form="kuppel", farbe="red_mushroom_block", punkte="white_wool")
    n = int(6 + 2 * s)
    for k in range(n):
        a = k / n * 2 * math.pi
        x, z = round(math.cos(a) * (rr - 1)), round(math.sin(a) * (rr - 1))
        for y in range(3, top[1]):
            w.setze(x, y, z, w.b("gold_block") if y == top[1] - 1 else w.b("iron_bars", north=False, south=False,
                                                                            east=False, west=False,
                                                                            waterlogged=False))
        if k % 2:
            w.setze(x, 2, z, w.b("red_mushroom_block", north=True, south=True, east=True, west=True, up=True,
                                 down=True))
        else:
            w.setze(x, 2, z, w.b("yellow_wool"))
            w.setze(x, 3, z, w.b("brown_terracotta"))
    for k in range(int(10 + 4 * s)):
        a = k / (10 + 4 * s) * 2 * math.pi
        x, z = round(math.cos(a) * (rr + 1)), round(math.sin(a) * (rr + 1))
        w.setze(x, top[1] - 1, z, w.b("lantern", hanging=True, waterlogged=False), False)
    return w


def pilzbaeckerei(seed, g=1):
    """Pilzbäckerei: ein gemütliches Haus im Stiel eines dicken Steinpilzes mit rundem Fenster, Backofen-Kamin aus Ziegeln,
    Auslage mit Kuchen und Broten unter einer Markise und einem Sitzplatz aus kleinen Pilzhockern."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    pilzboden(w, R, 0.15)
    r = 3 + s
    H = int(4 + 2 * s)
    top = stiel(w, 0, 0, 1, H, r + 0.8, r, mat="white_terracotta", knolle=1.0)
    fenster_rund(w, 0, 2, 0, r + 0.7, 5)
    tuer_rund(w, 0, 1, 0, r + 1, math.pi / 2)
    hut(w, 0, top[1], 0, r + 3, 3 + s, form="polster", farbe="brown_mushroom_block", lamellen="light_gray_terracotta")
    kx = round(r) + 1
    for y in range(1, top[1] + 4):
        w.setze(kx, y, -1, w.b("bricks"))
    w.setze(kx, top[1] + 4, -1, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for x in range(-2, 3):
        w.setze(x, 1, round(r) + 3, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x, 2, round(r) + 3, w.b("cake", bites=0) if x % 2 else w.b("hay_block", axis="x"))
        w.setze(x, 4, round(r) + 3, w.b("red_wool") if x % 2 else w.b("white_wool"))
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.5
        x, z = round(math.cos(a) * (R * 0.6)), round(math.sin(a) * (R * 0.6) + 2)
        w.setze(x, 1, z, w.b("mushroom_stem", north=True, south=True, east=True, west=True, up=True, down=True))
        w.setze(x, 2, z, w.b("red_mushroom_block", north=True, south=True, east=True, west=True, up=True, down=True))
    return w


def pilzschloss(seed, g=2):
    """Pilzschloss: eine Burg aus mehreren unterschiedlich hohen Pilztürmen – rote, braune und violette Hüte als
    Turmhauben – verbunden durch Mauern aus Stielmasse mit Zinnen und einem Tor."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    pilzboden(w, R, 0.2)
    A = int(R * 0.5)
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            if max(abs(x), abs(z)) == A and not (z == A and abs(x) <= 1):
                for y in range(1, int(4 + 2 * s)):
                    w.setze(x, y, z, pblk(w, "mushroom_stem"))
                if (x + z) % 2 == 0:
                    w.setze(x, int(4 + 2 * s), z, pblk(w, "mushroom_stem"))
    farben = ["red_mushroom_block", "brown_mushroom_block", "purple_terracotta", "red_mushroom_block"]
    for k, (sx, sz) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        H = int((6 + 3 * (k % 2)) * s + 6)
        top = stiel(w, sx * A, sz * A, 1, H, 2 + 0.5 * s, 1.6 + 0.4 * s, mat="mushroom_stem")
        for y in range(3, H, 4):
            fenster_rund(w, sx * A, y, sz * A, 2 + 0.4 * s, 3)
        hut(w, sx * A, top[1], sz * A, 3 + s, 3 + s, form="kegel" if k % 2 else "kuppel", farbe=farben[k],
            punkte="white_wool" if farben[k] == "red_mushroom_block" else None)
    H = int(10 * s + 10)
    top = stiel(w, 0, -2, 1, H, 3 + s, 2.5 + 0.8 * s, mat="mushroom_stem")
    hut(w, 0, top[1], -2, 5 + 2 * s, 4 + s, form="kuppel", farbe="red_mushroom_block", punkte="white_wool")
    for y in range(3, H, 4):
        fenster_rund(w, 0, y, -2, 3 + s, 5)
    return w


def schneckenweide(seed, g=1):
    """Schneckenweide: zwischen großen Pilzen weiden riesige Schnecken mit gewundenen, bunten Häusern auf einer
    feuchten Moosweide, ein Schneckenhirte mit Laterne und ein Unterstand aus Pilzhüten."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = pilzboden(w, R, 0.1)
    rng = w.rng
    farben = [("orange_terracotta", "yellow_terracotta"), ("light_blue_terracotta", "white_terracotta"),
              ("pink_terracotta", "magenta_terracotta"), ("lime_terracotta", "green_terracotta")]
    for k in range(int(3 + 2 * s)):
        a = rng.random() * 6.28
        r = R * (0.2 + rng.random() * 0.6)
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        y = zellen.get((x, z), 0) + 1
        f1, f2 = farben[k % 4]
        u = 0.35 * s + 0.3
        teile = [(kap((-2.4, 0.6, 0), (2.4, 0.6, 0), 0.7, 0.5), w.b("light_gray_terracotta")),
                 (kap((2.2, 0.8, 0), (2.8, 2.4, 0), 0.45), w.b("light_gray_terracotta")),
                 (kap((2.8, 2.2, 0.25), (3.0, 3.2, 0.4), 0.1), w.b("light_gray_terracotta")),
                 (kap((2.8, 2.2, -0.25), (3.0, 3.2, -0.4), 0.1), w.b("light_gray_terracotta"))]
        for j in range(12):
            t = j / 11
            rr = 1.8 * (1 - t * 0.75)
            b = t * 4 * math.pi
            teile.append((ell(-0.3 + math.cos(b) * rr * 0.6, 2.6 + math.sin(b) * rr * 0.6, 0, 0.7 * (1 - t * 0.5),
                              0.7 * (1 - t * 0.5), 0.9 * (1 - t * 0.5)), w.b(f1 if j % 2 else f2)))
        figur(w, u, teile, (-3, -1, -2), (4, 5, 2), pos=(x, y, z), winkel=a)
    for k in range(int(2 + s)):
        a = k * 2.5
        x, z = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        top = stiel(w, x, z, 1, int(5 + 2 * s), 1.0, 0.8)
        hut(w, x, top[1], z, 2.5 + s, 1.5 + s * 0.5, form="kuppel", farbe="brown_mushroom_block")
    figur(w, 0.28 * s + 0.22, mensch(w, "green_wool"), (-2, -1, -2), (2, 6, 2), pos=(1, 1, 1), winkel=0.5)
    return w


def sporenlabor(seed, g=2):
    """Sporenlabor: ein Forscherhaus aus Glas und Kupfer zwischen Riesenpilzen, mit Sporenfängern auf Masten,
    Kulturbecken voller Leuchtpilze, Destillierkolben und einer Röhre, die Sporen vom Hut eines Pilzes saugt."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    pilzboden(w, R, 0.3)
    A, B = int(3 + 1.5 * s), int(2 + s)
    for x in range(-A, A + 1):
        for z in range(-B, B + 1):
            w.setze(x, 0, z, w.b("waxed_cut_copper"))
            if max(abs(x) / A, abs(z) / B) >= 1:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("waxed_cut_copper") if abs(x) == A and abs(z) == B else w.b("glass"))
            w.setze(x, 4, z, w.b("waxed_cut_copper_slab", type="bottom", waterlogged=False))
    for k in range(int(2 + s)):
        w.setze(-A + 1 + k * 2, 1, -B + 1, w.b("brewing_stand", has_bottle_0=True, has_bottle_1=True,
                                               has_bottle_2=False))
    px, pz = A + 5, 0
    top = stiel(w, px, pz, 1, int(8 * s + 6), 1.5 + 0.4 * s, 1.2)
    hut(w, px, top[1], pz, 4 + 1.5 * s, 2 + s, form="kuppel", farbe="purple_terracotta", punkte="shroomlight")
    from steampunk2 import zylinder
    zylinder(w, (A, 3, 0), (px - 1, top[1] - 1, pz), 0.6, w.b("waxed_cut_copper"))
    for k in range(3):
        x, z = -A - 3, -2 + k * 2
        for y in range(1, int(5 + 2 * s)):
            w.setze(x, y, z, w.b("lightning_rod", facing="up", powered=False, waterlogged=False) if y > 1 else
                    w.b("waxed_cut_copper"))
    for x in range(-2, 3):
        for z in range(B + 2, B + 5):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("mycelium", snowy=False))
            if (x + z) % 2:
                w.setze(x, 1, z, w.b("shroomlight")) if False else None
    return w


def pilzpagode(seed, g=2):
    """Pilzpagode: ein Turm aus übereinandergestapelten, nach oben kleiner werdenden Pilzhüten auf einem gemeinsamen
    Stiel, jede Etage mit hängenden Laternen und Balkonen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    pilzboden(w, R, 0.2)
    n = int(3 + 1.5 * s)
    y = 1
    for k in range(n):
        rk = (n - k) * (1.2 + 0.4 * s) + 1.5
        H = int(3 + s)
        top = stiel(w, 0, 0, y, H, 1.4 + 0.3 * s, 1.2 + 0.3 * s, mat="mushroom_stem")
        y = hut(w, 0, top[1], 0, rk, 1.5 + 0.5 * s, form="flach", farbe=["red_mushroom_block",
                                                                         "brown_mushroom_block"][k % 2],
                lamellen="white_terracotta", dicke=1)
        for j in range(4):
            a = j / 4 * 2 * math.pi + k * 0.4
            w.setze(round(math.cos(a) * (rk - 0.5)), top[1] - 1, round(math.sin(a) * (rk - 0.5)),
                    w.b("lantern", hanging=True, waterlogged=False), False)
        y = top[1] + 1
    w.setze(0, y + 1, 0, w.b("shroomlight"))
    return w


def trueffelgarten(seed, g=1):
    """Trüffelgarten: ein Hain aus alten Eichen, unter denen Trüffelschweine mit ihrem Sucher den Boden durchwühlen;
    aufgegrabene Erdlöcher, Körbe mit schwarzen Knollen und ein Gatter."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, huegel=0.2, art="wald")
    from erw_basis import baum
    for k in range(int(3 + s)):
        a = k / (3 + s) * 2 * math.pi + 0.3
        x, z = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        baum(w, x, zellen.get((x, z), 0) + 1, z, seed + k, 7 + 2 * s)
    rng = w.rng
    for k in range(int(6 + 4 * s)):
        a = rng.random() * 6.28
        r = rng.random() * R * 0.5
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        h = zellen.get((x, z), 0)
        w.setze(x, h, z, w.b("rooted_dirt"))
        w.setze(x, h + 1, z, w.b("coarse_dirt"))
        if k % 3 == 0:
            w.setze(x + 1, h + 1, z, w.b("black_concrete_powder"))
    from erw_bauernhof import tier
    schwein = tier(w, "pink_wool", kopf="pink_wool", beine="pink_terracotta", L=1.4, hals=0.0)
    for k in range(int(2 + s)):
        x, z = -2 + k * 3, 1 - k
        figur(w, 0.3 * s + 0.25, schwein, (-3, -1, -2), (4, 5, 2), pos=(x, zellen.get((x, z), 0) + 1, z),
              winkel=k * 1.3)
    figur(w, 0.3 * s + 0.25, mensch(w, "brown_wool"), (-2, -1, -2), (2, 6, 2), pos=(2, 1, 3), winkel=2.0)
    w.setze(3, 1, 4, w.b("barrel", facing="up", open=True))
    return w


def bovistsiedlung(seed, g=2):
    """Bovist-Siedlung: ein Dorf aus kugelrunden Riesenbovisten, ausgehöhlt zu Wohnhäusern mit runden Türen, kleinen
    Fenstern und Schornsteinpilzen, verbunden durch Moospfade."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = pilzboden(w, R, 0.15)
    n = int(4 + 2 * s)
    for k in range(n):
        a = k / n * 2 * math.pi + 0.2
        r = R * (0.25 + 0.4 * (k % 2))
        cx, cz = round(math.cos(a) * r), round(math.sin(a) * r)
        rb = 2.2 + (k % 3) * 0.6 + s * 0.8
        y0 = zellen.get((cx, cz), 0)
        for x in range(int(cx - rb) - 1, int(cx + rb) + 2):
            for y in range(int(y0), int(y0 + rb * 1.8) + 2):
                for z in range(int(cz - rb) - 1, int(cz + rb) + 2):
                    d = math.sqrt((x - cx) ** 2 + ((y - y0 - rb * 0.85) / 0.9) ** 2 + (z - cz) ** 2)
                    if rb - 1 < d <= rb:
                        w.setze(x, y, z, w.b("white_terracotta") if (x + y + z) % 5 else w.b("light_gray_terracotta"))
                    elif d <= rb - 1:
                        w.bloecke.pop((x, y, z), None)
        dx, dz = round(-math.cos(a) * rb), round(-math.sin(a) * rb)
        for y in (y0 + 1, y0 + 2):
            w.bloecke.pop((cx + dx, y, cz + dz), None)
        w.setze(cx + dx, y0 + 1, cz + dz, w.b("spruce_door", facing="north", half="lower", hinge="left",
                                               open=False, powered=False)) if False else None
        w.setze(cx, round(y0 + rb * 1.7) + 1, cz, w.b("brown_mushroom"))
        fenster_rund(w, cx, y0 + 2, cz, rb - 0.3, 3)
    for k in range(n):
        a = k / n * 2 * math.pi + 0.2
        for t in range(int(R * 0.25)):
            x, z = round(math.cos(a) * t), round(math.sin(a) * t)
            if (x, z) in zellen:
                w.setze(x, zellen[(x, z)], z, w.b("moss_block"))
    return w


def pilzteehaus(seed, g=1):
    """Pilz-Teehaus: ein niedriges Teehaus mit einem flachen, weit ausladenden Parasolhut als Dach, Schiebewänden,
    einer Holzveranda über einem kleinen Teich und Teeschalen auf niedrigen Tischen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = pilzboden(w, R, 0.1)
    A = int(3 + s)
    for x in range(-A - 2, A + 3):
        for z in range(-A - 2, A + 3):
            w.setze(x, 1, z, w.b("spruce_planks") if max(abs(x), abs(z)) <= A + 1 else w.b("spruce_slab",
                                                                                           type="bottom",
                                                                                           waterlogged=False))
            if max(abs(x), abs(z)) == A and (x + z) % 3:
                for y in range(2, 4):
                    w.setze(x, y, z, w.b("white_wool") if y == 2 else w.b("birch_planks"))
            elif max(abs(x), abs(z)) == A:
                for y in range(2, 4):
                    w.setze(x, y, z, w.b("dark_oak_log", axis="y"))
    top = stiel(w, 0, 0, 2, 3, 0.8, 0.8)
    hut(w, 0, 4, 0, A + 4 + s, 2 + s, form="flach", farbe="light_gray_terracotta", lamellen="white_terracotta",
        dicke=1)
    for x in range(-A - 3, A + 4):
        for z in range(A + 3, A + 7):
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("water", level=0))
                w.bloecke.pop((x, 1, z), None)
    w.setze(-1, 2, -1, w.b("flower_pot"))
    w.setze(1, 2, 1, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False))
    _ = top
    return w


def pilzlaternenallee(seed, g=2):
    """Pilzlaternen-Allee: ein geschwungener Waldweg, gesäumt von mannshohen Leuchtpilzen, deren Hüte von unten in
    Blau, Grün und Gelb glühen; dazwischen Moos, Farn und kleine Pilzgruppen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = pilzboden(w, R, 0.2)
    pts = []
    for z in range(-R, R + 1):
        x = round(math.sin(z / 5) * R * 0.25)
        pts.append((x, z))
        for dx in (-1, 0, 1):
            if (x + dx, z) in zellen:
                w.setze(x + dx, zellen[(x + dx, z)], z, w.b("dirt_path"))
                w.bloecke.pop((x + dx, zellen[(x + dx, z)] + 1, z), None)
    farben = [("warped_wart_block", "sea_lantern"), ("nether_wart_block", "shroomlight"),
              ("light_blue_terracotta", "pearlescent_froglight")]
    for k, (x, z) in enumerate(pts[2::int(4 + s)]):
        for sx in (-1, 1):
            px = x + sx * 3
            y0 = zellen.get((px, z), 0) + 1
            H = int(3 + (k % 3) + s)
            top = stiel(w, px, z, y0, H, 0.5, 0.5, mat="mushroom_stem")
            f, licht = farben[(k + (sx > 0)) % 3]
            hut(w, px, top[1], z, 1.5 + 0.5 * s, 1 + 0.5 * s, form="kuppel", farbe=f,
                lamellen=licht if licht != "pearlescent_froglight" else "shroomlight")
    return w


def pilzfelsen(seed, g=2):
    """Pilzfelsen: verwitterte Felsnadeln mit breiten Deckplatten wie versteinerte Pilze ragen aus einer Heide; auf
    den Platten wachsen Moos und Gras, eine davon trägt ein kleines Vogelnest."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, huegel=0.3, art="kies")
    rng = w.rng
    f = M(w, [("sandstone", 2), ("terracotta", 2), ("smooth_sandstone", 1), ("orange_terracotta", 1)])
    for k in range(int(3 + 2 * s)):
        a = k * 2.3
        r = R * (0.15 + 0.6 * ((k * 0.41) % 1))
        cx, cz = round(math.cos(a) * r), round(math.sin(a) * r)
        H = int((4 + rng.random() * 6) * s + 4)
        rs = 0.8 + 0.4 * s
        for y in range(0, H):
            rr = rs * (1 + 0.3 * math.sin(y * 0.8))
            for x in range(cx - 3, cx + 4):
                for z in range(cz - 3, cz + 4):
                    if math.hypot(x - cx, z - cz) <= rr:
                        w.setze(x, y, z, f(x, y, z))
        rp = 2 + rng.random() * 1.5 * s
        for x in range(int(cx - rp) - 1, int(cx + rp) + 2):
            for z in range(int(cz - rp) - 1, int(cz + rp) + 2):
                d = math.hypot(x - cx, z - cz)
                if d <= rp:
                    for y in range(H, H + 2):
                        w.setze(x, y, z, f(x, y, z))
                    w.setze(x, H + 2, z, w.b("grass_block", snowy=False) if d < rp - 0.6 else w.b("moss_block"))
        if k == 0:
            w.setze(cx, H + 3, cz, w.b("hay_block", axis="y"))
    return w


def tintenfischpilz(seed, g=1):
    """Tintenfischpilz: aus einem weißen Hexenei entfalten sich mehrere rote, gekrümmte Fangarme wie bei einem
    Seestern, mit dunklen Sporenflecken – eine bizarre, riesige Pilzart im Laub."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    pilzboden(w, R, 0.2)
    u = 1.0 * s + 0.6
    kugel(w, 0, 1, 0, 1.6 * u, w.b("white_terracotta"), ry=1.2 * u)
    for k in range(5):
        a = k / 5 * 2 * math.pi
        pts = bez((math.cos(a) * u, 1.5 * u, math.sin(a) * u), (math.cos(a) * 3 * u, 4 * u, math.sin(a) * 3 * u),
                  (math.cos(a) * 5 * u, 0.5, math.sin(a) * 5 * u))
        rohr(w, pts, 0.8 * u, 0.3 * u, lambda x, y, z, *_: w.b("black_concrete") if (x * 3 + y * 5 + z) % 9 == 0 else
             w.b("red_concrete"), rauh=0.05)
    return w


def krause_glucke(seed, g=1):
    """Krause Glucke: ein riesiger, schwammartiger Pilzknäuel aus hunderten gewellten, cremefarbenen Lappen am Fuß einer
    Kiefer – wie ein überdimensionaler Badeschwamm."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    zellen = pilzboden(w, R, 0.1)
    from erw_basis import fichte
    fichte(w, -int(R * 0.35), 1, -int(R * 0.35), seed, 9 + 3 * s)
    rg = 2.5 + 2 * s
    rn = Rauschen(w, 1.2)
    for x in range(-int(rg) - 1, int(rg) + 2):
        for y in range(0, int(rg * 1.6) + 2):
            for z in range(-int(rg) - 1, int(rg) + 2):
                d = math.sqrt(x * x + ((y - rg * 0.6) / 0.8) ** 2 + z * z)
                if d <= rg and rn(x, y, z) > 0.45:
                    w.setze(x, y + 1, z, w.b("sandstone") if (x + y + z) % 3 else w.b("birch_planks"))
    return w


def rotkappe(seed, g=1):
    """Rotkappe: eine Gruppe großer Rotkappen-Röhrlinge mit orangeroten, gewölbten Hüten und schuppigen, weiß-
    schwarz gesprenkelten Stielen unter Birken."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    zellen = pilzboden(w, R, 0.1)
    from erw_basis import birke
    birke(w, int(R * 0.5), 1, -int(R * 0.4), seed, 8 + 3 * s)
    rng = w.rng
    for k in range(int(2 + s)):
        a = k * 2.2
        r = 0 if k == 0 else R * 0.35
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        H = int((5 - k) * s + 4)
        top = stiel(w, x, z, zellen.get((x, z), 0) + 1, H, 1.3 + 0.4 * s - k * 0.2, 1.0 + 0.3 * s - k * 0.15,
                    mat=lambda xx, yy, zz: "black_terracotta" if rng.random() < 0.12 else "white_terracotta",
                    knolle=0.5)
        hut(w, top[0], top[1], top[2], 3 + s - k * 0.5, 2 + s * 0.7, form="polster",
            farbe=lambda xx, yy, zz, ss: "orange_terracotta" if (xx + zz) % 4 else "red_terracotta",
            lamellen="light_gray_terracotta")
    return w


def lacktrichter(seed, g=1):
    """Lila Lacktrichter: ein Ring kleiner und großer, leuchtend violetter Trichterpilze mit gewellten Hüten und
    schlanken Stielen auf moosigem Grund."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    zellen = pilzboden(w, R, 0.05)
    n = int(5 + 3 * s)
    for k in range(n):
        a = k / n * 2 * math.pi
        r = R * (0.2 + 0.25 * (k % 2))
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        H = int(2 + (k % 3) + 1.5 * s)
        top = stiel(w, x, z, zellen.get((x, z), 0) + 1, H, 0.6 + 0.2 * s, 0.5, mat="purple_terracotta")
        hut(w, top[0], top[1], top[2], 1.5 + 0.7 * s, 1 + 0.5 * s, form="trichter",
            farbe=lambda xx, yy, zz, ss: "purple_concrete" if ss < 0.7 else "magenta_terracotta", wellig=1.0)
    return w


def pilzbaumhaus(seed, g=2):
    """Pilzbaumhaus: ein Wohnhaus im dicken Stiel eines haushohen Fliegenpilzes, mit spiralig angeordneten Fenstern,
    einer Außentreppe, einem Balkon unter dem Hut und Wäscheleine zum Nachbarpilz."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    pilzboden(w, R, 0.15)
    H = int(10 * s + 8)
    r = 3 + s
    top = stiel(w, 0, 0, 1, H, r + 0.6, r, mat="mushroom_stem", knolle=1.2, ring=0.75)
    for k in range(int(H / 2)):
        a = k * 1.1
        y = 2 + k * 2
        if y < top[1] - 1:
            w.setze(round(math.cos(a) * (r + 0.4)), y, round(math.sin(a) * (r + 0.4)), w.b("yellow_stained_glass"))
    for k in range(H * 2):
        a = k * 0.45 + 1
        y = 1 + k // 2
        if y > top[1] - 2:
            break
        w.setze(round(math.cos(a) * (r + 1.6)), y, round(math.sin(a) * (r + 1.6)), w.b("spruce_slab", type="top",
                                                                                     waterlogged=False), False)
    hut(w, 0, top[1], 0, r + 4 + s, 3 + s, form="kuppel", farbe="red_mushroom_block", punkte="white_wool")
    nx = round(R * 0.6)
    top2 = stiel(w, nx, 0, 1, int(H * 0.5), 1.2, 1.0)
    hut(w, nx, top2[1], 0, 2.5 + s, 1.5 + s * 0.5, form="kuppel", farbe="brown_mushroom_block")
    yl = int(H * 0.45)
    for x in range(round(r) + 1, nx - 1):
        w.setze(x, yl, 0, w.b("tripwire", attached=True, disarmed=False, powered=False, east=True, west=True,
                              north=False, south=False))
        if x % 2:
            w.setze(x, yl - 1, 0, w.b(["white_wool", "light_blue_wool", "pink_wool"][x % 3]))
    return w


def pilzgondel(seed, g=2):
    """Pilzgondel: zwischen zwei gewaltigen Riesenpilzen spannt sich ein Seil, an dem eine Gondel aus einem halben
    Pilzhut hängt; auf jedem Hut eine Station mit Seilrad und Geländer."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    pilzboden(w, R, 0.2)
    tops = []
    for k, (x, H, f) in enumerate(((-int(R * 0.55), int(10 * s + 8), "red_mushroom_block"),
                                   (int(R * 0.55), int(7 * s + 6), "brown_mushroom_block"))):
        top = stiel(w, x, 0, 1, H, 1.6 + 0.5 * s, 1.2 + 0.4 * s)
        yt = hut(w, x, top[1], 0, 3.5 + 1.2 * s, 1.5 + 0.5 * s, form="flach", farbe=f, dicke=1,
                 punkte="white_wool" if k == 0 else None)
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                w.setze(x + dx, yt + 1, dz, w.b("spruce_planks"))
                if max(abs(dx), abs(dz)) == 2:
                    w.setze(x + dx, yt + 2, dz, w.b("spruce_fence"))
        for y in range(yt + 2, yt + 5):
            w.setze(x, y, 0, w.b("spruce_log", axis="y"))
        tops.append((x, yt + 4))
    (x0, y0), (x1, y1) = tops
    n = x1 - x0
    for k in range(n + 1):
        t = k / n
        y = round(y0 + (y1 - y0) * t - math.sin(t * math.pi) * 2)
        w.setze(x0 + k, y, 0, w.b("chain", axis="x", waterlogged=False), False)
    gx = (x0 + x1) // 2
    gy = round((y0 + y1) / 2 - 2)
    for y in range(gy - 2, gy):
        w.setze(gx, y, 0, w.b("chain", axis="y", waterlogged=False), False)
    for dx in range(-2, 3):
        for dz in range(-1, 2):
            w.setze(gx + dx, gy - 5, dz, w.b("red_mushroom_block", north=True, south=True, east=True, west=True,
                                             up=True, down=True))
            if abs(dx) == 2 or abs(dz) == 1:
                w.setze(gx + dx, gy - 4, dz, w.b("red_mushroom_block", north=True, south=True, east=True, west=True,
                                                 up=True, down=True))
        w.setze(gx + dx, gy - 3, 0, w.b("mushroom_stem", north=True, south=True, east=True, west=True, up=True,
                                        down=True)) if abs(dx) < 2 else None
    return w


PILZE3 = {
    "pilzleuchtturm": ("Pilzleuchtturm", pilzleuchtturm),
    "pilzmuehle": ("Pilzmühle", pilzmuehle),
    "baumschwammtreppe": ("Baumschwamm-Treppe", baumschwammtreppe),
    "pilzkarussell": ("Pilzkarussell", pilzkarussell),
    "pilzbaeckerei": ("Pilzbäckerei", pilzbaeckerei),
    "pilzschloss": ("Pilzschloss", pilzschloss),
    "schneckenweide": ("Schneckenweide", schneckenweide),
    "sporenlabor": ("Sporenlabor", sporenlabor),
    "pilzpagode": ("Pilzpagode", pilzpagode),
    "trueffelgarten": ("Trüffelgarten", trueffelgarten),
    "bovistsiedlung": ("Bovist-Siedlung", bovistsiedlung),
    "pilzteehaus": ("Pilz-Teehaus", pilzteehaus),
    "pilzlaternenallee": ("Pilzlaternen-Allee", pilzlaternenallee),
    "pilzfelsen": ("Pilzfelsen", pilzfelsen),
    "tintenfischpilz": ("Tintenfischpilz", tintenfischpilz),
    "krause_glucke": ("Krause Glucke", krause_glucke),
    "rotkappe": ("Rotkappe", rotkappe),
    "lacktrichter": ("Lila Lacktrichter", lacktrichter),
    "pilzbaumhaus": ("Pilzbaumhaus", pilzbaumhaus),
    "pilzgondel": ("Pilzgondel", pilzgondel),
}

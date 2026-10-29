"""Wüstenreich II – zwanzig weitere Wüstenbauten: Minarett mit Kuppelhalle, Palmenhain mit Kanälen,
Sandsturm-Ruine, Kamelkarawane, Zisterne, Sonnenuhr-Platz, Felsenstadt, Glasbläserei, Dattelhändler,
Tafelberg-Zitadelle, Schakalwächter, Grabkammer-Eingang, Schöpfwerk, Salzpfanne, Scheichzelt, Teehaus mit
Dachterrasse, Wasserpalast, Wurmskelett in den Dünen, Lehmspeicher und Töpfermarkt."""

from __future__ import annotations

import math

import wald2
from feinbau import Mix, kram, platte, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen, einfuegen
from wueste_eis import kuppel

S = [0.6, 1.0, 1.6, 2.5]


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def sand(w, R, duenen=1.0):
    rn = Rauschen(w, 7)
    zellen = {}
    for x in range(-int(R) - 2, int(R) + 3):
        for z in range(-int(R) - 2, int(R) + 3):
            if math.hypot(x, z) <= R + 2 * rn(x, 0, z):
                h = int(duenen * 2 * rn(x * 0.7, 3, z * 0.7))
                for y in range(-2, h + 1):
                    w.setze(x, y, z, w.b("sand" if y == h else "sandstone"))
                zellen[(x, z)] = h
    return zellen


def lehm(w):
    return M(w, [("smooth_sandstone", 3), ("cut_sandstone", 1), ("sandstone", 1), ("white_terracotta", 1)])


def lehmbau(w, cx, cz, B, T, y0, H, mat=None, tuer_s="south", zinnen=True):
    mat = mat or lehm(w)
    x0, z0, x1, z1 = cx - B // 2, cz - T // 2, cx + B // 2, cz + T // 2
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            rand = x in (x0, x1) or z in (z0, z1)
            for y in range(y0, y0 + H):
                if rand:
                    fen = y == y0 + 2 and (x + z) % 3 == 0 and not (x in (x0, x1) and z in (z0, z1))
                    w.setze(x, y, z, w.b("spruce_trapdoor", facing="north", half="top", open=False, powered=False,
                                         waterlogged=False) if fen else mat(x, y, z))
                else:
                    w.bloecke.pop((x, y, z), None)
            w.setze(x, y0 - 1, z, w.b("smooth_sandstone"))
            w.setze(x, y0 + H, z, mat(x, y0 + H, z))
            if rand and zinnen and (x + z) % 2 == 0:
                w.setze(x, y0 + H + 1, z, mat(x, y0 + H + 1, z))
    for x in range(x0 + 1, x1, 3):
        w.setze(x, y0 + H - 1, z1 + 1, w.b("stripped_jungle_log", axis="z"), False)
    d = {"south": (cx, z1), "north": (cx, z0), "east": (x1, cz), "west": (x0, cz)}[tuer_s]
    for y in (y0, y0 + 1):
        w.bloecke.pop((d[0], y, d[1]), None)
    return y0 + H + 1


def palme(w, x, y, z, seed):
    einfuegen(w, wald2.palme(seed + x * 31 + z), x, y, z)


def markise(w, x0, x1, z, y, farben=("red_wool", "white_wool")):
    for x in range(x0, x1 + 1):
        w.setze(x, y, z, w.b(farben[x % 2]), False)
        w.setze(x, y - 1, z + 1, w.b(farben[x % 2]), False)


# ============================================================================ Bauten

def minarett(seed, g=2):
    """Minarett mit Kuppelhalle: eine Halle mit großer, gerippter Kuppel und Arkadenhof, daneben ein schlankes,
    hohes Minarett mit Balkonen und einer kleinen Zwiebelhaube."""
    w = _neu(seed)
    s = S[g]
    sand(w, 12 * s + 5, 0.5)
    B = int(8 * s + 5) | 1
    top = lehmbau(w, 0, 0, B, B, 1, int(4 * s + 3), zinnen=False)
    kuppel(w, lambda x, y, z, t: w.b("light_blue_terracotta" if (x + z) % 3 else "white_terracotta"), 0, 0, top,
           int(B * 0.4))
    H = int(14 * s + 8)
    mx = B // 2 + 3
    for y in range(1, H):
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                if abs(dx) + abs(dz) < 2 or y % 6 == 0:
                    w.setze(mx + dx, y, dz, w.b("smooth_sandstone" if y % 6 else "cut_sandstone"))
    kuppel(w, w.b("gold_block"), mx, 0, H, 1.5, form="zwiebel")
    for x in range(-B // 2, B // 2 + 1, 2):
        for y in range(1, 4):
            w.bloecke.pop((x, y, B // 2), None) if y < 3 else None
    return w


def palmenhain(seed, g=1):
    """Palmenhain mit Kanälen: ein Garten aus Dattelpalmen im Raster, dazwischen schmale, gemauerte
    Bewässerungskanäle mit Wasser, ein Brunnenhaus und Beete mit Gemüse."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 5)
    sand(w, R, 0.2)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) > R:
                continue
            if x % 6 == 0 or z % 6 == 0:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("smooth_sandstone"))
            elif x % 6 == 3 and z % 6 == 3:
                palme(w, x, 0, z, seed)
            else:
                w.setze(x, 0, z, w.b("grass_block", snowy=False) if (x + z) % 4 else w.b("farmland", moisture=7))
    lehmbau(w, 0, 0, 5, 5, 1, 3)
    return w


def sandsturmruine(seed, g=2):
    """Sandsturm-Ruine: die Säulen und Mauern eines Tempels ragen schräg aus hohen Dünen, ein riesiger Statuenkopf
    liegt halb begraben im Sand, Torbögen führen ins Nichts."""
    from skulptur import Skulptur, ell, kasten
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 5)
    rng = w.rng
    zellen = sand(w, R, 2.5)
    st = lehm(w)
    for k in range(6 + g * 2):
        x, z = int((rng.random() - 0.5) * R * 1.4), int((rng.random() - 0.5) * R * 1.4)
        H = int((4 + rng.random() * 6) * s)
        for y in range(zellen.get((x, z), 0), zellen.get((x, z), 0) + H):
            w.setze(x, y, z, w.b("sandstone" if y % 3 else "chiseled_sandstone"))
    Sk = Skulptur(w, s)
    Sk.mat("k", lambda x, y, z, *a: st(x, y, z))
    Sk.mat("d", w.b("black_terracotta"))
    Sk.plus(ell(0, 2, 0, 4.0, 4.5, 3.8), "k")
    Sk.plus(kasten(-4.5, 4.5, -4, 4.5, 6.5, 4), "k")
    Sk.plus(ell(-1.4, 3, 3.4, 0.6, 0.4, 0.3), "d")
    Sk.plus(ell(1.4, 3, 3.4, 0.6, 0.4, 0.3), "d")
    Sk.rendern((-6, -2, -5), (6, 8, 5), versatz=(R * 0.3 + 0.5, 0, -R * 0.2 + 0.5), ueberschreiben=False)
    return w


def kamelkarawane(seed, g=2):
    """Kamelkarawane: eine Reihe von Kamel-Skulpturen mit bunten Satteldecken und Lasten zieht über eine Düne,
    angeführt von einem Laternenträger, Fußspuren im Sand."""
    from skulptur import Skulptur, ell, kap
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 6)
    sand(w, R, 1.0)
    farben = ["red_wool", "blue_wool", "orange_wool", "purple_wool"]
    n = 3 + g
    for k in range(n):
        x0 = int((k - (n - 1) / 2) * 8 * s)
        Sk = Skulptur(w, s)
        Sk.mat("h", w.b("yellow_terracotta"))
        Sk.mat("f", w.b(farben[k % 4]))
        Sk.mat("l", w.b("brown_wool"))
        Sk.mat("d", w.b("black_concrete"))
        Sk.plus(ell(0, 5, 0, 3.0, 1.8, 1.6), "h")
        Sk.plus(ell(0, 6.8, 0, 1.2, 1.2, 1.2), "h")
        for sx in (-1.6, 1.6):
            for sz in (-0.7, 0.7):
                Sk.plus(kap((sx, 4.5, sz), (sx, 0, sz), 0.4), "h")
        Sk.plus(kap((2.5, 5.5, 0), (3.5, 8.5, 0), 0.6, 0.5), "h")
        Sk.plus(ell(4.1, 8.8, 0, 1.0, 0.6, 0.6), "h")
        Sk.plus(ell(0, 6.3, 0, 1.8, 0.5, 1.8), "f")
        Sk.plus(ell(-1.4, 7.4, 0, 0.9, 0.9, 1.2), "l")
        Sk.rendern((-4, 0, -3), (6, 10, 3), versatz=(x0 + 0.5, 1, round(math.sin(k) * 2) + 0.5))
    return w


def zisterne(seed, g=2):
    """Zisterne: ein unterirdischer Wasserspeicher mit Säulenhalle, deren Gewölbe teils eingebrochen ist – von oben
    sieht man Säulenreihen im Wasser, eine Treppe führt hinab."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 5)
    sand(w, R + 3, 0.3)
    D = int(5 * s + 3)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            for y in range(-D, 1):
                rand = abs(x) == R or abs(z) == R
                if rand or y == -D:
                    w.setze(x, y, z, w.b("sandstone"))
                elif y < -D + 3:
                    w.setze(x, y, z, w.b("water", level=0))
                else:
                    w.bloecke.pop((x, y, z), None)
            if x % 3 == 0 and z % 3 == 0 and abs(x) < R and abs(z) < R:
                for y in range(-D, 1):
                    w.setze(x, y, z, w.b("cut_sandstone" if y % 2 else "chiseled_sandstone"))
            if (x + z) % 5 == 0 and abs(x) < R - 1 and abs(z) < R - 1 and x % 3 and z % 3:
                w.bloecke.pop((x, 0, z), None)
    for k in range(D):
        for x in range(R - 3, R):
            w.setze(x, -k, -R + 1 + k, treppe(w, "sandstone", "north"))
    return w


def sonnenuhrplatz(seed, g=2):
    """Sonnenuhr-Platz: ein runder Platz mit einer großen Bodensonnenuhr aus Stundenlinien und Zahlensteinen, in
    der Mitte ein schräger Schattenstab aus Gold, Bänke und Palmen am Rand."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 5)
    sand(w, R + 3, 0.2)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d <= R:
                a = math.degrees(math.atan2(z, x)) % 30
                w.setze(x, 0, z, w.b("chiseled_sandstone" if d > R - 1.2 and a < 6 else
                                     "cut_sandstone" if a < 3 else "smooth_sandstone"))
    for k in range(int(8 * s) + 3):
        w.setze(0, 1 + k, -round(k * 0.6), w.b("gold_block"))
    for k in range(6):
        a = k / 6 * 6.283
        palme(w, round(math.cos(a) * (R + 2)), 0, round(math.sin(a) * (R + 2)), seed)
    return w


def felsenstadt(seed, g=3):
    """Felsenstadt: an einer roten Felswand kleben Häuser, deren Fassaden direkt aus dem Stein gehauen sind, mit
    Fenstern, Türen und Treppen auf mehreren Ebenen, Stoffbahnen als Sonnenschutz."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 6)
    rng = w.rng
    sand(w, R, 0.3)
    H = int(14 * s + 6)
    for x in range(-R, R + 1):
        for z in range(-R, -int(R * 0.2)):
            for y in range(1, H - int(abs(x) * 0.15)):
                w.setze(x, y, z, w.b(["red_sandstone", "orange_terracotta", "terracotta", "smooth_red_sandstone"]
                                     [int((y + math.sin(x * 0.3) * 2) / 2) % 4]))
    zf = -int(R * 0.2)
    for e in range(3 + g):
        y0 = 1 + e * 4
        for k in range(3):
            x0 = int((k - 1) * 8 * s) + (e % 2) * 3
            for x in range(x0 - 2, x0 + 3):
                for y in range(y0, y0 + 3):
                    w.setze(x, y, zf - 1, w.b("smooth_red_sandstone"))
                    if abs(x - x0) <= 1 and y < y0 + 2:
                        w.bloecke.pop((x, y, zf - 1), None) if x == x0 else w.setze(x, y + 1, zf - 1,
                                                                                    w.b("orange_stained_glass_pane",
                                                                                        east=True, west=True,
                                                                                        north=False, south=False,
                                                                                        waterlogged=False))
                    for z in range(zf - 4, zf - 1):
                        if abs(x - x0) <= 1 and y < y0 + 3:
                            w.bloecke.pop((x, y, z), None)
            for x in range(x0 - 2, x0 + 3):
                w.setze(x, y0 + 3, zf, w.b("red_wool" if x % 2 else "white_wool"), False)
        for x in range(-R // 2, R // 2):
            w.setze(x, y0 - 1, zf, w.b("smooth_red_sandstone_slab", type="top", waterlogged=False), False)
    return w


def glasblaeserei(seed, g=1):
    """Glasbläserei: eine Lehmwerkstatt mit kuppelförmigem Glasofen, aus dem Glut leuchtet, Regale voller bunter
    Glasflaschen vor der Tür, Sandhaufen und ein Brunnen."""
    w = _neu(seed)
    s = S[g]
    sand(w, 9 * s + 4, 0.3)
    top = lehmbau(w, 0, 0, int(7 * s + 4) | 1, int(5 * s + 4) | 1, 1, 4)
    kuppel(w, w.b("bricks"), int(4 * s + 4), 0, 1, 2.5)
    w.setze(int(4 * s + 4), 1, 2, w.b("magma_block"))
    farben = ["green_stained_glass", "blue_stained_glass", "yellow_stained_glass", "red_stained_glass",
              "cyan_stained_glass"]
    for k in range(5):
        x = -3 + k * 2
        w.setze(x, 1, int(2.5 * s + 4), w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                            waterlogged=False))
        w.setze(x, 2, int(2.5 * s + 4), w.b(farben[k]))
    return w


def dattelhaendler(seed, g=1):
    """Dattelhändler: ein Marktstand unter Palmen mit Körben voller Datteln und Feigen, Säcken, einer Waage, einer
    gestreiften Markise und einem Lehmhaus mit Dachgarten dahinter."""
    w = _neu(seed)
    s = S[g]
    sand(w, 9 * s + 4, 0.3)
    top = lehmbau(w, 0, -3, int(7 * s + 4) | 1, 5, 1, 4)
    for x in range(-2, 3):
        w.setze(x, top, -3, w.b("grass_block", snowy=False))
        w.setze(x, top + 1, -3, w.b("azalea"))
    markise(w, -4, 4, 2, 4)
    for x in range(-4, 5, 2):
        w.setze(x, 1, 3, w.b("composter", level=8) if x % 4 else w.b("barrel", facing="up", open=True))
    for k in range(3):
        palme(w, -6 + k * 6, 0, 6, seed + k)
    return w


def tafelbergzitadelle(seed, g=3):
    """Tafelberg-Zitadelle: auf einem steilen, roten Tafelberg thront eine Zitadelle mit Lehmmauern und Türmen, ein
    Zickzackweg führt die Flanke hinauf, unten ein Brunnen mit Palmen."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 6)
    sand(w, R + 4, 0.3)
    H = int(10 * s + 5)
    rng = w.rng
    Rb = R * 0.6
    for x in range(-int(Rb) - 3, int(Rb) + 4):
        for z in range(-int(Rb) - 3, int(Rb) + 4):
            d = math.hypot(x, z)
            if d <= Rb + 2:
                h = H if d <= Rb else int(H * (1 - (d - Rb) / 2))
                for y in range(1, h + 1):
                    w.setze(x, y, z, w.b(["red_terracotta", "orange_terracotta", "terracotta", "red_sandstone"]
                                         [int(y / 2) % 4]))
    a = int(Rb * 0.7)
    st = lehm(w)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if abs(x) == a or abs(z) == a:
                for y in range(H + 1, H + 5):
                    w.setze(x, y, z, st(x, y, z))
                if (x + z) % 2 == 0:
                    w.setze(x, H + 5, z, st(x, 0, z))
    for (x, z) in ((-a, -a), (a, -a), (-a, a), (a, a)):
        for y in range(H + 1, H + 9):
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    w.setze(x + dx, y, z + dz, st(x, y, z))
    lehmbau(w, 0, 0, 7, 7, H + 1, 6)
    for i in range(H * 3):
        y = 1 + i // 3
        t = i / (H * 3)
        x = round(math.cos(t * 6.283 * 1.5) * (Rb + 2))
        z = round(math.sin(t * 6.283 * 1.5) * (Rb + 2))
        w.setze(x, y, z, w.b("smooth_sandstone_slab", type="top", waterlogged=False), False)
    return w


def schakalwaechter(seed, g=2):
    """Schakalwächter: zwei riesige, sitzende Schakal-Statuen aus schwarzem Stein mit goldenen Halsbändern
    flankieren einen Prozessionsweg, der zu einem kleinen Tor im Sandstein führt."""
    from skulptur import Skulptur, ell, kap
    w = _neu(seed)
    s = S[g]
    L = int(14 * s + 6)
    sand(w, L + 3, 0.3)
    for z in range(-L, L + 1):
        for x in range(-2, 3):
            w.setze(x, 0, z, w.b("smooth_sandstone"))
    for sx in (-1, 1):
        Sk = Skulptur(w, s)
        Sk.mat("k", w.b("blackstone"))
        Sk.mat("g", w.b("gold_block"))
        Sk.plus(kap((0, 0, 0), (0, 2, 0), 2.8, 2.6), "k")
        Sk.plus(ell(0, 5, -0.5, 2.2, 3.5, 2.6), "k")
        Sk.plus(kap((0, 7.5, 0.4), (0, 10, 1.0), 1.0, 0.9), "k")
        Sk.plus(ell(0, 10.6, 1.4, 1.2, 1.2, 1.4), "k")
        Sk.plus(kap((0, 10.4, 2.4), (0, 10.0, 4.0), 0.6, 0.35), "k")
        for ex in (-0.6, 0.6):
            Sk.plus(kap((ex, 11.4, 1.2), (ex * 1.4, 13.6, 0.8), 0.45, 0.15), "k")
        Sk.plus(kap((0, 7.4, 0.6), (0, 7.4, 0.6), 1.2), "g")
        for ex in (-0.9, 0.9):
            Sk.plus(kap((ex, 3, 2.0), (ex, 0.3, 2.6), 0.5), "k")
        Sk.rendern((-4, 0, -4), (4, 15, 5), versatz=(sx * 6 + 0.5, 1, -L // 2 + 0.5))
    for x in range(-4, 5):
        for y in range(1, 8):
            w.setze(x, y, -L, w.b("cut_sandstone") if abs(x) > 1 or y > 4 else w.b("air"))
    return w


def grabkammer(seed, g=2):
    """Grabkammer-Eingang: ein in den Fels gehauener Eingang mit massivem Sturz, flankiert von zwei steifen
    Wächterfiguren, eine Rampe führt hinab in die Dunkelheit, Fackeln am Eingang."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 5)
    rng = w.rng
    sand(w, R, 0.4)
    H = int(8 * s + 4)
    for x in range(-R, R + 1):
        for z in range(-R, -2):
            for y in range(1, H + int(rng.random() * 2)):
                w.setze(x, y, z, w.b(["sandstone", "smooth_sandstone", "yellow_terracotta"][int(rng.random() * 3)]))
    for y in range(-3, 5):
        for x in range(-1, 2):
            for z in range(-8, 0):
                if y > -3 + max(0, z + 8) // 2 - 4:
                    w.bloecke.pop((x, y, z), None)
    for x in range(-3, 4):
        w.setze(x, 5, -3, w.b("chiseled_sandstone"))
    for sx in (-1, 1):
        for y in range(1, 5):
            w.setze(sx * 3, y, -2, w.b("cut_sandstone" if y < 4 else "gold_block"))
        w.setze(sx * 2, 4, -2, w.b("wall_torch", facing="south"))
    return w


def schoepfwerk(seed, g=2):
    """Schöpfwerk: ein großes hölzernes Wasserrad mit Tonkrügen am Rand hebt Wasser aus einem Brunnen in eine
    erhöhte Rinne, die zu Feldern führt, angetrieben von einem Göpelwerk."""
    w = _neu(seed)
    s = S[g]
    sand(w, 10 * s + 4, 0.3)
    R = int(4 * s + 2)
    for x in range(-2, 3):
        for z in range(-2, 3):
            for y in range(-3, 1):
                w.setze(x, y, z, w.b("water", level=0) if abs(x) < 2 and abs(z) < 2 else w.b("sandstone"))
    for k in range(R * 8):
        a = k / (R * 8) * 6.283
        for r in range(R + 1):
            if r == R or k % R == 0:
                x, y = round(math.cos(a) * r), round(R + math.sin(a) * r)
                w.setze(x, y - 1, 0, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False)
                        if r == R and k % 3 == 0 else w.b("jungle_planks") if r == R else
                        w.b("stripped_jungle_log", axis="y"))
    for x in range(R, R + int(8 * s)):
        w.setze(x, 2 * R - 1, 0, w.b("smooth_sandstone"))
        w.setze(x, 2 * R, 0, w.b("water", level=0))
    for x in range(R + int(8 * s) - 4, R + int(8 * s) + 4):
        for z in range(-4, 5):
            w.setze(x, 0, z, w.b("farmland", moisture=7))
            w.setze(x, 1, z, w.b("wheat", age=6))
    return w


def salzpfanne(seed, g=2):
    """Salzpfanne: eine flache, weiß glitzernde Salzebene mit rechteckigen Verdunstungsbecken in Rosa und Weiß,
    Salzhaufen, Arbeitswege und eine kleine Hütte der Salzsieder."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                w.setze(x, 0, z, w.b("white_concrete_powder" if (x * z) % 7 else "calcite"))
                w.setze(x, -1, z, w.b("sandstone"))
    k = 0
    for bx in range(-R + 2, R - 4, 6):
        for bz in range(-R // 2, R // 2, 6):
            for x in range(bx, bx + 5):
                for z in range(bz, bz + 5):
                    if math.hypot(x, z) < R - 1:
                        w.setze(x, 0, z, w.b("water", level=0) if (k % 3) else w.b("pink_concrete_powder"))
            k += 1
    for k in range(4):
        x, z = int(R * 0.6) - k * 3, -int(R * 0.7)
        kugel(w, x, 1, z, 1.5, w.b("white_concrete"), ry=1.2)
    lehmbau(w, -int(R * 0.6), int(R * 0.6), 5, 5, 1, 3)
    return w


def scheichzelt(seed, g=2):
    """Scheichzelt: ein großes, prächtiges Zelt aus gestreiftem Tuch mit mehreren Spitzen, innen Teppiche und
    Kissen, davor ein Lagerfeuer, Kamele und Wasserkrüge."""
    w = _neu(seed)
    s = S[g]
    sand(w, 11 * s + 4, 0.6)
    B, T = int(8 * s + 4), int(5 * s + 3)
    farben = ["red_wool", "black_wool", "white_wool"]
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            spitze = max(0, 1 - min(abs(x - px) for px in (-B // 2, 0, B // 2)) / 3)
            h = int(3 + 3 * spitze * s + (T - abs(z)) * 0.3)
            w.setze(x, h, z, w.b(farben[(z + 9) % 3]))
            if abs(z) == T:
                for y in range(1, h):
                    if not (abs(x) <= 1 and z == T):
                        w.setze(x, y, z, w.b(farben[(x + 9) % 3]))
            w.setze(x, 0, z, w.b("red_wool" if (x + z) % 2 else "orange_wool"))
    for px in (-B // 2, 0, B // 2):
        for y in range(1, int(3 + 3 * s) + 2):
            w.setze(px, y, 0, w.b("dark_oak_fence", north=False, south=False, east=False, west=False,
                                  waterlogged=False))
    w.setze(0, 1, T + 4, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


def dachterrassenteehaus(seed, g=1):
    """Teehaus mit Dachterrasse: ein zweistöckiges Lehmhaus mit bunt bemalter Tür, eine Außentreppe führt auf die
    Dachterrasse mit Teppichen, Kissen, Laternen und einem Sonnensegel."""
    w = _neu(seed)
    s = S[g]
    sand(w, 9 * s + 4, 0.3)
    B = int(6 * s + 4) | 1
    top = lehmbau(w, 0, 0, B, B, 1, 7)
    for x in range(-B // 2 + 1, B // 2):
        for z in range(-B // 2 + 1, B // 2):
            w.setze(x, top, z, w.b("red_carpet" if (x + z) % 2 else "orange_carpet"))
    for (x, z) in ((-B // 2 + 1, -B // 2 + 1), (B // 2 - 1, -B // 2 + 1), (-B // 2 + 1, B // 2 - 1),
                   (B // 2 - 1, B // 2 - 1)):
        for y in range(top, top + 3):
            w.setze(x, y, z, zaun(w, "jungle"))
    for x in range(-B // 2 + 1, B // 2):
        for z in range(-B // 2 + 1, B // 2):
            w.setze(x, top + 3, z, w.b("white_wool"))
    for k in range(7):
        w.setze(B // 2 + 1, 1 + k, B // 2 - k, treppe(w, "sandstone", "north"), False)
    w.setze(0, 1, B // 2, w.b("blue_terracotta"))
    return w


def wasserpalast(seed, g=3):
    """Wasserpalast: ein weißer Palast mit Bogenarkaden steht mitten in einem langen Wasserbecken, Springbrunnen-
    reihen, Zypressen und Palmen säumen die Ränder, eine Brücke führt zum Eingang."""
    w = _neu(seed)
    s = S[g]
    L = int(16 * s + 6)
    sand(w, L + 4, 0.2)
    B = int(6 * s + 3)
    for x in range(-B - 2, B + 3):
        for z in range(-L, L + 1):
            w.setze(x, 0, z, w.b("water", level=0) if abs(x) <= B else w.b("smooth_sandstone"))
            w.setze(x, -1, z, w.b("light_blue_terracotta"))
    top = lehmbau(w, 0, 0, B * 2 - 1, B * 2 - 1, 1, int(5 * s + 3), mat=M(w, [("white_terracotta", 2),
                                                                              ("smooth_quartz", 1)]), zinnen=False)
    kuppel(w, w.b("smooth_quartz"), 0, 0, top, B * 0.6)
    for z in range(B, L):
        w.setze(0, 1, z, w.b("smooth_sandstone_slab", type="bottom", waterlogged=False))
    for z in range(-L + 2, L - 1, 4):
        for sx in (-1, 1):
            if abs(z) > B + 1:
                w.setze(sx * (B // 2 + 1), 1, z, w.b("water", level=0))
            palme(w, sx * (B + 2), 0, z, seed)
    return w


def wurmskelett(seed, g=3):
    """Wurmskelett in den Dünen: das gewaltige Skelett eines Riesenwurms windet sich aus dem Sand – Wirbelringe,
    Rippen, ein mächtiger Kiefer mit Zahnkränzen."""
    w = _neu(seed)
    s = S[g]
    R = int(16 * s + 6)
    sand(w, R, 2.0)
    pts = []
    for i in range(int(R * 3)):
        t = i / (R * 3)
        x = (t - 0.5) * R * 1.7
        y = abs(math.sin(t * math.pi * 2.2)) * 6 * s - 1
        z = math.sin(t * 6.283) * R * 0.3
        pts.append((x, y, z))
    for k, (x, y, z) in enumerate(pts):
        if k % 4 == 0:
            r = 3 * s + 1
            for a in range(int(r * 8)):
                aa = a / (r * 8) * 6.283
                p = (round(x), round(y + math.sin(aa) * r), round(z + math.cos(aa) * r))
                if p[1] >= 0:
                    w.setze(*p, w.b("bone_block", axis="x"), False)
    x, y, z = pts[-1]
    for a in range(int(6 * s * 8)):
        aa = a / (6 * s * 8) * 6.283
        for r in (3 * s + 2, 3 * s + 1):
            p = (round(x + 1), round(y + 3 + math.sin(aa) * r), round(z + math.cos(aa) * r))
            if p[1] >= 0:
                w.setze(*p, w.b("bone_block", axis="x") if r > 3 * s + 1.5 else w.b("pointed_dripstone",
                                                                                    vertical_direction="up",
                                                                                    thickness="tip",
                                                                                    waterlogged=False), False)
    return w


def lehmspeicher(seed, g=2):
    """Lehmspeicher: ein hoher, wehrhafter Kornspeicher aus Lehm mit hunderten kleinen Kammern übereinander, deren
    Holztüren über Leitern und Balkenstufen erreichbar sind."""
    w = _neu(seed)
    s = S[g]
    sand(w, 10 * s + 4, 0.3)
    B = int(8 * s + 4) | 1
    H = int(10 * s + 4)
    st = lehm(w)
    for x in range(-B // 2, B // 2 + 1):
        for z in range(-B // 2, B // 2 + 1):
            for y in range(1, H + 1):
                rand = abs(x) == B // 2 or abs(z) == B // 2
                if rand:
                    tuer_ = (y % 3 == 1) and (x % 3 == 0) and z == B // 2
                    w.setze(x, y, z, w.b("jungle_trapdoor", facing="south", half="bottom", open=False, powered=False,
                                         waterlogged=False) if tuer_ else st(x, y, z))
            if (x + z) % 2 == 0 and (abs(x) == B // 2 or abs(z) == B // 2):
                w.setze(x, H + 1, z, st(x, H, z))
    for y in range(2, H, 3):
        for x in range(-B // 2, B // 2 + 1, 2):
            w.setze(x, y, B // 2 + 1, w.b("stripped_jungle_log", axis="z"), False)
    return w


def toepfermarkt(seed, g=1):
    """Töpfermarkt: auf einem Platz stapeln sich Tonkrüge, Amphoren und Schalen in allen Größen, eine Töpferscheibe
    unter einem Sonnendach, ein Brennofen und Lehmhäuser ringsum."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 5)
    sand(w, R, 0.2)
    rng = w.rng
    for k in range(int(30 * s) + 10):
        x, z = int((rng.random() - 0.5) * R * 1.2), int((rng.random() - 0.5) * R * 1.2)
        if w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("decorated_pot", facing="north", waterlogged=False, cracked=rng.random() < 0.2))
            if rng.random() < 0.3:
                w.setze(x, 2, z, w.b("flower_pot"))
    kuppel(w, w.b("bricks"), R - 3, -R + 3, 1, 2.5)
    for k in range(2):
        lehmbau(w, -R + 4, -R // 2 + k * (R + 1), 5, 5, 1, 4)
    for (x, z) in ((-2, 0), (2, 0), (-2, 3), (2, 3)):
        for y in range(1, 4):
            w.setze(x, y, z, zaun(w, "jungle"))
    for x in range(-2, 3):
        for z in range(0, 4):
            w.setze(x, 4, z, w.b("white_wool"))
    w.setze(0, 1, 1, w.b("stonecutter", facing="north"))
    return w


WUESTE3 = {
    "minarett": ("Minarett mit Kuppelhalle", minarett),
    "palmenhain": ("Palmenhain mit Kanälen", palmenhain),
    "sandsturmruine": ("Sandsturm-Ruine", sandsturmruine),
    "kamelkarawane": ("Kamelkarawane", kamelkarawane),
    "zisterne": ("Zisterne", zisterne),
    "sonnenuhrplatz": ("Sonnenuhr-Platz", sonnenuhrplatz),
    "felsenstadt": ("Felsenstadt", felsenstadt),
    "glasblaeserei": ("Glasbläserei", glasblaeserei),
    "dattelhaendler": ("Dattelhändler", dattelhaendler),
    "tafelbergzitadelle": ("Tafelberg-Zitadelle", tafelbergzitadelle),
    "schakalwaechter": ("Schakalwächter", schakalwaechter),
    "grabkammer": ("Grabkammer-Eingang", grabkammer),
    "schoepfwerk": ("Schöpfwerk", schoepfwerk),
    "salzpfanne": ("Salzpfanne", salzpfanne),
    "scheichzelt": ("Scheichzelt", scheichzelt),
    "dachterrassenteehaus": ("Teehaus mit Dachterrasse", dachterrassenteehaus),
    "wasserpalast": ("Wasserpalast", wasserpalast),
    "wurmskelett": ("Wurmskelett in den Dünen", wurmskelett),
    "lehmspeicher": ("Lehmspeicher", lehmspeicher),
    "toepfermarkt": ("Töpfermarkt", toepfermarkt),
}

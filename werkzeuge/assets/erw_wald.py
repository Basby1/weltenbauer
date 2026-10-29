"""Wald II – zwanzig weitere Waldszenen: Lärchenwald, Eibenhain, Moosfelsen-Wald, Farnschlucht, Hochsitz am Wald-
rand, Försterhaus, Waldkapelle, Biberdamm, Spechtlichtung, Hirschlichtung, Stammbrücke über die Klamm, Waldsee mit
Steg, Fuchsbau, Windbruch, Wanderhütte mit Wegweiser, Ameisenhügel-Lichtung, Quellgrund, Kletterwald,
Beerenhecke am Waldrand und Riesenstumpf."""

from __future__ import annotations

import math

import modbloecke as MB
import wald2
from erw_basis import M, S, baum, birke, figur, fichte, haus, hoehe, wiese
from feinbau import Dachmat, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, laubball, rohr
from lib import Rauschen, einfuegen, laub
from skulptur import ell, kap, kasten, kegel, kreisrand


def setze_baum(w, welt, x, y, z):
    einfuegen(w, welt, x, y, z)


def wald(w, zellen, R, n, seed, arten=("eiche",), innen=0.0, frei=None, H=(10, 16)):
    """Verteilt Bäume über die Fläche (mit Mindestabstand), optional ohne Freiflächen-Kreis."""
    rng = w.rng
    gesetzt = []
    for _ in range(n * 4):
        if len(gesetzt) >= n:
            break
        a = rng.random() * 6.28
        d = R * (innen + rng.random() * (0.95 - innen))
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if frei and math.hypot(x - frei[0], z - frei[1]) < frei[2]:
            continue
        if any(math.hypot(x - a2, z - b2) < 4 for a2, b2 in gesetzt):
            continue
        gesetzt.append((x, z))
        y = zellen.get((x, z), 0) + 1
        hh = H[0] + rng.random() * (H[1] - H[0])
        art = arten[len(gesetzt) % len(arten)]
        sd = seed + x * 13 + z * 7
        if art == "eiche":
            welt = wald2.laubbaum(sd, holz="oak", H=int(hh))
        elif art == "buche":
            welt = wald2.laubbaum(sd, holz="birch", H=int(hh), blaetter=[("oak", 1)])
        elif art == "fichte":
            welt = wald2.fichte(sd, H=int(hh))
        elif art == "kiefer":
            welt = wald2.kiefer(sd, H=int(hh))
        elif art == "birke":
            welt = wald2.birke(sd, H=int(hh))
        elif art == "dunkel":
            welt = wald2.dunkeleiche(sd, H=int(hh))
        elif art == "herbst":
            welt = wald2.herbstbaum(sd, H=int(hh), stil=len(gesetzt) % 3)
        else:
            welt = wald2.laubbaum(sd, holz="oak", H=int(hh))
        einfuegen(w, welt, x, y, z)
    return gesetzt


def unterwuchs(w, zellen, dichte=0.12, arten=("fern", "grass", "large_fern", "sweet_berry_bush")):
    rng = w.rng
    for (x, z), h in zellen.items():
        if h < 0 or not w.frei(x, h + 1, z):
            continue
        if rng.random() < dichte:
            a = arten[int(rng.integers(len(arten)))]
            if a == "large_fern":
                w.setze(x, h + 1, z, w.b("large_fern", half="lower"))
                w.setze(x, h + 2, z, w.b("large_fern", half="upper"))
            elif a == "sweet_berry_bush":
                w.setze(x, h + 1, z, w.b("sweet_berry_bush", age=2))
            else:
                w.setze(x, h + 1, z, w.b(a))


def tier(w, art):
    if art == "hirsch":
        f = w.b("brown_terracotta")
        hell = w.b("white_terracotta")
        g = w.b("stripped_spruce_log")
        return [(ell(0, 3.0, 0, 1.8, 0.9, 0.75), f), (kap((1.5, 3.4, 0), (2.3, 5.0, 0), 0.5, 0.4), f),
                (ell(2.7, 5.1, 0, 0.75, 0.4, 0.35), f), (ell(-1.6, 3.2, 0, 0.35, 0.35, 0.3), hell)] + \
               [(kap((sx, 2.6, sz), (sx, 0, sz), 0.22), f) for sx in (-1.2, 1.2) for sz in (-0.35, 0.35)] + \
               [(kap((2.4, 5.4, sz * 0.3), (2.0, 7.0, sz * 1.2), 0.12), g) for sz in (-1, 1)] + \
               [(kap((2.2, 6.2, sz * 0.8), (2.9, 7.2, sz * 1.4), 0.1), g) for sz in (-1, 1)]
    if art == "fuchs":
        f = w.b("orange_terracotta")
        hell = w.b("white_terracotta")
        return [(ell(0, 1.2, 0, 1.1, 0.5, 0.45), f), (ell(1.1, 1.6, 0, 0.45, 0.4, 0.4), f),
                (ell(1.5, 1.5, 0, 0.3, 0.2, 0.2), hell), (kegel(1.0, 0.25, 1.9, 2.4, 0.15, 0.02), f),
                (kegel(1.0, -0.25, 1.9, 2.4, 0.15, 0.02), f), (kap((-1.0, 1.2, 0), (-2.2, 1.0, 0), 0.4, 0.25), f),
                (ell(-2.3, 1.0, 0, 0.25, 0.25, 0.25), hell)] + \
               [(kap((sx, 0.9, sz), (sx, 0, sz), 0.12), w.b("black_terracotta")) for sx in (-0.7, 0.7)
                for sz in (-0.25, 0.25)]
    return []


# ============================================================================ Bauten

def laerchenwald(seed, g=2):
    """Lärchenwald: ein lichter Bergwald aus Lärchen mit goldgelben Nadeln im Herbst, dazwischen Heidelbeerpolster,
    Felsbrocken und ein schmaler Pfad mit Holzbank."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = wiese(w, R, 0.6, art="wald")
    rng = w.rng
    for k in range(int(10 * s + 6)):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.9
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        t = wald2.fichte(seed + k * 31, H=int(10 + rng.random() * 8 * s), schmal=0.8)
        nadel = laub(t, "spruce")
        gelb_t = MB.herbstlaub(t, "yellow_autumn")
        for p, b in list(t.bloecke.items()):
            if b == nadel and rng.random() < 0.85:
                t.bloecke[p] = gelb_t
        einfuegen(w, t, x, zellen.get((x, z), 0) + 1, z)
    for z in range(-R, R):
        x = round(math.sin(z / 6) * 3)
        if (x, z) in zellen:
            w.setze(x, zellen[(x, z)], z, w.b("dirt_path"))
    unterwuchs(w, zellen, 0.1, ("sweet_berry_bush", "fern", "grass"))
    return w


def eibenhain(seed, g=2):
    """Eibenhain: ein uralter, dunkler Hain aus knorrigen, ausladenden Eiben mit tiefgrünem Laub und roten Beeren,
    der Boden kahl und moosig, in der Mitte ein verwitterter Opferstein."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.3, art="wald", blumen=0.0)
    rng = w.rng
    for k in range(int(5 + 3 * s)):
        a = k / (5 + 3 * s) * 2 * math.pi + rng.random() * 0.4
        d = R * (0.35 + rng.random() * 0.45)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = zellen.get((x, z), 0) + 1
        H = int(5 + rng.random() * 4 * s)
        rohr(w, bez((x, y - 1, z), (x + 0.5, y + H * 0.5, z + 0.3), (x, y + H, z)), 1.0 + 0.6 * s, 0.6,
             mat=w.b("dark_oak_wood", axis="y"), rauh=0.2)
        laubball(w, x, y + H + 1, z, 3 + 1.5 * s, arten=("dark_oak_leaves", "spruce_leaves"), dicht=0.85)
        for _ in range(int(5 * s)):
            w.setze(x + int((rng.random() - 0.5) * 6 * s), y + H + int((rng.random() - 0.5) * 3),
                    z + int((rng.random() - 0.5) * 6 * s), w.b("red_concrete"), False)
    for x in range(-1, 2):
        for z in range(-1, 1):
            w.setze(x, 1, z, w.b("mossy_cobblestone"))
    w.setze(0, 2, 0, w.b("candle", candles=2, lit=True, waterlogged=False))
    unterwuchs(w, zellen, 0.05, ("moss_carpet", "fern"))
    return w


def moosfelsen(seed, g=2):
    """Moosfelsen-Wald: ein Buchenwald voller riesiger, dick bemooster Findlinge, über die Wurzeln kriechen, mit
    Farnen in den Spalten und einem kleinen Rinnsal zwischen den Steinen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.4, art="wald")
    rng = w.rng
    for k in range(int(6 + 4 * s)):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.8
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        r = 1.5 + rng.random() * 2.5 * s
        kugel(w, x, zellen.get((x, z), 0), z, r, lambda xx, yy, zz: w.b("moss_block") if yy > zellen.get((x, z), 0) + r * 0.3
              else w.b("mossy_cobblestone") if (xx + zz) % 2 else w.b("stone"), ry=r * 0.7, ueber=False)
    wald(w, zellen, R, int(6 + 3 * s), seed, arten=("buche", "eiche"))
    for z in range(-R, R):
        x = round(math.sin(z / 4) * 2) - 3
        if (x, z) in zellen and w.frei(x, zellen[(x, z)] + 1, z):
            w.setze(x, zellen[(x, z)], z, w.b("water", level=0))
    unterwuchs(w, zellen, 0.15, ("fern", "large_fern", "moss_carpet"))
    return w


def farnschlucht(seed, g=2):
    """Farnschlucht: eine enge, feuchte Schlucht mit moosgrünen Felswänden, auf deren Grund ein Bach plätschert,
    die Hänge dicht mit großen Farnen bewachsen, umgestürzte Stämme quer darüber."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 4)
    H = int(6 * s + 5)
    zellen = {}
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            mitte = math.sin(z / 5) * 2
            d = abs(x - mitte)
            h = int(min(H, max(0, (d - 2) * 1.6)) + rn(x, 3, z) * 2)
            for y in range(-2, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h and d > 4 else
                        w.b("moss_block") if y == h else w.b("stone") if (x + y) % 3 else w.b("mossy_cobblestone"))
            if d < 1.5:
                w.setze(x, 0, z, w.b("water", level=0))
            zellen[(x, z)] = h
    unterwuchs(w, zellen, 0.35, ("fern", "large_fern", "fern"))
    rng = w.rng
    for k in range(2 + g):
        z = int((rng.random() - 0.5) * R * 1.4)
        y = H - 1
        for x in range(-int(H / 1.6) - 3, int(H / 1.6) + 4):
            w.setze(x + round(math.sin(z / 5) * 2), y, z, w.b("oak_log", axis="x"))
    wald(w, {k: v for k, v in zellen.items() if v >= H - 1}, R, int(4 + 2 * s), seed, arten=("buche", "fichte"))
    return w


def hochsitz(seed, g=1):
    """Hochsitz am Waldrand: ein hölzerner Jägerstand auf hohen Stelzen mit Leiter und überdachter Kanzel am Rand
    einer Wiese, dahinter dichter Mischwald, im Gras eine Futterraufe und Wildspuren."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.2)
    wald(w, zellen, R, int(6 + 3 * s), seed, arten=("fichte", "eiche", "birke"), frei=(R * 0.25, R * 0.2, R * 0.6))
    hx, hz = -int(R * 0.2), -int(R * 0.15)
    H = int(4 * s + 4)
    for dx in (0, 2):
        for dz in (0, 2):
            for y in range(1, H + 1):
                w.setze(hx + dx, y, hz + dz, w.b("spruce_log", axis="y"))
    for dx in range(-1, 4):
        for dz in range(-1, 4):
            w.setze(hx + dx, H + 1, hz + dz, w.b("spruce_planks"))
            if dx in (-1, 3) or dz in (-1, 3):
                w.setze(hx + dx, H + 2, hz + dz, w.b("spruce_planks") if dz != 3 else w.b("spruce_fence"))
    satteldach(w, hx - 1, hz - 1, hx + 3, hz + 3, H + 4, Dachmat(w, ["spruce"]), first_x=True, ue=1, giebel=None,
               traufe="spruce")
    for y in range(1, H + 2):
        w.setze(hx + 1, y, hz + 4 + (y < 2), w.b("ladder", facing="south", waterlogged=False), False)
    fx, fz = int(R * 0.3), int(R * 0.2)
    for y in range(1, 3):
        for dx in (-1, 1):
            w.setze(fx + dx, y, fz, w.b("spruce_fence"))
    w.setze(fx, 2, fz, w.b("hay_block", axis="x"))
    satteldach(w, fx - 1, fz - 1, fx + 1, fz + 1, 3, Dachmat(w, ["spruce"]), first_x=True, ue=0, giebel=None,
               traufe="spruce")
    figur(w, 0.5 * s + 0.35, tier(w, "hirsch"), (-3, -1, -2), (4, 8, 2), pos=(fx + 4, 1, fz + 3), winkel=2.0)
    return w


def foersterhaus(seed, g=2):
    """Försterhaus: ein behagliches Fachwerkhaus mit Geweih über der Tür, Holzstapel, Hundezwinger, Pflanzgarten mit
    Setzlingen in Reihen und einem Brunnen, mitten im Hochwald."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.2)
    B, T = int(4 * s + 6) | 1, int(3 * s + 5) | 1
    haus(w, 0, -2, B, T, 1, M(w, [("white_terracotta", 2), ("calcite", 1)]), holz="dark_oak", H=4,
         dach=("dark_oak", "spruce"), tuer_s="south", steil=2)
    z1 = -2 + T // 2
    for k in range(3):
        w.setze(-1 + k, 4, z1 + 1, w.b("stripped_spruce_log", axis="y") if k != 1 else w.b("air"))
    for k in range(4):
        w.setze(B // 2 + 2, 1 + k // 2, -3 + k % 2 * 2, w.b("oak_log", axis="z"))
    for x in range(-B // 2 - 4, -B // 2 - 1):
        for z in range(z1 + 2, z1 + 2 + int(4 * s + 2)):
            w.setze(x, zellen.get((x, z), 0) + 1, z, w.b("spruce_sapling", stage=0) if (x + z) % 2 else
                    w.b("oak_sapling", stage=0))
    w.setze(B // 2 + 3, 1, z1 + 3, w.b("cobblestone_wall"))
    w.setze(B // 2 + 3, 0, z1 + 3, w.b("water", level=0))
    wald(w, zellen, R, int(8 + 3 * s), seed, arten=("fichte", "eiche", "buche"), frei=(0, 0, B * 0.9))
    return w


def waldkapelle(seed, g=1):
    """Waldkapelle: eine winzige, weiß getünchte Kapelle mit Glockentürmchen auf einer Waldlichtung, davor ein
    Wegkreuz, Bänke aus halbierten Stämmen und Kerzen in einer Nische."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.15)
    B, T = int(2 * s + 5) | 1, int(3 * s + 6) | 1
    top = haus(w, 0, -1, B, T, 1, M(w, [("white_concrete", 2), ("calcite", 1)]), holz="dark_oak", H=4,
               dach=("mcw:gray_terracotta", "deepslate_tile"), tuer_s="south", schorn=False, steil=2)
    for y in range(top - 1, top + 3):
        w.setze(0, y, -T // 2, w.b("dark_oak_planks"))
    w.setze(0, top + 1, -T // 2 + 1, w.b("bell", attachment="ceiling", facing="north", powered=False))
    kegeldach(w, 0, -T // 2, top + 3, 1, Dachmat(w, ["deepslate_tile"]), form="nadel", eckig=True, spitze="gold_block")
    kz = T // 2 + 4
    for y in range(1, 4):
        w.setze(2, y, kz, w.b("dark_oak_log", axis="y"))
    w.setze(1, 3, kz, w.b("dark_oak_fence"))
    w.setze(3, 3, kz, w.b("dark_oak_fence"))
    for k in range(2):
        for x in range(-3, 0):
            w.setze(x, 1, kz + k * 2, w.b("oak_log", axis="x"))
    wald(w, zellen, R, int(7 + 3 * s), seed, arten=("fichte", "buche"), frei=(0, 1, R * 0.5))
    return w


def biberdamm(seed, g=2):
    """Biberdamm: ein Bach, aufgestaut durch einen Damm aus kreuz und quer liegenden Ästen und Schlamm, dahinter ein
    Biberteich mit Biberburg, angenagte Baumstümpfe mit Spitzen und Biber-Figuren am Ufer."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.2, art="wald")
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if (x, z) not in zellen:
                continue
            if z < -1 and math.hypot(x, (z + R * 0.3) * 1.3) < R * 0.55:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
                zellen[(x, z)] = -1
            elif z > 1 and abs(x - round(math.sin(z / 4))) < 1.5:
                w.setze(x, -1, z, w.b("water", level=0))
                w.setze(x, 0, z, w.b("air"))
                zellen[(x, z)] = -2
    rng = w.rng
    for x in range(-int(R * 0.5), int(R * 0.5)):
        for y in range(0, 2 + int(s)):
            for z in (-1, 0, 1):
                w.setze(x, y, z, w.b("oak_log" if (x + y + z) % 3 else "mud", axis="x" if (x + y) % 2 else "z")
                        if (x + y + z) % 3 else w.b("mud"))
    bx, bz = int(R * 0.15), -int(R * 0.35)
    kugel(w, bx, 0, bz, 2.5 + s, lambda x, y, z: w.b("oak_log", axis="y") if (x + y + z) % 2 else w.b("mud"),
          ry=2 + s)
    for k in range(4 + g):
        a = rng.random() * 6.28
        x, z = round(math.cos(a) * R * 0.75), round(math.sin(a) * R * 0.75)
        if (x, z) in zellen and zellen[(x, z)] >= 0:
            y = zellen[(x, z)] + 1
            w.setze(x, y, z, w.b("birch_log", axis="y"))
            w.setze(x, y + 1, z, w.b("birch_fence"))
    br = w.b("brown_terracotta")
    for k in range(2):
        teile = [(ell(0, 0.9, 0, 1.1, 0.8, 0.8), br), (ell(1.0, 1.1, 0, 0.5, 0.45, 0.45), br),
                 (ell(-1.3, 0.3, 0, 0.9, 0.15, 0.5), w.b("black_terracotta"))]
        figur(w, 0.6 * s + 0.4, teile, (-3, -1, -2), (2, 3, 2), pos=(-int(R * 0.3) + k * 4, 1, 3), winkel=k * 2.5)
    wald(w, zellen, R, int(5 + 2 * s), seed, arten=("birke", "eiche"), innen=0.7)
    return w


def spechtlichtung(seed, g=1):
    """Spechtlichtung: eine Lichtung mit hohen, abgestorbenen Baumstämmen voller Spechthöhlen, Totholzhaufen, Pilzen
    an den Stümpfen und bunten Specht-Figuren an den Stämmen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.2, art="wald")
    rng = w.rng
    for k in range(int(4 + 2 * s)):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.5
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y0 = zellen.get((x, z), 0) + 1
        H = int(6 + rng.random() * 8 * s)
        for y in range(y0, y0 + H):
            w.setze(x, y, z, w.b("stripped_oak_log", axis="y") if (y + k) % 4 else w.b("oak_log", axis="y"))
            if y % 3 == 0:
                w.setze(x + 1, y, z, w.b("black_concrete"), False) if rng.random() < 0.4 else None
            if rng.random() < 0.1:
                w.setze(x - 1, y, z, w.b("brown_mushroom_block", north=True, south=True, east=True, west=True,
                                         up=True, down=True), False)
        if rng.random() < 0.7:
            y = y0 + int(H * 0.6)
            w.setze(x, y, z + 1, w.b("black_wool"), False)
            w.setze(x, y + 1, z + 1, w.b("red_wool"), False)
    for k in range(2 + g):
        einfuegen(w, wald2.totholz(seed + k, "oak"), int((rng.random() - 0.5) * R), 0,
                  int((rng.random() - 0.5) * R))
    wald(w, zellen, R, int(6 + 2 * s), seed, arten=("eiche", "buche"), innen=0.7)
    return w


def hirschlichtung(seed, g=2):
    """Hirschlichtung: eine nebelige Waldlichtung im Morgengrauen, auf der ein röhrender Hirsch mit mächtigem Geweih
    und zwei Hirschkühe stehen, mit hohem Gras, einem Salzleckstein und Fichten ringsum."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.2, blumen=0.0)
    unterwuchs(w, zellen, 0.35, ("grass", "grass", "fern"))
    for k, (x, z, gr) in enumerate(((0, 0, 1.0), (-4, 3, 0.8), (4, 4, 0.8))):
        teile = tier(w, "hirsch")
        if k:
            teile = teile[:-4]
        figur(w, (1.0 * s + 0.6) * gr, teile, (-3, -1, -3), (4, 8, 3), pos=(x, zellen.get((x, z), 0) + 1, z),
              winkel=k * 1.2 + 0.4)
    w.setze(6, 1, -3, w.b("white_concrete"))
    wald(w, zellen, R, int(8 + 3 * s), seed, arten=("fichte", "fichte", "eiche"), innen=0.6)
    return w


def stammbruecke(seed, g=2):
    """Stammbrücke über die Klamm: ein einzelner, mächtiger Baumstamm mit abgeflachter Lauffläche und Seilgeländer
    überspannt eine tiefe Felsklamm mit Wildbach, an beiden Seiten Bergwald."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 4)
    H = int(8 * s + 6)
    zellen = {}
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            d = abs(x - math.sin(z / 4) * 1.5)
            if d < 2 + s:
                w.setze(x, -H, z, w.b("water", level=0))
                w.setze(x, -H - 1, z, w.b("gravel"))
                continue
            for y in range(-H - 1, 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == 0 else w.b("stone") if (x + y) % 4 else
                        w.b("andesite"))
            zellen[(x, z)] = 0
    L = int(2 + s) + 4
    for x in range(-L, L + 1):
        w.setze(x, 1, 0, w.b("oak_log", axis="x"))
        w.setze(x, 2, 0, w.b("oak_slab", type="bottom", waterlogged=False))
        if x % 3 == 0:
            for sz in (-1, 1):
                w.setze(x, 2, sz, w.b("oak_fence"))
                w.setze(x, 3, sz, w.b("oak_fence"))
    wald(w, zellen, R, int(8 + 3 * s), seed, arten=("fichte", "kiefer", "fichte"), frei=(0, 0, L + 2))
    return w


def waldsee(seed, g=2):
    """Waldsee mit Steg: ein stiller, dunkler See zwischen Fichten und Birken, ein langer Holzsteg mit festgebun-
    denem Ruderboot, Seerosen, Schilf am Ufer und eine Bank zum Verweilen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.2, art="wald")
    rn = Rauschen(w, 5)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z * 1.2) < R * 0.55 + rn(x, 2, z) * 3:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
                zellen[(x, z)] = -1
    for z in range(int(R * 0.35), int(R * 0.75)):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
        if z % 3 == 0:
            for x in (-1, 1):
                w.setze(x, 0, z, w.b("spruce_log", axis="y"))
    for i in range(-2, 3):
        for q in (-1, 0, 1):
            if abs(q) <= 1.2 * math.sqrt(max(0, 1 - (i / 2.6) ** 2)):
                w.setze(2 + q, 0, int(R * 0.35) + i, w.b("spruce_planks"))
    rng = w.rng
    for k in range(int(8 * s)):
        x, z = int((rng.random() - 0.5) * R), int((rng.random() - 0.5) * R * 0.8)
        if w.hole(x, 0, z) == w.b("water", level=0):
            w.setze(x, 1, z, w.b("lily_pad"))
    wald(w, zellen, R, int(8 + 3 * s), seed, arten=("fichte", "birke"), innen=0.65)
    return w


def fuchsbau(seed, g=1):
    """Fuchsbau: ein sandiger Hang unter den Wurzeln einer Eiche mit mehreren Höhleneingängen, davor spielende Fuchs-
    welpen und eine Füchsin, abgenagte Knochen und Federn."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.2, art="wald")
    kugel(w, 0, 0, -int(R * 0.2), 5 * s + 3, lambda x, y, z: w.b("coarse_dirt") if (x + y) % 3 else w.b("dirt"),
          ry=3 * s + 2)
    baum(w, 0, int(3 * s + 2), -int(R * 0.25), seed, 10 + 4 * s)
    for k in range(3):
        x = -3 + k * 3
        z = -int(R * 0.2) + int(5 * s + 3) - 1
        for dx in (0, 1):
            for y in (1, 2):
                w.bloecke.pop((x + dx, y, z), None)
                w.bloecke.pop((x + dx, y, z - 1), None)
        w.setze(x, 0, z + 1, w.b("coarse_dirt"))
    rng = w.rng
    for k in range(3 + g):
        x, z = int((rng.random() - 0.5) * 8), int(R * 0.15) + int(rng.random() * 5)
        gr = 1.0 if k == 0 else 0.6
        figur(w, (0.6 * s + 0.4) * gr, tier(w, "fuchs"), (-3, -1, -1), (2, 3, 1),
              pos=(x, zellen.get((x, z), 0) + 1, z), winkel=rng.random() * 6.28)
    w.setze(4, 1, int(R * 0.3), w.b("bone_block", axis="x"))
    w.setze(-4, 1, int(R * 0.35), w.b("white_carpet"))
    return w


def windbruch(seed, g=2):
    """Windbruch: nach einem Sturm liegen entwurzelte Fichten kreuz und quer, ihre aufgestellten Wurzelteller ragen
    mannshoch in die Luft, dazwischen abgeknickte Stämme und erste junge Birken."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.3, art="wald")
    rng = w.rng
    for k in range(int(6 + 3 * s)):
        a = rng.random() * 6.28
        x0, z0 = int((rng.random() - 0.5) * R * 1.2), int((rng.random() - 0.5) * R * 1.2)
        L = int(8 + rng.random() * 8 * s)
        y0 = zellen.get((x0, z0), 0) + 1
        for i in range(L):
            x, z = round(x0 + math.cos(a) * i), round(z0 + math.sin(a) * i)
            ax = "x" if abs(math.cos(a)) > 0.7 else "z"
            w.setze(x, y0, z, w.b("spruce_log", axis=ax))
            if i > L * 0.6 and rng.random() < 0.5:
                w.setze(x, y0 + 1, z, w.b("spruce_leaves", persistent=True, distance=1, waterlogged=False))
        rt = 1.5 + s
        for dy in range(-int(rt), int(rt) + 1):
            for d in range(-int(rt), int(rt) + 1):
                if dy * dy + d * d <= rt * rt:
                    x = round(x0 - math.cos(a) + (-math.sin(a)) * d)
                    z = round(z0 - math.sin(a) + math.cos(a) * d)
                    w.setze(x, y0 + int(rt) + dy, z, w.b("rooted_dirt") if (dy + d) % 3 else w.b("dirt"))
    for k in range(int(3 + 2 * s)):
        x, z = int((rng.random() - 0.5) * R * 1.4), int((rng.random() - 0.5) * R * 1.4)
        if (x, z) in zellen and w.frei(x, zellen[(x, z)] + 1, z):
            einfuegen(w, wald2.jungbaum(seed + k, "birch"), x, zellen[(x, z)] + 1, z)
    for k in range(int(3 + s)):
        a = rng.random() * 6.28
        x, z = round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8)
        y = zellen.get((x, z), 0) + 1
        for yy in range(y, y + int(3 + rng.random() * 4)):
            w.setze(x, yy, z, w.b("spruce_log", axis="y"))
    return w


def wanderhuette(seed, g=1):
    """Wanderhütte mit Wegweiser: eine offene Schutzhütte aus Rundholz an einer Wegkreuzung im Wald, darin Tisch und
    Bänke, davor ein Wegweiser mit vier Armen, eine Karte und ein Brunnentrog."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.15)
    for t in range(-R, R + 1):
        for d in (-1, 0, 1):
            for (x, z) in ((t, d), (d, t)):
                if (x, z) in zellen:
                    w.setze(x, zellen[(x, z)], z, w.b("dirt_path"))
    hx, hz = -int(R * 0.35), -int(R * 0.35)
    B = int(2 * s + 3)
    for x in range(hx - B, hx + B + 1):
        for z in range(hz - B, hz + B + 1):
            w.setze(x, 0, z, w.b("spruce_planks"))
            if abs(x - hx) == B and abs(z - hz) == B:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
            elif z == hz - B:
                for y in range(1, 3):
                    w.setze(x, y, z, w.b("stripped_spruce_log", axis="x"))
    satteldach(w, hx - B, hz - B, hx + B, hz + B, 4, Dachmat(w, ["spruce", "dark_oak"]), first_x=True, ue=1,
               giebel=None, traufe="spruce")
    for x in range(hx - 1, hx + 2):
        w.setze(x, 1, hz, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x, 1, hz - 1, treppe(w, "spruce", "south"))
        w.setze(x, 1, hz + 1, treppe(w, "spruce", "north"))
    for y in range(1, 5):
        w.setze(2, y, 2, w.b("spruce_fence"))
    for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        w.setze(2 + dx, 4, 2 + dz, w.b("spruce_planks"))
    w.setze(-2, 1, 3, w.b("cobblestone_wall"))
    w.setze(-3, 1, 3, w.b("water_cauldron", level=3))
    wald(w, zellen, R, int(7 + 3 * s), seed, arten=("fichte", "buche"), frei=(0, 0, R * 0.3))
    return w


def ameisenhuegel(seed, g=1):
    """Ameisenhügel-Lichtung: eine sonnige Lichtung im Nadelwald mit mehreren mannshohen Ameisenhügeln aus Nadel-
    streu, Ameisenstraßen aus kleinen dunklen Punkten und einem Lehrpfad-Schild."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.2, art="wald")
    rng = w.rng
    for k in range(2 + g):
        a = k / (2 + g) * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.3), round(math.sin(a) * R * 0.3)
        r = 1.5 + rng.random() * s
        kugel(w, x, zellen.get((x, z), 0), z, r, lambda xx, yy, zz: w.b("brown_concrete_powder") if (xx + yy + zz) % 3
              else w.b("coarse_dirt"), ry=r * 1.3, ueber=False)
        for t in range(int(R * 0.4)):
            xx = round(x + math.cos(a + 1) * t)
            zz = round(z + math.sin(a + 1) * t)
            if (xx, zz) in zellen and t % 2:
                w.setze(xx, zellen[(xx, zz)] + 1, zz, w.b("black_carpet") if False else w.b("brown_carpet"))
    for y in range(1, 3):
        w.setze(0, y, int(R * 0.45), w.b("spruce_fence"))
    w.setze(0, 3, int(R * 0.45), w.b("spruce_planks"))
    wald(w, zellen, R, int(7 + 3 * s), seed, arten=("fichte", "kiefer"), innen=0.6)
    return w


def quellgrund(seed, g=1):
    """Quellgrund: eine von Moos und Bergahorn umgebene Quelle, die aus einem Felsspalt sprudelt, in ein gefasstes
    Becken fließt und als Bächlein über kleine Kaskaden davonplätschert, mit Trittsteinen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.3, art="wald")
    st = M(w, [("mossy_cobblestone", 2), ("stone", 1), ("moss_block", 1)])
    for x in range(-3, 4):
        for z in range(-int(R * 0.5) - 3, -int(R * 0.5) + 1):
            for y in range(1, int(4 + 2 * s)):
                w.setze(x, y, z, st(x, y, z))
    w.setze(0, int(2 + s), -int(R * 0.5) + 1, w.b("water", level=0))
    for x in range(-2, 3):
        for z in range(-int(R * 0.5) + 2, -int(R * 0.5) + 5):
            w.setze(x, 0, z, w.b("water", level=0))
            if abs(x) == 2 or z == -int(R * 0.5) + 4:
                w.setze(x, 1, z, w.b("mossy_stone_bricks"))
    for z in range(-int(R * 0.5) + 5, R):
        x = round(math.sin(z / 3))
        if (x, z) in zellen:
            w.setze(x, zellen[(x, z)], z, w.b("water", level=0))
            if z % 5 == 0:
                w.setze(x + 1, zellen[(x, z)], z, w.b("stone"))
    wald(w, zellen, R, int(6 + 2 * s), seed, arten=("eiche", "buche"), innen=0.55)
    unterwuchs(w, zellen, 0.2, ("fern", "moss_carpet", "large_fern"))
    return w


def kletterwald(seed, g=2):
    """Kletterwald: ein Hochseilgarten zwischen dicken Waldbäumen, mit Plattformen, Hängebrücken aus Brettern,
    Netzen, Seilrutschen und Kletterwänden, unten ein Kassenhäuschen und Helmregal."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.15, art="wald")
    pos = wald(w, zellen, R, int(5 + 2 * s), seed, arten=("eiche", "buche"), innen=0.2, H=(14, 20))
    yp = int(6 * s + 5)
    for x, z in pos:
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if abs(dx) + abs(dz) <= 3 and (dx, dz) != (0, 0):
                    w.setze(x + dx, yp, z + dz, w.b("spruce_planks"), False)
    for (a, b) in zip(pos, pos[1:]):
        n = int(math.hypot(b[0] - a[0], b[1] - a[1]))
        for k in range(n + 1):
            t = k / max(1, n)
            x, z = round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t)
            y = yp - round(1.2 * math.sin(math.pi * t))
            if k % 2 == 0:
                w.setze(x, y, z, w.b("spruce_slab", type="bottom", waterlogged=False), False)
            w.setze(x, y + 2, z, w.b("chain", axis="x" if abs(b[0] - a[0]) > abs(b[1] - a[1]) else "z",
                                     waterlogged=False), False)
    if pos:
        x, z = pos[0]
        for y in range(1, yp):
            w.setze(x + 3, y, z, w.b("cobweb") if y % 2 else w.b("spruce_fence"), False)
    haus(w, int(R * 0.5), int(R * 0.6), 4, 4, 1, M(w, [("spruce_planks", 1)]), holz="spruce", H=3, tuer_s="west",
         schorn=False)
    return w


def beerenhecke(seed, g=1):
    """Beerenhecke am Waldrand: ein dichter Saum aus Brombeer-, Himbeer- und Holunderbüschen zwischen Wiese und Wald,
    Körbe und eine Leiter zum Pflücken, Vogelnester in den Zweigen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.2, blumen=0.06)
    rng = w.rng
    for x in range(-R, R + 1):
        z = round(math.sin(x / 4) * 2) - 2
        for dz in range(-1, 2):
            if (x, z + dz) in zellen:
                y = zellen[(x, z + dz)] + 1
                w.setze(x, y, z + dz, w.b("sweet_berry_bush", age=3) if (x + dz) % 3 else
                        w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
                if rng.random() < 0.4:
                    w.setze(x, y + 1, z + dz, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False))
    for k in range(3):
        x = -int(R * 0.4) + k * int(R * 0.4)
        w.setze(x, zellen.get((x, 3), 0) + 1, 3, w.b("composter", level=5))
    for y in range(1, 4):
        w.setze(2, y, 0, w.b("ladder", facing="south", waterlogged=False), False)
    wald(w, {k: v for k, v in zellen.items() if k[1] < -4}, R, int(6 + 3 * s), seed, arten=("eiche", "birke"))
    return w


def riesenstumpf(seed, g=2):
    """Riesenstumpf: der gewaltige, hohle Stumpf eines einst riesigen Baumes, dessen Jahresringe auf der Schnittfläche
    sichtbar sind; Pilze wachsen an den Seiten, ein Tunnel führt hindurch, junge Bäume sprießen oben."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.2, art="wald")
    r = 4 * s + 3
    H = int(4 * s + 4)
    for y in range(1, H + 1):
        rr = r + (1.2 if y < 3 else 0)
        for x in range(-int(rr) - 1, int(rr) + 2):
            for z in range(-int(rr) - 1, int(rr) + 2):
                d = math.hypot(x, z)
                if d <= rr:
                    if y == H:
                        ring = int(d) % 2
                        w.setze(x, y, z, w.b("stripped_oak_wood", axis="y") if ring else w.b("oak_planks"))
                    elif d > rr - 1.3:
                        w.setze(x, y, z, w.b("oak_log", axis="y"))
                    elif d < r * 0.4:
                        w.bloecke.pop((x, y, z), None)
                    else:
                        w.setze(x, y, z, w.b("stripped_oak_wood", axis="y"))
    for z in range(-int(r) - 2, int(r) + 3):
        for x in (-1, 0, 1):
            for y in (1, 2):
                w.bloecke.pop((x, y, z), None)
    rng = w.rng
    for k in range(int(8 * s)):
        a = rng.random() * 6.28
        y = int(2 + rng.random() * (H - 3))
        x, z = round(math.cos(a) * (r + 1.2)), round(math.sin(a) * (r + 1.2))
        w.setze(x, y, z, w.b("brown_mushroom_block", north=True, south=True, east=True, west=True, up=True, down=True),
                False)
    for k in range(2 + g):
        a = rng.random() * 6.28
        x, z = round(math.cos(a) * r * 0.6), round(math.sin(a) * r * 0.6)
        einfuegen(w, wald2.jungbaum(seed + k, "oak"), x, H + 1, z)
    wald(w, zellen, R, int(5 + 2 * s), seed, arten=("eiche", "buche"), innen=0.75)
    return w


WALD3 = {
    "laerchenwald": ("Lärchenwald", laerchenwald),
    "eibenhain": ("Eibenhain", eibenhain),
    "moosfelsen": ("Moosfelsen-Wald", moosfelsen),
    "farnschlucht": ("Farnschlucht", farnschlucht),
    "hochsitz": ("Hochsitz am Waldrand", hochsitz),
    "foersterhaus": ("Försterhaus", foersterhaus),
    "waldkapelle": ("Waldkapelle", waldkapelle),
    "biberdamm": ("Biberdamm", biberdamm),
    "spechtlichtung": ("Spechtlichtung", spechtlichtung),
    "hirschlichtung": ("Hirschlichtung", hirschlichtung),
    "stammbruecke": ("Stammbrücke über die Klamm", stammbruecke),
    "waldsee": ("Waldsee mit Steg", waldsee),
    "fuchsbau": ("Fuchsbau", fuchsbau),
    "windbruch": ("Windbruch", windbruch),
    "wanderhuette": ("Wanderhütte mit Wegweiser", wanderhuette),
    "ameisenhuegel": ("Ameisenhügel-Lichtung", ameisenhuegel),
    "quellgrund": ("Quellgrund", quellgrund),
    "kletterwald": ("Kletterwald", kletterwald),
    "beerenhecke": ("Beerenhecke am Waldrand", beerenhecke),
    "riesenstumpf": ("Riesenstumpf", riesenstumpf),
}

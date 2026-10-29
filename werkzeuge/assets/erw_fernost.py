"""Fernost II – zwanzig weitere Bauten im fernöstlichen Stil: Laternentreppe, Koi-Teich mit Zickzackbrücke,
Wasserfall-Tempel, Stelzendorf, Flusshafen, Bergtorhaus, Teeplantage, Lesepavillon im Bambus, Glockentor, Heiße
Quellen, Kranichteich, Pflaumenblüten-Hof, Klingenschmiede, Löwenbrücke, Riesenbonsai, Klippenkloster,
Drachensäule, Nachtmarkt, Reisspeicher und Reismühle."""

from __future__ import annotations

import math

from fernost import (U, Ost, _r, _welt, bambus, geschoss, kiesgarten, kirsche, ostdach, steinlaterne, teich,
                     terrasse, torii)
from feinbau import kram, platte, treppe, zaun
from leuchtwald2 import bez, kugel, rohr
from lib import einfuegen
from pracht import gelaende
from weltwunder import hohl


def halle(w, o, cx, cz, a, b, y, h=4, stock=1, ue=3, tuer="south"):
    for k in range(stock):
        aa, bb = a - k, b - k
        if aa < 1 or bb < 1:
            break
        geschoss(w, o, cx - aa, cz - bb, cx + aa, cz + bb, y, h if k == 0 else 3, tuer=tuer)
        y = ostdach(w, o, cx - aa, cz - bb, cx + aa, cz + bb, y + (h if k == 0 else 3), ue=ue) - max(aa, bb) + 1 \
            if k < stock - 1 else ostdach(w, o, cx - aa, cz - bb, cx + aa, cz + bb, y + (h if k == 0 else 3), ue=ue)
    return y


def wasser(w, x0, z0, x1, z1, tief=2):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            for y in range(-tief + 1, 1):
                w.setze(x, y, z, w.b("water", level=0))
            w.setze(x, -tief, z, w.b("gravel"))
            w.bloecke.pop((x, 1, z), None)


# ============================================================================ Bauten

def laternentreppe(seed, g=2):
    """Laternentreppe: eine lange, steile Steintreppe führt durch einen Bergwald hinauf, gesäumt von dutzenden
    Steinlaternen und roten Toren, oben wartet ein kleiner Schrein."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    n = _r(14 * u + 6, 8)
    gelaende(w, n + 6, art="wald")
    for i in range(n):
        y = 1 + i // 2 * 1
        for x in range(-1, 2):
            for yy in range(1, y + 1):
                w.setze(x, yy, n - i, o.terr(x, yy, n - i, 0.4))
            w.setze(x, y + 1, n - i, treppe(w, "stone_brick", "south"))
        for sx in (-3, 3):
            for yy in range(1, y + 1):
                w.setze(sx, yy, n - i, w.b("dirt"))
            w.setze(sx, y + 1, n - i, w.b("grass_block", snowy=False))
            if i % 4 == 0:
                steinlaterne(w, sx, n - i, y + 2)
        if i % 8 == 4:
            torii(w, o, 0, n - i, 2, _r(4 * u + 3, 4) + y, achse="z")
    ytop = 1 + (n - 1) // 2 + 1
    for x in range(-4, 5):
        for z in range(-4, 1):
            for yy in range(1, ytop + 1):
                w.setze(x, yy, z, o.terr(x, yy, z, 0.4))
    halle(w, o, 0, -2, 2, 2, ytop + 1, h=3)
    hohl(w, 2)
    return w


def koiteich(seed, g=1):
    """Koi-Teich mit Zickzackbrücke: ein großer Gartenteich mit bunten Koi, eine hölzerne Zickzackbrücke quert ihn,
    am Ufer ein Pavillon, Trauerweiden und runde Trittsteine."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(9 * u + 4, 6)
    gelaende(w, R + 6, art="wiese")
    teich(w, 0, 0, R)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y == -1 and w.P.name(b) == "minecraft:water" and rng.random() < 0.05:
            w.setze(x, -1, z, w.b(["orange_concrete", "white_concrete", "red_concrete"][int(rng.random() * 3)]))
    x, z = -R, 0
    for k in range(R * 2 + 1):
        seg = (k // 4) % 2
        dz = 1 if seg else -1
        for q in (0, 1):
            w.setze(-R + k, 1, z + q, w.b(f"{o.holz}_planks"))
        if k % 4 == 3:
            z += dz * 2
    halle(w, o, R + 3, -R // 2, 2, 2, 1, h=3)
    hohl(w, 2)
    return w


def wasserfalltempel(seed, g=2):
    """Wasserfall-Tempel: ein Tempel mit geschwungenem Dach klebt an einer Felswand neben einem hohen Wasserfall, der
    in ein Becken stürzt, eine Brücke führt vor dem Fall vorbei."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    H = _r(16 * u + 6, 10)
    R = _r(12 * u + 5, 8)
    gelaende(w, R + 4, art="wald")
    rng = w.rng
    for x in range(-R, R + 1):
        for z in range(-R, -R // 3):
            for y in range(1, H + 1 - int(abs(x) * 0.2)):
                w.setze(x, y, z, w.b(["stone", "andesite", "mossy_cobblestone", "tuff"][int(rng.random() * 4)]))
    zf = -R // 3
    for x in range(-2, 3):
        for y in range(1, H + 1):
            w.setze(x, y, zf, w.b("water", level=0))
    wasser(w, -5, zf + 1, 5, zf + 6)
    for x in range(-6, 7):
        w.setze(x, 4, zf + 3, w.b(f"{o.holz}_planks"))
    ty = _r(H * 0.5, 4)
    for x in range(R // 3, R // 3 + 9):
        for z in range(zf - 1, zf + 6):
            for y in range(1, ty):
                if (x, z) in ((R // 3, zf + 5), (R // 3 + 8, zf + 5)):
                    w.setze(x, y, z, o.saeule)
    for x in range(R // 3, R // 3 + 9):
        for z in range(zf, zf + 6):
            w.setze(x, ty, z, w.b(f"{o.holz}_planks"))
    halle(w, o, R // 3 + 4, zf + 2, 3, 2, ty + 1, h=3)
    hohl(w, 2)
    return w


def stelzendorf(seed, g=2):
    """Stelzendorf: Holzhäuser mit geschwungenen Dächern stehen auf Pfählen über einem Flussarm, verbunden durch
    Stege, Sampans liegen dazwischen, Laternen an Schnüren."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(14 * u + 6, 8)
    gelaende(w, R + 4, art="wiese")
    wasser(w, -R, -R // 2, R, R // 2)
    n = 3 + g
    pos = []
    for k in range(n):
        cx = int((k - (n - 1) / 2) * 7)
        cz = (k % 2) * 4 - 2
        for (dx, dz) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            for y in range(-1, 3):
                w.setze(cx + dx, y, cz + dz, o.saeule)
        halle(w, o, cx, cz, 2, 2, 3, h=3, ue=2)
        pos.append((cx, cz))
    for (a, b) in zip(pos, pos[1:]):
        for x in range(a[0], b[0] + 1):
            w.setze(x, 2, (a[1] + b[1]) // 2, w.b(f"{o.holz}_slab", type="top", waterlogged=False), False)
    hohl(w, 2)
    return w


def flusshafen(seed, g=2):
    """Flusshafen: ein steinerner Kai am Fluss mit Lagerhäusern unter geschwungenen Dächern, Hebekran aus Bambus,
    Warenstapeln und zwei Dschunken-Sampans."""
    from boote import dschunke
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(14 * u + 6, 9)
    gelaende(w, R + 4, art="wiese")
    wasser(w, -R, 3, R, R)
    for x in range(-R, R + 1):
        for z in (1, 2):
            w.setze(x, 1, z, o.terr(x, 1, z, 0.4))
    for k in range(2):
        halle(w, o, -R // 2 + k * R, -4, 3, 2, 1, h=4, ue=2)
    einfuegen(w, dschunke(seed, max(0, g - 2)), 0, 0, 3 + _r(4 * u, 3))
    kram(w, R // 3, 2, 1, 6)
    hohl(w, 2)
    return w


def torhausfestung(seed, g=2):
    """Bergtorhaus: ein mächtiges Torhaus aus geböschtem Steinsockel mit hölzernem Wachgeschoss und doppeltem
    Walmdach sperrt einen Pass, Mauern laufen die Hänge hinauf."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(14 * u + 6, 9)
    gelaende(w, R + 4, art="wald")
    rng = w.rng
    for x in range(-R, R + 1):
        h = int(abs(x) * 0.6)
        for z in range(-R, R + 1):
            for y in range(1, h + 1):
                w.setze(x, y, z, w.b(["stone", "andesite", "tuff"][int(rng.random() * 3)]))
    a = _r(4 * u + 2, 3)
    hs = _r(4 * u + 2, 3)
    for y in range(1, hs + 1):
        for x in range(-a - (hs - y) // 2, a + (hs - y) // 2 + 1):
            for z in range(-3, 4):
                w.setze(x, y, z, o.terr(x, y, z, 0.4))
    for y in range(1, 4):
        for z in range(-4, 5):
            for x in range(-1, 2):
                w.bloecke.pop((x, y, z), None)
    halle(w, o, 0, 0, a, 3, hs + 1, h=3, stock=2)
    for x in range(a + 2, R):
        y = int(x * 0.6) + 1
        for yy in range(y, y + 3):
            w.setze(x, yy, 0, o.terr(x, yy, 0, 0.4))
            w.setze(-x, yy, 0, o.terr(-x, yy, 0, 0.4))
    hohl(w, 2)
    return w


def teeplantage(seed, g=2):
    """Teeplantage: an einem Hang wachsen Teesträucher in geschwungenen Reihen auf Terrassen, oben ein Trockenhaus
    mit offenen Seiten und Körben, Pflückerhüte an Haken."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(14 * u + 6, 9)
    gelaende(w, R + 2, art="wiese")
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            h = max(0, int((R - z) / 3)) if math.hypot(x, z) <= R else 0
            for y in range(1, h + 1):
                w.setze(x, y, z, w.b("dirt") if y < h else w.b("grass_block", snowy=False))
            if h and (z + int(2 * math.sin(x * 0.3))) % 3 == 0 and w.frei(x, h + 1, z):
                w.setze(x, h + 1, z, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False))
    halle(w, o, 0, -R + 3, 3, 2, int(2 * R / 3) + 1, h=3, ue=2)
    hohl(w, 2)
    return w


def lesepavillon(seed, g=1):
    """Lesepavillon im Bambus: ein kleiner offener Pavillon mitten in einem dichten Bambushain, ein Pfad aus
    Trittsteinen führt hinein, Schriftrollen-Regal und Teetisch."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(10 * u + 5, 7)
    gelaende(w, R + 3, art="wald")
    bambus(w, 0, 0, R, 0.45)
    for x in range(-4, 5):
        for z in range(-4, 5):
            for y in range(1, 12):
                w.bloecke.pop((x, y, z), None)
    for (x, z) in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        for y in range(1, 5):
            w.setze(x, y, z, o.saeule)
    for x in range(-3, 4):
        for z in range(-3, 4):
            w.setze(x, 1, z, w.b(f"{o.holz}_planks"))
    ostdach(w, o, -3, -3, 3, 3, 5, ue=2)
    w.setze(0, 2, 0, w.b(f"{o.holz}_slab", type="bottom", waterlogged=False))
    w.setze(-2, 2, -2, w.b("bookshelf"))
    for z in range(4, R + 1, 2):
        w.setze(0, 0, z, w.b("smooth_stone"))
    return w


def glockentor(seed, g=2):
    """Glockentor: ein zweigeschossiges Tor mit offener Glockenstube im Obergeschoss, in der eine große Bronzeglocke
    hängt, ein Holzbalken zum Anschlagen, Steinlöwen davor."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    gelaende(w, _r(10 * u + 5, 7), art="wiese")
    a = _r(3 * u + 2, 3)
    y = terrasse(w, o, -a - 2, -3, a + 2, 3, 2)
    for x in range(-a, a + 1):
        for z in range(-2, 3):
            if abs(x) <= 1:
                continue
            for yy in range(y, y + 4):
                if abs(x) == a or abs(z) == 2:
                    w.setze(x, yy, z, o.wand(x, yy, z, 0.5))
    for x in range(-a, a + 1):
        for z in range(-2, 3):
            w.setze(x, y + 4, z, w.b(f"{o.holz}_planks"))
    for (x, z) in ((-a, -2), (a, -2), (-a, 2), (a, 2)):
        for yy in range(y + 5, y + 9):
            w.setze(x, yy, z, o.saeule)
    w.setze(0, y + 8, 0, w.b("bell", attachment="ceiling", facing="north", powered=False))
    ostdach(w, o, -a, -2, a, 2, y + 9, ue=2)
    for sx in (-1, 1):
        w.setze(sx * (a + 3), 1, 4, w.b("stone_bricks"))
        w.setze(sx * (a + 3), 2, 4, w.b("chiseled_stone_bricks"))
    return w


def onsen(seed, g=2):
    """Heiße Quellen: dampfende Becken zwischen moosigen Felsen, ein Badehaus mit Holzdach und Bambuszaun, Dampf
    steigt über den Becken auf, Steinlaternen am Rand."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(12 * u + 5, 8)
    gelaende(w, R + 3, art="wald")
    rng = w.rng
    for k in range(2 + g):
        a = k / (2 + g) * 6.283
        cx, cz = round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)
        r = 2 + u * 2
        for x in range(int(cx - r) - 2, int(cx + r) + 3):
            for z in range(int(cz - r) - 2, int(cz + r) + 3):
                d = math.hypot(x - cx, z - cz)
                if d < r:
                    w.setze(x, 0, z, w.b("water", level=0))
                    w.setze(x, -1, z, w.b("smooth_stone"))
                    w.bloecke.pop((x, 1, z), None)
                    if rng.random() < 0.06:
                        w.setze(x, -1, z, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                              waterlogged=False))
                elif d < r + 1.5:
                    w.setze(x, 1, z, w.b(["mossy_cobblestone", "stone", "andesite"][int(rng.random() * 3)]))
        steinlaterne(w, round(cx + r + 2), cz)
    halle(w, o, 0, -R + 4, 3, 2, 1, h=3)
    hohl(w, 2)
    return w


def kranichteich(seed, g=1):
    """Kranichteich: in einem stillen Teich stehen zwei elegante Kranich-Statuen aus weißem Stein auf je einem Bein,
    Schilf und Lotus ringsum, eine Steinbank am Ufer."""
    from skulptur import Skulptur, ell, kap
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(8 * u + 4, 6)
    gelaende(w, R + 3, art="wiese")
    teich(w, 0, 0, R)
    for k, (cx, cz) in enumerate(((-2, 0), (3, 1))):
        S = Skulptur(w, u)
        S.mat("w", w.b("white_concrete"))
        S.mat("d", w.b("black_concrete"))
        S.mat("r", w.b("red_concrete"))
        S.plus(kap((0, 0, 0), (0, 4, 0), 0.25), "d")
        S.plus(ell(0, 5, 0, 1.0, 1.0, 2.0), "w")
        S.plus(kap((0, 5.5, 1.5), (0, 8.5, 2.2 + k * 0.6), 0.35, 0.3), "w")
        S.plus(ell(0, 8.7, 2.5 + k * 0.6, 0.45, 0.45, 0.6), "r")
        S.plus(kap((0, 8.6, 3.0 + k * 0.6), (0, 8.3, 4.2 + k * 0.6), 0.2, 0.1), "d")
        S.plus(ell(0, 5.2, -1.8, 0.9, 0.6, 1.0), "d")
        S.rendern((-2, 0, -4), (2, 10, 6), versatz=(cx + 0.5, 1, cz + 0.5))
    for k in range(int(10 * u)):
        a = w.rng.random() * 6.283
        x, z = round(math.cos(a) * (R + 0.5)), round(math.sin(a) * (R + 0.5))
        for y in range(1, 3):
            w.setze(x, y, z, w.b("sugar_cane", age=0))
    return w


def pflaumenhof(seed, g=2):
    """Pflaumenblüten-Hof: ein von weißen Mauern mit Ziegelabdeckung umschlossener Hof, in dem rosa und weiß
    blühende Bäume stehen, ein runder Mondtor-Durchgang und eine Halle an der Stirnseite."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(10 * u + 5, 7)
    gelaende(w, R + 3, art="wiese")
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if max(abs(x), abs(z)) == R:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("white_terracotta"))
                w.setze(x, 4, z, w.b("deepslate_tile_slab", type="bottom", waterlogged=False))
    rr = 2
    for x in range(-rr, rr + 1):
        for y in range(1, 4):
            if x * x + (y - 2) ** 2 <= rr * rr + 0.5:
                w.bloecke.pop((x, y, R), None)
    halle(w, o, 0, -R + 3, 3, 2, 1, h=4)
    for k in range(3 + g):
        kirsche(w, int((k - (2 + g) / 2) * 4), 2, 0)
    hohl(w, 2)
    return w


def klingenschmiede(seed, g=1):
    """Klingenschmiede: eine offene Werkstatt mit Esse, Amboss, Wasserbottich und Schleifsteinen, an der Wand
    hängen gebogene Klingen, ein Wohnbau mit Garten dahinter."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    gelaende(w, _r(9 * u + 5, 7), art="wiese")
    for (x, z) in ((-4, -3), (4, -3), (-4, 3), (4, 3)):
        for y in range(1, 5):
            w.setze(x, y, z, o.saeule)
    ostdach(w, o, -4, -3, 4, 3, 5, ue=2)
    for x in range(-4, 5):
        for y in range(1, 5):
            w.setze(x, y, -3, o.wand(x, y, -3, 0.5))
    w.setze(-2, 1, -2, w.b("blast_furnace", facing="south", lit=True))
    w.setze(0, 1, 0, w.b("anvil", facing="east"))
    w.setze(2, 1, -2, w.b("water_cauldron", level=3))
    w.setze(3, 1, 1, w.b("grindstone", face="floor", facing="south"))
    for x in (-1, 1, 3):
        w.setze(x, 3, -2, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
    halle(w, o, 0, -9, 3, 2, 1, h=3)
    hohl(w, 2)
    return w


def loewenbruecke(seed, g=2):
    """Löwenbrücke: eine geschwungene Steinbogenbrücke mit vielen Bögen über einen breiten Fluss, auf jedem
    Geländerpfosten sitzt ein kleiner Steinlöwe, ein Pavillon in der Mitte."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    L = _r(16 * u + 8, 10)
    gelaende(w, L + 3, art="wiese")
    wasser(w, -L, -_r(6 * u + 3, 4), L, _r(6 * u + 3, 4))
    for z in range(-L, L + 1):
        t = z / L
        y = round((1 - t * t) * 4 * u) + 2
        for x in range(-2, 3):
            w.setze(x, y, z, o.terr(x, y, z, 0.4))
            w.setze(x, y - 1, z, o.terr(x, y, z, 0.4))
        for sx in (-3, 3):
            w.setze(sx, y, z, w.b("stone_brick_wall", up=True, north="low", south="low", east="none", west="none",
                                  waterlogged=False))
            if z % 3 == 0:
                w.setze(sx, y + 1, z, w.b("chiseled_stone_bricks"))
    yc = round(4 * u) + 3
    for (x, z) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        for y in range(yc, yc + 3):
            w.setze(x, y, z, o.saeule)
    ostdach(w, o, -2, -2, 2, 2, yc + 3, ue=2)
    return w


def bonsairiese(seed, g=2):
    """Riesenbonsai: ein gewaltiger, kunstvoll geformter Bonsai wächst aus einer flachen Steinschale auf einem
    Felssockel, mit verdrehtem Stamm und wolkenförmigen Laubpolstern."""
    from leuchtwald2 import laubball
    w = _welt(seed)
    u = U[g]
    gelaende(w, _r(9 * u + 4, 6), art="wiese")
    R = 5 * u + 2
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R * 0.7) - 1, int(R * 0.7) + 2):
            if (x / R) ** 2 + (z / (R * 0.7)) ** 2 <= 1:
                w.setze(x, 1, z, w.b("brown_terracotta"))
                w.setze(x, 2, z, w.b("moss_block") if (x / R) ** 2 + (z / (R * 0.7)) ** 2 < 0.8 else
                        w.b("brown_terracotta"))
    pts = bez((0, 2, 0), (3 * u, 6 * u, 0), (-2 * u, 10 * u, 1), (2 * u, 13 * u, 0))
    rohr(w, pts, 1.3 * u + 0.5, 0.6, w.b("spruce_wood", axis="y"))
    for (x, y, z, r) in ((4 * u, 8 * u, 1, 2.5), (-3 * u, 10 * u, -1, 2.2), (2 * u, 13.5 * u, 0, 2.8),
                         (-1 * u, 12 * u, 2, 1.8)):
        rohr(w, bez((0, y - 1.5 * u, 0), (x * 0.5, y, z * 0.5), (x, y, z)), 0.5 * u + 0.3, 0.3,
             w.b("spruce_wood", axis="y"))
        laubball(w, x, y + 0.5, z, r * u + 0.8, ("oak_leaves", "azalea_leaves", "oak_leaves"), 0.95)
    return w


def klippenkloster(seed, g=2):
    """Klippenkloster: an eine senkrechte Felswand gebaute Hallen auf Holzstreben, verbunden durch Galerien und
    Stege, rote Säulen und geschwungene Dächer über einer Schlucht."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    H = _r(18 * u + 6, 10)
    R = _r(14 * u + 5, 8)
    gelaende(w, R, art="wald")
    rng = w.rng
    for x in range(-R, R + 1):
        for z in range(-R, -3):
            for y in range(1, H + 1):
                w.setze(x, y, z, w.b(["stone", "andesite", "tuff"][int(rng.random() * 3)]))
    for k in range(2 + g):
        cx = int((k - (1 + g) / 2) * 10)
        y = 4 + k * _r(4 * u, 3)
        for x in range(cx - 4, cx + 5):
            for z in range(-3, 3):
                w.setze(x, y - 1, z, w.b(f"{o.holz}_planks"))
        for x in (cx - 3, cx + 3):
            for yy in range(1, y - 1):
                w.setze(x, yy, 1, w.b(f"{o.holz}_fence", north=False, south=False, east=False, west=False,
                                      waterlogged=False))
        halle(w, o, cx, -1, 3, 2, y, h=3, ue=2)
    hohl(w, 2)
    return w


def drachensaeule(seed, g=2):
    """Drachensäule: um eine hohe rote Säule windet sich ein goldgrüner Drache mit Schuppen, Mähne und Perle in den
    Klauen, auf einem Marmorsockel mit Wolkenreliefs."""
    w = _welt(seed)
    u = U[g]
    gelaende(w, _r(8 * u + 4, 6), art="wiese")
    H = _r(16 * u + 6, 10)
    for y in range(1, 4):
        for x in range(-3, 4):
            for z in range(-3, 4):
                w.setze(x, y, z, w.b("smooth_quartz" if y < 3 else "chiseled_quartz_block"))
    for y in range(4, H):
        for x in range(-1, 2):
            for z in range(-1, 2):
                w.setze(x, y, z, w.b("red_concrete"))
    pts = []
    for i in range(int(H * 4)):
        t = i / (H * 4)
        a = t * 6.283 * 2.5
        pts.append((math.cos(a) * 2.6, 4 + t * (H - 5), math.sin(a) * 2.6, t))
    rohr(w, pts, 0.9 * u + 0.3, 0.9 * u + 0.4, lambda x, y, z, t: w.b("gold_block" if (y % 2) else
                                                                    "lime_terracotta"))
    x, y, z, _ = pts[-1]
    kugel(w, x, y + 1, z, 1.2 * u + 0.6, w.b("lime_terracotta"))
    kugel(w, -x, y + 1, -z, 0.9 * u + 0.4, w.b("pearlescent_froglight", axis="y"))
    return w


def nachtmarkt(seed, g=2):
    """Nachtmarkt: eine Gasse voller Garküchen und Marktstände unter Stoffdächern, Ketten von Papierlaternen in
    Rot und Gold zwischen Stangen, Dampfkessel und Hocker."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    L = _r(14 * u + 6, 9)
    gelaende(w, L + 3, art="wiese")
    for x in range(-L, L + 1):
        for z in range(-1, 2):
            w.setze(x, 0, z, w.b("stone_bricks" if (x + z) % 2 else "polished_andesite"))
    farben = ["red_wool", "orange_wool", "yellow_wool"]
    for k, x in enumerate(range(-L + 2, L - 1, 5)):
        for sz in (-1, 1):
            z = sz * 4
            for (dx, dz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                for y in range(1, 4):
                    w.setze(x + dx, y, z + dz, w.b(f"{o.holz}_fence", north=False, south=False, east=False,
                                                   west=False, waterlogged=False))
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    w.setze(x + dx, 4, z + dz, w.b(farben[(k + dx) % 3]))
            w.setze(x, 1, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)
                    if (k + sz) % 2 else w.b("barrel", facing="up", open=False))
    for x in range(-L, L + 1):
        w.setze(x, 5, 0, w.b("chain", axis="x", waterlogged=False) if x % 3 else
                w.b("red_stained_glass" if x % 2 else "yellow_stained_glass"), False)
    return w


def reisspeicher(seed, g=1):
    """Reisspeicher: ein hölzerner Speicher auf hohen Pfählen mit Nagerschutz-Scheiben, steilem Strohdach und einer
    Leiter, Reissäcke und Dreschflegel davor, ein kleines Reisfeld."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    gelaende(w, _r(9 * u + 4, 6), art="wiese")
    a = _r(2 * u + 2, 2)
    for (x, z) in ((-a, -a), (a, -a), (-a, a), (a, a)):
        for y in range(1, 4):
            w.setze(x, y, z, o.saeule)
        w.setze(x, 3, z, w.b("smooth_stone_slab", type="top", waterlogged=False))
    geschoss(w, o, -a, -a, a, a, 4, 3, veranda=False)
    from feinbau import Dachmat, satteldach
    satteldach(w, -a, -a, a, a, 7, Dachmat(w, ["mcw:yellow_terracotta" if False else "spruce", "dark_oak"]),
               first_x=True, ue=1, traufe="spruce", steil=2)
    for x in range(a + 3, a + 9):
        for z in range(-3, 4):
            w.setze(x, 0, z, w.b("water", level=0) if (x + z) % 2 else w.b("mud"))
            if (x + z) % 2 == 0:
                w.setze(x, 1, z, w.b("wheat", age=5))
    for k in range(3):
        w.setze(-a - 2, 1, -1 + k, w.b("white_wool"))
    return w


def reismuehle(seed, g=2):
    """Reismühle: ein Mühlenhaus mit großem Wasserrad an einem gemauerten Kanal, Stampfer klopfen im Inneren,
    Säcke und Körbe am Ufer, eine kleine Brücke."""
    w = _welt(seed)
    o = Ost(w, seed)
    u = U[g]
    R = _r(10 * u + 5, 7)
    gelaende(w, R + 3, art="wiese")
    wasser(w, -R, 4, R, 6)
    halle(w, o, 0, -1, 3, 3, 1, h=4)
    rr = _r(3 * u + 1, 2)
    for k in range(rr * 8):
        a = k / (rr * 8) * 6.283
        for r in range(rr + 1):
            if r == rr or k % rr == 0:
                for dx in (0, 1):
                    w.setze(round(math.cos(a) * r), round(rr + math.sin(a) * r), 4 + dx, w.b(f"{o.holz}_planks")
                            if r == rr else w.b("stripped_spruce_log", axis="y"), False)
    for x in range(-2, 3):
        w.setze(x, 1, R - 1, w.b(f"{o.holz}_slab", type="bottom", waterlogged=False)) if False else None
    kram(w, 5, 1, 2, 4)
    hohl(w, 2)
    return w


FERNOST3 = {
    "laternentreppe": ("Laternentreppe", laternentreppe),
    "koiteich": ("Koi-Teich mit Zickzackbrücke", koiteich),
    "wasserfalltempel": ("Wasserfall-Tempel", wasserfalltempel),
    "stelzendorf": ("Stelzendorf", stelzendorf),
    "flusshafen": ("Flusshafen", flusshafen),
    "torhausfestung": ("Bergtorhaus", torhausfestung),
    "teeplantage": ("Teeplantage", teeplantage),
    "lesepavillon": ("Lesepavillon im Bambus", lesepavillon),
    "glockentor": ("Glockentor", glockentor),
    "onsen": ("Heiße Quellen", onsen),
    "kranichteich": ("Kranichteich", kranichteich),
    "pflaumenhof": ("Pflaumenblüten-Hof", pflaumenhof),
    "klingenschmiede": ("Klingenschmiede", klingenschmiede),
    "loewenbruecke": ("Löwenbrücke", loewenbruecke),
    "bonsairiese": ("Riesenbonsai", bonsairiese),
    "klippenkloster": ("Klippenkloster", klippenkloster),
    "drachensaeule": ("Drachensäule", drachensaeule),
    "nachtmarkt": ("Nachtmarkt", nachtmarkt),
    "reisspeicher": ("Reisspeicher", reisspeicher),
    "reismuehle": ("Reismühle", reismuehle),
}

"""Ruinen & Vergessenes III – zwanzig weitere Ruinen: Leuchtturmruine, Zwergentor, Elfenruine, Kuppelruine,
Glockenturmruine, Stadtmauerrest, Thermenruine, Felsentempel, verbrannte Drachenburg, eingesunkenes Haus,
Kristallruine, Sandstadt, Eisruine, Treppe ins Nichts, Zisterne, Riesenschwert, Labyrinthruine, Schreinruine,
Hafenruine und Magierturmruine. Boden y = 0."""

from __future__ import annotations

import math

import pracht as P
import wald2
from flora import _lv, _neu, _r, _stil, linie
from gewaesser import Land
from lib import Rauschen, einfuegen
from pracht import Mat, gelaende
from ruinen2 import baeume, schwebend_entfernen, stein, stil_haus, verfallen
from veredeln import bewuchs

U = [0.6, 1.0, 1.7, 2.8]


def ring(w, cx, cz, r, y0, y1, M, dicke=1, luecke=None):
    """Runde Mauer (Hohlzylinder)."""
    for x in range(int(cx - r) - 2, int(cx + r) + 3):
        for z in range(int(cz - r) - 2, int(cz + r) + 3):
            d = math.hypot(x - cx, z - cz)
            if r - dicke < d <= r + 0.4:
                if luecke and luecke(x, z):
                    continue
                for y in range(y0, y1):
                    w.setze(x, y, z, M(x, y, z, (y - y0) / max(1, y1 - y0)))


def kasten(w, x0, z0, x1, z1, y0, y1, M, voll=False):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if voll or x in (x0, x1) or z in (z0, z1):
                for y in range(y0, y1):
                    w.setze(x, y, z, M(x, y, z, (y - y0) / max(1, y1 - y0)))


def leuchtturmruine(seed, g=2):
    """Leuchtturmruine: auf einer Felszunge am Meer steht der zerbrochene Schaft eines rot-weißen Leuchtturms, die
    Laterne liegt zerschellt auf den Klippen, Möwennester und Treibholz."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    L = Land(w, R)
    L.heben(lambda x, z, h: max(-3, min(4, round(4 - math.hypot(x + R * 0.2, z) / R * 9))))
    for (x, z), h in L.h.items():
        if h < 0:
            L.wasser[(x, z)] = 0
    L.bauen(gras="grass_block", unten=-4)
    L.bepflanzen(dichte=0.3)
    L.steine(int(5 * u), 1.4, im_wasser=True)
    cx = -round(R * 0.2)
    hb = L.h.get((cx, 0), 3)
    r = _r(2.5 * u + 1.5)
    H = _r(16 * u + 6)
    rn = Rauschen(w, 2)
    for y in range(-1, hb + H):
        for k in range(int(r * 8)):
            a = k / (r * 8) * 6.283
            x, z = cx + round(math.cos(a) * r), round(math.sin(a) * r)
            bruch = y > hb + H * (0.55 + 0.4 * rn(x, 0, z))
            if not bruch:
                w.setze(x, y, z, w.b("red_terracotta" if ((y - hb) // 4) % 2 else "white_terracotta"))
    for k in range(int(10 * u)):
        a = w.rng.random() * 6.283
        d = r + 2 + w.rng.random() * 5 * u
        x, z = cx + round(math.cos(a) * d), round(math.sin(a) * d)
        y = L.h.get((x, z), 0) + 1
        w.setze(x, y, z, w.b(["glass", "iron_bars", "white_terracotta", "red_terracotta", "yellow_stained_glass"]
                             [k % 5], **({"north": False, "south": False, "east": False, "west": False,
                                          "waterlogged": False} if k % 5 == 1 else {})), False)
    verfallen(w, 0.15, ab_y=hb + 3, moos=0.03, ranken=0.0, schutt=False)
    return w


def zwergentor(seed, g=2):
    """Zwergentor: in eine Felswand gehauen ein gewaltiges, halb eingestürztes Tor mit kantigen Säulen, Runenband
    und zerbrochenen Steinwächtern, Geröll versperrt den halben Eingang."""
    from drachen import felsen
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.3)
    felsen(w, R * 0.75, 14 * u + 6, cz=-round(R * 0.45), spitz=0.8, rauh=0.25)
    M = Mat(w, ["polished_deepslate", "deepslate_bricks", "deepslate_tiles", "cracked_deepslate_bricks"])
    B = _r(2.5 * u + 2)
    H = _r(7 * u + 4)
    zf = -round(R * 0.05)
    for z in range(zf - round(R * 0.5), zf + 1):
        for x in range(-B, B + 1):
            for y in range(1, H + 1):
                w.bloecke.pop((x, y, z), None)
    for x in range(-B - 5, B + 6):
        for z in range(zf + 2, R + 1):
            for y in range(1, 40):
                w.bloecke.pop((x, y, z), None)
    for x in range(-B - 3, B + 4):
        for y in range(1, H + 4):
            if abs(x) <= B and y <= H:
                continue
            w.setze(x, y, zf + 1, M(x, y, 0, y / H))
        if abs(x) <= B:
            w.setze(x, H + 1, zf + 1, w.b("chiseled_deepslate") if x % 2 else w.b("gold_block") if x == 0 else
                    w.b("chiseled_polished_blackstone"))
    for sx in (-1, 1):
        x = sx * (B + 2)
        for y in range(1, H + 3):
            w.setze(x, y, zf + 2, w.b("polished_basalt", axis="y"))
        for y in range(1, 4 + int(u)):
            w.setze(x, y, zf + 3, M(x, y, 0, 0.5))
        w.setze(x, 4 + int(u), zf + 3, w.b("chiseled_deepslate")) if sx < 0 else None
    for k in range(int(25 * u)):
        x = int(w.rng.integers(-B, B + 1))
        z = zf + int(w.rng.integers(-2, 3))
        y = 1
        while (x, y, z) in w.bloecke and y < H:
            y += 1
        if y < H * 0.6:
            w.setze(x, y, z, M(x, y, z, 0.5))
    verfallen(w, 0.1, ab_y=H, moos=0.05, ranken=0.05, schutt=False)
    return w


def elfenruine(seed, g=2):
    """Elfenruine: schlanke weiße Spitzbögen aus Kalzit und Quarz, halb von blühendem Efeu überwuchert, ein
    leerer Springbrunnen und ein Pavillon ohne Dach unter Birken."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.55)
    M = Mat(w, ["calcite", "smooth_quartz", "quartz_bricks", "diorite"])
    n = 5 + g
    H = _r(9 * u + 5)
    for k in range(n):
        a = k / n * 6.283
        r = R * 0.55
        x0, z0 = round(math.cos(a) * r), round(math.sin(a) * r)
        a2 = (k + 1) / n * 6.283
        x1, z1 = round(math.cos(a2) * r), round(math.sin(a2) * r)
        for (x, z) in ((x0, z0),):
            for y in range(1, H + 1):
                w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
        steps = max(abs(x1 - x0), abs(z1 - z0))
        for i in range(steps + 1):
            t = i / max(1, steps)
            x, z = round(x0 + (x1 - x0) * t), round(z0 + (z1 - z0) * t)
            y = round(H + 2.5 * math.sin(t * math.pi) ** 0.6)
            w.setze(x, y, z, M(x, y, z, 0.8))
    for x in range(-3, 4):
        for z in range(-3, 4):
            d = math.hypot(x, z)
            if d <= 3.3:
                w.setze(x, 1, z, M(x, 1, z, 0.3) if d > 2.3 else w.b("moss_block"))
    for y in range(2, 5):
        w.setze(0, y, 0, w.b("quartz_pillar", axis="y"))
    w.setze(0, 5, 0, w.b("flowering_azalea"))
    verfallen(w, 0.12, ab_y=H + 1, moos=0.05, ranken=0.3, schutt=True)
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) == "minecraft:vine" and w.rng.random() < 0.2:
            w.bloecke[(x, y, z)] = _lv(w, "flowering_azalea")
    baeume(w, 3 + g, R * 0.85, arten=("birke", "birke", "oak"))
    return w


def kuppelruine(seed, g=2):
    """Kuppelruine: ein runder Kuppelbau, dessen Kuppel zur Hälfte eingestürzt ist – die verbleibende Schale
    wölbt sich wie eine Muschel über den bewachsenen Innenraum, Trümmerberg in der Mitte."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.4)
    M = stein(w, seed)
    r = _r(7 * u + 3)
    H = _r(5 * u + 3)
    ring(w, 0, 0, r, 1, H + 1, M, dicke=1.2, luecke=lambda x, z: abs(x) <= 1 and z > 0)
    rn = Rauschen(w, 3)
    for x in range(-r - 1, r + 2):
        for z in range(-r - 1, r + 2):
            for y in range(0, r + 1):
                d = math.sqrt(x * x + y * y + z * z)
                if r - 1.2 < d <= r and (x + z * 0.4) < r * (0.1 + 0.5 * rn(x, y, z)) - r * 0.1:
                    w.setze(x, H + y, z, M(x, y, z, 0.8) if (y + x) % 5 else w.b("weathered_copper"))
    for k in range(int(40 * u)):
        a = w.rng.random() * 6.283
        d = w.rng.random() * r * 0.6 + r * 0.1
        x, z = round(math.cos(a) * d + r * 0.35), round(math.sin(a) * d)
        y = 1
        while (x, y, z) in w.bloecke and y < 5:
            y += 1
        w.setze(x, y, z, M(x, y, z, 0.5))
    schwebend_entfernen(w)
    bewuchs(w, moos=0.12, ranken=0.15)
    baeume(w, 1 + g // 2, r * 0.4)
    return w


def glockenturmruine(seed, g=1):
    """Glockenturmruine: ein schlanker, viereckiger Glockenturm ohne Spitze, die Glocke ist herabgestürzt und
    liegt gesprungen im Gras, Krähen auf dem Mauerkranz."""
    w = _neu(seed)
    u = U[g]
    R = _r(9 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.45)
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="spruce")
    H = _r(14 * u + 7)
    P.turm(w, st, 0, 0, 1, H, _r(2 * u + 1.5), form="eckig", dach="platt", krone=False, fenster=4)
    a = _r(2 * u + 1.5)
    for sx in (-1, 1):
        for y in range(H - 4, H):
            for z in range(-1, 2):
                w.bloecke.pop((sx * a, y, z), None)
    verfallen(w, 0.3, ab_y=H - 6)
    gx, gz = a + 3, 2
    for y in range(1, 3):
        for x in range(-1, 2):
            for z in range(-1, 2):
                if y == 2 and (abs(x) + abs(z)) == 2:
                    continue
                w.setze(gx + x, y, gz + z, w.b("raw_copper_block" if y == 1 else "copper_block"))
    w.setze(gx, 3, gz, w.b("bell", attachment="floor", facing="north", powered=False))
    return w


def stadtmauerrest(seed, g=2):
    """Stadtmauerrest: ein langes, unterbrochenes Stück Stadtmauer mit Wehrgang, einem Torbogen ohne Tor und dem
    Stumpf eines Rundturms, außen ein verlandeter Graben."""
    w = _neu(seed)
    u = U[g]
    L = _r(20 * u + 8)
    gelaende(w, L + 3, art="wiese", dichte=0.4)
    M = stein(w, seed)
    H = _r(6 * u + 4)
    for x in range(-L, L + 1):
        for z in (0, 1, 2):
            for y in range(1, H + 1):
                if abs(x) <= 2 and y <= H - 2 and (abs(x) < 2 or y < H - 3):
                    continue
                w.setze(x, y, z, M(x, y, z, y / H))
        if x % 2 == 0:
            w.setze(x, H + 1, 0, M(x, H + 1, 0, 0.9))
        for z in range(-5, -1):
            if (x, 1, z) in w.bloecke:
                w.bloecke.pop((x, 1, z), None)
            w.setze(x, 0, z, w.b("mud" if z in (-3, -4) else "coarse_dirt"))
            if z in (-3, -4) and w.rng.random() < 0.3:
                w.setze(x, 1, z, w.b("sugar_cane", age=0))
    r = _r(3 * u + 2)
    ring(w, L * 0.6, 4, r, 1, H + 3, M, dicke=1.3)
    for x in range(-L // 5, -L // 5 + _r(4 * u + 2)):
        for y in range(1, H + 2):
            for z in (0, 1, 2):
                w.bloecke.pop((x, y, z), None)
    verfallen(w, 0.3, ab_y=3)
    return w


def thermenruine(seed, g=2):
    """Thermenruine: römische Badebecken mit Stufen, eines noch mit grünem Wasser gefüllt, Mosaikboden aus
    Terrakotta, Säulenstümpfe und eine halbe Apsis mit Nischen."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.35)
    M = Mat(w, ["smooth_sandstone", "cut_sandstone", "sandstone", "bricks"])
    a, b = _r(9 * u + 4), _r(6 * u + 3)
    mosaik = ["white_terracotta", "light_blue_terracotta", "terracotta", "white_terracotta", "cyan_terracotta"]
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.bloecke.pop((x, 1, z), None)
            w.setze(x, 0, z, w.b(mosaik[(abs(x) // 2 + abs(z) // 2) % len(mosaik)] if (x + z) % 3 else
                                 "smooth_sandstone"))
    for (bx, bz, br, wasser) in ((-a // 2, 0, _r(3 * u + 1), True), (a // 2, 0, _r(2.5 * u + 1), False)):
        for x in range(bx - br - 1, bx + br + 2):
            for z in range(-br - 1, br + 2):
                if abs(x - bx) <= br and abs(z) <= br:
                    for y in (0, -1):
                        w.bloecke.pop((x, y, z), None)
                    w.setze(x, -2, z, w.b("prismarine_bricks" if wasser else "cut_sandstone"))
                    if wasser:
                        for y in (-1, 0):
                            w.setze(x, y, z, w.b("water", level=0))
                    elif w.rng.random() < 0.3:
                        w.setze(x, -1, z, w.b("moss_carpet"))
                else:
                    w.setze(x, 0, z, w.b("smooth_sandstone_slab", type="bottom", waterlogged=False))
    for x in range(-a, a + 1, 3):
        for z in (-b, b):
            for y in range(1, 1 + int(w.rng.integers(1, int(6 * u) + 2))):
                w.setze(x, y, z, w.b("quartz_pillar", axis="y") if _stil(seed) else M(x, y, z, 0.5))
    ra = b
    for k in range(int(ra * 5)):
        t = k / (ra * 5) * math.pi
        x, z = a + round(math.sin(t) * ra * 0.6), round(math.cos(t) * ra)
        for y in range(1, _r(8 * u + 3)):
            nische = y in (2, 3) and k % 6 == 3
            if not nische:
                w.setze(x, y, z, M(x, y, z, y / 8))
    verfallen(w, 0.3, ab_y=3, moos=0.06, ranken=0.08)
    return w


def felsentempel(seed, g=2):
    """Felsentempel: eine prächtige Fassade mit Säulen, Giebel und Urnen ist direkt in eine rote Sandsteinwand
    gemeißelt, Teile sind abgebröckelt, dahinter ein dunkler Saal."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="sand", dichte=0.2)
    F = Mat(w, ["red_sandstone", "smooth_red_sandstone", "terracotta", "orange_terracotta", "red_sandstone"])
    Wd = _r(8 * u + 4)
    H = _r(14 * u + 7)
    zf = -2
    for x in range(-Wd - 6, Wd + 7):
        for z in range(zf - _r(8 * u + 4), zf + 1):
            top = H + 4 - int(abs(x) * 0.3)
            for y in range(1, top):
                w.setze(x, y, z, F(x, y, z, y / H))
    for x in range(-Wd + 2, Wd - 1):
        for z in range(zf - _r(6 * u + 3), zf + 1):
            for y in range(1, int(H * 0.45)):
                w.bloecke.pop((x, y, z), None)
    for x in range(-Wd, Wd + 1):
        for y in range(1, H):
            w.bloecke.pop((x, y, zf + 1), None)
            w.bloecke.pop((x, y, zf + 2), None)
        if x % 3 == 0:
            for y in range(1, int(H * 0.5)):
                w.setze(x, y, zf + 1, w.b("cut_red_sandstone"))
            w.setze(x, int(H * 0.5), zf + 1, w.b("chiseled_red_sandstone"))
        w.setze(x, int(H * 0.5) + 1, zf + 1, w.b("smooth_red_sandstone"))
        dach = int(H * 0.5) + 2 + max(0, Wd // 2 - abs(x) // 2)
        for y in range(int(H * 0.5) + 2, dach + 1):
            w.setze(x, y, zf + 1, w.b("cut_red_sandstone") if y < dach else w.b("smooth_red_sandstone"))
    w.setze(0, int(H * 0.5) + 3 + Wd // 2, zf + 1, w.b("decorated_pot", facing="south", waterlogged=False,
                                                      cracked=False))
    for x in range(-2, 3):
        for y in range(1, 5):
            w.bloecke.pop((x, y, zf + 1), None)
    verfallen(w, 0.12, ab_y=int(H * 0.5), moos=0.0, ranken=0.0, schutt=True)
    return w


def drachenburgruine(seed, g=2):
    """Verbrannte Drachenburg: eine von Drachenfeuer geschwärzte Burgruine – rußige Mauern aus Schwarzstein,
    geschmolzene Zinnen, glühende Asche und riesige Krallenspuren im Mauerwerk."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="asche", dichte=0.25)
    M = Mat(w, ["blackstone", "polished_blackstone_bricks", "cracked_polished_blackstone_bricks", "basalt",
                "stone_bricks", "cobblestone"])
    st = P.Stil(w, wand="schwarzstein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="dark_oak")
    a = _r(9 * u + 4)
    H = _r(6 * u + 4)
    kasten(w, -a, -a, a, a, 1, H, M)
    for (x, z) in ((-a, -a), (a, -a), (-a, a), (a, a)):
        P.turm(w, st, x, z, 1, H + _r(5 * u + 3), _r(2 * u + 1.5), dach="platt", krone=True, fenster=4)
    P.turm(w, st, 0, 0, 1, H + _r(10 * u + 4), _r(3 * u + 2), form="eckig", dach="platt", krone=True, fenster=5)
    verfallen(w, 0.5, ab_y=3, moos=0.0, ranken=0.0, schutt=True)
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if y > 0 and ("stone" in n or "brick" in n) and w.rng.random() < 0.3:
            w.bloecke[(x, y, z)] = w.b("blackstone" if w.rng.random() < 0.7 else "coal_block")
    for k in range(3):
        x = -a + 3 + k * 2
        for y in range(2, H - 1):
            w.bloecke.pop((x + y // 3, y, -a), None)
    for k in range(int(20 * u)):
        x, z = int(w.rng.integers(-R, R)), int(w.rng.integers(-R, R))
        if w.frei(x, 1, z) and (x, 0, z) in w.bloecke:
            w.setze(x, 0, z, w.b("magma_block"))
            if w.rng.random() < 0.3:
                w.setze(x, 1, z, w.b("fire", age=0, north=False, south=False, east=False, west=False, up=False))
    return w


def eingesunkenes_haus(seed, g=1):
    """Eingesunkenes Haus: ein Fachwerkhaus ist schief in den Sumpf gesackt, das Wasser steht bis zu den Fenstern,
    das Dach hängt durch, Schilf und Seerosen ringsum."""
    from skulptur import dreh_x, dreh_z
    from piraten import einfuegen_gedreht
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 6)
    L = Land(w, R)
    L.see(0, 0, R * 0.8, 0, tiefe=3)
    L.bauen(gras="grass_block", unten=-5)
    L.bepflanzen(dichte=0.4)
    for (x, z) in L.wasser:
        if w.rng.random() < 0.06:
            w.setze(x, 1, z, w.b("lily_pad"))
    h = _neu(seed)
    st = stil_haus(h, "fachwerk_rot")
    a = _r(3 * u + 2)
    P.gebaeude(h, st, -a, -a + 1, a, a - 1, y0=0, etagen=1 + (g > 1), eh=4, dach="sattel", tuer="south", sockel_h=0,
               gauben=False, kamine=1)
    einfuegen_gedreht(w, h, dreh_z(0.18) @ dreh_x(-0.12), (0, -2.2, 0))
    verfallen(w, 0.12, ab_y=4, moos=0.08, ranken=0.15, schutt=False)
    return w


def kristallruine(seed, g=2):
    """Kristallruine: die Reste eines Tempels sind von riesigen Amethyst- und Glaskristallen durchbrochen, die aus
    dem Boden wachsen und Säulen zur Seite gedrückt haben."""
    from kristall import kristall
    w = _neu(seed)
    u = U[g]
    R = _r(13 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.3)
    M = Mat(w, ["calcite", "smooth_quartz", "polished_diorite", "quartz_bricks"])
    a = _r(7 * u + 3)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            w.setze(x, 1, z, M(x, 1, z, 0.3))
    H = _r(7 * u + 4)
    for x in range(-a, a + 1, 3):
        for z in (-a, a):
            for y in range(2, 2 + int(H * (0.4 + 0.6 * w.rng.random()))):
                w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    rng = w.rng
    for k in range(3 + g):
        x, z = int(rng.integers(-a, a + 1)), int(rng.integers(-a, a + 1))
        kristall(w, (x, 1, z), ((rng.random() - 0.5) * 0.8, 1, (rng.random() - 0.5) * 0.8),
                 (5 + rng.random() * 6) * u, (0.8 + rng.random() * 0.8) * u, art="amethyst")
    verfallen(w, 0.2, ab_y=4, moos=0.04, ranken=0.05, schutt=True)
    return w


def sandstadt(seed, g=2):
    """Versandete Stadt: Kuppeln, Bögen und Mauerkronen einer Wüstenstadt ragen aus hohen Dünen, ein Minarett
    steht noch fast ganz, Palmenstümpfe und Tonkrüge im Sand."""
    from wueste_eis import kuppel
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    L = Land(w, R)
    rn = Rauschen(w, 8)
    L.heben(lambda x, z, h: round(3 * u * rn(x, 0, z)))
    L.bauen(gras="sand", unten=-2)
    M = Mat(w, ["sandstone", "cut_sandstone", "smooth_sandstone", "chiseled_sandstone", "terracotta"])
    rng = w.rng
    for i in range(5 + 2 * g):
        a = i * 2.39996
        d = R * 0.65 * math.sqrt((i + 0.5) / (5 + 2 * g))
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        b = _r(2.5 * u + 2)
        kasten(w, cx - b, cz - b, cx + b, cz + b, -2, _r(4 * u + 2), M)
        if i % 2 == 0:
            kuppel(w, w.b("smooth_sandstone" if i % 4 else "light_blue_terracotta"), cx, cz, _r(4 * u + 2), b + 0.5)
    st = P.Stil(w, wand="sandstein", sockel="sandstein", gesims="stone_brick", dach="sand", holz="spruce")
    P.turm(w, st, round(R * 0.3), -round(R * 0.3), 1, _r(16 * u + 6), _r(1.5 * u + 1), dach="kegel", krone=False,
           fenster=4)
    verfallen(w, 0.25, ab_y=3, moos=0.0, ranken=0.0, schutt=False)
    for (x, z), h in L.h.items():
        for y in range(1, h + 1):
            if (x, y, z) not in w.bloecke:
                w.setze(x, y, z, w.b("sand" if y < h else "sand"))
    for k in range(int(6 * u)):
        x, z = int(rng.integers(-R // 2, R // 2)), int(rng.integers(-R // 2, R // 2))
        y = L.h.get((x, z), 0) + 1
        w.setze(x, y, z, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False), False)
    return w


def eisruine(seed, g=2):
    """Eisruine: eine Festung, die im Gletscher erstarrt ist – Mauern und Türme stecken halb in Packeis, Eiszapfen
    hängen von den Zinnen, Schneewehen im Hof."""
    w = _neu(seed)
    u = U[g]
    R = _r(15 * u + 6)
    gelaende(w, R, art="schnee", dichte=0.1)
    M = Mat(w, ["stone_bricks", "cracked_stone_bricks", "cobblestone", "andesite"])
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="spruce")
    a = _r(8 * u + 4)
    H = _r(6 * u + 4)
    kasten(w, -a, -a, a, a, 1, H, M)
    for (x, z) in ((-a, -a), (a, -a), (-a, a), (a, a)):
        P.turm(w, st, x, z, 1, H + _r(5 * u + 3), _r(2 * u + 1.5), dach="kegel", krone=False, fenster=4)
    verfallen(w, 0.35, ab_y=3, moos=0.0, ranken=0.0, schutt=True)
    rn = Rauschen(w, 4)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            hgl = int((rn(x, 0, z) - 0.35) * 14 * u) - int(math.hypot(x - R * 0.5, z) * 0.25)
            for y in range(1, max(1, hgl)):
                if (x, y, z) not in w.bloecke:
                    w.setze(x, y, z, w.b("packed_ice" if y < hgl - 1 else "snow_block"))
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 3 and w.frei(x, y - 1, z) and w.rng.random() < 0.05 and "ice" not in w.P.name(b):
            for k in range(1, 3):
                if w.frei(x, y - k, z):
                    w.setze(x, y - k, z, w.b("ice"))
    return w


def treppe_ins_nichts(seed, g=2):
    """Treppe ins Nichts: eine monumentale, breite Freitreppe mit Löwenpostamenten führt hinauf zu einem Podest mit
    zwei Säulen – dahinter ist nichts mehr, nur Himmel."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.4)
    M = Mat(w, ["smooth_quartz", "calcite", "quartz_bricks"]) if _stil(seed) else stein(w, seed)
    B = _r(4 * u + 2)
    n = _r(9 * u + 4)
    for k in range(n):
        for x in range(-B, B + 1):
            for y in range(1, k + 1):
                w.setze(x, y, k - n // 2, M(x, y, k, y / n))
            w.setze(x, k + 1, k - n // 2, w.b("quartz_stairs" if _stil(seed) else "stone_brick_stairs",
                                               facing="south", half="bottom", shape="straight", waterlogged=False))
    zt = n - n // 2
    for x in range(-B - 1, B + 2):
        for z in range(zt, zt + 4):
            for y in range(1, n + 1):
                w.setze(x, y, z, M(x, y, z, y / n))
    for sx in (-B - 1, B + 1):
        for y in range(n + 1, n + 1 + _r(7 * u + 3)):
            w.setze(sx, y, zt + 2, w.b("quartz_pillar", axis="y"))
        for k in range(0, n, max(2, n // 3)):
            w.setze(sx, k + 2, k - n // 2, w.b("chiseled_quartz_block" if _stil(seed) else "chiseled_stone_bricks"))
    verfallen(w, 0.08, ab_y=n, moos=0.05, ranken=0.1, schutt=False)
    return w


def zisterne(seed, g=2):
    """Freigelegte Zisterne: das Gewölbe einer unterirdischen Zisterne ist eingebrochen – Reihen von Säulen mit
    Rundbögen stehen im dunklen Wasser, Moos und Tropfstein, ein Treppenabgang."""
    from arena import anheben
    w = _neu(seed)
    u = U[g]
    a = _r(8 * u + 4)
    H = _r(5 * u + 4)
    M = Mat(w, ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "bricks"])
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            rand = abs(x) == a + 1 or abs(z) == a + 1
            for y in range(-H, 1):
                if rand:
                    w.setze(x, y, z, M(x, y, z, 0.5))
            if not rand:
                w.setze(x, -H - 1, z, w.b("mud"))
                for y in range(-H, -H + 2):
                    w.setze(x, y, z, w.b("water", level=0))
    for x in range(-a + 1, a, 3):
        for z in range(-a + 1, a, 3):
            for y in range(-H, 0):
                w.setze(x, y, z, w.b("quartz_pillar", axis="y") if y < -1 else w.b("chiseled_stone_bricks"))
            for d in (1, 2):
                if x + d < a:
                    w.setze(x + d, 0, z, M(x, 0, z, 0.7))
                if z + d < a:
                    w.setze(x, 0, z + d, M(x, 0, z, 0.7))
            w.setze(x, 0, z, M(x, 0, z, 0.7))
    rn = Rauschen(w, 3)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if rn(x, 0, z) < 0.55:
                w.bloecke.pop((x, 0, z), None)
    for k in range(H):
        for x in range(-1, 2):
            w.setze(x, -k, -a - 2 - k, w.b("stone_brick_stairs", facing="south", half="bottom", shape="straight",
                                         waterlogged=False))
    anheben(w, H + 1)
    gelaende(w, a + 6, art="wiese", dichte=0.3)
    bewuchs(w, moos=0.12, ranken=0.2)
    return w


def riesenschwert(seed, g=2):
    """Riesenschwert: in den Trümmern eines Rundtempels steckt schräg ein gewaltiges Steinschwert mit goldenem
    Griff und Edelstein im Knauf – Risse laufen strahlenförmig durch den Boden."""
    w = _neu(seed)
    u = U[g]
    R = _r(13 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.35)
    M = stein(w, seed)
    r = _r(6 * u + 3)
    for x in range(-r, r + 1):
        for z in range(-r, r + 1):
            if math.hypot(x, z) <= r:
                w.setze(x, 0, z, M(x, 0, z, 0.3))
    for k in range(10):
        a = k / 10 * 6.283
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        for y in range(1, 1 + int(w.rng.integers(1, int(5 * u) + 3))):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y") if _stil(seed) else M(x, y, z, 0.5))
    for k in range(8):
        a = k / 8 * 6.283 + 0.2
        for d in range(1, r):
            if w.rng.random() < 0.7:
                w.setze(round(math.cos(a) * d), 0, round(math.sin(a) * d), w.b("cracked_stone_bricks"))
    L = _r(14 * u + 6)
    neig = 0.25
    for i in range(-3, L):
        y = i
        x = round(i * neig)
        br = 2 if i < L - 3 else 1
        for dz in range(-br, br + 1):
            w.setze(x, y, dz, w.b("iron_block" if abs(dz) < br else "light_gray_concrete"))
        w.setze(x - 1, y, 0, w.b("iron_block"))
    yg = L
    xg = round(L * neig)
    for dz in range(-4, 5):
        w.setze(xg, yg, dz, w.b("gold_block"))
    for k in range(1, 5):
        w.setze(xg + round(k * neig), yg + k, 0, w.b("dark_oak_log", axis="y"))
    w.setze(xg + round(5 * neig), yg + 5, 0, w.b("emerald_block"))
    return w


def labyrinthruine(seed, g=2):
    """Labyrinthruine: ein steinernes Labyrinth mit eingestürzten Gängen, Moos und Efeu, in der Mitte ein Podest
    mit einem verwitterten Wächterstein."""
    w = _neu(seed)
    u = U[g]
    n = 4 + g * 2
    zelle = 3
    R = n * zelle // 2 + 3
    gelaende(w, R + 2, art="wiese", dichte=0.25)
    M = stein(w, seed)
    rng = w.rng
    besucht = {(0, 0)}
    stapel = [(0, 0)]
    offen = set()
    while stapel:
        c = stapel[-1]
        nb = [(c[0] + dx, c[1] + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= c[0] + dx < n and 0 <= c[1] + dz < n and (c[0] + dx, c[1] + dz) not in besucht]
        if not nb:
            stapel.pop()
            continue
        q = nb[int(rng.integers(len(nb)))]
        offen.add((c, q))
        offen.add((q, c))
        besucht.add(q)
        stapel.append(q)
    H = 3 + (g > 1)
    o = -n * zelle // 2
    for i in range(n * zelle + 1):
        for j in range(n * zelle + 1):
            ci, cj = i // zelle, j // zelle
            wand = i % zelle == 0 or j % zelle == 0
            if not wand:
                continue
            if i % zelle == 0 and j % zelle != 0:
                a, b = (ci - 1, cj), (ci, cj)
                if (a, b) in offen:
                    continue
            if j % zelle == 0 and i % zelle != 0:
                a, b = (ci, cj - 1), (ci, cj)
                if (a, b) in offen:
                    continue
            if (i in (0, n * zelle) and j in (1, 2)) or (i == n * zelle // 2 and j == n * zelle // 2):
                continue
            for y in range(1, H + 1):
                w.setze(o + i, y, o + j, M(i, y, j, y / H))
    w.setze(0, 1, 0, w.b("chiseled_stone_bricks"))
    w.setze(0, 2, 0, w.b("carved_pumpkin", facing="south")) if False else w.setze(0, 2, 0, w.b("lodestone"))
    verfallen(w, 0.4, ab_y=2, moos=0.12, ranken=0.2, schutt=True)
    return w


def schreinruine(seed, g=0):
    """Schreinruine: ein kleiner Waldschrein aus Stein unter einer alten Eiche, mit Opferschale, Kerzenresten,
    verblichenem Banner und einem moosbedeckten Torbogen davor."""
    w = _neu(seed)
    u = U[g]
    R = _r(7 * u + 5)
    gelaende(w, R, art="wald", dichte=0.4)
    M = stein(w, seed)
    for x in range(-2, 3):
        for z in range(-2, 2):
            w.setze(x, 1, z, M(x, 1, z, 0.3))
    for x in (-2, 2):
        for z in (-2, 1):
            for y in range(2, 5):
                w.setze(x, y, z, M(x, y, z, y / 5))
    for x in range(-3, 4):
        for z in range(-3, 3):
            w.setze(x, 5, z, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    w.setze(0, 2, -1, w.b("cauldron"))
    for (x, z) in ((-1, -1), (1, -1), (1, 0)):
        w.setze(x, 2, z, w.b("candle", candles=1 + (x + z) % 3, lit=False, waterlogged=False))
    for sx in (-2, 2):
        for y in range(1, 5):
            w.setze(sx, y, 5, M(sx, y, 5, y / 5))
    for x in range(-2, 3):
        w.setze(x, 5, 5, M(x, 5, 5, 0.9))
    einfuegen(w, wald2.laubbaum(seed, "oak", H=_r(9 * u + 5)), -5, 0, -4)
    verfallen(w, 0.15, ab_y=3, moos=0.2, ranken=0.2, schutt=False)
    return w


def hafenruine(seed, g=2):
    """Hafenruine: ein verfallener Steinkai mit Pollern, ein morscher Holzsteg auf schiefen Pfählen, das Wrack eines
    Ruderboots im flachen Wasser und ein dachloses Lagerhaus."""
    w = _neu(seed)
    u = U[g]
    R = _r(15 * u + 6)
    L = Land(w, R)
    L.heben(lambda x, z, h: 2 if x < -2 else -3)
    for (x, z), h in L.h.items():
        if h < 0:
            L.wasser[(x, z)] = 0
    L.bauen(gras="grass_block", unten=-4)
    L.bepflanzen(dichte=0.3)
    M = stein(w, seed)
    for z in range(-R, R + 1):
        for x in (-2, -1):
            if (x, z) in L.h:
                for y in range(-3, 3):
                    w.setze(x, y, z, M(x, y, z, 0.5))
        if z % 6 == 0 and (-2, z) in L.h:
            w.setze(-2, 3, z, w.b("polished_andesite"))
    lz = _r(10 * u + 4)
    for x in range(0, lz):
        for z in (-1, 0, 1):
            if w.rng.random() < 0.8:
                w.setze(x, 1, z, w.b("spruce_planks" if w.rng.random() < 0.8 else "spruce_slab", **(
                    {} if w.rng.random() < 0.8 else {})))
        if x % 3 == 0:
            for z in (-1, 1):
                for y in range(-3, 1):
                    w.setze(x + (1 if y < -1 and z > 0 else 0), y, z, w.b("spruce_log", axis="y"))
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) == "minecraft:spruce_slab":
            w.bloecke[(x, y, z)] = w.b("spruce_slab", type="bottom", waterlogged=False)
    from boote import ruderboot
    try:
        b = ruderboot(seed, 0)
        from piraten import einfuegen_gedreht
        from skulptur import dreh_y, dreh_z
        einfuegen_gedreht(w, b, dreh_y(0.8) @ dreh_z(0.3), (lz // 2, -1.5, 5))
    except Exception:
        pass
    st = stil_haus(w, "backstein")
    P.gebaeude(w, st, -R + 3, -5, -6, 5, y0=3, etagen=1, eh=4, dach="sattel", tuer="east", sockel_h=0,
               gauben=False, kamine=0)
    verfallen(w, 0.4, ab_y=5, moos=0.05, ranken=0.08, schutt=True)
    return w


def magierturmruine(seed, g=2):
    """Magierturmruine: ein verdrehter, geborstener Turm aus dunklem Stein, über dem abgebrochenen Oberteil
    schweben noch einzelne Mauerbrocken, von violettem Licht gehalten; Bücher und Kristalle im Schutt."""
    w = _neu(seed)
    u = U[g]
    R = _r(11 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.3)
    M = Mat(w, ["deepslate_bricks", "polished_blackstone_bricks", "deepslate_tiles", "cracked_deepslate_bricks",
                "purpur_block"])
    r = _r(3 * u + 2)
    H = _r(10 * u + 5)
    rn = Rauschen(w, 2)
    for y in range(1, H + 1):
        dreh = y * 0.08
        for k in range(int(r * 8)):
            a = k / (r * 8) * 6.283 + dreh
            x, z = round(math.cos(a) * r), round(math.sin(a) * r)
            if y > H * (0.6 + 0.4 * rn(x, 0, z)):
                continue
            w.setze(x, y, z, M(x, y, z, y / H))
    rng = w.rng
    for k in range(int(10 * u)):
        a = rng.random() * 6.283
        x, z = round(math.cos(a) * r * 1.1), round(math.sin(a) * r * 1.1)
        y = H + 2 + int(rng.random() * 6 * u)
        for dx in range(2):
            for dy in range(2):
                w.setze(x + dx, y + dy, z, M(x, y, z, 0.6))
        w.setze(x, y - 1, z, w.b("purple_stained_glass"))
    for k in range(int(8 * u)):
        x, z = int(rng.integers(-R // 2, R // 2)), int(rng.integers(-R // 2, R // 2))
        w.setze(x, 1, z, w.b(["bookshelf", "amethyst_cluster", "crying_obsidian", "lectern"][k % 4], **(
            {"facing": "up", "waterlogged": False} if k % 4 == 1 else
            {"facing": "north", "has_book": True, "powered": False} if k % 4 == 3 else {})), False)
    return w


RUINEN3 = {
    "leuchtturmruine": ("Leuchtturmruine", leuchtturmruine),
    "zwergentor": ("Verfallenes Zwergentor", zwergentor),
    "elfenruine": ("Elfenruine", elfenruine),
    "kuppelruine": ("Kuppelruine", kuppelruine),
    "glockenturmruine": ("Glockenturmruine", glockenturmruine),
    "stadtmauerrest": ("Stadtmauerrest", stadtmauerrest),
    "thermenruine": ("Thermenruine", thermenruine),
    "felsentempel": ("Felsentempel", felsentempel),
    "drachenburgruine": ("Verbrannte Drachenburg", drachenburgruine),
    "eingesunkenes_haus": ("Eingesunkenes Haus", eingesunkenes_haus),
    "kristallruine": ("Kristallruine", kristallruine),
    "sandstadt": ("Versandete Stadt", sandstadt),
    "eisruine": ("Eisruine", eisruine),
    "treppe_ins_nichts": ("Treppe ins Nichts", treppe_ins_nichts),
    "zisterne": ("Freigelegte Zisterne", zisterne),
    "riesenschwert": ("Riesenschwert", riesenschwert),
    "labyrinthruine": ("Labyrinthruine", labyrinthruine),
    "schreinruine": ("Schreinruine", schreinruine),
    "hafenruine": ("Hafenruine", hafenruine),
    "magierturmruine": ("Magierturmruine", magierturmruine),
}

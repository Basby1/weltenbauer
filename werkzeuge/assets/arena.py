"""Arena & Turnierplatz – Tjostbahn, Tribünen, Ritterzelte, Holz- und Steinarenen, Rennbahnen, Kampfgruben,
Trainingshof, Siegerpodest, Königsloge, Hindernisparcours, Seeschlacht-Becken, Riesenschach und Turnierlager.
Boden y = 0."""

from __future__ import annotations

import math

import modbloecke as MB
import pracht as P
from flora import _neu, _r, _stil, linie
from lib import Rauschen
from pracht import Mat, gelaende

U = [0.6, 1.0, 1.7, 2.8]
FARBPAARE = [("red", "yellow"), ("blue", "white"), ("green", "white"), ("purple", "yellow"), ("black", "red"),
             ("orange", "white")]


def zf(w, holz="oak", **v):
    d = dict(north=False, south=False, east=False, west=False, waterlogged=False)
    d.update(v)
    return w.b(f"{holz}_fence", **d)


def sand(w, x0, z0, x1, z1, rund=False):
    rn = Rauschen(w, 1.5)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    rx, rz = (x1 - x0) / 2, (z1 - z0) / 2
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if rund and ((x - cx) / rx) ** 2 + ((z - cz) / rz) ** 2 > 1:
                continue
            w.setze(x, 0, z, w.b(["sand", "sand", "smooth_sandstone", "coarse_dirt", "sand"][int(rn(x, 0, z) * 4.99)]))
            w.bloecke.pop((x, 1, z), None)


def zelt(w, x, z, r, farben=("red", "white"), H=None, wimpel=True):
    """Rundes Turnierzelt mit gestreifter Kegelhaube, Volant und Wimpel."""
    H = H or int(r * 1.6) + 2
    a_, b_ = farben
    wand = int(r * 0.8) + 1
    for y in range(1, H + 1):
        if y <= wand:
            rr = r
        else:
            rr = r * (1 - (y - wand) / (H - wand + 0.5))
        n = int(rr * 7) + 4
        for k in range(n):
            ang = k / n * 6.28
            px, pz = x + round(math.cos(ang) * rr), z + round(math.sin(ang) * rr)
            if y <= 2 and abs(math.sin(ang)) < 0.25 and math.cos(ang) > 0:
                continue
            f = a_ if (k * 8 // n) % 2 else b_
            w.setze(px, y, pz, w.b(f"{f}_wool"))
        if y == wand:
            for k in range(int(r * 7) + 4):
                ang = k / (r * 7 + 4) * 6.28
                if k % 2:
                    w.setze(x + round(math.cos(ang) * (r + 1)), y, z + round(math.sin(ang) * (r + 1)),
                            w.b(f"{a_}_carpet"), False)
    w.setze(x, H + 1, z, zf(w, "spruce"))
    if wimpel:
        w.setze(x, H + 2, z, zf(w, "spruce"))
        w.setze(x - 1, H + 2, z, w.b(f"{a_}_wool"))
        w.setze(x - 2, H + 2, z, w.b(f"{b_}_wool"))


def tribuene(w, x0, x1, z, stufen=4, richtung=1, holz="spruce", dach=True, farben=("red", "yellow")):
    """Holztribüne mit Sitzstufen, Rückwand, Baldachin und Bannern. richtung: +1 = Blick nach +z."""
    for k in range(stufen):
        zz = z - richtung * k
        for x in range(x0, x1 + 1):
            for y in range(1, k + 2):
                w.setze(x, y, zz, w.b(f"{holz}_planks") if y < k + 1 else
                        w.b(f"{holz}_stairs", facing="south" if richtung < 0 else "north", half="bottom",
                            shape="straight", waterlogged=False))
    zr = z - richtung * stufen
    for x in range(x0, x1 + 1):
        for y in range(1, stufen + 4):
            w.setze(x, y, zr, w.b(f"{holz}_planks") if y < stufen + 3 else w.b(f"{holz}_slab", type="bottom",
                                                                               waterlogged=False))
    if dach:
        H = stufen + 4
        for x in range(x0 - 1, x1 + 2):
            for k in range(stufen + 2):
                zz = zr + richtung * k
                w.setze(x, H, zz, w.b(f"{farben[(x // 2) % 2]}_wool"))
        for x in range(x0, x1 + 1, 4):
            for y in range(1, H):
                w.setze(x, y, z + richtung, zf(w, holz))
            w.setze(x, H - 1, z + richtung + richtung, w.b(f"{farben[0]}_banner", rotation=0 if richtung > 0 else 8)
                    if False else w.b(f"{farben[0]}_wool"))


def bannerreihe(w, x0, x1, z, h=5, farben=("red", "yellow")):
    for x in range(x0, x1 + 1, 3):
        for y in range(1, h + 1):
            w.setze(x, y, z, zf(w, "spruce"))
        f = farben[(x // 3) % 2]
        for y in range(h - 2, h + 1):
            w.setze(x + 1, y, z, w.b(f"{f}_wool"))


def waffenstaender(w, x, z):
    for d in range(3):
        w.setze(x + d, 1, z, w.b("spruce_fence", north=False, south=False, east=d < 2, west=d > 0,
                                 waterlogged=False))
        w.setze(x + d, 2, z, w.b("lightning_rod", facing="up", powered=False, waterlogged=False) if d % 2 else
                w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))


def ringwand(w, cx, cz, rx, rz, h, mat, oeffnungen=()):
    n = int((rx + rz) * 6)
    for k in range(n):
        a = k / n * 6.28
        x, z = cx + round(math.cos(a) * rx), cz + round(math.sin(a) * rz)
        if any(abs(math.atan2(math.sin(a - o), math.cos(a - o))) < 0.18 for o in oeffnungen):
            continue
        for y in range(1, h + 1):
            w.setze(x, y, z, mat(x, y, z, y / h) if callable(mat) else w.b(mat))


def ovaltribuene(w, cx, cz, rx, rz, stufen, M, oeffnungen=()):
    """Steinerne Ränge rund um ein Oval."""
    for k in range(stufen):
        for j in range(int((rx + rz + 2 * k) * 6)):
            a = j / ((rx + rz + 2 * k) * 6) * 6.28
            if any(abs(math.atan2(math.sin(a - o), math.cos(a - o))) < 0.2 for o in oeffnungen):
                continue
            x, z = cx + round(math.cos(a) * (rx + k)), cz + round(math.sin(a) * (rz + k))
            for y in range(1, k + 3):
                w.setze(x, y, z, M(x, y, z, y / (stufen + 2)))


# ============================================================================ Turnier

def tjostbahn(seed, g=2):
    """Tjostbahn: eine lange Bahn mit hölzerner Trennplanke, an beiden Enden Rüstzelte der Ritter, an der Längsseite
    eine überdachte Tribüne mit Fahnen und Lanzenständer."""
    w = _neu(seed)
    u = U[g]
    L, B = _r(22 * u + 8), _r(8 * u + 4)
    gelaende(w, L + 6, art="wiese", dichte=0.2)
    sand(w, -L, -B, L, B)
    for x in range(-L + 4, L - 3):
        w.setze(x, 1, 0, w.b("spruce_planks") if x % 4 else w.b("spruce_log", axis="y"))
        w.setze(x, 2, 0, zf(w, "spruce", east=True, west=True))
    fa = FARBPAARE[seed % 6]
    fb = FARBPAARE[(seed + 3) % 6]
    zelt(w, -L - 2, 3, 2.5 * u + 1, fa)
    zelt(w, L + 2, -3, 2.5 * u + 1, fb)
    tribuene(w, -L // 2, L // 2, B + 2, stufen=_r(3 * u + 1), richtung=-1, farben=fa)
    for x in range(-L, L + 1, 2):
        w.setze(x, 1, -B - 1, zf(w, "oak", east=True, west=True))
    waffenstaender(w, -L + 1, -2)
    waffenstaender(w, L - 3, 2)
    return w


def ritterzelte(seed, g=2):
    """Ritterlager: ein Halbkreis bunter Rundzelte mit Wappenwimpeln, dazwischen Rüstungsständer, Feuerstelle,
    Pferdetränke und Fässer."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.25)
    n = 5 + g
    for i in range(n):
        a = math.pi * 0.1 + i / (n - 1) * math.pi * 0.8
        x, z = round(math.cos(a) * R * 0.65), -round(math.sin(a) * R * 0.65)
        zelt(w, x, z, (1.6 + (i % 2) * 0.6) * u + 1, FARBPAARE[(seed + i) % 6])
    w.setze(0, 1, 2, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for k in range(3):
        w.setze(-3 + k * 3, 1, R // 2, w.b("armor_stand") if False else zf(w, "spruce"))
        w.setze(-3 + k * 3, 2, R // 2, w.b("carved_pumpkin", facing="south") if False else w.b("iron_block"))
    for x in range(R // 3, R // 3 + 4):
        w.setze(x, 1, R // 3, w.b("water_cauldron", level=3) if x % 2 else w.b("hay_block", axis="y"))
    return w


def holzarena(seed, g=2):
    """Holzarena: ein runder Kampfplatz mit Palisadenwand, umlaufender Zuschauergalerie auf Stelzen, zwei Toren
    und Fackeln."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R + 6, art="wiese", dichte=0.2)
    sand(w, -R, -R, R, R, rund=True)
    for k in range(int(R * 7)):
        a = k / (R * 7) * 6.28
        if abs(math.sin(a)) < 0.1:
            continue
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        for y in range(1, 4):
            w.setze(x, y, z, w.b("spruce_log", axis="y") if k % 2 else w.b("stripped_spruce_log", axis="y"))
        for dr in (1, 2, 3):
            x2, z2 = round(math.cos(a) * (R + dr)), round(math.sin(a) * (R + dr))
            w.setze(x2, 4, z2, w.b("spruce_planks"))
            if dr == 3:
                w.setze(x2, 5, z2, zf(w, "spruce"))
        if k % 6 == 0:
            x3, z3 = round(math.cos(a) * (R + 3)), round(math.sin(a) * (R + 3))
            for y in range(1, 4):
                w.setze(x3, y, z3, w.b("spruce_log", axis="y"))
            w.setze(x3, 6, z3, w.b("lantern", hanging=False, waterlogged=False))
    return w


def steinarena(seed, g=2):
    """Steinarena: ein ovales Amphitheater aus Bruchstein mit fünf Rängen, Ehrenloge, zwei Toren mit Fallgattern
    und Sandboden mit Fallgruben."""
    w = _neu(seed)
    u = U[g]
    rx, rz = _r(14 * u + 5), _r(10 * u + 4)
    gelaende(w, rx + 10, art="wiese", dichte=0.2)
    sand(w, -rx, -rz, rx, rz, rund=True)
    M = Mat(w, ["stone_bricks", "cobblestone", "mossy_stone_bricks", "andesite", "cracked_stone_bricks"])
    ovaltribuene(w, 0, 0, rx + 1, rz + 1, _r(4 * u + 2), M, oeffnungen=(0, math.pi))
    for sx in (-1, 1):
        x = sx * (rx + 1)
        for z in range(-2, 3):
            for y in range(1, 5):
                w.setze(x, y, z, w.b("iron_bars", north=True, south=True, east=False, west=False,
                                     waterlogged=False) if abs(z) < 2 and y < 4 else M(x, y, z, 0.5))
    for x in range(-3, 4):
        w.setze(x, _r(4 * u + 2) + 2, -(rz + _r(4 * u + 2)), w.b("red_wool"))
    for k in range(3):
        x = -rx // 2 + k * rx // 2
        for dx in (0, 1):
            for dz in (0, 1):
                w.setze(x + dx, 0, 3 + dz, w.b("iron_trapdoor", facing="north", half="top", open=False,
                                               powered=False, waterlogged=False))
    return w


def tribuene_bau(seed, g=1):
    """Turniertribüne: eine große, überdachte Holztribüne mit gestreiftem Baldachin, Königsbank in der Mitte und
    Wappenbannern – passt an jede Kampfbahn."""
    w = _neu(seed)
    u = U[g]
    L = _r(12 * u + 5)
    gelaende(w, L + 3, art="wiese", dichte=0.2)
    fa = FARBPAARE[seed % 6]
    tribuene(w, -L, L, 3, stufen=_r(4 * u + 2), richtung=-1, farben=fa)
    for x in (-1, 0, 1):
        w.setze(x, 3, 1, w.b("gold_block") if x == 0 else w.b(f"{fa[0]}_wool"))
    bannerreihe(w, -L, L, -_r(4 * u + 2) - 4 + 3, h=_r(4 * u + 2) + 6, farben=fa)
    return w


def koenigsloge(seed, g=1):
    """Königsloge: ein erhöhter, steinerner Balkon mit Thronsesseln unter einem Baldachin aus Purpur und Gold,
    Treppe, Wachen-Nischen und Wappenschild."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    gelaende(w, R + 3, art="wiese", dichte=0.2)
    M = Mat(w, ["stone_bricks", "chiseled_stone_bricks", "polished_andesite", "stone_bricks"])
    a, b = _r(4 * u + 2), _r(3 * u + 1)
    H = _r(3 * u + 2)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            for y in range(1, H + 1):
                w.setze(x, y, z, M(x, y, z, y / H))
        w.setze(x, H + 1, b, w.b("stone_brick_wall", up=False, north="none", south="none", east="low", west="low",
                                 waterlogged=False))
    for x in (-1, 1):
        w.setze(x, H + 1, 0, w.b("dark_oak_stairs", facing="north", half="bottom", shape="straight", waterlogged=False))
        w.setze(x, H + 2, -1, w.b("gold_block"))
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.setze(x, H + 5, z, w.b("purple_wool" if (x + z) % 2 else "yellow_wool"))
    for sx in (-a, a):
        for sz in (-b, b):
            for y in range(H + 1, H + 5):
                w.setze(sx, y, sz, w.b("dark_oak_fence", north=False, south=False, east=False, west=False,
                                       waterlogged=False))
    for k in range(H):
        for x in (a + 1, a + 2):
            w.setze(x, k + 1, -b + k, w.b("stone_brick_stairs", facing="south", half="bottom", shape="straight",
                                          waterlogged=False))
    return w


def schwertkampfring(seed, g=1):
    """Schwertkampfring: ein mit Seilen begrenzter Sandring zwischen vier Pfosten, Waffenständer, Holzpuppen zum
    Üben, Wassereimer und eine Bank für die Sekundanten."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    gelaende(w, R + 4, art="wiese", dichte=0.25)
    sand(w, -R, -R, R, R)
    for sx in (-R, R):
        for sz in (-R, R):
            for y in range(1, 4):
                w.setze(sx, y, sz, w.b("spruce_log", axis="y"))
    for k in range(-R + 1, R):
        for (x, z) in ((k, -R), (k, R), (-R, k), (R, k)):
            w.setze(x, 2, z, MB.seil(w, "x" if abs(z) == R else "z"))
    waffenstaender(w, R + 2, -2)
    for k in range(2):
        x, z = -R - 2, -2 + k * 4
        w.setze(x, 1, z, zf(w, "oak"))
        w.setze(x, 2, z, w.b("hay_block", axis="y"))
        w.setze(x, 3, z, w.b("carved_pumpkin", facing="east"))
    return w


def pferderennbahn(seed, g=2):
    """Pferderennbahn: eine ovale Sandbahn mit weißem Innenzaun, Startboxen, Zielrichterturm und Zuschauerwall
    mit Fahnen."""
    w = _neu(seed)
    u = U[g]
    rx, rz = _r(20 * u + 6), _r(11 * u + 4)
    gelaende(w, rx + 5, art="wiese", dichte=0.2)
    B = _r(3 * u + 2)
    for x in range(-rx - B, rx + B + 1):
        for z in range(-rz - B, rz + B + 1):
            d_innen = (x / rx) ** 2 + (z / rz) ** 2
            d_aussen = (x / (rx + B)) ** 2 + (z / (rz + B)) ** 2
            if d_aussen <= 1 and d_innen >= 1:
                w.setze(x, 0, z, w.b("sand" if (x + z) % 5 else "coarse_dirt"))
                w.bloecke.pop((x, 1, z), None)
    for k in range(int((rx + rz) * 6)):
        a = k / ((rx + rz) * 6) * 6.28
        for (r_x, r_z) in ((rx, rz), (rx + B, rz + B)):
            w.setze(round(math.cos(a) * r_x), 1, round(math.sin(a) * r_z), zf(w, "birch", east=True, west=True))
    for k in range(5):
        x = -4 + k * 2
        for y in (1, 2, 3):
            w.setze(x, y, rz + 1, w.b("white_concrete") if y == 3 else zf(w, "birch"))
    for y in range(1, 6):
        w.setze(rx // 2, y, rz + B + 2, w.b("spruce_log", axis="y"))
    for x in range(rx // 2 - 1, rx // 2 + 2):
        for z in range(rz + B + 1, rz + B + 4):
            w.setze(x, 6, z, w.b("spruce_planks"))
    return w


def drachenarena(seed, g=3):
    """Drachenarena: eine gewaltige, kreisrunde Grube mit Mauern aus Schwarzstein, riesigen Ketten an Ringen, einem
    Käfigtor, verbrannten Spuren und Tribünen hoch oben."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    T = _r(6 * u + 3)
    gelaende(w, R + 8, art="wiese", dichte=0.15)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d <= R:
                for y in range(-T, 1):
                    w.bloecke.pop((x, y, z), None)
                w.setze(x, -T, z, w.b(["blackstone", "basalt", "coarse_dirt", "magma_block"][(x * 3 + z) % 4],
                                      **({"axis": "y"} if (x * 3 + z) % 4 == 1 else {})))
            elif d <= R + 2:
                for y in range(-T, 3):
                    w.setze(x, y, z, w.b("polished_blackstone_bricks" if y % 3 else "blackstone"))
    for k in range(6):
        a = k / 6 * 6.28
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        linie(w, (x, -1, z), (x * 0.5, -T + 1, z * 0.5), w.b("chain", axis="y", waterlogged=False))
        w.setze(x, 0, z, w.b("iron_block"))
    M = Mat(w, ["stone_bricks", "polished_blackstone_bricks", "cobblestone", "andesite"])
    ovaltribuene(w, 0, 0, R + 3, R + 3, _r(3 * u + 2), M, oeffnungen=(math.pi / 2,))
    for x in range(-3, 4):
        for y in range(-T + 1, -T + 6):
            w.setze(x, y, R, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
    return w


def magierduell(seed, g=2):
    """Magierduell-Plattform: zwei runde Steinpodeste mit Runenkreisen stehen sich auf einer schwebenden Insel
    gegenüber, verbunden durch eine leuchtende Bahn, umgeben von Kristallobelisken."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                w.setze(x, 0, z, w.b("polished_deepslate" if (x + z) % 2 else "deepslate_tiles"))
    for sx in (-1, 1):
        cx = sx * round(R * 0.55)
        r = 3 * u + 1.5
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(x, z)
                if d <= r:
                    w.setze(cx + x, 1, z, w.b("chiseled_polished_blackstone" if abs(d - r * 0.7) < 0.6 else
                                              "polished_blackstone"))
        w.setze(cx, 2, 0, w.b("enchanting_table"))
        farbe = "purple_stained_glass" if sx < 0 else "light_blue_stained_glass"
        for k in range(6):
            a = k / 6 * 6.28
            for y in range(1, _r(4 * u + 3)):
                w.setze(cx + round(math.cos(a) * (r + 1.5)), y, round(math.sin(a) * (r + 1.5)),
                        w.b("obsidian" if y % 3 else farbe))
    for x in range(-round(R * 0.55) + 4, round(R * 0.55) - 3):
        w.setze(x, 0, 0, w.b("sea_lantern"))
    return w


def faustkampfgrube(seed, g=1):
    """Faustkampfgrube: eine in den Boden gegrabene, mit Bohlen ausgekleidete Grube, Zuschauer stehen am Rand
    hinter Seilen, Fackeln an Pfählen."""
    w = _neu(seed)
    u = U[g]
    R = _r(7 * u + 4)
    T = _r(2 * u + 1)
    gelaende(w, R + 5, art="wiese", dichte=0.2)
    for x in range(-R - 1, R + 2):
        for z in range(-R - 1, R + 2):
            rand = max(abs(x), abs(z)) == R + 1
            for y in range(-T, 1):
                if rand:
                    w.setze(x, y, z, w.b("spruce_planks" if (x + y) % 3 else "stripped_spruce_log", axis="y")
                            if (x + y) % 3 == 0 else w.b("spruce_planks"))
                else:
                    w.bloecke.pop((x, y, z), None)
            if not rand:
                w.setze(x, -T, z, w.b("coarse_dirt" if (x + z) % 2 else "dirt"))
    for k in range(-R - 2, R + 3, 3):
        for (x, z) in ((k, -R - 3), (k, R + 3), (-R - 3, k), (R + 3, k)):
            w.setze(x, 1, z, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
            w.setze(x, 2, z, w.b("lantern", hanging=False, waterlogged=False)) if k % 6 == 0 else None
    return w


def siegerpodest(seed, g=1):
    """Siegerpodest: drei gestaffelte Stufen aus Stein mit Gold, Silber und Bronze, ein Ehrenbogen mit Lorbeer und
    Fahnenmasten."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.2)
    for i, (dx, h, top) in enumerate(((0, 3, "gold_block"), (-3, 2, "iron_block"), (3, 1, "copper_block"))):
        for x in range(dx - 1, dx + 2):
            for z in range(-1, 2):
                for y in range(1, h + 1):
                    w.setze(x, y, z, w.b("smooth_quartz") if y < h else w.b(top))
    for k in range(int(5 * 4)):
        a = k / 20 * math.pi
        x, y = round(math.cos(a) * 5), round(4 + math.sin(a) * 4)
        w.setze(x, y, -3, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
    for sx in (-6, 6):
        for y in range(1, 8):
            w.setze(sx, y, -3, zf(w, "spruce"))
        w.setze(sx - 1, 7, -3, w.b("red_wool"))
        w.setze(sx - 1, 6, -3, w.b("yellow_wool"))
    return w


def ehrentor(seed, g=2):
    """Ehrentor der Arena: ein mächtiger Torbau mit zwei Rundtürmen, Wappen über dem Bogen, Fallgatter und
    Bannerallee davor."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.2)
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="spruce")
    B = _r(3 * u + 1.5)
    H = _r(8 * u + 4)
    for sx in (-1, 1):
        P.turm(w, st, sx * (B + 3), 0, 1, H + 3, 2.5 * u + 1, dach="kegel", krone=True,
               fahne=FARBPAARE[seed % 6][0])
    M = Mat(w, ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks"])
    for x in range(-B - 1, B + 2):
        for z in range(-2, 3):
            for y in range(1, H + 1):
                if abs(x) <= B and y < H - 2:
                    continue
                w.setze(x, y, z, M(x, y, z, y / H))
    for x in range(-B, B + 1):
        for y in range(H - 5, H - 2):
            w.setze(x, y, 0, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
    w.setze(0, H - 1, 3, w.b(f"{FARBPAARE[seed % 6][0]}_wool"))
    w.setze(0, H, 3, w.b("gold_block"))
    bannerreihe(w, -B - 1, -B - 1, 6, h=6)
    for z in range(5, R, 4):
        for sx in (-B - 2, B + 2):
            for y in range(1, 6):
                w.setze(sx, y, z, zf(w, "spruce"))
            f = FARBPAARE[(seed + z) % 6]
            for y in range(3, 6):
                w.setze(sx, y, z + 1, w.b(f"{f[y % 2]}_wool"))
    return w


def waffenkammer(seed, g=1):
    """Waffenkammer: ein Steinhaus mit offenem Vordach, an dem Schilde mit Wappen hängen, Waffenregale, Schleifstein,
    Amboss und Rüstungsständer."""
    from haeuser2 import vordach, werkbank
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.2)
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="mcw_schiefer", holz="spruce")
    a, b = _r(4 * u + 1, 3), _r(3 * u + 1, 2)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=4, dach="sattel", tuer="south", gauben=False, kamine=1)
    vordach(w, st, -a, a, b, 4, "south", 3)
    werkbank(w, -a + 1, b + 2, gegenstaende=("grindstone", "anvil", "smithing_table"))
    for x in range(-a + 1, a, 2):
        f = FARBPAARE[(seed + x) % 6]
        w.setze(x, 3, b + 1, w.b(f"{f[0]}_wool"))
    waffenstaender(w, a - 3, b + 3)
    return w


def heilerzelt(seed, g=1):
    """Heilerzelt: ein großes weißes Zelt mit rotem Kreuzwimpel, Feldbetten, Kräuterkisten, Kessel mit Sud und
    Wasserfässern."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.25)
    zelt(w, 0, 0, 3 * u + 1.5, ("white", "white"), wimpel=False)
    H = int((3 * u + 1.5) * 1.6) + 2
    w.setze(0, H + 2, 0, zf(w, "spruce"))
    w.setze(-1, H + 2, 0, w.b("red_wool"))
    for k in range(3):
        w.setze(-1 + k, 1, -1, w.b("white_bed", facing="north", part="foot", occupied=False))
    w.setze(round(3 * u) + 3, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    w.setze(round(3 * u) + 3, 2, 0, w.b("cauldron"))
    for k in range(3):
        w.setze(-round(3 * u) - 3, 1, -1 + k, w.b("barrel", facing="up", open=False))
    return w


def steinstossplatz(seed, g=1):
    """Kraftspiele-Platz: Baumstämme zum Werfen, Steinkugeln in Reihen, eine Zugseil-Bahn, Messlatten und Fahnen –
    für Wettkämpfe der Stärksten."""
    w = _neu(seed)
    u = U[g]
    L = _r(14 * u + 5)
    gelaende(w, L + 3, art="wiese", dichte=0.1)
    for k in range(4):
        x = -L + 3 + k * 2
        for d in range(5):
            w.setze(x, 1, -4 + d, w.b("spruce_log", axis="z"))
    for k in range(5):
        x = -L + 3 + k * 3
        r = 0.6 + k * 0.25
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for dy in (0, 1):
                    if dx * dx + dz * dz + dy * dy <= r * r + 0.3:
                        w.setze(x + dx, 1 + dy, 4 + dz, w.b("smooth_stone"))
    for x in range(0, L + 1):
        w.setze(x, 0, 0, w.b("white_concrete" if x % 5 == 0 else "dirt_path"))
    for x in range(2, L, 5):
        for y in range(1, 4):
            w.setze(x, y, -2, zf(w, "birch"))
    return w


def hindernisparcours(seed, g=1):
    """Hindernisparcours: Hürden, Balancierbalken, Kletterwand, Seilschwingen über einen Graben und Strohsäcke –
    zur Ausbildung junger Knappen."""
    w = _neu(seed)
    u = U[g]
    L = _r(16 * u + 6)
    gelaende(w, L + 3, art="wiese", dichte=0.1)
    x = -L
    stationen = ["huerde", "balken", "graben", "wand", "huerde", "stroh"]
    i = 0
    while x < L - 4:
        art = stationen[i % len(stationen)]
        if art == "huerde":
            for z in (-1, 0, 1):
                w.setze(x, 1, z, zf(w, "oak", north=z > -1, south=z < 1))
        elif art == "balken":
            for d in range(5):
                w.setze(x + d, 1, 0, w.b("spruce_log", axis="x"))
        elif art == "graben":
            for d in range(4):
                for z in (-2, -1, 0, 1, 2):
                    w.setze(x + d, 0, z, w.b("water", level=0))
                    w.setze(x + d, -1, z, w.b("mud"))
            for y in range(1, 6):
                w.setze(x + 1, y, -3, w.b("spruce_log", axis="y"))
            w.setze(x + 1, 5, -2, w.b("spruce_log", axis="z"))
            for y in range(2, 5):
                w.setze(x + 1, y, -1, MB.seil(w, "y"))
        elif art == "wand":
            for z in (-1, 0, 1):
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("spruce_planks"))
            for y in range(1, 4):
                w.setze(x - 1, y, 0, w.b("ladder", facing="west", waterlogged=False))
        else:
            for d in range(3):
                w.setze(x + d, 1, 0, w.b("hay_block", axis="x"))
        x += 6
        i += 1
    return w


def seeschlachtbecken(seed, g=2):
    """Seeschlacht-Becken: ein geflutetes, ovales Becken mit zwei kleinen Kriegsschiffen, Steinrängen ringsum und
    Schleusentor – für Schaukämpfe auf dem Wasser."""
    from boote import ruderboot
    from lib import einfuegen
    w = _neu(seed)
    u = U[g]
    rx, rz = _r(14 * u + 5), _r(9 * u + 4)
    gelaende(w, rx + 8, art="wiese", dichte=0.2)
    for x in range(-rx, rx + 1):
        for z in range(-rz, rz + 1):
            if (x / rx) ** 2 + (z / rz) ** 2 <= 1:
                for y in range(-2, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -3, z, w.b("smooth_stone"))
                w.bloecke.pop((x, 1, z), None)
    M = Mat(w, ["stone_bricks", "smooth_stone", "polished_andesite", "cobblestone"])
    ovaltribuene(w, 0, 0, rx + 1, rz + 1, _r(3 * u + 2), M, oeffnungen=(0,))
    for k in range(2):
        einfuegen(w, ruderboot(seed + k, min(3, g + 1)), -rx // 3 + k * 2 * rx // 3, 0, (k * 2 - 1) * 2)
    return w


def bestiengrube(seed, g=2):
    """Bestiengrube: eine tiefe Grube mit Käfigen aus Eisengittern an den Wänden, Knochen am Boden, Ketten und
    einer Brücke darüber für die Zuschauer."""
    w = _neu(seed)
    u = U[g]
    R = _r(9 * u + 4)
    T = _r(5 * u + 3)
    gelaende(w, R + 5, art="wiese", dichte=0.2)
    for x in range(-R - 1, R + 2):
        for z in range(-R - 1, R + 2):
            rand = max(abs(x), abs(z)) == R + 1
            for y in range(-T, 1):
                if rand:
                    w.setze(x, y, z, w.b("cobblestone" if (x + y) % 3 else "mossy_cobblestone"))
                else:
                    w.bloecke.pop((x, y, z), None)
            if not rand:
                w.setze(x, -T, z, w.b("coarse_dirt" if (x + z) % 3 else "gravel"))
                if (x * 7 + z) % 13 == 0:
                    w.setze(x, -T + 1, z, w.b("bone_block", axis="x"))
    for k in range(4):
        x = -R + 1 + k * (2 * R - 2) // 3
        for y in range(-T + 1, -T + 4):
            w.setze(x, y, -R, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
    for x in range(-R - 3, R + 4):
        w.setze(x, 1, 0, w.b("spruce_slab", type="bottom", waterlogged=False))
        for z in (-1, 1):
            w.setze(x, 2, z, zf(w, "spruce", east=True, west=True))
    return w


def trainingshof(seed, g=1):
    """Trainingshof: ein umzäunter Hof mit Quintana (Drehpuppe für Lanzenübungen), Strohpuppen, Zielscheiben,
    Holzschwert-Ständer und einem Unterstand."""
    w = _neu(seed)
    u = U[g]
    R = _r(11 * u + 5)
    gelaende(w, R + 2, art="wiese", dichte=0.1)
    sand(w, -R, -R, R, R)
    for k in range(-R, R + 1):
        for (x, z) in ((k, -R), (k, R), (-R, k), (R, k)):
            w.setze(x, 1, z, zf(w, "oak", east=abs(z) == R, west=abs(z) == R, north=abs(x) == R, south=abs(x) == R))
    for y in range(1, 4):
        w.setze(0, y, 0, w.b("spruce_log", axis="y"))
    for x in range(-2, 3):
        w.setze(x, 4, 0, w.b("spruce_planks") if x else w.b("spruce_log", axis="y"))
    w.setze(-2, 3, 0, w.b("red_wool"))
    w.setze(2, 3, 0, w.b("hay_block", axis="y"))
    for k in range(3):
        x = -R + 3 + k * 3
        w.setze(x, 1, R - 3, zf(w, "oak"))
        w.setze(x, 2, R - 3, w.b("hay_block", axis="y"))
        w.setze(x, 3, R - 3, w.b("carved_pumpkin", facing="north"))
    for k in range(2):
        w.setze(R - 2, 2, -R + 3 + k * 3, w.b("target", power=0))
        w.setze(R - 2, 1, -R + 3 + k * 3, w.b("hay_block", axis="y"))
    return w


def labyrintharena(seed, g=2):
    """Labyrinth-Arena: ein Heckenlabyrinth mit Steinpfeilern, in dessen Mitte ein Podest mit Siegerglocke wartet –
    für Wettläufe und Turnierspiele."""
    w = _neu(seed)
    u = U[g]
    n = 5 + 2 * g
    zelle = 3
    R = n * zelle // 2 + 1
    gelaende(w, R + 3, art="wiese", dichte=0.05)
    rng = w.rng
    besucht = set()
    waende = set()
    for i in range(n):
        for j in range(n):
            waende.add((i, j, "e"))
            waende.add((i, j, "s"))
    stapel = [(0, 0)]
    besucht.add((0, 0))
    while stapel:
        i, j = stapel[-1]
        nb = [(i + di, j + dj, d) for di, dj, d in ((1, 0, "e"), (-1, 0, "w"), (0, 1, "s"), (0, -1, "n"))
              if 0 <= i + di < n and 0 <= j + dj < n and (i + di, j + dj) not in besucht]
        if not nb:
            stapel.pop()
            continue
        ni, nj, d = nb[int(rng.integers(len(nb)))]
        if d == "e":
            waende.discard((i, j, "e"))
        elif d == "w":
            waende.discard((ni, nj, "e"))
        elif d == "s":
            waende.discard((i, j, "s"))
        else:
            waende.discard((ni, nj, "s"))
        besucht.add((ni, nj))
        stapel.append((ni, nj))
    ox = -n * zelle // 2
    hecke = w.b("oak_leaves", persistent=True, distance=1, waterlogged=False)
    for (i, j, d) in waende:
        x0, z0 = ox + i * zelle, ox + j * zelle
        for k in range(zelle + 1):
            x, z = (x0 + zelle, z0 + k) if d == "e" else (x0 + k, z0 + zelle)
            for y in (1, 2):
                w.setze(x, y, z, hecke)
    for k in range(n * zelle + 1):
        for (x, z) in ((ox + k, ox), (ox, ox + k)):
            if not (x == ox and z == ox + 1):
                for y in (1, 2):
                    w.setze(x, y, z, hecke)
    c = ox + (n // 2) * zelle + 1
    w.setze(c, 1, c, w.b("bell", attachment="floor", facing="north", powered=False))
    return w


def turnierlager(seed, g=3):
    """Großes Turnierlager: dutzende Zelte der Ritterhäuser in Reihen, Fahnenstraße, Schmiede, Pferdekoppel,
    Marktstände und in der Mitte die Tjostbahn."""
    w = tjostbahn(seed, max(1, g - 1))
    u = U[g]
    R = _r(30 * u + 10)
    gelaende(w, R, art="wiese", dichte=0.2)
    rng = w.rng
    for i in range(int(8 + 4 * u)):
        a = i * 2.39996
        d = R * (0.55 + 0.35 * rng.random())
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        zelt(w, x, z, (1.4 + rng.random() * 0.8) * u + 0.8, FARBPAARE[(seed + i) % 6])
    return w


def riesenschach(seed, g=2):
    """Riesenschach: ein Schachbrett aus schwarzen und weißen Platten, auf dem mannshohe Figuren aus Stein und
    Quarz stehen, ringsum Bänke für Zuschauer."""
    w = _neu(seed)
    u = U[g]
    f = _r(2 * u + 1, 2)
    R = 4 * f + 4
    gelaende(w, R, art="wiese", dichte=0.1)
    for i in range(8):
        for j in range(8):
            for dx in range(f):
                for dz in range(f):
                    w.setze(-4 * f + i * f + dx, 0, -4 * f + j * f + dz,
                            w.b("smooth_quartz" if (i + j) % 2 else "polished_blackstone"))

    def figur(x, z, art, farbe):
        h = {"bauer": 2, "turm": 3, "springer": 3, "laeufer": 4, "dame": 5, "koenig": 6}[art] * u * 0.8 + 1
        h = _r(h)
        m = "quartz_block" if farbe == "w" else "polished_blackstone"
        for y in range(1, h + 1):
            w.setze(x, y, z, w.b(m))
        if art == "turm":
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                w.setze(x + dx, h, z + dz, w.b(m))
        elif art == "koenig":
            w.setze(x, h + 1, z, w.b("gold_block"))
            w.setze(x, h + 2, z, w.b("gold_block"))
        elif art == "dame":
            w.setze(x, h + 1, z, w.b("gold_block"))
        elif art == "springer":
            w.setze(x + 1, h, z, w.b(m))
        elif art == "laeufer":
            w.setze(x, h + 1, z, w.b("quartz_slab" if farbe == "w" else "polished_blackstone_slab", type="bottom",
                                     waterlogged=False))

    reihe = ["turm", "springer", "laeufer", "dame", "koenig", "laeufer", "springer", "turm"]
    for i, art in enumerate(reihe):
        for (j, farbe, a) in ((0, "w", art), (1, "w", "bauer"), (7, "s", art), (6, "s", "bauer")):
            if (i + j) % 3 == 0 or j in (0, 7):
                figur(-4 * f + i * f + f // 2, -4 * f + j * f + f // 2, a, farbe)
    return w


def schiessstand(seed, g=1):
    """Armbrust-Schießstand: Schützenstände unter einem Pultdach, Zielscheiben auf Strohballen in drei
    Entfernungen, Wimpelleine und Schreiberpult für die Punkte."""
    w = _neu(seed)
    u = U[g]
    L = _r(18 * u + 6)
    gelaende(w, L + 3, art="wiese", dichte=0.1)
    for z in range(-5, 6):
        for x in (-L, -L + 1):
            w.setze(x, 0, z, w.b("spruce_planks"))
        w.setze(-L - 1, 4, z, w.b("spruce_slab", type="bottom", waterlogged=False))
        w.setze(-L, 4, z, w.b("spruce_slab", type="bottom", waterlogged=False))
        if z % 2 == 0:
            w.setze(-L + 1, 1, z, zf(w, "spruce"))
    for z in (-5, 5):
        for y in range(1, 4):
            w.setze(-L - 1, y, z, w.b("spruce_log", axis="y"))
    for k, x in enumerate((-L // 3, L // 4, L - 2)):
        for z in (-3, 0, 3):
            w.setze(x, 1, z, w.b("hay_block", axis="y"))
            w.setze(x, 2, z, w.b("hay_block", axis="y"))
            w.setze(x - 1, 2, z, w.b("target", power=0))
    for x in range(-L, L + 1):
        if x % 2:
            w.setze(x, 4, -7, w.b(["red_wool", "yellow_wool", "blue_wool"][x % 3]))
    w.setze(-L - 2, 1, 0, w.b("lectern", facing="east", has_book=True, powered=False))
    return w


def fahnenallee(seed, g=1):
    """Fahnenallee: der Prachtweg zum Turnierplatz, gesäumt von hohen Masten mit den Bannern aller Ritterhäuser,
    Kohlebecken und gepflastertem Mittelstreifen – kachelbar."""
    w = _neu(seed)
    L = [10, 16, 26, 38][g]
    u = U[g]
    gelaende(w, L + 3, art="wiese", dichte=0.15)
    for x in range(-L, L + 1):
        for z in range(-2, 3):
            w.setze(x, 0, z, w.b("cobblestone" if abs(z) < 2 else "stone_bricks"))
            w.bloecke.pop((x, 1, z), None)
        if x % 4 == 0:
            for s in (-4, 4):
                H = _r(6 * u + 3)
                for y in range(1, H + 1):
                    w.setze(x, y, s, zf(w, "dark_oak"))
                f = FARBPAARE[(seed + x // 4 + (s > 0)) % 6]
                for y in range(H - 3, H + 1):
                    for d in (1, 2):
                        w.setze(x + d, y, s, w.b(f"{f[(y + d) % 2]}_wool"))
                w.setze(x, H + 1, s, w.b("gold_block"))
        if x % 8 == 2:
            for s in (-3, 3):
                w.setze(x, 1, s, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


ARENA = {
    "tjostbahn": ("Tjostbahn", tjostbahn),
    "ritterzelte": ("Ritterlager", ritterzelte),
    "holzarena": ("Holzarena", holzarena),
    "steinarena": ("Steinarena", steinarena),
    "tribuene": ("Turniertribüne", tribuene_bau),
    "koenigsloge": ("Königsloge", koenigsloge),
    "schwertkampfring": ("Schwertkampfring", schwertkampfring),
    "pferderennbahn": ("Pferderennbahn", pferderennbahn),
    "drachenarena": ("Drachenarena", drachenarena),
    "magierduell": ("Magierduell-Plattform", magierduell),
    "faustkampfgrube": ("Faustkampfgrube", faustkampfgrube),
    "siegerpodest": ("Siegerpodest", siegerpodest),
    "ehrentor": ("Ehrentor der Arena", ehrentor),
    "waffenkammer": ("Waffenkammer", waffenkammer),
    "heilerzelt": ("Heilerzelt", heilerzelt),
    "steinstossplatz": ("Kraftspiele-Platz", steinstossplatz),
    "hindernisparcours": ("Hindernisparcours", hindernisparcours),
    "seeschlachtbecken": ("Seeschlacht-Becken", seeschlachtbecken),
    "bestiengrube": ("Bestiengrube", bestiengrube),
    "trainingshof": ("Trainingshof", trainingshof),
    "labyrintharena": ("Labyrinth-Arena", labyrintharena),
    "turnierlager": ("Großes Turnierlager", turnierlager),
    "riesenschach": ("Riesenschach", riesenschach),
    "schiessstand": ("Armbrust-Schießstand", schiessstand),
    "fahnenallee": ("Fahnenallee", fahnenallee),
}

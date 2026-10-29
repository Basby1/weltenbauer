"""Sternwarte & Astronomie – Kuppelsternwarten, Riesenteleskope, Radioteleskope, Planetarium, Sonnenuhren,
Steinkreis-Kalender, Armillarsphäre, Planetenmodell, Meteoritenkrater, Saturn, Schwarzes Loch, Nordlicht und
Sonnensystem-Park. Boden y = 0."""

from __future__ import annotations

import math

import numpy as np

import pracht as P
from flora import _neu, _r, _stil, linie
from lib import Rauschen
from pracht import Mat, gelaende

U = [0.6, 1.0, 1.7, 2.8]


def kugel(w, c, r, blk, ueber=True):
    cx, cy, cz = c
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for z in range(int(cz - r) - 1, int(cz + r) + 2):
                if (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2 <= r * r:
                    b = blk(x - cx, y - cy, z - cz) if callable(blk) else blk
                    if b is not None:
                        w.setze(x, y, z, w.b(b) if isinstance(b, str) else b, ueber)


def ring(w, c, R, r, blk, neig=0.0, achse="y"):
    """Torus (Planetenring/Armillarring) um c, geneigt um neig (Bogenmaß) um die x-Achse."""
    cx, cy, cz = c
    ca, sa = math.cos(neig), math.sin(neig)
    n = int(R * 12) + 8
    for k in range(n):
        a = k / n * 6.28
        x, z = math.cos(a) * R, math.sin(a) * R
        y = 0.0
        if achse == "y":
            y, z = -z * sa, z * ca
        elif achse == "z":
            x, y, z = x, z, 0
        for dx in range(-int(r), int(r) + 1):
            for dy in range(-int(r), int(r) + 1):
                if dx * dx + dy * dy <= r * r + 0.2:
                    p = (round(cx + x + dx), round(cy + y + dy), round(cz + z))
                    w.setze(*p, w.b(blk(k) if callable(blk) else blk))


def teleskop(w, basis, richtung, L, r, mat="iron_block", ring_mat="gold_block"):
    d = np.asarray(richtung, float)
    d /= np.linalg.norm(d)
    b = np.asarray(basis, float)
    linie(w, tuple(b - d * L * 0.3), tuple(b + d * L * 0.7), w.b(mat), r)
    for t in (-0.25, 0.2, 0.65):
        p = b + d * L * t
        kugel(w, tuple(p), r + 0.7, lambda x, y, z: ring_mat if abs(np.dot((x, y, z), d)) < 0.6 else None, False)
    end = b + d * L * 0.7
    w.setze(round(end[0]), round(end[1]), round(end[2]), w.b("light_blue_stained_glass"))


def kuppel_mit_spalt(w, cx, cz, y0, R, mat="white_concrete", spalt="black_concrete", richtung=(1, 0)):
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            for y in range(0, int(R) + 2):
                d = math.sqrt(x * x + y * y + z * z)
                if R - 1.1 < d <= R:
                    im_spalt = abs(z * richtung[0] - x * richtung[1]) < 1.2 and (x * richtung[0] + z * richtung[1]) > -1
                    blk = spalt if im_spalt else (mat if (y % 3 or y == 0) else "light_gray_concrete")
                    if im_spalt:
                        continue
                    w.setze(cx + x, y0 + y, cz + z, w.b(blk))


def sternenboden(w, R, cx=0, cz=0, grund="black_concrete", stern="sea_lantern", dichte=0.06):
    rng = w.rng
    for x in range(int(cx - R), int(cx + R) + 1):
        for z in range(int(cz - R), int(cz + R) + 1):
            if math.hypot(x - cx, z - cz) <= R:
                w.setze(x, 0, z, w.b(stern if rng.random() < dichte else grund))


# ============================================================================ Bauten

def sternwarte(seed, g=2):
    """Kuppelsternwarte: ein runder Steinbau mit weißer, drehbarer Kuppel und geöffnetem Spalt, aus dem ein großes
    Fernrohr ragt, Treppe, Laternen und ein Garten mit Sonnenuhr."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.3)
    st = P.Stil(w, wand="graustein" if _stil(seed) == 0 else "backstein", sockel="graustein", gesims="stone_brick",
                dach="schiefer", holz="spruce", fensterart="bogen")
    r = _r(5 * u + 2)
    H = _r(6 * u + 3)
    P.turm(w, st, 0, 0, 1, H, r, dach="platt", krone=False, fenster=6)
    kuppel_mit_spalt(w, 0, 0, H + 1, r + 0.5)
    teleskop(w, (0, H + 2 + r * 0.3, 0), (1, 1.1, 0.2), r * 2.2, 0.8 * u + 0.4)
    for k in range(H):
        a = k * 0.4
        w.setze(round(math.cos(a) * (r + 1.5)), 1 + k, round(math.sin(a) * (r + 1.5)),
                w.b("stone_brick_slab", type="top", waterlogged=False), False)
    for y in range(1, 3):
        w.setze(R - 4, y, R - 4, w.b("stone_bricks"))
    w.setze(R - 4, 3, R - 4, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return w


def riesenteleskop(seed, g=2):
    """Riesenteleskop: ein freistehender Refraktor aus Messing auf einer gewaltigen Gabelmontierung mit
    Zahnkranz, Beobachterplattform und Leiter."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.25)
    for x in range(-4, 5):
        for z in range(-4, 5):
            if x * x + z * z <= 16:
                for y in (1, 2):
                    w.setze(x, y, z, w.b("polished_andesite" if y == 1 else "smooth_stone"))
    Hm = _r(6 * u + 3)
    for sx in (-2, 2):
        for y in range(3, 3 + Hm):
            w.setze(sx, y, 0, w.b("waxed_cut_copper"))
    teleskop(w, (0, 3 + Hm, 0), (0.3, 0.8, 1), _r(20 * u + 6), 1.2 * u + 0.6, mat="waxed_copper_block",
             ring_mat="gold_block")
    for k in range(int(8 * 4)):
        a = k / 32 * 6.28
        w.setze(round(math.cos(a) * 4), 3, round(math.sin(a) * 4), w.b("gold_block" if k % 2 else "waxed_cut_copper"))
    for y in range(1, 3 + Hm):
        w.setze(-4, y, 3, w.b("ladder", facing="west", waterlogged=False))
    return w


def radioteleskop(seed, g=2):
    """Radioteleskop: eine riesige weiße Parabolschüssel auf einem Drehgestell, mit Empfangsmast im Brennpunkt,
    Kontrollgebäude und Kabelkanälen."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.25)
    rs = 10 * u + 4
    yc = _r(8 * u + 4)
    for y in range(1, yc):
        for dx in (-2, 2):
            w.setze(dx, y, 0, w.b("white_concrete"))
    neig = 0.6
    ca, sa = math.cos(neig), math.sin(neig)
    for i in range(-int(rs), int(rs) + 1):
        for j in range(-int(rs), int(rs) + 1):
            if i * i + j * j > rs * rs:
                continue
            h = (i * i + j * j) / (4 * rs * 0.55)
            x, y, z = i, h, j
            y2 = y * ca - z * sa
            z2 = y * sa + z * ca
            for t in (0, 0.5):
                w.setze(round(x), yc + round(y2 + t), round(z2), w.b("white_concrete" if (i + j) % 6 else
                                                                     "light_gray_concrete"))
    f = rs * 0.55
    fy, fz = f * ca, f * sa
    for k in range(3):
        a = k / 3 * 6.28
        linie(w, (math.cos(a) * rs * 0.7, yc + (rs * 0.7) ** 2 / (4 * rs * 0.55) * ca - math.sin(a) * rs * 0.7 * sa,
                  math.sin(a) * rs * 0.7 * ca), (0, yc + fy, fz), w.b("light_gray_concrete"))
    w.setze(0, round(yc + fy), round(fz), w.b("iron_block"))
    st = P.Stil(w, wand=["white_concrete", "light_gray_concrete"], sockel="graustein", gesims="stone_brick",
                dach="grau", holz="spruce")
    P.gebaeude(w, st, R - 9, -R + 3, R - 3, -R + 8, y0=1, etagen=1, eh=4, dach="sattel", tuer="west",
               gauben=False, kamine=0)
    return w


def antennenfeld(seed, g=2):
    """Antennenfeld: ein Verbund aus sechs kleineren Radioschüsseln, alle zum selben Punkt am Himmel gerichtet,
    verbunden durch Kabeltrassen und eine Messstation."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.2)
    for k in range(6):
        a = k / 6 * 6.28
        cx, cz = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        rs = 3 * u + 2
        yc = _r(3 * u + 2)
        for y in range(1, yc):
            w.setze(cx, y, cz, w.b("white_concrete"))
        for i in range(-int(rs), int(rs) + 1):
            for j in range(-int(rs), int(rs) + 1):
                if i * i + j * j <= rs * rs:
                    h = (i * i + j * j) / (4 * rs * 0.5)
                    w.setze(cx + i, yc + round(h * 0.8 + j * 0.5), cz + j, w.b("white_concrete"))
        linie(w, (cx, 1, cz), (0, 1, 0), w.b("gray_concrete"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            for y in range(1, 4):
                if abs(x) == 2 or abs(z) == 2 or y == 3:
                    w.setze(x, y, z, w.b("light_gray_concrete" if y < 3 else "white_concrete"))
    return w


def planetarium(seed, g=2):
    """Planetarium: ein Gebäude mit großer Halbkugel-Kuppel, innen ein Sternenhimmel aus Lichtpunkten (Schnitt
    geöffnet), Säulenvorhalle und Sternbild-Mosaik auf dem Vorplatz."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.2)
    rk = 8 * u + 3
    rng = w.rng
    for x in range(-int(rk) - 1, int(rk) + 2):
        for z in range(-int(rk) - 1, int(rk) + 2):
            for y in range(0, int(rk) + 2):
                d = math.sqrt(x * x + y * y + z * z)
                if rk - 1.2 < d <= rk:
                    if x > 0 and z > 0 and y > 1:
                        continue
                    w.setze(x, 2 + y, z, w.b("white_concrete"))
                    if rng.random() < 0.08:
                        w.setze(x - int(np.sign(x)), 2 + y, z - int(np.sign(z)), w.b("sea_lantern"), False)
                elif d <= rk - 1.2 and y == 0:
                    w.setze(x, 1, z, w.b("black_concrete"))
    for x in range(-int(rk) - 2, int(rk) + 3):
        for z in range(-int(rk) - 2, int(rk) + 3):
            if math.hypot(x, z) < rk + 2:
                w.setze(x, 0, z, w.b("polished_andesite"))
    for k in range(5):
        x = -4 + k * 2
        for y in range(1, 6):
            w.setze(x, y, round(rk) + 3, w.b("quartz_pillar", axis="y"))
    for x in range(-5, 6):
        w.setze(x, 6, round(rk) + 3, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
    sternenboden(w, 5, 0, round(rk) + 9, dichte=0.15)
    return w


def sonnenuhr(seed, g=2):
    """Große Sonnenuhr: ein gepflasterter Platz mit Stundenlinien aus Gold, römischen Ziffernsteinen am Rand und
    einem hohen schrägen Schattenstab (Gnomon) in der Mitte."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R + 3, art="wiese", dichte=0.25)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d <= R:
                a = math.degrees(math.atan2(z, x)) % 15
                w.setze(x, 0, z, w.b("gold_block" if a < 1.5 and d > 2 else "smooth_sandstone" if d < R - 1.5
                                     else "chiseled_sandstone"))
    for k in range(12):
        a = k / 12 * 6.28
        x, z = round(math.cos(a) * (R - 0.5)), round(math.sin(a) * (R - 0.5))
        w.setze(x, 1, z, w.b("chiseled_stone_bricks"))
    H = _r(10 * u + 4)
    linie(w, (0, 1, 0), (0, H, -H * 0.8), w.b("waxed_cut_copper"), 0.6 if u > 1 else 0)
    linie(w, (0, 1, -H * 0.8), (0, H, -H * 0.8), w.b("waxed_cut_copper"))
    return w


def steinkreis(seed, g=2):
    """Himmelskalender: ein Steinkreis aus mächtigen Trilithen, durch dessen Tor am Sonnwendtag die Sonne genau auf
    den Altarstein fällt, mit Fersenstein und Wall."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R + 5, art="wiese", dichte=0.3)
    M = Mat(w, ["stone", "andesite", "mossy_cobblestone", "tuff", "cobblestone"])
    n = 10
    H = _r(5 * u + 3)
    for i in range(n):
        a = i / n * 6.28
        x, z = math.cos(a) * R, math.sin(a) * R
        for y in range(1, H + 1):
            for d in (-1, 0, 1) if u > 1 else (0,):
                p = (round(x - math.sin(a) * d), y, round(z + math.cos(a) * d))
                w.setze(*p, M(*p, y / H))
        if i % 2 == 0:
            a2 = (i + 1) / n * 6.28
            linie(w, (x, H + 1, z), (math.cos(a2) * R, H + 1, math.sin(a2) * R), M(0, H, 0, 0.9), 0.5)
    for x in range(-2, 3):
        for z in (-1, 0, 1):
            w.setze(x, 1, z, M(x, 1, z, 0.3))
    for y in range(1, H):
        w.setze(0, y, R + 5, M(0, y, R + 5, 0.5))
    for k in range(int(R * 8)):
        a = k / (R * 8) * 6.28
        w.setze(round(math.cos(a) * (R + 3)), 1, round(math.sin(a) * (R + 3)), w.b("grass_block", snowy=False))
    return w


def armillarsphaere(seed, g=2):
    """Armillarsphäre: ein riesiges Himmelsmodell aus ineinander gesetzten goldenen und kupfernen Ringen
    (Äquator, Ekliptik, Meridian) mit einer Erdkugel in der Mitte, auf einem Sockel."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    gelaende(w, R + 2, art="wiese", dichte=0.2)
    for k in range(3):
        rr = 3 - k
        for x in range(-rr, rr + 1):
            for z in range(-rr, rr + 1):
                w.setze(x, 1 + k, z, w.b(["polished_andesite", "smooth_stone", "chiseled_stone_bricks"][k]))
    Rr = 6 * u + 2.5
    c = (0, 4 + Rr, 0)
    ring(w, c, Rr, 0.4, "gold_block", neig=0)
    ring(w, c, Rr - 0.6, 0.4, "waxed_cut_copper", neig=0.41)
    ring(w, c, Rr, 0.4, "gold_block", neig=1.5708)
    ring(w, c, Rr * 0.75, 0.4, "waxed_copper_block", neig=-0.9)
    linie(w, (0, 4, 0), (0, 4 + 2 * Rr, 0), w.b("iron_bars", north=False, south=False, east=False, west=False,
                                                 waterlogged=False))
    kugel(w, c, 1.6 * u + 0.8, lambda x, y, z: "blue_concrete" if (x * 3 + y * 5 + z) % 4 else "lime_concrete")
    return w


def planetenmodell(seed, g=2):
    """Planetenmodell (Orrery): eine glühende Sonne in der Mitte, auf langen Messingarmen kreisen die Planeten mit
    Monden und Ringen, getragen von einem Zahnradsockel."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.15)
    for x in range(-4, 5):
        for z in range(-4, 5):
            if x * x + z * z <= 16:
                w.setze(x, 1, z, w.b("waxed_cut_copper" if (x + z) % 2 else "gold_block"))
    Hs = _r(6 * u + 3)
    for y in range(2, Hs):
        w.setze(0, y, 0, w.b("waxed_copper_block"))
    kugel(w, (0, Hs + 2 * u, 0), 2.2 * u + 1, lambda x, y, z: "shroomlight" if (x + y + z) % 3 else "glowstone")
    planeten = [(0.25, 0.4, "light_gray_concrete"), (0.38, 0.6, "orange_terracotta"), (0.52, 0.65, "blue_concrete"),
                (0.66, 0.5, "red_terracotta"), (0.82, 1.3, "orange_concrete"), (0.95, 1.1, "yellow_terracotta")]
    for i, (rd, rp, farbe) in enumerate(planeten):
        a = i * 2.39996
        r = R * rd
        p = (math.cos(a) * r, Hs + 2 * u, math.sin(a) * r)
        linie(w, (0, Hs, 0), (p[0], Hs, p[2]), w.b("gold_block" if i % 2 else "waxed_cut_copper"))
        linie(w, (p[0], Hs, p[2]), p, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                          waterlogged=False))
        kugel(w, p, rp * u + 0.5, farbe)
        if i == 5:
            ring(w, p, rp * u + 2, 0.3, "smooth_sandstone", neig=0.3)
        if i == 2:
            kugel(w, (p[0] + 2, p[1] + 1, p[2]), 0.6, "light_gray_concrete")
    return w


def meteoritenkrater(seed, g=2):
    """Meteoritenkrater: ein frischer Einschlagkrater mit aufgeworfenem Rand und verbrannter Erde, in der Mitte
    der noch glühende, schwarz-grüne Meteorit, verstreute Bruchstücke."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    rn = Rauschen(w, 3)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z) / R
            if d > 1:
                continue
            h = int(3 * u * math.exp(-((d - 0.62) / 0.15) ** 2) - (4 * u * (1 - d / 0.55) if d < 0.55 else 0))
            for y in range(min(-1, h - 2), h + 1):
                blk = ("coarse_dirt" if d > 0.7 else "blackstone" if d < 0.35 else "basalt") if y == h else "dirt"
                w.setze(x, y, z, w.b(blk, axis="y") if blk == "basalt" else w.b(blk))
            if d < 0.3 and rn(x, 0, z) > 0.7:
                w.setze(x, h, z, w.b("magma_block"))
    tief = int(-4 * u * (1 - 0 / 0.55))
    kugel(w, (0, tief + 2 * u, 0), 2.2 * u + 1, lambda x, y, z: "crying_obsidian" if (x + y + z) % 4 == 0 else
          "obsidian" if (x + z) % 3 else "emerald_block" if _stil(seed) else "gilded_blackstone")
    for k in range(int(6 * u)):
        a = w.rng.random() * 6.28
        d = R * (0.7 + 0.3 * w.rng.random())
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = max([p[1] for p in w.bloecke if p[0] == x and p[2] == z] + [0]) + 1
        w.setze(x, y, z, w.b("obsidian" if k % 2 else "blackstone"))
    return w


def saturnskulptur(seed, g=2):
    """Saturn-Skulptur: ein riesiger gebänderter Planet mit geneigtem Ringsystem, schwebend auf einem schlanken
    Sockel über einem Spiegelbecken."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.2)
    for x in range(-R + 3, R - 2):
        for z in range(-R + 3, R - 2):
            if math.hypot(x, z) < R * 0.7:
                w.setze(x, 0, z, w.b("water", level=0))
    rp = 5 * u + 2
    cy = rp + 6 * u + 3
    for y in range(1, int(cy - rp) + 1):
        w.setze(0, y, 0, w.b("smooth_quartz"))
    farben = ["yellow_terracotta", "orange_terracotta", "white_terracotta", "brown_terracotta", "yellow_terracotta"]
    kugel(w, (0, cy, 0), rp, lambda x, y, z: farben[int((y + rp) * 1.3) % 5])
    for k, (rr, f) in enumerate(((rp * 1.5, "smooth_sandstone"), (rp * 1.75, "white_terracotta"),
                                 (rp * 2.0, "light_gray_terracotta"))):
        ring(w, (0, cy, 0), rr, 0.6, f, neig=0.35)
    return w


def schwarzes_loch(seed, g=2):
    """Schwarzes Loch: eine pechschwarze Kugel, umgeben von einer glühenden, verzerrten Akkretionsscheibe in
    Orange, Gelb und Weiß – eine kosmische Skulptur."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    sternenboden(w, R, dichte=0.05)
    rp = 3 * u + 1.5
    cy = rp + 4 * u + 3
    kugel(w, (0, cy, 0), rp, "black_concrete")
    for k, f in enumerate(["white_concrete", "yellow_concrete", "orange_concrete", "orange_terracotta", "red_concrete",
                           "red_terracotta"]):
        ring(w, (0, cy, 0), rp + 1.2 + k * 0.9 * u, 0.5, f, neig=0.2)
    ring(w, (0, cy, 0), rp + 1.0, 0.5, "white_concrete", neig=1.45)
    return w


def nordlicht(seed, g=2):
    """Nordlicht-Ausblick: ein verschneiter Hügel mit Bank und Laternen, darüber wallt ein Vorhang aus grünem und
    violettem Licht am Himmel."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z) / R
            if d > 1:
                continue
            h = int(3 * u * (1 - d * d))
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("snow_block" if y == h else "dirt"))
    import wald2
    from lib import einfuegen
    for k in range(4):
        a = k * 1.6 + 0.5
        x, z = round(math.cos(a) * R * 0.75), round(math.sin(a) * R * 0.75)
        einfuegen(w, wald2.fichte(int(w.rng.integers(1, 10 ** 6)), H=_r(7 * u + 3)), x, int(3 * u * 0.4), z)
    top = int(3 * u) + 1
    for x in (-1, 0, 1):
        w.setze(x, top, 0, w.b("spruce_stairs", facing="north", half="bottom", shape="straight", waterlogged=False))
    Y = _r(18 * u + 8)
    for x in range(-R, R + 1):
        welle = math.sin(x * 0.25) * 3 * u
        for k in range(_r(8 * u + 3)):
            y = Y + k + round(math.sin(x * 0.4 + k * 0.3) * u)
            z = -R // 2 + round(welle)
            f = "lime_stained_glass" if k < 3 * u else "green_stained_glass" if k < 6 * u else "purple_stained_glass"
            if (x + k) % 3:
                w.setze(x, y, z, w.b(f))
    return w


def mondlandschaft(seed, g=2):
    """Mondlandschaft: eine graue Kraterebene mit Staub, ein Landemodul auf vier Beinen, Flagge, Fußspuren und die
    Erde als blaue Kugel darüber."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    rn = Rauschen(w, 3)
    rng = w.rng
    krater = [(rng.random() * 2 - 1, rng.random() * 2 - 1, 0.1 + rng.random() * 0.2) for _ in range(5)]
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) > R:
                continue
            h = 0
            for (kx, kz, kr) in krater:
                d = math.hypot(x / R - kx, z / R - kz) / kr
                if d < 1.3:
                    h += int(2 * u * (math.exp(-((d - 1) / 0.25) ** 2) - (1 - d * d) * 0.8 * (d < 1)))
            for y in range(-2, h + 1):
                w.setze(x, y, z, w.b(["light_gray_concrete_powder", "gray_concrete_powder", "andesite"][
                    int(rn(x, y, z) * 2.99)]))
    for sx in (-2, 2):
        for sz in (-2, 2):
            linie(w, (sx * 1.6, 1, sz * 1.6), (sx * 0.8, 4, sz * 0.8), w.b("gold_block"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            for y in range(4, 7):
                if abs(x) == 2 or abs(z) == 2 or y in (4, 6):
                    w.setze(x, y, z, w.b("gold_block" if y == 4 else "light_gray_concrete"))
    for y in range(1, 6):
        w.setze(5, y, 3, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
    for k in range(3):
        for d in range(2):
            w.setze(4 - k, 5 - d, 3, w.b(["red_wool", "white_wool", "blue_wool"][(k + d) % 3]))
    kugel(w, (-R * 0.5, 22 * u + 8, -R * 0.5), 3 * u + 1.5,
          lambda x, y, z: "blue_concrete" if (x * 3 + y * 7 + z * 5) % 5 else "lime_concrete" if y < 0 else
          "white_concrete")
    return w


def astronomenturm(seed, g=2):
    """Turm des Astronomen: ein schlanker Magierturm mit Sternbildfenstern, auf dessen Spitze eine offene
    Messingplattform mit Fernrohr, Himmelsglobus und Sternkarten-Tisch liegt."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.3)
    st = P.Stil(w, wand="tiefenschiefer" if _stil(seed) == 0 else "marmor", sockel="graustein",
                gesims="stone_brick", dach="mcw_blau", holz="dark_oak", fensterart="bogen")
    r = _r(3 * u + 1.5)
    H = _r(22 * u + 6)
    P.turm(w, st, 0, 0, 1, H, r, dach="platt", krone=False, fenster=5)
    for x in range(-r - 2, r + 3):
        for z in range(-r - 2, r + 3):
            if math.hypot(x, z) <= r + 2:
                w.setze(x, H + 1, z, w.b("waxed_cut_copper"))
                if math.hypot(x, z) > r + 1:
                    w.setze(x, H + 2, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                             waterlogged=False))
    teleskop(w, (1, H + 3, 0), (1, 1, 0.3), 6 * u + 2, 0.5)
    kugel(w, (-1.5, H + 3.5, 1), 1.2, lambda x, y, z: "blue_concrete" if (x + y + z) % 2 else "gold_block")
    w.setze(0, H + 2, -2, w.b("cartography_table"))
    for k in range(6):
        y = 4 + k * 3
        a = k * 1.1
        if y < H:
            w.setze(round(math.cos(a) * r), y, round(math.sin(a) * r), w.b("sea_lantern"))
    return w


def caracol(seed, g=2):
    """Schneckenturm-Observatorium: ein runder Turm mit Kuppeldach auf zwei breiten Stufenplattformen, kleine
    Sichtfenster in Richtung der Venus – nach mittelamerikanischem Vorbild."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.2)
    M = Mat(w, ["smooth_sandstone", "sandstone", "cut_sandstone", "mossy_cobblestone"])
    for k in range(2):
        rr = R - 2 - k * round(3 * u + 1)
        for x in range(-rr, rr + 1):
            for z in range(-rr, rr + 1):
                for y in range(1 + k * 2, 3 + k * 2):
                    w.setze(x, y, z, M(x, y, z, 0.4))
    for y in range(1, 5):
        for x in range(-1, 2):
            w.setze(x, y, R - 2 - y, w.b("sandstone_stairs", facing="north", half="bottom", shape="straight",
                                         waterlogged=False))
    r = 3 * u + 1.5
    H = _r(6 * u + 3)
    for y in range(5, 5 + H):
        for k in range(int(r * 8)):
            a = k / (r * 8) * 6.28
            fenster = y == 5 + H - 2 and k % int(r * 2) == 0
            if not fenster:
                w.setze(round(math.cos(a) * r), y, round(math.sin(a) * r), M(0, y, 0, 0.6))
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            for y in range(0, int(r) + 1):
                d = math.sqrt(x * x + y * y + z * z)
                if r - 1 < d <= r + 0.3:
                    w.setze(x, 5 + H + y, z, M(x, y, z, 0.8))
    return w


def samrat_yantra(seed, g=2):
    """Riesen-Sonnenuhr-Instrument: eine gewaltige dreieckige Schattenwand mit Treppe auf dem Rücken, flankiert
    von zwei viertelkreisförmigen Skalenbögen aus rotem Sandstein."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.15)
    L = _r(12 * u + 4)
    H = _r(9 * u + 3)
    for z in range(-L, L + 1):
        h = round(H * (z + L) / (2 * L))
        for y in range(1, h + 2):
            for x in (-1, 0, 1):
                w.setze(x, y, z, w.b("red_sandstone" if (y + z) % 4 else "smooth_red_sandstone"))
        w.setze(0, h + 2, z, w.b("red_sandstone_stairs", facing="south", half="bottom", shape="straight",
                                 waterlogged=False))
    for sx in (-1, 1):
        rb = L * 0.8
        for k in range(int(rb * 4)):
            a = k / (rb * 4) * math.pi
            z = round(math.cos(a) * rb)
            y = round(1 + math.sin(a) * rb * 0.5)
            for d in range(2, 5):
                w.setze(sx * d, 1, z, w.b("smooth_red_sandstone"))
            w.setze(sx * 3, y, z, w.b("white_terracotta" if k % 3 == 0 else "smooth_quartz"))
    return w


def kometenskulptur(seed, g=2):
    """Kometenskulptur: ein leuchtender Eiskern mit langem, sich auffächerndem Schweif aus Glas, schräg über einen
    Platz schießend, getragen von einem einzigen Bogen."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    sternenboden(w, R, grund="polished_deepslate", dichte=0.08)
    c = np.array([R * 0.4, 14 * u + 6, R * 0.3])
    kugel(w, tuple(c), 2.2 * u + 1, lambda x, y, z: "sea_lantern" if (x + y + z) % 3 else "packed_ice")
    d = np.array([-1.0, -0.35, -0.8])
    d /= np.linalg.norm(d)
    rng = w.rng
    for k in range(int(80 * u)):
        t = rng.random() * R * 1.5
        spread = t * 0.25
        p = c + d * t + rng.normal(size=3) * spread * np.array([1, 0.6, 1])
        w.setze(round(p[0]), round(p[1]), round(p[2]),
                w.b(["light_blue_stained_glass", "white_stained_glass", "cyan_stained_glass"][k % 3]), False)
    linie(w, (R * 0.4, 1, R * 0.3), tuple(c - np.array([0, 2.2 * u + 1, 0])), w.b("iron_bars", north=False,
                                                                                     south=False, east=False,
                                                                                     west=False, waterlogged=False))
    return w


def mondphasenpfad(seed, g=1):
    """Mondphasenpfad: ein Kreisweg mit acht runden Steinscheiben, die die Mondphasen von Neumond bis Vollmond
    zeigen, in der Mitte ein Mondstein auf einer Säule."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R + 3, art="wiese", dichte=0.3)
    for k in range(int(R * 8)):
        a = k / (R * 8) * 6.28
        for dr in (-1, 0, 1):
            w.setze(round(math.cos(a) * (R + dr)), 0, round(math.sin(a) * (R + dr)), w.b("gravel" if dr else
                                                                                         "smooth_stone"))
    rs = 1.6 * u + 1
    for i in range(8):
        a = i / 8 * 6.28
        cx, cz = math.cos(a) * R, math.sin(a) * R
        phase = i / 8
        for x in range(int(cx - rs) - 1, int(cx + rs) + 2):
            for z in range(int(cz - rs) - 1, int(cz + rs) + 2):
                dx, dz = x - cx, z - cz
                if dx * dx + dz * dz <= rs * rs:
                    hell_grenze = rs * math.cos(phase * 2 * math.pi)
                    hell = (dx > hell_grenze) if phase < 0.5 else (dx < -hell_grenze)
                    w.setze(x, 1, z, w.b("smooth_quartz" if hell else "polished_blackstone"))
    for y in range(1, 4):
        w.setze(0, y, 0, w.b("quartz_pillar", axis="y"))
    w.setze(0, 4, 0, w.b("pearlescent_froglight", axis="y"))
    return w


def sternschnuppenwiese(seed, g=2):
    """Sternschnuppenwiese: auf einer nächtlichen Wiese liegen herabgefallene Sternsplitter, die golden und weiß
    glühen, umringt von verbrannten Kreisen und Glühwürmchen."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.45)
    rng = w.rng
    for k in range(int(4 + 3 * u)):
        a = rng.random() * 6.28
        d = R * 0.8 * math.sqrt(rng.random())
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        r = 1.2 * u + 1
        for x in range(cx - 3, cx + 4):
            for z in range(cz - 3, cz + 4):
                if math.hypot(x - cx, z - cz) < r + 1.2:
                    w.setze(x, 0, z, w.b("coarse_dirt" if (x + z) % 2 else "soul_soil"))
                    w.bloecke.pop((x, 1, z), None)
        for j in range(5):
            dd = (rng.normal() * 0.4, 1, rng.normal() * 0.4)
            linie(w, (cx, 1, cz), (cx + dd[0] * r * 1.5, 1 + r * 1.5, cz + dd[2] * r * 1.5),
                  w.b(["glowstone", "gold_block", "shroomlight", "sea_lantern"][j % 4]))
    for k in range(int(10 * u)):
        a = rng.random() * 6.28
        d = rng.random() * R
        w.setze(round(math.cos(a) * d), round(2 + rng.random() * 4), round(math.sin(a) * d),
                w.b("ochre_froglight", axis="y"), False)
    return w


def sternenportal(seed, g=2):
    """Sternenportal: ein aufrechter Ring aus dunklem Stein mit eingelassenen Sternbildern, in seiner Mitte ein
    funkelnder Ausschnitt des Nachthimmels."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.2)
    rr = 5 * u + 2.5
    yc = rr + 2
    rng = w.rng
    for k in range(int(rr * 12)):
        a = k / (rr * 12) * 6.28
        for dr in (0, 1, 2):
            x, y = round(math.cos(a) * (rr + dr)), round(yc + math.sin(a) * (rr + dr))
            w.setze(x, y, 0, w.b("sea_lantern" if dr == 1 and k % 7 == 0 else "polished_blackstone_bricks"
                                 if dr != 1 else "chiseled_polished_blackstone"))
    for x in range(-int(rr), int(rr) + 1):
        for y in range(round(yc - rr), round(yc + rr) + 1):
            if x * x + (y - yc) ** 2 < (rr - 0.5) ** 2:
                w.setze(x, y, 0, w.b("sea_lantern" if rng.random() < 0.06 else "black_stained_glass"
                                     if rng.random() < 0.9 else "blue_stained_glass"))
    for x in range(-3, 4):
        for z in range(-1, 2):
            w.setze(x, 0, z, w.b("polished_blackstone"))
    return w


def sonnensystempark(seed, g=2):
    """Sonnensystem-Park: ein langer Spazierweg, an dem die Planeten maßstäblich als Kugeln auf Sockeln stehen,
    beginnend mit einer großen Sonne am Eingang."""
    w = _neu(seed)
    u = U[g]
    L = _r(26 * u + 8)
    for x in range(-L, L + 1):
        for z in range(-6, 7):
            w.setze(x, 0, z, w.b("grass_block", snowy=False) if abs(z) > 1 else w.b("gravel" if x % 2 else
                                                                                       "smooth_stone"))
    kugel(w, (-L + 4, 4 * u + 1, 0), 3.5 * u + 1.5, lambda x, y, z: "shroomlight" if (x + y + z) % 3 else
          "glowstone")
    planeten = [(0.4, "light_gray_concrete"), (0.7, "orange_terracotta"), (0.75, "blue_concrete"),
                (0.55, "red_terracotta"), (2.2, "orange_concrete"), (1.9, "yellow_terracotta"),
                (1.3, "light_blue_concrete"), (1.25, "blue_terracotta")]
    for i, (rp, f) in enumerate(planeten):
        x = round(-L + 10 + i * (2 * L - 12) / 8)
        z = 4 if i % 2 else -4
        r = rp * u * 0.6 + 0.5
        for y in range(1, 3):
            w.setze(x, y, z, w.b("smooth_quartz"))
        kugel(w, (x, 3 + r, z), r, f)
        if i == 5:
            ring(w, (x, 3 + r, z), r + 1.2, 0.3, "smooth_sandstone", neig=0.3)
    return w


def astronomenakademie(seed, g=2):
    """Astronomenakademie: ein langgestrecktes Lehrgebäude mit drei kleinen Beobachtungskuppeln auf dem Dach,
    Innenhof mit Sternkarte im Pflaster und Bibliotheksturm."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.2)
    st = P.Stil(w, wand="backstein" if _stil(seed) == 0 else "marmor", sockel="graustein", gesims="stone_brick",
                dach="kupfer", holz="spruce", fensterart="bogen")
    a = _r(10 * u + 3)
    P.gebaeude(w, st, -a, -R + 3, a, -R + 9, y0=1, etagen=2, eh=4, dach="platt" if False else "walm", tuer="south",
               gauben=False, kamine=0)
    for k in range(3):
        x = -a + 3 + k * (a - 3)
        kuppel_mit_spalt(w, x, -R + 6, 10, 2.5 * u + 1)
    sternenboden(w, R * 0.4, 0, R * 0.2, grund="polished_andesite", stern="gold_block", dichte=0.06)
    P.turm(w, st, a + 3, -R + 6, 1, _r(14 * u + 4), _r(2.5 * u + 1), dach="kegel", krone=False, fenster=5)
    return w


def weltkugel(seed, g=2):
    """Weltkugel-Statue: ein riesiger Globus mit Kontinenten aus Grün und Ocker, Meeren aus Blau, eingefasst in
    einen goldenen Meridianring auf einem Bronzesockel."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.2)
    rg = 5 * u + 2
    cy = rg + 5
    rn = Rauschen(w, 3)
    kugel(w, (0, cy, 0), rg, lambda x, y, z: ("white_concrete" if abs(y) > rg * 0.85 else
                                              ("lime_terracotta" if rn(x, y, z) > 0.62 else "green_concrete")
                                              if rn(x + 30, y, z) > 0.5 else "blue_concrete"))
    ring(w, (0, cy, 0), rg + 1.2, 0.4, "gold_block", neig=1.5708)
    for y in range(1, int(cy - rg) + 1):
        for x in range(-1, 2):
            for z in range(-1, 2):
                w.setze(x, y, z, w.b("waxed_cut_copper" if y < cy - rg else "gold_block"))
    for x in range(-3, 4):
        for z in range(-3, 4):
            w.setze(x, 1, z, w.b("waxed_copper_block"))
    return w


def sternbildgarten(seed, g=2):
    """Sternbildgarten: auf einer dunklen Rasenfläche sind die großen Sternbilder mit Leuchtsteinen nachgelegt und
    mit Linien aus Kies verbunden, Bänke laden zum Vergleichen mit dem echten Himmel ein."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.05)
    bilder = [[(0, 0), (2, 1), (4, 1), (6, 0), (7, -2), (9, -1), (8, 1)],
              [(0, 0), (1, 2), (3, 3), (5, 2), (6, 0)],
              [(0, 0), (1, -2), (3, -2), (4, 0), (2, 1), (0, 0)],
              [(0, 0), (2, 0), (2, 2), (4, 3), (6, 2), (7, 4)]]
    rng = w.rng
    for i, pts in enumerate(bilder):
        a = i / len(bilder) * 6.28
        ox, oz = math.cos(a) * R * 0.45 - 4 * u, math.sin(a) * R * 0.45
        s = 1.2 * u
        P_ = [(round(ox + x * s), round(oz + z * s)) for x, z in pts]
        for (ax, az), (bx, bz) in zip(P_, P_[1:]):
            n = max(abs(bx - ax), abs(bz - az), 1)
            for k in range(n + 1):
                w.setze(round(ax + (bx - ax) * k / n), 0, round(az + (bz - az) * k / n), w.b("gravel"))
        for (x, z) in P_:
            w.setze(x, 0, z, w.b("sea_lantern"))
            w.setze(x, 1, z, w.b("white_carpet"))
    for k in range(4):
        a = k * 1.57 + 0.78
        x, z = round(math.cos(a) * R * 0.85), round(math.sin(a) * R * 0.85)
        w.setze(x, 1, z, w.b("spruce_stairs", facing="north", half="bottom", shape="straight", waterlogged=False))
    return w


STERNE = {
    "sternwarte": ("Kuppelsternwarte", sternwarte),
    "riesenteleskop": ("Riesenteleskop", riesenteleskop),
    "radioteleskop": ("Radioteleskop", radioteleskop),
    "antennenfeld": ("Antennenfeld", antennenfeld),
    "planetarium": ("Planetarium", planetarium),
    "sonnenuhr": ("Große Sonnenuhr", sonnenuhr),
    "steinkreis": ("Himmelskalender (Steinkreis)", steinkreis),
    "armillarsphaere": ("Armillarsphäre", armillarsphaere),
    "planetenmodell": ("Planetenmodell", planetenmodell),
    "meteoritenkrater": ("Meteoritenkrater", meteoritenkrater),
    "saturnskulptur": ("Saturn-Skulptur", saturnskulptur),
    "schwarzes_loch": ("Schwarzes Loch", schwarzes_loch),
    "nordlicht": ("Nordlicht-Ausblick", nordlicht),
    "mondlandschaft": ("Mondlandschaft", mondlandschaft),
    "astronomenturm": ("Turm des Astronomen", astronomenturm),
    "caracol": ("Schneckenturm-Observatorium", caracol),
    "samrat_yantra": ("Riesen-Sonnenuhr-Instrument", samrat_yantra),
    "kometenskulptur": ("Kometenskulptur", kometenskulptur),
    "mondphasenpfad": ("Mondphasenpfad", mondphasenpfad),
    "sternschnuppenwiese": ("Sternschnuppenwiese", sternschnuppenwiese),
    "sternenportal": ("Sternenportal", sternenportal),
    "sonnensystempark": ("Sonnensystem-Park", sonnensystempark),
    "astronomenakademie": ("Astronomenakademie", astronomenakademie),
    "weltkugel": ("Weltkugel-Statue", weltkugel),
    "sternbildgarten": ("Sternbildgarten", sternbildgarten),
}

"""Nether-Reich II – zwanzig weitere Bauten aus der Unterwelt: Seelensand-Fossilien, Basaltdelta, Piglin-
Schatzkammer, Schreiter-Anleger, Karmesin-Baumriese, Quarzmine, Ghast-Schwarm, Nether-Felsbogen, Magmawürfel-
Grube, Wither-Wachturm, Piglin-Tauschmarkt, Schrott-Ausgrabung, Lava-Galeere, Weinender Schrein, Pilzlicht-
Gewächshaus, Seelenkerker, Trankbrauerei, Portalknoten, Wirrwurzel-Brücke und Leuchtfeuer-Pyramide."""

from __future__ import annotations

import math

import numpy as np

from feinbau import Dachmat, Mix, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen
from skulptur import Skulptur, dreh_y, ell, kap, kasten, kegel, kreisrand

S = [0.6, 1.0, 1.6, 2.5]

BODEN = {
    "rack": [("netherrack", 5), ("nether_quartz_ore", 1), ("magma_block", 1), ("nether_gold_ore", 1)],
    "seele": [("soul_sand", 3), ("soul_soil", 3), ("bone_block", 0.3)],
    "karmesin": [("crimson_nylium", 4), ("netherrack", 2), ("nether_wart_block", 1)],
    "wirr": [("warped_nylium", 4), ("netherrack", 2), ("warped_wart_block", 1)],
    "basalt": [("basalt", 3), ("blackstone", 2), ("smooth_basalt", 1), ("magma_block", 0.5)],
}


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def ziegel(w):
    return M(w, [("nether_bricks", 4), ("cracked_nether_bricks", 1), ("red_nether_bricks", 1)])


def boden(w, R, art="rack", huegel=0.8, cx=0, cz=0):
    rn = Rauschen(w, 7)
    m = M(w, BODEN[art], zelle=2.2)
    zellen = {}
    for x in range(cx - int(R) - 2, cx + int(R) + 3):
        for z in range(cz - int(R) - 2, cz + int(R) + 3):
            if math.hypot(x - cx, z - cz) <= R + 2 * rn(x, 0, z):
                h = int(huegel * 2 * rn(x * 0.7, 3, z * 0.7))
                for y in range(-2, h + 1):
                    b = m(x, y, z) if y == h else w.b("netherrack")
                    w.setze(x, y, z, b)
                zellen[(x, z)] = h
    return zellen


def lava(w, cx, cz, r, y=0):
    for x in range(int(cx - r) - 2, int(cx + r) + 3):
        for z in range(int(cz - r) - 2, int(cz + r) + 3):
            d = math.hypot(x - cx, z - cz)
            if d <= r:
                w.setze(x, y, z, w.b("lava", level=0))
                w.setze(x, y - 1, z, w.b("magma_block"))
                for yy in range(y + 1, y + 3):
                    w.bloecke.pop((x, yy, z), None)
            elif d <= r + 1.2:
                w.setze(x, y, z, w.b("netherrack" if (x + z) % 3 else "magma_block"))


def oben(w, x, z, bis=40):
    for y in range(bis, -3, -1):
        if not w.frei(x, y, z):
            return y
    return 0


def skulptur(w, u, teile, lo, hi, pos=(0, 0, 0), winkel=0.0):
    Sk = Skulptur(w, u)
    for i, (form, blk) in enumerate(teile):
        if blk is None:
            Sk.minus(form)
            continue
        Sk.mat(str(i), blk)
        Sk.plus(form, str(i))
    Sk.rendern(lo, hi, versatz=(pos[0] + 0.5, pos[1], pos[2] + 0.5), dreh=dreh_y(winkel))


def kasten_haus(w, x0, z0, x1, z1, y0, H, wand, dach="nether_brick", tuer_s="south", fenster="red_stained_glass"):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, y0 - 1, z, w.b("polished_blackstone"))
            for y in range(y0, y0 + H):
                rand = x in (x0, x1) or z in (z0, z1)
                if rand:
                    ecke = x in (x0, x1) and z in (z0, z1)
                    fen = y == y0 + 1 and not ecke and (x + z) % 3 == 0
                    w.setze(x, y, z, w.b(fenster) if fen else wand(x, y, z))
                else:
                    w.bloecke.pop((x, y, z), None)
    first = satteldach(w, x0, z0, x1, z1, y0 + H, Dachmat(w, [dach, "red_nether_brick"]),
                       first_x=(x1 - x0) >= (z1 - z0), ue=1, giebel=wand, traufe="crimson")
    d = {"south": ((x0 + x1) // 2, z1), "north": ((x0 + x1) // 2, z0), "east": (x1, (z0 + z1) // 2),
         "west": (x0, (z0 + z1) // 2)}[tuer_s]
    for y in (y0, y0 + 1):
        w.bloecke.pop((d[0], y, d[1]), None)
    return first


# ============================================================================ Bauten

def seelensand_fossilien(seed, g=2):
    """Seelensand-Fossilien: ein bläulich glimmendes Seelensandtal mit riesigen Rippenbögen und Wirbeln eines
    uralten Wesens, Seelenfeuern zwischen den Knochen und Basaltsäulen am Rand."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = boden(w, R, "seele", 0.6)
    rng = w.rng
    L = R * 1.3
    n = int(4 * s + 3)
    for i in range(n):
        x = round(-L / 2 + (i + 0.5) / n * L)
        rr = (5 * s + 3) * math.sin(math.pi * (i + 0.5) / n) + 2
        for sz in (-1, 1):
            pts = bez((x, 0, 0), (x + 1, rr * 1.4, sz * rr * 0.4), (x + 2, 0, sz * rr * 1.1))
            for px, py, pz, _ in pts:
                w.setze(round(px), round(py), round(pz), w.b("bone_block", axis="y"))
        kugel(w, x, 1, 0, 0.9 + 0.4 * s, w.b("bone_block", axis="x"))
    for _ in range(5 + 3 * g):
        x, z = int((rng.random() - 0.5) * R * 1.6), int((rng.random() - 0.5) * R * 1.6)
        if (x, z) in zellen and w.frei(x, zellen[(x, z)] + 1, z):
            w.setze(x, zellen[(x, z)] + 1, z, w.b("soul_fire"))
            w.setze(x, zellen[(x, z)], z, w.b("soul_soil"))
    for _ in range(3 + 2 * g):
        a = rng.random() * 6.28
        x, z = round(math.cos(a) * R * 0.85), round(math.sin(a) * R * 0.85)
        for y in range(0, int(3 + rng.random() * 8 * s)):
            w.setze(x, y, z, w.b("basalt", axis="y"))
    return w


def basaltdelta(seed, g=2):
    """Basaltdelta: zerklüftete Säulen und Zacken aus Basalt und Schwarzstein, dazwischen Rinnen aus Magma und
    kleine Lavatümpel, über allem ein Bogen aus grauem Basalt."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = boden(w, R, "basalt", 1.0)
    rng = w.rng
    for _ in range(int(25 * s + 12)):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.9
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        H = int(2 + rng.random() ** 2 * 12 * s)
        y0 = zellen.get((x, z), 0)
        for y in range(y0, y0 + H):
            w.setze(x, y, z, w.b("basalt", axis="y") if (y % 5) else w.b("polished_basalt", axis="y"))
            if y < y0 + H // 2:
                for dx, dz in ((1, 0), (0, 1)):
                    if rng.random() < 0.6:
                        w.setze(x + dx, y, z + dz, w.b("basalt", axis="y"))
    for k in range(2 + g):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.5
        lava(w, round(math.cos(a) * d), round(math.sin(a) * d), 1.2 + s)
    pts = bez((-R * 0.6, 0, -R * 0.2), (-R * 0.1, 9 * s + 6, 0), (R * 0.6, 0, R * 0.2))
    rohr(w, pts, 1.8 * s + 0.8, 1.4 * s + 0.6,
         mat=lambda x, y, z, *a: w.b("smooth_basalt") if (x + y) % 4 else w.b("blackstone"), rauh=0.2)
    return w


def schatzkammer(seed, g=2):
    """Piglin-Schatzkammer: ein gedrungener Bau aus Schwarzsteinziegeln mit goldbeschlagenem Tor; durch ein
    offenes Dach sieht man Haufen aus Goldblöcken, Truhen und vergoldeten Schwarzstein auf Podesten."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    boden(w, R, "basalt", 0.3)
    st = M(w, [("polished_blackstone_bricks", 3), ("cracked_polished_blackstone_bricks", 1), ("gilded_blackstone", 1)])
    A = int(5 * s + 5)
    H = int(4 * s + 4)
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            w.setze(x, 0, z, w.b("polished_blackstone"))
            rand = max(abs(x), abs(z)) == A
            for y in range(1, H + 1):
                if rand:
                    w.setze(x, y, z, st(x, y, z))
                else:
                    w.bloecke.pop((x, y, z), None)
            if rand:
                w.setze(x, H + 1, z, w.b("polished_blackstone_bricks") if (x + z) % 2 else w.b("gold_block"))
            elif max(abs(x), abs(z)) == A - 1:
                w.setze(x, H, z, w.b("polished_blackstone_brick_slab", type="top", waterlogged=False))
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in range(1, H + 4):
                for dx in (0, 1):
                    for dz in (0, 1):
                        w.setze(sx * A + dx * -sx, y, sz * A + dz * -sz, w.b("gilded_blackstone" if y % 3 == 0 else
                                                                            "polished_blackstone_bricks"))
    rng = w.rng
    for _ in range(int(6 * s + 4)):
        cx, cz = int((rng.random() - 0.5) * (A - 2) * 2), int((rng.random() - 0.5) * (A - 2) * 2)
        h = 1 + rng.random() * 1.5 * s
        kugel(w, cx, 0, cz, h + 0.5, w.b("gold_block"), ry=h, ueber=False)
    for x, z in ((-A + 2, -A + 2), (A - 2, -A + 2), (0, -A + 2)):
        w.setze(x, 1, z, w.b("chest", facing="south", type="single", waterlogged=False))
    for x in (-1, 0, 1):
        for y in (1, 2, 3):
            w.bloecke.pop((x, y, A), None)
    for y in range(1, 5):
        w.setze(-2, y, A + 1, w.b("gold_block" if y == 4 else "gilded_blackstone"))
        w.setze(2, y, A + 1, w.b("gold_block" if y == 4 else "gilded_blackstone"))
    return w


def schreiter_anleger(seed, g=2):
    """Schreiter-Anleger: ein Steg aus Netherziegeln ragt in einen Lavasee, an Pfählen sind zwei rote
    Schreiter-Figuren mit Sätteln angebunden, daneben ein Kassenhäuschen und Pilzlaternen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    boden(w, R, "rack", 0.3)
    lava(w, 0, int(R * 0.3), R * 0.55)
    zg = ziegel(w)
    for z in range(-int(R * 0.4), int(R * 0.55)):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, zg(x, 1, z) if x == 0 or z % 2 else w.b("nether_brick_slab", type="bottom",
                                                                         waterlogged=False))
        if z % 4 == 0:
            for x in (-2, 2):
                for y in range(0, 4):
                    w.setze(x, y, z, w.b("nether_brick_fence", waterlogged=False))
                w.setze(x, 4, z, w.b("shroomlight"))
    rot = w.b("red_concrete")
    dk = w.b("red_nether_bricks")
    sa = w.b("brown_wool")
    for k, sx in enumerate((-1, 1)):
        teile = [(ell(0, 6, 0, 1.6, 1.4, 1.4), rot), (ell(0, 7.2, 0, 1.1, 0.4, 1.1), sa)] + \
                [(kap((0, 5, sz), (0.4, 0, sz * 1.4), 0.35), dk) for sz in (-0.8, 0.8)] + \
                [(kap((-1.2, 6.3, 0), (-1.6, 7.5, 0), 0.15), w.b("white_concrete")),
                 (kap((1.2, 6.3, 0), (1.6, 7.5, 0), 0.15), w.b("white_concrete"))]
        skulptur(w, 0.55 * s + 0.35, teile, (-3, -1, -3), (3, 9, 3), pos=(sx * 4, 0, int(R * 0.35) + k * 2),
                 winkel=0.3 * sx)
    hx, hz = -int(R * 0.45), -int(R * 0.45)
    kasten_haus(w, hx - 2, hz - 2, hx + 2, hz + 2, 1, 3, zg, tuer_s="east")
    return w


def karmesinriese(seed, g=2):
    """Karmesin-Baumriese: ein riesiger Karmesinpilz mit knorrigem Stamm, mehrstöckigem Hut aus Warzenblöcken,
    leuchtenden Pilzlichtern und herabhängenden Trauerranken über einem Karmesin-Nyzelboden."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = boden(w, R, "karmesin", 0.5)
    H = int(16 * s + 8)
    pts = bez((0, 0, 0), (1.5 * s, H * 0.5, -s), (-s, H, s))
    rohr(w, pts, 2.0 * s + 1.0, 0.9 * s + 0.6, mat=lambda x, y, z, *a: w.b("crimson_hyphae", axis="y") if
         (x + z) % 3 else w.b("crimson_stem", axis="y"), rauh=0.15)
    for k in range(5):
        a = k / 5 * 2 * math.pi
        rohr(w, bez((0, 1, 0), (math.cos(a) * 3 * s, 0, math.sin(a) * 3 * s),
                    (math.cos(a) * 5 * s, -1, math.sin(a) * 5 * s)), 0.9 * s + 0.4, 0.4,
             mat=w.b("crimson_hyphae", axis="y"))
    hx, hz = round(-s), round(s)
    rng = w.rng
    for stufe, (yy, r) in enumerate(((H, 9 * s + 4), (H + 3 * s + 2, 6 * s + 3), (H + 6 * s + 3, 3 * s + 2))):
        for x in range(int(hx - r) - 1, int(hx + r) + 2):
            for z in range(int(hz - r) - 1, int(hz + r) + 2):
                d = math.hypot(x - hx, z - hz)
                if d <= r:
                    dy = int((1 - (d / r) ** 2) * 2.5 * s)
                    for y in range(round(yy) + dy - 1, round(yy) + dy + 1):
                        w.setze(x, y, z, w.b("shroomlight") if rng.random() < 0.06 else w.b("nether_wart_block"))
                    if d > r - 1.3 and rng.random() < 0.4:
                        L = int(1 + rng.random() * 5 * s)
                        for k in range(1, L):
                            w.setze(x, round(yy) + dy - 1 - k, z, w.b("weeping_vines_plant"), False)
                        w.setze(x, round(yy) + dy - 1 - L, z, w.b("weeping_vines", age=20), False)
    for _ in range(int(14 * s + 6)):
        x, z = int((rng.random() - 0.5) * R * 1.7), int((rng.random() - 0.5) * R * 1.7)
        if (x, z) in zellen and w.frei(x, zellen[(x, z)] + 1, z):
            w.setze(x, zellen[(x, z)] + 1, z, w.b("crimson_roots" if rng.random() < 0.6 else "crimson_fungus"))
    return w


def quarzmine(seed, g=2):
    """Quarzmine: ein Netherrack-Hügel mit Stolleneingang aus Holzbalken, freigelegte Quarz- und Goldadern,
    Schienen mit Loren voll Quarz und ein Förderturm aus Netherziegeln mit Seilrad."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = boden(w, R, "rack", 0.4)
    rn = Rauschen(w, 3)
    hz = -int(R * 0.3)
    Rh = R * 0.7
    H = 8 * s + 5
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, (z - hz) * 1.3)
            if d < Rh:
                h = int(H * (1 - (d / Rh) ** 2) + rn(x, 0, z) * 2)
                for y in range(1, h + 1):
                    v = rn(x * 2, y * 2, z * 2)
                    w.setze(x, y, z, w.b("nether_quartz_ore" if v > 0.72 else "nether_gold_ore" if v < 0.12 else
                                         "netherrack"))
    ez = hz + int(Rh / 1.3)
    for z in range(hz, ez + 2):
        for x in (-2, -1, 0, 1, 2):
            for y in range(1, 5):
                if abs(x) < 2 and y < 4:
                    w.bloecke.pop((x, y, z), None)
        if (z - hz) % 3 == 0:
            for y in range(1, 4):
                w.setze(-2, y, z, w.b("crimson_stem", axis="y"))
                w.setze(2, y, z, w.b("crimson_stem", axis="y"))
            for x in range(-2, 3):
                w.setze(x, 4, z, w.b("crimson_stem", axis="x"))
        w.setze(0, 1, z, w.b("rail", shape="north_south", waterlogged=False))
    for z in range(ez + 2, R - 1):
        w.setze(0, zellen.get((0, z), 0) + 1, z, w.b("rail", shape="north_south", waterlogged=False))
    w.setze(1, 1, ez + 4, w.b("quartz_block"))
    w.setze(1, 2, ez + 4, w.b("nether_quartz_ore"))
    tx, tz = int(R * 0.45), int(R * 0.35)
    zg = ziegel(w)
    th = int(8 * s + 6)
    for y in range(1, th):
        for dx in (-1, 1):
            for dz in (-1, 1):
                w.setze(tx + dx, y, tz + dz, w.b("nether_brick_fence", waterlogged=False) if y % 3 else zg(tx, y, tz))
    for dz in range(-2, 3):
        for dy in range(-2, 3):
            if abs(math.hypot(dz, dy) - 2) < 0.6:
                w.setze(tx, th + dy, tz + dz, w.b("crimson_planks"))
    w.setze(tx, th, tz, w.b("crimson_stem", axis="x"))
    for y in range(1, th - 2):
        w.setze(tx, y, tz, w.b("chain", axis="y", waterlogged=False))
    return w


def ghast(w, u):
    we = w.b("white_concrete")
    gr = w.b("light_gray_concrete")
    sch = w.b("black_concrete")
    teile = [(kasten(-2, 2, -2, 2, 6, 2), we), (kasten(-1.6, 3.6, 1.9, -0.6, 4.4, 2.2), sch),
             (kasten(0.6, 3.6, 1.9, 1.6, 4.4, 2.2), sch), (kasten(-0.6, 2.6, 1.9, 0.6, 3.0, 2.2), sch)]
    for i, (tx, tz) in enumerate(((-1.4, -1.4), (0, -1.4), (1.4, -1.4), (-1.4, 0.2), (1.4, 0.2), (-0.7, 1.4),
                                  (0.7, 1.4), (0, 0))):
        teile.append((kasten(tx - 0.3, 2 - (2.5 + (i % 3)), tz - 0.3, tx + 0.3, 2, tz + 0.3), gr))
    return teile


def ghastschwarm(seed, g=2):
    """Ghast-Schwarm: drei große, weiße Ghasts mit hängenden Tentakeln schweben über zackigen Netherrack-
    Spitzen, in denen Feuer brennt; einer von ihnen hat das Maul geöffnet."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = boden(w, R, "rack", 0.6)
    rng = w.rng
    for _ in range(int(6 * s + 4)):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.85
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        h = int((3 + rng.random() * 8) * s)
        for y in range(1, h):
            r = 1.8 * s * (1 - y / h) + 0.4
            for dx in range(-3, 4):
                for dz in range(-3, 4):
                    if dx * dx + dz * dz <= r * r:
                        w.setze(x + dx, y, z + dz, w.b("netherrack" if (y + dx) % 5 else "magma_block"))
        w.setze(x, h, z, w.b("fire", age=0, north=False, south=False, east=False, west=False, up=False))
    for k, (gx, gy, gz) in enumerate(((0, 14, 0), (-0.5, 10, 0.5), (0.5, 12, -0.4))):
        u = (1.2 if k == 0 else 0.8) * s + 0.4
        skulptur(w, u, ghast(w, u), (-3, -5, -3), (3, 7, 3),
                 pos=(round(gx * R), round(gy * s + 4), round(gz * R)), winkel=rng.random() * 6.28)
    _ = zellen
    return w


def felsbogen(seed, g=2):
    """Nether-Felsbogen: ein wilder Doppelbogen aus Netherrack mit Quarz- und Goldadern über einem Lavafluss,
    behangen mit Trauerranken und mit Leuchtsteinclustern an der Unterseite."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    boden(w, R, "rack", 0.4)
    for x in range(-R, R + 1):
        for dz in range(-int(1 + s), int(2 + s)):
            z = dz + round(math.sin(x / 5) * 2)
            if math.hypot(x, z) < R:
                w.setze(x, 0, z, w.b("lava", level=0))
                w.setze(x, -1, z, w.b("magma_block"))
    rn = Rauschen(w, 2)

    def mat(x, y, z, *a):
        v = rn(x, y, z)
        return w.b("nether_quartz_ore" if v > 0.75 else "nether_gold_ore" if v < 0.15 else "netherrack")
    for k, (a, b, hoch) in enumerate((((-R * 0.7, -R * 0.4), (R * 0.2, R * 0.3), 13), ((-R * 0.1, R * 0.5),
                                                                                       (R * 0.7, -R * 0.2), 9))):
        pts = bez((a[0], -1, a[1]), ((a[0] + b[0]) / 2, 2 * hoch * s + 10, (a[1] + b[1]) / 2), (b[0], -1, b[1]))
        rohr(w, pts, (1.6 - 0.4 * k) * s + 1, (1.3 - 0.3 * k) * s + 0.8, mat=mat, rauh=0.2)
    rng = w.rng
    for (x, y, z), bl in list(w.bloecke.items()):
        if y > 3 and w.frei(x, y - 1, z) and rng.random() < 0.06:
            if rng.random() < 0.5:
                w.setze(x, y - 1, z, w.b("glowstone"))
            else:
                L = int(1 + rng.random() * 5)
                for k in range(1, L):
                    if w.frei(x, y - k, z):
                        w.setze(x, y - k, z, w.b("weeping_vines_plant"))
                w.setze(x, y - L, z, w.b("weeping_vines", age=20), False)
    return w


def magmawuerfel(seed, g=1):
    """Magmawürfel-Grube: eine runde Grube aus Schwarzstein, in der große und kleine Magmawürfel-Figuren mit
    glühenden Augen übereinander hüpfen, umgeben von einem Geländer aus Netherziegelzaun."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    boden(w, R, "basalt", 0.2)
    rg = R * 0.6
    for x in range(-int(rg) - 2, int(rg) + 3):
        for z in range(-int(rg) - 2, int(rg) + 3):
            d = math.hypot(x, z)
            if d <= rg:
                for y in range(-3, 2):
                    w.bloecke.pop((x, y, z), None)
                w.setze(x, -4, z, w.b("magma_block" if (x + z) % 3 else "blackstone"))
            elif d <= rg + 1.2:
                for y in range(-4, 1):
                    w.setze(x, y, z, w.b("polished_blackstone_bricks"))
                w.setze(x, 1, z, w.b("nether_brick_fence", waterlogged=False))
    rng = w.rng
    for k in range(4 + 2 * g):
        gr = (1.5 + rng.random() * 2.5) * s * 0.6 + 0.8
        a = rng.random() * 6.28
        d = rng.random() * (rg - gr - 1)
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        y0 = -3 + int(rng.random() * 4 * s)
        n = int(gr)
        for x in range(-n, n + 1):
            for z in range(-n, n + 1):
                for y in range(0, 2 * n + 1):
                    rand = max(abs(x), abs(z)) == n or y in (0, 2 * n)
                    if rand:
                        w.setze(cx + x, y0 + y, cz + z, w.b("magma_block") if (x + y + z) % 3 else
                                w.b("red_nether_bricks"))
        for sx in (-1, 1):
            w.setze(cx + sx * max(1, n // 2), y0 + n + 1, cz + n, w.b("shroomlight"))
    return w


def witherwachturm(seed, g=2):
    """Wither-Wachturm: ein hoher, quadratischer Turm aus Netherziegeln mit auskragender Plattform und
    Zinnen, an der Spitze zwei dunkle Wither-Skelett-Statuen mit Steinschwertern und Seelenfeuer-Becken."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    boden(w, R, "seele", 0.4)
    zg = ziegel(w)
    A = int(2 * s + 2)
    H = int(18 * s + 10)
    for y in range(1, H):
        for x in range(-A, A + 1):
            for z in range(-A, A + 1):
                if max(abs(x), abs(z)) == A:
                    fen = y % 6 == 3 and (x == 0 or z == 0)
                    w.setze(x, y, z, w.b("nether_brick_fence", waterlogged=False) if fen else zg(x, y, z))
    P = A + 2
    for x in range(-P, P + 1):
        for z in range(-P, P + 1):
            w.setze(x, H, z, w.b("red_nether_bricks"))
            if max(abs(x), abs(z)) == P:
                w.setze(x, H + 1, z, w.b("nether_brick_fence", waterlogged=False) if (x + z) % 2 else zg(x, H, z))
    for k in range(1, 3):
        for x in range(-A - k, A + k + 1):
            for z in range(-A - k, A + k + 1):
                if max(abs(x), abs(z)) == A + k:
                    w.setze(x, H - 3 + k, z, w.b("nether_brick_stairs", facing="north", half="top", shape="straight",
                                                 waterlogged=False) if False else w.b("nether_bricks"))
    sch = w.b("black_concrete")
    dk = w.b("gray_concrete")
    st = w.b("cobblestone")
    for sx in (-1, 1):
        teile = [(kasten(-0.5, 5.2, -0.5, 0.5, 6.4, 0.5), sch), (kasten(-0.9, 2.4, -0.35, 0.9, 5.2, 0.35), sch),
                 (kap((-0.5, 2.4, 0), (-0.5, 0, 0), 0.3), sch), (kap((0.5, 2.4, 0), (0.5, 0, 0), 0.3), sch),
                 (kap((-1.2, 5.0, 0), (-1.3, 3.0, 0.6), 0.28), sch), (kap((1.2, 5.0, 0), (1.3, 3.0, 0.6), 0.28), sch),
                 (kasten(1.15, 2.6, 0.5, 1.45, 6.2, 0.8), st), (kasten(-0.3, 5.7, 0.45, -0.1, 5.9, 0.6), dk),
                 (kasten(0.1, 5.7, 0.45, 0.3, 5.9, 0.6), dk)]
        skulptur(w, 0.6 * s + 0.4, teile, (-2, -1, -2), (2, 8, 2), pos=(sx * (A + 1), H + 1, 0),
                 winkel=0.0 if sx > 0 else math.pi)
    for x, z in ((-P + 1, -P + 1), (P - 1, P - 1)):
        w.setze(x, H + 1, z, w.b("soul_soil"))
        w.setze(x, H + 2, z, w.b("soul_fire"))
    for y in (1, 2):
        w.bloecke.pop((0, y, A), None)
    return w


def tauschmarkt(seed, g=2):
    """Piglin-Tauschmarkt: Marktstände aus Karmesin- und Wirrholz mit Markisen aus roter und schwarzer Wolle,
    Goldbarren-Stapel, Fässer, Kisten und ein Platz mit einem Goldbrunnen in der Mitte."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    boden(w, R, "rack", 0.1)
    for x in range(-R + 2, R - 1):
        for z in range(-R + 2, R - 1):
            if math.hypot(x, z) < R * 0.75:
                w.setze(x, 0, z, w.b("polished_blackstone_bricks" if (x + z) % 3 else "blackstone"))
    n = 5 + 2 * g
    rng = w.rng
    for i in range(n):
        a = i / n * 2 * math.pi
        cx, cz = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        holz = "crimson" if i % 2 else "warped"
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                w.setze(cx + dx, 1, cz + dz, w.b(f"{holz}_planks") if abs(dx) + abs(dz) < 2 else w.b("air"))
        for dx in (-2, 2):
            for dz in (-2, 2):
                for y in range(1, 4):
                    w.setze(cx + dx, y, cz + dz, w.b(f"{holz}_fence", waterlogged=False))
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                w.setze(cx + dx, 4, cz + dz, w.b(["red_wool", "black_wool"][(dx + dz + 10) % 2]))
        ware = ["gold_block", "barrel", "raw_gold_block", "chest", "crying_obsidian", "glowstone"][i % 6]
        pr = {"barrel": dict(facing="up", open=False), "chest": dict(facing="south", type="single",
                                                                      waterlogged=False)}.get(ware, {})
        w.setze(cx, 2, cz, w.b(ware, **pr))
    for x in range(-2, 3):
        for z in range(-2, 3):
            if math.hypot(x, z) <= 2.3:
                w.setze(x, 1, z, w.b("gilded_blackstone") if math.hypot(x, z) > 1.3 else w.b("lava", level=0))
    for y in range(2, int(3 * s + 3)):
        w.setze(0, y + 1, 0, w.b("gold_block"))
    _ = rng
    return w


def ausgrabung(seed, g=2):
    """Schrott-Ausgrabung: eine tiefe, gestufte Grube im Netherrack, an deren Grund Brocken antiken Schrotts
    freigelegt sind; Gerüste, Leitern, Lampen und ein Seilkran führen hinab."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    boden(w, R, "rack", 0.3)
    T = int(5 * s + 4)
    stufen = 3 + g
    for k in range(stufen):
        r = R * 0.7 - k * (R * 0.5 / stufen)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                if math.hypot(x, z) <= r:
                    for y in range(-k * 2 - 2, 2):
                        w.bloecke.pop((x, y, z), None)
                    w.setze(x, -k * 2 - 3, z, w.b("netherrack"))
    yb = -(stufen - 1) * 2 - 3
    rng = w.rng
    for _ in range(int(5 * s + 3)):
        x, z = int((rng.random() - 0.5) * R * 0.4), int((rng.random() - 0.5) * R * 0.4)
        w.setze(x, yb + 1, z, w.b("ancient_debris"))
        if rng.random() < 0.4:
            w.setze(x, yb + 2, z, w.b("ancient_debris"))
    for k in range(stufen):
        x = round(R * 0.7 - k * (R * 0.5 / stufen)) - 1
        for y in range(-k * 2 - 2, 2):
            w.setze(x, y, 0, w.b("scaffolding", distance=0, bottom=False, waterlogged=False))
    for z in range(-2, 3):
        for y in range(yb + 1, 2):
            if z in (-2, 2) and y % 3 == 0:
                w.setze(-round(R * 0.2), y, z, w.b("crimson_planks"))
    kx = -round(R * 0.75)
    for y in range(1, T + 6):
        w.setze(kx, y, 0, w.b("crimson_stem", axis="y"))
    for k in range(int(R * 0.6)):
        w.setze(kx + k, T + 5, 0, w.b("crimson_stem", axis="x"))
    for y in range(yb + 3, T + 5):
        w.setze(kx + int(R * 0.6) - 1, y, 0, w.b("chain", axis="y", waterlogged=False))
    w.setze(kx + int(R * 0.6) - 1, yb + 2, 0, w.b("ancient_debris"))
    for a in range(6):
        aa = a / 6 * 2 * math.pi
        x, z = round(math.cos(aa) * R * 0.78), round(math.sin(aa) * R * 0.78)
        w.setze(x, 1, z, w.b("crimson_fence", waterlogged=False))
        w.setze(x, 2, z, w.b("lantern", hanging=False, waterlogged=False))
    return w


def lavagaleere(seed, g=2):
    """Lava-Galeere: ein dunkles Schiff aus Netherziegeln und Karmesinholz gleitet über einen Lavasee, mit
    Ruderreihen, einem Segel aus roter Wolle mit Totenkopf und einer Pilzlicht-Laterne am Bug."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    boden(w, R, "rack", 0.2)
    lava(w, 0, 0, R * 0.8)
    L = 9 * s + 6
    B = 2.2 * s + 1.5
    D = int(1.5 * s + 1)
    for x in range(-int(L), int(L) + 1):
        t = x / L
        bw = B * math.sqrt(max(0, 1 - t ** 4)) if t > -0.85 else B * 0.8
        for z in range(-int(bw) - 1, int(bw) + 2):
            if abs(z) <= bw:
                for y in range(-D + (1 if abs(z) > bw - 1 else 0), 2):
                    rand = abs(z) > bw - 1 or y == -D
                    if rand:
                        w.setze(x, y, z, w.b("nether_bricks" if y < 1 else "red_nether_bricks"))
                    else:
                        w.bloecke.pop((x, y, z), None)
                w.setze(x, 1, z, w.b("crimson_planks") if abs(z) < bw - 0.5 else w.b("red_nether_bricks"))
                if abs(z) > bw - 1:
                    w.setze(x, 2, z, w.b("nether_brick_fence", waterlogged=False))
        if x % 2 == 0 and abs(t) < 0.7:
            for sz in (-1, 1):
                for k in range(1, int(2 + s)):
                    w.setze(x - k // 2, 0 - k // 2, sz * (round(bw) + k), w.b("crimson_fence", waterlogged=False))
    for k in range(int(3 * s + 2)):
        w.setze(int(L) + k, 2 + k // 2, 0, w.b("red_nether_bricks"))
    w.setze(int(L) + int(3 * s + 2), 3 + int(3 * s + 2) // 2, 0, w.b("shroomlight"))
    for y in range(-int(L * 0.4), int(L * 0.4)):
        pass
    hm = int(10 * s + 6)
    for y in range(2, hm):
        w.setze(0, y, 0, w.b("crimson_stem", axis="y"))
    sb = int(4 * s + 3)
    for y in range(4, hm - 1):
        for z in range(-sb, sb + 1):
            bauch = round(1.2 * math.sin(math.pi * (y - 4) / (hm - 5)))
            schaedel = abs(z) <= 1 and abs(y - (hm + 4) // 2) <= 1
            w.setze(1 + bauch, y, z, w.b("white_wool" if schaedel else "red_wool"))
    for z in range(-sb - 1, sb + 2):
        w.setze(0, hm - 1, z, w.b("crimson_stem", axis="z"))
    for x in range(-int(L) + 1, -int(L) + 4):
        for z in (-1, 0, 1):
            for y in (2, 3):
                w.setze(x, y, z, w.b("red_nether_bricks") if y == 3 or abs(z) == 1 else w.b("air"))
    return w


def weinschrein(seed, g=2):
    """Weinender Schrein: ein Ring aus Säulen aus weinendem Obsidian mit Kuppelbögen aus Schwarzstein um einen
    Seelen-Anker-Altar; violette Tränen-Lichter und Amethyst-Splitter umgeben ihn."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    boden(w, R, "seele", 0.3)
    rr = 4 * s + 3
    n = 8
    H = int(4 * s + 4)
    for i in range(n):
        a = i / n * 2 * math.pi
        x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b("crying_obsidian" if y % 3 else "obsidian"))
        a2 = (i + 1) / n * 2 * math.pi
        for k in range(9):
            t = k / 8
            aa = a + (a2 - a) * t
            yy = H + round(math.sin(math.pi * t) * 1.5 * s)
            w.setze(round(math.cos(aa) * rr), yy, round(math.sin(aa) * rr), w.b("polished_blackstone_bricks"))
    for x in range(-int(rr), int(rr) + 1):
        for z in range(-int(rr), int(rr) + 1):
            if math.hypot(x, z) < rr - 0.5:
                w.setze(x, 0, z, w.b("polished_blackstone" if (x + z) % 2 else "obsidian"))
    for k in range(3):
        for x in range(-2 + k, 3 - k):
            for z in range(-2 + k, 3 - k):
                w.setze(x, 1 + k, z, w.b("polished_blackstone_bricks"))
    w.setze(0, 4, 0, w.b("respawn_anchor", charges=4))
    rng = w.rng
    for _ in range(int(8 * s + 4)):
        a = rng.random() * 6.28
        d = rr + 2 + rng.random() * (R - rr - 3)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = oben(w, x, z, 6) + 1
        w.setze(x, y, z, w.b("amethyst_cluster", facing="up", waterlogged=False) if rng.random() < 0.6 else
                w.b("crying_obsidian"))
    return w


def gewaechshaus(seed, g=2):
    """Pilzlicht-Gewächshaus: ein Glashaus mit Rahmen aus Wirrholz, darin Beete mit Karmesin- und Wirrpilzen,
    Netherwarzen auf Seelensand, hängende Pilzlichter und ein Wasserbecken mit Seelenlaternen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    boden(w, R, "wirr", 0.2)
    B, T = int(5 * s + 5), int(8 * s + 6)
    H = int(4 * s + 4)
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            rand = abs(x) == B or abs(z) == T
            w.setze(x, 0, z, w.b("warped_planks") if abs(x) <= 1 else w.b("soul_sand") if x % 3 == 0 else
                    w.b("crimson_nylium") if x < 0 else w.b("warped_nylium"))
            for y in range(1, H + 1):
                if rand:
                    rahmen = y == H or (x + z) % 4 == 0 or (abs(x) == B and abs(z) == T)
                    w.setze(x, y, z, w.b("warped_stem", axis="y") if rahmen else w.b("glass"))
                else:
                    w.bloecke.pop((x, y, z), None)
            if not rand and abs(x) > 1:
                if x % 3 == 0:
                    w.setze(x, 1, z, w.b("nether_wart", age=3))
                elif (x + z) % 2:
                    w.setze(x, 1, z, w.b("crimson_fungus" if x < 0 else "warped_fungus"))
    for k in range(B + 1):
        for z in range(-T, T + 1):
            for sx in (-1, 1):
                x = sx * (B - k)
                w.setze(x, H + 1 + k // 2, z, w.b("glass") if z % 4 else w.b("warped_stem", axis="x"))
    for z in range(-T + 2, T - 1, 4):
        laterne(w, 0, H + B // 2, z, kette=2)
        w.setze(0, H + B // 2 - 2, z, w.b("shroomlight"))
    for y in (1, 2):
        w.bloecke.pop((0, y, T), None)
    return w


def seelenkerker(seed, g=2):
    """Seelenkerker: ein runder Kerkerhof aus Schwarzstein mit Käfigen aus Eisengittern an Ketten, in denen
    Seelenfeuer flackern, ein Wachturm mit Seelenlaterne und ein vergittertes Tor."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    boden(w, R, "seele", 0.3)
    rh = R * 0.65
    H = int(4 * s + 3)
    for x, z in kreisrand(rh):
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b("polished_blackstone_bricks" if y < H else "blackstone"))
        if (x + z) % 2 == 0:
            w.setze(x, H + 1, z, w.b("polished_blackstone_wall"))
    for x in (-1, 0, 1):
        for y in range(1, 4):
            w.setze(x, y, round(rh), w.b("iron_bars", waterlogged=False))
    rng = w.rng
    n = 4 + g
    for i in range(n):
        a = i / n * 2 * math.pi
        cx, cz = round(math.cos(a) * rh * 0.55), round(math.sin(a) * rh * 0.55)
        yk = int(3 + rng.random() * 3 * s)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for y in range(yk, yk + 4):
                    if abs(dx) == 1 or abs(dz) == 1:
                        w.setze(cx + dx, y, cz + dz, w.b("iron_bars", waterlogged=False))
                w.setze(cx + dx, yk - 1, cz + dz, w.b("polished_blackstone"))
                w.setze(cx + dx, yk + 4, cz + dz, w.b("polished_blackstone"))
        w.setze(cx, yk, cz, w.b("soul_soil"))
        w.setze(cx, yk + 1, cz, w.b("soul_fire"))
        for y in range(yk + 5, int(H + 8 * s + 4)):
            w.setze(cx, y, cz, w.b("chain", axis="y", waterlogged=False))
        w.setze(cx, int(H + 8 * s + 4), cz, w.b("polished_blackstone_bricks"))
    th = int(10 * s + 7)
    for y in range(1, th):
        for x, z in kreisrand(1.8 + 0.4 * s):
            w.setze(x, y, z, w.b("polished_blackstone_bricks"))
    for x in range(-3, 4):
        for z in range(-3, 4):
            w.setze(x, th, z, w.b("polished_blackstone"))
    w.setze(0, th + 1, 0, w.b("soul_lantern", hanging=False, waterlogged=False))
    for i in range(n):
        a = i / n * 2 * math.pi
        cx, cz = round(math.cos(a) * rh * 0.55), round(math.sin(a) * rh * 0.55)
        for k in range(1, 10):
            t = k / 10
            w.setze(round(cx * (1 - t)), round(int(H + 8 * s + 4) * (1 - t) + th * t), round(cz * (1 - t)),
                    w.b("chain", axis="y", waterlogged=False), False)
    return w


def brauerei(seed, g=1):
    """Trankbrauerei: eine Werkstatt aus Netherziegeln mit Braustand-Tischen, Kesseln, Regalen voller Flaschen
    (Glasblöcke), einem Netherwarzen-Beet im Hinterhof und einem rauchenden Schlot."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    boden(w, R, "rack", 0.2)
    zg = ziegel(w)
    B, T = int(4 * s + 5), int(3 * s + 4)
    first = kasten_haus(w, -B, -T, B, T, 1, int(2 * s + 4), zg, tuer_s="south")
    for x in range(-B + 2, B - 1, 3):
        w.setze(x, 1, -T + 1, w.b("brewing_stand", has_bottle_0=True, has_bottle_1=False, has_bottle_2=True))
        w.setze(x + 1, 1, -T + 1, w.b("water_cauldron", level=3))
    for x in range(-B + 1, B):
        if x % 2:
            w.setze(x, 2, T - 1, w.b("bookshelf"))
    for z in range(T + 2, T + 2 + int(3 * s + 3)):
        for x in range(-B, B + 1):
            w.setze(x, 0, z, w.b("soul_sand"))
            w.setze(x, 1, z, w.b("nether_wart", age=3) if (x + z) % 4 else w.b("air"))
        w.setze(-B - 1, 1, z, w.b("nether_brick_fence", waterlogged=False))
        w.setze(B + 1, 1, z, w.b("nether_brick_fence", waterlogged=False))
    for y in range(1, (first or 8) + 4):
        w.setze(B - 1, y, -T - 1, zg(B, y, -T))
    w.setze(B - 1, (first or 8) + 4, -T - 1, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                     waterlogged=False))
    return w


def portalknoten(seed, g=2):
    """Portalknoten: ein runder Platz aus Schwarzstein mit vier leuchtenden Netherportalen in Rahmen aus
    Obsidian und weinendem Obsidian, Wegweiser-Säulen und eine Laternenspitze in der Mitte."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    boden(w, R, "rack", 0.2)
    rp = R * 0.6
    for x in range(-int(rp) - 1, int(rp) + 2):
        for z in range(-int(rp) - 1, int(rp) + 2):
            if math.hypot(x, z) <= rp:
                w.setze(x, 0, z, w.b("polished_blackstone" if (x + z) % 2 else "polished_blackstone_bricks"))
    PB = int(1.5 * s + 2)
    PH = int(2.5 * s + 3)
    for i in range(4):
        a = i * math.pi / 2
        cx, cz = round(math.cos(a) * rp * 0.75), round(math.sin(a) * rp * 0.75)
        ax = "z" if i % 2 == 0 else "x"
        for k in range(-PB - 1, PB + 2):
            for y in range(1, PH + 3):
                x = cx if ax == "z" else cx + k
                z = cz + k if ax == "z" else cz
                rand = abs(k) == PB + 1 or y in (1, PH + 2)
                if rand:
                    w.setze(x, y, z, w.b("crying_obsidian" if (k + y) % 4 == 0 else "obsidian"))
                else:
                    w.setze(x, y, z, w.b("nether_portal", axis="z" if ax == "z" else "x"))
    for y in range(1, int(5 * s + 5)):
        w.setze(0, y, 0, w.b("polished_blackstone_bricks") if y % 3 else w.b("gilded_blackstone"))
    w.setze(0, int(5 * s + 5), 0, w.b("lantern", hanging=False, waterlogged=False))
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        x, z = round(math.cos(a) * rp * 0.45), round(math.sin(a) * rp * 0.45)
        for y in range(1, 4):
            w.setze(x, y, z, w.b("crimson_fence", waterlogged=False))
        w.setze(x, 3, z + 1, w.b("crimson_planks"))
        w.setze(x + 1, 2, z, w.b("warped_planks"))
    return w


def wurzelbruecke(seed, g=2):
    """Wirrwurzel-Brücke: dicke, ineinander verflochtene Wirrstiele wachsen von beiden Ufern über eine Lava-
    schlucht und bilden einen begehbaren Bogen, behangen mit Zwirbelranken und Wirrwarzen-Knoten."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    rn = Rauschen(w, 5)
    H = int(6 * s + 4)
    breit = R * 0.35
    for x in range(-R - 1, R + 2):
        for z in range(-R - 1, R + 2):
            if math.hypot(x, z) > R + rn(x, 0, z) * 2:
                continue
            if abs(x) < breit:
                w.setze(x, -2, z, w.b("lava", level=0))
                w.setze(x, -3, z, w.b("magma_block"))
                continue
            for y in range(-3, H + int(rn(x, 3, z) * 3) + 1):
                w.setze(x, y, z, w.b("warped_nylium") if y == H + int(rn(x, 3, z) * 3) else w.b("netherrack"))
    for k, dz in enumerate((-1.2 * s, 0, 1.2 * s)):
        pts = bez((-breit - 3, H, dz), (-breit * 0.3, H + 6 * s + (k % 2) * 2, dz * 2.5),
                  (breit * 0.3, H + 6 * s - (k % 2) * 2, -dz * 1.5), (breit + 3, H, dz))
        rohr(w, pts, 0.9 * s + 0.6, 0.9 * s + 0.6, mat=w.b("warped_hyphae", axis="y"), rauh=0.1)
    yb = [p for p in bez((-breit - 3, H + 1, 0), (-breit * 0.3, H + 6 * s + 1.5, 0), (breit * 0.3, H + 6 * s + 1.5, 0),
                         (breit + 3, H + 1, 0))]
    for x, y, z, _ in yb:
        for dz in (-1, 0, 1):
            w.setze(round(x), round(y), round(z + dz), w.b("warped_planks"))
            w.bloecke.pop((round(x), round(y) + 1, round(z + dz)), None)
            w.bloecke.pop((round(x), round(y) + 2, round(z + dz)), None)
    rng = w.rng
    for (x, y, z), bl in list(w.bloecke.items()):
        if abs(x) < breit and y > H and w.frei(x, y - 1, z) and rng.random() < 0.08:
            L = int(1 + rng.random() * 4 * s)
            for k in range(1, L):
                if w.frei(x, y - k, z):
                    w.setze(x, y - k, z, w.b("twisting_vines_plant"))
            if rng.random() < 0.3:
                w.setze(x, y - 1, z, w.b("warped_wart_block"))
    return w


def leuchtfeuer_pyramide(seed, g=2):
    """Leuchtfeuer-Pyramide: eine gestufte Pyramide aus Gold-, Eisen- und Netheritblöcken auf einer Plattform aus
    Schwarzstein, auf deren Spitze ein Leuchtfeuer strahlt, bewacht von vier vergoldeten Piglin-Statuen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    boden(w, R, "basalt", 0.2)
    stufen = int(3 * s + 3)
    for k in range(stufen):
        a = stufen - k + 1
        mat = ["netherite_block", "gold_block", "iron_block", "gold_block", "netherite_block", "gold_block"][k % 6]
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                w.setze(x, 1 + k, z, w.b(mat))
    for x in range(-stufen - 3, stufen + 4):
        for z in range(-stufen - 3, stufen + 4):
            w.setze(x, 0, z, w.b("polished_blackstone_bricks"))
    w.setze(0, stufen + 1, 0, w.b("beacon"))
    gold = w.b("gold_block")
    rosa = w.b("pink_terracotta")
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        x, z = round(math.cos(a) * (stufen + 4)), round(math.sin(a) * (stufen + 4))
        teile = [(kasten(-1, 4, -0.8, 1, 7.5, 0.8), gold), (kasten(-1.2, 7.5, -1.0, 1.2, 9.5, 1.0), rosa),
                 (kasten(-0.6, 7.6, 0.9, 0.6, 8.4, 1.4), rosa), (kasten(-1.3, 9.2, -1.1, 1.3, 9.7, 1.1), gold),
                 (kasten(-1, 0, -0.6, -0.1, 4, 0.6), w.b("brown_terracotta")),
                 (kasten(0.1, 0, -0.6, 1, 4, 0.6), w.b("brown_terracotta")),
                 (kasten(-1.8, 4.5, -0.5, -1.0, 7.3, 0.5), rosa), (kasten(1.0, 4.5, -0.5, 1.8, 7.3, 0.5), rosa)]
        skulptur(w, 0.7 * s + 0.45, teile, (-2, -1, -2), (2, 11, 2), pos=(x, 1, z), winkel=-a + math.pi / 2)
    return w


NETHER3 = {
    "seelensand_fossilien": ("Seelensand-Fossilien", seelensand_fossilien),
    "basaltdelta": ("Basaltdelta", basaltdelta),
    "schatzkammer": ("Piglin-Schatzkammer", schatzkammer),
    "schreiter_anleger": ("Schreiter-Anleger", schreiter_anleger),
    "karmesinriese": ("Karmesin-Baumriese", karmesinriese),
    "quarzmine": ("Quarzmine", quarzmine),
    "ghastschwarm": ("Ghast-Schwarm", ghastschwarm),
    "felsbogen": ("Nether-Felsbogen", felsbogen),
    "magmawuerfel": ("Magmawürfel-Grube", magmawuerfel),
    "witherwachturm": ("Wither-Wachturm", witherwachturm),
    "tauschmarkt": ("Piglin-Tauschmarkt", tauschmarkt),
    "ausgrabung": ("Schrott-Ausgrabung", ausgrabung),
    "lavagaleere": ("Lava-Galeere", lavagaleere),
    "weinschrein": ("Weinender Schrein", weinschrein),
    "gewaechshaus": ("Pilzlicht-Gewächshaus", gewaechshaus),
    "seelenkerker": ("Seelenkerker", seelenkerker),
    "brauerei": ("Trankbrauerei", brauerei),
    "portalknoten": ("Portalknoten", portalknoten),
    "wurzelbruecke": ("Wirrwurzel-Brücke", wurzelbruecke),
    "leuchtfeuer_pyramide": ("Leuchtfeuer-Pyramide", leuchtfeuer_pyramide),
}

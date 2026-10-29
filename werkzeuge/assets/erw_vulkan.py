"""Vulkanreich II – zwanzig weitere Bauten aus Feuer und Asche: Feuersalamander-Statue, Aschewald, Obsidian-
Spiegelhalle, Kraterdorf, Schwefelquellen, Lavaröhre, Magmawurm, Bimsstein-Steinbruch, Signalfeuer-Turm,
Lavafestung, Opferaltar am Kraterrand, Erstarrte Lavazunge, Drachengerippe in der Asche, Glutpilzhain, Schwarzer
Strand mit Hafen, Feuerblumen-Feld, Lavabrunnen-Platz, Geschmolzene Burg, Lava-Grubenbahn und Feuerkloster."""

from __future__ import annotations

import math

import numpy as np

from feinbau import Dachmat, Mix, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen
from skulptur import Skulptur, dreh_y, ell, kap, kasten, kegel, kreisrand

S = [0.6, 1.0, 1.6, 2.5]


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def schwarz(w):
    return M(w, [("blackstone", 3), ("polished_blackstone_bricks", 2), ("cracked_polished_blackstone_bricks", 1),
                 ("basalt", 1)])


def asche(w, R, huegel=1.0, cx=0, cz=0, risse=0.025, hell=False):
    """Aschefeld: Basalt, Schwarzstein, Tuff und graue Asche mit glühenden Rissen; gibt Höhen zurück."""
    rn = Rauschen(w, 7)
    rf = Rauschen(w, 2.5)
    zellen = {}
    for x in range(cx - int(R) - 2, cx + int(R) + 3):
        for z in range(cz - int(R) - 2, cz + int(R) + 3):
            if math.hypot(x - cx, z - cz) <= R + 2 * rn(x, 0, z):
                h = int(huegel * 2 * rn(x * 0.7, 3, z * 0.7))
                v = rf(x, 5, z)
                for y in range(-2, h + 1):
                    if y == h:
                        if hell:
                            b = ("andesite" if v > 0.7 else "tuff" if v < 0.45 else "gray_concrete_powder")
                        else:
                            b = ("magma_block" if abs(v - 0.5) < risse else "gray_concrete_powder" if v > 0.72 else
                                 "tuff" if v < 0.22 else "basalt" if v < 0.4 else "blackstone")
                    else:
                        b = "blackstone" if y < h - 1 else "basalt"
                    w.setze(x, y, z, w.b(b, axis="y") if b == "basalt" else w.b(b))
                zellen[(x, z)] = h
    return zellen


def lavabecken(w, cx, cz, r, y=0, rand="blackstone", glut=True):
    for x in range(int(cx - r) - 2, int(cx + r) + 3):
        for z in range(int(cz - r) - 2, int(cz + r) + 3):
            d = math.hypot(x - cx, z - cz)
            if d <= r:
                w.setze(x, y, z, w.b("lava", level=0))
                w.setze(x, y - 1, z, w.b("magma_block"))
                for yy in range(y + 1, y + 3):
                    w.bloecke.pop((x, yy, z), None)
            elif d <= r + 1.2:
                w.setze(x, y, z, w.b("magma_block" if glut and (x + z) % 3 == 0 else rand))


def skulptur(w, u, teile, lo, hi, pos=(0, 0, 0), winkel=0.0):
    Sk = Skulptur(w, u)
    for i, (form, blk) in enumerate(teile):
        if blk is None:
            Sk.minus(form)
            continue
        Sk.mat(str(i), blk)
        Sk.plus(form, str(i))
    Sk.rendern(lo, hi, versatz=(pos[0] + 0.5, pos[1], pos[2] + 0.5), dreh=dreh_y(winkel))


def kohlenbecken(w, x, y, z, seele=False):
    w.setze(x, y, z, w.b("polished_blackstone_wall") if False else w.b("chiseled_polished_blackstone"))
    w.setze(x, y + 1, z, w.b("soul_campfire" if seele else "campfire", lit=True, signal_fire=False, facing="north",
                             waterlogged=False))


# ============================================================================ Bauten

def feuersalamander(seed, g=2):
    """Feuersalamander-Statue: ein riesiger schwarzer Salamander mit leuchtend orangen Flecken windet sich über
    einen Lavafelsen, den Kopf erhoben, der Schwanz in einer Glutlache."""
    w = _neu(seed)
    s = S[g]
    u = 0.9 * s + 0.4
    R = int(10 * u + 5)
    asche(w, R, 0.5)
    lavabecken(w, -int(6 * u), int(3 * u), 2 + s)
    kugel(w, 0, 0, 0, 4 * u, M(w, [("tuff", 2), ("basalt", 2), ("blackstone", 1)]), ry=1.6 * u)

    def haut(x, y, z, *a):
        return w.b("orange_concrete" if (x * 5 + y * 3 + z * 7) % 13 < 2 else "yellow_concrete" if
                   (x * 5 + y * 3 + z * 7) % 13 == 2 else "black_concrete")
    pts = bez((-7 * u, 1.5, 3 * u), (-2 * u, 2.6 * u + 2, 4 * u), (2 * u, 2.6 * u + 2, -2 * u),
              (6 * u, 3.6 * u + 1, 0))
    rohr(w, pts, 0.6 * u, 1.7 * u, mat=haut, rauh=0.03)
    hx, hy, hz = 6 * u, 3.6 * u + 1, 0
    kugel(w, hx + 1.2 * u, hy + 0.6 * u, hz, 1.5 * u, haut, ry=1.0 * u)
    for sz in (-1, 1):
        w.setze(round(hx + 1.8 * u), round(hy + 1.3 * u), round(hz + sz * 1.0 * u), w.b("shroomlight"))
    for t, sz in ((0.55, -1), (0.55, 1), (0.85, -1), (0.85, 1)):
        i = int(t * (len(pts) - 1))
        x, y, z, _ = pts[i]
        bein = bez((x, y, z), (x, y, z + sz * 2.2 * u), (x + 0.5 * u, 1, z + sz * 2.8 * u))
        rohr(w, bein, 0.7 * u, 0.5 * u, mat=haut)
    return w


def aschewald(seed, g=1):
    """Aschewald: verkohlte, kahle Baumgerippe auf grauer Asche, manche noch mit glimmenden Stellen, umgestürzte
    Stämme, Glutnester und dünne Rauchfäden."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = asche(w, R, 0.4, risse=0.04)
    rng = w.rng
    n = int(8 * s + 6)
    for _ in range(n):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.85
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y0 = zellen.get((x, z), 0) + 1
        H = int((5 + rng.random() * 7) * s + 3)
        holz = "dark_oak_log" if rng.random() < 0.5 else "basalt"
        for y in range(y0, y0 + H):
            w.setze(x, y, z, w.b(holz, axis="y") if rng.random() > 0.06 else w.b("magma_block"))
        for k in range(2 + int(s)):
            aa = rng.random() * 6.28
            yb = y0 + int(H * (0.45 + rng.random() * 0.4))
            L = 2 + rng.random() * 3 * s
            pts = bez((x, yb, z), (x + math.cos(aa) * L * 0.5, yb + L * 0.6, z + math.sin(aa) * L * 0.5),
                      (x + math.cos(aa) * L, yb + L * 0.9, z + math.sin(aa) * L))
            for px, py, pz, _ in pts:
                w.setze(round(px), round(py), round(pz), w.b("dark_oak_wood", axis="y") if holz != "basalt" else
                        w.b("polished_basalt", axis="y"), False)
        if rng.random() < 0.35:
            w.setze(x + 1, y0, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    for _ in range(2 + g):
        x0, z0 = int((rng.random() - 0.5) * R), int((rng.random() - 0.5) * R)
        for k in range(int(5 * s + 3)):
            w.setze(x0 + k, zellen.get((x0 + k, z0), 0) + 1, z0, w.b("dark_oak_log", axis="x"))
    for _ in range(int(10 * s)):
        x, z = int((rng.random() - 0.5) * R * 1.6), int((rng.random() - 0.5) * R * 1.6)
        if (x, z) in zellen and w.frei(x, zellen[(x, z)] + 1, z):
            w.setze(x, zellen[(x, z)] + 1, z, w.b("dead_bush") if rng.random() < 0.6 else w.b("gray_carpet"))
    return w


def spiegelhalle(seed, g=2):
    """Obsidian-Spiegelhalle: eine Säulenhalle aus poliertem Schwarzstein, deren Wände aus glänzendem und
    weinendem Obsidian bestehen; schwarze Glasfenster, ein Boden aus Obsidian-Schachbrett und Glutschalen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    asche(w, R, 0.2)
    B, T = int(6 * s + 6), int(9 * s + 8)
    H = int(5 * s + 5)
    st = schwarz(w)
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            w.setze(x, 0, z, w.b("obsidian" if (x + z) % 2 else "polished_blackstone"))
            for y in range(1, H + 1):
                rand = abs(x) == B or abs(z) == T
                saeule = abs(x) == B - 2 and z % 3 == 0
                if rand:
                    fen = 2 <= y <= H - 2 and (x + z) % 4 == 0 and abs(z) != T
                    w.setze(x, y, z, w.b("black_stained_glass") if fen else
                            w.b("crying_obsidian" if (x * 3 + y + z) % 7 == 0 else "obsidian"))
                elif saeule:
                    w.setze(x, y, z, w.b("polished_blackstone_bricks") if y % 3 else w.b("gilded_blackstone"))
                else:
                    w.bloecke.pop((x, y, z), None)
            w.setze(x, H + 1, z, st(x, H + 1, z))
    for x in range(-B - 1, B + 2):
        for z in range(-T - 1, T + 2):
            rand = abs(x) == B + 1 or abs(z) == T + 1
            if rand:
                w.setze(x, H + 1, z, w.b("polished_blackstone_bricks"))
                if (x + z) % 2 == 0:
                    w.setze(x, H + 2, z, w.b("polished_blackstone_brick_wall"))
            elif abs(x) <= 1:
                w.setze(x, H + 1, z, w.b("black_stained_glass"))
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * (B + 1), sz * (T + 1)
            for y in range(H + 1, H + int(5 * s + 5)):
                r = 1 if y < H + int(5 * s + 2) else 0
                for dx in range(-r, r + 1):
                    for dz in range(-r, r + 1):
                        w.setze(cx + dx, y, cz + dz, w.b("obsidian" if r else "crying_obsidian"))
            w.setze(cx, H + int(5 * s + 5), cz, w.b("gold_block"))
    for x in (-1, 0, 1):
        for y in range(1, 4):
            w.bloecke.pop((x, y, T), None)
    for z in range(-T + 2, T - 1, 4):
        kohlenbecken(w, 0, 1, z)
    w.setze(0, 1, -T + 1, w.b("crying_obsidian"))
    w.setze(0, 2, -T + 1, w.b("respawn_anchor", charges=4))
    return w


def kraterdorf(seed, g=2):
    """Kraterdorf: Hütten aus Basalt mit Schwarzsteindächern stehen auf dem Ringwall eines erloschenen Kraters,
    in dessen Mitte ein Lavasee glüht; Stege führen hinab, Glutlaternen säumen den Pfad."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    rn = Rauschen(w, 5)
    Rr = R * 0.55
    H = 4 * s + 4
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 2 * rn(x, 0, z):
                continue
            h = int(H * math.exp(-((d - Rr) / (R * 0.28)) ** 2) + rn(x, 2, z) * 2)
            if d < Rr * 0.45:
                h = 0
            for y in range(-2, h + 1):
                b = "gray_concrete_powder" if y == h and rn(x, 5, z) > 0.6 else "basalt" if (y + x) % 4 else "tuff"
                w.setze(x, y, z, w.b(b, axis="y") if b == "basalt" else w.b(b))
    lavabecken(w, 0, 0, Rr * 0.4, y=0)
    n = 4 + g
    for i in range(n):
        a = i / n * 2 * math.pi + 0.2
        cx, cz = round(math.cos(a) * Rr), round(math.sin(a) * Rr)
        top = max(y for y in range(-2, int(H) + 5) if not w.frei(cx, y, cz))
        Bh = int(2 * s + 4) | 1
        x0, z0 = cx - Bh // 2, cz - Bh // 2
        for x in range(x0, x0 + Bh):
            for z in range(z0, z0 + Bh):
                w.setze(x, top, z, w.b("polished_basalt", axis="y"))
                for y in range(top + 1, top + 4):
                    rand = x in (x0, x0 + Bh - 1) or z in (z0, z0 + Bh - 1)
                    if rand:
                        fen = y == top + 2 and (x + z) % 2 == 0 and not (x in (x0, x0 + Bh - 1) and
                                                                         z in (z0, z0 + Bh - 1))
                        w.setze(x, y, z, w.b("orange_stained_glass") if fen else w.b("basalt", axis="y"))
                    else:
                        w.bloecke.pop((x, y, z), None)
        satteldach(w, x0, z0, x0 + Bh - 1, z0 + Bh - 1, top + 4, Dachmat(w, ["blackstone", "polished_blackstone"]),
                   first_x=i % 2 == 0, ue=1, giebel=M(w, [("blackstone", 1)]), traufe="dark_oak", steil=1)
        dx = -1 if cx > 0 else 1
        w.setze(cx, top + 1, cz - Bh // 2 if cz > 0 else cz + Bh // 2, w.b("air"))
        w.setze(cx + dx * (Bh // 2 + 1), top + 1, cz, w.b("chiseled_polished_blackstone"))
        w.setze(cx + dx * (Bh // 2 + 1), top + 2, cz, w.b("lantern", hanging=False, waterlogged=False))
    return w


def schwefelquellen(seed, g=1):
    """Schwefelquellen: gelb verkrustete Terrassen mit dampfenden, giftgrünen Becken, rauchende Fumarolen,
    weiße Salzränder und ein verwitterter Holzsteg mit Warnschildern."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = asche(w, R, 0.3, risse=0.0)
    rng = w.rng
    gelb = M(w, [("yellow_terracotta", 3), ("yellow_concrete", 1), ("horn_coral_block", 1), ("calcite", 1)])
    for k in range(4 + g):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.55
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        r = (1.5 + rng.random() * 2) * s + 1
        for x in range(int(cx - r) - 2, int(cx + r) + 3):
            for z in range(int(cz - r) - 2, int(cz + r) + 3):
                dd = math.hypot(x - cx, z - cz)
                if dd <= r:
                    w.setze(x, 0, z, w.b("water", level=0))
                    w.setze(x, -1, z, w.b("lime_terracotta" if dd < r * 0.5 else "green_terracotta"))
                    for y in range(1, 3):
                        w.bloecke.pop((x, y, z), None)
                elif dd <= r + 1.5:
                    w.setze(x, 0, z, gelb(x, 0, z))
                    w.setze(x, 1, z, w.b("white_concrete_powder" if (x + z) % 3 == 0 else "yellow_terracotta"),
                            False)
    for _ in range(4 + 2 * g):
        a = rng.random() * 6.28
        d = R * (0.4 + rng.random() * 0.4)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = zellen.get((x, z), 0) + 1
        h = int(1 + rng.random() * 3 * s)
        for k in range(h):
            for dx, dz in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)):
                if k < h - 1 or (dx, dz) == (0, 0):
                    w.setze(x + dx, y + k, z + dz, gelb(x, y, z) if (dx, dz) != (0, 0) else w.b("yellow_terracotta"))
        w.setze(x, y + h, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
        w.setze(x, y + h - 1, z, w.b("hay_block"))
    for x in range(-R + 2, R - 1):
        z = round(math.sin(x / 4) * 2)
        y = max(zellen.get((x, z), 0), 1) + 1
        for dz in (0, 1):
            w.setze(x, y, z + dz, platte(w, "spruce", "bottom"))
        if x % 5 == 0:
            w.setze(x, y, z - 1, w.b("spruce_fence"))
            w.setze(x, y + 1, z - 1, w.b("spruce_wall_sign", facing="south", waterlogged=False) if False else
                    w.b("yellow_wool"))
    return w


def lavaroehre(seed, g=2):
    """Lavaröhre: ein langer, gewundener Tunnel aus erstarrter Lava, dessen Decke stellenweise eingestürzt ist –
    durch die Oberlichter sieht man den glühenden Lavastrom am Grund und Tropfsteine aus Basalt."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    asche(w, R, 0.4)
    r = 3.0 * s + 2.5
    L = R * 1.6
    pts = [(-L / 2 + t * L, r * 0.35, math.sin(t * 2.4 * math.pi) * R * 0.3, t) for t in np.linspace(0, 1, 80)]
    mat = M(w, [("basalt", 3), ("blackstone", 2), ("smooth_basalt", 1), ("tuff", 1)])
    rohr(w, pts, r, r * 0.8, mat=lambda x, y, z, *a: mat(x, y, z), rauh=0.12)
    rn = Rauschen(w, 4)
    for x, y, z, t in pts:
        rr = r + (r * 0.8 - r) * t
        for dx in range(-int(rr) - 1, int(rr) + 2):
            for dy in range(-int(rr) - 1, int(rr) + 2):
                for dz in range(-int(rr) - 1, int(rr) + 2):
                    d = math.sqrt(dx * dx + dy * dy + dz * dz)
                    p = (round(x + dx), round(y + dy), round(z + dz))
                    if d < rr - 1.3 and p[1] >= 1:
                        w.bloecke.pop(p, None)
                    elif d < rr + 0.6 and dy > rr * 0.4 and rn(p[0], 0, p[2]) > 0.62:
                        w.bloecke.pop(p, None)
        for dz in (-1, 0, 1):
            w.setze(round(x), 0, round(z + dz), w.b("magma_block") if dz else w.b("lava", level=0))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 2 and w.frei(x, y - 1, z) and w.frei(x, y - 2, z) and rng.random() < 0.05:
            w.setze(x, y - 1, z, w.b("pointed_dripstone", vertical_direction="down", thickness="tip",
                                     waterlogged=False))
    return w


def magmawurm(seed, g=2):
    """Magmawurm: ein gewaltiger Wurm aus geschuppten Magma- und Basaltringen bricht in hohem Bogen aus einem
    Lavasee, sein runder Schlund voller Obsidianzähne glüht von innen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 7)
    asche(w, R, 0.3)
    lavabecken(w, -int(R * 0.35), 0, 3 * s + 2)
    lavabecken(w, int(R * 0.3), int(R * 0.2), 2.5 * s + 1.5)
    r = 1.8 * s + 1.2
    A = 10 * s + 6

    def mat(x, y, z, lx=0, *a):
        return w.b("magma_block" if (x + y * 2 + z) % 6 == 0 else "basalt" if (y // 2) % 2 else "blackstone",
                   **({"axis": "y"} if (y // 2) % 2 and (x + y * 2 + z) % 6 else {}))
    pts = bez((-R * 0.35, -2, 0), (-R * 0.3, A * 1.4, 0), (R * 0.25, A * 1.3, R * 0.15), (R * 0.3, -2, R * 0.2))
    rohr(w, pts, r, r, mat=mat, rauh=0.05)
    pts2 = bez((-R * 0.6, -2, -R * 0.4), (-R * 0.7, A * 0.9, -R * 0.2), (-R * 0.45, A * 1.2, -R * 0.1))
    rohr(w, pts2, r * 1.15, r * 1.35, mat=mat, rauh=0.05)
    hx, hy, hz, _ = pts2[-1]
    for dx in range(-int(r * 1.35) - 1, int(r * 1.35) + 2):
        for dz in range(-int(r * 1.35) - 1, int(r * 1.35) + 2):
            d = math.hypot(dx, dz)
            for dy in range(0, 3):
                p = (round(hx + dx), round(hy + dy), round(hz + dz))
                if d < r * 1.35 - 1:
                    w.setze(*p, w.b("shroomlight") if dy == 0 else w.b("air"))
                elif d < r * 1.35 + 0.5 and dy == 2 and (dx + dz) % 2 == 0:
                    w.setze(*p, w.b("obsidian"))
    return w


def bimssteinbruch(seed, g=1):
    """Bimsstein-Steinbruch: hellgraue Abbaustufen im Vulkangestein, ein hölzerner Lastkran mit Kette, Loren auf
    Schienen, gestapelte Steinblöcke und eine Werkzeughütte."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = asche(w, R, 0.2)
    bims = M(w, [("smooth_basalt", 2), ("tuff", 3), ("calcite", 1), ("diorite", 1)])
    stufen = 3 + g
    for k in range(stufen):
        rr = R * 0.75 - k * 2.2 * s
        for x in range(-int(rr), int(rr) + 1):
            for z in range(-R, 0):
                if math.hypot(x, z * 1.2) <= rr:
                    for y in range(1, (stufen - k) * 2 + 2):
                        w.setze(x, y, z, bims(x, y, z))
    for x in range(-int(R * 0.4), int(R * 0.4) + 1):
        for z in range(-int(R * 0.35), 0):
            for y in range(1, stufen * 2 + 3):
                if abs(x) < R * 0.3 - y * 0.6:
                    w.bloecke.pop((x, y, z), None)
    kx, kz = int(R * 0.45), int(R * 0.1)
    hk = int(6 * s + 6)
    for y in range(1, hk):
        w.setze(kx, y, kz, w.b("spruce_log", axis="y"))
    for k in range(int(5 * s + 4)):
        w.setze(kx - k, hk, kz - k // 2, w.b("spruce_log", axis="x"))
    ax, az = kx - int(5 * s + 3), kz - int(5 * s + 3) // 2
    for y in range(hk - 1, 3, -1):
        w.setze(ax, y, az, w.b("chain", axis="y", waterlogged=False))
    w.setze(ax, 3, az, w.b("tuff"))
    w.setze(ax, 2, az, w.b("tuff"))
    for z in range(-int(R * 0.6), int(R * 0.7)):
        x = -int(R * 0.6)
        w.setze(x, zellen.get((x, z), 0) + 1, z, w.b("rail", shape="north_south", waterlogged=False))
    for k, z in enumerate((-2, 3)):
        w.setze(-int(R * 0.6), zellen.get((-int(R * 0.6), z), 0) + 1, z, w.b("rail", shape="north_south",
                                                                           waterlogged=False))
    hx, hz = -int(R * 0.25), int(R * 0.55)
    for x in range(hx - 2, hx + 3):
        for z in range(hz - 2, hz + 3):
            for y in range(1, 4):
                rand = abs(x - hx) == 2 or abs(z - hz) == 2
                if rand:
                    w.setze(x, y, z, w.b("spruce_planks" if (x + z) % 4 else "stripped_spruce_log", axis="y"))
            w.setze(x, 4, z, platte(w, "spruce", "bottom"))
    w.bloecke.pop((hx, 1, hz + 2), None)
    w.bloecke.pop((hx, 2, hz + 2), None)
    for k in range(3 + g):
        x, z = int(R * 0.2) + (k % 3) * 2, int(R * 0.45) + (k // 3) * 2
        for y in range(1, 2 + k % 2):
            w.setze(x, y, z, w.b("polished_andesite"))
    return w


def signalfeuerturm(seed, g=2):
    """Signalfeuer-Turm: ein schlanker, sich verjüngender Turm aus Schwarzstein auf einem Basaltfelsen, oben ein
    riesiges Kohlenbecken mit lodernden Feuern unter einem Ring aus vergoldeten Zacken."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    asche(w, R, 0.6)
    st = schwarz(w)
    kugel(w, 0, 0, 0, 5 * s + 3, M(w, [("basalt", 3), ("tuff", 1), ("blackstone", 1)]), ry=3 * s + 2)
    H = int(18 * s + 10)
    y0 = int(3 * s + 2)
    for y in range(y0, y0 + H):
        r = (2.4 * s + 1.8) * (1 - 0.35 * (y - y0) / H)
        for x, z in kreisrand(r):
            fen = (y - y0) % 6 == 3 and (x == 0 or z == 0)
            w.setze(x, y, z, w.b("orange_stained_glass") if fen else st(x, y, z))
        if (y - y0) % 6 == 0:
            for x, z in kreisrand(r + 0.8):
                w.setze(x, y, z, w.b("polished_blackstone_bricks"))
    top = y0 + H
    rb = 2.4 * s + 2.0
    for k in range(3):
        rr = rb * (0.7 + 0.15 * k)
        for x in range(-int(rr) - 1, int(rr) + 2):
            for z in range(-int(rr) - 1, int(rr) + 2):
                d = math.hypot(x, z)
                if d <= rr:
                    w.setze(x, top + k, z, w.b("gilded_blackstone") if d > rr - 1 else
                            (w.b("magma_block") if k < 2 else w.b("campfire", lit=True, signal_fire=True,
                                                                  facing="north", waterlogged=False)))
    for i in range(10):
        a = i / 10 * 2 * math.pi
        x, z = round(math.cos(a) * rb * 1.1), round(math.sin(a) * rb * 1.1)
        for k in range(int(2 + s)):
            w.setze(x, top + 3 + k, z, w.b("gold_block" if k == 0 else "polished_blackstone_wall"))
    for y in (y0, y0 + 1):
        w.bloecke.pop((0, y, round(2.4 * s + 1.8)), None)
    return w


def lavafestung(seed, g=2):
    """Lavafestung: eine trutzige Festung aus Schwarzsteinziegeln mit vier wuchtigen Ecktürmen, Zinnen und
    glühenden Schießscharten, umgeben von einem Lavagraben mit Zugbrücke aus Basalt."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    asche(w, R, 0.2)
    st = schwarz(w)
    A = int(7 * s + 5)
    H = int(5 * s + 5)
    for x in range(-A - 4, A + 5):
        for z in range(-A - 4, A + 5):
            m = max(abs(x), abs(z))
            if A + 1 < m <= A + 3:
                w.setze(x, 0, z, w.b("lava", level=0))
                w.setze(x, -1, z, w.b("magma_block"))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            rand = max(abs(x), abs(z)) == A
            w.setze(x, 0, z, w.b("polished_blackstone"))
            if rand:
                for y in range(1, H + 1):
                    sch = y == H - 2 and (x + z) % 4 == 0
                    w.setze(x, y, z, w.b("shroomlight") if sch else st(x, y, z))
                if (x + z) % 2 == 0:
                    w.setze(x, H + 1, z, st(x, H + 1, z))
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * A, sz * A
            rt = 2 * s + 1.8
            for y in range(1, H + int(4 * s) + 3):
                for x, z in kreisrand(rt, cx, cz):
                    w.setze(x, y, z, st(x, y, z))
            yt = H + int(4 * s) + 3
            for x, z in kreisrand(rt + 1, cx, cz):
                w.setze(x, yt, z, w.b("polished_blackstone_bricks"))
                if (x + z) % 2 == 0:
                    w.setze(x, yt + 1, z, w.b("polished_blackstone_brick_wall"))
            w.setze(cx, yt + 1, cz, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    kh = int(8 * s + 6)
    for x in range(-int(2 * s + 2), int(2 * s + 3)):
        for z in range(-int(2 * s + 2), int(2 * s + 3)):
            for y in range(1, kh):
                if max(abs(x), abs(z)) == int(2 * s + 2):
                    w.setze(x, y, z, st(x, y, z))
    kegeldach(w, 0, 0, kh, int(2 * s + 2), Dachmat(w, ["blackstone", "polished_blackstone"]), form="kegel",
              eckig=True, spitze="gold_block")
    for x in (-1, 0, 1):
        for y in (1, 2, 3):
            w.bloecke.pop((x, y, A), None)
        for z in range(A + 1, A + 4):
            w.setze(x, 0, z, w.b("polished_basalt", axis="z"))
    return w


def opferaltar(seed, g=2):
    """Opferaltar am Kraterrand: eine Felsnase ragt über einen glühenden Krater, darauf ein gestufter Altar aus
    Schwarzstein mit goldener Schale, flankiert von Feuersäulen und einer Allee aus Wächterpfeilern."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 4)
    H = 6 * s + 4
    for x in range(-R - 1, R + 2):
        for z in range(-R - 1, R + 2):
            d = math.hypot(x, z)
            if d > R + rn(x, 0, z) * 2:
                continue
            krater = math.hypot(x, z - R * 0.45) < R * 0.45
            nase = abs(x) < 3 * s + 2 and z < R * 0.55
            h = int(H * min(1.0, 1.6 * (1 - d / (R + 2))) + rn(x, 3, z) * 2) if not krater or nase else -1
            for y in range(-2, h + 1):
                w.setze(x, y, z, w.b("basalt", axis="y") if (x + y) % 3 else w.b("blackstone"))
            if krater and not nase:
                w.setze(x, -1, z, w.b("lava", level=0) if (x + z) % 2 else w.b("magma_block"))
    top = int(H) + 1
    st = schwarz(w)
    for k in range(3):
        a = int(3 * s + 2) - k
        for x in range(-a, a + 1):
            for z in range(int(R * 0.35) - a, int(R * 0.35) + a + 1):
                w.setze(x, top + k, z, st(x, top + k, z))
    zt = int(R * 0.35)
    w.setze(0, top + 3, zt, w.b("gold_block"))
    w.setze(0, top + 4, zt, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for z in range(-int(R * 0.6), zt - 3, 3):
        for sx in (-1, 1):
            x = sx * int(2 * s + 2)
            for y in range(top, top + int(3 * s + 2)):
                if w.frei(x, y, z) or y == top:
                    w.setze(x, y, z, w.b("polished_blackstone_bricks"))
            w.setze(x, top + int(3 * s + 2), z, w.b("magma_block"))
    for sx in (-1, 1):
        x = sx * int(3 * s + 3)
        for y in range(top, top + int(6 * s + 4)):
            w.setze(x, y, zt, w.b("chiseled_polished_blackstone") if y % 4 == 0 else w.b("polished_blackstone"))
        kohlenbecken(w, x, top + int(6 * s + 4), zt)
    return w


def lavazunge(seed, g=1):
    """Erstarrte Lavazunge: ein breiter, gewundener Lavastrom aus schwarzer Stricklava mit glühenden Spalten,
    wulstigen Rändern und Pahoehoe-Falten, der sich in eine Ebene aus Asche ergossen hat."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = asche(w, R, 0.2, risse=0.0, hell=True)
    rn = Rauschen(w, 3)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            mitte = math.sin(x / (5 * s + 3)) * R * 0.25
            breite = (3 + 2.5 * s) * (1.2 - 0.5 * (x + R) / (2 * R)) + rn(x, 0, z) * 2
            dz = abs(z - mitte)
            if dz > breite or math.hypot(x, z) > R:
                continue
            h0 = zellen.get((x, z), 0)
            wulst = 1 + int(1.5 * s * (1 - (dz / breite) ** 2)) + (1 if dz > breite - 1.5 else 0)
            for y in range(h0 + 1, h0 + wulst + 1):
                falte = math.sin((x * 1.3 + dz * dz * 0.25)) > 0.6
                b = "magma_block" if (y == h0 + wulst and rn(x * 2, 5, z * 2) > 0.68) else \
                    "polished_basalt" if falte else "blackstone" if (x + z) % 3 else "basalt"
                w.setze(x, y, z, w.b(b, axis="x") if "basalt" in b else w.b(b))
    for k in range(int(3 * s)):
        x = int((k / max(1, int(3 * s)) - 0.5) * R * 1.4)
        z = round(math.sin(x / (5 * s + 3)) * R * 0.25)
        w.setze(x, zellen.get((x, z), 0) + int(1.5 * s) + 2, z, w.b("lava", level=0))
    return w


def drachengerippe(seed, g=2):
    """Drachengerippe in der Asche: das riesige Skelett eines Drachen liegt halb versunken im Aschefeld – Schädel
    mit Hörnern, Wirbelsäule, gebogene Rippen und die Knochenfinger eines ausgebreiteten Flügels."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    asche(w, R, 0.4)
    L = R * 1.3
    knochen = M(w, [("bone_block", 4), ("calcite", 1), ("smooth_quartz", 1)])
    pts = [(-L / 2 + t * L, 1 + math.sin(t * math.pi) * 2.5 * s, math.sin(t * 2 * math.pi) * R * 0.15, t)
           for t in np.linspace(0, 1, int(L * 1.5))]
    for i, (x, y, z, t) in enumerate(pts):
        r = 0.6 + 0.6 * s * math.sin(math.pi * min(1, t * 1.3))
        kugel(w, x, y, z, r, knochen)
        if 0.25 < t < 0.65 and i % 3 == 0:
            rr = (4.5 * s + 2) * math.sin(math.pi * (t - 0.25) / 0.4)
            for sz in (-1, 1):
                rp = bez((x, y, z), (x, y + rr * 0.8, z + sz * rr * 0.9), (x + 1, 0, z + sz * rr * 1.1))
                for px, py, pz, _ in rp:
                    w.setze(round(px), round(py), round(pz), w.b("bone_block", axis="y"), False)
    hx, hy, hz, _ = pts[-1]
    kugel(w, hx + 2 * s, hy + 1, hz, 2.2 * s + 1, knochen, ry=1.6 * s + 0.8)
    rohr(w, bez((hx + 2 * s, hy + 1, hz), (hx + 4 * s, hy + 1, hz), (hx + 6 * s + 1, hy, hz)), 1.0 * s + 0.5,
         0.6 * s + 0.4, mat=knochen)
    for sz in (-1, 1):
        rohr(w, bez((hx + 1.5 * s, hy + 2 * s, hz + sz * s), (hx, hy + 4 * s, hz + sz * 2 * s),
                    (hx - 2 * s, hy + 5 * s, hz + sz * 2.5 * s)), 0.6 * s + 0.4, 0.25, mat=w.b("bone_block"))
        w.setze(round(hx + 2.5 * s), round(hy + 1.5 * s), round(hz + sz * 1.2 * s), w.b("air"))
    wx, wy, wz, _ = pts[int(len(pts) * 0.4)]
    for k in range(4):
        aa = 0.4 + k * 0.45
        Lf = (7 + k * 1.5) * s
        rohr(w, bez((wx, wy + 1, wz), (wx + math.cos(aa) * Lf * 0.5, wy + 3 * s, wz - Lf * 0.5),
                    (wx + math.cos(aa) * Lf, 1, wz - math.sin(aa) * Lf)), 0.5 * s + 0.3, 0.25, mat=w.b("bone_block"))
    return w


def glutpilzhain(seed, g=1):
    """Glutpilzhain: riesige Pilze mit karmesinroten Stielen und orange glühenden Hüten voller Pilzlicht wachsen
    zwischen Basaltbrocken, dazu kleine Feuerpilze und Netherwarzen-Polster."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = asche(w, R, 0.4)
    rng = w.rng
    n = 3 + 2 * g
    for i in range(n):
        a = i / n * 2 * math.pi + rng.random() * 0.5
        d = R * (0.2 + rng.random() * 0.55) if i else 0
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        y0 = zellen.get((cx, cz), 0) + 1
        H = int((5 + rng.random() * 6) * s + 3) if i else int(14 * s + 6)
        neig = (rng.random() - 0.5) * 0.3
        for y in range(y0, y0 + H):
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    if abs(dx) + abs(dz) <= (1 if H > 8 else 0):
                        w.setze(cx + dx + round(neig * (y - y0)), y, cz + dz, w.b("crimson_stem", axis="y"))
        tx = cx + round(neig * H)
        r = H * 0.45 + 1.5
        for k in range(int(r * 0.6) + 2):
            rr = r * math.sqrt(max(0, 1 - (k / (r * 0.6 + 1.5)) ** 2))
            for x in range(int(tx - rr) - 1, int(tx + rr) + 2):
                for z in range(int(cz - rr) - 1, int(cz + rr) + 2):
                    dd = math.hypot(x - tx, z - cz)
                    if rr - 1.4 < dd <= rr or (dd <= rr and k == int(r * 0.6) + 1):
                        w.setze(x, y0 + H + k, z, w.b("shroomlight") if (x * 3 + z + k) % 7 == 0 else
                                w.b("orange_terracotta" if k < 2 else "nether_wart_block"))
    for _ in range(int(12 * s + 6)):
        x, z = int((rng.random() - 0.5) * R * 1.7), int((rng.random() - 0.5) * R * 1.7)
        if (x, z) in zellen and w.frei(x, zellen[(x, z)] + 1, z):
            w.setze(x, zellen[(x, z)] + 1, z, w.b("crimson_fungus") if rng.random() < 0.5 else
                    w.b("crimson_roots"))
            w.setze(x, zellen[(x, z)], z, w.b("crimson_nylium"))
    return w


def schwarzer_strand(seed, g=2):
    """Schwarzer Strand mit Hafen: ein Strand aus schwarzem Vulkansand an einer Bucht, ein Steg aus dunklem Holz
    mit einem Fischerboot, Basaltklippen mit Säulen und eine kleine Hafenkneipe mit Leuchtfeuer."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    rn = Rauschen(w, 5)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            ufer = z + rn(x, 3, 0) * 5 - R * 0.1
            if ufer > 0:
                w.setze(x, -1, z, w.b("black_concrete_powder"))
                w.setze(x, 0, z, w.b("water", level=0))
            else:
                h = 0 if ufer > -R * 0.4 else int((-ufer - R * 0.4) * 0.8 + rn(x, 6, z) * 2)
                for y in range(-2, h + 1):
                    b = "black_concrete_powder" if h == 0 and y == 0 else "basalt"
                    w.setze(x, y, z, w.b(b, axis="y") if b == "basalt" else w.b(b))
    for x in range(-1, 2):
        for z in range(int(-R * 0.1), int(R * 0.6)):
            w.setze(x, 1, z, w.b("dark_oak_planks" if x == 0 or z % 2 else "dark_oak_slab", type="bottom",
                                 waterlogged=False) if x == 0 or z % 2 else w.b("dark_oak_slab", type="bottom",
                                                                                 waterlogged=False))
            if z % 4 == 0 and x != 0:
                w.setze(x, 0, z, w.b("dark_oak_log", axis="y"))
                w.setze(x, -1, z, w.b("dark_oak_log", axis="y"))
    bx, bz = 4, int(R * 0.35)
    for i in range(-3, 4):
        bw = 1.6 * math.sqrt(max(0, 1 - (i / 3.6) ** 2))
        for q in (-1, 0, 1):
            if abs(q) <= bw:
                w.setze(bx + q, 0, bz + i, w.b("spruce_planks"))
                if abs(q) >= bw - 0.8:
                    w.setze(bx + q, 1, bz + i, w.b("spruce_planks"))
    for y in range(1, 6):
        w.setze(bx, y, bz, w.b("spruce_fence"))
    hx, hz = -int(R * 0.35), -int(R * 0.25)
    for x in range(hx - 3, hx + 4):
        for z in range(hz - 2, hz + 3):
            w.setze(x, 0, z, w.b("cobbled_deepslate"))
            for y in range(1, 4):
                if abs(x - hx) == 3 or abs(z - hz) == 2:
                    fen = y == 2 and (x + z) % 2 == 0 and abs(x - hx) < 3
                    w.setze(x, y, z, w.b("orange_stained_glass") if fen else w.b("dark_oak_planks" if (x + z) % 3
                                                                                   else "dark_oak_log", axis="y"))
                else:
                    w.bloecke.pop((x, y, z), None)
    satteldach(w, hx - 3, hz - 2, hx + 3, hz + 2, 4, Dachmat(w, ["blackstone", "deepslate_tile"]), first_x=True,
               ue=1, giebel=M(w, [("dark_oak_planks", 1)]), traufe="dark_oak")
    w.bloecke.pop((hx, 1, hz + 2), None)
    w.bloecke.pop((hx, 2, hz + 2), None)
    lx, lz = int(R * 0.45), -int(R * 0.05)
    for y in range(1, int(5 * s + 5)):
        for dx, dz in ((0, 0), (1, 0), (0, 1), (1, 1)):
            w.setze(lx + dx, y, lz + dz, w.b("polished_basalt", axis="y") if y % 4 else w.b("blackstone"))
    w.setze(lx, int(5 * s + 5), lz, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    return w


def feuerblumenfeld(seed, g=1):
    """Feuerblumen-Feld: auf warmem Aschegrund blühen riesige Feuerblumen mit Blütenblättern aus orangem und
    rotem Glas und Pilzlicht-Kelchen, dazwischen Fackellilien und Glutkristalle."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = asche(w, R, 0.3, risse=0.03)
    rng = w.rng
    n = 4 + 3 * g
    for i in range(n):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.8
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        y0 = zellen.get((cx, cz), 0) + 1
        H = int((3 + rng.random() * 5) * s + 2)
        for y in range(y0, y0 + H):
            w.setze(cx, y, cz, w.b("warped_stem", axis="y") if False else w.b("crimson_hyphae", axis="y"))
        top = y0 + H
        w.setze(cx, top, cz, w.b("shroomlight"))
        rp = 1.5 + s * 1.2
        farbe = ["orange_stained_glass", "red_stained_glass", "yellow_stained_glass"][i % 3]
        for k in range(6):
            aa = k / 6 * 2 * math.pi + i
            for L in range(1, int(rp) + 2):
                x, z = round(cx + math.cos(aa) * L), round(cz + math.sin(aa) * L)
                yy = top + (1 if L > rp * 0.6 else 0)
                w.setze(x, yy, z, w.b(farbe))
                if L > 1:
                    w.setze(round(cx + math.cos(aa + 0.25) * L), yy, round(cz + math.sin(aa + 0.25) * L), w.b(farbe),
                            False)
    for _ in range(int(20 * s + 8)):
        x, z = int((rng.random() - 0.5) * R * 1.7), int((rng.random() - 0.5) * R * 1.7)
        if (x, z) in zellen and w.frei(x, zellen[(x, z)] + 1, z):
            w.setze(x, zellen[(x, z)] + 1, z, w.b("torchflower") if rng.random() < 0.6 else w.b("orange_tulip"))
            w.setze(x, zellen[(x, z)], z, w.b("coarse_dirt"))
    return w


def lavabrunnen(seed, g=1):
    """Lavabrunnen-Platz: ein gepflasterter Platz aus Schwarzsteinplatten, in der Mitte ein dreistufiger Brunnen,
    aus dessen Drachenköpfen Lava in glühende Becken fließt, umringt von Säulen mit Glutschalen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    asche(w, R, 0.1)
    for x in range(-R + 2, R - 1):
        for z in range(-R + 2, R - 1):
            if math.hypot(x, z) < R * 0.8:
                w.setze(x, 0, z, w.b("polished_blackstone" if (x // 2 + z // 2) % 2 else "polished_blackstone_bricks"))
    stufen = 3
    for k in range(stufen):
        r = (4.5 - k * 1.3) * s + 1.5
        y = k * 2 + 1
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(x, z)
                if d <= r:
                    for yy in range(1, y + 1):
                        w.setze(x, yy, z, w.b("polished_blackstone_bricks"))
                    w.setze(x, y + 1, z, w.b("lava", level=0) if d < r - 1 else w.b("chiseled_polished_blackstone"))
    sp = stufen * 2 + 2
    for y in range(sp, sp + int(3 * s + 2)):
        w.setze(0, y, 0, w.b("gilded_blackstone" if y % 2 else "polished_blackstone"))
    for i in range(4):
        a = i * math.pi / 2
        x, z = round(math.cos(a)), round(math.sin(a))
        w.setze(x, sp + int(3 * s + 1), z, w.b("magma_block"))
    w.setze(0, sp + int(3 * s + 2), 0, w.b("shroomlight"))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.65), round(math.sin(a) * R * 0.65)
        for y in range(1, int(3 * s + 3)):
            w.setze(x, y, z, w.b("polished_blackstone_wall") if y > 1 else w.b("chiseled_polished_blackstone"))
        kohlenbecken(w, x, int(3 * s + 3), z)
    return w


def geschmolzene_burg(seed, g=2):
    """Geschmolzene Burg: eine Burg, die in einem Lavastrom halb zerflossen ist – Türme neigen sich, Mauern sind
    abgerutscht und zu glühender Schlacke verlaufen, auf der Hälfte steht noch das stolze Tor."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    asche(w, R, 0.2)
    st = M(w, [("stone_bricks", 3), ("cracked_stone_bricks", 2), ("andesite", 1)])
    A = int(7 * s + 5)
    H = int(5 * s + 5)
    rn = Rauschen(w, 4)

    def schmelz(x, z):
        return max(0.0, min(1.0, (x + A * 0.2) / (A * 1.2) + rn(x, 0, z) * 0.3))
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            if max(abs(x), abs(z)) != A:
                continue
            m = schmelz(x, z)
            h = int(H * (1 - m * 0.85))
            for y in range(1, h + 1):
                b = st(x, y, z) if y < h - 1 or m < 0.3 else w.b("magma_block" if (x + y) % 2 else "blackstone")
                w.setze(x, y, z, b)
            if m > 0.4:
                for k in range(1, int(m * 4) + 1):
                    w.setze(x + k, 1, z, w.b("magma_block" if (x + z + k) % 3 else "blackstone"), False)
            elif (x + z) % 2 == 0:
                w.setze(x, h + 1, z, st(x, h + 1, z))
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * A, sz * A
            m = schmelz(cx, cz)
            Ht = int((H + 6 * s) * (1 - 0.6 * m))
            neig = m * 0.35 * sx
            for y in range(1, Ht + 1):
                ox = round(neig * y)
                for x, z in kreisrand(2 * s + 1.5, cx + ox, cz):
                    w.setze(x, y, z, st(x, y, z) if m < 0.4 or y < Ht - 2 else w.b("magma_block"))
            if m < 0.4:
                kegeldach(w, cx + round(neig * Ht), cz, Ht + 1, int(2 * s + 1.5), Dachmat(w, ["deepslate_tile"]),
                          form="kegel")
    for x in range(int(A * 0.2), R):
        for z in range(-int(A * 0.8), int(A * 0.8)):
            if math.hypot(x, z) < R and rn(x * 1.5, 7, z * 1.5) > 0.35:
                w.setze(x, 0, z, w.b("lava", level=0) if rn(x * 3, 1, z * 3) > 0.6 else w.b("magma_block"))
    for x in (-1, 0, 1):
        for y in (1, 2, 3):
            w.bloecke.pop((-A, y, x), None)
    return w


def grubenbahn(seed, g=2):
    """Lava-Grubenbahn: eine Holzbahn auf hohen Gerüstböcken überquert einen Lavasee zu einem Stolleneingang im
    Vulkanfels, mit Loren, Signallaternen und einer Verladerampe für Erz."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    asche(w, R, 0.2)
    lavabecken(w, 0, 0, R * 0.45, y=0)
    hz = int(4 * s + 4)
    for x in range(-R + 2, R - 1):
        z = round(math.sin(x / R * 1.5) * 2)
        if math.hypot(x, z) > R:
            continue
        w.setze(x, hz, z, w.b("spruce_planks"))
        w.setze(x, hz + 1, z, w.b("rail", shape="east_west", waterlogged=False))
        if x % 4 == 0:
            for y in range(0, hz):
                for dz in (-1, 1):
                    w.setze(x, y, z + dz, w.b("spruce_log", axis="y"))
            for dz in (-1, 0, 1):
                w.setze(x, hz - 1, z + dz, w.b("stripped_spruce_log", axis="z"))
        if x % 8 == 0:
            w.setze(x, hz + 1, z + 1, w.b("spruce_fence"))
            w.setze(x, hz + 2, z + 1, w.b("lantern", hanging=False, waterlogged=False))
    ex = R - 3
    for x in range(ex - int(4 * s), R + 1):
        for z in range(-int(5 * s + 4), int(5 * s + 5)):
            if math.hypot(x, z) < R + 1:
                for y in range(1, hz + int(5 * s + 4)):
                    w.setze(x, y, z, w.b("basalt", axis="y") if (y + z) % 3 else w.b("blackstone"))
    for x in range(ex - int(4 * s) - 1, R + 1):
        for z in (-1, 0, 1):
            for y in range(hz, hz + 4):
                w.bloecke.pop((x, y, z), None)
        w.setze(x, hz, 0, w.b("spruce_planks"))
        w.setze(x, hz + 1, 0, w.b("rail", shape="east_west", waterlogged=False))
    for z in (-1, 1):
        for y in range(hz, hz + 4):
            w.setze(ex - int(4 * s) - 1, y, z, w.b("spruce_log", axis="y"))
    for z in (-1, 0, 1):
        w.setze(ex - int(4 * s) - 1, hz + 4, z, w.b("spruce_log", axis="z"))
    for k, x in enumerate((-int(R * 0.3), int(R * 0.15))):
        z = round(math.sin(x / R * 1.5) * 2)
        w.setze(x, hz + 1, z, w.b("rail", shape="east_west", waterlogged=False))
        w.setze(x, hz + 2, z, w.b("iron_block" if k else "raw_iron_block") if False else w.b("raw_gold_block"), False)
    return w


def feuerkloster(seed, g=2):
    """Feuerkloster: ein Kloster aus rotem Sandstein auf einer steilen Basaltklippe über einem Lavafluss, mit
    gestuften Pagodendächern aus Schwarzstein, Glutbecken auf den Terrassen und einer langen Felstreppe."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 4)
    H = int(8 * s + 6)
    for x in range(-R - 1, R + 2):
        for z in range(-R - 1, R + 2):
            if math.hypot(x, z) > R + rn(x, 0, z) * 2:
                continue
            fluss = abs(z - R * 0.55 - math.sin(x / 4) * 1.5) < 2 + s
            if fluss:
                w.setze(x, 0, z, w.b("lava", level=0))
                w.setze(x, -1, z, w.b("magma_block"))
                continue
            klippe = z < R * 0.35
            h = int(H + rn(x, 3, z) * 2) if klippe else int(rn(x, 4, z) * 2)
            for y in range(-2, h + 1):
                w.setze(x, y, z, w.b("basalt", axis="y") if (x * 2 + y) % 5 else w.b("tuff"))
    top = H + 1
    rs = M(w, [("red_sandstone", 2), ("cut_red_sandstone", 2), ("smooth_red_sandstone", 1)])
    for k, (B, yk) in enumerate(((int(4 * s + 4), top), (int(3 * s + 3), top + int(3 * s) + 4),
                                  (int(2 * s + 2), top + 2 * int(3 * s) + 8))):
        cz = -int(R * 0.15)
        hh = int(3 * s) + 3
        for x in range(-B, B + 1):
            for z in range(cz - B, cz + B + 1):
                rand = max(abs(x), abs(z - cz)) == B
                for y in range(yk, yk + hh):
                    if rand:
                        fen = y == yk + 1 and (x + z) % 3 == 0
                        w.setze(x, y, z, w.b("orange_stained_glass") if fen else rs(x, y, z))
                    else:
                        w.bloecke.pop((x, y, z), None)
                w.setze(x, yk - 1, z, w.b("smooth_red_sandstone"))
        for j in range(3):
            for x in range(-B - 2 + j, B + 3 - j):
                for z in range(cz - B - 2 + j, cz + B + 3 - j):
                    if max(abs(x), abs(z - cz)) == B + 2 - j:
                        w.setze(x, yk + hh + j, z, w.b("blackstone_slab", type="bottom", waterlogged=False)
                                if j == 0 else w.b("polished_blackstone_bricks"))
            if j == 2:
                for x in range(-B + j, B + 1 - j):
                    for z in range(cz - B + j, cz + B + 1 - j):
                        w.setze(x, yk + hh + j, z, w.b("polished_blackstone_bricks"))
        for sx in (-1, 1):
            for sz in (-1, 1):
                w.setze(sx * (B + 2), yk + hh, cz + sz * (B + 2), w.b("gold_block"))
    for sx in (-1, 1):
        kohlenbecken(w, sx * int(4 * s + 6), top, -int(R * 0.15) + int(4 * s + 3))
    for k in range(H + 1):
        z = int(R * 0.35) - 1 - k
        x = -int(4 * s + 4) - 2
        y = k + 1
        for dx in (0, 1):
            w.setze(x + dx, y, z, treppe(w, "polished_blackstone_brick", "south"))
            for yy in range(y + 1, y + 4):
                w.bloecke.pop((x + dx, yy, z), None)
    return w


VULKAN3 = {
    "feuersalamander": ("Feuersalamander-Statue", feuersalamander),
    "aschewald": ("Aschewald", aschewald),
    "spiegelhalle": ("Obsidian-Spiegelhalle", spiegelhalle),
    "kraterdorf": ("Kraterdorf", kraterdorf),
    "schwefelquellen": ("Schwefelquellen", schwefelquellen),
    "lavaroehre": ("Lavaröhre", lavaroehre),
    "magmawurm": ("Magmawurm", magmawurm),
    "bimssteinbruch": ("Bimsstein-Steinbruch", bimssteinbruch),
    "signalfeuerturm": ("Signalfeuer-Turm", signalfeuerturm),
    "lavafestung": ("Lavafestung", lavafestung),
    "opferaltar": ("Opferaltar am Kraterrand", opferaltar),
    "lavazunge": ("Erstarrte Lavazunge", lavazunge),
    "drachengerippe": ("Drachengerippe in der Asche", drachengerippe),
    "glutpilzhain": ("Glutpilzhain", glutpilzhain),
    "schwarzer_strand": ("Schwarzer Strand mit Hafen", schwarzer_strand),
    "feuerblumenfeld": ("Feuerblumen-Feld", feuerblumenfeld),
    "lavabrunnen": ("Lavabrunnen-Platz", lavabrunnen),
    "geschmolzene_burg": ("Geschmolzene Burg", geschmolzene_burg),
    "grubenbahn": ("Lava-Grubenbahn", grubenbahn),
    "feuerkloster": ("Feuerkloster", feuerkloster),
}

"""End-Reich II – zwanzig weitere Bauten aus dem End: Endermann-Allee, Schwebende Bibliothek, Leerenspalte,
Ringinsel, Purpurbrücken-Kreuzung, End-Kristall-Monument, Elytra-Startturm, Chorus-Irrgarten, Leerenwal, Gateway-
Ruine, Leerensee, Purpur-Leuchtturm, Enderauge-Monument, Purpur-Gassen, Schwebende Trittsteine, Drachenschädel,
Angekettete Inseln, Schwebebrunnen, Leerenwerft und Shulker-Bastion."""

from __future__ import annotations

import math

import numpy as np

from elemente2 import chorus_pflanze
from feinbau import Dachmat, Mix, kegeldach, laterne, platte, satteldach, treppe
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen
from skulptur import Skulptur, dreh_y, ell, kap, kasten, kegel, kreisrand, torus

S = [0.6, 1.0, 1.6, 2.5]


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def purpur(w):
    return M(w, [("purpur_block", 4), ("purpur_pillar", 1), ("end_stone_bricks", 1)])


def endstein(w):
    return M(w, [("end_stone", 5), ("end_stone_bricks", 1), ("obsidian", 0.4)], zelle=2.0)


def grund(w, R, cx=0, cz=0, huegel=0.5, chorus=0.0):
    rn = Rauschen(w, 6)
    e = endstein(w)
    zellen = {}
    rng = w.rng
    for x in range(cx - int(R) - 2, cx + int(R) + 3):
        for z in range(cz - int(R) - 2, cz + int(R) + 3):
            if math.hypot(x - cx, z - cz) <= R + 2 * rn(x, 0, z):
                h = int(huegel * 2 * rn(x * 0.7, 3, z * 0.7))
                for y in range(-2, h + 1):
                    w.setze(x, y, z, e(x, y, z))
                zellen[(x, z)] = h
                if rng.random() < chorus:
                    chorus_pflanze(w, x, h + 1, z, int(2 + rng.random() * 4))
    return zellen


def insel(w, R, cx=0, cz=0, yo=10, tiefe=None, chorus=0.0):
    """Schwebende Endstein-Insel mit zerklüfteter Unterseite; gibt die Oberkante zurück."""
    rn = Rauschen(w, 4)
    e = endstein(w)
    tiefe = tiefe or R * 0.9
    rng = w.rng
    for x in range(int(cx - R) - 2, int(cx + R) + 3):
        for z in range(int(cz - R) - 2, int(cz + R) + 3):
            d = math.hypot(x - cx, z - cz) / R
            if d > 1 + 0.15 * rn(x, 0, z):
                continue
            unter = yo - (1 - min(1, d) ** 1.4) * tiefe * (0.6 + 0.6 * rn(x, 5, z))
            for y in range(int(unter), yo + 1):
                w.setze(x, y, z, e(x, y, z))
            if rng.random() < chorus:
                chorus_pflanze(w, x, yo + 1, z, int(2 + rng.random() * 3))
    return yo


def figur(w, u, teile, lo, hi, pos=(0, 0, 0), winkel=0.0):
    Sk = Skulptur(w, u)
    for i, (form, blk) in enumerate(teile):
        if blk is None:
            Sk.minus(form)
            continue
        Sk.mat(str(i), blk)
        Sk.plus(form, str(i))
    Sk.rendern(lo, hi, versatz=(pos[0] + 0.5, pos[1], pos[2] + 0.5), dreh=dreh_y(winkel))


def enderman(w):
    s = w.b("black_concrete")
    a = w.b("magenta_concrete")
    return [(kasten(-0.65, 0, -0.3, -0.1, 7, 0.3), s), (kasten(0.1, 0, -0.3, 0.65, 7, 0.3), s),
            (kasten(-0.85, 7, -0.45, 0.85, 10, 0.45), s), (kasten(-1.45, 5.6, -0.3, -0.85, 10, 0.3), s),
            (kasten(0.85, 5.6, -0.3, 1.45, 10, 0.3), s), (kasten(-0.9, 10, -0.9, 0.9, 11.8, 0.9), s),
            (kasten(-0.7, 10.6, 0.8, -0.15, 11.0, 0.95), a), (kasten(0.15, 10.6, 0.8, 0.7, 11.0, 0.95), a)]


# ============================================================================ Bauten

def endermann_allee(seed, g=2):
    """Endermann-Allee: ein Weg aus Endsteinziegeln, gesäumt von zwei Reihen hoher, schwarzer Endermann-Statuen
    mit violett glühenden Augen auf Obsidiansockeln, am Ende ein Portalbogen aus Purpur."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    grund(w, R, huegel=0.3)
    L = int(R * 0.85)
    for z in range(-L, L + 1):
        for x in range(-2, 3):
            w.setze(x, 0, z, w.b("end_stone_bricks" if (x + z) % 3 else "purpur_block"))
    n = int(3 + 2 * s)
    for i in range(n):
        z = -L + 2 + round(i * (2 * L - 6) / max(1, n - 1))
        for sx in (-1, 1):
            x = sx * 5
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    w.setze(x + dx, 1, z + dz, w.b("obsidian"))
            figur(w, 0.7 * s + 0.5, enderman(w), (-2, -1, -2), (2, 13, 2), pos=(x, 2, z),
                  winkel=math.pi / 2 * -sx)
    H = int(8 * s + 6)
    for sx in (-1, 1):
        for y in range(1, H):
            for dz in (0, 1):
                w.setze(sx * 3, y, L + dz, w.b("purpur_pillar", axis="y"))
    for x in range(-3, 4):
        w.setze(x, H, L, w.b("purpur_block"))
        w.setze(x, H, L + 1, w.b("purpur_block"))
    w.setze(0, H + 1, L, w.b("end_rod", facing="up"))
    return w


def schwebende_bibliothek(seed, g=2):
    """Schwebende Bibliothek: ein Lesesaal aus Purpur auf einer Endstein-Insel, umkreist von kleinen schwebenden
    Bücherregal-Inseln, verbunden durch schmale Stege; Endstäbe als Leselampen."""
    w = _neu(seed)
    s = S[g]
    yo = int(10 * s + 6)
    R = 6 * s + 4
    insel(w, R, 0, 0, yo)
    p = purpur(w)
    B = int(3 * s + 3)
    H = int(3 * s + 4)
    for x in range(-B, B + 1):
        for z in range(-B, B + 1):
            rand = max(abs(x), abs(z)) == B
            for y in range(yo + 1, yo + H + 1):
                if rand:
                    fen = y in (yo + 2, yo + 3) and (x + z) % 3 == 0 and not (abs(x) == B and abs(z) == B)
                    w.setze(x, y, z, w.b("magenta_stained_glass") if fen else p(x, y, z))
                elif max(abs(x), abs(z)) == B - 1 and y < yo + H - 1 and (x + z) % 4:
                    w.setze(x, y, z, w.b("bookshelf"))
                else:
                    w.bloecke.pop((x, y, z), None)
    kegeldach(w, 0, 0, yo + H + 1, B, Dachmat(w, ["purpur", "end_stone_brick"]), form="glocke", eckig=True,
              spitze="end_rod")
    for y in (yo + 1, yo + 2):
        w.bloecke.pop((0, y, B), None)
    w.setze(0, yo + 1, 0, w.b("lectern", facing="south", has_book=True, powered=False))
    rng = w.rng
    n = 4 + g
    for i in range(n):
        a = i / n * 2 * math.pi + 0.3
        d = R + 4 + 3 * s
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        y = yo + int((rng.random() - 0.3) * 6 * s)
        insel(w, 2 + s * 0.8, cx, cz, y, tiefe=3 + s)
        for k in range(2 + int(s)):
            w.setze(cx, y + 1 + k, cz, w.b("bookshelf"))
            w.setze(cx + 1, y + 1 + k, cz, w.b("bookshelf"))
        w.setze(cx, y + 3 + int(s), cz + 1, w.b("end_rod", facing="up"))
        for k in range(1, 12):
            t = k / 12
            x = round(cx * (1 - t))
            z = round(cz * (1 - t))
            yy = round(y + (yo - y) * t)
            if math.hypot(x, z) > R:
                w.setze(x, yy, z, w.b("purpur_slab", type="bottom", waterlogged=False))
    return w


def leerenspalte(seed, g=2):
    """Leerenspalte: ein klaffender Riss im Endsteinboden, an dessen Kanten Obsidian glänzt; aus der Tiefe steigen
    schwebende Splitter auf, zwei Brücken aus Purpurplatten überspannen den Abgrund."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    rn = Rauschen(w, 5)
    e = endstein(w)
    D = int(8 * s + 6)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            mitte = math.sin(x / (5 * s + 3)) * 2 * s
            breite = (2.0 + 1.5 * s) * (1 - (x / (R + 2)) ** 2) + rn(x, 2, 0) * 2
            dz = abs(z - mitte)
            if dz < breite:
                continue
            unten = -D if dz < breite + 2 else -2
            for y in range(unten, 1):
                kante = dz < breite + 1.2
                w.setze(x, y, z, w.b("obsidian") if kante and y > -3 else w.b("crying_obsidian") if kante and
                        (x + y) % 5 == 0 else e(x, y, z))
    rng = w.rng
    for _ in range(int(14 * s + 6)):
        x = int((rng.random() - 0.5) * R * 1.4)
        z = round(math.sin(x / (5 * s + 3)) * 2 * s + (rng.random() - 0.5) * 3)
        y = int(-D + rng.random() * (D + 6 * s))
        kugel(w, x, y, z, 0.6 + rng.random() * s * 0.8, w.b("obsidian" if rng.random() < 0.6 else "end_stone"),
              ueber=False)
    for bx in (-int(R * 0.4), int(R * 0.3)):
        mitte = math.sin(bx / (5 * s + 3)) * 2 * s
        for z in range(round(mitte - 3 - 2 * s), round(mitte + 4 + 2 * s)):
            for dx in (0, 1):
                w.setze(bx + dx, 0, z, w.b("purpur_slab", type="bottom", waterlogged=False), False)
    return w


def ringinsel(seed, g=2):
    """Ringinsel: ein Atoll aus Endstein, das ein rundes, tiefschwarzes Becken umschließt; auf dem Ring stehen
    Obsidiansäulen mit Endstäben, in der Mitte schwebt ein Kristall über dem Dunkel."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 4)
    e = endstein(w)
    ri = R * 0.55
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 2 * rn(x, 0, z):
                continue
            if d < ri:
                w.setze(x, -1, z, w.b("black_concrete"))
                w.setze(x, -2, z, w.b("obsidian"))
                continue
            h = int(3 * s * math.sin(math.pi * min(1, (d - ri) / (R - ri))) + rn(x, 3, z) * 2)
            for y in range(-2, h + 1):
                w.setze(x, y, z, e(x, y, z))
    n = 6 + 2 * g
    for i in range(n):
        a = i / n * 2 * math.pi
        x, z = round(math.cos(a) * (ri + (R - ri) * 0.5)), round(math.sin(a) * (ri + (R - ri) * 0.5))
        top = max(y for y in range(-2, 20) if not w.frei(x, y, z))
        H = int((4 + (i % 3) * 2) * s + 2)
        for y in range(top + 1, top + H):
            w.setze(x, y, z, w.b("obsidian"))
        w.setze(x, top + H, z, w.b("end_rod", facing="up"))
    yk = int(5 * s + 4)
    for y in range(-int(2 * s + 1), int(2 * s + 2)):
        r = (1.4 * s + 1) * (1 - abs(y) / (2 * s + 1.5))
        for x in range(-3, 4):
            for z in range(-3, 4):
                if abs(x) + abs(z) <= r:
                    w.setze(x, yk + y, z, w.b("purple_stained_glass") if abs(x) + abs(z) > r - 1 else
                            w.b("end_rod", facing="up") if y == 0 else w.b("amethyst_block"))
    return w


def brueckenkreuz(seed, g=2):
    """Purpurbrücken-Kreuzung: vier schwebende Pfeilerinseln mit kleinen Purpurtürmen, verbunden durch
    elegante Bogenbrücken mit Geländern, die sich auf einer Mittelplattform treffen."""
    w = _neu(seed)
    s = S[g]
    yo = int(8 * s + 6)
    D = 10 * s + 6
    p = purpur(w)
    r0 = 2.5 * s + 2
    insel(w, r0 + 1, 0, 0, yo, tiefe=4 * s + 3)
    for x in range(-int(r0), int(r0) + 1):
        for z in range(-int(r0), int(r0) + 1):
            w.setze(x, yo + 1, z, w.b("purpur_block" if (x + z) % 2 else "end_stone_bricks"))
    w.setze(0, yo + 2, 0, w.b("end_rod", facing="up"))
    for i in range(4):
        a = i * math.pi / 2
        cx, cz = round(math.cos(a) * D), round(math.sin(a) * D)
        ri = 2.5 * s + 2
        insel(w, ri, cx, cz, yo, tiefe=6 * s + 4)
        th = int(6 * s + 5)
        for y in range(yo + 1, yo + th):
            for x, z in kreisrand(1.4 + 0.5 * s, cx, cz):
                w.setze(x, y, z, p(x, y, z) if (y - yo) % 4 else w.b("end_stone_bricks"))
        kegeldach(w, cx, cz, yo + th, int(1.4 + 0.5 * s), Dachmat(w, ["purpur", "end_stone_brick"]), form="nadel",
                  spitze="end_rod")
        L = int(D)
        for k in range(L + 1):
            t = k / L
            x = round(cx * t)
            z = round(cz * t)
            yy = yo + 1 + round(math.sin(math.pi * t) * 2 * s)
            tx, tz = (0, 1) if i % 2 == 0 else (1, 0)
            for q in (-1, 0, 1):
                w.setze(x + tx * q, yy, z + tz * q, w.b("purpur_block"), False)
            for q in (-2, 2):
                w.setze(x + tx * q, yy + 1, z + tz * q, w.b("end_stone_brick_wall"), False)
            w.setze(x, yy - 1, z, w.b("purpur_stairs", facing="north", half="top", shape="straight",
                                      waterlogged=False), False)
    return w


def kristallmonument(seed, g=2):
    """End-Kristall-Monument: ein riesiger, schräg gestellter Würfel aus violettem Glas mit Grundgestein-Kern auf
    einer gestuften Obsidiansäule, umringt von Eisenstäben und schwebenden Lichtringen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    grund(w, R, huegel=0.3)
    H = int(10 * s + 6)
    for y in range(1, H):
        r = (2.5 * s + 2) * (1 - 0.4 * y / H)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                if max(abs(x), abs(z)) <= r:
                    w.setze(x, y, z, w.b("obsidian" if (y % 5) else "crying_obsidian"))
    yc = H + int(3 * s + 3)
    a = 2.6 * s + 2
    from skulptur import dreh_x, dreh_z
    Sk = Skulptur(w, 1.0)
    Sk.mat("g", w.b("magenta_stained_glass"))
    Sk.mat("k", w.b("bedrock"))
    Sk.mat("i", w.b("purple_stained_glass"))
    Sk.plus(kasten(-a, -a, -a, a, a, a), "g")
    Sk.minus(kasten(-a + 1, -a + 1, -a + 1, a - 1, a - 1, a - 1))
    Sk.plus(kasten(-a * 0.6, -a * 0.6, -a * 0.6, a * 0.6, a * 0.6, a * 0.6), "i")
    Sk.minus(kasten(-a * 0.6 + 1, -a * 0.6 + 1, -a * 0.6 + 1, a * 0.6 - 1, a * 0.6 - 1, a * 0.6 - 1))
    Sk.plus(kasten(-a * 0.3, -a * 0.3, -a * 0.3, a * 0.3, a * 0.3, a * 0.3), "k")
    Sk.rendern((-a * 1.8, -a * 1.8, -a * 1.8), (a * 1.8, a * 1.8, a * 1.8), versatz=(0.5, yc, 0.5),
               dreh=dreh_x(0.6) @ dreh_z(0.62))
    for i in range(4):
        aa = i * math.pi / 2 + math.pi / 4
        for k in range(int(a * 1.6) + 2):
            x, z = round(math.cos(aa) * (a * 1.6 + 1)), round(math.sin(aa) * (a * 1.6 + 1))
            w.setze(x, H + k - 2, z, w.b("iron_bars", waterlogged=False))
    for k, rr in enumerate((a * 2.2, a * 2.8)):
        for x, z in kreisrand(rr):
            if (x + z) % 3 == 0:
                w.setze(x, yc - 2 + k * 4, z, w.b("end_rod", facing="up"))
    return w


def elytra_turm(seed, g=2):
    """Elytra-Startturm: ein schlanker Turm aus Endsteinziegeln mit Wendeltreppe außen herum, oben eine
    vorkragende Sprungplattform mit violetten Bannern und Leuchtstäben, unten ein Landefeld mit Heuballen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    grund(w, R, huegel=0.2)
    H = int(22 * s + 12)
    r = 1.8 * s + 1.5
    for y in range(1, H):
        for x, z in kreisrand(r):
            w.setze(x, y, z, w.b("end_stone_bricks") if y % 6 else w.b("purpur_block"))
    for k in range(H * 3):
        ang = k / 3 * 0.35
        y = 1 + k // 3
        if y >= H:
            break
        x, z = round(math.cos(ang) * (r + 1)), round(math.sin(ang) * (r + 1))
        w.setze(x, y, z, w.b("purpur_slab", type="top", waterlogged=False), False)
    P = int(r + 2)
    for x in range(-P, P + 1):
        for z in range(-P, P + 1):
            if math.hypot(x, z) <= P + 0.3:
                w.setze(x, H, z, w.b("purpur_block"))
    for k in range(1, int(5 * s + 4)):
        for x in (-1, 0, 1):
            w.setze(x, H, P + k, w.b("purpur_slab", type="bottom", waterlogged=False))
    for x, z in kreisrand(P):
        if (x + z) % 3 == 0:
            w.setze(x, H + 1, z, w.b("end_rod", facing="up"))
    for i in range(4):
        aa = i * math.pi / 2
        x, z = round(math.cos(aa) * (P - 1)), round(math.sin(aa) * (P - 1))
        for y in range(H + 1, H + 5):
            w.setze(x, y, z, w.b("end_stone_brick_wall"))
        for y in range(H + 2, H + 5):
            w.setze(x + (1 if x >= 0 else -1) * (0 if abs(z) > abs(x) else 0), y, z + 1 if abs(x) > abs(z) else z,
                    w.b("purple_wool"))
    lx = int(R * 0.5)
    for x in range(lx - 2, lx + 3):
        for z in range(-2, 3):
            w.setze(x, 1, z, w.b("hay_block", axis="y"))
    return w


def chorus_irrgarten(seed, g=1):
    """Chorus-Irrgarten: ein Labyrinth, dessen Wände aus dicht verwachsenen Chorus-Pflanzen auf Endsteinziegel-
    Sockeln bestehen, in der Mitte ein Pavillon aus Purpur mit Chorusblüten."""
    w = _neu(seed)
    s = S[g]
    n = 5 + 2 * g
    zelle = 3
    R = n * zelle // 2 + 3
    grund(w, R + 2, huegel=0.0)
    rng = w.rng
    besucht = {(0, 0)}
    stapel = [(0, 0)]
    offen = set()
    while stapel:
        cx, cz = stapel[-1]
        nb = [(cx + dx, cz + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= cx + dx < n and 0 <= cz + dz < n and (cx + dx, cz + dz) not in besucht]
        if not nb:
            stapel.pop()
            continue
        nx, nz = nb[int(rng.integers(len(nb)))]
        offen.add(frozenset(((cx, cz), (nx, nz))))
        besucht.add((nx, nz))
        stapel.append((nx, nz))
    x0 = -n * zelle // 2
    H = int(2 * s + 2)
    for i in range(n * zelle + 1):
        for j in range(n * zelle + 1):
            ci, ri = divmod(i, zelle)
            cj, rj = divmod(j, zelle)
            if ri == 0 and rj == 0:
                wand = True
            elif ri == 0:
                wand = not (0 < ci < n and frozenset(((ci - 1, cj), (ci, cj))) in offen)
            elif rj == 0:
                wand = not (0 < cj < n and frozenset(((ci, cj - 1), (ci, cj))) in offen)
            else:
                wand = False
            x, z = x0 + i, x0 + j
            if wand and not (j == 0 and abs(i - n * zelle // 2) <= 1):
                w.setze(x, 1, z, w.b("end_stone_bricks"))
                for y in range(2, H + 2):
                    w.setze(x, y, z, w.b("chorus_plant", up=y < H + 1, down=True, north=True, south=True, east=True,
                                         west=True))
                if rng.random() < 0.25:
                    w.setze(x, H + 2, z, w.b("chorus_flower", age=int(rng.integers(2, 6))))
            else:
                w.setze(x, 0, z, w.b("purpur_block" if (i + j) % 2 else "end_stone_bricks"))
    m = x0 + (n // 2) * zelle + zelle // 2
    for dx in (-1, 1):
        for dz in (-1, 1):
            for y in range(1, 4):
                w.setze(m + dx, y, m + dz, w.b("purpur_pillar", axis="y"))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(m + dx, 4, m + dz, w.b("purpur_slab", type="bottom", waterlogged=False))
    w.setze(m, 1, m, w.b("end_rod", facing="up"))
    return w


def leerenwal(seed, g=2):
    """Leerenwal: ein gewaltiger, schwebender Wal aus Obsidian und Purpur mit violetten Leuchtflecken, langen
    Brustflossen und einer kleinen Purpurstadt auf dem Rücken, die er durch die Leere trägt."""
    w = _neu(seed)
    s = S[g]
    u = 1.0 * s + 0.6
    yo = int(6 * u + 4)
    o = w.b("obsidian")
    hell = w.b("end_stone")
    lp = w.b("magenta_stained_glass")
    teile = [(ell(0, 0, 0, 10, 3.2, 3.6), o), (ell(4, -0.8, 0, 6, 2.2, 3.0), hell),
             (kap((-9, 0.3, 0), (-14, 1.6, 0), 2.2, 0.8), o),
             (lambda X, Y, Z: ((X + 15) ** 2 / 2.0 + (Y - 1.8) ** 2 / 0.4 + Z ** 2 / 12 <= 1), o),
             (kap((3, -1.5, 2.8), (0, -3.5, 7), 0.9, 0.5), o), (kap((3, -1.5, -2.8), (0, -3.5, -7), 0.9, 0.5), o),
             (ell(7.5, 0.8, 2.5, 0.5, 0.5, 0.4), w.b("purple_concrete")),
             (ell(7.5, 0.8, -2.5, 0.5, 0.5, 0.4), w.b("purple_concrete"))]
    for i in range(7):
        teile.append((ell(-6 + i * 2, 2.6 - abs(i - 3) * 0.2, (i % 2 - 0.5) * 2.2, 0.5, 0.35, 0.5), lp))
    figur(w, u, teile, (-17, -5, -8), (11, 5, 8), pos=(0, yo, 0), winkel=0.3)
    top = yo + round(3.0 * u)
    p = purpur(w)
    for k, (dx, h) in enumerate(((-3, 3), (0, 5), (3, 2))):
        x = round(dx * u * 0.9 * math.cos(0.3))
        z = round(-dx * u * 0.9 * math.sin(0.3))
        for y in range(top - 1, top + int(h * s) + 1):
            for xx in (x, x + 1):
                for zz in (z, z + 1):
                    w.setze(xx, y, zz, p(xx, y, zz))
        w.setze(x, top + int(h * s) + 1, z, w.b("end_rod", facing="up"))
    return w


def gateway_ruine(seed, g=2):
    """Gateway-Ruine: ein zerborstener Rahmen aus Grundgestein-artigem Gestein um ein schwarzes Tor, umgeben von
    abgesprengten Brocken und Lichtfäden, als sei hier einst ein Tor zu fernen Inseln gewesen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    grund(w, R, huegel=0.4)
    a = int(2 * s + 2)
    yc = int(5 * s + 5)
    rng = w.rng
    for x in range(-a - 1, a + 2):
        for y in range(-a - 1, a + 2):
            for z in range(-a - 1, a + 2):
                m = max(abs(x), abs(y), abs(z))
                if m == a + 1 and (abs(x) + abs(y) + abs(z)) <= 2 * a + 2 and rng.random() < 0.82:
                    w.setze(x, yc + y, z, w.b("bedrock"))
                elif m <= a - 1 and abs(x) + abs(z) <= a:
                    w.setze(x, yc + y, z, w.b("black_concrete") if y else w.b("end_gateway") if False else
                            w.b("black_concrete"))
    for y in range(1, yc - a):
        w.setze(0, y, 0, w.b("bedrock"))
    for _ in range(int(10 * s + 5)):
        x, y, z = (rng.random() - 0.5) * R * 1.2, 1 + rng.random() * yc * 1.6, (rng.random() - 0.5) * R * 1.2
        kugel(w, x, y, z, 0.6 + rng.random() * s, w.b("bedrock" if rng.random() < 0.5 else "obsidian"), ueber=False)
    for i in range(6):
        aa = i / 6 * 2 * math.pi
        for k in range(int(R * 0.5)):
            x, z = round(math.cos(aa) * (a + 3 + k)), round(math.sin(aa) * (a + 3 + k))
            if k % 3 == 0:
                w.setze(x, 1, z, w.b("end_rod", facing="up"), False)
    return w


def leerensee(seed, g=2):
    """Leerensee: ein spiegelglatter, schwarzer See in einer Endstein-Senke, aus dem schlanke Obsidiannadeln mit
    violetten Spitzen ragen; ein Steg aus Purpur führt zu einem Pavillon in der Mitte."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = grund(w, R, huegel=0.4)
    rn = Rauschen(w, 5)
    rs = R * 0.65
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z * 1.2) < rs + rn(x, 3, z) * 3:
                for y in range(0, 4):
                    w.bloecke.pop((x, y, z), None)
                w.setze(x, -1, z, w.b("black_stained_glass"))
                w.setze(x, -2, z, w.b("obsidian"))
    rng = w.rng
    for _ in range(int(6 * s + 4)):
        a = rng.random() * 6.28
        d = rs * (0.3 + rng.random() * 0.6)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d / 1.2)
        H = int((4 + rng.random() * 8) * s)
        for y in range(-1, H):
            w.setze(x, y, z, w.b("obsidian"))
        w.setze(x, H, z, w.b("amethyst_block"))
        w.setze(x, H + 1, z, w.b("amethyst_cluster", facing="up", waterlogged=False))
    for z in range(0, int(rs / 1.2) + 4):
        for x in (-1, 0, 1):
            w.setze(x, 0, z, w.b("purpur_slab", type="bottom", waterlogged=False))
    for x, z in kreisrand(2.5):
        for y in range(0, 4):
            w.setze(x, y, z, w.b("purpur_pillar", axis="y") if (x + z) % 2 else w.b("air"))
    for x in range(-3, 4):
        for z in range(-3, 4):
            if math.hypot(x, z) <= 3.2:
                w.setze(x, 0, z, w.b("purpur_block"))
                w.setze(x, 4, z, w.b("purpur_slab", type="bottom", waterlogged=False))
    w.setze(0, 5, 0, w.b("end_rod", facing="up"))
    _ = zellen
    return w


def purpur_leuchtturm(seed, g=2):
    """Purpur-Leuchtturm: ein Leuchtturm aus gebänderten Purpur- und Endsteinringen auf einer Klippeninsel,
    mit Glaskammer voller Endstäbe und einem Galeriering, darunter eine Wärterhütte."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    yo = int(4 * s + 4)
    insel(w, R * 0.8, 0, 0, yo, tiefe=8 * s + 6)
    H = int(16 * s + 10)
    for y in range(yo + 1, yo + H):
        r = (2.2 * s + 1.6) * (1 - 0.25 * (y - yo) / H)
        for x, z in kreisrand(r):
            w.setze(x, y, z, w.b("purpur_block" if ((y - yo) // 3) % 2 else "end_stone_bricks"))
    top = yo + H
    rg = 2.2 * s + 2
    for x in range(-int(rg) - 1, int(rg) + 2):
        for z in range(-int(rg) - 1, int(rg) + 2):
            if math.hypot(x, z) <= rg:
                w.setze(x, top, z, w.b("purpur_block"))
            if abs(math.hypot(x, z) - rg) < 0.6:
                w.setze(x, top + 1, z, w.b("end_stone_brick_wall"))
    for y in range(top + 1, top + int(3 * s + 3)):
        for x, z in kreisrand(rg - 1.2):
            w.setze(x, y, z, w.b("magenta_stained_glass"))
    for y in range(top + 1, top + int(3 * s + 2)):
        w.setze(0, y, 0, w.b("end_rod", facing="up"))
    kegeldach(w, 0, 0, top + int(3 * s + 3), int(rg - 1), Dachmat(w, ["purpur"]), form="kegel", spitze="end_rod")
    hx = int(R * 0.45)
    for x in range(hx - 2, hx + 3):
        for z in range(-2, 3):
            for y in range(yo + 1, yo + 4):
                if abs(x - hx) == 2 or abs(z) == 2:
                    w.setze(x, y, z, w.b("end_stone_bricks"))
    satteldach(w, hx - 2, -2, hx + 2, 2, yo + 4, Dachmat(w, ["purpur"]), first_x=True, ue=1,
               giebel=purpur(w), traufe="warped")
    return w


def enderauge(seed, g=2):
    """Enderauge-Monument: ein riesiges Enderauge aus grünem und dunkelgrünem Gestein mit schwarzer Pupille
    schwebt in einem Ring aus Obsidian über einem gestuften Sockel aus Endsteinziegeln."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    grund(w, R, huegel=0.2)
    for k in range(3):
        a = int(5 * s + 4) - k * 2
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                w.setze(x, 1 + k, z, w.b("end_stone_bricks" if (x + z) % 2 else "purpur_block"))
    rk = 3.5 * s + 2.5
    yc = 3 + int(rk) + int(3 * s + 2)
    for x in range(-int(rk) - 1, int(rk) + 2):
        for y in range(-int(rk) - 1, int(rk) + 2):
            for z in range(-int(rk) - 1, int(rk) + 2):
                d = math.sqrt(x * x + y * y + z * z)
                if d <= rk:
                    pup = z > rk * 0.55 and abs(x) < rk * 0.25 and abs(y) < rk * 0.5
                    iris = z > rk * 0.5 and math.hypot(x, y) < rk * 0.7
                    b = "black_concrete" if pup else "lime_terracotta" if iris else \
                        "green_terracotta" if (x + y + z) % 3 else "emerald_block"
                    w.setze(x, yc + y, z, w.b(b))
    for x, y in [(x, y) for x in range(-int(rk) - 3, int(rk) + 4) for y in range(-int(rk) - 3, int(rk) + 4)]:
        if abs(math.hypot(x, y) - (rk + 2)) < 0.7:
            w.setze(x, yc + y, 0, w.b("obsidian"))
    for y in range(4, yc - int(rk) - 1):
        w.setze(0, y, 0, w.b("obsidian"))
    return w


def purpur_gassen(seed, g=2):
    """Purpur-Gassen: ein Viertel aus schmalen, hohen Purpurhäusern mit spitzen Dächern, Brückenstegen zwischen
    den Obergeschossen, Endstab-Laternen und einem kleinen Platz mit Chorusbaum."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    grund(w, R, huegel=0.0)
    p = purpur(w)
    rng = w.rng
    haeuser = []
    for gx in range(-2, 3):
        for gz in range(-2, 3):
            if abs(gx) + abs(gz) == 0 or rng.random() < 0.25:
                continue
            cx, cz = round(gx * (4 * s + 3)), round(gz * (4 * s + 3))
            if math.hypot(cx, cz) > R - 3:
                continue
            B = int(1.5 * s + 2)
            H = int((3 + rng.random() * 4) * s + 4)
            for x in range(cx - B, cx + B + 1):
                for z in range(cz - B, cz + B + 1):
                    for y in range(1, H + 1):
                        rand = max(abs(x - cx), abs(z - cz)) == B
                        if rand:
                            fen = y % 4 == 2 and (x + z) % 2 == 0
                            w.setze(x, y, z, w.b("magenta_stained_glass") if fen else p(x, y, z))
            kegeldach(w, cx, cz, H + 1, B, Dachmat(w, ["purpur", "end_stone_brick"]), form="nadel", eckig=True,
                      spitze="end_rod")
            w.bloecke.pop((cx, 1, cz + B), None)
            w.bloecke.pop((cx, 2, cz + B), None)
            haeuser.append((cx, cz, H))
    for (a, b) in zip(haeuser, haeuser[1:]):
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) > 12 * s:
            continue
        y = min(a[2], b[2]) - 2
        n = int(max(abs(a[0] - b[0]), abs(a[1] - b[1])))
        for k in range(n + 1):
            t = k / max(1, n)
            w.setze(round(a[0] + (b[0] - a[0]) * t), y, round(a[1] + (b[1] - a[1]) * t),
                    w.b("purpur_slab", type="bottom", waterlogged=False), False)
    chorus_pflanze(w, 0, 1, 0, int(4 + 2 * s))
    for x, z in ((2, 2), (-2, -2)):
        w.setze(x, 1, z, w.b("end_rod", facing="up"))
    return w


def trittsteine(seed, g=2):
    """Schwebende Trittsteine: eine aufsteigende Kette kleiner Endstein-Inseln mit Purpurplatten führt in einer
    Spirale zu einem Aussichtspavillon auf einer hohen Insel; Endstäbe markieren den Weg."""
    w = _neu(seed)
    s = S[g]
    n = int(10 + 5 * s)
    Rs = 7 * s + 5
    for i in range(n):
        t = i / n
        a = t * 2.4 * math.pi
        x, z = round(math.cos(a) * Rs), round(math.sin(a) * Rs)
        y = round(2 + t * (14 * s + 6))
        insel(w, 1.3 + 0.4 * s, x, z, y, tiefe=2 + s)
        w.setze(x, y + 1, z, w.b("purpur_slab", type="bottom", waterlogged=False))
        if i % 3 == 0:
            w.setze(x + 1, y + 1, z, w.b("end_rod", facing="up"))
    yt = round(2 + 14 * s + 8)
    insel(w, 3 + 1.5 * s, 0, 0, yt, tiefe=6 * s + 4, chorus=0.03)
    for x, z in kreisrand(2 + s):
        for y in range(yt + 1, yt + 4):
            if (x + z) % 2 == 0:
                w.setze(x, y, z, w.b("purpur_pillar", axis="y"))
    kegeldach(w, 0, 0, yt + 4, int(2 + s), Dachmat(w, ["purpur"]), form="glocke", spitze="end_rod")
    grund(w, Rs + 3, huegel=0.0)
    return w


def drachenschaedel(seed, g=2):
    """Drachenschädel: der riesige, schwarze Schädel eines Enderdrachen liegt mit offenem Maul im Endstein, die
    Augenhöhlen glühen violett, Hörner ragen nach hinten; rundherum zerfallene Obsidiansäulen."""
    w = _neu(seed)
    s = S[g]
    u = 1.0 * s + 0.5
    R = int(9 * u + 6)
    grund(w, R, huegel=0.3)
    sch = w.b("black_concrete")
    ob = w.b("obsidian")
    vi = w.b("magenta_concrete")
    teile = [(ell(0, 4, 0, 4.5, 3.5, 3.6), sch), (kasten(2.5, 2.5, -2.4, 9.5, 5.0, 2.4), sch),
             (kasten(2.5, 0.0, -2.2, 9.0, 1.6, 2.2), ob), (kasten(3, 1.6, -1.8, 9.2, 2.6, 1.8), None),
             (ell(3.2, 5.8, 1.9, 0.9, 0.7, 0.6), vi), (ell(3.2, 5.8, -1.9, 0.9, 0.7, 0.6), vi),
             (kap((-2, 6.5, 1.8), (-7, 9, 3.2), 0.9, 0.2), ob), (kap((-2, 6.5, -1.8), (-7, 9, -3.2), 0.9, 0.2), ob),
             (kap((-3.5, 4.5, 2.5), (-7.5, 5, 4.5), 0.6, 0.15), ob),
             (kap((-3.5, 4.5, -2.5), (-7.5, 5, -4.5), 0.6, 0.15), ob)]
    for k in range(5):
        teile.append((kegel(4 + k * 1.2, 2.0, 1.6, 2.6, 0.3, 0.05), w.b("white_concrete")))
        teile.append((kegel(4 + k * 1.2, -2.0, 1.6, 2.6, 0.3, 0.05), w.b("white_concrete")))
    figur(w, u, teile, (-9, -1, -6), (11, 11, 6), pos=(0, 0, 0), winkel=0.4)
    rng = w.rng
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8)
        h = int((2 + rng.random() * 6) * s)
        for y in range(1, h):
            for dx in (0, 1):
                for dz in (0, 1):
                    if rng.random() < 0.9:
                        w.setze(x + dx, y, z + dz, w.b("obsidian"))
    return w


def angekettete_inseln(seed, g=2):
    """Angekettete Inseln: drei schwebende Endstein-Inseln mit Purpurhäuschen, durch schwere Ketten miteinander
    und mit Ankerpfeilern am Boden verbunden, damit sie nicht davontreiben."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    grund(w, R, huegel=0.2)
    p = purpur(w)
    pos = []
    for i in range(3):
        a = i / 3 * 2 * math.pi + 0.5
        cx, cz = round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)
        yo = int((8 + i * 3) * s + 6)
        ri = 3 * s + 2
        insel(w, ri, cx, cz, yo, tiefe=5 * s + 3, chorus=0.02)
        B = int(1.2 * s + 1.5)
        for x in range(cx - B, cx + B + 1):
            for z in range(cz - B, cz + B + 1):
                for y in range(yo + 1, yo + 4):
                    if max(abs(x - cx), abs(z - cz)) == B:
                        w.setze(x, y, z, p(x, y, z))
        kegeldach(w, cx, cz, yo + 4, B, Dachmat(w, ["purpur"]), form="kegel", eckig=True, spitze="end_rod")
        pos.append((cx, yo, cz))
        ax, az = round(cx * 1.7), round(cz * 1.7)
        for y in range(1, 4):
            w.setze(ax, y, az, w.b("obsidian"))
        for k in range(1, 20):
            t = k / 20
            x = round(ax + (cx - ax) * t)
            z = round(az + (cz - az) * t)
            y = round(3 + (yo - 3 - 3 * s) * t - 2 * math.sin(math.pi * t))
            w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False), False)
    for (a, b) in zip(pos, pos[1:] + pos[:1]):
        for k in range(1, 20):
            t = k / 20
            x = round(a[0] + (b[0] - a[0]) * t)
            z = round(a[2] + (b[2] - a[2]) * t)
            y = round(a[1] + (b[1] - a[1]) * t - 3 * s * math.sin(math.pi * t)) - 1
            w.setze(x, y, z, w.b("chain", axis="x", waterlogged=False), False)
    return w


def schwebebrunnen(seed, g=1):
    """Schwebebrunnen: ein rundes Becken aus Purpur, aus dem statt Wasser eine Säule schwebender Endstein- und
    Obsidianwürfel spiralförmig aufsteigt, gekrönt von einem Ring aus Endstäben."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    grund(w, R, huegel=0.1)
    rb = 4 * s + 3
    for x in range(-int(rb) - 1, int(rb) + 2):
        for z in range(-int(rb) - 1, int(rb) + 2):
            d = math.hypot(x, z)
            if d <= rb:
                w.setze(x, 0, z, w.b("black_concrete" if d < rb - 1 else "purpur_block"))
                if d > rb - 1:
                    w.setze(x, 1, z, w.b("purpur_slab", type="bottom", waterlogged=False))
    H = int(14 * s + 8)
    n = int(16 * s + 10)
    rng = w.rng
    for i in range(n):
        t = i / n
        a = t * 5 * math.pi
        r = 1.0 + t * 2.5 * s
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        y = 2 + round(t * H)
        c = 1 + int(s * 0.7)
        for dx in range(c):
            for dy in range(c):
                for dz in range(c):
                    w.setze(x + dx, y + dy, z + dz, w.b(["end_stone", "obsidian", "purpur_block", "amethyst_block"][i % 4]))
        _ = rng
    for x, z in kreisrand(2.5 * s + 2.5):
        if (x + z) % 2 == 0:
            w.setze(x, H + 4, z, w.b("end_rod", facing="up"))
    return w


def leerenwerft(seed, g=2):
    """Leerenwerft: ein halbfertiges Leerenschiff aus Purpur in einem Gerüst aus Endsteinziegelpfeilern und
    Gerüststangen, mit Kran, Stapeln aus Purpurblöcken und einem Arbeiterhäuschen."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    grund(w, R, huegel=0.1)
    L = int(9 * s + 6)
    B = 2.2 * s + 1.8
    yk = int(3 * s + 3)
    for x in range(-L, L + 1):
        t = x / L
        bw = B * math.sqrt(max(0, 1 - t ** 2)) if t > 0 else B * math.sqrt(max(0, 1 - t ** 6))
        fertig = x < L * 0.4
        for z in range(-int(bw) - 1, int(bw) + 2):
            if abs(abs(z) - bw) < 0.8 or (abs(z) <= bw and fertig):
                for y in range(yk, yk + int(1.5 * s + 2)):
                    if abs(abs(z) - bw) < 0.8 and (fertig or (x + y) % 2 == 0):
                        w.setze(x, y, z, w.b("purpur_block") if y > yk else w.b("obsidian"))
                if abs(z) <= bw and fertig:
                    w.setze(x, yk, z, w.b("purpur_block"))
                    w.setze(x, yk + int(1.5 * s + 2), z, w.b("purpur_slab", type="bottom", waterlogged=False))
        if x % 3 == 0:
            for y in range(1, yk):
                w.setze(x, y, 0, w.b("end_stone_brick_wall"))
    for x in range(-L - 2, L + 3, 4):
        for sz in (-1, 1):
            z = sz * (int(B) + 3)
            for y in range(1, yk + int(5 * s + 4)):
                w.setze(x, y, z, w.b("scaffolding", distance=0, bottom=False, waterlogged=False))
    kx = -L - 4
    hk = yk + int(8 * s + 6)
    for y in range(1, hk):
        w.setze(kx, y, 0, w.b("end_stone_bricks"))
    for k in range(int(L * 0.8)):
        w.setze(kx + k, hk, 0, w.b("purpur_block"))
    for y in range(yk + int(2 * s + 3), hk):
        w.setze(kx + int(L * 0.8) - 1, y, 0, w.b("chain", axis="y", waterlogged=False))
    w.setze(kx + int(L * 0.8) - 1, yk + int(2 * s + 2), 0, w.b("purpur_block"))
    for k in range(4):
        w.setze(int(R * 0.5) + k % 2, 1 + k // 2, int(R * 0.5), w.b("purpur_block"))
    return w


def shulker_bastion(seed, g=2):
    """Shulker-Bastion: eine sternförmige Festung aus Purpur mit niedrigen Mauern und Spitzbastionen, auf deren
    Ecken violette Shulker-Kisten als Wachposten sitzen, in der Mitte ein Turm mit Glashaube."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    grund(w, R, huegel=0.1)
    p = purpur(w)
    n = 5
    Ra = R * 0.78
    Ri = R * 0.45
    H = int(3 * s + 3)
    ecken = []
    for i in range(2 * n):
        a = i / (2 * n) * 2 * math.pi
        r = Ra if i % 2 == 0 else Ri
        ecken.append((math.cos(a) * r, math.sin(a) * r))
    for (a, b) in zip(ecken, ecken[1:] + ecken[:1]):
        L = int(math.hypot(b[0] - a[0], b[1] - a[1]) * 2) + 1
        for k in range(L + 1):
            t = k / L
            x, z = round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t)
            for y in range(1, H + 1):
                w.setze(x, y, z, p(x, y, z))
            if k % 2 == 0:
                w.setze(x, H + 1, z, w.b("purpur_slab", type="bottom", waterlogged=False))
    for i in range(0, 2 * n, 2):
        x, z = round(ecken[i][0]), round(ecken[i][1])
        w.setze(x, H + 1, z, w.b("purple_shulker_box", facing="up"))
    th = int(10 * s + 7)
    for y in range(1, th):
        for x, z in kreisrand(2 * s + 1.6):
            w.setze(x, y, z, p(x, y, z) if y % 5 else w.b("end_stone_bricks"))
    from wueste_eis import kuppel
    kuppel(w, w.b("magenta_stained_glass"), 0, 0, th, 2 * s + 1.6, form="spitz", spitze="purpur_pillar")
    for y in (1, 2):
        w.bloecke.pop((round(Ri), y, 0), None)
    return w


ENDREICH3 = {
    "endermann_allee": ("Endermann-Allee", endermann_allee),
    "schwebende_bibliothek": ("Schwebende Bibliothek", schwebende_bibliothek),
    "leerenspalte": ("Leerenspalte", leerenspalte),
    "ringinsel": ("Ringinsel", ringinsel),
    "brueckenkreuz": ("Purpurbrücken-Kreuzung", brueckenkreuz),
    "kristallmonument": ("End-Kristall-Monument", kristallmonument),
    "elytra_turm": ("Elytra-Startturm", elytra_turm),
    "chorus_irrgarten": ("Chorus-Irrgarten", chorus_irrgarten),
    "leerenwal": ("Leerenwal", leerenwal),
    "gateway_ruine": ("Gateway-Ruine", gateway_ruine),
    "leerensee": ("Leerensee", leerensee),
    "purpur_leuchtturm": ("Purpur-Leuchtturm", purpur_leuchtturm),
    "enderauge": ("Enderauge-Monument", enderauge),
    "purpur_gassen": ("Purpur-Gassen", purpur_gassen),
    "trittsteine": ("Schwebende Trittsteine", trittsteine),
    "drachenschaedel": ("Drachenschädel", drachenschaedel),
    "angekettete_inseln": ("Angekettete Inseln", angekettete_inseln),
    "schwebebrunnen": ("Schwebebrunnen", schwebebrunnen),
    "leerenwerft": ("Leerenwerft", leerenwerft),
    "shulker_bastion": ("Shulker-Bastion", shulker_bastion),
}

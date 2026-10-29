"""Unterwasserwelt II – zwanzig weitere Bauten am Meeresgrund: Nautilus-Haus, Seeigel-Kuppeln, Mantarochen-
Statue, Seepferdchen-Stall, Taucherglocken-Station, Versunkener Hafen, Riesenkrabbe, Anglerfisch, Tiefsee-
Schlote, Korallen-Amphitheater, Versunkene Bibliothek, Seeschlange, Schwammriff, U-Boot-Wrack, Ankerfriedhof,
Leuchtgrotte, Meerhexen-Hütte, Fischschwarm-Spirale, Tang-Labyrinth und Austernbank mit Riesenperlen."""

from __future__ import annotations

import math

import numpy as np

from elemente import KORALLEN, korallenbewuchs, meeresgrund
from feinbau import Mix, platte, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen
from skulptur import Skulptur, dreh_y, ell, kap, kasten, kegel, kreisrand, torus

S = [0.6, 1.0, 1.6, 2.5]


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def prisma(w):
    return M(w, [("prismarine_bricks", 3), ("prismarine", 2), ("dark_prismarine", 1)])


def fels(w):
    return M(w, [("stone", 3), ("andesite", 2), ("tuff", 1), ("mossy_cobblestone", 1)])


def grund(w, R, dichte=1.0, felsen=0):
    rng = w.rng
    f = fels(w)
    for _ in range(felsen):
        a = rng.random() * 6.28
        d = R * (0.5 + rng.random() * 0.45)
        kugel(w, math.cos(a) * d, 0, math.sin(a) * d, 1.2 + rng.random() * 2.2, f, ueber=False,
              ry=1.0 + rng.random() * 1.5)
    meeresgrund(w, int(R), dichte=dichte)


def skulptur(w, u, teile, lo, hi, pos=(0, 0, 0), winkel=0.0):
    Sk = Skulptur(w, u)
    for i, (form, blk) in enumerate(teile):
        Sk.mat(str(i), blk)
        Sk.plus(form, str(i))
    Sk.rendern(lo, hi, versatz=(pos[0] + 0.5, pos[1], pos[2] + 0.5), dreh=dreh_y(winkel))


def wl(w, name, **pr):
    return w.b(name, waterlogged=True, **pr)


# ============================================================================ Bauten

def nautilushaus(seed, g=1):
    """Nautilus-Haus: ein Wohnhaus in Form eines riesigen, spiralig gewundenen Nautilusgehäuses mit
    rotbraunen Streifen, runder Öffnung als Eingang, Bullaugen und einem kleinen Korallengarten davor."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    grund(w, R, 1.0, felsen=2 + g)
    k = 0.2
    thmax = 3.3 * math.pi
    rmax = 6.0 * s + 3.0
    a0 = rmax / math.exp(k * thmax)
    roh = []
    th = 0.0
    while th <= thmax:
        r = a0 * math.exp(k * th)
        roh.append((math.cos(th) * r, math.sin(th) * r, th))
        th += 0.05
    xs = [p[0] for p in roh]
    ys = [p[1] for p in roh]
    ymin = min(ys) - 0.45 * rmax
    xm = (max(xs) + min(xs)) / 2
    pts = [(x - xm, y - ymin + 1, 0, th / thmax) for x, y, th in roh]
    mx, my = pts[0][0], pts[0][1]

    def mat(x, y, z, *a):
        ang = math.atan2(y - my, x - mx)
        streifen = math.sin(ang * 7 + math.hypot(x - mx, y - my) * 0.15) > 0.4
        return w.b("brown_terracotta" if streifen else "white_terracotta")
    from bogen2 import koerper, setzen
    lo, occ, tg = koerper(w, pts, lambda t: max(0.6, 0.42 * a0 * math.exp(k * t * thmax)), rz=1.0, rauh=0.03)
    setzen(w, lo, occ, tg, mat, ab_y=0, ueber=True)
    rr0 = 0.42 * a0
    rr1 = 0.42 * rmax
    ende = pts[-1]
    ex, ey = round(ende[0]), round(ende[1])
    for dx in range(-int(rr1), int(rr1) + 1):
        for dy in range(-int(rr1), int(rr1) + 1):
            for dz in range(-int(rr1), int(rr1) + 1):
                if dx * dx + dy * dy + dz * dz < (rr1 - 1.2) ** 2:
                    w.bloecke.pop((ex + dx, ey + dy, dz), None)
    for t in (0.35, 0.6, 0.8):
        i = int(t * (len(pts) - 1))
        x, y, z, _ = pts[i]
        r = rr0 + (rr1 - rr0) * t
        w.setze(round(x), round(y), round(r) - 0, w.b("glass"))
        w.setze(round(x), round(y), -round(r) + 0, w.b("glass"))
    for x in range(ex - 3, ex + 4):
        for z in range(-3, 4):
            if (x + z) % 2 == 0 and w.frei(x, 1, z):
                w.setze(x, 1, z, wl(w, f"{KORALLEN[(x * 3 + z) % 5]}_coral"))
    korallenbewuchs(w, 0.12)
    return w


def seeigelkuppeln(seed, g=1):
    """Seeigel-Kuppeln: eine kleine Siedlung aus violetten, stacheligen Kuppelhäusern mit Glaskappen und
    Seelaternen, verbunden durch gepflasterte Wege aus Prismarin."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    grund(w, R, 0.8)
    rng = w.rng
    n = 3 + g
    for i in range(n + 1):
        if i == n:
            cx, cz, r = 0, 0, 3.5 * s + 3
        else:
            a = i / n * 2 * math.pi + 0.4
            cx, cz = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
            r = (2 + rng.random()) * s + 1.8
        for x in range(int(cx - r) - 3, int(cx + r) + 4):
            for z in range(int(cz - r) - 3, int(cz + r) + 4):
                for y in range(1, int(r) + 4):
                    d = math.sqrt((x - cx) ** 2 + ((y - 1) * 1.15) ** 2 + (z - cz) ** 2)
                    if r - 1.1 < d <= r:
                        oben = y > r * 0.75
                        w.setze(x, y, z, w.b("purple_stained_glass" if oben and (x + z) % 2 else
                                             "purple_terracotta" if (x + y + z) % 3 else "magenta_terracotta"))
                    elif d <= r - 1.1:
                        w.bloecke.pop((x, y, z), None)
        for k in range(int(10 * r)):
            th = rng.random() * math.pi * 0.45
            ph = rng.random() * 2 * math.pi
            for L in range(1, int(2 + s * 1.5)):
                rr = r + L
                x = round(cx + math.cos(ph) * math.cos(th) * rr)
                z = round(cz + math.sin(ph) * math.cos(th) * rr)
                y = round(1 + math.sin(th) * rr / 1.15)
                w.setze(x, y, z, w.b("purple_concrete" if L < 2 else "end_rod", facing="up") if L >= 2 else
                        w.b("purple_concrete"), False)
        w.setze(cx, 1, cz, w.b("sea_lantern"))
        for y in (1, 2):
            w.bloecke.pop((cx, y, round(cz + r - 0.5)), None)
            w.bloecke.pop((cx, y, round(cz + r)), None)
        for k in range(int(math.hypot(cx, cz))):
            t = k / max(1, math.hypot(cx, cz))
            x, z = round(cx * (1 - t)), round(cz * (1 - t))
            if w.frei(x, 1, z) or True:
                w.setze(x, 0, z, w.b("prismarine_bricks"))
    return w


def mantastatue(seed, g=2):
    """Mantarochen-Statue: ein riesiger Mantarochen aus dunklem Prismarin mit heller Unterseite gleitet
    über einem schlanken Korallenpfeiler; Kopflappen, langer Schwanz, Kiemen aus Seelaternen."""
    w = _neu(seed)
    s = S[g]
    u = 1.0 * s + 0.4
    R = int(10 * u + 5)
    grund(w, R, 1.0, felsen=3)
    H = 8 * u + 3
    korallenbewuchs(w, 0.18)
    dk = w.b("black_concrete")
    hell = w.b("white_concrete")
    teile = [
        (lambda X, Y, Z: ((np.abs(X) / 10.5) ** 1.4 + ((Z - 0.04 * X ** 2) / 5.5) ** 2 <= 1)
         & (np.abs(Y - 0.05 * X ** 2 * 0.3) <= 0.8 * (1 - np.abs(X) / 11) + 0.35), dk),
        (lambda X, Y, Z: ((np.abs(X) / 9.5) ** 1.4 + ((Z - 0.04 * X ** 2) / 4.5) ** 2 <= 1)
         & (Y - 0.015 * X ** 2 < -0.3) & (Y - 0.015 * X ** 2 > -1.1), hell),
        (kap((-1.4, 0, 4.8), (-1.6, -0.6, 7.0), 0.45), dk), (kap((1.4, 0, 4.8), (1.6, -0.6, 7.0), 0.45), dk),
        (kap((0, 0, -4.5), (0, 0.6, -14), 0.35, 0.15), dk),
        (ell(-1.9, 0.5, 4.0, 0.3, 0.3, 0.3), w.b("sea_lantern")), (ell(1.9, 0.5, 4.0, 0.3, 0.3, 0.3),
                                                                    w.b("sea_lantern")),
    ]
    skulptur(w, u, teile, (-12, -3, -15), (12, 3, 8), pos=(0, H + 2 * u, 0), winkel=0.5)
    for y in range(1, int(H + 1.5 * u)):
        r = 1.2 * u * (1 - y / (H * 1.6)) + 0.6
        for x in range(-2, 3):
            for z in range(-2, 3):
                if x * x + z * z <= r * r + 0.3:
                    w.setze(x, y, z, w.b(f"{KORALLEN[(y // 3) % 5]}_coral_block"))
    return w


def seepferdchen(seed, g=1):
    """Seepferdchen-Stall: ein Bogenstall aus Prismarin mit Boxen, davor stehen große Seepferdchen-Figuren
    in Gelb und Orange mit eingerolltem Schwanz, dazu Futtertröge mit Seegras."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    grund(w, R, 0.9)
    p = prisma(w)
    B = int(8 * s + 7)
    T = int(3 * s + 4)
    hh = int(2 * s + 4)
    for x in range(-B, B + 1):
        for z in range(-T - int(R * 0.4), -int(R * 0.4) + 1):
            zr = z + int(R * 0.4)
            for y in range(1, hh + 2):
                rand = x in (-B, B) or zr in (-T, 0)
                box = x % 4 == 0
                if y == hh + 1:
                    w.setze(x, y, z, p(x, y, z))
                elif rand or box:
                    oeff = zr == 0 and not box and y <= hh - 1 and x not in (-B, B)
                    if not oeff:
                        w.setze(x, y, z, p(x, y, z) if not (rand and y == hh) else w.b("sea_lantern"))
                else:
                    w.bloecke.pop((x, y, z), None)
            w.setze(x, 0, z, w.b("prismarine_bricks"))
        if x % 4 == 2:
            w.setze(x, 1, -int(R * 0.4) - T + 1, w.b("composter", level=8))
    farben = [("yellow_concrete", "orange_concrete"), ("orange_terracotta", "yellow_terracotta"),
              ("pink_concrete", "magenta_terracotta")]
    for k in range(2 + g):
        a, b = farben[k % 3]
        A, Bb = w.b(a), w.b(b)
        teile = [(kap((0, 7.5, 0), (0.6, 4.5, 0), 1.1, 1.4), A), (ell(0.9, 4.5, 0, 1.2, 1.4, 1.0), Bb),
                 (kap((0.6, 3.6, 0), (0, 1.8, 0), 1.0, 0.6), A), (ell(0.3, 1.2, 0, 0.9, 0.7, 0.4), A),
                 (ell(-0.6, 1.4, 0, 0.5, 0.5, 0.4), A),
                 (ell(-0.2, 8.6, 0, 1.0, 0.9, 0.8), A), (kap((0.4, 8.5, 0), (2.4, 8.1, 0), 0.45, 0.35), A),
                 (ell(0.1, 9.4, 0, 0.3, 0.6, 0.2), Bb), (ell(0.3, 8.9, 0.75, 0.2, 0.2, 0.1), w.b("black_concrete")),
                 (ell(0.3, 8.9, -0.75, 0.2, 0.2, 0.1), w.b("black_concrete")),
                 (ell(-1.0, 6.5, 0, 0.5, 0.9, 0.2), Bb)]
        x = -B + 3 + k * int(2 * B / (2 + g))
        skulptur(w, 0.5 * s + 0.3, teile, (-2, 0, -2), (3, 10, 2), pos=(x, 1, int(R * 0.25)),
                 winkel=math.pi / 2 + (k % 2) * 0.5)
    korallenbewuchs(w, 0.12)
    return w


def taucherglocke(seed, g=1):
    """Taucherglocken-Station: eine große Kupfer-Taucherglocke mit Bullaugen hängt an Ketten über dem Grund,
    darunter Arbeitsplattform, Truhen, Seilwinde, Luftschläuche und gestapelte Kisten mit Fundstücken."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    grund(w, R, 0.8, felsen=2)
    P = int(4 * s + 4)
    for x in range(-P, P + 1):
        for z in range(-P, P + 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
        for z in (-P, P):
            if x % 3 == 0:
                w.setze(x, 2, z, w.b("spruce_fence", waterlogged=True))
    for x in (-P, P):
        for z in (-P, P):
            w.setze(x, 0, z, w.b("spruce_log", axis="y"))
            w.setze(x, -1, z, w.b("spruce_log", axis="y"))
    rb = 2.0 * s + 2.2
    yb = int(6 * s + 6)
    for y in range(0, int(rb * 1.5) + 1):
        t = y / (rb * 1.5)
        r = rb * (1 - t ** 3 * 0.75)
        for x, z in kreisrand(max(0.5, r), 0, 0):
            nah = y == int(rb * 0.6) and (abs(x) < 1 or abs(z) < 1)
            w.setze(x, yb + y, z, w.b("glass") if nah else w.b("waxed_weathered_cut_copper" if y % 3 else
                                                                 "waxed_cut_copper"))
    for x in range(-int(rb) - 1, int(rb) + 2):
        for z in range(-int(rb) - 1, int(rb) + 2):
            if math.hypot(x, z) <= rb + 0.5 and int(rb * 1.5) > 0:
                w.setze(x, yb + int(rb * 1.5), z, w.b("waxed_cut_copper"))
    for y in range(yb + int(rb * 1.5) + 1, yb + int(rb * 1.5) + 8 + int(4 * s)):
        w.setze(0, y, 0, w.b("chain", axis="y", waterlogged=True))
    w.setze(0, yb + 1, 0, w.b("lantern", hanging=True, waterlogged=True))
    for k, (x, z) in enumerate(((P - 1, P - 1), (-P + 1, P - 1), (P - 1, -P + 1))):
        for y in range(2, 2 + 1 + k % 2):
            w.setze(x, y, z, w.b("barrel", facing="up", open=False))
    w.setze(-P + 2, 2, -P + 1, w.b("chest", facing="south", type="single", waterlogged=True))
    w.setze(-P + 1, 2, -P + 1, w.b("spruce_log", axis="x"))
    w.setze(-P + 1, 3, -P + 1, w.b("chain", axis="y", waterlogged=True))
    pts = bez((-P + 1, 2, -P + 1), (-P, yb * 0.6, 0), (-rb, yb + rb * 0.7, 0))
    for x, y, z, _ in pts:
        w.setze(round(x), round(y), round(z), w.b("black_concrete"), False)
    korallenbewuchs(w, 0.1)
    return w


def versunkener_hafen(seed, g=2):
    """Versunkener Hafen: eine eingestürzte Kaimauer, schiefe Holzpfähle eines Stegs, gesunkene Ruderboote,
    verstreute Fässer, ein großer Anker an Kette und ein umgestürzter Hafenkran."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    grund(w, R, 1.1)
    rng = w.rng
    st = M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 2), ("cracked_stone_bricks", 1)])
    zk = -int(R * 0.5)
    for x in range(-R, R + 1):
        for z in range(zk - 3, zk + 1):
            hoehe = int(3 * s + 2 - (abs(x) % 7 == 3) * 2 + rng.random() * 1.5)
            for y in range(1, hoehe + 1):
                if math.hypot(x, z) <= R:
                    w.setze(x, y, z, st(x, y, z))
    for k in range(int(5 * s + 3)):
        z = zk + 2 + k * 2
        for x in (-2, 2):
            neig = rng.random() * 0.6 - 0.3
            for y in range(1, int(4 * s + 3) - (k % 3)):
                w.setze(round(x + neig * y), y, z, w.b("stripped_spruce_log", axis="y"))
        if rng.random() < 0.55:
            for x in range(-2, 3):
                w.setze(x, int(4 * s + 2) - (k % 3), z, platte(w, "spruce", "bottom"))
    for j in range(1 + g):
        bx, bz = int((rng.random() - 0.3) * R), int(R * 0.2 + rng.random() * R * 0.4)
        ang = rng.random() * 3
        L, Bb = 4 + int(s * 2), 1.5 + 0.5 * s
        for i in range(-L, L + 1):
            bw = Bb * math.sqrt(max(0, 1 - (i / (L + 0.5)) ** 2))
            for q in range(-int(bw) - 1, int(bw) + 2):
                if abs(abs(q) - bw) < 0.8:
                    x = round(bx + math.cos(ang) * i - math.sin(ang) * q)
                    z = round(bz + math.sin(ang) * i + math.cos(ang) * q)
                    w.setze(x, 1 + (q > 0), z, w.b("dark_oak_planks" if (i + q) % 4 else "spruce_planks"))
            x = round(bx + math.cos(ang) * i)
            z = round(bz + math.sin(ang) * i)
            w.setze(x, 1, z, w.b("dark_oak_planks"))
    ax, az = int(R * 0.55), int(R * 0.1)
    for y in range(1, int(4 * s + 3)):
        w.setze(ax, y, az, w.b("iron_block" if y > 1 else "anvil", facing="north") if y > 1 else
                w.b("iron_block"))
    for dx in (-2, -1, 1, 2):
        w.setze(ax + dx, 1 + (abs(dx) == 2), az, w.b("iron_block"))
    w.setze(ax, int(4 * s + 3), az, w.b("iron_bars", waterlogged=True))
    for k in range(int(6 * s + 4)):
        w.setze(ax - k, 1, az + 1 + (k % 2), w.b("chain", axis="x", waterlogged=True))
    kx, kz = -int(R * 0.45), int(R * 0.15)
    for k in range(int(8 * s + 5)):
        x, y = kx + k, 1 + int(k * 0.25)
        w.setze(x, y, kz, w.b("dark_oak_log", axis="x"))
        if k % 3 == 0:
            w.setze(x, y + 1, kz, w.b("dark_oak_fence", waterlogged=True))
    for _ in range(4 + 3 * g):
        x, z = int((rng.random() - 0.5) * R * 1.4), int((rng.random() - 0.5) * R * 1.4)
        if w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("barrel", facing=["up", "east", "north"][int(rng.integers(3))], open=False))
    korallenbewuchs(w, 0.22)
    return w


def riesenkrabbe(seed, g=2):
    """Riesenkrabbe: eine gewaltige rote Krabbe mit gepanzertem Rücken, erhobenen Scheren, Stielaugen und
    acht gespreizten Beinen steht auf einem Felsen aus Muschelschalen."""
    w = _neu(seed)
    s = S[g]
    u = 0.9 * s + 0.4
    R = int(10 * u + 5)
    grund(w, R, 0.9, felsen=2)
    rot = w.b("red_concrete")
    rt = w.b("red_terracotta")
    hell = w.b("white_terracotta")
    sch = w.b("black_concrete")
    teile = [(ell(0, 4.5, 0, 5.0, 2.0, 3.8), rot), (ell(0, 5.6, -0.3, 4.4, 1.3, 3.2), rt),
             (ell(0, 3.6, 0, 4.5, 1.0, 3.4), hell)]
    for sx in (-1, 1):
        for k, wz in enumerate((-2.4, -0.8, 0.8, 2.2)):
            kx = sx * 4.4
            teile.append((kap((kx, 4.2, wz), (sx * 7.2, 5.6, wz * 1.3), 0.55, 0.45), rot))
            teile.append((kap((sx * 7.2, 5.6, wz * 1.3), (sx * 8.6, 0, wz * 1.6), 0.45, 0.2), rot))
        teile.append((kap((sx * 2.8, 4.4, 3.4), (sx * 4.2, 6.5, 6.0), 0.8, 0.7), rot))
        teile.append((ell(sx * 4.6, 7.6, 7.0, 1.8, 1.4, 1.6), rt))
        teile.append((kap((sx * 4.3, 8.6, 7.8), (sx * 3.8, 10.4, 8.8), 0.6, 0.3), rot))
        teile.append((kap((sx * 5.0, 8.0, 8.3), (sx * 5.4, 9.6, 9.6), 0.5, 0.25), rt))
        teile.append((kap((sx * 1.2, 6.0, 3.0), (sx * 1.4, 7.6, 3.4), 0.25), rot))
        teile.append((ell(sx * 1.4, 7.9, 3.4, 0.45, 0.45, 0.45), sch))
    skulptur(w, u, teile, (-10, -1, -6), (10, 12, 11), pos=(0, 1, -2))
    korallenbewuchs(w, 0.1)
    return w


def anglerfisch(seed, g=2):
    """Anglerfisch: ein schwarzer Tiefseefisch mit aufgerissenem Maul voller weißer Zähne, kleinen Augen
    und einer leuchtenden Angel an einem gebogenen Stiel – darunter ein dunkles Tiefseebecken."""
    w = _neu(seed)
    s = S[g]
    u = 0.9 * s + 0.4
    R = int(10 * u + 5)
    grund(w, R, 0.6, felsen=4)
    k = w.b("black_concrete")
    k2 = w.b("gray_concrete")
    z_ = w.b("white_concrete")
    teile = [(ell(0, 7, 0, 5.5, 4.5, 4.0), k), (ell(-2, 6.5, 0, 4.5, 3.6, 3.6), k2),
             (kap((-5, 7, 0), (-9, 7.5, 0), 1.8, 0.6), k),
             (lambda X, Y, Z: ((X + 10.2) ** 2 / 1.0 + (Y - 7.5) ** 2 / 9 <= 1) & (np.abs(Z) < 0.5), k),
             (ell(3.8, 6.0, 0, 2.5, 2.5, 3.4), None), (ell(3.5, 8.5, 2.6, 0.5, 0.5, 0.4), w.b("yellow_concrete")),
             (ell(3.5, 8.5, -2.6, 0.5, 0.5, 0.4), w.b("yellow_concrete"))]
    Sk = Skulptur(w, u)
    for i, (form, blk) in enumerate(teile):
        if blk is None:
            Sk.minus(form)
        else:
            Sk.mat(str(i), blk)
            Sk.plus(form, str(i))
    for i in range(10):
        a = -0.4 + i * 0.32
        for sign, yb in ((1, 4.0), (-1, 8.2)):
            Sk.mat("z", z_)
            Sk.plus(kegel(4.6 + math.cos(a) * 0.4, math.sin(a) * 2.6, yb if sign > 0 else yb - 1.2,
                          yb + 1.2 if sign > 0 else yb, 0.35 if sign > 0 else 0.05, 0.05 if sign > 0 else 0.35), "z")
    Sk.rendern((-12, 0, -6), (8, 13, 6), versatz=(0.5, 1, 0.5))
    pts = bez((0, 11.5 * u + 1, 0), (2 * u, 16 * u, 0), (7 * u, 14 * u, 0))
    rohr(w, pts, 0.5 + 0.2 * s, 0.4, mat=w.b("black_concrete"))
    lx, ly = round(7 * u), round(14 * u)
    kugel(w, lx, ly - 1.5 * u, 0, 1.0 + 0.4 * s, w.b("ochre_froglight", axis="y"))
    korallenbewuchs(w, 0.05)
    return w


def tiefseeschlote(seed, g=1):
    """Tiefsee-Schlote: schwarze Raucher aus Basalt und Schwarzstein mit glühenden Magmaspitzen, umringt von
    Kolonien roter Röhrenwürmer, gelben Schwefelkrusten und bleichen Muscheln."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rng = w.rng
    for x, z in [(x, z) for x in range(-R, R + 1) for z in range(-R, R + 1) if math.hypot(x, z) <= R]:
        w.setze(x, 0, z, w.b("basalt", axis="y") if (x * 7 + z * 3) % 5 else w.b("blackstone"))
    n = 3 + g * 2
    for i in range(n):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.6
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        H = int((5 + rng.random() * 8) * s + 3)
        r0 = 1.4 + s * 0.9
        for y in range(1, H + 1):
            t = y / H
            r = r0 * (1 - t * 0.6) + 0.3 * math.sin(y * 1.3)
            for x in range(cx - 3, cx + 4):
                for z in range(cz - 3, cz + 4):
                    dd = math.hypot(x - cx, z - cz)
                    if dd <= r:
                        b = "magma_block" if dd < 0.8 and y > H - 2 else "polished_basalt" if dd > r - 0.9 and \
                            (x + y) % 3 else "blackstone" if dd > r - 0.9 else "basalt"
                        w.setze(x, y, z, w.b(b, axis="y") if "basalt" in b else w.b(b))
            if y % 4 == 2 and rng.random() < 0.6:
                w.setze(cx + 2, y, cz, w.b("yellow_terracotta"), False)
        w.setze(cx, H + 1, cz, w.b("magma_block"))
        w.setze(cx, H + 2, cz, w.b("bubble_column", drag=True) if False else w.b("magma_block"))
        for _ in range(int(8 * s + 4)):
            aa = rng.random() * 6.28
            dd = r0 + 1 + rng.random() * 3
            x, z = round(cx + math.cos(aa) * dd), round(cz + math.sin(aa) * dd)
            h = int(1 + rng.random() * 3)
            for y in range(1, h + 1):
                w.setze(x, y, z, w.b("white_concrete" if y < h else "red_concrete"), False)
    for _ in range(int(10 * s)):
        x, z = int((rng.random() - 0.5) * 2 * R), int((rng.random() - 0.5) * 2 * R)
        if math.hypot(x, z) < R and w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("bone_block", axis="y") if rng.random() < 0.5 else w.b("yellow_terracotta"))
    return w


def korallenamphitheater(seed, g=2):
    """Korallen-Amphitheater: ein halbrunder Zuschauerraum mit Sitzreihen aus Prismarin, überwuchert von
    bunten Korallen, eine Bühne mit Muschelrückwand und vier Fackelsäulen aus Seelaternen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 7)
    grund(w, R + 2, 0.8)
    p = prisma(w)
    reihen = int(4 * s + 3)
    r0 = R * 0.35
    for k in range(reihen):
        rr = r0 + k * 1.6
        for x, z in [(x, z) for x in range(-R, R + 1) for z in range(-R, 1)]:
            d = math.hypot(x, z)
            if rr <= d < rr + 1.6 and z <= 0:
                for y in range(1, k + 2):
                    w.setze(x, y, z, p(x, y, z))
                if (x + k) % 5 == 0:
                    w.setze(x, k + 2, z, wl(w, f"{KORALLEN[(x // 5 + k) % 5]}_coral"), False)
    for x in range(-int(r0) + 1, int(r0)):
        for z in range(0, int(r0 * 0.7)):
            w.setze(x, 1, z, w.b("smooth_quartz"))
    sz = int(r0 * 0.7)
    for x in range(-int(r0), int(r0) + 1):
        h = int(r0 * 0.9 * math.sqrt(max(0, 1 - (x / (r0 + 0.5)) ** 2))) + 2
        for y in range(2, h + 2):
            rippe = abs(math.atan2(y, x) * 6 % 1 - 0.5) < 0.15
            w.setze(x, y, sz, w.b("pink_terracotta" if rippe else "white_terracotta"))
    for x in (-int(r0), -int(r0 * 0.4), int(r0 * 0.4), int(r0)):
        for y in range(1, int(4 * s + 3)):
            w.setze(x, y, 1, w.b("prismarine_wall", waterlogged=True))
        w.setze(x, int(4 * s + 3), 1, w.b("sea_lantern"))
    korallenbewuchs(w, 0.25)
    return w


def unterwasserbibliothek(seed, g=2):
    """Versunkene Bibliothek: ein runder, halb eingestürzter Turm aus Steinziegeln mit Bücherregalen an den
    Innenwänden, Lesepulten, umgestürzten Regalen im Sand und Tang, der durch die Fenster wächst."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    grund(w, R, 1.0)
    st = M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 2), ("cracked_stone_bricks", 1), ("prismarine", 1)])
    rt = 4 * s + 3
    H = int(10 * s + 8)
    rn = Rauschen(w, 3)
    for y in range(1, H + 1):
        for x, z in kreisrand(rt):
            bruch = y > H * 0.55 and rn(x, y, z) < (y - H * 0.55) / (H * 0.6)
            if bruch:
                continue
            fen = y % 5 == 3 and (x + z) % 3 == 0
            w.setze(x, y, z, w.b("glass_pane", waterlogged=True) if fen else st(x, y, z))
        for x, z in kreisrand(rt - 1):
            if y % 5 not in (0,) and y < H * 0.7 and (x + z) % 4 != 0:
                w.setze(x, y, z, w.b("bookshelf"), False)
        if y % 5 == 0:
            for x in range(-int(rt), int(rt) + 1):
                for z in range(-int(rt), int(rt) + 1):
                    if math.hypot(x, z) < rt - 1.5 and (math.hypot(x, z) > rt * 0.4 or y < H * 0.4):
                        if rn(x * 2, y, z * 2) > 0.3:
                            w.setze(x, y, z, w.b("dark_oak_planks"), False)
    for y in (1, 2):
        w.bloecke.pop((0, y, round(rt)), None)
        w.bloecke.pop((0, y, round(rt) - 1), None)
    w.setze(0, 1, 0, w.b("lectern", facing="south", has_book=True, powered=False))
    w.setze(1, 1, 0, w.b("sea_lantern"))
    rng = w.rng
    for k in range(3 + g):
        a = rng.random() * 6.28
        d = rt + 2 + rng.random() * (R - rt - 3)
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        for i in range(3):
            w.setze(x0 + i, 1, z0, w.b("bookshelf"))
        w.setze(x0, 2, z0, w.b("lectern", facing="north", has_book=False, powered=False))
    for _ in range(4 + 2 * g):
        x, z = int((rng.random() - 0.5) * rt), int((rng.random() - 0.5) * rt)
        h = int(H * 0.6 + rng.random() * H * 0.5)
        for y in range(1, h):
            w.setze(x, y, z, w.b("kelp_plant"), False)
        w.setze(x, h, z, w.b("kelp", age=20), False)
    korallenbewuchs(w, 0.1)
    return w


def seeschlange(seed, g=2):
    """Seeschlange: eine gewaltige, türkis geschuppte Seeschlange windet sich in hohen Bögen aus dem Sand,
    mit gezackter Rückenflosse, gehörntem Kopf und aufgerissenem Maul."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    grund(w, R, 0.9)
    r = 1.1 * s + 1.0
    n = 5
    L = R * 1.7
    pts = []
    for i in range(int(L * 4)):
        t = i / (L * 4)
        x = -L / 2 + t * L
        y = max(-r, math.sin(t / 0.85 * n * math.pi) * (6 * s + 4)) if t < 0.85 else (6 * s + 4) * (t - 0.85) * 7
        z = math.sin(t * 2 * math.pi) * R * 0.25
        pts.append((x, y + 1, z, t))
    rohr(w, pts, r, r * 0.9, mat=lambda x, y, z, *a: w.b("prismarine" if (x + y * 2 + z) % 5 else "dark_prismarine"),
         rauh=0.05)
    for x, y, z, t in pts[::3]:
        if y > 1:
            w.setze(round(x), round(y + r + 0.8), round(z), w.b("cyan_terracotta"), False)
    hx, hy, hz, _ = pts[-1]
    kugel(w, hx, hy, hz, r * 1.6, w.b("prismarine"), ry=r * 1.3)
    for sz in (-1, 1):
        w.setze(round(hx + r * 0.6), round(hy + r * 0.6), round(hz + sz * r * 1.1), w.b("sea_lantern"))
        for k in range(1, int(2 + s * 1.5)):
            w.setze(round(hx - k * 0.6), round(hy + r * 1.2 + k), round(hz + sz * r * 0.8), w.b("bone_block"))
    for k in range(int(r * 1.6)):
        w.setze(round(hx + r * 1.6 - k * 0), round(hy - 0.3), round(hz), w.b("white_concrete"), True)
    for dx in range(0, int(r * 1.8) + 1):
        w.bloecke.pop((round(hx + dx), round(hy), round(hz)), None)
    korallenbewuchs(w, 0.08)
    return w


def schwammriff(seed, g=1):
    """Schwammriff: ein Feld aus gelben Röhren- und Vasenschwämmen in allen Größen, dazwischen Schwamm-
    blöcke, Seegras und kleine Fischfiguren."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    grund(w, R, 0.7, felsen=2)
    rng = w.rng
    for _ in range(int(14 * s + 8)):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.9
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        H = int(2 + rng.random() * 6 * s)
        r = 0.8 + rng.random() * 1.2 * s
        art = rng.random()
        for y in range(1, H + 1):
            t = y / H
            rr = r * (0.6 + 0.6 * t) if art < 0.5 else r * (1 - 0.3 * t)
            for x, z in kreisrand(max(0.5, rr), cx, cz):
                w.setze(x, y, z, w.b("sponge" if (x + y + z) % 3 else "wet_sponge" if art < 0.7 else
                                     "yellow_terracotta"))
            if y == 1:
                for x in range(cx - int(rr), cx + int(rr) + 1):
                    for z in range(cz - int(rr), cz + int(rr) + 1):
                        if math.hypot(x - cx, z - cz) < rr:
                            w.setze(x, y, z, w.b("sponge"))
    for _ in range(3 + g * 2):
        x, y, z = int((rng.random() - 0.5) * R), int(3 + rng.random() * 5 * s), int((rng.random() - 0.5) * R)
        f = ["orange_concrete", "yellow_concrete", "light_blue_concrete"][int(rng.integers(3))]
        for k in range(3):
            w.setze(x + k, y, z, w.b(f) if k < 2 else w.b("white_concrete"), False)
        w.setze(x - 1, y, z, w.b(f), False)
    korallenbewuchs(w, 0.15)
    return w


def uboot_wrack(seed, g=2):
    """U-Boot-Wrack: ein rostiges, schräg im Sand steckendes Unterseeboot mit Turm, Sehrohr, Bullaugen,
    aufgerissener Flanke, Propeller und herausgefallenen Kisten."""
    w = _neu(seed)
    s = S[g]
    L = 14 * s + 8
    R = int(L * 0.75 + 5)
    grund(w, R, 1.0)
    r = 2.0 * s + 1.8
    rost = M(w, [("brown_terracotta", 2), ("waxed_exposed_copper", 1), ("gray_concrete", 2), ("iron_block", 1)])
    neig = 0.12
    pts = []
    for i in range(int(L * 3) + 1):
        t = i / (L * 3)
        x = -L / 2 + t * L
        pts.append((x, r * 0.6 + x * neig, 0, t))

    def radius(t):
        return r * (0.35 + 0.65 * math.sin(math.pi * min(1, t * 1.15)) ** 0.4)
    from bogen2 import koerper, setzen
    lo, occ, tg = koerper(w, pts, radius, rz=1.0, rauh=0.03)
    setzen(w, lo, occ, tg, lambda x, y, z, *a: rost(x, y, z), ab_y=0, ueber=True)
    tx = round(L * 0.08)
    ty = round(r * 0.6 + tx * neig + r)
    for y in range(ty - 1, ty + int(2 * s + 2)):
        for x in range(tx - int(s + 1), tx + int(s + 2)):
            for z in (-1, 0, 1):
                w.setze(x, y, z, rost(x, y, z))
    for y in range(ty + int(2 * s + 2), ty + int(2 * s + 5)):
        w.setze(tx, y, 0, w.b("iron_bars", waterlogged=True))
    for t in (0.25, 0.4, 0.6, 0.75):
        x = round(-L / 2 + t * L)
        y = round(r * 0.6 + x * neig)
        w.setze(x, y, round(radius(t)), w.b("glass"))
    rx = round(-L / 2) - 1
    ry = round(r * 0.6 - L / 2 * neig)
    for k in range(-2, 3):
        w.setze(rx, ry + k, 0, w.b("waxed_cut_copper"))
        w.setze(rx, ry, k, w.b("waxed_cut_copper"))
    for x in range(round(-L * 0.1), round(L * 0.15)):
        for y in range(1, int(r * 1.2)):
            w.bloecke.pop((x, y, round(radius(0.5))), None)
            w.bloecke.pop((x, y, round(radius(0.5)) - 1), None)
    rng = w.rng
    for _ in range(3 + g):
        x, z = int((rng.random() - 0.5) * L * 0.4), round(radius(0.5)) + 2 + int(rng.random() * 3)
        w.setze(x, 1, z, w.b("barrel", facing="east", open=False))
    korallenbewuchs(w, 0.2)
    return w


def ankerfriedhof(seed, g=2):
    """Ankerfriedhof: riesige, rostige Schiffsanker in allen Größen stecken schräg im Sand, verbunden durch
    lange Ketten, zwischen ihnen Seesterne, Muscheln und eine versunkene Schiffsglocke."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    grund(w, R, 0.8)
    rng = w.rng
    ankerpos = []
    for k in range(3 + g):
        a = k / (3 + g) * 2 * math.pi + rng.random() * 0.4
        d = R * (0.25 + rng.random() * 0.45)
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        gr = (0.6 + rng.random() * 0.8) * s + 0.4
        teile = [(kap((0, -1, 0), (0, 9, 0), 0.55), w.b("iron_block")),
                 (kap((-2.5, 7.5, 0), (2.5, 7.5, 0), 0.45), w.b("iron_block")),
                 (lambda X, Y, Z: (np.abs(np.sqrt(X ** 2 + (Y - 4) ** 2) - 3.6) < 0.6) & (Y < 2.2) & (np.abs(Z) < 0.6),
                  w.b("iron_block")),
                 (kegel(-3.5, 0, 2.0, 3.6, 0.9, 0.1), w.b("iron_block")),
                 (kegel(3.5, 0, 2.0, 3.6, 0.9, 0.1), w.b("iron_block")),
                 (lambda X, Y, Z: (np.abs(np.sqrt(X ** 2 + (Y - 10) ** 2) - 1.1) < 0.4) & (np.abs(Z) < 0.4),
                  w.b("iron_block"))]
        Sk = Skulptur(w, gr)
        for i, (f, b) in enumerate(teile):
            Sk.mat(str(i), lambda x, y, z, *aa: w.b("brown_terracotta") if (x * 3 + y + z) % 5 == 0 else
                   w.b("gray_concrete"))
            Sk.plus(f, str(i))
        from skulptur import dreh_z
        Sk.rendern((-5, -2, -1), (5, 12, 1), versatz=(cx + 0.5, 0, cz + 0.5),
                   dreh=dreh_y(rng.random() * 6.28) @ dreh_z((rng.random() - 0.5) * 0.7))
        ankerpos.append((cx, round(10 * gr), cz))
    for (a, b) in zip(ankerpos, ankerpos[1:]):
        pts = bez((a[0], a[1], a[2]), ((a[0] + b[0]) / 2, 1, (a[2] + b[2]) / 2), (b[0], b[1], b[2]))
        for x, y, z, _ in pts:
            w.setze(round(x), max(1, round(y)), round(z), w.b("chain", axis="y", waterlogged=True), False)
    w.setze(0, 1, 0, w.b("bell", attachment="floor", facing="north", powered=False))
    for _ in range(6 + 3 * g):
        x, z = int((rng.random() - 0.5) * R * 1.6), int((rng.random() - 0.5) * R * 1.6)
        if math.hypot(x, z) < R and w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("orange_carpet") if rng.random() < 0.5 else w.b("sea_pickle", pickles=3,
                                                                                    waterlogged=True))
    korallenbewuchs(w, 0.1)
    return w


def leuchtgrotte(seed, g=2):
    """Leuchtgrotte: ein zerklüfteter Felsbogen, dessen Höhle voller Seegurken, Leuchtflechten, Seelaternen
    und Glühbeeren-Ranken schimmert; draußen ein Kranz aus Korallen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    grund(w, R, 0.8)
    f = fels(w)
    rn = Rauschen(w, 3)
    Rh = R * 0.65
    H = 7 * s + 5
    for x in range(-int(Rh), int(Rh) + 1):
        for z in range(-int(Rh), int(Rh) + 1):
            d = math.hypot(x, z)
            if d < Rh:
                h = H * (1 - (d / Rh) ** 2) ** 0.6 + rn(x, 0, z) * 3
                for y in range(1, int(h) + 1):
                    w.setze(x, y, z, f(x, y, z))
    ri = Rh * 0.7
    for x in range(-int(ri), int(ri) + 1):
        for z in range(-int(ri), int(Rh) + 2):
            for y in range(1, int(H * 0.8)):
                if (x / ri) ** 2 + ((y - 1) / (H * 0.75)) ** 2 + ((z if z < 0 else z * 0.2) / ri) ** 2 < 1:
                    w.bloecke.pop((x, y, z), None)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y < 1 or abs(x) > ri + 1 or z > Rh:
            continue
        if w.frei(x, y - 1, z) and y > 2 and rng.random() < 0.18:
            for k in range(1, int(2 + rng.random() * 3)):
                if w.frei(x, y - k, z):
                    w.setze(x, y - k, z, w.b("cave_vines_plant", berries=True) if k > 1 or True else None)
        elif w.frei(x, y + 1, z) and rng.random() < 0.1 and math.hypot(x, z) < ri:
            w.setze(x, y + 1, z, w.b("sea_pickle", pickles=4, waterlogged=True))
        elif rng.random() < 0.05:
            w.setze(x, y, z, w.b("sea_lantern"))
    for x in range(-int(ri) + 1, int(ri)):
        for z in range(-int(ri) + 1, int(ri)):
            if math.hypot(x, z) < ri - 1 and w.frei(x, 1, z) and (x + z) % 3 == 0:
                w.setze(x, 1, z, w.b("sea_pickle", pickles=int(1 + (x * z) % 4), waterlogged=True))
    korallenbewuchs(w, 0.22)
    return w


def meerhexenhuette(seed, g=1):
    """Meerhexen-Hütte: eine krumme Hütte aus Wrackplanken auf Walknochen-Stelzen, mit Bullaugen, einem
    blubbernden Kessel, hängenden Laternen, Totenschädeln und Schlingpflanzen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    grund(w, R, 1.1)
    B, T = int(4 * s + 5), int(4 * s + 4)
    y0 = int(3 * s + 3)
    for x in (-B // 2, B // 2):
        for z in (-T // 2, T // 2):
            for y in range(1, y0):
                w.setze(x + (y % 3 == 0) * (1 if x > 0 else -1) * 0, y, z, w.b("bone_block", axis="y"))
    holz = M(w, [("dark_oak_planks", 3), ("spruce_planks", 2), ("mangrove_planks", 1), ("stripped_dark_oak_log", 1)])
    for x in range(-B // 2, B // 2 + 1):
        for z in range(-T // 2, T // 2 + 1):
            w.setze(x, y0, z, holz(x, y0, z))
            for y in range(y0 + 1, y0 + 5):
                neig = round((y - y0) * 0.25)
                rand = x in (-B // 2, B // 2) or z in (-T // 2, T // 2)
                if rand:
                    fen = y == y0 + 2 and (x + z) % 3 == 0
                    w.setze(x + neig, y, z, w.b("glass") if fen else holz(x, y, z))
    for k in range(int(B * 0.8) + 2):
        for x in range(-B // 2 - 1 + k // 2, B // 2 + 2 - k // 2):
            for z in range(-T // 2 - 1 + k // 2, T // 2 + 2 - k // 2):
                if k // 2 == min(x + B // 2 + 1, B // 2 + 1 - x, z + T // 2 + 1, T // 2 + 1 - z) or k == 0:
                    pass
        lv = k
        if lv > max(B, T) // 2 + 1:
            break
        for x in range(-B // 2 - 1 + lv, B // 2 + 2 - lv):
            for z in range(-T // 2 - 1 + lv, T // 2 + 2 - lv):
                rand = x in (-B // 2 - 1 + lv, B // 2 + 1 - lv) or z in (-T // 2 - 1 + lv, T // 2 + 1 - lv)
                if rand:
                    w.setze(x + 1, y0 + 5 + lv, z, w.b("mossy_cobblestone" if (x + z) % 3 else "dark_oak_planks"))
    for y in (y0 + 1, y0 + 2):
        w.bloecke.pop((0, y, T // 2), None)
    for z in range(T // 2 + 1, T // 2 + y0 + 1):
        w.setze(0, y0 - (z - T // 2) + 1, z, treppe(w, "dark_oak", "north"))
    w.setze(0, y0 + 1, 0, w.b("water_cauldron", level=3))
    w.setze(0, y0, 0, w.b("magma_block"))
    for x, z in ((-B // 2, T // 2 + 1), (B // 2, T // 2 + 1)):
        w.setze(x, y0 + 4, z, w.b("chain", axis="y", waterlogged=True))
        w.setze(x, y0 + 3, z, w.b("soul_lantern", hanging=True, waterlogged=True))
    w.setze(B // 2 + 1, y0 + 1, 0, w.b("skeleton_skull", rotation=4))
    w.setze(-B // 2 - 1, y0 + 1, 1, w.b("skeleton_skull", rotation=12))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > y0 and rng.random() < 0.03:
            for k in range(1, 4):
                if w.frei(x, y - k, z):
                    w.setze(x, y - k, z, w.b("kelp_plant") if k < 3 else w.b("kelp", age=20))
                else:
                    break
    korallenbewuchs(w, 0.1)
    return w


def fischschwarm(seed, g=2):
    """Fischschwarm-Spirale: Hunderte kleiner, farbiger Fischfiguren kreisen in einer aufsteigenden Spirale um
    eine Korallensäule – von gelben Doktorfischen unten bis zu silbernen Makrelen oben."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    grund(w, R, 0.9)
    H = int(16 * s + 8)
    for y in range(1, H):
        r = 1.5 * s + 0.8 + math.sin(y * 0.5) * 0.4
        for x, z in [(x, z) for x in range(-4, 5) for z in range(-4, 5)]:
            if x * x + z * z <= r * r:
                w.setze(x, y, z, w.b(f"{KORALLEN[(y // 4) % 5]}_coral_block"))
    farben = ["yellow_concrete", "orange_concrete", "light_blue_concrete", "cyan_concrete", "light_gray_concrete",
              "white_concrete"]
    rng = w.rng
    n = int(110 * s + 60)
    for i in range(n):
        t = i / n
        ang = t * 6 * math.pi + rng.random() * 0.6
        rr = R * 0.35 + R * 0.35 * math.sin(t * math.pi) + rng.random() * 2
        y = 3 + t * (H - 2) + rng.random() * 2
        x, z = math.cos(ang) * rr, math.sin(ang) * rr
        tx, tz = -math.sin(ang), math.cos(ang)
        f = w.b(farben[min(5, int(t * 6))])
        for k in range(2 if s < 1.2 else 3):
            w.setze(round(x - tx * k), round(y), round(z - tz * k), f)
        w.setze(round(x - tx * (k + 1)), round(y), round(z - tz * (k + 1)), w.b("white_concrete"), False)
    korallenbewuchs(w, 0.2)
    return w


def tanglabyrinth(seed, g=1):
    """Tang-Labyrinth: ein Irrgarten aus hohen Tangwänden zwischen Prismarin-Mauern, mit einer
    Schatzlichtung in der Mitte, auf der eine Truhe auf einem Seelaternen-Sockel steht."""
    w = _neu(seed)
    s = S[g]
    n = 5 + 2 * g
    zelle = 3
    R = n * zelle // 2 + 3
    grund(w, R + 2, 0.4)
    rng = w.rng
    besucht = {(n // 2, n // 2)}
    stapel = [(n // 2, n // 2)]
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
    H = int(4 * s + 3)
    p = prisma(w)
    for i in range(n * zelle + 1):
        for j in range(n * zelle + 1):
            ci, ri = divmod(i, zelle)
            cj, rj = divmod(j, zelle)
            wand = False
            if ri == 0 and rj == 0:
                wand = True
            elif ri == 0:
                wand = not (0 < ci < n and frozenset(((ci - 1, cj), (ci, cj))) in offen)
            elif rj == 0:
                wand = not (0 < cj < n and frozenset(((ci, cj - 1), (ci, cj))) in offen)
            if wand:
                x, z = x0 + i, x0 + j
                if (i, j) in ((n * zelle // 2, 0),):
                    continue
                if ri == 0 and rj == 0:
                    for y in range(1, H + 2):
                        w.setze(x, y, z, p(x, y, z))
                    w.setze(x, H + 2, z, w.b("sea_lantern") if (i + j) % (zelle * 4) == 0 else p(x, H + 2, z))
                else:
                    w.setze(x, 1, z, p(x, 1, z))
                    for y in range(2, H + 1):
                        w.setze(x, y, z, w.b("kelp_plant"))
                    w.setze(x, H + 1, z, w.b("kelp", age=25))
    for x in (x0 + n * zelle // 2 - 1, x0 + n * zelle // 2, x0 + n * zelle // 2 + 1):
        for y in range(1, H + 2):
            w.bloecke.pop((x, y, x0), None)
    m = x0 + (n // 2) * zelle + zelle // 2
    w.setze(m, 1, m, w.b("sea_lantern"))
    w.setze(m, 2, m, w.b("chest", facing="south", type="single", waterlogged=True))
    return w


def austernbank(seed, g=1):
    """Austernbank mit Riesenperlen: eine Bank aus Kalkfelsen voller Austern, darunter drei riesige, halb
    geöffnete Austern mit perlmuttschimmerndem Inneren und je einer großen, leuchtenden Perle."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    grund(w, R, 0.8)
    rng = w.rng
    kalk = M(w, [("calcite", 3), ("diorite", 1), ("bone_block", 1), ("white_terracotta", 1)])
    rn = Rauschen(w, 3)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) < R * 0.85 and rn(x, 0, z) > 0.45:
                for y in range(1, 1 + int(rn(x, 4, z) * 2 * s) + 1):
                    w.setze(x, y, z, kalk(x, y, z))
    n = 2 + g
    for k in range(n):
        a = k / n * 2 * math.pi + 0.3
        cx, cz = round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)
        r = (2.2 + rng.random()) * s + 1.8
        ow = 0.5 + rng.random() * 0.4
        aus = M(w, [("gray_terracotta", 2), ("light_gray_terracotta", 2), ("brown_terracotta", 1)])
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for z in range(int(cz - r) - 1, int(cz + r) + 2):
                dx, dz = x - cx, z - cz
                d = math.hypot(dx, dz * 1.2)
                if d > r:
                    continue
                rille = math.sin(math.atan2(dz, dx) * 10) > 0.6
                yb = 1 + (1 - d / r) * 1.2
                w.setze(x, round(yb), z, aus(x, 1, z) if not rille else w.b("light_gray_terracotta"))
                w.setze(x, round(yb) + 1, z, w.b("pink_glazed_terracotta", facing="north") if d < r - 1 else
                        aus(x, 2, z), False)
                xd = dx * math.cos(ow) - 0
                yl = 2 + round(-dx * math.sin(ow) * 0.9 + r * math.sin(ow) * 0.9 + (1 - d / r) * 1.0)
                if dx > -r * 0.2:
                    w.setze(x - round(dx * (1 - math.cos(ow)) * 0.6), yl, z, aus(x, yl, z))
        kugel(w, cx - r * 0.2, 3.5 + s * 0.4, cz, 0.9 + 0.5 * s, w.b("pearlescent_froglight", axis="y"))
    for _ in range(int(20 * s)):
        x, z = int((rng.random() - 0.5) * R * 1.7), int((rng.random() - 0.5) * R * 1.7)
        if math.hypot(x, z) < R:
            top = max([y for y in range(0, 6) if not w.frei(x, y, z)] or [0])
            w.setze(x, top + 1, z, w.b("gray_carpet") if rng.random() < 0.6 else w.b("dead_brain_coral",
                                                                                        waterlogged=True), False)
    korallenbewuchs(w, 0.12)
    return w


UNTERWASSER3 = {
    "nautilushaus": ("Nautilus-Haus", nautilushaus),
    "seeigelkuppeln": ("Seeigel-Kuppeln", seeigelkuppeln),
    "mantastatue": ("Mantarochen-Statue", mantastatue),
    "seepferdchen": ("Seepferdchen-Stall", seepferdchen),
    "taucherglocke": ("Taucherglocken-Station", taucherglocke),
    "versunkener_hafen": ("Versunkener Hafen", versunkener_hafen),
    "riesenkrabbe": ("Riesenkrabbe", riesenkrabbe),
    "anglerfisch": ("Anglerfisch", anglerfisch),
    "tiefseeschlote": ("Tiefsee-Schlote", tiefseeschlote),
    "korallenamphitheater": ("Korallen-Amphitheater", korallenamphitheater),
    "unterwasserbibliothek": ("Versunkene Bibliothek", unterwasserbibliothek),
    "seeschlange": ("Seeschlange", seeschlange),
    "schwammriff": ("Schwammriff", schwammriff),
    "uboot_wrack": ("U-Boot-Wrack", uboot_wrack),
    "ankerfriedhof": ("Ankerfriedhof", ankerfriedhof),
    "leuchtgrotte": ("Leuchtgrotte", leuchtgrotte),
    "meerhexenhuette": ("Meerhexen-Hütte", meerhexenhuette),
    "fischschwarm": ("Fischschwarm-Spirale", fischschwarm),
    "tanglabyrinth": ("Tang-Labyrinth", tanglabyrinth),
    "austernbank": ("Austernbank mit Riesenperlen", austernbank),
}

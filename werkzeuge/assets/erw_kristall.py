"""Kristallhöhlen II – zwanzig weitere Kristallbauten: Kristallorgel, Prismenturm, Spiegelsee mit Kristallinseln,
Quarzkathedrale, Kristallschlange, Kristallmeteor, Kristallglocke, Kristall-Leuchtfeuer, Kristall-Wendeltreppe,
Kristallrosengarten, Kristallschildkröte, Kristallbogengang, Kristallwoge, Hängende Kristalldecke, Kristallnest,
Kristallpyramide, Halbierte Geode, Kristall-Labyrinth, Lichtsäulen-Altar und Kristallfluss."""

from __future__ import annotations

import math

import numpy as np

from erw_basis import M, S, figur, hoehe
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen
from skulptur import Skulptur, dreh_x, dreh_y, ell, kap, kegel, torus

FARBEN = {
    "amethyst": ["amethyst_block", "purple_stained_glass", "magenta_stained_glass"],
    "eis": ["light_blue_stained_glass", "cyan_stained_glass", "white_stained_glass"],
    "smaragd": ["lime_stained_glass", "green_stained_glass", "emerald_block"],
    "rubin": ["red_stained_glass", "pink_stained_glass", "red_terracotta"],
    "quarz": ["quartz_block", "smooth_quartz", "white_stained_glass"],
}


def hoehlenboden(w, R, rand=0.0, H=0, art="tief"):
    """Felsiger Höhlenboden mit Pfützen und Kristallsplittern; optional Felsring (rand) als Höhlenwand."""
    rn = Rauschen(w, 4)
    f = M(w, [("deepslate", 3), ("tuff", 2), ("smooth_basalt", 1), ("calcite", 0.6)] if art == "tief" else
          [("stone", 3), ("andesite", 2), ("calcite", 1), ("tuff", 1)])
    rng = w.rng
    zellen = {}
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 2 * rn(x, 0, z):
                continue
            h = int(rn(x, 3, z) * 1.6)
            if rand and d > R * (1 - rand):
                h = int(H * min(1, (d - R * (1 - rand)) / (R * rand * 0.6)) + rn(x, 5, z) * 3)
            for y in range(-2, h + 1):
                w.setze(x, y, z, f(x, y, z))
            zellen[(x, z)] = h
            if h <= 1 and rng.random() < 0.025:
                w.setze(x, h + 1, z, w.b("amethyst_cluster", facing="up", waterlogged=False))
            elif h <= 1 and rng.random() < 0.02:
                w.setze(x, h + 1, z, w.b("glow_lichen", down=True, up=False, north=False, south=False, east=False,
                                         west=False, waterlogged=False))
    return zellen


def kristall(w, a, b, r0, farbe="amethyst", kern=True, spitze=True):
    """Kristallprisma von a nach b, sechseckig verjüngt, mit leuchtendem Kern und Spitze."""
    mats = [w.b(m) for m in FARBEN[farbe]]
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = np.linalg.norm(d)
    if L < 0.5:
        return
    d /= L
    lo = np.floor(np.minimum(a, b) - r0 - 1).astype(int)
    hi = np.ceil(np.maximum(a, b) + r0 + 1).astype(int)
    for x in range(lo[0], hi[0] + 1):
        for y in range(lo[1], hi[1] + 1):
            for z in range(lo[2], hi[2] + 1):
                p = np.array([x, y, z], float) - a
                t = p @ d
                if t < -0.3 or t > L + 0.3:
                    continue
                q = p - t * d
                rq = np.linalg.norm(q)
                r = r0 * (1 if t < L * 0.7 else max(0.0, (L - t) / (L * 0.3)))
                if rq <= r + 0.35:
                    if kern and rq < r * 0.35 and t < L * 0.8:
                        w.setze(x, y, z, w.b("sea_lantern"))
                    else:
                        w.setze(x, y, z, mats[(x + y * 2 + z) % len(mats)])
    if spitze:
        e = np.round(b + d * 0.6).astype(int)
        w.setze(int(e[0]), int(e[1]), int(e[2]), w.b("end_rod", facing="up" if d[1] >= 0 else "down"), False)


def buendel(w, x, y, z, n, L, r, farbe="amethyst", seed_off=0, neigung=0.5):
    rng = w.rng
    for k in range(n):
        a = rng.random() * 6.28
        nk = neigung * (0.3 + rng.random())
        ll = L * (0.5 + rng.random() * 0.6)
        d = (math.cos(a) * math.sin(nk), math.cos(nk), math.sin(a) * math.sin(nk))
        kristall(w, (x, y, z), (x + d[0] * ll, y + d[1] * ll, z + d[2] * ll), r * (0.6 + rng.random() * 0.5), farbe)


# ============================================================================ Bauten

def kristallorgel(seed, g=2):
    """Kristallorgel: an einer Felswand stehen in Reihen gestaffelte, senkrechte Kristallpfeifen wie die Pfeifen einer
    Orgel, davor ein Spieltisch aus Basalt mit leuchtenden Tasten und Kristallbänke."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = hoehlenboden(w, R)
    n = int(7 + 4 * s)
    for k in range(n):
        x = -n + 1 + k * 2
        h = int((4 + 6 * (1 - abs(k - n / 2) / (n / 2))) * s + 4)
        r = 0.7 + 0.25 * s
        farbe = ["amethyst", "eis", "amethyst", "quarz"][k % 4]
        kristall(w, (x, 0, -int(R * 0.3)), (x, h, -int(R * 0.3)), r, farbe)
        kristall(w, (x + 1, 0, -int(R * 0.3) - 2), (x + 1, int(h * 0.7), -int(R * 0.3) - 2), r * 0.8, "amethyst")
    for x in range(-n, n + 1):
        for y in range(1, int(4 + 3 * s)):
            w.setze(x, y, -int(R * 0.3) - 4, w.b("smooth_basalt") if (x + y) % 3 else w.b("polished_basalt", axis="y"))
    for x in range(-3, 4):
        w.setze(x, 1, 2, w.b("polished_blackstone"))
        w.setze(x, 2, 2, w.b("polished_blackstone_slab", type="bottom", waterlogged=False))
        w.setze(x, 2, 1, w.b("sea_lantern") if x % 2 else w.b("quartz_slab", type="bottom", waterlogged=False))
    for x in range(-2, 3):
        w.setze(x, 1, 4, w.b("amethyst_block"))
    return w


def prismenturm(seed, g=2):
    """Prismenturm: ein hoher, sechseckiger Turm aus klarem Kristall, an dessen Spitze ein Leuchtkern sitzt; sein
    Licht fällt in sieben Regenbogenfarben als Glasbahnen auf den Boden ringsum."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hoehlenboden(w, R, art="hell")
    H = int(12 * s + 8)
    kristall(w, (0, 0, 0), (0, H, 0), 2 + 0.8 * s, "quarz")
    kugel(w, 0, H + 1, 0, 1.6 + 0.4 * s, w.b("sea_lantern"))
    farben = ["red", "orange", "yellow", "lime", "light_blue", "blue", "purple"]
    for k, f in enumerate(farben):
        a = -math.pi / 2 + (k - 3) * 0.22
        for t in range(int(3 + s), int(R * 0.9)):
            x, z = round(math.cos(a) * t), round(math.sin(a) * t)
            y = hoehe(w, x, z, 4)
            w.setze(x, y, z, w.b(f"{f}_stained_glass"))
            if t % 4 == 0:
                w.setze(x, y + 1, z, w.b("end_rod", facing="up"), False)
    buendel(w, 3, 0, 3, 3, 4 * s + 2, 0.8, "eis")
    buendel(w, -3, 0, 2, 3, 3 * s + 2, 0.7, "quarz")
    return w


def spiegelsee(seed, g=2):
    """Spiegelsee mit Kristallinseln: ein dunkler, stiller Höhlensee, auf dem kleine Felsinseln mit leuchtenden
    Kristallbüscheln liegen, verbunden durch Trittsteine; die Kristalle spiegeln sich im Wasser."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = hoehlenboden(w, R, rand=0.18, H=int(4 + 3 * s))
    rn = Rauschen(w, 3)
    for (x, z), h in zellen.items():
        if math.hypot(x, z) < R * 0.78:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("water", level=0))
            w.setze(x, -2, z, w.b("deepslate") if rn(x, 1, z) < 0.8 else w.b("sea_lantern"))
            for y in range(1, 3):
                w.bloecke.pop((x, y, z), None)
    inseln = []
    for k in range(int(3 + 2 * s)):
        a = k * 2.4
        r = R * (0.15 + 0.45 * ((k * 0.37) % 1))
        cx, cz = round(math.cos(a) * r), round(math.sin(a) * r)
        ri = 1.5 + s * 0.6
        kugel(w, cx, 0, cz, ri, w.b("smooth_basalt"), ry=1.2)
        buendel(w, cx, 1, cz, int(2 + s), 3 + 2 * s, 0.6 + 0.2 * s, ["amethyst", "eis", "smaragd"][k % 3])
        inseln.append((cx, cz))
    for (a, b) in zip(inseln, inseln[1:]):
        n = int(math.hypot(b[0] - a[0], b[1] - a[1]))
        for t in range(0, n + 1, 2):
            q = t / max(1, n)
            w.setze(round(a[0] + (b[0] - a[0]) * q), 1, round(a[1] + (b[1] - a[1]) * q),
                    w.b("polished_deepslate_slab", type="bottom", waterlogged=False), False)
    return w


def quarzkathedrale(seed, g=2):
    """Quarzkathedrale: in einer Höhle sind gewaltige Quarzkristalle zu einem natürlichen Kirchenschiff
    zusammengewachsen – zwei Reihen schräger Säulen bilden ein Spitzbogengewölbe, am Ende ein Rosettenkristall."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    hoehlenboden(w, R, art="hell")
    L = int(R * 0.75)
    H = int(8 * s + 6)
    B = int(3 + 1.5 * s)
    for z in range(-L, L + 1, int(3 + s)):
        for sx in (-1, 1):
            kristall(w, (sx * (B + 2), 0, z), (-sx * 0.5, H + 2, z), 0.7 + 0.3 * s, "quarz", spitze=False)
    for z in range(-L, L + 1):
        for x in range(-B, B + 1):
            w.setze(x, 0, z, w.b("smooth_quartz") if (x + z) % 2 else w.b("calcite"))
    for x in range(-B - 2, B + 3):
        for y in range(1, H + 4):
            d = math.hypot(x, y - H * 0.6)
            if d <= B + 1.5:
                ring = abs(math.sin(math.atan2(y - H * 0.6, x) * 6)) < 0.3 or d > B + 0.5
                w.setze(x, y, -L - 1, w.b("quartz_block") if ring else
                        w.b(["purple_stained_glass", "light_blue_stained_glass", "pink_stained_glass"][int(d) % 3]))
    for k in range(int(3 + s)):
        z = -L + 3 + k * int(2 * L / (3 + s))
        for x in (-2, 2):
            w.setze(x, 1, z, w.b("quartz_stairs", facing="north", half="bottom", shape="straight", waterlogged=False))
    return w


def kristallschlange(seed, g=2):
    """Kristallschlange: eine gewaltige Schlange aus Stein, deren Rücken mit Kristallzacken besetzt ist, windet sich in
    Bögen über den Höhlenboden, den Kopf erhoben mit leuchtenden Kristallaugen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hoehlenboden(w, R)
    L = R * 0.85
    pts = []
    n = int(L * 4)
    for k in range(n):
        t = k / n
        x = -L + 2 * L * t
        z = math.sin(t * math.pi * 2.2) * R * 0.35
        y = 1 + abs(math.sin(t * math.pi * 4)) * (1.5 + s) if t < 0.85 else 1 + (t - 0.85) / 0.15 * (5 + 3 * s)
        pts.append((x, y, z, t))
    rohr(w, pts, 0.8 + 0.3 * s, 1.6 + 0.6 * s, M(w, [("smooth_basalt", 2), ("deepslate_tiles", 1),
                                                       ("polished_deepslate", 1)]), rauh=0.05)
    for k in range(0, len(pts) - 4, int(5 + s)):
        x, y, z, t = pts[k]
        r = 0.8 + 0.3 * s + (1.6 + 0.6 * s - 0.8 - 0.3 * s) * t
        kristall(w, (x, y + r * 0.6, z), (x, y + r + 2 + 2 * s * t, z), 0.4 + 0.3 * s * t, "amethyst")
    hx, hy, hz, _ = pts[-1]
    kugel(w, hx + 1, hy, hz, 2 + 0.7 * s, w.b("smooth_basalt"), ry=1.4 + 0.4 * s)
    for sz in (-1, 1):
        w.setze(round(hx + 2), round(hy + 1), round(hz + sz * (1 + 0.5 * s)), w.b("sea_lantern"))
    kristall(w, (hx, hy + 1, hz), (hx - 2, hy + 4 + 2 * s, hz), 0.6 + 0.2 * s, "rubin")
    return w


def kristallmeteor(seed, g=2):
    """Kristallmeteor: ein vom Himmel gestürzter, glühender Kristallbrocken steckt schräg in einem Krater, von dem
    strahlenförmig Kristallsplitter in den Boden gefahren sind; verbrannte Erde und Rauch ringsum."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = hoehlenboden(w, R, art="hell")
    rk = R * 0.45
    for (x, z), h in zellen.items():
        d = math.hypot(x, z)
        if d < rk:
            tief = int((1 - (d / rk) ** 2) * (3 + 2 * s))
            for y in range(-tief, h + 1):
                w.bloecke.pop((x, y, z), None)
            w.setze(x, -tief - 1, z, w.b("magma_block") if d < rk * 0.3 else w.b("blackstone"))
        elif d < rk + 2:
            w.setze(x, h + 1, z, w.b("blackstone") if (x + z) % 2 else w.b("basalt", axis="y"))
    kristall(w, (0, -3 - 2 * s, 0), (2 + s, 6 + 5 * s, -1 - s), 2 + 1.0 * s, "rubin")
    kristall(w, (1, -2, 1), (-1, 3 + 3 * s, 3 + s), 1.2 + 0.5 * s, "amethyst")
    for k in range(8):
        a = k / 8 * 2 * math.pi
        x0, z0 = math.cos(a) * rk * 0.6, math.sin(a) * rk * 0.6
        kristall(w, (x0, 0, z0), (x0 + math.cos(a) * (2 + 2 * s), 2 + s, z0 + math.sin(a) * (2 + 2 * s)),
                 0.5 + 0.2 * s, ["rubin", "amethyst"][k % 2])
    for k in range(3):
        w.setze(k - 1, int(8 + 5 * s), 0, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                waterlogged=False), False) if False else None
    return w


def kristallglocke(seed, g=2):
    """Kristallglocke: zwischen zwei aufragenden Kristallpfeilern hängt an Ketten eine riesige, durchscheinende Glocke
    aus Kristall mit leuchtendem Klöppel, darunter ein runder Klangteich."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    hoehlenboden(w, R)
    H = int(10 * s + 8)
    B = int(4 + 2 * s)
    for sx in (-1, 1):
        kristall(w, (sx * B, 0, 0), (sx * (B - 1), H + 2, 0), 1.2 + 0.4 * s, "amethyst")
    for x in range(-B, B + 1):
        w.setze(x, H, 0, w.b("polished_deepslate"))
    rg = 2 + 1.2 * s
    yb = H - 2
    for y in range(int(yb - 2.4 * rg), yb):
        t = (yb - y) / (2.4 * rg)
        r = rg * (0.45 + 0.55 * t ** 0.7) + (0.6 if t > 0.92 else 0)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(x, z)
                if r - 1 < d <= r:
                    w.setze(x, y, z, w.b("light_blue_stained_glass") if (x + y) % 3 else w.b("purple_stained_glass"))
    for y in range(int(yb - 2.4 * rg) + 1, H):
        w.setze(0, y, 0, w.b("chain", axis="y", waterlogged=False))
    kugel(w, 0, yb - 2.4 * rg + 0.5, 0, 0.9, w.b("sea_lantern"))
    for x in range(-int(rg) - 2, int(rg) + 3):
        for z in range(-int(rg) - 2, int(rg) + 3):
            if math.hypot(x, z) <= rg + 1.5:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("amethyst_block"))
                w.bloecke.pop((x, 1, z), None)
    return w


def kristallleuchtfeuer(seed, g=2):
    """Kristall-Leuchtfeuer: auf einem Felsen am Rand eines unterirdischen Sees steht ein Turm aus Basaltblöcken, auf
    dessen Spitze statt einer Laterne ein riesiger, leuchtender Kristall in einer Fassung strahlt."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = hoehlenboden(w, R)
    for (x, z), h in zellen.items():
        if z > R * 0.1 and math.hypot(x, z) < R - 1:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("water", level=0))
            for y in range(1, 3):
                w.bloecke.pop((x, y, z), None)
    kugel(w, 0, 0, 0, 3 + s, w.b("smooth_basalt"), ry=2.5)
    H = int(8 * s + 6)
    rt = int(1.5 + s * 0.6)
    for y in range(2, H):
        for x in range(-rt - 1, rt + 2):
            for z in range(-rt - 1, rt + 2):
                if math.hypot(x, z) <= rt + 0.4:
                    w.setze(x, y, z, w.b("polished_basalt", axis="y") if (y // 3) % 2 else w.b("deepslate_bricks"))
    for x in range(-rt - 2, rt + 3):
        for z in range(-rt - 2, rt + 3):
            if math.hypot(x, z) <= rt + 1.6:
                w.setze(x, H, z, w.b("polished_deepslate"))
                if math.hypot(x, z) > rt + 0.6:
                    w.setze(x, H + 1, z, w.b("deepslate_brick_wall", up=True, north="none", south="none",
                                             east="none", west="none", waterlogged=False))
    kristall(w, (0, H + 1, 0), (0, H + 6 + 3 * s, 0), 1.3 + 0.4 * s, "eis")
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.78
        kristall(w, (0, H + 1, 0), (math.cos(a) * 2.5, H + 3 + s, math.sin(a) * 2.5), 0.5, "eis", kern=False)
    return w


def kristalltreppe(seed, g=2):
    """Kristall-Wendeltreppe: um eine zentrale, hohe Kristallsäule windet sich eine freischwebende Treppe aus
    Kristallplatten nach oben zu einer kleinen Aussichtsplattform, von der Kristalle herabhängen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    hoehlenboden(w, R)
    H = int(14 * s + 8)
    kristall(w, (0, 0, 0), (0, H + 2, 0), 1.5 + 0.4 * s, "amethyst", spitze=False)
    r = 3 + s
    for k in range(H * 3):
        a = k * 0.35
        y = 1 + k // 3
        if y > H:
            break
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        w.setze(x, y, z, w.b("purple_stained_glass") if k % 2 else w.b("amethyst_block"), False)
        if k % 6 == 0:
            w.setze(round(math.cos(a) * (r + 1)), y + 1, round(math.sin(a) * (r + 1)), w.b("end_rod", facing="up"),
                    False)
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            if math.hypot(x, z) <= r + 0.5:
                w.setze(x, H + 1, z, w.b("calcite") if math.hypot(x, z) > 2 else w.b("amethyst_block"))
    rng = w.rng
    for k in range(int(4 + 2 * s)):
        a = rng.random() * 6.28
        x, z = math.cos(a) * (r - 0.5), math.sin(a) * (r - 0.5)
        kristall(w, (x, H, z), (x, H - 2 - rng.random() * 3 * s, z), 0.5, "amethyst", kern=False)
    return w


def kristallrosengarten(seed, g=1):
    """Kristallrosengarten: aus dem Höhlenboden wachsen mannshohe Rosen, deren Blüten aus geschichteten Kristall-
    blättern bestehen, auf Stielen aus Moosstein, dazwischen leuchtende Flechten und Wege aus Calcit."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = hoehlenboden(w, R)
    for (x, z), h in zellen.items():
        if abs(x - math.sin(z / 3) * 2) < 1:
            w.setze(x, h, z, w.b("calcite"))
    rng = w.rng
    farben = [("red_stained_glass", "pink_stained_glass"), ("purple_stained_glass", "magenta_stained_glass"),
              ("light_blue_stained_glass", "white_stained_glass")]
    for k in range(int(5 + 4 * s)):
        a = rng.random() * 6.28
        r = R * (0.2 + rng.random() * 0.65)
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        if abs(x - math.sin(z / 3) * 2) < 3:
            continue
        H = int(3 + rng.random() * 3 * s)
        for y in range(1, H):
            w.setze(x, y, z, w.b("mossy_cobblestone_wall", up=True, north="none", south="none", east="none",
                                 west="none", waterlogged=False))
        if H > 3:
            w.setze(x + 1, H // 2, z, w.b("moss_block"))
        f1, f2 = farben[k % 3]
        rb = 1.2 + 0.4 * s
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                for dy in range(0, 3):
                    d = math.hypot(dx, dz)
                    if d <= rb - dy * 0.4 and (dy == 0 or d > rb - dy * 0.4 - 1.2):
                        w.setze(x + dx, H + dy, z + dz, w.b(f1) if (dx + dz + dy) % 2 else w.b(f2), False)
        w.setze(x, H, z, w.b("sea_lantern"))
    return w


def kristallschildkroete(seed, g=2):
    """Kristallschildkröte: eine riesige, steinerne Schildkröte ruht auf dem Höhlenboden; ihr gewölbter Panzer ist
    ein Wald aus Kristallen in Grün und Türkis, aus dem kleine Wasserrinnsale laufen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hoehlenboden(w, R)
    u = 1.0 * s + 0.6
    Sk = Skulptur(w, u)
    Sk.mat("p", lambda x, y, z, *a: w.b("mossy_cobblestone") if (x + z) % 3 == 0 else w.b("smooth_basalt"))
    Sk.mat("h", w.b("tuff"))
    Sk.mat("a", w.b("sea_lantern"))
    Sk.plus(ell(0, 1.6, 0, 6.0, 3.0, 4.8), "p")
    Sk.minus(lambda X, Y, Z: Y < 0.6)
    Sk.plus(ell(7.0, 1.6, 0, 2.0, 1.4, 1.4), "h")
    Sk.plus(ell(8.3, 2.0, 0.8, 0.3, 0.3, 0.3), "a")
    Sk.plus(ell(8.3, 2.0, -0.8, 0.3, 0.3, 0.3), "a")
    for sx in (-4, 4):
        for sz in (-4, 4):
            Sk.plus(ell(sx, 0.8, sz, 1.5, 0.8, 1.2), "h")
    Sk.plus(kap((-6.0, 1.2, 0), (-7.8, 0.6, 0), 0.5, 0.2), "h")
    Sk.rendern((-9, 0, -7), (10, 6, 7), versatz=(0.5, 1, 0.5))
    rng = w.rng
    for k in range(int(8 + 6 * s)):
        a = rng.random() * 6.28
        r = rng.random() * 0.8
        x, z = math.cos(a) * r * 5.5 * u, math.sin(a) * r * 4.3 * u
        y = hoehe(w, round(x), round(z), int(12 * u) + 4)
        nk = r * 0.8
        kristall(w, (x, y, z), (x + math.cos(a) * nk * 3, y + (1.2 + 1.6 * (1 - r)) * u, z + math.sin(a) * nk * 3),
                 0.4 + 0.3 * s, ["smaragd", "eis"][k % 2])
    return w


def kristallbogengang(seed, g=2):
    """Kristallbogengang: ein Weg aus Calcitplatten führt durch eine Reihe von Spitzbögen, die jeweils aus zwei sich
    zuneigenden Kristallen gebildet werden, in wechselnden Farben, mit Lichtern an den Scheiteln."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hoehlenboden(w, R)
    L = int(R * 0.8)
    B = int(2 + s)
    H = int(5 + 3 * s)
    for z in range(-L, L + 1):
        for x in range(-B + 1, B):
            w.setze(x, 0, z, w.b("calcite") if (z + x) % 3 else w.b("smooth_quartz"))
            w.bloecke.pop((x, 1, z), None)
    farben = ["amethyst", "eis", "rubin", "smaragd"]
    for k, z in enumerate(range(-L + 1, L, int(3 + s))):
        f = farben[k % 4]
        for sx in (-1, 1):
            kristall(w, (sx * (B + 1), 0, z), (sx * 0.3, H, z), 0.6 + 0.25 * s, f, spitze=False)
        w.setze(0, H + 1, z, w.b("sea_lantern"))
    return w


def kristallwoge(seed, g=2):
    """Kristallwoge: eine gewaltige Welle, die mitten im Brechen zu Kristall erstarrt ist – ein überhängender Kamm
    aus blauem und türkisem Kristall mit weißer Gischt aus Calcit über einem Kiesstrand."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = hoehlenboden(w, R, art="hell")
    for (x, z), h in zellen.items():
        if z > R * 0.3:
            w.setze(x, h, z, w.b("gravel") if (x + z) % 3 else w.b("sand"))
    L = int(R * 0.8)
    H = 6 * s + 4
    for x in range(-L, L + 1):
        f = 1 - (x / L) ** 2
        for k in range(int(30 * s) + 10):
            t = k / (30 * s + 10)
            a = t * math.pi * 1.25
            r = H * f * 0.9
            y = r * math.sin(a)
            z = -r * math.cos(a) + r * 0.2 - R * 0.1
            th = 0.6 + 1.2 * (1 - t) * f
            for dz in range(-int(th), int(th) + 1):
                yy, zz = round(y), round(z + dz)
                if yy < 0:
                    continue
                gischt = t > 0.85
                w.setze(x, yy, zz, w.b("calcite") if gischt and (x + yy) % 2 else
                        w.b(["light_blue_stained_glass", "cyan_stained_glass", "blue_stained_glass"][(x + yy + zz) % 3]),
                        False)
    return w


def kristalldecke(seed, g=2):
    """Hängende Kristalldecke: unter einer niedrigen Felsdecke, die auf natürlichen Säulen ruht, hängen hunderte Kristall-
    zapfen in Violett und Weiß, deren Spitzen leuchten; darunter ein Pfad zwischen Pfützen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = hoehlenboden(w, R)
    H = int(8 * s + 6)
    rn = Rauschen(w, 4)
    f = M(w, [("deepslate", 2), ("tuff", 1), ("calcite", 0.5)])
    for (x, z), h in zellen.items():
        if math.hypot(x, z) > R * 0.85:
            continue
        hd = H + int(rn(x, 2, z) * 2)
        offen = z > R * 0.3
        if not offen:
            for y in range(hd, hd + 2):
                w.setze(x, y, z, f(x, y, z))
    rng = w.rng
    for k in range(int(5 + 3 * s)):
        a = rng.random() * 6.28
        r = R * rng.random() * 0.75
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        if z > R * 0.3:
            continue
        rr = 1 + rng.random() * s
        for y in range(1, H + 1):
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if math.hypot(dx, dz) <= rr * (0.7 + 0.4 * abs(y / H - 0.5)):
                        w.setze(x + dx, y, z + dz, f(x + dx, y, z + dz))
    for k in range(int(20 + 18 * s)):
        x, z = int((rng.random() - 0.5) * R * 1.6), int((rng.random() - 0.5) * R * 1.6)
        if math.hypot(x, z) > R * 0.8 or z > R * 0.3:
            continue
        L = 1.5 + rng.random() * (2 + 2 * s)
        kristall(w, (x, H, z), (x, H - L, z), 0.4 + rng.random() * 0.4 * s, ["amethyst", "quarz"][k % 2], kern=False)
    for (x, z), h in zellen.items():
        if math.hypot(x, z) < R * 0.8 and rn(x, 7, z) > 0.72:
            w.setze(x, 0, z, w.b("water", level=0))
            w.bloecke.pop((x, 1, z), None)
    return w


def kristallnest(seed, g=1):
    """Kristallnest: in einer Mulde liegt ein riesiges Nest aus versteinerten Ästen und Wurzeln, darin große, schillernde
    Kristalleier mit leuchtendem Inneren, ringsum ausgebrochene Schalensplitter."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    hoehlenboden(w, R)
    rn_ = 3 + 1.5 * s
    rng = w.rng
    for k in range(int(40 * s + 20)):
        a = rng.random() * 6.28
        y = rng.random() * (1.5 + s)
        L = 2 + rng.random() * 3
        r = rn_ + rng.random() * 1.2
        x0, z0 = math.cos(a) * r, math.sin(a) * r
        b = a + math.pi / 2 + (rng.random() - 0.5)
        for t in range(int(L * 2)):
            q = t / 2 - L / 2
            w.setze(round(x0 + math.cos(b) * q), round(1 + y), round(z0 + math.sin(b) * q),
                    w.b("stripped_dark_oak_wood", axis="x") if t % 2 else w.b("mangrove_roots", waterlogged=False),
                    False)
    for x in range(-int(rn_), int(rn_) + 1):
        for z in range(-int(rn_), int(rn_) + 1):
            if math.hypot(x, z) < rn_ - 0.5:
                w.setze(x, 1, z, w.b("moss_block") if (x + z) % 3 else w.b("hay_block", axis="y"))
    eier = [(0, 0, "amethyst"), (1.5 + 0.5 * s, 1, "eis"), (-1.2 - 0.4 * s, -1.2, "smaragd")]
    for (x, z, f) in eier[:2 + (g >= 1)]:
        re = 1.0 + 0.5 * s
        mats = FARBEN[f]
        for dx in range(-int(re) - 1, int(re) + 2):
            for dy in range(0, int(re * 2.6) + 1):
                for dz in range(-int(re) - 1, int(re) + 2):
                    e = (dx / re) ** 2 + ((dy - re * 1.2) / (re * 1.35)) ** 2 + (dz / re) ** 2
                    if e <= 1:
                        w.setze(round(x + dx), 2 + dy, round(z + dz), w.b("sea_lantern") if e < 0.25 else
                                w.b(mats[(dx + dy + dz) % 3]))
    for k in range(int(4 + 2 * s)):
        a = rng.random() * 6.28
        r = rn_ + 2 + rng.random() * 2
        w.setze(round(math.cos(a) * r), 1, round(math.sin(a) * r), w.b("amethyst_cluster", facing="up",
                                                                      waterlogged=False))
    return w


def kristallpyramide(seed, g=2):
    """Kristallpyramide: eine glatte, vierseitige Pyramide aus geschichtetem Kristall in Farbverläufen von Violett bis
    Weiß, mit leuchtenden Kanten, auf einem Sockel aus Basalt mit Treppen an allen Seiten."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    hoehlenboden(w, R)
    A = int(R * 0.55)
    for x in range(-A - 2, A + 3):
        for z in range(-A - 2, A + 3):
            w.setze(x, 1, z, w.b("polished_basalt", axis="y") if max(abs(x), abs(z)) > A else
                    w.b("polished_deepslate"))
    for k in range(A + 1):
        a = A - k
        f = ["purple_stained_glass", "magenta_stained_glass", "pink_stained_glass", "white_stained_glass"][
            min(3, k * 4 // (A + 1))]
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                if max(abs(x), abs(z)) == a or k == 0:
                    kante = abs(x) == a and abs(z) == a
                    w.setze(x, 2 + k, z, w.b("sea_lantern") if kante else w.b(f))
    for d in range(3):
        for t in range(-1, 2):
            for sx, sz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                x = sx * (A + 3 + d) + (t if sz else 0)
                z = sz * (A + 3 + d) + (t if sx else 0)
                w.setze(x, 1 - d + 1 - 1, z, w.b("polished_deepslate_stairs",
                                                 facing={(1, 0): "west", (-1, 0): "east", (0, 1): "north",
                                                         (0, -1): "south"}[(sx, sz)], half="bottom",
                                                 shape="straight", waterlogged=False)) if d == 0 else None
    return w


def halbierte_geode(seed, g=2):
    """Halbierte Geode: zwei Hälften einer riesigen Geode liegen aufgeklappt nebeneinander und zeigen ihre Schichten
    aus Basalt, Calcit und Amethyst und das funkelnde Kristallinnere."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hoehlenboden(w, R)
    rg = 4 * s + 3.5
    rng = w.rng
    for sx in (-1, 1):
        cx = sx * (rg + 1.5)
        for x in range(int(cx - rg) - 2, int(cx + rg) + 3):
            for y in range(1, int(2 * rg) + 3):
                for z in range(-int(rg) - 2, int(rg) + 3):
                    lx = (x - cx) * sx
                    d = math.sqrt(lx ** 2 + (y - rg - 1) ** 2 + z ** 2)
                    if lx > 0.5 or d > rg:
                        continue
                    if lx > -0.5:
                        b = "smooth_basalt" if d > rg - 1 else "calcite" if d > rg - 2 else "amethyst_block" \
                            if d > rg - 3 else "budding_amethyst" if rng.random() < 0.2 else "purple_stained_glass"
                        if d < rg - 3 and rng.random() < 0.6:
                            continue
                        w.setze(x, y, z, w.b(b))
                    elif d > rg - 1:
                        w.setze(x, y, z, w.b("smooth_basalt"))
                    elif d > rg - 2:
                        w.setze(x, y, z, w.b("calcite"))
                    elif d > rg - 3:
                        w.setze(x, y, z, w.b("amethyst_block"))
                        if rng.random() < 0.3:
                            w.setze(x + sx, y, z, w.b("amethyst_cluster", facing="east" if sx > 0 else "west",
                                                      waterlogged=False), False)
    return w


def kristalllabyrinth(seed, g=2):
    """Kristall-Labyrinth: ein Irrgarten, dessen Wände aus dicht stehenden Kristallsäulen in wechselnden Farben
    bestehen; in der Mitte ein Podest mit einem großen Leuchtkristall."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    hoehlenboden(w, R)
    n = int(4 + 2 * s)
    zelle = 3
    rng = np.random.default_rng(seed)
    besucht = set()
    wand = set()
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            wand.add((i, j))
    stapel = [(1 - n % 2, 1 - n % 2)]
    besucht.add(stapel[0])
    while stapel:
        i, j = stapel[-1]
        nb = [(i + di, j + dj) for di, dj in ((2, 0), (-2, 0), (0, 2), (0, -2)) if -n < i + di < n and -n < j + dj < n
              and (i + di, j + dj) not in besucht]
        if not nb:
            stapel.pop()
            continue
        k = nb[int(rng.integers(len(nb)))]
        wand.discard((i, j))
        wand.discard(k)
        wand.discard(((i + k[0]) // 2, (j + k[1]) // 2))
        besucht.add(k)
        stapel.append(k)
    for i in range(-1, 2):
        for j in range(-1, 2):
            wand.discard((i, j))
    wand.discard((0, n))
    wand.discard((0, n - 1))
    farben = ["amethyst", "eis", "smaragd", "rubin"]
    for (i, j) in wand:
        x, z = i * (zelle - 1), j * (zelle - 1)
        if math.hypot(x, z) > R - 1:
            continue
        h = int(3 + s + (i * 7 + j * 3) % 3)
        kristall(w, (x, 0, z), (x, h, z), 0.9, farben[(i + j) % 4], kern=False, spitze=False)
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, 1, z, w.b("polished_deepslate"))
    kristall(w, (0, 1, 0), (0, 6 + 3 * s, 0), 1.0 + 0.3 * s, "quarz")
    return w


def lichtsaeulenaltar(seed, g=1):
    """Lichtsäulen-Altar: ein runder, gestufter Altar aus poliertem Schwarzstein, in dessen Mitte ein Kristall in einer
    Krone steckt, aus dem eine Lichtsäule senkrecht nach oben steigt; ringsum kniende Kristallwächter."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    hoehlenboden(w, R)
    for k in range(3):
        r = R * 0.45 - k * 1.6
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                if math.hypot(x, z) <= r:
                    w.setze(x, 1 + k, z, w.b("polished_blackstone_bricks") if k < 2 else w.b("polished_blackstone"))
    yt = 4
    kristall(w, (0, yt, 0), (0, yt + 3 + s, 0), 0.9 + 0.3 * s, "amethyst", spitze=False)
    for k in range(6):
        a = k / 6 * 2 * math.pi
        w.setze(round(math.cos(a) * 1.6), yt, round(math.sin(a) * 1.6), w.b("gold_block"))
    for y in range(int(yt + 4 + s), int(yt + 14 + 8 * s)):
        w.setze(0, y, 0, w.b("end_rod", facing="up") if y % 2 else w.b("white_stained_glass"))
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.78
        x, z = round(math.cos(a) * (R * 0.55)), round(math.sin(a) * (R * 0.55))
        kristall(w, (x, 0, z), (x * 0.9, 3 + 2 * s, z * 0.9), 0.7 + 0.2 * s, "eis")
    return w


def kristallfluss(seed, g=2):
    """Kristallfluss: durch eine Höhle zieht sich ein Bachbett, in dem statt Wasser unzählige Kristallsplitter in
    Blau und Türkis glitzern; an den Ufern wachsen schräge Kristallsäulen und Leuchtflechten."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = hoehlenboden(w, R)
    rng = w.rng
    bw = 2 + s
    for (x, z), h in zellen.items():
        mz = math.sin(x / 5) * R * 0.2
        d = abs(z - mz)
        if d < bw:
            w.setze(x, 0, z, w.b(["light_blue_stained_glass", "cyan_stained_glass", "blue_stained_glass",
                                  "sea_lantern"][int(rng.integers(4))] if rng.random() < 0.85 else "calcite"))
            w.bloecke.pop((x, 1, z), None)
            if rng.random() < 0.15:
                w.setze(x, 1, z, w.b("amethyst_cluster", facing="up", waterlogged=False)) if False else \
                    w.setze(x, 1, z, w.b("light_blue_stained_glass"))
    for k in range(int(6 + 4 * s)):
        x = int((rng.random() - 0.5) * R * 1.6)
        mz = math.sin(x / 5) * R * 0.2
        sz = 1 if k % 2 else -1
        z = mz + sz * (bw + 1 + rng.random() * 3)
        kristall(w, (x, 0, z), (x + (rng.random() - 0.5) * 3, 3 + rng.random() * 4 * s, z + sz * 2),
                 0.5 + rng.random() * 0.4 * s, ["eis", "amethyst"][k % 2])
    return w


KRISTALL3 = {
    "kristallorgel": ("Kristallorgel", kristallorgel),
    "prismenturm": ("Prismenturm", prismenturm),
    "spiegelsee": ("Spiegelsee mit Kristallinseln", spiegelsee),
    "quarzkathedrale": ("Quarzkathedrale", quarzkathedrale),
    "kristallschlange": ("Kristallschlange", kristallschlange),
    "kristallmeteor": ("Kristallmeteor", kristallmeteor),
    "kristallglocke": ("Kristallglocke", kristallglocke),
    "kristallleuchtfeuer": ("Kristall-Leuchtfeuer", kristallleuchtfeuer),
    "kristalltreppe": ("Kristall-Wendeltreppe", kristalltreppe),
    "kristallrosengarten": ("Kristallrosengarten", kristallrosengarten),
    "kristallschildkroete": ("Kristallschildkröte", kristallschildkroete),
    "kristallbogengang": ("Kristallbogengang", kristallbogengang),
    "kristallwoge": ("Kristallwoge", kristallwoge),
    "kristalldecke": ("Hängende Kristalldecke", kristalldecke),
    "kristallnest": ("Kristallnest", kristallnest),
    "kristallpyramide": ("Kristallpyramide", kristallpyramide),
    "halbierte_geode": ("Halbierte Geode", halbierte_geode),
    "kristalllabyrinth": ("Kristall-Labyrinth", kristalllabyrinth),
    "lichtsaeulenaltar": ("Lichtsäulen-Altar", lichtsaeulenaltar),
    "kristallfluss": ("Kristallfluss", kristallfluss),
}

"""Elfenreich – anmutige Elfenarchitektur aus weißem Stein, Silber und Gold: Paläste mit schlanken Türmen,
Mondtempel, Mallornbäume mit Fletts, Brücken, Tore, Gärten, Hafen und Silberwald.
Boden y = 0."""

from __future__ import annotations

import math

import modbloecke as MB
import pracht as P
import wald2
from flora import _lv, _neu, _r, _stil, bogen, linie
from lib import Rauschen, einfuegen
from pracht import Mat, gelaende
from wald import Stueck, _fertig, hohes
from wueste_eis import kuppel

U = [0.6, 1.0, 1.7, 2.8]
WEISS = ["polished_diorite", "calcite", "smooth_quartz", "quartz_bricks", "diorite", "calcite"]


def stil(w, seed, **kw):
    d = dict(wand=WEISS, sockel="kalkstein", gesims="quartz",
             dach="mcw_gruen" if _stil(seed) == 0 else "mcw_blau", holz="birch", fensterart="bogen", laeden=False,
             blumen=0.6)
    d.update(kw)
    return P.Stil(w, **d)


def gold(w):
    return w.b("gold_block")


def laub_gold(w, stil_):
    if stil_ == 0:
        return MB.mod(w, "biomesoplenty:yellow_autumn_leaves", "birch_leaves",
                      {"persistent": True, "distance": 1, "waterlogged": False}, persistent=True, distance=7,
                      waterlogged=False)
    return _lv(w, "birch")


# ============================================================================ Bausteine

def elfenturm(w, cx, cz, y0, H, R, stil_=0, M=None, balkone=2):
    """Schlanker Rundturm mit Balkonringen, Spitzbogenfenstern und geschwungener, goldbekrönter Spitze."""
    M = M or Mat(w, WEISS)
    for y in range(y0, y0 + H):
        t = (y - y0) / H
        r = R * (1 - 0.12 * t)
        for k in range(int(r * 8) + 6):
            a = k / (r * 8 + 6) * 6.28
            x, z = cx + round(math.cos(a) * r), cz + round(math.sin(a) * r)
            fenster = (y - y0) % 7 in (3, 4) and k % max(2, int(r * 2)) == 0
            w.setze(x, y, z, w.b("light_blue_stained_glass") if fenster else M(x, y, z, t))
    for b in range(balkone):
        yb = y0 + round(H * (0.45 + 0.4 * b / max(1, balkone)))
        for k in range(int((R + 1.5) * 8)):
            a = k / ((R + 1.5) * 8) * 6.28
            x, z = cx + round(math.cos(a) * (R + 1)), cz + round(math.sin(a) * (R + 1))
            w.setze(x, yb, z, w.b("smooth_quartz_slab", type="top", waterlogged=False), False)
            if k % 2 == 0:
                w.setze(x, yb + 1, z, w.b("birch_fence", north=False, south=False, east=False, west=False,
                                          waterlogged=False), False)
    yt = y0 + H
    Hs = _r(R * 3.2 + 2)
    dach = ["waxed_oxidized_cut_copper", "waxed_weathered_cut_copper"] if stil_ == 0 else \
        ["light_blue_terracotta", "cyan_terracotta"]
    for y in range(Hs):
        t = y / Hs
        r = (R + 1) * (1 - t) ** 1.4 * (1 + 0.35 * math.sin(t * math.pi) * (t < 0.4))
        for k in range(int(r * 8) + 4):
            a = k / (r * 8 + 4) * 6.28
            w.setze(cx + round(math.cos(a) * r), yt + y, cz + round(math.sin(a) * r), w.b(dach[(y // 2) % 2]))
    for y in range(Hs, Hs + 3):
        w.setze(cx, yt + y, cz, gold(w) if y < Hs + 2 else w.b("lightning_rod", facing="up", powered=False,
                                                                waterlogged=False))


def spitzbogen(w, cx, cz, y0, B, H, achse="x", mat=None, dicke=1):
    """Spitzbogen (Elfenbogen) als freistehender Rahmen, B = halbe Breite."""
    mat = mat or Mat(w, WEISS)
    for k in range(-B, B + 1):
        t = abs(k) / B
        hb = H * 0.55 + H * 0.45 * math.sqrt(max(0, 1 - t ** 1.3)) if True else H
        for d in range(dicke):
            for yy in range(0, 2):
                y = y0 + round(hb) + yy
                p = (cx + k, y, cz + d) if achse == "x" else (cx + d, y, cz + k)
                w.setze(*p, mat(*p, 0.8))
    for s in (-B, B):
        for y in range(y0, y0 + round(H * 0.6)):
            for d in range(dicke):
                p = (cx + s, y, cz + d) if achse == "x" else (cx + d, y, cz + s)
                w.setze(*p, mat(*p, (y - y0) / H))
    p = (cx, y0 + H + 2, cz) if achse == "x" else (cx, y0 + H + 2, cz)
    w.setze(*p, gold(w))


def mallorn(w, x0, z0, H, stil_=0, y0=1, flett=True):
    """Mallornbaum: glatter, silbergrauer Stamm, ausladende Äste in Etagen, goldenes (oder silbergrünes) Laub,
    auf halber Höhe ein weißes Flett mit Geländer."""
    rng = w.rng
    R = 0.8 + H * 0.06
    for y in range(y0, y0 + H):
        r = R * (1 - (y - y0) / H * 0.5) + (1.2 if y < y0 + 2 else 0)
        for dx in range(-int(r) - 1, int(r) + 2):
            for dz in range(-int(r) - 1, int(r) + 2):
                if dx * dx + dz * dz <= r * r + 0.3:
                    w.setze(x0 + dx, y, z0 + dz, w.b("stripped_birch_log" if (y + dx) % 5 else "birch_log",
                                                     axis="y"))
    for e in range(3):
        y = y0 + round(H * (0.5 + e * 0.18))
        rk = H * (0.32 - e * 0.07) + 2
        for k in range(5):
            a = k / 5 * 6.28 + e * 0.6
            end = (x0 + math.cos(a) * rk * 0.8, y + 2, z0 + math.sin(a) * rk * 0.8)
            linie(w, (x0, y - 1, z0), end, w.b("stripped_birch_log", axis="y"))
        for dx in range(-int(rk) - 1, int(rk) + 2):
            for dz in range(-int(rk) - 1, int(rk) + 2):
                for dy in range(-1, 3):
                    d = (dx * dx + dz * dz) / (rk * rk) + ((dy - 0.5) / 1.6) ** 2
                    if d < 1 and rng.random() < 0.82:
                        w.setze(x0 + dx, y + 2 + dy, z0 + dz, laub_gold(w, stil_) if (dx + dz + dy) % 4 else
                                _lv(w, "birch"), False)
    if flett:
        yf = y0 + round(H * 0.38)
        rf = H * 0.18 + 2.5
        for dx in range(-int(rf) - 1, int(rf) + 2):
            for dz in range(-int(rf) - 1, int(rf) + 2):
                d = math.hypot(dx, dz)
                if d <= rf:
                    w.setze(x0 + dx, yf, z0 + dz, w.b("birch_planks") if d < rf - 1 else
                            w.b("smooth_quartz_slab", type="top", waterlogged=False), False)
                    if rf - 1 < d <= rf and (dx + dz) % 2 == 0:
                        w.setze(x0 + dx, yf + 1, z0 + dz, w.b("birch_fence", north=False, south=False, east=False,
                                                              west=False, waterlogged=False), False)
        for k in range(yf - y0):
            a = k * 0.45
            w.setze(x0 + round(math.cos(a) * (R + 1.6)), y0 + k, z0 + round(math.sin(a) * (R + 1.6)),
                    w.b("birch_slab", type="top", waterlogged=False), False)
        for k in range(4):
            a = k * 1.57 + 0.78
            w.setze(x0 + round(math.cos(a) * (rf - 1.5)), yf + 1, z0 + round(math.sin(a) * (rf - 1.5)),
                    w.b("lantern", hanging=False, waterlogged=False), False)


def elfengarten(w, R, cx=0, cz=0, dichte=0.35):
    """Gepflegter Rasen mit Blumen, Silberbirken-Büschen und weißen Wegsteinen."""
    rng = w.rng
    bl = ["lily_of_the_valley", "azure_bluet", "oxeye_daisy", "allium", "blue_orchid", "cornflower", "white_tulip"]
    for x in range(int(cx - R) - 1, int(cx + R) + 2):
        for z in range(int(cz - R) - 1, int(cz + R) + 2):
            if math.hypot(x - cx, z - cz) > R or not w.frei(x, 1, z):
                continue
            if (x, 0, z) not in w.bloecke:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
            if rng.random() < dichte:
                w.setze(x, 1, z, w.b(bl[int(rng.integers(len(bl)))]) if rng.random() < 0.6 else w.b("grass"))


def weg(w, pts, breite=1, mat=None):
    mat = mat or ["calcite", "smooth_quartz", "polished_diorite"]
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        n = max(abs(bx - ax), abs(bz - az), 1)
        for k in range(n + 1):
            x, z = round(ax + (bx - ax) * k / n), round(az + (bz - az) * k / n)
            for dx in range(-breite, breite + 1):
                for dz in range(-breite, breite + 1):
                    if abs(dx) + abs(dz) <= breite:
                        w.setze(x + dx, 0, z + dz, w.b(mat[(x + z + dx) % len(mat)]))
                        w.bloecke.pop((x + dx, 1, z + dz), None)


def laterne_pfahl(w, x, z, y0=1, h=3):
    for y in range(y0, y0 + h):
        w.setze(x, y, z, w.b("birch_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(x, y0 + h, z, w.b("lantern", hanging=False, waterlogged=False))


# ============================================================================ Bauten

def elfenpalast(seed, g=2):
    """Elfenpalast: ein weißer Palast mit Bogenfenstern und grünen Kupferdächern, flankiert von schlanken
    Türmen mit goldenen Spitzen, Säulengang, Wasserbecken und Gärten."""
    w = _neu(seed)
    u = U[g]
    R = _r(24 * u + 8)
    gelaende(w, R, art="wiese", dichte=0.25)
    st = stil(w, seed)
    a, b = _r(8 * u + 3), _r(5 * u + 2)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=5, dach="walm", tuer="south", gauben=True, kamine=0,
               pilaster=2)
    kuppel(w, w.b("waxed_oxidized_copper" if _stil(seed) == 0 else "light_blue_terracotta"), 0, 0, 1 + 2 * 5 + 3,
           min(a, b) * 0.6, form="zwiebel", spitze="gold_block")
    for sx in (-1, 1):
        for sz in (-1, 1):
            elfenturm(w, sx * (a + 2), sz * (b + 2), 1, _r(18 * u + 6), 1.8 * u + 1.2, _stil(seed))
        P.gebaeude(w, st, sx * (a + 4) - 3 * (sx < 0) * 1, -b + 1, sx * (a + 4) + 3 * (sx > 0), b - 1, y0=1,
                   etagen=1, eh=5, dach="sattel", tuer="south", gauben=False, kamine=0) if False else None
    for x in range(-a, a + 1, 3):
        for y in range(1, 6):
            w.setze(x, y, b + 3, w.b("quartz_pillar", axis="y"))
        w.setze(x, 6, b + 3, w.b("chiseled_quartz_block"))
    for x in range(-a - 1, a + 2):
        w.setze(x, 7, b + 3, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
        w.setze(x, 7, b + 2, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
    for x in range(-a // 2, a // 2 + 1):
        for z in range(b + 6, b + 6 + _r(6 * u + 2)):
            w.setze(x, 0, z, w.b("water", level=0) if abs(x) < a // 2 and z < b + 5 + _r(6 * u + 2) else
                    w.b("smooth_quartz"))
    weg(w, [(0, b + 3), (0, R)], 1)
    elfengarten(w, R, dichte=0.25)
    for k in range(4):
        x = (k % 2 * 2 - 1) * round(R * 0.7)
        z = (k // 2 * 2 - 1) * round(R * 0.6)
        einfuegen(w, wald2.birke(int(w.rng.integers(1, 10 ** 6)), H=_r(8 * u + 4)), x, 0, z)
    return w


def mondtempel(seed, g=2):
    """Mondtempel: ein offener Rundtempel aus schlanken weißen Säulen unter einer filigranen Gitterkuppel, in der
    Mitte ein Becken mit Mondstein, der nachts leuchtet."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    gelaende(w, R + 6, art="wiese", dichte=0.3)
    for k in range(3):
        for x in range(-R - 3 + k, R + 4 - k):
            for z in range(-R - 3 + k, R + 4 - k):
                if math.hypot(x, z) <= R + 3 - k:
                    w.setze(x, k, z, w.b(["calcite", "smooth_quartz", "polished_diorite"][k]))
    n = 12
    Hs = _r(9 * u + 4)
    for i in range(n):
        a = i / n * 6.28
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        for y in range(3, 3 + Hs):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
        w.setze(x, 3 + Hs, z, w.b("chiseled_quartz_block"))
    yk = 3 + Hs + 1
    for k in range(int(R * 1.4) + 1):
        for j in range(n * 2):
            a = j / (n * 2) * 6.28
            t = k / (R * 1.4)
            r = R * math.cos(t * math.pi / 2)
            y = yk + round(R * 0.9 * math.sin(t * math.pi / 2))
            if j % 2 == 0 or k % 3 == 0:
                w.setze(round(math.cos(a) * r), y, round(math.sin(a) * r),
                        w.b("smooth_quartz") if k % 3 == 0 else w.b("white_stained_glass"))
    w.setze(0, yk + round(R * 0.9) + 1, 0, gold(w))
    for x in range(-2, 3):
        for z in range(-2, 3):
            if x * x + z * z <= 5:
                w.setze(x, 3, z, w.b("water", level=0) if x * x + z * z <= 2 else w.b("chiseled_quartz_block"))
    w.setze(0, 2, 0, w.b("sea_lantern"))
    w.setze(0, 4, 0, w.b("pearlescent_froglight", axis="y"))
    return w


def mallornhalle(seed, g=2):
    """Mallornhalle: ein gewaltiger silberner Mallornbaum mit goldener Krone, auf dessen Flett eine offene Halle mit
    Thronsitz steht, Wendeltreppe und Laternen."""
    w = _neu(seed)
    u = U[g]
    gelaende(w, _r(16 * u + 6), art="wald", dichte=0.25)
    H = _r(30 * u + 8)
    mallorn(w, 0, 0, H, _stil(seed))
    yf = 1 + round(H * 0.38)
    rf = H * 0.18 + 2.5
    for k in range(10):
        a = k / 10 * 6.28
        x, z = round(math.cos(a) * (rf - 1.5)), round(math.sin(a) * (rf - 1.5))
        for y in range(yf + 1, yf + 5):
            w.setze(x, y, z, w.b("birch_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    for dx in range(-int(rf), int(rf) + 1):
        for dz in range(-int(rf), int(rf) + 1):
            if math.hypot(dx, dz) <= rf - 1:
                w.setze(dx, yf + 5, dz, w.b("birch_slab", type="bottom", waterlogged=False), False)
    w.setze(0, yf + 1, round(rf * 0.5), w.b("birch_stairs", facing="north", half="bottom", shape="straight",
                                            waterlogged=False))
    elfengarten(w, _r(14 * u + 5), dichte=0.2)
    return w


def elfentor(seed, g=1):
    """Elfentor: ein hoher, verschlungener Spitzbogen aus weißem Stein, von Silberranken und Blüten umwunden, mit
    Laternen zu beiden Seiten und einem Weg hindurch."""
    w = _neu(seed)
    u = U[g]
    gelaende(w, _r(10 * u + 5), art="wiese", dichte=0.35)
    B, H = _r(4 * u + 2), _r(10 * u + 4)
    spitzbogen(w, 0, 0, 1, B, H, dicke=2)
    weg(w, [(0, -_r(10 * u + 5)), (0, _r(10 * u + 5))], 1)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 1 and rng.random() < 0.25:
            w.setze(x, y, z - 1, _lv(w, "flowering_azalea" if rng.random() < 0.5 else "azalea"), False)
    for sx in (-1, 1):
        laterne_pfahl(w, sx * (B + 2), 2, h=3)
    return w


def elfenbruecke(seed, g=2):
    """Elfenbrücke: eine schlanke, hochgeschwungene Bogenbrücke aus weißem Stein mit filigranem Geländer und
    Laternen über einen klaren Bach."""
    w = _neu(seed)
    u = U[g]
    L = _r(12 * u + 5)
    gelaende(w, L + 5, art="wiese", dichte=0.3)
    for x in range(-L - 4, L + 5):
        for z in range(-_r(3 * u + 2), _r(3 * u + 2) + 1):
            if abs(z) < 2.5 * u + 1.5:
                w.setze(z, 0, x, w.b("water", level=0))
                w.setze(z, -1, x, w.b("gravel"))
    M = Mat(w, WEISS)
    for x in range(-L, L + 1):
        t = (x + L) / (2 * L)
        y = 1 + round(math.sin(t * math.pi) * 4 * u)
        for z in (-1, 0, 1):
            w.setze(x, y, z, M(x, y, z, 0.5))
            w.setze(x, y - 1, z, M(x, y, z, 0.3)) if abs(x) > L * 0.3 else None
        for z in (-2, 2):
            w.setze(x, y + 1, z, w.b("quartz_slab", type="bottom", waterlogged=False) if x % 2 else
                    w.b("birch_fence", north=False, south=False, east=True, west=True, waterlogged=False))
        if x % _r(4 * u + 2) == 0:
            for z in (-2, 2):
                w.setze(x, y + 1, z, w.b("quartz_pillar", axis="y"))
                w.setze(x, y + 2, z, w.b("lantern", hanging=False, waterlogged=False))
    return w


def quellschrein(seed, g=1):
    """Quellschrein: eine Quelle entspringt unter einem kleinen offenen Pavillon mit Blattkuppel, fließt über
    weiße Stufen in ein Becken, umgeben von Silberbirken."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.3)
    for k in range(6):
        a = k / 6 * 6.28
        x, z = round(math.cos(a) * 3 * u + 0.5), round(math.sin(a) * 3 * u + 0.5)
        for y in range(1, _r(5 * u + 2) + 1):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    kuppel(w, w.b("waxed_oxidized_copper" if _stil(seed) == 0 else "light_blue_terracotta"), 0, 0,
           _r(5 * u + 2) + 1, 3 * u + 1.5, form="zwiebel", spitze="gold_block")
    for k in range(4):
        for x in range(-1 - k, 2 + k):
            w.setze(x, max(0, 2 - k), 2 + k * 2, w.b("calcite"))
            w.setze(x, max(0, 2 - k) + 1, 2 + k * 2, w.b("water", level=0)) if abs(x) <= k else None
    for x in range(-3, 4):
        for z in range(10, 14):
            w.setze(x, 0, z, w.b("water", level=0))
    for k in range(3):
        a = k * 2.1 + 0.5
        einfuegen(w, wald2.birke(int(w.rng.integers(1, 10 ** 6)), H=_r(7 * u + 3)), round(math.cos(a) * R * 0.75), 0,
                  round(math.sin(a) * R * 0.75))
    return w


def elfenpavillon(seed, g=1):
    """Elfenpavillon: ein achteckiger Pavillon mit geschwungenem Blattdach auf zarten Säulen, Kissen und Harfe,
    über einem Seerosenteich."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.3)
    for x in range(-R + 2, R - 1):
        for z in range(-R + 2, R - 1):
            if math.hypot(x, z) < R * 0.7:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("clay"))
                if w.rng.random() < 0.06:
                    w.setze(x, 1, z, w.b("lily_pad"))
    rp = 3 * u + 1.5
    for x in range(-int(rp) - 1, int(rp) + 2):
        for z in range(-int(rp) - 1, int(rp) + 2):
            if math.hypot(x, z) <= rp:
                w.setze(x, 1, z, w.b("smooth_quartz"))
                w.bloecke.pop((x, 2, z), None)
    Hs = _r(4 * u + 2)
    for k in range(8):
        a = k / 8 * 6.28
        x, z = round(math.cos(a) * rp), round(math.sin(a) * rp)
        for y in range(2, 2 + Hs):
            w.setze(x, y, z, w.b("birch_fence", north=False, south=False, east=False, west=False, waterlogged=False)
                    if y < 1 + Hs else w.b("quartz_pillar", axis="y"))
    yd = 2 + Hs
    for y in range(int(rp * 1.6) + 2):
        t = y / (rp * 1.6 + 1)
        r = (rp + 1.5) * (1 - t) ** 1.2 * (1 + 0.2 * math.sin(t * 3))
        for k in range(int(r * 8) + 4):
            a = k / (r * 8 + 4) * 6.28
            w.setze(round(math.cos(a) * r), yd + y, round(math.sin(a) * r),
                    w.b("waxed_oxidized_cut_copper" if _stil(seed) == 0 else "light_blue_terracotta"))
    w.setze(0, yd + int(rp * 1.6) + 2, 0, gold(w))
    for k in range(4):
        a = k * 1.57
        w.setze(round(math.cos(a) * rp * 0.6), 2, round(math.sin(a) * rp * 0.6), w.b("white_carpet"))
    w.setze(0, 2, 0, w.b("note_block", instrument="harp", note=12, powered=False))
    for k in range(round(R * 0.3) + 1):
        w.setze(round(rp) + k, 1, 0, w.b("birch_slab", type="bottom", waterlogged=False))
    return w


def kraeutergarten(seed, g=1):
    """Heilkräutergarten: geschwungene Beete mit Kräutern und Blumen um ein rundes Heilhaus mit Kuppel,
    Rankbögen und ein kleiner Brunnen."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.15)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if R * 0.35 < d < R * 0.9 and math.sin(math.atan2(z, x) * 6 + d * 0.5) > 0.1:
                w.setze(x, 0, z, w.b("farmland", moisture=7))
                kr = ["sweet_berry_bush", "carrots", "beetroots", "potatoes", "wheat"]
                pf = kr[int(abs(x * 3 + z)) % len(kr)]
                w.setze(x, 1, z, w.b(pf, age=2 if pf in ("sweet_berry_bush", "beetroots") else 5))
    st = stil(w, seed)
    r = _r(3 * u + 2)
    P.turm(w, st, 0, 0, 1, _r(5 * u + 3), r, dach="kuppel", krone=False, fenster=6)
    return w


def bogenschiessplatz(seed, g=1):
    """Bogenschießplatz: ein langer Rasenplatz mit Strohzielscheiben unterschiedlicher Entfernung, ein Schützenstand
    unter Blätterdach, Pfeilständer und Wimpel."""
    w = _neu(seed)
    u = U[g]
    L = _r(16 * u + 6)
    for x in range(-L - 3, L + 4):
        for z in range(-6, 7):
            w.setze(x, 0, z, w.b("grass_block", snowy=False) if abs(z) < 5 else w.b("calcite"))
    for k in range(3):
        x = round(-L * 0.2 + k * L * 0.5)
        z = (k - 1) * 3
        for y in range(1, 4):
            w.setze(x, y, z, w.b("hay_block", axis="y"))
            w.setze(x, y, z + 1, w.b("hay_block", axis="y"))
        w.setze(x - 1, 2, z, w.b("target", power=0))
        w.setze(x - 1, 2, z + 1, w.b("red_wool"))
    for z in range(-3, 4):
        w.setze(-L, 1, z, w.b("birch_planks"))
        w.setze(-L, 4, z, _lv(w, "birch"))
        if abs(z) == 3:
            for y in range(2, 4):
                w.setze(-L, y, z, w.b("birch_log", axis="y"))
    for k in range(4):
        w.setze(-L - 2, 1, -3 + k * 2, w.b("barrel", facing="up", open=True))
    for x in range(-L, L + 1, 4):
        for sz in (-6, 6):
            w.setze(x, 1, sz, w.b("birch_fence", north=False, south=False, east=False, west=False, waterlogged=False))
            w.setze(x, 2, sz, w.b("light_blue_banner" if (x // 4) % 2 else "white_banner", rotation=0))
    return w


def elfenbibliothek(seed, g=2):
    """Elfenbibliothek: ein runder Lesesaal mit hohen Bogenfenstern und Glaskuppel, Galerien voller Bücher,
    Lesepulte und ein Sternenmosaik im Boden."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    gelaende(w, R + 6, art="wiese", dichte=0.3)
    st = stil(w, seed)
    H = _r(10 * u + 5)
    P.turm(w, st, 0, 0, 1, H, R, dach="kuppel", krone=False, fenster=10)
    for y in range(2, H, 4):
        for k in range(int(R * 7)):
            a = k / (R * 7) * 6.28
            w.setze(round(math.cos(a) * (R - 1)), y, round(math.sin(a) * (R - 1)), w.b("bookshelf"), True)
            w.setze(round(math.cos(a) * (R - 1)), y + 1, round(math.sin(a) * (R - 1)), w.b("bookshelf"), True)
    for x in range(-R + 2, R - 1):
        for z in range(-R + 2, R - 1):
            if x * x + z * z < (R - 2) ** 2:
                ang = math.atan2(z, x)
                w.setze(x, 1, z, w.b("lapis_block" if math.cos(ang * 8) > 0.85 else "smooth_quartz"))
    w.setze(0, 2, 0, w.b("lectern", facing="south", has_book=True, powered=False))
    for sx in (-1, 1):
        elfenturm(w, sx * (R + 3), 0, 1, _r(H * 1.3), 1.4 * u + 0.8, _stil(seed), balkone=1)
    elfengarten(w, R + 6, dichte=0.2)
    return w


def elfenwachturm(seed, g=2):
    """Elfenwachturm: ein einzelner, sehr schlanker weißer Turm auf einem Felssporn, mit Balkonen, Leuchtfeuer
    und Bogenschützen-Galerie, eine Wendeltreppe außen herum."""
    from drachen import felsen
    w = _neu(seed)
    u = U[g]
    gelaende(w, _r(10 * u + 5), art="wiese", dichte=0.3)
    hoehe = felsen(w, 6 * u + 3, 6 * u + 3, spitz=1.6, rauh=0.2,
                   mat=Mat(w, ["stone", "andesite", "mossy_cobblestone", "calcite"], kontrast=1.2))
    top = max(v for (x, z), v in hoehe.items() if abs(x) < 2 and abs(z) < 2) + 1
    H = _r(26 * u + 8)
    elfenturm(w, 0, 0, top, H, 2.2 * u + 1.2, _stil(seed), balkone=3)
    for k in range(H):
        a = k * 0.35
        r = 2.2 * u + 2.4
        w.setze(round(math.cos(a) * r), top + k, round(math.sin(a) * r), w.b("quartz_slab", type="top",
                                                                             waterlogged=False), False)
    w.setze(0, top + H - 1, 0, w.b("sea_lantern"))
    return w


def terrassengaerten(seed, g=2):
    """Terrassengärten: am Hang gestufte Gartenterrassen mit weißen Stützmauern, Wasserläufen von Stufe zu Stufe,
    Pavillons und Blütenbäumen."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    n = 4
    sh = _r(2.5 * u + 1)
    M = Mat(w, WEISS)
    for k in range(n):
        z0 = -R + k * (2 * R // n)
        y0 = (n - 1 - k) * sh
        for x in range(-R, R + 1):
            for z in range(z0, z0 + 2 * R // n):
                if abs(x) > R:
                    continue
                for y in range(-1, y0 + 1):
                    w.setze(x, y, z, w.b("grass_block", snowy=False) if y == y0 else w.b("dirt"))
                if z == z0 + 2 * R // n - 1 and k < n - 1:
                    for y in range(-1, y0 + 2):
                        w.setze(x, y, z, M(x, y, z, 0.6))
                if abs(x) <= 1:
                    w.setze(x, y0, z, w.b("water", level=0))
        for x in range(-1, 2):
            zz = z0 + 2 * R // n - 1
            for y in range(max(0, y0 - sh + 1), y0 + 1):
                if k < n - 1:
                    w.setze(x, y, zz + 1, w.b("water", level=0 if y == y0 else 8))
        elfengarten(w, R * 0.45, cx=round(R * 0.45), cz=z0 + R // n, dichte=0.4)
        if k % 2 == 0:
            einfuegen(w, wald2.kirschbaum(int(w.rng.integers(1, 10 ** 6)), H=_r(5 * u + 3)), -round(R * 0.55), y0,
                      z0 + R // n)
    return w


def elfenhafen(seed, g=2):
    """Elfenhafen: ein weißer Kai mit Bogenhallen und zwei schlanken Leuchttürmen, an dem ein Schwanenschiff
    zur Fahrt übers Meer bereitliegt."""
    from boote import schwanenschiff
    w = _neu(seed)
    u = U[g]
    L = _r(18 * u + 6)
    M = Mat(w, WEISS)
    for x in range(-L, L + 1):
        for z in range(-L, L + 1):
            if z > -2:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -3, z, w.b("sand"))
                for y in (-1, -2):
                    w.setze(x, y, z, w.b("water", level=0))
            else:
                for y in range(-3, 2):
                    w.setze(x, y, z, M(x, y, z, 0.5) if y < 1 else w.b("smooth_quartz"))
    for x in range(-L + 2, L - 1, 4):
        spitzbogen(w, x, -L + 3, 2, 1, _r(5 * u + 2), achse="x")
    for sx in (-1, 1):
        elfenturm(w, sx * (L - 2), 2, 0, _r(18 * u + 6), 1.6 * u + 1, _stil(seed), balkone=1)
        for y in range(-3, 1):
            for dx in range(-3, 4):
                for dz in range(-1, 6):
                    if abs(dx) + abs(dz - 2) < 5:
                        w.setze(sx * (L - 2) + dx, y, dz, M(dx, y, dz, 0.5))
    einfuegen(w, schwanenschiff(seed, max(0, g - 1)), 0, 0, round(L * 0.4))
    return w


def flettsiedlung(seed, g=2):
    """Flettsiedlung: in einem Hain aus Mallornbäumen hängen weiße Plattformen mit Zelten aus Silberstoff,
    verbunden durch geschwungene Hängebrücken."""
    w = _neu(seed)
    u = U[g]
    R = _r(20 * u + 6)
    gelaende(w, R, art="wald", dichte=0.25)
    n = 3 + g
    pos = []
    for i in range(n):
        a = i / n * 6.28 + 0.4
        x, z = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        H = _r((16 + 4 * (i % 2)) * u + 6)
        mallorn(w, x, z, H, _stil(seed))
        yf = 1 + round(H * 0.38)
        pos.append((x, yf, z))
        for k in range(3):
            for dx in range(-2 + k, 3 - k):
                w.setze(x + dx, yf + 1 + k, z + 3, w.b("white_wool" if k % 2 == 0 else "light_blue_wool"), False)
    for (ax, ay, az), (bx, by, bz) in zip(pos, pos[1:] + pos[:1]):
        L = max(abs(bx - ax), abs(bz - az))
        for k in range(L + 1):
            t = k / L
            x, z = round(ax + (bx - ax) * t), round(az + (bz - az) * t)
            y = round(ay + (by - ay) * t - math.sin(t * math.pi) * 2)
            w.setze(x, y, z, w.b("birch_slab", type="bottom", waterlogged=False), False)
    return w


def elfenkoenigin(seed, g=2):
    """Statue der Elfenkönigin: eine riesige, schlanke Figur mit erhobenem Stab und Diadem steht auf einem
    Sockel aus Mondstein, umgeben von einem Spiegelbecken."""
    from motive import figur
    from skulptur import Skulptur
    from weltwunder import bl, sk
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.25)
    for x in range(-R + 2, R - 1):
        for z in range(-R + 2, R - 1):
            if math.hypot(x, z) < R * 0.7:
                w.setze(x, 0, z, w.b("water", level=0))
    for k in range(3):
        rr = 4 * u + 2 - k
        for x in range(-int(rr), int(rr) + 1):
            for z in range(-int(rr), int(rr) + 1):
                if max(abs(x), abs(z)) <= rr:
                    w.setze(x, 1 + k, z, w.b(["calcite", "polished_diorite", "smooth_quartz"][k]))
    S = Skulptur(w, 0.75 * u + 0.3)
    M = Mat(w, ["calcite", "smooth_quartz", "polished_diorite", "quartz_bricks"])
    S.mat("k", sk(M, 0, 30))
    S.mat("a", bl(w, "gold_block"))
    S.mat("d", bl(w, "white_concrete"))
    S.mat("g", bl(w, "sea_lantern"))
    figur(S, "elf", "stab")
    S.rendern((-7, -1, -5), (7, 26, 7), versatz=(0.5, 4.01, 0.5))
    return w


def kristallbrunnen(seed, g=1):
    """Kristallbrunnen: eine Brunnenschale aus weißem Stein, aus deren Mitte ein Bündel leuchtender
    Kristallsäulen wächst, Wasser rinnt über drei Stufen."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    gelaende(w, R + 3, art="wiese", dichte=0.3)
    for k in range(3):
        rr = (3.5 - k) * u + 1.5
        y = 1 + k * 2
        for x in range(-int(rr) - 1, int(rr) + 2):
            for z in range(-int(rr) - 1, int(rr) + 2):
                d = math.hypot(x, z)
                if d <= rr:
                    w.setze(x, y - 1, z, w.b("calcite"))
                    w.setze(x, y, z, w.b("water", level=0) if d < rr - 0.9 else w.b("smooth_quartz"))
    for k in range(6):
        a = k / 6 * 6.28
        h = _r((5 + k % 3 * 2) * u + 3)
        x, z = round(math.cos(a) * 0.8), round(math.sin(a) * 0.8)
        for y in range(5, 5 + h):
            w.setze(x, y, z, w.b("amethyst_block" if y % 3 else "light_blue_stained_glass") if k % 2 else
                    w.b("white_stained_glass" if y % 2 else "pearlescent_froglight", **({} if y % 2 else
                                                                                        {"axis": "y"})))
    weg(w, [(0, R), (0, R + 3)], 1)
    return w


def silberwald(seed, g=1):
    """Silberwald: ein lichter Hain aus Mallornbäumen und Silberbirken mit goldenem Laub, weißen Blumen und
    Laternenpfaden – kombinierbar."""
    st = Stueck(seed, g)

    def baum(x, z, rd, a):
        sd = int(st.rng.integers(1, 10 ** 6))
        if st.rng.random() < 0.35:
            w = _neu(sd)
            H = int(14 + st.rng.integers(6) + st.g * 4)
            mallorn(w, 0, 0, H, st.stil, flett=st.rng.random() < 0.3)
            return w, H * 0.38 + 4
        H = int(8 + st.rng.integers(5) + st.g)
        return wald2.birke(sd, H=H), wald2.kronen_r(H) * 1.5

    st.verteile(7, int(160 * (g + 1) ** 2), baum)
    st.boden([("grass_block_s", 6), ("moss_block", 1)],
             [("lily_of_the_valley", 2), ("oxeye_daisy", 2), ("azure_bluet", 1.5), ("grass", 5),
              (hohes("tall_grass"), 1), ("white_tulip", 1), (hohes("lilac"), 0.4)], dichte=0.55)
    return st


def mondsee(seed, g=2):
    """Mondsee: ein spiegelglatter See, auf dem schwimmende Laternen treiben, ein weißer Steg mit Bogen führt
    hinaus zu einer kleinen Insel mit Pavillon."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R + 3, art="wiese", dichte=0.3)
    rn = Rauschen(w, 4)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) < R * (0.8 + 0.15 * rn(x, 0, z)):
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("water", level=0))
                w.setze(x, -2, z, w.b("clay"))
                w.bloecke.pop((x, 1, z), None)
    ri = R * 0.2
    for x in range(-int(ri) - 1, int(ri) + 2):
        for z in range(-int(ri) - 1, int(ri) + 2):
            if math.hypot(x, z) < ri:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
    for k in range(6):
        a = k / 6 * 6.28
        x, z = round(math.cos(a) * ri * 0.6), round(math.sin(a) * ri * 0.6)
        for y in range(1, 4):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    kuppel(w, w.b("smooth_quartz"), 0, 0, 4, ri * 0.7 + 0.5, form="zwiebel", spitze="gold_block")
    for z in range(round(ri), R + 2):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
    spitzbogen(w, 0, round(R * 0.6), 1, 2, _r(4 * u + 2), achse="x")
    rng = w.rng
    for k in range(int(12 * u)):
        a = rng.random() * 6.28
        d = R * (0.3 + 0.5 * rng.random())
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if abs(x) > 2:
            w.setze(x, 1, z, w.b("lily_pad"))
            w.setze(x, 2, z, w.b("lantern", hanging=False, waterlogged=False)) if k % 2 else \
                w.setze(x, 2, z, w.b("candle", candles=3, lit=True, waterlogged=False))
    return w


def elfenmarkt(seed, g=1):
    """Elfenmarkt: anmutige Stände mit seidenen Baldachinen in Silber und Blau, Körbe mit Früchten, Harfen und
    Laternengirlanden zwischen schlanken Pfählen."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.15)
    for x in range(-R + 2, R - 1):
        for z in range(-R + 2, R - 1):
            if math.hypot(x, z) < R * 0.75:
                w.setze(x, 0, z, w.b(["calcite", "smooth_quartz", "polished_diorite"][(x * 3 + z) % 3]))
                w.bloecke.pop((x, 1, z), None)
    n = 5 + 2 * g
    stoff = ["white_wool", "light_blue_wool", "light_gray_wool", "cyan_wool"]
    for i in range(n):
        a = i / n * 6.28
        cx, cz = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        for dx in (-1, 1):
            for dz in (-1, 1):
                for y in range(1, 4):
                    w.setze(cx + dx, y, cz + dz, w.b("birch_fence", north=False, south=False, east=False,
                                                     west=False, waterlogged=False))
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                w.setze(cx + dx, 4 + (abs(dx) + abs(dz) < 2), cz + dz, w.b(stoff[i % 4] if (dx + dz) % 2 else
                                                                            "white_wool"))
        w.setze(cx, 1, cz, w.b(["barrel", "composter", "hay_block"][i % 3], **(
            {"facing": "up", "open": True} if i % 3 == 0 else {"level": 7} if i % 3 == 1 else {"axis": "y"})))
    for i in range(n):
        a = i / n * 6.28 + 3.14 / n
        laterne_pfahl(w, round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8), h=3)
    return w


def ahnenhain(seed, g=2):
    """Hain der Ahnen: im Kreis stehende, schlanke Gedenkstelen aus Mondstein unter alten Silberbäumen, mit
    eingelassenen Laternen und einem Altar in der Mitte."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R, art="wald", dichte=0.25)
    n = 9
    for i in range(n):
        a = i / n * 6.28
        x, z = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        H = _r((4 + (i % 3)) * u + 2)
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b("smooth_quartz" if y < H else "chiseled_quartz_block"))
        w.setze(x, H + 1, z, w.b("quartz_slab", type="bottom", waterlogged=False))
        w.setze(x, 2, z, w.b("pearlescent_froglight", axis="y"))
    for x in range(-1, 2):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("calcite"))
    w.setze(0, 2, 0, w.b("candle", candles=4, lit=True, waterlogged=False))
    for k in range(4):
        a = k * 1.57 + 0.78
        einfuegen(w, wald2.birke(int(w.rng.integers(1, 10 ** 6)), H=_r(10 * u + 4)), round(math.cos(a) * R * 0.8), 0,
                  round(math.sin(a) * R * 0.8))
    return w


def wasserfallpalast(seed, g=2):
    """Wasserfallpalast: ein Palast schmiegt sich an eine Felswand, durch deren Bögen mehrere Wasserfälle in ein
    Becken stürzen, Brücken und Türme davor."""
    from gewaesser import Land, fall_spalten
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 7)
    L = Land(w, R)
    H = _r(16 * u + 6)
    zc = -round(R * 0.3)
    L.heben(lambda x, z, h: H + 2 * L.rn(x, 0, z) if z < zc else 1)
    L.see(0, zc + R * 0.35, R * 0.55, 0, tiefe=3, rauh=0.1)
    for xf in (-round(R * 0.4), 0, round(R * 0.4)):
        L.fluss([(xf, -R), (xf, zc - 1)], 1.6, H, tiefe=1)
        fall_spalten(L, xf - 1, xf + 1, zc, H, 1)
    L.bauen(fels=["calcite", "diorite", "stone", "andesite", "polished_diorite"])
    st = stil(w, seed)
    a = _r(6 * u + 2)
    for sx in (-1, 1):
        P.gebaeude(w, st, sx * round(R * 0.2) - 3, zc - 6, sx * round(R * 0.2) + 3, zc - 1, y0=H + 1, etagen=1,
                   eh=5, dach="walm", tuer="south", gauben=False, kamine=0)
        elfenturm(w, sx * round(R * 0.65), zc + 3, 1, _r(H * 1.2), 1.6 * u + 1, _stil(seed))
    for x in range(-round(R * 0.6), round(R * 0.6) + 1):
        w.setze(x, H + 1, zc + 1, w.b("smooth_quartz_slab", type="bottom", waterlogged=False), False)
    return w


def mallornbaum(seed, g=2):
    """Mallornbaum: ein einzelner, majestätischer Baum mit glatter Silberrinde und goldener Krone in drei Etagen,
    ein kleines Flett mit Laternen auf halber Höhe."""
    w = _neu(seed)
    u = U[g]
    gelaende(w, _r(12 * u + 5), art="wiese", dichte=0.3)
    mallorn(w, 0, 0, _r(24 * u + 6), _stil(seed))
    return w


def koeniginnenlaube(seed, g=1):
    """Laube der Königin: ein Gewölbe aus verflochtenen Birkenzweigen voller Blüten über einem weißen Sitz, mit
    Kissen, Kerzen und einem Blütenteppich."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.4)
    rng = w.rng
    B = _r(3 * u + 2)
    L = _r(5 * u + 3)
    for z in range(-L, L + 1):
        for k in range(int(B * 3.2) + 1):
            a = k / (B * 3.2) * math.pi
            x, y = round(math.cos(a) * B), round(1 + math.sin(a) * B * 1.4)
            w.setze(x, y, z, w.b("birch_log", axis="y") if k % 4 == 0 else w.b("stripped_birch_log", axis="z"))
            if rng.random() < 0.75:
                w.setze(x + rng.integers(-1, 2), y + 1, z, _lv(w, "flowering_azalea" if rng.random() < 0.5 else
                                                              "azalea"), False)
    for x in range(-1, 2):
        w.setze(x, 1, -L + 1, w.b("smooth_quartz"))
        w.setze(x, 2, -L + 1, w.b("light_blue_carpet" if x else "white_carpet"))
        w.setze(x, 1, -L, w.b("smooth_quartz"))
        w.setze(x, 2, -L, w.b("smooth_quartz"))
    for z in range(-L + 2, L + 1):
        for x in range(-B + 1, B):
            if rng.random() < 0.5:
                w.setze(x, 1, z, w.b("pink_petals", flower_amount=int(rng.integers(1, 5)),
                                     facing=["north", "south", "east", "west"][int(rng.integers(4))]), False)
    for sx in (-1, 1):
        w.setze(sx * (B - 1), 1, -L + 1, w.b("candle", candles=3, lit=True, waterlogged=False), False)
    return w


def elfenhaus(seed, g=1):
    """Elfenhaus: ein anmutiges Wohnhaus aus weißem Stein mit Bogenfenstern, geschwungenem Kupferdach, einem
    schlanken Treppenturm, Balkon und Blumengarten."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.2)
    st = stil(w, seed)
    a, b = _r(4 * u + 2), _r(3 * u + 2)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="walm", tuer="south", gauben=False, kamine=0)
    elfenturm(w, a + 1, -b + 1, 1, _r(14 * u + 4), 1.3 * u + 0.8, _stil(seed), balkone=1)
    for x in range(-a, a + 1):
        w.setze(x, 5, b + 1, w.b("smooth_quartz_slab", type="top", waterlogged=False))
        if x % 2 == 0:
            w.setze(x, 6, b + 2, w.b("birch_fence", north=False, south=False, east=True, west=True,
                                     waterlogged=False))
    elfengarten(w, R, dichte=0.4)
    weg(w, [(0, b + 1), (0, R)], 0)
    return w


def schwanensteg(seed, g=1):
    """Schwanensteg: ein weißer Bootssteg mit Laternenbögen an einem stillen Gewässer, daran vertäut ein
    Schwanenboot der Elfen."""
    from boote import schwanenschiff
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.3)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if z > -R * 0.2 and math.hypot(x, z) <= R:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("water", level=0))
                w.setze(x, -2, z, w.b("clay"))
                w.bloecke.pop((x, 1, z), None)
    for z in range(-round(R * 0.2), round(R * 0.7)):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
        if z % 4 == 0:
            spitzbogen(w, 0, z, 2, 2, _r(3 * u + 2), achse="x")
    einfuegen(w, schwanenschiff(seed, 0), 5, 0, round(R * 0.4))
    return w


ELFEN = {
    "elfenpalast": ("Elfenpalast", elfenpalast),
    "mondtempel": ("Mondtempel", mondtempel),
    "mallornhalle": ("Mallornhalle", mallornhalle),
    "elfentor": ("Elfentor", elfentor),
    "elfenbruecke": ("Elfenbrücke", elfenbruecke),
    "quellschrein": ("Quellschrein", quellschrein),
    "elfenpavillon": ("Elfenpavillon", elfenpavillon),
    "kraeutergarten": ("Heilkräutergarten", kraeutergarten),
    "bogenschiessplatz": ("Bogenschießplatz", bogenschiessplatz),
    "elfenbibliothek": ("Elfenbibliothek", elfenbibliothek),
    "elfenwachturm": ("Elfenwachturm", elfenwachturm),
    "terrassengaerten": ("Terrassengärten", terrassengaerten),
    "elfenhafen": ("Elfenhafen", elfenhafen),
    "flettsiedlung": ("Flettsiedlung", flettsiedlung),
    "elfenkoenigin": ("Statue der Elfenkönigin", elfenkoenigin),
    "kristallbrunnen": ("Kristallbrunnen", kristallbrunnen),
    "mondsee": ("Mondsee", mondsee),
    "elfenmarkt": ("Elfenmarkt", elfenmarkt),
    "ahnenhain": ("Hain der Ahnen", ahnenhain),
    "wasserfallpalast": ("Wasserfallpalast", wasserfallpalast),
    "mallornbaum": ("Mallornbaum", mallornbaum),
    "koeniginnenlaube": ("Laube der Königin", koeniginnenlaube),
    "elfenhaus": ("Elfenhaus", elfenhaus),
    "schwanensteg": ("Schwanensteg", schwanensteg),
    "silberwald": ("Silberwald", lambda seed, g=1: _fertig(silberwald(seed, g).w)),
}

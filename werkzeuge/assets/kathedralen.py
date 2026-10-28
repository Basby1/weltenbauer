"""Kathedralen & Tempel – Paket: gotische Kathedrale, Dorfkapelle, Kuppeltempel, Kloster mit Kreuzgang,
freistehender Glockenturm, Rundkirche und Wegschrein. Spitzbogenfenster mit Buntglas, Rosetten,
Strebebögen, Turmhelme. Stil 1 grauer Stein mit Schiefer, Stil 2 heller Sandstein mit Patina-Kupfer."""

from __future__ import annotations

import math

from lib import Verlauf, Welt
from skulptur import kreisrand, platte, scheibe, treppe, verbinde

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


BUNT = ["red_stained_glass", "blue_stained_glass", "yellow_stained_glass", "purple_stained_glass",
        "light_blue_stained_glass", "orange_stained_glass", "lime_stained_glass", "magenta_stained_glass"]


class Kirche:
    def __init__(self, w, seed):
        self.w = w
        self.hell = _stil(seed) == 1
        if not self.hell:
            self.stein = Verlauf(w, "Stein", ["cobblestone", "stone_bricks", "stone_bricks", "polished_andesite",
                                              "chiseled_stone_bricks"])
            self.tr = "stone_brick"
            self.dach_tr = "deepslate_tile"
            self.dach_voll = "deepslate_tiles"
            self.zier = "chiseled_stone_bricks"
        else:
            self.stein = Verlauf(w, "Sandstein", ["sandstone", "cut_sandstone", "smooth_sandstone", "calcite",
                                                  "chiseled_sandstone"])
            self.tr = "smooth_sandstone"
            self.dach_tr = "waxed_oxidized_cut_copper"
            self.dach_voll = "waxed_oxidized_copper"
            self.zier = "chiseled_sandstone"
        self.bunt = [w.b(b) for b in BUNT]

    def st(self, x, y, z, H=20):
        return self.stein(0.3 + 3 * min(1, y / max(1, H)) + self.w.rng.random() * 0.8, x, y, z)

    def glas(self, t, v):
        return self.bunt[(t * 3 + v * 5 + (t * v) % 3) % len(self.bunt)]


def _boden(w, r, cx=0, cz=0):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, w.b("grass_block", snowy=False), ueberschreiben=False)


def spitzbogen(t, v, breite, hoehe):
    """Liegt (t, v) – quer und hoch, t um 0 – innerhalb eines Spitzbogenfensters?"""
    hb = breite / 2
    if abs(t) > hb or v < 0 or v > hoehe:
        return False
    oben = hoehe - v
    return oben >= (abs(t) / max(0.5, hb)) * min(hoehe * 0.5, breite * 0.9) - 0.01 or v < hoehe - breite * 0.9


def wand_x(w, k, x0, x1, z, y0, y1, fenster=None, H=20):
    """Wand in x-Richtung bei z. fenster: Liste (xm, breite, yb, hoehe)."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            blk = None
            for (xm, br, yb, hh) in (fenster or []):
                if spitzbogen(x - xm, y - yb, br, hh):
                    blk = k.glas(x - xm, y - yb)
            w.setze(x, y, z, blk if blk is not None else k.st(x, y, z, H))


def wand_z(w, k, z0, z1, x, y0, y1, fenster=None, H=20):
    for z in range(z0, z1 + 1):
        for y in range(y0, y1 + 1):
            blk = None
            for (zm, br, yb, hh) in (fenster or []):
                if spitzbogen(z - zm, y - yb, br, hh):
                    blk = k.glas(z - zm, y - yb)
            w.setze(x, y, z, blk if blk is not None else k.st(x, y, z, H))


def steildach(w, k, x0, x1, z0, z1, yt, entlang_z=True, ue=1):
    """Steiles Satteldach (2 Höhen pro Stufe) mit gefüllten Giebeln."""
    s = 0
    while True:
        if entlang_z:
            a, b = x0 - ue + s, x1 + ue - s
        else:
            a, b = z0 - ue + s, z1 + ue - s
        if a > b:
            break
        for lage in range(2):
            y = yt + 1 + 2 * s + lage
            rng = range(z0 - ue, z1 + ue + 1) if entlang_z else range(x0 - ue, x1 + ue + 1)
            for q in rng:
                if a == b:
                    p1 = (a, y, q) if entlang_z else (q, y, a)
                    w.setze(*p1, w.b(k.dach_voll))
                    continue
                if lage == 0:
                    for p in ((a, y, q), (b, y, q)) if entlang_z else ((q, y, a), (q, y, b)):
                        w.setze(*p, w.b(k.dach_voll))
                else:
                    if entlang_z:
                        w.setze(a, y, q, treppe(w, k.dach_tr, "east"))
                        w.setze(b, y, q, treppe(w, k.dach_tr, "west"))
                    else:
                        w.setze(q, y, a, treppe(w, k.dach_tr, "south"))
                        w.setze(q, y, b, treppe(w, k.dach_tr, "north"))
            for q in ((z0, z1) if entlang_z else (x0, x1)):
                for r in range(max(a + 1, (x0 if entlang_z else z0)), min(b, (x1 if entlang_z else z1) + 1)):
                    p = (r, y, q) if entlang_z else (q, y, r)
                    w.setze(*p, k.st(*p, 10))
        s += 1
    return yt + 2 * s


def turmhelm(w, k, cx, cz, R, y0, H):
    """Achteckiger, spitzer Turmhelm mit Kreuzblume."""
    for kk in range(H + 1):
        r = R * (1 - kk / (H + 1))
        for x, z in kreisrand(max(0.3, r), cx, cz):
            w.setze(x, y0 + kk, z, w.b(k.dach_voll) if kk % 4 else w.b(k.zier))
    w.setze(cx, y0 + H + 1, cz, w.b("gold_block"))
    w.setze(cx, y0 + H + 2, cz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))


def rosette(w, k, cx, cy, z, R):
    for x in range(cx - int(R) - 1, cx + int(R) + 2):
        for y in range(cy - int(R) - 1, cy + int(R) + 2):
            d = math.hypot(x - cx, y - cy)
            if d <= R:
                if d > R - 0.8:
                    blk = w.b(k.zier)
                else:
                    a = math.atan2(y - cy, x - cx)
                    sektor = int((a + math.pi) / (2 * math.pi) * 12)
                    ring = int(d / max(1, R / 3))
                    blk = k.bunt[(sektor + ring * 2) % len(k.bunt)] if d > 1 else w.b("yellow_stained_glass")
                w.setze(x, y, z, blk)


def eckturm_q(w, k, x0, z0, x1, z1, y0, H, helm=True):
    for y in range(y0, y0 + H):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if x in (x0, x1) or z in (z0, z1):
                    mitte = x == (x0 + x1) // 2 or z == (z0 + z1) // 2
                    fen = mitte and (y - y0) % 8 in (3, 4, 5) and not (x in (x0, x1) and z in (z0, z1))
                    w.setze(x, y, z, k.glas(x, y) if fen else k.st(x, y, z, H + y0))
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            if x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1):
                if (x + z) % 2 == 0:
                    w.setze(x, y0 + H, z, w.b(k.zier))
    if helm:
        R = (x1 - x0) / 2 + 0.3
        turmhelm(w, k, (x0 + x1) // 2, (z0 + z1) // 2, R, y0 + H, _r(R * 3.6, 6))


# ============================================================================ Typen

def kathedrale(seed, g=2):
    """Gotische Kathedrale: hohes Mittelschiff mit Obergaden, Seitenschiffe mit Strebebögen, Querhaus,
    Apsis, Doppelturmfassade mit Rosette und Portal, Vierungsturm mit Spitze."""
    w = _welt(seed)
    k = Kirche(w, seed)
    u = U[g]
    L = _r(28 * u + 10, 16)
    b = _r(4 * u + 2, 3)
    Hw = _r(12 * u + 6, 9)
    sb = _r(3 * u + 1, 2)
    Hs = _r(Hw * 0.5, 4)
    z0, z1 = -L // 2, L // 2
    _boden(w, L // 2 + 10)
    for x in range(-b - sb - 1, b + sb + 2):
        for z in range(z0 - 1, z1 + 2):
            w.setze(x, 0, z, w.b("polished_andesite") if not k.hell else w.b("smooth_sandstone"))
    joch = max(4, _r(4 * u, 4))
    fen_m = [(z, max(2, _r(1.6 * u, 2)), Hs + 2, Hw - Hs - 3) for z in range(z0 + joch // 2, z1, joch)]
    fen_s = [(z, max(2, _r(1.4 * u, 2)), 2, Hs - 3) for z in range(z0 + joch // 2, z1, joch)]
    for s in (-1, 1):
        wand_z(w, k, z0, z1, s * b, 1, Hw, fen_m, Hw)                         # Mittelschiff (Obergaden)
        wand_z(w, k, z0, z1, s * (b + sb), 1, Hs, fen_s, Hw)                    # Seitenschiff-Außenwand
        for z in range(z0, z1 + 1):                                             # Pultdach Seitenschiff
            for t in range(sb + 2):
                y = Hs + 1 + (sb + 1 - t) // 2 * 0 + (t // 1) * 0
                x = s * (b + sb + 1 - t)
                w.setze(x, Hs + 1 + t // 2, z, treppe(w, k.dach_tr, "west" if s > 0 else "east") if t % 2 == 0
                        else w.b(k.dach_voll))
        # Strebepfeiler und Strebebögen
        for z in range(z0, z1 + 1, joch):
            xa = s * (b + sb + 1)
            for y in range(1, Hs + 3):
                w.setze(xa, y, z, w.b(k.zier) if y == Hs + 2 else k.st(xa, y, z, Hw))
            w.setze(xa, Hs + 3, z, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
            n = sb + 1
            for t in range(n + 1):
                x = s * (b + sb + 1 - t)
                y = Hs + 2 + int((Hw - Hs - 3) * (t / n) ** 0.7)
                w.setze(x, y, z, k.st(x, y, z, Hw))
    for z in (z0,):
        wand_x(w, k, -b, b, z, 1, Hw, None, Hw)
    steildach(w, k, -b, b, z0, z1, Hw, entlang_z=True)
    # Querhaus
    zq = z0 + L // 3
    qa = b + sb + _r(4 * u, 3)
    for s in (-1, 1):
        wand_x(w, k, min(s * b, s * qa), max(s * b, s * qa), zq - b, 1, Hw, None, Hw)
        wand_x(w, k, min(s * b, s * qa), max(s * b, s * qa), zq + b, 1, Hw, None, Hw)
        wand_z(w, k, zq - b, zq + b, s * qa, 1, Hw, [(zq, max(2, _r(2 * u, 2)), 3, Hw - 5)], Hw)
    steildach(w, k, -qa, qa, zq - b, zq + b, Hw, entlang_z=False)
    # Apsis
    for y in range(1, Hw + 1):
        for x, z in kreisrand(b, 0, z0):
            if z <= z0:
                a = math.atan2(z - z0, x)
                fen = 3 <= y <= Hw - 3 and abs(math.sin(a * 3)) < 0.25
                w.setze(x, y, z, k.glas(x, y) if fen else k.st(x, y, z, Hw))
    for kk in range(b + 2):
        for x, z in kreisrand(max(0.3, b + 1 - kk), 0, z0):
            if z <= z0:
                w.setze(x, Hw + 1 + kk, z, w.b(k.dach_voll))
    # Westfassade mit Doppeltürmen, Rosette, Portal
    tb = _r(2.5 * u + 1, 2)
    Ht = _r(Hw * 1.45, 12)
    for s in (-1, 1):
        x0 = s * (b + 1) if s > 0 else -(b + 1) - 2 * tb
        eckturm_q(w, k, x0, z1 - 2 * tb + 1, x0 + 2 * tb, z1 + 1, 1, Ht)
    wand_x(w, k, -b, b, z1, 1, Hw + 2, None, Hw)
    rosette(w, k, 0, int(Hw * 0.65), z1 + 1, max(2, b - 1.5))
    pb, ph = max(3, _r(2 * u + 1, 3)) | 1, _r(4 * u + 2, 4)
    for x in range(-pb // 2, pb // 2 + 1):
        for y in range(1, ph + 1):
            if spitzbogen(x, y - 1, pb, ph):
                w.bloecke.pop((x, y, z1), None)
                w.setze(x, y, z1 + 1, w.b(k.zier)) if not spitzbogen(x, y - 1, pb - 2, ph - 1) else None
    for kk in range(3):
        for x in range(-pb // 2 - 2, pb // 2 + 3):
            w.setze(x, 0, z1 + 2 + kk, treppe(w, k.tr, "north") if kk == 2 else w.b(k.zier if False else "polished_andesite"))
    # Vierungsturm
    turmhelm(w, k, 0, zq, b * 0.7, Hw + b + 2, _r(Hw * 0.9, 8))
    return w


def dorfkapelle(seed, g=1):
    """Kleine Dorfkapelle mit Dachreiter-Glockentürmchen, Spitzbogenfenstern und Friedhofsmauer."""
    w = _welt(seed)
    k = Kirche(w, seed)
    u = U[g]
    L, b, H = _r(10 * u + 5, 7), _r(2.5 * u + 1.5, 2), _r(5 * u + 3, 4)
    _boden(w, L // 2 + 6)
    z0, z1 = -L // 2, L // 2
    fen = [(z, 2, 2, H - 3) for z in range(z0 + 2, z1 - 1, 3)]
    for s in (-1, 1):
        wand_z(w, k, z0, z1, s * b, 1, H, fen, H)
    wand_x(w, k, -b, b, z0, 1, H, [(0, 2, 2, H - 2)], H)
    wand_x(w, k, -b, b, z1, 1, H, None, H)
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(0, y, z1, w.b("dark_oak_door", facing="south", half=half, hinge="left", open=False, powered=False))
    top = steildach(w, k, -b, b, z0, z1, H, entlang_z=True)
    # Dachreiter
    for y in range(top - 1, top + _r(3 * u, 2)):
        for x in (-1, 1):
            for z in (z1 - 2, z1):
                w.setze(x, y, z, w.b("dark_oak_fence", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
    w.setze(0, top + 1, z1 - 1, w.b("bell", facing="north", attachment="ceiling", powered=False))
    turmhelm(w, k, 0, z1 - 1, 1.6, top + _r(3 * u, 2), _r(4 * u, 3))
    # Friedhofsmauer
    verbinde(w, [(x, 1, z) for x in range(-b - 4, b + 5) for z in (z0 - 4, z1 + 4)
                 if abs(x) > 1 or z == z0 - 4] + [(x, 1, z) for x in (-b - 4, b + 4) for z in range(z0 - 4, z1 + 5)],
             "cobblestone_wall" if False else "spruce_fence")
    return w


def kuppeltempel(seed, g=2):
    """Kuppeltempel: quadratischer Bau mit Säulenvorhalle, Tambour mit Fenstern, große Kuppel mit Laterne,
    vier kleine Ecktürme mit Kuppeln."""
    w = _welt(seed)
    k = Kirche(w, seed)
    u = U[g]
    h, H = _r(7 * u + 3, 5), _r(8 * u + 4, 6)
    _boden(w, h + 9)
    for y in range(0, H + 1):
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                if y == 0 or x in (-h, h) or z in (-h, h):
                    mitte = abs(x) <= 1 or abs(z) <= 1
                    fen = mitte and 2 <= y <= H - 2 and (x in (-h, h) or z in (-h, h)) and y > 1
                    w.setze(x, y, z, k.glas(x + z, y) if fen else k.st(x, y, z, H))
    for x in range(-h - 1, h + 2):
        for z in range(-h - 1, h + 2):
            if x in (-h - 1, h + 1) or z in (-h - 1, h + 1):
                w.setze(x, H, z, w.b(k.zier))
    Rt = h - 1
    Ht = _r(3 * u + 2, 3)
    for y in range(H + 1, H + 1 + Ht):
        for i, (x, z) in enumerate(kreisrand(Rt)):
            w.setze(x, y, z, k.glas(i, y) if y == H + 2 and i % 2 == 0 else k.st(x, y, z, H))
    yk = H + 1 + Ht
    kuppel = Verlauf(w, "Kuppel", [k.dach_voll, k.dach_voll, "gold_block"]) if not k.hell else \
        Verlauf(w, "Kuppel", ["waxed_oxidized_copper", "waxed_weathered_copper", "waxed_oxidized_cut_copper"])
    for x in range(-Rt - 1, Rt + 2):
        for z in range(-Rt - 1, Rt + 2):
            for y in range(0, Rt + 2):
                d = (x / (Rt + 0.5)) ** 2 + (z / (Rt + 0.5)) ** 2 + (y / (Rt * 1.1)) ** 2
                if 0.7 < d <= 1:
                    w.setze(x, yk + y, z, kuppel(2.2 if (math.atan2(z, x) * 8 / math.pi) % 1 < 0.14 else 0.2, x, yk + y, z))
    yl = yk + int(Rt * 1.1)
    for x, z in kreisrand(1.4):
        w.setze(x, yl, z, k.glas(x, z))
        w.setze(x, yl + 1, z, k.glas(x, z))
    for x, z in scheibe(1.6):
        w.setze(x, yl + 2, z, w.b("gold_block"))
    w.setze(0, yl + 3, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * h, sz * h
            for y in range(H, H + _r(4 * u, 3)):
                for x, z in kreisrand(1.3 * u + 0.4, cx, cz):
                    w.setze(x, y, z, k.st(x, y, z, H))
            for kk in range(_r(1.5 * u + 1, 2)):
                for x, z in scheibe(max(0.3, 1.3 * u + 0.4 - kk), cx, cz):
                    w.setze(x, H + _r(4 * u, 3) + kk, z, kuppel(1, x, 0, z))
    # Vorhalle mit Säulen
    for x in range(-h + 1, h, 2):
        for y in range(1, H - 1):
            w.setze(x, y, h + 3, w.b("quartz_pillar", axis="y") if k.hell else k.st(x, y, h + 3, 1))
    for x in range(-h, h + 1):
        for z in range(h + 1, h + 4):
            w.setze(x, H - 1, z, w.b(k.zier))
            w.setze(x, 0, z, w.b("polished_andesite") if not k.hell else w.b("smooth_sandstone"))
    for x in range(-h, h + 1):
        for kk in range(1, h // 2 + 1):
            if abs(x) <= h - kk * 2:
                w.setze(x, H - 1 + kk, h + 3, w.b(k.zier))
    return w


def kloster(seed, g=2):
    """Kloster: Kreuzgang mit Arkaden um einen Garten mit Brunnen, Kirche an einer Seite, Klostergebäude."""
    w = _welt(seed)
    k = Kirche(w, seed)
    u = U[g]
    h = _r(8 * u + 4, 6)
    Hk = _r(4 * u + 2, 4)
    _boden(w, h + 14)
    for x in range(-h, h + 1):
        for z in range(-h, h + 1):
            w.setze(x, 0, z, w.b("grass_block", snowy=False))
    for x in range(-h - 3, h + 4):
        for z in range(-h - 3, h + 4):
            ring = max(abs(x), abs(z))
            if h < ring <= h + 3:
                w.setze(x, 0, z, w.b("polished_andesite") if not k.hell else w.b("smooth_sandstone"))
                w.setze(x, Hk + 1, z, w.b(k.dach_voll))
                if ring == h + 3:
                    for y in range(1, Hk + 1):
                        w.setze(x, y, z, k.st(x, y, z, Hk))
                if ring == h + 1:
                    t = x if abs(z) == h + 1 else z
                    if t % 3 == 0 or (x in (-h - 1, h + 1) and z in (-h - 1, h + 1)):
                        for y in range(1, Hk + 1):
                            w.setze(x, y, z, k.st(x, y, z, Hk))
                    else:
                        w.setze(x, Hk, z, w.b(k.zier))
                        w.setze(x, Hk - 1, z, treppe(w, k.tr, "east" if t % 3 == 1 else "west", "top")
                                if abs(z) == h + 1 else treppe(w, k.tr, "south" if t % 3 == 1 else "north", "top"))
    for x in range(-h - 3, h + 4):
        w.setze(x, Hk + 2, -h - 3, platte(w, k.tr))
    # Garten mit Brunnen und Wegen
    for t in range(-h, h + 1):
        w.setze(t, 0, 0, w.b("gravel"))
        w.setze(0, 0, t, w.b("gravel"))
    for x, z in kreisrand(1.6):
        w.setze(x, 1, z, w.b(k.zier))
    w.setze(0, 0, 0, w.b("water", level=0))
    for x in range(-h + 1, h):
        for z in range(-h + 1, h):
            if x and z and w.rng.random() < 0.25:
                w.setze(x, 1, z, w.b(["rose_bush" if False else "poppy", "allium", "lily_of_the_valley",
                                      "azure_bluet"][int(w.rng.integers(4))]))
    # Kirche an der Nordseite
    zk = -h - 4
    L, b = _r(14 * u + 6, 9), _r(3 * u + 1.5, 2)
    Hc = _r(8 * u + 4, 6)
    for s in (-1, 1):
        wand_x(w, k, -L // 2, L // 2, zk - (b + 1) + (1 + s) * (b + 1) // 1 * 0 + (0 if s < 0 else 0) - (0 if s < 0 else -2 * b - 2) * 0, 1, Hc,
               [(x, 2, 2, Hc - 3) for x in range(-L // 2 + 2, L // 2 - 1, 3)], Hc) if False else None
    for z in (zk, zk - 2 * b):
        wand_x(w, k, -L // 2, L // 2, z, 1, Hc, [(x, 2, 2, Hc - 3) for x in range(-L // 2 + 2, L // 2 - 1, 3)], Hc)
    for x in (-L // 2, L // 2):
        wand_z(w, k, zk - 2 * b, zk, x, 1, Hc, [(zk - b, max(2, _r(1.6 * u, 2)), 2, Hc - 3)], Hc)
    steildach(w, k, -L // 2, L // 2, zk - 2 * b, zk, Hc, entlang_z=False)
    eckturm_q(w, k, L // 2 - 2 * _r(1.5 * u + 1, 1), zk - 2 * _r(1.5 * u + 1, 1), L // 2, zk, 1, _r(Hc * 1.6, 9))
    return w


def glockenturm(seed, g=1):
    """Freistehender Glockenturm (Campanile) mit Schallarkaden, Glocke, Zifferblatt und Spitzhelm."""
    w = _welt(seed)
    k = Kirche(w, seed)
    u = U[g]
    h = _r(2.2 * u + 1, 2)
    H = _r(20 * u + 6, 12)
    _boden(w, h + 6)
    eckturm_q(w, k, -h, -h, h, h, 1, H, helm=False)
    ys = H - _r(4 * u, 3)
    for y in range(ys, H):
        for t in range(-h + 1, h):
            for (x, z) in ((t, -h), (t, h), (-h, t), (h, t)):
                if abs(t) < h:
                    w.bloecke.pop((x, y, z), None)
    w.setze(0, H - 1, 0, w.b("bell", facing="north", attachment="ceiling", powered=False))
    for y in range(ys, H):
        w.setze(0, y, 0, w.b("chain", axis="y", waterlogged=False)) if y < H - 2 else None
    turmhelm(w, k, 0, 0, h + 0.6, H + 1, _r(h * 4, 6))
    yu = ys - _r(3 * u, 3)
    for x in range(-1, 2):
        for y in range(yu - 1, yu + 2):
            w.setze(x, y, h + 1, w.b("smooth_quartz") if (x, y) != (0, yu) else w.b("gold_block"))
    return w


def rundkirche(seed, g=2):
    """Romanische Rundkirche mit Rundbogenfries, Kegeldach, Apsis und kleinem Glockenturm."""
    w = _welt(seed)
    k = Kirche(w, seed)
    u = U[g]
    R = 5 * u + 3
    H = _r(6 * u + 3, 5)
    _boden(w, R + 8)
    for y in range(0, H + 1):
        for i, (x, z) in enumerate(kreisrand(R)):
            fen = y in range(2, H - 1) and i % _r(4 * u + 1, 3) == 0
            w.setze(x, y, z, k.glas(i, y) if fen else k.st(x, y, z, H))
        if y == 0:
            for x, z in scheibe(R - 1):
                w.setze(x, 0, z, w.b("polished_andesite"))
    for x, z in kreisrand(R + 1):
        w.setze(x, H, z, treppe(w, k.tr, "north" if z > 0 else "south", "top") if abs(z) >= abs(x)
                else treppe(w, k.tr, "west" if x > 0 else "east", "top"))
    kh = _r(R * 1.2, 4)
    for kk in range(kh + 1):
        for x, z in kreisrand(max(0.3, (R + 1) * (1 - kk / (kh + 1))), 0, 0):
            w.setze(x, H + 1 + kk, z, w.b(k.dach_voll))
    w.setze(0, H + kh + 2, 0, w.b("gold_block"))
    for y in range(1, H):
        for x, z in kreisrand(R * 0.5, 0, -int(R)):
            if z <= -int(R):
                w.setze(x, y, z, k.st(x, y, z, H))
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(0, y, int(R), w.b("spruce_door", facing="south", half=half, hinge="left", open=False, powered=False))
    eckturm_q(w, k, int(R) - 1, -2, int(R) + 3, 2, 1, _r(H * 1.8, 8))
    return w


def wegschrein(seed, g=1):
    """Kleiner Wegschrein mit Dach, Kerzen, Blumen und Bank."""
    w = _welt(seed)
    k = Kirche(w, seed)
    u = U[g]
    h = _r(1.2 * u + 0.6, 1)
    H = _r(4 * u + 2, 3)
    _boden(w, h + 5)
    for y in range(1, H):
        for x in range(-h, h + 1):
            w.setze(x, y, -h, k.st(x, y, -h, H))
        for z in range(-h, h + 1):
            for x in (-h, h):
                w.setze(x, y, z, k.st(x, y, z, H))
    for x in range(-h, h + 1):
        for z in range(-h, h + 1):
            w.setze(x, 0, z, w.b(k.zier))
    w.setze(0, 1, -h + 1, w.b("white_candle", candles=4, lit=True, waterlogged=False))
    w.setze(0, 2, -h, k.glas(0, 0))
    steildach(w, k, -h, h, -h, h, H - 1, entlang_z=True)
    for x in range(-h - 1, h + 2, 2):
        w.setze(x, 1, h + 2, w.b(["poppy", "dandelion", "cornflower"][abs(x) % 3]))
    for x in range(-1, 2):
        w.setze(x, 1, h + 4, treppe(w, "spruce", "south"))
    return w


KATHEDRALEN = {
    "kathedrale": ("Gotische Kathedrale", kathedrale),
    "dorfkapelle": ("Dorfkapelle", dorfkapelle),
    "kuppeltempel": ("Kuppeltempel", kuppeltempel),
    "kloster": ("Kloster mit Kreuzgang", kloster),
    "glockenturm": ("Glockenturm", glockenturm),
    "rundkirche": ("Rundkirche", rundkirche),
    "wegschrein": ("Wegschrein", wegschrein),
}

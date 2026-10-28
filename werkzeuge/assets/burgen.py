"""Burgen & Festungen – Paket: Bergfried, Torburg mit Zugbrücke, Ringburg, Wehrmauer, Wasserburg,
Bergfeste, Märchenschloss, Eckwachturm. Stil 1 graues Mauerwerk mit Schieferdächern und roten Bannern,
Stil 2 heller Sandstein mit blauen Dächern und goldenen Spitzen."""

from __future__ import annotations

import math

from lib import Verlauf, Welt, ueberwuchern
from skulptur import kreisrand, platte, scheibe, treppe, verbinde, zur_mitte

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


class Burg:
    def __init__(self, w, seed):
        self.w = w
        b = w.b
        self.hell = _stil(seed) == 1
        if not self.hell:
            self.mauer = Verlauf(w, "Mauer", ["mossy_cobblestone", "cobblestone", "stone_bricks", "cracked_stone_bricks",
                                              "stone_bricks", "polished_andesite"])
            self.tr = "stone_brick"
            self.voll = "stone_bricks"
            self.dach = Verlauf(w, "Schiefer", ["deepslate_tiles", "polished_deepslate", "deepslate_tiles"])
            self.dach_tr = "deepslate_tile"
            self.banner = ["red_wool", "yellow_wool"]
            self.spitze = b("lightning_rod", facing="up", powered=False, waterlogged=False)
            self.holz = "spruce"
        else:
            self.mauer = Verlauf(w, "Sandstein", ["sandstone", "cut_sandstone", "smooth_sandstone", "calcite",
                                                  "smooth_quartz"])
            self.tr = "smooth_sandstone"
            self.voll = "smooth_sandstone"
            self.dach = Verlauf(w, "Blaudach", ["blue_terracotta", "blue_concrete", "light_blue_terracotta"])
            self.dach_tr = "prismarine_brick"
            self.banner = ["blue_wool", "white_wool"]
            self.spitze = b("gold_block")
            self.holz = "dark_oak"

    def stein(self, x, y, z, hoehe=20):
        return self.mauer(0.3 + 4.5 * min(1, y / max(1, hoehe)) + self.w.rng.random() * 0.9, x, y, z)


def _boden(w, r, cx=0, cz=0):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, w.b("grass_block", snowy=False), ueberschreiben=False)


def rundturm(w, m, cx, cz, R, H, y0=0, kegel=True, kegel_h=None, schlitze=True):
    """Runder Turm mit Schießscharten, Kragsteinkranz, Zinnen und optional spitzem Kegeldach."""
    for y in range(y0, y0 + H):
        for x, z in scheibe(R + (1 if y == y0 else 0), cx, cz):
            d = math.hypot(x - cx, z - cz)
            if d > R - 1.1 or y == y0:
                a = math.atan2(z - cz, x - cx)
                schlitz = schlitze and (y - y0) % 5 == 3 and abs(math.sin(2 * a)) < 0.15 and d > R - 0.6
                w.setze(x, y, z, w.b("air") if False else (w.b("iron_bars", north=False, south=False, east=False,
                                                                         west=False, waterlogged=False)
                                                                if schlitz else m.stein(x, y, z, H)))
            elif (y - y0) % 6 == 5:
                w.setze(x, y, z, w.b(f"{m.holz}_planks"))
    yt = y0 + H
    for x, z in kreisrand(R + 1, cx, cz):
        w.setze(x, yt - 1, z, treppe(w, m.tr, zur_mitte(x, z, cx, cz), "top"))
    for x, z in scheibe(R + 1, cx, cz):
        w.setze(x, yt, z, m.stein(x, yt, z, 1))
    for i, (x, z) in enumerate(kreisrand(R + 1, cx, cz)):
        if i % 2 == 0 or not kegel:
            w.setze(x, yt + 1, z, m.stein(x, yt + 1, z, 1))
    if kegel:
        kh = kegel_h or _r(R * 2.6, 4)
        for k in range(kh + 1):
            r = (R + 0.7) * (1 - k / (kh + 1)) ** 1.1
            for x, z in kreisrand(max(0.3, r), cx, cz):
                w.setze(x, yt + 1 + k, z, m.dach(3 * k / kh + w.rng.random() * 0.4, x, yt + k, z))
        w.setze(cx, yt + kh + 2, cz, m.spitze)
        _fahne(w, m, cx, yt + kh + 3, cz, max(2, int(R)))
        return yt + kh + 3
    return yt + 1


def _fahne(w, m, x, y, z, laenge):
    for k in range(2):
        w.setze(x, y + k, z, w.b(f"{m.holz}_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False))
    for k in range(laenge):
        w.setze(x + 1 + k, y + 1, z, w.b(m.banner[k % 2]))
        if k < laenge - 1:
            w.setze(x + 1 + k, y, z, w.b(m.banner[(k + 1) % 2]))


def eckturm(w, m, x0, z0, x1, z1, H, y0=0, dach=True):
    """Eckiger Turm mit Kragsteinen, Zinnen und Pyramidendach."""
    for y in range(y0, y0 + H):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                rand = x in (x0, x1) or z in (z0, z1)
                if rand:
                    mitte = (x == (x0 + x1) // 2 or z == (z0 + z1) // 2)
                    schlitz = (y - y0) % 5 == 3 and mitte and not (x in (x0, x1) and z in (z0, z1))
                    w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                         waterlogged=False) if schlitz else m.stein(x, y, z, H))
                elif (y - y0) % 6 == 5:
                    w.setze(x, y, z, w.b(f"{m.holz}_planks"))
    yt = y0 + H
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            if x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1):
                if not (x in (x0 - 1, x1 + 1) and z in (z0 - 1, z1 + 1)):
                    if x in (x0 - 1, x1 + 1):
                        fac = "east" if x < x0 else "west"
                    else:
                        fac = "south" if z < z0 else "north"
                    w.setze(x, yt - 1, z, treppe(w, m.tr, fac, "top"))
                w.setze(x, yt, z, m.stein(x, yt, z, 1))
                if (x + z) % 2 == 0:
                    w.setze(x, yt + 1, z, m.stein(x, yt + 1, z, 1))
            else:
                w.setze(x, yt, z, m.stein(x, yt, z, 1))
    if dach:
        k = 0
        while True:
            ax, bx, az, bz = x0 + k, x1 - k, z0 + k, z1 - k
            if ax > bx or az > bz:
                break
            for x in range(ax, bx + 1):
                for z in range(az, bz + 1):
                    if x in (ax, bx) or z in (az, bz):
                        w.setze(x, yt + 1 + k, z, m.dach(3 * k / max(1, (x1 - x0) // 2) + w.rng.random() * 0.4, x,
                                                         yt + k, z))
            k += 1
        mx, mz = (x0 + x1) // 2, (z0 + z1) // 2
        w.setze(mx, yt + 1 + k, mz, m.spitze)
        return yt + 1 + k
    return yt + 1


def mauerzug(w, m, a, b, H, dick=2, y0=0):
    """Wehrmauer von a nach b (x, z) mit Wehrgang und Zinnen auf beiden Seiten."""
    (ax, az), (bx, bz) = a, b
    n = int(max(abs(bx - ax), abs(bz - az)))
    dx, dz = (bx - ax) / max(1, n), (bz - az) / max(1, n)
    nx, nz = -dz, dx
    for k in range(n + 1):
        cx, cz = ax + dx * k, az + dz * k
        for t in range(-dick // 2, dick - dick // 2):
            x, z = round(cx + nx * t), round(cz + nz * t)
            for y in range(y0, y0 + H + 1):
                w.setze(x, y, z, m.stein(x, y, z, H))
        for t in (-dick // 2 - 1, dick - dick // 2):
            x, z = round(cx + nx * t), round(cz + nz * t)
            w.setze(x, y0 + H + 1, z, m.stein(x, y0 + H + 1, z, H))
            if k % 2 == 0:
                w.setze(x, y0 + H + 2, z, m.stein(x, y0 + H + 2, z, H))
            w.setze(x, y0 + H, z, m.stein(x, y0 + H, z, H))


def tor(w, m, x, z, breite, hoehe, achse="x", y0=1):
    """Torbogen (achse: entlang welcher Achse man hindurchgeht) mit Fallgitter."""
    for t in range(-breite // 2 - 2, breite // 2 + 3):
        for y in range(y0, y0 + hoehe + 2):
            for d in range(-3, 4):
                px, pz = (x + d, z + t) if achse == "x" else (x + t, z + d)
                innen = abs(t) <= breite // 2 and (y < y0 + hoehe or (y == y0 + hoehe and abs(t) < breite // 2))
                if innen:
                    w.bloecke.pop((px, y, pz), None)
    gitter = []
    for t in range(-breite // 2, breite // 2 + 1):
        px, pz = (x, z + t) if achse == "x" else (x + t, z)
        for y in range(y0 + hoehe - 2, y0 + hoehe):
            gitter.append((px, y, pz))
    verbinde(w, gitter, "iron_bars")


# ============================================================================ Typen

def bergfried(seed, g=1):
    """Wuchtiger Bergfried mit Eckerkern, Schießscharten, Zinnenkranz, Wehrplattform und Banner."""
    w = _welt(seed)
    m = Burg(w, seed)
    u = U[g]
    h = _r(4 * u + 2, 3)
    H = _r(18 * u + 6, 10)
    _boden(w, h + 6)
    eckturm(w, m, -h, -h, h, h, H, dach=m.hell)
    for sx in (-1, 1):
        for sz in (-1, 1):
            rundturm(w, m, sx * (h + 1), sz * (h + 1), 1.2 * u + 0.6, _r(4 * u + 2, 3), y0=H - _r(4 * u + 2, 3) + 2,
                     kegel=True, kegel_h=_r(4 * u + 1, 3), schlitze=False)
    for y, half in ((1, "lower"), (2, "upper")):
        w.bloecke.pop((0, y, h), None)
        w.setze(0, y, h, w.b(f"{m.holz}_door", facing="south", half=half, hinge="left", open=False, powered=False))
    for k in range(_r(3 * u, 2)):
        w.setze(k - 1, 4 + k, h + 1, m.stein(0, 0, 0, 1)) if False else None
    for y in range(H // 3, H - 2, 2):
        w.setze(0, y, h + 1, w.b(m.banner[(y // 2) % 2]))
    if not m.hell:
        _fahne(w, m, 0, H + 2, 0, _r(3 * u, 2))
    return w


def torburg(seed, g=1):
    """Torburg: zwei runde Flankentürme, Torhaus mit Fallgitter, Zugbrücke über einen Wassergraben."""
    w = _welt(seed)
    m = Burg(w, seed)
    u = U[g]
    R = 2.4 * u + 1.4
    H = _r(11 * u + 5, 7)
    br = _r(1.6 * u + 1.5, 3) | 1
    abst = br // 2 + int(R) + 2
    _boden(w, abst + R + 10)
    for x in range(-abst - int(R) - 6, abst + int(R) + 7):
        for z in range(4, 4 + _r(3 * u + 2, 3)):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("dirt"))
    for s in (-1, 1):
        rundturm(w, m, s * abst, 0, R, H)
    eckturm(w, m, -abst + 1, -int(R), abst - 1, int(R), H - 3, dach=False)
    tor(w, m, 0, 0, br, _r(3.5 * u + 2, 4), achse="z")
    for x in range(-br // 2, br // 2 + 1):
        for z in range(int(R) + 1, 4 + _r(3 * u + 2, 3) + 1):
            w.setze(x, 0, z, w.b(f"{m.holz}_planks"))
    for s in (-1, 1):
        for k in range(_r(3 * u + 2, 3)):
            w.setze(s * (br // 2 + 1), 1 + k // 2, int(R) + 1 + k, w.b("chain", axis="z", waterlogged=False))
    for s in (-1, 1):
        w.setze(s * (br // 2 + 1), 3, int(R) + 1, w.b("lantern", hanging=False, waterlogged=False))
    for y in range(4, H - 4, 2):
        w.setze(0, y, int(R) + 1, w.b(m.banner[(y // 2) % 2]))
    return w


def ringburg(seed, g=2):
    """Ringburg: runde Ringmauer mit Türmen, Tor, Bergfried in der Mitte, Palas und Burghof."""
    w = _welt(seed)
    m = Burg(w, seed)
    u = U[g]
    R = 14 * u + 6
    _boden(w, R + 5)
    for x, z in scheibe(R - 2):
        w.setze(x, 0, z, w.b("coarse_dirt") if w.rng.random() < 0.3 else w.b("gravel") if w.rng.random() < 0.2
                else w.b("grass_block", snowy=False))
    n = 4 + g
    Hm = _r(6 * u + 3, 5)
    pts = [(round(math.cos(i * 2 * math.pi / n + math.pi / n) * R), round(math.sin(i * 2 * math.pi / n + math.pi / n) * R))
           for i in range(n)]
    for i in range(n):
        mauerzug(w, m, pts[i], pts[(i + 1) % n], Hm, dick=2)
    for (x, z) in pts:
        rundturm(w, m, x, z, 1.8 * u + 1.2, Hm + _r(4 * u, 3), kegel=m.hell or g % 2 == 0)
    tor(w, m, 0, round(R * math.cos(math.pi / n)), _r(1.6 * u + 1.5, 3) | 1, _r(3 * u + 2, 3), achse="z")
    h = _r(2.6 * u + 1.5, 2)
    eckturm(w, m, -h - int(R * 0.25), -h - int(R * 0.3), h - int(R * 0.25), h - int(R * 0.3), _r(14 * u + 5, 9),
            dach=True)
    # Palas
    from bau import Stil, kasten_haus, satteldach
    st = Stil(w, m.mauer, holz=m.holz, dach=m.dach_tr, dach_voll="deepslate_tiles" if not m.hell else "prismarine_bricks",
              sockel=m.voll, fachwerk=False)
    px0, pz0 = int(R * 0.05), -int(R * 0.45)
    yt, a, b, c, d = kasten_haus(w, st, px0, pz0, px0 + _r(8 * u + 3, 6), pz0 + _r(4 * u + 3, 5), 0, 2, eh=4,
                                 fenster_abstand=2, blumen=False)
    satteldach(w, st, a, b, c, d, yt)
    # Brunnen im Hof
    for x, z in kreisrand(1.5 * u + 0.6, 0, int(R * 0.3)):
        w.setze(x, 1, z, m.stein(x, 1, z, 1))
    for x, z in scheibe(1.5 * u - 0.4, 0, int(R * 0.3)):
        w.setze(x, 0, z, w.b("water", level=0))
    return w


def wehrmauer(seed, g=1):
    """Gerades Stück Stadtmauer mit Wehrgang, zwei Türmen, Tor und Treppen – zum Aneinanderreihen."""
    w = _welt(seed)
    m = Burg(w, seed)
    u = U[g]
    L = _r(20 * u + 8, 12)
    Hm = _r(7 * u + 3, 5)
    for x in range(-L - 4, L + 5):
        for z in range(-5, 6):
            w.setze(x, 0, z, w.b("grass_block", snowy=False))
    mauerzug(w, m, (-L, 0), (L, 0), Hm, dick=2 + (g >= 2))
    R = 1.8 * u + 1.2
    for s in (-1, 1):
        rundturm(w, m, s * L, 0, R, Hm + _r(4 * u, 3), kegel=m.hell)
    tor(w, m, 0, 0, _r(1.6 * u + 1.5, 3) | 1, _r(3 * u + 2, 3), achse="z")
    for k in range(Hm):
        for t in (1, 2):
            w.setze(-L + int(R) + 2 + k, k + 1, t + 1, treppe(w, m.tr, "west"))
    return w


def wasserburg(seed, g=2):
    """Quadratische Wasserburg auf einer Insel im Graben: Ecktürme, Torbau mit Brücke, Innenhof, Kapelle."""
    w = _welt(seed)
    m = Burg(w, seed)
    u = U[g]
    h = _r(10 * u + 5, 7)
    gr = _r(4 * u + 2, 3)
    for x in range(-h - gr - 3, h + gr + 4):
        for z in range(-h - gr - 3, h + gr + 4):
            ring = max(abs(x), abs(z))
            if ring > h + gr:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
            elif ring > h + 1:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("dirt"))
            else:
                w.setze(x, 0, z, m.stein(x, 0, z, 1))
    Hm = _r(6 * u + 3, 5)
    ecken = [(-h, -h), (h, -h), (h, h), (-h, h)]
    for i in range(4):
        mauerzug(w, m, ecken[i], ecken[(i + 1) % 4], Hm, dick=2)
    for (x, z) in ecken:
        rundturm(w, m, x, z, 2 * u + 1.2, Hm + _r(5 * u, 3), kegel=True)
    tor(w, m, 0, h, _r(1.6 * u + 1.5, 3) | 1, _r(3 * u + 2, 3), achse="z")
    eckturm(w, m, -2 - int(u), h - 2, 2 + int(u), h + 2, Hm + 3, dach=True)
    tor(w, m, 0, h, _r(1.6 * u + 1.5, 3) | 1, _r(3 * u + 2, 3), achse="z")
    for x in range(-1 - int(u * 0.5), 2 + int(u * 0.5)):
        for z in range(h + 2, h + gr + 2):
            w.setze(x, 0, z, w.b(f"{m.holz}_planks"))
    return w


def bergfeste(seed, g=2):
    """Bergfeste auf einem Felssporn: steile Felsen, Mauern entlang der Kante, Türme und ein Hauptturm."""
    w = _welt(seed)
    m = Burg(w, seed)
    u = U[g]
    R = 12 * u + 6
    Hf = _r(10 * u + 4, 6)
    fels = Verlauf(w, "Fels", ["tuff", "andesite", "stone", "cobblestone", "stone"])
    for x in range(-int(R) - 3, int(R) + 4):
        for z in range(-int(R) - 3, int(R) + 4):
            a = math.atan2(z, x)
            d = math.hypot(x, z)
            rr = R * (1 + 0.15 * math.sin(3 * a + 1) + 0.08 * math.sin(7 * a))
            for y in range(0, Hf + 1):
                t = y / Hf
                if d <= rr * (1.25 - 0.35 * t) + 0.6 * math.sin(y * 0.8 + a * 4):
                    w.setze(x, y, z, fels(0.5 + 2.5 * t + w.rng.random() * 0.8, x, y, z))
    n = 5 + g
    Hm = _r(5 * u + 2, 4)
    pts = [(round(math.cos(i * 2 * math.pi / n) * R * 0.8), round(math.sin(i * 2 * math.pi / n) * R * 0.8)) for i in range(n)]
    for i in range(n):
        mauerzug(w, m, pts[i], pts[(i + 1) % n], Hm, dick=2, y0=Hf + 1)
    for i, (x, z) in enumerate(pts):
        rundturm(w, m, x, z, 1.4 * u + 1, Hm + _r(3 * u, 2), y0=Hf + 1, kegel=i % 2 == 0)
    h = _r(2.8 * u + 1.5, 2)
    eckturm(w, m, -h, -h, h, h, _r(16 * u + 4, 8), y0=Hf + 1, dach=True)
    for k in range(Hf + 1):
        for t in range(2):
            x = int(R * 0.5) + k // 2
            w.setze(x + t, k, int(R * 1.05) - k // 2 + 3, treppe(w, m.tr, "north"))
    ueberwuchern(w, None, ranken=0.25, moos_oben=0.2, pflanzen=0.2, buesche=0.03, max_ranke=4)
    return w


def maerchenschloss(seed, g=2):
    """Märchenschloss: viele schlanke Rundtürme verschiedener Höhe mit hohen Spitzdächern, Hauptbau,
    Balkone und Wimpel."""
    w = _welt(seed)
    m = Burg(w, seed)
    m.mauer = Verlauf(w, "Weiß", ["polished_diorite", "calcite", "smooth_quartz", "white_concrete"]) if not m.hell else \
        Verlauf(w, "Rosé", ["pink_terracotta", "white_terracotta", "calcite", "smooth_quartz"])
    m.dach = Verlauf(w, "Spitzdach", ["blue_terracotta", "blue_concrete", "light_blue_concrete"]) if not m.hell else \
        Verlauf(w, "Spitzdach", ["purple_terracotta", "magenta_terracotta", "pink_concrete"])
    m.spitze = w.b("gold_block")
    u = U[g]
    _boden(w, 14 * u + 8)
    h = _r(5 * u + 2, 3)
    H = _r(10 * u + 4, 6)
    eckturm(w, m, -h, -h, h, h, H, dach=True)
    rundturm(w, m, 0, 0, 1.6 * u + 1.2, H + _r(10 * u + 3, 6), kegel=True, kegel_h=_r(8 * u + 3, 5))
    for i in range(5 + g):
        a = i * 2 * math.pi / (5 + g) + 0.3
        d = h + 1 + (i % 2) * 2 * u
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        rr = (0.9 + 0.6 * ((i * 3) % 4) / 3) * u + 0.8
        hh = H + int((-3 + 2 * (i % 4)) * u) + 3
        rundturm(w, m, x, z, rr, max(5, hh), kegel=True, kegel_h=_r(rr * 3.5, 4), schlitze=False)
    for y, half in ((1, "lower"), (2, "upper")):
        w.bloecke.pop((0, y, h), None)
        w.setze(0, y, h, w.b("dark_oak_door", facing="south", half=half, hinge="left", open=False, powered=False))
    return w


def eckwachturm(seed, g=1):
    """Eckiger Wachturm mit Pyramidendach, Treppe außen und Laternen."""
    w = _welt(seed)
    m = Burg(w, seed)
    u = U[g]
    h = _r(2 * u + 1, 2)
    H = _r(12 * u + 4, 7)
    _boden(w, h + 6)
    eckturm(w, m, -h, -h, h, h, H, dach=True)
    for y, half in ((1, "lower"), (2, "upper")):
        w.bloecke.pop((0, y, h), None)
        w.setze(0, y, h, w.b(f"{m.holz}_door", facing="south", half=half, hinge="left", open=False, powered=False))
    for s in (-1, 1):
        w.setze(s * 2, 1, h + 1, w.b("lantern", hanging=False, waterlogged=False))
    return w


BURGEN = {
    "bergfried": ("Bergfried", bergfried),
    "torburg": ("Torburg mit Zugbrücke", torburg),
    "ringburg": ("Ringburg", ringburg),
    "wehrmauer": ("Wehrmauer", wehrmauer),
    "wasserburg": ("Wasserburg", wasserburg),
    "bergfeste": ("Bergfeste", bergfeste),
    "maerchenschloss": ("Märchenschloss", maerchenschloss),
    "eckwachturm": ("Eckwachturm", eckwachturm),
}

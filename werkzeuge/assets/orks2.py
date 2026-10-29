"""Orklager (neu) – 20 Bauten: Kriegslager, Zelte, Häuptlingshalle, Türme, Totems, Schmiede, Knochentor, Thron,
Kampfgrube, Katapult, Belagerungsturm, Schamanenhütte, Räucherei, Wargzwinger, Trophäenwand, Kriegstrommeln,
Seilbrücke, Signalfeuer, Knochenhütte, Palisadenring."""

from __future__ import annotations

import math

import numpy as np

import modbloecke as MB
import pracht as P
from lib import Rauschen, laub
from pracht import Mat, gelaende
from skulptur import Skulptur, dreh_y, ell, kap, kreisrand, scheibe
from spuk import knorrbaum, schaedel
from weltwunder import bl, hohl, sk

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    from lib import Welt
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


class Ork:
    """Stil 0: Rot/Schwarz, Fichte, Lehm. Stil 1: Grün/Braun, Dunkeleiche, Schwarzstein."""

    def __init__(self, w, seed):
        self.w = w
        rot = _stil(seed) == 0
        self.farbe = ["red_wool", "black_wool"] if rot else ["green_wool", "brown_wool"]
        self.holz = "spruce" if rot else "dark_oak"
        self.fell = Mat(w, ["brown_wool", "brown_terracotta", "black_wool", "brown_wool", "light_gray_wool"],
                        kontrast=1.0)
        self.stein = Mat(w, ["mud_bricks", "packed_mud", "cobblestone", "mossy_cobblestone"] if rot else
                         ["blackstone", "cobbled_deepslate", "polished_blackstone_bricks", "basalt"], kontrast=1.0)

    def log(self, achse="y"):
        return self.w.b(f"{self.holz}_log", axis=achse)


def orkboden(w, R, cx=0, cz=0):
    r1 = Rauschen(w, 3)
    rng = w.rng
    for x, z in scheibe(R, cx, cz):
        v = r1(x, 0, z)
        w.setze(x, 0, z, w.b("coarse_dirt") if v < 0.35 else w.b("mud") if v < 0.45 else
                w.b("podzol", snowy=False) if v < 0.6 else w.b("rooted_dirt") if v < 0.7 else
                w.b("grass_block", snowy=False), ueberschreiben=False)
        if w.frei(x, 1, z) and rng.random() < 0.03:
            w.setze(x, 1, z, w.b("bone_block", axis=["x", "z"][int(rng.integers(2))]) if rng.random() < 0.3 else
                    w.b("dead_bush"))


def pfahl(w, O, x, z, y0, h, spitze=True):
    for y in range(y0, y0 + h):
        w.setze(x, y, z, O.log())
    if spitze:
        w.setze(x, y0 + h, z, w.b("pointed_dripstone", vertical_direction="up", thickness="tip", waterlogged=False))


def palisade(w, O, pts, h=4, tor=()):
    menge = set(pts)
    for i, (x, z) in enumerate(pts):
        if (x, z) in tor:
            continue
        hh = h + (i % 3 == 0) - (i % 5 == 0)
        pfahl(w, O, x, z, 1, hh)
        if i % 7 == 0:
            w.setze(x, hh - 1, z + 0, schaedel(w, rot=0)) if False else None


def fahne(w, O, x, z, y0=1, h=7):
    for y in range(y0, y0 + h):
        w.setze(x, y, z, w.b(f"{O.holz}_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    for k in range(3):
        w.setze(x + 1, y0 + h - 1 - k, z, w.b(O.farbe[k % 2]))
        w.setze(x + 2, y0 + h - 1 - k, z, w.b(O.farbe[(k + 1) % 2])) if k < 2 else None
    w.setze(x, y0 + h, z, schaedel(w, rot=4))


def zelt_kegel(w, O, cx, cz, R, H, y0=1):
    for y in range(y0, y0 + H):
        r = R * (1 - (y - y0) / H)
        for x, z in kreisrand(max(0.5, r), cx, cz):
            if not (y < y0 + 2 and abs(x - cx) <= 0 and z > cz):
                w.setze(x, y, z, O.fell(x, y, z, 0.5))
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.4
        w.setze(round(cx + math.cos(a) * 0.6), y0 + H, round(cz + math.sin(a) * 0.6),
                w.b(f"{O.holz}_fence", north=False, south=False, east=False, west=False, waterlogged=False))
        w.setze(round(cx + math.cos(a) * 0.6), y0 + H + 1, round(cz + math.sin(a) * 0.6),
                w.b(f"{O.holz}_fence", north=False, south=False, east=False, west=False, waterlogged=False))


def langzelt(w, O, x0, z0, x1, z1, H=5):
    """Firstzelt aus Fellen über Pfosten (First entlang x)."""
    mz = (z0 + z1) / 2
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            y = 1 + round(H - abs(z - mz) * H / ((z1 - z0) / 2 + 0.5))
            w.setze(x, max(1, y), z, O.fell(x, y, z, 0.5))
            if x in (x0, x1):
                for yy in range(1, max(1, y)):
                    if not (x == x0 and abs(z - mz) < 1):
                        w.setze(x, yy, z, O.fell(x, yy, z, 0.3))
    for x in (x0, x1):
        for y in range(1, H + 3):
            w.setze(x, y, round(mz), O.log())
        w.setze(x, H + 3, round(mz), schaedel(w, rot=4))


def feuerstelle(w, x, z, gross=False):
    for dx, dz in scheibe(1.6 if gross else 1.2):
        if dx or dz:
            w.setze(x + dx, 1, z + dz, w.b("cobblestone") if (dx + dz) % 2 else w.b("blackstone"))
    w.setze(x, 1, z, w.b("campfire", lit=True, signal_fire=gross, facing="north", waterlogged=False))


def knochenhaufen(w, x, z, n=4):
    rng = w.rng
    for k in range(n):
        w.setze(x + int(rng.integers(-1, 2)), 1 + (k // 3), z + int(rng.integers(-1, 2)),
                w.b("bone_block", axis=["x", "y", "z"][k % 3]) if k % 4 else schaedel(w))


# ============================================================================ Bauten


def kriegszelt(seed, g=1):
    """Kriegszelt: großes Kegelzelt aus Fellen auf Pfählen, mit Schädeln geschmückt, Feuerstelle, Fahnen,
    Waffenständer und Knochenhaufen."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    R = 3.5 * u + 2.5
    orkboden(w, _r(R + 7))
    zelt_kegel(w, O, 0, 0, R, _r(R * 2 + 1))
    feuerstelle(w, 0, round(R) + 4)
    fahne(w, O, -round(R) - 2, 2, 1, _r(5 * u + 4))
    knochenhaufen(w, round(R) + 2, -2)
    for k in range(3):
        w.setze(round(R) + 3, 1, round(R) - k, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return w


def haeuptlingshalle(seed, g=2):
    """Häuptlingshalle: lange Halle aus Stämmen mit Fellen und Lehm, gewaltiges Hörnergeweih über dem Eingang,
    Schädelreihen am First, Thron im Inneren und Feuerrinne."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    a, b = _r(8 * u + 4), _r(4 * u + 3)
    orkboden(w, a + 7)
    H = _r(3 * u + 3)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            rand = x in (-a, a) or z in (-b, b)
            if rand:
                for y in range(1, H + 1):
                    w.setze(x, y, z, O.log() if x % 3 == 0 or z in (-b, b) and x in (-a, a) else
                            O.stein(x, y, z, y / H))
    for x in range(-a - 1, a + 2):
        for z in range(-b - 1, b + 2):
            y = H + 1 + (b + 1 - abs(z))
            w.setze(x, y, z, O.fell(x, y, z, 0.5))
        w.setze(x, H + b + 3, 0, schaedel(w, rot=4) if x % 3 == 0 else O.log("x"))
    for y in (1, 2, 3):
        w.bloecke.pop((a, y, 0), None)
    S = Skulptur(w, 0.4 * u + 0.2)
    S.mat("h", bl(w, "bone_block"))
    for sz in (-1, 1):
        S.plus(kap((0, 0, sz * 1.0), (1.5, 4, sz * 4), 0.8, 0.5), "h")
        S.plus(kap((1.5, 4, sz * 4), (0.5, 8, sz * 3.5), 0.5, 0.15), "h")
    S.rendern((-2, -1, -6), (4, 10, 6), versatz=(a + 1.5, H + 1.01, 0.5))
    for x in range(-a + 2, a - 1):
        w.setze(x, 0, 0, w.b("magma_block") if x % 2 else w.b("campfire", lit=True, signal_fire=False,
                                                                   facing="north", waterlogged=False))
    w.setze(-a + 1, 1, 0, w.b("polished_blackstone_stairs", facing="east", half="bottom", shape="straight",
                              waterlogged=False))
    for sx in (-1, 1):
        fahne(w, O, a + 3, sx * (b + 1), 1, _r(6 * u + 4))
    hohl(w, 2)
    return w


def wachturm(seed, g=1):
    """Ork-Wachturm: windschiefer Turm aus Stämmen und Querstreben, Plattform mit Fellunterstand, Spießen und
    Alarmhorn, Leiter und Fahne."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    H = _r(10 * u + 6)
    orkboden(w, _r(6 * u + 5))
    B = 2
    for y in range(1, H + 1):
        sh = round((y / H) * 1.2)
        for sx in (-B, B):
            for sz in (-B, B):
                w.setze(sx + sh, y, sz, O.log())
        if y % 4 == 0:
            for t in range(-B, B + 1):
                w.setze(t + sh, y, -B, O.log("x"))
                w.setze(t + sh, y, B, O.log("x"))
    sh = 1
    for x in range(-B - 1, B + 2):
        for z in range(-B - 1, B + 2):
            w.setze(x + sh, H + 1, z, w.b(f"{O.holz}_planks"))
            if max(abs(x), abs(z)) == B + 1:
                pfahl(w, O, x + sh, z, H + 2, 1 + (x + z) % 2)
    for x in range(-B, B + 1):
        for z in range(-B, B + 1):
            if abs(z) <= B:
                w.setze(x + sh, H + 5, z, O.fell(x, 0, z, 0.5))
    for y in range(1, H + 1):
        w.setze(-B - 1 + round((y / H) * 1.2), y, 0, w.b("ladder", facing="west", waterlogged=False))
    fahne(w, O, B + 1 + sh, B + 1, H + 2, 5)
    return w


def totempfahl(seed, g=1):
    """Totempfahl: geschnitzter Pfahl mit übereinander gestapelten Fratzen, Hörnern, Schwingen und Schädeln, umgeben
    von Opferschalen und Pfählen."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    H = _r(12 * u + 6)
    orkboden(w, _r(5 * u + 5))
    farben = ["red_terracotta", "black_terracotta", "yellow_terracotta", "white_terracotta", "green_terracotta"]
    for y in range(1, H + 1):
        k = (y - 1) // 3
        for dx in (0, 1):
            for dz in (0, 1):
                w.setze(dx, y, dz, w.b(farben[(k + dx) % len(farben)]) if (y % 3 == 2 and dz == 1) else O.log())
        if y % 3 == 2:
            w.setze(0, y, 2, w.b("shroomlight") if k % 2 else w.b("black_concrete"))
            w.setze(1, y, 2, w.b("shroomlight") if k % 2 else w.b("black_concrete"))
    for sx in (-1, 2):
        for k in range(3):
            w.setze(sx + (k if sx > 0 else -k), H - 3 + k, 0, w.b("bone_block", axis="x"))
    w.setze(0, H + 1, 0, schaedel(w, rot=0))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * (3 + u)), round(math.sin(a) * (3 + u))
        pfahl(w, O, x, z, 1, 2 + i % 2)
    return w


def orkschmiede(seed, g=1):
    """Orkschmiede: offener Unterstand mit Lavagrube als Esse, Ambossen, Schleifrad, Waffengestellen voller
    Speere und ein Schlot aus Schwarzstein."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    a, b = _r(5 * u + 3), _r(3 * u + 2)
    orkboden(w, a + 6)
    for x in (-a, a):
        for z in (-b, b):
            for y in range(1, 6):
                w.setze(x, y, z, O.log())
    for x in range(-a - 1, a + 2):
        for z in range(-b - 1, b + 2):
            w.setze(x, 6 + (b + 1 - abs(z)) // 2, z, O.fell(x, 6, z, 0.4))
    for x, z in scheibe(1.5, -a + 2, 0):
        w.setze(x, 0, z, w.b("lava", level=0))
        w.setze(x, 1, z, w.b("blackstone")) if math.hypot(x + a - 2, z) > 1.2 else None
    for y in range(1, _r(10 * u + 6)):
        for x, z in kreisrand(1.0, -a + 2, -b - 2):
            w.setze(x, y, z, O.stein(x, y, z, y / 10))
    w.setze(-a + 2, _r(10 * u + 6), -b - 2, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                 waterlogged=False))
    for k in range(2):
        w.setze(k * 2, 1, 0, w.b("anvil", facing="north"))
    w.setze(3, 1, 1, w.b("grindstone", face="floor", facing="north"))
    for z in range(-b + 1, b):
        for y in (1, 2):
            w.setze(a + 2, y, z, w.b(f"{O.holz}_fence", north=True, south=True, east=False, west=False,
                                     waterlogged=False))
        w.setze(a + 2, 3, z, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return w


def knochentor(seed, g=2):
    """Knochentor: zwei gewaltige Stoßzähne bilden einen Bogen über dem Lagereingang, behängt mit Ketten und
    Schädeln, flankiert von Palisaden und Feuerkörben."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    s = 0.7 * u + 0.3
    orkboden(w, _r(10 * s + 6))
    S = Skulptur(w, s)
    S.mat("h", lambda x, y, z, *_: w.b("bone_block", axis="y") if (x + y) % 4 else w.b("calcite"))
    for sx in (-1, 1):
        pts = [(sx * 7, 0, 0), (sx * 7.5, 5, 0), (sx * 6.5, 10, 0), (sx * 4, 14, 0), (sx * 0.5, 15.5, 0)]
        for i in range(4):
            S.plus(kap(pts[i], pts[i + 1], 1.6 - i * 0.3, 1.3 - i * 0.3), "h")
    S.rendern((-10, -1, -3), (10, 18, 3), versatz=(0.5, 1.01, 0.5))
    for k in range(4):
        x = round((k - 1.5) * 3 * s)
        for y in range(round(12 * s), round(14 * s)):
            w.setze(x, y, 0, w.b("chain", axis="y", waterlogged=False)) if w.frei(x, y, 0) else None
        w.setze(x, round(12 * s) - 1, 0, schaedel(w, rot=0)) if w.frei(x, round(12 * s) - 1, 0) else None
    pts = [(x, 0) for x in range(-_r(10 * s) - 8, -_r(7 * s))] + [(x, 0) for x in range(_r(7 * s) + 1, _r(10 * s) + 9)]
    palisade(w, O, pts, 5)
    for sx in (-1, 1):
        x = sx * (_r(7 * s) + 1)
        w.setze(x, 1, 2, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                             west="none", waterlogged=False))
        w.setze(x, 2, 2, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    hohl(w, 2)
    return w


def thron(seed, g=1):
    """Häuptlingsthron: ein Thron aus Schwarzstein und Knochen auf einem Podest aus Schädeln, hinter ihm ein
    Fächer aus Speeren und Fahnen, Kohlebecken an den Seiten."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    R = _r(4 * u + 3)
    orkboden(w, R + 5)
    for k in range(3):
        for x in range(-R + k, R - k + 1):
            for z in range(-R + k, R - k + 1):
                w.setze(x, 1 + k, z, O.stein(x, k, z, 0.5) if (x + z + k) % 5 else w.b("bone_block", axis="y"))
    y = 4
    for x in (-1, 0, 1):
        w.setze(x, y, 0, w.b("polished_blackstone_stairs", facing="south", half="bottom", shape="straight",
                             waterlogged=False) if x == 0 else w.b("polished_blackstone_bricks"))
        for yy in range(y, y + 4):
            w.setze(x, yy, -1, w.b("polished_blackstone_bricks") if yy < y + 3 else schaedel(w, rot=0))
    for i in range(7):
        a = math.pi * (0.15 + 0.7 * i / 6)
        for t in range(2, 7 + int(u * 2)):
            w.setze(round(math.cos(a) * t * 0.6), y + round(math.sin(a) * t), -2,
                    w.b("lightning_rod", facing="up", powered=False, waterlogged=False) if t > 5 else
                    w.b(f"{O.holz}_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    for sx in (-1, 1):
        w.setze(sx * (R + 1), 1, 0, MB.kohlenbecken(w))
        fahne(w, O, sx * (R - 1), -R, 1, 8)
    return w


def kampfgrube(seed, g=2):
    """Kampfgrube: eine eingetiefte Arena mit Sandboden, Spießbarrieren, Knochen, Zuschauerrängen aus Stämmen und
    einem Gong."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    R = _r(8 * u + 5)
    orkboden(w, R + 6)
    for x, z in scheibe(R):
        for y in (-2, -1, 0):
            w.bloecke.pop((x, y, z), None)
        w.setze(x, -3, z, w.b("sand") if (x + z) % 4 else w.b("coarse_dirt"))
    for x, z in kreisrand(R + 0.5):
        for y in range(-2, 1):
            w.setze(x, y, z, O.stein(x, y, z, 0.5))
        pfahl(w, O, x, z, 1, 1 + (x + z) % 2) if (x + z) % 2 == 0 else None
    for k in range(3):
        for x, z in kreisrand(R + 2 + k):
            w.setze(x, 1 + k, z, O.log("x" if abs(x) > abs(z) else "z"))
    for i in range(5):
        knochenhaufen(w, int(w.rng.integers(-R + 2, R - 1)), int(w.rng.integers(-R + 2, R - 1)), 3)
    w.setze(0, 1, R + 6, w.b("bell", attachment="floor", facing="north", powered=False))
    return w


def katapult(seed, g=1):
    """Ork-Katapult: grob gezimmertes Wurfgeschütz mit Gegengewicht aus Steinen, Wurfarm mit Schleuder, Rädern und
    einem Stapel Felsbrocken als Munition."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    s = 0.6 * u + 0.4
    orkboden(w, _r(10 * s + 5))
    L = _r(5 * s + 3)
    for x in range(-L, L + 1):
        for z in (-2, 2):
            w.setze(x, 1, z, O.log("x"))
    for z in range(-2, 3):
        for x in (-L, L):
            w.setze(x, 1, z, O.log("z"))
    for sx in (-L, L):
        for sz in (-3, 3):
            w.setze(sx, 1, sz, w.b(f"{O.holz}_trapdoor", facing="north" if sz < 0 else "south", half="bottom",
                                   open=True, powered=False, waterlogged=False))
    H = _r(5 * s + 3)
    for y in range(2, H + 2):
        for z in (-2, 2):
            w.setze(0, y, z, O.log())
    for z in range(-2, 3):
        w.setze(0, H + 2, z, O.log("z"))
    A = _r(8 * s + 4)
    for k in range(A):
        w.setze(-k + 2, H + 2 + k // 2, 0, O.log("x"))
    for dx, dy in ((2, 0), (3, 0), (2, -1), (3, -1), (2, -2), (3, -2)):
        w.setze(dx, H + 2 + dy, 0, w.b("cobblestone"))
    w.setze(-A + 2, H + 2 + A // 2 + 1, 0, O.fell(0, 0, 0, 0.5))
    for k in range(5):
        w.setze(L + 3 + k % 3, 1 + k // 3, 3, w.b("cobblestone") if k % 2 else w.b("andesite"))
    return w


def belagerungsturm(seed, g=2):
    """Belagerungsturm: ein hoher fahrbarer Holzturm mit Fellverkleidung, Fallbrücke oben, großen Scheibenrädern und
    Kriegsfahnen."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    B = _r(2.5 * u + 2)
    H = _r(10 * u + 8)
    orkboden(w, B + 8)
    for y in range(1, H + 1):
        for x in range(-B, B + 1):
            for z in range(-B, B + 1):
                if max(abs(x), abs(z)) == B:
                    w.setze(x, y, z, O.log() if abs(x) == B and abs(z) == B else
                            O.fell(x, y, z, 0.5) if y % 4 else O.log("x" if abs(z) == B else "z"))
    for x in range(-B, B + 1):
        for z in range(-B, B + 1):
            w.setze(x, H + 1, z, w.b(f"{O.holz}_planks"))
            if max(abs(x), abs(z)) == B and (x + z) % 2 == 0:
                pfahl(w, O, x, z, H + 2, 1)
    for x in range(-B + 1, B):
        for k in range(4):
            w.setze(x, H - k, B + 1 + k // 3, w.b(f"{O.holz}_planks")) if k == 0 else None
    for sx in (-B - 1, B + 1):
        for sz in (-B + 1, B - 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if abs(dy) + abs(dz) < 2:
                        w.setze(sx, 2 + dy, sz + dz, w.b(f"{O.holz}_planks") if dy or dz else O.log("x"))
    fahne(w, O, 0, 0, H + 2, 5)
    return w


def schamanenhuette(seed, g=1):
    """Schamanenhütte: runde Hütte aus Lehm und Fellen mit Hörnerdach, Kessel mit grünem Gebräu, Kräuterbündeln,
    Knochenwindspielen und leuchtenden Pilzen."""
    from spuk import hexenkessel
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    R = 2.5 * u + 2
    orkboden(w, _r(R + 6))
    for y in range(1, 4):
        for x, z in kreisrand(R):
            if not (y < 3 and x == 0 and z > 0):
                w.setze(x, y, z, O.stein(x, y, z, 0.5) if y < 3 else O.log())
    zelt_kegel(w, O, 0, 0, R + 1, _r(R * 1.6 + 2), y0=4)
    for sx in (-1, 1):
        for k in range(3):
            w.setze(sx * (round(R) + k), 5 + k, 0, w.b("bone_block", axis="x"))
    hexenkessel(w, round(R) + 3, 2)
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.8
        x, z = round(math.cos(a) * (R + 1.5)), round(math.sin(a) * (R + 1.5))
        w.setze(x, 1, z, w.b("red_mushroom") if k % 2 else w.b("shroomlight"))
    return w


def raeucherei(seed, g=1):
    """Räucherei: Trockengestelle mit Fleisch (rote Wolle), Rauchfeuer darunter, Häute auf Rahmen gespannt und ein
    Vorratszelt."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    n = 2 + g
    orkboden(w, n * 3 + 6)
    for i in range(n):
        x = -n * 3 // 2 + i * 3
        for z in (-2, 2):
            for y in (1, 2, 3):
                w.setze(x, y, z, O.log())
        for z in range(-2, 3):
            w.setze(x, 4, z, O.log("z"))
            if abs(z) < 2:
                w.setze(x, 3, z, w.b("red_wool") if (z + i) % 2 else w.b("brown_wool"))
        w.setze(x, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    langzelt(w, O, -3, 5, 3, 9, 4)
    return w


def wargzwinger(seed, g=1):
    """Wargzwinger: Gehege aus spitzen Pfählen mit Unterständen, Futtertrog mit Knochen, Ketten an Pfosten und ein
    Wachtposten mit Horn."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    a = _r(6 * u + 4)
    orkboden(w, a + 5)
    pts = [(x, -a) for x in range(-a, a + 1)] + [(x, a) for x in range(-a, a + 1)] + \
          [(-a, z) for z in range(-a + 1, a)] + [(a, z) for z in range(-a + 1, a)]
    palisade(w, O, pts, 3, tor=[(0, a), (1, a)])
    for k in range(3):
        x = -a + 2 + k * 4
        for dx in (0, 1, 2):
            for y in (1, 2):
                w.setze(x + dx, y, -a + 1, O.log("x") if y == 2 else w.b("hay_block", axis="y"))
        w.setze(x + 1, 3, -a + 1, O.fell(0, 0, 0, 0.5))
    for x in range(-2, 3):
        w.setze(x, 1, 0, w.b(f"{O.holz}_slab", type="bottom", waterlogged=False))
    knochenhaufen(w, 2, 2, 5)
    for k in range(3):
        w.setze(a - 2, 1 + k, a - 2, O.log())
        w.setze(a - 1, 2 + k, a - 2, w.b("chain", axis="x", waterlogged=False)) if k == 1 else None
    return w


def trophaeenwand(seed, g=1):
    """Trophäenwand: eine Mauer aus Pfählen und Lehm, gespickt mit erbeuteten Schilden (Banner-Farben), Helmen,
    Schädeln und zerbrochenen Waffen."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    L = _r(8 * u + 5)
    orkboden(w, L + 4)
    for x in range(-L, L + 1):
        hh = 4 + (x % 3 == 0) + (x % 5 == 0)
        for y in range(1, hh + 1):
            w.setze(x, y, 0, O.log() if x % 2 == 0 else O.stein(x, y, 0, y / 6))
        w.setze(x, hh + 1, 0, w.b("pointed_dripstone", vertical_direction="up", thickness="tip", waterlogged=False))
        if x % 3 == 1:
            w.setze(x, 3, 1, w.b(["blue_wool", "yellow_wool", "white_wool", "red_wool"][(x // 3) % 4]))
        elif x % 3 == 2:
            w.setze(x, 4, 1, schaedel(w, rot=0))
    for k in range(4):
        w.setze(-L + 2 + k * 4, 1, 2, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                          waterlogged=False))
    return w


def kriegstrommeln(seed, g=1):
    """Kriegstrommeln: eine Holzplattform mit drei riesigen Fasstrommeln mit Fellbespannung, Schlegeln und Fahnen,
    daneben Signalfeuer."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    R = _r(5 * u + 4)
    orkboden(w, R + 5)
    for x, z in scheibe(R):
        w.setze(x, 1, z, w.b(f"{O.holz}_planks"))
    for i, (cx, cz, rr) in enumerate(((0, 0, 1.6 * u + 1.2), (-round(R * 0.5), 2, 1.2 * u + 0.8),
                                      (round(R * 0.5), 2, 1.2 * u + 0.8))):
        hh = _r(rr * 1.8)
        for y in range(2, 2 + hh):
            for x, z in kreisrand(rr, cx, cz):
                w.setze(x, y, z, O.log() if (x + z) % 3 == 0 else w.b(f"stripped_{O.holz}_log", axis="y")
                        if y % 3 else w.b("red_wool" if O.farbe[0] == "red_wool" else "green_wool"))
        for x, z in scheibe(rr, cx, cz):
            w.setze(x, 2 + hh, z, w.b("brown_wool") if (x + z) % 2 else w.b("white_terracotta"))
    for sx in (-1, 1):
        fahne(w, O, sx * (R - 1), -R + 1, 2, 7)
    feuerstelle(w, 0, R + 3, True)
    return w


def seilbruecke(seed, g=2):
    """Ork-Seilbrücke: eine schwankende Hängebrücke aus Brettern und Ketten über eine Felsschlucht, an beiden Enden
    Spießtore und Wachfeuer."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    L = _r(12 * u + 6)
    H = _r(8 * u + 5)
    fels = Mat(w, ["stone", "andesite", "tuff", "cobblestone", "dirt"], kontrast=1.2)
    for x in range(-L - 6, L + 7):
        for z in range(-8, 9):
            if abs(x) > L:
                for y in range(-2, H + 1):
                    w.setze(x, y, z, fels(x, y, z, y / H))
                w.setze(x, H + 1, z, w.b("coarse_dirt") if (x + z) % 3 else w.b("grass_block", snowy=False))
            else:
                w.setze(x, -3, z, w.b("water", level=0) if abs(z) < 4 else fels(x, -3, z, 0))
    for x in range(-L, L + 1):
        y = H + 1 - round((1 - (x / L) ** 2) * 2.5)
        for z in (-1, 0, 1):
            if (x + z) % 7:
                w.setze(x, y, z, w.b(f"{O.holz}_slab", type="bottom", waterlogged=False))
        for z in (-2, 2):
            w.setze(x, y + 1, z, w.b("chain", axis="x", waterlogged=False))
    for sx in (-1, 1):
        x = sx * (L + 2)
        for z in (-2, 2):
            pfahl(w, O, x, z, H + 2, 4)
        w.setze(x + sx * 2, H + 2, 3, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


def signalfeuer(seed, g=1):
    """Signalfeuerturm: ein Gerüst aus Stämmen mit einer Feuerschale aus Eisen und Schwarzstein an der Spitze,
    Holzvorrat und Horn am Fuß."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    H = _r(9 * u + 5)
    orkboden(w, _r(5 * u + 4))
    for y in range(1, H + 1):
        r = 2.2 - y / H * 1.2
        for a in range(4):
            ang = a / 4 * 2 * math.pi + math.pi / 4
            w.setze(round(math.cos(ang) * r * 1.4), y, round(math.sin(ang) * r * 1.4), O.log())
    for x, z in scheibe(1.8):
        w.setze(x, H + 1, z, w.b("polished_blackstone_bricks"))
        w.setze(x, H + 2, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False)
                if abs(x) + abs(z) < 2 else w.b("iron_bars", north=True, south=True, east=True, west=True,
                                                waterlogged=False))
    for k in range(3):
        w.setze(3, 1, -1 + k, O.log("z"))
        w.setze(3, 2, -1 + k, O.log("z")) if k < 2 else None
    return w


def knochenhuette(seed, g=1):
    """Knochenhütte: eine Kuppelhütte aus riesigen gebogenen Rippen und Stoßzähnen, mit Fellen bespannt, ein
    Schädel über dem Eingang und ein Feuerplatz davor."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    R = 3 * u + 2.5
    orkboden(w, _r(R + 6))
    for y in range(1, _r(R) + 2):
        r = R * math.sqrt(max(0, 1 - ((y - 1) / (R + 0.5)) ** 2))
        for x, z in kreisrand(max(0.5, r)):
            a = math.atan2(z, x)
            rippe = abs(math.sin(a * 4)) < 0.3
            if not (y < 3 and x == 0 and z > 0):
                w.setze(x, y, z, w.b("bone_block", axis="y") if rippe else O.fell(x, y, z, 0.5))
    w.setze(0, 4, round(R) + 1, schaedel(w, rot=0))
    for sx in (-1, 1):
        for k in range(4):
            w.setze(sx * (2 + k // 2), 1 + k, round(R) + 1, w.b("bone_block", axis="y"))
    feuerstelle(w, 0, round(R) + 4)
    return w


def palisadenring(seed, g=2):
    """Palisadenring: kreisrunde Wehr aus angespitzten Stämmen mit Wehrgang, zwei Torburgen, Ecktürmchen und
    Spießgraben davor."""
    w = _welt(seed)
    O = Ork(w, seed)
    u = U[g]
    R = _r(10 * u + 6)
    orkboden(w, R + 6)
    pts = kreisrand(R)
    tor = {(x, z) for (x, z) in pts if abs(x) <= 1 and z > 0}
    palisade(w, O, pts, 5, tor=tor)
    for x, z in kreisrand(R - 1):
        w.setze(x, 3, z, w.b(f"{O.holz}_planks"))
    for sx in (-2, 2):
        for y in range(1, 9):
            w.setze(sx, y, R, O.log())
    for x in range(-2, 3):
        w.setze(x, 8, R, O.log("x"))
        w.setze(x, 9, R, O.fell(0, 0, 0, 0.5))
    for x, z in kreisrand(R + 3):
        if (x + z) % 2 == 0 and not (abs(x) < 4 and z > 0):
            w.setze(x, 1, z, w.b("pointed_dripstone", vertical_direction="up", thickness="tip", waterlogged=False))
    return w


def kriegslager(seed, g=2):
    """Kriegslager (komplett): Palisadenring mit Knochentor, Häuptlingszelt, Kriegszelte, Schmiede, Totem,
    Kampfgrube, Feuerstellen und Fahnen."""
    w = palisadenring(seed, g)
    O = Ork(w, seed)
    u = U[g]
    R = _r(10 * u + 6)
    rng = w.rng
    zelt_kegel(w, O, 0, -round(R * 0.4), 2.5 * u + 2, _r(5 * u + 4))
    for i in range(3 + g):
        a = i / (3 + g) * 2 * math.pi + 0.3
        x, z = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        if z > R * 0.3 and abs(x) < 4:
            continue
        zelt_kegel(w, O, x, z, 1.5 * u + 1.2, _r(3 * u + 3))
    feuerstelle(w, 0, round(R * 0.2), True)
    for k in range(3):
        fahne(w, O, round(math.cos(k * 2.1) * R * 0.35), round(math.sin(k * 2.1) * R * 0.35), 1, 6)
    for k in range(6):
        knochenhaufen(w, int(rng.integers(-R // 2, R // 2)), int(rng.integers(-R // 2, R // 2)), 3)
    return w


ORKLAGER2 = {
    "kriegslager": ("Kriegslager (komplett)", kriegslager),
    "kriegszelt": ("Kriegszelt", kriegszelt),
    "haeuptlingshalle": ("Häuptlingshalle", haeuptlingshalle),
    "wachturm": ("Ork-Wachturm", wachturm),
    "totempfahl": ("Totempfahl", totempfahl),
    "orkschmiede": ("Orkschmiede", orkschmiede),
    "knochentor": ("Knochentor", knochentor),
    "thron": ("Häuptlingsthron", thron),
    "kampfgrube": ("Kampfgrube", kampfgrube),
    "katapult": ("Katapult", katapult),
    "belagerungsturm": ("Belagerungsturm", belagerungsturm),
    "schamanenhuette": ("Schamanenhütte", schamanenhuette),
    "raeucherei": ("Räucherei", raeucherei),
    "wargzwinger": ("Wargzwinger", wargzwinger),
    "trophaeenwand": ("Trophäenwand", trophaeenwand),
    "kriegstrommeln": ("Kriegstrommeln", kriegstrommeln),
    "seilbruecke": ("Seilbrücke", seilbruecke),
    "signalfeuer": ("Signalfeuer", signalfeuer),
    "knochenhuette": ("Knochenhütte", knochenhuette),
    "palisadenring": ("Palisadenring", palisadenring),
}

"""Zwergenreich – 20 Bauten: Bergtore, Schmiedehallen, Minen, Brauhaus, Ahnenhalle, Runensteine, Hügelhäuser."""

from __future__ import annotations

import math

import numpy as np

import modbloecke as MB
import pracht as P
from drachen import felsen, gold_haufen
from lib import Rauschen, laub
from pracht import Mat, gelaende
from skulptur import Skulptur, dreh_y, ell, kap, kreisrand, scheibe
from weltwunder import bl, hohl, platz, sk

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


class Zwerg:
    """Stil 0: Granit & Kupfer. Stil 1: Tiefenschiefer & Gold."""

    def __init__(self, w, seed):
        self.w = w
        self.granit = _stil(seed) == 0
        if self.granit:
            self.fels = Mat(w, ["stone", "andesite", "granite", "tuff", "stone", "diorite"], kontrast=1.3)
            self.bau = Mat(w, ["polished_granite", "granite", "stone_bricks", "polished_andesite"], kontrast=0.7)
            self.fein = Mat(w, ["polished_andesite", "smooth_stone", "stone_bricks"], kontrast=0.5)
            self.gold = "waxed_cut_copper"
            self.gold2 = "waxed_copper_block"
            self.rune = "waxed_oxidized_cut_copper"
            self.dach = "mcw_stein"
            self.wand = "graustein"
            self.gesims = "stone_brick"
            self.licht = "lantern"
        else:
            self.fels = Mat(w, ["deepslate", "cobbled_deepslate", "tuff", "blackstone", "smooth_basalt"], kontrast=1.3)
            self.bau = Mat(w, ["polished_deepslate", "deepslate_bricks", "deepslate_tiles", "polished_blackstone_bricks"],
                           kontrast=0.7)
            self.fein = Mat(w, ["polished_deepslate", "deepslate_tiles", "polished_blackstone"], kontrast=0.5)
            self.gold = "gold_block"
            self.gold2 = "raw_gold_block"
            self.rune = "gilded_blackstone"
            self.dach = "schiefer"
            self.wand = "tiefenschiefer"
            self.gesims = "deepslate_brick"
            self.licht = "lantern"
        self.holz = "dark_oak" if not self.granit else "spruce"

    def stil(self, **extra):
        d = dict(wand=self.wand, sockel=self.wand, gesims=self.gesims, dach=self.dach, holz=self.holz, laeden=False,
                 blumen=0, licht="lantern")
        d.update(extra)
        return P.Stil(self.w, **d)


def bergwand(w, z, W, H, Z, D=None, cx=0):
    """Felswand (nach Süden offen) mit Rauschen; Hinterland bis z - D."""
    D = D or W * 0.8
    r_n = Rauschen(w, 5)
    hoehe = {}
    for x in range(cx - _r(W), cx + _r(W) + 1):
        for zz in range(z - _r(D), z + 1):
            tx = abs(x - cx) / W
            hh = H * (1 - tx ** 2) * (0.75 + 0.35 * r_n(x, 0, zz)) * min(1, (z - zz + 3) / 4)
            for y in range(0, int(hh) + 1):
                w.setze(x, y, zz, Z.fels(x, y, zz, y / H))
            if hh > 2:
                w.setze(x, int(hh) + 1, zz, w.b("snow_block") if hh > H * 0.85 else w.b("grass_block", snowy=False)
                        if Z.granit else w.b("tuff"))
            hoehe[(x, zz)] = int(hh)
    return hoehe


def zwergenstatue(w, Z, x, y, z, s, pose="stab", dreh=0.0, spiegel=False):
    from motive import figur
    S = Skulptur(w, s)
    S.mat("k", sk(Z.fein, y, y + 22 * s))
    S.mat("a", bl(w, Z.gold))
    S.mat("d", bl(w, Z.gold2))
    S.mat("g", bl(w, "shroomlight"))
    figur(S, "zwerg", pose)
    R = dreh_y(dreh)
    if spiegel:
        R = R @ np.diag([-1, 1, 1])
    S.rendern((-7, -1, -5), (7, 22, 7), versatz=(x + 0.5, y + 0.01, z + 0.5), dreh=R)


def runenband(w, Z, x0, x1, y, z):
    for x in range(x0, x1 + 1):
        w.setze(x, y, z, w.b(Z.gold) if x % 3 else w.b(Z.rune))


def portal(w, Z, cx, z, B, H, tiefe=4):
    """Kantiges Zwergenportal: gestufter Rahmen, Sturz mit Runenband, Kupfer-/Goldtor."""
    for k in range(3):
        for x in range(cx - B - 2 + k, cx + B + 3 - k):
            for y in range(0, H + 3 - k):
                if abs(x - cx) > B - k + 0 or y > H - k:
                    w.setze(x, y, z + k, Z.bau(x, y, z + k, 0.5 + k * 0.1))
    for x in range(cx - B, cx + B + 1):
        for y in range(1, H + 1):
            for zz in range(z - tiefe, z + 3):
                w.bloecke.pop((x, y, zz), None)
            w.setze(x, y, z - tiefe, w.b(Z.gold) if (x + y) % 4 == 0 else Z.fein(x, y, z, 0.8))
    runenband(w, Z, cx - B - 1, cx + B + 1, H + 1, z + 2)


# ============================================================================ Bauten


def bergtor(seed, g=2):
    """Bergtor: ein gewaltiges kantiges Tor in einer Felswand, gestufter Rahmen mit Runenband, flankiert von zwei
    Zwergenstatuen mit Äxten, Feuerbecken und Prunktreppe."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    W, H = 18 * u + 8, 16 * u + 8
    bergwand(w, 0, W, H, Z)
    gelaende(w, _r(W), art="wiese" if Z.granit else "asche", dichte=0.2)
    B = _r(3 * u + 2)
    Ht = _r(7 * u + 4)
    portal(w, Z, 0, 0, B, Ht)
    for sx in (-1, 1):
        x = sx * (B + _r(5 * u + 2))
        for y in range(0, 3):
            for xx, zz in scheibe(2 * u + 1, x, 3):
                w.setze(xx, y, zz, Z.bau(xx, y, zz, 0.4))
        zwergenstatue(w, Z, x, 3, 3, 0.45 * u + 0.15, pose="schwert", spiegel=sx > 0)
        w.setze(sx * (B + 2), 1, 5, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for k in range(4):
        for x in range(-B - 1, B + 2):
            w.setze(x, k, 4 + 4 - k, Z.bau(x, k, 4, 0.3))
    hohl(w, 3)
    return w


def schmiedehalle(seed, g=2):
    """Große Schmiedehalle: wuchtige Halle mit Lava-Rinnen, Essen aus Schwarzstein, Ambossreihen, Wassertrögen,
    hohen Schornsteinen und einem Riesenhammer über dem Eingang."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    a, b = _r(8 * u + 4), _r(5 * u + 3)
    gelaende(w, a + 6, art="asche" if not Z.granit else "wiese", dichte=0.2)
    st = Z.stil()
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=_r(6 * u + 3), dach="walm", tuer="south", gauben=False,
               kamine=0)
    for sx in (-1, 1):
        x = sx * (a - 3)
        for y in range(1, _r(16 * u + 8)):
            for xx, zz in kreisrand(1.5, x, -b - 2):
                w.setze(xx, y, zz, w.b("polished_blackstone_bricks") if y % 5 else w.b(Z.gold))
        w.setze(x, _r(16 * u + 8), -b - 2, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                waterlogged=False))
    for x in range(-a + 2, a - 1):
        w.setze(x, 0, 0, w.b("lava", level=0) if x % 3 else w.b("magma_block"))
    for x in range(-a + 2, a - 1, 3):
        w.setze(x, 1, 2, w.b("anvil", facing="east"))
        w.setze(x, 1, -2, w.b("water_cauldron", level=3) if x % 2 else w.b("blast_furnace", facing="south", lit=True))
    S = Skulptur(w, 0.5 * u + 0.2)
    S.mat("m", bl(w, "iron_block"))
    S.mat("h", bl(w, "dark_oak_log"))
    S.plus(lambda X, Y, Z_: (np.abs(X) < 3) & (np.abs(Y) < 1.5) & (np.abs(Z_) < 1.5), "m")
    S.plus(kap((0, 0, 0), (0, -8, 0), 0.6, 0.6), "h")
    hy = _r(6 * u + 3) + 6
    S.rendern((-4, -9, -2), (4, 2, 2), versatz=(0.5, hy + 4 * u, b + 2.5), dreh=dreh_y(0.0))
    hohl(w, 2)
    return w


def bergfestung(seed, g=2):
    """Bergfestung: Festung auf einem Felssporn, wuchtige Mauern mit Rundtürmen und Schieferdächern, ein Bergfried,
    Serpentinenweg und Runenfahnen."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    R = 12 * u + 6
    H = 6 * u + 4
    hoehe = felsen(w, R, H, mat=Z.fels, spitz=0.9, rauh=0.15)
    top = int(H) + 1
    a = _r(R * 0.45)
    st = Z.stil()
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            w.setze(x, top, z, Z.fein(x, top, z, 0.5))
            if max(abs(x), abs(z)) == a:
                for y in range(top + 1, top + 5 + g):
                    w.setze(x, y, z, Z.bau(x, y, z, y / 10))
                if (x + z) % 2 == 0:
                    w.setze(x, top + 5 + g, z, Z.bau(x, top + 5 + g, z, 0.9))
    for sx in (-1, 1):
        for sz in (-1, 1):
            P.turm(w, st, sx * a, sz * a, top, _r(8 * u + 5), max(2.0, 1.8 * u), dach="kegel", krone=True,
                   fahne="orange" if Z.granit else "yellow")
    P.gebaeude(w, st, -a // 2, -a // 2, a // 2, a // 2, y0=top + 1, etagen=2 + (g >= 2), eh=5, dach="walm",
               tuer="south", gauben=False, kamine=1)
    for i in range(int(R * 3)):
        t = i / (R * 3)
        aa = t * 2.5 * math.pi
        rr = R * (0.95 - 0.4 * t)
        x, z = round(math.cos(aa) * rr), round(math.sin(aa) * rr)
        y = hoehe.get((x, z), 0)
        if y > 0:
            w.setze(x, y, z, w.b("gravel") if i % 3 else Z.fein(x, y, z, 0.3))
    hohl(w, 3)
    return w


def mineneingang(seed, g=1):
    """Mineneingang: Stollenmund mit Holzverschalung im Hang, Schienen mit Loren voller Erz, Laternen, Seilwinde,
    Abraumhalde und Werkzeughütte."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    W, H = 12 * u + 6, 9 * u + 5
    bergwand(w, 0, W, H, Z)
    gelaende(w, _r(W), art="wiese", dichte=0.2)
    B, Ht = 2, 4
    for x in range(-B, B + 1):
        for y in range(1, Ht + 1):
            for z in range(-_r(W * 0.6), 1):
                w.bloecke.pop((x, y, z), None)
    for z in range(-_r(W * 0.6), 3, 3):
        for sx in (-B - 1, B + 1):
            for y in range(1, Ht + 1):
                w.setze(sx, y, z, w.b(f"{Z.holz}_log", axis="y"))
        for x in range(-B - 1, B + 2):
            w.setze(x, Ht + 1, z, w.b(f"{Z.holz}_log", axis="x"))
        w.setze(0, Ht, z, w.b("lantern", hanging=True, waterlogged=False))
    for z in range(-_r(W * 0.6), _r(W * 0.6)):
        w.setze(0, 1, z, w.b("rail", shape="north_south", waterlogged=False))
    for z in (2, 5):
        w.setze(0, 2, z, w.b("raw_iron_block") if z == 2 else w.b("coal_block"))
    for x, z in scheibe(4 * u + 2, round(W * 0.5), 4):
        hh = int((1 - math.hypot(x - round(W * 0.5), z - 4) / (4 * u + 2)) * (2 * u + 1))
        for y in range(1, hh + 1):
            w.setze(x, y, z, w.b(["gravel", "cobblestone", "andesite", "iron_ore"][(x + y * 3 + z) % 4]))
    st = Z.stil(wand="holz_dunkel")
    P.gebaeude(w, st, -round(W * 0.6), 3, -round(W * 0.6) + 5, 8, y0=1, etagen=1, eh=3, dach="sattel",
               tuer="east", gauben=False, kamine=1)
    hohl(w, 3)
    return w


def thronhalle(seed, g=2):
    """Thronhalle der Bergkönige: offene Säulenhalle mit massiven Vierkantsäulen, goldenen Kapitellen, einem
    Thron auf Stufen, Feuerschalen und Banner, halb in den Fels gebaut."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    a, b = _r(6 * u + 4), _r(10 * u + 5)
    W, H = a + 8, 10 * u + 8
    bergwand(w, -b, W, H, Z, D=8)
    Hs = _r(7 * u + 5)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.setze(x, 0, z, Z.fein(x, 0, z, 0.3) if (x + z) % 2 else w.b(Z.gold) if x == 0 else Z.bau(x, 0, z, 0.2))
    for z in range(-b + 2, b, 4):
        for sx in (-a, a):
            for y in range(1, Hs + 1):
                for dx in (0, 1 if sx < 0 else -1):
                    for dz in (0, 1):
                        w.setze(sx + dx, y, z + dz, w.b(Z.gold) if y in (Hs, Hs - 1) else Z.bau(sx, y, z, y / Hs))
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            if abs(x) >= a - 1:
                w.setze(x, Hs + 1, z, Z.bau(x, Hs + 1, z, 0.9))
        for z in range(-b, b + 1, 4):
            w.setze(x, Hs + 1, z, Z.bau(x, Hs + 1, z, 0.9))
    for k in range(3):
        for x in range(-2 - k, 3 + k):
            w.setze(x, 1 + (2 - k), -b + 1 + k, Z.fein(x, 1, -b, 0.6))
    w.setze(0, 4, -b + 1, w.b(Z.gold))
    w.setze(0, 5, -b + 1, w.b(Z.gold))
    for sx in (-1, 1):
        w.setze(sx, 4, -b + 1, w.b(Z.gold2))
    for z in range(-b + 4, b, 6):
        for sx in (-1, 1):
            w.setze(sx * (a - 3), 1, z, w.b("polished_blackstone_wall", up=True, north="none", south="none",
                                            east="none", west="none", waterlogged=False))
            w.setze(sx * (a - 3), 2, z, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                            waterlogged=False))
    hohl(w, 3)
    return w


def brauhaus(seed, g=1):
    """Zwergen-Brauhaus: wuchtiges Steinhaus mit Kupferkesseln, riesigen liegenden Fässern als Anbau, Bierbänken
    und einem Schild mit Krug."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    a, b = _r(5 * u + 3, 4), _r(4 * u + 2, 3)
    gelaende(w, a + 9, art="wiese", dichte=0.2)
    st = Z.stil()
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="walm", tuer="south", kamine=2, gauben=False)
    for i in range(2):
        cz = -b + 2 + i * (2 * b - 4) // 1 if b > 2 else 0
        cz = -2 + i * 4
        Rf = 1.8 + u * 0.6
        for x in range(a + 1, a + 1 + _r(4 * u + 3)):
            for y in range(-round(Rf), round(Rf) + 1):
                for z in range(-round(Rf), round(Rf) + 1):
                    r = math.hypot(y, z)
                    if Rf - 1 < r <= Rf:
                        w.setze(x, round(Rf) + 1 + y, cz * 1 + z, w.b("stripped_dark_oak_log", axis="x") if
                                (x - a) % 3 == 0 else w.b(f"{Z.holz}_planks"))
                    elif r <= Rf - 1 and x in (a + 1, a + _r(4 * u + 3)):
                        w.setze(x, round(Rf) + 1 + y, cz + z, w.b(f"{Z.holz}_planks"))
    for k in range(2):
        for xx, zz in kreisrand(1.4, -a - 3, -2 + k * 4):
            for y in range(1, 4):
                w.setze(xx, y, zz, w.b("waxed_copper_block") if y < 3 else w.b("waxed_cut_copper"))
    for z in range(b + 2, b + 6, 3):
        for x in range(-a + 1, a, 1):
            w.setze(x, 1, z, w.b(f"{Z.holz}_planks") if x % 4 else w.b(f"{Z.holz}_fence", north=False, south=False,
                                                                         east=False, west=False, waterlogged=False))
    hohl(w, 2)
    return w


def kluftbruecke(seed, g=2):
    """Kluftbrücke: eine schmale Steinbrücke ohne Geländer über eine tiefe Kluft mit Lavastrom, an den Enden
    Wachstatuen und Portaltürme."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    L = _r(14 * u + 6)
    B = 8 * u + 4
    for x in range(-L - 6, L + 7):
        for z in range(-_r(B), _r(B) + 1):
            if abs(x) > L * 0.8:
                for y in range(-10, 1):
                    w.setze(x, y, z, Z.fels(x, y, z, (y + 10) / 11))
            else:
                w.setze(x, -10, z, w.b("lava", level=0) if abs(z) < B * 0.5 else w.b("magma_block"))
                for y in range(-10, -7):
                    if abs(z) > B * 0.8:
                        w.setze(x, y, z, Z.fels(x, y, z, 0.2))
    for x in range(-L, L + 1):
        bog = -1 - (1 - (x / L) ** 2) * 0 if abs(x) > L * 0.8 else -2
        for z in (-1, 0, 1):
            w.setze(x, 0, z, Z.fein(x, 0, z, 0.5))
            w.setze(x, -1, z, Z.bau(x, -1, z, 0.4))
        if abs(x) < L * 0.8:
            d = round((1 - (x / (L * 0.8)) ** 2) * 2.5)
            for y in range(-2 - d, -1):
                w.setze(x, y, 0, Z.bau(x, y, 0, 0.4))
    for sx in (-1, 1):
        x = sx * (L + 2)
        P.turm(w, Z.stil(), x, 4, 1, _r(8 * u + 4), 2.0, form="eckig", dach="pyramide", krone=True, fahne=None)
        zwergenstatue(w, Z, x, 1, -4, 0.3 * u + 0.1, pose="stab", dreh=math.pi / 2 * -sx)
    hohl(w, 3)
    return w


def wachturm(seed, g=1):
    """Zwergen-Wachturm: gedrungener, sich verjüngender Steinturm mit Kragsteinen, schwerer Zinnenkrone, Kupfer-
    oder Goldbändern, Alarmhorn und Signalfeuer."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    R = 3 * u + 2.5
    H = _r(12 * u + 6)
    gelaende(w, _r(R + 6), art="wiese", dichte=0.2)
    for y in range(1, H + 1):
        r = R * (1 - 0.2 * y / H)
        for x, z in kreisrand(r):
            fen = y % 5 == 3 and (abs(x) < 0.6 or abs(z) < 0.6)
            w.setze(x, y, z, w.b("iron_bars", north=True, south=True, east=True, west=True, waterlogged=False)
                    if fen else w.b(Z.gold) if y % 8 == 0 else Z.bau(x, y, z, y / H))
    for x, z in kreisrand(R * 0.8 + 1.2):
        w.setze(x, H + 1, z, Z.bau(x, H + 1, z, 0.9))
        if (x + z) % 2 == 0:
            w.setze(x, H + 2, z, Z.bau(x, H + 2, z, 0.9))
    for x, z in scheibe(R * 0.8 + 0.5):
        w.setze(x, H + 1, z, Z.fein(x, H + 1, z, 0.6))
    w.setze(0, H + 2, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    S = Skulptur(w, 0.4 + 0.15 * g)
    S.mat("h", bl(w, "bone_block"))
    S.mat("g", bl(w, Z.gold))
    S.plus(lambda X, Y, Z_: (np.abs(np.sqrt(X * X + (Y - 3) ** 2) - 3) < 0.6 + X * 0.08) & (X > -1) & (np.abs(Z_) <
                                                                                               0.5 + X * 0.08), "h")
    S.plus(lambda X, Y, Z_: (np.abs(X - 3.5) < 0.6) & (np.abs(Y - 6) < 0.7) & (np.abs(Z_) < 0.9), "g")
    S.rendern((-2, -1, -2), (5, 8, 2), versatz=(round(R) + 1.5, H - 3, 0.5))
    hohl(w, 2)
    return w


def runenstein(seed, g=1):
    """Großer Runenstein: ein mächtiger, behauener Monolith mit eingelegten Goldrunen in Bändern, auf einer
    Stufenplattform, umringt von kleineren Steinen und Kohlebecken."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    gelaende(w, _r(8 * u + 6), art="wiese", dichte=0.3)
    for k in range(2):
        for x in range(-4 - k * 0, 5):
            for z in range(-4 + k, 5 - k):
                w.setze(x - (0), 1 + k, z, Z.fein(x, 1 + k, z, 0.4)) if abs(x) <= 4 - k else None
    H = _r(10 * u + 6)
    B = _r(1.5 * u + 1)
    for y in range(3, 3 + H):
        bb = B if y < 3 + H - 2 else B - 1
        for x in range(-bb, bb + 1):
            for z in (-1, 0, 1):
                rune = z == 1 and (y + x * 2) % 3 == 0 and abs(x) < bb and y % 4 != 0
                w.setze(x, y, z, w.b(Z.gold) if rune else w.b(Z.rune) if y % 4 == 0 else Z.fein(x, y, z, y / H))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * (6 + u * 2)), round(math.sin(a) * (6 + u * 2))
        for y in range(1, 3 + (i % 2)):
            w.setze(x, y, z, Z.fels(x, y, z, 0.5))
        if i % 3 == 0:
            w.setze(x, 3 + (i % 2), z, MB.kohlenbecken(w))
    return w


def erzlager(seed, g=2):
    """Erzlager: Hof mit gemauerten Erzbunkern voller Eisen-, Kupfer- und Golderz, Lorenschienen, ein Holzkran mit
    Kette, Schmelzofen und Waage."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, _r(R + 3), art="wiese", dichte=0.1)
    erze = [("raw_iron_block", "iron_ore"), ("raw_copper_block", "copper_ore"), ("raw_gold_block", "gold_ore"),
            ("coal_block", "coal_ore")]
    for i, (roh, erz) in enumerate(erze[:2 + g]):
        x0 = -R // 2 + i * _r(5 * u + 2)
        for x in range(x0, x0 + 4):
            for z in range(-3, 2):
                rand = x in (x0, x0 + 3) or z in (-3, 1)
                for y in range(1, 3):
                    if rand:
                        w.setze(x, y, z, Z.bau(x, y, z, 0.4))
                if not rand:
                    for y in range(1, 3 + (x + z) % 2):
                        w.setze(x, y, z, w.b(roh) if (x + y + z) % 3 else w.b(erz))
    for x in range(-R // 2 - 2, R // 2 + 3):
        w.setze(x, 1, 4, w.b("rail", shape="east_west", waterlogged=False))
    H = _r(8 * u + 5)
    for y in range(1, H):
        w.setze(R // 2 + 3, y, 0, w.b(f"{Z.holz}_log", axis="y"))
    for x in range(R // 2 - 3, R // 2 + 4):
        w.setze(x, H, 0, w.b(f"{Z.holz}_log", axis="x"))
    for y in range(H - 4, H):
        w.setze(R // 2 - 3, y, 0, w.b("chain", axis="y", waterlogged=False))
    w.setze(-R // 2 - 3, 1, -2, w.b("blast_furnace", facing="east", lit=True))
    hohl(w, 2)
    return w


def huegelhaus(seed, g=1):
    """Zwergen-Hügelhaus: ein in einen grasbewachsenen Hügel gebautes Haus mit runder Steintür, gemauerter Front,
    rauchendem Schornstein, Fenstern mit Läden und Vorgarten."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    R = 6 * u + 4
    gelaende(w, _r(R + 5), art="wiese", dichte=0.5)
    r_n = Rauschen(w, 3)
    for x, z in scheibe(R):
        d = math.hypot(x, z * 1.2) / R
        hh = int((1 - d * d) * (3.5 * u + 3) * (0.9 + 0.2 * r_n(x, 0, z)))
        for y in range(1, hh + 1):
            w.setze(x, y, z, w.b("grass_block", snowy=False) if y == hh else w.b("dirt"))
    zf = round(R * 0.65)
    Hd = _r(2 * u + 3, 4)
    for x in range(-_r(R * 0.6), _r(R * 0.6) + 1):
        for y in range(1, Hd + 2):
            for z in range(zf - 3, zf + 3):
                w.bloecke.pop((x, y, z), None)
            w.setze(x, y, zf - 2, Z.bau(x, y, zf, y / 6))
    rt = 1.6
    for x in range(-2, 3):
        for y in range(1, 5):
            if (x / 2.2) ** 2 + ((y - 1.5) / 2.6) ** 2 < 1:
                w.setze(x, y, zf - 2, w.b(Z.gold) if (x, y) == (0, 2) else w.b(f"{Z.holz}_planks"))
    for sx in (-1, 1):
        x = sx * (_r(R * 0.6) - 2)
        w.setze(x, 2, zf - 2, w.b("glass_pane", north=False, south=False, east=True, west=True, waterlogged=False))
        w.setze(x - sx, 2, zf - 2, MB.fensterladen(w, Z.holz, "south") if False else Z.bau(x, 2, zf, 0.5))
    ytop = max(y for (x, y, z) in w.bloecke if abs(x - 2) < 1 and abs(z) < 1)
    for y in range(ytop, ytop + 3):
        w.setze(2, y, 0, w.b("cobblestone"))
    w.setze(2, ytop + 3, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    H_ = __import__("haeuser")
    H_.beet(w, -4, zf + 2, -1, zf + 4, "blumen")
    H_.beet(w, 1, zf + 2, 4, zf + 4, "gemuese")
    return w


def ahnenhalle(seed, g=2):
    """Halle der Ahnen: eine Allee aus Zwergenkönigen mit gekreuzten Äxten, Bärten aus Gold, die zu einem Grabmal
    führt; Kohlebecken zwischen den Statuen."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    n = 2 + g
    L = n * 7
    gelaende(w, L + 6, art="wiese" if Z.granit else "asche", dichte=0.2)
    for z in range(-L, L + 1):
        for x in range(-3, 4):
            w.setze(x, 0, z, Z.fein(x, 0, z, 0.3) if abs(x) < 3 else w.b(Z.gold) if z % 3 == 0 else
                    Z.bau(x, 0, z, 0.3))
    s = 0.3 * u + 0.15
    for i in range(n):
        z = -L + 4 + i * 14 // 1 if False else -L + 4 + i * (2 * L - 8) // max(1, n - 1)
        for sx in (-1, 1):
            x = sx * 7
            for y in (1, 2):
                for xx, zz in scheibe(2 * s * 5 + 1, x, z):
                    w.setze(xx, y, zz, Z.bau(xx, y, zz, 0.3))
            zwergenstatue(w, Z, x, 3, z, s, pose=["stab", "schwert"][i % 2], dreh=math.pi / 2 * sx)
            w.setze(sx * 4, 1, z + 3, MB.kohlenbecken(w))
    a = 4
    st = Z.stil()
    P.gebaeude(w, st, -a, L + 1, a, L + 2 * a + 1, y0=1, etagen=1, eh=5, dach="walm", tuer="north", gauben=False,
               kamine=0)
    hohl(w, 2)
    return w


def lavaschmelze(seed, g=2):
    """Lavaschmelze: aus einer Felswand stürzt ein Lavafall in eine Gießrinne, Gießpfannen aus Schwarzstein,
    Kühlbecken mit Wasser, Goldbarren-Stapel und eine Arbeitsplattform."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    W, H = 10 * u + 5, 12 * u + 6
    hoehe = bergwand(w, -3, W, H, Z, D=6)
    gelaende(w, _r(W), art="asche", dichte=0.3)
    ytop = max([hoehe.get((0, z), 0) for z in range(-6, -2)] + [3])
    for y in range(1, ytop + 1):
        w.setze(0, y, -3, w.b("lava", level=0 if y == ytop else 8))
        w.setze(0, y, -4, w.b("magma_block"))
    for z in range(-2, _r(W * 0.6)):
        for x in (-1, 0, 1):
            w.setze(x, 0, z, w.b("polished_blackstone_bricks") if x else w.b("lava", level=0))
    for k in range(3):
        x = 3 + k * 3
        for xx, zz in kreisrand(1.2, x, 4):
            w.setze(xx, 1, zz, w.b("polished_blackstone_bricks"))
        w.setze(x, 1, 4, w.b("lava_cauldron") if k % 2 == 0 else w.b("water_cauldron", level=3))
    gold_haufen(w, -5, 5, 2 + u, 1.5 + u * 0.5)
    hohl(w, 3)
    return w


def schatzkammer(seed, g=2):
    """Edelsteinkammer: ein sechseckiger Gewölbesaal mit Säulen aus Gold und Stein, Nischen voller Edelsteinblöcke,
    Amethyst-Drusen, Truhen und ein Smaragdthron; das Dach offen wie eine Kuppel aus Rippen."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    R = 7 * u + 4
    gelaende(w, _r(R + 3), art="wiese" if Z.granit else "asche", dichte=0.1)
    H = _r(5 * u + 4)
    for x, z in scheibe(R):
        w.setze(x, 0, z, Z.fein(x, 0, z, 0.3) if (x + z) % 3 else w.b(Z.gold))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        for y in range(1, H + 1):
            for dx in (0, 1):
                w.setze(x + dx, y, z, w.b(Z.gold) if y in (1, H) else Z.bau(x, y, z, y / H))
        a2 = (i + 0.5) / 6 * 2 * math.pi
        nx, nz = round(math.cos(a2) * (R - 1)), round(math.sin(a2) * (R - 1))
        edel = ["emerald_block", "diamond_block", "lapis_block", "redstone_block", "amethyst_block", "gold_block"][i]
        for y in (1, 2):
            w.setze(nx, y, nz, w.b(edel))
        w.setze(nx, 3, nz, w.b("amethyst_cluster", facing="up", waterlogged=False))
        for t in np.linspace(0, 1, int(R * 1.2)):
            rr = R * (1 - t)
            yy = round(H + math.sin(t * math.pi / 2) * R * 0.6)
            w.setze(round(math.cos(a) * rr), yy, round(math.sin(a) * rr), Z.bau(0, yy, 0, 0.9))
    gold_haufen(w, 0, 0, R * 0.35, 1.5 + u * 0.4)
    w.setze(0, round(H + R * 0.6) + 1, 0, w.b("lantern", hanging=True, waterlogged=False))
    hohl(w, 2)
    return w


def tunnelportal(seed, g=2):
    """Bahn-Tunnelportal: ein mächtiges gemauertes Tunnelportal mit Zahnradbahn-Gleisen, Signalmasten und
    Wappen, in den Berg geschlagen, davor ein kleiner Bahnsteig."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    W, H = 12 * u + 6, 10 * u + 6
    bergwand(w, 0, W, H, Z, D=W * 0.6)
    gelaende(w, _r(W), art="wiese", dichte=0.2)
    B, Ht = 2 + (g >= 2), _r(3 * u + 3, 4)
    for x in range(-B - 2, B + 3):
        for y in range(1, Ht + 3):
            bog = (x / (B + 0.5)) ** 2 + ((y - 1) / (Ht + 0.5)) ** 2 < 1
            for z in range(-_r(W * 0.5), 2):
                if bog:
                    w.bloecke.pop((x, y, z), None)
            if not bog and ((x / (B + 2.5)) ** 2 + ((y - 1) / (Ht + 2.5)) ** 2 < 1):
                w.setze(x, y, 1, Z.bau(x, y, 1, y / (Ht + 3)))
    runenband(w, Z, -B - 2, B + 2, Ht + 3, 1)
    for z in range(-_r(W * 0.5), _r(W * 0.6)):
        w.setze(0, 1, z, MB.mod(w, "create:track", "rail", {"shape": "north_south", "waterlogged": False},
                                shape="zo", turn=False, waterlogged=False))
    for z in range(3, _r(W * 0.5)):
        for x in range(2, 5):
            w.setze(x, 1, z, Z.fein(x, 1, z, 0.3))
    for z in (4, _r(W * 0.5) - 1):
        for y in range(2, 6):
            w.setze(5, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
        w.setze(5, 6, z, w.b("redstone_lamp", lit=True))
    hohl(w, 3)
    return w


def pilzfarm(seed, g=1):
    """Pilzfarm unter dem Berg: eine offene Felsgrotte mit Myzelfeldern, Riesenpilzen, Glühflechten, Bewässerungs-
    rinnen und einem kleinen Lagerhaus."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    R = 9 * u + 5
    S = Skulptur(w, 1.0)
    S.mat("f", lambda x, y, z, *_: Z.fels(x, y, z, y / R))
    S.plus(lambda X, Y, Z_: (X * X + (Y * 1.4) ** 2 + Z_ * Z_ < R * R) & (Y >= -1), "f")
    S.minus(lambda X, Y, Z_: (X * X + (Y * 1.5) ** 2 + Z_ * Z_ < (R - 2.5) ** 2) & (Y >= 0))
    S.minus(lambda X, Y, Z_: (Z_ > R * 0.25) & (Y >= 0))
    S.rendern((-R - 1, -2, -R - 1), (R + 1, R, R + 1), versatz=(0.5, 0.01, 0.5))
    rng = w.rng
    for x, z in scheibe(R - 2.5):
        if z > R * 0.25:
            continue
        w.setze(x, 0, z, w.b("mycelium", snowy=False) if x % 4 else w.b("water", level=0))
        if x % 4 and rng.random() < 0.3:
            w.setze(x, 1, z, w.b("brown_mushroom") if rng.random() < 0.5 else w.b("red_mushroom"))
    for i in range(2 + g):
        x, z = int(rng.integers(-R // 2, R // 2)), int(rng.integers(-R // 2, 0))
        hh = 3 + g
        for y in range(1, hh + 1):
            w.setze(x, y, z, w.b("mushroom_stem", up=True, down=True, north=True, south=True, east=True, west=True))
        for xx, zz in scheibe(2.2, x, z):
            w.setze(xx, hh + 1, zz, w.b("red_mushroom_block" if i % 2 else "brown_mushroom_block", up=True,
                                        down=False, north=True, south=True, east=True, west=True))
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 3 and w.frei(x, y - 1, z) and rng.random() < 0.08:
            w.setze(x, y - 1, z, w.b("glow_lichen", down=False, up=True, north=False, south=False, east=False,
                                     west=False, waterlogged=False))
    hohl(w, 3)
    return w


def amboss_monument(seed, g=2):
    """Amboss-Monument: ein gewaltiger Amboss aus Eisen auf einem Stufensockel, darauf ein Kriegshammer mit
    Runengriff, umgeben von Kohlebecken und Schildern."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    s = 0.6 * u + 0.3
    gelaende(w, _r(10 * s + 6), art="wiese" if Z.granit else "asche", dichte=0.2)
    for k in range(3):
        for x in range(-_r(6 * s) - 3 + k, _r(6 * s) + 4 - k):
            for z in range(-_r(4 * s) - 3 + k, _r(4 * s) + 4 - k):
                w.setze(x, 1 + k, z, Z.bau(x, 1 + k, z, k / 3))
    S = Skulptur(w, s)
    S.mat("e", lambda x, y, z, *_: w.b("iron_block") if (x + y + z) % 4 else w.b("polished_basalt", axis="y"))
    S.mat("h", bl(w, "dark_oak_log"))
    S.mat("g", bl(w, Z.gold))
    S.plus(lambda X, Y, Z_: (np.abs(X) < 3) & (np.abs(Z_) < 2) & (Y >= 0) & (Y < 2), "e")
    S.plus(lambda X, Y, Z_: (np.abs(X) < 1.6 - 0.2 * (Y - 2)) & (np.abs(Z_) < 1.2) & (Y >= 2) & (Y < 5), "e")
    S.plus(lambda X, Y, Z_: (X > -5.5 + np.maximum(0, 7 - Y) * 0) & (X < 5) & (np.abs(Z_) < 1.8) & (Y >= 5) & (Y < 7.5)
           & ((X < 2.5) | (Y > 6.0 + (X - 2.5) * 0.4)), "e")
    S.plus(kap((-1, 7.5, 0), (2.5, 14, 0), 0.5, 0.5), "h")
    S.plus(lambda X, Y, Z_: (np.abs(X - 2.8) < 1.6) & (np.abs(Y - 14.5) < 1.2) & (np.abs(Z_) < 1.3), "e")
    S.plus(lambda X, Y, Z_: (np.abs(X - 2.8) < 1.7) & (np.abs(Y - 14.5) < 0.3) & (np.abs(Z_) < 1.4), "g")
    S.rendern((-7, 0, -3), (6, 17, 3), versatz=(0.5, 4.01, 0.5))
    for i in range(4):
        a = i / 4 * 2 * math.pi + math.pi / 4
        x, z = round(math.cos(a) * (8 * s + 3)), round(math.sin(a) * (8 * s + 3))
        w.setze(x, 1, z, MB.kohlenbecken(w))
    hohl(w, 2)
    return w


def stufenstadt(seed, g=2):
    """Terrassenstadt am Berg: Häuser auf in den Hang gehauenen Terrassen, verbunden durch Treppen, mit
    Steindächern, Schornsteinen und einem Tor oben in der Felswand."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    n = 2 + g
    W = 10 * u + 8
    T = 6
    for k in range(n + 1):
        z0 = -k * T
        for x in range(-_r(W), _r(W) + 1):
            for z in range(z0 - T, z0 + 1):
                for y in range(0, k * 4 + 1):
                    w.setze(x, y, z, Z.fels(x, y, z, y / (n * 4 + 4)) if y < k * 4 else Z.fein(x, y, z, 0.3))
    st = Z.stil()
    rng = w.rng
    for k in range(n):
        z0 = -k * T
        for i in range(2 + (u > 1)):
            x0 = -_r(W) + 2 + i * _r(W * 0.7)
            P.gebaeude(w, st, x0, z0 - T + 1, x0 + 4, z0 - 2, y0=k * 4 + 1, etagen=1, eh=4, dach="sattel",
                       tuer="south", gauben=False, kamine=1)
        for s in range(4):
            for x in (_r(W) - 3, _r(W) - 2):
                w.setze(x, k * 4 + 1 + s, z0 - 1 - s, w.b("stone_brick_stairs", facing="north", half="bottom",
                                                          shape="straight", waterlogged=False))
    ztop = -n * T
    portal(w, Z, 0, ztop - T + 1, 2, 5)
    hohl(w, 3)
    return w


def horn_turm(seed, g=2):
    """Hornturm: ein kantiger Turm, an dessen Spitze ein riesiges geschwungenes Kriegshorn aus Knochen und Gold
    montiert ist, Wimpel und Wachplattform."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    B = _r(2.5 * u + 2, 3)
    H = _r(14 * u + 6)
    gelaende(w, B + 8, art="wiese", dichte=0.2)
    for y in range(1, H + 1):
        bb = B - (y > H * 0.7)
        for x in range(-bb, bb + 1):
            for z in range(-bb, bb + 1):
                if max(abs(x), abs(z)) == bb:
                    w.setze(x, y, z, w.b(Z.gold) if y % 7 == 0 else Z.bau(x, y, z, y / H))
    for x in range(-B - 1, B + 2):
        for z in range(-B - 1, B + 2):
            w.setze(x, H + 1, z, Z.fein(x, H + 1, z, 0.7))
            if max(abs(x), abs(z)) == B + 1 and (x + z) % 2 == 0:
                w.setze(x, H + 2, z, Z.bau(x, H + 2, z, 0.9))
    s = 0.5 * u + 0.3
    S = Skulptur(w, s)
    S.mat("h", lambda x, y, z, *_: w.b("bone_block", axis="y") if (x + y) % 3 else w.b("calcite"))
    S.mat("g", bl(w, Z.gold))
    pts = [(0, 0, 0), (2, 1.5, 0), (4, 3.8, 0), (5.2, 6.5, 0), (5.0, 9.5, 0)]
    rad = [0.6, 0.9, 1.3, 1.8, 2.4]
    for i in range(len(pts) - 1):
        S.plus(kap(pts[i], pts[i + 1], rad[i], rad[i + 1]), "h")
        S.plus(lambda X, Y, Z_, p=pts[i + 1], r=rad[i + 1]: ((X - p[0]) ** 2 + (Y - p[1]) ** 2 + Z_ * Z_ < (r + 0.3) ** 2)
               & (np.abs(Y - p[1]) < 0.3), "g")
    S.minus(ell(5.0, 9.9, 0, 1.8, 0.6, 1.8))
    S.rendern((-2, -2, -4), (8, 12, 4), versatz=(0.5, H + 2.01, 0.5))
    hohl(w, 2)
    return w


def talsperre(seed, g=2):
    """Zwergen-Talsperre: eine gekrümmte Staumauer zwischen zwei Felshängen, oben ein Wehrgang mit Wachhäusern,
    aus drei Auslässen schießen Wasserfälle in ein Tosbecken."""
    w = _welt(seed)
    Z = Zwerg(w, seed)
    u = U[g]
    L = _r(14 * u + 6)
    H = _r(10 * u + 5)
    for x in range(-L - 6, L + 7):
        for z in range(-L, L + 1):
            if abs(x) > L:
                hh = H + 3 - (abs(z) > L * 0.7) * 2
                for y in range(0, hh):
                    w.setze(x, y, z, Z.fels(x, y, z, y / H))
            elif z < -2:
                w.setze(x, H - 2, z, w.b("water", level=0))
                for y in range(0, H - 2):
                    w.setze(x, y, z, Z.fels(x, y, z, 0.2)) if y < 2 else None
            else:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel"))
    for x in range(-L, L + 1):
        bog = round((x / L) ** 2 * 3)
        for y in range(0, H + 1):
            dicke = max(1, round(3 - y / H * 2))
            for z in range(-2 - dicke + bog, -1 + bog):
                w.setze(x, y, z, Z.bau(x, y, z, y / H))
        w.setze(x, H + 1, -1 + bog, Z.bau(x, H + 1, 0, 0.9) if x % 2 else w.b(Z.gold))
    for i, x in enumerate((-L // 2, 0, L // 2)):
        for y in range(1, H - 2):
            w.setze(x, y, -1 + round((x / L) ** 2 * 3), w.b("water", level=0 if y == H - 3 else 8))
    st = Z.stil()
    for sx in (-1, 1):
        P.gebaeude(w, st, sx * (L // 2) - 2, -6, sx * (L // 2) + 2, -3, y0=H + 1, etagen=1, eh=4, dach="walm",
                   tuer="south", gauben=False, kamine=0)
    hohl(w, 3)
    return w


ZWERGE = {
    "bergtor": ("Bergtor", bergtor),
    "schmiedehalle": ("Große Schmiedehalle", schmiedehalle),
    "bergfestung": ("Bergfestung", bergfestung),
    "mineneingang": ("Mineneingang", mineneingang),
    "thronhalle": ("Thronhalle der Bergkönige", thronhalle),
    "brauhaus": ("Zwergen-Brauhaus", brauhaus),
    "kluftbruecke": ("Kluftbrücke", kluftbruecke),
    "wachturm": ("Zwergen-Wachturm", wachturm),
    "runenstein": ("Großer Runenstein", runenstein),
    "erzlager": ("Erzlager", erzlager),
    "huegelhaus": ("Hügelhaus", huegelhaus),
    "ahnenhalle": ("Halle der Ahnen", ahnenhalle),
    "lavaschmelze": ("Lavaschmelze", lavaschmelze),
    "schatzkammer": ("Edelsteinkammer", schatzkammer),
    "tunnelportal": ("Tunnelportal", tunnelportal),
    "pilzfarm": ("Pilzfarm", pilzfarm),
    "amboss": ("Amboss-Monument", amboss_monument),
    "stufenstadt": ("Terrassenstadt", stufenstadt),
    "hornturm": ("Hornturm", horn_turm),
    "talsperre": ("Zwergen-Talsperre", talsperre),
}

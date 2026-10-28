"""Kathedralen & Tempel (neu) – 20 sakrale Bauten aller Kulturen im Pracht-Stil.

Hohe Spitzbogenfenster mit Buntglas-Verläufen, Strebepfeiler mit Fialen, Rosetten, Apsiden,
Säulenhallen mit Kapitellen, Kuppeln mit Rippen, Tempelpyramiden, Pylone und Steinkreise.
"""

from __future__ import annotations

import math

import numpy as np

import pracht as P
from lib import Rauschen, Verlauf, einfuegen, laub, zerfall
from pracht import Mat, gelaende, treppe
from skulptur import Skulptur, ell, kap, kreisrand, ohne, scheibe, torus
from weltwunder import bl, hohl, platz, sk

U = [0.6, 1.0, 1.7, 2.8]
GEGEN = {"north": "south", "south": "north", "east": "west", "west": "east"}


def _welt(seed):
    from lib import Welt
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _richtung(x, z, x0, z0, x1, z1):
    if z == z0:
        return "south"
    if z == z1:
        return "north"
    if x == x0:
        return "east"
    return "west"


GLAS = {
    "bunt": ["blue_stained_glass", "red_stained_glass", "purple_stained_glass", "yellow_stained_glass",
             "light_blue_stained_glass"],
    "blau": ["blue_stained_glass", "light_blue_stained_glass", "cyan_stained_glass", "white_stained_glass"],
    "gold": ["yellow_stained_glass", "orange_stained_glass", "white_stained_glass", "yellow_stained_glass"],
    "rot": ["red_stained_glass", "orange_stained_glass", "magenta_stained_glass", "purple_stained_glass"],
    "gruen": ["lime_stained_glass", "green_stained_glass", "cyan_stained_glass", "yellow_stained_glass"],
}

SAKRAL = {
    "kalk": dict(wand="kalkstein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="spruce",
                 glas="bunt"),
    "grau": dict(wand="graustein", sockel="graustein", gesims="stone_brick", dach="kupfer", holz="dark_oak",
                 glas="blau"),
    "backstein": dict(wand="backstein", sockel="graustein", gesims="brick", dach="schiefer", holz="dark_oak",
                      glas="rot"),
    "marmor": dict(wand="marmor", sockel="kalkstein", gesims="quartz", dach="kupfer", holz="birch", glas="gold"),
    "sand": dict(wand="sandstein", sockel="sandstein", gesims="sandstone", dach="sand", holz="jungle", glas="gold"),
    "schwarz": dict(wand="schwarzstein", sockel="schwarzstein", gesims="polished_blackstone_brick", dach="schwarz",
                    holz="dark_oak", glas="rot"),
    "tief": dict(wand="tiefenschiefer", sockel="tiefenschiefer", gesims="deepslate_brick", dach="schiefer",
                 holz="dark_oak", glas="blau"),
    "moos": dict(wand="moosstein", sockel="graustein", gesims="mossy_stone_brick", dach="moos", holz="spruce",
                 glas="gruen"),
    "rot": dict(wand="rotsandstein", sockel="rotsandstein", gesims="red_sandstone", dach="ziegel", holz="acacia",
                glas="gold"),
}


class S:
    def __init__(self, w, name):
        d = dict(SAKRAL[name])
        self.glas = Verlauf(w, "Glas" + name, GLAS[d.pop("glas")])
        self.st = P.Stil(w, laeden=False, blumen=0, fensterart="bogen", **d)
        self.wand = self.st.wand
        self.sockel = self.st.sockel
        self.gesims = self.st.gesims
        self.dach = self.st.dach
        self.holz = self.st.holz
        self.w = w

    def g(self, x, y, z, t):
        return self.glas(t * 4, x, y, z)


def stil(w, seed, a, b):
    return S(w, a if _stil(seed) == 0 else b)


# ============================================================================ Bauteile


def halle(w, s, x0, z0, x1, z1, y0, H, achse="x", fenster_abst=4, strebe=True, dach=True, fialen=True,
          rund=False, offen_enden=()):
    """Kirchenschiff: Wände mit hohen Spitz- oder Rundbogenfenstern aus Buntglas, Strebepfeiler mit Fialen,
    Kranzgesims und steilem Satteldach (First entlang achse). Gibt die Firsthöhe zurück."""
    lang = range(x0, x1 + 1) if achse == "x" else range(z0, z1 + 1)
    for y in range(y0, y0 + H):
        t = (y - y0) / H
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                rand_l = (z in (z0, z1)) if achse == "x" else (x in (x0, x1))
                rand_q = (x in (x0, x1)) if achse == "x" else (z in (z0, z1))
                if not (rand_l or rand_q):
                    if y == y0:
                        w.setze(x, y, z, w.b("polished_andesite") if (x + z) % 2 else w.b("smooth_stone"))
                    continue
                q = x - x0 if achse == "x" else z - z0
                hy = y - y0
                fen_h = H - 4
                in_fenster = rand_l and not rand_q and q % fenster_abst == fenster_abst // 2 and 2 <= hy < 2 + fen_h
                if in_fenster:
                    spitze = hy >= 2 + fen_h - 1 and not rund
                    w.setze(x, y, z, s.g(x, y, z, (hy - 2) / max(1, fen_h)) if not spitze else w.b("chiseled_stone_bricks")
                            if s.gesims == "stone_brick" else s.wand(x, y, z, 0.9))
                    if fenster_abst >= 4:
                        for d in (-1, 1):
                            if hy < 2 + fen_h - 2:
                                px, pz = (x + d, z) if achse == "x" else (x, z + d)
                                w.setze(px, y, pz, s.g(px, y, pz, (hy - 2) / max(1, fen_h)))
                    continue
                w.setze(x, y, z, s.wand(x, y, z, t) if hy > 0 else s.sockel(x, y, z, 0.1))
    # Strebepfeiler mit Fialen
    if strebe:
        for q in lang:
            if (q - (x0 if achse == "x" else z0)) % fenster_abst != 0:
                continue
            for seite in (-1, 1):
                for k in range(3):
                    hh = H - 1 - k * (H // 4)
                    for y in range(y0, y0 + hh):
                        if achse == "x":
                            p = (q, y, (z0 - 1 - k) if seite < 0 else (z1 + 1 + k))
                        else:
                            p = ((x0 - 1 - k) if seite < 0 else (x1 + 1 + k), y, q)
                        w.setze(*p, s.sockel(*p, (y - y0) / H))
                    if achse == "x":
                        p = (q, y0 + hh, (z0 - 1 - k) if seite < 0 else (z1 + 1 + k))
                        f = "south" if seite < 0 else "north"
                    else:
                        p = ((x0 - 1 - k) if seite < 0 else (x1 + 1 + k), y0 + hh, q)
                        f = "east" if seite < 0 else "west"
                    w.setze(*p, treppe(w, s.gesims, f))
                if fialen:
                    if achse == "x":
                        p = (q, y0 + H, z0 - 1 if seite < 0 else z1 + 1)
                    else:
                        p = (x0 - 1 if seite < 0 else x1 + 1, y0 + H, q)
                    w.setze(p[0], p[1] - 1, p[2], s.sockel(*p, 0.8))
                    w.setze(*p, w.b(f"{s.gesims}_wall" if s.gesims in ("stone_brick", "brick", "sandstone",
                                                                         "red_sandstone", "deepslate_brick",
                                                                         "polished_blackstone_brick", "mossy_stone_brick")
                                    else "stone_brick_wall", up=True, north="none", south="none", east="none",
                                    west="none", waterlogged=False))
                    w.setze(p[0], p[1] + 1, p[2], w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    # Kranzgesims
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            if (x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1)) and not (x in (x0 - 1, x1 + 1) and z in (z0 - 1, z1 + 1)):
                w.setze(x, y0 + H - 1, z, treppe(w, s.gesims, _richtung(x, z, x0 - 1, z0 - 1, x1 + 1, z1 + 1), "top"),
                        ueberschreiben=False)
    top = y0 + H
    if dach:
        top = P.satteldach(w, s.dach, x0, z0, x1, z1, y0 + H, ue=1, first_x=achse == "x", wand=s.wand, steil=True)
    return top


def rosette(w, s, cx, cy, z, R, achse="z"):
    """Rundfenster (Rosette) mit Speichen; achse = Blickrichtung der Wand."""
    for a in range(-int(R) - 1, int(R) + 2):
        for b in range(-int(R) - 1, int(R) + 2):
            d = math.hypot(a, b)
            if d > R + 0.5:
                continue
            p = (cx + a, cy + b, z) if achse == "z" else (z, cy + b, cx + a)
            ang = math.atan2(b, a)
            if d > R - 0.6 or d < 1.2 or abs(math.sin(ang * 4)) < 0.2:
                w.setze(*p, w.b("chiseled_stone_bricks") if s.gesims == "stone_brick" else s.sockel(*p, 0.9))
            else:
                w.setze(*p, s.g(*p, d / max(1, R)))


def apsis(w, s, cx, cz, y0, R, H, richtung="x+"):
    """Halbrunde Apsis mit Fenstern und Halbkegeldach."""
    sgn = 1 if richtung.endswith("+") else -1
    for y in range(y0, y0 + H):
        for x, z in kreisrand(R, cx, cz):
            if (x - cx) * sgn < 0 if richtung[0] == "x" else (z - cz) * sgn < 0:
                continue
            a = math.atan2(z - cz, x - cx)
            fen = (y - y0) in range(2, H - 2) and abs(math.sin(a * 3)) < 0.25
            w.setze(x, y, z, s.g(x, y, z, (y - y0) / H) if fen else s.wand(x, y, z, (y - y0) / H))
    for k in range(int(R) + 2):
        r = R + 0.8 - k
        for x, z in kreisrand(max(0.4, r), cx, cz):
            if (x - cx) * sgn < 0 if richtung[0] == "x" else (z - cz) * sgn < 0:
                continue
            w.setze(x, y0 + H + k, z, s.dach.voll(x, y0 + H + k, z))


def saeulenreihe(w, s, punkte, y0, H, mat="quartz_pillar", kapitell="chiseled_quartz_block"):
    for (x, z) in punkte:
        w.setze(x, y0, z, s.sockel(x, y0, z, 0.2))
        for y in range(y0 + 1, y0 + H - 1):
            w.setze(x, y, z, w.b(mat, axis="y") if mat.endswith(("pillar", "log")) else w.b(mat))
        w.setze(x, y0 + H - 1, z, w.b(kapitell))


def giebel_dreieck(w, s, x0, x1, z, y0, mat_voll, mat_treppe, tief=1):
    """Flacher Tempelgiebel (Tympanon) an der Stirnseite z."""
    h = (x1 - x0) // 4
    for k in range(h + 1):
        a, b = x0 + 2 * k, x1 - 2 * k
        if a > b:
            break
        for x in range(a, b + 1):
            for d in range(tief):
                zz = z + d
                if x in (a, a + 1) and k < h:
                    w.setze(x, y0 + k, zz, treppe(w, mat_treppe, "east"))
                elif x in (b, b - 1) and k < h:
                    w.setze(x, y0 + k, zz, treppe(w, mat_treppe, "west"))
                else:
                    w.setze(x, y0 + k, zz, w.b(mat_voll))


# ============================================================================ 1 Kathedrale


def kathedrale(seed, g=2):
    """Gotische Kathedrale: dreischiffiges Langhaus mit Strebewerk und Fialen, Querhaus, Vierungsturm,
    Doppelturmfassade mit Rosette und Portal, Chor mit Apsis."""
    w = _welt(seed)
    s = stil(w, seed, "kalk", "grau")
    u = U[g]
    L = _r(20 * u + 6, 14)
    B = _r(5 * u + 2, 4)
    H = _r(13 * u + 5, 10)
    gelaende(w, L + _r(12 * u, 6), art="wiese", wege=[((-L - 4, 0), (-L - 18, 0))])
    halle(w, s, -L, -B, L, B, 1, H, achse="x")
    # Seitenschiffe
    for sz in (-1, 1):
        z0, z1 = (B + 1, B + _r(3 * u + 2, 3)) if sz > 0 else (-B - _r(3 * u + 2, 3), -B - 1)
        halle(w, s, -L + 2, z0, L - 6, z1, 1, _r(H * 0.55), achse="x", strebe=True, fialen=True, dach=False)
        for x in range(-L + 1, L - 5):
            for k in range(z1 - z0 + 2):
                z = (z1 + 1 - k) if sz > 0 else (z0 - 1 + k)
                y = 1 + _r(H * 0.55) + k // 1 * 0 + (k if False else 0)
        P.satteldach(w, s.dach, -L + 2, z0, L - 6, z1, 1 + _r(H * 0.55), ue=1, first_x=True)
    # Querhaus
    Q = _r(4 * u + 2, 3)
    halle(w, s, _r(L * 0.35) - Q, -B - _r(7 * u + 4, 6), _r(L * 0.35) + Q, B + _r(7 * u + 4, 6), 1, H, achse="z")
    # Vierungsturm
    P.turm(w, s.st, _r(L * 0.35), 0, H, _r(10 * u + 4), max(2.0, Q - 0.5), form="achteck", dach="nadel",
           krone=False, fahne=None)
    # Doppelturmfassade
    tw = _r(3 * u + 1.5, 3)
    for sz in (-1, 1):
        P.turm(w, s.st, -L - tw, sz * (B + tw - 1), 1, _r(H * 1.7), tw + 0.4, form="eckig", dach="nadel",
               krone=False, fahne=None, fenster=8)
    for y in range(1, H + 4):
        for z in range(-B + 1, B):
            w.setze(-L - 1, y, z, s.wand(-L - 1, y, z, y / H))
    rosette(w, s, 0, _r(H * 0.7), -L - 2, max(2, B - 1.5), achse="x")
    # Portal
    for y in range(1, _r(H * 0.4) + 1):
        for z in range(-2, 3):
            for x in (-L - 1, -L):
                w.bloecke.pop((x, y, z), None)
    for y, half in ((1, "lower"), (2, "upper")):
        for z in (0,):
            w.setze(-L, y, z, w.b(f"{s.holz}_door", facing="west", half=half, hinge="left", open=False, powered=False))
    for k in range(3):
        for z in range(-3 - k, 4 + k):
            w.setze(-L - 2 - k, 0, z, treppe(w, s.gesims, "east"))
    # Apsis
    apsis(w, s, L, 0, 1, B + 0.5, H, "x+")
    hohl(w, 2)
    return w


# ============================================================================ 2 Dorfkirche


def dorfkirche(seed, g=1):
    """Dorfkirche: Saalbau mit Westturm und Zwiebelhaube oder Spitzhelm, Kirchhof mit Mauer, Gräbern und Linde."""
    import haeuser as H_
    w = _welt(seed)
    s = stil(w, seed, "kalk", "backstein")
    u = U[g]
    L, B, H = _r(8 * u + 4, 6), _r(3 * u + 2, 3), _r(6 * u + 4, 6)
    gelaende(w, L + 10, art="wiese", wege=[((-L - 3, 0), (-L - 12, 0))])
    halle(w, s, -L, -B, L, B, 1, H, achse="x", fenster_abst=4, fialen=False)
    apsis(w, s, L, 0, 1, B, H - 1, "x+")
    P.turm(w, s.st, -L - 2, 0, 1, _r(H * 2.1), B + 0.3, form="eckig", dach="zwiebel" if _stil(seed) else "nadel",
           krone=False, fahne=None)
    for x in range(-L - 6, L + 7):
        for z in (-B - 7, B + 7):
            w.setze(x, 1, z, s.sockel(x, 1, z, 0.3))
    for i in range(8):
        x, z = -L + 2 + (i % 4) * 4, (B + 4) * (1 if i < 4 else -1)
        w.setze(x, 1, z, w.b("cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
                             waterlogged=False))
        w.setze(x, 0, z + (1 if z > 0 else -1), w.b("podzol", snowy=False))
    H_.baum(w, L + 5, B + 4, "oak", H=7)
    hohl(w, 2)
    return w


# ============================================================================ 3 Basilika


def basilika(seed, g=2):
    """Romanische Basilika: wuchtige Mauern mit Rundbogenfenstern, Obergaden, Zwerggalerie, zwei Rundtürme
    an der Apsis und ein Vierungsturm mit Pyramidendach."""
    w = _welt(seed)
    s = stil(w, seed, "rot", "sand")
    u = U[g]
    L, B, H = _r(16 * u + 5), _r(4 * u + 2, 3), _r(10 * u + 4, 7)
    gelaende(w, L + 10, art="wiese")
    halle(w, s, -L, -B, L, B, 1, H, achse="x", strebe=False, rund=True, fenster_abst=3)
    for sz in (-1, 1):
        z0, z1 = (B + 1, B + _r(3 * u + 2, 3)) if sz > 0 else (-B - _r(3 * u + 2, 3), -B - 1)
        halle(w, s, -L, z0, L - 2, z1, 1, _r(H * 0.55), achse="x", strebe=False, rund=True, dach=False, fenster_abst=3)
        P.satteldach(w, s.dach, -L, z0, L - 2, z1, 1 + _r(H * 0.55), ue=1, first_x=True)
    apsis(w, s, L, 0, 1, B + 0.5, H - 2, "x+")
    for sz in (-1, 1):
        P.turm(w, s.st, L - 1, sz * (B + 2), 1, _r(H * 1.5), 1.8 * min(u, 1.7), form="rund", dach="kegel",
               krone=False, fahne=None)
    P.turm(w, s.st, _r(-L * 0.1), 0, H, _r(6 * u + 3), B + 0.4, form="achteck", dach="pyramide", krone=False,
           fahne=None)
    hohl(w, 2)
    return w


# ============================================================================ 4 Kuppelkirche


def kuppelkirche(seed, g=2):
    """Kuppelkirche: Kreuzförmiger Bau mit großer Rippenkuppel auf Tambour, vier Nebenkuppeln,
    Laterne und schlanken Glockentürmen. Stil 1 Marmor mit Kupfer, Stil 2 Sandstein mit Gold."""
    w = _welt(seed)
    s = stil(w, seed, "marmor", "sand")
    u = U[g]
    A, B, H = _r(10 * u + 4), _r(4 * u + 2, 3), _r(8 * u + 4, 6)
    y0 = platz(w, _r(A + 10 * u), Mat(w, "marmor") if _stil(seed) == 0 else Mat(w, "sandstein"),
               rand="quartz" if _stil(seed) == 0 else "sandstone",
               muster=["polished_diorite", "quartz_bricks", "gold_block"] if _stil(seed) == 0 else
               ["smooth_sandstone", "cut_sandstone", "gold_block"], akzent="chiseled_quartz_block" if _stil(seed) == 0
               else "chiseled_sandstone", lichter="lantern", pfosten="diorite_wall" if _stil(seed) == 0 else
               "sandstone_wall")
    halle(w, s, -A, -B, A, B, y0, H, achse="x", strebe=False, fenster_abst=3, rund=True)
    halle(w, s, -B, -A, B, A, y0, H, achse="z", strebe=False, fenster_abst=3, rund=True)
    # Tambour und Kuppel
    R = B + 2.5
    yt = y0 + H + 1
    for y in range(yt - 2, yt + _r(4 * u + 2, 4)):
        for x, z in kreisrand(R):
            a = math.atan2(z, x)
            w.setze(x, y, z, s.g(x, y, z, 0.5) if (y - yt) in (1, 2) and abs(math.sin(a * 4)) < 0.3 else
                    s.wand(x, y, z, 0.8))
    yk = yt + _r(4 * u + 2, 4)
    Sk = Skulptur(w, 1.0)
    Sk.mat("k", lambda x, y, z, lx, ly, lz: s.dach.voll(x, y, z))
    Sk.mat("r", bl(w, "gold_block" if _stil(seed) else "smooth_quartz"))
    Sk.plus(ohne(ell(0, 0, 0, R + 0.6, R * 1.15, R + 0.6), lambda X, Y, Z: Y < 0), "k")
    for i in range(8):
        a = i / 8 * math.pi
        Sk.plus(lambda X, Y, Z, a=a: (np.abs(np.sqrt(X * X + Z * Z + (Y / 1.15) ** 2) - (R + 0.6)) < 0.8)
                & (np.abs(-X * math.sin(a) + Z * math.cos(a)) < 0.5) & (Y >= 0), "r")
    Sk.rendern((-R - 2, 0, -R - 2), (R + 2, R * 1.2 + 2, R + 2), versatz=(0.5, yk, 0.5))
    ylat = yk + int(R * 1.15)
    for y in range(ylat, ylat + 4):
        for x, z in kreisrand(1.3):
            w.setze(x, y, z, w.b("gold_block") if y == ylat + 3 else w.b("glass_pane", north=True, south=True,
                                                                         east=True, west=True, waterlogged=False))
    w.setze(0, ylat + 4, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    # Nebenkuppeln
    for (x, z) in ((A, 0), (-A, 0), (0, A), (0, -A)):
        for k in range(B + 1):
            for xx, zz in kreisrand(max(0.4, (B - 0.5) * math.cos(k / (B + 1) * math.pi / 2)), x, z):
                w.setze(xx, y0 + H + k, zz, s.dach.voll(xx, y0 + H + k, zz))
    for sx in (-1, 1):
        P.turm(w, s.st, sx * (A + 2), A // 2 + 2, y0, _r(H * 2.4), 1.6 * min(u, 1.7), form="rund", dach="zwiebel",
               krone=False, fahne=None)
    hohl(w, 2)
    return w


# ============================================================================ 5 Kloster


def kloster(seed, g=2):
    """Kloster: Klosterkirche, Kreuzgang mit Arkaden um einen Kräutergarten mit Brunnen, Refektorium,
    Dormitorium und Glockenturm."""
    import haeuser as H_
    w = _welt(seed)
    s = stil(w, seed, "grau", "backstein")
    u = U[g]
    a = _r(9 * u + 4, 6)
    eh = _r(3 * u + 2, 4)
    gelaende(w, a + 14, art="wiese")
    halle(w, s, -a, -a - _r(6 * u + 4, 5), a + 4, -a - 1, 1, _r(8 * u + 4, 6), achse="x", fialen=False)
    for (x0, z0, x1, z1, t) in ((-a, a - 3, a, a, "north"), (-a, -a, -a + 3, a - 4, "east"),
                                (a - 3, -a, a, a - 4, "west")):
        P.gebaeude(w, s.st, x0, z0, x1, z1, y0=1, etagen=2, eh=eh, dach="sattel", tuer=t, gauben=False)
    # Kreuzgang
    for x in range(-a + 4, a - 3):
        for z in range(-a, a - 3):
            rand = x in (-a + 4, a - 4) or z in (-a, a - 4)
            if rand:
                if (x + z) % 2 == 0:
                    for y in range(1, eh):
                        w.setze(x, y, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                             west="none", waterlogged=False))
                w.setze(x, eh, z, s.sockel(x, eh, z, 0.5))
            else:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
                if (x * 3 + z) % 5 == 0:
                    w.setze(x, 1, z, w.b(["allium", "azure_bluet", "lily_of_the_valley", "cornflower"][abs(x + z) % 4]))
                elif (x + z) % 7 == 0:
                    w.setze(x, 1, z, laub(w, "azalea"))
    w.setze(0, 1, -2, w.b("water", level=0))
    for x, z in kreisrand(1.5, 0, -2):
        w.setze(x, 1, z, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    P.turm(w, s.st, a + 2, -a - 3, 1, _r(18 * u + 6), 1.8 * min(u, 1.7), form="eckig", dach="nadel", krone=False,
           fahne=None)
    H_.beet(w, a + 3, -a + 2, a + 8, a - 4, "gemuese")
    hohl(w, 2)
    return w


# ============================================================================ 6 Abteiruine


def abteiruine(seed, g=2):
    """Abteiruine: Gerippe einer gotischen Kirche ohne Dach – stehende Fensterbögen, eingestürzte Pfeiler,
    Moos, Efeu und junge Birken im Schiff."""
    import baeume as Bm
    w = _welt(seed)
    s = stil(w, seed, "moos", "grau")
    u = U[g]
    L, B, H = _r(14 * u + 5), _r(4 * u + 2, 3), _r(11 * u + 5, 8)
    halle(w, s, -L, -B, L, B, 1, H, achse="x", dach=False)
    apsis(w, s, L, 0, 1, B, H, "x+")
    P.turm(w, s.st, -L - 2, 0, 1, _r(H * 1.6), B + 0.3, form="eckig", dach="platt", krone=False, fahne=None)
    betroffen = set(b for b in w.bloecke.values() if b)
    zerfall(w, betroffen, Rauschen(w, 3), _r(H * 1.6), staerke=0.8, boden=3)
    gelaende(w, L + 10, art="wald", dichte=1.2)
    rng = w.rng
    for (x, y, z), blk in list(w.bloecke.items()):
        if y > 1 and w.frei(x, y + 1, z) and rng.random() < 0.4:
            w.setze(x, y + 1, z, w.b("moss_carpet"))
        if y > 3 and rng.random() < 0.05:
            for dx, dz, sd in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
                if w.frei(x + dx, y, z + dz):
                    for k in range(int(2 + rng.random() * 7)):
                        if not w.frei(x + dx, y - k, z + dz) or y - k < 1:
                            break
                        w.setze(x + dx, y - k, z + dz, w.b("vine", **{q: q == sd for q in
                                                                     ("north", "east", "south", "west")}, up=False))
                    break
    for i in range(int(3 * u) + 1):
        einfuegen(w, Bm.ARTEN["birke"][1](int(rng.integers(1, 10 ** 6)), 0), int(-L + 3 + rng.random() * 2 * L * 0.8),
                  0, int((rng.random() - 0.5) * B))
    hohl(w, 2)
    return w


# ============================================================================ 7 Griechischer Tempel


def saeulentempel(seed, g=2):
    """Griechischer Säulentempel: dreistufiger Unterbau, umlaufende Säulenhalle mit Kapitellen, Cella mit
    Bronzetür, Giebelfelder mit Gesims, flaches Ziegeldach und Opferaltar."""
    w = _welt(seed)
    s = stil(w, seed, "marmor", "kalk")
    u = U[g]
    L, B = _r(11 * u + 4, 7), _r(6 * u + 3, 5)
    H = _r(9 * u + 3, 7)
    gelaende(w, L + 9, art="wiese")
    for k in range(3):
        for x in range(-L - 3 + k, L + 4 - k):
            for z in range(-B - 3 + k, B + 4 - k):
                rnd = x in (-L - 3 + k, L + 3 - k) or z in (-B - 3 + k, B + 3 - k)
                w.setze(x, 1 + k, z, treppe(w, s.gesims, _richtung(x, z, -L - 3 + k, -B - 3 + k, L + 3 - k, B + 3 - k))
                        if rnd and not (x in (-L - 3 + k, L + 3 - k) and z in (-B - 3 + k, B + 3 - k)) else
                        s.sockel(x, 1 + k, z, 0.3))
    y0 = 4
    pts = [(x, z) for x in range(-L, L + 1, 2) for z in (-B, B)] + [(x, z) for x in (-L, L) for z in range(-B + 2, B, 2)]
    saeulenreihe(w, s, pts, y0 - 1, H + 1, mat="quartz_pillar" if s.gesims == "quartz" else "polished_andesite",
                 kapitell="chiseled_quartz_block" if s.gesims == "quartz" else "chiseled_stone_bricks")
    # Cella
    P.gebaeude(w, s.st, -L + 3, -B + 2, L - 3, B - 2, y0=y0, etagen=1, eh=H - 1, dach="flach", tuer="west",
               gauben=False, kamine=0, sockel_h=0)
    # Gebälk
    ye = y0 + H
    for x in range(-L - 1, L + 2):
        for z in range(-B - 1, B + 2):
            w.setze(x, ye, z, s.wand(x, ye, z, 0.9))
            if x in (-L - 1, L + 1) or z in (-B - 1, B + 1):
                w.setze(x, ye + 1, z, w.b("chiseled_quartz_block" if s.gesims == "quartz" else "chiseled_stone_bricks")
                        if (x + z) % 3 == 0 else s.wand(x, ye + 1, z, 0.95))
    P.satteldach(w, P.Dach(w, "ziegel" if _stil(seed) == 0 else "grau"), -L - 1, -B - 1, L + 1, B + 1, ye + 1, ue=1,
                 first_x=True, wand=s.wand)
    # Altar
    for x in range(-L - 7, -L - 4):
        w.setze(x, 1, 0, s.sockel(x, 1, 0, 0.5))
    w.setze(-L - 6, 2, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    hohl(w, 2)
    return w


# ============================================================================ 8 Rundtempel


def rundtempel(seed, g=1):
    """Rundtempel (Tholos): Säulenkranz um eine runde Cella, Kuppeldach mit Laterne, Stufensockel."""
    w = _welt(seed)
    s = stil(w, seed, "marmor", "rot")
    u = U[g]
    R = 6 * u + 3
    H = _r(7 * u + 3, 6)
    gelaende(w, _r(R + 8), art="wiese")
    for k in range(3):
        for x, z in kreisrand(R + 3 - k):
            w.setze(x, 1 + k, z, treppe(w, s.gesims, zur(x, z)))
        for x, z in scheibe(R + 2 - k):
            if w.frei(x, 1 + k, z):
                w.setze(x, 1 + k, z, s.sockel(x, 1 + k, z, 0.3))
    y0 = 4
    n = max(8, int(R * 2))
    pts = [(round(math.cos(i / n * 2 * math.pi) * (R + 0.5)), round(math.sin(i / n * 2 * math.pi) * (R + 0.5)))
           for i in range(n)]
    saeulenreihe(w, s, pts, y0 - 1, H + 1, mat="quartz_pillar" if s.gesims == "quartz" else "smooth_red_sandstone",
                 kapitell="chiseled_quartz_block" if s.gesims == "quartz" else "chiseled_red_sandstone")
    for y in range(y0, y0 + H):
        for x, z in kreisrand(R - 2.5):
            w.setze(x, y, z, s.wand(x, y, z, (y - y0) / H))
    for y, half in ((y0, "lower"), (y0 + 1, "upper")):
        w.bloecke.pop((0, y, round(R - 2.5)), None)
    for x, z in scheibe(R + 1.5):
        w.setze(x, y0 + H, z, s.wand(x, y0 + H, z, 0.9))
    for k in range(int(R) + 1):
        r = (R + 1) * math.cos(k / (R + 1) * math.pi / 2)
        for x, z in kreisrand(max(0.4, r)):
            w.setze(x, y0 + H + 1 + k, z, s.dach.voll(x, y0 + H + 1 + k, z))
    hohl(w, 2)
    return w


def zur(x, z):
    from skulptur import zur_mitte
    return zur_mitte(x, z)


# ============================================================================ 9 Stufentempel


def stufentempel(seed, g=2):
    """Stufentempel im Dschungel: neun Terrassen, steile Prunktreppe mit Wangen, Tempelhaus mit Dachkamm,
    Schlangenköpfe am Treppenfuß, Ranken und Moos."""
    w = _welt(seed)
    s = stil(w, seed, "moos", "sand")
    u = U[g]
    n = 6 + (g >= 2) * 2
    B0 = _r(12 * u + 5)
    sh = _r(2 * u + 1.5, 2)
    gelaende(w, B0 + 10, art="wald" if _stil(seed) == 0 else "sand", dichte=1.0)
    rng = w.rng
    for k in range(n):
        h = B0 - k * (B0 - 4) // n
        for y in range(1 + k * sh, 1 + (k + 1) * sh):
            for x in range(-h, h + 1):
                for z in range(-h, h + 1):
                    if max(abs(x), abs(z)) >= h - 1:
                        w.setze(x, y, z, s.wand(x, y, z, k / n) if max(abs(x), abs(z)) == h - 1 or y % sh else
                                s.sockel(x, y, z, k / n))
    ytop = 1 + n * sh
    # Treppe (Süd)
    for y in range(1, ytop):
        z = B0 - (y - 1) * (B0 - (B0 - (n - 1) * (B0 - 4) // n)) // (ytop - 1) + 1
        for x in range(-3, 4):
            if abs(x) == 3:
                w.setze(x, y, z, s.sockel(x, y, z, 0.6))
                w.setze(x, y + 1, z, s.sockel(x, y + 1, z, 0.6))
            else:
                w.setze(x, y, z, treppe(w, s.gesims, "north"))
            for yy in range(1, y):
                w.setze(x, yy, z, s.sockel(x, yy, z, 0.3))
    for sx in (-3, 3):
        w.setze(sx, 1, B0 + 2, w.b("chiseled_stone_bricks" if _stil(seed) == 0 else "chiseled_sandstone"))
        w.setze(sx, 2, B0 + 2, w.b("green_glazed_terracotta" if False else "emerald_block"))
    # Tempelhaus
    ht = max(3, (B0 - (n - 1) * (B0 - 4) // n) - 2)
    P.gebaeude(w, s.st, -ht, -ht, ht, ht, y0=ytop, etagen=1, eh=5, dach="flach", tuer="south", gauben=False,
               kamine=0, sockel_h=0)
    for x in range(-ht, ht + 1):
        for y in range(ytop + 6, ytop + 6 + _r(4 * u, 2)):
            if (x + y) % 2 == 0:
                w.setze(x, y, 0, s.wand(x, y, 0, 1))
    if _stil(seed) == 0:
        for (x, y, z), blk in list(w.bloecke.items()):
            if y > 2 and rng.random() < 0.035:
                for dx, dz, sd in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
                    if w.frei(x + dx, y, z + dz):
                        for k in range(int(1 + rng.random() * 5)):
                            if not w.frei(x + dx, y - k, z + dz) or y - k < 1:
                                break
                            w.setze(x + dx, y - k, z + dz, w.b("vine", **{q: q == sd for q in
                                                                         ("north", "east", "south", "west")}, up=False))
                        break
    hohl(w, 3)
    return w


# ============================================================================ 10 Waldschrein


def waldschrein(seed, g=0):
    """Waldschrein: kleines Heiligtum unter alten Bäumen – Torbogen, Steinlaternen, Opferstein, Wasserbecken
    und moosbedeckte Stufen."""
    import haeuser as H_
    w = _welt(seed)
    s = stil(w, seed, "moos", "kalk")
    u = U[g]
    a = _r(3 * u + 2, 2)
    gelaende(w, a + _r(10 * u, 6), art="wald", dichte=1.2)
    P.gebaeude(w, s.st, -a, -a, a, a, y0=1, etagen=1, eh=_r(3 * u + 2, 4), dach="walm", ue=2, steil=True,
               tuer="south", gauben=False, kamine=0)
    for k in range(_r(6 * u + 3, 4)):
        z = a + 2 + k
        for x in (-1, 0, 1):
            w.setze(x, 0, z, w.b("mossy_stone_bricks") if (x + k) % 2 else w.b("stone_bricks"))
        if k % 3 == 1:
            for sx in (-2, 2):
                for y in range(1, 3):
                    w.setze(sx, y, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                          west="none", waterlogged=False))
                w.setze(sx, 3, z, w.b("lantern", hanging=False, waterlogged=False))
    zt = a + 2 + _r(6 * u + 3, 4)
    for y in range(1, 5):
        for sx in (-2, 2):
            w.setze(sx, y, zt, w.b(f"stripped_{s.holz}_log", axis="y"))
    for x in range(-3, 4):
        w.setze(x, 5, zt, w.b(f"{s.holz}_planks") if abs(x) < 3 else w.b(f"{s.holz}_slab", type="bottom",
                                                                          waterlogged=False))
    for i in range(3):
        H_.baum(w, -a - 4 - i * 2, -a + i * 3, "dark_oak" if i % 2 else "oak", H=8)
    hohl(w, 2)
    return w


# ============================================================================ 11 Glockenturm


def glockenturm(seed, g=1):
    """Freistehender Campanile: schlanker Turm mit Geschossgesimsen, offenen Schallarkaden, Glocken und
    spitzem Helm, am Fuß eine kleine Loggia."""
    w = _welt(seed)
    s = stil(w, seed, "backstein", "marmor")
    u = U[g]
    a = _r(2.5 * u + 1.5, 2)
    H = _r(28 * u + 10)
    gelaende(w, a + 8, art="wiese")
    P.turm(w, s.st, 0, 0, 1, H, a + 0.3, form="eckig", dach="pyramide", krone=False, fahne=None, fenster=8)
    for y in range(H - 6, H - 1):
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                if max(abs(x), abs(z)) == a and not (abs(x) == a and abs(z) == a) and abs(x) + abs(z) < 2 * a - 1:
                    w.bloecke.pop((x, y, z), None)
    w.setze(0, H - 2, 0, w.b("bell", attachment="ceiling", facing="north", powered=False))
    w.setze(0, H - 1, 0, s.wand(0, H - 1, 0, 1))
    hohl(w, 2)
    return w


# ============================================================================ 12 Baptisterium


def baptisterium(seed, g=1):
    """Achteckiges Baptisterium mit Marmorinkrustation in zwei Farben, Kuppeldach, Laterne und Taufbecken."""
    w = _welt(seed)
    u = U[g]
    st = _stil(seed)
    hell = Mat(w, ["calcite", "smooth_quartz", "polished_diorite", "white_concrete"], kontrast=0.4)
    dunkel = Mat(w, ["green_terracotta", "dark_prismarine", "polished_deepslate"] if st == 0 else
                 ["red_terracotta", "polished_granite", "red_nether_bricks"], kontrast=0.4)
    s = stil(w, seed, "marmor", "marmor")
    R = 5 * u + 3
    H = _r(9 * u + 4, 7)
    gelaende(w, _r(R + 8), art="wiese")
    for y in range(1, H + 1):
        for x in range(-int(R) - 1, int(R) + 2):
            for z in range(-int(R) - 1, int(R) + 2):
                d = max(abs(x), abs(z), (abs(x) + abs(z)) / 1.42)
                if R - 1 < d <= R:
                    band = y % 4 == 0 or ((x + z) % 4 == 0 and y % 4 in (1, 2, 3) and (abs(x) + abs(z)) % 2 == 0)
                    fen = y in range(3, H - 2) and (abs(x) < 1 or abs(z) < 1)
                    w.setze(x, y, z, s.g(x, y, z, y / H) if fen else (dunkel(x, y, z, 0.5) if band else hell(x, y, z, 0.5)))
                elif d <= R - 1 and y == 1:
                    w.setze(x, 0, z, w.b("polished_diorite") if (x + z) % 2 else dunkel(x, 0, z, 0.5))
    for k in range(int(R) + 2):
        r = (R + 0.5) * math.cos(k / (R + 1) * math.pi / 2)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = max(abs(x), abs(z), (abs(x) + abs(z)) / 1.42)
                if r - 1 < d <= r:
                    w.setze(x, H + 1 + k, z, s.dach.voll(x, H + 1 + k, z))
    w.setze(0, H + int(R) + 3, 0, w.b("lantern", hanging=False, waterlogged=False))
    for x, z in kreisrand(1.5):
        w.setze(x, 1, z, w.b("quartz_slab", type="bottom", waterlogged=False))
    w.setze(0, 1, 0, w.b("water", level=0))
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(0, y, int(R), w.b("dark_oak_door", facing="south", half=half, hinge="left", open=False, powered=False))
    hohl(w, 2)
    return w


# ============================================================================ 13 Wallfahrtskapelle


def wallfahrtskapelle(seed, g=1):
    """Wallfahrtskapelle auf einem Hügel: lange Treppe mit Stationen und Laternen, kleine Kapelle mit Turm."""
    w = _welt(seed)
    s = stil(w, seed, "kalk", "rot")
    u = U[g]
    Hh = _r(8 * u + 4, 6)
    R = _r(14 * u + 6)
    fels = Mat(w, ["grass_block", "dirt", "coarse_dirt", "stone", "andesite"], kontrast=1.2)
    r_n = Rauschen(w, 5)
    for x, z in scheibe(R):
        d = math.hypot(x, z) / R
        hh = Hh * (1 - d ** 1.6) * (0.85 + 0.3 * r_n(x, 0, z))
        for y in range(0, int(hh) + 1):
            w.setze(x, y, z, w.b("grass_block", snowy=False) if y == int(hh) else w.b("dirt") if y > hh - 3 else
                    w.b("stone"))
    L, B = _r(4 * u + 2, 3), _r(2.5 * u + 1.5, 2)
    halle(w, s, -L, -B, L, B, Hh + 1, _r(5 * u + 3, 4), achse="x", fialen=False)
    P.turm(w, s.st, -L - 1, 0, Hh + 1, _r(10 * u + 4), B, form="eckig", dach="zwiebel", krone=False, fahne=None)
    for k in range(R - 2):
        x = L + 2 + k
        y = Hh - int(k * Hh / (R - L - 2)) if k < R - L - 2 else 0
        for z in (-1, 0, 1):
            w.setze(x, y, z, treppe(w, s.gesims, "west"))
            for yy in range(y + 1, y + 4):
                w.bloecke.pop((x, yy, z), None)
        if k % 4 == 0:
            w.setze(x, y + 1, 2, w.b("cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
                                     waterlogged=False))
            w.setze(x, y + 2, 2, w.b("lantern", hanging=False, waterlogged=False))
    hohl(w, 2)
    return w


# ============================================================================ 14 Tempelruine


def tempelruine(seed, g=2):
    """Antike Tempelruine: umgestürzte und stehende Säulen, Gebälkreste, zerbrochene Statue, Gras und Efeu."""
    w = saeulentempel(seed, g)
    rng = w.rng
    betroffen = set(b for b in w.bloecke.values() if b)
    zerfall(w, betroffen, Rauschen(w, 2.5), 30 * U[g], staerke=0.95, boden=5)
    for i in range(int(4 * U[g]) + 2):
        x0, z0 = int((rng.random() - 0.5) * 30 * U[g]), int((rng.random() - 0.5) * 20 * U[g])
        L = int(4 + rng.random() * 6 * U[g])
        ax = rng.random() < 0.5
        for k in range(L):
            p = (x0 + k, 1, z0) if ax else (x0, 1, z0 + k)
            w.setze(*p, w.b("quartz_pillar", axis="x" if ax else "z"))
    for (x, y, z), blk in list(w.bloecke.items()):
        if w.frei(x, y + 1, z) and rng.random() < 0.25 and y >= 1:
            w.setze(x, y + 1, z, w.b("moss_carpet") if rng.random() < 0.5 else w.b("grass"))
    return w


# ============================================================================ 15 Steinkreis-Heiligtum


def steinkreis(seed, g=1):
    """Steinkreis-Heiligtum: zwei Ringe aus Menhiren mit Decksteinen, Altarstein in der Mitte,
    Feuerschalen und ein Kreis aus Blumen."""
    w = _welt(seed)
    u = U[g]
    st = _stil(seed)
    M = Mat(w, ["stone", "andesite", "tuff", "mossy_cobblestone", "cobblestone", "diorite"] if st == 0 else
            ["blackstone", "basalt", "tuff", "deepslate", "obsidian"], kontrast=1.3)
    R = 10 * u + 4
    gelaende(w, _r(R + 8), art="wiese" if st == 0 else "stein", dichte=0.8)
    n = 12 if u > 0.8 else 8
    H = _r(6 * u + 3, 4)
    for ring, rr, hh in ((0, R, H), (1, R * 0.55, int(H * 1.3))):
        for i in range(n if ring == 0 else 5):
            a = i / (n if ring == 0 else 5) * 2 * math.pi
            x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
            for y in range(1, hh + 1):
                for dx in (0, 1):
                    for dz in (0, 1):
                        if y < hh or (dx + dz) < 2:
                            w.setze(x + dx, y, z + dz, M(x + dx, y, z + dz, y / hh))
            if ring == 0 and i % 2 == 0:
                a2 = (i + 1) / n * 2 * math.pi
                x2, z2 = round(math.cos(a2) * rr), round(math.sin(a2) * rr)
                for k in range(11):
                    t = k / 10
                    w.setze(round(x + (x2 - x) * t), hh + 1, round(z + (z2 - z) * t), M(x, hh + 1, z, 1))
    for x in range(-2, 3):
        for z in range(-1, 2):
            w.setze(x, 1, z, M(x, 1, z, 0.5))
    w.setze(0, 2, 0, w.b("candle", candles=4, lit=True, waterlogged=False) if False else w.b("lantern", hanging=False,
                                                                                          waterlogged=False))
    for x, z in kreisrand(R * 0.8):
        if w.frei(x, 1, z) and (x + z) % 2 == 0:
            w.setze(x, 1, z, w.b("allium" if st == 0 else "wither_rose"))
    hohl(w, 2)
    return w


# ============================================================================ 16 Pylontempel


def pylontempel(seed, g=2):
    """Wüstentempel mit Pylon: zwei mächtige geböschte Tortürme, Obelisken, Sphingenallee, Säulenhof mit
    Papyrussäulen und ein Sanktuar."""
    w = _welt(seed)
    s = stil(w, seed, "sand", "rot")
    u = U[g]
    hb = _r(7 * u + 3, 5)
    H = _r(14 * u + 5, 9)
    L = _r(14 * u + 6)
    gelaende(w, L + 14, art="sand", dichte=0.4)
    for sx in (-1, 1):
        for y in range(1, H + 1):
            sh = int((y - 1) * 0.18)
            x0, x1 = (2 + sh, 2 + hb * 2 - sh) if sx > 0 else (-2 - hb * 2 + sh, -2 - sh)
            for x in range(min(x0, x1), max(x0, x1) + 1):
                for z in range(-3 + sh // 2, 4 - sh // 2):
                    rnd = x in (x0, x1) or z in (-3 + sh // 2, 3 - sh // 2)
                    if rnd:
                        b = w.b("blue_terracotta") if y % 7 == 0 else s.wand(x, y, z, y / H)
                        w.setze(x, y, z, b)
    for x in range(-2, 3):
        for y in range(1, int(H * 0.6)):
            for z in range(-1, 2):
                if abs(x) == 2:
                    w.setze(x, y, z, s.sockel(x, y, z, 0.4))
        w.setze(x, int(H * 0.6), 0, w.b("gold_block") if x == 0 else s.wand(x, int(H * 0.6), 0, 0.8))
    # Hof mit Säulen
    for x in range(-hb, hb + 1, 3):
        for z in range(-L, -4, 3):
            if abs(x) == hb or x == 0 and False:
                pass
    saeulenreihe(w, s, [(x, z) for x in (-hb + 1, hb - 1) for z in range(-L, -4, 3)], 1, _r(8 * u + 3, 6),
                 mat="cut_sandstone" if _stil(seed) == 0 else "cut_red_sandstone",
                 kapitell="lime_terracotta" if False else "chiseled_sandstone")
    P.gebaeude(w, s.st, -hb + 2, -L - _r(6 * u + 3, 5), hb - 2, -L - 1, y0=1, etagen=1, eh=_r(6 * u + 3, 5),
               dach="flach", tuer="south", gauben=False, kamine=0)
    # Obelisken und Sphingen
    for sx in (-1, 1):
        x = sx * (hb * 2 + 4)
        for y in range(1, _r(H * 1.1)):
            w.setze(x, y, 6, s.wand(x, y, 6, 0.6))
        w.setze(x, _r(H * 1.1), 6, w.b("gold_block"))
        for z in range(8, 8 + _r(10 * u, 6), 4):
            for dx in (-1, 0, 1):
                for dz in (0, 1, 2):
                    w.setze(sx * 4 + dx, 1, z + dz, s.sockel(sx * 4 + dx, 1, z + dz, 0.4))
            w.setze(sx * 4, 2, z, s.wand(sx * 4, 2, z, 0.7))
            w.setze(sx * 4, 3, z, s.wand(sx * 4, 3, z, 0.8))
    hohl(w, 2)
    return w


# ============================================================================ 17 Mausoleum


def mausoleum(seed, g=1):
    """Mausoleum: quadratischer Grabbau mit Säulenvorhalle, Kuppel, Bronzetüren, Urnen und Zypressen."""
    import wald
    w = _welt(seed)
    s = stil(w, seed, "marmor", "tief")
    u = U[g]
    a = _r(5 * u + 3, 4)
    H = _r(7 * u + 3, 6)
    gelaende(w, a + 9, art="wiese")
    for k in range(2):
        for x in range(-a - 2 + k, a + 3 - k):
            for z in range(-a - 2 + k, a + 3 - k):
                w.setze(x, 1 + k, z, s.sockel(x, 1 + k, z, 0.2))
    P.gebaeude(w, s.st, -a, -a, a, a, y0=3, etagen=1, eh=H, dach="flach", tuer="south", gauben=False, kamine=0,
               sockel_h=0, pilaster=2)
    for k in range(a + 1):
        r = (a + 0.5) * math.cos(k / (a + 1) * math.pi / 2)
        for x, z in kreisrand(max(0.4, r)):
            w.setze(x, 3 + H + 1 + k, z, s.dach.voll(x, 3 + H + 1 + k, z))
    for sx in (-2, 2):
        for y in range(3, 3 + H):
            w.setze(sx, y, a + 2, w.b("quartz_pillar", axis="y") if s.gesims == "quartz" else w.b("polished_deepslate"))
    for x in range(-3, 4):
        w.setze(x, 3 + H, a + 1, s.wand(x, 3 + H, a + 1, 1))
        w.setze(x, 3 + H, a + 2, s.wand(x, 3 + H, a + 2, 1))
    for sx in (-a - 4, a + 4):
        for sz in (-a, a):
            einfuegen(w, wald.schlanke_fichte(int(w.rng.integers(1, 10 ** 6)), H=_r(9 * u + 4), art="spruce"), sx, 0, sz)
    for sx in (-a - 1, a + 1):
        w.setze(sx, 3, a + 2, w.b("decorated_pot", facing="north", waterlogged=False) if False else w.b("flower_pot"))
    hohl(w, 2)
    return w


# ============================================================================ 18 Dunkler Tempel


def dunkeltempel(seed, g=2):
    """Dunkler Tempel: schwarze Spitzbogenhalle mit roten Fenstern, Dornenzinnen, Seelenfeuern, finsteren
    Wächterpfeilern und einem Blutbecken vor dem Portal."""
    w = _welt(seed)
    s = stil(w, seed, "schwarz", "tief")
    u = U[g]
    L, B, H = _r(12 * u + 5), _r(4 * u + 2, 3), _r(12 * u + 5, 9)
    gelaende(w, L + 10, art="asche", dichte=0.6)
    halle(w, s, -L, -B, L, B, 1, H, achse="x")
    for sz in (-1, 1):
        P.turm(w, s.st, -L - 2, sz * (B + 2), 1, _r(H * 1.8), 2.0 * min(u, 1.7), form="achteck", dach="nadel",
               krone=False, fahne=None)
    apsis(w, s, L, 0, 1, B + 0.5, H, "x+")
    for x in range(-L - 12, -L - 2, 3):
        for sz in (-1, 1):
            z = sz * (B + 1)
            for y in range(1, 5):
                w.setze(x, y, z, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                                     west="none", waterlogged=False) if y < 4 else w.b("soul_campfire", lit=True,
                                                                                      signal_fire=False,
                                                                                      facing="north", waterlogged=False))
    for x in range(-L - 9, -L - 3):
        for z in range(-1, 2):
            w.setze(x, 0, z, w.b("crimson_nylium") if (x + z) % 2 else w.b("nether_wart_block"))
    hohl(w, 2)
    return w


# ============================================================================ 19 Zwergenschrein


def bergtempel(seed, g=2):
    """Bergtempel: in eine Felswand gehauene Fassade mit Säulen, Giebel und Treppe, Felsen ringsum,
    Fackeln und ein Gebetsfahnen-Seil."""
    w = _welt(seed)
    s = stil(w, seed, "rot", "tief")
    u = U[g]
    W, H, D = _r(18 * u + 6), _r(20 * u + 8), _r(12 * u + 4)
    fels = Mat(w, ["stone", "andesite", "tuff", "granite", "stone", "diorite"], kontrast=1.3)
    r_n = Rauschen(w, 6)
    for x in range(-W, W + 1):
        for z in range(-D, 1):
            hh = H * (1 - (abs(x) / W) ** 2) * (0.7 + 0.4 * r_n(x, 0, z)) + 4
            for y in range(0, int(hh) + 1):
                w.setze(x, y, z, fels(x, y, z, y / H))
    fb = _r(W * 0.55)
    fh = _r(H * 0.75)
    for x in range(-fb, fb + 1):
        for y in range(1, fh + 1):
            w.setze(x, y, 0, s.wand(x, y, 0, y / fh))
            w.setze(x, y, 1, w.b("air")) if False else None
    saeulenreihe(w, s, [(x, 2) for x in range(-fb + 1, fb, 3)], 1, fh - 3,
                 mat="cut_red_sandstone" if _stil(seed) == 0 else "polished_deepslate",
                 kapitell="chiseled_red_sandstone" if _stil(seed) == 0 else "chiseled_deepslate")
    for x in range(-fb, fb + 1):
        for z in (1, 2, 3):
            w.setze(x, fh - 2, z, s.wand(x, fh - 2, z, 0.9))
    giebel_dreieck(w, s, -fb, fb, 1, fh - 1, "chiseled_red_sandstone" if _stil(seed) == 0 else "polished_deepslate",
                   s.gesims, tief=3)
    for y in range(1, 6):
        for x in range(-2, 3):
            w.bloecke.pop((x, y, 0), None)
            w.setze(x, y, -1, w.b("black_concrete"))
    for k in range(4):
        for x in range(-fb - k, fb + k + 1):
            w.setze(x, 0 - 0, 4 + k, treppe(w, s.gesims, "north") if k < 3 else s.sockel(x, 0, 4 + k, 0.2))
    rng = w.rng
    for x in range(-fb - 4, fb + 5):
        y = fh + 3 - int(abs(x) / (fb + 4) * 4)
        w.setze(x, y, 4, w.b(["red_wool", "yellow_wool", "blue_wool", "white_wool", "green_wool"][(x // 2) % 5])
                if x % 2 == 0 else w.b("chain", axis="x", waterlogged=False) if False else
                w.b(["red_carpet", "yellow_carpet"][x % 2]) if False else w.b("tripwire", attached=False,
                                                                                disarmed=False, north=False,
                                                                                south=False, east=True, west=True,
                                                                                powered=False))
    hohl(w, 3)
    return w


# ============================================================================ 20 Sternenkapelle


def sternenkapelle(seed, g=1):
    """Sternenkapelle: kleiner Rundbau ganz aus Buntglas zwischen schlanken Rippen, mit Sternkuppel
    und Leuchtkristall – nachts eine leuchtende Laterne in der Landschaft."""
    w = _welt(seed)
    s = stil(w, seed, "marmor", "tief")
    u = U[g]
    R = 4 * u + 3
    H = _r(8 * u + 4, 6)
    gelaende(w, _r(R + 8), art="wiese", dichte=1.3)
    for x, z in scheibe(R + 1):
        w.setze(x, 1, z, s.sockel(x, 1, z, 0.3))
    for y in range(2, 2 + H):
        for x, z in kreisrand(R):
            a = math.atan2(z, x)
            rippe = abs(math.sin(a * 4)) < 0.25
            w.setze(x, y, z, s.wand(x, y, z, 0.8) if rippe or y == 2 else s.g(x, y, z, (y - 2) / H))
    Sk = Skulptur(w, 1.0)
    Sk.mat("g", lambda x, y, z, lx, ly, lz: s.g(x, y, z, 0.5 + ly / (2 * R)))
    Sk.mat("r", lambda x, y, z, lx, ly, lz: s.wand(x, y, z, 0.9))
    Sk.plus(lambda X, Y, Z: (np.abs(np.sqrt(X * X + Y * Y * 0.8 + Z * Z) - R) < 0.6) & (Y >= 0), "g")
    for i in range(4):
        a = i / 4 * math.pi
        Sk.plus(lambda X, Y, Z, a=a: (np.abs(np.sqrt(X * X + Y * Y * 0.8 + Z * Z) - R) < 0.7)
                & (np.abs(-X * math.sin(a) + Z * math.cos(a)) < 0.5) & (Y >= 0), "r")
    Sk.rendern((-R - 2, 0, -R - 2), (R + 2, R * 1.2 + 2, R + 2), versatz=(0.5, 2 + H, 0.5))
    for y in range(2, 2 + H + int(R * 0.6)):
        if y % 3 == 0:
            w.setze(0, y, 0, w.b("end_rod", facing="up"))
    w.setze(0, 2, 0, w.b("amethyst_block"))
    w.setze(0, 3, 0, w.b("amethyst_cluster", facing="up", waterlogged=False))
    for y, half in ((2, "lower"), (3, "upper")):
        w.setze(0, y, round(R), w.b(f"{s.holz}_door", facing="south", half=half, hinge="left", open=False,
                                    powered=False))
    hohl(w, 2)
    return w


KATHEDRALEN = {
    "kathedrale": ("Gotische Kathedrale", kathedrale),
    "dorfkapelle": ("Dorfkirche", dorfkirche),
    "basilika": ("Romanische Basilika", basilika),
    "kuppeltempel": ("Kuppelkirche", kuppelkirche),
    "kloster": ("Kloster mit Kreuzgang", kloster),
    "abteiruine": ("Abteiruine", abteiruine),
    "saeulentempel": ("Säulentempel", saeulentempel),
    "rundkirche": ("Rundtempel", rundtempel),
    "stufentempel": ("Stufentempel", stufentempel),
    "wegschrein": ("Waldschrein", waldschrein),
    "glockenturm": ("Glockenturm", glockenturm),
    "baptisterium": ("Baptisterium", baptisterium),
    "wallfahrtskapelle": ("Wallfahrtskapelle", wallfahrtskapelle),
    "tempelruine": ("Tempelruine", tempelruine),
    "steinkreis": ("Steinkreis-Heiligtum", steinkreis),
    "pylontempel": ("Pylontempel", pylontempel),
    "mausoleum": ("Mausoleum", mausoleum),
    "dunkeltempel": ("Dunkler Tempel", dunkeltempel),
    "bergtempel": ("Felsentempel", bergtempel),
    "sternenkapelle": ("Sternenkapelle", sternenkapelle),
}

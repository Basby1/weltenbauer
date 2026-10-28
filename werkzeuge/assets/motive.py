"""Motiv-Baukasten: wiederverwendbare, parametrische Bauwerke, die mit einem Thema (Materialsatz) eingefärbt
werden. Damit bekommt jede Kategorie viele unterschiedliche Motive.

Ein Motiv ist eine Funktion motiv(w, T, u, **param) und baut am Ursprung (Anker = Boden in der Mitte).
`vorlage(motiv, thema, **param)` macht daraus eine Vorlagenfunktion (seed, g) mit 4 Größen und 2 Stilen."""

from __future__ import annotations

import math

import numpy as np

from lib import Verlauf, Welt, laub, ueberwuchern
from skulptur import (Skulptur, dreh_y, ell, kap, kegel, kreisrand, platte, scheibe, spiegel_x, torus, treppe,
                      verbinde, zur_mitte)

U = [0.6, 1.0, 1.7, 2.8]


def _r(v, mind=1):
    return max(mind, int(round(v)))


# ============================================================================ Thema

class Thema:
    """Materialsatz. Alle Felder sind Blocknamen oder Listen davon; Verläufe werden pro Welt gebaut."""

    def __init__(self, name, stein, akzent="gold_block", holz="spruce", dach=("deepslate_tile", "deepslate_tiles"),
                 glas="glass", licht="lantern", boden=("grass_block",), pflanzen=("poppy", "dandelion", "grass"),
                 metall=("gold_block",), stoff=("red_wool", "white_wool"), figur=None, treppe="stone_brick",
                 kristall=("amethyst_block", "purple_stained_glass"), laub_art="oak", feuer="campfire", wasser=True,
                 deko=None):
        self.name = name
        self.stein_n = list(stein)
        self.akzent_n = akzent
        self.holz = holz
        self.dach_tr, self.dach_voll = dach
        self.glas_n = glas
        self.licht_n = licht
        self.boden_n = list(boden)
        self.pflanzen = list(pflanzen)
        self.metall_n = list(metall)
        self.stoff = list(stoff)
        self.figur_n = list(figur or stein)
        self.tr = treppe
        self.kristall_n = list(kristall)
        self.laub_art = laub_art
        self.feuer = feuer
        self.wasser = wasser
        self.deko = deko

    def binden(self, w):
        self.w = w
        self.stein = Verlauf(w, self.name + "S", self.stein_n)
        self.figur = Verlauf(w, self.name + "F", self.figur_n)
        self.metall = Verlauf(w, self.name + "M", self.metall_n)
        return self

    # Blöcke
    def s(self, x, y, z, v=None, H=12):
        v = (0.2 + (len(self.stein_n) - 1.2) * min(1, max(0, y) / max(1, H))) if v is None else v
        return self.stein(v + self.w.rng.random() * 0.9, x, y, z)

    def akzent(self):
        return self.w.b(self.akzent_n)

    def glas(self):
        n = self.glas_n
        if n.endswith("_pane"):
            return self.w.b(n, north=False, south=False, east=True, west=True, waterlogged=False)
        return self.w.b(n)

    def licht(self, haengend=False):
        n = self.licht_n
        if n.endswith("lantern"):
            return self.w.b(n, hanging=haengend, waterlogged=False)
        return self.w.b(n)

    def bodenblock(self):
        n = self.boden_n[int(self.w.rng.integers(len(self.boden_n)))]
        if n in ("grass_block", "podzol", "mycelium"):
            return self.w.b(n, snowy=False)
        return self.w.b(n)

    def treppe(self, facing, half="bottom"):
        return self.w.b(f"{self.tr}_stairs", facing=facing, half=half, shape="straight", waterlogged=False)

    def dachtreppe(self, facing, half="bottom"):
        return self.w.b(f"{self.dach_tr}_stairs", facing=facing, half=half, shape="straight", waterlogged=False)

    def pfosten(self, mat=None):
        return self.w.b(mat or f"{self.holz}_fence", north=False, south=False, east=False, west=False,
                        waterlogged=False)

    def feuerblock(self):
        return self.w.b(self.feuer, lit=True, signal_fire=False, facing="north", waterlogged=False)


def boden(w, T, r, cx=0, cz=0, streu=0.0):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, T.bodenblock(), ueberschreiben=False)
        if streu and w.frei(x, 1, z) and w.rng.random() < streu and T.pflanzen:
            p = T.pflanzen[int(w.rng.integers(len(T.pflanzen)))]
            w.setze(x, 1, z, w.b(p), ueberschreiben=False)


def vorlage(motiv, thema, boden_r=None, streu=0.06, **param):
    """thema: Funktion stil(0/1) -> Thema."""
    def f(seed, g=1):
        w = Welt(seed)
        w.anker = (0, 0, 0)
        stil = 0 if seed % 100 < 14 else 1
        T = thema(stil).binden(w)
        u = U[g]
        motiv(w, T, u, **param)
        if boden_r is not None:
            boden(w, T, boden_r * u + 3, streu=streu)
        else:
            lo, hi = w.grenzen() if w.bloecke else (np.array([0, 0, 0]), np.array([0, 0, 0]))
            r = max(abs(lo[0]), abs(hi[0]), abs(lo[2]), abs(hi[2])) + 2
            boden(w, T, r * 0.9, streu=streu)
        return w
    f.__doc__ = motiv.__doc__
    return f


# ============================================================================ Dächer

def dach_kegel(w, T, cx, cz, y0, R, H=None, mat=None):
    H = H or _r(R * 2.4, 3)
    for k in range(H + 1):
        r = (R + 0.8) * (1 - k / (H + 1)) ** 1.1
        for x, z in kreisrand(max(0.3, r), cx, cz):
            w.setze(x, y0 + k, z, w.b(mat or T.dach_voll))
    w.setze(cx, y0 + H + 1, cz, T.akzent())
    return y0 + H + 1


def dach_pyramide(w, T, x0, z0, x1, z1, y0, ue=1):
    k = 0
    while True:
        ax, bx, az, bz = x0 - ue + k, x1 + ue - k, z0 - ue + k, z1 + ue - k
        if ax > bx or az > bz:
            break
        for x in range(ax, bx + 1):
            for z in range(az, bz + 1):
                if not (x in (ax, bx) or z in (az, bz)):
                    continue
                if ax == bx or az == bz:
                    w.setze(x, y0 + k, z, w.b(T.dach_voll))
                elif z == az:
                    w.setze(x, y0 + k, z, T.dachtreppe("south"))
                elif z == bz:
                    w.setze(x, y0 + k, z, T.dachtreppe("north"))
                elif x == ax:
                    w.setze(x, y0 + k, z, T.dachtreppe("east"))
                else:
                    w.setze(x, y0 + k, z, T.dachtreppe("west"))
        k += 1
    return y0 + k


def dach_sattel(w, T, x0, z0, x1, z1, y0, ue=1, entlang_x=None):
    if entlang_x is None:
        entlang_x = (x1 - x0) >= (z1 - z0)
    k = 0
    while True:
        y = y0 + k
        if entlang_x:
            a, b = z0 - ue + k, z1 + ue - k
            if a > b:
                break
            for x in range(x0 - ue, x1 + ue + 1):
                if a == b:
                    w.setze(x, y, a, w.b(T.dach_voll))
                else:
                    w.setze(x, y, a, T.dachtreppe("south"))
                    w.setze(x, y, b, T.dachtreppe("north"))
            for x in (x0, x1):
                for z in range(max(a + 1, z0), min(b, z1 + 1)):
                    w.setze(x, y, z, T.s(x, y, z, v=len(T.stein_n) - 1.5))
        else:
            a, b = x0 - ue + k, x1 + ue - k
            if a > b:
                break
            for z in range(z0 - ue, z1 + ue + 1):
                if a == b:
                    w.setze(a, y, z, w.b(T.dach_voll))
                else:
                    w.setze(a, y, z, T.dachtreppe("east"))
                    w.setze(b, y, z, T.dachtreppe("west"))
            for z in (z0, z1):
                for x in range(max(a + 1, x0), min(b, x1 + 1)):
                    w.setze(x, y, z, T.s(x, y, z, v=len(T.stein_n) - 1.5))
        k += 1
    return y0 + k


def dach_kuppel(w, T, cx, cz, y0, R, mat=None, hoehe=1.0):
    vm = Verlauf(w, T.name + "K", [mat] if mat else [T.dach_voll])
    for x in range(cx - int(R) - 1, cx + int(R) + 2):
        for z in range(cz - int(R) - 1, cz + int(R) + 2):
            for y in range(0, int(R * hoehe) + 2):
                d = ((x - cx) / (R + 0.4)) ** 2 + ((z - cz) / (R + 0.4)) ** 2 + (y / (R * hoehe + 0.4)) ** 2
                if 0.62 < d <= 1:
                    w.setze(x, y0 + y, z, vm(0.5, x, y, z))
    w.setze(cx, y0 + int(R * hoehe) + 1, cz, T.akzent())
    return y0 + int(R * hoehe) + 1


def dach_zwiebel(w, T, cx, cz, y0, R, mat=None):
    H = R * 2.6
    for y in range(int(H) + 1):
        t = y / H
        r = R * 1.25 * math.sin(math.pi * min(1, t * 1.15)) ** 0.8 if t < 0.87 else R * 0.25 * (1 - (t - 0.87) / 0.13)
        for x, z in scheibe(max(0.3, r), cx, cz):
            w.setze(x, y0 + y, z, w.b(mat or T.dach_voll))
    w.setze(cx, y0 + int(H) + 1, cz, T.akzent())
    return y0 + int(H) + 1


def zinnen_rund(w, T, cx, cz, y, R):
    for x, z in kreisrand(R + 1, cx, cz):
        w.setze(x, y - 1, z, T.treppe(zur_mitte(x, z, cx, cz), "top"))
    for x, z in scheibe(R + 1, cx, cz):
        w.setze(x, y, z, T.s(x, y, z, v=1.5))
    for i, (x, z) in enumerate(kreisrand(R + 1, cx, cz)):
        if i % 2 == 0:
            w.setze(x, y + 1, z, T.s(x, y + 1, z, v=1.5))
    return y + 1


# ============================================================================ Grundformen

def schaft(w, T, cx, cz, y0, H, R, form="rund", fenster=5, hohl=True, verjuengung=0.0):
    """Turmschaft: rund, eckig oder achteckig, mit Fensterreihen."""
    for y in range(y0, y0 + H):
        r = R * (1 - verjuengung * (y - y0) / max(1, H))
        n = int(r) + 2
        for x in range(cx - n, cx + n + 1):
            for z in range(cz - n, cz + n + 1):
                dx, dz = x - cx, z - cz
                if form == "rund":
                    d = math.hypot(dx, dz)
                elif form == "eckig":
                    d = max(abs(dx), abs(dz))
                else:
                    d = max(abs(dx), abs(dz), (abs(dx) + abs(dz)) / 1.42)
                if d > r + 0.45:
                    continue
                rand = d > r - 0.6
                if rand:
                    a = math.atan2(dz, dx)
                    fen = fenster and (y - y0) % fenster == fenster // 2 + 1 and y > y0 + 1 and \
                        (abs(math.sin(2 * a)) < 0.2 if form == "rund" else (dx == 0 or dz == 0))
                    w.setze(x, y, z, T.glas() if fen else T.s(x, y, z, H=H + y0))
                elif not hohl or y == y0:
                    w.setze(x, y, z, T.s(x, y, z, H=H + y0))
    return y0 + H


def quader(w, T, x0, z0, x1, z1, y0, H, fenster=3, tuer=True, hohl=True):
    for y in range(y0, y0 + H):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                rand = x in (x0, x1) or z in (z0, z1)
                if rand:
                    t = (x - x0) if z in (z0, z1) else (z - z0)
                    ecke = x in (x0, x1) and z in (z0, z1)
                    fen = fenster and not ecke and (y - y0) % 4 in (1, 2) and t % fenster == fenster // 2 and y > y0
                    w.setze(x, y, z, T.glas() if fen else T.s(x, y, z, H=H + y0))
                elif y == y0 or not hohl:
                    w.setze(x, y, z, T.s(x, y, z, v=0.6))
    if tuer:
        mx = (x0 + x1) // 2
        for y, half in ((y0 + 1, "lower"), (y0 + 2, "upper")):
            w.setze(mx, y, z1, w.b(f"{T.holz}_door", facing="south", half=half, hinge="left", open=False, powered=False))
    return y0 + H


def saeule(w, T, x, z, y0, H, kapitell=True, mat=None):
    for y in range(y0, y0 + H):
        w.setze(x, y, z, w.b(mat) if mat else T.s(x, y, z, v=len(T.stein_n) - 1.5))
    if kapitell:
        w.setze(x, y0 + H, z, T.akzent() if T.akzent_n != "gold_block" else T.s(x, y0 + H, z, v=len(T.stein_n) - 1))


def sockel_stufen(w, T, R, stufen, rund=True):
    for k in range(stufen):
        r = R - k
        if rund:
            for x, z in scheibe(r):
                w.setze(x, k, z, T.s(x, k, z, v=0.5 + k * 0.4))
        else:
            for x in range(-int(r), int(r) + 1):
                for z in range(-int(r), int(r) + 1):
                    rand = max(abs(x), abs(z)) == int(r)
                    w.setze(x, k, z, T.treppe(zur_mitte(x, z)) if rand and not (abs(x) == abs(z)) else
                            T.s(x, k, z, v=0.5 + k * 0.4))
    return stufen


# ============================================================================ Motive

def m_turm(w, T, u, form="rund", dach="kegel", hoehe=16, breite=3.0, balkon=True, erker=False, verjuengung=0.0):
    """Turm mit Fensterreihen, optionalem Balkonkranz und Erkern; Dach als Kegel, Pyramide, Kuppel,
    Zwiebel oder Zinnen."""
    R = breite * u + 1.2
    H = _r(hoehe * u + 4, 6)
    schaft(w, T, 0, 0, 0, H, R, form=form, verjuengung=verjuengung)
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(0, y, int(R), w.b(f"{T.holz}_door", facing="south", half=half, hinge="left", open=False, powered=False))
    w.setze(1, 1, int(R) + 1, T.licht())
    if balkon:
        yb = int(H * 0.62)
        for x, z in kreisrand(R + 1.4):
            w.setze(x, yb, z, T.treppe(zur_mitte(x, z), "top"))
        verbinde(w, [(x, yb + 1, z) for x, z in kreisrand(R + 1.4)], f"{T.holz}_fence")
    if erker:
        for a in (0.8, 2.6, 4.4):
            ex, ez = round(math.cos(a) * (R + 1)), round(math.sin(a) * (R + 1))
            schaft(w, T, ex, ez, int(H * 0.45), int(H * 0.35), max(1.2, R * 0.38), form="rund", fenster=3)
            dach_kegel(w, T, ex, ez, int(H * 0.8), max(1.2, R * 0.38))
    Rt = R * (1 - verjuengung)
    if dach == "kegel":
        dach_kegel(w, T, 0, 0, H, Rt)
    elif dach == "pyramide":
        dach_pyramide(w, T, -int(Rt), -int(Rt), int(Rt), int(Rt), H, ue=1)
    elif dach == "kuppel":
        dach_kuppel(w, T, 0, 0, H, Rt + 0.5)
    elif dach == "zwiebel":
        dach_zwiebel(w, T, 0, 0, H, Rt * 0.9)
    else:
        zinnen_rund(w, T, 0, 0, H, Rt)
        w.setze(0, H + 1, 0, T.feuerblock())


def m_turmgruppe(w, T, u, anzahl=4, form="rund", dach="kegel"):
    """Gruppe verschieden hoher Türme, die zusammenwachsen – mit Brückengängen."""
    rng = w.rng
    spitzen = []
    for i in range(anzahl):
        a = i * 2 * math.pi / anzahl
        d = 0 if i == 0 else (3.5 * u + 2.5)
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        R = (2.6 if i == 0 else 1.4 + 0.6 * rng.random()) * u + 1
        H = _r((20 if i == 0 else 9 + 7 * rng.random()) * u + 4, 6)
        schaft(w, T, cx, cz, 0, H, R, form=form)
        if dach == "kegel":
            dach_kegel(w, T, cx, cz, H, R)
        elif dach == "zwiebel":
            dach_zwiebel(w, T, cx, cz, H, R * 0.9)
        else:
            dach_kuppel(w, T, cx, cz, H, R + 0.4)
        spitzen.append((cx, cz, H))
    for (cx, cz, H) in spitzen[1:]:
        yb = int(min(H, spitzen[0][2]) * 0.6)
        for t in np.linspace(0, 1, 2 * int(math.hypot(cx, cz)) + 2):
            w.setze(round(cx * t), yb, round(cz * t), T.s(0, yb, 0, v=1.5), ueberschreiben=False)


def m_halle(w, T, u, laenge=14, breite=7, hoehe=6, dach="sattel", saeulen=True, turm=False):
    """Lange Halle mit Säulenreihe davor, Fensterreihen und Sattel- oder Walmdach; optional Glockenturm."""
    L, B = _r(laenge * u + 4, 6), _r(breite * u + 3, 4)
    H = _r(hoehe * u + 2, 4)
    x0, z0, x1, z1 = -L // 2, -B // 2, L // 2, B // 2
    quader(w, T, x0, z0, x1, z1, 0, H)
    if dach == "sattel":
        dach_sattel(w, T, x0, z0, x1, z1, H, ue=1)
    else:
        dach_pyramide(w, T, x0, z0, x1, z1, H, ue=1)
    if saeulen:
        for x in range(x0, x1 + 1, 3):
            saeule(w, T, x, z1 + 2, 1, H - 1)
        for x in range(x0 - 1, x1 + 2):
            w.setze(x, H, z1 + 1, T.s(x, H, z1 + 1, v=2))
            w.setze(x, H, z1 + 2, T.s(x, H, z1 + 2, v=2))
            w.setze(x, 0, z1 + 1, T.s(x, 0, z1 + 1, v=1))
            w.setze(x, 0, z1 + 2, T.s(x, 0, z1 + 2, v=1))
    if turm:
        R = 1.6 * u + 1
        schaft(w, T, x0, z0, 0, H + _r(8 * u, 5), R, form="eckig")
        dach_pyramide(w, T, x0 - int(R), z0 - int(R), x0 + int(R), z0 + int(R), H + _r(8 * u, 5), ue=1)


def m_tempel(w, T, u, form="rechteck", saeulen_n=6, dach="giebel", hoehe=7):
    """Tempel auf Stufensockel: Säulenkranz, Cella und Giebel- oder Kuppeldach; rund oder rechteckig."""
    stufen = 2 + (u > 1.5)
    if form == "rund":
        R = 5 * u + 3
        sockel_stufen(w, T, R + stufen, stufen)
        H = _r(hoehe * u + 2, 4)
        for i, (x, z) in enumerate(kreisrand(R)):
            if i % max(2, int(len(kreisrand(R)) / saeulen_n / 1.0)) == 0:
                saeule(w, T, x, z, stufen, H)
        for x, z in kreisrand(R + 0.5):
            w.setze(x, stufen + H, z, T.s(x, stufen + H, z, v=2))
        schaft(w, T, 0, 0, stufen, H, R * 0.55, form="rund", fenster=0)
        dach_kuppel(w, T, 0, 0, stufen + H + 1, R)
    else:
        L, B = _r(7 * u + 3, 5), _r(4.5 * u + 2, 3)
        for k in range(stufen):
            for x in range(-L - stufen + k, L + stufen - k + 1):
                for z in range(-B - stufen + k, B + stufen - k + 1):
                    w.setze(x, k, z, T.s(x, k, z, v=0.6 + k * 0.3))
        H = _r(hoehe * u + 2, 4)
        for x in range(-L, L + 1, 2):
            for z in (-B, B):
                saeule(w, T, x, z, stufen, H)
        for z in range(-B + 2, B - 1, 2):
            for x in (-L, L):
                saeule(w, T, x, z, stufen, H)
        quader(w, T, -L + 2, -B + 2, L - 2, B - 2, stufen, H, fenster=0, tuer=False)
        for x in range(-L - 1, L + 2):
            for z in range(-B - 1, B + 2):
                w.setze(x, stufen + H, z, T.s(x, stufen + H, z, v=2))
        if dach == "kuppel":
            dach_kuppel(w, T, 0, 0, stufen + H + 1, B)
        else:
            dach_sattel(w, T, -L - 1, -B - 1, L + 1, B + 1, stufen + H + 1, ue=0, entlang_x=True)


def m_tor(w, T, u, breite=5, hoehe=8, tuerme=True, bogen=True):
    """Prächtiges Tor: Bogen mit Schlussstein, flankierende Türme und Laternen."""
    b = _r(breite * u * 0.5 + 1, 2)
    H = _r(hoehe * u + 3, 5)
    d = max(1, int(u))
    for x in range(-b - 2, b + 3):
        for y in range(1, H + 3):
            for z in range(-d, d + 1):
                innen = abs(x) <= b and (y < H - b // 2 or (bogen and (x / (b + 0.5)) ** 2 + ((y - H + b // 2) /
                                                                                            (b * 0.9 + 0.5)) ** 2 <= 1))
                if not innen:
                    w.setze(x, y, z, T.s(x, y, z, H=H))
    w.setze(0, H + 1, d + 1, T.akzent())
    for x in range(-b - 3, b + 4):
        w.setze(x, H + 3, 0, T.s(x, H + 3, 0, v=2) if (x % 2 == 0) else T.s(x, H + 2, 0, v=2))
    if tuerme:
        for s in (-1, 1):
            cx = s * (b + 3 + int(u))
            schaft(w, T, cx, 0, 0, H + _r(4 * u, 3), 1.6 * u + 1, form="rund")
            dach_kegel(w, T, cx, 0, H + _r(4 * u, 3), 1.6 * u + 1)
    for s in (-1, 1):
        w.setze(s * (b + 1), 1, d + 1, T.licht())


def m_bruecke(w, T, u, laenge=16, boegen=3, breite=3, gelaender="mauer"):
    """Steinbrücke mit mehreren Bögen über Wasser, Brüstung und Laternen."""
    L = _r(laenge * u + 6, 10)
    b = _r(breite * u * 0.5 + 0.5, 1)
    H = _r(4 * u + 2, 3)
    if T.wasser:
        for x in range(-L + 2, L - 1):
            for z in range(-b - 4, b + 5):
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("sand"))
    span = 2 * L / boegen
    for x in range(-L, L + 1):
        p = ((x + L) % span) / span
        unten = int(H * (1 - math.sin(math.pi * p) ** 0.6)) if abs(x) < L - 1 else 0
        for y in range(unten, H + 1):
            for z in range(-b, b + 1):
                w.setze(x, y, z, T.s(x, y, z, H=H + 2))
        for z in (-b - 1, b + 1):
            if gelaender == "mauer":
                w.setze(x, H + 1, z, T.s(x, H + 1, z, v=2))
            else:
                w.setze(x, H + 1, z, w.b(f"{T.holz}_fence", north=False, south=False, east=True, west=True,
                                         waterlogged=False))
        if x % 6 == 0:
            for z in (-b - 1, b + 1):
                w.setze(x, H + 2, z, T.licht())


def m_mauerring(w, T, u, ecken=6, radius=12, hoehe=6, turm_dach="kegel", innen=None):
    """Polygonaler Mauerring mit Wehrgang, Ecktürmen, Tor und optionalem Bau im Inneren."""
    R = radius * u + 4
    Hm = _r(hoehe * u + 2, 4)
    pts = [(round(math.cos(i * 2 * math.pi / ecken + math.pi / ecken) * R),
            round(math.sin(i * 2 * math.pi / ecken + math.pi / ecken) * R)) for i in range(ecken)]
    for i in range(ecken):
        (ax, az), (bx, bz) = pts[i], pts[(i + 1) % ecken]
        n = int(max(abs(bx - ax), abs(bz - az)))
        for k in range(n + 1):
            x, z = round(ax + (bx - ax) * k / max(1, n)), round(az + (bz - az) * k / max(1, n))
            for y in range(0, Hm + 1):
                w.setze(x, y, z, T.s(x, y, z, H=Hm))
            if k % 2 == 0:
                w.setze(x, Hm + 1, z, T.s(x, Hm + 1, z, v=2))
    for (x, z) in pts:
        Rt = 1.6 * u + 1.2
        schaft(w, T, x, z, 0, Hm + _r(4 * u, 3), Rt)
        if turm_dach == "kegel":
            dach_kegel(w, T, x, z, Hm + _r(4 * u, 3), Rt)
        else:
            zinnen_rund(w, T, x, z, Hm + _r(4 * u, 3), Rt)
    zt = round(R * math.cos(math.pi / ecken))
    for x in range(-1 - int(u), 2 + int(u)):
        for y in range(1, 4 + int(u)):
            w.bloecke.pop((x, y, zt), None)
    if innen:
        innen(w, T, u * 0.7)


def m_pyramide(w, T, u, stufen=6, steil=2, tempel=True, treppe_vorn=True):
    """Stufenpyramide mit Mitteltreppe und Tempelhaus auf der Spitze."""
    R = stufen * 2 + _r(2 * u, 1)
    sh = _r(steil * u * 0.6 + 0.4, 1)
    for st in range(stufen):
        r = R - st * 2
        for y in range(st * sh, (st + 1) * sh):
            for x in range(-r, r + 1):
                for z in range(-r, r + 1):
                    if max(abs(x), abs(z)) >= r - 1 or y == (st + 1) * sh - 1:
                        w.setze(x, y, z, T.s(x, y, z, H=stufen * sh))
    top = stufen * sh
    if treppe_vorn:
        for t in range(top):
            z = R - (t * 2) // sh
            for x in range(-1, 2):
                w.setze(x, t, z, T.treppe("north"))
    rt = R - stufen * 2
    if tempel and rt >= 1:
        quader(w, T, -rt, -rt, rt, rt, top, _r(3 * u + 1, 3), fenster=0)
        dach_pyramide(w, T, -rt, -rt, rt, rt, top + _r(3 * u + 1, 3), ue=1)
    else:
        w.setze(0, top, 0, T.akzent())
        w.setze(0, top + 1, 0, T.feuerblock())


def m_obelisk(w, T, u, hoehe=18, bekroenung="spitze"):
    """Obelisk oder Siegessäule auf gestuftem Sockel mit Bändern und Bekrönung."""
    stufen = 2 + (u > 1)
    sockel_stufen(w, T, 2 * u + 3, stufen, rund=False)
    H = _r(hoehe * u + 4, 8)
    hb = max(1, int(1.4 * u))
    for y in range(H):
        h = max(0, int(round(hb * (1 - 0.4 * y / H))))
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                w.setze(x, stufen + y, z, T.akzent() if y % _r(5 * u, 3) == 0 and y > 0 else
                        T.s(x, y, z, H=H))
    top = stufen + H
    if bekroenung == "spitze":
        for k in range(hb + 2):
            hh = max(0, int(hb * 0.6) - k)
            for x in range(-hh, hh + 1):
                for z in range(-hh, hh + 1):
                    w.setze(x, top + k, z, T.akzent())
    elif bekroenung == "kugel":
        dach_kuppel(w, T, 0, 0, top, hb + 1, mat=T.akzent_n)
    else:
        w.setze(0, top, 0, T.feuerblock())


# ---------------------------------------------------------------------------- Figuren

def figur(S, art="mensch", pose="stehend", y0=0.0):
    """Fügt einer Skulptur eine Figur hinzu (Etiketten k=Körper, a=Akzent, d=Dunkel, g=Glas/Licht).
    art: mensch, ork, zwerg, elf, golem, ritter. pose: stehend, arme_hoch, schwert, stab, kniend, denker."""
    p = dict(mensch=(1.0, 1.0, 1.0), ork=(1.35, 0.95, 1.25), zwerg=(1.3, 0.65, 1.1), elf=(0.8, 1.12, 0.9),
             golem=(1.6, 1.0, 1.5), ritter=(1.1, 1.0, 1.1))[art]
    bw, hh, kw = p
    knie = pose == "kniend"
    by = y0 + (0 if not knie else -3 * hh)
    # Beine
    if not knie:
        S.plus(spiegel_x(kap((1.2 * bw, y0 + 0.5, 0), (1.1 * bw, y0 + 7 * hh, 0), 1.0 * bw, 1.3 * bw)), "k")
    else:
        S.plus(kap((1.2 * bw, y0 + 0.6, -2.5), (1.2 * bw, y0 + 3.5 * hh, 0.4), 1.0 * bw, 1.3 * bw), "k")
        S.plus(kap((-1.2 * bw, y0 + 0.6, 0.4), (-1.2 * bw, y0 + 3.5 * hh, 0.4), 1.0 * bw, 1.3 * bw), "k")
    t0 = y0 + 7 * hh if not knie else y0 + 3.5 * hh
    S.plus(kegel(0, 0, t0 - 1.5, t0 + 1.5, 2.6 * bw, 2.4 * bw, zf=0.75), "k")
    S.plus(kap((0, t0 + 1, 0), (0, t0 + 5.5 * hh, 0), 2.2 * bw, 2.9 * bw, zf=0.7), "k")
    S.plus(kegel(0, 0, t0 + 0.9, t0 + 1.6, 2.5 * bw, 2.5 * bw, zf=0.78), "a")
    sy = t0 + 5.3 * hh
    S.plus(spiegel_x(ell(3.0 * bw, sy, 0, 1.4 * bw, 1.2, 1.4 * bw)), "k")
    kopf = sy + 2.2 * kw
    S.plus(ell(0, kopf, 0, 1.6 * kw, 1.9 * kw, 1.7 * kw), "k")
    if art == "ork":
        S.plus(spiegel_x(kap((0.7, kopf - 1.0, 1.5), (0.9, kopf + 0.3, 2.1), 0.3, 0.12)), "a")
        S.plus(ell(0, kopf + 0.6, 1.0, 1.6, 0.4, 0.8), "k")
    if art == "zwerg":
        S.plus(kap((0, kopf - 0.8, 1.2), (0, kopf - 4.5, 1.8), 1.4, 0.6), "a")
        S.plus(ell(0, kopf + 1.3, 0, 1.8, 0.9, 1.8), "d")
    if art == "elf":
        S.plus(spiegel_x(kap((1.4, kopf + 0.2, 0), (2.4, kopf + 1.4, -0.4), 0.3, 0.1)), "k")
        S.plus(lambda X, Y, Z: (Y < kopf + 1.2) & (Y > sy - 4) & ((X / 1.8) ** 2 + ((Z + 1.0) / 1.0) ** 2 <= 1), "a")
    if art in ("ritter", "golem"):
        S.plus(lambda X, Y, Z: (np.abs(Y - kopf - 0.1) < 0.3) & (np.abs(X) < 1.2) & (Z > 1.0) & (Z < 2.2), "d")
    if art == "golem":
        S.plus(ell(0, t0 + 3.2, 2.2, 0.8, 0.8, 0.5), "g")
    # Arme
    sh = (3.0 * bw, sy - 0.3, 0)
    if pose == "arme_hoch":
        for s in (-1, 1):
            S.plus(kap((s * sh[0], sh[1], 0), (s * 2.4 * bw, sh[1] + 4, 0.5), 0.9 * bw, 0.8 * bw), "k")
            S.plus(kap((s * 2.4 * bw, sh[1] + 4, 0.5), (s * 1.0, sh[1] + 7.5, 0.6), 0.8 * bw, 0.7 * bw), "k")
        S.plus(ell(0, sh[1] + 8.8, 0.6, 1.4, 1.4, 1.4), "g")
    elif pose == "schwert":
        for s in (-1, 1):
            S.plus(kap((s * sh[0], sh[1], 0), (s * 2.6 * bw, sh[1] - 3.2, 1.3), 0.9 * bw), "k")
            S.plus(kap((s * 2.6 * bw, sh[1] - 3.2, 1.3), (s * 0.8, sh[1] - 4.5, 2.8), 0.85 * bw), "k")
        S.plus(lambda X, Y, Z: (np.abs(X) < 0.5) & (Y > y0) & (Y < sh[1] - 5.2) & (np.abs(Z - 3.0) < 0.5), "a")
        S.plus(lambda X, Y, Z: (np.abs(X) < 2.4) & (np.abs(Y - (sh[1] - 5.2)) < 0.4) & (np.abs(Z - 3.0) < 0.6), "d")
    elif pose == "stab":
        S.plus(kap((sh[0], sh[1], 0), (sh[0] + 0.8, sh[1] - 3, 1.5), 0.9 * bw), "k")
        S.plus(kap((-sh[0], sh[1], 0), (-sh[0] + 0.4, sh[1] - 4.2, 0.4), 0.9 * bw), "k")
        S.plus(kap((sh[0] + 1.0, y0, 1.8), (sh[0] + 1.0, sh[1] + 5, 1.8), 0.4), "d")
        S.plus(ell(sh[0] + 1.0, sh[1] + 5.8, 1.8, 0.9, 0.9, 0.9), "g")
    elif pose == "denker":
        S.plus(kap((sh[0], sh[1], 0), (1.6, sh[1] - 2.5, 2.0), 0.9 * bw), "k")
        S.plus(kap((1.6, sh[1] - 2.5, 2.0), (0.4, kopf - 1.6, 1.6), 0.8 * bw), "k")
        S.plus(kap((-sh[0], sh[1], 0), (-sh[0] + 0.3, sh[1] - 4.5, 0.6), 0.9 * bw), "k")
    else:
        for s in (-1, 1):
            S.plus(kap((s * sh[0], sh[1], 0), (s * (sh[0] + 0.5), sh[1] - 5, 0.4), 0.9 * bw, 0.8 * bw), "k")
    return kopf + 2


def m_statue(w, T, u, art="mensch", pose="stehend", sockel="eckig", groesse=1.0):
    """Statue auf Sockel – Figuren: Mensch, Ork, Zwerg, Elf, Golem, Ritter; Posen: stehend, Arme hoch mit
    Leuchtkugel, auf ein Schwert gestützt, mit Stab, kniend, nachdenkend."""
    stufen = 2 + (u > 1.5)
    R = (5 * u + 2) * groesse
    if sockel == "rund":
        sockel_stufen(w, T, R, stufen)
        top = stufen
    else:
        sockel_stufen(w, T, R, stufen, rund=False)
        hs = _r(2 * u, 1)
        for y in range(stufen, stufen + hs):
            for x in range(-int(R * 0.6), int(R * 0.6) + 1):
                for z in range(-int(R * 0.6), int(R * 0.6) + 1):
                    w.setze(x, y, z, T.akzent() if (y == stufen + hs // 2 and (x == 0 or z == 0) and
                                                    max(abs(x), abs(z)) == int(R * 0.6)) else T.s(x, y, z, v=1))
        top = stufen + hs
    S = Skulptur(w, u * 0.75 * groesse)
    S.mat("k", lambda x, y, z, lx, ly, lz: T.figur(0.3 + (len(T.figur_n) - 1.3) * min(1, ly / 20) +
                                                   w.rng.random() * 0.6, x, y, z))
    S.mat("a", T.akzent())
    S.mat("d", w.b("polished_blackstone"))
    S.mat("g", T.w.b(T.kristall_n[0]))
    figur(S, art, pose)
    S.rendern((-7, -2, -5), (7, 28, 6), versatz=(0.5, top, 0.5))


def m_brunnen(w, T, u, ebenen=2, form="rund", figur_oben=False):
    """Brunnen mit Becken, gestuften Schalen, Wasser und optionaler Figur obenauf."""
    R = 4 * u + 3
    rand = kreisrand(R) if form == "rund" else [(x, z) for x in range(-int(R), int(R) + 1) for z in range(-int(R), int(R) + 1)
                                                if max(abs(x), abs(z)) == int(R)]
    inner = scheibe(R - 0.5) if form == "rund" else [(x, z) for x in range(-int(R) + 1, int(R)) for z in range(-int(R) + 1, int(R))]
    for x, z in inner:
        w.setze(x, 0, z, T.s(x, 0, z, v=1))
        w.setze(x, 1, z, w.b("water", level=0))
    for x, z in rand:
        w.setze(x, 0, z, T.s(x, 0, z, v=1))
        w.setze(x, 1, z, T.s(x, 1, z, v=2))
    y = 1
    for e in range(ebenen):
        rr = R * (0.5 - e * 0.18)
        hs = _r(2 * u + 1, 2)
        for yy in range(y, y + hs):
            w.setze(0, yy, 0, T.s(0, yy, 0, v=2))
        y += hs
        for x, z in scheibe(max(1, rr)):
            w.setze(x, y, z, T.s(x, y, z, v=2.5) if math.hypot(x, z) > rr - 1 else w.b("water", level=0))
        y += 1
    if figur_oben:
        S = Skulptur(w, u * 0.3)
        S.mat("k", lambda x, yy, z, *_: T.figur(1.5, x, yy, z))
        S.mat("a", T.akzent())
        S.mat("d", T.akzent())
        S.mat("g", w.b("water", level=0))
        figur(S, "mensch", "arme_hoch")
        S.rendern((-7, 0, -5), (7, 26, 6), versatz=(0.5, y, 0.5))
    else:
        w.setze(0, y, 0, T.akzent())


def m_pavillon(w, T, u, ecken=8, dach="kuppel", hoehe=4):
    """Offener Pavillon mit Säulen, Gesims und Kuppel-, Kegel- oder Zwiebeldach, Bänke innen."""
    R = 3 * u + 2
    for x, z in scheibe(R + 0.6):
        w.setze(x, 0, z, T.s(x, 0, z, v=1.5))
    H = _r(hoehe * u + 1, 3)
    pts = [(round(math.cos(i * 2 * math.pi / ecken) * R), round(math.sin(i * 2 * math.pi / ecken) * R)) for i in range(ecken)]
    for x, z in pts:
        saeule(w, T, x, z, 1, H, kapitell=False)
    for x, z in kreisrand(R + 0.6):
        w.setze(x, H + 1, z, T.s(x, H + 1, z, v=2.5))
    if dach == "kuppel":
        dach_kuppel(w, T, 0, 0, H + 2, R)
    elif dach == "zwiebel":
        dach_zwiebel(w, T, 0, 0, H + 2, R * 0.8)
    else:
        dach_kegel(w, T, 0, 0, H + 2, R + 0.5)
    w.setze(0, H, 0, T.licht(haengend=True))


def m_huette(w, T, u, form="rund", dach="kegel", groesse=1.0):
    """Hütte: rund oder eckig, Kegel-/Sattel-/Kuppeldach, Tür, Fenster, Laterne und Holzstapel."""
    R = (2.5 * u + 1.5) * groesse
    H = _r(3 * u + 1, 3)
    if form == "rund":
        schaft(w, T, 0, 0, 0, H, R, form="rund", fenster=3)
        if dach == "kuppel":
            dach_kuppel(w, T, 0, 0, H, R + 0.5)
        else:
            dach_kegel(w, T, 0, 0, H, R + 0.6, H=_r(R * 1.6, 3))
        tz = int(R)
    else:
        b = int(R)
        quader(w, T, -b - 1, -b, b + 1, b, 0, H, fenster=3, tuer=False)
        if dach == "sattel":
            dach_sattel(w, T, -b - 1, -b, b + 1, b, H, ue=1)
        else:
            dach_pyramide(w, T, -b - 1, -b, b + 1, b, H, ue=1)
        tz = b
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(0, y, tz, w.b(f"{T.holz}_door", facing="south", half=half, hinge="left", open=False, powered=False))
    w.setze(2, 1, tz + 1, T.licht())
    for k in range(2):
        w.setze(-int(R) - 1, 1 + k, 0, w.b(f"{T.holz}_log", axis="z") if T.holz not in ("crimson", "warped") else
                w.b(f"{T.holz}_stem", axis="z"))


def m_haus(w, T, u, etagen=2, breite=7, tiefe=5, dach="sattel", turm=False):
    """Mehrstöckiges Haus mit Eckbalken, Fensterreihen, Sattel-/Walmdach, Kamin und optionalem Eckturm."""
    from bau import Stil, kasten_haus, satteldach, walmdach, kamin
    st = Stil(w, T.stein, holz=T.holz, dach=T.dach_tr, dach_voll=T.dach_voll, sockel=T.stein_n[0], fachwerk=True,
              glas="glass_pane")
    bx, bz = _r(breite * u + 2, 4), _r(tiefe * u + 2, 3)
    yt, a, b, c, d = kasten_haus(w, st, -bx // 2, -bz // 2, -bx // 2 + bx, -bz // 2 + bz, 0, _r(etagen * min(1.5, u), 1),
                                 eh=4, jetty=etagen > 1)
    top = satteldach(w, st, a, b, c, d, yt) if dach == "sattel" else walmdach(w, st, a, b, c, d, yt)
    kamin(w, c - 1, b + 1, yt, top + 1)
    if turm:
        schaft(w, T, c, d, 1, yt + 3, 1.4 * u + 1)
        dach_kegel(w, T, c, d, yt + 4, 1.4 * u + 1)


def m_baum(w, T, u, art="rund", groesse=1.0, holz=None, blaetter=None):
    """Baum: rund, kegelförmig, Trauerweide, Pilz, Kristall oder Laternenbaum – im Thema eingefärbt."""
    h = _r((6 * u + 3) * groesse, 4)
    holzb = w.b(holz or f"{T.laub_art}_log", axis="y") if not (holz or T.laub_art).startswith(("crimson", "warped")) else \
        w.b(f"{holz or T.laub_art}_stem", axis="y")
    bl = blaetter or [laub(w, T.laub_art) if T.laub_art not in ("crimson", "warped") else
                      w.b("nether_wart_block" if T.laub_art == "crimson" else "warped_wart_block")]
    for y in range(1, h + 1):
        w.setze(0, y, 0, holzb)
        if u > 1.2 and y < h * 0.5:
            for dx, dz in ((1, 0), (0, 1), (1, 1)):
                w.setze(dx, y, dz, holzb)
    S = Skulptur(w, max(0.8, u * groesse))
    S.mat("l", lambda *a: bl[int(w.rng.integers(len(bl)))])
    S.mat("g", T.licht() if not T.licht_n.endswith("lantern") else w.b("shroomlight"))
    S.mat("k", lambda x, y, z, *_: w.b(T.kristall_n[(x + y + z) % len(T.kristall_n)]))
    if art == "rund":
        S.plus(lambda X, Y, Z: (X / 3.2) ** 2 + (Y / 2.6) ** 2 + (Z / 3.2) ** 2 <= 1 + 0.1 * np.sin(X * 2 + Z), "l")
        top = (-4, -3, -4), (4, 3, 4)
    elif art == "kegel":
        S.plus(lambda X, Y, Z: (Y > -3) & (Y < 6) & (X * X + Z * Z <= (2.8 * (1 - (Y + 3) / 9)) ** 2 + 0.3), "l")
        top = (-4, -4, -4), (4, 7, 4)
    elif art == "weide":
        S.plus(lambda X, Y, Z: (X / 3.5) ** 2 + (Y / 1.8) ** 2 + (Z / 3.5) ** 2 <= 1, "l")
        S.plus(lambda X, Y, Z: (np.abs(np.sqrt(X * X + Z * Z) - 3.2) < 0.6) & (Y < 0) & (Y > -4.5) &
               (np.mod(np.arctan2(Z, X) * 5, 1) < 0.4), "l")
        top = (-5, -5, -5), (5, 3, 5)
    elif art == "pilz":
        S.plus(lambda X, Y, Z: ((X * X + Z * Z) / 4.0 ** 2 + (Y / 2.0) ** 2 <= 1) & (Y >= -0.3), "l")
        S.plus(lambda X, Y, Z: (np.abs(Y + 0.4) < 0.4) & (X * X + Z * Z <= 3.5 ** 2) & (X * X + Z * Z > 2.5 ** 2), "g")
        top = (-5, -1, -5), (5, 3, 5)
    elif art == "kristall":
        for i in range(5):
            a = i * 1.26
            S.plus(kap((0, -1, 0), (math.cos(a) * 2.6, 3 + (i % 2) * 1.5, math.sin(a) * 2.6), 0.9, 0.2), "k")
        top = (-4, -2, -4), (4, 6, 4)
    else:  # laterne
        S.plus(lambda X, Y, Z: (X / 3.2) ** 2 + (Y / 2.4) ** 2 + (Z / 3.2) ** 2 <= 1, "l")
        top = (-4, -3, -4), (4, 3, 4)
    S.rendern(top[0], top[1], versatz=(0.5, h + 1, 0.5), ueberschreiben=False)
    if art == "laterne":
        for a in range(4):
            x, z = round(math.cos(a * 1.57 + 0.4) * 3 * max(0.8, u)), round(math.sin(a * 1.57 + 0.4) * 3 * max(0.8, u))
            w.setze(x, h - 1, z, w.b("chain", axis="y", waterlogged=False), ueberschreiben=False)
            w.setze(x, h - 2, z, T.licht(haengend=True), ueberschreiben=False)


def m_kristalle(w, T, u, anzahl=7, hoehe=10, sechseck=True):
    """Gruppe schräg wachsender Kristallsäulen mit Leuchtkernen auf einem Felsbett."""
    R = 5 * u + 3
    for x, z in scheibe(R + 1):
        w.setze(x, 0, z, T.s(x, 0, z, v=0.5))
    S = Skulptur(w, 1.0)
    S.mat("k", lambda x, y, z, *_: w.b(T.kristall_n[(x * 3 + y + z * 7) % len(T.kristall_n)]) if (x + y * 3 + z) % 13
          else (T.licht() if not T.licht_n.endswith("lantern") else w.b("sea_lantern")))
    rng = w.rng
    for i in range(anzahl + int(u)):
        a = i * 2.39996
        d = R * 0.6 * math.sqrt((i + 0.5) / (anzahl + u))
        bx, bz = math.cos(a) * d, math.sin(a) * d
        lang = (hoehe * (0.4 + 0.6 * rng.random())) * u + 2
        r = (0.7 + 0.7 * rng.random()) * u + 0.6
        neig = 0.2 + 0.35 * rng.random()
        tx, tz = bx + math.cos(a) * lang * neig, bz + math.sin(a) * lang * neig

        def saeule(X, Y, Z, bx=bx, bz=bz, tx=tx, tz=tz, lang=lang, r=r):
            d = np.array([tx - bx, lang, tz - bz])
            L2 = d @ d
            t = np.clip(((X - bx) * d[0] + Y * d[1] + (Z - bz) * d[2]) / L2, 0, 1)
            qx, qy, qz = X - bx - t * d[0], Y - t * d[1], Z - bz - t * d[2]
            rr = r * np.where(t > 0.82, (1 - t) / 0.18, 1)
            if sechseck:
                ang = np.arctan2(qz, qx)
                rr = rr * np.cos(math.pi / 6) / np.cos(np.mod(ang, math.pi / 3) - math.pi / 6)
            return qx * qx + qy * qy + qz * qz <= rr * rr
        S.plus(saeule, "k")
    S.rendern((-R - hoehe * u, 0, -R - hoehe * u), (R + hoehe * u, hoehe * u + 4, R + hoehe * u), versatz=(0.5, 1, 0.5))


def m_felsbogen(w, T, u, radius=9, dicke=2.5, natur=True):
    """Natürlicher oder gemauerter Bogen, bewachsen, mit Leuchtstein im Scheitel."""
    R = radius * u + 3
    d = dicke * u + 1
    S = Skulptur(w, 1.0)
    S.mat("f", lambda x, y, z, lx, ly, lz: T.s(x, y, z, v=0.3 + (len(T.stein_n) - 1.5) * ly / (R + d)))
    S.mat("a", T.akzent())
    S.plus(lambda X, Y, Z: (np.abs(np.sqrt(X * X + Y * Y) - R) <= d * (1 + (0.18 * np.sin(X * 0.7 + Y * 0.4) if natur else 0)))
           & (Y >= 0) & (np.abs(Z) <= d * 0.85), "f")
    S.plus(ell(0, R + d - 0.2, 0, 0.8, 0.8, 0.8), "a")
    S.rendern((-R - d - 1, 0, -d - 1), (R + d + 1, R + d + 1, d + 1), versatz=(0.5, 1, 0.5))
    if natur:
        ueberwuchern(w, None, ranken=0.35, moos_oben=0.4, pflanzen=0.2, buesche=0.03, max_ranke=4)


def m_schwebeinsel(w, T, u, radius=8, bau=None, hoehe=10):
    """Schwebende Insel mit zapfenförmiger Unterseite; obenauf ein kleiner Bau."""
    R = radius * u + 3
    yi = _r(hoehe * u + 4, 6)
    S = Skulptur(w, 1.0)
    S.mat("e", lambda x, y, z, lx, ly, lz: T.bodenblock() if ly > -0.5 else T.s(x, y, z, v=0.3 + (len(T.stein_n) - 1.5) * (1 + ly / R)))

    def insel(X, Y, Z):
        d = np.sqrt(X * X + Z * Z) / R
        unten = -R * 1.1 * np.clip(1 - d, 0, 1) ** 1.4
        return (d <= 1) & (Y <= 0.5) & (Y >= unten)
    S.plus(insel, "e")
    S.rendern((-R - 1, -R * 1.2, -R - 1), (R + 1, 1, R + 1), versatz=(0.5, yi, 0.5))
    if bau:
        vorher = dict(w.bloecke)
        w.bloecke = {}
        bau(w, T, u * 0.6)
        neu = w.bloecke
        w.bloecke = vorher
        for (x, y, z), b in neu.items():
            w.setze(x, y + yi + 1, z, b)
    w.setze(0, 0, 0, T.s(0, 0, 0, v=1))


def m_steinkreis(w, T, u, anzahl=10, hoehe=6, decksteine=True):
    """Kreis aus Megalithen mit Decksteinen und leuchtendem Mittelstein."""
    R = 8 * u + 4
    hs = _r(hoehe * u + 2, 4)
    bs = max(1, int(u))
    pf = []
    for i in range(anzahl):
        a = i * 2 * math.pi / anzahl
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        pf.append((x, z))
        for y in range(1, hs + 1):
            for dx in range(-bs + 1, bs + 1):
                for dz in range(-bs + 1, bs + 1):
                    w.setze(x + dx, y, z + dz, T.s(x, y, z, H=hs))
    if decksteine:
        for i in range(0, anzahl - 1, 2):
            (x1, z1), (x2, z2) = pf[i], pf[i + 1]
            for t in np.linspace(0, 1, 2 * int(math.hypot(x2 - x1, z2 - z1)) + 2):
                w.setze(round(x1 + (x2 - x1) * t), hs + 1, round(z1 + (z2 - z1) * t), T.s(0, hs, 0, v=2))
    w.setze(0, 1, 0, T.akzent())
    w.setze(0, 2, 0, w.b(T.kristall_n[0]))


def m_zelt(w, T, u, groesse=1.0, rund=True):
    """Großes Zelt mit gestreiften Bahnen, Mittelmast mit Wimpel und Spannseilen."""
    R = (4 * u + 2) * groesse
    H = _r(3 * u + 1, 2)
    st = [w.b(s) for s in T.stoff]
    for y in range(1, H + 1):
        for x, z in kreisrand(R) if rund else [(x, z) for x in range(-int(R), int(R) + 1) for z in range(-int(R), int(R) + 1)
                                                 if max(abs(x), abs(z)) == int(R)]:
            if not (z > R - 1.5 and abs(x) <= 1 and y <= 2):
                w.setze(x, y, z, st[int((math.atan2(z, x) + math.pi) / (2 * math.pi) * 16) % len(st)])
    kh = _r(R * 0.9, 3)
    for k in range(kh + 1):
        r = R * (1 - k / (kh + 1))
        for x, z in kreisrand(max(0.3, r)):
            w.setze(x, H + 1 + k, z, st[int((math.atan2(z, x) + math.pi) / (2 * math.pi) * 16) % len(st)])
    for y in range(H + kh + 2, H + kh + 4):
        w.setze(0, y, 0, T.pfosten())
    w.setze(1, H + kh + 3, 0, st[0])


def m_schrein(w, T, u, dach="sattel", figur_art=None):
    """Kleiner Schrein: Podest, Säulen, Dach, Opferschale mit Licht und Kerzen; optional Figur."""
    h = _r(2 * u + 1, 2)
    H = _r(3 * u + 2, 3)
    for x in range(-h - 1, h + 2):
        for z in range(-h - 1, h + 2):
            w.setze(x, 0, z, T.s(x, 0, z, v=1))
    for x in (-h, h):
        for z in (-h, h):
            saeule(w, T, x, z, 1, H, kapitell=False)
    if dach == "sattel":
        dach_sattel(w, T, -h, -h, h, h, H + 1, ue=1)
    elif dach == "kuppel":
        dach_kuppel(w, T, 0, 0, H + 1, h + 0.5)
    else:
        dach_pyramide(w, T, -h, -h, h, h, H + 1, ue=1)
    if figur_art:
        S = Skulptur(w, u * 0.18)
        S.mat("k", lambda x, y, z, *_: T.figur(1.5, x, y, z))
        S.mat("a", T.akzent())
        S.mat("d", T.akzent())
        S.mat("g", T.licht() if not T.licht_n.endswith("lantern") else w.b("shroomlight"))
        figur(S, figur_art, "arme_hoch")
        S.rendern((-7, 0, -5), (7, 26, 6), versatz=(0.5, 1, 0.5))
    else:
        w.setze(0, 1, 0, T.akzent())
        w.setze(0, 2, 0, T.licht())
    for x in (-h - 1, h + 1):
        w.setze(x, 1, h + 1, w.b("candle", candles=3, lit=True, waterlogged=False))


def m_ruine(w, T, u, art="halle", zerfall=0.45):
    """Ruine eines Turms, einer Halle oder eines Tempels: eingestürzte Mauern, Trümmer und Bewuchs."""
    if art == "turm":
        m_turm(w, T, u, dach="zinnen", balkon=False)
    elif art == "tempel":
        m_tempel(w, T, u)
    else:
        m_halle(w, T, u, saeulen=True, dach="sattel")
    rs = w.rng
    hmax = max(p[1] for p in w.bloecke) if w.bloecke else 1
    for p in list(w.bloecke):
        x, y, z = p
        if y > 1 and rs.random() < zerfall * (y / hmax) ** 0.7 + 0.04 * math.sin(x * 0.7 + z):
            w.bloecke.pop(p, None)
    for i in range(int(6 * u) + 3):
        a = rs.random() * 2 * math.pi
        d = (3 + rs.random() * 6) * u + 3
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        w.setze(x, 1, z, T.s(x, 1, z, v=1), ueberschreiben=False)
    ueberwuchern(w, None, ranken=0.45, moos_oben=0.5, pflanzen=0.3, buesche=0.05, max_ranke=4)


def m_terrassen(w, T, u, stufen=4, haeuser=True):
    """Terrassenhang mit Stützmauern, Treppen, kleinen Häusern und Gärten auf jeder Stufe."""
    W = _r(10 * u + 4, 7)
    Hs, Ts = _r(2.5 * u + 1, 2), _r(3 * u + 2, 3)
    for k in range(stufen):
        for x in range(-W, W + 1):
            for z in range(-k * Ts - Ts, -k * Ts + 1):
                for y in range(0, (k + 1) * Hs + 1):
                    w.setze(x, y, z, T.s(x, y, z, v=0.5) if y < (k + 1) * Hs else T.bodenblock())
        if haeuser:
            yb = (k + 1) * Hs + 1
            for i, x0 in enumerate(range(-W + 2, W - 4, 7)):
                if (i + k) % 2 == 0:
                    quader(w, T, x0, -k * Ts - Ts + 1, x0 + 3, -k * Ts - 1, yb, 3, fenster=2, tuer=False)
                    dach_pyramide(w, T, x0, -k * Ts - Ts + 1, x0 + 3, -k * Ts - 1, yb + 3, ue=0)
                else:
                    for xx in range(x0, x0 + 4):
                        w.setze(xx, yb, -k * Ts - Ts // 2, w.b(T.pflanzen[xx % len(T.pflanzen)]) if T.pflanzen else T.akzent())
        for s in range(Hs):
            for b in range(2):
                w.setze(W - 2 - b, k * Hs + 1 + s, -k * Ts - s, T.treppe("north"))


def m_laternenweg(w, T, u, laenge=14, bogen=False):
    """Gepflasterter Weg mit Laternenpfählen, Bänken und optionalen Rosenbögen."""
    L = _r(laenge * u + 4, 6)
    for z in range(-L, L + 1):
        for x in (-1, 0, 1):
            w.setze(x, 0, z, T.s(x, 0, z, v=1))
        if z % 4 == 0:
            for s in (-1, 1):
                for y in range(1, 4):
                    w.setze(s * 2, y, z, T.pfosten())
                w.setze(s * 2, 4, z, T.licht())
            if bogen:
                for x in range(-2, 3):
                    w.setze(x, 4, z, laub(w, "flowering_azalea") if T.laub_art != "crimson" else w.b("nether_wart_block"))


def m_markt(w, T, u, staende=4):
    """Kleiner Platz mit Marktständen (Stoffdächer), Brunnen in der Mitte und Laternen."""
    L = staende * 3 + 4
    for x in range(-L, L + 1):
        for z in range(-L, L + 1):
            w.setze(x, 0, z, T.s(x, 0, z, v=1))
    for x, z in kreisrand(2):
        w.setze(x, 1, z, T.s(x, 1, z, v=2))
    w.setze(0, 1, 0, w.b("water", level=0))
    st = [w.b(s) for s in T.stoff]
    for i in range(staende):
        a = i * 2 * math.pi / staende
        cx, cz = round(math.cos(a) * L * 0.65), round(math.sin(a) * L * 0.65)
        for dx in (-1, 1):
            for dz in (-1, 1):
                for y in range(1, 4):
                    w.setze(cx + dx, y, cz + dz, T.pfosten())
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                w.setze(cx + dx, 4, cz + dz, st[(dx + 4) % len(st)])
        w.setze(cx, 1, cz, w.b("barrel", facing="up", open=False))


def m_monument(w, T, u, art="ring"):
    """Monument: schwebender Ring, Säulenkranz mit Kugel oder gestapelte Steine mit Leuchtkern."""
    R = 5 * u + 2
    for x, z in scheibe(R * 0.7 + 1):
        w.setze(x, 0, z, T.s(x, 0, z, v=1))
    S = Skulptur(w, 1.0)
    S.mat("r", lambda x, y, z, *_: T.metall(1 + w.rng.random(), x, y, z))
    S.mat("k", lambda x, y, z, *_: w.b(T.kristall_n[(x + y + z) % len(T.kristall_n)]))
    S.mat("s", lambda x, y, z, *_: T.s(x, y, z, v=2))
    if art == "ring":
        S.plus(torus(0, R + 2, 0, R, 0.6 * u + 0.4, "z"), "r")
        S.plus(ell(0, R + 2, 0, 1.2 * u + 0.5, 1.2 * u + 0.5, 1.2 * u + 0.5), "k")
    elif art == "kugel":
        S.plus(ell(0, R * 1.6, 0, R * 0.6, R * 0.6, R * 0.6), "k")
        for i in range(6):
            a = i * math.pi / 3
            S.plus(kap((math.cos(a) * R * 0.9, 0, math.sin(a) * R * 0.9), (math.cos(a) * R * 0.5, R * 1.5, math.sin(a) * R * 0.5),
                       0.6 * u + 0.4, 0.3), "r")
    else:
        y = 0.5
        for i in range(5):
            rr = (R * 0.55) * (1 - i * 0.15)
            S.plus(ell(0.4 * math.sin(i), y + rr * 0.45, 0.3 * math.cos(i), rr, rr * 0.5, rr * 0.9), "s")
            y += rr * 0.9
        S.plus(ell(0, y + 0.6, 0, 0.9, 0.9, 0.9), "k")
    S.rendern((-R - 2, 0, -R - 2), (R + 2, R * 3 + 4, R + 2), versatz=(0.5, 1, 0.5))


def m_insel_dorf(w, T, u, haeuser=4):
    """Kleines Dorf: Hütten im Kreis um einen Platz mit Feuer und Laternen, verbunden durch Wege."""
    R = 7 * u + 3 + haeuser
    for i in range(haeuser):
        a = i * 2 * math.pi / haeuser
        cx, cz = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        vorher = dict(w.bloecke)
        w.bloecke = {}
        m_huette(w, T, u * 0.6, form="rund" if i % 2 else "eckig", dach="kegel" if i % 2 else "sattel")
        neu = w.bloecke
        w.bloecke = vorher
        for (x, y, z), b in neu.items():
            w.setze(x + cx, y, z + cz, b)
        for t in np.linspace(0, 1, int(R)):
            w.setze(round(cx * t), 0, round(cz * t), T.s(0, 0, 0, v=1))
    w.setze(0, 1, 0, T.feuerblock())

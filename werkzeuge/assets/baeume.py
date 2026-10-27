"""Baum-Generator: Stämme mit Verjüngung, verzweigte Äste, Wurzeln und lockere Blätterkronen.

Jede Art hat eine eigene Wuchsform. Alle Bäume stehen mit dem Stammfuß auf (0, 0, 0):
y = 0 ist der Bodenblock, Wurzeln reichen in den Boden hinein.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from lib import Welt, laub

# --------------------------------------------------------------------------- Vektorhilfen


def norm(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else np.array([0.0, 1.0, 0.0])


def drehe_zufaellig(w: Welt, v, staerke):
    return norm(np.asarray(v) + (w.rng.random(3) - 0.5) * 2 * staerke)


def richtung_aus_winkeln(azimut, neigung):
    """neigung 0 = senkrecht nach oben, 90° = waagerecht."""
    n = math.radians(neigung)
    a = math.radians(azimut)
    return norm([math.sin(n) * math.cos(a), math.cos(n), math.sin(n) * math.sin(a)])


def abzweig(eltern, spreizung, azimut):
    """Richtung, die um 'spreizung' Grad von 'eltern' abweicht, rundherum gedreht um 'azimut'."""
    d = norm(eltern)
    hilf = np.array([0.0, 1.0, 0.0]) if abs(d[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = norm(np.cross(d, hilf))
    v = np.cross(d, u)
    s, a = math.radians(spreizung), math.radians(azimut)
    return norm(math.cos(s) * d + math.sin(s) * (math.cos(a) * u + math.sin(a) * v))


def achse(v):
    ax, ay, az = abs(v[0]), abs(v[1]), abs(v[2])
    if ay >= ax and ay >= az:
        return "y"
    return "x" if ax >= az else "z"


# --------------------------------------------------------------------------- Holz und Laub


class Holzart:
    def __init__(self, w: Welt, art: str):
        self.w = w
        self.art = art
        self.log = {a: w.b(f"{art}_log", axis=a) for a in "xyz"}
        self.wood = {a: w.b(f"{art}_wood", axis=a) for a in "xyz"}
        self.alle = set(self.log.values()) | set(self.wood.values())


def kugel_f(w: Welt, c, r, blk, ueberschreiben=True, schutz=None):
    cx, cy, cz = c
    ri = int(math.ceil(r)) + 1
    bx, by, bz = int(math.floor(cx)), int(math.floor(cy)), int(math.floor(cz))
    for x in range(bx - ri, bx + ri + 1):
        for y in range(by - ri, by + ri + 1):
            for z in range(bz - ri, bz + ri + 1):
                if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 + (z + 0.5 - cz) ** 2 <= r * r:
                    if schutz and w.hole(x, y, z) in schutz:
                        continue
                    w.setze(x, y, z, blk, ueberschreiben)


class Pinsel:
    """Zeichnet Holz entlang eines Wegs. Dünne Äste bleiben flächig verbunden (keine Eckverbindungen)."""

    def __init__(self, w: Welt, holz: Holzart):
        self.w, self.holz = w, holz
        self.letzte = None

    def neu(self):
        self.letzte = None

    def zelle(self, x, y, z, a):
        b = self.w.hole(x, y, z)
        if b in self.holz.alle:
            return
        self.w.setze(x, y, z, self.holz.log[a])

    def punkt(self, p, r, d):
        a = achse(d)
        if r >= 0.85:
            kugel_f(self.w, p, r, self.holz.wood[a])
            self.letzte = None
            return
        c = (math.floor(p[0]), math.floor(p[1]), math.floor(p[2]))
        if self.letzte is not None and c != self.letzte:
            # Lücken über Kanten/Ecken mit Zwischenblöcken schließen
            cur = list(self.letzte)
            reihenfolge = sorted(range(3), key=lambda i: -abs(d[i]))
            for i in reihenfolge:
                while cur[i] != c[i]:
                    cur[i] += 1 if c[i] > cur[i] else -1
                    if tuple(cur) != c:
                        self.zelle(*cur, "xyz"[i])
        self.zelle(*c, a)
        self.letzte = c


def ast(w: Welt, pinsel: Pinsel, start, richtung, laenge, r0, r1, biegung=0.08, auftrieb=0.0, schwerkraft=0.0):
    """Wächst einen Ast und gibt die Punkte (Position, Richtung, Radius) zurück."""
    p = np.asarray(start, dtype=float)
    d = norm(richtung)
    punkte = []
    schritte = max(2, int(laenge / 0.4))
    pinsel.neu()
    for i in range(schritte + 1):
        t = i / schritte
        r = r0 + (r1 - r0) * t
        pinsel.punkt(p, r, d)
        punkte.append((p.copy(), d.copy(), r))
        d = drehe_zufaellig(w, d, biegung)
        d = norm(d + np.array([0, auftrieb - schwerkraft, 0]))
        p = p + d * (laenge / schritte)
    return punkte


def blattwolke(w: Welt, c, rx, ry, bloecke, dichte=0.9, schutz=None, luecken=0.0, min_y=-999):
    """Unregelmäßige Blätterwolke (Ellipsoid mit ausgefranstem Rand und optionalen Löchern)."""
    cx, cy, cz = c
    ri = int(math.ceil(max(rx, ry))) + 2
    bx, by, bz = int(math.floor(cx)), int(math.floor(cy)), int(math.floor(cz))
    gewichte = np.array([g for _, g in bloecke], dtype=float)
    kum = np.cumsum(gewichte / gewichte.sum())
    for x in range(bx - ri, bx + ri + 1):
        for y in range(by - ri, by + ri + 1):
            for z in range(bz - ri, bz + ri + 1):
                dx = (x + 0.5 - cx) / rx
                dy = (y + 0.5 - cy) / ry
                dz = (z + 0.5 - cz) / rx
                # Unterseite flacher abschneiden – Kronen sind unten offen
                if dy < 0:
                    dy *= 1.35
                d = math.sqrt(dx * dx + dy * dy + dz * dz)
                if d > 1.0 + (w.rng.random() - 0.5) * 0.4:
                    continue
                if d > 0.72 and w.rng.random() > dichte:
                    continue
                if luecken and d < 0.8 and w.rng.random() < luecken:
                    continue
                if y < min_y:
                    continue
                if schutz and w.hole(x, y, z) in schutz:
                    continue
                blk = bloecke[min(len(bloecke) - 1, int(np.searchsorted(kum, w.rng.random())))][0]
                w.setze(x, y, z, blk, ueberschreiben=False)


@dataclass
class Wuchs:
    """Regeln für die rekursive Verzweigung."""
    kinder: int = 3              # Abzweigungen je Ast
    spreizung: tuple = (30, 55)  # Winkel zum Elternast
    laenge: float = 0.62         # Länge Kind / Elternast
    ansatz: float = 0.35         # ab welchem Anteil der Astlänge verzweigt wird
    biegung: float = 0.1
    auftrieb: float = 0.03
    schwerkraft: float = 0.0
    duenn: float = 0.62          # Radius Kind / Elternast


def verzweigen(w: Welt, pinsel: Pinsel, start, d, laenge, r, tiefe, cfg: Wuchs, enden: list, mitte: list):
    r_ende = max(0.4, r * 0.55)
    pkt = ast(w, pinsel, start, d, laenge, r, r_ende, cfg.biegung, cfg.auftrieb, cfg.schwerkraft)
    enden.append((pkt[-1][0], tiefe))
    if tiefe <= 0 or laenge < 1.6:
        return
    az0 = w.rng.random() * 360
    for k in range(cfg.kinder):
        t = cfg.ansatz + (1 - cfg.ansatz) * (k + 0.5 + (w.rng.random() - 0.5) * 0.6) / cfg.kinder
        p, pd, pr = pkt[min(len(pkt) - 1, int(t * (len(pkt) - 1)))]
        richtung = abzweig(pd, cfg.spreizung[0] + w.rng.random() * (cfg.spreizung[1] - cfg.spreizung[0]),
                           az0 + k * 360 / cfg.kinder * 1.618 + (w.rng.random() - 0.5) * 50)
        if tiefe == 1:
            mitte.append(p)
        verzweigen(w, pinsel, p, richtung, laenge * cfg.laenge * (0.8 + 0.4 * w.rng.random()),
                   max(0.4, pr * cfg.duenn), tiefe - 1, cfg, enden, mitte)


def wurzeln(w: Welt, pinsel: Pinsel, basis_r, anzahl, laenge, hoehe=1.5, abfall=0.35):
    """Wurzeln, die vom Stammfuß nach außen und in den Boden laufen."""
    start_winkel = w.rng.random() * 360
    for i in range(anzahl):
        a = math.radians(start_winkel + i * 360 / anzahl + (w.rng.random() - 0.5) * 30)
        start = np.array([0.5 + math.cos(a) * basis_r * 0.5, hoehe, 0.5 + math.sin(a) * basis_r * 0.5])
        richtung = norm([math.cos(a), -abfall, math.sin(a)])
        l = laenge * (0.7 + w.rng.random() * 0.6)
        ast(w, pinsel, start, richtung, l, max(0.5, basis_r * 0.7), 0.4, biegung=0.1, schwerkraft=0.04)


def stamm(w: Welt, pinsel: Pinsel, hoehe, r_unten, r_oben, neigung=0.0, biegung=0.04, auftrieb=0.05):
    richtung = richtung_aus_winkeln(w.rng.random() * 360, neigung)
    return ast(w, pinsel, [0.5, 0.5, 0.5], richtung, hoehe, r_unten, r_oben, biegung=biegung, auftrieb=auftrieb)


def neue_welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def bodenstreu(w: Welt, blk_liste, anzahl, r_min, r_max):
    for _ in range(anzahl):
        a = w.rng.random() * 2 * math.pi
        d = r_min + w.rng.random() * (r_max - r_min)
        x, z = int(round(math.cos(a) * d)), int(round(math.sin(a) * d))
        if w.frei(x, 1, z):
            w.setze(x, 1, z, blk_liste[int(w.rng.random() * len(blk_liste))])


def ranken(w: Welt, traeger, anteil, max_laenge, min_y=2):
    """Ranken an Seitenflächen von Holz/Laub. Jede Ranke hängt an ihrem Block oder an der Ranke darüber."""
    seiten = [(1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")]
    for (x, y, z), b in list(w.bloecke.items()):
        if b not in traeger:
            continue
        for dx, dz, s in seiten:
            ax, az = x + dx, z + dz
            if not w.frei(ax, y, az) or w.rng.random() > anteil:
                continue
            ranke = w.b("vine", **{k: (k == s) for k in ("north", "east", "south", "west")}, up=False)
            for k in range(int(1 + w.rng.random() * max_laenge)):
                yy = y - k
                if yy < min_y or not w.frei(ax, yy, az):
                    break
                w.setze(ax, yy, az, ranke)


# --------------------------------------------------------------------------- Laubbäume (verzweigt)


def _laubbaum(w, holz_art, blaetter, H, r, stamm_anteil, cfg, tiefe, wolke, wurzel_n=0, wurzel_l=0,
              neigung=4, krone_aeste=4, kronen_neigung=(25, 50), stamm_biegung=0.05, luecken=0.12, flach=0.62, kronen_unterkante=0.8):
    pinsel = Pinsel(w, Holzart(w, holz_art))
    holz = pinsel.holz
    st = stamm(w, pinsel, H * stamm_anteil, r, r * 0.75, neigung=neigung, biegung=stamm_biegung)
    if wurzel_n:
        wurzeln(w, pinsel, r, wurzel_n, wurzel_l)
    enden, mitte = [], []
    gabel, gd, gr = st[-1]
    az0 = w.rng.random() * 360
    for i in range(krone_aeste):
        d = abzweig(gd, kronen_neigung[0] + w.rng.random() * (kronen_neigung[1] - kronen_neigung[0]),
                    az0 + i * 360 / krone_aeste + (w.rng.random() - 0.5) * 40)
        # Hauptäste setzen gestaffelt am oberen Stamm an
        k = len(st) - 1 - int(w.rng.random() * len(st) * 0.25) if i else len(st) - 1
        verzweigen(w, pinsel, st[k][0], d, H * (1 - stamm_anteil) * (0.8 + 0.3 * w.rng.random()),
                   max(0.5, gr * 0.8), tiefe, cfg, enden, mitte)
    # Kronen-Unterkante: darunter bleibt der Stamm frei sichtbar
    unterkante = int(gabel[1] * kronen_unterkante)
    for p, t in enden:
        f = 1.0 if t == 0 else 0.8
        rw = wolke * f * (0.8 + 0.4 * w.rng.random())
        blattwolke(w, p + [0, 0.6, 0], rw, rw * flach, blaetter, schutz=holz.alle, luecken=luecken,
                   min_y=unterkante)
    for p in mitte[::3]:
        rw = wolke * 0.6
        blattwolke(w, p + [0, 0.5, 0], rw, rw * 0.6, blaetter, schutz=holz.alle, luecken=luecken,
                   min_y=unterkante)
    return holz


def eiche(seed, groesse=1):
    """Mächtige Eiche: kräftiger Stamm, weit ausladende knorrige Äste, Krone aus vielen Blätterballen."""
    w = neue_welt(seed)
    blaetter = [(laub(w, "oak"), 0.88), (laub(w, "azalea"), 0.12)]
    H = [11, 19, 28][groesse]
    cfg = Wuchs(kinder=3, spreizung=(28, 55), laenge=0.62, biegung=0.12, auftrieb=0.02)
    _laubbaum(w, "oak", blaetter, H, [0.7, 1.5, 2.3][groesse], 0.42, cfg, [1, 2, 2][groesse],
              [2.8, 3.4, 4.0][groesse], wurzel_n=[0, 6, 8][groesse], wurzel_l=[0, 4, 6][groesse],
              krone_aeste=[3, 4, 5][groesse], kronen_neigung=(30, 58), flach=0.78,
              kronen_unterkante=1.1)
    return w


def birke(seed, groesse=1):
    """Schlanke, hohe Birke: gerader weißer Stamm, schmale lockere Krone aus kleinen Ballen."""
    w = neue_welt(seed)
    blaetter = [(laub(w, "birch"), 1.0)]
    H = [10, 16, 23][groesse]
    pinsel = Pinsel(w, Holzart(w, "birch"))
    st = stamm(w, pinsel, H, [0.5, 0.7, 1.0][groesse], 0.45, neigung=3, biegung=0.05)
    enden = []
    az = w.rng.random() * 360
    for k in range(int(len(st) * 0.35), len(st) - 2, max(2, len(st) // [6, 10, 14][groesse])):
        p, pd, _ = st[k]
        az += 137.5
        d = abzweig(pd, 40 + w.rng.random() * 25, az)
        rest = 1 - k / len(st)
        pkt = ast(w, pinsel, p, d, 1.5 + rest * [3, 5, 7][groesse], 0.45, 0.4, biegung=0.15, auftrieb=0.06)
        enden.append(pkt[-1][0])
    for e in enden:
        r = 1.5 + groesse * 0.3 + w.rng.random() * 0.6
        blattwolke(w, e + [0, 0.5, 0], r, r * 1.1, blaetter, schutz=pinsel.holz.alle, luecken=0.1)
    r = 1.8 + groesse * 0.4
    blattwolke(w, st[-1][0] + [0, 0.8, 0], r, r * 1.4, blaetter, schutz=pinsel.holz.alle)
    return w


def kirschbaum(seed, groesse=1):
    """Kirschbaum: geschwungener Stamm, weit ausgreifende Äste, breite flache rosa Wolken, Blütenteppich."""
    w = neue_welt(seed)
    blaetter = [(laub(w, "cherry"), 1.0)]
    H = [9, 14, 20][groesse]
    cfg = Wuchs(kinder=2, spreizung=(25, 45), laenge=0.65, biegung=0.12, auftrieb=0.05)
    holz = _laubbaum(w, "cherry", blaetter, H, [0.5, 0.9, 1.4][groesse], 0.45, cfg, [1, 1, 2][groesse],
                     [2.8, 3.4, 3.9][groesse], wurzel_n=[0, 4, 6][groesse], wurzel_l=[0, 3, 4][groesse],
                     neigung=12, krone_aeste=[3, 4, 5][groesse], kronen_neigung=(45, 70), stamm_biegung=0.14,
                     luecken=0.05, kronen_unterkante=1.0)
    # Wolken sind beim Kirschbaum flacher und breiter: zusätzliche Schicht unter jedem Ballen weglassen
    blueten = w.b("pink_petals", facing="north", flower_amount=3)
    bodenstreu(w, [blueten], 18 + groesse * 18, 1.5, 3 + groesse * 2.5)
    return w


def schwarzeiche(seed, groesse=1):
    """Uralte Schwarzeiche: wuchtig, knorrig, dichte dunkle Krone, Brettwurzeln und Pilze."""
    w = neue_welt(seed)
    blaetter = [(laub(w, "dark_oak"), 0.85), (laub(w, "oak"), 0.15)]
    H = [10, 16, 23][groesse]
    cfg = Wuchs(kinder=3, spreizung=(30, 55), laenge=0.6, biegung=0.18, auftrieb=0.02)
    _laubbaum(w, "dark_oak", blaetter, H, [1.1, 2.0, 2.9][groesse], 0.48, cfg, [1, 1, 2][groesse],
              [3.0, 3.4, 3.8][groesse], wurzel_n=[5, 7, 9][groesse], wurzel_l=[3, 5, 7][groesse],
              neigung=6, krone_aeste=[4, 5, 6][groesse], kronen_neigung=(38, 62), stamm_biegung=0.1,
              luecken=0.04, flach=0.7, kronen_unterkante=1.05)
    r = [1.1, 2.0, 2.9][groesse]
    bodenstreu(w, [w.b("brown_mushroom"), w.b("red_mushroom"), w.b("fern")], 8 + groesse * 6, r + 1, r + 5)
    return w


def trauerweide(seed, groesse=1):
    """Trauerweide: kurzer dicker Stamm, aufstrebende Hauptäste und lange herabhängende Blättervorhänge."""
    w = neue_welt(seed)
    blatt, hell = laub(w, "oak"), laub(w, "azalea")
    blaetter = [(blatt, 0.75), (hell, 0.25)]
    H = [10, 15, 21][groesse]
    cfg = Wuchs(kinder=3, spreizung=(25, 45), laenge=0.6, biegung=0.1, auftrieb=0.0, schwerkraft=0.012)
    holz = _laubbaum(w, "oak", blaetter, H, [0.7, 1.3, 1.9][groesse], 0.35, cfg, [1, 1, 2][groesse],
                     [2.4, 2.8, 3.2][groesse], wurzel_n=[3, 5, 7][groesse], wurzel_l=[2, 4, 5][groesse],
                     neigung=6, krone_aeste=[4, 5, 6][groesse], kronen_neigung=(15, 32), luecken=0.1, flach=0.7)
    # Vorhänge: von der Unterseite der äußeren Krone herabhängende Stränge
    lo, hi = w.grenzen()
    rmax = max(abs(lo[0]), abs(hi[0]), abs(lo[2]), abs(hi[2]))
    for (x, y, z), b in list(w.bloecke.items()):
        if b not in (blatt, hell) or not w.frei(x, y - 1, z):
            continue
        if math.hypot(x, z) < rmax * 0.55 or w.rng.random() > 0.3:
            continue
        laenge = int(3 + w.rng.random() * (y * 0.75))
        for k in range(1, laenge + 1):
            yy = y - k
            if yy < 3 or not w.frei(x, yy, z):
                break
            w.setze(x, yy, z, hell if w.rng.random() < 0.3 else blatt)
    return w


def toter_baum(seed, groesse=1):
    """Abgestorbener Baum mit kahlen, verdrehten Ästen und abgebrochener Spitze."""
    w = neue_welt(seed)
    pinsel = Pinsel(w, Holzart(w, "oak"))
    H = [11, 14, 19][groesse]
    st = stamm(w, pinsel, H * 0.55, [0.5, 1.0, 1.5][groesse], 0.6, neigung=8, biegung=0.12)
    if groesse:
        wurzeln(w, pinsel, [0.5, 1.0, 1.5][groesse], 3 + groesse * 2, 2 + groesse * 2)
    cfg = Wuchs(kinder=2, spreizung=(25, 60), laenge=0.6, biegung=0.28, auftrieb=0.02)
    enden, mitte = [], []
    for i in range(3 + groesse):
        k = len(st) - 1 - int(w.rng.random() * len(st) * 0.4)
        p, pd, pr = st[k]
        d = abzweig(pd, 25 + w.rng.random() * 40, w.rng.random() * 360)
        verzweigen(w, pinsel, p, d, H * 0.45, max(0.45, pr * 0.7), [1, 2, 2][groesse], cfg, enden, mitte)
    # etwas Moos und Pilze am Fuß
    bodenstreu(w, [w.b("brown_mushroom"), w.b("dead_bush")], 4 + groesse * 3, 1, 3 + groesse)
    return w


def azaleenbaum(seed, groesse=0):
    """Blühender Azaleenbaum mit gebogenem Stamm und runder bunter Krone."""
    w = neue_welt(seed)
    blaetter = [(laub(w, "azalea"), 0.5), (laub(w, "flowering_azalea"), 0.5)]
    H = [6, 9, 13][groesse]
    cfg = Wuchs(kinder=2, spreizung=(30, 50), laenge=0.65, biegung=0.18, auftrieb=0.04)
    _laubbaum(w, "oak", blaetter, H, [0.5, 0.6, 0.9][groesse], 0.5, cfg, [0, 1, 1][groesse],
              [2.3, 2.7, 3.2][groesse], neigung=14, krone_aeste=[3, 3, 4][groesse], kronen_neigung=(35, 60),
              stamm_biegung=0.2, luecken=0.05)
    # Azaleenbusch-Wurzelerde am Fuß
    w.setze(0, 0, 0, w.b("rooted_dirt"))
    return w


# --------------------------------------------------------------------------- Nadelbäume und Exoten


def fichte(seed, groesse=1):
    """Riesenfichte: gerader Stamm, Astetagen mit hängenden Spitzen, schlanke Spitze."""
    w = neue_welt(seed)
    pinsel = Pinsel(w, Holzart(w, "spruce"))
    nadel = laub(w, "spruce")
    H = [14, 24, 36][groesse]
    r = [0.6, 1.3, 2.1][groesse]
    st = stamm(w, pinsel, H, r, 0.45, neigung=0, biegung=0.012, auftrieb=0.06)
    if groesse:
        wurzeln(w, pinsel, r, 4 + groesse * 2, 2 + groesse * 2, hoehe=1.2)
    unten = int(H * 0.25)
    rmax = [4.0, 6.5, 9.5][groesse]
    y = unten
    while y < H - 1:
        t = (y - unten) / max(1, H - unten)
        rad = rmax * (1 - t) ** 0.95 + 0.8
        rad *= 0.82 + 0.3 * w.rng.random()
        mitte = st[min(len(st) - 1, int(y / H * (len(st) - 1)))][0]
        n_aeste = max(4, int(rad * 1.6))
        az0 = w.rng.random() * 360
        for k in range(n_aeste):
            d = richtung_aus_winkeln(az0 + k * 360 / n_aeste + (w.rng.random() - 0.5) * 25, 80)
            pkt = ast(w, pinsel, mitte, d, rad * 0.75, 0.45, 0.4, biegung=0.05, schwerkraft=0.05)
            # Nadelpolster entlang des Asts, außen hängend
            for p, _, _ in pkt[1::2]:
                dist = math.hypot(p[0] - mitte[0], p[2] - mitte[2])
                blattwolke(w, p + [0, 0.3, 0], 1.4 + (1 - dist / max(rad, 1)) * 0.8, 0.9, [(nadel, 1.0)],
                           schutz=pinsel.holz.alle, dichte=0.8)
        y += 2 if groesse == 0 else 3
    blattwolke(w, st[-1][0] + [0, 0.5, 0], 1.3, 3.0, [(nadel, 1.0)], schutz=pinsel.holz.alle)
    top = st[-1][0]
    for k in range(1, 3):
        w.setze(math.floor(top[0]), math.floor(top[1]) + 2 + k, math.floor(top[2]), nadel)
    return w


def mammutbaum(seed, groesse=1):
    """Mammutbaum: gewaltiger rotbrauner Stamm mit Brettwurzeln, Krone nur im oberen Teil."""
    w = neue_welt(seed)
    pinsel = Pinsel(w, Holzart(w, "spruce"))
    nadel = laub(w, "spruce")
    H = [22, 32, 44][groesse]
    r = [1.4, 2.2, 3.1][groesse]
    st = stamm(w, pinsel, H, r, 0.6, neigung=0, biegung=0.01, auftrieb=0.06)
    wurzeln(w, pinsel, r, 7 + groesse, 3 + groesse * 2, hoehe=2.0 + groesse, abfall=0.5)
    for k in range(int(len(st) * 0.5), len(st) - 2, 3):
        p, _, _ = st[k]
        t = k / len(st)
        laenge = (1 - t) * [6, 8, 11][groesse] + 2
        for _ in range(3):
            d = richtung_aus_winkeln(w.rng.random() * 360, 70 + w.rng.random() * 25)
            pkt = ast(w, pinsel, p, d, laenge, 0.5, 0.4, biegung=0.06, schwerkraft=0.02)
            blattwolke(w, pkt[-1][0] + [0, 0.3, 0], 1.6 + laenge * 0.22, 1.2, [(nadel, 1.0)],
                       schutz=pinsel.holz.alle, luecken=0.1)
            blattwolke(w, pkt[len(pkt) // 2][0] + [0, 0.3, 0], 1.4 + laenge * 0.12, 1.0, [(nadel, 1.0)],
                       schutz=pinsel.holz.alle)
    blattwolke(w, st[-1][0] + [0, 1.2, 0], 2.2, 3.4, [(nadel, 1.0)], schutz=pinsel.holz.alle)
    podsol = w.b("podzol", snowy=False)
    for x in range(-int(r) - 5, int(r) + 6):
        for z in range(-int(r) - 5, int(r) + 6):
            if math.hypot(x, z) < r + 4.5 and w.rng.random() < 0.65 and w.frei(x, 0, z):
                w.setze(x, 0, z, podsol)
    bodenstreu(w, [w.b("fern"), w.b("large_fern", half="lower")], 6 + groesse * 4, r + 1, r + 5)
    _farn_oben(w)
    return w


def _farn_oben(w):
    """Ergänzt die obere Hälfte von großen Farnen."""
    unten = w.b("large_fern", half="lower")
    oben = w.b("large_fern", half="upper")
    for (x, y, z), b in list(w.bloecke.items()):
        if b == unten:
            if w.frei(x, y + 1, z):
                w.setze(x, y + 1, z, oben)
            else:
                w.setze(x, y, z, w.b("fern"))


def dschungelriese(seed, groesse=1):
    """Dschungelriese: Brettwurzeln, hoher Stamm, breite Schirmkrone, Lianen und Kakao."""
    w = neue_welt(seed)
    blaetter = [(laub(w, "jungle"), 0.9), (laub(w, "oak"), 0.1)]
    H = [18, 27, 38][groesse]
    pinsel = Pinsel(w, Holzart(w, "jungle"))
    r = [1.0, 1.7, 2.4][groesse]
    st = stamm(w, pinsel, H * 0.72, r, r * 0.6, neigung=3)
    wurzeln(w, pinsel, r, 5 + groesse, 3 + groesse * 2, hoehe=2.5 + groesse * 1.5, abfall=0.6)
    cfg = Wuchs(kinder=2, spreizung=(30, 50), laenge=0.6, biegung=0.1, auftrieb=0.04)
    enden, mitte = [], []
    gd = st[-1][1]
    for i in range(3 + groesse):
        k = len(st) - 1 - int(w.rng.random() * len(st) * 0.15)
        d = abzweig(gd, 45 + w.rng.random() * 25, i * 360 / (3 + groesse) + w.rng.random() * 30)
        verzweigen(w, pinsel, st[k][0], d, H * 0.38, max(0.5, r * 0.5), 1, cfg, enden, mitte)
    for p, t in enden:
        rw = [3.0, 3.6, 4.3][groesse] * (0.8 + 0.4 * w.rng.random())
        blattwolke(w, p + [0, 0.6, 0], rw, rw * 0.42, blaetter, schutz=pinsel.holz.alle)
    # Seitentriebe weiter unten am Stamm
    for k in range(int(len(st) * 0.4), int(len(st) * 0.85), 6):
        p, pd, _ = st[k]
        d = abzweig(pd, 70, w.rng.random() * 360)
        pkt = ast(w, pinsel, p, d, 2 + groesse, 0.45, 0.4, biegung=0.1)
        blattwolke(w, pkt[-1][0] + [0, 0.3, 0], 1.8, 1.0, blaetter, schutz=pinsel.holz.alle)
    ranken(w, pinsel.holz.alle | {b for b, _ in blaetter}, 0.05, 4 + groesse * 3)
    return w


def mangrove(seed, groesse=1):
    """Mangrove auf hohen bogenförmigen Stelzwurzeln mit Luftwurzeln unter der Krone."""
    w = neue_welt(seed)
    pinsel = Pinsel(w, Holzart(w, "mangrove"))
    wurzel = w.b("mangrove_roots", waterlogged=False)
    blaetter = [(laub(w, "mangrove"), 1.0)]
    H = [8, 12, 17][groesse]
    sockel = [3, 4, 6][groesse]
    n = 6 + groesse * 2
    for i in range(n):
        a = math.radians(i * 360 / n + w.rng.random() * 20)
        weite = 2.5 + groesse * 1.2 + w.rng.random() * 2
        letzte = None
        for t in np.linspace(0, 1, 40):
            x = 0.5 + math.cos(a) * weite * t
            z = 0.5 + math.sin(a) * weite * t
            y = sockel + 0.5 + 1.2 * t * (1 - t) * 2 - (sockel + 1.5) * t ** 2.2
            c = (math.floor(x), math.floor(y), math.floor(z))
            if letzte and c != letzte:
                # flächig verbinden
                zw = (c[0], letzte[1], c[2])
                w.setze(*zw, wurzel, ueberschreiben=False)
            w.setze(*c, wurzel, ueberschreiben=False)
            letzte = c
    st = ast(w, pinsel, [0.5, sockel + 0.5, 0.5], richtung_aus_winkeln(w.rng.random() * 360, 5), H,
             0.7 + groesse * 0.35, 0.5, biegung=0.06, auftrieb=0.03)
    cfg = Wuchs(kinder=2, spreizung=(30, 55), laenge=0.6, biegung=0.12, auftrieb=0.03)
    enden, mitte = [], []
    for i in range(3 + groesse):
        k = int(len(st) * (0.55 + 0.45 * i / (3 + groesse)))
        p, pd, _ = st[min(k, len(st) - 1)]
        d = abzweig(pd, 40 + w.rng.random() * 25, w.rng.random() * 360)
        verzweigen(w, pinsel, p, d, H * 0.4, 0.5, 1, cfg, enden, mitte)
    for p, _ in enden:
        rw = 2.4 + groesse * 0.4
        blattwolke(w, p + [0, 0.5, 0], rw, rw * 0.6, blaetter, schutz=pinsel.holz.alle, luecken=0.08)
    haengend = w.b("hanging_roots", waterlogged=False)
    for (x, y, z), b in list(w.bloecke.items()):
        if b == blaetter[0][0] and w.frei(x, y - 1, z) and w.rng.random() < 0.07:
            w.setze(x, y - 1, z, haengend)
    w.setze(0, 0, 0, w.b("muddy_mangrove_roots", axis="y"))
    return w


def akazie(seed, groesse=1):
    """Savannen-Akazie: schiefer, gegabelter Stamm mit flachen, mehrstöckigen Schirmkronen."""
    w = neue_welt(seed)
    pinsel = Pinsel(w, Holzart(w, "acacia"))
    blaetter = [(laub(w, "acacia"), 1.0)]
    H = [7, 11, 16][groesse]
    st = stamm(w, pinsel, H * 0.45, [0.6, 1.0, 1.4][groesse], 0.7, neigung=14, biegung=0.08)
    gabeln = [2, 3, 4][groesse]
    az0 = w.rng.random() * 360
    for i in range(gabeln):
        d = abzweig(st[-1][1], 35 + w.rng.random() * 20, az0 + i * 360 / gabeln + w.rng.random() * 40)
        pkt = ast(w, pinsel, st[-1][0], d, H * (0.5 + w.rng.random() * 0.35), 0.6, 0.45, biegung=0.08,
                  auftrieb=0.03)
        rw = [2.8, 3.8, 5.0][groesse] * (0.8 + 0.4 * w.rng.random())
        top = pkt[-1][0]
        blattwolke(w, top + [0, 0.6, 0], rw, 0.8, blaetter, dichte=0.95, schutz=pinsel.holz.alle)
        blattwolke(w, top + [0, 1.6, 0], rw * 0.6, 0.7, blaetter, dichte=0.9, schutz=pinsel.holz.alle)
        # Nebenkrone auf halber Länge
        if groesse and w.rng.random() < 0.7:
            q, qd, _ = pkt[len(pkt) // 2]
            d2 = abzweig(qd, 50, w.rng.random() * 360)
            pk2 = ast(w, pinsel, q, d2, 2 + groesse * 1.5, 0.45, 0.4, biegung=0.1, auftrieb=0.04)
            blattwolke(w, pk2[-1][0] + [0, 0.6, 0], rw * 0.6, 0.7, blaetter, schutz=pinsel.holz.alle)
    return w


# --------------------------------------------------------------------------- Liste

ARTEN = {
    "eiche": ("Eiche", eiche),
    "birke": ("Birke", birke),
    "fichte": ("Riesenfichte", fichte),
    "kirschbaum": ("Kirschbaum", kirschbaum),
    "trauerweide": ("Trauerweide", trauerweide),
    "akazie": ("Akazie", akazie),
    "mammutbaum": ("Mammutbaum", mammutbaum),
    "dschungelriese": ("Dschungelriese", dschungelriese),
    "mangrove": ("Mangrove", mangrove),
    "schwarzeiche": ("Uralte Schwarzeiche", schwarzeiche),
    "toter_baum": ("Toter Baum", toter_baum),
    "azaleenbaum": ("Azaleenbaum", azaleenbaum),
}

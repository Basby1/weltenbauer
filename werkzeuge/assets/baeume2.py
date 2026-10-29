"""Bäume II – zwanzig weitere Arten mit eigener Silhouette: Linde, Buche, Rotahorn, Pyramidenpappel, Baobab,
Drachenbaum, Olivenbaum, Eibe, Herbstlärche, Libanonzeder, blühende Rosskastanie, Magnolie, Ginkgo, Platane,
Apfelbaum, Blauregenbaum, Jacaranda, Flammenbaum, Kopfweide und Eberesche.

Stammfuß auf (0, 0, 0), groesse 0 klein · 1 mittel · 2 groß. Farbiges Laub kommt aus Biomes O' Plenty bzw.
Chipped und fällt ohne die Mods auf passendes Vanilla-Laub zurück.
"""

from __future__ import annotations

import math

import numpy as np

import modbloecke as MB
from baeume import (Pinsel, Wuchs, _laubbaum, abzweig, ast, blattwolke, bodenstreu, kugel_f, neue_welt,
                    richtung_aus_winkeln, stamm, verzweigen, wurzeln)
from lib import laub


class HolzX:
    """Holzart aus frei gewählten Blöcken (z. B. grauer Akazienstamm, gefleckte Platane)."""

    def __init__(self, w, log, wood=None):
        self.w = w
        self.log = {a: w.b(log, axis=a) for a in "xyz"}
        self.wood = {a: w.b(wood or log, axis=a) for a in "xyz"}
        self.alle = set(self.log.values()) | set(self.wood.values())


def _mod_laub(w, name, ersatz):
    return MB.mod(w, name, ersatz, {"persistent": True, "distance": 7, "waterlogged": False}
                  if ersatz.endswith("_leaves") else None, persistent=True, distance=7)


def jacaranda_laub(w):
    return _mod_laub(w, "biomesoplenty:jacaranda_leaves", "flowering_azalea_leaves")


def rot_laub(w):
    return _mod_laub(w, "biomesoplenty:maple_leaves", "nether_wart_block")


def orange_laub(w):
    return _mod_laub(w, "biomesoplenty:orange_autumn_leaves", "honeycomb_block")


def gelb_laub(w):
    return _mod_laub(w, "biomesoplenty:yellow_autumn_leaves", "hay_block")


def chipped(w, art, ersatz="oak_leaves"):
    return _mod_laub(w, f"chipped:{art}_leaves", ersatz)


def _G(groesse, werte):
    return werte[max(0, min(len(werte) - 1, groesse))]


def _flecken(w, holz_bloecke, ersatz, anteil):
    """Färbt einen Teil der Holzblöcke um (gefleckte Rinde)."""
    for p, b in list(w.bloecke.items()):
        if b in holz_bloecke and w.rng.random() < anteil:
            w.bloecke[p] = ersatz


# ============================================================================ Laubbäume

def linde(seed, groesse=1):
    """Linde: gerader Stamm, hohe, dichte, herzförmig gewölbte Krone in hellem Grün, Stockausschläge am Fuß."""
    w = neue_welt(seed)
    bl = [(laub(w, "oak"), 0.55), (laub(w, "birch"), 0.3), (laub(w, "azalea"), 0.15)]
    H = _G(groesse, [11, 18, 26])
    cfg = Wuchs(kinder=3, spreizung=(22, 40), laenge=0.64, biegung=0.08, auftrieb=0.05)
    _laubbaum(w, "oak", bl, H, _G(groesse, [0.6, 1.2, 1.9]), 0.38, cfg, _G(groesse, [1, 2, 2]),
              _G(groesse, [2.6, 3.2, 3.8]), wurzel_n=_G(groesse, [0, 5, 7]), wurzel_l=_G(groesse, [0, 3, 5]),
              neigung=2, krone_aeste=_G(groesse, [3, 5, 6]), kronen_neigung=(18, 38), luecken=0.04, flach=1.05,
              kronen_unterkante=0.9)
    bodenstreu(w, [w.b("oak_sapling", stage=0), w.b("fern")], 3 + groesse * 3, 1, 2.5)
    return w


def buche(seed, groesse=1):
    """Rotbuche: glatter, mächtiger Stamm, sehr breite, tief herabreichende dunkelgrüne Kuppel, Laubstreu."""
    w = neue_welt(seed)
    bl = [(laub(w, "dark_oak"), 0.65), (laub(w, "oak"), 0.25), (laub(w, "jungle"), 0.1)]
    H = _G(groesse, [10, 17, 24])
    cfg = Wuchs(kinder=3, spreizung=(22, 42), laenge=0.66, biegung=0.08, auftrieb=0.04)
    holz = HolzX(w, "stripped_birch_log", "stripped_birch_wood")
    pinsel = Pinsel(w, holz)
    r = _G(groesse, [0.7, 1.4, 2.1])
    st = stamm(w, pinsel, H * 0.5, r, r * 0.8, neigung=2, biegung=0.03)
    if groesse:
        wurzeln(w, pinsel, r, 5 + groesse, 2 + groesse * 2)
    enden, mitte = [], []
    for i in range(_G(groesse, [4, 5, 7])):
        d = abzweig(st[-1][1], 30 + w.rng.random() * 25, i * 360 / 6 + w.rng.random() * 40)
        verzweigen(w, pinsel, st[-1 - int(w.rng.random() * 3)][0], d, H * 0.55, max(0.5, r * 0.6),
                   _G(groesse, [1, 2, 2]), cfg, enden, mitte)
    for p, t in enden:
        rw = _G(groesse, [2.6, 3.2, 3.8]) * (0.85 + 0.3 * w.rng.random())
        blattwolke(w, p + [0, 0.4, 0], rw, rw * 0.62, bl, schutz=holz.alle, luecken=0.03, min_y=int(H * 0.35))
    for p in mitte[::2]:
        blattwolke(w, p + [0, 0.6, 0], 2.4, 1.6, bl, schutz=holz.alle, min_y=int(H * 0.35))
    _flecken(w, holz.alle, w.b("stripped_oak_wood", axis="y"), 0.06)
    bodenstreu(w, [w.b("brown_mushroom"), w.b("fern")], 4 + groesse * 4, r + 1, r + 6)
    return w


def rotahorn(seed, groesse=1):
    """Rotahorn im Herbst: runde, lockere Krone in Rot, Orange und letzten grünen Tupfen, roter Laubteppich."""
    w = neue_welt(seed)
    bl = [(rot_laub(w), 0.55), (orange_laub(w), 0.25), (chipped(w, "red_oak", "nether_wart_block"), 0.12),
          (laub(w, "oak"), 0.08)]
    H = _G(groesse, [10, 16, 23])
    cfg = Wuchs(kinder=3, spreizung=(25, 48), laenge=0.63, biegung=0.1, auftrieb=0.04)
    _laubbaum(w, "dark_oak", bl, H, _G(groesse, [0.55, 1.0, 1.6]), 0.42, cfg, _G(groesse, [1, 2, 2]),
              _G(groesse, [2.6, 3.0, 3.6]), wurzel_n=_G(groesse, [0, 4, 6]), wurzel_l=_G(groesse, [0, 3, 4]),
              neigung=4, krone_aeste=_G(groesse, [3, 4, 5]), kronen_neigung=(25, 50), luecken=0.08, flach=0.85)
    teppich = [w.b("red_carpet"), w.b("orange_carpet"), w.b("red_carpet")]
    bodenstreu(w, teppich, 14 + groesse * 16, 1, 3 + groesse * 2.5)
    return w


def pyramidenpappel(seed, groesse=1):
    """Pyramidenpappel: sehr schlank und hoch, steil aufstrebende Äste, schmale säulenförmige Krone."""
    w = neue_welt(seed)
    bl = [(laub(w, "oak"), 0.6), (laub(w, "birch"), 0.4)]
    H = _G(groesse, [14, 22, 32])
    holz = HolzX(w, "oak_log", "oak_wood")
    pinsel = Pinsel(w, holz)
    st = stamm(w, pinsel, H, _G(groesse, [0.5, 0.8, 1.2]), 0.45, neigung=1, biegung=0.01, auftrieb=0.08)
    rmax = _G(groesse, [1.8, 2.6, 3.4])
    for k in range(int(len(st) * 0.12), len(st), 2):
        p, pd, _ = st[k]
        t = k / len(st)
        rad = rmax * math.sin(min(1.0, t * 1.15) * math.pi) ** 0.6 + 0.6
        for j in range(2):
            d = abzweig(pd, 18 + w.rng.random() * 12, w.rng.random() * 360)
            pkt = ast(w, pinsel, p, d, rad * 1.2, 0.45, 0.4, biegung=0.05, auftrieb=0.05)
            blattwolke(w, pkt[-1][0], rad, 1.7, bl, schutz=holz.alle, luecken=0.06)
    blattwolke(w, st[-1][0] + [0, 0.8, 0], 1.3, 2.4, bl, schutz=holz.alle)
    return w


def baobab(seed, groesse=1):
    """Baobab: ein flaschenförmiger, gewaltiger grauer Stamm, oben kurze, knorrige Astarme mit kleinen
    Blätterbüscheln, trockene Erde ringsum."""
    w = neue_welt(seed)
    bl = [(laub(w, "acacia"), 0.7), (laub(w, "jungle"), 0.3)]
    H = _G(groesse, [9, 14, 20])
    R = _G(groesse, [1.8, 3.0, 4.4])
    holz = HolzX(w, "acacia_log", "acacia_wood")
    st = w.b("acacia_wood", axis="y")
    for y in range(0, H + 1):
        t = y / H
        r = R * (0.75 + 0.45 * math.sin(t * math.pi * 0.9 + 0.2)) * (1 - 0.35 * t)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                if math.hypot(x, z) <= r + (w.rng.random() - 0.5) * 0.3:
                    w.setze(x, y, z, st)
    pinsel = Pinsel(w, holz)
    cfg = Wuchs(kinder=2, spreizung=(30, 60), laenge=0.55, biegung=0.18, auftrieb=0.02)
    enden, mitte = [], []
    for i in range(_G(groesse, [4, 6, 8])):
        a = i / _G(groesse, [4, 6, 8]) * 360 + w.rng.random() * 30
        d = richtung_aus_winkeln(a, 55 + w.rng.random() * 20)
        start = np.array([0.5, H - 0.5, 0.5]) + np.array([math.cos(math.radians(a)), 0, math.sin(math.radians(a))]) \
            * R * 0.4
        verzweigen(w, pinsel, start, d, H * 0.45, _G(groesse, [0.6, 0.9, 1.2]), 1, cfg, enden, mitte)
    for p, t in enden:
        rw = _G(groesse, [1.6, 2.0, 2.4])
        blattwolke(w, p + [0, 0.5, 0], rw, rw * 0.55, bl, schutz=holz.alle, luecken=0.15)
    for x in range(-int(R) - 4, int(R) + 5):
        for z in range(-int(R) - 4, int(R) + 5):
            if R < math.hypot(x, z) < R + 4 and w.rng.random() < 0.5 and w.frei(x, 0, z):
                w.setze(x, 0, z, w.b("coarse_dirt" if w.rng.random() < 0.6 else "red_sand"))
    bodenstreu(w, [w.b("dead_bush")], 3 + groesse * 3, R + 1, R + 4)
    return w


def drachenbaum(seed, groesse=1):
    """Drachenbaum: kurzer kräftiger Stamm, der sich immer wieder gabelt, alle Äste streben nach oben und tragen
    eine dichte, flache Schirmkrone wie ein umgedrehter Regenschirm."""
    w = neue_welt(seed)
    bl = [(laub(w, "dark_oak"), 0.6), (laub(w, "jungle"), 0.25), (laub(w, "spruce"), 0.15)]
    H = _G(groesse, [8, 12, 17])
    holz = HolzX(w, "acacia_log", "acacia_wood")
    pinsel = Pinsel(w, holz)
    r = _G(groesse, [0.6, 1.0, 1.5])
    st = stamm(w, pinsel, H * 0.3, r, r * 0.9, neigung=0, biegung=0.02)
    cfg = Wuchs(kinder=2, spreizung=(28, 40), laenge=0.75, ansatz=0.95, biegung=0.04, auftrieb=0.03, duenn=0.75)
    enden, mitte = [], []
    for i in range(_G(groesse, [3, 4, 5])):
        d = abzweig(st[-1][1], 35 + w.rng.random() * 15, i * 360 / _G(groesse, [3, 4, 5]) + w.rng.random() * 30)
        verzweigen(w, pinsel, st[-1][0], d, H * 0.36, max(0.5, r * 0.75), _G(groesse, [2, 3, 3]), cfg, enden, mitte)
    top = max(p[1] for p, _ in enden)
    for p, t in enden:
        rw = _G(groesse, [2.2, 2.8, 3.4])
        blattwolke(w, [p[0], top + 0.3, p[2]], rw, 0.9, bl, schutz=holz.alle, dichte=0.95)
        blattwolke(w, [p[0], top - 0.6, p[2]], rw * 0.8, 0.6, bl, schutz=holz.alle, dichte=0.7)
    return w


def olivenbaum(seed, groesse=1):
    """Olivenbaum: ein knorriger, verdrehter, oft hohler Stamm, mehrere schief stehende Äste und eine lockere,
    silbrig-grüne Krone, darunter ein Fleck trockener Erde."""
    w = neue_welt(seed)
    silber = chipped(w, "frosted_oak", "azalea_leaves")
    bl = [(laub(w, "azalea"), 0.45), (silber, 0.35), (laub(w, "oak"), 0.2)]
    H = _G(groesse, [7, 11, 15])
    cfg = Wuchs(kinder=2, spreizung=(30, 60), laenge=0.6, biegung=0.3, auftrieb=0.02)
    holz = HolzX(w, "dark_oak_log", "dark_oak_wood")
    pinsel = Pinsel(w, holz)
    r = _G(groesse, [0.7, 1.2, 1.7])
    st = stamm(w, pinsel, H * 0.35, r, r * 0.8, neigung=18, biegung=0.25)
    if groesse:
        wurzeln(w, pinsel, r, 4 + groesse, 2 + groesse)
    enden, mitte = [], []
    for i in range(_G(groesse, [3, 4, 5])):
        d = abzweig(st[-1][1], 35 + w.rng.random() * 30, i * 120 + w.rng.random() * 60)
        verzweigen(w, pinsel, st[-2][0], d, H * 0.55, max(0.5, r * 0.6), _G(groesse, [1, 2, 2]), cfg, enden, mitte)
    for p, t in enden:
        rw = _G(groesse, [1.8, 2.3, 2.8])
        blattwolke(w, p + [0, 0.4, 0], rw, rw * 0.6, bl, schutz=holz.alle, luecken=0.1, dichte=0.85)
    for p in mitte:
        blattwolke(w, p + [0, 0.6, 0], 1.6, 1.0, bl, schutz=holz.alle, luecken=0.15)
    if groesse >= 1:
        for y in range(1, int(H * 0.25)):
            w.bloecke.pop((0, y, 0), None)
    for x in range(-5 - groesse * 2, 6 + groesse * 2):
        for z in range(-5 - groesse * 2, 6 + groesse * 2):
            if math.hypot(x, z) < 4 + groesse * 2 and w.frei(x, 0, z) and w.rng.random() < 0.55:
                w.setze(x, 0, z, w.b("coarse_dirt"))
    return w


def eibe(seed, groesse=1):
    """Eibe: ein vielstämmiger, rötlicher, gefurchter Stamm und eine dichte, sehr dunkle, breit eiförmige Krone
    aus Nadeln – ein uralter Friedhofs- und Parkbaum."""
    w = neue_welt(seed)
    bl = [(laub(w, "spruce"), 0.6), (laub(w, "dark_oak"), 0.4)]
    H = _G(groesse, [8, 13, 19])
    holz = HolzX(w, "mangrove_log", "mangrove_wood")
    pinsel = Pinsel(w, holz)
    enden, mitte = [], []
    cfg = Wuchs(kinder=2, spreizung=(20, 45), laenge=0.65, biegung=0.15, auftrieb=0.03)
    for i in range(_G(groesse, [2, 3, 4])):
        d = richtung_aus_winkeln(i * 360 / 3 + w.rng.random() * 40, 12 + w.rng.random() * 15)
        verzweigen(w, pinsel, [0.5 + (i % 2), 0.5, 0.5 + (i // 2)], d, H * 0.55, _G(groesse, [0.5, 0.8, 1.1]),
                   _G(groesse, [1, 2, 2]), cfg, enden, mitte)
    blattwolke(w, [0.5, H * 0.55, 0.5], _G(groesse, [3.2, 4.6, 6.2]), H * 0.5, bl, schutz=holz.alle, luecken=0.02,
               min_y=2)
    for p, t in enden:
        blattwolke(w, p + [0, 0.3, 0], 1.8, 1.4, bl, schutz=holz.alle)
    return w


# ============================================================================ Nadelbäume

def herbstlaerche(seed, groesse=1):
    """Lärche im Herbst: schlanker Kegel mit leicht hängenden Ästen und goldgelben Nadeln – der einzige
    Nadelbaum, der sich verfärbt."""
    w = neue_welt(seed)
    gold = gelb_laub(w)
    bl = [(gold, 0.6), (chipped(w, "golden_spruce", "hay_block"), 0.25), (orange_laub(w), 0.15)]
    H = _G(groesse, [13, 21, 30])
    holz = HolzX(w, "spruce_log", "spruce_wood")
    pinsel = Pinsel(w, holz)
    r = _G(groesse, [0.5, 0.9, 1.4])
    st = stamm(w, pinsel, H, r, 0.45, neigung=0, biegung=0.015, auftrieb=0.06)
    rmax = _G(groesse, [3.0, 4.6, 6.4])
    y0 = int(H * 0.2)
    for k in range(int(len(st) * 0.2), len(st) - 1, 3):
        p, _, _ = st[k]
        t = k / len(st)
        rad = rmax * (1 - t) + 0.6
        n = max(3, int(rad * 0.9))
        az0 = w.rng.random() * 360
        for j in range(n):
            d = richtung_aus_winkeln(az0 + j * 360 / n, 72 + w.rng.random() * 12)
            pkt = ast(w, pinsel, p, d, rad * 0.8, 0.45, 0.4, biegung=0.05, schwerkraft=0.05)
            for q, _, _ in pkt[1::2]:
                blattwolke(w, q + [0, 0.2, 0], 1.5, 1.0, bl, schutz=holz.alle, dichte=0.85, luecken=0.08)
    blattwolke(w, st[-1][0] + [0, 0.5, 0], 1.0, 2.0, bl, schutz=holz.alle)
    teppich = [w.b("yellow_carpet"), w.b("orange_carpet")]
    bodenstreu(w, teppich, 10 + groesse * 10, 1, 2 + rmax * 0.6)
    return w


def libanonzeder(seed, groesse=1):
    """Libanonzeder: ein mächtiger Stamm, der sich in mehrere Leittriebe teilt; die Äste bilden weit ausladende,
    waagerechte, tellerflache Nadelschichten in Etagen übereinander."""
    w = neue_welt(seed)
    bl = [(laub(w, "spruce"), 0.7), (laub(w, "dark_oak"), 0.15), (laub(w, "jungle"), 0.15)]
    H = _G(groesse, [12, 19, 27])
    holz = HolzX(w, "spruce_log", "spruce_wood")
    pinsel = Pinsel(w, holz)
    r = _G(groesse, [0.7, 1.3, 2.0])
    st = stamm(w, pinsel, H * 0.85, r, 0.6, neigung=3, biegung=0.03)
    if groesse:
        wurzeln(w, pinsel, r, 5 + groesse, 2 + groesse * 2)
    etagen = _G(groesse, [3, 4, 5])
    for e in range(etagen):
        k = int(len(st) * (0.3 + 0.62 * e / max(1, etagen - 1)))
        p, _, _ = st[min(k, len(st) - 1)]
        weite = _G(groesse, [4.5, 7.0, 10.0]) * (1 - 0.55 * e / max(1, etagen))
        for j in range(_G(groesse, [3, 4, 5])):
            d = richtung_aus_winkeln(j * 360 / 4 + w.rng.random() * 50 + e * 37, 82)
            pkt = ast(w, pinsel, p, d, weite, 0.6, 0.4, biegung=0.05, auftrieb=0.0)
            for q, _, _ in pkt[len(pkt) // 3::2]:
                blattwolke(w, q + [0, 0.4, 0], 2.2 + weite * 0.12, 0.75, bl, schutz=holz.alle, dichte=0.9)
    return w


# ============================================================================ Blütenbäume

def rosskastanie(seed, groesse=1):
    """Blühende Rosskastanie: breite, dichte, gewölbte Krone, übersät mit aufrechten weißen Blütenkerzen."""
    w = neue_welt(seed)
    bl = [(laub(w, "oak"), 0.7), (laub(w, "dark_oak"), 0.3)]
    H = _G(groesse, [10, 16, 23])
    cfg = Wuchs(kinder=3, spreizung=(25, 50), laenge=0.64, biegung=0.08, auftrieb=0.03)
    _laubbaum(w, "dark_oak", bl, H, _G(groesse, [0.6, 1.2, 1.9]), 0.4, cfg, _G(groesse, [1, 2, 2]),
              _G(groesse, [2.8, 3.4, 4.0]), wurzel_n=_G(groesse, [0, 5, 7]), wurzel_l=_G(groesse, [0, 3, 5]),
              neigung=3, krone_aeste=_G(groesse, [3, 4, 6]), kronen_neigung=(25, 48), luecken=0.02, flach=0.9)
    kerze = chipped(w, "white_flower_oak", "white_terracotta")
    for (x, y, z), b in list(w.bloecke.items()):
        if b in (bl[0][0], bl[1][0]) and w.frei(x, y + 1, z) and w.rng.random() < 0.12:
            w.setze(x, y + 1, z, kerze)
            if w.rng.random() < 0.5:
                w.setze(x, y + 2, z, w.b("white_wool") if w.rng.random() < 0.2 else kerze)
    return w


def magnolie(seed, groesse=1):
    """Magnolie: niedrig und vielstämmig, weit gespreizte, kahle Äste mit großen rosa-weißen Blütenbüscheln,
    Blütenblätter auf dem Boden."""
    w = neue_welt(seed)
    bl = [(laub(w, "cherry"), 0.55), (chipped(w, "white_flower_oak", "white_terracotta"), 0.25),
          (chipped(w, "magenta_flower_oak", "flowering_azalea_leaves"), 0.2)]
    H = _G(groesse, [7, 10, 14])
    holz = HolzX(w, "cherry_log", "cherry_wood")
    pinsel = Pinsel(w, holz)
    cfg = Wuchs(kinder=2, spreizung=(25, 50), laenge=0.66, biegung=0.16, auftrieb=0.05)
    enden, mitte = [], []
    for i in range(_G(groesse, [3, 4, 5])):
        d = richtung_aus_winkeln(i * 360 / 4 + w.rng.random() * 40, 28 + w.rng.random() * 18)
        verzweigen(w, pinsel, [0.5, 0.5, 0.5], d, H * 0.6, _G(groesse, [0.45, 0.6, 0.8]), _G(groesse, [1, 2, 2]),
                   cfg, enden, mitte)
    for p, t in enden:
        rw = 1.2 + 0.4 * w.rng.random() + groesse * 0.25
        blattwolke(w, p + [0, 0.4, 0], rw, rw * 0.75, bl, schutz=holz.alle, luecken=0.18, dichte=0.8)
    bodenstreu(w, [w.b("pink_petals", facing="north", flower_amount=4)], 12 + groesse * 12, 1, 3 + groesse * 2)
    return w


def ginkgo(seed, groesse=1):
    """Ginkgo im Herbst: aufrechter, etwas unregelmäßiger Wuchs mit kurzen Seitenästen, leuchtend goldgelbe
    Fächerblätter, gelber Blätterteppich."""
    w = neue_welt(seed)
    bl = [(gelb_laub(w), 0.65), (chipped(w, "golden_oak", "hay_block"), 0.3), (laub(w, "birch"), 0.05)]
    H = _G(groesse, [11, 17, 25])
    holz = HolzX(w, "jungle_log", "jungle_wood")
    pinsel = Pinsel(w, holz)
    st = stamm(w, pinsel, H, _G(groesse, [0.5, 0.9, 1.3]), 0.45, neigung=4, biegung=0.05, auftrieb=0.05)
    for k in range(int(len(st) * 0.3), len(st) - 1, 3):
        p, pd, _ = st[k]
        t = k / len(st)
        L = (1 - t) * _G(groesse, [3.5, 5.5, 7.5]) + 1.5
        d = abzweig(pd, 50 + w.rng.random() * 25, w.rng.random() * 360)
        pkt = ast(w, pinsel, p, d, L, 0.45, 0.4, biegung=0.1, auftrieb=0.02)
        for q, _, _ in pkt[1::2]:
            blattwolke(w, q + [0, 0.3, 0], 1.3 + groesse * 0.2, 1.0, bl, schutz=holz.alle, luecken=0.12)
    blattwolke(w, st[-1][0] + [0, 0.5, 0], 1.6, 2.0, bl, schutz=holz.alle)
    bodenstreu(w, [w.b("yellow_carpet")], 14 + groesse * 12, 1, 3 + groesse * 2)
    return w


def platane(seed, groesse=1):
    """Platane: hoher Stamm mit der typischen gefleckten, abblätternden Rinde in Grau, Oliv und Creme, weit
    ausladende, lichte Krone mit großen Blättern."""
    w = neue_welt(seed)
    bl = [(laub(w, "oak"), 0.5), (laub(w, "jungle"), 0.3), (laub(w, "birch"), 0.2)]
    H = _G(groesse, [13, 20, 29])
    cfg = Wuchs(kinder=3, spreizung=(25, 50), laenge=0.62, biegung=0.12, auftrieb=0.04)
    holz = _laubbaum(w, "birch", bl, H, _G(groesse, [0.6, 1.2, 1.8]), 0.48, cfg, _G(groesse, [1, 2, 2]),
                     _G(groesse, [2.4, 3.0, 3.6]), wurzel_n=_G(groesse, [0, 4, 6]), wurzel_l=_G(groesse, [0, 3, 4]),
                     neigung=4, krone_aeste=_G(groesse, [3, 4, 5]), kronen_neigung=(22, 45), luecken=0.12, flach=0.8)
    flecken = [w.b("stripped_birch_wood", axis="y"), w.b("stripped_oak_wood", axis="y"),
               w.b("stripped_jungle_wood", axis="y"), w.b("mushroom_stem", up=True, down=True, north=True,
                                                          south=True, east=True, west=True)]
    for p, b in list(w.bloecke.items()):
        if b in holz.alle and w.rng.random() < 0.38:
            w.bloecke[p] = flecken[int(w.rng.random() * 4)]
    return w


def apfelbaum(seed, groesse=1):
    """Apfelbaum: kurzer, krummer Stamm, runde, offene Krone voller roter Äpfel, eine angelehnte Leiter und ein
    Erntekorb im Gras."""
    w = neue_welt(seed)
    bl = [(laub(w, "oak"), 0.7), (chipped(w, "apple_oak", "oak_leaves"), 0.3)]
    H = _G(groesse, [6, 9, 12])
    cfg = Wuchs(kinder=2, spreizung=(30, 55), laenge=0.65, biegung=0.18, auftrieb=0.04)
    _laubbaum(w, "oak", bl, H, _G(groesse, [0.5, 0.7, 1.0]), 0.38, cfg, _G(groesse, [1, 1, 2]),
              _G(groesse, [2.0, 2.5, 3.0]), neigung=10, krone_aeste=_G(groesse, [3, 4, 5]),
              kronen_neigung=(35, 60), stamm_biegung=0.2, luecken=0.12, flach=0.8)
    apfel = w.b("red_terracotta")
    for (x, y, z), b in list(w.bloecke.items()):
        if b == bl[0][0] and w.frei(x, y - 1, z) and w.rng.random() < 0.08:
            w.setze(x, y - 1, z, w.b("red_mushroom_block", up=False, down=True, north=True, south=True, east=True,
                                     west=True) if w.rng.random() < 0.0 else apfel)
    w.setze(2, 1, 0, w.b("barrel", facing="up", open=True))
    if groesse:
        for k in range(1, H // 2):
            w.setze(-1 - k // 3, k, 1, w.b("ladder", facing="north", waterlogged=False), False)
    return w


def blauregenbaum(seed, groesse=1):
    """Blauregenbaum: ein uralter, verdrehter Stamm trägt ein flaches Blätterdach, von dem lange violette
    Blütentrauben wie ein Vorhang herabhängen."""
    w = neue_welt(seed)
    lila = jacaranda_laub(w)
    bl = [(laub(w, "oak"), 0.55), (laub(w, "azalea"), 0.25), (lila, 0.2)]
    H = _G(groesse, [8, 12, 17])
    cfg = Wuchs(kinder=2, spreizung=(30, 55), laenge=0.65, biegung=0.25, auftrieb=0.02)
    holz = HolzX(w, "dark_oak_log", "dark_oak_wood")
    pinsel = Pinsel(w, holz)
    r = _G(groesse, [0.6, 0.9, 1.3])
    st = stamm(w, pinsel, H * 0.5, r, r * 0.8, neigung=15, biegung=0.3)
    enden, mitte = [], []
    for i in range(_G(groesse, [3, 4, 5])):
        d = abzweig(st[-1][1], 45 + w.rng.random() * 30, i * 90 + w.rng.random() * 50)
        verzweigen(w, pinsel, st[-1][0], d, H * 0.5, max(0.45, r * 0.6), _G(groesse, [1, 2, 2]), cfg, enden, mitte)
    for p, t in enden:
        rw = _G(groesse, [2.0, 2.6, 3.2])
        blattwolke(w, p + [0, 0.3, 0], rw, rw * 0.45, bl, schutz=holz.alle, luecken=0.05)
    lila2 = chipped(w, "magenta_flower_oak", "flowering_azalea_leaves")
    for (x, y, z), b in list(w.bloecke.items()):
        if b in (bl[0][0], bl[1][0], lila) and w.frei(x, y - 1, z) and w.rng.random() < 0.35:
            for k in range(1, 2 + int(w.rng.random() * (3 + groesse * 2))):
                if y - k < 2 or not w.frei(x, y - k, z):
                    break
                w.setze(x, y - k, z, lila if w.rng.random() < 0.75 else lila2)
    return w


def jacaranda(seed, groesse=1):
    """Jacaranda: ein feingliedriger, breit schirmförmiger Baum, die Krone ganz in Lavendelblau, darunter ein
    violetter Blütenteppich."""
    w = neue_welt(seed)
    lila = jacaranda_laub(w)
    bl = [(lila, 0.8), (laub(w, "jungle"), 0.12), (laub(w, "flowering_azalea"), 0.08)]
    H = _G(groesse, [9, 14, 20])
    cfg = Wuchs(kinder=3, spreizung=(30, 55), laenge=0.6, biegung=0.12, auftrieb=0.02)
    _laubbaum(w, "jungle", bl, H, _G(groesse, [0.5, 0.9, 1.4]), 0.45, cfg, _G(groesse, [1, 2, 2]),
              _G(groesse, [2.6, 3.0, 3.6]), wurzel_n=_G(groesse, [0, 3, 5]), wurzel_l=_G(groesse, [0, 2, 4]),
              neigung=6, krone_aeste=_G(groesse, [3, 4, 5]), kronen_neigung=(40, 65), luecken=0.06, flach=0.55)
    bodenstreu(w, [w.b("purple_carpet"), w.b("magenta_carpet")], 14 + groesse * 14, 1, 3 + groesse * 3)
    return w


def flammenbaum(seed, groesse=1):
    """Flammenbaum: ein ausladender, flacher Schirm aus feurig rotem und orangem Laub auf einem glatten,
    geteilten Stamm – leuchtet wie ein Lagerfeuer in der Landschaft."""
    w = neue_welt(seed)
    bl = [(rot_laub(w), 0.45), (orange_laub(w), 0.35), (chipped(w, "orange_oak", "honeycomb_block"), 0.1),
          (laub(w, "jungle"), 0.1)]
    H = _G(groesse, [8, 12, 17])
    cfg = Wuchs(kinder=3, spreizung=(45, 70), laenge=0.62, biegung=0.1, auftrieb=0.0)
    _laubbaum(w, "acacia", bl, H, _G(groesse, [0.5, 0.9, 1.3]), 0.4, cfg, _G(groesse, [1, 2, 2]),
              _G(groesse, [2.4, 2.9, 3.4]), wurzel_n=_G(groesse, [0, 4, 6]), wurzel_l=_G(groesse, [0, 3, 4]),
              neigung=5, krone_aeste=_G(groesse, [4, 5, 6]), kronen_neigung=(55, 75), luecken=0.05, flach=0.45)
    return w


def kopfweide(seed, groesse=1):
    """Kopfweide: ein kurzer, dicker, hohler Stamm mit knolligem Kopf, aus dem ein Schopf gerader, dünner Ruten
    senkrecht emporschießt; Brennnesseln und Schilf am Fuß."""
    w = neue_welt(seed)
    bl = [(laub(w, "oak"), 0.4), (laub(w, "azalea"), 0.3), (chipped(w, "frosted_birch", "birch_leaves"), 0.3)]
    H = _G(groesse, [4, 6, 8])
    R = _G(groesse, [1.2, 1.8, 2.5])
    holz = w.b("oak_wood", axis="y")
    for y in range(0, H + 1):
        r = R * (1.0 + 0.35 * (y / H) ** 3)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(x, z)
                if d <= r and (d > r - 1.2 or y == H):
                    w.setze(x, y, z, holz)
    for x in range(-1, 2):
        w.bloecke.pop((x, 1, int(R)), None)
        w.bloecke.pop((x, 2, int(R)), None)
    rng = w.rng
    for k in range(_G(groesse, [7, 12, 18])):
        a = rng.random() * 6.283
        d = rng.random() * R
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        L = _G(groesse, [4, 6, 8]) + int(rng.integers(0, 4))
        for y in range(H + 1, H + 1 + L):
            w.setze(x, y, z, w.b("oak_fence", north=False, south=False, east=False, west=False, waterlogged=False))
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if rng.random() < 0.3:
                    w.setze(x + dx, y, z + dz, bl[int(rng.random() * 3)][0], False)
    bodenstreu(w, [w.b("fern"), w.b("sugar_cane", age=0), w.b("grass")], 6 + groesse * 4, R + 1, R + 3)
    return w


def eberesche(seed, groesse=1):
    """Eberesche: schlanker Stamm, lockere, gefiederte Krone in hellem Grün mit leuchtend roten Beerendolden."""
    w = neue_welt(seed)
    bl = [(laub(w, "birch"), 0.45), (laub(w, "oak"), 0.4), (laub(w, "azalea"), 0.15)]
    H = _G(groesse, [8, 13, 18])
    cfg = Wuchs(kinder=2, spreizung=(25, 45), laenge=0.64, biegung=0.1, auftrieb=0.05)
    _laubbaum(w, "birch", bl, H, _G(groesse, [0.45, 0.7, 1.0]), 0.45, cfg, _G(groesse, [1, 2, 2]),
              _G(groesse, [2.0, 2.4, 2.9]), neigung=5, krone_aeste=_G(groesse, [3, 4, 4]), kronen_neigung=(25, 45),
              luecken=0.2, flach=0.75)
    beere = chipped(w, "red_oak", "red_terracotta")
    for (x, y, z), b in list(w.bloecke.items()):
        if b in (bl[0][0], bl[1][0]) and w.frei(x, y - 1, z) and w.rng.random() < 0.1:
            w.setze(x, y - 1, z, beere)
    return w


BAEUME2 = {
    "linde": ("Linde", linde),
    "buche": ("Rotbuche", buche),
    "rotahorn": ("Rotahorn im Herbst", rotahorn),
    "pyramidenpappel": ("Pyramidenpappel", pyramidenpappel),
    "baobab": ("Baobab", baobab),
    "drachenbaum": ("Drachenbaum", drachenbaum),
    "olivenbaum": ("Olivenbaum", olivenbaum),
    "eibe": ("Eibe", eibe),
    "herbstlaerche": ("Lärche im Herbst", herbstlaerche),
    "libanonzeder": ("Libanonzeder", libanonzeder),
    "rosskastanie": ("Blühende Rosskastanie", rosskastanie),
    "magnolie": ("Magnolie", magnolie),
    "ginkgo": ("Ginkgo", ginkgo),
    "platane": ("Platane", platane),
    "apfelbaum": ("Apfelbaum", apfelbaum),
    "blauregenbaum": ("Blauregenbaum", blauregenbaum),
    "jacaranda": ("Jacaranda", jacaranda),
    "flammenbaum": ("Flammenbaum", flammenbaum),
    "kopfweide": ("Kopfweide", kopfweide),
    "eberesche": ("Eberesche", eberesche),
}

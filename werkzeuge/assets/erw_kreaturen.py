"""Kreaturen III – zwanzig weitere Riesentiere und Fabelwesen: Riesenschildkröte, Mammut, Nashorn, Giraffe,
Ruhender Löwe, Säbelzahntiger, Krokodil, Chamäleon, Pfau, Flamingos, Riesenlibelle, Schmetterling, Seepferdchen,
Mantarochen, Basilisk, Chimäre, Kentaur, Riesenadler, Waldgeist und Panda. Kopf jeweils nach +z."""

from __future__ import annotations

import math

import numpy as np

from kreaturen import SICHT, U, _stil, _welt, glied
from kreaturen2 import SEITE, _rendern, bein, fell, fluegel
from lib import ueberwuchern
from skulptur import Skulptur, ell, kap, kasten, kegel, spiegel_x, torus, und


def auge(S, x, y, z, r=0.45, pupille=True):
    S.plus(ell(x, y, z, r, r, r * 0.8), "w")
    if pupille:
        S.plus(ell(x + (0.1 if x > 0 else -0.1), y, z + r * 0.4, r * 0.5, r * 0.6, r * 0.5), "d")


def basis(w, u):
    S = Skulptur(w, u)
    S.mat("w", w.b("white_concrete"))
    S.mat("d", w.b("black_concrete"))
    S.mat("g", w.b("gold_block"))
    S.mat("k", w.b("bone_block", axis="y"))
    return S


# ============================================================================ Tiere

def riesenschildkroete(seed, g=2):
    """Riesenschildkröte: eine uralte Landschildkröte mit hochgewölbtem, bemoostem Panzer aus Platten, faltigem
    Hals und Elefantenfüßen, auf dem Rücken wachsen Farne und Blumen."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("h", fell(w, "Haut", ["gray_terracotta", "light_gray_terracotta", "tuff", "andesite"]), basis=1, rausch=1)
    rng = np.random.default_rng(seed)
    zent = rng.normal(size=(14, 3)) * [4, 2, 5]

    def panzer(x, y, z, lx, ly, lz):
        d = np.sqrt(((zent - [lx, ly - 7, lz]) ** 2).sum(1))
        o = np.sort(d)[:2]
        if o[1] - o[0] < 0.8:
            return w.b("dark_oak_planks")
        return w.b(["brown_terracotta", "terracotta", "mud_bricks", "packed_mud"][int(np.argmin(d)) % 4])
    S.mat("p", panzer)
    S.plus(und(ell(0, 5, 0, 6.5, 6.5, 8.0), lambda X, Y, Z: Y > 3), "p")
    S.plus(ell(0, 3.6, 0, 6.8, 1.2, 8.2), "h")
    for sx in (-1, 1):
        for sz in (-1, 1):
            S.plus(kap((sx * 4.5, 3.5, sz * 5.0), (sx * 5.0, 0.5, sz * 5.4), 1.7, 1.9), "h")
    glied(S, [(0, 4.5, 7.0), (0, 6.5, 10.0), (0, 7.5, 12.0)], [1.6, 1.3, 1.2], "h")
    S.plus(ell(0, 7.8, 13.0, 1.8, 1.5, 2.2), "h")
    auge(S, 1.3, 8.3, 14.0, 0.35)
    auge(S, -1.3, 8.3, 14.0, 0.35)
    S.plus(kap((0, 4.0, -8.0), (0, 3.0, -9.6), 0.8, 0.3), "h")
    _rendern(S, (-9, -1, -11), (9, 13, 16), w, dreh=SEITE)
    ueberwuchern(w, None, ranken=0.0, moos_oben=0.6, pflanzen=0.4, buesche=0.03)
    return w


def mammut(seed, g=2):
    """Mammut: ein zotteliges Wollhaarmammut mit gebogenen Stoßzähnen, hohem Schulterbuckel und langem Fell, das
    bis zu den Knien hängt, Schnee auf dem Rücken."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("h", fell(w, "Fell", ["brown_wool", "brown_terracotta", "dark_oak_planks", "spruce_planks"]), basis=0.5,
          rausch=1.4)
    S.mat("s", w.b("snow_block"))
    S.plus(ell(0, 11, 0, 5.4, 5.4, 8.0), "h")
    S.plus(ell(0, 14, 3.5, 4.2, 4.0, 3.5), "h")
    for sx in (-1, 1):
        for sz in (-1, 1):
            S.plus(kap((sx * 3.0, 8, sz * 4.6), (sx * 3.2, 0.6, sz * 4.8), 2.3, 1.9), "h")
        glied(S, [(sx * 1.6, 11, 10.2), (sx * 2.4, 7.5, 12.5), (sx * 1.5, 7.2, 15.0), (sx * 0.4, 9.5, 16.0)],
              [0.6, 0.6, 0.5, 0.3], "k")
        auge(S, sx * 2.2, 14.0, 10.2, 0.35)
    S.plus(ell(0, 13, 9.0, 3.2, 3.6, 3.0), "h")
    glied(S, [(0, 11.5, 11.4), (0, 8, 12.8), (0, 4.5, 13.4), (0, 2.6, 12.6)], [1.3, 1.1, 0.9, 0.7], "h")
    S.plus(und(ell(0, 12, 0, 5.5, 5.5, 8.0), lambda X, Y, Z: Y > 15.6), "s")
    _rendern(S, (-8, -1, -10), (8, 20, 18), w, dreh=SEITE)
    return w


def nashorn(seed, g=2):
    """Nashorn: ein schweres Panzernashorn mit gefalteten Hautplatten, zwei Hörnern, kleinen Ohren und einem
    Madenhacker-Vogel auf dem Rücken."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("h", fell(w, "Haut", ["gray_terracotta", "andesite", "light_gray_terracotta", "stone"]), basis=0.6,
          rausch=1.2)
    S.mat("v", w.b("brown_concrete"))
    S.plus(ell(0, 6.5, 0, 4.2, 4.0, 7.5), "h")
    S.plus(und(ell(0, 6.5, 0, 4.4, 4.2, 7.7), lambda X, Y, Z: np.abs(Z - 2.5) < 0.4), "h")
    for sx in (-1, 1):
        for sz in (-1, 1):
            S.plus(kap((sx * 2.6, 5, sz * 4.2), (sx * 2.8, 0.5, sz * 4.4), 1.5, 1.4), "h")
        S.plus(kap((sx * 1.4, 9.4, 9.4), (sx * 1.8, 10.8, 8.8), 0.5, 0.3), "h")
        auge(S, sx * 1.6, 7.6, 11.2, 0.3)
    S.plus(kap((0, 7.0, 7.0), (0, 5.5, 13.0), 2.6, 1.8), "h")
    S.plus(kap((0, 6.2, 12.6), (0, 10.0, 14.2), 0.9, 0.2), "k")
    S.plus(kap((0, 7.3, 10.6), (0, 9.2, 11.4), 0.6, 0.2), "k")
    S.plus(ell(0, 11.0, -1.0, 0.6, 0.6, 0.9), "v")
    _rendern(S, (-6, -1, -9), (6, 14, 16), w, dreh=SEITE)
    return w


def giraffe(seed, g=2):
    """Giraffe: eine hochgewachsene Giraffe mit gemustertem Fell aus orangen und hellen Flecken, langem Hals,
    Hörnchen und schwarzer Zunge, die an einer Akazie knabbert."""
    w = _welt(seed)
    S = basis(w, U[g])
    rng = np.random.default_rng(seed)
    fl = rng.normal(size=(40, 3)) * [3, 10, 4] + [0, 12, 2]

    def muster(x, y, z, lx, ly, lz):
        d = np.sqrt(((fl - [lx, ly, lz]) ** 2).sum(1))
        o = np.sort(d)[:2]
        return w.b("white_terracotta") if o[1] - o[0] < 0.55 else w.b(["orange_terracotta", "brown_terracotta"]
                                                                       [int(np.argmin(d)) % 2])
    S.mat("h", muster)
    S.mat("l", w.b("acacia_leaves", persistent=True, distance=1, waterlogged=False))
    S.mat("s", w.b("acacia_log", axis="y"))
    S.plus(ell(0, 11, 0, 2.8, 2.8, 5.0), "h")
    for sx in (-1, 1):
        for sz in (-1, 1):
            S.plus(kap((sx * 1.6, 10, sz * 3.2), (sx * 1.6, 0.4, sz * 3.4 + 0.4), 0.8, 0.6), "h")
        S.plus(kap((sx * 0.6, 24.6, 6.2), (sx * 0.7, 26.0, 5.8), 0.3), "h")
        auge(S, sx * 0.9, 24.2, 7.4, 0.3)
    glied(S, [(0, 12, 3.8), (0, 18, 5.0), (0, 23, 6.0)], [1.6, 1.2, 0.9], "h")
    S.plus(ell(0, 24, 7.2, 1.1, 1.0, 1.8), "h")
    S.plus(kap((0, 11.5, -4.8), (0, 6.5, -5.4), 0.25), "h")
    S.plus(kap((6, 0, 9), (6, 20, 9), 0.7), "s")
    S.plus(ell(6, 22, 9, 4.5, 1.5, 4.5), "l")
    _rendern(S, (-6, -1, -7), (12, 28, 14), w, dreh=SEITE)
    return w


def loewe(seed, g=2):
    """Ruhender Löwe: ein majestätischer Löwe liegt mit gekreuzten Vorderpranken da, die Mähne fällt in schweren
    Locken, der Schwanz mit Quaste ringelt sich neben ihm."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("h", fell(w, "Fell", ["yellow_terracotta", "orange_terracotta", "smooth_sandstone", "yellow_terracotta"]),
          basis=1, rausch=1)
    S.mat("m", fell(w, "Mähne", ["brown_terracotta", "orange_terracotta", "brown_wool", "terracotta"]), basis=1,
          rausch=1.5)
    S.plus(ell(0, 3.2, -1, 3.6, 3.0, 7.0), "h")
    for sx in (-1, 1):
        S.plus(kap((sx * 1.6, 1.0, 5.0), (sx * 0.8, 0.8, 10.4), 1.1, 1.0), "h")
        S.plus(ell(sx * 2.4, 2.2, -5.0, 1.6, 2.2, 2.6), "h")
        auge(S, sx * 1.0, 7.3, 9.0, 0.3)
    S.plus(ell(0, 6.2, 6.6, 3.8, 3.8, 2.8), "m")
    S.plus(ell(0, 6.6, 8.0, 2.0, 2.2, 2.0), "h")
    S.plus(ell(0, 5.8, 9.6, 1.1, 0.9, 0.9), "h")
    S.plus(ell(0, 6.3, 10.4, 0.4, 0.3, 0.3), "d")
    glied(S, [(0, 2.5, -7.5), (2.6, 0.8, -9.5), (5.4, 0.8, -8.0)], [0.4, 0.35, 0.3], "h")
    S.plus(ell(5.8, 0.8, -7.4, 0.7, 0.6, 0.7), "m")
    _rendern(S, (-6, -1, -11), (8, 11, 12), w, dreh=SEITE)
    return w


def saebelzahntiger(seed, g=2):
    """Säbelzahntiger: eine gedrungene Raubkatze mit gewaltigen Eckzähnen, gestreiftem Fell und kurzem Schwanz,
    auf einem Felsen kauernd, sprungbereit."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("h", lambda x, y, z, lx, ly, lz: w.b("brown_terracotta" if int(lz * 1.2) % 3 == 0 else
                                                "orange_terracotta" if (x + y) % 5 else "yellow_terracotta"))
    S.mat("f", fell(w, "Fels", ["stone", "andesite", "cobblestone", "mossy_cobblestone"]), basis=1.5, rausch=1.5)
    S.plus(ell(0, 1.8, 0, 6, 2.2, 8), "f")
    S.plus(ell(0, 7.0, 0, 3.0, 2.8, 6.0), "h")
    for sx in (-1, 1):
        bein(S, (sx * 2.0, 6.2, 4.2), (sx * 2.2, 4.8, 6.0), (sx * 2.0, 3.8, 7.6), 1.1, "h")
        bein(S, (sx * 2.0, 6.0, -4.0), (sx * 2.4, 4.6, -2.4), (sx * 2.2, 3.8, -5.0), 1.3, "h")
        S.plus(kap((sx * 0.7, 8.6, 10.4), (sx * 0.8, 6.2, 11.0), 0.3, 0.12), "w")
        auge(S, sx * 1.0, 10.4, 10.0, 0.3)
    S.plus(ell(0, 9.6, 8.8, 2.2, 2.0, 2.4), "h")
    S.plus(ell(0, 9.0, 10.6, 1.2, 1.0, 1.2), "h")
    S.plus(kap((0, 7.6, -6), (0, 8.2, -7.8), 0.6, 0.4), "h")
    _rendern(S, (-7, -1, -9), (7, 13, 13), w, dreh=SEITE)
    return w


def krokodil(seed, g=2):
    """Krokodil: ein riesiges Krokodil mit geschupptem Panzerrücken, aufgerissenem Maul voller Zähne und
    gewundenem Schwanz, halb im Uferschlamm."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("h", lambda x, y, z, lx, ly, lz: w.b("green_terracotta" if (int(lz) + int(lx * 1.5)) % 3 else
                                                "moss_block" if ly > 1.8 else "lime_terracotta"))
    S.mat("m", w.b("pink_terracotta"))
    S.mat("u", w.b("mud"))
    S.plus(ell(0, 0, 0, 8, 0.8, 12), "u")
    S.plus(ell(0, 1.6, 0, 3.0, 1.6, 6.5), "h")
    pts = [(0, 1.5, -5.5), (1.5, 1.2, -10), (4.5, 1.0, -13), (7.5, 0.8, -13.5), (9.0, 0.7, -11.5)]
    glied(S, pts, [2.2, 1.6, 1.1, 0.7, 0.3], "h")
    for sx in (-1, 1):
        for sz in (-1, 1):
            bein(S, (sx * 2.4, 1.4, sz * 3.6), (sx * 4.0, 1.2, sz * 4.2), (sx * 4.4, 0.4, sz * 5.4), 0.8, "h")
        auge(S, sx * 1.2, 3.4, 7.4, 0.35)
    S.plus(kap((0, 1.8, 6.0), (0, 1.3, 13.0), 1.6, 1.0), "h")
    S.plus(kap((0, 3.2, 6.6), (0, 6.2, 12.2), 1.5, 0.9), "h")
    S.plus(kap((0, 2.2, 7.2), (0, 4.4, 11.8), 1.0, 0.6), "m")
    for k in range(5):
        z = 8 + k * 1.0
        for sx in (-1, 1):
            S.plus(ell(sx * 1.0, 2.6 + (z - 7) * 0.15, z, 0.18, 0.4, 0.18), "w")
    _rendern(S, (-9, -1, -15), (11, 8, 15), w, dreh=SEITE)
    return w


def chamaeleon(seed, g=1):
    """Chamäleon: ein buntes Riesenchamäleon mit Helmkamm und Kugelaugen klammert sich mit Greiffüßen an einen
    Ast, sein Ringelschwanz ist eingerollt, die Haut schillert in Regenbogenstreifen."""
    w = _welt(seed)
    S = basis(w, U[g])
    farben = ["lime_terracotta", "green_terracotta", "cyan_terracotta", "yellow_terracotta", "orange_terracotta"]
    S.mat("h", lambda x, y, z, lx, ly, lz: w.b(farben[int((lz + 20) * 0.6) % 5]))
    S.mat("a", w.b("dark_oak_log", axis="z"))
    S.plus(kap((0, 2.0, -12), (0, 4.0, 12), 1.0), "a")
    S.plus(ell(0, 7.2, 0, 2.2, 3.0, 5.4), "h")
    S.plus(ell(0, 9.6, 6.0, 1.6, 2.0, 2.4), "h")
    S.plus(kap((0, 11.0, 5.2), (0, 12.2, 3.2), 0.9, 0.3), "h")
    for sx in (-1, 1):
        S.plus(ell(sx * 1.4, 9.8, 7.0, 0.9, 0.9, 0.9), "h")
        S.plus(ell(sx * 2.1, 9.8, 7.3, 0.3, 0.3, 0.3), "d")
        bein(S, (sx * 1.6, 6.0, 3.0), (sx * 2.4, 4.4, 3.8), (sx * 1.2, 4.6, 4.6), 0.6, "h")
        bein(S, (sx * 1.6, 6.0, -3.0), (sx * 2.4, 4.4, -3.6), (sx * 1.2, 4.6, -4.6), 0.6, "h")
    pts = [(0, 7, -5), (0, 5, -8), (0, 2, -8.5), (0, 0.8, -7), (0, 1.6, -5.6), (0, 2.6, -6.4)]
    glied(S, pts, [1.0, 0.8, 0.6, 0.45, 0.35, 0.3], "h")
    _rendern(S, (-4, -1, -13), (4, 14, 13), w, dreh=SEITE)
    return w


def pfau(seed, g=2):
    """Pfau: ein Pfau schlägt ein gewaltiges Rad aus schillernden Schwanzfedern mit Augenflecken in Blau, Grün und
    Gold, der Hals glänzt tiefblau, auf dem Kopf ein Federkrönchen."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("b", w.b("blue_concrete"))
    S.mat("c", w.b("cyan_concrete"))

    def rad(x, y, z, lx, ly, lz):
        r = math.hypot(lx, ly - 3)
        a = math.atan2(ly - 3, lx)
        fe = (a * 9) % (2 * math.pi / 9 * 9) if False else (a * 18 / math.pi)
        dfeder = abs(fe - round(fe))
        ring = r % 3.2
        if ring > 2.3 and dfeder < 0.35:
            return w.b("blue_concrete") if ring > 2.8 else w.b("gold_block")
        return w.b("lime_terracotta" if (int(r) + int(fe)) % 2 else "green_concrete")
    S.mat("r", rad)

    def schweif(X, Y, Z):
        r = np.hypot(X, Y - 3)
        return (r <= 12) & (Y >= 1.5) & (np.abs(Z + 2.0 + 0.04 * r * r) <= 0.6)
    S.plus(schweif, "r")
    S.plus(ell(0, 4, 0.5, 1.8, 2.4, 2.4), "b")
    glied(S, [(0, 5.5, 1.5), (0, 8.5, 2.2), (0, 10.0, 2.8)], [1.0, 0.7, 0.6], "b")
    S.plus(ell(0, 10.4, 3.2, 0.8, 0.8, 1.0), "b")
    S.plus(kap((0, 10.2, 4.0), (0, 9.9, 4.8), 0.25, 0.1), "g")
    for k in (-0.6, 0, 0.6):
        S.plus(kap((k, 11.0, 3.0), (k * 1.5, 12.6, 2.8), 0.12), "c")
    for sx in (-1, 1):
        S.plus(kap((sx * 0.6, 2.2, 0.6), (sx * 0.7, 0, 0.8), 0.25), "d")
    _rendern(S, (-13, -1, -10), (13, 16, 6), w, dreh=SICHT)
    return w


def flamingos(seed, g=1):
    """Flamingos: drei rosafarbene Riesenflamingos stehen auf einem Bein in einer Lagune, mit gebogenen Hälsen und
    schwarz gespitzten Schnäbeln, einer putzt sich das Gefieder."""
    w = _welt(seed)
    u = U[g]
    S = basis(w, u)
    S.mat("p", fell(w, "Rosa", ["pink_concrete", "pink_terracotta", "pink_wool", "magenta_terracotta"]), basis=1,
          rausch=1)
    S.mat("b", w.b("pink_terracotta"))
    S.mat("wa", w.b("water", level=0))
    S.plus(ell(0, -0.2, 0, 13, 0.6, 9), "wa")
    for k, (cx, cz, dreh) in enumerate(((0, 0, 0), (-7, -3, 1), (6, -4, -1))):
        S.plus(ell(cx, 9, cz, 1.8, 1.8, 3.0), "p")
        S.plus(kap((cx, 8, cz), (cx, 0, cz), 0.3), "b")
        S.plus(kap((cx, 7.5, cz - 0.5), (cx + 0.6, 6.5, cz + 1.0), 0.25), "b")
        glied(S, [(cx, 10, cz + 2.4), (cx, 13, cz + 3.6), (cx, 15, cz + 2.4), (cx, 16, cz + 3.4)],
              [0.6, 0.5, 0.45, 0.5], "p")
        S.plus(kap((cx, 16.0, cz + 3.8), (cx, 14.6, cz + 5.0), 0.35, 0.2), "w")
        S.plus(ell(cx, 14.5, cz + 5.1, 0.3, 0.4, 0.3), "d")
        auge(S, cx + 0.4, 16.2, cz + 3.6, 0.2, pupille=False)
    _rendern(S, (-14, -1, -10), (14, 18, 10), w)
    return w


def riesenlibelle(seed, g=2):
    """Riesenlibelle: eine schimmernde Libelle mit zwei Paar gläsernen Flügeln voller Adern, langem segmentiertem
    Leib in Türkis und großen Facettenaugen, sie sitzt auf einem Schilfhalm."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("t", lambda x, y, z, lx, ly, lz: w.b("cyan_concrete" if int(lz) % 2 else "light_blue_concrete"))
    S.mat("f", lambda x, y, z, lx, ly, lz: w.b("light_gray_stained_glass" if (int(lx * 1.3) + int(lz)) % 3 else
                                               "black_stained_glass"))
    S.mat("e", w.b("blue_concrete"))
    S.mat("s", w.b("lime_terracotta"))
    S.plus(kap((3, 0, -6), (3, 10, -6), 0.5), "s")
    glied(S, [(0, 10, 3), (0, 10, -4), (0, 10.2, -10)], [1.1, 0.7, 0.5], "t")
    S.plus(ell(0, 10.4, 4.2, 1.6, 1.3, 1.6), "t")
    S.plus(spiegel_x(ell(1.1, 11.0, 5.0, 1.0, 1.0, 1.0)), "e")
    for sz, lang in ((3.2, 11), (1.4, 10)):
        S.plus(lambda X, Y, Z, sz=sz, lang=lang: (np.abs(X) > 1) & (np.abs(X) < lang) & (np.abs(Y - 10.8) < 0.5)
               & (np.abs(Z - sz) < 1.3 * (1 - (np.abs(X) / lang) ** 2) + 0.2), "f")
    _rendern(S, (-12, -1, -11), (12, 13, 7), w)
    return w


def schmetterling(seed, g=2):
    """Riesenschmetterling: ein farbenprächtiger Falter mit weit geöffneten Flügeln voller Augenflecken in Orange,
    Schwarz und Blau ruht auf einer großen Blüte."""
    w = _welt(seed)
    S = basis(w, U[g])

    def flu(x, y, z, lx, ly, lz):
        r1 = math.hypot(abs(lx) - 5, ly - 12)
        r2 = math.hypot(abs(lx) - 3.5, ly - 6.5)
        if r1 < 1.2 or r2 < 0.8:
            return w.b("light_blue_concrete")
        if r1 < 2.0 or r2 < 1.4:
            return w.b("black_concrete")
        rand = abs(lx) > 7.2 or ly > 14.5
        return w.b("black_concrete" if rand else "orange_concrete" if (int(abs(lx)) + int(ly)) % 4 else
                   "yellow_concrete")
    S.mat("f", flu)
    S.mat("b", w.b("brown_concrete"))
    S.mat("bl", w.b("pink_concrete"))
    S.mat("st", w.b("lime_terracotta"))

    def fluegel_f(X, Y, Z):
        ob = ((np.abs(X) - 4.5) / 4.0) ** 2 + ((Y - 12) / 4.0) ** 2 <= 1
        un = ((np.abs(X) - 3.0) / 2.8) ** 2 + ((Y - 6.8) / 2.6) ** 2 <= 1
        return (ob | un) & (np.abs(Z) <= 0.6) & (np.abs(X) > 0.6)
    S.plus(fluegel_f, "f")
    S.plus(kap((0, 5.5, 0), (0, 13.5, 0), 0.7), "b")
    S.plus(ell(0, 14.4, 0, 0.9, 0.9, 0.9), "b")
    for sx in (-1, 1):
        S.plus(kap((sx * 0.3, 15, 0), (sx * 1.8, 17.5, 0.4), 0.15), "b")
    S.plus(kap((0, 0, 0), (0, 4, 0), 0.5), "st")
    for k in range(6):
        a = k / 6 * 6.283
        S.plus(ell(math.cos(a) * 2.2, 4.6, math.sin(a) * 2.2, 1.6, 0.5, 1.6), "bl")
    S.plus(ell(0, 5.0, 0, 1.2, 0.6, 1.2), "g")
    _rendern(S, (-10, -1, -5), (10, 19, 5), w)
    return w


def seepferdchen(seed, g=2):
    """Riesenseepferdchen: ein aufrecht schwebendes Seepferdchen mit geringeltem Leib, Rückenflosse und
    eingerolltem Schwanz, der sich um eine Korallensäule schlingt."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("h", lambda x, y, z, lx, ly, lz: w.b("orange_terracotta" if int(ly) % 2 else "yellow_terracotta"))
    S.mat("f", w.b("yellow_stained_glass"))
    S.mat("ko", fell(w, "Koralle", ["fire_coral_block", "brain_coral_block", "horn_coral_block"]), basis=1, rausch=1)
    S.plus(kap((0, 0, -3), (0, 10, -3), 1.2, 0.8), "ko")
    pts = [(0, 14, 0), (0, 11, 1.2), (0, 8, 0.8), (0, 5.5, -0.8), (0, 3.6, -2.4), (0, 3.0, -3.6),
           (0, 3.8, -4.4), (0, 4.6, -3.6)]
    glied(S, pts, [2.0, 2.2, 1.8, 1.3, 0.9, 0.6, 0.5, 0.4], "h")
    S.plus(ell(0, 15.6, 0.8, 1.6, 1.7, 1.6), "h")
    S.plus(kap((0, 15.6, 1.6), (0, 14.8, 4.4), 0.6, 0.45), "h")
    S.plus(kap((0, 17.0, 0.4), (0, 18.0, -0.4), 0.5, 0.2), "h")
    S.plus(lambda X, Y, Z: (np.abs(X) < 0.5) & (Y > 9) & (Y < 12.5) & (Z < -0.6) & (Z > -3.2 + (Y - 9) * 0.3), "f")
    for sx in (-1, 1):
        auge(S, sx * 1.1, 16.0, 1.6, 0.35)
    _rendern(S, (-4, -1, -6), (4, 20, 6), w, dreh=SEITE)
    return w


def mantarochen(seed, g=2):
    """Mantarochen: ein gewaltiger Mantarochen gleitet knapp über dem Meeresboden, die Flügel weit ausgebreitet,
    die Kopfflossen eingerollt, Bauch weiß, Rücken dunkelblau mit Punkten."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("r", lambda x, y, z, lx, ly, lz: w.b("white_concrete") if ly < 4.0 else w.b(
        "light_blue_terracotta" if (int(lx * 2) * 7 + int(lz * 2) * 3) % 13 == 0 else "blue_terracotta"))
    S.mat("sa", w.b("sand"))
    S.mat("ko", fell(w, "Koralle", ["tube_coral_block", "bubble_coral_block", "brain_coral_block"]), basis=1,
          rausch=1)

    def koerper(X, Y, Z):
        sp = 13 * np.clip(1 - np.abs(Z / 6.0) ** 1.6, 0, 1) * np.clip(1 - (np.maximum(0, -Z) / 8), 0, 1)
        dick = 1.4 * np.clip(1 - np.abs(X) / np.maximum(sp, 0.1), 0, 1) + 0.3
        yc = 4.5 + 0.6 * (np.abs(X) / 13) ** 2 * 6
        return (np.abs(X) <= sp) & (np.abs(Y - yc) <= dick) & (Z > -6) & (Z < 6)
    S.plus(koerper, "r")
    S.plus(kap((0, 4.4, -5), (0, 4.0, -14), 0.4, 0.15), "r")
    for sx in (-1, 1):
        S.plus(kap((sx * 1.4, 4.4, 5.5), (sx * 1.6, 3.6, 7.2), 0.5, 0.4), "r")
    S.plus(ell(0, -0.3, 0, 15, 0.6, 10), "sa")
    S.plus(ell(9, 1.2, 6, 1.6, 1.4, 1.6), "ko")
    S.plus(ell(-10, 1.0, -5, 1.2, 1.2, 1.4), "ko")
    _rendern(S, (-16, -1, -15), (16, 9, 11), w)
    return w


# ============================================================================ Fabelwesen

def basilisk(seed, g=2):
    """Basilisk: eine riesige Schlange mit gezacktem Rückenkamm und Krone aus Hornstacheln richtet sich drohend auf,
    die gelben Augen glühen, der Leib liegt in mächtigen Windungen."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("h", lambda x, y, z, lx, ly, lz: w.b("green_terracotta" if (int(ly * 1.5) + int(lx)) % 3 else
                                                "lime_terracotta"))
    S.mat("y", w.b("yellow_concrete"))
    S.mat("rk", w.b("red_terracotta"))
    pts = []
    for i in range(40):
        t = i / 39
        a = t * 6.283 * 1.4
        r = 7 * (1 - 0.55 * t)
        pts.append((math.cos(a) * r, 1.2 + t * 2, math.sin(a) * r))
    pts += [(1.5, 5, 3.0), (0.8, 9, 4.0), (0, 13, 4.6), (0, 15, 6.0)]
    glied(S, pts, [2.0 - 0.6 * i / len(pts) for i in range(len(pts))], "h")
    S.plus(ell(0, 15.4, 7.2, 1.8, 1.4, 2.6), "h")
    for sx in (-1, 1):
        S.plus(ell(sx * 1.3, 16.0, 8.6, 0.45, 0.45, 0.4), "y")
    for k in range(6):
        a = (k - 2.5) * 0.35
        S.plus(kap((math.sin(a) * 1.2, 16.4, 6.4), (math.sin(a) * 2.6, 19.0 - abs(k - 2.5) * 0.4, 5.6), 0.35, 0.1),
               "rk")
    for (x, y, z) in pts[::3]:
        S.plus(kap((x, y + 1.6, z), (x, y + 2.8, z), 0.35, 0.1), "rk")
    _rendern(S, (-10, -1, -10), (10, 21, 11), w)
    return w


def chimaere(seed, g=2):
    """Chimäre: ein Löwenkörper mit Ziegenkopf auf dem Rücken, ledrigen Flügeln und einem Schlangenschwanz mit
    eigenem Kopf – ein Fabelwesen aus drei Tieren."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("h", fell(w, "Fell", ["yellow_terracotta", "orange_terracotta", "smooth_sandstone"]), basis=1, rausch=1)
    S.mat("m", fell(w, "Mähne", ["brown_terracotta", "brown_wool", "orange_terracotta"]), basis=1, rausch=1.5)
    S.mat("z", w.b("white_terracotta"))
    S.mat("s", w.b("green_terracotta"))
    S.mat("f", fell(w, "Flügel", ["red_terracotta", "brown_terracotta", "red_terracotta"]), basis=1, rausch=0.6)
    S.plus(ell(0, 7, 0, 3.4, 3.2, 6.5), "h")
    for sx in (-1, 1):
        for sz in (-1, 1):
            bein(S, (sx * 2.0, 6, sz * 3.8), (sx * 2.2, 3, sz * 4.2), (sx * 2.0, 0.6, sz * 4.4), 1.1, "h")
        fluegel(S, sx, 9.5, -0.5, 10, 6, 5, "f", kante="h", neig=0.2)
        auge(S, sx * 1.0, 11.6, 9.2, 0.3)
    S.plus(ell(0, 10.0, 7.0, 3.4, 3.4, 2.4), "m")
    S.plus(ell(0, 10.6, 8.4, 1.9, 2.0, 1.9), "h")
    glied(S, [(0, 9.5, -1), (0, 13, 0), (0, 15, 0.6)], [1.0, 0.8, 0.7], "z")
    S.plus(ell(0, 15.6, 1.4, 1.0, 1.0, 1.4), "z")
    for sx in (-1, 1):
        glied(S, [(sx * 0.6, 16.4, 0.8), (sx * 1.6, 17.6, -0.4), (sx * 2.0, 17.0, -1.6)], [0.3, 0.25, 0.15], "k")
    glied(S, [(0, 6.5, -6.0), (0, 5.0, -9.0), (2.0, 7.0, -11.0), (2.4, 9.5, -10.0)], [0.8, 0.7, 0.6, 0.6], "s")
    S.plus(ell(2.4, 10.2, -9.4, 0.9, 0.8, 1.2), "s")
    _rendern(S, (-12, -1, -13), (12, 19, 12), w, dreh=SEITE)
    return w


def kentaur(seed, g=2):
    """Kentaur: halb Pferd, halb Krieger – ein Kentaur mit braunem Pferdeleib, muskulösem Oberkörper, Lorbeerkranz
    und einem gespannten Bogen, die Mähne weht."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("h", fell(w, "Fell", ["brown_terracotta", "dark_oak_planks", "brown_concrete"]), basis=1, rausch=1)
    S.mat("t", fell(w, "Haut", ["smooth_sandstone", "birch_planks", "smooth_sandstone"]), basis=1, rausch=0.6)
    S.mat("l", w.b("lime_terracotta"))
    S.mat("bo", w.b("dark_oak_planks"))
    S.plus(ell(0, 9, -1, 2.8, 2.8, 5.6), "h")
    for sx in (-1, 1):
        for sz in (-1, 1):
            bein(S, (sx * 1.6, 8, sz * 3.6 - 1), (sx * 1.7, 4, sz * 3.9 - 1), (sx * 1.6, 0.6, sz * 4.2 - 1), 0.9,
                 "h", huf="d")
    glied(S, [(0, 9, -6.4), (0, 7, -8.6), (0, 4, -9.2)], [0.8, 0.6, 0.4], "d")
    S.plus(kap((0, 10, 3.2), (0, 16, 4.0), 1.8, 2.0), "t")
    S.plus(ell(0, 17.8, 4.2, 1.1, 1.3, 1.2), "t")
    S.plus(torus(0, 18.6, 4.2, 1.1, 0.3), "l")
    S.plus(kap((0, 18.6, 3.4), (0, 15.5, 2.4), 0.8, 0.4), "d")
    S.plus(kap((1.8, 15.4, 4.0), (3.0, 14.2, 7.6), 0.5), "t")
    S.plus(kap((-1.8, 15.4, 4.0), (-1.0, 15.0, 6.0), 0.5), "t")
    S.plus(lambda X, Y, Z: (np.abs(np.hypot(Y - 14.2, Z - 4.4) - 3.8) < 0.35) & (Z > 6.6) & (np.abs(X - 3.0) < 0.5),
           "bo")
    _rendern(S, (-6, -1, -10), (6, 21, 11), w, dreh=SEITE)
    return w


def riesenadler(seed, g=2):
    """Riesenadler: ein Adler mit ausgebreiteten Schwingen landet auf einem Felszacken, die Fänge vorgestreckt, der
    weiße Kopf mit gelbem Hakenschnabel blickt scharf nach vorn."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("h", fell(w, "Gefieder", ["brown_terracotta", "dark_oak_planks", "brown_concrete", "spruce_planks"]),
          basis=1, rausch=1)
    S.mat("y", w.b("yellow_concrete"))
    S.mat("f", fell(w, "Fels", ["stone", "andesite", "tuff"]), basis=1, rausch=1.5)
    S.plus(kegel(0, 0, 0, 7, 3.5, 1.2), "f")
    S.plus(ell(0, 11, 0, 2.6, 3.6, 2.4), "h")
    S.plus(ell(0, 15.2, 0.6, 1.8, 1.9, 1.9), "w")
    S.plus(kap((0, 15.0, 2.0), (0, 14.0, 3.6), 0.6, 0.25), "y")
    for sx in (-1, 1):
        fluegel(S, sx, 13, -0.6, 15, 4, 5, "h", kante="h", neig=0.1, schwung=0.25)
        bein(S, (sx * 1.0, 8.4, 0.6), (sx * 1.0, 7.4, 1.4), (sx * 0.9, 7.2, 2.0), 0.5, "y")
        auge(S, sx * 1.0, 15.6, 1.8, 0.25)
    S.plus(lambda X, Y, Z: (np.abs(X) < 2.2) & (Y > 7.5) & (Y < 9.5) & (Z < -1.5) & (Z > -5), "w")
    _rendern(S, (-16, -1, -7), (16, 19, 5), w)
    return w


def waldgeist(seed, g=2):
    """Waldgeist: ein großer, sanfter Waldgeist aus Moos, Rinde und Laub mit einem Hirschgeweih aus Ästen und
    leuchtenden Augen, an seinen Armen wachsen Pilze und Blumen."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("h", fell(w, "Moos", ["moss_block", "mossy_cobblestone", "green_terracotta", "moss_block"]), basis=1,
          rausch=1.5)
    S.mat("r", w.b("dark_oak_wood", axis="y"))
    S.mat("l", w.b("shroomlight"))
    S.mat("lb", w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False))
    S.plus(kegel(0, 0, 0, 10, 4.5, 2.6), "h")
    S.plus(ell(0, 12, 0, 3.0, 3.6, 2.6), "h")
    S.plus(ell(0, 16.4, 0.4, 2.0, 2.2, 2.0), "r")
    for sx in (-1, 1):
        S.plus(ell(sx * 0.8, 16.8, 2.2, 0.4, 0.4, 0.3), "l")
        glied(S, [(sx * 2.6, 13.4, 0), (sx * 4.6, 10, 1.4), (sx * 5.0, 6.8, 2.4)], [1.0, 0.8, 0.6], "r")
        glied(S, [(sx * 1.0, 18, 0), (sx * 2.4, 21, -0.4), (sx * 4.0, 23.6, 0)], [0.4, 0.32, 0.2], "r")
        glied(S, [(sx * 2.4, 21, -0.4), (sx * 3.8, 21.4, 1.0)], [0.25, 0.15], "r")
        glied(S, [(sx * 3.2, 22.4, -0.2), (sx * 3.0, 24.8, -1.2)], [0.2, 0.12], "r")
        S.plus(ell(sx * 4.4, 11.0, 1.6, 1.4, 0.9, 1.2), "lb")
    _rendern(S, (-7, -1, -5), (7, 26, 5), w)
    ueberwuchern(w, None, ranken=0.06, moos_oben=0.3, pflanzen=0.5, buesche=0.0)
    return w


def panda(seed, g=2):
    """Panda: ein großer, gemütlich sitzender Pandabär mit schwarz-weißem Fell kaut an einem Bambusstängel, um ihn
    herum wächst ein kleines Bambuswäldchen."""
    w = _welt(seed)
    S = basis(w, U[g])
    S.mat("bam", w.b("bamboo_block", axis="y"))
    S.plus(ell(0, 5, -0.5, 4.2, 4.6, 4.0), "w")
    S.plus(und(ell(0, 5, -0.5, 4.3, 4.7, 4.1), lambda X, Y, Z: (Y > 6.0) & (Y < 8.2)), "d")
    S.plus(ell(0, 11, 0.6, 3.0, 2.8, 2.7), "w")
    for sx in (-1, 1):
        S.plus(ell(sx * 2.2, 13.4, 0.2, 0.9, 0.9, 0.6), "d")
        S.plus(ell(sx * 1.1, 11.6, 2.8, 0.7, 0.6, 0.3), "d")
        S.plus(ell(sx * 1.1, 11.6, 3.0, 0.25, 0.25, 0.2), "w")
        S.plus(kap((sx * 2.6, 1.4, 2.0), (sx * 2.4, 1.2, 5.4), 1.4, 1.2), "d")
        S.plus(kap((sx * 3.4, 7.8, 0.4), (sx * 1.6, 9.0, 3.6), 1.2, 1.0), "d")
    S.plus(ell(0, 10.4, 3.2, 1.0, 0.8, 0.6), "w")
    S.plus(ell(0, 10.8, 3.8, 0.3, 0.25, 0.2), "d")
    S.plus(kap((1.2, 6, 4.0), (-0.6, 14, 3.4), 0.35), "bam")
    for (x, z) in ((7, -3), (8, 2), (-7, -4), (-8, 1), (6, -6)):
        S.plus(kap((x, 0, z), (x, 14 + (x + z) % 4, z), 0.45), "bam")
    _rendern(S, (-9, -1, -7), (9, 19, 7), w)
    return w


KREATUREN3 = {
    "riesenschildkroete": ("Riesenschildkröte", riesenschildkroete),
    "mammut": ("Mammut", mammut),
    "nashorn": ("Nashorn", nashorn),
    "giraffe": ("Giraffe an der Akazie", giraffe),
    "loewe": ("Ruhender Löwe", loewe),
    "saebelzahntiger": ("Säbelzahntiger", saebelzahntiger),
    "krokodil": ("Krokodil", krokodil),
    "chamaeleon": ("Chamäleon", chamaeleon),
    "pfau": ("Pfau", pfau),
    "flamingos": ("Flamingos", flamingos),
    "riesenlibelle": ("Riesenlibelle", riesenlibelle),
    "schmetterling": ("Riesenschmetterling", schmetterling),
    "seepferdchen": ("Riesenseepferdchen", seepferdchen),
    "mantarochen": ("Mantarochen", mantarochen),
    "basilisk": ("Basilisk", basilisk),
    "chimaere": ("Chimäre", chimaere),
    "kentaur": ("Kentaur", kentaur),
    "riesenadler": ("Riesenadler", riesenadler),
    "waldgeist": ("Waldgeist", waldgeist),
    "panda": ("Panda im Bambus", panda),
}

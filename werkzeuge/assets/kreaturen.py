"""Kreaturen – Paket: riesige Gestalten als begehbare Statuen. Größen 0 klein · 1 mittel · 2 riesig ·
3 gigantisch, je zwei Stile. Alle schauen zur Vorschau-Seite (diagonal), im Spiel frei drehbar."""

from __future__ import annotations

import math

import numpy as np

from lib import Verlauf, Welt, laub, ueberwuchern
from skulptur import Skulptur, dreh_y, ell, kap, kasten, kegel, scheibe, spiegel_x, torus, und

U = [0.6, 1.0, 1.7, 2.8]
SICHT = dreh_y(math.pi / 4)          # Gesicht (+z) zur Vorschau-Kamera drehen


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def glied(S, pts, radien, etikett):
    """Kette von Kapseln durch mehrere Punkte (Arm, Bein, Fangarm …)."""
    for (a, b), (ra, rb) in zip(zip(pts, pts[1:]), zip(radien, radien[1:])):
        S.plus(kap(a, b, ra, rb), etikett)


def _rendern(S, lo, hi, w, boden_weg=True):
    S.rendern(lo, hi, versatz=(0.5, 0, 0.5), dreh=SICHT)
    if boden_weg:
        w.bloecke = {p: b for p, b in w.bloecke.items() if p[1] >= 0}


# ============================================================================ Riesenork

def riesenork(seed, g=2):
    """Riesiger Ork im Ausschreiten: vorgebeugt, Hauer, glühende Augen, Stachelkeule über der Schulter,
    Schulterpanzer mit Dornen, Lendenschurz, Gürtel mit Schädel und Knochenkette."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        haut = Verlauf(w, "Orkhaut", ["green_terracotta", "moss_block", "green_concrete", "lime_terracotta"])
    else:
        haut = Verlauf(w, "Grauhaut", ["gray_terracotta", "light_gray_terracotta", "tuff", "andesite"])
    S = Skulptur(w, u)
    S.mat("h", haut, basis=0.3, steigung=2.6 / 20, rausch=0.7)
    S.mat("r", Verlauf(w, "Rüstung", ["blackstone", "polished_blackstone", "polished_deepslate"]), basis=1, rausch=1.2)
    S.mat("l", w.b("brown_wool"))
    S.mat("g", w.b("brown_terracotta"))
    S.mat("k", w.b("bone_block", axis="y"))
    S.mat("e", w.b("redstone_block"))
    S.mat("w", Verlauf(w, "Keule", ["dark_oak_log", "stripped_dark_oak_log", "spruce_log"]), basis=1, rausch=1.5)
    S.mat("d", w.b("iron_block"))
    # Beine im Schritt
    glied(S, [(-1.8, 9, 0.3), (-2.0, 5, 2.8), (-1.9, 1.1, 3.4)], [2.0, 1.6, 1.15], "h")
    glied(S, [(1.8, 9, -0.3), (2.0, 4.8, -1.6), (1.9, 1.3, -3.8)], [2.0, 1.6, 1.15], "h")
    S.plus(ell(-1.9, 0.8, 4.3, 1.2, 0.85, 1.9), "h")
    S.plus(ell(1.9, 0.9, -3.0, 1.2, 0.85, 1.9), "h")
    # Becken, Bauch, Oberkörper
    S.plus(ell(0, 9.3, 0, 3.4, 1.9, 2.5), "h")
    S.plus(kap((0, 9.5, 0), (0, 16, 1.5), 3.4, 4.4, zf=0.8), "h")
    S.plus(ell(0, 11.5, 1.7, 3.1, 2.6, 2.3), "h")
    S.plus(ell(0, 16.5, 0.8, 5.0, 2.1, 2.9), "h")
    # Lendenschurz und Gürtel mit Schädel
    S.plus(lambda X, Y, Z: (np.abs(X) < 1.6) & (Y > 4.8) & (Y < 9.2)
           & (np.abs(Z - 2.5 - 0.25 * np.sin(Y * 1.4)) < 0.45), "l")
    S.plus(und(kap((0, 9.6, 0), (0, 10.4, 0.3), 3.65, 3.75, zf=0.82), lambda X, Y, Z: (Y > 9.4) & (Y < 10.6)), "g")
    S.plus(ell(0, 10, 3.2, 0.8, 0.8, 0.5), "k")
    # Kopf mit Hauern, Brauen, Ohren, Augen
    S.plus(ell(0, 17.3, 4.2, 2.3, 2.3, 2.4), "h")
    S.plus(ell(0, 16.2, 5.1, 2.3, 1.2, 1.8), "h")
    S.plus(kap((-1.7, 18.3, 5.9), (1.7, 18.3, 5.9), 0.6), "h")
    S.plus(spiegel_x(kap((1.3, 16.4, 6.3), (1.5, 18.1, 6.7), 0.45, 0.15)), "k")
    S.plus(spiegel_x(kap((2.2, 17.6, 3.8), (3.7, 18.9, 3.1), 0.6, 0.15)), "h")
    S.plus(spiegel_x(ell(0.9, 17.8, 6.2, 0.38, 0.3, 0.28)), "e")
    # Knochenkette
    for i in range(7):
        a = -1.2 + i * 0.4
        S.plus(ell(math.sin(a) * 2.6, 15.2 - 0.3 * math.cos(a * 2), 2.4 + math.cos(a) * 1.4, 0.35, 0.5, 0.35), "k")
    # Arm mit Keule über der Schulter
    glied(S, [(-4.6, 16, 0.8), (-6.3, 13, 3.0), (-4.5, 16.5, 4.6)], [1.5, 1.3, 1.1], "h")
    S.plus(ell(-4.5, 16.6, 4.6, 1.3, 1.3, 1.3), "h")
    S.plus(kap((-4.5, 15.2, 5.6), (-2.6, 24.5, -3.4), 0.7, 1.7), "w")
    for k in range(6):
        t = 0.55 + k * 0.08
        cx, cy, cz = -4.5 + 1.9 * t, 15.2 + 9.3 * t, 5.6 - 9.0 * t
        a = k * 2.1
        S.plus(kap((cx, cy, cz), (cx + 2.2 * math.cos(a), cy + 0.6, cz + 2.2 * math.sin(a)), 0.3, 0.1), "d")
    # Hängender Arm mit Faust und Schulterpanzer
    glied(S, [(4.6, 16, 0.8), (6.1, 11.5, 1.8), (5.3, 7.6, 3.0)], [1.5, 1.35, 1.15], "h")
    S.plus(ell(5.2, 7.0, 3.2, 1.4, 1.4, 1.4), "h")
    S.plus(ell(4.9, 17.1, 0.8, 2.3, 1.5, 2.3), "r")
    for k in range(3):
        S.plus(kap((4.3 + k * 0.8, 18, 0.8 - 0.8 + k * 0.8), (4.3 + k * 0.9, 20.2, 0.3 + k * 0.6), 0.45, 0.08), "d")
    _rendern(S, (-9, -1, -7), (9, 27, 9), w)
    return w


# ============================================================================ Versteinerter Troll

def steintroll(seed, g=2):
    """Versteinerter Troll, gebückt mit einer Hand am Boden: Knollennase, Buckel mit Gras und Büschen,
    Moos, Ranken und Risse. Stil 2: Schneetroll."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        stein = Verlauf(w, "Troll", ["mossy_cobblestone", "mossy_stone_bricks", "cobblestone", "andesite", "stone",
                                     "tuff"])
    else:
        stein = Verlauf(w, "Schneetroll", ["tuff", "andesite", "stone", "calcite", "snow_block"])
    S = Skulptur(w, u)
    S.mat("s", stein, basis=0.3, steigung=4 / 13, rausch=1.3)
    S.mat("d", w.b("blackstone"))
    S.mat("m", Verlauf(w, "Gesicht", ["andesite", "stone", "smooth_stone"]) if _stil(seed) == 0 else
          Verlauf(w, "Gesicht", ["andesite", "calcite"]), basis=0.8, rausch=1.0)
    S.plus(ell(0, 7, -1.0, 5.5, 4.8, 4.3), "s")                               # Buckel
    S.plus(ell(0, 4.5, 1.2, 4, 3.5, 3.2), "s")                                # Bauch
    S.plus(kap((0, 9, 2), (0, 10.5, 4.5), 1.6), "s")                          # Hals
    S.plus(ell(0, 11, 6.0, 2.7, 2.6, 2.5), "m")                               # Kopf
    S.plus(kap((0, 11.3, 8.0), (0, 8.6, 9.9), 1.05, 0.8), "m")                # Knollennase
    S.plus(ell(0, 8.4, 9.9, 1.15, 0.95, 0.95), "m")
    S.plus(kap((-1.9, 12.4, 7.6), (1.9, 12.4, 7.6), 0.65), "s")              # Brauenwulst
    S.plus(spiegel_x(kasten(0.6, 11.4, 7.9, 1.5, 11.8, 8.5)), "d")           # geschlossene Augen
    S.plus(kasten(-1.5, 9.0, 7.6, 1.5, 9.35, 8.6), "d")                      # Mund
    S.plus(spiegel_x(kap((2.4, 11.4, 5.2), (4.4, 12.6, 4.2), 0.9, 0.3)), "m") # große Ohren
    glied(S, [(-4.5, 9, 1), (-6.2, 5, 3.6), (-5.6, 0.9, 6.2)], [1.7, 1.45, 1.2], "s")
    for k in (-0.7, 0, 0.7):
        S.plus(kap((-5.6, 0.7, 6.2), (-5.6 + k * 1.4, 0.4, 7.6), 0.42, 0.3), "s")
    glied(S, [(4.5, 9, 1), (5.6, 5, 4.2), (3.6, 4.6, 5.6)], [1.7, 1.45, 1.2], "s")
    S.plus(ell(3.5, 4.6, 5.8, 1.2, 1.1, 1.2), "s")
    for sx in (-1, 1):
        glied(S, [(sx * 2.5, 3, 0), (sx * 3.1, 3.6, 4), (sx * 3.1, 0.6, 1.6)], [1.9, 1.5, 1.2], "s")
        S.plus(ell(sx * 3.1, 0.6, 2.6, 1.3, 0.7, 2.1), "s")
    S.minus(lambda X, Y, Z: (np.abs(np.sin(X * 0.9 + Z * 0.4) * np.cos(Y * 0.7 - X * 0.2)) < 0.025) & (Y > 2))
    _rendern(S, (-9, -1, -7), (9, 15, 12), w)
    ueberwuchern(w, None, ranken=0.45, moos_oben=0.75 if _stil(seed) == 0 else 0.0, pflanzen=0.4,
                 buesche=0.12 if _stil(seed) == 0 else 0.0, max_ranke=max(2, int(4 * u)))
    if _stil(seed) == 1:
        oben = {}
        for (x, y, z), b in w.bloecke.items():
            if b and y > oben.get((x, z), -1):
                oben[(x, z)] = y
        for (x, z), y in oben.items():
            if y > 3 * u:
                w.setze(x, y + 1, z, w.b("snow", layers=1 + int(w.rng.random() * 2)))
    return w


# ============================================================================ Golem

def golem(seed, g=2):
    """Riesiger Felsgolem aus losen Brocken in Gorilla-Haltung: leuchtender Kern in der Brust,
    glühende Adern, Kristalle auf den Schultern. Stil 1: Lava, Stil 2: Kristall."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        stein = Verlauf(w, "Lavastein", ["blackstone", "basalt", "smooth_basalt", "cobbled_deepslate"])
        ader, kern, kristall = "magma_block", "shroomlight", "orange_stained_glass"
    else:
        stein = Verlauf(w, "Kristallstein", ["deepslate", "cobbled_deepslate", "tuff", "calcite"])
        ader, kern, kristall = "amethyst_block", "sea_lantern", "amethyst_block"
    aid = w.b(ader)
    S = Skulptur(w, u)

    def mat(x, y, z, lx, ly, lz):
        if abs(math.sin(lx * 0.8 + ly * 0.35) * math.cos(lz * 0.7 - ly * 0.2)) < 0.07:
            return aid
        return stein(0.5 + 2.5 * ly / 18 + w.rng.random() * 0.9, x, y, z)
    S.mat("s", mat)
    S.mat("k", w.b(kern))
    S.mat("c", w.b(kristall))
    S.plus(ell(0, 12, 0, 5, 4.5, 3.5), "s")                                   # Rumpf
    S.plus(ell(0, 7.8, 0, 3.4, 2.4, 2.6), "s")                                # Becken
    S.plus(ell(0, 17.2, 1.4, 2.0, 1.8, 1.9), "s")                             # Kopf
    S.plus(spiegel_x(kasten(0.4, 17.3, 3.0, 1.3, 17.7, 3.4)), "k")           # Augenschlitze
    S.minus(ell(0, 12.4, 3.1, 1.7, 1.7, 1.5))                                 # Brusthöhle
    S.plus(ell(0, 12.4, 2.2, 1.2, 1.2, 1.1), "k")                             # Kern
    for sx in (-1, 1):
        S.plus(ell(sx * 6, 15, 0, 2.8, 2.6, 2.6), "s")                        # Schulterbrocken
        S.plus(ell(sx * 7, 11, 0.6, 1.8, 2.6, 1.8), "s")
        S.plus(ell(sx * 7.6, 6.4, 1.6, 2.2, 3.0, 2.2), "s")
        S.plus(ell(sx * 7.6, 2.3, 2.2, 2.6, 2.3, 2.6), "s")                   # Fäuste am Boden
        S.plus(ell(sx * 2.8, 4.8, 0, 2.0, 3.0, 2.0), "s")
        S.plus(ell(sx * 3.0, 1.1, 0.8, 2.4, 1.2, 2.8), "s")
        for k in range(4):
            a = k * 1.6 + (0 if sx > 0 else 0.8)
            base = (sx * 6 + math.cos(a) * 1.2, 16.8, math.sin(a) * 1.2)
            S.plus(kap(base, (base[0] + sx * (0.8 + k * 0.3), base[1] + 2.2 + k * 0.5, base[2] * 1.4), 0.65, 0.12),
                   "c")
    _rendern(S, (-11, -1, -6), (11, 22, 7), w)
    return w


# ============================================================================ Baumriese

def baumriese(seed, g=2):
    """Wandelnder Baumriese: Wurzelbeine, Rindenkörper mit Gesicht, Äste als Arme mit Zweigfingern,
    blühende Laubkrone, Moos und Ranken."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        rinde = Verlauf(w, "Rinde", ["dark_oak_log", "spruce_log", "dark_oak_wood" if False else "stripped_spruce_log",
                                     "mangrove_log"])
        blatt = [laub(w, "oak"), laub(w, "flowering_azalea"), laub(w, "azalea"), laub(w, "oak")]
        auge = "shroomlight"
    else:
        rinde = Verlauf(w, "Silberrinde", ["birch_log", "stripped_birch_log", "calcite", "mushroom_stem" if False else
                                           "smooth_quartz"])
        blatt = [laub(w, "cherry"), laub(w, "cherry"), laub(w, "birch"), laub(w, "flowering_azalea")]
        auge = "sea_lantern"
    S = Skulptur(w, u)
    S.mat("r", rinde, basis=0.4, steigung=0.08, rausch=1.6)
    S.mat("e", w.b(auge))
    S.mat("d", w.b("dark_oak_log"))
    S.mat("l", lambda x, y, z, *_: blatt[int(w.rng.integers(len(blatt)))])
    for sx, vor in ((-1, 1), (1, -1)):
        hip = (sx * 1.8, 9, 0)
        knie = (sx * 2.2, 5, vor * 2.2)
        fuss = (sx * 2.2, 1, vor * 3.4)
        glied(S, [hip, knie, fuss], [1.8, 1.5, 1.3], "r")
        for k in range(3):
            a = (k - 1) * 0.7
            glied(S, [fuss, (fuss[0] + math.sin(a) * 2.4, 0.5, fuss[2] + vor * math.cos(a) * 2.6),
                      (fuss[0] + math.sin(a) * 3.6, 0.2, fuss[2] + vor * math.cos(a) * 3.6)], [0.8, 0.55, 0.3], "r")
    S.plus(kap((0, 9, 0), (0, 20, 0.6), 3.6, 3.0, zf=0.9), "r")
    S.plus(spiegel_x(ell(1.2, 17.2, 3.1, 0.55, 0.4, 0.3)), "e")
    S.plus(ell(0, 14.8, 3.0, 1.1, 0.6, 0.4), "d")
    S.plus(kap((-1.6, 18, 3.1), (1.6, 18, 3.1), 0.45), "r")
    for sx in (-1, 1):
        sh = (sx * 3, 18.5, 0)
        el = (sx * 7.2, 15.5, 1.4 * (1 if sx > 0 else 2))
        ha = (sx * 9.2, 11.5 if sx > 0 else 19, 3)
        glied(S, [sh, el, ha], [1.4, 1.0, 0.7], "r")
        for k in range(4):
            a = (k - 1.5) * 0.5
            glied(S, [ha, (ha[0] + sx * math.cos(a) * 2.2, ha[1] + math.sin(a) * 2.2 - (1.5 if sx > 0 else -1.5),
                           ha[2] + 1)], [0.45, 0.2], "r")
        S.plus(ell(el[0], el[1] + 1.5, el[2], 2.3, 1.6, 2.3), "l")
    for (cx, cy, cz, r) in ((0, 23, 0, 5.5), (-3.5, 21.5, -1, 3.5), (3.6, 22, -0.5, 3.6), (0, 25.5, -1, 4)):
        S.plus(lambda X, Y, Z, cx=cx, cy=cy, cz=cz, r=r: ((X - cx) / r) ** 2 + ((Y - cy) / (r * 0.7)) ** 2
               + ((Z - cz) / r) ** 2 <= 1 + 0.25 * np.sin(X * 1.7) * np.cos(Z * 1.5 + Y), "l")
    _rendern(S, (-13, -1, -8), (13, 30, 9), w)
    ueberwuchern(w, None, ranken=0.35, moos_oben=0.3, pflanzen=0.1, buesche=0.0, max_ranke=max(2, int(4 * u)))
    return w


# ============================================================================ Krakenarme

def krakenarme(seed, g=2):
    """Fangarme einer unterirdischen Riesenkrake brechen aus einem Krater: geschwungen, mit Saugnäpfen,
    um ein dunkles Loch mit glimmendem Auge."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        haut = Verlauf(w, "Krake", ["nether_wart_block", "red_terracotta", "magenta_terracotta", "pink_terracotta"])
        napf = "pink_terracotta"
    else:
        haut = Verlauf(w, "Tiefsee", ["dark_prismarine", "warped_wart_block", "prismarine", "cyan_terracotta"])
        napf = "light_blue_terracotta"
    S = Skulptur(w, u)
    S.mat("h", haut, basis=0.3, steigung=0.2, rausch=1.0)
    S.mat("s", w.b(napf))
    S.mat("b", Verlauf(w, "Erde", ["coarse_dirt", "rooted_dirt", "cobblestone", "gravel"]), basis=1, rausch=3)
    S.mat("e", w.b("yellow_concrete"))
    S.mat("p", w.b("black_concrete"))
    S.mat("o", w.b("black_concrete"))
    S.plus(ohne_rand := (lambda X, Y, Z: (np.sqrt(X * X + Z * Z) < 9.5 + np.sin(np.arctan2(Z, X) * 7))
                         & (np.sqrt(X * X + Z * Z) > 4.5) & (Y < 1.5 - 0.15 * np.abs(np.sqrt(X * X + Z * Z) - 7))
                         & (Y >= 0)), "b")
    S.plus(ell(0, -0.2, 0, 4.5, 0.6, 4.5), "o")
    S.plus(ell(1.2, 0.3, 1.2, 1.3, 0.7, 1.3), "e")
    S.plus(ell(1.5, 0.6, 1.5, 0.5, 0.5, 0.5), "p")
    for i in range(7):
        a = i * 2 * math.pi / 7 + 0.3
        hoehe = 10 + 4 * ((i * 3) % 4)
        pts, rr = [], []
        for k in range(16):
            t = k / 15
            r = 3.5 + 6 * t
            ang = a + 0.6 * t
            y = hoehe * math.sin(math.pi * min(1, t * 0.95)) * (1.2 - 0.4 * t)
            curl = max(0, t - 0.75) / 0.25
            pts.append((math.cos(ang) * r - math.cos(ang) * curl * 3, y + curl * 2, math.sin(ang) * r - math.sin(ang)
                        * curl * 3))
            rr.append(1.6 * (1 - t * 0.85) + 0.3)
        glied(S, pts, rr, "h")
        for k in range(3, 14, 2):
            x, y, z = pts[k]
            S.plus(ell(x - math.cos(a) * rr[k] * 0.8, y, z - math.sin(a) * rr[k] * 0.8, 0.4, 0.4, 0.4), "s")
    _rendern(S, (-13, -1, -13), (13, 22, 13), w)
    return w


# ============================================================================ Riesenwurm

def riesenwurm(seed, g=2):
    """Gepanzerter Riesenwurm, der sich in zwei Bögen aus dem Boden wölbt; vorne ein aufgerissenes Maul mit
    Zahnkranz. Erdwälle, wo er ein- und austaucht."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        panzer = Verlauf(w, "Wüstenwurm", ["brown_terracotta", "terracotta", "cut_sandstone", "smooth_sandstone"])
        boden = Verlauf(w, "Sand", ["sand", "sandstone", "sand"])
    else:
        panzer = Verlauf(w, "Höhlenwurm", ["deepslate_tiles", "purple_terracotta", "polished_deepslate", "tuff"])
        boden = Verlauf(w, "Erde", ["coarse_dirt", "rooted_dirt", "gravel"])
    S = Skulptur(w, u)
    S.mat("a", panzer, basis=0.6, rausch=0.5)
    S.mat("b", panzer, basis=2.6, rausch=0.5)
    S.mat("m", w.b("nether_wart_block"))
    S.mat("z", w.b("bone_block", axis="y"))
    S.mat("e", boden, basis=1, rausch=2)

    def bogen(x0, x1, h, z0, z1, n=26):
        return [(x0 + (x1 - x0) * t, -3 + h * math.sin(math.pi * t), z0 + (z1 - z0) * t) for t in np.linspace(0, 1, n)]
    teil1 = bogen(-16, -3, 11, -2, 0)
    for k, p in enumerate(teil1):
        S.plus(ell(*p, 2.4, 2.4, 2.4), "a" if k % 2 else "b")
    pts = [(1, -3, 1), (3, 4, 1.5), (6, 9.5, 2.2), (9.5, 12.5, 3), (13, 13.5, 3.5)]
    for k in range(len(pts) - 1):
        for t in np.linspace(0, 1, 7):
            p = tuple(np.array(pts[k]) * (1 - t) + np.array(pts[k + 1]) * t)
            S.plus(ell(*p, 2.8, 2.8, 2.8), "a" if int(t * 6 + k * 7) % 2 else "b")
    kx, ky, kz = 13.8, 13.6, 3.6
    S.plus(torus(kx + 1.4, ky, kz, 2.5, 1.0, achse="x"), "b")
    S.plus(ell(kx + 1.0, ky, kz, 0.7, 2.0, 2.0), "m")
    for i in range(12):
        a = i * math.pi / 6
        y0, z0 = ky + math.cos(a) * 2.2, kz + math.sin(a) * 2.2
        S.plus(kap((kx + 2.2, y0, z0), (kx + 2.6, ky + math.cos(a) * 1.3, kz + math.sin(a) * 1.3), 0.35, 0.1), "z")
    for (x, z) in ((-16, -2), (-3, 0), (1, 1)):
        S.plus(lambda X, Y, Z, x=x, z=z: ((X - x) ** 2 + (Z - z) ** 2 < 16) & ((X - x) ** 2 + (Z - z) ** 2 > 4)
               & (Y >= 0) & (Y < 1.6 - 0.25 * np.sqrt((X - x) ** 2 + (Z - z) ** 2)), "e")
    _rendern(S, (-20, -1, -8), (19, 18, 9), w)
    return w


# ============================================================================ Zyklop

def zyklop(seed, g=2):
    """Sitzender Zyklop auf einem Felsblock: großes Auge, Horn, Bart, Lendenschurz, Keule an den Fels gelehnt."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        haut = Verlauf(w, "Haut", ["brown_terracotta", "terracotta", "orange_terracotta", "white_terracotta"])
    else:
        haut = Verlauf(w, "Blauhaut", ["blue_terracotta", "light_blue_terracotta", "cyan_terracotta", "light_gray_terracotta"])
    S = Skulptur(w, u)
    S.mat("h", haut, basis=0.4, steigung=2.4 / 20, rausch=0.7)
    S.mat("f", Verlauf(w, "Fels", ["cobblestone", "andesite", "stone", "mossy_cobblestone"]), basis=1, rausch=2)
    S.mat("l", w.b("brown_wool"))
    S.mat("w", w.b("white_concrete"))
    S.mat("i", w.b("red_concrete"))
    S.mat("p", w.b("black_concrete"))
    S.mat("b", w.b("gray_wool" if _stil(seed) == 0 else "white_wool"))
    S.mat("k", w.b("bone_block", axis="y"))
    S.mat("c", Verlauf(w, "Keule", ["dark_oak_log", "stripped_dark_oak_log"]), basis=0.5, rausch=1)
    S.plus(ell(0, 3, -1, 5.5, 3.2, 4.2), "f")                                 # Sitzfels
    S.plus(ell(0, 8.6, -1, 3.6, 2.4, 2.8), "h")                               # Becken
    S.plus(lambda X, Y, Z: (np.abs(X) < 3.2) & (Y > 4.5) & (Y < 8.8) & (np.abs(Z - 1.8) < 0.5), "l")
    for sx in (-1, 1):
        glied(S, [(sx * 2.2, 8.6, 0), (sx * 2.8, 8.4, 4.4), (sx * 2.9, 1.2, 4.8)], [2.0, 1.6, 1.2], "h")
        S.plus(ell(sx * 2.9, 0.8, 5.8, 1.3, 0.8, 2.0), "h")
    S.plus(kap((0, 9, -1), (0, 16, 0), 3.6, 4.3, zf=0.82), "h")
    S.plus(ell(0, 15.5, 0.2, 5.4, 2, 2.9), "h")
    S.plus(ell(0, 18.8, 1.2, 2.8, 2.9, 2.8), "h")
    S.plus(ell(0, 19.2, 3.5, 1.5, 1.4, 0.9), "w")                             # Auge
    S.plus(ell(0, 19.2, 4.1, 0.8, 0.8, 0.5), "i")
    S.plus(ell(0, 19.2, 4.45, 0.4, 0.4, 0.3), "p")
    S.plus(kap((-1.9, 20.8, 3.4), (1.9, 20.8, 3.4), 0.5), "h")
    S.plus(kap((0, 21.4, 1.4), (0, 24, 0.6), 0.8, 0.12), "k")                # Horn
    S.plus(lambda X, Y, Z: (((X / 2.6) ** 2 + ((Y - 15.8) / 2.4) ** 2 + ((Z - 3.0) / 1.4) ** 2) <= 1) & (Y < 17.4), "b")
    for sx in (-1, 1):
        glied(S, [(sx * 4.8, 15.5, 0), (sx * 6.2, 11.5, 2.2), (sx * 4.2, 9.5, 4.2)], [1.6, 1.4, 1.2], "h")
        S.plus(ell(sx * 4, 9.6, 4.4, 1.3, 1.2, 1.3), "h")
    S.plus(kap((6.5, 0.5, 2.5), (5.8, 11, -2.4), 1.6, 0.7), "c")
    _rendern(S, (-9, -1, -6), (9, 25, 8), w)
    return w


# ============================================================================ Seeschlange

def seeschlange(seed, g=2):
    """Seeschlange, die sich in drei Windungen aus dem Meer hebt: Schuppen mit Farbverlauf, Rückenflosse,
    gehörnter Kopf mit offenem Maul. Wasserlinie bei y = 0."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        schuppe = Verlauf(w, "Schuppen", ["dark_prismarine", "prismarine", "prismarine_bricks", "light_blue_terracotta"])
        flosse = "yellow_terracotta"
    else:
        schuppe = Verlauf(w, "Schuppen", ["purple_terracotta", "magenta_terracotta", "pink_terracotta", "white_terracotta"])
        flosse = "orange_terracotta"
    S = Skulptur(w, u)
    S.mat("s", schuppe, basis=0.3, steigung=0.25, rausch=0.8)
    S.mat("f", w.b(flosse))
    S.mat("z", w.b("bone_block", axis="y"))
    S.mat("e", w.b("yellow_concrete"))
    S.mat("m", w.b("nether_wart_block"))
    x = -18
    pts = []
    for i, (lang, h) in enumerate(((9, 6), (10, 8), (8, 6))):
        for t in np.linspace(0, 1, 18):
            pts.append((x + lang * t, -2.5 + h * math.sin(math.pi * t), 1.5 * math.sin(x * 0.2 + t * 2)))
        x += lang + 1.5
    for k, p in enumerate(pts):
        r = 1.7 + 0.3 * math.sin(k * 0.2)
        S.plus(ell(*p, r, r, r), "s")
        if p[1] > 0.5 and k % 2 == 0:
            S.plus(kap(p, (p[0] - 0.4, p[1] + r + 1.0, p[2]), 0.35, 0.1), "f")
    kopf = [(x, -2, 0), (x + 2, 4, 0.5), (x + 3.5, 9, 1), (x + 4.5, 12, 1)]
    glied(S, kopf, [1.9, 1.8, 1.6, 1.5], "s")
    hx, hy, hz = x + 5.8, 12.6, 1
    S.plus(ell(hx, hy + 0.4, hz, 2.2, 1.2, 1.4), "s")
    S.plus(ell(hx + 1, hy - 0.9, hz, 1.9, 0.5, 1.1), "s")
    S.plus(ell(hx + 1.2, hy - 0.2, hz, 1.6, 0.4, 0.9), "m")
    S.plus(spiegel_x(kap((0, 0, 0), (0, 0, 0), 0.1)), "s") if False else None
    for s_ in (-1, 1):
        S.plus(ell(hx + 0.4, hy + 1.0, hz + s_ * 1.0, 0.35, 0.3, 0.25), "e")
        S.plus(kap((hx - 0.8, hy + 1.2, hz + s_ * 0.8), (hx - 3, hy + 3.4, hz + s_ * 1.4), 0.4, 0.1), "z")
    for k in range(4):
        S.plus(kap((hx + 0.6 + k * 0.6, hy - 0.4, hz + 0.9), (hx + 0.6 + k * 0.6, hy - 1.0, hz + 0.9), 0.2), "z")
    _rendern(S, (-21, -4, -6), (x + 9, 16, 6), w, boden_weg=False)
    w.bloecke = {p: b for p, b in w.bloecke.items() if p[1] >= -3}
    return w


KREATUREN = {
    "riesenork": ("Riesenork", riesenork),
    "steintroll": ("Versteinerter Troll", steintroll),
    "golem": ("Felsgolem", golem),
    "baumriese": ("Baumriese", baumriese),
    "krakenarme": ("Krakenarme", krakenarme),
    "riesenwurm": ("Riesenwurm", riesenwurm),
    "zyklop": ("Zyklop", zyklop),
    "seeschlange": ("Seeschlange", seeschlange),
}

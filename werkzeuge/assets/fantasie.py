"""Prächtige Statuen und Magie-Bauwerke. Größen 0 klein · 1 mittel · 2 riesig · 3 gigantisch.
Zwei Stile je Vorlage (Variante 1 / 2)."""

from __future__ import annotations

import math

import numpy as np

from lib import Rauschen, Verlauf, Welt, ueberwuchern
from skulptur import kap as _kap
from skulptur import (SOCKEL, Skulptur, dreh_x, dreh_y, dreh_z, ell, kap, kasten, kegel, kreisrand, laterne, ohne, pfosten,
                      platte, scheibe, sockel, spiegel_x, torus, treppe, und, verbinde, zur_mitte)

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


# ============================================================================ Ritter

def ritterstatue(seed, g=1):
    """Ritter in Rüstung, die Hände auf dem Knauf des Schwertes, mit wehendem Umhang und Helmbusch."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        haut = Verlauf(w, "Marmor", ["andesite", "stone", "smooth_stone", "polished_diorite", "calcite", "smooth_quartz"])
        umhang = Verlauf(w, "Umhang", ["nether_wart_block", "red_concrete", "red_wool"])
        m, busch = SOCKEL["schiefer"], "red_wool"
    else:
        haut = Verlauf(w, "Bronze", ["waxed_oxidized_copper", "waxed_oxidized_cut_copper", "waxed_weathered_cut_copper",
                                     "waxed_weathered_copper", "waxed_exposed_copper"])
        umhang = Verlauf(w, "Umhang", ["blue_terracotta", "blue_concrete", "blue_wool"])
        m, busch = SOCKEL["stein"], "gold_block"
    stufen = [2, 2, 3, 4][g]
    sx = sz = _r(4.4 * u, 2)
    top = sockel(w, m, sx + 2 + stufen + 1, sz + 2 + stufen + 1, stufen, sx, sz, _r(3.2 * u, 2))

    S = Skulptur(w, u)
    S.mat("k", haut, basis=0.4, steigung=4.2 / 21, rausch=0.7)
    S.mat("u", umhang, basis=0.2, steigung=1.8 / 15, rausch=0.5)
    S.mat("a", w.b("gold_block"))
    S.mat("d", w.b("polished_blackstone"))
    S.mat("f", w.b(busch))
    S.mat("klinge", Verlauf(w, "Klinge", ["polished_andesite", "smooth_stone", "iron_block"]), basis=0.5,
          steigung=1.5 / 9, rausch=0.3)
    dick = S.dicke(0.5)

    def mantel(X, Y, Z):
        t = (15 - Y) / 13.5
        zc = -2.3 - 1.7 * t + 0.4 * np.sin(X * 1.3 + Y * 0.5)
        return (Y >= 1.2) & (Y <= 15.2) & (np.abs(X) <= 3.3 + 1.7 * t) & (np.abs(Z - zc) <= dick)
    S.plus(mantel, "u")
    S.plus(spiegel_x(kasten(0.4, 0, -1.2, 2.6, 1.3, 2.4)), "k")                    # Eisenschuhe
    S.plus(spiegel_x(kap((1.5, 1, 0), (1.3, 8, 0), 1.2, 1.5)), "k")                 # Beinschienen
    S.plus(spiegel_x(ell(1.4, 4.6, 0.8, 0.95, 0.85, 0.8)), "k")                     # Kniekacheln
    S.plus(kegel(0, 0, 6.5, 10.5, 3.3, 2.7, zf=0.75), "k")                          # Kettenrock
    S.plus(kap((0, 10.5, 0), (0, 15, 0), 2.6, 3.4, zf=0.7), "k")                    # Brustpanzer
    S.plus(kegel(0, 0, 10.0, 10.9, 2.9, 2.9, zf=0.76), "a")                          # Gürtel
    S.plus(ell(0, 13.3, 2.2, 1.0, 1.2, 0.6), "a")                                   # Brustwappen
    S.plus(spiegel_x(ell(3.5, 15, 0, 1.8, 1.4, 1.8)), "k")                          # Schulterstücke
    S.plus(spiegel_x(und(ell(3.6, 14.2, 0, 1.95, 0.4, 1.95), ell(3.6, 14.2, 0, 3, 3, 3))), "a")
    S.plus(spiegel_x(kap((3.6, 14.3, 0), (3.0, 11, 1.2), 1.0)), "k")                # Oberarme
    S.plus(spiegel_x(kap((3.0, 11, 1.2), (0.9, 9.8, 2.9), 0.95, 0.85)), "k")        # Unterarme
    S.plus(spiegel_x(ell(0.7, 9.8, 3.0, 0.9, 0.9, 0.9)), "k")                       # Panzerhandschuhe
    S.plus(kasten(-0.5, 0, 2.6, 0.5, 8.6, 3.4), "klinge")                           # Klinge
    S.plus(kasten(-2.8, 8.6, 2.5, 2.8, 9.3, 3.5), "a")                              # Parierstange
    S.plus(ell(0, 11.0, 3.0, 0.75, 0.75, 0.75), "a")                                # Knauf
    S.plus(kap((0, 15, 0), (0, 16.5, 0), 1.1), "k")                                 # Hals
    helm = ell(0, 18, 0, 2.0, 2.4, 2.1)
    S.plus(helm, "k")
    S.plus(und(helm, kasten(-1.5, 17.8, 1.0, 1.5, 18.5, 3)), "d")                   # Sehschlitz
    S.plus(und(ell(0, 18.3, 0, 0.5, 2.8, 2.35), lambda X, Y, Z: Y > 18.2), "a")    # Helmkamm
    S.plus(kap((0, 20.4, 0.8), (0, 21.4, -1.5), 0.75, 0.55), "f")                   # Helmbusch
    S.plus(kap((0, 21.4, -1.5), (0, 19.3, -3.3), 0.55, 0.4), "f")
    S.rendern((-8, 0, -7), (8, 23, 6), versatz=(0.5, top, 0.5))
    return w


# ============================================================================ Wächterin am Brunnen

def waechterstatue(seed, g=1):
    """Geflügelte Wächterin hält eine leuchtende Kugel über einem Brunnenbecken; Heiligenschein aus Gold."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        haut = Verlauf(w, "Marmor", ["polished_diorite", "calcite", "smooth_quartz", "white_concrete"])
        federn = ["white_concrete", "smooth_quartz", "calcite", "polished_diorite", "diorite"]
        kern, huelle, m = "sea_lantern", "light_blue_stained_glass", SOCKEL["quarz"]
    else:
        haut = Verlauf(w, "Schatten", ["polished_blackstone", "deepslate_tiles", "polished_deepslate", "tuff"])
        federn = ["amethyst_block", "purple_terracotta", "polished_deepslate", "deepslate_tiles", "polished_blackstone"]
        kern, huelle, m = "pearlescent_froglight", "purple_stained_glass", SOCKEL["schwarz"]
    feder_ids = [w.b(n) for n in federn]

    # --- Brunnen
    Rb, rc, hs = _r(9 * u, 5), _r(2.6 * u, 2), _r(4 * u, 3)
    voll, saeule = w.b(m["voll"]), w.b(m["saeule"])
    for x, z in scheibe(Rb + 1):
        w.setze(x, 0, z, voll)
    for x, z in kreisrand(Rb + 1):
        w.setze(x, 0, z, treppe(w, m["treppe"], zur_mitte(x, z)))
    rand = set(kreisrand(Rb))
    for x, z in scheibe(Rb):
        if (x, z) in rand:
            w.setze(x, 1, z, voll)
            w.setze(x, 2, z, platte(w, m["treppe"]))
        elif math.hypot(x, z) > rc + 1.5:
            w.setze(x, 1, z, w.b("water", level=0))
            if w.rng.random() < 0.05:
                w.setze(x, 2, z, w.b("lily_pad"))
    for x, z in kreisrand(rc + 1):
        w.setze(x, 1, z, w.b(f"{m['treppe']}_stairs", facing=zur_mitte(x, z), half="bottom", shape="straight",
                             waterlogged=True))
    for x, z in scheibe(rc):
        for y in range(1, hs + 1):
            w.setze(x, y, z, saeule)
    for i, (x, z) in enumerate(kreisrand(rc)):
        if i % 2 == 0:
            w.setze(x, hs // 2 + 1, z, w.b(m["akzent"]))
    for x, z in kreisrand(rc + 1):
        w.setze(x, hs + 1, z, treppe(w, m["treppe"], zur_mitte(x, z), "top"))
    for x, z in scheibe(rc):
        w.setze(x, hs + 1, z, voll)
    top = hs + 2

    # --- Figur
    S = Skulptur(w, u)
    S.mat("k", haut, basis=0.2, steigung=2.8 / 20, rausch=0.6)
    S.mat("a", w.b("gold_block"))
    S.mat("o", w.b(kern))
    S.mat("g", w.b(huelle))
    dick = S.dicke(0.45)

    def wt(xw):
        t = np.clip((xw - 1.5) / 11.5, 0, 1)
        yt = 16 + 6.5 * np.sin(t * math.pi * 0.75)
        yb = 10 - 3 * np.sin(t * math.pi) + 8 * t * t - 1.8 * np.abs(np.sin(t * math.pi * 5))
        return t, yt, yb

    def fluegel(X, Y, Z):
        xw = np.abs(X)
        t, yt, yb = wt(xw)
        return (xw >= 1.5) & (xw <= 13) & (Y <= yt) & (Y >= yb) & (np.abs(Z - (-1.7 - 1.5 * t)) <= dick)

    def feder(x, y, z, lx, ly, lz):
        xw = abs(lx)
        t, yt, yb = wt(xw)
        band = int((yt - ly) / max(0.5, yt - yb) * 4.5 + 0.3 * math.sin(xw * 2.2))
        return feder_ids[min(max(band, 0), len(feder_ids) - 1)]
    S.mat("fl", feder)

    def gewand(X, Y, Z):
        a = np.arctan2(Z, X)
        r = (3.6 - 1.6 * Y / 12) * (1 + 0.09 * np.sin(7 * a))
        return (Y >= 0) & (Y <= 12) & (X * X + (Z / 0.85) ** 2 <= r * r)
    S.plus(fluegel, "fl")
    S.plus(gewand, "k")
    S.plus(kap((0, 11.5, 0), (0, 15.5, 0), 2.0, 2.3, zf=0.7), "k")
    S.plus(kegel(0, 0, 11.6, 12.3, 2.15, 2.15, zf=0.72), "a")
    S.plus(spiegel_x(kap((2.1, 15.2, 0), (1.9, 19, 0.6), 0.85)), "k")
    S.plus(spiegel_x(kap((1.9, 19, 0.6), (0.9, 22.2, 0.6), 0.8, 0.7)), "k")
    S.plus(kap((0, 15.3, 0), (0, 16.4, 0), 0.9), "k")
    S.plus(ell(0, 17.6, 0, 1.4, 1.7, 1.5), "k")
    S.plus(und(ell(0, 17.9, -0.25, 1.65, 1.9, 1.65), lambda X, Y, Z: (Z < 0.2) | (Y > 18.7)), "k")
    S.plus(torus(0, 18.3, -1.9, 2.1, S.dicke(0.3), achse="z"), "a")                 # Heiligenschein
    S.plus(ell(0, 23.9, 0.6, 1.6, 1.6, 1.6), "g")
    S.plus(ell(0, 23.9, 0.6, 0.95, 0.95, 0.95), "o")
    S.plus(torus(0, 23.9, 0.6, 1.75, S.dicke(0.25), achse="y"), "a")
    S.rendern((-14, 0, -7), (14, 26, 4), versatz=(0.5, top, 0.5))
    return w


# ============================================================================ Löwe

def loewenstatue(seed, g=1):
    """Liegender Wächterlöwe mit gelockter Mähne auf einem langen Sockel – am besten als Paar."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        koerper = Verlauf(w, "Sandstein", ["sandstone", "cut_sandstone", "smooth_sandstone", "end_stone"])
        maehne = Verlauf(w, "Mähne", ["cut_red_sandstone", "smooth_red_sandstone", "orange_terracotta", "raw_gold_block"])
        auge, nase, m = "polished_blackstone", "brown_terracotta", SOCKEL["sandstein"]
    else:
        koerper = Verlauf(w, "Obsidian", ["polished_blackstone", "blackstone", "polished_deepslate", "deepslate_tiles"])
        maehne = Verlauf(w, "Goldmähne", ["gilded_blackstone", "raw_gold_block", "gold_block"])
        auge, nase, m = "shroomlight", "blackstone", SOCKEL["quarz"]
    stufen = [1, 2, 2, 3][g]
    sx, sz = _r(8.6 * u, 4), _r(4.4 * u, 2)
    top = sockel(w, m, sx + 1 + stufen, sz + 1 + stufen, stufen, sx, sz, _r(2.4 * u, 2), lichter=False)

    S = Skulptur(w, u)
    S.mat("k", koerper, basis=0.4, steigung=2.4 / 8, rausch=0.6)
    S.mat("m", maehne, basis=0.3, steigung=2.2 / 9, rausch=0.9)
    S.mat("d", w.b(auge))
    S.mat("n", w.b(nase))
    S.plus(kap((-5, 3, 0), (2, 3.4, 0), 2.6, 3.0, zf=0.85), "k")
    for s in (-1, 1):
        S.plus(ell(-4.3, 3, 1.6 * s, 2.4, 2.6, 1.6), "k")                        # Hinterläufe
        S.plus(ell(-3.0, 1.0, 2.6 * s, 2.6, 1.0, 1.0), "k")
        S.plus(kap((2.5, 2.5, 1.6 * s), (6.5, 0.8, 1.6 * s), 1.0, 0.9), "k")     # Vorderläufe
        S.plus(ell(7.0, 0.7, 1.6 * s, 1.3, 0.8, 1.05), "k")
        S.plus(ell(4.4, 7.3, 1.15 * s, 0.55, 0.65, 0.45), "m")                   # Ohren

    def maehne_form(X, Y, Z):
        d = ((X - 3.2) / 2.7) ** 2 + ((Y - 5.2) / 3.5) ** 2 + (Z / 3.4) ** 2
        welle = 0.18 * np.sin(np.arctan2(Y - 5.2, Z) * 9) * np.cos((X - 3.2) * 2)
        return d <= 1 + welle
    S.plus(maehne_form, "m")
    S.plus(ell(4.9, 5.2, 0, 1.45, 1.65, 1.65), "k")                              # Gesicht
    S.plus(ell(6.0, 4.6, 0, 0.95, 0.85, 1.05), "k")                              # Schnauze
    S.plus(ell(6.7, 5.0, 0, 0.4, 0.35, 0.5), "n")                                # Nase
    S.plus(kasten(5.7, 5.55, -0.95, 6.3, 6.0, -0.4), "d")                        # Augen
    S.plus(kasten(5.7, 5.55, 0.4, 6.3, 6.0, 0.95), "d")
    S.plus(kap((-7, 1.4, 0), (-8.6, 0.8, 2.2), 0.55), "k")                      # Schwanz
    S.plus(ell(-8.7, 0.9, 2.6, 0.85, 0.75, 0.85), "m")
    S.rendern((-10, 0, -5), (9, 9, 5), versatz=(0.5 + 0.5 * u, top, 0.5))
    return w


# ============================================================================ Riesenkopf

def riesenkopf(seed, g=2):
    """Gekrönter Kopf eines gestürzten Königs, schräg im Boden versunken, mit glimmenden Augen."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        stein = Verlauf(w, "Stein", ["mossy_cobblestone", "mossy_stone_bricks", "andesite", "stone", "smooth_stone",
                                     "polished_andesite"])
        krone = Verlauf(w, "Krone", ["gilded_blackstone", "raw_gold_block", "gold_block"])
        auge = "shroomlight"
    else:
        stein = Verlauf(w, "Sandstein", ["cut_red_sandstone", "sandstone", "cut_sandstone", "smooth_sandstone",
                                         "end_stone"])
        krone = Verlauf(w, "Krone", ["lapis_block", "raw_gold_block", "gold_block"])
        auge = "sea_lantern"
    S = Skulptur(w, u)
    S.mat("k", stein, basis=0.2, steigung=4.5 / 20, rausch=0.9)
    S.mat("c", krone, basis=0.6, steigung=0.08, rausch=1.2)
    S.mat("e", w.b(auge))
    S.plus(ell(0, 8, 0, 6.5, 9, 7), "k")                                         # Schädel
    S.plus(kap((-4.2, 10.8, 5.0), (4.2, 10.8, 5.0), 1.6), "k")                       # Brauen
    S.plus(kap((0, 10.4, 6.0), (0, 5.4, 8.6), 1.2, 2.0), "k")                    # Nase
    S.plus(spiegel_x(ell(3.6, 6.5, 4.5, 2.2, 2.2, 2.1)), "k")                    # Wangen
    S.plus(ell(0, 3.8, 6.2, 2.8, 1.0, 1.5), "k")                               # Lippen
    S.plus(ell(0, 2.4, 6.0, 2.5, 0.9, 1.4), "k")
    S.plus(ell(0, 0.8, 4.8, 2.7, 2.1, 2.3), "k")                                 # Kinn
    S.plus(spiegel_x(ell(6.6, 8, 0.5, 0.95, 2.6, 1.6)), "k")                     # Ohren
    S.minus(kasten(-2.6, 2.95, 5.4, 2.6, 3.35, 9))                                # Mundlinie
    S.minus(spiegel_x(ell(2.5, 8.7, 6.3, 1.8, 1.3, 2.2)))                      # Augenhöhlen
    S.plus(spiegel_x(ell(2.5, 8.6, 4.4, 1.05, 0.8, 0.7)), "e")
    S.plus(ohne(kegel(0, 0, 14.4, 16.4, 6.4, 6.6, zf=1.08), kegel(0, 0, 14, 17, 5.2, 5.4, zf=1.08)), "c")
    for i in range(9):
        a = i * 2 * math.pi / 9
        x, z = math.cos(a) * 6.0, math.sin(a) * 6.4
        S.plus(kap((x, 16, z), (x * 0.97, 19.8, z * 0.97), 0.95, 0.35), "c")
        S.plus(ell(x * 1.05, 15.4, z * 1.05, 0.55, 0.55, 0.55), "e" if i % 3 == 0 else "c")
    dreh = dreh_y(0.65) @ dreh_z(0.15) @ dreh_x(-0.3)
    S.rendern((-8, -2, -8), (8, 21, 10), versatz=(0.5, -1.2 * u, 0.5), dreh=dreh)
    w.bloecke = {p: b for p, b in w.bloecke.items() if p[1] >= 0}
    # Trümmer der Krone und Felsbrocken ringsum
    T = Skulptur(w, u)
    T.mat("k", stein, basis=0.8, rausch=1.5)
    T.mat("c", krone, basis=1.0, rausch=1.2)
    for i in range(5):
        a = w.rng.random() * 2 * math.pi
        d = 10 + w.rng.random() * 3
        x, z = math.cos(a) * d, math.sin(a) * d
        r = 0.9 + w.rng.random() * 1.1
        T.plus(ell(x, 0.2, z, r * 1.2, r, r), "k")
    T.plus(kap((9.5, 0.6, -6), (12.5, 1.6, -4.5), 0.9, 0.35), "c")
    T.rendern((-15, -1, -15), (15, 4, 15), versatz=(0.5, 0, 0.5))
    w.bloecke = {p: b for p, b in w.bloecke.items() if p[1] >= 0}
    ueberwuchern(w, None, ranken=0.35, pflanzen=0.5, buesche=0.08, max_ranke=_r(5 * u, 2))
    return w


# ============================================================================ Obelisk

def obelisk(seed, g=1):
    """Obelisk mit Goldbändern, leuchtenden Glyphen und goldener Spitze; Feuerschalen an den Ecken."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        schaft = Verlauf(w, "Obsidian", ["polished_blackstone_bricks", "polished_blackstone", "deepslate_tiles",
                                         "polished_deepslate"])
        glyphe, m = "crying_obsidian", SOCKEL["schwarz"]
    else:
        schaft = Verlauf(w, "Wüste", ["cut_sandstone", "sandstone", "smooth_sandstone", "end_stone"])
        glyphe, m = "lapis_block", SOCKEL["sandstein"]
    hb = _r(1.6 * u, 1)
    stufen = [2, 3, 3, 4][g]
    R = hb + 3 + stufen
    top = sockel(w, m, R, R, stufen, hb + 1, hb + 1, _r(2 * u, 2), lichter=False)
    H = _r(20 * u, 10)
    for y in range(H):
        t = y / H
        h = max(0, int(round(hb * (1 - 0.4 * t))))
        band = y % _r(5 * u, 3) == 0 and y > 0
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                if band:
                    blk = w.b("gold_block")
                elif (abs(x) == h or abs(z) == h) and (x == 0 or z == 0) and y % 2 == 1 and h >= 1:
                    blk = w.b(glyphe)
                else:
                    blk = schaft(3 * t + w.rng.random() * 0.5, x, top + y, z)
                w.setze(x, top + y, z, blk)
    h = max(0, int(round(hb * 0.6)))
    for k in range(h + 2):
        hh = max(h - k, 0)
        for x in range(-hh, hh + 1):
            for z in range(-hh, hh + 1):
                w.setze(x, top + H + k, z, w.b("gold_block"))
    c = R - stufen + 1
    for a in (-1, 1):
        for b in (-1, 1):
            pfosten(w, a * c, stufen, stufen + _r(u, 1), b * c, m["pfosten"])
            w.setze(a * c, stufen + _r(u, 1) + 1, b * c,
                    w.b("soul_campfire" if m["seele"] else "campfire", lit=True, signal_fire=False, facing="north",
                        waterlogged=False))
    return w


# ============================================================================ Portal

def portal(seed, g=1):
    """Runenring mit wirbelndem Kern, Kristallzacken, Schlusssteinen und Feuerschalen auf einer Treppe."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        stein = Verlauf(w, "End", ["obsidian", "crying_obsidian", "purpur_block", "purpur_pillar", "end_stone_bricks"])
        wirbel = ["purple_stained_glass", "magenta_stained_glass", "pink_stained_glass", "purple_stained_glass",
                  "blue_stained_glass"]
        rune, zacke, m = "pearlescent_froglight", "amethyst_block", SOCKEL["purpur"]
    else:
        stein = Verlauf(w, "Wald", ["mossy_cobblestone", "mossy_stone_bricks", "stone_bricks", "polished_andesite"])
        wirbel = ["lime_stained_glass", "green_stained_glass", "cyan_stained_glass", "light_blue_stained_glass",
                  "lime_stained_glass"]
        rune, zacke, m = "verdant_froglight", "prismarine_bricks", SOCKEL["stein"]
    R = 6.5 * u + 1
    th = max(1.2, 1.5 * u)
    tiefe = max(1, int(0.9 * u))
    breite = _r(R + th + 2)
    stufen = [1, 2, 2, 3][g]
    voll = w.b(m["voll"])
    for k in range(stufen):
        hx, hz = breite + stufen - k, tiefe + 2 + stufen - k
        for x in range(-hx, hx + 1):
            for z in range(-hz, hz + 1):
                ax, az = abs(x) == hx, abs(z) == hz
                if ax and az:
                    blk = w.b(m["ecke"])
                elif ax:
                    blk = treppe(w, m["treppe"], "east" if x < 0 else "west")
                elif az:
                    blk = treppe(w, m["treppe"], "south" if z < 0 else "north")
                else:
                    blk = voll
                w.setze(x, k, z, blk)
    cy = stufen + R + th * 0.4
    n = int(R + th) + 2
    rid = [w.b(b) for b in wirbel]
    for x in range(-n, n + 1):
        for y in range(stufen, int(cy + n) + 1):
            d = math.hypot(x, y - cy)
            a = math.atan2(y - cy, x)
            if abs(d - R) <= th:
                q = (a + math.pi) * 8 / (2 * math.pi)
                schluss = abs(q - round(q)) < 0.14 and abs(d - R) < 0.75
                for z in range(-tiefe, tiefe + 1):
                    w.setze(x, y, z, w.b(rune) if schluss and z == 0 else
                            stein(1.5 + 1.6 * math.sin(a * 4) + (d - R) / th + w.rng.random() * 0.6, x, y, z))
            elif d < R - th:
                band = int(((a + d * 0.42) % (2 * math.pi)) / (2 * math.pi) * 10) % len(rid)
                w.setze(x, y, 0, rid[band])
    for i in range(12):
        a = i * 2 * math.pi / 12 + math.pi / 12
        if math.sin(a) < -0.6:
            continue
        lang = (2.5 + (i % 2) * 2) * u
        for k in np.arange(0, lang, 0.5):
            r = R + th + k
            dicke = max(0, int((1 - k / lang) * u))
            x, y = round(math.cos(a) * r), round(cy + math.sin(a) * r)
            for dz in range(-dicke, dicke + 1):
                w.setze(x, y, dz, w.b(zacke))
    for sx_ in (-1, 1):
        x = sx_ * (breite - 1)
        pfosten(w, x, stufen, stufen + _r(2 * u, 1), tiefe + 1, m["pfosten"])
        w.setze(x, stufen + _r(2 * u, 1) + 1, tiefe + 1, w.b("soul_campfire", lit=True, signal_fire=False,
                                                             facing="north", waterlogged=False))
    for i in range(2 + 2 * g):
        x = (w.rng.random() - 0.5) * 2 * (R + 4)
        y = cy + (w.rng.random() - 0.3) * R
        z = (1 if w.rng.random() < 0.5 else -1) * (tiefe + 2 + w.rng.random() * 2 * u)
        if math.hypot(x, y - cy) < R + th + 1:
            continue
        S = Skulptur(w, u)
        S.mat("k", stein, basis=2, rausch=1)
        S.plus(ell(0, 0, 0, 0.9, 0.7, 0.9), "k")
        S.rendern((-1, -1, -1), (1, 1, 1), versatz=(x, y, z))
    return w


# ============================================================================ Magierturm

def magierturm(seed, g=1):
    """Leicht verdrehter Magierturm mit Strebepfeilern, Balkon, Nebentürmchen, Hexenhutdach,
    schwebendem Kristall und einem Ring kreisender Runensteine."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        wand = Verlauf(w, "Turm", ["cobbled_deepslate", "deepslate_bricks", "stone_bricks", "polished_andesite"])
        dach = Verlauf(w, "Dach", ["purple_terracotta", "purple_concrete", "purpur_block", "magenta_terracotta"])
        glas, kristall, holz, wt_ = "purple_stained_glass", "amethyst_block", "dark_oak", "deepslate_brick"
    else:
        wand = Verlauf(w, "Turm", ["mossy_stone_bricks", "stone_bricks", "calcite", "smooth_quartz"])
        dach = Verlauf(w, "Dach", ["dark_prismarine", "waxed_oxidized_cut_copper", "prismarine_bricks",
                                   "light_blue_terracotta"])
        glas, kristall, holz, wt_ = "light_blue_stained_glass", "prismarine_bricks", "spruce", "stone_brick"
    R = max(2.5, 3.2 * u)
    H = _r(22 * u, 12)
    seele = _stil(seed) == 0

    def ox(y):
        return math.sin(y / H * 2.2) * 1.4 * u

    for i in range(4):                                                        # Strebepfeiler
        a = i * math.pi / 2 + math.pi / 4
        for k in range(_r(4 * u, 2)):
            for y in range(int(H * 0.32 * (1 - k / (4 * u)))):
                x, z = round(ox(y) + math.cos(a) * (R + k)), round(math.sin(a) * (R + k))
                w.setze(x, y, z, wand(0.6 + 2 * y / H, x, y, z))
    fenster_h = _r(5 * u, 4)
    for y in range(H):                                                        # Schaft
        o = ox(y)
        r = R + (1 if y < _r(2 * u) else 0)
        n = int(r) + 2
        for x in range(int(o) - n, int(o) + n + 1):
            for z in range(-n, n + 1):
                d = math.hypot(x - o, z)
                if d > r + 0.5:
                    continue
                if d > r - 0.6:
                    a = math.atan2(z, x - o)
                    fenster = (2 <= y % fenster_h < 2 + _r(1.6 * u, 1) and y > fenster_h
                               and abs(math.sin(2 * a)) < 0.2)
                    band = y % _r(7 * u, 4) == 0
                    w.setze(x, y, z, w.b(glas) if fenster else w.b("polished_deepslate") if band
                            else wand(0.4 + 3 * y / H + w.rng.random() * 0.7, x, y, z))
                elif y == 0:
                    w.setze(x, y, z, w.b("polished_deepslate"))
    o0, zt = round(ox(0)), int(R + 0.5)                                       # Tür mit Laternen
    for x in range(o0 - 1, o0 + 2):
        for y in (1, 2):
            w.setze(x, y, zt, 0)
            w.setze(x, y, zt - 1, 0)
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(o0, y, zt, w.b(f"{holz}_door", facing="north", half=half, hinge="left", open=False, powered=False))
    for dx in (-2, 2):
        laterne(w, o0 + dx, 1, zt + 1, seele)
    yb = int(H * 0.62)                                                        # Balkon
    o = round(ox(yb))
    for x, z in kreisrand(R + 1.6):
        w.setze(x + o, yb - 1, z, treppe(w, wt_, zur_mitte(x, z), "top"))
    for x, z in scheibe(R + 2):
        if math.hypot(x, z) > R - 0.5:
            w.setze(x + o, yb, z, w.b(f"{holz}_planks"))
    verbinde(w, [(x + o, yb + 1, z) for x, z in kreisrand(R + 2)], f"{holz}_fence")
    a = math.radians(140)                                                     # Nebentürmchen
    rt = max(1.2, 1.6 * u)
    tx, tz = ox(H * 0.6) + math.cos(a) * (R + rt * 0.6), math.sin(a) * (R + rt * 0.6)
    y0, y1 = int(H * 0.38), int(H * 0.86)
    for y in range(y0 - _r(3 * u, 2), y1):
        r = rt if y >= y0 else rt * (1 - (y0 - y) / (3 * u + 1))
        for x in range(int(tx - r) - 1, int(tx + r) + 2):
            for z in range(int(tz - r) - 1, int(tz + r) + 2):
                d = math.hypot(x - tx, z - tz)
                if d <= r:
                    w.setze(x, y, z, w.b(glas) if (y - y0) % _r(4 * u, 3) == 2 and d > r - 1 and y >= y0
                            else wand(1 + 2 * y / H, x, y, z))
    hd = _r(5 * u, 3)
    for k in range(hd + 1):
        r = (rt + 1) * (1 - k / hd) ** 1.2
        for x in range(int(tx - r) - 1, int(tx + r) + 2):
            for z in range(int(tz - r) - 1, int(tz + r) + 2):
                if math.hypot(x - tx, z - tz) <= r + 0.3:
                    w.setze(x, y1 + k, z, dach(3 * k / hd + w.rng.random() * 0.4, x, y1 + k, z))
    hr = _r(11 * u, 6)                                                        # Hexenhutdach
    for k in range(hr + 1):
        t = k / hr
        r = (R + 2.2) * (1 - t) ** 1.35
        o = ox(H) + t * t * 2.5 * u
        n = int(r) + 2
        for x in range(int(o) - n, int(o) + n + 1):
            for z in range(-n, n + 1):
                d = math.hypot(x - o, z)
                if d <= r + 0.35 and (d > r - 1.3 or k == 0):
                    w.setze(x, H + k, z, dach(3.2 * t + w.rng.random() * 0.5, x, H + k, z))
    spx = round(ox(H) + 2.5 * u)
    w.setze(spx, H + hr + 1, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    S = Skulptur(w, u)                                                        # schwebender Kristall
    S.mat("k", w.b(kristall))
    S.mat("g", w.b(glas))
    kc = H + hr + 3 + 2 * u
    S.plus(lambda X, Y, Z: np.abs(X) + np.abs(Y) * 0.55 + np.abs(Z) <= 1.4, "g")
    S.plus(lambda X, Y, Z: np.abs(X) + np.abs(Y) * 0.55 + np.abs(Z) <= 0.9, "k")
    S.rendern((-2, -3, -2), (2, 3, 2), versatz=(spx + 0.5, kc, 0.5))
    anzahl = 4 + 2 * g                                                        # Runensteine
    for i in range(anzahl):
        a = i * 2 * math.pi / anzahl
        rr = R + 4.5 * u
        x, z = round(ox(H) + math.cos(a) * rr), round(math.sin(a) * rr)
        y = int(H * 0.75 + math.sin(a * 2) * 2 * u)
        T = Skulptur(w, u)
        T.mat("k", wand, basis=1.5, rausch=1.2)
        T.mat("e", w.b(kristall))
        T.plus(ell(0, 0, 0, 1.0, 0.75, 1.0), "k")
        T.plus(kasten(-0.25, 0.4, -0.25, 0.25, 1.1, 0.25), "e")
        T.rendern((-2, -2, -2), (2, 2, 2), versatz=(x + 0.5, y, z + 0.5))
        unten = min(p[1] for p in w.bloecke if p[0] == x and p[2] == z and abs(p[1] - y) < 4 * u + 2)
        w.setze(x, unten - 1, z, w.b("chain", axis="y", waterlogged=False))
        w.setze(x, unten - 2, z, w.b("soul_lantern" if seele else "lantern", hanging=True, waterlogged=False))
    return w


# ============================================================================ Drachenskelett mit Hort

def drachenskelett(seed, g=2):
    """Gewaltiges Drachenskelett mit Rückenstacheln, Flügelknochen, Klauen und gehörntem Schädel
    auf einem Goldhort."""
    w = _welt(seed)
    u = U[g] * 1.5
    S = Skulptur(w, u)
    dk = S.dicke

    def kap(a, b, ra, rb=None):
        return _kap(a, b, dk(ra), dk(ra if rb is None else rb))
    if _stil(seed) == 0:
        knochen = Verlauf(w, "Knochen", ["bone_block", "calcite", "smooth_quartz"])
    else:
        knochen = Verlauf(w, "Schattenknochen", ["polished_blackstone", "blackstone", "bone_block"])
    S.mat("k", knochen, basis=0.4, steigung=0.12, rausch=1.0)
    S.mat("g", Verlauf(w, "Gold", ["raw_gold_block", "gold_block", "honeycomb_block"]), basis=0.8, rausch=1.8)
    S.mat("e", w.b("shroomlight" if _stil(seed) == 0 else "sea_lantern"))
    L = 26.0

    def wirbel(t):
        return (t * L - L / 2, 1.2 + 6 * math.sin(min(1, t * 1.15) * math.pi) ** 0.7, 2.6 * math.sin(t * 4))
    S.plus(lambda X, Y, Z: ((X + 1) / 9) ** 2 + (Y / 2.2) ** 2 + (Z / 6) ** 2 <= 1, "g")          # Hort
    S.plus(lambda X, Y, Z: ((X - 6) / 4) ** 2 + (Y / 1.4) ** 2 + ((Z + 4) / 3) ** 2 <= 1, "g")
    n = 70
    for i in range(n):
        t = i / (n - 1)
        x, y, z = wirbel(t)
        r = max(0.45, 0.75 * (0.45 + math.sin(math.pi * min(1, t * 1.2))))
        S.plus(ell(x, y, z, r, r, r), "k")
        if i % 3 == 0 and t > 0.15:
            S.plus(kap((x, y, z), (x - 0.4, y + 1.2 + 1.4 * math.sin(math.pi * t), z), 0.35, 0.12), "k")
        if i % 4 == 0 and 0.28 < t < 0.68:
            for s in (-1, 1):
                pts = [(x, y, z)] + [(x + 0.3 * k, y - (y - 0.4) * k / 6, z + s * math.sin(k / 6 * math.pi * 0.85) * 4)
                                     for k in range(1, 7)]
                for a, b in zip(pts, pts[1:]):
                    S.plus(kap(a, b, 0.32), "k")
    for tt, vor in ((0.36, 1.6), (0.62, -1.4)):                                                 # Beine
        x, y, z = wirbel(tt)
        for s in (-1, 1):
            knie = (x + vor, 2.6, z + s * 4.2)
            fuss = (x + vor * 1.8, 0.4, z + s * 5.4)
            S.plus(kap((x, y, z), knie, 0.55, 0.45), "k")
            S.plus(kap(knie, fuss, 0.45, 0.35), "k")
            for k in (-0.6, 0, 0.6):
                S.plus(kap(fuss, (fuss[0] + 1.4, 0.2, fuss[2] + k * 1.4), 0.3, 0.12), "k")
    sx_, sy_, sz_ = wirbel(0.42)                                                                # Flügel
    for s in (-1, 1):
        e = (sx_ + 2, sy_ + 7.5, sz_ + s * 6)
        S.plus(kap((sx_, sy_, sz_), e, 0.6, 0.45), "k")
        for f in range(4):
            spitze = (e[0] - 4 - 5 * f, e[1] - 2 - 3.2 * f, e[2] + s * (6 + f))
            mitte = ((e[0] + spitze[0]) / 2, (e[1] + spitze[1]) / 2 + 2, (e[2] + spitze[2]) / 2)
            S.plus(kap(e, mitte, 0.38, 0.3), "k")
            S.plus(kap(mitte, spitze, 0.3, 0.12), "k")
    hx, hy, hz = wirbel(1.0)                                                                    # Schädel
    S.plus(ell(hx + 2.8, hy + 1.3, hz, 3.6, 1.7, 1.9), "k")
    S.plus(ell(hx + 4.2, hy - 0.4, hz, 2.8, 0.55, 1.35), "k")
    S.minus(ell(hx + 4.2, hy + 0.35, hz, 2.6, 0.35, 1.0))
    for s in (-1, 1):
        S.minus(ell(hx + 2.4, hy + 2.0, hz + s * 1.3, 0.75, 0.65, 0.55))
        S.plus(ell(hx + 2.2, hy + 1.9, hz + s * 1.05, 0.3, 0.3, 0.3), "e")
        S.plus(kap((hx + 1.2, hy + 2.4, hz + s * 1.1), (hx - 2.6, hy + 4.4, hz + s * 2.0), 0.5, 0.15), "k")
        for k in range(4):
            S.plus(kap((hx + 3 + k * 0.8, hy + 0.2, hz + s * 1.15), (hx + 3 + k * 0.8, hy - 0.4, hz + s * 1.15),
                       0.18), "k")
    S.rendern((-24, -1, -16), (20, 18, 16), versatz=(0.5, 0, 0.5))
    w.bloecke = {p: b for p, b in w.bloecke.items() if p[1] >= 0}
    ueberwuchern(w, None, ranken=0.12, pflanzen=0.25, buesche=0.02)
    return w


FANTASIE = {
    "ritterstatue": ("Ritterstatue", ritterstatue),
    "waechterstatue": ("Wächterin am Brunnen", waechterstatue),
    "loewenstatue": ("Wächterlöwe", loewenstatue),
    "riesenkopf": ("Versunkener Königskopf", riesenkopf),
    "obelisk": ("Obelisk", obelisk),
    "portal": ("Runenportal", portal),
    "magierturm": ("Magierturm", magierturm),
    "drachenskelett": ("Drachenskelett mit Hort", drachenskelett),
}

from schiffe import SCHIFFE  # noqa: E402,F401  (Schiffe & Steampunk liegen in eigener Datei)

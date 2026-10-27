"""Prächtige Schiffe, Luftschiffe und Steampunk-Bauten. Größen 0 klein · 1 mittel · 2 riesig · 3 gigantisch."""

from __future__ import annotations

import math

import numpy as np

from lib import Verlauf, Welt
from riesenbogen import zahnrad
from skulptur import (Skulptur, ell, und, kap, kasten, kreisrand, laterne, linie, pfosten, platte, scheibe, treppe,
                      verbinde, zur_mitte)

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


# ============================================================================ Rumpf

def rumpf(w, L, B, D, F, u, holz, y0=0, kanonen=True, kastelle=True):
    """Geschwungener Schiffsrumpf entlang x (Bug bei +x). Wasserlinie bei y0. Gibt Hilfsdaten zurück.
    holz: dict mit unten, wand (Verläufe), streifen, leiste, deck (Verlauf), zaun, fenster."""
    half = L / 2
    hk_a = _r(2.6 * u, 2) if kastelle else 0
    hk_v = _r(1.6 * u, 1) if kastelle else 0

    def kiel(x):
        uu = x / half
        return -D + 0.9 * D * np.clip((uu - 0.45) / 0.55, 0, 1) ** 2 + 0.3 * D * np.clip((-uu - 0.8) / 0.2, 0, 1)

    def deck_haupt(x):
        uu = x / half
        return F + 0.12 * F * uu ** 2

    def deck_oben(x):
        uu = x / half
        return deck_haupt(x) + hk_a * (uu < -0.45) + hk_v * (uu > 0.6)

    def halbbreite(x, y):
        uu = np.clip(x / half, -1, 1)
        px = np.where(uu >= 0, np.clip(1 - np.abs(uu) ** 2.2, 0, 1) ** 0.6, np.clip(1 - np.abs(uu) ** 6, 0, 1) ** 0.5)
        v = (y - kiel(x)) / (deck_haupt(x) - kiel(x))
        py = np.where(v < 0.8, np.clip(v, 0, 1) ** 0.45, 0.8 ** 0.45 - 0.22 * (v - 0.8))
        return B * px * py

    n = int(half) + 2
    ymax = int(F * 1.2 + hk_a) + 2
    X, Y, Z = np.mgrid[-n:n + 1, -int(D) - 2:ymax + 1, -int(B) - 2:int(B) + 3]
    Xf = X.astype(float)
    fest = (Y >= kiel(Xf)) & (Y <= np.round(deck_oben(Xf))) & (np.abs(Z) <= halbbreite(Xf, Y.astype(float)) + 0.3) \
        & (np.abs(Xf) <= half)
    ox, oy, oz = X[0, 0, 0], Y[0, 0, 0], Z[0, 0, 0]
    idx = {tuple(p) for p in np.argwhere(fest)}

    def drin(x, y, z):
        return (x - ox, y - oy, z - oz) in idx

    gp = _r(F * 0.5, 1)
    rail = []
    oben_punkte = []
    for i, j, k in idx:
        x, y, z = int(i + ox), int(j + oy), int(k + oz)
        oben = not drin(x, y + 1, z)
        seite = not (drin(x + 1, y, z) and drin(x - 1, y, z) and drin(x, y, z + 1) and drin(x, y, z - 1))
        unten = not drin(x, y - 1, z)
        dh = int(round(float(deck_haupt(x))))
        if oben:
            if seite:
                heck = not drin(x - 1, y, z)
                blk = w.b("gold_block") if heck and y > dh else w.b(holz["leiste"], axis="x")
                rail.append((x, y + 1 + y0, z))
            else:
                blk = holz["deck"](1 + 0.8 * math.sin(z * 1.7) + w.rng.random() * 0.6, x, y, z)
            oben_punkte.append((x, y, z))
        elif seite or unten:
            heck = not drin(x - 1, y, z)
            if y < 0:
                blk = holz["unten"](1.2 + y / max(1, D) + w.rng.random() * 0.5, x, y, z)
            elif y == 0 or y == gp + 1:
                blk = w.b(holz["leiste"], axis="x")
            elif y == gp and abs(x) < half * 0.5:
                blk = w.b("black_terracotta") if kanonen and x % 3 == 0 and F >= 4 else w.b(holz["streifen"])
            elif heck and y > dh and z % 2 == 0 and y < deck_oben(x) - 0:
                blk = w.b(holz["fenster"])
                w.setze(x + 1, y + y0, z, w.b("shroomlight"))
            elif y > dh and (x % 3 == 0) and not heck and x / half < -0.5 and y < deck_oben(x):
                blk = w.b(holz["fenster"])
            else:
                blk = holz["wand"](1 + 1.5 * y / max(1, F) + w.rng.random() * 0.4, x, y, z)
        elif y == int(round(float(deck_haupt(x)))):
            blk = holz["deck"](1.0, x, y, z)
        else:
            continue
        w.setze(x, y + y0, z, blk, ueberschreiben=False)
    verbinde(w, rail, holz["zaun"])
    return dict(half=half, deck_haupt=deck_haupt, deck_oben=deck_oben, kiel=kiel, oben=oben_punkte, B=B,
                hk_a=hk_a, hk_v=hk_v)


def segel(w, xm, y_oben, y_unten, hz_oben, hz_unten, bauch, farbe, wappen=None):
    """Rahsegel quer zum Schiff (Ebene yz), nach vorn (+x) gebläht."""
    h = max(1, y_oben - y_unten)
    versatz = {}
    for y in range(y_unten, y_oben + 1):
        t = (y_oben - y) / h
        hz = hz_oben + (hz_unten - hz_oben) * t
        for z in range(-int(hz), int(hz) + 1):
            versatz[(y, z)] = int(round(bauch * math.sin(math.pi * (z + hz) / (2 * hz + 1e-9))
                                        * math.sin(math.pi * min(1, t * 0.9 + 0.1))))
    for (y, z), o in versatz.items():
        nb = [versatz.get((y + 1, z), o), versatz.get((y, z - 1), o), versatz.get((y, z + 1), o)]
        for k in range(min(nb + [o]), o + 1):
            if wappen and wappen(y, z):
                blk = w.b(wappen(y, z))
            else:
                blk = farbe(1 + 1.2 * (1 - (y - y_unten) / h) + (0.4 if z % 3 == 0 else 0), xm + 1 + k, y, z)
            w.setze(xm + 1 + k, y, z, blk)


def dreieckssegel(w, a, b, c, z, blk):
    """Dreieck in der Ebene z = const (Längssegel / Klüver)."""
    xs = [a[0], b[0], c[0]]
    ys = [a[1], b[1], c[1]]
    for x in range(int(min(xs)), int(max(xs)) + 1):
        for y in range(int(min(ys)), int(max(ys)) + 1):
            d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            l1 = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / d
            l2 = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / d
            if l1 >= -0.02 and l2 >= -0.02 and 1 - l1 - l2 >= -0.02:
                w.setze(x, y, z, blk)


def flagge(w, x, y, z, laenge, farben):
    for k in range(laenge):
        for d in range(max(1, laenge // 3)):
            w.setze(x - 1 - k, y - d, z, w.b(farben[(k + d) % len(farben)]))


def mast(w, x, y0, hoehe, dick, holz="spruce_log"):
    for y in range(y0, y0 + hoehe):
        w.setze(x, y, 0, w.b(holz, axis="y"))
        if dick:
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if y < y0 + hoehe * 0.7:
                    w.setze(x + dx, y, dz, w.b(holz, axis="y"))


# ============================================================================ Galeone

def segelschiff(seed, g=1):
    """Dreimastige Galeone: Achter- und Vorderkastell, beleuchtete Heckfenster mit Goldrahmen, Kanonenpforten,
    geblähte Rahsegel mit Wappen, Klüver, Besan, Krähennest, Bugspriet mit goldener Galionsfigur, Flaggen
    und Hecklaternen. Wasserlinie bei y = 0."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        holz = dict(unten=Verlauf(w, "Rumpf", ["dark_oak_planks", "dark_oak_planks", "spruce_planks"]),
                    wand=Verlauf(w, "Wand", ["dark_oak_planks", "spruce_planks", "stripped_spruce_log"]),
                    streifen="yellow_terracotta", leiste="stripped_dark_oak_log", zaun="dark_oak_fence",
                    deck=Verlauf(w, "Deck", ["spruce_planks", "oak_planks", "stripped_oak_log"]),
                    fenster="yellow_stained_glass")
        tuch = Verlauf(w, "Segel", ["white_wool", "white_concrete", "white_wool"])
        wf, flaggen = "red_wool", ["red_wool", "yellow_wool"]
    else:
        holz = dict(unten=Verlauf(w, "Rumpf", ["spruce_planks", "spruce_planks", "oak_planks"]),
                    wand=Verlauf(w, "Wand", ["spruce_planks", "oak_planks", "stripped_birch_log"]),
                    streifen="blue_terracotta", leiste="stripped_spruce_log", zaun="spruce_fence",
                    deck=Verlauf(w, "Deck", ["oak_planks", "birch_planks", "stripped_birch_log"]),
                    fenster="light_blue_stained_glass")
        tuch = Verlauf(w, "Segel", ["white_wool", "white_wool", "white_concrete"])
        wf, flaggen = "blue_wool", ["blue_wool", "white_wool"]
    L = 30 * u + 6
    B = 3.6 * u + 1.2
    D = 2.6 * u + 1
    F = 3.4 * u + 1.2
    r = rumpf(w, L, B, D, F, u, holz)
    half, dh, do = r["half"], r["deck_haupt"], r["deck_oben"]
    dick = g >= 2
    masten = [(round(half * 0.42), 0.95), (round(-half * 0.04), 1.15), (round(-half * 0.55), 0.78)]
    Hm = L * 0.78
    for i, (xm, f) in enumerate(masten):
        y0 = int(round(float(do(xm)))) + 1
        h = int(Hm * f)
        mast(w, xm, y0 - 2, h + 2, dick)
        top = y0 + h
        w.setze(xm, top, 0, w.b("lightning_rod" if False else "spruce_fence", north=False, south=False, east=False,
                                west=False, waterlogged=False))
        flagge(w, xm, top + _r(2 * u, 1), 0, _r(3 * u, 2), flaggen)
        for k in range(_r(2 * u, 1)):
            w.setze(xm, top + 1 + k, 0, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                            waterlogged=False))
        if i == 2:                                                              # Besan: Längssegel
            dreieckssegel(w, (xm - 1, y0 + h * 0.85), (xm - 1, y0 + 2), (xm - half * 0.42, y0 + 2),
                          0, w.b("white_wool"))
            continue
        rahen = [y0 + int(h * f_) for f_ in (0.36, 0.63, 0.86)]
        unten = y0 + _r(2.5 * u, 2)
        breiten = [B * 1.7, B * 1.35, B * 1.0]
        for k, yr in enumerate(rahen):
            hz = int(breiten[k])
            for z in range(-hz, hz + 1):
                w.setze(xm + 1, yr, z, w.b("spruce_log", axis="z"))
            for zs in (-hz, hz):
                w.setze(xm + 1, yr - 1, zs, w.b("lantern", hanging=True, waterlogged=False)) if k == 0 else None
            y_unten = unten if k == 0 else rahen[k - 1] + 1
            hz_u = (breiten[k - 1] if k > 0 else breiten[0] * 1.05) - 1
            wappen = None
            if k == 0 and i == 1:
                ym = (yr + y_unten) // 2
                bw = max(0.6, 0.6 * u)

                def wappen(y, z, ym=ym, bw=bw):
                    return wf if abs(z) <= bw or abs(y - ym) <= bw else None
            segel(w, xm + 1, yr - 1, y_unten, breiten[k] - 1, hz_u, max(1, 1.6 * u), tuch, wappen)
        if i == 1:                                                              # Krähennest
            yn = y0 + int(h * 0.72)
            rn = max(1, 1.4 * u)
            for x, z in scheibe(rn):
                if (x, z) != (0, 0):
                    w.setze(xm + x, yn, z, w.b("spruce_planks"))
            verbinde(w, [(xm + x, yn + 1, z) for x, z in kreisrand(rn)], holz["zaun"])
        if g >= 2:                                                              # Wanten
            for s in (-1, 1):
                for dx in (-2, 0, 2):
                    linie(w, (xm + dx, int(dh(xm)) + 1, s * int(B)), (xm, rahen[1] - 1, s), w.b(holz["zaun"],
                          north=False, south=False, east=False, west=False, waterlogged=False))
    # Bugspriet, Klüver, Galionsfigur
    xb = int(half) - 1
    yb = int(round(float(do(xb)))) + 1
    lang = half * 0.55
    spitze = (xb + lang * math.cos(0.42), yb + lang * math.sin(0.42))
    for t in np.linspace(0, 1, int(lang * 2) + 2):
        w.setze(round(xb + (spitze[0] - xb) * t), round(yb + (spitze[1] - yb) * t), 0, w.b("spruce_log", axis="x"))
    xf, ff = masten[0]
    yf = int(round(float(do(xf)))) + 1
    dreieckssegel(w, (spitze[0] - 1, spitze[1] - 1), (xf + 2, yf + Hm * ff * 0.7), (xf + 2, yf + 2), 0,
                  w.b("white_wool"))
    G = Skulptur(w, u)
    G.mat("g", w.b("gold_block"))
    G.plus(kap((0, 0, 0), (1.8, 1.2, 0), 0.7, 0.45), "g")
    G.plus(ell(2.2, 1.6, 0, 0.6, 0.6, 0.6), "g")
    G.rendern((-1, -1, -2), (3, 3, 2), versatz=(xb + 0.5, yb - 1.5 * u, 0.5))
    # Hecklaternen und Deckdetails
    xh = -int(half) + 1
    yh = int(round(float(do(xh)))) + 1
    for z in (-int(B * 0.6), 0, int(B * 0.6)):
        pfosten(w, xh, yh, yh + _r(u, 1), z, "dark_oak_fence" if False else "spruce_fence") if False else None
        w.setze(xh, yh, z, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
        w.setze(xh, yh + 1, z, w.b("lantern", hanging=False, waterlogged=False))
    for x, y, z in r["oben"]:
        if w.rng.random() < 0.025 and abs(z) < B - 1.5 and abs(x) < half * 0.4:
            w.setze(x, y + 1, z, w.b("barrel", facing="up", open=False))
    # Ruder
    for y in range(int(-D) + 1, int(F)):
        w.setze(-int(half) - 1, y, 0, w.b("dark_oak_planks"))
    return w


# ============================================================================ Luftschiff

def luftschiff(seed, g=1):
    """Steampunk-Luftschiff: Holzrumpf mit Kupferkiel unter einem gestreiften Ballon mit Kupferspanten,
    Leitwerk, seitlichen Propellern an Auslegern, Schornstein, Kajüte und Laternen."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        bahnen = ["red_wool", "yellow_terracotta"]
        holz = dict(unten=Verlauf(w, "Rumpf", ["waxed_cut_copper", "waxed_copper_block", "dark_oak_planks"]),
                    wand=Verlauf(w, "Wand", ["dark_oak_planks", "spruce_planks", "stripped_spruce_log"]),
                    streifen="waxed_cut_copper", leiste="stripped_dark_oak_log", zaun="dark_oak_fence",
                    deck=Verlauf(w, "Deck", ["spruce_planks", "oak_planks", "stripped_oak_log"]),
                    fenster="orange_stained_glass")
    else:
        bahnen = ["blue_wool", "white_wool"]
        holz = dict(unten=Verlauf(w, "Rumpf", ["waxed_oxidized_cut_copper", "waxed_weathered_cut_copper",
                                               "spruce_planks"]),
                    wand=Verlauf(w, "Wand", ["spruce_planks", "oak_planks", "stripped_birch_log"]),
                    streifen="waxed_oxidized_cut_copper", leiste="stripped_spruce_log", zaun="spruce_fence",
                    deck=Verlauf(w, "Deck", ["oak_planks", "birch_planks", "stripped_birch_log"]),
                    fenster="light_blue_stained_glass")
    L = 22 * u + 5
    B = 2.8 * u + 1
    y0 = _r(5 * u, 3) + 3
    r = rumpf(w, L, B, 2 * u + 1, 2 * u + 1, u, holz, y0=y0, kanonen=False)
    half, do = r["half"], r["deck_oben"]
    yd = y0 + int(round(float(r["deck_haupt"](0))))
    # Ballon
    cy = yd + 9 * u + 2
    Lb, Rb = L * 0.62, 4.8 * u + 1
    S = Skulptur(w, 1.0)
    bids = [w.b(b) for b in bahnen]

    def huelle(x, y, z, lx, ly, lz):
        a = math.atan2(lz, ly - cy)
        if abs(lx) % max(3, int(5 * u)) < 1 or abs(lx) > Lb - 1.5:
            return w.b("waxed_cut_copper")
        return bids[int((a + math.pi) / (2 * math.pi) * 14) % 2]
    S.mat("h", huelle)
    S.mat("a", w.b("gold_block"))

    def ballon(X, Y, Z):
        d = (X / Lb) ** 2 + ((Y - cy) / Rb) ** 2 + (Z / Rb) ** 2
        return (d <= 1) & (d > 0.72)
    S.plus(ballon, "h")
    S.plus(ell(Lb - 0.5, cy, 0, 1.2, 1.2, 1.2), "a")
    flosse = max(0.6, 0.5 * u)
    S.plus(lambda X, Y, Z: (X < -Lb * 0.6) & (X > -Lb - 2 * u) & (np.abs(Z) <= flosse)
           & (np.abs(Y - cy) < Rb + 3 * u * (-X - Lb * 0.6) / (Lb * 0.4 + 2 * u)), "h")
    S.plus(lambda X, Y, Z: (X < -Lb * 0.6) & (X > -Lb - 2 * u) & (np.abs(Y - cy) <= flosse)
           & (np.abs(Z) < Rb + 3 * u * (-X - Lb * 0.6) / (Lb * 0.4 + 2 * u)), "h")
    S.rendern((-Lb - 3 * u - 2, cy - Rb - 4 * u - 2, -Rb - 4 * u - 2), (Lb + 2, cy + Rb + 4 * u + 2, Rb + 4 * u + 2))
    # Tragseile
    unterseite = cy - Rb * 0.85
    for x in range(-int(half * 0.6), int(half * 0.6) + 1, max(3, int(4 * u))):
        for s in (-1, 1):
            linie(w, (x, yd + 1, s * int(B - 1)), (x, unterseite, s * int(Rb * 0.5)),
                  w.b("chain", axis="y", waterlogged=False))
    # Kajüte
    kx0, kx1 = -int(half * 0.45), -int(half * 0.1)
    kz = max(1, int(B - 2))
    kh = _r(2.5 * u, 2)
    for x in range(kx0, kx1 + 1):
        for z in range(-kz, kz + 1):
            for y in range(yd + 1, yd + 1 + kh):
                rand = x in (kx0, kx1) or abs(z) == kz
                if rand:
                    fenster = y == yd + 2 and (x + z) % 2 == 0 and not (x in (kx0, kx1) and abs(z) == kz)
                    w.setze(x, y, z, w.b(holz["fenster"]) if fenster else w.b("stripped_dark_oak_log", axis="y")
                            if x in (kx0, kx1) and abs(z) == kz else w.b("spruce_planks"))
            w.setze(x, yd + 1 + kh, z, w.b("waxed_cut_copper_slab" if abs(z) == kz else "waxed_cut_copper",
                                            **({"type": "bottom", "waterlogged": False} if abs(z) == kz else {})))
    # Schornstein
    sx_ = kx1 + 2
    for y in range(yd + 1, yd + 2 + kh + _r(3 * u, 2)):
        w.setze(sx_, y, 0, w.b("bricks"))
    w.setze(sx_, yd + 2 + kh + _r(3 * u, 2), 0, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                    waterlogged=False))
    # Ausleger mit Propellern
    for s in (-1, 1):
        zp = s * (int(B) + _r(3 * u, 2))
        for z in range(s * int(B - 1), zp + s, s):
            w.setze(-int(half * 0.2), yd, z, w.b("waxed_cut_copper"))
        R = _r(2.2 * u, 2)
        zahnrad(w, -int(half * 0.2) - 1, yd, zp, R, ebene="zy", material="spruce_planks", nabe="waxed_copper_block")
        for k in range(-R - 1, R + 2):
            w.setze(-int(half * 0.2) - 1, yd + k, zp, w.b("spruce_planks"))
            w.setze(-int(half * 0.2) - 1, yd, zp + k, w.b("spruce_planks"))
    # Laternen an Bug und Heck
    for x in (int(half) - 2, -int(half) + 2):
        w.setze(x, yd + int(round(float(do(x) - r["deck_haupt"](x)))) + 1, 0, w.b("lantern", hanging=False,
                                                                                  waterlogged=False))
    return w


# ============================================================================ Zeppelin

def zeppelin(seed, g=2):
    """Starrluftschiff mit Spantenringen, Zierstreifen, Kreuzleitwerk, verglaster Gondel und Motorgondeln."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        huelle = Verlauf(w, "Hülle", ["light_gray_concrete", "light_gray_wool", "white_concrete", "white_wool"])
        streifen, akzent = "red_concrete", "red_wool"
    else:
        huelle = Verlauf(w, "Hülle", ["gray_concrete", "light_gray_concrete", "light_gray_wool", "white_concrete"])
        streifen, akzent = "black_concrete", "yellow_concrete"
    L = 20 * u + 6
    R = 3.8 * u + 1
    cy = 8 * u + R + 4
    S = Skulptur(w, 1.0)
    rippe = max(3, int(4 * u))

    def mat(x, y, z, lx, ly, lz):
        if abs(lx) > L / 2 - 1.5 or abs(ly - cy) < 0.5 and lz > 0:
            return w.b(streifen)
        if int(lx) % rippe == 0:
            return w.b("light_gray_concrete" if _stil(seed) == 0 else "gray_concrete")
        return huelle(1.5 + 1.5 * (ly - cy) / R + w.rng.random() * 0.4, x, y, z)
    S.mat("h", mat)
    S.mat("f", w.b(akzent))
    S.mat("s", w.b(streifen))

    def koerper(X, Y, Z):
        uu = np.clip(X / (L / 2), -1, 1)
        r = R * np.clip(1 - np.abs(uu) ** 2.4, 0, 1) ** 0.5
        d = np.sqrt((Y - cy) ** 2 + Z ** 2)
        return (np.abs(X) <= L / 2) & (d <= r) & (d > r - 1.3)
    S.plus(koerper, "h")
    dick = max(0.6, 0.45 * u)
    fl = 4 * u + 1
    for (ay, az) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        def flosse(X, Y, Z, ay=ay, az=az):
            t = np.clip((-X - L * 0.3) / (L * 0.2), 0, 1)
            radial = (Y - cy) * ay + Z * az
            quer = np.abs((Y - cy) * az - Z * ay)
            return (X < -L * 0.3) & (X > -L / 2 - 1) & (quer <= dick) & (radial > 0) & (radial < R * 0.6 + fl * t)
        S.plus(flosse, "f")
    # Gondel
    gl, gh, gb = 5 * u + 2, 1.6 * u + 1, 1.4 * u + 0.8
    gy = cy - R - gh - 0.5
    S.mat("g", Verlauf(w, "Gondel", ["waxed_copper_block", "waxed_cut_copper", "waxed_exposed_cut_copper"]),
          basis=1, rausch=1)
    S.mat("glas", w.b("light_blue_stained_glass"))
    S.plus(kap((-gl, gy, 0), (gl, gy, 0), gb, gb * 0.8, zf=1.0), "g")
    gondel = kap((-gl, gy, 0), (gl, gy, 0), gb, gb * 0.8)
    S.plus(lambda X, Y, Z: gondel(X, Y, Z) & (np.abs(X) < gl - 0.5) & (np.abs(Y - gy - 0.3) < max(0.5, 0.35 * u))
           & (np.abs(Z) > gb * 0.4), "glas")
    S.plus(kasten(-gl * 0.6, gy, -0.4, gl * 0.6, cy - R + 1, 0.4), "g")
    # Motorgondeln mit Propellern
    for s in (-1, 1):
        mx, mz = -L * 0.12, s * (R + 2 * u)
        S.plus(ell(mx, cy - R * 0.55, mz, 2 * u + 0.8, 0.9 * u + 0.5, 0.9 * u + 0.5), "g")
        S.plus(kap((mx, cy - R * 0.55, mz), (mx, cy - R * 0.4, s * R * 0.7), max(0.5, 0.3 * u)), "g")
        S.plus(lambda X, Y, Z, mx=mx, mz=mz: (np.abs(X - (mx - 2 * u - 1.2)) <= 0.5)
               & (((np.abs(Y - (cy - R * 0.55)) <= 0.5) & (np.abs(Z - mz) <= 2 * u + 0.6))
                  | ((np.abs(Z - mz) <= 0.5) & (np.abs(Y - (cy - R * 0.55)) <= 2 * u + 0.6))), "s")
    S.rendern((-L / 2 - 3, gy - gb - 2, -R - fl - 3), (L / 2 + 2, cy + R + fl + 2, R + fl + 3))
    return w


# ============================================================================ Dampf-Uhrturm

def dampfturm(seed, g=1):
    """Steampunk-Uhrturm: Ziegel mit Steinecken, Uhren auf allen vier Seiten, Balkon, Patina-Kuppel mit
    Laterne und Blitzableiter, Zahnräder, Kupferrohre, rauchende Kamine und ein Kesselhaus."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        wand = Verlauf(w, "Ziegel", ["mud_bricks", "bricks", "bricks", "terracotta"])
        ecke, sockel_m = "polished_andesite", "stone_brick"
    else:
        wand = Verlauf(w, "Ziegel", ["deepslate_bricks", "polished_deepslate", "deepslate_tiles", "polished_blackstone"])
        ecke, sockel_m = "polished_granite", "polished_granite"
    kup = Verlauf(w, "Kupfer", ["waxed_copper_block", "waxed_cut_copper", "waxed_exposed_cut_copper",
                                "waxed_weathered_cut_copper", "waxed_oxidized_cut_copper"])
    patina = Verlauf(w, "Patina", ["waxed_exposed_copper", "waxed_weathered_copper", "waxed_oxidized_copper",
                                   "waxed_oxidized_cut_copper"])
    h = _r(3.6 * u, 3)
    Hb = _r(16 * u, 9)
    # Sockelprofil
    for x in range(-h - 1, h + 2):
        for z in range(-h - 1, h + 2):
            if abs(x) == h + 1 or abs(z) == h + 1:
                w.setze(x, 0, z, w.b(f"{sockel_m}_stairs", facing=zur_mitte(x, z), half="bottom", shape="straight",
                                     waterlogged=False) if not (abs(x) == h + 1 and abs(z) == h + 1)
                        else w.b("polished_andesite"))
    fh = _r(4 * u, 3)
    for y in range(Hb):
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                ax, az = abs(x) == h, abs(z) == h
                if not (ax or az):
                    continue
                if ax and az:
                    blk = w.b(ecke if (y // max(1, int(u))) % 2 == 0 else "stone_bricks")
                elif y % fh in (1, 2) and y > 2 and (abs(x) <= max(1, h // 3) or abs(z) <= max(1, h // 3)):
                    blk = w.b("orange_stained_glass")
                elif y % fh == 0 and y > 0:
                    blk = w.b("waxed_cut_copper")
                else:
                    blk = wand(1 + 2 * y / Hb + w.rng.random() * 0.6, x, y, z)
                w.setze(x, y, z, blk)
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(0, y, h, w.b("dark_oak_door", facing="north", half=half, hinge="left", open=False, powered=False))
    # Balkon unter der Uhrenstufe
    for x in range(-h - 2, h + 3):
        for z in range(-h - 2, h + 3):
            m = max(abs(x), abs(z))
            if m == h + 1:
                w.setze(x, Hb - 1, z, treppe(w, "waxed_cut_copper", zur_mitte(x, z), "top")
                        if not (abs(x) == h + 1 and abs(z) == h + 1) else w.b("waxed_cut_copper"))
            if h < m <= h + 2:
                w.setze(x, Hb, z, w.b("waxed_cut_copper"))
    verbinde(w, [(x, Hb + 1, z) for x in range(-h - 2, h + 3) for z in range(-h - 2, h + 3)
                 if max(abs(x), abs(z)) == h + 2], "iron_bars")
    # Uhrenstufe
    hu = h + 1
    Hu = _r(2 * h + 3, 5)
    for y in range(Hb, Hb + Hu):
        for x in range(-hu, hu + 1):
            for z in range(-hu, hu + 1):
                if max(abs(x), abs(z)) == hu:
                    w.setze(x, y, z, kup(1 + 2.5 * (y - Hb) / Hu + w.rng.random() * 0.5, x, y, z))
    Ru = max(2, hu - 1)
    cyu = Hb + Hu // 2
    for s in (-1, 1):
        uhr(w, (0, cyu, s * (hu + 1)), Ru, "xy")
        uhr(w, (s * (hu + 1), cyu, 0), Ru, "zy")
    # Kuppel mit Laterne
    yk = Hb + Hu
    rk = hu + 0.5
    hk = rk * 1.25
    for x in range(-hu - 1, hu + 2):
        for z in range(-hu - 1, hu + 2):
            for y in range(0, int(hk) + 2):
                d = (x / rk) ** 2 + (z / rk) ** 2 + (y / hk) ** 2
                if 0.6 < d <= 1:
                    w.setze(x, yk + y, z, patina(3 * y / hk + w.rng.random() * 0.6, x, yk + y, z))
    yl = yk + int(hk)
    for x in (-1, 0, 1):
        for z in (-1, 0, 1):
            if abs(x) + abs(z) == 2:
                pfosten(w, x, yl, yl + 1, z, "stone_brick_wall") if False else w.setze(x, yl, z, w.b("waxed_cut_copper"))
    w.setze(0, yl, 0, w.b("glowstone"))
    w.setze(0, yl + 1, 0, w.b("gold_block"))
    w.setze(0, yl + 2, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for k in range(_r(2 * u, 1)):
        w.setze(0, yl + 3 + k, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    # Zahnräder an der Flanke
    zahnrad(w, h + 1, int(Hb * 0.45), 0, _r(2.4 * u, 2), ebene="zy", material="waxed_cut_copper",
            nabe="waxed_copper_block")
    zahnrad(w, h + 1, int(Hb * 0.45) + _r(3.6 * u, 3), _r(2.6 * u, 2), _r(1.4 * u, 1), ebene="zy",
            material="waxed_exposed_cut_copper", nabe="gold_block")
    # Kupferrohre an zwei Ecken
    for (x, z) in ((-h - 1, -h + 1), (h - 1, -h - 1)):
        for y in range(1, Hb - 1):
            w.setze(x, y, z, w.b("waxed_cut_copper" if y % 4 else "waxed_copper_block"))
    # Kamine
    for s in (-1, 1):
        x = s * (h - 1)
        z = -(h - 1)
        for y in range(yk, yk + _r(4 * u, 3)):
            w.setze(x, y, z, w.b("bricks"))
        w.setze(x, yk + _r(4 * u, 3), z, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                              waterlogged=False))
    # Kesselhaus mit liegendem Kessel
    kx = -h - 2 - _r(4 * u, 3)
    rk2 = max(1.5, 2.2 * u)
    for x in range(kx - _r(3 * u, 2), -h - 1):
        for y in range(0, int(2 * rk2) + 2):
            for z in range(-int(rk2) - 1, int(rk2) + 2):
                d = math.hypot(y - rk2 - 0.5, z)
                if d <= rk2:
                    band = (x - kx) % 3 == 0
                    w.setze(x, y, z, w.b("waxed_copper_block") if band else kup(1.5 + d / rk2, x, y, z))
    xs = kx - _r(3 * u, 2) - 1
    for y in range(0, int(2 * rk2) + _r(6 * u, 4)):
        for dx, dz in ((0, 0), (1, 0), (0, 1), (1, 1)) if u > 1.2 else ((0, 0),):
            w.setze(xs + dx, y, dz, w.b("bricks") if y % 5 else w.b("waxed_cut_copper"))
    w.setze(xs, int(2 * rk2) + _r(6 * u, 4), 0, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                    waterlogged=False))
    for z in (-int(rk2) - 2, int(rk2) + 2):
        laterne(w, kx, 0 + 1, z) if False else w.setze(kx, 1, z, w.b("lantern", hanging=False, waterlogged=False))
    return w


def uhr(w, c, R, ebene):
    """Zifferblatt mit Goldring, Stundenmarken und Zeigern auf 10 nach 10."""
    cx, cy, cz = c
    feld = {}
    for a in range(-R - 1, R + 2):
        for b in range(-R - 1, R + 2):
            d = math.hypot(a, b)
            if d <= R + 0.4:
                feld[(a, b)] = "gold_block" if d > R - 0.7 else "smooth_quartz"
    for k in range(12):
        ang = k * math.pi / 6
        feld[(round(math.sin(ang) * (R - 1.5)), round(math.cos(ang) * (R - 1.5)))] = "polished_blackstone"
    for ang, lang in ((-math.pi / 3, 0.5), (math.pi / 3, 0.8)):
        for t in np.linspace(0, lang * (R - 1), int(R * 2) + 1):
            feld[(round(math.sin(ang) * t), round(math.cos(ang) * t))] = "polished_blackstone"
    feld[(0, 0)] = "gold_block"
    for (a, b), n in feld.items():
        if ebene == "xy":
            w.setze(cx + a, cy + b, cz, w.b(n))
        else:
            w.setze(cx, cy + b, cz + a, w.b(n))


# ============================================================================ Dampffabrik

def fabrik(seed, g=1):
    """Fabrikhalle mit Lisenen, Rundbogenfenstern, verglastem Sheddach, runden Schloten mit Bändern,
    Wasserturm, liegenden Kesseln, Schwungrad und Rohrleitungen."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        wand = Verlauf(w, "Ziegel", ["mud_bricks", "bricks", "bricks", "terracotta"])
        lisene = "nether_bricks" if False else "red_nether_bricks"
    else:
        wand = Verlauf(w, "Ziegel", ["deepslate_bricks", "polished_deepslate", "deepslate_tiles", "tuff"])
        lisene = "polished_blackstone_bricks"
    kup = Verlauf(w, "Kupfer", ["waxed_copper_block", "waxed_cut_copper", "waxed_exposed_cut_copper",
                                "waxed_weathered_cut_copper"])
    bx, bz, H = _r(9 * u, 5), _r(5.5 * u, 3), _r(6 * u, 4)
    for x in range(-bx - 1, bx + 2):
        for z in range(-bz - 1, bz + 2):
            w.setze(x, 0, z, w.b("polished_andesite"))
    for y in range(1, H + 1):
        for x in range(-bx, bx + 1):
            for z in range(-bz, bz + 1):
                ax, az = abs(x) == bx, abs(z) == bz
                if not (ax or az):
                    continue
                t = x if az else z
                if (ax and az) or t % 4 == 0:
                    blk = w.b(lisene)
                elif y == H:
                    blk = w.b("stone_bricks")
                elif 2 <= y <= H - 2 and t % 4 in (1, 2, 3) and y < H - 1:
                    blk = w.b("glass") if not (y == H - 2 and t % 4 != 2) else wand(2, x, y, z)
                else:
                    blk = wand(1 + 2 * y / H + w.rng.random() * 0.5, x, y, z)
                w.setze(x, y, z, blk)
    # Sheddach
    zahn = _r(3 * u, 2)
    for x0 in range(-bx, bx, zahn):
        for k in range(zahn):
            x = x0 + k
            if x > bx:
                break
            for z in range(-bz, bz + 1):
                w.setze(x, H + 1 + k, z, kup(1 + 2.5 * k / zahn, x, H + 1 + k, z))
                for y in range(H + 1, H + 1 + k):
                    if x == x0 + zahn - 1:
                        pass
            for z in range(-bz, bz + 1):
                if k == zahn - 1:
                    for y in range(H + 1, H + 1 + zahn):
                        w.setze(x + 1, y, z, w.b("glass") if abs(z) < bz else w.b("waxed_cut_copper"))
    # Schlote
    for sx_, hoehe in ((-bx + _r(2 * u, 2), 1.0), (bx - _r(2 * u, 2), 0.8)):
        r = max(1, 1.2 * u)
        zs = -bz - int(r) - 2
        hs = int((H + 14 * u) * hoehe)
        for y in range(0, hs):
            for x, z in scheibe(r):
                w.setze(sx_ + x, y, zs + z, w.b("waxed_cut_copper") if y % _r(5 * u, 3) == 0
                        else wand(1.5 + y / hs, sx_ + x, y, zs + z))
        for x, z in kreisrand(r + 1):
            w.setze(sx_ + x, hs, zs + z, w.b("bricks"))
        w.setze(sx_, hs, zs, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    # Wasserturm auf Stelzen
    wx, wz = bx + _r(4 * u, 3), bz - 1
    rw = max(1.5, 2 * u)
    hw = _r(H + 2 * u, 5)
    for dx in (-1, 1):
        for dz in (-1, 1):
            for y in range(0, hw):
                w.setze(wx + dx * int(rw), y, wz + dz * int(rw), w.b("spruce_fence", north=False, south=False,
                                                                     east=False, west=False, waterlogged=False))
    for y in range(hw, hw + _r(3 * u, 3)):
        for x, z in scheibe(rw):
            w.setze(wx + x, y, wz + z, kup(1 + 2 * (y - hw) / (3 * u) + w.rng.random() * 0.4, wx + x, y, wz + z))
    for k in range(int(rw) + 1):
        for x, z in scheibe(rw - k):
            w.setze(wx + x, hw + _r(3 * u, 3) + k, wz + z, w.b("waxed_oxidized_cut_copper"))
    # Kessel vor der Halle
    rk = max(1.2, 1.5 * u)
    for x in range(-bx + 2, -bx + 2 + _r(6 * u, 4)):
        for y in range(0, int(2 * rk) + 2):
            for z in range(-int(rk) - 1, int(rk) + 2):
                d = math.hypot(y - rk - 0.5, z - (bz + int(rk) + 2))
                if d <= rk:
                    w.setze(x, y, z + 0, w.b("waxed_copper_block") if x % 3 == 0 else kup(1.5 + d / rk, x, y, z))
    # Schwungrad
    zahnrad(w, bx - _r(3 * u, 2), _r(3 * u, 2), bz + 1, _r(2.6 * u, 2), material="waxed_cut_copper",
            nabe="waxed_copper_block")
    # Rohrleitung zum Wasserturm
    for x in range(bx, wx - int(rw) + 1):
        w.setze(x, H - 1, wz, w.b("waxed_cut_copper"))
    for z in (-bz - 1, bz + 1):
        for x in range(-bx + 2, bx - 1, max(4, int(5 * u))):
            w.setze(x, 1, z + (1 if z > 0 else -1), w.b("lantern", hanging=False, waterlogged=False))
    return w


SCHIFFE = {
    "segelschiff": ("Galeone", segelschiff),
    "luftschiff": ("Luftschiff", luftschiff),
    "zeppelin": ("Zeppelin", zeppelin),
    "dampfturm": ("Dampf-Uhrturm", dampfturm),
    "fabrik": ("Dampffabrik", fabrik),
}

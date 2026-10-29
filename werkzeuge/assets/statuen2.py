"""Statuen & Magie II – zwanzig weitere Statuen und magische Monumente (eigene Entwürfe): Laternenträger, Eule,
Hirsch, heulender Wolf, Bär, Engel, Mönch, Kniender Steinriese, Wasserträgerin, Bogenschützin, Magier, Aufbäumendes
Pferd, Drachenkopf-Brunnen, Phönix, Weltenkugel in Händen, Schlafender Riese, Tempelkatze, Fuchs, Runenkreis und
Arkane Monolithen. Zwei Stile (Marmor / Bronze) je Vorlage."""

from __future__ import annotations

import math

import numpy as np

from fantasie import U, _r, _stil, _welt
from lib import Verlauf
from skulptur import (SOCKEL, Skulptur, ell, kap, kasten, kegel, laterne, ohne, sockel, spiegel_x, torus, und)


def stil(w, seed):
    if _stil(seed) == 0:
        return (Verlauf(w, "Marmor", ["andesite", "stone", "smooth_stone", "polished_diorite", "calcite",
                                      "smooth_quartz"]), SOCKEL["schiefer"])
    return (Verlauf(w, "Bronze", ["waxed_oxidized_copper", "waxed_oxidized_cut_copper", "waxed_weathered_cut_copper",
                                  "waxed_weathered_copper", "waxed_exposed_copper"]), SOCKEL["stein"])


def basis(w, seed, g, sx, sz, hs=3.0, stufen=None, m=None):
    u = U[g]
    haut, msock = stil(w, seed)
    m = m or msock
    st = stufen if stufen is not None else [2, 2, 3, 4][g]
    sxx, szz = _r(sx * u, 2), _r(sz * u, 2)
    top = sockel(w, m, sxx + 2 + st + 1, szz + 2 + st + 1, st, sxx, szz, _r(hs * u, 2))
    return u, haut, top


def skulptur(w, u, haut, H, extra=None):
    S = Skulptur(w, u)
    S.mat("k", haut, basis=0.4, steigung=4.2 / H, rausch=0.7)
    S.mat("a", w.b("gold_block"))
    S.mat("d", w.b("polished_blackstone"))
    S.mat("w", w.b("white_concrete"))
    for k, v in (extra or {}).items():
        S.mat(k, v)
    return S


# ============================================================================ Figuren

def laternentraeger(seed, g=1):
    """Laternenträger: ein Wanderer im langen Kapuzenmantel stützt sich auf einen Stab und hält eine echte, brennende
    Laterne hoch über den Kopf."""
    w = _welt(seed)
    u, haut, top = basis(w, seed, g, 3.6, 3.6)
    S = skulptur(w, u, haut, 20)
    S.plus(kegel(0, 0, 0, 13, 4.2, 2.2, zf=0.8), "k")
    S.plus(kap((0, 12, 0), (0, 15, 0), 2.6, 2.2, zf=0.85), "k")
    S.plus(ell(0, 16.6, 0.2, 1.7, 2.0, 1.8), "k")
    S.plus(und(ell(0, 16.4, 1.2, 1.3, 1.5, 1.0), lambda X, Y, Z: Z > 1.0), "d")
    S.plus(kap((0, 16.6, -0.4), (0, 18.6, -1.8), 1.6, 0.6), "k")
    S.plus(kap((2.2, 14.6, 0), (3.6, 18.5, 0.6), 0.85, 0.7), "k")
    S.plus(kap((3.6, 18.5, 0.6), (3.6, 21.5, 0.6), 0.25), "d")
    S.plus(kap((-2.1, 14.4, 0.4), (-3.0, 10.5, 1.6), 0.85, 0.75), "k")
    S.plus(kap((-3.3, 0, 1.8), (-3.3, 17, 1.8), 0.45), "d")
    S.rendern((-6, 0, -5), (6, 23, 5), versatz=(0.5, top, 0.5))
    xl, yl = round(3.6 * u + 0.5), top + round(21.5 * u)
    w.setze(xl, yl, round(0.6 * u + 0.5), w.b("lantern", hanging=True, waterlogged=False))
    return w


def eule(seed, g=1):
    """Eulenstatue: eine große Eule mit Federohren und goldenen Augen hockt auf einem knorrigen Ast, die Flügel
    angelegt, Federschuppen auf der Brust."""
    w = _welt(seed)
    u, haut, top = basis(w, seed, g, 3.4, 3.0, hs=2.5)
    S = skulptur(w, u, haut, 16)
    S.plus(kap((-4.5, 1.2, 0), (4.5, 1.6, 0.4), 1.2), "d")
    S.plus(ell(0, 7, 0, 3.6, 5.2, 3.2), "k")
    S.plus(ell(0, 13, 0.3, 3.2, 2.8, 2.9), "k")
    for sx in (-1, 1):
        S.plus(kap((sx * 2.0, 15.0, 0), (sx * 2.6, 17.3, -0.4), 0.8, 0.3), "k")
        S.plus(ell(sx * 1.3, 13.4, 2.6, 1.0, 1.0, 0.6), "a")
        S.plus(ell(sx * 1.3, 13.4, 3.0, 0.45, 0.45, 0.4), "d")
        S.plus(ell(sx * 3.4, 7.5, -0.3, 1.0, 4.4, 2.6), "k")
        S.plus(kap((sx * 1.0, 2.2, 1.0), (sx * 1.2, 1.6, 2.2), 0.45), "a")
    S.plus(kap((0, 12.6, 3.0), (0, 11.6, 3.4), 0.45, 0.2), "a")
    S.plus(kegel(0, -0.5, 0, 1.2, 1.4, 1.2), "d")
    S.rendern((-6, 0, -5), (6, 19, 5), versatz=(0.5, top, 0.5))
    return w


def hirsch(seed, g=1):
    """Hirschstatue: ein stolzer Hirsch mit gewaltigem, verzweigtem Geweih steht mit erhobenem Kopf auf einem
    Felssockel, ein Vorderlauf angewinkelt."""
    w = _welt(seed)
    u, haut, top = basis(w, seed, g, 5.0, 2.4, hs=2.5)
    S = skulptur(w, u, haut, 20)
    S.plus(ell(0, 9, 0, 5.2, 2.6, 2.2), "k")
    for (x, z, knick) in ((-3.6, 1.0, 0), (-3.6, -1.0, 0), (3.4, -1.0, 0), (3.4, 1.0, 1)):
        if knick:
            S.plus(kap((x, 8, z), (x + 1.4, 5, z), 0.75, 0.6), "k")
            S.plus(kap((x + 1.4, 5, z), (x + 0.6, 3.4, z), 0.55, 0.45), "k")
        else:
            S.plus(kap((x, 8, z), (x, 0.3, z), 0.8, 0.45), "k")
    S.plus(kap((4.0, 10, 0), (5.6, 14.2, 0), 1.5, 1.1), "k")
    S.plus(kap((5.6, 14.5, 0), (7.6, 14.0, 0), 1.0, 0.65), "k")
    S.plus(kap((-5.0, 10, 0), (-5.8, 10.6, 0), 0.6), "k")
    for sz in (-1, 1):
        S.plus(ell(6.3, 15.2, sz * 1.1, 0.8, 0.4, 0.5), "k")
        S.plus(ell(6.7, 14.8, sz * 0.75, 0.3, 0.3, 0.25), "d")
        a = (5.4, 15.4, sz * 0.5)
        b = (4.6, 18.6, sz * 2.4)
        c = (3.2, 21.4, sz * 3.4)
        S.plus(kap(a, b, 0.4, 0.32), "k")
        S.plus(kap(b, c, 0.32, 0.2), "k")
        for (p, q) in ((b, (6.0, 20.4, sz * 2.8)), (((a[0] + b[0]) / 2, 17, sz * 1.4), (6.6, 18.0, sz * 1.8)),
                       (c, (4.6, 23, sz * 4.0)), (c, (1.8, 22.8, sz * 3.2))):
            S.plus(kap(p, q, 0.28, 0.18), "k")
    S.rendern((-7, 0, -6), (9, 25, 6), versatz=(0.5, top, 0.5))
    return w


def wolf(seed, g=1):
    """Heulender Wolf: ein sitzender Wolf hebt die Schnauze zum Himmel, das dichte Nackenfell und der buschige
    Schwanz sind in Stein gehauen, zu seinen Füßen ein Mond-Emblem."""
    w = _welt(seed)
    u, haut, top = basis(w, seed, g, 3.6, 3.6, hs=2.5)
    S = skulptur(w, u, haut, 18)
    S.plus(ell(0, 4, -1.2, 2.8, 3.4, 3.4), "k")
    S.plus(kap((0, 5, 0.6), (0, 11, 2.2), 2.4, 1.8), "k")
    S.plus(ell(0, 10.6, 2.6, 2.6, 2.4, 2.0), "k")
    S.plus(kap((0, 12.4, 2.6), (0, 15.6, 4.8), 1.5, 0.9), "k")
    S.plus(ell(0, 15.8, 5.6, 0.6, 0.6, 0.6), "d")
    for sx in (-1, 1):
        S.plus(kap((sx * 1.0, 13.8, 2.0), (sx * 1.3, 15.2, 1.0), 0.6, 0.2), "k")
        S.plus(kap((sx * 1.2, 6, 2.6), (sx * 1.2, 0.4, 3.2), 0.75, 0.6), "k")
        S.plus(ell(sx * 1.2, 0.5, 3.8, 0.8, 0.5, 1.0), "k")
        S.plus(ell(sx * 2.4, 2.0, -0.4, 1.4, 2.0, 2.4), "k")
        S.plus(ell(sx * 0.9, 13.4, 3.6, 0.3, 0.3, 0.3), "a")
    S.plus(kap((0, 1, -4), (2.6, 0.6, -5.8), 1.2, 0.8), "k")
    S.plus(kap((2.6, 0.6, -5.8), (4.4, 1.2, -4.2), 0.8, 0.5), "k")
    S.rendern((-6, 0, -7), (6, 18, 7), versatz=(0.5, top, 0.5))
    return w


def baer(seed, g=1):
    """Bärenstatue: ein mächtiger Bär richtet sich auf den Hinterbeinen auf, die Pranken mit Krallen erhoben, das
    Maul geöffnet."""
    w = _welt(seed)
    u, haut, top = basis(w, seed, g, 3.8, 3.6, hs=2.5)
    S = skulptur(w, u, haut, 20)
    for sx in (-1, 1):
        S.plus(kap((sx * 1.8, 0.8, 0.2), (sx * 1.9, 6, 0), 1.5, 1.8), "k")
        S.plus(ell(sx * 1.8, 0.7, 1.4, 1.2, 0.7, 1.6), "k")
        S.plus(kap((sx * 3.2, 13.6, 0.2), (sx * 4.4, 16.4, 2.0), 1.3, 1.0), "k")
        S.plus(ell(sx * 4.6, 17.0, 2.4, 1.2, 1.0, 1.0), "k")
        for k in (-1, 0, 1):
            S.plus(kap((sx * 4.6 + k * 0.5, 17.8, 2.6), (sx * 4.8 + k * 0.6, 18.6, 3.2), 0.18), "w")
        S.plus(ell(sx * 1.4, 18.6, 0.6, 0.6, 0.6, 0.5), "k")
    S.plus(ell(0, 9, 0, 3.6, 5.6, 3.0), "k")
    S.plus(ell(0, 16.2, 0.6, 2.3, 2.0, 2.2), "k")
    S.plus(kap((0, 15.6, 1.8), (0, 15.2, 3.8), 1.1, 0.9), "k")
    S.plus(und(ell(0, 14.9, 3.4, 0.8, 0.5, 0.9), lambda X, Y, Z: Y < 15.1), "d")
    for sx in (-1, 1):
        S.plus(ell(sx * 0.9, 16.8, 2.2, 0.3, 0.3, 0.3), "d")
    S.rendern((-7, 0, -5), (7, 20, 6), versatz=(0.5, top, 0.5))
    return w


def engel(seed, g=1):
    """Engelsstatue: eine Gestalt in fließendem Gewand mit hoch aufragenden Schwingen und goldenem Heiligenschein,
    die Hände vor der Brust gefaltet."""
    w = _welt(seed)
    u, haut, top = basis(w, seed, g, 3.6, 3.2)
    S = skulptur(w, u, haut, 22)
    S.plus(kegel(0, 0, 0, 12, 3.6, 2.0, zf=0.75), "k")
    S.plus(kap((0, 11.5, 0), (0, 14.8, 0), 2.0, 2.3, zf=0.7), "k")
    S.plus(ell(0, 16.6, 0, 1.4, 1.7, 1.5), "k")
    S.plus(spiegel_x(kap((2.2, 14.4, 0), (1.6, 11.6, 1.4), 0.75, 0.65)), "k")
    S.plus(spiegel_x(kap((1.6, 11.6, 1.4), (0.3, 13.0, 1.9), 0.65, 0.55)), "k")
    S.plus(ell(0, 13.2, 2.0, 0.7, 1.0, 0.6), "k")
    S.plus(torus(0, 19.0, -0.4, 1.6, 0.3, achse="z"), "a")
    d = S.dicke(0.5)

    def fluegel(X, Y, Z):
        Xa = np.abs(X)
        t = (Y - 8) / 16
        inner = (Xa > 1.2) & (Xa < 1.2 + 6.5 * np.sin(np.clip(t, 0, 1) * math.pi) ** 0.7 + 0.5) & (Y > 8) & (Y < 24)
        zc = -1.8 - 0.25 * (Xa - 1.2)
        return inner & (np.abs(Z - zc) <= d)
    S.plus(fluegel, "w" if _stil(seed) == 0 else "k")
    S.rendern((-9, 0, -6), (9, 25, 4), versatz=(0.5, top, 0.5))
    return w


def moench(seed, g=1):
    """Meditierender Mönch: eine sitzende Gestalt im Lotussitz mit gesenktem Blick und offenen Händen im Schoß,
    vor ihr Kerzen und eine Räucherschale."""
    w = _welt(seed)
    u, haut, top = basis(w, seed, g, 4.0, 3.6, hs=2.0)
    S = skulptur(w, u, haut, 14)
    S.plus(ell(0, 1.6, 0.6, 4.4, 1.7, 3.2), "k")
    S.plus(kap((0, 2.5, 0), (0, 7.5, -0.2), 2.6, 2.2, zf=0.75), "k")
    S.plus(spiegel_x(kap((2.4, 7.0, -0.2), (2.6, 4.0, 0.8), 0.7, 0.6)), "k")
    S.plus(spiegel_x(kap((2.6, 4.0, 0.8), (0.6, 3.4, 2.0), 0.6, 0.5)), "k")
    S.plus(ell(0, 3.5, 2.1, 1.0, 0.4, 0.8), "k")
    S.plus(ell(0, 9.6, 0, 1.5, 1.8, 1.6), "k")
    S.plus(ell(0, 9.4, 1.4, 0.3, 0.6, 0.3), "k")
    S.plus(kap((-3.0, 7.4, -0.6), (3.0, 7.4, -0.6), 0.6), "a")
    S.rendern((-6, 0, -5), (6, 12, 5), versatz=(0.5, top, 0.5))
    zf = top
    for x in (-3, 3):
        w.setze(round(x * u), zf, round(4 * u) + 1, w.b("candle", candles=3, lit=True, waterlogged=False))
    w.setze(0, zf, round(4 * u) + 1, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                          waterlogged=False))
    return w


def steinriese(seed, g=1):
    """Kniender Steinriese: ein grob behauener Golem kniet auf einem Bein, eine Faust auf den Boden gestützt, Moos
    und Gras wachsen auf Schultern und Kopf, die Augen glühen."""
    w = _welt(seed)
    u, haut, top = basis(w, seed, g, 4.4, 3.6, hs=1.5, stufen=1)
    S = skulptur(w, u, haut, 18, {"m": w.b("moss_block"), "l": w.b("shroomlight")})
    S.plus(kasten(-2.6, 0, -3.6, -0.6, 2.2, 0.6), "k")
    S.plus(kasten(-2.6, 0, -1.0, -0.6, 6, 1.4), "k")
    S.plus(kasten(0.6, 4.0, -1.4, 2.8, 6.2, 3.2), "k")
    S.plus(kasten(0.8, 0, 1.6, 2.8, 5, 3.6), "k")
    S.plus(kasten(-3.4, 5.6, -2.0, 3.4, 13, 2.2), "k")
    S.plus(kasten(-4.2, 10.6, -2.4, 4.2, 13.6, 2.6), "m")
    S.plus(kasten(-5.6, 6.5, -1.4, -3.4, 13, 1.4), "k")
    S.plus(kasten(-6.0, 0, -1.6, -3.2, 6.5, 1.6), "k")
    S.plus(kasten(3.4, 8, -1.2, 5.4, 13, 1.2), "k")
    S.plus(kasten(3.6, 5.4, 0.4, 5.6, 8.4, 3.6), "k")
    S.plus(kasten(-1.6, 13, -1.4, 1.6, 16.2, 1.6), "k")
    S.plus(kasten(-1.8, 16.0, -1.6, 1.8, 16.8, 1.8), "m")
    S.plus(kasten(-1.1, 14.4, 1.5, -0.4, 15.0, 1.8), "l")
    S.plus(kasten(0.4, 14.4, 1.5, 1.1, 15.0, 1.8), "l")
    S.rendern((-7, 0, -5), (7, 18, 5), versatz=(0.5, top, 0.5))
    for (x, y, z), b in list(w.bloecke.items()):
        if b == w.b("moss_block") and w.frei(x, y + 1, z) and w.rng.random() < 0.4:
            w.setze(x, y + 1, z, w.b("grass" if w.rng.random() < 0.7 else "fern"))
    return w


def wassertraegerin(seed, g=1):
    """Wasserträgerin: eine Frau im Faltengewand neigt einen großen Krug, aus dem ein echter Wasserstrahl in das
    Brunnenbecken zu ihren Füßen fließt."""
    w = _welt(seed)
    u = U[g]
    haut, m = stil(w, seed)
    R = _r(6 * u + 3, 4)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d <= R:
                w.setze(x, 0, z, w.b("stone_bricks"))
                w.setze(x, 1, z, w.b("chiseled_stone_bricks" if d > R - 1 else "water", **({} if d > R - 1 else
                                                                                         {"level": 0})))
    top = 1
    for y in range(1, _r(2 * u, 1) + 2):
        for x in range(-2, 3):
            for z in range(-2, 3):
                w.setze(x, y, z, w.b(m["saeule"]))
    top = _r(2 * u, 1) + 2
    S = skulptur(w, u, haut, 18)
    S.plus(kegel(0, 0, 0, 10, 3.0, 1.8, zf=0.8), "k")
    S.plus(kap((0, 9.5, 0), (0, 12.5, 0), 1.8, 1.9, zf=0.7), "k")
    S.plus(ell(0, 14.0, 0, 1.2, 1.5, 1.3), "k")
    S.plus(kap((0, 14.6, -0.6), (0, 12.0, -2.0), 0.9, 0.5), "k")
    S.plus(kap((1.8, 12, 0), (2.8, 13.8, 1.6), 0.6), "k")
    S.plus(kap((-1.8, 12, 0), (-1.0, 10.8, 1.8), 0.6), "k")
    S.plus(ell(1.8, 13.4, 2.6, 1.6, 1.4, 1.4), "k")
    S.plus(kap((1.8, 13.4, 2.6), (1.0, 12.6, 4.2), 0.55, 0.45), "k")
    S.rendern((-5, 0, -5), (5, 17, 6), versatz=(0.5, top, 0.5))
    xs, zs = round(1.0 * u + 0.5), round(4.6 * u + 0.5)
    for y in range(2, top + round(12.4 * u)):
        w.setze(xs, y, zs, w.b("water", level=0), False)
    return w


def bogenschuetzin(seed, g=1):
    """Bogenschützin: eine Schützin im Ausfallschritt spannt einen großen Langbogen, der Pfeil zeigt in die Ferne,
    der Köcher auf dem Rücken, das Haar im Zopf."""
    w = _welt(seed)
    u, haut, top = basis(w, seed, g, 4.0, 3.0)
    S = skulptur(w, u, haut, 20, {"h": w.b("dark_oak_planks"), "s": w.b("iron_block")})
    S.plus(kap((1.0, 0.6, 2.2), (0.8, 8, 0.2), 0.9, 1.2), "k")
    S.plus(kap((-1.0, 0.6, -2.6), (-0.8, 8, 0), 0.9, 1.2), "k")
    S.plus(kap((0, 8, 0), (0, 13.8, 0), 1.9, 2.2, zf=0.7), "k")
    S.plus(ell(0, 15.6, 0.2, 1.2, 1.5, 1.3), "k")
    S.plus(kap((0, 15.6, -1.0), (0, 11.4, -1.8), 0.6, 0.3), "k")
    S.plus(kap((2.0, 13.4, 0), (5.6, 13.6, 0.2), 0.6, 0.5), "k")
    S.plus(kap((-2.0, 13.4, 0), (-1.6, 13.6, 0.3), 0.6, 0.5), "k")
    S.plus(kap((-1.6, 13.6, 0.3), (1.0, 13.8, 0.3), 0.5), "k")
    bog = lambda X, Y, Z: (np.abs(np.sqrt((X - 4.0) ** 2 + (Y - 13.6) ** 2) - 5.0) < 0.45) & (X > 5.9) & \
        (np.abs(Z - 0.2) < S.dicke(0.4))
    S.plus(bog, "h")
    S.plus(kap((1.0, 13.8, 0.2), (10.8, 13.7, 0.2), 0.18), "s")
    S.plus(kap((-1.2, 10.6, -2.0), (1.2, 16.0, -2.4), 0.7), "h")
    S.rendern((-5, 0, -5), (12, 18, 4), versatz=(0.5, top, 0.5))
    return w


def magier(seed, g=1):
    """Magierstatue: ein bärtiger Magier mit spitzem Hut und weitem Mantel hält einen Stab, auf dem ein echter
    Amethystkristall leuchtet, Sterne zieren den Mantelsaum."""
    w = _welt(seed)
    u, haut, top = basis(w, seed, g, 3.6, 3.6)
    S = skulptur(w, u, haut, 24, {"c": w.b("amethyst_block"), "l": w.b("pearlescent_froglight", axis="y"),
                                  "h": w.b("dark_oak_planks")})
    S.plus(kegel(0, 0, 0, 13, 4.2, 2.2, zf=0.8), "k")
    S.plus(kap((0, 12.5, 0), (0, 15, 0), 2.3, 2.4, zf=0.7), "k")
    S.plus(ell(0, 16.6, 0.2, 1.4, 1.6, 1.4), "k")
    S.plus(kegel(0, 1.4, 12.0, 15.6, 2.4, 0.8), "k")
    S.plus(kegel(0, 0, 17.6, 18.2, 3.2, 3.2), "k")
    S.plus(kap((0, 18.0, 0), (0.6, 23.6, -1.2), 1.6, 0.3), "k")
    S.plus(spiegel_x(kap((2.3, 14.6, 0), (3.6, 12.0, 1.4), 0.8, 0.7)), "k")
    S.plus(kap((3.8, 0, 1.6), (3.8, 20, 1.6), 0.4), "h")
    S.plus(ell(3.8, 21.4, 1.6, 1.0, 1.6, 1.0), "c")
    S.plus(ell(3.8, 21.4, 1.6, 0.4, 0.5, 0.4), "l")
    for k in range(8):
        a = k / 8 * 6.283
        S.plus(ell(math.cos(a) * 4.0, 1.4, math.sin(a) * 3.2, 0.35, 0.35, 0.35), "a")
    S.rendern((-6, 0, -5), (6, 25, 5), versatz=(0.5, top, 0.5))
    return w


def pferd(seed, g=1):
    """Aufbäumendes Pferd: ein Hengst steigt auf die Hinterbeine, Mähne und Schweif wehen, die Vorderhufe
    schlagen in die Luft."""
    w = _welt(seed)
    u, haut, top = basis(w, seed, g, 4.6, 2.6)
    S = skulptur(w, u, haut, 22, {"m": haut})
    dreh = 0.75
    c, s_ = math.cos(dreh), math.sin(dreh)
    S.plus(kap((-2.6, 5.5, 0), (2.2, 5.5 + 4.6 * s_ / c * 0.9, 0), 2.6, 2.3, zf=0.8), "k")
    for sz in (-1, 1):
        S.plus(kap((-2.6, 5, sz * 1.1), (-2.0, 2.6, sz * 1.2), 0.9, 0.7), "k")
        S.plus(kap((-2.0, 2.6, sz * 1.2), (-2.6, 0.3, sz * 1.2), 0.6, 0.5), "k")
        S.plus(kap((1.8, 9.2, sz * 1.0), (4.2, 9.6, sz * 1.0), 0.7, 0.6), "k")
        S.plus(kap((4.2, 9.6, sz * 1.0), (4.6, 7.4, sz * 1.0), 0.55, 0.5), "k")
    S.plus(kap((2.4, 10, 0), (3.4, 15, 0), 1.6, 1.1, zf=0.8), "k")
    S.plus(kap((3.4, 15.2, 0), (5.6, 14.0, 0), 1.2, 0.7), "k")
    for sz in (-1, 1):
        S.plus(kap((3.2, 16.0, sz * 0.5), (3.0, 17.2, sz * 0.6), 0.35, 0.15), "k")
    S.plus(kap((2.2, 16, 0), (1.6, 11, 0), 0.6, 0.4), "k")
    S.plus(kap((-4.6, 6.4, 0), (-6.2, 3.0, 0), 0.8, 0.4), "k")
    S.plus(kap((-6.2, 3.0, 0), (-5.8, 0.8, 0), 0.4, 0.3), "k")
    S.rendern((-8, 0, -5), (8, 19, 5), versatz=(0.5, top, 0.5))
    return w


def drachenkopfbrunnen(seed, g=1):
    """Drachenkopf-Brunnen: aus einem runden Becken ragt der Kopf eines Drachen mit Hörnern und Kamm, aus seinem
    geöffneten Maul ergießt sich ein Wasserstrahl."""
    w = _welt(seed)
    u = U[g]
    haut, m = stil(w, seed)
    R = _r(7 * u + 3, 4)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d <= R:
                w.setze(x, 0, z, w.b("polished_deepslate"))
                if d > R - 1:
                    w.setze(x, 1, z, w.b("polished_deepslate_wall", up=True, north="none", south="none", east="none",
                                         west="none", waterlogged=False) if False else w.b("deepslate_tiles"))
                else:
                    w.setze(x, 1, z, w.b("water", level=0))
    S = skulptur(w, u, haut, 16, {"z": w.b("bone_block", axis="y"), "r": w.b("red_concrete")})
    S.plus(kap((0, 0, -3), (0, 8, -1.4), 2.6, 2.2), "k")
    S.plus(ell(0, 9.6, 0.4, 2.6, 2.4, 3.2), "k")
    S.plus(kap((0, 10.2, 2.2), (0, 9.6, 6.2), 1.7, 1.3), "k")
    S.plus(kap((0, 8.2, 2.0), (0, 7.4, 5.6), 1.3, 1.0), "k")
    S.plus(und(ell(0, 8.8, 4.4, 1.2, 0.7, 2.0), lambda X, Y, Z: Z > 3.0), "r")
    for sx in (-1, 1):
        S.plus(kap((sx * 1.6, 11.0, -0.6), (sx * 2.8, 14.6, -3.0), 0.55, 0.15), "z")
        S.plus(ell(sx * 1.5, 10.8, 2.6, 0.45, 0.45, 0.4), "a")
        for k in range(3):
            S.plus(kap((sx * 1.0, 10.0 - k * 0.7, 5.6 - k * 0.2), (sx * 1.0, 9.4 - k * 0.7, 5.8 - k * 0.2), 0.15), "z")
    for k in range(5):
        S.plus(kap((0, 11.8 - k * 1.6, -0.4 - k * 0.7), (0, 13.0 - k * 1.6, -1.2 - k * 0.7), 0.45, 0.1), "k")
    S.rendern((-5, 0, -5), (5, 15, 8), versatz=(0.5, 1, 0.5))
    zm = round(7.0 * u + 1.5)
    ym = 1 + round(8.6 * u)
    w.setze(0, ym, zm, w.b("water", level=0), False)
    for y in range(2, ym):
        w.setze(0, y, zm + 1, w.b("water", level=0), False)
    return w


def phoenix(seed, g=1):
    """Phönix-Statue: auf einer hohen Säule entfaltet ein Feuervogel seine flammenden Schwingen in Rot, Orange und
    Gold, die Schwanzfedern fließen wie Flammen herab."""
    w = _welt(seed)
    u = U[g]
    _, m = stil(w, seed)
    H = _r(8 * u + 4, 5)
    for y in range(0, H):
        for x in range(-1, 2):
            for z in range(-1, 2):
                w.setze(x, y, z, w.b("quartz_pillar", axis="y") if (x == 0 or z == 0) else w.b("smooth_quartz"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, 0, z, w.b("chiseled_quartz_block"))
            w.setze(x, H, z, w.b("chiseled_quartz_block"))
    S = Skulptur(w, u)
    S.mat("r", w.b("red_concrete"))
    S.mat("o", w.b("orange_concrete"))
    S.mat("y", w.b("gold_block"))
    S.mat("l", w.b("shroomlight"))
    S.plus(ell(0, 4, 0, 1.8, 3.0, 1.6), "r")
    S.plus(ell(0, 8, 0.6, 1.2, 1.3, 1.2), "o")
    S.plus(kap((0, 8, 1.6), (0, 7.4, 3.0), 0.4, 0.1), "y")
    S.plus(kap((0, 9, 0), (0, 11.4, -1.6), 0.5, 0.1), "y")
    d = S.dicke(0.5)

    def fluegel(X, Y, Z):
        Xa = np.abs(X)
        t = np.clip((Xa - 1.0) / 10, 0, 1)
        oben = 4 + 8 * np.sin(t * math.pi * 0.8)
        unten = 3 + 2 * t
        return (Xa > 1.0) & (Xa < 11) & (Y > unten) & (Y < oben) & (np.abs(Z + 0.5 + 0.2 * Xa) <= d)
    S.plus(fluegel, "o")
    S.plus(und(fluegel, lambda X, Y, Z: (np.abs(X) > 7) | (Y > 9)), "y")
    S.plus(und(fluegel, lambda X, Y, Z: (np.abs(X) < 3.5)), "r")
    for k in range(5):
        a = (k - 2) * 0.35
        S.plus(kap((0, 2.6, -1.0), (math.sin(a) * 4, -4.5 - abs(k - 2) * 0.5, -3.0), 0.6, 0.2),
               "y" if k % 2 else "o")
    S.plus(ell(0, 4.4, 0.2, 0.6, 0.6, 0.6), "l")
    S.rendern((-12, -6, -5), (12, 13, 4), versatz=(0.5, H - round(1.5 * u) + 1, 0.5))
    return w


def weltenkugel(seed, g=1):
    """Weltenkugel in Händen: zwei riesige steinerne Hände wachsen aus dem Boden und halten behutsam eine Kugel mit
    blauen Meeren und grünen Kontinenten."""
    w = _welt(seed)
    u, haut, top = basis(w, seed, g, 4.0, 4.0, hs=1.5, stufen=1)
    S = skulptur(w, u, haut, 14)
    rs = np.random.default_rng(seed)
    kont = [(rs.normal(size=3)) for _ in range(6)]

    def erde(x, y, z, lx, ly, lz):
        v = np.array([lx, ly - 10.0, lz])
        n = np.linalg.norm(v) + 1e-9
        v /= n
        land = max(float(v @ (k / np.linalg.norm(k))) for k in kont) > 0.8
        if abs(v[1]) > 0.88:
            return w.b("snow_block")
        return w.b("lime_terracotta" if land and (x + z) % 3 else "green_terracotta") if land else \
            w.b("blue_concrete" if (x + y) % 4 else "light_blue_concrete")
    S.mat("e", erde)
    for sx in (-1, 1):
        S.plus(kap((sx * 2.4, 0, 0), (sx * 3.4, 5.6, 0), 1.6, 1.4), "k")
        S.plus(ell(sx * 3.6, 7.0, 0, 1.4, 2.0, 2.6), "k")
        for k, zz in enumerate((-1.8, -0.6, 0.6, 1.8)):
            S.plus(kap((sx * 3.6, 8.2, zz), (sx * 2.4, 10.6 + 0.3 * (k % 2), zz * 1.2), 0.55, 0.45), "k")
        S.plus(kap((sx * 3.4, 6.6, 2.2), (sx * 1.4, 7.4, 3.6), 0.6, 0.5), "k")
    S.plus(ell(0, 10.0, 0, 4.4, 4.4, 4.4), "e")
    S.rendern((-7, 0, -6), (7, 15, 6), versatz=(0.5, top, 0.5))
    return w


def schlafender_riese(seed, g=1):
    """Schlafender Riese: ein überwachsener Steinriese liegt auf dem Rücken in der Wiese, Gras und Bäumchen
    wachsen auf Brust und Bauch, sein Gesicht ruhig mit geschlossenen Augen."""
    import wald2
    from lib import einfuegen
    w = _welt(seed)
    u = U[g]
    haut, _ = stil(w, seed)
    R = _r(16 * u + 6, 8)
    for x in range(-R, R + 1):
        for z in range(-int(R * 0.6), int(R * 0.6) + 1):
            if (x / R) ** 2 + (z / (R * 0.6)) ** 2 <= 1:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
                w.setze(x, -1, z, w.b("dirt"))
    S = Skulptur(w, u)
    fels = Verlauf(w, "Fels", ["mossy_cobblestone", "andesite", "stone", "mossy_stone_bricks"])
    S.mat("k", fels, basis=1.5, steigung=0, rausch=1.8)
    S.plus(ell(-10.5, 1.6, 0, 2.4, 2.4, 2.6), "k")
    S.plus(ell(-8.6, 2.6, 0, 0.8, 0.8, 0.8), "k")
    S.plus(kap((-8.0, 1.2, 0), (-6.4, 1.2, 0), 1.2), "k")
    S.plus(ell(-2, 1.8, 0, 5.6, 3.0, 4.0), "k")
    S.plus(ell(4.4, 1.6, 0, 3.2, 2.4, 3.2), "k")
    for sz in (-1, 1):
        S.plus(kap((-5.6, 1.0, sz * 3.6), (2.0, 0.8, sz * 5.0), 1.2, 1.0), "k")
        S.plus(kap((6.0, 1.0, sz * 1.8), (14.0, 1.0, sz * 2.2), 1.6, 1.2), "k")
        S.plus(kap((14.0, 1.0, sz * 2.2), (14.6, 3.2, sz * 2.2), 1.0, 0.9), "k")
    S.rendern((-14, -1, -8), (16, 6, 8), versatz=(0.5, 0, 0.5))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 0 and w.frei(x, y + 1, z) and b in fels.ids:
            r = rng.random()
            if r < 0.55:
                w.setze(x, y, z, w.b("grass_block", snowy=False))
                if rng.random() < 0.3:
                    w.setze(x, y + 1, z, w.b(["grass", "fern", "poppy", "dandelion"][int(rng.random() * 4)]))
    for k in range(1 + g):
        x, z = round((-2 + k * 3) * u), round((rng.random() - 0.5) * 3 * u)
        ytop = max((yy for (xx, yy, zz) in w.bloecke if xx == x and zz == z), default=0)
        einfuegen(w, wald2.birke(seed + k) if k % 2 else wald2.busch(seed + k), x, ytop, z)
    return w


def tempelkatze(seed, g=1):
    """Tempelkatze: eine schlanke, aufrecht sitzende Katze mit hohen Ohren, goldenem Halsband und Ohrring, den
    Schwanz um die Pfoten gelegt, auf einem Sandsteinsockel."""
    w = _welt(seed)
    u = U[g]
    haut = Verlauf(w, "Stein", ["deepslate", "polished_deepslate", "blackstone", "polished_blackstone"]) \
        if _stil(seed) else Verlauf(w, "Sand", ["sandstone", "smooth_sandstone", "cut_sandstone", "smooth_sandstone"])
    top = sockel(w, SOCKEL["sandstein"], _r(3 * u, 2) + 5, _r(3 * u, 2) + 5, [2, 2, 3, 4][g], _r(3 * u, 2),
                 _r(3 * u, 2), _r(2.5 * u, 2))
    S = skulptur(w, u, haut, 18)
    S.plus(ell(0, 4, -0.8, 2.4, 3.8, 3.0), "k")
    S.plus(kap((0, 6, 0.4), (0, 11, 1.2), 1.6, 1.3), "k")
    S.plus(ell(0, 12.4, 1.4, 1.8, 1.6, 1.7), "k")
    S.plus(kap((0, 12.0, 2.6), (0, 11.6, 3.6), 0.8, 0.6), "k")
    for sx in (-1, 1):
        S.plus(kap((sx * 1.0, 13.4, 1.0), (sx * 1.3, 15.8, 0.8), 0.7, 0.15), "k")
        S.plus(kap((sx * 0.9, 7, 2.0), (sx * 0.8, 0.5, 2.6), 0.6, 0.55), "k")
        S.plus(ell(sx * 0.7, 12.6, 2.8, 0.3, 0.25, 0.2), "a")
    S.plus(torus(0, 10.2, 1.0, 1.4, 0.35), "a")
    S.plus(ell(1.8, 12.0, 1.4, 0.35, 0.5, 0.35), "a")
    S.plus(und(torus(0, 0.5, 0.0, 3.0, 0.55), lambda X, Y, Z: Z > -0.5), "k")
    S.rendern((-5, 0, -5), (5, 17, 5), versatz=(0.5, top, 0.5))
    return w


def fuchs(seed, g=1):
    """Fuchsstatue: ein sitzender Fuchs mit spitzer Schnauze und großen Ohren, der buschige Schwanz legt sich in
    einem Bogen um ihn, kupferrot oder weiß in Marmor."""
    w = _welt(seed)
    u, haut, top = basis(w, seed, g, 3.4, 3.4, hs=2.0)
    if _stil(seed):
        haut = Verlauf(w, "Fuchs", ["red_terracotta", "orange_terracotta", "orange_concrete", "orange_terracotta"])
    S = skulptur(w, u, haut, 16)
    S.plus(ell(0, 3.6, -0.6, 2.2, 3.4, 2.8), "k")
    S.plus(kap((0, 5.6, 0.6), (0, 9.4, 1.4), 1.4, 1.2), "k")
    S.plus(ell(0, 10.4, 1.6, 1.8, 1.5, 1.6), "k")
    S.plus(kap((0, 10.0, 2.6), (0, 9.6, 5.0), 0.9, 0.3), "k")
    S.plus(ell(0, 9.6, 5.0, 0.35, 0.35, 0.35), "d")
    S.plus(ell(0, 7.6, 1.8, 1.1, 1.8, 0.9), "w")
    for sx in (-1, 1):
        S.plus(kap((sx * 1.0, 11.4, 1.2), (sx * 1.8, 14.0, 0.6), 0.8, 0.15), "k")
        S.plus(kap((sx * 0.8, 6, 1.6), (sx * 0.8, 0.4, 2.2), 0.5, 0.45), "k")
        S.plus(ell(sx * 0.8, 10.8, 2.8, 0.25, 0.25, 0.2), "d")
    S.plus(kap((0, 1.2, -3.0), (3.4, 1.0, -2.2), 1.3, 1.6), "k")
    S.plus(kap((3.4, 1.0, -2.2), (3.6, 1.0, 1.8), 1.6, 1.2), "k")
    S.plus(ell(3.4, 1.1, 2.6, 1.0, 0.9, 1.0), "w")
    S.rendern((-5, 0, -6), (6, 15, 6), versatz=(0.5, top, 0.5))
    return w


def runenkreis(seed, g=1):
    """Runenkreis: ein Ring hoher, unbehauener Standsteine mit leuchtenden Runenbändern umschließt einen Altarstein,
    auf dem ein Kristall schwebt, Moos und Farn zwischen den Steinen."""
    w = _welt(seed)
    u = U[g]
    rng = w.rng
    R = _r(8 * u + 4, 5)
    for x in range(-R - 3, R + 4):
        for z in range(-R - 3, R + 4):
            if math.hypot(x, z) <= R + 3:
                w.setze(x, 0, z, w.b("grass_block", snowy=False) if rng.random() < 0.8 else w.b("moss_block"))
                w.setze(x, -1, z, w.b("dirt"))
    n = 8 + g * 2
    for k in range(n):
        a = k / n * 6.283
        cx, cz = math.cos(a) * R, math.sin(a) * R
        H = int((5 + rng.random() * 3) * u + 3)
        b = max(1, int(1.2 * u))
        for y in range(1, H + 1):
            for dx in range(-b, b + 1):
                for dz in range(-b, b + 1):
                    if abs(dx) + abs(dz) <= b + (1 if y < H - 1 else 0):
                        x, z = round(cx + dx), round(cz + dz)
                        rune = y % 3 == 0 and (abs(dx) + abs(dz)) == b and rng.random() < 0.5
                        w.setze(x, y, z, w.b("crying_obsidian") if rune else
                                w.b(["stone", "andesite", "tuff", "mossy_cobblestone"][int(rng.random() * 4)]))
    for x in range(-2, 3):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("polished_deepslate"))
            w.setze(x, 2, z, w.b("deepslate_tiles") if abs(x) < 2 else w.b("polished_deepslate_slab", type="bottom",
                                                                            waterlogged=False))
    from kristall import kristall
    kristall(w, (0, 4 + u * 1.5, 0), (0, 1, 0), 3 * u + 1.5, 0.8 * u + 0.5, art="amethyst")
    for (x, y, z), b in list(w.bloecke.items()):
        if y == 0 and w.frei(x, 1, z) and rng.random() < 0.15:
            w.setze(x, 1, z, w.b("fern" if rng.random() < 0.5 else "grass"))
    return w


def arkane_monolithen(seed, g=1):
    """Arkane Monolithen: drei schwarze, glatte Obelisken schweben über einem Runenpflaster, jeder von leuchtenden
    Ringen umkreist, zwischen ihnen pulsiert ein Lichtkern."""
    w = _welt(seed)
    u = U[g]
    rng = w.rng
    R = _r(7 * u + 4, 5)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d <= R + 2:
                ring = abs(d - R) < 0.6 or abs(d - R * 0.5) < 0.5
                w.setze(x, 0, z, w.b("crying_obsidian") if ring and rng.random() < 0.6 else
                        w.b("polished_blackstone_bricks" if (x + z) % 3 else "chiseled_polished_blackstone"))
    for k in range(3):
        a = k / 3 * 6.283 + 0.5
        cx, cz = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        y0 = int(3 + 2 * u + k)
        H = int(9 * u + 5)
        for y in range(y0, y0 + H):
            t = (y - y0) / H
            b = 1 if t < 0.85 else 0
            for dx in range(-b, b + 1):
                for dz in range(-b, b + 1):
                    w.setze(cx + dx, y, cz + dz, w.b("obsidian") if (dx or dz) else w.b("polished_blackstone"))
        w.setze(cx, y0 + H, cz, w.b("end_rod", facing="up"))
        for j, (yr, rr) in enumerate(((y0 + H * 0.3, 2.6 * u + 1.5), (y0 + H * 0.65, 2.0 * u + 1.2))):
            for i in range(int(rr * 14)):
                aa = i / (rr * 14) * 6.283
                x, z = cx + math.cos(aa) * rr, cz + math.sin(aa) * rr
                y = yr + math.sin(aa) * (0.8 + j * 0.5)
                w.setze(round(x), round(y), round(z), w.b("purple_stained_glass" if i % 3 else "end_rod",
                                                          **({} if i % 3 else {"facing": "up"})))
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            for dz in range(-1, 2):
                if abs(dx) + abs(dy) + abs(dz) <= 1:
                    w.setze(dx, int(6 + 3 * u) + dy, dz, w.b("pearlescent_froglight", axis="y"))
    return w


STATUEN2 = {
    "laternentraeger": ("Laternenträger", laternentraeger),
    "eule": ("Eulenstatue", eule),
    "hirsch": ("Hirschstatue", hirsch),
    "wolf": ("Heulender Wolf", wolf),
    "baer": ("Bärenstatue", baer),
    "engel": ("Engelsstatue", engel),
    "moench": ("Meditierender Mönch", moench),
    "steinriese": ("Kniender Steinriese", steinriese),
    "wassertraegerin": ("Wasserträgerin", wassertraegerin),
    "bogenschuetzin": ("Bogenschützin", bogenschuetzin),
    "magier": ("Magierstatue", magier),
    "pferd": ("Aufbäumendes Pferd", pferd),
    "drachenkopfbrunnen": ("Drachenkopf-Brunnen", drachenkopfbrunnen),
    "phoenix": ("Phönix-Statue", phoenix),
    "weltenkugel": ("Weltenkugel in Händen", weltenkugel),
    "schlafender_riese": ("Schlafender Riese", schlafender_riese),
    "tempelkatze": ("Tempelkatze", tempelkatze),
    "fuchs": ("Fuchsstatue", fuchs),
    "runenkreis": ("Kristallaltar im Steinring", runenkreis),
    "arkane_monolithen": ("Obsidian-Obelisken mit Lichtringen", arkane_monolithen),
}

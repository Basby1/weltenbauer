"""Kreaturen – Erweiterung (inkl. Tiere): Hirsch, Bär, Wolf, Eule, Fuchs, Pferd/Pegasus, Elefant, Wal, Frosch,
Schnecke, Greif, Phönix, Einhorn, Minotaurus, Hydra, Riesenspinne, Yeti, Riesenkrabbe.
Alle schauen zur Vorschau-Kamera (Kopf +z), Boden bei y = 0."""

from __future__ import annotations

import math

import numpy as np

from kreaturen import SICHT, U, _stil, _welt, glied
from lib import Verlauf, ueberwuchern
from skulptur import Skulptur, dreh_y, ell, kap, kasten, kegel, scheibe, spiegel_x, torus, und


SEITE = dreh_y(math.pi / 4 - 1.05)   # Dreiviertelansicht für Vierbeiner


def _rendern(S, lo, hi, w, boden=-1, dreh=SICHT):
    S.rendern(lo, hi, versatz=(0.5, 0, 0.5), dreh=dreh)
    w.bloecke = {p: b for p, b in w.bloecke.items() if p[1] >= boden}


def fell(w, name, bloecke):
    return Verlauf(w, name, bloecke)


def bein(S, oben, knie, fuss, r, et, huf=None):
    glied(S, [oben, knie, fuss], [r, r * 0.75, r * 0.6], et)
    if huf:
        S.plus(ell(fuss[0], fuss[1] - 0.2, fuss[2] + 0.2, r * 0.75, r * 0.5, r * 0.85), huf)


def fluegel(S, sx, y0, z0, spann, hoehe, tiefe, et, kante=None, neig=0.0, schwung=0.4):
    """Flügel in der x-y-Ebene (bei z≈z0) mit gewelltem Hinterrand, sx = ±1."""
    def f(X, Y, Z):
        ax = X * sx
        t = np.clip((ax - 1.2) / (spann - 1.2), 0, 1)
        oben = y0 + hoehe * t ** 0.7 + neig * ax
        unten = oben - tiefe * (1 - 0.75 * t) + 0.9 * np.abs(np.sin(t * math.pi * 4.5))
        zz = z0 - schwung * spann * t ** 2
        return (ax >= 1.2) & (ax <= spann) & (Y <= oben) & (Y >= unten) & (np.abs(Z - zz) <= 0.55)
    S.plus(f, et)
    if kante:
        pts = [(sx * (1.2 + (spann - 1.2) * t), y0 + hoehe * t ** 0.7 + neig * sx * sx * (1.2 + (spann - 1.2) * t),
                z0 - schwung * spann * t ** 2) for t in np.linspace(0, 1, 6)]
        glied(S, pts, [0.7, 0.6, 0.5, 0.4, 0.3, 0.2], kante)


# ============================================================================ Tiere

def hirsch(seed, g=2):
    """Röhrender Hirsch mit gewaltigem Geweih, erhobenem Kopf und Mähne am Hals. Stil 2: weißer Zauberhirsch
    mit leuchtendem Geweih."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    if _stil(seed) == 0:
        S.mat("h", fell(w, "Hirsch", ["brown_terracotta", "brown_concrete", "light_gray_terracotta",
                                      "white_terracotta"]), basis=0.4, steigung=0.08, rausch=0.7)
        S.mat("m", w.b("brown_wool"))
        S.mat("g", fell(w, "Geweih", ["stripped_birch_log", "bone_block", "birch_planks"]), basis=0.5, rausch=1.5)
    else:
        S.mat("h", fell(w, "Weiß", ["light_gray_concrete", "white_terracotta", "white_concrete", "snow_block"]),
              basis=0.8, steigung=0.08, rausch=0.7)
        S.mat("m", w.b("white_wool"))
        S.mat("g", fell(w, "Lichtgeweih", ["sea_lantern", "glowstone", "shroomlight"]), basis=0.5, rausch=2)
    S.mat("d", w.b("black_concrete"))
    S.mat("f", w.b("blackstone"))
    S.plus(ell(0, 10, 0, 2.6, 2.9, 5.6), "h")
    S.plus(ell(0, 10.6, 3.2, 2.7, 3.2, 2.8), "h")
    for sx in (-1, 1):
        bein(S, (sx * 1.4, 9.5, 3.8), (sx * 1.4, 5.2, 4.3), (sx * 1.3, 0.8, 3.9), 1.0, "h", "f")
        bein(S, (sx * 1.4, 10, -4), (sx * 1.5, 5.6, -5.2), (sx * 1.4, 0.8, -4.4), 1.2, "h", "f")
    S.plus(kap((0, 11.5, 4.5), (0, 16.5, 7.0), 2.0, 1.3), "h")
    S.plus(kap((0, 12.5, 5.0), (0, 15.5, 6.4), 2.3, 1.6, zf=0.8), "m")
    S.plus(ell(0, 17.4, 7.9, 1.3, 1.4, 1.8), "h")
    S.plus(kap((0, 17.0, 8.5), (0, 16.4, 10.4), 0.9, 0.6), "h")
    S.plus(ell(0, 16.4, 10.6, 0.5, 0.45, 0.4), "d")
    S.plus(spiegel_x(ell(0.95, 17.8, 8.6, 0.25, 0.25, 0.25)), "d")
    S.plus(spiegel_x(kap((0.9, 18.3, 7.3), (2.1, 18.9, 6.6), 0.4, 0.15)), "h")
    S.plus(kap((0, 11, -5.2), (0, 10.4, -6.6), 0.7, 0.4), "m")
    for sx in (-1, 1):
        stange = [(sx * 0.7, 18.6, 7.6), (sx * 2.2, 21.5, 6.8), (sx * 3.6, 24.5, 5.5), (sx * 4.3, 27.5, 4.8),
                  (sx * 4.6, 29.5, 5.2)]
        glied(S, stange, [0.45, 0.42, 0.38, 0.32, 0.2], "g")
        for k, (px, py, pz) in enumerate(stange[1:4]):
            S.plus(kap((px, py, pz), (px + sx * 0.4, py + 2.2, pz + 1.6), 0.3, 0.12), "g")
            S.plus(kap((px, py, pz), (px + sx * 1.6, py + 1.4, pz - 0.6), 0.28, 0.1), "g")
    _rendern(S, (-7, -1, -8), (7, 31, 12), w, dreh=SEITE)
    return w


def baer(seed, g=2):
    """Aufgerichteter brüllender Bär mit erhobenen Pranken, Krallen, offenem Maul und zotteligem Fell.
    Stil 2: Eisbär."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    if _stil(seed) == 0:
        S.mat("h", fell(w, "Bär", ["brown_terracotta", "dark_oak_planks", "brown_concrete", "brown_wool",
                                   "spruce_planks"]), basis=0.6, steigung=0.1, rausch=1.4)
    else:
        S.mat("h", fell(w, "Eisbär", ["light_gray_wool", "white_terracotta", "white_wool", "snow_block"]),
              basis=0.6, steigung=0.1, rausch=1.2)
    S.mat("d", w.b("black_concrete"))
    S.mat("k", w.b("bone_block", axis="y"))
    S.mat("r", w.b("red_terracotta"))
    for sx in (-1, 1):
        glied(S, [(sx * 2.3, 7, -0.5), (sx * 2.6, 3.5, 1.2), (sx * 2.4, 1, 0.6)], [2.4, 2.0, 1.7], "h")
        S.plus(ell(sx * 2.4, 0.8, 1.8, 1.6, 0.8, 2.3), "h")
    S.plus(ell(0, 9, 0, 4.4, 4.8, 3.8), "h")
    S.plus(kap((0, 10, 0.2), (0, 16, 1.4), 4.2, 3.6), "h")
    S.plus(ell(0, 17, 1.6, 4.0, 2.6, 3.2), "h")
    S.plus(ell(0, 19.5, 3.4, 2.5, 2.3, 2.3), "h")
    S.plus(kap((0, 19.3, 4.6), (0, 19.0, 6.6), 1.4, 1.1), "h")
    S.plus(kasten(-0.9, 17.8, 5.0, 0.9, 18.5, 6.8), "r")
    S.plus(ell(0, 19.6, 7.0, 0.5, 0.45, 0.35), "d")
    S.plus(spiegel_x(ell(1.1, 20.4, 5.4, 0.3, 0.3, 0.25)), "d")
    S.plus(spiegel_x(ell(1.8, 21.6, 2.9, 0.75, 0.8, 0.5)), "h")
    for k in (-0.5, 0.5):
        S.plus(kap((k, 18.6, 6.2), (k, 18.0, 6.4), 0.2, 0.1), "k")
    for sx in (-1, 1):
        glied(S, [(sx * 3.8, 16.5, 1.2), (sx * 6.2, 18.5, 3.6), (sx * 6.0, 22.5, 5.0)], [1.8, 1.5, 1.3], "h")
        S.plus(ell(sx * 6.0, 23.2, 5.2, 1.5, 1.2, 1.3), "h")
        for d in (-0.8, 0, 0.8):
            S.plus(kap((sx * 6.0 + d, 23.6, 6.2), (sx * 6.0 + d * 1.2, 24.4, 7.4), 0.25, 0.08), "k")
    _rendern(S, (-9, -1, -6), (9, 27, 10), w)
    return w


def wolf(seed, g=2):
    """Heulender Wolf, auf einem Felsen sitzend, den Kopf zum Mond gereckt, mit buschiger Rute und dichtem
    Halskragen. Stil 2: schwarzer Schattenwolf mit glühenden Augen."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    if _stil(seed) == 0:
        S.mat("h", fell(w, "Wolf", ["gray_concrete", "gray_wool", "light_gray_concrete", "light_gray_wool",
                                    "white_wool"]), basis=0.6, steigung=0.12, rausch=1.2)
        S.mat("e", w.b("yellow_concrete"))
    else:
        S.mat("h", fell(w, "Schatten", ["black_concrete", "black_wool", "gray_concrete", "gray_wool"]),
              basis=0.3, steigung=0.08, rausch=1.0)
        S.mat("e", w.b("shroomlight"))
    S.mat("s", fell(w, "Fels", ["andesite", "stone", "cobblestone", "mossy_cobblestone"]), basis=0.5, rausch=2.5)
    S.mat("d", w.b("black_concrete"))
    S.plus(ell(0, 2.2, 0, 7, 3.4, 6.5), "s")
    S.plus(ell(0, 9, -1.5, 3.0, 3.6, 3.6), "h")
    S.plus(kap((0, 8, 0), (0, 13.5, 2.2), 3.0, 2.3), "h")
    S.plus(ell(0, 12.5, 2.4, 3.3, 2.6, 2.6), "h")
    for sx in (-1, 1):
        glied(S, [(sx * 1.6, 11, 2.6), (sx * 1.6, 8, 3.6), (sx * 1.5, 5.6, 3.8)], [1.0, 0.8, 0.7], "h")
        S.plus(ell(sx * 1.5, 5.6, 4.3, 0.8, 0.5, 1.0), "h")
        S.plus(ell(sx * 2.4, 7.6, -1.2, 1.4, 2.4, 2.6), "h")
        S.plus(ell(sx * 2.2, 5.6, 0.8, 0.8, 0.5, 1.6), "h")
    S.plus(kap((0, 14, 2.6), (0, 17.6, 3.6), 1.6, 1.3), "h")
    S.plus(ell(0, 18.4, 3.8, 1.6, 1.7, 1.5), "h")
    S.plus(kap((0, 19.0, 4.6), (0, 21.6, 6.6), 0.9, 0.55), "h")
    S.plus(ell(0, 21.7, 6.8, 0.4, 0.4, 0.35), "d")
    S.plus(spiegel_x(kap((0.9, 19.5, 2.9), (1.1, 21.4, 2.2), 0.55, 0.12)), "h")
    S.plus(spiegel_x(ell(0.85, 19.2, 4.9, 0.3, 0.25, 0.25)), "e")
    glied(S, [(0, 7.5, -4.6), (1.5, 5.8, -6.6), (3.6, 5.6, -6.2), (5.2, 6.4, -4.2)], [1.4, 1.5, 1.3, 0.7], "h")
    _rendern(S, (-8, -1, -9), (8, 24, 10), w)
    return w


def eule(seed, g=2):
    """Riesige Eule auf einem knorrigen Ast-Stumpf: gefleckte Brust, große runde Augen mit Federschleier,
    Federohren und halb ausgebreitete Schwingen. Stil 2: Schneeeule."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    if _stil(seed) == 0:
        S.mat("h", lambda x, y, z, lx, ly, lz: w.b(["brown_terracotta", "brown_wool", "spruce_planks"][
            int(abs(lx * 1.3 + ly * 0.7)) % 3]))
        S.mat("b", lambda x, y, z, lx, ly, lz: w.b("white_terracotta" if (int(ly * 1.5) + int(lx)) % 3 else
                                                   "brown_terracotta"))
        S.mat("e", w.b("orange_concrete"))
    else:
        S.mat("h", lambda x, y, z, lx, ly, lz: w.b("white_wool" if (int(lx * 2) + int(ly * 1.5)) % 4 else
                                                   "black_wool"))
        S.mat("b", lambda x, y, z, lx, ly, lz: w.b("white_concrete" if (int(ly * 2) + int(lx * 2)) % 5 else
                                                   "gray_wool"))
        S.mat("e", w.b("yellow_concrete"))
    S.mat("s", lambda x, y, z, lx, ly, lz: w.b("white_terracotta") if False else w.b("light_gray_terracotta"))
    S.mat("d", w.b("black_concrete"))
    S.mat("y", w.b("yellow_terracotta"))
    S.mat("t", fell(w, "Stumpf", ["dark_oak_log", "spruce_log", "dark_oak_log"]), basis=0.5, rausch=1.5)
    S.plus(kegel(0, 0, 0, 7, 3.6, 2.6), "t")
    for a in range(5):
        aa = a * 1.26
        S.plus(kap((0, 1, 0), (math.cos(aa) * 4.5, 0, math.sin(aa) * 4.5), 1.0, 0.5), "t")
    S.plus(ell(0, 12, 0, 4.2, 5.6, 3.8), "h")
    S.plus(ell(0, 11.5, 1.6, 3.4, 4.6, 2.6), "b")
    S.plus(ell(0, 18.3, 0.4, 3.7, 3.2, 3.4), "h")
    for sx in (-1, 1):
        S.plus(ell(sx * 1.45, 18.5, 3.0, 1.45, 1.45, 0.8), "s")
        S.plus(ell(sx * 1.45, 18.5, 3.5, 0.75, 0.75, 0.5), "e")
        S.plus(ell(sx * 1.45, 18.5, 3.85, 0.35, 0.35, 0.35), "d")
        S.plus(kap((sx * 2.5, 20.6, 0.8), (sx * 3.1, 23.3, 0.2), 0.7, 0.2), "h")
        fluegel(S, sx, 14.5, -0.6, 8.5, 2.2, 7.5, "h", schwung=0.25, neig=-0.2)
        for k in (-0.6, 0, 0.6):
            S.plus(kap((sx * 1.4 + k, 7.2, 1.2), (sx * 1.4 + k * 1.4, 6.8, 2.6), 0.3, 0.15), "y")
    S.plus(kap((0, 18.0, 3.6), (0, 16.8, 4.2), 0.45, 0.15), "y")
    S.plus(kap((0, 8, -2.6), (0, 4.5, -4.2), 2.0, 0.8, zf=0.5), "h")
    _rendern(S, (-11, -1, -8), (11, 25, 8), w)
    return w


def fuchs(seed, g=1):
    """Schlafender Fuchs, eingerollt auf einem Moospolster, die buschige Rute mit weißer Spitze über die Schnauze
    gelegt. Stil 2: Polarfuchs."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    if _stil(seed) == 0:
        S.mat("h", fell(w, "Fuchs", ["red_terracotta", "orange_terracotta", "orange_concrete", "orange_wool"]),
              basis=0.8, steigung=0.25, rausch=1.0)
    else:
        S.mat("h", fell(w, "Polarfuchs", ["light_gray_wool", "white_terracotta", "white_wool", "snow_block"]),
              basis=0.8, steigung=0.25, rausch=1.0)
    S.mat("w", w.b("white_wool"))
    S.mat("d", w.b("black_concrete"))
    S.mat("m", fell(w, "Moos", ["moss_block", "grass_block", "moss_block"]), basis=0.6, rausch=2)
    S.plus(kegel(0, 0, 0, 1.2, 7.5, 7.0), "m")
    S.plus(torus(0, 3.2, 0, 3.4, 2.6), "h")
    S.plus(ell(0, 3.4, 0, 4.2, 2.8, 4.2), "h")
    S.plus(ell(2.8, 3.6, 3.0, 1.9, 1.7, 1.9), "h")
    S.plus(kap((3.8, 3.3, 4.2), (4.0, 2.8, 5.8), 0.9, 0.5), "h")
    S.plus(ell(4.05, 2.8, 6.1, 0.35, 0.3, 0.3), "d")
    S.plus(ell(2.6, 2.7, 4.2, 1.2, 0.8, 1.2), "w")
    for dz in (-0.9, 0.9):
        S.plus(kap((2.3, 5.0, 2.8 + dz), (2.0, 6.3, 2.6 + dz), 0.5, 0.12), "h")
    pts = [(-3.5, 3.2, -2.5), (-4.6, 3.4, 1.0), (-3.0, 3.8, 4.5), (0.4, 4.2, 6.2), (3.0, 4.6, 6.6)]
    glied(S, pts[:4], [1.6, 1.9, 1.9, 1.7], "h")
    S.plus(kap(pts[3], pts[4], 1.7, 1.1), "w")
    _rendern(S, (-9, -1, -9), (9, 8, 9), w, dreh=SEITE)
    return w


def pferd(seed, g=2):
    """Aufbäumendes Pferd mit wehender Mähne und Schweif, Vorderhufe in der Luft. Stil 2: geflügelter Pegasus."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    if _stil(seed) == 0:
        S.mat("h", fell(w, "Rappe", ["brown_terracotta", "brown_concrete", "dark_oak_planks", "brown_wool"]),
              basis=0.5, steigung=0.08, rausch=1.0)
        S.mat("m", w.b("black_wool"))
        S.mat("f", w.b("white_concrete"))
    else:
        S.mat("h", fell(w, "Schimmel", ["light_gray_concrete", "white_terracotta", "white_concrete", "white_wool"]),
              basis=0.8, steigung=0.08, rausch=0.8)
        S.mat("m", fell(w, "Mähne", ["light_blue_wool", "white_wool", "light_blue_concrete"]), basis=0.4, rausch=2)
        S.mat("f", w.b("gold_block"))
        S.mat("w", lambda x, y, z, lx, ly, lz: w.b("white_wool" if (int(abs(lx) * 1.2) % 3) else
                                                   "light_gray_wool"))
    S.mat("d", w.b("black_concrete"))
    S.plus(kap((0, 7, -3.5), (0, 13, 3.2), 2.8, 2.5), "h")
    S.plus(ell(0, 7.3, -3.8, 2.9, 3.0, 3.0), "h")
    for sx in (-1, 1):
        bein(S, (sx * 1.5, 7, -4.2), (sx * 1.6, 3.8, -2.2), (sx * 1.5, 0.8, -3.6), 1.3, "h", "f")
    bein(S, (1.5, 12.4, 3.8), (1.6, 11.2, 7.0), (1.6, 8.0, 7.2), 1.0, "h", "f")
    bein(S, (-1.5, 12.4, 3.8), (-1.6, 13.2, 6.8), (-1.6, 10.6, 8.2), 1.0, "h", "f")
    S.plus(kap((0, 14, 3.6), (0, 19.0, 5.4), 1.9, 1.4), "h")
    S.plus(kap((0, 19.2, 5.6), (0, 18.2, 9.2), 1.4, 0.95), "h")
    S.plus(ell(0, 18.1, 9.4, 0.85, 0.8, 0.6), "d")
    S.plus(spiegel_x(kap((0.6, 20.2, 5.4), (0.8, 21.8, 5.0), 0.4, 0.1)), "h")
    S.plus(spiegel_x(ell(1.15, 19.4, 6.8, 0.25, 0.25, 0.25)), "d")
    for k in range(7):
        t = k / 6
        S.plus(kap((0, 20.0 - 6 * t, 4.8 - 2.0 * t), (0.3, 20.6 - 6 * t, 2.4 - 2.6 * t), 0.6, 0.25), "m")
    glied(S, [(0, 8.5, -6.0), (0, 7.0, -8.6), (0.8, 3.5, -9.8), (1.6, 1.6, -9.0)], [0.9, 1.0, 0.8, 0.4], "m")
    if _stil(seed) == 1:
        for sx in (-1, 1):
            fluegel(S, sx, 14.5, 1.0, 11, 7, 6.5, "w", kante="w", schwung=0.35)
    _rendern(S, (-13, -1, -12), (13, 23, 12), w, dreh=SEITE)
    return w


def elefant(seed, g=2):
    """Elefant mit erhobenem Rüssel, großen Ohren und Stoßzähnen. Stil 2: Kriegselefant mit Turm-Sänfte,
    Prunkdecke und Goldschmuck."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    S.mat("h", fell(w, "Elefant", ["gray_terracotta", "light_gray_terracotta", "tuff", "andesite"]), basis=0.5,
          steigung=0.06, rausch=1.2)
    S.mat("k", w.b("bone_block", axis="y"))
    S.mat("d", w.b("black_concrete"))
    S.mat("o", fell(w, "Ohr", ["light_gray_terracotta", "pink_terracotta", "light_gray_terracotta"]), basis=1,
          rausch=1)
    S.plus(ell(0, 11, 0, 5.2, 5.0, 7.5), "h")
    for sx in (-1, 1):
        for sz in (-1, 1):
            S.plus(kap((sx * 2.9, 9, sz * 4.2), (sx * 3.0, 0.8, sz * 4.4), 2.0, 1.8), "h")
            S.plus(ell(sx * 3.0, 0.7, sz * 4.4 + 0.3, 2.0, 0.7, 2.0), "k")
        S.plus(ell(sx * 4.6, 13.2, 6.6, 0.6, 4.2, 3.6), "o")
        S.plus(kap((sx * 1.5, 10.6, 9.8), (sx * 2.2, 8.2, 13.2), 0.6, 0.3), "k")
        S.plus(spiegel_x(ell(2.4, 14.6, 9.2, 0.35, 0.35, 0.3)), "d")
    S.plus(ell(0, 13.5, 8.0, 3.5, 3.8, 3.2), "h")
    glied(S, [(0, 12.5, 10.5), (0, 9.5, 12.5), (0, 9.5, 15.0), (0, 13.5, 16.4), (0, 16.6, 15.6)],
          [1.4, 1.2, 1.0, 0.8, 0.6], "h")
    S.plus(kap((0, 9.5, -7.3), (0.5, 4.5, -8.6), 0.4, 0.3), "h")
    if _stil(seed) == 1:
        S.mat("p", lambda x, y, z, lx, ly, lz: w.b("red_wool" if (int(lz) + int(ly)) % 4 else "yellow_wool"))
        S.mat("g", w.b("gold_block"))
        S.mat("t", fell(w, "Turm", ["dark_oak_planks", "stripped_dark_oak_log", "dark_oak_planks"]), basis=1)
        S.plus(und(ell(0, 11, 0, 5.5, 5.3, 6.0), lambda X, Y, Z: (Y > 10) & (Y < 15.6)), "p")
        S.plus(kasten(-3.2, 16, -3.2, 3.2, 20, 3.2), "t")
        S.plus(lambda X, Y, Z: (np.abs(X) < 2.6) & (np.abs(Z) < 2.6) & (Y > 16.5) & (Y < 20.5), None)
        S.plus(kegel(0, 0, 20, 24, 4.2, 0.5), "p")
        S.plus(ell(0, 15.8, 8.4, 3.6, 1.0, 3.0), "g")
    _rendern(S, (-8, -1, -10), (8, 25, 18), w, dreh=SEITE)
    return w


def wal(seed, g=2):
    """Springender Wal, der aus dem Meer bricht, mit Gischtkranz, Brustflossen und gefurchter Kehle.
    Stil 2: Orca. Wasserlinie bei y = 0."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    if _stil(seed) == 0:
        S.mat("h", fell(w, "Buckelwal", ["blue_terracotta", "gray_terracotta", "cyan_terracotta",
                                         "light_gray_terracotta"]), basis=0.6, steigung=0.04, rausch=1.0)
        S.mat("b", lambda x, y, z, lx, ly, lz: w.b("white_terracotta" if int(lx * 2) % 2 else
                                                   "light_gray_terracotta"))
    else:
        S.mat("h", w.b("black_concrete"))
        S.mat("b", w.b("white_concrete"))
    S.mat("s", fell(w, "Gischt", ["white_concrete", "white_wool", "snow_block", "light_blue_wool"]), basis=1,
          rausch=3)
    S.mat("d", w.b("black_wool"))
    pts = [(0, -4, -8), (0, 2, -3), (0, 9, 2), (0, 16, 5.5), (0, 21, 7)]
    glied(S, pts, [3.0, 4.6, 5.0, 4.4, 3.0], "h")
    S.plus(und(kap((0, 2, -3), (0, 16, 5.5), 4.8, 4.5), lambda X, Y, Z: Z - (Y * 0.42) > 2.6), "b")
    for sx in (-1, 1):
        S.plus(kap((sx * 3.8, 11, 3.2), (sx * 9, 8.5, 1.5), 1.1, 0.4, zf=0.5), "h" if _stil(seed) == 0 else "b")
        S.plus(ell(sx * 2.4, 17.5, 8.3, 0.4, 0.4, 0.4), "d")
        if _stil(seed) == 1:
            S.plus(ell(sx * 2.8, 18.6, 7.4, 0.5, 1.2, 1.4), "b")
    if _stil(seed) == 1:
        S.plus(kap((0, 11, -0.8), (0, 16, -4.5), 1.0, 0.2, zf=0.5), "h")
    for k in range(14):
        a = k / 14 * 2 * math.pi
        S.plus(kap((math.cos(a) * 5.5, 0, math.sin(a) * 5.5 - 3), (math.cos(a) * 8.5, 2.5 + (k % 3), math.sin(a) *
                                                                  8.5 - 3), 1.0, 0.3), "s")
    S.plus(ell(0, 0, -3, 9, 0.8, 9), "s")
    _rendern(S, (-11, -5, -13), (11, 25, 11), w, boden=-3, dreh=SEITE)
    return w


def frosch(seed, g=1):
    """Froschkönig: ein riesiger Frosch mit goldener Krone sitzt auf einem Seerosenblatt in einem Teich, mit
    Schilf, Blüten und glänzenden Augen."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    if _stil(seed) == 0:
        S.mat("h", fell(w, "Frosch", ["green_terracotta", "green_concrete", "lime_terracotta", "lime_concrete"]),
              basis=0.4, steigung=0.2, rausch=1.2)
    else:
        S.mat("h", lambda x, y, z, lx, ly, lz: w.b("blue_concrete" if (int(lx * 1.3) + int(lz * 1.1) +
                                                                       int(ly)) % 3 else "black_concrete"))
    S.mat("b", w.b("yellow_terracotta"))
    S.mat("e", w.b("yellow_concrete"))
    S.mat("d", w.b("black_concrete"))
    S.mat("g", w.b("gold_block"))
    S.mat("l", fell(w, "Seerose", ["green_concrete", "lime_concrete", "green_terracotta"]), basis=1, rausch=2)
    S.mat("wa", w.b("water", level=0))
    S.plus(kegel(0, 0, -1, 0.0, 9.5, 9.5), "wa")
    S.plus(und(kegel(0, 0, 0.0, 0.8, 7.5, 7.5), lambda X, Y, Z: ~((X > 0) & (np.abs(Z) < X * 0.25))), "l")
    S.plus(ell(0, 4.2, -0.5, 3.6, 3.2, 4.0), "h")
    S.plus(ell(0, 3.8, 1.0, 3.0, 2.3, 3.0), "b")
    S.plus(ell(0, 6.6, 2.0, 3.4, 2.0, 2.8), "h")
    for sx in (-1, 1):
        S.plus(ell(sx * 1.6, 8.2, 2.6, 1.1, 1.1, 1.1), "h")
        S.plus(ell(sx * 1.7, 8.4, 3.4, 0.6, 0.6, 0.4), "e")
        S.plus(ell(sx * 1.75, 8.4, 3.75, 0.3, 0.45, 0.2), "d")
        S.plus(ell(sx * 3.4, 2.4, -1.5, 1.8, 2.0, 2.8), "h")
        S.plus(ell(sx * 3.8, 1.0, 1.2, 1.0, 0.5, 2.0), "h")
        glied(S, [(sx * 2.2, 4.5, 2.5), (sx * 2.8, 2.4, 3.6), (sx * 2.6, 1.0, 4.4)], [0.8, 0.6, 0.5], "h")
    S.plus(kap((-2.4, 5.6, 4.2), (2.4, 5.6, 4.2), 0.25), "d")
    S.plus(und(kegel(0, 2.0, 8.6, 10.2, 1.5, 1.7),
               lambda X, Y, Z: ~((Y > 9.4) & (np.sin(np.arctan2(Z - 2.0, X) * 5) < 0))), "g")
    _rendern(S, (-11, -2, -11), (11, 11, 11), w, boden=-1)
    for k in range(10):
        a = k / 10 * 2 * math.pi
        x, z = round(math.cos(a) * 8.5 * u), round(math.sin(a) * 8.5 * u)
        for y in range(0, 2 + k % 3):
            w.setze(x, y, z, w.b("sugar_cane", age=0) if y else w.b("dirt"), ueberschreiben=False)
    return w


def schnecke(seed, g=1):
    """Riesenschnecke mit spiralig gestreiftem Haus, Fühlern mit Augen und glänzender Schleimspur; im Haus
    ein kleines Fenster mit Licht."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    if _stil(seed) == 0:
        haus = ["brown_terracotta", "orange_terracotta", "yellow_terracotta", "white_terracotta"]
        S.mat("h", fell(w, "Körper", ["light_gray_terracotta", "white_terracotta", "pink_terracotta"]), basis=0.8,
              rausch=1)
    else:
        haus = ["purple_terracotta", "magenta_terracotta", "pink_terracotta", "white_terracotta"]
        S.mat("h", fell(w, "Körper", ["cyan_terracotta", "light_blue_terracotta", "white_terracotta"]), basis=0.8,
              rausch=1)
    S.mat("s", lambda x, y, z, lx, ly, lz: w.b(haus[int((math.atan2(ly - 7, lz + 1) / math.pi + 1) * 6 +
                                                       math.hypot(ly - 7, lz + 1) * 0.6) % 4]))
    S.mat("d", w.b("black_concrete"))
    S.mat("g", w.b("slime_block"))
    S.mat("l", w.b("shroomlight"))
    S.plus(kap((0, 1.4, -6), (0, 1.6, 7), 2.2, 2.0, zf=1.0), "h")
    S.plus(kap((0, 1.6, 6), (0, 5.5, 9), 1.6, 1.3), "h")
    for sx in (-1, 1):
        S.plus(kap((sx * 0.6, 6.2, 9.0), (sx * 1.6, 10.0, 10.4), 0.3, 0.2), "h")
        S.plus(ell(sx * 1.6, 10.2, 10.5, 0.5, 0.5, 0.5), "d")
    for k in range(120):
        t = k / 119
        a = t * 2.6 * 2 * math.pi
        rr = 6.5 * (1 - t) ** 0.9 + 0.6
        cy, cz = 7 + math.sin(a) * rr * 0.9, -1 + math.cos(a) * rr * 0.9
        S.plus(ell(0.8 * t, cy, cz, 2.8 * (1 - t) + 0.6, 2.3 * (1 - t) + 0.5, 2.3 * (1 - t) + 0.5), "s")
    S.plus(ell(3.0, 7, -1, 0.4, 1.0, 1.0), "l")
    S.plus(kegel(0, -12, 0, 0.5, 1.6, 1.0), "g")
    S.plus(kap((0, 0.2, -6), (0, 0.2, -15), 1.6, 1.0), "g")
    _rendern(S, (-7, -1, -16), (7, 16, 12), w, dreh=SEITE)
    return w


# ============================================================================ Fabelwesen

def greif(seed, g=2):
    """Greif: Löwenkörper mit Adlerkopf, Krummschnabel und gewaltigen erhobenen Schwingen, auf einem Felsen
    sitzend, eine Vorderklaue erhoben."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    S.mat("h", fell(w, "Löwe", ["orange_terracotta", "yellow_terracotta", "sandstone", "smooth_sandstone"]),
          basis=0.4, steigung=0.08, rausch=1.2)
    S.mat("f", lambda x, y, z, lx, ly, lz: w.b(["white_wool", "white_terracotta", "light_gray_wool"][
        int(abs(lx) + ly * 0.5) % 3]) if _stil(seed) == 0 else w.b(["brown_wool", "brown_terracotta",
                                                                     "white_terracotta"][int(abs(lx) + ly * 0.5) % 3]))
    S.mat("w", lambda x, y, z, lx, ly, lz: w.b(["brown_terracotta", "brown_wool", "white_terracotta",
                                                "yellow_terracotta"][int(abs(lx) * 0.9 + ly * 0.4) % 4]))
    S.mat("y", w.b("yellow_concrete"))
    S.mat("d", w.b("black_concrete"))
    S.mat("s", fell(w, "Fels", ["andesite", "stone", "cobblestone", "tuff"]), basis=0.5, rausch=2.5)
    S.plus(ell(0, 2.4, -1, 7.5, 3.6, 8.0), "s")
    S.plus(ell(0, 9.5, -3.6, 3.2, 3.2, 3.6), "h")
    S.plus(kap((0, 9.5, -3), (0, 12.5, 2.6), 3.0, 2.8), "h")
    for sx in (-1, 1):
        S.plus(ell(sx * 2.5, 8.2, -3.8, 1.6, 2.4, 3.0), "h")
        S.plus(ell(sx * 2.4, 6.3, -1.4, 1.0, 0.6, 2.0), "h")
    glied(S, [(1.6, 11.5, 3.0), (1.7, 8.4, 4.2), (1.6, 6.4, 4.6)], [1.1, 0.9, 0.8], "f")
    glied(S, [(-1.6, 11.5, 3.0), (-1.8, 11.0, 6.0), (-1.8, 13.0, 7.2)], [1.1, 0.9, 0.8], "f")
    for k in (-0.5, 0, 0.5):
        S.plus(kap((-1.8 + k, 13.3, 7.4), (-1.8 + k * 1.4, 14.2, 8.2), 0.25, 0.08), "y")
    S.plus(kap((0, 13, 2.6), (0, 17, 4.0), 2.2, 1.7), "f")
    S.plus(ell(0, 18.0, 4.3, 1.9, 1.9, 2.1), "f")
    S.plus(kap((0, 18.4, 6.0), (0, 16.6, 7.8), 0.8, 0.2), "y")
    S.plus(spiegel_x(ell(1.2, 18.7, 5.4, 0.3, 0.3, 0.25)), "d")
    S.plus(spiegel_x(kap((0.9, 19.6, 3.6), (1.4, 20.6, 2.0), 0.5, 0.1)), "f")
    for sx in (-1, 1):
        fluegel(S, sx, 13, -1.0, 11, 12, 9.5, "w", kante="f", schwung=0.3)
    glied(S, [(0, 8.5, -7), (2, 4.5, -9), (4.5, 5.0, -9.5), (5.6, 6.6, -8.4)], [0.6, 0.55, 0.5, 0.9], "h")
    _rendern(S, (-12, -1, -11), (12, 27, 10), w)
    return w


def phoenix(seed, g=2):
    """Phönix: ein Feuervogel steigt mit weit ausgebreiteten Flammenschwingen und langen Schweiffedern aus einem
    glühenden Scheiterhaufen auf. Stil 2: blauer Seelenphönix."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    if _stil(seed) == 0:
        glut = ["red_concrete", "orange_concrete", "orange_terracotta", "yellow_concrete", "shroomlight"]
        feuer = "fire"
    else:
        glut = ["blue_concrete", "cyan_concrete", "light_blue_concrete", "sea_lantern", "white_concrete"]
        feuer = "soul_fire"
    S.mat("h", fell(w, "Glut", glut), basis=0.4, steigung=0.12, rausch=1.4)
    S.mat("w", lambda x, y, z, lx, ly, lz: w.b(glut[min(4, int(abs(lx) / 3.2 + (ly - 12) / 6))]))
    S.mat("y", w.b("gold_block"))
    S.mat("d", w.b("black_concrete"))
    S.mat("t", fell(w, "Holz", ["dark_oak_log", "stripped_dark_oak_log", "magma_block", "dark_oak_log"]), basis=0.5,
          rausch=2.5)
    S.plus(kegel(0, 0, 0, 3.2, 5.2, 3.6), "t")
    for k in range(8):
        a = k / 8 * math.pi
        S.plus(kap((math.cos(a) * 5, 0.6, math.sin(a) * 5), (-math.cos(a) * 5, 2.6, -math.sin(a) * 5), 0.6), "t")
    S.plus(ell(0, 13, 0, 2.4, 3.6, 2.4), "h")
    S.plus(kap((0, 15, 0.4), (0, 18.5, 1.6), 1.4, 1.0), "h")
    S.plus(ell(0, 19.4, 2.0, 1.4, 1.3, 1.5), "h")
    S.plus(kap((0, 19.5, 3.2), (0, 18.8, 4.6), 0.5, 0.15), "y")
    S.plus(spiegel_x(ell(0.75, 19.8, 2.9, 0.25, 0.25, 0.25)), "d")
    for k in range(5):
        S.plus(kap((0, 20.4, 1.8), ((k - 2) * 0.6, 23 + (2 - abs(k - 2)) * 0.8, 0.2), 0.3, 0.1), "w")
    for sx in (-1, 1):
        fluegel(S, sx, 15, 0.0, 15, 10, 9.5, "w", kante="h", schwung=0.15, neig=0.0)
    for k in range(5):
        a = (k - 2) * 0.25
        glied(S, [(0, 10, -1.5), (math.sin(a) * 3, 6.5, -4.5), (math.sin(a) * 6, 4.8, -7.5 - k % 2),
                  (math.sin(a) * 8, 5.4, -10)], [0.9, 0.7, 0.5, 0.3], "w")
    _rendern(S, (-16, -1, -12), (16, 27, 7), w)
    for i in range(int(14 * u)):
        a = w.rng.random() * 2 * math.pi
        d = w.rng.random() * 4 * u
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = max([p[1] for p in w.bloecke if p[0] == x and p[2] == z and p[1] < 4 * u] + [0]) + 1
        if (x, y, z) not in w.bloecke:
            w.setze(x, y, z, w.b(feuer) if feuer == "soul_fire" else w.b(feuer, age=0, north=False, south=False,
                                                                          east=False, west=False, up=False))
    return w


def einhorn(seed, g=2):
    """Einhorn mit spiralig gedrehtem Horn, stolz erhobenem Kopf, wallender Mähne und Federn an den Hufen,
    auf einer Blumenwiese. Stil 2: Regenbogenmähne."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    S.mat("h", fell(w, "Einhorn", ["light_gray_concrete", "white_terracotta", "white_concrete", "white_wool"]),
          basis=1.0, steigung=0.06, rausch=0.8)
    if _stil(seed) == 0:
        S.mat("m", fell(w, "Mähne", ["light_blue_wool", "white_wool", "pink_wool", "white_wool"]), basis=0.5,
              rausch=2.5)
    else:
        S.mat("m", lambda x, y, z, lx, ly, lz: w.b(["red_wool", "orange_wool", "yellow_wool", "lime_wool",
                                                    "light_blue_wool", "purple_wool"][int(ly * 0.9 + lz * 0.3) % 6]))
    S.mat("g", lambda x, y, z, lx, ly, lz: w.b("gold_block" if int(ly * 2.5 + lz * 1.0) % 2 else
                                               "yellow_concrete"))
    S.mat("d", w.b("black_concrete"))
    S.mat("f", w.b("gold_block"))
    S.plus(ell(0, 9.5, 0, 2.6, 2.8, 5.4), "h")
    for sx in (-1, 1):
        bein(S, (sx * 1.4, 9, 3.6), (sx * 1.4, 5, 4.3), (sx * 1.3, 0.8, 4.2), 1.0, "h", "f")
        bein(S, (sx * 1.4, 9.5, -3.8), (sx * 1.5, 5.4, -5.0), (sx * 1.4, 0.8, -4.2), 1.15, "h", "f")
        for sz in (4.1, -4.3):
            S.plus(ell(sx * 1.4, 1.9, sz, 0.95, 0.8, 0.95), "m")
    S.plus(kap((0, 11, 4.3), (0, 16.5, 6.4), 1.9, 1.3), "h")
    S.plus(kap((0, 16.8, 6.6), (0, 15.6, 10.0), 1.4, 0.9), "h")
    S.plus(ell(0, 15.4, 10.2, 0.8, 0.75, 0.55), "h")
    S.plus(spiegel_x(ell(1.15, 17.0, 7.8, 0.3, 0.3, 0.3)), "d")
    S.plus(spiegel_x(kap((0.6, 17.8, 6.6), (0.8, 19.2, 6.2), 0.4, 0.1)), "h")
    S.plus(kap((0, 17.6, 8.0), (0, 22.6, 10.2), 0.55, 0.08), "g")
    for k in range(8):
        t = k / 7
        S.plus(kap((0, 18.0 - 6 * t, 5.6 - 2.2 * t), (0.6 * (k % 2 * 2 - 1), 17 - 7 * t, 3.4 - 2.6 * t), 0.7,
                   0.3), "m")
    glied(S, [(0, 10, -5.2), (0, 9.0, -8.0), (0.6, 5.0, -9.2), (1.2, 2.4, -8.2)], [0.8, 1.1, 0.9, 0.5], "m")
    _rendern(S, (-6, -1, -11), (6, 24, 12), w, dreh=SEITE)
    bl = ["poppy", "dandelion", "azure_bluet", "oxeye_daisy", "cornflower", "allium", "pink_tulip"]
    R = int(10 * u)
    for x, z in scheibe(R):
        if (x, 0, z) not in w.bloecke:
            w.setze(x, -1, z, w.b("grass_block", snowy=False))
            if w.rng.random() < 0.3:
                w.setze(x, 0, z, w.b(bl[int(w.rng.integers(len(bl)))]))
    return w


def minotaurus(seed, g=2):
    """Minotaurus: muskulöser Stiermensch mit gewaltigen Hörnern, Nasenring, Lendenschurz und doppelschneidiger
    Axt, breitbeinig auf einem Labyrinth-Pflaster."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    S.mat("h", fell(w, "Stier", ["brown_terracotta", "dark_oak_planks", "brown_concrete", "brown_wool"]) if
          _stil(seed) == 0 else fell(w, "Schwarzstier", ["black_concrete", "black_terracotta", "gray_concrete",
                                                         "black_wool"]), basis=0.6, steigung=0.08, rausch=1.2)
    S.mat("k", w.b("bone_block", axis="y"))
    S.mat("g", w.b("gold_block"))
    S.mat("i", w.b("iron_block"))
    S.mat("l", w.b("red_wool"))
    S.mat("e", w.b("redstone_block"))
    S.mat("w", w.b("stripped_dark_oak_log", axis="y"))
    S.mat("p", lambda x, y, z, lx, ly, lz: w.b("smooth_stone" if (int(lx + 20) // 2 + int(lz + 20) // 2) % 2 else
                                               "stone_bricks"))
    S.plus(kasten(-8, -0.6, -8, 8, 0.4, 8), "p")
    for sx in (-1, 1):
        glied(S, [(sx * 2.2, 9, 0), (sx * 3.2, 5, 1.0), (sx * 3.4, 1.6, -0.2)], [1.9, 1.5, 1.2], "h")
        S.plus(ell(sx * 3.4, 1.0, 0.2, 1.3, 1.0, 1.6), "k")
    S.plus(ell(0, 10, 0, 3.6, 2.4, 2.6), "h")
    S.plus(kap((0, 10.5, 0), (0, 16, 0.6), 3.4, 4.6), "h")
    S.plus(ell(0, 17, 0.4, 5.5, 2.0, 3.0), "h")
    S.plus(und(kap((0, 10.2, 0), (0, 10.8, 0), 3.8), lambda X, Y, Z: Y > 9.8), "l")
    S.plus(lambda X, Y, Z: (np.abs(X) < 1.6) & (Y > 5.5) & (Y < 10) & (np.abs(Z - 2.4) < 0.4), "l")
    S.plus(ell(0, 19.5, 2.0, 2.4, 2.6, 2.5), "h")
    S.plus(kap((0, 19.3, 3.4), (0, 18.8, 5.6), 1.6, 1.4), "h")
    S.plus(torus(0, 17.8, 5.7, 0.7, 0.18, achse="x"), "g")
    S.plus(spiegel_x(ell(1.2, 20.6, 3.9, 0.3, 0.3, 0.25)), "e")
    S.plus(spiegel_x(kap((2.0, 21.0, 2.2), (4.6, 22.2, 2.6), 0.7, 0.4)), "k")
    S.plus(spiegel_x(kap((4.6, 22.2, 2.6), (5.0, 25.0, 3.6), 0.4, 0.1)), "k")
    glied(S, [(-4.8, 16.5, 0.4), (-6.0, 12.5, 1.6), (-5.6, 9.0, 3.0)], [1.6, 1.4, 1.2], "h")
    glied(S, [(4.8, 16.5, 0.4), (6.8, 14.0, 2.6), (6.4, 17.5, 4.2)], [1.6, 1.4, 1.2], "h")
    S.plus(ell(6.4, 17.8, 4.4, 1.2, 1.2, 1.2), "h")
    S.plus(kap((6.4, 12.0, 4.8), (6.4, 28.0, 3.4), 0.45), "w")
    S.plus(und(ell(6.4, 26.2, 3.6, 3.6, 2.3, 0.4), lambda X, Y, Z: np.abs(X - 6.4) > 0.5), "i")
    _rendern(S, (-9, -1, -9), (11, 30, 9), w)
    return w


def hydra(seed, g=2):
    """Hydra: ein schuppiger Leib in einem Sumpftümpel, aus dem fünf lange Hälse mit fauchenden Köpfen in alle
    Richtungen ragen."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    if _stil(seed) == 0:
        S.mat("h", fell(w, "Hydra", ["green_terracotta", "moss_block", "green_concrete", "lime_terracotta"]),
              basis=0.3, steigung=0.12, rausch=1.2)
        S.mat("b", w.b("yellow_terracotta"))
    else:
        S.mat("h", fell(w, "Hydra", ["purple_terracotta", "magenta_terracotta", "purple_concrete",
                                     "pink_terracotta"]), basis=0.3, steigung=0.12, rausch=1.2)
        S.mat("b", w.b("white_terracotta"))
    S.mat("e", w.b("yellow_concrete"))
    S.mat("k", w.b("bone_block", axis="y"))
    S.mat("r", w.b("red_terracotta"))
    S.mat("wa", w.b("water", level=0))
    S.mat("m", fell(w, "Sumpf", ["mud", "mud", "muddy_mangrove_roots", "moss_block"]), basis=1, rausch=2)
    S.plus(kegel(0, 0, -1.5, 0.0, 12, 12), "m")
    S.plus(kegel(0, 0, -0.6, 0.0, 8.5, 8.5), "wa")
    S.plus(ell(0, 3, -1, 6.0, 4.5, 6.5), "h")
    for i in range(5):
        a = -math.pi * 0.85 + i / 4 * math.pi * 0.7 + math.pi / 2
        hoch = 15 + 4 * (i % 2) + (2 if i == 2 else 0)
        dx, dz = math.cos(a), math.sin(a)
        pts = [(dx * 2, 5, dz * 2 - 1), (dx * 5, 9, dz * 5), (dx * 6, 12.5 + (i % 2), dz * 7), (dx * 5,
                                                                                                hoch, dz * 8.5)]
        glied(S, pts, [1.8, 1.5, 1.2, 1.0], "h")
        hx, hy, hz = dx * 5 + dx * 1.5, hoch + 0.6, dz * 8.5 + dz * 1.5
        S.plus(ell(hx, hy, hz, 1.4, 1.1, 1.4), "h")
        S.plus(kap((hx, hy, hz), (hx + dx * 2.2, hy - 0.2, hz + dz * 2.2), 0.9, 0.6), "h")
        S.plus(kap((hx, hy - 0.8, hz), (hx + dx * 2.2, hy - 1.6, hz + dz * 2.2), 0.6, 0.4), "b")
        S.plus(ell(hx + dx * 1.2, hy - 0.6, hz + dz * 1.2, 0.6, 0.35, 0.6), "r")
        S.plus(ell(hx - dz * 0.8, hy + 0.6, hz + dx * 0.8, 0.3, 0.3, 0.3), "e")
        S.plus(ell(hx + dz * 0.8, hy + 0.6, hz - dx * 0.8, 0.3, 0.3, 0.3), "e")
        S.plus(kap((hx - dx * 0.6, hy + 0.8, hz - dz * 0.6), (hx - dx * 2.0, hy + 2.2, hz - dz * 2.0), 0.3, 0.08),
               "k")
    glied(S, [(0, 2.5, -6.5), (2, 1.5, -10), (5, 1.0, -11)], [2.0, 1.2, 0.5], "h")
    _rendern(S, (-13, -2, -13), (13, 25, 13), w, boden=-2)
    return w


def riesenspinne(seed, g=2):
    """Riesenspinne in ihrem Netz zwischen zwei toten Bäumen: behaarter Hinterleib mit Muster, acht geknickte
    Beine, rot glühende Augenreihe, eingesponnene Beute."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    S.mat("h", fell(w, "Spinne", ["black_concrete", "black_wool", "gray_wool", "brown_wool"]), basis=0.5, rausch=1.5)
    S.mat("p", w.b("red_concrete") if _stil(seed) == 0 else w.b("lime_concrete"))
    S.mat("e", w.b("redstone_block") if _stil(seed) == 0 else w.b("verdant_froglight", axis="y"))
    S.mat("t", fell(w, "Totholz", ["dark_oak_log", "spruce_log", "stripped_dark_oak_log"]), basis=0.5, rausch=2)
    S.mat("c", w.b("white_wool"))
    for sx in (-1, 1):
        S.plus(kegel(sx * 12, -2, 0, 22, 1.4, 0.8), "t")
        S.plus(kap((sx * 12, 14, -2), (sx * 8, 18, -2), 0.6, 0.3), "t")
    S.plus(ell(0, 9, -3.5, 4.2, 4.0, 4.8), "h")
    S.plus(und(ell(0, 9, -3.5, 4.3, 4.1, 4.9), lambda X, Y, Z: (np.abs(X) < 0.8) & (Y > 10) |
               ((np.abs(Y - 11) < 0.7) & (np.abs(X) < 2.6) & (Z < -2.5))), "p")
    S.plus(ell(0, 8, 2.0, 2.6, 2.2, 2.4), "h")
    for k in range(4):
        S.plus(ell((k - 1.5) * 0.8, 9.0 + (k % 2) * 0.3, 4.1, 0.35, 0.35, 0.3), "e")
    for sx in (-1, 1):
        for i in range(4):
            a = 0.7 - i * 0.48
            bx, bz = sx * 2.0, 2.0 - i * 0.9
            knie = (sx * (6 + i * 0.4), 13 - i * 0.6, bz + math.sin(a) * 5)
            fuss = (sx * (9 + i * 0.6), 0.4 + i * 0.2, bz + math.sin(a) * 9)
            glied(S, [(bx, 8, bz), knie, fuss], [0.6, 0.5, 0.25], "h")
        S.plus(kap((sx * 0.6, 7, 4.0), (sx * 0.5, 5.6, 4.8), 0.35, 0.15), "h")
    S.plus(ell(-7, 6, -1.5, 1.2, 2.0, 1.2), "c")
    _rendern(S, (-14, -1, -8), (14, 23, 12), w)
    for k in range(10):
        a = k / 10 * math.pi * 2
        for d in range(1, int(11 * u)):
            x, y = round(math.cos(a) * d), round(11 * u + math.sin(a) * d)
            if 0 < y and abs(x) < 12 * u:
                w.setze(x, y, round(-5 * u), w.b("cobweb"), ueberschreiben=False)
    for r in (3, 6, 9):
        for k in range(int(r * 6)):
            a = k / (r * 6) * 2 * math.pi
            x, y = round(math.cos(a) * r * u), round(11 * u + math.sin(a) * r * u)
            if 0 < y and abs(x) < 12 * u:
                w.setze(x, y, round(-5 * u), w.b("cobweb"), ueberschreiben=False)
    return w


def yeti(seed, g=2):
    """Yeti: ein zotteliger Schneeriese mit langen Armen, der einen Eisbrocken über den Kopf stemmt, auf einem
    verschneiten Felsen mit Eiszapfen."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    S.mat("h", fell(w, "Yeti", ["light_gray_wool", "white_terracotta", "white_wool", "snow_block"]), basis=0.8,
          steigung=0.08, rausch=1.6)
    S.mat("g", fell(w, "Gesicht", ["light_blue_terracotta", "cyan_terracotta", "light_blue_terracotta"]), basis=1)
    S.mat("d", w.b("black_concrete"))
    S.mat("k", w.b("bone_block", axis="y"))
    S.mat("i", fell(w, "Eis", ["packed_ice", "blue_ice", "ice", "packed_ice"]), basis=1, rausch=2.5)
    S.mat("s", fell(w, "Fels", ["andesite", "stone", "calcite", "snow_block"]), basis=0.5, steigung=0.6, rausch=2)
    S.plus(ell(0, 1.5, 0, 7.5, 3.0, 6.5), "s")
    for sx in (-1, 1):
        glied(S, [(sx * 2.4, 9.5, 0), (sx * 3.2, 6, 1.4), (sx * 3.0, 3.6, 0.4)], [2.2, 1.8, 1.5], "h")
        S.plus(ell(sx * 3.0, 3.5, 1.2, 1.6, 0.8, 2.2), "h")
    S.plus(ell(0, 11, 0, 4.4, 3.0, 3.4), "h")
    S.plus(kap((0, 11, -0.2), (0, 17.5, -0.6), 4.2, 5.0), "h")
    S.plus(ell(0, 20, 0.4, 2.8, 2.8, 2.6), "h")
    S.plus(ell(0, 19.6, 2.4, 1.8, 1.6, 0.9), "g")
    S.plus(spiegel_x(ell(0.8, 20.3, 3.1, 0.3, 0.3, 0.25)), "d")
    S.plus(kasten(-0.9, 18.6, 2.8, 0.9, 19.0, 3.4), "d")
    S.plus(spiegel_x(kap((0.6, 18.8, 3.1), (0.7, 18.0, 3.2), 0.18, 0.08)), "k")
    for sx in (-1, 1):
        glied(S, [(sx * 5.0, 17.5, 0), (sx * 6.6, 21.5, 0.6), (sx * 4.6, 25.5, 0.6)], [2.0, 1.7, 1.5], "h")
        S.plus(ell(sx * 4.2, 26.2, 0.6, 1.5, 1.3, 1.5), "h")
    S.plus(ell(0, 28.6, 0.6, 5.2, 2.4, 3.4), "i")
    for k in range(8):
        a = k / 8 * 2 * math.pi
        S.plus(kap((math.cos(a) * 6, 2.5, math.sin(a) * 5), (math.cos(a) * 6.3, 0.2, math.sin(a) * 5.2), 0.4, 0.1),
               "i")
    _rendern(S, (-9, -1, -8), (9, 32, 8), w)
    return w


def riesenkrabbe(seed, g=2):
    """Riesenkrabbe am Strand: gepanzerter Rückenschild mit Höckern, zwei erhobene Scheren, Stielaugen und
    sechs spitze Laufbeine; um sie herum Muscheln und Seetang."""
    w = _welt(seed)
    u = U[g]
    S = Skulptur(w, u)
    if _stil(seed) == 0:
        S.mat("h", fell(w, "Krabbe", ["red_terracotta", "red_concrete", "orange_terracotta", "orange_concrete"]),
              basis=0.5, steigung=0.25, rausch=1.2)
    else:
        S.mat("h", fell(w, "Blaukrabbe", ["blue_terracotta", "blue_concrete", "light_blue_terracotta",
                                          "cyan_concrete"]), basis=0.5, steigung=0.25, rausch=1.2)
    S.mat("w", w.b("white_terracotta"))
    S.mat("d", w.b("black_concrete"))
    S.mat("s", fell(w, "Sand", ["sand", "sand", "sandstone", "gravel"]), basis=1, rausch=2)
    S.plus(kegel(0, 0, -0.8, 0.3, 13, 13), "s")
    S.plus(ell(0, 5.5, 0, 7.0, 3.4, 5.2), "h")
    for k in range(6):
        a = k / 6 * 2 * math.pi
        S.plus(ell(math.cos(a) * 4, 7.6, math.sin(a) * 2.8, 0.8, 0.8, 0.8), "h")
    S.plus(und(ell(0, 4.4, 0, 7.4, 2.8, 5.4), lambda X, Y, Z: Y < 3.2), "w")
    for sx in (-1, 1):
        S.plus(kap((sx * 1.4, 6.5, 4.6), (sx * 1.6, 9.5, 5.4), 0.3), "h")
        S.plus(ell(sx * 1.6, 9.8, 5.5, 0.55, 0.55, 0.55), "d")
        for i in range(3):
            bz = -2.5 + i * 2.2
            glied(S, [(sx * 6, 4.5, bz), (sx * 10.5, 9.0, bz * 1.3), (sx * 13, 0.3, bz * 1.6)], [1.2, 0.9, 0.35],
                  "h")
        glied(S, [(sx * 5, 5.5, 3.5), (sx * 9, 9, 6.5), (sx * 9.5, 14, 9.5)], [1.6, 1.4, 1.3], "h")
        S.plus(ell(sx * 9.6, 16.5, 10.0, 2.6, 3.4, 2.2), "h")
        S.plus(kap((sx * 8.8, 19.2, 10.2), (sx * 7.6, 24.5, 11.4), 1.3, 0.35), "h")
        S.plus(kap((sx * 10.8, 19.0, 10.2), (sx * 12.4, 23.0, 11.2), 1.0, 0.3), "h")
    _rendern(S, (-15, -1, -10), (15, 27, 14), w)
    return w


NEU = {
    "hirsch": ("Röhrender Hirsch", hirsch),
    "baer": ("Brüllender Bär", baer),
    "wolf": ("Heulender Wolf", wolf),
    "eule": ("Riesen-Eule", eule),
    "fuchs": ("Schlafender Fuchs", fuchs),
    "pferd": ("Aufbäumendes Pferd / Pegasus", pferd),
    "elefant": ("Elefant", elefant),
    "wal": ("Springender Wal", wal),
    "frosch": ("Froschkönig", frosch),
    "schnecke": ("Riesenschnecke", schnecke),
    "greif": ("Greif", greif),
    "phoenix": ("Phönix", phoenix),
    "einhorn": ("Einhorn", einhorn),
    "minotaurus": ("Minotaurus", minotaurus),
    "hydra": ("Hydra", hydra),
    "riesenspinne": ("Riesenspinne", riesenspinne),
    "yeti": ("Yeti", yeti),
    "riesenkrabbe": ("Riesenkrabbe", riesenkrabbe),
}

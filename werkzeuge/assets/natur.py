"""Natur-Assets: Felsbogen, Felsnadeln, Findlinge, Wasserfall-Klippe.

Alle Funktionen nehmen (seed, groesse) mit groesse 0 = mittel, 1 = groß.
"""

from __future__ import annotations

import math

from baeume import birke, fichte
from lib import Rauschen, Welt, einfuegen, ueberwuchern


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


class Gestein:
    """Geschichtetes Gestein: wechselnde Lagen aus Stein, Andesit, Tuff und Kalzit."""

    def __init__(self, w: Welt, art="stein"):
        self.w = w
        if art == "stein":
            self.lagen = [w.b("stone"), w.b("andesite"), w.b("stone"), w.b("tuff"), w.b("stone"), w.b("cobblestone")]
        elif art == "sand":
            self.lagen = [w.b("sandstone"), w.b("smooth_sandstone"), w.b("terracotta"), w.b("orange_terracotta"),
                          w.b("sandstone"), w.b("red_sandstone")]
        else:
            self.lagen = [w.b("deepslate"), w.b("tuff"), w.b("calcite"), w.b("deepslate"), w.b("tuff"), w.b("andesite")]
        self.alle = set(self.lagen)
        self.r = Rauschen(w, 7)

    def __call__(self, x, y, z):
        lage = int((y + self.r(x, 0, z) * 4) / 2.5) % len(self.lagen)
        return self.lagen[lage]


def _bewachsen(w: Welt, g: Gestein, gras_anteil=0.85):
    gras = w.b("grass_block", snowy=False)
    erde = w.b("dirt")
    moos = w.b("moss_block")
    for (x, y, z), b in list(w.bloecke.items()):
        if b in g.alle and w.frei(x, y + 1, z) and y >= 0:
            u = w.rng.random()
            if u < gras_anteil:
                w.setze(x, y, z, gras)
                if (x, y - 1, z) in w.bloecke and w.bloecke[(x, y - 1, z)] in g.alle:
                    w.setze(x, y - 1, z, erde)
            elif u < gras_anteil + 0.1:
                w.setze(x, y, z, moos)


def felsbogen(seed, groesse=1, art="stein"):
    """Natürlicher Felsbogen mit bewachsener Oberseite."""
    w = _welt(seed)
    g = Gestein(w, art)
    rs = Rauschen(w, 5)
    spann = [14, 24][groesse]
    hoehe = [12, 20][groesse]
    dicke = [3.5, 5.5][groesse]
    tiefe = [4, 6][groesse]
    R = spann / 2
    for x in range(int(-R - dicke * 2.5), int(R + dicke * 2.5) + 1):
        for z in range(-tiefe - 4, tiefe + 5):
            for y in range(-2, hoehe + int(dicke) + 4):
                # Abstand zu einer Halbellipse (dem Bogen)
                t = max(-1.0, min(1.0, x / (R + dicke)))
                bogen_y = hoehe * math.sqrt(max(0, 1 - t * t))
                d_bogen = math.hypot((abs(x) - (R + dicke * 0.3)) * 0.6, 0) if abs(x) > R else 0
                dy = y - bogen_y
                r_lokal = dicke * (1 + 0.6 * (abs(x) / (R + dicke)) ** 3) * (0.7 + 0.6 * rs(x, y, z))
                tz = abs(z) / (tiefe * (0.7 + 0.6 * rs(x, 40, z)))
                d = math.sqrt((dy / r_lokal) ** 2 + tz ** 2 + (d_bogen / r_lokal) ** 2)
                # Füße verbreitern sich zum Boden hin
                fuss = abs(x) > R * 0.7 and y < hoehe * 0.5
                if d < 1 or (fuss and tz < 1.1 and abs(abs(x) - R - dicke * 0.3) < dicke * (1.4 - y / hoehe)):
                    w.setze(x, y, z, g(x, y, z))
    _bewachsen(w, g, gras_anteil=0.5 if art == "stein" else 0.25)
    ueberwuchern(w, None, ranken=0.25, pflanzen=0.4, buesche=0.03, max_ranke=8)
    return w


def felsnadeln(seed, groesse=1, art="stein"):
    """Gruppe aus spitzen, geschichteten Felsnadeln."""
    w = _welt(seed)
    g = Gestein(w, art)
    rs = Rauschen(w, 3)
    n = [4, 7][groesse]
    for i in range(n):
        a = w.rng.random() * 2 * math.pi
        dist = 0 if i == 0 else [4, 7][groesse] + w.rng.random() * [5, 9][groesse]
        cx, cz = math.cos(a) * dist, math.sin(a) * dist
        H = ([20, 34][groesse] if i == 0 else [8, 14][groesse] + w.rng.random() * [9, 16][groesse])
        r0 = H * 0.17 + 1.2
        neig = (w.rng.random(2) - 0.5) * 0.25
        for y in range(-2, int(H) + 1):
            t = max(0, y) / H
            r = r0 * (1 - t) ** 0.9 + 0.4
            mx, mz = cx + neig[0] * y, cz + neig[1] * y
            for x in range(int(mx - r - 2), int(mx + r + 3)):
                for z in range(int(mz - r - 2), int(mz + r + 3)):
                    d = math.hypot(x - mx, z - mz)
                    if d < r * (0.75 + 0.5 * rs(x, y, z)):
                        w.setze(x, y, z, g(x, y, z))
    _bewachsen(w, g, gras_anteil=0.5)
    ueberwuchern(w, None, ranken=0.2, pflanzen=0.3, buesche=0.02)
    if groesse:
        for k in range(2):
            a = w.rng.random() * 2 * math.pi
            einfuegen(w, fichte(seed + k, 0), int(math.cos(a) * 14), 0, int(math.sin(a) * 14))
    return w


def findlinge(seed, groesse=1):
    """Gruppe bemooster Findlinge mit Farnen."""
    w = _welt(seed)
    rs = Rauschen(w, 3)
    steine = [w.b("stone"), w.b("andesite"), w.b("cobblestone"), w.b("mossy_cobblestone")]
    moos = w.b("moss_block")
    n = [4, 7][groesse]
    for i in range(n):
        a = w.rng.random() * 2 * math.pi
        dist = 0 if i == 0 else 3 + w.rng.random() * [6, 10][groesse]
        cx, cz = math.cos(a) * dist, math.sin(a) * dist
        r = ([3.5, 5.5][groesse] if i == 0 else 1.3 + w.rng.random() * [2, 3][groesse])
        cy = r * 0.35
        for x in range(int(cx - r - 2), int(cx + r + 3)):
            for y in range(-1, int(cy + r) + 2):
                for z in range(int(cz - r - 2), int(cz + r + 3)):
                    d = math.sqrt((x - cx) ** 2 + ((y - cy) * 1.25) ** 2 + (z - cz) ** 2)
                    if d < r * (0.8 + 0.4 * rs(x, y, z)):
                        w.setze(x, y, z, steine[int(rs(x * 3, y * 3, z * 3) * 3.99)])
    for (x, y, z), b in list(w.bloecke.items()):
        if b in steine and w.frei(x, y + 1, z) and w.rng.random() < 0.7:
            w.setze(x, y, z, moos)
    ueberwuchern(w, None, ranken=0.15, pflanzen=0.6, buesche=0.05)
    farn = w.b("fern")
    for _ in range([20, 40][groesse]):
        x, z = int(w.rng.integers(-12, 13)), int(w.rng.integers(-12, 13))
        if w.frei(x, 1, z) and not w.frei(x, 0, z) is False:
            w.setze(x, 1, z, farn)
    return w


def wasserfall_klippe(seed, groesse=1):
    """Klippe mit Wasserfall, Becken am Fuß und bewachsener Kante."""
    w = _welt(seed)
    g = Gestein(w, "stein")
    rs = Rauschen(w, 5)
    H = [14, 24][groesse]
    breite = [16, 26][groesse]
    tiefe = [10, 16][groesse]
    wasser = w.b("water", level=0)
    for x in range(-breite // 2, breite // 2 + 1):
        kante = 2 + rs(x, 0, 0) * 3
        for z in range(0, tiefe + 1):
            h = H * min(1, (z + 1) / kante) * (0.9 + 0.2 * rs(x, 10, z))
            if abs(x) > breite / 2 - 3:
                h *= 1 - (abs(x) - (breite / 2 - 3)) / 4
            for y in range(-1, int(h) + 1):
                w.setze(x, y, z, g(x, y, z))
    _bewachsen(w, g)
    # Rinne oben und Wasserfall an der Vorderkante
    for z in range(1, tiefe + 1):
        top = max(y for (a, y, c) in w.bloecke if a == 0 and c == z)
        for dx in (-1, 0, 1):
            w.setze(dx, top, z, wasser)
            w.setze(dx, top - 1, z, g(dx, top - 1, z))
    # Becken unten
    for x in range(-5, 6):
        for z in range(-7, 1):
            if math.hypot(x, z + 3) < 4.5 + rs(x, 0, z) * 1.5 and w.frei(x, 1, z):
                w.setze(x, 0, z, wasser)
                w.setze(x, -1, z, w.b("gravel"))
            elif math.hypot(x, z + 3) < 6.5 and w.frei(x, 0, z):
                w.setze(x, 0, z, w.b("mossy_cobblestone") if w.rng.random() < 0.5 else w.b("gravel"))
    # spiegeln, damit die Wasserfallseite nach Süden zeigt (Vorschau-Kamera)
    w.bloecke = {(x, y, -z): b for (x, y, z), b in w.bloecke.items()}
    # nur für die Vorschau: fallendes Wasser (im Spiel fließt es von selbst)
    kante = max(z for (x, y, z), b in w.bloecke.items() if b == wasser and y > 2)
    top = max(y for (x, y, z), b in w.bloecke.items() if b == wasser and z == kante)
    w.vorschau_extra = {}
    for y in range(1, top):
        for dx in (-1, 0, 1):
            fels = [z for z in range(-tiefe - 2, 12) if (dx, y, z) in w.bloecke and w.bloecke[(dx, y, z)] != wasser]
            if fels:
                w.vorschau_extra[(dx, y, max(fels) + 1)] = wasser
    ueberwuchern(w, None, ranken=0.35, pflanzen=0.4, buesche=0.04, max_ranke=10)
    if groesse:
        einfuegen(w, birke(seed, 1), -breite // 4, H, -(tiefe // 2 + 2))
    return w


NATUR = {
    "felsbogen": ("Felsbogen", felsbogen),
    "felsbogen_wueste": ("Wüsten-Felsbogen", lambda s, g: felsbogen(s, g, "sand")),
    "felsnadeln": ("Felsnadeln", felsnadeln),
    "findlinge": ("Findlinge", findlinge),
    "wasserfall": ("Wasserfall-Klippe", wasserfall_klippe),
}

"""Leuchtwald: biolumineszente Fantasie-Flora im Stil einer fremden Dschungelwelt.

Eigene Entwürfe (kein Nachbau): Leuchtweide, Riesiger Hohlbaum, Spiralpflanzen, Leuchtpilze,
Wurzeltor und Leuchtwiese. Größen 0 klein · 1 mittel · 2 riesig · 3 gigantisch.
"""

from __future__ import annotations

import math

import numpy as np

from baeume import Holzart, Pinsel, Wuchs, abzweig, ast, blattwolke, richtung_aus_winkeln, verzweigen, kugel_f
from lib import Rauschen, Verlauf, Welt, einfuegen, laub
from spektakulaer import brettwurzeln, verdrehter_stamm, bodenflaeche, bodenstreu

LEUCHT = ["light_blue_stained_glass", "cyan_stained_glass", "purple_stained_glass", "magenta_stained_glass"]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _boden(w: Welt, r):
    bodenflaeche(w, [w.b("moss_block"), w.b("grass_block", snowy=False), w.b("rooted_dirt")], r, 0.9)
    bodenstreu(w, [w.b("fern"), w.b("large_fern", half="lower"), w.b("torchflower"), w.b("moss_carpet"),
                   w.b("azalea")], int(r * 3), 1, r)
    for (x, y, z), b in list(w.bloecke.items()):
        if b == w.b("large_fern", half="lower"):
            if w.frei(x, y + 1, z):
                w.setze(x, y + 1, z, w.b("large_fern", half="upper"))
            else:
                w.setze(x, y, z, w.b("fern"))


def _strang(w: Welt, x, y, z, laenge, farben):
    """Leuchtender Hängestrang aus Glas mit Glühperlen."""
    for k in range(1, laenge + 1):
        if not w.frei(x, y - k, z) or y - k < 2:
            return
        if k % 5 == 0:
            w.setze(x, y - k, z, w.b("sea_lantern") if w.rng.random() < 0.5 else w.b("shroomlight"))
        else:
            w.setze(x, y - k, z, w.b(farben[int(w.rng.random() * len(farben))]))


def leuchtweide(seed, g=1):
    """Gewaltige Trauerweide, deren Zweige als leuchtende Stränge bis fast zum Boden hängen."""
    w = _welt(seed)
    holz = Holzart(w, "mangrove")
    pinsel = Pinsel(w, holz)
    H = [10, 16, 26, 40][g]
    rt = [1.0, 1.6, 2.6, 4.0][g]
    mitte = verdrehter_stamm(w, holz, H, 3, rt, rt * 1.1, 0.12, r_oben=rt * 0.6)
    brettwurzeln(w, pinsel, mitte[0], [4, 6, 8, 11][g], rt * 2.4, [5, 8, 13, 20][g], start_h=[3, 5, 7, 10][g],
                 dicke=[0.7, 1.0, 1.5, 2.2][g])
    cfg = Wuchs(kinder=3, spreizung=(30, 55), laenge=0.6, biegung=0.1, auftrieb=0.0, schwerkraft=0.015)
    enden, zw = [], []
    for i in range([4, 5, 7, 9][g]):
        d = richtung_aus_winkeln(i * 137.5, 45 + w.rng.random() * 20)
        verzweigen(w, pinsel, mitte[-1], d, H * 0.7, rt * 0.6, 2, cfg, enden, zw)
    blaetter = [(laub(w, "azalea"), 0.4), (laub(w, "mangrove"), 0.4), (laub(w, "flowering_azalea"), 0.2)]
    for p, t in enden:
        blattwolke(w, p + [0, 0.5, 0], [2.2, 2.8, 3.6, 4.6][g], 1.6, blaetter, schutz=holz.alle)
    ids = {b for b, _ in blaetter}
    for (x, y, z), b in list(w.bloecke.items()):
        if b in ids and w.frei(x, y - 1, z) and w.rng.random() < 0.07:
            _strang(w, x, y, z, int(y * (0.4 + 0.5 * w.rng.random())), LEUCHT)
    _boden(w, [6, 10, 16, 24][g])
    return w


def hohlbaum(seed, g=2):
    """Riesiger Hohlbaum mit Brettwurzeln, Eingängen und leuchtendem Inneren."""
    w = _welt(seed)
    holz = Holzart(w, "jungle")
    pinsel = Pinsel(w, holz)
    H = [18, 30, 50, 80][g]
    rt = [2.5, 4.0, 6.5, 10][g]
    mitte = verdrehter_stamm(w, holz, H, 4, rt, rt * 1.4, 0.06, r_oben=rt * 0.6)
    # aushöhlen und mit Lichtern füllen
    hohl = rt * 1.1
    for y in range(1, int(H * 0.8)):
        c = mitte[min(len(mitte) - 1, y * 2)]
        for x in range(int(c[0] - hohl) - 1, int(c[0] + hohl) + 2):
            for z in range(int(c[2] - hohl) - 1, int(c[2] + hohl) + 2):
                if math.hypot(x - c[0], z - c[2]) < hohl * (1 - y / (H * 1.2)):
                    w.setze(x, y, z, 0)
        if y % 6 == 3:
            w.setze(int(c[0]), y, int(c[2]), w.b("shroomlight"))
    # Eingänge
    for a in range(3):
        ang = a * 2.1
        for k in range(int(rt * 3)):
            for dy in range(1, [3, 4, 6, 8][g]):
                x = int(math.cos(ang) * k)
                z = int(math.sin(ang) * k)
                if w.hole(x, dy, z) in holz.alle:
                    w.setze(x, dy, z, 0)
    brettwurzeln(w, pinsel, mitte[0], [5, 7, 9, 12][g], rt * 2.6, [6, 10, 16, 26][g], start_h=[4, 7, 11, 18][g],
                 dicke=[1.0, 1.6, 2.4, 3.4][g])
    cfg = Wuchs(kinder=3, spreizung=(35, 60), laenge=0.6, biegung=0.08, auftrieb=0.02)
    enden, zw = [], []
    for i in range([5, 7, 9, 12][g]):
        p = mitte[int(len(mitte) * (0.7 + 0.3 * i / 12))]
        d = richtung_aus_winkeln(i * 137.5, 55 + w.rng.random() * 20)
        verzweigen(w, pinsel, p, d, H * 0.65, rt * 0.4, 2, cfg, enden, zw)
    blaetter = [(laub(w, "jungle"), 0.6), (laub(w, "dark_oak"), 0.25), (laub(w, "azalea"), 0.15)]
    for p, t in enden:
        blattwolke(w, p + [0, 0.5, 0], [3.2, 4.2, 5.6, 7.5][g], 2.4, blaetter, schutz=holz.alle)
    for (x, y, z), b in list(w.bloecke.items()):
        if b in {bb for bb, _ in blaetter} and w.frei(x, y - 1, z) and w.rng.random() < 0.05:
            _strang(w, x, y, z, int(3 + w.rng.random() * [6, 10, 16, 24][g]), LEUCHT[:2])
    _boden(w, [8, 12, 20, 30][g])
    return w


def spiralpflanzen(seed, g=1):
    """Gruppe hoher Spiralpflanzen mit eingerollten, leuchtend orangeroten Fächern."""
    w = _welt(seed)
    stiel = Verlauf(w, "Stiel", ["green_terracotta", "lime_terracotta", "moss_block"])
    faecher = Verlauf(w, "Spirale", ["red_terracotta", "red_concrete", "orange_concrete", "orange_terracotta",
                                     "yellow_concrete"])
    n = [3, 5, 8, 12][g]
    for i in range(n):
        a = w.rng.random() * 2 * math.pi
        d = 0 if i == 0 else [5, 8, 13, 20][g] * (0.4 + 0.6 * w.rng.random())
        cx, cz = math.cos(a) * d, math.sin(a) * d
        H = [6, 10, 16, 24][g] * (0.6 + 0.6 * w.rng.random())
        for y in range(0, int(H)):
            w.setze(int(cx), y, int(cz), stiel(2.0 * y / H, int(cx), y, int(cz)))
        # Spirale um den Stiel
        R = [1.5, 2.5, 3.5, 5][g]
        for k in range(int(H * 5)):
            t = k / (H * 5)
            y = H * 0.25 + t * H * 0.8
            r = R * (0.4 + 0.6 * math.sin(math.pi * t))
            ang = t * 6 * math.pi + i
            x, z = int(round(cx + math.cos(ang) * r)), int(round(cz + math.sin(ang) * r))
            w.setze(x, int(y), z, faecher(4.0 * t, x, int(y), z))
        w.setze(int(cx), int(H), int(cz), w.b("shroomlight"))
    _boden(w, [5, 8, 12, 18][g])
    return w


def leuchtpilze(seed, g=1):
    """Biolumineszente Riesenpilze in Türkis und Violett mit Leuchtlicht unter dem Hut."""
    w = _welt(seed)
    hut = [Verlauf(w, "Hut türkis", ["warped_wart_block", "cyan_terracotta", "light_blue_concrete"]),
           Verlauf(w, "Hut violett", ["purple_terracotta", "purple_concrete", "magenta_concrete"])]
    n = [2, 4, 6, 9][g]
    for i in range(n):
        a = w.rng.random() * 2 * math.pi
        d = 0 if i == 0 else [4, 7, 11, 16][g] * (0.5 + 0.5 * w.rng.random())
        cx, cz = math.cos(a) * d, math.sin(a) * d
        H = [6, 10, 16, 26][g] * (0.5 + 0.7 * w.rng.random()) * (1.3 if i == 0 else 1)
        R = H * 0.45
        v = hut[i % 2]
        for y in range(0, int(H)):
            kugel_f(w, (cx, y + 0.5, cz), max(0.6, R * 0.12), w.b("mushroom_stem"))
        for x in range(int(cx - R) - 1, int(cx + R) + 2):
            for z in range(int(cz - R) - 1, int(cz + R) + 2):
                dd = math.hypot(x - cx, z - cz) / R
                if dd > 1:
                    continue
                hy = int(H + (1 - dd ** 2) * R * 0.45)
                for y in range(hy - 1, hy + 1):
                    w.setze(x, y, z, v(2.5 * (1 - dd) + w.rng.random() * 0.4, x, y, z))
                if dd < 0.85 and w.rng.random() < 0.15:
                    w.setze(x, hy - 2, z, w.b("shroomlight") if w.rng.random() < 0.5 else w.b("sea_lantern"))
    _boden(w, [6, 10, 15, 22][g])
    return w


def wurzeltor(seed, g=1):
    """Tor aus verschlungenen Wurzeln mit leuchtenden Perlen."""
    w = _welt(seed)
    holz = Holzart(w, "mangrove")
    pinsel = Pinsel(w, holz)
    S = [8, 14, 22, 34][g]
    H = [8, 13, 20, 30][g]
    for k in range(3):
        versatz = (k - 1) * [1.0, 1.5, 2.0, 3.0][g]
        punkte = []
        for i in range(41):
            t = i / 40
            x = -S / 2 + S * t
            y = H * math.sin(math.pi * t) + 0.5
            z = versatz * math.cos(t * 9 + k)
            punkte.append((x, y, z))
        pinsel.neu()
        for (x, y, z) in punkte:
            for dx in np.arange(0, S / 40 + 0.01, 0.25):
                pinsel.punkt(np.array([x + dx, y, z]), [0.45, 0.6, 0.9, 1.3][g], np.array([1, 0, 0]))
    for (x, y, z), b in list(w.bloecke.items()):
        if b in holz.alle and w.frei(x, y - 1, z) and y > 3 and w.rng.random() < 0.18:
            _strang(w, x, y, z, int(2 + w.rng.random() * 5), LEUCHT)
    _boden(w, S // 2 + 3)
    return w


def leuchtwiese(seed, g=1):
    """Waldboden voller leuchtender Pflanzen, Farne und kleiner Pilze."""
    w = _welt(seed)
    r = [6, 10, 16, 24][g]
    _boden(w, r)
    for _ in range(int(r * r * 0.12)):
        a = w.rng.random() * 2 * math.pi
        d = r * w.rng.random() ** 0.6
        x, z = int(math.cos(a) * d), int(math.sin(a) * d)
        if not w.frei(x, 1, z):
            continue
        u = w.rng.random()
        if u < 0.25:
            h = 1 + int(w.rng.random() * 3)
            for y in range(1, h + 1):
                w.setze(x, y, z, w.b(LEUCHT[int(w.rng.random() * 4)]))
            w.setze(x, h + 1, z, w.b("shroomlight"))
        elif u < 0.4:
            w.setze(x, 1, z, w.b("warped_fungus") if w.rng.random() < 0.5 else w.b("crimson_fungus"))
        elif u < 0.55:
            w.setze(x, 1, z, w.b("sea_lantern"))
            w.setze(x, 2, z, w.b("moss_carpet"))
    return w


LEUCHTWALD = {
    "leuchtweide": ("Leuchtweide", leuchtweide),
    "hohlbaum": ("Riesiger Hohlbaum", hohlbaum),
    "spiralpflanzen": ("Spiralpflanzen", spiralpflanzen),
    "leuchtpilze": ("Leuchtpilze", leuchtpilze),
    "wurzeltor": ("Wurzeltor", wurzeltor),
    "leuchtwiese": ("Leuchtwiese", leuchtwiese),
}

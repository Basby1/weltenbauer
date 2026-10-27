"""Spektakuläre Bäume: riesige und mittelgroße Fantasy-Bäume.

Jede Funktion nimmt (seed, groesse) mit groesse 0 = mittel, 1 = riesig.
"""

from __future__ import annotations

import math

import numpy as np

from baeume import (Holzart, Pinsel, Wuchs, abzweig, ast, blattwolke, bodenstreu, kugel_f, neue_welt, norm,
                    richtung_aus_winkeln, verzweigen)
from lib import Rauschen, Welt, einfuegen, laub

# --------------------------------------------------------------------------- Bausteine


def verdrehter_stamm(w: Welt, holz: Holzart, H, n, r_teil, spirale, drall, r_oben=None):
    """Mehrere ineinander verdrehte Teilstämme. Gibt Mittelpunkte je Höhe zurück."""
    r_oben = r_oben if r_oben is not None else r_teil * 0.5
    phase0 = w.rng.random() * 2 * math.pi
    schritte = int(H / 0.5)
    mitte = []
    neig = (w.rng.random(2) - 0.5) * 0.08
    for i in range(schritte + 1):
        t = i / schritte
        y = 0.5 + t * H
        cx = 0.5 + neig[0] * y * y / H
        cz = 0.5 + neig[1] * y * y / H
        sr = spirale * (1 - 0.7 * t)
        rr = r_teil + (r_oben - r_teil) * t
        for k in range(n):
            ph = phase0 + k * 2 * math.pi / n + y * drall
            p = (cx + math.cos(ph) * sr, y, cz + math.sin(ph) * sr)
            kugel_f(w, p, rr, holz.wood["y"])
        mitte.append(np.array([cx, y, cz]))
    return mitte


def brettwurzeln(w: Welt, pinsel: Pinsel, mitte_unten, anzahl, r_stamm, weite, start_h, dicke=1.6):
    """Mächtige Wurzeln: setzen hoch am Stamm an, wölben sich nach außen und schlängeln über den Boden."""
    az0 = w.rng.random() * 360
    for i in range(anzahl):
        az = math.radians(az0 + i * 360 / anzahl + (w.rng.random() - 0.5) * 25)
        richtung = norm([math.cos(az), -0.55, math.sin(az)])
        start = np.array([mitte_unten[0] + math.cos(az) * r_stamm * 0.6, start_h * (0.7 + 0.5 * w.rng.random()),
                          mitte_unten[2] + math.sin(az) * r_stamm * 0.6])
        l1 = start[1] / 0.55 * 1.1
        pkt = ast(w, pinsel, start, richtung, l1, dicke, dicke * 0.7, biegung=0.06)
        # danach am Boden entlang schlängeln, mal über, mal unter der Erde
        p = pkt[-1][0].copy()
        p[1] = max(p[1], 0.5)
        d = norm([math.cos(az), 0, math.sin(az)])
        rest = weite * (0.6 + 0.6 * w.rng.random())
        schritte = int(rest / 0.5)
        r = dicke * 0.7
        pinsel.neu()
        for s in range(schritte):
            t = s / schritte
            d = norm(d + (w.rng.random(3) - 0.5) * [0.35, 0, 0.35])
            p = p + d * 0.5
            p[1] = 0.6 + math.sin(s * 0.35 + i) * 0.9 - t * 1.2
            pinsel.punkt(p, max(0.45, r * (1 - t)), d)
            # Seitenwurzeln
            if w.rng.random() < 0.04:
                d2 = norm(d + np.array([-d[2], 0, d[0]]) * (1 if w.rng.random() < 0.5 else -1))
                ast(w, pinsel, p, d2 + [0, -0.2, 0], 2 + w.rng.random() * 3, 0.5, 0.4, biegung=0.2)
                pinsel.neu()


def kuppel_aus_enden(w, enden, rx, ry, blaetter, schutz, luecken=0.08, min_y=-999, streuung=0.35):
    for p in enden:
        f = 1 + (w.rng.random() - 0.5) * 2 * streuung
        blattwolke(w, p + [0, ry * 0.4, 0], rx * f, ry * f, blaetter, schutz=schutz, luecken=luecken, min_y=min_y)


def leuchten_einstreuen(w: Welt, blaetter_ids, licht, anteil=0.02):
    """Lichtquellen (z. B. Shroomlight) im Inneren der Krone verteilen."""
    for (x, y, z), b in list(w.bloecke.items()):
        if b not in blaetter_ids or w.rng.random() > anteil:
            continue
        innen = all(not w.frei(x + a, y + c, z + e) for a, c, e in
                    ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, -1)))
        if innen:
            w.setze(x, y, z, licht)


def leuchtbeeren(w: Welt, traeger, anteil, max_laenge):
    """Leuchtbeeren-Ranken (Cave Vines), die unter Holz hängen."""
    koerper = w.b("cave_vines_plant", berries=True)
    koerper_leer = w.b("cave_vines_plant", berries=False)
    spitze = w.b("cave_vines", age=25, berries=True)
    for (x, y, z), b in list(w.bloecke.items()):
        if b not in traeger or not w.frei(x, y - 1, z) or w.rng.random() > anteil:
            continue
        laenge = int(2 + w.rng.random() * max_laenge)
        pos = []
        for k in range(1, laenge + 1):
            if y - k < 2 or not w.frei(x, y - k, z):
                break
            pos.append(y - k)
        if len(pos) < 2:
            continue
        for yy in pos[:-1]:
            w.setze(x, yy, z, koerper if w.rng.random() < 0.45 else koerper_leer)
        w.setze(x, pos[-1], z, spitze)


def haengende_ranken(w: Welt, traeger, anteil, max_laenge, min_y=2):
    """Normale Ranken an den Seiten von Blättern/Holz – jede hängt an Block oder Ranke darüber."""
    seiten = [(1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")]
    for (x, y, z), b in list(w.bloecke.items()):
        if b not in traeger:
            continue
        for dx, dz, s in seiten:
            ax, az = x + dx, z + dz
            if not w.frei(ax, y, az) or w.rng.random() > anteil:
                continue
            if not w.frei(ax, y + 1, az) and w.hole(ax, y + 1, az) in traeger:
                continue
            ranke = w.b("vine", **{k: (k == s) for k in ("north", "east", "south", "west")}, up=False)
            for k in range(int(1 + w.rng.random() * max_laenge)):
                yy = y - k
                if yy < min_y or not w.frei(ax, yy, az):
                    break
                w.setze(ax, yy, az, ranke)


def bodenflaeche(w: Welt, blk_liste, r, dichte=0.7):
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            d = math.hypot(x, z) / r
            if d < 1 and w.rng.random() < dichte * (1.2 - d) and w.frei(x, 0, z):
                w.setze(x, 0, z, blk_liste[int(w.rng.random() * len(blk_liste))])


# --------------------------------------------------------------------------- Arten


def weltenbaum(seed, groesse=1):
    """Weltenbaum: verdrehte Zwillingsstämme, riesige Brettwurzeln, gewaltige Krone mit Leuchtbeeren."""
    w = neue_welt(seed)
    holz = Holzart(w, "oak")
    pinsel = Pinsel(w, holz)
    H = [22, 40][groesse]
    rt = [1.6, 2.8][groesse]
    mitte = verdrehter_stamm(w, holz, H, [3, 4][groesse], rt, [1.8, 3.2][groesse], 0.09, r_oben=rt * 0.55)
    brettwurzeln(w, pinsel, mitte[0], [6, 9][groesse], rt * 2.5, [7, 12][groesse], start_h=[5, 9][groesse],
                 dicke=[1.2, 2.0][groesse])
    blaetter = [(laub(w, "oak"), 0.62), (laub(w, "dark_oak"), 0.2), (laub(w, "azalea"), 0.12),
                (laub(w, "flowering_azalea"), 0.06)]
    cfg = Wuchs(kinder=3, spreizung=(30, 55), laenge=0.6, biegung=0.08, auftrieb=0.035, duenn=0.6)
    enden, zw = [], []
    n_haupt = [6, 9][groesse]
    az0 = w.rng.random() * 360
    for i in range(n_haupt):
        hoehe_i = int(len(mitte) * (0.62 + 0.38 * i / n_haupt))
        p = mitte[min(hoehe_i, len(mitte) - 1)]
        d = richtung_aus_winkeln(az0 + i * 137.5, 50 + w.rng.random() * 25 - 15 * i / n_haupt)
        verzweigen(w, pinsel, p, d, [13, 26][groesse] * (0.8 + 0.4 * w.rng.random()), [1.0, 1.7][groesse],
                   2, cfg, enden, zw)
    rx = [3.6, 5.6][groesse]
    kuppel_aus_enden(w, [p for p, t in enden if t == 0], rx, rx * 0.6, blaetter, holz.alle, min_y=H * 0.55)
    kuppel_aus_enden(w, [p for p, t in enden if t == 1][::2], rx * 0.8, rx * 0.5, blaetter, holz.alle,
                     min_y=H * 0.55)
    blattwolke(w, mitte[-1] + [0, 3, 0], rx * 1.6, rx * 0.9, blaetter, schutz=holz.alle)
    ids = {b for b, _ in blaetter}
    leuchten_einstreuen(w, ids, w.b("shroomlight"), 0.03)
    leuchtbeeren(w, holz.alle, 0.08, [4, 8][groesse])
    haengende_ranken(w, ids, 0.02, [5, 9][groesse])
    bodenflaeche(w, [w.b("moss_block"), w.b("rooted_dirt"), w.b("podzol", snowy=False)], [7, 13][groesse])
    bodenstreu(w, [w.b("fern"), w.b("moss_carpet"), w.b("azalea"), w.b("flowering_azalea")],
               [20, 50][groesse], 3, [8, 15][groesse])
    return w


def sakura_riese(seed, groesse=1):
    """Sakura-Riese: dicker geneigter Stamm, weit ausladende tragende Äste, riesige rosa Wolken."""
    w = neue_welt(seed)
    holz = Holzart(w, "cherry")
    pinsel = Pinsel(w, holz)
    H = [11, 17][groesse]
    st = ast(w, pinsel, [0.5, 0.5, 0.5], richtung_aus_winkeln(w.rng.random() * 360, 18), H, [1.6, 2.6][groesse],
             [1.0, 1.6][groesse], biegung=0.1, auftrieb=0.05)
    brettwurzeln(w, pinsel, st[0][0], [5, 7][groesse], [1.6, 2.6][groesse] * 1.6, [5, 9][groesse], start_h=3,
                 dicke=[0.8, 1.2][groesse])
    blaetter = [(laub(w, "cherry"), 1.0)]
    cfg = Wuchs(kinder=3, spreizung=(20, 40), laenge=0.6, biegung=0.08, auftrieb=0.018, schwerkraft=0.0)
    enden, zw = [], []
    n = [5, 7][groesse]
    az0 = w.rng.random() * 360
    for i in range(n):
        p, pd, pr = st[int(len(st) * (0.6 + 0.4 * i / n)) - 1]
        d = richtung_aus_winkeln(az0 + i * 360 / n + (w.rng.random() - 0.5) * 30, 50 + w.rng.random() * 15)
        verzweigen(w, pinsel, p, d, [13, 22][groesse] * (0.8 + 0.4 * w.rng.random()), pr * 0.6, 2, cfg, enden, zw)
    rx = [3.4, 4.6][groesse]
    kuppel_aus_enden(w, [p for p, t in enden if t <= 1], rx, rx * 0.55, blaetter, holz.alle, luecken=0.04,
                     min_y=H * 0.6)
    # hängende Blütenzweige
    blatt = blaetter[0][0]
    for (x, y, z), b in list(w.bloecke.items()):
        if b == blatt and w.frei(x, y - 1, z) and w.rng.random() < 0.06:
            for k in range(1, int(2 + w.rng.random() * 4)):
                if not w.frei(x, y - k, z) or y - k < 3:
                    break
                w.setze(x, y - k, z, blatt)
    blueten = w.b("pink_petals", facing="north", flower_amount=4)
    bodenstreu(w, [blueten, w.b("pink_petals", facing="east", flower_amount=2)], [80, 220][groesse], 1,
               [12, 20][groesse])
    return w


def drachenbaum(seed, groesse=1):
    """Drachenbaum: kurzer Stamm, kandelaberartig nach oben gabelnde Äste und flacher, dichter Schirm."""
    w = neue_welt(seed)
    holz = Holzart(w, "spruce")
    pinsel = Pinsel(w, holz)
    H = [5, 8][groesse]
    st = ast(w, pinsel, [0.5, 0.5, 0.5], [0, 1, 0], H, [1.1, 1.7][groesse], [1.0, 1.5][groesse], biegung=0.03,
             auftrieb=0.05)
    cfg = Wuchs(kinder=2, spreizung=(18, 32), laenge=0.85, ansatz=0.97, biegung=0.03, auftrieb=0.05, duenn=0.8)
    enden, zw = [], []
    n = [5, 7][groesse]
    for i in range(n):
        d = richtung_aus_winkeln(i * 360 / n + w.rng.random() * 20, 40 + w.rng.random() * 12)
        verzweigen(w, pinsel, st[-1][0], d, [4, 6][groesse], [0.8, 1.0][groesse], [2, 3][groesse], cfg, enden, zw)
    spitzen = [p for p, t in enden if t == 0]
    oben = max(p[1] for p in spitzen)
    blaetter = [(laub(w, "dark_oak"), 0.55), (laub(w, "jungle"), 0.45)]
    for p in spitzen:
        blattwolke(w, p + [0, 0.8, 0], [3.0, 3.6][groesse], 1.4, blaetter, dichte=0.97, schutz=holz.alle,
                   min_y=oben - [5, 7][groesse])
    bodenflaeche(w, [w.b("coarse_dirt"), w.b("rooted_dirt")], [4, 6][groesse], 0.5)
    return w


def baobab(seed, groesse=1):
    """Baobab: gewaltiger flaschenförmiger Stamm mit kleiner, knorriger Krone."""
    w = neue_welt(seed)
    holz = Holzart(w, "acacia")
    pinsel = Pinsel(w, holz)
    H = [13, 21][groesse]
    R = [3.0, 5.0][groesse]
    rs = Rauschen(w, 4)
    for y in range(0, H + 1):
        t = y / H
        r = R * (1.0 + 0.18 * math.sin(t * math.pi * 1.2) - 0.45 * t ** 2.2)
        for x in range(-int(R) - 3, int(R) + 4):
            for z in range(-int(R) - 3, int(R) + 4):
                d = math.hypot(x, z)
                ang = math.atan2(z, x)
                rr = r * (0.88 + 0.24 * rs(math.cos(ang) * 6, y, math.sin(ang) * 6))
                if d <= rr:
                    w.setze(x, y, z, holz.wood["y"])
    top = np.array([0.5, H + 0.5, 0.5])
    cfg = Wuchs(kinder=2, spreizung=(40, 65), laenge=0.7, biegung=0.1, auftrieb=0.0)
    enden, zw = [], []
    n = [5, 7][groesse]
    for i in range(n):
        a = math.radians(i * 360 / n)
        start = top + np.array([math.cos(a) * R * 0.3, -1, math.sin(a) * R * 0.3])
        d = richtung_aus_winkeln(i * 360 / n + w.rng.random() * 30, 78 + w.rng.random() * 10)
        verzweigen(w, pinsel, start, d, [4, 6][groesse], [0.7, 1.0][groesse], 2, cfg, enden, zw)
    blaetter = [(laub(w, "acacia"), 0.6), (laub(w, "jungle"), 0.4)]
    for p, t in enden:
        if t == 0:
            blattwolke(w, p + [0, 0.5, 0], 2.0, 1.1, blaetter, dichte=0.9, schutz=holz.alle, luecken=0.15)
    return w


def gespensterbaum(seed, groesse=1):
    """Gespensterbaum: riesiger toter Baum, verdrehte Äste, Spinnweben und Seelenlaternen an Ketten."""
    w = neue_welt(seed)
    holz = Holzart(w, "dark_oak")
    pinsel = Pinsel(w, holz)
    H = [14, 24][groesse]
    rt = [1.3, 2.0][groesse]
    mitte = verdrehter_stamm(w, holz, H, 3, rt, [1.2, 2.0][groesse], 0.16, r_oben=rt * 0.5)
    brettwurzeln(w, pinsel, mitte[0], [5, 7][groesse], rt * 2.5, [7, 12][groesse], start_h=[4, 6][groesse],
                 dicke=[0.9, 1.3][groesse])
    cfg = Wuchs(kinder=2, spreizung=(30, 70), laenge=0.65, biegung=0.3, auftrieb=0.02, schwerkraft=0.01)
    enden, zw = [], []
    n = [5, 7][groesse]
    for i in range(n):
        p = mitte[min(len(mitte) - 1, int(len(mitte) * (0.5 + 0.5 * i / n)))]
        d = richtung_aus_winkeln(i * 137.5, 45 + w.rng.random() * 35)
        verzweigen(w, pinsel, p, d, [9, 15][groesse], [0.8, 1.2][groesse], [2, 3][groesse], cfg, enden, zw)
    # Spinnweben in Astgabeln
    netz = w.b("cobweb")
    for p in zw:
        for _ in range(2):
            q = p + (w.rng.random(3) - 0.5) * 3
            if w.frei(*np.floor(q)):
                w.setze(*np.floor(q), netz)
    # Seelenlaternen an Ketten unter Ästen
    kette = w.b("chain", axis="y", waterlogged=False)
    laterne = w.b("soul_lantern", hanging=True, waterlogged=False)
    kandidaten = [(x, y, z) for (x, y, z), b in w.bloecke.items()
                  if b in holz.alle and y > H * 0.5 and w.frei(x, y - 1, z)]
    w.rng.shuffle(kandidaten)
    for (x, y, z) in kandidaten[:[6, 14][groesse]]:
        laenge = int(1 + w.rng.random() * 3)
        if all(w.frei(x, y - k, z) for k in range(1, laenge + 3)):
            for k in range(1, laenge + 1):
                w.setze(x, y - k, z, kette)
            w.setze(x, y - laenge - 1, z, laterne)
    bodenflaeche(w, [w.b("soul_soil"), w.b("coarse_dirt"), w.b("podzol", snowy=False)], [6, 10][groesse])
    bodenstreu(w, [w.b("dead_bush"), w.b("brown_mushroom")], [10, 20][groesse], 2, [7, 11][groesse])
    return w


def _pilzhut_seiten(w: Welt, ids):
    """Setzt die Seiten-Properties der Pilzblöcke wie bei natürlichen Riesenpilzen."""
    nach = {"up": (0, 1, 0), "down": (0, -1, 0), "north": (0, 0, -1), "south": (0, 0, 1),
            "east": (1, 0, 0), "west": (-1, 0, 0)}
    for (x, y, z), b in list(w.bloecke.items()):
        name = w.P.name(b)
        if name not in ids:
            continue
        props = {k: (w.hole(x + d[0], y + d[1], z + d[2]) is None or
                     w.P.name(w.hole(x + d[0], y + d[1], z + d[2])) not in ids | {"minecraft:mushroom_stem"})
                 for k, d in nach.items()}
        w.setze(x, y, z, w.b(name, **props))


def riesenpilz(seed, groesse=1, art="red"):
    """Riesenpilz mit gebogenem Stiel und gewölbtem Hut, plus kleinere Pilze daneben."""
    w = neue_welt(seed)
    _pilz(w, np.array([0.5, 0.5, 0.5]), [14, 26][groesse], [1.3, 2.3][groesse], [6, 11][groesse], art)
    for k in range(2):
        a = w.rng.random() * 2 * math.pi
        d = [7, 12][groesse] + w.rng.random() * 3
        andere = "brown" if art == "red" and k == 1 else art
        _pilz(w, np.array([0.5 + math.cos(a) * d, 0.5, 0.5 + math.sin(a) * d]), [6, 11][groesse] * (0.7 + 0.5 * k),
              [0.6, 1.0][groesse], [3, 5][groesse] * (0.8 + 0.3 * k), andere)
    _pilzhut_seiten(w, {"minecraft:red_mushroom_block", "minecraft:brown_mushroom_block"})
    bodenflaeche(w, [w.b("mycelium", snowy=False), w.b("podzol", snowy=False)], [10, 17][groesse], 0.9)
    bodenstreu(w, [w.b("red_mushroom"), w.b("brown_mushroom")], [15, 30][groesse], 2, [10, 16][groesse])
    return w


def _pilz(w, fuss, H, r, R, art):
    stiel = w.b("mushroom_stem")
    hut = w.b(f"{art}_mushroom_block")
    d = richtung_aus_winkeln(w.rng.random() * 360, 15)
    p = fuss.astype(float)
    for i in range(int(H / 0.5)):
        t = i / (H / 0.5)
        kugel_f(w, p, r * (1.15 - 0.3 * t), stiel)
        d = norm(d + [0, 0.05, 0] + (w.rng.random(3) - 0.5) * 0.05)
        p = p + d * 0.5
    top = p
    licht = w.b("shroomlight")
    if art == "red":
        # gewölbter Hut mit herabgezogenem Rand
        for x in range(int(top[0] - R - 2), int(top[0] + R + 3)):
            for z in range(int(top[2] - R - 2), int(top[2] + R + 3)):
                dd = math.hypot(x + 0.5 - top[0], z + 0.5 - top[2]) / R
                if dd > 1.05:
                    continue
                h = math.sqrt(max(0, 1 - dd * dd)) * R * 0.75
                y_ober = int(top[1] + h)
                dicke = 2 if dd < 0.85 else int(2 + (dd - 0.85) * R * 1.2)
                for y in range(y_ober - dicke + 1, y_ober + 1):
                    w.setze(x, y, z, hut)
                if 0.55 < dd < 0.8 and w.rng.random() < 0.12:
                    w.setze(x, y_ober - dicke, z, licht)
    else:
        # flacher, breiter Hut
        for x in range(int(top[0] - R * 1.3 - 2), int(top[0] + R * 1.3 + 3)):
            for z in range(int(top[2] - R * 1.3 - 2), int(top[2] + R * 1.3 + 3)):
                dd = math.hypot(x + 0.5 - top[0], z + 0.5 - top[2]) / (R * 1.3)
                if dd > 1:
                    continue
                y = int(top[1] + (1 if dd < 0.6 else 0))
                w.setze(x, y, z, hut)
                if 0.4 < dd < 0.8 and w.rng.random() < 0.08:
                    w.setze(x, y - 1, z, licht)


def netherriese(seed, groesse=1, art="crimson"):
    """Riesiger Netherpilz: Karmesin (rot, Trauerranken) oder Wirr (türkis, Zwirbelranken)."""
    w = neue_welt(seed)
    holz_name = f"{art}_stem"
    stamm = {a: w.b(holz_name, axis=a) for a in "xyz"}
    huelle = {a: w.b(f"{art}_hyphae", axis=a) for a in "xyz"}

    class H_:  # kleine Holzart-Attrappe für den Pinsel
        pass
    holz = H_()
    holz.log, holz.wood, holz.alle = stamm, huelle, set(stamm.values()) | set(huelle.values())
    pinsel = Pinsel(w, holz)
    H = [16, 28][groesse]
    st = ast(w, pinsel, [0.5, 0.5, 0.5], richtung_aus_winkeln(w.rng.random() * 360, 6), H, [1.4, 2.4][groesse],
             [0.9, 1.4][groesse], biegung=0.06, auftrieb=0.05)
    from spektakulaer import brettwurzeln as bw  # noqa
    bw(w, pinsel, st[0][0], [5, 7][groesse], [1.4, 2.4][groesse] * 2, [5, 9][groesse], start_h=3,
       dicke=[0.8, 1.2][groesse])
    wart = w.b("nether_wart_block" if art == "crimson" else "warped_wart_block")
    licht = w.b("shroomlight")
    top = st[-1][0]
    R = [7, 12][groesse]
    rs = Rauschen(w, 3)
    for x in range(int(top[0] - R - 2), int(top[0] + R + 3)):
        for z in range(int(top[2] - R - 2), int(top[2] + R + 3)):
            dd = math.hypot(x + 0.5 - top[0], z + 0.5 - top[2]) / R
            dd *= 0.85 + 0.3 * rs(x, 0, z)
            if dd > 1:
                continue
            h = math.sqrt(max(0, 1 - dd * dd)) * R * 0.55
            y_ober = int(top[1] + h)
            dicke = 2 if dd < 0.8 else int(2 + (dd - 0.8) * 25)
            for y in range(y_ober - dicke + 1, y_ober + 1):
                w.setze(x, y, z, licht if w.rng.random() < 0.05 else wart)
    # Ranken
    if art == "crimson":
        koerper, spitze = w.b("weeping_vines_plant"), w.b("weeping_vines", age=25)
        for (x, y, z), b in list(w.bloecke.items()):
            if b == wart and w.frei(x, y - 1, z) and w.rng.random() < 0.18:
                laenge = int(2 + w.rng.random() * [6, 12][groesse])
                pos = [y - k for k in range(1, laenge + 1) if y - k >= 2]
                pos2 = []
                for yy in pos:
                    if not w.frei(x, yy, z):
                        break
                    pos2.append(yy)
                if len(pos2) >= 2:
                    for yy in pos2[:-1]:
                        w.setze(x, yy, z, koerper)
                    w.setze(x, pos2[-1], z, spitze)
        boden = [w.b("crimson_nylium"), w.b("netherrack")]
        streu = [w.b("crimson_roots"), w.b("crimson_fungus")]
    else:
        koerper, spitze = w.b("twisting_vines_plant"), w.b("twisting_vines", age=25)
        for (x, y, z), b in list(w.bloecke.items()):
            if b == wart and w.frei(x, y + 1, z) and w.rng.random() < 0.05:
                laenge = int(2 + w.rng.random() * 4)
                for k in range(1, laenge):
                    w.setze(x, y + k, z, koerper)
                w.setze(x, y + laenge, z, spitze)
        boden = [w.b("warped_nylium"), w.b("netherrack")]
        streu = [w.b("warped_roots"), w.b("warped_fungus"), w.b("nether_sprouts")]
    bodenflaeche(w, boden, [8, 13][groesse], 0.9)
    bodenstreu(w, streu, [20, 40][groesse], 2, [8, 13][groesse])
    return w


def schwebende_insel(seed, groesse=1):
    """Schwebende Insel mit Baum, Wasserfall-Becken und herabhängenden Wurzeln.
    Die Insel schwebt über dem Anker (der Anker liegt auf dem Boden darunter)."""
    from baeume import eiche, kirschbaum
    w = neue_welt(seed)
    R = [9, 15][groesse]
    T = [13, 24][groesse]
    sockel = T + [8, 12][groesse]
    rs = Rauschen(w, 4)
    stein = [w.b("stone"), w.b("andesite"), w.b("tuff"), w.b("cobblestone")]
    erde, gras, moos = w.b("dirt"), w.b("grass_block", snowy=False), w.b("moss_block")
    oben = {}
    for x in range(-R - 3, R + 4):
        for z in range(-R - 3, R + 4):
            d = math.hypot(x, z) / R
            d *= 0.85 + 0.35 * rs(x, 0, z)
            if d > 1:
                continue
            tiefe = int(T * (1 - d) ** 0.85 * (0.7 + 0.6 * rs(x, 30, z))) + 2
            buckel = int(2 * (1 - d) * rs(x, 60, z))
            y_top = sockel + buckel
            oben[(x, z)] = y_top
            for y in range(y_top - tiefe, y_top + 1):
                if y == y_top:
                    b = gras
                elif y > y_top - 3:
                    b = erde
                else:
                    b = stein[int(rs(x, y * 2, z) * 3.99)]
                w.setze(x, y, z, b)
    # Unterseite: hängende Wurzeln, Ranken, Moos
    wurzeln = w.b("hanging_roots", waterlogged=False)
    for (x, y, z), b in list(w.bloecke.items()):
        if b in stein and w.frei(x, y - 1, z):
            u = w.rng.random()
            if u < 0.08:
                w.setze(x, y - 1, z, wurzeln)
            elif u < 0.12:
                w.setze(x, y, z, moos)
    # Becken mit Wasserfall an der Kante
    a = w.rng.random() * 2 * math.pi
    wasser = w.b("water", level=0)
    for r in np.arange(R * 0.35, R * 1.2, 0.5):
        x, z = int(round(math.cos(a) * r)), int(round(math.sin(a) * r))
        if (x, z) not in oben:
            continue
        y = oben[(x, z)]
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if (x + dx, z + dz) in oben and abs(dx) + abs(dz) < 2:
                    w.setze(x + dx, oben[(x + dx, z + dz)], z + dz, wasser)
    # Baum obendrauf
    baum = (kirschbaum if w.rng.random() < 0.5 else eiche)(seed + 1, 1 if groesse else 0)
    mx, mz = int(-math.cos(a) * R * 0.25), int(-math.sin(a) * R * 0.25)
    einfuegen(w, baum, mx, oben.get((mx, mz), sockel), mz)
    bodenstreu_ueber(w, oben, [w.b("grass"), w.b("fern"), w.b("poppy"), w.b("dandelion"), w.b("azure_bluet")], 0.3)
    w.anker = (0, 0, 0)
    return w


def bodenstreu_ueber(w, oben, liste, anteil):
    for (x, z), y in oben.items():
        if w.P.name(w.hole(x, y, z) or 0) == "minecraft:grass_block" and w.frei(x, y + 1, z) and w.rng.random() < anteil:
            w.setze(x, y + 1, z, liste[int(w.rng.random() * len(liste))])


def wurzelfelsen(seed, groesse=1):
    """Ein alter Baum thront auf einem Felsen und umklammert ihn mit seinen Wurzeln."""
    from baeume import eiche, schwarzeiche
    w = neue_welt(seed)
    R = [5, 9][groesse]
    rs = Rauschen(w, 3)
    stein = [w.b("stone"), w.b("andesite"), w.b("mossy_cobblestone"), w.b("cobblestone")]
    hoehe = {}
    for x in range(-R - 3, R + 4):
        for y in range(-1, int(R * 1.6) + 3):
            for z in range(-R - 3, R + 4):
                dy = (y - R * 0.3) / (R * 1.15)
                d = math.sqrt((x / R) ** 2 + dy ** 2 + (z / R) ** 2)
                if d < 0.8 + 0.4 * rs(x, y, z):
                    w.setze(x, y, z, stein[int(rs(x * 2, y * 2, z * 2) * 3.99)])
                    hoehe[(x, z)] = max(hoehe.get((x, z), -99), y)
    # Moos auf der Oberseite
    for (x, z), y in hoehe.items():
        if w.rng.random() < 0.55:
            w.setze(x, y, z, w.b("moss_block"))
    top = hoehe.get((0, 0), int(R * 1.2))
    # Baum
    baum = schwarzeiche(seed + 3, 1) if groesse else eiche(seed + 3, 0)
    holz = Holzart(w, "dark_oak" if groesse else "oak")
    pinsel = Pinsel(w, holz)
    einfuegen(w, baum, 0, top, 0)
    # Wurzeln, die über die Felsoberfläche nach unten kriechen
    for i in range([6, 9][groesse]):
        a = i * 2 * math.pi / [6, 9][groesse] + w.rng.random() * 0.4
        r = 0.0
        letzte = None
        while r < R + 6:
            r += 0.4
            a += (w.rng.random() - 0.5) * 0.08
            x, z = int(round(math.cos(a) * r)), int(round(math.sin(a) * r))
            y = hoehe.get((x, z), -1) + 1
            if letzte is not None and abs(y - letzte[1]) > 1:
                for yy in range(min(y, letzte[1]), max(y, letzte[1]) + 1):
                    pinsel.zelle(letzte[0], yy, letzte[2], "y")
            dicke = max(0, int((1 - r / (R + 6)) * [1.6, 2.4][groesse]))
            for dx in range(-dicke // 2, dicke // 2 + 1):
                for dz in range(-dicke // 2, dicke // 2 + 1):
                    yy = hoehe.get((x + dx, z + dz), -1) + 1
                    pinsel.zelle(x + dx, yy, z + dz, "x" if abs(math.cos(a)) > abs(math.sin(a)) else "z")
            letzte = (x, y, z)
            if y <= 0 and r > R + 2:
                break
    haengende_ranken(w, set(stein) | {w.b("moss_block")}, 0.04, 6, min_y=1)
    return w


SPEKTAKULAER = {
    "weltenbaum": ("Weltenbaum", weltenbaum),
    "sakura_riese": ("Sakura-Riese", sakura_riese),
    "drachenbaum": ("Drachenbaum", drachenbaum),
    "baobab": ("Baobab", baobab),
    "gespensterbaum": ("Gespensterbaum", gespensterbaum),
    "riesenpilz_rot": ("Riesenpilz rot", lambda s, g: riesenpilz(s, g, "red")),
    "riesenpilz_braun": ("Riesenpilz braun", lambda s, g: riesenpilz(s, g, "brown")),
    "karmesin_riese": ("Karmesin-Riese", lambda s, g: netherriese(s, g, "crimson")),
    "wirr_riese": ("Wirr-Riese", lambda s, g: netherriese(s, g, "warped")),
    "schwebende_insel": ("Schwebende Insel", schwebende_insel),
    "wurzelfelsen": ("Wurzelfelsen", wurzelfelsen),
}

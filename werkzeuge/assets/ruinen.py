"""Überwucherte Ruinen: Torbogen, Turm, Säulengang, Tempel, Brücke, Brunnen.

Alle Funktionen nehmen (seed, groesse) mit groesse 0 = mittel, 1 = groß.
"""

from __future__ import annotations

import math

from baeume import azaleenbaum, birke, eiche
from lib import Rauschen, Welt, Ziegel, einfuegen, geroell, laub, ueberwuchern, zerfall


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _boden(w: Welt, z: Ziegel, x0, z0, x1, z1, anteil=0.75):
    """Alter Plattenboden mit Lücken auf Höhe 0."""
    for x in range(x0, x1 + 1):
        for zz in range(z0, z1 + 1):
            if w.rng.random() < anteil:
                w.setze(x, 0, zz, z(0.1))


def _saeule(w: Welt, z: Ziegel, x, zz, h, dick=1, y0=1):
    """Säule mit Sockel und Kapitell. dick=1 → 1x1, dick=3 → 3x3 mit abgeschrägten Ecken."""
    if dick == 1:
        for y in range(y0, y0 + h):
            w.setze(x, y, zz, z())
        for dx, dz, f in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
            w.setze(x + dx, y0, zz + dz, z.treppe(f, w.rng.random() < 0.4), ueberschreiben=False)
            w.setze(x + dx, y0 + h - 1, zz + dz, z.treppe(f, w.rng.random() < 0.4, "top"), ueberschreiben=False)
    else:
        for y in range(y0, y0 + h):
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    ecke = dx != 0 and dz != 0
                    if ecke and y0 < y < y0 + h - 1:
                        continue
                    w.setze(x + dx, y, zz + dz, w.b("chiseled_stone_bricks") if (y in (y0, y0 + h - 1) and not ecke) and
                            w.rng.random() < 0.3 else z())


def torbogen(seed, groesse=1):
    """Freistehender Torbogen mit eingestürztem Pfeiler und Schutt."""
    w = _welt(seed)
    z = Ziegel(w, moos=0.4)
    breite = [7, 11][groesse]
    hoehe = [9, 14][groesse]
    tiefe = [3, 4][groesse]
    p = [2, 3][groesse]
    halb = breite // 2 + p
    for x in range(-halb, halb + 1):
        for zz in range(0, tiefe):
            innen = abs(x) <= breite // 2
            if not innen:
                for y in range(1, hoehe + 1):
                    w.setze(x, y, zz, z())
            else:
                # halbrunder Bogen
                r = breite / 2 + 0.5
                bogen_y = hoehe - r + math.sqrt(max(0, r * r - x * x)) + 0.5
                for y in range(int(bogen_y), hoehe + 3):
                    w.setze(x, y, zz, z())
    # Gesims und Zinnen
    for x in range(-halb - 1, halb + 2):
        for zz in (-1, tiefe):
            w.setze(x, hoehe + 2, zz, z.treppe("north" if zz < 0 else "south", True, "top"))
        if x % 2 == 0:
            for zz in range(0, tiefe):
                w.setze(x, hoehe + 3, zz, z())
    rs = Rauschen(w, 4)
    zerfall(w, z.alle, rs, hoehe + 3, staerke=0.3)
    # eine Seite deutlich stärker eingestürzt
    seite = 1 if w.rng.random() < 0.5 else -1
    for (x, y, zz) in [p for p in list(w.bloecke) if p[0] * seite > breite // 2 - 1]:
        if y > hoehe * (0.45 + 0.45 * rs(x, 0, zz)):
            w.bloecke.pop((x, y, zz), None)
    geroell(w, z, seite * (halb + 2), tiefe / 2 + 1, [3, 4.5][groesse], hoehe=[2, 3][groesse])
    geroell(w, z, -seite * (halb - 1), tiefe + 2, 2, hoehe=1.2)
    ueberwuchern(w, z, ranken=0.45, moos_oben=0.6)
    if groesse:
        einfuegen(w, azaleenbaum(seed + 1, 0), -seite * (halb + 3), 0, -3)
    return w


def turm(seed, groesse=1):
    """Runder Wachturm, an einer Seite aufgerissen, mit Fensterschlitzen und Resten von Zwischenböden."""
    w = _welt(seed)
    z = Ziegel(w, moos=0.35)
    R = [4, 6][groesse]
    H = [16, 26][groesse]
    rs = Rauschen(w, 5)
    riss = w.rng.random() * 2 * math.pi
    holz = w.b("spruce_planks")
    for x in range(-R - 1, R + 2):
        for zz in range(-R - 1, R + 2):
            d = math.hypot(x, zz)
            if d > R + 0.5:
                continue
            wand = d > R - 1.5
            ang = math.atan2(zz, x)
            abstand = abs((ang - riss + math.pi) % (2 * math.pi) - math.pi)
            # Höhe der Mauer: am Riss niedrig, gegenüber voll
            h = H * (0.25 + 0.75 * min(1, abstand / 1.6)) * (0.85 + 0.3 * rs(x, 0, zz))
            for y in range(0, int(h) + 1):
                if wand:
                    fenster = (y % 6 == 4 or y % 6 == 5) and abs(round(ang * 4 / math.pi) - ang * 4 / math.pi) < 0.08
                    if not fenster:
                        w.setze(x, y, zz, z())
                elif y == 0:
                    w.setze(x, y, zz, z(0.2))
                elif y % 7 == 0 and rs(x, y, zz) > 0.45 and y < h - 1:
                    w.setze(x, y, zz, holz)
    # Zinnenkranz an der höchsten Stelle
    for x in range(-R - 1, R + 2):
        for zz in range(-R - 1, R + 2):
            d = math.hypot(x, zz)
            if R - 0.5 < d <= R + 0.5:
                ang = math.atan2(zz, x)
                abstand = abs((ang - riss + math.pi) % (2 * math.pi) - math.pi)
                if abstand > 2.2:
                    top = max([y for (a, y, c) in w.bloecke if a == x and c == zz] or [0])
                    if (x + zz) % 2 == 0:
                        w.setze(x, top + 1, zz, z())
    zerfall(w, z.alle, rs, H, staerke=0.25, boden=2)
    geroell(w, z, math.cos(riss) * (R + 3), math.sin(riss) * (R + 3), [3.5, 5][groesse], hoehe=[2.5, 3.5][groesse])
    ueberwuchern(w, z, ranken=0.5, moos_oben=0.6, max_ranke=10)
    if groesse:
        einfuegen(w, birke(seed + 2, 0), int(math.cos(riss + 0.6) * (R + 4)), 0, int(math.sin(riss + 0.6) * (R + 4)))
    return w


def saeulengang(seed, groesse=1):
    """Doppelte Säulenreihe mit teilweise erhaltenem Gebälk und umgestürzten Säulentrommeln."""
    w = _welt(seed)
    z = Ziegel(w, moos=0.35)
    n = [5, 8][groesse]
    abstand = 4
    h = [7, 10][groesse]
    breite = [5, 7][groesse]
    laenge = (n - 1) * abstand
    _boden(w, z, -2, -breite // 2 - 2, laenge + 2, breite // 2 + 2)
    rs = Rauschen(w, 6)
    for i in range(n):
        x = i * abstand
        for zz in (-breite // 2, breite // 2):
            erhalten = rs(x, 0, zz) + 0.25
            hh = h if erhalten > 0.55 else int(h * (0.25 + erhalten))
            _saeule(w, z, x, zz, hh, 3 if groesse else 1)
            if hh == h:
                # Architrav zur nächsten Säule
                if i < n - 1 and rs(x + 2, h, zz) > 0.4:
                    for xx in range(x, x + abstand + 1):
                        for dz in ((-1, 0, 1) if groesse else (0,)):
                            w.setze(xx, h + 1, zz + dz, z())
                # Querbalken
                if zz < 0 and rs(x, h, 0) > 0.5:
                    for zq in range(-breite // 2, breite // 2 + 1):
                        w.setze(x, h + 1, zq, z())
            else:
                # umgestürzte Trommel daneben
                richtung = 1 if w.rng.random() < 0.5 else -1
                for k in range(2, 2 + h - hh):
                    w.setze(x + w.rng.integers(-1, 2), 1, zz + richtung * k, z(0.2))
    zerfall(w, z.alle, rs, h + 2, staerke=0.3, boden=2)
    ueberwuchern(w, z, ranken=0.4, moos_oben=0.65)
    return w


def tempel(seed, groesse=1):
    """Tempel auf Stufenpodest: Säulenumgang, Cella mit Tor, eingestürztes Giebeldach, Baum wächst durch."""
    w = _welt(seed)
    z = Ziegel(w, moos=0.4)
    L = [15, 23][groesse]
    B = [11, 15][groesse]
    h = [7, 9][groesse]
    stufen = 3
    # Stufenpodest
    for s in range(stufen):
        rand = stufen - s
        for x in range(-L // 2 - rand, L // 2 + rand + 1):
            for zz in range(-B // 2 - rand, B // 2 + rand + 1):
                w.setze(x, s, zz, z(0.1))
    boden = stufen
    # Säulenumgang
    for x in range(-L // 2, L // 2 + 1, 3):
        for zz in (-B // 2, B // 2):
            _saeule(w, z, x, zz, h, 1, y0=boden)
    for zz in range(-B // 2 + 3, B // 2 - 2, 3):
        for x in (-L // 2, L // 2):
            _saeule(w, z, x, zz, h, 1, y0=boden)
    # Cella
    cx, cz = L // 2 - 3, B // 2 - 3
    for x in range(-cx, cx + 1):
        for zz in range(-cz, cz + 1):
            if abs(x) == cx or abs(zz) == cz:
                tor = x == -cx and abs(zz) <= 1
                for y in range(boden, boden + h):
                    if not (tor and y < boden + 4):
                        w.setze(x, y, zz, z())
    # Gebälk und Giebeldach
    for x in range(-L // 2 - 1, L // 2 + 2):
        for zz in range(-B // 2 - 1, B // 2 + 2):
            w.setze(x, boden + h, zz, z())
    for stufe in range(B // 2 + 2):
        y = boden + h + 1 + stufe
        for x in range(-L // 2 - 1, L // 2 + 2):
            for zz, f in ((-B // 2 - 1 + stufe, "south"), (B // 2 + 1 - stufe, "north")):
                w.setze(x, y, zz, z.treppe(f, w.rng.random() < 0.5))
            for zz in range(-B // 2 + stufe, B // 2 - stufe + 1):
                if x in (-L // 2 - 1, L // 2 + 1):
                    w.setze(x, y, zz, z())
    rs = Rauschen(w, 5)
    oben = boden + h + B // 2 + 3
    zerfall(w, z.alle | {w.b("mossy_stone_brick_stairs", facing=f, half="bottom", shape="straight",
                                waterlogged=False) for f in ("north", "south")}
            | {w.b("stone_brick_stairs", facing=f, half="bottom", shape="straight", waterlogged=False)
               for f in ("north", "south")}, rs, oben, staerke=0.55, boden=boden + 2)
    # Dach über einer Hälfte ganz eingestürzt
    for p in [p for p in list(w.bloecke) if p[0] > L // 6 and p[1] > boden + h - 1]:
        if rs(p[0], 50, p[2]) > 0.3:
            del w.bloecke[p]
    geroell(w, z, L // 2 + 2, B // 3, 3.5, hoehe=3)
    geroell(w, z, 2, 0, 2.5, hoehe=1.5)
    ueberwuchern(w, z, ranken=0.5, moos_oben=0.65, max_ranke=8)
    # Baum wächst aus dem eingestürzten Teil
    baum = eiche(seed + 4, 0) if groesse else azaleenbaum(seed + 4, 1)
    einfuegen(w, baum, L // 4 + 1, boden, 0)
    return w


def bruecke(seed, groesse=1):
    """Steinbrücke mit Bögen über eine Schlucht, ein Bogen eingestürzt."""
    w = _welt(seed)
    z = Ziegel(w, moos=0.35)
    boegen = [2, 3][groesse]
    spann = [7, 9][groesse]
    pfeiler = 3
    h = [9, 13][groesse]
    breite = 4
    L = boegen * (spann + pfeiler) + pfeiler
    rs = Rauschen(w, 4)
    kaputt = int(w.rng.integers(0, boegen)) if boegen > 1 else -1
    for x in range(L):
        k = x % (spann + pfeiler)
        ist_pfeiler = k < pfeiler
        bogen_nr = x // (spann + pfeiler)
        for zz in range(breite):
            if ist_pfeiler:
                for y in range(-3, h + 1):
                    w.setze(x, y, zz, z())
            else:
                u = k - pfeiler - (spann - 1) / 2
                r = spann / 2
                bogen_y = h - 3 - r + math.sqrt(max(0, r * r - u * u)) + 1.5
                if bogen_nr == kaputt and abs(u) < r * 0.75:
                    continue
                for y in range(int(bogen_y), h + 1):
                    w.setze(x, y, zz, z())
        # Brüstung
        if not (bogen_nr == kaputt and not ist_pfeiler and abs(k - pfeiler - (spann - 1) / 2) < spann * 0.4):
            for zz in (-1, breite):
                w.setze(x, h + 1, zz, z() if x % 3 else w.b("stone_brick_wall", **{
                    "east": "low", "west": "low", "north": "none", "south": "none", "up": True,
                    "waterlogged": False}))
                w.setze(x, h, zz, z())
    zerfall(w, z.alle, rs, h + 2, staerke=0.3, boden=h - 2)
    # Schutt unter dem eingestürzten Bogen
    if kaputt >= 0:
        mx = kaputt * (spann + pfeiler) + pfeiler + spann // 2
        geroell(w, z, mx, breite / 2, spann * 0.4, hoehe=2.5)
    ueberwuchern(w, z, ranken=0.55, moos_oben=0.6, max_ranke=9)
    w.anker = (L // 2, 0, breite // 2)
    return w


def brunnen(seed, groesse=1):
    """Runder Zierbrunnen mit Wasserbecken, Mittelsäule und Laternen – halb verfallen."""
    w = _welt(seed)
    z = Ziegel(w, moos=0.45)
    R = [4, 6][groesse]
    wasser = w.b("water", level=0)
    for x in range(-R - 3, R + 4):
        for zz in range(-R - 3, R + 4):
            d = math.hypot(x, zz)
            if d <= R + 2.5 and w.rng.random() < 0.8:
                w.setze(x, 0, zz, z(0.1))
            if R - 0.5 < d <= R + 0.5:
                w.setze(x, 1, zz, z())
                if w.rng.random() < 0.6:
                    w.setze(x, 2, zz, z.stufe(w.rng.random() < 0.5))
            elif d <= R - 0.5:
                w.setze(x, 0, zz, z())
                w.setze(x, 1, zz, wasser)
    hs = [5, 8][groesse]
    for y in range(1, hs + 1):
        w.setze(0, y, 0, z())
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        w.setze(dx, hs, dz, w.b("stone_brick_slab", type="top", waterlogged=False))
        w.setze(dx, hs - 1, dz, w.b("chain", axis="y", waterlogged=False))
        w.setze(dx, hs - 2, dz, w.b("lantern", hanging=True, waterlogged=False))
    w.setze(0, hs + 1, 0, w.b("chiseled_stone_bricks"))
    lilien = w.b("lily_pad")
    for (x, y, zz), b in list(w.bloecke.items()):
        if b == wasser and w.rng.random() < 0.12 and w.frei(x, 2, zz):
            w.setze(x, 2, zz, lilien)
    ueberwuchern(w, z, ranken=0.3, moos_oben=0.5)
    return w


RUINEN = {
    "torbogen": ("Torbogen", torbogen),
    "turm": ("Turmruine", turm),
    "saeulengang": ("Säulengang", saeulengang),
    "tempel": ("Tempelruine", tempel),
    "bruecke": ("Brückenruine", bruecke),
    "brunnen": ("Brunnen", brunnen),
}

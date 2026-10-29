"""Schwebende Strukturen II – zwanzig weitere Wunder in der Luft: Himmelstempel, Wolkenbibliothek, Wasserfallfels,
Schwebegarten, Wolkenkloster, Ringsphäre, Kristallschwarm, umgekehrte Pyramide, Luftburg, Himmelsleuchtturm,
Wolkentreppe, Miniplanet, Trümmerfeld, Wurzelinsel, Schwebedorf, Ballon-Insel, Himmelssee, Obelisk mit Orbit,
Kettenfels und Sanduhr-Inseln. Der Anker liegt am Boden unter der Insel."""

from __future__ import annotations

import math

import numpy as np

import pracht as P
import wald2
from flora import _r
from himmelsstadt import Schema, _fertig, _welt, haengebruecke_teil, insel, laternenpfahl, turm, unterseite
from lib import Rauschen, einfuegen
from pracht import Mat
from riesenbogen import fantasiehaus, haengelaterne

RG = [8, 12, 18, 28]
TG = [10, 14, 20, 30]
U = [0.6, 1.0, 1.7, 2.8]


def basis(seed, g, rf=1.0, flach=0.6, extras=True):
    w = _welt(seed)
    sch = Schema(w)
    rs = Rauschen(w, 4)
    R = RG[g] * rf
    T = TG[g] * rf
    top = int(T * 1.9) + [10, 14, 18, 24][g]
    oben = insel(w, sch, rs, 0, top, 0, R, T, flach=flach, extras=extras)
    return w, sch, rs, R, T, top, oben


def stil_himmel(w):
    return P.Stil(w, wand="kalkstein", sockel="graustein", gesims="stone_brick", dach="kupfer", holz="dark_oak")


def schwebender_tempel(seed, g=2):
    """Himmelstempel: auf einer Insel steht ein runder Säulentempel mit Kupferkuppel, eine Freitreppe führt zur
    Kante, wo zwei Wächtersäulen mit Feuerschalen stehen."""
    w, sch, rs, R, T, top, oben = basis(seed, g)
    u = U[g]
    r = _r(R * 0.45)
    y0 = top + 1
    for x in range(-r - 1, r + 2):
        for z in range(-r - 1, r + 2):
            if math.hypot(x, z) <= r + 1:
                w.setze(x, y0, z, w.b("smooth_quartz" if (x + z) % 2 else "calcite"))
    H = _r(6 * u + 3)
    for k in range(int(r * 2.2)):
        a = k / int(r * 2.2) * 6.283
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        for y in range(y0 + 1, y0 + H + 1):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    for x in range(-r - 1, r + 2):
        for z in range(-r - 1, r + 2):
            for y in range(0, r + 2):
                d = math.sqrt(x * x + (y * 1.1) ** 2 + z * z)
                if r - 0.2 < d <= r + 1:
                    w.setze(x, y0 + H + 1 + y, z, sch.dach(1 + 2.5 * y / r, x, y, z))
    w.setze(0, y0 + 1, 0, w.b("lodestone"))
    w.setze(0, y0 + 2, 0, w.b("end_rod", facing="up"))
    for x in (-2, 2):
        for y in range(y0 + 1, y0 + 4):
            w.setze(x, y, round(R * 0.8), w.b("chiseled_quartz_block" if y == y0 + 3 else "quartz_pillar",
                                             **({} if y == y0 + 3 else {"axis": "y"})))
        w.setze(x, y0 + 4, round(R * 0.8), w.b("campfire", lit=True, signal_fire=False, facing="north",
                                               waterlogged=False))
    return _fertig(w, sch)


def wolkenbibliothek(seed, g=2):
    """Wolkenbibliothek: ein hoher Bücherturm mit Bogenfenstern auf einer Insel, ringsum schwebende Bücherregal-
    Brocken, Lesepulte unter Laternen und weiße Wolkenbänke."""
    w, sch, rs, R, T, top, oben = basis(seed, g)
    u = U[g]
    st = stil_himmel(w)
    a = _r(R * 0.35)
    P.gebaeude(w, st, -a, -a, a, a, y0=top + 1, etagen=2 + g // 2, eh=5, dach="walm", sockel_h=1, gauben=True,
               kamine=0, steil=True)
    for k in range(3 + g):
        ang = k * 2.4
        d = R * (0.9 + 0.3 * (k % 2))
        x, z = round(math.cos(ang) * d), round(math.sin(ang) * d)
        y = top + 4 + (k % 3) * 3
        for dx in range(2):
            for dy in range(3):
                w.setze(x + dx, y + dy, z, w.b("bookshelf"))
        w.setze(x, y - 1, z, w.b("dark_oak_slab", type="top", waterlogged=False))
    for k in range(int(6 * u)):
        ang = w.rng.random() * 6.283
        d = R * (1.2 + w.rng.random() * 0.5)
        x, z = round(math.cos(ang) * d), round(math.sin(ang) * d)
        for dx in range(-2, 3):
            for dz in range(-1, 2):
                if abs(dx) + abs(dz) < 3:
                    w.setze(x + dx, top - 2 - k % 4, z + dz, w.b("white_wool"))
    for x in (-a - 2, a + 2):
        w.setze(x, top + 1, 0, w.b("lectern", facing="north", has_book=True, powered=False))
        laternenpfahl(w, x, top, 2)
    return _fertig(w, sch)


def wasserfallfels(seed, g=2):
    """Wasserfallfels: eine hohe, schmale Felsinsel, aus deren Mitte drei Wasserfälle in die Tiefe stürzen,
    Moos, Farne und ein kleiner Steinschrein auf der Spitze."""
    w, sch, rs, R, T, top, oben = basis(seed, g, rf=0.75, extras=False)
    u = U[g]
    H = _r(10 * u + 4)
    for x in range(-int(R * 0.5), int(R * 0.5) + 1):
        for z in range(-int(R * 0.5), int(R * 0.5) + 1):
            d = math.hypot(x, z) / (R * 0.5)
            if d <= 1:
                h = int(H * (1 - d ** 2) * (0.8 + 0.3 * rs(x, 5, z)))
                for y in range(top, top + h + 1):
                    w.setze(x, y, z, sch.fels(2 + 2 * (y - top) / H, x, y, z) if y < top + h else sch.moos)
    peak = top + H
    for k in range(3):
        ang = k * 2.094
        for d in range(0, int(R) + 2):
            x, z = round(math.cos(ang) * d), round(math.sin(ang) * d)
            ys = [y for y in range(top, peak + 2) if (x, y, z) in w.bloecke]
            yy = max(ys) if ys else top
            w.setze(x, yy, z, w.b("water", level=0))
        x, z = round(math.cos(ang) * (R + 2)), round(math.sin(ang) * (R + 2))
        w.vorschau_extra = getattr(w, "vorschau_extra", {})
        for y in range(1, top):
            w.vorschau_extra[(x, y, z)] = w.b("water", level=0)
    for (x, z) in ((0, 0),):
        w.setze(x, peak + 1, z, w.b("chiseled_stone_bricks"))
        w.setze(x, peak + 2, z, w.b("lantern", hanging=False, waterlogged=False))
    return _fertig(w, sch, pflanzen=0.5)


def schwebegarten(seed, g=2):
    """Schwebegarten: eine Insel als Ziergarten – Heckenrondell, Blumenbeete in Mustern, ein Pavillon mit Kuppel,
    ein Teich mit Brücke und Kirschbäume an den Rändern."""
    w, sch, rs, R, T, top, oben = basis(seed, g, flach=0.8)
    u = U[g]
    y = top
    for (x, z), yo in oben.items():
        d = math.hypot(x, z)
        if d < R * 0.75 and yo == top:
            ring = int(d / 2.2) % 3
            if ring == 1:
                w.setze(x, y + 1, z, w.b(["red_tulip", "allium", "cornflower", "pink_tulip", "oxeye_daisy"]
                                         [(x * 7 + z * 3) % 5]))
            elif ring == 2 and abs(x) > 1 and abs(z) > 1:
                w.setze(x, y + 1, z, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
            else:
                w.setze(x, y, z, w.b("gravel" if (x + z) % 3 else "cobblestone"))
    for k in range(8):
        a = k / 8 * 6.283
        x, z = round(math.cos(a) * 2), round(math.sin(a) * 2)
        for yy in range(y + 1, y + 4):
            w.setze(x, yy, z, w.b("stripped_birch_log", axis="y"))
    for x in range(-3, 4):
        for z in range(-3, 4):
            for yy in range(0, 3):
                d = math.sqrt(x * x + (yy * 1.3) ** 2 + z * z)
                if 2.0 < d <= 3.1:
                    w.setze(x, y + 4 + yy, z, sch.dach(1.5 + yy, x, yy, z))
    for k in range(3 + g):
        a = k * 2.2 + 0.5
        d = R * 0.82
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if (x, z) in oben:
            einfuegen(w, wald2.kirschbaum(seed + k, H=_r(5 * u + 3)), x, oben[(x, z)], z)
    return _fertig(w, sch, pflanzen=0.2)


def wolkenkloster(seed, g=3):
    """Wolkenkloster: Gebäude mit geschwungenen Dächern auf drei gestaffelten Felsinseln, verbunden durch
    Hängebrücken, Gebetsfahnen an Seilen, ein Glockenturm auf der höchsten Insel."""
    w = _welt(seed)
    sch = Schema(w)
    rs = Rauschen(w, 4)
    u = U[g]
    Rb = RG[g] * 0.55
    Tb = TG[g] * 0.6
    top0 = int(Tb * 1.9) + 10
    inseln = [(-Rb * 1.6, top0, 0), (Rb * 1.4, top0 + 5, -Rb * 0.6), (0, top0 + 11, Rb * 1.5)]
    st = P.Stil(w, wand="putz", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="dark_oak")
    for i, (cx, t, cz) in enumerate(inseln):
        insel(w, sch, rs, cx, t, cz, Rb, Tb, extras=False)
        a = _r(Rb * 0.45)
        if i < 2:
            P.gebaeude(w, st, int(cx) - a, int(cz) - a + 1, int(cx) + a, int(cz) + a - 1, y0=t + 1, etagen=1, eh=4,
                       dach="walm", sockel_h=1, gauben=False, kamine=0)
        else:
            P.turm(w, st, int(cx), int(cz), t + 1, _r(10 * u + 4), _r(1.5 * u + 1), form="eckig", dach="pyramide",
                   krone=False, fenster=4)
    for (a, b) in zip(inseln, inseln[1:]):
        n = 20
        for i in range(n + 1):
            t = i / n
            x = a[0] + (b[0] - a[0]) * t
            z = a[2] + (b[2] - a[2]) * t
            y = a[1] + (b[1] - a[1]) * t + 1 - 2 * 4 * t * (1 - t)
            for dz in (-1, 0, 1):
                w.setze(round(x), round(y), round(z) + dz, w.b("dark_oak_planks"), False)
            if i % 2 == 0:
                w.setze(round(x), round(y) + 3, round(z), w.b(["red_wool", "yellow_wool", "blue_wool", "green_wool",
                                                              "white_wool"][i % 5]), False)
    return _fertig(w, sch)


def ringsphaere(seed, g=2):
    """Ringsphäre: über einer kleinen Insel schweben drei ineinander verschränkte, schräg gestellte Steinringe mit
    goldenen Einlagen um eine leuchtende Kugel."""
    w, sch, rs, R, T, top, oben = basis(seed, g, rf=0.7)
    u = U[g]
    cy = top + RG[g] * 0.9 + 4
    Rr = RG[g] * 0.75
    for k, (neig, dreh) in enumerate(((0.5, 0.0), (0.5, 2.094), (0.5, 4.189))):
        n = int(Rr * 14)
        for i in range(n):
            t = i / n * 6.283
            x, y, z = math.cos(t) * Rr, math.sin(t) * Rr, 0.0
            y, z = y * math.cos(neig) - z * math.sin(neig), y * math.sin(neig) + z * math.cos(neig)
            x, z = x * math.cos(dreh) - z * math.sin(dreh), x * math.sin(dreh) + z * math.cos(dreh)
            for dd in (0, 0.6):
                w.setze(round(x * (1 - dd / Rr)), round(cy + y), round(z * (1 - dd / Rr)),
                        w.b("gold_block") if i % 9 == 0 else w.b(["polished_andesite", "calcite", "smooth_quartz"][k]))
    for x in range(-3, 4):
        for y in range(-3, 4):
            for z in range(-3, 4):
                if x * x + y * y + z * z <= 2.6 ** 2:
                    w.setze(x, round(cy) + y, z, w.b("sea_lantern" if (x + y + z) % 2 else "glass"))
    return _fertig(w, sch)


def kristallschwarm(seed, g=2):
    """Kristallschwarm: eine Insel, aus deren Unterseite riesige Amethyst- und Glaskristalle nach unten wachsen,
    darüber schweben einzelne Kristallsplitter in einem lockeren Ring."""
    from kristall import kristall
    w, sch, rs, R, T, top, oben = basis(seed, g, rf=0.85, extras=False)
    u = U[g]
    rng = w.rng
    for k in range(5 + g * 2):
        a = rng.random() * 6.283
        d = rng.random() * R * 0.6
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        kristall(w, (x, top - T * 0.6, z), ((rng.random() - 0.5) * 0.6, -1, (rng.random() - 0.5) * 0.6),
                 (4 + rng.random() * 6) * u, (0.8 + rng.random() * 0.6) * u, art="amethyst")
    for k in range(4 + g * 2):
        a = rng.random() * 6.283
        x, z = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        kristall(w, (x, top + 1, z), ((rng.random() - 0.5) * 0.5, 1, (rng.random() - 0.5) * 0.5),
                 (2 + rng.random() * 4) * u, (0.5 + rng.random() * 0.5) * u, art="amethyst")
    for k in range(10):
        a = k / 10 * 6.283
        x, z = round(math.cos(a) * R * 1.4), round(math.sin(a) * R * 1.4)
        y = top + 3 + int(math.sin(a * 2) * 3)
        w.setze(x, y, z, w.b("amethyst_block"))
        w.setze(x, y + 1, z, w.b("amethyst_cluster", facing="up", waterlogged=False))
    return _fertig(w, sch, pflanzen=0.15)


def umgekehrte_pyramide(seed, g=2):
    """Umgekehrte Pyramide: eine Stufenpyramide aus Sandstein steht auf ihrer Spitze in der Luft, oben eine flache
    Plattform mit Obelisken und goldener Sonnenscheibe, Ranken hängen von den Stufen."""
    w = _welt(seed)
    u = U[g]
    n = _r(7 * u + 4)
    y0 = n * 2 + 12
    M = Mat(w, "sandstein")
    for k in range(n):
        r = k + 1
        y = y0 - (n - k) * 2
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                for dy in (0, 1):
                    w.setze(x, y + dy, z, M(x, y, z, k / n))
    yt = y0
    for x in range(-n, n + 1):
        for z in range(-n, n + 1):
            w.setze(x, yt, z, w.b("smooth_sandstone" if (x + z) % 2 else "cut_sandstone"))
    for (x, z) in ((-n + 1, -n + 1), (n - 1, -n + 1), (-n + 1, n - 1), (n - 1, n - 1)):
        for y in range(yt + 1, yt + 1 + _r(4 * u + 2)):
            w.setze(x, y, z, w.b("chiseled_sandstone" if y % 3 == 0 else "cut_sandstone"))
        w.setze(x, yt + 1 + _r(4 * u + 2), z, w.b("gold_block"))
    for x in range(-2, 3):
        for y in range(0, 5):
            if x * x + (y - 2) ** 2 <= 5:
                w.setze(x, yt + 2 + y, 0, w.b("gold_block" if x * x + (y - 2) ** 2 <= 2 else "orange_stained_glass"))
    from veredeln import bewuchs
    bewuchs(w, moos=0.05, ranken=0.12)
    return w


def luftburg(seed, g=3):
    """Luftburg: eine kleine Burg mit Bergfried, Ringmauer und vier Ecktürmen steht auf einer großen Felsinsel,
    eine lange Kettenbrücke führt zu einem vorgelagerten Wachfelsen."""
    w, sch, rs, R, T, top, oben = basis(seed, g)
    u = U[g]
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="kupfer", holz="dark_oak")
    a = _r(R * 0.55)
    Hm = _r(4 * u + 3)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if abs(x) == a or abs(z) == a:
                for y in range(top + 1, top + Hm + 1):
                    w.setze(x, y, z, st.wand(x, y, z, 0.5))
                if (x + z) % 2 == 0:
                    w.setze(x, top + Hm + 1, z, st.wand(x, 0, z, 0.9))
    for (x, z) in ((-a, -a), (a, -a), (-a, a), (a, a)):
        P.turm(w, st, x, z, top + 1, _r(7 * u + 4), _r(1.4 * u + 1), dach="kegel", krone=True, fenster=4)
    P.turm(w, st, 0, 0, top + 1, _r(14 * u + 6), _r(2.4 * u + 1.5), form="eckig", dach="pyramide", krone=True,
           fenster=5)
    cx = R * 1.7
    insel(w, sch, rs, cx, top - 2, 0, R * 0.3, T * 0.4, extras=False)
    P.turm(w, st, int(cx), 0, top - 1, _r(6 * u + 3), _r(1.2 * u + 1), dach="kegel", krone=False, fenster=4)
    haengebruecke_teil(w, a + 1, top + 1, 0, int(cx - a - 2), durchhang=3)
    return _fertig(w, sch)


def himmelsleuchtturm(seed, g=2):
    """Himmelsleuchtturm: ein rot-weiß geringelter Leuchtturm auf einer schmalen Felsnadel über den Wolken, mit
    Laternenhaus aus Glas, Galerie und einem kleinen Wärterhaus."""
    w, sch, rs, R, T, top, oben = basis(seed, g, rf=0.6)
    u = U[g]
    r = _r(1.8 * u + 1)
    H = _r(16 * u + 6)
    for y in range(top + 1, top + H + 1):
        for x in range(-r - 1, r + 2):
            for z in range(-r - 1, r + 2):
                d = math.hypot(x, z)
                if r - 0.8 < d <= r + 0.4:
                    w.setze(x, y, z, w.b("red_terracotta" if ((y - top) // 3) % 2 else "white_terracotta"))
    yg = top + H
    for x in range(-r - 2, r + 3):
        for z in range(-r - 2, r + 3):
            d = math.hypot(x, z)
            if d <= r + 1.8:
                w.setze(x, yg, z, w.b("dark_oak_planks"))
                if d > r + 0.9:
                    w.setze(x, yg + 1, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                              waterlogged=False))
    for y in range(yg + 1, yg + 4):
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                if math.hypot(x, z) <= r + 0.4:
                    rand = math.hypot(x, z) > r - 0.6
                    w.setze(x, y, z, w.b("yellow_stained_glass") if rand else
                            (w.b("sea_lantern") if y == yg + 2 and x == 0 and z == 0 else w.b("glass")))
    for k in range(r + 2):
        for x in range(-r + k, r - k + 1):
            for z in range(-r + k, r - k + 1):
                w.setze(x, yg + 4 + k, z, w.b("red_terracotta"))
    fantasiehaus(w, r + 2, top + 1, -3, B=7, T=5, H=4, stil="kupfer", fundament=2)
    return _fertig(w, sch)


def wolkentreppe(seed, g=2):
    """Wolkentreppe: eine frei schwebende Wendeltreppe aus einzelnen Steinplatten schraubt sich von einer kleinen
    Insel hinauf zu einer höheren Insel mit Torbogen, Wolkenbänke umspielen die Stufen."""
    w, sch, rs, R, T, top, oben = basis(seed, g, rf=0.55, extras=False)
    u = U[g]
    H = _r(18 * u + 8)
    r = 4 * u + 3
    n = H * 2
    for i in range(n):
        a = i * 0.38
        y = top + 1 + i // 2
        x, z = math.cos(a) * r, math.sin(a) * r
        for dx in (0, 1):
            for dz in (0, 1):
                w.setze(round(x) + dx, y, round(z) + dz, w.b("smooth_stone_slab", type="bottom", waterlogged=False)
                        if i % 2 else w.b("polished_andesite"))
        if i % 9 == 0:
            for dx in range(-2, 3):
                w.setze(round(x * 1.5) + dx, y - 2, round(z * 1.5), w.b("white_wool"))
    ex, ez = round(math.cos((n - 1) * 0.38) * r), round(math.sin((n - 1) * 0.38) * r)
    insel(w, sch, rs, ex * 2, top + H + 1, ez * 2, R * 0.5, T * 0.4, extras=False)
    st = P.Stil(w, wand="marmor", sockel="graustein", gesims="quartz", dach="kupfer", holz="dark_oak")
    for y in range(top + H + 2, top + H + 2 + _r(6 * u + 3)):
        for x in (ex * 2 - 2, ex * 2 + 2):
            w.setze(x, y, ez * 2, w.b("quartz_pillar", axis="y"))
    for x in range(ex * 2 - 2, ex * 2 + 3):
        w.setze(x, top + H + 2 + _r(6 * u + 3), ez * 2, w.b("chiseled_quartz_block"))
    return _fertig(w, sch)


def miniplanet(seed, g=2):
    """Miniplanet: eine kugelrunde kleine Welt mit Graskruste, Bäumen, einem Häuschen und einem Ozeanfleck, die
    über einer Felsnadel schwebt, umkreist von einem Ring aus Schnee- und Eisbrocken."""
    w = _welt(seed)
    u = U[g]
    Rp = 6 * u + 4
    cy = Rp + 14
    rn = Rauschen(w, 3)
    for x in range(-int(Rp) - 1, int(Rp) + 2):
        for y in range(-int(Rp) - 1, int(Rp) + 2):
            for z in range(-int(Rp) - 1, int(Rp) + 2):
                d = math.sqrt(x * x + y * y + z * z)
                if d <= Rp:
                    if d > Rp - 1:
                        meer = x > Rp * 0.3 and z > 0
                        b = w.b("water", level=0) if meer and y > 0 else w.b("grass_block", snowy=False) \
                            if y > -Rp * 0.3 else w.b("stone")
                    elif d > Rp - 2.5:
                        b = w.b("dirt")
                    else:
                        b = w.b(["stone", "andesite", "deepslate", "magma_block"][int(rn(x, y, z) * 3.99)])
                    w.setze(x, round(cy) + y, z, b)
    einfuegen(w, wald2.laubbaum(seed, "oak", H=_r(4 * u + 3)), -2, round(cy + Rp), -1)
    einfuegen(w, wald2.fichte(seed + 1, H=_r(4 * u + 3)), 1, round(cy + Rp - 1), -round(Rp * 0.5))
    fantasiehaus(w, -round(Rp * 0.4), round(cy + Rp * 0.8), 1, B=5, T=5, H=3, stil="kupfer", fundament=3)
    n = int(Rp * 10)
    for i in range(n):
        t = i / n * 6.283
        r = Rp * 1.7
        if i % 3:
            w.setze(round(math.cos(t) * r), round(cy + math.sin(t) * r * 0.25), round(math.sin(t) * r),
                    w.b("packed_ice" if i % 5 else "snow_block"))
    for y in range(0, round(cy - Rp)):
        rr = 2.5 * (1 - y / (cy - Rp)) + 0.6
        for x in range(-3, 4):
            for z in range(-3, 4):
                if math.hypot(x, z) <= rr and y < 6:
                    w.setze(x, y, z, w.b("stone"))
    return w


def truemmerfeld(seed, g=2):
    """Trümmerfeld: die Bruchstücke einer zerborstenen Insel schweben auseinandergerissen in der Luft – auf jedem
    ein Teil eines Hauses, einer Mauer oder eines Gartens, verbunden durch Kettenreste."""
    w = _welt(seed)
    sch = Schema(w)
    rs = Rauschen(w, 4)
    u = U[g]
    rng = w.rng
    st = P.Stil(w, wand="kalkstein", sockel="graustein", gesims="stone_brick", dach="kupfer", holz="dark_oak")
    teile = []
    for k in range(5 + g):
        a = k * 2.399
        d = RG[g] * 0.25 * math.sqrt(k + 1) * 1.6
        cx, cz = math.cos(a) * d, math.sin(a) * d
        t = int(TG[g] * 1.4) + 8 + int(rng.random() * 10 * u)
        r = RG[g] * (0.22 + 0.12 * rng.random())
        oben = insel(w, sch, rs, cx, t, cz, r, r * 1.2, extras=False)
        teile.append((cx, t, cz, r))
        if k % 3 == 0:
            for x in range(int(cx - r * 0.5), int(cx + r * 0.5)):
                for y in range(t + 1, t + 4):
                    w.setze(x, y, int(cz), st.wand(x, y, int(cz), 0.5))
        elif k % 3 == 1:
            w.setze(int(cx), t + 1, int(cz), w.b("chest", facing="south", type="single", waterlogged=False))
            laternenpfahl(w, int(cx) + 1, t, int(cz))
    for (a, b) in zip(teile, teile[1:]):
        if rng.random() < 0.6:
            n = 10
            for i in range(n + 1):
                tt = i / n
                w.setze(round(a[0] + (b[0] - a[0]) * tt), round(a[1] + (b[1] - a[1]) * tt - 3 * 4 * tt * (1 - tt)),
                        round(a[2] + (b[2] - a[2]) * tt), w.b("chain", axis="x", waterlogged=False), False)
    return _fertig(w, sch)


def wurzelinsel(seed, g=2):
    """Wurzelinsel: ein uralter Baum hält mit seinen Wurzeln einen kleinen Felsklumpen umschlungen, die Wurzeln
    hängen meterweit in die Tiefe, die Krone breitet sich über der Insel aus."""
    w, sch, rs, R, T, top, oben = basis(seed, g, rf=0.55, extras=False)
    u = U[g]
    from baeume import eiche
    b = eiche(seed, min(2, g))
    einfuegen(w, b, 0, top, 0)
    rng = w.rng
    for k in range(int(10 * u) + 4):
        a = rng.random() * 6.283
        r = R * (0.5 + rng.random() * 0.5)
        x, z = math.cos(a) * r, math.sin(a) * r
        L = int(T * (0.8 + rng.random()))
        for i in range(L):
            yy = top - i
            xx = round(x * (1 + i / L * 0.3) + math.sin(i * 0.3) * 0.8)
            zz = round(z * (1 + i / L * 0.3))
            w.setze(xx, yy, zz, w.b("oak_wood" if i < L * 0.6 else "mangrove_roots", axis="y")
                    if i < L * 0.6 else w.b("mangrove_roots", waterlogged=False), False)
    return _fertig(w, sch)


def schwebedorf(seed, g=3):
    """Schwebedorf: eine große Insel mit fünf kleinen Fachwerkhäusern um einen Dorfplatz mit Brunnen und Maibaum,
    gewundene Wege, Gärten und Zäune, am Rand eine Aussichtsplattform."""
    w, sch, rs, R, T, top, oben = basis(seed, g, flach=0.8)
    u = U[g]
    pools = ["fachwerk_rot", "fachwerk_ocker", "putz_blau", "holz_dunkel", "kalk_kupfer"]
    from haeuser import HAUSPOOL
    for k in range(5):
        a = k / 5 * 6.283 + 0.3
        d = R * 0.55
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        st = P.Stil(w, **HAUSPOOL[pools[k]])
        P.gebaeude(w, st, x - 2, z - 2, x + 2, z + 2, y0=top + 1, etagen=1, eh=4, dach="sattel", sockel_h=0,
                   gauben=False, kamine=1, tuer="north" if z > 0 else "south")
    for x in range(-3, 4):
        for z in range(-3, 4):
            if x * x + z * z <= 9:
                w.setze(x, top, z, w.b("cobblestone" if (x + z) % 2 else "stone_bricks"))
    for y in range(top + 1, top + 1 + _r(7 * u + 4)):
        w.setze(0, y, 0, w.b("stripped_spruce_log", axis="y"))
    for k, f in enumerate(["red_wool", "yellow_wool", "blue_wool", "green_wool"]):
        w.setze(round(math.cos(k * 1.57)), top + _r(7 * u + 4) - 1, round(math.sin(k * 1.57)), w.b(f))
    return _fertig(w, sch, pflanzen=0.3)


def balloninsel(seed, g=2):
    """Ballon-Insel: eine kleine Felsinsel mit Hütte wird von vier riesigen, bunt gestreiften Ballons an Seilen
    getragen, ein Steuerrad und Sandsäcke am Rand."""
    w, sch, rs, R, T, top, oben = basis(seed, g, rf=0.6, extras=False)
    u = U[g]
    fantasiehaus(w, -3, top + 1, -2, B=7, T=5, H=4, stil="kupfer", fundament=2)
    farben = [("red_wool", "white_wool"), ("yellow_wool", "orange_wool"), ("blue_wool", "light_blue_wool"),
              ("lime_wool", "green_wool")]
    for k in range(4):
        a = k / 4 * 6.283 + 0.785
        bx, bz = math.cos(a) * R * 1.0, math.sin(a) * R * 1.0
        by = top + 10 + 6 * u
        rb = 3 * u + 2
        for x in range(-int(rb) - 1, int(rb) + 2):
            for y in range(-int(rb * 1.2) - 1, int(rb * 1.2) + 2):
                for z in range(-int(rb) - 1, int(rb) + 2):
                    d = (x / rb) ** 2 + (y / (rb * 1.2)) ** 2 + (z / rb) ** 2
                    if 0.75 < d <= 1:
                        f = farben[k][int((math.atan2(z, x) + 3.15) * 2) % 2]
                        w.setze(round(bx) + x, round(by) + y, round(bz) + z, w.b(f))
        from flora import linie
        linie(w, (bx, by - rb * 1.2, bz), (bx * 0.5, top + 1, bz * 0.5), w.b("chain", axis="y", waterlogged=False))
    for k in range(4):
        w.setze(round(R * 0.6) - k, top + 1, round(R * 0.4), w.b("brown_wool" if k % 2 else "barrel",
                                                                 **({} if k % 2 else {"facing": "up", "open": False})))
    return _fertig(w, sch)


def himmelssee(seed, g=2):
    """Himmelssee: eine schüsselförmige Felsinsel trägt einen klaren See, aus dem an einer Stelle das Wasser über
    den Rand in die Tiefe fällt, Schilf, Seerosen und ein Bootssteg."""
    w, sch, rs, R, T, top, oben = basis(seed, g, extras=False)
    for (x, z), yo in oben.items():
        d = math.hypot(x, z) / R
        if d < 0.65:
            tief = int(3 * (1 - d / 0.65)) + 1
            for y in range(yo - tief + 1, yo + 1):
                w.setze(x, y, z, w.b("water", level=0))
            w.setze(x, yo - tief, z, w.b("clay" if (x + z) % 3 else "sand"))
            if w.rng.random() < 0.05:
                w.setze(x, yo + 1, z, w.b("lily_pad"))
        elif d < 0.75:
            if w.rng.random() < 0.4:
                w.setze(x, yo + 1, z, w.b("sugar_cane", age=0))
                w.setze(x, yo + 2, z, w.b("sugar_cane", age=0))
    for k in range(int(R * 0.4)):
        w.setze(int(R * 0.35) + k, top + 1, 0, w.b("spruce_slab", type="bottom", waterlogged=False))
    x = int(R) + 1
    w.vorschau_extra = {}
    for y in range(1, top + 1):
        w.vorschau_extra[(x, y, 0)] = w.b("water", level=0)
    for k in range(int(R * 0.65), int(R) + 2):
        w.setze(k, top, 0, w.b("water", level=0))
    return _fertig(w, sch)


def orbit_obelisk(seed, g=2):
    """Obelisk mit Orbit: ein schwarzer Obelisk mit leuchtenden Runenbändern ragt aus einer Insel, um ihn kreisen
    auf zwei Bahnen kleine Felsbrocken mit Kristallen."""
    w, sch, rs, R, T, top, oben = basis(seed, g, rf=0.7, extras=False)
    u = U[g]
    H = _r(18 * u + 8)
    for y in range(top + 1, top + H + 1):
        b = max(1, round(2 * u * (1 - (y - top) / H * 0.6)))
        for x in range(-b, b + 1):
            for z in range(-b, b + 1):
                rune = (y - top) % 6 == 0
                w.setze(x, y, z, w.b("crying_obsidian" if rune and (x + z) % 2 else
                                     "polished_blackstone" if not rune else "obsidian"))
    w.setze(0, top + H + 1, 0, w.b("end_rod", facing="up"))
    for bahn, (r, h) in enumerate(((R * 1.2, top + H * 0.4), (R * 1.7, top + H * 0.75))):
        for k in range(6 + bahn * 2):
            a = k / (6 + bahn * 2) * 6.283 + bahn
            cx, cz = math.cos(a) * r, math.sin(a) * r
            y = h + math.sin(a * 2) * 2
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    if abs(dx) + abs(dz) < 2:
                        w.setze(round(cx) + dx, round(y), round(cz) + dz, sch.fels(2, 0, 0, 0))
            w.setze(round(cx), round(y) + 1, round(cz), w.b("amethyst_cluster", facing="up", waterlogged=False))
    return _fertig(w, sch)


def kettenfels(seed, g=2):
    """Kettenfels: eine schwebende Felsinsel wird von vier gewaltigen Eisenketten an steinernen Ankerblöcken im
    Boden festgehalten, oben steht ein Wachturm."""
    w, sch, rs, R, T, top, oben = basis(seed, g, rf=0.8, extras=False)
    u = U[g]
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="dark_oak")
    P.turm(w, st, 0, 0, top + 1, _r(10 * u + 5), _r(2 * u + 1.5), dach="kegel", krone=True, fenster=4)
    for k in range(4):
        a = k / 4 * 6.283 + 0.785
        ax, az = math.cos(a) * R * 1.9, math.sin(a) * R * 1.9
        for x in range(-2, 3):
            for z in range(-2, 3):
                for y in range(0, 4):
                    w.setze(round(ax) + x, y, round(az) + z, w.b("polished_blackstone_bricks" if y < 3 else
                                                                 "chiseled_polished_blackstone"))
        sx, sz = math.cos(a) * R * 0.8, math.sin(a) * R * 0.8
        n = int(math.dist((ax, 4, az), (sx, top - T * 0.3, sz)) * 1.2)
        for i in range(n + 1):
            t = i / n
            x = ax + (sx - ax) * t
            z = az + (sz - az) * t
            y = 4 + (top - T * 0.3 - 4) * t - 3 * 4 * t * (1 - t)
            w.setze(round(x), round(y), round(z), w.b("iron_block" if i % 3 == 0 else "chain", **(
                {} if i % 3 == 0 else {"axis": "y", "waterlogged": False})), False)
    return _fertig(w, sch)


def sanduhr_inseln(seed, g=2):
    """Sanduhr-Inseln: zwei Inseln übereinander, die obere umgedreht, verbunden durch einen dünnen, rieselnden
    Sandfall in einer Glasröhre; auf der unteren ein Dünenfleck, auf der oberen ein kleiner Tempel."""
    w, sch, rs, R, T, top, oben = basis(seed, g, rf=0.7, extras=False)
    u = U[g]
    for (x, z), yo in oben.items():
        if math.hypot(x, z) < R * 0.5:
            w.setze(x, yo, z, w.b("sand" if (x * z) % 3 else "sandstone"))
    H = _r(10 * u + 6)
    t2 = top + H + int(T * 0.9)
    w2 = _welt(seed + 1)
    sch2 = Schema(w2)
    insel(w2, sch2, Rauschen(w2, 4), 0, 0, 0, R * 0.8, T * 0.8, extras=False)
    for (x, y, z), b in w2.bloecke.items():
        w.setze(x, t2 - y, z, b)
    for y in range(top + 1, t2 - 1):
        for x in range(-1, 2):
            for z in range(-1, 2):
                if abs(x) + abs(z) == 2:
                    continue
                w.setze(x, y, z, w.b("glass") if (x, z) != (0, 0) else w.b("sandstone"))
    return _fertig(w, sch)


SCHWEBEND2 = {
    "schwebender_tempel": ("Himmelstempel", schwebender_tempel),
    "wolkenbibliothek": ("Wolkenbibliothek", wolkenbibliothek),
    "wasserfallfels": ("Wasserfallfels", wasserfallfels),
    "schwebegarten": ("Schwebegarten", schwebegarten),
    "wolkenkloster": ("Wolkenkloster", wolkenkloster),
    "ringsphaere": ("Ringsphäre", ringsphaere),
    "kristallschwarm": ("Kristallschwarm", kristallschwarm),
    "umgekehrte_pyramide": ("Umgekehrte Pyramide", umgekehrte_pyramide),
    "luftburg": ("Luftburg", luftburg),
    "himmelsleuchtturm": ("Himmelsleuchtturm", himmelsleuchtturm),
    "wolkentreppe": ("Wolkentreppe", wolkentreppe),
    "miniplanet": ("Miniplanet", miniplanet),
    "truemmerfeld": ("Trümmerfeld", truemmerfeld),
    "wurzelinsel": ("Wurzelinsel", wurzelinsel),
    "schwebedorf": ("Schwebedorf", schwebedorf),
    "balloninsel": ("Ballon-Insel", balloninsel),
    "himmelssee": ("Himmelssee", himmelssee),
    "orbit_obelisk": ("Obelisk mit Orbit", orbit_obelisk),
    "kettenfels": ("Kettenfels", kettenfels),
    "sanduhr_inseln": ("Sanduhr-Inseln", sanduhr_inseln),
}

"""Drachenhort II – zwanzig weitere Drachenorte: Schlafender Drache, Seedrache, Drachenküken-Nest, Moosdrache,
Kristalldrache, Zweiköpfiger Drache, Drachenstall, Drachenschmiede, Drachenkopf-Felsen, Drachentöter-Denkmal,
Goldene Drachensäule, Drachen-Landeplattform, Drachensteigen-Wiese, Drachenbau, Drache am Turm, Drachenbaum,
Wyvern-Felsnadel, Drachengrab, Sternbild-Drache und Schuppenhort."""

from __future__ import annotations

import math

import numpy as np

from drachen import FARBEN, drache_setzen, drachenmat, felsen, gold_haufen, verbrennen
from erw_basis import M, S, baumrand, figur, haus, hoehe, wiese
from feinbau import Dachmat, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, laubball, rohr
from lib import Rauschen
from skulptur import Skulptur, dreh_y, ell, kap, kasten, kegel, kreisrand


def kopf(S, hx, hy, hz, r=1.0, richtung=1, offen=False):
    """Drachenkopf mit Schnauze, Augen und Hörnern an (hx, hy, hz); Blick in +x (richtung=-1: -x)."""
    d = richtung
    S.plus(ell(hx, hy, hz, 1.8 * r, 1.1 * r, 1.0 * r), "s")
    S.plus(ell(hx + d * 1.7 * r, hy - 0.2 * r, hz, 1.4 * r, 0.6 * r, 0.75 * r), "s")
    if offen:
        S.plus(ell(hx + d * 1.6 * r, hy - 1.0 * r, hz, 1.3 * r, 0.35 * r, 0.65 * r), "b")
        S.minus(kasten(min(hx + d * 0.8 * r, hx + d * 3 * r), hy - 0.75 * r, hz - 0.5 * r,
                       max(hx + d * 0.8 * r, hx + d * 3 * r), hy - 0.45 * r, hz + 0.5 * r))
    else:
        S.plus(ell(hx + d * 0.6 * r, hy - 0.6 * r, hz, 1.4 * r, 0.4 * r, 0.8 * r), "b")
    for sz in (-1, 1):
        S.plus(ell(hx + d * 0.6 * r, hy + 0.5 * r, hz + sz * 0.7 * r, 0.28 * r, 0.22 * r, 0.18 * r), "a")
        S.plus(kap((hx - d * 0.4 * r, hy + 0.7 * r, hz + sz * 0.5 * r),
                   (hx - d * 2.2 * r, hy + 2.0 * r, hz + sz * 1.0 * r), 0.32 * r, 0.08), "h")


def koerper_rohr(S, pts, radien):
    for i in range(len(pts) - 1):
        S.plus(kap(pts[i], pts[i + 1], radien[i], radien[i + 1]), "s")


def fluegel(S, schulter, spann, hoch, z_seite, s_dick=0.5):
    """Fledermausartiger Flügel: Arm, Fingerknochen, Membran (vereinfacht als dünne Fächer)."""
    sx, sy, sz = schulter
    ell_ = (sx - 0.5, sy + hoch * 0.6, sz + z_seite * spann * 0.45)
    S.plus(kap((sx, sy, sz), ell_, 0.5, 0.35), "s")
    spitzen = [(sx - 2 - 2.6 * f, sy + hoch * 0.3 - 1.6 * f, sz + z_seite * (spann + 0.6 * f)) for f in range(4)]
    for sp in spitzen:
        S.plus(kap(ell_, sp, 0.3, 0.12), "s")

    def membran(X, Y, Z):
        out = np.zeros(X.shape, dtype=bool)
        punkte = [(sx, sy, sz)] + spitzen
        for f in range(len(punkte) - 1):
            A = np.array(ell_)
            B = np.array(punkte[f])
            C = np.array(punkte[f + 1])
            n = np.cross(B - A, C - A)
            nn = np.linalg.norm(n) + 1e-9
            n = n / nn
            P = np.stack([X - A[0], Y - A[1], Z - A[2]], -1)
            dist = np.abs(P @ n)
            v0, v1 = B - A, C - A
            d00, d01, d11 = v0 @ v0, v0 @ v1, v1 @ v1
            d20, d21 = P @ v0, P @ v1
            den = d00 * d11 - d01 * d01 + 1e-9
            v = (d11 * d20 - d01 * d21) / den
            wv = (d00 * d21 - d01 * d20) / den
            out |= (dist <= s_dick) & (v >= 0) & (wv >= 0) & (v + wv <= 1)
        return out
    S.plus(membran, "b")


def skulptur_drache(w, art, u, lo, hi, versatz, dreh=0.0, bauen=None):
    Sk = Skulptur(w, u)
    sch, bau, horn, auge = drachenmat(w, art)
    Sk.mat("s", sch)
    Sk.mat("b", bau)
    Sk.mat("h", horn)
    Sk.mat("a", auge)
    bauen(Sk)
    Sk.rendern(lo, hi, versatz=versatz, dreh=dreh_y(dreh))


# ============================================================================ Bauten

def schlafender_drache(seed, g=2):
    """Schlafender Drache: ein roter Drache liegt zusammengerollt wie eine Katze auf einem Goldhaufen, den Kopf auf
    dem Schwanz, die Flügel angelegt, Rauchwölkchen aus den Nüstern, umgeben von Schätzen in einer Felsmulde."""
    w = _neu(seed)
    s = S[g]
    u = 0.85 * s + 0.4
    R = int(11 * u + 6)
    hoch = felsen(w, R, 3 * u + 2, spitz=0.6)
    for x in range(-int(R * 0.6), int(R * 0.6) + 1):
        for z in range(-int(R * 0.6), int(R * 0.6) + 1):
            if math.hypot(x, z) < R * 0.55:
                for y in range(1, 20):
                    w.bloecke.pop((x, y, z), None)
    gold_haufen(w, 0, 0, R * 0.55, 2 + s, y0=1)

    def bauen(Sk):
        pts = []
        for i in range(40):
            a = i / 40 * 1.25 * 2 * math.pi
            r = 8.5 - i * 0.12
            pts.append((math.cos(a) * r, 1.6 + 1.6 * math.sin(math.pi * i / 40), math.sin(a) * r))
        radien = [max(0.35, 2.3 * math.sin(math.pi * min(1, (i + 2) / 36)) ** 0.8) for i in range(40)]
        koerper_rohr(Sk, pts, radien)
        hx, hy, hz = pts[-1]
        kopf(Sk, hx + 1.0, hy + 0.4, hz + 2.6, r=1.1, richtung=1)
        for i in range(4, 30, 3):
            x, y, z = pts[i]
            Sk.plus(kap((x, y + radien[i] * 0.9, z), (x, y + radien[i] * 0.9 + 1.0, z), 0.3, 0.08), "h")
        for i in (10, 18):
            x, y, z = pts[i]
            Sk.plus(ell(x * 0.85, y + 1.6, z * 0.85, 2.6, 0.6, 1.6), "b")
    skulptur_drache(w, "rot", u, (-11, -1, -11), (11, 10, 11), (0.5, 1 + 0.8 * s, 0.5), bauen=bauen)
    w.setze(round(3 * u), round(5 * u), round(3 * u), w.b("campfire", lit=False, signal_fire=True, facing="north",
                                                       waterlogged=False))
    _ = hoch
    return w


def seedrache(seed, g=2):
    """Seedrache: ein blau-türkiser Drache mit Flossenkämmen taucht in mehreren Schleifen aus einer Meeresbucht auf,
    der Kopf mit aufgerissenem Maul erhoben, um ihn herum Gischt und Felsen."""
    w = _neu(seed)
    s = S[g]
    u = 0.9 * s + 0.4
    R = int(12 * u + 6)
    rn = Rauschen(w, 5)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) <= R + 2 * rn(x, 0, z):
                w.setze(x, -2, z, w.b("sand"))
                w.setze(x, -1, z, w.b("water", level=0))
                w.setze(x, 0, z, w.b("water", level=0))

    def bauen(Sk):
        L = 22
        pts = []
        for i in range(60):
            t = i / 59
            x = -L / 2 + t * L
            y = max(-2.5, math.sin(t * 3 * math.pi) * 4.5) if t < 0.85 else 4.5 + (t - 0.85) * 40
            z = math.sin(t * 2 * math.pi) * 3
            pts.append((x, y, z))
        radien = [0.5 + 1.6 * math.sin(math.pi * min(1, t / 0.95)) ** 0.5 for t in np.linspace(0, 1, 60)]
        koerper_rohr(Sk, pts, radien)
        for i in range(2, 55, 2):
            x, y, z = pts[i]
            if y > -1:
                Sk.plus(kasten(x - 0.2, y + radien[i] * 0.8, z - 0.1, x + 0.2, y + radien[i] * 0.8 + 1.2, z + 0.1), "b")
        hx, hy, hz = pts[-1]
        kopf(Sk, hx + 1.2, hy + 0.6, hz, r=1.3, richtung=1, offen=True)
        for sz in (-1, 1):
            Sk.plus(kap((hx, hy + 0.5, hz + sz * 0.9), (hx - 1.5, hy + 1.0, hz + sz * 2.5), 0.25, 0.1), "b")
    skulptur_drache(w, "blau", u, (-13, -4, -6), (14, 15, 6), (0.5, 0, 0.5), dreh=0.3, bauen=bauen)
    rng = w.rng
    for _ in range(int(10 * s)):
        x, z = int((rng.random() - 0.5) * R * 1.4), int((rng.random() - 0.5) * R * 1.4)
        if w.hole(x, 0, z) == w.b("water", level=0):
            w.setze(x, 1, z, w.b("white_concrete_powder") if rng.random() < 0.5 else w.b("stone"))
    return w


def drachenkueken(seed, g=1):
    """Drachenküken-Nest: ein großes Nest aus verkohlten Ästen und Felsbrocken auf einer Anhöhe, darin geschlüpfte
    bunte Drachenküken zwischen Eierschalen und zwei noch ungeschlüpfte, gefleckte Eier."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    felsen(w, R, 3 * s + 2, spitz=0.7)
    top = hoehe(w, 0, 0, 20)
    rn = 3.5 * s + 2.5
    for k in range(int(2 * s + 2)):
        for x, z in kreisrand(rn - k * 0.4):
            w.setze(x, top + 1 + k, z, w.b("dark_oak_wood", axis="y") if (x + z + k) % 3 else
                    w.b("stripped_dark_oak_wood", axis="y"))
    for x in range(-int(rn), int(rn) + 1):
        for z in range(-int(rn), int(rn) + 1):
            if math.hypot(x, z) < rn - 1:
                w.setze(x, top + 1, z, w.b("hay_block", axis="y") if (x + z) % 2 else w.b("coarse_dirt"))
    farben = ["rot", "gruen", "blau", "gold"]
    for k in range(2 + g):
        a = k / (2 + g) * 2 * math.pi
        x, z = round(math.cos(a) * rn * 0.45), round(math.sin(a) * rn * 0.45)
        sch, bau, horn, auge = drachenmat(w, farben[k % 4])
        teile = [(ell(0, 1.0, 0, 1.0, 0.7, 0.6), sch), (ell(0.4, 0.8, 0, 0.7, 0.4, 0.5), bau),
                 (ell(1.0, 1.9, 0, 0.55, 0.5, 0.45), sch), (ell(1.5, 1.8, 0, 0.35, 0.25, 0.3), sch),
                 (ell(1.2, 2.1, 0.3, 0.12, 0.12, 0.1), auge), (ell(1.2, 2.1, -0.3, 0.12, 0.12, 0.1), auge),
                 (kap((-0.8, 0.8, 0), (-1.8, 0.6, 0.5), 0.3, 0.1), sch),
                 (kap((0, 1.5, 0.4), (-0.6, 2.4, 1.2), 0.15), bau), (kap((0, 1.5, -0.4), (-0.6, 2.4, -1.2), 0.15), bau)]
        figur(w, 0.7 * s + 0.5, teile, (-2, -1, -2), (2, 3, 2), pos=(x, top + 2, z), winkel=a + math.pi)
    for k in range(2):
        x, z = round(rn * 0.2) * (1 if k else -1), round(rn * 0.1)
        kugel(w, x, top + 2.5, z, 0.9 + 0.3 * s, lambda xx, yy, zz: w.b("white_terracotta") if (xx + yy + zz) % 3 else
              w.b("red_terracotta"), ry=1.2 + 0.4 * s)
    return w


def moosdrache(seed, g=2):
    """Moosdrache: ein uralter grüner Drache liegt so lange schlafend im Wald, dass Moos, Farne und kleine Bäume
    auf seinem Rücken wachsen; nur das halb geöffnete Auge verrät, dass er lebt."""
    w = _neu(seed)
    s = S[g]
    u = 0.85 * s + 0.4
    R = int(13 * u + 6)
    zellen = wiese(w, R, 0.3, art="wald")
    drache_setzen(w, "gruen", u, (0.5, 0, 0.5), haltung="liegend", dreh=0.4)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 2 and w.frei(x, y + 1, z) and rng.random() < 0.5:
            q = rng.random()
            w.setze(x, y + 1, z, w.b("moss_carpet") if q < 0.6 else w.b("fern") if q < 0.8 else
                    w.b("azalea", ) if q < 0.85 else w.b("grass"))
    for k in range(2 + g):
        tops = [(x, y, z) for (x, y, z) in w.bloecke if y > 4 * u]
        if not tops:
            break
        x, y, z = tops[int(rng.random() * len(tops))]
        for yy in range(y + 1, y + 3 + int(s)):
            w.setze(x, yy, z, w.b("oak_log", axis="y"))
        laubball(w, x, y + 3 + int(s), z, 1.5 + 0.5 * s, arten=("oak_leaves", "azalea_leaves"), dicht=0.85)
    baumrand(w, zellen, R, 4 + 2 * g, seed, innen=0.85)
    return w


def kristalldrache(seed, g=2):
    """Kristalldrache: eine Drachenstatue, ganz aus Amethyst, violettem Glas und Quarz gewachsen, mit kristallinen
    Flügeln und Stacheln aus Amethyst-Clustern, auf einem Feld aus Kristalldrusen."""
    w = _neu(seed)
    s = S[g]
    u = 0.85 * s + 0.4
    R = int(12 * u + 6)
    zellen = wiese(w, R, 0.2, art="kies")
    Sk = Skulptur(w, u)
    am = M(w, [("amethyst_block", 3), ("purple_stained_glass", 1), ("budding_amethyst", 1)])
    Sk.mat("s", lambda x, y, z, *a: am(x, y, z))
    Sk.mat("b", w.b("magenta_stained_glass"))
    Sk.mat("h", w.b("smooth_quartz"))
    Sk.mat("a", w.b("sea_lantern"))
    from reiche import _drache
    _drache(w, Sk, lambda x, y, z, *a: am(x, y, z), w.b("magenta_stained_glass"), w.b("smooth_quartz"),
            w.b("sea_lantern"), "sitzend")
    Sk.rendern((-17, -1, -14), (13, 16, 14), versatz=(0.5, 0, 0.5), dreh=dreh_y(-0.5))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 3 and w.frei(x, y + 1, z) and rng.random() < 0.08:
            w.setze(x, y + 1, z, w.b("amethyst_cluster", facing="up", waterlogged=False))
    for _ in range(int(10 * s + 5)):
        a = rng.random() * 6.28
        d = R * (0.6 + rng.random() * 0.35)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = zellen.get((x, z), 0)
        h = int(1 + rng.random() * 3 * s)
        for k in range(1, h + 1):
            w.setze(x, y + k, z, w.b("amethyst_block"))
        w.setze(x, y + h + 1, z, w.b("amethyst_cluster", facing="up", waterlogged=False))
    return w


def zweikopf(seed, g=2):
    """Zweiköpfiger Drache: ein schwarz-violetter Drache mit zwei langen Hälsen und Köpfen, die in verschiedene
    Richtungen blicken, steht mit gespreizten Flügeln auf einem Felsplateau voller Brandspuren."""
    w = _neu(seed)
    s = S[g]
    u = 0.85 * s + 0.4
    R = int(12 * u + 6)
    felsen(w, R, 2 * u + 2, spitz=0.5)

    def bauen(Sk):
        koerper_rohr(Sk, [(-12, 2, 2), (-8, 3, 1), (-4, 5, 0), (0, 6, 0), (3, 6.5, 0)], [0.4, 1.0, 2.2, 2.8, 2.4])
        for sz in (-1, 1):
            hals = [(3, 6.5, sz * 0.8), (5, 8.5, sz * 2.0), (6, 11, sz * 3.2), (7.5, 12.5, sz * 4.0)]
            koerper_rohr(Sk, hals, [1.6, 1.3, 1.1, 1.0])
            kopf(Sk, 8.5, 12.8, sz * 4.4, r=1.0, richtung=1, offen=sz > 0)
            fluegel(Sk, (0, 8, sz * 1.5), 8.5, 9, sz)
        for lx in (-3.5, 2):
            for sz in (-1, 1):
                Sk.plus(kap((lx, 4.5, sz * 1.2), (lx + 0.8, 0.5, sz * 2.4), 0.8, 0.6), "s")
                Sk.plus(kap((lx + 0.8, 0.5, sz * 2.4), (lx + 2.0, 0.3, sz * 2.6), 0.4, 0.2), "h")
    top = hoehe(w, 0, 0, 30)
    skulptur_drache(w, "schwarz", u, (-14, -1, -12), (11, 15, 12), (0.5, top + 1, 0.5), dreh=0.2, bauen=bauen)
    verbrennen(w, 0.2)
    return w


def drachenstall(seed, g=2):
    """Drachenstall: eine gewaltige Scheune mit Toren hoch wie ein Turm, Futtertrögen voller Schinken (roter Ton),
    Sätteln für Drachenreiter an der Wand und einem jungen Drachen, der neugierig aus dem Tor schaut."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.1)
    B, T = int(6 * s + 7) | 1, int(5 * s + 7) | 1
    H = int(5 * s + 6)
    st = M(w, [("cobblestone", 2), ("stone_bricks", 2)])
    for x in range(-B // 2, B // 2 + 1):
        for z in range(-T // 2, T // 2 + 1):
            w.setze(x, 0, z, w.b("coarse_dirt"))
            for y in range(1, H + 1):
                if abs(x) == B // 2 or abs(z) == T // 2:
                    w.setze(x, y, z, st(x, y, z) if y < 3 else w.b("spruce_planks") if (x + z) % 4 else
                            w.b("spruce_log", axis="y"))
                else:
                    w.bloecke.pop((x, y, z), None)
    satteldach(w, -B // 2, -T // 2, B // 2, T // 2, H + 1, Dachmat(w, ["spruce", "dark_oak"]), first_x=False, ue=1,
               giebel=M(w, [("spruce_planks", 1)]), traufe="spruce", steil=1)
    tb = int(2 * s + 2)
    for x in range(-tb, tb + 1):
        for y in range(1, H - 1):
            w.bloecke.pop((x, y, T // 2), None)
    drache_setzen(w, "bronze", 0.35 * s + 0.2, (0.5, 0, T // 2 - 2), haltung="sitzend", dreh=-math.pi / 2)
    for k in range(3):
        w.setze(-B // 2 + 1, 1, -T // 2 + 2 + k * 2, w.b("composter", level=8))
        w.setze(-B // 2 + 1, 2, -T // 2 + 2 + k * 2, w.b("red_terracotta"))
    for k in range(3):
        w.setze(B // 2 - 1, 3, -T // 2 + 2 + k * 2, w.b("brown_wool"))
    _ = zellen
    return w


def drachenschmiede(seed, g=2):
    """Drachenschmiede: eine Schmiede, deren Esse von einer gezähmten Drachenstatue befeuert wird – der Steindrache
    hält das Maul über den glühenden Herd; Ambosse, Schuppenpanzer an Puppen und Wassertröge."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.1, art="kies")
    B, T = int(5 * s + 6) | 1, int(4 * s + 5) | 1
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            w.setze(x, 0, z, w.b("stone_bricks") if (x + z) % 2 else w.b("cobblestone"))
            if abs(x) == B and abs(z) == T:
                for y in range(1, 6):
                    w.setze(x, y, z, w.b("dark_oak_log", axis="y"))
    satteldach(w, -B, -T, B, T, 6, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]), first_x=True, ue=1,
               giebel=None, traufe="dark_oak")
    for x in range(-2, 3):
        for z in range(-T + 1, -T + 4):
            w.setze(x, 1, z, w.b("bricks"))
            w.setze(x, 2, z, w.b("magma_block") if abs(x) < 2 else w.b("bricks"))
    drache_setzen(w, "stein", 0.35 * s + 0.25, (-B - 2.5, 0, -T + 1.5), haltung="sitzend", dreh=0.0)
    w.setze(0, 1, 0, w.b("anvil", facing="east"))
    w.setze(3, 1, 1, w.b("anvil", facing="north"))
    for k in range(2):
        x = B - 2
        z = -2 + k * 4
        w.setze(x, 1, z, w.b("oak_fence"))
        w.setze(x, 2, z, w.b(["red_terracotta", "waxed_exposed_copper"][k]))
        w.setze(x, 3, z, w.b(["red_terracotta", "waxed_exposed_copper"][k]))
    for x in range(-B + 1, -B + 4):
        w.setze(x, 1, T - 1, w.b("water_cauldron", level=3))
    _ = zellen
    return w


def drachenkopf_felsen(seed, g=2):
    """Drachenkopf-Felsen: eine natürliche Felsformation an einer Klippe, die genau wie ein riesiger Drachenkopf
    aussieht – mit Höhlen als Augen, einem Wasserfall aus dem Maul und Hörnern aus Felsnadeln."""
    w = _neu(seed)
    s = S[g]
    u = 1.2 * s + 0.5
    R = int(10 * u + 6)
    zellen = wiese(w, R, 0.2)
    st = M(w, [("stone", 3), ("andesite", 2), ("tuff", 1), ("mossy_cobblestone", 1)])
    Sk = Skulptur(w, u)
    Sk.mat("s", lambda x, y, z, *a: st(x, y, z))
    Sk.mat("m", w.b("moss_block"))
    Sk.plus(ell(0, 4, -2, 6, 5, 5.5), "s")
    Sk.plus(ell(4.5, 3, -2, 4, 2.5, 3.5), "s")
    Sk.plus(ell(4.5, 0.8, -2, 3.8, 1.2, 3.2), "s")
    Sk.minus(kasten(3, 1.6, -4.5, 9, 2.4, 0.5))
    for sz in (-1, 1):
        Sk.minus(ell(2.5, 5.5, -2 + sz * 2.6, 0.9, 0.7, 0.8))
        Sk.plus(kegel(-2, -2 + sz * 2.8, 7.5, 12, 1.4, 0.2), "s")
    Sk.plus(ell(-1, 8.5, -2, 4, 0.8, 4), "m")
    Sk.rendern((-7, -1, -9), (10, 13, 5), versatz=(0.5, 0, 0.5))
    for y in range(0, int(2 * u)):
        for z in range(-3, 0):
            w.setze(round(6 * u), y + 1, round(z * u * 0.5) - 1, w.b("water", level=0), False)
    for x in range(round(6 * u), round(6 * u) + 6):
        for z in range(-4, 2):
            w.setze(x, 0, z, w.b("water", level=0))
    _ = zellen
    return w


def drachentoeter(seed, g=2):
    """Drachentöter-Denkmal: auf einem hohen Sockel steht ein Ritter mit erhobener Lanze und Schild über einem
    besiegten, sich windenden Lindwurm aus Bronze; eine Inschriftplatte und Blumenbeete ringsum."""
    w = _neu(seed)
    s = S[g]
    u = 0.8 * s + 0.4
    R = int(10 * u + 6)
    zellen = wiese(w, R, 0.05)
    st = M(w, [("stone_bricks", 3), ("chiseled_stone_bricks", 1)])
    A = int(3 * u + 2)
    Hs = int(2 * u + 2)
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            for y in range(1, Hs + 1):
                w.setze(x, y, z, st(x, y, z))
    bz = w.b("waxed_cut_copper")
    dz = w.b("waxed_exposed_copper")
    eis = w.b("iron_block")
    teile = []
    pts = [(-4, 0.6, 2), (-2, 1.2, 3), (0, 1.0, 1.5), (2, 1.5, -0.5), (3.5, 2.5, -2), (4.5, 4.0, -1.5)]
    for i in range(len(pts) - 1):
        teile.append((kap(pts[i], pts[i + 1], 0.4 + i * 0.15, 0.5 + i * 0.15), dz))
    teile.append((ell(5.2, 4.5, -1.2, 1.2, 0.8, 0.8), dz))
    teile += [(kap((0, 1.5, 0), (0, 4.5, 0), 0.7, 0.6), eis), (ell(0, 5.4, 0, 0.6, 0.65, 0.6), eis),
              (kap((-0.4, 1.5, 0.3), (-0.6, 0, 0.6), 0.3), eis), (kap((0.4, 1.5, -0.3), (0.8, 0, -0.6), 0.3), eis),
              (kap((0.6, 4.0, 0), (1.6, 5.5, 0), 0.25), eis), (kap((1.6, 5.5, 0), (5.0, 3.6, -1.0), 0.12), bz),
              (ell(-0.7, 3.2, 0.2, 0.15, 1.0, 0.8), w.b("red_terracotta")),
              (kegel(0, 0, 5.9, 6.6, 0.25, 0.05), w.b("red_wool"))]
    figur(w, u, teile, (-5, -1, -4), (7, 8, 4), pos=(0, Hs + 1, 0), winkel=0.4)
    w.setze(0, Hs // 2 + 1, A + 1, w.b("polished_andesite"))
    for x, z in kreisrand(A + 3):
        if (x, z) in zellen:
            w.setze(x, zellen[(x, z)] + 1, z, w.b(["red_tulip", "poppy", "oxeye_daisy"][(x + z) % 3]))
    return w


def drachensaeule(seed, g=2):
    """Goldene Drachensäule: eine hohe, rote Säule, um die sich ein goldener Drache in einer Spirale bis zur Spitze
    windet, wo er eine leuchtende Perle hält; der Sockel aus weißem Stein mit Wolkenmuster."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, 0.05, art="kies")
    H = int(16 * s + 10)
    for k in range(3):
        a = int(3 * s + 3) - k
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                w.setze(x, 1 + k, z, w.b("smooth_quartz") if (x + z) % 3 else w.b("chiseled_quartz_block"))
    for y in range(4, H):
        for x, z in kreisrand(1.4 + 0.3 * s):
            w.setze(x, y, z, w.b("red_terracotta"))
    rs = 1.4 + 0.3 * s + 1.2 + 0.4 * s
    pts = [(math.cos(t * 3.2 * 2 * math.pi) * rs, 4 + t * (H - 6), math.sin(t * 3.2 * 2 * math.pi) * rs, t)
           for t in np.linspace(0, 1, 200)]
    rohr(w, pts, 0.5 + 0.2 * s, 1.0 + 0.4 * s, mat=lambda x, y, z, *a: w.b("gold_block") if (x + y + z) % 4 else
         w.b("yellow_concrete"), rauh=0.02)
    hx, hy, hz, _ = pts[-1]
    kugel(w, hx * 1.2, hy + 1.5, hz * 1.2, 1.3 + 0.4 * s, w.b("gold_block"))
    kugel(w, 0, H + 1 + 0.8 * s, 0, 1.0 + 0.4 * s, w.b("sea_lantern"))
    w.setze(round(hx * 1.4), round(hy + 2), round(hz * 1.4), w.b("redstone_block"))
    _ = zellen
    return w


def landeplattform(seed, g=2):
    """Drachen-Landeplattform: eine runde, auf Felsen gebaute Plattform mit Landekreis-Markierung, Windsäcken,
    Signalfeuern, einer Treppe in den Fels und einem gerade landenden Drachen mit ausgebreiteten Flügeln."""
    w = _neu(seed)
    s = S[g]
    u = 0.6 * s + 0.35
    R = int(13 * s + 6)
    felsen(w, R * 0.7, 6 * s + 4, spitz=0.4)
    top = hoehe(w, 0, 0, 40)
    rp = R * 0.6
    for x in range(-int(rp) - 1, int(rp) + 2):
        for z in range(-int(rp) - 1, int(rp) + 2):
            d = math.hypot(x, z)
            if d <= rp:
                ring = abs(d - rp * 0.6) < 0.8
                w.setze(x, top + 1, z, w.b("red_concrete") if ring else w.b("stone_bricks") if (x + z) % 2 else
                        w.b("polished_andesite"))
                for y in range(top + 2, top + 30):
                    w.bloecke.pop((x, y, z), None)
    for i in range(4):
        a = i * math.pi / 2
        x, z = round(math.cos(a) * rp), round(math.sin(a) * rp)
        w.setze(x, top + 2, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    for y in range(top + 2, top + 7):
        w.setze(round(rp) - 1, y, round(rp * 0.5), w.b("spruce_fence"))
    w.setze(round(rp) - 2, top + 6, round(rp * 0.5), w.b("orange_wool"))
    w.setze(round(rp) - 3, top + 6, round(rp * 0.5), w.b("white_wool"))

    def bauen(Sk):
        koerper_rohr(Sk, [(-12, 5, 0), (-8, 6, 0), (-4, 7, 0), (0, 8, 0), (3, 9.5, 0), (5, 11, 0)],
                     [0.4, 1.0, 2.0, 2.4, 1.6, 1.1])
        kopf(Sk, 6.3, 11.5, 0, r=1.1, richtung=1)
        for sz in (-1, 1):
            fluegel(Sk, (-1, 9, sz * 1.5), 10, 6, sz)
            Sk.plus(kap((-2, 7, sz * 1.2), (-1, 3, sz * 2.0), 0.7, 0.5), "s")
            Sk.plus(kap((-1, 3, sz * 2.0), (0.5, 0.5, sz * 2.2), 0.45, 0.25), "h")
    skulptur_drache(w, "gruen", u, (-13, -1, -13), (9, 14, 13), (0.5, top + 2, 0.5), dreh=0.6, bauen=bauen)
    return w


def drachensteigen(seed, g=1):
    """Drachensteigen-Wiese: eine windige Hügelwiese, auf der bunte Papierdrachen in Drachenform an langen Schnüren
    hoch am Himmel stehen, mit Schwänzen aus Wimpeln, Kinder-Figuren und ein Picknickplatz."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.8, blumen=0.08)
    rng = w.rng
    farben = [("red_wool", "yellow_wool"), ("blue_wool", "white_wool"), ("lime_wool", "orange_wool"),
              ("purple_wool", "pink_wool")]
    for k in range(3 + g):
        x0, z0 = int((rng.random() - 0.5) * R), int((rng.random() - 0.5) * R)
        y0 = zellen.get((x0, z0), 0) + 1
        kx, ky, kz = x0 + int(4 * s + 3), y0 + int(10 * s + 8) + k * 2, z0 - int(3 * s + 2)
        a, b = farben[k % 4]
        for i in range(-3, 4):
            for j in range(-2, 4):
                if abs(i) + abs(j - 1) <= 3:
                    w.setze(kx + i, ky + j, kz, w.b(a if (i + j) % 2 else b))
        w.setze(kx, ky + 4, kz, w.b(a))
        w.setze(kx - 1, ky + 3, kz, w.b("black_wool"))
        w.setze(kx + 1, ky + 3, kz, w.b("black_wool"))
        for t in range(int(6 * s + 4)):
            w.setze(kx + round(math.sin(t * 0.8) * 1.2), ky - 3 - t, kz + t // 3, w.b([a, b][t % 2]), False)
        n = int(math.hypot(kx - x0, ky - y0))
        for t in range(1, n):
            f = t / n
            w.setze(round(x0 + (kx - x0) * f), round(y0 + 2 + (ky - y0 - 2) * f), round(z0 + (kz - z0) * f),
                    w.b("white_stained_glass"), False)
        from erw_markt import mensch
        figur(w, 0.45 * s + 0.3, mensch(w, ["red_wool", "blue_wool", "yellow_wool"][k % 3]), (-2, -1, -2),
              (2, 6, 2), pos=(x0, y0, z0))
    return w


def drachenbau(seed, g=2):
    """Drachenbau: ein gewaltiger, von Klauen in den Hang gegrabener Tunneleingang mit Kratzspuren, abgenagten
    Knochen, verstreuten Goldmünzen und rußgeschwärzten Wänden, aus dem Rauch aufsteigt."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.2)
    rn = Rauschen(w, 4)
    H = 8 * s + 5
    for x in range(-R, R + 1):
        for z in range(-R, 0):
            if math.hypot(x, z) > R:
                continue
            h = int(H * min(1, -z / (R * 0.4)) + rn(x, 0, z) * 3)
            for y in range(1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else w.b("stone") if (x + y) % 3 else
                        w.b("andesite"))
    tb, th = 3.5 * s + 2.5, 4 * s + 3
    for x in range(-int(tb) - 1, int(tb) + 2):
        for y in range(1, int(th) + 2):
            if (x / tb) ** 2 + ((y - 0.5) / th) ** 2 <= 1:
                for z in range(-R, 1):
                    w.bloecke.pop((x, y, z), None)
            elif (x / (tb + 1.5)) ** 2 + ((y - 0.5) / (th + 1.5)) ** 2 <= 1:
                for z in range(-int(R * 0.5), 0):
                    if not w.frei(x, y, z):
                        w.setze(x, y, z, w.b("blackstone") if (y + z) % 2 else w.b("basalt", axis="y"))
    for k in range(4):
        x = -int(tb) + 1 + k * 2
        for y in range(1, int(th)):
            if not w.frei(x, y, -1):
                w.setze(x, y, -1, w.b("black_concrete"))
    gold_haufen(w, 0, int(R * 0.15), 2.5 + s, 1, y0=1)
    rng = w.rng
    for _ in range(int(6 * s + 3)):
        x, z = int((rng.random() - 0.5) * R), int(rng.random() * R * 0.6)
        if (x, z) in zellen:
            w.setze(x, zellen[(x, z)] + 1, z, w.b("bone_block", axis="x" if rng.random() < 0.5 else "z"))
    w.setze(0, int(H) + 1, -int(R * 0.6), w.b("campfire", lit=True, signal_fire=True, facing="north",
                                             waterlogged=False))
    return w


def drache_am_turm(seed, g=2):
    """Drache am Turm: ein roter Drache klammert sich mit den Krallen an einen hohen Burgturm, den Hals um die
    Turmspitze geschlungen, die Flügel halb geöffnet, Zinnen sind herausgebrochen."""
    w = _neu(seed)
    s = S[g]
    u = 0.65 * s + 0.35
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.1)
    rt = 3 * s + 2.5
    H = int(20 * s + 12)
    st = M(w, [("stone_bricks", 3), ("cracked_stone_bricks", 1), ("andesite", 1)])
    for y in range(1, H):
        for x, z in kreisrand(rt):
            fen = y % 6 == 3 and (x == 0 or z == 0)
            w.setze(x, y, z, w.b("glass_pane") if fen else st(x, y, z))
    for x, z in kreisrand(rt + 1):
        w.setze(x, H, z, st(x, H, z))
        if (x + z) % 2 == 0 and x > 0:
            w.setze(x, H + 1, z, st(x, H + 1, z))
    kegeldach(w, 0, 0, H + 1, int(rt), Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]), form="kegel",
              spitze="gold_block")

    def bauen(Sk):
        r = rt / u + 1.6
        pts = []
        for i in range(30):
            t = i / 29
            a = -0.8 + t * 2.4 * math.pi * 0.55
            pts.append((math.cos(a) * r, 4 + t * (H / u - 2), math.sin(a) * r))
        radien = [0.5 + 1.6 * math.sin(math.pi * min(1, (i + 3) / 31)) ** 0.6 for i in range(30)]
        koerper_rohr(Sk, pts, radien)
        hx, hy, hz = pts[-1]
        kopf(Sk, hx + 1.5, hy + 1.0, hz, r=1.2, richtung=1, offen=True)
        mx, my, mz = pts[12]
        for sz in (-1, 1):
            fluegel(Sk, (mx, my + 1, mz + sz * 1.0), 7, 6, sz)
        for i in (8, 15):
            x, y, z = pts[i]
            Sk.plus(kap((x, y, z), (x * 0.75, y - 1.5, z * 0.75), 0.6, 0.4), "s")
    skulptur_drache(w, "rot", u, (-14, -1, -14), (14, H / u + 6, 14), (0.5, 0, 0.5), bauen=bauen)
    _ = zellen
    return w


def drachenbaum(seed, g=2):
    """Drachenbaum: ein uralter Baum mit schuppiger Rinde, dessen Stamm sich wie ein Drachenhals windet und dessen
    Krone ein Kopf mit Astgeweih bildet; im Laub glühen rote Früchte wie Augen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.2)
    H = int(14 * s + 8)
    pts = bez((0, 0, 0), (3 * s, H * 0.4, 2 * s), (-2 * s, H * 0.75, -1 * s), (1 * s, H, 0))
    rohr(w, pts, 2.2 * s + 1, 1.0 * s + 0.6, mat=lambda x, y, z, *a: w.b("dark_oak_wood", axis="y") if (x + y + z) % 3
         else w.b("mangrove_wood", axis="y"), rauh=0.12)
    hx, hy, hz, _ = pts[-1]
    for k in range(6):
        a = k / 6 * 2 * math.pi
        L = 4 * s + 3
        rohr(w, bez((hx, hy, hz), (hx + math.cos(a) * L * 0.5, hy + L * 0.6, hz + math.sin(a) * L * 0.5),
                    (hx + math.cos(a) * L, hy + L * 0.5, hz + math.sin(a) * L)), 0.6 * s + 0.3, 0.25,
             mat=w.b("dark_oak_wood", axis="y"))
        laubball(w, hx + math.cos(a) * L, hy + L * 0.5 + 1, hz + math.sin(a) * L, 2 + s,
                 arten=("dark_oak_leaves", "mangrove_leaves"), dicht=0.85)
    for sz in (-1, 1):
        w.setze(round(hx + 2), round(hy), round(hz + sz * 1.5), w.b("shroomlight"))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if "leaves" in w.P.name(b) and rng.random() < 0.03:
            w.setze(x, y, z, w.b("red_concrete"))
    for k in range(5):
        a = k / 5 * 2 * math.pi
        rohr(w, bez((0, 1, 0), (math.cos(a) * 3 * s, 0.5, math.sin(a) * 3 * s),
                    (math.cos(a) * (5 * s + 2), -1, math.sin(a) * (5 * s + 2))), 0.9 * s + 0.4, 0.4,
             mat=w.b("dark_oak_wood", axis="y"))
    _ = zellen
    return w


def wyvern(seed, g=2):
    """Wyvern-Felsnadel: eine schlanke, zerklüftete Felsnadel, auf deren Spitze ein zweibeiniger Wyvern mit großen
    Flugarmen hockt und kreischt, darunter Nester und weiße Kotspuren an den Wänden."""
    w = _neu(seed)
    s = S[g]
    u = 0.6 * s + 0.35
    R = int(10 * s + 6)
    zellen = wiese(w, R, 0.3)
    rn = Rauschen(w, 3)
    H = int(16 * s + 10)
    st = M(w, [("stone", 3), ("andesite", 2), ("tuff", 1)])
    for y in range(1, H):
        r = (3.5 * s + 2) * (1 - 0.55 * y / H) + rn(0, y, 0) * 1.2
        for x in range(-int(r) - 2, int(r) + 3):
            for z in range(-int(r) - 2, int(r) + 3):
                if math.hypot(x, z) <= r + rn(x, y, z) * 1.0:
                    w.setze(x, y, z, st(x, y, z) if rn(x * 3, y, z * 3) > 0.12 else w.b("white_concrete_powder"))

    def bauen(Sk):
        koerper_rohr(Sk, [(-8, 2, 0), (-5, 3, 0), (-2, 4.5, 0), (0, 5.5, 0), (2, 7.5, 0), (3, 9.5, 0)],
                     [0.3, 0.8, 1.5, 1.8, 1.0, 0.8])
        kopf(Sk, 4.2, 10.2, 0, r=0.9, richtung=1, offen=True)
        for sz in (-1, 1):
            fluegel(Sk, (0, 6.5, sz * 1.0), 8, 7, sz, s_dick=0.45)
            Sk.plus(kap((-1, 4.5, sz * 0.9), (0, 1.8, sz * 1.2), 0.6, 0.4), "s")
            Sk.plus(kap((0, 1.8, sz * 1.2), (1.2, 0.2, sz * 1.3), 0.35, 0.2), "h")
    top = hoehe(w, 0, 0, H + 3)
    skulptur_drache(w, "bronze", u, (-10, -1, -10), (7, 12, 10), (0.5, top + 1, 0.5), dreh=0.9, bauen=bauen)
    _ = zellen
    return w


def drachengrab(seed, g=2):
    """Drachengrab: eine von Säulen umstandene Gruftplatte, auf der die liegende Steinfigur eines Drachen ruht,
    flankiert von Feuerschalen; Treppen führen hinab zur versiegelten Grabkammer mit Drachensymbol."""
    w = _neu(seed)
    s = S[g]
    u = 0.6 * s + 0.35
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.05)
    A = int(R * 0.6)
    st = M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 1), ("chiseled_stone_bricks", 0.3)])
    for x in range(-A, A + 1):
        for z in range(-int(A * 0.6), int(A * 0.6) + 1):
            w.setze(x, 1, z, st(x, 1, z))
            w.setze(x, 0, z, st(x, 0, z))
    for x in range(-A, A + 1, 3):
        for sz in (-1, 1):
            z = sz * int(A * 0.6)
            for y in range(2, int(4 * s + 4)):
                w.setze(x, y, z, w.b("stone_bricks") if y % 3 else w.b("chiseled_stone_bricks"))
    drache_setzen(w, "stein", u, (0.5, 2, 0.5), haltung="liegend", dreh=0.0)
    for sx in (-1, 1):
        x = sx * (A + 2)
        w.setze(x, 1, 0, w.b("chiseled_stone_bricks"))
        w.setze(x, 2, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for k in range(3):
        for x in (-1, 0, 1):
            w.setze(x, 1 - k, int(A * 0.6) + 1 + k, treppe(w, "stone_brick", "north"))
            w.bloecke.pop((x, 2 - k, int(A * 0.6) + 1 + k), None)
    w.setze(0, -1, int(A * 0.6) + 4, w.b("red_terracotta"))
    _ = zellen
    return w


def sternbild_drache(seed, g=2):
    """Sternbild-Drache: am nächtlichen Himmel über einer Sternwarten-Plattform schwebt ein riesiger Drache aus
    leuchtenden Sternen (Endstäbe, Seelaternen), verbunden durch feine Linien aus blauem Glas."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.1)
    for x in range(-4, 5):
        for z in range(-4, 5):
            if math.hypot(x, z) < 4.3:
                w.setze(x, 1, z, w.b("smooth_stone"))
    w.setze(0, 2, 0, w.b("iron_bars", waterlogged=False))
    w.setze(0, 3, 0, w.b("lightning_rod", facing="east", powered=False, waterlogged=False))
    sterne = [(-12, 14, 0), (-8, 16, 2), (-4, 18, 1), (0, 19, 0), (4, 21, -1), (7, 24, 0), (9, 23, 2), (10, 25, 1),
              (-2, 22, 6), (-6, 24, 9), (-2, 22, -6), (-6, 24, -9), (-1, 15, 3), (2, 13, 4), (-1, 15, -3),
              (2, 13, -4)]
    kanten = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (2, 8), (8, 9), (2, 10), (10, 11), (3, 12),
              (12, 13), (3, 14), (14, 15)]
    f = 0.9 * s + 0.4
    P = [(round(x * f), round(5 + (y - 10) * f), round(z * f)) for x, y, z in sterne]
    for a, b in kanten:
        A, B = P[a], P[b]
        n = int(max(abs(B[0] - A[0]), abs(B[1] - A[1]), abs(B[2] - A[2])))
        for k in range(1, n):
            t = k / n
            w.setze(round(A[0] + (B[0] - A[0]) * t), round(A[1] + (B[1] - A[1]) * t), round(A[2] + (B[2] - A[2]) * t),
                    w.b("light_blue_stained_glass"), False)
    for i, p in enumerate(P):
        w.setze(*p, w.b("sea_lantern") if i % 3 else w.b("end_rod", facing="up"))
    _ = zellen
    return w


def schuppenhort(seed, g=2):
    """Schuppenhort: eine Höhle, in der ein Drache seine abgeworfenen, schillernden Schuppen hortet – Haufen aus
    grün-, rot- und blauschimmernden Platten zwischen Goldmünzen, Kristallen und einem alten Ritterhelm."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    felsen(w, R, 7 * s + 5, spitz=0.8)
    rh = R * 0.55
    for x in range(-int(rh), int(rh) + 1):
        for z in range(-int(rh), int(R) + 1):
            for y in range(1, int(5 * s + 4)):
                if (x / rh) ** 2 + ((y - 0.5) / (5 * s + 3)) ** 2 + ((z if z < 0 else z * 0.25) / rh) ** 2 < 1:
                    w.bloecke.pop((x, y, z), None)
    rng = w.rng
    farben = ["emerald_block", "red_terracotta", "lapis_block", "waxed_oxidized_copper", "prismarine",
              "nether_wart_block"]
    for k in range(4 + g):
        a = rng.random() * 6.28
        d = rng.random() * rh * 0.6
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        r = 1.2 + rng.random() * 1.5 * s
        for x in range(int(cx - r), int(cx + r) + 1):
            for z in range(int(cz - r), int(cz + r) + 1):
                dd = math.hypot(x - cx, z - cz)
                if dd <= r:
                    for y in range(1, int((1 - dd / r) * 2 * s) + 2):
                        w.setze(x, y, z, w.b(farben[int(rng.integers(6))]) if rng.random() < 0.7 else
                                w.b("gold_block"))
    gold_haufen(w, 0, -int(rh * 0.5), 2 + s, 1 + s * 0.5, y0=1)
    w.setze(2, 1, 2, w.b("iron_block"))
    w.setze(2, 2, 2, w.b("iron_bars", waterlogged=False))
    return w


DRACHEN3 = {
    "schlafender_drache": ("Schlafender Drache", schlafender_drache),
    "seedrache": ("Seedrache", seedrache),
    "drachenkueken": ("Drachenküken-Nest", drachenkueken),
    "moosdrache": ("Moosdrache", moosdrache),
    "kristalldrache": ("Kristalldrache", kristalldrache),
    "zweikopf": ("Zweiköpfiger Drache", zweikopf),
    "drachenstall": ("Drachenstall", drachenstall),
    "drachenschmiede": ("Drachenschmiede", drachenschmiede),
    "drachenkopf_felsen": ("Drachenkopf-Felsen", drachenkopf_felsen),
    "drachentoeter": ("Drachentöter-Denkmal", drachentoeter),
    "drachensaeule": ("Goldene Drachensäule", drachensaeule),
    "landeplattform": ("Drachen-Landeplattform", landeplattform),
    "drachensteigen": ("Drachensteigen-Wiese", drachensteigen),
    "drachenbau": ("Drachenbau", drachenbau),
    "drache_am_turm": ("Drache am Turm", drache_am_turm),
    "drachenbaum": ("Drachenbaum", drachenbaum),
    "wyvern": ("Wyvern-Felsnadel", wyvern),
    "drachengrab": ("Drachengrab", drachengrab),
    "sternbild_drache": ("Sternbild-Drache", sternbild_drache),
    "schuppenhort": ("Schuppenhort", schuppenhort),
}

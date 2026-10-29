"""Piraten – Paket: Bucht mit Pfahltaverne, Schatzinsel, Totenkopffelsen, Hafenfort, Schiffswrack,
Schatzgrotte, Kraken-Angriff und ein gigantischer Mahlstrom. Meeresspiegel bei y = 0."""

from __future__ import annotations

import math

import numpy as np

from boote import piratenschiff, ruderboot
from gebaeude import palme
from lib import LUFT, Verlauf, Welt, einfuegen, ueberwuchern
from skulptur import Skulptur, dreh_x, dreh_y, ell, kap, kasten, und, kreisrand, laterne, platte, scheibe, treppe, verbinde

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def einfuegen_gedreht(ziel: Welt, quelle: Welt, R, versatz):
    """Fügt eine Welt gedreht ein (R: 3×3, welt = R · lokal + versatz). Rückwärts abgetastet, also lückenlos."""
    karte = {i: ziel.b(n, **dict(p)) for i, (n, p) in enumerate(quelle.P.eintraege)}
    pts = np.array([p for p, b in quelle.bloecke.items() if b != LUFT], float)
    if len(pts) == 0:
        return
    R = np.asarray(R, float)
    lo, hi = pts.min(0) - 1, pts.max(0) + 1
    ecken = np.array([[a, b, c] for a in (lo[0], hi[0]) for b in (lo[1], hi[1]) for c in (lo[2], hi[2])])
    welt = ecken @ R.T + np.asarray(versatz, float)
    wlo, whi = np.floor(welt.min(0)).astype(int), np.ceil(welt.max(0)).astype(int)
    X, Y, Z = np.mgrid[wlo[0]:whi[0] + 1, wlo[1]:whi[1] + 1, wlo[2]:whi[2] + 1]
    P = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1).astype(float) - np.asarray(versatz, float)
    L = np.rint(P @ R).astype(int)
    for (wx, wy, wz), (lx, ly, lz) in zip(np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1), L):
        s = quelle.bloecke.get((int(lx), int(ly), int(lz)))
        if s is not None and s != LUFT:
            ziel.setze(int(wx), int(wy), int(wz), karte[s])


def _insel(w, R, sand_breite=2.5, hoehe=3, gras=True, rauh=0.15):
    """Runde Insel: Unterwasser-Sockel, Sandstrand, Grasmitte. Gibt Höhenkarte zurück."""
    sand, sst, erde = w.b("sand"), w.b("sandstone"), w.b("dirt")
    gr = w.b("grass_block", snowy=False)
    hoehen = {}
    n = int(R) + 4
    for x in range(-n, n + 1):
        for z in range(-n, n + 1):
            a = math.atan2(z, x)
            d = math.hypot(x, z) / (1 + rauh * math.sin(3 * a + 1) + 0.6 * rauh * math.sin(7 * a))
            if d > R + 3:
                continue
            if d > R:
                h = -1 - int((d - R) * 0.8)
            else:
                h = int(hoehe * max(0.0, 1 - (d / R) ** 2) ** 0.7)
            for y in range(min(-3, h - 2), h + 1):
                if y == h:
                    blk = gr if gras and d < R - sand_breite and h > 0 else sand
                else:
                    blk = sst if y < h - 2 else (erde if gras and d < R - sand_breite else sand)
                w.setze(x, y, z, blk)
            hoehen[(x, z)] = h
    return hoehen


# ============================================================================ Piratenbucht

def piratenbucht(seed, g=1):
    """Sichelförmige Felsbucht um eine Lagune: Sandstrand mit Palmen, Taverne auf Pfählen über dem Wasser,
    Steg mit Pollern und vertäutem Ruderboot, Laternen und Fässer."""
    w = _welt(seed)
    u = U[g]
    fels = Verlauf(w, "Fels", ["tuff", "andesite", "stone", "calcite"]) if _stil(seed) == 0 else \
        Verlauf(w, "Fels", ["terracotta", "brown_terracotta", "orange_terracotta", "smooth_sandstone"])
    R = 16 * u + 6
    breit = 5 * u + 2
    Hf = 9 * u + 3
    n = int(R + breit) + 3
    sand, wasser = w.b("sand"), w.b("water", level=0)
    for x in range(-n, n + 1):
        for z in range(-n, n + 1):
            d = math.hypot(x, z)
            a = math.atan2(z, x)
            offen = -0.55 < a < 0.55                       # Einfahrt nach +x
            if d < R - 3:
                for y in range(-3, 0):
                    w.setze(x, y, z, sand)
                w.setze(x, 0, z, wasser)
            elif d < R:
                for y in range(-2, 1):
                    w.setze(x, y, z, sand)
            elif d < R + breit and not offen:
                t = (d - R) / breit
                h = int(Hf * math.sin(math.pi * min(1, t * 1.3)) * (0.75 + 0.25 * math.sin(a * 5 + 1)))
                for y in range(-3, h + 1):
                    w.setze(x, y, z, fels(0.4 + 3 * y / Hf + w.rng.random() * 0.7, x, y, z))
                if h > 2:
                    w.setze(x, h + 1, z, w.b("grass_block", snowy=False)) if w.rng.random() < 0.6 else None
            elif d < R + 1 and offen:
                w.setze(x, 0, z, wasser)
    # Palmen am Strand
    for i in range(3 + 2 * g):
        a = math.pi * (0.4 + 1.2 * w.rng.random()) * (1 if w.rng.random() < 0.5 else -1)
        if abs(a) < 0.7:
            continue
        x, z = round(math.cos(a) * (R - 1.5)), round(math.sin(a) * (R - 1.5))
        palme(w, x, 0, z, hoehe=_r(7 * u + 2, 5), neigung=a + math.pi)
    # Taverne auf Pfählen
    tx, tz = -int(R * 0.35), -int(R * 0.25)
    bx, bz, hh = _r(4 * u, 3), _r(3 * u, 2), _r(3.5 * u, 3)
    yb = 2
    for dx in (-bx, bx):
        for dz in (-bz, bz):
            for y in range(-3, yb):
                w.setze(tx + dx, y, tz + dz, w.b("stripped_spruce_log", axis="y"))
    for x in range(tx - bx - 1, tx + bx + 2):
        for z in range(tz - bz - 1, tz + bz + 2):
            w.setze(x, yb, z, w.b("spruce_planks"))
    for x in range(tx - bx, tx + bx + 1):
        for z in range(tz - bz, tz + bz + 1):
            rand = x in (tx - bx, tx + bx) or z in (tz - bz, tz + bz)
            if not rand:
                continue
            for y in range(yb + 1, yb + 1 + hh):
                ecke = x in (tx - bx, tx + bx) and z in (tz - bz, tz + bz)
                fenster = y == yb + 2 and not ecke and (x + z) % 3 == 0
                w.setze(x, y, z, w.b("stripped_spruce_log", axis="y") if ecke else
                        w.b("yellow_stained_glass") if fenster else w.b("spruce_planks" if y % 2 else "oak_planks"))
    for k in range(bz + 2):
        for x in range(tx - bx - 1, tx + bx + 2):
            for s in (-1, 1):
                w.setze(x, yb + 1 + hh + k, tz + s * (bz + 1 - k), treppe(w, "dark_oak", "south" if s < 0 else "north"))
        if bz + 1 - k <= 0:
            break
    for x in range(tx - bx - 1, tx + bx + 2):
        w.setze(x, yb + 1 + hh + bz + 1, tz, platte(w, "dark_oak"))
    for y, half in ((yb + 1, "lower"), (yb + 2, "upper")):
        w.setze(tx + bx, y, tz, w.b("spruce_door", facing="west", half=half, hinge="left", open=False, powered=False))
    for dz in (-1, 1):
        laterne(w, tx + bx + 1, yb + 1, tz + 2 * dz)
    # Steg von der Taverne zur Lagunenmitte
    for x in range(tx + bx + 1, int(R * 0.35)):
        for z in (tz - 1, tz, tz + 1):
            w.setze(x, yb, z, w.b("spruce_planks"))
        if x % 4 == 0:
            for z in (tz - 2, tz + 2):
                for y in range(-3, yb + 2):
                    w.setze(x, y, z, w.b("stripped_spruce_log", axis="y"))
            laterne(w, x, yb + 2, tz + 2)
    for k in range(3):
        w.setze(tx - bx + 1 + k, yb + 1, tz + bz + 1, w.b("barrel", facing="up", open=False))
    boot = ruderboot(seed, max(0, g - 1))
    einfuegen(w, boot, int(R * 0.2), 0, tz + 4, ueberschreiben=False)
    ueberwuchern(w, None, ranken=0.25, moos_oben=0.0, pflanzen=0.3, buesche=0.05)
    return w


# ============================================================================ Schatzinsel

def schatzinsel(seed, g=1):
    """Kleine Insel mit Palmen, Totenkopf-Stein, Kreuz im Sand, offener Truhe mit Goldhaufen,
    Spaten, zerbrochenem Mast und einem gestrandeten Beiboot."""
    w = _welt(seed)
    u = U[g]
    R = 9 * u + 4
    hoehen = _insel(w, R, hoehe=_r(2 * u, 1) + 1)
    for i in range(2 + g):
        a = i * 2 * math.pi / (2 + g) + 0.6
        x, z = round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)
        palme(w, x, hoehen.get((x, z), 0), z, hoehe=_r(6 * u + 3, 5))
    # X im Sand und Schatz
    sx, sz = round(R * 0.25), round(R * 0.35)
    yb = hoehen.get((sx, sz), 0)
    for k in range(-2, 3):
        w.setze(sx + k, yb, sz + k, w.b("red_concrete"))
        w.setze(sx + k, yb, sz - k, w.b("red_concrete"))
    S = Skulptur(w, max(0.8, u))
    S.mat("g", Verlauf(w, "Gold", ["raw_gold_block", "gold_block", "honeycomb_block"]), basis=0.8, rausch=1.8)
    S.plus(lambda X, Y, Z: (X / 2.4) ** 2 + (Y / 1.1) ** 2 + (Z / 2.0) ** 2 <= 1, "g")
    S.rendern((-3, -1, -3), (3, 2, 3), versatz=(sx - 3 + 0.5, yb + 0.5, sz + 0.5))
    w.setze(sx - 3, yb + _r(1.2 * max(0.8, u)) + 1, sz, w.b("chest", facing="south", type="single", waterlogged=False))
    w.setze(sx + 2, yb + 1, sz - 3, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                        waterlogged=False))
    w.setze(sx + 2, yb + 2, sz - 3, w.b("iron_trapdoor", facing="north", half="top", open=True, powered=False,
                                        waterlogged=False))
    # Totenkopf-Stein
    kx, kz = -round(R * 0.4), round(R * 0.1)
    yk = hoehen.get((kx, kz), 0)
    T = Skulptur(w, max(0.8, u))
    T.mat("k", Verlauf(w, "Knochenstein", ["andesite", "diorite", "calcite", "bone_block"]), basis=1.5, rausch=1.2)
    T.mat("d", w.b("black_concrete"))
    T.plus(ell(0, 2.6, 0, 2.2, 2.2, 2.0), "k")
    T.plus(ell(0, 0.9, 0.4, 1.4, 1.0, 1.4), "k")
    T.plus(ell(-0.8, 2.6, 1.6, 0.55, 0.6, 0.6), "d")
    T.plus(ell(0.8, 2.6, 1.6, 0.55, 0.6, 0.6), "d")
    T.plus(kasten(-0.2, 1.6, 1.5, 0.2, 2.0, 2.2), "d")
    T.rendern((-3, 0, -3), (3, 5, 3), versatz=(kx + 0.5, yk, kz + 0.5))
    # Gestrandetes Beiboot und Mast
    boot = ruderboot(seed + 3, max(0, g - 1))
    einfuegen_gedreht(w, boot, dreh_y(0.9) @ dreh_x(0.25), (-R * 0.15, 0, -R * 0.75))
    for k in range(_r(6 * u, 4)):
        w.setze(round(R * 0.6) - k, 1, -round(R * 0.2) + k // 3, w.b("spruce_log", axis="x"))
    ueberwuchern(w, None, ranken=0.0, moos_oben=0.0, pflanzen=0.35, buesche=0.08)
    return w


# ============================================================================ Totenkopffelsen

def totenkopffelsen(seed, g=2):
    """Riesiger Felsen in Form eines Schädels, der aus dem Meer ragt: hohle Augen mit Glut, Nasenloch,
    Zahnreihe über einer Grotte mit Wasser, Moos und Ranken."""
    w = _welt(seed)
    u = U[g]
    stein = Verlauf(w, "Stein", ["mossy_cobblestone", "andesite", "stone", "diorite", "calcite"]) if _stil(seed) == 0 \
        else Verlauf(w, "Schwarzfels", ["blackstone", "basalt", "tuff", "andesite", "calcite"])
    glut = "shroomlight" if _stil(seed) == 0 else "sea_lantern"
    _insel(w, 12 * u + 4, sand_breite=4 * u + 2, hoehe=1, gras=False)
    S = Skulptur(w, u)
    S.mat("k", stein, basis=0.2, steigung=4 / 18, rausch=1.0)
    S.mat("z", w.b("bone_block", axis="y") if _stil(seed) == 0 else w.b("calcite"))
    S.mat("e", w.b(glut))
    S.plus(ell(0, 10, -0.5, 8.5, 8.5, 8.5), "k")                        # Schädeldach
    S.plus(ell(0, 5, 1.5, 7.5, 5, 7), "k")                               # Gesicht
    S.plus(ell(0, 0.5, 2.5, 6.2, 3.5, 5.6), "k")                         # Kiefer
    S.plus(ell(-7.2, 6, 0, 1.6, 2.6, 2.4), "k")
    S.plus(ell(7.2, 6, 0, 1.6, 2.6, 2.4), "k")
    S.mat("d", w.b("blackstone"))
    for sx in (-3.2, 3.2):
        S.minus(ell(sx, 8, 7.0, 2.7, 2.4, 4.0))                          # Augenhöhlen
        S.plus(und(ell(sx, 8, 4.0, 2.9, 2.6, 1.2), ell(0, 10, -0.5, 8.5, 8.5, 8.5)), "d")
        S.plus(ell(sx, 8, 4.6, 1.0, 1.0, 0.8), "e")
    S.minus(lambda X, Y, Z: (Y > 3.6) & (Y < 6) & (np.abs(X) < 1.8 - (Y - 3.6) * 0.6) & (Z > 4))   # Nase
    S.minus(ell(0, 1.3, 6, 4.6, 1.9, 4.5))                               # Mundgrotte
    for i in range(-4, 5):
        if i % 2 == 0:
            S.plus(kasten(i * 0.95 - 0.4, 2.4, 6.6, i * 0.95 + 0.4, 3.4, 7.4), "z")
            S.plus(kasten(i * 0.95 - 0.4, -0.3, 6.4, i * 0.95 + 0.4, 0.6, 7.2), "z")
    S.rendern((-10, -2, -10), (10, 19, 10), versatz=(0.5, 0, 0.5), dreh=dreh_y(math.pi / 4))
    for (x, y, z), b in list(w.bloecke.items()):
        if y == 0 and b == LUFT:
            w.setze(x, 0, z, w.b("water", level=0))
    for x in range(-int(9 * u), int(9 * u) + 1):
        for z in range(-int(9 * u), int(9 * u)):
            if w.frei(x, 0, z) and math.hypot(x - 3.5 * u, z - 3.5 * u) < 4.0 * u:
                w.setze(x, 0, z, w.b("water", level=0))
    ueberwuchern(w, None, ranken=0.4, moos_oben=0.6, pflanzen=0.2, buesche=0.05, max_ranke=_r(5 * u, 2))
    return w


# ============================================================================ Hafenfort

def hafenfort(seed, g=1):
    """Hafenfestung auf einem Felssockel: vier spitze Bastionen mit Kanonen, Zinnenmauern, Bergfried mit
    Flagge, Kaserne, Pulvermagazin, Leuchtfeuer und Anlegesteg."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        mauer = Verlauf(w, "Mauer", ["mossy_stone_bricks", "stone_bricks", "cracked_stone_bricks", "polished_andesite"])
        flagge = ["black_wool", "white_wool"]
    else:
        mauer = Verlauf(w, "Mauer", ["mud_bricks", "cut_sandstone", "smooth_sandstone", "sandstone"])
        flagge = ["red_wool", "yellow_wool"]
    fels = Verlauf(w, "Fels", ["tuff", "andesite", "stone", "cobblestone"])
    S_ = _r(9 * u + 3, 6)
    Hm = _r(5 * u, 4)
    bas = _r(4 * u + 1, 3)
    n = S_ + bas + 6
    for x in range(-n, n + 1):
        for z in range(-n, n + 1):
            d = max(abs(x), abs(z)) + 0.4 * min(abs(x), abs(z)) * 0.2
            if d > n - 1:
                continue
            top = 1 if d < S_ + bas + 1 else int(1 - (d - S_ - bas))
            for y in range(-4, top + 1):
                w.setze(x, y, z, fels(0.5 + w.rng.random() * 2.5, x, y, z))

    def im_fort(x, z):
        if max(abs(x), abs(z)) <= S_:
            return True
        for cx in (-S_, S_):
            for cz in (-S_, S_):
                if abs(x - cx) + abs(z - cz) <= bas + 1:
                    return True
        return False
    ring = []
    for x in range(-n, n + 1):
        for z in range(-n, n + 1):
            if im_fort(x, z) and not all(im_fort(x + a, z + b) for a in (-1, 0, 1) for b in (-1, 0, 1)):
                ring.append((x, z))
    for (x, z) in ring:
        for y in range(2, 2 + Hm):
            w.setze(x, y, z, mauer(1 + 2 * y / Hm + w.rng.random() * 0.6, x, y, z))
        if (x + z) % 2 == 0:
            w.setze(x, 2 + Hm, z, mauer(2.5, x, 2 + Hm, z))
    for x in range(-n, n + 1):
        for z in range(-n, n + 1):
            if im_fort(x, z) and (x, z) not in ring:
                inner_rand = not all(im_fort(x + a, z + b) for a in (-2, 0, 2) for b in (-2, 0, 2))
                w.setze(x, 1 + (Hm if inner_rand else 0), z, w.b("stone_bricks" if inner_rand else "gravel"))
    # Kanonen auf den Bastionen
    for cx in (-S_, S_):
        for cz in (-S_, S_):
            for k in range(-1, 2, 2):
                x = cx + (1 if cx > 0 else -1) * (bas - 1)
                z = cz + k * 2
                w.setze(x, 2 + Hm, z, w.b("spruce_planks"))
                w.setze(x + (1 if cx > 0 else -1), 2 + Hm, z, w.b("polished_blackstone_wall", up=True, north="none",
                                                                  south="none", east="none", west="none",
                                                                  waterlogged=False))
            w.setze(cx, 2 + Hm, cz, w.b("lantern", hanging=False, waterlogged=False))
    # Bergfried mit Flagge
    hb = _r(2.5 * u, 2)
    Hb = _r(9 * u, 6)
    for y in range(2, 2 + Hb):
        for x in range(-hb, hb + 1):
            for z in range(-hb, hb + 1):
                if max(abs(x), abs(z)) == hb:
                    fenster = y % 4 == 0 and (x == 0 or z == 0)
                    w.setze(x, y, z, w.b("glass_pane", north=x == 0, south=x == 0, east=z == 0, west=z == 0,
                                         waterlogged=False) if fenster else mauer(1 + 2 * y / Hb, x, y, z))
    for x in range(-hb - 1, hb + 2):
        for z in range(-hb - 1, hb + 2):
            if max(abs(x), abs(z)) == hb + 1:
                w.setze(x, 1 + Hb, z, treppe(w, "stone_brick", "south" if z < -hb else "north" if z > hb else
                                             "east" if x < 0 else "west", "top"))
                if (x + z) % 2 == 0:
                    w.setze(x, 2 + Hb, z, mauer(2.5, x, 2 + Hb, z))
            else:
                w.setze(x, 1 + Hb, z, w.b("spruce_planks"))
    for y in range(2 + Hb, 2 + Hb + _r(5 * u, 3)):
        w.setze(0, y, 0, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    top = 2 + Hb + _r(5 * u, 3)
    for k in range(_r(3 * u, 2)):
        for d in range(max(1, _r(2 * u, 1))):
            w.setze(-1 - k, top - d, 0, w.b(flagge[(k + d) % 2]))
    # Kaserne und Pulvermagazin
    for (x0, z0, x1, z1) in ((-S_ + 2, -S_ + 2, -hb - 3, -hb - 2), (hb + 3, hb + 2, S_ - 2, S_ - 3)):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for z in range(min(z0, z1), max(z0, z1) + 1):
                for y in range(2, 2 + _r(2.5 * u, 2)):
                    if x in (x0, x1) or z in (z0, z1):
                        w.setze(x, y, z, w.b("spruce_planks"))
                w.setze(x, 2 + _r(2.5 * u, 2), z, w.b("red_terracotta" if _stil(seed) == 0 else "orange_terracotta"))
    # Leuchtfeuer auf der Seeseite und Steg
    w.setze(S_ + bas, 2 + Hm, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    for x in range(n - 2, n + _r(8 * u, 5)):
        for z in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
        if x % 3 == 0:
            for y in range(-3, 1):
                w.setze(x, y, 2, w.b("stripped_spruce_log", axis="y"))
                w.setze(x, y, -2, w.b("stripped_spruce_log", axis="y"))
    return w


# ============================================================================ Schiffswrack

def schiffswrack(seed, g=1):
    """Gestrandetes Wrack: schief im Sand liegender, aufgerissener Rumpf, abgebrochener Mast, Segelfetzen,
    verstreute Fässer, Truhe und Algen."""
    w = _welt(seed)
    u = U[g]
    schiff = piratenschiff(seed, g)
    # Rumpf aufreißen, Segel größtenteils weg, Masten kürzen
    hoch = max(p[1] for p in schiff.bloecke)
    for p, b in list(schiff.bloecke.items()):
        n = schiff.P.name(b)
        if n.endswith("_wool") and w.rng.random() < 0.8:
            del schiff.bloecke[p]
        elif p[1] > hoch * 0.45 and w.rng.random() < 0.6:
            del schiff.bloecke[p]
        elif n.endswith("planks") or n.endswith("concrete") or n.endswith("terracotta"):
            if p[2] > 0 and math.sin(p[0] * 0.5) * math.cos(p[1] * 0.7) > 0.45:
                del schiff.bloecke[p]
    R = 14 * u + 6
    _insel(w, R, sand_breite=R, hoehe=_r(2 * u, 1), gras=False)
    einfuegen_gedreht(w, schiff, dreh_y(0.3) @ dreh_x(0.42), (0, -1.0 * u, 0))
    for i in range(4 + 2 * g):
        a = w.rng.random() * 2 * math.pi
        d = R * (0.4 + 0.5 * w.rng.random())
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = max([p[1] for p in w.bloecke if p[0] == x and p[2] == z] + [0]) + 1
        w.setze(x, y, z, w.b("barrel", facing="up", open=False) if i % 3 else
                w.b("chest", facing="north", type="single", waterlogged=False))
    for k in range(_r(8 * u, 5)):
        w.setze(-round(R * 0.3) + k, 1 + (k // 6), round(R * 0.55), w.b("spruce_log", axis="x"))
    ueberwuchern(w, None, ranken=0.3, moos_oben=0.3, pflanzen=0.05, buesche=0.0)
    return w


# ============================================================================ Schatzgrotte

def schatzgrotte(seed, g=1):
    """Halboffene Felsgrotte mit Tropfsteinen, Wasserbecken, Goldhaufen, Truhen, Kristallen und Laternen."""
    w = _welt(seed)
    u = U[g]
    fels = Verlauf(w, "Fels", ["deepslate", "tuff", "andesite", "stone", "dripstone_block"])
    R = 10 * u + 4
    S = Skulptur(w, 1.0)
    S.mat("k", fels, basis=0.3, steigung=3.5 / (R * 1.3), rausch=1.2)

    def dom(X, Y, Z):
        d = np.sqrt((X / R) ** 2 + (Y / (R * 0.85)) ** 2 + (Z / R) ** 2)
        return (Y >= 0) & (d <= 1 + 0.08 * np.sin(X * 0.4) * np.cos(Z * 0.35)) & (d > 0.78)
    S.plus(dom, "k")
    S.minus(lambda X, Y, Z: ((X + Z) / 1.414 > 0.05 * R) & (Y < R * 0.72 - np.abs(X - Z) / 1.414 * 0.3))
    S.rendern((-R - 2, 0, -R - 2), (R + 2, R + 2, R + 2), versatz=(0.5, 0, 0.5))
    for x, z in scheibe(R * 0.85):
        w.setze(x, 0, z, fels(1.5 + w.rng.random(), x, 0, z), ueberschreiben=False)
    # Goldberg mit Truhen
    G = Skulptur(w, 1.0)
    G.mat("g", Verlauf(w, "Gold", ["raw_gold_block", "gold_block", "honeycomb_block"]), basis=0.8, rausch=1.8)
    gr = R * 0.4
    G.plus(lambda X, Y, Z: (X / gr) ** 2 + (Y / (gr * 0.45)) ** 2 + (Z / (gr * 0.8)) ** 2 <= 1, "g")
    G.rendern((-gr - 1, 0, -gr - 1), (gr + 1, gr, gr + 1), versatz=(0.5, 1, -R * 0.25))
    for k, (x, z) in enumerate(((-2, -int(R * 0.25)), (2, -int(R * 0.25) + 1), (0, -int(R * 0.25) - 2))):
        y = max([p[1] for p in w.bloecke if p[0] == x and p[2] == z and p[1] < R * 0.5] + [0]) + 1
        w.setze(x, y, z, w.b("chest", facing="south", type="single", waterlogged=False))
    # Wasserbecken
    for x, z in scheibe(R * 0.18, -int(R * 0.45), int(R * 0.1)):
        w.setze(x, 0, z, w.b("water", level=0))
    # Tropfsteine, Kristalle, Laternen
    for i in range(int(6 * u) + 4):
        a = w.rng.random() * 2 * math.pi
        d = R * 0.6 * w.rng.random()
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        dach = [p[1] for p in w.bloecke if p[0] == x and p[2] == z and p[1] > R * 0.4]
        if dach:
            y = min(dach) - 1
            lang = 1 + int(w.rng.random() * 3 * u)
            for k in range(lang):
                dicke = "tip" if k == lang - 1 else "frustum" if k else "base"
                w.setze(x, y - k, z, w.b("pointed_dripstone", vertical_direction="down", thickness=dicke,
                                         waterlogged=False))
        if i % 3 == 0:
            w.setze(x, 1, z, w.b("amethyst_cluster", facing="up", waterlogged=False), ueberschreiben=False)
    for x in (-int(R * 0.5), int(R * 0.5)):
        w.setze(x, 1, int(R * 0.2), w.b("lantern", hanging=False, waterlogged=False))
    ueberwuchern(w, None, ranken=0.35, moos_oben=0.4, pflanzen=0.15, buesche=0.03)
    return w


# ============================================================================ Kraken-Angriff

def krakenangriff(seed, g=2):
    """Eine riesige Krake taucht neben einer Piratenbrigg auf und schlingt ihre Fangarme über das Deck."""
    w = _welt(seed)
    u = U[g]
    schiff = piratenschiff(seed, g)
    einfuegen(w, schiff, 0, 0, 0)
    B = 3.4 * u + 1.2
    L = 26 * u + 6
    if _stil(seed) == 0:
        haut = Verlauf(w, "Krake", ["nether_wart_block", "red_terracotta", "magenta_terracotta", "pink_terracotta"])
    else:
        haut = Verlauf(w, "Krake", ["dark_prismarine", "warped_wart_block", "prismarine", "cyan_terracotta"])
    S = Skulptur(w, u)
    S.mat("h", haut, basis=0.4, steigung=0.15, rausch=1.0)
    S.mat("s", w.b("pink_terracotta" if _stil(seed) == 0 else "light_blue_terracotta"))
    S.mat("e", w.b("yellow_concrete"))
    S.mat("p", w.b("black_concrete"))
    kz = -(B / u + 8)
    S.plus(ell(-2, 2.5, kz, 6.5, 6.5, 5.5), "h")                                # Mantel
    S.plus(ell(1.5, 5, kz + 3.6, 1.5, 1.5, 1.2), "e")
    S.plus(ell(1.9, 5, kz + 4.4, 0.7, 1.2, 0.5), "p")
    S.plus(ell(-5.5, 5, kz + 3.6, 1.5, 1.5, 1.2), "e")
    S.plus(ell(-5.1, 5, kz + 4.4, 0.7, 1.2, 0.5), "p")
    for i in range(7):
        x0 = (i - 3) * (L / u) / 8
        seite = -1 if i % 2 == 0 else 1
        hoehe = 9 + 4 * (i % 3)
        pts = []
        for k in range(14):
            t = k / 13
            z = (kz + 4) * (1 - t) + (B / u + 3) * t * (1 if seite > 0 else 0.6)
            y = -2 + hoehe * math.sin(math.pi * min(1, t * 1.1))
            x = x0 + 2.5 * math.sin(t * 5 + i)
            pts.append((x, y, z))
        for k, (a, b) in enumerate(zip(pts, pts[1:])):
            r0 = 1.5 * (1 - k / 14) + 0.35
            S.plus(kap(a, b, r0, r0 * 0.92), "h")
            if k % 2 == 0 and k > 2:
                S.plus(ell(a[0], a[1] - r0 * 0.8, a[2], 0.45, 0.35, 0.45), "s")
    S.rendern((-L / u / 2 - 6, -4, kz - 8), (L / u / 2 + 6, 22, B / u + 8), versatz=(0.5, 0, 0.5))
    return w


# ============================================================================ Mahlstrom

def mahlstrom(seed, g=3):
    """Gigantischer Mahlstrom: ein tiefer Wassertrichter mit spiralförmigen Gischtkämmen, in dem eine
    Piratenbrigg schräg an der Wand entlangrast; Treibgut kreist mit. Der Trichter wird beim Setzen
    freigeräumt (Luft), damit das Meer ihn nicht füllt."""
    w = _welt(seed)
    u = U[g]
    R = 26 * u + 8
    D = 15 * u + 6
    farbe = Verlauf(w, "Wasser", ["black_concrete", "blue_terracotta", "blue_concrete", "cyan_concrete",
                                  "light_blue_concrete", "light_blue_stained_glass"])
    gischt = [w.b("white_concrete"), w.b("snow_block"), w.b("white_wool"), w.b("packed_ice")]
    eis = w.b("blue_ice")

    def tiefe(r):
        return -D * max(0.0, 1 - r / R) ** 2.4 if r < R else 0.0
    n = int(R) + 8
    for x in range(-n, n + 1):
        for z in range(-n, n + 1):
            r = math.hypot(x, z)
            if r > R + 7:
                continue
            a = math.atan2(z, x)
            band = ((a + 3.0 * math.log(r + 1)) * 6 / (2 * math.pi)) % 1
            if r <= R:
                ys = int(math.floor(tiefe(r)))
                y_innen = int(math.floor(tiefe(max(0.0, r - 1.2)))) - 1
                if r < 2 * u + 1:
                    y_innen = -int(D) - 4
                for y in range(min(y_innen, ys - 1), ys + 1):
                    w.setze(x, y, z, farbe(0.3 + 5 * (1 + tiefe(r) / D) ** 1.4 + w.rng.random() * 0.4, x, y, z)
                            if y < ys else
                            (gischt[int(w.rng.integers(4))] if band < 0.1 else eis if band < 0.16 else
                             farbe(0.5 + 5 * (1 + tiefe(r) / D) ** 1.2 + w.rng.random() * 0.5, x, y, z)))
                for y in range(ys + 1, 1):
                    w.setze(x, y, z, LUFT)
            else:
                ring = 1 - (r - R) / 7
                if band < 0.25 or w.rng.random() < ring * 0.3:
                    w.setze(x, 0, z, gischt[int(w.rng.integers(4))])
                    if ring > 0.6 and band < 0.12:
                        w.setze(x, 1, z, w.b("white_wool"))
    # Schiff schräg an der Trichterwand
    schiff = piratenschiff(seed, 2)
    th = 0.35
    r0 = R * 0.48
    y0 = tiefe(r0)
    neig = math.atan(D * 2.4 * (1 - r0 / R) ** 1.4 / R)
    vor = np.array([-math.sin(th), 0, math.cos(th)])
    aussen = np.array([math.cos(th), 0, math.sin(th)])
    oben = np.array([0, math.cos(neig), 0]) - aussen * math.sin(neig)
    oben /= np.linalg.norm(oben)
    seite = np.cross(vor, oben)
    Rm = np.stack([vor, oben, seite], 1)
    einfuegen_gedreht(w, schiff, Rm, (r0 * math.cos(th), y0 + 0.5, r0 * math.sin(th)))
    # Treibgut auf der Spirale
    for i in range(40):
        r = R * (0.15 + 0.8 * w.rng.random())
        a = w.rng.random() * 2 * math.pi
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        y = int(math.floor(tiefe(r))) + 1
        w.setze(x, y, z, w.b("barrel", facing="up", open=False) if i % 3 == 0 else
                w.b("spruce_planks") if i % 3 == 1 else w.b("spruce_log", axis="x"))
    w.anker = (0, 0, 0)
    return w


PIRATEN = {
    "piratenbucht": ("Piratenbucht", piratenbucht),
    "schatzinsel": ("Schatzinsel", schatzinsel),
    "totenkopffelsen": ("Totenkopffelsen", totenkopffelsen),
    "hafenfort": ("Hafenfort", hafenfort),
    "schiffswrack": ("Schiffswrack", schiffswrack),
    "schatzgrotte": ("Schatzgrotte", schatzgrotte),
    "krakenangriff": ("Kraken-Angriff", krakenangriff),
}
MAHLSTROM = {"mahlstrom": ("Mahlstrom", mahlstrom)}


from piraten2 import NEU as _NEU  # noqa: E402

PIRATEN.update(_NEU)

"""Friedhof & Spuk, Hexenwerk (neu) – je 20 Bauten im Pracht-Stil, mit Mod-Blöcken als Variation."""

from __future__ import annotations

import math

import numpy as np

import haeuser as H_
import modbloecke as MB
import pracht as P
from kathedralen import halle, stil as sakralstil
from lib import Rauschen, Verlauf, einfuegen, laub
from pracht import Mat, gelaende
from skulptur import Skulptur, dreh_y, ell, kap, kreisrand, scheibe, spiegel_x
from weltwunder import bl, hohl, sk

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    from lib import Welt
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _pf(w, name, **verb):
    d = dict(north=False, south=False, east=False, west=False, waterlogged=False)
    d.update(verb)
    return w.b(name, **d)


def _wand(w, name, up=True, **verb):
    d = dict(north="none", south="none", east="none", west="none")
    d.update(verb)
    return w.b(name, up=up, waterlogged=False, **d)


def _achse(dx, dy, dz):
    a = np.abs([dx, dy, dz])
    return "xyz"[int(np.argmax(a))]


def kerze(w, farbe=None, n=None):
    n = n or int(w.rng.integers(1, 5))
    return w.b(f"{farbe}_candle" if farbe else "candle", candles=n, lit=True, waterlogged=False)


def schaedel(w, art="skeleton_skull", rot=None):
    return w.b(art, rotation=int(w.rng.integers(0, 16)) if rot is None else rot)


# ============================================================================ Boden, Bäume, Gräber


def spukboden(w, R, cx=0, cz=0, nass=False, dichte=1.0):
    """Morbider Boden: Podsol, grobe Erde, Matsch, Seelenerde-Flecken, welkes Gras, tote Büsche, Spinnweben."""
    r1 = Rauschen(w, 5)
    r2 = Rauschen(w, 2)
    rng = w.rng
    for x, z in scheibe(R, cx, cz):
        v = r1(x, 0, z)
        q = r2(x, 3, z)
        if nass and v < 0.25:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("mud"))
            if rng.random() < 0.15:
                w.setze(x, 1, z, w.b("lily_pad"))
            continue
        b = ("mud" if nass and v < 0.35 else "podzol" if v < 0.4 else "coarse_dirt" if q < 0.3 else
             "soul_soil" if q > 0.82 else "rooted_dirt" if v > 0.75 else "grass_block")
        w.setze(x, 0, z, w.b(b, snowy=False) if b in ("podzol", "grass_block") else w.b(b))
        if w.frei(x, 1, z):
            r = rng.random() / dichte
            if r < 0.04:
                w.setze(x, 1, z, w.b("dead_bush"))
            elif r < 0.10:
                w.setze(x, 1, z, w.b("grass") if b == "grass_block" else w.b("fern"))
            elif r < 0.115:
                w.setze(x, 1, z, MB.zweig(w))
            elif r < 0.122:
                w.setze(x, 1, z, w.b("cobweb"))
            elif r < 0.13:
                w.setze(x, 1, z, w.b(["brown_mushroom", "red_mushroom"][int(rng.integers(2))]))


def ast(w, x0, y0, z0, x1, y1, z1, holz, dick=True):
    n = int(max(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))) + 1
    ax = _achse(x1 - x0, y1 - y0, z1 - z0)
    for i in range(n + 1):
        t = i / n
        p = (round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), round(z0 + (z1 - z0) * t))
        if dick or t < 0.6:
            w.setze(*p, w.b(f"{holz}_log", axis=ax) if not holz.endswith("_stem") else w.b(holz, axis=ax))
        else:
            w.setze(*p, _pf(w, f"{holz}_fence"))


def knorrbaum(w, x, z, H, holz="dark_oak", y0=1, krone=None, seed_off=0):
    """Knorriger toter Baum: Wurzelanlauf, gedrehter Stamm, verzweigte Äste, dünne Zweige aus Zäunen.
    krone: optionale Laubsorte für spärliche Blätterbüschel."""
    rng = w.rng
    H = max(4, int(H))
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        lw = 1 + int(rng.integers(0, 2 + H // 6))
        for k in range(lw):
            w.setze(x + dx * (k + 1), y0 - (1 if k else 0), z + dz * (k + 1),
                    w.b(f"{holz}_log", axis="x" if dx else "z"))
    dick = H >= 12
    cx, cz = float(x), float(z)
    drift = rng.random() * 2 * math.pi
    for y in range(y0, y0 + H):
        cx += math.cos(drift + y * 0.3) * 0.25
        cz += math.sin(drift + y * 0.3) * 0.25
        w.setze(round(cx), y, round(cz), w.b(f"{holz}_log", axis="y"))
        if dick and y < y0 + H * 0.6:
            for dx, dz in ((1, 0), (0, 1), (1, 1)):
                w.setze(round(cx) + dx, y, round(cz) + dz, w.b(f"{holz}_log", axis="y"))
    enden = []

    def zweig(px, py, pz, a, steig, laenge, tiefe):
        ex = px + math.cos(a) * laenge
        ez = pz + math.sin(a) * laenge
        ey = py + steig * laenge
        ast(w, px, py, pz, ex, ey, ez, holz, dick=tiefe < 2)
        if tiefe < 2 and laenge > 2:
            for d in (-0.6, 0.7):
                zweig(ex, ey, ez, a + d + rng.random() * 0.4, steig + 0.15, laenge * 0.6, tiefe + 1)
        else:
            enden.append((round(ex), round(ey), round(ez)))
    for i in range(3 + H // 6):
        a = i * 2.39 + rng.random()
        yb = y0 + H * (0.45 + 0.5 * i / (3 + H // 6))
        zweig(cx, yb, cz, a, 0.35 + rng.random() * 0.4, H * (0.3 + 0.2 * rng.random()), 0)
    if krone:
        for (ex, ey, ez) in enden:
            for xx, zz in scheibe(1.3, ex, ez):
                if rng.random() < 0.6:
                    w.setze(xx, ey, zz, laub(w, krone))
    return enden


GRAB_STEINE = [("stone_brick", "stone_bricks", "chiseled_stone_bricks"),
               ("cobblestone", "cobblestone", "mossy_cobblestone"),
               ("mossy_stone_brick", "mossy_stone_bricks", "chiseled_stone_bricks"),
               ("deepslate_brick", "deepslate_bricks", "chiseled_deepslate"),
               ("polished_blackstone_brick", "polished_blackstone_bricks", "chiseled_polished_blackstone"),
               ("andesite", "polished_andesite", "polished_andesite")]


def grab(w, x, z, richtung="south", art=None, stein=None, deko=True):
    """Ein Grab: Grabstein (Platte, Kreuz, Obelisk, Totenkopf, Engelskopf, umgekippt) und Grabhügel davor."""
    rng = w.rng
    art = int(rng.integers(0, 7)) if art is None else art
    stein = GRAB_STEINE[int(rng.integers(len(GRAB_STEINE)))] if stein is None else stein
    wand, voll, zier = stein
    dz = 1 if richtung == "south" else -1
    quer = {"east": "low", "west": "low"}
    if art == 0:  # Kreuz
        w.setze(x, 1, z, _wand(w, f"{wand}_wall"))
        w.setze(x, 2, z, _wand(w, f"{wand}_wall", **quer))
        w.setze(x - 1, 2, z, _wand(w, f"{wand}_wall", up=False, east="low"))
        w.setze(x + 1, 2, z, _wand(w, f"{wand}_wall", up=False, west="low"))
        w.setze(x, 3, z, _wand(w, f"{wand}_wall"))
    elif art == 1:  # Platte mit Abdeckung
        w.setze(x, 1, z, w.b(zier))
        w.setze(x, 2, z, w.b(f"{wand}_slab", type="bottom", waterlogged=False))
    elif art == 2:  # Obelisk
        w.setze(x, 1, z, w.b(voll))
        w.setze(x, 2, z, _wand(w, f"{wand}_wall"))
        w.setze(x, 3, z, w.b("lightning_rod", facing="up", powered=False, waterlogged=False) if rng.random() < 0.5
                else _wand(w, f"{wand}_wall"))
    elif art == 3:  # Totenkopf
        w.setze(x, 1, z, _wand(w, f"{wand}_wall"))
        w.setze(x, 2, z, schaedel(w, rot=0 if dz > 0 else 8))
    elif art == 4:  # breiter Stein
        for d in (-1, 0, 1):
            w.setze(x + d, 1, z, w.b(f"{wand}_stairs", facing="north" if dz > 0 else "south", half="bottom",
                                     shape="straight", waterlogged=False) if d else w.b(zier))
        w.setze(x, 2, z, w.b(f"{wand}_slab", type="bottom", waterlogged=False))
    elif art == 5:  # umgekippt / eingesunken
        w.setze(x, 1, z, w.b(f"{wand}_stairs", facing=["east", "west", "north", "south"][int(rng.integers(4))],
                             half="bottom", shape="straight", waterlogged=False))
    else:  # einfacher Grabstein
        w.setze(x, 1, z, w.b(f"{wand}_wall", up=True, north="none", south="none", east="none", west="none",
                             waterlogged=False) if rng.random() < 0.5 else w.b(voll))
    for k in (1, 2):
        w.setze(x, 0, z + dz * k, w.b(["coarse_dirt", "podzol", "rooted_dirt"][int(rng.integers(3))],
                                      snowy=False) if False else w.b("coarse_dirt" if rng.random() < 0.6 else "rooted_dirt"))
        w.bloecke.pop((x, 1, z + dz * k), None)
    if deko:
        r = rng.random()
        if r < 0.15:
            w.setze(x, 1, z + dz, kerze(w))
        elif r < 0.25:
            w.setze(x, 1, z + dz, w.b(["poppy", "wither_rose", "lily_of_the_valley", "azure_bluet"][int(rng.integers(4))]))
        elif r < 0.3:
            w.setze(x, 1, z + dz * 2, w.b("soul_lantern", hanging=False, waterlogged=False))
        elif r < 0.33:
            w.setze(x, 1, z + dz, w.b("cobweb"))


def eisenzaun(w, pts, hoehe=2, pfosten="polished_blackstone_bricks", spitzen=True):
    menge = set(pts)
    for i, (x, z) in enumerate(pts):
        if i % 5 == 0:
            for y in range(1, hoehe + 1):
                w.setze(x, y, z, w.b(pfosten))
            w.setze(x, hoehe + 1, z, w.b("soul_lantern", hanging=False, waterlogged=False) if i % 10 == 0 else
                    w.b("polished_blackstone_button", face="floor", facing="north", powered=False) if False else
                    _wand(w, "polished_blackstone_wall"))
            continue
        for y in range(1, hoehe + 1):
            w.setze(x, y, z, w.b("iron_bars", north=(x, z - 1) in menge, south=(x, z + 1) in menge,
                                 east=(x + 1, z) in menge, west=(x - 1, z) in menge, waterlogged=False))
        if spitzen:
            w.setze(x, hoehe + 1, z, w.b("lightning_rod", facing="up", powered=False, waterlogged=False)
                    if i % 2 else _pf(w, "dark_oak_fence") if False else w.b("air") if False else
                    w.b("iron_bars", north=(x, z - 1) in menge, south=(x, z + 1) in menge,
                        east=(x + 1, z) in menge, west=(x - 1, z) in menge, waterlogged=False))


def rechteck(x0, z0, x1, z1):
    return ([(x, z0) for x in range(x0, x1 + 1)] + [(x1, z) for z in range(z0 + 1, z1 + 1)] +
            [(x, z1) for x in range(x1 - 1, x0 - 1, -1)] + [(x0, z) for z in range(z1 - 1, z0, -1)])


def friedhofstor(w, x, z, breite=3, H=5, mat="polished_blackstone_bricks", wand="polished_blackstone_brick"):
    for sx in (-1, 1):
        px = x + sx * (breite // 2 + 1)
        for y in range(1, H + 1):
            for dx in (0, sx):
                w.setze(px + dx, y, z, w.b(mat) if y < H else w.b(f"{wand}_slab", type="bottom", waterlogged=False))
        w.setze(px, H + 1, z, w.b("soul_lantern", hanging=False, waterlogged=False))
    for dx in range(-(breite // 2), breite // 2 + 1):
        w.setze(x + dx, H, z, w.b("iron_bars", east=True, west=True, north=False, south=False, waterlogged=False))
        w.setze(x + dx, H - 1, z, w.b("chain", axis="x", waterlogged=False) if dx == 0 else
                w.b("iron_bars", east=True, west=True, north=False, south=False, waterlogged=False))
        for y in range(1, 3):
            w.setze(x + dx, y, z, w.b("iron_bars", east=True, west=True, north=False, south=False,
                                      waterlogged=False) if abs(dx) == breite // 2 else w.b("air") if False else None) \
                if abs(dx) == breite // 2 else None


def spinnweben(w, anteil=0.02, nur_ecken=True):
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 1 and rng.random() < anteil and w.frei(x, y - 1, z):
            w.setze(x, y - 1, z, w.b("cobweb"))


def nebel(w, R, cx=0, cz=0, anteil=0.02):
    """Bodennebel-Andeutung: weiße Teppiche und Spinnweben in Senken (nur Optik)."""
    rng = w.rng
    for x, z in scheibe(R, cx, cz):
        if w.frei(x, 1, z) and (x, 0, z) in w.bloecke and rng.random() < anteil:
            w.setze(x, 1, z, w.b("cobweb") if rng.random() < 0.3 else w.b("white_carpet") if False else w.b("cobweb"))


def krummer_turm(w, cx, cz, y0, H, R, wand, neigung=2.0, fenster="purple_stained_glass", dach=None, knick=2.5):
    """Schiefer Turm mit Fenstern, Kragstufen und optionalem Hexenhut-Dach. Gibt Spitzenposition zurück."""
    rng = w.rng
    for y in range(y0, y0 + H):
        t = (y - y0) / H
        ox = neigung * t * t
        rr = R * (1.0 - 0.15 * t)
        for x, z in kreisrand(rr):
            fen = (y - y0) % 5 == 3 and (abs(x) < 0.6 or abs(z) < 0.6)
            p = (round(cx + x + ox), y, cz + z)
            w.setze(*p, w.b(fenster) if fen else wand(*p, t))
        if (y - y0) % 7 == 6:
            for x, z in kreisrand(rr + 0.8):
                w.setze(round(cx + x + ox), y, cz + z, wand(round(cx + x + ox), y, cz + z, 0.9))
    top_x = round(cx + neigung)
    if dach is not None:
        hexenhut(w, dach, top_x, cz, y0 + H, R + 1, _r(R * 2.2 + 3), knick)
    return top_x, y0 + H


def hexenhut(w, D, cx, cz, y0, R, H, knick=2.5, krempe=True):
    """Spitzhut-Dach mit Krempe und abknickender Spitze."""
    if krempe:
        for x, z in kreisrand(R + 1):
            w.setze(cx + x, y0, cz + z, D.platte(cx + x, y0, cz + z))
    for k in range(H + 1):
        t = k / H
        r = R * (1 - t) ** 1.6
        ox = round(knick * t ** 2.5)
        oz = round(knick * 0.4 * t ** 3)
        if r < 0.6:
            w.setze(cx + ox, y0 + k, cz + oz, D.voll(cx + ox, y0 + k, cz + oz))
            continue
        for x, z in scheibe(r):
            rand = math.hypot(x, z) > r - 1.0
            p = (cx + x + ox, y0 + k, cz + z + oz)
            if rand:
                f = ("west" if x > 0 else "east") if abs(x) >= abs(z) else ("north" if z > 0 else "south")
                w.setze(*p, D.treppe(*p, f))
            else:
                w.setze(*p, D.voll(*p))


# ============================================================================ FRIEDHOF & SPUK


def _sp(seed):
    """Spukstil: 0 = Schwarzstein/Seelenfeuer, 1 = Tiefenschiefer/Moos."""
    return _stil(seed)


def friedhof(seed, g=1):
    """Ummauerter Friedhof: schmiedeeisernes Tor mit Seelenlaternen, Grabreihen aller Art (Kreuze, Obelisken,
    Totenköpfe), Kieswege, knorrige tote Bäume, Gruftkapelle in der Ecke und Bodennebel aus Spinnweben."""
    w = _welt(seed)
    u = U[g]
    a = _r(9 * u + 5)
    b = _r(7 * u + 4)
    spukboden(w, max(a, b) + 6)
    pts = rechteck(-a, -b, a, b)
    tor = {(x, b) for x in range(-2, 3)}
    eisenzaun(w, [p for p in pts if p not in tor], 2 + (g >= 2))
    friedhofstor(w, 0, b, 3, 4 + g)
    for z in range(-b + 1, b + 1):
        for x in (-1, 0, 1):
            w.setze(x, 0, z, w.b("gravel") if (x + z) % 3 else MB.pflaster(w, "cobblestone", "running_bond"))
    stein = GRAB_STEINE[(seed // 3) % 3 + (3 if _sp(seed) == 0 else 0)]
    for z in range(-b + 3, b - 2, 4):
        for x in list(range(-a + 2, -2, 2)) + list(range(3, a - 1, 2)):
            if w.rng.random() < 0.9:
                grab(w, x, z, "south", stein=stein if w.rng.random() < 0.6 else None)
    for (x, z) in ((-a + 2, -b + 2), (a - 3, b - 4)):
        knorrbaum(w, x, z, 6 * u + 4, "dark_oak" if _sp(seed) == 0 else "spruce")
    if g >= 1:
        st = P.Stil(w, wand="schwarzstein" if _sp(seed) == 0 else "tiefenschiefer", sockel="schwarzstein",
                    gesims="polished_blackstone_brick" if _sp(seed) == 0 else "deepslate_brick",
                    dach="mcw_schwarz" if _sp(seed) == 0 else "schiefer", holz="dark_oak", laeden=False, blumen=0,
                    fenster="purple_stained_glass", fensterart="bogen")
        P.gebaeude(w, st, a - 6, -b + 1, a - 1, -b + 5, y0=1, etagen=1, eh=5, dach="sattel", tuer="west",
                   gauben=False, kamine=0, steil=True)
    nebel(w, max(a, b), anteil=0.015)
    hohl(w, 2)
    return w


def mausoleum(seed, g=1):
    """Gotisches Mausoleum: Säulenportikus, Bronzetür, Buntglas-Rosette, Giebel mit Engelsfigur, Urnen an den
    Stufen und Grabplatten im Vorhof."""
    from motive import figur
    w = _welt(seed)
    u = U[g]
    a = _r(4 * u + 2, 3)
    b = _r(5 * u + 3, 4)
    s = sakralstil(w, seed, "schwarz", "tief")
    spukboden(w, b + 8)
    H = _r(6 * u + 4, 5)
    for k in range(2):
        for x in range(-a - 2 + k, a + 3 - k):
            for z in range(-b - 2 + k, b + 4 - k):
                w.setze(x, k + 1, z, s.sockel(x, k + 1, z, 0.2))
    top = halle(w, s, -a, -b, a, b, 3, H, achse="z", fenster_abst=3, strebe=g >= 1, fialen=g >= 2)
    for x in (-a, a - 0):
        for zz in (b + 2,):
            pass
    for x in range(-a, a + 1, max(2, a)):
        for y in range(3, 3 + H):
            w.setze(x, y, b + 2, w.b("polished_basalt", axis="y") if _sp(seed) == 0 else w.b("deepslate_tile_wall",
                                                                                                   up=True,
                                                                                                   north="none",
                                                                                                   south="none",
                                                                                                   east="none",
                                                                                                   west="none",
                                                                                                   waterlogged=False))
    for x in range(-a - 1, a + 2):
        for z in range(b + 1, b + 4):
            w.setze(x, 3 + H, z, s.sockel(x, 3 + H, z, 0.9))
    for y in range(3, 6):
        w.bloecke.pop((0, y, b), None)
    w.setze(0, 3, b, w.b("iron_door", facing="south", half="lower", hinge="left", open=False, powered=False))
    w.setze(0, 4, b, w.b("iron_door", facing="south", half="upper", hinge="left", open=False, powered=False))
    for x in (-a - 1, a + 1):
        w.setze(x, 3, b + 3, w.b("decorated_pot", facing="south", cracked=True, waterlogged=False))
        w.setze(x, 4, b + 3, w.b("soul_lantern", hanging=False, waterlogged=False))
    S = Skulptur(w, 0.32 + 0.06 * g)
    S.mat("k", bl(w, "calcite" if _sp(seed) else "smooth_quartz"))
    S.mat("a", bl(w, "calcite"))
    S.mat("d", bl(w, "gray_concrete"))
    S.mat("g", bl(w, "soul_lantern"))
    figur(S, "elf", "kniend")
    for sx in (-1, 1):
        S.plus(lambda X, Y, Z, sx=sx: (((X - sx * 3.5) / 3.2) ** 2 + ((Y - 13) / 5) ** 2 < 1) &
               (np.abs(Z + 1.5) < 0.6), "k")
    S.rendern((-8, -4, -4), (8, 22, 4), versatz=(0.5, top + 1.01, b + 1.5))
    for i in range(4):
        grab(w, -a - 4 + (i % 2) * (2 * a + 8), b + 4 + (i // 2) * 3, "south", art=1 + i % 3)
    hohl(w, 2)
    return w


def gruft(seed, g=1):
    """Gruft im Hügel: grasbewachsener Erdhügel mit gemauertem Spitzbogenportal, Treppe hinab ins Dunkel,
    Schädelnischen, Gittertor und zwei Wächterstatuen aus Stein."""
    w = _welt(seed)
    u = U[g]
    R = 7 * u + 5
    spukboden(w, _r(R + 6))
    r_n = Rauschen(w, 4)
    for x, z in scheibe(R):
        d = math.hypot(x, z * 1.2) / R
        hh = int((1 - d * d) * (4 * u + 3) * (0.85 + 0.3 * r_n(x, 0, z)))
        for y in range(1, hh + 1):
            w.setze(x, y, z, w.b("grass_block", snowy=False) if y == hh else w.b("dirt") if y > hh - 3 else
                    w.b("stone"))
        if hh > 0 and w.rng.random() < 0.08:
            w.setze(x, hh + 1, z, w.b(["dead_bush", "fern", "grass"][int(w.rng.integers(3))]))
    pm = Mat(w, ["mossy_stone_bricks", "stone_bricks", "cracked_stone_bricks", "cobblestone"]) if _sp(seed) else \
        Mat(w, ["cracked_polished_blackstone_bricks", "polished_blackstone_bricks", "blackstone"])
    pw = 2
    ph = _r(3 * u + 3, 4)
    zf = round(R * 0.55)
    for x in range(-pw - 2, pw + 3):
        for y in range(1, ph + 3):
            bog = (x / (pw + 0.5)) ** 2 + ((y - ph + 1.5) / 2.0) ** 2 < 1 or (abs(x) <= pw and y < ph - 1)
            for z in range(zf - 1, zf + 2):
                if bog:
                    w.bloecke.pop((x, y, z), None)
                else:
                    w.setze(x, y, z, pm(x, y, z, y / (ph + 3)))
    for k in range(_r(5 * u + 3)):
        for x in range(-pw, pw + 1):
            w.setze(x, -k, zf - 1 - k, w.b("stone_brick_stairs", facing="south", half="bottom", shape="straight",
                                            waterlogged=False))
            for y in range(1 - k, 1 - k + ph):
                w.bloecke.pop((x, y, zf - 1 - k), None) if y > -k else None
        for sx in (-pw - 1, pw + 1):
            for y in range(-k, ph - k + 1):
                w.setze(sx, y, zf - 1 - k, pm(sx, y, zf - 1 - k, 0.3) if (y + k) % 3 else schaedel(w, rot=0)
                        if False else w.b("bone_block", axis="y") if (k + y) % 4 == 0 else pm(sx, y, zf - 1 - k, 0.3))
        w.setze(0, ph - k, zf - 1 - k, w.b("soul_lantern", hanging=True, waterlogged=False)) if k % 3 == 1 else None
    for x in range(-pw, pw + 1):
        w.setze(x, 1, zf + 1, w.b("iron_bars", east=True, west=True, north=False, south=False, waterlogged=False)
                if x != 0 else w.b("air") if False else w.b("iron_bars", east=True, west=True, north=False,
                                                            south=False, waterlogged=False))
        w.bloecke.pop((x, 1, zf + 1), None) if abs(x) < 1 else None
    for sx in (-1, 1):
        x = sx * (pw + 4)
        for y in (1, 2):
            w.setze(x, y, zf + 2, pm(x, y, zf + 2, 0.5))
        w.setze(x, 3, zf + 2, w.b("carved_pumpkin", facing="south") if False else schaedel(w, "wither_skeleton_skull", 0))
    knorrbaum(w, -round(R * 0.4), -round(R * 0.2), 5 * u + 4, "dark_oak", y0=_r(3 * u + 2))
    return w


def spukhaus(seed, g=2):
    """Viktorianisches Spukhaus: verwinkeltes Herrenhaus mit Turmerker, Mansarddach, zerbrochenen Fenstern,
    schiefen Läden, Veranda, verwildertem Garten mit Kürbissen und rostigem Zaun."""
    w = _welt(seed)
    u = U[g]
    a, b = _r(5 * u + 3, 4), _r(4 * u + 2, 3)
    spukboden(w, a + 9)
    st = P.Stil(w, wand=Mat(w, ["dark_oak_planks", "spruce_planks", "stripped_dark_oak_log", "dark_oak_planks"])
                if _sp(seed) else Mat(w, ["gray_terracotta", "cyan_terracotta", "light_gray_terracotta"]),
                sockel="schwarzstein", gesims="deepslate_brick" if _sp(seed) else "polished_blackstone_brick",
                dach="mcw_schwarz" if _sp(seed) == 0 else "schindel_grau", holz="dark_oak", laeden=True, blumen=0,
                fenster="black_stained_glass_pane" if False else "gray_stained_glass_pane",
                licht="soul_lantern")
    yt = P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2 + (g >= 2), eh=4, dach="walm", tuer="south", kamine=2)
    P.turm(w, st, a, b, 1, _r(14 * u + 6), max(2.0, 2.2 * u), dach="kegel", krone=False, fahne=None,
           spitze="lightning_rod", fenster=5)
    for x in range(-a, a + 1):
        for z in (b + 1, b + 2, b + 3):
            w.setze(x, 1, z, w.b("dark_oak_planks") if (x + z) % 4 else w.b("dark_oak_slab", type="bottom",
                                                                                waterlogged=False))
        if x % 3 == 0:
            for y in (2, 3, 4):
                w.setze(x, y, b + 3, _pf(w, "dark_oak_fence"))
        w.setze(x, 5, b + 3, w.b("dark_oak_slab", type="bottom", waterlogged=False))
        w.setze(x, 5, b + 2, w.b("dark_oak_slab", type="bottom", waterlogged=False))
        w.setze(x, 5, b + 1, w.b("dark_oak_slab", type="bottom", waterlogged=False))
    rng = w.rng
    for (x, y, z), bk in list(w.bloecke.items()):
        n = w.P.name(bk)
        if "glass_pane" in n and rng.random() < 0.25:
            w.bloecke[(x, y, z)] = w.b("cobweb") if rng.random() < 0.5 else w.b("air") if False else w.b("cobweb")
    pts = rechteck(-a - 6, -b - 6, a + 6, b + 8)
    eisenzaun(w, [p for p in pts if abs(p[0]) > 1 or p[1] != b + 8], 1, spitzen=False)
    for i in range(8):
        x, z = int(rng.integers(-a - 5, -a)), int(rng.integers(b + 1, b + 7))
        w.setze(x, 1, z, w.b("jack_o_lantern", facing="south") if i % 3 == 0 else w.b("pumpkin"))
    knorrbaum(w, a + 5, -b - 3, 7 * u + 4, "dark_oak")
    knorrbaum(w, -a - 4, -b - 3, 5 * u + 3, "spruce")
    spinnweben(w, 0.01)
    hohl(w, 2)
    return w


def kraehenbaum(seed, g=2):
    """Krähenbaum: uralter, riesiger toter Baum mit weit ausgreifenden Ästen, Krähen (schwarze Blöcke),
    hängenden Seelenlaternen und Ketten, an den Wurzeln Schädel und Kerzen."""
    w = _welt(seed)
    u = U[g]
    H = 10 * u + 6
    spukboden(w, _r(H * 0.9 + 4))
    enden = knorrbaum(w, 0, 0, H, "dark_oak" if _sp(seed) == 0 else "mangrove")
    rng = w.rng
    for i, (x, y, z) in enumerate(enden):
        r = rng.random()
        if r < 0.3:
            w.setze(x, y + 1, z, w.b("black_wool") if rng.random() < 0.5 else w.b("black_concrete"))
            w.setze(x + 1, y + 1, z, w.b("black_carpet")) if rng.random() < 0.5 else None
        elif r < 0.55:
            for k in range(1, 3 + int(rng.integers(0, 3))):
                w.setze(x, y - k, z, w.b("chain", axis="y", waterlogged=False))
            w.setze(x, y - 3 - int(rng.integers(0, 3)) + 0, z, w.b("soul_lantern", hanging=True, waterlogged=False))
    for x, z in kreisrand(3.5):
        if rng.random() < 0.4:
            w.setze(x, 1, z, schaedel(w) if rng.random() < 0.4 else kerze(w, "black" if rng.random() < 0.5 else None))
    hohl(w, 2)
    return w


def totenwaechter(seed, g=2):
    """Der Totenwächter: kolossale Kapuzengestalt mit Sense über einem Gräberfeld, im Inneren der Kapuze glühen
    Seelenlichter; zu Füßen ein Ring aus Grabsteinen."""
    w = _welt(seed)
    u = U[g]
    s = 0.55 * u + 0.25
    R = _r(9 * s + 5)
    spukboden(w, R + 4)
    stoff = Mat(w, ["blackstone", "polished_blackstone", "gray_concrete", "black_concrete"] if _sp(seed) == 0 else
                ["deepslate", "cobbled_deepslate", "polished_deepslate", "gray_concrete"], kontrast=0.8)
    S = Skulptur(w, s)
    S.mat("k", sk(stoff, 0, 30 * s))
    S.mat("g", bl(w, "soul_lantern" if False else "sea_lantern" if _sp(seed) else "shroomlight"))
    S.mat("d", bl(w, "black_concrete"))
    S.mat("m", bl(w, "iron_block"))
    S.mat("h", bl(w, "dark_oak_log"))
    # Robe: Kegel
    S.plus(lambda X, Y, Z: (X * X + Z * Z < (5.5 - Y * 0.22) ** 2) & (Y >= 0) & (Y < 17), "k")
    S.plus(ell(0, 18.5, 0, 3.2, 3.6, 3.2), "k")
    S.plus(ell(0, 18.0, 1.6, 2.0, 2.4, 2.0), "d")
    for sz in (-0.7, 0.7):
        S.plus(ell(sz, 18.6, 2.6, 0.45, 0.35, 0.3), "g")
    S.plus(kap((-3.5, 15, 0), (-5.5, 9, 2), 1.4, 1.1), "k")
    S.plus(kap((3.5, 15, 0), (5.0, 10, 2), 1.4, 1.1), "k")
    S.plus(kap((5.4, 1, 3), (5.4, 27, 3), 0.45, 0.45), "h")
    S.plus(lambda X, Y, Z: (np.abs(Z - 3) < 0.5) & (((X - 0.5) / 5.5) ** 2 + ((Y - 25.5) / 3) ** 2 < 1) &
           (((X - 0.0) / 5.5) ** 2 + ((Y - 24.0) / 2.6) ** 2 > 1) & (X < 5.4), "m")
    S.rendern((-8, 0, -6), (8, 30, 6), versatz=(0.5, 1.01, 0.5), dreh=dreh_y(0.0))
    for i in range(10):
        a = i / 10 * 2 * math.pi
        grab(w, round(math.cos(a) * (R - 2)), round(math.sin(a) * (R - 2)),
             "south" if math.sin(a) < 0 else "north", art=i % 5)
    hohl(w, 2)
    return w


def friedhofskapelle(seed, g=2):
    """Friedhofskapelle: kleines gotisches Schiff mit Buntglasfenstern, spitzem Dachreiter mit Glocke, Vorhalle,
    eingesunkene Gräber rund herum und ein Totenkopf-Fries."""
    w = _welt(seed)
    u = U[g]
    a, b = _r(6 * u + 4, 5), _r(3 * u + 2, 3)
    s = sakralstil(w, seed, "schwarz", "moos")
    spukboden(w, a + 8)
    H = _r(5 * u + 4, 5)
    top = halle(w, s, -a, -b, a, b, 1, H, achse="x", fenster_abst=3)
    for y in range(top, top + _r(5 * u + 4)):
        for x in (-1, 0):
            for z in (-1, 0):
                w.setze(a - 2 + x, y, z, s.sockel(a - 2 + x, y, z, 0.6) if (y - top) % 3 else w.b("iron_bars",
                        north=True, south=True, east=True, west=True, waterlogged=False))
    yk = top + _r(5 * u + 4)
    w.setze(a - 2, yk - 2, 0, w.b("bell", attachment="ceiling", facing="north", powered=False))
    for k in range(4):
        r = 1.6 - k * 0.45
        for x, z in scheibe(r, a - 2, 0):
            w.setze(x, yk + k, z, s.dach.voll(x, yk + k, z))
    w.setze(a - 2, yk + 4, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for y in (1, 2):
        w.bloecke.pop((-a, y, 0), None)
    for i in range(14):
        x = int(w.rng.integers(-a - 6, a + 7))
        z = int(w.rng.choice([-b - 5, -b - 3, b + 3, b + 5]))
        grab(w, x, z, "south" if z > 0 else "north")
    hohl(w, 2)
    return w


def beinhaus(seed, g=1):
    """Beinhaus: Gewölbebau aus Knochenblöcken und Tiefenschiefer, Fassade mit Schädelreihen, Kerzen in den
    Nischen, Rundfenster und eine Totenlaterne davor."""
    w = _welt(seed)
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    spukboden(w, a + 7)
    H = _r(4 * u + 3, 4)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            rand = x in (-a, a) or z in (-b, b)
            for y in range(1, H + 1):
                if rand:
                    w.setze(x, y, z, w.b("bone_block", axis="y") if (x + y) % 3 else w.b("polished_deepslate")
                            if y % 2 else w.b("deepslate_tiles"))
            w.setze(x, 0, z, w.b("deepslate_tiles"))
    for k in range(b + 2):
        for x in range(-a - 1, a + 2):
            for z in (-b - 1 + k, b + 1 - k):
                w.setze(x, H + 1 + k, z, w.b("deepslate_tile_stairs", facing="south" if z < 0 else "north",
                                             half="bottom", shape="straight", waterlogged=False) if z != 0 or
                        k <= b else w.b("deepslate_tile_slab", type="bottom", waterlogged=False))
    for x in range(-a + 1, a, 1):
        if x % 2 == 0:
            w.setze(x, H, b + 1, schaedel(w, rot=0))
            w.setze(x, 2, b + 1, kerze(w, "white"))
    for y in (1, 2, 3):
        w.bloecke.pop((0, y, b), None)
    w.setze(0, 4, b, w.b("bone_block", axis="x"))
    for y in range(1, 5):
        w.setze(0, y, b + 5, w.b("polished_deepslate_wall", up=True, north="none", south="none", east="none",
                                 west="none", waterlogged=False) if y < 4 else w.b("soul_lantern", hanging=False,
                                                                                   waterlogged=False))
    hohl(w, 2)
    return w


def kirchenruine(seed, g=2):
    """Kirchenruine: eingestürzte gotische Kirche ohne Dach, leere Spitzbogenfenster, ein halber Turm,
    Schutthaufen, Efeu und Moos, im Schiff wachsen junge Birken."""
    from kathedralen import abteiruine
    w = abteiruine(seed, g)
    rng = w.rng
    for (x, y, z), bk in list(w.bloecke.items()):
        n = w.P.name(bk)
        if "stained_glass" in n:
            w.bloecke[(x, y, z)] = w.b("cobweb") if rng.random() < 0.3 else w.b("air") if False else w.b("cobweb")
            if rng.random() < 0.7:
                del w.bloecke[(x, y, z)]
    for (x, y, z) in list(w.bloecke):
        if y == 0 and rng.random() < 0.05 and w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("dead_bush") if rng.random() < 0.5 else w.b("cobweb"))
    return w


def irrlichtsumpf(seed, g=1):
    """Irrlichtsumpf: düsteres Moor mit Wasserlöchern, Mangroven-Gerippen, Seelenlaternen auf Pfählen (Irrlichter),
    halb versunkenen Grabsteinen und einem verrotteten Steg."""
    w = _welt(seed)
    u = U[g]
    R = _r(12 * u + 6)
    spukboden(w, R, nass=True)
    rng = w.rng
    for i in range(3 + g * 2):
        a = rng.random() * 2 * math.pi
        d = R * (0.3 + 0.6 * rng.random())
        knorrbaum(w, round(math.cos(a) * d), round(math.sin(a) * d), 4 * u + 3 + rng.random() * 3, "mangrove",
                  krone="mangrove" if rng.random() < 0.4 else None)
    for i in range(6 + 3 * g):
        a = rng.random() * 2 * math.pi
        d = R * rng.random() * 0.9
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        hh = 1 + int(rng.integers(0, 3))
        for y in range(1, hh + 1):
            w.setze(x, y, z, _pf(w, "mangrove_fence"))
        w.setze(x, hh + 1, z, w.b("soul_lantern", hanging=False, waterlogged=False))
    for z in range(-R + 2, R - 1):
        if rng.random() < 0.85:
            w.setze(round(math.sin(z * 0.25) * 2), 1, z, w.b("mangrove_slab", type="bottom", waterlogged=False)
                    if rng.random() < 0.8 else w.b("mangrove_planks"))
    for i in range(5):
        grab(w, int(rng.integers(-R // 2, R // 2)), int(rng.integers(-R // 2, R // 2)), art=5)
    return w


def kuerbisfeld(seed, g=1):
    """Spuk-Kürbisfeld: Reihen von Kürbissen und Kürbislaternen, eine große Vogelscheuche, krumme Zäune,
    ein kleiner Schuppen und Raben."""
    w = _welt(seed)
    u = U[g]
    a = _r(8 * u + 5)
    spukboden(w, a + 4)
    rng = w.rng
    for x in range(-a, a + 1):
        for z in range(-a, a + 1, 3):
            w.setze(x, 0, z, w.b("farmland", moisture=0))
            if rng.random() < 0.45:
                w.setze(x, 1, z, w.b("jack_o_lantern", facing=["north", "south", "east", "west"][int(rng.integers(4))])
                        if rng.random() < 0.25 else w.b("carved_pumpkin", facing="south") if rng.random() < 0.15
                        else w.b("pumpkin"))
            elif rng.random() < 0.3:
                w.setze(x, 1, z, w.b("attached_pumpkin_stem", facing="east") if False else w.b("dead_bush"))
    for p in rechteck(-a - 1, -a - 1, a + 1, a + 1):
        if rng.random() < 0.85:
            w.setze(p[0], 1, p[1], MB.lattenzaun(w, "spruce") if rng.random() < 0.5 else _pf(w, "spruce_fence"))
    vogelscheuche(w, 0, 0, 0.45 + 0.12 * g, seed)
    st = P.Stil(w, wand="holz_dunkel", sockel="graustein", gesims="stone_brick", dach="mcw_stroh", holz="spruce",
                laeden=False, blumen=0)
    P.gebaeude(w, st, a + 3, -3, a + 8, 3, y0=1, etagen=1, eh=3, dach="sattel", tuer="west", gauben=False, kamine=0)
    return w


def vogelscheuche(w, x, z, s, seed=0):
    S = Skulptur(w, s)
    S.mat("k", bl(w, "hay_block"))
    S.mat("h", bl(w, "spruce_log"))
    S.mat("s", bl(w, "brown_wool"))
    S.mat("p", bl(w, "jack_o_lantern"))
    S.mat("t", bl(w, "black_wool"))
    S.plus(kap((0, 0, 0), (0, 22, 0), 0.6, 0.6), "h")
    S.plus(kap((-9, 17, 0), (9, 17, 0), 0.6, 0.6), "h")
    S.plus(kap((0, 9, 0), (0, 17.5, 0), 2.4, 2.8), "s")
    S.plus(kap((-2.5, 17, 0), (-8, 16.3, 0), 1.2, 0.9), "s")
    S.plus(kap((2.5, 17, 0), (8, 16.6, 0), 1.2, 0.9), "s")
    for sx in (-8.8, 8.8):
        S.plus(ell(sx, 16, 0, 0.9, 1.6, 0.9), "k")
    S.plus(kap((-1, 9, 0), (-1.4, 5, 0.3), 1.0, 0.6), "k")
    S.plus(kap((1, 9, 0), (1.4, 5, 0.3), 1.0, 0.6), "k")
    S.plus(ell(0, 21, 0, 2.6, 2.4, 2.6), "p")
    S.plus(lambda X, Y, Z: (X * X + Z * Z < 16) & (np.abs(Y - 23.2) < 0.45), "t")
    S.plus(kap((0, 23, 0), (0.8, 27.5, 0.5), 2.2, 0.3), "t")
    S.rendern((-11, 0, -5), (11, 29, 5), versatz=(x + 0.5, 1.01, z + 0.5))


def huegelgrab(seed, g=2):
    """Hügelgrab der Ahnen: langer Grabhügel mit Steinkranz, monumentalem Trilithon-Eingang, Runenmenhiren in
    einer Allee und Opferschale mit Seelenfeuer."""
    w = _welt(seed)
    u = U[g]
    L, B = 10 * u + 5, 5 * u + 3
    spukboden(w, _r(L + 8))
    r_n = Rauschen(w, 3)
    fels = Mat(w, ["stone", "andesite", "mossy_cobblestone", "cobblestone", "tuff"], kontrast=1.2)
    for x in range(-_r(L), _r(L) + 1):
        for z in range(-_r(B), _r(B) + 1):
            d = (x / L) ** 2 + (z / B) ** 2
            if d < 1:
                hh = int((1 - d) * (3.5 * u + 2) * (0.9 + 0.2 * r_n(x, 0, z)))
                for y in range(1, hh + 1):
                    w.setze(x, y, z, w.b("grass_block", snowy=False) if y == hh else w.b("dirt"))
            elif d < 1.15 and (x + z) % 3 == 0:
                w.setze(x, 1, z, fels(x, 1, z, 0.3))
    xe = _r(L)
    for y in range(1, _r(3 * u + 3) + 1):
        for z in (-2, 2):
            w.setze(xe + 1, y, z, fels(xe + 1, y, z, y / 6))
    for z in range(-3, 4):
        w.setze(xe + 1, _r(3 * u + 3) + 1, z, fels(xe + 1, 6, z, 0.9))
    for y in range(1, _r(3 * u + 3) + 1):
        for z in (-1, 0, 1):
            for x in range(xe - 3, xe + 2):
                w.bloecke.pop((x, y, z), None)
    for i in range(3 + g):
        for sz in (-1, 1):
            x = xe + 4 + i * 4
            hh = 2 + int(w.rng.integers(0, 2 + g))
            for y in range(1, hh + 1):
                w.setze(x, y, sz * 3, fels(x, y, sz * 3, y / hh) if y < hh else w.b("chiseled_stone_bricks"))
    xs = xe + 6 + (3 + g) * 4
    w.setze(xs, 1, 0, w.b("polished_andesite"))
    w.setze(xs, 2, 0, w.b("soul_campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


def katakomben(seed, g=2):
    """Katakomben-Eingang: Säulenhalle aus Tiefenschiefer über einer breiten Treppe ins Erdreich, Knochennischen
    in den Wänden, Gitter, Ketten und Seelenfackeln."""
    w = _welt(seed)
    u = U[g]
    a = _r(4 * u + 3, 4)
    spukboden(w, a + 9)
    mat = Mat(w, ["deepslate_bricks", "cracked_deepslate_bricks", "deepslate_tiles", "polished_deepslate"])
    H = _r(4 * u + 4, 5)
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            w.setze(x, 0, z, mat(x, 0, z, 0.2))
    saeulen = set()
    for x in range(-a, a + 1, 3):
        saeulen |= {(x, -a), (x, a)}
    for z in range(-a, a + 1, 3):
        saeulen |= {(-a, z), (a, z)}
    for (x, z) in saeulen:
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b("polished_basalt", axis="y") if 1 < y < H else w.b("chiseled_deepslate"))
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            rand = max(abs(x), abs(z)) >= a - 1
            if rand:
                w.setze(x, H + 1, z, mat(x, H + 1, z, 0.8))
            if max(abs(x), abs(z)) == a + 1:
                w.setze(x, H + 2, z, w.b("deepslate_brick_wall", up=(x + z) % 3 == 0, north="none", south="none",
                                         east="none", west="none", waterlogged=False))
    for k in range(a):
        for x in range(-a + 1 + k, a - k):
            for z in range(-a + 1 + k, a - k):
                if max(abs(x), abs(z)) == a - 1 - k:
                    w.setze(x, H + 2 + k, z, w.b("deepslate_tile_stairs",
                                                 facing=("west" if x > 0 else "east") if abs(x) >= abs(z) else
                                                 ("north" if z > 0 else "south"), half="bottom", shape="straight",
                                                 waterlogged=False))
    w.setze(0, H + 2 + a, 0, w.b("soul_lantern", hanging=False, waterlogged=False))
    for k in range(a + 1):
        for x in range(-a + 2, a - 1):
            w.setze(x, -k, -a + 2 + k, w.b("deepslate_brick_stairs", facing="north", half="bottom", shape="straight",
                                           waterlogged=False))
            for y in range(-k + 1, 1):
                w.bloecke.pop((x, y, -a + 2 + k), None)
        for sx in (-a + 1, a - 1):
            w.setze(sx, -k, -a + 2 + k, w.b("bone_block", axis="y") if k % 2 else mat(sx, -k, -a + 2 + k, 0.4))
            w.setze(sx, -k + 1, -a + 2 + k, schaedel(w, rot=8) if k % 2 == 0 else mat(sx, 0, 0, 0.4))
    w.setze(0, H, 0, w.b("chain", axis="y", waterlogged=False))
    w.setze(0, H - 1, 0, w.b("soul_lantern", hanging=True, waterlogged=False))
    for x in (-a - 1, a + 1):
        w.setze(x, 2, a + 1, w.b("soul_wall_torch", facing="south"))
    hohl(w, 2)
    return w


def totengraeber(seed, g=1):
    """Totengräberhütte: schiefe Holzhütte mit Laterne, Schaufeln, offenen Gruben, Särge (Holzkisten),
    Karren mit Erde und ein kleiner Gräbergarten."""
    w = _welt(seed)
    u = U[g]
    a, b = _r(3 * u + 2, 3), _r(2.5 * u + 2, 3)
    spukboden(w, a + 9)
    st = P.Stil(w, wand="holz_dunkel", sockel="graustein", gesims="stone_brick", dach="schindel_grau" if _sp(seed)
                else "mcw_braun", holz="spruce", laeden=True, blumen=0, licht="soul_lantern")
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=4, dach="sattel", tuer="south", kamine=1, gauben=False)
    for k in range(3):
        x0 = a + 3 + k * 3
        for z in range(-1, 2):
            w.setze(x0, 0, z, w.b("air") if False else w.b("coarse_dirt"))
            w.bloecke.pop((x0, 0, z), None)
            w.setze(x0, -1, z, w.b("rooted_dirt"))
        w.setze(x0 + 1, 1, -2, w.b("coarse_dirt"))
        w.setze(x0 + 1, 2, -2, w.b("coarse_dirt")) if k == 1 else None
    for k in range(2):
        for z in range(3):
            w.setze(-a - 2, 1, -1 + z + k * 0, w.b("spruce_trapdoor", facing="north", half="bottom", open=False,
                                                    powered=False, waterlogged=False))
    w.setze(-a - 3, 1, 2, w.b("composter", level=7))
    for i in range(6):
        grab(w, -a - 7 + (i % 3) * 2, -b + (i // 3) * 4, "south")
    return w


def engelsgrab(seed, g=2):
    """Grab des weinenden Engels: große kniende Engelsfigur mit weiten Flügeln aus Kalzit auf einem Sockel,
    Kranz aus Wither-Rosen, umgeben von Säulen mit Seelenschalen."""
    from motive import figur
    w = _welt(seed)
    u = U[g]
    s = 0.45 * u + 0.2
    R = _r(8 * s + 6)
    spukboden(w, R + 4)
    sockel = Mat(w, ["polished_andesite", "smooth_stone", "stone_bricks"] if _sp(seed) else
                 ["polished_deepslate", "deepslate_tiles", "polished_blackstone"])
    for k in range(3):
        for x, z in scheibe(R * 0.45 - k):
            w.setze(x, k + 1, z, sockel(x, k + 1, z, k / 3))
    S = Skulptur(w, s)
    S.mat("k", sk(Mat(w, ["calcite", "smooth_quartz", "diorite", "white_concrete"]), 3, 3 + 24 * s))
    S.mat("a", bl(w, "calcite"))
    S.mat("d", bl(w, "light_gray_concrete"))
    S.mat("g", bl(w, "calcite"))
    figur(S, "elf", "kniend")
    for sx in (-1, 1):
        S.plus(lambda X, Y, Z, sx=sx: (((X - sx * 5.5) / 5.0) ** 2 + ((Y - 15) / 8.0) ** 2 < 1) &
               (np.abs(Z + 2.0 + 0.15 * np.abs(X)) < 0.7) & (Y > 5), "k")
    S.rendern((-12, -4, -6), (12, 25, 5), versatz=(0.5, 4.01, 0.5))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * (R - 1)), round(math.sin(a) * (R - 1))
        for y in range(1, 4 + g):
            w.setze(x, y, z, w.b("polished_basalt", axis="y") if _sp(seed) == 0 else w.b("quartz_pillar", axis="y"))
        w.setze(x, 4 + g, z, w.b("soul_campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for x, z in kreisrand(R * 0.45 + 1):
        if w.rng.random() < 0.6:
            w.setze(x, 1, z, w.b("wither_rose"))
    hohl(w, 2)
    return w


def gruftallee(seed, g=2):
    """Gruftallee: Reihe von Familiengrüften in verschiedenen Stilen (Giebel, Kuppel, Pyramide) an einem
    gepflasterten Weg mit Zypressen und Laternenpfählen."""
    w = _welt(seed)
    u = U[g]
    n = 2 + g
    L = n * 9 // 2 + 3
    spukboden(w, L + 6)
    for z in range(-L, L + 1):
        for x in (-1, 0, 1):
            w.setze(x, 0, z, MB.pflaster(w, "cobblestone", "running_bond") if (x + z) % 3 else w.b("gravel"))
        if z % 6 == 0:
            for sx in (-2, 2):
                MB.strassenlampe(w, sx, 1, z, seele=True)
    stile = [("schwarzstein", "polished_blackstone_brick"), ("tiefenschiefer", "deepslate_brick"),
             ("graustein", "stone_brick"), ("moosstein", "mossy_stone_brick"), ("kalkstein", "stone_brick")]
    for i in range(n):
        for sx in (-1, 1):
            z0 = -L + 2 + i * 9
            x0 = sx * 4 if sx > 0 else -4 - 5
            wnd, ges = stile[(i * 2 + (sx > 0) + seed) % len(stile)]
            st = P.Stil(w, wand=wnd, sockel="schwarzstein", gesims=ges, dach="schiefer", holz="dark_oak",
                        laeden=False, blumen=0, fenster="purple_stained_glass", fensterart="bogen")
            form = (i + (sx > 0)) % 3
            P.gebaeude(w, st, x0, z0, x0 + 5, z0 + 5, y0=1, etagen=1, eh=4,
                       dach=["sattel", "walm", "walm"][form], tuer="east" if sx < 0 else "west", gauben=False,
                       kamine=0, steil=form == 2)
            for y in range(1, 6 + 2 * g):
                w.setze(x0 + (6 if sx < 0 else -1), y, z0 + 7, laub(w, "spruce") if y > 1 else w.b("spruce_log",
                                                                                                    axis="y"))
    hohl(w, 2)
    return w


def spukturm(seed, g=2):
    """Schiefer Spukturm: verdrehter, sich neigender Turm aus Tiefenschiefer, schief sitzender Spitzhelm,
    leuchtende Fenster, Fledermausschwarm (schwarze Blöcke), Wurzeln und Schutt am Fuß."""
    w = _welt(seed)
    u = U[g]
    H = _r(18 * u + 8)
    R = 2.5 * u + 2
    spukboden(w, _r(R + 8))
    wand = Mat(w, ["deepslate_bricks", "cracked_deepslate_bricks", "cobbled_deepslate", "deepslate_tiles"]
               if _sp(seed) else ["blackstone", "polished_blackstone_bricks", "cracked_polished_blackstone_bricks"])
    D = P.Dach(w, "mcw_schwarz" if _sp(seed) == 0 else "schiefer")
    tx, ty = krummer_turm(w, 0, 0, 1, H, R, wand, neigung=2 + u, fenster="orange_stained_glass" if _sp(seed) else
                          "purple_stained_glass", dach=D, knick=2 + u)
    rng = w.rng
    for i in range(6 + 3 * g):
        x = round(tx + rng.normal(0, R + 2))
        z = round(rng.normal(0, R + 2))
        y = ty + int(rng.integers(-H // 3, 4))
        w.setze(x, y, z, w.b("black_concrete"))
    for i in range(10):
        x, z = int(rng.integers(-R - 4, R + 5)), int(rng.integers(-R - 4, R + 5))
        if w.frei(x, 1, z):
            w.setze(x, 1, z, wand(x, 1, z, 0.1) if rng.random() < 0.6 else w.b("cobbled_deepslate_slab",
                                                                                   type="bottom", waterlogged=False))
    hohl(w, 2)
    return w


def seelenschrein(seed, g=1):
    """Seelenfeuer-Schrein: offener Rundbau aus Basaltsäulen um ein Becken mit Seelenfeuer, Ketten mit
    Seelenlaternen, Seelensand-Ring, Schädel und schwarze Kerzen."""
    w = _welt(seed)
    u = U[g]
    R = 4 * u + 3
    spukboden(w, _r(R + 5))
    H = _r(5 * u + 3, 4)
    for x, z in scheibe(R + 1):
        w.setze(x, 0, z, w.b("soul_sand") if math.hypot(x, z) < R * 0.5 else w.b("polished_blackstone_bricks"))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b("polished_basalt", axis="y"))
        w.setze(x, H + 1, z, w.b("chiseled_polished_blackstone"))
    for x, z in kreisrand(R):
        w.setze(x, H + 2, z, w.b("polished_blackstone_brick_slab", type="bottom", waterlogged=False))
    for x, z in kreisrand(1.5):
        w.setze(x, 1, z, w.b("polished_blackstone_brick_wall", up=True, north="none", south="none", east="none",
                             west="none", waterlogged=False))
    w.setze(0, 1, 0, w.b("soul_campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for i in range(4):
        a = i / 4 * 2 * math.pi + 0.4
        x, z = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        for y in range(H - 1, H + 2):
            w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False))
        w.setze(x, H - 2, z, w.b("soul_lantern", hanging=True, waterlogged=False))
    for x, z in kreisrand(R * 0.75):
        if w.rng.random() < 0.3:
            w.setze(x, 1, z, kerze(w, "black") if w.rng.random() < 0.7 else schaedel(w))
    return w


def vergessener_friedhof(seed, g=2):
    """Vergessener Friedhof im Wald: überwucherte, schiefe Grabsteine zwischen Fichten und toten Bäumen, ein
    eingestürzter Torbogen, Moos, Pilze und verfallene Mauerreste."""
    import wald
    w = _welt(seed)
    u = U[g]
    R = _r(11 * u + 6)
    gelaende(w, R + 2, art="wald", dichte=0.8)
    rng = w.rng
    for i in range(int(R * R * 0.08)):
        a = rng.random() * 2 * math.pi
        d = R * math.sqrt(rng.random()) * 0.9
        grab(w, round(math.cos(a) * d), round(math.sin(a) * d), art=[5, 6, 1, 0, 3][i % 5],
             stein=GRAB_STEINE[1 + (i % 2)])
    for i in range(2 + g):
        a = rng.random() * 2 * math.pi
        d = R * (0.5 + 0.4 * rng.random())
        einfuegen(w, wald._baum(int(rng.integers(1, 10 ** 6)), "fichte", 0), round(math.cos(a) * d), 0,
                  round(math.sin(a) * d))
    knorrbaum(w, 2, -3, 6 * u + 4, "dark_oak", krone="dark_oak")
    m = Mat(w, ["mossy_stone_bricks", "mossy_cobblestone", "cracked_stone_bricks", "stone_bricks"])
    for x in range(-R + 2, -R + 8):
        for y in range(1, 2 + (x % 3)):
            w.setze(x, y, 2, m(x, y, 2, 0.3))
    for sx in (-1, 1):
        for y in range(1, 5):
            w.setze(sx * 2, y, R - 3, m(sx * 2, y, R - 3, 0.5))
    w.setze(-1, 5, R - 3, m(0, 5, 0, 0.5))
    for (x, y, z), bk in list(w.bloecke.items()):
        if y in (1, 2) and rng.random() < 0.15 and "wall" in w.P.name(bk):
            w.setze(x, y + 1, z, w.b("moss_carpet")) if w.frei(x, y + 1, z) else None
    return w


def geisterschiff_steg(seed, g=2):
    """Geistersteg: morscher Anleger in einem nebligen Moorsee, daran ein halb versunkenes Geisterboot mit
    zerfetzten Segeln (Spinnweben, graue Wolle) und Seelenlaternen."""
    w = _welt(seed)
    u = U[g]
    R = _r(12 * u + 6)
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("mud"))
    spukboden(w, R * 0.45, -R // 2, 0)
    for x in range(-R // 3, R // 4):
        for z in (-1, 0, 1):
            if w.rng.random() < 0.85:
                w.setze(x, 1, z, w.b("dark_oak_slab", type="bottom", waterlogged=False) if (x + z) % 4 else
                        w.b("dark_oak_planks"))
        if x % 3 == 0:
            for sz in (-2, 2):
                for y in (-1, 0, 1, 2):
                    w.setze(x, y, sz, w.b("dark_oak_log", axis="y"))
                w.setze(x, 3, sz, w.b("soul_lantern", hanging=False, waterlogged=False))
    L = _r(8 * u + 4)
    B = 2 * u + 1.5
    x0 = R // 4 + 2
    for i in range(L * 2 + 1):
        t = i / (2 * L)
        x = x0 + i // 2
        br = B * math.sin(t * math.pi) ** 0.6
        neig = 0.25
        for z in range(-round(br) - 1, round(br) + 2):
            if abs(z) <= br + 0.4:
                yy = round(-1 + abs(z) * 0.5 + neig * z)
                w.setze(x, yy, z, w.b("dark_oak_planks") if abs(z) >= br - 0.6 else w.b("dark_oak_slab", type="bottom",
                                                                                         waterlogged=False))
                if abs(z) >= br - 0.6:
                    w.setze(x, yy + 1, z, w.b("dark_oak_planks") if (x + z) % 3 else w.b("dark_oak_fence",
                                                                                          north=False, south=False,
                                                                                          east=True, west=True,
                                                                                          waterlogged=False))
    mx = x0 + L
    Hm = _r(9 * u + 4)
    for y in range(0, Hm):
        w.setze(mx, y, 0, w.b("dark_oak_log", axis="y"))
    for y in range(Hm // 2, Hm - 1):
        for z in range(-round(B) - 1, round(B) + 2):
            r = w.rng.random()
            if r < 0.55:
                w.setze(mx + 1, y, z, w.b("light_gray_wool") if r < 0.35 else w.b("cobweb"))
    w.setze(mx, Hm, 0, w.b("soul_lantern", hanging=False, waterlogged=False))
    return w


FRIEDHOF = {
    "friedhof": ("Friedhof", friedhof),
    "mausoleum": ("Mausoleum", mausoleum),
    "gruft": ("Gruft im Hügel", gruft),
    "spukhaus": ("Spukhaus", spukhaus),
    "kraehenbaum": ("Krähenbaum", kraehenbaum),
    "totenwaechter": ("Totenwächter", totenwaechter),
    "friedhofskapelle": ("Friedhofskapelle", friedhofskapelle),
    "beinhaus": ("Beinhaus", beinhaus),
    "kirchenruine": ("Kirchenruine", kirchenruine),
    "irrlichtsumpf": ("Irrlichtsumpf", irrlichtsumpf),
    "kuerbisfeld": ("Spuk-Kürbisfeld", kuerbisfeld),
    "huegelgrab": ("Hügelgrab", huegelgrab),
    "katakomben": ("Katakomben", katakomben),
    "totengraeber": ("Totengräberhütte", totengraeber),
    "engelsgrab": ("Grab des Engels", engelsgrab),
    "gruftallee": ("Gruftallee", gruftallee),
    "spukturm": ("Schiefer Spukturm", spukturm),
    "seelenschrein": ("Seelenfeuer-Schrein", seelenschrein),
    "vergessener_friedhof": ("Vergessener Friedhof", vergessener_friedhof),
    "geistersteg": ("Geistersteg", geisterschiff_steg),
}


# ============================================================================ HEXENWERK

HEXDACH = ["schindel_lila", "mcw_schwarz", "schindel_grau", "mcw_lila", "mcw_braun", "schindel_gruen"]


def _hexdach(w, seed, k=0):
    return P.Dach(w, HEXDACH[(seed + k) % len(HEXDACH)] if _stil(seed) else ["mcw_lila", "schindel_lila",
                                                                              "mcw_schwarz"][(seed // 7 + k) % 3])


def hexenwand(w, seed):
    if _stil(seed) == 0:
        return Mat(w, ["spruce_planks", "dark_oak_planks", "stripped_spruce_log", "mud_bricks", "spruce_planks"],
                   kontrast=1.1)
    return Mat(w, ["mossy_cobblestone", "cobblestone", "mud_bricks", "dark_oak_planks", "packed_mud"], kontrast=1.1)


def hexenhaus(w, seed, cx, cz, y0, R, H, D=None, knick=None, tuer="south", glas="lime_stained_glass"):
    """Runde, schiefe Hexenhütte mit Spitzhut-Dach, krummem Schornstein, Kerzen im Fenster."""
    wand = hexenwand(w, seed)
    D = D or _hexdach(w, seed)
    rng = w.rng
    for x, z in scheibe(R - 0.5):
        w.setze(cx + x, y0 - 1, cz + z, w.b("spruce_planks") if (x + z) % 3 else w.b("dark_oak_planks"))
    for y in range(y0, y0 + H):
        for x, z in kreisrand(R):
            p = (cx + x, y, cz + z)
            fen = (y - y0) in (1, 2) and (abs(x) <= 0.5 or abs(z) <= 0.5) and not (z > 0 and abs(x) < 1)
            w.setze(*p, w.b(glas) if fen else wand(*p, (y - y0) / H))
        for x, z in ((round(R * 0.7), round(R * 0.7)), (-round(R * 0.7), round(R * 0.7)),
                     (round(R * 0.7), -round(R * 0.7)), (-round(R * 0.7), -round(R * 0.7))):
            w.setze(cx + x, y, cz + z, w.b("dark_oak_log", axis="y"))
    dz = {"south": (0, 1), "north": (0, -1), "east": (1, 0), "west": (-1, 0)}[tuer]
    tx, tz = cx + round(dz[0] * R), cz + round(dz[1] * R)
    w.setze(tx, y0, tz, w.b("spruce_door", facing=tuer, half="lower", hinge="left", open=False, powered=False))
    w.setze(tx, y0 + 1, tz, w.b("spruce_door", facing=tuer, half="upper", hinge="left", open=False, powered=False))
    w.setze(tx + dz[0], y0 - 1, tz + dz[1], w.b("spruce_stairs", facing={"south": "north", "north": "south",
                                                                          "east": "west", "west": "east"}[tuer],
                                                 half="bottom", shape="straight", waterlogged=False))
    hexenhut(w, D, cx, cz, y0 + H, R + 1, _r(R * 3.2 + 4), knick if knick is not None else 2.5 + R * 0.7)
    kx, kz = cx - round(R * 0.6), cz - round(R * 0.4)
    for y in range(y0 + H - 2, y0 + H + _r(R * 1.5 + 2)):
        dxk = (y - y0 - H) // 3 if y > y0 + H else 0
        w.setze(kx + dxk, y, kz, w.b("cobblestone") if (y + kx) % 3 else w.b("mossy_cobblestone"))
    w.setze(kx + (_r(R * 1.5 + 2)) // 3, y0 + H + _r(R * 1.5 + 2), kz,
            w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    w.setze(cx, y0, cz, w.b("brewing_stand", has_bottle_0=True, has_bottle_1=False, has_bottle_2=True))
    for x, z in kreisrand(R - 1):
        if rng.random() < 0.15:
            w.setze(cx + x, y0, cz + z, w.b("barrel", facing="up", open=False) if rng.random() < 0.5 else
                    w.b("bookshelf"))


def hexenkessel(w, x, z, y=1, gross=False, inhalt="lime", R=2.3):
    """Kessel über Feuer: 1 Block (Kessel) oder groß (3x3 Schwarzstein-Topf mit grünem Gebräu)."""
    if not gross:
        w.setze(x, y, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
        w.setze(x, y + 1, z, w.b("water_cauldron", level=3))
        return
    Ri = int(math.ceil(R))
    hk = max(2, round(R * 0.9))
    for dx in range(-Ri, Ri + 1):
        for dz in range(-Ri, Ri + 1):
            r = math.hypot(dx, dz)
            if r <= R:
                w.setze(x + dx, y, z + dz, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                               waterlogged=False) if r < R - 0.8 else w.b("polished_blackstone"))
                if r > R - 0.8:
                    for yy in range(y + 1, y + hk + 1):
                        w.setze(x + dx, yy, z + dz, w.b("polished_blackstone_bricks"))
                    w.setze(x + dx, y + hk + 1, z + dz, w.b("polished_blackstone_brick_slab", type="bottom",
                                                            waterlogged=False))
                else:
                    for yy in range(y + 1, y + hk):
                        w.setze(x + dx, yy, z + dz, w.b("slime_block") if inhalt == "lime" else
                                w.b(f"{inhalt}_stained_glass"))
                    w.setze(x + dx, y + hk, z + dz, w.b(f"{inhalt}_stained_glass"))
                    if w.rng.random() < 0.3:
                        w.setze(x + dx, y + hk + 1, z + dz, w.b(f"{inhalt}_stained_glass"))


def kraeuterbuendel(w, x, y, z):
    w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False) if False else w.b("spore_blossom")
            if w.rng.random() < 0.3 else w.b("hanging_roots"))


def hexenhuette(seed, g=1):
    """Hexenhütte: runde schiefe Hütte mit hohem, abknickendem Spitzhut-Dach, krummem Schornstein, Kessel über
    dem Feuer im Vorgarten, Kürbisse, Pilze, Kräuterbüschel und ein knorriger Baum."""
    w = _welt(seed)
    u = U[g]
    R = 2.2 * u + 2
    spukboden(w, _r(R + 8))
    hexenhaus(w, seed, 0, 0, 1, R, _r(2 * u + 3, 4))
    hexenkessel(w, 0, round(R) + 3)
    rng = w.rng
    for i in range(6):
        a = rng.random() * math.pi + math.pi * 0.1
        d = R + 2 + rng.random() * 3
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if w.frei(x, 1, z):
            w.setze(x, 1, z, w.b(["pumpkin", "red_mushroom", "brown_mushroom", "carved_pumpkin"][i % 4], facing="south")
                    if i % 4 == 3 else w.b(["pumpkin", "red_mushroom", "brown_mushroom"][i % 3]))
    knorrbaum(w, -round(R) - 4, -round(R) - 2, 5 * u + 3, "dark_oak", krone="dark_oak" if _stil(seed) else None)
    for z in range(round(R) + 1, round(R) + 7):
        w.setze(0, 0, z, w.b("dirt_path") if z % 2 else MB.kiesel(w) if False else w.b("coarse_dirt"))
    return w


def alchemieturm(seed, g=2):
    """Alchemistenturm: schiefer Steinturm mit lila Fenstern und gewaltigem Hexenhut-Dach, Anbau-Labor,
    Balkon mit Braustand, Kupfer-Destille und leuchtenden Glaskolben."""
    w = _welt(seed)
    u = U[g]
    R = 2.4 * u + 2.2
    H = _r(14 * u + 7)
    spukboden(w, _r(R + 9))
    wand = Mat(w, ["stone_bricks", "mossy_stone_bricks", "cobblestone", "andesite", "cracked_stone_bricks"]
               if _stil(seed) else ["deepslate_bricks", "cobbled_deepslate", "polished_deepslate", "deepslate_tiles"])
    tx, ty = krummer_turm(w, 0, 0, 1, H, R, wand, neigung=1 + u, fenster="purple_stained_glass",
                          dach=_hexdach(w, seed), knick=2 + u)
    hexenhaus(w, seed, round(R) + 4, 2, 1, max(2.0, R * 0.8), _r(1.5 * u + 3, 3), tuer="east")
    for x, z in kreisrand(R + 1.5):
        w.setze(round(x + 1 + u * 0.5), H // 2, z, w.b("dark_oak_planks"))
        w.setze(round(x + 1 + u * 0.5), H // 2 + 1, z, _pf(w, "dark_oak_fence"))
    w.setze(-round(R) - 2, 1, 0, w.b("waxed_copper_block"))
    w.setze(-round(R) - 2, 2, 0, w.b("waxed_cut_copper"))
    w.setze(-round(R) - 2, 3, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    w.setze(-round(R) - 3, 1, 0, w.b("brewing_stand", has_bottle_0=True, has_bottle_1=True, has_bottle_2=True))
    for k, f in enumerate(["lime", "purple", "orange", "cyan"]):
        w.setze(-round(R) - 2 + k - 1, 1, 2, w.b(f"{f}_stained_glass"))
    hohl(w, 2)
    return w


def kesselplatz(seed, g=1):
    """Hexensabbat-Platz: riesiger brodelnder Kessel über dem Feuer, Baumstamm-Bänke im Kreis, Knochenhaufen,
    Kerzen, Hängeleuchten an toten Bäumen und Fläschchen-Regale."""
    w = _welt(seed)
    u = U[g]
    R = 6 * u + 5
    spukboden(w, _r(R + 4))
    for x, z in scheibe(R * 0.55):
        w.setze(x, 0, z, w.b("coarse_dirt") if (x + z) % 3 else w.b("soul_soil"))
    inhalt = ["lime", "purple", "green"][seed % 3]
    hexenkessel(w, 0, 0, 1, gross=True, inhalt=inhalt, R=1.5 + 1.3 * u)
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)
        ax = "x" if abs(math.sin(a)) > 0.7 else "z"
        for d in (-1, 0, 1):
            w.setze(x + (d if ax == "x" else 0), 1, z + (d if ax == "z" else 0),
                    w.b("stripped_dark_oak_log", axis=ax))
    for i in range(3):
        a = i / 3 * 2 * math.pi + 0.5
        x, z = round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8)
        enden = knorrbaum(w, x, z, 4 * u + 3, "dark_oak")
        for (ex, ey, ez) in enden[:3]:
            w.setze(ex, ey - 1, ez, w.b("lantern", hanging=True, waterlogged=False))
    for x, z in kreisrand(R * 0.3 + 2):
        r = w.rng.random()
        if r < 0.25:
            w.setze(x, 1, z, kerze(w, ["purple", "black", "green", None][int(w.rng.integers(4))]))
        elif r < 0.33:
            w.setze(x, 1, z, w.b("bone_block", axis="y"))
    return w


def hexenbaumhaus(seed, g=2):
    """Hexen-Baumhaus: uralter knorriger Baum, dessen Krone eine Hütte mit Spitzhut trägt, Plattformen,
    Strickleiter, Hängelaternen und Hängewurzeln."""
    w = _welt(seed)
    u = U[g]
    H = 8 * u + 5
    spukboden(w, _r(H * 0.8 + 4))
    knorrbaum(w, 0, 0, H + 3, "dark_oak", krone="dark_oak")
    y0 = _r(H)
    R = 1.8 * u + 2
    for x, z in scheibe(R + 2):
        w.setze(x + 1, y0 - 1, z, w.b("dark_oak_planks") if (x + z) % 3 else w.b("spruce_planks"))
    for x, z in kreisrand(R + 2):
        w.setze(x + 1, y0, z, _pf(w, "dark_oak_fence"))
    hexenhaus(w, seed, 1, 0, y0, R, _r(1.5 * u + 3, 3))
    for y in range(1, y0 - 1):
        w.setze(1, y, round(R) + 3, w.b("ladder", facing="south", waterlogged=False))
    for (x, z) in ((-round(R) - 1, -2), (round(R) + 3, 2)):
        for k in range(1, 3):
            w.setze(x, y0 - 1 - k, z, w.b("hanging_roots"))
        w.setze(x, y0 - 2, z, w.b("lantern", hanging=True, waterlogged=False))
    hohl(w, 2)
    return w


def hexengarten(seed, g=1):
    """Hexengarten: Hochbeete voller Giftpilze, Nachtschatten (Beeren), Wither-Rosen und Farnen, Trockengestell
    mit Kräuterbüscheln, Kürbisranken, Glaskolben auf Pfählen und ein Weidenzaun."""
    w = _welt(seed)
    u = U[g]
    a = _r(6 * u + 4)
    spukboden(w, a + 4)
    rng = w.rng
    pflanzen = ["red_mushroom", "brown_mushroom", "fern", "wither_rose", "lily_of_the_valley", "allium", "dead_bush",
                "crimson_fungus", "warped_fungus"]
    for i in range(-a + 1, a, 4):
        for j in range(-a + 1, a, 4):
            if i == 0 and j == 0:
                continue
            for dx in range(3):
                for dz in range(2):
                    x, z = i + dx, j + dz
                    w.setze(x, 1, z, w.b("rooted_dirt") if pflanzen[(i + j) % len(pflanzen)] not in
                            ("crimson_fungus", "warped_fungus") else w.b("crimson_nylium" if (i + j) % 2 else
                                                                         "warped_nylium"))
                    w.setze(x, 2, z, w.b(pflanzen[(i * 3 + j + dx) % len(pflanzen)]) if rng.random() < 0.8 else
                            w.b("sweet_berry_bush", age=3))
            for dx in (-1, 3):
                for dz in range(2):
                    w.setze(i + dx, 1, j + dz, w.b("spruce_log", axis="z"))
    for p in rechteck(-a - 1, -a - 1, a + 1, a + 1):
        w.setze(p[0], 1, p[1], MB.palisade(w, "spruce") if rng.random() < 0.3 else _pf(w, "dark_oak_fence"))
    for y in range(1, 4):
        for x in (-2, 2):
            w.setze(x, y, 0, _pf(w, "spruce_fence"))
    for x in range(-2, 3):
        w.setze(x, 4, 0, w.b("stripped_spruce_log", axis="x"))
        if x not in (-2, 2):
            w.setze(x, 3, 0, w.b("hanging_roots") if x % 2 else w.b("spore_blossom"))
    return w


def hexenkreis(seed, g=1):
    """Magischer Steinkreis: Menhire mit Runenköpfen, Kerzenring, Zauberkreis aus Amethyst und lila Teppich,
    leuchtender Kristall in der Mitte."""
    w = _welt(seed)
    u = U[g]
    R = 6 * u + 4
    spukboden(w, _r(R + 4))
    fels = Mat(w, ["stone", "andesite", "mossy_cobblestone", "tuff", "cobblestone"], kontrast=1.2)
    n = 6 + g * 2
    for i in range(n):
        a = i / n * 2 * math.pi
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        hh = 3 + int(1.5 * u) + (i % 2)
        for y in range(1, hh + 1):
            for dx in ((0,) if u < 1.5 else (0, 1)):
                w.setze(x + dx, y, z, fels(x, y, z, y / hh) if y < hh else w.b("chiseled_stone_bricks"))
        w.setze(x, hh + 1, z, kerze(w, "purple", 3))
    for x, z in kreisrand(R - 1.5):
        w.setze(x, 0, z, w.b("amethyst_block"))
    for x, z in kreisrand(R * 0.5):
        w.setze(x, 0, z, w.b("purpur_block") if False else w.b("crying_obsidian"))
    for k in range(6):
        a1 = k / 6 * 2 * math.pi
        a2 = (k + 2) / 6 * 2 * math.pi
        for t in np.linspace(0, 1, int(R * 2)):
            x = round(math.cos(a1) * (R - 1.5) * (1 - t) + math.cos(a2) * (R - 1.5) * t)
            z = round(math.sin(a1) * (R - 1.5) * (1 - t) + math.sin(a2) * (R - 1.5) * t)
            w.setze(x, 1, z, w.b("purple_carpet"))
    w.setze(0, 1, 0, w.b("amethyst_block"))
    w.setze(0, 2, 0, w.b("amethyst_cluster", facing="up", waterlogged=False))
    return w


def lebkuchenhaus(seed, g=1):
    """Lebkuchenhaus: Wände aus Lebkuchen (Terrakotta), Zuckerguss-Kanten (weißer Beton), Bonbon-Dach,
    Zuckerstangen-Zaun, Lutscherbäume und Kuchen auf der Fensterbank."""
    w = _welt(seed)
    u = U[g]
    a, b = _r(3.5 * u + 2.5, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 8, art="wiese", dichte=0.4)
    H = _r(3 * u + 3, 4)
    teig = Mat(w, ["orange_terracotta", "terracotta", "brown_terracotta", "orange_terracotta"], kontrast=0.6)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            rand = x in (-a, a) or z in (-b, b)
            for y in range(1, H + 1):
                if rand:
                    ecke = x in (-a, a) and z in (-b, b)
                    fen = (y in (2, 3) and ((x % 3 == 0 and z in (-b, b)) or (z % 3 == 0 and x in (-a, a)))
                           and not ecke)
                    w.setze(x, y, z, w.b("white_concrete") if ecke or y == H else
                            w.b(["pink_stained_glass", "lime_stained_glass", "yellow_stained_glass"][(x + z) % 3])
                            if fen else teig(x, y, z, y / H))
            w.setze(x, 0, z, w.b("pink_terracotta") if (x + z) % 2 else w.b("white_terracotta"))
    for y in (1, 2):
        w.bloecke.pop((0, y, b), None)
    w.setze(0, 1, b, w.b("crimson_door", facing="south", half="lower", hinge="left", open=False, powered=False))
    w.setze(0, 2, b, w.b("crimson_door", facing="south", half="upper", hinge="left", open=False, powered=False))
    farben = ["pink", "red", "white", "lime", "light_blue", "yellow"]
    for k in range(b + 2):
        for x in range(-a - 1, a + 2):
            for z in (-b - 1 + k, b + 1 - k):
                f = farben[(x + k) % len(farben)]
                p = (x, H + 1 + k, z)
                if z == 0 and -b - 1 + k == b + 1 - k:
                    w.setze(*p, w.b("white_concrete"))
                else:
                    w.setze(*p, w.b(f"{f}_concrete") if k % 2 == 0 else w.b(f"{f}_terracotta" if f != "light_blue"
                                                                            else "light_blue_terracotta"))
        for x in (-a - 1, a + 1):
            for z in range(-b - 1 + k + 1, b + 1 - k):
                w.setze(x, H + 1 + k, z, w.b("white_concrete"))
    for x in range(-a - 3, a + 4):
        for z in (-b - 3, b + 3):
            if x % 2 == 0 and not (abs(x) < 2 and z > 0):
                for y in (1, 2):
                    w.setze(x, y, z, w.b("red_concrete") if (x // 2 + y) % 2 else w.b("white_concrete"))
    for i, (x, z) in enumerate(((-a - 5, b + 1), (a + 5, b + 2), (a + 4, -b - 2))):
        for y in range(1, 4):
            w.setze(x, y, z, _pf(w, "birch_fence"))
        for dx, dz in scheibe(1.5):
            for y in (4, 5):
                if math.hypot(dx, y - 4.5) < 1.6:
                    w.setze(x + dx, y, z, w.b(f"{farben[i]}_concrete") if (dx + y) % 2 else w.b("white_concrete"))
    w.setze(a - 1, 3, b + 1, w.b("cake", bites=0))
    hohl(w, 2)
    return w


def stelzenhuette(seed, g=1):
    """Sumpfhexen-Hütte auf Stelzen: Mangroven-Pfähle im Moorwasser, Veranda mit Kessel, Schilfdach aus Stroh,
    Glühbeeren, hängende Laternen und ein schmaler Steg zum Ufer."""
    w = _welt(seed)
    u = U[g]
    a, b = _r(3 * u + 2, 3), _r(2.5 * u + 2, 3)
    R = a + 9
    spukboden(w, R, nass=True)
    for x, z in scheibe(a + 4):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("mud"))
    y0 = 4
    for x in range(-a, a + 1, max(2, a)):
        for z in range(-b, b + 1, max(2, b)):
            for y in range(-1, y0):
                w.setze(x, y, z, w.b("mangrove_log", axis="y"))
            w.setze(x, 0, z + 1, w.b("mangrove_roots", waterlogged=True)) if False else None
    st = P.Stil(w, wand=Mat(w, ["mangrove_planks", "mud_bricks", "mangrove_planks", "stripped_mangrove_log"]),
                sockel=["mangrove_planks"], gesims="mud_brick", dach="mcw_stroh" if _stil(seed) else "schindel_grau",
                holz="mangrove", laeden=False, blumen=0, licht="lantern")
    P.gebaeude(w, st, -a, -b, a, b, y0=y0, etagen=1, eh=4, dach="sattel", tuer="south", sockel_h=0, gauben=False,
               kamine=1, steil=True)
    for x in range(-a, a + 1):
        for z in range(b + 1, b + 4):
            w.setze(x, y0 - 1, z, w.b("mangrove_planks") if (x + z) % 3 else w.b("mangrove_slab", type="top",
                                                                                  waterlogged=False))
    hexenkessel(w, a - 1, b + 2, y0)
    for z in range(b + 4, R - 1):
        w.setze(0, y0 - 1 - min(y0 - 1, (z - b - 4) // 2), z, w.b("mangrove_slab", type="bottom", waterlogged=False))
    for x in (-a, a):
        w.setze(x, y0 + 3, b + 3, w.b("lantern", hanging=True, waterlogged=False))
    hohl(w, 2)
    return w


def pilzhaus(seed, g=1):
    """Riesenpilz-Haus: dicker Stiel mit Tür und Fenstern, gewaltiger gepunkteter Hut (rot oder braun),
    Wendeltreppe außen, kleinere Pilze und Glühpilze rundherum."""
    w = _welt(seed)
    u = U[g]
    R = 2.5 * u + 2
    H = _r(9 * u + 4)
    gelaende(w, _r(R * 3 + 6), art="wald", dichte=0.5)
    for y in range(1, H + 1):
        rr = R * (1.1 - 0.15 * y / H)
        for x, z in kreisrand(rr):
            fen = y % 4 == 2 and (abs(x) < 0.6 or abs(z) < 0.6)
            w.setze(x, y, z, w.b("glass_pane", north=True, south=True, east=True, west=True, waterlogged=False)
                    if fen else w.b("mushroom_stem", up=True, down=True, north=True, south=True, east=True,
                                    west=True))
    for y in (1, 2):
        w.bloecke.pop((0, y, round(R)), None)
    w.setze(0, 1, round(R), w.b("spruce_door", facing="south", half="lower", hinge="left", open=False, powered=False))
    w.setze(0, 2, round(R), w.b("spruce_door", facing="south", half="upper", hinge="left", open=False, powered=False))
    rot = _stil(seed) == 1
    Rh = R * 2.6 + 1
    for k in range(_r(Rh * 0.7) + 1):
        rr = Rh * math.cos(min(1, k / (Rh * 0.7)) * math.pi / 2) ** 0.7
        for x, z in scheibe(rr):
            if math.hypot(x, z) > rr - 1.2 or k == _r(Rh * 0.7):
                punkt = rot and w.rng.random() < 0.12
                w.setze(x, H + 1 + k, z, w.b("white_concrete") if punkt else
                        w.b("red_mushroom_block" if rot else "brown_mushroom_block", up=True, down=False, north=True,
                            south=True, east=True, west=True))
    for x, z in kreisrand(Rh - 0.5):
        if w.rng.random() < 0.4:
            w.setze(x, H, z, w.b("shroomlight"))
    for i in range(5 + g):
        a = w.rng.random() * 2 * math.pi
        d = Rh + 2 + w.rng.random() * 4
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        hh = 2 + int(w.rng.integers(0, 2 + g))
        for y in range(1, hh + 1):
            w.setze(x, y, z, w.b("mushroom_stem", up=True, down=True, north=True, south=True, east=True, west=True))
        for xx, zz in scheibe(1.5, x, z):
            w.setze(xx, hh + 1, zz, w.b("red_mushroom_block" if (i % 2) else "brown_mushroom_block", up=True,
                                        down=False, north=True, south=True, east=True, west=True))
    hohl(w, 2)
    return w


def hexenmarkt(seed, g=1):
    """Hexenmarkt: dunkle Stände mit lila und schwarzen Markisen, Tränke (Braustände), Schädel, Kerzen,
    Glasflaschen, Kräuter, getrocknete Fledermäuse und eine Laternengasse."""
    w = _welt(seed)
    u = U[g]
    n = 2 + g
    L = n * 5 + 2
    spukboden(w, L + 7 + g, dichte=0.4)
    for x in range(-L, L + 1):
        for z in (-1, 0, 1):
            w.setze(x, 0, z, MB.pflaster(w, "cobblestone", "running_bond") if (x + z) % 3 else w.b("mossy_cobblestone"))
    farben = ["purple", "black", "magenta", "green", "gray"]
    waren = [lambda: w.b("brewing_stand", has_bottle_0=True, has_bottle_1=True, has_bottle_2=False),
             lambda: schaedel(w), lambda: kerze(w, "purple"), lambda: w.b("lime_stained_glass"),
             lambda: w.b("flower_pot") if False else w.b("decorated_pot", facing="north", cracked=False,
                                                          waterlogged=False),
             lambda: w.b("bone_block", axis="y"), lambda: w.b("amethyst_cluster", facing="up", waterlogged=False)]
    for i in range(n):
        for sz in (-1, 1):
            x0 = -L + 2 + i * 5 + (2 if sz > 0 else 0)
            z = sz * 3
            f = farben[(i + (sz > 0)) % len(farben)]
            for x in range(x0, x0 + 4):
                w.setze(x, 1, z, w.b("dark_oak_planks"))
                w.setze(x, 2, z, waren[(x + i) % len(waren)]())
                for zz in (z - 1, z, z + 1):
                    w.setze(x, 4, zz, MB.markise(w, f, "north" if sz > 0 else "south") if zz != z + sz else
                            w.b(f"{f}_wool"))
            for x in (x0, x0 + 3):
                w.setze(x, 3, z + sz, _pf(w, "dark_oak_fence"))
                w.setze(x, 2, z + sz, _pf(w, "dark_oak_fence"))
                w.setze(x, 1, z + sz, _pf(w, "dark_oak_fence"))
    for x in range(-L, L + 1, 4):
        w.setze(x, 1, 2, _pf(w, "dark_oak_fence"))
        w.setze(x, 2, 2, _pf(w, "dark_oak_fence"))
        w.setze(x, 3, 2, w.b("soul_lantern", hanging=False, waterlogged=False) if x % 8 else
                MB.laterne(w, "chain_lantern"))
    hexenhaus(w, seed, L + 3 + g, 0, 1, 2.2 + 0.6 * g, 3 + g, tuer="west")
    hexenkessel(w, -L - 2, 0, 1, gross=g >= 2, R=2.3)
    return w


def zaubererturm(seed, g=2):
    """Zaubererturm: schlanker blauer Turm mit außen umlaufender Wendeltreppe, Sternenhut-Dach, schwebender
    Amethystring und Fernrohr-Balkon."""
    w = _welt(seed)
    u = U[g]
    R = 2.0 * u + 2
    H = _r(18 * u + 8)
    gelaende(w, _r(R + 9), art="wiese", dichte=0.3)
    wand = Mat(w, ["light_blue_terracotta", "cyan_terracotta", "blue_terracotta", "light_blue_terracotta"]
               if _stil(seed) else ["calcite", "diorite", "polished_diorite", "smooth_quartz"], kontrast=0.8)
    krummer_turm(w, 0, 0, 1, H, R, wand, neigung=0.0, fenster="light_blue_stained_glass")
    D = P.Dach(w, "mcw_blau" if _stil(seed) == 0 else "mcw_lila")
    hexenhut(w, D, 0, 0, H + 1, round(R) + 1, _r(R * 3 + 4), knick=0.5)
    for k in range(H * 3):
        a = k / 12 * 2 * math.pi
        y = 1 + k // 3
        if y >= H:
            break
        x, z = round(math.cos(a) * (R + 1.2)), round(math.sin(a) * (R + 1.2))
        w.setze(x, y, z, w.b("quartz_slab" if _stil(seed) == 0 else "smooth_stone_slab", type="top",
                             waterlogged=False))
    ry = H + _r(R * 3 + 4) // 2 + 1
    for x, z in kreisrand(R + 3.5):
        if (x + z) % 2 == 0:
            w.setze(x, ry, z, w.b("amethyst_block"))
    for x, z in kreisrand(R + 2):
        w.setze(x, H - 4, z, w.b("dark_oak_planks"))
        w.setze(x, H - 3, z, _pf(w, "dark_oak_fence"))
    w.setze(round(R) + 2, H - 2, 0, w.b("spyglass") if False else w.b("lightning_rod", facing="east", powered=False,
                                                                         waterlogged=False))
    hohl(w, 2)
    return w


def kristallaltar(seed, g=1):
    """Kristallaltar: aufgebrochene Amethyst-Geode mit Kalzit- und Basaltschale, Kristallspitzen, darin ein
    Altar mit Zauberbuchständer und Kerzen."""
    w = _welt(seed)
    u = U[g]
    R = 4 * u + 3
    spukboden(w, _r(R + 5))
    S = Skulptur(w, 1.0)
    S.mat("b", bl(w, "smooth_basalt"))
    S.mat("c", bl(w, "calcite"))
    S.mat("a", lambda x, y, z, *_: w.b("budding_amethyst") if (x * 7 + y * 3 + z) % 5 == 0 else w.b("amethyst_block"))

    def kugel(rr):
        return lambda X, Y, Z: X * X + (Y * 1.1) ** 2 + Z * Z < rr * rr

    offen = lambda X, Y, Z: (Z > R * 0.2) | (Y > R * 0.55)
    S.plus(lambda X, Y, Z: kugel(R)(X, Y, Z) & ~offen(X, Y, Z), "b")
    S.plus(lambda X, Y, Z: kugel(R - 1)(X, Y, Z) & ~offen(X, Y, Z), "c")
    S.plus(lambda X, Y, Z: kugel(R - 2)(X, Y, Z) & ~offen(X, Y, Z), "a")
    S.minus(lambda X, Y, Z: kugel(R - 3)(X, Y, Z))
    S.rendern((-R - 1, -R - 1, -R - 1), (R + 1, R + 1, R + 1), versatz=(0.5, 1.5, 0.5))
    for (x, y, z), b in list(w.bloecke.items()):
        if "amethyst" in w.P.name(b) and w.rng.random() < 0.25:
            for (dx, dy, dz, f) in ((0, 1, 0, "up"), (0, 0, 1, "south"), (1, 0, 0, "east"), (-1, 0, 0, "west")):
                if w.frei(x + dx, y + dy, z + dz):
                    w.setze(x + dx, y + dy, z + dz, w.b("amethyst_cluster", facing=f, waterlogged=False))
                    break
    for y in range(-int(R) + 2, 1):
        for x, z in scheibe(R - 3.2):
            w.bloecke.pop((x, y + 1, z), None) if y > -int(R) + 2 else None
    for x, z in scheibe(1.5):
        w.setze(x, 0, z, w.b("polished_blackstone_bricks"))
    w.setze(0, 1, 0, w.b("lectern", facing="south", has_book=True, powered=False))
    for x, z in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
        w.setze(x, 1, z, kerze(w, "purple", 4))
    return w


def froschteich(seed, g=1):
    """Froschkönig-Teich: Moorteich mit Seerosen, Froschlichtern, Schilf, einer großen Froschstatue auf einem Stein
    und einem kleinen Hexensteg."""
    w = _welt(seed)
    u = U[g]
    R = _r(8 * u + 5)
    spukboden(w, R + 4)
    for x, z in scheibe(R * 0.8):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("mud"))
        r = w.rng.random()
        if r < 0.12:
            w.setze(x, 1, z, w.b("lily_pad"))
        elif r < 0.15:
            w.setze(x, 0, z, w.b(["ochre_froglight", "verdant_froglight", "pearlescent_froglight"][int(w.rng.integers(3))],
                                 axis="y"))
    for x, z in kreisrand(R * 0.8 + 0.5):
        if w.rng.random() < 0.4:
            w.setze(x, 1, z, w.b("sugar_cane", age=0))
            w.setze(x, 2, z, w.b("sugar_cane", age=0))
            w.setze(x, 0, z, w.b("grass_block", snowy=False))
    s = 0.5 + 0.2 * g
    for x, z in scheibe(3 * s + 2):
        for y in (0, 1):
            w.setze(x, y, z, w.b("mossy_cobblestone"))
    S = Skulptur(w, s)
    gruen = Mat(w, ["green_terracotta", "lime_terracotta", "moss_block", "green_concrete"], kontrast=0.7)
    S.mat("k", sk(gruen, 2, 12))
    S.mat("b", bl(w, "lime_terracotta"))
    S.mat("a", bl(w, "gold_block"))
    S.mat("d", bl(w, "black_concrete"))
    S.plus(ell(0, 4, 0, 5, 4, 4.5), "k")
    S.plus(ell(0, 3.5, 2, 3.8, 2.8, 3.0), "b")
    S.plus(ell(0, 8, 2.5, 4, 2.6, 3.0), "k")
    for sx in (-1, 1):
        S.plus(ell(sx * 2.2, 10, 3.5, 1.3, 1.3, 1.3), "k")
        S.plus(ell(sx * 2.4, 10.2, 4.6, 0.6, 0.6, 0.4), "d")
        S.plus(kap((sx * 4, 2, 1), (sx * 6.5, 0.5, 4), 1.4, 1.0), "k")
    S.plus(lambda X, Y, Z: (np.abs(Y - 11.8) < 0.7) & (X * X + (Z - 2.5) ** 2 < 6) & (X * X + (Z - 2.5) ** 2 > 2.5),
           "a")
    S.rendern((-8, 0, -6), (8, 14, 8), versatz=(0.5, 2.01, 0.5))
    for z in range(round(R * 0.8) - 3, R + 2):
        w.setze(-round(R * 0.5), 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    return w


def totenkopffelsen(seed, g=2):
    """Totenkopffelsen: riesiger Schädel aus Stein, aus dessen Augen Seelenfeuer leuchten, das Maul ist der
    Höhleneingang mit Fackeln; Knochen und tote Bäume ringsum."""
    w = _welt(seed)
    u = U[g]
    s = 0.6 * u + 0.3
    spukboden(w, _r(10 * s + 6))
    fels = Mat(w, ["stone", "andesite", "diorite", "calcite", "tuff", "cobblestone"], kontrast=1.0)
    S = Skulptur(w, s)
    S.mat("f", sk(fels, 0, 20 * s))
    S.mat("g", bl(w, "soul_lantern" if False else "sea_lantern" if _stil(seed) else "shroomlight"))
    S.mat("d", bl(w, "black_concrete"))
    S.plus(ell(0, 9, 0, 8, 8, 8), "f")
    S.plus(ell(0, 3, 2.5, 5.5, 3.5, 5.5), "f")
    for sx in (-1, 1):
        S.minus(ell(sx * 3.2, 9, 6.5, 2.2, 2.2, 3.0))
        S.plus(ell(sx * 3.2, 9, 5.0, 1.0, 1.0, 1.0), "g")
    S.minus(lambda X, Y, Z: (np.abs(X) < 0.9 + (7 - Y) * 0.2) & (Y > 5.0) & (Y < 7.0) & (Z > 5))
    S.minus(lambda X, Y, Z: (np.abs(X) < 3.6) & (Y > 0) & (Y < 3.6) & (Z > 2))
    for k in range(-3, 4):
        S.plus(lambda X, Y, Z, k=k: (np.abs(X - k * 1.1) < 0.4) & (Y > 2.6) & (Y < 3.8) & (Z > 6.5) & (Z < 7.6), "f")
    S.rendern((-9, 0, -9), (9, 18, 9), versatz=(0.5, 0.01, 0.5))
    for sx in (-1, 1):
        w.setze(sx * round(4 * s), 1, round(8 * s), w.b("soul_campfire", lit=True, signal_fire=False,
                                                         facing="north", waterlogged=False))
    for i in range(8):
        a = w.rng.random() * 2 * math.pi
        d = 10 * s + 1 + w.rng.random() * 3
        w.setze(round(math.cos(a) * d), 1, round(math.sin(a) * d), w.b("bone_block", axis=["x", "y", "z"][i % 3]))
    knorrbaum(w, -round(10 * s), -round(6 * s), 5 * u + 3, "dark_oak")
    hohl(w, 2)
    return w


def huehnerbeinhaus(seed, g=2):
    """Hütte auf Hühnerbeinen: eine Hexenhütte auf zwei gewaltigen, schuppigen Vogelbeinen mit Krallen,
    die gerade einen Schritt macht – Leiter und Kerzen inklusive."""
    w = _welt(seed)
    u = U[g]
    s = 0.5 * u + 0.25
    spukboden(w, _r(12 * s + 6))
    S = Skulptur(w, s)
    haut = Mat(w, ["yellow_terracotta", "orange_terracotta", "terracotta", "yellow_terracotta"], kontrast=0.6)
    S.mat("k", sk(haut, 0, 20 * s))
    S.mat("h", bl(w, "bone_block"))
    S.mat("f", bl(w, "brown_wool"))
    for sx, vor in ((-1, 1.0), (1, -0.8)):
        hx = sx * 3.0
        knie = (hx, 9, -3 + vor * 2)
        fuss = (hx, 1.0, 1 + vor * 3)
        S.plus(kap((hx, 17, 0), knie, 2.2, 1.4), "f")
        S.plus(kap(knie, fuss, 1.0, 0.8), "k")
        for d in (-1, 0, 1):
            S.plus(kap(fuss, (hx + d * 2.5, 0.4, fuss[2] + 3.5 - abs(d)), 0.6, 0.3), "k")
            S.plus(ell(hx + d * 2.7, 0.4, fuss[2] + 3.9 - abs(d), 0.45, 0.45, 0.6), "h")
        S.plus(kap(fuss, (hx, 0.4, fuss[2] - 2.5), 0.6, 0.3), "k")
    S.rendern((-8, 0, -8), (8, 19, 10), versatz=(0.5, 1.01, 0.5))
    y0 = round(19 * s) + 1
    R = max(2.2, 3.2 * s + 1)
    for x, z in scheibe(R + 1):
        w.setze(x, y0 - 1, z, w.b("spruce_planks"))
    hexenhaus(w, seed, 0, 0, y0, R, _r(4 * s + 3, 3))
    for y in range(2, y0 - 1):
        w.setze(0, y, round(R) + 2, w.b("ladder", facing="south", waterlogged=False)) if y > y0 // 2 else None
    hohl(w, 2)
    return w


def spinnenwald(seed, g=2):
    """Spinnenhain: tote Bäume, dicht mit Spinnweben verhangen, eine riesige Spinnenstatue mit roten Augen,
    weiße Eierkokons und umgefallene Stämme."""
    w = _welt(seed)
    u = U[g]
    R = _r(10 * u + 6)
    spukboden(w, R + 2, dichte=0.6)
    rng = w.rng
    for i in range(4 + 2 * g):
        a = rng.random() * 2 * math.pi
        d = R * (0.4 + 0.5 * rng.random())
        enden = knorrbaum(w, round(math.cos(a) * d), round(math.sin(a) * d), 4 * u + 3 + rng.random() * 3,
                          "dark_oak" if i % 2 else "spruce")
        for (ex, ey, ez) in enden:
            for k in range(1, 3):
                if rng.random() < 0.6:
                    w.setze(ex + int(rng.integers(-1, 2)), ey - k, ez + int(rng.integers(-1, 2)), w.b("cobweb"))
    s = 0.6 + 0.25 * g
    S = Skulptur(w, s)
    S.mat("k", bl(w, "black_concrete"))
    S.mat("b", bl(w, "gray_concrete"))
    S.mat("a", bl(w, "redstone_block"))
    S.plus(ell(0, 4, -4, 4.5, 3.5, 5.5), "k")
    S.plus(ell(0, 4, -4, 3.0, 2.2, 4.0), "b")
    S.plus(ell(0, 3.5, 3, 2.8, 2.2, 2.8), "k")
    for sx in (-1, 1):
        S.plus(ell(sx * 0.9, 4.2, 5.4, 0.5, 0.5, 0.4), "a")
        S.plus(ell(sx * 1.8, 4.6, 5.0, 0.4, 0.4, 0.3), "a")
        for k, zz in enumerate((-1, 1, 3, 5)):
            knie = (sx * 6, 7.5 - k * 0.3, zz)
            S.plus(kap((sx * 2, 3.5, zz * 0.5 + 1), knie, 0.7, 0.55), "k")
            S.plus(kap(knie, (sx * 10, 0.3, zz * 1.4), 0.55, 0.3), "k")
    S.rendern((-12, 0, -11), (12, 9, 10), versatz=(0.5, 1.01, 0.5))
    for i in range(6):
        x, z = int(rng.integers(-R // 2, R // 2)), int(rng.integers(-R // 2, R // 2))
        if w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("white_wool"))
            w.setze(x, 2, z, w.b("cobweb"))
    return w


def kerzenschrein(seed, g=1):
    """Kerzenschrein: kleine offene Kapelle aus dunklem Holz und Stein, auf Stufen hunderte Kerzen in allen
    Höhen, ein Hexenbild (Buntglas) und Weihrauchschalen."""
    w = _welt(seed)
    u = U[g]
    a = _r(3 * u + 2, 3)
    spukboden(w, a + 7)
    st = P.Stil(w, wand="schwarzstein" if _stil(seed) else "tiefenschiefer", sockel="schwarzstein",
                gesims="polished_blackstone_brick", dach=HEXDACH[seed % 3], holz="dark_oak", laeden=False, blumen=0)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            w.setze(x, 0, z, w.b("polished_blackstone_bricks"))
            if x in (-a, a) or z == -a:
                for y in range(1, 5 + g):
                    w.setze(x, y, z, st.wand(x, y, z, y / 6))
    P.satteldach(w, st.dach, -a, -a, a, a + 1, 5 + g, ue=1, first_x=False)
    for k in range(3):
        for x in range(-a + 1, a):
            w.setze(x, 1 + k, -a + 1 + k, w.b("polished_blackstone_brick_stairs", facing="south", half="bottom",
                                              shape="straight", waterlogged=False) if False else
                    w.b("polished_blackstone_bricks"))
            for z in range(-a + 1 + k + 1, -a + 1 + k + 2):
                pass
    farben = ["purple", "black", "white", "red", None]
    rng = w.rng
    for x in range(-a + 1, a):
        for k in range(3):
            w.setze(x, 2 + k, -a + 1 + k, kerze(w, farben[int(rng.integers(len(farben)))], int(rng.integers(1, 5))))
    for y in range(2, 5 + g):
        w.setze(0, y, -a, w.b(["purple_stained_glass", "magenta_stained_glass", "black_stained_glass"][y % 3]))
    for sx in (-a - 1, a + 1):
        w.setze(sx, 1, a + 1, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                                  west="none", waterlogged=False))
        w.setze(sx, 2, a + 1, w.b("soul_campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


def trankbrauerei(seed, g=2):
    """Trankbrauerei: Fachwerk-Werkstatt mit Kupferdestillen, Glasröhren (Create-Rohre als Mod-Block),
    Fässern voller Elixiere, Braustandreihen und lila Rauch aus dem Schornstein."""
    w = _welt(seed)
    u = U[g]
    a, b = _r(5 * u + 3, 4), _r(3 * u + 2, 3)
    spukboden(w, a + 8, dichte=0.5)
    st = P.Stil(w, wand="holz_dunkel", sockel="schwarzstein", gesims="deepslate_brick", dach=HEXDACH[seed % 6],
                holz="dark_oak", fenster="purple_stained_glass_pane" if False else "glass_pane", blumen=0)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1 + (g >= 2), eh=4, dach="sattel", tuer="south", kamine=1)
    for k in range(2 + g // 2):
        x = a + 3 + k * 4
        for y in range(1, 4):
            for x2, z2 in kreisrand(1.2, x, 0):
                w.setze(x2, y, z2, w.b("waxed_copper_block") if y < 3 else w.b("waxed_cut_copper"))
        w.setze(x, 4, 0, w.b("waxed_cut_copper_slab", type="bottom", waterlogged=False))
        for y in range(4, 7):
            w.setze(x, y + 1, 0, MB.mod(w, "create:fluid_pipe", "lightning_rod", {"facing": "up", "powered": False,
                                                                                  "waterlogged": False},
                                        up=True, down=True, north=False, south=False, east=False, west=False,
                                        waterlogged=False))
        for xx in range(x - 3, x + 1):
            w.setze(xx, 7, 0, MB.mod(w, "create:fluid_pipe", "chain", {"axis": "x", "waterlogged": False},
                                     east=True, west=True, up=False, down=False, north=False, south=False,
                                     waterlogged=False))
    for z in range(-b, b + 1, 2):
        w.setze(-a - 2, 1, z, w.b("barrel", facing="east", open=False))
        w.setze(-a - 2, 2, z, w.b("brewing_stand", has_bottle_0=True, has_bottle_1=True, has_bottle_2=True))
    hohl(w, 2)
    return w


def rabenturm(seed, g=1):
    """Rabenturm: runder Taubenschlag-Turm aus Bruchstein mit Fluglöchern und Sitzstangen, schwarze Raben,
    spitzes Holzdach und eine Botenhütte."""
    w = _welt(seed)
    u = U[g]
    R = 2.0 * u + 2.0
    H = _r(9 * u + 5)
    spukboden(w, _r(R + 8))
    wand = hexenwand(w, seed + 1)
    for y in range(1, H + 1):
        for x, z in kreisrand(R):
            loch = y > 3 and y % 3 == 0 and (x + z + y) % 3 == 0
            w.setze(x, y, z, w.b("dark_oak_trapdoor", facing="north", half="top", open=False, powered=False,
                                 waterlogged=False) if loch else wand(x, y, z, y / H))
    D = _hexdach(w, seed, 2)
    hexenhut(w, D, 0, 0, H + 1, round(R) + 1, _r(R * 2 + 3), knick=0.5)
    rng = w.rng
    for i in range(8 + 3 * g):
        a = rng.random() * 2 * math.pi
        y = 4 + int(rng.integers(0, max(1, H - 3)))
        x, z = round(math.cos(a) * (R + 1)), round(math.sin(a) * (R + 1))
        w.setze(x, y, z, _pf(w, "dark_oak_fence") if rng.random() < 0.5 else w.b("black_wool"))
        if rng.random() < 0.5:
            w.setze(x, y + 1, z, w.b("black_carpet"))
    hexenhaus(w, seed, round(R) + 5, 0, 1, 2.2, 3, tuer="east")
    return w


def mondaltar(seed, g=2):
    """Mondaltar: Stufenplattform aus Kalzit und Tiefenschiefer, darüber eine riesige leuchtende Mondsichel,
    Sternensplitter (Endstäbe) und ein Ring aus Silberkerzen."""
    w = _welt(seed)
    u = U[g]
    R = 5 * u + 4
    spukboden(w, _r(R + 4), dichte=0.5)
    for k in range(3):
        for x, z in scheibe(R * (1 - k * 0.2)):
            w.setze(x, 1 + k, z, w.b("polished_deepslate") if k % 2 == 0 else w.b("calcite"))
    s = 0.5 * u + 0.25
    S = Skulptur(w, s)
    S.mat("m", lambda x, y, z, *_: w.b("pearlescent_froglight", axis="y") if (x + y) % 5 == 0 else
          w.b("white_concrete") if (x + y + z) % 3 else w.b("calcite"))
    S.plus(lambda X, Y, Z: ((X ** 2 + (Y - 12) ** 2) < 81) & ((X - 3.5) ** 2 + (Y - 13.5) ** 2 > 56) &
           (np.abs(Z) < 1.2), "m")
    S.rendern((-11, 0, -2), (11, 24, 2), versatz=(0.5, 4.01, 0.5))
    rng = w.rng
    for i in range(10 + 4 * g):
        x = int(rng.integers(-R, R + 1))
        y = 6 + int(rng.integers(0, int(20 * s) + 3))
        z = int(rng.integers(-3, 4))
        w.setze(x, y, z, w.b("end_rod", facing="up"))
    for x, z in kreisrand(R * 0.6 - 0.5):
        w.setze(x, 4, z, kerze(w, "light_gray", 2)) if (x + z) % 2 == 0 else None
    for x, z in kreisrand(R * 0.3):
        w.setze(x, 4, z, w.b("chiseled_quartz_block"))
    return w


HEXEN = {
    "hexenhuette": ("Hexenhütte", hexenhuette),
    "alchemieturm": ("Alchemistenturm", alchemieturm),
    "kesselplatz": ("Kesselplatz", kesselplatz),
    "hexenbaumhaus": ("Hexen-Baumhaus", hexenbaumhaus),
    "hexengarten": ("Hexengarten", hexengarten),
    "hexenkreis": ("Hexenkreis", hexenkreis),
    "lebkuchenhaus": ("Lebkuchenhaus", lebkuchenhaus),
    "stelzenhuette": ("Sumpfhütte auf Stelzen", stelzenhuette),
    "pilzhaus": ("Riesenpilz-Haus", pilzhaus),
    "hexenmarkt": ("Hexenmarkt", hexenmarkt),
    "zaubererturm": ("Zaubererturm", zaubererturm),
    "kristallaltar": ("Kristallaltar", kristallaltar),
    "froschteich": ("Froschkönig-Teich", froschteich),
    "totenkopffelsen": ("Totenkopffelsen", totenkopffelsen),
    "huehnerbeinhaus": ("Hütte auf Hühnerbeinen", huehnerbeinhaus),
    "spinnenhain": ("Spinnenhain", spinnenwald),
    "kerzenschrein": ("Kerzenschrein", kerzenschrein),
    "trankbrauerei": ("Trankbrauerei", trankbrauerei),
    "rabenturm": ("Rabenturm", rabenturm),
    "mondaltar": ("Mondaltar", mondaltar),
}

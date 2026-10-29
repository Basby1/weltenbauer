"""Riesenbögen II – zwanzig weitere natürliche und gebaute Riesenbögen: Sandstein, Eis, Moos mit Wasserfall,
Doppelbogen, Basalt, Kristall, Wurzeln, Korallen, Lava, gebrochener Schwebebogen, Tempel, Pfad, gewundener Bogen,
Bogenkette, Felsenfenster, Kirschblüten, Nether, End, Walknochen und Regenbogen."""

from __future__ import annotations

import math

import numpy as np

import wald2
from feinbau import Mix, laterne, platte, stamm, zaun
from flora import _neu, _r
from inseln2 import haeuschen, wasserflaeche
from lib import Rauschen, einfuegen

SP = [22, 34, 50, 72]


# ============================================================================ Werkzeuge

def pfad(S, H, n=None, form=1.0, spitz=False, x0=0.0, z0=0.0, achse="x", fuss=-3, schwung=0.0):
    n = n or int(S * 4)
    pts = []
    for i in range(n + 1):
        t = i / n
        u = -S / 2 + S * t
        if spitz:
            h = H * (1 - abs(2 * t - 1) ** 1.25)
        else:
            h = H * math.sin(math.pi * t) ** form
        y = h + fuss * (1 - math.sin(math.pi * t))
        q = schwung * math.sin(math.pi * t * 2)
        pts.append((x0 + u, y, z0 + q, t) if achse == "x" else (x0 + q, y, z0 + u, t))
    return pts


def radius(r0, r1, k=3):
    return lambda t: r0 + (r1 - r0) * abs(2 * t - 1) ** k


def koerper(w, pts, rfn, rz=1.4, rauh=0.35, zelle=5.0, quer="z"):
    """Füllt Ellipsoide entlang des Pfads (numpy). Gibt (lo, occ, tg) zurück."""
    rs = Rauschen(w, zelle)
    P = np.array([p[:3] for p in pts])
    rmax = max(rfn(p[3]) for p in pts) * (1 + rauh) * max(1, rz) + 2
    lo = np.floor(P.min(0) - rmax).astype(int)
    hi = np.ceil(P.max(0) + rmax).astype(int)
    occ = np.zeros(hi - lo + 1, bool)
    tg = np.zeros(hi - lo + 1, np.float32)
    for (x, y, z, t) in pts:
        r = max(0.6, rfn(t) * (1 - rauh / 2 + rauh * rs(x, y, z)))
        rx, ry, rzz = (r, r, r * rz) if quer == "z" else (r * rz, r, r)
        a = [int(math.floor(c - rr)) for c, rr in ((x, rx), (y, ry), (z, rzz))]
        b = [int(math.ceil(c + rr)) + 1 for c, rr in ((x, rx), (y, ry), (z, rzz))]
        X, Y, Z = (np.arange(a[i], b[i]) for i in range(3))
        m = (((X[:, None, None] - x) / rx) ** 2 + ((Y[None, :, None] - y) / ry) ** 2 +
             ((Z[None, None, :] - z) / rzz) ** 2) <= 1
        sl = tuple(slice(a[i] - lo[i], b[i] - lo[i]) for i in range(3))
        occ[sl] |= m
        tg[sl][m] = t
    return lo, occ, tg


def setzen(w, lo, occ, tg, mat, oben=None, oben2=None, ab_y=-6, ueber=True):
    """Setzt den Körper; gibt (oben_liste, unten_liste) zurück."""
    ob = np.zeros_like(occ)
    ob[:, :-1, :] = occ[:, 1:, :]
    ob2 = np.zeros_like(occ)
    ob2[:, :-2, :] = occ[:, 2:, :]
    un = np.zeros_like(occ)
    un[:, 1:, :] = occ[:, :-1, :]
    top, unter = [], []
    for i, j, k in np.argwhere(occ):
        x, y, z = int(i + lo[0]), int(j + lo[1]), int(k + lo[2])
        if y < ab_y:
            continue
        t = float(tg[i, j, k])
        if oben is not None and not ob[i, j, k]:
            blk = oben(x, y, z, t)
        elif oben2 is not None and not ob2[i, j, k]:
            blk = oben2(x, y, z, t)
        else:
            blk = mat(x, y, z, t)
        if blk is None:
            continue
        w.setze(x, y, z, blk, ueber)
        if not ob[i, j, k]:
            top.append((x, y, z, t))
        if not un[i, j, k] and y > 1:
            unter.append((x, y, z, t))
    return top, unter


def schichten(w, namen, dicke=2.0, wellig=3.0):
    rs = Rauschen(w, 9)
    ids = [w.b(n) for n in namen]
    return lambda x, y, z, *_: ids[int((y + wellig * rs(x, 0, z)) / dicke) % len(ids)]


def mix(w, liste, zelle=1.8, **pr):
    M = Mix(w, liste, zelle=zelle, **pr)
    return lambda x, y, z, *_: M(x, y, z)


def gras(w):
    return lambda *_: w.b("grass_block", snowy=False)


def erde(w):
    return lambda *_: w.b("dirt")


def sockel(w, R, oben, tiefe=3, frei=None, rx=1.0, rz=1.0, unter=("dirt", "stone", "andesite", "gravel")):
    """Unregelmäßige Bodenplatte bei y = 0. frei(x, z) -> True: Wasser statt Boden. Gibt Zellen zurück."""
    rn = Rauschen(w, 4)
    zellen = set()
    for x in range(-int(R * rx) - 2, int(R * rx) + 3):
        for z in range(-int(R * rz) - 2, int(R * rz) + 3):
            d = math.hypot(x / rx, z / rz) / R
            if d > 0.82 + 0.36 * rn(x, 0, z):
                continue
            if frei and frei(x, z):
                w.setze(x, 0, z, w.b("water", level=0), False)
                w.setze(x, -1, z, w.b("water", level=0), False)
                w.setze(x, -2, z, w.b(["sand", "gravel", "clay"][int(rn(x, 3, z) * 2.99)]), False)
                continue
            zellen.add((x, z))
            t = int(tiefe * (0.6 + 0.6 * rn(x, 5, z)))
            for y in range(-t, 1):
                b = oben(x, y, z) if y == 0 else w.b(unter[min(len(unter) - 1, int(-y / 1.5))])
                w.setze(x, y, z, b, False)
    return zellen


def bodenbewuchs(w, zellen, dichte=0.35, blumen=("poppy", "dandelion", "oxeye_daisy", "azure_bluet", "cornflower"),
                 y=0):
    rng = w.rng
    for (x, z) in zellen:
        n = w.P.name(w.bloecke.get((x, y, z), 0))
        if n not in ("minecraft:grass_block", "minecraft:moss_block") or not w.frei(x, y + 1, z):
            continue
        r = rng.random()
        if r < dichte * 0.5:
            w.setze(x, y + 1, z, w.b("grass"))
        elif r < dichte * 0.62:
            w.setze(x, y + 1, z, w.b("fern"))
        elif blumen and r < dichte * 0.78:
            w.setze(x, y + 1, z, w.b(blumen[int(rng.random() * len(blumen))]))


def oben_bewuchs(w, top, dichte=0.4, blumen=("poppy", "dandelion", "azure_bluet", "oxeye_daisy")):
    bodenbewuchs(w, [(x, z) for (x, y, z, t) in top], 0, blumen) if False else None
    rng = w.rng
    for (x, y, z, t) in top:
        if w.P.name(w.bloecke.get((x, y, z), 0)) not in ("minecraft:grass_block", "minecraft:moss_block"):
            continue
        if not w.frei(x, y + 1, z):
            continue
        r = rng.random()
        if r < dichte * 0.55:
            w.setze(x, y + 1, z, w.b("grass"))
        elif r < dichte * 0.7:
            w.setze(x, y + 1, z, w.b("fern"))
        elif blumen and r < dichte * 0.85:
            w.setze(x, y + 1, z, w.b(blumen[int(rng.random() * len(blumen))]))


def baeume_oben(w, top, n, macher, abstand=6, t_bereich=(0.2, 0.8)):
    rng = w.rng
    kand = [p for p in top if t_bereich[0] <= p[3] <= t_bereich[1]]
    rng.shuffle(kand)
    gesetzt = []
    for (x, y, z, t) in kand:
        if len(gesetzt) >= n:
            break
        if any(math.hypot(x - a, z - b) < abstand for a, b in gesetzt):
            continue
        if not all(w.frei(x, y + h, z) for h in (1, 3, 5)):
            continue
        if w.P.name(w.bloecke.get((x, y, z), 0)) not in ("minecraft:grass_block", "minecraft:moss_block",
                                                          "minecraft:snow_block", "minecraft:sand",
                                                          "minecraft:podzol", "minecraft:crimson_nylium",
                                                          "minecraft:end_stone", "minecraft:dirt"):
            continue
        einfuegen(w, macher(int(rng.integers(1, 10 ** 6))), x, y, z)
        gesetzt.append((x, z))


def ranken(w, unter, anteil=0.25, art="cave", lmax=6):
    rng = w.rng
    for (x, y, z, t) in unter:
        if rng.random() > anteil or not w.frei(x, y - 1, z):
            continue
        L = 1 + int(rng.random() * lmax)
        for k in range(1, L + 1):
            if not w.frei(x, y - k, z) or y - k <= 1:
                break
            ende = k == L or not w.frei(x, y - k - 1, z)
            if art == "cave":
                b = (w.b("cave_vines", age=25, berries=rng.random() < 0.35) if ende else
                     w.b("cave_vines_plant", berries=rng.random() < 0.3))
            elif art == "weeping":
                b = w.b("weeping_vines", age=25) if ende else w.b("weeping_vines_plant")
            elif art == "wurzel":
                b = w.b("hanging_roots", waterlogged=False)
                L = 1
            elif art == "eis":
                b = w.b("ice") if k < L else w.b("pointed_dripstone", vertical_direction="down", thickness="tip",
                                                  waterlogged=False)
            elif art == "tropf":
                dick = ["tip", "frustum", "middle", "base"]
                b = w.b("pointed_dripstone", vertical_direction="down",
                        thickness=dick[max(0, min(3, L - k))] if k < L else "tip", waterlogged=False)
            else:
                b = w.b(art)
            w.setze(x, y - k, z, b, False)
            if art == "wurzel":
                break


def wasserfall(w, x, y, z, unten=1, breite=1, mat="water"):
    for yy in range(unten, y + 1):
        for dx in range(breite):
            w.setze(x + dx, yy, z, w.b(mat, level=0))


def _scheitel(top, t=0.5):
    return min(top, key=lambda p: (abs(p[3] - t), -p[1]))


def masse(g):
    S = SP[g]
    return S, S / 36


# ============================================================================ Bögen

def sandsteinbogen(seed, g=1):
    """Sandsteinbogen: ein gewaltiger, rot-orange gebänderter Wüstenbogen auf sandigem Boden, mit Kakteen,
    toten Büschen und Felsbrocken."""
    w = _neu(seed)
    S, s = masse(g)
    rng = w.rng
    zellen = sockel(w, S * 0.75, lambda *_: w.b("sand" if rng.random() < 0.8 else "red_sand"), rz=0.6)
    mat = schichten(w, ["red_sandstone", "orange_terracotta", "smooth_red_sandstone", "terracotta",
                        "cut_red_sandstone", "red_terracotta", "smooth_sandstone"], dicke=1.6 + s)
    lo, occ, tg = koerper(w, pfad(S, S * 0.76, form=0.75), radius(S * 0.07 + 1.2, S * 0.11 + 2), rz=1.6, rauh=0.45)
    setzen(w, lo, occ, tg, mat)
    for (x, z) in zellen:
        if w.frei(x, 1, z) and rng.random() < 0.025:
            for k in range(1 + int(rng.random() * 3)):
                w.setze(x, 1 + k, z, w.b("cactus", age=0))
        elif w.frei(x, 1, z) and rng.random() < 0.03:
            w.setze(x, 1, z, w.b("dead_bush"))
    return w


def eisbogen(seed, g=1):
    """Eisbogen: ein schimmernder Bogen aus Pack- und Blaueis über einer Schneelandschaft, auf dem Scheitel eine
    Schneedecke, darunter hängen Eiszapfen."""
    w = _neu(seed)
    S, s = masse(g)
    sockel(w, S * 0.75, lambda *_: w.b("snow_block"), rz=0.6, unter=("packed_ice", "snow_block", "stone"))
    mat = mix(w, [("packed_ice", 4), ("blue_ice", 2), ("ice", 1), ("snow_block", 1)], zelle=2.2)
    lo, occ, tg = koerper(w, pfad(S, S * 0.8, form=0.9), radius(S * 0.06 + 1, S * 0.1 + 2), rz=1.3, rauh=0.4)
    top, unter = setzen(w, lo, occ, tg, mat, oben=lambda *_: w.b("snow_block"))
    ranken(w, unter, 0.18, "eis", lmax=4)
    for (x, y, z, t) in top:
        if w.frei(x, y + 1, z) and w.rng.random() < 0.5:
            w.setze(x, y + 1, z, w.b("snow", layers=1 + int(w.rng.random() * 2)))
    for k in range(3 + g):
        x, z = int((w.rng.random() - 0.5) * S * 1.2), int((w.rng.random() - 0.5) * S * 0.7)
        if w.frei(x, 1, z) and w.frei(x, 6, z):
            einfuegen(w, wald2.fichte(seed + k, schnee=True), x, 0, z)
    return w


def moosbogen(seed, g=1):
    """Moosbogen mit Wasserfall: ein bemooster Felsbogen, oben Wiese mit Bäumen, vom Scheitel stürzt ein
    Wasserfall in einen Teich, unten hängen leuchtende Höhlenranken."""
    w = _neu(seed)
    S, s = masse(g)
    teich = lambda x, z: math.hypot(x / 1.3, z - S * 0.12) < S * 0.17
    zellen = sockel(w, S * 0.8, gras(w), rz=0.7, frei=teich)
    mat = mix(w, [("stone", 3), ("mossy_cobblestone", 2), ("andesite", 2), ("tuff", 1), ("moss_block", 1)])
    lo, occ, tg = koerper(w, pfad(S, S * 0.74, form=0.8), radius(S * 0.08 + 1.2, S * 0.105 + 2), rz=1.5, rauh=0.4)
    top, unter = setzen(w, lo, occ, tg, mat, oben=gras(w), oben2=erde(w))
    ranken(w, unter, 0.3, "cave", lmax=int(4 + 4 * s))
    oben_bewuchs(w, top)
    baeume_oben(w, top, 2 + g, lambda sd: wald2.laubbaum(sd, "oak", H=5 + g))
    x, y, z, t = _scheitel(top)
    zr = max(p[2] for p in top if abs(p[0] - x) < 1 and abs(p[3] - t) < 0.05)
    for yy in range(1, y + 1):
        w.setze(x, yy, zr + 1, w.b("water", level=0))
    w.setze(x, y, zr, w.b("water", level=0))
    bodenbewuchs(w, zellen, 0.5)
    return w


def doppelbogen(seed, g=1):
    """Doppelbogen: zwei Felsbögen kreuzen sich über einer Lichtung, auf dem Kreuzungspunkt wächst ein Baum, an
    den Füßen liegen Felsbrocken."""
    w = _neu(seed)
    S, s = masse(g)
    zellen = sockel(w, S * 0.75, gras(w))
    mat = mix(w, [("calcite", 2), ("stone", 3), ("diorite", 1), ("andesite", 2)])
    for achse, H in (("x", S * 0.7), ("z", S * 0.62)):
        lo, occ, tg = koerper(w, pfad(S * (1 if achse == "x" else 0.85), H, form=0.8, achse=achse),
                              radius(S * 0.06 + 1, S * 0.095 + 1.6), rz=1.3, rauh=0.4, quer="z" if achse == "x" else "x")
        top, unter = setzen(w, lo, occ, tg, mat, oben=gras(w), oben2=erde(w))
        oben_bewuchs(w, top)
        ranken(w, unter, 0.12, "wurzel")
    yt = max(y for (x, y, z), b in w.bloecke.items() if abs(x) <= 1 and abs(z) <= 1)
    einfuegen(w, wald2.laubbaum(seed, "oak", H=5 + g), 0, yt, 0)
    bodenbewuchs(w, zellen, 0.45)
    return w


def basaltbogen(seed, g=1):
    """Basaltbogen: ein dunkler Bogen aus Basaltsäulen steigt aus dem Meer, um seine Füße stehen sechseckige
    Säulen in Stufen wie ein Damm aus Riesenhand."""
    w = _neu(seed)
    S, s = masse(g)
    wasserflaeche(w, int(S * 0.8), tiefe=3)
    mat = mix(w, [("basalt", 3), ("polished_basalt", 2), ("smooth_basalt", 1), ("blackstone", 1)], axis="y")
    lo, occ, tg = koerper(w, pfad(S, S * 0.68, form=0.9, fuss=-4), radius(S * 0.06 + 1, S * 0.1 + 2), rz=1.4,
                          rauh=0.3)
    top, unter = setzen(w, lo, occ, tg, mat, oben=lambda *_: w.b("moss_block" if w.rng.random() < 0.4 else
                                                                 "smooth_basalt"))
    rng = w.rng
    for fx in (-S / 2, S / 2):
        for k in range(int(14 + 10 * s)):
            ang = rng.random() * 6.283
            d = 2 + rng.random() * S * 0.25
            cx, cz = round(fx + math.cos(ang) * d), round(math.sin(ang) * d)
            h = max(1, int((S * 0.18) * (1 - d / (S * 0.3)) + rng.random() * 2))
            for dx in (0, 1):
                for dz in (0, 1):
                    for y in range(-2, h + 1):
                        w.setze(cx + dx, y, cz + dz, w.b("basalt" if y < h else "polished_basalt", axis="y"))
    return w


def kristallbogen(seed, g=1):
    """Kristallbogen: ein dunkler Tiefenschieferbogen, aus dem überall violette und blaue Kristalle wachsen, mit
    Amethystdrusen am Boden."""
    from kristall import kristall
    w = _neu(seed)
    S, s = masse(g)
    sockel(w, S * 0.7, mix(w, [("tuff", 2), ("calcite", 1), ("deepslate", 2), ("smooth_basalt", 1)]))
    mat = mix(w, [("deepslate", 3), ("cobbled_deepslate", 2), ("tuff", 1), ("calcite", 1)])
    lo, occ, tg = koerper(w, pfad(S, S * 0.74, form=0.85), radius(S * 0.06 + 1, S * 0.1 + 1.8), rz=1.3, rauh=0.4)
    top, unter = setzen(w, lo, occ, tg, mat)
    rng = w.rng
    for k in range(int(8 + 10 * s)):
        x, y, z, t = (top + unter)[int(rng.random() * len(top + unter))]
        auf = (x, y, z, t) in top[:len(top)] if False else y > 0
        d = (rng.normal() * 0.5, 1 if rng.random() < 0.6 else -1, rng.normal() * 0.5)
        kristall(w, (x, y, z), d, (2 + rng.random() * 5) * s + 1, (0.6 + rng.random() * 0.8) * s + 0.4,
                 art="amethyst" if rng.random() < 0.6 else "saphir")
    for k in range(int(20 * s) + 6):
        x, z = int((rng.random() - 0.5) * S * 1.2), int((rng.random() - 0.5) * S * 0.8)
        if w.frei(x, 1, z) and not w.frei(x, 0, z):
            w.setze(x, 1, z, w.b("amethyst_cluster", facing="up", waterlogged=False))
    return w


def wurzelbogen(seed, g=1):
    """Wurzelbogen: drei gewaltige, ineinander verschlungene Baumwurzeln bilden einen Bogen, oben ein grünes
    Blätterdach, unten hängen Wurzelfäden über einem Moosboden."""
    w = _neu(seed)
    S, s = masse(g)
    zellen = sockel(w, S * 0.7, mix(w, [("moss_block", 3), ("grass_block", 2), ("rooted_dirt", 1)]))
    holz = [mix(w, [("dark_oak_wood", 3), ("oak_wood", 1)], axis="y"),
            mix(w, [("spruce_wood", 3), ("dark_oak_wood", 1)], axis="y"),
            mix(w, [("oak_wood", 2), ("jungle_wood", 1)], axis="y")]
    for k in range(3):
        ph = k * 2.094
        pts = []
        for (x, y, z, t) in pfad(S, S * 0.68, form=0.8):
            off = (S * 0.05 + 1.2) * (1 - 0.4 * math.sin(math.pi * t))
            pts.append((x, y + off * math.sin(t * 9 + ph) * 0.6, z + off * math.cos(t * 9 + ph), t))
        lo, occ, tg = koerper(w, pts, radius(S * 0.035 + 0.7, S * 0.07 + 1.3), rz=1.0, rauh=0.25)
        top, unter = setzen(w, lo, occ, tg, holz[k], oben=(lambda *_: w.b("moss_block")) if k == 0 else None)
        ranken(w, unter, 0.2, "wurzel")
    yt = max(y for (x, y, z), b in w.bloecke.items() if abs(x) <= 1)
    rng = w.rng
    R = S * 0.18 + 2
    for dx in range(-int(R) - 1, int(R) + 2):
        for dy in range(-2, int(R * 0.6) + 1):
            for dz in range(-int(R) - 1, int(R) + 2):
                if (dx / R) ** 2 + (dy / (R * 0.55)) ** 2 + (dz / R) ** 2 <= 1 - rng.random() * 0.12:
                    w.setze(dx, yt + 1 + dy, dz, w.b("oak_leaves" if rng.random() < 0.7 else "azalea_leaves",
                                                     persistent=True, distance=1, waterlogged=False), False)
    bodenbewuchs(w, zellen, 0.4)
    return w


def korallenbogen(seed, g=1):
    """Korallenbogen: ein bunter Bogen steigt aus einer türkisen Lagune – unter Wasser lebende Korallen und
    Seegras, über Wasser rosa, gelb und blau geflecktes Gestein mit Muschelkalk."""
    w = _neu(seed)
    S, s = masse(g)
    R = int(S * 0.8)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z * 1.3) <= R:
                for y in range(-3, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -4, z, w.b("sand"))
    unter_w = mix(w, [("brain_coral_block", 1), ("tube_coral_block", 1), ("fire_coral_block", 1),
                      ("bubble_coral_block", 1), ("horn_coral_block", 1), ("prismarine", 1)], zelle=1.5)
    ueber_w = mix(w, [("pink_terracotta", 2), ("calcite", 2), ("yellow_terracotta", 1), ("light_blue_terracotta", 1),
                      ("magenta_terracotta", 1), ("white_terracotta", 1)], zelle=1.5)
    mat = lambda x, y, z, t: unter_w(x, y, z) if y <= 0 else ueber_w(x, y, z)
    lo, occ, tg = koerper(w, pfad(S, S * 0.68, form=0.85, fuss=-5), radius(S * 0.06 + 1, S * 0.1 + 2), rz=1.4,
                          rauh=0.5)
    setzen(w, lo, occ, tg, mat, ab_y=-4)
    rng = w.rng
    kor = ["brain_coral", "tube_coral", "fire_coral", "bubble_coral", "horn_coral"]
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if w.P.name(w.bloecke.get((x, -3, z), 0)) == "minecraft:water" and rng.random() < 0.15:
                r = rng.random()
                w.setze(x, -3, z, w.b(kor[int(rng.random() * 5)], waterlogged=True) if r < 0.5 else
                        w.b("seagrass") if r < 0.85 else w.b("sea_pickle", pickles=1 + int(rng.random() * 3),
                                                             waterlogged=True))
    return w


def lavabogen(seed, g=1):
    """Lavabogen: ein schwarzer Bogen aus Schwarzstein und Basalt mit glühenden Magmaadern, vom Scheitel fällt ein
    Lavastrom in ein Lavabecken, ringsum Asche und Basaltspitzen."""
    w = _neu(seed)
    S, s = masse(g)
    becken = lambda x, z: math.hypot(x / 1.4, z - S * 0.1) < S * 0.12
    zellen = sockel(w, S * 0.75, mix(w, [("blackstone", 2), ("basalt", 1), ("smooth_basalt", 1), ("magma_block", 1)]),
                    frei=becken, unter=("blackstone", "basalt", "blackstone"))
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) == "minecraft:water":
            w.bloecke[(x, y, z)] = w.b("lava", level=0)
    rv = Rauschen(w, 3)
    basis = mix(w, [("blackstone", 3), ("basalt", 1), ("polished_blackstone", 1), ("gilded_blackstone", 0.15)],
                axis="y")
    mat = lambda x, y, z, t: w.b("magma_block") if abs(rv(x, y, z) - 0.5) < 0.04 else basis(x, y, z)
    lo, occ, tg = koerper(w, pfad(S, S * 0.74, form=0.8, spitz=True), radius(S * 0.06 + 1, S * 0.105 + 2), rz=1.3,
                          rauh=0.45)
    top, unter = setzen(w, lo, occ, tg, mat)
    ranken(w, unter, 0.12, "tropf", lmax=3)
    x, y, z, t = _scheitel(top)
    zr = max(p[2] for p in top if abs(p[0] - x) < 1 and abs(p[3] - t) < 0.05)
    for yy in range(1, y + 1):
        w.setze(x, yy, zr + 1, w.b("lava", level=0))
    rng = w.rng
    for k in range(int(6 + 6 * s)):
        cx, cz = int((rng.random() - 0.5) * S * 1.2), int((rng.random() - 0.5) * S * 0.9)
        if (cx, cz) in zellen and w.frei(cx, 1, cz):
            for yy in range(1, 2 + int(rng.random() * 4 * s + 1)):
                w.setze(cx, yy, cz, w.b("basalt", axis="y"))
    return w


def schwebebogen(seed, g=1):
    """Gebrochener Schwebebogen: ein Felsbogen, dessen Mittelstück zerbrochen in der Luft schwebt – die Bruchstücke
    hängen über der Lücke, Ranken und Gras überall, darunter eine Blumenwiese."""
    w = _neu(seed)
    S, s = masse(g)
    zellen = sockel(w, S * 0.75, gras(w))
    mat = mix(w, [("stone", 3), ("andesite", 2), ("mossy_cobblestone", 1), ("calcite", 1)])
    lo, occ, tg = koerper(w, pfad(S, S * 0.74, form=0.85), radius(S * 0.06 + 1, S * 0.1 + 1.8), rz=1.4, rauh=0.4)
    teile = [(0.0, 0.4, 0), (0.6, 1.0, 0), (0.44, 0.56, int(3 + 3 * s))]
    for (a, b, dy) in teile:
        m = occ & (tg >= a) & (tg <= b)
        top, unter = setzen(w, lo + np.array([0, dy, 0]), m, tg, mat, oben=gras(w), oben2=erde(w))
        oben_bewuchs(w, top)
        ranken(w, unter, 0.25, "cave", lmax=4)
    rng = w.rng
    for k in range(int(5 + 5 * s)):
        cx, cy, cz = (rng.random() - 0.5) * S * 0.3, S * 0.55 + rng.random() * S * 0.2, (rng.random() - 0.5) * S * 0.4
        r = 0.8 + rng.random() * 1.5 * s
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                for dz in range(-2, 3):
                    if dx * dx + dy * dy * 1.5 + dz * dz <= r * r:
                        w.setze(round(cx + dx), round(cy + dy), round(cz + dz), mat(round(cx + dx), 0, dz, 0), False)
    bodenbewuchs(w, zellen, 0.6)
    return w


def tempelbogen(seed, g=1):
    """Tempelbogen: ein breiter Spitzbogen aus hellem Fels, auf dessen Scheitel ein kleiner Säulentempel mit
    goldener Kuppel thront, Kerzen und Treppen an der Flanke."""
    w = _neu(seed)
    S, s = masse(g)
    zellen = sockel(w, S * 0.75, gras(w))
    mat = schichten(w, ["smooth_sandstone", "sandstone", "calcite", "cut_sandstone"], dicke=2 + s)
    lo, occ, tg = koerper(w, pfad(S, S * 0.74, spitz=True), radius(S * 0.07 + 1.4, S * 0.105 + 2), rz=1.6, rauh=0.3)
    top, unter = setzen(w, lo, occ, tg, mat, oben=gras(w), oben2=erde(w))
    oben_bewuchs(w, top, 0.3)
    yt = max(p[1] for p in top if abs(p[0]) <= 2 and abs(p[2]) <= 2)
    for x in range(-3, 4):
        for z in range(-3, 4):
            for yy in range(yt - 2, yt + 1):
                w.setze(x, yy, z, w.b("smooth_quartz" if yy == yt else "sandstone"))
            for yy in range(yt + 1, yt + 6):
                w.bloecke.pop((x, yy, z), None)
    for (x, z) in ((-3, -3), (3, -3), (-3, 3), (3, 3), (0, -3), (0, 3), (-3, 0), (3, 0)):
        for yy in range(yt + 1, yt + 5):
            w.setze(x, yy, z, w.b("quartz_pillar", axis="y"))
    for x in range(-3, 4):
        for z in range(-3, 4):
            w.setze(x, yt + 5, z, w.b("chiseled_quartz_block") if (abs(x) == 3 or abs(z) == 3) else
                    w.b("smooth_quartz"))
    for x in range(-3, 4):
        for yy in range(0, 4):
            for z in range(-3, 4):
                d = math.sqrt(x * x + (yy * 1.2) ** 2 + z * z)
                if 2.2 < d <= 3.3:
                    w.setze(x, yt + 6 + yy, z, w.b("gold_block" if yy < 3 else "yellow_terracotta"))
    w.setze(0, yt + 1, 0, w.b("enchanting_table"))
    for (x, z) in ((-2, -2), (2, 2), (-2, 2), (2, -2)):
        w.setze(x, yt + 1, z, w.b("candle", candles=3, lit=True, waterlogged=False))
    bodenbewuchs(w, zellen, 0.4)
    return w


def pfadbogen(seed, g=1):
    """Pfadbogen: über den Felsbogen führt ein gepflasterter Wanderweg mit Holzgeländer und Laternenpfählen, an
    beiden Füßen beginnt eine Treppe, unten fließt ein Bach."""
    w = _neu(seed)
    S, s = masse(g)
    bach = lambda x, z: abs(z + 2 * math.sin(x / 5)) < 1.5 + s and abs(x) < S * 0.3
    zellen = sockel(w, S * 0.8, gras(w), frei=bach)
    mat = mix(w, [("stone", 3), ("andesite", 1), ("cobblestone", 1), ("mossy_cobblestone", 1)])
    lo, occ, tg = koerper(w, pfad(S, S * 0.62, form=0.65), radius(S * 0.06 + 1.6, S * 0.095 + 2.2), rz=1.5, rauh=0.25)
    top, unter = setzen(w, lo, occ, tg, mat, oben=gras(w), oben2=erde(w))
    weg = Mix(w, [("cobblestone", 2), ("stone_bricks", 2), ("mossy_cobblestone", 1), ("gravel", 1)], zelle=1.2)
    spalten = {}
    for (x, y, z, t) in top:
        if abs(z) <= 1:
            w.setze(x, y, z, weg(x, y, z))
            spalten[x] = max(spalten.get(x, -99), y)
    for x, y in sorted(spalten.items()):
        for z in (-2, 2):
            if (x, y, z) in w.bloecke and w.frei(x, y + 1, z):
                w.setze(x, y + 1, z, zaun(w, "spruce", "x"))
        if x % 6 == 0:
            for yy in range(y + 1, y + 4):
                w.setze(x, yy, 2, zaun(w, "spruce"))
            w.setze(x, y + 4, 2, w.b("lantern", hanging=False, waterlogged=False))
    oben_bewuchs(w, top, 0.35)
    ranken(w, unter, 0.15, "cave", lmax=3)
    bodenbewuchs(w, zellen, 0.45)
    return w


def gewundener_bogen(seed, g=1):
    """Gewundener Bogen: zwei schlanke Felsstränge – einer hell, einer dunkel – winden sich spiralförmig umeinander
    zu einem verdrehten Bogen, Moos in den Fugen."""
    w = _neu(seed)
    S, s = masse(g)
    zellen = sockel(w, S * 0.7, gras(w))
    mats = [mix(w, [("calcite", 3), ("diorite", 1), ("smooth_stone", 1)]),
            mix(w, [("deepslate", 2), ("tuff", 2), ("cobbled_deepslate", 1)])]
    for k in range(2):
        pts = []
        for (x, y, z, t) in pfad(S, S * 0.74, form=0.85):
            off = (S * 0.06 + 1.2) * (1 - 0.3 * math.sin(math.pi * t))
            ph = t * 6.283 * 2.5 + k * math.pi
            pts.append((x, y + off * math.sin(ph), z + off * math.cos(ph), t))
        lo, occ, tg = koerper(w, pts, radius(S * 0.045 + 0.9, S * 0.08 + 1.5), rz=1.0, rauh=0.3)
        top, unter = setzen(w, lo, occ, tg, mats[k], oben=(lambda *_: w.b("moss_block")) if k == 0 else None)
        oben_bewuchs(w, top, 0.25)
    bodenbewuchs(w, zellen, 0.45)
    return w


def bogenkette(seed, g=1):
    """Bogenkette: drei aneinandergereihte Felsbögen unterschiedlicher Größe überspannen einen Fluss wie ein
    natürliches Aquädukt, oben Gras und Büsche, unten Seerosen."""
    w = _neu(seed)
    S, s = masse(g)
    fluss = lambda x, z: abs(z) < S * 0.12
    zellen = sockel(w, S * 1.0, gras(w), rx=1.2, rz=0.6, frei=fluss)
    mat = schichten(w, ["stone", "andesite", "tuff", "stone", "calcite"], dicke=1.5 + s)
    xs = [(-S * 0.55, S * 0.45, S * 0.38), (0, S * 0.6, S * 0.48), (S * 0.55, S * 0.45, S * 0.38)]
    for (x0, Sp, H) in xs:
        lo, occ, tg = koerper(w, pfad(Sp, H, form=0.75, x0=x0, achse="x"),
                              radius(S * 0.05 + 1, S * 0.1 + 1.5), rz=1.4, rauh=0.35)
        top, unter = setzen(w, lo, occ, tg, mat, oben=gras(w), oben2=erde(w))
        oben_bewuchs(w, top)
        ranken(w, unter, 0.2, "cave", lmax=3)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y == 0 and w.P.name(b) == "minecraft:water" and rng.random() < 0.06 and w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("lily_pad"))
    bodenbewuchs(w, zellen, 0.45)
    return w


def felsenfenster(seed, g=1):
    """Felsenfenster: eine mächtige Felswand mit einem großen, ovalen Durchbruch, oben ein Wäldchen, Efeu und
    Wasserrinnsale an der Wand, unten Geröll und Farn."""
    w = _neu(seed)
    S, s = masse(g)
    zellen = sockel(w, S * 0.75, gras(w), rz=0.7)
    mat = schichten(w, ["stone", "andesite", "stone", "tuff", "gravel", "stone"], dicke=1.5 + s)
    rs = Rauschen(w, 6)
    A, H, T = S * 0.5, S * 0.7, S * 0.095 + 2
    hx, hy = S * 0.22, S * 0.28
    top = []
    for x in range(-int(A) - 2, int(A) + 3):
        for z in range(-int(T) - 2, int(T) + 3):
            prof = 1 - (x / A) ** 2
            if prof <= 0:
                continue
            ht = H * prof ** 0.5 * (0.85 + 0.3 * rs(x, 0, z)) * (1 - (z / (T * (1.2 - 0.4 * prof ** 0.5))) ** 2)
            for y in range(-2, int(ht) + 1):
                if (x / hx) ** 2 + ((y - H * 0.35) / hy) ** 2 < 1 + 0.15 * (rs(x, y, z) - 0.5):
                    continue
                w.setze(x, y, z, mat(x, y, z))
            if ht > 3:
                yt = int(ht)
                w.setze(x, yt, z, w.b("grass_block", snowy=False))
                w.setze(x, yt - 1, z, w.b("dirt"))
                top.append((x, yt, z, 0.5 + x / (2 * A)))
    oben_bewuchs(w, top, 0.5)
    baeume_oben(w, top, 2 + g, lambda sd: wald2.birke(sd), abstand=5, t_bereich=(0.15, 0.85))
    from feinbau import efeu
    efeu(w, 0.1, laub=0.3)
    bodenbewuchs(w, zellen, 0.5)
    return w


def kirschbluetenbogen(seed, g=1):
    """Kirschblütenbogen: ein sanft geschwungener Bogen, oben stehen Kirschbäume, rosa Blütenblätter bedecken
    Bogen und Wiese, darunter ein kleiner Steg über einen Teich."""
    w = _neu(seed)
    S, s = masse(g)
    teich = lambda x, z: math.hypot(x / 1.5, z) < S * 0.15
    zellen = sockel(w, S * 0.8, gras(w), rz=0.75, frei=teich)
    mat = mix(w, [("stone", 2), ("calcite", 2), ("andesite", 1), ("mossy_cobblestone", 1)])
    lo, occ, tg = koerper(w, pfad(S, S * 0.62, form=0.7), radius(S * 0.06 + 1.2, S * 0.095 + 1.8), rz=1.5, rauh=0.35)
    top, unter = setzen(w, lo, occ, tg, mat, oben=gras(w), oben2=erde(w))
    baeume_oben(w, top, 2 + g, lambda sd: wald2.kirschbaum(sd), abstand=7)
    rng = w.rng
    for (x, y, z, t) in top + [(x, 0, z, 0) for (x, z) in zellen]:
        if w.frei(x, y + 1, z) and rng.random() < 0.35 and w.P.name(w.bloecke.get((x, y, z), 0)) == \
                "minecraft:grass_block":
            w.setze(x, y + 1, z, w.b("pink_petals", facing=["north", "east", "south", "west"][int(rng.random() * 4)],
                                     flower_amount=1 + int(rng.random() * 4)))
    for x in range(-int(S * 0.2), int(S * 0.2) + 1):
        w.setze(x, 1, 0, platte(w, "cherry"))
    for k in range(2 + g):
        x, z = int((rng.random() - 0.5) * S), int((rng.random() * 0.4 + 0.3) * S * 0.5 * (1 if k % 2 else -1))
        if (x, z) in zellen and w.frei(x, 3, z):
            einfuegen(w, wald2.kirschbaum(seed + k), x, 0, z)
    return w


def netherbogen(seed, g=1):
    """Nether-Bogen: ein roter Bogen aus Netherrack und Netherziegeln, oben Karmesin-Nyzel mit Pilzbäumen,
    darunter hängen Trauerranken und Pilzlicht, am Boden Seelensand und Lava."""
    w = _neu(seed)
    S, s = masse(g)
    lava = lambda x, z: math.hypot(x / 1.6, z) < S * 0.1
    zellen = sockel(w, S * 0.75, mix(w, [("crimson_nylium", 3), ("netherrack", 2), ("soul_sand", 1)]), frei=lava,
                    unter=("netherrack", "netherrack", "basalt"))
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) == "minecraft:water":
            w.bloecke[(x, y, z)] = w.b("lava", level=0)
    mat = mix(w, [("netherrack", 4), ("nether_bricks", 1), ("red_nether_bricks", 1), ("nether_wart_block", 1),
                  ("nether_quartz_ore", 0.3)])
    lo, occ, tg = koerper(w, pfad(S, S * 0.74, form=0.85), radius(S * 0.06 + 1, S * 0.1 + 1.8), rz=1.4, rauh=0.45)
    top, unter = setzen(w, lo, occ, tg, mat, oben=lambda *_: w.b("crimson_nylium"))
    ranken(w, unter, 0.3, "weeping", lmax=int(3 + 4 * s))
    rng = w.rng
    for (x, y, z, t) in unter:
        if rng.random() < 0.04:
            w.setze(x, y, z, w.b("shroomlight"))
    for (x, y, z, t) in top:
        if w.frei(x, y + 1, z) and rng.random() < 0.25:
            w.setze(x, y + 1, z, w.b(["crimson_roots", "crimson_fungus", "crimson_roots"][int(rng.random() * 3)]))
    for (x, z) in zellen:
        if w.frei(x, 1, z) and rng.random() < 0.15 and w.P.name(w.bloecke.get((x, 0, z), 0)) == \
                "minecraft:crimson_nylium":
            w.setze(x, 1, z, w.b("crimson_roots"))
    return w


def endbogen(seed, g=1):
    """End-Bogen: ein bleicher Bogen aus Endstein mit Purpur-Adern über einer schwarzen Leere, auf ihm wachsen
    Chorusgewächse, Endstäbe leuchten, an den Füßen stehen Obsidiansäulen."""
    w = _neu(seed)
    S, s = masse(g)
    zellen = sockel(w, S * 0.7, mix(w, [("end_stone", 4), ("end_stone_bricks", 1)]), unter=("end_stone",))
    rv = Rauschen(w, 4)
    basis = mix(w, [("end_stone", 4), ("end_stone_bricks", 1)])
    mat = lambda x, y, z, t: w.b("purpur_block") if abs(rv(x, y, z) - 0.5) < 0.05 else basis(x, y, z)
    lo, occ, tg = koerper(w, pfad(S, S * 0.76, form=0.9), radius(S * 0.055 + 1, S * 0.095 + 1.8), rz=1.3, rauh=0.4)
    top, unter = setzen(w, lo, occ, tg, mat)
    rng = w.rng
    for (x, y, z, t) in top:
        if w.frei(x, y + 1, z) and rng.random() < 0.05:
            h = 1 + int(rng.random() * 3 * s + 1)
            for k in range(1, h + 1):
                w.setze(x, y + k, z, w.b("chorus_plant", up=k < h, down=True, north=False, south=False, east=False,
                                         west=False))
            w.setze(x, y + h + 1, z, w.b("chorus_flower", age=5 if rng.random() < 0.5 else 0))
        elif w.frei(x, y + 1, z) and rng.random() < 0.02:
            w.setze(x, y + 1, z, w.b("end_rod", facing="up"))
    for fx in (-S * 0.75, S * 0.75):
        for k in range(2):
            cx, cz = round(fx + (rng.random() - 0.5) * 4), round((k - 0.5) * S * 0.5)
            h = int(S * 0.25 + rng.random() * S * 0.2)
            for y in range(-2, h):
                for dx in range(-1, 2):
                    for dz in range(-1, 2):
                        if abs(dx) + abs(dz) < 2:
                            w.setze(cx + dx, y, cz + dz, w.b("obsidian" if rng.random() < 0.85 else "crying_obsidian"))
            w.setze(cx, h, cz, w.b("end_rod", facing="up"))
    return w


def walknochenbogen(seed, g=1):
    """Walknochen-Bogen: am Strand bilden die gebleichten Rippen eines riesigen Wals einen Tunnel aus Bögen, oben
    läuft das Rückgrat entlang, Seegras und Muschelsand ringsum."""
    w = _neu(seed)
    S, s = masse(g)
    meer = lambda x, z: z > S * 0.35
    zellen = sockel(w, S * 0.85, lambda *_: w.b("sand" if w.rng.random() < 0.85 else "gravel"), frei=meer,
                    unter=("sand", "sandstone"))
    knochen = lambda *_: w.b("bone_block", axis="y")
    L = S * 0.9
    n = int(5 + 4 * s)
    for i in range(n):
        x0 = -L / 2 + L * i / (n - 1)
        f = 1 - 0.5 * abs(i / (n - 1) - 0.4) ** 1.5
        lo, occ, tg = koerper(w, pfad(S * 0.55 * f, S * 0.45 * f, form=0.75, x0=x0, achse="z", fuss=-2),
                              radius(S * 0.02 + 0.6, S * 0.03 + 0.9), rz=1.0, rauh=0.2, quer="x")
        setzen(w, lo, occ, tg, knochen)
    yt = int(S * 0.45 * 0.97)
    for x in range(int(-L / 2) - int(S * 0.15), int(L / 2) + 2):
        f = 1 - 0.5 * abs((x + L / 2) / L - 0.4) ** 1.5
        y = round(S * 0.45 * f) - 1
        r = 1 if x % 3 else 2
        for dy in range(-r + 1, r):
            for dz in range(-r + 1, r):
                w.setze(x, y + dy, dz, w.b("bone_block", axis="x"))
        if x % 3 == 0:
            w.setze(x, y + r, 0, w.b("bone_block", axis="y"))
    for (x, z) in zellen:
        if w.frei(x, 1, z) and w.rng.random() < 0.02:
            w.setze(x, 1, z, w.b("dead_bush"))
    return w


def regenbogen(seed, g=1):
    """Regenbogen mit Wolken: ein leuchtender Regenbogen aus sieben Farbbändern spannt sich über eine Wiese, seine
    Enden ruhen auf flauschigen Wolken, unter einem Ende steht ein Topf voll Gold."""
    w = _neu(seed)
    S, s = masse(g)
    zellen = sockel(w, S * 0.8, gras(w), rz=0.6)
    farben = ["red_concrete", "orange_concrete", "yellow_concrete", "lime_concrete", "light_blue_concrete",
              "blue_concrete", "purple_concrete"]
    R0 = S * 0.5
    dicke = max(1.0, 0.9 * s + 0.4)
    breite = int(1 + s)
    for i, f in enumerate(farben):
        R = R0 - i * dicke
        for k in range(int(R * 12)):
            a = math.pi * k / (R * 12)
            for dd in np.arange(0, dicke, 0.5):
                x, y = (R - dd) * math.cos(a), (R - dd) * math.sin(a) * 0.95 + 3
                for z in range(-breite, breite + 1):
                    w.setze(round(x), round(y), z, w.b(f))
    rng = w.rng
    for fx in (-R0 + dicke * 3, R0 - dicke * 3):
        for k in range(int(10 + 8 * s)):
            cx = fx + (rng.random() - 0.5) * S * 0.25
            cy = 2 + rng.random() * 3 * s
            cz = (rng.random() - 0.5) * S * 0.2
            r = 1.5 + rng.random() * 2.5 * s
            for dx in range(-int(r) - 1, int(r) + 2):
                for dy in range(-int(r) - 1, int(r) + 2):
                    for dz in range(-int(r) - 1, int(r) + 2):
                        if dx * dx + (dy * 1.5) ** 2 + dz * dz <= r * r:
                            w.setze(round(cx + dx), max(1, round(cy + dy)), round(cz + dz),
                                    w.b("white_wool" if rng.random() < 0.85 else "white_concrete_powder"))
    px = round(R0 - dicke * 3)
    pz = round(S * 0.25)
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            for y in range(1, 4):
                if abs(dx) == 2 or abs(dz) == 2 or y == 1:
                    if not (abs(dx) == 2 and abs(dz) == 2):
                        w.setze(px + dx, y, pz + dz, w.b("black_concrete" if y < 3 else "gray_concrete"))
                else:
                    w.setze(px + dx, y, pz + dz, w.b("gold_block" if y == 2 else "raw_gold_block"))
    w.setze(px, 4, pz, w.b("gold_block"))
    bodenbewuchs(w, zellen, 0.5)
    return w


BOGEN2 = {
    "sandsteinbogen": ("Sandsteinbogen", sandsteinbogen),
    "eisbogen": ("Eisbogen", eisbogen),
    "moosbogen": ("Moosbogen mit Wasserfall", moosbogen),
    "doppelbogen": ("Doppelbogen", doppelbogen),
    "basaltbogen": ("Basaltbogen", basaltbogen),
    "kristallbogen": ("Kristallbogen", kristallbogen),
    "wurzelbogen": ("Wurzelbogen", wurzelbogen),
    "korallenbogen": ("Korallenbogen", korallenbogen),
    "lavabogen": ("Lavabogen", lavabogen),
    "schwebebogen": ("Gebrochener Schwebebogen", schwebebogen),
    "tempelbogen": ("Tempelbogen", tempelbogen),
    "pfadbogen": ("Pfadbogen mit Geländer", pfadbogen),
    "gewundener_bogen": ("Gewundener Bogen", gewundener_bogen),
    "bogenkette": ("Bogenkette über dem Fluss", bogenkette),
    "felsenfenster": ("Felsenfenster", felsenfenster),
    "kirschbluetenbogen": ("Kirschblütenbogen", kirschbluetenbogen),
    "netherbogen": ("Nether-Bogen", netherbogen),
    "endbogen": ("End-Bogen", endbogen),
    "walknochenbogen": ("Walknochen-Bogen", walknochenbogen),
    "regenbogen": ("Regenbogen mit Wolken", regenbogen),
}

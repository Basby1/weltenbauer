"""Dschungeltempel, Wikingerdorf und Mittelaltermarkt (neu) – je 20 Bauten.

Mit Blöcken aus dem Modpack (Macaw's Roofs/Paths/Bridges/Lights, Supplementaries, Farmer's Delight,
Decorative Blocks, Twigs, Chipped) – alle mit Vanilla-Ersatz.
"""

from __future__ import annotations

import math

import numpy as np

import modbloecke as MB
import pracht as P
from lib import Rauschen, Verlauf, einfuegen, laub, zerfall
from pracht import Mat, gelaende, treppe
from skulptur import Skulptur, dreh_y, ell, kap, kreisrand, ohne, scheibe, spiegel_x, zur_mitte
from weltwunder import bl, hohl, platz, sk

U = [0.6, 1.0, 1.7, 2.8]
GEGEN = {"north": "south", "south": "north", "east": "west", "west": "east"}


def _welt(seed):
    from lib import Welt
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _wand(w, name):
    return w.b(name, up=True, north="none", south="none", east="none", west="none", waterlogged=False)


def ranken(w, dichte=0.04, min_y=2):
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y < min_y or rng.random() > dichte:
            continue
        for dx, dz, sd in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
            if w.frei(x + dx, y, z + dz):
                for k in range(int(1 + rng.random() * 6)):
                    if not w.frei(x + dx, y - k, z + dz) or y - k < 1:
                        break
                    w.setze(x + dx, y - k, z + dz, w.b("vine", **{q: q == sd for q in ("north", "east", "south", "west")},
                                                       up=False))
                break


def moos_oben(w, dichte=0.35, min_y=1):
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y >= min_y and w.frei(x, y + 1, z) and rng.random() < dichte and "leaves" not in w.P.name(b):
            w.setze(x, y + 1, z, w.b("moss_carpet"))


# ============================================================================ DSCHUNGEL


def _ds(w, seed):
    if _stil(seed) == 0:
        return dict(M=Mat(w, "moosstein"), S=Mat(w, ["mossy_cobblestone", "cobblestone", "mossy_stone_bricks",
                                                      "chiseled_stone_bricks", "stone_bricks"]),
                    tr="mossy_stone_brick", gold="gold_block", akz="emerald_block", holz="jungle", licht="lantern")
    return dict(M=Mat(w, ["smooth_sandstone", "cut_sandstone", "mossy_cobblestone", "sandstone", "chiseled_sandstone",
                          "terracotta"], kontrast=1.1),
                S=Mat(w, ["cut_sandstone", "sandstone", "mossy_cobblestone", "smooth_sandstone"]),
                tr="sandstone", gold="gold_block", akz="lapis_block", holz="jungle", licht="lantern")


def dschungelboden(w, R, dichte=1.0):
    gelaende(w, R, art="wald", dichte=dichte)
    rng = w.rng
    import wald
    w.folgen = {}
    for x, z in scheibe(R):
        if w.frei(x, 1, z) and rng.random() < 0.05 * dichte:
            wald.hohes("large_fern")(w, x, 1, z)
        elif w.frei(x, 1, z) and rng.random() < 0.015 * dichte:
            wald.bambus(w, x, 1, z)
    del w.folgen


def dschungelbaum(w, x, z, gross=0):
    import baeume as B
    einfuegen(w, B.ARTEN["dschungelriese"][1](int(w.rng.integers(1, 10 ** 6)), gross), x, 0, z)


def stufenpyramide(seed, g=2):
    """Dschungel-Stufenpyramide: verwitterte Terrassen mit Moos und Ranken, Prunktreppe, Tempelhaus mit
    Jaguar-Köpfen, Smaragd-Augen und einem Schatz im Allerheiligsten."""
    from kathedralen import stufentempel
    w = stufentempel(seed - 0 if _stil(seed) == 0 else seed - 14, g)
    ranken(w, 0.05)
    moos_oben(w, 0.3)
    return w


def dschungelruine(seed, g=2):
    """Dschungelruine: Mauerreste und eingestürzte Hallen eines Palastes, von Urwaldriesen gesprengt, Wurzeln
    über den Steinen, Ranken überall."""
    w = _welt(seed)
    d = _ds(w, seed)
    u = U[g]
    a = _r(12 * u + 5)
    dschungelboden(w, a + 8)
    st = P.Stil(w, wand=d["M"], sockel=d["S"], gesims=d["tr"], dach="moos", holz="jungle", laeden=False, blumen=0)
    P.gebaeude(w, st, -a, -a // 2, a // 3, a // 2, y0=1, etagen=2, eh=_r(3 * u + 3, 4), dach="flach", tuer="south")
    P.gebaeude(w, st, a // 3 + 3, -a // 3, a, a // 2, y0=1, etagen=1, eh=_r(4 * u + 3, 4), dach="flach", tuer="west")
    zerfall(w, set(b for b in w.bloecke.values() if b), Rauschen(w, 3), 14 * u, staerke=0.75, boden=2)
    dschungelbaum(w, 0, 0, 1 if g >= 2 else 0)
    dschungelbaum(w, a - 2, -a // 2 - 3, 0)
    ranken(w, 0.07)
    moos_oben(w, 0.4)
    hohl(w, 2)
    return w


def baumhausdorf(seed, g=2):
    """Baumhausdorf: Hütten auf Plattformen in Urwaldriesen, verbunden durch Seil-Hängebrücken (Macaw's
    Bridges), Strickleitern und Laternen."""
    w = _welt(seed)
    u = U[g]
    rng = w.rng
    R = _r(14 * u + 6)
    dschungelboden(w, R + 4, 0.6)
    n = 3 + g
    pts = []
    for i in range(n):
        a = i / n * 2 * math.pi + rng.random() * 0.3
        x, z = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        pts.append((x, z))
        dschungelbaum(w, x, z, 1 if g >= 2 else 0)
    yp = _r(9 * u + 5)
    st = P.Stil(w, wand="holz_hell", sockel=["jungle_planks"], gesims="jungle", dach="mcw_stroh", holz="jungle",
                laeden=False)
    for (x, z) in pts:
        for (xx, yy, zz), b in list(w.bloecke.items()):
            if yp <= yy <= yp + 6 and abs(xx - x) <= 4 and abs(zz - z) <= 4 and "leaves" in w.P.name(b):
                del w.bloecke[(xx, yy, zz)]
        for xx, zz in scheibe(4, x, z):
            w.setze(xx, yp - 1, zz, w.b("jungle_planks"))
        for xx, zz in kreisrand(4, x, z):
            w.setze(xx, yp, zz, MB.lattenzaun(w, "jungle", north=True, south=True, east=True, west=True))
        P.gebaeude(w, st, x - 2, z - 2, x + 2, z + 2, y0=yp, etagen=1, eh=3, dach="walm", tuer="south", sockel_h=0,
                   gauben=False, kamine=0)
        for y in range(1, yp):
            w.setze(x + 4, y, z, w.b("ladder", facing="east", waterlogged=False))
    for i in range(n):
        (ax, az), (bx, bz) = pts[i], pts[(i + 1) % n]
        L = int(max(abs(bx - ax), abs(bz - az)))
        for k in range(L + 1):
            t = k / max(1, L)
            x, z = round(ax + (bx - ax) * t), round(az + (bz - az) * t)
            if math.hypot(x - ax, z - az) > 4 and math.hypot(x - bx, z - bz) > 4:
                sag = int(2 * math.sin(t * math.pi))
                f = "east" if abs(bx - ax) >= abs(bz - az) else "north"
                w.setze(x, yp - 1 - sag, z, MB.mod(w, "mcwbridges:rope_jungle_bridge", "jungle_slab",
                                                   dict(type="bottom", waterlogged=False), facing=f,
                                                   toggle=False, torch=False))
    hohl(w, 2)
    return w


def schlangentor(seed, g=1):
    """Schlangentor: Torbogen aus zwei sich aufbäumenden steinernen Schlangen, deren Köpfe sich oben treffen."""
    w = _welt(seed)
    d = _ds(w, seed)
    u = U[g]
    S = Skulptur(w, 1.0 * u + 0.4)
    S.mat("k", sk(d["M"], 0, 14 * u))
    S.mat("a", bl(w, d["akz"]))
    S.mat("g", bl(w, d["gold"]))
    for sx in (-1, 1):
        pts = [(sx * 7, 0, 0), (sx * 7.5, 4, 0.5), (sx * 6.5, 8, -0.5), (sx * 5, 11, 0), (sx * 2.5, 13, 0.6)]
        for a, b in zip(pts, pts[1:]):
            S.plus(kap(a, b, 1.6, 1.4), "k")
        S.plus(ell(sx * 1.6, 13.2, 0.8, 1.8, 1.3, 1.6), "k")
        S.plus(ell(sx * 1.6, 13.7, 2.0, 0.35, 0.35, 0.3), "a")
        S.plus(kap((sx * 0.6, 12.6, 1.8), (sx * 0.2, 11.8, 2.6), 0.25, 0.1), "g")
    S.rendern((-10, -1, -3), (10, 16, 4), versatz=(0.5, 1.01, 0.5))
    dschungelboden(w, _r(12 * u + 4))
    for z in range(-8, 9):
        for x in (-1, 0, 1):
            w.setze(x, 0, z, MB.pflaster(w, "mossy_cobblestone", "basket_weave_paving") if (x + z) % 2 else
                    w.b("mossy_cobblestone"))
    ranken(w, 0.04)
    hohl(w, 2)
    return w


def wasserfallschrein(seed, g=2):
    """Wasserfallschrein: ein kleiner Tempel hinter einem Wasserfall in einer bemoosten Felswand, Becken,
    Trittsteine und Fackeln."""
    w = _welt(seed)
    d = _ds(w, seed)
    u = U[g]
    W, H, D = _r(12 * u + 5), _r(16 * u + 6), _r(10 * u + 4)
    fels = Mat(w, ["stone", "mossy_cobblestone", "andesite", "moss_block", "cobblestone", "tuff"], kontrast=1.3)
    r_n = Rauschen(w, 4)
    for x in range(-W, W + 1):
        for z in range(-D, 1):
            hh = H * (0.8 + 0.3 * r_n(x, 0, z))
            for y in range(0, int(hh) + 1):
                w.setze(x, y, z, fels(x, y, z, y / H))
            w.setze(x, int(hh) + 1, z, w.b("grass_block", snowy=False))
    for x in range(-3, 4):
        for y in range(1, 7):
            for z in range(-5, 1):
                w.bloecke.pop((x, y, z), None)
    st = P.Stil(w, wand=d["M"], sockel=d["S"], gesims=d["tr"], dach="mcw_gruen", holz="jungle", laeden=False)
    for x in range(-2, 3):
        w.setze(x, 6, -2, d["M"](x, 6, -2, 0.7))
    w.setze(0, 1, -4, w.b(d["gold"]))
    w.setze(0, 2, -4, w.b("lantern", hanging=False, waterlogged=False))
    for x in range(-2, 3):
        w.setze(x, H - 2, 1, w.b("water", level=0))
    for x, z in scheibe(4 * u + 2, 0, 5):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("mossy_cobblestone"))
    for k in range(4):
        w.setze(-3 + k * 2, 1, 4 + (k % 2), w.b("mossy_cobblestone"))
    dschungelboden(w, _r(W + 4), 0.8)
    ranken(w, 0.05)
    hohl(w, 3)
    return w


def steinkopf(seed, g=2):
    """Steinkopf: ein riesiges steinernes Gesicht mit Helm, halb vom Dschungel verschlungen."""
    w = _welt(seed)
    d = _ds(w, seed)
    u = U[g]
    S = Skulptur(w, 1.6 * u + 0.4)
    S.mat("k", sk(d["S"], 0, 14 * u))
    S.mat("a", bl(w, d["akz"]))
    S.mat("d", bl(w, "black_concrete"))
    S.plus(ell(0, 5, 0, 4.5, 5.5, 4.2), "k")
    S.plus(ell(0, 9.5, -0.3, 5.0, 2.2, 4.6), "k")                  # Helm
    S.plus(kap((0, 6, 3.6), (0, 3.8, 4.8), 0.9, 1.1), "k")         # Nase
    S.plus(kap((-1.8, 2.4, 3.8), (1.8, 2.4, 3.8), 0.6), "k")       # Lippen
    S.plus(spiegel_x(ell(1.8, 6.6, 3.6, 0.9, 0.5, 0.4)), "d")
    S.plus(spiegel_x(ell(4.6, 5, 0, 0.9, 1.8, 1.0)), "k")          # Ohren
    S.plus(spiegel_x(ell(4.8, 4, 0.4, 0.5, 0.5, 0.5)), "a")        # Ohrpflöcke
    S.rendern((-7, -1, -6), (7, 12, 6), versatz=(0.5, 0.01, 0.5))
    dschungelboden(w, _r(12 * u + 4))
    ranken(w, 0.06)
    moos_oben(w, 0.4)
    hohl(w, 2)
    return w


def jaguartempel(seed, g=2):
    """Jaguartempel: ein flacher Tempel auf einer Plattform mit zwei liegenden Jaguarstatuen an der Treppe
    und einem Dachkamm."""
    from weltwunder2 import _loewe
    w = _welt(seed)
    d = _ds(w, seed)
    u = U[g]
    a = _r(7 * u + 3, 5)
    dschungelboden(w, a + 10)
    for k in range(3):
        for x in range(-a - 3 + k, a + 4 - k):
            for z in range(-a - 3 + k, a + 4 - k):
                w.setze(x, 1 + k, z, d["S"](x, 1 + k, z, 0.3))
    st = P.Stil(w, wand=d["M"], sockel=d["S"], gesims=d["tr"], dach="moos", holz="jungle", laeden=False, blumen=0)
    P.gebaeude(w, st, -a, -a // 2, a, a // 2, y0=4, etagen=1, eh=5, dach="flach", tuer="south", gauben=False, kamine=0,
               sockel_h=0)
    for x in range(-a, a + 1):
        for y in range(10, 10 + _r(4 * u, 2)):
            if (x + y) % 2 == 0:
                w.setze(x, y, 0, d["M"](x, y, 0, 1))
    for sx in (-1, 1):
        S = Skulptur(w, 0.7 * u + 0.3)
        S.mat("k", sk(Mat(w, ["yellow_terracotta", "orange_terracotta", "black_terracotta"]) if _stil(seed) == 0 else
                      d["S"], 0, 8))
        S.mat("m", bl(w, "black_terracotta"))
        S.mat("a", bl(w, d["akz"]))
        S.mat("s", sk(d["S"], 0, 3))
        _loewe(w, S, 0, 0, 0, 1, "s")
        S.rendern((-4, -1, -10), (4, 9, 9), versatz=(sx * (a // 2 + 2) + 0.5, 4.01, a // 2 + 7))
    ranken(w, 0.04)
    hohl(w, 2)
    return w


def opferplatz(seed, g=1):
    """Opferplatz: runder Steinplatz mit Altar, Totempfählen aus Dschungelholz, Feuerschalen und Knochen."""
    w = _welt(seed)
    d = _ds(w, seed)
    u = U[g]
    R = _r(8 * u + 4)
    dschungelboden(w, R + 6)
    for x, z in scheibe(R):
        w.setze(x, 0, z, d["S"](x, 0, z, 0.3) if math.hypot(x, z) < R - 1 else w.b("mossy_stone_bricks"))
    for x in range(-2, 3):
        for z in range(-1, 2):
            w.setze(x, 1, z, d["M"](x, 1, z, 0.6))
    w.setze(0, 2, 0, w.b(d["gold"]))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * (R - 2)), round(math.sin(a) * (R - 2))
        for y in range(1, 6):
            w.setze(x, y, z, w.b(["stripped_jungle_log", "jungle_log", "carved_pumpkin" if False else "jungle_wood",
                                  "stripped_jungle_log", "jungle_log"][y - 1], axis="y"))
        w.setze(x, 6, z, MB.kohlenbecken(w))
    for k in range(5):
        w.setze(int(w.rng.integers(-R + 2, R - 2)), 1, int(w.rng.integers(-R + 2, R - 2)), w.b("bone_block", axis="x"))
    hohl(w, 2)
    return w


def mayaballspiel(seed, g=2):
    """Ballspielplatz: zwei geneigte Steintribünen mit Steinringen in der Mitte, Zuschauerterrassen und Pfeilern."""
    w = _welt(seed)
    d = _ds(w, seed)
    u = U[g]
    L, B = _r(14 * u + 6), _r(5 * u + 3, 4)
    dschungelboden(w, L + 6)
    for x in range(-L, L + 1):
        for z in range(-B, B + 1):
            w.setze(x, 0, z, w.b("smooth_sandstone") if _stil(seed) else w.b("stone_bricks"))
        for sz in (-1, 1):
            for k in range(5):
                z = sz * (B + 1 + k)
                for y in range(1, 2 + k):
                    w.setze(x, y, z, d["S"](x, y, z, y / 6))
                w.setze(x, 2 + k, z, treppe(w, d["tr"], "south" if sz > 0 else "north"))
    for sz in (-1, 1):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if abs(dx) + abs(dy) == 2 or (abs(dx) + abs(dy) == 1):
                    w.setze(dx, 6 + dy, sz * (B + 1), w.b(d["akz"]) if abs(dx) + abs(dy) == 1 else d["M"](0, 0, 0, 1))
    hohl(w, 2)
    return w


def dschungelpalast(seed, g=2):
    """Dschungelpalast: weitläufige Anlage auf mehreren Plattformen, Säulengänge mit Dachkämmen, Höfe mit
    Wasserbecken und Bananenstauden (Dschungelbäumchen)."""
    w = _welt(seed)
    d = _ds(w, seed)
    u = U[g]
    a = _r(12 * u + 5)
    dschungelboden(w, a + 6, 0.6)
    st = P.Stil(w, wand=d["M"], sockel=d["S"], gesims=d["tr"], dach="mcw_gruen", holz="jungle", laeden=False, blumen=0)
    for (x0, z0, x1, z1, y0) in ((-a, -a, -2, a // 3, 1), (2, -a, a, -2, 3), (2, 2, a, a, 1)):
        for y in range(1, y0 + 1):
            for x in range(x0 - 1, x1 + 2):
                for z in range(z0 - 1, z1 + 2):
                    w.setze(x, y, z, d["S"](x, y, z, 0.3))
        P.gebaeude(w, st, x0, z0, x1, z1, y0=y0 + 1, etagen=1, eh=5, dach="walm", tuer="south", gauben=False, kamine=0,
                   sockel_h=0)
    for x in range(-a, -1):
        for z in range(a // 3 + 2, a):
            w.setze(x, 0, z, w.b("water", level=0) if abs(x + a // 2) < a // 3 and abs(z - a * 2 // 3) < a // 4 else
                    w.b("mossy_stone_bricks"))
    ranken(w, 0.04)
    hohl(w, 2)
    return w


def haengebruecke(seed, g=2):
    """Hängebrücke über eine Schlucht: Seilbrücke (Macaw's) zwischen zwei Felsklippen mit Totempfählen."""
    w = _welt(seed)
    u = U[g]
    L = _r(14 * u + 6)
    H = _r(10 * u + 5)
    fels = Mat(w, ["stone", "mossy_cobblestone", "andesite", "moss_block", "cobblestone"], kontrast=1.3)
    for sx in (-1, 1):
        for x in range(sx * L, sx * (L + 10), sx):
            for z in range(-6, 7):
                for y in range(0, H + 1):
                    w.setze(x, y, z, fels(x, y, z, y / H))
                w.setze(x, H + 1, z, w.b("grass_block", snowy=False))
        for sz in (-2, 2):
            for y in range(H + 1, H + 5):
                w.setze(sx * (L + 1), y, sz, w.b("stripped_jungle_log", axis="y"))
    for x in range(-L + 1, L):
        sag = int(3 * math.cos(x / L * math.pi / 2))
        for z in (-1, 0, 1):
            w.setze(x, H + 1 - sag, z, MB.mod(w, "mcwbridges:rope_jungle_bridge", "jungle_slab",
                                              dict(type="bottom", waterlogged=False), facing="east", toggle=False,
                                              torch=False))
    for x in range(-L, L + 1):
        for z in range(-5, 6):
            w.setze(x, -1, z, w.b("water", level=0))
    hohl(w, 2)
    return w


def goldener_goetze(seed, g=1):
    """Schatzkammer mit goldenem Götzen: Raum aus Stein mit Druckplatten-Falle (dekorativ), Goldbarren-Haufen
    und einer Götzenstatue auf einem Sockel."""
    w = _welt(seed)
    d = _ds(w, seed)
    u = U[g]
    a = _r(5 * u + 3, 4)
    dschungelboden(w, a + 6)
    st = P.Stil(w, wand=d["M"], sockel=d["S"], gesims=d["tr"], dach="moos", holz="jungle", laeden=False, blumen=0)
    P.gebaeude(w, st, -a, -a, a, a, y0=1, etagen=1, eh=6, dach="flach", tuer="south", gauben=False, kamine=0)
    S = Skulptur(w, 0.5 * u + 0.4)
    S.mat("g", bl(w, "gold_block"))
    S.mat("a", bl(w, d["akz"]))
    S.plus(ell(0, 2, 0, 1.6, 2.2, 1.4), "g")
    S.plus(ell(0, 5, 0, 1.4, 1.4, 1.3), "g")
    S.plus(spiegel_x(ell(0.6, 5.3, 1.1, 0.3, 0.3, 0.2)), "a")
    S.rendern((-3, -1, -3), (3, 7, 3), versatz=(0.5, 3.01, -a + 2.5))
    for x in range(-1, 2):
        w.setze(x, 2, -a + 2, w.b("chiseled_stone_bricks"))
    for k in range(10):
        w.setze(int(w.rng.integers(-a + 1, a)), 2, int(w.rng.integers(-a + 1, a - 1)),
                w.b("raw_gold_block") if k % 2 else w.b("gold_block"))
    ranken(w, 0.05)
    hohl(w, 2)
    return w


def kanuanleger(seed, g=1):
    """Flussdorf-Anleger: Pfahlhütten mit Strohdächern (Macaw's Thatch) über einem Fluss, Kanus, Netze und Stege."""
    w = _welt(seed)
    u = U[g]
    L = _r(12 * u + 6)
    for x in range(-L, L + 1):
        for z in range(-3, 6):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("mud"))
    dschungelboden(w, L + 2, 0.4)
    st = P.Stil(w, wand="holz_hell", sockel=["jungle_planks"], gesims="jungle", dach="mcw_stroh", holz="jungle",
                laeden=False)
    for i in range(2 + g):
        x0 = -L + 2 + i * 8
        for dx in (0, 4):
            for dz in (0, 4):
                for y in range(-1, 3):
                    w.setze(x0 + dx, y, -1 + dz, w.b("jungle_log", axis="y"))
        for xx in range(x0 - 1, x0 + 6):
            for zz in range(-2, 5):
                w.setze(xx, 2, zz, w.b("jungle_planks"))
        P.gebaeude(w, st, x0, -1, x0 + 4, 3, y0=3, etagen=1, eh=3, dach="sattel", tuer="south", sockel_h=0,
                   gauben=False, kamine=0)
    for k in range(4):
        w.setze(k * 3 - 4, 1, 4, w.b("oak_boat") if False else w.b("jungle_slab", type="bottom", waterlogged=False))
    hohl(w, 2)
    return w


def obsidianaltar(seed, g=1):
    """Altar auf einem Felsen im Dschungel: schwarze Steinplatte, Kristallschalen, Jaguar-Fahnen."""
    w = _welt(seed)
    u = U[g]
    dschungelboden(w, _r(8 * u + 4))
    for x, z in scheibe(3 * u + 2):
        for y in range(1, 3):
            w.setze(x, y, z, w.b("mossy_cobblestone") if y == 1 else w.b("polished_blackstone"))
    w.setze(0, 3, 0, w.b("crying_obsidian"))
    w.setze(0, 4, 0, w.b("amethyst_cluster", facing="up", waterlogged=False))
    for sx in (-1, 1):
        for y in range(1, 5):
            w.setze(sx * 4, y, 0, w.b("stripped_jungle_log", axis="y"))
        w.setze(sx * 4, 5, 0, MB.fahne(w, "yellow", "east" if sx < 0 else "west"))
    return w


def mangrovenhuetten(seed, g=1):
    """Mangrovenhütten auf Stelzwurzeln im Sumpf, verbunden durch Bretterstege."""
    w = _welt(seed)
    u = U[g]
    R = _r(12 * u + 5)
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("water", level=0) if (x * 3 + z) % 5 else w.b("mud"))
        w.setze(x, -1, z, w.b("mud"))
    st = P.Stil(w, wand=["mangrove_planks", "stripped_mangrove_log", "mangrove_planks"], sockel=["mangrove_planks"],
                gesims="mangrove", dach="mcw_braun", holz="mangrove", laeden=True)
    pts = [(-5, -4), (5, -3), (0, 6)][:2 + (g > 0)]
    for (x, z) in pts:
        x, z = round(x * u), round(z * u)
        for xx, zz in scheibe(3.5, x, z):
            for y in range(0, 3):
                if (xx + zz + y) % 3 == 0:
                    w.setze(xx, y, zz, w.b("mangrove_roots", waterlogged=False))
            w.setze(xx, 3, zz, w.b("mangrove_planks"))
        P.gebaeude(w, st, x - 2, z - 2, x + 2, z + 2, y0=4, etagen=1, eh=3, dach="sattel", tuer="south", sockel_h=0,
                   gauben=False, kamine=0)
    for i in range(len(pts) - 1):
        (ax, az), (bx, bz) = pts[i], pts[i + 1]
        ax, az, bx, bz = round(ax * u), round(az * u), round(bx * u), round(bz * u)
        n = max(abs(bx - ax), abs(bz - az))
        for k in range(n + 1):
            w.setze(round(ax + (bx - ax) * k / n), 3, round(az + (bz - az) * k / n), w.b("mangrove_slab", type="top",
                                                                                         waterlogged=False))
    hohl(w, 2)
    return w


def tempelterrassen(seed, g=2):
    """Bewässerte Tempelterrassen: Stufenfelder am Hang mit Kanälen, kleine Schreine an jeder Stufe."""
    from fernost import reisterrassen
    w = reisterrassen(seed, g)
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) in ("minecraft:dark_oak_planks", "minecraft:stripped_dark_oak_log"):
            w.bloecke[(x, y, z)] = w.b("jungle_planks")
    ranken(w, 0.02)
    return w


def kristallhoehle_dschungel(seed, g=2):
    """Smaragdhöhle: Höhleneingang im Dschungelhügel, innen grüne Kristalle (Smaragd und Glas) und ein Teich."""
    from elemente import schatzhoehle
    w = _welt(seed)
    u = U[g]
    R = 10 * u + 4
    S = Skulptur(w, 1.0)
    fels = Mat(w, ["stone", "mossy_cobblestone", "andesite", "moss_block", "cobblestone"], kontrast=1.3)
    S.mat("f", lambda x, y, z, lx, ly, lz: fels(x, y, z, ly / R) if ly < R * 0.6 else w.b("moss_block"))
    S.plus(ell(0, 0, 0, R, R * 0.75, R), "f")
    S.minus(ell(0, 1, 0, R * 0.7, R * 0.5, R * 0.7))
    S.minus(ell(0, 1, R * 0.8, R * 0.35, R * 0.35, R * 0.4))
    S.rendern((-R - 1, 0, -R - 1), (R + 1, R, R + 1))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if w.frei(x, y - 1, z) and 2 < y and rng.random() < 0.05:
            w.setze(x, y - 1, z, w.b("emerald_block") if rng.random() < 0.3 else w.b("lime_stained_glass"))
    for x, z in scheibe(R * 0.3, 0, -2):
        w.setze(x, 0, z, w.b("water", level=0))
    dschungelboden(w, _r(R + 4))
    ranken(w, 0.05)
    hohl(w, 3)
    return w


def wachturm_dschungel(seed, g=1):
    """Dschungel-Wachturm: Holzturm auf Steinsockel, oben eine Plattform mit Strohdach und Trommel."""
    w = _welt(seed)
    u = U[g]
    H = _r(14 * u + 6)
    dschungelboden(w, _r(8 * u + 4))
    for y in range(1, H):
        for x, z in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            w.setze(x, y, z, w.b("jungle_log", axis="y") if y > 3 else w.b("mossy_cobblestone"))
        if y % 4 == 0:
            for x in range(-2, 3):
                for z in (-2, 2):
                    w.setze(x, y, z, w.b("stripped_jungle_log", axis="x"))
    for x in range(-3, 4):
        for z in range(-3, 4):
            w.setze(x, H, z, w.b("jungle_planks"))
    P.walmdach(w, P.Dach(w, "mcw_stroh"), -3, -3, 3, 3, H + 3, ue=1)
    for x, z in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        for y in range(H + 1, H + 3):
            w.setze(x, y, z, w.b("jungle_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(0, H + 1, 0, w.b("note_block", instrument="basedrum", note=0, powered=False))
    for y in range(1, H):
        w.setze(0, y, 3, w.b("ladder", facing="south", waterlogged=False))
    hohl(w, 2)
    return w


def dschungeldorf(seed, g=2):
    """Dschungeldorf: Rundhütten mit Strohdächern um einen Dorfplatz mit Feuer, Totems und Gemüsegärten."""
    import haeuser as H_
    w = _welt(seed)
    u = U[g]
    R = _r(12 * u + 6)
    dschungelboden(w, R + 4, 0.5)
    for x, z in scheibe(R * 0.35):
        w.setze(x, 0, z, w.b("coarse_dirt") if (x + z) % 3 else w.b("dirt_path"))
    w.setze(0, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    n = 3 + g * 2
    for i in range(n):
        a = i / n * 2 * math.pi
        cx, cz = round(math.cos(a) * R * 0.65), round(math.sin(a) * R * 0.65)
        r = 2.5 + (i % 2) * 0.6
        for y in range(1, 4):
            for x, z in kreisrand(r, cx, cz):
                w.setze(x, y, z, w.b("stripped_jungle_log", axis="y") if (x + z) % 3 == 0 else w.b("mud_bricks"))
        for k in range(int(r) + 3):
            for x, z in kreisrand(max(0.4, r + 1 - k), cx, cz):
                w.setze(x, 4 + k, z, MB.mod(w, "decorative_blocks:thatch", "hay_block", dict(axis="y")) if False else
                        w.b("hay_block", axis="y"))
        dx, dz = round(-math.cos(a) * r), round(-math.sin(a) * r)
        for y in (1, 2):
            w.bloecke.pop((cx + dx, y, cz + dz), None)
    H_.beet(w, R // 2, -R // 2, R // 2 + 4, -R // 2 + 3, "gemuese")
    hohl(w, 2)
    return w


def totemallee(seed, g=1):
    """Totem-Allee: zwei Reihen geschnitzter Totempfähle mit Tiergesichtern in Farbe, dazwischen ein Steinweg."""
    w = _welt(seed)
    u = U[g]
    n = 3 + g
    dschungelboden(w, n * 4 + 4, 0.6)
    farben = ["red_terracotta", "yellow_terracotta", "green_terracotta", "blue_terracotta", "white_terracotta"]
    for i in range(n):
        z = -n * 2 + i * 4
        for x in range(-1, 2):
            for zz in range(z - 1, z + 3):
                w.setze(x, 0, zz, w.b("mossy_cobblestone") if (x + zz) % 2 else w.b("cobblestone"))
        for sx in (-3, 3):
            H = _r((6 + (i % 3)) * u + 2)
            for y in range(1, H + 1):
                w.setze(sx, y, z, w.b(farben[(y // 2 + i) % len(farben)]) if y % 2 else w.b("stripped_jungle_log", axis="y"))
            w.setze(sx - 1, H - 1, z, w.b("jungle_trapdoor", facing="west", half="top", open=False, powered=False,
                                          waterlogged=False))
            w.setze(sx + 1, H - 1, z, w.b("jungle_trapdoor", facing="east", half="top", open=False, powered=False,
                                          waterlogged=False))
            w.setze(sx, H + 1, z, MB.kohlenbecken(w))
    return w


DSCHUNGEL = {
    "stufenpyramide": ("Stufenpyramide", stufenpyramide),
    "dschungelruine": ("Dschungelruine", dschungelruine),
    "baumhausdorf": ("Baumhausdorf", baumhausdorf),
    "schlangentor": ("Schlangentor", schlangentor),
    "wasserfallschrein": ("Wasserfallschrein", wasserfallschrein),
    "steinkopf": ("Steinkopf", steinkopf),
    "jaguartempel": ("Jaguartempel", jaguartempel),
    "opferplatz": ("Opferplatz", opferplatz),
    "ballspielplatz": ("Ballspielplatz", mayaballspiel),
    "dschungelpalast": ("Dschungelpalast", dschungelpalast),
    "haengebruecke": ("Hängebrücke", haengebruecke),
    "goldener_goetze": ("Goldener Götze", goldener_goetze),
    "kanuanleger": ("Flussdorf-Anleger", kanuanleger),
    "obsidianaltar": ("Kristallaltar", obsidianaltar),
    "mangrovenhuetten": ("Mangrovenhütten", mangrovenhuetten),
    "tempelterrassen": ("Tempelterrassen", tempelterrassen),
    "smaragdhoehle": ("Smaragdhöhle", kristallhoehle_dschungel),
    "dschungelwachturm": ("Dschungel-Wachturm", wachturm_dschungel),
    "dschungeldorf": ("Dschungeldorf", dschungeldorf),
    "totemallee": ("Totem-Allee", totemallee),
}


# ============================================================================ WIKINGER


def _wk(w, seed):
    if _stil(seed) == 0:
        return dict(holz="spruce", dach="mcw_stroh", wand=["stripped_spruce_log", "spruce_planks", "spruce_log",
                                                             "stripped_spruce_log"],
                    stein=Mat(w, ["cobblestone", "mossy_cobblestone", "stone", "andesite", "gravel"], kontrast=1.2),
                    schild=["red_wool", "white_wool"], gras="wiese")
    return dict(holz="dark_oak", dach="mcw_holz", wand=["stripped_dark_oak_log", "dark_oak_planks", "dark_oak_log"],
                stein=Mat(w, ["cobbled_deepslate", "cobblestone", "tuff", "stone", "andesite"], kontrast=1.2),
                schild=["blue_wool", "yellow_wool"], gras="wald")


def langhaus_bau(w, d, x0, z0, x1, z1, H=4, tuer="south"):
    """Langhaus: niedrige Wände aus Stämmen, tief herabgezogenes Dach, gekreuzte Drachenköpfe an den Giebeln."""
    st = P.Stil(w, wand=d["wand"], sockel=d["stein"], gesims="cobblestone", dach=d["dach"], holz=d["holz"],
                laeden=False, blumen=0)
    top = P.gebaeude(w, st, x0, z0, x1, z1, y0=1, etagen=1, eh=H, dach="sattel", ue=2, steil=True, tuer=tuer,
                     first_x=(x1 - x0) >= (z1 - z0), gauben=False, kamine=0)
    fx = (x1 - x0) >= (z1 - z0)
    if fx:
        for xe, sgn in ((x0 - 3, -1), (x1 + 3, 1)):
            for k in range(3):
                w.setze(xe + sgn * k // 2, top - 1 + k, (z0 + z1) // 2 + (1 if k % 2 else -1),
                        w.b(f"{d['holz']}_log", axis="y"))
    w.setze((x0 + x1) // 2, top + 1, (z0 + z1) // 2, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                           waterlogged=False))
    return top


def langhaus(seed, g=1):
    """Langhaus: langgestreckte Halle mit Stroh- oder Holzschindeldach, Drachenköpfen, Schilden an der Wand,
    Feuerstelle, Holzstapel und Pferch."""
    import haeuser as H_
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    L, B = _r(8 * u + 4, 6), _r(3 * u + 2, 3)
    gelaende(w, L + 8, art=d["gras"])
    langhaus_bau(w, d, -L, -B, L, B, H=4)
    for x in range(-L + 2, L - 1, 3):
        w.setze(x, 3, B + 1, w.b(d["schild"][x % 2]))
    H_.holzstapel(w, L + 3, -B, 4, d["holz"], "z")
    for x in range(-L, -L + 6):
        for z in (B + 4, B + 9):
            w.setze(x, 1, z, MB.palisade(w, d["holz"], east=True, west=True))
    hohl(w, 2)
    return w


def stabkirche(seed, g=1):
    """Stabkirche: gestaffelte Dächer mit Schindeln, Drachenköpfe an den Giebeln, Laubengang und Dachreiter."""
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    a = _r(3 * u + 2, 3)
    gelaende(w, a + 10, art=d["gras"])
    st = P.Stil(w, wand=d["wand"], sockel=d["stein"], gesims=d["holz"], dach="mcw_holz", holz=d["holz"], laeden=False,
                blumen=0)
    y = 1
    for s, (h, eh) in enumerate(((a + 2, 3), (a, 4), (a - 1, 4))):
        top = P.gebaeude(w, st, -h, -h, h, h, y0=y, etagen=1, eh=eh, dach="sattel", ue=1, steil=True, tuer="south",
                         gauben=False, kamine=0, sockel_h=1 if s == 0 else 0)
        y += eh + (2 if s == 0 else 1)
    P.turm(w, st, 0, 0, top - 2, _r(5 * u + 3), 1.2, form="eckig", dach="nadel", krone=False, fahne=None)
    for sx in (-1, 1):
        w.setze(sx * (a + 3), top - 2, 0, w.b(f"{d['holz']}_log", axis="y"))
    hohl(w, 2)
    return w


def runenstein(seed, g=0):
    """Runensteine: ein Kreis aus behauenen Steinen mit eingeritzten Runen (Chipped/Akzent) um eine Feuerstelle."""
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    R = 5 * u + 3
    gelaende(w, _r(R + 5), art=d["gras"])
    for i in range(7):
        a = i / 7 * 2 * math.pi
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        h = _r((3 + i % 3) * u + 2)
        for y in range(1, h + 1):
            for dx in (0, 1):
                w.setze(x + dx, y, z, MB.mod(w, "chipped:carved_stone_bricks" if (y + i) % 2 else "chipped:engraved_stone_bricks",
                                             "chiseled_stone_bricks") if y == h // 2 + 1 else d["stein"](x, y, z, y / h))
    w.setze(0, 1, 0, MB.kohlenbecken(w))
    return w


def schiffssetzung(seed, g=1):
    """Schiffssetzung: Grabmal aus Steinen in Form eines Schiffs, mit höheren Steinen an Bug und Heck."""
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    L = 12 * u + 5
    gelaende(w, _r(L + 4), art=d["gras"])
    for i in range(int(L * 1.2)):
        t = i / (L * 1.2) * 2 * math.pi
        x = round(math.cos(t) * L)
        z = round(math.sin(t) * L * 0.3)
        h = _r(2 * u + 1, 2) if abs(math.cos(t)) < 0.95 else _r(5 * u + 3)
        for y in range(1, h + 1):
            w.setze(x, y, z, d["stein"](x, y, z, y / h))
    return w


def methalle(seed, g=2):
    """Methalle des Jarls: große Halle mit geschnitzten Säulen, Feuerrinne, Hochsitz, Fellen und Trinkhörnern."""
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    L, B = _r(12 * u + 5), _r(5 * u + 3, 4)
    gelaende(w, L + 8, art=d["gras"])
    langhaus_bau(w, d, -L, -B, L, B, H=_r(4 * u + 2, 4))
    for x in range(-L + 3, L - 2):
        w.setze(x, 0, 0, w.b("magma_block") if x % 4 == 0 else w.b("cobblestone"))
    for x in range(-L + 2, L - 1, 4):
        for sz in (-B + 2, B - 2):
            for y in range(1, _r(4 * u + 2, 4) + 1):
                w.setze(x, y, sz, w.b(f"stripped_{d['holz']}_log", axis="y"))
    for x in (L - 2,):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b(f"{d['holz']}_stairs", facing="east", half="bottom", shape="straight", waterlogged=False))
    for i in range(6):
        w.setze(-L + 3 + i * 3, 1, B - 1, MB.teppich(w, "brown"))
    hohl(w, 2)
    return w


def palisadendorf(seed, g=2):
    """Palisadendorf: Ring aus angespitzten Palisaden (Decorative Blocks) mit Tor, darin Langhäuser, Grubenhäuser,
    Brunnen, Räuchergestelle und ein Wachturm."""
    import haeuser as H_
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R + 4, art=d["gras"])
    pts = kreisrand(R)
    menge = set(pts)
    for (x, z) in pts:
        if abs(x) <= 1 and z > 0:
            continue
        for y in range(1, 4):
            w.setze(x, y, z, MB.palisade(w, d["holz"], north=(x, z - 1) in menge, south=(x, z + 1) in menge,
                                         east=(x + 1, z) in menge, west=(x - 1, z) in menge))
    for (x0, z0, x1, z1) in ((-R // 2, -R // 2, R // 6, -R // 2 + 6), (R // 6 + 3, -R // 3, R // 2 + 2, R // 6)):
        langhaus_bau(w, d, x0, z0, x1, z1, H=4)
    for y in range(1, 9):
        for x, z in ((-R + 3, -2), (-R + 6, -2), (-R + 3, 1), (-R + 6, 1)):
            w.setze(x, y, z, w.b(f"{d['holz']}_log", axis="y"))
    for x in range(-R + 3, -R + 7):
        for z in range(-2, 2):
            w.setze(x, 9, z, w.b(f"{d['holz']}_planks"))
    H_.holzstapel(w, R // 3, R // 3, 4, d["holz"], "x")
    from burgen import brunnen, Burgstil, POOL
    hohl(w, 2)
    return w


def drachenschiff(seed, g=2):
    """Drachenboot am Ufer: Klinkerrumpf mit geschwungenem Drachenkopf, rot-weißes Rahsegel, Schilde an der Reling."""
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    L = 12 * u + 4
    B = 2.5 * u + 1
    S = Skulptur(w, 1.0)
    S.mat("h", lambda x, y, z, *a: w.b(f"{d['holz']}_planks") if y % 2 else w.b(f"stripped_{d['holz']}_log", axis="x"))
    S.mat("k", bl(w, f"{d['holz']}_log"))
    S.plus(ohne(ell(0, 2.5 * u, 0, L, 2.5 * u, B), lambda X, Y, Z: Y > 2.5 * u + 0.5), "h")
    S.minus(ell(0, 2.5 * u + 1, 0, L - 1, 2.2 * u, B - 1))
    for sx in (-1, 1):
        S.plus(kap((sx * (L - 0.5), 2.5 * u, 0), (sx * (L + 1.5), 5.5 * u, 0), 0.7, 0.5), "k")
        S.plus(kap((sx * (L + 1.5), 5.5 * u, 0), (sx * (L + 0.5), 7 * u, 0), 0.6, 0.4), "k")
    S.rendern((-L - 3, -1, -B - 1), (L + 3, 8 * u, B + 1), versatz=(0.5, 0.01, 0.5))
    for y in range(1, _r(10 * u + 4)):
        w.setze(0, y, 0, w.b(f"{d['holz']}_log", axis="y"))
    hs = _r(5 * u + 2, 3)
    for x in range(-hs, hs + 1):
        for y in range(_r(4 * u + 2), _r(9 * u + 3)):
            w.setze(x, y, 1, w.b(d["schild"][(x // 2 + y // 2) % 2]))
    for x in range(-int(L) + 3, int(L) - 2, 2):
        for sz in (-1, 1):
            w.setze(x, round(2.5 * u + 0.5), sz * round(B), w.b(d["schild"][x % 2]))
    for x in range(-int(L) - 6, int(L) + 7):
        for z in range(-int(B) - 4, int(B) + 5):
            if not w.bloecke.get((x, 0, z)):
                w.setze(x, 0, z, w.b("sand") if z < 2 else w.b("water", level=0))
    hohl(w, 2)
    return w


def grubenhaus(seed, g=0):
    """Grubenhaus: halb in die Erde gesenktes Haus mit Grassodendach, Rauchloch und Webstuhl."""
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    a, b = _r(3 * u + 2, 3), _r(2 * u + 2, 2)
    gelaende(w, a + 6, art=d["gras"])
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            for y in range(-1, 1):
                w.bloecke.pop((x, y, z), None)
            w.setze(x, -2, z, w.b("coarse_dirt"))
    for x in range(-a - 1, a + 2):
        for z in range(-b - 1, b + 2):
            rnd = x in (-a - 1, a + 1) or z in (-b - 1, b + 1)
            if rnd:
                for y in range(-1, 2):
                    w.setze(x, y, z, w.b(f"{d['holz']}_planks") if y < 1 else w.b(f"stripped_{d['holz']}_log", axis="y"))
    k = 0
    while b + 2 - k >= 0:
        for x in range(-a - 2, a + 3):
            for z in (-b - 2 + k, b + 2 - k):
                w.setze(x, 2 + k, z, w.b("grass_block", snowy=False) if k % 2 == 0 else w.b("moss_block"))
        k += 1
    w.setze(0, 2 + k, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    w.setze(-a, -1, 0, w.b("loom", facing="east"))
    return w


def wikinger_hafen(seed, g=2):
    """Wikingerhafen: Holzstege ins Wasser, zwei Drachenboote, Bootshaus mit Strohdach, Fischgestelle."""
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    L = _r(16 * u + 6)
    for x in range(-L, L + 1):
        for z in range(0, L):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("gravel"))
    gelaende(w, L, art=d["gras"])
    for (x0, n) in ((-L // 2, L // 2), (L // 3, L // 2)):
        for z in range(0, n):
            for x in (x0, x0 + 1, x0 + 2):
                w.setze(x, 1, z, w.b(f"{d['holz']}_planks"))
            if z % 3 == 0:
                w.setze(x0 - 1, 0, z, w.b(f"{d['holz']}_log", axis="y"))
                w.setze(x0 + 3, 0, z, w.b(f"{d['holz']}_log", axis="y"))
    langhaus_bau(w, d, -L // 2 - 3, -9, -L // 2 + 6, -3, H=4)
    for x in range(L // 3, L // 3 + 6):
        for y in (1, 2, 3):
            if x % 2 == 0:
                w.setze(x, y, -4, w.b(f"{d['holz']}_fence", north=False, south=False, east=False, west=False,
                                      waterlogged=False))
        w.setze(x, 3, -4, w.b(f"{d['holz']}_fence", north=False, south=False, east=True, west=True, waterlogged=False))
        w.setze(x, 2, -4, w.b("cod") if False else w.b("dried_kelp_block")) if x % 2 else None
    hohl(w, 2)
    return w


def schmiede_nord(seed, g=1):
    """Nordische Schmiede: offener Schuppen mit Esse, Amboss, Wasserbottich und Waffenständer mit Schilden."""
    from haeuser import schmiede
    w = schmiede(seed, g)
    return w


def runenportal(seed, g=1):
    """Runenportal: Steintor mit Runenband zwischen zwei Monolithen, davor eine Feuerschale – ein Tor zu den
    Neun Welten."""
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    H = _r(9 * u + 4)
    gelaende(w, _r(10 * u + 4), art=d["gras"])
    for sx in (-1, 1):
        for y in range(1, H + 1):
            for dx in (0, 1):
                for dz in (0, 1):
                    w.setze(sx * 3 + dx - (1 if sx < 0 else 0), y, dz, d["stein"](sx, y, dz, y / H))
    for x in range(-4, 5):
        for dz in (0, 1):
            w.setze(x, H + 1, dz, d["stein"](x, H + 1, dz, 1))
    for y in range(2, H, 2):
        for sx in (-4, 3):
            w.setze(sx, y, 2, MB.mod(w, "chipped:runic_stone_bricks", "chiseled_stone_bricks"))
    for x in range(-2, 3):
        for y in range(1, H + 1):
            w.setze(x, y, 1, w.b("light_blue_stained_glass") if (x + y) % 2 else w.b("blue_stained_glass"))
    w.setze(0, 1, 5, MB.kohlenbecken(w))
    return w


def thingplatz(seed, g=1):
    """Thingplatz: Versammlungsplatz mit Steinbänken im Kreis, einem Rednerstein und Fackelpfählen."""
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    R = 7 * u + 4
    gelaende(w, _r(R + 5), art=d["gras"])
    for ring in (R, R - 2):
        for x, z in kreisrand(ring):
            if (x + z) % 3:
                w.setze(x, 1, z, w.b("cobblestone_slab", type="bottom", waterlogged=False))
    for y in range(1, 3):
        w.setze(0, y, 0, d["stein"](0, y, 0, 0.5))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * (R + 2)), round(math.sin(a) * (R + 2))
        for y in range(1, 4):
            w.setze(x, y, z, w.b(f"{d['holz']}_fence", north=False, south=False, east=False, west=False, waterlogged=False))
        w.setze(x, 4, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


def jarlhof(seed, g=2):
    """Jarlhof: Langhaus mit Nebengebäuden, Stall, Vorratshaus auf Stelzen, Zaun und Felder."""
    import haeuser as H_
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R + 4, art=d["gras"])
    langhaus_bau(w, d, -R // 2, -4, R // 2, 4, H=4)
    langhaus_bau(w, d, -R // 2, 8, -R // 2 + 8, 12, H=3)
    for x in (R // 2 - 4, R // 2):
        for z in (8, 12):
            for y in range(1, 3):
                w.setze(x, y, z, w.b(f"{d['holz']}_log", axis="y"))
    langhaus_bau(w, d, R // 2 - 4, 8, R // 2, 12, H=3)
    H_.beet(w, -R // 2, -R // 2 - 2, R // 2, -6, "gemuese")
    hohl(w, 2)
    return w


def wikingerwachturm(seed, g=1):
    """Holzwachturm mit Schildwand oben, Hornbläser-Plattform und Signalfeuer."""
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    H = _r(12 * u + 6)
    gelaende(w, _r(7 * u + 4), art=d["gras"])
    for y in range(1, H):
        for x, z in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            w.setze(x, y, z, w.b(f"{d['holz']}_log", axis="y"))
        if y % 4 == 0:
            for x in range(-2, 3):
                for z in (-2, 2):
                    w.setze(x, y, z, w.b(f"stripped_{d['holz']}_log", axis="x"))
    for x in range(-3, 4):
        for z in range(-3, 4):
            w.setze(x, H, z, w.b(f"{d['holz']}_planks"))
            if max(abs(x), abs(z)) == 3:
                w.setze(x, H + 1, z, w.b(d["schild"][(x + z) % 2]))
    w.setze(0, H + 1, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    for y in range(1, H):
        w.setze(0, y, 3, w.b("ladder", facing="south", waterlogged=False))
    hohl(w, 2)
    return w


def grabhuegel(seed, g=1):
    """Königsgrabhügel: grasbewachsener Hügel mit steinernem Eingang, Gang und Grabkammer mit Schätzen."""
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    R = 10 * u + 4
    for x, z in scheibe(R):
        hh = int(R * 0.5 * (1 - (math.hypot(x, z) / R) ** 2))
        for y in range(0, hh + 1):
            w.setze(x, y, z, w.b("grass_block", snowy=False) if y == hh else w.b("dirt"))
    for z in range(0, int(R) + 1):
        for x in (-1, 0, 1):
            for y in (1, 2):
                w.bloecke.pop((x, y, z), None)
        for x in (-2, 2):
            for y in (1, 2):
                w.setze(x, y, z, d["stein"](x, y, z, 0.5))
        for x in range(-2, 3):
            w.setze(x, 3, z, d["stein"](x, 3, z, 0.8))
    for x in range(-2, 3):
        for z in range(-2, 3):
            for y in (1, 2):
                w.bloecke.pop((x, y, z), None)
    w.setze(0, 1, -1, w.b("chest", facing="south", type="single", waterlogged=False))
    w.setze(1, 1, -1, w.b("gold_block"))
    return w


def goettervater(seed, g=2):
    """Statue des einäugigen Göttervaters mit Speer, Umhang und zwei Raben auf den Schultern."""
    from motive import figur
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    S = Skulptur(w, 1.5 * u + 0.4)
    S.mat("k", sk(d["stein"], 0, 30 * u))
    S.mat("a", bl(w, "gold_block"))
    S.mat("d", bl(w, "polished_blackstone"))
    S.mat("g", bl(w, "sea_lantern"))
    S.mat("r", bl(w, "black_concrete"))
    kopf = figur(S, "zwerg" if False else "mensch", "stab", y0=2)
    S.plus(kap((0, kopf - 2.4, 1.2), (0, kopf - 6, 1.9), 1.5, 0.7), "k")
    S.plus(spiegel_x(ell(3.0, kopf - 3.2, -0.2, 0.7, 0.8, 1.1)), "r")
    S.plus(lambda X, Y, Z: (Y > 3) & (Y < kopf - 3) & (Z < -1.2) & (Z > -2.2) & (np.abs(X) < 3.0 + (kopf - 3 - Y) * 0.1), "d")
    S.plus(kap((-1.1, kopf - 1.2, 1.4), (1.1, kopf - 1.2, 1.4), 0.25), "d")
    S.rendern((-8, -1, -6), (8, kopf + 4, 6), versatz=(0.5, 0.01, 0.5))
    for x, z in scheibe(4 * u + 2):
        for y in (0, 1):
            w.setze(x, y, z, d["stein"](x, y, z, 0.3))
    gelaende(w, _r(10 * u + 4), art=d["gras"])
    hohl(w, 2)
    return w


def weltenesche(seed, g=2):
    """Weltenesche: gewaltiger Baum mit drei Wurzeln, an deren Fuß ein Brunnen, Runensteine und Opfergaben."""
    from weltwunder import weltenbaum
    w = weltenbaum(seed, max(1, g - 1))
    w.setze(0, 1, 9, MB.kohlenbecken(w))
    return w


def raeucherhuette(seed, g=0):
    """Räucherhütte: kleine Hütte mit Rauch, Fischgestellen, Fässern und gesalzenem Fleisch (Netherwarzen)."""
    w = _welt(seed)
    d = _wk(w, seed)
    gelaende(w, 8, art=d["gras"])
    langhaus_bau(w, d, -2, -2, 2, 2, H=3)
    for x in range(3, 7):
        for y in (1, 2, 3):
            if x in (3, 6):
                w.setze(x, y, 0, w.b(f"{d['holz']}_fence", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
        w.setze(x, 3, 0, w.b(f"{d['holz']}_fence", north=False, south=False, east=True, west=True, waterlogged=False))
        if x in (4, 5):
            w.setze(x, 2, 0, w.b("dried_kelp_block"))
    for k in range(2):
        w.setze(-4, 1 + k, 1, w.b("barrel", facing="up", open=False))
    return w


def bootsschuppen(seed, g=1):
    """Bootsschuppen: offene Halle am Wasser mit Rampe, darin ein Boot auf Böcken, Ruder und Netze."""
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    L, B = _r(6 * u + 4, 5), _r(3 * u + 2, 3)
    for x in range(-L - 2, L + 3):
        for z in range(B + 2, B + 10):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("gravel"))
    gelaende(w, L + 4, art=d["gras"])
    for x in (-L, L):
        for z in range(-B, B + 2, 2):
            for y in range(1, 4):
                w.setze(x, y, z, w.b(f"{d['holz']}_log", axis="y"))
    P.satteldach(w, P.Dach(w, d["dach"]), -L, -B, L, B + 1, 4, ue=1, first_x=False, steil=True)
    for z in range(-B + 1, B + 6):
        w.setze(0, 0 if z <= B else 0, z, w.b(f"{d['holz']}_planks"))
    for x in range(-L + 2, L - 1):
        w.setze(x, 2, 0, w.b(f"{d['holz']}_slab", type="bottom", waterlogged=False))
    hohl(w, 2)
    return w


def schildwalltor(seed, g=1):
    """Schildwall-Tor: Palisadentor mit zwei Wachtürmen aus Stämmen, oben eine Reihe bemalter Schilde."""
    w = _welt(seed)
    d = _wk(w, seed)
    u = U[g]
    hb = 3
    H = _r(7 * u + 4, 6)
    L = _r(10 * u + 6)
    gelaende(w, L + 4, art=d["gras"])
    for x in range(-L, L + 1):
        if abs(x) > hb + 2:
            for y in range(1, 5):
                w.setze(x, y, 0, MB.palisade(w, d["holz"], east=True, west=True))
    for sx in (-1, 1):
        for y in range(1, H):
            for dx in (0, 1, 2):
                for dz in (-1, 0, 1):
                    if dx in (0, 2) or dz != 0:
                        w.setze(sx * (hb + dx), y, dz, w.b(f"{d['holz']}_log", axis="y"))
        for dx in range(-1, 4):
            for dz in range(-2, 3):
                w.setze(sx * (hb + dx), H, dz, w.b(f"{d['holz']}_planks"))
        for dx in range(-1, 4):
            w.setze(sx * (hb + dx), H + 1, 2, w.b(d["schild"][(dx) % 2]))
    for x in range(-hb - 1, hb + 2):
        w.setze(x, H, 0, w.b(f"stripped_{d['holz']}_log", axis="x"))
        w.setze(x, H + 1, 1, w.b(d["schild"][x % 2]))
    return w


def seherhuette(seed, g=0):
    """Hütte der Seherin: runde Hütte mit Torfdach, Knochenzaun, Kessel und Kräuterbündeln."""
    w = _welt(seed)
    d = _wk(w, seed)
    gelaende(w, 8, art=d["gras"])
    for y in range(1, 4):
        for x, z in kreisrand(3):
            w.setze(x, y, z, w.b(f"stripped_{d['holz']}_log", axis="y") if (x + z) % 2 else w.b("mud_bricks"))
    for k in range(5):
        for x, z in kreisrand(max(0.4, 4 - k)):
            w.setze(x, 4 + k, z, w.b("moss_block") if (x + z + k) % 3 else w.b("grass_block", snowy=False))
    w.bloecke.pop((0, 1, 3), None)
    w.bloecke.pop((0, 2, 3), None)
    w.setze(0, 1, 0, w.b("water_cauldron", level=3))
    for x, z in kreisrand(5.5):
        if (x + z) % 2 == 0:
            w.setze(x, 1, z, w.b("bone_block", axis="y"))
    return w


WIKINGER = {
    "langhaus": ("Langhaus", langhaus),
    "stabkirche": ("Stabkirche", stabkirche),
    "runenstein": ("Runenstein-Kreis", runenstein),
    "schiffssetzung": ("Schiffssetzung", schiffssetzung),
    "thronhalle": ("Methalle", methalle),
    "palisadendorf": ("Palisadendorf", palisadendorf),
    "drachenschiff": ("Drachenboot am Ufer", drachenschiff),
    "grubenhaus": ("Grubenhaus", grubenhaus),
    "wikingerhafen": ("Wikingerhafen", wikinger_hafen),
    "runenportal": ("Runenportal", runenportal),
    "thingplatz": ("Thingplatz", thingplatz),
    "jarlhof": ("Jarlhof", jarlhof),
    "wikingerwachturm": ("Holzwachturm", wikingerwachturm),
    "grabhuegel": ("Königsgrabhügel", grabhuegel),
    "goettervater": ("Göttervater-Statue", goettervater),
    "weltenesche": ("Weltenesche", weltenesche),
    "raeucherhuette": ("Räucherhütte", raeucherhuette),
    "bootsschuppen": ("Bootsschuppen", bootsschuppen),
    "schildwalltor": ("Schildwall-Tor", schildwalltor),
    "seherhuette": ("Hütte der Seherin", seherhuette),
}


# ============================================================================ MARKT


def _mk(w, seed):
    if _stil(seed) == 0:
        return dict(farben=["red", "white"], holz="spruce", haus="fachwerk_rot", pflaster=("cobblestone", "basket_weave_paving"))
    return dict(farben=["blue", "yellow"], holz="dark_oak", haus="fachwerk_ocker", pflaster=("stone", "running_bond"))


def marktboden(w, R, d, cx=0, cz=0):
    rng = w.rng
    for x, z in scheibe(R, cx, cz):
        v = rng.random()
        w.setze(x, 0, z, MB.pflaster(w, *d["pflaster"]) if v < 0.5 else w.b("cobblestone") if v < 0.75 else
                w.b("stone_bricks") if v < 0.9 else w.b("gravel"))


def stand(w, d, x0, z0, breite=4, tiefe=3, farbe=None, facing="south"):
    """Marktstand: vier Pfosten, gestreifte Markise (Macaw's Awning), Tresen mit Waren."""
    rng = w.rng
    farbe = farbe or d["farben"][int(rng.integers(2))]
    for x in (x0, x0 + breite):
        for z in (z0, z0 + tiefe):
            for y in range(1, 4):
                w.setze(x, y, z, w.b(f"{d['holz']}_fence", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
    for x in range(x0, x0 + breite + 1):
        for z in range(z0, z0 + tiefe + 1):
            w.setze(x, 4, z, MB.markise(w, farbe, "north" if z < z0 + tiefe / 2 else "south"))
    for x in range(x0 + 1, x0 + breite):
        w.setze(x, 1, z0 + tiefe, w.b(f"{d['holz']}_planks") if False else w.b("barrel", facing="up", open=True))
        w.setze(x, 1, z0 + 1, MB.ware(w, rng))
        if rng.random() < 0.5:
            w.setze(x, 2, z0 + 1, MB.ware(w, rng))


def marktstaende(seed, g=1):
    """Marktstände: Reihe von Ständen mit gestreiften Markisen, Kisten voller Gemüse, Säcke, Körbe und Fässer."""
    w = _welt(seed)
    d = _mk(w, seed)
    u = U[g]
    n = 2 + g
    gelaende(w, n * 6 + 4, art="wiese")
    marktboden(w, n * 6 + 2, d)
    for sx in (-1, 1):
        for i in range(n):
            stand(w, d, -n * 3 + i * 6, sx * 5 - (3 if sx < 0 else 0), 4, 3, d["farben"][(i + (sx > 0)) % 2])
    hohl(w, 2)
    return w


def marktbrunnen(seed, g=1):
    """Marktbrunnen: achteckiger Brunnen mit Säule und Figur, Bänke und Laternen rundherum."""
    from weltwunder4 import himmelsbrunnen
    w = himmelsbrunnen(seed, max(0, g - 1))
    return w


def gauklerzelt(seed, g=1):
    """Gauklerzelt: großes rundes Zirkuszelt in Streifen, Fahnen, Wagen der Gaukler, Bühne und Laternenkette."""
    from wueste_eis import zelt
    w = _welt(seed)
    d = _mk(w, seed)
    u = U[g]
    R = 6 * u + 4
    gelaende(w, _r(R + 8), art="wiese")
    zelt(w, 0, 0, R, _r(R * 1.3), [f"{d['farben'][0]}_wool", "white_wool", f"{d['farben'][1]}_wool", "white_wool"])
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * (R + 3)), round(math.sin(a) * (R + 3))
        for y in range(1, 5):
            w.setze(x, y, z, w.b(f"{d['holz']}_fence", north=False, south=False, east=False, west=False, waterlogged=False))
        w.setze(x, 5, z, MB.fahne(w, d["farben"][i % 2], "east"))
    for x in range(-3, 4):
        for z in range(int(R) + 4, int(R) + 7):
            w.setze(x, 1, z, w.b(f"{d['holz']}_planks"))
    hohl(w, 2)
    return w


def turnierplatz(seed, g=2):
    """Turnierplatz: Tjostbahn mit Holzschranke, überdachte Tribüne für den Adel, Ritterzelte und Wappenfahnen."""
    from wueste_eis import zelt
    w = _welt(seed)
    d = _mk(w, seed)
    u = U[g]
    L = _r(16 * u + 6)
    gelaende(w, L + 6, art="wiese")
    for x in range(-L, L + 1):
        w.setze(x, 0, 0, w.b("dirt_path"))
        w.setze(x, 0, 2, w.b("dirt_path"))
        w.setze(x, 0, -2, w.b("dirt_path"))
        w.setze(x, 1, 0, w.b(f"{d['holz']}_fence", north=False, south=False, east=True, west=True, waterlogged=False))
    for x in range(-L // 2, L // 2 + 1):
        for k in range(3):
            w.setze(x, 1 + k, 5 + k, w.b(f"{d['holz']}_stairs", facing="north", half="bottom", shape="straight",
                                         waterlogged=False))
        w.setze(x, 6, 7, MB.markise(w, d["farben"][x % 2], "north"))
        w.setze(x, 6, 6, MB.markise(w, d["farben"][x % 2], "north"))
        if x % 4 == 0:
            for y in range(1, 6):
                w.setze(x, y, 8, w.b(f"{d['holz']}_log", axis="y"))
    for i, sx in enumerate((-1, 1)):
        zelt(w, sx * (L - 3), -6, 2.5, 4, [f"{d['farben'][i]}_wool", "white_wool"])
    hohl(w, 2)
    return w


def ladenzeile(seed, g=2):
    """Ladenzeile: Fachwerkhäuser mit Läden im Erdgeschoss, Markisen, Auslagen, Schildern und Pflasterstraße."""
    import haeuser as H_
    w = _welt(seed)
    d = _mk(w, seed)
    u = U[g]
    n = 3 + g
    gb = 6
    gelaende(w, n * (gb + 1) // 2 + 6, art="wiese")
    pool = ["fachwerk_rot", "fachwerk_ocker", "backstein", "putz_blau", "kalk_kupfer"]
    x = -n * (gb + 1) // 2
    for i in range(n):
        dd = dict(H_.HAUSPOOL[pool[(i + _stil(seed)) % len(pool)]])
        dd["dach"] = ["mcw_ziegel", "mcw_schiefer", "schindel_rot", "mcw_braun", "schindel_blau"][(i * 3 + _stil(seed)) % 5]
        st = P.Stil(w, **dd)
        P.gebaeude(w, st, x, -4, x + gb - 1, 2, y0=1, etagen=2 + (i % 2), eh=4, dach="sattel", first_x=False,
                   steil=i % 2 == 0, tuer="south", gauben=False)
        for xx in range(x, x + gb):
            w.setze(xx, 4, 3, MB.markise(w, d["farben"][(i + xx) % 2], "south"))
        w.setze(x + 1, 1, 3, MB.ware(w, w.rng))
        w.setze(x + gb - 2, 1, 3, MB.korb(w))
        x += gb + 1
    for xx in range(-n * (gb + 1) // 2 - 2, n * (gb + 1) // 2 + 2):
        for z in range(4, 8):
            w.setze(xx, 0, z, MB.pflaster(w, *d["pflaster"]) if (xx + z) % 2 else w.b("cobblestone"))
    hohl(w, 2)
    return w


def marktplatz(seed, g=2):
    """Großer Marktplatz: gepflasterter Platz mit Brunnen in der Mitte, Ständen im Kreis, Pranger, Maibaum
    und umliegenden Fachwerkfassaden."""
    import haeuser as H_
    w = _welt(seed)
    d = _mk(w, seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R + 4, art="wiese")
    marktboden(w, R, d)
    w.setze(0, 0, 0, w.b("water", level=0))
    for x, z in kreisrand(2):
        w.setze(x, 1, z, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    n = 4 + g * 2
    for i in range(n):
        a = i / n * 2 * math.pi
        cx, cz = round(math.cos(a) * R * 0.6) - 2, round(math.sin(a) * R * 0.6) - 1
        stand(w, d, cx, cz, 3, 2, d["farben"][i % 2])
    for y in range(1, _r(10 * u + 6)):
        w.setze(R // 2, y, -R // 2, w.b("stripped_birch_log", axis="y"))
    for k in range(4):
        w.setze(R // 2, _r(10 * u + 6) - 2 - k, -R // 2 + 1, w.b(["red_wool", "yellow_wool", "blue_wool", "green_wool"][k]))
    hohl(w, 2)
    return w


def gasthaus(seed, g=1):
    """Gasthaus zum Marktplatz: großes Wirtshaus mit Biergarten, Fässern, Tischen, Lampions und Zunftschild."""
    from haeuser import taverne
    w = taverne(seed, g)
    for x in range(-6, 7, 3):
        w.setze(x, 5, 10, MB.laterne(w, "festive_lantern", haengend=True))
    return w


def kraeuterstand(seed, g=0):
    """Kräuterstand der Heilerin: Stand mit getrockneten Kräutern, Blumentöpfen, Tränken und Körben."""
    w = _welt(seed)
    d = _mk(w, seed)
    gelaende(w, 7, art="wiese")
    marktboden(w, 5, d)
    stand(w, d, -2, -1, 4, 3, "green")
    for x in range(-1, 2):
        w.setze(x, 3, 0, w.b("hanging_roots", waterlogged=False))
        w.setze(x, 2, 2, w.b("brewing_stand", has_bottle_0=True, has_bottle_1=False, has_bottle_2=True) if x == 0 else
                w.b("flower_pot"))
    return w


def schmiedestand(seed, g=0):
    """Schmiedestand: Amboss, Schleifstein, Esse und Waffenständer unter einer Markise."""
    w = _welt(seed)
    d = _mk(w, seed)
    gelaende(w, 7, art="wiese")
    marktboden(w, 5, d)
    stand(w, d, -2, -1, 4, 3, "gray")
    w.setze(0, 1, 2, w.b("anvil", facing="north"))
    w.setze(-1, 1, 2, w.b("grindstone", face="floor", facing="north"))
    w.setze(1, 1, 0, w.b("blast_furnace", facing="south", lit=True))
    return w


def pranger(seed, g=0):
    """Pranger und Galgenbühne auf dem Marktplatz – mit Holztreppe und Laterne."""
    w = _welt(seed)
    d = _mk(w, seed)
    gelaende(w, 7, art="wiese")
    marktboden(w, 5, d)
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, 1, z, w.b(f"{d['holz']}_planks"))
    for y in range(2, 4):
        w.setze(0, y, 0, w.b(f"{d['holz']}_log", axis="y"))
    for x in (-1, 0, 1):
        w.setze(x, 4, 0, w.b(f"{d['holz']}_slab", type="bottom", waterlogged=False))
    for x in (-1, 0, 1):
        w.setze(x, 1, 3, w.b(f"{d['holz']}_stairs", facing="north", half="bottom", shape="straight", waterlogged=False))
    w.setze(2, 2, 2, w.b("lantern", hanging=False, waterlogged=False))
    return w


def stadtwaage(seed, g=1):
    """Stadtwaage: offene Markthalle auf Steinsäulen mit Obergeschoss in Fachwerk, darunter Waagen und Säcke."""
    import haeuser as H_
    w = _welt(seed)
    d = _mk(w, seed)
    u = U[g]
    a, b = _r(5 * u + 3, 4), _r(3 * u + 2, 3)
    gelaende(w, a + 6, art="wiese")
    marktboden(w, a + 3, d)
    for x in range(-a, a + 1, 3):
        for z in (-b, b):
            for y in range(1, 5):
                w.setze(x, y, z, w.b("stone_bricks") if y < 4 else w.b("chiseled_stone_bricks"))
    st = P.Stil(w, **dict(H_.HAUSPOOL[d["haus"]], dach="mcw_ziegel"))
    P.gebaeude(w, st, -a, -b, a, b, y0=5, etagen=1, eh=4, dach="sattel", tuer="south", sockel_h=0, gauben=True)
    for k in range(4):
        w.setze(-a + 2 + k * 2, 1, 0, MB.ware(w, w.rng))
    hohl(w, 2)
    return w


def zunfthaus(seed, g=2):
    """Zunfthaus der Tuchhändler: hoher Giebelbau mit Stufengiebel, Fahnen der Zünfte und Lastenaufzug."""
    from haeuser import gildenhaus
    return gildenhaus(seed, g)


def maibaum(seed, g=1):
    """Maibaum mit Kranz und bunten Bändern, umgeben von Bänken, Tischen und Lampions für das Dorffest."""
    w = _welt(seed)
    d = _mk(w, seed)
    u = U[g]
    H = _r(16 * u + 6)
    gelaende(w, _r(8 * u + 5), art="wiese")
    for y in range(1, H):
        w.setze(0, y, 0, w.b("stripped_birch_log", axis="y") if (y // 2) % 2 else w.b(f"{d['farben'][0]}_wool"))
    for x, z in kreisrand(1.6):
        w.setze(x, H - 3, z, laub(w, "flowering_azalea"))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        for k in range(1, 6):
            x, z = round(math.cos(a) * k * 0.9), round(math.sin(a) * k * 0.9)
            w.setze(x, H - 3 - k * 2, z, w.b(["red_wool", "yellow_wool", "blue_wool", "lime_wool"][i % 4]))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * 6), round(math.sin(a) * 6)
        w.setze(x, 1, z, w.b(f"{d['holz']}_stairs", facing="north", half="bottom", shape="straight", waterlogged=False))
    return w


def stadttor_markt(seed, g=1):
    """Markttor: Tordurchfahrt mit Zollhäuschen, Schlagbaum, Wappen und Laternen."""
    from burgen import stadttor
    return stadttor(seed, g)


def fischmarkt(seed, g=1):
    """Fischmarkt am Kai: Stände mit Eis und Fisch (Tang, Prismarin), Netze, Fässer und Krane."""
    w = _welt(seed)
    d = _mk(w, seed)
    u = U[g]
    n = 2 + g
    L = n * 6 + 4
    for x in range(-L // 2 - 2, L // 2 + 3):
        for z in range(4, 12):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("gravel"))
    gelaende(w, L // 2 + 4, art="wiese")
    marktboden(w, L // 2 + 1, d, 0, -2)
    for i in range(n):
        x0 = -L // 2 + i * 6
        stand(w, d, x0, -3, 4, 2, ["blue", "white"][i % 2])
        for x in range(x0 + 1, x0 + 4):
            w.setze(x, 1, -2, w.b("packed_ice"))
            w.setze(x, 2, -2, w.b("dried_kelp_block") if x % 2 else w.b("prismarine"))
    for x in range(-L // 2, L // 2 + 1):
        w.setze(x, 0, 3, w.b("spruce_planks"))
    hohl(w, 2)
    return w


def karussell(seed, g=1):
    """Holzkarussell: runde Plattform mit Holzpferden, buntem Kegeldach mit Wimpeln und Laternen."""
    w = _welt(seed)
    d = _mk(w, seed)
    u = U[g]
    R = 3.5 * u + 2.5
    gelaende(w, _r(R + 5), art="wiese")
    for x, z in scheibe(R):
        w.setze(x, 1, z, w.b(f"{d['holz']}_planks") if (x + z) % 2 else w.b("stripped_oak_log", axis="y"))
    for y in range(2, 7):
        w.setze(0, y, 0, w.b("stripped_birch_log", axis="y"))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * (R - 1)), round(math.sin(a) * (R - 1))
        for y in range(2, 6):
            w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False) if y > 3 else
                    w.b(["white_wool", "brown_wool", "black_wool"][i % 3]))
    for k in range(int(R) + 2):
        for x, z in kreisrand(max(0.4, R + 0.6 - k)):
            w.setze(x, 6 + k, z, w.b(f"{d['farben'][(x + z + k) % 2]}_wool"))
    w.setze(0, 7 + int(R) + 2, 0, MB.fahne(w, d["farben"][0], "east"))
    return w


def weinstand(seed, g=0):
    """Weinstand: Fässer-Pyramide, Tresen, Krüge, Rebenlaube und Bänke."""
    w = _welt(seed)
    d = _mk(w, seed)
    gelaende(w, 8, art="wiese")
    marktboden(w, 6, d)
    for k, row in enumerate((5, 4, 3)):
        for i in range(row):
            w.setze(-2 + i + k // 2, 1 + k, -3, w.b("barrel", facing="south", open=False))
    for x in range(-3, 4):
        w.setze(x, 1, 0, w.b(f"{d['holz']}_planks"))
        w.setze(x, 4, 1, laub(w, "jungle") if x % 2 else laub(w, "flowering_azalea"))
    for sx in (-3, 3):
        for y in range(1, 4):
            w.setze(sx, y, 1, w.b(f"{d['holz']}_fence", north=False, south=False, east=False, west=False,
                                  waterlogged=False))
    return w


def stoffmarkt(seed, g=1):
    """Stoffmarkt: Stände mit Ballen farbiger Wolle, Teppichen, Garn-Spulen und Webstühlen."""
    w = _welt(seed)
    d = _mk(w, seed)
    u = U[g]
    n = 2 + g
    gelaende(w, n * 6 + 4, art="wiese")
    marktboden(w, n * 6 + 2, d)
    farben = ["red", "orange", "yellow", "lime", "cyan", "blue", "purple", "magenta", "pink", "white"]
    for i in range(n):
        x0 = -n * 3 + i * 6
        stand(w, d, x0, -2, 4, 3, farben[i % len(farben)])
        for x in range(x0 + 1, x0 + 4):
            for y in (1, 2):
                w.setze(x, y, -1, w.b(f"{farben[(x + y) % len(farben)]}_wool"))
        w.setze(x0 + 2, 1, 3, w.b("loom", facing="north"))
    return w


def kerzenzieher(seed, g=0):
    """Kerzenzieher-Bude: kleine Holzbude mit Kerzenreihen, Bienenstock-Waben und Honigtöpfen."""
    w = _welt(seed)
    d = _mk(w, seed)
    gelaende(w, 7, art="wiese")
    marktboden(w, 5, d)
    stand(w, d, -2, -1, 4, 3, "yellow")
    for x in range(-1, 2):
        w.setze(x, 1, 0, w.b("honeycomb_block"))
        w.setze(x, 2, 0, w.b("candle", candles=3, lit=True, waterlogged=False))
    w.setze(-1, 1, 2, w.b("beehive", facing="south", honey_level=5))
    return w


def gemuesemarkt(seed, g=1):
    """Gemüsemarkt: Karren und Kisten voller Kohl, Möhren, Tomaten, Kartoffeln und Kürbisse (Farmer's Delight)."""
    w = _welt(seed)
    d = _mk(w, seed)
    u = U[g]
    R = _r(7 * u + 4)
    gelaende(w, R + 4, art="wiese")
    marktboden(w, R, d)
    rng = w.rng
    for i in range(3 + g):
        a = i / (3 + g) * 2 * math.pi
        x0, z0 = round(math.cos(a) * R * 0.5) - 2, round(math.sin(a) * R * 0.5) - 1
        stand(w, d, x0, z0, 3, 2)
    for i in range(10 + g * 6):
        x, z = int(rng.integers(-R + 1, R)), int(rng.integers(-R + 1, R))
        if w.frei(x, 1, z):
            w.setze(x, 1, z, MB.ware(w, rng) if rng.random() < 0.7 else w.b("pumpkin"))
    return w


MARKT = {
    "marktstaende": ("Marktstände", marktstaende),
    "marktbrunnen": ("Marktbrunnen", marktbrunnen),
    "gauklerzelt": ("Gaukler-Zelt", gauklerzelt),
    "turnierplatz": ("Turnierplatz", turnierplatz),
    "ladenzeile": ("Ladenzeile", ladenzeile),
    "marktplatz": ("Großer Marktplatz", marktplatz),
    "gasthaus": ("Gasthaus", gasthaus),
    "kraeuterstand": ("Kräuterstand", kraeuterstand),
    "schmiedestand": ("Schmiedestand", schmiedestand),
    "pranger": ("Pranger", pranger),
    "stadtwaage": ("Stadtwaage", stadtwaage),
    "zunfthaus": ("Zunfthaus", zunfthaus),
    "maibaum": ("Maibaum", maibaum),
    "markttor": ("Markttor", stadttor_markt),
    "fischmarkt": ("Fischmarkt", fischmarkt),
    "karussell": ("Holzkarussell", karussell),
    "weinstand": ("Weinstand", weinstand),
    "stoffmarkt": ("Stoffmarkt", stoffmarkt),
    "kerzenzieher": ("Kerzenzieher-Bude", kerzenzieher),
    "gemuesemarkt": ("Gemüsemarkt", gemuesemarkt),
}

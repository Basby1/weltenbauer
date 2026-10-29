"""Boote & Schiffe II – zwanzig weitere Wasserfahrzeuge (Wasserlinie y = 0): Segeljolle, Schoner, Dreimast-Bark,
Teeklipper, Luxusjacht, Eisbrecher, Feuerlöschboot, Flussfähre, Schleppkahn, Lotsenboot, Rettungsboot,
Auslegerkanu, Schilfboot, Galeasse, Knorr, Feuerschiff, Schwimmender Markt, Sonnenbarke, Muschelboot und
Mondbarke."""

from __future__ import annotations

import math

from boote import U, _dh, _holz, _r, _rahsegel_mast, _ruder, _stil, _welt, _zaun, rumpf2
from lib import Verlauf
from schiffe import dreieckssegel, flagge, mast
from skulptur import platte, treppe


def tuch(w, namen):
    return Verlauf(w, "Tuch", namen)


def kajuete(w, x0, x1, hz, yb, hh, wand="white_concrete", dach="spruce_planks", glas="glass", rund=False):
    for x in range(x0, x1 + 1):
        for z in range(-hz, hz + 1):
            for y in range(yb, yb + hh):
                if x in (x0, x1) or abs(z) == hz:
                    fen = y == yb + 1 and not (x in (x0, x1) and abs(z) == hz) and (x + z) % 2 == 0
                    w.setze(x, y, z, w.b(glas) if fen else w.b(wand))
            w.setze(x, yb + hh, z, w.b(dach))


def schornstein(w, x, y, z, h, mat="black_concrete", rauch=True, band=None):
    for k in range(h):
        w.setze(x, y + k, z, w.b(band if band and k == h - 2 else mat))
    if rauch:
        w.setze(x, y + h, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))


def laterne_auf(w, x, y, z):
    w.setze(x, y, z, _zaun(w, "spruce_fence"))
    w.setze(x, y + 1, z, w.b("lantern", hanging=False, waterlogged=False))


# ============================================================================ Segler

def segeljolle(seed, g=1):
    """Segeljolle: ein kleines, offenes Segelboot mit weißem Groß- und Vorsegel, Schwert, Pinne und
    bunt gestreiftem Rumpf."""
    w = _welt(seed)
    u = U[g] * 0.6
    mat = _holz(w, "birch", wand=["blue_terracotta", "white_terracotta", "white_concrete"], deck="birch")
    L, B, D, F = 12 * u + 5, 2.4 * u + 1.2, 1 * u + 0.8, 1.2 * u + 0.8
    r = rumpf2(w, L, B, D, F, mat, form="spitz", reling=False, offen=True, sheer=0.2)
    xm = int(L * 0.12)
    hm = _r(12 * u, 6)
    yb = _dh(r, xm) + 1
    mast(w, xm, 0, hm + yb, False)
    dreieckssegel(w, (xm - 1, yb + hm - 1), (xm - 1, yb + 1), (xm - int(L * 0.42), yb + 1), 0, w.b("white_wool"))
    dreieckssegel(w, (xm + 1, yb + hm - 2), (xm + 1, yb + 1), (int(L * 0.48), yb), 0, w.b("light_gray_wool"))
    flagge(w, xm, yb + hm + 1, 0, 2, ["red_wool", "white_wool"])
    w.setze(-int(L / 2) + 1, yb, 0, w.b("spruce_fence", north=False, south=False, east=True, west=True,
                                        waterlogged=False))
    return w


def schoner(seed, g=2):
    """Schoner: ein schlanker Zweimaster mit großen Gaffelsegeln, Klüvern am langen Bugspriet, dunkelgrünem Rumpf
    mit goldener Zierleiste und Steuerrad am Heck."""
    w = _welt(seed)
    u = U[g] * 0.8
    mat = _holz(w, "dark_oak", wand=["green_terracotta", "green_concrete", "dark_oak_planks"], streifen="gold_block",
                deck="oak")
    L, B, D, F = 26 * u + 8, 3.6 * u + 1.4, 2.2 * u + 1, 2.4 * u + 1
    r = rumpf2(w, L, B, D, F, mat, achter=1)
    tw = tuch(w, ["white_wool", "white_concrete", "light_gray_wool"])
    for k, xf in enumerate((0.15, -0.18)):
        xm = int(L * xf)
        yb = _dh(r, xm) + 1
        hm = _r((18 - k * 2) * u, 7)
        mast(w, xm, yb - 1, hm + 1, False)
        dreieckssegel(w, (xm - 1, yb + hm - 1), (xm - 1, yb + 2), (xm - int(L * 0.28), yb + 2), 0, w.b("white_wool"))
        dreieckssegel(w, (xm - 1, yb + hm - 1), (xm - int(L * 0.28), yb + 2), (xm - int(L * 0.26), yb + hm - 3), 0,
                      w.b("white_wool"))
    xb = int(L / 2)
    yb = _dh(r, xb - 1) + 1
    for k in range(_r(6 * u, 3)):
        w.setze(xb + k, yb + k // 3, 0, w.b("spruce_log", axis="x"))
    xm = int(L * 0.15)
    dreieckssegel(w, (xm + 1, yb + _r(14 * u, 6)), (xm + 1, yb + 1), (xb + _r(5 * u, 2), yb + 1), 0,
                  w.b("light_gray_wool"))
    flagge(w, int(L * 0.15), _dh(r, 0) + _r(18 * u, 7) + 2, 0, 3, ["blue_wool", "white_wool"])
    xh = -int(L / 2) + 2
    w.setze(xh, _dh(r, xh) + 1, 0, w.b("spruce_trapdoor", facing="east", half="bottom", open=True, powered=False,
                                       waterlogged=False))
    return w


def bark(seed, g=3):
    """Dreimast-Bark: ein großer Rahsegler mit drei Masten (die vorderen voll getakelt, der hintere mit
    Gaffelsegel), Kajüten am Heck mit Fensterreihe, Rettungsbooten und Galionsfigur."""
    w = _welt(seed)
    u = U[g] * 0.75
    mat = _holz(w, "dark_oak", wand=["black_terracotta", "dark_oak_planks", "gray_terracotta"], streifen="white_concrete",
                deck="spruce")
    L, B, D, F = 34 * u + 10, 4.6 * u + 1.6, 2.8 * u + 1, 3 * u + 1
    r = rumpf2(w, L, B, D, F, mat, achter=_r(2 * u, 1), heckfenster=True, kanonen=False)
    tw = tuch(w, ["white_wool", "white_concrete", "light_gray_wool"])
    for k, xf in enumerate((0.25, 0.0)):
        xm = int(L * xf)
        yb = _dh(r, xm) + 1
        _rahsegel_mast(w, xm, yb, _r((22 - 2 * k) * u, 9), B, tw, stufen=(0.35, 0.62, 0.86), dick=g >= 2)
    xm = int(-L * 0.25)
    yb = _dh(r, xm) + 1
    hm = _r(18 * u, 8)
    mast(w, xm, yb - 1, hm + 1, False)
    dreieckssegel(w, (xm - 1, yb + hm - 1), (xm - 1, yb + 2), (xm - int(L * 0.2), yb + 2), 0, w.b("white_wool"))
    flagge(w, int(L * 0.25), _dh(r, 0) + _r(22 * u, 9) + 2, 0, 3, ["red_wool", "white_wool", "red_wool"])
    xb = int(L / 2)
    w.setze(xb, _dh(r, xb - 1), 0, w.b("gold_block"))
    return w


def teeklipper(seed, g=3):
    """Teeklipper: ein extrem schlanker, schneller Frachtsegler mit scharfem Bug, drei sehr hohen Masten voller
    Segel, schwarz-goldenem Rumpf und Teekisten an Deck."""
    w = _welt(seed)
    u = U[g] * 0.75
    mat = _holz(w, "dark_oak", wand=["black_concrete", "black_terracotta", "gray_terracotta"], streifen="gold_block",
                deck="birch")
    L, B, D, F = 38 * u + 10, 3.8 * u + 1.4, 2.6 * u + 1, 2.6 * u + 1
    r = rumpf2(w, L, B, D, F, mat, form="normal", sheer=0.15)
    tw = tuch(w, ["white_wool", "white_concrete", "white_wool"])
    for k, xf in enumerate((0.28, 0.02, -0.24)):
        xm = int(L * xf)
        yb = _dh(r, xm) + 1
        _rahsegel_mast(w, xm, yb, _r((26 - 3 * k) * u, 10), B * 0.95, tw, stufen=(0.3, 0.52, 0.72, 0.9))
    for x, y, z in r["oben"]:
        if w.rng.random() < 0.04 and abs(z) < B - 1.5:
            w.setze(x, y + 1, z, w.b("barrel", facing="up", open=False) if w.rng.random() < 0.5 else
                    w.b("spruce_planks"))
    return w


# ============================================================================ Motorschiffe

def jacht(seed, g=2):
    """Luxusjacht: ein weißer Rumpf mit blauem Wasserpass, zwei gestaffelte Aufbauten mit dunklen Panorama-
    fenstern, Sonnendeck mit Liegen und ein kleiner Radarmast."""
    w = _welt(seed)
    u = U[g] * 0.75
    mat = dict(unten=Verlauf(w, "Rumpf", ["blue_concrete", "blue_concrete", "white_concrete"]),
               wand=Verlauf(w, "Wand", ["white_concrete", "white_concrete", "white_concrete"]),
               streifen="light_blue_concrete", leiste="stripped_birch_log", zaun="iron_bars",
               deck=Verlauf(w, "Deck", ["birch_planks", "stripped_birch_log", "birch_planks"]), gold=False)
    L, B, D, F = 24 * u + 8, 3.6 * u + 1.4, 1.8 * u + 1, 2.4 * u + 1
    r = rumpf2(w, L, B, D, F, mat, form="normal", sheer=0.25)
    hz = int(B * 0.7)
    yb = _dh(r, 0) + 1
    kajuete(w, -int(L * 0.3), int(L * 0.15), hz, yb, _r(2 * u + 1, 2), glas="black_stained_glass",
            dach="white_concrete")
    yb2 = yb + _r(2 * u + 1, 2) + 1
    kajuete(w, -int(L * 0.22), int(L * 0.02), max(1, hz - 1), yb2, _r(1.6 * u + 1, 2), glas="black_stained_glass",
            dach="white_concrete")
    ytop = yb2 + _r(1.6 * u + 1, 2) + 1
    for y in range(ytop, ytop + _r(3 * u, 2)):
        w.setze(-int(L * 0.1), y, 0, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                         waterlogged=False))
    w.setze(-int(L * 0.1), ytop + _r(3 * u, 2), 0, w.b("white_concrete"))
    for k in range(2):
        w.setze(-int(L * 0.38) + k * 2, yb, 0, w.b("white_bed", facing="east", part="foot", occupied=False))
    return w


def eisbrecher(seed, g=3):
    """Eisbrecher: ein wuchtiges, rot-schwarzes Schiff mit verstärktem, schräg ansteigendem Bug, hohem
    Brückenhaus, Kran und dickem Schornstein, das sich durch Eisschollen schiebt."""
    w = _welt(seed)
    u = U[g] * 0.75
    mat = dict(unten=Verlauf(w, "Rumpf", ["black_concrete", "black_concrete", "red_concrete"]),
               wand=Verlauf(w, "Wand", ["red_concrete", "red_concrete", "red_terracotta"]),
               streifen="white_concrete", leiste="polished_blackstone", zaun="iron_bars",
               deck=Verlauf(w, "Deck", ["gray_concrete", "light_gray_concrete", "gray_concrete"]), gold=False)
    L, B, D, F = 28 * u + 8, 5 * u + 2, 2.8 * u + 1, 3 * u + 1
    r = rumpf2(w, L, B, D, F, mat, form="normal", sheer=0.3, vorn=_r(1.5 * u, 1))
    hz = int(B * 0.75)
    yb = _dh(r, 0) + 1
    x0, x1 = -int(L * 0.3), int(L * 0.02)
    for e in range(3):
        kajuete(w, x0 + e, x1 - e, hz - e // 2, yb + e * 3, 3, wand="white_concrete", glas="black_stained_glass",
                dach="white_concrete")
    schornstein(w, int(-L * 0.2), yb + 9, 0, _r(4 * u + 2, 3), "red_concrete", band="black_concrete")
    for k in range(_r(6 * u, 3)):
        w.setze(int(L * 0.2), yb + k, 0, w.b("yellow_concrete"))
        w.setze(int(L * 0.2) + k // 2, yb + _r(6 * u, 3), 0, w.b("yellow_concrete"))
    rng = w.rng
    for k in range(int(20 * u) + 8):
        x = int(L / 2) + int(rng.random() * L * 0.6)
        z = int((rng.random() - 0.5) * B * 5)
        for dx in range(_r(2 * u, 1)):
            for dz in range(_r(2 * u, 1)):
                w.setze(x + dx, 0, z + dz, w.b("packed_ice" if rng.random() < 0.6 else "snow_block"))
    return w


def feuerloeschboot(seed, g=1):
    """Feuerlöschboot: ein rotes Hafenschiff mit weißem Aufbau, zwei Wasserwerfern auf Türmchen, aus denen echte
    Wasserbögen schießen, und Rettungsringen an der Reling."""
    w = _welt(seed)
    u = U[g] * 0.8
    mat = dict(unten=Verlauf(w, "Rumpf", ["black_concrete", "red_concrete", "red_concrete"]),
               wand=Verlauf(w, "Wand", ["red_concrete", "red_concrete", "red_concrete"]),
               streifen="white_concrete", leiste="stripped_spruce_log", zaun="iron_bars",
               deck=Verlauf(w, "Deck", ["gray_concrete", "light_gray_concrete", "gray_concrete"]), gold=False)
    L, B, D, F = 18 * u + 6, 3.4 * u + 1.4, 1.8 * u + 1, 2.2 * u + 1
    r = rumpf2(w, L, B, D, F, mat, sheer=0.2)
    hz = int(B * 0.6)
    yb = _dh(r, 0) + 1
    kajuete(w, -int(L * 0.3), 0, hz, yb, 3, wand="white_concrete", glas="glass", dach="red_concrete")
    for k, xf in enumerate((0.25, -0.05)):
        x = int(L * xf)
        y0 = yb + (4 if k else 0)
        for y in range(y0, y0 + 2):
            w.setze(x, y, 0, w.b("red_concrete"))
        w.setze(x, y0 + 2, 0, w.b("iron_block"))
        for i in range(_r(10 * u, 5)):
            t = i / _r(10 * u, 5)
            xx = x + 1 + i
            yy = y0 + 2 + round(6 * u * math.sin(math.pi * t))
            if yy >= 1:
                w.setze(xx, yy, 0, w.b("water", level=0), False)
    for x, y, z in r["oben"]:
        if abs(z) >= B - 1 and x % 6 == 0:
            w.setze(x, y + 1, z, w.b("white_concrete"))
    return w


def flussfaehre(seed, g=2):
    """Flussfähre: eine breite, flache Holzfähre mit Geländer, Laderampen an beiden Enden, Fährmannshäuschen und
    einem Seil, an dem sie über den Fluss gezogen wird; ein Karren und Fässer an Bord."""
    from feinbau import kram
    w = _welt(seed)
    u = U[g] * 0.8
    mat = _holz(w, "spruce", deck="spruce")
    L, B, D, F = 16 * u + 6, 5 * u + 2, 1 * u + 0.6, 1.2 * u + 0.6
    r = rumpf2(w, L, B, D, F, mat, form="flach", sheer=0.0)
    yb = _dh(r, 0) + 1
    hz = int(B)
    for e in (int(L / 2) + 1, -int(L / 2) - 1):
        for k in range(_r(3 * u, 2)):
            for z in range(-int(B * 0.6), int(B * 0.6) + 1):
                w.setze(e + (k if e > 0 else -k), yb - 1 - k // 2, z, platte(w, "spruce"))
    kajuete(w, -2, 2, 2, yb, 3, wand="spruce_planks", dach="dark_oak_planks", glas="glass_pane"
            if False else "glass")
    kram(w, int(L * 0.25), yb, 0, 5)
    for x in range(-int(L), int(L) + 1):
        w.setze(x, yb + 5, hz + 1, w.b("chain", axis="x", waterlogged=False), False)
    for xs in (-int(L * 0.3), int(L * 0.3)):
        for y in range(yb, yb + 5):
            w.setze(xs, y, hz + 1, _zaun(w, "spruce_fence"))
    return w


def schleppkahn(seed, g=2):
    """Schleppkahn mit Schlepper: ein kleiner, kräftiger Schlepper mit Schornstein und Fendern zieht an einer Kette
    einen langen, beladenen Lastkahn voller Kohle und Kisten."""
    w = _welt(seed)
    u = U[g] * 0.7
    mat = dict(unten=Verlauf(w, "Rumpf", ["black_concrete", "black_concrete", "brown_terracotta"]),
               wand=Verlauf(w, "Wand", ["brown_terracotta", "orange_terracotta", "brown_terracotta"]),
               streifen="yellow_concrete", leiste="stripped_spruce_log", zaun="spruce_fence",
               deck=Verlauf(w, "Deck", ["spruce_planks", "oak_planks", "spruce_planks"]), gold=False)
    Ls, B, D, F = 12 * u + 5, 3 * u + 1.2, 1.6 * u + 1, 2 * u + 1
    r = rumpf2(w, Ls, B, D, F, mat, sheer=0.3)
    yb = _dh(r, 0) + 1
    kajuete(w, -int(Ls * 0.25), int(Ls * 0.1), int(B * 0.6), yb, 3, wand="white_concrete", dach="black_concrete")
    schornstein(w, -int(Ls * 0.1), yb + 4, 0, _r(3 * u + 1, 2), "black_concrete", band="yellow_concrete")
    for x, y, z in r["oben"]:
        if abs(z) >= int(B) and x % 2 == 0:
            w.setze(x, y - 1, z + (1 if z > 0 else -1), w.b("black_wool"), False)
    Lk = 22 * u + 6
    x0 = -int(Ls / 2) - _r(5 * u, 3) - int(Lk / 2)
    for x in range(int(x0 - Lk / 2), int(x0 + Lk / 2) + 1):
        for z in range(-int(B * 1.2), int(B * 1.2) + 1):
            for y in range(-1, 2):
                rand = abs(z) == int(B * 1.2) or x in (int(x0 - Lk / 2), int(x0 + Lk / 2)) or y == -1
                if rand:
                    w.setze(x, y, z, w.b("black_concrete" if y < 1 else "brown_terracotta"))
                elif y == 1:
                    w.setze(x, y, z, w.b("coal_block") if (x // 4) % 2 else w.b("barrel", facing="up", open=False))
    for x in range(int(x0 + Lk / 2) + 1, -int(Ls / 2)):
        w.setze(x, 2, 0, w.b("chain", axis="x", waterlogged=False))
    return w


def lotsenboot(seed, g=1):
    """Lotsenboot: ein kleines, wendiges Motorboot mit orangefarbenem Rumpf, Steuerhaus, Signalmast mit
    Lotsenflagge, Suchscheinwerfer und Fendern."""
    w = _welt(seed)
    u = U[g] * 0.7
    mat = dict(unten=Verlauf(w, "Rumpf", ["black_concrete", "orange_concrete", "orange_concrete"]),
               wand=Verlauf(w, "Wand", ["orange_concrete", "orange_concrete", "orange_terracotta"]),
               streifen="white_concrete", leiste="stripped_spruce_log", zaun="iron_bars",
               deck=Verlauf(w, "Deck", ["light_gray_concrete", "gray_concrete", "light_gray_concrete"]), gold=False)
    L, B, D, F = 14 * u + 5, 2.8 * u + 1.2, 1.4 * u + 0.8, 1.8 * u + 0.8
    r = rumpf2(w, L, B, D, F, mat, sheer=0.3)
    yb = _dh(r, 0) + 1
    kajuete(w, -int(L * 0.2), int(L * 0.1), int(B * 0.6), yb, 3, wand="white_concrete", dach="orange_concrete")
    for y in range(yb + 4, yb + 4 + _r(4 * u, 2)):
        w.setze(0, y, 0, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
    flagge(w, 0, yb + 3 + _r(4 * u, 2), 0, 2, ["red_wool", "white_wool"])
    w.setze(int(L * 0.1) + 1, yb + 3, 0, w.b("redstone_lamp", lit=True))
    return w


def rettungsboot(seed, g=1):
    """Rettungsboot: ein geschlossenes, leuchtend orangefarbenes Rettungsboot mit rundem Dach, Bullaugen,
    Haltegriffen und einem Davit-Kran an einer kleinen Hafenmole."""
    w = _welt(seed)
    u = U[g] * 0.7
    mat = dict(unten=Verlauf(w, "Rumpf", ["white_concrete", "white_concrete", "orange_concrete"]),
               wand=Verlauf(w, "Wand", ["orange_concrete", "orange_concrete", "orange_concrete"]),
               streifen=None, leiste="orange_concrete", zaun="iron_bars",
               deck=Verlauf(w, "Deck", ["orange_concrete", "orange_concrete", "orange_concrete"]), gold=False)
    L, B, D, F = 12 * u + 5, 2.6 * u + 1.2, 1.4 * u + 0.8, 1.4 * u + 0.8
    r = rumpf2(w, L, B, D, F, mat, form="spitz", reling=False)
    yb = _dh(r, 0) + 1
    hz = int(B)
    for x in range(-int(L * 0.38), int(L * 0.38) + 1):
        for z in range(-hz, hz + 1):
            h = int(math.sqrt(max(0, hz * hz - z * z)) * 0.8) + 1
            for y in range(yb, yb + h + 1):
                if abs(z) >= hz - 0.5 or y == yb + h:
                    bull = y == yb + 1 and x % 3 == 0 and abs(z) >= hz - 0.5
                    w.setze(x, y, z, w.b("light_blue_stained_glass") if bull else w.b("orange_concrete"))
    for x in range(-int(L / 2) - 2, int(L / 2) + 3):
        for z in range(hz + 2, hz + 6):
            for y in range(-2, 2):
                w.setze(x, y, z, w.b("stone_bricks"))
    for y in range(2, yb + _r(5 * u, 3)):
        w.setze(0, y, hz + 3, w.b("polished_blackstone"))
    for z in range(0, hz + 4):
        w.setze(0, yb + _r(5 * u, 3), z, w.b("polished_blackstone"))
    for y in range(yb + 3, yb + _r(5 * u, 3)):
        w.setze(0, y, 0, w.b("chain", axis="y", waterlogged=False))
    return w


def auslegerkanu(seed, g=1):
    """Auslegerkanu: ein schmaler, geschnitzter Einbaum mit Ausleger aus Bambus, einem Krebsscherensegel aus
    Mattengeflecht und Paddeln."""
    w = _welt(seed)
    u = U[g] * 0.6
    mat = _holz(w, "jungle", deck="jungle")
    L, B, D, F = 14 * u + 6, 1.6 * u + 1, 1 * u + 0.6, 1 * u + 0.8
    r = rumpf2(w, L, B, D, F, mat, form="spitz", enden=1.2 * u, reling=False, offen=True)
    za = int(B) + _r(4 * u, 3)
    for x in range(-int(L * 0.35), int(L * 0.35) + 1):
        w.setze(x, 0, za, w.b("bamboo_block", axis="x"))
    for xs in (-int(L * 0.2), int(L * 0.2)):
        for z in range(0, za):
            w.setze(xs, _dh(r, xs), z, w.b("bamboo_block", axis="z"), False)
    yb = _dh(r, 0) + 1
    hm = _r(9 * u, 4)
    for k in range(hm):
        w.setze(0, yb + k, 0, w.b("bamboo_block", axis="y"))
    dreieckssegel(w, (-1, yb + hm - 1), (-1, yb + 1), (-int(L * 0.32), yb + 1), 0, w.b("yellow_terracotta"))
    return w


def schilfboot(seed, g=1):
    """Schilfboot: ein Boot aus gebündeltem Schilfrohr mit hochgebogenen, verschnürten Enden, einem kleinen
    Sonnendach aus Matten und einem Steuerruder, wie aus alten Seevölker-Sagen."""
    w = _welt(seed)
    u = U[g] * 0.7
    L = 16 * u + 6
    half = L / 2
    for i in range(int(-half), int(half) + 1):
        t = i / half
        b = (2 * u + 1) * math.sqrt(max(0, 1 - t ** 4))
        y_end = round(5 * u * max(0, abs(t) - 0.6) ** 1.5 * 6)
        for z in range(-int(b), int(b) + 1):
            for y in range(-1, 1 + (y_end if abs(z) < 1 else 0)):
                bund = i % 3 == 0 and y == 0
                w.setze(i, y, z, w.b("brown_wool" if bund else "hay_block", axis="x") if not bund else
                        w.b("brown_wool"))
    for (x, z) in ((-2, -1), (2, -1), (-2, 1), (2, 1)):
        for y in range(1, 4):
            w.setze(x, y, z, w.b("bamboo_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False))
    for x in range(-3, 4):
        for z in range(-2, 3):
            w.setze(x, 4, z, w.b("bamboo_mosaic_slab", type="bottom", waterlogged=False))
    for k in range(3):
        w.setze(-int(half) + 2 - k, 1 - k, 1, w.b("spruce_fence", north=False, south=False, east=True, west=True,
                                                  waterlogged=False))
    return w


def galeasse(seed, g=3):
    """Galeasse: ein großes Ruder-Segel-Kriegsschiff mit zwei Lateinersegeln, langen Riemenreihen, einem
    gepanzerten Vorkastell mit Geschützpforten und prächtigem Achterdeck mit Laternen."""
    w = _welt(seed)
    u = U[g] * 0.75
    mat = _holz(w, "dark_oak", wand=["red_terracotta", "dark_oak_planks", "red_concrete"], streifen="gold_block",
                deck="spruce")
    L, B, D, F = 34 * u + 10, 4.4 * u + 1.6, 2.4 * u + 1, 2.6 * u + 1
    r = rumpf2(w, L, B, D, F, mat, achter=_r(2 * u, 1), vorn=_r(1.6 * u, 1), kanonen=True, heckfenster=True)
    _ruder(w, r, list(range(-int(L * 0.3), int(L * 0.3), 2)), F, B, _r(4 * u, 3))
    for k, xf in enumerate((0.2, -0.12)):
        xm = int(L * xf)
        yb = _dh(r, xm) + 1
        hm = _r((18 - 3 * k) * u, 7)
        mast(w, xm, yb - 1, hm + 1, g >= 3)
        dreieckssegel(w, (xm + int(L * 0.1), yb + hm), (xm - int(L * 0.16), yb + 3), (xm + 1, yb + 2), 0,
                      w.b("white_wool" if k else "red_wool"))
    xh = -int(L / 2) + 2
    for z in (-int(B * 0.5), int(B * 0.5)):
        laterne_auf(w, xh, _dh(r, xh) + 1, z)
    return w


def knorr(seed, g=2):
    """Knorr: ein bauchiges nordisches Handelsschiff mit Klinkerplanken, einem großen rot-weiß gestreiften
    Rahsegel, Ladung aus Fässern, Fellen und Tieren unter einer Plane in der Mitte."""
    w = _welt(seed)
    u = U[g] * 0.75
    mat = _holz(w, "spruce", wand=["spruce_planks", "dark_oak_planks", "stripped_spruce_log"], deck="spruce")
    L, B, D, F = 20 * u + 6, 4.2 * u + 1.6, 1.8 * u + 1, 2 * u + 1
    r = rumpf2(w, L, B, D, F, mat, form="spitz", enden=2.4 * u, offen=True, reling=False)
    xm = 0
    yb = _dh(r, 0) + 1
    tw = tuch(w, ["red_wool", "white_wool", "red_wool"])
    _rahsegel_mast(w, xm, yb, _r(14 * u, 6), B * 0.9, tw, stufen=(0.75,), bauch=1.5)
    for x in range(-int(L * 0.25), int(L * 0.25) + 1):
        for z in range(-int(B * 0.5), int(B * 0.5) + 1):
            if x != 0 or z != 0:
                w.setze(x, max(0, int(F) - 2), z, w.b("barrel", facing="up", open=False) if (x + z) % 3 == 0 else
                        w.b("brown_wool") if (x + z) % 3 == 1 else w.b("white_wool"), False)
    return w


def feuerschiff(seed, g=2):
    """Feuerschiff: ein rot gestrichenes, verankertes Leuchtschiff mit großem weißem Namensschriftzug-Band, einem
    Gittermast mit Leuchtlaterne, Nebelhorn und Ankerkette."""
    w = _welt(seed)
    u = U[g] * 0.75
    mat = dict(unten=Verlauf(w, "Rumpf", ["black_concrete", "red_concrete", "red_concrete"]),
               wand=Verlauf(w, "Wand", ["red_concrete", "red_concrete", "red_terracotta"]),
               streifen="white_concrete", leiste="white_concrete", zaun="iron_bars",
               deck=Verlauf(w, "Deck", ["spruce_planks", "oak_planks", "spruce_planks"]), gold=False)
    L, B, D, F = 20 * u + 6, 4 * u + 1.4, 2 * u + 1, 2.4 * u + 1
    r = rumpf2(w, L, B, D, F, mat, sheer=0.15)
    yb = _dh(r, 0) + 1
    kajuete(w, -int(L * 0.35), -int(L * 0.1), int(B * 0.6), yb, 3, wand="white_concrete", dach="red_concrete")
    hm = _r(12 * u, 6)
    for y in range(yb, yb + hm):
        for (dx, dz) in ((0, 0),):
            w.setze(dx, y, dz, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False)
                    if y % 3 else w.b("red_concrete"))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(dx, yb + hm, dz, w.b("yellow_stained_glass") if (dx or dz) else w.b("sea_lantern"))
            w.setze(dx, yb + hm + 1, dz, w.b("red_concrete"))
    for k in range(_r(8 * u, 4)):
        w.setze(int(L / 2) + 1, -k, 1, w.b("chain", axis="y", waterlogged=False))
    return w


def schwimmmarkt(seed, g=2):
    """Schwimmender Markt: mehrere zusammengebundene Flöße und Kähne mit bunten Sonnensegeln, Marktständen voller
    Früchte, Körben und Fässern, Laternen an Stangen."""
    w = _welt(seed)
    u = U[g] * 0.8
    rng = w.rng
    farben = ["red_wool", "yellow_wool", "lime_wool", "orange_wool", "light_blue_wool", "magenta_wool"]
    n = 3 + g
    for k in range(n):
        cx = int((k - (n - 1) / 2) * (7 * u + 3))
        cz = int((rng.random() - 0.5) * 4 * u)
        B, T = _r(3 * u + 1, 2), _r(2.4 * u + 1, 2)
        for x in range(cx - B, cx + B + 1):
            for z in range(cz - T, cz + T + 1):
                w.setze(x, 0, z, w.b("stripped_spruce_log" if (x + k) % 2 else "spruce_planks", axis="z") if
                        (x + k) % 2 else w.b("spruce_planks"))
        for (x, z) in ((cx - B, cz - T), (cx + B, cz - T), (cx - B, cz + T), (cx + B, cz + T)):
            for y in range(1, 4):
                w.setze(x, y, z, _zaun(w, "spruce_fence"))
        f = farben[k % len(farben)]
        for x in range(cx - B, cx + B + 1):
            for z in range(cz - T, cz + T + 1):
                w.setze(x, 4, z, w.b(f if (x + z) % 2 else "white_wool"))
        for x in range(cx - B + 1, cx + B):
            w.setze(x, 1, cz, w.b(["melon", "pumpkin", "hay_block", "barrel", "composter"][(x + k) % 5],
                                  **({"axis": "y"} if (x + k) % 5 == 2 else {"facing": "up", "open": False}
                                     if (x + k) % 5 == 3 else {"level": 0} if (x + k) % 5 == 4 else {})))
        laterne_auf(w, cx + B + 1, 1, cz)
    return w


# ============================================================================ Fantasieboote

def sonnenbarke(seed, g=2):
    """Sonnenbarke: eine prunkvolle Zeremonienbarke mit sichelförmig hochgezogenen Enden in Lotusform, goldener
    Sonnenscheibe am Bug, einem Baldachin auf Säulen und Rudern."""
    w = _welt(seed)
    u = U[g] * 0.75
    mat = _holz(w, "jungle", wand=["yellow_terracotta", "smooth_sandstone", "orange_terracotta"], deck="jungle")
    mat["leiste"] = "stripped_jungle_log"
    L, B, D, F = 22 * u + 6, 3 * u + 1.2, 1.4 * u + 0.8, 1.8 * u + 0.8
    r = rumpf2(w, L, B, D, F, mat, form="spitz", enden=5 * u, reling=False)
    yb = _dh(r, 0) + 1
    for (x, z) in ((-3, -2), (3, -2), (-3, 2), (3, 2)):
        for y in range(yb, yb + 4):
            w.setze(x, y, z, w.b("smooth_sandstone_wall" if False else "sandstone_wall", up=True, north="none",
                                 south="none", east="none", west="none", waterlogged=False))
    for x in range(-4, 5):
        for z in range(-3, 4):
            w.setze(x, yb + 4, z, w.b("blue_wool" if (x + z) % 2 else "gold_block"))
    xb = int(L / 2)
    yt = _dh(r, xb - 1)
    for dy in range(-2, 3):
        for dz in range(-2, 3):
            if dy * dy + dz * dz <= 5:
                w.setze(xb - 1, yt + 2 + dy, dz, w.b("gold_block"))
    _ruder(w, r, [-int(L * 0.25), int(L * 0.2)], F, B, _r(3 * u, 2), holz="jungle_fence")
    return w


def muschelboot(seed, g=1):
    """Muschelboot: eine riesige, perlmuttschimmernde Muschelschale als Boot, gezogen von zwei Seepferdchen-
    Galionsfiguren aus Prismarin, mit Perlenlaternen und einem Thronsitz."""
    w = _welt(seed)
    u = U[g] * 0.8
    R = 6 * u + 3
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            d = math.hypot(x, z)
            if d > R:
                continue
            a = math.atan2(z, -x)
            rippe = abs(math.sin(a * 7)) < 0.3
            h = round((d / R) ** 2 * R * 0.5)
            for y in range(-1, h + 1):
                if y == h or (d > R - 1.2):
                    w.setze(x, y, z, w.b("pink_terracotta" if rippe else "white_terracotta" if y > 0 else
                                         "calcite"))
            if d > R - 1.5 and x < -R * 0.3:
                for y in range(h, h + round((1 - abs(z) / R) * R * 0.6)):
                    w.setze(x, y, z, w.b("pink_terracotta" if rippe else "white_terracotta"))
    for y in range(1, 4):
        w.setze(-int(R * 0.4), y, 0, w.b("prismarine_bricks"))
    w.setze(-int(R * 0.4) + 1, 1, 0, treppe(w, "prismarine_brick", "west"))
    for sz in (-2, 2):
        x0 = int(R) + 2
        for k, (dx, dy) in enumerate(((0, 0), (1, 1), (1, 2), (2, 3), (2, 4), (3, 4))):
            w.setze(x0 + dx, dy, sz, w.b("prismarine"))
        w.setze(x0 + 3, 3, sz, w.b("dark_prismarine"))
        for k in range(1, 3):
            w.setze(x0 - k, 1, sz, w.b("chain", axis="x", waterlogged=False))
    for (x, z) in ((int(R * 0.4), int(R * 0.6)), (int(R * 0.4), -int(R * 0.6))):
        w.setze(x, 2, z, w.b("pearlescent_froglight", axis="y"), False)
    return w


def mondbarke(seed, g=2):
    """Mondbarke: ein fliegendes Fantasieboot in Form einer silbernen Mondsichel mit Sternenlaternen an
    Ketten, einem Segel aus Nachtblau mit goldenen Sternen und einer Glaskanzel."""
    from feinbau import laterne
    w = _welt(seed)
    u = U[g] * 0.8
    R = 10 * u + 4
    y0 = int(R * 0.4) + 2
    for x in range(-int(R) - 1, int(R) + 2):
        for y in range(-int(R) - 1, int(R) + 2):
            d1 = math.hypot(x, y)
            d2 = math.hypot(x, y - R * 0.45)
            if d1 <= R and d2 > R * 0.9 and y <= R * 0.2:
                for z in range(-_r(2 * u, 1), _r(2 * u, 1) + 1):
                    w.setze(x, y0 + y + int(R * 0.6), z, w.b("smooth_quartz" if (x + y) % 4 else "white_concrete"))
    yd = y0 + int(R * 0.6) - int(R * 0.45)
    hm = _r(10 * u, 5)
    mast(w, 0, yd, hm, False, "stripped_birch_log")
    for x in range(-int(R * 0.35), int(R * 0.35) + 1):
        for y in range(yd + 2, yd + hm - 1):
            if abs(x) <= (yd + hm - 1 - y) * 0.7:
                w.setze(x, y, 1, w.b("gold_block") if (x * 7 + y * 3) % 11 == 0 else w.b("blue_wool"))
    for x in (-int(R * 0.6), int(R * 0.6)):
        y = max(yy for (xx, yy, zz) in w.bloecke if xx == x and zz == 0) if any(
            xx == x and zz == 0 for (xx, yy, zz) in w.bloecke) else yd
        laterne(w, x, y - 1, 0, 2, seele=False)
    return w


BOOTE3 = {
    "segeljolle": ("Segeljolle", segeljolle),
    "schoner": ("Schoner", schoner),
    "bark": ("Dreimast-Bark", bark),
    "teeklipper": ("Teeklipper", teeklipper),
    "jacht": ("Luxusjacht", jacht),
    "eisbrecher": ("Eisbrecher", eisbrecher),
    "feuerloeschboot": ("Feuerlöschboot", feuerloeschboot),
    "flussfaehre": ("Flussfähre", flussfaehre),
    "schleppkahn": ("Schlepper mit Lastkahn", schleppkahn),
    "lotsenboot": ("Lotsenboot", lotsenboot),
    "rettungsboot": ("Rettungsboot am Davit", rettungsboot),
    "auslegerkanu": ("Auslegerkanu", auslegerkanu),
    "schilfboot": ("Schilfboot", schilfboot),
    "galeasse": ("Galeasse", galeasse),
    "knorr": ("Knorr", knorr),
    "feuerschiff": ("Feuerschiff", feuerschiff),
    "schwimmmarkt": ("Schwimmender Markt", schwimmmarkt),
    "sonnenbarke": ("Sonnenbarke", sonnenbarke),
    "muschelboot": ("Muschelboot", muschelboot),
    "mondbarke": ("Mondbarke", mondbarke),
}

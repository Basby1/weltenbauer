"""Himmelsstadt II – zwanzig weitere, fein gebaute Himmelsinseln: Himmelsdom, Bibliotheksturm, Sternwarte,
Teehaus, Himmelsleuchtturm, Glockenturm, Weinberg, Badehaus, Ballonstation, Gewächshäuser, Schmiede, Akademie,
Amphitheater, Brunnenplatz, Wassermühle, Taubentürme, Herrenhaus, Bogenbrücken-Inseln, Treppeninseln und Wachbastion.

Häuser mit Steinsockel, Fachwerk-Obergeschoss auf Kragsteinen, Fenstern mit Läden und Blumenkästen, geschwungenen
Satteldächern, Kaminen mit Rauch."""

from __future__ import annotations

import math

import wald2
from baeume import kirschbaum as kirsche_alt
from feinbau import (D, GEGEN, Dachmat, Mix, balkon, boden, busch, fachwerk, fenster, fensterreihe, kamin, kegeldach,
                     kragsteine, kram, laterne, mauer, platte, satteldach, sockel, stamm, treppe, tuer, zaun)
from himmelsstadt import Schema, _welt, flaeche, haengebruecke_teil, insel, laternenpfahl, unterseite, weg
from lib import Rauschen, einfuegen

RG = [8, 12, 18, 28]
TG = [10, 14, 20, 30]

STILE = {
    "fachwerk": dict(sockel=[("stone_bricks", 3), ("cobblestone", 1), ("mossy_stone_bricks", 1)],
                     wand=[("white_terracotta", 3), ("calcite", 2), ("smooth_sandstone", 1)],
                     fuell=[("white_terracotta", 3), ("calcite", 2)], holz="dark_oak",
                     dach=["dark_oak", "spruce", "mud_brick"]),
    "kupfer": dict(sockel=[("andesite", 2), ("stone_bricks", 2), ("polished_andesite", 1)],
                   wand=[("calcite", 3), ("smooth_quartz", 1), ("diorite", 1)],
                   fuell=[("calcite", 3), ("white_concrete", 1)], holz="spruce",
                   dach=["mcw:cyan_terracotta", "prismarine_brick", "dark_prismarine"]),
    "stein": dict(sockel=[("cobbled_deepslate", 2), ("stone_bricks", 2)],
                  wand=[("stone_bricks", 3), ("cracked_stone_bricks", 1), ("andesite", 1), ("mossy_stone_bricks", 1)],
                  fuell=[("stone_bricks", 2), ("andesite", 1)], holz="spruce",
                  dach=["deepslate_tile", "cobbled_deepslate", "deepslate_brick"]),
    "terrakotta": dict(sockel=[("bricks", 2), ("stone_bricks", 1)],
                       wand=[("smooth_sandstone", 2), ("white_terracotta", 1), ("yellow_terracotta", 1)],
                       fuell=[("smooth_sandstone", 2), ("orange_terracotta", 1)], holz="oak",
                       dach=["mcw:orange_terracotta", "brick", "granite"]),
    "blau": dict(sockel=[("stone_bricks", 2), ("andesite", 1)],
                 wand=[("calcite", 2), ("light_blue_terracotta", 1)], fuell=[("calcite", 3)], holz="spruce",
                 dach=["mcw:blue_terracotta", "mcw:light_blue_terracotta", "deepslate_tile"]),
}


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


# ============================================================================ Grundlagen

def basis(seed, g, flach=0.7, rf=1.0, cx=0, cz=0, top=None, w=None, sch=None, extras=True):
    w = w or _welt(seed)
    sch = sch or Schema(w)
    rs = Rauschen(w, 4)
    R, T = RG[g] * rf, TG[g] * rf
    top = top if top is not None else int(TG[g] * 1.9) + [10, 14, 18, 24][g]
    oben = insel(w, sch, rs, cx, top, cz, R, T, flach=flach, extras=extras)
    return w, sch, R, top, oben


def platz(w, oben, cx, cz, B, T, top, tiefe=6, mat=None):
    """Ebnet den Bauplatz (B×T um cx, cz) und gibt die Bodenhöhe y0 (erstes freies y) zurück."""
    x0, z0 = cx - B // 2, cz - T // 2
    y = flaeche(oben, x0 - 1, z0 - 1, B + 2, T + 2, top)
    mat = mat or M(w, [("stone", 2), ("andesite", 1), ("tuff", 1)])
    for x in range(x0 - 1, x0 + B + 1):
        for z in range(z0 - 1, z0 + T + 1):
            for yy in range(y - tiefe, y + 1):
                if (x, yy, z) not in w.bloecke:
                    w.setze(x, yy, z, mat(x, yy, z) if yy < y else w.b("grass_block", snowy=False))
            for yy in range(y + 1, y + 30):
                if (x, yy, z) in w.bloecke:
                    w.bloecke.pop((x, yy, z))
            oben[(x, z)] = y
    return y + 1


def haus(w, cx, cz, B, T, y0, stil="fachwerk", geschosse=2, tuer_s="south", first_x=None, schorn=True, steil=1,
         balk=False):
    """Detailliertes Haus mit Sockel; gibt die Firsthöhe zurück."""
    S = STILE[stil]
    holz = S["holz"]
    x0, z0 = cx - B // 2, cz - T // 2
    x1, z1 = x0 + B - 1, z0 + T - 1
    sockel(w, x0, z0, x1, z1, y0 - 2, 2, M(w, S["sockel"]), "stone_brick")
    wand = M(w, S["wand"])
    mauer(w, x0, z0, x1, z1, y0, y0 + 3, wand, ecke=M(w, S["sockel"]))
    boden(w, x0 + 1, z0 + 1, x1 - 1, z1 - 1, y0 - 1, holz)
    fensterreihe(w, x0, z0, x1, z1, y0 + 1, ("north", "south", "east", "west"), abstand=3, holz=holz, blumen=0.6)
    seite_x = {"south": (cx, z1), "north": (cx, z0), "east": (x1, cz), "west": (x0, cz)}[tuer_s]
    tuer(w, seite_x[0], y0, seite_x[1], tuer_s, holz=holz, stufen=0)
    yo = y0 + 4
    X0, Z0, X1, Z1 = x0, z0, x1, z1
    for k in range(1, geschosse):
        kragsteine(w, x0, z0, x1, z1, yo - 1, holz)
        X0, Z0, X1, Z1 = x0 - 1, z0 - 1, x1 + 1, z1 + 1
        fachwerk(w, X0, Z0, X1, Z1, yo, yo + 3, M(w, S["fuell"]), holz=holz, abstand=2)
        boden(w, X0 + 1, Z0 + 1, X1 - 1, Z1 - 1, yo, holz)
        fensterreihe(w, X0, Z0, X1, Z1, yo + 1, ("north", "south", "east", "west"), abstand=3, holz=holz,
                     blumen=0.5)
        if balk and k == 1:
            balkon(w, cx - 1, cx + 1, Z1, yo, "south", holz=holz)
        yo += 4
    fx = first_x if first_x is not None else (X1 - X0) >= (Z1 - Z0)
    first = satteldach(w, X0, Z0, X1, Z1, yo, Dachmat(w, S["dach"]), first_x=fx, ue=1, giebel=M(w, S["fuell"]),
                       traufe=holz, steil=steil)
    if schorn:
        kamin(w, X1 - 2, Z0 + 1, yo, (first or yo + 4) + 1, M(w, S["sockel"]))
    return first


def bepflanzen(w, oben, dichte=0.35, baeume=0, macher=None, abstand=5):
    rng = w.rng
    gras = w.b("grass_block", snowy=False)
    zellen = [(x, z, y) for (x, z), y in oben.items() if w.bloecke.get((x, y, z)) == gras and w.frei(x, y + 1, z)]
    for (x, z, y) in zellen:
        r = rng.random()
        if r < dichte * 0.5:
            w.setze(x, y + 1, z, w.b("grass"))
        elif r < dichte * 0.6:
            w.setze(x, y + 1, z, w.b("fern"))
        elif r < dichte * 0.75:
            w.setze(x, y + 1, z, w.b(["poppy", "dandelion", "oxeye_daisy", "azure_bluet", "cornflower", "allium"]
                                     [int(rng.random() * 6)]))
        elif r < dichte * 0.8:
            busch(w, x, y + 1, z, 1.0 + rng.random(), "oak" if rng.random() < 0.6 else "azalea")
    rng.shuffle(zellen)
    gesetzt = []
    for (x, z, y) in zellen:
        if len(gesetzt) >= baeume:
            break
        if any(math.hypot(x - a, z - b) < abstand for a, b in gesetzt):
            continue
        if not all(w.frei(x + dx, y + h, z + dz) for h in (1, 4, 7) for dx, dz in ((0, 0), (2, 0), (-2, 0), (0, 2),
                                                                                    (0, -2))):
            continue
        sd = int(rng.integers(1, 10 ** 6))
        einfuegen(w, (macher or (lambda s: wald2.laubbaum(s, "oak", H=6)))(sd), x, y, z)
        gesetzt.append((x, z))


def fertig(w, sch, oben, dichte=0.35, baeume=0, macher=None):
    bepflanzen(w, oben, dichte, baeume, macher)
    unterseite(w, sch, 0.08)
    return w


def rundturm(w, cx, cz, y0, R, H, wand, dm, form="glocke", fenster_alle=4, holz="spruce", innen=None):
    for y in range(y0 - 3, y0 + H):
        for x in range(cx - R - 1, cx + R + 2):
            for z in range(cz - R - 1, cz + R + 2):
                d = math.hypot(x - cx, z - cz)
                if d > R + 0.45:
                    continue
                if y < y0:
                    w.setze(x, y, z, wand(x, y, z))
                elif d > R - 0.75:
                    fen = (y - y0) % fenster_alle in (1, 2) and (x == cx or z == cz) and y > y0 + 2
                    if fen:
                        rz = x == cx
                        w.setze(x, y, z, w.b("glass_pane", east=rz, west=rz, north=not rz, south=not rz,
                                             waterlogged=False))
                    else:
                        w.setze(x, y, z, wand(x, y, z))
                elif innen and d > R - 1.75:
                    w.setze(x, y, z, innen(x, y, z))
                else:
                    w.bloecke.pop((x, y, z), None)
    for x in range(cx - R - 2, cx + R + 3):
        for z in range(cz - R - 2, cz + R + 3):
            d = math.hypot(x - cx, z - cz)
            if R - 0.5 < d <= R + 1.3:
                w.setze(x, y0 + H, z, stamm(w, holz, "y") if d > R + 0.6 else w.b(f"{holz}_planks"))
    return kegeldach(w, cx, cz, y0 + H + 1, R, dm, form=form)


def eckturm(w, cx, cz, y0, r, H, wand, dm, form="kegel", zinnen=True):
    for y in range(y0 - 3, y0 + H):
        for x in range(cx - r, cx + r + 1):
            for z in range(cz - r, cz + r + 1):
                rand = abs(x - cx) == r or abs(z - cz) == r
                if rand or y < y0:
                    w.setze(x, y, z, wand(x, y, z))
    if dm:
        return kegeldach(w, cx, cz, y0 + H, r, dm, form=form, eckig=True)
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            if (abs(x - cx) == r or abs(z - cz) == r) and (x + z) % 2 == 0:
                w.setze(x, y0 + H, z, wand(x, y0 + H, z))
            w.setze(x, y0 + H - 1, z, wand(x, y0, z)) if not (abs(x - cx) == r or abs(z - cz) == r) else None
    return y0 + H


# ============================================================================ Inseln

def himmelsdom(seed, g=2):
    """Himmelsdom: eine gotische Kirche mit steilem Schieferdach, hohen bunten Spitzbogenfenstern und einem
    Westturm mit Nadelhelm, davor ein Kirchhof mit Laternen und Linden."""
    w, sch, R, top, oben = basis(seed, g, flach=0.8)
    L = [11, 15, 19, 25][g]
    B = [7, 7, 9, 11][g]
    y0 = platz(w, oben, 1, 0, L + 6, B + 2, top)
    x0, x1 = 1 - L // 2 + 2, 1 + L // 2 + 2
    z0, z1 = -B // 2, B // 2
    st = M(w, [("stone_bricks", 3), ("calcite", 1), ("andesite", 1), ("cracked_stone_bricks", 1)])
    hw = 6 + g
    mauer(w, x0, z0, x1, z1, y0, y0 + hw, st, ecke=M(w, [("polished_andesite", 1)]))
    boden(w, x0 + 1, z0 + 1, x1 - 1, z1 - 1, y0 - 1, "spruce")
    for x in range(x0 + 2, x1 - 1, 3):
        for z, s in ((z0, "north"), (z1, "south")):
            fenster(w, x, y0 + 2, z, s, holz="spruce", hoehe=hw - 3, glas="blue_stained_glass_pane", laeden=False,
                    blumen=0, bogen=True)
            for y in range(y0, y0 + hw):
                w.setze(x - 1 if x - 1 > x0 else x + 1, y, z + (-1 if s == "north" else 1), st(x, y, z), False) \
                    if (x - x0) % 6 == 2 else None
    satteldach(w, x0, z0, x1, z1, y0 + hw + 1, Dachmat(w, ["deepslate_tile", "cobbled_deepslate", "deepslate_brick"]),
               first_x=True, ue=1, giebel=st, traufe="dark_oak", steil=2)
    tx = x0 - 3
    r = 2 + (g > 1)
    eckturm(w, tx, 0, y0, r, hw + 6 + g * 2, st, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]), form="nadel")
    tuer(w, tx - r, y0, 0, "west", holz="dark_oak", laternen=True)
    for y in (y0 + hw + 2, y0 + hw + 3):
        for (dx, dz, s) in ((r, 0, "east"), (-r, 0, "west"), (0, r, "south"), (0, -r, "north")):
            w.setze(tx + dx, y, dz, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                        waterlogged=False))
    w.setze(tx, y0 + hw + 2, 0, w.b("bell", attachment="ceiling", facing="north", powered=False))
    for k in range(4):
        a = k * 1.57 + 0.6
        x, z = round(math.cos(a) * R * 0.7), round(math.sin(a) * R * 0.7)
        if (x, z) in oben and w.frei(x, oben[(x, z)] + 1, z):
            laternenpfahl(w, x, oben[(x, z)], z)
    return fertig(w, sch, oben, 0.35, 1 + g // 2, lambda s: wald2.laubbaum(s, "oak", H=6 + g))


def bibliotheksturm(seed, g=2):
    """Bibliotheksturm: ein runder, mehrstöckiger Turm aus hellem Stein mit Bücherregalen hinter den Fenstern,
    blauem Glockenhelm und Leseerker, daneben ein kleines Schreiberhaus."""
    w, sch, R, top, oben = basis(seed, g)
    Rt = [3, 4, 5, 6][g]
    y0 = platz(w, oben, -2, 0, 2 * Rt + 3, 2 * Rt + 3, top)
    wand = M(w, [("calcite", 3), ("smooth_quartz", 1), ("diorite", 1)])
    regal = lambda x, y, z: w.b("bookshelf") if (y % 4) else w.b("spruce_planks")
    rundturm(w, -2, 0, y0, Rt, 10 + g * 4, wand, Dachmat(w, ["mcw:blue_terracotta", "mcw:light_blue_terracotta",
                                                             "deepslate_tile"]), innen=regal)
    tuer(w, -2, y0, Rt, "south", holz="spruce")
    for k in range(g + 1):
        y = y0 + 4 + k * 4
        balkon(w, -3, -1, -Rt, y, "north", holz="spruce", tiefe=1)
    if g >= 1:
        hx = Rt + 4
        y1 = platz(w, oben, hx, 1, 7, 6, top)
        haus(w, hx, 1, 7, 6, y1, "blau", geschosse=1 + (g > 1), tuer_s="south")
    return fertig(w, sch, oben, 0.4, g, lambda s: wald2.birke(s))


def sternwarte(seed, g=2):
    """Sternwarte: ein Rundbau mit weißer Kuppel, Beobachtungsspalt und herausragendem Kupferteleskop, daneben ein
    Sonnenuhr-Platz und ein Gelehrtenhaus."""
    w, sch, R, top, oben = basis(seed, g)
    Rk = [3, 4, 5, 7][g]
    y0 = platz(w, oben, 0, 0, 2 * Rk + 3, 2 * Rk + 3, top)
    wand = M(w, [("stone_bricks", 2), ("polished_andesite", 1)])
    rundturm(w, 0, 0, y0, Rk, 4 + g, wand, None.__class__ and Dachmat(w, ["stone_brick"]), form="kegel") if False \
        else None
    for y in range(y0 - 3, y0 + 4 + g):
        for x in range(-Rk - 1, Rk + 2):
            for z in range(-Rk - 1, Rk + 2):
                d = math.hypot(x, z)
                if d <= Rk + 0.4 and (d > Rk - 0.8 or y < y0):
                    w.setze(x, y, z, wand(x, y, z))
    yk = y0 + 4 + g
    for x in range(-Rk - 1, Rk + 2):
        for y in range(0, Rk + 2):
            for z in range(-Rk - 1, Rk + 2):
                d = math.sqrt(x * x + y * y + z * z)
                if Rk - 0.9 < d <= Rk + 0.3:
                    spalt = abs(x) <= 0 and z > 0
                    if not spalt:
                        w.setze(x, yk + y, z, w.b("white_concrete" if (y + z) % 5 else "smooth_quartz"))
    for k in range(Rk + 4):
        x, y, z = 0, yk + 1 + round(k * 0.7), round(k * 0.7)
        for dx in (0, 1) if k > 2 else (0,):
            w.setze(x + dx, y, z, w.b("waxed_cut_copper" if k < Rk + 3 else "waxed_copper_block"))
    for (dx, dz, s) in ((Rk, 0, "east"), (-Rk, 0, "west")):
        fenster(w, dx, y0 + 1, dz, s, holz="spruce", blumen=0.3)
    tuer(w, 0, y0, Rk, "south", holz="spruce")
    sx, sz = round(-R * 0.45), round(R * 0.4)
    if (sx, sz) in oben:
        ys = oben[(sx, sz)]
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if dx * dx + dz * dz <= 5:
                    w.setze(sx + dx, ys, sz + dz, w.b("smooth_stone"))
        w.setze(sx, ys + 1, sz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    if g >= 2:
        y1 = platz(w, oben, round(R * 0.5), -round(R * 0.3), 7, 6, top)
        haus(w, round(R * 0.5), -round(R * 0.3), 7, 6, y1, "stein", geschosse=2, tuer_s="west")
    return fertig(w, sch, oben, 0.35, 1, lambda s: wald2.fichte(s))


def teehaus(seed, g=2):
    """Teehaus-Insel: ein Pavillon mit zwei geschwungenen Dachstufen auf roten Säulen, ein Koiteich mit
    Mondbrücke, Steinlaternen und Kirschbäume."""
    w, sch, R, top, oben = basis(seed, g, flach=0.8)
    B = [5, 7, 9, 11][g]
    y0 = platz(w, oben, -1, -1, B + 2, B + 2, top)
    h = B // 2
    for x in range(-1 - h, -1 + h + 1):
        for z in range(-1 - h, -1 + h + 1):
            w.setze(x, y0 - 1, z, w.b("spruce_planks"))
    for (x, z) in ((-1 - h, -1 - h), (-1 + h, -1 - h), (-1 - h, -1 + h), (-1 + h, -1 + h)):
        for y in range(y0, y0 + 4):
            w.setze(x, y, z, w.b("red_concrete" if y < y0 + 3 else "stripped_dark_oak_log", axis="y")
                    if y < y0 + 3 else w.b("stripped_dark_oak_log", axis="y"))
    for x in range(-h, h - 1):
        for z in (-1 - h + 1, -1 + h - 1):
            for y in range(y0, y0 + 3):
                if z == -1 + h - 1 and abs(x + 1) <= 1:
                    continue
                w.setze(x, y, z, w.b("white_wool") if y > y0 else w.b("spruce_planks"))
    dm = Dachmat(w, ["dark_oak", "spruce", "deepslate_tile"])
    satteldach(w, -1 - h, -1 - h, -1 + h, -1 + h, y0 + 4, dm, first_x=True, ue=2, ue_giebel=2, traufe="dark_oak")
    teich_c = (round(R * 0.4), round(R * 0.35))
    rt = max(2, R * 0.25)
    for (x, z), y in list(oben.items()):
        if math.hypot((x - teich_c[0]) / 1.3, z - teich_c[1]) < rt:
            w.setze(x, y, z, w.b("water", level=0))
            w.setze(x, y - 1, z, w.b("clay"))
            if w.rng.random() < 0.12:
                w.setze(x, y + 1, z, w.b("lily_pad"))
    for k in range(3):
        a = 2.2 + k * 1.1
        x, z = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        if (x, z) in oben:
            y = oben[(x, z)]
            for i, n in enumerate(["stone_bricks", "stone_brick_wall", "lantern", "stone_brick_slab"]):
                kw = {"up": True, "north": "none", "south": "none", "east": "none", "west": "none",
                      "waterlogged": False} if "wall" in n else {"hanging": False, "waterlogged": False} \
                    if n == "lantern" else {"type": "bottom", "waterlogged": False} if "slab" in n else {}
                w.setze(x, y + 1 + i, z, w.b(n, **kw))
    return fertig(w, sch, oben, 0.3, 2 + g, lambda s: wald2.kirschbaum(s))


def himmelsleuchtturm(seed, g=2):
    """Himmelsleuchtturm: ein schlanker rot-weißer Turm mit Laternenhaus weist Luftschiffen den Weg, am Fuß das
    Wärterhaus mit Fachwerk-Obergeschoss und ein Anlegesteg in die Wolken."""
    from inseln2 import leuchtturm
    w, sch, R, top, oben = basis(seed, g)
    y0 = platz(w, oben, -round(R * 0.3), 0, 7, 7, top)
    leuchtturm(w, -round(R * 0.3), y0 - 1, 0, H=12 + g * 6, r=2 + (g > 1))
    if g >= 1:
        hx = round(R * 0.35)
        y1 = platz(w, oben, hx, 0, 7, 6, top)
        haus(w, hx, 0, 7, 6, y1, "fachwerk", geschosse=2, tuer_s="west")
    rand = max(x for (x, z) in oben if abs(z) <= 1)
    for k in range(6 + g * 2):
        for dz in (-1, 0, 1):
            w.setze(rand + k, top, dz, w.b("spruce_planks"))
        if k % 3 == 0:
            for dz in (-1, 1):
                w.setze(rand + k, top + 1, dz, zaun(w, "spruce"))
                w.setze(rand + k, top - 1, dz, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                                   waterlogged=False))
    return fertig(w, sch, oben, 0.35, g)


def glockenturm(seed, g=2):
    """Glockenturm-Insel: ein quadratischer Campanile mit offener Glockenstube, Bögen und Pyramidendach, unten ein
    Platz mit Bänken und zwei Bürgerhäusern."""
    w, sch, R, top, oben = basis(seed, g)
    r = [2, 2, 3, 3][g]
    H = 12 + g * 5
    y0 = platz(w, oben, 0, 0, 2 * r + 3, 2 * r + 3, top)
    st = M(w, [("bricks", 3), ("stone_bricks", 1), ("granite", 1)])
    for y in range(y0 - 3, y0 + H):
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                if abs(x) == r or abs(z) == r or y < y0:
                    offen = y >= y0 + H - 4 and abs(x) < r and abs(z) < r
                    offen = y >= y0 + H - 4 and not (abs(x) == r and abs(z) == r)
                    if not offen:
                        w.setze(x, y, z, st(x, y, z))
    for x in range(-r - 1, r + 2):
        for z in range(-r - 1, r + 2):
            w.setze(x, y0 + H - 5, z, w.b("stone_bricks") if abs(x) <= r and abs(z) <= r else
                    treppe(w, "stone_brick", GEGEN["north" if z < -r else "south" if z > r else "west" if x < -r
                                                    else "east"], "top"))
    w.setze(0, y0 + H - 1, 0, w.b("bell", attachment="ceiling", facing="north", powered=False))
    kegeldach(w, 0, 0, y0 + H, r, Dachmat(w, ["mcw:orange_terracotta", "brick", "granite"]), form="kegel", eckig=True)
    tuer(w, 0, y0, r, "south", holz="dark_oak")
    if g >= 1:
        for k, (hx, hz, s) in enumerate(((-round(R * 0.5), round(R * 0.2), "east"),
                                         (round(R * 0.5), -round(R * 0.15), "west"))[: 1 + (g > 1)]):
            y1 = platz(w, oben, hx, hz, 7, 7, top)
            haus(w, hx, hz, 7, 7, y1, ["terrakotta", "fachwerk"][k], geschosse=2, tuer_s=s, balk=True)
    return fertig(w, sch, oben, 0.3, g)


def weinberg(seed, g=2):
    """Weinberg-Insel: Rebzeilen an Holzpfählen ziehen sich in Terrassen um einen Hügel, oben ein Kelterhaus mit
    Fässern, Weinpresse und Pergola."""
    w, sch, R, top, oben = basis(seed, g, flach=0.5)
    rng = w.rng
    for (x, z), y in list(oben.items()):
        d = math.hypot(x, z)
        if d < R * 0.85 and d > 4:
            yy = y + int((1 - d / R) * (2 + g))
            for k in range(y + 1, yy + 1):
                w.setze(x, k, z, w.b("dirt") if k < yy else w.b("grass_block", snowy=False))
            oben[(x, z)] = yy
    for (x, z), y in oben.items():
        d = math.hypot(x, z)
        if 4 < d < R * 0.8 and x % 3 == 0:
            w.setze(x, y, z, w.b("farmland", moisture=7) if False else w.b("coarse_dirt"))
            if z % 4 == 0:
                w.setze(x, y + 1, z, zaun(w, "spruce"))
                w.setze(x, y + 2, z, zaun(w, "spruce"))
            else:
                w.setze(x, y + 1, z, w.b("sweet_berry_bush", age=3))
                if rng.random() < 0.6:
                    w.setze(x, y + 2, z, w.b("azalea_leaves" if rng.random() < 0.7 else "flowering_azalea_leaves",
                                             persistent=True, distance=1, waterlogged=False))
    y1 = platz(w, oben, 0, 0, 7, 6, top + 2)
    haus(w, 0, 0, 7, 6, y1, "terrakotta", geschosse=1 + (g > 0), tuer_s="south")
    kram(w, 4, y1, 3, 5)
    for x in range(-3, 4):
        w.setze(x, y1 + 3, 4, w.b("spruce_slab", type="top", waterlogged=False), False)
        if x % 3 == 0:
            for y in range(y1, y1 + 3):
                w.setze(x, y, 4 + 2, zaun(w, "spruce"))
    return fertig(w, sch, oben, 0.2, 0)


def badehaus(seed, g=2):
    """Badehaus-Insel: dampfende Becken in Terrassen aus hellem Stein, Wasser fällt von Becken zu Becken und über
    den Inselrand, daneben ein Badehaus mit Säulenhalle."""
    w, sch, R, top, oben = basis(seed, g, flach=0.85)
    rng = w.rng
    for k, (cx, cz, r) in enumerate(((-R * 0.3, -R * 0.2, R * 0.25 + 1), (R * 0.15, R * 0.25, R * 0.2 + 1),
                                     (R * 0.5, -R * 0.05, R * 0.15 + 1))):
        yb = top + 2 - k
        for x in range(int(cx - r) - 2, int(cx + r) + 3):
            for z in range(int(cz - r) - 2, int(cz + r) + 3):
                d = math.hypot(x - cx, z - cz)
                if d <= r + 1:
                    for y in range(top - 2, yb + 1):
                        w.setze(x, y, z, w.b("calcite" if d > r else "smooth_stone") if y < yb or d > r else
                                w.b("water", level=0))
                    if d > r:
                        w.setze(x, yb + 1, z, platte(w, "smooth_stone"))
                    elif rng.random() < 0.03:
                        w.setze(x, yb - 1, z, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                  waterlogged=False))
                    oben[(x, z)] = yb + 1 if d > r else yb
    if g >= 1:
        hx = -round(R * 0.15)
        hz = round(R * 0.55)
        y1 = platz(w, oben, hx, hz, 9, 6, top)
        haus(w, hx, hz, 9, 6, y1, "kupfer", geschosse=1 + (g > 1), tuer_s="north")
        for x in range(hx - 4, hx + 5, 2):
            for y in range(y1, y1 + 3):
                w.setze(x, y, hz - 4, w.b("quartz_pillar", axis="y"))
            w.setze(x, y1 + 3, hz - 4, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
    return fertig(w, sch, oben, 0.3, 1, lambda s: wald2.birke(s))


def ballon(w, cx, y, cz, r, farben):
    for dx in range(-r - 1, r + 2):
        for dy in range(-r - 1, int(r * 1.3) + 2):
            for dz in range(-r - 1, r + 2):
                d = math.sqrt(dx * dx + (dy / 1.25 if dy > 0 else dy) ** 2 + dz * dz)
                if r - 1 < d <= r:
                    a = math.atan2(dz, dx)
                    w.setze(cx + dx, y + dy, cz + dz, w.b(farben[int((a + math.pi) / (2 * math.pi) * 8) % 2]))
    yk = y - r - 3
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(cx + dx, yk, cz + dz, w.b("spruce_planks") if (dx or dz) else w.b("barrel", facing="up",
                                                                                  open=False))
            if dx and dz:
                w.setze(cx + dx, yk + 1, cz + dz, zaun(w, "spruce"))
                for k in range(yk + 2, y - r + 1):
                    w.setze(cx + dx, k, cz + dz, w.b("chain", axis="y", waterlogged=False))
    w.setze(cx, yk + 1, cz, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return yk


def ballonstation(seed, g=2):
    """Ballonstation: an einem Holzsteg mit Pollern liegen bunt gestreifte Heißluftballons mit Weidenkörben vertäut,
    dazu das Stationshaus mit Wetterfahne und Kisten."""
    w, sch, R, top, oben = basis(seed, g)
    y1 = platz(w, oben, -round(R * 0.25), 0, 7, 7, top)
    haus(w, -round(R * 0.25), 0, 7, 7, y1, "kupfer", geschosse=2 if g else 1, tuer_s="east")
    rand = max(x for (x, z) in oben if abs(z) <= 1)
    L = 8 + g * 4
    for k in range(L):
        for dz in range(-2, 3):
            w.setze(rand + k, top, dz, w.b("spruce_planks"))
        for dz in (-3, 3):
            if k % 4 == 0:
                w.setze(rand + k, top + 1, dz - (1 if dz < 0 else -1), stamm(w, "spruce", geschaelt=False))
            w.setze(rand + k, top - 1, dz - (1 if dz < 0 else -1), treppe(w, "spruce", "north" if dz > 0 else "south",
                                                                         "top"), False)
    farben = [("red_wool", "white_wool"), ("yellow_wool", "blue_wool"), ("lime_wool", "orange_wool")]
    for k in range(1 + (g > 0) + (g > 2)):
        r = 3 + g
        bx, bz = rand + 4 + k * (2 * r + 3), (r + 3) * (1 if k % 2 else -1)
        yk = ballon(w, bx, top + r + 6, bz, r, farben[k % 3])
        for i in range(abs(bz) - 2):
            w.setze(bx, top + 1, (bz - (1 if bz > 0 else -1) * (i + 2)), w.b("chain", axis="z", waterlogged=False))
    kram(w, rand - 2, top + 1, 2, 4)
    return fertig(w, sch, oben, 0.3, g)


def gewaechshaus(w, cx, cz, y0, B, T):
    x0, z0 = cx - B // 2, cz - T // 2
    x1, z1 = x0 + B - 1, z0 + T - 1
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, y0 - 1, z, w.b("stone_bricks") if x in (x0, x1) or z in (z0, z1) else w.b("rooted_dirt"))
    r = (T - 1) / 2
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            u = z - (z0 + r)
            hy = int(math.sqrt(max(0, r * r - u * u)) * 0.9) + 2
            rahmen = x in (x0, x1) or (x - x0) % 3 == 0
            for y in range(y0, y0 + hy + 1):
                aussen = y == y0 + hy or x in (x0, x1) or z in (z0, z1)
                if aussen:
                    w.setze(x, y, z, stamm(w, "birch", "z") if rahmen and y == y0 + hy and x not in (x0, x1) else
                            w.b("white_stained_glass") if (x + y) % 5 == 0 else w.b("glass"))
    rng = w.rng
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            if z == z0 + int(r):
                continue
            n = ["red_tulip", "orange_tulip", "allium", "blue_orchid", "fern", "azalea", "flowering_azalea",
                 "lily_of_the_valley"][int(rng.random() * 8)]
            w.setze(x, y0, z, w.b(n))
    for y in (y0, y0 + 1):
        w.bloecke.pop((x0, y, z0 + int(r)), None)
    w.setze(x0, y0, z0 + int(r), w.b("birch_door", facing="west", half="lower", hinge="left", open=False,
                                     powered=False))
    w.setze(x0, y0 + 1, z0 + int(r), w.b("birch_door", facing="west", half="upper", hinge="left", open=False,
                                         powered=False))


def gewaechshausinsel(seed, g=2):
    """Gewächshaus-Insel: zwei Glashäuser mit gewölbten Dächern voller Blumen und Farne, dazwischen Beete,
    Gießkannen-Brunnen und ein Gärtnerhaus."""
    w, sch, R, top, oben = basis(seed, g, flach=0.85)
    n = 1 + (g > 0)
    for k in range(n):
        B, T = 7 + g * 2, 5 + 2 * (g > 1)
        cx, cz = -round(R * 0.15), (k * 2 - (n - 1)) * (T // 2 + 2)
        y0 = platz(w, oben, cx, cz, B, T, top)
        gewaechshaus(w, cx, cz, y0, B, T)
    if g >= 2:
        y1 = platz(w, oben, round(R * 0.5), 0, 6, 7, top)
        haus(w, round(R * 0.5), 0, 6, 7, y1, "fachwerk", geschosse=2, tuer_s="west")
    rng = w.rng
    for (x, z), y in oben.items():
        if w.frei(x, y + 1, z) and x % 2 == 0 and abs(z) > 2 and rng.random() < 0.5:
            w.setze(x, y, z, w.b("farmland", moisture=7))
            w.setze(x, y + 1, z, w.b(["carrots", "potatoes", "beetroots", "wheat"][int(rng.random() * 4)],
                                     age=3 if rng.random() < 0.5 else 7))
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if n in ("minecraft:beetroots",):
            w.bloecke[(x, y, z)] = w.b("beetroots", age=3)
        elif n in ("minecraft:carrots", "minecraft:potatoes", "minecraft:wheat"):
            w.bloecke[(x, y, z)] = w.b(n.split(":")[1], age=7)
    return fertig(w, sch, oben, 0.25, 1)


def schmiede(seed, g=2):
    """Himmelsschmiede: eine steinerne Werkstatt mit offener Front, glühender Esse und hohem Schlot, Amboss,
    Schleifstein und Wasserfass, Holzstapel und ein Wohnhaus daneben."""
    w, sch, R, top, oben = basis(seed, g)
    B, T = 9, 7
    y0 = platz(w, oben, -1, 0, B, T, top)
    x0, z0, x1, z1 = -1 - B // 2, -T // 2, -1 - B // 2 + B - 1, -T // 2 + T - 1
    st = M(w, [("cobblestone", 2), ("stone_bricks", 2), ("andesite", 1), ("mossy_cobblestone", 1)])
    sockel(w, x0, z0, x1, z1, y0 - 2, 2, st)
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, y0 - 1, z, w.b("polished_andesite" if (x + z) % 2 else "andesite"))
            if x in (x0, x1) or z == z0:
                for y in range(y0, y0 + 4):
                    w.setze(x, y, z, st(x, y, z))
            elif z == z1 and x in (x0 + 3, x1 - 3):
                for y in range(y0, y0 + 4):
                    w.setze(x, y, z, stamm(w, "spruce"))
    satteldach(w, x0, z0, x1, z1, y0 + 4, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]), first_x=True,
               traufe="spruce")
    kamin(w, x0 + 1, z0 + 1, y0, y0 + 10 + g * 2, st)
    w.setze(x0 + 2, y0, z0 + 3, w.b("lava_cauldron"))
    w.setze(x0 + 3, y0, z0 + 1, w.b("blast_furnace", facing="south", lit=True))
    w.setze(-1, y0, 0, w.b("anvil", facing="east"))
    w.setze(1, y0, z0 + 1, w.b("grindstone", face="floor", facing="south"))
    w.setze(2, y0, z0 + 1, w.b("water_cauldron", level=3))
    w.setze(x1 - 1, y0, z0 + 1, w.b("smithing_table"))
    for k in range(3):
        for j in range(3 - k):
            w.setze(x1 + 2, y0 + k, z0 + j * 1 + k, stamm(w, "oak", "x", geschaelt=False))
    if g >= 1:
        hx = round(R * 0.5)
        y1 = platz(w, oben, hx, 1, 7, 6, top)
        haus(w, hx, 1, 7, 6, y1, "stein", geschosse=2, tuer_s="west")
    return fertig(w, sch, oben, 0.25, g // 2)


def akademie(seed, g=2):
    """Akademie-Insel: ein U-förmiges Kollegiengebäude mit Fachwerk-Obergeschoss, Uhrgiebel und Arkaden um einen
    Innenhof mit Brunnen und Baum."""
    w, sch, R, top, oben = basis(seed, g, flach=0.85, rf=1.1)
    a = [5, 7, 9, 12][g]
    y0 = platz(w, oben, 0, 0, 2 * a + 5, 2 * a + 5, top)
    for (cx, cz, B, T, s) in ((0, -a, 2 * a + 5, 5, "south"), (-a, 1, 5, 2 * a - 1, "east"),
                              (a, 1, 5, 2 * a - 1, "west")):
        haus(w, cx, cz, B, T, y0, "fachwerk", geschosse=2, tuer_s=s, schorn=s == "south")
    for k in range(5):
        w.setze(0, y0 + 9 + k, -a - 3, w.b("stone_bricks"))
    w.setze(0, y0 + 11, -a - 4 + 6, w.b("white_concrete"), False)
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            w.setze(dx, y0 - 1, 2 + dz, w.b("stone_bricks"))
            if dx or dz:
                w.setze(dx, y0, 2 + dz, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                            west="none", waterlogged=False))
            else:
                w.setze(dx, y0, 2 + dz, w.b("water", level=0))
    for k in range(2):
        w.setze(0, y0 + k, 2, w.b("water", level=0)) if k == 0 else None
    return fertig(w, sch, oben, 0.3, 1 + g // 2)


def amphitheater(seed, g=2):
    """Amphitheater-Insel: halbrunde Sitzstufen aus Stein blicken auf eine Bühne mit Säulen, Vorhang und Fackeln,
    über allem der offene Himmel."""
    w, sch, R, top, oben = basis(seed, g, flach=0.9, rf=1.1)
    Ra = R * 0.75
    st = "stone_brick"
    for (x, z), y in list(oben.items()):
        d = math.hypot(x, z)
        if z >= -1 and d < Ra:
            stufe = int((d / Ra) * (4 + g * 2))
            for k in range(y + 1, top + stufe + 1):
                w.setze(x, k, z, w.b("stone_bricks"))
            if stufe > 1:
                a = math.atan2(z, x)
                f = "north" if abs(math.sin(a)) > abs(math.cos(a)) else ("west" if math.cos(a) > 0 else "east")
                w.setze(x, top + stufe + 1, z, treppe(w, st, GEGEN[{"north": "north", "west": "west",
                                                                    "east": "east"}[f]] if False else
                                                     {"north": "south", "west": "east", "east": "west"}[f]))
                w.setze(x, top + stufe + 1, z, treppe(w, st, {"north": "north", "west": "west", "east": "east"}[f]))
            oben[(x, z)] = top + stufe
    bw = int(Ra * 0.7)
    for x in range(-bw, bw + 1):
        for z in range(-int(Ra * 0.5), -1):
            w.setze(x, top + 1, z, w.b("spruce_planks"))
    for x in range(-bw, bw + 1, 3):
        for y in range(top + 2, top + 7):
            w.setze(x, y, -int(Ra * 0.5), w.b("quartz_pillar", axis="y"))
        w.setze(x, top + 7, -int(Ra * 0.5), w.b("chiseled_quartz_block"))
    for x in range(-bw, bw + 1):
        w.setze(x, top + 8, -int(Ra * 0.5), w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
        if x % 3:
            for y in range(top + 4, top + 7):
                w.setze(x, y, -int(Ra * 0.5), w.b("red_wool"))
    for x in (-bw - 1, bw + 1):
        w.setze(x, top + 2, -1, w.b("torch"))
    return fertig(w, sch, oben, 0.2, 1)


def brunnenplatz(seed, g=2):
    """Brunnenplatz: ein runder, gepflasterter Platz mit großem Springbrunnen, ringsum drei bis fünf Bürgerhäuser in
    verschiedenen Stilen, Laternen und Blumenkübel."""
    w, sch, R, top, oben = basis(seed, g, flach=0.9, rf=1.15)
    rp = max(3, R * 0.35)
    pfl = M(w, [("stone_bricks", 2), ("andesite", 1), ("polished_andesite", 1), ("cobblestone", 1)], zelle=1.0)
    for (x, z), y in oben.items():
        if math.hypot(x, z) <= rp:
            w.setze(x, top, z, pfl(x, top, z))
    for x in range(-3, 4):
        for z in range(-3, 4):
            d = math.hypot(x, z)
            if d <= 3.3:
                w.setze(x, top + 1, z, w.b("stone_bricks") if d > 2.4 else w.b("water", level=0))
    for y in range(top + 1, top + 4):
        w.setze(0, y, 0, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                             waterlogged=False))
    w.setze(0, top + 4, 0, w.b("water", level=0))
    n = [1, 3, 4, 5][g]
    stile = ["fachwerk", "terrakotta", "kupfer", "stein", "blau"]
    for k in range(n):
        a = k / n * 2 * math.pi + 0.4
        d = rp + 4
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        s = "west" if abs(math.cos(a)) > abs(math.sin(a)) and math.cos(a) > 0 else \
            "east" if abs(math.cos(a)) > abs(math.sin(a)) else "north" if math.sin(a) > 0 else "south"
        y1 = platz(w, oben, cx, cz, 7, 7, top)
        haus(w, cx, cz, 7, 7, y1, stile[k % 5], geschosse=2 + (g == 3 and k % 2 == 0), tuer_s=s, balk=k % 2 == 1)
    for k in range(4):
        a = k * 1.57 + 0.8
        x, z = round(math.cos(a) * (rp - 1)), round(math.sin(a) * (rp - 1))
        laternenpfahl(w, x, top, z)
    return fertig(w, sch, oben, 0.3, 0)


def wassermuehleninsel(seed, g=2):
    """Wassermühlen-Insel: aus einem Felsteich auf dem Hügel stürzt ein Bach über ein großes Wasserrad an der
    Mühle und weiter über den Inselrand in die Tiefe."""
    w, sch, R, top, oben = basis(seed, g)
    B, T = 7, 6
    y0 = platz(w, oben, 0, 0, B, T, top)
    haus(w, 0, 0, B, T, y0, "fachwerk", geschosse=2, tuer_s="south")
    rr = 3 + g
    wx = B // 2 + 2
    for k in range(int(rr * 7)):
        a = k / (rr * 7) * 2 * math.pi
        for r in range(rr + 1):
            x, y = round(math.cos(a) * r), round(math.sin(a) * r)
            if r == rr or (k % int(rr * 7 / 8) == 0):
                for dz in (-1, 0, 1):
                    w.setze(wx, y0 + 1 + y, dz, w.b("spruce_planks") if r == rr else stamm(w, "spruce", "x"))
    w.setze(wx - 1, y0 + 1, 0, stamm(w, "dark_oak", "x", False))
    for y in range(y0 + 1 + rr + 1, y0 + rr + 6):
        for dz in (-1, 0, 1):
            w.setze(wx, y, dz, w.b("water", level=0))
    for dz in (-1, 0, 1):
        for x in range(wx - 1, wx + 4):
            w.setze(x, y0 + rr + 5, dz, w.b("water", level=0))
            w.setze(x, y0 + rr + 4, dz, w.b("spruce_planks"))
    for x in range(wx + 3, wx + 8):
        for z in range(-3, 4):
            for y in range(y0 - 2, y0 + rr + 6):
                if abs(z) > 1 or x > wx + 5 or y < y0 + rr + 4:
                    w.setze(x, y, z, w.b(["stone", "mossy_cobblestone", "andesite"][(x + y + z) % 3]), False)
                elif y == y0 + rr + 5:
                    w.setze(x, y, z, w.b("water", level=0))
    rand_z = max(z for (x, z) in oben if abs(x - wx) <= 0) if any(abs(x - wx) <= 0 for (x, z) in oben) else 5
    for y in range(top - 8, y0):
        w.setze(wx, y, rand_z + 1, w.b("water", level=0))
    return fertig(w, sch, oben, 0.35, 1 + g // 2)


def taubentuerme(seed, g=2):
    """Taubentürme: schlanke hölzerne Taubenschläge auf hohen Pfählen mit spitzen Dächern und vielen Fluglöchern,
    dazwischen ein Gartenhaus und Blumenwiesen."""
    w, sch, R, top, oben = basis(seed, g)
    rng = w.rng
    n = 2 + g
    for k in range(n):
        a = k / n * 2 * math.pi + 0.3
        cx, cz = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        y0 = platz(w, oben, cx, cz, 3, 3, top)
        H = 5 + int(rng.random() * 4) + g
        for y in range(y0, y0 + H):
            w.setze(cx, y, cz, stamm(w, "spruce", geschaelt=False))
        yh = y0 + H
        for x in range(cx - 1, cx + 2):
            for z in range(cz - 1, cz + 2):
                for y in range(yh, yh + 3):
                    rand = x != cx or z != cz
                    if rand:
                        loch = y == yh + 1 and (x == cx or z == cz)
                        w.setze(x, y, z, w.b("air") if loch else w.b("white_terracotta" if y > yh else
                                                                    "spruce_planks"))
        kegeldach(w, cx, cz, yh + 3, 1, Dachmat(w, ["mcw:red_terracotta", "red_nether_brick", "brick"]),
                  form="nadel", eckig=True)
        for (dx, dz, f) in ((0, -2, "north"), (0, 2, "south"), (2, 0, "east"), (-2, 0, "west")):
            w.setze(cx + dx, yh, cz + dz, platte(w, "spruce", "top"), False)
    y1 = platz(w, oben, 0, 0, 6, 6, top)
    haus(w, 0, 0, 6, 6, y1, "blau", geschosse=1 + (g > 1), tuer_s="south")
    return fertig(w, sch, oben, 0.55, 0)


def herrenhaus(seed, g=2):
    """Herrenhaus-Insel: ein symmetrisches Herrenhaus mit Mittelrisalit, Balkon, zwei Seitenflügeln mit Turmhelmen
    und ein formaler Garten mit Hecken, Wegen und Springbrunnen."""
    w, sch, R, top, oben = basis(seed, g, flach=0.85, rf=1.15)
    B = [9, 13, 15, 19][g]
    y0 = platz(w, oben, 0, -round(R * 0.25), B + 4, 9, top)
    cz = -round(R * 0.25)
    haus(w, 0, cz, B, 7, y0, "kupfer", geschosse=3 if g >= 2 else 2, tuer_s="south", balk=True)
    if g >= 1:
        for sx in (-1, 1):
            tx = sx * (B // 2 + 2)
            eckturm(w, tx, cz, y0, 2, 9 + g * 2, M(w, [("calcite", 3), ("smooth_quartz", 1)]),
                    Dachmat(w, ["mcw:cyan_terracotta", "prismarine_brick", "dark_prismarine"]), form="glocke")
    gz = cz + 6
    for (x, z), y in oben.items():
        if z >= gz and abs(x) <= B // 2 + 1:
            if x == 0 or (z - gz) % 4 == 0:
                w.setze(x, y, z, w.b("gravel"))
            elif abs(x) == 1 or (z - gz) % 4 == 1:
                if w.frei(x, y + 1, z):
                    w.setze(x, y + 1, z, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
            elif w.frei(x, y + 1, z) and w.rng.random() < 0.6:
                w.setze(x, y + 1, z, w.b(["red_tulip", "white_tulip", "pink_tulip", "allium"][abs(x + z) % 4]))
    return fertig(w, sch, oben, 0.2, 2, lambda s: wald2.fichte(s, schmal=0.6))


def bogenbrueckeninseln(seed, g=2):
    """Bogenbrücken-Inseln: zwei schwebende Inseln sind durch eine steinerne Bogenbrücke mit Brüstung und Laternen
    verbunden, auf beiden stehen Häuser."""
    w = _welt(seed)
    sch = Schema(w)
    d = [12, 18, 26, 38][g]
    top = int(TG[g] * 1.9) + [10, 14, 18, 24][g]
    _, _, R, _, oben1 = basis(seed, g, rf=0.75, cx=-d, w=w, sch=sch, top=top)
    _, _, _, _, oben2 = basis(seed, g, rf=0.7, cx=d, w=w, sch=sch, top=top - 2)
    y1 = platz(w, oben1, -d, 0, 7, 6, top)
    haus(w, -d, 0, 7, 6, y1, "fachwerk", geschosse=2, tuer_s="east")
    y2 = platz(w, oben2, d, 0, 6, 6, top - 2)
    haus(w, d, 0, 6, 6, y2, "terrakotta", geschosse=1 + (g > 0), tuer_s="west")
    x0 = max(x for (x, z) in oben1 if abs(z) <= 1) - 1
    x1 = min(x for (x, z) in oben2 if abs(z) <= 1) + 1
    L = x1 - x0
    st = M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 1), ("cracked_stone_bricks", 1)])
    for i in range(L + 1):
        x = x0 + i
        t = i / L
        y = round(top + (top - 2 - top) * t + 2 * math.sin(math.pi * t))
        for dz in (-1, 0, 1):
            w.setze(x, y, dz, w.b("polished_andesite") if dz == 0 else st(x, y, dz))
            tief = round(3 * (1 - math.sin(math.pi * t) ** 0.5)) + 1
            for k in range(1, tief + 1):
                w.setze(x, y - k, dz, st(x, y - k, dz))
        for dz in (-2, 2):
            for k in range(0, 2):
                w.setze(x, y + k, dz, st(x, y, dz) if k == 0 else w.b("stone_brick_wall", up=False, north="none",
                                                                    south="none", east="low", west="low",
                                                                    waterlogged=False))
            if i % 5 == 0:
                w.setze(x, y + 2, dz, w.b("lantern", hanging=False, waterlogged=False))
    oben = dict(oben1)
    oben.update(oben2)
    return fertig(w, sch, oben, 0.35, 1 + g // 2)


def treppeninseln(seed, g=2):
    """Treppeninseln: drei übereinander gestaffelte Inseln, verbunden durch einen Turm mit Wendeltreppe; jede
    Etage trägt ein Häuschen, einen Garten oder einen Aussichtspavillon."""
    w = _welt(seed)
    sch = Schema(w)
    rf = [0.7, 0.65, 0.6, 0.55][g]
    top = int(TG[g] * 1.9) + [10, 14, 18, 24][g]
    dy = [8, 11, 14, 18][g]
    dx = round(RG[g] * rf * 1.4)
    obens = []
    for k in range(3):
        cx = (k - 1) * dx
        _, _, R, _, ob = basis(seed + k, g, rf=rf, cx=cx, w=w, sch=sch, top=top + k * dy)
        obens.append((cx, top + k * dy, ob))
    for k, (cx, t, ob) in enumerate(obens):
        if k == 0:
            y1 = platz(w, ob, cx - 1, 0, 6, 6, t)
            haus(w, cx - 1, 0, 6, 6, y1, "fachwerk", geschosse=1 + (g > 1), tuer_s="south")
        elif k == 1:
            bepflanzen(w, ob, 0.7, 1)
        else:
            y1 = platz(w, ob, cx, 0, 5, 5, t)
            for (px, pz) in ((cx - 2, -2), (cx + 2, -2), (cx - 2, 2), (cx + 2, 2)):
                for y in range(y1, y1 + 3):
                    w.setze(px, y, pz, zaun(w, "dark_oak"))
            kegeldach(w, cx, 0, y1 + 3, 2, Dachmat(w, ["mcw:blue_terracotta", "deepslate_tile"]), form="glocke")
    sx, sz = (obens[0][0] + obens[1][0]) // 2, round(RG[g] * rf * 0.9)
    y_lo, y_hi = top - 2, top + 2 * dy + 2
    r = 2
    for y in range(y_lo, y_hi):
        for x in range(sx - r, sx + r + 1):
            for z in range(sz - r, sz + r + 1):
                rand = abs(x - sx) == r or abs(z - sz) == r
                if rand:
                    fen = (y % 4 == 0) and (x == sx or z == sz)
                    w.setze(x, y, z, w.b("glass_pane", east=x == sx, west=x == sx, north=z == sz, south=z == sz,
                                         waterlogged=False) if fen else w.b("stone_bricks"))
        ring = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
        ddx, ddz = ring[(y - y_lo) % 8]
        w.setze(sx + ddx, y, sz + ddz, w.b("smooth_stone_slab", type="top" if y % 2 else "bottom", waterlogged=False))
        w.setze(sx, y, sz, stamm(w, "spruce"))
    kegeldach(w, sx, sz, y_hi, r, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]), form="kegel", eckig=True)
    for k, (cx, t, ob) in enumerate(obens):
        for x in range(min(cx, sx), max(cx, sx) + 1):
            for z in range(0, sz - r + 1):
                if (x, z) not in ob and abs(x - sx) <= 1:
                    w.setze(x, t, z, w.b("spruce_planks"))
            if (x, sz - r) in ob or abs(x - sx) <= 1:
                pass
        for y in (t + 1, t + 2):
            w.bloecke.pop((sx, y, sz - r), None)
    oben = {}
    for _, _, ob in obens:
        oben.update(ob)
    return fertig(w, sch, oben, 0.35, 0)


def wachbastion(seed, g=2):
    """Wachbastion: eine Festungsinsel mit zinnenbewehrter Ringmauer, vier Rundtürmen, Torhaus mit Fallgitter,
    Wachstube und Fahnen über den Wolken."""
    w, sch, R, top, oben = basis(seed, g, flach=0.9, rf=1.1)
    a = int(R * 0.6)
    y0 = platz(w, oben, 0, 0, 2 * a + 3, 2 * a + 3, top)
    st = M(w, [("stone_bricks", 3), ("cobblestone", 1), ("andesite", 1), ("mossy_stone_bricks", 1)])
    hm = 4 + g
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if abs(x) == a or abs(z) == a:
                for y in range(y0 - 3, y0 + hm):
                    w.setze(x, y, z, st(x, y, z))
                if (x + z) % 2 == 0:
                    w.setze(x, y0 + hm, z, st(x, y0, z))
            elif abs(x) == a - 1 or abs(z) == a - 1:
                w.setze(x, y0 + hm - 2, z, w.b("spruce_planks"))
    dm = Dachmat(w, ["deepslate_tile", "cobbled_deepslate"])
    for (cx, cz) in ((-a, -a), (a, -a), (-a, a), (a, a)):
        rr = 2
        for y in range(y0 - 3, y0 + hm + 4):
            for x in range(cx - rr - 1, cx + rr + 2):
                for z in range(cz - rr - 1, cz + rr + 2):
                    d = math.hypot(x - cx, z - cz)
                    if rr - 0.7 < d <= rr + 0.4:
                        w.setze(x, y, z, st(x, y, z))
        kegeldach(w, cx, cz, y0 + hm + 4, rr, dm, form="kegel")
        w.setze(cx, y0 + hm + 4 + 6, cz, w.b("red_wool"), False)
    for y in range(y0, y0 + 3):
        for x in (-1, 0, 1):
            w.setze(x, y, a, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False)
                    if y > y0 or x == 0 else w.b("air"))
    for x in (-2, 2):
        for y in range(y0, y0 + hm + 3):
            w.setze(x, y, a + 1, st(x, y, a))
    y1 = y0
    haus(w, 0, -a + 4, min(2 * a - 3, 9), 5, y1, "stein", geschosse=2, tuer_s="south")
    return fertig(w, sch, oben, 0.2, 0)


HIMMELSSTADT2 = {
    "himmelsdom": ("Himmelsdom", himmelsdom),
    "bibliotheksturm": ("Bibliotheksturm", bibliotheksturm),
    "sternwarte": ("Sternwarte", sternwarte),
    "teehaus": ("Teehaus-Insel", teehaus),
    "himmelsleuchtturm": ("Himmelsleuchtturm", himmelsleuchtturm),
    "glockenturm": ("Glockenturm-Insel", glockenturm),
    "weinberg": ("Weinberg-Insel", weinberg),
    "badehaus": ("Badehaus-Insel", badehaus),
    "ballonstation": ("Ballonstation", ballonstation),
    "gewaechshausinsel": ("Gewächshaus-Insel", gewaechshausinsel),
    "schmiede": ("Himmelsschmiede", schmiede),
    "akademie": ("Akademie-Insel", akademie),
    "amphitheater": ("Amphitheater-Insel", amphitheater),
    "brunnenplatz": ("Brunnenplatz", brunnenplatz),
    "wassermuehleninsel": ("Wassermühlen-Insel", wassermuehleninsel),
    "taubentuerme": ("Taubentürme", taubentuerme),
    "herrenhaus": ("Herrenhaus-Insel", herrenhaus),
    "bogenbrueckeninseln": ("Bogenbrücken-Inseln", bogenbrueckeninseln),
    "treppeninseln": ("Treppeninseln", treppeninseln),
    "wachbastion": ("Wachbastion", wachbastion),
}

"""Instagram (detailliert) – eigene, sehr detaillierte Nachbauten von Bau-Ideen, die auf Instagram gesammelt wurden
(keine 1:1-Kopien). Jeder Bau steht auf einem Diorama-Sockel mit Wegen, Büschen, Steinen und Deko. Boden y = 0."""

from __future__ import annotations

import math

import wald2
from feinbau import (D, Dachmat, Mix, balkon, bepflanzen, busch, diorama, efeu, fachwerk, fenster, fensterreihe,
                     gaube, kamin, kegeldach, kragsteine, kram, laterne, mauer, platte, satteldach, sockel, stamm,
                     stein, treppe, treppe_gerade, tuer, weg, zaun)
from flora import _neu, _r, linie
from lib import einfuegen

SK = [0.7, 0.85, 1.0, 1.3]


def S(g, v, mind=1):
    return max(mind, int(round(v * SK[g])))


def steinmix(w, art="grau"):
    if art == "grau":
        return Mix(w, [("stone_bricks", 4), ("cobblestone", 2), ("mossy_stone_bricks", 1), ("andesite", 1),
                       ("cracked_stone_bricks", 1), ("mossy_cobblestone", 1)])
    if art == "dunkel":
        return Mix(w, [("deepslate_bricks", 4), ("cobbled_deepslate", 2), ("deepslate_tiles", 2),
                       ("polished_deepslate", 1), ("tuff", 1), ("mossy_cobblestone", 1)])
    if art == "hell":
        return Mix(w, [("stone_bricks", 3), ("andesite", 2), ("polished_andesite", 2), ("diorite", 1),
                       ("calcite", 1)])
    if art == "weiss":
        return Mix(w, [("calcite", 4), ("diorite", 2), ("smooth_quartz", 2), ("polished_diorite", 2),
                       ("white_terracotta", 1)])
    if art == "sand":
        return Mix(w, [("smooth_sandstone", 3), ("sandstone", 2), ("cut_sandstone", 2), ("end_stone", 1)])
    return art


def putz(w, art="weiss"):
    if art == "weiss":
        return Mix(w, [("white_terracotta", 2), ("calcite", 3), ("diorite", 1), ("smooth_quartz", 1)], zelle=1.5)
    if art == "ocker":
        return Mix(w, [("smooth_sandstone", 3), ("yellow_terracotta", 1), ("end_stone", 1), ("sandstone", 1)],
                   zelle=1.5)
    if art == "rot":
        return Mix(w, [("red_terracotta", 4), ("red_concrete", 1), ("red_nether_bricks", 1)], zelle=1.4)
    if art == "gruen":
        return Mix(w, [("moss_block", 2), ("green_terracotta", 3), ("lime_terracotta", 1)], zelle=1.4)
    return art


def deko_garten(w, zellen, n=6):
    rng = w.rng
    z = sorted(zellen)
    for k in range(n):
        x, zz = z[int(rng.random() * len(z))]
        if (x, 1, zz) in w.bloecke or (x, 0, zz) not in w.bloecke:
            continue
        r = rng.random()
        if r < 0.45:
            busch(w, x, 1, zz, 1.0 + rng.random() * 0.8, "oak" if rng.random() < 0.6 else "azalea",
                  blueten="flowering_azalea_leaves" if rng.random() < 0.4 else None)
        elif r < 0.75:
            stein(w, x, 0, zz, 0.9 + rng.random() * 0.8)
        else:
            w.setze(x, 1, zz, w.b("rose_bush", half="lower"))
            w.setze(x, 2, zz, w.b("rose_bush", half="upper"))


def rundmauer(w, cx, cz, r, y0, y1, M):
    for y in range(y0, y1 + 1):
        for x in range(cx - r - 1, cx + r + 2):
            for z in range(cz - r - 1, cz + r + 2):
                d = math.hypot(x - cx, z - cz)
                if r - 0.8 < d <= r + 0.45:
                    w.setze(x, y, z, M(x, y, z))


# ============================================================================ Bauten

def alchemistenturm(seed, g=2):
    """Alchemistenturm: ein Fachwerk-Laborhaus auf Steinsockel mit blauem Dach, dahinter ein eckiger Steinturm mit
    Holzgalerie, Laternen an Ketten, Fernrohr und hohem Glockenhelm. Unten Kessel mit grünem Gebräu, ein
    Glashaus voller Blumen, eine Treppe zum Obergeschoss, ein Seerosenteich und Leuchtpilze."""
    w = _neu(seed)
    R = S(g, 19, 12)
    zellen = diorama(w, R, art="wiese")
    st = steinmix(w, "grau")
    dm = Dachmat(w, ["mcw:blue_terracotta", "mcw:blue_terracotta", "mcw:light_blue_terracotta", "mcw:purple_terracotta"],
                 rand="mcw:blue_terracotta")
    holz = "dark_oak"
    a, b = S(g, 6, 4), S(g, 4, 3)
    mauer(w, -a, -b, a, b, 1, 5, st, ecke=w.b("polished_andesite"))
    for x in range(-a + 1, a):
        if (x + a) % 3 != 0:
            for y in range(1, 4):
                w.bloecke.pop((x, y, b), None)
            w.setze(x, 4, b, treppe(w, "stone_brick", "south", "top"))
    for x in range(-a + 1, a):
        for z in range(-b + 1, b):
            w.setze(x, 0, z, w.b("stone_bricks" if (x + z) % 2 else "polished_andesite"))
    for i, x in enumerate(range(-a + 2, a - 1, 3)):
        w.setze(x, 1, 0, w.b("water_cauldron", level=3))
        w.setze(x, 0, 0, w.b("magma_block"))
        w.setze(x, 2, 0, w.b(["lime_stained_glass", "purple_stained_glass", "magenta_stained_glass"][i % 3]))
        w.setze(x, 1, -b + 1, w.b("brewing_stand", has_bottle_0=True, has_bottle_1=i % 2 == 0, has_bottle_2=True))
        laterne(w, x, 4, -1, 1)
    fachwerk(w, -a - 1, -b - 1, a + 1, b + 1, 6, 10, putz(w, "weiss"), holz=holz, abstand=3)
    kragsteine(w, -a - 1, -b - 1, a + 1, b + 1, 5, holz)
    fensterreihe(w, -a - 1, -b - 1, a + 1, b + 1, 7, ("north", "south", "west"), abstand=3, holz=holz,
                 glas="purple_stained_glass_pane", blumen=0.3)
    balkon(w, -a + 1, a - 1, b + 1, 6, "south", holz=holz, tiefe=2)
    for x in range(-a + 1, a, 2):
        w.setze(x, 7, b + 2, w.b("brewing_stand", has_bottle_0=True, has_bottle_1=True, has_bottle_2=False), False)
    top = satteldach(w, -a - 1, -b - 1, a + 1, b + 1, 11, dm, first_x=True, ue=1, giebel=putz(w, "weiss"),
                     traufe=holz, steil=1)
    gaube(w, -2, 13, -b + 1, "north", dm, holz)
    kamin(w, -a + 1, -b, 6, top + 2, st)
    tx0, tz0 = a - 1, -b - S(g, 7, 5)
    ta = S(g, 5, 4)
    H = S(g, 17, 12)
    mauer(w, tx0, tz0, tx0 + ta, tz0 + ta, 1, H, st, ecke=w.b("polished_andesite"), gurt=H // 2)
    for y in range(3, H - 2, 4):
        fenster(w, tx0 + ta // 2, y, tz0 + ta, "south", holz=holz, laeden=False, blumen=0)
        fenster(w, tx0 + ta, y, tz0 + ta // 2, "east", holz=holz, laeden=False, blumen=0)
    for x in range(tx0 - 1, tx0 + ta + 2):
        for z in range(tz0 - 1, tz0 + ta + 2):
            w.setze(x, H + 1, z, w.b(f"{holz}_planks"))
            if x in (tx0 - 1, tx0 + ta + 1) or z in (tz0 - 1, tz0 + ta + 1):
                w.setze(x, H + 2, z, zaun(w, holz))
    kragsteine(w, tx0, tz0, tx0 + ta, tz0 + ta, H, holz, abstand=1)
    for (x, z) in ((tx0, tz0), (tx0 + ta, tz0), (tx0, tz0 + ta), (tx0 + ta, tz0 + ta)):
        for y in range(H + 2, H + 6):
            w.setze(x, y, z, stamm(w, holz))
    for x in range(tx0, tx0 + ta + 1):
        for z in range(tz0, tz0 + ta + 1):
            if (x in (tx0, tx0 + ta) or z in (tz0, tz0 + ta)) and not (x in (tx0, tx0 + ta) and z in (tz0, tz0 + ta)):
                w.setze(x, H + 2, z, w.b("bookshelf"))
                w.setze(x, H + 5, z, stamm(w, holz, "x" if z in (tz0, tz0 + ta) else "z"))
    laterne(w, tx0 - 1, H, tz0 - 1, 2, seele=True)
    laterne(w, tx0 + ta + 1, H, tz0 + ta + 1, 2, seele=True)
    w.setze(tx0 + ta + 1, H + 3, tz0 + 1, w.b("lightning_rod", facing="east", powered=False, waterlogged=False))
    w.setze(tx0 + ta + 2, H + 3, tz0 + 1, w.b("copper_block"))
    kegeldach(w, tx0 + ta // 2, tz0 + ta // 2, H + 6, ta / 2 + 0.6, dm, form="glocke", eckig=False, h=S(g, 14, 10))
    sx0 = -a - S(g, 7, 5)
    mauer(w, sx0, -b + 1, -a - 2, b, 1, 4, st)
    satteldach(w, sx0, -b + 1, -a - 2, b, 5, Dachmat(w, ["deepslate_tile", "cobbled_deepslate", "deepslate_brick"]),
               first_x=False, ue=1, giebel=st, traufe="spruce")
    fenster(w, sx0, 2, 0, "west", holz="spruce")
    tuer(w, (sx0 - a - 2) // 2, 1, b, "south", holz="spruce")
    treppe_gerade(w, -a + 1, 5, b + 3, "south", 5, breite=2, mat="spruce")
    gx0, gz0, gx1, gz1 = a + 2, 1, a + 2 + S(g, 6, 4), b + S(g, 5, 3)
    for x in range(gx0, gx1 + 1):
        for z in range(gz0, gz1 + 1):
            w.setze(x, 0, z, w.b("spruce_planks"))
            rand = x in (gx0, gx1) or z in (gz0, gz1)
            for y in range(1, 4):
                if rand:
                    pf = (x in (gx0, gx1) and z in (gz0, gz1)) or ((x - gx0) % 3 == 0 and z in (gz0, gz1))
                    w.setze(x, y, z, stamm(w, "spruce") if pf else w.b("glass"))
                elif y == 1:
                    if (x + z) % 3 == 0:
                        w.setze(x, 1, z, w.b("rose_bush", half="lower"))
                        w.setze(x, 2, z, w.b("rose_bush", half="upper"))
                    else:
                        w.setze(x, 1, z, w.b(["allium", "pink_tulip", "azure_bluet", "red_tulip"][(x * 3 + z) % 4]))
    gm = (gx0 + gx1) / 2
    for x in range(gx0, gx1 + 1):
        hh = round(4 + (gx1 - gx0) / 2 - abs(x - gm))
        for z in range(gz0, gz1 + 1):
            w.setze(x, hh, z, stamm(w, "spruce", "z") if (z - gz0) % 3 == 0 or x in (gx0, gx1) else w.b("glass"))
            for yy in range(4, hh):
                if z in (gz0, gz1):
                    w.setze(x, yy, z, w.b("glass"))
    for x in range(-a - 2, -a + 3):
        for z in range(b + 5, b + 9):
            if (x + a) ** 2 / 6 + (z - b - 7) ** 2 / 3 < 1.6:
                w.bloecke.pop((x, 1, z), None)
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("clay"))
                if w.rng.random() < 0.2:
                    w.setze(x, 1, z, w.b("lily_pad"))
    weg(w, [(0, b + 1), (1, b + 6), (3, R - 1)], breite=1.3)
    for (x, z) in ((-a - 4, b + 2), (-a - 5, b + 4), (a + 1, b + 7)):
        w.setze(x, 1, z, w.b("warped_fungus"))
        w.setze(x + 1, 1, z, w.b("shroomlight"))
    kram(w, a - 1, 1, b + 3, 3)
    bepflanzen(w, zellen, 0.4)
    deko_garten(w, zellen, n=8)
    efeu(w, 0.05, bis=12)
    return w


def tuerkis_gehoeft(seed, g=2):
    """Türkis-Gehöft: ein großes, verwinkeltes Fachwerkhaus auf grauem Steinsockel mit mehreren türkisen
    Prismarindächern, Gauben und Balkonen, daneben ein Rundturm mit offener Holzlaube und Schieferhelm; ein
    Wimpelseil spannt sich vom Turm zur Fahnenstange am First."""
    w = _neu(seed)
    R = S(g, 20, 13)
    zellen = diorama(w, R, art="wiese")
    st = steinmix(w, "grau")
    dm = Dachmat(w, ["prismarine_brick", "prismarine", "prismarine_brick", "dark_prismarine"], rand="dark_prismarine")
    holz = "spruce"
    a, b = S(g, 7, 5), S(g, 4, 3)
    sockel(w, -a, -b, a, b, 1, 3, st)
    mauer(w, -a, -b, a, b, 1, 4, st)
    fachwerk(w, -a - 1, -b - 1, a + 1, b + 1, 5, 9, putz(w, "weiss"), holz=holz, abstand=3)
    kragsteine(w, -a - 1, -b - 1, a + 1, b + 1, 4, holz)
    fensterreihe(w, -a - 1, -b - 1, a + 1, b + 1, 6, ("north", "south", "west", "east"), abstand=3, holz=holz,
                 blumen=0.6)
    fensterreihe(w, -a, -b, a, b, 2, ("south",), abstand=4, holz=holz, laeden=False, blumen=0)
    tuer(w, 0, 1, b, "south", holz=holz)
    top = satteldach(w, -a - 1, -b - 1, a + 1, b + 1, 10, dm, first_x=True, ue=1, giebel=putz(w, "weiss"),
                     traufe=holz, steil=1)
    for gx in range(-a + 2, a - 1, 4):
        gaube(w, gx, 12, b + 1, "south", dm, holz)
        gaube(w, gx, 12, -b - 1, "north", dm, holz)
    kamin(w, a - 2, -1, 9, top + 1, st)
    sa = S(g, 3, 2)
    sl = S(g, 5, 3)
    fachwerk(w, -a + 1, b + 2, -a + 1 + 2 * sa, b + 2 + sl, 1, 5, putz(w, "weiss"), holz=holz)
    fenster(w, -a + 1 + sa, 2, b + 2 + sl, "south", holz=holz)
    satteldach(w, -a + 1, b + 2, -a + 1 + 2 * sa, b + 2 + sl, 6, dm, first_x=False, ue=1, giebel=putz(w, "weiss"),
               traufe=holz)
    balkon(w, 1, a - 1, b + 1, 5, "south", holz=holz, tiefe=2)
    tx, tz = a + S(g, 5, 4), -1
    r = S(g, 3, 2)
    H = S(g, 15, 11)
    rundmauer(w, tx, tz, r, 1, H, st)
    for y in range(3, H - 2, 4):
        fenster(w, tx, y, tz + r, "south", holz=holz, laeden=False, blumen=0)
    for x in range(tx - r - 2, tx + r + 3):
        for z in range(tz - r - 2, tz + r + 3):
            d = math.hypot(x - tx, z - tz)
            if d <= r + 1.8:
                w.setze(x, H + 1, z, w.b(f"{holz}_planks"))
            if r + 0.8 < d <= r + 1.8:
                w.setze(x, H + 2, z, zaun(w, holz))
    for k in range(8):
        ang = k / 8 * 6.283
        x, z = tx + round(math.cos(ang) * (r + 1)), tz + round(math.sin(ang) * (r + 1))
        for y in range(H + 2, H + 6):
            w.setze(x, y, z, stamm(w, holz))
        if k % 2:
            laterne(w, x, H + 5, z, 1)
    spitze = kegeldach(w, tx, tz, H + 6, r + 1.5, Dachmat(w, ["deepslate_tile", "cobbled_deepslate",
                                                              "deepslate_brick"]), form="glocke", h=S(g, 12, 8))
    for y in range(spitze + 1, spitze + 4):
        w.setze(tx, y, tz, zaun(w, holz))
    for k in range(3):
        w.setze(tx + 1 + k // 2, spitze + 3 - k % 2, tz, w.b("red_wool"))
    fx = -a + 1
    for y in range(top, top + 4):
        w.setze(fx, y, 0, zaun(w, holz))
    w.setze(fx + 1, top + 3, 0, w.b("red_wool"))
    w.setze(fx + 2, top + 3, 0, w.b("red_wool"))
    n = 50
    for i in range(n + 1):
        t = i / n
        x = tx + (fx - tx) * t
        y = spitze + 2 + (top + 3 - spitze - 2) * t - 4 * 4 * t * (1 - t)
        zz = round(tz + (0 - tz) * t)
        w.setze(round(x), round(y), zz, w.b("spruce_fence", north=False, south=False, east=True, west=True,
                                            waterlogged=False), False)
    weg(w, [(0, b + 2), (0, R - 1)], breite=1.4, mats=(("cobblestone", 3), ("stone_bricks", 2), ("gravel", 1),
                                                     ("mossy_cobblestone", 1)))
    kram(w, a + 1, 1, b + 3, 4)
    bepflanzen(w, zellen, 0.35)
    deko_garten(w, zellen, n=10)
    efeu(w, 0.04, bis=8)
    return w


def hexenladen(seed, g=2):
    """Hexenladen: ein runder Turm aus dunklem Stein mit hohem, krumm geknicktem Hexenhut-Dach und breiter Krempe,
    windschiefe Fachwerkhäuschen daneben, ein Anbau unter einem Dach in Form eines riesigen Kürbisses mit Gesicht
    und Stiel, ein Marktstand mit gestreifter Markise, Kerzenhaufen, Kisten und moosige Dachbüschel."""
    w = _neu(seed)
    R = S(g, 17, 11)
    zellen = diorama(w, R, art="wald")
    st = steinmix(w, "dunkel")
    holz = "dark_oak"
    r = S(g, 4, 3)
    H = S(g, 13, 9)
    rundmauer(w, 0, 0, r, 1, H, st)
    for y in (H // 3, 2 * H // 3):
        for k in range(int((r + 1) * 6.4)):
            ang = k / int((r + 1) * 6.4) * 6.283
            w.setze(round(math.cos(ang) * (r + 1)), y, round(math.sin(ang) * (r + 1)),
                    stamm(w, holz, "x" if abs(math.cos(ang)) < 0.7 else "z"), False)
    for (y, seite) in ((3, "south"), (H - 3, "south"), (H // 2, "east")):
        dx, dz = D[seite]
        fenster(w, dx * r, y, dz * r, seite, holz=holz, glas="orange_stained_glass_pane", hoehe=3, blumen=0,
                laeden=False)
    yk = H + 1
    for x in range(-r - 4, r + 5):
        for z in range(-r - 4, r + 5):
            d = math.hypot(x, z)
            if d <= r + 3.6:
                w.setze(x, yk, z, w.b("dark_oak_planks") if d > r + 2.6 else w.b("spruce_planks"))
            if r + 2.6 < d <= r + 3.6:
                w.setze(x, yk - 1, z, treppe(w, "dark_oak", "north", "top"), False)
    hh = S(g, 16, 11)
    dm = Dachmat(w, ["deepslate_tile", "cobbled_deepslate", "deepslate_tile", "mossy_cobblestone"])
    for k in range(hh):
        t = k / hh
        rr = (r + 1.8) * (1 - t) ** 1.15
        ox = (t ** 2.4) * (r + 3)
        for x in range(-int(rr) - 2, int(rr) + 3):
            for z in range(-int(rr) - 2, int(rr) + 3):
                d = math.hypot(x, z)
                if rr - 1.2 < d <= rr or (k == 0 and d <= rr):
                    w.setze(round(x + ox), yk + 1 + k, z, dm.voll(x, k, z))
    w.setze(round(r + 3), yk + hh - 1, 1, w.b("lantern", hanging=True, waterlogged=False), False)
    for k in range(int(10 * SK[g])):
        ang = w.rng.random() * 6.283
        w.setze(round(math.cos(ang) * (r + 2.8)), yk + 1, round(math.sin(ang) * (r + 2.8)),
                w.b("moss_carpet") if k % 2 else w.b("fern"), False)
    cx = r + S(g, 6, 4)
    ka, kb = S(g, 3, 2), S(g, 3, 2)
    mauer(w, cx - ka, -kb, cx + ka, kb, 1, 4, st)
    fenster(w, cx + ka, 2, 0, "east", holz=holz, glas="orange_stained_glass_pane", blumen=0)
    tuer(w, cx, 1, kb, "south", holz=holz)
    kr = ka + 1.6
    for x in range(-int(kr) - 1, int(kr) + 2):
        for y in range(0, int(kr * 1.5) + 1):
            for z in range(-int(kr) - 1, int(kr) + 2):
                rip = 1 + 0.08 * math.cos(math.atan2(z, x) * 8)
                d = (x / (kr * rip)) ** 2 + ((y - kr * 0.55) / (kr * 0.75)) ** 2 + (z / (kr * rip)) ** 2
                if 0.68 < d <= 1.0:
                    vorn = z >= kr * 0.75
                    auge = vorn and abs(abs(x) - kr * 0.45) < 0.8 and abs(y - kr * 0.9) < 0.8
                    mund = vorn and abs(x) <= kr * 0.6 and abs(y - kr * 0.35) < 0.6 and (x % 2 == 0)
                    w.setze(cx + x, 5 + y, z, w.b("shroomlight") if (auge or mund) else
                            w.b("orange_terracotta" if int(math.atan2(z, x) * 8 / 3.14) % 2 else "pumpkin"))
    for y in range(0, 3):
        w.setze(cx + (1 if y == 2 else 0), 5 + int(kr * 1.5) + 1 + y, 0, w.b("dark_oak_log", axis="y"))
    w.setze(cx + 2, 5 + int(kr * 1.5) + 3, 0, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False))
    lx1 = -r - 1
    lx0 = lx1 - S(g, 6, 4)
    fachwerk(w, lx0, -3, lx1, 3, 1, 5, putz(w, "weiss"), holz=holz, abstand=2)
    fachwerk(w, lx0 - 1, -4, lx1 + 1, 4, 6, 9, putz(w, "weiss"), holz=holz, abstand=2)
    kragsteine(w, lx0, -3, lx1, 3, 5, holz)
    fenster(w, lx0 - 1, 7, 0, "west", holz=holz, glas="orange_stained_glass_pane")
    fenster(w, (lx0 + lx1) // 2, 7, 4, "south", holz=holz, glas="orange_stained_glass_pane")
    fenster(w, (lx0 + lx1) // 2, 2, 3, "south", holz=holz, glas="orange_stained_glass_pane", blumen=0)
    satteldach(w, lx0 - 1, -4, lx1 + 1, 4, 10, Dachmat(w, ["dark_oak", "spruce", "dark_oak", "mossy_cobblestone"]),
               first_x=False, ue=1, giebel=putz(w, "weiss"), traufe=holz, steil=1)
    treppe_gerade(w, lx1, 5, 6, "south", 5, breite=2, mat="dark_oak")
    sx0, sz0 = -2, r + 3
    farben = ["purple_wool", "orange_wool", "magenta_wool", "lime_wool"]
    for x in range(sx0 - 2, sx0 + 4):
        for z in range(sz0, sz0 + 3):
            w.setze(x, 4 + (1 if z == sz0 else 0), z, w.b(farben[(x - sx0) % 4]))
        w.setze(x, 1, sz0 + 1, w.b("spruce_planks") if sx0 - 1 <= x <= sx0 + 2 else w.b("barrel", facing="up",
                                                                                       open=False))
    for (x, z) in ((sx0 - 2, sz0), (sx0 + 3, sz0), (sx0 - 2, sz0 + 2), (sx0 + 3, sz0 + 2)):
        for y in range(1, 5):
            w.setze(x, y, z, zaun(w, holz))
    for i, x in enumerate(range(sx0 - 1, sx0 + 3)):
        w.setze(x, 2, sz0 + 1, w.b("candle", candles=1 + i % 4, lit=True, waterlogged=False) if i % 2 else
                w.b("brewing_stand", has_bottle_0=True, has_bottle_1=True, has_bottle_2=True))
    for k, (x, z) in enumerate(((-r - 2, r + 1), (-r - 3, r + 2), (-r - 2, r + 3))):
        w.setze(x, 1, z, w.b("white_wool"))
        if k != 1:
            w.setze(x, 2, z, w.b("white_wool"))
        w.setze(x, 3 if k != 1 else 2, z, w.b("white_candle", candles=3, lit=True, waterlogged=False))
    kram(w, cx + ka + 2, 1, kb + 2, 4)
    w.setze(cx + ka + 1, 1, kb + 3, w.b("carved_pumpkin", facing="south"))
    weg(w, [(0, r + 1), (1, R - 1)], breite=1.2)
    bepflanzen(w, zellen, 0.35, blumen=("red_mushroom", "brown_mushroom", "fern", "lily_of_the_valley"))
    deko_garten(w, zellen, n=8)
    efeu(w, 0.05, bis=10)
    return w




def stelzen_aussenposten(seed, g=2):
    """Stelzen-Außenposten: ein weißer, wuchtiger Steinsockel mit Treppenanlage, darauf ringsum Holzdecks auf
    schlanken Stelzen mit Laternen, zwei seitliche Plattformen mit Ziegelsäulen und Ladekränen samt hängenden
    Käfigen, oben zwei moosgrün verkleidete Fachwerkgeschosse unter einem weit ausladenden Schieferdach."""
    w = _neu(seed)
    R = S(g, 20, 13)
    zellen = diorama(w, R, art="wiese")
    weiss = steinmix(w, "weiss")
    holz = "spruce"
    a = S(g, 4, 3)
    H = S(g, 9, 6)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            for y in range(1, H + 1):
                if abs(x) == a or abs(z) == a or y == H:
                    w.setze(x, y, z, weiss(x, y, z))
    for y in range(1, 4):
        w.bloecke.pop((0, y, a), None)
    tuer(w, 0, 1, a, "south", holz=holz, vordach=False)
    for y in range(3, H, 3):
        w.setze(-a, y, 0, w.b("glass_pane", north=True, south=True, east=False, west=False, waterlogged=False))
        w.setze(a, y, 0, w.b("glass_pane", north=True, south=True, east=False, west=False, waterlogged=False))
    # Steinstufen-Sockel vorn
    for k in range(3):
        for x in range(-a - 2 + k, a + 3 - k):
            for z in range(a + 1, a + 4 - k):
                w.setze(x, 1 + k, z, w.b("stone_bricks" if (x + z) % 3 else "cobblestone"))
    for x in range(-2, 3):
        treppe_gerade(w, x, 3, a + 4, "south", 3, breite=1, mat="stone_brick")
    # Deck 1 mit Stelzen
    r1 = a + S(g, 5, 3)
    yd = H + 1
    for x in range(-r1, r1 + 1):
        for z in range(-r1, r1 + 1):
            w.setze(x, yd, z, w.b(f"{holz}_planks") if (x + z) % 7 else stamm(w, holz, "x"))
            if max(abs(x), abs(z)) == r1:
                w.setze(x, yd + 1, z, zaun(w, holz))
    for x in range(-r1, r1 + 1, max(3, r1 // 2)):
        for z in (-r1, r1):
            for y in range(1, yd):
                w.setze(x, y, z, stamm(w, holz))
            w.setze(x, 1, z, w.b("stone_bricks"))
    for z in range(-r1, r1 + 1, max(3, r1 // 2)):
        for x in (-r1, r1):
            for y in range(1, yd):
                w.setze(x, y, z, stamm(w, holz))
            w.setze(x, 1, z, w.b("stone_bricks"))
    kragsteine(w, -r1, -r1, r1, r1, yd - 1, holz, abstand=2)
    for (x, z) in ((-r1, -r1), (r1, r1), (-r1, r1), (r1, -r1)):
        w.setze(x, yd + 2, z, w.b("lantern", hanging=False, waterlogged=False))
    # seitliche Kranplattformen
    for sx in (-1, 1):
        cx = sx * (r1 + S(g, 4, 3))
        for x in range(cx - 2, cx + 3):
            for z in range(-2, 3):
                w.setze(x, yd - 2, z, w.b(f"{holz}_planks"))
                if abs(x - cx) == 2 or abs(z) == 2:
                    w.setze(x, yd - 1, z, zaun(w, holz))
        for (x, z) in ((cx - 2, -2), (cx + 2, 2), (cx - 2, 2), (cx + 2, -2)):
            for y in range(1, yd - 2):
                w.setze(x, y, z, stamm(w, holz))
        for x in range(min(cx, sx * r1), max(cx, sx * r1) + 1):
            w.setze(x, yd - 2, 0, w.b(f"{holz}_planks"))
        for y in range(yd - 1, yd + 7):
            for dz in (0, 1):
                w.setze(cx, y, dz, w.b("bricks" if y % 3 else "granite"))
        arm = S(g, 5, 3)
        for k in range(arm + 1):
            w.setze(cx + sx * k, yd + 7, 0, stamm(w, holz, "x"))
        for k in range(1, 3):
            w.setze(cx + sx * k, yd + 7 - k, 0, treppe(w, holz, "west" if sx > 0 else "east", "top"), False)
        ex = cx + sx * arm
        for y in range(yd + 3, yd + 7):
            w.setze(ex, y, 0, w.b("chain", axis="y", waterlogged=False))
        for y in range(yd, yd + 3):
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if abs(dx) == 1 or abs(dz) == 1:
                        w.setze(ex + dx, y, dz, w.b("iron_bars", north=dz != 0 and dx == 0, south=dz != 0 and dx == 0,
                                                    east=dx != 0 and dz == 0, west=dx != 0 and dz == 0,
                                                    waterlogged=False))
            w.setze(ex, yd + 2, 0, w.b("iron_block"))
    # Deck 2 und Wohngeschosse
    r2 = a + S(g, 2, 1)
    y2 = yd + 4
    for x in range(-r2 - 1, r2 + 2):
        for z in range(-r2 - 1, r2 + 2):
            w.setze(x, y2, z, w.b(f"{holz}_planks"))
            if max(abs(x), abs(z)) == r2 + 1:
                w.setze(x, y2 + 1, z, zaun(w, holz))
    for (x, z) in ((-r2, -r2), (r2, r2), (-r2, r2), (r2, -r2)):
        for y in range(yd + 1, y2):
            w.setze(x, y, z, stamm(w, holz))
    fachwerk(w, -a, -a, a, a, y2 + 1, y2 + 5, putz(w, "gruen"), holz=holz, abstand=2)
    fachwerk(w, -a - 1, -a - 1, a + 1, a + 1, y2 + 6, y2 + 10, putz(w, "gruen"), holz=holz, abstand=2)
    kragsteine(w, -a, -a, a, a, y2 + 5, holz)
    fensterreihe(w, -a, -a, a, a, y2 + 2, ("north", "south", "east", "west"), abstand=2, holz=holz, blumen=0.3)
    fensterreihe(w, -a - 1, -a - 1, a + 1, a + 1, y2 + 7, ("north", "south", "east", "west"), abstand=2, holz=holz,
                 blumen=0.2)
    dm = Dachmat(w, ["deepslate_tile", "deepslate_tile", "cobbled_deepslate", "deepslate_brick"])
    top = satteldach(w, -a - 1, -a - 1, a + 1, a + 1, y2 + 11, dm, first_x=True, ue=2, ue_giebel=2,
                     giebel=putz(w, "gruen"), traufe=holz)
    kamin(w, -1, -a + 1, y2 + 6, top + 2, steinmix(w, "grau"))
    weg(w, [(0, a + 5), (0, R - 1)], breite=1.4, mats=(("gravel", 3), ("cobblestone", 2), ("stone", 1)))
    bepflanzen(w, zellen, 0.35)
    deko_garten(w, zellen, n=10)
    kram(w, a + 2, 1, a + 3, 4)
    return w


def kirschbluetental(seed, g=3):
    """Kirschblütental: zwei grüne Hänge voller rosa Kirschbäume rahmen einen blauen Teich, darüber spannt sich eine
    geschwungene Holzbogenbrücke mit überdachtem Mittelpavillon, Laternen an Ketten, roten und violetten Bannern
    und Blütenteppichen."""
    from gewaesser import Land
    w = _neu(seed)
    R = S(g, 26, 16)
    Hh = S(g, 11, 7)
    L = Land(w, R)
    L.heben(lambda x, z, h: round(Hh * min(1.0, max(0.0, (abs(x) - R * 0.2) / (R * 0.45))) ** 1.15
                                  + L.rn(x, 0, z) * 1.5))
    L.see(0, 0, R * 0.22, 0, tiefe=3)
    L.bauen(unten=-4, fels=["stone", "andesite", "dirt", "coarse_dirt"])
    L.bepflanzen(dichte=0.45)
    rng = w.rng
    gesetzt = []
    for k in range(int(80 * SK[g])):
        x, z = int(rng.integers(-R, R)), int(rng.integers(-R, R))
        if (x, z) in L.h and abs(x) > R * 0.3 and (x, z) not in L.wasser and abs(z) > 4 and \
                all(math.hypot(x - a, z - b) > 6 for a, b in gesetzt):
            einfuegen(w, wald2.kirschbaum(int(rng.integers(1, 10 ** 6)), H=S(g, 7, 5)), x, L.h[(x, z)], z)
            gesetzt.append((x, z))
    for (x, z), h in L.h.items():
        if (x, z) not in L.wasser and rng.random() < 0.08 and (x, h + 1, z) not in w.bloecke:
            w.setze(x, h + 1, z, w.b("pink_petals", facing="north", flower_amount=1 + int(rng.random() * 4)))
    S0 = round(R * 0.66)
    D0 = Hh + 1
    hb = S(g, 3, 2)
    holz = "dark_oak"
    for x in range(-S0, S0 + 1):
        t = x / S0
        y = D0 + round(hb * (1 - t * t))
        for z in range(-2, 3):
            w.setze(x, y, z, w.b(f"{holz}_planks") if abs(z) < 2 else stamm(w, "mangrove", "x"))
        for z in (-2, 2):
            w.setze(x, y + 1, z, w.b("mangrove_fence", north=False, south=False, east=True, west=True,
                                     waterlogged=False))
        bogen = round(D0 - 1 - (D0 + 1) * (1 - t * t) ** 0.5 * 0.75 + hb * (1 - t * t))
        for z in (-2, 2):
            w.setze(x, bogen, z, stamm(w, "mangrove", "x"))
            if abs(x) % 4 == 0:
                for yy in range(bogen + 1, y):
                    w.setze(x, yy, z, stamm(w, holz))
        if abs(x) % 6 == 3 and abs(x) > S0 * 0.4:
            laterne(w, x, y - 1, 3, 1) if False else None
    pv = S(g, 5, 3)
    ym = D0 + hb
    for x in range(-pv, pv + 1):
        if abs(x) % 2 == 0:
            for z in (-2, 2):
                for yy in range(ym + 1, ym + 5):
                    w.setze(x, yy, z, stamm(w, holz))
    satteldach(w, -pv, -2, pv, 2, ym + 5, Dachmat(w, ["dark_oak", "dark_oak", "spruce", "mangrove"]), first_x=True,
               ue=2, ue_giebel=1, giebel=None, traufe=holz, firstzier=True)
    for x in range(-pv + 1, pv, 3):
        laterne(w, x, ym + 4, 0, 1)
    for sx in (-1, 1):
        x = sx * (pv + 1)
        for z in (-3, 3):
            for k in range(4):
                w.setze(x, ym - k, z, w.b("red_wool" if sx > 0 else "purple_wool"))
    return w


def riesenhand(seed, g=3):
    """Riesenhand im Meer: eine gewaltige, fein modellierte Steinhand ragt aus dem Wasser, Finger leicht gekrümmt,
    Seile um das Handgelenk geschlungen; auf der Handfläche eine gotische Kapelle mit Glockenturm, Grabsteinen
    und Laternen."""
    from skulptur import Skulptur, ell, kap
    w = _neu(seed)
    s = [1.0, 1.4, 1.9, 2.6][g]
    R = int(10 * s) + 4
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R + 1.5 * math.sin(math.atan2(z, x) * 5):
                for y in (-2, -1, 0):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -3, z, w.b("sand"))
    S_ = Skulptur(w, s)
    stn = Mix(w, [("smooth_stone", 3), ("calcite", 2), ("polished_andesite", 2), ("diorite", 2), ("andesite", 1)])
    S_.mat("k", lambda x, y, z, *a: stn(x, y, z))
    S_.mat("d", lambda x, y, z, *a: w.b("spruce_planks") if (x + y) % 2 else w.b("stripped_spruce_log", axis="y"))
    S_.plus(kap((0, -4, 0), (0, 4, 0), 3.0, 2.6), "k")
    S_.plus(ell(0, 6.6, 0.2, 4.2, 2.4, 2.4), "k")
    finger = ((-2.7, 6.0, 0.55), (-0.9, 7.6, 0.6), (0.9, 7.2, 0.6), (2.6, 5.6, 0.55))
    for (fx, fl, fr) in finger:
        b1 = (fx, 8.0, 0.9)
        b2 = (fx * 1.05, 8.0 + fl * 0.55, 1.5)
        b3 = (fx * 1.08, 8.0 + fl * 0.95, 0.6)
        S_.plus(kap(b1, b2, fr + 0.4, fr + 0.3), "k")
        S_.plus(kap(b2, b3, fr + 0.3, fr + 0.15), "k")
        S_.plus(ell(b3[0], b3[1] + 0.3, b3[2], fr + 0.1, fr + 0.15, fr + 0.1), "k")
    S_.plus(kap((-3.6, 5.5, 0.5), (-6.2, 8.5, 2.0), 1.0, 0.85), "k")
    S_.plus(kap((-6.2, 8.5, 2.0), (-6.6, 11.2, 1.6), 0.85, 0.7), "k")
    from skulptur import torus
    S_.plus(torus(0, 1.2, 0, 2.9, 0.45), "d")
    S_.plus(torus(0, 2.6, 0, 2.8, 0.4), "d")
    S_.rendern((-9, -5, -5), (9, 17, 5), versatz=(0.5, 0, 0.5))
    py = round(8.4 * s) + 1
    holz = "dark_oak"
    st = steinmix(w, "hell")
    a = max(2, round(1.0 * s))
    b = max(2, round(1.5 * s))
    for x in range(-a - 1, a + 2):
        for z in range(-b - 1, b + 2):
            w.setze(x, py - 1, z, stn(x, py, z))
    mauer(w, -a, -b, a, b, py, py + max(3, round(1.6 * s)), st, ecke=w.b("polished_andesite"))
    for z in range(-b + 1, b, 2):
        fenster(w, -a, py + 1, z, "west", holz=holz, laeden=False, blumen=0, hoehe=2, bogen=True)
        fenster(w, a, py + 1, z, "east", holz=holz, laeden=False, blumen=0, hoehe=2, bogen=True)
    tuer(w, 0, py, b, "south", holz=holz, vordach=False)
    top = satteldach(w, -a, -b, a, b, py + max(4, round(1.6 * s) + 1), Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]),
                     first_x=False, ue=1, giebel=st, traufe=holz, steil=2)
    ta = 1
    for y in range(py, top + 2):
        for x in range(-ta, ta + 1):
            for z in range(-b - 2 - ta, -b - 1 + ta):
                if abs(x) == ta or z in (-b - 2 - ta, -b - 2 + ta):
                    w.setze(x, y, z, st(x, y, z))
    kegeldach(w, 0, -b - 2, top + 2, 1.2, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]), form="nadel",
              eckig=True, h=max(6, round(4 * s)))
    for k, (x, z) in enumerate(((-a - 1, b + 2), (a + 1, b + 2), (a + 1, b + 1))):
        w.setze(x, py, z, w.b("mossy_cobblestone_wall", up=True, north="none", south="none", east="none",
                              west="none", waterlogged=False), False)
    laterne(w, a + 1, py + 2, b + 1, 1)
    return w


def schattenzitadelle(seed, g=3):
    """Schattenzitadelle: ein schwindelerregend hoher, gestufter Turm aus grauem Stein mit gerippten Strebepfeilern,
    leuchtenden Spitzbogenfenstern und gezackter Krone, ringsum zwei Mauerringe mit spitzen Wachtürmen und eine
    breite Treppenrampe."""
    w = _neu(seed)
    R = S(g, 30, 18)
    zellen = diorama(w, R, art="sand")
    for (x, z) in zellen:
        if (x, 0, z) in w.bloecke:
            w.setze(x, 0, z, w.b(["gravel", "andesite", "tuff", "coarse_dirt"][(x * 3 + z) % 4]))
    M = Mix(w, [("polished_andesite", 3), ("stone_bricks", 3), ("andesite", 2), ("cracked_stone_bricks", 1),
                ("polished_deepslate", 1)])
    H = S(g, 60, 34)
    r0 = S(g, 7, 4)
    stufen = [(0.0, 1.0), (0.3, 0.8), (0.55, 0.62), (0.75, 0.48), (0.9, 0.36)]
    for y in range(1, H + 1):
        t = y / H
        f = [f for (t0, f) in stufen if t >= t0][-1]
        r = r0 * f
        for x in range(-int(r) - 3, int(r) + 4):
            for z in range(-int(r) - 3, int(r) + 4):
                d = max(abs(x), abs(z)) * 0.6 + math.hypot(x, z) * 0.4
                if r - 1.2 < d <= r:
                    rippe = (x + z) % 3 == 0
                    w.setze(x, y, z, w.b("polished_deepslate") if rippe else M(x, y, z))
                elif r < d <= r + 1 and (x * 7 + z) % 5 == 0 and y % 2 == 0:
                    w.setze(x, y, z, M(x, y, z))
        if y % 7 in (3, 4) and y > 4:
            for (x, z) in ((round(r) - 0, 0), (-round(r), 0), (0, round(r)), (0, -round(r))):
                w.setze(x, y, z, w.b("black_stained_glass") if y % 7 == 3 else w.b("soul_lantern",
                                                                                     hanging=False,
                                                                                     waterlogged=False))
    for (t0, f) in stufen[1:]:
        y = int(t0 * H)
        r = r0 * f + 1.5
        for k in range(int(r * 6.3)):
            ang = k / int(r * 6.3) * 6.283
            x, z = round(math.cos(ang) * r), round(math.sin(ang) * r)
            w.setze(x, y, z, M(x, y, z))
            if k % 2 == 0:
                w.setze(x, y + 1, z, w.b("polished_blackstone_wall", up=True, north="none", south="none",
                                         east="none", west="none", waterlogged=False))
    for k in range(10):
        ang = k / 10 * 6.283
        for y in range(1, int(H * 0.32)):
            tt = y / (H * 0.32)
            r = r0 + (1 - tt) * 4 * SK[g] + 1
            w.setze(round(math.cos(ang) * r), y, round(math.sin(ang) * r), M(0, y, 0))
    rk = r0 * 0.36
    for k in range(8):
        ang = k / 8 * 6.283
        for y in range(H, H + S(g, 6, 4) + (k % 2) * 3):
            w.setze(round(math.cos(ang) * rk), y, round(math.sin(ang) * rk), w.b("polished_blackstone"))
    st_t = Dachmat(w, ["deepslate_tile", "polished_blackstone", "deepslate_tile"])
    for ring, (rr, n, hh) in enumerate(((R * 0.55, 6, S(g, 12, 8)), (R * 0.85, 8, S(g, 9, 6)))):
        for k in range(int(rr * 6.3)):
            ang = k / int(rr * 6.3) * 6.283
            x, z = round(math.cos(ang) * rr), round(math.sin(ang) * rr)
            if abs(x) <= 2 and z > 0:
                continue
            for y in range(1, hh - 3):
                w.setze(x, y, z, M(x, y, z))
            if k % 2 == 0:
                w.setze(x, hh - 3, z, M(x, y, z))
        for k in range(n):
            ang = k / n * 6.283 + 0.3
            cx, cz = round(math.cos(ang) * rr), round(math.sin(ang) * rr)
            rundmauer(w, cx, cz, 2, 1, hh, M)
            kegeldach(w, cx, cz, hh + 1, 2, st_t, form="nadel", h=S(g, 8, 5))
    for k in range(int(R * 0.85)):
        for x in range(-2, 3):
            w.setze(x, 0, r0 + 2 + k, w.b("polished_andesite" if (k + x) % 3 else "stone_bricks"))
    return w


def rosenanwesen(seed, g=2):
    """Rosenanwesen: ein Fachwerk-Herrenhaus mit leuchtend roten Dächern, Gauben und Efeu, zwei Rundtürme mit roten
    Glockenhelmen und Spitzen, davor ein Glaskuppel-Pavillon mit Holzrippen, Rosenbeete, eine Picknickdecke, ein
    Kiesweg zum Teich mit Bootssteg und Laternen."""
    w = _neu(seed)
    R = S(g, 22, 14)
    zellen = diorama(w, R, art="wiese")
    st = steinmix(w, "grau")
    dm = Dachmat(w, ["mcw:red_terracotta", "mcw:red_terracotta", "mcw:red_terracotta", "mcw:brown_terracotta"])
    holz = "spruce"
    a, b = S(g, 7, 5), S(g, 4, 3)
    zc = -S(g, 4, 3)
    sockel(w, -a, zc - b, a, zc + b, 1, 2, st)
    mauer(w, -a, zc - b, a, zc + b, 1, 4, st)
    fachwerk(w, -a - 1, zc - b - 1, a + 1, zc + b + 1, 5, 9, putz(w, "ocker"), holz=holz, abstand=3)
    kragsteine(w, -a - 1, zc - b - 1, a + 1, zc + b + 1, 4, holz)
    fensterreihe(w, -a - 1, zc - b - 1, a + 1, zc + b + 1, 6, ("north", "south", "west", "east"), abstand=3,
                 holz=holz, blumen=0.6)
    fensterreihe(w, -a, zc - b, a, zc + b, 2, ("south", "west"), abstand=3, holz=holz, blumen=0.3)
    tuer(w, -2, 1, zc + b, "south", holz=holz)
    top = satteldach(w, -a - 1, zc - b - 1, a + 1, zc + b + 1, 10, dm, first_x=True, ue=1, giebel=putz(w, "ocker"),
                     traufe=holz, steil=1)
    for gx in range(-a + 2, a - 1, 4):
        gaube(w, gx, 12, zc + b + 1, "south", dm, holz)
    kamin(w, -a + 2, zc - 1, 9, top + 2, st)
    tdm = Dachmat(w, ["mcw:red_terracotta", "mcw:red_terracotta", "mcw:orange_terracotta"])
    for (tx, tz, H, r) in ((a + 3, zc - 1, S(g, 14, 10), S(g, 3, 2)), (a + 7, zc + b + 3, S(g, 10, 7), S(g, 2, 2))):
        rundmauer(w, tx, tz, r, 1, H, putz(w, "ocker"))
        for y in (H // 2, H):
            for k in range(int((r + 1) * 6.4)):
                ang = k / int((r + 1) * 6.4) * 6.283
                w.setze(tx + round(math.cos(ang) * (r + 0.6)), y, tz + round(math.sin(ang) * (r + 0.6)),
                        stamm(w, holz, "x"), False)
        for y in range(3, H - 1, 4):
            fenster(w, tx, y, tz + r, "south", holz=holz, laeden=False, blumen=0)
        sp = kegeldach(w, tx, tz, H + 1, r + 0.9, tdm, form="glocke", h=S(g, 10, 7) if r > 2 else S(g, 8, 6))
        w.setze(tx, sp, tz, w.b("deepslate_tile_wall", up=True, north="none", south="none", east="none",
                                west="none", waterlogged=False))
        w.setze(tx, sp + 1, tz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    cx, cz = -S(g, 1, 0), b + S(g, 3, 2)
    rr = S(g, 4, 3) + 0.5
    for x in range(-int(rr) - 1, int(rr) + 2):
        for z in range(-int(rr) - 1, int(rr) + 2):
            d = math.hypot(x, z)
            if d <= rr:
                w.setze(cx + x, 0, cz + z, w.b("smooth_stone" if (x + z) % 2 else "polished_andesite"))
            if rr - 0.8 < d <= rr:
                for y in range(1, 4):
                    ang = math.degrees(math.atan2(z, x)) % 45
                    w.setze(cx + x, y, cz + z, stamm(w, "oak") if ang < 9 else w.b("glass"))
    for x in range(-int(rr) - 1, int(rr) + 2):
        for z in range(-int(rr) - 1, int(rr) + 2):
            for y in range(0, int(rr) + 2):
                d = math.sqrt(x * x + (y * 1.1) ** 2 + z * z)
                if rr - 1 < d <= rr:
                    rippe = (round(math.degrees(math.atan2(z, x))) % 45) < 9
                    w.setze(cx + x, 4 + y, cz + z, stamm(w, "oak") if rippe else w.b("white_stained_glass"))
    w.setze(cx, 5 + int(rr), cz, w.b("white_concrete"))
    w.setze(cx, 6 + int(rr), cz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    rng = w.rng
    for k in range(int(26 * SK[g])):
        x, z = int(rng.integers(-R + 2, R - 2)), int(rng.integers(b + 2, R - 2))
        if (x, 0, z) in w.bloecke and w.frei(x, 1, z) and w.frei(x, 2, z) and math.hypot(x - cx, z - cz) > rr + 2:
            n = ["rose_bush", "peony", "lilac", "rose_bush"][k % 4]
            w.setze(x, 1, z, w.b(n, half="lower"))
            w.setze(x, 2, z, w.b(n, half="upper"))
    px, pz = -a + 1, R - 5
    for x in range(px, px + 3):
        for z in range(pz, pz + 2):
            w.setze(x, 1, z, w.b("red_carpet" if (x + z) % 2 else "white_carpet"))
    w.setze(px + 3, 1, pz, w.b("barrel", facing="up", open=False))
    tx0 = -a - 3
    for x in range(tx0 - 3, tx0 + 4):
        for z in range(b - 1, b + 6):
            if ((x - tx0) / 3.5) ** 2 + ((z - b - 2) / 3.2) ** 2 < 1:
                w.bloecke.pop((x, 1, z), None)
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("clay"))
                if rng.random() < 0.12:
                    w.setze(x, 1, z, w.b("lily_pad"))
    for k in range(4):
        w.setze(tx0 + 2 - k, 1, b + 2, platte(w, "spruce", "bottom"))
    weg(w, [(-2, zc + b + 1), (cx, cz + int(rr) + 1), (2, R - 1)], breite=1.3,
        mats=(("gravel", 3), ("coarse_dirt", 1), ("dirt_path", 2)))
    for (x, z) in ((2, cz + int(rr) + 3), (-4, R - 3)):
        for y in range(1, 4):
            w.setze(x, y, z, zaun(w, "dark_oak"))
        w.setze(x, 4, z, w.b("lantern", hanging=False, waterlogged=False))
    bepflanzen(w, zellen, 0.4)
    deko_garten(w, zellen, n=8)
    efeu(w, 0.08, laub=0.6, bis=10)
    return w


def herbsthof(seed, g=2):
    """Herbsthof: ein Fachwerkhaus mit moosbewachsenem Holzdach und Eckturm thront auf einem Schieferfelsen,
    ein Bach stürzt in Stufen in einen Teich mit Steg und Ruderboot, davor Ackerterrassen mit Weizen und Kürbissen,
    ein Backofen, Brennholzstapel und Bäume in Rot, Orange und Gold."""
    from baeume2 import ginkgo, rotahorn
    from gewaesser import Land
    w = _neu(seed)
    R = S(g, 22, 14)
    L = Land(w, R)
    Hs = S(g, 6, 4)
    L.heben(lambda x, z, h: Hs + round(L.rn(x, 0, z)) if z < -2 and abs(x) < R * 0.6 else
            (2 if z < R * 0.2 else 0))
    L.see(round(R * 0.35), round(R * 0.55), R * 0.25, 0, tiefe=2)
    L.bauen(gras="grass_block", fels=["deepslate_tiles", "cobbled_deepslate", "deepslate_bricks", "tuff"],
            unten=-3)
    L.bepflanzen(dichte=0.35)
    st = steinmix(w, "dunkel")
    holz = "spruce"
    a, b = S(g, 6, 4), S(g, 4, 3)
    zc = -b - 4
    y0 = Hs + 1
    mauer(w, -a, zc - b, a, zc + b, y0, y0 + 3, st)
    fachwerk(w, -a - 1, zc - b - 1, a + 1, zc + b + 1, y0 + 4, y0 + 8, putz(w, "ocker"), holz=holz, abstand=3)
    kragsteine(w, -a - 1, zc - b - 1, a + 1, zc + b + 1, y0 + 3, holz)
    fensterreihe(w, -a - 1, zc - b - 1, a + 1, zc + b + 1, y0 + 5, ("south", "east", "west"), abstand=3, holz=holz,
                 blumen=0.6)
    fensterreihe(w, -a, zc - b, a, zc + b, y0 + 1, ("south",), abstand=3, holz=holz, blumen=0)
    tuer(w, 0, y0, zc + b, "south", holz=holz)
    dm = Dachmat(w, ["dark_oak", "spruce", "dark_oak", "mossy_cobblestone", "spruce"])
    top = satteldach(w, -a - 1, zc - b - 1, a + 1, zc + b + 1, y0 + 9, dm, first_x=True, ue=1,
                     giebel=putz(w, "ocker"), traufe=holz, steil=1)
    for (x, y, z), bk in list(w.bloecke.items()):
        if y >= y0 + 9 and w.P.name(bk).endswith("_stairs") and w.frei(x, y + 1, z) and w.rng.random() < 0.12:
            w.setze(x, y + 1, z, w.b("moss_carpet"))
    kamin(w, a - 2, zc, y0 + 4, top + 2, st)
    tx, tz = -a - 2, zc + b - 1
    ta = S(g, 2, 2)
    TH = S(g, 13, 9)
    mauer(w, tx - ta, tz - ta, tx + ta, tz + ta, y0, y0 + TH, st)
    fenster(w, tx, y0 + TH - 3, tz + ta, "south", holz=holz, blumen=0)
    for x in range(tx - ta - 1, tx + ta + 2):
        for z in range(tz - ta - 1, tz + ta + 2):
            if x in (tx - ta - 1, tx + ta + 1) or z in (tz - ta - 1, tz + ta + 1):
                w.setze(x, y0 + TH + 1, z, zaun(w, holz))
            w.setze(x, y0 + TH, z, w.b(f"{holz}_planks"))
    kegeldach(w, tx, tz, y0 + TH + 2, ta + 0.5, Dachmat(w, ["dark_oak", "spruce"]), form="kegel", eckig=True,
              h=S(g, 6, 4))
    for y in range(y0 + TH + 6, y0 + TH + 9):
        w.setze(tx, y, tz, zaun(w, holz))
    w.setze(tx + 1, y0 + TH + 8, tz, w.b("orange_wool"))
    bx = a + 3
    for z in range(-R, round(R * 0.4)):
        h = L.h.get((bx, z))
        if h is not None:
            w.setze(bx, h, z, w.b("water", level=0))
            w.bloecke.pop((bx, h + 1, z), None)
    for k in range(Hs - 1):
        w.setze(bx, Hs - k, -1, w.b("water", level=8), False)
    for k in range(S(g, 5, 3)):
        for z in (0, 1):
            w.setze(round(R * 0.35) - 3 - k, 1, round(R * 0.55) + z, w.b("spruce_planks"))
    from boote import ruderboot
    einfuegen(w, ruderboot(seed, 0), round(R * 0.35) + 1, 0, round(R * 0.55) + 1)
    for x in range(-R + 3, -R + 3 + S(g, 8, 5)):
        for z in range(round(R * 0.15), round(R * 0.15) + 6):
            if (x, z) in L.h and (x, z) not in L.wasser:
                hh = L.h[(x, z)]
                w.setze(x, hh, z, w.b("farmland", moisture=7) if z % 3 else w.b("water", level=0))
                if z % 3:
                    w.setze(x, hh + 1, z, w.b("wheat", age=7) if x % 4 else w.b("pumpkin"))
    for k in range(4):
        w.setze(a + 1, y0 + k // 2, zc + b + 2 + k % 2, w.b("oak_log", axis="z"))
    rng = w.rng
    for k in range(int(6 * SK[g])):
        x, z = int(rng.integers(-R + 2, R - 2)), int(rng.integers(-R + 2, R - 2))
        if (x, z) in L.h and (x, z) not in L.wasser and math.hypot(x, z) > R * 0.6 and (z < -2 or abs(x) > a + 6):
            baum = (rotahorn if k % 2 else ginkgo)(int(rng.integers(1, 10 ** 6)), 1 if g < 3 else 2)
            einfuegen(w, baum, x, L.h[(x, z)], z)
    for (x, z), h in L.h.items():
        if (x, z) not in L.wasser and rng.random() < 0.06 and w.frei(x, h + 1, z):
            w.setze(x, h + 1, z, w.b(["orange_carpet", "red_carpet", "yellow_carpet"][int(rng.random() * 3)]))
    efeu(w, 0.04, bis=y0 + 8)
    return w


def himmelsschmiede(seed, g=2):
    """Himmelsschmiede: eine große Fachwerk-Werkstatt mit verschachtelten türkisen Dächern, ein hoher Steinschlot
    mit Kupferkappe, ein großes Wasserrad am Mühlgraben, ein Ladekran mit hängender Plattform, ein efeubewachsener
    Hang mit breiter Freitreppe und eine Rampe mit Erzkarren."""
    from gewaesser import Land
    w = _neu(seed)
    R = S(g, 21, 14)
    L = Land(w, R)
    L.heben(lambda x, z, h: round(max(0, min(4, (z + R * 0.1) / R * 9))) if x > -3 else 0)
    L.bauen(unten=-3)
    L.bepflanzen(0.45)
    st = steinmix(w, "grau")
    dm = Dachmat(w, ["prismarine", "prismarine_brick", "prismarine", "dark_prismarine"], rand="dark_prismarine")
    holz = "spruce"
    a, b = S(g, 7, 5), S(g, 4, 3)
    zc = -b - 2
    sockel(w, -a, zc - b, a, zc + b, 1, 2, st)
    mauer(w, -a, zc - b, a, zc + b, 1, 5, st, ecke=w.b("polished_andesite"))
    for x in range(-2, 3):
        for y in range(1, 4):
            w.bloecke.pop((x, y, zc + b), None)
    w.setze(-2, 4, zc + b, treppe(w, "stone_brick", "east", "top"))
    w.setze(2, 4, zc + b, treppe(w, "stone_brick", "west", "top"))
    fachwerk(w, -a - 1, zc - b - 1, a + 1, zc + b + 1, 6, 10, putz(w, "weiss"), holz=holz, abstand=3)
    kragsteine(w, -a - 1, zc - b - 1, a + 1, zc + b + 1, 5, holz)
    fensterreihe(w, -a - 1, zc - b - 1, a + 1, zc + b + 1, 7, ("south", "east", "west"), abstand=3, holz=holz,
                 blumen=0.4)
    top = satteldach(w, -a - 1, zc - b - 1, a + 1, zc + b + 1, 11, dm, first_x=True, ue=1, giebel=putz(w, "weiss"),
                     traufe=holz)
    gaube(w, -3, 13, zc + b + 1, "south", dm, holz)
    gaube(w, 3, 13, zc + b + 1, "south", dm, holz)
    sx0 = a + 2
    fachwerk(w, sx0, zc - 2, sx0 + S(g, 5, 4), zc + 3, 1, 5, putz(w, "weiss"), holz=holz, abstand=2)
    satteldach(w, sx0, zc - 2, sx0 + S(g, 5, 4), zc + 3, 6, dm, first_x=False, ue=1, giebel=putz(w, "weiss"),
               traufe=holz)
    for y in range(1, top + S(g, 8, 5)):
        for dx in (0, 1):
            for dz in (0, 1):
                w.setze(-a + 1 + dx, y, zc - b + 1 + dz, st(dx, y, dz) if y < top + S(g, 7, 4) else w.b("cut_copper"))
    w.setze(-a + 1, top + S(g, 8, 5), zc - b + 1, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                      waterlogged=False))
    rr = S(g, 4, 3) + 0.5
    wx = -a - 2
    for k in range(int(rr * 12)):
        t = k / (rr * 12) * 6.283
        for dd in (rr, rr - 0.6):
            w.setze(wx, round(rr + 1 + math.sin(t) * dd), zc + round(math.cos(t) * dd), w.b("spruce_planks"))
            w.setze(wx - 1, round(rr + 1 + math.sin(t) * dd), zc + round(math.cos(t) * dd), w.b("spruce_planks"))
    for k in range(8):
        t = k / 8 * 6.283
        linie(w, (wx, rr + 1, zc), (wx, rr + 1 + math.sin(t) * rr, zc + math.cos(t) * rr), stamm(w, holz, "x"))
    for z in range(-R, R + 1):
        for x in (wx - 3, wx - 2, wx - 1, wx):
            if (x, 0, z) in w.bloecke and x <= wx - 2:
                w.bloecke.pop((x, 1, z), None)
                w.setze(x, 0, z, w.b("water", level=0))
    ky = 13
    for k in range(S(g, 5, 3) + 1):
        w.setze(-a + 3, ky, zc + b + 1 + k, stamm(w, holz, "z"))
    ex = zc + b + 1 + S(g, 5, 3)
    for y in range(ky - 4, ky):
        w.setze(-a + 3, y, ex, w.b("chain", axis="y", waterlogged=False))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(-a + 3 + dx, ky - 5, ex + dz, platte(w, "spruce", "bottom"))
    w.setze(-a + 3, ky - 4, ex, w.b("barrel", facing="up", open=False))
    for k in range(S(g, 7, 4)):
        for x in range(1, 5):
            h = L.h.get((x, zc + b + 2 + k), 0)
            w.setze(x, h + 1, zc + b + 2 + k, treppe(w, "mud_brick", "north"), True)
    rng = w.rng
    for k in range(int(30 * SK[g])):
        x, z = int(rng.integers(-R, R)), int(rng.integers(0, R))
        if (x, z) in L.h and w.frei(x, L.h[(x, z)] + 1, z):
            busch(w, x, L.h[(x, z)] + 1, z, 0.9 + rng.random() * 0.6, "oak" if rng.random() < 0.6 else "azalea")
    kram(w, a + 2, 1, zc + b + 2, 4)
    efeu(w, 0.06, laub=0.5, bis=11)
    return w


def karmesinlodge(seed, g=2):
    """Karmesin-Lodge: ein zweigeschossiges Haus mit leuchtend roten Gefachen zwischen Eichenbalken, dunklen
    Schieferdächern mit Gauben und einem Holzbalkon, ein hoher Eckturm mit Pyramidenhelm und Kranausleger mit
    goldener Laterne, ein weißer Steinkamin, ein steinerner Sockel mit Treppe und ein kleiner Brunnen."""
    w = _neu(seed)
    R = S(g, 19, 12)
    zellen = diorama(w, R, art="wiese")
    st = steinmix(w, "hell")
    rot = putz(w, "rot")
    holz = "oak"
    dm = Dachmat(w, ["deepslate_tile", "deepslate_tile", "cobbled_deepslate", "polished_blackstone"])
    a, b = S(g, 6, 4), S(g, 4, 3)
    sockel(w, -a, -b, a, b, 1, 3, st)
    mauer(w, -a, -b, a, b, 1, 4, st)
    fensterreihe(w, -a, -b, a, b, 2, ("south", "east"), abstand=3, holz=holz, blumen=0.4)
    tuer(w, 1, 1, b, "south", holz=holz, stufen=0)
    fachwerk(w, -a - 1, -b - 1, a + 1, b + 1, 5, 9, rot, holz=holz, abstand=3)
    kragsteine(w, -a - 1, -b - 1, a + 1, b + 1, 4, holz)
    fensterreihe(w, -a - 1, -b - 1, a + 1, b + 1, 6, ("south", "east", "west"), abstand=4, holz=holz, blumen=0.5,
                 glas="glass_pane")
    balkon(w, -a + 1, a - 1, b + 1, 5, "south", holz=holz, tiefe=2)
    top = satteldach(w, -a - 1, -b - 1, a + 1, b + 1, 10, dm, first_x=True, ue=2, giebel=rot, traufe=holz, steil=1)
    gaube(w, 2, 12, b + 1, "south", dm, holz)
    gaube(w, -3, 12, -b - 1, "north", dm, holz)
    kamin(w, a + 1, -1, 1, top + 1, steinmix(w, "weiss"))
    tx0 = -a - S(g, 5, 4)
    ta = S(g, 4, 3)
    TH = S(g, 16, 11)
    mauer(w, tx0, -ta // 2 - 1, tx0 + ta, ta // 2 + 1, 1, 4, st)
    fachwerk(w, tx0, -ta // 2 - 1, tx0 + ta, ta // 2 + 1, 5, TH, rot, holz=holz, abstand=2, diagonal=False)
    for y in range(7, TH - 1, 4):
        fenster(w, tx0 + ta // 2, y, ta // 2 + 1, "south", holz=holz, blumen=0, glas="yellow_stained_glass_pane")
    for x in range(tx0 - 1, tx0 + ta + 2):
        for z in range(-ta // 2 - 2, ta // 2 + 3):
            if x in (tx0 - 1, tx0 + ta + 1) or z in (-ta // 2 - 2, ta // 2 + 2):
                w.setze(x, TH, z, treppe(w, holz, "north", "top"), False)
    kegeldach(w, tx0 + ta // 2, 0, TH + 1, ta / 2 + 0.8, dm, form="kegel", eckig=True, h=S(g, 10, 7))
    for k in range(S(g, 4, 3) + 1):
        w.setze(tx0 - 1 - k, TH - 3, 0, stamm(w, holz, "x"))
    w.setze(tx0, TH - 4, 0, treppe(w, holz, "east", "top"), False)
    ex = tx0 - 1 - S(g, 4, 3)
    for y in (TH - 4, TH - 5):
        w.setze(ex, y, 0, w.b("chain", axis="y", waterlogged=False))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(ex + dx, TH - 6, dz, w.b("gold_block") if dx == dz == 0 else w.b("yellow_stained_glass"))
            w.setze(ex + dx, TH - 7, dz, w.b("glowstone") if dx == dz == 0 else w.b("yellow_stained_glass"))
    fx, fz = a + 3, b + 4
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(fx + dx, 1, fz + dz, w.b("stone_bricks") if abs(dx) + abs(dz) else w.b("water", level=0))
    for (dx, dz) in ((-1, -1), (1, 1)):
        for y in (2, 3):
            w.setze(fx + dx, y, fz + dz, zaun(w, "spruce"))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(fx + dx, 4, fz + dz, platte(w, "spruce"))
    weg(w, [(1, b + 4), (1, R - 1)], breite=1.3)
    kram(w, -a, 1, b + 3, 3)
    bepflanzen(w, zellen, 0.4)
    deko_garten(w, zellen, n=8)
    efeu(w, 0.05, bis=6)
    return w


def mandarinvilla(seed, g=2):
    """Mandarinvilla: ein steiles A-Haus mit orange-roten Ziegeldächern, die in mehreren Ebenen weit überstehen,
    mit Rundfenster im Giebel und Balkon, ein grauer Natursteinsockel mit Freitreppe, ein seitlicher Anbau mit
    eigenem Dach und Laternen, Büsche und Blumen am Fuß."""
    w = _neu(seed)
    R = S(g, 18, 12)
    zellen = diorama(w, R, art="wiese")
    st = steinmix(w, "grau")
    holz = "spruce"
    dm = Dachmat(w, ["mcw:orange_terracotta", "mcw:orange_terracotta", "mcw:red_terracotta", "mcw:brown_terracotta"])
    a, b = S(g, 4, 3), S(g, 5, 4)
    sockel(w, -a, -b, a, b, 1, 4, st)
    mauer(w, -a, -b, a, b, 1, 5, st)
    fensterreihe(w, -a, -b, a, b, 2, ("east", "south"), abstand=3, holz=holz, blumen=0.5)
    tuer(w, 0, 5 - 4 + 0, b, "south", holz=holz) if False else None
    for k in range(4):
        for x in range(-1, 2):
            w.setze(x, 4 - k, b + 1 + k, treppe(w, "stone_brick", "north"))
            for yy in range(1, 4 - k):
                w.setze(x, yy, b + 1 + k, w.b("stone_bricks"))
    tuer(w, 0, 5, b, "south", holz=holz, vordach=False)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.setze(x, 5, z, w.b(f"{holz}_planks"))
    fachwerk(w, -a - 1, -b - 1, a + 1, b + 1, 6, 10, putz(w, "weiss"), holz=holz, abstand=2)
    kragsteine(w, -a - 1, -b - 1, a + 1, b + 1, 5, holz)
    fensterreihe(w, -a - 1, -b - 1, a + 1, b + 1, 7, ("east", "west", "south"), abstand=3, holz=holz, blumen=0.5)
    balkon(w, -a + 1, a - 1, b + 1, 6, "south", holz=holz, tiefe=2)
    top = satteldach(w, -a - 1, -b - 1, a + 1, b + 1, 11, dm, first_x=False, ue=2, ue_giebel=2,
                     giebel=putz(w, "weiss"), traufe=holz, steil=2)
    for x in (-1, 0, 1):
        for y in (16, 17, 18):
            if abs(x) + abs(y - 17) <= 1:
                w.setze(x, y, b + 1, w.b("light_blue_stained_glass"))
    ax0 = a + 2
    mauer(w, ax0, -b + 2, ax0 + S(g, 4, 3), b - 1, 1, 5, st)
    fachwerk(w, ax0, -b + 2, ax0 + S(g, 4, 3), b - 1, 6, 8, putz(w, "weiss"), holz=holz, abstand=2)
    fenster(w, ax0 + S(g, 4, 3), 2, 0, "east", holz=holz)
    satteldach(w, ax0, -b + 2, ax0 + S(g, 4, 3), b - 1, 9, dm, first_x=False, ue=1, giebel=putz(w, "weiss"),
               traufe=holz)
    kamin(w, ax0 + 1, -b + 3, 1, 14, st)
    for (x, z) in ((-a - 2, b + 2), (a + 3, b + 2)):
        for y in range(1, 4):
            w.setze(x, y, z, zaun(w, "dark_oak"))
        w.setze(x, 4, z, w.b("lantern", hanging=False, waterlogged=False))
    weg(w, [(0, b + 5), (0, R - 1)], breite=1.3, mats=(("cobblestone", 2), ("gravel", 2), ("coarse_dirt", 1)))
    bepflanzen(w, zellen, 0.4)
    deko_garten(w, zellen, n=9)
    efeu(w, 0.04, bis=6)
    return w


def schwertschmiede(seed, g=2):
    """Schwertschmiede: eine Fachwerk-Schmiede mit Schieferdach und offener Werkstatt auf einem Steinsockel, mit
    Esse, Amboss, Schleifstein, Erzhaufen und Kristallen, ein Holzschild am Ausleger, blaue Banner; dahinter ragt
    aus einem bemoosten Felsen ein riesiges Steinschwert mit kupfernem Parierstück und umwickeltem Griff."""
    from drachen import felsen
    w = _neu(seed)
    R = S(g, 19, 12)
    zellen = diorama(w, R, art="wiese")
    st = steinmix(w, "grau")
    holz = "spruce"
    dm = Dachmat(w, ["deepslate_tile", "cobbled_deepslate", "deepslate_tile", "deepslate_brick"])
    sx, sz = -S(g, 8, 6), -S(g, 5, 4)
    felsen(w, S(g, 6, 4), S(g, 9, 6), cx=sx, cz=sz, spitz=0.6, rauh=0.3)
    for (x, y, z), bk in list(w.bloecke.items()):
        if y > 1 and w.frei(x, y + 1, z) and abs(x - sx) < 9 and abs(z - sz) < 9 and w.rng.random() < 0.5:
            w.bloecke[(x, y, z)] = w.b("moss_block")
    a, b = S(g, 5, 4), S(g, 4, 3)
    sockel(w, -a + 2, -b, a + 2, b, 1, 2, st)
    mauer(w, -a + 2, -b, a + 2, b, 1, 4, st)
    for x in range(-a + 4, a + 1):
        for y in range(1, 4):
            w.bloecke.pop((x, y, b), None)
    for x in range(-a + 3, a + 2, 3):
        for y in range(1, 4):
            w.setze(x, y, b + 1, stamm(w, holz))
    fachwerk(w, -a + 1, -b - 1, a + 3, b + 1, 5, 8, putz(w, "weiss"), holz=holz, abstand=2)
    kragsteine(w, -a + 1, -b - 1, a + 3, b + 1, 4, holz)
    fensterreihe(w, -a + 1, -b - 1, a + 3, b + 1, 6, ("south", "east"), abstand=3, holz=holz, blumen=0.4)
    top = satteldach(w, -a + 1, -b - 1, a + 3, b + 1, 9, dm, first_x=True, ue=1, giebel=putz(w, "weiss"),
                     traufe=holz)
    kamin(w, a + 1, -b + 1, 1, top + 2, st)
    w.setze(a + 1, 1, b - 1, w.b("blast_furnace", facing="south", lit=True))
    w.setze(a, 1, b - 1, w.b("lava_cauldron"))
    w.setze(-1, 1, b - 1, w.b("anvil", facing="east"))
    w.setze(1, 1, b - 1, w.b("grindstone", face="floor", facing="north"))
    w.setze(-2, 1, b - 2, w.b("smithing_table"))
    for k, (x, z) in enumerate(((a + 4, b + 2), (a + 5, b + 1), (a + 4, b + 1))):
        w.setze(x, 1, z, w.b(["raw_copper_block", "raw_iron_block", "copper_ore"][k]))
    w.setze(-a, 1, b + 2, w.b("amethyst_block"))
    w.setze(-a, 2, b + 2, w.b("amethyst_cluster", facing="up", waterlogged=False))
    for y in range(3, 6):
        w.setze(a + 4, y, b, w.b("blue_wool") if y < 5 else w.b("white_wool"))
    for k in range(3):
        w.setze(a + 4 + k, 7, b + 1, stamm(w, holz, "x"))
    for dz in (0, 1, 2):
        w.setze(a + 6, 6, b + dz, w.b("spruce_planks"))
        w.setze(a + 6, 5, b + dz, w.b("spruce_planks") if dz != 1 else w.b("dark_oak_planks"))
    H = S(g, 28, 18)
    bw = S(g, 2, 1)
    yb = S(g, 6, 4)
    for y in range(yb, H):
        tt = (y - yb) / (H - yb)
        breite = bw if tt > 0.12 else max(0, round(bw * tt / 0.12))
        for x in range(-breite, breite + 1):
            for z in (-1, 0, 1):
                kern = abs(x) < max(1, breite) and z == 0
                w.setze(sx + x, y, sz + z, w.b("polished_deepslate" if kern and breite > 0 else
                                               ("calcite" if abs(x) == breite else "polished_andesite")))
    gb = S(g, 6, 4)
    for x in range(-gb, gb + 1):
        for z in (-1, 0, 1):
            for y in (H, H + 1):
                w.setze(sx + x, y, sz + z, w.b("cut_copper" if abs(x) < gb - 1 else "waxed_exposed_cut_copper"))
        if abs(x) >= gb - 1:
            w.setze(sx + x, H + 2, sz, w.b("waxed_exposed_cut_copper"))
            w.setze(sx + x, H - 1, sz, w.b("waxed_exposed_cut_copper"))
    gl = S(g, 5, 4)
    for y in range(H + 2, H + 2 + gl):
        w.setze(sx, y, sz, w.b("stripped_mangrove_log" if y % 2 else "dark_oak_log", axis="y"))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            for dy in (0, 1):
                w.setze(sx + dx, H + 2 + gl + dy, sz + dz, w.b("emerald_block") if dx == dz == 0 and dy == 0
                        else w.b("copper_block"))
    weg(w, [(0, b + 2), (2, R - 1)], breite=1.4)
    kram(w, -a + 1, 1, b + 3, 4)
    bepflanzen(w, zellen, 0.4)
    deko_garten(w, zellen, n=8)
    return w


def efeuturm(seed, g=2):
    """Efeuturm: ein schlanker, sich nach oben verjüngender Turm aus hellem Stein, über und über mit Efeu und Moos
    bewachsen, oben ein auskragendes Fachwerkhaus mit Balkon, Erkern und vier spitzen Türmchen, einem Hauptdach in
    Violett und einer roten Fahne."""
    w = _neu(seed)
    R = S(g, 11, 8)
    zellen = diorama(w, R, art="wiese")
    hell = w.rng.random() < 0.5 or True
    M = steinmix(w, "sand") if seed % 2 else steinmix(w, "grau")
    holz = "spruce"
    H = S(g, 30, 20)
    r0 = S(g, 5, 3) + 0.5
    for y in range(1, H + 1):
        r = r0 * (1 - 0.3 * y / H)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(x, z)
                if r - 1 < d <= r + 0.4:
                    w.setze(x, y, z, M(x, y, z))
        if y % 6 == 0:
            for (x, z, s) in ((round(r), 0, "east"), (0, round(r), "south")):
                fenster(w, x, y, z, s, holz=holz, laeden=False, blumen=0, hoehe=2)
    a = round(r0 * 0.7 + 1.5)
    yb = H + 1
    for k in range(3):
        for x in range(-a + k, a - k + 1):
            for z in range(-a + k, a - k + 1):
                if max(abs(x), abs(z)) == a - k:
                    w.setze(x, yb - 1 - k, z, treppe(w, holz, "north", "top") if False else platte(w, holz, "top"))
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            w.setze(x, yb, z, w.b(f"{holz}_planks"))
            if max(abs(x), abs(z)) == a + 1:
                w.setze(x, yb + 1, z, zaun(w, holz))
    fachwerk(w, -a + 1, -a + 1, a - 1, a - 1, yb + 1, yb + 5, putz(w, "weiss"), holz=holz, abstand=2)
    fensterreihe(w, -a + 1, -a + 1, a - 1, a - 1, yb + 2, ("north", "south", "east", "west"), abstand=2, holz=holz,
                 blumen=0.4)
    dm = Dachmat(w, ["mcw:purple_terracotta", "mcw:magenta_terracotta", "mcw:purple_terracotta"]) if seed % 2 else \
        Dachmat(w, ["deepslate_tile", "cobbled_deepslate", "deepslate_tile"])
    sp = kegeldach(w, 0, 0, yb + 6, a - 0.5, dm, form="glocke", eckig=True, h=S(g, 14, 10))
    for y in range(sp + 1, sp + 4):
        w.setze(0, y, 0, zaun(w, holz))
    w.setze(1, sp + 3, 0, w.b("red_wool"))
    w.setze(2, sp + 3, 0, w.b("red_wool"))
    for (x, z) in ((-a, -a), (a, a), (-a, a), (a, -a)):
        for y in range(yb + 1, yb + 6):
            w.setze(x, y, z, stamm(w, holz))
        kegeldach(w, x, z, yb + 6, 0.6, dm, form="nadel", h=S(g, 7, 5))
    efeu(w, 0.25, laub=0.8, bis=H - 2)
    for (x, y, z), bk in list(w.bloecke.items()):
        if y < H * 0.6 and w.P.name(bk) in ("minecraft:stone_bricks", "minecraft:cobblestone",
                                            "minecraft:smooth_sandstone", "minecraft:sandstone") and \
                w.rng.random() < 0.18:
            w.bloecke[(x, y, z)] = w.b("moss_block")
    bepflanzen(w, zellen, 0.5)
    deko_garten(w, zellen, n=6)
    return w


def stelzenfischer(seed, g=2):
    """Fischerhütte auf Stelzen: eine Holzhütte mit tief gezogenem, türkisem A-Dach steht auf Pfählen im Wasser,
    umlaufende Stege mit Geländer und Leitern, ein geschwungener Kranausleger mit einem großen Fisch als Ladenschild,
    Netze, Fässer, Bojen, ein Ruderboot und Seerosen."""
    w = _neu(seed)
    R = S(g, 18, 12)
    zellen = diorama(w, R, art="wiese", frei=lambda x, z: True)
    for (x, z) in zellen:
        for y in (-2, -1, 0):
            w.setze(x, y, z, w.b("water", level=0))
        w.setze(x, -3, z, w.b("sand" if (x + z) % 3 else "gravel"))
    holz = "oak"
    a, b = S(g, 4, 3), S(g, 4, 3)
    yd = 2
    r = a + S(g, 4, 3)
    for x in range(-r, r + 1):
        for z in range(-r, r + 1):
            if max(abs(x), abs(z)) <= r and not (x > a + 1 and z < -1):
                w.setze(x, yd, z, w.b("birch_planks") if (x + z) % 4 else w.b(f"{holz}_planks"))
                if max(abs(x), abs(z)) == r:
                    w.setze(x, yd + 1, z, zaun(w, "birch"))
    for x in range(-r, r + 1, 3):
        for z in (-r, r):
            for y in range(-2, yd):
                w.setze(x, y, z, stamm(w, "spruce", geschaelt=False))
    for z in range(-r, r + 1, 3):
        for x in (-r, r):
            for y in range(-2, yd):
                w.setze(x, y, z, stamm(w, "spruce", geschaelt=False))
    for y in range(-1, yd + 1):
        w.setze(0, y, r + 1, w.b("ladder", facing="south", waterlogged=y < 1), False)
    fachwerk(w, -a, -b, a, b, yd + 1, yd + 5, Mix(w, [("oak_planks", 3), ("birch_planks", 1), ("stripped_oak_log", 1)],
                                                   axis="y") if False else w.b("oak_planks"), holz="spruce", abstand=2)
    fensterreihe(w, -a, -b, a, b, yd + 2, ("south", "east", "west"), abstand=3, holz="spruce", blumen=0.4)
    tuer(w, 0, yd + 1, b, "south", holz="spruce")
    dm = Dachmat(w, ["warped", "prismarine_brick", "warped", "dark_prismarine"])
    satteldach(w, -a, -b, a, b, yd + 6, dm, first_x=False, ue=2, ue_giebel=1, giebel=w.b("oak_planks"), traufe="spruce",
               steil=2)
    kamin(w, a - 1, -b + 1, yd + 1, yd + 15, steinmix(w, "grau"))
    kx = -r
    for k in range(6):
        w.setze(kx - 1 - k, yd + 9 + min(k, 3) - max(0, k - 3), 0, stamm(w, "spruce", "x"))
    for y in range(yd + 1, yd + 10):
        w.setze(kx, y, 0, stamm(w, "spruce"))
    ex = kx - 6
    for y in range(yd + 6, yd + 8):
        w.setze(ex, y, 0, w.b("chain", axis="y", waterlogged=False))
    from skulptur import Skulptur, ell, kap
    from weltwunder import bl
    Sk = Skulptur(w, 0.5 * SK[g] + 0.3)
    Sk.mat("k", bl(w, "prismarine_bricks"))
    Sk.mat("d", bl(w, "dark_prismarine"))
    Sk.plus(ell(0, 0, 0, 1.3, 2.4, 0.9), "k")
    Sk.plus(kap((0, -2.2, 0), (0, -3.4, 0), 0.4, 1.0), "d")
    Sk.plus(ell(0.9, 0.6, 0, 0.6, 0.3, 0.3), "d")
    Sk.rendern((-3, -4, -2), (3, 3, 2), versatz=(ex + 0.5, yd + 2, 0.5))
    for k in range(4):
        w.setze(a + 2, yd + 1, -b + k, w.b("barrel", facing="up", open=False) if k % 2 else w.b("cobweb"))
    for (x, z) in ((r + 3, -2), (-r - 3, r - 1), (2, r + 4)):
        w.setze(x, 0, z, w.b("red_wool"))
        w.setze(x, 1, z, w.b("white_wool"))
    from boote import ruderboot
    einfuegen(w, ruderboot(seed, 0), a + 3, 0, r + 4)
    rng = w.rng
    for (x, z) in zellen:
        if max(abs(x), abs(z)) > r + 1 and rng.random() < 0.05:
            w.setze(x, 1, z, w.b("lily_pad"))
    return w


def freibeuter_brigg(seed, g=2):
    """Freibeuter-Brigg: ein großer Zweimaster mit dunklem Rumpf und gelbem Zierstreifen, Kanonenpforten, Heckkastell
    mit Galeriefenstern und Laternen, gebogenen Segeln an mehreren Rahen, Klüver- und Stagsegeln, Wanten und einer
    schwarzen Flagge."""
    w = _neu(seed)
    L = S(g, 22, 13)
    B = S(g, 4, 3)
    T = S(g, 4, 3)
    for x in range(-L, L + 1):
        t = x / L
        bb = B * (1 - max(0, t) ** 2.2 * 0.92) * (1 - max(0, -t) ** 4 * 0.35)
        for y in range(-T, 4):
            br = bb * (1 - ((-y) / (T + 1)) ** 2 * 0.75) if y < 0 else bb + (0.4 if y > 1 else 0)
            for z in range(-int(br) - 1, int(br) + 2):
                if abs(z) > br + 0.3:
                    continue
                rand = abs(z) > br - 1 or y == -T
                if rand:
                    if y == 1:
                        blk = "yellow_terracotta"
                    elif y == 2 and x % 4 == 0 and abs(x) < L * 0.7:
                        blk = "black_concrete"
                    elif y >= 3:
                        blk = "dark_oak_fence" if y == 3 else None
                    else:
                        blk = "dark_oak_planks" if y < 0 else "spruce_planks"
                    if blk == "dark_oak_fence":
                        w.setze(x, y, z, zaun(w, "dark_oak"))
                    elif blk:
                        w.setze(x, y, z, w.b(blk))
                elif y == 2:
                    w.setze(x, y, z, w.b("spruce_planks"))
    hk = S(g, 6, 4)
    for x in range(-L, -L + hk):
        for z in range(-B, B + 1):
            for y in range(3, 7):
                if abs(z) == B or x == -L:
                    fen = y in (4, 5) and (z % 2 == 0 or x == -L)
                    w.setze(x, y, z, w.b("yellow_stained_glass_pane", north=x != -L, south=x != -L, east=x == -L,
                                         west=x == -L, waterlogged=False) if fen and x == -L else
                            w.b("dark_oak_planks"))
            w.setze(x, 7, z, w.b("spruce_planks"))
            if abs(z) == B or x == -L:
                w.setze(x, 8, z, zaun(w, "dark_oak"))
    for z in (-B + 1, B - 1):
        laterne(w, -L - 1, 7, z, 1)
    masten = [(-round(L * 0.2), S(g, 26, 16)), (round(L * 0.32), S(g, 30, 18))]
    for (mx, mh) in masten:
        for y in range(2, mh):
            w.setze(mx, y, 0, stamm(w, "dark_oak", geschaelt=False))
        abst = max(4, (mh - 8) // 3)
        for i, y in enumerate(range(6, mh - 3, abst)):
            sb = round(B * 2.3 * (1 - i * 0.16))
            hs = abst - 1
            for z in range(-sb, sb + 1):
                w.setze(mx, y + hs + 1, z, stamm(w, "spruce", "z", geschaelt=False))
                for yy in range(y, y + hs + 1):
                    bauch = round(1.4 * SK[g] * 1.5 * math.sin((yy - y + 0.5) / (hs + 1) * math.pi) *
                                  (1 - (z / (sb + 1)) ** 2))
                    w.setze(mx + bauch, yy, z, w.b("white_wool" if (z * 3 + yy) % 9 else "light_gray_wool"))
        w.setze(mx, mh, 0, w.b("dark_oak_planks"))
        for k in range(3):
            w.setze(mx + 1 + k, mh - (k // 2), 0, w.b("black_wool"))
        for z in (-B, B):
            linie(w, (mx, mh - 4, 0), (mx - 2, 3, z), w.b("chain", axis="y", waterlogged=False), 0.0, False)
            linie(w, (mx, mh - 4, 0), (mx + 2, 3, z), w.b("chain", axis="y", waterlogged=False), 0.0, False)
    bug = L + S(g, 9, 6)
    linie(w, (L - 1, 3, 0), (bug, 7 + S(g, 3, 2), 0), stamm(w, "spruce", "x", geschaelt=False))
    for k in range(S(g, 7, 4)):
        t = k / S(g, 7, 4)
        x0 = round(L + (bug - L) * t)
        y0 = round(3 + (4 + S(g, 3, 2)) * t)
        linie(w, (x0, y0, 0), (masten[1][0] + 1, masten[1][1] - 5 - k, 0), w.b("white_wool"), 0.0, False)
    for x in range(-L + hk + 2, L - 3, 4):
        for z in (-B, B):
            w.setze(x, 2, z, w.b("black_concrete"))
    return w


def totenkopfatoll(seed, g=3):
    """Totenkopf-Atoll: ein Ring aus zerklüfteten Bergen mit Palmenwald und Sandstränden umschließt eine Lagune;
    in der Bergflanke klafft ein riesiger Totenkopf, aus dessen Mund ein Wasserfall stürzt, in der Lagune liegt
    eine Festungsinsel mit Türmen und Hafen, draußen ankert ein Segelschiff."""
    from gewaesser import Land
    from lib import Rauschen
    w = _neu(seed)
    R = S(g, 34, 22)
    L = Land(w, R)
    rn = Rauschen(w, 5)
    Hm = S(g, 20, 12)

    def hoehe(x, z, h):
        d = math.hypot(x, z) / R
        ring = math.exp(-((d - 0.62) / 0.15) ** 2)
        lag = -3 if d < 0.42 else 0
        auss = -3 if d > 0.86 else 0
        return round(ring * Hm * (0.55 + 0.7 * rn(x, 0, z)) + lag + auss + (2 if 0.42 <= d <= 0.86 else 0))
    L.heben(hoehe)
    for (x, z), h in L.h.items():
        if h < 0:
            L.wasser[(x, z)] = 0
    L.bauen(gras="grass_block", fels=["stone", "granite", "andesite", "coarse_dirt", "dirt", "tuff"], unten=-4)
    L.bepflanzen(dichte=0.35, baeume=int(26 * SK[g]), arten=("palme", "palme", "busch", "palme"))
    for (x, z), h in L.h.items():
        if 0 <= h <= 2 and (x, z) not in L.wasser:
            w.setze(x, h, z, w.b("sand"))
    from skulptur import Skulptur, ell
    from weltwunder import bl
    sz = -round(R * 0.62)
    hy = max(4, L.h.get((0, sz), 5))
    s = 1.0 * SK[g] + 0.6
    Sk = Skulptur(w, s)
    knochen = Mix(w, [("bone_block", 4), ("calcite", 2), ("diorite", 1), ("smooth_sandstone", 1)])
    Sk.mat("k", lambda x, y, z, *a: knochen(x, y, z))
    Sk.mat("d", bl(w, "black_concrete"))
    Sk.plus(ell(0, 3, 0, 4.2, 4.0, 3.4), "k")
    Sk.plus(ell(0, 0.2, 0.6, 2.8, 2.0, 2.6), "k")
    Sk.minus(ell(-1.6, 3.5, 3.2, 1.2, 1.3, 1.2))
    Sk.minus(ell(1.6, 3.5, 3.2, 1.2, 1.3, 1.2))
    Sk.plus(ell(-1.6, 3.5, 2.4, 1.1, 1.2, 0.6), "d")
    Sk.plus(ell(1.6, 3.5, 2.4, 1.1, 1.2, 0.6), "d")
    Sk.plus(ell(0, 1.8, 3.4, 0.5, 0.7, 0.6), "d")
    Sk.minus(ell(0, -0.4, 3.0, 2.0, 0.7, 0.9))
    Sk.rendern((-6, -4, -5), (6, 8, 5), versatz=(0.5, hy - 1, sz + 2.5))
    mz = sz + round(3.4 * s)
    for y in range(1, hy):
        w.setze(0, y, mz, w.b("water", level=8 if y < hy - 1 else 0), False)
    fi = S(g, 5, 4)
    st = steinmix(w, "sand")
    for x in range(-fi - 2, fi + 3):
        for z in range(-fi - 2, fi + 3):
            if max(abs(x), abs(z)) <= fi + 1 + (1 if (x + z) % 3 == 0 else 0):
                for y in range(-3, 1):
                    w.setze(x, y, z, w.b("sandstone" if y == 0 else "stone"))
    mauer(w, -fi, -fi, fi, fi, 1, 4, st)
    for x in range(-fi, fi + 1):
        for z in (-fi, fi):
            if x % 2 == 0:
                w.setze(x, 5, z, st(x, 5, z))
    tdm = Dachmat(w, ["mcw:red_terracotta", "mcw:orange_terracotta"])
    for (x, z) in ((-fi, -fi), (fi, -fi), (-fi, fi), (fi, fi)):
        rundmauer(w, x, z, 2, 1, S(g, 8, 6), st)
        kegeldach(w, x, z, S(g, 8, 6) + 1, 2.2, tdm, form="kegel", h=S(g, 5, 4))
    mauer(w, -2, -2, 2, 2, 1, S(g, 10, 7), st)
    satteldach(w, -2, -2, 2, 2, S(g, 10, 7) + 1, tdm, first_x=True, ue=1, giebel=st, traufe="spruce")
    for k in range(S(g, 8, 5)):
        for z in (-1, 0, 1):
            w.setze(fi + 2 + k, 1, z, platte(w, "spruce", "bottom"))
    from boote import kogge
    from piraten import einfuegen_gedreht
    from skulptur import dreh_y
    sch = kogge(seed, max(0, g - 2))
    einfuegen_gedreht(w, sch, dreh_y(0.4), (round(R * 0.62), 0, round(R * 0.82)))
    return w


INSTAGRAM = {
    "alchemistenturm": ("Alchemistenturm", alchemistenturm),
    "tuerkis_gehoeft": ("Türkis-Gehöft mit Wimpelturm", tuerkis_gehoeft),
    "stelzen_aussenposten": ("Stelzen-Außenposten", stelzen_aussenposten),
    "kirschbluetental": ("Kirschblütental mit Bogenbrücke", kirschbluetental),
    "hexenladen": ("Hexenladen mit Kürbisdach", hexenladen),
    "riesenhand": ("Riesenhand mit Kapelle", riesenhand),
    "schattenzitadelle": ("Schattenzitadelle", schattenzitadelle),
    "rosenanwesen": ("Rosenanwesen mit Glaskuppel", rosenanwesen),
    "herbsthof": ("Herbsthof am Wasserfall", herbsthof),
    "himmelsschmiede": ("Himmelsschmiede", himmelsschmiede),
    "karmesinlodge": ("Karmesin-Lodge", karmesinlodge),
    "mandarinvilla": ("Mandarinvilla", mandarinvilla),
    "schwertschmiede": ("Schwertschmiede", schwertschmiede),
    "efeuturm": ("Efeuturm", efeuturm),
    "stelzenfischer": ("Fischerhütte auf Stelzen", stelzenfischer),
    "freibeuter_brigg": ("Freibeuter-Brigg", freibeuter_brigg),
    "totenkopfatoll": ("Totenkopf-Atoll", totenkopfatoll),
}

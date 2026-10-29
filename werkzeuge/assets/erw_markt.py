"""Mittelaltermarkt II – zwanzig weitere Buden und Bauten: Backhaus, Marionettenbühne, Bogenschützen-Stand,
Gewürzstand, Käsestand, Wahrsagerwagen, Zinngießer-Bude, Metzgerei, Schusterwerkstatt, Badestube, Waffenhändler,
Musikantenbühne, Markthalle, Lebkuchenbude, Pferdekoppel mit Händler, Taubenschlag-Turm, Schreibstube,
Geflügelmarkt, Wechselstube und Holzriesenrad."""

from __future__ import annotations

import math

from erw_basis import M, S, baumrand, figur, haus, hoehe, wiese
from feinbau import Dachmat, fachwerk, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from skulptur import ell, kap, kasten, kegel, kreisrand


def pflaster(w, R, cx=0, cz=0):
    p = M(w, [("cobblestone", 3), ("stone_bricks", 2), ("andesite", 1), ("mossy_cobblestone", 1)], zelle=1.2)
    for x in range(cx - int(R), cx + int(R) + 1):
        for z in range(cz - int(R), cz + int(R) + 1):
            if math.hypot(x - cx, z - cz) <= R:
                w.setze(x, 0, z, p(x, 0, z))
                for y in range(1, 3):
                    if w.hole(x, y, z) in (w.b("grass"), w.b("poppy"), w.b("dandelion")):
                        w.bloecke.pop((x, y, z), None)


def fachwerkwand(w):
    return M(w, [("white_terracotta", 3), ("calcite", 2), ("smooth_sandstone", 1)])


def bude(w, cx, cz, B=5, T=3, holz="spruce", farben=("red_wool", "white_wool"), waren=(), richtung="south",
         y0=1):
    """Marktbude: Tresen, Pfosten, gestreiftes Satteldach aus Wolle, Rückwand mit Regal und Waren."""
    x0, x1 = cx - B // 2, cx + B // 2
    z0, z1 = cz - T // 2, cz + T // 2
    vorne = z1 if richtung == "south" else z0
    hinten = z0 if richtung == "south" else z1
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, y0 - 1, z, w.b(f"{holz}_planks"))
    for x in (x0, x1):
        for z in (z0, z1):
            for y in range(y0, y0 + 3):
                w.setze(x, y, z, w.b(f"{holz}_fence"))
    for x in range(x0, x1 + 1):
        w.setze(x, y0, vorne, w.b(f"{holz}_slab", type="top", waterlogged=False) if x0 < x < x1 else
                w.b(f"{holz}_fence"))
        w.setze(x, y0, hinten, w.b("barrel", facing="up", open=False) if x % 2 else w.b(f"{holz}_planks"))
        w.setze(x, y0 + 1, hinten, w.b(f"{holz}_planks") if x in (x0, x1) else w.b(f"{holz}_trapdoor",
                                                                                     facing=richtung, half="bottom",
                                                                                     open=True, powered=False,
                                                                                     waterlogged=False))
    mitte = (z0 + z1) / 2
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            dz = abs(z - mitte)
            y = y0 + 3 + round((T / 2 + 1 - dz) * 0.7)
            w.setze(x, y, z, w.b(farben[(x + 20) % 2]))
    for i, ware in enumerate(waren):
        x = x0 + 1 + i
        if x >= x1:
            break
        name, pr = ware if isinstance(ware, tuple) else (ware, {})
        w.setze(x, y0 + 1, vorne, w.b(name, **pr))


def marktdeko(w, R, n=6, frei=4):
    """Verteilt Marktkram am Platzrand: Fässer, Kisten, Heuballen, Laternenpfähle, Bänke, Blumenkübel."""
    rng = w.rng
    for i in range(n):
        a = i / n * 2 * math.pi + rng.random() * 0.5
        d = max(frei, R * (0.55 + rng.random() * 0.25))
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if not w.frei(x, 1, z):
            continue
        art = i % 5
        if art == 0:
            w.setze(x, 1, z, w.b("barrel", facing="up", open=False))
            w.setze(x + 1, 1, z, w.b("barrel", facing="up", open=False), False)
            w.setze(x, 2, z, w.b("barrel", facing="up", open=False))
        elif art == 1:
            for y in range(1, 4):
                w.setze(x, y, z, w.b("spruce_fence"))
            w.setze(x, 4, z, w.b("lantern", hanging=False, waterlogged=False))
        elif art == 2:
            w.setze(x, 1, z, w.b("hay_block", axis="x"))
            w.setze(x, 1, z + 1, w.b("hay_block", axis="x"), False)
        elif art == 3:
            for k in (-1, 0, 1):
                w.setze(x + k, 1, z, treppe(w, "spruce", "north"), False)
        else:
            w.setze(x, 1, z, w.b("composter", level=0))
            w.setze(x, 2, z, w.b(["poppy", "dandelion", "cornflower"][i % 3]))


def mensch(w, rock="red_wool", haut="white_terracotta", haar="brown_wool"):
    return [(kap((0, 0, 0), (0, 2.6, 0), 0.75, 0.55), w.b(rock)), (kap((0, 2.6, 0), (0, 3.6, 0), 0.5, 0.45), w.b(rock)),
            (ell(0, 4.3, 0, 0.5, 0.55, 0.5), w.b(haut)), (ell(0, 4.6, -0.1, 0.55, 0.35, 0.55), w.b(haar))]


# ============================================================================ Bauten

def backhaus(seed, g=1):
    """Backhaus: ein kleines Fachwerkhaus mit gewölbtem, gemauertem Backofen an der Giebelseite, Brotlaiben auf
    der Auslage, Mehlsäcken, Holzstapel und einer Brezel als Zunftzeichen über der Tür."""
    w = _neu(seed)
    s = S[g]
    R = int(8 * s + 5)
    zellen = wiese(w, R, 0.1)
    pflaster(w, R * 0.85)
    B, T = int(3 * s + 5) | 1, int(2 * s + 5) | 1
    haus(w, 0, -2, B, T, 1, fachwerkwand(w), holz="dark_oak", H=4, dach=("brick", "mud_brick"), tuer_s="south")
    ox = B // 2 + 2
    for x in range(ox, ox + 3):
        for z in range(-4, 1):
            w.setze(x, 1, z, w.b("bricks"))
    kugel(w, ox + 1, 2, -2, 2.0, w.b("bricks"), ry=1.6)
    w.setze(ox + 1, 2, 0, w.b("furnace", facing="south", lit=True))
    for y in range(2, 7):
        w.setze(ox + 1, y, -4, w.b("bricks"))
    w.setze(ox + 1, 7, -4, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    bude(w, -B // 2 - 3, 3, B=5, T=3, farben=("brown_wool", "white_wool"),
         waren=[("hay_block", {"axis": "y"}), "cake", ("hay_block", {"axis": "x"})])
    for k in range(3):
        w.setze(2 + k, 1, 2, w.b("white_wool"))
    for k in range(3):
        for x in range(ox, ox + 3):
            w.setze(x, 1 + k // 2, 2 + k % 2, w.b("oak_log", axis="x"))
    baumrand(w, zellen, R, 2 + g, seed, innen=0.88)
    marktdeko(w, R, n=int(4 + 3 * s))
    return w


def marionettenbuehne(seed, g=1):
    """Marionettenbühne: ein bemalter Bühnenwagen mit rotem Vorhang, Kulissen und hängenden Holzpuppen an
    Fäden, davor Zuschauerbänke im Halbkreis und ein Ausrufer mit Glocke."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.1)
    pflaster(w, R * 0.7)
    B = int(4 * s + 5)
    T = int(2 * s + 3)
    zb = -int(R * 0.3)
    for x in range(-B, B + 1):
        for z in range(zb - T, zb + 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
            w.setze(x, 2, z, w.b("spruce_planks") if z < zb else w.b("air"))
            if z == zb - T or abs(x) == B:
                for y in range(3, 8):
                    w.setze(x, y, z, w.b("blue_terracotta") if (y + x) % 4 else w.b("yellow_terracotta"))
        for y in range(3, 8):
            if abs(x) == B or y == 7:
                w.setze(x, y, zb, w.b("red_terracotta"))
            elif y >= 6 or abs(x) >= B - 1:
                w.setze(x, y, zb, w.b("red_wool"))
    for k in range(3):
        x = -B + 2 + k * B // 2 + 1
        w.setze(x, 6, zb - 1, w.b("chain", axis="y", waterlogged=False))
        w.setze(x, 5, zb - 1, w.b("chain", axis="y", waterlogged=False))
        w.setze(x, 4, zb - 1, w.b(["red_wool", "lime_wool", "yellow_wool"][k]))
        w.setze(x, 3, zb - 1, w.b("oak_planks"))
    for sx in (-1, 1):
        for x in (sx * (B + 1),):
            for z in (zb - T, zb):
                w.setze(x, 1, z, w.b("spruce_fence"))
                w.setze(x, 0, z, w.b("spruce_log", axis="x"))
    for r in (4, 6, 8):
        for i in range(-3, 4):
            a = math.pi / 2 + i * 0.22
            x, z = round(math.cos(a) * r * s * 0.8), zb + round(math.sin(a) * r * s * 0.8)
            w.setze(x, 1, z, treppe(w, "spruce", "north"))
    figur(w, 0.6 * s + 0.3, mensch(w, "green_wool"), (-2, -1, -2), (2, 6, 2), pos=(B + 3, 1, zb + 3))
    baumrand(w, zellen, R, 2 + g, seed, innen=0.88)
    return w


def bogenschiessstand(seed, g=1):
    """Bogenschützen-Stand: eine überdachte Schützenlinie mit Bogenständer, eine Wiese mit Strohscheiben in
    verschiedenen Entfernungen, Pfeilköcher, Siegertafel und Wimpelketten."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.05, blumen=0.0)
    L = int(R * 0.75)
    for x in range(-4, 5):
        for z in (-L, -L + 2):
            w.setze(x, 0, z, w.b("spruce_planks"))
        for z in range(-L - 1, -L + 3):
            w.setze(x, 4, z, w.b(["red_wool", "yellow_wool"][(x + 10) % 2]))
    for x in (-4, 4):
        for z in (-L - 1, -L + 2):
            for y in range(1, 4):
                w.setze(x, y, z, w.b("spruce_fence"))
    w.setze(0, 1, -L, w.b("fletching_table"))
    for k in range(3 + g):
        z = -L + 6 + k * int((2 * L - 8) / (3 + g))
        x = (k % 3 - 1) * 3
        w.setze(x, 1, z, w.b("spruce_fence"))
        w.setze(x, 2, z, w.b("hay_block", axis="z"))
        w.setze(x, 3, z, w.b("target", power=0))
        w.setze(x + 1, 2, z, w.b("hay_block", axis="z"))
        w.setze(x - 1, 2, z, w.b("hay_block", axis="z"))
    for k in range(2 * L):
        z = -L + k
        y = 6 - round(math.sin(math.pi * k / (2 * L)) * 1.5)
        if k % 2 == 0:
            w.setze(-6, y, z, w.b(["red_wool", "yellow_wool", "blue_wool"][k % 3]))
    for z in (-L, L - 1):
        for y in range(1, 7):
            w.setze(-6, y, z, w.b("spruce_log", axis="y"))
    baumrand(w, zellen, R, 3 + g, seed, innen=0.9)
    return w


def gewuerzstand(seed, g=1):
    """Gewürzstand: eine orientalisch anmutende Bude mit Stoffbahnen in Purpur und Gold, offene Säcke voller
    roter, gelber und brauner Gewürze, hängende Kräuterbündel und Messingwaagen."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    wiese(w, R, 0.05)
    pflaster(w, R * 0.75)
    bude(w, 0, 0, B=int(3 * s + 5) | 1, T=3, farben=("purple_wool", "yellow_wool"),
         waren=["red_concrete_powder", "yellow_concrete_powder", "brown_concrete_powder", "orange_concrete_powder",
                "lime_concrete_powder"])
    B = int(3 * s + 5) | 1
    for k, f in enumerate(["red_concrete_powder", "orange_concrete_powder", "yellow_concrete_powder",
                           "brown_concrete_powder"]):
        x = -B // 2 + k * 2
        w.setze(x, 1, 3, w.b("brown_wool"))
        w.setze(x, 2, 3, w.b(f))
    for x in range(-B // 2 + 1, B // 2):
        w.setze(x, 3, 0, w.b("chain", axis="y", waterlogged=False))
        w.setze(x, 2, 0, w.b("flowering_azalea_leaves" if x % 2 else "azalea_leaves", persistent=True, distance=1,
                             waterlogged=False))
    w.setze(B // 2 + 2, 1, 1, w.b("heavy_weighted_pressure_plate", power=0) if False else w.b("light_weighted_pressure_plate", power=0))
    marktdeko(w, R, n=int(4 + 3 * s))
    return w


def kaesestand(seed, g=1):
    """Käsestand: Regale voller runder Käselaibe (gelbe und orange Blöcke) unter einem Holzdach, eine Käseharfe,
    Milchkannen, eine angeschnittene Riesenkäserad-Auslage und eine Kuh-Figur daneben."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    zellen = wiese(w, R, 0.05)
    pflaster(w, R * 0.85)
    B = int(3 * s + 5) | 1
    bude(w, 0, 0, B=B, T=3, farben=("yellow_wool", "white_wool"),
         waren=["yellow_terracotta", "orange_terracotta", "yellow_terracotta", "honeycomb_block"])
    for x in range(-B // 2 + 1, B // 2):
        w.setze(x, 2, -1, w.b("yellow_terracotta") if x % 2 else w.b("orange_terracotta"))
    kx, kz = B // 2 + 3, 2
    for x in range(kx - 2, kx + 3):
        for z in range(kz - 2, kz + 3):
            if math.hypot(x - kx, z - kz) <= 2.3 and not (x > kx and z > kz):
                w.setze(x, 1, z, w.b("yellow_terracotta"))
    for k in range(3):
        w.setze(-B // 2 - 2, 1, -1 + k, w.b("cauldron"))
    sch = w.b("black_wool")
    we = w.b("white_wool")
    teile = [(ell(0, 2.3, 0, 1.8, 1.0, 0.9), lambda x, y, z, *a: sch if (x + z) % 3 == 0 else we),
             (ell(1.9, 2.7, 0, 0.6, 0.55, 0.5), we), (ell(2.4, 2.5, 0, 0.35, 0.3, 0.35), w.b("pink_wool"))] + \
            [(kap((sx, 1.6, sz), (sx, 0, sz), 0.3), we) for sx in (-1.1, 1.1) for sz in (-0.5, 0.5)]
    figur(w, 0.6 * s + 0.4, teile, (-3, -1, -2), (3, 4, 2), pos=(-B // 2 - 4, 1, 3), winkel=0.4)
    _ = zellen
    marktdeko(w, R, n=int(4 + 3 * s))
    return w


def wahrsagerwagen(seed, g=1):
    """Wahrsagerwagen: ein bunt bemalter Wohnwagen mit gewölbtem Dach, Speichenrädern, Treppchen und Laternen,
    davor ein Tisch mit Kristallkugel unter einem Sternenzelt."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    zellen = wiese(w, R, 0.1)
    L = int(3 * s + 4)
    B = 2
    H = 4
    for x in range(-L, L + 1):
        for z in range(-B, B + 1):
            w.setze(x, 2, z, w.b("dark_oak_planks"))
            for y in range(3, 3 + H):
                bogen = y - 3 >= H - 1 - (abs(z) == B)
                if abs(z) == B or abs(x) == L or y == 2 + H:
                    farbe = "red_terracotta" if (x + y) % 4 else "yellow_terracotta"
                    if y > 3 + H - 2 and abs(z) == B:
                        farbe = "green_terracotta"
                    w.setze(x, y, z, w.b(farbe))
                else:
                    w.bloecke.pop((x, y, z), None)
                _ = bogen
        w.setze(x, 3 + H, 0, w.b("green_terracotta"))
    for x in (-L + 1, L - 1):
        for z in (-B - 1, B + 1):
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if abs(dx) + abs(dy) == 1 or (dx, dy) == (0, 0):
                        w.setze(x + dx, 2 + dy, z, w.b("dark_oak_fence") if (dx, dy) != (0, 0) else
                                w.b("stripped_dark_oak_log", axis="z"))
    for y in (3, 4):
        w.bloecke.pop((L, y, 0), None)
    w.setze(L + 1, 2, 0, treppe(w, "dark_oak", "west"))
    w.setze(L + 2, 1, 0, treppe(w, "dark_oak", "west"))
    for z in (-B, B):
        w.setze(0, 4, z, w.b("glass_pane"))
    tx = -L - 4
    for x in range(tx - 2, tx + 3):
        for z in range(-2, 3):
            w.setze(x, 4, z, w.b("blue_wool") if (x + z) % 3 else w.b("yellow_wool"))
            if abs(x - tx) == 2 and abs(z) == 2:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("dark_oak_fence"))
    w.setze(tx, 1, 0, w.b("dark_oak_fence"))
    w.setze(tx, 2, 0, w.b("purple_stained_glass"))
    laterne(w, L, 7, B + 1, kette=1)
    _ = zellen
    marktdeko(w, R, n=int(4 + 3 * s))
    return w


def zinngiesser(seed, g=1):
    """Zinngießer-Bude: ein Stand mit Schmelzofen und Gussformen, Regale voller Zinnkrüge, Teller und Figuren
    (Eisenstangen, Ketten), ein Blasebalg und ein Schild mit einem Krug."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    wiese(w, R, 0.05)
    pflaster(w, R * 0.85)
    B = int(3 * s + 5) | 1
    bude(w, 0, 0, B=B, T=3, farben=("gray_wool", "light_gray_wool"),
         waren=["iron_block", ("lantern", {"hanging": False, "waterlogged": False}), "iron_block",
                ("chain", {"axis": "x", "waterlogged": False})])
    ox = B // 2 + 2
    for y in range(1, 3):
        for z in (-1, 0):
            w.setze(ox, y, z, w.b("bricks"))
    w.setze(ox, 2, 1, w.b("blast_furnace", facing="south", lit=True))
    for y in range(3, 6):
        w.setze(ox, y, -1, w.b("bricks"))
    w.setze(ox, 6, -1, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    w.setze(ox + 1, 1, 1, w.b("cauldron"))
    for y in range(1, 4):
        w.setze(-B // 2 - 1, y, 2, w.b("spruce_fence"))
    w.setze(-B // 2 - 1, 4, 2, w.b("spruce_log", axis="x"))
    w.setze(-B // 2 - 2, 3, 2, w.b("chain", axis="y", waterlogged=False))
    w.setze(-B // 2 - 2, 2, 2, w.b("iron_block"))
    marktdeko(w, R, n=int(4 + 3 * s))
    return w


def metzgerei(seed, g=1):
    """Metzgerei: ein Fachwerkladen mit offener Theke, an Haken hängenden Schinken und Würsten (Ketten mit rotem
    Ton), einem Räucherschrank, Hackklotz und einem Schweinchen-Schild."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    zellen = wiese(w, R, 0.05)
    pflaster(w, R * 0.85)
    B, T = int(3 * s + 5) | 1, int(2 * s + 5) | 1
    haus(w, 0, -2, B, T, 1, fachwerkwand(w), holz="dark_oak", H=4, dach=("dark_oak", "spruce"), tuer_s="south")
    z1 = -2 + T // 2
    for x in range(-B // 2 + 1, B // 2):
        w.setze(x, 2, z1, w.b("air"))
        w.setze(x, 1, z1 + 1, w.b("dark_oak_slab", type="top", waterlogged=False))
        if x % 2:
            w.setze(x, 3, z1 + 1, w.b("chain", axis="y", waterlogged=False))
            w.setze(x, 2, z1 + 1, w.b("red_terracotta") if x % 4 == 1 else w.b("pink_terracotta"))
    w.setze(B // 2 + 2, 1, 0, w.b("smoker", facing="east", lit=True))
    w.setze(B // 2 + 2, 1, 2, w.b("stripped_oak_wood", axis="y"))
    pk = w.b("pink_terracotta")
    teile = [(ell(0, 1.5, 0, 1.4, 1.0, 0.9), pk), (ell(1.3, 1.7, 0, 0.6, 0.6, 0.6), pk),
             (ell(1.85, 1.6, 0, 0.25, 0.3, 0.35), w.b("pink_concrete"))] + \
            [(kap((sx, 1.0, sz), (sx, 0, sz), 0.25), pk) for sx in (-0.8, 0.8) for sz in (-0.45, 0.45)]
    figur(w, 0.6 * s + 0.4, teile, (-2, -1, -2), (3, 3, 2), pos=(-B // 2 - 3, 1, 3), winkel=0.6)
    _ = zellen
    marktdeko(w, R, n=int(4 + 3 * s))
    return w


def schuster(seed, g=1):
    """Schusterwerkstatt: ein schmales Fachwerkhaus mit Erker und Werkbank im Freien, Stiefel- und Lederstapel
    (braune Wolle), Leisten an der Wand und ein großer Holzstiefel als Zunftzeichen."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    zellen = wiese(w, R, 0.05)
    pflaster(w, R * 0.85)
    B, T = int(2 * s + 5) | 1, int(2 * s + 5) | 1
    top = haus(w, 0, -2, B, T, 1, fachwerkwand(w), holz="spruce", H=int(3 + 2 * s), dach=("spruce", "dark_oak"),
               tuer_s="south", steil=2)
    for x in range(B // 2 + 1, B // 2 + 4):
        w.setze(x, 1, 1, w.b("spruce_slab", type="top", waterlogged=False))
    w.setze(B // 2 + 2, 2, 1, w.b("brown_wool"))
    for k in range(3):
        w.setze(-B // 2 - 1 - k % 2, 1 + k // 2, 1, w.b("brown_wool") if k % 2 else w.b("brown_terracotta"))
    sx, sz = 0, -2 + T // 2 + 1
    for y, (dx, dz) in enumerate(((0, 0), (0, 0), (0, 0), (1, 0), (1, 0))):
        w.setze(sx + dx + 3, 4 + (y if y < 3 else 2), sz + 1, w.b("brown_terracotta"))
    w.setze(sx + 3, 3, sz + 1, w.b("spruce_fence"))
    _ = (top, zellen)
    marktdeko(w, R, n=int(4 + 3 * s))
    return w


def badestube(seed, g=1):
    """Badestube: ein Bader-Haus mit dampfenden Holzzubern unter einem Vordach, einem Kessel über dem Feuer,
    einem Barbierstuhl, Handtüchern auf der Leine und einem Brunnen."""
    w = _neu(seed)
    s = S[g]
    R = int(8 * s + 5)
    zellen = wiese(w, R, 0.05)
    pflaster(w, R * 0.85)
    B, T = int(4 * s + 5) | 1, int(2 * s + 5) | 1
    haus(w, 0, -3, B, T, 1, fachwerkwand(w), holz="oak", H=4, dach=("brick", "mud_brick"), tuer_s="south")
    z1 = -3 + T // 2
    for k in range(2 + g // 2):
        cx = -B // 2 + 2 + k * 4
        for x in range(cx - 1, cx + 2):
            for z in range(z1 + 2, z1 + 5):
                rand = abs(x - cx) == 1 or z in (z1 + 2, z1 + 4)
                w.setze(x, 1, z, w.b("spruce_planks") if rand else w.b("water", level=0))
    for x in range(-B // 2, B // 2 + 1):
        for z in range(z1 + 1, z1 + 6):
            w.setze(x, 4, z, w.b("oak_slab", type="bottom", waterlogged=False))
    for x in (-B // 2, B // 2):
        for y in range(1, 4):
            w.setze(x, y, z1 + 5, w.b("oak_fence"))
    w.setze(B // 2 + 2, 1, z1 + 2, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    w.setze(B // 2 + 2, 2, z1 + 2, w.b("cauldron"))
    for x in range(-B // 2 - 4, -B // 2):
        w.setze(x, 3, 0, w.b("white_carpet") if False else w.b("tripwire", attached=False, disarmed=False,
                                                                   east=True, west=True, north=False, south=False,
                                                                   powered=False))
        w.setze(x, 2, 0, w.b("white_wool") if x % 2 else w.b("light_blue_wool"))
    for x in (-B // 2 - 5, -B // 2):
        for y in range(1, 4):
            w.setze(x, y, 0, w.b("oak_fence"))
    _ = zellen
    marktdeko(w, R, n=int(4 + 3 * s))
    return w


def waffenhaendler(seed, g=1):
    """Waffenhändler: eine robuste Bude mit Waffenständern voller Schwerter und Speere (Blitzableiter, Eisen-
    gitter), Schilden in Wappenfarben, einer Rüstungspuppe und einem Schleifstein."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    wiese(w, R, 0.05)
    pflaster(w, R * 0.85)
    B = int(3 * s + 5) | 1
    bude(w, 0, 0, B=B, T=3, farben=("blue_wool", "yellow_wool"),
         waren=["iron_block", ("grindstone", {"face": "floor", "facing": "south"}), "anvil"])
    for x in range(-B // 2 - 4, -B // 2 - 1):
        w.setze(x, 1, 1, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x, 2, 1, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
        w.setze(x, 3, 1, w.b("iron_bars", waterlogged=False))
    for k in range(4):
        w.setze(-B // 2 + k * 2 - 1, 2, -2, w.b(["red_wool", "blue_wool", "yellow_wool", "white_wool"][k]))
    rx = B // 2 + 3
    w.setze(rx, 1, 1, w.b("oak_fence"))
    w.setze(rx, 2, 1, w.b("iron_block"))
    w.setze(rx, 3, 1, w.b("iron_block"))
    w.setze(rx, 4, 1, w.b("iron_bars", waterlogged=False))
    w.setze(rx - 1, 3, 1, w.b("iron_bars", waterlogged=False))
    w.setze(rx + 1, 3, 1, w.b("iron_bars", waterlogged=False))
    marktdeko(w, R, n=int(4 + 3 * s))
    return w


def musikantenbuehne(seed, g=1):
    """Musikantenbühne: ein Podest mit Holzdach und Wimpeln, darauf Musikanten-Figuren mit Trommel und Laute,
    davor ein Tanzplatz mit Strohballen zum Sitzen und Lichterketten zwischen Masten."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.05)
    pflaster(w, R * 0.75)
    A = int(2 * s + 3)
    zb = -int(R * 0.35)
    for x in range(-A - 1, A + 2):
        for z in range(zb - A, zb + 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
            w.setze(x, 2, z, w.b("spruce_slab", type="bottom", waterlogged=False) if z == zb else w.b("air"))
    for x in (-A - 1, A + 1):
        for z in (zb - A, zb):
            for y in range(2, 6):
                w.setze(x, y, z, w.b("spruce_log", axis="y"))
    satteldach(w, -A - 1, zb - A, A + 1, zb, 6, Dachmat(w, ["spruce", "dark_oak"]), first_x=True, ue=1,
               giebel=M(w, [("spruce_planks", 1)]), traufe="spruce")
    for k, (rock, x) in enumerate((("red_wool", -A + 1), ("green_wool", 0), ("blue_wool", A - 1))):
        figur(w, 0.55 * s + 0.35, mensch(w, rock), (-2, -1, -2), (2, 6, 2), pos=(x, 2, zb - A // 2))
    w.setze(A, 2, zb - 1, w.b("note_block", instrument="basedrum", note=0, powered=False))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6) + 2
        for y in range(1, 6):
            w.setze(x, y, z, w.b("spruce_fence"))
        w.setze(x, 6, z, w.b("lantern", hanging=False, waterlogged=False))
        a2 = (i + 1) / 6 * 2 * math.pi
        x2, z2 = round(math.cos(a2) * R * 0.6), round(math.sin(a2) * R * 0.6) + 2
        for k in range(1, 8):
            t = k / 8
            w.setze(round(x + (x2 - x) * t), 5 - round(math.sin(math.pi * t)), round(z + (z2 - z) * t),
                    w.b(["red_wool", "yellow_wool", "blue_wool"][k % 3]), False)
    for k in range(4):
        a = math.pi * 0.25 + k * 0.5
        w.setze(round(math.cos(a) * 4), 1, round(math.sin(a) * 4) + 3, w.b("hay_block", axis="x"))
    _ = zellen
    return w


def markthalle(seed, g=2):
    """Markthalle: ein großes Fachwerkgebäude, dessen Erdgeschoss eine offene Halle auf Steinbögen ist, in der
    Händler unter dem Dach ihre Tische aufgebaut haben; oben die Ratsstube mit Uhrtürmchen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.05)
    pflaster(w, R * 0.8)
    B, T = int(6 * s + 7), int(3 * s + 5)
    st = M(w, [("stone_bricks", 3), ("cracked_stone_bricks", 1), ("andesite", 1)])
    H1 = 4
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            rand = abs(x) == B or abs(z) == T
            pfeiler = rand and (x % 3 == 0 or abs(x) == B) and (z % 3 == 0 or abs(z) == T)
            for y in range(1, H1 + 1):
                if pfeiler or (rand and y == H1):
                    w.setze(x, y, z, st(x, y, z))
                elif rand and y == H1 - 1 and (x % 3 in (1, 2)):
                    w.setze(x, y, z, treppe(w, "stone_brick", "south" if z < 0 else "north", "top") if abs(z) == T
                            else w.b("stone_bricks"))
            w.setze(x, H1 + 1, z, w.b("spruce_planks"))
    fachwerk(w, -B - 1, -T - 1, B + 1, T + 1, H1 + 2, H1 + 5, fachwerkwand(w), holz="dark_oak", abstand=3)
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            for y in range(H1 + 2, H1 + 6):
                if abs(x) < B + 1 and abs(z) < T + 1:
                    w.bloecke.pop((x, y, z), None)
    first = satteldach(w, -B - 1, -T - 1, B + 1, T + 1, H1 + 6, Dachmat(w, ["dark_oak", "spruce"]), first_x=True,
                       ue=1, giebel=fachwerkwand(w), traufe="dark_oak", steil=1)
    for y in range(first - 1, first + int(3 * s + 2)):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) == 1 or abs(dz) == 1:
                    w.setze(dx, y, dz, w.b("dark_oak_planks"))
    w.setze(0, first + 1, 2, w.b("white_concrete"))
    kegeldach(w, 0, 0, first + int(3 * s + 2), 1, Dachmat(w, ["deepslate_tile"]), form="nadel", eckig=True,
              spitze="gold_block")
    rng = w.rng
    for k in range(int(4 * s + 2)):
        x = -B + 2 + k * 3
        if x > B - 2:
            break
        w.setze(x, 1, 0, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x, 2, 0, w.b(["melon", "pumpkin", "hay_block", "barrel"][k % 4],
                             **({"axis": "y"} if k % 4 == 2 else {"facing": "up", "open": False} if k % 4 == 3
                                else {})))
    _ = (zellen, rng)
    return w


def lebkuchenbude(seed, g=1):
    """Lebkuchenbude: ein Hexenhaus-artiger Stand mit Dach aus braunen und weißen Streifen wie Zuckerguss, Herzen
    aus rotem Ton an der Front, Bonbons in Gläsern und einer langen Schlange Zuckerstangen-Pfosten."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    wiese(w, R, 0.05)
    pflaster(w, R * 0.85)
    B = int(3 * s + 5) | 1
    bude(w, 0, 0, B=B, T=3, farben=("brown_wool", "white_wool"),
         waren=["red_terracotta", "brown_terracotta", "pink_terracotta", "red_terracotta"])
    for x in range(-B // 2, B // 2 + 1, 2):
        w.setze(x, 4, 2, w.b("red_concrete"))
    for k in range(4):
        x = -B // 2 - 2 + k * (B + 3) // 3
        for y in range(1, 4):
            w.setze(x, y, 4, w.b("red_concrete" if (y + k) % 2 else "white_concrete"))
    for k, f in enumerate(["pink_stained_glass", "lime_stained_glass", "yellow_stained_glass"]):
        w.setze(B // 2 + 2, 1 + k, 0, w.b(f))
    marktdeko(w, R, n=int(4 + 3 * s))
    return w


def pferdekoppel(seed, g=2):
    """Pferdekoppel mit Händler: eine umzäunte Koppel mit drei Pferde-Figuren in Braun, Schimmel und Rappe, ein
    Unterstand mit Heuraufe, Sättel auf einem Bock und das Zelt des Pferdehändlers."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.15)
    A = int(R * 0.6)
    for x in range(-A, A + 1):
        for z in (-A, A):
            w.setze(x, hoehe(w, x, z, 5) + 1, z, zaun(w, "oak"))
    for z in range(-A, A + 1):
        for x in (-A, A):
            if not (x == A and abs(z) < 2):
                w.setze(x, hoehe(w, x, z, 5) + 1, z, zaun(w, "oak"))
    farben = [("brown_terracotta", "black_wool"), ("white_terracotta", "light_gray_wool"),
              ("black_terracotta", "black_wool")]
    for k in range(2 + g // 2):
        f, m = farben[k % 3]
        F, Mn = w.b(f), w.b(m)
        teile = [(ell(0, 3.4, 0, 2.0, 1.1, 0.9), F), (kap((1.6, 3.8, 0), (2.6, 5.4, 0), 0.6, 0.5), F),
                 (ell(3.0, 5.4, 0, 0.9, 0.5, 0.45), F), (kap((1.4, 4.5, 0), (2.4, 5.9, 0), 0.25), Mn),
                 (kap((-2.0, 3.8, 0), (-2.6, 2.2, 0), 0.3, 0.2), Mn)] + \
                [(kap((sx, 3.0, sz), (sx, 0, sz), 0.3), F) for sx in (-1.3, 1.3) for sz in (-0.45, 0.45)]
        x, z = -A + 4 + k * int(A * 0.7), -A // 3 + (k % 2) * A // 2
        figur(w, 0.6 * s + 0.4, teile, (-3, -1, -2), (4, 7, 2), pos=(x, hoehe(w, x, z, 5) + 1, z), winkel=k * 1.1)
    for x in range(-A + 1, -A + 6):
        for z in (A - 4, A - 1):
            w.setze(x, 4, z, w.b("oak_slab", type="bottom", waterlogged=False))
        w.setze(x, 4, A - 2, w.b("oak_slab", type="bottom", waterlogged=False))
        w.setze(x, 4, A - 3, w.b("oak_slab", type="bottom", waterlogged=False))
    for x in (-A + 1, -A + 5):
        for z in (A - 4, A - 1):
            for y in range(1, 4):
                w.setze(x, y, z, w.b("oak_fence"))
    w.setze(-A + 3, 1, A - 2, w.b("hay_block", axis="y"))
    tx = A + 4
    for k in range(4):
        for x in range(tx - 3 + k, tx + 4 - k):
            for z in range(-3 + k, 4 - k):
                if x in (tx - 3 + k, tx + 3 - k) or z in (-3 + k, 3 - k):
                    w.setze(x, 1 + k, z, w.b("red_wool" if (x + z) % 2 else "white_wool"))
    w.setze(tx - 3, 1, 0, w.b("air"))
    _ = zellen
    return w


def taubenschlag(seed, g=1):
    """Taubenschlag-Turm: ein runder Fachwerkturm mit vielen kleinen Einfluglöchern und Sitzstangen, Kegeldach
    mit Wetterhahn, umflattert von weißen Tauben-Figuren auf dem Dach und am Boden."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, 0.1)
    rt = 2.2 * s + 2
    H = int(7 * s + 6)
    st = M(w, [("cobblestone", 2), ("stone", 1)])
    for y in range(1, H):
        for x, z in kreisrand(rt):
            if y < 3:
                w.setze(x, y, z, st(x, y, z))
            elif y % 3 == 1 and (x + z) % 2 == 0:
                w.setze(x, y, z, w.b("dark_oak_trapdoor", facing="north", half="top", open=False, powered=False,
                                     waterlogged=False))
            else:
                w.setze(x, y, z, w.b("white_terracotta") if (x + y + z) % 5 else w.b("dark_oak_log", axis="y"))
    kegeldach(w, 0, 0, H, int(rt), Dachmat(w, ["dark_oak", "spruce"]), form="kegel", spitze="lightning_rod")
    we = w.b("white_wool")
    rng = w.rng
    for k in range(5 + 3 * g):
        a = rng.random() * 6.28
        d = rt + 1 + rng.random() * (R - rt - 3)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = hoehe(w, x, z, H + 10) + 1
        w.setze(x, y, z, we, False)
        w.setze(x + 1, y, z, w.b("light_gray_wool"), False)
    for y in (1, 2):
        w.bloecke.pop((0, y, round(rt)), None)
    baumrand(w, zellen, R, 2 + g, seed, innen=0.88)
    return w


def schreibstube(seed, g=1):
    """Schreibstube: ein schmales Haus mit Erkerfenster, in dem ein Schreiber am Pult sitzt; Regale mit
    Büchern, Pergamentrollen (weiße Teppiche), Siegelwachs und ein Schild mit Feder über der Tür."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    wiese(w, R, 0.05)
    pflaster(w, R * 0.85)
    B, T = int(2 * s + 5) | 1, int(2 * s + 5) | 1
    haus(w, 0, -2, B, T, 1, fachwerkwand(w), holz="dark_oak", H=int(3 + 2 * s), dach=("deepslate_tile",
                                                                                      "dark_oak"),
         tuer_s="south", steil=2)
    for x in range(-B // 2 + 1, B // 2):
        w.setze(x, 1, -2 - T // 2 + 1, w.b("bookshelf"))
        w.setze(x, 2, -2 - T // 2 + 1, w.b("bookshelf"))
    w.setze(0, 1, -1, w.b("lectern", facing="south", has_book=True, powered=False))
    ex, ez = B // 2 + 1, -2
    for y in range(2, 4):
        for z in (ez - 1, ez, ez + 1):
            w.setze(ex, y, z, w.b("glass_pane"))
    w.setze(ex, 1, ez, w.b("dark_oak_stairs", facing="west", half="top", shape="straight", waterlogged=False))
    w.setze(ex, 4, ez, w.b("dark_oak_slab", type="bottom", waterlogged=False))
    w.setze(2, 3, -2 + T // 2 + 1, w.b("white_wool"))
    w.setze(2, 4, -2 + T // 2 + 1, w.b("spruce_fence"))
    marktdeko(w, R, n=int(4 + 3 * s))
    return w


def gefluegelmarkt(seed, g=1):
    """Geflügelmarkt: Weidenkäfige mit Hühnern und Gänsen (weiße, braune Figuren) auf Tischen, ein freilaufendes
    Federvieh-Gehege, Eierkörbe und ein Brunnen zum Tränken."""
    w = _neu(seed)
    s = S[g]
    R = int(8 * s + 5)
    zellen = wiese(w, R, 0.05)
    pflaster(w, R * 0.8)
    rng = w.rng
    for k in range(3 + g):
        x0, z0 = -int(R * 0.4) + k * 3, -int(R * 0.3)
        w.setze(x0, 1, z0, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x0, 2, z0, w.b("white_wool") if k % 2 else w.b("brown_wool"))
        w.setze(x0, 3, z0, w.b("spruce_trapdoor", facing="north", half="bottom", open=False, powered=False,
                               waterlogged=False))
    A = int(4 * s + 3)
    px, pz = int(R * 0.25), int(R * 0.25)
    for x in range(px - A, px + A + 1):
        for z in (pz - A, pz + A):
            w.setze(x, hoehe(w, x, z, 4) + 1, z, zaun(w, "oak"))
    for z in range(pz - A, pz + A + 1):
        for x in (px - A, px + A):
            w.setze(x, hoehe(w, x, z, 4) + 1, z, zaun(w, "oak"))
    for k in range(5 + 2 * g):
        x, z = px - A + 1 + int(rng.random() * (2 * A - 2)), pz - A + 1 + int(rng.random() * (2 * A - 2))
        f = w.b("white_wool" if rng.random() < 0.6 else "brown_wool")
        teile = [(ell(0, 1.0, 0, 0.8, 0.6, 0.55), f), (ell(0.7, 1.7, 0, 0.35, 0.35, 0.3), f),
                 (ell(1.05, 1.65, 0, 0.2, 0.12, 0.12), w.b("orange_concrete")),
                 (ell(0.7, 2.1, 0, 0.1, 0.15, 0.08), w.b("red_concrete"))]
        figur(w, 0.6 * s + 0.4, teile, (-1, -1, -1), (2, 3, 1), pos=(x, hoehe(w, x, z, 4) + 1, z),
              winkel=rng.random() * 6.28)
    w.setze(-int(R * 0.4), 1, int(R * 0.3), w.b("water_cauldron", level=3))
    for k in range(2):
        w.setze(-int(R * 0.2) + k, 1, int(R * 0.35), w.b("composter", level=8))
    marktdeko(w, R, n=int(4 + 3 * s))
    return w


def wechselstube(seed, g=1):
    """Wechselstube: ein steinernes Kontorhaus mit vergitterten Fenstern und einer Tresen-Luke, Goldstapeln und
    Waagen auf dem Tisch, schweren Truhen und einem Wappenschild mit Münze über dem Eingang."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    wiese(w, R, 0.05)
    pflaster(w, R * 0.85)
    B, T = int(3 * s + 5) | 1, int(2 * s + 5) | 1
    st = M(w, [("stone_bricks", 3), ("cracked_stone_bricks", 1), ("chiseled_stone_bricks", 0.3)])
    haus(w, 0, -2, B, T, 1, st, holz="dark_oak", H=4, dach=("deepslate_tile", "cobbled_deepslate"), tuer_s="south",
         fenster=False, sockel=M(w, [("cobbled_deepslate", 1)]))
    z1 = -2 + T // 2
    for x in range(-B // 2 + 1, B // 2, 2):
        w.setze(x, 2, z1, w.b("iron_bars", waterlogged=False))
    w.setze(-2, 2, z1, w.b("air"))
    w.setze(-2, 1, z1 + 1, w.b("dark_oak_slab", type="top", waterlogged=False))
    w.setze(-2, 2, z1 + 1, w.b("gold_block"))
    for x in range(-B // 2 + 1, B // 2):
        w.setze(x, 1, -2 - T // 2 + 1, w.b("chest", facing="south", type="single", waterlogged=False) if x % 2 else
                w.b("gold_block"))
    w.setze(0, 4, z1 + 1, w.b("yellow_wool"))
    w.setze(1, 4, z1 + 1, w.b("blue_wool"))
    marktdeko(w, R, n=int(4 + 3 * s))
    return w


def holzriesenrad(seed, g=2):
    """Holzriesenrad: ein großes, von Knechten im Laufrad angetriebenes Riesenrad aus Holzbalken mit sechs
    offenen Gondeln, einem Kassenhäuschen und einer Warteschlange zwischen Seilen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.05)
    pflaster(w, R * 0.6)
    Rr = 6 * s + 4
    yc = int(Rr) + 3
    for k in range(int(Rr * 8)):
        a = k / (Rr * 8) * 2 * math.pi
        for dz in (-2, 2):
            w.setze(round(math.cos(a) * Rr), yc + round(math.sin(a) * Rr), dz, w.b("spruce_planks"))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        for k in range(int(Rr)):
            for dz in (-2, 2):
                w.setze(round(math.cos(a) * k), yc + round(math.sin(a) * k), dz, w.b("spruce_log", axis="y"), False)
    for z in range(-3, 4):
        w.setze(0, yc, z, w.b("dark_oak_log", axis="z"))
    for sx in (-1, 1):
        for dz in (-3, 3):
            for k in range(yc):
                w.setze(sx * round(k * 0.4), yc - k, dz, w.b("dark_oak_log", axis="y"))
    for i in range(6):
        a = i / 6 * 2 * math.pi + 0.2
        gx, gy = round(math.cos(a) * Rr), yc + round(math.sin(a) * Rr)
        for dz in (-1, 0, 1):
            w.setze(gx, gy - 1, dz, w.b("spruce_slab", type="bottom", waterlogged=False))
            w.setze(gx, gy - 2, dz, w.b(["red_wool", "blue_wool", "yellow_wool"][i % 3]))
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if abs(math.hypot(dx, dy) - 2) < 0.6:
                w.setze(dx + int(Rr) + 3, 3 + dy, 4, w.b("oak_planks"))
    hx = -int(Rr) - 4
    for x in range(hx - 1, hx + 2):
        for z in range(3, 6):
            if abs(x - hx) == 1 or z in (3, 5):
                for y in range(1, 3):
                    w.setze(x, y, z, w.b("oak_planks"))
            w.setze(x, 3, z, w.b("red_wool"))
    _ = zellen
    return w


MARKT3 = {
    "backhaus": ("Backhaus", backhaus),
    "marionettenbuehne": ("Marionettenbühne", marionettenbuehne),
    "bogenschiessstand": ("Bogenschützen-Stand", bogenschiessstand),
    "gewuerzstand": ("Gewürzstand", gewuerzstand),
    "kaesestand": ("Käsestand", kaesestand),
    "wahrsagerwagen": ("Wahrsagerwagen", wahrsagerwagen),
    "zinngiesser": ("Zinngießer-Bude", zinngiesser),
    "metzgerei": ("Metzgerei", metzgerei),
    "schuster": ("Schusterwerkstatt", schuster),
    "badestube": ("Badestube", badestube),
    "waffenhaendler": ("Waffenhändler", waffenhaendler),
    "musikantenbuehne": ("Musikantenbühne", musikantenbuehne),
    "markthalle": ("Markthalle", markthalle),
    "lebkuchenbude": ("Lebkuchenbude", lebkuchenbude),
    "pferdekoppel": ("Pferdekoppel mit Händler", pferdekoppel),
    "taubenschlag": ("Taubenschlag-Turm", taubenschlag),
    "schreibstube": ("Schreibstube", schreibstube),
    "gefluegelmarkt": ("Geflügelmarkt", gefluegelmarkt),
    "wechselstube": ("Wechselstube", wechselstube),
    "holzriesenrad": ("Holzriesenrad", holzriesenrad),
}

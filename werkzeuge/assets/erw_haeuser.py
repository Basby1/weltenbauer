"""Häuser III – zwanzig weitere fein gebaute Häuser: Brauhaus, Bootshaus, Uhrmacherhaus, Maleratelier,
Musikantenhaus, Kanalhaus, Pförtnerhaus, Glockengießerei, Gewürzhändler, Hutmacher, Teestube, Fischräucherei,
Brückenhaus, Hanghaus, Kreuzgiebelhaus, Dreigiebelhaus, Schieferhaus, Blumenladen, Lehmhaus und Weinstube."""

from __future__ import annotations

import math

from fantasie2 import garten
from feinbau import (Dachmat, Mix, balkon, fachwerk, fenster, fensterreihe, gaube, kamin, kegeldach, kragsteine, kram,
                     laterne, mauer, platte, satteldach, sockel, stamm, treppe, tuer, zaun)
from flora import _neu
from himmelsstadt2 import STILE, haus

S = [0.6, 1.0, 1.6, 2.5]

STILE.setdefault("schiefer", dict(sockel=[("cobbled_deepslate", 2), ("deepslate_bricks", 1)],
                                  wand=[("deepslate_tiles", 2), ("polished_deepslate", 1), ("deepslate_bricks", 1)],
                                  fuell=[("deepslate_tiles", 2), ("polished_deepslate", 1)], holz="dark_oak",
                                  dach=["deepslate_tile", "cobbled_deepslate", "deepslate_brick"]))
STILE.setdefault("lehm", dict(sockel=[("packed_mud", 2), ("mud_bricks", 1)],
                              wand=[("packed_mud", 2), ("mud_bricks", 1), ("smooth_sandstone", 1)],
                              fuell=[("packed_mud", 2), ("mud_bricks", 1)], holz="jungle",
                              dach=["mud_brick", "brick", "mcw:brown_terracotta"]))
STILE.setdefault("ziegel", dict(sockel=[("stone_bricks", 2), ("cobblestone", 1)],
                                wand=[("bricks", 4), ("mud_bricks", 1), ("granite", 1)],
                                fuell=[("bricks", 3), ("white_terracotta", 1)], holz="dark_oak",
                                dach=["mcw:red_terracotta", "brick", "deepslate_tile"]))


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def schild(w, x, y, z, seite, farbe="oak"):
    dx, dz = {"south": (0, 1), "north": (0, -1), "east": (1, 0), "west": (-1, 0)}[seite]
    w.setze(x + dx, y, z + dz, w.b("spruce_fence", north=False, south=False, east=dx != 0, west=dx != 0,
                                   waterlogged=False), False)
    w.setze(x + 2 * dx, y, z + 2 * dz, w.b("chain", axis="y", waterlogged=False), False)
    w.setze(x + 2 * dx, y - 1, z + 2 * dz, w.b(f"{farbe}_planks"), False)


def grund(seed, g, R=9):
    w = _neu(seed)
    s = S[g]
    zl = garten(w, R * s + 4, seed=seed, baeume=1 + g // 2)
    return w, s, zl


def B_(s, b):
    return max(5, int(b * (0.6 + 0.4 * s)) | 1)


# ============================================================================ Häuser

def brauhaus(seed, g=1):
    """Brauhaus: ein breites Ziegelhaus mit großen Rundbogentoren, durch die man kupferne Braukessel sieht, ein
    Malzspeicher mit Aufzugsluke, Bierfässer und ein Wirtshausschild."""
    w, s, zl = grund(seed, g, 10)
    B, T = B_(s, 13), B_(s, 9)
    first = haus(w, 0, 0, B, T, 1, "ziegel", geschosse=2 + (g > 1), tuer_s="south")
    for x in (-B // 2 + 2, B // 2 - 2):
        for y in range(1, 4):
            w.bloecke.pop((x, y, T // 2), None)
        w.setze(x, 1, T // 2 - 2, w.b("waxed_copper_block"))
        w.setze(x, 2, T // 2 - 2, w.b("waxed_cut_copper"))
    schild(w, 2, 4, T // 2, "south")
    kram(w, B // 2 + 2, 1, 2, 5)
    return w


def bootshaus(seed, g=1):
    """Bootshaus: ein Holzhaus auf Pfählen halb über dem Wasser, mit großem Bootstor, Ruderboot darin, Steg,
    Netzen und einer Wohnstube mit Balkon im Obergeschoss."""
    from boote import ruderboot
    from lib import einfuegen
    w, s, zl = grund(seed, g, 10)
    for (x, z) in zl:
        if z > 1:
            for y in (0, -1):
                w.setze(x, y, z, w.b("water", level=0))
            w.bloecke.pop((x, 1, z), None)
    B, T = B_(s, 9), B_(s, 9)
    for (x, z) in ((-B // 2, 2), (B // 2, 2), (-B // 2, T), (B // 2, T)):
        for y in range(-2, 2):
            w.setze(x, y, z, stamm(w, "spruce", geschaelt=False))
    for x in range(-B // 2, B // 2 + 1):
        for z in range(-T // 2 + 2, T + 1):
            if abs(x) == B // 2 or z < 3:
                w.setze(x, 1, z, w.b("spruce_planks"))
    haus(w, 0, T // 2, B, T, 2, "fachwerk", geschosse=2, tuer_s="west", balk=True)
    for x in range(-B // 2 + 2, B // 2 - 1):
        for y in range(2, 5):
            w.bloecke.pop((x, y, T // 2 + T // 2), None)
    einfuegen(w, ruderboot(seed, 0), 0, 0, T // 2 + 1)
    for z in range(T, T + 6):
        w.setze(B // 2 + 1, 1, z, w.b("spruce_planks"))
    return w


def uhrmacherhaus(seed, g=1):
    """Uhrmacherhaus: ein schmales, hohes Giebelhaus mit einer großen Uhr im Giebel, einem Schaufenster voller
    Taschenuhren, Zahnrad-Schild und einem Türmchen mit Glocke."""
    w, s, zl = grund(seed, g)
    B, T = B_(s, 7), B_(s, 9)
    first = haus(w, 0, 0, B, T, 1, "blau", geschosse=3, tuer_s="south", first_x=False)
    yc = 1 + 4 * 3 + 2
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx * dx + dy * dy <= 5:
                w.setze(dx, yc + dy, T // 2 + 2, w.b("white_concrete" if dx * dx + dy * dy < 4 else "gold_block"),
                        False)
    w.setze(0, yc, T // 2 + 3, w.b("black_concrete"), False)
    w.setze(0, yc + 1, T // 2 + 3, w.b("black_concrete"), False)
    w.setze(1, yc, T // 2 + 3, w.b("black_concrete"), False)
    for x in (-1, 1):
        w.setze(x, 2, T // 2, w.b("glass"))
    schild(w, -2, 4, T // 2, "south", "spruce")
    return w


def maleratelier(seed, g=1):
    """Maleratelier: ein Haus mit riesigem, schrägem Nordfenster im Dach, Staffeleien auf der Terrasse, bunten
    Farbtöpfen und einem verwilderten Blumengarten."""
    w, s, zl = grund(seed, g)
    B, T = B_(s, 9), B_(s, 7)
    first = haus(w, 0, 0, B, T, 1, "terrakotta", geschosse=2, tuer_s="south", first_x=True)
    for x in range(-B // 2 + 2, B // 2 - 1):
        for k in range(3):
            w.setze(x, 9 + k, -T // 2 + k, w.b("glass"), True)
    for k in range(2):
        x = B // 2 + 2 + k * 2
        w.setze(x, 1, 3, zaun(w, "spruce"))
        w.setze(x, 2, 3, w.b("white_wool"))
        w.setze(x, 1, 5, w.b(["red_wool", "blue_wool"][k]))
    return w


def musikantenhaus(seed, g=1):
    """Musikantenhaus: ein fröhliches, buntes Fachwerkhaus mit Balkon für Ständchen, Notenblatt-Fensterläden,
    einer Glocke am Giebel und Notenblöcken im Hof."""
    w, s, zl = grund(seed, g)
    B, T = B_(s, 9), B_(s, 7)
    haus(w, 0, 0, B, T, 1, "fachwerk", geschosse=2, tuer_s="south", balk=True)
    w.setze(0, 13, T // 2 + 1, w.b("bell", attachment="single_wall", facing="south", powered=False), False)
    for k in range(4):
        w.setze(-B // 2 + 1 + k * 2, 1, T // 2 + 3, w.b("note_block", instrument="harp", note=k * 3, powered=False))
    w.setze(B // 2 + 2, 1, 0, w.b("jukebox", has_record=False))
    return w


def kanalhaus(seed, g=1):
    """Kanalhaus: ein schmales, hohes Kaufmannshaus direkt an einem Kanal, die Haustür über eine kleine Treppe am
    Wasser, Lastenkran am Giebel, Blumenkästen und Bootsanleger."""
    w, s, zl = grund(seed, g)
    for (x, z) in zl:
        if z > 5 * s + 1:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("water", level=0))
            w.bloecke.pop((x, 1, z), None)
    B, T = B_(s, 7), B_(s, 9)
    first = haus(w, 0, 0, B, T, 2, "ziegel", geschosse=3 + (g > 1), tuer_s="south", first_x=False)
    top = 2 + 4 * (3 + (g > 1))
    for k in range(3):
        w.setze(0, top + 2, T // 2 + 1 + k, stamm(w, "dark_oak", "z"), False)
    for y in range(top - 2, top + 2):
        w.setze(0, y, T // 2 + 3, w.b("chain", axis="y", waterlogged=False), False)
    for k in range(int(5 * s + 1) - T // 2):
        for x in range(-1, 2):
            w.setze(x, 1, T // 2 + 1 + k, w.b("stone_bricks"))
    return w


def pfoertnerhaus(seed, g=1):
    """Pförtnerhaus: ein zierliches Torhaus neben einem schmiedeeisernen Tor zwischen Steinpfeilern mit Kugeln,
    dahinter beginnt eine Allee, ein Laternenpfahl und ein Briefkasten."""
    w, s, zl = grund(seed, g)
    B, T = B_(s, 7), B_(s, 5)
    haus(w, -B, 0, B, T, 1, "stein", geschosse=1 + (g > 1), tuer_s="east")
    for sx in (2, 7):
        for y in range(1, 5):
            w.setze(sx, y, 0, w.b("stone_bricks"))
        w.setze(sx, 5, 0, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                              waterlogged=False))
    for x in range(3, 7):
        for y in range(1, 4):
            w.setze(x, y, 0, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
    for z in range(-10, 0, 3):
        for sx in (2, 7):
            w.setze(sx, 1, z, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False))
    return w


def glockengiesserei(seed, g=1):
    """Glockengießerei: eine hohe Werkhalle mit Schmelzofen und Schornstein, vor der Tür hängt eine frisch gegossene
    Bronzeglocke in einem Holzgestell, Formen aus Lehm liegen im Hof."""
    w, s, zl = grund(seed, g, 10)
    B, T = B_(s, 11), B_(s, 7)
    haus(w, 0, 0, B, T, 1, "ziegel", geschosse=1 + (g > 1), tuer_s="south")
    for y in range(1, 12):
        for dx in (0, 1):
            for dz in (0, 1):
                w.setze(B // 2 + 1 + dx, y, -T // 2 + dz, w.b("bricks"))
    w.setze(B // 2 + 1, 12, -T // 2, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    for (x, z) in ((-3, T // 2 + 4), (3, T // 2 + 4)):
        for y in range(1, 5):
            w.setze(x, y, z, stamm(w, "dark_oak", geschaelt=False))
    for x in range(-3, 4):
        w.setze(x, 5, T // 2 + 4, stamm(w, "dark_oak", "x", geschaelt=False))
    w.setze(0, 4, T // 2 + 4, w.b("bell", attachment="ceiling", facing="north", powered=False))
    for k in range(3):
        w.setze(-B // 2 + k * 2, 1, T // 2 + 6, w.b("packed_mud"))
    return w


def gewuerzhaendler(seed, g=1):
    """Gewürzhändler: ein orientalisch angehauchtes Ladenhaus mit Markise aus gestreiftem Stoff, offenen Säcken
    voller bunter Gewürze vor der Tür und einem Lagerboden unterm Dach."""
    w, s, zl = grund(seed, g)
    B, T = B_(s, 9), B_(s, 7)
    haus(w, 0, 0, B, T, 1, "lehm", geschosse=2, tuer_s="south")
    for x in range(-B // 2, B // 2 + 1):
        for k in range(2):
            w.setze(x, 4 - k, T // 2 + 1 + k, w.b("red_wool" if x % 2 else "white_wool"), False)
    farben = ["orange_concrete_powder", "red_concrete_powder", "yellow_concrete_powder", "brown_concrete_powder",
              "lime_concrete_powder"]
    for k in range(5):
        x = -B // 2 + 1 + k * 2
        w.setze(x, 1, T // 2 + 3, w.b("barrel", facing="up", open=True))
        w.setze(x, 2, T // 2 + 3, w.b(farben[k]))
    return w


def hutmacher(seed, g=1):
    """Hutmacherladen: ein verwinkeltes Eckhaus mit Rundturm, dessen Dach ein riesiger Zylinderhut ist, Schaufenster
    voller Hüte und ein Schild in Hutform."""
    w, s, zl = grund(seed, g)
    B, T = B_(s, 9), B_(s, 7)
    haus(w, 0, 0, B, T, 1, "blau", geschosse=2, tuer_s="south")
    cx, cz = B // 2 + 1, T // 2 + 1
    r = 2
    for y in range(1, 10):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                d = math.hypot(dx, dz)
                if r - 0.8 < d <= r + 0.3:
                    w.setze(cx + dx, y, cz + dz, w.b("calcite"))
    for dx in range(-r - 2, r + 3):
        for dz in range(-r - 2, r + 3):
            d = math.hypot(dx, dz)
            if d <= r + 2:
                w.setze(cx + dx, 10, cz + dz, w.b("black_concrete"))
            if d <= r + 0.4:
                for y in range(11, 15):
                    w.setze(cx + dx, y, cz + dz, w.b("red_concrete" if y == 11 else "black_concrete"))
    return w


def teestube(seed, g=1):
    """Teestube: ein kleines, verspieltes Haus mit Erkerfenstern, rot-weiß gestreifter Markise, Tischchen mit
    Teekannen im Vorgarten und Rosen am Zaun."""
    w, s, zl = grund(seed, g)
    B, T = B_(s, 9), B_(s, 7)
    haus(w, 0, 0, B, T, 1, "fachwerk", geschosse=2, tuer_s="south")
    for x in range(-B // 2, B // 2 + 1):
        w.setze(x, 4, T // 2 + 1, w.b("red_wool" if x % 2 else "white_wool"), False)
    for k in range(2):
        x = -2 + k * 4
        w.setze(x, 1, T // 2 + 4, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                      waterlogged=False))
        w.setze(x, 2, T // 2 + 4, w.b("spruce_pressure_plate", powered=False))
        w.setze(x + 1, 1, T // 2 + 4, treppe(w, "spruce", "west"))
        w.setze(x, 3, T // 2 + 4, w.b("flower_pot")) if False else None
    for (x, z) in zl:
        if math.hypot(x, z) > 9 * s + 2 and w.rng.random() < 0.3 and w.frei(x, 2, z):
            w.setze(x, 2, z, w.b("rose_bush", half="lower") if w.frei(x, 3, z) and False else w.b("poppy"))
    return w


def fischraeucherei(seed, g=1):
    """Fischräucherei: eine dunkle Holzhütte mit rauchendem Räucherturm, Fische hängen an Stangen, Netze und Körbe,
    ein kleiner Steg in einen Teich."""
    w, s, zl = grund(seed, g)
    for (x, z) in zl:
        if math.hypot(x - 6 * s, z - 5 * s) < 4 * s + 1:
            w.setze(x, 0, z, w.b("water", level=0))
            w.bloecke.pop((x, 1, z), None)
    B, T = B_(s, 7), B_(s, 5)
    haus(w, -2, -2, B, T, 1, "schiefer", geschosse=1, tuer_s="south", schorn=False)
    for y in range(1, 10):
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                if abs(dx) == 1 or abs(dz) == 1:
                    w.setze(-2 - B // 2 - 2 + dx, y, -2 + dz, w.b("spruce_planks" if y % 3 else "dark_oak_planks"))
    w.setze(-2 - B // 2 - 2, 9, -2, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    for x in range(2, 6):
        w.setze(x, 3, -4, w.b("spruce_fence", east=True, west=True, north=False, south=False, waterlogged=False))
        w.setze(x, 2, -4, w.b("orange_terracotta"))
    return w


def brueckenhaus(seed, g=2):
    """Brückenhaus: ein Fachwerkhaus, das auf einer steinernen Bogenbrücke quer über einen Bach gebaut ist, mit
    Durchgang unten, Erkern über dem Wasser und Wasserrad an der Seite."""
    w, s, zl = grund(seed, g, 10)
    for (x, z) in zl:
        if abs(x) < 2 * s + 2:
            for y in (0, -1):
                w.setze(x, y, z, w.b("water", level=0))
            w.bloecke.pop((x, 1, z), None)
    B, T = B_(s, 9), B_(s, 7)
    st = M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 1)])
    for x in range(-B // 2 - 1, B // 2 + 2):
        for z in range(-T // 2, T // 2 + 1):
            for y in range(-1, 4):
                bogen = math.hypot(x, y + 1) < 2.5 * s + 1.5 and abs(z) < T // 2
                if not bogen:
                    w.setze(x, y, z, st(x, y, z))
    haus(w, 0, 0, B, T, 5, "fachwerk", geschosse=2, tuer_s="east")
    return w


def hanghaus(seed, g=1):
    """Hanghaus: ein Haus an einem steilen Hang, vorne auf hohen Holzstützen mit umlaufendem Balkon, hinten in den
    Fels gebaut, Treppen führen den Hang hinauf."""
    w, s, zl = grund(seed, g)
    for (x, z) in zl:
        h = max(0, int(-z * 0.6))
        for y in range(1, h + 1):
            w.setze(x, y, z, w.b("stone" if y < h else "grass_block", **({} if y < h else {"snowy": False})))
    B, T = B_(s, 9), B_(s, 7)
    y0 = int(T * 0.6) + 2
    for (x, z) in ((-B // 2, T // 2), (B // 2, T // 2), (0, T // 2)):
        for y in range(1, y0):
            w.setze(x, y, z, stamm(w, "spruce", geschaelt=False))
    haus(w, 0, 0, B, T, y0, "fachwerk", geschosse=2, tuer_s="east", balk=True)
    for k in range(y0):
        w.setze(B // 2 + 2, y0 - k, T // 2 - k, treppe(w, "stone_brick", "north"), False)
    return w


def kreuzgiebelhaus(seed, g=1):
    """Kreuzgiebelhaus: ein Bauernhaus mit zwei sich kreuzenden Satteldächern und vier Giebeln, jeder mit Fenster
    und Blumenkasten, Kamin in der Mitte, Holzbank an der Wand."""
    w, s, zl = grund(seed, g)
    B, T = B_(s, 11), B_(s, 7)
    haus(w, 0, 0, B, T, 1, "fachwerk", geschosse=1, tuer_s="south", first_x=True, schorn=False)
    haus(w, 0, 0, T, B, 1, "fachwerk", geschosse=1, tuer_s="east", first_x=False, schorn=False)
    kamin(w, 0, 0, 5, 12, M(w, [("bricks", 1)]))
    return w


def dreigiebelhaus(seed, g=2):
    """Dreigiebelhaus: ein breites Stadthaus mit drei nebeneinander liegenden, steilen Giebeln in verschiedenen
    Farben, einer gemeinsamen Ladenzone im Erdgeschoss und Arkaden."""
    w, s, zl = grund(seed, g, 11)
    b = B_(s, 5)
    stile = ["blau", "terrakotta", "fachwerk"]
    for k in range(3):
        haus(w, (k - 1) * b, 0, b, B_(s, 9), 1, stile[k], geschosse=3, tuer_s="south", first_x=False, steil=2,
             schorn=k == 1)
    return w


def schieferhaus(seed, g=1):
    """Schieferhaus: ein Haus ganz in grauen Schiefer gekleidet, mit schwarzem Steildach, grünen Fensterläden,
    einer Gaube und einem Vorbau mit Holzsäulen."""
    w, s, zl = grund(seed, g)
    B, T = B_(s, 9), B_(s, 7)
    haus(w, 0, 0, B, T, 1, "schiefer", geschosse=2, tuer_s="south", steil=2)
    for x in (-2, 2):
        for y in range(1, 4):
            w.setze(x, y, T // 2 + 2, stamm(w, "dark_oak"))
    for x in range(-2, 3):
        for z in range(T // 2 + 1, T // 2 + 3):
            w.setze(x, 4, z, platte(w, "deepslate_tile"))
    return w


def blumenladen(seed, g=1):
    """Blumenladen: ein kleines Ladenhaus, dessen Erdgeschoss ein Glashaus-Vorbau voller Blumen ist, Eimer mit
    Sträußen auf der Treppe, Rankrosen über der Tür und Blumenkästen an jedem Fenster."""
    w, s, zl = grund(seed, g)
    B, T = B_(s, 9), B_(s, 7)
    haus(w, 0, -2, B, T, 1, "terrakotta", geschosse=2, tuer_s="south")
    z0 = -2 + T // 2 + 1
    for x in range(-B // 2, B // 2 + 1):
        for z in range(z0, z0 + 3):
            for y in range(1, 4):
                rand = abs(x) == B // 2 or z == z0 + 2 or y == 3
                if rand:
                    w.setze(x, y, z, w.b("glass") if not (abs(x) == B // 2 and z == z0 + 2) else stamm(w, "birch"))
                elif y == 1:
                    w.setze(x, y, z, w.b(["red_tulip", "pink_tulip", "allium", "blue_orchid", "cornflower"]
                                         [(x + z) % 5]))
    for y in (1, 2):
        w.bloecke.pop((0, y, z0 + 2), None)
    return w


def lehmhaus(seed, g=1):
    """Lehmhaus: ein kubisches Haus aus Lehmziegeln mit Flachdach-Terrasse, Holzbalken, die aus der Wand ragen,
    kleinen tiefen Fenstern, Tonkrügen und einer Außentreppe zum Dach."""
    w, s, zl = grund(seed, g)
    B, T = B_(s, 9), B_(s, 7)
    x0, z0, x1, z1 = -B // 2, -T // 2, B // 2, T // 2
    mm = M(w, [("packed_mud", 3), ("mud_bricks", 1), ("smooth_sandstone", 1)])
    for e in range(1 + (g > 1)):
        y0 = 1 + e * 4
        mauer(w, x0 + e, z0 + e, x1 - e, z1 - e, y0, y0 + 3, mm)
        fensterreihe(w, x0 + e, z0 + e, x1 - e, z1 - e, y0 + 1, ("north", "south", "east", "west"), abstand=3,
                     holz="jungle", laeden=False, blumen=0.3)
        for x in range(x0 + e, x1 - e + 1):
            for z in range(z0 + e, z1 - e + 1):
                w.setze(x, y0 + 4, z, mm(x, 0, z))
        for x in range(x0 + e + 1, x1 - e, 2):
            w.setze(x, y0 + 3, z1 - e + 1, stamm(w, "jungle", "z", False), False)
    tuer(w, 0, 1, z1, "south", holz="jungle", laternen=False)
    for k in range(4):
        w.setze(x1 + 1, 1 + k, z1 - k, treppe(w, "mud_brick", "north"), False)
    for k in range(3):
        w.setze(x0 - 1, 1, z1 - k * 2, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False))
    return w


def weinstube(seed, g=1):
    """Weinstube: ein Winzerhaus mit Weinlaube über der Terrasse, Fässern als Tische, einem Gewölbekeller-Eingang
    mit Rundbogen und Rebstöcken an der Hauswand."""
    w, s, zl = grund(seed, g)
    B, T = B_(s, 9), B_(s, 7)
    haus(w, 0, -2, B, T, 1, "terrakotta", geschosse=2, tuer_s="south")
    z0 = -2 + T // 2 + 1
    for x in range(-B // 2, B // 2 + 1, 2):
        for y in range(1, 4):
            w.setze(x, y, z0 + 4, zaun(w, "spruce"))
    for x in range(-B // 2, B // 2 + 1):
        for z in range(z0, z0 + 5):
            w.setze(x, 4, z, w.b("azalea_leaves" if (x + z) % 3 else "flowering_azalea_leaves", persistent=True,
                                 distance=1, waterlogged=False))
    for k in range(3):
        w.setze(-B // 2 + 2 + k * 3, 1, z0 + 2, w.b("barrel", facing="up", open=False))
    for y in range(1, 3):
        w.bloecke.pop((B // 2 - 1, y, -2 - T // 2), None)
    return w


HAEUSER3 = {
    "brauhaus": ("Brauhaus", brauhaus),
    "bootshaus": ("Bootshaus", bootshaus),
    "uhrmacherhaus": ("Uhrmacherhaus", uhrmacherhaus),
    "maleratelier": ("Maleratelier", maleratelier),
    "musikantenhaus": ("Musikantenhaus", musikantenhaus),
    "kanalhaus": ("Kanalhaus", kanalhaus),
    "pfoertnerhaus": ("Pförtnerhaus", pfoertnerhaus),
    "glockengiesserei": ("Glockengießerei", glockengiesserei),
    "gewuerzhaendler": ("Gewürzhändler", gewuerzhaendler),
    "hutmacher": ("Hutmacherladen", hutmacher),
    "teestube": ("Teestube", teestube),
    "fischraeucherei": ("Fischräucherei", fischraeucherei),
    "brueckenhaus": ("Brückenhaus", brueckenhaus),
    "hanghaus": ("Hanghaus", hanghaus),
    "kreuzgiebelhaus": ("Kreuzgiebelhaus", kreuzgiebelhaus),
    "dreigiebelhaus": ("Dreigiebelhaus", dreigiebelhaus),
    "schieferhaus": ("Schieferhaus", schieferhaus),
    "blumenladen": ("Blumenladen", blumenladen),
    "lehmhaus": ("Lehmhaus", lehmhaus),
    "weinstube": ("Weinstube", weinstube),
}

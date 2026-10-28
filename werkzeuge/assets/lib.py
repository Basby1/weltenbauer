"""Gemeinsamer Baukasten für alle Weltenbauer-Assets.

Ein Asset wird in einer "Welt" gebaut: ein dünn besetztes Raster {(x, y, z): Block-Index}.
y = 0 ist die Bodenschicht (der Block, auf dem man steht). Alles mit y < 0 liegt im Boden.
Beim Export wird alles auf (0, 0, 0) verschoben und als Minecraft-Strukturdatei (.nbt) gespeichert.
"""

from __future__ import annotations

import gzip
import math
import struct
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

DATA_VERSION = 3465  # Minecraft 1.20.1


# --------------------------------------------------------------------------- Palette

class Palette:
    def __init__(self):
        self.eintraege: list[tuple[str, tuple]] = []
        self.index: dict = {}
        self.b("minecraft:air")

    def b(self, name: str, **props) -> int:
        if ":" not in name:
            name = "minecraft:" + name
        schluessel = (name, tuple(sorted((k, str(v).lower()) for k, v in props.items())))
        if schluessel not in self.index:
            self.index[schluessel] = len(self.eintraege)
            self.eintraege.append(schluessel)
        return self.index[schluessel]

    def name(self, idx: int) -> str:
        return self.eintraege[idx][0]


LUFT = 0


# --------------------------------------------------------------------------- Welt

class Welt:
    def __init__(self, seed: int = 1):
        self.P = Palette()
        self.bloecke: dict[tuple[int, int, int], int] = {}
        self.rng = np.random.default_rng(abs(int(seed)))
        self.anker = (0, 0, 0)          # dieser Punkt landet auf dem Bodenblock unter dem Spieler

    # Grundfunktionen
    def b(self, name, **props):
        return self.P.b(name, **props)

    def setze(self, x, y, z, blk, ueberschreiben=True):
        p = (int(x), int(y), int(z))
        if not ueberschreiben and self.bloecke.get(p, LUFT) != LUFT:
            return False
        self.bloecke[p] = blk
        return True

    def hole(self, x, y, z):
        return self.bloecke.get((int(x), int(y), int(z)))

    def frei(self, x, y, z):
        v = self.bloecke.get((int(x), int(y), int(z)))
        return v is None or v == LUFT

    def zufall(self):
        return self.rng.random()

    # Formen
    def kugel(self, cx, cy, cz, r, blk, ueberschreiben=False, rauschen=0.0, sy=1.0):
        ri = int(math.ceil(r)) + 1
        for dx in range(-ri, ri + 1):
            for dy in range(-ri, ri + 1):
                for dz in range(-ri, ri + 1):
                    d = math.sqrt(dx * dx + (dy / sy) ** 2 + dz * dz)
                    grenze = r + (self.rng.random() - 0.5) * 2 * rauschen
                    if d <= grenze:
                        self.setze(cx + dx, cy + dy, cz + dz, blk, ueberschreiben)

    def quader(self, x0, y0, z0, x1, y1, z1, blk, ueberschreiben=True):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.setze(x, y, z, blk, ueberschreiben)

    def grenzen(self):
        pos = np.array(list(self.bloecke.keys()))
        return pos.min(axis=0), pos.max(axis=0)


# --------------------------------------------------------------------------- Materialien

class Ziegel:
    """Steinziegel-Mix mit Moos, Rissen und Bruchstein – für Ruinen."""

    def __init__(self, welt: Welt, moos: float = 0.35, risse: float = 0.12, bruch: float = 0.08):
        b = welt.b
        self.w = welt
        self.moos = moos
        self.risse = risse
        self.bruch = bruch
        self.STEIN = b("stone_bricks")
        self.MOOS = b("mossy_stone_bricks")
        self.RISS = b("cracked_stone_bricks")
        self.BRUCH = b("cobblestone")
        self.MOOSBRUCH = b("mossy_cobblestone")
        self.ANDESIT = b("andesite")
        self.alle = {self.STEIN, self.MOOS, self.RISS, self.BRUCH, self.MOOSBRUCH, self.ANDESIT}

    def __call__(self, extra_moos: float = 0.0):
        u = self.w.zufall()
        if u < self.risse:
            return self.RISS
        u = self.w.zufall()
        if u < self.bruch:
            return self.MOOSBRUCH if self.w.zufall() < self.moos + extra_moos else self.BRUCH
        if self.w.zufall() < self.moos + extra_moos:
            return self.MOOS
        return self.STEIN if self.w.zufall() > 0.05 else self.ANDESIT

    def treppe(self, facing, moosig=False, half="bottom"):
        name = "mossy_stone_brick_stairs" if moosig else "stone_brick_stairs"
        return self.w.b(name, facing=facing, half=half, shape="straight", waterlogged=False)

    def stufe(self, moosig=False, typ="bottom"):
        name = "mossy_stone_brick_slab" if moosig else "stone_brick_slab"
        return self.w.b(name, type=typ, waterlogged=False)


def laub(welt: Welt, art: str):
    return welt.b(f"{art}_leaves", persistent=True, distance=7, waterlogged=False)


def stamm(welt: Welt, art: str, achse: str = "y"):
    return welt.b(f"{art}_log", axis=achse)


def holz(welt: Welt, art: str, achse: str = "y"):
    """Rundum mit Rinde (für dicke Stämme und Äste)."""
    return welt.b(f"{art}_wood", axis=achse)


# --------------------------------------------------------------------------- Bewuchs

RICHTUNGEN = [(1, 0, "east"), (-1, 0, "west"), (0, 1, "south"), (0, -1, "north")]


def ist_massiv(welt: Welt, blk) -> bool:
    if blk is None or blk == LUFT:
        return False
    n = welt.P.name(blk)
    weich = ("vine", "grass", "fern", "poppy", "dandelion", "bluet", "daisy", "cornflower", "carpet",
             "lily_pad", "petals", "water", "lantern", "torch", "button", "flower", "mushroom", "sapling")
    if n.endswith("leaves"):
        return False
    return not any(w in n for w in weich)


def ueberwuchern(welt: Welt, ziegel: Ziegel | None = None, ranken: float = 0.5, moos_oben: float = 0.5,
                 pflanzen: float = 0.35, buesche: float = 0.06, max_ranke: int = 7):
    """Moos auf Oberseiten, Ranken an Seitenwänden, Gras/Blumen/Büsche obendrauf."""
    w = welt
    MOOS = w.b("moss_block")
    GRAS = w.b("grass_block", snowy=False)
    MOOSTEPPICH = w.b("moss_carpet")
    KURZGRAS = w.b("grass")
    FARN = w.b("fern")
    BLUMEN = [w.b("poppy"), w.b("dandelion"), w.b("azure_bluet"), w.b("oxeye_daisy")]
    AZALEE = laub(w, "azalea")
    BLUETEN = laub(w, "flowering_azalea")

    positionen = list(w.bloecke.items())
    # 1) Oberseiten
    for (x, y, z), blk in positionen:
        if not ist_massiv(w, blk) or not w.frei(x, y + 1, z):
            continue
        if y < 0:
            continue
        u = w.zufall()
        if ziegel is not None and blk in ziegel.alle and u < moos_oben:
            w.setze(x, y, z, MOOS if w.zufall() < 0.55 else GRAS)
            v = w.zufall()
            if v < buesche:
                w.setze(x, y + 1, z, AZALEE if w.zufall() < 0.75 else BLUETEN)
            elif v < buesche + pflanzen * 0.5:
                w.setze(x, y + 1, z, MOOSTEPPICH if w.hole(x, y, z) == MOOS else KURZGRAS)
        elif blk in (GRAS, MOOS):
            v = w.zufall()
            if v < pflanzen * 0.6:
                w.setze(x, y + 1, z, KURZGRAS if blk == GRAS else MOOSTEPPICH)
            elif v < pflanzen * 0.75:
                w.setze(x, y + 1, z, FARN)
            elif v < pflanzen:
                w.setze(x, y + 1, z, BLUMEN[int(w.zufall() * len(BLUMEN))])

    # 2) Ranken an Seitenwänden, von oben herabhängend
    if ranken > 0:
        massiv = {p for p, blk in w.bloecke.items() if ist_massiv(w, blk)}
        for (x, y, z) in list(massiv):
            if (x, y + 1, z) in massiv:
                continue  # nur an Oberkanten anfangen
            for dx, dz, seite in RICHTUNGEN:
                ax, az = x + dx, z + dz
                if not w.frei(ax, y, az) or w.zufall() > ranken:
                    continue
                gegenseite = {"east": "west", "west": "east", "north": "south", "south": "north"}[seite]
                ranke = w.b("vine", **{s: (s == gegenseite) for s in ("north", "east", "south", "west")}, up=False)
                laenge = int(2 + w.zufall() * max_ranke)
                for yy in range(y, y - laenge, -1):
                    if yy < 1 or not w.frei(ax, yy, az) or (x, yy, z) not in massiv:
                        break
                    w.setze(ax, yy, az, ranke)


# --------------------------------------------------------------------------- Export

def _tstr(s: str) -> bytes:
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def exportieren(welt: Welt, pfad: Path) -> dict:
    """Speichert als Minecraft-Strukturdatei. Gibt Größe und Anker (verschoben) zurück."""
    lo, hi = welt.grenzen()
    groesse = (hi - lo + 1).tolist()
    pal = welt.P.eintraege
    teile = [b"\x0a", _tstr("")]
    teile += [b"\x03", _tstr("DataVersion"), struct.pack(">i", DATA_VERSION)]
    teile += [b"\x09", _tstr("size"), b"\x03", struct.pack(">i", 3), struct.pack(">iii", *groesse)]
    teile += [b"\x09", _tstr("palette"), b"\x0a", struct.pack(">i", len(pal))]
    for name, props in pal:
        teile += [b"\x08", _tstr("Name"), _tstr(name)]
        if props:
            teile += [b"\x0a", _tstr("Properties")]
            for k, v in props:
                teile += [b"\x08", _tstr(k), _tstr(v)]
            teile.append(b"\x00")
        teile.append(b"\x00")
    eintraege = sorted(welt.bloecke.items())
    teile += [b"\x09", _tstr("blocks"), b"\x0a", struct.pack(">i", len(eintraege))]
    kp = b"\x09" + _tstr("pos") + b"\x03" + struct.pack(">i", 3)
    ks = b"\x03" + _tstr("state")
    for (x, y, z), s in eintraege:
        teile.append(kp + struct.pack(">iii", x - lo[0], y - lo[1], z - lo[2]) + ks + struct.pack(">i", s) + b"\x00")
    teile += [b"\x09", _tstr("entities"), b"\x00", struct.pack(">i", 0)]
    teile.append(b"\x00")
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(pfad, "wb", compresslevel=9) as f:
        f.write(b"".join(teile))
    ax, ay, az = welt.anker
    return {"groesse": groesse, "anker": [int(ax - lo[0]), int(ay - lo[1]), int(az - lo[2])],
            "bloecke": len(eintraege)}


# --------------------------------------------------------------------------- Vorschau

FARBEN = {
    "stone_bricks": (122, 122, 122), "mossy_stone_bricks": (104, 121, 86), "cracked_stone_bricks": (112, 111, 112),
    "cobblestone": (128, 127, 128), "mossy_cobblestone": (101, 118, 89), "andesite": (136, 136, 137),
    "stone": (126, 126, 126), "deepslate_tiles": (54, 54, 55), "polished_deepslate": (72, 72, 73), "tuff": (108, 109, 103),
    "grass_block": (107, 150, 66), "dirt": (134, 96, 67), "coarse_dirt": (119, 85, 59), "rooted_dirt": (144, 104, 77),
    "podzol": (92, 63, 24), "moss_block": (89, 109, 45), "water": (52, 90, 190), "calcite": (223, 224, 221),
    "gravel": (131, 127, 126), "diorite": (189, 189, 189), "granite": (149, 103, 86), "mud": (60, 57, 60),
    "stone_brick_stairs": (122, 122, 122), "mossy_stone_brick_stairs": (104, 121, 86),
    "stone_brick_slab": (122, 122, 122), "mossy_stone_brick_slab": (104, 121, 86),
    "chiseled_stone_bricks": (119, 118, 119), "smooth_stone": (159, 159, 159), "lantern": (210, 160, 80),
    "oak_log": (109, 85, 50), "oak_wood": (109, 85, 50), "oak_leaves": (64, 112, 40),
    "birch_log": (216, 215, 210), "birch_wood": (216, 215, 210), "birch_leaves": (110, 145, 70),
    "spruce_log": (58, 37, 16), "spruce_wood": (58, 37, 16), "spruce_leaves": (48, 82, 48),
    "dark_oak_log": (60, 46, 26), "dark_oak_wood": (60, 46, 26), "dark_oak_leaves": (50, 95, 30),
    "jungle_log": (85, 67, 25), "jungle_wood": (85, 67, 25), "jungle_leaves": (48, 125, 30),
    "acacia_log": (103, 96, 86), "acacia_wood": (103, 96, 86), "acacia_leaves": (95, 130, 40),
    "cherry_log": (54, 33, 44), "cherry_wood": (54, 33, 44), "cherry_leaves": (229, 172, 194),
    "mangrove_log": (84, 66, 41), "mangrove_wood": (84, 66, 41), "mangrove_leaves": (70, 120, 40),
    "mangrove_roots": (74, 59, 38), "muddy_mangrove_roots": (70, 58, 45),
    "stripped_oak_log": (177, 144, 86), "stripped_spruce_log": (115, 89, 52), "stripped_dark_oak_log": (72, 56, 36),
    "azalea_leaves": (90, 125, 45), "flowering_azalea_leaves": (110, 120, 70),
    "vine": (55, 105, 30), "pink_petals": (240, 170, 200), "hanging_roots": (160, 110, 80),
    "brown_mushroom": (150, 110, 80), "fern": (90, 130, 60), "grass": (95, 140, 60), "poppy": (190, 40, 40), "dandelion": (230, 200, 40), "azure_bluet": (200, 210, 220), "oxeye_daisy": (220, 220, 210), "cornflower": (80, 110, 200), "allium": (180, 110, 220), "moss_carpet": (89, 109, 45), "lily_pad": (40, 120, 50), "large_fern": (90, 130, 60), "dead_bush": (140, 100, 50), "red_mushroom": (200, 40, 40), "glow_lichen": (110, 140, 120),
    "shroomlight": (240, 146, 70),
    "crimson_stem": (92, 25, 29), "crimson_hyphae": (92, 25, 29), "warped_stem": (58, 58, 77), "warped_hyphae": (58, 58, 77),
    "nether_wart_block": (115, 3, 2), "warped_wart_block": (22, 119, 121), "crimson_nylium": (130, 31, 31),
    "warped_nylium": (43, 114, 101), "netherrack": (97, 38, 38), "weeping_vines": (160, 20, 10),
    "weeping_vines_plant": (140, 20, 10), "twisting_vines": (20, 140, 120), "twisting_vines_plant": (20, 140, 120),
    "crimson_roots": (126, 8, 41), "warped_roots": (20, 138, 124), "crimson_fungus": (140, 30, 30),
    "warped_fungus": (30, 120, 110), "nether_sprouts": (20, 150, 130),
    "soul_soil": (75, 57, 46), "soul_lantern": (80, 200, 210), "chain": (60, 64, 75), "cobweb": (225, 225, 230), "chiseled_sandstone": (216, 203, 155), "sandstone_wall": (216, 203, 155), "bricks": (150, 97, 83), "mud_bricks": (137, 103, 79), "brick_wall": (150, 97, 83), "white_stained_glass": (240, 240, 240), "cherry_planks": (226, 178, 172), "cherry_slab": (226, 178, 172), "cherry_fence": (226, 178, 172), "stripped_cherry_log": (215, 145, 148), "mangrove_planks": (117, 54, 48), "mangrove_slab": (117, 54, 48), "mangrove_fence": (117, 54, 48), "stripped_mangrove_log": (119, 54, 47), "mangrove_log": (84, 66, 41), "spruce_log": (58, 37, 16), "dark_oak_log": (60, 46, 26), "dark_oak_slab": (66, 43, 20), "spruce_slab": (114, 84, 48), "stone_bricks": (122, 122, 122), "bee_nest": (200, 160, 70), "lily_of_the_valley": (230, 230, 230), "red_tulip": (200, 40, 40), "orange_tulip": (230, 120, 30), "pink_tulip": (230, 150, 180), "mangrove_roots": (74, 59, 38), "oak_wood": (109, 85, 50), "cyan_stained_glass": (76, 127, 153), "magenta_stained_glass": (178, 76, 216), "torchflower": (220, 120, 40), "cyan_terracotta": (86, 91, 91), "purple_terracotta": (118, 70, 86), "amethyst_block": (133, 97, 191), "amethyst_cluster": (160, 120, 220), "clay": (160, 166, 179), "barrel": (140, 106, 60), "farmland": (82, 54, 30), "wheat": (200, 180, 70), "carrots": (90, 150, 40), "dark_oak_fence": (66, 43, 20), "waxed_weathered_cut_copper": (109, 145, 107), "smooth_sandstone": (223, 214, 170), "brown_terracotta": (77, 51, 36), "pointed_dripstone": (134, 107, 92), "dripstone_block": (134, 107, 92), "polished_granite": (154, 106, 89), "polished_granite_stairs": (154, 106, 89), "polished_granite_slab": (154, 106, 89), "smooth_sandstone_stairs": (223, 214, 170), "smooth_sandstone_slab": (223, 214, 170), "deepslate_bricks": (70, 70, 71), "deepslate_tiles": (54, 54, 55), "cobbled_deepslate": (77, 77, 80), "deepslate_brick_wall": (70, 70, 71), "stone_brick_slab": (122, 122, 122), "stone_brick_stairs": (122, 122, 122), "packed_mud": (142, 107, 80), "dark_oak_log": (60, 46, 26), "spruce_log": (58, 37, 16), "lantern": (210, 160, 80), "dark_oak_slab": (66, 43, 20), "waxed_oxidized_cut_copper": (79, 153, 126), "cut_sandstone": (217, 206, 159),  "red_concrete": (142, 32, 32), "red_wool": (157, 47, 47), "orange_concrete": (224, 97, 0), "orange_wool": (239, 112, 15), "yellow_concrete": (240, 175, 21), "yellow_wool": (255, 190, 36), "lime_concrete": (94, 169, 24), "lime_wool": (109, 184, 39), "green_concrete": (73, 91, 36), "green_wool": (88, 106, 51), "cyan_concrete": (21, 119, 136), "cyan_wool": (36, 134, 151), "light_blue_concrete": (35, 137, 198), "light_blue_wool": (50, 152, 213), "blue_concrete": (44, 46, 143), "blue_wool": (59, 61, 158), "purple_concrete": (100, 31, 156), "purple_wool": (115, 46, 171), "magenta_concrete": (169, 48, 159), "magenta_wool": (184, 63, 174), "pink_concrete": (213, 101, 142), "pink_wool": (228, 116, 157), "white_concrete": (207, 213, 214), "white_wool": (222, 228, 229), "light_gray_concrete": (125, 125, 115), "light_gray_wool": (140, 140, 130), "gray_concrete": (54, 57, 61), "gray_wool": (69, 72, 76), "black_concrete": (8, 10, 15), "black_wool": (23, 25, 30), "light_blue_stained_glass": (120, 180, 230), "blue_ice": (116, 167, 253), "purple_stained_glass": (130, 60, 190), "black_stained_glass": (25, 25, 30), "quartz_slab": (235, 229, 222), "quartz_stairs": (235, 229, 222), "polished_diorite": (192, 193, 194), "polished_andesite": (132, 134, 133), "end_rod": (240, 235, 220),  "black_terracotta": (37, 23, 16), "oxidized_copper": (82, 162, 132), "waxed_oxidized_copper": (82, 162, 132), "weathered_copper": (108, 153, 110), "waxed_weathered_copper": (108, 153, 110), "prismarine": (99, 156, 151), "dark_prismarine": (51, 91, 75), "prismarine_bricks": (99, 171, 158), "green_terracotta": (76, 83, 42), "lime_terracotta": (103, 117, 53), "green_concrete": (73, 91, 36), "lime_concrete": (94, 169, 24), "black_concrete": (8, 10, 15), "white_concrete": (207, 213, 214), "end_stone": (219, 222, 158), "sand": (219, 207, 163), "smooth_quartz": (235, 229, 222), "white_terracotta": (209, 178, 161), "red_terracotta": (143, 61, 46), "glass": (200, 230, 240), "glass_pane": (190, 225, 235), "sea_lantern": (172, 199, 190), "glowstone": (250, 210, 120), "dark_oak_planks": (66, 43, 20), "dark_oak_stairs": (66, 43, 20), "dark_oak_slab": (66, 43, 20), "spruce_stairs": (114, 84, 48), "spruce_slab": (114, 84, 48), "spruce_fence": (114, 84, 48), "spruce_trapdoor": (103, 79, 47), "spruce_door": (106, 80, 48), "stripped_spruce_log": (115, 89, 52), "stripped_dark_oak_log": (72, 56, 36), "stripped_oak_log": (177, 144, 86), "stripped_birch_log": (196, 176, 118), "birch_planks": (192, 175, 121), "oak_planks": (162, 130, 78), "oak_stairs": (162, 130, 78), "oak_fence": (162, 130, 78), "oak_trapdoor": (124, 99, 56), "oak_door": (140, 110, 66), "dark_oak_fence": (66, 43, 20), "dark_oak_trapdoor": (75, 49, 23), "dark_oak_door": (76, 51, 25), "campfire": (90, 70, 40), "ladder": (125, 97, 55), "lightning_rod": (200, 120, 90), "white_wool": (234, 236, 237), "jungle_planks": (160, 115, 80), "cocoa": (150, 90, 40), "potted_poppy": (120, 70, 50), "potted_azure_bluet": (120, 70, 50), "potted_red_tulip": (120, 70, 50), "potted_cornflower": (120, 70, 50), "potted_allium": (120, 70, 50), "spruce_planks": (114, 84, 48), "deepslate": (80, 80, 82), "sandstone": (216, 203, 155), "smooth_sandstone": (223, 214, 170), "terracotta": (152, 94, 67), "orange_terracotta": (161, 83, 37), "red_sandstone": (186, 99, 29), "stone_brick_wall": (122, 122, 122), "chiseled_stone_bricks": (119, 118, 119),
    "cave_vines": (230, 160, 50), "cave_vines_plant": (110, 120, 40), "mycelium": (111, 99, 105),
    "azalea": (100, 125, 50), "flowering_azalea": (130, 110, 120), "cocoa": (150, 90, 40), "bee_nest": (200, 160, 70),
    "red_mushroom_block": (200, 46, 45), "brown_mushroom_block": (149, 111, 81), "mushroom_stem": (203, 196, 185),
}

DEKO = ("grass", "fern", "poppy", "dandelion", "azure_bluet", "oxeye_daisy", "cornflower", "vine",
        "moss_carpet", "lily_pad", "pink_petals", "brown_mushroom", "red_mushroom", "glow_lichen", "cocoa",
        "hanging_roots", "spore_blossom", "lantern", "torch", "cobweb", "soul_lantern", "chain", "cave_vines",
        "cave_vines_plant", "weeping_vines", "weeping_vines_plant", "twisting_vines", "twisting_vines_plant",
        "crimson_roots", "warped_roots", "crimson_fungus", "warped_fungus", "nether_sprouts", "dead_bush",
        "large_fern", "azalea", "flowering_azalea")


SICHTBARE_DEKO = ("amethyst_cluster", "hanging_roots", "lantern", "soul_lantern", "chain", "cobweb", "cave_vines",
                  "cave_vines_plant", "weeping_vines", "weeping_vines_plant", "twisting_vines", "twisting_vines_plant")


def als_raster(welt: Welt, deko_ausblenden=True):
    """Für den Renderer: dichtes int-Raster (0 = leer) und Liste von Objekten mit .rgb."""
    lo, hi = welt.grenzen()
    groesse = hi - lo + 1
    idx = np.zeros(groesse, dtype=np.int16)
    for (x, y, z), s in welt.bloecke.items():
        if s == LUFT:
            continue
        kurz = welt.P.name(s).split(":")[1]
        if kurz.endswith("_trapdoor") or kurz.startswith("potted_") or kurz in ("ladder", "campfire"):
            continue
        if kurz in DEKO and (deko_ausblenden or kurz not in SICHTBARE_DEKO):
            continue
        idx[x - lo[0], y - lo[1], z - lo[2]] = s

    @dataclass
    class B:
        rgb: tuple

    liste = []
    for name, _ in welt.P.eintraege[1:]:
        kurz = name.split(":")[1]
        liste.append(B(farbe_von(kurz) or (220, 0, 220)))
    return idx, liste


# --------------------------------------------------------------------------- Werkzeuge für Ruinen und Natur

class Rauschen:
    """Glattes 3D-Wertrauschen (0..1) mit fester Zellgröße."""

    def __init__(self, welt: Welt, zelle: float = 6.0, n: int = 64):
        self.g = welt.rng.random((n, n, n))
        self.z = zelle
        self.n = n

    def __call__(self, x, y=0.0, z=0.0):
        x, y, z = x / self.z, y / self.z, z / self.z
        x0, y0, z0 = math.floor(x), math.floor(y), math.floor(z)
        fx, fy, fz = x - x0, y - y0, z - z0
        fx, fy, fz = (fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy), fz * fz * (3 - 2 * fz))
        n, g = self.n, self.g

        def v(i, j, k):
            return g[(x0 + i) % n, (y0 + j) % n, (z0 + k) % n]

        a = v(0, 0, 0) * (1 - fx) + v(1, 0, 0) * fx
        b = v(0, 1, 0) * (1 - fx) + v(1, 1, 0) * fx
        c = v(0, 0, 1) * (1 - fx) + v(1, 0, 1) * fx
        d = v(0, 1, 1) * (1 - fx) + v(1, 1, 1) * fx
        return (a * (1 - fy) + b * fy) * (1 - fz) + (c * (1 - fy) + d * fy) * fz


def einfuegen(ziel: Welt, quelle: Welt, dx=0, dy=0, dz=0, ueberschreiben=False):
    """Kopiert eine andere Welt (z. B. einen Baum) hinein und übersetzt dabei die Palette."""
    karte = {}
    for i, (name, props) in enumerate(quelle.P.eintraege):
        karte[i] = ziel.b(name, **dict(props))
    for (x, y, z), s in quelle.bloecke.items():
        if s == LUFT:
            continue
        ziel.setze(x + dx, y + dy, z + dz, karte[s], ueberschreiben)


def zerfall(welt: Welt, betroffen, rauschen: Rauschen, hoehe_max: float, staerke: float = 0.5, boden: int = 1):
    """Lässt Mauerwerk von oben her abbröckeln: je höher und je 'rauschiger', desto eher fehlt ein Block."""
    weg = []
    for (x, y, z), s in welt.bloecke.items():
        if s not in betroffen or y < boden:
            continue
        h = y / max(hoehe_max, 1)
        if rauschen(x, y * 0.7, z) * 0.9 + h * staerke + welt.rng.random() * 0.12 > 0.95:
            weg.append((x, y, z))
    for p in weg:
        del welt.bloecke[p]
    # schwebende Einzelblöcke entfernen
    for _ in range(2):
        einsam = []
        for (x, y, z), s in welt.bloecke.items():
            if s not in betroffen or y <= boden:
                continue
            n = sum((x + a, y + b, z + c) in welt.bloecke for a, b, c in
                    ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)))
            if (x, y - 1, z) not in welt.bloecke and n <= 1:
                einsam.append((x, y, z))
        for p in einsam:
            del welt.bloecke[p]
    return len(weg)


def geroell(welt: Welt, ziegel: Ziegel, cx, cz, r, hoehe=2.0, dichte=0.7):
    """Schutthaufen aus Steinziegeln, Bruchstein und Stufen."""
    for x in range(int(cx - r - 1), int(cx + r + 2)):
        for z in range(int(cz - r - 1), int(cz + r + 2)):
            d = math.hypot(x - cx, z - cz) / max(r, 0.5)
            if d > 1:
                continue
            h = int(round((1 - d * d) * hoehe + welt.rng.random() * 0.8))
            for y in range(1, h + 1):
                if welt.frei(x, y, z) and welt.rng.random() < dichte:
                    welt.setze(x, y, z, ziegel(0.1))
            if welt.frei(x, h + 1, z) and welt.rng.random() < 0.25 and h >= 0:
                welt.setze(x, h + 1, z, ziegel.stufe(welt.rng.random() < 0.5))


# --------------------------------------------------------------------------- Einlesen (zur Kontrolle und für fertige Dateien)

def _nbt_lesen(daten: bytes):
    pos = 0

    def u(fmt, n):
        nonlocal pos
        v = struct.unpack_from(fmt, daten, pos)
        pos += n
        return v[0]

    def text():
        n = u(">H", 2)
        nonlocal pos
        s = daten[pos:pos + n].decode("utf-8")
        pos += n
        return s

    def wert(typ):
        nonlocal pos
        if typ == 1:
            return u(">b", 1)
        if typ == 2:
            return u(">h", 2)
        if typ == 3:
            return u(">i", 4)
        if typ == 4:
            return u(">q", 8)
        if typ == 5:
            return u(">f", 4)
        if typ == 6:
            return u(">d", 8)
        if typ == 7:
            n = u(">i", 4)
            pos += n
            return None
        if typ == 8:
            return text()
        if typ == 9:
            t = u(">b", 1)
            n = u(">i", 4)
            return [wert(t) for _ in range(n)]
        if typ == 10:
            d = {}
            while True:
                t = u(">b", 1)
                if t == 0:
                    return d
                k = text()
                d[k] = wert(t)
        if typ == 11:
            n = u(">i", 4)
            return [u(">i", 4) for _ in range(n)]
        if typ == 12:
            n = u(">i", 4)
            return [u(">q", 8) for _ in range(n)]
        raise ValueError(f"NBT-Typ {typ}")

    t = u(">b", 1)
    text()
    return wert(t)


def laden(pfad: Path, seed: int = 1) -> Welt:
    """Liest eine Minecraft-Strukturdatei (.nbt) in eine Welt ein (Luft wird übersprungen)."""
    with gzip.open(pfad, "rb") as f:
        d = _nbt_lesen(f.read())
    w = Welt(seed)
    pal = d.get("palette") or d["palettes"][0]
    karte = []
    for e in pal:
        karte.append(w.b(e["Name"], **e.get("Properties", {})))
    for b in d["blocks"]:
        s = karte[b["state"]]
        if s == LUFT or w.P.name(s) in ("minecraft:air", "minecraft:structure_void"):
            continue
        x, y, z = b["pos"]
        w.bloecke[(x, y, z)] = s
    w.groesse = d["size"]
    return w


# --------------------------------------------------------------------------- Farbverläufe

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 + 1 / 32


class Verlauf:
    """Eine abgestimmte Blockpalette von dunkel nach hell. Zwischenwerte werden geordnet gerastert
    (wie es Builder von Hand machen), statt zufällig gemischt."""

    def __init__(self, welt: Welt, name: str, bloecke: list[str]):
        self.name = name
        self.namen = bloecke
        self.ids = [welt.b(n) for n in bloecke]

    def __call__(self, wert: float, x: int, y: int, z: int):
        wert = min(max(wert, 0.0), len(self.ids) - 1.0)
        unten = int(math.floor(wert))
        rest = wert - unten
        if unten + 1 < len(self.ids) and rest > BAYER[(x + y) & 3][(z + 2 * y) & 3]:
            unten += 1
        return self.ids[unten]

FARBEN.update({
    "gold_block": (246, 208, 61), "polished_blackstone": (53, 48, 56), "gilded_blackstone": (78, 62, 48),
    "crying_obsidian": (45, 18, 90), "purpur_block": (169, 125, 169), "end_stone_bricks": (218, 224, 162),
    "obsidian": (20, 18, 30), "magenta_terracotta": (149, 88, 108), "bone_block": (229, 225, 207),
    "waxed_cut_copper": (191, 106, 80), "waxed_copper_block": (192, 107, 79),
    "waxed_exposed_cut_copper": (154, 121, 101), "iron_block": (220, 220, 220),
})


FARBEN.update({
    "chiseled_deepslate": (54, 54, 55), "quartz_block": (235, 229, 222), "quartz_bricks": (234, 229, 221),
    "quartz_pillar": (235, 230, 224), "chiseled_quartz_block": (231, 226, 218), "polished_blackstone_bricks": (48, 43, 50),
    "chiseled_polished_blackstone": (53, 48, 56), "blackstone": (42, 36, 41), "nether_wart_block": (114, 3, 2),
    "yellow_terracotta": (186, 133, 35), "blue_terracotta": (74, 59, 91), "light_blue_terracotta": (113, 108, 137),
    "raw_gold_block": (221, 169, 46), "purpur_pillar": (171, 129, 171), "shroomlight": (240, 146, 70),
    "ochre_froglight": (250, 230, 170), "pearlescent_froglight": (240, 215, 225), "verdant_froglight": (210, 235, 200),
    "lily_pad": (32, 128, 48), "iron_bars": (110, 110, 110), "exposed_copper": (161, 125, 103),
    "waxed_exposed_copper": (161, 125, 103), "waxed_oxidized_cut_copper": (79, 153, 126),
    "yellow_stained_glass": (230, 210, 60), "orange_stained_glass": (216, 127, 51), "pink_stained_glass": (240, 150, 190),
    "blue_stained_glass": (60, 70, 190), "lime_stained_glass": (130, 200, 30), "green_stained_glass": (90, 120, 40),
    "light_gray_stained_glass": (160, 160, 160), "gray_stained_glass": (75, 75, 75), "red_stained_glass": (160, 50, 50),
    "lapis_block": (31, 67, 140), "diorite": (188, 188, 188), "smooth_stone": (158, 158, 158), "red_nether_bricks": (69, 7, 9),
    "stripped_birch_log": (196, 176, 118), "birch_log": (216, 215, 210), "soul_campfire": (80, 200, 210),
    "dark_oak_wood": (60, 46, 26), "spruce_wood": (58, 37, 16), "anvil": (68, 68, 68), "cauldron": (60, 60, 60),
    "coal_block": (16, 15, 15), "netherite_block": (66, 61, 63), "honeycomb_block": (229, 148, 29),
    "smooth_red_sandstone": (181, 97, 31), "cut_red_sandstone": (189, 101, 31), "red_sandstone": (186, 99, 29),
    "mossy_stone_bricks": (104, 121, 86), "cracked_stone_bricks": (112, 111, 112), "brown_wool": (114, 71, 40),
    "light_gray_terracotta": (135, 107, 98), "gray_terracotta": (57, 42, 35), "gilded_blackstone": (78, 62, 48),
})


def farbe_von(kurz: str):
    """Farbe eines Blocks fürs Vorschaubild; Treppen, Stufen, Mauern usw. erben die Farbe des Grundblocks."""
    if kurz in FARBEN:
        return FARBEN[kurz]
    k = kurz.replace("waxed_", "")
    if k in FARBEN:
        return FARBEN[k]
    for suf in ("_stairs", "_slab", "_wall", "_fence_gate", "_fence", "_button", "_pressure_plate", "_pane"):
        if k.endswith(suf):
            basis = k[: -len(suf)]
            for c in (basis, basis + "s", basis + "_block", basis + "_planks", basis + "_bricks",
                      basis.replace("brick", "bricks"), basis.replace("tile", "tiles")):
                if c in FARBEN:
                    return FARBEN[c]
                if "waxed_" + c in FARBEN:
                    return FARBEN["waxed_" + c]
    for pre in ("chiseled_", "cracked_", "cut_", "polished_", "smooth_", "stripped_"):
        if k.startswith(pre) and k[len(pre):] in FARBEN:
            return FARBEN[k[len(pre):]]
    return None

FARBEN.update({
    "basalt": (73, 72, 77), "smooth_basalt": (72, 72, 78), "polished_basalt": (99, 98, 100), "magma_block": (142, 63, 31),
    "dirt_path": (148, 122, 65), "tall_grass": (110, 160, 70), "snow_block": (249, 254, 254), "hay_block": (166, 136, 38),
    "soul_sand": (81, 62, 50), "soul_soil": (75, 57, 46), "packed_ice": (141, 180, 250), "granite": (149, 103, 85),
    "carved_pumpkin": (198, 118, 24), "pumpkin": (198, 118, 24), "potatoes": (100, 160, 50), "mud": (60, 57, 60),
})

FARBEN.update({
    "chest": (164, 116, 46), "iron_trapdoor": (200, 200, 200), "pink_terracotta": (161, 78, 78),
    "warped_wart_block": (22, 119, 121), "gravel": (131, 127, 126), "honeycomb_block": (229, 148, 29),
})

FARBEN.update({"snow": (249, 254, 254), "redstone_block": (175, 24, 5), "stripped_bamboo_block": (190, 170, 80)})

FARBEN.update({"small_amethyst_bud": (160, 120, 220), "birch_door": (200, 185, 130), "pink_petals": (240, 160, 200),
               "warped_nylium": (43, 114, 101), "mushroom_stem": (203, 196, 185), "red_mushroom_block": (200, 46, 45)})

FARBEN.update({
    "warped_planks": (43, 104, 99), "warped_fence": (43, 104, 99), "stripped_warped_stem": (57, 150, 147),
    "crimson_planks": (101, 48, 70), "crimson_fence": (101, 48, 70), "stripped_crimson_stem": (137, 57, 90),
    "jungle_log": (85, 67, 25), "acacia_planks": (168, 90, 50), "mangrove_log": (84, 66, 41),
})

FARBEN.update({"honey_block": (251, 185, 52), "flower_pot": (124, 68, 52), "bee_nest": (202, 160, 74),
               "beehive": (180, 146, 90), "blue_orchid": (40, 160, 220), "podzol": (92, 63, 24)})

FARBEN.update({"beetroots": (160, 40, 50), "bamboo_planks": (193, 173, 80), "bamboo_block": (127, 143, 52),
               "stripped_bamboo_block": (193, 173, 80), "quartz_pillar": (235, 230, 224)})

FARBEN.update({"white_candle": (230, 230, 220), "purple_candle": (120, 50, 170), "candle": (220, 200, 150),
               "red_candle": (160, 40, 40), "black_candle": (40, 40, 50), "orange_candle": (220, 120, 40)})

FARBEN.update({"bell": (250, 200, 60), "chiseled_sandstone": (216, 203, 155)})

FARBEN.update({"sugar_cane": (140, 190, 90), "red_sand": (190, 102, 33), "decorated_pot": (150, 80, 60),
               "brown_stained_glass": (102, 76, 51), "ice": (145, 183, 253), "white_carpet": (234, 236, 237),
               "orange_carpet": (240, 118, 19), "purple_carpet": (121, 42, 172), "cyan_carpet": (21, 137, 145),
               "blue_carpet": (53, 57, 157), "yellow_carpet": (248, 197, 39), "red_carpet": (160, 39, 34),
               "chiseled_red_sandstone": (183, 96, 27), "coal_block": (16, 15, 15), "snow": (249, 254, 254)})

FARBEN.update({
    "seagrass": (40, 120, 60), "kelp": (60, 130, 50), "kelp_plant": (60, 130, 50), "sea_pickle": (110, 130, 50),
    "tube_coral_block": (49, 87, 207), "tube_coral": (49, 87, 207), "tube_coral_fan": (49, 87, 207),
    "brain_coral_block": (207, 91, 159), "brain_coral": (207, 91, 159), "brain_coral_fan": (207, 91, 159),
    "bubble_coral_block": (165, 26, 162), "bubble_coral": (165, 26, 162), "bubble_coral_fan": (165, 26, 162),
    "fire_coral_block": (163, 35, 46), "fire_coral": (163, 35, 46), "fire_coral_fan": (163, 35, 46),
    "horn_coral_block": (216, 199, 66), "horn_coral": (216, 199, 66), "horn_coral_fan": (216, 199, 66),
    "lava": (230, 100, 20), "nether_bricks": (44, 21, 26), "chiseled_nether_bricks": (47, 23, 28),
    "nether_brick_fence": (44, 21, 26), "nether_wart": (150, 20, 20), "chorus_flower": (150, 110, 150),
    "chorus_plant": (93, 57, 93), "end_portal_frame": (90, 120, 100), "netherrack": (97, 38, 38),
    "crimson_nylium": (130, 31, 31), "warped_wart_block": (22, 119, 121), "warped_stem": (58, 58, 77),
    "crimson_stem": (92, 25, 29), "twisting_vines_plant": (20, 140, 120), "weeping_vines_plant": (140, 20, 20),
    "cracked_polished_blackstone_bricks": (44, 37, 43), "purpur_slab": (169, 125, 169), "end_rod": (240, 235, 220),
    "pink_concrete": (213, 101, 142), "pink_terracotta": (161, 78, 78), "soul_campfire": (80, 200, 210),
})

"""Blöcke aus den Mods des Modpacks – sicher verwendet.

Grundlage ist die Blockliste aus `/wb blockliste` (modbloecke.txt.gz). Jeder Mod-Block wird nur gesetzt,
wenn er dort mit genau diesen Zuständen existiert; sonst (und im Spiel, falls die Mod fehlt) erscheint
automatisch der angegebene Vanilla-Ersatzblock.
"""

from __future__ import annotations

import gzip
from functools import lru_cache
from pathlib import Path

HIER = Path(__file__).resolve().parent


@lru_cache(maxsize=1)
def liste():
    d = {}
    p = HIER / "modbloecke.txt.gz"
    if not p.exists():
        return d
    with gzip.open(p, "rt", encoding="utf-8") as f:
        for z in f:
            teile = z.split()
            if not teile:
                continue
            props = {}
            for t in teile[1:]:
                k, _, v = t.partition("=")
                props[k] = set(v.split(","))
            d[teile[0]] = props
    return d


def gibt(name):
    return name in liste()


def mod(w, name, ersatz, ersatz_props=None, **props):
    """Mod-Block mit Ersatz. Unbekannte Namen → nur der Ersatz; unpassende Zustände werden weggelassen."""
    L = liste()
    if name not in L:
        return w.b(ersatz, **(ersatz_props or {}))
    erlaubt = L[name]
    p = {k: v for k, v in props.items() if k in erlaubt and str(v).lower() in erlaubt[k]}
    if "waterlogged" in erlaubt and "waterlogged" not in p:
        p["waterlogged"] = False
    return w.mod(name, ersatz, ersatz_props, **p)


# ============================================================================ Dächer (Macaw's Roofs, Twigs-Schindeln)

# Macaw-Material -> (Vanilla-Treppe als Ersatz, Vollblock als Ersatz)
DACH_ERSATZ = {
    "red_terracotta": ("brick", "red_terracotta"), "orange_terracotta": ("smooth_red_sandstone", "orange_terracotta"),
    "brown_terracotta": ("mud_brick", "brown_terracotta"), "gray_terracotta": ("deepslate_tile", "gray_terracotta"),
    "black_terracotta": ("polished_blackstone", "black_terracotta"), "white_terracotta": ("smooth_quartz", "white_terracotta"),
    "green_terracotta": ("mossy_cobblestone", "green_terracotta"), "lime_terracotta": ("mossy_stone_brick", "lime_terracotta"),
    "blue_terracotta": ("dark_prismarine", "blue_terracotta"), "light_blue_terracotta": ("prismarine", "light_blue_terracotta"),
    "cyan_terracotta": ("prismarine_brick", "cyan_terracotta"), "purple_terracotta": ("purpur", "purple_terracotta"),
    "yellow_terracotta": ("smooth_sandstone", "yellow_terracotta"), "light_gray_terracotta": ("andesite", "light_gray_terracotta"),
    "magenta_terracotta": ("purpur", "magenta_terracotta"), "pink_terracotta": ("cherry", "pink_terracotta"),
    "thatch": ("spruce", "hay_block"), "deepslate": ("deepslate_tile", "deepslate_tiles"),
    "stone_bricks": ("stone_brick", "stone_bricks"), "stone": ("stone", "stone"), "cobblestone": ("cobblestone", "cobblestone"),
    "blackstone": ("polished_blackstone", "polished_blackstone"), "bricks": ("brick", "bricks"),
    "nether_bricks": ("nether_brick", "nether_bricks"), "red_nether_bricks": ("red_nether_brick", "red_nether_bricks"),
    "sandstone": ("sandstone", "sandstone"), "red_sandstone": ("red_sandstone", "red_sandstone"),
    "mud_brick": ("mud_brick", "mud_bricks"), "dark_prismarine": ("dark_prismarine", "dark_prismarine"),
    "prismarine_brick": ("prismarine_brick", "prismarine_bricks"), "andesite": ("andesite", "andesite"),
    "granite": ("granite", "granite"), "diorite": ("diorite", "diorite"),
}
for _f in ("white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray", "cyan", "purple",
           "blue", "brown", "green", "red", "black"):
    DACH_ERSATZ.setdefault(f"{_f}_concrete", ("stone_brick", f"{_f}_concrete"))
for _h in ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "crimson", "warped"):
    DACH_ERSATZ.setdefault(_h, (_h, f"{_h}_planks"))
    DACH_ERSATZ.setdefault(f"{_h}_planks", (_h, f"{_h}_planks"))


def dach_treppe(w, mat, facing, half="bottom", form="roof"):
    """mat: 'mcw:<material>' (Macaw's Roofs) oder 'silt:<farbe>' (Twigs-Schindeln)."""
    if mat.startswith("mcw:"):
        m = mat[4:]
        ers = DACH_ERSATZ.get(m, ("stone_brick", "stone_bricks"))[0]
        return mod(w, f"mcwroofs:{m}_{form}", f"{ers}_stairs",
                   dict(facing=facing, half=half, shape="straight", waterlogged=False),
                   facing=facing, half=half, shape="straight")
    if mat.startswith("silt:"):
        c = mat[5:]
        return mod(w, f"twigs:{c}_silt_shingle_stairs", "brick_stairs" if c in ("red", "orange", "brown") else
                   "deepslate_tile_stairs", dict(facing=facing, half=half, shape="straight", waterlogged=False),
                   facing=facing, half=half, shape="straight")
    return None


def dach_voll(w, mat):
    if mat.startswith("mcw:"):
        return w.b(DACH_ERSATZ.get(mat[4:], ("stone_brick", "stone_bricks"))[1])
    if mat.startswith("silt:"):
        c = mat[5:]
        return mod(w, f"twigs:{c}_silt_shingles", f"{c}_terracotta")
    return None


def dach_platte(w, mat, typ="bottom"):
    if mat.startswith("mcw:"):
        ers = DACH_ERSATZ.get(mat[4:], ("stone_brick", "stone_bricks"))[0]
        return w.b(f"{ers}_slab", type=typ, waterlogged=False)
    if mat.startswith("silt:"):
        c = mat[5:]
        return mod(w, f"twigs:{c}_silt_shingle_slab", "brick_slab", dict(type=typ, waterlogged=False), type=typ)
    return None


def markise(w, farbe, facing, half="bottom"):
    return mod(w, f"mcwroofs:{farbe}_striped_awning", f"{farbe}_carpet", None, facing=facing, half=half,
               shape="straight")


# ============================================================================ Wandvarianten (Chipped)

MATERIALWORTE = ("end", "smooth", "mossy", "red", "polished", "deepslate", "nether", "quartz", "cobbled", "mud",
                 "prismarine", "blackstone", "stone", "sandstone", "basalt", "tuff", "calcite", "dripstone", "purpur",
                 "andesite", "diorite", "granite", "gilded", "lodestone", "obsidian", "terracotta", "brick", "bricks",
                 "cobblestone", "dark", "netherrack", "amethyst", "bone", "copper", "gold", "iron", "emerald",
                 "diamond", "lapis", "redstone", "coal", "magma", "packed", "ice", "snow", "clay", "sculk", "soul")


STILWORTE = {"bordered", "inlayed", "tiny", "tiled", "disordered", "vertical", "cut", "cracked", "brick", "carved",
             "edged", "etched", "massive", "small", "stacked", "layered", "rough", "double", "offset", "pillar",
             "rounded", "engraved", "ringed", "thick", "layed", "eroded", "weathered", "chiseled", "fancy",
             "panelled", "angled", "centered", "large", "mini", "spiraled", "trodden", "runic", "inscribed"}


@lru_cache(maxsize=None)
def chipped_varianten(basis):
    """Einfache Chipped-Varianten genau dieses Grundblocks (z. B. 'stone_bricks', nicht end_stone_bricks)."""
    L = liste()
    out = []
    for n, p in L.items():
        if not n.startswith("chipped:") or p or not n.endswith("_" + basis):
            continue
        prefix = n[len("chipped:"):-len(basis) - 1]
        if not prefix or not set(prefix.split("_")) <= STILWORTE:
            continue
        out.append(n)
    return tuple(sorted(out))


# ============================================================================ Kleinkram


def laterne(w, art="chain_lantern", haengend=False):
    return mod(w, f"mcwlights:{art}", "lantern", dict(hanging=haengend, waterlogged=False), hanging=haengend)


def papierlampe(w, farbe="red"):
    return mod(w, f"mcwlights:{farbe}_paper_lamp", "shroomlight" if farbe in ("red", "orange", "yellow") else "sea_lantern",
               lit=True)


def strassenlampe(w, x, y, z, seele=False):
    name = "mcwlights:soul_classic_street_lamp" if seele else "mcwlights:classic_street_lamp"
    if not gibt(name):
        for k in range(3):
            w.setze(x, y + k, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
        w.setze(x, y + 3, z, w.b("soul_lantern" if seele else "lantern", hanging=False, waterlogged=False))
        return
    for k, teil in enumerate(("bottom", "middle", "top")):
        w.setze(x, y + k, z, mod(w, name, "spruce_fence", dict(north=False, south=False, east=False, west=False,
                                                                  waterlogged=False), lit=True, part=teil))


def hecke(w, art="azalea", **verb):
    return mod(w, f"mcwfences:{art}_hedge", f"{art}_leaves" if art in ("azalea", "flowering_azalea") else "oak_leaves",
               dict(persistent=True, distance=7, waterlogged=False), up=True,
               **{k: ("tall" if v else "none") for k, v in verb.items()})


def lattenzaun(w, holz="oak", **verb):
    return mod(w, f"mcwfences:{holz}_picket_fence", f"{holz}_fence",
               dict(waterlogged=False, **{k: bool(v) for k, v in verb.items()}), **verb)


def kiesel(w):
    return mod(w, "twigs:pebble", "stone_button", dict(face="floor", facing="north", powered=False))


def zweig(w):
    return mod(w, "twigs:twig", "dead_bush")


def muschel(w):
    return mod(w, "twigs:seashell", "nautilus_shell" if False else "dead_brain_coral", dict(waterlogged=False))


def blumenkasten(w, facing):
    return mod(w, "supplementaries:flower_box", "flowering_azalea_leaves", dict(persistent=True, distance=7,
                                                                                 waterlogged=False),
               facing=facing, floor=False)


def lehmputz(w, art="daub"):
    """Fachwerk-Füllung aus Supplementaries: daub, daub_frame, daub_brace, daub_cross_brace."""
    return mod(w, f"supplementaries:{art}", "white_terracotta")


def balken(w, holz="oak", achse="x"):
    return mod(w, f"decorative_blocks:{holz}_beam", f"stripped_{holz}_log", dict(axis=achse), axis=achse)


def kohlenbecken(w, seele=False):
    return mod(w, "decorative_blocks:soul_brazier" if seele else "decorative_blocks:brazier",
               "soul_campfire" if seele else "campfire",
               dict(lit=True, signal_fire=False, facing="north", waterlogged=False), lit=True)


def kronleuchter(w, seele=False):
    return mod(w, "decorative_blocks:soul_chandelier" if seele else "decorative_blocks:chandelier", "lantern",
               dict(hanging=True, waterlogged=False))


def fensterladen(w, holz, facing, offen=True, hinge="left"):
    return mod(w, f"mcwwindows:{holz}_shutter", f"{holz}_trapdoor",
               dict(facing=facing, half="bottom", open=True, powered=False, waterlogged=False),
               facing=facing, open=offen, hinge=hinge, powered=False)


def zahnrad(w, achse="z", gross=False):
    return mod(w, "create:large_cogwheel" if gross else "create:cogwheel", f"stripped_spruce_log",
               dict(axis=achse), axis=achse)


def welle(w, achse="x"):
    return mod(w, "create:shaft", "iron_bars", dict(north=False, south=False, east=False, west=False,
                                                    waterlogged=False), axis=achse)


def herbstlaub(w, art):
    """BOP-Herbstlaub: maple (rot), orange_autumn, yellow_autumn."""
    ers = {"maple": "nether_wart_block", "orange_autumn": "honeycomb_block", "yellow_autumn": "hay_block"}[art]
    return mod(w, f"biomesoplenty:{art}_leaves", ers, None, persistent=True, distance=7)

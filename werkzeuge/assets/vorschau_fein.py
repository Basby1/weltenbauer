"""Feinere Vorschau: jeder Block wird in 2×2×2 Teilwürfel zerlegt, damit Stufen, Treppen, Zäune, Scheiben,
Falltüren, Laternen, Blumen, Teppiche und Ranken ihre echte Form bekommen; dazu leichte Farbrauschen-„Textur“."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from lib import FARBEN, farbe_von

N = 2
_VOLL = np.ones((2, 2, 2), bool)


def _m(*zellen):
    m = np.zeros((2, 2, 2), bool)
    for (x, y, z) in zellen:
        m[x, y, z] = True
    return m


UNTEN = _m((0, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 1))
OBEN = _m((0, 1, 0), (1, 1, 0), (0, 1, 1), (1, 1, 1))
SEITE = {  # halbe Platte an einer Seite (x, z-Teilzellen)
    "north": _m(*[(x, y, 0) for x in (0, 1) for y in (0, 1)]),
    "south": _m(*[(x, y, 1) for x in (0, 1) for y in (0, 1)]),
    "west": _m(*[(0, y, z) for z in (0, 1) for y in (0, 1)]),
    "east": _m(*[(1, y, z) for z in (0, 1) for y in (0, 1)]),
}
GEGEN = {"north": "south", "south": "north", "east": "west", "west": "east"}
SAEULE = _m((1, 0, 1), (1, 1, 1))
PUNKT = _m((1, 0, 1))
PUNKT_OBEN = _m((1, 1, 1))

PFLANZEN = ("grass", "fern", "poppy", "dandelion", "azure_bluet", "oxeye_daisy", "cornflower", "allium",
            "red_tulip", "orange_tulip", "pink_tulip", "white_tulip", "lily_of_the_valley", "blue_orchid",
            "brown_mushroom", "red_mushroom", "dead_bush", "sweet_berry_bush", "crimson_roots", "warped_roots",
            "crimson_fungus", "warped_fungus", "nether_sprouts", "sapling", "torchflower", "wither_rose",
            "sugar_cane", "bamboo", "kelp", "seagrass", "wheat", "carrots", "potatoes", "beetroots", "candle",
            "potted_", "flower_pot", "torch", "end_rod", "lightning_rod", "amethyst_cluster", "_bud",
            "pointed_dripstone", "small_dripleaf", "frogspawn", "sea_pickle", "turtle_egg")
DUENN_UNTEN = ("carpet", "snow", "pressure_plate", "lily_pad", "pink_petals", "rail", "moss_carpet", "repeater",
               "comparator", "redstone_wire", "daylight_detector", "sculk_vein")


def form(name, props):
    k = name.split(":")[1] if ":" in name else name
    p = dict(props)
    if k.endswith("_slab"):
        t = p.get("type", "bottom")
        return _VOLL if t == "double" else (OBEN if t == "top" else UNTEN)
    if k.endswith("_stairs"):
        f = p.get("facing", "north")
        unten = p.get("half", "bottom") == "bottom"
        basis = UNTEN if unten else OBEN
        stufe = SEITE[f] & (OBEN if unten else UNTEN)
        return basis | stufe
    if k.endswith("_trapdoor"):
        if p.get("open") == "true":
            return SEITE[GEGEN.get(p.get("facing", "north"), "north")]
        return OBEN if p.get("half") == "top" else UNTEN
    if k.endswith("_door"):
        return SEITE[GEGEN.get(p.get("facing", "north"), "north")]
    if k.endswith("glass_pane") or k == "iron_bars":
        if p.get("east") == "true" or p.get("west") == "true":
            return _m((0, 0, 1), (1, 0, 1), (0, 1, 1), (1, 1, 1))
        if p.get("north") == "true" or p.get("south") == "true":
            return _m((1, 0, 0), (1, 1, 0), (1, 0, 1), (1, 1, 1))
        return SAEULE
    if k.endswith("_fence") or k == "chain" or k.endswith("_fence_gate"):
        return SAEULE
    if k.endswith("_wall") and "wall_" not in k:
        return UNTEN | SAEULE
    if k in ("ladder",):
        return SEITE[GEGEN.get(p.get("facing", "north"), "north")]
    if k in ("vine", "glow_lichen"):
        for s in ("north", "south", "east", "west"):
            if p.get(s) == "true":
                return SEITE[s]
        return PUNKT
    if k in ("lantern", "soul_lantern"):
        return PUNKT_OBEN if p.get("hanging") == "true" else PUNKT
    if k in ("campfire", "soul_campfire", "stonecutter", "enchanting_table"):
        return UNTEN
    if any(t in k for t in DUENN_UNTEN):
        return UNTEN
    if k in ("tall_grass", "large_fern", "rose_bush", "peony", "lilac", "sunflower"):
        return SAEULE
    if any(t in k for t in PFLANZEN):
        return PUNKT
    if k in ("cobweb", "hanging_roots", "cave_vines", "cave_vines_plant", "weeping_vines", "weeping_vines_plant",
             "twisting_vines", "twisting_vines_plant", "spore_blossom", "glow_berries"):
        return SAEULE
    if k in ("bell", "brewing_stand", "lectern", "grindstone", "anvil", "chipped_anvil", "damaged_anvil",
             "decorated_pot", "flower_pot", "cauldron", "water_cauldron", "lava_cauldron", "composter"):
        return _VOLL
    if k in ("water", "lava"):
        return _VOLL
    return _VOLL


def als_raster_fein(welt, deko=True):
    """Feines Raster (2× Auflösung) mit Farbvarianten für Textur-Rauschen."""
    lo, hi = welt.grenzen()
    g = (hi - lo + 1) * N
    idx = np.zeros(g, dtype=np.int32)
    P = welt.P
    cache = {}
    varianten = 3
    for (x, y, z), s in welt.bloecke.items():
        if s == 0:
            continue
        m = cache.get(s)
        if m is None:
            name, props = P.eintraege[s]
            if name == "minecraft:air":
                m = False
            else:
                m = form(name, props)
            cache[s] = m
        if m is False:
            continue
        bx, by, bz = (x - lo[0]) * N, (y - lo[1]) * N, (z - lo[2]) * N
        sub = idx[bx:bx + N, by:by + N, bz:bz + N]
        v = (x * 73856093 ^ y * 19349663 ^ z * 83492791) % varianten
        sub[m] = s * varianten + v
    # Farben
    ids = np.unique(idx[idx > 0])

    @dataclass
    class B:
        rgb: tuple

    groesste = int(idx.max()) if idx.size else 0
    liste = [B((220, 0, 220))] * groesste
    hell = [0.93, 1.0, 1.07]
    for i in ids:
        s, v = divmod(int(i), varianten)
        name = P.eintraege[s][0]
        kurz = name.split(":")[1]
        f = farbe_von(kurz) if name.startswith("minecraft:") else FARBEN.get(name)
        if f is None and name.startswith("mcwroofs:"):
            basis = kurz
            for suf in ("_top_roof", "_attic_roof", "_lower_roof", "_steep_roof", "_upper_steep_roof",
                        "_upper_lower_roof", "_roof"):
                if basis.endswith(suf):
                    basis = basis[: -len(suf)]
                    break
            f = farbe_von(basis)
        if f is None:
            f = farbe_von(P.name(s).split(":")[1])
        f = f or (220, 0, 220)
        h = hell[v]
        liste[int(i) - 1] = B(tuple(min(255, int(c * h)) for c in f))
    return idx, liste

"""Veredeln – hebt ältere Bauten auf den aktuellen Detailgrad.

- textur(): ersetzt einfarbige Flächen durch fleckige Mehrblock-Mischungen mit Höhenverlauf
  (Marmor, Sandstein, Stein, Ziegel, Holz, Erde …), Treppen/Stufen bleiben unverändert.
- boden(): verwandelt flache Grasplatten in lebendigen Boden mit Erde, Moos, Kies, Blumen und Gras.
- bewuchs(): Moos auf Kanten, Ranken an Wänden (wahlweise).
- rand_ausfransen(): rundet eckige Grundplatten zu natürlichen Rändern ab.
"""

from __future__ import annotations

import math

from lib import Rauschen, laub

GRUPPEN = {
    "marmor": (("quartz_block", "smooth_quartz", "quartz_bricks", "calcite", "polished_diorite", "end_stone",
                "white_concrete"),
               ["polished_andesite", "diorite", "polished_diorite", "calcite", "quartz_bricks", "smooth_quartz",
                "smooth_quartz"]),
    "sandstein": (("sandstone", "cut_sandstone", "smooth_sandstone"),
                  ["sandstone", "cut_sandstone", "smooth_sandstone", "smooth_sandstone", "chiseled_sandstone",
                   "cut_sandstone"]),
    "rotsand": (("red_sandstone", "cut_red_sandstone", "smooth_red_sandstone"),
                ["red_sandstone", "cut_red_sandstone", "smooth_red_sandstone", "orange_terracotta",
                 "smooth_red_sandstone"]),
    "stein": (("stone_bricks", "stone", "cobblestone", "andesite", "polished_andesite"),
              ["stone_bricks", "stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "andesite", "cobblestone",
               "stone", "polished_andesite"]),
    "tief": (("deepslate_bricks", "deepslate_tiles", "polished_deepslate", "cobbled_deepslate"),
             ["deepslate_bricks", "deepslate_tiles", "cracked_deepslate_bricks", "polished_deepslate",
              "cobbled_deepslate"]),
    "schwarz": (("blackstone", "polished_blackstone", "polished_blackstone_bricks"),
                ["polished_blackstone_bricks", "blackstone", "cracked_polished_blackstone_bricks",
                 "polished_blackstone", "basalt"]),
    "ziegel": (("bricks",), ["bricks", "bricks", "mud_bricks", "granite", "bricks"]),
    "dunkelholz": (("dark_oak_planks", "dark_oak_log"),
                   ["dark_oak_planks", "dark_oak_planks", "spruce_planks", "stripped_dark_oak_log"]),
    "fichte": (("spruce_planks",), ["spruce_planks", "spruce_planks", "dark_oak_planks", "stripped_spruce_log"]),
    "eiche": (("oak_planks",), ["oak_planks", "oak_planks", "stripped_oak_log", "spruce_planks"]),
    "erde": (("dirt", "coarse_dirt"), ["coarse_dirt", "dirt", "rooted_dirt", "podzol", "coarse_dirt"]),
}

ACHSE = {"stripped_dark_oak_log", "stripped_spruce_log", "stripped_oak_log", "basalt", "dark_oak_log"}
SCHNEE = {"podzol", "grass_block", "mycelium"}


def _blk(w, name):
    if name in ACHSE:
        return w.b(name, axis="y")
    if name in SCHNEE:
        return w.b(name, snowy=False)
    return w.b(name)


def textur(w, gruppen=None, zelle=2.2, verlauf=True, ausnahme_y=None):
    """Mischt Flächen aus den angegebenen Gruppen (Standard: alle) neu – rauschbasiert mit Höhenverlauf."""
    gruppen = gruppen or list(GRUPPEN)
    r1 = Rauschen(w, zelle)
    r2 = Rauschen(w, 0.9)
    karte = {}
    for g in gruppen:
        quellen, ziel = GRUPPEN[g]
        ids = [_blk(w, n) for n in ziel]
        for q in quellen:
            karte[q] = ids
    if not w.bloecke:
        return w
    ys = [p[1] for p in w.bloecke]
    y0, y1 = min(ys), max(ys)
    for p, b in list(w.bloecke.items()):
        n = w.P.name(b)
        if not n.startswith("minecraft:"):
            continue
        k = n[10:]
        if k not in karte or (w.P.eintraege[b][1] and k not in ACHSE):
            continue
        if ausnahme_y is not None and p[1] <= ausnahme_y:
            continue
        ids = karte[k]
        v = r1(*p) * 0.7 + r2(*p) * 0.3
        if verlauf and y1 > y0:
            t = (p[1] - y0) / (y1 - y0)
            v = min(0.999, v * 0.7 + t * 0.3) if len(ids) > 3 else v
        w.bloecke[p] = ids[min(len(ids) - 1, int(v * len(ids)))]
    return w


def boden(w, art="wiese", pflanzen=0.35):
    """Gras-, Sand- oder Erdplatten auf y=0 beleben (Flecken, Wege-Spuren, Blumen)."""
    r1 = Rauschen(w, 4)
    r2 = Rauschen(w, 1.5)
    rng = w.rng
    gras = w.P.index.get(("minecraft:grass_block", (("snowy", "false"),)))
    sand = w.P.index.get(("minecraft:sand", ()))
    if art == "wiese":
        flecken = [("grass_block", 0.62), ("moss_block", 0.08), ("coarse_dirt", 0.1), ("podzol", 0.08),
                   ("grass_block", 0.12)]
        pfl = ["grass", "grass", "fern", "dandelion", "poppy", "oxeye_daisy", "azure_bluet", "cornflower", "grass"]
    elif art == "trocken":
        flecken = [("grass_block", 0.5), ("coarse_dirt", 0.25), ("rooted_dirt", 0.1), ("gravel", 0.15)]
        pfl = ["grass", "dead_bush", "grass", "fern"]
    else:
        flecken = [("sand", 0.65), ("sandstone", 0.12), ("gravel", 0.08), ("sand", 0.15)]
        pfl = ["dead_bush"]
    kum = []
    s = 0
    for n, g in flecken:
        s += g
        kum.append((s, _blk(w, n)))
    for (x, y, z), b in list(w.bloecke.items()):
        if y != 0 or b not in (gras, sand) or b is None:
            continue
        v = r1(x, 0, z) * 0.75 + r2(x, 0, z) * 0.25
        for grenze, blk in kum:
            if v <= grenze * 1.0 / s:
                w.bloecke[(x, y, z)] = blk
                break
        if w.frei(x, 1, z) and rng.random() < pflanzen * (0.5 + r2(x, 3, z)):
            w.setze(x, 1, z, w.b(pfl[int(rng.integers(len(pfl)))]))
    return w


def rand_ausfransen(w, staerke=4):
    """Quadratische Grundplatten (y=0 und darunter) zu einer organischen Insel runden."""
    platte = [(x, z) for (x, y, z) in w.bloecke if y == 0]
    if not platte:
        return w
    xs = [p[0] for p in platte]
    zs = [p[1] for p in platte]
    cx, cz = (min(xs) + max(xs)) / 2, (min(zs) + max(zs)) / 2
    rx, rz = (max(xs) - min(xs)) / 2 + 0.5, (max(zs) - min(zs)) / 2 + 0.5
    r1 = Rauschen(w, 5)
    oben = {}
    for (x, y, z) in w.bloecke:
        if y >= 1:
            oben[(x, z)] = True
    for (x, y, z) in list(w.bloecke):
        if y > 0 or (x, z) in oben:
            continue
        d = math.hypot((x - cx) / rx, (z - cz) / rz)
        if d > 0.86 + 0.14 * r1(x, 0, z):
            del w.bloecke[(x, y, z)]
    return w


def bewuchs(w, moos=0.04, ranken=0.0, nur_unter=None):
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y < 2 or (nur_unter and y > nur_unter):
            continue
        n = w.P.name(b)
        if not any(k in n for k in ("stone", "brick", "cobble", "sandstone", "quartz", "calcite", "diorite",
                                    "andesite", "deepslate")) or "stairs" in n or "slab" in n or "wall" in n:
            continue
        if moos and w.frei(x, y + 1, z) and rng.random() < moos:
            w.setze(x, y + 1, z, w.b("moss_carpet"))
        if ranken and rng.random() < ranken:
            for dx, dz, seite in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
                if w.frei(x + dx, y, z + dz):
                    for k in range(int(1 + rng.integers(4))):
                        if not w.frei(x + dx, y - k, z + dz) or y - k < 1:
                            break
                        w.setze(x + dx, y - k, z + dz, w.b("vine", **{s: s == seite for s in
                                                                      ("north", "south", "east", "west")}, up=False))
                    break
    return w


def grund(w, art="wiese", rand=4, dichte=0.4):
    """Lebendiges Gelände rund um den Bau (nur wo y=0 frei ist)."""
    import pracht as P
    if not w.bloecke:
        return w
    xs = [p[0] for p in w.bloecke]
    zs = [p[2] for p in w.bloecke]
    cx, cz = round((min(xs) + max(xs)) / 2), round((min(zs) + max(zs)) / 2)
    R = max(max(xs) - min(xs), max(zs) - min(zs)) / 2 + rand
    P.gelaende(w, int(R), cx, cz, art={"trocken": "wiese"}.get(art, art), dichte=dichte)
    return w


def veredle(w, art="wiese", gruppen=None, moos=0.03, ranken=0.0, runden=True, gelaende=True):
    textur(w, gruppen)
    if gelaende and art in ("wiese", "sand", "wald", "schnee", "asche", "trocken"):
        grund(w, art)
    else:
        boden(w, art)
        if runden:
            rand_ausfransen(w)
    if moos or ranken:
        bewuchs(w, moos, ranken)
    return w


def veredelt(tabelle, **kw):
    """Gibt eine neue Tabelle zurück, deren Bauten beim Erzeugen veredelt werden."""
    neu = {}
    for k, (name, f) in tabelle.items():
        def g(seed, groesse=1, f=f):
            return veredle(f(seed, groesse), **kw)
        g.__doc__ = f.__doc__
        neu[k] = (name, g)
    return neu

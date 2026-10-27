"""Brücken und hängende Gärten – in allen Größen und mit verschiedenen Materialien.

Brücken laufen entlang x; der Anker liegt am Anfang der Brücke auf Laufhöhe.
Größen 0 klein · 1 mittel · 2 riesig · 3 gigantisch.
"""

from __future__ import annotations

import math

from baeume import azaleenbaum, kirschbaum
from lib import Rauschen, Verlauf, Welt, laub, ueberwuchern

LAENGE = [12, 22, 36, 60]

MATERIAL = {
    "stein": dict(boden=["cobblestone", "stone_bricks", "polished_andesite", "stone_bricks"], bogen="stone_bricks",
                  gelaender="stone_brick_wall", pfeiler=["andesite", "stone_bricks", "chiseled_stone_bricks"]),
    "tiefenschiefer": dict(boden=["cobbled_deepslate", "deepslate_bricks", "deepslate_tiles", "polished_deepslate"],
                           bogen="deepslate_bricks", gelaender="deepslate_brick_wall",
                           pfeiler=["cobbled_deepslate", "deepslate_bricks", "deepslate_tiles"]),
    "sandstein": dict(boden=["sandstone", "cut_sandstone", "smooth_sandstone", "chiseled_sandstone"],
                      bogen="cut_sandstone", gelaender="sandstone_wall",
                      pfeiler=["sandstone", "cut_sandstone", "smooth_sandstone"]),
    "ziegel": dict(boden=["bricks", "mud_bricks", "packed_mud", "bricks"], bogen="bricks", gelaender="brick_wall",
                   pfeiler=["bricks", "mud_bricks", "packed_mud"]),
}
HOLZ = ["spruce", "dark_oak", "cherry", "mangrove", "oak", "birch"]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _anheben(w, extra=1):
    """Schiebt die Brücke so hoch, dass ihr tiefster Punkt auf dem Boden steht (Anker = Boden)."""
    lo = min(p[1] for p in w.bloecke)
    w.bloecke = {(x, y - lo + extra, z): b for (x, y, z), b in w.bloecke.items()}
    return w


def _mauer(w, name):
    return w.b(name, east="low", west="low", north="none", south="none", up=True, waterlogged=False)


def steinbruecke(seed, g=1, material="stein"):
    """Bogenbrücke aus Stein mit Pfeilern, Brüstung, Laternen und Moos."""
    w = _welt(seed)
    m = MATERIAL[material]
    boden = Verlauf(w, "Boden", m["boden"])
    pfeiler = Verlauf(w, "Pfeiler", m["pfeiler"])
    L = LAENGE[g]
    breite = [3, 5, 7, 9][g]
    hoch = [6, 10, 16, 26][g]
    spann = [10, 12, 14, 18][g]
    for x in range(L + 1):
        k = x % spann
        u = (k - spann / 2) / (spann / 2)
        bogen_y = int(-hoch * 0.35 * (1 - u * u)) if 0 < x < L else -hoch
        for z in range(-breite // 2, breite // 2 + 1):
            w.setze(x, 0, z, boden(1 + 2 * abs(z) / max(1, breite // 2) + w.rng.random(), x, 0, z))
            for y in range(-hoch, 0):
                if y >= bogen_y + 0 and (y > -3 or k in (0, 1, spann - 1) or y >= bogen_y):
                    if k in (0, spann - 1) or y >= bogen_y:
                        w.setze(x, y, z, pfeiler(1.0 + (y + hoch) / hoch * 1.5, x, y, z))
        for z in (-breite // 2 - 1, breite // 2 + 1):
            w.setze(x, 0, z, w.b(m["bogen"]))
            w.setze(x, 1, z, _mauer(w, m["gelaender"]))
            if x % spann == 0:
                w.setze(x, 2, z, w.b("lantern", hanging=False, waterlogged=False))
    ueberwuchern(w, None, ranken=0.12, pflanzen=0.1, buesche=0.02, max_ranke=hoch // 2)
    return _anheben(w, 1 if "steinbruecke" not in ("kristallbruecke", "haengebruecke") else 8)


def holzbruecke(seed, g=1, holz="spruce"):
    """Holzbrücke auf Stelzen mit Geländer, Laternen und Querstreben."""
    w = _welt(seed)
    L = LAENGE[g]
    breite = [3, 3, 5, 7][g]
    hoch = [5, 8, 12, 18][g]
    planke = Verlauf(w, "Planken", [f"stripped_{holz}_log", f"{holz}_planks", f"{holz}_planks"])
    for x in range(L + 1):
        for z in range(-breite // 2, breite // 2 + 1):
            w.setze(x, 0, z, planke(1 + w.rng.random() * 1.5, x, 0, z) if not planke.namen[0].endswith("_log")
                    else w.b(f"{holz}_planks") if (x + z) % 3 else w.b(f"stripped_{holz}_log", axis="z"))
        for z in (-breite // 2 - 1, breite // 2 + 1):
            if x % 4 == 0:
                for y in range(-hoch, 2):
                    w.setze(x, y, z, w.b(f"{holz}_log", axis="y"))
                if x % 8 == 0:
                    w.setze(x, 2, z, w.b("lantern", hanging=False, waterlogged=False))
            else:
                w.setze(x, 1, z, w.b(f"{holz}_fence", east=True, west=True, north=False, south=False,
                                     waterlogged=False))
        if x % 8 == 4:
            for k in range(1, hoch):
                for z in (-breite // 2 - 1 + k % 2 * 0, ):
                    pass
            for z in range(-breite // 2 - 1, breite // 2 + 2):
                w.setze(x, -hoch // 2, z, w.b(f"{holz}_log", axis="z"))
    return _anheben(w, 1 if "holzbruecke" not in ("kristallbruecke", "haengebruecke") else 8)


def haengebruecke(seed, g=1, holz="spruce"):
    """Hängebrücke mit Durchhang, Seil-Ketten, Laternen und Ranken."""
    w = _welt(seed)
    L = LAENGE[g]
    durchhang = [2, 4, 7, 12][g]
    breite = [1, 1, 2, 2][g]
    for x in range(L + 1):
        t = x / L
        y = int(round(-durchhang * 4 * t * (1 - t)))
        for z in range(-breite, breite + 1):
            w.setze(x, y, z, w.b(f"{holz}_planks") if (x % 3) else w.b(f"{holz}_slab", type="top", waterlogged=False))
        hand = int(round(-durchhang * 0.6 * 4 * t * (1 - t))) + 2
        for z in (-breite - 1, breite + 1):
            w.setze(x, hand, z, w.b("chain", axis="x", waterlogged=False))
            if x % 4 == 0:
                for k in range(y + 1, hand):
                    w.setze(x, k, z, w.b("chain", axis="y", waterlogged=False))
    for x in (0, L):
        for z in (-breite - 1, breite + 1):
            for k in range(0, 4):
                w.setze(x, k, z, w.b(f"{holz}_log", axis="y"))
            w.setze(x, 4, z, w.b("lantern", hanging=False, waterlogged=False))
    blatt = laub(w, "azalea")
    for x in range(2, L - 1):
        if w.rng.random() < 0.15:
            t = x / L
            y = int(round(-durchhang * 4 * t * (1 - t)))
            for k in range(1, int(2 + w.rng.random() * 5)):
                w.setze(x, y - k, breite + 1 if w.rng.random() < 0.5 else -breite - 1, blatt)
    return _anheben(w, 1 if "haengebruecke" not in ("kristallbruecke", "haengebruecke") else 8)


def ruinenbruecke(seed, g=1):
    """Eingestürzte Steinbrücke: Lücken, Schutt, viel Moos und Ranken."""
    w = steinbruecke(seed, g, "stein")
    rs = Rauschen(w, 4)
    L = LAENGE[g]
    for (x, y, z) in list(w.bloecke):
        if rs(x, y, z) > 0.72 or (abs(x - L * 0.55) < L * 0.08 and y > 2):
            del w.bloecke[(x, y, z)]
    ueberwuchern(w, None, ranken=0.3, pflanzen=0.4, buesche=0.08, max_ranke=10)
    return w


def kristallbruecke(seed, g=1):
    """Schwebende Brücke aus Glas und Amethyst mit Leuchtsteinen – ohne Pfeiler."""
    w = _welt(seed)
    L = LAENGE[g]
    breite = [1, 2, 3, 4][g]
    glas = Verlauf(w, "Kristall", ["purple_stained_glass", "magenta_stained_glass", "light_blue_stained_glass",
                                   "white_stained_glass"])
    for x in range(L + 1):
        t = x / L
        y = int(round(3 * math.sin(math.pi * t)))
        for z in range(-breite, breite + 1):
            w.setze(x, y, z, glas(3.0 * abs(z) / max(1, breite) + w.rng.random() * 0.8, x, y, z))
        if x % 5 == 0:
            for z in (-breite - 1, breite + 1):
                w.setze(x, y + 1, z, w.b("amethyst_block"))
                w.setze(x, y + 2, z, w.b("amethyst_cluster", facing="up", waterlogged=False))
            w.setze(x, y - 1, 0, w.b("sea_lantern"))
    return _anheben(w, 1 if "kristallbruecke" not in ("kristallbruecke", "haengebruecke") else 8)


def wurzelbruecke(seed, g=1):
    """Lebende Brücke aus verflochtenen Wurzeln mit Moos und Laub."""
    w = _welt(seed)
    L = LAENGE[g]
    holz = {a: w.b("mangrove_log", axis=a) for a in "xyz"}
    for strang in range([3, 4, 6, 8][g]):
        phase = strang * 1.7
        for i in range(L * 3 + 1):
            t = i / (L * 3)
            x = t * L
            y = -2 * 4 * t * (1 - t) + 0.8 * math.sin(t * 12 + phase)
            z = 1.6 * math.cos(t * 9 + phase) * (1 + strang * 0.15)
            w.setze(int(x), int(round(y)), int(round(z)), holz["x"])
    for (x, y, z) in list(w.bloecke):
        if w.frei(x, y + 1, z) and w.rng.random() < 0.6:
            w.setze(x, y + 1, z, w.b("moss_carpet"))
    blatt = laub(w, "azalea")
    for (x, y, z) in list(w.bloecke):
        if w.rng.random() < 0.06:
            for k in range(1, int(2 + w.rng.random() * 4)):
                if w.frei(x, y - k, z):
                    w.setze(x, y - k, z, blatt)
    return _anheben(w, 1 if "wurzelbruecke" not in ("kristallbruecke", "haengebruecke") else 8)


# ---------------------------------------------------------------------------- Hängende Gärten


def haengender_garten(seed, g=1, stil="stein"):
    """Terrassierter Garten: Stufen mit Pflanzkästen, aus denen Laub, Blumen und Ranken herabhängen."""
    w = _welt(seed)
    m = MATERIAL[stil]
    stein = Verlauf(w, "Mauer", m["pfeiler"])
    stufen = [3, 4, 6, 9][g]
    R = [6, 9, 14, 22][g]
    hoehe = [3, 4, 5, 6][g]
    blatt = [laub(w, "azalea"), laub(w, "flowering_azalea"), laub(w, "oak")]
    blumen = ["poppy", "dandelion", "allium", "azure_bluet", "red_tulip", "pink_tulip", "cornflower"]
    for s in range(stufen):
        r = R * (1 - s / (stufen + 0.5))
        y0 = s * hoehe
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = max(abs(x), abs(z))
                if d > r:
                    continue
                for y in range(y0, y0 + hoehe):
                    w.setze(x, y, z, stein(1 + 1.5 * (y - y0) / hoehe + w.rng.random() * 0.5, x, y, z))
                rand = d > r - 1
                if rand:
                    w.setze(x, y0 + hoehe, z, w.b("grass_block", snowy=False))
                    w.setze(x, y0 + hoehe + 1, z, blatt[int(w.rng.random() * 3)] if w.rng.random() < 0.6
                            else w.b(blumen[int(w.rng.random() * len(blumen))]))
                    # herabhängendes Laub über die Stufenkante
                    if w.rng.random() < 0.45:
                        for k in range(1, int(1 + w.rng.random() * (hoehe + 2))):
                            dx = 1 if x > 0 and abs(x) >= abs(z) else -1 if abs(x) >= abs(z) else 0
                            dz = 0 if dx else (1 if z > 0 else -1)
                            if w.frei(x + dx, y0 + hoehe - k, z + dz):
                                w.setze(x + dx, y0 + hoehe - k, z + dz, blatt[int(w.rng.random() * 2)])
                else:
                    w.setze(x, y0 + hoehe, z, w.b("grass_block", snowy=False))
    top = stufen * hoehe
    from baeume import kirschbaum as kb
    from lib import einfuegen
    einfuegen(w, kb(seed, min(2, g)), 0, top, 0)
    ueberwuchern(w, None, ranken=0.3, pflanzen=0.5, buesche=0.05, max_ranke=hoehe * 2)
    return w


def blumenampel(seed, g=1):
    """Hängende Pflanzschalen an Ketten (zum Aufhängen unter Inseln, Brücken, Dächern)."""
    w = _welt(seed)
    n = [1, 3, 5, 8][g]
    for i in range(n):
        x = (i - n // 2) * [0, 5, 6, 7][g]
        laenge = int(3 + w.rng.random() * [3, 6, 10, 14][g])
        top = 20
        for y in range(top - laenge, top + 1):
            w.setze(x, y, 0, w.b("chain", axis="y", waterlogged=False))
        y = top - laenge - 1
        r = [1, 1, 2, 2][g]
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                w.setze(x + dx, y, dz, w.b("moss_block"))
                w.setze(x + dx, y - 1, dz, w.b("dark_oak_planks") if abs(dx) + abs(dz) <= r else 0)
                w.setze(x + dx, y + 1, dz, laub(w, "flowering_azalea") if w.rng.random() < 0.5 else w.b("poppy"))
        for dx in range(-r - 1, r + 2):
            for dz in range(-r - 1, r + 2):
                if max(abs(dx), abs(dz)) == r + 1 and w.rng.random() < 0.5:
                    for k in range(0, int(2 + w.rng.random() * 5)):
                        w.setze(x + dx, y - k, dz, laub(w, "azalea"))
    return w


BRUECKEN = {}
for _m in MATERIAL:
    BRUECKEN[f"steinbruecke_{_m}"] = (f"Bogenbrücke ({_m})", lambda s, g, m=_m: steinbruecke(s, g, m))
for _h in ("spruce", "dark_oak", "cherry", "mangrove"):
    BRUECKEN[f"holzbruecke_{_h}"] = (f"Holzbrücke ({_h})", lambda s, g, h=_h: holzbruecke(s, g, h))
    BRUECKEN[f"haengebruecke_{_h}"] = (f"Hängebrücke ({_h})", lambda s, g, h=_h: haengebruecke(s, g, h))
BRUECKEN["ruinenbruecke"] = ("Eingestürzte Brücke", ruinenbruecke)
BRUECKEN["kristallbruecke"] = ("Kristallbrücke", kristallbruecke)
BRUECKEN["wurzelbruecke"] = ("Wurzelbrücke", wurzelbruecke)

GAERTEN = {}
for _m in MATERIAL:
    GAERTEN[f"haengender_garten_{_m}"] = (f"Hängender Garten ({_m})", lambda s, g, m=_m: haengender_garten(s, g, m))
GAERTEN["blumenampel"] = ("Hängende Blumenampeln", blumenampel)

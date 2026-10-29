"""Schildkröten-Inseln II – zwanzig weitere lebende Inseln: Schildkröten mit Leuchtturm, Schrein, Urwald, Hafen,
Eis, Oase, Burg, Mühle, Kristallen, Garten und Geisterruinen, eine Schildkrötenfamilie, dazu Walinsel,
Krabbenhütte, Schneckenhaus-Dorf, Fischinsel mit Leuchtturm, Seeschlangen-Bögen, Kraken-Fels, Riesenmuschel
mit Perlenpalast und eine Quallenkuppel.

y = 0 ist die Wasseroberfläche (Anker auf die oberste Wasserschicht setzen). Der Kopf zeigt nach +x."""

from __future__ import annotations

import math

import numpy as np

import wald2
from feinbau import (Dachmat, Mix, balkon, busch, efeu, fachwerk, fenster, fensterreihe, kamin, kegeldach,
                     kragsteine, kram, laterne, mauer, platte, satteldach, stamm, stein, treppe, tuer, zaun)
from flora import _neu, _r, linie
from lib import Rauschen, einfuegen
from skulptur import Skulptur, ell, kap, torus

LG = [26, 36, 48, 64]

PALETTEN = {
    "gruen": dict(fuge="dark_prismarine", platte=["prismarine", "waxed_oxidized_copper", "waxed_weathered_copper",
                                                  "waxed_oxidized_cut_copper"], rand="prismarine_bricks",
                  haut=["waxed_oxidized_copper", "prismarine", "waxed_weathered_copper"], bauch="smooth_sandstone"),
    "braun": dict(fuge="dark_oak_planks", platte=["brown_terracotta", "terracotta", "packed_mud", "mud_bricks"],
                  rand="spruce_planks", haut=["brown_terracotta", "terracotta", "light_gray_terracotta"],
                  bauch="smooth_sandstone"),
    "eis": dict(fuge="blue_ice", platte=["packed_ice", "snow_block", "packed_ice", "light_blue_terracotta"],
                rand="blue_ice", haut=["light_blue_terracotta", "white_terracotta", "light_gray_terracotta"],
                bauch="calcite"),
    "stein": dict(fuge="deepslate_tiles", platte=["mossy_cobblestone", "andesite", "stone", "tuff"],
                  rand="polished_deepslate", haut=["andesite", "stone", "tuff"], bauch="calcite"),
    "geist": dict(fuge="black_concrete", platte=["bone_block", "calcite", "diorite", "smooth_quartz"],
                  rand="polished_blackstone", haut=["bone_block", "calcite", "diorite"], bauch="smooth_quartz"),
    "sand": dict(fuge="cut_red_sandstone", platte=["smooth_sandstone", "sandstone", "yellow_terracotta", "end_stone"],
                 rand="red_sandstone", haut=["yellow_terracotta", "smooth_sandstone", "terracotta"],
                 bauch="smooth_sandstone"),
}


def _mixfn(w, namen, zelle=1.6):
    M = Mix(w, [(n, 1) for n in namen], zelle=zelle, axis="y") if False else Mix(w, [(n, 1) for n in namen],
                                                                                 zelle=zelle)
    return M


def wasserflaeche(w, R, tiefe=2):
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                for y in range(-tiefe + 1, 1):
                    if (x, y, z) not in w.bloecke:
                        w.setze(x, y, z, w.b("water", level=0))


def schildkroete(w, L, pal="gruen", cx=0, cz=0, kopf_hoch=True):
    """Riesenschildkröte; gibt (oben_y, a, b) zurück – oben_y: {(x, z): Panzeroberkante}."""
    P = PALETTEN[pal]
    a, b, c = L / 2, 0.38 * L, 0.27 * L
    rs = Rauschen(w, 5)
    platte_m = _mixfn(w, P["platte"])
    fuge, rand = w.b(P["fuge"]), w.b(P["rand"])
    zentren = [(u * a, 0.0) for u in (-0.66, -0.34, -0.02, 0.3, 0.6)]
    for s in (-1, 1):
        zentren += [(u * a, s * 0.52 * b) for u in (-0.52, -0.17, 0.18, 0.5)]
    zentren = np.array(zentren)
    oben = {}
    for x in range(int(-a) - 1, int(a) + 2):
        for z in range(int(-b) - 1, int(b) + 2):
            q = (x / a) ** 2 + (z / b) ** 2
            if q >= 1:
                continue
            top = int(round(c * (1 - q) ** 0.5))
            unten = -2
            oben[(cx + x, cz + z)] = top
            if q > 0.8:
                for y in range(unten, top + 1):
                    w.setze(cx + x, y, cz + z, w.b(P["bauch"]) if y <= 0 and q > 0.9 else rand)
                continue
            dd = np.hypot(zentren[:, 0] - x, (zentren[:, 1] - z) * 1.1)
            o = np.argsort(dd)[:2]
            ab = dd[o[1]] - dd[o[0]]
            for y in range(max(unten, top - 2), top + 1):
                w.setze(cx + x, y, cz + z, fuge if ab < 1.5 else platte_m(x, y, z))
    s = L / 40
    S = Skulptur(w, s)
    haut = _mixfn(w, P["haut"])
    S.mat("k", lambda x, y, z, *_: haut(x, y, z))
    S.mat("a", lambda x, y, z, *_: w.b("black_concrete"))
    S.mat("w", lambda x, y, z, *_: w.b("white_concrete"))
    hy = 3 if kopf_hoch else 1
    S.plus(kap((17, 0, 0), (24, hy, 0), 3.2, 2.8), "k")
    S.plus(ell(25.5, hy + 1, 0, 4.0, 3.0, 3.3), "k")
    for sz in (-1, 1):
        S.plus(ell(27.2, hy + 2.0, sz * 2.3, 0.9, 0.9, 0.7), "a")
        S.plus(ell(27.6, hy + 2.4, sz * 2.1, 0.35, 0.35, 0.35), "w")
        S.plus(kap((10, -0.5, sz * 13), (17, -0.2, sz * 22), 2.6, 1.2), "k")
        S.plus(kap((-12, -0.5, sz * 12), (-17, -0.6, sz * 18), 2.2, 1.0), "k")
    S.plus(kap((-19, -0.3, 0), (-25, -0.6, 0), 1.6, 0.6), "k")
    S.rendern((-28, -3, -25), (31, 9, 25), versatz=(cx, 0, cz), ueberschreiben=False)
    return oben, a, b


def aufsatz(w, oben, cx, cz, a, b, art="wiese", rx=0.62, rz=0.62, hoch=0, rand_fels=("stone", "andesite",
                                                                                         "mossy_cobblestone", "tuff")):
    """Erdreich/Insel auf dem Panzer: eine gerundete Kappe mit Felsrand. Gibt {(x, z): y_oben}."""
    rs = Rauschen(w, 4)
    ob = {"wiese": "grass_block", "sand": "sand", "schnee": "snow_block", "moos": "moss_block",
          "asche": "soul_soil"}[art]
    fels = Mix(w, [(n, 1) for n in rand_fels])
    insel = {}
    for (x, z), top in oben.items():
        e = ((x - cx) / (rx * a)) ** 2 + ((z - cz) / (rz * b)) ** 2
        if e > 1 + 0.25 * (rs(x, 0, z) - 0.5):
            continue
        y_ob = top + 1 + (1 if e < 0.7 else 0) + int(hoch * max(0, 1 - e) ** 0.8)
        insel[(x, z)] = y_ob
        for y in range(top + 1, y_ob + 1):
            if y == y_ob:
                w.setze(x, y, z, w.b(ob, snowy=False) if ob == "grass_block" else w.b(ob))
            elif y >= y_ob - 1:
                w.setze(x, y, z, w.b("dirt") if ob in ("grass_block", "moss_block") else w.b("sandstone")
                        if ob == "sand" else w.b("packed_ice") if ob == "snow_block" else w.b("soul_sand"))
            else:
                w.setze(x, y, z, fels(x, y, z))
    return insel


def flach(w, insel, cx, cz, r, y=None):
    """Ebnet einen runden Bauplatz auf der Insel auf Höhe y (Standard: höchster Punkt im Kreis)."""
    zellen = [(x, z) for (x, z) in insel if math.hypot(x - cx, z - cz) <= r]
    if not zellen:
        return 1
    y = y if y is not None else max(insel[p] for p in zellen)
    for (x, z) in zellen:
        y0 = insel[(x, z)]
        if y0 < y:
            for yy in range(y0, y):
                w.setze(x, yy, z, w.b("dirt"))
            w.setze(x, y, z, w.b("grass_block", snowy=False))
        elif y0 > y:
            for yy in range(y + 1, y0 + 1):
                w.bloecke.pop((x, yy, z), None)
            w.setze(x, y, z, w.b("grass_block", snowy=False))
        insel[(x, z)] = y
    return y


def begruenen(w, insel, dichte=0.35, baeume=0, arten=("oak",), blumen=True):
    rng = w.rng
    for (x, z), y in insel.items():
        if w.P.name(w.bloecke.get((x, y, z), 0)) not in ("minecraft:grass_block", "minecraft:moss_block"):
            continue
        if not w.frei(x, y + 1, z):
            continue
        r = rng.random()
        if r < dichte * 0.5:
            w.setze(x, y + 1, z, w.b("grass"))
        elif r < dichte * 0.62:
            w.setze(x, y + 1, z, w.b("fern"))
        elif blumen and r < dichte * 0.75:
            w.setze(x, y + 1, z, w.b(["poppy", "dandelion", "oxeye_daisy", "azure_bluet", "cornflower"]
                                     [int(rng.random() * 5)]))
    plaetze = sorted(insel.items(), key=lambda kv: rng.random())
    gesetzt = []
    for (x, z), y in plaetze:
        if len(gesetzt) >= baeume:
            break
        if any(math.hypot(x - a, z - b) < 6 for a, b in gesetzt) or not all(w.frei(x, y + k, z) for k in (1, 3, 6)):
            continue
        art = arten[len(gesetzt) % len(arten)]
        sd = int(rng.integers(1, 10 ** 6))
        t = {"palme": wald2.palme, "kirsche": wald2.kirschbaum, "fichte": wald2.fichte, "birke": wald2.birke,
             "busch": wald2.busch}.get(art)
        t = t(sd) if t else wald2.laubbaum(sd, art, H=7 + int(rng.random() * 4))
        einfuegen(w, t, x, y, z)
        gesetzt.append((x, z))


def haeuschen(w, x, y, z, a=2, b=2, wand=None, dach=("spruce", "dark_oak"), holz="spruce", tuer_s="south",
              steil=1):
    wand = wand or Mix(w, [("white_terracotta", 2), ("calcite", 2), ("smooth_sandstone", 1)])
    fachwerk(w, x - a, z - b, x + a, z + b, y + 1, y + 4, wand, holz=holz, abstand=2)
    fenster(w, x + a, y + 2, z, "east", holz=holz, blumen=0.5)
    fenster(w, x - a, y + 2, z, "west", holz=holz, blumen=0.5)
    tuer(w, x, y + 1, z + b if tuer_s == "south" else z - b, tuer_s, holz=holz)
    return satteldach(w, x - a, z - b, x + a, z + b, y + 5, Dachmat(w, list(dach)), first_x=a >= b, ue=1,
                      giebel=wand, traufe=holz, steil=steil)


def leuchtturm(w, x, y, z, H=12, r=2):
    for yy in range(y + 1, y + H + 1):
        for dx in range(-r - 1, r + 2):
            for dz in range(-r - 1, r + 2):
                d = math.hypot(dx, dz)
                if r - 0.8 < d <= r + 0.4:
                    w.setze(x + dx, yy, z + dz, w.b("red_terracotta" if ((yy - y) // 3) % 2 else "white_terracotta"))
    for dx in range(-r - 1, r + 2):
        for dz in range(-r - 1, r + 2):
            d = math.hypot(dx, dz)
            if d <= r + 1.4:
                w.setze(x + dx, y + H + 1, z + dz, w.b("dark_oak_planks"))
                if d > r + 0.5:
                    w.setze(x + dx, y + H + 2, z + dz, w.b("iron_bars", north=False, south=False, east=False,
                                                           west=False, waterlogged=False))
    for yy in range(y + H + 2, y + H + 4):
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                w.setze(x + dx, yy, z + dz, w.b("yellow_stained_glass") if (dx or dz) else w.b("sea_lantern"))
    kegeldach(w, x, z, y + H + 4, 1.4, Dachmat(w, ["red_nether_brick", "nether_brick"]), form="kegel", h=4)


def steg(w, x, z, laenge, richtung=(0, 1), breite=1, y=1):
    dx, dz = richtung
    for k in range(laenge):
        for s in range(-breite, breite + 1):
            px, pz = x + dx * k + (s if dz else 0), z + dz * k + (s if dx else 0)
            w.setze(px, y, pz, w.b("spruce_planks"))
            if k % 3 == 0 and abs(s) == breite:
                for yy in range(-2, y):
                    w.setze(px, yy, pz, stamm(w, "spruce", geschaelt=False))
                w.setze(px, y + 1, pz, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                          waterlogged=False))


# ============================================================================ Schildkröten

def _basis(seed, g, pal="gruen", art="wiese", hoch=0, rx=0.62, rz=0.62):
    w = _neu(seed)
    L = LG[g]
    oben, a, b = schildkroete(w, L, pal)
    insel = aufsatz(w, oben, -0.18 * a, 0, a, b, art=art, rx=rx, rz=rz, hoch=hoch)
    wasserflaeche(w, int(L * 0.85))
    return w, L, oben, a, b, insel


def leuchtturm_schildkroete(seed, g=2):
    """Leuchtturm-Schildkröte: auf dem Panzer stehen ein rot-weißer Leuchtturm, ein Wärterhäuschen mit Kamin, ein
    Bootssteg mit Ruderboot und Palmen am Rand."""
    w, L, oben, a, b, insel = _basis(seed, g, hoch=3)
    y = flach(w, insel, -0.3 * a, -0.1 * b, 4)
    leuchtturm(w, round(-0.3 * a), y, round(-0.1 * b), H=_r(L * 0.3), r=2)
    y2 = flach(w, insel, 0.05 * a, 0.25 * b, 4)
    haeuschen(w, round(0.05 * a), y2, round(0.25 * b), 2, 2)
    steg(w, round(0.1 * a), round(b * 0.9), _r(L * 0.2))
    from boote import ruderboot
    einfuegen(w, ruderboot(seed, 0), round(0.1 * a) + 3, 0, round(b * 0.9) + _r(L * 0.15))
    begruenen(w, insel, baeume=2 + L // 20, arten=("palme",))
    return w


def schrein_schildkroete(seed, g=2):
    """Schrein-Schildkröte: ein kleiner Schrein mit geschwungenem Dach, eine Reihe roter Tore, Steinlaternen,
    Kirschbäume und ein Moosgarten auf dem Panzer."""
    w, L, oben, a, b, insel = _basis(seed, g, pal="braun", art="moos", hoch=2)
    cx, cz = round(-0.25 * a), 0
    y = flach(w, insel, cx, cz, 5)
    for x in range(cx - 3, cx + 4):
        for z in range(cz - 3, cz + 4):
            w.setze(x, y, z, w.b("spruce_planks"))
    for (x, z) in ((cx - 3, cz - 3), (cx + 3, cz - 3), (cx - 3, cz + 3), (cx + 3, cz + 3)):
        for yy in range(y + 1, y + 5):
            w.setze(x, yy, z, w.b("red_concrete"))
    satteldach(w, cx - 3, cz - 3, cx + 3, cz + 3, y + 5, Dachmat(w, ["dark_oak", "spruce"]), first_x=True, ue=2,
               ue_giebel=2, giebel=w.b("spruce_planks"), traufe="dark_oak")
    for k in range(3):
        tx = cx + 6 + k * 4
        ty = insel.get((tx, 0), y)
        for z in (-2, 2):
            for yy in range(ty + 1, ty + 6):
                w.setze(tx, yy, z, w.b("red_concrete"))
        for z in range(-3, 4):
            w.setze(tx, ty + 6, z, w.b("red_concrete"))
            w.setze(tx, ty + 7, z, platte(w, "dark_oak"))
    for (dx, dz) in ((-5, -4), (-5, 4)):
        x, z = cx + dx, cz + dz
        yy = insel.get((x, z), y)
        for k, n in enumerate(["stone_bricks", "stone_brick_wall", "lantern", "stone_brick_slab"]):
            w.setze(x, yy + 1 + k, z, w.b(n, **({"up": True, "north": "none", "south": "none", "east": "none",
                                                 "west": "none", "waterlogged": False} if "wall" in n else
                                                {"hanging": False, "waterlogged": False} if n == "lantern" else
                                                {"type": "bottom", "waterlogged": False} if "slab" in n else {})))
    begruenen(w, insel, baeume=3, arten=("kirsche",))
    return w


def urwald_schildkroete(seed, g=2):
    """Urwald-Schildkröte: der Panzer trägt einen hohen, dichten Urwaldhügel mit Riesenbäumen, Lianen und einem
    Wasserfall, der über den Panzerrand ins Meer stürzt."""
    w, L, oben, a, b, insel = _basis(seed, g, pal="gruen", art="moos", hoch=_r(L * 0.2))
    begruenen(w, insel, dichte=0.6, baeume=4 + L // 12, arten=("jungle", "oak", "jungle"))
    efeu(w, 0.12, laub=0.6)
    top = max(insel.items(), key=lambda kv: kv[1])
    (x0, z0), y0 = top
    w.vorschau_extra = {}
    for z in range(z0, int(b) + 3):
        y = insel.get((x0, z), oben.get((x0, z)))
        if y is None:
            for yy in range(0, y0 + 1):
                w.vorschau_extra[(x0, yy, z)] = w.b("water", level=0)
            break
        w.setze(x0, y, z, w.b("water", level=0))
    return w


def hafen_schildkroete(seed, g=3):
    """Hafen-Schildkröte: eine kleine Hafenstadt auf dem Panzer – Lagerhäuser, ein Kran, Fässer und Kisten, ein
    langer Steg mit festgemachten Booten und Laternen."""
    w, L, oben, a, b, insel = _basis(seed, g, pal="braun", hoch=2)
    for i, (fx, fz) in enumerate(((-0.45, -0.25), (-0.1, -0.3), (-0.35, 0.25))):
        cx, cz = round(fx * a), round(fz * b)
        y = flach(w, insel, cx, cz, 4)
        haeuschen(w, cx, y, cz, 3, 2, dach=("spruce", "dark_oak") if i % 2 else ("brick", "mud_brick"))
    cx, cz = round(0.15 * a), round(0.1 * b)
    y = flach(w, insel, cx, cz, 3)
    for yy in range(y + 1, y + 9):
        w.setze(cx, yy, cz, stamm(w, "spruce"))
    for k in range(6):
        w.setze(cx, y + 9, cz + k, stamm(w, "spruce", "z"))
    for yy in range(y + 5, y + 9):
        w.setze(cx, yy, cz + 5, w.b("chain", axis="y", waterlogged=False))
    w.setze(cx, y + 4, cz + 5, w.b("barrel", facing="up", open=False))
    kram(w, cx + 2, y + 1, cz - 2, 5)
    steg(w, round(0.0 * a), round(b * 0.85), _r(L * 0.3), breite=2)
    from boote import ruderboot
    for k in range(2):
        einfuegen(w, ruderboot(seed + k, 0), 4 + k * 6, 0, round(b * 0.85) + _r(L * 0.12) + k * 4)
    begruenen(w, insel, baeume=2, arten=("oak",))
    return w


def eis_schildkroete(seed, g=2):
    """Eis-Schildkröte: eine weiße Schildkröte mit Eispanzer trägt verschneite Fichten, ein Iglu, eine kleine
    Holzhütte mit rauchendem Kamin und Eisschollen ringsum."""
    w, L, oben, a, b, insel = _basis(seed, g, pal="eis", art="schnee", hoch=3)
    cx, cz = round(-0.2 * a), round(0.15 * b)
    y = flach(w, insel, cx, cz, 4)
    for x in range(-3, 4):
        for yy in range(0, 4):
            for z in range(-3, 4):
                d = math.sqrt(x * x + (yy * 1.2) ** 2 + z * z)
                if 2.3 < d <= 3.3:
                    w.setze(cx + x, y + 1 + yy, cz + z, w.b("snow_block" if (x + yy) % 3 else "packed_ice"))
    for yy in range(1, 3):
        w.bloecke.pop((cx, y + yy, cz + 3), None)
    cx2, cz2 = round(-0.45 * a), round(-0.25 * b)
    y2 = flach(w, insel, cx2, cz2, 4)
    top = haeuschen(w, cx2, y2, cz2, 2, 2, wand=Mix(w, [("spruce_planks", 3), ("stripped_spruce_log", 1)]),
                    dach=("spruce", "dark_oak"))
    rng = w.rng
    for k in range(3 + L // 16):
        (x, z), yy = list(insel.items())[int(rng.random() * len(insel))]
        if w.frei(x, yy + 1, z) and all(w.frei(x, yy + h, z) for h in (2, 5)):
            einfuegen(w, wald2.fichte(int(rng.integers(1, 10 ** 6)), schnee=True), x, yy, z)
    for k in range(8):
        ang = rng.random() * 6.283
        d = L * (0.6 + rng.random() * 0.2)
        x, z = round(math.cos(ang) * d), round(math.sin(ang) * d * 0.8)
        for dx in range(2):
            for dz in range(2):
                w.setze(x + dx, 0, z + dz, w.b("packed_ice"))
    return w


def oasen_schildkroete(seed, g=2):
    """Oasen-Schildkröte: eine sandfarbene Schildkröte trägt eine kleine Wüstenoase – ein türkiser Teich, Palmen, ein
    Beduinenzelt mit gestreiftem Tuch und Tonkrüge."""
    w, L, oben, a, b, insel = _basis(seed, g, pal="sand", art="sand", hoch=2)
    cx, cz = round(-0.2 * a), 0
    y = flach(w, insel, cx, cz, 5)
    for x in range(cx - 3, cx + 4):
        for z in range(cz - 2, cz + 3):
            if ((x - cx) / 3.3) ** 2 + ((z - cz) / 2.3) ** 2 < 1:
                w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, y - 1, z, w.b("light_blue_terracotta"))
    tx, tz = round(-0.45 * a), round(0.2 * b)
    yt = flach(w, insel, tx, tz, 4)
    for x in range(tx - 3, tx + 4):
        for z in range(tz - 2, tz + 3):
            hh = 3 - abs(z - tz)
            if hh >= 0:
                w.setze(x, yt + 1 + hh, z, w.b("red_wool" if x % 2 else "white_wool"))
    for (x, z) in ((tx - 3, tz), (tx + 3, tz)):
        for yy in range(yt + 1, yt + 4):
            w.setze(x, yy, z, zaun(w, "spruce"))
    begruenen(w, insel, dichte=0.1, baeume=3 + L // 20, arten=("palme",), blumen=False)
    for k in range(3):
        w.setze(cx + 4 + k, y + 1, cz + 3, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False))
    return w


def burg_schildkroete(seed, g=3):
    """Burg-Schildkröte: eine kleine Steinburg mit Ringmauer, vier Ecktürmen mit Kegeldächern und Bergfried auf dem
    Panzer einer steingrauen Schildkröte, Fahnen auf den Türmen."""
    w, L, oben, a, b, insel = _basis(seed, g, pal="stein", hoch=3)
    cx, cz = round(-0.22 * a), 0
    r = _r(L * 0.12)
    y = flach(w, insel, cx, cz, r + 3)
    st = Mix(w, [("stone_bricks", 3), ("cobblestone", 1), ("mossy_stone_bricks", 1), ("andesite", 1)])
    mauer(w, cx - r, cz - r, cx + r, cz + r, y + 1, y + 4, st)
    for x in range(cx - r, cx + r + 1, 2):
        for z in (cz - r, cz + r):
            w.setze(x, y + 5, z, st(x, y, z))
    dm = Dachmat(w, ["deepslate_tile", "cobbled_deepslate"])
    for (x, z) in ((cx - r, cz - r), (cx + r, cz - r), (cx - r, cz + r), (cx + r, cz + r)):
        for yy in range(y + 1, y + 8):
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    if abs(dx) == 1 or abs(dz) == 1:
                        w.setze(x + dx, yy, z + dz, st(x + dx, yy, z + dz))
        kegeldach(w, x, z, y + 8, 1.3, dm, form="kegel", h=5)
        w.setze(x + 1, y + 13, z, w.b("blue_wool"))
    mauer(w, cx - 2, cz - 2, cx + 2, cz + 2, y + 1, y + 11, st)
    kegeldach(w, cx, cz, y + 12, 2.3, dm, form="glocke", eckig=True, h=7)
    begruenen(w, insel, baeume=2, arten=("oak",))
    return w


def muehlen_schildkroete(seed, g=2):
    """Mühlen-Schildkröte: eine hölzerne Windmühle mit weißen Flügeln, kleine Felder mit Weizen und Kürbissen,
    ein Zaun und Heuballen auf dem Panzer."""
    w, L, oben, a, b, insel = _basis(seed, g, pal="braun", hoch=2)
    cx, cz = round(-0.3 * a), 0
    y = flach(w, insel, cx, cz, 4)
    for yy in range(y + 1, y + 11):
        r = 3 - (yy - y) * 0.12
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                d = math.hypot(dx, dz)
                if r - 1 < d <= r:
                    w.setze(cx + dx, yy, cz + dz, w.b("spruce_planks" if (yy % 3) else "stripped_spruce_log",
                                                      axis="y") if not (yy % 3) else w.b("spruce_planks"))
    kegeldach(w, cx, cz, y + 11, 2.0, Dachmat(w, ["spruce", "dark_oak"]), form="kegel", h=4)
    hx = cx + 3
    for k in range(-7, 8):
        w.setze(hx, y + 8 + k, cz, w.b("dark_oak_log", axis="y"))
        w.setze(hx, y + 8, cz + k, w.b("dark_oak_log", axis="z"))
        if abs(k) > 1:
            w.setze(hx, y + 8 + k, cz + (1 if k > 0 else -1), w.b("white_wool"))
            w.setze(hx, y + 8 + (-1 if k > 0 else 1), cz + k, w.b("white_wool"))
    fx, fz = round(0.1 * a), round(0.0 * b)
    yf = flach(w, insel, fx, fz, 5)
    for x in range(fx - 4, fx + 5):
        for z in range(fz - 4, fz + 5):
            if (x, z) in insel and insel[(x, z)] == yf:
                w.setze(x, yf, z, w.b("farmland", moisture=7) if z % 3 else w.b("water", level=0))
                if z % 3:
                    w.setze(x, yf + 1, z, w.b("wheat", age=7) if x % 4 else w.b("pumpkin"))
    begruenen(w, insel, baeume=1, arten=("oak",))
    return w


def kristall_schildkroete(seed, g=2):
    """Kristall-Schildkröte: aus dem dunklen Panzer wachsen riesige violette Amethystkristalle, Leuchtflechten und
    ein Kristallschrein."""
    from kristall import kristall
    w = _neu(seed)
    L = LG[g]
    oben, a, b = schildkroete(w, L, "stein")
    wasserflaeche(w, int(L * 0.85))
    rng = w.rng
    for k in range(5 + g * 2):
        (x, z), y = list(oben.items())[int(rng.random() * len(oben))]
        if (x / a) ** 2 + (z / b) ** 2 > 0.5:
            continue
        kristall(w, (x, y, z), ((rng.random() - 0.5) * 0.7, 1, (rng.random() - 0.5) * 0.7),
                 (3 + rng.random() * 5) * L / 36, (0.7 + rng.random() * 0.7) * L / 36, art="amethyst")
    return w


def schildkroetenfamilie(seed, g=2):
    """Schildkrötenfamilie: eine große Schildkröte mit Wiesenhügel und Baum, daneben schwimmen zwei kleine
    Schildkröten mit je einem winzigen Inselchen und einem Busch."""
    w = _neu(seed)
    L = LG[g]
    oben, a, b = schildkroete(w, L, "gruen")
    insel = aufsatz(w, oben, -0.18 * a, 0, a, b, hoch=3)
    begruenen(w, insel, baeume=2, arten=("oak", "birke"))
    for k, (dx, dz) in enumerate(((-0.6, 1.25), (-0.95, -1.15))):
        Lk = L * 0.35
        ok, ak, bk = schildkroete(w, Lk, "gruen", cx=round(dx * L), cz=round(dz * b))
        ik = aufsatz(w, ok, round(dx * L) - 0.18 * ak, round(dz * b), ak, bk, hoch=1)
        begruenen(w, ik, baeume=1, arten=("busch",))
    wasserflaeche(w, int(L * 1.3))
    return w


def garten_schildkroete(seed, g=2):
    """Garten-Schildkröte: ein bunter Blumengarten mit Glashaus, Rosenbögen, Gemüsebeeten und Vogeltränke auf dem
    Panzer einer grünen Schildkröte."""
    w, L, oben, a, b, insel = _basis(seed, g, pal="gruen", hoch=1)
    cx, cz = round(-0.25 * a), 0
    y = flach(w, insel, cx, cz, 4)
    for x in range(cx - 3, cx + 4):
        for z in range(cz - 2, cz + 3):
            rand = abs(x - cx) == 3 or abs(z - cz) == 2
            for yy in range(y + 1, y + 4):
                if rand:
                    w.setze(x, yy, z, w.b("glass") if (x + z) % 3 else stamm(w, "birch"))
            if not rand:
                w.setze(x, y + 1, z, w.b(["red_tulip", "allium", "pink_tulip", "cornflower"][(x + z) % 4]))
    for x in range(cx - 3, cx + 4):
        for z in range(cz - 2, cz + 3):
            w.setze(x, y + 4, z, w.b("glass"))
    rng = w.rng
    for (x, z), yy in insel.items():
        if rng.random() < 0.18 and w.frei(x, yy + 1, z) and w.frei(x, yy + 2, z):
            n = ["rose_bush", "peony", "lilac"][int(rng.random() * 3)]
            w.setze(x, yy + 1, z, w.b(n, half="lower"))
            w.setze(x, yy + 2, z, w.b(n, half="upper"))
    begruenen(w, insel, dichte=0.6, baeume=1, arten=("kirsche",))
    return w


def geisterschildkroete(seed, g=2):
    """Geister-Schildkröte: eine bleiche Schildkröte mit knochenweißem Panzer trägt eine zerfallene Kapelle,
    schiefe Grabsteine, tote Bäume und Seelenlaternen – nachts leuchtet sie türkis."""
    w, L, oben, a, b, insel = _basis(seed, g, pal="geist", art="asche", hoch=2)
    cx, cz = round(-0.25 * a), 0
    y = flach(w, insel, cx, cz, 4)
    st = Mix(w, [("stone_bricks", 2), ("cracked_stone_bricks", 2), ("mossy_stone_bricks", 1), ("cobblestone", 1)])
    mauer(w, cx - 3, cz - 2, cx + 3, cz + 2, y + 1, y + 5, st)
    rng = w.rng
    for (x, yy, z), bk in list(w.bloecke.items()):
        if abs(x - cx) <= 3 and abs(z - cz) <= 2 and yy > y + 2 and rng.random() < 0.35:
            del w.bloecke[(x, yy, z)]
    for k in range(6):
        (x, z), yy = list(insel.items())[int(rng.random() * len(insel))]
        if w.frei(x, yy + 1, z):
            w.setze(x, yy + 1, z, w.b("cobblestone_wall", up=True, north="none", south="none", east="none",
                                      west="none", waterlogged=False))
    for k in range(2):
        (x, z), yy = list(insel.items())[int(rng.random() * len(insel))]
        einfuegen(w, wald2.totholz(seed + k, "dark_oak"), x, yy, z)
    for k in range(5):
        (x, z), yy = list(insel.items())[int(rng.random() * len(insel))]
        w.setze(x, yy + 1, z, w.b("soul_lantern", hanging=False, waterlogged=False), False)
    return w


# ============================================================================ andere Meeresriesen

def walinsel(seed, g=3):
    """Walinsel: ein gewaltiger Wal treibt an der Oberfläche, auf seinem Rücken ein Fischerdorf mit drei Häusern,
    am Kopf schießt eine Wasserfontäne empor, die Schwanzflosse ragt aus dem Wasser."""
    w = _neu(seed)
    L = LG[g] * 1.3
    s = L / 50
    S = Skulptur(w, s)
    haut = Mix(w, [("gray_concrete", 3), ("light_gray_concrete", 1), ("gray_terracotta", 1)])
    S.mat("k", lambda x, y, z, *_: haut(x, y, z))
    S.mat("b", lambda x, y, z, *_: w.b("white_terracotta"))
    S.mat("a", lambda x, y, z, *_: w.b("black_concrete"))
    S.plus(ell(0, -1, 0, 25, 7, 9), "k")
    S.plus(ell(14, -3, 0, 10, 5, 7.5), "b")
    S.plus(kap((-20, -1, 0), (-32, 1, 0), 5, 2), "k")
    S.plus(ell(-34, 3, 0, 2.5, 4.5, 7), "k")
    S.plus(ell(17, 1.5, 6.5, 0.7, 0.7, 0.5), "a")
    S.plus(ell(17, 1.5, -6.5, 0.7, 0.7, 0.5), "a")
    for sz in (-1, 1):
        S.plus(kap((6, -3, sz * 8), (2, -4, sz * 15), 2.2, 0.8), "k")
    S.rendern((-38, -9, -18), (27, 9, 18), versatz=(0, 0, 0))
    wasserflaeche(w, int(L * 0.8))
    oben = {}
    for (x, y, z), bk in w.bloecke.items():
        if w.P.name(bk) != "minecraft:water" and y >= 0:
            oben[(x, z)] = max(oben.get((x, z), -9), y)
    a, b = 20 * s, 7 * s
    insel = aufsatz(w, oben, -3 * s, 0, 25 * s, 9 * s, rx=0.55, rz=0.6, hoch=1)
    for i, fx in enumerate((-0.35, 0.0, 0.3)):
        cx = round(fx * a)
        y = flach(w, insel, cx, 0, 3)
        haeuschen(w, cx, y, 0, 2, 2, dach=("spruce", "dark_oak") if i % 2 else ("brick", "mud_brick"))
    hx = round(13 * s)
    hy = oben.get((hx, 0), 5)
    for yy in range(hy + 1, hy + _r(10 * s)):
        w.setze(hx, yy, 0, w.b("water", level=0 if yy == hy + 1 else 8))
    begruenen(w, insel, baeume=1, arten=("oak",))
    return w


def krabbenhuette(seed, g=2):
    """Krabbenhütte: eine riesige rote Krabbe mit erhobenen Scheren trägt auf ihrem Panzer eine Fischerhütte mit
    Netzen, Laternen und einem Wimpel, ihre Beine stehen im flachen Wasser."""
    w = _neu(seed)
    s = LG[g] / 36
    S = Skulptur(w, s)
    rot = Mix(w, [("red_terracotta", 3), ("red_concrete", 1), ("orange_terracotta", 1)])
    S.mat("k", lambda x, y, z, *_: rot(x, y, z))
    S.mat("a", lambda x, y, z, *_: w.b("black_concrete"))
    S.mat("w", lambda x, y, z, *_: w.b("white_concrete"))
    S.plus(ell(0, 4, 0, 12, 4.5, 9), "k")
    for sz in (-1, 1):
        for k in range(4):
            x = -6 + k * 4
            S.plus(kap((x, 4, sz * 7), (x - 1, 7, sz * 13), 1.0), "k")
            S.plus(kap((x - 1, 7, sz * 13), (x - 2, -2, sz * 16), 0.9, 0.6), "k")
        S.plus(kap((9, 5, sz * 6), (15, 9, sz * 9), 1.5), "k")
        S.plus(ell(17, 11, sz * 10, 3.2, 2.2, 2.0), "k")
        S.plus(kap((18, 12, sz * 10), (22, 15, sz * 9), 1.0, 0.5), "k")
        S.plus(kap((10, 7, sz * 2.5), (12, 10, sz * 2.8), 0.4), "k")
        S.plus(ell(12.3, 10.6, sz * 2.8, 0.9, 0.9, 0.9), "w")
        S.plus(ell(12.9, 10.8, sz * 2.8, 0.45, 0.45, 0.45), "a")
    S.rendern((-18, -3, -20), (25, 17, 20))
    wasserflaeche(w, int(LG[g] * 0.9))
    ytop = max(y for (x, y, z) in w.bloecke if abs(x) < 3 and abs(z) < 3)
    for x in range(-4, 5):
        for z in range(-4, 5):
            w.setze(x, ytop, z, w.b("spruce_planks"))
    haeuschen(w, 0, ytop, 0, 3, 3, wand=Mix(w, [("spruce_planks", 3), ("stripped_spruce_log", 1)]),
              dach=("spruce", "dark_oak"))
    for x in (-4, 4):
        w.setze(x, ytop + 1, 5, w.b("cobweb"))
    return w


def schneckenhausdorf(seed, g=2):
    """Schneckenhaus-Dorf: eine riesige Schnecke kriecht durch das Flachwasser, ihr spiralförmiges Gehäuse ist zu
    einem Turmhaus mit Fenstern, Balkon und Schornstein ausgebaut, die Fühler tragen Laternen."""
    w = _neu(seed)
    s = LG[g] / 36
    wasserflaeche(w, int(LG[g] * 0.9), tiefe=1)
    S = Skulptur(w, s)
    haut = Mix(w, [("lime_terracotta", 2), ("green_terracotta", 1), ("moss_block", 1)])
    S.mat("k", lambda x, y, z, *_: haut(x, y, z))
    S.plus(kap((-14, 1, 0), (16, 2, 0), 4.5, 3.2), "k")
    S.plus(kap((15, 2, 1.5), (19, 9, 2.5), 0.6), "k")
    S.plus(kap((15, 2, -1.5), (19, 9, -2.5), 0.6), "k")
    S.rendern((-20, -2, -8), (22, 11, 8))
    gm = Mix(w, [("orange_terracotta", 2), ("brown_terracotta", 2), ("yellow_terracotta", 1),
                 ("white_terracotta", 1)], zelle=1.2)
    R0 = 11 * s
    for i in range(int(R0 * 30)):
        t = i / (R0 * 30)
        ang = t * 6.283 * 2.3
        r = R0 * (1 - t * 0.75)
        cx = -2 * s + math.cos(ang) * r * 0.9
        cy = 5 * s + R0 + math.sin(ang) * r
        rt = (4 * s) * (1 - t * 0.6) + 0.6
        for dx in range(-int(rt) - 1, int(rt) + 2):
            for dy in range(-int(rt) - 1, int(rt) + 2):
                for dz in range(-int(rt * 1.4) - 1, int(rt * 1.4) + 2):
                    if dx * dx + dy * dy + (dz / 1.4) ** 2 <= rt * rt:
                        w.setze(round(cx + dx), round(cy + dy), dz, gm(round(cx + dx), round(cy + dy), dz))
    cy = round(5 * s + R0)
    for z in (-round(5 * s), round(5 * s)):
        for (dx, dy) in ((-3, 0), (3, 2), (0, -3), (0, 4)):
            fenster(w, round(-2 * s) + dx, cy + dy, z, "south" if z > 0 else "north", holz="spruce", blumen=0.5)
    for k in range(int(4 * s)):
        w.setze(round(-2 * s), round(cy + R0 * 1.8) + k, 0, w.b("bricks"))
    w.setze(round(-2 * s), round(cy + R0 * 1.8) + int(4 * s), 0, w.b("campfire", lit=True, signal_fire=True,
                                                                     facing="north", waterlogged=False))
    for z in (2.5, -2.5):
        laterne(w, round(19 * s), round(9 * s), round(z * s), 1)
    return w


def fischinsel(seed, g=2):
    """Fischinsel: ein riesiger, schuppiger Fisch liegt halb aufgetaucht im Meer, auf seinem Rücken ein Leuchtturm
    und eine Hütte, Flossen und Schwanz ragen aus dem Wasser."""
    w = _neu(seed)
    s = LG[g] / 36
    S = Skulptur(w, s)
    sch = Mix(w, [("light_blue_terracotta", 2), ("cyan_terracotta", 2), ("prismarine", 1), ("white_terracotta", 1)],
              zelle=1.1)
    S.mat("k", lambda x, y, z, *_: sch(x, y, z))
    S.mat("a", lambda x, y, z, *_: w.b("black_concrete"))
    S.mat("f", lambda x, y, z, *_: w.b("orange_terracotta"))
    S.plus(ell(0, -1, 0, 18, 7, 6), "k")
    S.plus(kap((-16, 0, 0), (-24, 1, 0), 3, 1), "k")
    S.plus(ell(-27, 3, 0, 2, 6, 1.2), "f")
    S.plus(ell(-2, 6, 0, 7, 3, 0.8), "f")
    S.plus(ell(14, 1.5, 4.2, 1.2, 1.2, 1.0), "a")
    S.plus(ell(14, 1.5, -4.2, 1.2, 1.2, 1.0), "a")
    S.rendern((-30, -8, -9), (20, 10, 9))
    wasserflaeche(w, int(LG[g] * 0.95))
    top = {}
    for (x, y, z), bk in w.bloecke.items():
        if y >= 0 and w.P.name(bk) != "minecraft:water":
            top[(x, z)] = max(top.get((x, z), -9), y)
    hx = round(6 * s)
    leuchtturm(w, hx, top.get((hx, 0), 5), 0, H=_r(10 * s + 4), r=1)
    return w


def seeschlangenboegen(seed, g=3):
    """Seeschlangen-Bögen: eine riesige Seeschlange windet sich in drei Bögen aus dem Wasser, über die Bögen führt
    eine Hängebrücke zu einer kleinen Felsinsel mit Hütte, der Kopf mit Hörnern blickt herüber."""
    w = _neu(seed)
    s = LG[g] / 36
    wasserflaeche(w, int(LG[g] * 1.0))
    sch = Mix(w, [("dark_prismarine", 2), ("prismarine", 2), ("warped_wart_block", 1)])
    rt = 2.2 * s + 0.6
    pts = []
    for i in range(240):
        t = i / 239
        x = -LG[g] * 0.75 + t * LG[g] * 1.4
        y = abs(math.sin(t * math.pi * 3)) * 10 * s - 2
        pts.append((x, y))
    for (x, y) in pts:
        for dx in range(-int(rt) - 1, int(rt) + 2):
            for dy in range(-int(rt) - 1, int(rt) + 2):
                for dz in range(-int(rt) - 1, int(rt) + 2):
                    if dx * dx + dy * dy + dz * dz <= rt * rt:
                        yy = round(y + dy)
                        if yy >= -2:
                            w.setze(round(x + dx), yy, dz, sch(round(x + dx), yy, dz))
    hx = round(LG[g] * 0.65)
    S = Skulptur(w, s)
    S.mat("k", lambda x, y, z, *_: sch(x, y, z))
    S.mat("h", lambda x, y, z, *_: w.b("bone_block", axis="y"))
    S.mat("a", lambda x, y, z, *_: w.b("yellow_concrete"))
    S.plus(kap((0, 0, 0), (3, 8, 0), 2.2), "k")
    S.plus(ell(5, 9, 0, 4, 2.2, 2.4), "k")
    S.plus(kap((3, 10.5, 1.5), (0, 14, 2.5), 0.5, 0.2), "h")
    S.plus(kap((3, 10.5, -1.5), (0, 14, -2.5), 0.5, 0.2), "h")
    S.plus(ell(6.5, 10, 1.8, 0.6, 0.5, 0.4), "a")
    S.plus(ell(6.5, 10, -1.8, 0.6, 0.5, 0.4), "a")
    S.rendern((-3, -2, -5), (10, 16, 5), versatz=(hx, 0, 0))
    ix = -round(LG[g] * 0.85)
    for x in range(ix - 6, ix + 7):
        for z in range(-6, 7):
            if math.hypot(x - ix, z) <= 6:
                for y in range(-2, 3):
                    w.setze(x, y, z, w.b("grass_block", snowy=False) if y == 2 else w.b("stone"))
    haeuschen(w, ix, 2, 0, 2, 2)
    return w


def krakenfels(seed, g=3):
    """Kraken-Fels: ein riesiger Krake umklammert mit seinen Fangarmen eine Felsinsel mit Wachturm, die Arme ringeln
    sich aus dem Wasser über den Fels, die Saugnäpfe leuchten."""
    w = _neu(seed)
    s = LG[g] / 36
    wasserflaeche(w, int(LG[g] * 1.0))
    R = 8 * s + 3
    rs = Rauschen(w, 3)
    for x in range(-int(R) - 2, int(R) + 3):
        for z in range(-int(R) - 2, int(R) + 3):
            d = math.hypot(x, z) / R
            if d <= 1:
                h = int((1 - d ** 2) * 10 * s * (0.8 + 0.4 * rs(x, 0, z)))
                for y in range(-2, h + 1):
                    w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h and d < 0.6 else
                            w.b(["stone", "andesite", "mossy_cobblestone", "tuff"][(x + y + z) % 4]))
    h0 = int(10 * s * 0.9)
    st = Mix(w, [("stone_bricks", 3), ("mossy_stone_bricks", 1), ("cobblestone", 1)])
    mauer(w, -2, -2, 2, 2, h0 + 1, h0 + 1 + _r(8 * s + 3), st)
    kegeldach(w, 0, 0, h0 + 2 + _r(8 * s + 3), 2.3, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]), form="kegel",
              eckig=True, h=5)
    haut = Mix(w, [("purple_terracotta", 2), ("magenta_terracotta", 1), ("purple_concrete", 1)])
    for k in range(8):
        ang = k / 8 * 6.283
        r0 = R + 3
        for i in range(140):
            t = i / 139
            rr = r0 * (1 - 0.55 * t)
            a2 = ang + t * 2.2
            x = math.cos(a2) * rr
            z = math.sin(a2) * rr
            y = -1 + math.sin(t * math.pi) * (6 + 6 * s) * (0.7 + 0.3 * (k % 2))
            rt = (1.8 * s + 0.6) * (1 - 0.7 * t) + 0.3
            for dx in range(-int(rt) - 1, int(rt) + 2):
                for dy in range(-int(rt) - 1, int(rt) + 2):
                    for dz in range(-int(rt) - 1, int(rt) + 2):
                        if dx * dx + dy * dy + dz * dz <= rt * rt:
                            p = (round(x + dx), round(y + dy), round(z + dz))
                            if p[1] >= -2:
                                inner = dy < 0 and i % 6 == 0
                                w.setze(*p, w.b("pearlescent_froglight", axis="y") if inner else haut(*p))
    return w


def riesenmuschel(seed, g=2):
    """Riesenmuschel: eine gewaltige, halb geöffnete Muschel mit gerippten Schalen, in ihr thront eine Perle, auf
    der ein kleiner Kuppelpalast aus Quarz und Prismarin steht."""
    w = _neu(seed)
    s = LG[g] / 36
    wasserflaeche(w, int(LG[g] * 0.9))
    R = 13 * s + 3
    sch = Mix(w, [("pink_terracotta", 2), ("white_terracotta", 2), ("calcite", 1), ("magenta_terracotta", 1)],
              zelle=1.2)
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 1):
            d = math.hypot(x, z)
            if d > R or z > 0:
                continue
            ang = math.atan2(-z, x)
            rippe = int(ang / math.pi * 14) % 2 == 0
            h = (1 - (d / R) ** 2) * R * 0.25
            for k, (yb, top) in enumerate(((0, h), None)):
                pass
            y = round(h)
            w.setze(x, y, z, sch(x, y, z) if not rippe else w.b("pink_terracotta"))
            w.setze(x, y - 1, z, sch(x, y - 1, z))
            # obere Schale, gekippt
            yo = round(R * 0.35 + z * -0.75 + h * 0.6)
            w.setze(x, yo + R // 2, -z // 2 - round(R * 0.5), sch(x, yo, z) if not rippe else w.b("pink_terracotta"))
    pr = 3 * s + 1.5
    for x in range(-int(pr) - 1, int(pr) + 2):
        for y in range(-int(pr) - 1, int(pr) + 2):
            for z in range(-int(pr) - 1, int(pr) + 2):
                if x * x + y * y + z * z <= pr * pr:
                    w.setze(x, round(R * 0.25 + pr) + y, z - round(R * 0.4), w.b("white_concrete" if (x + y) % 3 else
                                                                                   "pearlescent_froglight",
                                                                                   **({} if (x + y) % 3 else
                                                                                      {"axis": "y"})))
    yp = round(R * 0.25 + 2 * pr) + 1
    zp = -round(R * 0.4)
    for x in range(-2, 3):
        for z in range(-2, 3):
            for yy in range(yp, yp + 3):
                if abs(x) == 2 or abs(z) == 2:
                    w.setze(x, yy, zp + z, w.b("quartz_pillar", axis="y") if (abs(x) == 2 and abs(z) == 2) else
                            w.b("glass"))
    for x in range(-3, 4):
        for yy in range(0, 3):
            for z in range(-3, 4):
                d = math.sqrt(x * x + (yy * 1.3) ** 2 + z * z)
                if 2.0 < d <= 3.0:
                    w.setze(x, yp + 3 + yy, zp + z, w.b("prismarine_bricks"))
    return w


def quallenkuppel(seed, g=2):
    """Quallenkuppel: eine riesige, durchscheinende Qualle schwebt über einer kleinen Insel und überwölbt sie wie
    eine Glaskuppel, ihre leuchtenden Tentakel hängen bis ins Wasser."""
    w = _neu(seed)
    s = LG[g] / 36
    wasserflaeche(w, int(LG[g] * 0.9))
    R = 6 * s + 2
    for x in range(-int(R), int(R) + 1):
        for z in range(-int(R), int(R) + 1):
            if math.hypot(x, z) <= R:
                for y in range(-2, 2):
                    w.setze(x, y, z, w.b("grass_block", snowy=False) if y == 1 else w.b("sand"))
    haeuschen(w, 0, 1, 0, 2, 2)
    begruenen(w, {(x, z): 1 for x in range(-int(R), int(R) + 1) for z in range(-int(R), int(R) + 1)
                  if math.hypot(x, z) <= R}, dichte=0.4)
    Rk = R + 5 * s + 3
    yk = 14 * s + 8
    for x in range(-int(Rk) - 1, int(Rk) + 2):
        for z in range(-int(Rk) - 1, int(Rk) + 2):
            for y in range(0, int(Rk * 0.7) + 2):
                d = math.sqrt(x * x + (y / 0.7) ** 2 + z * z)
                if Rk - 1.2 < d <= Rk:
                    w.setze(x, round(yk + y), z, w.b("magenta_stained_glass" if (x + z) % 4 else "pink_stained_glass"))
    rng = w.rng
    for k in range(int(30 * s)):
        ang = rng.random() * 6.283
        r = Rk * (0.5 + rng.random() * 0.5)
        x, z = round(math.cos(ang) * r), round(math.sin(ang) * r)
        for y in range(0, int(yk)):
            yy = round(yk) - y
            if (x, yy, z) in w.bloecke:
                break
            w.setze(x, yy, z, w.b("pearlescent_froglight", axis="y") if y % 5 == 0 else w.b("pink_stained_glass_pane",
                                                                                         north=False, south=False,
                                                                                         east=False, west=False,
                                                                                         waterlogged=False))
    return w


INSELN2 = {
    "leuchtturm_schildkroete": ("Leuchtturm-Schildkröte", leuchtturm_schildkroete),
    "schrein_schildkroete": ("Schrein-Schildkröte", schrein_schildkroete),
    "urwald_schildkroete": ("Urwald-Schildkröte", urwald_schildkroete),
    "hafen_schildkroete": ("Hafen-Schildkröte", hafen_schildkroete),
    "eis_schildkroete": ("Eis-Schildkröte", eis_schildkroete),
    "oasen_schildkroete": ("Oasen-Schildkröte", oasen_schildkroete),
    "burg_schildkroete": ("Burg-Schildkröte", burg_schildkroete),
    "muehlen_schildkroete": ("Mühlen-Schildkröte", muehlen_schildkroete),
    "kristall_schildkroete": ("Kristall-Schildkröte", kristall_schildkroete),
    "schildkroetenfamilie": ("Schildkrötenfamilie", schildkroetenfamilie),
    "garten_schildkroete": ("Garten-Schildkröte", garten_schildkroete),
    "geisterschildkroete": ("Geister-Schildkröte", geisterschildkroete),
    "walinsel": ("Walinsel", walinsel),
    "krabbenhuette": ("Krabbenhütte", krabbenhuette),
    "schneckenhausdorf": ("Schneckenhaus-Dorf", schneckenhausdorf),
    "fischinsel": ("Fischinsel", fischinsel),
    "seeschlangenboegen": ("Seeschlangen-Bögen", seeschlangenboegen),
    "krakenfels": ("Kraken-Fels", krakenfels),
    "riesenmuschel": ("Riesenmuschel mit Perlenpalast", riesenmuschel),
    "quallenkuppel": ("Quallenkuppel", quallenkuppel),
}

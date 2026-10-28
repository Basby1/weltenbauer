"""Gärten & Parks, Mühlen & Handwerk, Küste & Leuchttürme – drei Pakete."""

from __future__ import annotations

import math

import numpy as np

from bau import Stil, kamin, kasten_haus, satteldach, turm_rund, walmdach, zaun_rechteck
from lib import Verlauf, Welt, laub
from riesenbogen import zahnrad
from skulptur import Skulptur, ell, kap, kreisrand, platte, scheibe, treppe, verbinde, zur_mitte

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _gras(w, r, cx=0, cz=0):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, w.b("grass_block", snowy=False), ueberschreiben=False)


def _pf(w, mat):
    return w.b(mat, north=False, south=False, east=False, west=False, waterlogged=False)


def _baum(w, x, z, u, art="oak", h=None, r=2.5):
    h = h or _r(4 * u + 2, 3)
    for y in range(1, h + 1):
        w.setze(x, y, z, w.b(f"{art}_log", axis="y"))
    S = Skulptur(w, max(0.8, u))
    bl = [laub(w, art), laub(w, art), laub(w, "azalea")]
    S.mat("l", lambda *a: bl[int(w.rng.integers(3))])
    S.plus(ell(0, 0, 0, r, r * 0.8, r), "l")
    S.rendern((-4, -3, -4), (4, 3, 4), versatz=(x + 0.5, h + 1, z + 0.5), ueberschreiben=False)


def _hecke(w, x, z, h, art="oak"):
    for y in range(1, h + 1):
        w.setze(x, y, z, laub(w, art))


def _bank(w, x, z, facing="south", holz="spruce"):
    w.setze(x, 1, z, treppe(w, holz, facing))
    w.setze(x + 1, 1, z, treppe(w, holz, facing))


BLUMEN = ["poppy", "dandelion", "azure_bluet", "oxeye_daisy", "cornflower", "allium", "red_tulip", "pink_tulip",
          "lily_of_the_valley", "orange_tulip"]


# ============================================================================ Gärten & Parks

def heckenlabyrinth(seed, g=1):
    """Heckenlabyrinth mit garantiert lösbarem Weg, Pavillon in der Mitte und Laternen."""
    w = _welt(seed)
    u = U[g]
    n = [4, 6, 9, 13][g]
    zelle = 2
    R = n * zelle + 1
    _gras(w, R * 0.8 + 2)
    import random
    rnd = random.Random(seed)
    offen = set()
    besucht = {(0, 0)}
    stapel = [(0, 0)]
    while stapel:
        cx, cz = stapel[-1]
        nb = [(cx + dx, cz + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= cx + dx < n and 0 <= cz + dz < n and (cx + dx, cz + dz) not in besucht]
        if not nb:
            stapel.pop()
            continue
        nx, nz = rnd.choice(nb)
        offen.add(((cx, cz), (nx, nz)))
        offen.add(((nx, nz), (cx, cz)))
        besucht.add((nx, nz))
        stapel.append((nx, nz))
    h = 2 + (g >= 2)
    art = "oak" if _stil(seed) == 0 else "azalea"
    o = -R // 2
    for gx in range(n * zelle + 1):
        for gz in range(n * zelle + 1):
            x, z = o + gx, o + gz
            if gx % 2 == 0 and gz % 2 == 0:
                _hecke(w, x, z, h, art)
            elif gx % 2 == 0:
                a, b = (gx // 2 - 1, gz // 2), (gx // 2, gz // 2)
                if not (0 <= a[0] and b[0] < n and (a, b) in offen):
                    _hecke(w, x, z, h, art)
            elif gz % 2 == 0:
                a, b = (gx // 2, gz // 2 - 1), (gx // 2, gz // 2)
                if not (0 <= a[1] and b[1] < n and (a, b) in offen):
                    _hecke(w, x, z, h, art)
            else:
                w.setze(x, 0, z, w.b("gravel") if (x + z) % 3 else w.b("dirt_path"))
    for y in range(1, h + 1):
        w.bloecke.pop((o + 1, y, o), None)
        w.bloecke.pop((o + n * zelle - 1, y, o + n * zelle), None)
    m = o + (n // 2) * zelle + 1
    w.setze(m, 1, m, w.b("lantern", hanging=False, waterlogged=False))
    return w


def rosenpavillon(seed, g=1):
    """Achteckiger Pavillon mit Kuppeldach, Rosenbüschen ringsum, Bänken und Kiesweg."""
    w = _welt(seed)
    u = U[g]
    R = 3 * u + 2
    _gras(w, R + 6)
    holz = "birch" if _stil(seed) == 0 else "dark_oak"
    for x, z in scheibe(R + 0.5):
        w.setze(x, 0, z, w.b("smooth_stone") if (x + z) % 2 else w.b("polished_diorite"))
    H = _r(3 * u + 2, 3)
    for i, (x, z) in enumerate(kreisrand(R)):
        if i % 3 == 0:
            for y in range(1, H + 1):
                w.setze(x, y, z, _pf(w, f"{holz}_fence"))
    for x, z in kreisrand(R + 0.8):
        w.setze(x, H + 1, z, platte(w, holz))
    dach = "waxed_oxidized_copper" if _stil(seed) == 0 else "white_concrete"
    for kk in range(int(R) + 2):
        for x, z in kreisrand(max(0.3, R * (1 - (kk / (R + 1)) ** 2) ** 0.5)):
            w.setze(x, H + 2 + kk, z, w.b(dach))
    w.setze(0, H + int(R) + 3, 0, w.b("gold_block"))
    w.setze(0, H, 0, w.b("lantern", hanging=True, waterlogged=False))
    for i, (x, z) in enumerate(kreisrand(R + 2.5)):
        if i % 2 == 0:
            w.setze(x, 1, z, w.b("rose_bush", half="lower"))
            w.setze(x, 2, z, w.b("rose_bush", half="upper"))
    for z in range(int(R) + 1, int(R) + 7):
        w.setze(0, 0, z, w.b("gravel"))
        w.bloecke.pop((0, 1, z), None)
        w.bloecke.pop((0, 2, z), None)
    return w


def springbrunnen(seed, g=1):
    """Großer Springbrunnen mit drei Schalen übereinander, Becken und Wasser, das von oben herabfließt."""
    w = _welt(seed)
    u = U[g]
    R = 5 * u + 3
    stein = "smooth_quartz" if _stil(seed) == 0 else "polished_andesite"
    _gras(w, R + 4)
    for x, z in scheibe(R + 2):
        w.setze(x, 0, z, w.b("smooth_stone"))
    for x, z in scheibe(R):
        w.setze(x, 1, z, w.b("water", level=0))
    for x, z in kreisrand(R):
        w.setze(x, 1, z, w.b(stein))
        w.setze(x, 2, z, w.b(stein + ("_slab" if stein == "smooth_quartz" else "_slab"), type="bottom", waterlogged=False))
    y = 1
    for k, rr in enumerate((R * 0.55, R * 0.35, R * 0.18)):
        hs = _r(2 * u + 1, 2)
        for yy in range(y, y + hs):
            w.setze(0, yy, 0, w.b(stein))
        y += hs
        for x, z in scheibe(rr):
            w.setze(x, y, z, w.b(stein) if math.hypot(x, z) > rr - 1 else w.b("water", level=0))
        y += 1
    w.setze(0, y, 0, w.b("water", level=0))
    return w


def barockgarten(seed, g=2):
    """Barockgarten: symmetrische Beete mit niedrigen Hecken, Kieswege, Kegelbäumchen, Statuen auf Sockeln
    und ein Wasserbecken in der Mitte."""
    w = _welt(seed)
    u = U[g]
    L = _r(12 * u + 6, 8)
    _gras(w, L * 1.45 * 0.85)
    for x in range(-L, L + 1):
        for z in range(-L, L + 1):
            if abs(x) <= 1 or abs(z) <= 1 or max(abs(x), abs(z)) == L:
                w.setze(x, 0, z, w.b("gravel"))
            elif (abs(x) + abs(z)) % 6 == 0 or max(abs(x), abs(z)) == L - 1:
                w.setze(x, 1, z, laub(w, "oak"))
            elif (x * z) % 5 == 0:
                w.setze(x, 1, z, w.b(BLUMEN[(abs(x) + abs(z)) % len(BLUMEN)]))
    for x, z in scheibe(2.5 * u + 1):
        w.setze(x, 0, z, w.b("water", level=0))
    for x, z in kreisrand(2.5 * u + 1.8):
        w.setze(x, 0, z, w.b("smooth_quartz"))
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * (L // 2), sz * (L // 2)
            for y in range(1, 4):
                w.setze(x, y, z, laub(w, "spruce") if y < 3 else laub(w, "spruce"))
            w.setze(x, 4, z, laub(w, "spruce"))
            x2, z2 = sx * (L - 3), sz * 3
            w.setze(x2, 1, z2, w.b("polished_diorite"))
            w.setze(x2, 2, z2, w.b("quartz_pillar", axis="y"))
            w.setze(x2, 3, z2, w.b("player_head" if False else "smooth_quartz"))
    return w


def teichpark(seed, g=2):
    """Teichpark: geschwungener Teich mit Insel, Holzbrücke, Trauerweiden, Bänken und Laternen."""
    w = _welt(seed)
    u = U[g]
    R = 10 * u + 5
    _gras(w, R + 4)
    for x in range(-int(R), int(R) + 1):
        for z in range(-int(R), int(R) + 1):
            d = math.hypot(x / 1.3, z) / (R * 0.75) + 0.12 * math.sin(math.atan2(z, x) * 3)
            if d < 1:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("dirt"))
                if w.rng.random() < 0.05:
                    w.setze(x, 1, z, w.b("lily_pad"))
    for x, z in scheibe(2 * u + 1, int(R * 0.2), 0):
        w.setze(x, 0, z, w.b("grass_block", snowy=False))
    _baum(w, int(R * 0.2), 0, u * 0.7, "oak")
    for x in range(int(R * 0.2) + 2, int(R) + 1):
        w.setze(x, 1, 0, w.b("spruce_planks"))
        w.setze(x, 2, -1, _pf(w, "spruce_fence"))
        w.setze(x, 2, 1, _pf(w, "spruce_fence"))
    for a in (2.0, 3.6, 5.0):
        x, z = round(math.cos(a) * R * 0.95), round(math.sin(a) * R * 0.95)
        _baum(w, x, z, u, "oak", r=3)
        for kk in range(2, _r(4 * u, 3)):
            for dx, dz in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                w.setze(x + dx * 1, _r(4 * u + 2, 3) + 1 - kk, z + dz * 1, laub(w, "oak"), ueberschreiben=False)
    for a in (0.8, 4.2):
        x, z = round(math.cos(a) * R * 0.95), round(math.sin(a) * R * 0.95)
        _bank(w, x, z)
        w.setze(x - 1, 1, z, w.b("lantern", hanging=False, waterlogged=False))
    return w


def rosenallee(seed, g=1):
    """Allee aus Rosenbögen über einem Kiesweg, mit Blumenrabatten und Bänken."""
    w = _welt(seed)
    u = U[g]
    n = [3, 5, 8, 12][g]
    L = n * 3
    _gras(w, L // 2 + 4)
    for z in range(-L // 2 - 1, L // 2 + 2):
        for x in (-1, 0, 1):
            w.setze(x, 0, z, w.b("gravel"))
        for x in (-3, -2, 2, 3):
            w.setze(x, 1, z, w.b(BLUMEN[(z + x) % len(BLUMEN)]))
    for i in range(n):
        z = -L // 2 + i * 3
        for s in (-1, 1):
            for y in range(1, 4):
                w.setze(s * 2, y, z, _pf(w, "dark_oak_fence") if y < 3 else laub(w, "flowering_azalea"))
        for x in range(-2, 3):
            w.setze(x, 4, z, laub(w, "flowering_azalea") if abs(x) < 2 else laub(w, "azalea"))
    for s in (-1, 1):
        _bank(w, s * 4, 0, "east" if s < 0 else "west")
    return w


def gewaechshaus(seed, g=2):
    """Orangerie/Gewächshaus aus Glas und weißen Streben mit Kuppel, Palmen und Beeten innen."""
    w = _welt(seed)
    u = U[g]
    bx, bz = _r(7 * u + 3, 5), _r(4 * u + 2, 3)
    H = _r(4 * u + 2, 4)
    _gras(w, bx + 4)
    rahmen = w.b("white_concrete") if _stil(seed) == 0 else w.b("waxed_oxidized_cut_copper")
    for y in range(0, H + 1):
        for x in range(-bx, bx + 1):
            for z in range(-bz, bz + 1):
                rand = x in (-bx, bx) or z in (-bz, bz)
                if y == 0:
                    w.setze(x, 0, z, w.b("smooth_stone") if rand else w.b("grass_block", snowy=False))
                elif rand:
                    w.setze(x, y, z, rahmen if (x % 3 == 0 or z % 3 == 0 or y == H) else w.b("glass"))
    for kk in range(bz + 1):
        for x in range(-bx, bx + 1):
            for s in (-1, 1):
                w.setze(x, H + 1 + kk, s * (bz - kk), rahmen if x % 3 == 0 else w.b("glass"))
    for x in range(-bx + 2, bx - 1, 4):
        _baum(w, x, 0, u * 0.6, "jungle", h=_r(3 * u, 2), r=1.6)
    for x in range(-bx + 1, bx):
        for z in (-bz + 1, bz - 1):
            w.setze(x, 1, z, w.b(BLUMEN[(x * 7) % len(BLUMEN)]))
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(0, y, bz, w.b("birch_door", facing="south", half=half, hinge="left", open=False, powered=False))
    return w


PARKS = {
    "heckenlabyrinth": ("Heckenlabyrinth", heckenlabyrinth),
    "rosenpavillon": ("Rosenpavillon", rosenpavillon),
    "springbrunnen": ("Springbrunnen", springbrunnen),
    "barockgarten": ("Barockgarten", barockgarten),
    "teichpark": ("Teichpark", teichpark),
    "rosenallee": ("Rosenallee", rosenallee),
    "gewaechshaus": ("Gewächshaus", gewaechshaus),
}


# ============================================================================ Mühlen & Handwerk

def windmuehle(seed, g=2):
    """Turmwindmühle mit Steinsockel, Holzkappe, vier großen Flügeln mit Segeltuch und Galerie."""
    w = _welt(seed)
    u = U[g]
    R = 3 * u + 2
    H = _r(10 * u + 4, 7)
    _gras(w, R + 8)
    st = Stil(w, Verlauf(w, "Mühle", ["cobblestone", "stone_bricks", "white_terracotta", "calcite"]
                         if _stil(seed) == 0 else ["bricks", "red_terracotta", "white_terracotta"]),
              holz="spruce", dach="dark_oak", dach_voll="dark_oak_planks")
    for y in range(0, H):
        r = R * (1 - 0.18 * y / H)
        for i, (x, z) in enumerate(kreisrand(r)):
            fen = y % 5 == 3 and i % 5 == 0
            w.setze(x, y, z, w.b("glass_pane", north=False, south=False, east=True, west=True, waterlogged=False)
                    if fen else st.wandblock(x, y, z, 0.5 + 2.5 * y / H))
    yg = int(H * 0.45)
    for x, z in kreisrand(R + 1.5):
        w.setze(x, yg, z, w.b("spruce_planks"))
    verbinde(w, [(x, yg + 1, z) for x, z in kreisrand(R + 1.5)], "spruce_fence")
    for kk in range(_r(R * 1.2, 3)):
        for x, z in kreisrand(max(0.3, R * 0.85 * (1 - kk / (R * 1.2)))):
            w.setze(x, H + kk, z, w.b("dark_oak_planks"))
    zh = int(R) + 1
    cy = H + 1
    w.setze(0, cy, zh, w.b("spruce_log", axis="z"))
    w.setze(0, cy, zh + 1, w.b("spruce_log", axis="z"))
    L = _r(9 * u + 4, 6)
    for i in range(4):
        a = i * math.pi / 2 + 0.35
        for t in range(1, L + 1):
            x, y = round(math.cos(a) * t), round(cy + math.sin(a) * t)
            w.setze(x, y, zh + 1, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                      waterlogged=False) if t < 2 else w.b("stripped_spruce_log", axis="y"))
            if t > 2:
                bx, by = round(math.cos(a + 0.18) * t), round(cy + math.sin(a + 0.18) * t)
                bx2, by2 = round(math.cos(a + 0.33) * t), round(cy + math.sin(a + 0.33) * t)
                w.setze(bx, by, zh + 1, w.b("white_wool"), ueberschreiben=False)
                w.setze(bx2, by2, zh + 1, w.b("white_wool"), ueberschreiben=False)
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(0, y, -int(R), w.b("spruce_door", facing="north", half=half, hinge="left", open=False, powered=False))
    return w


def wassermuehle(seed, g=2):
    """Wassermühle: Fachwerkhaus am Bach mit großem Wasserrad, Mühlgraben-Holzrinne und Säcken."""
    w = _welt(seed)
    u = U[g]
    st = Stil(w, Verlauf(w, "Putz", ["white_terracotta", "calcite"]) if _stil(seed) == 0 else
              Verlauf(w, "Stein", ["cobblestone", "mossy_cobblestone", "stone_bricks"]), holz="dark_oak",
              dach="spruce", sockel="cobblestone", fachwerk=_stil(seed) == 0)
    bx, bz = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    _gras(w, bx + 10)
    for x in range(-bx - 10, bx + 11):
        for z in range(bz + 1, bz + 5):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("dirt"))
    yt, a, b, c, d = kasten_haus(w, st, -bx, -bz, bx, bz, 0, 1 + (g >= 2), eh=4)
    satteldach(w, st, a, b, c, d, yt)
    R = _r(3.5 * u + 1.5, 3)
    zw = bz + 2
    zahnrad(w, 0, R - 1, zw, R, ebene="xy", material="spruce_planks", nabe="stripped_spruce_log")
    zahnrad(w, 0, R - 1, zw + 1, R, ebene="xy", material="spruce_planks", nabe="stripped_spruce_log")
    for z in range(zw - 1, zw + 3):
        w.setze(0, R - 1, z, w.b("stripped_spruce_log", axis="z"))
    for x in range(-bx - 6, -1):
        w.setze(x, 2 * R, zw, w.b("spruce_planks"))
        w.setze(x, 2 * R + 1, zw, w.b("water", level=0))
        w.setze(x, 2 * R + 1, zw - 1, w.b("spruce_planks"))
        w.setze(x, 2 * R + 1, zw + 1, w.b("spruce_planks"))
        if x % 3 == 0:
            for y in range(0, 2 * R):
                w.setze(x, y, zw, _pf(w, "spruce_fence"))
    for k in range(3):
        w.setze(bx + 1, 1, -1 + k, w.b("white_wool"))
    return w


def schmiede(seed, g=1):
    """Dorfschmiede: offene Werkstatt mit Esse und Kamin, Amboss, Schleifstein, Werkzeugwand und Pferdetränke."""
    w = _welt(seed)
    u = U[g]
    st = Stil(w, Verlauf(w, "Stein", ["cobblestone", "stone_bricks", "andesite"]), holz="spruce", dach="spruce",
              sockel="cobblestone", fachwerk=False)
    bx, bz = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    _gras(w, bx + 6)
    yt, a, b, c, d = kasten_haus(w, st, -bx, -bz, bx, bz, 0, 1, eh=4, tuer_seite="east", blumen=False)
    for x in range(-bx + 1, bx):
        for y in range(1, 4):
            w.bloecke.pop((x, y, bz), None)
    satteldach(w, st, a, b, c, d, yt)
    for y in range(1, yt + 5):
        w.setze(-bx + 1, y, -bz + 1, w.b("bricks"))
    w.setze(-bx + 1, yt + 5, -bz + 1, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    w.setze(-bx + 2, 1, -bz + 1, w.b("blast_furnace", facing="south", lit=True))
    w.setze(-bx + 2, 1, -bz + 2, w.b("lava", level=0))
    w.setze(0, 1, 0, w.b("anvil", facing="north"))
    w.setze(2, 1, 0, w.b("grindstone", face="floor", facing="north"))
    w.setze(bx - 1, 1, -bz + 1, w.b("smithing_table"))
    for x in range(bx + 2, bx + 5):
        w.setze(x, 0, bz - 1, w.b("water", level=0))
        w.setze(x, 1, bz - 2, w.b("spruce_slab", type="bottom", waterlogged=False))
    return w


def saegewerk(seed, g=2):
    """Sägewerk: offene Halle mit Sägeblatt (Zahnrad), Baumstammstapel, Bretterstapeln und Kran."""
    w = _welt(seed)
    u = U[g]
    bx, bz = _r(6 * u + 3, 4), _r(3 * u + 2, 3)
    H = _r(4 * u + 2, 4)
    _gras(w, bx + 6)
    for x in range(-bx, bx + 1):
        for z in range(-bz, bz + 1):
            w.setze(x, 0, z, w.b("spruce_planks"))
    for x in range(-bx, bx + 1, 3):
        for z in (-bz, bz):
            for y in range(1, H + 1):
                w.setze(x, y, z, w.b("spruce_log", axis="y"))
    for kk in range(bz + 2):
        for x in range(-bx - 1, bx + 2):
            for s in (-1, 1):
                w.setze(x, H + 1 + kk, s * (bz + 1 - kk), treppe(w, "spruce", "south" if s < 0 else "north")
                        if kk <= bz else w.b("spruce_planks"))
    zahnrad(w, 0, 2, 0, _r(1.6 * u, 2), ebene="xy", material="iron_block", nabe="polished_andesite")
    for x in range(-bx + 1, bx):
        w.setze(x, 1, 0, w.b("stripped_oak_log", axis="x") if x != 0 else w.b("iron_block"))
    for k in range(3):
        for y in range(1, 3 - k % 2):
            for z in range(bz + 2, bz + 5):
                w.setze(-bx + k, y, z, w.b("oak_log", axis="z"))
        for y in range(1, 3):
            w.setze(bx - k, y, bz + 3, w.b("oak_planks"))
    return w


def brauerei(seed, g=1):
    """Brauerei: Ziegelhaus mit Sudkesseln aus Kupfer, Fassstapeln, Hopfengarten und Wirtshausschild."""
    w = _welt(seed)
    u = U[g]
    st = Stil(w, Verlauf(w, "Ziegel", ["bricks", "red_terracotta", "bricks"]), holz="dark_oak", dach="deepslate_tile",
              dach_voll="deepslate_tiles", sockel="stone_bricks", fachwerk=False)
    bx, bz = _r(5 * u + 2, 4), _r(3 * u + 2, 3)
    _gras(w, bx + 7)
    yt, a, b, c, d = kasten_haus(w, st, -bx, -bz, bx, bz, 0, 1 + (g >= 2), eh=4)
    satteldach(w, st, a, b, c, d, yt)
    kamin(w, c - 1, b + 1, yt, yt + _r(4 * u, 3), "bricks")
    for s in (-1, 1):
        cx = s * (bx + 3)
        for y in range(1, 4):
            for x, z in kreisrand(1.4, cx, 0):
                w.setze(x, y, z, w.b("waxed_copper_block") if y < 3 else w.b("waxed_cut_copper"))
        w.setze(cx, 4, 0, w.b("waxed_cut_copper"))
    for k in range(4):
        for y in range(1, 2 + (k % 2)):
            w.setze(-2 + k, y, bz + 2, w.b("barrel", facing="east", open=False))
    for x in range(-bx, bx + 1, 2):
        for y in range(1, 4):
            w.setze(x, y, -bz - 3, _pf(w, "spruce_fence") if y < 3 else laub(w, "jungle"))
    return w


def kohlenmeiler(seed, g=1):
    """Rauchender Kohlenmeiler: mit Erde abgedeckter Holzhaufen, Glutstellen, Holzstapel und Köhlerhütte."""
    w = _welt(seed)
    u = U[g]
    R = 3.5 * u + 2
    _gras(w, R + 7)
    for y in range(0, int(R) + 1):
        for x, z in scheibe(R * math.sqrt(max(0, 1 - (y / (R + 0.5)) ** 2))):
            w.setze(x, y + 1, z, w.b("coarse_dirt") if (x + y + z) % 5 else w.b("magma_block"))
    for k in range(3):
        a = k * 2.1
        x, z = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        top = max([p[1] for p in w.bloecke if p[0] == x and p[2] == z] or [1])
        w.setze(x, top + 1, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    for k in range(4):
        for y in range(1, 3):
            w.setze(int(R) + 3 + k, y, 0, w.b("oak_log", axis="z"))
    hx = -int(R) - 5
    for kk in range(3):
        for z in range(-2 + kk, 3 - kk):
            w.setze(hx, 1 + kk, z, w.b("spruce_planks"))
            w.setze(hx - 1, 1 + kk, z, w.b("spruce_planks"))
    return w


HANDWERK = {
    "windmuehle": ("Windmühle", windmuehle),
    "wassermuehle": ("Wassermühle", wassermuehle),
    "schmiede": ("Dorfschmiede", schmiede),
    "saegewerk": ("Sägewerk", saegewerk),
    "brauerei": ("Brauerei", brauerei),
    "kohlenmeiler": ("Kohlenmeiler", kohlenmeiler),
}


# ============================================================================ Küste & Leuchttürme

def leuchtturm(seed, g=2):
    """Rot-weiß gestreifter Leuchtturm mit Galerie, Laternenhaus, Kuppel und Wärterhaus auf Felsen."""
    w = _welt(seed)
    u = U[g]
    R = 2.6 * u + 1.6
    H = _r(18 * u + 6, 10)
    s1, s2 = ("red_concrete", "white_concrete") if _stil(seed) == 0 else ("black_concrete", "white_concrete")
    fels = Verlauf(w, "Fels", ["stone", "andesite", "cobblestone", "mossy_cobblestone"])
    for x, z in scheibe(R + 5):
        for y in range(0, int(2 * u) + 1):
            if math.hypot(x, z) < R + 5 - y:
                w.setze(x, y, z, fels(0.5 + w.rng.random() * 2, x, y, z))
    y0 = int(2 * u) + 1
    band = _r(3 * u, 2)
    for y in range(y0, y0 + H):
        r = R * (1 - 0.25 * (y - y0) / H)
        for i, (x, z) in enumerate(kreisrand(r)):
            fen = (y - y0) % 6 == 3 and i % 7 == 0
            w.setze(x, y, z, w.b("glass_pane", north=False, south=False, east=True, west=True, waterlogged=False)
                    if fen else w.b(s1 if ((y - y0) // band) % 2 == 0 else s2))
    yt = y0 + H
    rt = R * 0.75
    for x, z in scheibe(rt + 1.5):
        w.setze(x, yt, z, w.b("smooth_stone"))
    verbinde(w, [(x, yt + 1, z) for x, z in kreisrand(rt + 1.5)], "iron_bars")
    for y in range(yt + 1, yt + 4):
        for x, z in kreisrand(rt):
            w.setze(x, y, z, w.b("glass") if y < yt + 3 else w.b("iron_block"))
    w.setze(0, yt + 1, 0, w.b("redstone_lamp", lit=True) if False else w.b("sea_lantern"))
    w.setze(0, yt + 2, 0, w.b("glowstone"))
    for kk in range(_r(rt + 1, 2)):
        for x, z in kreisrand(max(0.3, rt - kk)):
            w.setze(x, yt + 4 + kk, z, w.b(s1))
    w.setze(0, yt + 5 + _r(rt + 1, 2), 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    st = Stil(w, Verlauf(w, "Weiß", ["white_concrete", "calcite"]), holz="spruce", dach="deepslate_tile" if _stil(seed) else "brick",
              dach_voll="deepslate_tiles" if _stil(seed) else "bricks", sockel="stone_bricks", fachwerk=False)
    yt2, a, b, c, d = kasten_haus(w, st, int(R) + 1, -2, int(R) + 6, 2, y0 - 1, 1, eh=3, blumen=False)
    satteldach(w, st, a, b, c, d, yt2)
    return w


def hafenkran(seed, g=2):
    """Hölzerner Tretradkran am Kai: Kranhaus mit Ausleger, Laufrad, Seil und Lastkiste."""
    w = _welt(seed)
    u = U[g]
    h = _r(2.5 * u + 1.5, 2)
    H = _r(6 * u + 3, 5)
    for x in range(-h - 3, h + 4):
        for z in range(-h - 3, h + 10):
            w.setze(x, 0, z, w.b("water", level=0) if z > h + 2 else w.b("stone_bricks"))
            if z > h + 2:
                w.setze(x, -1, z, w.b("sand"))
    for y in range(1, H + 1):
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                if max(abs(x), abs(z)) == h:
                    w.setze(x, y, z, w.b("stripped_spruce_log", axis="y") if abs(x) == abs(z) else w.b("spruce_planks"))
    for kk in range(h + 2):
        for x in range(-h - 1 + kk, h + 2 - kk):
            for z in range(-h - 1 + kk, h + 2 - kk):
                if max(abs(x), abs(z)) == h + 1 - kk:
                    w.setze(x, H + 1 + kk, z, w.b("dark_oak_planks"))
    L = _r(7 * u + 3, 5)
    for k in range(L + 1):
        w.setze(0, H - k // 3, h + k, w.b("spruce_log", axis="z"))
    ze = h + L
    ye = H - L // 3
    for y in range(2, ye):
        w.setze(0, y, ze, w.b("chain", axis="y", waterlogged=False))
    w.setze(0, 1, ze, w.b("barrel", facing="up", open=False))
    zahnrad(w, h + 1, H // 2 + 1, 0, _r(2 * u + 1, 2), ebene="zy", material="spruce_planks", nabe="stripped_spruce_log")
    return w


def kai(seed, g=1):
    """Kaimauer mit Holzsteg, Pollern, Laternen, Kisten, Fässern und Ankern."""
    w = _welt(seed)
    u = U[g]
    L = _r(12 * u + 6, 8)
    for x in range(-L, L + 1):
        for z in range(-4, 12):
            if z <= 0:
                w.setze(x, 0, z, w.b("stone_bricks") if (x + z) % 4 else w.b("cobblestone"))
            else:
                w.setze(x, -1, z, w.b("sand"))
                w.setze(x, 0, z, w.b("water", level=0))
    for z in range(1, 10):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
        if z % 3 == 0:
            for x in (-2, 2):
                for y in (-1, 0, 1):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
                w.setze(x, 2, z, w.b("lantern", hanging=False, waterlogged=False))
    for x in range(-L + 2, L - 1, 4):
        w.setze(x, 1, 0, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                             waterlogged=False))
        w.setze(x, 2, 0, w.b("chain", axis="x", waterlogged=False)) if False else None
    for k in range(5):
        x = -L + 2 + k * 2
        w.setze(x, 1, -2, w.b("barrel", facing="up", open=False) if k % 2 else w.b("oak_planks"))
    w.setze(L - 2, 1, -2, w.b("anvil", facing="east"))
    return w


def fischerhuetten(seed, g=2):
    """Fischerhütten auf Stelzen am Ufer mit Netzen, Bootsstegen und Räucherhütte."""
    w = _welt(seed)
    u = U[g]
    n = [1, 2, 3, 5][g]
    L = n * 7
    for x in range(-L // 2 - 3, L // 2 + 4):
        for z in range(-6, 10):
            if z < 0:
                w.setze(x, 0, z, w.b("sand"))
            else:
                w.setze(x, -1, z, w.b("sand"))
                w.setze(x, 0, z, w.b("water", level=0))
    for i in range(n):
        x0 = -L // 2 + i * 7
        for x in (x0, x0 + 4):
            for z in (1, 5):
                for y in range(-1, 2):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
        for x in range(x0 - 1, x0 + 6):
            for z in range(0, 7):
                w.setze(x, 2, z, w.b("spruce_planks"))
        for y in range(3, 6):
            for x in range(x0, x0 + 5):
                for z in (1, 5):
                    w.setze(x, y, z, w.b("spruce_planks") if (x + y) % 4 else w.b("stripped_spruce_log", axis="y"))
            for z in range(1, 6):
                for x in (x0, x0 + 4):
                    w.setze(x, y, z, w.b("spruce_planks") if not (z == 3 and y == 4) else
                            w.b("glass_pane", north=True, south=True, east=False, west=False, waterlogged=False))
        for kk in range(4):
            for x in range(x0 - 1, x0 + 6):
                w.setze(x, 6 + kk, 1 + kk, treppe(w, "spruce", "south"))
                w.setze(x, 6 + kk, 5 - kk, treppe(w, "spruce", "north")) if 5 - kk > 1 + kk else \
                    w.setze(x, 6 + kk, 3, w.b("spruce_planks"))
        w.setze(x0 + 2, 3, 1, w.b("spruce_door", facing="north", half="lower", hinge="left", open=False, powered=False))
        w.setze(x0 + 2, 4, 1, w.b("spruce_door", facing="north", half="upper", hinge="left", open=False, powered=False))
        for y in range(3, 5):
            w.setze(x0 + 5, y, 4, w.b("cobweb"))
        for z in range(7, 10):
            w.setze(x0 + 2, 1, z, w.b("spruce_slab", type="top", waterlogged=True))
    return w


def klippenleuchtturm(seed, g=2):
    """Achteckiger Steinleuchtturm auf einer hohen Klippe mit Treppe in den Fels."""
    w = _welt(seed)
    u = U[g]
    Hk = _r(10 * u + 4, 6)
    R = 7 * u + 4
    fels = Verlauf(w, "Klippe", ["stone", "andesite", "tuff", "grass_block"])
    for x in range(-int(R) - 2, int(R) + 3):
        for z in range(-int(R) - 2, int(R) + 3):
            a = math.atan2(z, x)
            d = math.hypot(x, z)
            rr = R * (1 + 0.12 * math.sin(4 * a))
            if d <= rr:
                h = int(Hk * min(1, (rr - d) / 3 + 0.4))
                for y in range(0, h + 1):
                    w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h and h >= Hk - 1 else
                            fels(0.3 + 2 * y / Hk + w.rng.random() * 0.6, x, y, z))
    st = Stil(w, Verlauf(w, "Stein", ["stone_bricks", "polished_andesite", "calcite"]), holz="spruce",
              dach="deepslate_tile", dach_voll="deepslate_tiles")
    Ht = _r(10 * u + 4, 6)
    top = turm_rund(w, st, 0, 0, Hk + 1, 2 * u + 1.4, Ht, dach_hoehe=_r(2 * u + 2, 2))
    yl = Hk + 1 + Ht
    for x, z in kreisrand(2 * u + 2.4):
        w.setze(x, yl - 1, z, w.b("smooth_stone"))
    w.setze(0, yl - 2, 0, w.b("sea_lantern"))
    for k in range(Hk):
        for t in range(2):
            w.setze(int(R) - 1 - k // 2, k + 1, int(R * 0.4) + t, treppe(w, "stone_brick", "west"))
    return w


def bootshaus(seed, g=1):
    """Bootshaus über dem Wasser mit offener Bootseinfahrt, Ruderboot darin und Steg."""
    w = _welt(seed)
    u = U[g]
    bx, bz = _r(3 * u + 2, 3), _r(5 * u + 3, 4)
    for x in range(-bx - 4, bx + 5):
        for z in range(-bz - 4, bz + 6):
            if z < -bz:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
            else:
                w.setze(x, -1, z, w.b("sand"))
                w.setze(x, 0, z, w.b("water", level=0))
    st = Stil(w, Verlauf(w, "Holz", ["spruce_planks", "stripped_spruce_log"]) if _stil(seed) == 0 else
              Verlauf(w, "Rot", ["red_terracotta", "red_concrete"]), holz="spruce", dach="spruce",
              sockel="spruce_planks", fachwerk=False)
    yt, a, b, c, d = kasten_haus(w, st, -bx, -bz, bx, bz, 0, 1, eh=_r(3 * u + 2, 3), tuer_seite="north", blumen=False)
    for x in range(-bx + 1, bx):
        for y in range(0, _r(3 * u + 2, 3)):
            w.bloecke.pop((x, y, bz), None)
        for z in range(-bz + 1, bz):
            if abs(x) < bx - 1:
                w.setze(x, 0, z, w.b("water", level=0))
    satteldach(w, st, a, b, c, d, yt, first_x=False)
    for z in range(-bz + 2, bz - 1):
        w.setze(0, 0, z, w.b("oak_planks") if abs(z) < bz - 3 else w.b("oak_slab", type="top", waterlogged=True))
    for z in range(bz, bz + 5):
        w.setze(bx + 1, 0, z, w.b("spruce_planks"))
    return w


KUESTE = {
    "leuchtturm": ("Leuchtturm", leuchtturm),
    "hafenkran": ("Hafenkran", hafenkran),
    "kai": ("Kai mit Steg", kai),
    "fischerhuetten": ("Fischerhütten", fischerhuetten),
    "klippenleuchtturm": ("Klippenleuchtturm", klippenleuchtturm),
    "bootshaus": ("Bootshaus", bootshaus),
}

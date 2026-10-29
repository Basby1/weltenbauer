"""Küste & Leuchttürme II – zwanzig weitere Bauten am Meer: Robbenbank, Strandkorb-Strand, Salzwiesen-Steg,
Kliffhaus, Rettungsstation, Reetdachkate, Hafenmole, Krabbenkutter am Kai, Riesen-Sandburg, Dünenpfad,
Brandungshöhle, Seebrücke, Buhnenfeld, Feuerschiff, Netzflickerplatz, Fischräucherei, Seemannskapelle,
Papageitaucher-Klippe, Treibgutstrand und Gezeitenmühle."""

from __future__ import annotations

import math

from erw_basis import M, S, baumrand, figur, haus, hoehe
from feinbau import Dachmat, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen
from skulptur import ell, kap, kasten, kegel, kreisrand


def kueste(w, R, ufer=0.25, strand=0.3, huegel=0.6, kliff=0):
    """Küstenstück: hinten Grasland (z < ...), dann Sandstrand, vorn (z groß) Meer. Gibt Höhen zurück."""
    rn = Rauschen(w, 6)
    rf = Rauschen(w, 2)
    rng = w.rng
    zellen = {}
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            uz = R * ufer + rn(x * 0.5, 3, 0) * 4
            sz = uz - R * strand
            if z > uz:
                w.setze(x, -1, z, w.b("sand"))
                w.setze(x, 0, z, w.b("water", level=0))
                zellen[(x, z)] = -1
                continue
            if z > sz:
                h = 0
                for y in range(-2, 1):
                    w.setze(x, y, z, w.b("sand"))
            else:
                h = int(huegel * 2 * rn(x * 0.7, 5, z * 0.7)) + (kliff if kliff else 0) * (z < sz - 2)
                for y in range(-2, h):
                    w.setze(x, y, z, w.b("stone" if kliff and y > 0 else "dirt"))
                v = rf(x, 4, z)
                w.setze(x, h, z, w.b("grass_block", snowy=False) if v < 0.75 else w.b("sand"))
                if v < 0.75 and rng.random() < 0.15:
                    w.setze(x, h + 1, z, w.b("grass"))
            zellen[(x, z)] = h
    return zellen


def holz(w, art="spruce"):
    return M(w, [(f"{art}_planks", 3), (f"stripped_{art}_log", 1)])


def boot(w, x0, y0, z0, L=4, B=1.5, holz_art="spruce", farbe="blue_terracotta", achse="x"):
    for i in range(-L, L + 1):
        t = i / (L + 0.5)
        bw = B * math.sqrt(max(0, 1 - t * t))
        for q in range(-int(bw) - 1, int(bw) + 2):
            if abs(q) <= bw:
                x, z = (x0 + i, z0 + q) if achse == "x" else (x0 + q, z0 + i)
                w.setze(x, y0, z, w.b(f"{holz_art}_planks"))
                if abs(q) > bw - 1:
                    w.setze(x, y0 + 1, z, w.b(farbe))


# ============================================================================ Bauten

def robbenbank(seed, g=2):
    """Robbenbank: eine flache Sandbank im Wattenmeer, auf der graue und gefleckte Seehund-Figuren dösen,
    umgeben von Prielen, Muschelfeldern und einem Beobachtungsturm mit Fernrohr am Ufer."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = kueste(w, R, ufer=-0.3, strand=0.4, huegel=0.2)
    rn = Rauschen(w, 4)
    for x in range(-R, R + 1):
        for z in range(int(-R * 0.2), R + 1):
            if math.hypot(x, z - R * 0.35) < R * 0.45 + rn(x, 1, z) * 3:
                w.setze(x, 0, z, w.b("sand"))
    gr = w.b("light_gray_concrete")
    dk = w.b("gray_concrete")
    rng = w.rng
    for k in range(3 + 2 * g):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.35
        x, z = round(math.cos(a) * d), round(R * 0.35 + math.sin(a) * d)
        f = gr if k % 2 else dk
        teile = [(ell(0, 0.9, 0, 2.0, 0.8, 0.9), f), (ell(1.8, 1.3, 0, 0.7, 0.6, 0.6), f),
                 (ell(2.4, 1.2, 0, 0.3, 0.25, 0.3), w.b("white_concrete")),
                 (ell(-2.2, 0.5, 0, 0.6, 0.3, 0.8), f), (ell(0.8, 0.4, 0.8, 0.5, 0.2, 0.3), f),
                 (ell(0.8, 0.4, -0.8, 0.5, 0.2, 0.3), f)]
        figur(w, 0.6 * s + 0.4, teile, (-3, -1, -2), (3, 3, 2), pos=(x, 1, z), winkel=rng.random() * 6.28)
    tx, tz = -int(R * 0.5), -int(R * 0.6)
    for y in range(1, 6):
        for dx in (0, 2):
            for dz in (0, 2):
                w.setze(tx + dx, y, tz + dz, w.b("spruce_fence"))
    for dx in range(-1, 4):
        for dz in range(-1, 4):
            w.setze(tx + dx, 6, tz + dz, w.b("spruce_planks"))
            if dx in (-1, 3) or dz in (-1, 3):
                w.setze(tx + dx, 7, tz + dz, w.b("spruce_fence"))
    w.setze(tx + 1, 7, tz + 1, w.b("spyglass_placeholder") if False else w.b("lightning_rod", facing="east",
                                                                               powered=False, waterlogged=False))
    _ = zellen
    return w


def strandkoerbe(seed, g=1):
    """Strandkorb-Strand: Reihen gestreifter Strandkörbe mit Hauben, Windschutz-Wände, Sandburgen, ein Rettungs-
    schwimmer-Hochstand und eine Holzpromenade mit Kiosk."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = kueste(w, R, ufer=0.4, strand=0.8)
    farben = [("blue_wool", "white_wool"), ("red_wool", "white_wool"), ("yellow_wool", "white_wool"),
              ("lime_wool", "white_wool")]
    n = int(4 + 3 * s)
    for k in range(n):
        x = -R // 2 + k * max(3, int(R / n))
        z = int(R * 0.05) + (k % 2) * 3
        if math.hypot(x, z) > R - 2:
            continue
        a, b = farben[k % 4]
        w.setze(x, 1, z, w.b("white_wool"))
        w.setze(x + 1, 1, z, w.b("white_wool"))
        for y in (2, 3):
            w.setze(x, y, z - 1, w.b(a if y % 2 else b))
            w.setze(x + 1, y, z - 1, w.b(b if y % 2 else a))
        w.setze(x, 3, z, w.b(a))
        w.setze(x + 1, 3, z, w.b(a))
        w.setze(x - 1, 2, z, w.b(b))
        w.setze(x + 2, 2, z, w.b(b))
    hx, hz = int(R * 0.45), int(R * 0.2)
    for y in range(1, 5):
        for dx in (0, 1):
            w.setze(hx + dx, y, hz, w.b("white_concrete") if dx == 0 else w.b("spruce_fence"))
    w.setze(hx, 5, hz, w.b("red_wool"))
    w.setze(hx + 1, 5, hz, w.b("red_wool"))
    for x in range(-R, R + 1):
        z = -int(R * 0.35)
        if (x, z) in zellen:
            for dz in (0, 1, 2):
                w.setze(x, zellen[(x, z + dz)] if (x, z + dz) in zellen else 0, z + dz, w.b("spruce_planks"))
    haus(w, -int(R * 0.4), -int(R * 0.55), 5, 4, 1, holz(w), holz="spruce", H=3, tuer_s="south",
         dach=("mcw:blue_terracotta", "prismarine_brick"), schorn=False)
    kugel(w, int(R * 0.1), 0.5, int(R * 0.3), 1.5 + 0.4 * s, w.b("sand"), ry=1.6)
    return w


def salzwiesensteg(seed, g=2):
    """Salzwiesen-Steg: ein langer, zickzack verlaufender Bohlensteg über eine Salzwiese mit Prielen, Queller-
    polstern (lila), Vogelbeobachtungshütte am Ende und Hinweistafeln."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    rn = Rauschen(w, 4)
    zellen = {}
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            v = rn(x * 1.5, 2, z * 1.5)
            if v < 0.3:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
                zellen[(x, z)] = -1
            else:
                w.setze(x, 0, z, w.b("grass_block", snowy=False) if v > 0.45 else w.b("mud"))
                w.setze(x, -1, z, w.b("dirt"))
                if v > 0.6 and (x + z) % 5 == 0:
                    w.setze(x, 1, z, w.b("allium") if (x * z) % 3 else w.b("grass"))
                zellen[(x, z)] = 0
    pts = [(-R * 0.8, -R * 0.6), (-R * 0.3, -R * 0.2), (-R * 0.5, R * 0.2), (R * 0.1, R * 0.4), (R * 0.5, R * 0.1)]
    for (a, b) in zip(pts, pts[1:]):
        n = int(math.hypot(b[0] - a[0], b[1] - a[1]))
        for k in range(n + 1):
            t = k / max(1, n)
            x, z = round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t)
            for dx in (-1, 0, 1):
                w.setze(x + dx, 1, z, w.b("spruce_planks"))
            if k % 3 == 0:
                w.setze(x - 2, 1, z, w.b("spruce_fence"))
                w.setze(x + 2, 1, z, w.b("spruce_fence"))
                w.setze(x, 0, z, w.b("spruce_log", axis="y"))
    hx, hz = round(pts[-1][0]), round(pts[-1][1])
    for x in range(hx - 2, hx + 3):
        for z in range(hz - 2, hz + 3):
            w.setze(x, 1, z, w.b("spruce_planks"))
            for y in range(2, 4):
                if abs(x - hx) == 2 or abs(z - hz) == 2:
                    w.setze(x, y, z, w.b("spruce_planks") if not (y == 3 and z == hz + 2) else w.b("air"))
    satteldach(w, hx - 2, hz - 2, hx + 2, hz + 2, 4, Dachmat(w, ["mcw:thatch", "spruce"]), first_x=True, ue=1,
               giebel=holz(w), traufe="spruce")
    return w


def kliffhaus(seed, g=2):
    """Kliffhaus: ein weißes Kapitänshaus mit blauen Fensterläden und Walmdach steht direkt an der Kante einer
    hohen, roten Steilküste; ein Garten mit Fahnenmast und eine Treppe in den Fels hinab zum Strand."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    H = int(6 * s + 5)
    rn = Rauschen(w, 4)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            kante = R * 0.15 + rn(x * 0.7, 3, 0) * 3
            if z > kante + 4:
                w.setze(x, -1, z, w.b("sand"))
                w.setze(x, 0, z, w.b("water", level=0))
            elif z > kante:
                for y in range(-1, 1):
                    w.setze(x, y, z, w.b("sand"))
            else:
                for y in range(-1, H + 1):
                    w.setze(x, y, z, w.b("grass_block", snowy=False) if y == H else
                            w.b("red_terracotta" if (y + x // 3) % 3 else "orange_terracotta"))
    B, T = int(4 * s + 5) | 1, int(3 * s + 5) | 1
    haus(w, 0, -T // 2 - 1, B, T, H + 1, M(w, [("white_terracotta", 2), ("calcite", 1)]), holz="spruce", H=4,
         dach=("mcw:gray_terracotta", "deepslate_tile"), tuer_s="north")
    for y in range(H + 1, H + int(7 * s + 4)):
        w.setze(B // 2 + 3, y, -2, w.b("white_concrete") if y < H + 3 else w.b("birch_fence"))
    w.setze(B // 2 + 4, H + int(7 * s + 2), -2, w.b("blue_wool"))
    w.setze(B // 2 + 5, H + int(7 * s + 2), -2, w.b("white_wool"))
    for k in range(H):
        z = int(R * 0.15) - 1 - k
        x = -B // 2 - 3
        for dx in (0, 1):
            w.setze(x + dx, H - k, z + H, treppe(w, "cobblestone", "north"))
    for x in range(-B // 2 - 1, B // 2 + 2):
        w.setze(x, H + 1, -T - 3, zaun(w, "birch"))
    return w


def rettungsstation(seed, g=2):
    """Rettungsstation: ein Bootshaus mit rot-weißem Turm und Glockengiebel, eine steile Slipanlage mit
    Rettungsboot auf dem Wagen, Rettungsringe an der Wand und ein Signalmast mit Flaggen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = kueste(w, R, ufer=0.25, strand=0.25)
    B, T = int(4 * s + 5) | 1, int(5 * s + 6) | 1
    hz = -int(R * 0.3)
    haus(w, 0, hz, B, T, 1, M(w, [("white_terracotta", 2), ("red_terracotta", 1)]), holz="spruce", H=5,
         dach=("mcw:red_terracotta", "brick"), tuer_s="south", schorn=False)
    for y in range(1, 4):
        for x in (-1, 0, 1):
            w.bloecke.pop((x, y, hz + T // 2), None)
    tx = B // 2 + 2
    for y in range(1, int(8 * s + 7)):
        for x, z in kreisrand(1.6, tx, hz):
            w.setze(x, y, z, w.b("red_concrete" if (y // 2) % 2 else "white_concrete"))
    kegeldach(w, tx, hz, int(8 * s + 7), 1, Dachmat(w, ["brick"]), form="kegel", spitze="lightning_rod")
    for z in range(hz + T // 2, int(R * 0.6)):
        y = max(0, 1 - (z - hz - T // 2) // 4)
        for x in (-1, 1):
            w.setze(x, y, z, w.b("rail", shape="north_south", waterlogged=False) if y > 0 else w.b("spruce_planks"))
        w.setze(0, y, z, w.b("spruce_planks"))
    boot(w, 0, 1, hz + T // 2 + 3, L=int(2 * s + 2), B=1.3, farbe="orange_terracotta", achse="z")
    for k in range(3):
        w.setze(-B // 2 - 1, 3, hz - 2 + k * 2, w.b("orange_terracotta"))
    mx = -B // 2 - 4
    for y in range(1, int(8 * s + 5)):
        w.setze(mx, y, hz, w.b("spruce_fence"))
    for k, f in enumerate(["red_wool", "yellow_wool", "blue_wool"]):
        w.setze(mx + 1, int(8 * s + 4) - k * 2, hz, w.b(f))
    _ = zellen
    return w


def reetdachkate(seed, g=1):
    """Reetdachkate: ein langgestrecktes Fischerhaus mit tief heruntergezogenem Reetdach, Backsteinwänden, grünen
    Türen, einem Bauerngarten mit Staketenzaun und Netzen über dem Zaun."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = kueste(w, R, ufer=0.45, strand=0.25)
    B, T = int(6 * s + 7) | 1, int(3 * s + 5) | 1
    haus(w, 0, -int(R * 0.25), B, T, 1, M(w, [("bricks", 3), ("mud_bricks", 1)]), holz="dark_oak", H=3,
         dach=("mcw:thatch", "spruce"), tuer_s="south", steil=2)
    gz = -int(R * 0.25) + T // 2 + 2
    for x in range(-B // 2, B // 2 + 1):
        w.setze(x, 1, gz + 4, w.b("birch_fence"))
        for z in range(gz, gz + 4):
            if (x + z) % 2 == 0:
                w.setze(x, 1, z, w.b(["poppy", "cornflower", "dandelion", "oxeye_daisy"][(x + z) % 4]))
    for x in range(-B // 2, B // 2 + 1, 2):
        w.setze(x, 2, gz + 4, w.b("cobweb"))
    for k in range(2):
        boot(w, -int(R * 0.3) + k * 8, 1, int(R * 0.35), L=3, B=1.3, farbe=["blue_terracotta", "green_terracotta"][k])
    _ = zellen
    return w


def hafenmole(seed, g=2):
    """Hafenmole: eine geschwungene Steinmole mit Pollern, Laternen und einem kleinen grün-weißen Leuchtfeuer am
    Molenkopf schützt ein Hafenbecken mit Fischerbooten vor der Brandung."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = kueste(w, R, ufer=-0.2, strand=0.25)
    st = M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 1), ("cobblestone", 1)])
    pts = bez((-R * 0.6, 0, -R * 0.15), (-R * 0.5, 0, R * 0.6), (R * 0.3, 0, R * 0.7))
    for x, y, z, t in pts:
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for yy in range(-1, 2):
                    w.setze(round(x + dx), yy, round(z + dz), st(round(x), yy, round(z)))
    for i, (x, y, z, t) in enumerate(pts[::6]):
        w.setze(round(x), 2, round(z), w.b("stone_brick_wall") if i % 2 else w.b("spruce_fence"))
        if i % 2 == 0:
            w.setze(round(x), 3, round(z), w.b("lantern", hanging=False, waterlogged=False))
    ex, _, ez, _ = pts[-1]
    ex, ez = round(ex), round(ez)
    H = int(5 * s + 4)
    for y in range(2, H + 2):
        for x, z in kreisrand(1.4, ex, ez):
            w.setze(x, y, z, w.b("lime_terracotta" if (y // 2) % 2 else "white_terracotta"))
    w.setze(ex, H + 2, ez, w.b("sea_lantern"))
    w.setze(ex, H + 3, ez, w.b("lime_terracotta"))
    for k in range(2 + g // 2):
        boot(w, -int(R * 0.2) + k * 7, 1, int(R * 0.25), L=3, B=1.3,
             farbe=["blue_terracotta", "red_terracotta", "yellow_terracotta"][k % 3])
    _ = zellen
    return w


def krabbenkutter(seed, g=2):
    """Krabbenkutter am Kai: ein Kutter mit Steuerhaus und zwei ausgefahrenen Baumkurren-Auslegern mit Netzen
    liegt an einer Kaimauer, auf der Kisten, Fischkörbe und ein Krabbenkocher stehen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = kueste(w, R, ufer=0.0, strand=0.05)
    st = M(w, [("stone_bricks", 3), ("cobblestone", 1)])
    kz = int(R * 0.0) + 1
    for x in range(-R, R + 1):
        for z in range(kz - 3, kz + 1):
            if math.hypot(x, z) < R:
                for y in range(-1, 2):
                    w.setze(x, y, z, st(x, y, z))
    L = int(5 * s + 4)
    bz = kz + int(2 * s + 3)
    for i in range(-L, L + 1):
        t = i / (L + 0.5)
        bw = (1.4 * s + 1.4) * math.sqrt(max(0, 1 - t ** 4)) if t > -0.8 else (1.4 * s + 1.4) * 0.7
        for q in range(-int(bw) - 1, int(bw) + 2):
            if abs(q) <= bw:
                rand = abs(q) > bw - 1
                w.setze(i, 0, bz + q, w.b("white_concrete") if rand else w.b("spruce_planks"))
                if rand:
                    w.setze(i, 1, bz + q, w.b("blue_concrete"))
                    w.setze(i, -1, bz + q, w.b("red_concrete"))
    for x in range(-2, 1):
        for z in range(bz - 1, bz + 2):
            for y in range(1, 4):
                if x in (-2, 0) or z in (bz - 1, bz + 1):
                    w.setze(x, y, z, w.b("white_concrete") if y < 3 else w.b("glass_pane"))
            w.setze(x, 4, z, w.b("blue_concrete"))
    for y in range(1, int(6 * s + 5)):
        w.setze(2, y, bz, w.b("white_concrete") if y < 3 else w.b("iron_bars", waterlogged=False))
    for sz in (-1, 1):
        for k in range(int(3 * s + 3)):
            w.setze(2, int(6 * s + 4) - k // 2, bz + sz * (k + 1), w.b("iron_bars", waterlogged=False))
        w.setze(2, int(6 * s + 4) - int(3 * s + 3) // 2 - 1, bz + sz * int(3 * s + 4), w.b("cobweb"))
    for k in range(4 + g):
        x = -int(R * 0.5) + k * 2
        w.setze(x, 2, kz - 2, w.b("barrel", facing="up", open=False) if k % 2 else w.b("spruce_planks"))
    w.setze(int(R * 0.4), 2, kz - 2, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    w.setze(int(R * 0.4), 3, kz - 2, w.b("water_cauldron", level=3))
    _ = zellen
    return w


def sandburg(seed, g=2):
    """Riesen-Sandburg: eine riesige, detaillierte Sandburg mit Rundtürmen, Zinnen, Muschel-Fenstern, Wassergraben
    und einer kleinen Fahne, gebaut am Flutsaum, mit Eimer und Schaufel daneben."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = kueste(w, R, ufer=0.55, strand=1.2)
    A = int(4 * s + 4)
    H = int(3 * s + 3)
    sa = M(w, [("sandstone", 3), ("smooth_sandstone", 1), ("sand", 1)])
    for x, z in kreisrand(A + 3):
        w.setze(x, 0, z, w.b("water", level=0))
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            rand = max(abs(x), abs(z)) == A
            for y in range(1, (H if rand else 1) + 1):
                w.setze(x, y, z, sa(x, y, z))
            if rand and (x + z) % 2 == 0:
                w.setze(x, H + 1, z, w.b("sandstone_wall"))
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in range(1, H + int(3 * s) + 3):
                for x, z in kreisrand(1.5 + 0.4 * s, sx * A, sz * A):
                    w.setze(x, y, z, sa(x, y, z))
            kegeldach(w, sx * A, sz * A, H + int(3 * s) + 3, int(1.5 + 0.4 * s), Dachmat(w, ["sandstone"]),
                      form="kegel", spitze=None)
    for y in range(1, H + int(6 * s) + 4):
        for x, z in kreisrand(1.8 + 0.6 * s):
            w.setze(x, y, z, sa(x, y, z))
    top = H + int(6 * s) + 4
    w.setze(0, top, 0, w.b("spruce_fence"))
    w.setze(0, top + 1, 0, w.b("spruce_fence"))
    w.setze(1, top + 1, 0, w.b("red_wool"))
    for x in (-1, 0, 1):
        for y in (1, 2):
            w.bloecke.pop((x, y, A), None)
    for x in range(-1, 2):
        w.setze(x, 1, A + 1, w.b("smooth_sandstone_slab", type="bottom", waterlogged=False))
        w.setze(x, 1, A + 2, w.b("smooth_sandstone_slab", type="bottom", waterlogged=False))
        w.setze(x, 1, A + 3, w.b("smooth_sandstone_slab", type="bottom", waterlogged=False))
    ex, ez = A + 6, -2
    for y in range(1, 3):
        for x, z in kreisrand(1.2, ex, ez):
            w.setze(x, y, z, w.b("red_concrete"))
    w.setze(ex - 3, 1, ez, w.b("yellow_concrete"))
    w.setze(ex - 3, 2, ez, w.b("yellow_concrete"))
    _ = zellen
    return w


def duenenpfad(seed, g=2):
    """Dünenpfad: ein gewundener Holzbohlenweg über hohe, mit Strandhafer bewachsene Sanddünen und Sandfangzäune,
    oben eine Aussichtsplattform mit Bank, unten der Strand mit Treibholz."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    rn = Rauschen(w, 6)
    rng = w.rng
    zellen = {}
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            if z > R * 0.55:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("sand"))
                zellen[(x, z)] = -1
                continue
            d = abs(z + R * 0.1)
            h = int((5 * s + 3) * max(0, 1 - d / (R * 0.45)) * (0.6 + 0.6 * rn(x * 0.6, 3, z * 0.6)))
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("sand"))
            if rng.random() < 0.25 and h > 0:
                w.setze(x, h + 1, z, w.b("grass") if rng.random() < 0.7 else w.b("dead_bush"))
            zellen[(x, z)] = h
    for z in range(-R + 2, int(R * 0.55)):
        x = round(math.sin(z / 5) * 3)
        y = max(zellen.get((x, z), 0), zellen.get((x - 1, z), 0), zellen.get((x + 1, z), 0)) + 1
        for dx in (-1, 0, 1):
            w.setze(x + dx, y, z, w.b("spruce_slab", type="bottom", waterlogged=False))
            for yy in range(y + 1, y + 3):
                w.bloecke.pop((x + dx, yy, z), None)
    for k in range(3):
        z = -int(R * 0.6) + k * int(R * 0.3)
        for x in range(-R, -4):
            if (x, z) in zellen and x % 2 == 0:
                w.setze(x, zellen[(x, z)] + 1, z, w.b("spruce_fence"))
    top = max(zellen.values())
    for x in range(-3, 4):
        for z in range(-int(R * 0.1) - 2, -int(R * 0.1) + 3):
            w.setze(x + 6, top + 2, z, w.b("spruce_planks"))
    w.setze(6, top + 3, -int(R * 0.1), treppe(w, "spruce", "north"))
    for k in range(2):
        w.setze(int(R * 0.3) + k, 1, int(R * 0.45), w.b("stripped_oak_log", axis="x"))
    return w


def brandungshoehle(seed, g=2):
    """Brandungshöhle: eine Felsklippe am Meer mit einem großen Felstor, durch das die Wellen in eine Grotte
    rollen, davor ein freistehender Brandungspfeiler und Möwennester auf den Simsen."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    rn = Rauschen(w, 4)
    H = int(10 * s + 6)
    st = M(w, [("stone", 3), ("andesite", 2), ("diorite", 1), ("tuff", 1)])
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            w.setze(x, -1, z, w.b("sand"))
            if z > -R * 0.1 + rn(x, 3, 0) * 4:
                w.setze(x, 0, z, w.b("water", level=0))
            else:
                h = H + int(rn(x, 5, z) * 3)
                for y in range(0, h + 1):
                    w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else st(x, y, z))
    tb, th = 3 * s + 2.5, 5 * s + 4
    for x in range(-int(tb) - 1, int(tb) + 2):
        for y in range(0, int(th) + 2):
            if (x / tb) ** 2 + (y / th) ** 2 <= 1:
                for z in range(-int(R * 0.6), int(R * 0.1)):
                    w.bloecke.pop((x, y, z), None)
                    if y == 0:
                        w.setze(x, 0, z, w.b("water", level=0))
    px, pz = int(R * 0.35), int(R * 0.45)
    for y in range(0, int(H * 0.8)):
        r = (1.8 * s + 1.2) * (1 - 0.3 * y / H)
        for x in range(-3, 4):
            for z in range(-3, 4):
                if math.hypot(x, z) <= r:
                    w.setze(px + x, y, pz + z, st(px + x, y, pz + z))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 3 and w.frei(x, y + 1, z) and w.frei(x, y, z + 1) and rng.random() < 0.01:
            w.setze(x, y + 1, z, w.b("white_wool"))
    return w


def seebruecke(seed, g=2):
    """Seebrücke: eine lange Holzbrücke auf Pfählen führt weit ins Meer zu einem Pavillon mit Kuppeldach, Geländer
    mit Laternen, Sitzbänke und eine Anlegestelle für Ausflugsboote."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = kueste(w, R, ufer=-0.4, strand=0.3)
    z0 = -int(R * 0.55)
    z1 = int(R * 0.45)
    for z in range(z0, z1 + 1):
        for x in (-2, -1, 0, 1, 2):
            w.setze(x, 2, z, w.b("spruce_planks") if abs(x) < 2 else w.b("spruce_slab", type="top",
                                                                             waterlogged=False))
        for x in (-2, 2):
            w.setze(x, 3, z, w.b("spruce_fence"))
            if z % 6 == 0:
                w.setze(x, 4, z, w.b("lantern", hanging=False, waterlogged=False))
        if z % 4 == 0:
            for x in (-2, 2):
                for y in range(-1, 2):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
    pr = int(3 * s + 3)
    for x in range(-pr, pr + 1):
        for z in range(z1 - pr, z1 + pr + 1):
            d = math.hypot(x, z - z1)
            if d <= pr:
                w.setze(x, 2, z, w.b("spruce_planks"))
            if abs(d - pr + 0.5) < 0.6 and (x + z) % 3 == 0:
                for y in range(3, 7):
                    w.setze(x, y, z, w.b("white_concrete"))
    from wueste_eis import kuppel
    kuppel(w, w.b("waxed_oxidized_cut_copper"), 0, z1, 7, pr, form="rund", spitze="gold_block")
    for x in range(-pr, pr + 1):
        for z in range(z1 - pr, z1 + pr + 1):
            if math.hypot(x, z - z1) < pr:
                w.setze(x, 7, z, w.b("white_concrete"), False)
    boot(w, pr + 4, 1, z1, L=int(3 * s + 2), B=1.5, farbe="white_concrete")
    _ = zellen
    return w


def buhnenfeld(seed, g=1):
    """Buhnenfeld: mehrere Reihen alter, verwitterter Holzpfähle ragen schräg vom Strand ins Meer, dazwischen
    angespülter Tang, Muscheln und Möwen auf den Pfahlköpfen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = kueste(w, R, ufer=-0.1, strand=0.5)
    rng = w.rng
    n = 3 + g
    for k in range(n):
        x0 = -R + 3 + k * int(2 * R / n)
        for z in range(-int(R * 0.4), int(R * 0.9)):
            x = x0 + round(z * 0.15)
            if math.hypot(x, z) > R:
                continue
            for dx in (0, 1):
                hoch = 2 + int(rng.random() * 2) if rng.random() > 0.1 else 1
                for y in range(-1, hoch):
                    w.setze(x + dx, y, z, w.b("dark_oak_log", axis="y") if (z + dx) % 2 else
                            w.b("stripped_dark_oak_log", axis="y"))
            if rng.random() < 0.06:
                w.setze(x, 3, z, w.b("white_wool"))
    for _ in range(int(14 * s)):
        x, z = int((rng.random() - 0.5) * R * 1.6), int((rng.random() - 0.3) * R * 0.6)
        if (x, z) in zellen and zellen[(x, z)] == 0:
            w.setze(x, 1, z, w.b("dried_kelp_block") if rng.random() < 0.3 else w.b("dead_bush"))
    return w


def feuerschiff(seed, g=2):
    """Feuerschiff: ein rot gestrichenes, vor Anker liegendes Leuchtschiff mit großem Laternenmast in der Mitte,
    Ankerketten, Rettungsbooten an Davits und weißem Namenszug auf dem Rumpf."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                w.setze(x, -1, z, w.b("sand"))
                w.setze(x, 0, z, w.b("water", level=0))
    L = int(8 * s + 6)
    B = 2.2 * s + 1.8
    for i in range(-L, L + 1):
        t = i / (L + 0.5)
        bw = B * math.sqrt(max(0, 1 - t ** 4))
        for q in range(-int(bw) - 1, int(bw) + 2):
            if abs(q) <= bw:
                rand = abs(q) > bw - 1
                for y in range(-1, 3):
                    if rand or y == -1:
                        w.setze(i, y, q, w.b("white_concrete" if y == 1 and rand and abs(i) < L * 0.5 and i % 2 else
                                             "red_concrete"))
                w.setze(i, 2, q, w.b("spruce_planks") if not rand else w.b("red_concrete"))
                if rand:
                    w.setze(i, 3, q, w.b("iron_bars", waterlogged=False))
    for x in range(-int(L * 0.6), -int(L * 0.2)):
        for z in range(-1, 2):
            for y in range(3, 5):
                if x in (-int(L * 0.6), -int(L * 0.2) - 1) or abs(z) == 1:
                    w.setze(x, y, z, w.b("white_concrete") if y == 3 else w.b("glass_pane"))
            w.setze(x, 5, z, w.b("red_concrete"))
    H = int(8 * s + 6)
    for y in range(3, H):
        w.setze(0, y, 0, w.b("red_concrete") if y % 3 else w.b("white_concrete"))
    for x, z in kreisrand(1.2):
        w.setze(x, H, z, w.b("glass"))
    w.setze(0, H, 0, w.b("sea_lantern"))
    w.setze(0, H + 1, 0, w.b("red_concrete"))
    for k in range(int(L * 0.6)):
        w.setze(L + 1 + k, 2 - k // 2, 0, w.b("chain", axis="x", waterlogged=False))
    for sz in (-1, 1):
        for y in (3, 4):
            w.setze(int(L * 0.4), y, sz * (round(B) + 1), w.b("iron_bars", waterlogged=False))
        w.setze(int(L * 0.4), 2, sz * (round(B) + 2), w.b("white_concrete"))
        w.setze(int(L * 0.4) + 1, 2, sz * (round(B) + 2), w.b("white_concrete"))
    return w


def netzflickerplatz(seed, g=1):
    """Netzflickerplatz: zwischen Pfählen gespannte Fischernetze (Spinnweben) zum Trocknen, Netzflicker-Figuren
    auf Hockern, Bojen in Rot und Orange, Korkschwimmer und ein Teerkessel."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = kueste(w, R, ufer=0.4, strand=0.6)
    n = 2 + g
    for k in range(n):
        z = -int(R * 0.4) + k * 4
        for x in range(-int(R * 0.5), int(R * 0.5)):
            if x % 4 == 0:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("spruce_fence"))
            else:
                w.setze(x, 2, z, w.b("cobweb"))
                w.setze(x, 3, z, w.b("cobweb") if (x + k) % 2 else w.b("air"))
    for k in range(3 + g):
        x, z = -int(R * 0.4) + k * 3, int(R * 0.15)
        w.setze(x, 1, z, w.b("red_concrete") if k % 2 else w.b("orange_concrete"))
    for k, rock in enumerate(("blue_wool", "brown_wool")):
        from erw_markt import mensch
        figur(w, 0.5 * s + 0.3, mensch(w, rock), (-2, -1, -2), (2, 6, 2), pos=(-int(R * 0.3) + k * 6, 1, -int(R * 0.6)))
    w.setze(int(R * 0.45), 1, -2, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    w.setze(int(R * 0.45), 2, -2, w.b("cauldron"))
    _ = zellen
    return w


def raeucherei(seed, g=1):
    """Fischräucherei: ein schwarzes Holzhaus mit mehreren hohen Räucherschloten, aus denen Rauch quillt, Stangen
    mit goldgelben Räucherfischen, Buchenholzstapel und ein Verkaufsfenster zum Strand."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = kueste(w, R, ufer=0.4, strand=0.35)
    B, T = int(5 * s + 6) | 1, int(3 * s + 5) | 1
    top = haus(w, 0, -int(R * 0.25), B, T, 1, M(w, [("dark_oak_planks", 2), ("black_terracotta", 1)]),
               holz="dark_oak", H=4, dach=("deepslate_tile", "dark_oak"), tuer_s="south", schorn=False)
    for k in range(2 + g // 2):
        x = -B // 2 + 2 + k * 3
        for y in range(4, top + 4):
            for dx in (0, 1):
                w.setze(x + dx, y, -int(R * 0.25), w.b("bricks"))
        w.setze(x, top + 4, -int(R * 0.25), w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                 waterlogged=False))
    for k in range(2):
        z = -int(R * 0.25) + T // 2 + 2 + k * 2
        for x in range(-B // 2, B // 2 + 1):
            w.setze(x, 3, z, w.b("spruce_fence") if x % 3 == 0 else w.b("orange_terracotta") if x % 2 else
                    w.b("yellow_terracotta"))
            if x % 3 == 0:
                for y in (1, 2):
                    w.setze(x, y, z, w.b("spruce_fence"))
    for k in range(4):
        w.setze(B // 2 + 2, 1 + k // 2, -2 + k % 2, w.b("birch_log", axis="x"))
    _ = zellen
    return w


def seemannskapelle(seed, g=1):
    """Seemannskapelle: eine kleine weiße Kapelle mit spitzem Turm auf einer Düne, ein Schiffsmodell über dem
    Portal, ein Friedhof mit Ankerkreuzen und ein Gedenkstein für die auf See Gebliebenen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = kueste(w, R, ufer=0.45, strand=0.3)
    B, T = int(3 * s + 5) | 1, int(5 * s + 7) | 1
    top = haus(w, 0, -int(R * 0.2), B, T, 1, M(w, [("white_concrete", 2), ("calcite", 1)]), holz="spruce", H=4,
               dach=("mcw:gray_terracotta", "deepslate_tile"), tuer_s="south", schorn=False, steil=2)
    tz = -int(R * 0.2) + T // 2 - 1
    for y in range(top - 1, top + int(4 * s + 3)):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) == 1 or abs(dz) == 1:
                    w.setze(dx, y, tz + dz, w.b("white_concrete"))
    kegeldach(w, 0, tz, top + int(4 * s + 3), 1, Dachmat(w, ["deepslate_tile"]), form="nadel", eckig=True,
              spitze="gold_block")
    for k in range(3 + g):
        x, z = -B // 2 - 3 - (k % 2) * 2, -int(R * 0.4) + k * 2
        y = zellen.get((x, z), 0) + 1
        w.setze(x, y, z, w.b("iron_bars", waterlogged=False))
        w.setze(x, y + 1, z, w.b("iron_bars", waterlogged=False))
        w.setze(x, y + 2, z, w.b("chain", axis="x", waterlogged=False))
    w.setze(B // 2 + 3, 1, 0, w.b("stone"))
    w.setze(B // 2 + 3, 2, 0, w.b("chiseled_stone_bricks"))
    return w


def papageitaucher(seed, g=2):
    """Papageitaucher-Klippe: eine grasbewachsene Steilklippe voller Nisthöhlen, auf deren Rand bunte Papageitaucher-
    Figuren mit orangen Schnäbeln sitzen, darunter Brandung und Felsklippen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    H = int(8 * s + 6)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            if z > R * 0.2 + rn(x, 3, 0) * 3:
                w.setze(x, -1, z, w.b("gravel"))
                w.setze(x, 0, z, w.b("water", level=0))
            else:
                h = H + int(rn(x, 5, z) * 2)
                for y in range(-1, h + 1):
                    w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else w.b("dirt") if y > h - 2 else
                            w.b("stone"))
    rng = w.rng
    for x in range(-R, R + 1):
        for y in range(H - 3, H):
            z = None
            for zz in range(R, -R, -1):
                if not w.frei(x, y, zz):
                    z = zz
                    break
            if z is not None and rng.random() < 0.18:
                w.bloecke.pop((x, y, z), None)
    sch = w.b("black_concrete")
    we = w.b("white_concrete")
    og = w.b("orange_concrete")
    for k in range(5 + 3 * g):
        x = int((rng.random() - 0.5) * R * 1.4)
        zt = max([zz for zz in range(-R, R) if not w.frei(x, H, zz)] or [0])
        teile = [(ell(0, 1.1, 0, 0.6, 0.9, 0.6), sch), (ell(0.25, 1.0, 0, 0.4, 0.7, 0.45), we),
                 (ell(0, 2.1, 0, 0.45, 0.45, 0.45), sch), (ell(0.2, 2.1, 0, 0.3, 0.3, 0.42), we),
                 (ell(0.55, 2.0, 0, 0.3, 0.2, 0.12), og), (kap((0, 0.3, 0.2), (0.2, 0, 0.2), 0.12), og)]
        figur(w, 0.6 * s + 0.4, teile, (-1, -1, -1), (2, 3, 1), pos=(x, H + 1, zt - 1), winkel=-math.pi / 2)
    return w


def treibgut(seed, g=1):
    """Treibgutstrand: ein Strand voller angespülter Schätze – zerbrochene Masten, Fässer, eine Galionsfigur,
    Flaschen (Glas), Kisten, Tauknäuel und eine aus Treibholz gebaute Unterschlupf-Hütte."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = kueste(w, R, ufer=0.35, strand=0.9)
    rng = w.rng
    for k in range(3 + g):
        a = rng.random() * 3.14
        x0, z0 = int((rng.random() - 0.5) * R), int(rng.random() * R * 0.3)
        L = int(4 + rng.random() * 4 * s)
        for i in range(L):
            w.setze(x0 + round(math.cos(a) * i), 1, z0 + round(math.sin(a) * i), w.b("stripped_oak_log",
                                                                                     axis="x" if math.cos(a) > 0.7
                                                                                     else "z"))
    for k in range(5 + 2 * g):
        x, z = int((rng.random() - 0.5) * R * 1.4), int((rng.random() - 0.4) * R * 0.6)
        if (x, z) in zellen and zellen[(x, z)] >= 0:
            ware = ["barrel", "glass", "brown_wool", "chest", "lime_stained_glass"][k % 5]
            pr = {"barrel": dict(facing="east", open=False), "chest": dict(facing="south", type="single",
                                                                          waterlogged=False)}.get(ware, {})
            w.setze(x, zellen[(x, z)] + 1, z, w.b(ware, **pr))
    hx, hz = -int(R * 0.4), -int(R * 0.4)
    for k in range(4):
        for x in range(hx - 3 + k, hx + 4 - k):
            w.setze(x, 1 + k, hz - 2 + k, w.b("stripped_oak_log", axis="x"))
            w.setze(x, 1 + k, hz + 2 - k, w.b("stripped_oak_log", axis="x"))
    teile = [(kap((0, 0, 0), (0, 3.5, 0), 0.8, 0.6), w.b("white_terracotta")),
             (ell(0, 4.2, 0, 0.6, 0.7, 0.6), w.b("white_terracotta")),
             (ell(0, 4.6, -0.1, 0.65, 0.4, 0.65), w.b("yellow_terracotta"))]
    figur(w, 0.6 * s + 0.4, teile, (-2, -1, -2), (2, 6, 2), pos=(int(R * 0.3), 1, int(R * 0.1)), winkel=0.0)
    return w


def gezeitenmuehle(seed, g=2):
    """Gezeitenmühle: eine Mühle auf einem Damm zwischen Meer und Staubecken, mit Schleusentoren und einem
    Wasserrad unter dem Mühlenhaus, das bei Ebbe vom ablaufenden Wasser angetrieben wird."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = kueste(w, R, ufer=0.2, strand=0.15)
    for x in range(-R, R + 1):
        for z in range(-R, -int(R * 0.15)):
            if math.hypot(x, z) < R * 0.85 and (x, z) in zellen:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
    st = M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 1)])
    for x in range(-R, R + 1):
        for z in range(-int(R * 0.15) - 2, -int(R * 0.15) + 3):
            if math.hypot(x, z) < R:
                for y in range(-1, 2):
                    w.setze(x, y, z, st(x, y, z))
    for x in (-int(R * 0.4), int(R * 0.4)):
        for y in range(0, 3):
            for z in range(-int(R * 0.15) - 2, -int(R * 0.15) + 3):
                w.setze(x, y, z, w.b("spruce_planks") if y else w.b("water", level=0))
    from erw_handwerk import wasserrad
    wasserrad(w, 0, -int(R * 0.15), 2, 2 * s + 1.5, achse="z")
    B, T = int(4 * s + 6) | 1, int(3 * s + 5) | 1
    haus(w, 0, -int(R * 0.15) - T // 2 - 2, B, T, 2, M(w, [("white_terracotta", 2), ("calcite", 1)]), holz="dark_oak",
         H=int(2 * s + 4), dach=("mcw:thatch", "spruce"), tuer_s="north")
    return w


KUESTE3 = {
    "robbenbank": ("Robbenbank", robbenbank),
    "strandkoerbe": ("Strandkorb-Strand", strandkoerbe),
    "salzwiesensteg": ("Salzwiesen-Steg", salzwiesensteg),
    "kliffhaus": ("Kliffhaus", kliffhaus),
    "rettungsstation": ("Rettungsstation", rettungsstation),
    "reetdachkate": ("Reetdachkate", reetdachkate),
    "geschwungene_mole": ("Geschwungene Mole mit Leuchtfeuer", hafenmole),
    "krabbenkutter": ("Krabbenkutter am Kai", krabbenkutter),
    "sandburg": ("Riesen-Sandburg", sandburg),
    "duenenpfad": ("Dünenpfad", duenenpfad),
    "brandungshoehle": ("Brandungshöhle", brandungshoehle),
    "seebruecke": ("Seebrücke", seebruecke),
    "buhnenfeld": ("Buhnenfeld", buhnenfeld),
    "feuerschiff": ("Feuerschiff", feuerschiff),
    "netzflickerplatz": ("Netzflickerplatz", netzflickerplatz),
    "raeucherei": ("Fischräucherei", raeucherei),
    "seemannskapelle": ("Seemannskapelle", seemannskapelle),
    "papageitaucher": ("Papageitaucher-Klippe", papageitaucher),
    "treibgut": ("Treibgutstrand", treibgut),
    "gezeitenmuehle": ("Gezeitenmühle", gezeitenmuehle),
}

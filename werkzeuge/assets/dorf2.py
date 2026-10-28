"""Gärten & Parks, Mühlen & Handwerk, Küste & Leuchttürme (neu) – je 20 Bauten, mit Mod-Blöcken."""

from __future__ import annotations

import math

import numpy as np

import modbloecke as MB
import pracht as P
from lib import Rauschen, Verlauf, einfuegen, laub, zerfall
from pracht import Mat, gelaende, treppe
from skulptur import Skulptur, dreh_y, dreh_z, ell, kap, kreisrand, ohne, scheibe, spiegel_x, torus, zur_mitte
from weltwunder import bl, hohl, platz, sk
import haeuser as H_

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    from lib import Welt
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _wand(w, name):
    return w.b(name, up=True, north="none", south="none", east="none", west="none", waterlogged=False)


BLUMEN = ["poppy", "dandelion", "allium", "azure_bluet", "red_tulip", "orange_tulip", "white_tulip", "pink_tulip",
          "oxeye_daisy", "cornflower", "lily_of_the_valley", "blue_orchid"]


# ============================================================================ GÄRTEN & PARKS


def heckenring(w, pts, hoehe=2, art="azalea"):
    menge = set(pts)
    for (x, z) in pts:
        for y in range(1, hoehe + 1):
            w.setze(x, y, z, MB.hecke(w, art, north=(x, z - 1) in menge, south=(x, z + 1) in menge,
                                      east=(x + 1, z) in menge, west=(x - 1, z) in menge))


def blumenbeet(w, pts, farben=None):
    rng = w.rng
    farben = farben or BLUMEN
    for (x, z) in pts:
        w.setze(x, 0, z, w.b("grass_block", snowy=False) if rng.random() < 0.6 else w.b("rooted_dirt"))
        w.setze(x, 1, z, w.b(farben[int(rng.integers(len(farben)))]))


def kiesweg(w, pts, d=None):
    rng = w.rng
    for (x, z) in pts:
        v = rng.random()
        w.setze(x, 0, z, MB.pflaster(w, "stone", "running_bond") if v < 0.35 else w.b("gravel") if v < 0.7 else
                w.b("dirt_path"))


def parkbank(w, x, z, richtung, holz="dark_oak"):
    H_.bank(w, x, z, richtung, holz)


def parklaterne(w, x, z):
    for y in range(1, 4):
        w.setze(x, y, z, w.b("dark_oak_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(x, 4, z, MB.laterne(w, "cross_lantern"))


def heckenlabyrinth(seed, g=1):
    """Heckenlabyrinth: verschlungene Gänge zwischen mannshohen Hecken (Macaw's Hedges), in der Mitte ein
    Brunnenpavillon, an den Ecken Laternen."""
    w = _welt(seed)
    u = U[g]
    n = 5 + g * 2
    rng = w.rng
    gelaende(w, n * 2 + 4, art="wiese", dichte=0.2)
    wand = set((x, z) for x in range(2 * n + 1) for z in range(2 * n + 1))
    besucht = {(0, 0)}
    stack = [(0, 0)]
    wand.discard((1, 1))
    while stack:
        cx, cz = stack[-1]
        nb = [(cx + dx, cz + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= cx + dx < n and 0 <= cz + dz < n and (cx + dx, cz + dz) not in besucht]
        if not nb:
            stack.pop()
            continue
        nx, nz = nb[int(rng.integers(len(nb)))]
        wand.discard((2 * nx + 1, 2 * nz + 1))
        wand.discard((cx + nx + 1, cz + nz + 1))
        besucht.add((nx, nz))
        stack.append((nx, nz))
    wand.discard((n, 0))
    wand.discard((n, 2 * n))
    off = -n
    pts = [(gx + off, gz + off) for (gx, gz) in wand]
    heckenring(w, pts, 2 + (g >= 2), "azalea" if _stil(seed) == 0 else "flowering_azalea")
    kiesweg(w, [(x, z) for x in range(-n, n + 1) for z in range(-n, n + 1) if (x, z) not in set(pts)])
    w.setze(0, 1, 0, w.b("water", level=0)) if (0, 0) not in set(pts) else None
    for (x, z) in ((-n - 1, -n - 1), (n + 1, -n - 1), (-n - 1, n + 1), (n + 1, n + 1)):
        parklaterne(w, x, z)
    return w


def rosenpavillon(seed, g=1):
    """Rosenpavillon: achteckiger weißer Pavillon mit Kuppeldach, umrankt von Rosen, Bänke und Rosenbeete."""
    w = _welt(seed)
    u = U[g]
    a = _r(3 * u + 2, 3)
    gelaende(w, a + 8, art="wiese", dichte=0.4)
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            if abs(x) + abs(z) <= 2 * a + 1:
                w.setze(x, 1, z, w.b("smooth_quartz") if (x + z) % 2 else w.b("polished_diorite"))
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if abs(x) + abs(z) == 2 * a or (abs(x) == a and abs(z) == a):
                for y in range(2, 6):
                    w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
                if (x + z) % 2:
                    w.setze(x, 2, z + (1 if z >= 0 else -1), w.b("rose_bush", half="lower"))
                    w.setze(x, 3, z + (1 if z >= 0 else -1), w.b("rose_bush", half="upper"))
    from wueste_eis import kuppel
    kuppel(w, lambda x, y, z, t: w.b("white_terracotta") if (x + y) % 3 else w.b("pink_terracotta"), 0, 0, 6, a + 0.8,
           form="zwiebel" if _stil(seed) else "rund", spitze="gold_block")
    for i in range(8):
        a2 = i / 8 * 2 * math.pi
        x, z = round(math.cos(a2) * (a + 5)), round(math.sin(a2) * (a + 5))
        blumenbeet(w, [(x, z), (x + 1, z), (x, z + 1)], ["red_tulip", "pink_tulip", "poppy"])
    hohl(w, 2)
    return w


def springbrunnen(seed, g=1):
    """Springbrunnen-Platz: dreistufiger Brunnen mit Wasserfontäne, umgeben von Blumenrabatten und Bänken."""
    from weltwunder4 import himmelsbrunnen
    return himmelsbrunnen(seed, max(0, g - 1))


def barockgarten(seed, g=2):
    """Barockgarten: symmetrische Parterres mit Buchsornamenten, Kegelbäumen, Kieswegen, Statuen und Wasserbecken."""
    w = _welt(seed)
    u = U[g]
    a = _r(12 * u + 5)
    gelaende(w, a + 4, art="wiese", dichte=0.2)
    rng = w.rng
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            weg = abs(x) <= 1 or abs(z) <= 1 or abs(abs(x) - abs(z)) <= 0
            if weg:
                kiesweg(w, [(x, z)])
                continue
            q = (abs(x) + abs(z)) % 6
            if max(abs(x), abs(z)) == a:
                w.setze(x, 1, z, MB.hecke(w, "azalea", east=True, west=True, north=True, south=True))
            elif q == 0:
                w.setze(x, 1, z, laub(w, "azalea"))
            elif q == 3:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
                w.setze(x, 1, z, w.b(BLUMEN[(abs(x) // 3 + abs(z) // 3) % len(BLUMEN)]))
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * a // 2, sz * a // 2
            for y in range(1, 5):
                for xx, zz in scheibe(1.5 - y * 0.3, cx, cz):
                    w.setze(xx, y, zz, laub(w, "oak"))
    for x, z in scheibe(3):
        w.setze(x, 0, z, w.b("water", level=0))
    for x, z in kreisrand(3.5):
        w.setze(x, 1, z, w.b("quartz_slab", type="bottom", waterlogged=False))
    return w


def teichpark(seed, g=1):
    """Teichpark: geschwungener Teich mit Seerosen und Schilf, Holzsteg, Trauerweiden, Bootshäuschen."""
    w = _welt(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R + 4, art="wiese", dichte=0.5)
    from fernost import teich
    teich(w, 0, 0, R * 0.6)
    for z in range(-int(R * 0.6), int(R * 0.6)):
        for x in (2, 3):
            w.setze(x, 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    import baeume as B
    for i in range(2 + g):
        a = i / (2 + g) * 2 * math.pi + 0.5
        einfuegen(w, B.ARTEN["trauerweide"][1](int(w.rng.integers(1, 10 ** 6)), 0),
                  round(math.cos(a) * R * 0.8), 0, round(math.sin(a) * R * 0.8))
    parkbank(w, -R // 2, R // 2 + 2, "north")
    return w


def rosenallee(seed, g=1):
    """Rosenallee: Laubengang aus Rosenbögen über einem Kiesweg, an beiden Seiten Rosenstöcke und Laternen."""
    w = _welt(seed)
    u = U[g]
    L = _r(10 * u + 6)
    gelaende(w, L + 4, art="wiese", dichte=0.3)
    kiesweg(w, [(x, z) for x in range(-2, 3) for z in range(-L, L + 1)])
    for z in range(-L, L + 1, 3):
        for x in (-3, 3):
            for y in range(1, 4):
                w.setze(x, y, z, w.b("dark_oak_fence", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
        for x in range(-3, 4):
            w.setze(x, 4, z, laub(w, "flowering_azalea") if abs(x) < 3 else laub(w, "azalea"))
        w.setze(0, 5, z, w.b("rose_bush", half="lower")) if False else None
        for x in (-4, 4):
            w.setze(x, 1, z, w.b("rose_bush", half="lower"))
            w.setze(x, 2, z, w.b("rose_bush", half="upper"))
    for z in range(-L, L + 1, 6):
        parklaterne(w, 5, z)
    return w


def gewaechshaus(seed, g=1):
    """Gewächshaus: Glaspalast mit Eisenrahmen, darin Palmen, Farne und Blumen, Brunnen in der Mitte."""
    w = _welt(seed)
    u = U[g]
    a, b = _r(7 * u + 3, 5), _r(4 * u + 2, 3)
    H = _r(5 * u + 3, 4)
    gelaende(w, a + 6, art="wiese", dichte=0.3)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.setze(x, 0, z, w.b("grass_block", snowy=False) if abs(z) > 1 else w.b("polished_andesite"))
            for y in range(1, H + 1):
                if x in (-a, a) or z in (-b, b):
                    w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                         waterlogged=False) if (x + z) % 4 == 0 or y == H else w.b("glass"))
    for k in range(b + 2):
        for x in range(-a, a + 1):
            for z in (-b + k, b - k):
                w.setze(x, H + 1 + k, z, w.b("glass") if x % 4 else w.b("iron_block"))
    import wald
    for x in range(-a + 2, a - 1, 4):
        for z in (-b + 2, b - 2):
            einfuegen(w, wald.palme(int(w.rng.integers(1, 10 ** 6)), H=H - 1), x, 0, z)
    for x in range(-a + 1, a):
        for z in (-b + 1, b - 1):
            if w.frei(x, 1, z):
                w.setze(x, 1, z, w.b(BLUMEN[(x + z) % len(BLUMEN)]))
    hohl(w, 2)
    return w


def japanischer_garten(seed, g=1):
    """Japanischer Garten: Teich mit Koi, Steinlaternen, Kiesgarten, Ahorne in Herbstfarben (BOP-Laub) und Teehaus."""
    from fernost import teehaus
    w = teehaus(seed, g)
    import wald
    for i in range(3):
        einfuegen(w, wald.kleiner_laubbaum(int(w.rng.integers(1, 10 ** 6)), "oak", blaetter=[("oak", 0.3)], breit=1.0),
                  -8 + i * 4, 0, 8)
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) == "minecraft:oak_leaves" and w.rng.random() < 0.8:
            w.bloecke[(x, y, z)] = MB.herbstlaub(w, ["maple", "orange_autumn"][int(w.rng.integers(2))])
    return w


def obstgarten(seed, g=1):
    """Obstgarten: Reihen von Obstbäumen, Bienenstöcke, Leitern, Körbe voller Äpfel und eine Saftpresse."""
    w = _welt(seed)
    u = U[g]
    import wald
    n = 2 + g
    A = 9
    gelaende(w, n * A // 2 + 6, art="wiese", dichte=0.5)
    arten = [[("oak", 0.7), ("flowering_azalea", 0.3)], [("birch", 0.6), ("flowering_azalea", 0.4)],
             [("cherry", 0.8), ("oak", 0.2)]]
    for i in range(n):
        kiesweg(w, [(-n * A // 2 + i * A + A // 2, z) for z in range(-n * A // 2, n * A // 2)])
        for j in range(n):
            x, z = -n * A // 2 + i * A + 2, -n * A // 2 + j * A + 2
            einfuegen(w, wald.kleiner_laubbaum(int(w.rng.integers(1, 10 ** 6)), "oak", H=3 + g // 2,
                                               blaetter=arten[(i + seed) % 3], breit=0.7), x, 0, z)
            if (i + j) % 3 == 0:
                w.setze(x + 3, 1, z, MB.korb(w))
            if (i * 3 + j) % 4 == 1:
                w.setze(x, 1, z + 3, w.b("ladder", facing="north", waterlogged=False))
    w.setze(0, 1, n * A // 2 + 3, w.b("beehive", facing="south", honey_level=3))
    w.setze(2, 1, n * A // 2 + 3, w.b("bee_nest", facing="south", honey_level=2))
    w.setze(-2, 1, n * A // 2 + 3, w.b("barrel", facing="up", open=False))
    return w


def kraeutergarten(seed, g=0):
    """Kräutergarten: Hochbeete mit Kräutern, Weidenzaun, Kräuterspirale aus Stein und Gartenhäuschen."""
    w = _welt(seed)
    u = U[g]
    a = _r(5 * u + 3, 4)
    gelaende(w, a + 5, art="wiese", dichte=0.3)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if max(abs(x), abs(z)) == a:
                w.setze(x, 1, z, MB.lattenzaun(w, "spruce", north=abs(x) == a, south=abs(x) == a, east=abs(z) == a,
                                               west=abs(z) == a))
            elif x % 3 != 0 and abs(z) < a - 1:
                w.setze(x, 1, z, w.b("rooted_dirt"))
                w.setze(x, 2, z, w.b(["fern", "lily_of_the_valley", "allium", "azure_bluet", "sweet_berry_bush"][(x + z) % 5])
                        if (x + z) % 5 != 4 else w.b("sweet_berry_bush", age=2))
    for k in range(10):
        a2 = k / 10 * 2 * math.pi * 1.5
        x, z = round(math.cos(a2) * (1 + k * 0.2)), round(math.sin(a2) * (1 + k * 0.2))
        w.setze(x + a + 3, 1 + k // 4, z, w.b("mossy_cobblestone"))
    return w


def pergola(seed, g=1):
    """Pergola-Terrasse: Holzpergola mit Weinlaub, Steinterrasse, Tisch und Stühlen, Blumenkübel."""
    w = _welt(seed)
    u = U[g]
    a, b = _r(5 * u + 3, 4), _r(3 * u + 2, 3)
    gelaende(w, a + 5, art="wiese", dichte=0.3)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.setze(x, 0, z, MB.pflaster(w, "sandstone", "flagstone") if (x + z) % 2 else w.b("smooth_sandstone"))
            if x in (-a, a) and z in (-b, b, 0):
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("stripped_oak_log", axis="y"))
            if x % 2 == 0:
                w.setze(x, 4, z, w.b("stripped_oak_log", axis="z"))
            elif (x + z) % 3:
                w.setze(x, 4, z, laub(w, "jungle") if (x + z) % 2 else laub(w, "flowering_azalea"))
    w.setze(0, 1, 0, w.b("oak_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(0, 2, 0, w.b("oak_pressure_plate", powered=False))
    for dx in (-1, 1):
        w.setze(dx, 1, 0, w.b("oak_stairs", facing="east" if dx < 0 else "west", half="bottom", shape="straight",
                              waterlogged=False))
    return w


def statuengarten(seed, g=2):
    """Statuengarten: Allee aus Marmorstatuen auf Sockeln zwischen Kegelhecken, am Ende eine Exedra."""
    from motive import figur
    w = _welt(seed)
    u = U[g]
    n = 2 + g
    L = n * 5
    gelaende(w, L + 6, art="wiese", dichte=0.3)
    kiesweg(w, [(x, z) for x in range(-2, 3) for z in range(-L, L + 1)])
    posen = ["denker", "stab", "arme_hoch", "schwert", "stehend"]
    for i in range(n):
        z = -L + 3 + i * 10
        for sx in (-1, 1):
            x = sx * 6
            for y in (1, 2):
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        w.setze(x + dx, y, z + dz, w.b("polished_andesite") if y == 1 else w.b("smooth_quartz"))
            S = Skulptur(w, 0.4 + 0.06 * g)
            S.mat("k", sk(Mat(w, ["smooth_quartz", "calcite", "polished_diorite"]), 0, 10))
            S.mat("a", bl(w, "gold_block"))
            S.mat("d", bl(w, "smooth_quartz"))
            S.mat("g", bl(w, "sea_lantern"))
            figur(S, ["mensch", "elf", "ritter", "mensch"][(i + (sx > 0)) % 4], posen[(i * 2 + (sx > 0)) % len(posen)])
            S.rendern((-6, -1, -4), (6, 22, 4), versatz=(x + 0.5, 3.01, z + 0.5), dreh=dreh_y(math.pi / 2 * -sx))
            for y in range(1, 4):
                for xx, zz in scheibe(1.4 - y * 0.35, x, z + 5):
                    w.setze(xx, y, zz, laub(w, "azalea"))
    # Exedra: halbrunde Säulenbank am Ende der Allee
    for x, z in kreisrand(5.5, 0, L + 1):
        if z >= L + 1:
            w.setze(x, 1, z, w.b("quartz_stairs", facing="north" if abs(x) < 3 else ("east" if x < 0 else "west"),
                                 half="bottom", shape="straight", waterlogged=False))
            if (x + z) % 3 == 0:
                for y in range(2, 5):
                    w.setze(x, y, z + 1, w.b("quartz_pillar", axis="y"))
                w.setze(x, 5, z + 1, w.b("quartz_slab", type="bottom", waterlogged=False))
    hohl(w, 2)
    return w


def bluehwiese(seed, g=1):
    """Blühwiese mit Bienenhotel: wilde Blumen in Farbinseln, Bienenstöcke, ein Holzsteg und Trittsteine."""
    w = _welt(seed)
    u = U[g]
    R = _r(10 * u + 5)
    r_n = Rauschen(w, 3)
    gelaende(w, R + 3, art="wiese", dichte=0.2)
    for x, z in scheibe(R):
        v = int(r_n(x, 0, z) * len(BLUMEN))
        if w.frei(x, 1, z) and w.rng.random() < 0.7:
            w.setze(x, 1, z, w.b(BLUMEN[v % len(BLUMEN)]))
    for k in range(3):
        for y in (1, 2):
            w.setze(k - 1, y, 0, w.b("bee_nest", facing="south", honey_level=k) if y == 2 else w.b("oak_planks"))
    return w


def baumhaus_park(seed, g=1):
    """Abenteuerspielplatz: Baumhaus, Rutsche aus Kupfer, Schaukel, Sandkasten und Kletterturm."""
    w = _welt(seed)
    u = U[g]
    gelaende(w, _r(10 * u + 5), art="wiese", dichte=0.3)
    for x in range(-3, 4):
        for z in range(-3, 4):
            w.setze(x + 6, 0, z, w.b("sand"))
        w.setze(x + 6, 1, -4, w.b("oak_planks"))
    for y in range(1, 6):
        for x, z in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            w.setze(x, y, z, w.b("oak_log", axis="y"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, 5, z, w.b("oak_planks"))
    for k in range(5):
        w.setze(3 + k, 5 - k, 0, w.b("waxed_cut_copper_slab", type="bottom", waterlogged=False))
    for x in (-7, -3):
        for y in range(1, 5):
            w.setze(x, y, 5, w.b("oak_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    for x in range(-7, -2):
        w.setze(x, 5, 5, w.b("oak_log", axis="x"))
    for y in (3, 4):
        w.setze(-5, y, 5, w.b("chain", axis="y", waterlogged=False))
    w.setze(-5, 2, 5, w.b("oak_slab", type="bottom", waterlogged=False))
    return w


def stadtpark(seed, g=2):
    """Stadtpark: geschwungene Wege, Rasenflächen, alte Bäume, Bänke, Laternen, Musikpavillon und Teich."""
    import wald
    w = _welt(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R + 2, art="wiese", dichte=0.3)
    for t in range(0, 360, 2):
        a = math.radians(t)
        rr = R * 0.6 + R * 0.15 * math.sin(a * 3)
        kiesweg(w, [(round(math.cos(a) * rr + d), round(math.sin(a) * rr)) for d in (-1, 0, 1)])
    for i in range(5 + g * 2):
        a = w.rng.random() * 2 * math.pi
        dd = R * (0.15 if i % 2 else 0.85)
        einfuegen(w, wald._baum(int(w.rng.integers(1, 10 ** 6)), "eiche", 0), round(math.cos(a) * dd), 0,
                  round(math.sin(a) * dd))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        parklaterne(w, round(math.cos(a) * (R * 0.6 + 2)), round(math.sin(a) * (R * 0.6 + 2)))
    return w


def zierteich(seed, g=0):
    """Kleiner Zierteich mit Steinrand, Seerosen, Schilf, Trittsteinen und einer Froschstatue."""
    w = _welt(seed)
    from fernost import teich
    gelaende(w, 9, art="wiese", dichte=0.4)
    teich(w, 0, 0, 4)
    w.setze(5, 1, 0, w.b("lime_terracotta"))
    w.setze(5, 2, 0, w.b("green_terracotta"))
    return w


def irrgarten_rund(seed, g=2):
    """Runder Heckengarten mit konzentrischen Ringen, Durchgängen und einem Turmpavillon in der Mitte."""
    w = _welt(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R + 3, art="wiese", dichte=0.2)
    rng = w.rng
    for ring in range(3, R + 1, 3):
        offen = rng.random() * 2 * math.pi
        pts = [(x, z) for x, z in kreisrand(ring) if abs(math.atan2(z, x) - offen) > 0.25]
        heckenring(w, pts, 2, "azalea" if ring % 2 else "flowering_azalea")
    st = P.Stil(w, wand="marmor", sockel="kalkstein", gesims="quartz", dach="mcw_gruen", holz="birch", laeden=False)
    P.turm(w, st, 0, 0, 1, _r(6 * u + 4), 1.5, dach="glocke", krone=False, fahne=None)
    return w


def schmetterlingshaus(seed, g=1):
    """Schmetterlingshaus: runde Glaskuppel voller blühender Azaleen, Blumen und Leuchtlaternen."""
    w = _welt(seed)
    u = U[g]
    R = 5 * u + 3
    gelaende(w, _r(R + 5), art="wiese", dichte=0.3)
    S = Skulptur(w, 1.0)
    S.mat("g", lambda x, y, z, *a: w.b("glass") if (x + z) % 4 else w.b("white_stained_glass"))
    S.plus(lambda X, Y, Z: (np.abs(np.sqrt(X * X + Y * Y + Z * Z) - R) < 0.55) & (Y >= 0), "g")
    S.rendern((-R - 1, 0, -R - 1), (R + 1, R + 1, R + 1), versatz=(0.5, 1, 0.5))
    for x, z in scheibe(R - 1):
        w.setze(x, 0, z, w.b("moss_block"))
        r = w.rng.random()
        if r < 0.3:
            w.setze(x, 1, z, laub(w, "flowering_azalea"))
        elif r < 0.6:
            w.setze(x, 1, z, w.b(BLUMEN[int(w.rng.integers(len(BLUMEN)))]))
    w.setze(0, int(R), 0, MB.laterne(w, "chain_lantern", haengend=True))
    for y, half in ((1, "lower"), (2, "upper")):
        w.bloecke.pop((0, y, round(R)), None)
    return w


def kaskadengarten(seed, g=2):
    """Kaskadengarten: Wassertreppe über mehrere Terrassen, flankiert von Balustraden, Kegelbäumen und Vasen,
    unten ein Becken mit Fontäne."""
    w = _welt(seed)
    u = U[g]
    n = 3 + g
    B = _r(3 * u + 2, 3)
    T = 5
    gelaende(w, n * T // 2 + B + 8, art="wiese", dichte=0.3)
    stein = Mat(w, ["smooth_stone", "polished_andesite", "stone_bricks"] if _stil(seed) else
                ["smooth_sandstone", "cut_sandstone", "sandstone"], kontrast=0.6)
    for i in range(n):
        y = 2 * (n - i)
        z0 = -n * T // 2 + i * T
        for z in range(z0, z0 + T):
            for x in range(-B - 4, B + 5):
                for yy in range(1, y + 1):
                    w.setze(x, yy, z, stein(x, yy, z, yy / (2 * n + 1)) if abs(x) <= B or yy < y else
                            w.b("grass_block", snowy=False))
                if abs(x) <= B - 1:
                    w.setze(x, y, z, w.b("water", level=0))
                elif abs(x) == B:
                    w.setze(x, y + 1, z, _wand(w, "stone_brick_wall" if _stil(seed) else "sandstone_wall"))
                elif abs(x) == B + 3 and z == z0 + 2:
                    for k in range(1, 4):
                        for xx, zz in scheibe(1.3 - k * 0.3, x, z):
                            w.setze(xx, y + k, zz, laub(w, "azalea"))
                elif abs(x) == B + 2 and z == z0:
                    w.setze(x, y + 1, z, w.b("decorated_pot", facing="north", cracked=False, waterlogged=False))
    zb = n * T // 2
    for x, z in scheibe(B + 3, 0, zb + B + 2):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("prismarine_bricks") if _stil(seed) else w.b("smooth_sandstone"))
    for x, z in kreisrand(B + 3.5, 0, zb + B + 2):
        w.setze(x, 1, z, w.b("smooth_stone_slab" if _stil(seed) else "smooth_sandstone_slab", type="bottom",
                             waterlogged=False))
    cz = zb + B + 2
    for y in range(1, 4):
        w.setze(0, y, cz, w.b("smooth_stone" if _stil(seed) else "chiseled_sandstone"))
    w.setze(0, 4, cz, w.b("water", level=0))
    hohl(w, 2)
    return w


def musikpavillon(seed, g=1):
    """Musikpavillon: sechseckiger Pavillon mit Holzbühne, Zierschnitzerei, Laternen und Stuhlreihen davor."""
    w = _welt(seed)
    u = U[g]
    R = 3 * u + 3
    gelaende(w, _r(R + 12), art="wiese", dichte=0.3)
    holz = "dark_oak" if _stil(seed) else "spruce"
    for x, z in scheibe(R + 0.5):
        w.setze(x, 1, z, w.b(f"{holz}_planks"))
        w.setze(x, 0, z, w.b("stone_bricks"))
    ecken = [(round(math.cos(a) * R), round(math.sin(a) * R)) for a in np.linspace(0, 2 * math.pi, 7)[:-1]]
    H = _r(4 * u + 2, 4)
    for (x, z) in ecken:
        for y in range(2, H + 2):
            w.setze(x, y, z, w.b(f"stripped_{holz}_log", axis="y") if y < H + 1 else w.b(f"{holz}_planks"))
        w.setze(x, H, z + (1 if z < 0 else -1), w.b(f"{holz}_trapdoor", facing="north" if z > 0 else "south",
                                                       half="top", open=True, powered=False, waterlogged=False))
    for x, z in kreisrand(R + 0.5):
        if (x, z) not in ecken and z < R - 1:
            w.setze(x, 2, z, w.b(f"{holz}_fence", north=True, south=True, east=True, west=True, waterlogged=False))
    D = P.Dach(w, "mcw_gruen" if _stil(seed) else "mcw_rot")
    for k in range(_r(R) + 2):
        rr = R + 1 - k
        if rr <= 0:
            break
        for x, z in kreisrand(rr):
            f = ("west" if x > 0 else "east") if abs(x) >= abs(z) else ("north" if z > 0 else "south")
            w.setze(x, H + 2 + k, z, D.treppe(x, H + 2 + k, z, f))
        for x, z in scheibe(rr - 1):
            w.setze(x, H + 2 + k, z, D.voll(x, H + 2 + k, z))
    w.setze(0, H + 2 + _r(R) + 2, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    w.setze(0, H + 1, 0, MB.laterne(w, "chain_lantern", haengend=True))
    for reihe in range(3 + g):
        z = round(R) + 3 + reihe * 2
        for x in range(-round(R), round(R) + 1):
            if x != 0:
                w.setze(int(x), 1, z, w.b(f"{holz}_stairs", facing="north", half="bottom", shape="straight",
                                          waterlogged=False))
    hohl(w, 2)
    return w


PARKS = {
    "heckenlabyrinth": ("Heckenlabyrinth", heckenlabyrinth),
    "rosenpavillon": ("Rosenpavillon", rosenpavillon),
    "springbrunnen": ("Springbrunnen", springbrunnen),
    "barockgarten": ("Barockgarten", barockgarten),
    "teichpark": ("Teichpark", teichpark),
    "rosenallee": ("Rosenallee", rosenallee),
    "gewaechshaus": ("Gewächshaus", gewaechshaus),
    "japanischer_garten": ("Japanischer Garten", japanischer_garten),
    "obstgarten": ("Obstgarten", obstgarten),
    "kraeutergarten": ("Kräutergarten", kraeutergarten),
    "pergola": ("Pergola-Terrasse", pergola),
    "statuengarten": ("Statuengarten", statuengarten),
    "bluehwiese": ("Blühwiese", bluehwiese),
    "spielplatz": ("Abenteuerspielplatz", baumhaus_park),
    "stadtpark": ("Stadtpark", stadtpark),
    "zierteich": ("Zierteich", zierteich),
    "heckenrund": ("Runder Heckengarten", irrgarten_rund),
    "schmetterlingshaus": ("Schmetterlingshaus", schmetterlingshaus),
    "kaskadengarten": ("Kaskadengarten", kaskadengarten),
    "musikpavillon": ("Musikpavillon", musikpavillon),
}


# ============================================================================ MÜHLEN & HANDWERK


def _hw(w, seed):
    return dict(haus="fachwerk_rot" if _stil(seed) == 0 else "stein_schiefer",
                dach="mcw_ziegel" if _stil(seed) == 0 else "mcw_schiefer",
                holz="spruce" if _stil(seed) == 0 else "dark_oak")


def _stilhaus(w, d, **extra):
    dd = dict(H_.HAUSPOOL[d["haus"]])
    dd["dach"] = d["dach"]
    dd.update(extra)
    return P.Stil(w, **dd)


def windmuehle(seed, g=2):
    """Windmühle: achteckiger Turm mit drehbarer Kappe, vier großen Flügeln aus Segeltuch (Create-Segel als Mod-Block),
    Galerie, Mehlsäcke und Kornfeld."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    R = 3.5 * u + 2.5
    H = _r(14 * u + 6)
    gelaende(w, _r(R + 12), art="wiese")
    st = _stilhaus(w, d)
    P.turm(w, st, 0, 0, 1, H, R, form="achteck", dach="kegel", krone=False, fahne=None, fenster=6)
    for x, z in kreisrand(R + 1.5):
        w.setze(x, _r(H * 0.4), z, w.b(f"{d['holz']}_planks"))
        w.setze(x, _r(H * 0.4) + 1, z, w.b(f"{d['holz']}_fence", north=True, south=True, east=True, west=True,
                                            waterlogged=False))
    zy = H + _r(R)
    zz = round(R) + 2
    w.setze(0, zy, zz - 1, w.b(f"{d['holz']}_log", axis="z"))
    L = _r(10 * u + 4)
    for i in range(4):
        a = i * math.pi / 2 + 0.3
        for k in range(1, L + 1):
            x, y = round(math.cos(a) * k), round(zy + math.sin(a) * k)
            w.setze(x, y, zz, w.b(f"stripped_{d['holz']}_log", axis="x" if abs(math.cos(a)) > 0.7 else "y"))
            if k > 2:
                for q in (1, 2):
                    px = round(math.cos(a) * k - math.sin(a) * q)
                    py = round(zy + math.sin(a) * k + math.cos(a) * q)
                    w.setze(px, py, zz, MB.mod(w, "create:white_sail", "white_wool", facing="south"))
    H_.beet(w, -round(R) - 10, -6, -round(R) - 3, 6, "gemuese")
    for k in range(4):
        w.setze(round(R) + 2, 1, -2 + k, MB.mod(w, "supplementaries:sack", "white_wool", open=False))
    hohl(w, 2)
    return w


def wassermuehle(seed, g=2):
    """Wassermühle am Bach: Fachwerkhaus mit großem Wasserrad (Create-Wasserrad), Mühlgraben und Steg."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a, b = _r(5 * u + 3, 4), _r(4 * u + 2, 3)
    gelaende(w, a + 10, art="wiese")
    for x in range(-a - 10, a + 11):
        for z in range(b + 1, b + 5):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("gravel"))
    st = _stilhaus(w, d)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="sattel", tuer="west", kamine=1)
    Rr = _r(3 * u + 2, 3)
    cx, cy, cz = 0, Rr, b + 2
    for x in range(-Rr, Rr + 1):
        for y in range(-Rr, Rr + 1):
            r = math.hypot(x, y)
            if Rr - 1 <= r <= Rr + 0.3 or abs(x) == 0 or abs(y) == 0 and r <= Rr:
                w.setze(cx + x, cy + y, cz, w.b(f"stripped_{d['holz']}_log", axis="z") if r < Rr - 0.6 else
                        w.b(f"{d['holz']}_planks"))
    w.setze(cx, cy, cz, MB.wasserrad(w, "south"))
    w.setze(cx, cy, cz - 1, MB.welle(w, "z"))
    hohl(w, 2)
    return w


def schmiede(seed, g=1):
    """Dorfschmiede mit Esse, Amboss, Wassertrog und Wohnhaus."""
    return H_.schmiede(seed, g)


def saegewerk(seed, g=2):
    """Sägewerk: offene Halle mit Sägebank (Create-Säge als Deko-Welle), Stammstapeln, Bretterstapeln und Wasserrad."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a, b = _r(6 * u + 3, 5), _r(3 * u + 2, 3)
    gelaende(w, a + 10, art="wiese")
    for x in (-a, a):
        for z in range(-b, b + 1, 2):
            for y in range(1, 5):
                w.setze(x, y, z, w.b(f"{d['holz']}_log", axis="y"))
    P.satteldach(w, P.Dach(w, d["dach"]), -a, -b, a, b, 5, ue=1, first_x=True)
    for x in range(-a + 1, a):
        w.setze(x, 1, 0, w.b(f"stripped_{d['holz']}_log", axis="x"))
    w.setze(0, 2, 0, MB.mod(w, "create:mechanical_saw", "stonecutter", {"facing": "north"}, facing="up",
                            axis_along_first=True, flipped=False))
    Rr = 3
    for x in range(-Rr, Rr + 1):
        for y in range(-Rr, Rr + 1):
            r = math.hypot(x, y)
            if Rr - 0.7 <= r <= Rr + 0.3 or (r <= Rr and (x == 0 or y == 0)):
                w.setze(-a - 2 + 0 * x, Rr + 1 + y, x, w.b(f"{d['holz']}_planks") if r > Rr - 0.7 else
                        w.b(f"stripped_{d['holz']}_log", axis="x"))
    for x in range(-a - 1, 0):
        w.setze(x, Rr + 1, 0, MB.welle(w, "x"))
    for k in range(3):
        H_.holzstapel(w, a + 2, -b + k * 2, 5, d["holz"], "x") if False else None
        for x in range(a + 2, a + 7):
            for y in range(1, 3 - k % 2 + 1):
                w.setze(x, y, -b + k * 2, w.b(f"{d['holz']}_log", axis="x"))
    for x in range(-a - 6, -a - 1):
        for y in range(1, 4):
            w.setze(x, y, 0, w.b(f"{d['holz']}_planks") if y < 3 else w.b(f"{d['holz']}_slab", type="bottom",
                                                                           waterlogged=False))
    hohl(w, 2)
    return w


def brauerei(seed, g=2):
    """Brauerei: Backsteinbau mit Sudhaus-Turm, Kupferkesseln, Fasslager, Malzböden und Gaststube."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a, b = _r(6 * u + 3, 5), _r(4 * u + 2, 3)
    gelaende(w, a + 8, art="wiese")
    st = P.Stil(w, wand="backstein", sockel="graustein", gesims="brick", dach="mcw_schiefer", holz=d["holz"])
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="sattel", tuer="south", kamine=1)
    P.turm(w, st, a + 2, 0, 1, _r(16 * u + 6), 2.2, form="eckig", dach="pyramide", krone=False, fahne=None)
    for k in range(2):
        for x, z in kreisrand(1.5, -a - 4 - k * 4, 0):
            for y in range(1, 4):
                w.setze(x, y, z, w.b("waxed_copper_block") if y < 3 else w.b("waxed_cut_copper"))
    for i in range(8):
        w.setze(-a + i * 2, 1, b + 2, w.b("barrel", facing="east", open=False))
        w.setze(-a + i * 2, 2, b + 2, w.b("barrel", facing="east", open=False)) if i % 2 else None
    hohl(w, 2)
    return w


def kohlenmeiler(seed, g=1):
    """Kohlenmeiler: rauchender Erdhügel mit Holzscheit-Kern, Köhlerhütte, Holzstapel und Kohlesäcke."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    R = 4 * u + 3
    gelaende(w, _r(R + 8), art="wald")
    for x, z in scheibe(R):
        hh = int(R * 0.7 * (1 - (math.hypot(x, z) / R) ** 2))
        for y in range(1, hh + 1):
            w.setze(x, y, z, w.b("coarse_dirt") if y == hh else w.b("coal_block") if y < hh - 1 else w.b("dirt"))
        if hh > 1 and (x + z) % 5 == 0:
            w.setze(x, hh + 1, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    st = P.Stil(w, wand="holz_dunkel", sockel="graustein", gesims="stone_brick", dach="mcw_holz", holz="spruce")
    P.gebaeude(w, st, round(R) + 3, -2, round(R) + 7, 2, y0=1, etagen=1, eh=3, dach="sattel", tuer="west",
               gauben=False)
    return w


def toepferei(seed, g=1):
    """Töpferei: Werkstatt mit Brennofen aus Lehmziegeln, Töpferscheibe, Regalen voller Krüge und Tonlager."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 8, art="wiese")
    st = P.Stil(w, wand="lehm", sockel="graustein", gesims="mud_brick", dach="mcw_ziegel", holz=d["holz"], fachwerk=True)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=4, dach="sattel", tuer="south", kamine=0, gauben=False)
    for x, z in scheibe(2.5, a + 5, 0):
        for y in range(1, 5):
            if math.hypot(x - a - 5, z) + y * 0.5 < 3:
                w.setze(x, y, z, w.b("mud_bricks") if (x + y) % 2 else w.b("bricks"))
    w.setze(a + 5, 5, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for i in range(5):
        w.setze(-a + 1 + i, 1, b + 2, w.b("decorated_pot", facing="north", cracked=False, waterlogged=False))
    for k in range(4):
        w.setze(-a - 3, 1 + k // 2, -b + k % 2 * 2, w.b("clay"))
    return w


def imkerei(seed, g=1):
    """Imkerei: Bienenstand mit Reihen von Stöcken, Blumenwiese, Imkerhaus mit Honigfässern und Waben."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a = _r(5 * u + 3, 4)
    b2 = 3
    gelaende(w, a + 8, art="wiese", dichte=1.5)
    for x in range(-a, a + 1):
        w.setze(x, 1, 0, w.b(f"{d['holz']}_planks"))
        if x % 2 == 0:
            w.setze(x, 2, 0, w.b("beehive", facing="south", honey_level=int(w.rng.integers(0, 6))))
        w.setze(x, 4, 0, w.b(f"{d['holz']}_slab", type="bottom", waterlogged=False))
        w.setze(x, 4, 1, w.b(f"{d['holz']}_slab", type="bottom", waterlogged=False))
    for x in (-a, a):
        for y in (2, 3):
            w.setze(x, y, 1, w.b(f"{d['holz']}_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    for x, z in scheibe(a + 4):
        if z > 2 and w.frei(x, 1, z) and w.rng.random() < 0.5:
            w.setze(x, 1, z, w.b(BLUMEN[int(w.rng.integers(len(BLUMEN)))]))
    st = P.Stil(w, wand="holz_hell", sockel="graustein", gesims="stone_brick", dach="schindel_gruen" if _stil(seed)
                else "mcw_stroh", holz=d["holz"], blumen=1.0)
    P.gebaeude(w, st, -4, -b2 - 6, 4, -b2, y0=1, etagen=1, eh=4, dach="sattel", tuer="south", gauben=False)
    for k in range(5):
        w.setze(5 + k, 1, -b2 - 1, w.b("barrel", facing="up", open=False) if k % 2 else
                w.b("honey_block") if k == 2 else w.b("honeycomb_block"))
    for x in (-5, 5):
        w.setze(x, 2, -b2 + 1, w.b("candle", candles=3, lit=True, waterlogged=False)) if False else None
    return w


def gerberei(seed, g=1):
    """Gerberei: Haus mit Trockengestellen voller Häute (braune Wolle), Gerbbottichen (Kessel) und Bach."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 8, art="wiese")
    st = _stilhaus(w, d)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="sattel", tuer="south", kamine=1)
    for i in range(3):
        x = a + 3 + i * 3
        for y in (1, 2, 3):
            w.setze(x, y, -2, w.b(f"{d['holz']}_fence", north=False, south=False, east=False, west=False,
                                  waterlogged=False))
            w.setze(x, y, 2, w.b(f"{d['holz']}_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False))
        for z in range(-2, 3):
            w.setze(x, 4, z, w.b(f"{d['holz']}_fence", north=True, south=True, east=False, west=False, waterlogged=False))
            if -2 < z < 2:
                w.setze(x, 3, z, w.b(["brown_wool", "orange_wool", "white_wool"][i]))
    for k in range(3):
        w.setze(-a - 2, 1, -2 + k * 2, w.b("water_cauldron", level=3))
    return w


def glasblaeserei(seed, g=1):
    """Glasbläserei: Werkstatt mit glühendem Ofen, Regalen voller bunter Glasflaschen und Schaufenster."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 8, art="wiese")
    st = _stilhaus(w, d, fenster="glass_pane")
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=5, dach="sattel", tuer="south", kamine=1, gauben=False)
    farben = ["red", "orange", "yellow", "lime", "cyan", "blue", "purple", "magenta"]
    for x in range(-a + 1, a):
        w.setze(x, 2, b, w.b(f"{farben[(x + a) % len(farben)]}_stained_glass"))
    w.setze(0, 1, -b + 1, w.b("blast_furnace", facing="south", lit=True))
    return w


def muehlrad_saege(seed, g=2):
    """Hammerwerk am Fluss: Wasserrad treibt Hämmer (Create-Zahnräder als Deko), Esse, Amboss und Eisenbarren."""
    w = wassermuehle(seed, g)
    d = _hw(w, seed)
    for k in range(3):
        w.setze(-2 + k * 2, 5, 3, MB.zahnrad(w, "z", gross=k == 1))
    w.setze(-6, 1, 0, w.b("anvil", facing="north"))
    w.setze(-6, 1, 2, w.b("iron_block"))
    return w


def mine(seed, g=2):
    """Bergwerk: Stolleneingang mit Stützbalken, Förderturm mit Seilrad, Gleise, Loren und Erzhalden."""
    from elemente import schlackenmine
    w = schlackenmine(seed, g)
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if any(t in n for t in ("basalt", "blackstone", "magma", "soul", "tuff")):
            w.bloecke[(x, y, z)] = w.b(["stone", "andesite", "cobblestone", "gravel"][(x + y + z) % 4])
    return w


def schneiderei(seed, g=1):
    """Schneiderei: Laden mit Schaufenster, Stoffballen, Webstuhl, Kleiderständern und Markise."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 6, art="wiese")
    st = _stilhaus(w, d)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="sattel", tuer="south")
    for x in range(-a, a + 1):
        w.setze(x, 4, b + 1, MB.markise(w, ["red", "white"][x % 2], "south"))
    w.setze(-a + 1, 1, -b + 1, w.b("loom", facing="south"))
    for k in range(4):
        w.setze(a + 2, 1 + k // 2, -b + k % 2 * 2, w.b(["red_wool", "blue_wool", "yellow_wool", "green_wool"][k]))
    return w


def getreidespeicher(seed, g=2):
    """Getreidespeicher: hoher Fachwerkspeicher auf Steinstelzen, Lastenaufzug, Strohballen und Säcke."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 6, art="wiese")
    for x in range(-a, a + 1, 2):
        for z in (-b, b):
            for y in (1, 2):
                w.setze(x, y, z, w.b("stone_bricks") if y == 1 else w.b("mossy_cobblestone"))
    st = _stilhaus(w, d)
    P.gebaeude(w, st, -a, -b, a, b, y0=3, etagen=2 + (g >= 2), eh=4, dach="sattel", tuer="south", sockel_h=0, steil=True)
    for k in range(6):
        w.setze(-a + k, 1, b + 2, MB.stroh(w))
    return w


def schreinerei(seed, g=1):
    """Schreinerei: Werkstatt mit Werkbänken, Hobelbank, Stuhl- und Fassrohlingen und einem Holzlager."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 8, art="wiese")
    st = _stilhaus(w, d)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=4, dach="sattel", tuer="south", gauben=False)
    for k in range(3):
        w.setze(-a + 1 + k, 1, -b + 1, w.b("crafting_table"))
    for x in range(a + 2, a + 6):
        for y in (1, 2):
            w.setze(x, y, 0, w.b(f"{d['holz']}_planks"))
    w.setze(a + 2, 1, 2, w.b("barrel", facing="up", open=False))
    return w


def ziegelei(seed, g=2):
    """Ziegelei: Ringofen mit hohem Schlot, Trockenschuppen mit Lehmziegel-Reihen und Tongrube."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a, b = _r(6 * u + 3, 5), _r(3 * u + 2, 3)
    gelaende(w, a + 8, art="wiese")
    st = P.Stil(w, wand="backstein", sockel="graustein", gesims="brick", dach="mcw_ziegel", holz=d["holz"])
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=4, dach="walm", tuer="south", gauben=False, kamine=0)
    for y in range(1, _r(18 * u + 8)):
        for x, z in kreisrand(1.4 - y * 0.01, 0, -b - 3):
            w.setze(x, y, z, w.b("bricks"))
    for x in range(-a, a + 1):
        for z in range(b + 3, b + 7):
            if (x + z) % 2 == 0:
                w.setze(x, 1, z, w.b("mud_bricks") if z % 2 else w.b("packed_mud"))
    for x, z in scheibe(3, -a - 5, 0):
        w.setze(x, 0, z, w.b("clay"))
        w.setze(x, -1, z, w.b("clay"))
    hohl(w, 2)
    return w


def schmelzhuette(seed, g=2):
    """Schmelzhütte mit Create-Technik: großes Wasserrad treibt über Wellen und Zahnräder ein Gebläse,
    Backstein-Hochofen mit Kupfertanks, Mischer, Presse und Gusshalle."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a, b = _r(6 * u + 3, 5), _r(4 * u + 2, 3)
    gelaende(w, a + 12, art="wiese")
    for x in range(-a - 12, a + 13):
        for z in range(-b - 7, -b - 2):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("gravel"))
    st = P.Stil(w, wand="backstein", sockel="graustein", gesims="brick", dach="mcw_schwarz", holz="dark_oak")
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=6, dach="sattel", tuer="south", gauben=False, kamine=0)
    Hh = _r(14 * u + 6)
    for y in range(1, Hh):
        r = 2.6 - 1.2 * y / Hh
        for x, z in kreisrand(r, a + 4, 0):
            w.setze(x, y, z, w.b("bricks") if y % 5 else w.b("polished_blackstone_bricks"))
    w.setze(a + 4, Hh, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    w.setze(a + 4, 1, 0, w.b("blast_furnace", facing="west", lit=True))
    for k in range(2):
        x = -a - 3 - k * 3
        for y in range(1, 5):
            for dx in (0, 1):
                for dz in (0, 1):
                    w.setze(x + dx, y, dz - 1, MB.mod(w, "create:fluid_tank", "waxed_copper_block",
                                                      bottom=y == 1, top=y == 4, shape="window" if y in (2, 3) else "plain"))
    Rr = _r(2.5 * u + 2, 3)
    wz = -b - 4
    for x in range(-Rr, Rr + 1):
        for y in range(-Rr, Rr + 1):
            r = math.hypot(x, y)
            if Rr - 0.7 <= r <= Rr + 0.3 or (r <= Rr and (x == 0 or y == 0 or abs(x) == abs(y))):
                w.setze(x, Rr + y, wz, w.b(f"{d['holz']}_planks") if r > Rr - 0.7 else
                        w.b(f"stripped_{d['holz']}_log", axis="z"))
    w.setze(0, Rr, wz, MB.mod(w, "create:water_wheel", "spruce_log", {"axis": "z"}, facing="south"))
    for z in range(wz + 1, -b):
        w.setze(0, Rr, z, MB.welle(w, "z"))
    w.setze(0, Rr, -b - 1, MB.zahnrad(w, "z", gross=True))
    for k, x in enumerate(range(-a + 2, a - 1, 3)):
        w.setze(x, 7, -b + 1, MB.zahnrad(w, "z", gross=k % 2 == 0))
    w.setze(-2, 1, 0, MB.mod(w, "create:basin", "cauldron", facing="down"))
    w.setze(-2, 3, 0, MB.mod(w, "create:mechanical_mixer", "iron_block"))
    w.setze(2, 1, 0, MB.mod(w, "create:depot", "smooth_stone_slab", {"type": "bottom", "waterlogged": False},
                            waterlogged=False))
    w.setze(2, 3, 0, MB.mod(w, "create:mechanical_press", "piston", {"facing": "down", "extended": False},
                            facing="north"))
    w.setze(0, 1, -b + 2, MB.mod(w, "create:encased_fan", "dispenser", {"facing": "east", "triggered": False},
                                 facing="east"))
    hohl(w, 2)
    return w


def faerberei(seed, g=1):
    """Färberei am Fluss: Fachwerkhaus, Färbebottiche (Kessel), bunte Tuchbahnen an Trockengestellen,
    Farbpflanzen-Beete und Steg ins Wasser."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 10, art="wiese")
    for x in range(-a - 10, a + 11):
        for z in range(b + 6, b + 10):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("clay") if (x + z) % 3 else w.b("gravel"))
    st = _stilhaus(w, d)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="sattel", tuer="south", kamine=1)
    farben = ["red", "yellow", "blue", "purple", "orange", "lime", "cyan", "magenta"]
    for i in range(3 + g):
        x0 = a + 3 + i * 3
        for y in range(1, 6):
            for z in (-3, 3):
                w.setze(x0, y, z, w.b(f"{d['holz']}_fence", north=False, south=False, east=False, west=False,
                                      waterlogged=False))
        for z in range(-3, 4):
            w.setze(x0, 6, z, w.b(f"stripped_{d['holz']}_log", axis="z"))
            if -3 < z < 3:
                for y in range(6 - 2 - (z + i) % 2, 6):
                    w.setze(x0, y, z, w.b(f"{farben[(i * 2 + (z > 0)) % len(farben)]}_wool"))
    for k in range(4):
        x = -a + k * 2
        w.setze(x, 1, b + 3, w.b("water_cauldron", level=3))
        w.setze(x, 1, b + 4, w.b(f"{farben[k]}_concrete_powder"))
    H_.beet(w, -a - 8, -b, -a - 3, b, "blumen")
    for z in range(b + 5, b + 9):
        w.setze(0, 1, z, w.b(f"{d['holz']}_slab", type="bottom", waterlogged=False))
    hohl(w, 2)
    return w


def steinmetz(seed, g=1):
    """Steinmetzhütte: offener Bauhof mit Rohblöcken, halbfertiger Statue, Säulentrommeln, Werkzeug und Kran."""
    from motive import figur
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a = _r(6 * u + 4, 6)
    gelaende(w, a + 8, art="wiese", dichte=0.2)
    rng = w.rng
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if rng.random() < 0.5:
                w.setze(x, 0, z, w.b(["gravel", "cobblestone", "andesite", "diorite"][int(rng.integers(4))]))
    roh = ["stone", "diorite", "calcite", "andesite", "smooth_stone", "tuff"]
    for i in range(6 + 2 * g):
        x, z = int(rng.integers(-a + 1, a)), int(rng.integers(-a + 1, 0))
        for dx in range(2):
            for dz in range(2):
                for y in range(1, 2 + (i % 2)):
                    w.setze(x + dx, y, z + dz, w.b(roh[i % len(roh)]))
    for k in range(3):
        for y in range(1, 3 - k % 2):
            w.setze(a - 2, y, 2 + k * 2, w.b("quartz_pillar", axis="y"))
        w.setze(a - 2 - k, 1, a - 1, w.b("quartz_pillar", axis="x"))
    S = Skulptur(w, 0.35 + 0.05 * g)
    S.mat("k", sk(Mat(w, ["calcite", "smooth_quartz", "diorite"]), 0, 10))
    S.mat("a", bl(w, "calcite"))
    S.mat("d", bl(w, "calcite"))
    S.mat("g", bl(w, "calcite"))
    figur(S, "mensch", "stehend")
    S.teile.append((lambda X, Y, Z: Y < 9, "k"))
    S.rendern((-6, -1, -4), (6, 22, 4), versatz=(0.5, 1.01, 3.5))
    for y in range(1, 9):
        for x in (-3, 3):
            w.setze(x, y, 3, w.b(f"{d['holz']}_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False) if y < 8 else w.b(f"{d['holz']}_planks"))
    for x in range(-3, 4):
        w.setze(x, 9, 3, w.b(f"{d['holz']}_slab", type="bottom", waterlogged=False))
    w.setze(-a + 1, 1, a - 1, w.b("stonecutter", facing="north"))
    w.setze(-a + 2, 1, a - 1, w.b("grindstone", face="floor", facing="north"))
    st = P.Stil(w, wand="holz_dunkel", sockel="graustein", gesims="stone_brick", dach="mcw_schiefer", holz=d["holz"])
    P.gebaeude(w, st, -a - 1, a + 1, -a + 5, a + 5, y0=1, etagen=1, eh=3, dach="pult" if False else "sattel",
               tuer="east", gauben=False, kamine=0)
    hohl(w, 2)
    return w


def baeckerei(seed, g=1):
    """Dorfbäckerei: Fachwerkhaus mit großem Backofen-Anbau aus Ziegeln, Brezel-Schild, Mehlsäcke,
    Brotkörbe vor dem Laden und Holzlager für den Ofen."""
    w = _welt(seed)
    d = _hw(w, seed)
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 8, art="wiese")
    st = _stilhaus(w, d)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="sattel", tuer="south", kamine=0)
    for x in range(a + 1, a + 6):
        for z in range(-2, 3):
            hh = 4 - (abs(z) == 2) - (x == a + 5)
            for y in range(1, hh + 1):
                w.setze(x, y, z, w.b("bricks") if (x + y + z) % 5 else w.b("mud_bricks"))
    for y in range(5, 5 + _r(5 * u + 3)):
        w.setze(a + 3, y, 0, w.b("bricks"))
    w.setze(a + 3, 5 + _r(5 * u + 3), 0, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                              waterlogged=False))
    w.setze(a + 3, 1, 2, w.b("smoker", facing="south", lit=True))
    w.setze(a + 4, 1, 2, w.b("furnace", facing="south", lit=True))
    for x in range(-a, a + 1):
        w.setze(x, 4, b + 1, MB.markise(w, ["brown", "white"][x % 2], "south"))
    for k in range(3):
        w.setze(-a + 1 + k * 2, 1, b + 2, MB.korb(w))
        w.setze(-a + 2 + k * 2, 1, b + 2, MB.mod(w, "supplementaries:sack", "white_wool", open=False))
    H_.holzstapel(w, a + 2, -b - 2, 4, d["holz"], "x")
    hohl(w, 2)
    return w


HANDWERK = {
    "windmuehle": ("Windmühle", windmuehle),
    "wassermuehle": ("Wassermühle", wassermuehle),
    "schmiede": ("Dorfschmiede", schmiede),
    "saegewerk": ("Sägewerk", saegewerk),
    "brauerei": ("Brauerei", brauerei),
    "kohlenmeiler": ("Kohlenmeiler", kohlenmeiler),
    "toepferei": ("Töpferei", toepferei),
    "imkerei": ("Imkerei", imkerei),
    "gerberei": ("Gerberei", gerberei),
    "glasblaeserei": ("Glasbläserei", glasblaeserei),
    "hammerwerk": ("Hammerwerk", muehlrad_saege),
    "bergwerk": ("Bergwerk", mine),
    "schneiderei": ("Schneiderei", schneiderei),
    "getreidespeicher": ("Getreidespeicher", getreidespeicher),
    "schreinerei": ("Schreinerei", schreinerei),
    "ziegelei": ("Ziegelei", ziegelei),
    "schmelzhuette": ("Schmelzhütte", schmelzhuette),
    "faerberei": ("Färberei", faerberei),
    "steinmetz": ("Steinmetzhütte", steinmetz),
    "baeckerei": ("Bäckerei", baeckerei),
}


# ============================================================================ KÜSTE & LEUCHTTÜRME


def strand(w, R, cx=0, cz=0, meer_ab=0):
    """Strand: Sand, Kies, Muscheln (Twigs), Treibholz, Seegras im Wasser ab z > meer_ab."""
    rng = w.rng
    for x, z in scheibe(R, cx, cz):
        if z > meer_ab:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("sand"))
            if rng.random() < 0.08:
                w.setze(x, -1, z, w.b("gravel"))
        else:
            w.setze(x, 0, z, w.b("sand") if z > meer_ab - 6 else w.b("grass_block", snowy=False))
            if z > meer_ab - 6 and w.frei(x, 1, z):
                r = rng.random()
                if r < 0.03:
                    w.setze(x, 1, z, MB.muschel(w))
                elif r < 0.05:
                    w.setze(x, 1, z, MB.kiesel(w))


def leuchtturm(seed, g=2):
    """Leuchtturm: rot-weiß geringelter Turm auf Felsen, Galerie mit Geländer, Laternenhaus mit Leuchtfeuer,
    Wärterhaus und Steg."""
    w = _welt(seed)
    u = U[g]
    R = 3 * u + 2
    H = _r(22 * u + 8)
    strand(w, _r(R + 14), meer_ab=4)
    fels = Mat(w, ["stone", "andesite", "cobblestone", "mossy_cobblestone", "diorite"], kontrast=1.3)
    for x, z in scheibe(R + 4):
        for y in range(0, 3):
            if math.hypot(x, z) + y * 1.2 < R + 4:
                w.setze(x, y, z, fels(x, y, z, y / 3))
    farben = ["white_concrete", "red_concrete"] if _stil(seed) == 0 else ["white_concrete", "black_concrete"]
    for y in range(3, H):
        r = R * (1 - 0.25 * (y / H))
        for x, z in kreisrand(r):
            fen = y % 6 == 3 and (x == 0 or z == 0)
            w.setze(x, y, z, w.b("glass_pane", north=True, south=True, east=True, west=True, waterlogged=False) if fen
                    else w.b(farben[(y // 4) % 2]))
    rt = R * 0.75
    for x, z in scheibe(rt + 1.5):
        w.setze(x, H, z, w.b("iron_block") if math.hypot(x, z) > rt else w.b("smooth_stone"))
    for x, z in kreisrand(rt + 1.5):
        w.setze(x, H + 1, z, w.b("iron_bars", north=True, south=True, east=True, west=True, waterlogged=False))
    for y in range(H + 1, H + 4):
        for x, z in kreisrand(rt * 0.7):
            w.setze(x, y, z, w.b("glass"))
    w.setze(0, H + 1, 0, w.b("sea_lantern"))
    w.setze(0, H + 2, 0, w.b("glowstone"))
    from wueste_eis import kuppel
    kuppel(w, w.b("red_terracotta" if _stil(seed) == 0 else "black_terracotta"), 0, 0, H + 4, rt * 0.8,
           form="rund", spitze=None)
    st = P.Stil(w, wand="putz", sockel="graustein", gesims="stone_brick", dach="mcw_ziegel", holz="spruce")
    P.gebaeude(w, st, round(R) + 4, -3, round(R) + 9, 2, y0=1, etagen=1, eh=4, dach="sattel", tuer="west",
               gauben=False)
    hohl(w, 2)
    return w


def hafenkran(seed, g=2):
    """Hafenkran: hölzerner Tretradkran auf dem Kai, Ausleger mit Seil und Last, Kisten und Fässer."""
    w = _welt(seed)
    u = U[g]
    strand(w, _r(12 * u + 5), meer_ab=0)
    for x in range(-6, 7):
        for z in range(-3, 2):
            w.setze(x, 0, z, w.b("stone_bricks") if (x + z) % 3 else w.b("cobblestone"))
    H = _r(10 * u + 5)
    for y in range(1, H):
        for x, z in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            w.setze(x, y, z, w.b("spruce_log", axis="y"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, H, z, w.b("spruce_planks"))
    P.walmdach(w, P.Dach(w, "mcw_holz"), -2, -2, 2, 2, H, ue=1)
    for k in range(_r(8 * u + 3)):
        w.setze(0, H - 1 - k // 3, 2 + k, w.b("stripped_spruce_log", axis="z"))
    tip = 2 + _r(8 * u + 3)
    for y in range(3, H - 3):
        w.setze(0, y, tip, MB.seil(w, "y"))
    w.setze(0, 2, tip, w.b("barrel", facing="up", open=False))
    for x, z in kreisrand(2.5, -4, 0):
        for y in range(1, 5):
            if (x + y) % 2:
                w.setze(x, y, z, w.b("spruce_planks"))
    hohl(w, 2)
    return w


def kai(seed, g=1):
    """Kai mit Steg: gemauerte Kaimauer, Poller mit Tauen, Holzsteg ins Wasser, Fässer, Kisten und Laternen."""
    w = _welt(seed)
    u = U[g]
    L = _r(12 * u + 6)
    strand(w, L + 4, meer_ab=0)
    for x in range(-L, L + 1):
        for z in range(-3, 1):
            for y in range(-2, 1):
                w.setze(x, y, z, w.b("stone_bricks") if (x + y) % 4 else w.b("mossy_stone_bricks"))
        if x % 4 == 0:
            w.setze(x, 1, 0, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                                 waterlogged=False))
    for z in range(1, L):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
        if z % 3 == 0:
            for sx in (-2, 2):
                w.setze(sx, 0, z, w.b("spruce_log", axis="y"))
                w.setze(sx, 1, z, w.b("spruce_log", axis="y"))
                w.setze(sx, 2, z, MB.laterne(w, "chain_lantern"))
    for k in range(5):
        w.setze(-L + 2 + k * 2, 1, -2, w.b("barrel", facing="up", open=False) if k % 2 else MB.ware(w, w.rng))
    st = P.Stil(w, wand="backstein", sockel="graustein", gesims="brick", dach="mcw_schiefer", holz="dark_oak")
    bb = _r(4 * u + 2, 3)
    P.gebaeude(w, st, -L + 2, -6 - 2 * bb, -L + 2 + 2 * bb + 4, -6, y0=1, etagen=2 + (g >= 2), eh=4, dach="sattel",
               tuer="south", kamine=0)
    for x in range(-L + 2, -L + 2 + 2 * bb + 5, 3):
        w.setze(x, 1, -5, MB.mod(w, "supplementaries:sack", "white_wool", open=False) if x % 2 else
                w.b("barrel", facing="up", open=False))
    for x in range(L - 6, L + 1):
        for y in range(1, 3):
            if (x + y) % 3:
                w.setze(x, y, -5, w.b("spruce_planks") if y == 1 else MB.ware(w, w.rng))
    hohl(w, 2)
    return w


def fischerhuetten(seed, g=1):
    """Fischerhütten: kleine bunte Holzhäuser am Strand, Netze, umgedrehte Boote, Räucherofen und Steg."""
    w = _welt(seed)
    u = U[g]
    n = 2 + g
    L = n * 8
    strand(w, L, meer_ab=3)
    farben = [["putz_blau"], ["holz_hell"], ["fachwerk_rot"], ["kalk_kupfer"]]
    for i in range(n):
        x0 = -L // 2 + i * 8
        dd = dict(H_.HAUSPOOL[["putz_blau", "holz_hell", "fachwerk_rot", "kalk_kupfer"][i % 4]])
        dd["dach"] = ["mcw_rot", "mcw_blau", "mcw_ziegel", "schindel_gruen"][i % 4]
        st = P.Stil(w, **dd)
        P.gebaeude(w, st, x0, -5, x0 + 4, -1, y0=1, etagen=1, eh=3, dach="sattel", first_x=False, tuer="south",
                   gauben=False, kamine=1)
    for z in range(0, L // 2):
        for x in (2, 3):
            w.setze(x, 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    return w


def klippenleuchtturm(seed, g=2):
    """Klippenleuchtturm: steinerner Turm auf hoher Klippe über der Brandung, Treppe in den Fels gehauen."""
    w = _welt(seed)
    u = U[g]
    W, H = _r(12 * u + 5), _r(12 * u + 5)
    fels = Mat(w, ["stone", "andesite", "cobblestone", "diorite", "tuff", "mossy_cobblestone"], kontrast=1.3)
    r_n = Rauschen(w, 4)
    for x, z in scheibe(W + 3):
        rand = W * (0.85 + 0.25 * r_n(x, 5, z))
        dd = math.hypot(x, z * 1.3 if z > 0 else z)
        if dd < rand:
            stufe = min(1.0, (rand - dd) / 3.0)
            hh = H * (0.75 + 0.35 * r_n(x, 0, z)) * stufe
            for y in range(-2, int(hh) + 1):
                w.setze(x, y, z, fels(x, y, z, max(0, y) / H))
            if hh > 1 and stufe >= 1:
                w.setze(x, int(hh) + 1, z, w.b("grass_block", snowy=False))
                if w.rng.random() < 0.15:
                    w.setze(x, int(hh) + 2, z, w.b(["grass", "fern", "dandelion"][int(w.rng.integers(3))]))
        else:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("gravel") if (x + z) % 3 else w.b("sand"))
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="mcw_schiefer", holz="spruce")
    top = max(y for (x, y, z) in w.bloecke if abs(x) < 3 and abs(z + 3) < 3)
    # in den Fels gehauene Treppe zum Wasser
    for k in range(top):
        zz = W // 2 - k // 2 + 0
        xx = round(W * 0.55) - k
        for y in range(k + 1, top + 3):
            w.bloecke.pop((xx, y, zz), None)
        w.setze(xx, k, zz, w.b("stone_brick_stairs", facing="west", half="bottom", shape="straight",
                               waterlogged=False))
    P.turm(w, st, 0, -3, top + 1, _r(14 * u + 6), max(2.2, 2.8 * u), dach="platt", fenster=6)
    w.setze(0, top + _r(14 * u + 6) + 2, -3, w.b("sea_lantern"))
    hohl(w, 3)
    return w


def bootshaus(seed, g=1):
    """Bootshaus: Holzhalle über dem Wasser mit Tor zur Seeseite, Boot auf Slipanlage und Ruder an der Wand."""
    from dorf1 import bootsschuppen
    return bootsschuppen(seed, g)


def muschelstrand(seed, g=1):
    """Muschelstrand: Strand mit Muscheln, Kieseln, Treibholz, Sonnenschirm-Markisen und Liegen."""
    w = _welt(seed)
    u = U[g]
    R = _r(10 * u + 5)
    strand(w, R, meer_ab=R // 3)
    for i in range(2 + g):
        x, z = -R // 2 + i * 5, 0
        for y in (1, 2, 3):
            w.setze(x, y, z, w.b("birch_fence", north=False, south=False, east=False, west=False, waterlogged=False))
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                w.setze(x + dx, 4, z + dz, MB.markise(w, ["red", "blue", "yellow"][i % 3],
                                                      "north" if dz < 0 else "south"))
        w.setze(x + 1, 1, z + 2, w.b("white_bed", facing="south", part="foot", occupied=False) if False else
                w.b("birch_slab", type="bottom", waterlogged=False))
    for k in range(3):
        w.setze(R // 2 - 2 + k, 1, -2, w.b("stripped_oak_log", axis="x"))
    return w


def strandpromenade(seed, g=2):
    """Strandpromenade: Holzsteg entlang des Strandes, Laternen, Bänke, Strandkörbe und ein Pavillon."""
    w = _welt(seed)
    u = U[g]
    L = _r(16 * u + 6)
    strand(w, L, meer_ab=3)
    for x in range(-L, L + 1):
        for z in (-2, -1, 0):
            w.setze(x, 1, z, w.b("spruce_planks") if (x + z) % 2 else w.b("stripped_spruce_log", axis="x"))
        if x % 5 == 0:
            w.setze(x, 2, -2, MB.laterne(w, "chain_lantern") if False else w.b("spruce_fence", north=False,
                                                                                south=False, east=False, west=False,
                                                                                waterlogged=False))
            w.setze(x, 3, -2, w.b("lantern", hanging=False, waterlogged=False))
    for sx in (-1, 1):
        x = sx * L // 2
        for y in range(2, 5):
            for dx, dz in ((-2, -4), (2, -4), (-2, -8), (2, -8)):
                w.setze(x + dx, y, dz, w.b("white_concrete"))
        P.walmdach(w, P.Dach(w, "mcw_blau"), x - 2, -8, x + 2, -4, 5, ue=1)
    return w


def wrackstrand(seed, g=2):
    """Wrack am Strand: gestrandetes Schiff schräg im Sand, Kisten im Spülsaum, Möwen-Felsen."""
    from wueste_eis import gestrandetes_schiff
    w = gestrandetes_schiff(seed, g)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) == "minecraft:sand" and y > 1 and rng.random() < 0.5:
            del w.bloecke[(x, y, z)]
    for x in range(-30, 31):
        for z in range(6, 20):
            if w.frei(x, 0, z):
                w.setze(x, 0, z, w.b("water", level=0))
    return w


def seezeichen(seed, g=1):
    """Seezeichen-Turm: kleiner Feuerturm auf einer Mole, Glocke, Signallaternen und Wellenbrecher."""
    w = _welt(seed)
    u = U[g]
    L = _r(10 * u + 5)
    for x, z in scheibe(L + 2):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("sand") if (x * 7 + z) % 5 else w.b("gravel"))
    for x, z in scheibe(4, -2, -L):
        for y in (0, 1):
            w.setze(x, y, z, w.b(["stone", "andesite", "mossy_cobblestone"][(x + z) % 3]))
    for z in range(-L, 2):
        for x in (-1, 0, 1):
            for y in (0, 1):
                w.setze(x, y, z, w.b("cobblestone") if (x + z) % 2 else w.b("stone_bricks"))
    for y in range(2, _r(8 * u + 4)):
        for x, z in kreisrand(1.4):
            w.setze(x, y, z, w.b("white_concrete") if (y // 2) % 2 else w.b("green_concrete"))
    top = _r(8 * u + 4)
    w.setze(0, top, 0, w.b("sea_lantern"))
    w.setze(0, top - 2, 2, w.b("bell", attachment="single_wall", facing="south", powered=False))
    return w


def schiffswerft(seed, g=2):
    """Schiffswerft: Helling mit einem halbfertigen Rumpf (Spanten), Holzlager, Teerkessel und Kran."""
    w = _welt(seed)
    u = U[g]
    L = _r(12 * u + 5)
    strand(w, L + 6, meer_ab=L // 2)
    for x in range(-L, L + 1):
        w.setze(x, 0, 0, w.b("spruce_planks"))
        if x % 2 == 0:
            r = 3 * u * math.sin((x + L) / (2 * L) * math.pi) + 1
            for k in range(13):
                a = k / 12 * math.pi
                yy = round(r - math.sin(a) * r + 1)
                zz = round(math.cos(a) * r)
                w.setze(x, yy, zz, w.b("stripped_spruce_log", axis="y"))
    for k in range(4):
        w.setze(-L - 3, 1, -2 + k * 2, w.b("water_cauldron", level=3) if k == 0 else w.b("spruce_log", axis="x"))
    return w


def kuestenfort(seed, g=2):
    """Küstenfort: sternförmige Batterie auf einem Felsvorsprung über dem Meer mit Kanonenscharten und Flagge."""
    from burgen import barbakane
    w = barbakane(seed, g)
    boden = [(x, z) for (x, y, z) in w.bloecke if y == 0]
    Rg = max(math.hypot(x, z) for x, z in boden)
    bau = {(x, z) for (x, y, z), b in w.bloecke.items() if y >= 2}
    r_n = Rauschen(w, 4)
    for x, z in scheibe(Rg + 6):
        if z > Rg * (0.55 + 0.2 * r_n(x, 0, z)) and (x, z) not in bau:
            for y in range(1, 4):
                w.bloecke.pop((x, y, z), None)
            nah = z < Rg * 0.75
            w.setze(x, 0, z, w.b("sand") if nah and (x + z) % 4 else w.b("water", level=0))
            w.setze(x, -1, z, w.b("sand"))
            if nah and w.rng.random() < 0.04:
                w.setze(x, 1, z, MB.muschel(w))
    return w


def austernbank(seed, g=1):
    """Austernbank: flache Lagune mit Pfählen, Austernkörben und einem kleinen Schuppen auf Stelzen."""
    w = _welt(seed)
    u = U[g]
    R = _r(10 * u + 5)
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("sand") if (x + z) % 3 else w.b("clay"))
    for x in range(-R + 2, R - 1, 3):
        for z in range(-R + 2, R - 1, 3):
            if math.hypot(x, z) < R - 2:
                w.setze(x, 0, z, w.b("oak_log", axis="y"))
                w.setze(x, 1, z, MB.korb(w) if (x + z) % 2 else w.b("oak_fence", north=False, south=False, east=False,
                                                                      west=False, waterlogged=False))
    st = P.Stil(w, wand="holz_hell", sockel=["oak_planks"], gesims="oak", dach="mcw_holz", holz="oak", laeden=False)
    P.gebaeude(w, st, -2, -2, 2, 2, y0=2, etagen=1, eh=3, dach="sattel", tuer="south", sockel_h=0, gauben=False,
               kamine=0)
    for x in (-2, 2):
        for z in (-2, 2):
            for y in (0, 1):
                w.setze(x, y, z, w.b("oak_log", axis="y"))
    hohl(w, 2)
    return w


def gezeitenbecken(seed, g=1):
    """Gezeitenbecken: Felsplatten mit kleinen Becken voller Korallen, Seegras, Seegurken und Muscheln."""
    w = _welt(seed)
    u = U[g]
    R = _r(9 * u + 4)
    fels = Mat(w, ["stone", "andesite", "tuff", "diorite", "mossy_cobblestone"], kontrast=1.3)
    r_n = Rauschen(w, 2)
    rng = w.rng
    for x, z in scheibe(R):
        v = r_n(x, 0, z)
        if v < 0.4:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("sand"))
            if rng.random() < 0.15:
                w.setze(x, 0, z, w.b(f"{['tube', 'brain', 'fire', 'horn', 'bubble'][int(rng.integers(5))]}_coral",
                                     waterlogged=True))
        else:
            for y in range(0, int((v - 0.4) * 5) + 1):
                w.setze(x, y, z, fels(x, y, z, 0.5))
            if rng.random() < 0.05:
                w.setze(x, int((v - 0.4) * 5) + 1, z, MB.muschel(w))
    return w


def hafenkneipe(seed, g=1):
    """Hafenkneipe: schiefe Fachwerkkneipe am Kai mit Wirtshausschild, Fässern, Terrasse über dem Wasser,
    Laternen und Netzen an der Wand."""
    w = _welt(seed)
    u = U[g]
    a, b = _r(4 * u + 3, 4), _r(3 * u + 2, 3)
    strand(w, a + 10, meer_ab=b + 3)
    pool = ["fachwerk_ocker", "holz_dunkel"][_stil(seed)]
    dd = dict(H_.HAUSPOOL[pool])
    dd["dach"] = ["mcw_ziegel", "schindel_grau"][_stil(seed)]
    st = P.Stil(w, **dd)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2 + (g >= 2), eh=4, dach="sattel", tuer="south", kamine=2)
    for x in range(-a, a + 1):
        for z in range(b + 1, b + 7):
            w.setze(x, 1, z, w.b("spruce_planks") if (x + z) % 2 else w.b("stripped_spruce_log", axis="x"))
            if z == b + 6 or abs(x) == a:
                w.setze(x, 2, z, w.b("spruce_fence", north=abs(x) == a, south=abs(x) == a, east=z == b + 6,
                                     west=z == b + 6, waterlogged=False))
        if x % 3 == 0:
            for y in (-1, 0):
                w.setze(x, y, b + 6, w.b("spruce_log", axis="y"))
    for k, x in enumerate(range(-a + 2, a - 1, 4)):
        w.setze(x, 2, b + 3, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
        w.setze(x, 3, b + 3, w.b("spruce_pressure_plate", powered=False))
        w.setze(x - 1, 2, b + 3, w.b("spruce_stairs", facing="east", half="bottom", shape="straight",
                                     waterlogged=False))
        w.setze(x + 1, 2, b + 3, w.b("spruce_stairs", facing="west", half="bottom", shape="straight",
                                     waterlogged=False))
    for z in range(-b, b + 1, 2):
        w.setze(-a - 1, 1, z, w.b("barrel", facing="up", open=False))
        w.setze(-a - 1, 2, z, w.b("barrel", facing="east", open=False)) if z % 4 == 0 else None
    w.setze(a + 1, 4, 0, MB.mod(w, "supplementaries:hanging_sign", "oak_wall_sign" if False else "spruce_fence",
                                {"north": False, "south": False, "east": False, "west": False, "waterlogged": False},
                                facing="east", waterlogged=False) if False else w.b("spruce_fence", north=False,
                                south=False, east=False, west=False, waterlogged=False))
    for x in (-a, a):
        w.setze(x, 4, b + 1, MB.laterne(w, "chain_lantern", haengend=True))
    for x in range(-a + 1, a, 2):
        w.setze(x, 3, b + 1, w.b("cobweb")) if (x + seed) % 5 == 0 else None
    hohl(w, 2)
    return w


def fischmarkt(seed, g=1):
    """Fischmarkt am Hafen: Stände mit Markisen, Fisch-Fässer, Eisblöcke zum Kühlen, Waage und Kran-Galgen."""
    w = _welt(seed)
    u = U[g]
    n = 2 + g
    L = n * 5 + 4
    strand(w, L + 4, meer_ab=4)
    for x in range(-L, L + 1):
        for z in range(-8, 4):
            w.setze(x, 0, z, MB.pflaster(w, "stone", "running_bond") if (x * 3 + z) % 4 else w.b("cobblestone"))
    for z in range(-1, 4):
        for x in range(-L, L + 1):
            w.setze(x, 0, z + 1, w.b("stone_bricks"))
    farben = ["blue", "white", "cyan", "light_blue", "red"]
    for i in range(n):
        for reihe in (-6, -1):
            x0 = -L + 3 + i * 10 // 2 * 2
            if reihe == -1:
                x0 += 4
            for x in range(x0, x0 + 4):
                w.setze(x, 1, reihe, w.b("spruce_planks"))
                w.setze(x, 2, reihe, w.b(["packed_ice", "barrel", "ice", "blue_ice"][(x + i) % 4])
                        if (x + reihe) % 2 else MB.ware(w, w.rng))
                w.setze(x, 4, reihe - 1, MB.markise(w, farben[(i + (reihe > -5)) % len(farben)], "north"))
                w.setze(x, 4, reihe + 1, MB.markise(w, farben[(i + (reihe > -5)) % len(farben)], "south"))
                w.setze(x, 4, reihe, MB.markise(w, farben[(i + (reihe > -5)) % len(farben)], "north", half="top")
                        if False else w.b(f"{farben[(i + (reihe > -5)) % len(farben)]}_wool"))
            for x in (x0, x0 + 3):
                w.setze(x, 3, reihe, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                         waterlogged=False))
    for y in range(1, 6):
        w.setze(L - 2, y, 3, w.b("spruce_log", axis="y"))
    for z in range(3, 7):
        w.setze(L - 2, 6, z, w.b("spruce_log", axis="z"))
    for y in range(3, 6):
        w.setze(L - 2, y, 6, MB.seil(w, "y"))
    w.setze(L - 2, 2, 6, w.b("barrel", facing="up", open=False))
    for z in range(4, 4 + _r(6 * u + 3)):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    return w


def inselleuchtfeuer(seed, g=2):
    """Leuchtfeuer-Insel: Felsinsel im Meer mit gedrungenem Steinleuchtturm, Wärterhaus mit Gemüsegarten,
    Bootssteg und Seevögelfelsen."""
    w = _welt(seed)
    u = U[g]
    R = _r(8 * u + 5)
    fels = Mat(w, ["stone", "andesite", "cobblestone", "mossy_cobblestone", "tuff"], kontrast=1.2)
    r_n = Rauschen(w, 3)
    for x, z in scheibe(R + 8):
        rr = R * (0.8 + 0.35 * r_n(x, 0, z))
        dd = math.hypot(x, z)
        if dd < rr:
            hh = int(min(4 + g, (rr - dd) * 0.9))
            for y in range(-2, hh + 1):
                w.setze(x, y, z, fels(x, y, z, max(0, y) / 6))
            if (rr - dd) > 2.5:
                w.setze(x, hh, z, w.b("grass_block", snowy=False))
        else:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("sand") if (x + z) % 3 else w.b("gravel"))
    top = max(y for (x, y, z) in w.bloecke if abs(x) <= 1 and abs(z) <= 1)
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="mcw_rot", holz="spruce")
    Ht = _r(12 * u + 6)
    P.turm(w, st, 0, 0, top + 1, Ht, max(2.2, 2.4 * u), dach="kegel", krone=False, fenster=5, fahne=None)
    yl = top + 1 + Ht
    w.setze(0, yl - 1, 0, w.b("sea_lantern"))
    hx = round(R * 0.4) + 1
    th = max(y for (x, y, z) in w.bloecke if abs(x - hx - 2) <= 1 and abs(z) <= 1)
    st2 = P.Stil(w, wand="putz", sockel="graustein", gesims="stone_brick", dach="mcw_rot", holz="spruce")
    P.gebaeude(w, st2, hx, -2, hx + 5, 3, y0=th + 1, etagen=1, eh=4, dach="sattel", tuer="west", gauben=False,
               sockel_h=1)
    for z in range(R - 2, R + 6):
        for x in (-1, 0):
            w.setze(x - R // 2, 1, z, w.b("spruce_planks"))
    hohl(w, 2)
    return w


def strandbad(seed, g=1):
    """Strandbad: Badehäuschen in Streifen auf Stelzen, Sprungturm am Steg, Rettungsring-Pfosten und Liegen."""
    w = _welt(seed)
    u = U[g]
    n = 3 + g * 2
    L = n * 4 // 2 + 4
    strand(w, L + 3, meer_ab=2)
    farben = ["red", "blue", "green", "yellow", "light_blue", "orange", "magenta"]
    for i in range(n):
        x = -n * 4 // 2 + i * 4
        f = farben[(i + seed) % len(farben)]
        for y in range(1, 4):
            for dx in (0, 1, 2):
                for dz in (0, 1, 2):
                    if dx == 1 and dz == 1:
                        continue
                    if y < 3 and (dx, dz) == (1, 2):
                        continue
                    w.setze(x + dx, y, -4 + dz, w.b(f"{f}_concrete") if dx != 1 else w.b("white_concrete"))
        for dx in (-1, 0, 1, 2, 3):
            for dz in (-1, 0, 1, 2, 3):
                hh = 4 + (min(dx, 2 - dx) + 1 if 0 <= dx <= 2 else 0) // 2
                w.setze(x + dx, 4 + (1 if dx == 1 else 0), -4 + dz,
                        w.b("spruce_stairs", facing="east" if dx < 1 else "west", half="bottom", shape="straight",
                            waterlogged=False) if dx != 1 else w.b("spruce_slab", type="bottom", waterlogged=False))
        w.setze(x + 1, 1, -2, w.b("spruce_door", facing="south", half="lower", hinge="left", open=False, powered=False))
        w.setze(x + 1, 2, -2, w.b("spruce_door", facing="south", half="upper", hinge="left", open=False, powered=False))
        w.setze(x + 1, 0, -1, w.b("spruce_slab", type="top", waterlogged=False))
    Ls = _r(8 * u + 5)
    for z in range(0, Ls):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("birch_planks"))
        if z % 3 == 0:
            for x in (-2, 2):
                for y in (-1, 0, 1, 2):
                    w.setze(x, y, z, w.b("birch_log" if y < 2 else "birch_fence", axis="y") if y < 2 else
                            w.b("birch_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    for y in range(2, 6):
        w.setze(0, y, Ls, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False)
                if y < 5 else w.b("birch_planks"))
    for z in range(Ls, Ls + 3):
        w.setze(0, 5, z, w.b("birch_slab", type="bottom", waterlogged=False))
    w.setze(2, 3, Ls - 1, w.b("red_wool"))
    for k in range(3):
        w.setze(-L // 2 + k * 4, 1, 0, w.b("white_bed", facing="south", part="head", occupied=False) if False else
                w.b("birch_slab", type="bottom", waterlogged=False))
    return w


def salzgarten(seed, g=1):
    """Salzgarten: flache Verdunstungsbecken in Rastern, weiße Salzhaufen, Holzstege, Schubkarren und
    ein Salzspeicher mit Windrad-Pumpe."""
    w = _welt(seed)
    u = U[g]
    n = 3 + g
    F = 5
    L = n * F // 2 + 4
    strand(w, L + 5, meer_ab=L)
    for i in range(n):
        for j in range(n):
            x0, z0 = -n * F // 2 + i * F, -n * F // 2 + j * F
            reif = (i + j * 2 + seed) % 4
            for x in range(x0, x0 + F):
                for z in range(z0, z0 + F):
                    rand = x in (x0, x0 + F - 1) or z in (z0, z0 + F - 1)
                    w.setze(x, 0, z, w.b("mud_bricks") if rand else (w.b("water", level=0) if reif < 2 else
                                                                    w.b("calcite") if reif == 2 else
                                                                    w.b("white_concrete_powder")))
                    w.setze(x, -1, z, w.b("clay"))
            if reif == 3:
                for k in range(2):
                    w.setze(x0 + 2, 1 + k, z0 + 2, w.b("white_concrete_powder") if k == 0 else
                            w.b("snow", layers=4))
    st = P.Stil(w, wand="holz_hell", sockel="graustein", gesims="stone_brick", dach="mcw_holz", holz="oak")
    P.gebaeude(w, st, -L - 2, -4, -L + 4, 4, y0=1, etagen=1, eh=4, dach="sattel", tuer="east", gauben=False)
    for y in range(1, 8):
        w.setze(L + 1, y, 0, w.b("oak_log", axis="y"))
    w.setze(L + 1, 8, 1, MB.mod(w, "create:windmill_bearing", "oak_planks", facing="south"))
    for k in range(-3, 4):
        w.setze(L + 1 + k, 8, 2, w.b("white_wool") if k else w.b("oak_planks"))
        w.setze(L + 1, 8 + k, 2, w.b("white_wool") if k else w.b("oak_planks"))
    return w


def seestapel(seed, g=2):
    """Möwenfelsen: frei stehende Brandungspfeiler und ein Felsentor im Meer, Vogelnester, Guano-Krusten,
    Tang und Wellen-Gischt (Kalzit)."""
    w = _welt(seed)
    u = U[g]
    R = _r(12 * u + 6)
    fels = Mat(w, ["stone", "andesite", "tuff", "diorite", "calcite", "cobblestone"], kontrast=1.4)
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("sand") if (x * 3 + z) % 4 else w.b("gravel"))
        w.setze(x, -2, z, w.b("sand"))
    rng = w.rng
    pfeiler = [(0, 0, 1.0)] + [(round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55), 0.4 + 0.4 * rng.random())
                               for a in np.linspace(0, 2 * math.pi, 4 + g)[:-1] + rng.random()]
    S = Skulptur(w, 1.0)
    S.mat("f", sk(fels, 0, 30 * u))
    H = 18 * u + 6
    for (cx, cz, f) in pfeiler[1:]:
        rr = (2 + 2 * u) * f
        hh = H * f
        S.plus(lambda X, Y, Z, cx=cx, cz=cz, rr=rr, hh=hh: ((X - cx) ** 2 + (Z - cz) ** 2 <
                                                         (rr * (1.1 - 0.35 * Y / hh)) ** 2) & (Y > -3) & (Y < hh), "f")
    # Felsentor
    tb = 4 * u + 3
    S.plus(lambda X, Y, Z: (np.abs(Z) < 2.2 * u + 1) & (np.abs(X) < tb + 2.5 * u) & (Y > -3) & (Y < H * 0.75)
           & ~((X / tb) ** 2 + (Y / (H * 0.5)) ** 2 < 1), "f")
    S.rendern((-R, -3, -R), (R, H + 2, R), versatz=(0.5, 0, 0.5))
    oben = {}
    for (x, y, z) in w.bloecke:
        if y > 1 and w.P.name(w.bloecke[(x, y, z)]).split(":")[1] in ("stone", "andesite", "tuff", "diorite", "calcite",
                                                                       "cobblestone"):
            if oben.get((x, z), -99) < y:
                oben[(x, z)] = y
    for (x, z), y in oben.items():
        r = rng.random()
        if r < 0.35:
            w.setze(x, y, z, w.b("calcite"))
        elif r < 0.45:
            w.setze(x, y + 1, z, w.b("hay_block", axis="y") if False else MB.mod(w, "twigs:twig", "dead_bush"))
        elif r < 0.5:
            w.setze(x, y + 1, z, w.b("white_carpet"))
    for (x, y, z), b in list(w.bloecke.items()):
        if y in (1, 2) and rng.random() < 0.3 and w.P.name(b) != "minecraft:water":
            for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if w.frei(x + dx, y, z + dz) and (x + dx, 0, z + dz) in w.bloecke:
                    w.setze(x + dx, y, z + dz, w.b("calcite") if y == 1 else w.b("mossy_cobblestone"))
                    break
    hohl(w, 3)
    return w


def jachthafen(seed, g=2):
    """Jachthafen: Hafenbecken mit Mole, Schwimmstegen, Segelbooten mit Masten und Segeln, Hafenmeisterei
    und Laternen."""
    w = _welt(seed)
    u = U[g]
    R = _r(14 * u + 6)
    strand(w, R + 4, meer_ab=-R // 3)
    for x, z in kreisrand(R * 0.95):
        if z > -R // 3 and not (abs(x) < 3 and z > 0):
            for y in (-1, 0, 1):
                w.setze(x, y, z, w.b("stone_bricks") if (x + y) % 3 else w.b("mossy_stone_bricks"))
    for xs in range(-R // 2, R // 2 + 1, max(6, R // 3)):
        for z in range(-R // 3 + 1, R // 2):
            w.setze(xs, 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
        for k, z in enumerate(range(-R // 3 + 3, R // 2 - 2, 5)):
            sx = xs + (2 if k % 2 else -4)
            for dx in range(3):
                for dz in range(-1, 2):
                    if not (dx in (0, 2) and dz != 0 and False):
                        w.setze(sx + dx, 1, z + dz, w.b("white_concrete") if abs(dz) == 1 or dx in (0, 2) else
                                w.b("birch_planks"))
            mh = 5 + int(3 * u)
            for y in range(2, 2 + mh):
                w.setze(sx + 1, y, z, w.b("birch_fence", north=False, south=False, east=False, west=False,
                                          waterlogged=False))
                if y > 3 and y < 1 + mh:
                    w.setze(sx + 1, y, z + 1, w.b("white_wool"))
                    if y < mh - 1:
                        w.setze(sx + 1, y, z + 2, w.b("white_wool"))
    st = P.Stil(w, wand="putz", sockel="graustein", gesims="stone_brick", dach="mcw_blau", holz="spruce")
    P.gebaeude(w, st, -4, -R // 3 - 9, 4, -R // 3 - 3, y0=1, etagen=2, eh=4, dach="walm", tuer="south")
    for x in range(-R // 2, R // 2 + 1, 5):
        MB.strassenlampe(w, x, 1, -R // 3 - 1)
    hohl(w, 2)
    return w


KUESTE = {
    "leuchtturm": ("Leuchtturm", leuchtturm),
    "hafenkran": ("Hafenkran", hafenkran),
    "kai": ("Kai mit Steg", kai),
    "fischerhuetten": ("Fischerhütten", fischerhuetten),
    "klippenleuchtturm": ("Klippenleuchtturm", klippenleuchtturm),
    "bootshaus": ("Bootshaus", bootshaus),
    "muschelstrand": ("Muschelstrand", muschelstrand),
    "strandpromenade": ("Strandpromenade", strandpromenade),
    "wrackstrand": ("Wrack am Strand", wrackstrand),
    "seezeichen": ("Seezeichen-Turm", seezeichen),
    "schiffswerft": ("Schiffswerft", schiffswerft),
    "kuestenfort": ("Küstenfort", kuestenfort),
    "austernbank": ("Austernbank", austernbank),
    "gezeitenbecken": ("Gezeitenbecken", gezeitenbecken),
    "hafenkneipe": ("Hafenkneipe", hafenkneipe),
    "fischmarkt": ("Fischmarkt", fischmarkt),
    "inselleuchtfeuer": ("Leuchtfeuer-Insel", inselleuchtfeuer),
    "strandbad": ("Strandbad", strandbad),
    "salzgarten": ("Salzgarten", salzgarten),
    "moewenfelsen": ("Möwenfelsen", seestapel),
    "jachthafen": ("Jachthafen", jachthafen),
}

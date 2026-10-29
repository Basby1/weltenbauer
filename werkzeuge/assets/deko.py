"""Deko & Wege – kachelbare Wegstücke (Pflaster, Kies, Trittsteine, Stege, Treppen), Mauern, Hecken und Zäune
sowie Kleinkram zum Ausschmücken: Laternen, Bänke, Brunnen, Wegweiser, Marktstand, Fässer, Blumenkübel, Statuen,
Feuerstelle, Holzstapel, Wegkreuz, Picknick, Säulengang und Torbogen. Boden y = 0."""

from __future__ import annotations

import math

import modbloecke as MB
import pracht as P
from flora import _neu, _r, _stil, linie
from lib import Rauschen
from pracht import Mat

U = [0.6, 1.0, 1.7, 2.8]
LANG = [8, 14, 22, 32]


def zf(w, holz="oak", **v):
    d = dict(north=False, south=False, east=False, west=False, waterlogged=False)
    d.update(v)
    return w.b(f"{holz}_fence", **d)


def rasen(w, x0, z0, x1, z1, blumen=0.15):
    rng = w.rng
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, 0, z, w.b("grass_block", snowy=False), False)
            if rng.random() < blumen and w.frei(x, 1, z):
                w.setze(x, 1, z, w.b(["grass", "dandelion", "poppy", "grass", "oxeye_daisy"][int(rng.integers(5))]))


def pflaster_zelle(w, x, z, stil=0, rn=None):
    mats = [["cobblestone", "mossy_cobblestone", "andesite", "stone", "gravel"],
            ["stone_bricks", "cracked_stone_bricks", "mossy_stone_bricks", "polished_andesite", "stone_bricks"]][stil]
    v = rn(x, 0, z) if rn else 0.5
    w.setze(x, 0, z, w.b(mats[int(v * 4.99)]))


def weg_linie(w, pts, breite, zelle, rand=None):
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        n = max(abs(bx - ax), abs(bz - az), 1)
        for k in range(n + 1):
            x, z = ax + (bx - ax) * k / n, az + (bz - az) * k / n
            for dx in range(-breite - 1, breite + 2):
                for dz in range(-breite - 1, breite + 2):
                    d = math.hypot(dx, dz)
                    p = (round(x) + dx, round(z) + dz)
                    if d <= breite:
                        zelle(*p)
                        w.bloecke.pop((p[0], 1, p[1]), None)
                    elif d <= breite + 1 and rand:
                        rand(*p)


def laternenpfahl(w, x, z, h=3, holz="spruce", haengend=True, seele=False):
    for y in range(1, h + 1):
        w.setze(x, y, z, zf(w, holz))
    if haengend:
        w.setze(x, h + 1, z, w.b(f"{holz}_planks"))
        w.setze(x + 1, h + 1, z, zf(w, holz, west=True))
        w.setze(x + 1, h, z, w.b("soul_lantern" if seele else "lantern", hanging=True, waterlogged=False))
    else:
        w.setze(x, h + 1, z, w.b("soul_lantern" if seele else "lantern", hanging=False, waterlogged=False))


def bank(w, x, z, richtung="south", holz="spruce"):
    gegen = {"south": "north", "north": "south", "east": "west", "west": "east"}[richtung]
    dx, dz = (1, 0) if richtung in ("north", "south") else (0, 1)
    for k in range(-1, 2):
        w.setze(x + dx * k, 1, z + dz * k, w.b(f"{holz}_stairs", facing=gegen, half="bottom", shape="straight",
                                               waterlogged=False))
    for k in (-2, 2):
        w.setze(x + dx * k, 1, z + dz * k, w.b(f"{holz}_trapdoor", facing=richtung if dx else gegen, half="bottom",
                                               open=True, powered=False, waterlogged=False) if False else
                w.b(f"{holz}_slab", type="bottom", waterlogged=False))


# ============================================================================ Wege (kachelbar)

def pflasterweg(seed, g=1):
    """Pflasterweg gerade: ein kopfsteingepflasterter Weg mit Randsteinen und Grasstreifen, Ein- und Ausgang
    mittig an den Kanten – beliebig aneinanderreihbar."""
    w = _neu(seed)
    L = LANG[g]
    B = 1 + g // 2 + 1
    rn = Rauschen(w, 1.2)
    rasen(w, -L, -B - 3, L, B + 3)
    weg_linie(w, [(-L, 0), (L, 0)], B, lambda x, z: pflaster_zelle(w, x, z, _stil(seed), rn),
              lambda x, z: w.setze(x, 0, z, w.b("stone_bricks" if (x + z) % 2 else "andesite")))
    return w


def pflasterkurve(seed, g=1):
    """Pflasterweg Kurve: der gepflasterte Weg biegt um 90 Grad ab – passt an das gerade Wegstück."""
    w = _neu(seed)
    L = LANG[g]
    B = 1 + g // 2 + 1
    rn = Rauschen(w, 1.2)
    rasen(w, -L, -L, L, L)
    pts = [(-L, 0)] + [(round(-L + L * math.sin(i / 8 * math.pi / 2)), round(L - L * math.cos(i / 8 * math.pi / 2)))
                       for i in range(9)] + [(0, L)]
    weg_linie(w, pts, B, lambda x, z: pflaster_zelle(w, x, z, _stil(seed), rn),
              lambda x, z: w.setze(x, 0, z, w.b("stone_bricks" if (x + z) % 2 else "andesite")))
    return w


def dorfplatz(seed, g=2):
    """Dorfplatz: eine runde gepflasterte Kreuzung mit Sternmuster, Linde mit Rundbank in der Mitte und vier
    abgehenden Wegen – das Herzstück jedes Wegenetzes."""
    import wald2
    from lib import einfuegen
    w = _neu(seed)
    L = LANG[g]
    R = L * 0.6
    rn = Rauschen(w, 1.2)
    rasen(w, -L, -L, L, L)
    for x in range(-L, L + 1):
        for z in range(-L, L + 1):
            d = math.hypot(x, z)
            if d <= R:
                a = math.degrees(math.atan2(z, x)) % 45
                w.setze(x, 0, z, w.b("smooth_stone" if a < 4 else "stone_bricks" if d % 4 < 1 else
                                     ["cobblestone", "andesite", "mossy_cobblestone"][int(rn(x, 0, z) * 2.99)]))
    for (bx, bz) in ((L, 0), (-L, 0), (0, L), (0, -L)):
        weg_linie(w, [(0, 0), (bx, bz)], 2, lambda x, z: pflaster_zelle(w, x, z, 0, rn))
    for x in range(-2, 3):
        for z in range(-2, 3):
            if 1.5 < math.hypot(x, z) <= 2.5:
                w.setze(x, 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    einfuegen(w, wald2.laubbaum(seed, "oak", H=_r(4 + 3 * g)), 0, 0, 0)
    return w


def trittsteinpfad(seed, g=1):
    """Trittsteinpfad: unregelmäßige flache Steinplatten im Rasen, dazwischen Moos und kleine Blumen, leicht
    geschwungen – kachelbar."""
    w = _neu(seed)
    L = LANG[g]
    rasen(w, -L, -4, L, 4, blumen=0.25)
    rng = w.rng
    x = -L
    while x <= L:
        z = round(math.sin(x * 0.3) * 1.2)
        for dx in range(0, 2):
            for dz in range(-1, 1 + (rng.random() < 0.5)):
                w.setze(x + dx, 0, z + dz, w.b(["smooth_stone", "polished_andesite", "stone", "andesite"][
                    int(rng.integers(4))]))
                w.bloecke.pop((x + dx, 1, z + dz), None)
        w.setze(x + 2, 1, z, w.b("moss_carpet"), False)
        x += 3
    return w


def kiesweg(seed, g=1):
    """Kiesweg mit Beeten: ein heller Kiesweg mit Holzbohlen-Einfassung, beidseitig Blumenbeete und Buchskugeln
    – kachelbar."""
    w = _neu(seed)
    L = LANG[g]
    rasen(w, -L, -5, L, 5, blumen=0.0)
    rng = w.rng
    bl = ["poppy", "dandelion", "azure_bluet", "cornflower", "allium", "oxeye_daisy", "pink_tulip"]
    for x in range(-L, L + 1):
        for z in range(-5, 6):
            if abs(z) <= 1:
                w.setze(x, 0, z, w.b("gravel" if (x + z) % 4 else "dirt_path"))
            elif abs(z) == 2:
                w.setze(x, 0, z, w.b("spruce_planks"))
            elif abs(z) <= 4:
                w.setze(x, 0, z, w.b("coarse_dirt" if rng.random() < 0.2 else "dirt"))
                if x % 5 == 0 and abs(z) == 3:
                    w.setze(x, 1, z, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False))
                elif rng.random() < 0.7:
                    w.setze(x, 1, z, w.b(bl[(x + z) % len(bl)]))
    return w


def holzsteg(seed, g=1):
    """Holzsteg: ein erhöhter Bohlenweg über feuchtem Grund mit Pfosten, Querbalken und Laternen – kachelbar."""
    w = _neu(seed)
    L = LANG[g]
    rng = w.rng
    for x in range(-L, L + 1):
        for z in range(-4, 5):
            w.setze(x, 0, z, w.b("water", level=0) if abs(z) > 1 and rng.random() < 0.5 else w.b("mud"))
            if abs(z) > 2 and rng.random() < 0.2:
                w.setze(x, 1, z, w.b("sugar_cane", age=0))
        for z in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_slab", type="top", waterlogged=False) if x % 6 else
                    w.b("stripped_spruce_log", axis="z"))
        if x % 6 == 0:
            for z in (-2, 2):
                w.setze(x, 0, z, w.b("spruce_log", axis="y"))
                w.setze(x, 1, z, w.b("spruce_log", axis="y"))
                w.setze(x, 2, z, zf(w, "spruce"))
        if x % 12 == 0:
            w.setze(x, 3, 2, w.b("lantern", hanging=False, waterlogged=False))
    return w


def treppenweg(seed, g=1):
    """Treppenweg: eine Natursteintreppe steigt einen Hang hinauf, mit Podesten, Geländer aus Holz und Bodendeckern
    auf den Böschungen."""
    w = _neu(seed)
    L = LANG[g]
    H = _r(L * 0.5)
    rng = w.rng
    for x in range(-L, L + 1):
        hx = round((x + L) / (2 * L) * H)
        for z in range(-5, 6):
            for y in range(-1, hx + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == hx and abs(z) > 2 else
                        w.b("dirt") if abs(z) > 2 else w.b("stone_bricks"))
            if abs(z) <= 2:
                w.setze(x, hx, z, w.b("stone_brick_stairs", facing="east", half="bottom", shape="straight",
                                      waterlogged=False) if (x + L) % 6 else w.b("stone_bricks"))
            elif abs(z) > 3 and rng.random() < 0.3:
                w.setze(x, hx + 1, z, w.b(["fern", "grass", "sweet_berry_bush"][int(rng.integers(3))],
                                          **({"age": 1} if False else {})))
        if x % 3 == 0:
            for z in (-3, 3):
                w.setze(x, hx + 1, z, zf(w, "spruce"))
                w.setze(x, hx + 2, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    return w


def bruchsteinmauer(seed, g=1):
    """Bruchsteinmauer: eine hüfthohe Trockenmauer mit Moos, Abdeckplatten, Efeu und einer Pforte –
    kachelbar als Grundstücksgrenze."""
    w = _neu(seed)
    L = LANG[g]
    rasen(w, -L, -3, L, 3, blumen=0.15)
    M = Mat(w, ["cobblestone", "mossy_cobblestone", "stone", "andesite", "mossy_stone_bricks"])
    for x in range(-L, L + 1):
        if abs(x) <= 1:
            continue
        for y in (1, 2):
            w.setze(x, y, 0, M(x, y, 0, 0.5))
        w.setze(x, 3, 0, w.b("stone_brick_slab" if x % 2 else "mossy_stone_brick_slab", type="bottom",
                             waterlogged=False))
        if w.rng.random() < 0.15:
            w.setze(x, 2, 1, w.b("vine", north=True, south=False, east=False, west=False, up=False))
    for sx in (-2, 2):
        w.setze(sx, 3, 0, w.b("stone_bricks"))
        w.setze(sx, 4, 0, w.b("lantern", hanging=False, waterlogged=False))
    w.setze(0, 1, 0, w.b("oak_fence_gate", facing="south", in_wall=False, open=False, powered=False))
    w.setze(1, 1, 0, w.b("oak_fence_gate", facing="south", in_wall=False, open=False, powered=False))
    w.setze(-1, 1, 0, w.b("oak_fence_gate", facing="south", in_wall=False, open=False, powered=False))
    return w


def heckentor(seed, g=1):
    """Hecke mit Torbogen: eine dichte, geschnittene Hecke, in der Mitte ein Rundbogen aus Laub mit einem
    schmiedeeisernen Tor – kachelbar."""
    w = _neu(seed)
    L = LANG[g]
    rasen(w, -L, -3, L, 3, blumen=0.1)
    H = 3 + g // 2
    for x in range(-L, L + 1):
        for y in range(1, H + 1):
            for z in (0, 1):
                w.setze(x, y, z, w.b("oak_leaves" if (x + y) % 5 else "azalea_leaves", persistent=True, distance=1,
                                     waterlogged=False))
    for x in range(-1, 2):
        for y in range(1, H):
            for z in (0, 1):
                w.bloecke.pop((x, y, z), None)
    for k in range(7):
        a = k / 6 * math.pi
        x, y = round(math.cos(a) * 2), H + round(math.sin(a) * 2)
        for z in (0, 1):
            w.setze(x, y, z, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
    for x in range(-1, 2):
        for y in (1, 2):
            w.setze(x, y, 0, w.b("iron_bars", north=False, south=False, east=x < 1, west=x > -1, waterlogged=False))
    return w


def gartenzaun(seed, g=1):
    """Gartenzaun: ein weiß gestrichener Lattenzaun mit Pfosten, Kletterrosen und einer Gartenpforte mit Bogen –
    kachelbar."""
    w = _neu(seed)
    L = LANG[g]
    rasen(w, -L, -3, L, 3, blumen=0.2)
    for x in range(-L, L + 1):
        if abs(x) <= 1:
            continue
        w.setze(x, 1, 0, zf(w, "birch", east=True, west=True))
        if x % 4 == 0:
            w.setze(x, 2, 0, zf(w, "birch"))
        if w.rng.random() < 0.2:
            w.setze(x, 1, 1, w.b("rose_bush", half="lower"))
            w.setze(x, 2, 1, w.b("rose_bush", half="upper"))
    for x in range(-1, 2):
        w.setze(x, 1, 0, w.b("birch_fence_gate", facing="south", in_wall=False, open=False, powered=False))
    for sx in (-2, 2):
        for y in range(1, 4):
            w.setze(sx, y, 0, zf(w, "birch"))
    for x in range(-2, 3):
        w.setze(x, 4, 0, w.b("flowering_azalea_leaves", persistent=True, distance=1, waterlogged=False))
    return w


# ============================================================================ Kleinkram

def laternenreihe(seed, g=1):
    """Laternenreihe: verschiedene Laternenpfähle (Holz mit Ausleger, Stein mit Laternenkopf, Eisen mit
    Seelenlicht) in einer Reihe als Musterkatalog."""
    w = _neu(seed)
    L = LANG[g]
    rasen(w, -L, -3, L, 3, blumen=0.0)
    for k, x in enumerate(range(-L + 2, L - 1, 4)):
        art = k % 4
        h = 3 + g // 2
        if art == 0:
            laternenpfahl(w, x, 0, h, "spruce")
        elif art == 1:
            for y in range(1, h + 1):
                w.setze(x, y, 0, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                     west="none", waterlogged=False))
            w.setze(x, h + 1, 0, w.b("lantern", hanging=False, waterlogged=False))
        elif art == 2:
            laternenpfahl(w, x, 0, h, "dark_oak", haengend=False, seele=True)
        else:
            for y in range(1, h + 1):
                w.setze(x, y, 0, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
            w.setze(x, h + 1, 0, w.b("end_rod", facing="up"))
    return w


def brunnen_klein(seed, g=0):
    """Kleiner Zierbrunnen: ein runder Steintrog mit Wasserspeier-Säule und Blumen ringsum."""
    w = _neu(seed)
    u = U[g]
    R = _r(3 * u + 2)
    rasen(w, -R - 3, -R - 3, R + 3, R + 3, blumen=0.3)
    for x in range(-R - 1, R + 2):
        for z in range(-R - 1, R + 2):
            d = math.hypot(x, z)
            if d <= R:
                w.setze(x, 1, z, w.b("water", level=0) if d < R - 0.8 else w.b("stone_bricks"))
                w.setze(x, 0, z, w.b("stone_bricks"))
                w.bloecke.pop((x, 2, z), None)
    for y in range(1, R + 3):
        w.setze(0, y, 0, w.b("chiseled_stone_bricks") if y == R + 2 else w.b("stone_brick_wall", up=True,
                                                                               north="none", south="none",
                                                                               east="none", west="none",
                                                                               waterlogged=False))
    w.setze(0, R + 3, 0, w.b("water", level=0))
    return w


def bank_laterne(seed, g=0):
    """Rastplatz: eine Holzbank mit Laterne, Abfallkorb und einem Busch, auf einem kleinen Pflasterplatz."""
    w = _neu(seed)
    rasen(w, -5, -4, 5, 4, blumen=0.2)
    for x in range(-3, 4):
        for z in range(-1, 2):
            w.setze(x, 0, z, w.b("cobblestone" if (x + z) % 2 else "andesite"))
            w.bloecke.pop((x, 1, z), None)
    bank(w, 0, -1, "south")
    laternenpfahl(w, 3, -1, 3, "spruce", haengend=False)
    w.setze(-3, 1, -1, w.b("composter", level=2))
    w.setze(-4, 1, 1, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False))
    return w


def wegweiser(seed, g=0):
    """Wegweiser: ein Pfahl mit mehreren Richtungsschildern, ein Meilenstein und eine kleine Laterne an einer
    Wegkreuzung."""
    w = _neu(seed)
    rasen(w, -5, -5, 5, 5, blumen=0.15)
    rn = Rauschen(w, 1.2)
    for k in range(-5, 6):
        for d in (-1, 0, 1):
            w.setze(k, 0, d, w.b("dirt_path" if rn(k, 0, d) > 0.3 else "gravel"))
            w.setze(d, 0, k, w.b("dirt_path" if rn(d, 0, k) > 0.3 else "gravel"))
    for y in range(1, 5):
        w.setze(2, y, 2, w.b("spruce_log", axis="y") if y < 4 else zf(w, "spruce"))
    for f, (dx, dz), y in (("east", (1, 0), 3), ("south", (0, 1), 3), ("west", (-1, 0), 2), ("north", (0, -1), 2)):
        w.setze(2 + dx, y, 2 + dz, w.b("spruce_wall_sign", facing=f, waterlogged=False))
    w.setze(-2, 1, -2, w.b("chiseled_stone_bricks"))
    w.setze(-2, 2, -2, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    return w


def marktstand(seed, g=0):
    """Marktstand: ein kleiner Holzstand mit gestreifter Markise, Auslage voller Waren, Körben und Fässern."""
    w = _neu(seed)
    rasen(w, -5, -4, 5, 5, blumen=0.0)
    farbe = ["red", "blue", "green", "yellow"][seed % 4]
    for x in range(-2, 3):
        for z in (-1, 0):
            if abs(x) == 2 and z == -1:
                for y in range(1, 4):
                    w.setze(x, y, z, zf(w, "spruce"))
        w.setze(x, 1, 1, w.b("spruce_planks"))
        w.setze(x, 2, 1, MB.ware(w, w.rng))
        w.setze(x, 4, -1, w.b(f"{farbe}_wool" if x % 2 else "white_wool"))
        w.setze(x, 4, 0, w.b(f"{farbe}_wool" if x % 2 else "white_wool"))
        w.setze(x, 3, 1, w.b(f"{farbe}_wool" if x % 2 else "white_wool"))
    for x in (-2, 2):
        for y in (1, 2):
            w.setze(x, y, 1, zf(w, "spruce"))
    w.setze(3, 1, 2, w.b("barrel", facing="up", open=True))
    w.setze(-3, 1, 2, w.b("composter", level=7))
    return w


def fass_kisten(seed, g=0):
    """Fässer & Kisten: ein Stapel aus Fässern, Kisten, Säcken und Heu, wie er vor Lagerhäusern und Tavernen
    steht."""
    w = _neu(seed)
    rasen(w, -4, -4, 4, 4, blumen=0.0)
    for x in range(-2, 3):
        for z in range(-1, 2):
            w.setze(x, 0, z, w.b("gravel" if (x + z) % 2 else "coarse_dirt"))
    teile = [((0, 0), 2, "barrel"), ((1, 0), 1, "barrel"), ((-1, 0), 1, "chest"), ((0, 1), 1, "hay_block"),
             ((-1, -1), 2, "barrel"), ((1, 1), 1, "brown_wool"), ((2, 0), 1, "barrel"), ((-2, 1), 1, "white_wool")]
    for (x, z), h, n in teile:
        for y in range(1, h + 1):
            if n == "barrel":
                w.setze(x, y, z, w.b("barrel", facing="up" if y == h else "east", open=False))
            elif n == "chest":
                w.setze(x, y, z, w.b("chest", facing="south", type="single", waterlogged=False))
            elif n == "hay_block":
                w.setze(x, y, z, w.b("hay_block", axis="y"))
            else:
                w.setze(x, y, z, w.b(n))
    return w


def blumenkuebel(seed, g=0):
    """Blumenkübel-Gruppe: große Terrakotta- und Steinkübel mit Bäumchen, Blumen und Gräsern, unterschiedlich hoch."""
    w = _neu(seed)
    rasen(w, -5, -5, 5, 5, blumen=0.0)
    for x in range(-4, 5):
        for z in range(-4, 5):
            w.setze(x, 0, z, w.b("smooth_stone" if (x + z) % 2 else "polished_andesite"))
    kuebel = [((-2, -2), "terracotta", "azalea_leaves"), ((2, -1), "stone_bricks", "flowering_azalea_leaves"),
              ((0, 2), "bricks", "oak_leaves"), ((-3, 2), "terracotta", None), ((3, 3), "stone_bricks", None)]
    for (x, z), mat, laub in kuebel:
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) + abs(dz) == 2:
                    continue
                w.setze(x + dx, 1, z + dz, w.b(mat))
        w.setze(x, 1, z, w.b("dirt"))
        if laub:
            w.setze(x, 2, z, w.b("oak_log", axis="y"))
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    w.setze(x + dx, 3, z + dz, w.b(laub, persistent=True, distance=1, waterlogged=False))
            w.setze(x, 4, z, w.b(laub, persistent=True, distance=1, waterlogged=False))
        else:
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                w.setze(x + dx, 2, z + dz, w.b(["poppy", "cornflower", "dandelion", "allium"][abs(dx * 2 + dz) % 4]))
            w.setze(x, 2, z, w.b("tall_grass", half="lower"))
            w.setze(x, 3, z, w.b("tall_grass", half="upper"))
    return w


def kleine_statue(seed, g=1):
    """Kleine Statue: eine Steinfigur (Ritter, Gelehrter oder Elfe) auf einem gestuften Sockel mit Kerzen und
    Blumen – Blickfang für Gärten und Plätze."""
    from motive import figur
    from skulptur import Skulptur
    from weltwunder import bl, sk
    w = _neu(seed)
    u = U[g]
    rasen(w, -5, -5, 5, 5, blumen=0.2)
    for k in range(2):
        r = 2 - k
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                w.setze(x, 1 + k, z, w.b(["stone_bricks", "polished_andesite"][k]))
    S = Skulptur(w, 0.28 * u + 0.12)
    M = Mat(w, ["stone", "andesite", "polished_andesite", "smooth_stone"])
    S.mat("k", sk(M, 0, 30))
    S.mat("a", bl(w, "gold_block" if _stil(seed) else "polished_andesite"))
    S.mat("d", bl(w, "andesite"))
    S.mat("g", bl(w, "sea_lantern"))
    figur(S, ["ritter", "mensch", "elf"][seed % 3], ["schwert", "denker", "stab"][seed % 3])
    S.rendern((-7, -1, -5), (7, 26, 7), versatz=(0.5, 3.01, 0.5))
    for x, z in ((2, 2), (-2, 2)):
        w.setze(x, 2, z, w.b("candle", candles=2, lit=True, waterlogged=False), False)
    return w


def vogeltraenke(seed, g=0):
    """Vogeltränke: eine flache Steinschale auf einer Säule mit Wasser, darum ein Ring aus Lavendel und ein
    Vogelhäuschen an einem Pfahl."""
    w = _neu(seed)
    rasen(w, -4, -4, 4, 4, blumen=0.2)
    w.setze(0, 1, 0, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                         waterlogged=False))
    for x in (-1, 0, 1):
        for z in (-1, 0, 1):
            w.setze(x, 2, z, w.b("stone_brick_slab", type="bottom", waterlogged=False) if abs(x) + abs(z) else
                    w.b("water_cauldron", level=3))
    for k in range(8):
        a = k / 8 * 6.28
        w.setze(round(math.cos(a) * 3), 1, round(math.sin(a) * 3), w.b("lilac", half="lower") if k % 2 else
                w.b("allium"))
        if k % 2:
            w.setze(round(math.cos(a) * 3), 2, round(math.sin(a) * 3), w.b("lilac", half="upper"))
    for y in range(1, 4):
        w.setze(3, y, -3, zf(w, "spruce"))
    w.setze(3, 4, -3, w.b("spruce_planks"))
    w.setze(3, 5, -3, w.b("spruce_slab", type="bottom", waterlogged=False))
    return w


def feuerstelle(seed, g=0):
    """Feuerstelle: ein Steinring mit Lagerfeuer, Baumstämme als Sitze, ein Kessel an einem Dreibein und
    Feuerholz."""
    w = _neu(seed)
    rasen(w, -5, -5, 5, 5, blumen=0.0)
    for x in range(-4, 5):
        for z in range(-4, 5):
            if math.hypot(x, z) < 4:
                w.setze(x, 0, z, w.b("coarse_dirt" if (x + z) % 3 else "gravel"))
    for k in range(8):
        a = k / 8 * 6.28
        w.setze(round(math.cos(a) * 1.5), 1, round(math.sin(a) * 1.5), w.b("cobblestone_slab", type="bottom",
                                                                             waterlogged=False))
    w.setze(0, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for (x, z, ax) in ((-3, 0, "z"), (3, 0, "z"), (0, 3, "x")):
        for d in (-1, 0, 1):
            w.setze(x + (d if ax == "x" else 0), 1, z + (d if ax == "z" else 0), w.b("oak_log", axis=ax))
    for (x, z) in ((-1, -1), (1, -1)):
        w.setze(x, 2, z, zf(w, "spruce"))
    w.setze(0, 3, -1, w.b("chain", axis="x", waterlogged=False))
    w.setze(0, 2, -2, w.b("cauldron"))
    return w


def holzstapel(seed, g=0):
    """Holzstapel: sauber aufgeschichtete Scheite unter einem kleinen Pultdach, Hackklotz mit Axt und Späne."""
    w = _neu(seed)
    rasen(w, -5, -4, 5, 4, blumen=0.0)
    for x in range(-3, 4):
        for y in range(1, 4):
            w.setze(x, y, 0, w.b("oak_log" if (x + y) % 2 else "spruce_log", axis="z"))
        w.setze(x, 4, 0, w.b("spruce_slab", type="bottom", waterlogged=False))
        w.setze(x, 4, 1, w.b("spruce_slab", type="bottom", waterlogged=False))
    w.setze(2, 1, 3, w.b("oak_log", axis="y"))
    w.setze(2, 2, 3, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return w


def wegkreuz(seed, g=0):
    """Wegkreuz: ein steinernes Kreuz mit kleinem Dach auf einem Sockel am Wegrand, Blumen und eine Kerze davor."""
    w = _neu(seed)
    rasen(w, -4, -4, 4, 4, blumen=0.3)
    w.setze(0, 1, 0, w.b("stone_bricks"))
    for y in range(2, 6):
        w.setze(0, y, 0, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                             waterlogged=False))
    for x in (-1, 1):
        w.setze(x, 4, 0, w.b("stone_brick_wall", up=False, north="none", south="none", east="low", west="low",
                             waterlogged=False))
    for x in (-1, 0, 1):
        w.setze(x, 6, 0, w.b("spruce_slab", type="bottom", waterlogged=False))
    w.setze(0, 2, 1, w.b("candle", candles=1, lit=True, waterlogged=False))
    return w


def picknick(seed, g=0):
    """Picknickplatz: eine Decke mit Korb, Kuchen und Krügen unter einem Sonnenschirm, daneben ein Baumstumpf
    als Tisch."""
    w = _neu(seed)
    rasen(w, -5, -5, 5, 5, blumen=0.25)
    for x in range(-2, 2):
        for z in range(-2, 2):
            w.setze(x, 1, z, w.b("red_carpet" if (x + z) % 2 else "white_carpet"))
    w.setze(0, 1, 0, w.b("cake", bites=1))
    w.setze(-1, 1, -1, w.b("barrel", facing="up", open=True))
    for y in range(1, 4):
        w.setze(2, y, 2, zf(w, "birch"))
    for x in range(0, 5):
        for z in range(0, 5):
            if math.hypot(x - 2, z - 2) <= 2.3:
                w.setze(x, 4, z, w.b("yellow_wool" if (x + z) % 2 else "white_wool"))
    return w


def saeulengang(seed, g=1):
    """Säulengang: eine Pergola aus weißen Säulen mit Holzbalken, berankt von Wein und Blüten, über einem
    Plattenweg – kachelbar."""
    w = _neu(seed)
    L = LANG[g]
    rasen(w, -L, -4, L, 4, blumen=0.15)
    rng = w.rng
    for x in range(-L, L + 1):
        for z in (-1, 0, 1):
            w.setze(x, 0, z, w.b("smooth_stone" if (x + z) % 2 else "polished_andesite"))
        if x % 3 == 0:
            for z in (-2, 2):
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
            for z in range(-2, 3):
                w.setze(x, 4, z, w.b("stripped_oak_log", axis="z"))
        for z in (-2, 2):
            w.setze(x, 4, z, w.b("stripped_oak_log", axis="x"))
        for z in range(-2, 3):
            if rng.random() < 0.4:
                w.setze(x, 5, z, w.b("flowering_azalea_leaves" if rng.random() < 0.3 else "oak_leaves",
                                     persistent=True, distance=1, waterlogged=False))
    return w


def torbogen(seed, g=1):
    """Torbogen: ein freistehender Steinbogen mit Schlussstein und Laternen als Eingang zu Garten, Dorf oder Burg."""
    w = _neu(seed)
    u = U[g]
    B = _r(2 * u + 1.5, 2)
    H = _r(4 * u + 2)
    rasen(w, -B - 4, -4, B + 4, 4, blumen=0.15)
    M = Mat(w, ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "andesite"])
    for sx in (-B - 1, B + 1):
        for y in range(1, H + 1):
            for z in (0, 1):
                w.setze(sx, y, z, M(sx, y, z, y / H))
    for k in range(int(B * 4) + 1):
        a = k / (B * 4) * math.pi
        x, y = round(math.cos(a) * (B + 1)), round(H + math.sin(a) * (B * 0.8))
        for z in (0, 1):
            w.setze(x, y, z, M(x, y, z, 0.8))
            w.setze(x, y + 1, z, M(x, y + 1, z, 0.9))
    w.setze(0, round(H + B * 0.8) + 1, 0, w.b("chiseled_stone_bricks"))
    for sx in (-B - 2, B + 2):
        w.setze(sx, H - 1, 0, w.b("lantern", hanging=False, waterlogged=False))
    for x in range(-B, B + 1):
        for z in range(-4, 5):
            w.setze(x, 0, z, w.b("cobblestone" if (x + z) % 2 else "gravel"))
    return w


DEKO = {
    "pflasterweg": ("Pflasterweg gerade", pflasterweg),
    "pflasterkurve": ("Pflasterweg Kurve", pflasterkurve),
    "dorfplatz": ("Dorfplatz (Kreuzung)", dorfplatz),
    "trittsteinpfad": ("Trittsteinpfad", trittsteinpfad),
    "kiesweg": ("Kiesweg mit Beeten", kiesweg),
    "holzsteg": ("Holzsteg", holzsteg),
    "treppenweg": ("Treppenweg am Hang", treppenweg),
    "bruchsteinmauer": ("Bruchsteinmauer mit Pforte", bruchsteinmauer),
    "heckentor": ("Hecke mit Torbogen", heckentor),
    "gartenzaun": ("Gartenzaun mit Pforte", gartenzaun),
    "saeulengang": ("Säulengang (Pergola)", saeulengang),
    "laternenreihe": ("Laternen-Katalog", laternenreihe),
    "brunnen_klein": ("Kleiner Zierbrunnen", brunnen_klein),
    "bank_laterne": ("Rastplatz mit Bank", bank_laterne),
    "wegweiser": ("Wegweiser an der Kreuzung", wegweiser),
    "marktstand": ("Marktstand", marktstand),
    "fass_kisten": ("Fässer & Kisten", fass_kisten),
    "blumenkuebel": ("Blumenkübel", blumenkuebel),
    "kleine_statue": ("Kleine Statue", kleine_statue),
    "vogeltraenke": ("Vogeltränke", vogeltraenke),
    "feuerstelle": ("Feuerstelle", feuerstelle),
    "holzstapel": ("Holzstapel", holzstapel),
    "wegkreuz": ("Wegkreuz", wegkreuz),
    "picknick": ("Picknickplatz", picknick),
    "torbogen": ("Torbogen", torbogen),
}

"""Gebäude II – zwanzig öffentliche und besondere Bauten: Bahnhof, Feuerwache, Markthalle, Musikpavillon,
Orangerie, Wasserturm, Uhrturm, Bibliothek, Theater, Postamt, Museum, Bootshaus, Wetterstation, Kutschenstation,
Torhaus, Brauerei, Seilbahnstation, Universität, Kaufhaus und Grandhotel. Boden y = 0."""

from __future__ import annotations

import math

import pracht as P
import wald2
from flora import _neu, _r, _stil, linie
from haeuser import HAUSPOOL
from lib import einfuegen
from pracht import Mat, gelaende
from veredeln import bewuchs

U = [0.6, 1.0, 1.7, 2.8]


def stil(w, pool, **kw):
    d = dict(HAUSPOOL[pool])
    d.update(kw)
    return P.Stil(w, **d)


def zaun(w, name="dark_oak_fence", ax=None):
    return w.b(name, east=ax == "x", west=ax == "x", north=ax == "z", south=ax == "z", waterlogged=False)


def laterne_pfahl(w, x, y, z, h=3, holz="dark_oak"):
    for k in range(1, h + 1):
        w.setze(x, y + k, z, zaun(w, f"{holz}_fence"))
    w.setze(x, y + h + 1, z, w.b("lantern", hanging=False, waterlogged=False))


def pflaster(w, x0, z0, x1, z1, y=0, mats=("cobblestone", "stone_bricks", "polished_andesite", "andesite")):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.bloecke.pop((x, y + 1, z), None)
            w.setze(x, y, z, w.b(mats[(x * 7 + z * 3 + x * z) % len(mats)]))


def uhr(w, x, y, z, seite):
    """Zifferblatt (3×3) an einer Wand."""
    sx, sz = (1, 0) if seite in ("north", "south") else (0, 1)
    dx, dz = {"south": (0, 1), "north": (0, -1), "east": (1, 0), "west": (-1, 0)}[seite]
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            blk = "black_concrete" if (a, b) in ((0, 0), (0, 1), (1, 0)) else "white_concrete"
            w.setze(x + dx + a * sx, y + b, z + dz + a * sz, w.b(blk))


def bahnhof(seed, g=2):
    """Bahnhof: ein Backsteinbahnhof mit Uhr im Giebel, ein überdachter Bahnsteig auf gusseisernen Stützen,
    Gleise mit Prellbock, Bänke, Laternen und ein Wasserkran für Dampfloks."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 8)
    gelaende(w, R, art="wiese", dichte=0.3)
    a, b = _r(5 * u + 3), _r(3 * u + 2)
    st = stil(w, "backstein", fensterart="bogen")
    top = P.gebaeude(w, st, -a, -b - 4, a, b - 4, y0=1, etagen=2, eh=5, dach="sattel", first_x=True, sockel_h=1,
                     gauben=True, kamine=2, tuer="south")
    uhr(w, 0, 10, b - 4, "south")
    L = _r(14 * u + 6)
    for x in range(-L, L + 1):
        for z in range(b - 2, b + 2):
            w.setze(x, 1, z, w.b("smooth_stone"))
        if x % 4 == 0:
            for y in range(2, 6):
                w.setze(x, y, b - 1, w.b("iron_bars", north=True, south=True, east=False, west=False,
                                         waterlogged=False) if y < 5 else w.b("polished_blackstone"))
        for z in range(b - 2, b + 2):
            w.setze(x, 6, z, w.b("waxed_oxidized_cut_copper_slab", type="bottom", waterlogged=False))
        for z in (b + 3, b + 5):
            w.setze(x, 1, z, w.b("rail", shape="east_west", waterlogged=False))
            w.setze(x, 0, z, w.b("gravel"))
        w.setze(x, 0, b + 4, w.b("gravel"))
        if x % 6 == 0:
            w.setze(x, 2, b - 2, w.b("spruce_stairs", facing="north", half="bottom", shape="straight",
                                     waterlogged=False))
    for z in (b + 3, b + 5):
        w.setze(L + 1, 1, z, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                                 west="none", waterlogged=False))
    for y in range(1, 6):
        w.setze(-L - 2, y, b + 2, w.b("iron_block" if y < 5 else "black_concrete"))
    w.setze(-L - 2, 5, b + 3, w.b("black_concrete"))
    w.setze(-L - 2, 4, b + 4, w.b("chain", axis="y", waterlogged=False))
    return w


def feuerwache(seed, g=2):
    """Feuerwache: ein rotes Ziegelhaus mit zwei großen Tortoren, einem hohen Schlauchturm mit Glocke, einem
    Wasserbottich im Hof und einer Leiter an der Wand."""
    w = _neu(seed)
    u = U[g]
    R = _r(13 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.25)
    a, b = _r(5 * u + 3), _r(3.5 * u + 2)
    st = P.Stil(w, wand=Mat(w, ["red_terracotta", "bricks", "red_nether_bricks", "bricks"]), sockel="graustein",
                gesims="stone_brick", dach="schiefer", holz="spruce")
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="sattel", first_x=True, sockel_h=1, gauben=False,
               kamine=1, tuer="north")
    for cx in (-a // 2, a // 2):
        for x in range(cx - 1, cx + 2):
            for y in range(2, 5):
                w.setze(x, y, b, w.b("red_concrete") if y < 4 or x == cx else w.b("white_concrete"))
    pflaster(w, -a, b + 1, a, b + 5)
    st2 = P.Stil(w, wand=Mat(w, ["bricks", "red_terracotta"]), sockel="graustein", gesims="stone_brick",
                 dach="schiefer", holz="spruce")
    H = _r(14 * u + 6)
    P.turm(w, st2, a + 2, -b + 1, 1, H, 1, form="eckig", dach="pyramide", krone=False, fenster=4)
    w.setze(a + 2, H - 2, -b + 1, w.b("bell", attachment="ceiling", facing="north", powered=False))
    w.setze(-a + 1, 1, b + 3, w.b("water_cauldron", level=3))
    for y in range(2, 9):
        w.setze(-a - 1, y, 0, w.b("ladder", facing="west", waterlogged=False), False)
    return w


def markthalle(seed, g=2):
    """Markthalle: eine lange, offene Halle aus Stein-Arkaden mit hohem Kupferdach und Dachreiter, darunter
    Marktstände mit Fässern, Kisten und Obst, Laternen an Ketten."""
    w = _neu(seed)
    u = U[g]
    R = _r(15 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.2)
    a, b = _r(8 * u + 4), _r(4 * u + 2)
    pflaster(w, -a - 2, -b - 2, a + 2, b + 2)
    H = _r(4 * u + 4)
    M = Mat(w, "kalkstein")
    for x in range(-a, a + 1):
        for z in (-b, b):
            pfeiler = x % 3 == 0
            for y in range(1, H + 1):
                if pfeiler or y == H or (y == H - 1 and x % 3 in (1, 2)):
                    w.setze(x, y, z, M(x, y, z, y / H))
    for z in range(-b, b + 1):
        for x in (-a, a):
            for y in range(1, H + 1):
                if z % 3 == 0 or y >= H - 1:
                    w.setze(x, y, z, M(x, y, z, y / H))
    st = P.Stil(w, wand="kalkstein", sockel="graustein", gesims="stone_brick", dach="kupfer", holz="spruce")
    top = P.satteldach(w, st.dach, -a, -b, a, b, H + 1, ue=1, first_x=True, wand=st.wand, steil=True)
    P.turm(w, st, 0, 0, top - 1, _r(3 * u + 2), 1, form="eckig", dach="nadel", krone=False, fenster=99,
           schiessscharten=False)
    waren = ["barrel", "melon", "pumpkin", "hay_block", "chest"]
    for i, x in enumerate(range(-a + 2, a - 1, 4)):
        for z in (-b + 2, b - 2):
            w.setze(x, 1, z, w.b("spruce_planks"))
            w.setze(x + 1, 1, z, w.b("spruce_planks"))
            n = waren[(i + z) % len(waren)]
            w.setze(x, 2, z, w.b(n, **({"facing": "up", "open": False} if n == "barrel" else
                                       {"facing": "south", "type": "single", "waterlogged": False} if n == "chest"
                                       else {"axis": "y"} if n == "hay_block" else {})))
            w.setze(x, H, z, w.b("chain", axis="y", waterlogged=False))
            w.setze(x, H - 1, z, w.b("lantern", hanging=True, waterlogged=False))
    return w


def musikpavillon(seed, g=1):
    """Musikpavillon: ein achteckiger, erhöhter Pavillon mit schlanken Säulen, weißem Zierbalkon, geschwungenem
    Kupferdach mit Laterne, ringsum Bänke und Blumenbeete im Park."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.5)
    r = 4 * u + 2.5
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            d = max(abs(x), abs(z), (abs(x) + abs(z)) / 1.42)
            if d <= r:
                for y in (1, 2):
                    w.setze(x, y, z, w.b("stone_bricks" if y == 1 else "spruce_planks"))
                if r - 1 < d <= r:
                    w.setze(x, 3, z, w.b("birch_fence", north=False, south=False, east=False, west=False,
                                         waterlogged=False))
    H = _r(4 * u + 3)
    for k in range(8):
        a = k / 8 * 6.283
        x, z = round(math.cos(a) * (r - 0.5)), round(math.sin(a) * (r - 0.5))
        for y in range(3, 3 + H):
            w.setze(x, y, z, w.b("white_concrete") if y < 2 + H else w.b("birch_planks"))
    for k in range(int(r) + 2):
        rr = r + 1 - k
        for x in range(-int(rr) - 1, int(rr) + 2):
            for z in range(-int(rr) - 1, int(rr) + 2):
                d = max(abs(x), abs(z), (abs(x) + abs(z)) / 1.42)
                if rr - 1 < d <= rr:
                    w.setze(x, 3 + H + k, z, w.b("waxed_oxidized_cut_copper" if k % 2 else "waxed_weathered_cut_copper"))
    w.setze(0, 3 + H + int(r) + 2, 0, w.b("lantern", hanging=False, waterlogged=False))
    w.setze(0, 3 + H - 1, 0, w.b("lantern", hanging=True, waterlogged=False))
    for k in range(6):
        a = k / 6 * 6.283
        x, z = round(math.cos(a) * (r + 4)), round(math.sin(a) * (r + 4))
        w.setze(x, 1, z, w.b("spruce_stairs", facing=["west", "north", "east", "south"][k % 4], half="bottom",
                             shape="straight", waterlogged=False))
    return w


def orangerie(seed, g=2):
    """Orangerie: ein langgestreckter Glaspalast mit gewölbtem Glasdach und Mittelkuppel, darin Zitrusbäume in
    Kübeln, ein Brunnen und Kieswege, davor ein barocker Garten."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.25)
    a, b = _r(9 * u + 4), _r(3 * u + 2)
    H = _r(3 * u + 3)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.setze(x, 0, z, w.b("gravel" if abs(z) <= 1 else "grass_block", snowy=False) if abs(z) <= 1 else
                    w.b("grass_block", snowy=False))
            if abs(x) == a or abs(z) == b:
                for y in range(1, H + 1):
                    pf = x % 3 == 0 or abs(x) == a
                    w.setze(x, y, z, w.b("white_concrete") if pf else w.b("glass"))
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            hb = math.sqrt(max(0, 1 - (z / (b + 0.5)) ** 2)) * b * 0.8
            y = H + 1 + round(hb)
            w.setze(x, y, z, w.b("white_concrete") if x % 3 == 0 else w.b("glass"))
    rk = b + 1.5
    for x in range(-int(rk) - 1, int(rk) + 2):
        for z in range(-int(rk) - 1, int(rk) + 2):
            for y in range(0, int(rk) + 1):
                d = math.sqrt(x * x + (y * 1.2) ** 2 + z * z)
                if rk - 1 < d <= rk:
                    w.setze(x, H + 2 + y, z, w.b("white_concrete") if (x == 0 or z == 0) else w.b("glass"))
    for x in range(-a + 2, a - 1, 3):
        for z in (-b + 1, b - 1):
            w.setze(x, 1, z, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False))
            w.setze(x, 2, z, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False))
            w.setze(x, 3, z, w.b("chipped:orange_oak_leaves") if False else w.b("flowering_azalea_leaves",
                                                                                 persistent=True, distance=1,
                                                                                 waterlogged=False))
    w.setze(0, 1, 0, w.b("water_cauldron", level=3))
    for x in range(-a, a + 1, 2):
        for z in (b + 3, b + 5):
            w.setze(x, 1, z, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
    return w


def wasserturm(seed, g=2):
    """Wasserturm: ein schlanker Backsteinschaft mit Lisenen trägt einen runden, mit Holz verschalten Wasserbehälter
    unter einem Kegeldach, eine Außentreppe und Rohre führen hinauf."""
    w = _neu(seed)
    u = U[g]
    R = _r(9 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.35)
    st = stil(w, "backstein")
    H = _r(14 * u + 7)
    r = _r(2 * u + 1.5)
    P.turm(w, st, 0, 0, 1, H, r, form="rund", dach="platt", krone=False, fenster=4)
    rb = r + 2.5 * u + 1
    hb = _r(4 * u + 3)
    for y in range(H + 1, H + 1 + hb):
        for x in range(-int(rb) - 1, int(rb) + 2):
            for z in range(-int(rb) - 1, int(rb) + 2):
                d = math.hypot(x, z)
                if rb - 1 < d <= rb:
                    w.setze(x, y, z, w.b("stripped_spruce_log", axis="y") if (x + z) % 4 == 0 else
                            w.b("spruce_planks"))
        if (y - H) % 2 == 0:
            for k in range(int(rb * 7)):
                a = k / (rb * 7) * 6.283
                w.setze(round(math.cos(a) * (rb + 0.6)), y, round(math.sin(a) * (rb + 0.6)), w.b("iron_bars",
                        north=False, south=False, east=False, west=False, waterlogged=False), False)
    for k in range(int(rb) + 2):
        rr = rb + 1 - k
        for x in range(-int(rr) - 1, int(rr) + 2):
            for z in range(-int(rr) - 1, int(rr) + 2):
                if rr - 1 < math.hypot(x, z) <= rr:
                    w.setze(x, H + 1 + hb + k, z, w.b("deepslate_tiles"))
    for y in range(1, H + 1):
        w.setze(r + 1, y, 1, w.b("copper_block" if y % 6 else "cut_copper"))
    return w


def uhrturm(seed, g=2):
    """Uhrturm: ein frei stehender, schlanker Turm mit vier großen Zifferblättern, offener Glockenstube mit
    Spitzbögen und hohem Kupferhelm, am Fuß ein Brunnen und Bänke."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.3)
    pflaster(w, -R + 3, -R + 3, R - 3, R - 3)
    st = P.Stil(w, wand="kalkstein", sockel="graustein", gesims="stone_brick", dach="kupfer", holz="dark_oak")
    a = _r(2 * u + 1.5)
    H = _r(18 * u + 8)
    spitze = P.turm(w, st, 0, 0, 1, H, a, form="eckig", dach="nadel", krone=False, fenster=4)
    yu = H - 4
    for seite, (x, z) in (("south", (0, a)), ("north", (0, -a)), ("east", (a, 0)), ("west", (-a, 0))):
        uhr(w, x, yu, z, seite)
    for k in range(4):
        x, z = [(-a - 3, 0), (a + 3, 0), (0, -a - 3), (0, a + 3)][k]
        w.setze(x, 1, z, w.b("spruce_stairs", facing=["east", "west", "south", "north"][k], half="bottom",
                             shape="straight", waterlogged=False))
    return w


def bibliothek(seed, g=2):
    """Bibliothek: ein klassizistisches Gebäude mit Säulenportikus, Freitreppe und Dreiecksgiebel, hohe
    Bogenfenster, im Inneren Regalgalerien und Lesepulte unter einer Glaskuppel."""
    w = _neu(seed)
    u = U[g]
    R = _r(15 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.25)
    a, b = _r(7 * u + 3), _r(5 * u + 3)
    st = stil(w, "marmor", fensterart="bogen")
    top = P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=5, dach="flach", sockel_h=2, pilaster=3, gauben=False,
                     kamine=0, tuer="south")
    H = 2 + 2 * 5 + 1
    for x in range(-a + 2, a - 1, 2):
        for y in range(3, H):
            w.setze(x, y, b + 3, w.b("quartz_pillar", axis="y"))
    for x in range(-a + 1, a):
        for z in range(b + 1, b + 4):
            w.setze(x, 2, z, w.b("smooth_quartz"))
            w.setze(x, H, z, w.b("smooth_quartz"))
        gh = max(0, (a - 1 - abs(x)) // 2)
        for y in range(H + 1, H + 1 + gh):
            w.setze(x, y, b + 3, w.b("quartz_bricks"))
        w.setze(x, H + 1 + gh, b + 3, w.b("quartz_slab", type="bottom", waterlogged=False))
    for k in range(3):
        for x in range(-a + 1, a):
            w.setze(x, 1 - k + 1, b + 4 + k, w.b("quartz_stairs", facing="north", half="bottom", shape="straight",
                                                  waterlogged=False))
    rk = _r(3 * u + 2)
    for x in range(-rk, rk + 1):
        for z in range(-rk, rk + 1):
            for y in range(0, rk + 1):
                d = math.sqrt(x * x + y * y + z * z)
                if rk - 1 < d <= rk:
                    w.setze(x, H + 1 + y, z, w.b("glass") if (x + z) % 3 else w.b("waxed_oxidized_copper"))
    for x in range(-a + 1, a):
        for z in (-b + 1, b - 1):
            for y in range(3, 8):
                w.setze(x, y, z, w.b("bookshelf"), False)
    return w


def theater(seed, g=2):
    """Theater: ein prächtiger Bau mit runder Fassade, Kolonnade, Freitreppe, Balkon über dem Eingang und einer
    flachen Kuppel, Plakatsäulen und Laternen auf dem Vorplatz."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.2)
    st = P.Stil(w, wand="ockerputz", sockel="graustein", gesims="stone_brick", dach="kupfer", holz="dark_oak",
                fensterart="bogen")
    a, b = _r(6 * u + 3), _r(6 * u + 3)
    P.gebaeude(w, st, -a, -b - 2, a, b - 2, y0=1, etagen=2, eh=5, dach="walm", sockel_h=1, gauben=False, kamine=0,
               tuer="south", pilaster=2)
    rr = a + 1
    for k in range(int(rr * 3.2)):
        t = k / int(rr * 3.2) * math.pi
        x, z = round(math.cos(t) * rr), b - 2 + round(math.sin(t) * rr * 0.6)
        for y in range(2, 11):
            if k % 2 == 0:
                w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
        w.setze(x, 11, z, w.b("smooth_quartz"))
        w.setze(x, 1, z, w.b("smooth_quartz"))
    pflaster(w, -R + 3, b + 4, R - 3, R - 3)
    for x in (-a - 2, a + 2):
        for y in range(1, 4):
            w.setze(x, y, b + 6, w.b("white_terracotta" if y < 3 else "red_terracotta"))
        w.setze(x, 4, b + 6, w.b("lantern", hanging=False, waterlogged=False))
    return w


def postamt(seed, g=1):
    """Postamt: ein gelb verputztes Eckgebäude mit Schalterhalle, großem Posthorn-Schild, Briefkästen, einem
    Kutschenstellplatz und einem kleinen Glockentürmchen."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.25)
    st = P.Stil(w, wand=Mat(w, ["yellow_terracotta", "smooth_sandstone", "yellow_terracotta", "end_stone"]),
                sockel="graustein", gesims="stone_brick", dach="schiefer", holz="spruce")
    a, b = _r(5 * u + 3), _r(4 * u + 2)
    top = P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="walm", sockel_h=1, gauben=True, kamine=1,
                     tuer="south")
    for x in (-2, 2):
        w.setze(x, 2, b + 1, w.b("blue_concrete"))
        w.setze(x, 3, b + 1, w.b("blue_concrete") if x < 0 else w.b("yellow_concrete"))
    for x in range(-1, 2):
        w.setze(x, 7, b + 1, w.b("yellow_concrete" if x else "gold_block"))
    P.turm(w, st, 0, 0, top - 1, _r(3 * u + 2), 1, form="eckig", dach="nadel", krone=False, fenster=99,
           schiessscharten=False)
    pflaster(w, -a, b + 2, a, b + 6)
    return w


def museum(seed, g=2):
    """Museum: ein Säulentempel als Museum mit breiter Freitreppe, Rundbogenfenstern, einem Dinosaurier-Skelett in
    der Eingangshalle hinter Glas und Statuen auf Sockeln."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.2)
    a, b = _r(8 * u + 4), _r(5 * u + 3)
    st = stil(w, "marmor", fensterart="bogen")
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=5, dach="walm", sockel_h=2, gauben=False, kamine=0,
               tuer="south", pilaster=3)
    for x in range(-a, a + 1, 2):
        for y in range(3, 12):
            w.setze(x, y, b + 3, w.b("quartz_pillar", axis="y"))
    for x in range(-a, a + 1):
        for z in range(b + 1, b + 4):
            w.setze(x, 12, z, w.b("smooth_quartz"))
            w.setze(x, 2, z, w.b("smooth_quartz"))
    for k in range(2):
        for x in range(-a, a + 1):
            w.setze(x, 2 - k, b + 4 + k, w.b("quartz_stairs", facing="north", half="bottom", shape="straight",
                                              waterlogged=False))
    from skulptur import Skulptur, kap, ell
    from weltwunder import bl
    S = Skulptur(w, 0.6 * u + 0.4)
    S.mat("k", bl(w, "bone_block"))
    S.plus(kap((-5, 4, 0), (4, 5, 0), 0.5), "k")
    S.plus(kap((4, 5, 0), (7, 7, 0), 0.4), "k")
    S.plus(ell(7.5, 7.5, 0, 1.2, 0.8, 0.7), "k")
    S.plus(kap((-5, 4, 0), (-9, 2, 0), 0.4, 0.2), "k")
    for x0 in (-2, 2):
        S.plus(kap((x0, 4.5, 0.8), (x0, 0, 1.2), 0.4), "k")
        S.plus(kap((x0, 4.5, -0.8), (x0, 0, -1.2), 0.4), "k")
    for k in range(5):
        S.plus(kap((-2 + k, 5, 0), (-2 + k, 3, 1.6), 0.25), "k")
        S.plus(kap((-2 + k, 5, 0), (-2 + k, 3, -1.6), 0.25), "k")
    S.rendern((-10, -1, -3), (10, 9, 3), versatz=(0.5, 3, b + 7.5))
    for x in (-a - 2, a + 2):
        for y in (1, 2):
            w.setze(x, y, b + 4, w.b("polished_andesite"))
        w.setze(x, 3, b + 4, w.b("chiseled_quartz_block"))
    return w


def bootshaus(seed, g=1):
    """Bootshaus: ein hölzernes Bootshaus auf Pfählen über einem See, mit offener Wasserseite, darin ein Ruderboot,
    darüber ein Aufenthaltsraum mit Balkon, ein Steg mit Laternen."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d > R:
                continue
            if z > -R * 0.3:
                for y in (-2, -1, 0):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -3, z, w.b("sand"))
            else:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
                w.setze(x, -1, z, w.b("dirt"))
    a, b = _r(3 * u + 2), _r(4 * u + 3)
    z0 = -round(R * 0.3) - 1
    for x in range(-a, a + 1):
        for z in range(z0, z0 + 2 * b + 1):
            if abs(x) == a and (z - z0) % 3 == 0:
                for y in range(-2, 4):
                    w.setze(x, y, z, w.b("stripped_spruce_log", axis="y"))
            elif abs(x) == a:
                for y in range(2, 4):
                    w.setze(x, y, z, w.b("spruce_planks"))
            w.setze(x, 4, z, w.b("spruce_planks"))
    st = stil(w, "holz_dunkel", dach="dunkelholz")
    P.gebaeude(w, st, -a, z0, a, z0 + 2 * b, y0=5, etagen=1, eh=4, dach="sattel", first_x=False, sockel_h=0,
               gauben=False, kamine=0, tuer="north")
    for x in range(-a - 1, a + 2):
        w.setze(x, 5, z0 + 2 * b + 1, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x, 6, z0 + 2 * b + 1, w.b("spruce_fence", north=False, south=False, east=True, west=True,
                                          waterlogged=False))
    from boote import ruderboot
    einfuegen(w, ruderboot(seed, 0), 0, 0, z0 + b)
    for k in range(_r(6 * u + 3)):
        for x in (a + 2, a + 3):
            w.setze(x, 1, z0 + k, w.b("spruce_planks"))
        if k % 3 == 0:
            w.setze(a + 3, 2, z0 + k, w.b("lantern", hanging=False, waterlogged=False))
    return w


def wetterstation(seed, g=1):
    """Wetterstation: ein kleines Steinhaus auf einem Hügel mit Messturm, Windfahne, Windmesser, Regenmesser,
    einer weißen Wetterhütte mit Lamellen und einem Funkmast."""
    w = _neu(seed)
    u = U[g]
    R = _r(6 * u + 5)
    from gewaesser import Land
    L = Land(w, R)
    L.heben(lambda x, z, h: round(3 * u * max(0, 1 - math.hypot(x, z) / R)))
    L.bauen(unten=-1)
    L.bepflanzen(0.35)
    hb = L.h.get((0, 0), 0)
    st = stil(w, "stein_schiefer")
    P.gebaeude(w, st, -3, -2, 3, 2, y0=hb + 1, etagen=1, eh=4, dach="sattel", sockel_h=0, gauben=False, kamine=1)
    H = _r(10 * u + 6)
    for y in range(hb + 1, hb + H):
        for (x, z) in ((5, -1), (5, 1)):
            w.setze(x, y, z, w.b("iron_bars", north=True, south=True, east=False, west=False, waterlogged=False))
        if y % 3 == 0:
            w.setze(5, y, 0, w.b("iron_block"))
    for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        w.setze(5 + dx, hb + H, dz, w.b("lightning_rod", facing="east" if dx > 0 else "west" if dx < 0 else
                                         "south" if dz > 0 else "north", powered=False, waterlogged=False))
    w.setze(5, hb + H, 0, w.b("iron_block"))
    w.setze(5, hb + H + 1, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for x in range(-6, -3):
        for z in range(-1, 2):
            for y in range(hb + 1, hb + 4):
                if y == hb + 1:
                    if abs(z) == 1 and x in (-6, -4):
                        w.setze(x, y, z, w.b("birch_fence", north=False, south=False, east=False, west=False,
                                             waterlogged=False))
                    continue
                rand = x in (-6, -4) or abs(z) == 1
                if rand:
                    w.setze(x, y, z, w.b("birch_trapdoor", facing="south", half="top", open=False, powered=False,
                                         waterlogged=False) if y == hb + 2 else w.b("white_concrete"))
    w.setze(0, hb + 1, 4, w.b("cauldron"))
    return w


def kutschenstation(seed, g=2):
    """Kutschenstation: ein Gasthaus mit Pferdeställen um einen gepflasterten Hof, eine Kutsche unter dem Vordach,
    ein Tränketrog, Heuballen und ein Wegweiser an der Straße."""
    w = _neu(seed)
    u = U[g]
    R = _r(15 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.3)
    a = _r(6 * u + 4)
    pflaster(w, -a, -a, a, a)
    st = stil(w, "fachwerk_rot")
    P.gebaeude(w, st, -a, -a, a, -a + 5, y0=1, etagen=2, eh=4, dach="sattel", first_x=True, sockel_h=1, gauben=True,
               kamine=2, tuer="south")
    st2 = stil(w, "holz_dunkel")
    P.gebaeude(w, st2, -a, -a + 7, -a + 4, a, y0=1, etagen=1, eh=4, dach="sattel", first_x=False, sockel_h=0,
               gauben=False, kamine=0, tuer="east")
    for z in range(-a + 8, a, 3):
        w.setze(-a + 4, 2, z, w.b("spruce_fence_gate", facing="east", open=False, powered=False, in_wall=False))
    for x in range(2, 7):
        for z in range(1, 4):
            w.setze(x, 2 if 2 < x < 6 else 1, z, w.b("spruce_planks") if 2 < x < 6 else w.b("dark_oak_log",
                                                                                         axis="z"))
    w.setze(4, 3, 2, w.b("red_wool"))
    for x in range(-2, 3):
        w.setze(x, 1, a - 1, w.b("water_cauldron", level=3) if x % 2 == 0 else w.b("hay_block", axis="y"))
    for y in range(1, 4):
        w.setze(a + 2, y, a + 2, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
    w.setze(a + 3, 3, a + 2, w.b("spruce_planks"))
    return w


def torhaus(seed, g=2):
    """Torhaus: ein Fachwerktorhaus über einer Durchfahrt mit Spitzbogen, zwei Stockwerke mit Erkern, ein
    Uhrgiebel, beidseits ein Stück Stadtmauer und ein Brunnen vor dem Tor."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.3)
    st = stil(w, "fachwerk_ocker")
    a, b = _r(3.5 * u + 2), _r(3 * u + 2)
    st_u = stil(w, "stein_schiefer")
    P.gebaeude(w, st_u, -a, -b, a, b, y0=1, etagen=1, eh=5, dach="flach", sockel_h=1, gauben=False, kamine=0)
    for z in range(-b - 1, b + 2):
        for x in range(-1, 2):
            for y in range(1, 6):
                if y < 5 or x == 0:
                    w.bloecke.pop((x, y, z), None)
    P.gebaeude(w, st, -a - 1, -b - 1, a + 1, b + 1, y0=7, etagen=2, eh=4, dach="sattel", first_x=False, sockel_h=0,
               gauben=True, kamine=1, steil=True)
    uhr(w, 0, 16, b + 1, "south")
    M = Mat(w, "graustein")
    for x in list(range(-R, -a - 1)) + list(range(a + 2, R + 1)):
        for z in (-1, 0, 1):
            for y in range(1, _r(5 * u + 3)):
                w.setze(x, y, z, M(x, y, z, 0.5))
        if x % 2 == 0:
            w.setze(x, _r(5 * u + 3), -1, M(x, 0, 0, 0.9))
    for z in range(-R, R + 1):
        for x in range(-1, 2):
            if abs(z) > b + 1:
                w.bloecke.pop((x, 1, z), None)
                w.setze(x, 0, z, w.b("cobblestone"))
    return w


def brauerei(seed, g=2):
    """Brauerei: ein Backsteinbau mit hohem Schornstein, einem Sudhaus mit Kupferkessel hinter großen Fenstern,
    Fässerstapeln, einem Lastenaufzug am Speicher und einem Biergarten mit Tischen unter Kastanien."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.3)
    st = stil(w, "backstein", fensterart="bogen")
    a, b = _r(6 * u + 3), _r(4 * u + 2)
    top = P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=3, eh=4, dach="sattel", first_x=True, sockel_h=1, gauben=True,
                     kamine=0, tuer="south")
    for y in range(1, top + _r(8 * u + 4)):
        for x in (a + 2, a + 3):
            for z in (-1, 0):
                w.setze(x, y, z, w.b("bricks" if y % 8 else "stone_bricks"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            for y in range(2, 5):
                if x * x + z * z <= 4 + (1 if y == 3 else 0):
                    w.setze(x, y, z, w.b("copper_block" if y < 4 else "cut_copper"))
    for k in range(6):
        x, z = -a - 2 - (k % 2), -b + k
        w.setze(x, 1 + (k // 3), z, w.b("barrel", facing="east", open=False))
    for y in range(2, 13):
        w.setze(-a + 2, y, b + 1, w.b("chain", axis="y", waterlogged=False), False)
    for (x, z) in ((-a, b + 5), (0, b + 5), (a, b + 5)):
        w.setze(x, 1, z, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
        w.setze(x, 2, z, w.b("spruce_pressure_plate", powered=False))
        w.setze(x - 1, 1, z, w.b("spruce_stairs", facing="east", half="bottom", shape="straight", waterlogged=False))
        w.setze(x + 1, 1, z, w.b("spruce_stairs", facing="west", half="bottom", shape="straight", waterlogged=False))
    einfuegen(w, wald2.laubbaum(seed, "dark_oak", H=_r(8 * u + 5)), a + 4, 0, b + 7)
    return w


def seilbahnstation(seed, g=2):
    """Seilbahnstation: eine Bergstation aus Holz und Stein auf einer Felskuppe, eine große Seilscheibe, zwei
    Tragseile führen talwärts zu einem Stützmast, an ihnen hängt eine rote Gondel."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    from gewaesser import Land
    L = Land(w, R)
    L.heben(lambda x, z, h: round(max(0, (-x / R + 0.3)) * 10 * u))
    L.bauen(unten=-1)
    L.bepflanzen(0.3)
    hb = L.h.get((-round(R * 0.5), 0), 0)
    st = stil(w, "holz_dunkel")
    cx = -round(R * 0.5)
    P.gebaeude(w, st, cx - 4, -4, cx + 4, 4, y0=hb + 1, etagen=1, eh=5, dach="sattel", first_x=True, sockel_h=1,
               gauben=False, kamine=0)
    rr = 3 * u + 1
    for k in range(int(rr * 8)):
        t = k / (rr * 8) * 6.283
        w.setze(cx + 5 + round(math.cos(t) * rr), hb + 7, round(math.sin(t) * rr), w.b("iron_block"))
    mx = round(R * 0.7)
    mh = L.h.get((mx, 0), 0)
    for y in range(mh + 1, hb + 8):
        w.setze(mx, y, 0, w.b("iron_bars", north=True, south=True, east=False, west=False, waterlogged=False)
                if y % 3 else w.b("iron_block"))
    for z in (-1, 1):
        w.setze(mx, hb + 7, z, w.b("iron_block"))
        linie(w, (cx + 5, hb + 7, z), (mx, hb + 7, z), w.b("chain", axis="x", waterlogged=False))
    gx = (cx + 5 + mx) // 2
    for y in range(hb + 3, hb + 7):
        w.setze(gx, y, 1, w.b("chain", axis="y", waterlogged=False))
    for x in range(gx - 2, gx + 3):
        for z in range(0, 3):
            for y in range(hb, hb + 3):
                rand = abs(x - gx) == 2 or z in (0, 2) or y in (hb, hb + 2)
                if rand:
                    w.setze(x, y, z, w.b("glass_pane", north=True, south=True, east=False, west=False,
                                         waterlogged=False) if y == hb + 1 and abs(x - gx) < 2 else w.b("red_concrete"))
    return w


def universitaet(seed, g=3):
    """Universität: ein großer Vierflügelbau aus hellem Stein um einen Innenhof mit Kreuzgang, ein hoher Turm
    mit Kuppel über dem Hauptportal, Fahnen, ein Rasen mit Statue."""
    w = _neu(seed)
    u = U[g]
    R = _r(20 * u + 8)
    gelaende(w, R, art="wiese", dichte=0.2)
    st = stil(w, "marmor", fensterart="bogen", dach="schiefer")
    A = _r(10 * u + 6)
    t = _r(2.5 * u + 3)
    for (x0, z0, x1, z1, tu) in ((-A, -A, A, -A + t, "north"), (-A, A - t, A, A, "south"),
                                 (-A, -A + t + 1, -A + t, A - t - 1, "west"), (A - t, -A + t + 1, A, A - t - 1, "east")):
        P.gebaeude(w, st, x0, z0, x1, z1, y0=1, etagen=2, eh=5, dach="sattel", sockel_h=1, gauben=True, kamine=1,
                   tuer=tu)
    for x in range(-A + t + 1, A - t):
        for z in range(-A + t + 1, A - t):
            w.setze(x, 0, z, w.b("grass_block", snowy=False))
            if abs(x) == A - t - 1 or abs(z) == A - t - 1:
                for y in range(1, 4):
                    if (x + z) % 3 == 0:
                        w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
                w.setze(x, 4, z, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
    for y in range(1, 4):
        w.setze(0, y, 0, w.b("polished_andesite" if y < 3 else "chiseled_quartz_block"))
    P.turm(w, P.Stil(w, wand="marmor", sockel="kalkstein", gesims="quartz", dach="kupfer", holz="dark_oak"), 0, A + 2,
           1, _r(20 * u + 8), _r(2.5 * u + 1.5), form="eckig", dach="kuppel", krone=False, fenster=5)
    return w


def kaufhaus(seed, g=2):
    """Kaufhaus: ein vierstöckiges Warenhaus mit großen Schaufenstern im Erdgeschoss, bunten Markisen,
    Jugendstil-Erker an der Ecke mit Kuppel und Fahnenmast, Leuchtschrift aus Laternen."""
    w = _neu(seed)
    u = U[g]
    R = _r(15 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.15)
    st = P.Stil(w, wand="kalkstein", sockel="graustein", gesims="stone_brick", dach="kupfer", holz="dark_oak",
                fensterart="bogen")
    a, b = _r(7 * u + 4), _r(5 * u + 3)
    top = P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=4, eh=4, dach="mansarde", sockel_h=1, gauben=True,
                     kamine=0, tuer="south", pilaster=4)
    for x in range(-a + 1, a):
        if abs(x) <= 1:
            continue
        for y in (2, 3, 4):
            w.setze(x, y, b, w.b("glass_pane", east=True, west=True, north=False, south=False, waterlogged=False))
        w.setze(x, 5, b + 1, w.b(["red_wool", "white_wool"][(x // 2) % 2]))
    P.turm(w, st, a, b, 1, top + 3, _r(1.6 * u + 1), form="rund", dach="zwiebel", krone=False, fenster=4)
    for x in range(-3, 4):
        w.setze(x, top - 2, b + 1, w.b("lantern", hanging=False, waterlogged=False) if x % 2 == 0 else
                w.b("gold_block"))
    pflaster(w, -a - 3, b + 2, a + 3, b + 6)
    return w


def grandhotel(seed, g=3):
    """Grandhotel: ein symmetrischer, fünfstöckiger Prachtbau mit Mittelrisalit, Kuppeltürmen an den Ecken,
    Balkonreihen, Vordach mit Säulen, einer Auffahrt mit Springbrunnen und gestutzten Bäumchen."""
    w = _neu(seed)
    u = U[g]
    R = _r(20 * u + 8)
    gelaende(w, R, art="wiese", dichte=0.2)
    st = P.Stil(w, wand=Mat(w, ["white_terracotta", "smooth_quartz", "calcite", "white_terracotta"]),
                sockel="graustein", gesims="quartz", dach="schiefer", holz="dark_oak", fensterart="bogen")
    a, b = _r(10 * u + 5), _r(4 * u + 3)
    top = P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=5, eh=4, dach="mansarde", sockel_h=1, gauben=True, kamine=2,
                     tuer="south", pilaster=3)
    for x in (-a, a):
        P.turm(w, st, x, b, 1, top + 2, _r(2 * u + 1), form="eckig", dach="kuppel", krone=False, fenster=4)
    for e in range(1, 5):
        y = 1 + 1 + e * 4
        for x in range(-a + 2, a - 1):
            if x % 3 == 0:
                w.setze(x, y, b + 1, w.b("quartz_slab", type="top", waterlogged=False))
                w.setze(x, y + 1, b + 1, w.b("iron_bars", east=True, west=True, north=False, south=False,
                                             waterlogged=False))
    for x in (-3, 3):
        for y in range(1, 5):
            w.setze(x, y, b + 4, w.b("quartz_pillar", axis="y"))
    for x in range(-3, 4):
        for z in range(b + 1, b + 5):
            w.setze(x, 5, z, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
    fx, fz = 0, b + 10
    for x in range(-3, 4):
        for z in range(-3, 4):
            d = math.hypot(x, z)
            if d <= 3.3:
                w.setze(fx + x, 1, fz + z, w.b("water", level=0) if d < 2.4 else w.b("smooth_quartz"))
    for y in range(1, 4):
        w.setze(fx, y, fz, w.b("quartz_pillar", axis="y"))
    w.setze(fx, 4, fz, w.b("water", level=0))
    for k in range(6):
        x = -a + 2 + k * (2 * a - 4) // 5
        w.setze(x, 1, b + 7, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False))
        w.setze(x, 2, b + 7, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
    return w


GEBAEUDE2 = {
    "bahnhof": ("Bahnhof", bahnhof),
    "feuerwache": ("Feuerwache", feuerwache),
    "markthalle": ("Markthalle", markthalle),
    "musikpavillon": ("Musikpavillon", musikpavillon),
    "orangerie": ("Orangerie", orangerie),
    "wasserturm": ("Wasserturm", wasserturm),
    "uhrturm": ("Uhrturm", uhrturm),
    "bibliothek": ("Bibliothek", bibliothek),
    "theater": ("Theater", theater),
    "postamt": ("Postamt", postamt),
    "museum": ("Museum", museum),
    "bootshaus": ("Bootshaus", bootshaus),
    "wetterstation": ("Wetterstation", wetterstation),
    "kutschenstation": ("Kutschenstation", kutschenstation),
    "torhaus": ("Torhaus", torhaus),
    "brauerei": ("Brauerei", brauerei),
    "seilbahnstation": ("Seilbahnstation", seilbahnstation),
    "universitaet": ("Universität", universitaet),
    "kaufhaus": ("Kaufhaus", kaufhaus),
    "grandhotel": ("Grandhotel", grandhotel),
}

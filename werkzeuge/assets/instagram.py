"""Instagram – eigene Nachbauten von Bau-Ideen, die auf Instagram gesammelt wurden (keine 1:1-Kopien):
Alchemistenturm, Türkis-Gehöft mit Wimpelturm, Stelzen-Außenposten, Kirschblütental mit Bogenbrücke, Hexenladen
mit Kürbisdach, Riesenhand im Meer, Schattenzitadelle, Rosenanwesen mit Glaskuppel, Herbsthof am Wasserfall,
Himmelsschmiede, Karmesin-Lodge, Mandarinvilla, Schwertschmiede, Efeuturm, Fischerhütte auf Stelzen,
Freibeuter-Brigg und Totenkopf-Atoll. Boden y = 0."""

from __future__ import annotations

import math

import numpy as np

import pracht as P
import wald2
from flora import _lv, _neu, _r, _stil, linie
from gewaesser import Land
from haeuser import HAUSPOOL
from lib import Rauschen, einfuegen
from pracht import Mat, gelaende
from veredeln import bewuchs

U = [0.6, 1.0, 1.7, 2.8]


# ============================================================================ Bausteine

def stil(w, pool=None, **kw):
    d = dict(HAUSPOOL[pool]) if pool else {}
    d.update(kw)
    return P.Stil(w, **d)


def zaun(w, name, ax=None):
    return w.b(name, east=ax == "x", west=ax == "x", north=ax == "z", south=ax == "z", waterlogged=False)


def laterne(w, haengend=False, seele=False):
    return w.b("soul_lantern" if seele else "lantern", hanging=haengend, waterlogged=False)


def kette(w, ax="y"):
    return w.b("chain", axis=ax, waterlogged=False)


def fachwerkhaus(w, x0, z0, x1, z1, y0, unten="graustein", pool="fachwerk_ocker", etagen=2, eh=4, dach="schiefer",
                 ueberhang=1, steil=True, sockel_etagen=1, kamine=1, gauben=True, first_x=None, tuer="south"):
    """Steinernes Erdgeschoss, darüber auskragende Fachwerketagen mit steilem Dach. Gibt die Firsthöhe zurück."""
    st_u = stil(w, wand=unten, sockel="graustein", gesims="stone_brick", dach=dach, holz="spruce")
    yo = y0
    if sockel_etagen:
        P.gebaeude(w, st_u, x0, z0, x1, z1, y0=y0, etagen=sockel_etagen, eh=eh, dach="flach", tuer=tuer,
                   sockel_h=1, gauben=False, kamine=0)
        yo = y0 + 1 + sockel_etagen * eh
    st_o = stil(w, pool, dach=dach)
    o = ueberhang
    return P.gebaeude(w, st_o, x0 - o, z0 - o, x1 + o, z1 + o, y0=yo, etagen=etagen, eh=eh, dach="sattel",
                      first_x=first_x, tuer=tuer, sockel_h=0, gauben=gauben, kamine=kamine, steil=steil)


def kranarm(w, x, y, z, dx, dz, L, last=None, holz="spruce"):
    """Hölzerner Kranbalken mit Strebe, Kette und Last."""
    for k in range(L + 1):
        w.setze(x + dx * k, y, z + dz * k, w.b(f"stripped_{holz}_log", axis="x" if dx else "z"))
    for k in range(1, min(L, 4)):
        w.setze(x + dx * k, y - k, z + dz * k, w.b(f"{holz}_fence", north=False, south=False, east=False,
                                                    west=False, waterlogged=False), False)
    ex, ez = x + dx * L, z + dz * L
    n = 3
    for k in range(1, n + 1):
        w.setze(ex, y - k, ez, kette(w))
    if last:
        last(ex, y - n - 1, ez)
    return ex, ez


def seil(w, a, b, durchhang=2.0, blk=None, fahnen=None):
    """Durchhängendes Seil (Kette) mit bunten Wimpeln."""
    n = int(max(abs(b[0] - a[0]), abs(b[2] - a[2]), abs(b[1] - a[1])) * 1.5) + 1
    letzte = None
    for i in range(n + 1):
        t = i / n
        p = [a[k] + (b[k] - a[k]) * t for k in range(3)]
        p[1] -= durchhang * 4 * t * (1 - t)
        q = (round(p[0]), round(p[1]), round(p[2]))
        if q == letzte:
            continue
        w.setze(*q, blk or w.b("chain", axis="x" if abs(b[0] - a[0]) >= abs(b[2] - a[2]) else "z",
                               waterlogged=False), False)
        if fahnen and i % 3 == 1:
            w.setze(q[0], q[1] - 1, q[2], w.b(fahnen[(i // 3) % len(fahnen)]), False)
        letzte = q


def plattform(w, x0, z0, x1, z1, y, holz="spruce", gelaender=True, stuetzen=4, boden_y=0):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, y, z, w.b(f"{holz}_planks") if (x + z) % 5 else w.b(f"stripped_{holz}_log", axis="x"))
            if gelaender and (x in (x0, x1) or z in (z0, z1)):
                w.setze(x, y + 1, z, w.b(f"{holz}_fence", north=False, south=False, east=False, west=False,
                                         waterlogged=False), False)
    for x in range(x0, x1 + 1, stuetzen):
        for z in (z0, z1):
            for yy in range(boden_y, y):
                w.setze(x, yy, z, w.b(f"stripped_{holz}_log", axis="y"), False)
    for z in range(z0, z1 + 1, stuetzen):
        for x in (x0, x1):
            for yy in range(boden_y, y):
                w.setze(x, yy, z, w.b(f"stripped_{holz}_log", axis="y"), False)


def efeu(w, anteil=0.08, laub=0.5):
    """Efeu an Wänden: Ranken und kleine Laubpolster."""
    bewuchs(w, moos=0.02, ranken=anteil)
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) == "minecraft:vine" and w.rng.random() < laub * 0.3:
            w.bloecke[(x, y, z)] = _lv(w, "oak" if w.rng.random() < 0.7 else "azalea")


def gewaechshaus(w, x0, z0, x1, z1, y0, holz="spruce", H=4):
    """Kleines Glashaus mit Holzrahmen und Satteldach aus Glas, darin Beete."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            rand = x in (x0, x1) or z in (z0, z1)
            w.setze(x, y0, z, w.b(f"{holz}_planks"))
            if rand:
                for y in range(y0 + 1, y0 + H):
                    pfosten = (x in (x0, x1) and z in (z0, z1)) or (x - x0) % 3 == 0 and z in (z0, z1)
                    w.setze(x, y, z, w.b(f"stripped_{holz}_log", axis="y") if pfosten else w.b("glass"))
            else:
                w.setze(x, y0 + 1, z, w.b("farmland", moisture=7) if (z - z0) % 3 else w.b(f"{holz}_slab",
                                                                                            type="bottom",
                                                                                            waterlogged=False))
                if (z - z0) % 3 and w.rng.random() < 0.8:
                    w.setze(x, y0 + 2, z, w.b(["red_tulip", "allium", "pink_tulip", "azure_bluet", "poppy"]
                                               [(x + z) % 5]))
    mx = (x0 + x1) / 2
    hb = (x1 - x0) // 2 + 1
    for k in range(hb + 1):
        for z in range(z0, z1 + 1):
            for x in (x0 + k, x1 - k):
                w.setze(x, y0 + H + k, z, w.b("glass") if z not in (z0, z1) or True else w.b("glass"))
        if x0 + k >= x1 - k:
            break
    for k in range(hb + 1):
        for x in (x0 + k, x1 - k):
            w.setze(x, y0 + H + k, z0, w.b(f"stripped_{holz}_log", axis="z"))
            w.setze(x, y0 + H + k, z1, w.b(f"stripped_{holz}_log", axis="z"))


def teich(w, cx, cz, r, seerosen=0.1, tief=2):
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            d = math.hypot(x - cx, z - cz)
            if d <= r:
                for y in range(1, 4):
                    w.bloecke.pop((x, y, z), None)
                for y in range(-tief + 1, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -tief, z, w.b("clay" if (x + z) % 3 else "gravel"))
                if w.rng.random() < seerosen:
                    w.setze(x, 1, z, w.b("lily_pad"))
            elif d <= r + 1.2:
                w.setze(x, 0, z, w.b("mossy_cobblestone" if w.rng.random() < 0.5 else "stone"))


def feuerstelle_rauch(w, x, y, z):
    w.setze(x, y, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))


# ============================================================================ Bauten

def alchemistenturm(seed, g=2):
    """Alchemistenturm: ein steinerner Turm mit Kegeldächern aus Purpur und einem Aussichtsbalkon samt Fernrohr,
    davor ein offenes Laborgeschoss mit Bücherwänden, Braustand und Zaubertisch, unten Kessel mit grünem Gebräu,
    ein Glashaus voller Blumen, Leuchtpilze und ein Teich."""
    w = _neu(seed)
    u = U[g]
    R = _r(15 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.5)
    st = stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="mcw_lila", holz="dark_oak")
    a = _r(4 * u + 3)
    b = _r(3 * u + 2)
    top = fachwerkhaus(w, -a, -b, a, b, 1, unten="graustein", pool="holz_dunkel", etagen=1, eh=4, dach="mcw_lila",
                       sockel_etagen=1, kamine=1, first_x=True)
    tr = _r(2 * u + 1.5)
    tx, tz = a - 1, -b - 1
    H = _r(16 * u + 8)
    P.turm(w, st, tx, tz, 1, H, tr, form="eckig", dach="nadel", krone=False, fenster=4)
    ry = H - 2
    for x in range(tx - tr - 2, tx + tr + 3):
        for z in range(tz - tr - 2, tz + tr + 3):
            if max(abs(x - tx), abs(z - tz)) > tr:
                w.setze(x, ry, z, w.b("dark_oak_planks"))
                if max(abs(x - tx), abs(z - tz)) == tr + 2:
                    w.setze(x, ry + 1, z, zaun(w, "dark_oak_fence"))
    w.setze(tx + tr + 1, ry + 1, tz, w.b("spyglass") if False else w.b("lightning_rod", facing="east",
                                                                       powered=False, waterlogged=False))
    w.setze(tx - tr - 2, ry - 1, tz, kette(w))
    w.setze(tx - tr - 2, ry - 2, tz, laterne(w, True, seele=True))
    # Labor im Obergeschoss: Vorderwand offen
    yl = 1 + 1 + 4
    for x in range(-a, a + 1):
        for y in range(yl + 1, yl + 4):
            w.bloecke.pop((x, y, b + 1), None)
    for x in range(-a, a + 1):
        w.setze(x, yl + 1, -b, w.b("bookshelf"))
        w.setze(x, yl + 2, -b, w.b("bookshelf") if x % 3 else w.b("brewing_stand", has_bottle_0=True,
                                                                   has_bottle_1=False, has_bottle_2=True))
    w.setze(0, yl + 1, 0, w.b("enchanting_table"))
    w.setze(-2, yl + 1, 0, w.b("purple_carpet"))
    w.setze(2, yl + 1, 0, w.b("cauldron"))
    for x in range(-a + 1, a, 3):
        w.setze(x, yl + 3, b, kette(w))
        w.setze(x, yl + 2, b, w.b("magenta_stained_glass"))
    # Hof mit Kesseln
    for i, x in enumerate((-2, 1)):
        w.setze(x, 1, b + 3, w.b("water_cauldron", level=3))
        w.setze(x, 0, b + 3, w.b("magma_block"))
        w.setze(x, 2, b + 3, w.b("lime_stained_glass") if i == 0 else w.b("purple_stained_glass"), False)
    for x in range(-3, 4):
        w.setze(x, 1, b + 5, w.b("barrel", facing="up", open=False) if x % 2 else w.b("spruce_slab",
                                                                                       type="bottom",
                                                                                       waterlogged=False))
    gewaechshaus(w, a + 3, 0, a + 3 + _r(3 * u + 3), b + 4, 0, holz="dark_oak", H=4)
    teich(w, -a + 1, b + 7, 2.5 + u, seerosen=0.15)
    for k in range(6):
        x, z = -a - 3 - k % 2, b - k
        w.setze(x, 1, z, w.b("warped_fungus" if k % 2 else "brown_mushroom"))
    for k in range(int(4 * u)):
        y = yl + 4
        w.setze(-a - 1, y - k, 0, w.b("vine", north=False, south=False, east=True, west=False, up=False), False)
    efeu(w, 0.05)
    return w


def tuerkis_gehoeft(seed, g=2):
    """Türkis-Gehöft: ein großes Fachwerkhaus mit verschachtelten türkisen Prismarin-Dächern, Gauben und
    Wimpelstange, daneben ein runder Steinturm mit offener Holzgalerie und Schieferhelm; ein Wimpelseil spannt sich
    vom Turm zum Dachfirst."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.4)
    a = _r(5 * u + 3)
    b = _r(3.5 * u + 2)
    top = fachwerkhaus(w, -a, -b, a, b, 1, unten="graustein", pool="fachwerk_ocker", etagen=2, eh=4, dach="blau",
                       sockel_etagen=1, first_x=True)
    fachwerkhaus(w, -a + 1, b + 2, -a + 1 + _r(3 * u + 2), b + 2 + _r(3 * u + 2), 1, pool="fachwerk_ocker",
                 etagen=1, eh=4, dach="blau", sockel_etagen=1, first_x=False, gauben=False)
    st = stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="spruce")
    tx, tz = a + _r(3 * u + 2), 0
    tr = _r(2.4 * u + 1.5)
    H = _r(14 * u + 8)
    spitze = P.turm(w, st, tx, tz, 1, H, tr, form="rund", dach="kegel", krone=False, fenster=4)
    # offene Galerie unter dem Helm
    gy = H - 3
    for k in range(int((tr + 1) * 8)):
        t = k / ((tr + 1) * 8) * 6.283
        x, z = tx + round(math.cos(t) * (tr + 1)), tz + round(math.sin(t) * (tr + 1))
        w.setze(x, gy, z, w.b("spruce_planks"))
        w.setze(x, gy + 1, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                  waterlogged=False))
        if k % 4 == 0:
            for y in range(gy + 1, gy + 4):
                w.setze(x, y, z, w.b("stripped_spruce_log", axis="y"))
    for y in range(spitze + 1, spitze + 4):
        w.setze(tx, y, tz, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(tx + 1, spitze + 3, tz, w.b("red_wool"))
    w.setze(tx + 2, spitze + 3, tz, w.b("red_wool"))
    w.setze(tx + 1, spitze + 2, tz, w.b("red_wool"))
    for y in range(top + 1, top + 4):
        w.setze(-a + 1, y, 0, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                  waterlogged=False))
    w.setze(-a + 2, top + 3, 0, w.b("red_wool"))
    seil(w, (tx, spitze + 1, tz), (-a + 1, top + 2, 0), durchhang=3, blk=w.b("spruce_fence", north=False,
                                                                                south=False, east=True, west=True,
                                                                                waterlogged=False))
    for x in range(-a, a + 1, 2):
        w.setze(x, 6, b + 2, w.b("flowering_azalea_leaves", persistent=True, distance=1, waterlogged=False), False)
    return w


def stelzen_aussenposten(seed, g=2):
    """Stelzen-Außenposten: ein weißer, massiver Felsturm, umgeben von mehreren Holzdecks auf schlanken
    Stelzen, zwei Ladekräne mit hängenden Käfigen, darüber zwei grün verkleidete Wohngeschosse mit Schieferdach,
    Treppen aus Stein am Fuß."""
    w = _neu(seed)
    u = U[g]
    R = _r(15 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.25)
    M = Mat(w, ["calcite", "diorite", "smooth_quartz", "polished_diorite", "white_terracotta"])
    a = _r(3.5 * u + 2)
    H = _r(9 * u + 5)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            for y in range(1, H + 1):
                if abs(x) == a or abs(z) == a or y == H:
                    w.setze(x, y, z, M(x, y, z, y / H))
    for y in range(1, 4):
        w.bloecke.pop((0, y, a), None)
    w.setze(0, 1, a, w.b("spruce_door", facing="south", half="lower", hinge="left", open=False, powered=False))
    w.setze(0, 2, a, w.b("spruce_door", facing="south", half="upper", hinge="left", open=False, powered=False))
    # Decks auf Stelzen
    ebenen = [(H - 2, a + _r(4 * u + 2)), (H + 3, a + _r(2.5 * u + 1))]
    for (yd, r) in ebenen:
        plattform(w, -r, -r, r, r, yd, holz="spruce", stuetzen=max(4, r), boden_y=1)
    # Seitendecks mit Kränen
    for sx in (-1, 1):
        cx = sx * (a + _r(6 * u + 3))
        plattform(w, cx - 3, -3, cx + 3, 3, H - 4, holz="spruce", stuetzen=3, boden_y=1)
        for y in range(H - 3, H + 3):
            w.setze(cx, y, 0, w.b("bricks" if y % 3 else "granite"))
        kranarm(w, cx, H + 3, 0, sx, 0, _r(3 * u + 2),
                last=lambda x, y, z: [w.setze(x, y - k, z, w.b("iron_bars", north=True, south=True, east=True,
                                                                west=True, waterlogged=False)) for k in range(2)])
    # Wohngeschosse oben
    st = stil(w, wand=Mat(w, ["moss_block", "green_terracotta", "lime_terracotta", "green_terracotta"]),
              sockel="graustein", gesims="spruce", dach="schiefer", holz="spruce", fachwerk=True)
    yo = H + 4
    hb = a + 1
    P.gebaeude(w, st, -hb, -hb, hb, hb, y0=yo, etagen=2, eh=4, dach="walm", sockel_h=0, gauben=False, kamine=1)
    # Steintreppe
    for k in range(H - 2):
        for x in range(-2, 3):
            w.setze(x - a - 3 - k // 3, min(k, H - 3), a + 2 + k, w.b("stone_brick_stairs", facing="north",
                                                                        half="bottom", shape="straight",
                                                                        waterlogged=False)) if k < 4 else None
    for k in range(H - 3):
        w.setze(a + 1, 1 + k, -a - 1 + k % 3, w.b("ladder", facing="east", waterlogged=False), False) if False else None
    for y in range(1, H - 2):
        w.setze(-a - 1, y, 0, w.b("ladder", facing="west", waterlogged=False), False)
    for (x, z) in ((-a - 3, -a - 3), (a + 3, a + 3), (a + 3, -a - 3), (-a - 3, a + 3)):
        w.setze(x, H - 1, z, laterne(w, True), False)
    return w


def kirschbluetental(seed, g=3):
    """Kirschblütental: zwei grüne Hänge voller rosa Kirschbäume, unten ein blauer Teich, darüber spannt sich eine
    geschwungene, rote Holzbogenbrücke mit überdachtem Mittelteil, Laternen und Bannern."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 8)
    Hh = _r(10 * u + 5)
    L = Land(w, R)
    L.heben(lambda x, z, h: round(Hh * min(1.0, max(0.0, (abs(x) - R * 0.18) / (R * 0.45))) ** 1.2))
    L.see(0, 0, R * 0.22, 0, tiefe=3)
    L.bauen(unten=-4)
    L.bepflanzen(dichte=0.4)
    rng = w.rng
    for k in range(int(30 * u)):
        x, z = int(rng.integers(-R, R)), int(rng.integers(-R, R))
        if (x, z) in L.h and abs(x) > R * 0.35 and (x, z) not in L.wasser:
            einfuegen(w, wald2.kirschbaum(int(rng.integers(1, 10 ** 6)), H=_r(6 * u + 4)), x, L.h[(x, z)], z)
    S = round(R * 0.62)
    D = Hh + 1
    for x in range(-S, S + 1):
        t = x / S
        y = D + round(2.5 * u * (1 - t * t))
        for z in (-2, -1, 0, 1, 2):
            w.setze(x, y, z, w.b("dark_oak_planks" if abs(z) < 2 else "stripped_mangrove_log", axis="x")
                    if abs(z) == 2 else w.b("dark_oak_planks"))
        for z in (-2, 2):
            w.setze(x, y + 1, z, w.b("mangrove_fence", north=False, south=False, east=True, west=True,
                                     waterlogged=False))
        bogen = D - 1 - round((Hh + 1) * (1 - t * t) ** 0.5 * 0.7) + round(2.5 * u * (1 - t * t))
        for z in (-2, 2):
            for yy in range(bogen, y):
                if yy == bogen or abs(x) % 5 == 0:
                    w.setze(x, yy, z, w.b("stripped_mangrove_log", axis="y"))
        if abs(x) <= S * 0.35:
            if abs(x) % 3 == 0:
                for z in (-2, 2):
                    for yy in range(y + 1, y + 5):
                        w.setze(x, yy, z, w.b("stripped_dark_oak_log", axis="y"))
            for z in range(-3, 4):
                w.setze(x, y + 5, z, w.b("dark_oak_slab", type="bottom", waterlogged=False) if abs(z) == 3 else
                        w.b("dark_oak_planks"))
            if abs(x) % 4 == 2:
                w.setze(x, y + 4, 0, laterne(w, True))
        if abs(x) == round(S * 0.35) + 1:
            for z in (-3, 3):
                for yy in range(y - 3, y + 1):
                    w.setze(x, yy, z, w.b("red_wool" if x > 0 else "purple_wool"))
    for x in range(-S - 3, -S + 1):
        for z in (-2, -1, 0, 1, 2):
            for yy in range(1, D + 1):
                w.bloecke.pop((x, yy + 1, z), None) if yy > L.h.get((x, z), 0) else None
    return w


def hexenladen(seed, g=2):
    """Hexenladen: ein runder Turm aus dunklem Stein mit krummem, hohem Hexenhut-Dach, angebaute windschiefe
    Holzhäuschen, ein Anbau mit Dach in Form eines grinsenden Kürbisses, ein Marktstand mit bunt gestreifter Markise,
    Kerzen und Kisten."""
    w = _neu(seed)
    u = U[g]
    R = _r(13 * u + 6)
    gelaende(w, R, art="wald", dichte=0.3)
    M = Mat(w, ["deepslate_bricks", "polished_deepslate", "deepslate_tiles", "cobbled_deepslate", "tuff"])
    r = _r(3 * u + 2)
    H = _r(9 * u + 5)
    for y in range(1, H + 1):
        for x in range(-r - 1, r + 2):
            for z in range(-r - 1, r + 2):
                d = math.hypot(x, z)
                if r - 0.6 < d <= r + 0.45:
                    fen = (y - 1) % 5 in (2, 3) and abs(x) <= 0 and y > 2
                    w.setze(x, y, z, w.b("orange_stained_glass_pane", north=False, south=False, east=True,
                                         west=True, waterlogged=False) if fen else M(x, y, z, y / H))
    # Hexenhut: breite Krempe, dann krumme Spitze
    yk = H + 1
    for x in range(-r - 4, r + 5):
        for z in range(-r - 4, r + 5):
            d = math.hypot(x, z)
            if d <= r + 3.5:
                w.setze(x, yk, z, w.b("dark_oak_planks" if d > r + 2.5 else "spruce_planks"))
    hh = _r(12 * u + 6)
    for k in range(hh):
        t = k / hh
        rr = (r + 1.5) * (1 - t) ** 1.2
        ox = (t ** 2.2) * (3 + 3 * u)
        for x in range(-int(rr) - 2, int(rr) + 3):
            for z in range(-int(rr) - 2, int(rr) + 3):
                if math.hypot(x - 0, z) <= rr:
                    w.setze(round(x + ox), yk + 1 + k, z, w.b("deepslate_tiles" if (x + z + k) % 4 else
                                                               "mossy_cobblestone"))
    # Anbau mit Kürbisdach
    cx = r + _r(3 * u + 2)
    P.gebaeude(w, stil(w, "holz_dunkel"), cx - 2, -2, cx + 3, 3, y0=1, etagen=1, eh=4, dach="flach", sockel_h=0,
               gauben=False, kamine=0, tuer="south")
    kr = 2.2 * u + 1.5
    for x in range(-int(kr) - 1, int(kr) + 2):
        for y in range(0, int(kr * 1.6) + 1):
            for z in range(-int(kr) - 1, int(kr) + 2):
                d = (x / kr) ** 2 + ((y - kr * 0.7) / (kr * 0.8)) ** 2 + (z / kr) ** 2
                if 0.7 < d <= 1.0:
                    gesicht = z == int(kr) and ((abs(x) in (1, 2) and y == round(kr)) or (abs(x) <= 2 and
                                                                                         y == round(kr * 0.45)))
                    w.setze(cx + 1 + x, 6 + y, z, w.b("jack_o_lantern", facing="south") if gesicht else
                            w.b("pumpkin") if (x + y) % 3 else w.b("orange_terracotta"))
    w.setze(cx + 1, 7 + int(kr * 1.6), 0, w.b("dark_oak_log", axis="y"))
    # windschiefes Häuschen links
    P.gebaeude(w, stil(w, "holz_dunkel", dach="dunkelholz"), -r - 6, -3, -r - 1, 2, y0=1, etagen=2, eh=4,
               dach="sattel", sockel_h=0, gauben=False, kamine=1, tuer="south", steil=True)
    # Marktstand mit Markise
    sx, sz = -1, r + 3
    farben = ["purple_wool", "orange_wool", "lime_wool", "magenta_wool"]
    for x in range(sx - 2, sx + 3):
        for z in (sz, sz + 2):
            pass
        w.setze(x, 1, sz + 1, w.b("spruce_planks"))
        for z in range(sz, sz + 3):
            w.setze(x, 4, z, w.b(farben[(x - sx + 2) % 4]))
    for (x, z) in ((sx - 2, sz), (sx + 2, sz), (sx - 2, sz + 2), (sx + 2, sz + 2)):
        for y in range(1, 4):
            w.setze(x, y, z, w.b("dark_oak_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False))
    for k, (x, z) in enumerate(((sx - 1, sz + 1), (sx + 1, sz + 1), (sx, sz + 1))):
        w.setze(x, 2, z, w.b("candle", candles=1 + k, lit=True, waterlogged=False) if k < 2 else
                w.b("brewing_stand", has_bottle_0=True, has_bottle_1=True, has_bottle_2=False))
    for k in range(4):
        w.setze(-r - 2 + k, 1, r + 2, w.b("barrel", facing="up", open=False) if k % 2 else w.b("chest",
                                                                                               facing="south",
                                                                                               type="single",
                                                                                               waterlogged=False))
    for k in range(5):
        x, z = r + 1 + k % 2, -r - 2 - k // 2
        w.setze(x, 1, z, w.b("candle", candles=4, lit=True, waterlogged=False) if k % 2 else w.b("white_wool"))
    efeu(w, 0.04)
    return w


def riesenhand(seed, g=3):
    """Riesenhand im Meer: eine gewaltige steinerne Hand ragt aus dem Wasser, die Finger leicht gekrümmt, auf der
    Handfläche steht eine kleine gotische Kapelle mit Glockenturm und Grabsteinen."""
    from skulptur import Skulptur, kap, ell
    from weltwunder import bl
    w = _neu(seed)
    u = U[g]
    s = 1.5 * u + 0.6
    R = _r(7.5 * s + 3)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                for y in (-2, -1, 0):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -3, z, w.b("sand"))
    S = Skulptur(w, s)
    stein = Mat(w, ["smooth_stone", "stone", "andesite", "polished_andesite", "diorite", "calcite"])
    S.mat("k", lambda x, y, z, *a: stein(x, y, z, 0.5))
    S.mat("d", bl(w, "gray_concrete"))
    S.plus(kap((0, -4, 0), (0, 5, 0), 3.2, 2.7), "k")
    S.plus(ell(0, 7.2, 0, 4.0, 2.2, 2.6), "k")
    for i, (fx, fl) in enumerate(((-2.6, 7), (-0.9, 8.5), (0.9, 8), (2.6, 6.5))):
        b1 = (fx, 8.5, 0.6)
        b2 = (fx * 1.05, 8.5 + fl * 0.6, 0.9)
        b3 = (fx * 1.08, 8.5 + fl * 0.95, 0.2)
        S.plus(kap(b1, b2, 0.95, 0.85), "k")
        S.plus(kap(b2, b3, 0.85, 0.7), "k")
    S.plus(kap((-3.6, 6, 0.4), (-6, 9, 1.8), 1.0, 0.85), "k")
    S.plus(kap((-6, 9, 1.8), (-6.4, 12, 1.4), 0.85, 0.7), "k")
    S.rendern((-9, -5, -5), (9, 16, 5), versatz=(0.5, 0, 0.5))
    py = round(8.8 * s)
    st = stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="dark_oak")
    a = _r(1.6 * s)
    P.gebaeude(w, st, -a, -_r(2 * s), a, _r(1.2 * s), y0=py, etagen=1, eh=_r(2.4 * s), dach="sattel", first_x=False,
               sockel_h=0, gauben=False, kamine=0, steil=True, tuer="south")
    P.turm(w, st, 0, -_r(2 * s) - 1, py, _r(5 * s), max(1, _r(0.8 * s)), form="eckig", dach="nadel", krone=False,
           fenster=4)
    for k in range(3):
        w.setze(-a + k * a, py, _r(1.2 * s) + 2, w.b("mossy_cobblestone_wall", east="none", west="none",
                                                     north="none", south="none", up=True, waterlogged=False), False)
    return w


def schattenzitadelle(seed, g=3):
    """Schattenzitadelle: ein schwindelerregend hoher, nach oben verjüngter Turm aus grauem Stein mit Strebepfeilern,
    Spitzbogenfenstern und gezackter Krone, umgeben von einem Ring aus Mauern und spitzen Wachtürmen."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 8)
    gelaende(w, R, art="asche", dichte=0.15)
    M = Mat(w, ["polished_andesite", "stone_bricks", "andesite", "cracked_stone_bricks", "polished_deepslate"])
    H = _r(40 * u + 14)
    r0 = 4.5 * u + 3
    for y in range(1, H + 1):
        t = y / H
        r = r0 * (1 - 0.65 * t) * (1.0 if t < 0.9 else 0.8)
        for x in range(-int(r) - 2, int(r) + 3):
            for z in range(-int(r) - 2, int(r) + 3):
                d = max(abs(x), abs(z)) * 0.7 + math.hypot(x, z) * 0.3
                if r - 1.1 < d <= r:
                    w.setze(x, y, z, M(x, y, z, t))
                if y % max(4, int(6 * u)) == 0 and r < d <= r + 0.9:
                    w.setze(x, y, z, M(x, y, z, 0.9))
        if int(t * 20) % 3 == 1:
            for (x, z) in ((round(r), 0), (-round(r), 0), (0, round(r)), (0, -round(r))):
                w.setze(x, y, z, w.b("black_stained_glass"))
    # Strebepfeiler
    for k in range(8):
        a = k / 8 * 6.283
        for y in range(1, int(H * 0.45)):
            t = y / H
            r = r0 * (1 - 0.65 * t) + (1 - y / (H * 0.45)) * 3 * u
            w.setze(round(math.cos(a) * r), y, round(math.sin(a) * r), M(0, y, 0, t))
    # Krone mit Zacken
    rk = r0 * 0.4
    for k in range(6):
        a = k / 6 * 6.283
        for y in range(H, H + _r(4 * u + 2) + (k % 2) * 2):
            w.setze(round(math.cos(a) * rk), y, round(math.sin(a) * rk), w.b("polished_blackstone"))
    # Ringmauer mit Türmen
    st = stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="dark_oak")
    rm = R * 0.78
    for k in range(int(rm * 6.3)):
        a = k / (rm * 6.3) * 6.283
        x, z = round(math.cos(a) * rm), round(math.sin(a) * rm)
        for y in range(1, _r(5 * u + 3)):
            w.setze(x, y, z, M(x, y, z, 0.3))
        if k % 2 == 0:
            w.setze(x, _r(5 * u + 3), z, M(x, 0, z, 0.8))
    for k in range(6):
        a = k / 6 * 6.283
        P.turm(w, st, round(math.cos(a) * rm), round(math.sin(a) * rm), 1, _r(9 * u + 4), _r(1.4 * u + 1),
               dach="nadel", krone=True, fenster=4)
    return w


def rosenanwesen(seed, g=2):
    """Rosenanwesen: ein Fachwerk-Herrenhaus mit leuchtend roten Dächern und Gauben, zwei Rundtürme mit roten
    Kegelhelmen, davor ein Glaskuppel-Pavillon mit Holzrippen, Rosenbeete, ein Kiesweg und ein Steg am Teich."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.45)
    a = _r(5 * u + 3)
    b = _r(3 * u + 2)
    fachwerkhaus(w, -a, -b - 3, a, b - 3, 1, unten="graustein", pool="fachwerk_ocker", etagen=2, eh=4,
                 dach="mcw_ziegel", sockel_etagen=1, first_x=True)
    st = stil(w, wand="ockerputz", sockel="graustein", gesims="stone_brick", dach="mcw_ziegel", holz="spruce")
    for (tx, tz, H) in ((a + 3, -b, 12), (a + 6, b + 2, 9)):
        P.turm(w, st, tx, tz, 1, _r(H * u + 4), _r(2 * u + 1.5), form="rund", dach="kegel", krone=False, fenster=4)
    # Glaskuppel-Pavillon
    cx, cz = 0, b + _r(3 * u + 2)
    rr = 3 * u + 2
    for k in range(int(rr * 8)):
        t = k / (rr * 8) * 6.283
        x, z = cx + round(math.cos(t) * rr), cz + round(math.sin(t) * rr)
        for y in range(1, 4):
            w.setze(x, y, z, w.b("stripped_oak_log", axis="y") if k % 4 == 0 else w.b("glass"))
        w.setze(x, 0, z, w.b("stone_bricks"))
    for x in range(-int(rr) - 1, int(rr) + 2):
        for z in range(-int(rr) - 1, int(rr) + 2):
            for y in range(0, int(rr) + 1):
                d = math.sqrt(x * x + y * y + z * z)
                if rr - 1 < d <= rr:
                    rippe = (round(math.degrees(math.atan2(z, x))) % 45) < 9
                    w.setze(cx + x, 4 + y, cz + z, w.b("stripped_oak_log", axis="y") if rippe else
                            w.b("white_stained_glass"))
    w.setze(cx, 5 + int(rr), cz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    rosen = ["rose_bush", "peony", "lilac"]
    for k in range(int(30 * u)):
        x, z = int(w.rng.integers(-R // 2, R // 2)), int(w.rng.integers(b + 2, R - 2))
        if w.frei(x, 1, z) and w.frei(x, 2, z) and math.hypot(x - cx, z - cz) > rr + 2:
            n = rosen[k % 3]
            w.setze(x, 1, z, w.b(n, half="lower"))
            w.setze(x, 2, z, w.b(n, half="upper"))
    teich(w, -a - 3, R * 0.55, 3 + u, seerosen=0.1)
    for k in range(_r(4 * u + 2)):
        for z in (-1, 0):
            w.setze(-a - 3 + k, 1, round(R * 0.55) + z, w.b("spruce_slab", type="top", waterlogged=False))
    efeu(w, 0.05)
    return w


def herbsthof(seed, g=2):
    """Herbsthof: ein Fachwerkhaus mit Turm auf einem Felssockel aus Schiefer, ein Bach stürzt in Stufen
    hinab in einen Teich mit Steg und Ruderboot, Ackerterrassen, ein Backofen und Bäume in Rot und Gold."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    L = Land(w, R)
    Hs = _r(5 * u + 3)
    L.heben(lambda x, z, h: Hs if z < 0 and abs(x) < R * 0.55 else (2 if z < R * 0.25 else 0))
    L.see(round(R * 0.3), round(R * 0.55), R * 0.25, 0, tiefe=2)
    L.bauen(gras="grass_block", fels=["deepslate_tiles", "cobbled_deepslate", "deepslate_bricks", "tuff"],
            unten=-3)
    L.bepflanzen(dichte=0.35)
    for x in range(-round(R * 0.55), round(R * 0.55)):
        for y in range(1, Hs + 1):
            w.setze(x, y, 0, w.b(["deepslate_bricks", "cobbled_deepslate", "tuff", "deepslate_tiles"][(x + y) % 4]))
    a = _r(4 * u + 3)
    fachwerkhaus(w, -a, -_r(7 * u + 3), a, -1, Hs + 1, pool="fachwerk_ocker", etagen=1, eh=4, dach="dunkelholz",
                 sockel_etagen=1, first_x=True)
    st = stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="dunkelholz", holz="spruce")
    P.turm(w, st, -a - 2, -3, Hs + 1, _r(12 * u + 5), _r(1.8 * u + 1.2), form="eckig", dach="pyramide", krone=False,
           fenster=4)
    bx = a + 3
    for z in range(-R, round(R * 0.5)):
        h = L.h.get((bx, z), 0)
        w.setze(bx, h, z, w.b("water", level=0))
    for z in range(1, 6):
        for k in range(Hs):
            w.setze(bx, Hs - k, z if k < 2 else 2, w.b("water", level=8 if k else 0), False)
    for k in range(_r(5 * u + 3)):
        for z in (0, 1):
            w.setze(round(R * 0.3) - 3 - k, 1, round(R * 0.55) + z, w.b("spruce_planks"))
    for x in range(-R // 2, -R // 2 + _r(8 * u + 3)):
        for z in range(round(R * 0.2), round(R * 0.2) + 6):
            if (x, z) in L.h:
                w.setze(x, 2, z, w.b("farmland", moisture=7) if z % 3 else w.b("water", level=0))
                if z % 3:
                    w.setze(x, 3, z, w.b("wheat", age=7) if x % 4 else w.b("pumpkin"))
    rng = w.rng
    from baeume2 import gelb_laub, orange_laub, rot_laub
    for k in range(int(5 * u)):
        x, z = int(rng.integers(-R, R)), int(rng.integers(-R, R))
        if (x, z) in L.h and (x, z) not in L.wasser and math.hypot(x, z) > R * 0.5:
            bl = [(rot_laub(w), 0.4), (orange_laub(w), 0.35), (gelb_laub(w), 0.25)]
            t = wald2.laubbaum(int(rng.integers(1, 10 ** 6)), "dark_oak", H=_r(6 * u + 4))
            for p, b in list(t.bloecke.items()):
                if t.P.name(b).endswith("_leaves"):
                    t.bloecke[p] = -1
            hh = L.h[(x, z)]
            for (px, py, pz), b in t.bloecke.items():
                if b == -1:
                    w.setze(x + px, hh + py, z + pz, bl[int(rng.random() * 3)][0], False)
                else:
                    w.setze(x + px, hh + py, z + pz, w.b(t.P.name(b).replace("minecraft:", ""),
                                                         **dict(t.P.eintraege[b][1])), False)
    return w


def himmelsschmiede(seed, g=2):
    """Himmelsschmiede: eine große Werkstatt aus Fachwerk mit türkisen Prismarindächern, ein hoher Steinschlot,
    ein Wasserrad an der Flanke, ein Ladekran mit hängender Plattform und eine Freitreppe über einen bemoosten Hang."""
    w = _neu(seed)
    u = U[g]
    R = _r(15 * u + 6)
    L = Land(w, R)
    L.heben(lambda x, z, h: round(max(0, (x + R * 0.1) / R * 6 * u)))
    L.bauen(unten=-3)
    L.bepflanzen(dichte=0.5)
    a = _r(5 * u + 3)
    b = _r(3.5 * u + 2)
    y0 = 1
    fachwerkhaus(w, -a - 2, -b, a - 2, b, y0, unten="graustein", pool="holz_hell", etagen=2, eh=4, dach="blau",
                 sockel_etagen=1, first_x=True)
    st = stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="spruce")
    P.turm(w, st, a, -b + 1, 1, _r(18 * u + 7), _r(1.3 * u + 1), form="eckig", dach="platt", krone=True, fenster=4)
    rr = 3 * u + 2
    wx = -a - 4
    for k in range(int(rr * 10)):
        t = k / (rr * 10) * 6.283
        for d in (rr, rr - 0.6):
            w.setze(wx, round(rr + 1 + math.sin(t) * d), round(math.cos(t) * d), w.b("spruce_planks"))
    for k in range(8):
        t = k / 8 * 6.283
        linie(w, (wx, rr + 1, 0), (wx, rr + 1 + math.sin(t) * rr, math.cos(t) * rr),
              w.b("stripped_spruce_log", axis="x"))
    for z in range(-R, R + 1):
        if (wx - 1, z) in L.h:
            w.setze(wx - 1, 0, z, w.b("water", level=0))
            w.setze(wx, 0, z, w.b("water", level=0))
    kranarm(w, -a - 1, 13, b + 2, 0, 1, _r(3 * u + 3),
            last=lambda x, y, z: [w.setze(x + dx, y, z + dz, w.b("spruce_slab", type="bottom", waterlogged=False))
                                  for dx in (-1, 0, 1) for dz in (-1, 0, 1)])
    for k in range(_r(6 * u + 3)):
        for x in range(1, 4):
            w.setze(x, L.h.get((x, b + 3 + k), 0) + 1, b + 3 + k, w.b("mud_brick_stairs", facing="south",
                                                                       half="bottom", shape="straight",
                                                                       waterlogged=False), False)
    efeu(w, 0.06)
    return w


def karmesinlodge(seed, g=2):
    """Karmesin-Lodge: ein Haus mit leuchtend roten Wandfeldern zwischen Eichenbalken, dunklen Schieferdächern und
    Holzbalkonen, ein hoher Turm mit Pyramidendach und Laternenausleger, ein Steinkamin und ein steinerner Sockel."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.35)
    rot = Mat(w, ["red_terracotta", "red_concrete", "red_terracotta", "red_wool"])
    a = _r(4.5 * u + 3)
    b = _r(3 * u + 2)
    st_u = stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="oak")
    P.gebaeude(w, st_u, -a, -b, a, b, y0=1, etagen=1, eh=4, dach="flach", sockel_h=1, gauben=False, kamine=0)
    st = P.Stil(w, wand=rot, sockel="graustein", gesims="oak", dach="schiefer", holz="oak", fachwerk=True,
                balken="stripped_oak_log")
    P.gebaeude(w, st, -a - 1, -b - 1, a + 1, b + 1, y0=6, etagen=2, eh=4, dach="sattel", first_x=True, sockel_h=0,
               gauben=True, kamine=1, steil=True)
    tx = -a - 2
    tr = _r(1.8 * u + 1.5)
    st_t = P.Stil(w, wand=rot, sockel="graustein", gesims="oak", dach="schiefer", holz="oak", fachwerk=True,
                  balken="stripped_oak_log")
    H = _r(16 * u + 7)
    P.turm(w, st_t, tx, 0, 1, H, tr, form="eckig", dach="pyramide", krone=False, fenster=4)
    kranarm(w, tx - tr, H - 4, 0, -1, 0, _r(2 * u + 2),
            last=lambda x, y, z: [w.setze(x, y - k, z, w.b("glowstone") if k else w.b("yellow_stained_glass"))
                                  for k in range(2)])
    for x in range(-a, a + 1):
        w.setze(x, 6, b + 2, w.b("oak_slab", type="top", waterlogged=False))
        w.setze(x, 7, b + 2, w.b("oak_fence", north=False, south=False, east=True, west=True, waterlogged=False))
    for y in range(1, 19):
        w.setze(a + 2, y, 0, w.b("stone_bricks" if y % 4 else "polished_andesite"))
    return w


def mandarinvilla(seed, g=2):
    """Mandarinvilla: ein steiles A-Haus mit orangefarbenen Ziegeldächern, die in mehreren Stufen weit
    überstehen, Rundfenster im Giebel, ein Steinsockel mit Freitreppe und ein seitlicher Anbau mit Pultdach."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.35)
    a = _r(3.5 * u + 2)
    b = _r(4 * u + 3)
    fachwerkhaus(w, -a, -b, a, b, 1, unten="graustein", pool="holz_hell", etagen=2, eh=4, dach="mcw_gelb",
                 sockel_etagen=1, first_x=False, ueberhang=1)
    fachwerkhaus(w, a + 2, -b + 2, a + 2 + _r(3 * u + 2), b - 1, 1, unten="graustein", pool="holz_hell", etagen=1,
                 eh=4, dach="ziegel", sockel_etagen=0, first_x=False, gauben=False)
    for k in range(4):
        for x in range(-1, 2):
            w.setze(x, 1 + k, b + 4 - k, w.b("stone_brick_stairs", facing="north", half="bottom", shape="straight",
                                             waterlogged=False))
    return w


def schwertschmiede(seed, g=2):
    """Schwertschmiede: eine Fachwerk-Schmiede mit Schieferdach und offener Werkstatt, an der Felsflanke dahinter
    ragt ein riesiges steinernes Schwert mit kupfernem Parierstück senkrecht in den Himmel, davor Amboss, Esse und
    ein Ladenschild am Ausleger."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.4)
    from drachen import felsen
    sx, sz = -round(R * 0.55), round(R * 0.1)
    felsen(w, R * 0.3, 7 * u + 3, cx=sx, cz=sz, spitz=0.7, rauh=0.3)
    a = _r(4 * u + 3)
    b = _r(3 * u + 2)
    fachwerkhaus(w, -a + 2, -b, a + 2, b, 1, unten="graustein", pool="fachwerk_rot", etagen=1, eh=4, dach="schiefer",
                 sockel_etagen=1, first_x=True)
    H = _r(26 * u + 10)
    bw = max(1, _r(1.4 * u + 0.6))
    for y in range(1, H):
        breite = bw if y < H * 0.65 else max(1, round(bw * (1 - (y - H * 0.65) / (H * 0.4))))
        for x in range(-breite, breite + 1):
            for z in (-1, 0, 1):
                kern = abs(x) < max(1, breite - 1) and z == 0
                w.setze(sx + x, H - y, sz + z, w.b("polished_deepslate" if kern else
                                                   ("calcite" if abs(x) == breite else "polished_andesite")))
    gy = H
    gb = _r(5 * u + 3)
    for x in range(-gb, gb + 1):
        for z in (-1, 0, 1):
            for y in (gy, gy + 1):
                w.setze(sx + x, y, sz + z, w.b("cut_copper" if abs(x) < gb - 1 else "waxed_exposed_cut_copper"))
        if abs(x) == gb:
            w.setze(sx + x, gy + 2, sz, w.b("waxed_exposed_cut_copper"))
    gl = _r(4 * u + 3)
    for y in range(gy + 2, gy + 2 + gl):
        for z in (0,):
            w.setze(sx, y, sz, w.b("dark_oak_log", axis="y"))
            if y % 2:
                w.setze(sx, y, sz, w.b("stripped_mangrove_log", axis="y"))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(sx + dx, gy + 2 + gl, sz + dz, w.b("copper_block") if dx or dz else w.b("emerald_block"))
    w.setze(a, 1, b + 3, w.b("anvil", facing="north"))
    w.setze(a - 2, 1, b + 3, w.b("blast_furnace", facing="south", lit=True))
    w.setze(a - 3, 1, b + 3, w.b("smithing_table"))
    kranarm(w, a + 3, 6, b + 1, 1, 0, 2,
            last=lambda x, y, z: [w.setze(x, y, z + dz, w.b("spruce_planks")) for dz in (-1, 0, 1)])
    for k in range(3):
        w.setze(-a - 3 + k, 1, b + 4, w.b("copper_block") if k % 2 else w.b("raw_iron_block"))
    return w


def efeuturm(seed, g=2):
    """Efeuturm: ein schlanker, sich nach oben verjüngender Steinturm, über und über mit Efeu bewachsen, ganz oben
    ein auskragendes Holzhaus mit Erkern, Balkon und spitzen Türmchen."""
    w = _neu(seed)
    u = U[g]
    R = _r(9 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.5)
    hell = _stil(seed) != 0
    M = Mat(w, ["smooth_sandstone", "end_stone", "calcite", "diorite", "sandstone"] if hell else
            ["stone_bricks", "andesite", "cobblestone", "polished_andesite", "stone"])
    H = _r(24 * u + 10)
    r0 = 3.5 * u + 2
    for y in range(1, H + 1):
        r = r0 * (1 - 0.35 * y / H)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(x, z)
                if r - 1 < d <= r + 0.4:
                    w.setze(x, y, z, M(x, y, z, y / H))
    a = round(r0 * 0.65 + 2)
    dach = "mcw_lila" if hell else "schiefer"
    st = stil(w, "fachwerk_ocker", dach=dach)
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            if max(abs(x), abs(z)) <= a + 1:
                w.setze(x, H, z, w.b("spruce_planks"))
    for k in range(3):
        for x in range(-a + k, a - k + 1):
            for z in range(-a + k, a - k + 1):
                if max(abs(x), abs(z)) == a - k:
                    w.setze(x, H - 1 - k, z, w.b("spruce_slab", type="top", waterlogged=False))
    top = P.gebaeude(w, st, -a + 1, -a + 1, a - 1, a - 1, y0=H + 1, etagen=1, eh=5, dach="walm", sockel_h=0,
                     gauben=True, kamine=1, steil=True)
    for (x, z) in ((-a, -a), (a, a)):
        P.turm(w, stil(w, wand="graustein", dach=dach), x, z, H + 1, _r(6 * u + 3), 1, form="eckig", dach="nadel",
               krone=False, fenster=99, schiessscharten=False)
    efeu(w, 0.3, laub=0.8)
    return w


def stelzenfischer(seed, g=2):
    """Fischerhütte auf Stelzen: eine Holzhütte mit tief gezogenem türkisem Dach steht auf Pfählen im Wasser,
    umlaufende Stege mit Leitern, ein Kranbalken mit einem riesigen Fisch als Ladenschild, Netze, Kisten und ein
    Ruderboot."""
    w = _neu(seed)
    u = U[g]
    R = _r(13 * u + 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                for y in (-2, -1, 0):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -3, z, w.b("sand" if (x + z) % 3 else "gravel"))
    a = _r(3.5 * u + 2)
    b = _r(3 * u + 2)
    plattform(w, -a - 3, -b - 3, a + 3, b + 3, 2, holz="oak", stuetzen=3, boden_y=-2)
    st = stil(w, "holz_hell", dach="blau")
    P.gebaeude(w, st, -a, -b, a, b, y0=3, etagen=1, eh=5, dach="sattel", first_x=False, sockel_h=0, gauben=True,
               kamine=1, steil=True)
    ex, ez = kranarm(w, -a - 2, 11, 0, -1, 0, _r(3 * u + 2))
    from skulptur import Skulptur, ell, kap
    from weltwunder import bl
    S = Skulptur(w, 0.5 * u + 0.5)
    S.mat("k", bl(w, "prismarine_bricks"))
    S.mat("d", bl(w, "dark_prismarine"))
    S.plus(ell(0, 0, 0, 1.2, 2.2, 0.8), "k")
    S.plus(kap((0, -2, 0), (0, -3.2, 0), 0.4, 0.9), "d")
    S.plus(ell(0.9, -2.8, 0, 0.6, 0.3, 0.3), "d")
    S.plus(ell(-0.9, -2.8, 0, 0.6, 0.3, 0.3), "d")
    S.rendern((-3, -4, -2), (3, 3, 2), versatz=(ex + 0.5, 11 - 6 - 2 * u, ez + 0.5))
    for k in range(3):
        w.setze(a + 2, 3, -b + k, w.b("barrel", facing="up", open=False))
    for y in range(-1, 3):
        w.setze(0, y, b + 4, w.b("ladder", facing="south", waterlogged=y < 1))
    for x in range(-a, a + 1, 2):
        w.setze(x, 4, b + 2, w.b("white_wool") if x % 4 == 0 else w.b("cobweb"))
    from boote import ruderboot
    einfuegen(w, ruderboot(seed, 0), a + 5, 0, b + 5)
    return w


def freibeuter_brigg(seed, g=2):
    """Freibeuter-Brigg: ein großer Zweimaster mit vielen geblähten Segeln, Klüver und Stagsegeln, Wanten aus
    Seilen, Kanonenpforten, Heckgalerie mit Laternen und schwarzer Flagge."""
    w = _neu(seed)
    u = U[g]
    L = _r(18 * u + 8)
    B = _r(3.5 * u + 2)
    T = _r(3 * u + 2)
    for x in range(-L, L + 1):
        t = x / L
        bb = B * (1 - t ** 2 * 0.9) if t > 0 else B * (1 - t ** 4 * 0.5)
        for y in range(-T, 3):
            br = bb * (1 - ((-y) / (T + 1)) ** 2 * 0.7) if y < 0 else bb
            for z in range(-int(br) - 1, int(br) + 2):
                if abs(z) > br + 0.3:
                    continue
                rand = abs(z) > br - 1 or y == -T
                if rand:
                    blk = "dark_oak_planks" if y < 0 else ("spruce_planks" if y < 2 else "dark_oak_planks")
                    if y == 1 and x % 4 == 0 and abs(x) < L * 0.7:
                        blk = "black_concrete"
                    w.setze(x, y, z, w.b(blk))
                elif y == 1:
                    w.setze(x, y, z, w.b("spruce_planks"))
    for x in range(-L, -L + _r(5 * u + 3)):
        for z in range(-B, B + 1):
            if abs(z) <= B * 0.9:
                for y in range(2, 5):
                    if abs(z) >= B * 0.9 - 1 or x == -L:
                        w.setze(x, y, z, w.b("dark_oak_planks") if (x + y) % 3 else w.b("glass_pane", north=True,
                                                                                         south=True, east=False,
                                                                                         west=False,
                                                                                         waterlogged=False))
                w.setze(x, 5, z, w.b("dark_oak_planks"))
    masten = [(-round(L * 0.25), _r(22 * u + 8)), (round(L * 0.3), _r(26 * u + 9))]
    for (mx, mh) in masten:
        for y in range(1, mh):
            w.setze(mx, y, 0, w.b("stripped_dark_oak_log", axis="y"))
        abst = max(4, (mh - 8) // 3)
        for i, y in enumerate(range(6, mh - 3, abst)):
            sb = round(B * 2.2 * (1 - i * 0.15))
            hs = abst - 1
            for z in range(-sb, sb + 1):
                w.setze(mx, y + hs + 1, z, w.b("spruce_log", axis="z"))
                for yy in range(y, y + hs + 1):
                    bauch = round(1.5 * u * math.sin((yy - y + 0.5) / (hs + 1) * math.pi) * (1 - (z / (sb + 1)) ** 2))
                    w.setze(mx + bauch, yy, z, w.b("white_wool" if (z + yy) % 7 else "light_gray_wool"))
        for z in (-B, B):
            linie(w, (mx, mh - 3, 0), (mx, 2, z), w.b("chain", axis="y", waterlogged=False))
        w.setze(mx, mh, 0, w.b("black_wool"))
        w.setze(mx + 1, mh, 0, w.b("black_wool"))
        w.setze(mx + 2, mh - 1, 0, w.b("black_wool"))
    bug = L + _r(8 * u + 4)
    linie(w, (L, 3, 0), (bug, 7 + int(3 * u), 0), w.b("stripped_spruce_log", axis="x"))
    for k in range(int(6 * u) + 2):
        t = k / (int(6 * u) + 2)
        x0 = round(L + (bug - L) * t)
        y0 = round(3 + (4 + 3 * u) * t)
        linie(w, (x0, y0, 0), (masten[1][0] + 2, masten[1][1] - 4 - k, 0), w.b("white_wool"))
    for x in range(-L + 1, -L + 4):
        w.setze(x, 6, B - 1, laterne(w))
    return w


def totenkopfatoll(seed, g=3):
    """Totenkopf-Atoll: ein ringförmiges Gebirge aus Fels und Palmenwald umschließt eine Lagune; in der Bergflanke
    klafft ein riesiger Totenkopf mit Wasserfall aus dem Mund, in der Lagune liegt eine kleine Festungsinsel mit
    Hafen, draußen ankert ein Segelschiff."""
    w = _neu(seed)
    u = U[g]
    R = _r(26 * u + 10)
    L = Land(w, R)
    rn = Rauschen(w, 6)
    Hm = 14 * u + 6

    def hoehe(x, z, h):
        d = math.hypot(x, z) / R
        ring = math.exp(-((d - 0.62) / 0.16) ** 2)
        lag = -3 if d < 0.45 else 0
        auss = -3 if d > 0.85 else 0
        return round(ring * Hm * (0.6 + 0.6 * rn(x, 0, z)) + lag + auss + (2 if 0.45 <= d <= 0.85 else 0))
    L.heben(hoehe)
    for (x, z), h in L.h.items():
        if h < 0:
            L.wasser[(x, z)] = 0
    L.bauen(gras="grass_block", fels=["stone", "granite", "andesite", "coarse_dirt", "dirt"], unten=-4)
    L.bepflanzen(dichte=0.3, baeume=int(18 * u), arten=("palme", "palme", "busch"))
    for (x, z), h in L.h.items():
        if 0 <= h <= 1 and (x, z) not in L.wasser:
            w.setze(x, h, z, w.b("sand"))
    # Totenkopf in der Nordflanke
    from skulptur import Skulptur, ell
    from weltwunder import bl
    sz = -round(R * 0.62)
    hy = L.h.get((0, sz), 5)
    S = Skulptur(w, 1.2 * u + 0.8)
    S.mat("k", bl(w, "bone_block"))
    S.mat("d", bl(w, "black_concrete"))
    S.plus(ell(0, 3, 0, 4, 4, 3.4), "k")
    S.plus(ell(0, 0, 0.6, 2.8, 2.2, 2.6), "k")
    S.plus(ell(-1.5, 3.4, 3, 1.1, 1.2, 1.0), "d")
    S.plus(ell(1.5, 3.4, 3, 1.1, 1.2, 1.0), "d")
    S.plus(ell(0, 1.8, 3.3, 0.5, 0.7, 0.6), "d")
    S.plus(ell(0, -0.6, 2.9, 1.8, 0.6, 0.8), "d")
    S.rendern((-6, -4, -5), (6, 8, 5), versatz=(0.5, hy - 2, sz + 2.5))
    for y in range(1, hy - 2):
        w.setze(0, y, sz + 4 + int(u), w.b("water", level=8 if y < hy - 3 else 0), False)
    # Festungsinsel in der Lagune
    st = stil(w, wand="sandstein", sockel="graustein", gesims="stone_brick", dach="ziegel", holz="spruce")
    fi = _r(4 * u + 3)
    for x in range(-fi - 1, fi + 2):
        for z in range(-fi - 1, fi + 2):
            for y in range(-3, 1):
                w.setze(x, y, z, w.b("sandstone" if y == 0 else "stone"))
    P.gebaeude(w, st, -fi + 1, -fi + 1, fi - 1, fi - 1, y0=1, etagen=1, eh=4, dach="flach", sockel_h=1, gauben=False,
               kamine=0)
    for (x, z) in ((-fi, -fi), (fi, -fi), (-fi, fi), (fi, fi)):
        P.turm(w, st, x, z, 1, _r(5 * u + 4), 1, form="rund", dach="platt", krone=True, fenster=99,
               schiessscharten=False)
    for k in range(_r(6 * u + 3)):
        w.setze(fi + 1 + k, 1, 0, w.b("spruce_planks"))
    from boote import kogge
    from piraten import einfuegen_gedreht
    from skulptur import dreh_y
    s = kogge(seed, max(0, g - 2))
    einfuegen_gedreht(w, s, dreh_y(0.4), (round(R * 0.6), 0, round(R * 0.85)))
    return w


INSTAGRAM = {
    "alchemistenturm": ("Alchemistenturm", alchemistenturm),
    "tuerkis_gehoeft": ("Türkis-Gehöft mit Wimpelturm", tuerkis_gehoeft),
    "stelzen_aussenposten": ("Stelzen-Außenposten", stelzen_aussenposten),
    "kirschbluetental": ("Kirschblütental mit Bogenbrücke", kirschbluetental),
    "hexenladen": ("Hexenladen mit Kürbisdach", hexenladen),
    "riesenhand": ("Riesenhand mit Kapelle", riesenhand),
    "schattenzitadelle": ("Schattenzitadelle", schattenzitadelle),
    "rosenanwesen": ("Rosenanwesen mit Glaskuppel", rosenanwesen),
    "herbsthof": ("Herbsthof am Wasserfall", herbsthof),
    "himmelsschmiede": ("Himmelsschmiede", himmelsschmiede),
    "karmesinlodge": ("Karmesin-Lodge", karmesinlodge),
    "mandarinvilla": ("Mandarinvilla", mandarinvilla),
    "schwertschmiede": ("Schwertschmiede", schwertschmiede),
    "efeuturm": ("Efeuturm", efeuturm),
    "stelzenfischer": ("Fischerhütte auf Stelzen", stelzenfischer),
    "freibeuter_brigg": ("Freibeuter-Brigg", freibeuter_brigg),
    "totenkopfatoll": ("Totenkopf-Atoll", totenkopfatoll),
}

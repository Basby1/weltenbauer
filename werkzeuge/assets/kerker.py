"""Kerker & Gefängnis – Verliese, Zellenblöcke, Kerkertürme, Wachstuben, Oubliette, Gefängnisinsel, Pranger,
Hängekäfig, Magierkerker, Wassergefängnis, Kettenhalle, Schatzverlies und kachelbare Kerkergänge.
Unterirdische Anlagen sind ohne Decke gebaut (Schnittansicht), damit man hineinsehen kann. Boden y = 0."""

from __future__ import annotations

import math

import pracht as P
from flora import _neu, _r, _stil
from lib import Rauschen
from pracht import Mat, gelaende

U = [0.6, 1.0, 1.7, 2.8]


def stein(w, seed=0):
    if _stil(seed) == 0:
        return Mat(w, ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "cobblestone",
                       "mossy_cobblestone", "andesite"])
    return Mat(w, ["deepslate_bricks", "cracked_deepslate_bricks", "deepslate_tiles", "cobbled_deepslate",
                   "polished_deepslate"])


def gitter(w, achse="x"):
    if achse == "x":
        return w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False)
    return w.b("iron_bars", north=True, south=True, east=False, west=False, waterlogged=False)


def boden(w, x0, z0, x1, z1, M, y=0):
    rn = Rauschen(w, 1.4)
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, y, z, w.b("gravel") if rn(x, y, z) > 0.85 else M(x, y, z, 0.3))


def zelle(w, x0, z0, b, t, h, M, front="south", inhalt=True, wasser=False):
    """Zelle mit Gitterfront. x0,z0 = Ecke, b/t Innenmaß."""
    rng = w.rng
    x1, z1 = x0 + b + 1, z0 + t + 1
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            rand = x in (x0, x1) or z in (z0, z1)
            for y in range(1, h + 1):
                if rand:
                    istfront = (front == "south" and z == z1) or (front == "north" and z == z0) or \
                               (front == "east" and x == x1) or (front == "west" and x == x0)
                    ecke = x in (x0, x1) and z in (z0, z1)
                    if istfront and not ecke and y < h:
                        w.setze(x, y, z, gitter(w, "x" if front in ("south", "north") else "z"))
                    else:
                        w.setze(x, y, z, M(x, y, z, y / h))
            if not rand and wasser:
                w.setze(x, 1, z, w.b("water", level=0))
    if not inhalt:
        return
    w.setze(x0 + 1, 1, z0 + 1, w.b("hay_block", axis="x"))
    if b > 1:
        w.setze(x0 + 2, 1, z0 + 1, w.b("hay_block", axis="x"))
    w.setze(x1 - 1, 1, z0 + 1, w.b("cauldron") if rng.random() < 0.5 else w.b("composter", level=1))
    for y in range(2, h):
        w.setze(x0 + 1 + (b > 2), y, z0, w.b("chain", axis="y", waterlogged=False), True) if y == h - 1 and False \
            else None
    w.setze(x1 - 1, h - 1, z0 + 1, w.b("chain", axis="y", waterlogged=False))
    if rng.random() < 0.3:
        w.setze(x0 + 1, 1, z1 - 1, w.b("cobweb"))


def gang(w, x0, x1, z, B, h, M, fackeln=True):
    """Kerkergang entlang x, mit Wänden und Wandfackeln (Laternen)."""
    for x in range(x0, x1 + 1):
        for d in range(-B - 1, B + 2):
            w.setze(x, 0, z + d, M(x, 0, z + d, 0.2))
            if abs(d) == B + 1:
                for y in range(1, h + 1):
                    w.setze(x, y, z + d, M(x, y, z + d, y / h))
        if fackeln and x % 5 == 0:
            for d in (-B, B):
                w.setze(x, h - 1, z + d, w.b("soul_lantern" if (x // 5) % 3 == 0 else "lantern", hanging=False,
                                             waterlogged=False))


# ============================================================================ Bauten

def burgverlies(seed, g=2):
    """Burgverlies: ein gewölbter Keller mit einem langen Gang, beidseitig Zellen mit Gittern, Strohlager und
    Ketten, am Ende die Wachstube mit Schlüsselbrett."""
    w = _neu(seed)
    u = U[g]
    M = stein(w, seed)
    n = 2 + g
    b = _r(2 * u + 1, 2)
    h = _r(2 * u + 2, 4)
    L = n * (b + 2)
    boden(w, -2, -b - 5, L + 6, b + 5, M)
    gang(w, -2, L + 6, 0, 1, h, M)
    for i in range(n):
        x0 = i * (b + 2)
        zelle(w, x0, 2, b, b, h, M, front="north")
        zelle(w, x0, -b - 3, b, b, h, M, front="south")
    for x in range(L + 2, L + 7):
        for z in range(-3, 4):
            if x in (L + 2, L + 6) or abs(z) == 3:
                for y in range(1, h + 1):
                    w.setze(x, y, z, M(x, y, z, 0.5))
    w.bloecke.pop((L + 2, 1, 0), None)
    w.bloecke.pop((L + 2, 2, 0), None)
    w.setze(L + 4, 1, 0, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(L + 4, 2, 0, w.b("spruce_pressure_plate", powered=False))
    w.setze(L + 5, 1, -2, w.b("barrel", facing="up", open=False))
    w.setze(L + 5, 2, 2, w.b("tripwire_hook", attached=False, facing="west", powered=False))
    return w


def zellenblock(seed, g=1):
    """Zellenblock: eine Reihe gleichförmiger Zellen hinter einem Gittergang – kachelbar zu langen Trakten."""
    w = _neu(seed)
    u = U[g]
    M = stein(w, seed)
    n = 2 + g
    b = _r(2 * u + 1, 2)
    h = _r(2 * u + 2, 4)
    L = n * (b + 2)
    boden(w, -1, -3, L + 1, b + 3, M)
    for i in range(n):
        zelle(w, i * (b + 2), 0, b, b, h, M, front="north")
    for x in range(-1, L + 2):
        w.setze(x, h + 1, -2, M(x, h + 1, -2, 0.9))
        for y in range(1, h + 1):
            w.setze(x, y, -3, M(x, y, -3, y / h))
    return w


def kerkerturm(seed, g=2):
    """Kerkerturm: ein runder Bergfried mit winzigen Schießscharten, außen eine Wendeltreppe, oben Wachplattform
    mit Zinnen – im aufgeschnittenen Inneren übereinander liegende Zellen."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.15)
    M = stein(w, seed)
    r = _r(4 * u + 2)
    H = _r(16 * u + 6)
    for y in range(1, H + 1):
        for k in range(int(r * 8)):
            a = k / (r * 8) * 6.28
            x, z = round(math.cos(a) * r), round(math.sin(a) * r)
            if x > 0 and z > 0 and y > 1 and y < H - 1:
                continue
            w.setze(x, y, z, M(x, y, z, y / H))
        if y % 5 == 0:
            for x in range(-r, r + 1):
                for z in range(-r, r + 1):
                    if x * x + z * z < r * r:
                        w.setze(x, y, z, w.b("spruce_planks"), False)
            for d in range(-r + 1, 1):
                w.setze(d, y + 1, 0, gitter(w, "z"))
            w.setze(-r + 1, y + 1, -1, w.b("hay_block", axis="x"))
            w.setze(-1, y + 3, -r + 1, w.b("chain", axis="y", waterlogged=False))
    for k in range(int(r * 8)):
        a = k / (r * 8) * 6.28
        if k % 2:
            w.setze(round(math.cos(a) * r), H + 1, round(math.sin(a) * r), M(0, H, 0, 0.9))
    for k in range(H):
        a = k * 0.35
        w.setze(round(math.cos(a) * (r + 1)), k + 1, round(math.sin(a) * (r + 1)),
                w.b("stone_brick_slab", type="top", waterlogged=False), False)
    return w


def wachstube(seed, g=1):
    """Wachstube: ein gemauerter Raum am Kerkereingang mit Tisch, Würfelspiel, Waffenständer, Schlüsselbund,
    Kohlebecken und einem Ausblick durch ein Gitterfenster."""
    w = _neu(seed)
    u = U[g]
    M = stein(w, seed)
    a, b = _r(4 * u + 2), _r(3 * u + 2)
    h = 4
    boden(w, -a - 1, -b - 1, a + 1, b + 1, M)
    for x in range(-a - 1, a + 2):
        for z in range(-b - 1, b + 2):
            if abs(x) == a + 1 or abs(z) == b + 1:
                for y in range(1, h + 1):
                    w.setze(x, y, z, gitter(w, "x") if z == b + 1 and abs(x) < 2 and y in (2, 3) else
                            M(x, y, z, y / h))
    for x in (-1, 0, 1):
        w.setze(x, 1, 0, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
        w.setze(x, 2, 0, w.b("spruce_pressure_plate", powered=False))
    for x in (-2, 2):
        w.setze(x, 1, 0, w.b("spruce_stairs", facing="east" if x < 0 else "west", half="bottom", shape="straight",
                             waterlogged=False))
    w.setze(a, 1, -b, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    w.setze(-a, 1, -b, w.b("barrel", facing="up", open=False))
    w.setze(-a, 2, -b, w.b("barrel", facing="up", open=False))
    w.setze(0, 3, -b, w.b("tripwire_hook", attached=False, facing="south", powered=False))
    return w


def verlieseingang(seed, g=1):
    """Eingang zum Verlies: auf einem Burghof eine schwere Falltür mit Eisenbeschlägen über einer steilen
    Treppe in die Tiefe, bewacht von einem kleinen Wachhäuschen."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    M = stein(w, seed)
    boden(w, -R, -R, R, R, M)
    T = _r(5 * u + 3)
    for k in range(T):
        for x in (-1, 0, 1):
            w.setze(x, -k, k - 2, w.b("stone_brick_stairs", facing="south", half="bottom", shape="straight",
                                      waterlogged=False))
            for y in range(-k + 1, 1):
                w.bloecke.pop((x, y, k - 2), None)
        for x in (-2, 2):
            w.setze(x, -k, k - 2, M(x, -k, k, 0.5))
    for x in (-1, 0, 1):
        w.setze(x, 1, -2, w.b("iron_trapdoor", facing="south", half="bottom", open=True, powered=False,
                              waterlogged=False))
    for x in (-2, 2):
        for z in (-3, -2):
            w.setze(x, 1, z, M(x, 1, z, 0.5))
        w.setze(x, 2, -2, w.b("lantern", hanging=False, waterlogged=False))
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="mcw_schiefer", holz="spruce")
    P.gebaeude(w, st, R - 4, -R + 1, R - 1, -R + 4, y0=1, etagen=1, eh=3, dach="sattel", tuer="west",
               gauben=False, kamine=0)
    return w


def oubliette(seed, g=1):
    """Oubliette: ein flaschenförmiges Verlies, nur durch ein Loch mit Gitter im Boden erreichbar – im Schnitt
    sieht man den engen Hals und die dunkle Kammer darunter."""
    w = _neu(seed)
    u = U[g]
    M = stein(w, seed)
    R = _r(6 * u + 3)
    T = _r(8 * u + 4)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            w.setze(x, T, z, M(x, T, z, 0.8))
    for y in range(0, T):
        t = y / T
        r = (3 * u + 1.5) if t < 0.6 else 1.2
        for x in range(-R, R + 1):
            for z in range(-R, R + 1):
                d = math.hypot(x, z)
                if d > r and d <= R and not (x > 0 and z > 0):
                    w.setze(x, y, z, M(x, y, z, t))
    for x in (-1, 0, 1):
        for z in (-1, 0, 1):
            w.bloecke.pop((x, T, z), None)
            w.setze(x, T, z, w.b("iron_trapdoor", facing="north", half="top", open=False, powered=False,
                                 waterlogged=False))
    for x in range(-2, 3):
        for z in range(-2, 3):
            if x * x + z * z < 5:
                w.setze(x, 0, z, w.b("gravel"))
    w.setze(-1, 1, -1, w.b("bone_block", axis="x"))
    return w


def gefaengnisinsel(seed, g=2):
    """Gefängnisinsel: auf einem kahlen Felsen im Meer eine ummauerte Strafanstalt mit Zellentrakt, Wachtürmen,
    Leuchtfeuer und Anlegesteg – ein Entkommen scheint unmöglich."""
    from drachen import felsen
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    for x in range(-R - 4, R + 5):
        for z in range(-R - 4, R + 5):
            if math.hypot(x, z) <= R + 4:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("water", level=0))
                w.setze(x, -2, z, w.b("gravel"))
    hoehe = felsen(w, R, 4 * u + 2, mat=Mat(w, ["stone", "andesite", "cobblestone", "tuff"], kontrast=1.2),
                   spitz=1.8, rauh=0.2)
    top = int(4 * u + 2) + 1
    M = stein(w, seed)
    a = _r(R * 0.6)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            w.setze(x, top, z, M(x, top, z, 0.3))
            if max(abs(x), abs(z)) == a:
                for y in range(top + 1, top + 5):
                    w.setze(x, y, z, M(x, y, z, 0.6))
    st = P.Stil(w, wand="graustein" if _stil(seed) == 0 else "tiefenschiefer", sockel="graustein",
                gesims="stone_brick", dach="mcw_schiefer", holz="spruce")
    P.gebaeude(w, st, -a + 2, -a + 2, a - 2, -a + 2 + _r(4 * u + 2), y0=top + 1, etagen=2, eh=4, dach="sattel",
               tuer="south", gauben=False, kamine=0)
    for sx in (-a, a):
        for sz in (-a, a):
            P.turm(w, st, sx, sz, top + 1, _r(6 * u + 3), 2, dach="pyramide", form="eckig", krone=True)
    for z in range(a, R + 4):
        for x in (-1, 0, 1):
            w.setze(x, max(1, top - (z - a)), z, w.b("spruce_planks"))
    return w


def pranger(seed, g=0):
    """Pranger: ein hölzerner Schandpfahl mit Hals- und Handbrett auf einem gepflasterten Podest am Marktplatz,
    daneben ein Ausrufer-Pult."""
    w = _neu(seed)
    M = stein(w, seed)
    boden(w, -4, -4, 4, 4, M)
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, 1, z, w.b("stone_brick_slab", type="top", waterlogged=False) if max(abs(x), abs(z)) < 2 else
                    w.b("stone_bricks"))
    for y in range(2, 5):
        w.setze(-1, y, 0, w.b("dark_oak_log", axis="y"))
        w.setze(1, y, 0, w.b("dark_oak_log", axis="y"))
    for x in (-1, 0, 1):
        w.setze(x, 4, 0, w.b("dark_oak_slab", type="bottom", waterlogged=False) if x == 0 else w.b("dark_oak_log",
                                                                                                    axis="y"))
        w.setze(x, 5, 0, w.b("dark_oak_planks"))
    w.setze(3, 1, 3, w.b("lectern", facing="west", has_book=True, powered=False))
    return w


def haengekaefig(seed, g=0):
    """Hängekäfig: ein eiserner Käfig hängt an Ketten von einem schweren Galgenbalken über dem Burggraben – zur
    Abschreckung."""
    w = _neu(seed)
    u = U[g]
    for x in range(-4, 5):
        for z in range(-4, 5):
            w.setze(x, 0, z, w.b("water", level=0) if abs(z) < 2 else w.b("grass_block", snowy=False))
    H = _r(8 * u + 5)
    for y in range(1, H + 1):
        w.setze(-3, y, -3, w.b("dark_oak_log", axis="y"))
    for z in range(-3, 1):
        w.setze(-3, H, z, w.b("dark_oak_log", axis="z"))
    for x in range(-3, 1):
        w.setze(x, H, 0, w.b("dark_oak_log", axis="x"))
    for y in range(H - 2, H):
        w.setze(0, y, 0, w.b("chain", axis="y", waterlogged=False))
    for y in range(H - 5, H - 2):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) == 1 or abs(dz) == 1:
                    w.setze(dx, y, dz, gitter(w, "x" if abs(dz) == 1 else "z"))
        w.setze(0, H - 6, 0, w.b("iron_trapdoor", facing="north", half="top", open=False, powered=False,
                                 waterlogged=False))
    return w


def gefaengnishof(seed, g=2):
    """Gefängnishof: ein ummauerter Hof mit Wehrgang, vier Ecktürmen und Wachen-Laternen, darin ein Brunnen und
    die Zellentrakte an zwei Seiten."""
    w = _neu(seed)
    u = U[g]
    M = stein(w, seed)
    a = _r(12 * u + 5)
    H = _r(5 * u + 3)
    boden(w, -a - 2, -a - 2, a + 2, a + 2, M)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if max(abs(x), abs(z)) == a:
                for y in range(1, H + 1):
                    w.setze(x, y, z, M(x, y, z, y / H))
                if (x + z) % 2 == 0:
                    w.setze(x, H + 1, z, M(x, H + 1, z, 0.9))
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="mcw_schiefer", holz="spruce")
    for sx in (-a, a):
        for sz in (-a, a):
            P.turm(w, st, sx, sz, 1, H + 4, 2.5, form="rund", dach="kegel", krone=True)
    b = _r(2 * u + 1, 2)
    for i in range(int((2 * a - 4) / (b + 2))):
        zelle(w, -a + 2 + i * (b + 2), -a + 1, b, b, 4, M, front="south")
        zelle(w, -a + 1, -a + 2 + (i + 1) * (b + 2), b, b, 4, M, front="east") if -a + 2 + (i + 1) * (b + 2) + b < a \
            else None
    from haeuser2 import ziehbrunnen
    ziehbrunnen(w, a // 3, a // 3)
    return w


def schuldturm(seed, g=1):
    """Schuldturm: ein schmaler, viereckiger Stadtturm mit vergitterten Fenstern, in dem Schuldner sitzen, mit
    Spendenkasten am Tor und Stadtwappen."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.15)
    st = P.Stil(w, wand="backstein" if _stil(seed) == 0 else "graustein", sockel="graustein", gesims="stone_brick",
                dach="mcw_ziegel", holz="dark_oak", laeden=False)
    H = _r(14 * u + 6)
    P.turm(w, st, 0, 0, 1, H, 3, form="eckig", dach="pyramide", krone=False, fenster=4)
    for y in range(4, H, 4):
        for (x, z) in ((3, 0), (-3, 0), (0, 3), (0, -3)):
            w.setze(x, y, z, gitter(w, "x" if abs(z) == 3 else "z"))
    w.setze(2, 1, 4, w.b("chest", facing="south", type="single", waterlogged=False))
    w.setze(0, H - 2, 4, w.b("red_wool"))
    return w


def ausbruchstunnel(seed, g=1):
    """Ausbruchstunnel: eine Zelle (aufgeschnitten) mit beiseitegeschobenem Strohlager, darunter ein heimlich
    gegrabener Tunnel mit Holzstützen, Löffel-Werkzeug und Erdeimern, der unter der Mauer ins Freie führt."""
    w = _neu(seed)
    u = U[g]
    M = stein(w, seed)
    L = _r(12 * u + 5)
    for x in range(-4, L + 3):
        for z in range(-4, 5):
            for y in range(-4, 1):
                w.setze(x, y, z, w.b("dirt") if y < 0 else w.b("grass_block", snowy=False) if x > 6 else
                        M(x, y, z, 0.3))
    zelle(w, -4, -3, 3, 4, 4, M, front="south", inhalt=False)
    for x in range(6, 8):
        for z in range(-4, 5):
            for y in range(1, 6):
                w.setze(x, y, z, M(x, y, z, y / 5))
    for x in range(-2, L):
        for z in (0, 1):
            for y in (-3, -2):
                w.bloecke.pop((x, y, z), None)
        if x % 3 == 0:
            for z in (-1, 2):
                for y in (-3, -2):
                    w.setze(x, y, z, w.b("oak_log", axis="y"))
            for z in range(-1, 3):
                w.setze(x, -1, z, w.b("oak_planks"))
    for y in (-1, 0):
        w.bloecke.pop((-2, y, 0), None)
    w.setze(-1, 1, 1, w.b("hay_block", axis="x"))
    w.setze(3, -3, 0, w.b("bucket") if False else w.b("cauldron"))
    for y in (-1, 0):
        w.bloecke.pop((L - 1, y, 0), None)
    return w


def magierkerker(seed, g=2):
    """Magierkerker: Zellen, deren Gitter von Runen gebannt werden – Seelenlaternen, Kristallschlösser, ein
    Bannkreis im Boden und eine schwebende Zelle für den gefährlichsten Hexer."""
    w = _neu(seed)
    u = U[g]
    M = Mat(w, ["polished_blackstone_bricks", "cracked_polished_blackstone_bricks", "chiseled_polished_blackstone",
                "obsidian", "crying_obsidian"])
    R = _r(10 * u + 4)
    boden(w, -R, -R, R, R, M)
    for k in range(int(R * 5)):
        a = k / (R * 5) * 6.28
        w.setze(round(math.cos(a) * R * 0.4), 0, round(math.sin(a) * R * 0.4), w.b("soul_soil" if k % 2 else
                                                                                  "crying_obsidian"))
    n = 4
    for i in range(n):
        a = i / n * 6.28 + 0.78
        cx, cz = round(math.cos(a) * R * 0.7), round(math.sin(a) * R * 0.7)
        zelle(w, cx - 2, cz - 2, 2, 2, 4, M, front="south" if cz < 0 else "north", inhalt=False)
        w.setze(cx, 4, cz, w.b("soul_lantern", hanging=True, waterlogged=False))
        w.setze(cx, 1, cz, w.b("amethyst_cluster", facing="up", waterlogged=False))
    Y = _r(6 * u + 4)
    for y in range(Y, Y + 3):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) == 1 or abs(dz) == 1:
                    w.setze(dx, y, dz, gitter(w, "x" if abs(dz) == 1 else "z"))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(dx, Y - 1, dz, w.b("crying_obsidian"))
            w.setze(dx, Y + 3, dz, w.b("crying_obsidian"))
    for k in range(4):
        a = k * 1.57
        for d in range(1, R // 2):
            y = Y - 1 - d // 2
            w.setze(round(math.cos(a) * d), max(1, y), round(math.sin(a) * d), w.b("chain", axis="y",
                                                                                   waterlogged=False), False)
    return w


def wassergefaengnis(seed, g=1):
    """Wassergefängnis: Zellen in einem überfluteten Gewölbe, das Wasser steht knöcheltief, Tropfsteine an den
    Wänden, ein erhöhter Steg für die Wachen."""
    w = _neu(seed)
    u = U[g]
    M = Mat(w, ["mossy_stone_bricks", "mossy_cobblestone", "cracked_stone_bricks", "prismarine_bricks"])
    n = 2 + g
    b = _r(2 * u + 1, 2)
    L = n * (b + 2)
    boden(w, -2, -b - 4, L + 2, b + 4, M)
    for x in range(-1, L + 1):
        for z in (-1, 0, 1):
            w.setze(x, 1, z, w.b("water", level=0) if z else w.b("stone_brick_slab", type="top", waterlogged=False))
    for i in range(n):
        zelle(w, i * (b + 2), 2, b, b, 4, M, front="north", wasser=True)
        zelle(w, i * (b + 2), -b - 3, b, b, 4, M, front="south", wasser=True)
    return w


def kettenhalle(seed, g=2):
    """Kettenhalle: ein hoher Saal mit Pfeilern, von deren Gewölbe dutzende schwere Ketten herabhängen, Ringe in
    den Wänden und ein Kohlebecken in der Mitte."""
    w = _neu(seed)
    u = U[g]
    M = stein(w, seed)
    a, b = _r(8 * u + 4), _r(6 * u + 3)
    H = _r(8 * u + 4)
    boden(w, -a - 1, -b - 1, a + 1, b + 1, M)
    for x in range(-a - 1, a + 2):
        for z in range(-b - 1, b + 2):
            if abs(x) == a + 1 or abs(z) == b + 1:
                if x > 0 and z > 0:
                    continue
                for y in range(1, H + 1):
                    w.setze(x, y, z, M(x, y, z, y / H))
    for x in range(-a + 2, a - 1, 4):
        for z in (-b // 2, b // 2):
            for y in range(1, H + 1):
                w.setze(x, y, z, M(x, y, z, y / H))
    rng = w.rng
    for k in range(int(20 * u)):
        x, z = int(rng.integers(-a, a + 1)), int(rng.integers(-b, b + 1))
        for y in range(H - int(rng.integers(2, H - 1)), H + 1):
            w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False), False)
    w.setze(0, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for (x, z) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        w.setze(x, 1, z, w.b("iron_bars", north=z != 0, south=z != 0, east=x != 0, west=x != 0, waterlogged=False))
    return w


def schatzverlies(seed, g=1):
    """Schatzverlies: eine gepanzerte Kammer hinter einer massiven Eisentür mit Hebeln, darin Goldbarren, Truhen,
    Kronen auf Kissen und Fallen im Boden."""
    w = _neu(seed)
    u = U[g]
    M = stein(w, seed)
    a = _r(5 * u + 2)
    boden(w, -a - 1, -a - 1, a + 1, a + 1, M)
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            if max(abs(x), abs(z)) == a + 1:
                for y in range(1, 5):
                    w.setze(x, y, z, w.b("iron_block") if (x + y + z) % 4 == 0 else M(x, y, z, 0.5))
    for y in (1, 2):
        w.setze(0, y, a + 1, w.b("iron_door", facing="south", half="lower" if y == 1 else "upper", hinge="left",
                                 open=False, powered=False))
    w.setze(1, 2, a + 2, w.b("lever", face="wall", facing="south", powered=False))
    rng = w.rng
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if abs(x) == a or abs(z) == a:
                if rng.random() < 0.6:
                    w.setze(x, 1, z, w.b("gold_block" if rng.random() < 0.5 else "chest", **(
                        {} if rng.random() < 0.5 else {})) if False else w.b("gold_block") if (x + z) % 2 else
                        w.b("chest", facing="north", type="single", waterlogged=False))
    w.setze(0, 1, 0, w.b("red_wool"))
    w.setze(0, 2, 0, w.b("gold_block"))
    for (x, z) in ((-1, 2), (1, 2), (0, 3)):
        w.setze(x, 0, z, w.b("stone_pressure_plate", powered=False) if False else M(x, 0, z, 0.2))
    return w


def felsverlies(seed, g=2):
    """Felsverlies: Zellen in eine Felswand gehauen, mit Gittertüren am Fuß der Klippe, ein Pfad mit Wachposten und
    Fackeln davor."""
    from zwerge import Zwerg, bergwand
    w = _neu(seed)
    u = U[g]
    Z = Zwerg(w, seed)
    W, H = 16 * u + 6, 12 * u + 5
    bergwand(w, 0, W, H, Z, D=8)
    gelaende(w, _r(W), art="wiese", dichte=0.15)
    for i in range(int(3 + u)):
        x0 = round(-W * 0.6 + i * W * 1.2 / (3 + u))
        for x in range(x0, x0 + 3):
            for y in range(1, 4):
                for z in range(-4, 1):
                    w.bloecke.pop((x, y, z), None)
            w.setze(x, 1, 1, gitter(w, "x"))
            w.setze(x, 2, 1, gitter(w, "x"))
        w.setze(x0 + 1, 1, -3, w.b("hay_block", axis="x"))
        w.setze(x0 + 3, 3, 2, w.b("lantern", hanging=False, waterlogged=False))
    return w


def kerkergang(seed, g=1):
    """Kerkergang: ein gerades, offenes Gangstück mit Bodengitter, Wandnischen und Laternen – kachelbar, um
    Verliese beliebig zu verbinden."""
    w = _neu(seed)
    L = [8, 14, 22, 32][g]
    M = stein(w, seed)
    gang(w, -L, L, 0, 1, 4, M)
    for x in range(-L, L + 1, 6):
        w.setze(x, 0, 0, w.b("iron_trapdoor", facing="north", half="top", open=False, powered=False,
                             waterlogged=False))
    return w


def kerkerkreuzung(seed, g=1):
    """Kerkerkreuzung: vier Gänge treffen sich unter einer Säule mit Kohlebecken – passt an das Gangstück."""
    w = _neu(seed)
    L = [8, 14, 22, 32][g]
    M = stein(w, seed)
    gang(w, -L, L, 0, 1, 4, M)
    for x in range(-L, L + 1):
        for d in range(-2, 3):
            w.setze(d, 0, x, M(d, 0, x, 0.2))
            if abs(d) == 2 and abs(x) > 2:
                for y in range(1, 5):
                    w.setze(d, y, x, M(d, y, x, y / 4))
    for d in range(-1, 2):
        for z in (-2, 2):
            for y in range(1, 5):
                w.bloecke.pop((d, y, z), None)
    for x in (-2, 2):
        for z in (-2, 2):
            for y in range(1, 5):
                w.setze(x, y, z, M(x, y, z, y / 4))
    w.setze(0, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


def gefaengnisruine(seed, g=2):
    """Gefängnisruine: ein verlassener, halb eingestürzter Zellentrakt, durch dessen offenes Dach Bäume wachsen,
    verrostete Gitter, Moos und Ranken überall."""
    from veredeln import bewuchs
    import wald2
    from lib import einfuegen
    w = burgverlies(seed, g)
    rng = w.rng
    for p in list(w.bloecke):
        if p[1] >= 3 and rng.random() < 0.45:
            del w.bloecke[p]
        elif p[1] >= 1 and w.P.name(w.bloecke[p]) == "minecraft:iron_bars" and rng.random() < 0.4:
            del w.bloecke[p]
    bewuchs(w, moos=0.12, ranken=0.15)
    xs = [p[0] for p in w.bloecke]
    for k in range(2):
        einfuegen(w, wald2.birke(int(rng.integers(1, 10 ** 6)), H=7), int(rng.integers(min(xs), max(xs))), 0,
                  0 if k else 3)
    return w


def gerichtshaus(seed, g=2):
    """Gerichtshaus: ein ernster Steinbau mit Säulenportal, Richterbank im aufgeschnittenen Saal, Waage der
    Gerechtigkeit über dem Eingang und der Weg zum Kerker an der Seite."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.1)
    st = P.Stil(w, wand="marmor" if _stil(seed) == 0 else "graustein", sockel="graustein", gesims="quartz",
                dach="mcw_schiefer", holz="dark_oak", fensterart="bogen")
    a, b = _r(7 * u + 3), _r(5 * u + 2)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=5, dach="walm", tuer="south", gauben=False, kamine=0,
               pilaster=2)
    for x in range(-4, 5, 2):
        for y in range(1, 9):
            w.setze(x, y, b + 3, w.b("quartz_pillar", axis="y"))
    for x in range(-5, 6):
        w.setze(x, 9, b + 3, w.b("smooth_quartz"))
        w.setze(x, 9, b + 2, w.b("smooth_quartz"))
    w.setze(0, 10, b + 3, w.b("gold_block"))
    for x in (-1, 1):
        w.setze(x, 10, b + 3, w.b("chain", axis="x", waterlogged=False))
        w.setze(x * 2, 9, b + 4, w.b("gold_block"))
    return w


def gefangenenwagen(seed, g=0):
    """Gefangenenwagen: ein schwerer Holzwagen mit Eisengitter-Käfig auf vier Rädern, Kutschbock und Laterne, bereit
    für den Transport zum Kerker."""
    w = _neu(seed)
    for x in range(-5, 6):
        for z in range(-4, 5):
            w.setze(x, 0, z, w.b("dirt_path" if abs(z) < 3 else "grass_block", **({} if abs(z) < 3 else
                                                                                  {"snowy": False})))
    for x in range(-3, 3):
        for z in (-1, 0, 1):
            w.setze(x, 2, z, w.b("dark_oak_planks"))
        for z in (-1, 1):
            for y in (3, 4):
                w.setze(x, y, z, gitter(w, "x"))
        w.setze(x, 5, 0, w.b("dark_oak_slab", type="bottom", waterlogged=False))
        w.setze(x, 5, -1, w.b("dark_oak_slab", type="bottom", waterlogged=False))
        w.setze(x, 5, 1, w.b("dark_oak_slab", type="bottom", waterlogged=False))
    for z in (-1, 0, 1):
        for y in (3, 4):
            w.setze(-3, y, z, gitter(w, "z"))
            w.setze(2, y, z, w.b("dark_oak_planks"))
    for x in (-2, 1):
        for z in (-2, 2):
            w.setze(x, 1, z, w.b("dark_oak_trapdoor", facing="north" if z < 0 else "south", half="bottom",
                                 open=True, powered=False, waterlogged=False))
    w.setze(3, 3, 0, w.b("dark_oak_stairs", facing="west", half="bottom", shape="straight", waterlogged=False))
    w.setze(4, 2, 0, w.b("dark_oak_fence", north=False, south=False, east=True, west=False, waterlogged=False))
    w.setze(3, 5, 1, w.b("lantern", hanging=False, waterlogged=False))
    return w


def bestienkerker(seed, g=2):
    """Bestienkerker: riesige Käfige aus dicken Gitterstäben für gefangene Ungeheuer, Ketten mit Eisenkugeln,
    Futtertröge und zerkratzte Wände."""
    w = _neu(seed)
    u = U[g]
    M = stein(w, seed)
    R = _r(12 * u + 5)
    boden(w, -R, -R, R, R, M)
    c = _r(4 * u + 2)
    H = _r(5 * u + 3)
    for i, (cx, cz) in enumerate(((-R // 2, -R // 2), (R // 2, -R // 2), (-R // 2, R // 2))):
        for x in range(cx - c, cx + c + 1):
            for z in range(cz - c, cz + c + 1):
                if max(abs(x - cx), abs(z - cz)) == c:
                    for y in range(1, H + 1):
                        w.setze(x, y, z, gitter(w, "x" if abs(z - cz) == c else "z") if (x + z) % 2 else
                                w.b("iron_block") if y % 3 == 0 else gitter(w, "x" if abs(z - cz) == c else "z"))
                w.setze(x, H + 1, z, w.b("iron_trapdoor", facing="north", half="bottom", open=False, powered=False,
                                         waterlogged=False) if max(abs(x - cx), abs(z - cz)) < c else w.b("iron_block"))
        w.setze(cx, 1, cz, w.b("bone_block", axis="y"))
        w.setze(cx + 1, 1, cz, w.b("hay_block", axis="y"))
    for k in range(4):
        x, z = R // 2 + k - 2, R // 2
        w.setze(x, 1, z, w.b("chain", axis="x", waterlogged=False))
    w.setze(R // 2 + 2, 1, R // 2, w.b("anvil", facing="north"))
    return w


def kerkertor(seed, g=1):
    """Kerkertor: ein wuchtiges Torhaus mit Fallgitter und Pechnasen über dem Eingang, Wachhäuschen und einer
    Treppe, die hinab in die Dunkelheit führt."""
    w = _neu(seed)
    u = U[g]
    R = _r(9 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.1)
    M = stein(w, seed)
    B = _r(2 * u + 1, 2)
    H = _r(6 * u + 4)
    for x in range(-B - 3, B + 4):
        for z in range(-2, 3):
            for y in range(1, H + 1):
                if abs(x) <= B and y <= H - 3:
                    continue
                w.setze(x, y, z, M(x, y, z, y / H))
        if x % 2 == 0:
            w.setze(x, H + 1, 2, M(x, H + 1, 2, 0.9))
    for x in range(-B, B + 1):
        for y in range(H - 5, H - 3):
            w.setze(x, y, 0, gitter(w, "x"))
        w.setze(x, H - 2, 3, w.b("stone_brick_slab", type="top", waterlogged=False))
    for k in range(4):
        for x in range(-B, B + 1):
            w.setze(x, -k, -3 - k, w.b("stone_brick_stairs", facing="south", half="bottom", shape="straight",
                                       waterlogged=False))
            for y in range(-k + 1, 1):
                w.bloecke.pop((x, y, -3 - k), None)
    w.setze(-B - 1, 2, 3, w.b("lantern", hanging=False, waterlogged=False))
    w.setze(B + 1, 2, 3, w.b("lantern", hanging=False, waterlogged=False))
    return w


def kerkerzelle(seed, g=0):
    """Einzelzelle: eine detailliert eingerichtete Kerkerzelle mit Strohlager, Wandkette, Wassereimer,
    Strichliste an der Wand, Rattenloch und einem Lichtschacht hoch oben."""
    w = _neu(seed)
    M = stein(w, seed)
    boden(w, -4, -4, 4, 4, M)
    zelle(w, -3, -3, 5, 5, 5, M, front="south")
    for k in range(4):
        w.setze(-3, 2, -2 + k, w.b("spruce_wall_sign", facing="east", waterlogged=False)) if k == 1 else None
    w.setze(0, 5, -3, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
    w.setze(2, 1, -2, w.b("cauldron"))
    w.setze(-2, 1, 2, w.b("cobweb"))
    return w


KERKER = {
    "burgverlies": ("Burgverlies", burgverlies),
    "zellenblock": ("Zellenblock", zellenblock),
    "kerkerturm": ("Kerkerturm", kerkerturm),
    "wachstube": ("Wachstube", wachstube),
    "verlieseingang": ("Eingang zum Verlies", verlieseingang),
    "oubliette": ("Oubliette", oubliette),
    "gefaengnisinsel": ("Gefängnisinsel", gefaengnisinsel),
    "pranger": ("Pranger", pranger),
    "haengekaefig": ("Hängekäfig", haengekaefig),
    "gefaengnishof": ("Gefängnishof", gefaengnishof),
    "schuldturm": ("Schuldturm", schuldturm),
    "ausbruchstunnel": ("Ausbruchstunnel", ausbruchstunnel),
    "magierkerker": ("Magierkerker", magierkerker),
    "wassergefaengnis": ("Wassergefängnis", wassergefaengnis),
    "kettenhalle": ("Kettenhalle", kettenhalle),
    "schatzverlies": ("Schatzverlies", schatzverlies),
    "felsverlies": ("Felsverlies", felsverlies),
    "kerkergang": ("Kerkergang", kerkergang),
    "kerkerkreuzung": ("Kerkerkreuzung", kerkerkreuzung),
    "gefaengnisruine": ("Gefängnisruine", gefaengnisruine),
    "gerichtshaus": ("Gerichtshaus", gerichtshaus),
    "gefangenenwagen": ("Gefangenenwagen", gefangenenwagen),
    "bestienkerker": ("Bestienkerker", bestienkerker),
    "kerkertor": ("Kerkertor", kerkertor),
    "kerkerzelle": ("Einzelzelle", kerkerzelle),
}

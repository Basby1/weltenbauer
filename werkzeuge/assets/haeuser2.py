"""Häuser – 80 weitere Bauten für eine Mittelalter- und Fantasiewelt.

Baukasten aus Archetypen (Wohnhaus, Winkelhaus, Fachwerk mit Überhang, Turmhaus, Werkstatt, Laden, Gasthof,
Stall, Speicher, Hütte, Stadthaus, Amtsbau, Fantasiehaus), die mit eigenem Stil, eigenen Maßen, Anbauten
und einem passend eingerichteten Grundstück zu 80 verschiedenen Gebäuden kombiniert werden.
"""

from __future__ import annotations

import math

import modbloecke as MB
import pracht as P
from haeuser import HAUSPOOL, bank, beet, holzstapel, laternenpfahl, weg, zaun
from lib import Rauschen, einfuegen, laub
from pracht import Mat, gelaende
from skulptur import kreisrand, scheibe
from weltwunder import hohl

F = [0.75, 1.0, 1.3, 1.7]
GEGEN = {"north": "south", "south": "north", "east": "west", "west": "east"}
RICHT = {"south": (0, 1), "north": (0, -1), "east": (1, 0), "west": (-1, 0)}

POOL2 = dict(HAUSPOOL)
POOL2.update({
    "fachwerk_weiss": dict(wand="putz", sockel="graustein", gesims="stone_brick", dach="mcw_ziegel", holz="dark_oak",
                           fachwerk=True),
    "fachwerk_gruen": dict(wand="putz", sockel="graustein", gesims="stone_brick", dach="schindel_gruen",
                           holz="spruce", fachwerk=True),
    "stroh_lehm": dict(wand="lehm", sockel="graustein", gesims="mud_brick", dach="mcw_stroh", holz="oak",
                       fachwerk=True),
    "bruchstein": dict(wand="graustein", sockel="graustein", gesims="stone_brick", dach="mcw_schiefer",
                       holz="dark_oak"),
    "holz_rot": dict(wand=["spruce_planks", "spruce_planks", "stripped_spruce_log"], sockel="graustein",
                     gesims="stone_brick", dach="schindel_rot", holz="spruce"),
    "holz_blau": dict(wand=["dark_oak_planks", "spruce_planks"], sockel="graustein", gesims="stone_brick",
                      dach="schindel_blau", holz="dark_oak"),
    "patrizier": dict(wand="kalkstein", sockel="graustein", gesims="stone_brick", dach="mcw_schiefer",
                      holz="dark_oak"),
    "backstein_rot": dict(wand="backstein", sockel="graustein", gesims="brick", dach="mcw_ziegel", holz="spruce"),
    "tief": dict(wand="tiefenschiefer", sockel="tiefenschiefer", gesims="deepslate_brick", dach="schiefer",
                 holz="dark_oak"),
    "elfen": dict(wand="marmor", sockel="kalkstein", gesims="quartz", dach="mcw_gruen", holz="birch"),
    "magier": dict(wand="tiefenschiefer", sockel="schwarzstein", gesims="polished_blackstone_brick",
                   dach="mcw_lila", holz="dark_oak"),
    "moos": dict(wand="moosstein", sockel="graustein", gesims="mossy_stone_brick", dach="moos", holz="spruce"),
    "sand2": dict(wand="sandstein", sockel="sandstein", gesims="sandstone", dach="mcw_gelb", holz="jungle"),
    "ocker_blau": dict(wand="ockerputz", sockel="graustein", gesims="stone_brick", dach="mcw_blau", holz="spruce",
                       fachwerk=True),
})


def _welt(seed):
    from lib import Welt
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def stil(w, seed, pools, **extra):
    a, b = pools if isinstance(pools, tuple) else (pools, pools)
    d = dict(POOL2[a if _stil(seed) == 0 else b])
    d.update(extra)
    return P.Stil(w, **d)


# ============================================================================ Kleinkram fürs Grundstück


def zf(w, holz, **v):
    d = dict(north=False, south=False, east=False, west=False, waterlogged=False)
    d.update(v)
    return w.b(f"{holz}_fence", **d)


def karren(w, x, z, holz="spruce", ladung="hay_block"):
    for dx in range(3):
        w.setze(x + dx, 1, z, w.b(f"{holz}_slab", type="top", waterlogged=False))
        w.setze(x + dx, 2, z, w.b(ladung, axis="y") if ladung == "hay_block" else w.b(ladung))
    for dx in (0, 2):
        w.setze(x + dx, 1, z - 1, w.b(f"{holz}_trapdoor", facing="north", half="bottom", open=True, powered=False,
                                      waterlogged=False))
        w.setze(x + dx, 1, z + 1, w.b(f"{holz}_trapdoor", facing="south", half="bottom", open=True, powered=False,
                                      waterlogged=False))
    w.setze(x - 1, 1, z, zf(w, holz, east=True))


def ziehbrunnen(w, x, z, stein="cobblestone"):
    for dx, dz in scheibe(1.5, 0, 0):
        if abs(dx) + abs(dz) > 0:
            w.setze(x + dx, 1, z + dz, w.b(stein if stein != "cobblestone" else "mossy_cobblestone"
                                           if (dx + dz) % 2 else "cobblestone"))
    w.setze(x, 0, z, w.b("water", level=0))
    w.setze(x, 1, z, w.b("water", level=0))
    for dx in (-1, 1):
        for y in (2, 3):
            w.setze(x + dx, y, z, zf(w, "spruce"))
    for dx in (-1, 0, 1):
        w.setze(x + dx, 4, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    w.setze(x, 3, z, w.b("chain", axis="y", waterlogged=False))
    w.setze(x, 2, z, w.b("lantern", hanging=True, waterlogged=False) if False else w.b("water_cauldron", level=3)
            if False else w.b("chain", axis="y", waterlogged=False))


def waescheleine(w, x, z, laenge=5):
    for dx in (0, laenge):
        for y in (1, 2, 3):
            w.setze(x + dx, y, z, zf(w, "spruce"))
    farben = ["white", "light_blue", "red", "yellow", "white", "pink"]
    for dx in range(1, laenge):
        w.setze(x + dx, 3, z, w.b("tripwire", attached=False, disarmed=False, east=True, west=True, north=False,
                                  south=False, powered=False))
        if dx % 2:
            w.setze(x + dx, 2, z, w.b(f"{farben[dx % len(farben)]}_carpet") if False else
                    w.b(f"{farben[dx % len(farben)]}_banner", rotation=0) if False else
                    w.b(f"{farben[dx % len(farben)]}_wool"))


def heuhaufen(w, x, z):
    for dx, dz in scheibe(1.6):
        w.setze(x + dx, 1, z + dz, w.b("hay_block", axis="y"))
    w.setze(x, 2, z, w.b("hay_block", axis="y"))


def misthaufen(w, x, z):
    for dx, dz in scheibe(1.4):
        w.setze(x + dx, 1, z + dz, w.b("coarse_dirt") if (dx + dz) % 2 else w.b("podzol", snowy=False))
    w.setze(x, 2, z, w.b("composter", level=6))


def fassstapel(w, x, z, n=3):
    for k in range(n):
        w.setze(x + k, 1, z, w.b("barrel", facing="east", open=False))
        if k < n - 1:
            w.setze(x + k, 2, z, w.b("barrel", facing="up", open=False))


def kisten(w, x, z, n=3):
    for k in range(n):
        w.setze(x + k, 1, z, MB.ware(w, w.rng) if k % 2 else w.b("barrel", facing="up", open=False))


def koppel(w, x0, z0, x1, z1, holz="oak", tier_futter=True):
    pts = set()
    for x in range(x0, x1 + 1):
        pts |= {(x, z0), (x, z1)}
    for z in range(z0, z1 + 1):
        pts |= {(x0, z), (x1, z)}
    pts.discard(((x0 + x1) // 2, z1))
    for (x, z) in pts:
        w.setze(x, 1, z, zf(w, holz, north=(x, z - 1) in pts, south=(x, z + 1) in pts, east=(x + 1, z) in pts,
                            west=(x - 1, z) in pts))
    if tier_futter:
        w.setze(x0 + 1, 1, z0 + 1, w.b("hay_block", axis="y"))
        w.setze(x0 + 2, 1, z0 + 1, w.b("water_cauldron", level=3))
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            if (x, z) != (x0 + 1, z0 + 1):
                w.setze(x, 0, z, w.b("coarse_dirt") if (x + z) % 3 == 0 else w.b("grass_block", snowy=False))


def obstbaum(w, x, z, bluete=False):
    import wald2
    einfuegen(w, wald2.laubbaum(int(w.rng.integers(1, 10 ** 7)), "oak", H=5 + int(w.rng.integers(3)),
                                blaetter=[("oak", 0.7), ("flowering_azalea" if bluete else "azalea", 0.3)], breit=0.8),
              x, 0, z)


def werkbank(w, x, z, holz="spruce", gegenstaende=("crafting_table",)):
    for k, g in enumerate(gegenstaende):
        if g == "anvil":
            w.setze(x + k, 1, z, w.b("anvil", facing="north"))
        elif g in ("smithing_table", "crafting_table", "fletching_table", "cartography_table", "loom", "stonecutter",
                   "grindstone", "brewing_stand", "lectern", "composter", "smoker", "blast_furnace", "barrel",
                   "cauldron"):
            props = {}
            if g in ("loom", "stonecutter", "smoker", "blast_furnace"):
                props = dict(facing="north")
            if g in ("smoker", "blast_furnace"):
                props["lit"] = True
            if g == "grindstone":
                props = dict(face="floor", facing="north")
            if g == "brewing_stand":
                props = dict(has_bottle_0=True, has_bottle_1=False, has_bottle_2=True)
            if g == "lectern":
                props = dict(facing="north", has_book=True, powered=False)
            if g == "composter":
                props = dict(level=4)
            if g == "barrel":
                props = dict(facing="up", open=False)
            w.setze(x + k, 1, z, w.b(g, **props))
        else:
            w.setze(x + k, 1, z, w.b(g))


def vordach(w, st, x0, x1, z, y, richtung="south", tiefe=2, pfosten=True):
    """Pultdach-Vordach (Werkstatt, Veranda, Laube) mit Pfosten."""
    dz = 1 if richtung == "south" else -1
    D = st.dach
    for x in range(x0, x1 + 1):
        for k in range(1, tiefe + 1):
            w.setze(x, y - (k - 1) // 2, z + dz * k, D.treppe(x, y, z + dz * k, GEGEN[richtung] if False else
                                                                 ("north" if dz > 0 else "south")))
    if pfosten:
        for x in (x0, x1):
            for yy in range(1, y - (tiefe - 1) // 2):
                w.setze(x, yy, z + dz * tiefe, w.b(f"{st.holz}_log", axis="y"))


# ============================================================================ Archetypen


def _grund(w, b, t, art="wiese", dichte=0.4):
    gelaende(w, max(b, t) + 6, art=art, dichte=dichte)


def wohnhaus(seed, g, pools, b=4, t=3, etagen=1, dach="sattel", steil=False, first_x=None, eh=4,
             anbau=None, ueberhang=False, turm=None, laube=False, garten="blumen", deko=(), kamine=1,
             grund="wiese", gauben=True, sockel_h=1, extra=None, tuer="south"):
    """Allgemeines Wohnhaus mit optionalem Anbau, Überhang, Turm, Laube und Grundstück."""
    w = _welt(seed)
    f = F[g]
    B, T = _r(b * f, 2), _r(t * f, 2)
    _grund(w, B + 4, T + 4, grund)
    st = stil(w, seed, pools, **(extra or {}))
    y0 = 1
    if ueberhang:
        P.gebaeude(w, st, -B, -T, B, T, y0=y0, etagen=1, eh=eh, dach="flach", tuer=tuer, gauben=False, kamine=0,
                   sockel_h=sockel_h)
        ytop = y0 + sockel_h + eh
        for x in range(-B - 1, B + 2):
            for z in range(-T - 1, T + 2):
                w.setze(x, ytop - 1, z, w.b(f"{st.holz}_planks"), ueberschreiben=False)
            for z in (-T - 1, T + 1):
                w.setze(x, ytop - 2, z, w.b(f"{st.holz}_stairs", facing="north" if z > 0 else "south", half="top",
                                            shape="straight", waterlogged=False), ueberschreiben=False)
        P.gebaeude(w, st, -B - 1, -T - 1, B + 1, T + 1, y0=ytop, etagen=max(1, etagen - 1), eh=eh, dach=dach,
                   tuer=None if False else tuer, gauben=gauben, kamine=kamine, sockel_h=0, steil=steil, first_x=first_x)
        for x in range(-B, B + 1):
            w.bloecke.pop((x, ytop, T + 1), None) if (x == 0) else None
    else:
        P.gebaeude(w, st, -B, -T, B, T, y0=y0, etagen=etagen, eh=eh, dach=dach, tuer=tuer, gauben=gauben,
                   kamine=kamine, steil=steil, first_x=first_x, sockel_h=sockel_h)
    if anbau:
        seite, ab, at, ae = anbau
        Ab, At = _r(ab * f, 2), _r(at * f, 2)
        if seite == "east":
            x0, x1, z0, z1 = B + 1, B + 1 + 2 * Ab, -At, At
        elif seite == "west":
            x0, x1, z0, z1 = -B - 1 - 2 * Ab, -B - 1, -At, At
        elif seite == "north":
            x0, x1, z0, z1 = -Ab, Ab, -T - 1 - 2 * At, -T - 1
        else:
            x0, x1, z0, z1 = -Ab, Ab, T + 1, T + 1 + 2 * At
        P.gebaeude(w, st, x0, z0, x1, z1, y0=y0, etagen=ae, eh=eh, dach="sattel",
                   first_x=seite in ("north", "south") and False, tuer="south" if seite != "north" else "east",
                   gauben=False, kamine=0, sockel_h=sockel_h)
    if turm:
        ecke, R, Ht, form = turm
        tx = (B + 1) * (1 if "e" in ecke else -1)
        tz = (T + 1) * (1 if "s" in ecke else -1)
        P.turm(w, st, tx, tz, y0, _r(Ht * f), max(1.6, R * f), form=form, dach="kegel" if form == "rund" else
               "pyramide", krone=False, fahne=None, fenster=5)
    if laube:
        vordach(w, st, -B, B, T, y0 + sockel_h + eh - 1, "south", tiefe=3)
        for x in range(-B, B + 1):
            for z in range(T + 1, T + 4):
                w.setze(x, y0 + sockel_h - 1, z, w.b(f"{st.holz}_planks"))
    zz = T + 5 + (3 if laube else 0)
    if garten == "blumen":
        beet(w, -B, zz, -2, zz + 1, "blumen")
        beet(w, 2, zz, B, zz + 1, "blumen")
    elif garten == "gemuese":
        beet(w, B + 3, -T, B + 3 + _r(4 * f), T, "gemuese")
    elif garten == "zaun":
        zaun(w, st, -B - 3, -T - 3, B + 3, zz + 2, tor=[(0, 1, zz + 2), (1, 1, zz + 2), (-1, 1, zz + 2)])
    weg(w, (0, T + 2), (0, zz + 3), 1)
    _deko(w, st, deko, B, T, f)
    hohl(w, 2)
    return w


def _deko(w, st, deko, B, T, f):
    rng = w.rng
    for d in deko:
        if d == "holz":
            holzstapel(w, -B - 3, -T, 4, st.holz, "z")
        elif d == "brunnen":
            ziehbrunnen(w, B + 5, T + 3)
        elif d == "waesche":
            waescheleine(w, -B - 2, -T - 4, 5)
        elif d == "karren":
            karren(w, B + 4, T + 2, st.holz)
        elif d == "heu":
            heuhaufen(w, -B - 4, T + 2)
        elif d == "mist":
            misthaufen(w, B + 4, -T - 3)
        elif d == "faesser":
            fassstapel(w, B + 2, T + 2)
        elif d == "kisten":
            kisten(w, -B - 1, T + 2)
        elif d == "bank":
            bank(w, -2, T + 2, "north", st.holz)
        elif d == "laterne":
            laternenpfahl(w, 2, T + 3, 3, st.holz)
        elif d == "obst":
            obstbaum(w, -B - 5, T + 3, bluete=rng.random() < 0.5)
            obstbaum(w, B + 6, -T - 2)
        elif d == "baum":
            obstbaum(w, B + 6, T + 5)
        elif d == "huehner":
            koppel(w, -B - 7, -T, -B - 2, T - 2, st.holz)
            w.setze(-B - 5, 1, -T + 1, w.b("hay_block", axis="y"))
        elif d == "koppel":
            koppel(w, B + 3, -T - 2, B + 3 + _r(8 * f), T + 3, st.holz)
        elif d == "bienen":
            for k in range(3):
                w.setze(-B - 3 + k * 2, 1, T + 3, w.b("beehive", facing="south", honey_level=k * 2))
        elif d == "hund":
            for x in range(2):
                for z in range(2):
                    w.setze(B + 2 + x, 1, -T + z, w.b(f"{st.holz}_planks"))
            w.setze(B + 2, 2, -T, w.b(f"{st.holz}_slab", type="bottom", waterlogged=False))
            w.setze(B + 3, 2, -T, w.b(f"{st.holz}_slab", type="bottom", waterlogged=False))
        elif d == "mauer":
            for x in range(-B - 4, B + 5):
                for z in (-T - 4, T + 8):
                    w.setze(x, 1, z, w.b("mossy_cobblestone") if (x + z) % 3 else w.b("cobblestone"))
            for z in range(-T - 4, T + 9):
                for x in (-B - 4, B + 4):
                    if not (abs(z - T - 4) < 2 and False):
                        w.setze(x, 1, z, w.b("mossy_cobblestone") if (x + z) % 3 else w.b("cobblestone"))
            for x in (-1, 0, 1):
                w.bloecke.pop((x, 1, T + 8), None)


def werkstatt(seed, g, pools, b=4, t=3, etagen=2, offen="east", ausstattung=(), hof=(), schild=None,
              dach="sattel", rauch=False, extra=None):
    """Wohnhaus mit offener Werkstatt unter einem Pultdach an der Seite."""
    w = _welt(seed)
    f = F[g]
    B, T = _r(b * f, 2), _r(t * f, 2)
    gelaende(w, B + 6, art="wiese", dichte=0.3)
    st = stil(w, seed, pools, **(extra or {}))
    P.gebaeude(w, st, -B, -T, B, T, y0=1, etagen=etagen, eh=4, dach=dach, tuer="south", gauben=True,
               kamine=1 + rauch)
    L = _r(4 * f + 1, 4)
    xw0 = B + 1
    for x in range(xw0, xw0 + L + 1):
        for z in range(-T, T + 1):
            w.setze(x, 0, z, w.b("stone_bricks") if (x + z) % 3 else w.b("cobblestone"))
    for z in (-T, T):
        for y in range(1, 5):
            w.setze(xw0 + L, y, z, w.b(f"{st.holz}_log", axis="y"))
    for z in range(-T, T + 1):
        for x in range(xw0, xw0 + L + 1):
            y = 5 - (x - xw0) * 2 // max(1, L)
            w.setze(x, y, z, st.dach.treppe(x, y, z, "west"))
    for k, gegen in enumerate(ausstattung):
        z = -T + 1 + k * 2
        if z > T - 1:
            break
        werkbank(w, xw0 + 1 + (k % 2), z, st.holz, (gegen,))
    for i, h in enumerate(hof):
        _hofteil(w, st, h, -B - 2, T + 3 + i * 3, f)
    if rauch:
        w.setze(xw0 + L // 2, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    weg(w, (0, T + 2), (0, T + 8), 1)
    hohl(w, 2)
    return w


def _hofteil(w, st, art, x, z, f):
    if art == "holz":
        holzstapel(w, x, z, 4, st.holz)
    elif art == "faesser":
        fassstapel(w, x, z, 4)
    elif art == "kisten":
        kisten(w, x, z, 4)
    elif art == "karren":
        karren(w, x, z, st.holz, "barrel")
    elif art == "stein":
        for k in range(4):
            for y in (1, 2) if k % 2 else (1,):
                w.setze(x + k, y, z, w.b(["stone", "calcite", "andesite", "smooth_stone"][k]))
    elif art == "ton":
        for k in range(3):
            w.setze(x + k, 1, z, w.b("clay"))
        w.setze(x + 1, 2, z, w.b("decorated_pot", facing="north", cracked=False, waterlogged=False))
    elif art == "wolle":
        for k in range(4):
            w.setze(x + k, 1, z, w.b(["white_wool", "red_wool", "blue_wool", "yellow_wool"][k]))
    elif art == "leder":
        for y in (1, 2, 3):
            w.setze(x, y, z, zf(w, st.holz))
            w.setze(x + 3, y, z, zf(w, st.holz))
        for k in range(4):
            w.setze(x + k, 4, z, w.b(f"{st.holz}_slab", type="bottom", waterlogged=False))
        w.setze(x + 1, 3, z, w.b("brown_wool"))
        w.setze(x + 2, 3, z, w.b("orange_wool"))
    elif art == "seil":
        for k in range(8):
            w.setze(x + k, 1, z, MB.seil(w, "x") if False else w.b("spruce_fence", north=False, south=False,
                                                                     east=k < 7, west=k > 0, waterlogged=False))
    elif art == "glas":
        for k in range(4):
            w.setze(x + k, 1, z, w.b(["red_stained_glass", "blue_stained_glass", "lime_stained_glass",
                                      "yellow_stained_glass"][k]))
    elif art == "kerzen":
        for k in range(4):
            w.setze(x + k, 1, z, w.b("barrel", facing="up", open=False))
            w.setze(x + k, 2, z, w.b("candle", candles=k + 1, lit=True, waterlogged=False))
    elif art == "korb":
        for k in range(4):
            w.setze(x + k, 1, z, MB.korb(w))
    elif art == "waffen":
        for k in range(4):
            w.setze(x + k, 1, z, w.b("lightning_rod", facing="up", powered=False, waterlogged=False)
                    if k % 2 else w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
    elif art == "beet":
        beet(w, x, z, x + 4, z + 1, "gemuese")
    elif art == "heu":
        heuhaufen(w, x + 1, z)


def laden(seed, g, pools, b=4, t=3, etagen=2, markise=("red", "white"), waren=(), schild=None, extra=None,
          dach="sattel", steil=False, first_x=None):
    """Laden mit Schaufenstern, Markise, Auslagen vor der Tür und Wohnung im Obergeschoss."""
    w = _welt(seed)
    f = F[g]
    B, T = _r(b * f, 2), _r(t * f, 2)
    _grund(w, B + 4, T + 6)
    st = stil(w, seed, pools, **(extra or {}))
    P.gebaeude(w, st, -B, -T, B, T, y0=1, etagen=etagen, eh=4, dach=dach, tuer="south", gauben=True, kamine=1,
               steil=steil, first_x=first_x)
    for x in range(-B + 1, B):
        if abs(x) > 1:
            for y in (2, 3):
                w.setze(x, y, T, w.b("glass_pane", east=True, west=True, north=False, south=False, waterlogged=False))
    for x in range(-B, B + 1):
        w.setze(x, 5, T + 1, MB.markise(w, markise[(x + B) % len(markise)], "south"))
    for x in range(-B, B + 1):
        for z in range(T + 1, T + 4):
            w.setze(x, 0, z, MB.pflaster(w, "cobblestone", "running_bond") if (x + z) % 3 else w.b("cobblestone"))
    for k, ware in enumerate(waren):
        x = -B + k * 2
        if x > B or abs(x) <= 1:
            continue
        w.setze(x, 1, T + 2, w.b(f"{st.holz}_planks") if ware != "fass" else w.b("barrel", facing="up", open=False))
        if ware == "fass":
            continue
        if ware == "ware":
            w.setze(x, 2, T + 2, MB.ware(w, w.rng))
        elif ware == "korb":
            w.setze(x, 2, T + 2, MB.korb(w))
        else:
            w.setze(x, 2, T + 2, w.b(ware))
    laternenpfahl(w, B + 2, T + 3, 3, st.holz)
    hohl(w, 2)
    return w


def gasthof(seed, g, pools, b=6, t=4, etagen=2, stall=True, biergarten=True, fluegel=False, extra=None):
    """Gasthof: großes Haupthaus, Stall/Remise, Hof mit Brunnen, Biergarten mit Tischen und Laternen."""
    w = _welt(seed)
    f = F[g]
    B, T = _r(b * f, 3), _r(t * f, 3)
    _grund(w, B + 10, T + 8)
    st = stil(w, seed, pools, **(extra or {}))
    P.gebaeude(w, st, -B, -T, B, T, y0=1, etagen=etagen, eh=4, dach="sattel", tuer="south", gauben=True, kamine=2)
    if fluegel:
        P.gebaeude(w, st, B + 1, -T, B + 1 + _r(4 * f + 2), T + _r(4 * f), y0=1, etagen=etagen, eh=4, dach="sattel",
                   first_x=False, tuer="west", gauben=False, kamine=1)
    if stall:
        sx = -B - 2 - _r(5 * f + 3)
        stall_st = stil(w, seed, ("holz_dunkel", "holz_hell"))
        P.gebaeude(w, stall_st, sx, -T, -B - 2, T - 1, y0=1, etagen=1, eh=4, dach="sattel", first_x=False,
                   tuer="east", gauben=False, kamine=0)
        heuhaufen(w, sx + 1, T + 2)
    if biergarten:
        for i in range(2 + (g >= 2)):
            x = -B + 2 + i * 5
            z = T + 4
            w.setze(x, 1, z, w.b(f"{st.holz}_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False))
            w.setze(x, 2, z, w.b(f"{st.holz}_pressure_plate", powered=False))
            for dx in (-1, 1):
                w.setze(x + dx, 1, z, w.b(f"{st.holz}_stairs", facing="east" if dx < 0 else "west", half="bottom",
                                          shape="straight", waterlogged=False))
        for x in range(-B, B + 1, 4):
            laternenpfahl(w, x, T + 7, 3, st.holz)
    ziehbrunnen(w, B + 4, T + 4)
    fassstapel(w, B - 3, -T - 2, 4)
    hohl(w, 2)
    return w


def stall(seed, g, pools, b=5, t=3, tiere="pferd", extra=None):
    """Stallgebäude mit großem Tor, Heuboden-Luke, Koppel und Futterplatz."""
    w = _welt(seed)
    f = F[g]
    B, T = _r(b * f, 3), _r(t * f, 2)
    _grund(w, B + 10, T + 6)
    st = stil(w, seed, pools, **(extra or {}))
    P.gebaeude(w, st, -B, -T, B, T, y0=1, etagen=1, eh=5, dach="sattel", tuer="south", gauben=False, kamine=0,
               steil=True)
    for x in (-1, 0, 1):
        for y in range(2, 5):
            w.bloecke.pop((x, y, T), None)
    w.setze(0, 7, T, w.b(f"{st.holz}_trapdoor", facing="south", half="top", open=True, powered=False,
                         waterlogged=False))
    if tiere == "pferd":
        koppel(w, B + 2, -T - 2, B + 2 + _r(10 * f), T + 4, st.holz)
        heuhaufen(w, -B - 3, T + 2)
    elif tiere == "schaf":
        koppel(w, -B - 2 - _r(10 * f), -T - 2, -B - 2, T + 4, st.holz)
        for k in range(3):
            w.setze(B + 2, 1, -T + k * 2, w.b("white_wool"))
    elif tiere == "kuh":
        koppel(w, B + 2, -T, B + 2 + _r(8 * f), T + 6, st.holz)
        misthaufen(w, -B - 3, T + 2)
    elif tiere == "schwein":
        koppel(w, -B - 2 - _r(6 * f), T - 2, -B - 2, T + 6, st.holz, tier_futter=False)
        for x in range(-B - 1 - _r(6 * f), -B - 2):
            for z in range(T - 1, T + 6):
                w.setze(x, 0, z, w.b("mud") if (x + z) % 3 else w.b("coarse_dirt"))
    hohl(w, 2)
    return w


def huette(seed, g, pools, b=3, t=2, art="jaeger", extra=None, grund="wald"):
    """Kleine Hütte im Wald oder auf dem Feld mit typischem Werkplatz."""
    w = _welt(seed)
    f = F[g]
    B, T = _r(b * f, 2), _r(t * f, 2)
    _grund(w, B + 6, T + 6, grund, 0.6)
    st = stil(w, seed, pools, **(extra or {}))
    P.gebaeude(w, st, -B, -T, B, T, y0=1, etagen=1, eh=4, dach="sattel", tuer="south", gauben=False, kamine=1,
               steil=True)
    rng = w.rng
    if art == "jaeger":
        for y in (1, 2, 3):
            w.setze(B + 2, y, 0, zf(w, st.holz))
            w.setze(B + 2, y, 3, zf(w, st.holz))
        for z in range(0, 4):
            w.setze(B + 2, 4, z, w.b(f"{st.holz}_slab", type="bottom", waterlogged=False))
        w.setze(B + 2, 3, 1, w.b("brown_wool"))
        w.setze(B + 2, 3, 2, w.b("orange_wool"))
        holzstapel(w, -B - 2, -T, 3, st.holz, "z")
    elif art == "holzfaeller":
        for k in range(3):
            holzstapel(w, -B - 4 - k, -T + 1, 5, st.holz, "z")
        for k in range(4):
            w.setze(B + 3 + (k % 2) * 2, 1, -2 + k, w.b(f"{st.holz}_log", axis="y"))
        w.setze(B + 3, 2, -2, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
    elif art == "koehler":
        for x, z in scheibe(3.2, B + 6, 0):
            hh = int(2.5 * (1 - math.hypot(x - B - 6, z) / 3.3)) + 1
            for y in range(1, hh + 1):
                w.setze(x, y, z, w.b("coarse_dirt") if y == hh else w.b("coal_block"))
        w.setze(B + 6, 4, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    elif art == "einsiedler":
        for x, z in scheibe(2.0, -B - 4, T + 2):
            w.setze(x, 0, z, w.b("moss_block"))
        w.setze(-B - 4, 1, T + 2, w.b("campfire", lit=False, signal_fire=False, facing="north", waterlogged=False))
        for y in range(1, 4):
            w.setze(B + 3, y, T + 2, w.b("cobblestone_wall", up=True, north="none", south="none", east="none",
                                         west="none", waterlogged=False))
        w.setze(B + 3, 4, T + 2, w.b("lantern", hanging=False, waterlogged=False))
    elif art == "hirte":
        koppel(w, B + 2, -T - 3, B + 2 + _r(8 * f), T + 3, st.holz)
        for k in range(3):
            w.setze(B + 4 + k, 1, 0, w.b("white_wool"))
    elif art == "fischer":
        for x in range(-B - 8, B + 9):
            for z in range(T + 4, T + 10):
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("sand"))
        for z in range(T + 1, T + 8):
            w.setze(0, 1, z, w.b(f"{st.holz}_slab", type="bottom", waterlogged=False))
        for y in (1, 2, 3):
            w.setze(-3, y, T + 2, zf(w, st.holz))
        w.setze(-3, 3, T + 3, w.b("cobweb"))
    elif art == "kraeuter":
        beet(w, B + 2, -T, B + 6, T, "blumen")
        for y in (2, 3):
            w.setze(-B - 1, y, 0, w.b("hanging_roots") if y == 3 else w.b("spore_blossom")) if False else None
    elif art == "imker":
        for k in range(4):
            w.setze(-B - 3, 1, -T + k * 2, w.b("beehive", facing="west", honey_level=k))
        beet(w, B + 2, -T, B + 6, T + 2, "blumen")
    hohl(w, 2)
    return w


def stadthaus(seed, g, pools, b=3, t=5, etagen=3, giebel=True, erker=False, laube=False, eckturm=False,
              extra=None, schmal_hoch=True):
    """Schmales, hohes Stadthaus mit Giebel zur Straße, optionalen Erkern, Laubengang und Eckturm."""
    w = _welt(seed)
    f = F[g]
    B, T = _r(b * f, 2), _r(t * f, 3)
    gelaende(w, max(B, T) + 4, art="wiese", dichte=0.1)
    for x in range(-B - 3, B + 4):
        for z in range(T + 1, T + 5):
            w.setze(x, 0, z, MB.pflaster(w, "cobblestone", "running_bond") if (x + z) % 4 else w.b("cobblestone"))
    st = stil(w, seed, pools, **(extra or {}))
    P.gebaeude(w, st, -B, -T, B, T, y0=1, etagen=etagen + (g >= 2), eh=4, dach="sattel", first_x=not giebel,
               tuer="south", gauben=True, kamine=1, steil=True)
    yt = 1 + 1 + (etagen + (g >= 2)) * 4
    if erker:
        for y in range(6, yt - 1):
            for x in (-1, 0, 1):
                w.setze(x, y, T + 1, w.b("glass_pane", east=True, west=True, north=False, south=False,
                                         waterlogged=False) if x == 0 and y % 4 != 1 else st.wand(x, y, T, 0.5))
        for x in (-1, 0, 1):
            w.setze(x, 5, T + 1, w.b(f"{st.gesims}_stairs" if st.gesims not in ("quartz",) else "quartz_stairs",
                                     facing="north", half="top", shape="straight", waterlogged=False))
    if laube:
        for x in range(-B, B + 1, 2):
            for y in (1, 2, 3):
                w.setze(x, y, T + 3, st.sockel(x, y, T, 0.5))
        for x in range(-B, B + 1):
            for z in range(T + 1, T + 4):
                w.setze(x, 4, z, st.wand(x, 4, z, 0.3))
    if eckturm:
        P.turm(w, st, B, T, 6, _r(8 * f + 4), 1.6, dach="kegel", krone=False, fahne=None, fenster=4)
    hohl(w, 2)
    return w


def amtsbau(seed, g, pools, b=7, t=4, etagen=2, dach="walm", turm=False, portikus=False, hof=None,
            uhr=False, extra=None, schild_farbe=None):
    """Repräsentatives Amts- oder Zunftgebäude: symmetrische Fassade, Freitreppe, ggf. Dachreiter, Portikus."""
    w = _welt(seed)
    f = F[g]
    B, T = _r(b * f, 3), _r(t * f, 3)
    _grund(w, B + 6, T + 6, dichte=0.2)
    st = stil(w, seed, pools, **(extra or {}))
    P.gebaeude(w, st, -B, -T, B, T, y0=1, etagen=etagen, eh=5, dach=dach, tuer="south", gauben=True, kamine=2,
               pilaster=3)
    yt = 1 + 1 + etagen * 5
    if portikus:
        for x in (-3, -1, 1, 3):
            for y in range(1, yt - 1):
                w.setze(x, y, T + 3, w.b("quartz_pillar", axis="y") if st.gesims == "quartz" else st.sockel(x, y, T, 0.6))
        for x in range(-4, 5):
            for z in range(T + 1, T + 4):
                w.setze(x, yt - 1, z, st.wand(x, yt, z, 0.9))
        for k in range(5):
            for x in range(-4 + k, 5 - k):
                w.setze(x, yt + k, T + 3, st.wand(x, yt + k, T + 3, 0.95))
    if turm:
        top = max(y for (x, y, z) in w.bloecke if abs(x) <= 1 and abs(z) <= 1)
        P.turm(w, st, 0, 0, top - 1, _r(6 * f + 4), 1.6, form="achteck", dach="glocke", krone=False, fahne=None,
               fenster=4)
        if uhr:
            from uhrwerk import uhrblatt
            uhrblatt(w, 0, top + 2, 2, 1.5, "south")
    if hof == "brunnen":
        ziehbrunnen(w, 0, T + 7)
    elif hof == "baeume":
        for x in (-B, B):
            obstbaum(w, x, T + 6)
    for x in range(-B, B + 1):
        for z in range(T + 1, T + 9):
            if (x, 0, z) in w.bloecke and abs(x) < 3:
                w.setze(x, 0, z, w.b("stone_bricks") if (x + z) % 2 else w.b("polished_andesite"))
    hohl(w, 2)
    return w


def speicher(seed, g, pools, b=4, t=4, etagen=3, art="korn", extra=None):
    """Speicher/Scheune: hoher Bau mit Ladeluken, Lastenkran am Giebel, Säcken und Fässern."""
    w = _welt(seed)
    f = F[g]
    B, T = _r(b * f, 3), _r(t * f, 3)
    _grund(w, B + 5, T + 5)
    st = stil(w, seed, pools, **(extra or {}))
    if art == "scheune":
        P.gebaeude(w, st, -B - 2, -T, B + 2, T, y0=1, etagen=1, eh=6, dach="sattel", first_x=False, tuer="south",
                   gauben=False, kamine=0, steil=True)
        for x in range(-2, 3):
            for y in range(2, 6):
                w.bloecke.pop((x, y, T), None)
        heuhaufen(w, B + 5, T + 2)
        karren(w, -B - 6, T + 3, st.holz)
    else:
        P.gebaeude(w, st, -B, -T, B, T, y0=1, etagen=etagen, eh=4, dach="sattel", first_x=False, tuer="south",
                   gauben=False, kamine=0, steil=True)
        yt = 2 + etagen * 4
        for y in range(5, yt, 4):
            w.setze(0, y, T, w.b(f"{st.holz}_trapdoor", facing="south", half="bottom", open=True, powered=False,
                                 waterlogged=False))
        for k in range(3):
            w.setze(0, yt + 2, T + k, w.b(f"{st.holz}_log", axis="z"))
        for y in range(yt - 3, yt + 2):
            w.setze(0, y, T + 2, w.b("chain", axis="y", waterlogged=False))
        for k in range(4):
            w.setze(-B + k, 1, T + 2, MB.mod(w, "supplementaries:sack", "white_wool", open=False) if art == "korn"
                    else w.b("barrel", facing="up", open=False))
    hohl(w, 2)
    return w


def winkelhaus(seed, g, pools, b=5, t=3, etagen=2, fluegel=4, hof="garten", extra=None, turm=False):
    """Winkelhaus (L-Form): Haupthaus und Seitenflügel um einen kleinen Hof."""
    w = _welt(seed)
    f = F[g]
    B, T = _r(b * f, 3), _r(t * f, 2)
    L = _r(fluegel * f, 3)
    _grund(w, B + 6, T + L + 4)
    st = stil(w, seed, pools, **(extra or {}))
    P.gebaeude(w, st, -B, -T, B, T, y0=1, etagen=etagen, eh=4, dach="sattel", first_x=True, tuer="south",
               gauben=True, kamine=1)
    P.gebaeude(w, st, B - 2 * T, T + 1, B, T + 1 + 2 * L, y0=1, etagen=etagen, eh=4, dach="sattel",
               first_x=False, tuer="west", gauben=False, kamine=1)
    if turm:
        P.turm(w, st, B + 1, -T - 1, 1, _r((etagen * 4 + 6) * 1.0), 1.8, dach="kegel", krone=False, fahne=None,
               fenster=4)
    if hof == "garten":
        beet(w, -B, T + 3, B - 2 * T - 3, T + 4, "blumen")
        obstbaum(w, -B + 2, T + 2 * L)
    elif hof == "werk":
        holzstapel(w, -B, T + 3, 4)
        karren(w, -B + 1, T + 2 * L - 1)
    elif hof == "brunnen":
        ziehbrunnen(w, (B - 2 * T - B) // 2 - 1, T + L)
    hohl(w, 2)
    return w


def fantasiehaus(seed, g, art="magier"):
    """Fantasiehäuser: Magierturm-Haus, Elfenhaus, Halblingshöhle, Pilzhaus, Druidenhütte, Zwergenhaus,
    Gnomenhaus, Baumstumpfhaus."""
    w = _welt(seed)
    f = F[g]
    rng = w.rng
    if art == "magier":
        _grund(w, 8, 8)
        st = stil(w, seed, "magier", fenster="purple_stained_glass_pane" if False else "glass_pane")
        P.gebaeude(w, st, -_r(4 * f), -_r(3 * f), _r(4 * f), _r(3 * f), y0=1, etagen=2, eh=4, dach="sattel",
                   steil=True, tuer="south", kamine=1)
        P.turm(w, st, _r(4 * f) + 1, -_r(3 * f) - 1, 1, _r(14 * f + 4), 2.0 * f + 0.5, dach="nadel", krone=False,
               fahne=None, fenster=4)
        for i in range(6):
            w.setze(int(rng.integers(-6, 7)), 12 + int(rng.integers(0, 6)), int(rng.integers(-6, 7)),
                    w.b("end_rod", facing="up"))
    elif art == "elfen":
        gelaende(w, _r(10 * f + 4), art="wald", dichte=0.4)
        R = 3 * f + 2
        st = stil(w, seed, "elfen")
        for y in range(1, _r(4 * f + 3)):
            for x, z in kreisrand(R):
                fen = y % 3 == 2 and (abs(x) < 0.6 or abs(z) < 0.6)
                w.setze(x, y, z, w.b("glass_pane", north=True, south=True, east=True, west=True, waterlogged=False)
                        if fen else w.b("birch_planks") if (x + z) % 3 else w.b("stripped_birch_log", axis="y"))
        from wueste_eis import kuppel
        kuppel(w, lambda x, y, z, t: laub(w, "birch") if t > 0.3 else w.b("birch_planks"), 0, 0, _r(4 * f + 3), R + 1,
               form="zwiebel", spitze=None)
        import wald2
        einfuegen(w, wald2.birke(int(rng.integers(1, 10 ** 6)), H=_r(10 * f + 4)), _r(R + 3), 0, 0)
    elif art == "halbling":
        gelaende(w, _r(10 * f + 4), art="wiese", dichte=0.6)
        R = 6 * f + 3
        for x, z in scheibe(R):
            hh = int((1 - (math.hypot(x, z * 1.3) / R) ** 2) * (3 * f + 3))
            for y in range(1, hh + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == hh else w.b("dirt"))
        zf_ = round(R * 0.62)
        for x in range(-3, 4):
            for y in range(1, 5):
                for z in range(zf_ - 4, zf_ + 2):
                    w.bloecke.pop((x, y, z), None)
                w.setze(x, y, zf_ - 3, w.b("green_concrete") if (x / 2.2) ** 2 + ((y - 1.5) / 2.6) ** 2 < 1 else
                        w.b("stripped_oak_log", axis="y") if abs(x) == 3 else w.b("oak_planks"))
        w.setze(0, 2, zf_ - 2, w.b("gold_block") if False else w.b("lantern", hanging=False, waterlogged=False))
        for sx in (-1, 1):
            w.setze(sx * 5, 2, zf_ - 2, w.b("glass_pane", east=True, west=True, north=False, south=False,
                                            waterlogged=False))
        beet(w, -5, zf_ + 2, -2, zf_ + 4, "blumen")
        beet(w, 2, zf_ + 2, 6, zf_ + 4, "gemuese")
        ytop = max(y for (x, y, z) in w.bloecke if abs(x - 2) < 1 and abs(z) < 1)
        for y in range(ytop, ytop + 3):
            w.setze(2, y, 0, w.b("bricks"))
    elif art == "pilz":
        from spuk import pilzhaus
        return pilzhaus(seed, g)
    elif art == "druide":
        gelaende(w, _r(9 * f + 4), art="wald", dichte=0.6)
        R = 2.5 * f + 2
        for y in range(1, 4):
            for x, z in kreisrand(R):
                w.setze(x, y, z, w.b("mossy_cobblestone") if y == 1 else w.b("stripped_oak_log", axis="y")
                        if (x + z) % 2 else w.b("mud_bricks"))
        from spuk import hexenhut
        hexenhut(w, P.Dach(w, "mcw_stroh"), 0, 0, 4, round(R) + 1, _r(R * 2 + 2), knick=0.5)
        for i in range(6):
            a = i / 6 * 2 * math.pi
            x, z = round(math.cos(a) * (R + 5)), round(math.sin(a) * (R + 5))
            for y in range(1, 3 + i % 2):
                w.setze(x, y, z, w.b("mossy_cobblestone"))
    elif art == "zwerg":
        from zwerge import huegelhaus
        return huegelhaus(seed, g)
    elif art == "gnom":
        gelaende(w, _r(7 * f + 3), art="wald", dichte=0.6)
        import wald2
        einfuegen(w, wald2.laubbaum(int(rng.integers(1, 10 ** 6)), "oak", H=_r(10 * f + 4), dick=True), 0, 0, 0)
        for y in (1, 2):
            w.setze(0, y, 2, w.b("oak_door", facing="south", half="lower" if y == 1 else "upper", hinge="left",
                                 open=False, powered=False))
        w.setze(1, 2, 2, w.b("glass_pane", east=True, west=True, north=False, south=False, waterlogged=False))
        w.setze(-1, 3, 2, w.b("lantern", hanging=False, waterlogged=False))
    elif art == "stumpf":
        gelaende(w, _r(8 * f + 4), art="wald", dichte=0.5)
        R = 3 * f + 2
        H = _r(5 * f + 3)
        for y in range(0, H + 1):
            for x, z in kreisrand(R):
                w.setze(x, y, z, w.b("oak_wood", axis="y") if (x + z + y) % 4 else w.b("oak_log", axis="y"))
        for x, z in scheibe(R):
            w.setze(x, H + 1, z, w.b("stripped_oak_wood", axis="y") if math.hypot(x, z) > R - 1 else
                    w.b("moss_block"))
        for y in (1, 2):
            w.bloecke.pop((0, y, round(R)), None)
        w.setze(0, 1, round(R), w.b("oak_door", facing="south", half="lower", hinge="left", open=False, powered=False))
        w.setze(0, 2, round(R), w.b("oak_door", facing="south", half="upper", hinge="left", open=False, powered=False))
        for i in range(5):
            a = i / 5 * 2 * math.pi
            for k in range(1, 4):
                w.setze(round(math.cos(a) * (R + k)), 0 if k > 1 else 1, round(math.sin(a) * (R + k)),
                        w.b("oak_log", axis="x" if abs(math.cos(a)) > 0.7 else "z"))
        w.setze(round(R) - 1, H + 2, 0, w.b("brown_mushroom"))
    hohl(w, 2)
    return w


# ============================================================================ Katalog (80)


def _v(fn, beschreibung, **kw):
    def vorlage(seed, g=1):
        return fn(seed, g, **kw)
    vorlage.__doc__ = beschreibung
    return vorlage


HAEUSER2 = {
    # ---- Wohnhäuser
    "kate": ("Kleine Kate", _v(wohnhaus, "Einfache Kate mit Strohdach, Gemüsegarten und Holzstapel.",
                                pools=("stroh_lehm", "holz_hell"), b=3, t=2, garten="gemuese", deko=("holz",),
                                gauben=False)),
    "bauernhaus": ("Bauernhaus", _v(wohnhaus, "Bauernhaus mit Stallanbau, Misthaufen, Hühnern und Bauerngarten.",
                                     pools=("fachwerk_rot", "stroh_lehm"), b=5, t=3, anbau=("east", 2, 3, 1),
                                     garten="gemuese", deko=("mist", "huehner", "karren"))),
    "dorfhaus_fachwerk": ("Fachwerk-Dorfhaus", _v(wohnhaus, "Zweistöckiges Fachwerkhaus mit auskragendem Obergeschoss "
                                                             "und Blumenbeeten.",
                                                  pools=("fachwerk_weiss", "fachwerk_gruen"), b=4, t=3, etagen=2,
                                                  ueberhang=True, garten="blumen", deko=("bank", "laterne"))),
    "steinhaus": ("Steinhaus", _v(wohnhaus, "Massives Bruchsteinhaus mit Schieferdach, Feldsteinmauer und Obstbäumen.",
                                  pools=("bruchstein", "moos"), b=4, t=3, etagen=2, dach="walm",
                                  garten="blumen", deko=("mauer", "obst"))),
    "doppelhaus": ("Doppelhaus", _v(wohnhaus, "Breites Doppelhaus für zwei Familien mit zwei Kaminen und Wäscheleine.",
                                    pools=("ocker_blau", "fachwerk_rot"), b=7, t=3, etagen=2, kamine=2,
                                    garten="gemuese", deko=("waesche", "bank"))),
    "witwenhaus": ("Häuschen mit Laube", _v(wohnhaus, "Kleines Häuschen mit Laube vor der Tür, Rosenbeet und Bank.",
                                              pools=("putz_blau", "fachwerk_ocker"), b=3, t=3, laube=True,
                                              garten="blumen", deko=("bank",))),
    "eckturmhaus": ("Haus mit Eckturm", _v(wohnhaus, "Wohnhaus mit rundem Eckturm und spitzem Helm, Zaun und Brunnen.",
                                             pools=("kalk_kupfer", "stein_schiefer"), b=4, t=3, etagen=2,
                                             turm=("se", 2.0, 11, "rund"), garten="zaun", deko=("brunnen",))),
    "langhaus": ("Langes Bauernhaus", _v(wohnhaus, "Langgestrecktes Wohnstallhaus unter einem Dach, Heuhaufen und "
                                                    "Koppel.",
                                          pools=("holz_dunkel", "stroh_lehm"), b=8, t=3, etagen=1, steil=True,
                                          deko=("heu", "koppel"), garten=None)),
    "giebelhaus": ("Spitzgiebelhaus", _v(wohnhaus, "Hohes Haus mit sehr steilem Giebel, kleinem Garten und Hundehütte.",
                                          pools=("holz_rot", "holz_blau"), b=3, t=4, etagen=2, steil=True,
                                          first_x=False, garten="blumen", deko=("hund",))),
    "landhaus": ("Landhaus", _v(wohnhaus, "Behäbiges Landhaus mit Walmdach, Anbau, Bienenstöcken und Obstwiese.",
                                pools=("patrizier", "kalk_kupfer"), b=6, t=4, etagen=2, dach="walm",
                                anbau=("west", 2, 3, 1), deko=("bienen", "obst"))),
    "huehnerhof": ("Häuschen mit Hühnerhof", _v(wohnhaus, "Kleines Haus mit eingezäuntem Hühnerhof und Kräuterbeet.",
                                                  pools=("fachwerk_ocker", "stroh_lehm"), b=3, t=3,
                                                  deko=("huehner", "holz"), garten="blumen")),
    "mansardhaus": ("Mansardhaus", _v(wohnhaus, "Bürgerhaus mit Mansarddach, Gauben und gepflegtem Vorgarten.",
                                       pools=("patrizier", "backstein_rot"), b=5, t=4, etagen=2, dach="mansarde",
                                       garten="zaun", deko=("laterne",))),
    "bergbauernhof": ("Bergbauernhaus", _v(wohnhaus, "Bergbauernhaus mit Steinsockel, Holzoberbau, flachem Dach und "
                                                      "Holzlege.",
                                            pools=("holz_dunkel", "holz_hell"), b=5, t=4, etagen=2, sockel_h=2,
                                            deko=("holz", "heu"), garten=None, grund="wiese")),
    "moorkate": ("Moorkate", _v(wohnhaus, "Geduckte Kate aus Lehm und Moosstein mit tiefem Dach, Torfstapel und "
                                           "Brunnen.",
                                pools=("moos", "stroh_lehm"), b=4, t=2, steil=True, deko=("holz", "brunnen"),
                                garten=None, gauben=False)),
    "fischerkate": ("Fischerkate", _v(huette, "Fischerkate am Wasser mit Steg und Netzgestell.",
                                      pools=("holz_blau", "holz_hell"), art="fischer", grund="wiese")),
    # ---- Winkel & Höfe
    "winkelhof": ("Winkelhof", _v(winkelhaus, "Winkelhof mit Wohnhaus und Seitenflügel um einen Gartenhof.",
                                  pools=("fachwerk_rot", "fachwerk_gruen"), b=5, t=3, fluegel=4, hof="garten")),
    "handwerkerhof": ("Handwerkerhof", _v(winkelhaus, "Winkelhof eines Handwerkers mit Holzlager und Karren im Hof.",
                                          pools=("holz_dunkel", "bruchstein"), b=5, t=3, fluegel=4, hof="werk")),
    "turmhof": ("Hof mit Turm", _v(winkelhaus, "Winkelhaus mit Wohnturm an der Ecke und Brunnen im Hof.",
                                   pools=("stein_schiefer", "kalk_kupfer"), b=5, t=3, etagen=2, fluegel=5,
                                   hof="brunnen", turm=True)),
    # ---- Werkstätten
    "tischlerei": ("Tischlerei", _v(werkstatt, "Tischlerei mit offener Werkstatt, Hobelbänken und Bretterstapeln.",
                                    b=5, t=3, etagen=1, dach="sattel", pools=("holz_hell", "fachwerk_ocker"), ausstattung=("crafting_table", "stonecutter",
                                                                                         "crafting_table"),
                                    hof=("holz", "holz"))),
    "boettcherei": ("Böttcherei", _v(werkstatt, "Böttcherei: Fässer in allen Größen, Fassreifen und Dauben.",
                                     b=4, t=4, etagen=2, dach="walm", pools=("fachwerk_rot", "holz_dunkel"), ausstattung=("barrel", "crafting_table",
                                                                                          "barrel"),
                                     hof=("faesser", "faesser"))),
    "seilerei": ("Seilerei", _v(werkstatt, "Seilerei mit langer Seilbahn im Hof, Hanfballen und Haspeln.",
                                b=6, t=2, etagen=1, pools=("stroh_lehm", "holz_hell"), ausstattung=("loom", "crafting_table"),
                                hof=("seil", "heu"))),
    "weberei": ("Weberei", _v(werkstatt, "Weberei mit Webstühlen und bunten Tuchballen.",
                              b=4, t=3, etagen=3, pools=("fachwerk_gruen", "putz_blau"), ausstattung=("loom", "loom", "loom"),
                              hof=("wolle",))),
    "schusterei": ("Schusterei", _v(werkstatt, "Schusterei mit Lederwerkstatt und Trockengestell.",
                                    b=3, t=3, etagen=2, dach="walm", pools=("fachwerk_ocker", "backstein_rot"), ausstattung=("crafting_table", "loom"),
                                    hof=("leder",))),
    "kerzenzieher": ("Kerzenzieherei", _v(werkstatt, "Kerzenzieherei mit Wachskesseln und Kerzenregalen.",
                                          b=3, t=4, etagen=2, pools=("putz_blau", "fachwerk_weiss"), ausstattung=("cauldron", "barrel",
                                                                                               "cauldron"),
                                          hof=("kerzen",), rauch=True)),
    "waffenschmiede": ("Waffenschmiede", _v(werkstatt, "Waffenschmiede mit Esse, Ambossen, Schleifstein und "
                                                      "Waffenständern.",
                                            b=5, t=4, etagen=1, dach="walm", pools=("bruchstein", "tief"), ausstattung=("anvil", "smithing_table",
                                                                                        "grindstone", "blast_furnace"),
                                            hof=("waffen", "holz"), rauch=True)),
    "steinmetzhaus": ("Steinmetzhaus", _v(werkstatt, "Steinmetz mit Steinsägen, Rohblöcken und Werkstücken.",
                                          b=4, t=3, etagen=1, pools=("bruchstein", "kalk_kupfer"), ausstattung=("stonecutter", "stonecutter",
                                                                                             "grindstone"),
                                          hof=("stein", "stein"))),
    "glaserei": ("Glaserei", _v(werkstatt, "Glaserei mit Schmelzofen, bunten Glasplatten und Schaufenstern.",
                                b=4, t=3, etagen=2, dach="mansarde", pools=("kalk_kupfer", "putz_blau"), ausstattung=("blast_furnace", "crafting_table"),
                                hof=("glas",), rauch=True)),
    "toepferhaus": ("Töpferhaus", _v(werkstatt, "Töpferei mit Drehscheiben, Brennofen und Tonlager.",
                                     b=3, t=3, etagen=1, pools=("stroh_lehm", "sand2"), ausstattung=("smoker", "crafting_table"),
                                     hof=("ton", "ton"), rauch=True)),
    "korbflechter": ("Korbflechterei", _v(werkstatt, "Korbflechterei mit Weidenbündeln und Körben aller Art.",
                                          b=3, t=2, etagen=1, pools=("stroh_lehm", "holz_hell"), ausstattung=("crafting_table",),
                                          hof=("korb", "heu"))),
    "pfeilmacher": ("Pfeil- und Bogenmacher", _v(werkstatt, "Pfeilmacher mit Befiederungstisch und Zielscheiben.",
                                                 b=4, t=3, etagen=2, dach="walm", pools=("holz_dunkel", "fachwerk_gruen"),
                                                 ausstattung=("fletching_table", "crafting_table"),
                                                 hof=("holz",))),
    "kartograph": ("Kartographenhaus", _v(werkstatt, "Kartograph mit Kartentischen, Pulten und Globen.",
                                          b=4, t=4, etagen=3, pools=("patrizier", "backstein_rot"), ausstattung=("cartography_table",
                                                                                              "lectern"),
                                          hof=("kisten",))),
    "alchemistenhaus": ("Alchemistenhaus", _v(werkstatt, "Alchemist mit Braustand, Destille und Kräuterkisten.",
                                              b=3, t=3, etagen=3, pools=("magier", "tief"), ausstattung=("brewing_stand", "cauldron",
                                                                                      "brewing_stand"),
                                              hof=("kisten",), rauch=True)),
    "sattlerei": ("Sattlerei", _v(werkstatt, "Sattlerei mit Lederständern, Sätteln und einem Pferdeplatz.",
                                  b=5, t=3, etagen=1, pools=("holz_rot", "fachwerk_ocker"), ausstattung=("loom", "crafting_table"),
                                  hof=("leder", "heu"))),
    "faerberhaus": ("Färberhaus", _v(werkstatt, "Färberei mit Farbbottichen und bunten Tüchern.",
                                     b=4, t=3, etagen=2, pools=("ocker_blau", "fachwerk_rot"), ausstattung=("cauldron", "cauldron",
                                                                                          "barrel"),
                                     hof=("wolle", "faesser"))),
    "schmiede_dorf": ("Hufschmiede", _v(werkstatt, "Hufschmiede mit Esse, Amboss und Hufbeschlagplatz.",
                                        b=4, t=3, etagen=1, dach="walm", pools=("bruchstein", "holz_dunkel"), ausstattung=("anvil", "blast_furnace",
                                                                                          "grindstone"),
                                        hof=("heu", "holz"), rauch=True)),
    "wagnerei": ("Wagnerei", _v(werkstatt, "Wagnerei: Räder, Karren in Arbeit und Holzlager.",
                                b=5, t=4, etagen=1, pools=("holz_hell", "fachwerk_weiss"), ausstattung=("crafting_table", "grindstone"),
                                hof=("karren", "holz"))),
    # ---- Läden
    "metzgerei": ("Metzgerei", _v(laden, "Metzgerei mit rot-weißer Markise und Räucherkammer.",
                                  pools=("fachwerk_rot", "backstein_rot"), markise=("red", "white"),
                                  waren=("smoker", "ware", "fass"))),
    "kaeserei": ("Käseladen", _v(laden, "Käseladen mit gelben Laiben und Fässern.",
                                 pools=("fachwerk_ocker", "putz_blau"), markise=("yellow", "white"),
                                 waren=("yellow_terracotta", "fass", "ware"))),
    "gemuesehandel": ("Gemüsehändler", _v(laden, "Gemüsehändler mit Körben voller Ware.",
                                          pools=("fachwerk_gruen", "holz_hell"), markise=("green", "white"),
                                          waren=("korb", "pumpkin", "korb", "melon"))),
    "apotheke": ("Apotheke", _v(laden, "Apotheke mit grüner Markise, Braustand und Kräutertöpfen.",
                                pools=("patrizier", "kalk_kupfer"), markise=("green", "lime"),
                                waren=("brewing_stand", "flower_pot", "fass"))),
    "buchhandlung": ("Buchhandlung", _v(laden, "Buchhandlung mit Bücherregalen in der Auslage.",
                                        pools=("backstein_rot", "patrizier"), markise=("blue", "white"),
                                        waren=("bookshelf", "lectern", "bookshelf"))),
    "juwelier": ("Juwelier", _v(laden, "Juwelier mit Goldschmiedewerkstatt und Edelsteinen im Fenster.",
                                pools=("kalk_kupfer", "marmor"), markise=("purple", "yellow"),
                                waren=("amethyst_block", "gold_block", "emerald_block"))),
    "baecker_laden": ("Backstube", _v(laden, "Backstube mit braun-weißer Markise und Brotkörben.",
                                      pools=("fachwerk_weiss", "stroh_lehm"), markise=("brown", "white"),
                                      waren=("korb", "hay_block", "korb"))),
    "fischladen": ("Fischladen", _v(laden, "Fischladen mit blauer Markise und Eiskisten.",
                                    pools=("holz_blau", "putz_blau"), markise=("blue", "light_blue"),
                                    waren=("packed_ice", "fass", "packed_ice"))),
    "tuchhandel": ("Tuchhändler", _v(laden, "Tuchhändler mit bunten Stoffballen.",
                                     pools=("ocker_blau", "fachwerk_rot"), markise=("magenta", "white"),
                                     waren=("red_wool", "blue_wool", "yellow_wool", "green_wool"))),
    "spielzeug": ("Spielzeugladen", _v(laden, "Spielzeugmacher mit bunten Holzsachen in der Auslage.",
                                       pools=("fachwerk_gruen", "holz_rot"), markise=("orange", "light_blue"),
                                       waren=("note_block", "jukebox", "ware"))),
    "waffenladen": ("Waffenhändler", _v(laden, "Waffenhändler mit Schwertern, Schilden und Rüstungen.",
                                        pools=("bruchstein", "tief"), markise=("black", "red"),
                                        waren=("iron_block", "fass", "anvil"))),
    "kraemer": ("Krämerladen", _v(laden, "Krämerladen mit allerlei Waren, Säcken und Fässern.",
                                  pools=("holz_hell", "fachwerk_ocker"), markise=("orange", "white"),
                                  waren=("ware", "fass", "korb", "ware"))),
    "weinhandel": ("Weinhändler", _v(laden, "Weinhandlung mit Fassauslage und Weinlaub.",
                                     pools=("sand2", "kalk_kupfer"), markise=("purple", "white"),
                                     waren=("fass", "fass", "ware"))),
    # ---- Gasthöfe
    "gasthof": ("Gasthof", _v(gasthof, "Großer Gasthof mit Stall, Hofbrunnen und Biergarten.",
                              pools=("fachwerk_rot", "fachwerk_weiss"))),
    "wirtshaus": ("Wirtshaus", _v(gasthof, "Dörfliches Wirtshaus ohne Stall, mit großem Biergarten.",
                                  pools=("holz_dunkel", "stroh_lehm"), b=5, t=3, stall=False)),
    "herberge": ("Herberge", _v(gasthof, "Herberge mit Seitenflügel für Gästezimmer und Pferdestall.",
                                pools=("bruchstein", "fachwerk_gruen"), fluegel=True)),
    "rasthaus": ("Rasthaus am Weg", _v(gasthof, "Kleines Rasthaus an der Landstraße mit Stall.",
                                      pools=("holz_hell", "holz_rot"), b=4, t=3, etagen=1, biergarten=False)),
    # ---- Ställe & Speicher
    "pferdestall": ("Pferdestall", _v(stall, "Pferdestall mit Koppel und Heuboden.",
                                      pools=("holz_dunkel", "holz_rot"), tiere="pferd")),
    "schafstall": ("Schafstall", _v(stall, "Schafstall mit Weide und Wollballen.",
                                    pools=("stroh_lehm", "holz_hell"), tiere="schaf")),
    "kuhstall": ("Kuhstall", _v(stall, "Kuhstall mit Weide und Misthaufen.",
                                pools=("fachwerk_rot", "holz_dunkel"), tiere="kuh")),
    "schweinestall": ("Schweinestall", _v(stall, "Schweinekoben mit Suhle.",
                                          pools=("holz_hell", "stroh_lehm"), b=4, tiere="schwein")),
    "kornspeicher": ("Kornspeicher", _v(speicher, "Hoher Kornspeicher mit Ladeluken, Lastenkran und Säcken.",
                                        pools=("fachwerk_ocker", "holz_dunkel"), art="korn")),
    "scheune": ("Scheune", _v(speicher, "Große Scheune mit offenem Tor, Heu und Leiterwagen.",
                              pools=("holz_rot", "holz_dunkel"), art="scheune")),
    "lagerhaus": ("Lagerhaus", _v(speicher, "Städtisches Lagerhaus mit Kran und Fässern.",
                                  pools=("backstein_rot", "bruchstein"), art="lager", etagen=3)),
    # ---- Hütten
    "jaegerhuette": ("Jägerhütte", _v(huette, "Jägerhütte mit Fellgestell und Holzstapel.",
                                      pools=("holz_dunkel", "holz_rot"), art="jaeger")),
    "holzfaellerhuette": ("Holzfällerhütte", _v(huette, "Holzfällerhütte mit Hackklotz und Stammlager.",
                                                pools=("holz_hell", "holz_dunkel"), art="holzfaeller")),
    "koehlerhuette": ("Köhlerhütte", _v(huette, "Köhlerhütte neben einem rauchenden Meiler.",
                                        pools=("holz_dunkel", "stroh_lehm"), art="koehler")),
    "einsiedelei": ("Einsiedelei", _v(huette, "Einsiedlerklause mit Feuerstelle und Laternenstein.",
                                      pools=("moos", "bruchstein"), art="einsiedler")),
    "hirtenhuette": ("Hirtenhütte", _v(huette, "Hirtenhütte am Pferch.",
                                       pools=("stroh_lehm", "holz_hell"), art="hirte", grund="wiese")),
    "kraeuterhuette": ("Kräuterhütte", _v(huette, "Kräuterfrau-Hütte mit Blumen- und Kräuterbeeten.",
                                         pools=("moos", "fachwerk_gruen"), art="kraeuter", grund="wiese")),
    "imkerhuette": ("Imkerhütte", _v(huette, "Imkerhütte mit Bienenstöcken und Blumenwiese.",
                                     pools=("holz_hell", "stroh_lehm"), art="imker", grund="wiese")),
    # ---- Stadthäuser
    "giebelstadthaus": ("Giebel-Stadthaus", _v(stadthaus, "Schmales Stadthaus mit Giebel zur Straße.",
                                               pools=("fachwerk_weiss", "backstein_rot"))),
    "erkerhaus": ("Erkerhaus", _v(stadthaus, "Stadthaus mit durchgehendem Erker über der Tür.",
                                  pools=("patrizier", "ocker_blau"), erker=True)),
    "laubenhaus": ("Laubenhaus", _v(stadthaus, "Stadthaus mit Laubengang über dem Gehweg.",
                                    pools=("kalk_kupfer", "fachwerk_rot"), laube=True, b=4)),
    "eckhaus": ("Eckhaus mit Türmchen", _v(stadthaus, "Stadthaus mit Eckturm und Spitzhelm.",
                                           pools=("backstein_rot", "patrizier"), eckturm=True, b=4)),
    "kaufmannsturm": ("Kaufmannsturm", _v(stadthaus, "Sehr schmales, hohes Turmhaus eines reichen Kaufmanns.",
                                          pools=("bruchstein", "kalk_kupfer"), b=3, t=3, etagen=5)),
    # ---- Amts- und Zunftbauten
    "zunfthaus": ("Zunfthaus", _v(amtsbau, "Prächtiges Zunfthaus mit Pilastern und Dachreiter.",
                                  pools=("patrizier", "backstein_rot"), turm=True)),
    "zollhaus": ("Zollhaus", _v(amtsbau, "Zollhaus mit Schlagbaum-Hof und Brunnen.",
                                pools=("bruchstein", "kalk_kupfer"), b=5, t=4, hof="brunnen")),
    "pfarrhaus": ("Pfarrhaus", _v(amtsbau, "Pfarrhaus mit Walmdach und Obstbäumen.",
                                  pools=("kalk_kupfer", "fachwerk_weiss"), b=5, t=4, hof="baeume")),
    "schule": ("Dorfschule", _v(amtsbau, "Dorfschule mit Glockentürmchen.",
                                pools=("backstein_rot", "putz_blau"), b=6, t=3, turm=True)),
    "stadtwaage": ("Stadtwaage", _v(amtsbau, "Stadtwaage mit Säulenvorhalle.",
                                    pools=("marmor", "patrizier"), b=5, t=4, portikus=True, extra={"gesims": "quartz"})),
    "amtshaus": ("Amtshaus mit Uhr", _v(amtsbau, "Amtshaus mit Uhrtürmchen.",
                                        pools=("patrizier", "bruchstein"), turm=True, uhr=True)),
    "badehaus": ("Badehaus", _v(amtsbau, "Badehaus mit Kuppeldach-Reiter und Brunnen.",
                                pools=("kalk_kupfer", "sand2"), b=5, t=4, etagen=1, turm=True, hof="brunnen")),
    "hospital": ("Hospital", _v(amtsbau, "Hospital mit langem Flügel und Säulenvorhalle.",
                                pools=("kalk_kupfer", "marmor"), b=8, t=4, portikus=True, extra={"gesims": "quartz"})),
    # ---- Fantasie
    "magierhaus": ("Magierhaus", _v(fantasiehaus, "Magierhaus mit Nadelturm und schwebenden Lichtern.",
                                    art="magier")),
    "elfenhaus": ("Elfenhaus", _v(fantasiehaus, "Rundes Elfenhaus aus Birkenholz mit Laubkuppel.", art="elfen")),
    "halblingshoehle": ("Halblingshöhle", _v(fantasiehaus, "Höhlenhaus im Hügel mit runder grüner Tür und Gärten.",
                                             art="halbling")),
    "druidenhuette": ("Druidenhütte", _v(fantasiehaus, "Runde Druidenhütte mit Strohhut-Dach und Steinkreis.",
                                         art="druide")),
    "gnomenbaum": ("Gnomenbaum", _v(fantasiehaus, "Gnomenwohnung im Fuß einer alten Eiche.", art="gnom")),
    "stumpfhaus": ("Baumstumpfhaus", _v(fantasiehaus, "Haus in einem riesigen hohlen Baumstumpf.", art="stumpf")),
}

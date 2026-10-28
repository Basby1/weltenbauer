"""Häuser – Paket: Fachwerkhaus, Turmhaus, Bauernhof, Taverne, Stadtvilla, Pfahlhaus, Blockhütte,
Gildenhaus mit Treppengiebel, Reihenhäuser, Reetdachkate. Größen klein → gigantisch (mehr Etagen,
größere Grundrisse, Nebengebäude), zwei Stile je Typ."""

from __future__ import annotations

import math

from bau import (Stil, garten, kamin, kasten_haus, satteldach, treppengiebel, turm_rund, walmdach, wiese,
                 zaun_rechteck)
from lib import Verlauf, Welt, laub
from skulptur import Skulptur, ell, platte, scheibe, verbinde

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _putz(w, s):
    if s == 0:
        return Stil(w, Verlauf(w, "Putz", ["white_terracotta", "calcite", "smooth_quartz"]), holz="dark_oak",
                    dach="brick", dach_voll="bricks", sockel="cobblestone")
    return Stil(w, Verlauf(w, "Ocker", ["yellow_terracotta", "smooth_sandstone", "cut_sandstone"]), holz="spruce",
                dach="deepslate_tile", dach_voll="deepslate_tiles", sockel="stone_bricks")


def _baum(w, x, z, u, art="oak"):
    h = _r(4 * u + 1, 3)
    for y in range(1, h + 1):
        w.setze(x, y, z, w.b(f"{art}_log", axis="y"))
    S = Skulptur(w, max(0.8, u))
    blaetter = [laub(w, art), laub(w, art), laub(w, "azalea")]
    S.mat("l", lambda *a: blaetter[int(w.rng.integers(3))])
    S.plus(ell(0, 0, 0, 2.6, 2.0, 2.6), "l")
    S.rendern((-3, -3, -3), (3, 3, 3), versatz=(x + 0.5, h + 1.2, z + 0.5), ueberschreiben=False)


# ============================================================================ Typen

def fachwerkhaus(seed, g=1):
    """Fachwerkhaus mit vorkragenden Obergeschossen, Satteldach, Kamin, Blumenkästen und Vorgarten."""
    w = _welt(seed)
    st = _putz(w, _stil(seed))
    bx, bz = [6, 8, 10, 14][g], [5, 6, 8, 10][g]
    et = [1, 2, 3, 4][g]
    wiese(w, max(bx, bz) + 6, w.rng)
    x0, z0 = -bx // 2, -bz // 2
    yt, a, b, c, d = kasten_haus(w, st, x0, z0, x0 + bx, z0 + bz, 0, et, eh=4, jetty=et > 1)
    top = satteldach(w, st, a, b, c, d, yt)
    kamin(w, c - 1, b + 1, yt, top + 1)
    zaun_rechteck(w, x0 - 2, z0 + bz + 2, x0 + bx + 2, z0 + bz + 5, 1, f"{st.holz}_fence",
                  luecke={((x0 * 2 + bx) // 2, z0 + bz + 5)})
    garten(w, x0 - 1, z0 + bz + 3, x0 + bx + 1, z0 + bz + 4, w.rng)
    for z in range(z0 + bz + 1, z0 + bz + 6):
        w.setze((x0 * 2 + bx) // 2, 0, z, w.b("dirt_path"))
    if g >= 2:
        _baum(w, x0 - 4, z0, U[g] * 0.8)
    return w


def turmhaus(seed, g=1):
    """Haus mit rundem Eckturm, Kegeldach, Satteldach und Wetterfahne."""
    w = _welt(seed)
    st = _putz(w, _stil(seed))
    u = U[g]
    bx, bz = [6, 9, 12, 16][g], [5, 7, 9, 12][g]
    et = [1, 2, 2, 3][g]
    wiese(w, max(bx, bz) + 7, w.rng)
    x0, z0 = -bx // 2, -bz // 2
    yt, a, b, c, d = kasten_haus(w, st, x0, z0, x0 + bx, z0 + bz, 0, et, eh=4)
    satteldach(w, st, a, b, c, d, yt)
    R = 1.6 * u + 1.2
    turm_rund(w, st, x0 + bx, z0 + bz, 1, R, yt + _r(4 * u, 3), dach_mat=st.dach_voll)
    kamin(w, x0 + 1, z0 + 1, yt, yt + _r(4 * u, 3))
    return w


def bauernhof(seed, g=1):
    """Bauernhof: Wohnhaus, große Scheune mit Walmdach, Feld mit Feldfrüchten, Heuballen, Brunnen und Zaun."""
    w = _welt(seed)
    s = _stil(seed)
    st = _putz(w, s)
    u = U[g]
    R = _r(16 * u + 8, 12)
    wiese(w, R, w.rng)
    hx, hz = [5, 7, 9, 12][g], [4, 6, 7, 9][g]
    yt, a, b, c, d = kasten_haus(w, st, -R // 2, -R // 2, -R // 2 + hx, -R // 2 + hz, 0, 1 + (g >= 2), eh=4)
    satteldach(w, st, a, b, c, d, yt)
    scheune = Stil(w, Verlauf(w, "Scheune", ["red_terracotta", "red_concrete", "red_terracotta"] if s == 0
                              else ["dark_oak_planks", "spruce_planks", "dark_oak_planks"]),
                   holz="spruce" if s == 0 else "dark_oak", dach="dark_oak" if s == 0 else "spruce",
                   sockel="cobblestone", fachwerk=s == 0)
    sx0, sz0 = 2, -R // 2
    sb, st_ = [6, 9, 12, 16][g], [5, 7, 9, 12][g]
    yt2, a, b, c, d = kasten_haus(w, scheune, sx0, sz0, sx0 + sb, sz0 + st_, 0, 1, eh=_r(5 * u, 4),
                                  fenster_abstand=4, tuer_seite="south", blumen=False)
    walmdach(w, scheune, a, b, c, d, yt2)
    for k in range(3):
        w.setze(sx0 + sb + 2, 1, sz0 + 1 + k, w.b("hay_block", axis="z"))
    w.setze(sx0 + sb + 2, 2, sz0 + 2, w.b("hay_block", axis="x"))
    fx0, fz0 = -R // 2, 2
    fx1, fz1 = R // 2 - 2, R // 2 - 2
    frucht = ["wheat", "carrots", "potatoes", "beetroots"]
    for x in range(fx0 + 1, fx1):
        for z in range(fz0 + 1, fz1):
            if (x - fx0) % 5 == 0:
                w.setze(x, 0, z, w.b("water", level=0))
            else:
                w.setze(x, 0, z, w.b("farmland", moisture=7))
                f = frucht[((x - fx0) // 5) % len(frucht)]
                w.setze(x, 1, z, w.b(f, age=3 if f == "beetroots" else 7))
    zaun_rechteck(w, fx0, fz0, fx1, fz1, 1, f"{st.holz}_fence", luecke={(fx0 + 2, fz0)})
    # Brunnen
    bxw, bzw = -R // 2 + hx + 3, -2
    for x in range(bxw - 1, bxw + 2):
        for z in range(bzw - 1, bzw + 2):
            w.setze(x, 0, z, w.b("water", level=0) if (x, z) == (bxw, bzw) else w.b("cobblestone"))
            if (x, z) != (bxw, bzw):
                w.setze(x, 1, z, w.b("cobblestone_wall", up=True, north="none", south="none", east="none",
                                     west="none", waterlogged=False))
    for x in (bxw - 1, bxw + 1):
        w.setze(x, 2, bzw, w.b(f"{st.holz}_fence", north=False, south=False, east=False, west=False,
                               waterlogged=False))
    for x in range(bxw - 1, bxw + 2):
        w.setze(x, 3, bzw, platte(w, st.holz))
    return w


def taverne(seed, g=1):
    """Taverne: breites Gasthaus mit Galerie, Wirtshausschild, Bänken, Fässern und Stall mit Heu."""
    w = _welt(seed)
    st = _putz(w, _stil(seed))
    u = U[g]
    bx, bz = [8, 11, 15, 20][g], [6, 8, 10, 13][g]
    et = [2, 2, 3, 4][g]
    wiese(w, max(bx, bz) + 8, w.rng)
    x0, z0 = -bx // 2, -bz // 2
    yt, a, b, c, d = kasten_haus(w, st, x0, z0, x0 + bx, z0 + bz, 0, et, eh=4, jetty=True)
    top = satteldach(w, st, a, b, c, d, yt)
    kamin(w, a + 1, b + 1, yt, top + 1, "stone_bricks")
    kamin(w, c - 1, d - 1, yt, top, "stone_bricks")
    # Galerie vor der ersten Etage
    yg = 4
    zg = z0 + bz + 1
    for x in range(x0, x0 + bx + 1):
        w.setze(x, yg, zg, platte(w, st.holz, "top"))
        w.setze(x, yg, zg + 1, platte(w, st.holz, "top"))
    verbinde(w, [(x, yg + 1, zg + 1) for x in range(x0, x0 + bx + 1)], f"{st.holz}_fence")
    for x in range(x0, x0 + bx + 1, 3):
        for y in range(1, yg):
            w.setze(x, y, zg + 1, w.b(f"{st.holz}_fence", north=False, south=False, east=False, west=False,
                                      waterlogged=False))
    # Wirtshausschild
    sx = x0 + bx + 1
    w.setze(sx, 4, zg - 1, w.b(f"{st.holz}_fence", north=False, south=False, east=False, west=True, waterlogged=False))
    w.setze(sx + 1, 4, zg - 1, w.b(f"{st.holz}_fence", north=False, south=False, east=False, west=True,
                                   waterlogged=False))
    w.setze(sx + 1, 3, zg - 1, w.b("chain", axis="y", waterlogged=False))
    w.setze(sx + 1, 2, zg - 1, w.b("barrel", facing="east", open=False))
    # Bänke und Fässer
    for x in range(x0 + 1, x0 + bx, 4):
        w.setze(x, 1, zg + 3, w.b(f"{st.holz}_stairs", facing="north", half="bottom", shape="straight",
                                  waterlogged=False))
        w.setze(x + 1, 1, zg + 3, w.b(f"{st.holz}_fence", north=False, south=False, east=False, west=False,
                                      waterlogged=False))
        w.setze(x + 1, 2, zg + 3, w.b(f"{st.holz}_pressure_plate", powered=False))
    for z in range(z0, z0 + 3):
        w.setze(x0 - 2, 1, z, w.b("barrel", facing="up", open=False))
    # Stall
    sx0 = x0 - _r(6 * u + 2, 5)
    for x in range(sx0, x0 - 1):
        for z in range(z0, z0 + bz):
            w.setze(x, 0, z, w.b("coarse_dirt"))
            if x == sx0 or z == z0:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b(f"{st.holz}_fence", north=False, south=False, east=False, west=False,
                                         waterlogged=False) if (x + z) % 2 else w.b(st.balken, axis="y"))
            w.setze(x, 4, z, platte(w, st.holz))
        if x % 2:
            w.setze(x, 1, z0 + 1, w.b("hay_block", axis="y"))
    return w


def stadtvilla(seed, g=1):
    """Symmetrische Stadtvilla aus Stein: Mittelbau mit Mansarddach und Gauben, zwei Flügel, Säulenportikus,
    Freitreppe, Laternen und Ziergarten."""
    w = _welt(seed)
    s = _stil(seed)
    st = Stil(w, Verlauf(w, "Villa", ["polished_andesite", "stone_bricks", "polished_andesite"] if s == 0
                         else ["smooth_quartz", "quartz_bricks", "calcite"]), holz="dark_oak",
              dach="deepslate_tile" if s == 0 else "dark_prismarine", dach_voll="deepslate_tiles" if s == 0
              else "dark_prismarine", sockel="polished_deepslate" if s == 0 else "stone_bricks", fachwerk=False,
              glas="glass_pane")
    bx, bz = [8, 12, 16, 22][g], [6, 8, 10, 13][g]
    et = [1, 2, 3, 3][g]
    fl = [0, 4, 6, 8][g]
    wiese(w, bx // 2 + fl + 10, w.rng)
    x0, z0 = -bx // 2, -bz // 2
    yt, a, b, c, d = kasten_haus(w, st, x0, z0, x0 + bx, z0 + bz, 0, et, eh=5, fenster_abstand=2)
    walmdach(w, st, a, b, c, d, yt, ue=1, steil=2)
    for sgn in (-1, 1):
        if fl:
            fx0 = x0 - fl if sgn < 0 else x0 + bx
            yt2, a2, b2, c2, d2 = kasten_haus(w, st, fx0, z0 + 1, fx0 + fl, z0 + bz - 1, 0, max(1, et - 1), eh=5,
                                              fenster_abstand=2, tuer_seite="south", laternen=False)
            walmdach(w, st, a2, b2, c2, d2, yt2, ue=1)
    # Portikus mit Säulen und Freitreppe
    pz = z0 + bz + 1
    ph = 5 * min(et, 2)
    for x in range(-2, 3, 2):
        for y in range(1, ph):
            w.setze(x, y, pz + 2, w.b("quartz_pillar", axis="y"))
    for x in range(-3, 4):
        for z in range(pz, pz + 3):
            w.setze(x, ph, z, w.b("smooth_quartz"))
            w.setze(x, 0, z, w.b("polished_andesite"))
        w.setze(x, ph + 1, pz + 2, platte(w, "smooth_quartz"))
    for k in range(2):
        for x in range(-3, 4):
            w.setze(x, 0, pz + 3 + k, w.b("stone_brick_stairs", facing="north", half="bottom", shape="straight",
                                          waterlogged=False))
    for x in (-5, 5):
        w.setze(x, 1, pz + 3, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                                  waterlogged=False))
        w.setze(x, 2, pz + 3, w.b("lantern", hanging=False, waterlogged=False))
    for x in range(-bx // 2 - fl, bx // 2 + fl + 1):
        if abs(x) > 3 and x % 2 == 0:
            w.setze(x, 1, pz + 1, w.b("flowering_azalea_leaves", persistent=True, distance=7, waterlogged=False))
    return w


def pfahlhaus(seed, g=1):
    """Pfahlhaus über dem Wasser: Stelzen, umlaufende Veranda mit Geländer, Leiter, Steg und Laternen."""
    w = _welt(seed)
    s = _stil(seed)
    st = Stil(w, Verlauf(w, "Holz", ["spruce_planks", "stripped_spruce_log", "spruce_planks"] if s == 0
                         else ["bamboo_planks", "birch_planks", "bamboo_planks"]),
              holz="spruce" if s == 0 else "birch", dach="spruce" if s == 0 else "jungle",
              sockel="spruce_planks" if s == 0 else "birch_planks", fachwerk=False)
    bx, bz = [5, 7, 10, 14][g], [4, 6, 8, 11][g]
    hs = [3, 4, 5, 6][g]
    R = max(bx, bz) + 6
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("water", level=0))
    for x, z in scheibe(R + 1):
        w.setze(x, -1, z, w.b("sand"), ueberschreiben=False)
    x0, z0 = -bx // 2, -bz // 2
    for x in range(x0 - 2, x0 + bx + 3, 2):
        for z in range(z0 - 2, z0 + bz + 3, 2):
            if x in (x0 - 2, x0 + bx + 2) or z in (z0 - 2, z0 + bz + 2) or (x % 4 == 0 and z % 4 == 0):
                for y in range(-1, hs):
                    w.setze(x, y, z, w.b(f"stripped_{st.holz}_log", axis="y"))
    for x in range(x0 - 2, x0 + bx + 3):
        for z in range(z0 - 2, z0 + bz + 3):
            w.setze(x, hs, z, w.b(f"{st.holz}_planks"))
    verbinde(w, [(x, hs + 1, z) for x in range(x0 - 2, x0 + bx + 3) for z in range(z0 - 2, z0 + bz + 3)
                 if (x in (x0 - 2, x0 + bx + 2) or z in (z0 - 2, z0 + bz + 2)) and not (x == x0 + bx // 2 and z == z0 + bz + 2)],
             f"{st.holz}_fence")
    yt, a, b, c, d = kasten_haus(w, st, x0, z0, x0 + bx, z0 + bz, hs, 1 + (g >= 3), eh=4, blumen=False)
    satteldach(w, st, a, b, c, d, yt, ue=2)
    xl = x0 + bx // 2
    for y in range(0, hs + 1):
        w.setze(xl, y, z0 + bz + 3, w.b("ladder", facing="south", waterlogged=False))
    for z in range(z0 + bz + 3, R + 1):
        w.setze(xl, 0, z, w.b(f"{st.holz}_planks"))
        w.setze(xl + 1, 0, z, w.b(f"{st.holz}_planks"))
    w.setze(xl - 1, hs + 1, z0 + bz + 2, w.b("lantern", hanging=False, waterlogged=False))
    return w


def blockhuette(seed, g=1):
    """Blockhütte aus liegenden Stämmen mit Steinkamin, Veranda, Holzstapel und Axt-Block."""
    w = _welt(seed)
    s = _stil(seed)
    holz = "spruce" if s == 0 else "oak"
    bx, bz = [5, 7, 9, 12][g], [4, 6, 7, 9][g]
    wiese(w, max(bx, bz) + 6, w.rng, gras="grass_block" if s == 0 else "podzol")
    st = Stil(w, Verlauf(w, "Stämme", [f"{holz}_log"]), holz=holz, dach=holz, sockel="cobblestone", fachwerk=False)
    x0, z0 = -bx // 2, -bz // 2
    eh = 4 + (g >= 2)
    yt, a, b, c, d = kasten_haus(w, st, x0, z0, x0 + bx, z0 + bz, 0, 1 + (g >= 3), eh=eh, blumen=False)
    for (x, y, z), blk in list(w.bloecke.items()):
        if w.P.name(blk) == f"minecraft:{holz}_log" and y > 0:
            w.setze(x, y, z, w.b(f"{holz}_log", axis="x" if z in (b, d) else "z"))
    top = satteldach(w, st, a, b, c, d, yt, ue=1)
    for y in range(1, top + 2):
        w.setze(c + 1, y, (b + d) // 2, w.b("cobblestone" if y % 3 else "mossy_cobblestone"))
    w.setze(c + 1, top + 2, (b + d) // 2, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                              waterlogged=False))
    for x in range(a, c + 1):
        for z in (d + 1, d + 2):
            w.setze(x, 0, z, w.b(f"{holz}_planks"))
        w.setze(x, eh, d + 2, platte(w, holz))
        w.setze(x, eh, d + 1, platte(w, holz))
    for x in (a, c):
        for y in range(1, eh):
            w.setze(x, y, d + 2, w.b(f"{holz}_fence", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
    for k in range(3):
        for y in range(1, 3):
            w.setze(a - 2, y, b + k, w.b(f"{holz}_log", axis="x"))
    return w


def gildenhaus(seed, g=1):
    """Schmales, hohes Kaufmanns- und Gildenhaus mit Treppengiebel zur Straße, Kranbalken und Wappen."""
    w = _welt(seed)
    s = _stil(seed)
    st = Stil(w, Verlauf(w, "Backstein", ["bricks", "bricks", "red_terracotta"] if s == 0
                         else ["stone_bricks", "polished_andesite", "stone_bricks"]),
              holz="dark_oak" if s == 0 else "spruce", dach="deepslate_tile", dach_voll="deepslate_tiles",
              sockel="stone_bricks", fachwerk=False)
    bx, bz = [5, 7, 9, 11][g], [7, 9, 12, 15][g]
    et = [2, 3, 4, 5][g]
    wiese(w, bz // 2 + 6, w.rng)
    x0, z0 = -bx // 2, -bz // 2
    yt, a, b, c, d = kasten_haus(w, st, x0, z0, x0 + bx, z0 + bz, 0, et, eh=4, fenster_abstand=2)
    satteldach(w, st, a, b, c, d, yt, ue=0, first_x=False, giebelfenster=False)
    treppengiebel(w, st, a, d, c, yt, (c - a) // 2 + 2, "bricks" if s == 0 else "stone_bricks")
    treppengiebel(w, st, a, b, c, yt, (c - a) // 2 + 2, "bricks" if s == 0 else "stone_bricks")
    w.setze((a + c) // 2, yt + 1, d + 1, w.b(f"{st.holz}_fence", north=True, south=False, east=False, west=False,
                                             waterlogged=False))
    w.setze((a + c) // 2, yt + 1, d + 2, w.b(f"{st.holz}_fence", north=True, south=False, east=False, west=False,
                                             waterlogged=False))
    w.setze((a + c) // 2, yt, d + 2, w.b("chain", axis="y", waterlogged=False))
    w.setze((a + c) // 2, 5, d + 1, w.b("gold_block"))
    return w


def reihenhaeuser(seed, g=1):
    """Bunte Reihenhäuser mit unterschiedlichen Höhen, Giebeln und Farben."""
    w = _welt(seed)
    s = _stil(seed)
    farben = ["red_terracotta", "blue_terracotta", "yellow_terracotta", "white_terracotta", "green_terracotta",
              "orange_terracotta", "cyan_terracotta"] if s == 0 else \
        ["bricks", "mud_bricks", "stone_bricks", "polished_granite", "deepslate_bricks", "bricks"]
    anzahl = [3, 4, 6, 8][g]
    bx, bz = 5, [6, 8, 9, 10][g]
    x = -(anzahl * (bx + 1)) // 2
    wiese(w, anzahl * (bx + 1) // 2 + 5, w.rng)
    for i in range(anzahl):
        st = Stil(w, Verlauf(w, farben[i % len(farben)], [farben[i % len(farben)]]), holz="dark_oak",
                  dach="deepslate_tile" if i % 2 else "brick", dach_voll="deepslate_tiles" if i % 2 else "bricks",
                  sockel="stone_bricks", fachwerk=False)
        et = 2 + (i * 7 + g) % 3 + (g >= 2)
        yt, a, b, c, d = kasten_haus(w, st, x, -bz // 2, x + bx, bz // 2, 0, et, eh=4, fenster_abstand=2)
        satteldach(w, st, a, b, c, d, yt, ue=0, first_x=False, giebelfenster=True)
        x += bx + 1
    return w


def reetdachkate(seed, g=1):
    """Weiße Kate mit dickem Reetdach (Walm), Sprossenfenstern, Bauerngarten und Obstbaum."""
    w = _welt(seed)
    s = _stil(seed)
    st = Stil(w, Verlauf(w, "Kalk", ["white_concrete", "calcite", "white_terracotta"] if s == 0
                         else ["mud_bricks", "packed_mud", "mud_bricks"]), holz="oak", dach=None,
              dach_voll="hay_block", sockel="cobblestone", fachwerk=s == 0)
    bx, bz = [6, 9, 12, 16][g], [5, 6, 8, 10][g]
    wiese(w, max(bx, bz) + 7, w.rng)
    x0, z0 = -bx // 2, -bz // 2
    yt, a, b, c, d = kasten_haus(w, st, x0, z0, x0 + bx, z0 + bz, 0, 1 + (g >= 3), eh=4)
    walmdach(w, st, a, b, c, d, yt, ue=1)
    zaun_rechteck(w, x0 - 1, z0 + bz + 2, x0 + bx + 1, z0 + bz + 6, 1, "oak_fence",
                  luecke={((x0 * 2 + bx) // 2, z0 + bz + 6)})
    garten(w, x0, z0 + bz + 3, x0 + bx, z0 + bz + 5, w.rng, ("poppy", "cornflower", "allium", "rose_bush" if False else "dandelion"))
    _baum(w, x0 + bx + 4, z0 + 1, U[g] * 0.8, "oak")
    return w


HAEUSER = {
    "fachwerkhaus": ("Fachwerkhaus", fachwerkhaus),
    "turmhaus": ("Turmhaus", turmhaus),
    "bauernhof": ("Bauernhof", bauernhof),
    "taverne": ("Taverne", taverne),
    "stadtvilla": ("Stadtvilla", stadtvilla),
    "pfahlhaus": ("Pfahlhaus", pfahlhaus),
    "blockhuette": ("Blockhütte", blockhuette),
    "gildenhaus": ("Gildenhaus", gildenhaus),
    "reihenhaeuser": ("Reihenhäuser", reihenhaeuser),
    "reetdachkate": ("Reetdachkate", reetdachkate),
}

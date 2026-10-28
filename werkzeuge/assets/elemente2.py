"""Nether-Reich und End-Reich (neu) – je 20 Bauten."""

from __future__ import annotations

import math

import numpy as np

import modbloecke as MB
import pracht as P
from lib import Rauschen, Verlauf, einfuegen, laub, zerfall
from pracht import Mat, gelaende, treppe
from skulptur import Skulptur, dreh_x, dreh_y, dreh_z, ell, kap, kreisrand, ohne, scheibe, spiegel_x, torus, zur_mitte
from weltwunder import bl, hohl, platz, schwebende_splitter, sk
from wueste_eis import kuppel

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


# ============================================================================ NETHER


def netherboden(w, R, cx=0, cz=0, art="crimson"):
    """Netherboden: Netherrack, Nylium, Seelensand, Basalt-Flecken mit Pilzen, Wurzeln und Wurmfeuer."""
    r1 = Rauschen(w, 4)
    r2 = Rauschen(w, 1.6)
    rng = w.rng
    for x, z in scheibe(R, cx, cz):
        if not w.frei(x, 0, z):
            continue
        v = r1(x, 0, z) * 0.7 + r2(x, 0, z) * 0.3
        if art == "crimson":
            b = "crimson_nylium" if v < 0.45 else "netherrack" if v < 0.7 else "nether_wart_block" if v < 0.8 else "netherrack"
        elif art == "warped":
            b = "warped_nylium" if v < 0.45 else "netherrack" if v < 0.7 else "warped_wart_block" if v < 0.8 else "netherrack"
        elif art == "seele":
            b = "soul_sand" if v < 0.4 else "soul_soil" if v < 0.75 else "bone_block" if v < 0.8 else "basalt"
        else:
            b = "blackstone" if v < 0.35 else "basalt" if v < 0.6 else "netherrack" if v < 0.85 else "magma_block"
        w.setze(x, 0, z, w.b(b, axis="y") if b in ("basalt", "bone_block") else w.b(b))
        if w.frei(x, 1, z):
            q = rng.random()
            if b == "crimson_nylium" and q < 0.15:
                w.setze(x, 1, z, w.b("crimson_roots" if q < 0.1 else "crimson_fungus"))
            elif b == "warped_nylium" and q < 0.15:
                w.setze(x, 1, z, w.b("warped_roots" if q < 0.08 else "nether_sprouts" if q < 0.12 else "warped_fungus"))
            elif b in ("soul_sand", "soul_soil") and q < 0.03:
                w.setze(x, 1, z, w.b("soul_fire"))
            elif b == "netherrack" and q < 0.01:
                w.setze(x, 1, z, w.b("fire", age=0, north=False, south=False, east=False, west=False, up=False))


def _nb(w, seed):
    if _stil(seed) == 0:
        return dict(M=Mat(w, "netherziegel"), R=Mat(w, ["red_nether_bricks", "nether_wart_block", "red_nether_bricks",
                                                         "crimson_planks", "red_nether_bricks"]),
                    tr="nether_brick", tr2="red_nether_brick", holz="crimson", licht="shroomlight", feuer="campfire",
                    glas="red_stained_glass", boden="crimson", seele=False)
    return dict(M=Mat(w, "schwarzstein"), R=Mat(w, ["warped_wart_block", "warped_planks", "prismarine_bricks",
                                                     "warped_wart_block"]),
                tr="polished_blackstone_brick", tr2="polished_blackstone", holz="warped", licht="soul_lantern",
                feuer="soul_campfire", glas="cyan_stained_glass", boden="warped", seele=True)


def netherfestung(seed, g=2):
    """Netherfestung: Netherziegel-Bastion mit Bogenbrücken auf hohen Pfeilern, Wehrgängen, Netherwarzen-Höfen
    und Lohenspawner-Plattform (ohne Spawner)."""
    w = _welt(seed)
    d = _nb(w, seed)
    u = U[g]
    L = _r(20 * u + 8)
    H = _r(10 * u + 5, 7)
    netherboden(w, L + 4, art=d["boden"])
    for achse in ("x", "z"):
        for k in range(-L, L + 1):
            for q in range(-2, 3):
                x, z = (k, q) if achse == "x" else (q, k)
                w.setze(x, H, z, d["M"](x, H, z, 0.6))
                if abs(q) == 2:
                    w.setze(x, H + 1, z, w.b(f"{d['tr']}_wall" if d["tr"] == "nether_brick" else "polished_blackstone_brick_wall",
                                             up=True, north="none", south="none", east="none", west="none",
                                             waterlogged=False) if k % 3 else w.b(f"{d['tr']}_fence") if d["tr"] == "nether_brick"
                            else d["M"](x, H + 1, z, 0.9))
            if k % 7 == 0:
                for y in range(0, H):
                    for q in range(-2, 3):
                        x, z = (k, q) if achse == "x" else (q, k)
                        if abs(q) < 2 or y < 2:
                            w.setze(x, y, z, d["M"](x, y, z, y / H))
            else:
                t = (k % 7) / 7
                bog = int(H - 1 - math.sin(t * math.pi) * (H - 3))
                for q in range(-2, 3):
                    x, z = (k, q) if achse == "x" else (q, k)
                    for y in range(bog, H):
                        w.setze(x, y, z, d["M"](x, y, z, y / H))
    a = _r(5 * u + 3, 4)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            for y in range(H, H + _r(6 * u + 3, 4)):
                if max(abs(x), abs(z)) == a:
                    fen = y == H + 2 and (x + z) % 3 == 0
                    w.setze(x, y, z, w.b(d["glas"]) if fen else d["M"](x, y, z, 0.8))
            if max(abs(x), abs(z)) == a and (x + z) % 2 == 0:
                w.setze(x, H + _r(6 * u + 3, 4), z, d["M"](x, 0, z, 1))
    for x in range(-a + 1, a):
        for z in range(-a + 1, a):
            w.setze(x, H, z, w.b("soul_sand"))
            if (x + z) % 2 == 0:
                w.setze(x, H + 1, z, w.b("nether_wart", age=3))
    for (x, z) in ((L, 0), (-L, 0), (0, L), (0, -L)):
        w.setze(x, H + 1, z, MB.kohlenbecken(w, seele=d["seele"]))
    hohl(w, 2)
    return w


def bastion(seed, g=2):
    """Bastionsruine: wuchtiger Schwarzsteinblock mit Goldadern, Treppenrampen, Brücken und Schätzen."""
    w = _welt(seed)
    u = U[g]
    M = Mat(w, ["blackstone", "polished_blackstone_bricks", "cracked_polished_blackstone_bricks", "basalt",
                "gilded_blackstone", "polished_blackstone"], kontrast=1.2)
    a = _r(12 * u + 5)
    H = _r(14 * u + 6)
    netherboden(w, a + 6, art="basalt")
    for y in range(0, H):
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                m = max(abs(x), abs(z))
                if m >= a - 1 or (y % 6 == 0 and m < a):
                    w.setze(x, y, z, M(x, y, z, y / H))
    for k in range(H):
        for q in range(-1, 2):
            w.setze(-a + 2 + k, k, a + 1 + q - 0 if False else a + 2 + q, treppe(w, "polished_blackstone_brick", "east"))
    for i in range(int(6 * u) + 2):
        x, z = int((w.rng.random() - 0.5) * a * 1.4), int((w.rng.random() - 0.5) * a * 1.4)
        w.setze(x, H, z, w.b("gold_block"))
    zerfall(w, set(b for b in w.bloecke.values() if b), Rauschen(w, 3), H, staerke=0.55, boden=2)
    for i in range(3):
        w.setze(i - 1, 1, 0, w.b("chest", facing="south", type="single", waterlogged=False))
    hohl(w, 2)
    return w


def seelenschrein(seed, g=1):
    """Seelenschrein: Altar aus Seelensand und Knochen unter einem Baldachin aus Schwarzstein, blaue Flammen,
    Schädel und Ketten."""
    w = _welt(seed)
    u = U[g]
    a = _r(4 * u + 2, 3)
    netherboden(w, a + 8, art="seele")
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            w.setze(x, 1, z, w.b("polished_blackstone_bricks") if max(abs(x), abs(z)) < a else
                    treppe(w, "polished_blackstone_brick", "east" if x == -a else "west" if x == a else "south" if z == -a else "north"))
    for sx in (-a + 1, a - 1):
        for sz in (-a + 1, a - 1):
            for y in range(2, 2 + _r(5 * u + 3, 4)):
                w.setze(sx, y, sz, w.b("polished_blackstone_wall" if False else "bone_block", axis="y"))
    yt = 2 + _r(5 * u + 3, 4)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            w.setze(x, yt, z, w.b("polished_blackstone_brick_slab", type="bottom", waterlogged=False) if max(abs(x), abs(z)) == a
                    else w.b("polished_blackstone_bricks"))
    w.setze(0, 2, 0, w.b("soul_soil"))
    w.setze(0, 3, 0, w.b("soul_campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for (x, z) in ((1, 0), (-1, 0)):
        w.setze(x, 2, z, w.b("skeleton_skull", rotation=0) if False else w.b("bone_block", axis="y"))
    w.setze(0, yt - 1, 0, MB.kronleuchter(w, seele=True))
    hohl(w, 2)
    return w


def pilzriesenhain(seed, g=1):
    """Riesenpilzhain: Karmesin- oder Wirrpilze in Baumgröße mit Wurmranken, Shroomlights und Nylium."""
    w = _welt(seed)
    d = _nb(w, seed)
    u = U[g]
    rng = w.rng
    R = _r(12 * u + 6)
    netherboden(w, R, art=d["boden"])
    stamm = "crimson_stem" if d["boden"] == "crimson" else "warped_stem"
    hut = "nether_wart_block" if d["boden"] == "crimson" else "warped_wart_block"
    ranke = "weeping_vines_plant" if d["boden"] == "crimson" else "twisting_vines_plant"
    plaetze = []
    for i in range(int(5 * u) + 3):
        for _ in range(30):
            a = rng.random() * 2 * math.pi
            dd = rng.random() * R * 0.8
            x, z = round(math.cos(a) * dd), round(math.sin(a) * dd)
            if all(math.hypot(x - px, z - pz) > 6 for px, pz in plaetze):
                plaetze.append((x, z))
                break
        else:
            continue
        H = int(7 + rng.random() * 9 * u)
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b(stamm, axis="y"))
            if H > 10 and y < 3:
                for dx, dz in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    w.setze(x + dx, y, z + dz, w.b(stamm, axis="y"))
        r = 2.5 + rng.random() * 2 * u
        for k in range(4):
            for xx, zz in scheibe(r - k * 0.4, x, z):
                if math.hypot(xx - x, zz - z) > r - k * 0.4 - 1.3 or k == 3:
                    w.setze(xx, H + 1 - k, zz, w.b(hut) if rng.random() > 0.06 else w.b("shroomlight"))
        for xx, zz in kreisrand(r, x, z):
            if rng.random() < 0.4:
                for kk in range(int(1 + rng.random() * 5)):
                    if w.frei(xx, H - 3 - kk, zz):
                        w.setze(xx, H - 3 - kk, zz, w.b("weeping_vines_plant") if d["boden"] == "crimson" else w.b(hut))
    hohl(w, 2)
    return w


def portalruine(seed, g=1):
    """Netherportal-Ruine: zerbrochener Obsidianrahmen mit weinendem Obsidian, Goldblöcken und
    verkohltem Steinboden, halb in Netherrack versunken."""
    w = _welt(seed)
    u = U[g]
    rng = w.rng
    b, h = _r(4 * u + 2, 4), _r(6 * u + 3, 5)
    netherboden(w, b + 8, art="basalt")
    for x in range(-b, b + 1):
        for y in range(1, h + 1):
            if x in (-b, b) or y in (1, h):
                if rng.random() < 0.82:
                    w.setze(x, y, 0, w.b("crying_obsidian") if rng.random() < 0.25 else w.b("obsidian"))
    for x in range(-b - 3, b + 4):
        for z in range(-3, 4):
            if rng.random() < 0.6:
                w.setze(x, 0, z, w.b(["stone_bricks", "cracked_stone_bricks", "mossy_stone_bricks", "netherrack",
                                      "magma_block"][int(rng.integers(5))]))
    for i in range(3):
        w.setze(int(rng.integers(-b, b)), 1, int(rng.integers(-3, 4)), w.b("gold_block"))
    w.setze(b + 2, 1, 2, w.b("chest", facing="north", type="single", waterlogged=False))
    return w


def glutsee(seed, g=2):
    """Glutsee-Plattform: Basaltsäulen tragen eine Plattform über einem Lavasee, Pavillon mit Netherziegeldach."""
    w = _welt(seed)
    d = _nb(w, seed)
    u = U[g]
    R = _r(14 * u + 6)
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("lava", level=0))
        w.setze(x, -1, z, w.b("magma_block"))
    for x, z in kreisrand(R + 1):
        w.setze(x, 0, z, w.b("blackstone"))
    a = _r(5 * u + 3, 4)
    yp = _r(5 * u + 3, 4)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            w.setze(x, yp, z, d["M"](x, yp, z, 0.6))
            if max(abs(x), abs(z)) == a and (x + z) % 3 == 0:
                for y in range(-1, yp):
                    w.setze(x, y, z, w.b("basalt", axis="y"))
    st = P.Stil(w, wand=d["M"], sockel=d["M"], gesims=d["tr"], dach="mcw_rot" if d["boden"] == "crimson" else "mcw_schwarz",
                holz=d["holz"], laeden=False, fenster="glass_pane", licht=d["licht"])
    P.gebaeude(w, st, -a + 2, -a + 2, a - 2, a - 2, y0=yp + 1, etagen=1, eh=4, dach="walm", tuer="south",
               gauben=False, kamine=0, sockel_h=0)
    for z in range(a, R + 2):
        for x in (-1, 0, 1):
            w.setze(x, yp, z, w.b(f"{d['holz']}_planks"))
        if z % 4 == 0:
            for sx in (-2, 2):
                w.setze(sx, yp + 1, z, w.b(d["licht"]) if d["licht"] == "shroomlight" else
                        w.b("soul_lantern", hanging=False, waterlogged=False))
    hohl(w, 2)
    return w


def seelenbruecke(seed, g=2):
    """Knochenbrücke über ein Seelensandtal: Rippenbögen als Geländer, Schädelpfeiler, blaue Feuer."""
    w = _welt(seed)
    u = U[g]
    L = _r(18 * u + 6)
    netherboden(w, L + 4, art="seele")
    for x in range(-L, L + 1):
        y = 3 + int(4 * u * math.cos(x / L * math.pi / 2))
        for z in range(-1, 2):
            w.setze(x, y, z, w.b("bone_block", axis="x") if z == 0 else w.b("bone_block", axis="y"))
        if x % 3 == 0:
            for sz in (-1, 1):
                for k in range(4):
                    w.setze(x, y + 1 + k, sz * (2 + (1 if 0 < k < 3 else 0)), w.b("bone_block", axis="y"))
                w.setze(x, y + 5, sz * 2, w.b("bone_block", axis="y"))
        if x % 9 == 0:
            for yy in range(0, y):
                w.setze(x, yy, 0, w.b("bone_block", axis="y"))
            w.setze(x, y + 1, 0, w.b("soul_campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    hohl(w, 2)
    return w


def piglinlager(seed, g=1):
    """Piglin-Lager: Hütten aus Schwarzstein und Gold, Goldhaufen, Banner, Lagerfeuer und Handelsstand."""
    w = _welt(seed)
    u = U[g]
    rng = w.rng
    R = _r(10 * u + 6)
    netherboden(w, R + 2, art="basalt")
    st = P.Stil(w, wand="schwarzstein", sockel="schwarzstein", gesims="polished_blackstone_brick", dach="mcw_schwarz",
                holz="crimson", laeden=False, licht="lantern")
    n = 2 + g
    for i in range(n):
        a = i / n * 2 * math.pi
        cx, cz = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        P.gebaeude(w, st, cx - 2, cz - 2, cx + 2, cz + 2, y0=1, etagen=1, eh=3, dach="walm", tuer="south",
                   gauben=False, kamine=0)
    for x, z in scheibe(2.5):
        hh = int(3 - math.hypot(x, z))
        for y in range(1, hh + 1):
            w.setze(x, y, z, w.b("gold_block") if rng.random() < 0.7 else w.b("raw_gold_block"))
    for x, z in kreisrand(R * 0.3):
        if rng.random() < 0.3:
            w.setze(x, 1, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    hohl(w, 2)
    return w


def ghastturm(seed, g=2):
    """Ghastturm: schlanker Netherziegelturm mit Dornenkranz und einer riesigen weißen Ghast-Statue obenauf."""
    w = _welt(seed)
    d = _nb(w, seed)
    u = U[g]
    st = P.Stil(w, wand=d["M"], sockel=d["M"], gesims=d["tr"], dach="nether", holz=d["holz"], laeden=False,
                fenster="red_stained_glass_pane" if d["boden"] == "crimson" else "cyan_stained_glass_pane")
    netherboden(w, _r(10 * u + 5), art=d["boden"])
    H = _r(22 * u + 8)
    P.turm(w, st, 0, 0, 1, H, max(2.4, 3 * u), dach="platt", fenster=6)
    g_ = _r(4 * u + 2, 3)
    for x in range(-g_, g_ + 1):
        for y in range(0, 2 * g_ + 1):
            for z in range(-g_, g_ + 1):
                if max(abs(x), abs(y - g_), abs(z)) == g_:
                    w.setze(x, H + 3 + y, z, w.b("white_concrete") if (x + y + z) % 5 else w.b("white_terracotta"))
    for sx in (-1, 1):
        w.setze(sx * 2, H + 3 + g_, g_, w.b("black_concrete"))
    w.setze(0, H + 3 + g_ - 2, g_, w.b("red_concrete"))
    for i in range(9):
        x, z = -g_ + 1 + (i % 3) * g_, -g_ + 1 + (i // 3) * g_
        for k in range(1, int(2 + w.rng.random() * 4)):
            w.setze(x, H + 3 - k, z, w.b("white_concrete"))
    hohl(w, 2)
    return w


def blutturm(seed, g=2):
    """Blutturm: verdrehter roter Netherziegel-Turm mit Netherwarzen-Ranken, Glutfenstern und Krone."""
    from weltwunder import arkanspirale
    w = arkanspirale(seed, max(0, g - 1))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if "purpur" in n or "prismarine" in n or "end_stone" in n or "quartz" in n:
            w.bloecke[(x, y, z)] = w.b("red_nether_bricks") if rng.random() < 0.6 else w.b("nether_bricks")
        elif "amethyst" in n or "sea_lantern" in n or "froglight" in n:
            w.bloecke[(x, y, z)] = w.b("shroomlight")
        elif "glass" in n:
            w.bloecke[(x, y, z)] = w.b("red_stained_glass")
        elif "obsidian" in n or "gold" in n:
            w.bloecke[(x, y, z)] = w.b("nether_wart_block")
    return w


def netherwarzenfarm(seed, g=1):
    """Netherwarzenfarm: Terrassen aus Seelensand mit Warzen, Bewässerungsrinnen aus Lava? Nein – aus Magma,
    ein Lagerschuppen, Fässer und Hängelaternen."""
    w = _welt(seed)
    d = _nb(w, seed)
    u = U[g]
    a = _r(7 * u + 4, 5)
    netherboden(w, a + 6, art="crimson")
    for k in range(3):
        for x in range(-a + k * 2, a - k * 2 + 1):
            for z in range(-a + k * 2, a - k * 2 + 1):
                w.setze(x, k, z, d["M"](x, k, z, 0.4) if max(abs(x - 0), abs(z)) == a - k * 2 else w.b("soul_sand"))
                if max(abs(x), abs(z)) < a - k * 2 and (x + z) % 4:
                    w.setze(x, k + 1, z, w.b("nether_wart", age=int(w.rng.integers(1, 4))))
    st = P.Stil(w, wand=["crimson_planks", "stripped_crimson_stem", "crimson_planks"], sockel=d["M"], gesims=d["tr"],
                dach="mcw_rot", holz="crimson", laeden=False)
    P.gebaeude(w, st, a + 2, -2, a + 6, 2, y0=1, etagen=1, eh=4, dach="sattel", tuer="west", gauben=False, kamine=0)
    hohl(w, 2)
    return w


def glowstonegrotte(seed, g=2):
    """Glowstone-Grotte: Basaltgewölbe mit hängenden Glowstone-Trauben, Tropfsteinen und Lavatümpel."""
    w = _welt(seed)
    u = U[g]
    R = 12 * u + 5
    S = Skulptur(w, 1.0)
    S.mat("f", lambda x, y, z, lx, ly, lz: w.b(["basalt", "blackstone", "netherrack", "smooth_basalt"][(x + y + z) % 4], **({"axis": "y"} if (x + y + z) % 4 == 0 else {})))
    S.plus(ell(0, 0, 0, R, R * 0.8, R), "f")
    S.minus(ell(0, 1, 0, R * 0.75, R * 0.6, R * 0.75))
    S.minus(ell(0, 1, R * 0.8, R * 0.4, R * 0.4, R * 0.4))
    S.rendern((-R - 1, 0, -R - 1), (R + 1, R, R + 1))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if w.frei(x, y - 1, z) and y > 3 and rng.random() < 0.06:
            for k in range(1, int(2 + rng.random() * 3)):
                w.setze(x, y - k, z, w.b("glowstone"))
    for x, z in scheibe(R * 0.25, 2, -2):
        w.setze(x, 0, z, w.b("lava", level=0))
    netherboden(w, _r(R + 4), art="basalt")
    hohl(w, 3)
    return w


def schaedelthron(seed, g=2):
    """Schädelthron: Thron aus Seelensand und Schwarzstein, flankiert von Wither-Rosen und Knochenpfeilern,
    über allem ein steinerner dreiköpfiger Schädel."""
    w = _welt(seed)
    u = U[g]
    netherboden(w, _r(12 * u + 5), art="seele")
    for k in range(4):
        r = _r(6 * u + 3) - k
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                w.setze(x, 1 + k, z, w.b("polished_blackstone_bricks") if max(abs(x), abs(z)) < r else
                        treppe(w, "polished_blackstone_brick", "east" if x == -r else "west" if x == r else "south" if z == -r else "north")
                        if not (abs(x) == r and abs(z) == r) else w.b("gilded_blackstone"))
    y = 5
    for x in range(-2, 3):
        for yy in range(y, y + 2):
            w.setze(x, yy, 0, w.b("soul_soil"))
        for yy in range(y + 2, y + _r(10 * u + 4)):
            if abs(x) < 3 - (yy - y) // 6:
                w.setze(x, yy, -1, w.b("polished_blackstone") if abs(x) < 2 else w.b("blackstone"))
    S = Skulptur(w, 1.0 * u + 0.4)
    S.mat("k", lambda x, y, z, *a: w.b("coal_block") if (x + y) % 3 else w.b("blackstone"))
    S.mat("a", bl(w, "soul_lantern"))
    for sx in (-1, 0, 1):
        S.plus(ell(sx * 3.2, 0.5 * (sx == 0), 0, 1.4, 1.4, 1.4), "k")
        for ex in (-0.5, 0.5):
            S.plus(ell(sx * 3.2 + ex, 0.7 + 0.5 * (sx == 0), 1.2, 0.3, 0.3, 0.3), "a")
    S.rendern((-6, -2, -2), (6, 3, 3), versatz=(0.5, y + _r(10 * u + 4) + 2, -0.5))
    for sx in (-1, 1):
        for k in range(1, 5):
            w.setze(sx * (_r(6 * u + 3) + 2), k, 0, w.b("bone_block", axis="y"))
        w.setze(sx * (_r(6 * u + 3) + 2), 5, 0, w.b("soul_campfire", lit=True, signal_fire=False, facing="north",
                                                     waterlogged=False))
    hohl(w, 2)
    return w


def kettenbruecke(seed, g=2):
    """Kettenbrücke: Hängebrücke an schweren Ketten zwischen zwei Basalttürmen über einem Lavagraben."""
    w = _welt(seed)
    u = U[g]
    L = _r(16 * u + 6)
    H = _r(12 * u + 6)
    for x in range(-L + 2, L - 1):
        for z in range(-6, 7):
            w.setze(x, -2, z, w.b("lava", level=0))
    for sx in (-1, 1):
        for y in range(-2, H):
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if max(abs(dx), abs(dz)) == 2 or y < 1:
                        w.setze(sx * L + dx, y, dz, w.b("basalt", axis="y") if (dx + dz) % 2 else w.b("polished_blackstone_bricks"))
    for x in range(-L + 2, L - 1):
        y = int(2 * math.cos(x / L * math.pi / 2) * 0) + 1 - int(2 * math.cos(x / L * math.pi / 2))
        for z in range(-1, 2):
            w.setze(x, y + 2, z, w.b("crimson_planks") if (x + z) % 3 else w.b("crimson_slab", type="top", waterlogged=False))
        ky = int(H - 2 - (H - 6) * math.cos(x / L * math.pi / 2))
        for sz in (-2, 2):
            w.setze(x, ky, sz, w.b("chain", axis="x", waterlogged=False))
            if x % 3 == 0:
                for yy in range(y + 3, ky):
                    w.setze(x, yy, sz, w.b("chain", axis="y", waterlogged=False))
    hohl(w, 2)
    return w


def nethersaal(seed, g=2):
    """Nethersaal: hohe Halle aus roten Netherziegeln mit Spitzbogenfenstern aus Rotglas, Schwarzstein-Strebepfeilern
    und Macaw-Dach in Netherrot."""
    from kathedralen import halle, S as KS, SAKRAL
    w = _welt(seed)
    u = U[g]
    SAKRAL["nether_tmp"] = dict(wand="netherziegel", sockel="schwarzstein", gesims="nether_brick", dach="mcw_rot",
                                holz="crimson", glas="rot")
    s = KS(w, "nether_tmp")
    L, B, H = _r(12 * u + 5), _r(4 * u + 2, 3), _r(11 * u + 5, 8)
    netherboden(w, L + 8, art="crimson")
    halle(w, s, -L, -B, L, B, 1, H, achse="x")
    for sz in (-1, 1):
        P.turm(w, s.st, -L - 2, sz * (B + 1), 1, _r(H * 1.6), 2.0 * min(u, 1.7), form="achteck", dach="nadel",
               krone=False, fahne=None)
    hohl(w, 2)
    return w


def wirrwaldhuette(seed, g=1):
    """Hütte im Wirrwald: Haus aus Wirrholz mit Shroomlight-Laternen, Wirrpilzgarten und Dreh-Ranken."""
    w = _welt(seed)
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    netherboden(w, a + 8, art="warped")
    st = P.Stil(w, wand=["warped_planks", "stripped_warped_stem", "warped_planks"], sockel="schwarzstein",
                gesims="warped", dach="schindel_blau", holz="warped", laeden=True, licht="soul_lantern",
                fenster="cyan_stained_glass_pane")
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1 + (g >= 2), eh=4, dach="sattel", tuer="south", kamine=1)
    for i in range(4):
        x, z = -a - 3 + i * 3, b + 4
        for y in range(1, 4 + i % 2):
            w.setze(x, y, z, w.b("warped_stem", axis="y"))
        for xx, zz in scheibe(1.5, x, z):
            w.setze(xx, 4 + i % 2, zz, w.b("warped_wart_block"))
        w.setze(x, 4 + i % 2 - 1, z + 1, w.b("shroomlight"))
    hohl(w, 2)
    return w


def hoglinstall(seed, g=1):
    """Hoglin-Stall: Gehege aus Schwarzsteinmauern und Ketten, Futtertrog mit Karmesinpilzen, Wachhaus."""
    w = _welt(seed)
    u = U[g]
    a = _r(8 * u + 4, 6)
    netherboden(w, a + 6, art="crimson")
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if max(abs(x), abs(z)) == a:
                w.setze(x, 1, z, w.b("polished_blackstone_bricks"))
                w.setze(x, 2, z, _wand(w, "polished_blackstone_brick_wall") if (x + z) % 2 else
                        w.b("iron_bars", north=abs(x) == a, south=abs(x) == a, east=abs(z) == a, west=abs(z) == a,
                            waterlogged=False))
    for x in range(-2, 3):
        w.setze(x, 1, 0, w.b("crimson_slab", type="bottom", waterlogged=False))
        w.setze(x, 2, 0, w.b("crimson_fungus") if x % 2 else w.b("air")) if False else None
    for y in range(1, 6):
        w.setze(a, y, a, w.b("basalt", axis="y"))
    w.setze(a, 6, a, w.b("soul_lantern", hanging=False, waterlogged=False))
    hohl(w, 2)
    return w


def lavaterrassen(seed, g=2):
    """Lavaterrassen: gestufter Netherrack-Hügel, über dessen Stufen glühende Magmaströme kaskadieren,
    oben ein Lavabecken in einer Schwarzsteinfassung."""
    w = _welt(seed)
    u = U[g]
    n = 4 + g
    a = _r(12 * u + 5)
    rng = w.rng
    for k in range(n):
        h = a - k * a // (n + 1)
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                for y in range(k * 2, k * 2 + 2):
                    w.setze(x, y, z, w.b("netherrack") if (x * 3 + y + z) % 7 else w.b("blackstone"))
                rinne = abs(x) <= 1 or abs(z) <= 1
                if rinne:
                    w.setze(x, k * 2 + 1, z, w.b("magma_block") if (x + z + k) % 3 else w.b("shroomlight"))
                elif max(abs(x), abs(z)) == h and rng.random() < 0.15:
                    w.setze(x, k * 2 + 2, z, w.b("crimson_roots"))
    top = (n - 1) * 2 + 2
    hk = a - (n - 1) * a // (n + 1)
    for x in range(-hk + 1, hk):
        for z in range(-hk + 1, hk):
            if max(abs(x), abs(z)) == hk - 1:
                w.setze(x, top, z, w.b("polished_blackstone_bricks"))
            else:
                w.setze(x, top - 1, z, w.b("lava", level=0))
    netherboden(w, a + 4, art="crimson")
    hohl(w, 3)
    return w


def bastionsportal(seed, g=1):
    """Prunkportal: ein Netherportal-Rahmen aus Obsidian in einer Torfassade aus Gold und Schwarzstein mit
    Piglin-Bannern – fertig zum Anzünden."""
    w = _welt(seed)
    u = U[g]
    b, h = 2, 4
    netherboden(w, _r(10 * u + 4), art="basalt")
    for x in range(-b - 1, b + 2):
        for y in range(1, h + 3):
            if x in (-b - 1, b + 1) or y in (1, h + 2):
                w.setze(x, y, 0, w.b("obsidian"))
    for x in range(-b - 4, b + 5):
        for y in range(1, h + 7):
            if abs(x) > b + 1 or y > h + 2:
                if abs(x) <= b + 4 - max(0, y - h - 3):
                    w.setze(x, y, -1, w.b("gilded_blackstone") if (x + y) % 4 == 0 else w.b("polished_blackstone_bricks"))
    for sx in (-b - 3, b + 3):
        for y in range(2, h + 2):
            w.setze(sx, y, 1, w.b("orange_wool") if y % 2 else w.b("black_wool"))
    return w


def seelenallee(seed, g=1):
    """Seelenallee: ein Prachtweg aus Schwarzstein durch das Seelensandtal, gesäumt von Knochenpfeilern mit
    Seelenfeuer-Becken, an seinem Ende ein Torbogen."""
    w = _welt(seed)
    u = U[g]
    L = _r(16 * u + 6)
    netherboden(w, L + 4, art="seele")
    for z in range(-L, L + 1):
        for x in range(-2, 3):
            w.setze(x, 0, z, w.b("polished_blackstone_bricks") if (x + z) % 3 else w.b("polished_blackstone"))
        if z % 5 == 0:
            for sx in (-3, 3):
                for y in range(1, 5):
                    w.setze(sx, y, z, w.b("bone_block", axis="y") if y < 4 else MB.kohlenbecken(w, seele=True))
    for x in range(-4, 5):
        for y in range(1, 8):
            if abs(x) >= 3 or y >= 6:
                w.setze(x, y, L + 1, w.b("polished_blackstone_bricks") if (x + y) % 4 else w.b("gilded_blackstone"))
    return w


NETHER = {
    "netherfestung": ("Netherfestung", netherfestung),
    "seelenschrein": ("Seelenschrein", seelenschrein),
    "pilzriesenhain": ("Riesenpilzhain", pilzriesenhain),
    "bastion": ("Bastionsruine", bastion),
    "portalruine": ("Portalruine", portalruine),
    "glutsee": ("Glutsee-Plattform", glutsee),
    "seelenbruecke": ("Knochenbrücke", seelenbruecke),
    "piglinlager": ("Piglin-Lager", piglinlager),
    "ghastturm": ("Ghastturm", ghastturm),
    "blutturm": ("Blutturm", blutturm),
    "netherwarzenfarm": ("Netherwarzen-Farm", netherwarzenfarm),
    "glowstonegrotte": ("Glowstone-Grotte", glowstonegrotte),
    "schaedelthron": ("Schädelthron", schaedelthron),
    "kettenbruecke": ("Kettenbrücke", kettenbruecke),
    "nethersaal": ("Nethersaal", nethersaal),
    "wirrwaldhuette": ("Wirrwald-Hütte", wirrwaldhuette),
    "hoglinstall": ("Hoglin-Stall", hoglinstall),
    "lavaterrassen": ("Lavaterrassen", lavaterrassen),
    "bastionsportal": ("Prunkportal", bastionsportal),
    "seelenallee": ("Seelenallee", seelenallee),
}


# ============================================================================ END


def endboden(w, R, cx=0, cz=0, chorus=0.004):
    r1 = Rauschen(w, 4)
    rng = w.rng
    for x, z in scheibe(R, cx, cz):
        if not w.frei(x, 0, z):
            continue
        v = r1(x, 0, z)
        w.setze(x, 0, z, w.b("end_stone") if v < 0.75 else w.b("end_stone_bricks") if v < 0.85 else w.b("obsidian"))
        if rng.random() < chorus:
            chorus_pflanze(w, x, 1, z, int(2 + rng.random() * 4))


def chorus_pflanze(w, x, y, z, h):
    for k in range(h):
        w.setze(x, y + k, z, w.b("chorus_plant", up=k < h - 1, down=True, north=False, south=False, east=False,
                                 west=False))
    w.setze(x, y + h, z, w.b("chorus_flower", age=int(w.rng.integers(2, 6))))


def _ed(w, seed):
    if _stil(seed) == 0:
        return dict(M=Mat(w, ["purpur_block", "purpur_pillar", "purpur_block", "end_stone_bricks", "purpur_block"],
                          kontrast=0.8),
                    E=Mat(w, "endstein"), tr="purpur", licht="end_rod", glas="magenta_stained_glass",
                    dach=["purpur", "purpur", "end_stone_brick"], akz="crying_obsidian")
    return dict(M=Mat(w, ["obsidian", "crying_obsidian", "obsidian", "polished_blackstone", "obsidian"], kontrast=0.9),
                E=Mat(w, ["end_stone", "end_stone_bricks", "obsidian", "end_stone"]), tr="polished_blackstone_brick",
                licht="end_rod", glas="purple_stained_glass", dach=["polished_blackstone_brick", "blackstone"],
                akz="amethyst_block")


def endturm(seed, g=2):
    """End-Turm: Purpurturm wie aus einer Endstadt – gestapelte Kammern mit Balkonen, Endstab-Lichtern
    und einem Dach mit Hörnern."""
    w = _welt(seed)
    d = _ed(w, seed)
    u = U[g]
    endboden(w, _r(10 * u + 5), chorus=0.008)
    y = 1
    stock = 3 + g
    for s in range(stock):
        a = _r((4 - s * 0.3) * u + 2, 2)
        h = 5
        for yy in range(y, y + h):
            for x in range(-a, a + 1):
                for z in range(-a, a + 1):
                    if max(abs(x), abs(z)) == a:
                        fen = yy - y in (2, 3) and abs(x if abs(z) == a else z) == 1
                        w.setze(x, yy, z, w.b(d["glas"]) if fen else d["M"](x, yy, z, 0.5))
                    elif yy == y:
                        w.setze(x, yy, z, w.b("purpur_block") if (x + z) % 2 else w.b("end_stone_bricks"))
        for x in range(-a - 1, a + 2):
            for z in range(-a - 1, a + 2):
                if max(abs(x), abs(z)) == a + 1:
                    w.setze(x, y + h, z, w.b(f"{d['tr']}_slab", type="bottom", waterlogged=False))
        for (x, z) in ((a + 1, 0), (-a - 1, 0)):
            w.setze(x, y + 2, z, w.b("end_rod", facing="up"))
        y += h
        if s % 2 == 0:
            for (dx, dz) in ((1, 0), (-1, 0)):
                for k in range(3):
                    w.setze(dx * (a + 1 + k), y - 1, 0, d["M"](0, y, 0, 0.5))
    for sx in (-1, 1):
        for k in range(4):
            w.setze(sx * (2 - k // 2), y + k, 0, w.b("purpur_pillar", axis="y") if k < 3 else w.b("end_rod", facing="up"))
    hohl(w, 2)
    return w


def obsidiansplitter(seed, g=2):
    """Obsidiansplitter: ein Ring hoher Obsidiansäulen wie auf der Hauptinsel, mit Eisengittern und
    Leuchtkristallen (Seelaternen) auf der Spitze."""
    w = _welt(seed)
    u = U[g]
    R = 14 * u + 6
    endboden(w, _r(R + 6), chorus=0.0)
    n = 8 if u > 0.8 else 6
    for i in range(n):
        a = i / n * 2 * math.pi
        cx, cz = round(math.cos(a) * R), round(math.sin(a) * R)
        r = 1.6 + (i % 3) * 0.7 * u
        H = int((14 + (i * 7) % 12) * u + 6)
        for y in range(0, H):
            for x, z in scheibe(r, cx, cz):
                w.setze(x, y, z, w.b("obsidian") if (x + y + z) % 7 else w.b("crying_obsidian"))
        w.setze(cx, H, cz, w.b("bedrock"))
        w.setze(cx, H + 1, cz, w.b("sea_lantern"))
        if i % 2 == 0:
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    for y in range(H, H + 3):
                        if max(abs(dx), abs(dz)) == 1:
                            w.setze(cx + dx, y, cz + dz, w.b("iron_bars", north=False, south=False, east=False,
                                                             west=False, waterlogged=False))
    hohl(w, 2)
    return w


def chorusgarten(seed, g=1):
    """Chorusgarten: verzweigte Chorus-Gewächse in Kübeln aus Purpur, Endstab-Laternen und Pfade."""
    w = _welt(seed)
    u = U[g]
    rng = w.rng
    R = _r(10 * u + 5)
    endboden(w, R, chorus=0.02)
    for x in range(-R, R + 1):
        for z in (-1, 0, 1):
            w.setze(x, 0, z, w.b("purpur_block"))
            w.setze(z, 0, x, w.b("purpur_block"))
    for i in range(int(6 * u) + 4):
        a = rng.random() * 2 * math.pi
        dd = R * (0.3 + 0.6 * rng.random())
        x, z = round(math.cos(a) * dd), round(math.sin(a) * dd)
        hh = int(4 + rng.random() * 6 * u)
        chorus_pflanze(w, x, 1, z, hh)
        for k in range(2):
            ax = int(rng.integers(-1, 2))
            if ax:
                w.setze(x + ax, 1 + hh // 2 + k, z, w.b("chorus_plant", up=False, down=False, north=False, south=False,
                                                        east=ax < 0, west=ax > 0))
    for sx in (-3, 3):
        for sz in (-3, 3):
            w.setze(sx, 1, sz, w.b("purpur_pillar", axis="y"))
            w.setze(sx, 2, sz, w.b("end_rod", facing="up"))
    return w


def leerenschiff(seed, g=2):
    """Leerenschiff: schwebendes Purpurschiff mit Flügel-Segeln, Drachenkopf am Bug, Laderaum und Mast."""
    w = _welt(seed)
    d = _ed(w, seed)
    u = U[g]
    L = 12 * u + 5
    B = 3.5 * u + 1.5
    yo = _r(10 * u + 6)
    S = Skulptur(w, 1.0)
    S.mat("h", lambda x, y, z, *a: w.b("purpur_block") if (x + y) % 4 else w.b("purpur_pillar", axis="x"))
    S.mat("o", bl(w, "obsidian"))
    S.plus(ohne(ell(0, 0, 0, L, 3.5 * u, B), lambda X, Y, Z: Y > 0.6), "h")
    S.minus(ell(0, 1, 0, L - 1.2, 3.0 * u, B - 1.2))
    S.plus(kap((L - 1, 0, 0), (L + 3, 2.5, 0), 1.0, 0.6), "o")
    S.rendern((-L - 2, -4 * u - 1, -B - 1), (L + 5, 2, B + 1), versatz=(0.5, yo, 0.5))
    for x in range(-int(L) + 2, int(L) - 1):
        for z in range(-int(B) + 1, int(B)):
            w.setze(x, yo, z, w.b("purpur_slab", type="bottom", waterlogged=False))
    for y in range(yo, yo + _r(12 * u + 4)):
        w.setze(0, y, 0, w.b("purpur_pillar", axis="y"))
    for sz in (-1, 1):
        for x in range(-3, 4):
            for y in range(yo + 3, yo + _r(10 * u + 3)):
                if abs(x) < 4 - (y - yo - 3) // 4:
                    w.setze(x, y, sz, w.b("magenta_stained_glass") if (x + y) % 3 else w.b("purple_stained_glass"))
    w.setze(int(L) - 2, yo + 1, 0, w.b("end_rod", facing="up"))
    hohl(w, 2)
    return w


def leerenbogen(seed, g=2):
    """Leerenbogen: schwebender Endstein-Bogen über dem Nichts mit hängenden Chorus-Ranken."""
    w = _welt(seed)
    u = U[g]
    R = 12 * u + 5
    S = Skulptur(w, 1.0)
    E = Mat(w, "endstein")
    S.mat("e", lambda x, y, z, lx, ly, lz: E(x, y, z, ly / R))
    S.plus(lambda X, Y, Z: ((np.sqrt(X ** 2 + Y ** 2) - R) ** 2 / (3 * u) ** 2 + Z ** 2 / (4 * u) ** 2 <= 1) & (Y >= 0), "e")
    for sx in (-1, 1):
        S.plus(ell(sx * R, 0, 0, 5 * u, 4 * u, 6 * u), "e")
    S.rendern((-R - 7 * u, -5 * u, -7 * u), (R + 7 * u, R + 4 * u, 7 * u))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if w.frei(x, y + 1, z) and rng.random() < 0.03:
            chorus_pflanze(w, x, y + 1, z, int(2 + rng.random() * 3))
    hohl(w, 2)
    return w


def endinsel(seed, g=2):
    """Schwebende End-Insel: Endstein-Brocken mit Obsidianadern, kleiner Purpurhütte und Chorusbüschen."""
    w = _welt(seed)
    d = _ed(w, seed)
    u = U[g]
    R = 12 * u + 5
    yo = _r(14 * u + 6)
    r_n = Rauschen(w, 4)
    for x, z in scheibe(R):
        dd = math.hypot(x, z) / R
        unter = yo - (1 - dd ** 1.4) * 10 * u * (0.7 + 0.5 * r_n(x, 0, z))
        for y in range(int(unter), yo + 1):
            w.setze(x, y, z, d["E"](x, y, z, (y - unter) / max(1, yo - unter)))
        if w.rng.random() < 0.012:
            chorus_pflanze(w, x, yo + 1, z, int(2 + w.rng.random() * 4))
    st = P.Stil(w, wand=d["M"], sockel=d["E"], gesims=d["tr"], dach=d["dach"], holz="warped", laeden=False,
                fenster="magenta_stained_glass_pane", licht="soul_lantern")
    P.gebaeude(w, st, -3, -3, 3, 3, y0=yo + 1, etagen=1, eh=4, dach="walm", tuer="south", gauben=False, kamine=0,
               sockel_h=0)
    hohl(w, 3)
    return w


def leerenportal(seed, g=2):
    """Leerenportal: ein Endportal-Rahmen auf einem Treppenpodest aus Endstein, umringt von Endstäben,
    darüber schwebt ein Drachenei auf einem Obsidianfinger."""
    w = _welt(seed)
    u = U[g]
    endboden(w, _r(12 * u + 6), chorus=0.01)
    for k in range(3):
        r = 6 - k
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                w.setze(x, 1 + k, z, w.b("end_stone_bricks") if max(abs(x), abs(z)) < r else
                        treppe(w, "end_stone_brick", "east" if x == -r else "west" if x == r else "south" if z == -r else "north")
                        if not (abs(x) == r and abs(z) == r) else w.b("purpur_pillar", axis="y"))
    y = 4
    for x in range(-2, 3):
        for z in range(-2, 3):
            rand = max(abs(x), abs(z)) == 2 and not (abs(x) == 2 and abs(z) == 2)
            if rand:
                f = "south" if z == -2 else "north" if z == 2 else "east" if x == -2 else "west"
                w.setze(x, y, z, w.b("end_portal_frame", facing=f, eye=w.rng.random() < 0.5))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        w.setze(round(math.cos(a) * 5), 4, round(math.sin(a) * 5), w.b("end_rod", facing="up"))
    for yy in range(4, 4 + _r(10 * u + 4)):
        w.setze(0, yy + 2, -4, w.b("obsidian"))
    w.setze(0, 4 + _r(10 * u + 4) + 2, -4, w.b("dragon_egg"))
    hohl(w, 2)
    return w


def purpurpalast(seed, g=2):
    """Purpurpalast: großer Bau aus Purpur mit Säulenhallen, Kuppel aus Amethyst, Endstab-Kronleuchtern und
    Shulker-Kästen als Schmuck."""
    w = _welt(seed)
    d = _ed(w, seed)
    u = U[g]
    a = _r(9 * u + 4)
    y0 = platz(w, a + _r(8 * u, 5), d["E"], rand="end_stone_brick", muster=["end_stone_bricks", "purpur_block", "obsidian"],
               akzent="purpur_pillar" if False else "crying_obsidian", lichter="soul_lantern",
               pfosten="end_stone_brick_wall")
    st = P.Stil(w, wand=d["M"], sockel=d["E"], gesims=d["tr"], dach=d["dach"], holz="warped", laeden=False,
                fenster="magenta_stained_glass_pane", licht="soul_lantern")
    top = P.gebaeude(w, st, -a, -a // 2, a, a // 2, y0=y0, etagen=2, eh=_r(3 * u + 3, 4), dach="flach", tuer="south",
                     pilaster=3)
    kuppel(w, lambda x, y, z, t: w.b("amethyst_block") if (x + y) % 3 else w.b("purpur_block"), 0, 0, top, a * 0.45,
           form="zwiebel", spitze="end_rod")
    for sx in (-1, 1):
        P.turm(w, st, sx * (a + 2), 0, y0, _r(top * 1.4), max(1.6, 2.2 * u), dach="nadel", fahne=None)
    for i in range(4):
        w.setze(-a + 2 + i * (a - 1), y0, a // 2 + 2, w.b(["purple_shulker_box", "magenta_shulker_box"][i % 2],
                                                           facing="up"))
    hohl(w, 2)
    return w


def leerenobservatorium(seed, g=1):
    """Leeren-Observatorium: Obsidianturm mit gläserner Linse, umkreist von schwebenden Ringen aus
    Endstab-Lichtern."""
    w = _welt(seed)
    d = _ed(w, seed)
    u = U[g]
    endboden(w, _r(10 * u + 5))
    st = P.Stil(w, wand=["obsidian", "crying_obsidian", "obsidian"], sockel=d["E"], gesims="polished_blackstone_brick",
                dach=d["dach"], holz="warped", laeden=False, fenster="purple_stained_glass_pane")
    H = _r(18 * u + 6)
    R = max(2.5, 3.2 * u)
    P.turm(w, st, 0, 0, 1, H, R, dach="platt", fenster=6)
    kuppel(w, w.b("purple_stained_glass"), 0, 0, H + 2, R + 0.5, form="rund", spitze="end_rod")
    for yy, rr in ((H * 0.4, R + 4), (H * 0.7, R + 3)):
        for x, z in kreisrand(rr):
            if (x + z) % 2 == 0:
                w.setze(x, int(yy), z, w.b("end_rod", facing="up"))
    hohl(w, 2)
    return w


def shulkertuerme(seed, g=1):
    """Shulker-Türme: drei schlanke Purpursäulen mit Kästen als Kapitell, verbunden durch Brücken."""
    w = _welt(seed)
    u = U[g]
    endboden(w, _r(10 * u + 5))
    pts = [(0, -5), (5, 3), (-5, 3)]
    for i, (x, z) in enumerate(pts):
        x, z = round(x * u), round(z * u)
        H = _r((12 + i * 3) * u + 4)
        for y in range(1, H):
            for dx in (0, 1):
                for dz in (0, 1):
                    w.setze(x + dx, y, z + dz, w.b("purpur_pillar", axis="y"))
        for dx in range(-1, 3):
            for dz in range(-1, 3):
                w.setze(x + dx, H, z + dz, w.b(["purple_shulker_box", "magenta_shulker_box", "white_shulker_box"][i],
                                               facing="up"))
    hohl(w, 2)
    return w


def endrodgarten(seed, g=1):
    """Lichtgarten: Felder aus Endstäben unterschiedlicher Höhe in Mustern, dazwischen Amethystknospen."""
    w = _welt(seed)
    u = U[g]
    R = _r(9 * u + 4)
    endboden(w, R + 2)
    for x, z in scheibe(R):
        a = math.atan2(z, x)
        d = math.hypot(x, z)
        if abs(math.sin(a * 4 + d * 0.5)) < 0.25:
            hh = int(1 + (R - d) / R * 4 * u)
            for k in range(hh):
                w.setze(x, 1 + k, z, w.b("end_rod", facing="up") if k == hh - 1 else w.b("purpur_pillar", axis="y"))
        elif (x + z) % 5 == 0:
            w.setze(x, 1, z, w.b("small_amethyst_bud", facing="up", waterlogged=False))
    return w


def dracheneischrein(seed, g=1):
    """Drachenei-Schrein: ein Drachenei auf einem Podest unter einem Baldachin aus Obsidian mit Kristallsäulen."""
    w = _welt(seed)
    u = U[g]
    endboden(w, _r(8 * u + 4))
    a = 3
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            w.setze(x, 1, z, w.b("obsidian") if max(abs(x), abs(z)) == a else w.b("end_stone_bricks"))
    for (x, z) in ((a, a), (-a, a), (a, -a), (-a, -a)):
        for y in range(2, 7):
            w.setze(x, y, z, w.b("crying_obsidian") if y % 2 else w.b("obsidian"))
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            w.setze(x, 7, z, w.b("obsidian"))
    w.setze(0, 2, 0, w.b("purpur_pillar", axis="y"))
    w.setze(0, 3, 0, w.b("dragon_egg"))
    w.setze(0, 6, 0, w.b("end_rod", facing="down"))
    return w


def endkathedrale(seed, g=2):
    """Purpurkathedrale: gotische Halle aus Purpur und Endstein mit violetten Spitzbogenfenstern und
    Obsidian-Fialen."""
    from kathedralen import halle, S as KS, SAKRAL
    w = _welt(seed)
    u = U[g]
    SAKRAL["end_tmp"] = dict(wand="endstein", sockel=["obsidian", "crying_obsidian"], gesims="purpur", dach="purpur",
                             holz="warped", glas="rot")
    s = KS(w, "end_tmp")
    s.glas = Verlauf(w, "EG", ["purple_stained_glass", "magenta_stained_glass", "pink_stained_glass",
                                "purple_stained_glass"])
    L, B, H = _r(12 * u + 5), _r(4 * u + 2, 3), _r(12 * u + 5, 9)
    endboden(w, L + 8)
    halle(w, s, -L, -B, L, B, 1, H, achse="x")
    for sz in (-1, 1):
        P.turm(w, s.st, -L - 2, sz * (B + 1), 1, _r(H * 1.7), 2.0 * min(u, 1.7), form="achteck", dach="nadel",
               krone=False, fahne=None)
    hohl(w, 2)
    return w


def endstation(seed, g=1):
    """Verlassene Endstation: Forscherlager mit Zelten, Kisten, Fernrohr und einem kaputten Elytra-Startturm."""
    w = _welt(seed)
    u = U[g]
    endboden(w, _r(10 * u + 5))
    from wueste_eis import zelt
    zelt(w, -4, 0, 2.5, 4, ["purple", "white"])
    zelt(w, 4, 2, 2.2, 3, ["magenta", "white"])
    for k in range(3):
        w.setze(0, 1, -4 + k, w.b("barrel", facing="up", open=False))
    for y in range(1, _r(10 * u + 4)):
        w.setze(6, y, -5, w.b("purpur_pillar", axis="y") if y % 4 else w.b("end_rod", facing="up"))
    w.setze(6, _r(10 * u + 4), -5, w.b("purpur_slab", type="bottom", waterlogged=False))
    return w


def schwebethron(seed, g=2):
    """Schwebender Thron: eine Obsidianscheibe mit Thron, über dem Nichts schwebend, gehalten von Ketten aus
    Endstäben, umgeben von Splittern."""
    w = _welt(seed)
    d = _ed(w, seed)
    u = U[g]
    yo = _r(10 * u + 6)
    R = 5 * u + 3
    for x, z in scheibe(R):
        w.setze(x, yo, z, w.b("obsidian") if math.hypot(x, z) > R - 1.2 else w.b("purpur_block"))
        w.setze(x, yo - 1, z, w.b("crying_obsidian") if math.hypot(x, z) < 2 else w.b("obsidian")) if math.hypot(x, z) < R - 1 else None
    for x in range(-1, 2):
        for y in range(yo + 1, yo + 3):
            w.setze(x, y, 0, w.b("purpur_block"))
        for y in range(yo + 3, yo + 7):
            w.setze(x, y, -1, w.b("purpur_pillar", axis="y") if x == 0 else w.b("purpur_block"))
    schwebende_splitter(w, d["E"], 0, yo, 0, R + 6, int(8 * u), groesse=1.5 * u, h=6)
    return w


def endfestung(seed, g=2):
    """End-Festung: sechseckige Mauer aus Endsteinziegeln mit Purpurtürmen und einem zentralen Obsidiankern."""
    from burgen import mauer, Burgstil, POOL
    w = _welt(seed)
    u = U[g]
    POOL["end_tmp"] = dict(wand="endstein", sockel=["obsidian"], gesims="end_stone_brick", dach="purpur",
                           holz="warped", banner=["purple_wool", "black_wool"], mauer="end_stone_brick")
    B = Burgstil(w, "end_tmp")
    R = _r(14 * u + 5)
    endboden(w, R + 5)
    n = 6
    pts = [(round(math.cos(i / n * 2 * math.pi) * R), round(math.sin(i / n * 2 * math.pi) * R)) for i in range(n)]
    for i in range(n):
        mauer(w, B, pts[i], pts[(i + 1) % n], _r(6 * u + 3, 5), dick=3, y0=1, mitte=(0, 0))
    for (x, z) in pts:
        P.turm(w, B.st, x, z, 1, _r(10 * u + 6), max(1.6, 2.2 * u), dach="nadel", fahne=B.banner)
    for y in range(1, _r(18 * u + 6)):
        for x, z in scheibe(2.5):
            w.setze(x, y, z, w.b("obsidian") if (x + y + z) % 5 else w.b("crying_obsidian"))
    w.setze(0, _r(18 * u + 6), 0, w.b("end_rod", facing="up"))
    hohl(w, 2)
    return w


def endbaum(seed, g=2):
    """Chorusbaum-Riese: ein baumgroßer Chorus mit verzweigten Ästen und Blüten aus Amethyst."""
    w = _welt(seed)
    u = U[g]
    rng = w.rng
    endboden(w, _r(8 * u + 4))

    def ast(x, y, z, laenge, tiefe):
        for k in range(laenge):
            w.setze(x, y + k, z, w.b("chorus_plant", up=True, down=True, north=False, south=False, east=False, west=False)
                    if tiefe < 2 else w.b("purpur_pillar", axis="y"))
        y += laenge
        if tiefe == 0:
            w.setze(x, y, z, w.b("amethyst_block") if rng.random() < 0.5 else w.b("chorus_flower", age=5))
            return
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if rng.random() < 0.6:
                n = int(1 + rng.random() * 2 * u)
                for k in range(1, n + 1):
                    w.setze(x + dx * k, y, z + dz * k, w.b("purpur_block") if tiefe >= 2 else w.b("chorus_plant", up=False,
                                                                                                 down=False, north=True,
                                                                                                 south=True, east=True,
                                                                                                 west=True))
                ast(x + dx * n, y, z + dz * n, int(2 + rng.random() * 3 * u), tiefe - 1)
    ast(0, 1, 0, int(5 * u + 3), 3)
    return w


def leerentreppe(seed, g=2):
    """Leerentreppe: eine frei schwebende Wendeltreppe aus Purpur, die um eine Obsidiansäule in den Himmel führt,
    oben eine Aussichtsplattform."""
    w = _welt(seed)
    u = U[g]
    H = _r(26 * u + 8)
    R = 5 * u + 2
    endboden(w, _r(R + 5))
    for y in range(1, H):
        for x, z in scheibe(1.2):
            w.setze(x, y, z, w.b("obsidian") if y % 5 else w.b("crying_obsidian"))
    for k in range(H * 2):
        a = k / 12 * math.pi
        y = 1 + k // 2
        if y >= H:
            break
        for rr in range(2, int(R) + 1):
            x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
            w.setze(x, y, z, w.b("purpur_slab", type="top" if k % 2 else "bottom", waterlogged=False))
        if k % 6 == 0:
            x, z = round(math.cos(a) * R), round(math.sin(a) * R)
            w.setze(x, y + 1, z, w.b("end_rod", facing="up"))
    for x, z in scheibe(R + 1):
        w.setze(x, H, z, w.b("purpur_block") if math.hypot(x, z) < R else w.b("end_stone_bricks"))
    for x, z in kreisrand(R + 1):
        w.setze(x, H + 1, z, w.b("end_stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                                 waterlogged=False))
    hohl(w, 2)
    return w


def amethystgeode(seed, g=2):
    """Aufgebrochene Geode im Endstein: Schichten aus Basalt, Calcit und Amethyst, innen leuchtende Kristalle."""
    w = _welt(seed)
    u = U[g]
    R = 9 * u + 4
    S = Skulptur(w, 1.0)
    S.mat("b", bl(w, "smooth_basalt"))
    S.mat("c", bl(w, "calcite"))
    S.mat("a", lambda x, y, z, *a: w.b("budding_amethyst") if (x + y * 3 + z) % 7 == 0 else w.b("amethyst_block"))
    S.plus(ell(0, 0, 0, R, R, R), "b")
    S.plus(ell(0, 0, 0, R - 1.2, R - 1.2, R - 1.2), "c")
    S.plus(ell(0, 0, 0, R - 2.2, R - 2.2, R - 2.2), "a")
    S.minus(ell(0, 0, 0, R - 3.2, R - 3.2, R - 3.2))
    S.minus(lambda X, Y, Z: Z > R * 0.35 - Y * 0.2)
    S.rendern((-R - 1, -R * 0.4, -R - 1), (R + 1, R + 1, R + 1), versatz=(0.5, R * 0.4, 0.5))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b).endswith(("amethyst_block", "budding_amethyst")) and rng.random() < 0.25:
            for dx, dy, dz, f in ((0, 1, 0, "up"), (0, -1, 0, "down"), (1, 0, 0, "east"), (-1, 0, 0, "west"),
                                  (0, 0, 1, "south"), (0, 0, -1, "north")):
                if w.frei(x + dx, y + dy, z + dz) and math.hypot(x + dx, y + dy - R * 0.4, z + dz) < R - 2.5:
                    w.setze(x + dx, y + dy, z + dz, w.b("amethyst_cluster", facing=f, waterlogged=False))
                    break
    endboden(w, _r(R + 5))
    hohl(w, 2)
    return w


def endtor(seed, g=1):
    """End-Tor: drei hintereinander gestaffelte Purpur-Spitzbögen mit Obsidian-Schlusssteinen und Endstäben."""
    w = _welt(seed)
    u = U[g]
    endboden(w, _r(10 * u + 4))
    for i in range(3):
        z = -4 + i * 4
        R = (5 - i * 0.8) * u + 2
        for x in range(-int(R) - 2, int(R) + 3):
            for y in range(0, int(R * 1.6) + 3):
                dl = math.hypot(x - R * 0.4, y) if x < 0 else math.hypot(x + R * 0.4, y)
                if R * 1.4 - 1.4 < dl <= R * 1.4:
                    w.setze(x, y + 1, z, w.b("purpur_block") if (x + y) % 3 else w.b("purpur_pillar", axis="y"))
        w.setze(0, int(R * 1.25) + 1, z, w.b("crying_obsidian"))
        for sx in (-1, 1):
            w.setze(sx * (int(R * 1.0) + 1), 1, z + 1, w.b("end_rod", facing="up"))
    return w


END = {
    "endturm": ("End-Turm", endturm),
    "obsidiansplitter": ("Obsidiansäulen-Ring", obsidiansplitter),
    "chorusgarten": ("Chorusgarten", chorusgarten),
    "leerenschiff": ("Leerenschiff", leerenschiff),
    "leerenbogen": ("Leerenbogen", leerenbogen),
    "endinsel": ("Schwebende End-Insel", endinsel),
    "leerenportal": ("Leerenportal", leerenportal),
    "purpurpalast": ("Purpurpalast", purpurpalast),
    "leerenobservatorium": ("Leeren-Observatorium", leerenobservatorium),
    "shulkertuerme": ("Shulker-Türme", shulkertuerme),
    "endrodgarten": ("Lichtgarten", endrodgarten),
    "dracheneischrein": ("Drachenei-Schrein", dracheneischrein),
    "endkathedrale": ("Purpurkathedrale", endkathedrale),
    "endstation": ("Verlassene Endstation", endstation),
    "schwebethron": ("Schwebender Thron", schwebethron),
    "endfestung": ("End-Festung", endfestung),
    "endbaum": ("Chorusbaum-Riese", endbaum),
    "leerentreppe": ("Leerentreppe", leerentreppe),
    "amethystgeode": ("Amethyst-Geode", amethystgeode),
    "endtor": ("End-Tor", endtor),
}

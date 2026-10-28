"""Unterwasserwelt und Vulkanreich (neu) – je 20 Bauten. Nether und End kommen aus elemente2.py.

Unterwasser-Vorlagen sind für den Meeresgrund gedacht: Korallen leben nur im Wasser.
"""

from __future__ import annotations

import math

import numpy as np

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


# ============================================================================ UNTERWASSER

KORALLEN = ["tube", "brain", "bubble", "fire", "horn"]


def meeresgrund(w, R, cx=0, cz=0, dichte=1.0):
    """Sand, Kies, Ton, Seegras, Tang und Korallenbüschel."""
    r1 = Rauschen(w, 4)
    r2 = Rauschen(w, 1.5)
    rng = w.rng
    for x, z in scheibe(R, cx, cz):
        v = r1(x, 0, z) * 0.7 + r2(x, 0, z) * 0.3
        b = "sand" if v < 0.5 else "gravel" if v < 0.62 else "clay" if v < 0.7 else "sand" if v < 0.85 else "mud"
        if w.frei(x, 0, z):
            w.setze(x, 0, z, w.b(b))
        if not w.frei(x, 1, z):
            continue
        q = rng.random() * dichte
        if q < 0.12:
            w.setze(x, 1, z, w.b("seagrass"))
        elif q < 0.16:
            w.setze(x, 1, z, w.b("tall_seagrass", half="lower"))
            w.setze(x, 2, z, w.b("tall_seagrass", half="upper"))
        elif q < 0.168:
            h = int(2 + rng.random() * 5)
            for k in range(1, h):
                w.setze(x, k, z, w.b("kelp_plant"))
            w.setze(x, h, z, w.b("kelp", age=20))
        elif q < 0.21:
            w.setze(x, 1, z, w.b(f"{KORALLEN[int(rng.integers(5))]}_coral", waterlogged=True))
        elif q < 0.22:
            w.setze(x, 1, z, w.b("sea_pickle", pickles=int(1 + rng.integers(4)), waterlogged=True))


def korallenbewuchs(w, dichte=0.25):
    """Korallenfächer an Wänden, Korallen auf Oberseiten von Steinblöcken."""
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if not any(t in n for t in ("prismarine", "stone", "coral_block", "sand", "andesite", "tuff", "cobble")):
            continue
        if y >= 1 and w.frei(x, y + 1, z) and rng.random() < dichte * 0.4:
            k = KORALLEN[int(rng.integers(5))]
            w.setze(x, y + 1, z, w.b(f"{k}_coral" if rng.random() < 0.6 else f"{k}_coral_fan", waterlogged=True))
        elif rng.random() < dichte * 0.15:
            for dx, dz, f in ((1, 0, "east"), (-1, 0, "west"), (0, 1, "south"), (0, -1, "north")):
                if w.frei(x + dx, y, z + dz):
                    w.setze(x + dx, y, z + dz, w.b(f"{KORALLEN[int(rng.integers(5))]}_coral_wall_fan", facing=f,
                                                   waterlogged=True))
                    break


def _uw(w, seed):
    if _stil(seed) == 0:
        return dict(M=Mat(w, ["dark_prismarine", "prismarine_bricks", "prismarine", "prismarine_bricks",
                              "dark_prismarine"], kontrast=1.0),
                    S=Mat(w, ["prismarine_bricks", "prismarine", "sea_lantern", "prismarine_bricks"], kontrast=0.6),
                    tr="prismarine_brick", licht="sea_lantern", gold="gold_block",
                    glas="light_blue_stained_glass", koralle="tube")
    return dict(M=Mat(w, ["polished_diorite", "calcite", "smooth_quartz", "quartz_bricks", "diorite"], kontrast=0.8),
                S=Mat(w, ["quartz_bricks", "smooth_quartz", "pearlescent_froglight", "quartz_bricks"], kontrast=0.6),
                tr="quartz", licht="pearlescent_froglight", gold="gold_block", glas="cyan_stained_glass",
                koralle="fire")


def korallenpalast(seed, g=2):
    """Korallenpalast: Prismarin-Palast mit Kuppeln aus Korallenblöcken, Säulengängen, Seelaternen-Lichtern
    und üppigem Korallengarten."""
    w = _welt(seed)
    d = _uw(w, seed)
    u = U[g]
    a = _r(8 * u + 4, 6)
    meeresgrund(w, a + _r(10 * u, 6))
    st = P.Stil(w, wand=d["M"], sockel=d["M"], gesims=d["tr"], dach=["dark_prismarine", "prismarine_brick"],
                holz="warped" if False else "dark_oak", laeden=False, fenster="glass_pane", licht="sea_lantern")
    top = P.gebaeude(w, st, -a, -a // 2, a, a // 2, y0=1, etagen=2, eh=_r(3 * u + 3, 4), dach="flach", tuer="south",
                     gauben=False, kamine=0, pilaster=3)
    kor = Mat(w, [f"{k}_coral_block" for k in ("tube", "brain", "bubble", "horn", "fire")], kontrast=1.5, zelle=2)
    kuppel(w, lambda x, y, z, t: kor(x, y, z, t), 0, 0, top, a * 0.5, form="zwiebel", spitze=d["licht"])
    for (x, z) in ((-a, -a // 2), (a, -a // 2), (-a, a // 2), (a, a // 2)):
        P.turm(w, st, x, z, 1, _r(14 * u + 6), max(1.5, 2.0 * u), dach="platt", krone=True, fahne=None)
        kuppel(w, lambda x_, y_, z_, t: kor(x_, y_, z_, t), x, z, _r(14 * u + 6) + 2, max(1.6, 2.2 * u), form="zwiebel",
               spitze=d["licht"])
    korallenbewuchs(w, 0.35)
    hohl(w, 2)
    return w


def glaskuppel(seed, g=2):
    """Glaskuppel-Station: Forschungsbasis mit gerippter Glaskuppel, Röhrengängen zu kleinen Kuppeln,
    Schleusentor, Lichtern und Korallenzucht."""
    w = _welt(seed)
    d = _uw(w, seed)
    u = U[g]
    R = 10 * u + 4
    meeresgrund(w, _r(R * 2 + 4))
    vg = Verlauf(w, "uwg", ["glass", d["glas"], "glass", "light_blue_stained_glass"])
    for cx, cz, r in ((0, 0, R), (R * 1.5, 0, R * 0.5), (-R * 0.9, R * 1.1, R * 0.45)):
        cx, cz = round(cx), round(cz)
        S = Skulptur(w, 1.0)
        S.mat("g", lambda x, y, z, lx, ly, lz: vg(ly / r * 3, x, y, z))
        S.mat("r", sk(d["M"], 0, r))
        S.plus(lambda X, Y, Z, r=r: (np.abs(np.sqrt(X * X + Y * Y + Z * Z) - r) < 0.55) & (Y >= 0), "g")
        for i in range(8):
            a = i / 8 * math.pi
            S.plus(lambda X, Y, Z, a=a, r=r: (np.abs(np.sqrt(X * X + Y * Y + Z * Z) - r) < 1.0)
                   & (np.abs(-X * math.sin(a) + Z * math.cos(a)) < 0.5) & (Y >= 0), "r")
        S.plus(torus(0, 0.5, 0, r, 1.0, achse="y"), "r")
        S.rendern((-r - 2, 0, -r - 2), (r + 2, r + 2, r + 2), versatz=(cx + 0.5, 1, cz + 0.5))
        w.setze(cx, int(r) + 2, cz, w.b(d["licht"]))
    for (ax, az, bx, bz) in ((R - 1, 0, R * 1.5 - R * 0.5, 0), (-R * 0.6, R * 0.6, -R * 0.9, R * 1.1 - R * 0.45)):
        n = int(max(abs(bx - ax), abs(bz - az))) + 1
        for k in range(n + 1):
            x, z = round(ax + (bx - ax) * k / n), round(az + (bz - az) * k / n)
            for dx in range(-2, 3):
                for dy in range(0, 5):
                    rr = math.hypot(dx, dy - 2)
                    if 1.5 < rr <= 2.5:
                        w.setze(x + (dx if abs(bz - az) > abs(bx - ax) else 0), 1 + dy,
                                z + (dx if abs(bx - ax) >= abs(bz - az) else 0), w.b("glass"))
    korallenbewuchs(w, 0.2)
    hohl(w, 2)
    return w


def versunkener_tempel(seed, g=2):
    """Versunkener Tempel: halb eingestürzte Säulenhalle aus Prismarin, umgestürzte Säulen, Statuenkopf im Sand,
    überwuchert von Korallen, Tang und Seegras."""
    from kathedralen import saeulentempel
    w = saeulentempel(seed, g)
    d = _uw(w, seed)
    ersetz = {}
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if "grass" in n or "dirt" in n or "podzol" in n or "flower" in n or n.endswith(("poppy", "dandelion")):
            w.bloecke[(x, y, z)] = w.b("sand")
        elif any(t in n for t in ("quartz", "diorite", "calcite", "andesite", "stone_brick", "smooth_stone")):
            w.bloecke[(x, y, z)] = d["M"](x, y, z, y / 20) if (x + y + z) % 3 else w.b("prismarine_bricks")
    zerfall(w, set(b for b in w.bloecke.values() if b), Rauschen(w, 3), 30 * U[g], staerke=0.8, boden=4)
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 0 and not w.P.name(b).startswith("minecraft:") is False and w.P.name(b).endswith(("campfire", "lantern")):
            del w.bloecke[(x, y, z)]
    meeresgrund(w, _r(20 * U[g] + 8), dichte=1.3)
    korallenbewuchs(w, 0.4)
    return w


def korallenriff(seed, g=1):
    """Korallenriff: wogende Korallenhügel in allen Farben, Röhren, Fächer, Meeresgurken und Seegraswiesen."""
    w = _welt(seed)
    u = U[g]
    R = _r(14 * u + 6)
    r_n = Rauschen(w, 4)
    r_f = Rauschen(w, 7)
    rng = w.rng
    for x, z in scheibe(R):
        dd = math.hypot(x, z) / R
        hh = (r_n(x, 0, z) - 0.35) * 9 * u * (1 - dd ** 2)
        k = KORALLEN[int(r_f(x, 3, z) * 4.99)]
        for y in range(1, int(hh) + 1):
            w.setze(x, y, z, w.b(f"{k}_coral_block") if rng.random() < 0.85 else w.b(f"{KORALLEN[int(rng.integers(5))]}_coral_block"))
    meeresgrund(w, R + 3, dichte=1.5)
    korallenbewuchs(w, 0.8)
    for i in range(int(6 * u) + 2):
        a = rng.random() * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.6 * rng.random()), round(math.sin(a) * R * 0.6 * rng.random())
        k = KORALLEN[int(rng.integers(5))]
        y0 = max([y for (xx, y, zz) in w.bloecke if (xx, zz) == (x, z)] + [0])
        for y in range(y0 + 1, y0 + int(3 + rng.random() * 5 * u)):
            w.setze(x, y, z, w.b(f"{k}_coral_block"))
    return w


def riesenmuschel(seed, g=2):
    """Riesenmuschel: aufgeklappte Kammmuschel mit gerippter Schale, darin eine leuchtende Perle."""
    w = _welt(seed)
    d = _uw(w, seed)
    u = U[g]
    s = 1.9 * u + 0.5
    S = Skulptur(w, s)
    farben = ["pink_terracotta", "white_terracotta", "pink_concrete", "smooth_quartz", "calcite"] if _stil(seed) == 0 \
        else ["light_blue_terracotta", "white_terracotta", "cyan_terracotta", "smooth_quartz", "calcite"]
    S.mat("m", lambda x, y, z, lx, ly, lz: w.b(farben[int(abs(math.atan2(lx, lz + 6) * 14)) % len(farben)]))
    S.mat("p", bl(w, d["licht"]))
    for oben in (False, True):
        def f(X, Y, Z, oben=oben):
            if oben:
                Yr, Zr = Y * math.cos(0.9) - (Z + 6) * math.sin(0.9), Y * math.sin(0.9) + (Z + 6) * math.cos(0.9) - 6
            else:
                Yr, Zr = Y, Z
            r = np.sqrt(X * X + (Zr + 6) ** 2)
            a = np.arctan2(X, Zr + 6)
            schale = (r < 9) & (np.abs(a) < 1.15) & (np.abs(Yr - (0.35 + 0.35 * np.cos(a * 14)) * (r / 9) * 2.0) < 0.6)
            return schale & (Zr + 6 > 0)
        S.plus(f, "m")
    S.plus(ell(0, 1.6, 0, 1.4, 1.4, 1.4), "p")
    S.rendern((-11, -1, -8), (11, 11, 6), versatz=(0.5, 1.01, 3))
    meeresgrund(w, _r(14 * u + 4))
    hohl(w, 2)
    return w


def saeulenhalle(seed, g=2):
    """Atlantische Säulenhalle: endlose Reihen schlanker Säulen mit Seelaternen-Kapitellen, Kassettendecke,
    Mosaikboden aus Prismarin und Gold."""
    w = _welt(seed)
    d = _uw(w, seed)
    u = U[g]
    a, b = _r(10 * u + 4), _r(6 * u + 3, 4)
    H = _r(8 * u + 4, 6)
    meeresgrund(w, a + 6)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.setze(x, 0, z, w.b(d["gold"]) if (x + z) % 6 == 0 and abs(x) % 3 == 0 else d["M"](x, 0, z, 0.3))
            w.setze(x, H, z, d["S"](x, H, z, 0.8) if (x % 3 and z % 3) else w.b(d["tr"] + "_bricks") if False else
                    d["M"](x, H, z, 0.9))
    for x in range(-a + 1, a, 3):
        for z in range(-b + 1, b, 3):
            for y in range(1, H):
                w.setze(x, y, z, w.b("prismarine_wall" if _stil(seed) == 0 else "diorite_wall", up=True, north="none",
                                     south="none", east="none", west="none", waterlogged=True) if 1 < y < H - 1 else
                        w.b(d["licht"]))
    korallenbewuchs(w, 0.3)
    hohl(w, 2)
    return w


def riesenqualle(seed, g=1):
    """Riesenqualle aus leuchtendem Glas mit wehenden Nesselfäden, schwebend über dem Grund."""
    w = _welt(seed)
    u = U[g]
    st = _stil(seed)
    farben = ["pink_stained_glass", "magenta_stained_glass", "purple_stained_glass"] if st == 0 else \
        ["light_blue_stained_glass", "cyan_stained_glass", "blue_stained_glass"]
    R = 6 * u + 3
    y0 = _r(10 * u + 6)
    v = Verlauf(w, "Q", farben)
    S = Skulptur(w, 1.0)
    S.mat("g", lambda x, y, z, lx, ly, lz: v(ly / R * 2, x, y, z))
    S.mat("l", bl(w, "pearlescent_froglight" if st == 0 else "verdant_froglight"))
    S.plus(ohne(ell(0, 0, 0, R, R * 0.7, R), lambda X, Y, Z: (Y < 0) | ((X * X + Z * Z) / (R - 1.2) ** 2 + Y * Y / (R * 0.7 - 1.2) ** 2 < 1)), "g")
    S.plus(ell(0, R * 0.25, 0, R * 0.4, R * 0.25, R * 0.4), "l")
    S.rendern((-R - 1, -1, -R - 1), (R + 1, R + 1, R + 1), versatz=(0.5, y0, 0.5))
    rng = w.rng
    for i in range(int(10 * u) + 4):
        a = rng.random() * 2 * math.pi
        r = R * (0.3 + 0.6 * rng.random())
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        for k in range(1, int(y0 * (0.4 + 0.5 * rng.random()))):
            xx = x + round(math.sin(k * 0.4 + i) * 0.8)
            w.setze(xx, y0 - k, z, w.b(farben[k % 3].replace("_stained_glass", "_stained_glass_pane"), north=False,
                                       south=False, east=False, west=False, waterlogged=True))
    meeresgrund(w, _r(R + 6))
    return w


def schiffswrack(seed, g=2):
    """Gesunkenes Galeonenwrack: zerbrochener Rumpf auf der Seite, Masten im Sand, Kanonenluken,
    Schatzkiste, überwachsen mit Tang und Korallen."""
    from wueste_eis import gestrandetes_schiff
    w = gestrandetes_schiff(seed, g)
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) in ("minecraft:sand", "minecraft:grass_block", "minecraft:dead_bush"):
            w.bloecke[(x, y, z)] = w.b("sand")
    zerfall(w, set(b for b in w.bloecke.values() if b), Rauschen(w, 2), 20 * U[g], staerke=0.5, boden=3)
    meeresgrund(w, _r(24 * U[g] + 6), dichte=1.4)
    korallenbewuchs(w, 0.25)
    w.setze(2, 2, 0, w.b("chest", facing="south", type="single", waterlogged=True))
    w.setze(2, 1, 0, w.b("gold_block"))
    return w


def tritonstatue(seed, g=2):
    """Statue eines Meereskönigs mit Dreizack und Fischschwanz auf einem Muschelsockel."""
    from motive import figur
    w = _welt(seed)
    d = _uw(w, seed)
    u = U[g]
    S = Skulptur(w, 1.3 * u + 0.4)
    S.mat("k", sk(Mat(w, ["waxed_oxidized_copper", "waxed_weathered_copper", "waxed_oxidized_cut_copper"]) if _stil(seed) == 0
                  else d["M"], 0, 25 * u))
    S.mat("a", bl(w, d["gold"]))
    S.mat("d", bl(w, d["gold"]))
    S.mat("g", bl(w, d["licht"]))
    figur(S, "mensch", "stab", y0=4.0)
    S.minus(lambda X, Y, Z: (Y < 11) & (Y > 3.5))
    S.plus(kap((0, 11, 0), (0, 6, 1), 2.2, 1.8), "k")
    S.plus(kap((0, 6, 1), (0, 3, -2), 1.8, 1.2), "k")
    S.plus(kap((0, 3, -2), (0, 3.5, -6), 1.2, 0.6), "k")
    S.plus(lambda X, Y, Z: (np.abs(X) < 2.5 - np.abs(Z + 7) * 0.3) & (np.abs(Y - 4) < 0.4) & (Z < -6) & (Z > -8.5), "a")
    S.plus(ell(0, 1.5, 0, 4, 1.8, 4), "k")
    S.rendern((-7, -1, -10), (7, 30, 7), versatz=(0.5, 0.01, 0.5))
    meeresgrund(w, _r(12 * u + 4))
    korallenbewuchs(w, 0.2)
    hohl(w, 2)
    return w


def walskelett(seed, g=2):
    """Walskelett am Meeresgrund: gewaltiger Schädel, Wirbelsäule im Bogen und Rippen, umgeben von Tang."""
    from wueste_eis import mammutskelett
    w = _welt(seed)
    u = U[g]
    s = 1.3 * u + 0.4
    S = Skulptur(w, s)
    S.mat("k", lambda x, y, z, *a: w.b("bone_block", axis="x") if (x + z) % 4 else w.b("calcite"))
    for i in range(28):
        t = i / 27
        x = -14 + t * 30
        y = 3 + 2.5 * math.sin(t * math.pi) - 2 * max(0, t - 0.8) * 5
        S.plus(ell(x, y, 0, 0.7, 0.9 - 0.4 * t, 0.9 - 0.4 * t), "k")
        if 0.15 < t < 0.55 and i % 2 == 0:
            for sz in (-1, 1):
                for k in range(5):
                    a0, a1 = k / 5 * math.pi * 0.9, (k + 1) / 5 * math.pi * 0.9
                    S.plus(kap((x, y - math.sin(a0) * 3.5, sz * math.sin(a0) * 3.5 + sz * 0.2),
                               (x, y - math.sin(a1) * 3.5, sz * math.sin(a1) * 3.5 + sz * 0.2), 0.3), "k")
    S.plus(ell(-17, 3, 0, 4, 2, 2.6), "k")
    S.plus(kap((-17, 1.2, 1.8), (-23, 1.0, 1.0), 0.5, 0.3), "k")
    S.plus(kap((-17, 1.2, -1.8), (-23, 1.0, -1.0), 0.5, 0.3), "k")
    S.rendern((-25, -1, -6), (18, 8, 6), versatz=(0.5, 0.01, 0.5))
    meeresgrund(w, _r(26 * u + 4), dichte=1.3)
    return w


def schatzhoehle(seed, g=1):
    """Schatzhöhle im Riff: Felsbogen mit Höhle, Goldhaufen, Truhen, Leuchtgurken und Wächterstatuen."""
    w = _welt(seed)
    u = U[g]
    R = 9 * u + 4
    fels = Mat(w, ["stone", "andesite", "tuff", "dark_prismarine", "cobblestone", "prismarine"], kontrast=1.3)
    S = Skulptur(w, 1.0)
    S.mat("f", lambda x, y, z, lx, ly, lz: fels(x, y, z, ly / R))
    S.plus(ell(0, 0, 0, R, R * 0.75, R), "f")
    S.minus(ell(0, 1, 0, R * 0.7, R * 0.5, R * 0.7))
    S.minus(ell(0, 1, R * 0.8, R * 0.35, R * 0.35, R * 0.4))
    S.rendern((-R - 1, 0, -R - 1), (R + 1, R, R + 1))
    rng = w.rng
    for x, z in scheibe(R * 0.4):
        hh = int(2.5 * (1 - math.hypot(x, z) / (R * 0.4)) * u + 1)
        for y in range(1, hh + 1):
            w.setze(x, y, z, w.b("gold_block") if rng.random() < 0.6 else w.b("raw_gold_block"))
    for (x, z) in ((2, -2), (-2, 1)):
        w.setze(x, 1, z, w.b("chest", facing="south", type="single", waterlogged=True))
    for x, z in kreisrand(R * 0.6):
        if rng.random() < 0.3:
            w.setze(x, 1, z, w.b("sea_pickle", pickles=4, waterlogged=True))
    meeresgrund(w, _r(R + 6))
    korallenbewuchs(w, 0.4)
    hohl(w, 2)
    return w


def leuchtturmruine(seed, g=2):
    """Versunkener Leuchtturm: schräg gekippter Turm am Meeresgrund mit zerbrochener Laterne und Fischschwärmen
    aus Seelaternen."""
    w = _welt(seed)
    u = U[g]
    R = 3 * u + 1.5
    H = 28 * u + 6
    S = Skulptur(w, 1.0)
    S.mat("w", lambda x, y, z, *a: w.b("white_concrete") if int(a[1] / 5) % 2 else w.b("red_terracotta"))
    S.mat("l", bl(w, "sea_lantern"))
    S.plus(ohne(kap((0, 0, 0), (0, H, 0), R, R * 0.7), kap((0, 1, 0), (0, H - 1, 0), R - 1.2, R * 0.7 - 1.2)), "w")
    S.plus(ell(0, H + 1.5, 0, R, 2, R), "l")
    S.rendern((-R - 2, -1, -R - 2), (R + 2, H + 4, R + 2), versatz=(0.5, 0.01, 0.5), dreh=dreh_z(1.15))
    zerfall(w, set(b for b in w.bloecke.values() if b), Rauschen(w, 2), H, staerke=0.4, boden=1)
    meeresgrund(w, _r(H + 4), dichte=1.2)
    korallenbewuchs(w, 0.3)
    return w


def tiefseeportal(seed, g=2):
    """Tiefseeportal: ein Ring aus dunklem Prismarin mit Seelaternen, darin wirbelndes Blau, umgeben von
    Säulenstümpfen und Magmaspalten mit aufsteigenden Blasen."""
    w = _welt(seed)
    d = _uw(w, seed)
    u = U[g]
    R = 9 * u + 4
    S = Skulptur(w, 1.0)
    S.mat("m", sk(Mat(w, ["dark_prismarine", "prismarine_bricks", "dark_prismarine"]), 0, 2 * R))
    S.mat("l", bl(w, "sea_lantern"))
    v = Verlauf(w, "Tp", ["blue_stained_glass", "cyan_stained_glass", "light_blue_stained_glass", "white_stained_glass"])
    S.mat("g", lambda x, y, z, lx, ly, lz: v(min(3, math.hypot(lx, ly - R - 2) / R * 3), x, y, z))
    S.plus(torus(0, R + 2, 0, R, 1.6 * u + 0.5, achse="z"), "m")
    for i in range(12):
        a = i / 12 * 2 * math.pi
        S.plus(ell(math.cos(a) * R, R + 2 + math.sin(a) * R, 0, 1.1, 1.1, 1.6 * u + 0.8), "l")
    S.plus(lambda X, Y, Z: (np.hypot(X, Y - R - 2) < R - 1) & (np.abs(Z) < 0.75), "g")
    S.rendern((-R - 3, 0, -3), (R + 3, 2 * R + 5, 3))
    for x, z in scheibe(R * 1.6):
        if abs(math.sin(math.atan2(z, x) * 5)) < 0.08 and math.hypot(x, z) > R * 0.5:
            w.setze(x, 0, z, w.b("magma_block"))
    meeresgrund(w, _r(R * 1.8))
    hohl(w, 2)
    return w


def unterwassermarkt(seed, g=1):
    """Unterwassermarkt: Stände aus Prismarin unter Muschel-Baldachinen, Körbe mit Perlen (Seegurken),
    Laternen und eine Korallenallee."""
    w = _welt(seed)
    d = _uw(w, seed)
    u = U[g]
    n = 3 + g
    L = n * 6
    meeresgrund(w, L // 2 + 6)
    for z in range(-L // 2, L // 2 + 1):
        for x in range(-2, 3):
            w.setze(x, 0, z, d["M"](x, 0, z, 0.3) if (x + z) % 3 else w.b("smooth_sandstone"))
    for sx in (-1, 1):
        for i in range(n):
            z0 = -L // 2 + i * 6
            x0 = 3 if sx > 0 else -7
            for x in range(x0, x0 + 5):
                for z in range(z0, z0 + 4):
                    if x in (x0, x0 + 4) and z in (z0, z0 + 3):
                        for y in range(1, 4):
                            w.setze(x, y, z, w.b("prismarine_wall", up=True, north="none", south="none", east="none",
                                                 west="none", waterlogged=True))
                    w.setze(x, 4, z, w.b(f"{KORALLEN[(i + x) % 5]}_coral_block"))
                    if z == z0 + 1 and x0 < x < x0 + 4:
                        w.setze(x, 1, z, w.b("barrel", facing="up", open=True))
                        w.setze(x, 2, z, w.b("sea_pickle", pickles=3, waterlogged=True))
    for z in range(-L // 2, L // 2 + 1, 5):
        for sx in (-3, 3):
            w.setze(sx, 1, z, w.b(d["licht"]))
    korallenbewuchs(w, 0.25)
    hohl(w, 2)
    return w


def kelpwald(seed, g=1):
    """Tangwald: dichte, haushohe Kelpwälder mit Lichtungen, Felsen und Seegurken – Lebensraum für Fische."""
    w = _welt(seed)
    u = U[g]
    R = _r(14 * u + 6)
    rng = w.rng
    r_n = Rauschen(w, 4)
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("gravel") if r_n(x, 0, z) < 0.4 else w.b("sand"))
        if r_n(x, 5, z) > 0.42 and rng.random() < 0.45:
            h = int(6 + rng.random() * 14 * u)
            for k in range(1, h):
                w.setze(x, k, z, w.b("kelp_plant"))
            w.setze(x, h, z, w.b("kelp", age=int(rng.integers(0, 25))))
        elif rng.random() < 0.08:
            w.setze(x, 1, z, w.b("sea_pickle", pickles=int(1 + rng.integers(4)), waterlogged=True))
        elif rng.random() < 0.2:
            w.setze(x, 1, z, w.b("seagrass"))
    for i in range(int(4 * u) + 2):
        a = rng.random() * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                for y in range(1, 4):
                    if abs(dx) + abs(dz) + y < 5:
                        w.setze(x + dx, y, z + dz, w.b(["mossy_cobblestone", "andesite", "stone", "prismarine"][(dx + y) % 4]))
    return w


def meerjungfrauenfelsen(seed, g=2):
    """Meerjungfrauen-Felsen: zerklüftete Felsgruppe, die aus dem Wasser ragt, mit Grotte, Muscheln,
    Perlen-Laternen und einer sitzenden Steinfigur."""
    from motive import figur
    w = _welt(seed)
    u = U[g]
    fels = Mat(w, ["stone", "andesite", "tuff", "diorite", "mossy_cobblestone", "prismarine"], kontrast=1.4)
    r_n = Rauschen(w, 3)
    H = 20 * u + 6
    R = 10 * u + 4
    for x, z in scheibe(R):
        dd = min(1.0, math.hypot(x, z) / R)
        hh = H * (1 - dd) ** 1.3 * (0.6 + 0.6 * r_n(x, 0, z))
        for y in range(0, int(hh) + 1):
            w.setze(x, y, z, fels(x, y, z, y / H))
    S = Skulptur(w, 0.8 * u + 0.3)
    S.mat("k", sk(Mat(w, ["calcite", "smooth_quartz", "diorite"]), 0, 20))
    S.mat("a", bl(w, "prismarine"))
    S.mat("d", bl(w, "prismarine"))
    S.mat("g", bl(w, "sea_lantern"))
    figur(S, "elf", "denker", y0=0)
    S.minus(lambda X, Y, Z: Y < 6.5)
    S.plus(kap((0, 7, 0), (0, 3, 3), 2.0, 1.5), "a")
    S.plus(kap((0, 3, 3), (2, 1, 6), 1.5, 0.6), "a")
    top = max(y for (x, y, z) in w.bloecke if abs(x) < 2 and abs(z) < 2)
    S.rendern((-5, -1, -4), (5, 20, 8), versatz=(0.5, top - 2, 0.5))
    meeresgrund(w, _r(R + 6))
    korallenbewuchs(w, 0.2)
    hohl(w, 2)
    return w


def prismarinbogen(seed, g=2):
    """Prismarin-Bogenallee: hohe Spitzbögen aus Prismarin hintereinander, an den Scheiteln Seelaternen."""
    w = _welt(seed)
    d = _uw(w, seed)
    u = U[g]
    n = 3 + g
    R = 5 * u + 3
    meeresgrund(w, _r(n * 4 + R))
    for i in range(n):
        z = -n * 2 + i * 4
        for x in range(-int(R) - 2, int(R) + 3):
            for y in range(0, int(R * 1.6) + 3):
                dl = math.hypot(x - R * 0.4, y) if x < 0 else math.hypot(x + R * 0.4, y)
                if R * 1.4 - 1.4 < dl <= R * 1.4 and y >= 0:
                    w.setze(x, y + 1, z, d["M"](x, y, z, y / (R * 1.6)))
        w.setze(0, int(R * 1.25) + 1, z, w.b(d["licht"]))
    korallenbewuchs(w, 0.3)
    hohl(w, 2)
    return w


def quallengarten(seed, g=1):
    """Quallengarten: viele kleine schwebende Glasquallen in allen Farben über Seegras und Leuchtsteinen."""
    w = _welt(seed)
    u = U[g]
    rng = w.rng
    R = _r(12 * u + 6)
    meeresgrund(w, R)
    farben = ["pink", "magenta", "purple", "light_blue", "cyan", "lime"]
    for i in range(int(10 * u) + 4):
        a = rng.random() * 2 * math.pi
        dd = rng.random() * R * 0.8
        cx, cz = round(math.cos(a) * dd), round(math.sin(a) * dd)
        cy = int(6 + rng.random() * 10 * u)
        f = farben[int(rng.integers(len(farben)))]
        r = 1.5 + rng.random() * 1.5
        for x, z in scheibe(r, cx, cz):
            dd2 = math.hypot(x - cx, z - cz)
            w.setze(x, cy + int((r - dd2) * 0.8), z, w.b(f"{f}_stained_glass"))
        w.setze(cx, cy, cz, w.b("pearlescent_froglight") if i % 2 else w.b("ochre_froglight"))
        for k in range(1, int(3 + rng.random() * 5)):
            w.setze(cx + (k % 2), cy - k, cz, w.b(f"{f}_stained_glass_pane", north=False, south=False, east=False,
                                                  west=False, waterlogged=True))
    return w


def stadtmauer_versunken(seed, g=2):
    """Versunkene Stadtmauer: lange Mauer mit Toren und Rundtürmen aus Prismarin, eingestürzte Abschnitte."""
    from burgen import mauer, Burgstil, POOL
    w = _welt(seed)
    u = U[g]
    POOL["prism_tmp"] = dict(wand="prismarin", sockel="graustein", gesims="prismarine_brick", dach="blau",
                             holz="dark_oak", banner=["cyan_wool", "light_blue_wool"], mauer="stone_brick")
    B = Burgstil(w, "prism_tmp")
    L = _r(22 * u + 8)
    meeresgrund(w, L + 4)
    mauer(w, B, (-L, 0), (L, 0), _r(8 * u + 4, 6), dick=3, y0=1, mitte=(0, -10))
    for sx in (-1, 0, 1):
        P.turm(w, B.st, sx * _r(L * 0.6), 2, 1, _r(14 * u + 6), max(2.2, 3 * u), dach="kuppel", fahne=None)
    zerfall(w, set(b for b in w.bloecke.values() if b), Rauschen(w, 3), 20 * u, staerke=0.6, boden=3)
    korallenbewuchs(w, 0.4)
    hohl(w, 2)
    return w


def seesternplatz(seed, g=1):
    """Seesternplatz: ein großer Seestern als Mosaik im Boden, Säulenkranz, Muschelbrunnen mit Blasensäule."""
    w = _welt(seed)
    d = _uw(w, seed)
    u = U[g]
    R = _r(12 * u + 5)
    meeresgrund(w, R + 4)
    for x, z in scheibe(R):
        a = math.atan2(z, x)
        r = math.hypot(x, z)
        arm = r < R * (0.35 + 0.6 * abs(math.cos(a * 2.5)) ** 3)
        w.setze(x, 0, z, w.b("orange_terracotta") if arm and r > 2 else w.b("yellow_terracotta") if arm else
                d["M"](x, 0, z, 0.3))
    for i in range(10):
        a = i / 10 * 2 * math.pi
        x, z = round(math.cos(a) * (R + 1)), round(math.sin(a) * (R + 1))
        for y in range(1, 6):
            w.setze(x, y, z, d["M"](x, y, z, y / 6) if y < 5 else w.b(d["licht"]))
    w.setze(0, 0, 0, w.b("soul_sand"))
    for y in range(1, 3):
        for x, z in kreisrand(1.5):
            w.setze(x, y, z, d["M"](x, y, z, 0.5))
    hohl(w, 2)
    return w


UNTERWASSER = {
    "korallenpalast": ("Korallenpalast", korallenpalast),
    "glaskuppel": ("Glaskuppel-Station", glaskuppel),
    "versunkener_tempel": ("Versunkener Tempel", versunkener_tempel),
    "korallenriff": ("Korallenriff", korallenriff),
    "riesenmuschel": ("Riesenmuschel", riesenmuschel),
    "saeulenhalle": ("Säulenhalle", saeulenhalle),
    "riesenqualle": ("Riesenqualle", riesenqualle),
    "schiffswrack": ("Galeonenwrack", schiffswrack),
    "tritonstatue": ("Meereskönig-Statue", tritonstatue),
    "walskelett": ("Walskelett", walskelett),
    "schatzhoehle": ("Schatzhöhle", schatzhoehle),
    "leuchtturmruine": ("Versunkener Leuchtturm", leuchtturmruine),
    "tiefseeportal": ("Tiefseeportal", tiefseeportal),
    "unterwassermarkt": ("Unterwassermarkt", unterwassermarkt),
    "kelpwald": ("Tangwald", kelpwald),
    "meerjungfrauenfelsen": ("Meerjungfrauen-Felsen", meerjungfrauenfelsen),
    "prismarinbogen": ("Bogenallee", prismarinbogen),
    "quallengarten": ("Quallengarten", quallengarten),
    "stadtmauer_versunken": ("Versunkene Stadtmauer", stadtmauer_versunken),
    "seesternplatz": ("Seesternplatz", seesternplatz),
}


# ============================================================================ VULKAN


def _vk(w, seed):
    if _stil(seed) == 0:
        return dict(G=Mat(w, ["basalt", "blackstone", "smooth_basalt", "tuff", "cobbled_deepslate", "magma_block"],
                          kontrast=1.3),
                    B=Mat(w, "schwarzstein"), glut="shroomlight", ader="magma_block", feuer="campfire",
                    lava="lava", gold="gold_block", akz="orange_terracotta", glas="orange_stained_glass",
                    licht="lantern")
    return dict(G=Mat(w, ["basalt", "smooth_basalt", "soul_soil", "blackstone", "soul_sand", "polished_basalt"],
                      kontrast=1.3),
                B=Mat(w, "tiefenschiefer"), glut="sea_lantern", ader="crying_obsidian", feuer="soul_campfire",
                lava="soul_fire_b", gold="gold_block", akz="cyan_terracotta", glas="cyan_stained_glass",
                licht="soul_lantern")


def lavastrom(w, d, pts, breite=2):
    """Erstarrter Lavastrom mit glühendem Kern entlang einer Punktliste (x, y, z)."""
    for (a, b) in zip(pts, pts[1:]):
        n = int(max(abs(b[0] - a[0]), abs(b[2] - a[2]))) + 1
        for k in range(n + 1):
            t = k / n
            x, y, z = round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t), round(a[2] + (b[2] - a[2]) * t)
            for dx in range(-breite, breite + 1):
                for dz in range(-breite, breite + 1):
                    if abs(dx) + abs(dz) <= breite:
                        kern = abs(dx) + abs(dz) == 0
                        w.setze(x + dx, y, z + dz, w.b(d["glut"] if kern and k % 4 == 0 else d["ader"]) if kern or
                                w.rng.random() < 0.3 else d["G"](x, y, z, 0.2))


def vulkan(seed, g=2):
    """Vulkan mit Kratersee, Lavarinnen, Rauchsäulen und Basaltsäulen am Fuß."""
    from weltwunder2 import vulkanfeste
    w = vulkanfeste(seed, max(0, g - 1))
    return w


def glutstrom(seed, g=2):
    """Glutstrom-Klippe: Lavafall stürzt über eine Basaltklippe in ein glühendes Becken."""
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    W, H, D = _r(14 * u + 5), _r(16 * u + 6), _r(10 * u + 4)
    r_n = Rauschen(w, 4)
    for x in range(-W, W + 1):
        for z in range(-D, 1):
            hh = H * (0.8 + 0.3 * r_n(x, 0, z))
            for y in range(0, int(hh) + 1):
                w.setze(x, y, z, d["G"](x, y, z, y / H))
    for y in range(0, H):
        for x in range(-1, 2):
            w.setze(x, y, 1, w.b(d["ader"]) if (x + y) % 3 else w.b(d["glut"]))
    for x, z in scheibe(5 * u + 2, 0, 5):
        w.setze(x, 0, z, w.b("magma_block") if math.hypot(x, z - 5) > 3 * u else w.b(d["glut"]))
    gelaende(w, _r(W + 4), art="asche", dichte=0.5)
    hohl(w, 3)
    return w


def feuertempel(seed, g=2):
    """Feuertempel: schwarzer Stufentempel mit Glutfenstern, Feuerschalen an jeder Stufe und einer
    ewigen Flamme in einer Goldschale auf der Spitze."""
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    n = 4 + g
    B0 = _r(10 * u + 5)
    gelaende(w, B0 + 8, art="asche", dichte=0.4)
    sh = _r(2 * u + 1.5, 2)
    for k in range(n):
        h = B0 - k * (B0 - 3) // n
        for y in range(1 + k * sh, 1 + (k + 1) * sh):
            for x in range(-h, h + 1):
                for z in range(-h, h + 1):
                    if max(abs(x), abs(z)) >= h - 1:
                        rnd = max(abs(x), abs(z)) == h
                        fen = rnd and y % sh == 1 and (abs(x) == h and z % 4 == 0 or abs(z) == h and x % 4 == 0)
                        w.setze(x, y, z, w.b(d["glas"]) if fen else d["B"](x, y, z, k / n))
        for (x, z) in ((h, h), (-h, h), (h, -h), (-h, -h)):
            w.setze(x, 1 + (k + 1) * sh, z, w.b(d["feuer"], lit=True, signal_fire=False, facing="north",
                                                waterlogged=False))
    ytop = 1 + n * sh
    for x, z in scheibe(2):
        w.setze(x, ytop, z, w.b(d["gold"]))
    w.setze(0, ytop + 1, 0, w.b(d["feuer"], lit=True, signal_fire=True, facing="north", waterlogged=False))
    for k in range(ytop - 1):
        r = B0 - k * (B0 - 3) // (ytop - 1) + 1
        for x in (-1, 0, 1):
            w.setze(x, 1 + k, r, treppe(w, "polished_blackstone_brick", "north"))
    hohl(w, 3)
    return w


def riesenschmiede(seed, g=2):
    """Riesenschmiede: Halle aus Schwarzstein mit Esse aus Magma, gigantischem Amboss, Hammer-Statue,
    Kühlbecken und Schlackenhalde."""
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    a, b = _r(9 * u + 4), _r(6 * u + 3, 4)
    gelaende(w, a + 8, art="asche", dichte=0.4)
    st = P.Stil(w, wand="schwarzstein", sockel="tiefenschiefer", gesims="polished_blackstone_brick", dach="nether",
                holz="crimson", laeden=False, fenster="orange_stained_glass_pane", licht="lantern")
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=_r(8 * u + 4, 6), dach="sattel", tuer="south", kamine=0,
               gauben=False, pilaster=3)
    for y in range(1, _r(18 * u + 8)):
        for x in range(a - 3, a):
            for z in range(-2, 1):
                w.setze(x, y, z, w.b("bricks") if (x + y + z) % 4 else w.b("nether_bricks"))
    w.setze(a - 2, _r(18 * u + 8), -1, w.b(d["feuer"], lit=True, signal_fire=True, facing="north", waterlogged=False))
    for x in range(a - 4, a - 1):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("magma_block") if (x + z) % 2 else w.b(d["glut"]))
    S = Skulptur(w, 1.0 * u + 0.3)
    S.mat("e", bl(w, "netherite_block" if False else "anvil"))
    S.mat("i", sk(Mat(w, ["iron_block", "polished_andesite", "iron_block"]), 0, 6))
    S.plus(lambda X, Y, Z: (np.abs(X) < 4 - (Y < 2) * 1.5 - (np.abs(Y - 2.5) < 1) * 2) & (Y >= 0) & (Y < 4.5)
           & (np.abs(Z) < 1.6 - (Y < 2) * 0.4), "i")
    S.plus(kap((-4, 4, 0), (-6, 3.6, 0), 1.0, 0.3), "i")
    S.rendern((-7, -1, -3), (6, 5, 3), versatz=(-1.5, 1.01, 0.5))
    hohl(w, 2)
    return w


def basaltfeld(seed, g=1):
    """Basaltsäulenfeld: sechseckige Säulen unterschiedlicher Höhe wie Orgelpfeifen, dazwischen Magma."""
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    R = _r(12 * u + 5)
    r_n = Rauschen(w, 4)
    rng = w.rng
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            dd = math.hypot(x, z) / R
            if dd > 1:
                continue
            zelle = ((x + (z // 2) % 2) // 2, z // 2)
            hh = int((1 - dd) ** 0.7 * (4 + 14 * u) * (0.4 + 0.6 * r_n(zelle[0] * 2, 0, zelle[1] * 2)))
            for y in range(0, hh + 1):
                w.setze(x, y, z, w.b("basalt", axis="y") if (zelle[0] + zelle[1]) % 3 else
                        w.b("polished_basalt", axis="y"))
            if hh < 2 and rng.random() < 0.2:
                w.setze(x, 0, z, w.b(d["ader"]))
    hohl(w, 2)
    return w


def obsidianturm(seed, g=2):
    """Obsidianturm: schwarzer Spitzturm mit Glutfenstern, Dornenkränzen und weinendem Obsidian."""
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    st = P.Stil(w, wand=["obsidian", "crying_obsidian", "obsidian", "blackstone", "obsidian"], sockel="schwarzstein",
                gesims="polished_blackstone_brick", dach="schwarz", holz="crimson", laeden=False,
                fenster="orange_stained_glass_pane" if _stil(seed) == 0 else "cyan_stained_glass_pane")
    gelaende(w, _r(10 * u + 5), art="asche", dichte=0.5)
    H = _r(30 * u + 10)
    P.turm(w, st, 0, 0, 1, H, max(2.5, 3.5 * u), form="achteck", dach="nadel", fenster=7, fahne=None)
    for y in range(8, H, 9):
        for x, z in kreisrand(max(2.5, 3.5 * u) + 1.5):
            if (x + z) % 2 == 0:
                w.setze(x, y, z, w.b("pointed_dripstone", vertical_direction="up", thickness="tip", waterlogged=False)
                        if False else w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                                          west="none", waterlogged=False))
    hohl(w, 2)
    return w


def glutbaum(seed, g=1):
    """Glutbaum: verkohlter Riesenbaum mit glühenden Rissen und Pilzlicht-Früchten."""
    import baeume as B
    w = _welt(seed)
    d = _vk(w, seed)
    baum = B.ARTEN["toter_baum"][1](seed, min(2, g))
    einfuegen(w, baum, 0, 0, 0)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if "log" in n or "wood" in n:
            r = rng.random()
            w.bloecke[(x, y, z)] = w.b("basalt", axis="y") if r < 0.4 else w.b("blackstone") if r < 0.7 else \
                w.b(d["ader"]) if r < 0.85 else w.b("polished_basalt", axis="y")
            if w.frei(x, y - 1, z) and rng.random() < 0.06:
                w.setze(x, y - 1, z, w.b(d["glut"]))
    gelaende(w, _r(10 * U[g] + 4), art="asche", dichte=0.5)
    return w


def magmabruecke(seed, g=2):
    """Magmabrücke: Steinbrücke über einen Lavagraben, Geländer aus Ketten zwischen Feuerpfeilern."""
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    L = _r(14 * u + 6)
    B = 2
    gelaende(w, L + 4, art="asche", dichte=0.4)
    for x in range(-L - 3, L + 4):
        for z in range(-L // 2, L // 2 + 1):
            if abs(z) < L // 2 - 1:
                w.setze(x, 0, z, w.b("magma_block") if (x + z) % 3 else w.b(d["glut"]))
                w.setze(x, -1, z, w.b("magma_block"))
    for z in range(-L, L + 1):
        y = 2 + int(4 * u * math.cos(z / L * math.pi / 2))
        for x in range(-B - 1, B + 2):
            w.setze(x, y, z, d["B"](x, y, z, 0.5))
            w.setze(x, y - 1, z, d["B"](x, y, z, 0.3))
        if z % 5 == 0:
            for sx in (-B - 1, B + 1):
                for yy in range(y + 1, y + 4):
                    w.setze(sx, yy, z, d["B"](sx, yy, z, 0.8))
                w.setze(sx, y + 4, z, w.b(d["feuer"], lit=True, signal_fire=False, facing="north", waterlogged=False))
        else:
            for sx in (-B - 1, B + 1):
                w.setze(sx, y + 2, z, w.b("chain", axis="z", waterlogged=False))
    hohl(w, 2)
    return w


def aschestadt(seed, g=2):
    """Aschestadt: verschüttete Häuser einer Stadt am Vulkan, nur Dächer und Mauerkronen ragen aus der Asche."""
    import haeuser as H
    w = _welt(seed)
    u = U[g]
    rng = w.rng
    for i in range(3 + g):
        hw = H.HAEUSER[["fachwerkhaus", "kaufmannshaus", "taverne", "schmiede", "gildenhaus"][i % 5]][1](seed + i, 1)
        x0, z0 = int((rng.random() - 0.5) * 30 * u), int((rng.random() - 0.5) * 30 * u)
        einfuegen(w, hw, x0, 0, z0)
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if "leaves" in n or "flower" in n or n.endswith(("grass", "poppy", "dandelion", "fern")):
            del w.bloecke[(x, y, z)]
    r_n = Rauschen(w, 6)
    R = _r(24 * u + 8)
    for x, z in scheibe(R):
        hh = int((0.4 + 0.5 * r_n(x, 0, z)) * 7 * u)
        for y in range(0, hh + 1):
            w.setze(x, y, z, w.b(["tuff", "gravel", "smooth_basalt", "light_gray_concrete_powder" if False else "andesite"]
                                 [int(r_n(x, y * 3, z) * 3.99)]), ueberschreiben=y < hh * 0.6)
    hohl(w, 2)
    return w


def drachennest(seed, g=2):
    """Feuerdrachen-Nest: Krater aus Basalt mit Knochen, drei Dracheneiern aus Magma und Gold auf Glut."""
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    R = 8 * u + 4
    for x, z in scheibe(R + 3):
        dd = math.hypot(x, z)
        hh = int(max(0, 4 * u * (1 - abs(dd - R) / 3)))
        for y in range(0, hh + 1):
            w.setze(x, y, z, d["G"](x, y, z, y / 5))
        if dd < R - 1:
            w.setze(x, 0, z, w.b("magma_block") if (x + z) % 2 else w.b("netherrack"))
    for i, (x, z) in enumerate(((0, 0), (2, 1), (-1, 2))):
        h = int(3 * u) + 2
        for y in range(1, h + 1):
            r = 1.2 * u * math.sin(math.pi * y / (h + 1)) + 0.4
            for xx, zz in scheibe(r, x, z):
                w.setze(xx, y, zz, w.b(["magma_block", "gold_block", "orange_terracotta"][(i + y) % 3]))
    for i in range(int(6 * u) + 2):
        a = w.rng.random() * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8)
        for k in range(3):
            w.setze(x + k, 1, z, w.b("bone_block", axis="x"))
    gelaende(w, _r(R + 8), art="asche", dichte=0.4)
    hohl(w, 2)
    return w


def feuerkristalle(seed, g=2):
    """Feuerkristalle: orange und rot glühende Kristallsäulen aus einer Basaltspalte."""
    from weltwunder2 import _kristall
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    farben = ["shroomlight", "orange_stained_glass", "red_stained_glass", "magma_block"] if _stil(seed) == 0 else \
        ["sea_lantern", "cyan_stained_glass", "light_blue_stained_glass", "crying_obsidian"]
    v = Verlauf(w, "FK", farben)
    S = Skulptur(w, 1.0)
    S.mat("k", lambda x, y, z, lx, ly, lz: v(min(3, (ly / (20 * u)) * 3 + (w.rng.random() - 0.5)), x, y, z))
    rng = w.rng
    for i in range(7 + g * 2):
        a = rng.random() * 2 * math.pi
        nei = 0.1 + rng.random() * 0.5
        L = (8 + rng.random() * 16) * u
        st = (math.cos(a) * 2 * u, -2, math.sin(a) * 2 * u)
        _kristall(S, st, (st[0] + math.cos(a) * math.sin(nei) * L, L * math.cos(nei), st[2] + math.sin(a) * math.sin(nei) * L),
                  (1 + rng.random() * 1.6) * u, "k")
    S.rendern((-20 * u, -3, -20 * u), (20 * u, 25 * u, 20 * u))
    for x, z in scheibe(9 * u + 3):
        for y in range(0, 3):
            if math.hypot(x, z) + y * 2 < 9 * u + 3:
                w.setze(x, y, z, d["G"](x, y, z, 0.3))
    gelaende(w, _r(12 * u + 4), art="asche", dichte=0.4)
    hohl(w, 2)
    return w


def feuerdaemon(seed, g=2):
    """Feuerdämon-Statue: gehörnter Riese aus Basalt mit glühender Brust, Flammenpeitsche und Schwingen."""
    from motive import figur
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    S = Skulptur(w, 1.5 * u + 0.4)
    S.mat("k", sk(Mat(w, ["blackstone", "basalt", "polished_blackstone", "gilded_blackstone"]), 0, 30 * u))
    S.mat("a", bl(w, d["ader"]))
    S.mat("d", bl(w, "obsidian"))
    S.mat("g", bl(w, d["glut"]))
    kopf = figur(S, "ork", "arme_hoch", y0=0)
    S.plus(ell(0, 10, 1.8, 1.5, 1.8, 0.6), "g")
    for sx in (-1, 1):
        S.plus(kap((sx * 1.2, kopf - 1.5, 0), (sx * 3.5, kopf + 1.5, -1), 0.6, 0.15), "d")
        S.plus(kap((sx * 2, 12, -1.5), (sx * 9, 17, -3), 0.5, 0.25), "k")
        S.plus(lambda X, Y, Z, sx=sx: (sx * X > 2) & (sx * X < 9) & (Y > 6) & (Y < 17 - (sx * X - 2) * 0.1)
               & (np.abs(Z + 1.5 + (sx * X - 2) * 0.2) < 0.3) & (Y > 17 - (sx * X - 2) * 1.4), "a")
    S.rendern((-10, -1, -6), (10, kopf + 4, 6), versatz=(0.5, 2.01, 0.5))
    for x, z in scheibe(5 * u + 2):
        w.setze(x, 1, z, d["B"](x, 1, z, 0.4))
    gelaende(w, _r(10 * u + 4), art="asche", dichte=0.4)
    hohl(w, 2)
    return w


def geysirfeld(seed, g=1):
    """Geysirfeld: Sinterterrassen in Gelb und Weiß, dampfende Löcher (Lagerfeuer unter Wasser), Schwefelfelder."""
    w = _welt(seed)
    u = U[g]
    rng = w.rng
    R = _r(12 * u + 5)
    r_n = Rauschen(w, 3)
    for x, z in scheibe(R):
        v = r_n(x, 0, z)
        w.setze(x, 0, z, w.b("yellow_terracotta") if v < 0.3 else w.b("white_terracotta") if v < 0.5 else
                w.b("calcite") if v < 0.7 else w.b("orange_terracotta") if v < 0.8 else w.b("tuff"))
    for i in range(3 + g * 2):
        a = rng.random() * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.6 * rng.random()), round(math.sin(a) * R * 0.6 * rng.random())
        for dx, dz in ((0, 0), (1, 0), (0, 1), (1, 1)):
            w.setze(x + dx, 0, z + dz, w.b("water", level=0))
            w.setze(x + dx, -1, z + dz, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
        for xx, zz in kreisrand(2.2, x, z):
            w.setze(xx, 1, zz, w.b("calcite"))
    gelaende(w, R + 4, art="stein", dichte=0.3)
    return w


def vulkanobservatorium(seed, g=1):
    """Vulkanobservatorium: Forschungsturm aus Basalt mit Glaskuppel, Messinstrumenten und Blitzableiter."""
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    st = P.Stil(w, wand="tiefenschiefer", sockel="schwarzstein", gesims="deepslate_brick", dach="kupfer",
                holz="dark_oak", laeden=False)
    gelaende(w, _r(10 * u + 5), art="asche", dichte=0.4)
    H = _r(16 * u + 6)
    P.turm(w, st, 0, 0, 1, H, max(2.5, 3.5 * u), dach="platt", fenster=6)
    kuppel(w, w.b("glass"), 0, 0, H + 2, max(2.5, 3.5 * u), form="rund", spitze=None)
    w.setze(0, H + 2, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for y in range(H + 2, H + 2 + _r(6 * u + 4)):
        w.setze(0, y, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    hohl(w, 2)
    return w


def schlackenmine(seed, g=2):
    """Schlackenmine: Stolleneingang in einer Halde, Förderturm mit Seilrad, Loren-Gleise und Erzhaufen."""
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    R = _r(10 * u + 5)
    for x, z in scheibe(R):
        hh = int(6 * u * (1 - math.hypot(x, z) / R)) + 1
        for y in range(0, hh + 1):
            w.setze(x, y, z, d["G"](x, y, z, y / 6))
    for y in range(1, 5):
        for x in (-1, 0, 1):
            for z in range(R - 4, R + 1):
                w.bloecke.pop((x, y, z), None)
    for z in range(R - 4, R + 8):
        w.setze(0, 1, z, w.b("rail", shape="north_south", waterlogged=False))
        w.setze(0, 0, z, w.b("gravel"))
    for y in range(1, 5):
        for x in (-2, 2):
            w.setze(x, y, R, w.b("dark_oak_log", axis="y"))
    for x in range(-2, 3):
        w.setze(x, 5, R, w.b("dark_oak_log", axis="x"))
    for y in range(int(6 * u) + 1, int(6 * u) + 12):
        for sx in (-2, 2):
            w.setze(sx, y, 0, w.b("dark_oak_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    for x, y in [(x, y) for x in range(-3, 4) for y in range(-3, 4) if 2 < math.hypot(x, y) < 3.6]:
        w.setze(x, int(6 * u) + 12 + y, 0, w.b("iron_block") if (x + y) % 2 else w.b("chain", axis="y", waterlogged=False))
    for k in range(3):
        w.setze(4 + k, 1, R + 4, w.b(["iron_ore", "gold_ore", "copper_ore"][k]))
    hohl(w, 2)
    return w


def lavainsel(seed, g=2):
    """Lavasee mit Insel: Basaltinsel mit Wachposten mitten in einem Lavasee, Steg aus Schwarzstein."""
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    R = _r(14 * u + 5)
    r_n = Rauschen(w, 4)
    for x, z in scheibe(R):
        if math.hypot(x, z) / R < 0.85 + 0.25 * r_n(x, 0, z):
            w.setze(x, 0, z, w.b("lava", level=0) if _stil(seed) == 0 else w.b("magma_block"))
            w.setze(x, -1, z, w.b("magma_block"))
    for x, z in scheibe(R * 0.35):
        for y in range(0, 3):
            w.setze(x, y, z, d["G"](x, y, z, y / 3))
    P.turm(w, P.Stil(w, wand="schwarzstein", sockel="schwarzstein", gesims="polished_blackstone_brick", dach="nether",
                     holz="crimson", laeden=False), 0, 0, 3, _r(10 * u + 5), max(2.0, 2.6 * u), dach="kegel",
           fahne=["red_wool", "black_wool"])
    for z in range(int(R * 0.35), R + 3):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("polished_blackstone_bricks"))
    gelaende(w, R + 5, art="asche", dichte=0.4)
    hohl(w, 2)
    return w


def ascheruine(seed, g=2):
    """Verkohlte Festungsruine: geschwärzte Mauern, eingestürzte Türme, Glutnester und Rauchsäulen."""
    from burgen import burgruine
    w = burgruine(seed, g)
    d = _vk(w, seed)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if any(t in n for t in ("leaves", "grass", "fern", "flower", "moss", "vine", "poppy", "dandelion")):
            del w.bloecke[(x, y, z)]
        elif "log" in n or "planks" in n:
            w.bloecke[(x, y, z)] = w.b("basalt", axis="y")
        elif y >= 1:
            w.bloecke[(x, y, z)] = d["B"](x, y, z, 0.5) if rng.random() < 0.8 else w.b("cracked_polished_blackstone_bricks")
        else:
            w.bloecke[(x, y, z)] = w.b(["tuff", "gravel", "blackstone", "basalt"][int(rng.integers(4))])
    for (x, y, z), b in list(w.bloecke.items()):
        if w.frei(x, y + 1, z) and rng.random() < 0.01:
            w.setze(x, y + 1, z, w.b(d["feuer"], lit=True, signal_fire=True, facing="north", waterlogged=False))
    return w


def lavahoehle(seed, g=2):
    """Lavahöhle: Felshügel mit weitem Höhlenmaul, aus dem ein Lavastrom fließt, innen glühende Decke."""
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    R = 12 * u + 5
    S = Skulptur(w, 1.0)
    S.mat("f", lambda x, y, z, lx, ly, lz: d["G"](x, y, z, ly / R))
    S.plus(ell(0, 0, 0, R, R * 0.75, R), "f")
    S.minus(ell(0, 1, 0, R * 0.65, R * 0.45, R * 0.65))
    S.minus(ell(0, 1, R * 0.75, R * 0.35, R * 0.35, R * 0.45))
    S.rendern((-R - 1, 0, -R - 1), (R + 1, R, R + 1))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if w.frei(x, y - 1, z) and y > 2 and rng.random() < 0.08:
            w.setze(x, y, z, w.b(d["glut"]) if rng.random() < 0.5 else w.b(d["ader"]))
    lavastrom(w, d, [(0, 0, 0), (0, 0, int(R * 0.7)), (2, 0, int(R * 1.3)), (-1, 0, int(R * 1.8))], 1)
    gelaende(w, _r(R * 1.9), art="asche", dichte=0.4)
    hohl(w, 3)
    return w


def feuertor(seed, g=2):
    """Feuertor: zwei geböschte Basalttürme mit Glutfenstern, verbunden durch eine Brücke mit Fallgitter,
    davor Feuerschalen und eine Allee aus Obsidiansäulen."""
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    H = _r(14 * u + 6)
    hb = _r(3 * u + 2, 3)
    gelaende(w, _r(16 * u + 6), art="asche", dichte=0.4)
    for sx in (-1, 1):
        cx = sx * (hb + 4)
        for y in range(1, H + 1):
            r = hb - y // (H // 3 + 1) + 1
            for x in range(cx - r, cx + r + 1):
                for z in range(-r, r + 1):
                    if max(abs(x - cx), abs(z)) == r:
                        fen = y % 5 == 2 and (x == cx or z == 0)
                        w.setze(x, y, z, w.b(d["glas"]) if fen else d["B"](x, y, z, y / H))
        for x in range(cx - 2, cx + 3):
            for z in range(-2, 3):
                if (x + z) % 2 == 0 and max(abs(x - cx), abs(z)) == 2:
                    w.setze(x, H + 1, z, d["B"](x, H + 1, z, 1))
        w.setze(cx, H + 1, 0, w.b(d["feuer"], lit=True, signal_fire=True, facing="north", waterlogged=False))
    for x in range(-hb - 3, hb + 4):
        for y in range(_r(H * 0.6), _r(H * 0.6) + 3):
            for z in range(-2, 3):
                w.setze(x, y, z, d["B"](x, y, z, 0.7))
    for x in range(-hb - 1, hb + 2):
        for y in range(_r(H * 0.6) - 3, _r(H * 0.6)):
            w.setze(x, y, 2, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
    for z in range(5, _r(16 * u + 4), 4):
        for sx in (-hb - 2, hb + 2):
            for y in range(1, 5):
                w.setze(sx, y, z, w.b("obsidian") if y < 4 else w.b(d["feuer"], lit=True, signal_fire=False,
                                                                        facing="north", waterlogged=False))
    hohl(w, 2)
    return w


def glutschmelze(seed, g=2):
    """Glutschmelze: Hüttenwerk mit drei Hochöfen aus Backstein, Schmelzrinnen voller Glut, Erzbunkern,
    Förderbrücken und rauchenden Schloten."""
    w = _welt(seed)
    d = _vk(w, seed)
    u = U[g]
    gelaende(w, _r(16 * u + 6), art="asche", dichte=0.3)
    for i in range(3):
        cx = (i - 1) * _r(8 * u + 3, 6)
        H = _r((12 + 4 * (i % 2)) * u + 6)
        for y in range(1, H + 1):
            r = 3 * u * (1 - 0.35 * y / H) + 1
            for x, z in kreisrand(r, cx, 0):
                w.setze(x, y, z, w.b(["bricks", "nether_bricks", "bricks", "mud_bricks"][(x + y + z) % 4]))
        for y in range(H + 1, H + _r(6 * u + 3)):
            for x, z in kreisrand(1.2, cx, 0):
                w.setze(x, y, z, w.b("bricks"))
        w.setze(cx, H + _r(6 * u + 3), 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
        w.setze(cx, 1, round(3 * u + 1), w.b("blast_furnace", facing="south", lit=True))
    lavastrom(w, d, [(-_r(8 * u + 3, 6), 0, 5), (_r(8 * u + 3, 6), 0, 5)], 1)
    for k in range(4):
        w.setze(-_r(12 * u + 4) + k, 1, -5, w.b(["iron_ore", "raw_iron_block", "gold_ore", "raw_copper_block"][k]))
    hohl(w, 2)
    return w


VULKAN = {
    "vulkan": ("Vulkan", vulkan),
    "glutstrom": ("Glutstrom-Klippe", glutstrom),
    "feuertempel": ("Feuertempel", feuertempel),
    "riesenschmiede": ("Riesenschmiede", riesenschmiede),
    "basaltfeld": ("Basaltfeld", basaltfeld),
    "obsidianturm": ("Obsidianturm", obsidianturm),
    "glutbaum": ("Glutbaum", glutbaum),
    "magmabruecke": ("Magmabrücke", magmabruecke),
    "aschestadt": ("Verschüttete Aschestadt", aschestadt),
    "drachennest": ("Feuerdrachen-Nest", drachennest),
    "feuerkristalle": ("Feuerkristalle", feuerkristalle),
    "feuerdaemon": ("Feuerdämon-Statue", feuerdaemon),
    "geysirfeld": ("Geysirfeld", geysirfeld),
    "vulkanobservatorium": ("Vulkanobservatorium", vulkanobservatorium),
    "schlackenmine": ("Schlackenmine", schlackenmine),
    "lavainsel": ("Lavasee-Insel", lavainsel),
    "ascheruine": ("Verkohlte Ruine", ascheruine),
    "lavahoehle": ("Lavahöhle", lavahoehle),
    "feuertor": ("Feuertor", feuertor),
    "glutschmelze": ("Glutschmelze", glutschmelze),
}

from elemente2 import END, NETHER  # noqa: E402,F401

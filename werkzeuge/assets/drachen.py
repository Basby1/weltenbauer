"""Drachenhort (neu) – 20 Bauten: Drachenstatuen, Horste, Höhlen, Skelette, Tempel."""

from __future__ import annotations

import math

import numpy as np

import modbloecke as MB
import pracht as P
from lib import Rauschen, Verlauf, einfuegen, laub
from pracht import Mat, gelaende
from reiche import _drache
from skulptur import Skulptur, dreh_y, ell, kap, kreisrand, scheibe, spiegel_x
from spuk import knorrbaum, kerze, schaedel, spukboden
from weltwunder import bl, hohl, platz, sk

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


FARBEN = {
    "rot": (["nether_wart_block", "red_concrete", "red_terracotta", "red_nether_bricks", "nether_wart_block"],
            ["orange_terracotta", "yellow_terracotta", "smooth_sandstone"], "gold_block"),
    "gruen": (["dark_prismarine", "green_concrete", "green_terracotta", "waxed_oxidized_copper", "moss_block"],
              ["lime_terracotta", "yellow_terracotta", "end_stone"], "sea_lantern"),
    "schwarz": (["blackstone", "black_concrete", "polished_blackstone", "gray_concrete", "black_terracotta"],
                ["gray_terracotta", "purple_terracotta", "magenta_terracotta"], "crying_obsidian"),
    "gold": (["gold_block", "yellow_concrete", "orange_concrete", "raw_gold_block", "yellow_terracotta"],
             ["white_terracotta", "smooth_sandstone", "yellow_terracotta"], "redstone_block"),
    "blau": (["blue_concrete", "lapis_block", "blue_terracotta", "light_blue_concrete", "cyan_terracotta"],
             ["light_blue_terracotta", "white_concrete", "calcite"], "sea_lantern"),
    "eis": (["packed_ice", "blue_ice", "light_blue_concrete", "white_concrete", "ice"],
            ["snow_block", "white_concrete", "calcite"], "sea_lantern"),
    "bronze": (["waxed_copper_block", "raw_copper_block", "waxed_cut_copper", "orange_terracotta",
                "waxed_exposed_copper"], ["waxed_cut_copper", "smooth_sandstone", "yellow_terracotta"], "redstone_block"),
    "stein": (["stone", "andesite", "cobblestone", "tuff", "polished_andesite"],
              ["smooth_stone", "diorite", "calcite"], "shroomlight"),
}


def drachenmat(w, art):
    sch, bau, auge = FARBEN[art]
    S = Mat(w, sch, kontrast=1.0)
    B = Mat(w, bau, kontrast=0.7)
    return (lambda x, y, z, *_: S(x, y, z, 0.5), lambda x, y, z, *_: B(x, y, z, 0.5), w.b("bone_block", axis="y"),
            w.b(auge))


def _art(seed, liste):
    return liste[(seed // 7 + _stil(seed)) % len(liste)]


def drache_setzen(w, art, s, versatz, haltung="liegend", dreh=0.0, spiegel=False):
    S = Skulptur(w, s)
    sch, bau, horn, auge = drachenmat(w, art)
    _drache(w, S, sch, bau, horn, auge, haltung)
    R = dreh_y(dreh)
    if spiegel:
        R = R @ np.diag([1, 1, -1])
    S.rendern((-17, -1, -14), (13, 16, 14), versatz=versatz, dreh=R)


def felsen(w, R, H, mat=None, cx=0, cz=0, y0=0, rauh=0.35, spitz=1.0):
    """Organischer Felsen/Hügel (Höhenfeld mit Rauschen). Gibt Höhe-Funktion zurück."""
    mat = mat or Mat(w, ["stone", "andesite", "tuff", "cobblestone", "deepslate"], kontrast=1.2)
    r1 = Rauschen(w, 4)
    r2 = Rauschen(w, 1.5)
    hoehe = {}
    for x, z in scheibe(R, cx, cz):
        d = math.hypot(x - cx, z - cz) / R
        hh = H * max(0.0, 1 - d ** (2 / spitz)) * (1 - rauh + rauh * 2 * (0.7 * r1(x, 0, z) + 0.3 * r2(x, 0, z)))
        hh = int(hh)
        for y in range(y0, y0 + hh + 1):
            w.setze(x, y, z, mat(x, y, z, (y - y0) / max(1, H)))
        hoehe[(x, z)] = y0 + hh
    return hoehe


def verbrennen(w, anteil=0.4):
    """Brandspuren: Holz → verkohlt (Schwarzstein/Basalt), Gras → grobe Erde, etwas Feuer (Lagerfeuer)."""
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b).split(":")[-1]
        if rng.random() > anteil:
            continue
        if n.endswith("_planks") or n.endswith("_log"):
            w.bloecke[(x, y, z)] = w.b("polished_basalt", axis="y") if rng.random() < 0.5 else w.b("blackstone")
        elif n == "grass_block":
            w.bloecke[(x, y, z)] = w.b("coarse_dirt") if rng.random() < 0.6 else w.b("soul_soil")
        elif "leaves" in n:
            del w.bloecke[(x, y, z)]


def gold_haufen(w, cx, cz, R, H, y0=1):
    rng = w.rng
    for x, z in scheibe(R, cx, cz):
        d = math.hypot(x - cx, z - cz) / R
        hh = int(H * (1 - d * d) + rng.random() * 0.8)
        for y in range(y0, y0 + hh):
            r = rng.random()
            w.setze(x, y, z, w.b("gold_block") if r < 0.55 else w.b("raw_gold_block") if r < 0.8 else
                    w.b("yellow_concrete_powder") if r < 0.9 else w.b("gold_block"))
        if hh >= 0 and rng.random() < 0.08:
            w.setze(x, y0 + hh, z, w.b(["chest", "emerald_block", "diamond_block", "amethyst_cluster"][int(rng.integers(4))],
                                       **({"facing": "south", "type": "single", "waterlogged": False} if False else {}))
                    if False else w.b(["emerald_block", "diamond_block", "lapis_block", "redstone_block"][int(rng.integers(4))]))


# ============================================================================ Bauten


def drachenstatue(seed, g=2):
    """Liegender Drache mit gespreizten Flügeln, Rückenstacheln, Hörnern und leuchtenden Augen auf einem Felsen
    über einem Prunkplatz mit Feuerschalen."""
    w = _welt(seed)
    u = U[g]
    art = _art(seed, ["rot", "gruen", "bronze", "schwarz", "gold"])
    R = 8 * u + 5
    M = Mat(w, ["polished_blackstone_bricks", "polished_deepslate", "deepslate_tiles"] if _stil(seed) else
            ["stone_bricks", "polished_andesite", "smooth_stone"])
    yp = platz(w, _r(R + 3), M, rand="polished_blackstone_brick" if _stil(seed) else "stone_brick",
               lichter="campfire" if False else "lantern")
    felsen(w, R * 0.6, 2.5 * u + 1, y0=yp)
    drache_setzen(w, art, 0.95 * u, (0.5, yp + 2.5 * u + 1, 0.5))
    hohl(w, 2)
    return w


def drachennest(seed, g=1):
    """Drachennest auf einer Felsnadel: gewaltiges Nest aus Stämmen und Ästen, gefleckte Dracheneier, Knochen,
    Schuppen und Goldsplitter."""
    w = _welt(seed)
    u = U[g]
    R = 5 * u + 3
    gelaende(w, _r(R * 1.6 + 4), art="wiese", dichte=0.3)
    Hf = _r(8 * u + 3)
    felsen(w, R * 1.3, Hf, spitz=0.6, rauh=0.2)
    top = Hf
    rng = w.rng
    for i in range(int(50 * u) + 20):
        a = rng.random() * 2 * math.pi
        r = R * (0.75 + 0.35 * rng.random())
        y = top + 1 + int(rng.random() * 2.5 * u)
        lang = 3 + int(rng.random() * 3 * u)
        holz = ["spruce_log", "dark_oak_log", "oak_log", "stripped_spruce_log"][i % 4]
        for t in range(lang):
            aa = a + t * 0.6 / r
            w.setze(round(math.cos(aa) * r), y, round(math.sin(aa) * r),
                    w.b(holz, axis="x" if abs(math.sin(aa)) > 0.7 else "z"))
    for x, z in scheibe(R * 0.8):
        w.setze(x, top + 1, z, w.b("hay_block", axis="y") if (x + z) % 3 else w.b("coarse_dirt"))
    farben = [("red_terracotta", "yellow_terracotta"), ("green_terracotta", "lime_terracotta"),
              ("purple_terracotta", "magenta_terracotta"), ("blue_terracotta", "light_blue_terracotta"),
              ("black_terracotta", "gold_block")]
    for i in range(2 + g):
        a = i * 2.39996
        d = R * 0.45 * math.sqrt((i + 0.5) / (2 + g))
        cx, cz = math.cos(a) * d, math.sin(a) * d
        f1, f2 = farben[(i + seed) % len(farben)]
        S = Skulptur(w, max(0.7, u * 0.6))
        S.mat("e", lambda x, y, z, *_, f1=f1, f2=f2: w.b(f2) if (x * 3 + y * 5 + z) % 7 == 0 else w.b(f1))
        S.plus(lambda X, Y, Z: (X * X + Z * Z) / 1.6 ** 2 + ((Y - 1.8) / 2.2) ** 2 *
               np.where(Y > 1.8, 1.0, 1.4) <= 1, "e")
        S.rendern((-3, 0, -3), (3, 5, 3), versatz=(cx + 0.5, top + 2.01, cz + 0.5))
    for i in range(5):
        a = rng.random() * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        w.setze(x, top + 2, z, w.b("bone_block", axis=["x", "z"][i % 2]) if i % 2 else w.b("gold_block"))
    hohl(w, 2)
    return w


def hortgrotte(seed, g=2):
    """Hortgrotte: gewölbte Felshöhle, in deren offener Front ein Goldberg glänzt, auf dem ein Drache schläft;
    Truhen, Edelsteine, Tropfsteine und Knochen."""
    w = _welt(seed)
    u = U[g]
    R = 9 * u + 5
    fels = Mat(w, ["deepslate", "cobbled_deepslate", "tuff", "stone", "andesite"], kontrast=1.2)
    S = Skulptur(w, 1.0)
    S.mat("f", sk(fels, 0, R))
    r_n = Rauschen(w, 4)
    S.plus(lambda X, Y, Z: (X * X + (Y * 1.3) ** 2 + Z * Z < R * R) & (Y >= -1), "f")
    S.minus(lambda X, Y, Z: (X * X + (Y * 1.4) ** 2 + Z * Z < (R - 2.5) ** 2) & (Y >= 0))
    S.minus(lambda X, Y, Z: (Z > R * 0.3) & (np.abs(X) < R * 0.55 - Y * 0.3) & (Y >= 0))
    S.rendern((-R - 1, -2, -R - 1), (R + 1, R, R + 1), versatz=(0.5, 0.01, 0.5))
    for x, z in scheibe(R + 4):
        if (x, 0, z) not in w.bloecke:
            w.setze(x, 0, z, w.b("stone") if (x + z) % 3 else w.b("gravel"))
    gold_haufen(w, 0, -1, R * 0.55, 2.5 * u + 1)
    drache_setzen(w, _art(seed, ["rot", "gold", "schwarz", "gruen"]), 0.38 * u, (0.5, 2.5 * u + 1, -1.5),
                  dreh=0.6)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 3 and w.frei(x, y - 1, z) and rng.random() < 0.06 and "deepslate" in w.P.name(b) + "deepslate":
            w.setze(x, y - 1, z, w.b("pointed_dripstone", vertical_direction="down", thickness="tip",
                                     waterlogged=False))
    hohl(w, 3)
    return w


def drachenturm(seed, g=2):
    """Drachenhorst-Turm: hoher Basaltturm mit Landeplattform auf der Spitze, Kratzspuren, Brandflecken,
    ein Drache hockt auf dem Rand, Kette und Feuerschalen."""
    w = _welt(seed)
    u = U[g]
    R = 3 * u + 2.5
    H = _r(16 * u + 8)
    spukboden(w, _r(R + 10), dichte=0.5)
    st = P.Stil(w, wand="schwarzstein", sockel="schwarzstein", gesims="polished_blackstone_brick",
                dach="schwarz", holz="dark_oak", fenster="orange_stained_glass", laeden=False, blumen=0)
    P.turm(w, st, 0, 0, 1, H, R, dach="platt", krone=True, fenster=6, fahne=None)
    Rp = R + 2 + u
    for x, z in scheibe(Rp):
        w.setze(x, H + 1, z, w.b("polished_blackstone_bricks") if math.hypot(x, z) > Rp - 1 else
                w.b("smooth_basalt") if (x + z) % 3 else w.b("magma_block"))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x, z = round(math.cos(a) * Rp), round(math.sin(a) * Rp)
        for k in range(1, 4):
            w.setze(round(math.cos(a) * (Rp - k * 0.8)), H + 1 - k, round(math.sin(a) * (Rp - k * 0.8)),
                    w.b("polished_blackstone_bricks"))
        w.setze(x, H + 2, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)
                if i % 2 else w.b("polished_blackstone_brick_wall", up=True, north="none", south="none", east="none",
                                  west="none", waterlogged=False))
    drache_setzen(w, _art(seed, ["rot", "schwarz", "bronze", "gruen"]), 0.5 * u + 0.15,
                  (0.5, H + 2.01, 0.5), haltung="sitzend", dreh=0.8)
    verbrennen(w, 0.15)
    hohl(w, 2)
    return w


def schaedeltor(seed, g=2):
    """Drachenschädel-Tor: der gigantische Schädel eines Urdrachen als Eingang, Kiefer weit offen, Hörner,
    Zahnreihen aus Knochen, im Schlund Seelenfeuer."""
    w = _welt(seed)
    u = U[g]
    s = 0.7 * u + 0.3
    spukboden(w, _r(14 * s + 4), dichte=0.6)
    S = Skulptur(w, s)
    S.mat("k", lambda x, y, z, *_: w.b("bone_block", axis="y") if (x + 2 * y + z) % 5 else w.b("calcite"))
    S.mat("d", bl(w, "black_concrete"))
    S.mat("g", bl(w, "soul_lantern" if False else "sea_lantern"))
    # Schädeldecke
    S.plus(ell(0, 9, -3, 7, 5, 8), "k")
    S.minus(ell(0, 8.5, -3, 5.8, 3.8, 7))
    # Oberkiefer (Schnauze)
    S.plus(lambda X, Y, Z: (np.abs(X) < 4.5 - Z * 0.12) & (Y > 6) & (Y < 8 - Z * 0.05) & (Z > 2) & (Z < 14), "k")
    # Unterkiefer
    S.plus(lambda X, Y, Z: (np.abs(X) < 4.2 - Z * 0.1) & (Y > 0) & (Y < 1.5) & (Z > 0) & (Z < 13), "k")
    S.minus(lambda X, Y, Z: (np.abs(X) < 3.0 - Z * 0.1) & (Y > 0.5) & (Y < 7.2) & (Z > 1) & (Z < 13))
    for k in range(6):
        for sx in (-1, 1):
            z = 3 + k * 1.8
            x = sx * (3.6 - z * 0.1)
            S.plus(kap((x, 6.2, z), (x, 4.2, z + 0.2), 0.5, 0.15), "k")
            S.plus(kap((x, 1.4, z), (x, 3.0, z + 0.2), 0.45, 0.12), "k")
    for sx in (-1, 1):
        S.minus(ell(sx * 3.8, 10, 3, 1.6, 1.4, 1.6))
        S.plus(ell(sx * 3.8, 10, 2.2, 0.7, 0.7, 0.7), "g")
        S.plus(kap((sx * 5, 12, -6), (sx * 10, 17, -11), 1.4, 0.4), "k")
        S.plus(kap((sx * 6, 10, -8), (sx * 9, 6, -12), 1.0, 0.3), "k")
    S.rendern((-12, 0, -14), (12, 20, 15), versatz=(0.5, 1.01, 0.5))
    w.setze(0, 1, 0, w.b("soul_campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    hohl(w, 2)
    return w


def fliegender_drache(seed, g=2):
    """Fliegender Drache: aufgerichteter Drache mit gespreizten Schwingen auf einer gezackten Felssäule, als
    würde er gerade abheben; Geröll und verbrannter Boden."""
    w = _welt(seed)
    u = U[g]
    spukboden(w, _r(10 * u + 6), dichte=0.4)
    Hs = _r(7 * u + 3)
    felsen(w, 4 * u + 3, Hs, spitz=0.5, rauh=0.3, mat=Mat(w, ["blackstone", "basalt", "tuff", "deepslate"]))
    drache_setzen(w, _art(seed, ["gruen", "rot", "blau", "gold", "schwarz"]), 0.9 * u, (0.5, Hs - 1, 0.5),
                  haltung="sitzend", dreh=-0.4)
    verbrennen(w, 0.2)
    hohl(w, 2)
    return w


def drachenskelett(seed, g=2):
    """Drachenskelett: halb im Boden versunkene Gebeine eines Riesendrachen – Wirbelsäule, Rippenbögen,
    Flügelknochen, Schädel – wie eine Ausgrabungsstätte mit Zelt und Werkzeug."""
    w = _welt(seed)
    u = U[g]
    L = 18 * u + 8
    gelaende(w, _r(L * 0.75 + 4), art="sand" if _stil(seed) else "wiese", dichte=0.3)
    S = Skulptur(w, 1.0)
    S.mat("k", lambda x, y, z, *_: w.b("bone_block", axis="y") if (x + y) % 4 else w.b("calcite"))
    pts = [(-L * 0.6, 0.5, L * 0.12), (-L * 0.35, 1.0, -L * 0.05), (-L * 0.1, 1.5, 0), (L * 0.15, 1.6, 0),
           (L * 0.35, 1.3, L * 0.06), (L * 0.5, 1.0, L * 0.1)]
    for i in range(len(pts) - 1):
        S.plus(kap(pts[i], pts[i + 1], 0.55 + 0.25 * u * (1 - abs(i - 2) / 3), 0.5 + 0.2 * u), "k")
    rb = 2.5 * u + 1.5
    for k in range(5 + g * 2):
        x = -L * 0.12 + k * (L * 0.3 / (5 + g * 2)) - L * 0.05
        rr = rb * (1 - abs(k - (5 + g * 2) / 2) / ((5 + g * 2)))
        S.plus(lambda X, Y, Z, x=x, rr=rr: (np.abs(X - x) < 0.5) & (np.abs(np.sqrt((Y - 1.5) ** 2 + Z * Z) - rr) < 0.55)
               & (Y > -0.5), "k")
    hx, hy, hz = pts[-1]
    S.plus(ell(hx + 2.0 * u, 1.2, hz, 2.2 * u, 1.2 * u, 1.4 * u), "k")
    S.minus(ell(hx + 1.6 * u, 1.6 * u, hz + 0.6 * u, 0.5 * u, 0.5 * u, 0.5 * u))
    S.plus(kap((hx + 3.5 * u, 0.6, hz - 0.5), (hx + 5 * u, 0.6, hz - 0.4), 0.6 * u, 0.3 * u), "k")
    for sz in (-1, 1):
        a0 = (-L * 0.05, 1.5, 0)
        el = (-L * 0.05 - 2 * u, 1.0, sz * 6 * u)
        S.plus(kap(a0, el, 0.6, 0.45), "k")
        for f in range(3):
            S.plus(kap(el, (-L * 0.05 - (5 + 3 * f) * u, 0.5, sz * (7 + f * 1.5) * u), 0.35, 0.2), "k")
    S.rendern((-L, -1, -L * 0.6), (L, 4 * u + 4, L * 0.6), versatz=(0.5, 0.01, 0.5))
    rng = w.rng
    for i in range(6):
        x, z = int(rng.integers(-int(L * 0.6), int(L * 0.6))), int(rng.integers(-int(L * 0.4), int(L * 0.4)))
        if w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("bone_block", axis="x") if i % 2 else w.b("suspicious_sand", dusted=0)
                    if _stil(seed) else w.b("suspicious_gravel", dusted=0))
    xt = -_r(L * 0.6)
    for x in range(xt - 3, xt + 4):
        for z in range(-_r(L * 0.45) - 3, -_r(L * 0.45) + 2):
            hh = 3 - abs(z + _r(L * 0.45) + 0.5) * 0.8
            if hh > 0:
                w.setze(x, round(hh), z, w.b("white_wool") if x % 3 else w.b("light_gray_wool"))
    w.setze(xt, 1, -_r(L * 0.45), w.b("barrel", facing="up", open=False))
    return w


def verbrannte_burg(seed, g=2):
    """Verbrannte Burg: eine vom Drachen verwüstete Burgruine – geschwärzte Mauern, eingestürzte Dächer,
    Glut, Rauch; auf dem Bergfried thront der Drache."""
    from burgen import BURGEN
    namen = list(BURGEN)
    w = BURGEN[namen[(seed // 7) % len(namen)]][1](seed, max(1, g))
    rng = w.rng
    verbrennen(w, 0.45)
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if (("stairs" in n or "roof" in n or "copper" in n) and y > 6 and rng.random() < 0.5) or \
                ("glass" in n and rng.random() < 0.6):
            del w.bloecke[(x, y, z)]
        elif ("stairs" in n or "roof" in n or "copper" in n) and y > 6:
            w.bloecke[(x, y, z)] = w.b("blackstone_stairs", facing="north", half="bottom", shape="straight",
                                       waterlogged=False) if rng.random() < 0.6 else w.b("smooth_basalt")
        elif "brick" in n and rng.random() < 0.12:
            w.bloecke[(x, y, z)] = w.b("cracked_stone_bricks") if "stone" in n else w.b("blackstone")
    top = max(w.bloecke, key=lambda p: p[1])
    oben = [(x, z) for (x, y, z) in w.bloecke if y == top[1] - 1]
    cx = sum(p[0] for p in oben) / max(1, len(oben))
    cz = sum(p[1] for p in oben) / max(1, len(oben))
    ytop = max(y for (x, y, z) in w.bloecke if abs(x - cx) < 4 and abs(z - cz) < 4)
    U_ = U[g]
    drache_setzen(w, _art(seed, ["rot", "schwarz", "gold"]), 0.55 * U_ + 0.15, (cx + 0.5, ytop + 1.01, cz + 0.5),
                  haltung="sitzend", dreh=1.0)
    for (x, y, z) in list(w.bloecke):
        if y == 0 and rng.random() < 0.01 and w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    return w


def drachenhoehle(seed, g=2):
    """Drachenhöhle im Steilhang: Bergflanke mit riesigem, gezackten Höhlenmaul, tiefe Krallenspuren,
    Knochenhalde und Goldglanz im Dunkel."""
    w = _welt(seed)
    u = U[g]
    W = 14 * u + 6
    H = 12 * u + 6
    fels = Mat(w, ["stone", "andesite", "tuff", "deepslate", "cobblestone", "basalt"], kontrast=1.3)
    r_n = Rauschen(w, 4)
    for x in range(-_r(W), _r(W) + 1):
        for z in range(-_r(W * 0.8), _r(W * 0.3)):
            rand = 1 - abs(x) / W
            hh = H * min(1, (W * 0.3 - z) / (W * 0.4)) * (0.6 + 0.4 * rand) * (0.85 + 0.3 * r_n(x, 0, z))
            for y in range(0, int(hh) + 1):
                w.setze(x, y, z, fels(x, y, z, y / H))
            if hh > 2 and rand > 0.2:
                w.setze(x, int(hh) + 1, z, w.b("grass_block", snowy=False))
    mw = 4 * u + 3
    mh = 6 * u + 3
    for x in range(-_r(mw) - 1, _r(mw) + 2):
        for y in range(1, _r(mh) + 2):
            zack = 0.5 * math.sin(x * 1.7) + 0.5 * math.cos(y * 2.1)
            if (x / mw) ** 2 + ((y - 1) / mh) ** 2 < 1 + zack * 0.08:
                for z in range(-_r(W * 0.7), _r(W * 0.3) + 1):
                    w.bloecke.pop((x, y, z), None)
    for x, z in scheibe(mw * 0.8, 0, -_r(W * 0.25)):
        w.setze(x, 0, z, w.b("gravel") if (x + z) % 3 else w.b("coarse_dirt"))
    gold_haufen(w, 0, -_r(W * 0.4), mw * 0.7, 1.5 * u + 1)
    rng = w.rng
    for k in range(3):
        for y in range(2, _r(mh)):
            x = _r(mw) + 2 + k
            z = _r(W * 0.3) - int(H * 0.0)
            if (x, y, z - 1) in w.bloecke:
                w.bloecke[(x, y, z - 1)] = w.b("black_concrete") if (y + k) % 2 else w.b("blackstone")
    for i in range(8):
        x, z = int(rng.integers(-_r(mw) - 3, _r(mw) + 4)), _r(W * 0.3) + 1 + int(rng.integers(0, 4))
        w.setze(x, 1, z, w.b("bone_block", axis=["x", "y", "z"][i % 3]))
        w.setze(x, 0, z, w.b("coarse_dirt"))
    hohl(w, 3)
    return w


def eisdrache(seed, g=2):
    """Eisdrache: ein Drache aus Packeis und blauem Eis liegt auf einem Gletscherfelsen, Eiszapfen, Schnee,
    gefrorene Krieger (Rüstungsständer-Optik aus Eis)."""
    w = _welt(seed)
    u = U[g]
    R = 8 * u + 5
    gelaende(w, _r(R + 4), art="schnee", dichte=0.3)
    felsen(w, R * 0.7, 2.5 * u + 2, mat=Mat(w, ["packed_ice", "snow_block", "blue_ice", "stone", "snow_block"]))
    drache_setzen(w, "eis", 0.75 * u, (0.5, 2.5 * u + 2, 0.5), dreh=0.3)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 3 and w.frei(x, y - 1, z) and rng.random() < 0.05:
            w.setze(x, y - 1, z, w.b("ice"))
    hohl(w, 2)
    return w


def drachenhorst(seed, g=2):
    """Drachenreiter-Horst: Bergfestung mit hölzernen Landeplattformen an Felswänden, Sattelkammer,
    Fahnen, Fleischhaken, Treppen im Fels und ein ruhender Reitdrache."""
    w = _welt(seed)
    u = U[g]
    R = 10 * u + 5
    H = 12 * u + 6
    hoehe = felsen(w, R, H, spitz=0.8, rauh=0.25)
    gelaende(w, _r(R + 3), art="wiese", dichte=0.2)
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="mcw_rot", holz="spruce")
    top = max(hoehe.get((x, z), 0) for x in range(-2, 3) for z in range(-2, 3))
    P.turm(w, st, 0, 0, top + 1, _r(8 * u + 4), max(2.2, 2.4 * u), dach="kegel", krone=True, fahne="red")
    for i in range(2 + g):
        a = i / (2 + g) * 2 * math.pi + 0.4
        y = int(H * (0.35 + 0.45 * i / (2 + g)))
        cand = [(x, z) for (x, z), h in hoehe.items() if abs(h - y) <= 1]
        if not cand:
            continue
        best = max(cand, key=lambda p: (p[0] * math.cos(a) + p[1] * math.sin(a)))
        bx, bz = best
        L = _r(4 * u + 3)
        for k in range(L):
            for d in range(-2, 3):
                px = round(bx + math.cos(a) * k - math.sin(a) * d)
                pz = round(bz + math.sin(a) * k + math.cos(a) * d)
                w.setze(px, y, pz, w.b("spruce_planks") if (k + d) % 3 else w.b("stripped_spruce_log",
                                                                                 axis="x" if abs(math.cos(a)) > 0.7
                                                                                 else "z"))
            if k % 3 == 0:
                for sd in (-2, 2):
                    px = round(bx + math.cos(a) * k - math.sin(a) * sd)
                    pz = round(bz + math.sin(a) * k + math.cos(a) * sd)
                    for yy in range(y - 3, y):
                        w.setze(px, yy, pz, w.b("spruce_log", axis="y"))
        ex = round(bx + math.cos(a) * (L - 1))
        ez = round(bz + math.sin(a) * (L - 1))
        w.setze(ex, y + 1, ez, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                   waterlogged=False))
        w.setze(ex, y + 2, ez, MB.fahne(w, ["red", "yellow", "black"][i % 3], "north"))
    drache_setzen(w, _art(seed, ["rot", "bronze", "blau", "gruen"]), 0.3 * u + 0.1, (6.5, hoehe.get((6, 0), H) + 1.01,
                                                                                      0.5), dreh=2.0)
    hohl(w, 3)
    return w


def schlangendrachen_tempel(seed, g=2):
    """Drachentempel des Ostens: Pagode mit roten Säulen, um die sich ein langer schlangenartiger Drache mit
    Mähne und Barteln windet; Steinlaternen und Torii."""
    from fernost import Ost, steinlaterne, torii
    from fernost import FERNOST
    w = FERNOST["pagode"][1](seed, g) if "pagode" in FERNOST else _welt(seed)
    u = U[g]
    S = Skulptur(w, 1.0)
    art = "gold" if _stil(seed) == 0 else "gruen"
    sch, bau, horn, auge = drachenmat(w, art)
    S.mat("s", sch)
    S.mat("b", bau)
    S.mat("h", horn)
    S.mat("a", auge)
    S.mat("m", bl(w, "red_wool" if art == "gold" else "white_wool"))
    R = 6 * u + 3
    H = 14 * u + 6
    n = 60
    pts = []
    for i in range(n + 1):
        t = i / n
        a = t * 2.5 * 2 * math.pi
        pts.append((math.cos(a) * R, 1 + t * H, math.sin(a) * R))
    rad = 0.9 * u + 0.4
    for i in range(n):
        S.plus(kap(pts[i], pts[i + 1], rad * (0.5 + 0.5 * min(1, i / 10)), rad * (0.5 + 0.5 * min(1, (i + 1) / 10))),
               "s")
        if i % 3 == 0:
            x, y, z = pts[i]
            S.plus(ell(x, y + rad * 0.9, z, rad * 0.35, rad * 0.5, rad * 0.35), "m")
    hx, hy, hz = pts[-1]
    S.plus(ell(hx, hy + rad * 0.5, hz, rad * 1.6, rad * 1.1, rad * 1.3), "s")
    S.plus(ell(hx - rad * 1.2, hy + rad * 0.2, hz + rad * 0.8, rad * 1.0, rad * 0.6, rad * 0.9), "b")
    for sz in (-1, 1):
        S.plus(kap((hx, hy + rad * 1.2, hz + sz * rad * 0.6), (hx + rad * 1.5, hy + rad * 3.0, hz + sz * rad * 1.2),
                   rad * 0.25, rad * 0.1), "h")
        S.plus(ell(hx - rad * 0.4, hy + rad * 0.9, hz + sz * rad * 0.8, rad * 0.25, rad * 0.25, rad * 0.25), "a")
    S.rendern((-R - 4 * rad, 0, -R - 4 * rad), (R + 4 * rad, H + 6 * rad, R + 4 * rad), versatz=(0.5, 0.01, 0.5),
              ueberschreiben=False)
    hohl(w, 2)
    return w


def lindwurm(seed, g=2):
    """Lindwurm: ein gewaltiger, flügelloser Wurm, der sich in drei Bögen aus dem Boden windet – Kopf mit
    Hörnerkranz, Rückenkamm, aufgewühlte Erde an den Austrittsstellen."""
    w = _welt(seed)
    u = U[g]
    L = 18 * u + 8
    gelaende(w, _r(L * 0.7 + 4), art="wald", dichte=0.4)
    art = _art(seed, ["gruen", "bronze", "schwarz", "rot"])
    sch, bau, horn, auge = drachenmat(w, art)
    S = Skulptur(w, 1.0)
    S.mat("s", sch)
    S.mat("b", bau)
    S.mat("h", horn)
    S.mat("a", auge)
    rad = 1.5 * u + 0.7
    A = 5 * u + 2
    n = 80
    pts = []
    for i in range(n + 1):
        t = i / n
        x = -L * 0.6 + t * L * 1.1
        y = math.sin(t * 3 * math.pi) * A + rad * 0.3
        z = math.sin(t * 2 * math.pi) * L * 0.12
        pts.append((x, y, z))
    for i in range(n - 6):
        S.plus(kap(pts[i], pts[i + 1], rad, rad), "s")
        x, y, z = pts[i]
        if i % 3 == 0 and y > 0:
            S.plus(kap((x, y + rad * 0.8, z), (x - rad * 0.4, y + rad * 1.8, z), rad * 0.3, rad * 0.05), "h")
    hx, hy, hz = pts[n - 6]
    hy = max(hy, rad * 2) + rad
    S.plus(kap(pts[n - 6], (hx + rad, hy, hz), rad, rad * 0.9), "s")
    S.plus(ell(hx + rad * 2.2, hy + rad * 0.2, hz, rad * 1.8, rad * 1.0, rad * 1.1), "s")
    S.plus(ell(hx + rad * 2.4, hy - rad * 0.4, hz, rad * 1.6, rad * 0.35, rad * 0.9), "b")
    for sz in (-1, 1):
        S.plus(ell(hx + rad * 2.6, hy + rad * 0.6, hz + sz * rad * 0.7, rad * 0.25, rad * 0.25, rad * 0.25), "a")
        for k in range(3):
            S.plus(kap((hx + rad * 1.4, hy + rad * 0.8, hz + sz * rad * 0.6),
                       (hx - rad * (0.5 + k * 0.6), hy + rad * (1.6 + k * 0.4), hz + sz * rad * (1.4 + k * 0.5)),
                       rad * 0.3, rad * 0.08), "h")
    S.rendern((-L, -rad - 2, -L * 0.5), (L, A + rad * 6, L * 0.5), versatz=(0.5, 0.01, 0.5))
    for i in range(n):
        x, y, z = pts[i]
        if abs(y) < rad * 0.6:
            for xx, zz in scheibe(rad + 1.5, round(x), round(z)):
                if w.frei(xx, 1, zz):
                    w.setze(xx, 1, zz, w.b("coarse_dirt") if (xx + zz) % 2 else w.b("rooted_dirt"))
    hohl(w, 2)
    return w


def dracheneischrein(seed, g=1):
    """Schrein des Dracheneis: Stufenaltar mit einem riesigen schimmernden Ei in einer Goldschale, vier Feuersäulen,
    Runenpflaster und Schutzketten."""
    w = _welt(seed)
    u = U[g]
    R = 5 * u + 4
    M = Mat(w, ["polished_deepslate", "deepslate_tiles", "polished_blackstone_bricks"] if _stil(seed) else
            ["smooth_sandstone", "cut_sandstone", "chiseled_sandstone"])
    yp = platz(w, _r(R + 2), M, rand="deepslate_brick" if _stil(seed) else "sandstone", lichter="lantern")
    for k in range(3):
        for x, z in scheibe(R * 0.5 - k):
            w.setze(x, yp + k, z, M(x, yp + k, z, 0.5 + k * 0.1))
    yo = yp + 3
    for x, z in scheibe(1.8):
        w.setze(x, yo, z, w.b("gold_block"))
    f1, f2 = [("purple_terracotta", "magenta_terracotta"), ("black_terracotta", "crying_obsidian"),
              ("red_terracotta", "orange_terracotta"), ("green_terracotta", "emerald_block")][(seed // 7) % 4]
    s = 0.8 * u + 0.4
    S = Skulptur(w, s)
    S.mat("e", lambda x, y, z, *_: w.b(f2) if (x * 3 + y * 5 + z) % 6 == 0 else w.b(f1))
    S.plus(lambda X, Y, Z: (X * X + Z * Z) / 2.2 ** 2 + ((Y - 2.5) / 3.0) ** 2 * np.where(Y > 2.5, 1.0, 1.5) <= 1, "e")
    S.rendern((-3, 0, -3), (3, 6, 3), versatz=(0.5, yo + 0.51, 0.5))
    for i in range(4):
        a = i / 4 * 2 * math.pi + math.pi / 4
        x, z = round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8)
        for y in range(yp, yp + 4 + g):
            w.setze(x, y, z, w.b("polished_basalt", axis="y"))
        w.setze(x, yp + 4 + g, z, w.b("magma_block"))
        w.setze(x, yp + 5 + g, z, w.b("fire") if False else w.b("campfire", lit=True, signal_fire=False,
                                                                  facing="north", waterlogged=False))
    hohl(w, 2)
    return w


def vulkanhort(seed, g=2):
    """Vulkanhort: kleiner rauchender Vulkankegel mit Lavarinnen und Krater; am Kraterrand ein schwarzer Drache,
    Obsidiansplitter und Magmaadern."""
    w = _welt(seed)
    u = U[g]
    R = 11 * u + 6
    H = 9 * u + 5
    gelaende(w, _r(R + 3), art="asche", dichte=0.5)
    mat = Mat(w, ["basalt", "blackstone", "tuff", "smooth_basalt", "magma_block", "blackstone"], kontrast=1.3)
    hoehe = felsen(w, R, H, mat=mat, spitz=1.3, rauh=0.2)
    Rk = R * 0.3
    for x, z in scheibe(Rk):
        h = hoehe.get((x, z), 0)
        for y in range(int(H * 0.6), h + 1):
            w.bloecke.pop((x, y, z), None)
        w.setze(x, int(H * 0.6), z, w.b("lava", level=0))
    for k in range(3):
        a = k * 2.1 + 0.4
        for t in np.linspace(Rk, R, int(R * 2)):
            x, z = round(math.cos(a) * t), round(math.sin(a) * t)
            h = hoehe.get((x, z), 0)
            w.setze(x, h, z, w.b("magma_block") if (x + z) % 3 else w.b("lava", level=0) if False else
                    w.b("magma_block"))
    xr = round(Rk + 1)
    drache_setzen(w, _art(seed, ["schwarz", "rot", "gold"]), 0.35 * u + 0.1,
                  (xr + 0.5, hoehe.get((xr, 0), H) + 1.01, 0.5), haltung="sitzend", dreh=math.pi)
    for i in range(6 + 2 * g):
        a = w.rng.random() * 2 * math.pi
        d = R * (0.6 + 0.4 * w.rng.random())
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        h = hoehe.get((x, z), 0)
        for y in range(h + 1, h + 3 + int(w.rng.integers(0, 3))):
            w.setze(x, y, z, w.b("obsidian") if y % 2 else w.b("crying_obsidian"))
    hohl(w, 3)
    return w


def drachenbruecke(seed, g=2):
    """Drachenbrücke: steinerne Bogenbrücke über eine Schlucht, an beiden Enden thronen Drachenköpfe als
    Brückenwächter, Laternen in den Mäulern."""
    w = _welt(seed)
    u = U[g]
    L = 14 * u + 6
    B = 2 + (g >= 2)
    fels = Mat(w, ["stone", "andesite", "tuff", "cobblestone"], kontrast=1.2)
    for x in range(-_r(L) - 8, _r(L) + 9):
        for z in range(-_r(L * 0.6), _r(L * 0.6) + 1):
            if abs(x) > L * 0.75:
                for y in range(-6, 1):
                    w.setze(x, y, z, fels(x, y, z, (y + 6) / 7))
                w.setze(x, 1, z, w.b("grass_block", snowy=False))
            else:
                w.setze(x, -6, z, w.b("water", level=0))
    M = Mat(w, ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "polished_andesite"])
    for x in range(-_r(L), _r(L) + 1):
        bog = -6 + (1 - (x / (L * 0.8)) ** 2) * 6.5 if abs(x) < L * 0.8 else 1
        for z in range(-B, B + 1):
            for y in range(round(bog), 2):
                w.setze(x, y, z, M(x, y, z, 0.5))
            w.setze(x, 1, z, w.b("polished_andesite") if (x + z) % 2 else w.b("stone_bricks"))
        for z in (-B - 1, B + 1):
            w.setze(x, 2, z, w.b("stone_brick_wall", up=x % 3 == 0, north="none", south="none", east="low", west="low",
                                 waterlogged=False))
    for sx in (-1, 1):
        S = Skulptur(w, 0.4 * u + 0.2)
        art = _art(seed, ["stein", "bronze", "gold"])
        sch, bau, horn, auge = drachenmat(w, art)
        S.mat("s", sch)
        S.mat("b", bau)
        S.mat("h", horn)
        S.mat("a", auge)
        S.plus(kap((0, 0, 0), (0, 9, 0), 3.0, 2.4), "s")
        S.plus(ell(1.8, 11, 0, 3.6, 2.4, 2.4), "s")
        S.plus(ell(4.4, 10.2, 0, 2.4, 1.2, 1.6), "s")
        S.plus(ell(4.0, 8.9, 0, 2.2, 0.6, 1.4), "b")
        for sz in (-1, 1):
            S.plus(ell(3.0, 12.0, sz * 1.5, 0.5, 0.5, 0.5), "a")
            S.plus(kap((0.8, 12.8, sz * 1.2), (-3.0, 16.0, sz * 2.4), 0.6, 0.15), "h")
        S.rendern((-5, 0, -5), (8, 18, 5), versatz=(sx * (L + 2) + 0.5, 2.01, sx * (B + 3) + 0.5),
                  dreh=dreh_y(0 if sx < 0 else math.pi) @ dreh_y(math.pi / 2 * sx * 0))
    hohl(w, 2)
    return w


def drachenbrunnen(seed, g=1):
    """Drachenbrunnen: Prunkbecken mit einem sich aufbäumenden Drachen in der Mitte, der aus dem Maul Wasser
    speit; Becken aus Prismarin oder Kupfer."""
    w = _welt(seed)
    u = U[g]
    R = 6 * u + 4
    gelaende(w, _r(R + 5), art="wiese", dichte=0.2)
    rand = "prismarine_brick" if _stil(seed) else "stone_brick"
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("prismarine_bricks") if _stil(seed) else w.b("smooth_stone"))
        w.setze(x, 1, z, w.b("water", level=0))
    for x, z in kreisrand(R + 0.5):
        w.setze(x, 1, z, w.b(f"{rand}s") if rand.endswith("brick") and False else w.b("prismarine_bricks" if _stil(seed)
                                                                                         else "stone_bricks"))
        w.setze(x, 2, z, w.b(f"{rand}_slab", type="bottom", waterlogged=False))
    for x, z in scheibe(2.5):
        for y in (1, 2):
            w.setze(x, y, z, w.b("dark_prismarine") if _stil(seed) else w.b("polished_andesite"))
    art = "bronze" if _stil(seed) else "gold"
    drache_setzen(w, art, 0.35 * u + 0.1, (0.5, 3.01, 0.5), haltung="sitzend", dreh=0.0)
    hx = round((7 + 2.8) * (0.35 * u + 0.1)) + 1
    hy = round(3 + 12.5 * (0.35 * u + 0.1))
    for k in range(1, _r(hy)):
        x = hx + k // 2
        y = hy - k
        if y >= 2:
            w.setze(x, y, 0, w.b("water", level=0)) if w.frei(x, y, 0) else None
    hohl(w, 2)
    return w


def drachenkampf(seed, g=2):
    """Drachenkampf: zwei aufgerichtete Drachen in verschiedenen Farben stehen sich auf einem zerklüfteten
    Plateau gegenüber, dazwischen ein Feuerstrahl aus Magma und Glut."""
    w = _welt(seed)
    u = U[g]
    R = 12 * u + 6
    spukboden(w, _r(R + 3), dichte=0.4)
    felsen(w, R * 0.8, 2 * u + 1, rauh=0.4, mat=Mat(w, ["blackstone", "basalt", "stone", "tuff"]))
    paar = [("rot", "gruen"), ("gold", "schwarz"), ("blau", "rot"), ("bronze", "eis")][(seed // 7) % 4]
    s = 0.7 * u
    d = 9 * s + 2
    drache_setzen(w, paar[0], s, (-d + 0.5, 2 * u + 1.01, 0.5), haltung="sitzend", dreh=0.0)
    drache_setzen(w, paar[1], s, (d + 0.5, 2 * u + 1.01, 0.5), haltung="sitzend", dreh=math.pi)
    yf = round(2 * u + 1 + 12 * s)
    for x in range(-round(d * 0.4), round(d * 0.4) + 1):
        for k in range(2):
            w.setze(x, yf - k + (1 if abs(x) < 2 else 0), int(w.rng.integers(-1, 2)),
                    w.b("magma_block") if (x + k) % 3 else w.b("shroomlight"))
    verbrennen(w, 0.2)
    hohl(w, 2)
    return w


def drachenwaechter(seed, g=2):
    """Pforte der Drachenwächter: breite Freitreppe zu einem Steintor, flankiert von zwei sitzenden
    Drachenstatuen auf Sockeln, Feuerschalen und Banner."""
    w = _welt(seed)
    u = U[g]
    s = 0.55 * u + 0.15
    B = _r(3 * u + 2, 3)
    gelaende(w, _r(14 * s + 8), art="wiese", dichte=0.2)
    M = Mat(w, ["stone_bricks", "polished_andesite", "smooth_stone", "chiseled_stone_bricks"] if _stil(seed) else
            ["polished_blackstone_bricks", "polished_blackstone", "blackstone", "chiseled_polished_blackstone"])
    n = 3 + g
    for k in range(n):
        for x in range(-B - 1, B + 2):
            for z in range(-k, 3):
                w.setze(x, k + 1, z - 2 * k, M(x, k + 1, z, k / n))
    yt = n
    Ht = _r(6 * u + 4)
    for sx in (-1, 1):
        for y in range(yt + 1, yt + Ht + 1):
            for dx in (0, sx):
                for dz in (-1, 0):
                    w.setze(sx * (B + 1) + dx, y, -2 * n + dz, M(sx * B, y, 0, y / Ht))
    for x in range(-B - 2, B + 3):
        for dz in (-1, 0):
            w.setze(x, yt + Ht + 1, -2 * n + dz, M(x, 0, 0, 0.9))
    for sx in (-1, 1):
        px = sx * (B + 6 * s + 3)
        for y in range(1, 4):
            for x, z in scheibe(3 * s + 1, round(px), -n):
                w.setze(x, y, z, M(x, y, z, 0.3))
        drache_setzen(w, _art(seed, ["stein", "bronze", "gold", "schwarz"]), s, (px + 0.5, 4.01, -n + 0.5),
                      haltung="sitzend", dreh=-math.pi / 2, spiegel=sx > 0)
    hohl(w, 2)
    return w


def schatzberg(seed, g=2):
    """Schatzberg: unter freiem Himmel ein gewaltiger Hort aus Gold, Edelsteinen, Kronen und Truhen; darauf
    eingerollt ein schlafender Drache, Schwerter stecken im Gold."""
    w = _welt(seed)
    u = U[g]
    R = 8 * u + 4
    gelaende(w, _r(R + 4), art="sand", dichte=0.2)
    gold_haufen(w, 0, 0, R, 3 * u + 2)
    drache_setzen(w, _art(seed, ["rot", "gruen", "schwarz", "blau"]), 0.6 * u + 0.1, (0.5, 3 * u + 2, 0.5),
                  dreh=1.3)
    rng = w.rng
    for i in range(6 + 3 * g):
        a = rng.random() * 2 * math.pi
        d = R * (0.4 + 0.5 * rng.random())
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = max([yy for (xx, yy, zz) in w.bloecke if xx == x and zz == z] + [0]) + 1
        w.setze(x, y, z, w.b("lightning_rod", facing="up", powered=False, waterlogged=False) if i % 2 else
                w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
        if i % 2 == 0:
            w.setze(x, y + 1, z, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
    hohl(w, 2)
    return w


DRACHEN = {
    "drachenstatue": ("Drachenstatue", drachenstatue),
    "drachennest": ("Drachennest", drachennest),
    "hortgrotte": ("Hortgrotte", hortgrotte),
    "drachenturm": ("Drachenhorst-Turm", drachenturm),
    "schaedeltor": ("Drachenschädel-Tor", schaedeltor),
    "fliegender_drache": ("Abhebender Drache", fliegender_drache),
    "drachenskelett": ("Drachenskelett", drachenskelett),
    "verbrannte_burg": ("Verbrannte Burg", verbrannte_burg),
    "drachenhoehle": ("Drachenhöhle", drachenhoehle),
    "eisdrache": ("Eisdrache", eisdrache),
    "drachenhorst": ("Drachenreiter-Horst", drachenhorst),
    "drachentempel": ("Drachentempel des Ostens", schlangendrachen_tempel),
    "lindwurm": ("Lindwurm", lindwurm),
    "dracheneischrein": ("Schrein des Dracheneis", dracheneischrein),
    "vulkanhort": ("Vulkanhort", vulkanhort),
    "drachenbruecke": ("Drachenbrücke", drachenbruecke),
    "drachenbrunnen": ("Drachenbrunnen", drachenbrunnen),
    "drachenkampf": ("Drachenkampf", drachenkampf),
    "drachenwaechter": ("Pforte der Drachenwächter", drachenwaechter),
    "schatzberg": ("Schatzberg", schatzberg),
}

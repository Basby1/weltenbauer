"""Weltwunder Teil 5 – Hafenkoloss, Leuchtturm der Welten, Große Bibliothek, Kristallbaum, Himmelsbrücke,
Phönixschrein, Schildkröteninsel, Schwert im Stein, Kolosseum, Meerestempel."""

from __future__ import annotations

import math

import numpy as np

import pracht as P
from lib import Rauschen, einfuegen, laub
from motive import figur
from pracht import Mat, gelaende
from skulptur import Skulptur, dreh_x, dreh_y, dreh_z, ell, kap, kreisrand, scheibe, spiegel_x, torus
from weltwunder import GROESSEN, U, _r, _stil, bl, hohl, platz, sk, welt
from wueste_eis import kuppel


def meer(w, R, y=0, boden="sand"):
    for x, z in scheibe(R):
        if (x, y, z) not in w.bloecke:
            w.setze(x, y, z, w.b("water", level=0))
            w.setze(x, y - 1, z, w.b(boden) if (x * 3 + z) % 5 else w.b("gravel"))


def fels(w, R, H, cx=0, cz=0, y0=0, M=None, spitz=1.0, rauh=0.3):
    from drachen import felsen
    return felsen(w, R, H, mat=M, cx=cx, cz=cz, y0=y0, spitz=spitz, rauh=rauh)


# ============================================================================ 1 Hafenkoloss


def hafenkoloss(seed, g=2):
    """Hafenkoloss: eine bronzene oder marmorne Riesenstatue mit erhobener Fackel steht auf einem gewaltigen Sockel
    zwischen zwei Molen mit Leuchttürmen an der Hafeneinfahrt; Wellenbrecher und Laternen."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    R = _r(42 * u)
    meer(w, R)
    M = Mat(w, ["stone_bricks", "polished_andesite", "mossy_stone_bricks", "andesite"], kontrast=0.8)
    for sx in (-1, 1):
        for x in range(10, _r(R * 0.85)):
            for z in range(-3, 4):
                for y in range(-1, 3):
                    w.setze(sx * x, y, z + sx * 0, M(x, y, z, 0.4))
        lx = sx * _r(R * 0.8)
        for y in range(3, _r(22 * u)):
            for x, z in kreisrand(2.5, lx, 0):
                w.setze(x, y, z, w.b("white_concrete") if (y // 4) % 2 else w.b("red_concrete"))
        w.setze(lx, _r(22 * u), 0, w.b("sea_lantern"))
    hs = _r(12 * u)
    for y in range(-1, hs):
        for x, z in scheibe(9 * u - y * 0.15):
            w.setze(x, y, z, M(x, y, z, y / hs))
    s = 2.8 * u
    mat = Mat(w, ["waxed_copper_block", "waxed_exposed_copper", "waxed_weathered_copper", "waxed_cut_copper"]
              if st == 0 else ["smooth_quartz", "calcite", "polished_diorite", "white_concrete"], kontrast=0.7)
    S = Skulptur(w, s)
    S.mat("k", sk(mat, hs, hs + 26 * s))
    S.mat("a", bl(w, "gold_block"))
    S.mat("d", bl(w, "waxed_oxidized_copper" if st == 0 else "light_gray_concrete"))
    S.mat("g", bl(w, "shroomlight"))
    figur(S, "mensch", "stab")
    S.rendern((-7, -1, -5), (7, 26, 7), versatz=(0.5, hs + 0.01, 0.5))
    hohl(w, 3)
    return w


# ============================================================================ 2 Leuchtturm der Welten


def weltenleuchtturm(seed, g=2):
    """Leuchtturm der Welten: ein himmelhoher Turm auf einer Klippeninsel mit drei Galerien, gewundenem
    Fensterband, Bronzelaterne mit riesigem Leuchtfeuer und Wärterstadt am Fuß."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    R = _r(45 * u)
    meer(w, R)
    hoehe = fels(w, R * 0.5, 12 * u, spitz=0.8)
    yb = 12 * u
    H = _r(85 * u)
    Rt = 6 * u + 2
    wand = Mat(w, ["smooth_stone", "stone_bricks", "polished_andesite", "calcite"] if st == 0 else
               ["sandstone", "smooth_sandstone", "cut_sandstone", "calcite"], kontrast=0.6)
    y0 = int(yb)
    for y in range(y0, y0 + H):
        t = (y - y0) / H
        r = Rt * (1 - 0.35 * t)
        for x, z in kreisrand(r):
            a = math.atan2(z, x)
            fen = abs(((a / (2 * math.pi) * 8 + t * 6) % 1) - 0.5) < 0.06
            w.setze(x, y, z, w.b("light_blue_stained_glass") if fen else wand(x, y, z, t))
        if (y - y0) in (H // 3, 2 * H // 3, H - 1):
            for x, z in scheibe(r + 2.5):
                if math.hypot(x, z) > r - 0.5:
                    w.setze(x, y, z, wand(x, y, z, 0.9))
            for x, z in kreisrand(r + 2.5):
                w.setze(x, y + 1, z, w.b("iron_bars", north=True, south=True, east=True, west=True,
                                         waterlogged=False))
    yt = y0 + H
    rl = Rt * 0.65
    for y in range(yt, yt + _r(8 * u)):
        for x, z in kreisrand(rl):
            w.setze(x, y, z, w.b("glass") if (x + z) % 3 else w.b("waxed_copper_block"))
    for x, z in scheibe(rl - 1):
        for y in range(yt, yt + _r(6 * u)):
            if math.hypot(x, z) < rl * 0.5:
                w.setze(x, y, z, w.b("sea_lantern") if (y + x) % 2 else w.b("glowstone"))
    kuppel(w, w.b("waxed_oxidized_copper"), 0, 0, yt + _r(8 * u), rl + 0.5, form="spitz", spitze="gold_block")
    for i in range(5):
        a = i / 5 * 2 * math.pi + 0.5
        cx, cz = round(math.cos(a) * R * 0.35), round(math.sin(a) * R * 0.35)
        hy = hoehe.get((cx, cz), 0) + 1
        sti = P.Stil(w, wand="putz", sockel="graustein", gesims="stone_brick", dach="mcw_rot" if st == 0 else
                     "mcw_blau", holz="spruce")
        P.gebaeude(w, sti, cx - 3, cz - 3, cx + 3, cz + 3, y0=hy, etagen=1, eh=4, dach="sattel", tuer="south",
                   gauben=False, kamine=1)
    hohl(w, 3)
    return w


# ============================================================================ 3 Große Bibliothek


def grosse_bibliothek(seed, g=2):
    """Große Bibliothek: Rotunde mit gewaltiger Kuppel und Laterne, vier Flügel mit Bogenfenstern, Säulenportikus,
    vier Ecktürme und ein Platz mit Gelehrtenstatuen."""
    from kathedralen import halle, stil as sakralstil
    w = welt(seed)
    u = U[g]
    s = sakralstil(w, seed, "marmor", "kalk")
    Rp = _r(48 * u)
    yp = platz(w, Rp, s.wand, rand="quartz" if _stil(seed) == 0 else "stone_brick")
    Rr = _r(14 * u)
    Hr = _r(16 * u)
    for y in range(yp, yp + Hr):
        for x, z in kreisrand(Rr):
            a = math.atan2(z, x)
            fen = (y - yp) % 8 in (2, 3, 4, 5) and abs(math.sin(a * 6)) < 0.25
            w.setze(x, y, z, s.g(x, y, z, 0.5) if fen else s.wand(x, y, z, (y - yp) / Hr))
    kuppel(w, lambda x, y, z, t: w.b("waxed_oxidized_copper") if (x + z) % 4 else w.b("waxed_oxidized_cut_copper"),
           0, 0, yp + Hr, Rr + 0.5, spitze=None)
    yk = yp + Hr + _r(Rr)
    for y in range(yk - 1, yk + _r(5 * u)):
        for x, z in kreisrand(2.5):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y") if (x + z) % 2 else w.b("glass"))
    kuppel(w, w.b("gold_block"), 0, 0, yk + _r(5 * u), 2.8, spitze="gold_block")
    Lf = _r(18 * u)
    B = _r(6 * u)
    for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if dx:
            x0, x1 = (Rr - 1, Rr + Lf) if dx > 0 else (-Rr - Lf, -Rr + 1)
            halle(w, s, x0, -B, x1, B, yp, _r(10 * u), achse="x", fenster_abst=4)
        else:
            z0, z1 = (Rr - 1, Rr + Lf) if dz > 0 else (-Rr - Lf, -Rr + 1)
            halle(w, s, -B, z0, B, z1, yp, _r(10 * u), achse="z", fenster_abst=4)
    for sx in (-1, 1):
        for sz in (-1, 1):
            P.turm(w, s.st, sx * (Rr + Lf // 2), sz * (Rr + Lf // 2), yp, _r(26 * u), 3 * u + 1.5,
                   dach="kegel", krone=False, fahne=None, fenster=6)
    zp = Rr + Lf + 1
    for x in range(-B - 2, B + 3, 3):
        for y in range(yp, yp + _r(10 * u)):
            w.setze(x, y, zp + 4, w.b("quartz_pillar", axis="y"))
    for x in range(-B - 3, B + 4):
        for z in range(zp, zp + 6):
            w.setze(x, yp + _r(10 * u), z, s.wand(x, 0, z, 0.9))
    for sx in (-1, 1):
        S = Skulptur(w, 0.6 * u + 0.2)
        S.mat("k", sk(Mat(w, ["smooth_quartz", "calcite", "polished_diorite"]), yp, yp + 22))
        S.mat("a", bl(w, "gold_block"))
        S.mat("d", bl(w, "light_gray_concrete"))
        S.mat("g", bl(w, "sea_lantern"))
        figur(S, "mensch", "denker")
        S.rendern((-7, -1, -5), (7, 26, 7), versatz=(sx * (B + 8) + 0.5, yp + 0.01, zp + 10.5))
    hohl(w, 3)
    return w


# ============================================================================ 4 Kristallbaum


def kristallbaum(seed, g=2):
    """Kristallbaum: ein riesiger Baum mit Stamm und Ästen aus Amethyst und Kalzit, die Krone aus leuchtenden
    Glas- und Kristallballen, Kristallwurzeln brechen aus dem Boden, darunter ein Spiegelsee."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    R = _r(45 * u)
    gelaende(w, R, art="wiese", dichte=0.3)
    for x, z in scheibe(R * 0.6):
        if math.hypot(x, z) > R * 0.35:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("calcite"))
    stamm = Mat(w, ["amethyst_block", "purpur_block", "calcite", "amethyst_block"] if st == 0 else
                ["calcite", "diorite", "smooth_quartz", "packed_ice"], kontrast=0.8)
    glas = ["purple_stained_glass", "magenta_stained_glass", "pink_stained_glass", "amethyst_block"] if st == 0 else \
        ["light_blue_stained_glass", "cyan_stained_glass", "white_stained_glass", "sea_lantern"]
    S = Skulptur(w, 1.0)
    S.mat("s", sk(stamm, 0, 60 * u))
    S.mat("g", lambda x, y, z, *_: w.b(glas[(x * 7 + y * 3 + z * 5) % len(glas)]))
    H = 40 * u
    rs = 4.5 * u
    S.plus(kap((0, -1, 0), (0, H * 0.55, 0), rs, rs * 0.6), "s")
    rng = w.rng
    enden = []
    for i in range(6):
        a = i / 6 * 2 * math.pi + rng.random() * 0.4
        p0 = (0, H * (0.4 + 0.1 * (i % 3)), 0)
        L = H * (0.35 + 0.15 * rng.random())
        p1 = (math.cos(a) * L * 0.7, p0[1] + L * 0.6, math.sin(a) * L * 0.7)
        S.plus(kap(p0, p1, rs * 0.45, rs * 0.18), "s")
        enden.append(p1)
    for (x, y, z) in enden + [(0, H * 0.95, 0)]:
        r = 7 * u + rng.random() * 3 * u
        S.plus(lambda X, Y, Z, x=x, y=y, z=z, r=r: (((X - x) / r) ** 2 + ((Y - y) / (r * 0.65)) ** 2 +
                                                   ((Z - z) / r) ** 2 < 1) &
               ((X * 3 + Y * 5 + Z * 7) % 4 > 0.9), "g")
    for i in range(7):
        a = i / 7 * 2 * math.pi
        S.plus(kap((0, 2, 0), (math.cos(a) * 14 * u, -1, math.sin(a) * 14 * u), rs * 0.4, rs * 0.12), "s")
    S.rendern((-R, -2, -R), (R, H * 1.4, R), versatz=(0.5, 0.01, 0.5))
    hohl(w, 3)
    return w


# ============================================================================ 5 Himmelsbrücke


def himmelsbruecke(seed, g=2):
    """Himmelsbrücke: zwei schroffe Felsnadeln, verbunden durch eine kühne Bogenbrücke mit Torbauten an beiden
    Enden, darunter ein Wasserfall, der in eine Schlucht stürzt."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    L = _r(40 * u)
    H = _r(45 * u)
    fm = Mat(w, ["stone", "andesite", "tuff", "diorite", "cobblestone", "granite"], kontrast=1.3)
    for sx in (-1, 1):
        fels(w, 14 * u, H, cx=sx * L, cz=0, M=fm, spitz=0.45, rauh=0.25)
    for x in range(-L, L + 1):
        for z in range(-_r(18 * u), _r(18 * u) + 1):
            if (x / L) ** 2 + (z / (18 * u)) ** 2 < 1 and (x, 0, z) not in w.bloecke:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel"))
    M = Mat(w, ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "polished_andesite"] if st == 0 else
            ["smooth_sandstone", "cut_sandstone", "sandstone", "chiseled_sandstone"], kontrast=0.7)
    yb = int(H * 0.82)
    B = _r(3 * u + 1)
    for x in range(-L, L + 1):
        t = x / L
        unten = yb - 2 - int((1 - t * t) * 0 + 2)
        bog = yb - 3 - int(math.sqrt(max(0, 1 - (x / (L * 0.8)) ** 2)) * -0) if abs(x) > L * 0.8 else \
            int(yb - 3 - (1 - (x / (L * 0.8)) ** 2) * 0)
        tiefe = int(14 * u * (1 - math.sqrt(max(0, 1 - (x / (L * 0.82)) ** 2)))) if abs(x) < L * 0.82 else 14 * u
        for z in range(-B, B + 1):
            for y in range(yb - 2 - int(tiefe * 0.3), yb + 1):
                if abs(x) >= L * 0.82 or y >= yb - 2 - int(tiefe * 0.3):
                    w.setze(x, y, z, M(x, y, z, 0.5))
        for z in (-B - 1, B + 1):
            w.setze(x, yb + 1, z, w.b("stone_brick_wall" if st == 0 else "sandstone_wall", up=x % 4 == 0,
                                      north="none", south="none", east="low", west="low", waterlogged=False))
    for sx in (-1, 1):
        sti = P.Stil(w, wand="graustein" if st == 0 else "sandstein", sockel="graustein", gesims="stone_brick" if st == 0
                     else "sandstone", dach="mcw_blau" if st == 0 else "mcw_rot", holz="spruce")
        x0 = sx * (L - 6)
        P.turm(w, sti, x0, -B - 3, yb + 1, _r(14 * u), 3 * u, dach="kegel", krone=True, fahne=None)
        P.turm(w, sti, x0, B + 3, yb + 1, _r(14 * u), 3 * u, dach="kegel", krone=True, fahne=None)
    for y in range(1, yb - 4):
        w.setze(-L + _r(10 * u), y, _r(8 * u), w.b("water", level=0 if y == yb - 5 else 8))
    hohl(w, 3)
    return w


# ============================================================================ 6 Phönixschrein


def phoenixschrein(seed, g=2):
    """Phönixschrein: eine Stufenpyramide aus rotem Sandstein mit Feuerrinnen, auf deren Spitze ein Phönix mit
    weit ausgebreiteten Flammenschwingen thront; Feuerschalen an allen Ecken."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    R = _r(40 * u)
    gelaende(w, R + 6, art="sand", dichte=0.2)
    M = Mat(w, ["red_sandstone", "cut_red_sandstone", "smooth_red_sandstone", "orange_terracotta"] if st == 0 else
            ["blackstone", "polished_blackstone_bricks", "basalt", "smooth_basalt"], kontrast=0.7)
    n = 7
    for k in range(n):
        r = _r(R * (1 - k / (n + 1)))
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                for y in range(k * 4, k * 4 + 4):
                    w.setze(x, y, z, M(x, y, z, k / n))
                if max(abs(x), abs(z)) == r and (x + z) % 6 == 0:
                    w.setze(x, k * 4 + 4, z, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                 waterlogged=False))
        for x in range(-2, 3):
            for z in range(r - 4, r + 1):
                pass
    for k in range(n * 4):
        for x in range(-2, 3):
            w.setze(x, k, R - k + 0, w.b("red_sandstone_stairs" if st == 0 else "blackstone_stairs", facing="north",
                                        half="bottom", shape="straight", waterlogged=False))
    yt = n * 4
    s = 2.0 * u
    S = Skulptur(w, s)
    feuer = lambda x, y, z, lx, ly, lz: w.b(["red_concrete", "orange_concrete", "yellow_concrete", "shroomlight",
                                             "orange_terracotta"][int((abs(lx) * 0.6 + ly * 0.2 + (x + z) * 0.1)) % 5])
    S.mat("f", feuer)
    S.mat("k", bl(w, "red_concrete"))
    S.mat("a", bl(w, "gold_block"))
    S.mat("g", bl(w, "shroomlight"))
    S.plus(ell(0, 8, 0, 2.6, 4.0, 2.4), "k")
    S.plus(kap((0, 11, 0.5), (0, 14.5, 1.8), 1.3, 1.0), "k")
    S.plus(ell(0, 15.5, 2.3, 1.4, 1.3, 1.6), "k")
    S.plus(kap((0, 15.3, 3.6), (0, 14.6, 5.0), 0.6, 0.2), "a")
    for sz in (-1, 1):
        S.plus(ell(sz * 0.8, 16.0, 3.3, 0.3, 0.3, 0.3), "g")
    for sx in (-1, 1):
        S.plus(lambda X, Y, Z, sx=sx: (sx * X > 1.5) & (sx * X < 16) & (np.abs(Z + 0.5) < 0.8) &
               (Y > 5 + 0.35 * sx * X) & (Y < 9 + 1.1 * sx * X - 0.05 * X * X), "f")
    S.plus(lambda X, Y, Z: (np.abs(X) < 1.5 + (4.5 - Y) * 0.6) & (Y > 0) & (Y < 4.5) & (Z < -1) & (Z > -9 + Y), "f")
    S.rendern((-20, 0, -10), (20, 20, 8), versatz=(0.5, yt + 0.01, 0.5))
    hohl(w, 3)
    return w


# ============================================================================ 7 Schildkröteninsel


def schildkroeteninsel(seed, g=2):
    """Schildkröteninsel: eine gigantische Meeresschildkröte schwimmt im Meer, auf ihrem moosbewachsenen Panzer
    steht ein kleines Dorf mit Bäumen und Leuchtturm."""
    import wald2
    w = welt(seed)
    u = U[g]
    R = _r(55 * u)
    meer(w, R)
    s = 2.4 * u
    S = Skulptur(w, s)
    S.mat("p", lambda x, y, z, lx, ly, lz: w.b(["moss_block", "green_terracotta", "brown_terracotta",
                                                "mossy_cobblestone"][int((math.floor(lx / 2.5) + math.floor(lz / 2.5)) % 4)]))
    S.mat("h", lambda x, y, z, *_: w.b("lime_terracotta") if (x + z) % 3 else w.b("green_terracotta"))
    S.mat("a", bl(w, "black_concrete"))
    S.plus(lambda X, Y, Z: ((X / 11) ** 2 + (Y / 4.5) ** 2 + (Z / 9) ** 2 < 1) & (Y > -1.5), "p")
    S.plus(ell(13, 0.5, 0, 3.5, 2.6, 2.8), "h")
    for sz in (-1, 1):
        S.plus(ell(15, 1.6, sz * 1.5, 0.5, 0.5, 0.5), "a")
        S.plus(lambda X, Y, Z, sz=sz: (((X - 6) / 3.0) ** 2 + ((Z - sz * 12) / 6.5) ** 2 < 1) & (np.abs(Y) < 0.9),
               "h")
        S.plus(lambda X, Y, Z, sz=sz: (((X + 7) / 2.5) ** 2 + ((Z - sz * 10) / 4.0) ** 2 < 1) & (np.abs(Y) < 0.8),
               "h")
    S.rendern((-16, -2, -20), (18, 6, 20), versatz=(0.5, 0.01, 0.5))
    top = {}
    for (x, y, z) in w.bloecke:
        if abs(x) < 9 * s and abs(z) < 7 * s and y > top.get((x, z), -9):
            if w.P.name(w.bloecke[(x, y, z)]) != "minecraft:water":
                top[(x, z)] = y
    rng = w.rng
    sti = P.Stil(w, wand="putz", sockel="graustein", gesims="stone_brick", dach="mcw_rot", holz="spruce")
    for i in range(3 + g):
        a = i / (3 + g) * 2 * math.pi + 0.3
        cx, cz = round(math.cos(a) * 5 * s), round(math.sin(a) * 4 * s)
        yy = top.get((cx, cz))
        if yy is None:
            continue
        P.gebaeude(w, sti, cx - 3, cz - 2, cx + 3, cz + 2, y0=yy + 1, etagen=1, eh=4, dach="sattel", tuer="south",
                   gauben=False, kamine=1)
    for i in range(4 + g):
        cx, cz = int(rng.integers(-6 * s, 6 * s)), int(rng.integers(-5 * s, 5 * s))
        yy = top.get((cx, cz))
        if yy is not None and w.frei(cx, yy + 1, cz):
            einfuegen(w, wald2.laubbaum(int(rng.integers(1, 10 ** 6)), "oak", H=8 + int(rng.integers(4))),
                      cx, yy + 1, cz)
    yy = top.get((0, 0), 10)
    for y in range(yy + 1, yy + _r(14 * u)):
        for x, z in kreisrand(1.6):
            w.setze(x, y, z, w.b("white_concrete") if (y // 3) % 2 else w.b("red_concrete"))
    w.setze(0, yy + _r(14 * u), 0, w.b("sea_lantern"))
    hohl(w, 3)
    return w


# ============================================================================ 8 Schwert im Stein


def schwert_im_stein(seed, g=2):
    """Schwert im Stein: ein zerklüfteter Felshügel, in dem schräg ein gigantisches Schwert steckt – Klinge aus
    Eisen mit Kehle, goldene Parierstange mit Edelsteinen, Ledergriff und Knauf; Risse leuchten im Fels."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    R = _r(32 * u)
    gelaende(w, R + 8, art="wiese", dichte=0.3)
    fm = Mat(w, ["stone", "andesite", "mossy_cobblestone", "tuff", "cobblestone"], kontrast=1.2)
    hoehe = fels(w, R, 14 * u, M=fm, spitz=1.4, rauh=0.25)
    rng = w.rng
    for i in range(8):
        a = i / 8 * 2 * math.pi + rng.random() * 0.3
        for t in np.linspace(2, R * 0.8, int(R)):
            x, z = round(math.cos(a) * t), round(math.sin(a) * t)
            y = hoehe.get((x, z))
            if y:
                w.setze(x, y, z, w.b("magma_block") if st == 1 else w.b("sea_lantern"))
    s = 1.5 * u
    S = Skulptur(w, s)
    S.mat("b", lambda x, y, z, lx, ly, lz: w.b("iron_block") if abs(lz) > 0.35 else w.b("light_gray_concrete"))
    S.mat("g", bl(w, "gold_block"))
    S.mat("e", bl(w, "emerald_block" if st == 0 else "redstone_block"))
    S.mat("l", bl(w, "brown_terracotta"))
    S.plus(lambda X, Y, Z: (Y > -20) & (Y < 30) & (np.abs(Z) < 3.2 - np.maximum(0, Y - 26) * 0.8) &
           (np.abs(X) < 1.0), "b")
    S.plus(lambda X, Y, Z: (np.abs(Y - 31) < 1.0) & (np.abs(Z) < 9) & (np.abs(X) < 1.4), "g")
    S.plus(ell(0, 31, 0, 1.2, 1.2, 1.2), "e")
    S.plus(kap((0, 32, 0), (0, 40, 0), 1.2, 1.2), "l")
    S.plus(ell(0, 41.5, 0, 1.8, 1.8, 1.8), "g")
    top = hoehe.get((0, 0), 10)
    S.rendern((-4, -20, -10), (4, 44, 10), versatz=(0.5, top - 4, 0.5), dreh=dreh_z(0.25) @ dreh_y(0.5))
    hohl(w, 3)
    return w


# ============================================================================ 9 Kolosseum


def kolosseum(seed, g=2):
    """Kolosseum: ein elliptisches Amphitheater mit drei Bogenreihen übereinander, auf einer Seite eingestürzt,
    innen Sitzränge, Arena mit Sand und unterirdischen Gängen; Säulen und Statuen am Eingang."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    A, B = 48 * u, 38 * u
    gelaende(w, _r(A + 8), art="wiese", dichte=0.2)
    M = Mat(w, ["smooth_sandstone", "cut_sandstone", "sandstone", "chiseled_sandstone"] if st == 0 else
            ["stone_bricks", "polished_andesite", "smooth_stone", "cracked_stone_bricks"], kontrast=0.6)
    H = _r(9 * u) * 3
    ruine = lambda x, z: x > A * 0.4 and z > 0
    for x in range(-_r(A), _r(A) + 1):
        for z in range(-_r(B), _r(B) + 1):
            d = (x / A) ** 2 + (z / B) ** 2
            if 0.82 < d <= 1.0:
                hmax = H if not ruine(x, z) else int(H * (0.4 + 0.3 * math.sin(x * 0.3)))
                a = math.atan2(z / B, x / A)
                bogen = abs(math.sin(a * 32)) > 0.45
                for y in range(0, hmax):
                    e = y % (H // 3)
                    loch = bogen and 1 <= e <= H // 3 - 3 and d > 0.9
                    if not loch:
                        w.setze(x, y, z, M(x, y, z, y / H))
            elif d <= 0.82 and d > 0.35:
                hs = int((d - 0.35) / 0.47 * H * 0.7)
                for y in range(0, hs + 1):
                    if y == hs or (x + z) % 7 == 0:
                        w.setze(x, y, z, M(x, y, z, 0.4))
            elif d <= 0.35:
                w.setze(x, 0, z, w.b("sand") if (x * 3 + z) % 9 else w.b("gravel"))
    for sx in (-1, 1):
        S = Skulptur(w, 0.7 * u + 0.3)
        S.mat("k", sk(M, 0, 22))
        S.mat("a", bl(w, "gold_block"))
        S.mat("d", bl(w, "light_gray_concrete"))
        S.mat("g", bl(w, "shroomlight"))
        figur(S, "ritter", "schwert")
        S.rendern((-7, -1, -5), (7, 26, 7), versatz=(sx * 8 + 0.5, 0.01, _r(B) + 6.5))
    hohl(w, 2)
    return w


# ============================================================================ 10 Meerestempel


def meerestempel(seed, g=2):
    """Tempel des Ozeans: ein Prismarin-Tempel mit grüner Kuppel steht in einer Lagune, umgeben von Bögen,
    Korallengärten, Statuen von Meereswesen und leuchtenden Seelaternen-Säulen."""
    w = welt(seed)
    u = U[g]
    R = _r(50 * u)
    meer(w, R)
    rng = w.rng
    for x, z in scheibe(R * 0.9):
        if rng.random() < 0.06 and math.hypot(x, z) > R * 0.4:
            w.setze(x, 0, z, w.b(f"{['tube', 'brain', 'bubble', 'fire', 'horn'][int(rng.integers(5))]}_coral_block"))
    M = Mat(w, ["prismarine_bricks", "prismarine", "dark_prismarine", "prismarine_bricks"], kontrast=0.6)
    Rt = _r(20 * u)
    for k in range(3):
        for x, z in scheibe(Rt + 3 - k * 2):
            w.setze(x, k, z, M(x, k, z, k / 3))
    H = _r(12 * u)
    for i in range(16):
        a = i / 16 * 2 * math.pi
        x, z = round(math.cos(a) * (Rt - 3)), round(math.sin(a) * (Rt - 3))
        for y in range(3, 3 + H):
            w.setze(x, y, z, w.b("sea_lantern") if y % 4 == 0 else w.b("prismarine_bricks"))
    for x, z in kreisrand(Rt - 3):
        w.setze(x, 3 + H, z, M(x, 3 + H, z, 0.9))
    Rk = Rt * 0.55
    for y in range(3, 3 + H):
        for x, z in kreisrand(Rk):
            w.setze(x, y, z, M(x, y, z, 0.5) if (y + x) % 5 else w.b("cyan_stained_glass"))
    kuppel(w, lambda x, y, z, t: w.b("waxed_oxidized_copper") if (x + y) % 3 else w.b("dark_prismarine"), 0, 0,
           3 + H, Rk + 1, spitze="sea_lantern")
    for i in range(4):
        a = i / 4 * 2 * math.pi + math.pi / 4
        cx, cz = math.cos(a) * (Rt + 10 * u), math.sin(a) * (Rt + 10 * u)
        S = Skulptur(w, 0.8 * u + 0.3)
        S.mat("k", sk(M, 0, 20))
        S.mat("g", bl(w, "sea_lantern"))
        S.plus(lambda X, Y, Z: (np.sqrt(X * X + Z * Z) < 3 - Y * 0.1) & (Y >= 0) & (Y < 6), "k")
        for t in range(6):
            aa = t / 6 * 2 * math.pi
            S.plus(kap((math.cos(aa) * 1.5, 6, math.sin(aa) * 1.5),
                       (math.cos(aa) * 6, 12 + 3 * math.sin(t), math.sin(aa) * 6), 0.9, 0.3), "k")
        S.plus(ell(0, 7, 0, 2.2, 2.2, 2.2), "g")
        S.rendern((-8, -1, -8), (8, 16, 8), versatz=(cx + 0.5, 0.01, cz + 0.5))
    hohl(w, 3)
    return w


TEIL5 = {
    "hafenkoloss": ("Hafenkoloss", hafenkoloss),
    "weltenleuchtturm": ("Leuchtturm der Welten", weltenleuchtturm),
    "grosse_bibliothek": ("Große Bibliothek", grosse_bibliothek),
    "kristallbaum": ("Kristallbaum", kristallbaum),
    "himmelsbruecke": ("Himmelsbrücke", himmelsbruecke),
    "phoenixschrein": ("Phönixschrein", phoenixschrein),
    "schildkroeteninsel": ("Schildkröteninsel", schildkroeteninsel),
    "schwert_im_stein": ("Schwert im Stein", schwert_im_stein),
    "kolosseum": ("Kolosseum", kolosseum),
    "meerestempel": ("Tempel des Ozeans", meerestempel),
}

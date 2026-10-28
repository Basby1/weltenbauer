"""Himmelsreich (neu) – 20 Bauten auf Wolken und schwebenden Inseln."""

from __future__ import annotations

import math

import numpy as np

import modbloecke as MB
import pracht as P
from lib import Rauschen, einfuegen, laub
from pracht import Mat
from skulptur import Skulptur, dreh_y, ell, kap, kreisrand, scheibe, spiegel_x
from weltwunder import bl, hohl, sk
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


class Himmel:
    """Sonnenstil (Marmor + Gold) oder Mondstil (Kalzit + Silber/Hellblau)."""

    def __init__(self, w, seed):
        self.w = w
        self.sonne = _stil(seed) == 0
        self.stein = Mat(w, ["smooth_quartz", "calcite", "polished_diorite", "white_concrete", "quartz_bricks"],
                         kontrast=0.6)
        self.saeule = "quartz_pillar"
        self.gold = "gold_block" if self.sonne else "light_blue_concrete"
        self.gold2 = "yellow_concrete" if self.sonne else "light_blue_terracotta"
        self.glas = "yellow_stained_glass" if self.sonne else "light_blue_stained_glass"
        self.licht = "shroomlight" if self.sonne else "sea_lantern"
        self.dach = "mcw_gelb" if self.sonne else "mcw_blau"
        self.kuppel = "gold_block" if self.sonne else "light_blue_concrete"

    def b(self, n):
        return self.w.b(n)


def wolke(w, cx, cy, cz, r, flach=0.5, dichte=7, seed_off=0):
    """Bauschige Wolke: Unterseite hellgrau, Mitte weißer Beton, oben weiße Wolle; mehrere Ballen."""
    rng = np.random.default_rng(int(cx * 31 + cz * 17 + cy * 7 + r * 13 + seed_off) & 0xFFFFFFFF)
    S = Skulptur(w, 1.0)
    S.mat("w", lambda x, y, z, lx, ly, lz: w.b("light_gray_wool") if ly < -r * flach * 0.45 else
          w.b("white_concrete") if ly < r * flach * 0.1 and (x + z) % 3 == 0 else
          w.b("white_wool") if (x * 7 + y * 3 + z) % 5 else w.b("white_concrete_powder"))
    for i in range(dichte):
        a = i * 2.39996 + rng.random()
        d = r * 0.6 * math.sqrt((i + 0.5) / dichte)
        rr = r * (0.45 + 0.3 * rng.random())
        S.plus(ell(math.cos(a) * d, rr * 0.15 * rng.random(), math.sin(a) * d, rr, rr * flach, rr), "w")
    S.plus(ell(0, 0, 0, r * 0.9, r * flach * 0.7, r * 0.9), "w")
    S.rendern((-r * 2, -r, -r * 2), (r * 2, r, r * 2), versatz=(cx + 0.5, cy, cz + 0.5), ueberschreiben=False)


def insel(w, cx, cy, cz, R, tief=None, gras=True, wurzeln=True):
    """Schwebende Insel: umgedrehter Felskegel mit Erde, Graskappe, Hängewurzeln und Ranken. Gibt die
    Oberflächenhöhe zurück."""
    tief = tief or R * 1.3
    r1 = Rauschen(w, 3)
    fels = Mat(w, ["stone", "andesite", "dirt", "tuff", "cobblestone", "calcite"], kontrast=1.2)
    rng = w.rng
    for x, z in scheibe(R, cx, cz):
        d = math.hypot(x - cx, z - cz) / R
        unten = int(tief * max(0.0, 1 - d) ** 1.4 * (0.75 + 0.5 * r1(x, 0, z)))
        for k in range(unten + 1):
            y = cy - k
            w.setze(x, y, z, w.b("grass_block", snowy=False) if k == 0 and gras else
                    w.b("dirt") if k < 3 else fels(x, y, z, 1 - k / max(1, unten)))
        if wurzeln and rng.random() < 0.12:
            for k in range(1, 2 + int(rng.integers(0, 4))):
                w.setze(x, cy - unten - k, z, w.b("hanging_roots") if k == 1 else w.b("cave_vines",
                                                                                        age=0, berries=rng.random() < 0.3))
        if gras and rng.random() < 0.1 and d < 0.9:
            w.setze(x, cy + 1, z, w.b(["grass", "dandelion", "poppy", "azure_bluet", "oxeye_daisy"][int(rng.integers(5))]))
    return cy


def wasserfall(w, x, y0, z, laenge, rand_x=0, rand_z=1):
    for k in range(laenge):
        w.setze(x, y0 - k, z, w.b("water", level=0 if k == 0 else 8))


def saeulenkranz(w, H_, cx, cz, y0, R, n, Hs, mat=None, kapitell="chiseled_quartz_block", gebaelk=True):
    mat = mat or H_.saeule
    for i in range(n):
        a = i / n * 2 * math.pi
        x, z = round(cx + math.cos(a) * R), round(cz + math.sin(a) * R)
        w.setze(x, y0, z, w.b("quartz_bricks"))
        for y in range(y0 + 1, y0 + Hs):
            w.setze(x, y, z, w.b(mat, axis="y"))
        w.setze(x, y0 + Hs, z, w.b(kapitell))
    if gebaelk:
        for x, z in kreisrand(R, cx, cz):
            w.setze(x, y0 + Hs + 1, z, H_.stein(x, y0 + Hs + 1, z, 0.8))
        for x, z in kreisrand(R + 1, cx, cz):
            w.setze(x, y0 + Hs + 1, z, w.b("smooth_quartz_slab", type="top", waterlogged=False))


def strahlen(w, H_, cx, cy, cz, R, n=12, achse="z"):
    """Strahlenkranz (Sonne) in einer senkrechten Ebene."""
    for i in range(n):
        a = i / n * 2 * math.pi
        for t in np.linspace(R * 0.55, R * (1.0 if i % 2 else 0.8), int(R) + 2):
            x = round(cx + math.cos(a) * t)
            y = round(cy + math.sin(a) * t)
            w.setze(x, y, cz, w.b(H_.gold if t < R * 0.75 else H_.gold2)) if achse == "z" else \
                w.setze(cx, y, round(cz + math.cos(a) * t), w.b(H_.gold if t < R * 0.75 else H_.gold2))
    for x, z in scheibe(R * 0.45):
        if achse == "z":
            w.setze(cx + x, cy + z, cz, w.b(H_.licht) if math.hypot(x, z) < R * 0.3 else w.b(H_.gold))
        else:
            w.setze(cx, cy + z, cz + x, w.b(H_.licht) if math.hypot(x, z) < R * 0.3 else w.b(H_.gold))


def boden_wolken(w, R, y=0):
    """Wolkenteppich am Boden (damit die Vorlage im Spiel auf einem Wolkenfeld steht)."""
    wolke(w, 0, y, 0, R, flach=0.3, dichte=9)


# ============================================================================ Bauten


def himmelstor(seed, g=2):
    """Himmelstor: zwei hohe Marmortürme auf einer Wolkenbank, dazwischen ein goldenes Tor mit Strahlenkranz,
    Wolkentreppe hinauf, Laternen und Banner."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    R = 9 * u + 4
    yw = _r(3 * u + 2)
    wolke(w, 0, yw, 0, R, flach=0.4)
    H = _r(12 * u + 6)
    B = _r(3 * u + 2, 3)
    st = P.Stil(w, wand="marmor", sockel="kalkstein", gesims="quartz", dach=k.dach, holz="birch", laeden=False,
                blumen=0, fenster=k.glas, fensterart="bogen")
    ytop = yw + _r(R * 0.25)
    for sx in (-1, 1):
        P.turm(w, st, sx * (B + 2), 0, ytop, H, max(2.0, 1.6 * u), dach="kegel" if k.sonne else "glocke",
               krone=False, fahne=None, spitze="lightning_rod")
    for x in range(-B, B + 1):
        hb = H - 2 - round((x / (B + 0.5)) ** 2 * 3)
        w.setze(x, ytop + hb, 0, k.stein(x, ytop + hb, 0, 0.9))
        for y in range(ytop, ytop + hb):
            w.setze(x, y, 0, w.b("iron_bars", east=True, west=True, north=False, south=False, waterlogged=False)
                    if not k.sonne else w.b("gold_block") if (x + y) % 4 == 0 else
                    w.b("iron_bars", east=True, west=True, north=False, south=False, waterlogged=False))
    strahlen(w, k, 0, ytop + H + _r(2 * u), 0, 5 * u + 3)
    for s in range(_r(R * 0.25)):
        for x in range(-B, B + 1):
            w.setze(x, yw + s, round(R * 0.8) - s, w.b("quartz_stairs", facing="north", half="bottom",
                                                         shape="straight", waterlogged=False))
    hohl(w, 2)
    return w


def wolkenpalast(seed, g=2):
    """Wolkenpalast: weißer Palast mit goldenen Kuppeln und Minaretten auf einem Wolkenberg, Säulenhof,
    Prunktreppe und schwebende Lichtkugeln."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    R = 12 * u + 5
    yw = _r(4 * u + 2)
    wolke(w, 0, yw, 0, R, flach=0.45)
    y0 = yw + _r(R * 0.3)
    a, b = _r(6 * u + 3, 4), _r(4 * u + 3, 3)
    st = P.Stil(w, wand="marmor", sockel="kalkstein", gesims="quartz", dach=k.dach, holz="birch", laeden=False,
                blumen=0, fenster=k.glas, fensterart="bogen")
    for x in range(-a - 2, a + 3):
        for z in range(-b - 2, b + 3):
            w.setze(x, y0 - 1, z, w.b("smooth_quartz") if (x + z) % 2 else w.b(k.gold2) if (x * z) % 7 == 0
                    else w.b("quartz_bricks"))
    P.gebaeude(w, st, -a, -b, a, b, y0=y0, etagen=2, eh=5, dach="flach" if False else "walm", tuer="south",
               gauben=False, kamine=0, pilaster=1)
    top = kuppel(w, w.b(k.kuppel), 0, 0, y0 + 11, min(a, b) - 0.5, form="zwiebel" if k.sonne else "rund",
                 spitze="gold_block" if k.sonne else "sea_lantern")
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * (a + 1), sz * (b + 1)
            for y in range(y0, y0 + _r(14 * u + 6)):
                for xx, zz in kreisrand(1.2, x, z):
                    w.setze(xx, y, zz, k.stein(xx, y, zz, 0.5))
            kuppel(w, w.b(k.kuppel), x, z, y0 + _r(14 * u + 6), 1.8, form="zwiebel", spitze=None)
    for i in range(5 + g * 2):
        a2 = w.rng.random() * 2 * math.pi
        d = R * (0.6 + 0.3 * w.rng.random())
        w.setze(round(math.cos(a2) * d), y0 + 4 + int(w.rng.integers(0, 8)), round(math.sin(a2) * d), w.b(k.licht))
    hohl(w, 2)
    return w


def engelsstatue(seed, g=2):
    """Engelsstatue: gewaltige Engelsfigur mit hoch erhobenen Armen und ausgebreiteten Flügeln auf einem
    Säulensockel, der aus einer Wolke ragt; Heiligenschein aus Gold."""
    from motive import figur
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    s = 0.6 * u + 0.25
    R = 8 * s + 5
    yw = _r(3 * u + 2)
    wolke(w, 0, yw, 0, R, flach=0.35)
    ys = yw + _r(R * 0.2)
    for kk in range(3):
        for x, z in scheibe(3 * s + 2 - kk):
            w.setze(x, ys + kk, z, k.stein(x, ys + kk, z, kk / 3))
    S = Skulptur(w, s)
    S.mat("k", sk(Mat(w, ["smooth_quartz", "calcite", "white_concrete", "polished_diorite"]), ys, ys + 26 * s))
    S.mat("a", bl(w, k.gold))
    S.mat("d", bl(w, "light_gray_concrete"))
    S.mat("g", bl(w, k.licht))
    figur(S, "elf", "arme_hoch")
    for sx in (-1, 1):
        S.plus(lambda X, Y, Z, sx=sx: (((X - sx * 7) / 6.5) ** 2 + ((Y - 17) / 9) ** 2 < 1) &
               (np.abs(Z + 1.8 + 0.08 * np.abs(X)) < 0.7) & (Y > 8), "k")
    S.plus(lambda X, Y, Z: (np.abs(np.sqrt(X * X + (Y - 24.5) ** 2) - 2.6) < 0.5) & (np.abs(Z + 1.2) < 0.5), "a")
    S.rendern((-15, -1, -5), (15, 30, 5), versatz=(0.5, ys + 3.01, 0.5))
    hohl(w, 2)
    return w


def schwebende_insel(seed, g=2):
    """Schwebende Insel: Felsinsel mit Graskappe, einem alten Baum, kleinem Rundtempel und Wasserfall, der in
    die Tiefe stürzt; Hängewurzeln und Leuchtbeeren darunter."""
    import wald
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    R = 7 * u + 4
    cy = _r(R * 1.4 + 4)
    insel(w, 0, cy, 0, R)
    einfuegen(w, wald.kleiner_laubbaum(int(w.rng.integers(1, 10 ** 6)), "oak", H=4 + g,
                                       blaetter=[("oak", 0.6), ("flowering_azalea", 0.4)] if k.sonne else
                                       [("cherry", 0.8), ("oak", 0.2)], breit=0.8 + 0.2 * g),
              -round(R * 0.4), cy, -round(R * 0.2))
    tx, tz = round(R * 0.35), round(R * 0.2)
    rr = 1.5 + u
    for x, z in scheibe(rr + 0.5, tx, tz):
        w.setze(x, cy, z, w.b("smooth_quartz"))
    saeulenkranz(w, k, tx, tz, cy + 1, rr, 6, 3 + g)
    kuppel(w, w.b(k.kuppel), tx, tz, cy + 5 + g, rr + 0.8, spitze=None)
    wx = -round(R * 0.2)
    for z in range(0, round(R) + 1):
        w.setze(wx, cy, z, w.b("water", level=0))
    wasserfall(w, wx, cy, round(R) + 1, _r(cy * 0.9))
    hohl(w, 2)
    return w


def regenbogenbruecke(seed, g=2):
    """Regenbogenbrücke: ein siebenfarbiger Bogen aus Glas und Beton spannt sich zwischen zwei Wolkeninseln,
    an den Enden Marmorportale."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    L = 14 * u + 6
    yw = _r(3 * u + 2)
    for sx in (-1, 1):
        wolke(w, round(sx * L), yw, 0, 4 * u + 3, flach=0.45)
    farben = ["red", "orange", "yellow", "lime", "light_blue", "blue", "purple"]
    H = L * 0.7
    for i, f in enumerate(farben):
        r_b = L - i * 0.0
        for t in np.linspace(0, math.pi, int(L * 6)):
            x = round(math.cos(t) * L)
            y = round(yw + 2 + math.sin(t) * H)
            z = i - 3
            w.setze(x, y, z, w.b(f"{f}_stained_glass") if (x + y) % 3 else w.b(f"{f}_concrete"))
    for sx in (-1, 1):
        for z in (-5, 5):
            for y in range(yw + 2, yw + 7 + g):
                w.setze(round(sx * L), y, z, w.b(k.saeule, axis="y"))
            w.setze(round(sx * L), yw + 7 + g, z, w.b(k.licht))
    hohl(w, 2)
    return w


def sonnentempel(seed, g=2):
    """Sonnentempel: kreisrunde Stufenplattform auf Wolken, doppelter Säulenkranz, goldene Kuppel und eine
    riesige Sonnenscheibe mit Strahlen, die über dem Tempel schwebt."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    R = 7 * u + 4
    yw = _r(3 * u + 2)
    wolke(w, 0, yw, 0, R + 4, flach=0.35)
    y0 = yw + _r((R + 4) * 0.2)
    for kk in range(3):
        for x, z in scheibe(R + 1 - kk):
            w.setze(x, y0 + kk, z, k.stein(x, y0 + kk, z, kk / 3) if (x + z + kk) % 5 else w.b(k.gold2))
    Hs = _r(5 * u + 4)
    saeulenkranz(w, k, 0, 0, y0 + 3, R - 2, 12 + 4 * g, Hs)
    saeulenkranz(w, k, 0, 0, y0 + 3, R * 0.5, 8, Hs + 2, gebaelk=True)
    kuppel(w, w.b(k.kuppel), 0, 0, y0 + 3 + Hs + 3, R * 0.5 + 0.5, spitze=None)
    strahlen(w, k, 0, y0 + Hs + _r(R) + 6, 0, 4 * u + 3)
    hohl(w, 2)
    return w


def himmelssternwarte(seed, g=2):
    """Himmelssternwarte: Observatorium mit drehbarer Kupferkuppel und Fernrohr auf einer schwebenden Insel,
    Sternkarte im Boden, Messingringe (Armillarsphäre)."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    R = 6 * u + 4
    cy = _r(R * 1.3 + 3)
    insel(w, 0, cy, 0, R)
    for x, z in scheibe(R - 1):
        w.setze(x, cy, z, w.b("blue_concrete") if (x * 3 + z * 5) % 11 else w.b("sea_lantern")
                if math.hypot(x, z) > R * 0.5 else w.b("polished_deepslate"))
    a = _r(2.5 * u + 2, 3)
    for y in range(cy + 1, cy + 5 + g):
        for x, z in kreisrand(a, -2, -1):
            w.setze(x, y, z, k.stein(x, y, z, 0.4))
    kuppel(w, w.b("waxed_oxidized_copper" if k.sonne else "waxed_weathered_copper"), -2, -1, cy + 5 + g, a + 0.5,
           spitze=None)
    for t in range(_r(4 * u + 3)):
        w.setze(-2 + t, cy + 5 + g + _r(a) + t // 2, -1, w.b("waxed_copper_block") if t < 2 else
                w.b("lightning_rod", facing="east", powered=False, waterlogged=False))
    cx, cz = round(R * 0.5), round(R * 0.3)
    rr = 1.5 + u
    for t in np.linspace(0, 2 * math.pi, 40):
        w.setze(round(cx + math.cos(t) * rr), round(cy + 2 + rr + math.sin(t) * rr), cz, w.b("gold_block"))
        w.setze(cx, round(cy + 2 + rr + math.sin(t) * rr), round(cz + math.cos(t) * rr), w.b("gold_block"))
    w.setze(cx, round(cy + 2 + rr), cz, w.b(k.licht))
    hohl(w, 2)
    return w


def himmelsleuchtturm(seed, g=2):
    """Himmelsleuchtturm: schlanker weißer Turm, der durch mehrere Wolkenschichten ragt, mit goldener Laterne
    und einem Kranz aus Leuchtkristallen ganz oben."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    H = _r(24 * u + 10)
    R = 1.8 * u + 1.8
    wolke(w, 0, 2, 0, 6 * u + 3, flach=0.35)
    for y in range(1, H):
        r = R * (1 - 0.25 * y / H)
        for x, z in kreisrand(r):
            w.setze(x, y, z, k.stein(x, y, z, y / H) if (y // 5) % 2 or y < 4 else w.b(k.gold2) if y % 5 == 0
                    else k.stein(x, y, z, y / H))
    for i, hf in enumerate((0.45, 0.75)):
        wolke(w, round((i - 0.5) * 6), round(H * hf), 0, 3 * u + 2, flach=0.3, seed_off=i)
    for y in range(H, H + 4):
        for x, z in kreisrand(R * 0.75):
            w.setze(x, y, z, w.b(k.glas) if y < H + 3 else w.b(k.gold))
    w.setze(0, H + 1, 0, w.b(k.licht))
    w.setze(0, H + 2, 0, w.b("beacon") if False else w.b(k.licht))
    kuppel(w, w.b(k.kuppel), 0, 0, H + 4, R * 0.8, spitze="gold_block" if k.sonne else "sea_lantern")
    for x, z in kreisrand(R + 2):
        if (x + z) % 2 == 0:
            w.setze(x, H - 1, z, w.b("amethyst_cluster", facing="up", waterlogged=False))
        w.setze(x, H - 2, z, w.b("smooth_quartz_slab", type="top", waterlogged=False))
    hohl(w, 2)
    return w


def luftschiffhafen(seed, g=2):
    """Luftschiffhafen: Ankermast mit Plattform auf einer Wolke, daran vertäut ein Luftschiff mit Ballonhülle,
    Holzgondel, Propellern und Wimpeln."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    R = 8 * u + 4
    wolke(w, 0, _r(3 * u + 2), 0, R, flach=0.35)
    H = _r(12 * u + 6)
    y0 = _r(3 * u + 2) + _r(R * 0.15)
    for y in range(y0, y0 + H):
        for x, z in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            w.setze(x - round(R * 0.4), y, z, w.b("stripped_birch_log", axis="y") if y % 4 else w.b("gold_block"))
    for x, z in scheibe(2.5, -round(R * 0.4), 0):
        w.setze(x, y0 + H, z, w.b("birch_planks"))
    Lb, Rb = 10 * u + 4, 3 * u + 1.5
    bx, by = round(R * 0.25), y0 + H + 1
    S = Skulptur(w, 1.0)
    farbe = ["red", "white"] if k.sonne else ["light_blue", "white"]
    S.mat("b", lambda x, y, z, *_: w.b(f"{farbe[(x // 2) % 2]}_wool"))
    S.mat("h", bl(w, "spruce_planks"))
    S.mat("g", bl(w, "gold_block"))
    S.plus(ell(0, 0, 0, Lb, Rb, Rb), "b")
    for sz in (-1, 1):
        S.plus(lambda X, Y, Z, sz=sz: (X < -Lb * 0.75) & (X > -Lb * 1.05) & (np.abs(Z - sz * Rb * 0.6) < 0.5) &
               (np.abs(Y) < Rb * 0.9), "h")
    S.plus(lambda X, Y, Z: (np.abs(X) < Lb * 0.45) & (Y < -Rb - 1.5) & (Y > -Rb - 3.6) & (np.abs(Z) < Rb * 0.5), "h")
    S.plus(lambda X, Y, Z: (np.abs(X) < Lb * 0.47) & (np.abs(Y + Rb + 3.6) < 0.5) & (np.abs(Z) < Rb * 0.55), "g")
    S.rendern((-Lb - 2, -Rb - 5, -Rb - 2), (Lb + 2, Rb + 2, Rb + 2), versatz=(bx + 0.5, by + Rb + 4, 0.5))
    for sx in (-1, 1):
        for y in range(round(by + 1.5), round(by + 4)):
            w.setze(bx + sx * round(Lb * 0.35), y, 0, w.b("chain", axis="y", waterlogged=False))
    for t in range(round(R * 0.65)):
        w.setze(-round(R * 0.4) + t, y0 + H + 1 + t // 4, 0, MB.seil(w, "x") if False else w.b("chain", axis="x",
                                                                                              waterlogged=False))
    hohl(w, 2)
    return w


def inselkette(seed, g=2):
    """Inselkette: mehrere schwebende Inseln in verschiedenen Höhen, verbunden durch Ketten und Hängebrücken,
    mit Bäumen, Pavillon und Wasserfällen."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    n = 3 + g
    rng = w.rng
    inseln = []
    for i in range(n):
        a = i / n * 2 * math.pi + rng.random() * 0.4
        d = (6 * u + 4) * (1 if i else 0)
        R = (3 + 2 * u) * (1.4 if i == 0 else 0.7 + 0.3 * rng.random())
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        cy = _r(8 * u + 6 + rng.random() * 6 * u)
        insel(w, cx, cy, cz, R)
        inseln.append((cx, cy, cz, R))
    for (ax, ay, az, aR), (bx, by, bz, bR) in zip(inseln[1:], inseln[1:] + []):
        pass
    cx0, cy0, cz0, R0 = inseln[0]
    for (cx, cy, cz, R) in inseln[1:]:
        L = max(abs(cx - cx0), abs(cz - cz0), 1)
        for t in np.linspace(0, 1, int(L * 1.5) + 2):
            x = round(cx0 + (cx - cx0) * t)
            z = round(cz0 + (cz - cz0) * t)
            y = round(cy0 + (cy - cy0) * t - math.sin(t * math.pi) * 1.5)
            w.setze(x, y + 1, z, w.b("birch_slab", type="bottom", waterlogged=False), ueberschreiben=False)
    saeulenkranz(w, k, cx0, cz0, cy0 + 1, 2 + u * 0.5, 6, 3 + g)
    kuppel(w, w.b(k.kuppel), cx0, cz0, cy0 + 5 + g, 2.8 + u * 0.5, spitze=None)
    for (cx, cy, cz, R) in inseln[1:]:
        if rng.random() < 0.5:
            for y in range(cy + 1, cy + 4 + g):
                w.setze(cx, y, cz, w.b("birch_log", axis="y"))
            for x, z in scheibe(2 + u * 0.5, cx, cz):
                for y in (cy + 3 + g, cy + 4 + g):
                    w.setze(x, y, z, laub(w, "flowering_azalea" if k.sonne else "cherry"))
        else:
            wasserfall(w, cx, cy, round(cz + R), _r(cy * 0.6))
    hohl(w, 2)
    return w


def harfenhalle(seed, g=2):
    """Halle der Harfen: offene Säulenhalle auf Wolken mit goldenen Riesenharfen (Saiten aus Ketten),
    Marmorbänken und Lichtern zwischen den Säulen."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    a, b = _r(8 * u + 4), _r(4 * u + 3)
    yw = _r(3 * u + 2)
    wolke(w, 0, yw, 0, a + 4, flach=0.3)
    y0 = yw + _r((a + 4) * 0.15)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.setze(x, y0, z, w.b("smooth_quartz") if (x + z) % 2 else w.b(k.gold2) if x % 4 == 0 else
                    w.b("quartz_bricks"))
    Hs = _r(5 * u + 4)
    for x in range(-a, a + 1, 3):
        for z in (-b, b):
            w.setze(x, y0 + 1, z, w.b("quartz_bricks"))
            for y in range(y0 + 2, y0 + Hs):
                w.setze(x, y, z, w.b(k.saeule, axis="y"))
            w.setze(x, y0 + Hs, z, w.b("chiseled_quartz_block"))
    for x in range(-a - 1, a + 2):
        for z in range(-b - 1, b + 2):
            if abs(z) >= b - 1 or abs(x) >= a:
                w.setze(x, y0 + Hs + 1, z, k.stein(x, y0 + Hs + 1, z, 0.9))
    P.satteldach(w, P.Dach(w, k.dach), -a - 1, -b - 1, a + 1, b + 1, y0 + Hs + 2, ue=0, first_x=True)
    for i in range(1 + g):
        hx = -a + 3 + i * max(4, (2 * a - 4) // max(1, g))
        hh = _r(3 * u + 3, 4)
        for t in np.linspace(0, 1, hh * 3):
            w.setze(hx, round(y0 + 1 + t * hh), round(-1 + math.sin(t * math.pi) * -1.5), w.b(k.gold))
        for y in range(y0 + 1, y0 + hh + 1):
            w.setze(hx, y, 1, w.b(k.gold))
        for z in range(-1, 2):
            w.setze(hx, y0 + hh + 1, z, w.b(k.gold))
            for y in range(y0 + 2, y0 + hh + 1):
                if z == 0:
                    w.setze(hx, y, z, w.b("chain", axis="y", waterlogged=False))
    hohl(w, 2)
    return w


def windtempel(seed, g=1):
    """Tempel der Winde: offener Kuppelbau mit acht Bögen, Windspiele aus Ketten und Glocken, Wimpel in allen
    Farben, Wetterfahne und Wolkenringe."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    R = 5 * u + 3
    yw = _r(3 * u + 2)
    wolke(w, 0, yw, 0, R + 3, flach=0.35)
    y0 = yw + _r((R + 3) * 0.2)
    for x, z in scheibe(R + 1):
        w.setze(x, y0, z, w.b("smooth_quartz") if math.hypot(x, z) % 3 < 1.5 else w.b("quartz_bricks"))
    Hs = _r(7 * u + 4)
    saeulenkranz(w, k, 0, 0, y0 + 1, R, 8, Hs)
    kuppel(w, w.b(k.kuppel), 0, 0, y0 + Hs + 2, R - 0.5, form="spitz" if k.sonne else "rund", spitze=None)
    w.setze(0, y0 + Hs + 3 + _r((R - 0.5) * (1.9 if k.sonne else 1.0)), 0,
            w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for i in range(8):
        a = (i + 0.5) / 8 * 2 * math.pi
        x, z = round(math.cos(a) * (R - 0.5)), round(math.sin(a) * (R - 0.5))
        for y in range(y0 + Hs - 1, y0 + Hs + 2):
            w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False))
        w.setze(x, y0 + Hs - 2, z, w.b("bell", attachment="ceiling", facing="north", powered=False) if i % 2 else
                w.b("end_rod", facing="down"))
    farben = ["red", "orange", "yellow", "lime", "light_blue", "magenta", "white", "cyan"]
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x, z = round(math.cos(a) * (R + 1.5)), round(math.sin(a) * (R + 1.5))
        w.setze(x, y0 + Hs + 2, z, MB.fahne(w, farben[i], ["east", "south", "west", "north"][int((a + math.pi / 4)
                                                                                              / (math.pi / 2)) % 4]))
    hohl(w, 2)
    return w


def pegasus(seed, g=2):
    """Pegasus-Statue: ein geflügeltes Pferd steigt auf den Hinterbeinen von einem Wolkensockel auf, Flügel weit
    gespreizt, Mähne aus Gold."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    s = 0.6 * u + 0.25
    yw = _r(3 * u + 2)
    wolke(w, 0, yw, 0, 9 * s + 4, flach=0.4)
    ys = yw + _r((9 * s + 4) * 0.25)
    S = Skulptur(w, s)
    S.mat("k", sk(Mat(w, ["white_concrete", "smooth_quartz", "calcite", "white_wool"]), ys, ys + 24 * s))
    S.mat("m", bl(w, k.gold))
    S.mat("h", bl(w, "light_gray_concrete"))
    # Rumpf schräg aufgerichtet
    S.plus(kap((-3, 6, 0), (2.5, 11, 0), 2.6, 2.4), "k")
    S.plus(kap((2.5, 11.5, 0), (4.5, 16, 0), 1.4, 1.1), "k")
    S.plus(ell(5.6, 17, 0, 2.2, 1.2, 1.1), "k")
    S.plus(kap((6.5, 16.8, 0), (8.0, 16.0, 0), 0.9, 0.7), "k")
    S.plus(kap((3.0, 13, 0), (4.6, 17.5, 0), 0.6, 0.5), "m")
    for sz in (-1, 1):
        S.plus(kap((-3.5, 5.5, sz * 1.2), (-4.0, 2.5, sz * 1.4), 0.9, 0.7), "k")
        S.plus(kap((-4.0, 2.5, sz * 1.4), (-3.5, 0.2, sz * 1.4), 0.6, 0.5), "k")
        S.plus(kap((2.0, 9.5, sz * 1.0), (4.5, 8.5, sz * 1.3), 0.7, 0.6), "k")
        S.plus(kap((4.5, 8.5, sz * 1.3), (4.0, 6.5, sz * 1.3), 0.55, 0.45), "k")
        S.plus(ell(6.3, 18.6, sz * 0.5, 0.3, 0.7, 0.25), "k")
        # Flügel
        S.plus(lambda X, Y, Z, sz=sz: ((((X + 0.5) / 6.5) ** 2 + ((Y - 15) / 4.5) ** 2) < 1) &
               (np.abs(Z - sz * (2.6 + 0.6 * np.maximum(0, Y - 11))) < 0.8) & (Y > 11), "k")
    S.plus(kap((-5, 6.5, 0), (-8, 3, 0), 0.9, 0.4), "m")
    S.rendern((-11, -1, -12), (11, 24, 12), versatz=(0.5, ys + 0.01, 0.5), dreh=dreh_y(0.4))
    hohl(w, 2)
    return w


def himmelsgarten(seed, g=2):
    """Himmelsgarten: schwebende Insel voller blühender Kirsch- und Azaleenbäume, Teich mit Seerosen, weiße
    Pergola, Wasserfall und Schmetterlingsblumen."""
    import wald
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    R = 9 * u + 4
    cy = _r(R * 1.2 + 4)
    insel(w, 0, cy, 0, R)
    rng = w.rng
    for i in range(3 + g * 2):
        a = i * 2.39996
        d = R * 0.65 * math.sqrt((i + 0.5) / (3 + g * 2))
        einfuegen(w, wald.kleiner_laubbaum(int(rng.integers(1, 10 ** 6)), "cherry" if i % 2 else "birch", H=3 + g,
                                           blaetter=[("cherry", 0.8), ("flowering_azalea", 0.2)] if i % 2 else
                                           [("flowering_azalea", 0.7), ("azalea", 0.3)], breit=0.8),
                  round(math.cos(a) * d), cy, round(math.sin(a) * d))
    for x, z in scheibe(R * 0.25, round(R * 0.3), -round(R * 0.35)):
        w.setze(x, cy, z, w.b("water", level=0))
        if rng.random() < 0.2:
            w.setze(x, cy + 1, z, w.b("lily_pad"))
    for x, z in scheibe(R * 0.9):
        if w.frei(x, cy + 1, z) and rng.random() < 0.25 and (x, cy, z) in w.bloecke and \
                w.P.name(w.bloecke[(x, cy, z)]) == "minecraft:grass_block":
            w.setze(x, cy + 1, z, w.b(["pink_tulip", "allium", "azure_bluet", "lily_of_the_valley", "pink_petals"
                                       if False else "oxeye_daisy"][int(rng.integers(5))]))
    wasserfall(w, -round(R * 0.6), cy, round(R * 0.6), _r(cy * 0.8))
    hohl(w, 2)
    return w


def donnertempel(seed, g=2):
    """Donnertempel: eine dunkle Gewitterwolke trägt einen Kupfertempel mit Blitzableitern, aus der Wolke zucken
    Blitze aus gelbem Glas; Regen aus Glasfäden."""
    w = _welt(seed)
    u = U[g]
    R = 9 * u + 4
    yw = _r(10 * u + 6)
    S = Skulptur(w, 1.0)
    S.mat("w", lambda x, y, z, *_: w.b("gray_wool") if (x + y + z) % 3 else w.b("light_gray_wool")
          if y > yw else w.b("gray_concrete"))
    for i in range(8):
        a = i * 2.39996
        d = R * 0.6 * math.sqrt((i + 0.5) / 8)
        rr = R * (0.45 + 0.1 * (i % 3))
        S.plus(ell(math.cos(a) * d, 0, math.sin(a) * d, rr, rr * 0.45, rr), "w")
    S.rendern((-R * 2, -R, -R * 2), (R * 2, R, R * 2), versatz=(0.5, yw, 0.5))
    y0 = yw + _r(R * 0.25)
    a = _r(4 * u + 2, 3)
    st = P.Stil(w, wand=Mat(w, ["waxed_oxidized_cut_copper", "waxed_weathered_cut_copper", "waxed_oxidized_copper"]),
                sockel="schwarzstein", gesims="polished_blackstone_brick", dach="kupfer", holz="dark_oak",
                laeden=False, blumen=0, fenster="yellow_stained_glass", fensterart="bogen")
    P.gebaeude(w, st, -a, -a, a, a, y0=y0, etagen=1, eh=6, dach="walm", tuer="south", gauben=False, kamine=0,
               steil=True)
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in range(y0, y0 + 9 + g * 2):
                w.setze(sx * (a + 1), y, sz * (a + 1), w.b("waxed_copper_block") if y < y0 + 7 else
                        w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    rng = w.rng
    for i in range(2 + g):
        x, z = round(rng.normal(0, R * 0.4)), round(rng.normal(0, R * 0.4))
        y = yw - _r(R * 0.35)
        while y > 1:
            w.setze(x, y, z, w.b("yellow_stained_glass") if rng.random() < 0.7 else w.b("glowstone"))
            y -= 1
            if rng.random() < 0.35:
                x += int(rng.integers(-1, 2))
                z += int(rng.integers(-1, 2))
    for i in range(10 + 6 * g):
        x, z = round(rng.normal(0, R * 0.5)), round(rng.normal(0, R * 0.5))
        for y in range(yw - _r(R * 0.35) - int(rng.integers(2, 8)), yw - _r(R * 0.35)):
            w.setze(x, y, z, w.b("light_blue_stained_glass_pane", north=False, south=False, east=False, west=False,
                                 waterlogged=False))
    hohl(w, 2)
    return w


def sonnenuhr(seed, g=2):
    """Himmels-Sonnenuhr: kreisrundes Zifferblatt aus Marmor mit goldenen Stundenmarken auf einer Wolke,
    schräger goldener Zeiger (Gnomon), Stundensäulen und Tierkreis-Mosaik."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    R = 9 * u + 4
    yw = _r(3 * u + 2)
    wolke(w, 0, yw, 0, R + 2, flach=0.3)
    y0 = yw + _r((R + 2) * 0.15)
    farben = ["yellow", "orange", "red", "magenta", "purple", "blue", "light_blue", "cyan", "lime", "green", "brown",
              "white"]
    for x, z in scheibe(R):
        d = math.hypot(x, z)
        a = (math.atan2(z, x) + math.pi) / (2 * math.pi)
        if d > R - 2:
            b = w.b(f"{farben[int(a * 12) % 12]}_glazed_terracotta", facing="north") if False else \
                w.b(f"{farben[int(a * 12) % 12]}_concrete")
        elif abs(d - R * 0.6) < 0.6:
            b = w.b(k.gold)
        else:
            b = w.b("smooth_quartz") if (x + z) % 2 else w.b("calcite")
        w.setze(x, y0, z, b)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        for t in np.linspace(R * 0.62, R - 2.2, int(R)):
            w.setze(round(math.cos(a) * t), y0, round(math.sin(a) * t), w.b(k.gold2))
        x, z = round(math.cos(a) * (R + 0.5)), round(math.sin(a) * (R + 0.5))
        for y in range(y0, y0 + 3 + (i % 3 == 0) * 2):
            w.setze(x, y, z, w.b(k.saeule, axis="y"))
        w.setze(x, y0 + 3 + (i % 3 == 0) * 2, z, w.b(k.licht))
    L = R * 0.85
    for x in range(round(-L * 0.4), round(L * 0.5) + 1):
        hy = round((x + L * 0.4) * 0.8)
        for y in range(y0 + 1, y0 + 2 + hy):
            w.setze(x, y, 0, w.b(k.gold) if y == y0 + 1 + hy else w.b(k.gold2) if (x + y) % 3 else w.b(k.gold))
    hohl(w, 2)
    return w


def mondpavillon(seed, g=1):
    """Mondpavillon: zierlicher Silberpavillon mit Spitzkuppel auf einer kleinen Wolke, eine schwebende
    Mondsichel daneben, Sternenstaub (Endstäbe) und Laternen."""
    w = _welt(seed)
    u = U[g]
    R = 3 * u + 2.5
    yw = _r(3 * u + 2)
    wolke(w, 0, yw, 0, R + 5, flach=0.35)
    y0 = yw + _r((R + 5) * 0.2)
    for x, z in scheibe(R + 1):
        w.setze(x, y0, z, w.b("calcite") if (x + z) % 2 else w.b("light_blue_terracotta"))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        for y in range(y0 + 1, y0 + 5 + g):
            w.setze(x, y, z, w.b("iron_bars", north=True, south=True, east=True, west=True, waterlogged=False)
                    if y % 2 else w.b("quartz_pillar", axis="y"))
    kuppel(w, w.b("light_blue_concrete"), 0, 0, y0 + 5 + g, R + 0.5, form="spitz", spitze="sea_lantern")
    w.setze(0, y0 + 4 + g, 0, MB.laterne(w, "chain_lantern", haengend=True))
    s = 0.4 * u + 0.2
    S = Skulptur(w, s)
    S.mat("m", lambda x, y, z, *_: w.b("pearlescent_froglight", axis="y") if (x + y) % 4 == 0 else w.b("calcite"))
    S.plus(lambda X, Y, Z: ((X ** 2 + (Y - 10) ** 2) < 64) & ((X - 3) ** 2 + (Y - 11) ** 2 > 45) &
           (np.abs(Z) < 1.0), "m")
    S.rendern((-9, 0, -2), (9, 20, 2), versatz=(round(R + 6 * s + 3) + 0.5, y0 + 2.01, 0.5))
    rng = w.rng
    for i in range(8 + 4 * g):
        w.setze(int(rng.integers(-R - 6, R + 12)), y0 + 3 + int(rng.integers(0, 12)), int(rng.integers(-R - 4, R + 5)),
                w.b("end_rod", facing="up"))
    hohl(w, 2)
    return w


def himmelstreppe(seed, g=2):
    """Himmelstreppe: eine freischwebende Wendeltreppe aus Marmor windet sich durch drei Wolkenringe nach oben
    zu einem goldenen Lichttor."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    H = _r(22 * u + 10)
    R = 4 * u + 3
    wolke(w, 0, 2, 0, R + 3, flach=0.3)
    n = H * 3
    for i in range(n):
        a = i / 14 * 2 * math.pi
        y = 3 + i // 3
        if y >= H:
            break
        for rr in np.linspace(R - 1.5, R + 0.5, 3):
            x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
            w.setze(x, y, z, w.b("smooth_quartz_slab", type="top", waterlogged=False) if i % 3 else
                    w.b("smooth_quartz"))
        if i % 7 == 0:
            x, z = round(math.cos(a) * (R + 1.5)), round(math.sin(a) * (R + 1.5))
            w.setze(x, y + 1, z, w.b(k.licht))
    for i, hf in enumerate((0.35, 0.65)):
        for x, z in kreisrand(R + 3):
            if (x + z + i) % 3:
                w.setze(x, round(H * hf), z, w.b("white_wool"))
                if (x + z) % 2:
                    w.setze(x, round(H * hf) + 1, z, w.b("white_wool"))
    for y in range(H, H + 7):
        for sx in (-2, 2):
            w.setze(sx, y, 0, w.b(k.saeule, axis="y"))
    strahlen(w, k, 0, H + 8, 0, 3 + u)
    hohl(w, 2)
    return w


def sternbrunnen(seed, g=1):
    """Sternenbrunnen: Becken aus Lichtwasser (Prismarin und Seelaternen) auf einer Wolke, in der Mitte eine
    Säule aus Licht und Kristall, von der Sterne aufsteigen."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    R = 5 * u + 3
    yw = _r(3 * u + 2)
    wolke(w, 0, yw, 0, R + 3, flach=0.35)
    y0 = yw + _r((R + 3) * 0.2)
    for x, z in scheibe(R):
        w.setze(x, y0, z, w.b("sea_lantern") if (x + z) % 4 == 0 else w.b("prismarine_bricks"))
        w.setze(x, y0 + 1, z, w.b("water", level=0))
    for x, z in kreisrand(R + 0.5):
        w.setze(x, y0 + 1, z, w.b("smooth_quartz"))
        w.setze(x, y0 + 2, z, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
    Hs = _r(6 * u + 4)
    for y in range(y0 + 1, y0 + Hs):
        for x, z in kreisrand(1.0):
            w.setze(x, y, z, w.b("sea_lantern") if y % 3 == 0 else w.b(k.glas))
        w.setze(0, y, 0, w.b(k.licht))
    w.setze(0, y0 + Hs, 0, w.b("amethyst_block"))
    w.setze(0, y0 + Hs + 1, 0, w.b("amethyst_cluster", facing="up", waterlogged=False))
    rng = w.rng
    for i in range(10 + 5 * g):
        a = rng.random() * 2 * math.pi
        d = rng.random() * R
        w.setze(round(math.cos(a) * d), y0 + Hs + 1 + int(rng.integers(0, 6 + 3 * g)), round(math.sin(a) * d),
                w.b("end_rod", facing="up"))
    hohl(w, 2)
    return w


def wolkenstadt(seed, g=2):
    """Wolkenstadt: eine Ansammlung weißer Häuser mit goldenen und blauen Kuppeln auf einem großen Wolkenfeld,
    verbunden durch Brücken, ein Glockenturm in der Mitte."""
    w = _welt(seed)
    k = Himmel(w, seed)
    u = U[g]
    R = 12 * u + 6
    yw = _r(3 * u + 2)
    wolke(w, 0, yw, 0, R, flach=0.35, dichte=10)
    y0 = yw + _r(R * 0.18)
    rng = w.rng
    st = P.Stil(w, wand="marmor", sockel="kalkstein", gesims="quartz", dach=k.dach, holz="birch", laeden=False,
                blumen=0.6, fenster=k.glas, fensterart="bogen")
    P.turm(w, st, 0, 0, y0, _r(14 * u + 6), max(2.0, 2 * u), dach="glocke" if k.sonne else "kegel", krone=False,
           fahne=None)
    n = 4 + 2 * g
    for i in range(n):
        a = i / n * 2 * math.pi + rng.random() * 0.3
        d = R * (0.4 + 0.25 * (i % 2))
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        aa = 2 + int(rng.integers(0, 2 + g // 2))
        P.gebaeude(w, st, cx - aa, cz - aa, cx + aa, cz + aa, y0=y0, etagen=1 + (i % 2), eh=4, dach="flach"
                   if False else "walm", tuer="south", gauben=False, kamine=0)
        if i % 3 == 0:
            kuppel(w, w.b(k.kuppel if i % 2 else "light_blue_concrete"), cx, cz, y0 + 4 * (1 + i % 2) + 2,
                   aa - 0.5, form="zwiebel", spitze=None)
    for x, z in scheibe(R * 0.9):
        if (x, y0 - 1, z) in w.bloecke and w.frei(x, y0, z) and rng.random() < 0.02:
            w.setze(x, y0, z, w.b(k.licht))
    hohl(w, 2)
    return w


HIMMEL = {
    "himmelstor": ("Himmelstor", himmelstor),
    "wolkenpalast": ("Wolkenpalast", wolkenpalast),
    "engelsstatue": ("Engelsstatue", engelsstatue),
    "schwebende_insel": ("Schwebende Insel", schwebende_insel),
    "regenbogenbruecke": ("Regenbogenbrücke", regenbogenbruecke),
    "sonnentempel": ("Sonnentempel", sonnentempel),
    "himmelssternwarte": ("Himmelssternwarte", himmelssternwarte),
    "himmelsleuchtturm": ("Himmelsleuchtturm", himmelsleuchtturm),
    "luftschiffhafen": ("Luftschiffhafen", luftschiffhafen),
    "inselkette": ("Inselkette", inselkette),
    "harfenhalle": ("Halle der Harfen", harfenhalle),
    "windtempel": ("Tempel der Winde", windtempel),
    "pegasus": ("Pegasus", pegasus),
    "himmelsgarten": ("Himmelsgarten", himmelsgarten),
    "donnertempel": ("Donnertempel", donnertempel),
    "sonnenuhr": ("Himmels-Sonnenuhr", sonnenuhr),
    "mondpavillon": ("Mondpavillon", mondpavillon),
    "himmelstreppe": ("Himmelstreppe", himmelstreppe),
    "sternbrunnen": ("Sternenbrunnen", sternbrunnen),
    "wolkenstadt": ("Wolkenstadt", wolkenstadt),
}

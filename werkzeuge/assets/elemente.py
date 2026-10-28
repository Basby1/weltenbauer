"""Elementarreiche – vier Pakete.
Unterwasser: Korallenpalast, Glaskuppel-Station, versunkener Tempel, Korallenriff, Riesenmuschel,
Säulenhalle, Riesenqualle.  Vulkan: Vulkan, Glutstrom-Klippe, Feuertempel, Riesenschmiede, Basaltfeld,
Obsidianturm, Glutbaum.  Nether: Netherfestung, Seelenschrein, Pilzriesenhain, Bastion, Portalruine,
Glutsee-Plattform, Seelenbrücke.  End: End-Turm, Obsidiansplitter, Chorusgarten, Leerenschiff,
Leerenbogen, End-Insel, Leerenportal."""

from __future__ import annotations

import math

import numpy as np

from lib import Verlauf, Welt
from skulptur import Skulptur, ell, kap, kegel, kreisrand, platte, scheibe, treppe, verbinde, zur_mitte

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _flaeche(w, r, wahl, cx=0, cz=0, y=0):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, y, z, wahl(x, z), ueberschreiben=False)


KORALLEN = ["tube", "brain", "bubble", "fire", "horn"]


def _koralle(w, x, y, z, art=None):
    art = art or KORALLEN[int(w.rng.integers(5))]
    k = w.rng.random()
    if k < 0.45:
        w.setze(x, y, z, w.b(f"{art}_coral_block"))
    elif k < 0.75:
        w.setze(x, y, z, w.b(f"{art}_coral_fan", waterlogged=True))
    elif k < 0.9:
        w.setze(x, y, z, w.b(f"{art}_coral", waterlogged=True))
    else:
        w.setze(x, y, z, w.b("sea_pickle", pickles=int(w.rng.integers(1, 5)), waterlogged=True))


def _seegras(w, x, y, z):
    if w.rng.random() < 0.5:
        w.setze(x, y, z, w.b("seagrass"))
    else:
        h = int(w.rng.integers(2, 6))
        for k in range(h - 1):
            w.setze(x, y + k, z, w.b("kelp_plant"))
        w.setze(x, y + h - 1, z, w.b("kelp", age=25))


def _meeresboden(w, r, dichte=0.25, cx=0, cz=0):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, w.b("sand") if w.rng.random() < 0.7 else w.b("gravel"), ueberschreiben=False)
        if w.frei(x, 1, z) and w.rng.random() < dichte:
            (_koralle if w.rng.random() < 0.4 else _seegras)(w, x, 1, z)


def _kuppel(w, cx, cy, cz, R, rahmen, glas="light_blue_stained_glass", luft=True):
    """Glaskuppel (Halbkugel) mit Rahmenrippen; innen Luft (verdrängt Wasser)."""
    for x in range(cx - int(R) - 1, cx + int(R) + 2):
        for z in range(cz - int(R) - 1, cz + int(R) + 2):
            for y in range(0, int(R) + 2):
                d = math.sqrt((x - cx) ** 2 + (z - cz) ** 2 + y * y)
                if R - 1 < d <= R:
                    a = math.atan2(z - cz, x - cx)
                    rippe = (a * 6 / math.pi) % 1 < 0.17 or y == 0
                    w.setze(x, cy + y, z, w.b(rahmen) if rippe else w.b(glas))
                elif d <= R - 1 and luft and y > 0:
                    w.setze(x, cy + y, z, 0)


# ============================================================================ Unterwasser

class Meer:
    def __init__(self, w, seed):
        self.w = w
        self.tief = _stil(seed) == 1
        self.stein = Verlauf(w, "Prismarin", ["dark_prismarine", "prismarine", "prismarine_bricks", "sea_lantern"]) \
            if not self.tief else Verlauf(w, "Tiefsee", ["deepslate_tiles", "dark_prismarine", "prismarine_bricks",
                                                         "polished_deepslate"])
        self.rahmen = "prismarine_bricks" if not self.tief else "waxed_oxidized_cut_copper"
        self.licht = w.b("sea_lantern")


def korallenpalast(seed, g=2):
    """Palast aus Prismarin mit Korallenbewuchs, Glaskuppeln, Säulengang und Leuchtsteinen."""
    w = _welt(seed)
    m = Meer(w, seed)
    u = U[g]
    h = _r(7 * u + 3, 5)
    H = _r(6 * u + 3, 5)
    _meeresboden(w, h + 8)
    for y in range(0, H + 1):
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                ring = max(abs(x), abs(z))
                if y == 0 or ring == h or y == H:
                    fen = ring == h and 2 <= y <= H - 2 and (x % 3 == 0 or z % 3 == 0)
                    w.setze(x, y, z, w.b("light_blue_stained_glass") if fen else
                            (m.licht if (x + y + z) % 11 == 0 else m.stein(0.3 + 2 * y / H + w.rng.random() * 0.6, x, y, z)))
                else:
                    w.setze(x, y, z, 0)
    _kuppel(w, 0, H, 0, h * 0.75, m.rahmen)
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * h, sz * h
            for y in range(0, H + _r(5 * u, 3)):
                for x, z in kreisrand(1.4 * u + 0.6, cx, cz):
                    w.setze(x, y, z, m.stein(1 + w.rng.random(), x, y, z))
            _kuppel(w, cx, H + _r(5 * u, 3), cz, 1.6 * u + 1, m.rahmen, luft=False)
    for (x, y, z) in list(w.bloecke):
        if w.rng.random() < 0.04 and y > 0 and w.frei(x, y + 1, z):
            _koralle(w, x, y + 1, z)
    for x in range(-1, 2):
        for y in (1, 2):
            w.setze(x, y, h, 0)
    return w


def glaskuppel(seed, g=1):
    """Unterwasser-Station: große Glaskuppel mit Luft, Kupferrippen, Wohnmodul, Algengarten, Leuchtern
    und Röhrengängen zu kleinen Kuppeln."""
    w = _welt(seed)
    m = Meer(w, seed)
    u = U[g]
    R = 6 * u + 3
    _meeresboden(w, R + 10, 0.2)
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("smooth_stone") if (x + z) % 2 else w.b("polished_andesite"))
    _kuppel(w, 0, 0, 0, R, m.rahmen)
    for x, z in scheibe(R * 0.4):
        w.setze(x, 1, z, w.b("moss_block"))
        if w.rng.random() < 0.4:
            w.setze(x, 2, z, w.b(["fern", "grass", "azure_bluet"][int(w.rng.integers(3))]))
    w.setze(0, int(R) - 1, 0, w.b("chain", axis="y", waterlogged=False))
    w.setze(0, int(R) - 2, 0, w.b("lantern", hanging=True, waterlogged=False))
    for i in range(1 + g):
        a = i * 2 * math.pi / (1 + g) + 0.5
        d = R + 3 * u + 3
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        r2 = 2 * u + 1.5
        for x, z in scheibe(r2, cx, cz):
            w.setze(x, 0, z, w.b("smooth_stone"))
        _kuppel(w, cx, 0, cz, r2, m.rahmen)
        n = int(d)
        for k in range(int(R) - 1, n - int(r2) + 2):
            x, z = round(math.cos(a) * k), round(math.sin(a) * k)
            for dy in range(0, 4):
                for s in (-1, 0, 1):
                    px, pz = x + round(-math.sin(a) * s), z + round(math.cos(a) * s)
                    if dy in (0, 3) or abs(s) == 1:
                        w.setze(px, dy, pz, w.b("light_blue_stained_glass") if dy > 0 else w.b("smooth_stone"))
                    else:
                        w.setze(px, dy, pz, 0)
    return w


def versunkener_tempel(seed, g=2):
    """Versunkener Tempel: bewachsene Säulenfront, eingestürzter Giebel, Treppe, Korallen und Tang."""
    w = _welt(seed)
    m = Meer(w, seed)
    u = U[g]
    L, B = _r(9 * u + 4, 6), _r(6 * u + 3, 4)
    H = _r(7 * u + 3, 5)
    _meeresboden(w, L + 6, 0.35)
    for x in range(-L, L + 1):
        for z in range(-B, B + 1):
            w.setze(x, 0, z, m.stein(1 + w.rng.random(), x, 0, z))
            w.setze(x, 1, z, m.stein(1.2 + w.rng.random(), x, 1, z))
    for x in range(-L + 1, L, 3):
        for s in (-1, 1):
            hh = H if w.rng.random() < 0.7 else int(H * (0.3 + 0.4 * w.rng.random()))
            for y in range(2, hh + 1):
                w.setze(x, y, s * (B - 1), w.b("prismarine_bricks" if y % 3 else "dark_prismarine"))
    for x in range(-L, L + 1):
        if w.rng.random() < 0.75:
            for z in range(-B, B + 1):
                if w.rng.random() < 0.85:
                    w.setze(x, H + 1, z, m.stein(2, x, H + 1, z))
    for kk in range(B):
        for z in range(-B + kk, B - kk + 1):
            if w.rng.random() < 0.7:
                w.setze(L, H + 2 + kk, z, m.stein(2.5, L, H + 2, z))
    for (x, y, z) in list(w.bloecke):
        if y > 1 and w.frei(x, y + 1, z) and w.rng.random() < 0.1:
            (_koralle if w.rng.random() < 0.6 else _seegras)(w, x, y + 1, z)
    w.setze(0, 2, 0, m.licht)
    return w


def korallenriff(seed, g=1):
    """Buntes Korallenriff mit Korallenstöcken verschiedener Höhe, Fächern, Seegurken und Tangwäldern."""
    w = _welt(seed)
    u = U[g]
    R = 9 * u + 5
    _meeresboden(w, R, 0.15)
    S = Skulptur(w, 1.0)
    farben = [w.b(f"{k}_coral_block") for k in KORALLEN]
    S.mat("k", lambda x, y, z, *_: farben[(x // 2 + z // 3 + y // 2) % 5])
    for i in range(5 + 3 * g):
        a = i * 2.39996
        d = R * 0.85 * math.sqrt((i + 0.5) / (5 + 3 * g))
        cx, cz = math.cos(a) * d, math.sin(a) * d
        r = (1.0 + w.rng.random()) * u + 0.8
        S.plus(ell(cx, 0.5, cz, r, r * (0.8 + w.rng.random() * 1.2), r), "k")
    S.rendern((-R, 0, -R), (R, 6 * u + 4, R), versatz=(0.5, 1, 0.5))
    for (x, y, z) in list(w.bloecke):
        if y >= 1 and w.frei(x, y + 1, z) and w.rng.random() < 0.35:
            _koralle(w, x, y + 1, z)
    return w


def riesenmuschel(seed, g=1):
    """Riesige, halb geöffnete Muschel mit gerippter Schale und leuchtender Perle."""
    w = _welt(seed)
    u = U[g]
    _meeresboden(w, 6 * u + 4, 0.3)
    S = Skulptur(w, u)
    S.mat("s", lambda x, y, z, lx, ly, lz: w.b("pink_terracotta" if int(math.atan2(lz, lx) * 5) % 2 else
                                                 "white_terracotta") if ly < 2.5 else
          w.b("pink_concrete" if int(math.atan2(lz, lx - 0.5) * 5) % 2 else "white_concrete"))
    S.mat("p", w.b("pearlescent_froglight"))
    S.mat("i", w.b("pink_wool"))
    S.plus(lambda X, Y, Z: ((X / 5) ** 2 + (Y / 2) ** 2 + (Z / 4.5) ** 2 <= 1) & (((X / 5) ** 2 + ((Y - 0.6) / 1.4) ** 2
                                                                                   + (Z / 3.8) ** 2) > 1) & (Y >= 0), "s")
    S.plus(lambda X, Y, Z: (((X + 1) / 5) ** 2 + ((Y - 3.5 - 0.5 * X) / 1.6) ** 2 + (Z / 4.5) ** 2 <= 1)
           & ((((X + 1) / 4.6) ** 2 + ((Y - 3.0 - 0.5 * X) / 1.2) ** 2 + (Z / 4.0) ** 2) > 1), "s")
    S.plus(ell(0, 0.5, 0, 4.2, 0.6, 3.6), "i")
    S.plus(ell(0.5, 1.8, 0, 1.4, 1.4, 1.4), "p")
    S.rendern((-6, 0, -6), (6, 8, 6), versatz=(0.5, 1, 0.5))
    return w


def saeulenhalle(seed, g=2):
    """Versunkene Säulenhalle: kreisrunde Kolonnade mit Kuppelgerüst und Leuchtsteinen im Kreis."""
    w = _welt(seed)
    m = Meer(w, seed)
    u = U[g]
    R = 8 * u + 4
    H = _r(8 * u + 3, 6)
    _meeresboden(w, R + 5, 0.25)
    for x, z in scheibe(R + 1):
        w.setze(x, 0, z, m.stein(1 + w.rng.random(), x, 0, z))
    n = 8 + 4 * g
    for i in range(n):
        a = i * 2 * math.pi / n
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b("prismarine_bricks") if y % 4 else w.b("dark_prismarine"))
    for x, z in kreisrand(R):
        w.setze(x, H + 1, z, m.stein(2, x, H + 1, z))
    for i in range(8):
        a = i * math.pi / 4
        for t in np.linspace(0, 1, int(R * 2)):
            r = R * (1 - t)
            y = H + 1 + int(math.sin(t * math.pi / 2) * R * 0.6)
            w.setze(round(math.cos(a) * r), y, round(math.sin(a) * r), m.stein(2.5, 0, y, 0))
    for x, z in kreisrand(R * 0.4):
        w.setze(x, 1, z, m.licht)
    return w


def riesenqualle(seed, g=1):
    """Schwebende Riesenqualle: leuchtender Glasschirm, Innenleben und lange Nesselfäden."""
    w = _welt(seed)
    u = U[g]
    _meeresboden(w, 5 * u + 3, 0.2)
    R = 4 * u + 2
    cy = 10 * u + 6
    glas = ["pink_stained_glass", "magenta_stained_glass", "purple_stained_glass"] if _stil(seed) == 0 else \
        ["light_blue_stained_glass", "cyan_stained_glass", "white_stained_glass"]
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            for y in range(-1, int(R) + 1):
                d = math.sqrt(x * x + z * z + (y * 1.3) ** 2)
                if R - 1.1 < d <= R and y >= -0.5:
                    w.setze(x, int(cy) + y, z, w.b(glas[(x + z + y) % 3]))
                elif d < R * 0.4 and y >= 0:
                    w.setze(x, int(cy) + y, z, w.b("pearlescent_froglight" if _stil(seed) == 0 else "sea_lantern"))
    for i in range(10 + 4 * g):
        a = i * 2.39996
        r = R * (0.3 + 0.6 * ((i * 7) % 10) / 10)
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        lang = int(cy * (0.4 + 0.5 * w.rng.random()))
        for k in range(lang):
            w.setze(x + round(math.sin(k * 0.3 + i) * 0.6), int(cy) - 1 - k, z,
                    w.b(glas[k % 3]) if k % 2 else w.b("chain", axis="y", waterlogged=False))
    return w


UNTERWASSER = {
    "korallenpalast": ("Korallenpalast", korallenpalast),
    "glaskuppel": ("Glaskuppel-Station", glaskuppel),
    "versunkener_tempel": ("Versunkener Tempel", versunkener_tempel),
    "korallenriff": ("Korallenriff", korallenriff),
    "riesenmuschel": ("Riesenmuschel", riesenmuschel),
    "saeulenhalle": ("Säulenhalle", saeulenhalle),
    "riesenqualle": ("Riesenqualle", riesenqualle),
}


# ============================================================================ Vulkan

class Glut:
    def __init__(self, w, seed):
        self.w = w
        self.asche = _stil(seed) == 1
        self.fels = Verlauf(w, "Vulkan", ["blackstone", "basalt", "smooth_basalt", "tuff", "cobbled_deepslate"]) \
            if not self.asche else Verlauf(w, "Asche", ["tuff", "basalt", "smooth_basalt", "andesite", "calcite"])
        self.glut = [w.b("magma_block"), w.b("shroomlight"), w.b("orange_stained_glass")]

    def f(self, x, y, z, v):
        return self.fels(v + self.w.rng.random() * 0.9, x, y, z)


def vulkan(seed, g=2):
    """Vulkan mit Krater und Lavasee, Glutadern an den Flanken, Obsidianströmen und Rauchsäulen."""
    w = _welt(seed)
    k = Glut(w, seed)
    u = U[g]
    R = 16 * u + 6
    H = 13 * u + 5
    Rk = R * 0.28
    for x in range(-int(R) - 3, int(R) + 4):
        for z in range(-int(R) - 3, int(R) + 4):
            a = math.atan2(z, x)
            d = math.hypot(x, z) * (1 + 0.1 * math.sin(5 * a + 1))
            if d > R:
                continue
            h = H * (1 - (d / R)) ** 1.1 if d > Rk else H * (1 - Rk / R) ** 1.1 - (Rk - d) * 0.8
            h = int(h)
            ader = abs(math.sin(a * 7 + d * 0.15)) < 0.06 and d > Rk + 1
            for y in range(0, max(1, h) + 1):
                w.setze(x, y, z, k.glut[0] if ader and y == h else k.f(x, y, z, 0.2 + 3 * y / H))
            if d <= Rk - 1:
                for y in range(max(1, h) + 1, int(H * (1 - Rk / R) ** 1.1) - 1):
                    w.setze(x, y, z, w.b("lava", level=0) if y == int(H * (1 - Rk / R) ** 1.1) - 2 else w.b("magma_block"))
    for i in range(3 + g):
        a = i * 2.1 + 0.5
        for t in np.linspace(0.3, 1, int(R)):
            d = R * t
            x, z = round(math.cos(a + t * 0.3) * d), round(math.sin(a + t * 0.3) * d)
            y = int(H * (1 - t) ** 1.1)
            w.setze(x, y + 1, z, w.b("obsidian") if w.rng.random() < 0.7 else w.b("crying_obsidian"))
    for i in range(3):
        a = i * 2.1
        x, z = round(math.cos(a) * Rk * 0.5), round(math.sin(a) * Rk * 0.5)
        w.setze(x, int(H * (1 - Rk / R) ** 1.1) - 1, z, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                          waterlogged=False))
    return w


def glutstrom(seed, g=1):
    """Felsklippe, über die ein erstarrter Glutstrom aus Magma, Schroomlicht und orangem Glas fließt."""
    w = _welt(seed)
    k = Glut(w, seed)
    u = U[g]
    W, H = _r(8 * u + 4, 6), _r(10 * u + 4, 7)
    for x in range(-W - 3, W + 4):
        for z in range(-_r(6 * u + 2, 4), _r(6 * u + 6, 8)):
            w.setze(x, 0, z, k.f(x, 0, z, 0.5))
    for x in range(-W, W + 1):
        top = H * (1 - (abs(x) / W) ** 2)
        for z in range(-_r(6 * u + 2, 4), 1):
            for y in range(0, int(top) + 1):
                w.setze(x, y, z, k.f(x, y, z, 0.3 + 3 * y / H))
    bw = _r(1.5 * u + 0.5, 1)
    for x in range(-bw, bw + 1):
        for y in range(1, int(H * (1 - (abs(x) / W) ** 2)) + 1):
            w.setze(x, y, 1, k.glut[(x + y) % 3] if (x + y) % 4 else k.glut[0])
    for x, z in scheibe(bw + 3, 0, bw + 4):
        w.setze(x, 0, z, k.glut[0] if w.rng.random() < 0.6 else w.b("shroomlight"))
    return w


def feuertempel(seed, g=2):
    """Feuertempel aus Schwarzstein: Stufenpyramide, Feuerschalen, Goldband, Glutboden, Säulen."""
    w = _welt(seed)
    k = Glut(w, seed)
    u = U[g]
    stufen = [3, 4, 5, 6][g]
    s = _r(2 * u, 1)
    R = stufen * s + _r(3 * u, 2)
    _flaeche(w, R + 4, lambda x, z: k.f(x, 0, z, 0.3))
    for st in range(stufen):
        r = R - st * s
        for y in range(st * s, (st + 1) * s):
            for x in range(-r, r + 1):
                for z in range(-r, r + 1):
                    w.setze(x, y + 1, z, w.b("polished_blackstone_bricks") if max(abs(x), abs(z)) > r - 1
                            else w.b("blackstone"))
        for x in range(-r, r + 1):
            w.setze(x, (st + 1) * s, r, w.b("gold_block") if x % 4 == 0 else w.b("polished_blackstone_bricks"))
    top = stufen * s + 1
    rt = R - stufen * s
    for x in range(-rt, rt + 1):
        for z in range(-rt, rt + 1):
            w.setze(x, top, z, k.glut[0])
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in range(top, top + _r(4 * u, 3)):
                w.setze(sx * rt, y, sz * rt, w.b("polished_blackstone_bricks"))
            w.setze(sx * rt, top + _r(4 * u, 3), sz * rt, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                               waterlogged=False))
    for t in range(stufen * s + 1):
        for x in range(-1, 2):
            w.setze(x, t, R + 1 - t, treppe(w, "polished_blackstone_brick", "north"))
    return w


def riesenschmiede(seed, g=2):
    """Riesenschmiede: offene Halle mit Ambossen, Glutbecken, Blasebalg-Schloten, Waffenständer und einem
    überlebensgroßen Hammer."""
    w = _welt(seed)
    k = Glut(w, seed)
    u = U[g]
    bx, bz = _r(8 * u + 3, 5), _r(5 * u + 3, 4)
    H = _r(5 * u + 3, 4)
    for x in range(-bx - 2, bx + 3):
        for z in range(-bz - 2, bz + 3):
            w.setze(x, 0, z, w.b("polished_blackstone") if (x + z) % 2 else w.b("deepslate_tiles"))
    for x in range(-bx, bx + 1, 4):
        for z in (-bz, bz):
            for y in range(1, H + 1):
                w.setze(x, y, z, w.b("polished_blackstone_bricks"))
    for x in range(-bx - 1, bx + 2):
        for z in range(-bz - 1, bz + 2):
            w.setze(x, H + 1, z, w.b("deepslate_tile_slab", type="bottom", waterlogged=False))
    for i, x in enumerate(range(-bx + 2, bx - 1, 4)):
        w.setze(x, 1, 0, w.b("anvil", facing="north"))
        w.setze(x + 1, 0, -2, w.b("lava", level=0))
        for dx, dz in ((0, -1), (2, -2), (1, -3), (1, -1)):
            w.setze(x + dx, 1, -2 + dz + 1, w.b("polished_blackstone_wall", up=True, north="none", south="none",
                                               east="none", west="none", waterlogged=False), ueberschreiben=False)
    for s in (-1, 1):
        for y in range(1, H + _r(6 * u, 4)):
            for dx in (0, 1):
                w.setze(s * (bx - 1) + dx, y, -bz + 1, w.b("bricks"))
        w.setze(s * (bx - 1), H + _r(6 * u, 4), -bz + 1, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                          waterlogged=False))
    S = Skulptur(w, u)
    S.mat("g", w.b("dark_oak_log", axis="y"))
    S.mat("k", lambda x, y, z, *_: w.b("iron_block") if (x + y) % 3 else w.b("polished_blackstone"))
    S.plus(kap((0, 0, 0), (0, 6, 0), 0.45), "g")
    S.plus(lambda X, Y, Z: (np.abs(X) <= 2.2) & (Y >= 6) & (Y <= 8) & (np.abs(Z) <= 1.2), "k")
    S.rendern((-3, 0, -2), (3, 9, 2), versatz=(0.5, 1, bz + 3.5))
    return w


def basaltfeld(seed, g=1):
    """Feld aus sechseckigen Basaltsäulen unterschiedlicher Höhe, wie Orgelpfeifen, mit Glutspalten."""
    w = _welt(seed)
    k = Glut(w, seed)
    u = U[g]
    R = 9 * u + 4
    for x, z in scheibe(R):
        d = math.hypot(x, z) / R
        h = int((1 - d) * (8 * u + 3) * (0.6 + 0.4 * math.sin(x * 0.7 + z * 1.1)) + 1)
        if ((x * 3 + z * 5) % 7) == 0:
            h = 0
            w.setze(x, 0, z, k.glut[0])
            continue
        for y in range(0, h + 1):
            w.setze(x, y, z, w.b("polished_basalt", axis="y") if y < h else w.b("smooth_basalt"))
    return w


def obsidianturm(seed, g=2):
    """Zackige Obsidiannadel mit weinenden Rissen und einem glühenden Kern an der Spitze."""
    w = _welt(seed)
    u = U[g]
    H = 22 * u + 8
    _flaeche(w, 4 * u + 4, lambda x, z: w.b("blackstone"))
    S = Skulptur(w, 1.0)
    S.mat("o", lambda x, y, z, lx, ly, lz: w.b("crying_obsidian") if abs(math.sin(ly * 0.5 + math.atan2(lz, lx) * 3)) < 0.12
          else w.b("obsidian"))
    S.mat("k", w.b("shroomlight") if _stil(seed) == 0 else w.b("sea_lantern"))
    R = 3 * u + 1.5

    def nadel(X, Y, Z):
        t = np.clip(Y / H, 0, 1)
        a = np.arctan2(Z, X)
        r = R * (1 - t) ** 0.9 * (0.7 + 0.3 * np.abs(np.cos(3 * a + t * 4)))
        return (Y >= 0) & (Y <= H) & (X * X + Z * Z <= r * r)
    S.plus(nadel, "o")
    S.plus(ell(0, H * 0.82, 0, 0.9 * u + 0.3, 1.4 * u + 0.4, 0.9 * u + 0.3), "k")
    for i in range(3):
        a = i * 2.1 + 0.5
        S.plus(kap((math.cos(a) * R * 0.6, 0, math.sin(a) * R * 0.6),
                   (math.cos(a) * R * 1.6, H * 0.35, math.sin(a) * R * 1.6), R * 0.45, 0.2), "o")
    S.rendern((-R * 2, 0, -R * 2), (R * 2, H + 1, R * 2), versatz=(0.5, 1, 0.5))
    return w


def glutbaum(seed, g=1):
    """Verkohlter Baum mit glühenden Blättern aus Magma und Schroomlicht, Asche am Boden."""
    w = _welt(seed)
    u = U[g]
    _flaeche(w, 5 * u + 3, lambda x, z: w.b("blackstone") if w.rng.random() < 0.5 else w.b("basalt"))
    S = Skulptur(w, u)
    S.mat("h", w.b("stripped_crimson_stem", axis="y") if _stil(seed) == 0 else w.b("stripped_dark_oak_log", axis="y"))
    S.mat("l", lambda x, y, z, *_: [w.b("magma_block"), w.b("shroomlight"), w.b("nether_wart_block"),
                                     w.b("orange_stained_glass")][(x * 3 + y + z * 5) % 4])
    S.plus(kap((0, 0, 0), (0.5, 7, 0), 0.9, 0.6), "h")
    for i in range(4):
        a = i * math.pi / 2 + 0.4
        S.plus(kap((0.5, 5.5, 0), (math.cos(a) * 3.5, 8.5, math.sin(a) * 3.5), 0.5, 0.3), "h")
        S.plus(ell(math.cos(a) * 3.5, 9, math.sin(a) * 3.5, 2.2, 1.4, 2.2), "l")
    S.plus(ell(0.5, 10, 0, 2.5, 1.6, 2.5), "l")
    S.rendern((-7, 0, -7), (7, 12, 7), versatz=(0.5, 1, 0.5))
    return w


VULKAN = {
    "vulkan": ("Vulkan", vulkan),
    "glutstrom": ("Glutstrom-Klippe", glutstrom),
    "feuertempel": ("Feuertempel", feuertempel),
    "riesenschmiede": ("Riesenschmiede", riesenschmiede),
    "basaltfeld": ("Basaltfeld", basaltfeld),
    "obsidianturm": ("Obsidianturm", obsidianturm),
    "glutbaum": ("Glutbaum", glutbaum),
}


# ============================================================================ Nether

class Nether:
    def __init__(self, w, seed):
        self.w = w
        self.seele = _stil(seed) == 1
        self.ziegel = Verlauf(w, "Netherziegel", ["nether_bricks", "red_nether_bricks", "nether_bricks",
                                                  "chiseled_nether_bricks"]) if not self.seele else \
            Verlauf(w, "Seelenziegel", ["polished_blackstone_bricks", "nether_bricks", "polished_blackstone",
                                        "chiseled_polished_blackstone"])
        self.boden = (lambda x, z: w.b("netherrack") if w.rng.random() < 0.7 else w.b("crimson_nylium")) \
            if not self.seele else (lambda x, z: w.b("soul_soil") if w.rng.random() < 0.6 else w.b("soul_sand"))
        self.feuer = "campfire" if not self.seele else "soul_campfire"
        self.laterne = "lantern" if not self.seele else "soul_lantern"

    def z(self, x, y, z):
        return self.ziegel(0.3 + self.w.rng.random() * 2.2, x, y, z)


def netherfestung(seed, g=2):
    """Netherfestung: hohe Brückenbögen mit Zinnen, Turm mit Laternen, Warzenbeete und Feuerschalen."""
    w = _welt(seed)
    n = Nether(w, seed)
    u = U[g]
    L = _r(14 * u + 6, 9)
    H = _r(8 * u + 4, 6)
    b = _r(1.5 * u + 1, 2)
    _flaeche(w, L + 4, n.boden)
    for x in range(-L, L + 1):
        for z in range(-b, b + 1):
            w.setze(x, H, z, n.z(x, H, z))
            if abs(z) == b:
                w.setze(x, H + 1, z, n.z(x, H + 1, z))
                if x % 2 == 0:
                    w.setze(x, H + 2, z, w.b("nether_brick_fence", north=False, south=False, east=False, west=False,
                                             waterlogged=False))
        p = (x + L) % 8
        unten = 1 if p == 0 else H - 1 - int(round((H - 2) * 0.75 * math.sin(math.pi * p / 8)))
        for y in range(unten, H):
            for z in range(-b, b + 1):
                w.setze(x, y, z, n.z(x, y, z))
    h = _r(3 * u + 1, 2)
    for y in range(0, H + _r(8 * u, 4)):
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                if max(abs(x), abs(z)) == h:
                    w.setze(x, y, z, n.z(x, y, z))
    yt = H + _r(8 * u, 4)
    for x in range(-h - 1, h + 2):
        for z in range(-h - 1, h + 2):
            w.setze(x, yt, z, n.z(x, yt, z))
            if max(abs(x), abs(z)) == h + 1 and (x + z) % 2 == 0:
                w.setze(x, yt + 1, z, n.z(x, yt + 1, z))
    for x, z in ((h + 1, 0), (-h - 1, 0)):
        w.setze(x, yt - 1, z, w.b(n.laterne, hanging=True, waterlogged=False))
    for x in range(-L + 2, -L + 6):
        for z in range(b + 2, b + 5):
            w.setze(x, 0, z, w.b("soul_sand"))
            w.setze(x, 1, z, w.b("nether_wart", age=3))
    for x in (-L, L):
        w.setze(x, H + 1, 0, w.b(n.feuer, lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


def seelenschrein(seed, g=1):
    """Seelenschrein im Seelensandtal: Knochenbögen, Seelenfeuer, blaue Laternen und ein Altar."""
    w = _welt(seed)
    u = U[g]
    R = 6 * u + 3
    _flaeche(w, R + 3, lambda x, z: w.b("soul_soil") if w.rng.random() < 0.6 else w.b("soul_sand"))
    S = Skulptur(w, 1.0)
    S.mat("k", w.b("bone_block", axis="y"))
    for i in range(4):
        a = i * math.pi / 2
        S.plus(lambda X, Y, Z, a=a: (np.abs(np.sqrt((X * math.cos(a) + Z * math.sin(a)) ** 2 + Y * Y) - R * 0.8) <= 0.7 * u + 0.4)
               & (np.abs(-X * math.sin(a) + Z * math.cos(a)) <= 0.6 * u + 0.3) & (Y >= 0), "k")
    S.rendern((-R - 2, 0, -R - 2), (R + 2, R + 2, R + 2), versatz=(0.5, 1, 0.5))
    for x, z in scheibe(1.6 * u + 0.6):
        w.setze(x, 1, z, w.b("polished_blackstone_bricks"))
    w.setze(0, 2, 0, w.b("soul_campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    for x, z in kreisrand(R * 0.6):
        if (x + z) % 3 == 0:
            w.setze(x, 1, z, w.b("soul_lantern", hanging=False, waterlogged=False))
    return w


def pilzriesenhain(seed, g=2):
    """Hain riesiger Nether-Pilze mit Warzenhüten, Schroomlicht, Hängeranken und Nylium."""
    w = _welt(seed)
    u = U[g]
    gift = _stil(seed) == 1
    R = 10 * u + 4
    _flaeche(w, R + 2, lambda x, z: w.b("warped_nylium" if gift else "crimson_nylium") if w.rng.random() < 0.8
             else w.b("netherrack"))
    stamm = w.b("warped_stem" if gift else "crimson_stem", axis="y")
    hut = w.b("warped_wart_block" if gift else "nether_wart_block")
    for i in range(2 + g):
        a = i * 2.39996
        d = R * 0.6 * math.sqrt((i + 0.5) / (2 + g))
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        H = int((6 + 6 * w.rng.random()) * u) + 4
        r = (2.5 + w.rng.random() * 2) * u + 1
        for y in range(1, H):
            for x, z in scheibe(0.6 * u + 0.4, cx, cz):
                w.setze(x, y, z, stamm)
        for y in range(H - 2, H + int(r * 0.6) + 1):
            rr = r * (1 - max(0, (y - H) / (r * 0.6 + 1)) ** 2)
            for x, z in scheibe(rr, cx, cz):
                if math.hypot(x - cx, z - cz) > rr - 1.1 or y >= H + int(r * 0.6) - 1:
                    w.setze(x, y, z, w.b("shroomlight") if w.rng.random() < 0.06 else hut)
        for x, z in kreisrand(r, cx, cz):
            if w.rng.random() < 0.4:
                for kk in range(1, int(w.rng.integers(2, 5))):
                    w.setze(x, H - 2 - kk, z, w.b("twisting_vines_plant" if gift else "weeping_vines_plant"))
    return w


def bastion(seed, g=2):
    """Bastion aus Schwarzstein: wuchtige Mauern, Brücken, Goldblöcke und Ketten."""
    w = _welt(seed)
    u = U[g]
    h = _r(8 * u + 4, 6)
    H = _r(9 * u + 4, 6)
    _flaeche(w, h + 5, lambda x, z: w.b("blackstone") if w.rng.random() < 0.6 else w.b("basalt"))
    for y in range(1, H + 1):
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                ring = max(abs(x), abs(z))
                if ring in (h, h - 1) or (y == H // 2 and ring < h):
                    blk = ["polished_blackstone_bricks", "cracked_polished_blackstone_bricks", "blackstone",
                           "gilded_blackstone"][(x * 3 + y + z * 7) % 9 % 4]
                    w.setze(x, y, z, w.b(blk))
    for x in range(-h, h + 1):
        for z in range(-h, h + 1):
            if max(abs(x), abs(z)) == h and (x + z) % 3 == 0:
                w.setze(x, H + 1, z, w.b("polished_blackstone_bricks"))
    for k in range(3):
        w.setze(k - 1, H // 2 + 1, 0, w.b("gold_block"))
    for x in (-h + 2, h - 2):
        for y in range(H // 2 + 1, H):
            w.setze(x, y, 0, w.b("chain", axis="y", waterlogged=False))
    for y in range(1, 4):
        for x in range(-1, 2):
            w.bloecke.pop((x, y, h), None)
            w.bloecke.pop((x, y, h - 1), None)
    return w


def portalruine(seed, g=1):
    """Eingestürzte Portalruine: Rahmen aus Obsidian und weinendem Obsidian, Netherrack, Gold, Magma."""
    w = _welt(seed)
    u = U[g]
    b, H = _r(2 * u + 1, 2), _r(5 * u + 3, 5)
    _flaeche(w, b + 5, lambda x, z: w.b("netherrack") if w.rng.random() < 0.5 else w.b("magma_block")
             if w.rng.random() < 0.2 else w.b("grass_block", snowy=False))
    for x in range(-b - 1, b + 2):
        for y in range(1, H + 2):
            rand = x in (-b - 1, b + 1) or y in (1, H + 1)
            if rand and w.rng.random() < 0.82:
                w.setze(x, y, 0, w.b("crying_obsidian") if w.rng.random() < 0.3 else w.b("obsidian"))
            elif not rand and w.rng.random() < 0.15:
                w.setze(x, y, 0, w.b("purple_stained_glass"))
    for i in range(3 + g):
        x, z = round((w.rng.random() - 0.5) * 2 * b), round((w.rng.random() - 0.5) * 4) + 2
        w.setze(x, 1, z, w.b("gold_block") if i % 2 else w.b("obsidian"))
    return w


def glutsee(seed, g=2):
    """Basaltplattform über einem Lavasee mit Säulen, Feuerschalen und Kettenlaternen."""
    w = _welt(seed)
    n = Nether(w, seed)
    u = U[g]
    R = 9 * u + 4
    for x, z in scheibe(R + 3):
        w.setze(x, -1, z, w.b("netherrack"))
        w.setze(x, 0, z, w.b("lava", level=0) if math.hypot(x, z) < R + 1.5 else w.b("netherrack"))
    for x, z in kreisrand(R + 2.5):
        w.setze(x, 1, z, w.b("blackstone"))
    rp = R * 0.55
    for x, z in scheibe(rp):
        w.setze(x, 2, z, w.b("polished_basalt", axis="y") if math.hypot(x, z) > rp - 1 else w.b("smooth_basalt"))
    for i in range(6):
        a = i * math.pi / 3
        x, z = round(math.cos(a) * rp * 0.8), round(math.sin(a) * rp * 0.8)
        for y in range(0, 2):
            w.setze(x, y, z, w.b("basalt", axis="y"))
        for y in range(3, 3 + _r(3 * u, 2)):
            w.setze(x, y, z, n.z(x, y, z))
        w.setze(x, 3 + _r(3 * u, 2), z, w.b(n.feuer, lit=True, signal_fire=False, facing="north", waterlogged=False))
    for t in range(int(R * 0.45) + 3):
        w.setze(int(rp) + t, 2, 0, w.b("polished_blackstone_bricks"))
    return w


def seelenbruecke(seed, g=2):
    """Lange Brücke aus Netherziegeln an Ketten über dem Abgrund, mit Seelenlaternen."""
    w = _welt(seed)
    n = Nether(w, seed)
    u = U[g]
    L = _r(16 * u + 6, 10)
    H = _r(5 * u + 3, 4)
    for s in (-1, 1):
        for x in range(s * L - 3 * s, s * L + 4 * s, s):
            for z in range(-3, 4):
                for y in range(0, H + 1):
                    w.setze(x, y, z, w.b("netherrack") if y < H else n.z(x, y, z))
    for x in range(-L, L + 1):
        y = H - int(math.cos(x / L * math.pi / 2) * 2 * u)
        for z in (-1, 0, 1):
            w.setze(x, y, z, n.z(x, y, z))
        for z in (-2, 2):
            w.setze(x, y + 1, z, w.b("nether_brick_fence", north=False, south=False, east=True, west=True,
                                     waterlogged=False))
        if x % 5 == 0:
            for z in (-2, 2):
                w.setze(x, y + 2, z, w.b(n.laterne, hanging=False, waterlogged=False))
    for s in (-1, 1):
        for y in range(H, H + _r(6 * u, 4)):
            for z in (-3, 3):
                w.setze(s * L, y, z, n.z(s * L, y, z))
    return w


NETHER = {
    "netherfestung": ("Netherfestung", netherfestung),
    "seelenschrein": ("Seelenschrein", seelenschrein),
    "pilzriesenhain": ("Pilzriesenhain", pilzriesenhain),
    "bastion": ("Bastion", bastion),
    "portalruine": ("Portalruine", portalruine),
    "glutsee": ("Glutsee-Plattform", glutsee),
    "seelenbruecke": ("Seelenbrücke", seelenbruecke),
}


# ============================================================================ End

def _endstein(w, r, cx=0, cz=0, tief=None):
    tief = tief or r * 0.6
    for x, z in scheibe(r, cx, cz):
        d = math.hypot(x - cx, z - cz) / max(1, r)
        h = int(tief * (1 - d ** 1.5)) + 1
        for y in range(-h, 1):
            w.setze(x, y, z, w.b("end_stone") if y > -h + 1 or w.rng.random() < 0.7 else w.b("end_stone_bricks"),
                    ueberschreiben=False)


def endturm(seed, g=2):
    """Turm aus Purpur mit ausladenden Etagen-Dächern, End-Stäben und Fahnen aus Glas."""
    w = _welt(seed)
    u = U[g]
    _endstein(w, 5 * u + 4)
    stock = [3, 4, 6, 8][g]
    h = _r(2.5 * u + 1, 2)
    y = 1
    for s in range(stock):
        eh = _r(3 * u + 2, 3)
        for yy in range(y, y + eh):
            for x in range(-h, h + 1):
                for z in range(-h, h + 1):
                    if max(abs(x), abs(z)) == h:
                        fen = (yy - y) == eh // 2 and (x == 0 or z == 0)
                        w.setze(x, yy, z, w.b("magenta_stained_glass") if fen else
                                w.b("purpur_pillar", axis="y") if abs(x) == abs(z) else w.b("purpur_block"))
        y += eh
        for x in range(-h - 2, h + 3):
            for z in range(-h - 2, h + 3):
                if max(abs(x), abs(z)) >= h:
                    w.setze(x, y, z, w.b("purpur_slab", type="bottom", waterlogged=False)
                            if max(abs(x), abs(z)) == h + 2 else w.b("purpur_block"))
        for (x, z) in ((h + 2, h + 2), (-h - 2, h + 2), (h + 2, -h - 2), (-h - 2, -h - 2)):
            w.setze(x, y + 1, z, w.b("end_rod", facing="up"))
        y += 1
        h = max(1, h - (s % 2))
    for k in range(_r(3 * u, 2)):
        w.setze(0, y + k, 0, w.b("purpur_pillar", axis="y"))
    w.setze(0, y + _r(3 * u, 2), 0, w.b("dragon_head", rotation=0) if False else w.b("end_rod", facing="up"))
    for k in range(_r(2 * u, 2)):
        w.setze(1 + k, y + _r(3 * u, 2) - 1, 0, w.b("magenta_stained_glass"))
    return w


def obsidiansplitter(seed, g=2):
    """Schwebende Obsidiansplitter um einen leuchtenden Kern, darunter eine kleine End-Insel."""
    w = _welt(seed)
    u = U[g]
    _endstein(w, 4 * u + 3)
    cy = 8 * u + 6
    S = Skulptur(w, 1.0)
    S.mat("o", lambda x, y, z, *_: w.b("crying_obsidian") if (x + y + z) % 5 == 0 else w.b("obsidian"))
    S.mat("k", w.b("pearlescent_froglight"))
    S.plus(ell(0, 0, 0, 1.4 * u + 0.6, 1.4 * u + 0.6, 1.4 * u + 0.6), "k")
    for i in range(6 + 2 * g):
        a = i * 2.39996
        b = (i * 1.3) % math.pi - math.pi / 2
        d = (4 + 3 * ((i * 7) % 5) / 5) * u + 2
        c = (math.cos(a) * math.cos(b) * d, math.sin(b) * d, math.sin(a) * math.cos(b) * d)
        e = (c[0] * 1.6, c[1] * 1.6, c[2] * 1.6)
        S.plus(kap(c, e, 0.9 * u + 0.4, 0.15), "o")
    R = 12 * u + 6
    S.rendern((-R, -R, -R), (R, R, R), versatz=(0.5, cy, 0.5))
    return w


def chorusgarten(seed, g=1):
    """Garten aus verzweigten Chorus-Pflanzen mit Blüten auf End-Stein, eingefasst von Purpur-Platten."""
    w = _welt(seed)
    u = U[g]
    R = 7 * u + 3
    _endstein(w, R + 1)
    for x, z in kreisrand(R):
        w.setze(x, 1, z, w.b("purpur_slab", type="bottom", waterlogged=False))
    pflanzen = set()
    for i in range(3 + 3 * g):
        a = i * 2.39996
        d = R * 0.75 * math.sqrt((i + 0.5) / (3 + 3 * g))
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = 1
        hoehe = int((3 + w.rng.random() * 4) * u) + 2
        for k in range(hoehe):
            pflanzen.add((x, y + k, z))
            if k > 1 and w.rng.random() < 0.35:
                dx, dz = [(1, 0), (-1, 0), (0, 1), (0, -1)][int(w.rng.integers(4))]
                for kk in range(1, 3):
                    pflanzen.add((x + dx * kk, y + k, z + dz * kk))
                pflanzen.add((x + dx * 2, y + k + 1, z + dz * 2))
                w.setze(x + dx * 2, y + k + 2, z + dz * 2, w.b("chorus_flower", age=5))
        w.setze(x, y + hoehe, z, w.b("chorus_flower", age=5))
    for (x, y, z) in pflanzen:
        nb = lambda dx, dy, dz: (x + dx, y + dy, z + dz) in pflanzen or w.P.name(w.hole(x + dx, y + dy, z + dz) or 0) \
            == "minecraft:chorus_flower"
        w.setze(x, y, z, w.b("chorus_plant", north=nb(0, 0, -1), south=nb(0, 0, 1), east=nb(1, 0, 0), west=nb(-1, 0, 0),
                             up=nb(0, 1, 0), down=nb(0, -1, 0) or y == 1))
    return w


def leerenschiff(seed, g=2):
    """Schwebendes Schiff aus Purpur und End-Stein mit Glassegeln, End-Stäben und Bugfigur."""
    w = _welt(seed)
    u = U[g]
    from boote import rumpf2
    mat = dict(unten=Verlauf(w, "Purpur", ["purpur_block", "purpur_pillar", "end_stone_bricks"]),
               wand=Verlauf(w, "Purpur", ["purpur_block", "purpur_block", "end_stone_bricks"]),
               leiste="purpur_pillar", zaun="end_rod" if False else "birch_fence",
               deck=Verlauf(w, "Deck", ["end_stone_bricks", "purpur_block", "end_stone_bricks"]))
    y0 = _r(6 * u + 4, 6)
    L = 22 * u + 6
    r = rumpf2(w, L, 3 * u + 1.2, 2 * u + 1, 2 * u + 1, mat, form="spitz", enden=3 * u, y0=y0)
    half = r["half"]
    for i, x in enumerate((-int(half * 0.3), int(half * 0.25))):
        yd = y0 + int(round(float(r["deck_haupt"](x)))) + 1
        hm = _r(10 * u + 4, 6)
        for y in range(yd, yd + hm):
            w.setze(x, y, 0, w.b("purpur_pillar", axis="y"))
        hz = int(3 * u + 2)
        for y in range(yd + 2, yd + hm - 1):
            for z in range(-hz, hz + 1):
                w.setze(x + 1, y, z, w.b("magenta_stained_glass") if (y + z) % 2 else w.b("purple_stained_glass"))
        w.setze(x, yd + hm, 0, w.b("end_rod", facing="up"))
    w.setze(int(half) + 1, y0 + int(round(float(r["deck_oben"](half - 1)))) + 1, 0, w.b("end_rod", facing="east"))
    return w


def leerenbogen(seed, g=2):
    """Gewaltiger Bogen aus End-Stein über der Leere, mit Purpur-Bändern und End-Stäben."""
    w = _welt(seed)
    u = U[g]
    R = 10 * u + 5
    d = 2 * u + 1.2
    for s in (-1, 1):
        _endstein(w, 4 * u + 2, s * round(R), 0)
    S = Skulptur(w, 1.0)
    S.mat("e", lambda x, y, z, lx, ly, lz: w.b("purpur_block") if int(math.atan2(ly, lx) * 10) % 4 == 0 else
          w.b("end_stone_bricks") if (x + y) % 3 else w.b("end_stone"))
    S.plus(lambda X, Y, Z: (np.abs(np.sqrt(X * X + Y * Y) - R) <= d) & (Y >= 0) & (np.abs(Z) <= d * 0.8), "e")
    S.rendern((-R - d - 1, 0, -d - 1), (R + d + 1, R + d + 1, d + 1), versatz=(0.5, 1, 0.5))
    for i in range(7):
        a = math.pi * (i + 0.5) / 7
        w.setze(round(math.cos(a) * (R + d + 0.5)), round(math.sin(a) * (R + d + 0.5)) + 1, 0, w.b("end_rod", facing="up"))
    return w


def endinsel(seed, g=2):
    """Schwebende End-Insel mit Purpur-Pavillon, Chorus-Pflanzen und hängenden Steinspitzen."""
    w = _welt(seed)
    u = U[g]
    R = 8 * u + 4
    yi = _r(10 * u + 4, 8)
    S = Skulptur(w, 1.0)
    S.mat("e", lambda x, y, z, *_: w.b("end_stone") if (x * 3 + y + z) % 5 else w.b("end_stone_bricks"))

    def insel(X, Y, Z):
        d = np.sqrt(X * X + Z * Z) / R
        unten = -R * 0.9 * (1 - d) ** 1.5
        return (d <= 1) & (Y <= 0.5) & (Y >= unten)
    S.plus(insel, "e")
    S.rendern((-R - 1, -R, -R - 1), (R + 1, 1, R + 1), versatz=(0.5, yi, 0.5))
    h = _r(2.5 * u + 1, 2)
    for y in range(yi + 1, yi + _r(4 * u + 2, 3)):
        for x in (-h, h):
            for z in (-h, h):
                w.setze(x, y, z, w.b("purpur_pillar", axis="y"))
    yt = yi + _r(4 * u + 2, 3)
    for kk in range(h + 2):
        for x in range(-h - 1 + kk, h + 2 - kk):
            for z in range(-h - 1 + kk, h + 2 - kk):
                if max(abs(x), abs(z)) == h + 1 - kk:
                    w.setze(x, yt + kk, z, w.b("purpur_block"))
    w.setze(0, yt + h + 2, 0, w.b("end_rod", facing="up"))
    for x, z in scheibe(1.0):
        w.setze(x, 0, z, w.b("end_stone"))
    w.anker = (0, 0, 0)
    return w


def leerenportal(seed, g=1):
    """Ring aus End-Portalrahmen mit eingesetzten Augen auf einer Plattform aus End-Steinziegeln."""
    w = _welt(seed)
    u = U[g]
    R = 4 * u + 3
    for x, z in scheibe(R + 2):
        w.setze(x, 0, z, w.b("end_stone_bricks") if (x + z) % 2 else w.b("purpur_block"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            if max(abs(x), abs(z)) == 2 and not (abs(x) == 2 and abs(z) == 2):
                fac = "south" if z == -2 else "north" if z == 2 else "east" if x == -2 else "west"
                w.setze(x, 1, z, w.b("end_portal_frame", facing=fac, eye=True))
    for x, z in kreisrand(R + 1):
        if (x + z) % 2 == 0:
            for y in range(1, _r(3 * u, 2) + 1):
                w.setze(x, y, z, w.b("purpur_pillar", axis="y"))
            w.setze(x, _r(3 * u, 2) + 1, z, w.b("end_rod", facing="up"))
    return w


END = {
    "endturm": ("End-Turm", endturm),
    "obsidiansplitter": ("Obsidiansplitter", obsidiansplitter),
    "chorusgarten": ("Chorusgarten", chorusgarten),
    "leerenschiff": ("Leerenschiff", leerenschiff),
    "leerenbogen": ("Leerenbogen", leerenbogen),
    "endinsel": ("End-Insel", endinsel),
    "leerenportal": ("Leerenportal", leerenportal),
}

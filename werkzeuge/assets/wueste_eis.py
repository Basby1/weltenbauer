"""Wüstenreich und Eisreich (neu) – je 20 Bauten im Pracht-Stil."""

from __future__ import annotations

import math

import numpy as np

import pracht as P
from lib import Rauschen, Verlauf, einfuegen, laub, zerfall
from pracht import Mat, gelaende, treppe
from skulptur import Skulptur, ell, kap, kreisrand, ohne, scheibe, spiegel_x, zur_mitte
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


def _rand_richtung(x, z, x0, z0, x1, z1):
    return "south" if z == z0 else "north" if z == z1 else "east" if x == x0 else "west"


# ============================================================================ gemeinsame Bausteine


def kuppel(w, mat, cx, cz, y, R, form="rund", spitze="gold_block"):
    """Kuppel: rund, zwiebel oder spitz; mat(x, y, z, t) oder Block-ID."""
    H = int(R * (1.0 if form == "rund" else 1.9))
    for k in range(H + 1):
        t = k / max(1, H)
        if form == "rund":
            r = R * math.sqrt(max(0, 1 - t * t))
        elif form == "zwiebel":
            r = R * (1.15 * math.sin(math.pi * min(1, t * 1.25)) ** 0.7 if t < 0.8 else 0.25 * (1 - (t - 0.8) / 0.2))
        else:
            r = R * (1 - t) ** 0.8
        for x, z in kreisrand(max(0.35, r), cx, cz):
            w.setze(x, y + k, z, mat(x, y + k, z, t) if callable(mat) else mat)
    if spitze:
        w.setze(cx, y + H + 1, cz, w.b(spitze))
        w.setze(cx, y + H + 2, cz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return y + H + 2


def flachhaus(w, M, x0, z0, x1, z1, y0, H, holz="jungle", balken=True, zinnen=True, tuer="south", fenster=True,
              randmat="smooth_sandstone"):
    """Lehm-/Steinhaus mit Flachdach, Brüstung, vorstehenden Balkenköpfen, kleinen Fenstern."""
    for y in range(y0, y0 + H):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                rand = x in (x0, x1) or z in (z0, z1)
                if not rand:
                    if y == y0:
                        w.setze(x, y, z, w.b(f"{holz}_planks"))
                    continue
                q = (x - x0) if z in (z0, z1) else (z - z0)
                fen = fenster and (y - y0) == 2 and q % 3 == 1 and not (x in (x0, x1) and z in (z0, z1))
                w.setze(x, y, z, w.b(f"{holz}_trapdoor", facing=_rand_richtung(x, z, x0, z0, x1, z1), half="bottom",
                                     open=True, powered=False, waterlogged=False) if fen and False else
                        (w.b("glass_pane", north=x in (x0, x1), south=x in (x0, x1), east=z in (z0, z1),
                             west=z in (z0, z1), waterlogged=False) if fen else M(x, y, z, (y - y0) / (H + 2))))
    yt = y0 + H
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, yt, z, M(x, yt, z, 0.9))
            if zinnen and (x in (x0, x1) or z in (z0, z1)):
                w.setze(x, yt + 1, z, M(x, yt + 1, z, 1.0) if (x + z) % 2 == 0 else
                        w.b(f"{randmat}_slab", type="bottom", waterlogged=False))
    if balken:
        for x in range(x0 + 1, x1, 2):
            for z, d in ((z0, -1), (z1, 1)):
                w.setze(x, yt - 1, z + d, w.b(f"{holz}_log" if holz != "bamboo" else "stripped_jungle_log", axis="z"))
    mx, mz = (x0 + x1) // 2, (z0 + z1) // 2
    tx, tz = {"south": (mx, z1), "north": (mx, z0), "east": (x1, mz), "west": (x0, mz)}[tuer]
    for y, half in ((y0, "lower"), (y0 + 1, "upper")):
        w.setze(tx, y, tz, w.b(f"{holz}_door", facing=tuer, half=half, hinge="left", open=False, powered=False))
    return yt + 1


def zelt(w, cx, cz, r, h, farben, eingang="south"):
    for y in range(1, h + 1):
        rr = r * (1 - (y - 1) / h) ** 0.8
        for x, z in kreisrand(max(0.4, rr), cx, cz):
            a = math.atan2(z - cz, x - cx)
            f = farben[int((a + math.pi) / (2 * math.pi) * 8) % len(farben)]
            w.setze(x, y, z, w.b(f if f.endswith("_wool") else f + "_wool"))
    w.setze(cx, h + 1, cz, w.b("jungle_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    dz = int(r) if eingang == "south" else -int(r)
    for k in range(2):
        w.bloecke.pop((cx, 1 + k, cz + dz), None)


def palme(w, x, z, y=0, H=None):
    import wald
    einfuegen(w, wald.palme(int(w.rng.integers(1, 10 ** 6)), H=H), x, y, z)


def markise(w, x0, x1, z, y, farben, richtung=1):
    for x in range(x0, x1 + 1):
        w.setze(x, y, z, w.b(f"{farben[(x - x0) % len(farben)]}_wool"))
        w.setze(x, y - 1, z + richtung, w.b(f"{farben[(x - x0) % len(farben)]}_carpet")) if False else None


# ============================================================================ WÜSTE

def _wueste(w, seed):
    if _stil(seed) == 0:
        return dict(M=Mat(w, "sandstein"), lehm=Mat(w, ["smooth_sandstone", "sandstone", "cut_sandstone", "end_stone",
                                                          "smooth_sandstone", "birch_planks" if False else "sandstone"]),
                    rand="sandstone", holz="jungle", gold="gold_block", akz="lapis_block",
                    kuppel=Mat(w, ["light_blue_concrete", "cyan_concrete", "light_blue_concrete", "lapis_block",
                                   "prismarine_bricks"], kontrast=0.7), farben=["red", "white", "orange", "yellow"])
    return dict(M=Mat(w, "rotsandstein"), lehm=Mat(w, "lehm"), rand="red_sandstone", holz="acacia",
                gold="gold_block", akz="cyan_terracotta",
                kuppel=Mat(w, ["waxed_cut_copper", "waxed_exposed_cut_copper", "gold_block", "waxed_cut_copper"],
                           kontrast=0.7), farben=["purple", "yellow", "red", "white"])


def lehmhaeuser(seed, g=1):
    """Lehmhäuser: verschachtelte Flachdachhäuser auf verschiedenen Höhen, Dachterrassen mit Leitern,
    Sonnensegel, Krüge und eine Gassenbrücke."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    rng = w.rng
    gelaende(w, _r(12 * u + 8), art="sand", dichte=0.3)
    n = 4 + g * 3
    for i in range(n):
        a = i / n * 2 * math.pi + rng.random() * 0.4
        r = (5 + rng.random() * 8) * u
        x0, z0 = int(math.cos(a) * r) - 3, int(math.sin(a) * r) - 3
        bx, bz = int(3 + rng.random() * 3 * u), int(3 + rng.random() * 3 * u)
        hh = 4 + int(rng.random() * 2) * 3
        flachhaus(w, d["lehm"], x0, z0, x0 + bx, z0 + bz, 1, hh, holz=d["holz"],
                  tuer=["south", "east", "west", "north"][i % 4], randmat=d["rand"])
        if rng.random() < 0.6:
            for y in range(1, hh + 2):
                w.setze(x0 + bx + 1, y, z0 + 1, w.b("ladder", facing="east", waterlogged=False))
        if rng.random() < 0.5:
            for x in range(x0 + 1, x0 + bx):
                w.setze(x, hh + 3, z0 + 1, w.b(f"{d['farben'][x % 2]}_wool")) if False else \
                    w.setze(x, hh + 3, z0 + 1, w.b(f"{d['farben'][x % 2]}_carpet"))
            for sx in (x0 + 1, x0 + bx - 1):
                for y in range(hh + 2, hh + 3):
                    w.setze(sx, y, z0 + 1, w.b(f"{d['holz']}_fence", north=False, south=False, east=False, west=False,
                                               waterlogged=False))
        w.setze(x0 - 1, 1, z0 + 1, w.b("decorated_pot", facing="north", waterlogged=False) if False else w.b("flower_pot"))
    palme(w, 0, 0)
    hohl(w, 2)
    return w


def kuppelpalast(seed, g=2):
    """Kuppelpalast: Hauptbau mit großer Kuppel, vier schlanke Ecktürme mit Zwiebelhauben, Bogenarkaden,
    Wasserbecken mit Palmen und ein Prunkportal."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    a = _r(8 * u + 4, 6)
    H = _r(7 * u + 4, 6)
    y0 = platz(w, a + _r(10 * u, 6), d["M"], rand=d["rand"], muster=["smooth_sandstone", "cut_sandstone", d["akz"]],
               akzent="chiseled_sandstone", lichter="lantern", pfosten="sandstone_wall")
    yt = flachhaus(w, d["M"], -a, -a, a, a, y0, H, holz=d["holz"], balken=False, randmat=d["rand"])
    # Arkaden
    for x in range(-a, a + 1):
        for z in (-a, a):
            if (x + a) % 3 != 0 and 0 < (x + a) < 2 * a:
                for y in range(y0, y0 + 3):
                    w.bloecke.pop((x, y, z), None)
                w.setze(x, y0 + 3, z, treppe(w, d["rand"], "east" if (x + a) % 3 == 1 else "west", "top"))
    for x, z in kreisrand(a * 0.55):
        for y in range(yt, yt + 3):
            w.setze(x, y, z, d["M"](x, y, z, 0.9))
    kuppel(w, d["kuppel"], 0, 0, yt + 3, a * 0.6, form="zwiebel" if _stil(seed) else "rund")
    for sx in (-1, 1):
        for sz in (-1, 1):
            P.turm(w, P.Stil(w, wand="sandstein" if _stil(seed) == 0 else "rotsandstein", gesims=d["rand"],
                             dach=["dark_prismarine"]), sx * (a + 1), sz * (a + 1), y0, _r(H * 2.4),
                   1.4 * min(u, 1.8), dach="platt", krone=True, fenster=6, fahne=None)
            kuppel(w, d["kuppel"], sx * (a + 1), sz * (a + 1), y0 + _r(H * 2.4) + 2, 1.8 * min(u, 1.8), form="zwiebel")
    for x in range(-a // 2, a // 2 + 1):
        for z in range(a + 3, a + 3 + _r(8 * u, 5)):
            w.setze(x, y0 - 1, z, w.b("water", level=0) if abs(x) < a // 2 else w.b(d["akz"]))
    for sx in (-1, 1):
        palme(w, sx * (a // 2 + 2), a + 6, y0 - 1)
    hohl(w, 2)
    return w


def basar(seed, g=1):
    """Basar: Gasse mit Ständen unter bunten Sonnensegeln, Teppiche, Krüge, Gewürzsäcke, Laternen an Leinen."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    rng = w.rng
    n = 3 + g * 2
    L = n * 5
    gelaende(w, L // 2 + 6, art="sand", dichte=0.2)
    for z in range(-L // 2 - 2, L // 2 + 3):
        for x in range(-2, 3):
            w.setze(x, 0, z, w.b("smooth_sandstone") if (x + z) % 3 else w.b("sandstone"))
    waren = ["hay_block", "melon", "pumpkin", "barrel", "honey_block", "dried_kelp_block", "orange_wool", "red_wool",
             "yellow_wool", "brown_mushroom_block"]
    for sx in (-1, 1):
        for i in range(n):
            z0 = -L // 2 + i * 5
            x0 = 3 if sx > 0 else -7
            for x in range(x0, x0 + 5):
                for z in range(z0, z0 + 4):
                    if x in (x0, x0 + 4) and z in (z0, z0 + 3):
                        for y in range(1, 4):
                            w.setze(x, y, z, w.b(f"{d['holz']}_fence", north=False, south=False, east=False,
                                                 west=False, waterlogged=False))
                    w.setze(x, 4, z, w.b(f"{d['farben'][(i + (x - x0) // 2) % len(d['farben'])]}_wool"))
                    if z == z0 + 1 and x0 < x < x0 + 4:
                        w.setze(x, 1, z, w.b(waren[int(rng.integers(len(waren)))]) if waren[0] else None)
                    if z == z0 + 2 and x0 < x < x0 + 4:
                        w.setze(x, 0, z, w.b(f"{d['farben'][x % 4]}_wool"))
    for z in range(-L // 2, L // 2 + 1, 4):
        w.setze(0, 6, z, w.b("lantern", hanging=True, waterlogged=False))
        for x in range(-2, 3):
            w.setze(x, 7, z, w.b("chain", axis="x", waterlogged=False))
    hohl(w, 2)
    return w


def oase(seed, g=1):
    """Oase: Wasserloch mit Schilf und Seerosen, Palmenhain, Dünen, ein Brunnenhaus und Lagerzelte."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    rng = w.rng
    R = _r(14 * u + 6)
    gelaende(w, R + 6, art="sand", dichte=0.2)
    r_n = Rauschen(w, 4)
    for x, z in scheibe(R * 0.45):
        if math.hypot(x, z) / (R * 0.45) < 0.8 + 0.3 * r_n(x, 0, z):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("sand"))
            if rng.random() < 0.05:
                w.setze(x, 1, z, w.b("lily_pad"))
    for x, z in kreisrand(R * 0.5):
        w.setze(x, 0, z, w.b("grass_block", snowy=False))
        if rng.random() < 0.4:
            w.setze(x, 1, z, w.b("sugar_cane", age=0))
            w.setze(x, 2, z, w.b("sugar_cane", age=0))
    for i in range(5 + g * 3):
        a = rng.random() * 2 * math.pi
        dd = R * (0.55 + 0.3 * rng.random())
        palme(w, round(math.cos(a) * dd), round(math.sin(a) * dd))
    for x, z in scheibe(R + 5):
        dd = math.hypot(x, z)
        if dd > R * 0.8:
            hh = int((r_n(x, 5, z) - 0.3) * 6 * u)
            for y in range(1, hh + 1):
                w.setze(x, y, z, w.b("sand"), ueberschreiben=False)
    zelt(w, -R // 2, R // 2 + 2, 2.8, 4, [d["farben"][0], "white"])
    zelt(w, R // 2, R // 2 + 3, 2.4, 3, [d["farben"][1], "white"])
    hohl(w, 2)
    return w


def sandruine(seed, g=2):
    """Versunkene Sandstadt: halb im Sand begrabene Säulen, Mauerreste, ein Torbogen und eine zerbrochene
    Statue, Dünen wehen darüber."""
    w = kuppelpalast(seed, g)
    zerfall(w, set(b for b in w.bloecke.values() if b), Rauschen(w, 3), 40 * U[g], staerke=0.9, boden=2)
    r_n = Rauschen(w, 6)
    R = _r(20 * U[g] + 8)
    for x, z in scheibe(R):
        hh = int((r_n(x, 0, z) * 0.8 + 0.1) * 8 * U[g])
        for y in range(1, hh + 1):
            if w.frei(x, y, z):
                w.setze(x, y, z, w.b("sand"))
    return w


def karawanserei(seed, g=2):
    """Karawanserei: quadratischer Innenhof mit Bogengängen, Brunnen, Kamelställen (Heu), Wehrtürmen an
    den Ecken und einem hohen Tor."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    a = _r(10 * u + 5)
    gelaende(w, a + 6, art="sand", dichte=0.2)
    t = 4
    for (x0, z0, x1, z1, tu) in ((-a, -a, a, -a + t, "south"), (-a, a - t, a, a, "north"), (-a, -a + t + 1, -a + t,
                                                                                            a - t - 1, "east"),
                                 (a - t, -a + t + 1, a, a - t - 1, "west")):
        flachhaus(w, d["M"], x0, z0, x1, z1, 1, 5, holz=d["holz"], tuer=tu, randmat=d["rand"])
    for x in range(-2, 3):
        for y in range(1, 5):
            for z in range(a - t, a + 1):
                w.bloecke.pop((x, y, z), None)
    for x in range(-3, 4):
        for y in range(5, 9):
            w.setze(x, y, a, d["M"](x, y, a, 0.8))
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in range(1, 10):
                for dx in range(-1, 2):
                    for dz in range(-1, 2):
                        w.setze(sx * a + dx, y, sz * a + dz, d["M"](sx * a + dx, y, sz * a + dz, y / 10))
            kuppel(w, d["kuppel"], sx * a, sz * a, 10, 1.6, form="rund", spitze=None)
    w.setze(0, 0, 0, w.b("water", level=0))
    for x, z in kreisrand(1.5):
        w.setze(x, 1, z, w.b(f"{d['rand']}_slab", type="bottom", waterlogged=False))
    for i in range(8):
        w.setze(-a + t + 2 + i, 1, -a + t + 2, w.b("hay_block", axis="x"))
    hohl(w, 2)
    return w


def minarett(seed, g=1):
    """Schlanker Wachturm mit Balkonringen, Kacheldekor, Laternenkranz und Zwiebelspitze."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    R = 2.2 * u + 1.2
    H = _r(26 * u + 8)
    gelaende(w, _r(R + 6), art="sand", dichte=0.2)
    for y in range(1, H):
        r = R * (1 - 0.25 * y / H)
        for x, z in kreisrand(r):
            band = y % 8 in (0, 1)
            w.setze(x, y, z, w.b(d["akz"]) if band else d["M"](x, y, z, y / H))
        if y % 12 == 11:
            for x, z in kreisrand(r + 1.2):
                w.setze(x, y, z, treppe(w, d["rand"], zur_mitte(x, z), "top"))
                w.setze(x, y + 1, z, w.b(f"{d['rand']}_wall" if d["rand"] in ("sandstone", "red_sandstone") else
                                         "sandstone_wall", up=True, north="none", south="none", east="none",
                                         west="none", waterlogged=False))
    kuppel(w, d["kuppel"], 0, 0, H, R * 0.9, form="zwiebel")
    hohl(w, 2)
    return w


def lehmfestung(seed, g=2):
    """Kasbah: Lehmburg mit geböschten Mauern, Zinnenkranz, Ecktürmen mit Fensterreihen, Innenhof mit Palmen."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    a = _r(9 * u + 5)
    H = _r(8 * u + 4, 6)
    gelaende(w, a + 6, art="sand", dichte=0.2)
    for y in range(1, H + 1):
        sh = (H - y) // 4
        for x in range(-a - sh, a + sh + 1):
            for z in range(-a - sh, a + sh + 1):
                if max(abs(x), abs(z)) in (a + sh, a + sh - 1):
                    w.setze(x, y, z, d["lehm"](x, y, z, y / H))
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if max(abs(x), abs(z)) == a and (x + z) % 2 == 0:
                w.setze(x, H + 1, z, d["lehm"](x, H + 1, z, 1))
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * a, sz * a
            for y in range(1, H + 7):
                hb = 3 - y // (H // 2 + 2)
                for x in range(cx - hb, cx + hb + 1):
                    for z in range(cz - hb, cz + hb + 1):
                        if max(abs(x - cx), abs(z - cz)) == hb:
                            fen = y % 4 == 2 and (x == cx or z == cz)
                            w.setze(x, y, z, w.b("black_concrete") if fen else d["lehm"](x, y, z, y / (H + 7)))
            for x in range(cx - 2, cx + 3):
                for z in range(cz - 2, cz + 3):
                    if max(abs(x - cx), abs(z - cz)) == 2 and (x + z) % 2 == 0:
                        w.setze(x, H + 7, z, d["lehm"](x, H + 7, z, 1))
    for y in range(1, 5):
        for x in (-1, 0, 1):
            for z in (a - 1, a):
                w.bloecke.pop((x, y, z), None)
    for i in range(3):
        palme(w, -a // 2 + i * a // 2, -a // 3)
    hohl(w, 2)
    return w


def sphinxwaechter(seed, g=2):
    """Liegender Wächter mit Löwenleib und Menschenkopf mit Kopftuch, auf einem Sockel mit Treppe."""
    from weltwunder2 import _loewe
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    gelaende(w, _r(20 * u + 6), art="sand", dichte=0.2)
    S = Skulptur(w, 2.4 * u + 0.5)
    S.mat("k", sk(d["M"], 0, 18 * u))
    S.mat("m", bl(w, d["akz"]))
    S.mat("a", bl(w, d["gold"]))
    S.mat("s", sk(d["M"], 0, 4))
    _loewe(w, S, 0, 0, 0, 1, "s")
    S.plus(spiegel_x(kap((1.3, 7.2, 5.2), (1.7, 4.8, 4.6), 0.55, 0.9)), "m")    # Kopftuch-Lappen
    S.rendern((-5, -1, -10), (5, 10, 9), versatz=(0.5, 1.01, 0.5))
    hohl(w, 2)
    return w


def obeliskenhof(seed, g=1):
    """Vier Obelisken mit goldenen Spitzen um eine Sonnenscheibe auf einem Mosaikplatz."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    R = _r(10 * u + 5)
    y0 = platz(w, R, d["M"], rand=d["rand"], muster=["smooth_sandstone", d["akz"], "gold_block"],
               akzent="chiseled_sandstone", lichter="lantern", pfosten="sandstone_wall")
    for i in range(4):
        a = i / 4 * 2 * math.pi + math.pi / 4
        cx, cz = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        H = _r(16 * u + 6)
        for y in range(y0, y0 + H):
            r = 1 if y < y0 + H - 2 else 0
            for x in range(cx - r, cx + r + 1):
                for z in range(cz - r, cz + r + 1):
                    w.setze(x, y, z, w.b("chiseled_sandstone") if (y - y0) % 6 == 3 and r else d["M"](x, y, z, 0.5))
        w.setze(cx, y0 + H, cz, w.b("gold_block"))
    for y in range(y0, y0 + 3):
        w.setze(0, y, 0, d["M"](0, y, 0, 0.5))
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx * dx + dy * dy <= 5:
                w.setze(dx, y0 + 5 + dy, 0, w.b("gold_block") if dx * dx + dy * dy > 2 else w.b("raw_gold_block"))
    hohl(w, 2)
    return w


def nomadenlager(seed, g=1):
    """Nomadenlager: große Zelte in Stammesfarben, Lagerfeuer, Teppiche, Kamel-Heu, Wasserschläuche."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    rng = w.rng
    R = _r(10 * u + 6)
    gelaende(w, R + 4, art="sand", dichte=0.3)
    n = 3 + g * 2
    for i in range(n):
        a = i / n * 2 * math.pi
        zelt(w, round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6), 2.5 + rng.random() * u, 3 + g,
             [d["farben"][i % len(d["farben"])], "white", "brown"])
    w.setze(0, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for x, z in kreisrand(2.5):
        w.setze(x, 0, z, w.b(f"{d['farben'][(x + z) % 4]}_wool"))
    hohl(w, 2)
    return w


def windturm(seed, g=1):
    """Windturm (Badgir): Haus mit hohem Windfang-Turm, Lüftungsschlitzen und Kachelband."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    a = _r(4 * u + 2, 3)
    gelaende(w, a + 6, art="sand", dichte=0.2)
    yt = flachhaus(w, d["lehm"], -a, -a, a, a, 1, 5, holz=d["holz"], randmat=d["rand"])
    H = _r(10 * u + 5)
    for y in range(yt - 1, yt + H):
        for x in range(-1, 2):
            for z in range(-1, 2):
                if max(abs(x), abs(z)) == 1:
                    schlitz = y > yt + H - 4 and (x == 0 or z == 0)
                    w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                         waterlogged=False) if schlitz else
                            (w.b(d["akz"]) if (y - yt) % 5 == 0 else d["M"](x, y, z, 0.8)))
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, yt + H, z, w.b(f"{d['rand']}_slab", type="bottom", waterlogged=False))
    hohl(w, 2)
    return w


def felsengrab(seed, g=2):
    """Felsengrab: eine prunkvolle Tempelfassade direkt aus der roten Felswand gehauen – Säulen, Giebel,
    Rundbau oben und dunkler Eingang."""
    w = _welt(seed)
    u = U[g]
    st = _stil(seed)
    F = Mat(w, ["red_sandstone", "smooth_red_sandstone", "terracotta", "orange_terracotta", "granite"] if st == 0 else
            ["sandstone", "smooth_sandstone", "end_stone", "cut_sandstone"], kontrast=1.3)
    W, H, D = _r(16 * u + 6), _r(26 * u + 8), _r(10 * u + 4)
    r_n = Rauschen(w, 5)
    for x in range(-W, W + 1):
        for z in range(-D, 1):
            hh = H * (1 - (abs(x) / W) ** 3) * (0.85 + 0.3 * r_n(x, 0, z))
            for y in range(0, int(hh) + 1):
                w.setze(x, y, z, F(x, y, z, y / H))
    fb = _r(W * 0.5)
    for x in range(-fb, fb + 1):
        for y in range(1, int(H * 0.8)):
            w.setze(x, y, 1, F(x, y, 1, 0.6))
    from kathedralen import saeulenreihe, S as KS
    s = KS(w, "rot" if st == 0 else "sand")
    saeulenreihe(w, s, [(x, 2) for x in range(-fb + 1, fb, 3)], 1, int(H * 0.38),
                 mat="cut_red_sandstone" if st == 0 else "cut_sandstone",
                 kapitell="chiseled_red_sandstone" if st == 0 else "chiseled_sandstone")
    for x in range(-fb, fb + 1):
        for z in (2, 3):
            w.setze(x, int(H * 0.38), z, F(x, 0, z, 0.8))
    for y in range(int(H * 0.45), int(H * 0.75)):
        for x, z in kreisrand(fb * 0.3, 0, 3):
            if z >= 1:
                w.setze(x, y, z, F(x, y, z, 0.9))
    for y in range(1, int(H * 0.25)):
        for x in range(-2, 3):
            w.setze(x, y, 1, w.b("black_concrete"))
    hohl(w, 3)
    return w


def sandsteinbogen(seed, g=2):
    """Natürlicher Sandsteinbogen mit Schichtbänderung, Felsnadeln und Geröll."""
    w = _welt(seed)
    u = U[g]
    st = _stil(seed)
    farben = ["sandstone", "smooth_sandstone", "orange_terracotta", "terracotta", "red_sandstone", "white_terracotta"]
    if st:
        farben = ["red_sandstone", "orange_terracotta", "terracotta", "red_terracotta", "smooth_red_sandstone",
                  "brown_terracotta"]
    R = 14 * u + 5
    S = Skulptur(w, 1.0)
    r_n = Rauschen(w, 2)
    S.mat("f", lambda x, y, z, *a: w.b(farben[int(y / 2.5 + r_n(x, y, z) * 1.5) % len(farben)]))
    from skulptur import torus
    S.plus(lambda X, Y, Z: ((np.sqrt(X ** 2 + Y ** 2) - R) ** 2 / (3.5 * u) ** 2 + Z ** 2 / (4.5 * u) ** 2 <= 1)
           & (Y >= 0), "f")
    for sx in (-1, 1):
        S.plus(ell(sx * R, 0, 0, 5 * u, 4 * u, 6 * u), "f")
    S.rendern((-R - 8 * u, -1, -8 * u), (R + 8 * u, R + 5 * u, 8 * u))
    gelaende(w, _r(R + 10), art="sand", dichte=0.3)
    for i in range(int(4 * u) + 2):
        x, z = int((w.rng.random() - 0.5) * 2.4 * R), int((w.rng.random() - 0.5) * 2 * R)
        hh = int((4 + w.rng.random() * 10) * u)
        for y in range(1, hh):
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    if abs(dx) + abs(dz) < 2 or y < hh // 2:
                        w.setze(x + dx, y, z + dz, w.b(farben[(y // 2) % len(farben)]))
    hohl(w, 2)
    return w


def kuppelgrab(seed, g=1):
    """Kuppelgrab eines Wüstenfürsten: Würfelbau mit gerippter Kuppel, Kachelportalen und Garten-Wasserlauf."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    a = _r(5 * u + 3, 4)
    y0 = platz(w, a + _r(7 * u, 4), d["M"], rand=d["rand"], muster=["smooth_sandstone", d["akz"], "gold_block"],
               akzent="chiseled_sandstone", lichter="lantern", pfosten="sandstone_wall")
    yt = flachhaus(w, d["M"], -a, -a, a, a, y0, _r(6 * u + 3, 5), holz=d["holz"], balken=False, randmat=d["rand"])
    for sx in range(4):
        dx, dz = [(0, a), (0, -a), (a, 0), (-a, 0)][sx]
        for k in range(-1, 2):
            for y in range(y0, y0 + 4):
                p = (dx + k if dz else dx, y, dz if dz else dz + k)
                w.setze(*p, w.b(d["akz"]) if y == y0 + 3 or abs(k) == 1 else w.b("black_concrete"))
    kuppel(w, d["kuppel"], 0, 0, yt, a * 0.85, form="spitz" if _stil(seed) else "rund")
    hohl(w, 2)
    return w


def zisterne(seed, g=1):
    """Stufenbrunnen: tief in den Boden gesenkte Zisterne mit umlaufenden Treppen, Säulen und Wasser."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    a = _r(6 * u + 3, 4)
    T = _r(4 * u + 3, 4)
    gelaende(w, a + 6, art="sand", dichte=0.2)
    for k in range(T):
        h = a - k
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                if max(abs(x), abs(z)) == h:
                    w.setze(x, -k, z, treppe(w, d["rand"], "east" if x == -h else "west" if x == h else
                                             "south" if z == -h else "north") if (abs(x) + abs(z)) % 3 else
                            d["M"](x, -k, z, 0.4))
    for x in range(-a + T, a - T + 1):
        for z in range(-a + T, a - T + 1):
            w.setze(x, -T, z, w.b("water", level=0))
            w.setze(x, -T - 1, z, d["M"](x, -T - 1, z, 0.2))
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            if max(abs(x), abs(z)) == a + 1:
                w.setze(x, 1, z, w.b(f"{d['rand']}_wall" if d['rand'] in ("sandstone", "red_sandstone") else
                                     "sandstone_wall", up=True, north="none", south="none", east="none", west="none",
                                     waterlogged=False) if (x + z) % 2 else d["M"](x, 1, z, 0.5))
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * (a + 2), sz * (a + 2)
            for dx in (-1, 1):
                for dz in (-1, 1):
                    for y in range(1, 5):
                        w.setze(cx + dx, y, cz + dz, w.b("cut_sandstone"))
            for x in range(cx - 1, cx + 2):
                for z in range(cz - 1, cz + 2):
                    w.setze(x, 5, z, d["M"](x, 5, z, 0.9))
            kuppel(w, d["kuppel"], cx, cz, 6, 1.5, form="zwiebel")
    hohl(w, 2)
    return w


def wuestenwachturm(seed, g=1):
    """Rundwachturm aus Lehm mit Holzbalkon, Signalfeuer, Leiter und Wassertrog am Fuß."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    R = 2.5 * u + 2
    H = _r(14 * u + 6)
    gelaende(w, _r(R + 6), art="sand", dichte=0.2)
    for y in range(1, H):
        for x, z in kreisrand(R * (1 - 0.15 * y / H)):
            w.setze(x, y, z, d["lehm"](x, y, z, y / H))
    for x, z in kreisrand(R + 1):
        w.setze(x, H, z, w.b(f"{d['holz']}_planks"))
        w.setze(x, H + 1, z, w.b(f"{d['holz']}_fence", north=True, south=True, east=True, west=True, waterlogged=False))
    for x, z in scheibe(R):
        w.setze(x, H, z, w.b(f"{d['holz']}_planks"))
    w.setze(0, H + 1, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    hohl(w, 2)
    return w


def gestrandetes_schiff(seed, g=2):
    """Gestrandetes Wüstenschiff: das Wrack eines Segelschiffs, schräg in einer Düne, Mast gebrochen."""
    w = _welt(seed)
    u = U[g]
    st = _stil(seed)
    holz = "dark_oak" if st == 0 else "spruce"
    L = 18 * u + 6
    B = 4 * u + 2
    S = Skulptur(w, 1.0)
    S.mat("h", lambda x, y, z, *a: w.b(f"{holz}_planks") if (y + x // 3) % 3 else w.b(f"stripped_{holz}_log", axis="x"))
    S.plus(ohne(ell(0, 4 * u, 0, L, 5 * u, B), lambda X, Y, Z: Y > 4 * u + 0.5), "h")
    S.minus(ell(0, 4 * u + 1, 0, L - 1.2, 4.4 * u, B - 1.2))
    from skulptur import dreh_z, dreh_x
    S.rendern((-L - 1, -1, -B - 1), (L + 1, 5 * u + 1, B + 1), versatz=(0, 3, 0), dreh=dreh_z(0.12) @ dreh_x(0.15))
    for y in range(4, int(14 * u) + 4):
        w.setze(int(-L * 0.1), y, 0, w.b(f"{holz}_log", axis="y"))
    for k in range(int(10 * u)):
        w.setze(int(-L * 0.1) + k, 2 + k // 4, 3, w.b(f"{holz}_log", axis="x"))
    gelaende(w, _r(L + 8), art="sand", dichte=0.2)
    r_n = Rauschen(w, 5)
    for x, z in scheibe(L + 4):
        hh = int((r_n(x, 0, z) * 0.6 + 0.2 * (1 - abs(x) / (L + 4))) * 4 * u)
        for y in range(1, hh + 1):
            w.setze(x, y, z, w.b("sand"), ueberschreiben=False)
    hohl(w, 2)
    return w


def skorpionstatue(seed, g=2):
    """Riesiger Skorpion aus Stein und Gold, Scheren erhoben, Stachel über dem Rücken – Wächter der Dünen."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    S = Skulptur(w, 1.2 * u + 0.3)
    S.mat("k", sk(Mat(w, ["polished_blackstone", "blackstone", "gilded_blackstone"]) if _stil(seed) == 0 else
                  d["M"], 0, 10 * u))
    S.mat("a", bl(w, d["gold"]))
    S.mat("g", bl(w, "redstone_block"))
    S.plus(ell(0, 2, 0, 3.2, 1.8, 5), "k")
    for i in range(6):
        S.plus(ell(0, 2.2 + i * 0.6, -5.5 - i * 1.4, 1.6 - i * 0.12, 1.3, 1.1), "k")
    S.plus(kap((0, 6, -13), (0, 9, -11), 0.9, 0.6), "k")
    S.plus(kap((0, 9, -11), (0, 9.2, -8.5), 0.6, 0.15), "a")
    for sx in (-1, 1):
        for k in range(4):
            z = 2 - k * 1.6
            S.plus(kap((sx * 2.8, 2, z), (sx * 5.5, 2.5, z + 0.5), 0.5, 0.4), "k")
            S.plus(kap((sx * 5.5, 2.5, z + 0.5), (sx * 7, 0, z + 0.8), 0.4, 0.3), "k")
        S.plus(kap((sx * 2.5, 2.5, 4), (sx * 4.5, 4, 7), 0.8, 0.7), "k")
        S.plus(ell(sx * 4.8, 4.5, 8.5, 1.4, 1.0, 1.8), "a")
        S.plus(kap((sx * 4.4, 4.8, 9.8), (sx * 3.8, 5.5, 11.5), 0.5, 0.2), "a")
        S.plus(ell(sx * 0.8, 3.4, 4.6, 0.3, 0.3, 0.3), "g")
    S.rendern((-9, -1, -15), (9, 11, 13), versatz=(0.5, 1.01, 0.5))
    gelaende(w, _r(18 * u + 4), art="sand", dichte=0.2)
    hohl(w, 2)
    return w


def stufenpyramide(seed, g=2):
    """Kleine Stufenpyramide mit Treppe auf allen vier Seiten und Opferaltar auf der Spitze."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    n = 5 + g
    B0 = _r(9 * u + 4)
    gelaende(w, B0 + 6, art="sand", dichte=0.2)
    sh = 2
    for k in range(n):
        h = B0 - k * (B0 - 2) // n
        for y in range(1 + k * sh, 1 + (k + 1) * sh):
            for x in range(-h, h + 1):
                for z in range(-h, h + 1):
                    if max(abs(x), abs(z)) >= h - 1:
                        w.setze(x, y, z, w.b(d["akz"]) if y % sh == 0 and max(abs(x), abs(z)) == h and (x + z) % 4 == 0
                                else d["M"](x, y, z, k / n))
    ytop = 1 + n * sh
    for k in range(ytop - 1):
        for (dx, dz, f) in ((0, 1, "north"), (0, -1, "south"), (1, 0, "west"), (-1, 0, "east")):
            r = B0 - k * (B0 - (B0 - (n - 1) * (B0 - 2) // n)) // (ytop - 1) + 1
            for q in (-1, 0, 1):
                p = (dx * r + q * abs(dz), 1 + k, dz * r + q * abs(dx))
                w.setze(*p, treppe(w, d["rand"], f))
    w.setze(0, ytop, 0, w.b("gold_block"))
    w.setze(0, ytop + 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    hohl(w, 3)
    return w


def handelsposten(seed, g=1):
    """Handelsposten: Lagerhaus mit Säulenvordach, gestapelte Warenkisten, Waage, Brunnen, Palme."""
    w = _welt(seed)
    d = _wueste(w, seed)
    u = U[g]
    a, b = _r(5 * u + 3, 4), _r(3 * u + 2, 3)
    gelaende(w, a + 8, art="sand", dichte=0.2)
    flachhaus(w, d["M"], -a, -b, a, b, 1, 5, holz=d["holz"], randmat=d["rand"])
    for x in range(-a, a + 1):
        for z in range(b + 1, b + 4):
            w.setze(x, 5, z, w.b(f"{d['farben'][x % 2]}_wool"))
        if x % 3 == 0:
            for y in range(1, 5):
                w.setze(x, y, b + 3, w.b(f"{d['holz']}_fence", north=False, south=False, east=False, west=False,
                                         waterlogged=False))
    for i in range(6):
        w.setze(-a + i, 1, b + 2, w.b("barrel", facing="up", open=False) if i % 2 else w.b("hay_block", axis="y"))
    palme(w, a + 4, 0)
    hohl(w, 2)
    return w


WUESTE = {
    "oase": ("Oase", oase),
    "basar": ("Basar", basar),
    "kuppelpalast": ("Kuppelpalast", kuppelpalast),
    "lehmhaeuser": ("Lehmhäuser", lehmhaeuser),
    "sandruine": ("Versunkene Sandstadt", sandruine),
    "karawanserei": ("Karawanserei", karawanserei),
    "minarett": ("Schlanker Wachturm", minarett),
    "lehmfestung": ("Lehmburg (Kasbah)", lehmfestung),
    "sphinx": ("Löwenwächter", sphinxwaechter),
    "obeliskenhof": ("Obeliskenhof", obeliskenhof),
    "nomadenlager": ("Nomadenlager", nomadenlager),
    "windturm": ("Windturm-Haus", windturm),
    "felsengrab": ("Felsengrab", felsengrab),
    "sandsteinbogen": ("Sandsteinbogen", sandsteinbogen),
    "kuppelgrab": ("Kuppelgrab", kuppelgrab),
    "zisterne": ("Stufenbrunnen", zisterne),
    "wuestenwachturm": ("Lehm-Wachturm", wuestenwachturm),
    "wuestenschiff": ("Gestrandetes Schiff", gestrandetes_schiff),
    "skorpion": ("Skorpionstatue", skorpionstatue),
    "stufenpyramide": ("Stufenpyramide", stufenpyramide),
    "handelsposten": ("Handelsposten", handelsposten),
}


# ============================================================================ EIS


def _eis(w, seed):
    if _stil(seed) == 0:
        return dict(E=Mat(w, ["blue_ice", "packed_ice", "packed_ice", "ice", "snow_block"], kontrast=1.0),
                    S=Mat(w, ["snow_block", "snow_block", "powder_snow" if False else "white_concrete_powder",
                              "packed_ice"], kontrast=0.6),
                    stein=Mat(w, ["stone", "andesite", "cobblestone", "packed_ice", "snow_block"], kontrast=1.2),
                    glas="light_blue_stained_glass", licht="sea_lantern", holz="spruce", akz="diamond_block",
                    dach=P.Dach(w, ["prismarine_brick", "dark_prismarine", "prismarine_brick"]))
    return dict(E=Mat(w, ["packed_ice", "blue_ice", "calcite", "diorite", "snow_block"], kontrast=1.0),
                S=Mat(w, ["snow_block", "calcite", "white_concrete", "polished_diorite"], kontrast=0.6),
                stein=Mat(w, ["deepslate", "cobbled_deepslate", "tuff", "snow_block", "polished_deepslate"],
                          kontrast=1.2),
                glas="white_stained_glass", licht="soul_lantern", holz="dark_oak", akz="lapis_block",
                dach=P.Dach(w, ["deepslate_tile", "deepslate_tile", "polished_deepslate"]))


def eispalast(seed, g=2):
    """Eispalast: Hauptbau aus Packeis mit Glasfenstern, Kristalltürmen mit spitzen Hauben, Eiszinnen,
    schneebedeckter Platz mit Eisskulpturen."""
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    a = _r(8 * u + 4, 6)
    st = P.Stil(w, wand=["packed_ice", "blue_ice", "packed_ice", "snow_block"], sockel=["snow_block", "packed_ice"],
                gesims="quartz" if _stil(seed) else "prismarine_brick", dach=d["dach"], holz=d["holz"], laeden=False,
                fenster=d["glas"] if d["glas"].endswith("pane") else d["glas"] + "_pane" if False else "glass_pane",
                licht=d["licht"])
    gelaende(w, a + _r(10 * u, 5), art="schnee", dichte=0.3)
    top = P.gebaeude(w, st, -a, -a // 2, a, a // 2, y0=1, etagen=3, eh=_r(3 * u + 2, 4), dach="walm", steil=True,
                     tuer="south", kamine=0)
    for (x, z, f) in ((-a - 2, -a // 2 - 2, 1.0), (a + 2, -a // 2 - 2, 1.0), (-a - 2, a // 2 + 2, 0.8),
                      (a + 2, a // 2 + 2, 0.8), (0, -a // 2 - 3, 1.3)):
        P.turm(w, st, x, z, 1, _r((22 * f) * u + 6), max(1.3, 2.0 * u * f), dach="nadel", krone=True, fahne=None)
    hohl(w, 2)
    return w


def iglu_dorf(seed, g=1):
    """Iglu-Dorf: Schneekuppeln mit Eisfenstern und Tunneln, Lagerfeuer, Schlittenplatz, Eisfischloch."""
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    rng = w.rng
    R = _r(10 * u + 6)
    gelaende(w, R + 4, art="schnee", dichte=0.3)
    n = 3 + g * 2
    for i in range(n):
        a = i / n * 2 * math.pi + rng.random() * 0.3
        cx, cz = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        r = 2.5 + rng.random() * 1.5 * u
        for k in range(int(r) + 1):
            for x, z in kreisrand(max(0.4, r * math.cos(k / (r + 0.5) * math.pi / 2)), cx, cz):
                w.setze(x, 1 + k, z, d["S"](x, 1 + k, z, 0.5) if (x + k) % 4 else w.b("packed_ice"))
        dx, dz = round(-math.cos(a) * (r + 1)), round(-math.sin(a) * (r + 1))
        for y in (1, 2):
            w.setze(cx + dx, y, cz + dz, d["S"](cx, y, cz, 0.5))
            w.bloecke.pop((cx + round(-math.cos(a) * r), y, cz + round(-math.sin(a) * r)), None)
    w.setze(0, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    w.setze(3, 0, -2, w.b("water", level=0))
    hohl(w, 2)
    return w


def gletschertor(seed, g=2):
    """Gletschertor: ein gewaltiger Bogen aus blauem Gletschereis mit hängenden Eiszapfen und Spalten."""
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    R = 14 * u + 5
    S = Skulptur(w, 1.0)
    S.mat("e", lambda x, y, z, lx, ly, lz: d["E"](x, y, z, ly / (R + 5)))
    S.plus(lambda X, Y, Z: ((np.sqrt(X ** 2 + Y ** 2) - R) ** 2 / (4 * u) ** 2 + Z ** 2 / (6 * u) ** 2 <= 1) & (Y >= 0),
           "e")
    for sx in (-1, 1):
        S.plus(ell(sx * R, 0, 0, 6 * u, 5 * u, 8 * u), "e")
    S.rendern((-R - 9 * u, -1, -9 * u), (R + 9 * u, R + 6 * u, 9 * u))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 3 and w.frei(x, y - 1, z) and rng.random() < 0.08:
            for k in range(1, int(2 + rng.random() * 4)):
                w.setze(x, y - k, z, w.b("pointed_dripstone", vertical_direction="down",
                                         thickness="tip" if k > 2 else "frustum", waterlogged=False) if False else
                        w.b("ice"))
    gelaende(w, _r(R + 10), art="schnee", dichte=0.3)
    hohl(w, 3)
    return w


def eiskristall(seed, g=2):
    """Eiskristall-Gruppe: sechseckige Säulen aus Eis in Blautönen über einem verschneiten Felsen."""
    from weltwunder2 import frostkristall
    return frostkristall(seed - 8 if _stil(seed) else seed, max(0, g - 1))


def gefrorener_wasserfall(seed, g=2):
    """Gefrorener Wasserfall: Felsklippe mit erstarrtem Eisfall, Eisbecken und Eiszapfen."""
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    W, H, D = _r(14 * u + 5), _r(20 * u + 6), _r(10 * u + 4)
    r_n = Rauschen(w, 5)
    for x in range(-W, W + 1):
        for z in range(-D, 1):
            hh = H * (0.8 + 0.3 * r_n(x, 0, z))
            for y in range(0, int(hh) + 1):
                w.setze(x, y, z, d["stein"](x, y, z, y / H))
            w.setze(x, int(hh) + 1, z, w.b("snow_block"))
    for x in range(-3 - g, 4 + g):
        for y in range(0, H):
            for z in range(1, 3 + int(2 * (1 - y / H))):
                if abs(x) < 3 + g - abs(math.sin(y * 0.3)) * 2:
                    w.setze(x, y, z, d["E"](x, y, z, 0.3 + 0.7 * (abs(x) / (3 + g))))
    for x, z in scheibe(6 + g * 2, 0, 6):
        w.setze(x, 0, z, w.b("ice") if math.hypot(x, z - 6) < 4 + g * 1.5 else w.b("packed_ice"))
    gelaende(w, _r(W + 4), art="schnee", dichte=0.3)
    hohl(w, 3)
    return w


def nordhuette(seed, g=1):
    """Nordhütte: Blockhaus mit Schneedach, Steinkamin, Holzstapel, Schlitten und Laterne."""
    import haeuser as H_
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    st = P.Stil(w, wand=[f"stripped_{d['holz']}_log", f"{d['holz']}_log"], sockel="graustein", gesims="cobblestone",
                dach=["snow_block_s"] if False else "schindel", holz=d["holz"])
    gelaende(w, a + 8, art="schnee", dichte=0.3)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1 + (g >= 2), eh=4, dach="sattel", ue=2, tuer="south", kamine=1)
    for (x, y, z), blk in list(w.bloecke.items()):
        if w.P.name(blk).endswith("_stairs") and y > 4 and w.frei(x, y + 1, z):
            w.setze(x, y + 1, z, w.b("snow", layers=2))
    H_.holzstapel(w, a + 2, -b, 4, d["holz"], "z")
    hohl(w, 2)
    return w


def riesenschneemann(seed, g=1):
    """Riesenschneemann mit Kürbisgesicht, Karottennase aus Orange, Holzarmen, Schal und Hut."""
    w = _welt(seed)
    u = U[g]
    s = 1.0 * u + 0.4
    S = Skulptur(w, s)
    S.mat("s", lambda x, y, z, *a: w.b("snow_block") if (x * 7 + y * 3 + z) % 9 else w.b("white_concrete_powder"))
    S.mat("k", bl(w, "black_concrete"))
    S.mat("o", bl(w, "orange_concrete"))
    S.mat("r", bl(w, "red_wool" if _stil(seed) == 0 else "blue_wool"))
    S.mat("h", bl(w, f"dark_oak_log"))
    S.plus(ell(0, 4, 0, 5, 4.5, 5), "s")
    S.plus(ell(0, 10.5, 0, 3.8, 3.4, 3.8), "s")
    S.plus(ell(0, 15.5, 0, 2.8, 2.6, 2.8), "s")
    S.plus(kap((0, 15.5, 2.4), (0, 15.3, 5.0), 0.6, 0.15), "o")
    for sx in (-1, 1):
        S.plus(ell(sx * 1.1, 16.4, 2.4, 0.4, 0.4, 0.3), "k")
        S.plus(kap((sx * 3.4, 11.5, 0), (sx * 7.5, 14.5, 0), 0.35), "h")
    for k in range(3):
        S.plus(ell(0, 9 + k * 1.6, 3.6 - k * 0.2, 0.45, 0.45, 0.3), "k")
    S.plus(lambda X, Y, Z: (np.abs(np.hypot(X, Z) - 2.6) < 0.7) & (np.abs(Y - 13.3) < 0.6), "r")
    S.plus(kap((2.2, 13.2, 1.6), (2.8, 9.8, 2.2), 0.5), "r")
    S.plus(lambda X, Y, Z: (np.hypot(X, Z) < 3.4) & (np.abs(Y - 17.8) < 0.3), "k")
    S.plus(lambda X, Y, Z: (np.hypot(X, Z) < 2.0) & (Y > 17.8) & (Y < 20.5), "k")
    S.rendern((-8, -1, -6), (8, 21, 6), versatz=(0.5, 0.01, 0.5))
    gelaende(w, _r(10 * u + 4), art="schnee", dichte=0.3)
    hohl(w, 2)
    return w


def eiswachturm(seed, g=1):
    """Eiswachturm: Rundturm aus Eis und Stein mit Leuchtfeuer aus Seelaternen und Zinnen aus Packeis."""
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    st = P.Stil(w, wand=["packed_ice", "stone_bricks", "packed_ice", "snow_block", "blue_ice"],
                sockel=["cobblestone", "stone"], gesims="stone_brick", dach=d["dach"], holz=d["holz"], laeden=False)
    R = 2.6 * u + 1.6
    H = _r(18 * u + 6)
    gelaende(w, _r(R + 7), art="schnee", dichte=0.3)
    top = P.turm(w, st, 0, 0, 1, H, R, dach="platt", fenster=6)
    for x, z in kreisrand(1):
        w.setze(x, H + 1, z, w.b(d["licht"]) if d["licht"] == "sea_lantern" else w.b("sea_lantern"))
    hohl(w, 2)
    return w


def eisschloss(seed, g=2):
    """Eisschloss: Ringmauer aus Eisblöcken, Türme mit Kristallhauben, Torbau und Thronhalle."""
    from burgen import mauer, Burgstil, POOL
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    POOL["eis_tmp"] = dict(wand="eis", sockel="graustein", gesims="stone_brick", dach="blau", holz=d["holz"],
                           banner=["light_blue_wool", "white_wool"], mauer="stone_brick")
    B = Burgstil(w, "eis_tmp")
    R = _r(14 * u + 5)
    H = _r(6 * u + 3, 5)
    gelaende(w, R + 6, art="schnee", dichte=0.3)
    n = 6
    pts = [(round(math.cos(i / n * 2 * math.pi) * R), round(math.sin(i / n * 2 * math.pi) * R)) for i in range(n)]
    for i in range(n):
        mauer(w, B, pts[i], pts[(i + 1) % n], H, dick=3, y0=1, mitte=(0, 0))
    for (x, z) in pts:
        P.turm(w, B.st, x, z, 1, H + _r(6 * u, 3), max(1.6, 2.2 * u), dach="nadel", fahne=B.banner)
    P.gebaeude(w, B.st, -_r(R * 0.4), -_r(R * 0.3), _r(R * 0.4), _r(R * 0.3), y0=1, etagen=2, eh=_r(3 * u + 2, 4),
               dach="walm", steil=True, tuer="south")
    hohl(w, 2)
    return w


def mammutskelett(seed, g=2):
    """Mammutskelett im Eis: gewaltige Stoßzähne, Rippenbögen und Schädel, halb im Schnee."""
    w = _welt(seed)
    u = U[g]
    s = 1.0 * u + 0.3
    S = Skulptur(w, s)
    S.mat("k", lambda x, y, z, *a: w.b("bone_block", axis="y") if (x + z) % 5 else w.b("calcite"))
    for i in range(10):
        x = -6 + i * 1.4
        S.plus(ell(x, 9 + math.sin(i / 9 * math.pi) * 1.5, 0, 0.8, 0.9, 0.8), "k")
        if 2 <= i <= 8:
            for sz in (-1, 1):
                for k in range(6):
                    a0, a1 = k / 6 * math.pi * 0.8, (k + 1) / 6 * math.pi * 0.8
                    S.plus(kap((x, 9 - math.sin(a0) * 6, sz * math.sin(a0) * 4 + sz * 0.3),
                               (x, 9 - math.sin(a1) * 6, sz * math.sin(a1) * 4 + sz * 0.3), 0.4), "k")
    S.plus(ell(9, 9, 0, 3, 3.2, 2.6), "k")
    for sz in (-1, 1):
        pts = [(10.5, 6.5, sz * 1.5), (13, 3, sz * 2.5), (16, 2.5, sz * 3), (17.5, 4.5, sz * 2.2), (17.5, 7, sz * 0.8)]
        for a, b in zip(pts, pts[1:]):
            S.plus(kap(a, b, 0.8, 0.6), "k")
        for (lx, lz) in ((-4, 2.5), (6, 2.5)):
            S.plus(kap((lx, 8, sz * lz * 0.6), (lx, 0, sz * lz), 0.8, 0.7), "k")
    S.rendern((-10, -1, -6), (20, 13, 6), versatz=(0.5, 0.01, 0.5))
    gelaende(w, _r(22 * u + 4), art="schnee", dichte=0.3)
    r_n = Rauschen(w, 4)
    for x, z in scheibe(18 * u):
        hh = int((r_n(x, 0, z) - 0.5) * 6 * u)
        for y in range(1, hh + 1):
            w.setze(x, y, z, w.b("snow_block"), ueberschreiben=False)
    hohl(w, 2)
    return w


def eisbruecke(seed, g=2):
    """Eisbrücke: geschwungene Bogenbrücke aus Packeis über eine Gletscherspalte mit Laternengeländer."""
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    L = _r(16 * u + 6)
    gelaende(w, L + 4, art="schnee", dichte=0.3)
    for z in range(-L, L + 1):
        for x in range(-3, 4):
            w.bloecke.pop((x, 0, z), None)
            if abs(z) < L - 3:
                for y in range(-6, 1):
                    w.setze(x + 6, y, z, d["stein"](x, y, z, 0.3)) if False else None
    for x in range(-L, L + 1):
        hb = int(5 * u * math.cos(x / L * math.pi / 2))
        for z in range(-2, 3):
            for y in range(hb - 1, hb + 1):
                w.setze(x, y + 1, z, d["E"](x, y, z, 0.5))
            if abs(z) == 2:
                w.setze(x, hb + 2, z, w.b("ice") if x % 4 else w.b(d["licht"]) if d["licht"] == "sea_lantern" else
                        w.b("sea_lantern"))
    hohl(w, 2)
    return w


def frostthron(seed, g=2):
    """Frostthron: ein Thron aus Eiskristallen auf einem Podest mit Stufen, umgeben von Eisspeeren."""
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    gelaende(w, _r(14 * u + 5), art="schnee", dichte=0.3)
    for k in range(4):
        r = _r(6 * u + 3) - k
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                w.setze(x, 1 + k, z, d["E"](x, 1 + k, z, k / 4) if max(abs(x), abs(z)) < r else
                        treppe(w, "quartz", "east" if x == -r else "west" if x == r else "south" if z == -r else
                               "north") if not (abs(x) == r and abs(z) == r) else w.b("packed_ice"))
    y = 5
    for x in range(-2, 3):
        for z in range(-2, 1):
            for yy in range(y, y + 2):
                w.setze(x, yy, z, w.b("blue_ice"))
    for x in range(-2, 3):
        for yy in range(y + 2, y + _r(10 * u + 4)):
            if abs(x) < 3 - (yy - y) // 5:
                w.setze(x, yy, -2, w.b("packed_ice") if abs(x) < 2 else w.b("blue_ice"))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x, z = round(math.cos(a) * 8 * u + 0.5), round(math.sin(a) * 8 * u)
        for yy in range(1, _r((6 + (i % 3) * 3) * u)):
            w.setze(x, yy, z, w.b("packed_ice") if yy % 3 else w.b("blue_ice"))
    hohl(w, 2)
    return w


def eislabyrinth(seed, g=1):
    """Eislabyrinth: Gänge zwischen mannshohen Eismauern, in der Mitte ein Kristallschrein."""
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    n = 5 + g * 2
    zelle = 3
    gelaende(w, n * zelle // 2 * 1.5 + 4, art="schnee", dichte=0.2)
    rng = w.rng
    besucht = set()
    wand = set((x, z) for x in range(2 * n + 1) for z in range(2 * n + 1))
    stack = [(0, 0)]
    besucht.add((0, 0))
    wand.discard((1, 1))
    while stack:
        cx, cz = stack[-1]
        nb = [(cx + dx, cz + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= cx + dx < n and 0 <= cz + dz < n and (cx + dx, cz + dz) not in besucht]
        if not nb:
            stack.pop()
            continue
        nx, nz = nb[int(rng.integers(len(nb)))]
        wand.discard((2 * nx + 1, 2 * nz + 1))
        wand.discard((cx + nx + 1, cz + nz + 1))
        besucht.add((nx, nz))
        stack.append((nx, nz))
    wand.discard((n, 0))
    off = -(2 * n + 1) * 2 // 2
    for (gx, gz) in wand:
        for dx in range(2):
            for dz in range(2):
                x, z = off + gx * 2 + dx, off + gz * 2 + dz
                for y in range(1, 4):
                    w.setze(x, y, z, d["E"](x, y, z, y / 4))
    w.setze(0, 1, 0, w.b(d["akz"]))
    w.setze(0, 2, 0, w.b("sea_lantern"))
    hohl(w, 2)
    return w


def eisfischerdorf(seed, g=1):
    """Eisfischer-Lager auf einem gefrorenen See: kleine Hütten, Eislöcher, Fischfässer, Schlitten."""
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    rng = w.rng
    R = _r(12 * u + 5)
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("ice") if (x * 3 + z) % 7 else w.b("packed_ice"))
        w.setze(x, -1, z, w.b("water", level=0))
    for x, z in kreisrand(R + 1):
        w.setze(x, 0, z, w.b("snow_block"))
    n = 2 + g
    for i in range(n):
        a = i / n * 2 * math.pi
        cx, cz = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        st = P.Stil(w, wand="holz_dunkel", sockel=["spruce_planks"], gesims="spruce", dach="schindel", holz="spruce",
                    laeden=False)
        P.gebaeude(w, st, cx - 2, cz - 2, cx + 2, cz + 2, y0=1, etagen=1, eh=3, dach="sattel", tuer="south",
                   gauben=False, kamine=0, sockel_h=0)
        w.setze(cx + 3, 0, cz, w.b("water", level=0))
        w.setze(cx + 3, 1, cz + 1, w.b("barrel", facing="up", open=False))
    hohl(w, 2)
    return w


def frostdrache(seed, g=2):
    """Eisdrachen-Statue: ein Drache aus Eis mit ausgebreiteten Schwingen auf einem verschneiten Felsen."""
    from reiche import DRACHEN
    w = DRACHEN[list(DRACHEN)[0]][1](seed, g) if False else None
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    S = Skulptur(w, 1.3 * u + 0.4)
    S.mat("k", lambda x, y, z, lx, ly, lz: d["E"](x, y, z, ly / 14))
    S.mat("a", bl(w, "sea_lantern"))
    S.plus(ell(0, 6, 0, 2.6, 2.4, 5), "k")
    S.plus(kap((0, 7, 4), (0, 11.5, 7.5), 1.6, 1.1), "k")
    S.plus(ell(0, 12, 9, 1.5, 1.3, 2.6), "k")
    S.plus(kap((0, 11.6, 10.5), (0, 11.0, 12.5), 0.9, 0.5), "k")
    for sx in (-1, 1):
        S.plus(ell(sx * 0.8, 12.6, 9.8, 0.3, 0.3, 0.3), "a")
        S.plus(kap((sx * 0.8, 13, 8.2), (sx * 1.6, 15, 6.5), 0.35, 0.1), "k")
        S.plus(kap((sx * 1.6, 3, 2.5), (sx * 1.8, 0, 3.5), 0.8, 0.7), "k")
        S.plus(kap((sx * 1.6, 3, -3), (sx * 2, 0, -2.5), 0.9, 0.7), "k")
        S.plus(kap((sx * 2, 8, 1), (sx * 9, 13, -1), 0.6, 0.35), "k")
        for k in range(4):
            tip = (sx * (7 + k * 1.3), 12 - k * 3.2, -1 - k * 1.2)
            S.plus(kap((sx * 9, 13, -1), tip, 0.35, 0.15), "k")
        S.plus(lambda X, Y, Z, sx=sx: (sx * X > 2.2) & (sx * X < 10) & (Y > 4 + (sx * X) * 0.2) &
               (Y < 13 - (sx * X - 2) * 0.1) & (np.abs(Z + 1 + (sx * X - 2) * 0.12) < 0.35) &
               (Y > 13 - (sx * X - 2) * 1.2), "k")
    pts = [(0, 5, -4), (0, 4, -8), (1.5, 2.5, -11), (3, 1.5, -13)]
    for a, b in zip(pts, pts[1:]):
        S.plus(kap(a, b, 1.3, 0.8), "k")
    S.rendern((-12, -1, -15), (12, 16, 14), versatz=(0.5, 3.01, 0.5))
    for x, z in scheibe(6 * u + 3):
        for y in range(0, 4):
            if math.hypot(x, z) + y * 1.4 < 6 * u + 3:
                w.setze(x, y, z, d["stein"](x, y, z, y / 4))
    gelaende(w, _r(16 * u + 4), art="schnee", dichte=0.2)
    hohl(w, 2)
    return w


def polarstation(seed, g=1):
    """Polarstation: Kuppelzelte aus Wolle, Funkmast, Vorratsfässer, Hundeschlitten und Flaggen."""
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    gelaende(w, _r(10 * u + 6), art="schnee", dichte=0.2)
    for i, (x, z) in enumerate(((0, 0), (7, 2), (-6, 3))):
        r = 3 + (i == 0) * u
        for k in range(int(r) + 1):
            for xx, zz in kreisrand(max(0.4, r * math.cos(k / (r + 0.5) * math.pi / 2)), x, z):
                w.setze(xx, 1 + k, zz, w.b("orange_wool" if (xx + k) % 3 else "white_wool"))
    for y in range(1, _r(14 * u + 4)):
        w.setze(-2, y, -6, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(-2, _r(14 * u + 4), -6, w.b("redstone_lamp", lit=True))
    for k in range(5):
        w.setze(3 + k, 1, -5, w.b("barrel", facing="up", open=False))
    hohl(w, 2)
    return w


def gefrorenes_schiff(seed, g=2):
    """Im Packeis eingefrorenes Segelschiff: Rumpf schräg im Eis, vereiste Masten, Schnee an Deck."""
    w = gestrandetes_schiff(seed, g)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if n == "minecraft:sand":
            w.bloecke[(x, y, z)] = w.b("packed_ice") if rng.random() < 0.6 else w.b("snow_block")
        elif w.frei(x, y + 1, z) and rng.random() < 0.5 and y > 1:
            w.setze(x, y + 1, z, w.b("snow", layers=1))
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) == "minecraft:white_concrete_powder":
            pass
    return w


def eisgrotte(seed, g=2):
    """Eisgrotten-Eingang: ein Hügel aus Schnee und Fels mit einem blau leuchtenden Höhlenmaul, Eiszapfen
    und Kristallen im Inneren."""
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    R = 14 * u + 5
    S = Skulptur(w, 1.0)
    S.mat("f", lambda x, y, z, lx, ly, lz: d["stein"](x, y, z, ly / R) if ly < R * 0.55 else w.b("snow_block"))
    S.mat("e", lambda x, y, z, lx, ly, lz: d["E"](x, y, z, 0.4))
    S.plus(ell(0, 0, 0, R, R * 0.7, R), "f")
    S.plus(ell(0, 2, R * 0.55, R * 0.42, R * 0.38, R * 0.5), "e")
    S.minus(ell(0, 1, R * 0.6, R * 0.3, R * 0.3, R * 0.55))
    S.minus(ell(0, 2, 0, R * 0.7, R * 0.45, R * 0.7))
    S.rendern((-R - 1, 0, -R - 1), (R + 1, R, R + 1))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if w.frei(x, y - 1, z) and y > 2 and rng.random() < 0.12:
            w.setze(x, y - 1, z, w.b("ice"))
        if w.frei(x, y + 1, z) and y < R * 0.3 and rng.random() < 0.03 and math.hypot(x, z) < R * 0.6:
            w.setze(x, y + 1, z, w.b("sea_lantern") if rng.random() < 0.3 else w.b("blue_ice"))
    gelaende(w, _r(R + 6), art="schnee", dichte=0.3)
    hohl(w, 3)
    return w


def eisskulpturen(seed, g=1):
    """Eisskulpturen-Garten: Schwan, Bär, Kristallbaum und Wolf aus Eis auf Schneesockeln, Laternenweg."""
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    gelaende(w, _r(12 * u + 6), art="schnee", dichte=0.2)
    figuren = []
    for i, (cx, cz) in enumerate(((-6, -6), (6, -6), (-6, 6), (6, 6))):
        cx, cz = round(cx * u), round(cz * u)
        for x in range(cx - 2, cx + 3):
            for z in range(cz - 2, cz + 3):
                w.setze(x, 1, z, w.b("snow_block"))
        S = Skulptur(w, 0.7 * u + 0.3)
        S.mat("e", lambda x, y, z, lx, ly, lz: d["E"](x, y, z, ly / 8))
        if i == 0:      # Schwan
            S.plus(ell(0, 2, 0, 1.8, 1.2, 2.6), "e")
            S.plus(kap((0, 2.5, 2), (0, 5.5, 2.4), 0.5, 0.4), "e")
            S.plus(kap((0, 5.5, 2.4), (0, 5.2, 3.6), 0.45, 0.25), "e")
            S.plus(lambda X, Y, Z: (np.abs(X) > 0.8) & (np.abs(X) < 2.6) & (Y > 2) & (Y < 4 - np.abs(Z) * 0.3)
                   & (np.abs(Z) < 2.2), "e")
        elif i == 1:    # Bär
            S.plus(ell(0, 3, 0, 2, 2.2, 3), "e")
            S.plus(ell(0, 5, 2.6, 1.3, 1.2, 1.3), "e")
            for sx in (-1, 1):
                for sz in (-1.8, 1.8):
                    S.plus(kap((sx * 1.2, 2, sz), (sx * 1.2, 0, sz), 0.7), "e")
        elif i == 2:    # Kristallbaum
            S.plus(kap((0, 0, 0), (0, 5, 0), 0.6, 0.4), "e")
            for k in range(5):
                a = k / 5 * 2 * math.pi
                S.plus(kap((0, 4, 0), (math.cos(a) * 2.5, 7, math.sin(a) * 2.5), 0.4, 0.15), "e")
        else:           # Wolf (heulend)
            S.plus(ell(0, 2.5, 0, 1.2, 1.4, 2.4), "e")
            S.plus(kap((0, 3.2, 1.8), (0, 6, 2.6), 0.7, 0.5), "e")
            S.plus(kap((0, 6, 2.6), (0, 7.2, 3.6), 0.4, 0.2), "e")
            for sz in (-1.5, 1.5):
                for sx in (-0.6, 0.6):
                    S.plus(kap((sx, 1.5, sz), (sx, 0, sz), 0.35), "e")
        S.rendern((-4, -1, -4), (4, 9, 5), versatz=(cx + 0.5, 2.01, cz + 0.5))
    for k in range(-_r(9 * u), _r(9 * u) + 1, 3):
        w.setze(k, 1, 0, w.b("sea_lantern"))
    hohl(w, 2)
    return w


def schneefestung(seed, g=1):
    """Schneefestung: Wälle und Türmchen aus Schnee mit Zinnen, Schneeball-Depots und Fahne – für Schneeballschlachten."""
    w = _welt(seed)
    d = _eis(w, seed)
    u = U[g]
    a = _r(7 * u + 4, 5)
    gelaende(w, a + 6, art="schnee", dichte=0.2)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if max(abs(x), abs(z)) in (a, a - 1):
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("snow_block") if (x + y + z) % 5 else w.b("packed_ice"))
                if max(abs(x), abs(z)) == a and (x + z) % 2 == 0:
                    w.setze(x, 4, z, w.b("snow_block"))
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in range(1, 7):
                for x, z in kreisrand(1.6, sx * a, sz * a):
                    w.setze(x, y, z, w.b("snow_block"))
            for x, z in kreisrand(2.0, sx * a, sz * a):
                if (x + z) % 2 == 0:
                    w.setze(x, 7, z, w.b("snow_block"))
    for x in (-1, 0, 1):
        for y in (1, 2):
            w.bloecke.pop((x, y, a), None)
            w.bloecke.pop((x, y, a - 1), None)
    for y in range(1, 9):
        w.setze(0, y, 0, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    for k in range(3):
        w.setze(1 + k, 8, 0, w.b("light_blue_wool" if k % 2 else "white_wool"))
    hohl(w, 2)
    return w


EISREICH = {
    "eispalast": ("Eispalast", eispalast),
    "iglu_dorf": ("Iglu-Dorf", iglu_dorf),
    "gletschertor": ("Gletschertor", gletschertor),
    "eiskristall": ("Eiskristall", eiskristall),
    "gefrorener_wasserfall": ("Gefrorener Wasserfall", gefrorener_wasserfall),
    "nordhuette": ("Nordhütte", nordhuette),
    "riesenschneemann": ("Riesenschneemann", riesenschneemann),
    "eiswachturm": ("Eiswachturm", eiswachturm),
    "eisschloss": ("Eisschloss", eisschloss),
    "mammutskelett": ("Mammutskelett", mammutskelett),
    "eisbruecke": ("Eisbrücke", eisbruecke),
    "frostthron": ("Frostthron", frostthron),
    "eislabyrinth": ("Eislabyrinth", eislabyrinth),
    "eisfischer": ("Eisfischer-Lager", eisfischerdorf),
    "frostdrache": ("Frostdrache", frostdrache),
    "polarstation": ("Polarstation", polarstation),
    "gefrorenes_schiff": ("Eingefrorenes Schiff", gefrorenes_schiff),
    "eisgrotte": ("Eisgrotte", eisgrotte),
    "eisskulpturen": ("Eisskulpturen-Garten", eisskulpturen),
    "schneefestung": ("Schneefestung", schneefestung),
}

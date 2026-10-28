"""Bienenstadt – Erweiterung auf 20: Silos, Körbe, Taverne, Drohnenturm, Pollenmühle, Honigfall, Wachstempel,
Blütenarena, Schwarm, Wabenbrücke, Blütenhain."""

from __future__ import annotations

import math

import numpy as np

import modbloecke as MB
import pracht as P
from bienenstadt import (Bienen, U, _boden, _r, _stil, _streu, _welt, biene, hexd, korb, riesenblume, stockhaus,
                         wabensockel)
from lib import Rauschen, laub
from pracht import Mat
from skulptur import Skulptur, ell, kap, kreisrand, scheibe
from weltwunder import hohl


def _hex_saeule(w, f, cx, cz, R, H, y0=1, fenster=True, dach=True):
    for y in range(y0, y0 + H):
        for x in range(cx - int(R) - 1, cx + int(R) + 2):
            for z in range(cz - int(R) - 1, cz + int(R) + 2):
                d = hexd(x - cx, z - cz)
                if R - 1 < d <= R:
                    fen = fenster and (y - y0) % 4 == 2 and abs(x - cx) <= 0 and True
                    w.setze(x, y, z, f.glas if fen else f.gold if (y - y0) % 6 == 5 else
                            f.wabe if (x + y + z) % 5 else f.honig)
    if dach:
        k = 0
        while R - k > 0.3:
            for x in range(cx - int(R) - 1, cx + int(R) + 2):
                for z in range(cz - int(R) - 1, cz + int(R) + 2):
                    if hexd(x - cx, z - cz) <= R + 0.5 - k:
                        w.setze(x, y0 + H + k, z, f.honig if k % 2 else f.wabe)
            k += 1
        w.setze(cx, y0 + H + k, cz, f.gold)
    return y0 + H


def honigsilos(seed, g=2):
    """Honigsilos: eine Gruppe sechseckiger Speichertürme aus Waben mit goldenen Ringen, verbunden durch Laufstege,
    davor Fässer und Honigflaschen-Kisten."""
    w = _welt(seed)
    f = Bienen(w, seed)
    u = U[g]
    R0 = 10 * u + 5
    _boden(w, f, R0)
    n = 3 + g
    for i in range(n):
        a = i / n * 2 * math.pi
        d = 0 if i == 0 else R0 * 0.45
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        R = (2.2 * u + 1.5) * (1.3 if i == 0 else 1.0)
        H = _r((8 + (i % 3) * 3) * u + 4)
        _hex_saeule(w, f, cx, cz, R, H)
        if i:
            L = max(abs(cx), abs(cz))
            for t in np.linspace(0, 1, L * 2):
                w.setze(round(cx * t), _r(H * 0.6), round(cz * t), w.b(f"{f.holz}_slab", type="bottom",
                                                                         waterlogged=False), ueberschreiben=False)
    for k in range(6):
        w.setze(round(R0 * 0.75) - k, 1, round(R0 * 0.5), w.b("barrel", facing="up", open=False) if k % 2 else f.honig)
    _streu(w, f, R0, 0.1)
    hohl(w, 2)
    return w


def bienenkoerbe(seed, g=1):
    """Bienenkorb-Wiese: Reihen geflochtener Strohkörbe auf überdachten Holzbänken, dazwischen Blumenbeete und
    ein Imkerhäuschen."""
    w = _welt(seed)
    f = Bienen(w, seed)
    u = U[g]
    n = 2 + g
    L = n * 5 + 3
    _boden(w, f, L + 3)
    for r in range(2):
        z0 = -6 + r * 12
        for x in range(-L + 2, L - 1):
            w.setze(x, 1, z0, w.b(f"{f.holz}_planks"))
            if x % 4 == 0:
                w.setze(x, 0, z0, w.b(f"{f.holz}_log", axis="y"))
            for dz in (-2, -1, 0, 1, 2):
                w.setze(x, 6 - abs(dz) // 2, z0 + dz, w.b(f"{f.holz}_slab", type="bottom", waterlogged=False))
        for x in range(-L + 2, L - 1, 6):
            for y in (2, 3, 4, 5):
                w.setze(x, y, z0 - 2, w.b(f"{f.holz}_fence", north=False, south=False, east=False, west=False,
                                          waterlogged=False))
        for x in range(-L + 4, L - 2, 4):
            korb(w, f, x, z0, 2, 1.8, 2)
            w.setze(x, 2, z0 + 2, w.b(f"{f.holz}_slab", type="top", waterlogged=False))
    for x, z in scheibe(L):
        if abs(z) in (0, 1, 2) and w.frei(x, 1, z) and w.rng.random() < 0.7:
            w.setze(x, 1, z, w.b(f.ein(f.blumen)))
    st = P.Stil(w, wand="holz_hell", sockel="graustein", gesims="stone_brick", dach="mcw_stroh", holz=f.holz,
                blumen=1.0)
    P.gebaeude(w, st, -L - 6, -3, -L - 1, 3, y0=1, etagen=1, eh=4, dach="sattel", tuer="east", gauben=False)
    hohl(w, 2)
    return w


def honigtaverne(seed, g=1):
    """Honigtaverne „Zum Goldenen Stachel“: fassförmiges Rundhaus mit Holzreifen, Honigglas-Fenstern, Terrasse mit
    Fass-Tischen, Wabenschild und Laternen."""
    w = _welt(seed)
    f = Bienen(w, seed)
    u = U[g]
    R = 3.5 * u + 3
    H = _r(5 * u + 4)
    _boden(w, f, _r(R + 7))
    for y in range(1, H + 1):
        t = (y - 1) / max(1, H - 1)
        r = R * (0.88 + 0.12 * math.sin(t * math.pi))
        for x, z in kreisrand(r):
            reif = y in (2, H - 1) or y == H // 2 + 1
            fen = y % 4 == 3 and (x + z) % 3 == 0 and not reif
            w.setze(x, y, z, w.b("iron_block") if reif and False else w.b("stripped_dark_oak_log", axis="y")
                    if reif else f.glas if fen else w.b(f"{f.holz}_planks") if (x + z) % 2 else
                    w.b(f"stripped_{f.holz}_log", axis="y"))
    for x, z in scheibe(R * 0.9):
        w.setze(x, H + 1, z, w.b(f"{f.holz}_planks"))
    korb(w, f, 0, 0, H + 2, R * 0.6, _r(R * 0.6))
    for y in (1, 2):
        w.bloecke.pop((0, y, round(R)), None)
    for x, z in scheibe(R + 4):
        if z > R and abs(x) < R + 3 and math.hypot(x, z) > R + 0.5:
            w.setze(x, 0, z, w.b(f"{f.holz}_planks"))
    for i in range(3):
        x, z = -round(R) + 2 + i * round(R), round(R) + 3
        w.setze(x, 1, z, w.b("barrel", facing="up", open=False))
        w.setze(x, 2, z, w.b("candle", candles=2, lit=True, waterlogged=False) if i % 2 else f.honig)
        for dx in (-1, 1):
            w.setze(x + dx, 1, z, w.b(f"{f.holz}_stairs", facing="east" if dx < 0 else "west", half="bottom",
                                      shape="straight", waterlogged=False))
    w.setze(2, 4, round(R) + 1, f.wabe)
    w.setze(2, 4, round(R) + 2, f.gold) if False else None
    hohl(w, 2)
    return w


def drohnenturm(seed, g=2):
    """Drohnenturm: schlanker Wabenturm mit drei Blüten-Landeplattformen in verschiedenen Höhen, Bienen im Anflug
    und ein Leuchtfeuer aus Froschlicht."""
    w = _welt(seed)
    f = Bienen(w, seed)
    u = U[g]
    H = _r(16 * u + 8)
    R = 1.6 * u + 1.4
    _boden(w, f, _r(9 * u + 5))
    _hex_saeule(w, f, 0, 0, R, H)
    for i, hf in enumerate((0.35, 0.6, 0.85)):
        y = round(H * hf)
        a = i * 2.1
        cx, cz = round(math.cos(a) * (R + 3 * u)), round(math.sin(a) * (R + 3 * u))
        farbe = f.bluete[i % len(f.bluete)]
        for x, z in scheibe(2 * u + 1.5, cx, cz):
            d = math.hypot(x - cx, z - cz)
            w.setze(x, y, z, w.b("yellow_concrete") if d < 1.2 else farbe)
        for t in np.linspace(0, 1, 6):
            w.setze(round(cx * (1 - t) * 0.6), y - 1, round(cz * (1 - t) * 0.6), w.b("green_concrete"))
    w.setze(0, H + int(R) + 3, 0, f.licht)
    biene(w, f, round(R + 6 * u), round(H * 0.5), 2, 0.4 * u + 0.2, drehung=1.0)
    _streu(w, f, _r(9 * u + 5), 0.12)
    hohl(w, 2)
    return w


def pollenmuehle(seed, g=2):
    """Pollenmühle: Windmühle in Bienenkorbform, deren Flügel riesige Blütenblätter sind; Pollensäcke, Mahlstein
    (Create-Mühlstein als Mod-Block) und Honigkanne."""
    w = _welt(seed)
    f = Bienen(w, seed)
    u = U[g]
    R = 3.5 * u + 2.5
    H = _r(9 * u + 5)
    _boden(w, f, _r(R + 12))
    top = korb(w, f, 0, 0, 1, R, H)
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b(f"{f.holz}_planks"))
    zy = round(H * 0.7)
    zz = round(R) + 1
    w.setze(0, zy, zz, f.gold)
    L = _r(8 * u + 4)
    for i in range(5):
        a = i / 5 * 2 * math.pi
        farbe = f.bluete[i % len(f.bluete)]
        for k in range(1, L + 1):
            breite = 2.2 * u * math.sin(k / L * math.pi) + 0.5
            for q in np.linspace(-breite, breite, max(2, int(breite * 2) + 1)):
                px = round(math.cos(a) * k - math.sin(a) * q)
                py = round(zy + math.sin(a) * k + math.cos(a) * q)
                w.setze(px, py, zz + 1, farbe if abs(q) > 0.6 else w.b("yellow_wool"))
    for k in range(4):
        w.setze(round(R) + 2, 1, -2 + k, MB.mod(w, "supplementaries:sack", "yellow_wool", open=False))
    w.setze(-round(R) - 2, 1, 0, MB.mod(w, "create:millstone", "grindstone", {"face": "floor", "facing": "north"}))
    hohl(w, 2)
    return w


def honigfall(seed, g=2):
    """Honigfall: ein Felsen voller Waben, aus dessen Spalte ein Honigstrom in Kaskaden in ein sechseckiges
    Becken fließt; Bienennester in der Wand, Blumen am Ufer."""
    w = _welt(seed)
    f = Bienen(w, seed)
    u = U[g]
    R = 9 * u + 4
    H = _r(10 * u + 5)
    _boden(w, f, R + 5)
    r_n = Rauschen(w, 3)
    fels = Mat(w, ["stone", "andesite", "honeycomb_block", "dirt", "mossy_cobblestone"], kontrast=1.2)
    for x in range(-_r(R), _r(R) + 1):
        for z in range(-_r(R), -_r(R * 0.15)):
            d = math.hypot(x, z * 1.4) / R
            hh = int(H * max(0, 1 - d * d) * (0.8 + 0.4 * r_n(x, 0, z)))
            for y in range(1, hh + 1):
                w.setze(x, y, z, fels(x, y, z, y / H))
            if hh > 0:
                w.setze(x, hh + 1, z, f.ein(f.boden))
    zf = -_r(R * 0.15)
    ytop = max([y for (x, y, z) in w.bloecke if abs(x) <= 1 and z == zf - 1] + [3])
    for y in range(1, ytop + 1):
        for x in (-1, 0, 1):
            w.setze(x, y, zf - 1, f.honig)
    for x in range(-_r(R * 0.5), _r(R * 0.5) + 1):
        for z in range(zf, zf + _r(R * 0.7)):
            if hexd(x, z - zf - R * 0.35) <= R * 0.35:
                w.setze(x, 0, z, f.honig)
                w.setze(x, -1, z, f.wabe)
    for (x, y, z), b in list(w.bloecke.items()):
        if z == zf - 2 and y > 2 and w.rng.random() < 0.05:
            w.bloecke[(x, y, z)] = w.b("bee_nest", facing="south", honey_level=5)
    _streu(w, f, R + 4, 0.15)
    hohl(w, 3)
    return w


def wachstempel(seed, g=2):
    """Wachstempel: sechseckiger Tempel mit Säulen aus Wabenblöcken, goldener Kuppel, unzähligen gelben Kerzen auf
    Stufen und einer goldenen Bienenkönigin im Inneren."""
    w = _welt(seed)
    f = Bienen(w, seed)
    u = U[g]
    R = 6 * u + 4
    _boden(w, f, _r(R + 4))
    for k in range(3):
        for x in range(-_r(R) - 2, _r(R) + 3):
            for z in range(-_r(R) - 2, _r(R) + 3):
                if hexd(x, z) <= R + 1 - k:
                    w.setze(x, 1 + k, z, f.wabe if (x + z + k) % 3 else f.honig)
    Hs = _r(6 * u + 4)
    for i in range(6):
        a = i / 6 * 2 * math.pi + math.pi / 6
        x, z = round(math.cos(a) * (R - 2)), round(math.sin(a) * (R - 2))
        for y in range(4, 4 + Hs):
            w.setze(x, y, z, f.wabe if y % 3 else f.gold)
    for x in range(-_r(R), _r(R) + 1):
        for z in range(-_r(R), _r(R) + 1):
            d = hexd(x, z)
            if R - 3 < d <= R - 1:
                w.setze(x, 4 + Hs, z, f.gold if (x + z) % 2 else f.honig)
    from wueste_eis import kuppel
    kuppel(w, f.gold, 0, 0, 5 + Hs, R - 2.5, form="zwiebel", spitze=None)
    rng = w.rng
    for x in range(-_r(R) - 2, _r(R) + 3):
        for z in range(-_r(R) - 2, _r(R) + 3):
            for k in range(3):
                if abs(hexd(x, z) - (R + 1 - k)) < 0.5 and w.frei(x, 2 + k, z) and rng.random() < 0.35:
                    w.setze(x, 2 + k, z, w.b("yellow_candle" if rng.random() < 0.7 else "orange_candle",
                                             candles=int(rng.integers(1, 5)), lit=True, waterlogged=False))
    biene(w, f, 0, 4 + 3.4 * (0.4 * u + 0.2) + 1, 0, 0.4 * u + 0.2, drehung=0.3)
    hohl(w, 2)
    return w


def bluetenarena(seed, g=2):
    """Blütenarena: ein Amphitheater, dessen Sitzreihen wie riesige Blütenblätter angeordnet sind, in der Mitte
    eine Wabenbühne mit Honigbrunnen."""
    w = _welt(seed)
    f = Bienen(w, seed)
    u = U[g]
    R = 10 * u + 5
    _boden(w, f, _r(R + 3))
    for x, z in scheibe(R):
        d = math.hypot(x, z)
        a = math.atan2(z, x)
        blatt = int((a + math.pi) / (2 * math.pi) * 8) % 8
        if d < R * 0.3:
            w.setze(x, 1, z, f.wabe if hexd(x, z) % 2 < 1 else f.gold)
            continue
        stufe = int((d - R * 0.3) / (R * 0.7) * (3 + g))
        farbe = f.bluete[blatt % len(f.bluete)]
        for y in range(1, stufe + 2):
            w.setze(x, y, z, farbe if y == stufe + 1 else w.b("yellow_terracotta"))
    for x, z in scheibe(1.5):
        w.setze(x, 2, z, f.honig)
    _streu(w, f, _r(R + 3), 0.1)
    hohl(w, 2)
    return w


def schwarm(seed, g=2):
    """Bienenschwarm-Skulptur: eine spiralförmige Säule aus Waben, um die mehrere große Bienen kreisen,
    getragen von goldenen Stangen; Blumenring am Fuß."""
    w = _welt(seed)
    f = Bienen(w, seed)
    u = U[g]
    H = _r(12 * u + 6)
    R = 6 * u + 3
    _boden(w, f, _r(R + 5))
    wabensockel(w, f, 0, 0, 2.5 * u + 1.5, 2)
    for y in range(2, H):
        a = y * 0.5
        for k in range(2):
            x = round(math.cos(a + k * math.pi) * 1.2)
            z = round(math.sin(a + k * math.pi) * 1.2)
            w.setze(x, y, z, f.wabe if (y + k) % 3 else f.honig)
    n = 3 + g
    for i in range(n):
        a = i / n * 2 * math.pi
        y = round(H * (0.35 + 0.6 * i / n))
        x, z = round(math.cos(a) * R * 0.75), round(math.sin(a) * R * 0.75)
        for t in np.linspace(0.15, 0.85, 6):
            w.setze(round(x * t), round(y - 1), round(z * t), w.b("chain", axis="x" if abs(x) > abs(z) else "z",
                                                                     waterlogged=False))
        biene(w, f, x, y, z, 0.3 * u + 0.15, drehung=-a + math.pi / 2)
    _streu(w, f, _r(R + 5), 0.18)
    hohl(w, 2)
    return w


def wabenbruecke(seed, g=1):
    """Wabenbrücke: Bogenbrücke aus Waben- und Honigblöcken über einen Bach, Geländer aus Goldstäben,
    Bienenstatuen auf den Brückenköpfen."""
    w = _welt(seed)
    f = Bienen(w, seed)
    u = U[g]
    L = _r(8 * u + 5)
    _boden(w, f, L + 5)
    for x in range(-L - 5, L + 6):
        for z in range(-2, 3):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("gravel"))
    for z in range(-L, L + 1):
        y = round(1 + (1 - (z / L) ** 2) * 2.5 * u)
        for x in range(-2, 3):
            w.setze(x, y, z, f.wabe if (x + z) % 3 else f.honig)
            w.setze(x, y - 1, z, f.wabe) if abs(z) < L * 0.5 else None
        for x in (-3, 3):
            w.setze(x, y + 1, z, w.b("lightning_rod", facing="up", powered=False, waterlogged=False)
                    if z % 2 else f.gold)
    for sz in (-1, 1):
        biene(w, f, 4, 3.4 * (0.25 * u + 0.15) + 2, sz * L, 0.25 * u + 0.15, drehung=0.0)
        wabensockel(w, f, 4, sz * L, 1.5 * u + 1, 2)
    _streu(w, f, L + 5, 0.12)
    hohl(w, 2)
    return w


def bluetenhain(seed, g=2):
    """Blütenhain: ein Wäldchen aus Riesenblumen in allen Farben und Höhen, dazwischen Bienen, Blütenteppich
    und kleine Bienenstöcke."""
    w = _welt(seed)
    f = Bienen(w, seed)
    u = U[g]
    R = 11 * u + 5
    _boden(w, f, R)
    rng = w.rng
    n = 5 + 3 * g
    for i in range(n):
        a = i * 2.39996
        d = R * 0.8 * math.sqrt((i + 0.5) / n)
        riesenblume(w, f, round(math.cos(a) * d), round(math.sin(a) * d), 0.45 * u + 0.3 + 0.15 * rng.random(),
                    hoehe=0.7 + 0.6 * rng.random())
    for i in range(1 + g):
        a = rng.random() * 2 * math.pi
        biene(w, f, round(math.cos(a) * R * 0.5), round(8 * u + 4), round(math.sin(a) * R * 0.5), 0.25 * u + 0.12,
              drehung=a)
    _streu(w, f, R, 0.35)
    return w


NEU = {
    "honigsilos": ("Honigsilos", honigsilos),
    "bienenkoerbe": ("Bienenkorb-Wiese", bienenkoerbe),
    "honigtaverne": ("Honigtaverne", honigtaverne),
    "drohnenturm": ("Drohnenturm", drohnenturm),
    "pollenmuehle": ("Pollenmühle", pollenmuehle),
    "honigfall": ("Honigfall", honigfall),
    "wachstempel": ("Wachstempel", wachstempel),
    "bluetenarena": ("Blütenarena", bluetenarena),
    "schwarm": ("Bienenschwarm", schwarm),
    "wabenbruecke": ("Wabenbrücke", wabenbruecke),
    "bluetenhain": ("Blütenhain", bluetenhain),
}

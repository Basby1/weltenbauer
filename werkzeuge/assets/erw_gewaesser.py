"""Flüsse, Seen & Wasserfälle II – zwanzig weitere Gewässer: Flusstor, Mäanderschleife mit Altarm, Hängetal-Fall,
Gefrorener Wasserfall, Quelltopf, Gletschertöpfe, Klamm mit Steig, Schäreninseln, Wasserstrudel, Furt mit Trittsteinen,
Weidenufer, Seenkette, Flussmündung mit Sandbank, Moosbach, Dolinenfall, Landzunge, Umlaufberg, Schleusentreppe,
Stausee und Eisschollensee."""

from __future__ import annotations

import math

import wald2
from erw_basis import M, S, baum, fichte, figur, haus, hoehe
from feinbau import laterne
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen, einfuegen


def landschaft(w, R, hf, wy=None, schnee=False, fels_steil=2, sand=True, gras_deko=0.08, boden_tief=6):
    """Gelände aus Höhenfunktion hf(x, z); Wasser bis wy; steile Stellen als Fels. Gibt Höhen zurück."""
    rn = Rauschen(w, 5)
    f = M(w, [("stone", 3), ("andesite", 2), ("cobblestone", 1), ("tuff", 0.5)])
    rng = w.rng
    hs = {}
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) <= R + 2 * rn(x, 0, z):
                hs[(x, z)] = round(hf(x, z))
    for (x, z), h in hs.items():
        steil = max(abs(hs.get((x + dx, z + dz), h) - h) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        unten = min(h, (wy if wy is not None else h) - 3) - boden_tief
        for y in range(unten, h + 1):
            if y < h - 2 or steil >= fels_steil:
                b = f(x, y, z)
            elif y < h:
                b = w.b("dirt")
            elif wy is not None and h <= wy:
                b = w.b("sand") if sand and rn(x, 2, z) < 0.5 else w.b("gravel") if h < wy else w.b("sand")
            elif schnee:
                b = w.b("snow_block")
            else:
                b = w.b("grass_block", snowy=False)
            w.setze(x, y, z, b)
        if wy is not None and h < wy:
            for y in range(h + 1, wy + 1):
                w.setze(x, y, z, w.b("water", level=0))
        elif steil < fels_steil and not schnee and rng.random() < gras_deko and (wy is None or h > wy):
            w.setze(x, h + 1, z, w.b(["grass", "grass", "fern", "dandelion", "poppy", "azure_bluet"]
                                     [int(rng.integers(6))]))
        elif schnee and steil < fels_steil and (wy is None or h > wy):
            w.setze(x, h + 1, z, w.b("snow", layers=1 + int(rn(x, 9, z) * 2)))
    return hs


def baeume(w, hs, n, seed, art="laub", H=(7, 11), wy=None, frei=None):
    rng = w.rng
    pts = list(hs.items())
    k = 0
    for _ in range(n * 6):
        if k >= n:
            break
        (x, z), h = pts[int(rng.integers(len(pts)))]
        if wy is not None and h <= wy + 1:
            continue
        if frei and frei(x, z):
            continue
        if not w.frei(x, h + 1, z) or (x, h, z) not in w.bloecke:
            continue
        nb = [hs.get((x + dx, z + dz), h) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        if max(abs(v - h) for v in nb) > 1:
            continue
        hh = H[0] + rng.random() * (H[1] - H[0])
        if art == "fichte":
            fichte(w, x, h + 1, z, seed + k, hh)
        elif art == "weide":
            einfuegen(w, wald2.weide(seed + k * 7, H=int(hh)), x, h + 1, z)
        elif art == "kiefer":
            einfuegen(w, wald2.kiefer(seed + k * 5, H=int(hh)), x, h + 1, z)
        else:
            baum(w, x, h + 1, z, seed + k, hh, holz="oak" if k % 3 else "birch")
        k += 1


def schilf(w, hs, wy, n):
    rng = w.rng
    for (x, z), h in hs.items():
        if h in (wy, wy - 1) and rng.random() < n:
            top = max(h, wy) + 1
            for y in range(top, top + 1 + int(rng.random() * 2)):
                w.setze(x, y, z, w.b("sugar_cane", age=0))


def fall(w, x0, z0, y0, y1, breite, achse="x", fels=None):
    """Wasserfall-Säule: Wasser von y0 hinab bis y1 vor einer Felswand."""
    for d in range(-breite, breite + 1):
        x, z = (x0 + d, z0) if achse == "x" else (x0, z0 + d)
        for y in range(y1, y0 + 1):
            w.setze(x, y, z, w.b("water", level=0))


# ============================================================================ Gewässer

def flusstor(seed, g=2):
    """Flusstor: ein Fluss hat sich durch einen Felsrücken gefressen und ein gewaltiges natürliches Felsentor
    stehen lassen, unter dem das Wasser hindurchströmt; bewaldete Hänge rechts und links."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 6)
    H = 6 * s + 4

    def hf(x, z):
        mz = math.sin(x / 7) * 2
        d = abs(z - mz)
        return -2 if d < 2.5 + s else min(H, (d - 2.5 - s) * 1.2) + rn(x, 1, z) * 2

    hs = landschaft(w, R, hf, wy=0)
    st = M(w, [("stone", 3), ("andesite", 2), ("granite", 1), ("mossy_cobblestone", 1)])
    Ht = 6 * s + 5
    for k in range(3):
        dz = (k - 1) * (1 + 0.5 * s)
        pts = bez((0, -1, -5 - 3 * s + dz), (0, Ht * 1.5, dz), (0, -1, 5 + 3 * s + dz))
        rohr(w, pts, 1.8 + 0.6 * s, 1.8 + 0.6 * s, st, rauh=0.25)
    for x in range(-3, 4):
        for z in range(-int(3 + s), int(3 + s) + 1):
            for y in range(1, 4):
                if abs(z - math.sin(x / 7) * 2) < 2.5 + s:
                    w.bloecke.pop((x, y, z), None)
    baeume(w, hs, int(6 + 5 * s), seed, art="fichte", wy=0)
    return w


def maeanderschleife(seed, g=2):
    """Mäanderschleife mit Altarm: ein träger Fluss zieht in weiten Schleifen durch eine flache Aue; ein
    abgeschnürter Altarm liegt als sichelförmiger Teich daneben, mit Schilf und Seerosen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    A = R * 0.4
    bw = 1.5 + 0.7 * s

    def fluss(x):
        return math.sin(x / (R * 0.25)) * A

    def hf(x, z):
        d = abs(z - fluss(x))
        alt = abs(math.hypot(x - R * 0.35, z + A * 0.2) - A * 0.8) < bw and z < 0 and x > 0
        return -1 if d < bw or alt else 1

    hs = landschaft(w, R, hf, wy=0, gras_deko=0.12)
    rng = w.rng
    for (x, z), h in hs.items():
        if h < 0 and rng.random() < 0.03:
            w.setze(x, 1, z, w.b("lily_pad"))
    schilf(w, hs, 0, 0.0)
    for (x, z), h in hs.items():
        if h == 1 and any(hs.get((x + dx, z + dz), 1) < 0 for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))) and \
                rng.random() < 0.3:
            w.setze(x, 2, z, w.b("sugar_cane", age=0))
            w.setze(x, 3, z, w.b("sugar_cane", age=0))
    baeume(w, hs, int(4 + 3 * s), seed, art="weide", H=(6, 9), wy=0)
    return w


def haengetalfall(seed, g=2):
    """Hängetal-Fall: ein hoch gelegenes Seitental mündet als Felsstufe über einem breiten Haupttal; sein Bach stürzt
    als schmaler, hoher Wasserfall in den Fluss unten."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 5)
    H = int(10 * s + 7)

    def hf(x, z):
        if z > R * 0.15:
            return -1 if abs(z - R * 0.45 - math.sin(x / 6)) < 2 + s * 0.5 else 1 + rn(x, 2, z) * 1.5
        bach = abs(x - math.sin(z / 4)) < 1.5
        return H - (1 if bach else 0) + (0 if bach else rn(x, 3, z) * 3)

    hs = landschaft(w, R, hf, wy=0)
    zf = int(R * 0.15)
    for z in range(-R, zf + 1):
        for dx in (-1, 0, 1):
            x = round(math.sin(z / 4)) + dx
            if (x, z) in hs and hs[(x, z)] >= H - 2:
                w.setze(x, H, z, w.b("water", level=0))
                w.bloecke.pop((x, H + 1, z), None)
    for y in range(0, H + 1):
        for dx in (-1, 0, 1):
            w.setze(round(math.sin(zf / 4)) + dx, y, zf + 1, w.b("water", level=0))
    baeume(w, hs, int(6 + 4 * s), seed, art="fichte", wy=0)
    return w


def gefrorener_fall(seed, g=2):
    """Gefrorener Wasserfall: an einer hohen Felswand ist ein breiter Wasserfall zu Säulen und Vorhängen aus blauem
    und weißem Eis erstarrt; darunter ein zugefrorener Teich, verschneite Fichten und Felsen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    H = int(10 * s + 8)

    def hf(x, z):
        if z < -R * 0.15:
            return H + rn(x, 2, z) * 2
        return 0 + rn(x, 3, z) * 1.2

    hs = landschaft(w, R, hf, schnee=True)
    rng = w.rng
    B = int(3 + 2 * s)
    zf = -int(R * 0.15)
    for x in range(-B, B + 1):
        for y in range(1, H + 1):
            dicke = 1 + int(2 * (1 - y / H) + rn(x, y, 0) * 1.5)
            for dz in range(dicke):
                w.setze(x, y, zf + 1 + dz, w.b("blue_ice") if (x + y) % 4 == 0 else
                        w.b("packed_ice") if rng.random() < 0.6 else w.b("ice"))
    for (x, z), h in hs.items():
        if math.hypot(x, z - R * 0.2) < R * 0.35:
            w.setze(x, h, z, w.b("ice"))
            w.bloecke.pop((x, h + 1, z), None)
    baeume(w, hs, int(5 + 3 * s), seed, art="fichte", frei=lambda x, z: z < zf + 4)
    return w


def quelltopf(seed, g=1):
    """Quelltopf: ein kreisrunder, tiefblauer Karstquellteich, dessen Grund trichterförmig in die Tiefe abfällt; ein
    klarer Bach fließt über moosige Steine ab, Farne und Buchen säumen das Ufer."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    rq = R * 0.4
    rn = Rauschen(w, 4)

    def hf(x, z):
        d = math.hypot(x, z + R * 0.1)
        if d < rq:
            return -(rq - d) * 1.6 - 1
        if abs(x - math.sin(z / 3)) < 1.2 and z > 0:
            return -1
        return 1 + rn(x, 2, z) * 1.5

    hs = landschaft(w, R, hf, wy=0, boden_tief=4)
    for (x, z), h in hs.items():
        if h < -3:
            w.setze(x, h, z, w.b("light_blue_terracotta") if h > -rq * 1.2 else w.b("blue_terracotta"))
    for (x, z), h in hs.items():
        if 0 <= h <= 1 and any(hs.get((x + dx, z + dz), 1) < 0 for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            w.setze(x, h, z, w.b("mossy_cobblestone"))
    baeume(w, hs, int(4 + 3 * s), seed, art="laub", wy=0)
    return w


def gletschertoepfe(seed, g=2):
    """Gletschertöpfe: ein Bach fließt über glatt geschliffenen Fels, in den das Wasser kreisrunde, tiefe Töpfe
    gestrudelt hat; in jedem steht klares Wasser, auf manchen liegen runde Mahlsteine."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 6)

    def hf(x, z):
        return 1 + rn(x, 2, z) * 2 + z * -0.08

    hs = landschaft(w, R, hf, fels_steil=1)
    fels = M(w, [("smooth_stone", 2), ("diorite", 2), ("polished_diorite", 1), ("andesite", 1)])
    for (x, z), h in hs.items():
        if math.hypot(x, z) < R * 0.8:
            w.setze(x, h, z, fels(x, h, z))
            w.bloecke.pop((x, h + 1, z), None)
        if abs(x - math.sin(z / 4) * 2) < 1.2:
            w.setze(x, h, z, w.b("water", level=0))
    rng = w.rng
    for k in range(int(5 + 4 * s)):
        a = rng.random() * 6.28
        r = rng.random() * R * 0.65
        cx, cz = math.cos(a) * r, math.sin(a) * r
        rt = 1 + rng.random() * (1 + s)
        for x in range(int(cx - rt) - 1, int(cx + rt) + 2):
            for z in range(int(cz - rt) - 1, int(cz + rt) + 2):
                if math.hypot(x - cx, z - cz) <= rt and (x, z) in hs:
                    h = hs[(x, z)]
                    for y in range(h - int(rt * 1.5), h + 1):
                        w.setze(x, y, z, w.b("water", level=0))
        if k % 3 == 0:
            kugel(w, cx, hs.get((round(cx), round(cz)), 1) - rt, cz, 0.8, w.b("cobblestone"))
    return w


def klamm(seed, g=2):
    """Klamm mit Steig: ein tosender Wildbach hat eine enge, tiefe Schlucht gesägt; an der Felswand klebt ein Holzsteg
    auf Eisenstützen, Brücken queren die Klamm, Moos und Farn wachsen an den nassen Wänden."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    H = int(10 * s + 8)
    sp = 2 + s

    def hf(x, z):
        mz = math.sin(x / 4) * 1.5
        if abs(z - mz) < sp:
            return -3
        return (H if z < mz else 1) + rn(x, 2, z) * 2

    hs = landschaft(w, R, hf, wy=-2, fels_steil=2)
    rng = w.rng
    for (x, z), h in hs.items():
        if h > 0:
            for y in range(1, h):
                if w.frei(x, y, z + 1) and rng.random() < 0.06:
                    w.setze(x, y, z, w.b("moss_block"))
    ys = int(H * 0.35)
    for x in range(-R, R + 1):
        mz = math.sin(x / 4) * 1.5
        zs = round(mz - sp) + 1
        if (x, zs - 1) not in hs:
            continue
        w.setze(x, ys, zs, w.b("spruce_slab", type="top", waterlogged=False), False)
        w.setze(x, ys + 1, zs + 1, w.b("spruce_fence"), False) if x % 2 == 0 else None
        if x % 4 == 0:
            w.setze(x, ys - 1, zs, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                       waterlogged=False), False)
    for bx in (-int(R * 0.4), int(R * 0.4)):
        mz = math.sin(bx / 4) * 1.5
        for z in range(round(mz - sp), round(mz + sp) + 1):
            w.setze(bx, ys, z, w.b("spruce_planks"), False)
            w.setze(bx + 1, ys + 1, z, w.b("spruce_fence"), False)
    return w


def schaereninseln(seed, g=2):
    """Schäreninseln: im flachen Meer liegen dutzende rundgeschliffene Granitinseln, manche nackt, manche mit Moos,
    Kiefern und einem roten Bootshaus; Seegras und Steine im klaren Wasser dazwischen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rng = w.rng
    inseln = [(0, 0, 3 + 1.5 * s)]
    for k in range(int(6 + 4 * s)):
        a = rng.random() * 6.28
        r = R * (0.3 + rng.random() * 0.6)
        inseln.append((math.cos(a) * r, math.sin(a) * r, 1 + rng.random() * (1.5 + s)))
    rn = Rauschen(w, 3)

    def hf(x, z):
        best = -3.0
        for (cx, cz, ri) in inseln:
            d = math.hypot(x - cx, z - cz) / ri
            if d < 1.3:
                best = max(best, (1 - d) * ri * 0.8 + rn(x, 1, z) * 0.6)
        return best

    hs = landschaft(w, R, hf, wy=0, fels_steil=1, sand=False)
    gr = M(w, [("granite", 3), ("polished_granite", 1), ("diorite", 1)])
    for (x, z), h in hs.items():
        if h >= 1:
            w.setze(x, h, z, gr(x, h, z) if rn(x, 5, z) < 0.65 else w.b("moss_block"))
        elif h < 0 and rng.random() < 0.08:
            w.setze(x, h + 1, z, w.b("seagrass"))
    for k, (cx, cz, ri) in enumerate(inseln[:4]):
        if ri > 2:
            x, z = round(cx), round(cz)
            einfuegen(w, wald2.kiefer(seed + k, H=int(6 + 3 * s)), x, hs.get((x, z), 1) + 1, z)
    x0 = round(inseln[0][0]) + 2
    haus(w, x0, 2, 4, 3, hs.get((x0, 2), 1) + 1, M(w, [("red_terracotta", 2), ("red_concrete", 1)]),
         holz="spruce", H=2, dach=("deepslate_tile",), tuer_s="south", schorn=False)
    return w


def wasserstrudel(seed, g=2):
    """Wasserstrudel: in einer Felsbucht dreht sich ein gewaltiger Strudel – spiralige Schaumbänder auf dem Wasser
    ziehen sich zu einem dunklen Schlund in der Mitte; Felsen und Gischt am Rand."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)

    def hf(x, z):
        d = math.hypot(x, z)
        if d > R * 0.82:
            return 3 + rn(x, 2, z) * 4
        return -3 - max(0, (R * 0.25 - d)) * 1.5

    hs = landschaft(w, R, hf, wy=0, fels_steil=1, sand=False)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if 2 < d < R * 0.75:
                a = math.atan2(z, x)
                arm = math.sin(a * 3 + math.log(d) * 4)
                if arm > 0.75:
                    w.setze(x, 0, z, w.b("white_concrete_powder") if (x + z) % 2 else w.b("white_wool"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            if math.hypot(x, z) < 1.8:
                for y in range(-12, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -13, z, w.b("magma_block"))
    return w


def furt(seed, g=1):
    """Furt mit Trittsteinen: ein breiter, flacher Fluss mit Kiesbänken, über den ein Feldweg durch das seichte
    Wasser führt; daneben eine Reihe großer Trittsteine für Fußgänger und ein Wegweiser."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    rn = Rauschen(w, 4)
    bw = 3 + 1.5 * s

    def hf(x, z):
        d = abs(z - math.sin(x / 6) * 1.5)
        if d < bw:
            return -1 if rn(x, 2, z) > 0.3 else 0
        return 1 + rn(x, 3, z) * 0.8

    hs = landschaft(w, R, hf, wy=0)
    for z in range(-R, R + 1):
        for x in (-1, 0, 1):
            if (x, z) in hs:
                h = hs[(x, z)]
                if h >= 1:
                    w.setze(x, h, z, w.b("dirt_path") if (x + z) % 3 else w.b("coarse_dirt"))
                    w.bloecke.pop((x, h + 1, z), None)
                else:
                    w.setze(x, -1, z, w.b("gravel"))
    for z in range(-int(bw) - 1, int(bw) + 2, 2):
        w.setze(4, 0, z, w.b("smooth_stone"))
        w.setze(4, 1, z, w.b("stone_slab", type="bottom", waterlogged=False))
    sx, sz = 3, int(bw) + 3
    for y in range(1, 4):
        w.setze(sx, y + hs.get((sx, sz), 1), sz, w.b("spruce_fence"))
    w.setze(sx + 1, hs.get((sx, sz), 1) + 3, sz, w.b("spruce_planks"))
    baeume(w, hs, int(3 + 2 * s), seed, art="laub", wy=0, frei=lambda x, z: abs(x) < 6)
    return w


def weidenufer(seed, g=1):
    """Weidenufer: an einem stillen Flussufer hängen Trauerweiden ihre Zweige ins Wasser, Wurzeln ragen aus der
    Böschung, Schilf, Seerosen, eine Bank und ein angebundenes Ruderboot."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    rn = Rauschen(w, 4)

    def hf(x, z):
        return -2 if z > R * 0.1 + math.sin(x / 5) * 1.5 else 1 + rn(x, 2, z) * 0.8

    hs = landschaft(w, R, hf, wy=0)
    schilf(w, hs, 0, 0.0)
    rng = w.rng
    for (x, z), h in hs.items():
        if h < 0 and rng.random() < 0.04:
            w.setze(x, 1, z, w.b("lily_pad"))
        if h == 1 and hs.get((x, z + 1), 1) < 0 and rng.random() < 0.35:
            w.setze(x, 2, z, w.b("sugar_cane", age=0))
            w.setze(x, 3, z, w.b("sugar_cane", age=0))
    for k in range(int(2 + s)):
        x = -int(R * 0.5) + k * int(R * 0.5)
        z = int(R * 0.05)
        einfuegen(w, wald2.weide(seed + k * 3, H=int(7 + 2 * s)), x, hs.get((x, z), 1) + 1, z)
    bx, bz = int(R * 0.3), int(R * 0.35)
    for dx in range(-2, 3):
        for dz in (-1, 0, 1):
            if abs(dz) == 1 or abs(dx) == 2:
                w.setze(bx + dx, 1, bz + dz, w.b("spruce_slab", type="bottom", waterlogged=True))
    w.setze(bx - 3, 1, bz, w.b("spruce_fence"))
    for k in range(3):
        w.setze(-2 + k, 2, -2, w.b("spruce_stairs", facing="north", half="bottom", shape="straight",
                                   waterlogged=False))
    return w


def seenkette(seed, g=2):
    """Seenkette: mehrere kleine, türkisgrüne Seen liegen stufenweise übereinander im Wald und sind durch niedrige
    Kalksinterbarrieren getrennt, über die das Wasser in vielen kleinen Fällen rinnt."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 5)
    n = int(3 + s)
    stufe = 2

    def ebene(z):
        return max(0, min(n - 1, int((-z + R) / (2 * R / n))))

    def hf(x, z):
        k = ebene(z)
        see = abs(x - math.sin(z / 5) * 2) < R * 0.35 + rn(x, 1, z) * 2
        return k * stufe - 2 if see else k * stufe + 2 + rn(x, 2, z) * 2

    hs = landschaft(w, R, hf, wy=None)
    for (x, z), h in hs.items():
        k = ebene(z)
        if h <= k * stufe - 1:
            for y in range(h + 1, k * stufe + 1):
                w.setze(x, y, z, w.b("water", level=0))
            w.setze(x, h, z, w.b("prismarine") if (x + z) % 3 == 0 else w.b("light_blue_terracotta"))
    for k in range(1, n):
        zb = round(R - k * 2 * R / n)
        for x in range(-R, R + 1):
            if (x, zb) in hs and hs[(x, zb)] < k * stufe:
                w.setze(x, k * stufe - 1, zb, w.b("calcite"))
                w.setze(x, k * stufe, zb, w.b("water", level=0) if x % 3 else w.b("calcite"))
    baeume(w, hs, int(6 + 4 * s), seed, art="laub")
    return w


def flussmuendung(seed, g=2):
    """Flussmündung mit Sandbank: ein Fluss weitet sich zum Meer hin trichterförmig, eine lange Sandbank mit
    Muschelschalen und Seegras liegt in der Mündung, Dünen mit Strandhafer säumen die Küste."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 5)

    def hf(x, z):
        breite = 2 + max(0, (z + R * 0.2)) * 0.45
        if z > R * 0.45:
            return -3
        d = abs(x - math.sin(z / 6))
        if d < breite:
            bank = abs(x - 0.5) < breite * 0.25 and z > R * 0.05
            return 0 if bank else -2
        return 1 + rn(x, 2, z) * (2 + s)

    hs = landschaft(w, R, hf, wy=0)
    rng = w.rng
    for (x, z), h in hs.items():
        if h == 0:
            w.setze(x, 0, z, w.b("sand"))
            w.bloecke.pop((x, 1, z), None)
            if rng.random() < 0.03:
                w.setze(x, 1, z, w.b("dead_brain_coral_fan", waterlogged=False))
        elif h < 0 and rng.random() < 0.06:
            w.setze(x, h + 1, z, w.b("seagrass"))
        elif h >= 1 and z > -R * 0.2 and rng.random() < 0.15:
            w.setze(x, h, z, w.b("sand"))
            w.setze(x, h + 1, z, w.b("dead_bush") if rng.random() < 0.3 else w.b("grass"))
    return w


def moosbach(seed, g=1):
    """Moosbach: ein schmaler Waldbach plätschert über moosüberwachsene Steine und kleine Stufen, gesäumt von Farnen,
    Moospolstern und alten Fichten mit freiliegenden Wurzeln."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    rn = Rauschen(w, 4)

    def hf(x, z):
        bach = abs(x - math.sin(z / 3) * 2) < 1.0 + 0.3 * s
        return (-z * 0.18 + 2) - (1 if bach else -rn(x, 2, z) * 1.5)

    hs = landschaft(w, R, hf, gras_deko=0.0)
    rng = w.rng
    for (x, z), h in hs.items():
        bach = abs(x - math.sin(z / 3) * 2) < 1.0 + 0.3 * s
        if bach:
            w.setze(x, h, z, w.b("water", level=0))
            w.setze(x, h - 1, z, w.b("mossy_cobblestone"))
        else:
            w.setze(x, h, z, w.b("moss_block") if rn(x, 6, z) < 0.6 else w.b("podzol", snowy=False))
            if rng.random() < 0.15:
                w.setze(x, h + 1, z, w.b("fern") if rng.random() < 0.6 else w.b("moss_carpet"))
            elif rng.random() < 0.03:
                kugel(w, x, h + 0.5, z, 0.9, w.b("mossy_cobblestone"))
    baeume(w, hs, int(4 + 3 * s), seed, art="fichte", frei=lambda x, z: abs(x - math.sin(z / 3) * 2) < 3)
    return w


def dolinenfall(seed, g=2):
    """Dolinenfall: in eine kreisrunde, tiefe Doline stürzt ein Bach von der Kante als Wasserfall hinab; die Wände
    sind von Ranken und Farnen überwuchert, unten liegt ein grünes Becken mit Geröll."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    rd = R * 0.4
    T = int(8 * s + 6)

    def hf(x, z):
        d = math.hypot(x, z)
        if d < rd + rn(x, 1, z) * 1.5:
            return -T
        if abs(x) < 1.5 and z < -rd:
            return 1
        return 2 + rn(x, 2, z) * 1.5

    hs = landschaft(w, R, hf, fels_steil=2)
    for (x, z), h in hs.items():
        if h == -T:
            for y in range(-T, -T + 3):
                w.setze(x, y, z, w.b("water", level=0))
            w.setze(x, -T - 1, z, w.b("gravel"))
        if abs(x) < 1.5 and z < -rd + 1 and h == 1:
            w.setze(x, 1, z, w.b("water", level=0))
    zf = -round(rd)
    for y in range(-T + 2, 2):
        for x in (-1, 0, 1):
            w.setze(x, y, zf, w.b("water", level=0))
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if -T < y < 0 and math.hypot(x, z) > rd - 1 and rng.random() < 0.08:
            for dx, dz, f in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
                if w.frei(x + dx, y, z + dz) and math.hypot(x + dx, z + dz) < rd:
                    w.setze(x + dx, y, z + dz, w.b("vine", **{"north": f == "south", "south": f == "north",
                                                             "east": f == "west", "west": f == "east",
                                                             "up": False}), False)
                    break
    baeume(w, hs, int(4 + 3 * s), seed, art="laub", frei=lambda x, z: math.hypot(x, z) < rd + 2)
    return w


def landzunge(seed, g=1):
    """Landzunge: ein schmaler, felsiger Finger Land ragt weit in einen See hinaus, gesäumt von Kieselstrand; an
    seiner Spitze steht eine einzelne, windschiefe Kiefer neben einem Findling."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    rn = Rauschen(w, 4)

    def hf(x, z):
        if z < -R * 0.6:
            return 2 + rn(x, 2, z) * 2
        b = (1.5 + s) * (1 - (z + R * 0.6) / (R * 1.5)) + rn(x, 3, z) * 1.2
        if abs(x - math.sin(z / 5) * 2) < b:
            return 1 + rn(x, 4, z)
        return -3

    hs = landschaft(w, R, hf, wy=0, sand=False)
    rng = w.rng
    for (x, z), h in hs.items():
        if h in (0, 1) and any(hs.get((x + dx, z + dz), 0) < 0 for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            w.setze(x, h, z, w.b("gravel") if rng.random() < 0.6 else w.b("cobblestone"))
    tip = max((z for (x, z), h in hs.items() if h >= 1 and abs(x) < 3), default=0)
    x = round(math.sin(tip / 5) * 2)
    einfuegen(w, wald2.kiefer(seed, H=int(7 + 2 * s)), x, hs.get((x, tip - 1), 1) + 1, tip - 1)
    kugel(w, x + 1.5, hs.get((x, tip - 2), 1) + 1, tip - 2, 1.2, w.b("mossy_cobblestone"))
    baeume(w, hs, int(3 + 2 * s), seed, art="fichte", wy=1, frei=lambda xx, z: z > -R * 0.5)
    return w


def umlaufberg(seed, g=2):
    """Umlaufberg: ein Fluss umfließt in einer fast geschlossenen Schleife einen bewaldeten Hügel, der nur über einen
    schmalen Hals mit dem Hang verbunden ist; steile Prallhänge und flache Gleithänge."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 5)
    rl = R * 0.45
    bw = 1.5 + 0.6 * s
    Hh = 4 * s + 4

    def hf(x, z):
        d = math.hypot(x, z)
        a = math.atan2(z, x)
        hals = abs(math.atan2(math.sin(a + math.pi / 2), math.cos(a + math.pi / 2))) < 0.35
        if abs(d - rl) < bw and not hals:
            return -2
        if d < rl - bw:
            return Hh * (1 - d / rl) + 1 + rn(x, 2, z)
        return 1 + (d - rl) * 0.4 + rn(x, 3, z) * 1.5

    hs = landschaft(w, R, hf, wy=0)
    baeume(w, hs, int(6 + 5 * s), seed, art="laub", wy=0)
    return w


def schleusentreppe(seed, g=2):
    """Schleusentreppe: ein gemauerter Kanal steigt in drei Schleusenkammern einen Hang hinab, jede mit hölzernen
    Stemmtoren und Ausgleichsbecken; daneben ein Treidelpfad und das Häuschen des Schleusenwärters."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 5)
    n = 3
    st = 3

    def ebene(z):
        return max(0, min(n - 1, int((-z + R) / (2 * R / n))))

    def hf(x, z):
        return ebene(z) * st + 2 + rn(x, 2, z)

    hs = landschaft(w, R, hf)
    stein = M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 1)])
    B = int(2 + 0.6 * s)
    for (x, z), h in hs.items():
        if abs(x) <= B + 1:
            k = ebene(z)
            wy = k * st + 1
            for y in range(wy - 3, wy + 3):
                w.bloecke.pop((x, y, z), None)
            if abs(x) <= B:
                for y in range(wy - 2, wy + 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, wy - 3, z, stein(x, 0, z))
            else:
                for y in range(wy - 3, wy + 2):
                    w.setze(x, y, z, stein(x, y, z))
            if abs(x) == B + 1:
                w.setze(x + (1 if x > 0 else -1), wy + 1, z, w.b("gravel"))
    for k in range(1, n):
        zb = round(R - k * 2 * R / n)
        wy_hi = k * st + 1
        for x in range(-B, B + 1):
            for y in range(wy_hi - st - 2, wy_hi + 2):
                w.setze(x, y, zb, w.b("spruce_planks") if y <= wy_hi else w.b("spruce_fence"))
            w.setze(x, wy_hi + 1, zb - 1, w.b("spruce_slab", type="bottom", waterlogged=False))
    hx = B + 5
    haus(w, hx, 0, 5, 4, hoehe(w, hx, 0, 30) + 1, M(w, [("bricks", 2), ("stone_bricks", 1)]), holz="spruce", H=3,
         dach=("mcw:red_terracotta", "brick"), tuer_s="west")
    return w


def stausee(seed, g=2):
    """Stausee: eine geschwungene Staumauer aus Stein riegelt ein Tal ab; dahinter liegt ein hoher, blauer See, davor
    stürzt Wasser aus einem Überlauf in das tiefe Flussbett, ein Weg führt über die Mauerkrone."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 5)
    H = int(8 * s + 6)
    zm = int(R * 0.1)

    def hf(x, z):
        tal = abs(x) < R * 0.35 + (-z) * 0.3
        if z < zm:
            return (H - 4 if tal else H + 2 + rn(x, 2, z) * 2)
        return (-1 if abs(x) < 2 + s else 1 + abs(x) * 0.3 + rn(x, 3, z) * 1.5)

    hs = landschaft(w, R, hf, wy=None)
    for (x, z), h in hs.items():
        if z < zm and h < H - 1:
            for y in range(h + 1, H):
                w.setze(x, y, z, w.b("water", level=0))
        if z >= zm and h < 0:
            w.setze(x, 0, z, w.b("water", level=0))
    st = M(w, [("stone_bricks", 3), ("polished_andesite", 1), ("cracked_stone_bricks", 0.5)])
    for x in range(-R, R + 1):
        zc = zm + round((x / R) ** 2 * 3)
        for dz in range(3):
            for y in range(-1, H + 1):
                if (x, zc + dz) in hs:
                    w.setze(x, y, zc + dz, st(x, y, zc + dz))
        if (x, zc) in hs:
            w.setze(x, H + 1, zc, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                      west="none", waterlogged=False))
            w.setze(x, H + 1, zc + 2, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                          west="none", waterlogged=False))
    for x in range(-1, 2):
        for y in range(0, H):
            w.setze(x, y, zm + 3, w.b("water", level=0))
        w.setze(x, H - 1, zm + 1, w.b("water", level=0))
        w.setze(x, H - 1, zm + 2, w.b("water", level=0))
        w.setze(x, H - 1, zm, w.b("water", level=0))
    return w


def eisschollensee(seed, g=2):
    """Eisschollensee: ein See im späten Winter, auf dem zerbrochene Eisschollen treiben, dazwischen dunkles Wasser;
    verschneite Ufer, Fichten und ein Steg, an dem sich Eis aufgeschoben hat."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 5)
    rs = R * 0.7

    def hf(x, z):
        d = math.hypot(x, z)
        return -3 if d < rs + rn(x, 1, z) * 2 else 1 + (d - rs) * 0.4 + rn(x, 2, z) * 1.5

    hs = landschaft(w, R, hf, wy=0, schnee=True, sand=False)
    rs2 = Rauschen(w, 2.2)
    for (x, z), h in hs.items():
        if h < 0 and rs2(x, 3, z) > 0.45:
            w.setze(x, 0, z, w.b("ice") if rs2(x, 4, z) < 0.7 else w.b("packed_ice"))
            if rs2(x, 5, z) > 0.85:
                w.setze(x, 1, z, w.b("snow", layers=1))
    for z in range(int(rs) - 4, int(R * 0.95)):
        for x in (0, 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
    for x in range(-1, 3):
        w.setze(x, 1, int(rs) - 5, w.b("packed_ice"))
        w.setze(x, 2, int(rs) - 5, w.b("ice")) if x % 2 else None
    baeume(w, hs, int(5 + 4 * s), seed, art="fichte", wy=0)
    return w


GEWAESSER3 = {
    "flusstor": ("Flusstor", flusstor),
    "maeanderschleife": ("Mäanderschleife mit Altarm", maeanderschleife),
    "haengetalfall": ("Hängetal-Fall", haengetalfall),
    "gefrorener_fall": ("Gefrorener Wasserfall", gefrorener_fall),
    "quelltopf": ("Quelltopf", quelltopf),
    "gletschertoepfe": ("Gletschertöpfe", gletschertoepfe),
    "klamm": ("Klamm mit Steig", klamm),
    "schaereninseln": ("Schäreninseln", schaereninseln),
    "wasserstrudel": ("Wasserstrudel", wasserstrudel),
    "furt": ("Furt mit Trittsteinen", furt),
    "weidenufer": ("Weidenufer", weidenufer),
    "seenkette": ("Seenkette", seenkette),
    "flussmuendung": ("Flussmündung mit Sandbank", flussmuendung),
    "moosbach": ("Moosbach", moosbach),
    "dolinenfall": ("Dolinenfall", dolinenfall),
    "landzunge": ("Landzunge", landzunge),
    "umlaufberg": ("Umlaufberg", umlaufberg),
    "schleusentreppe": ("Schleusentreppe", schleusentreppe),
    "stausee": ("Stausee", stausee),
    "eisschollensee": ("Eisschollensee", eisschollensee),
}

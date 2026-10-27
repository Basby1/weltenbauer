"""Antike Monumente – Paket: Kolosseum, Tempel, Triumphbogen, Aquädukt, Pyramide, Leuchtturm, Pantheon,
Forum-Ruinen, Theater. Größen 0 klein · 1 mittel · 2 riesig · 3 gigantisch; Stil 1 prächtig erhalten,
Stil 2 verwitterte Ruine (wo es passt)."""

from __future__ import annotations

import math

import numpy as np

from lib import Verlauf, Welt, ueberwuchern
from skulptur import kreisrand, laterne, platte, scheibe, treppe, verbinde, zur_mitte

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _marmor(w, ruine):
    if ruine:
        return Verlauf(w, "Travertin", ["mossy_cobblestone", "sandstone", "cut_sandstone", "smooth_sandstone",
                                        "end_stone"])
    return Verlauf(w, "Marmor", ["polished_diorite", "calcite", "quartz_bricks", "smooth_quartz", "quartz_block"])


def saeule(w, x, z, y0, h, r, schaft, kapitell, basis, ruine=False):
    """Kannelierte Säule: Basis, Schaft (Rundung je nach Radius), Kapitell. Ruine: abgebrochen."""
    if ruine and w.rng.random() < 0.45:
        h = max(1, int(h * (0.25 + 0.6 * w.rng.random())))
        kap_ = False
    else:
        kap_ = True
    zellen = scheibe(r) if r >= 1 else [(0, 0)]
    for dx, dz in scheibe(r + 1) if r >= 1 else [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
        w.setze(x + dx, y0, z + dz, basis)
    for y in range(y0 + 1, y0 + h):
        for dx, dz in zellen:
            w.setze(x + dx, y, z + dz, schaft(x + dx, y, z + dz))
    if kap_:
        for dx, dz in scheibe(r + 1) if r >= 1 else [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            w.setze(x + dx, y0 + h, z + dz, kapitell)
    return y0 + h


# ============================================================================ Kolosseum

def kolosseum(seed, g=2):
    """Elliptisches Amphitheater: drei Arkadengeschosse mit vorgeblendeten Säulen und eine Attika,
    Ränge, die zur Sandarena abfallen, freiliegende Kammern unter der Arena. Stil 2: die berühmte Ruine
    mit eingestürztem Außenring."""
    w = _welt(seed)
    u = U[g]
    ruine = _stil(seed) == 1
    stein = _marmor(w, ruine)
    A, B = 24 * u + 9, 20 * u + 7.5
    tier = _r(5 * u, 4)
    H = 3 * tier + _r(3.5 * u, 3)
    ring = 2.2
    sitz_tief = 0.55
    n_bogen = int(2 * math.pi * (A + B) / 2 / max(3, 3.4 * u))
    sand, kammer = w.b("sand"), w.b("stone_bricks")
    for x in range(-int(A) - 1, int(A) + 2):
        for z in range(-int(B) - 1, int(B) + 2):
            e = math.sqrt((x / A) ** 2 + (z / B) ** 2)
            if e > 1:
                continue
            d = (1 - e) * (A + B) / 2                       # Abstand von der Außenkante in Blöcken
            phi = math.atan2(z / B, x / A)
            f = (phi / (2 * math.pi) * n_bogen) % 1
            if ruine:
                einsturz = -0.6 < phi < 0.9
                hmax = H if not einsturz else int(tier * (1.3 + 0.8 * math.sin(phi * 9) ** 2))
            else:
                hmax = H
            if d < ring:                                   # Außenmauer mit Arkaden
                for y in range(0, min(hmax, H) + 1):
                    stufe = min(y // tier, 3)
                    yr = y - stufe * tier
                    offen = stufe < 3 and abs(f - 0.5) < 0.3 and 1 <= yr <= tier - 1 - 1.6 * ((f - 0.5) / 0.3) ** 2 \
                        and d > 0.3
                    if offen:
                        continue
                    if yr == 0 or (stufe == 3 and y == H):
                        blk = w.b("chiseled_quartz_block" if not ruine else "chiseled_sandstone")
                    elif abs(f - 0.5) > 0.42 and d < 0.9:
                        blk = w.b("quartz_pillar", axis="y") if not ruine else w.b("cut_sandstone")
                    elif stufe == 3 and yr == tier // 2 and abs(f - 0.5) < 0.12:
                        blk = w.b("light_blue_stained_glass") if not ruine else 0
                    else:
                        blk = stein(0.5 + 3 * y / H + w.rng.random() * 0.8, x, y, z)
                    if blk:
                        w.setze(x, y, z, blk)
            elif d < ring + 3:                               # Umgang mit Gewölbe
                w.setze(x, 0, z, stein(1, x, 0, z))
                if hmax >= tier:
                    w.setze(x, tier, z, stein(1.5, x, tier, z))
                    if hmax >= 2 * tier:
                        w.setze(x, 2 * tier, z, stein(2, x, 2 * tier, z))
            else:                                           # Ränge
                tiefe = (A + B) / 2 * (1 - sitz_tief)
                t = (d - ring - 3) / max(1.0, tiefe - ring - 3)
                if t < 1:
                    hs = int((2 * tier) * (1 - t))
                    hs = min(hs, hmax)
                    for y in range(0, hs + 1):
                        w.setze(x, y, z, stein(0.8 + 2.2 * y / H + w.rng.random() * 0.5, x, y, z))
                    if hs > 0 and int(d) % 2 == 0:
                        w.setze(x, hs, z, w.b("smooth_quartz_slab" if not ruine else "smooth_sandstone_slab",
                                              type="bottom", waterlogged=False))
                else:                                       # Arena
                    if ruine and e < 0.45 * (1 - sitz_tief) * 2:
                        if (x % 4 == 0 or z % 3 == 0):
                            for y in range(-3, 1):
                                w.setze(x, y, z, kammer)
                        else:
                            w.setze(x, -3, z, w.b("gravel"))
                    else:
                        w.setze(x, 0, z, sand)
    if ruine:
        for i in range(int(20 * u)):
            a = 0.15 + w.rng.random() * 0.6
            r = 1.05 + w.rng.random() * 0.25
            x, z = round(math.cos(a) * A * r), round(math.sin(a) * B * r)
            w.setze(x, 0, z, stein(1 + w.rng.random() * 2, x, 0, z))
            if w.rng.random() < 0.4:
                w.setze(x, 1, z, stein(2, x, 1, z))
        ueberwuchern(w, None, ranken=0.3, moos_oben=0.25, pflanzen=0.25, buesche=0.03, max_ranke=max(2, int(3 * u)))
    else:
        for i in range(0, 24):
            a = i * 2 * math.pi / 24
            x, z = round(math.cos(a) * (A - 1)), round(math.sin(a) * (B - 1))
            for y in range(H + 1, H + 1 + _r(3 * u, 2)):
                w.setze(x, y, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
            w.setze(x, H + 1 + _r(3 * u, 2), z, w.b("red_wool" if i % 2 else "yellow_wool"))
    return w


# ============================================================================ Tempel

def tempel(seed, g=1):
    """Griechischer Ringhallentempel: dreistufiger Unterbau, umlaufende Säulen mit Kapitellen, Gebälk mit
    Triglyphenfries, Giebeldreiecke, Cella mit Tor und Feuerschalen. Stil 2: verwitterte Ruine."""
    w = _welt(seed)
    u = U[g]
    ruine = _stil(seed) == 1
    stein = _marmor(w, ruine)
    sp = _r(3 * u, 2)
    nx, nz = 6, 11 if u >= 1 else 8
    bx, bz = (nx - 1) * sp // 2, (nz - 1) * sp // 2
    stufen = 3
    hs = _r(10 * u, 6)
    r = 0 if u < 1.5 else 1
    for k in range(stufen):
        hx, hz = bx + 2 + stufen - k, bz + 2 + stufen - k
        for x in range(-hx, hx + 1):
            for z in range(-hz, hz + 1):
                rand = abs(x) == hx or abs(z) == hz
                if rand and not (abs(x) == hx and abs(z) == hz):
                    blk = treppe(w, "smooth_quartz" if not ruine else "smooth_sandstone",
                                 ("east" if x < 0 else "west") if abs(x) == hx else ("south" if z < 0 else "north"))
                else:
                    blk = stein(1 + w.rng.random(), x, k, z)
                w.setze(x, k, z, blk)
    y0 = stufen
    schaft = lambda x, y, z: w.b("quartz_pillar", axis="y") if not ruine else stein(2 + w.rng.random(), x, y, z)  # noqa
    kapitell = w.b("chiseled_quartz_block" if not ruine else "chiseled_sandstone")
    basis = w.b("quartz_bricks" if not ruine else "cut_sandstone")
    for i in range(nx):
        for j in range(nz):
            if 0 < i < nx - 1 and 0 < j < nz - 1:
                continue
            saeule(w, -bx + i * sp, -bz + j * sp, y0, hs, r, schaft, kapitell, basis, ruine)
    # Cella
    cx, cz = bx - sp, bz - sp
    for x in range(-cx, cx + 1):
        for z in range(-cz, cz + 1):
            if abs(x) == cx or abs(z) == cz:
                for y in range(y0, y0 + hs):
                    if z == cz and abs(x) <= 1 and y < y0 + _r(5 * u, 3):
                        continue
                    if ruine and y > y0 + hs * (0.4 + 0.5 * math.sin(x * 0.7 + z * 0.3) ** 2):
                        continue
                    w.setze(x, y, z, stein(1.5 + w.rng.random(), x, y, z))
    for s in (-1, 1):
        w.setze(s * 2, y0, cz + 2, w.b("campfire", lit=not ruine, signal_fire=False, facing="north",
                                       waterlogged=False))
    # Gebälk, Fries, Giebel
    if not ruine or True:
        ye = y0 + hs + 1
        for x in range(-bx - 1, bx + 2):
            for z in range(-bz - 1, bz + 2):
                rand = abs(x) == bx + 1 or abs(z) == bz + 1
                if ruine and math.sin(x * 0.5) * math.cos(z * 0.3) > 0.2:
                    continue
                w.setze(x, ye, z, stein(3, x, ye, z))
                if rand:
                    w.setze(x, ye + 1, z, w.b("chiseled_quartz_block" if not ruine else "chiseled_sandstone")
                            if (x + z) % 3 == 0 else w.b("blue_terracotta" if not ruine else "cut_sandstone"))
                    w.setze(x, ye + 2, z, w.b("gold_block") if not ruine and (x + z) % 6 == 0 else stein(3, x, ye + 2, z))
        hg = bx + 2
        for k in range(hg):
            for x in range(-bx - 1 + k, bx + 2 - k):
                for z in range(-bz - 1, bz + 2):
                    if ruine and (z > bz * 0.2 or math.sin(x * 0.9 + z) > 0.4):
                        continue
                    rand = abs(x) >= bx + 1 - k - 0 and True
                    w.setze(x, ye + 3 + k, z, treppe(w, "smooth_quartz" if not ruine else "smooth_sandstone",
                                                     "east" if x < 0 else "west") if abs(x) == bx + 1 - k
                            else (w.b("quartz_bricks") if not ruine else stein(2.5, x, ye + 3 + k, z)))
        if not ruine:
            w.setze(0, ye + 3 + hg, -bz - 1, w.b("gold_block"))
            w.setze(0, ye + 3 + hg, bz + 1, w.b("gold_block"))
    if ruine:
        for i in range(int(8 * u) + 3):
            x = int((w.rng.random() - 0.5) * 2 * (bx + 6))
            z = int((w.rng.random() - 0.5) * 2 * (bz + 6))
            if abs(x) > bx + 3 or abs(z) > bz + 3:
                for k in range(_r(2 * u, 1) + 1):
                    w.setze(x + k, 0, z, w.b("quartz_pillar" if False else "cut_sandstone"))
        ueberwuchern(w, None, ranken=0.35, moos_oben=0.3, pflanzen=0.3, buesche=0.04)
    return w


# ============================================================================ Triumphbogen

def triumphbogen(seed, g=1):
    """Dreitoriger Triumphbogen: große Mittelöffnung, zwei Seitendurchgänge, vorgesetzte Säulen auf Sockeln,
    Reliefbänder, Attika mit goldener Inschrift und Bronzegruppe aus Kupfer obenauf."""
    w = _welt(seed)
    u = U[g]
    ruine = _stil(seed) == 1
    stein = _marmor(w, ruine)
    B, T, H = _r(11 * u, 7), _r(3 * u, 2), _r(14 * u, 9)
    wm, hm = _r(3 * u, 2), _r(9 * u, 6)
    ws, hsd = _r(1.6 * u, 1), _r(5.5 * u, 4)
    xs = _r(6.5 * u, 4)
    att = _r(3.5 * u, 3)
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            for y in range(0, H + att + 1):
                def bogen(xc, hw, hh):
                    dx = abs(x - xc)
                    if dx > hw:
                        return False
                    return y <= hh - hw + math.sqrt(max(0, hw * hw - dx * dx))
                if bogen(0, wm, hm) or bogen(-xs, ws, hsd) or bogen(xs, ws, hsd):
                    continue
                if ruine and y > H * (0.75 + 0.25 * math.sin(x * 0.6) ** 2) + (att if abs(x) < B * 0.3 else 0):
                    continue
                if y > H:
                    blk = w.b("gold_block") if not ruine and abs(z) == T and y == H + att // 2 + 1 and \
                        abs(x) < B - 2 and x % 2 == 0 else stein(3 + w.rng.random() * 0.5, x, y, z)
                elif y in (hm + 2, H) or (y == hsd + 2 and abs(x) > xs - ws - 1):
                    blk = w.b("chiseled_quartz_block" if not ruine else "chiseled_sandstone")
                else:
                    blk = stein(1 + 2.2 * y / H + w.rng.random() * 0.5, x, y, z)
                w.setze(x, y, z, blk)
    for xc in (-B + 1, -xs - ws - 2, xs + ws + 2, B - 1):
        for s in (-1, 1):
            z = s * (T + 1)
            for y in range(0, _r(2 * u, 2)):
                w.setze(xc, y, z, w.b("quartz_bricks" if not ruine else "cut_sandstone"))
            for y in range(_r(2 * u, 2), H):
                w.setze(xc, y, z, w.b("quartz_pillar", axis="y") if not ruine else stein(2, xc, y, z))
            w.setze(xc, H, z, w.b("chiseled_quartz_block" if not ruine else "chiseled_sandstone"))
    if not ruine:
        kup = Verlauf(w, "Bronze", ["waxed_oxidized_copper", "waxed_weathered_copper", "waxed_oxidized_cut_copper"])
        for x in range(-_r(3 * u, 2), _r(3 * u, 2) + 1):
            for y in range(H + att + 1, H + att + 1 + _r(3 * u, 2)):
                if (x + y) % 3 != 0 or y == H + att + 1:
                    w.setze(x, y, 0, kup(w.rng.random() * 3, x, y, 0))
    else:
        ueberwuchern(w, None, ranken=0.4, moos_oben=0.3, pflanzen=0.25, buesche=0.03)
    return w


# ============================================================================ Aquädukt

def aquaedukt(seed, g=1):
    """Mehrstöckiger Aquädukt: übereinandergestellte Bogenreihen, oben eine Rinne mit fließendem Wasser,
    an den Enden verschlossen. Stil 2: teilweise eingestürzt, überwuchert."""
    w = _welt(seed)
    u = U[g]
    ruine = _stil(seed) == 1
    stein = Verlauf(w, "Stein", ["mossy_stone_bricks", "stone_bricks", "cut_sandstone", "smooth_sandstone"]) if ruine \
        else Verlauf(w, "Stein", ["stone_bricks", "cut_sandstone", "smooth_sandstone", "sandstone"])
    L = _r(30 * u + 10, 16)
    stock = [2, 2, 3, 3][g]
    sp = _r(5 * u, 4)
    hb = _r(7 * u, 5)
    for s in range(stock):
        y0 = s * hb
        sp_s = sp if s == 0 else max(3, sp // (1 if s == 1 else 2) if s > 1 else sp)
        for x in range(-L, L + 1):
            pos = (x + L) % sp_s
            hw = (sp_s - 2) / 2
            dx = abs(pos - sp_s / 2)
            for y in range(y0, y0 + hb):
                yr = y - y0
                offen = dx < hw and yr < hb - 1 - hw + math.sqrt(max(0.0, hw * hw - dx * dx)) - (0 if s else 0)
                if offen:
                    continue
                if ruine and abs(x - L * 0.35) < L * 0.15 and y > hb * (stock - 1) * 0.6:
                    continue
                for z in (-1, 0, 1) if s == 0 else (0,) if u < 1 else (-1, 0, 1):
                    w.setze(x, y, z, stein(1 + 2 * y / (stock * hb) + w.rng.random() * 0.5, x, y, z))
    yt = stock * hb
    for x in range(-L, L + 1):
        if ruine and abs(x - L * 0.35) < L * 0.15:
            continue
        for z in (-1, 0, 1):
            w.setze(x, yt, z, stein(3, x, yt, z))
        for z in (-1, 1):
            w.setze(x, yt + 1, z, stein(3, x, yt + 1, z))
        w.setze(x, yt + 1, 0, w.b("water", level=0) if not (abs(x) == L) else stein(3, x, yt + 1, 0))
    if ruine:
        for x in (round(L * 0.2), round(L * 0.5)):
            w.setze(x, yt + 1, 0, stein(3, x, yt + 1, 0))
        ueberwuchern(w, None, ranken=0.5, moos_oben=0.4, pflanzen=0.3, buesche=0.05, max_ranke=max(2, int(4 * u)))
    return w


# ============================================================================ Pyramide

def pyramide(seed, g=2):
    """Stil 1: glatte Sandsteinpyramide mit Goldspitze, Eingang und Sphinx-Wächtersteinen.
    Stil 2: Stufenpyramide mit Freitreppe und Tempelhaus auf der Spitze."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        stein = Verlauf(w, "Sandstein", ["sandstone", "cut_sandstone", "smooth_sandstone", "end_stone"])
        S_ = _r(16 * u + 5, 8)
        for y in range(int(S_ * 1.3) + 1):
            h = S_ - int(y / 1.3)
            for x in range(-h, h + 1):
                for z in range(-h, h + 1):
                    if max(abs(x), abs(z)) == h or y % 4 == 0 or h < 3:
                        w.setze(x, y, z, w.b("gold_block") if h < _r(1.5 * u, 1) + 1 else
                                stein(0.6 + 3 * y / (S_ * 1.3) + w.rng.random() * 0.4, x, y, z))
        for y in range(1, _r(3 * u, 3)):
            for x in (-1, 0, 1):
                w.setze(x, y, S_ - y, 0)
                w.setze(x, y, S_ - y - 1, 0)
        w.bloecke = {p: b for p, b in w.bloecke.items() if b != 0}
        for x in range(-2, 3):
            w.setze(x, _r(3 * u, 3), S_ - _r(3 * u, 3) + 1, w.b("chiseled_sandstone"))
        for s in (-1, 1):
            for y in range(0, _r(3 * u, 2)):
                w.setze(s * 4, y, S_ + 3, w.b("chiseled_sandstone" if y else "cut_sandstone"))
            w.setze(s * 4, _r(3 * u, 2), S_ + 3, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                     waterlogged=False))
    else:
        stein = Verlauf(w, "Dschungelstein", ["mossy_cobblestone", "mossy_stone_bricks", "stone_bricks", "andesite"])
        stufen = [5, 6, 8, 9][g]
        hst = _r(2.5 * u, 2)
        S_ = stufen * _r(2 * u, 2) + 4
        y = 0
        for k in range(stufen):
            h = S_ - k * _r(2 * u, 2)
            for yy in range(y, y + hst):
                for x in range(-h, h + 1):
                    for z in range(-h, h + 1):
                        w.setze(x, yy, z, stein(0.6 + 3 * yy / (stufen * hst) + w.rng.random() * 0.5, x, yy, z)
                                if max(abs(x), abs(z)) >= h - 1 or yy == y + hst - 1 else
                                w.b("stone_bricks"))
            y += hst
        for yy in range(0, y):
            for x in range(-2, 3):
                z = S_ - int(yy * (S_ - (S_ - stufen * _r(2 * u, 2))) / max(1, y)) + 1
                w.setze(x, yy, z, w.b("stone_brick_stairs", facing="north", half="bottom", shape="straight",
                                      waterlogged=False) if abs(x) < 2 else w.b("chiseled_stone_bricks"))
                for zz in range(z + 1, S_ + 2):
                    if yy < y and w.frei(x, yy, zz):
                        pass
        ht = S_ - stufen * _r(2 * u, 2) - 1
        for x in range(-ht, ht + 1):
            for z in range(-ht, ht + 1):
                for yy in range(y, y + _r(4 * u, 3)):
                    if max(abs(x), abs(z)) == ht and not (z == ht and abs(x) <= 1 and yy < y + 2):
                        w.setze(x, yy, z, w.b("chiseled_stone_bricks" if (x + yy) % 3 == 0 else "stone_bricks"))
                w.setze(x, y + _r(4 * u, 3), z, w.b("mossy_stone_bricks"))
        w.setze(0, y, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
        ueberwuchern(w, None, ranken=0.35, moos_oben=0.3, pflanzen=0.2, buesche=0.05)
    return w


# ============================================================================ Leuchtturm

def leuchtturm(seed, g=2):
    """Antiker Leuchtturm in drei Stufen: quadratischer Sockel mit Fenstern, achteckiger Mittelturm,
    runde Laterne mit großem Feuer, Bronzestatue mit Fackel obenauf; Ecktritonen aus Kupfer."""
    w = _welt(seed)
    u = U[g]
    stein = _marmor(w, False) if _stil(seed) == 0 else Verlauf(w, "Kalkstein", ["sandstone", "cut_sandstone",
                                                                                 "smooth_sandstone", "end_stone"])
    a = _r(5 * u + 2, 4)
    h1, h2, h3 = _r(18 * u, 10), _r(12 * u, 7), _r(6 * u, 4)
    for y in range(h1):
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                if max(abs(x), abs(z)) == a or y == 0:
                    fenster = y % 4 == 2 and (x % 3 == 0 if abs(z) == a else z % 3 == 0) and max(abs(x), abs(z)) == a \
                        and min(abs(x), abs(z)) < a - 1
                    w.setze(x, y, z, w.b("yellow_stained_glass") if fenster else stein(0.5 + 2 * y / h1, x, y, z))
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            w.setze(x, h1, z, stein(2.5, x, h1, z))
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            w.setze(s1 * a, h1 + 1, s2 * a, w.b("waxed_oxidized_copper"))
            w.setze(s1 * a, h1 + 2, s2 * a, w.b("waxed_oxidized_cut_copper"))
    b = max(2, int(a * 0.62))
    for y in range(h1 + 1, h1 + 1 + h2):
        for x in range(-b, b + 1):
            for z in range(-b, b + 1):
                if abs(x) + abs(z) <= b * 1.42 and (max(abs(x), abs(z)) >= b or abs(x) + abs(z) >= int(b * 1.42)):
                    w.setze(x, y, z, stein(1.5 + 1.5 * (y - h1) / h2, x, y, z))
    y3 = h1 + 1 + h2
    c = max(1.5, a * 0.38)
    for x, z in scheibe(c + 1):
        w.setze(x, y3, z, stein(3, x, y3, z))
    for i, (x, z) in enumerate(kreisrand(c)):
        for y in range(y3 + 1, y3 + h3):
            if i % 2 == 0:
                w.setze(x, y, z, w.b("quartz_pillar", axis="y") if _stil(seed) == 0 else w.b("cut_sandstone"))
    for x, z in scheibe(max(0.6, c - 1.2)):
        w.setze(x, y3 + 1, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    for x, z in scheibe(c + 0.6):
        w.setze(x, y3 + h3, z, w.b("waxed_oxidized_cut_copper"))
    for y in range(y3 + h3 + 1, y3 + h3 + _r(4 * u, 3)):
        w.setze(0, y, 0, w.b("waxed_oxidized_copper"))
    w.setze(0, y3 + h3 + _r(4 * u, 3), 1, w.b("waxed_oxidized_copper"))
    w.setze(0, y3 + h3 + _r(4 * u, 3) + 1, 1, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                  waterlogged=False))
    return w


# ============================================================================ Pantheon

def pantheon(seed, g=2):
    """Rundtempel mit gewaltiger Kuppel und Lichtauge, davor eine Säulenvorhalle mit Giebel."""
    w = _welt(seed)
    u = U[g]
    stein = _marmor(w, False) if _stil(seed) == 0 else Verlauf(w, "Ziegel", ["bricks", "mud_bricks", "terracotta",
                                                                              "smooth_sandstone"])
    kuppel = Verlauf(w, "Kuppel", ["waxed_oxidized_cut_copper", "waxed_oxidized_copper", "waxed_weathered_copper"]) \
        if _stil(seed) == 0 else Verlauf(w, "Kuppel", ["stone", "andesite", "smooth_stone", "calcite"])
    R = 11 * u + 4
    hw = _r(R * 0.9, 5)
    for i, (x, z) in enumerate(kreisrand(R)):
        for y in range(0, hw):
            w.setze(x, y, z, stein(0.6 + 2 * y / hw + w.rng.random() * 0.4, x, y, z))
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("polished_granite" if (x + z) % 4 == 0 else "smooth_quartz"))
    n = int(R) + 1
    for x in range(-n, n + 1):
        for z in range(-n, n + 1):
            for yy in range(0, int(R) + 2):
                d = math.sqrt(x * x + z * z + (yy * 1.05) ** 2)
                if R - 1.6 < d <= R + 0.4 and math.hypot(x, z) > max(1.2, R * 0.13):
                    w.setze(x, hw + yy, z, kuppel(3 * yy / R + w.rng.random() * 0.5, x, hw + yy, z))
    for x, z in kreisrand(max(1.2, R * 0.13) + 0.6):
        w.setze(x, hw + int(R * 0.93), z, w.b("gold_block"))
    # Vorhalle
    tz0 = int(R) - 1
    tz1 = tz0 + _r(7 * u, 5)
    bx = _r(R * 0.75, 4)
    hs = int(hw * 0.85)
    for x in range(-bx, bx + 1):
        for z in range(tz0, tz1 + 1):
            w.setze(x, 0, z, stein(1, x, 0, z))
    sp = max(2, (2 * bx) // 7)
    for x in range(-bx, bx + 1, sp):
        for z in (tz1 - 1, tz1 - 1 - _r(3 * u, 2)):
            saeule(w, x, z, 0, hs, 0 if u < 1.5 else 1, lambda a, b, c: w.b("quartz_pillar", axis="y"),
                   w.b("chiseled_quartz_block"), w.b("quartz_bricks"))
    for k in range(bx + 2):
        for x in range(-bx - 1 + k, bx + 2 - k):
            for z in range(tz0, tz1 + 1):
                w.setze(x, hs + 1 + k, z, treppe(w, "smooth_quartz", "east" if x < 0 else "west") if abs(x) == bx + 1 - k
                        else stein(2.5, x, hs + 1 + k, z))
    for x in range(-bx - 1, bx + 2):
        w.setze(x, hs + 1, tz1 + 1, w.b("gold_block") if x % 3 == 0 else w.b("chiseled_quartz_block"))
    for x in (-1, 0, 1):
        for y in range(1, _r(6 * u, 4)):
            w.setze(x, y, int(R), 0)
    w.bloecke = {p: b for p, b in w.bloecke.items() if b != 0}
    return w


# ============================================================================ Forum-Ruinen

def forum(seed, g=1):
    """Ruinenfeld eines Forums: Säulenreihen mit Gebälkresten, umgestürzte Säulentrommeln, Podeste,
    Statuenstümpfe, Pflaster mit Gras dazwischen."""
    w = _welt(seed)
    u = U[g]
    stein = _marmor(w, _stil(seed) == 1)
    W, T = _r(18 * u + 6, 10), _r(12 * u + 4, 7)
    for x in range(-W, W + 1):
        for z in range(-T, T + 1):
            if w.rng.random() < 0.82:
                w.setze(x, 0, z, stein(0.6 + w.rng.random() * 1.5, x, 0, z))
            else:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
    sp = _r(3 * u, 2)
    hs = _r(9 * u, 6)
    for reihe, z in enumerate((-T + 3, T - 3)):
        tops = []
        for x in range(-W + 2, W - 1, sp):
            schaft = lambda a, b, c: w.b("quartz_pillar", axis="y") if _stil(seed) == 0 else stein(2.5, a, b, c)  # noqa
            top = saeule(w, x, z, 1, hs, 0 if u < 1.5 else 1, schaft, w.b("chiseled_quartz_block" if _stil(seed) == 0
                                                                          else "chiseled_sandstone"),
                         stein(1, x, 1, z), ruine=True)
            tops.append((x, top))
        for (x1, t1), (x2, t2) in zip(tops, tops[1:]):
            if t1 == 1 + hs and t2 == 1 + hs:
                for x in range(x1, x2 + 1):
                    w.setze(x, t1 + 1, z, stein(3, x, t1 + 1, z))
    for i in range(int(4 * u) + 3):
        x = int((w.rng.random() - 0.5) * 2 * (W - 3))
        z = int((w.rng.random() - 0.5) * T)
        lang = _r(3 * u, 2) + 1
        for k in range(lang):
            w.setze(x + k, 1, z, w.b("quartz_pillar", axis="x") if _stil(seed) == 0 else stein(2, x + k, 1, z))
    for x in (-W // 2, W // 2):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                w.setze(x + dx, 1, dz, stein(1.5, x + dx, 1, dz))
                w.setze(x + dx, 2, dz, stein(2.5, x + dx, 2, dz))
        for y in range(3, 3 + _r(2.5 * u, 2)):
            w.setze(x, y, 0, stein(3, x, y, 0))
    ueberwuchern(w, None, ranken=0.35, moos_oben=0.3, pflanzen=0.3, buesche=0.05)
    return w


# ============================================================================ Theater

def theater(seed, g=2):
    """Halbrundes Theater: steigende Sitzreihen mit Treppengängen, Orchestra-Rund, Bühnenhaus mit
    Säulenfront und Statuennischen."""
    w = _welt(seed)
    u = U[g]
    stein = _marmor(w, _stil(seed) == 1)
    R = 16 * u + 6
    r0 = 4 * u + 2
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, 2):
            d = math.hypot(x, z)
            if d > R:
                continue
            if d < r0:
                w.setze(x, 0, z, w.b("smooth_quartz" if (x + z) % 2 else "polished_diorite"))
                continue
            h = int((d - r0) * 0.6) + 1
            a = math.atan2(-z, x)
            gang = any(abs(a - b) < 0.05 for b in (0.6, 1.2, 1.9, 2.5))
            for y in range(0, h + 1):
                w.setze(x, y, z, stein(0.6 + 2.5 * y / (R * 0.6) + w.rng.random() * 0.4, x, y, z))
            if gang:
                w.setze(x, h + 1, z, treppe(w, "smooth_quartz" if _stil(seed) == 0 else "smooth_sandstone",
                                            zur_mitte(-x, -z)))
    # Bühnenhaus
    bx = int(R * 0.75)
    hb = _r(8 * u, 5)
    for x in range(-bx, bx + 1):
        for z in range(3, 3 + _r(3 * u, 2)):
            for y in range(0, hb):
                rueck = z == 3 + _r(3 * u, 2) - 1
                if rueck or y == 0 or y == hb - 1:
                    nische = rueck and x % _r(4 * u, 3) == 0 and 2 <= y <= hb - 3
                    w.setze(x, y, z, w.b("chiseled_quartz_block") if nische else stein(1.5 + 1.5 * y / hb, x, y, z))
    for x in range(-bx + 1, bx, _r(3 * u, 2)):
        saeule(w, x, 3, 0, hb - 1, 0, lambda a, b, c: w.b("quartz_pillar", axis="y") if _stil(seed) == 0 else
               stein(2.5, a, b, c), w.b("chiseled_quartz_block"), stein(1, x, 0, 3), ruine=_stil(seed) == 1)
    if _stil(seed) == 1:
        ueberwuchern(w, None, ranken=0.35, moos_oben=0.3, pflanzen=0.3, buesche=0.05)
    return w


ANTIKE = {
    "kolosseum": ("Kolosseum", kolosseum),
    "tempel": ("Tempel", tempel),
    "triumphbogen": ("Triumphbogen", triumphbogen),
    "aquaedukt": ("Aquädukt", aquaedukt),
    "pyramide": ("Pyramide", pyramide),
    "leuchtturm": ("Antiker Leuchtturm", leuchtturm),
    "pantheon": ("Rundtempel mit Kuppel", pantheon),
    "forum": ("Forum-Ruinen", forum),
    "theater": ("Theater", theater),
}

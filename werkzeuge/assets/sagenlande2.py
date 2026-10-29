"""Sagenlande II – zwanzig weitere Landschaftsszenen aus einer eigenen Sagenwelt: Mondseeturm, Steppenlager,
Passfeste, Moorwacht, Waldläuferlager, Brückenstadt über der Schlucht, Weidenfurt mit Mühle, Orakelgrotte,
Sturmgipfel-Ruine, Klippenfestung, Handelsposten, Drachenbrand-Dorf, Riesentreppe, Hochlandruine, Pfahldorf am See,
Fjord-Leuchtturm, Bergkloster, Mühlenhügel, Schäferhof und Wasserfall-Heiligtum."""

from __future__ import annotations

import math

import wald2
from feinbau import (Dachmat, Mix, balkon, fachwerk, fenster, kamin, kegeldach, kram, laterne, mauer, platte,
                     satteldach, stamm, treppe, tuer, zaun)
from flora import _neu
from gewaesser import Land
from himmelsstadt2 import eckturm, haus, rundturm
from lib import Rauschen, einfuegen

S = [0.6, 1.0, 1.6, 2.5]


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def land(w, g, f=None, k=1.0):
    s = S[g]
    R = int((16 * s + 8) * k)
    L = Land(w, R)
    rn = Rauschen(w, 9)
    f = f or (lambda x, z, h, R: 1 + 2.5 * rn(x, 0, z) * s)
    L.heben(lambda x, z, h: f(x, z, h, R))
    return L, R, s


def ebnen(L, cx, cz, rx, rz=None, y=None):
    rz = rz if rz is not None else rx
    zellen = [(x, z) for (x, z) in L.h if abs(x - cx) <= rx and abs(z - cz) <= rz]
    if not zellen:
        return 1
    if y is None:
        ys = sorted(L.h[p] for p in zellen)
        y = ys[len(ys) // 2]
    for p in zellen:
        L.h[p] = y
        L.wasser.pop(p, None)
    return y


def stein(w):
    return M(w, [("stone_bricks", 3), ("cobblestone", 1), ("mossy_stone_bricks", 1), ("andesite", 1)])


def ruine(w, anteil=0.4, ab_y=None, box=None):
    rng = w.rng
    for (x, y, z) in list(w.bloecke):
        if box and not (box[0] <= x <= box[1] and box[2] <= z <= box[3]):
            continue
        if ab_y is not None and y < ab_y:
            continue
        if rng.random() < anteil * min(1.0, (y - (ab_y or 0)) / 6 + 0.2):
            n = w.P.name(w.bloecke[(x, y, z)])
            if any(t in n for t in ("brick", "cobble", "planks", "log", "stairs", "slab", "terracotta", "tile",
                                    "glass", "door", "lantern", "fence", "andesite")):
                del w.bloecke[(x, y, z)]


def jurte(w, cx, y, cz, r, farbe="white_wool"):
    for yy in range(y, y + 3):
        for x in range(cx - r - 1, cx + r + 2):
            for z in range(cz - r - 1, cz + r + 2):
                d = math.hypot(x - cx, z - cz)
                if r - 0.8 < d <= r + 0.3:
                    band = yy == y + 1 and int(math.degrees(math.atan2(z - cz, x - cx))) % 40 < 12
                    w.setze(x, yy, z, w.b("red_wool" if band else farbe))
    for k in range(r + 1):
        rr = r + 0.4 - k
        for x in range(cx - r - 1, cx + r + 2):
            for z in range(cz - r - 1, cz + r + 2):
                d = math.hypot(x - cx, z - cz)
                if rr - 1 < d <= rr:
                    w.setze(x, y + 3 + k // 2, z, w.b("light_gray_wool" if k < r else "brown_wool"))
    w.setze(cx, y + 3 + r // 2, cz, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                         waterlogged=False))
    for yy in (y, y + 1):
        w.bloecke.pop((cx, yy, cz + r), None)
    w.setze(cx, y + 2, cz + r, w.b("red_wool"))


def windmuehle(w, cx, y, cz, H, fluegel_z=1):
    for yy in range(y, y + H):
        r = 3 - (yy - y) * 0.13
        for dx in range(-4, 5):
            for dz in range(-4, 5):
                d = math.hypot(dx, dz)
                if r - 1 < d <= r:
                    w.setze(cx + dx, yy, cz + dz, w.b("white_terracotta" if (yy - y) % 4 else "spruce_planks"))
    kegeldach(w, cx, cz, y + H, 2, Dachmat(w, ["spruce", "dark_oak"]), form="kegel", h=4)
    hz = cz + 3 * fluegel_z
    yh = y + H - 1
    for k in range(-6, 7):
        if k:
            w.setze(cx + k, yh, hz, w.b("dark_oak_log", axis="x"))
            w.setze(cx, yh + k, hz, w.b("dark_oak_log", axis="y"))
            if abs(k) > 1:
                w.setze(cx + k, yh + (1 if k > 0 else -1), hz, w.b("white_wool"))
                w.setze(cx + (-1 if k > 0 else 1), yh + k, hz, w.b("white_wool"))
    tuer(w, cx, y, cz + 3 if fluegel_z < 0 else cz - 3, "south" if fluegel_z < 0 else "north", holz="spruce")


def pfahlhaus(w, cx, cz, y_wasser, B=5, T=4, stil="fachwerk"):
    yb = y_wasser + 2
    for (x, z) in ((cx - B // 2, cz - T // 2), (cx + B // 2, cz - T // 2), (cx - B // 2, cz + T // 2),
                   (cx + B // 2, cz + T // 2)):
        for yy in range(y_wasser - 3, yb):
            w.setze(x, yy, z, stamm(w, "spruce", geschaelt=False))
    for x in range(cx - B // 2 - 1, cx + B // 2 + 2):
        for z in range(cz - T // 2 - 1, cz + T // 2 + 2):
            w.setze(x, yb - 1, z, w.b("spruce_planks"))
    return haus(w, cx, cz, B, T, yb + 2, stil, geschosse=1, tuer_s="south", schorn=False)


# ============================================================================ Szenen

def mondseeturm(seed, g=1):
    """Mondseeturm: ein schlanker weißer Turm mit blauem Helm steht auf einer Felsinsel in einem stillen See, ein
    steinerner Damm mit Laternen führt hinüber, Weiden am Ufer."""
    w = _neu(seed)
    L, R, s = land(w, g)
    L.see(0, 0, R * 0.6, 2, tiefe=3)
    ri = max(3, int(R * 0.18))
    for (x, z) in L.h:
        d = math.hypot(x, z)
        if d < ri:
            L.h[(x, z)] = 3 + int((ri - d) * 0.5)
            L.wasser.pop((x, z), None)
        if abs(x) <= 1 and z > 0 and (x, z) in L.wasser:
            L.h[(x, z)] = 2
            L.wasser.pop((x, z), None)
    y = ebnen(L, 0, 0, 3)
    L.bauen()
    rt = int(2 * s + 2)
    rundturm(w, 0, 0, y + 1, rt, int(12 * s + 8), M(w, [("calcite", 3), ("smooth_quartz", 1), ("diorite", 1)]),
             Dachmat(w, ["mcw:blue_terracotta", "mcw:light_blue_terracotta", "deepslate_tile"]), form="nadel")
    tuer(w, 0, y + 1, rt, "south", holz="birch")
    for z in range(rt + 2, int(R * 0.65), 4):
        laterne(w, 1, 4, z, 0) if False else w.setze(1, 3, z, w.b("lantern", hanging=False, waterlogged=False))
    L.bepflanzen(0.35, baeume=3 + 2 * g, arten=("weide", "birke"), seed=seed)
    return w


def steppenlager(seed, g=1):
    """Steppenlager: auf einer weiten Grasebene stehen runde Filzjurten mit roten Bändern um ein großes Lagerfeuer,
    dazu Pferdekoppeln, Wimpelstangen und Holzkarren."""
    w = _neu(seed)
    L, R, s = land(w, g, k=1.1)
    L.bauen()
    rng = w.rng
    n = 3 + g * 2
    for k in range(n):
        a = k / n * 6.283
        cx, cz = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        y = L.h.get((cx, cz), 1) + 1
        jurte(w, cx, y, cz, int(2 * s + 2), "white_wool" if k % 3 else "light_gray_wool")
    y0 = L.h.get((0, 0), 1)
    for (x, z) in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)):
        w.setze(x, y0 + 1, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)
                if (x, z) == (0, 0) else w.b("cobblestone_slab", type="bottom", waterlogged=False))
    kx, kz = round(R * 0.75), 0
    r = int(3 * s + 2)
    for x in range(kx - r, kx + r + 1):
        for z in range(kz - r, kz + r + 1):
            if (abs(x - kx) == r or abs(z - kz) == r) and (x, z) in L.h:
                w.setze(x, L.h[(x, z)] + 1, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                                   waterlogged=False))
    for k in range(4):
        a = rng.random() * 6.283
        x, z = round(math.cos(a) * R * 0.3), round(math.sin(a) * R * 0.3)
        y = L.h.get((x, z), 1)
        for yy in range(y + 1, y + 6):
            w.setze(x, yy, z, zaun(w, "spruce"))
        w.setze(x + 1, y + 5, z, w.b(["red_wool", "yellow_wool", "blue_wool", "white_wool"][k]))
    L.bepflanzen(0.5, baeume=1, arten=("busch",), seed=seed)
    return w


def passfeste(seed, g=1):
    """Passfeste: zwischen zwei steilen Bergflanken sperrt eine hohe Mauer mit Zinnen das Tal, in der Mitte ein
    Torhaus mit Fallgitter, auf den Flanken zwei Wachtürme."""
    w = _neu(seed)
    rn = Rauschen(w, 8)
    sg = S[g]
    L, R, s = land(w, g, lambda x, z, h, R: 1 + max(0, (abs(x) - 5 * sg) * 0.9) * (0.8 + 0.4 * rn(x, 0, z)))
    L.bauen(fels_ab=int(8 * s))
    st = stein(w)
    hm = int(5 * s + 4)
    for x in range(-R, R + 1):
        if (x, 0) not in L.h:
            continue
        yb = L.h[(x, 0)]
        for z in (-1, 0, 1):
            for y in range(yb, max(yb, int(hm + 2)) + 1):
                w.setze(x, y, z, st(x, y, z))
            if z != 0 and (x % 2 == 0):
                w.setze(x, max(yb, hm + 2) + 1, z, st(x, 0, z))
    for y in range(1, int(4 * s) + 4):
        for x in range(-1, 2):
            for z in (-1, 0, 1):
                w.bloecke.pop((x, y + L.h.get((0, 0), 1), z), None)
    for x in range(-1, 2):
        w.setze(x, L.h.get((0, 0), 1) + int(4 * s) + 3, 0, w.b("iron_bars", north=False, south=False, east=True,
                                                                west=True, waterlogged=False))
    for sx in (-1, 1):
        tx = sx * int(R * 0.45)
        y = L.h.get((tx, 0), 1)
        eckturm(w, tx, 0, y + 1, 2, int(6 * s + 6), st, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]),
                form="kegel")
    eckturm(w, 0, 0, L.h.get((0, 0), 1) + hm, 2, int(3 * s + 2), st, None)
    L.bepflanzen(0.3, baeume=2 + g, arten=("fichte", "kiefer"), seed=seed)
    return w


def moorwacht(seed, g=1):
    """Moorwacht: ein hoher Holz-Wachturm auf Stelzen über einem nebligen Moor voller Tümpel, Bohlenwege führen
    zwischen Schilf und toten Bäumen hindurch, Laternen leuchten am Weg."""
    w = _neu(seed)
    L, R, s = land(w, g)
    rng = w.rng
    for k in range(5 + g * 3):
        a = rng.random() * 6.283
        d = rng.random() * R * 0.8
        L.see(math.cos(a) * d, math.sin(a) * d, (2 + rng.random() * 3) * s + 1, 1, tiefe=1)
    for p in L.h:
        if p not in L.wasser:
            L.boden[p] = ["grass_block", "mud", "moss_block", "podzol"][int(rng.random() * 4)]
    y = ebnen(L, 0, 0, 3)
    L.bauen()
    H = int(8 * s + 6)
    for (x, z) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        for yy in range(y + 1, y + H):
            w.setze(x, yy, z, stamm(w, "dark_oak", geschaelt=False))
    for x in range(-3, 4):
        for z in range(-3, 4):
            w.setze(x, y + H, z, w.b("dark_oak_planks"))
            if abs(x) == 3 or abs(z) == 3:
                w.setze(x, y + H + 1, z, zaun(w, "dark_oak"))
    kegeldach(w, 0, 0, y + H + 4, 3, Dachmat(w, ["spruce", "dark_oak"]), form="kegel", eckig=True)
    for (x, z) in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        for yy in range(y + H + 1, y + H + 4):
            w.setze(x, yy, z, zaun(w, "dark_oak"))
    for yy in range(y + 1, y + H):
        w.setze(0, yy, -2, w.b("ladder", facing="south", waterlogged=False))
    for k in range(3):
        a = k * 2.1
        for i in range(int(R * 0.9)):
            x, z = round(math.cos(a) * i), round(math.sin(a) * i)
            if (x, z) in L.h:
                yy = max(L.h[(x, z)], L.wasser.get((x, z), -9)) + 1
                w.setze(x, yy, z, w.b("spruce_slab", type="bottom", waterlogged=False))
                if i % 7 == 6:
                    w.setze(x + 1, yy, z, zaun(w, "spruce"))
                    w.setze(x + 1, yy + 1, z, w.b("lantern", hanging=False, waterlogged=False))
    L.bepflanzen(0.4, baeume=2 + g, arten=("weide",), seed=seed)
    for k in range(3 + g):
        (x, z) = list(L.h)[int(rng.random() * len(L.h))]
        if (x, z) not in L.wasser:
            einfuegen(w, wald2.totholz(seed + k, "dark_oak"), x, L.h[(x, z)], z)
    return w


def waldlaeuferlager(seed, g=1):
    """Waldläuferlager: in einem dichten Nadelwald verbergen sich Plattformen in den Baumkronen, verbunden durch
    Seilbrücken, unten ein Lagerfeuer, Zelte aus Tuch und Bogenziele."""
    w = _neu(seed)
    L, R, s = land(w, g)
    for p in L.h:
        L.boden[p] = "podzol" if w.rng.random() < 0.4 else "grass_block"
    L.bauen()
    rng = w.rng
    plattformen = []
    for k in range(3 + g):
        a = k / (3 + g) * 6.283
        x, z = round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)
        y = L.h.get((x, z), 1)
        H = int(10 * s + 6)
        einfuegen(w, wald2.fichte(seed + k, H=H + 6), x, y, z)
        yp = y + int(H * 0.55)
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                w.setze(x + dx, yp, z + dz, w.b("spruce_planks"))
                if abs(dx) == 2 or abs(dz) == 2:
                    w.setze(x + dx, yp + 1, z + dz, zaun(w, "spruce"))
        plattformen.append((x, yp, z))
    for (a, b) in zip(plattformen, plattformen[1:]):
        n = int(math.dist(a, b) * 1.5)
        for i in range(n + 1):
            t = i / n
            x = a[0] + (b[0] - a[0]) * t
            z = a[2] + (b[2] - a[2]) * t
            y = a[1] + (b[1] - a[1]) * t - 2 * math.sin(math.pi * t)
            w.setze(round(x), round(y), round(z), w.b("spruce_slab", type="bottom", waterlogged=False), False)
    y0 = L.h.get((0, 0), 1)
    w.setze(0, y0 + 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for k in range(2):
        cx, cz = (k * 2 - 1) * 4, 2
        y = L.h.get((cx, cz), y0)
        for dx in range(-1, 2):
            for h in range(2):
                w.setze(cx + dx, y + 1 + h, cz + (1 - h if dx == 0 else 0), w.b("green_wool"))
    L.bepflanzen(0.4, baeume=4 + g * 3, arten=("fichte", "kiefer"), seed=seed)
    return w


def brueckenstadt(seed, g=2):
    """Brückenstadt: über einer tiefen Felsschlucht mit Fluss spannt sich eine breite Steinbrücke, auf der dicht an
    dicht Fachwerkhäuser stehen, an beiden Enden Tortürme."""
    w = _neu(seed)
    rn = Rauschen(w, 7)
    sg = S[g]
    tief = int(8 * sg + 6)
    L, R, s = land(w, g, lambda x, z, h, R: (8 * sg + 4) - (tief if abs(z) < 4 * sg + 3 else 0) + 2 * rn(x, 0, z))
    L.fluss([(-R, 0), (R, 0)], 2 * s + 1, int(8 * sg + 4) - tief + 1, tiefe=1)
    L.bauen()
    yb = int(8 * s + 4) + 1
    st = stein(w)
    zr = int(4 * s + 4)
    for z in range(-zr - 2, zr + 3):
        for x in range(-4, 5):
            w.setze(x, yb, z, st(x, yb, z) if abs(x) == 4 else w.b("polished_andesite"))
        if abs(z) < zr:
            for y in range(yb - 1, yb - 1 - int(tief * (1 - (z / zr) ** 2) ** 0.5 * 0.3) - 1, -1):
                for x in range(-4, 5):
                    w.setze(x, y, z, st(x, y, z))
    stile = ["fachwerk", "terrakotta", "blau", "fachwerk"]
    for k, z in enumerate(range(-zr + 2, zr - 1, 6)):
        for sx in (-1, 1):
            haus(w, sx * 6, z, 5, 5, yb + 1, stile[(k + (sx > 0)) % 4], geschosse=2, tuer_s="west" if sx > 0
                 else "east", schorn=k % 2 == 0)
    for sz in (-1, 1):
        eckturm(w, 0, sz * (zr + 4), yb + 1, 2, int(6 * s + 5), st, Dachmat(w, ["mcw:red_terracotta", "brick"]),
                form="kegel")
        for y in range(yb + 1, yb + 4):
            w.bloecke.pop((0, y, sz * (zr + 4)), None)
    L.bepflanzen(0.3, baeume=3 + g, arten=("oak", "birke"), seed=seed)
    return w


def weidenfurt(seed, g=1):
    """Weidenfurt: ein breiter, flacher Fluss mit Trittsteinen und einer Furt, am Ufer eine Wassermühle mit großem
    Rad, Trauerweiden hängen ins Wasser, ein Weg führt durch."""
    w = _neu(seed)
    L, R, s = land(w, g)
    L.fluss([(-R, -R * 0.3), (0, 0), (R, R * 0.2)], 3 * s + 2, 1, tiefe=1)
    y = ebnen(L, round(R * 0.15), round(R * 0.45), 4, 3)
    L.bauen()
    for k in range(-int(3 * s + 2), int(3 * s + 3), 2):
        w.setze(0, 2, k, w.b("cobblestone_slab", type="bottom", waterlogged=False), False)
    hx, hz = round(R * 0.15), round(R * 0.45)
    haus(w, hx, hz, 7, 6, y + 1, "fachwerk", geschosse=2, tuer_s="south")
    rr = int(3 * s + 2)
    wx, wz = hx, hz - 4
    for k in range(int(rr * 7)):
        a = k / (rr * 7) * 6.283
        for r in range(rr + 1):
            if r == rr or k % max(1, int(rr * 7 / 8)) == 0:
                x, yy = round(math.cos(a) * r), round(math.sin(a) * r)
                w.setze(wx + x, y + 1 + yy, wz, w.b("spruce_planks") if r == rr else stamm(w, "spruce", "x"))
    L.bepflanzen(0.4, baeume=3 + g, arten=("weide", "weide", "oak"), seed=seed)
    return w


def orakelgrotte(seed, g=1):
    """Orakelgrotte: ein moosbewachsener Hügel mit einem großen Höhlenmaul, im Inneren leuchten Kristalle um ein
    Wasserbecken mit Altarstein, Fackeln säumen den Pfad hinein."""
    from kristall import kristall
    w = _neu(seed)
    sg = S[g]
    L, R, s = land(w, g, lambda x, z, h, R: 1 + max(0, (10 * sg + 6) * (1 - (math.hypot(x, z + 3) / (R * 0.7)) ** 2)))
    L.bauen(fels_ab=int(10 * s))
    hr = int(4 * s + 3)
    for x in range(-hr - 2, hr + 3):
        for y in range(1, hr * 2):
            for z in range(-int(R * 0.5), int(R * 0.4)):
                if (x / (hr + 1)) ** 2 + ((y - 1) / (hr * 1.4)) ** 2 + (z / (R * 0.45)) ** 2 <= 1:
                    w.bloecke.pop((x, y + 1, z - 2), None)
    for x in range(-2, 3):
        for z in range(-4, -1):
            w.setze(x, 1, z, w.b("water", level=0) if abs(x) < 2 else w.b("mossy_stone_bricks"))
    w.setze(0, 2, -6, w.b("chiseled_stone_bricks"))
    w.setze(0, 3, -6, w.b("enchanting_table"))
    rng = w.rng
    for k in range(6 + g * 3):
        a = rng.random() * 3.14 + 3.14
        kristall(w, (math.cos(a) * hr, 1 + rng.random() * hr, -2 + math.sin(a) * R * 0.3),
                 (-math.cos(a) * 0.5, 0.5, -math.sin(a) * 0.3), (2 + rng.random() * 3) * s, 0.6 * s + 0.4,
                 art="amethyst" if k % 2 else "saphir")
    for z in range(int(R * 0.35), int(R * 0.9), 3):
        for sx in (-2, 2):
            y = L.h.get((sx, z), 1)
            w.setze(sx, y + 1, z, zaun(w, "spruce"))
            w.setze(sx, y + 2, z, w.b("torch"))
    L.bepflanzen(0.5, baeume=2 + g, arten=("birke", "oak"), seed=seed)
    return w


def sturmgipfel(seed, g=1):
    """Sturmgipfel: ein kahler, felsiger Gipfel mit der Ruine eines runden Wachturms, eingestürzte Mauern, ein
    verwittertes Signalbecken und windzerzauste Kiefern."""
    w = _neu(seed)
    sg = S[g]
    rn = Rauschen(w, 6)
    L, R, s = land(w, g, lambda x, z, h, R: 1 + (14 * sg + 6) * max(0, 1 - math.hypot(x, z) / R) ** 1.3 *
                   (0.85 + 0.3 * rn(x, 0, z)))
    y = ebnen(L, 0, 0, int(3 * s + 3))
    L.bauen(fels_ab=int(6 * s + 3))
    rt = int(3 * s + 2)
    st = stein(w)
    for yy in range(y + 1, y + int(10 * s + 6)):
        for x in range(-rt - 1, rt + 2):
            for z in range(-rt - 1, rt + 2):
                d = math.hypot(x, z)
                if rt - 0.8 < d <= rt + 0.3:
                    w.setze(x, yy, z, st(x, yy, z))
    ruine(w, 0.55, ab_y=y + 3, box=(-rt - 1, rt + 1, -rt - 1, rt + 1))
    w.setze(rt + 3, y + 1, 0, w.b("cauldron"))
    L.bepflanzen(0.2, baeume=2 + g, arten=("kiefer",), seed=seed)
    return w


def klippenfestung(seed, g=2):
    """Klippenfestung: auf einer steilen Meeresklippe thront eine Festung mit Ringmauer, Rundtürmen und Bergfried,
    unten schlagen Wellen an den Fels, eine Treppe führt zur Anlegestelle."""
    w = _neu(seed)
    sg = S[g]
    rn = Rauschen(w, 6)
    L, R, s = land(w, g, lambda x, z, h, R: (10 * sg + 6) * (0.8 + 0.3 * rn(x, 0, z)) if z < R * 0.25 else -3)
    for p in L.h:
        if p[1] >= R * 0.25:
            L.wasser[p] = 1
    a = int(R * 0.4)
    y = ebnen(L, 0, -int(R * 0.25), a + 1)
    L.bauen(fels_ab=int(4 * s))
    st = stein(w)
    cz = -int(R * 0.25)
    mauer(w, -a, cz - a, a, cz + a, y + 1, y + int(4 * s) + 3, st)
    for x in range(-a, a + 1, 2):
        for z in (cz - a, cz + a):
            w.setze(x, y + int(4 * s) + 4, z, st(x, 0, z))
    dm = Dachmat(w, ["deepslate_tile", "cobbled_deepslate"])
    for (x, z) in ((-a, cz - a), (a, cz - a), (-a, cz + a), (a, cz + a)):
        eckturm(w, x, z, y + 1, 2, int(6 * s + 6), st, dm, form="kegel")
    eckturm(w, 0, cz, y + 1, 3, int(10 * s + 8), st, dm, form="glocke")
    for k in range(int(10 * s + 6)):
        w.setze(a - 1, y - k, cz + a + 1 + k // 2, treppe(w, "stone_brick", "north"), False)
    return w


def handelsposten(seed, g=1):
    """Handelsposten: an einer Wegkreuzung stehen ein großes Gasthaus mit Schild, ein Stall mit Heuboden, ein
    Brunnen und Karren mit Waren, Laternen säumen die Straßen."""
    w = _neu(seed)
    L, R, s = land(w, g)
    for (x, z) in L.h:
        if abs(x) <= 1 or abs(z) <= 1:
            L.boden[(x, z)] = "dirt_path"
    y1 = ebnen(L, 6, 7, 6, 5)
    y2 = ebnen(L, -7, 6, 4, 4)
    y3 = ebnen(L, 7, -7, 3, 3)
    L.bauen()
    haus(w, 7, 8, 9, 7, y1 + 1, "fachwerk", geschosse=2 + (g > 1), tuer_s="north", balk=True)
    fachwerk(w, -10, 3, -4, 9, y2 + 1, y2 + 4, M(w, [("spruce_planks", 1)]), holz="dark_oak", abstand=3)
    satteldach(w, -10, 3, -4, 9, y2 + 5, Dachmat(w, ["spruce", "dark_oak"]), first_x=False, traufe="dark_oak")
    for y in range(y2 + 1, y2 + 3):
        for z in range(5, 8):
            w.bloecke.pop((-4, y, z), None)
    w.setze(-6, y2 + 1, 6, w.b("hay_block", axis="y"))
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            w.setze(7 + dx, y3 + 1, -7 + dz, w.b("stone_bricks") if (dx or dz) else w.b("water", level=0))
    for (x, z) in ((3, 3), (-3, -3), (3, -3), (-3, 3)):
        y = L.h.get((x, z), 1)
        for yy in range(y + 1, y + 4):
            w.setze(x, yy, z, zaun(w, "spruce"))
        w.setze(x, y + 4, z, w.b("lantern", hanging=False, waterlogged=False))
    kram(w, -3, L.h.get((-3, 9), 1) + 1, 9, 5)
    L.bepflanzen(0.35, baeume=2 + g, arten=("oak", "birke"), seed=seed)
    return w


def drachenbrand(seed, g=1):
    """Drachenbrand-Dorf: die verkohlten Reste eines Dorfes nach einem Drachenangriff – geschwärzte Mauern,
    eingestürzte Dächer, glimmende Asche, verbrannte Bäume und tiefe Krallenspuren im Boden."""
    w = _neu(seed)
    L, R, s = land(w, g)
    rng = w.rng
    for p in L.h:
        L.boden[p] = ["coarse_dirt", "grass_block", "gravel", "soul_soil", "podzol"][int(rng.random() * 5)]
    plaetze = []
    for k in range(3 + g):
        a = k / (3 + g) * 6.283 + 0.4
        cx, cz = round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)
        plaetze.append((cx, cz, ebnen(L, cx, cz, 4)))
    for k in range(3):
        a = 0.8 + k * 0.25
        for i in range(int(R * 0.8)):
            x, z = round(math.cos(a) * i - R * 0.3), round(math.sin(a) * i - R * 0.3)
            if (x, z) in L.h:
                L.h[(x, z)] -= 2
    L.bauen()
    for (cx, cz, y) in plaetze:
        haus(w, cx, cz, 6, 5, y + 1, "fachwerk", geschosse=2, tuer_s="south", schorn=False)
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if y > 1 and any(t in n for t in ("planks", "log", "terracotta", "calcite", "stairs", "slab", "sandstone")):
            r = rng.random()
            if r < 0.45:
                del w.bloecke[(x, y, z)]
            elif r < 0.8:
                w.bloecke[(x, y, z)] = w.b("blackstone" if "log" not in n else "basalt", **({"axis": "y"} if
                                                                                              "log" in n else {}))
    for k in range(int(10 * s)):
        (x, z) = list(L.h)[int(rng.random() * len(L.h))]
        y = L.h[(x, z)]
        if w.frei(x, y + 1, z):
            w.setze(x, y + 1, z, w.b("campfire", lit=rng.random() < 0.5, signal_fire=True, facing="north",
                                     waterlogged=False) if rng.random() < 0.4 else w.b("magma_block") if False else
                    w.b("fire") if False else w.b("coal_block"))
    for k in range(2 + g):
        (x, z) = list(L.h)[int(rng.random() * len(L.h))]
        einfuegen(w, wald2.totholz(seed + k, "dark_oak"), x, L.h[(x, z)], z)
    return w


def riesentreppe(seed, g=2):
    """Riesentreppe: eine gewaltige, in den Berg gehauene Treppe mit hohen Stufen steigt zu einem Felsentor mit
    zwei Wächterpfeilern empor, Feuerschalen säumen den Aufstieg."""
    w = _neu(seed)
    sg = S[g]
    L, R, s = land(w, g, lambda x, z, h, R: 1 + max(0, (-z + R * 0.2) * 0.9))
    for (x, z) in L.h:
        if abs(x) <= int(2 * s + 2) and z < R * 0.6:
            L.h[(x, z)] = max(1, 1 + int(max(0, -z + R * 0.2) * 0.9 / 2) * 2)
            L.boden[(x, z)] = "stone_bricks"
    L.bauen(fels_ab=int(6 * s))
    zt = min(z for (x, z) in L.h if x == 0)
    ytop = L.h[(0, zt)]
    st = stein(w)
    for sx in (-1, 1):
        for y in range(ytop + 1, ytop + int(8 * s + 5)):
            for dx in (0, 1):
                for dz in (0, 1):
                    w.setze(sx * int(2 * s + 4) + dx, y, zt + dz, st(0, y, 0))
    for x in range(-int(2 * s + 4), int(2 * s + 5)):
        w.setze(x, ytop + int(8 * s + 5), zt, st(x, 0, zt))
    for z in range(-R, R, 5):
        for sx in (-1, 1):
            x = sx * (int(2 * s + 2) + 1)
            if (x, z) in L.h:
                y = L.h[(x, z)]
                w.setze(x, y + 1, z, w.b("cauldron"))
                w.setze(x, y + 2, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    L.bepflanzen(0.2, baeume=2, arten=("kiefer",), seed=seed)
    return w


def hochlandruine(seed, g=2):
    """Hochlandruine: auf einem grünen Hügel liegen die Reste einer Burg – ein halb eingestürzter Bergfried,
    Mauerstümpfe und ein Torbogen, von Efeu und Gras überwuchert, Schafe weiden im Hof."""
    w = _neu(seed)
    sg = S[g]
    L, R, s = land(w, g, lambda x, z, h, R: 1 + max(0, (8 * sg + 4) * (1 - (math.hypot(x, z) / R) ** 2)))
    a = int(R * 0.35)
    y = ebnen(L, 0, 0, a + 1)
    L.bauen()
    st = M(w, [("mossy_stone_bricks", 2), ("stone_bricks", 2), ("cracked_stone_bricks", 1), ("cobblestone", 1)])
    mauer(w, -a, -a, a, a, y + 1, y + int(4 * s) + 3, st)
    eckturm(w, -a + 3, -a + 3, y + 1, 2, int(10 * s + 6), st, None)
    ruine(w, 0.5, ab_y=y + 2)
    for z in (a,):
        for x in range(-1, 2):
            for yy in range(y + 1, y + 4):
                w.bloecke.pop((x, yy, z), None)
    from feinbau import efeu
    efeu(w, 0.08, laub=0.3)
    L.bepflanzen(0.4, baeume=1 + g, arten=("oak", "birke"), seed=seed)
    return w


def pfahldorf(seed, g=1):
    """Pfahldorf am See: Fischerhäuser auf Holzpfählen stehen im flachen Wasser eines Sees, verbunden durch
    Stege, Netze trocknen an Gestellen, Boote liegen am Ufer."""
    w = _neu(seed)
    L, R, s = land(w, g)
    L.see(0, R * 0.2, R * 0.65, 1, tiefe=2)
    L.bauen()
    n = 3 + g * 2
    pos = []
    for k in range(n):
        a = k / n * 3.14 + 0.2
        cx, cz = round(math.cos(a) * R * 0.35), round(R * 0.2 + math.sin(a) * R * 0.35)
        pfahlhaus(w, cx, cz, 1, 5, 4, ["fachwerk", "blau", "terrakotta"][k % 3])
        pos.append((cx, cz))
    for (a, b) in zip(pos, pos[1:]):
        n2 = int(math.dist(a, b) * 1.5)
        for i in range(n2 + 1):
            t = i / n2
            w.setze(round(a[0] + (b[0] - a[0]) * t), 2, round(a[1] + (b[1] - a[1]) * t), w.b("spruce_planks"),
                    False)
    L.bepflanzen(0.4, baeume=2 + g, arten=("weide", "birke"), seed=seed)
    return w


def fjordleuchtturm(seed, g=2):
    """Fjord-Leuchtturm: zwischen zwei steilen Felswänden öffnet sich ein Fjord zum Meer, auf einer Felsnase
    steht ein rot-weißer Leuchtturm mit Wärterhaus, Boote ankern im Wasser."""
    from inseln2 import leuchtturm
    w = _neu(seed)
    sg = S[g]
    rn = Rauschen(w, 6)
    L, R, s = land(w, g, lambda x, z, h, R: (12 * sg + 4) * (0.8 + 0.3 * rn(x, 0, z)) * min(1, abs(x) / (R * 0.4)) ** 1.5
                   - 3)
    for p in L.h:
        if L.h[p] < 1:
            L.wasser[p] = 1
    tx, tz = round(R * 0.45), round(R * 0.3)
    y = ebnen(L, tx, tz, 3, y=int(3 * sg) + 3)
    L.bauen(fels_ab=int(4 * s))
    leuchtturm(w, tx, y, tz, H=int(10 * s + 6), r=2)
    haus(w, tx, tz - 6, 6, 5, y + 1, "stein", geschosse=1, tuer_s="south") if (tx, tz - 6) in L.h else None
    from boote import ruderboot
    einfuegen(w, ruderboot(seed, 0), 0, 1, round(R * 0.2))
    L.bepflanzen(0.3, baeume=3, arten=("fichte", "kiefer"), seed=seed)
    return w


def bergkloster(seed, g=2):
    """Bergkloster: an eine senkrechte Felswand geschmiegt kleben übereinander gestaffelte Klostergebäude mit
    roten Dächern, verbunden durch Treppen und Holzgalerien."""
    w = _neu(seed)
    sg = S[g]
    L, R, s = land(w, g, lambda x, z, h, R: 1 + (18 * sg + 8) * min(1, max(0, (-z - R * 0.2) / (R * 0.15))))
    L.bauen(fels_ab=int(4 * s))
    stile = ["stein", "terrakotta", "stein", "fachwerk"]
    for k in range(3 + g):
        x = int((k - (2 + g) / 2) * 7)
        z = -int(R * 0.2) - 1 + 0
        y = 2 + k * int(4 * s + 2)
        for xx in range(x - 4, x + 5):
            for zz in range(z - 5, z + 3):
                for yy in range(1, y):
                    w.setze(xx, yy, zz, w.b("stone"), False)
        haus(w, x, z - 1, 7, 5, y + 1, stile[k % 4], geschosse=1 + (k % 2), tuer_s="south",
             schorn=k == 0)
    L.bepflanzen(0.3, baeume=2 + g, arten=("kiefer", "fichte"), seed=seed)
    return w


def muehlenhuegel(seed, g=1):
    """Mühlenhügel: auf einem sanften Hügel drehen sich drei Windmühlen über Weizen- und Kürbisfeldern, Feldwege,
    Heuballen und ein Bauernhaus am Fuß."""
    w = _neu(seed)
    sg = S[g]
    L, R, s = land(w, g, lambda x, z, h, R: 1 + max(0, (5 * sg + 2) * (1 - (math.hypot(x, z) / R) ** 2)))
    rng = w.rng
    for (x, z) in L.h:
        if x % 6 in (1, 2, 3, 4) and z % 8 not in (0,) and math.hypot(x, z) < R * 0.9:
            L.boden[(x, z)] = "farmland"
    pos = []
    for k in range(3):
        a = k / 3 * 6.283
        cx, cz = round(math.cos(a) * R * 0.3), round(math.sin(a) * R * 0.3)
        pos.append((cx, cz, ebnen(L, cx, cz, 4)))
    L.bauen()
    for (x, z), h in L.h.items():
        if L.boden.get((x, z)) == "farmland":
            w.setze(x, h, z, w.b("farmland", moisture=7))
            w.setze(x, h + 1, z, w.b("wheat", age=7) if z % 5 else w.b("pumpkin") if rng.random() < 0.3 else
                    w.b("carrots", age=7))
    for (cx, cz, y) in pos:
        windmuehle(w, cx, y + 1, cz, int(7 * s + 5), 1)
    L.bepflanzen(0.3, baeume=1, arten=("oak",), seed=seed)
    return w


def schaeferhof(seed, g=1):
    """Schäferhof: ein langgestrecktes Bauernhaus mit Steinsockel in einem grünen Tal, Trockenmauern umschließen
    Weiden mit Pferchen, ein Bach mit Holzsteg und ein Schäferkarren."""
    w = _neu(seed)
    sg = S[g]
    rn = Rauschen(w, 10)
    L, R, s = land(w, g, lambda x, z, h, R: 1 + abs(z) * 0.25 * sg + 2 * rn(x, 0, z))
    L.fluss([(-R, 2), (R, -2)], 1.5 * s + 1, 1, tiefe=1)
    y = ebnen(L, -int(R * 0.3), -int(R * 0.4), 6, 4)
    L.bauen()
    haus(w, -int(R * 0.3), -int(R * 0.4), 11, 6, y + 1, "stein", geschosse=1 + (g > 1), tuer_s="south")
    st = M(w, [("cobblestone", 2), ("mossy_cobblestone", 2), ("stone", 1)])
    for (x, z), h in L.h.items():
        if (x, z) in L.wasser:
            continue
        if (z == int(R * 0.35) or x in (int(R * 0.1), int(R * 0.6))) and 0 < z <= int(R * 0.35) + 1 and \
                int(R * 0.1) <= x <= int(R * 0.6):
            w.setze(x, h + 1, z, st(x, h, z))
            if (x + z) % 3 == 0:
                w.setze(x, h + 2, z, st(x, h + 1, z))
    for k in range(-2, 3):
        w.setze(0, 2, k, w.b("spruce_slab", type="bottom", waterlogged=False), False)
    L.bepflanzen(0.45, baeume=2 + g, arten=("oak", "busch"), seed=seed)
    return w


def wasserfallheiligtum(seed, g=2):
    """Wasserfall-Heiligtum: ein hoher Wasserfall stürzt von einer Felskante in ein Becken, hinter dem Wasservorhang
    liegt ein kleiner Schrein mit Säulen, Kerzen und einer Steinbank."""
    from gewaesser import fall_spalten, gischt
    w = _neu(seed)
    sg = S[g]
    H = int(12 * sg + 6)
    L, R, s = land(w, g, lambda x, z, h, R: 1 + (H if z < -R * 0.2 else 0))
    L.see(0, 0, R * 0.35, 1, tiefe=2)
    fall_spalten(L, -int(2 * s), int(2 * s), -int(R * 0.2), H + 1, 1)
    L.bauen(fels_ab=3)
    zf = -int(R * 0.2)
    for x in range(-int(2 * s) - 1, int(2 * s) + 2):
        for z in range(zf - 4, zf):
            for y in range(2, 6):
                w.bloecke.pop((x, y, z), None)
            w.setze(x, 1, z, w.b("smooth_stone"))
    for x in (-int(2 * s) - 1, int(2 * s) + 1):
        for y in range(2, 6):
            w.setze(x, y, zf - 1, w.b("quartz_pillar", axis="y"))
    w.setze(0, 2, zf - 3, w.b("chiseled_quartz_block"))
    w.setze(0, 3, zf - 3, w.b("candle", candles=4, lit=True, waterlogged=False))
    gischt(w, 0, 2, zf + 2, 2 + s)
    L.bepflanzen(0.4, baeume=2 + g, arten=("birke", "oak"), seed=seed)
    return w


SAGENLANDE2 = {
    "mondseeturm": ("Mondseeturm", mondseeturm),
    "steppenlager": ("Steppenlager", steppenlager),
    "passfeste": ("Passfeste", passfeste),
    "moorwacht": ("Moorwacht", moorwacht),
    "waldlaeuferlager": ("Waldläuferlager", waldlaeuferlager),
    "brueckenstadt": ("Brückenstadt über der Schlucht", brueckenstadt),
    "weidenfurt": ("Weidenfurt mit Mühle", weidenfurt),
    "orakelgrotte": ("Orakelgrotte", orakelgrotte),
    "sturmgipfel": ("Sturmgipfel-Ruine", sturmgipfel),
    "klippenfestung": ("Klippenfestung", klippenfestung),
    "handelsposten": ("Handelsposten an der Kreuzung", handelsposten),
    "drachenbrand": ("Drachenbrand-Dorf", drachenbrand),
    "riesentreppe": ("Riesentreppe", riesentreppe),
    "hochlandruine": ("Hochlandruine", hochlandruine),
    "pfahldorf": ("Pfahldorf am See", pfahldorf),
    "fjordleuchtturm": ("Fjord-Leuchtturm", fjordleuchtturm),
    "bergkloster": ("Bergkloster an der Felswand", bergkloster),
    "muehlenhuegel": ("Mühlenhügel", muehlenhuegel),
    "schaeferhof": ("Schäferhof im Tal", schaeferhof),
    "wasserfallheiligtum": ("Wasserfall-Heiligtum", wasserfallheiligtum),
}

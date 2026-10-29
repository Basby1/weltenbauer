"""Eisreich II – zwanzig weitere Bauten im ewigen Eis: Nordlicht-Bögen, Hundeschlitten-Station, Pinguinkolonie,
Walknochen-Hütte, Verschneite Ruinenstadt, Gletscherspalte mit Hängebrücke, Schneekapelle, Frostriese,
Eislaufsee mit Pavillon, Heiße Quellen mit Badehaus, Kota-Zeltlager, Eisbärenhöhle, Frostmagier-Turm,
Gipfel-Wetterwarte, Eingefrorener Krake, Holzfällerlager im Schnee, Eis-Steinkreis, Riesen-Schneekugel,
Eiszapfen-Höhle und Frostschmiede."""

from __future__ import annotations

import math

import numpy as np

import wald2
from feinbau import Dachmat, Mix, fensterreihe, kamin, kegeldach, laterne, platte, satteldach, treppe, tuer, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen, einfuegen
from skulptur import Skulptur, dreh_y, ell, kap, kasten, kegel, kreisrand
from wueste_eis import kuppel

S = [0.6, 1.0, 1.6, 2.5]


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def eis(w):
    return M(w, [("packed_ice", 3), ("blue_ice", 2), ("ice", 1)])


def schnee(w, R, huegel=1.0, cx=0, cz=0, fels=0.0):
    """Verschneiter Boden mit Eisflecken und (optional) Felsbuckeln; gibt die Höhen je Zelle zurück."""
    rn = Rauschen(w, 7)
    rf = Rauschen(w, 3)
    zellen = {}
    for x in range(cx - int(R) - 2, cx + int(R) + 3):
        for z in range(cz - int(R) - 2, cz + int(R) + 3):
            if math.hypot(x - cx, z - cz) <= R + 2 * rn(x, 0, z):
                h = int(huegel * 2 * rn(x * 0.7, 3, z * 0.7))
                v = rf(x, 5, z)
                for y in range(-2, h + 1):
                    if y == h:
                        b = "packed_ice" if v > 0.78 else "stone" if v < fels * 0.35 else "snow_block"
                    else:
                        b = "stone" if y < h - 1 else "snow_block"
                    w.setze(x, y, z, w.b(b))
                zellen[(x, z)] = h
    return zellen


def bestaeuben(w, p=0.65):
    """Puderschnee auf freiliegende Dächer, Felsen und Mauern."""
    namen = ["stone", "cobblestone", "stone_bricks", "spruce_planks", "dark_oak_planks", "spruce_log", "dark_oak_log",
             "deepslate_tiles", "cobbled_deepslate", "andesite", "tuff", "calcite", "mossy_cobblestone",
             "stripped_spruce_log", "oak_log", "oak_planks", "polished_andesite", "deepslate_bricks"]
    ids = {w.b(n) for n in namen}
    for n in ("spruce", "dark_oak", "deepslate_tile", "cobblestone", "stone_brick", "oak"):
        for f in ("north", "south", "east", "west"):
            ids.add(treppe(w, n, f))
    lage = w.b("snow", layers=1)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if b in ids and w.frei(x, y + 1, z) and rng.random() < p:
            w.setze(x, y + 1, z, lage)


def fichte(w, x, y, z, seed, H):
    einfuegen(w, wald2.fichte(seed + x * 31 + z * 7, H=int(H), schnee=True), x, y, z)


def fichtenrand(w, zellen, R, n, seed, innen=0.6, H=(8, 14)):
    rng = w.rng
    for _ in range(n):
        a = rng.random() * 2 * math.pi
        r = R * (innen + rng.random() * (0.95 - innen))
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        fichte(w, x, zellen.get((x, z), 0) + 1, z, seed, H[0] + rng.random() * (H[1] - H[0]))


def blockhaus(w, cx, cz, B, T, y0, holz="spruce", H=4, tuer_s="south", dach=("spruce", "dark_oak"), schorn=True,
              steil=1):
    """Blockhütte aus liegenden Stämmen mit Eckverband, Fenstern mit Läden, Satteldach und Kamin."""
    x0, z0 = cx - B // 2, cz - T // 2
    x1, z1 = x0 + B - 1, z0 + T - 1
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            w.setze(x, y0 - 1, z, w.b("cobblestone" if x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1)
                                      else f"{holz}_planks"))
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            for y in range(y0, y0 + H):
                if x in (x0, x1) and z in (z0, z1):
                    w.setze(x, y, z, w.b(f"{holz}_log", axis="y"))
                elif z in (z0, z1):
                    w.setze(x, y, z, w.b(f"{holz}_log", axis="x"))
                elif x in (x0, x1):
                    w.setze(x, y, z, w.b(f"{holz}_log", axis="z"))
                else:
                    w.bloecke.pop((x, y, z), None)
    fensterreihe(w, x0, z0, x1, z1, y0 + 1, ("north", "south", "east", "west"), abstand=3, holz=holz, blumen=0.0)
    d = {"south": (cx, z1), "north": (cx, z0), "east": (x1, cz), "west": (x0, cz)}[tuer_s]
    tuer(w, d[0], y0, d[1], tuer_s, holz=holz, stufen=0)
    first = satteldach(w, x0, z0, x1, z1, y0 + H, Dachmat(w, list(dach)), first_x=B >= T, ue=1,
                       giebel=M(w, [(f"{holz}_planks", 3), (f"stripped_{holz}_log", 1)]), traufe=holz, steil=steil)
    if schorn:
        kamin(w, x1 - 1, z0 + 1, y0, (first or y0 + H + 3) + 1, M(w, [("cobblestone", 2), ("stone_bricks", 1)]))
    return first or y0 + H + 3


def figur(w, teile, u, pos, winkel=0.0, lo=(-4, -1, -4), hi=(4, 8, 4)):
    """teile: [(form, block)] – kleine Tierskulptur, um winkel gedreht an pos."""
    Sk = Skulptur(w, u)
    for i, (form, blk) in enumerate(teile):
        Sk.mat(str(i), blk)
        Sk.plus(form, str(i))
    Sk.rendern(lo, hi, versatz=(pos[0] + 0.5, pos[1], pos[2] + 0.5), dreh=dreh_y(winkel))


def hund(w, fell="light_gray_wool"):
    b = w.b(fell)
    weiss = w.b("white_wool")
    d = w.b("black_wool")
    return [(ell(0, 2.0, 0, 1.7, 0.85, 0.75), b), (ell(0.2, 1.75, 0, 1.2, 0.5, 0.6), weiss),
            (ell(1.8, 2.8, 0, 0.75, 0.65, 0.6), b), (ell(2.5, 2.6, 0, 0.45, 0.3, 0.3), weiss),
            (ell(2.9, 2.65, 0, 0.15, 0.15, 0.15), d),
            (kap((1.7, 3.3, -0.35), (1.6, 3.9, -0.4), 0.22), b), (kap((1.7, 3.3, 0.35), (1.6, 3.9, 0.4), 0.22), b),
            (kap((-1.6, 2.4, 0), (-1.9, 3.3, 0), 0.35, 0.2), weiss)] + \
        [(kap((sx, 1.6, sz), (sx, 0, sz), 0.3), b) for sx in (-1.1, 1.1) for sz in (-0.4, 0.4)]


# ============================================================================ Bauten

def nordlichtbogen(seed, g=2):
    """Nordlicht-Bögen: schimmernde, wellige Bänder aus grünem, türkisem und violettem Glas spannen sich in
    Bögen über ein Schneefeld; ihre Füße stehen auf Säulen aus blauem Eis mit Seelaternen, darunter eine
    kleine Beobachterhütte."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    rng = w.rng
    zellen = schnee(w, R, 0.8)
    farben = ["lime_stained_glass", "green_stained_glass", "cyan_stained_glass", "light_blue_stained_glass",
              "purple_stained_glass", "magenta_stained_glass"]
    n = 3 + g
    for k in range(n):
        a = (k / n - 0.5) * 1.1 + rng.random() * 0.2
        zk = (k - (n - 1) / 2) * 3.0 * s
        Rk = (9 + rng.random() * 4) * s + 4
        hf = 0.9 + rng.random() * 0.4
        breite = max(2, int(2 + 2 * s))
        for i in range(int(Rk * 8)):
            th = math.pi * i / (Rk * 8)
            for dd in range(breite):
                r = Rk + dd
                px = math.cos(th) * r
                py = math.sin(th) * r * hf
                welle = math.sin(th * 4 + k) * 1.4 * s
                x = round(px * math.cos(a))
                z = round(zk + px * math.sin(a) + welle)
                w.setze(x, round(py) + 2, z, w.b(farben[min(5, (dd * 6) // breite + (k % 2))]))
        for sx in (-1, 1):
            fx, fz = round(sx * (Rk + breite / 2) * math.cos(a)), round(zk + sx * (Rk + breite / 2) * math.sin(a))
            for y in range(0, 4):
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        if abs(dx) + abs(dz) < 2 or y == 0:
                            w.setze(fx + dx, y, fz + dz, w.b("blue_ice" if y < 3 else "packed_ice"))
            w.setze(fx, 4, fz, w.b("sea_lantern"))
    hz = int(R * 0.6)
    blockhaus(w, 0, hz, int(4 * s + 4), int(3 * s + 4), zellen.get((0, hz), 0) + 1, tuer_s="north")
    fichtenrand(w, zellen, R, 4 + 3 * g, seed, innen=0.75)
    bestaeuben(w)
    return w


def hundeschlitten(seed, g=1):
    """Hundeschlitten-Station: eine Blockhütte mit Vorbau, eine Reihe Hundehütten mit Huskys, zwei beladene
    Schlitten mit vorgespannten Hundegespannen und eine festgefahrene Schlittenspur."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 7)
    zellen = schnee(w, R, 0.3)
    blockhaus(w, -int(R * 0.35), -int(R * 0.35), int(5 * s + 5) | 1, int(4 * s + 5) | 1, 1)
    for i in range(3 + g):
        x = -int(R * 0.6) + i * 4
        z = int(R * 0.15)
        for dx in (0, 1):
            for dz in (0, 1):
                w.setze(x + dx, 1, z + dz, w.b("spruce_planks"))
            w.setze(x + dx, 2, z, platte(w, "spruce", "bottom"))
            w.setze(x + dx, 2, z + 1, platte(w, "spruce", "bottom"))
        w.bloecke.pop((x, 1, z + 1), None)
        figur(w, hund(w, ["light_gray_wool", "gray_wool", "white_wool"][i % 3]), 0.55, (x, 1, z + 3),
              winkel=math.pi / 2 + (i % 2) * 0.6)
    for x in range(-R + 2, R - 1):
        for dz in (-1, 0, 1):
            z = int(R * 0.55) + dz + round(math.sin(x / 5) * 2)
            w.setze(x, zellen.get((x, z), 0), z, w.b("white_concrete_powder"))
    for k, x0 in enumerate((-int(R * 0.4), int(R * 0.15))):
        z0 = int(R * 0.55) + round(math.sin(x0 / 5) * 2)
        y = zellen.get((x0, z0), 0) + 1
        for x in range(x0, x0 + 5):
            for z in (z0 - 1, z0 + 1):
                w.setze(x, y, z, platte(w, "spruce", "bottom"))
            w.setze(x, y, z0, w.b("spruce_planks") if x < x0 + 4 else w.b("air"))
        w.setze(x0 + 5, y + 1, z0 - 1, treppe(w, "spruce", "west"))
        w.setze(x0 + 5, y + 1, z0 + 1, treppe(w, "spruce", "west"))
        w.setze(x0, y + 1, z0 - 1, zaun(w, "spruce"))
        w.setze(x0, y + 1, z0 + 1, zaun(w, "spruce"))
        w.setze(x0, y + 2, z0, w.b("spruce_fence"))
        w.setze(x0 + 1, y + 1, z0, w.b("barrel", facing="up", open=False))
        w.setze(x0 + 2, y + 1, z0, w.b("chest", facing="east", type="single", waterlogged=False))
        w.setze(x0 + 3, y + 1, z0, w.b("brown_wool"))
        for j in range(2 + g // 2):
            for sz in (-1, 1):
                figur(w, hund(w, ["white_wool", "light_gray_wool"][(j + sz) % 2]), 0.5,
                      (x0 + 7 + j * 3, y - 1, z0 + sz), winkel=0.0)
    fichtenrand(w, zellen, R, 3 + 2 * g, seed, innen=0.8)
    bestaeuben(w)
    return w


def pinguin(w, gross=1.0):
    sch = w.b("black_concrete")
    we = w.b("white_concrete")
    ge = w.b("orange_concrete")
    return [(ell(0, 2.0 * gross, 0, 1.1 * gross, 2.0 * gross, 1.0 * gross), sch),
            (ell(0.45 * gross, 1.9 * gross, 0, 0.75 * gross, 1.6 * gross, 0.8 * gross), we),
            (ell(0.1, 4.2 * gross, 0, 0.75 * gross, 0.8 * gross, 0.75 * gross), sch),
            (ell(0.95 * gross, 4.1 * gross, 0, 0.45 * gross, 0.2, 0.2), ge),
            (ell(0.3, 0.1, 0, 0.7 * gross, 0.25, 0.7 * gross), ge),
            (ell(0.2, 3.6 * gross, 0, 0.6 * gross, 0.3, 0.7 * gross), w.b("yellow_concrete") if gross > 1.2 else sch)]


def pinguinkolonie(seed, g=1):
    """Pinguinkolonie: Eisschollen und ein verschneites Schelfeis im dunklen Polarmeer, darauf Dutzende Pinguine
    in Gruppen – große Kaiserpinguine mit gelbem Kragen, kleine Küken, einige springen gerade ins Wasser."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 6)
    rng = w.rng
    rn = Rauschen(w, 5)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 2:
                continue
            w.setze(x, -2, z, w.b("gravel"))
            w.setze(x, -1, z, w.b("water", level=0))
            schelf = z < -R * 0.25 + rn(x, 0, 0) * 4
            scholle = rn(x, 2, z) > 0.62
            if schelf:
                h = 2 + int(rn(x, 4, z) * 2 * s)
                for y in range(-1, h + 1):
                    w.setze(x, y, z, w.b("snow_block" if y == h else "packed_ice" if y > h - 2 else "blue_ice"))
            elif scholle:
                w.setze(x, 0, z, w.b("snow_block" if rn(x, 7, z) > 0.4 else "packed_ice"))
                w.setze(x, -1, z, w.b("ice"))
            else:
                w.setze(x, 0, z, w.b("water", level=0))
    n = 8 + 8 * g
    for _ in range(n * 3):
        if n <= 0:
            break
        x, z = int((rng.random() - 0.5) * 1.8 * R), int((rng.random() - 0.5) * 1.8 * R)
        top = max([y for y in range(-1, 12) if not w.frei(x, y, z)] or [None]) if True else None
        if top is None or w.hole(x, top, z) == w.b("water", level=0):
            continue
        gross = 1.5 if rng.random() < 0.25 else 0.6 if rng.random() < 0.25 else 1.0
        figur(w, pinguin(w, gross), 0.45 * s + 0.2, (x, top + 1, z), winkel=rng.random() * 6.28,
              lo=(-3, -1, -3), hi=(3, 8, 3))
        n -= 1
    for x in range(-3, 4):
        w.setze(x, 0, int(R * 0.6), w.b("water", level=0))
    return w


def walknochenhuette(seed, g=1):
    """Walknochen-Hütte: eine längliche Hütte, deren Gerippe aus gebogenen Walrippen besteht, bespannt mit
    Fellen; der Eingang ist ein gewaltiger Kieferknochen, davor Trockengestelle, Feuerstelle und Harpunen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = schnee(w, R, 0.3)
    L = int(5 * s + 4)
    Rh = 3.0 * s + 2.5
    fell = M(w, [("brown_wool", 3), ("brown_terracotta", 2), ("light_gray_wool", 1), ("white_terracotta", 1)])
    for x in range(-L, L + 1):
        t = x / (L + 1)
        r = Rh * math.sqrt(max(0.15, 1 - t * t))
        rippe = x % 2 == 0
        for i in range(int(r * 6) + 1):
            th = math.pi * i / (r * 6)
            z, y = round(math.cos(th) * r), round(math.sin(th) * r * 1.15) + 1
            w.setze(x, y, z, w.b("bone_block", axis="x") if rippe else fell(x, y, z))
            if rippe and r > 2.5:
                z2, y2 = round(math.cos(th) * (r + 0.7)), round(math.sin(th) * (r + 0.7) * 1.15) + 1
                w.setze(x, y2, z2, w.b("bone_block", axis="x"))
    for x in range(-L, L + 1):
        for z in range(-int(Rh), int(Rh) + 1):
            for y in range(1, int(Rh * 1.15) + 1):
                t = x / (L + 1)
                r = Rh * math.sqrt(max(0.15, 1 - t * t))
                if (z / r) ** 2 + ((y - 1) / (r * 1.15)) ** 2 < 0.72:
                    w.bloecke.pop((x, y, z), None)
            w.setze(x, 0, z, w.b("spruce_planks") if abs(z) < Rh - 0.5 else w.bloecke.get((x, 0, z), w.b("snow_block")))
    Rk = Rh + 1.5
    for i in range(int(Rk * 6) + 1):
        th = math.pi * i / (Rk * 6)
        z, y = round(math.cos(th) * Rk), round(math.sin(th) * Rk * 1.4) + 1
        for dz in (0, 1):
            w.setze(L + 1, y, z, w.b("bone_block", axis="y"))
            w.setze(L + 1, y, z + dz if abs(z) > 1 else z, w.b("bone_block", axis="y"))
    for y in range(1, 3):
        for z in (-1, 0, 1):
            w.bloecke.pop((L, y, z), None)
    fx = L + 5
    w.setze(fx, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for dz in (-1, 1):
        w.setze(fx + dz, 1, dz * 2, w.b("cobblestone"))
    for k in range(3):
        z = -int(R * 0.5) + k * 3
        for y in (1, 2, 3):
            w.setze(-L - 3, y, z, w.b("spruce_fence"))
            w.setze(-L - 6, y, z, w.b("spruce_fence"))
        for x in range(-L - 6, -L - 2):
            w.setze(x, 4, z, w.b("stripped_spruce_log", axis="x"))
            w.setze(x, 3, z, w.b("dried_kelp_block") if x % 2 else w.b("air"))
    for k in range(3):
        w.setze(L + 3, 1 + k, -int(Rh) - 2, w.b("spruce_fence"))
        w.setze(L + 3, 4 + k, -int(Rh) - 2, w.b("lightning_rod", facing="up", powered=False, waterlogged=False)
                if k == 0 else w.b("air"))
    bestaeuben(w, 0.3)
    return w


def verschneite_stadt(seed, g=2):
    """Verschneite Ruinenstadt: ein Dorf, fast vollständig unter meterhohem Schnee begraben – nur Dächer, Kamine,
    Giebel und die Turmspitze der Kirche ragen heraus; ein paar freigeschaufelte Gräben führen zu Türen."""
    from himmelsstadt2 import haus
    import erw_haeuser  # noqa: F401  (Stile ziegel/schiefer)
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    rng = w.rng
    schnee(w, R, 0.4)
    y0 = -2
    plaetze = []
    n = 3 + 2 * g
    for _ in range(n * 5):
        if len(plaetze) >= n:
            break
        x, z = int((rng.random() - 0.5) * 1.5 * R), int((rng.random() - 0.5) * 1.5 * R)
        if all(abs(x - a) > 10 or abs(z - b) > 10 for a, b in plaetze) and math.hypot(x, z) > 6:
            plaetze.append((x, z))
    for i, (x, z) in enumerate(plaetze):
        stil = ["stein", "schiefer", "fachwerk", "kupfer"][i % 4]
        try:
            haus(w, x, z, 7 + (i % 2) * 2, 6 + (i % 3), y0, stil=stil, geschosse=2, tuer_s="south")
        except KeyError:
            haus(w, x, z, 7, 6, y0, stil="stein", geschosse=2, tuer_s="south")
    for y in range(y0 - 2, y0 + 22):
        for dx in (-2, -1, 0, 1, 2):
            for dz in (-2, -1, 0, 1, 2):
                rand = max(abs(dx), abs(dz)) == 2
                if rand:
                    w.setze(dx, y, dz, w.b("stone_bricks" if y % 5 else "chiseled_stone_bricks"))
                else:
                    w.bloecke.pop((dx, y, dz), None)
        if y in (y0 + 17, y0 + 18):
            for d in (-1, 0, 1):
                for p in ((d, -2), (d, 2), (-2, d), (2, d)):
                    w.bloecke.pop((p[0], y, p[1]), None)
    w.setze(0, y0 + 17, 0, w.b("bell", attachment="ceiling", facing="north", powered=False))
    kegeldach(w, 0, 0, y0 + 22, 2, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]), form="nadel", eckig=True)
    rn = Rauschen(w, 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) > R:
                continue
            hs = y0 + 6 + int(rn(x, 1, z) * 4 * s)
            graben = any(abs(x - a) <= 1 and b < z <= b + 9 for a, b in plaetze[:2])
            for y in range(0, hs + 1):
                if graben and y <= y0 + 7:
                    if w.hole(x, y, z) == w.b("snow_block"):
                        w.bloecke.pop((x, y, z), None)
                    continue
                w.setze(x, y, z, w.b("snow_block"), False)
    bestaeuben(w, 0.8)
    return w


def gletscherspalte(seed, g=2):
    """Gletscherspalte mit Hängebrücke: zwei Gletscherhänge mit gebänderten, tiefblauen Eiswänden, getrennt
    durch eine tiefe Spalte; darüber schwingt eine Hängebrücke aus Planken und Seilen, an einem Ende ein
    kleines Expeditionszelt mit Laterne."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    H = int(5 * s + 4)
    D = int(6 * s + 4)
    spalt = 1.8 * s + 1.8
    rn = Rauschen(w, 6)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            mitte = math.sin(x / (4 * s + 2)) * 1.5 * s
            dz = abs(z - mitte)
            h = H + int(rn(x, 5, z) * 3) - (1 if dz > R * 0.6 else 0)
            if dz < spalt:
                w.setze(x, -D, z, w.b("water", level=0))
                w.setze(x, -D - 1, z, w.b("blue_ice"))
                continue
            unten = -D if dz < spalt + 3 else -2
            for y in range(unten, h + 1):
                band = (y + int(rn(x, y, z) * 3)) % 4
                b = "snow_block" if y >= h - 1 else ["blue_ice", "packed_ice", "ice", "packed_ice"][band]
                w.setze(x, y, z, w.b(b))
    z0, z1 = -int(spalt) - 2, int(spalt) + 2
    durch = 1.2 * s + 0.8
    for z in range(z0, z1 + 1):
        t = (z - z0) / (z1 - z0)
        y = H + 1 - round(durch * (1 - (2 * t - 1) ** 2))
        for x in (-1, 0, 1):
            w.setze(x, y, z, platte(w, "spruce", "bottom") if z % 3 else w.b("spruce_planks"))
        for x in (-2, 2):
            w.setze(x, y + 1, z, w.b("spruce_fence"))
    for z in (z0 - 1, z1 + 1):
        for x in (-2, 2):
            for y in range(H + 1, H + 4):
                w.setze(x, y, z, w.b("spruce_log", axis="y"))
            w.setze(x, H + 4, z, w.b("lantern", hanging=False, waterlogged=False))
    tz = z1 + 5
    for k in range(4):
        for x in range(-3 + k, 4 - k):
            for z in (tz, tz + 1, tz + 2, tz + 3):
                if k < 3 and abs(x) == 3 - k:
                    w.setze(x + 6, H + 1 + k, z, w.b("orange_wool"))
            w.setze(6, H + 1 + 3, tz + k, w.b("orange_wool"))
    for x in range(4, 9):
        for z in (tz, tz + 3):
            pass
    w.setze(6, H + 1, tz - 1, w.b("lantern", hanging=False, waterlogged=False))
    bestaeuben(w, 0.2)
    return w


def schneekapelle(seed, g=1):
    """Schneekapelle: eine kleine dunkle Holzkirche mit steilen, gestuften Dächern und einem schlanken
    Dachreiter mit Glocke, umgeben von einem Lattenzaun, Grabkreuzen, Laternen und verschneiten Tannen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = schnee(w, R, 0.3)
    B, T = int(4 * s + 5) | 1, int(7 * s + 7)
    first = blockhaus(w, 0, 0, B, T, 1, holz="dark_oak", H=int(3 * s + 3), dach=("dark_oak", "spruce"),
                      schorn=False, steil=2, tuer_s="south")
    th = first
    for y in range(th - 2, th + int(4 * s + 3)):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) == 1 or abs(dz) == 1:
                    oben = y > th + int(4 * s + 3) - 4
                    w.setze(dx, y, dz - T // 4, w.b("dark_oak_fence") if oben and (dx == 0 or dz == 0)
                            else w.b("dark_oak_planks"))
    sp = th + int(4 * s + 3)
    w.setze(0, sp - 2, -T // 4, w.b("bell", attachment="ceiling", facing="north", powered=False))
    kegeldach(w, 0, -T // 4, sp, 1, Dachmat(w, ["dark_oak", "spruce"]), form="nadel", eckig=True, spitze="gold_block")
    sb = int(B * 0.6) + 2
    w.setze(0, 1, T // 2 + 2, w.b("air"))
    for x in range(-B // 2 - 3, B // 2 + 4):
        for z in (-T // 2 - 3, T // 2 + 5):
            if not (z > 0 and abs(x) < 2):
                w.setze(x, zellen.get((x, z), 0) + 1, z, zaun(w, "spruce"))
    for z in range(-T // 2 - 3, T // 2 + 6):
        for x in (-B // 2 - 3, B // 2 + 3):
            w.setze(x, zellen.get((x, z), 0) + 1, z, zaun(w, "spruce"))
    for k in range(2 + g):
        x, z = -B // 2 - 2 + (k % 2) * (B + 3) - (k % 2), -T // 2 + k * 3
        y = zellen.get((x, z), 0) + 1
        w.setze(x, y, z, w.b("cobblestone_wall"))
        w.setze(x, y + 1, z, w.b("cobblestone_wall"))
    for x in (-2, 2):
        w.setze(x, 1, T // 2 + 3, w.b("spruce_fence"))
        w.setze(x, 2, T // 2 + 3, w.b("lantern", hanging=False, waterlogged=False))
    fichtenrand(w, zellen, R, 4 + 3 * g, seed, innen=0.75, H=(9, 16))
    bestaeuben(w, 0.85)
    _ = sb
    return w


def frostriese(seed, g=2):
    """Frostriese: ein kniender Riese aus Eis mit Rüstung aus dunklem Prismarin, langem, geflochtenem Schneebart,
    Eiszacken-Krone und leuchtenden Augen – beide Hände ruhen auf einem riesigen Eisschwert im Schnee."""
    w = _neu(seed)
    s = S[g]
    u = 0.95 * s + 0.45
    R = int(10 * u + 5)
    schnee(w, R, 0.4, fels=0.8)
    Sk = Skulptur(w, u)
    haut = M(w, [("packed_ice", 3), ("blue_ice", 1), ("light_blue_terracotta", 1)])
    Sk.mat("h", lambda x, y, z, *a: haut(x, y, z))
    Sk.mat("r", lambda x, y, z, *a: w.b("dark_prismarine" if (y // 2) % 3 else "prismarine_bricks"))
    Sk.mat("b", lambda x, y, z, *a: w.b("snow_block" if (x + y) % 3 else "white_concrete"))
    Sk.mat("e", w.b("sea_lantern"))
    Sk.mat("k", w.b("blue_ice"))
    Sk.mat("s", lambda x, y, z, *a: w.b("ice" if (y % 3) else "packed_ice"))
    Sk.plus(ell(0, 6, 0, 3, 2.2, 2.2), "r")
    Sk.plus(kap((1.6, 6, 0), (1.6, 1.2, 2.2), 1.4, 1.2), "h")
    Sk.plus(kap((1.6, 1.0, 2.2), (1.6, 0.8, -3.0), 1.1, 0.9), "h")
    Sk.plus(kap((-1.6, 6, 0), (-1.7, 6.8, 4.6), 1.4, 1.2), "h")
    Sk.plus(kap((-1.7, 6.8, 4.6), (-1.7, 0.8, 5.2), 1.15, 1.0), "h")
    Sk.plus(ell(-1.7, 0.7, 6.0, 1.1, 0.7, 1.6), "r")
    Sk.plus(ell(1.6, 1.4, 2.4, 1.3, 1.1, 1.3), "r")
    Sk.plus(ell(0, 10, 0, 3.5, 4, 2.5), "h")
    Sk.plus(ell(0, 10.3, 0.7, 3.5, 3.2, 2.2), "r")
    for sx in (-1, 1):
        Sk.plus(ell(sx * 3.9, 13, 0, 1.7, 1.4, 1.7), "r")
        Sk.plus(kap((sx * 3.9, 13, 0), (sx * 3.0, 9.5, 3.0), 1.15, 1.0), "h")
        Sk.plus(kap((sx * 3.0, 9.5, 3.0), (sx * 0.8, 9.2, 5.6), 1.0, 0.9), "h")
        Sk.plus(kegel(sx * 3.9, 0, 14, 15.6, 0.6, 0.1), "k")
    Sk.plus(ell(0, 9.2, 6.0, 1.5, 1.1, 1.1), "h")
    Sk.plus(kasten(-0.5, 0, 5.6, 0.5, 8.3, 6.4), "s")
    Sk.plus(kasten(-2.4, 8.0, 5.5, 2.4, 8.6, 6.5), "r")
    Sk.plus(ell(0, 10.6, 6.0, 0.6, 0.6, 0.6), "k")
    Sk.plus(kap((0, 13.5, 0), (0, 15, 0.3), 1.1), "h")
    Sk.plus(ell(0, 16.3, 0.5, 1.8, 2.0, 1.8), "h")
    Sk.plus(ell(0, 14.6, 1.7, 1.6, 2.0, 1.0), "b")
    Sk.plus(kap((0, 14.5, 1.9), (0, 10.8, 2.7), 1.0, 0.45), "b")
    Sk.plus(ell(0, 17.4, 0.4, 2.0, 1.2, 2.0), "r")
    for i in range(7):
        a = i / 7 * 2 * math.pi
        Sk.plus(kegel(math.cos(a) * 1.5, 0.4 + math.sin(a) * 1.5, 17.8, 20.0 + (i % 2), 0.45, 0.05), "k")
    for sx in (-0.65, 0.65):
        Sk.plus(ell(sx, 16.6, 2.15, 0.32, 0.25, 0.2), "e")
    Sk.rendern((-6, 0, -5), (6, 21, 8), versatz=(0.5, 0, -2.5))
    rng = w.rng
    for _ in range(6 + 4 * g):
        a = rng.random() * 2 * math.pi
        r = R * (0.55 + rng.random() * 0.35)
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        h = int(2 + rng.random() * 5 * s)
        for y in range(1, h + 1):
            rr = 1.4 * (1 - (y - 1) / h) * (0.6 + s * 0.4)
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if dx * dx + dz * dz <= rr * rr + 0.3:
                        w.setze(x + dx, y, z + dz, w.b("blue_ice" if y < h - 1 else "packed_ice"))
    return w


def eislaufsee(seed, g=1):
    """Eislaufsee mit Pavillon: ein zugefrorener See zwischen Tannen, am Ufer ein achteckiger Musikpavillon,
    ein Punschstand, Laternen rund um die Eisfläche, Bänke und ein Schneemann."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = schnee(w, R, 0.3)
    rn = Rauschen(w, 6)
    Rs = R * 0.55
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z * 1.3)
            if d < Rs + rn(x, 2, z) * 3:
                w.setze(x, 0, z, w.b("ice" if rn(x, 8, z) > 0.35 else "packed_ice"))
                w.setze(x, -1, z, w.b("water", level=0))
                for y in range(1, 4):
                    w.bloecke.pop((x, y, z), None)
                zellen[(x, z)] = 0
    for i in range(10 + 4 * g):
        a = i / (10 + 4 * g) * 2 * math.pi
        x, z = round(math.cos(a) * (Rs + 3)), round(math.sin(a) * (Rs + 3) / 1.3)
        y = zellen.get((x, z), 0) + 1
        w.setze(x, y, z, w.b("dark_oak_fence"))
        w.setze(x, y + 1, z, w.b("dark_oak_fence"))
        w.setze(x, y + 2, z, w.b("lantern", hanging=False, waterlogged=False))
    px, pz = 0, -int(R * 0.78)
    pr = int(2 * s + 3)
    y0 = zellen.get((px, pz), 0) + 1
    for x, z in kreisrand(pr, px, pz):
        w.setze(x, y0 - 1, z, w.b("polished_andesite"))
    for x in range(px - pr, px + pr + 1):
        for z in range(pz - pr, pz + pr + 1):
            if math.hypot(x - px, z - pz) <= pr:
                w.setze(x, y0 - 1, z, w.b("spruce_planks" if math.hypot(x - px, z - pz) < pr - 0.5 else
                                          "polished_andesite"))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x, z = round(px + math.cos(a) * (pr - 0.5)), round(pz + math.sin(a) * (pr - 0.5))
        for y in range(y0, y0 + 4):
            w.setze(x, y, z, w.b("white_concrete" if y < y0 + 3 else "quartz_pillar", axis="y")
                    if False else w.b("quartz_pillar", axis="y"))
    kegeldach(w, px, pz, y0 + 4, pr, Dachmat(w, ["dark_prismarine", "prismarine_brick"]), form="glocke",
              eckig=True, spitze="gold_block")
    laterne(w, px, y0 + 3, pz, kette=1)
    kx, kz = int(R * 0.72), int(R * 0.15)
    blockhaus(w, kx, kz, 5, 4, zellen.get((kx, kz), 0) + 1, tuer_s="west", schorn=True)
    for k in range(2):
        bx, bz = -int(R * 0.7), -3 + k * 6
        y = zellen.get((bx, bz), 0) + 1
        for dz in (0, 1, 2):
            w.setze(bx, y, bz + dz, treppe(w, "spruce", "west"))
    sx, sz = -int(R * 0.5), int(R * 0.62)
    y = zellen.get((sx, sz), 0) + 1
    kugel(w, sx, y + 1, sz, 1.6, w.b("snow_block"))
    kugel(w, sx, y + 3.2, sz, 1.2, w.b("snow_block"))
    kugel(w, sx, y + 4.8, sz, 0.9, w.b("snow_block"))
    w.setze(sx, y + 5, sz + 1, w.b("carved_pumpkin", facing="south"))
    fichtenrand(w, zellen, R, 6 + 3 * g, seed, innen=0.82)
    bestaeuben(w)
    return w


def thermalquellen(seed, g=1):
    """Heiße Quellen mit Badehaus: dampfende Sinterterrassen mit türkisen Becken auf verschneitem Fels,
    Rauchschwaden aus Erdspalten und ein hölzernes Badehaus mit überdachtem Steg."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = schnee(w, R, 0.4, fels=1.0)
    rng = w.rng
    stufen = 3 + g
    for k in reversed(range(stufen)):
        cx, cz = round((k - stufen / 2) * 1.5 * s), round(-R * 0.45 + k * 3.2 * s)
        r = (2.0 + k * 0.8) * s + 2
        y = (stufen - k) * 2
        for x in range(int(cx - r) - 2, int(cx + r) + 3):
            for z in range(int(cz - r) - 2, int(cz + r) + 3):
                d = math.hypot(x - cx, (z - cz) * 1.3)
                if d <= r + 1:
                    for yy in range(0, y + 1):
                        w.setze(x, yy, z, w.b("calcite" if yy > y - 2 else "stone"))
                    if d <= r - 0.3:
                        w.setze(x, y, z, w.b("water", level=0))
                        w.setze(x, y - 1, z, w.b("light_blue_terracotta" if d > r * 0.6 else "cyan_terracotta"))
                    else:
                        w.setze(x, y + 1, z, w.b("calcite" if rng.random() < 0.8 else "dripstone_block"))
        for _ in range(2):
            a = rng.random() * 6.28
            x, z = round(cx + math.cos(a) * (r + 2)), round(cz + math.sin(a) * (r + 2))
            w.setze(x, y + 1, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
            w.setze(x, y, z, w.b("hay_block"))
    bx, bz = int(R * 0.55), int(R * 0.35)
    blockhaus(w, bx, bz, int(5 * s + 5) | 1, int(4 * s + 5) | 1, zellen.get((bx, bz), 0) + 1, tuer_s="west",
              dach=("dark_oak", "spruce"))
    for x in range(-int(R * 0.1), bx - int(2.5 * s + 2)):
        z = bz
        y = zellen.get((bx, bz), 0)
        for dz in (-1, 0, 1):
            w.setze(x, y, z + dz, w.b("spruce_planks"))
        if x % 3 == 0:
            for dz in (-1, 1):
                for yy in range(y + 1, y + 4):
                    w.setze(x, yy, z + dz, w.b("spruce_fence"))
        for dz in (-2, -1, 0, 1, 2):
            w.setze(x, y + 4, z + dz, platte(w, "dark_oak", "bottom"))
    fichtenrand(w, zellen, R, 3 + 2 * g, seed, innen=0.85)
    bestaeuben(w, 0.5)
    return w


def kotalager(seed, g=1):
    """Kota-Zeltlager: kegelförmige Zelte aus Fellbahnen mit herausragenden Stangen, eine Feuerstelle mit
    Sitzsteinen, Trockengestelle, ein Rentiergehege mit Rentieren und ein beladener Schlitten."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = schnee(w, R, 0.3)
    rng = w.rng
    n = 3 + g
    bahnen = [M(w, [("brown_wool", 2), ("brown_terracotta", 1)]), M(w, [("light_gray_wool", 2), ("gray_wool", 1)]),
              M(w, [("white_wool", 2), ("white_terracotta", 1)])]
    for i in range(n):
        a = i / n * 2 * math.pi + 0.3
        cx, cz = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        r = 2.5 + s * 1.5
        h = int(r * 2.2)
        y0 = zellen.get((cx, cz), 0) + 1
        mat = bahnen[i % 3]
        for k in range(h):
            rr = r * (1 - k / h)
            for x, z in kreisrand(max(0.4, rr), cx, cz):
                w.setze(x, y0 + k, z, mat(x, y0 + k, z) if (x + z + k) % 7 else w.b("red_wool"))
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for k in range(3):
                w.setze(cx + dx * (k // 2), y0 + h + k - 1, cz + dz * (k // 2), w.b("spruce_fence"))
        ex, ez = round(cx - math.cos(a) * r), round(cz - math.sin(a) * r)
        for y in (y0, y0 + 1):
            w.bloecke.pop((ex, y, ez), None)
        w.setze(cx, y0, cz, w.b("campfire", lit=False, signal_fire=False, facing="north", waterlogged=False))
    w.setze(0, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        w.setze(round(math.cos(a) * 2.5), 1, round(math.sin(a) * 2.5), w.b("cobblestone_slab", type="bottom",
                                                                         waterlogged=False))
    gx, gz = -int(R * 0.2), int(R * 0.75)
    gr = int(3 * s + 3)
    for x in range(gx - gr, gx + gr + 1):
        for z in (gz - gr // 2, gz + gr // 2):
            w.setze(x, zellen.get((x, z), 0) + 1, z, zaun(w, "spruce"))
    for z in range(gz - gr // 2, gz + gr // 2 + 1):
        for x in (gx - gr, gx + gr):
            w.setze(x, zellen.get((x, z), 0) + 1, z, zaun(w, "spruce"))
    br = w.b("brown_wool")
    we = w.b("white_wool")
    ge = w.b("stripped_spruce_log")
    for k in range(1 + g):
        teile = [(ell(0, 2.4, 0, 1.6, 0.9, 0.75), br), (ell(-0.2, 2.2, 0, 1.0, 0.6, 0.65), we),
                 (kap((1.3, 2.8, 0), (2.0, 3.7, 0), 0.45), br), (ell(2.4, 3.8, 0, 0.6, 0.4, 0.35), br)] + \
                [(kap((sx, 1.9, sz), (sx, 0, sz), 0.25), br) for sx in (-1.1, 1.1) for sz in (-0.4, 0.4)] + \
                [(kap((2.2, 4.1, sz), (1.8, 5.6, sz * 3), 0.18), ge) for sz in (-0.3, 0.3)] + \
                [(kap((2.0, 5.0, sz * 2), (2.7, 5.5, sz * 3), 0.15), ge) for sz in (-0.3, 0.3)]
        x = gx - gr + 2 + k * 3
        figur(w, teile, 0.5 * s + 0.25, (x, zellen.get((x, gz), 0) + 1, gz), winkel=rng.random() * 6.28,
              lo=(-3, -1, -3), hi=(4, 7, 3))
    for k in range(2):
        z = -int(R * 0.7) + k * 3
        for x in range(-2, 3):
            w.setze(x, 4, z, w.b("stripped_spruce_log", axis="x"))
            if x % 2 == 0:
                w.setze(x, 3, z, w.b("dried_kelp_block"))
        for x in (-2, 2):
            for y in range(1, 4):
                w.setze(x, y, z, w.b("spruce_fence"))
    fichtenrand(w, zellen, R, 4 + 2 * g, seed, innen=0.85)
    bestaeuben(w, 0.4)
    return w


def eisbaerhoehle(seed, g=1):
    """Eisbärenhöhle: ein verschneiter Felshügel mit dunklem Höhlenmaul und Eiszapfen, davor eine aufgerichtete
    Eisbärin und zwei Jungtiere auf einer Eisscholle, ein Wasserloch und abgenagte Knochen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    H = 7 * s + 5
    zellen = schnee(w, R, 0.2)
    hx, hz = 0, -int(R * 0.35)
    Rh = R * 0.7
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x - hx, (z - hz) * 1.2)
            if d < Rh:
                h = int(H * (1 - (d / Rh) ** 2) + rn(x, 0, z) * 3)
                for y in range(1, h + 1):
                    w.setze(x, y, z, w.b("snow_block" if y >= h - 1 and rn(x, y, z) > 0.3 else
                                         "stone" if rn(x, y + 9, z) > 0.4 else "andesite"))
    tr = 2.2 * s + 1.5
    vorn = hz + int(Rh / 1.2) + 2
    for x in range(-int(tr) - 1, int(tr) + 2):
        for z in range(hz - int(Rh * 0.4), vorn + 1):
            for y in range(1, int(tr * 1.3) + 2):
                if (x / tr) ** 2 + ((y - 0.5) / (tr * 1.3)) ** 2 <= 1:
                    w.bloecke.pop((x, y, z), None)
    rng = w.rng
    for x in range(-int(tr), int(tr) + 1):
        for z in range(hz - int(Rh * 0.4), vorn + 1):
            yd = next((y for y in range(int(tr * 1.3) + 2, 1, -1)
                       if not w.frei(x, y, z) and w.frei(x, y - 1, z)), None)
            if yd and rng.random() < 0.35:
                for k in range(1, int(1 + rng.random() * tr * 0.7) + 1):
                    if yd - k > 1:
                        w.setze(x, yd - k, z, w.b("ice"))
        w.setze(x, 0, hz - int(Rh * 0.3), w.b("sea_lantern"))
    zf = vorn
    we = w.b("white_wool")
    we2 = w.b("white_concrete")
    sch = w.b("black_concrete")
    def baer(stehend):
        if stehend:
            return [(ell(0, 4.5, 0, 1.6, 2.6, 1.4), we), (ell(0, 7.2, 0.3, 1.0, 1.0, 1.0), we),
                    (ell(0, 7.0, 1.3, 0.5, 0.45, 0.5), we2), (ell(0, 7.1, 1.85, 0.2, 0.2, 0.15), sch),
                    (ell(-0.65, 8.1, 0.2, 0.3, 0.3, 0.25), we), (ell(0.65, 8.1, 0.2, 0.3, 0.3, 0.25), we),
                    (kap((-1.4, 5.8, 0.3), (-1.8, 7.5, 1.2), 0.55), we), (kap((1.4, 5.8, 0.3), (1.8, 7.5, 1.2), 0.55),
                                                                           we),
                    (kap((-0.8, 2.5, 0), (-0.8, 0, 0.3), 0.7), we), (kap((0.8, 2.5, 0), (0.8, 0, 0.3), 0.7), we)]
        return [(ell(0, 2.0, 0, 2.0, 1.2, 1.1), we), (ell(1.9, 2.4, 0, 0.8, 0.7, 0.7), we),
                (ell(2.6, 2.2, 0, 0.4, 0.35, 0.35), we2), (ell(2.95, 2.25, 0, 0.12, 0.12, 0.12), sch)] + \
            [(kap((sx, 1.6, sz), (sx, 0, sz), 0.45), we) for sx in (-1.2, 1.2) for sz in (-0.55, 0.55)]
    figur(w, baer(True), 0.55 * s + 0.35, (0, zellen.get((0, zf + 5), 0) + 1, zf + 5), winkel=0,
          lo=(-3, -1, -3), hi=(3, 9, 3))
    for k, (x, z) in enumerate(((-int(R * 0.4), zf + 7), (int(R * 0.35), zf + 8))):
        figur(w, baer(False), 0.4 * s + 0.2, (x, zellen.get((x, z), 0) + 1, z), winkel=1.2 + k * 2.2)
    lx, lz = int(R * 0.45), int(R * 0.6)
    for x in range(lx - 2, lx + 3):
        for z in range(lz - 2, lz + 3):
            if math.hypot(x - lx, z - lz) < 2.3:
                w.setze(x, zellen.get((x, z), 0), z, w.b("water", level=0))
    for k in range(4):
        x, z = -int(R * 0.15) + k, zf + 3 + (k % 2)
        w.setze(x, zellen.get((x, z), 0) + 1, z, w.b("bone_block", axis="x" if k % 2 else "z"))
    bestaeuben(w, 0.4)
    return w


def frostmagierturm(seed, g=2):
    """Frostmagier-Turm: ein in sich verdrehter Turm aus Pack- und Blaueis mit Glasbändern, darüber eine offene
    Plattform mit Eissäulen und ein schwebender, leuchtender Kristall; Eissplitter kreisen um die Spitze."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    schnee(w, R, 0.4)
    r = 2.2 * s + 2.2
    H = int(22 * s + 12)
    e = eis(w)
    for y in range(1, H):
        rot = y / H * math.pi * 1.4
        rr = r * (1.15 - 0.3 * y / H)
        ring = y % 7 == 0
        for x in range(-int(rr * 1.5) - 1, int(rr * 1.5) + 2):
            for z in range(-int(rr * 1.5) - 1, int(rr * 1.5) + 2):
                xr = x * math.cos(rot) + z * math.sin(rot)
                zr = -x * math.sin(rot) + z * math.cos(rot)
                m = max(abs(xr), abs(zr)) + 0.25 * min(abs(xr), abs(zr))
                if m <= rr + (0.6 if ring else 0):
                    innen = m < rr - 1.1
                    if innen:
                        w.bloecke.pop((x, y, z), None)
                    elif ring:
                        w.setze(x, y, z, w.b("blue_ice"))
                    elif y % 7 in (3, 4) and (x + z) % 3 == 0:
                        w.setze(x, y, z, w.b("light_blue_stained_glass"))
                    else:
                        w.setze(x, y, z, e(x, y, z))
    pr = int(r + 2)
    for x in range(-pr, pr + 1):
        for z in range(-pr, pr + 1):
            if math.hypot(x, z) <= pr + 0.3:
                w.setze(x, H, z, w.b("packed_ice" if math.hypot(x, z) < pr - 1 else "blue_ice"))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * (pr - 0.5)), round(math.sin(a) * (pr - 0.5))
        for y in range(H + 1, H + 4 + int(s)):
            w.setze(x, y, z, w.b("blue_ice"))
        w.setze(x, H + 4 + int(s), z, w.b("soul_lantern", hanging=False, waterlogged=False))
    kc = H + 6 + int(2 * s)
    kr = 1.5 + s
    for y in range(-int(kr * 1.8), int(kr * 1.8) + 1):
        rr = kr * (1 - abs(y) / (kr * 1.8 + 0.5))
        for x in range(-int(rr) - 1, int(rr) + 2):
            for z in range(-int(rr) - 1, int(rr) + 2):
                if abs(x) + abs(z) <= rr:
                    w.setze(x, kc + y, z, w.b("sea_lantern") if abs(x) + abs(z) < rr - 1.2 else
                            w.b("light_blue_stained_glass"))
    for i in range(8 + 4 * g):
        a = i / (8 + 4 * g) * 2 * math.pi
        rr = pr + 2 + (i % 3)
        kugel(w, math.cos(a) * rr, kc - 2 + math.sin(a * 3) * 2, math.sin(a) * rr, 0.6 + 0.3 * s, w.b("blue_ice"))
    for x in (-1, 0, 1):
        for y in (1, 2, 3):
            w.bloecke.pop((x, y, int(r * 1.15) + 1), None)
            w.bloecke.pop((x, y, int(r * 1.15)), None)
    rng = w.rng
    for _ in range(5 + 3 * g):
        a = rng.random() * 6.28
        d = R * (0.5 + rng.random() * 0.4)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        h = int(3 + rng.random() * 5 * s)
        for y in range(1, h):
            w.setze(x, y, z, w.b("blue_ice" if y < h - 2 else "packed_ice"))
            if y < h // 2:
                for dx, dz in ((1, 0), (0, 1)):
                    w.setze(x + dx, y, z + dz, w.b("packed_ice"))
    return w


def wetterwarte(seed, g=2):
    """Gipfel-Wetterwarte: ein verschneiter Felsgipfel mit Zickzackpfad; oben eine kleine Steinwarte mit
    Kupferkuppel, Windmesser, Wetterfahne und Funkmast, gesichert durch ein Geländer."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    H = int(12 * s + 8)
    rn = Rauschen(w, 4)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 1.5 * rn(x, 0, z):
                continue
            h = int(H * max(0.0, 1 - d / R) ** 0.8 + rn(x, 4, z) * 2.5)
            h = min(h, H - 1) if d < 4 + s else h
            for y in range(-2, h + 1):
                b = "snow_block" if y >= h - (0 if rn(x, y, z) > 0.45 else -1) else \
                    "stone" if rn(x, y + 7, z) > 0.45 else "andesite" if y % 3 else "tuff"
                w.setze(x, y, z, w.b(b))
    top = H
    for x in range(-int(3 + s), int(4 + s)):
        for z in range(-int(3 + s), int(4 + s)):
            for y in range(top, top + 8):
                w.bloecke.pop((x, y, z), None)
            w.setze(x, top - 1, z, w.b("stone_bricks"))
    b = int(2 + s)
    for x in range(-b, b + 1):
        for z in range(-b, b + 1):
            for y in range(top, top + 4):
                if max(abs(x), abs(z)) == b:
                    fen = y == top + 2 and (x + z) % 2 == 0 and min(abs(x), abs(z)) < b
                    w.setze(x, y, z, w.b("glass_pane") if fen else w.b("stone_bricks" if y > top else
                                                                        "cobblestone"))
    for y in (top, top + 1):
        w.bloecke.pop((0, y, b), None)
    w.setze(0, top, b, w.b("spruce_door", facing="south", half="lower", hinge="left", open=False, powered=False))
    w.setze(0, top + 1, b, w.b("spruce_door", facing="south", half="upper", hinge="left", open=False, powered=False))
    kuppel(w, lambda x, y, z, t: w.b("oxidized_cut_copper" if (x + z) % 4 else "weathered_cut_copper"), 0, 0,
           top + 4, b + 0.6, form="rund", spitze=None)
    mx = -int(3 + s)
    for y in range(top, top + 8 + int(2 * s)):
        w.setze(mx, y, mx, w.b("iron_bars"))
    w.setze(mx, top + 8 + int(2 * s), mx, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    ax = int(3 + s)
    for y in range(top, top + 5):
        w.setze(ax, y, -ax, w.b("spruce_fence"))
    for dx, dz, f in ((1, 0, "east"), (-1, 0, "west"), (0, 1, "south"), (0, -1, "north")):
        w.setze(ax + dx, top + 5, -ax + dz, w.b("spruce_trapdoor", facing=f, half="bottom", open=True, powered=False,
                                                waterlogged=False))
    w.setze(ax, top + 5, -ax, w.b("spruce_fence"))
    w.setze(ax, top + 6, -ax, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for x in range(-int(3 + s), int(4 + s)):
        for z in (-int(3 + s), int(3 + s)):
            if w.frei(x, top, z):
                w.setze(x, top, z, w.b("iron_bars"))
    pts = []
    y = top - 1
    x, z = 0, int(4 + s)
    rich = 1
    while y > 1:
        for _ in range(int(3 + 2 * s)):
            d = math.hypot(x, z)
            if d > R - 1:
                break
            z += 1
            x += rich
            y -= 1
            for dx in (0, 1):
                w.setze(x + dx, y, z, w.b("cobblestone"))
                for yy in range(y + 1, y + 3):
                    w.bloecke.pop((x + dx, yy, z), None)
            pts.append((x, y, z))
        rich = -rich
        if math.hypot(x, z) > R - 1:
            break
    bestaeuben(w, 0.5)
    return w


def eingefrorener_kraken(seed, g=2):
    """Eingefrorener Krake: aus einer gefrorenen Meeresfläche ragen die gekrümmten, roten Fangarme eines
    riesigen Kraken mit hellen Saugnäpfen, sein Kopf mit einem riesigen Auge ist halb im Eis eingeschlossen;
    um die Arme liegt aufgebrochenes Packeis."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    rn = Rauschen(w, 5)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) <= R + 2 * rn(x, 0, z):
                w.setze(x, -2, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("ice"))
                v = rn(x, 3, z)
                w.setze(x, 0, z, w.b("snow_block" if v > 0.55 else "packed_ice" if v > 0.3 else "ice"))
    haut = M(w, [("red_terracotta", 3), ("red_nether_bricks", 1), ("brown_terracotta", 1)])
    rng = w.rng
    n = 5 + g
    for i in range(n):
        a = i / n * 2 * math.pi + rng.random() * 0.4
        d0 = 3 * s + 2
        L = (10 + rng.random() * 5) * s + 3
        p0 = (math.cos(a) * d0, -2, math.sin(a) * d0)
        p1 = (math.cos(a) * (d0 + L * 0.5), L * 0.7, math.sin(a) * (d0 + L * 0.5))
        p2 = (math.cos(a + 0.5) * (d0 + L * 0.9), L * 0.9, math.sin(a + 0.5) * (d0 + L * 0.9))
        p3 = (math.cos(a + 0.9) * (d0 + L * 0.6), L * 0.6 + rng.random() * 3, math.sin(a + 0.9) * (d0 + L * 0.6))
        pts = bez(p0, p1, p2, p3)
        rohr(w, pts, 1.6 * s + 0.6, 0.5,
             mat=lambda x, y, z, *aa: w.b("pink_terracotta") if (x * 3 + y * 5 + z * 7) % 11 == 0 else haut(x, y, z))
        kx, kz = round(p0[0]), round(p0[2])
        for _ in range(4):
            dx, dz = int((rng.random() - 0.5) * 6 * s), int((rng.random() - 0.5) * 6 * s)
            kugel(w, kx + dx, 1, kz + dz, 0.8 + rng.random() * s, w.b("packed_ice"), ueber=False)
    kugel(w, 0, 0, 0, 4 * s + 2.5, lambda x, y, z: haut(x, y, z), ry=5 * s + 3)
    for sz in (-1, 1):
        ex, ey, ez = 0, round(1.5 * s + 1), sz * round(3.5 * s + 2.2)
        kugel(w, ex, ey, ez, 0.9 * s + 0.6, w.b("yellow_concrete"))
        w.setze(ex, ey, ez + sz, w.b("black_concrete"))
        w.setze(ex + 1, ey, ez + sz, w.b("black_concrete"))
    for x in range(-int(5 * s + 4), int(5 * s + 5)):
        for z in range(-int(5 * s + 4), int(5 * s + 5)):
            d = math.hypot(x, z)
            if d < 5 * s + 4 and rn(x, 9, z) > 0.45:
                for y in range(1, int(2 + s)):
                    w.setze(x, y, z, w.b("ice"), False)
    return w


def holzfaellerlager(seed, g=1):
    """Holzfällerlager im Schnee: eine Blockhütte mit rauchendem Kamin, aufgeschichtete Stammstapel, Baumstümpfe,
    Hackklotz mit Axt, ein Schlitten voller Stämme und ein dichter Kranz verschneiter Tannen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 7)
    zellen = schnee(w, R, 0.3)
    rng = w.rng
    blockhaus(w, 0, -int(R * 0.2), int(6 * s + 5) | 1, int(4 * s + 5) | 1, 1, tuer_s="south")
    for k in range(2 + g):
        x0, z0 = -int(R * 0.55) + k * 6, int(R * 0.35)
        hoehe = 2 + k % 2 + g // 2
        for y in range(hoehe):
            for z in range(z0 - (hoehe - y), z0 + (hoehe - y) + 1):
                for x in range(x0, x0 + 5):
                    w.setze(x, 1 + y, z, w.b("spruce_log" if (z + y) % 3 else "stripped_spruce_log", axis="x"))
    for _ in range(5 + 3 * g):
        a = rng.random() * 6.28
        d = R * (0.35 + rng.random() * 0.45)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if w.frei(x, 1, z):
            y = zellen.get((x, z), 0) + 1
            w.setze(x, y, z, w.b("spruce_log", axis="y"))
            w.setze(x, y + 1, z, w.b("snow", layers=2))
    cx, cz = int(R * 0.4), int(R * 0.05)
    w.setze(cx, 1, cz, w.b("stripped_spruce_wood", axis="y"))
    w.setze(cx, 2, cz, w.b("tripwire_hook", facing="north", attached=False, powered=False))
    w.setze(cx + 2, 1, cz, w.b("grindstone", face="floor", facing="north"))
    for x in range(cx + 3, cx + 8):
        for z in (cz + 3, cz + 5):
            w.setze(x, 1, z, platte(w, "spruce", "bottom"))
        w.setze(x, 2, cz + 4, w.b("spruce_log", axis="x"))
    w.setze(cx + 8, 2, cz + 3, treppe(w, "spruce", "west"))
    w.setze(cx + 8, 2, cz + 5, treppe(w, "spruce", "west"))
    fichtenrand(w, zellen, R, 10 + 6 * g, seed, innen=0.72, H=(10, 18))
    bestaeuben(w, 0.6)
    return w


def eishenge(seed, g=2):
    """Eis-Steinkreis: ein Ring aus Monolithen aus blauem Eis mit Decksteinen aus Packeis, in den Pfeilern
    leuchtende Frostrunen, in der Mitte ein Altar mit Seelenlaterne auf einem Spiralmuster im Schnee."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = schnee(w, R, 0.15)
    n = 8 + 2 * g
    Rr = R * 0.6
    H = int(5 * s + 4)
    for i in range(n):
        a = i / n * 2 * math.pi
        cx, cz = math.cos(a) * Rr, math.sin(a) * Rr
        tx, tz = -math.sin(a), math.cos(a)
        bb = max(1, int(s + 0.6))
        for y in range(1, H + 1):
            for k in range(-bb, bb + 1):
                for dd in (0, 1) if s > 0.9 else (0,):
                    x = round(cx + tx * k + math.cos(a) * dd)
                    z = round(cz + tz * k + math.sin(a) * dd)
                    rune = k == 0 and y in (H // 2, H // 2 + 1) and dd == 0
                    w.setze(x, y, z, w.b("light_blue_glazed_terracotta", facing="north") if rune else
                            w.b("blue_ice" if (y + k) % 4 else "packed_ice"))
        a2 = (i + 0.5) / n * 2 * math.pi
        if i % 2 == 0:
            for j in range(-4, 5):
                aa = a + (a2 - a) * 2 * (j + 4) / 8
                x, z = round(math.cos(aa) * Rr), round(math.sin(aa) * Rr)
                w.setze(x, H + 1, z, w.b("packed_ice"))
                if s > 0.9:
                    w.setze(x, H + 2, z, w.b("snow_block"))
    for k in range(int(Rr * 8)):
        t = k / (Rr * 8)
        ang = t * 4 * math.pi
        rr = t * (Rr - 3)
        x, z = round(math.cos(ang) * rr), round(math.sin(ang) * rr)
        w.setze(x, zellen.get((x, z), 0), z, w.b("packed_ice"))
    for x in (-1, 0, 1):
        for z in (-1, 0, 1):
            w.setze(x, 1, z, w.b("chiseled_quartz_block" if x == z == 0 else "quartz_slab", type="bottom",
                                 waterlogged=False) if not (x == z == 0) else w.b("chiseled_quartz_block"))
    w.setze(0, 2, 0, w.b("soul_lantern", hanging=False, waterlogged=False))
    bestaeuben(w, 0.3)
    return w


def schneekugel(seed, g=1):
    """Riesen-Schneekugel: eine riesige Glaskugel auf einem gedrechselten Holzsockel mit Goldband; darin ein
    verschneites Miniaturdorf mit Hütte, Tannen, Laterne und schwebenden Schneeflocken."""
    w = _neu(seed)
    s = S[g]
    Rk = 6 * s + 5
    sock = int(2 + s * 1.5)
    rb = Rk * 0.85
    for y in range(0, sock + 1):
        rr = rb + 1.2 - (0.8 if y in (0, sock) else 0) + (0.5 if y == sock // 2 else 0)
        for x in range(-int(rr) - 1, int(rr) + 2):
            for z in range(-int(rr) - 1, int(rr) + 2):
                d = math.hypot(x, z)
                if d <= rr:
                    if y == sock // 2 and d > rr - 1.2:
                        blk = w.b("gold_block")
                    elif d > rr - 1.5:
                        blk = w.b("dark_oak_planks")
                    else:
                        blk = w.b("stripped_dark_oak_wood", axis="y")
                    w.setze(x, y, z, blk)
    cy = sock + Rk * 0.55
    for x in range(-int(Rk) - 1, int(Rk) + 2):
        for y in range(sock + 1, int(cy + Rk) + 2):
            for z in range(-int(Rk) - 1, int(Rk) + 2):
                d = math.sqrt(x * x + (y - cy) ** 2 + z * z)
                if Rk - 1.0 < d <= Rk and y > sock:
                    w.setze(x, y, z, w.b("glass"))
                elif d <= Rk - 1.0 and y == sock + 1:
                    w.setze(x, y, z, w.b("snow_block"))
    blockhaus(w, 0, 0, max(3, int(2 * s + 3)), max(3, int(1.5 * s + 3)), sock + 2, H=max(2, int(s + 2)),
              tuer_s="south", schorn=s > 0.9)
    rng = w.rng
    for k in range(3 + g):
        a = k / (3 + g) * 2 * math.pi + 0.4
        d = Rk * 0.55
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if math.hypot(x, z) < Rk - 2:
            fichte(w, x, sock + 2, z, seed + k, min(Rk * 0.9, 4 + rng.random() * 4 * s))
    w.setze(2, sock + 2, int(Rk * 0.4), w.b("dark_oak_fence"))
    w.setze(2, sock + 3, int(Rk * 0.4), w.b("lantern", hanging=False, waterlogged=False))
    for _ in range(int(14 * s + 6)):
        x, y, z = (rng.random() - 0.5) * 1.5 * Rk, sock + 4 + rng.random() * Rk, (rng.random() - 0.5) * 1.5 * Rk
        if math.sqrt(x * x + (y - cy) ** 2 + z * z) < Rk - 1.8 and w.frei(round(x), round(y), round(z)):
            w.setze(round(x), round(y), round(z), w.b("white_stained_glass"))
    for x in range(-int(rb) - 3, int(rb) + 4):
        for z in range(-int(rb) - 3, int(rb) + 4):
            if math.hypot(x, z) <= rb + 3:
                w.setze(x, -1, z, w.b("snow_block"))
    return w


def eiszapfenhoehle(seed, g=2):
    """Eiszapfen-Höhle: eine Gletscherwand mit einem riesigen Höhlentor, von dessen Rand Vorhänge aus
    meterlangen Eiszapfen hängen; drinnen ein gefrorener Teich, Eissäulen und blau schimmerndes Licht."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 5)
    zellen = schnee(w, R, 0.2)
    H = int(9 * s + 7)
    e = eis(w)
    hz = -int(R * 0.15)
    for x in range(-R, R + 1):
        for z in range(-R, hz + 1):
            if math.hypot(x, z) > R + 1:
                continue
            h = int(H * min(1, (hz - z + 2) / 4) + rn(x, 0, z) * 3)
            for y in range(1, h + 1):
                w.setze(x, y, z, w.b("snow_block") if y >= h - 1 else e(x, y, z))
    tb, th = 4 * s + 3, 6 * s + 4
    for x in range(-int(tb) - 1, int(tb) + 2):
        for y in range(1, int(th) + 2):
            if (x / tb) ** 2 + ((y - 0.5) / th) ** 2 <= 1:
                for z in range(hz - int(R * 0.6), hz + 1):
                    sx = tb * (0.6 + 0.4 * (z - hz + R * 0.6) / (R * 0.6))
                    if (x / sx) ** 2 + ((y - 0.5) / th) ** 2 <= 1:
                        w.bloecke.pop((x, y, z), None)
    rng = w.rng
    for x in range(-int(tb), int(tb) + 1):
        for z in range(hz - int(R * 0.5), hz + 1):
            yd = None
            for y in range(int(th) + 2, 1, -1):
                if not w.frei(x, y, z) and w.frei(x, y - 1, z):
                    yd = y
                    break
            if yd and rng.random() < (0.5 if z == hz else 0.18):
                L = int(1 + rng.random() * th * (0.6 if z == hz else 0.4))
                for k in range(1, L + 1):
                    if yd - k > 1:
                        w.setze(x, yd - k, z, w.b("ice" if k < L else "packed_ice"))
    for x in range(-int(tb * 0.6), int(tb * 0.6) + 1):
        for z in range(hz - int(R * 0.45), hz - 2):
            w.setze(x, 0, z, w.b("ice"))
    for k in range(3):
        x, z = int((k - 1) * tb * 0.5), hz - int(R * 0.35)
        for y in range(1, int(th)):
            if w.frei(x, y, z):
                w.setze(x, y, z, w.b("blue_ice"))
        w.setze(x, 0, z - 1, w.b("sea_lantern"))
    bestaeuben(w, 0.3)
    return w


def frostschmiede(seed, g=1):
    """Frostschmiede: eine offene Schmiede unter einem steilen Dach auf Steinpfeilern, mit Esse und
    Seelenfeuer, Amboss, Schleifstein, Löschbecken und auf Gestellen ausgestellten Klingen aus Eis;
    dahinter ein mächtiger Schlot aus Tiefenschiefer."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = schnee(w, R, 0.2)
    B, T = int(6 * s + 7) | 1, int(4 * s + 6) | 1
    x0, z0 = -B // 2, -T // 2
    x1, z1 = x0 + B - 1, z0 + T - 1
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, 0, z, w.b("polished_andesite" if (x + z) % 2 else "andesite"))
            for y in range(1, 6):
                w.bloecke.pop((x, y, z), None)
    for x in (x0, x1):
        for z in (z0, z1):
            for y in range(1, 5):
                w.setze(x, y, z, w.b("cobbled_deepslate" if y % 2 else "deepslate_bricks"))
    for x in range(x0, x1 + 1):
        w.setze(x, 4, z0, w.b("stripped_spruce_log", axis="x"))
        w.setze(x, 4, z1, w.b("stripped_spruce_log", axis="x"))
    satteldach(w, x0, z0, x1, z1, 5, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]), first_x=True, ue=1,
               giebel=M(w, [("spruce_planks", 2), ("cobbled_deepslate", 1)]), traufe="spruce", steil=2)
    for x in range(x0 + 1, x0 + 4):
        for z in range(z0, z0 + 3):
            for y in range(1, 3):
                w.setze(x, y, z, w.b("deepslate_bricks"))
    w.setze(x0 + 2, 3, z0 + 1, w.b("soul_campfire", lit=True, signal_fire=False, facing="south", waterlogged=False))
    for y in range(3, 14 + int(4 * s)):
        for dx in (0, 1):
            for dz in (0, 1):
                w.setze(x0 + 1 + dx, y, z0 - 1 + dz, w.b("cobbled_deepslate" if (y + dx) % 3 else "deepslate_bricks"))
    w.setze(x0 + 1, 14 + int(4 * s), z0 - 1, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                    waterlogged=False))
    w.setze(0, 1, 0, w.b("anvil", facing="east"))
    w.setze(2, 1, z0 + 1, w.b("blast_furnace", facing="south", lit=True))
    w.setze(3, 1, z0 + 1, w.b("grindstone", face="floor", facing="south"))
    w.setze(x1 - 1, 1, z0 + 1, w.b("smithing_table"))
    for x in range(x1 - 3, x1):
        w.setze(x, 1, z1 - 1, w.b("water", level=0))
        w.setze(x, 0, z1 - 1, w.b("deepslate_bricks"))
    for z in (z1 - 2, z1):
        for x in range(x1 - 3, x1):
            w.setze(x, 1, z, w.b("cobbled_deepslate_slab", type="bottom", waterlogged=False))
    for k in range(3):
        x = x0 + 2 + k * 2
        z = z1 + 2
        w.setze(x, 1, z, w.b("spruce_fence"))
        for y in range(2, 4 + k % 2):
            w.setze(x, y, z, w.b("blue_ice"))
        w.setze(x - 1, 2, z, w.b("prismarine_wall"))
        w.setze(x + 1, 2, z, w.b("prismarine_wall"))
    laterne(w, 0, 4, 0, kette=1, seele=True)
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            zellen[(x, z)] = 0
    fichtenrand(w, zellen, R, 3 + 2 * g, seed, innen=0.8)
    bestaeuben(w, 0.6)
    return w


EISREICH3 = {
    "nordlichtbogen": ("Nordlicht-Bögen", nordlichtbogen),
    "hundeschlitten": ("Hundeschlitten-Station", hundeschlitten),
    "pinguinkolonie": ("Pinguinkolonie", pinguinkolonie),
    "walknochenhuette": ("Walknochen-Hütte", walknochenhuette),
    "verschneite_stadt": ("Verschneite Ruinenstadt", verschneite_stadt),
    "gletscherspalte": ("Gletscherspalte mit Hängebrücke", gletscherspalte),
    "schneekapelle": ("Schneekapelle", schneekapelle),
    "frostriese": ("Frostriese", frostriese),
    "eislaufsee": ("Eislaufsee mit Pavillon", eislaufsee),
    "thermalquellen": ("Heiße Quellen mit Badehaus", thermalquellen),
    "kotalager": ("Kota-Zeltlager", kotalager),
    "eisbaerhoehle": ("Eisbärenhöhle", eisbaerhoehle),
    "frostmagierturm": ("Frostmagier-Turm", frostmagierturm),
    "wetterwarte": ("Gipfel-Wetterwarte", wetterwarte),
    "eingefrorener_kraken": ("Eingefrorener Krake", eingefrorener_kraken),
    "holzfaellerlager": ("Holzfällerlager im Schnee", holzfaellerlager),
    "eishenge": ("Eis-Steinkreis", eishenge),
    "schneekugel": ("Riesen-Schneekugel", schneekugel),
    "eiszapfenhoehle": ("Eiszapfen-Höhle", eiszapfenhoehle),
    "frostschmiede": ("Frostschmiede", frostschmiede),
}

"""Bienenstadt II – zwanzig weitere Bauten rund um Bienen und Honig: Imkerhof, Honigschleuder-Werkstatt,
Wabenkuppel, Kerzenzieherei, Honigsee, Pollenlager, Brutwaben-Kinderstube, Nektar-Fontäne, Lavendelfeld,
Waben-Leuchtturm, Sechseck-Platz mit Uhrturm, Strohkorb-Siedlung, Honigbahn, Sonnenblumen-Allee, Insektenhotel,
Hummel-Flugplatz, Gelée-Kammer, Tanzbühne der Bienen, Honigtopf-Haus und Wabentor."""

from __future__ import annotations

import math

from fantasie2 import fenster_rund, form, garten, tuer_rein
from feinbau import Dachmat, Mix, fachwerk, kegeldach, kram, laterne, mauer, platte, satteldach, stamm, treppe, tuer, \
    zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr

S = [0.6, 1.0, 1.6, 2.5]
W3 = math.sqrt(3) / 2


def M(w, liste, zelle=1.4, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def honig(w):
    return M(w, [("honeycomb_block", 3), ("yellow_terracotta", 1), ("orange_terracotta", 1)])


def im_hex(x, z, r):
    return abs(z) <= r * W3 and abs(x) * W3 + abs(z) / 2 <= r * W3


def hexprisma(w, cx, cz, y0, y1, r, mat, hohl=True, deckel=True):
    zellen = []
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            if not im_hex(x - cx, z - cz, r):
                continue
            rand = not im_hex(x - cx, z - cz, r - 1.0)
            for y in range(y0, y1 + 1):
                if rand or not hohl or (deckel and y in (y0, y1)):
                    w.setze(x, y, z, mat(x, y, z) if callable(mat) else mat)
                    if rand:
                        zellen.append((x, y, z))
                else:
                    w.bloecke.pop((x, y, z), None)
    return zellen


def hexpflaster(w, R, mat_a="yellow_terracotta", mat_b="honeycomb_block"):
    zellen = []
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            if math.hypot(x, z) <= R:
                q = round((x * 2 / 3) / 2.2)
                rr = round((-x / 3 + W3 * 1.15 * z) / 2.2)
                w.setze(x, 0, z, w.b(mat_a if (q + rr) % 3 else mat_b))
                w.setze(x, -1, z, w.b("dirt"))
                zellen.append((x, z))
    return zellen


def biene(w, x, y, z, s=1.0):
    from skulptur import Skulptur, ell
    S_ = Skulptur(w, s)
    S_.mat("g", lambda X, Y, Z, lx, ly, lz: w.b("yellow_concrete" if int(lx * 1.5 + 9) % 2 else "black_concrete"))
    S_.mat("f", w.b("white_stained_glass"))
    S_.mat("d", w.b("black_concrete"))
    S_.plus(ell(0, 0, 0, 1.8, 1.1, 1.1), "g")
    S_.plus(ell(1.9, 0.2, 0, 0.8, 0.8, 0.8), "d")
    S_.plus(ell(-0.2, 1.2, 1.2, 0.9, 0.2, 1.2), "f")
    S_.plus(ell(-0.2, 1.2, -1.2, 0.9, 0.2, 1.2), "f")
    S_.rendern((-3, -2, -3), (3, 2, 3), versatz=(x + 0.5, y, z + 0.5), ueberschreiben=False)


def stiel_bluete(w, x, z, H, farbe, R=2.0):
    rohr(w, bez((x, 0, z), (x, H * 0.6, z), (x, H, z)), 0.5, 0.4, w.b("lime_terracotta"))
    for k in range(6):
        a = k / 6 * 6.283
        for i in range(1, int(R) + 2):
            w.setze(round(x + math.cos(a) * i), round(H + i * 0.25), round(z + math.sin(a) * i), w.b(farbe), False)
    w.setze(x, H + 1, z, w.b("yellow_concrete"))


# ============================================================================ Bauten

def imkerhof(seed, g=1):
    """Imkerhof: ein Fachwerkhaus mit Strohdach, davor Reihen bunter Bienenkästen auf Holzböcken, ein
    Schleuderschuppen, Lavendelbeete und Bienen in der Luft."""
    from himmelsstadt2 import haus
    w = _neu(seed)
    s = S[g]
    zl = garten(w, 12 * s + 4, seed=seed, baeume=1)
    haus(w, -int(4 * s), -int(4 * s), 7, 6, 1, "fachwerk", geschosse=2, tuer_s="south")
    farben = ["yellow_terracotta", "light_blue_terracotta", "white_terracotta", "lime_terracotta", "pink_terracotta"]
    for k in range(3 + g * 2):
        x, z = int(2 * s) + (k % 3) * 3, int(2 * s) + (k // 3) * 3
        w.setze(x, 1, z, zaun(w, "spruce"))
        w.setze(x, 2, z, w.b("beehive", facing="south", honey_level=5))
        w.setze(x, 3, z, w.b(farben[k % 5]))
    for (x, z) in zl:
        if x < -int(6 * s) and z > 0 and w.frei(x, 1, z) and (x + z) % 2 == 0:
            w.setze(x, 1, z, w.b("allium"))
    biene(w, int(5 * s), int(6 * s) + 3, int(3 * s), max(0.6, s * 0.7))
    return w


def honigschleuder(seed, g=1):
    """Honigschleuder-Werkstatt: ein offener Schuppen mit einer großen Kupfer-Schleudertrommel, Honigrinnen,
    Fässern und Gläsern, durch die Fenster scheint goldenes Licht."""
    w = _neu(seed)
    s = S[g]
    garten(w, 10 * s + 3, seed=seed)
    B, T = int(4 * s + 3), int(3 * s + 2)
    fachwerk(w, -B, -T, B, T, 1, 4, M(w, [("yellow_terracotta", 2), ("white_terracotta", 1)]), holz="spruce",
             abstand=2)
    for y in range(1, 4):
        for x in range(-2, 3):
            w.bloecke.pop((x, y, T), None)
    satteldach(w, -B, -T, B, T, 5, Dachmat(w, ["mcw:orange_terracotta", "spruce"]), first_x=True, traufe="spruce")
    r = int(1.5 * s + 1)
    for y in range(1, 4):
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                if r - 0.8 < math.hypot(x, z) <= r + 0.3:
                    w.setze(x, y, z - 1, w.b("waxed_cut_copper"))
    w.setze(0, 4, -1, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for x in range(r + 1, B):
        w.setze(x, 1, -1, w.b("honey_block"))
    kram(w, -B + 1, 1, -T + 1, 4)
    return w


def wabenkuppel(seed, g=2):
    """Wabenkuppel: eine große Kuppel aus sechseckigen Wachswaben, manche verglast, manche mit Honig gefüllt,
    darunter eine Halle mit Säulen aus Honigblöcken."""
    w = _neu(seed)
    s = S[g]
    hexpflaster(w, 10 * s + 4)
    R = 8 * s + 3

    def kuppel(X, Y, Z):
        import numpy as np
        return X ** 2 + (Y - 1) ** 2 + Z ** 2 <= R * R

    def mat(x, y, z):
        a = math.atan2(z, x)
        b = math.atan2(y, math.hypot(x, z))
        q, r = round(a * R / 2.2), round(b * R / 1.9 + (round(a * R / 2.2) % 2) * 0.5)
        h = (q * 7 + r * 3) % 9
        return w.b("glass" if h == 0 else "honey_block" if h == 1 else "honeycomb_block")
    zellen = form(w, kuppel, (-int(R) - 1, 1, -int(R) - 1), (int(R) + 1, int(R) + 1, int(R) + 1), mat)
    for k in range(6):
        a = k / 6 * 6.283
        x, z = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        for y in range(1, int(R * 0.8)):
            w.setze(x, y, z, w.b("honey_block"))
    for y in range(1, 4):
        for x in range(-1, 2):
            w.bloecke.pop((x, y, int(R)), None)
            w.bloecke.pop((x, y, int(R) - 1), None)
    return w


def kerzenzieherei(seed, g=1):
    """Kerzenzieherei: ein Wachshaus mit runden Fenstern, an Gestellen hängen frisch gezogene Kerzen in langen
    Reihen, Wachskessel blubbern, auf dem Dach leuchtet eine Riesenkerze."""
    w = _neu(seed)
    s = S[g]
    garten(w, 10 * s + 3, seed=seed)
    r = int(3 * s + 2)
    zellen = hexprisma(w, 0, 0, 1, int(5 * s) + 3, r, honig(w))
    tuer(w, 0, 2, int(r * W3), "south", holz="spruce", laternen=True)
    for x in (-1, 0, 1):
        for y in (2, 3):
            w.bloecke.pop((0, y, int(r * W3)), None)
    yt = int(5 * s) + 4
    for y in range(yt, yt + int(4 * s) + 2):
        w.setze(0, y, 0, w.b("white_concrete"))
    w.setze(0, yt + int(4 * s) + 2, 0, w.b("shroomlight"))
    for k in range(2):
        x = r + 3 + k * 3
        for z in range(-2, 3):
            w.setze(x, 4, z, w.b("spruce_fence", north=True, south=True, east=False, west=False, waterlogged=False))
            w.setze(x, 3, z, w.b("candle", candles=1, lit=False, waterlogged=False)) if z % 2 == 0 else None
        for z in (-2, 2):
            for y in range(1, 4):
                w.setze(x, y, z, zaun(w, "spruce"))
    w.setze(-r - 2, 1, 0, w.b("cauldron"))
    w.setze(-r - 2, 0, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


def honigsee(seed, g=2):
    """Honigsee: ein goldener See aus Honig zwischen Riesenblumen, auf dem ein Floß aus Wachsplatten treibt, ein
    Steg mit Wabenlaternen und ein Honigfall aus einem Felsen."""
    w = _neu(seed)
    s = S[g]
    zl = garten(w, 13 * s + 4, seed=seed)
    R = 8 * s + 3
    for (x, z) in zl:
        if math.hypot(x, z - 1) < R:
            w.setze(x, 0, z, w.b("honey_block"))
            w.setze(x, -1, z, w.b("honeycomb_block"))
            w.bloecke.pop((x, 1, z), None)
    for x in range(-2, 3):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("yellow_terracotta"))
    for z in range(int(R), int(R + 4)):
        w.setze(0, 1, z, w.b("spruce_planks"))
    for k in range(3 + g):
        a = k / (3 + g) * 6.283
        x, z = round(math.cos(a) * (R + 2)), round(math.sin(a) * (R + 2))
        stiel_bluete(w, x, z, int(6 * s + 4), ["pink_concrete", "white_concrete", "orange_concrete",
                                               "magenta_concrete"][k % 4], 2 * s + 1)
    for y in range(1, int(5 * s) + 3):
        for dx in range(-1, 2):
            w.setze(-int(R) - 1 + dx, y, 0, w.b("stone") if y < int(5 * s) + 2 or dx else w.b("honey_block"))
    return w


def pollenlager(seed, g=1):
    """Pollenlager: eine Halle aus Wabenwänden, in der Pollen in großen Körben aus Weidengeflecht gelagert werden,
    gelb, orange und weiß, Schütten und Säcke davor."""
    w = _neu(seed)
    s = S[g]
    hexpflaster(w, 10 * s + 3)
    r = int(4 * s + 3)
    hexprisma(w, 0, 0, 1, int(4 * s) + 3, r, honig(w))
    for y in range(1, 4):
        for x in range(-1, 2):
            w.bloecke.pop((x, y, int(r * W3)), None)
    for k in range(6):
        a = k / 6 * 6.283
        x, z = round(math.cos(a) * r * 0.5), round(math.sin(a) * r * 0.5)
        for y in range(1, 3):
            w.setze(x, y, z, w.b(["yellow_wool", "orange_wool", "white_wool"][k % 3]))
    for k in range(4):
        w.setze(r + 2, 1, -2 + k, w.b("hay_block", axis="y"))
        w.setze(r + 2, 2, -1 + k // 2, w.b("yellow_wool")) if k % 2 else None
    return w


def kinderstube(seed, g=1):
    """Brutwaben-Kinderstube: eine Wand aus großen Brutwaben mit gewölbten Wachsdeckeln, in einigen schauen kleine
    Bienenlarven heraus, Ammenbienen mit Honigtöpfen davor."""
    w = _neu(seed)
    s = S[g]
    hexpflaster(w, 10 * s + 3)
    R = 2.2 * s + 1
    n = 3 + g
    for i in range(n):
        for j in range(n):
            cx = (i - (n - 1) / 2) * R * 1.8
            cy = 2 + j * R * 1.6 + (i % 2) * R * 0.8
            for dx in range(-int(R) - 1, int(R) + 2):
                for dy in range(-int(R) - 1, int(R) + 2):
                    if im_hex(dx, dy, R):
                        rand = not im_hex(dx, dy, R - 1)
                        w.setze(round(cx + dx), round(cy + dy), 0, w.b("honeycomb_block" if rand else
                                                                         "white_concrete" if (i + j) % 3 else
                                                                         "honey_block"))
                        if not rand:
                            w.setze(round(cx + dx), round(cy + dy), 1, w.b("white_wool" if (i + j) % 3 else
                                                                             "yellow_concrete"), False)
    biene(w, 0, 2, int(4 * s) + 3, max(0.6, s * 0.7))
    return w


def nektarfontaene(seed, g=1):
    """Nektar-Fontäne: aus einer riesigen Blüte auf einem Wabensockel sprudelt goldener Nektar in drei Schalen
    hinab, Bienen trinken am Rand."""
    w = _neu(seed)
    s = S[g]
    hexpflaster(w, 9 * s + 3)
    for k, (r, y) in enumerate(((4 * s + 2, 1), (3 * s + 1.5, int(3 * s) + 2), (2 * s + 1, int(6 * s) + 3))):
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                if im_hex(x, z, r):
                    rand = not im_hex(x, z, r - 1)
                    w.setze(x, y, z, w.b("honeycomb_block") if rand else w.b("honey_block"))
        for yy in range(1, y):
            w.setze(0, yy, 0, w.b("yellow_terracotta"))
    yt = int(6 * s) + 4
    for k in range(6):
        a = k / 6 * 6.283
        for i in range(1, int(2 * s) + 2):
            w.setze(round(math.cos(a) * i), yt + i // 2, round(math.sin(a) * i), w.b("pink_concrete"))
    w.setze(0, yt, 0, w.b("yellow_concrete"))
    biene(w, int(4 * s) + 2, 3, 0, max(0.5, s * 0.6))
    return w


def lavendelfeld(seed, g=1):
    """Lavendelfeld: lange violette Lavendelreihen ziehen sich über einen Hang, dazwischen stehen bunte Bienenkästen,
    ein Feldweg führt zu einem kleinen Steinhaus mit Lavendel-Trockenboden."""
    from himmelsstadt2 import haus
    w = _neu(seed)
    s = S[g]
    zl = garten(w, 13 * s + 4, seed=seed, dichte=0.1, baeume=0)
    for (x, z) in zl:
        if z % 3 != 0 and abs(x) < 13 * s and z < 6 * s and w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("allium") if (x + z) % 2 else w.b("purple_wool") if (x * z) % 5 == 0 else
                    w.b("lilac", half="lower"))
            if w.P.name(w.bloecke[(x, 1, z)]) == "minecraft:lilac":
                w.setze(x, 2, z, w.b("lilac", half="upper"))
    for k in range(4 + g):
        x = int(-10 * s) + k * int(5 * s)
        w.setze(x, 1, 0, w.b("beehive", facing="south", honey_level=3))
    haus(w, 0, int(9 * s), 6, 5, 1, "stein", geschosse=1, tuer_s="north")
    return w


def wabenleuchtturm(seed, g=2):
    """Waben-Leuchtturm: ein sechseckiger Turm aus Honigwaben mit umlaufenden Balkonen, oben ein Laternenhaus mit
    gelb leuchtenden Waben, das den Bienen den Heimweg zeigt."""
    w = _neu(seed)
    s = S[g]
    hexpflaster(w, 8 * s + 3)
    r = 2.6 * s + 1.5
    H = int(14 * s + 6)
    hexprisma(w, 0, 0, 1, H, r, honig(w), deckel=False)
    for y in range(4, H, int(4 * s) + 2):
        for x in range(-int(r) - 2, int(r) + 3):
            for z in range(-int(r) - 2, int(r) + 3):
                if im_hex(x, z, r + 1.2) and not im_hex(x, z, r):
                    w.setze(x, y, z, w.b("spruce_planks"))
    hexprisma(w, 0, 0, H + 1, H + 3, r, lambda *a: w.b("yellow_stained_glass" if (a[0] + a[2]) % 2 else
                                                       "ochre_froglight", **({} if (a[0] + a[2]) % 2 else
                                                                             {"axis": "y"})), hohl=True)
    w.setze(0, H + 2, 0, w.b("ochre_froglight", axis="y"))
    kegeldach(w, 0, 0, H + 4, int(r), Dachmat(w, ["mcw:orange_terracotta", "brick"]), form="kegel", eckig=True)
    tuer(w, 0, 1, int(r * W3), "south", holz="spruce")
    return w


def sechseckplatz(seed, g=2):
    """Sechseck-Platz mit Uhrturm: ein gepflasterter Platz aus Sechseckplatten, in der Mitte ein Uhrturm mit
    Wabenzifferblatt, ringsum Bänke, Blumenkübel und Bienenlaternen."""
    w = _neu(seed)
    s = S[g]
    hexpflaster(w, 12 * s + 4)
    r = 1.8 * s + 1.2
    H = int(12 * s + 6)
    hexprisma(w, 0, 0, 1, H, r, M(w, [("yellow_terracotta", 2), ("smooth_sandstone", 1)]), hohl=False)
    zc = int(r * W3) + 1
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if abs(dx) + abs(dy) <= 3:
                w.setze(dx, H - 3 + dy, zc, w.b("white_concrete") if abs(dx) + abs(dy) < 3 else w.b("gold_block"))
    w.setze(0, H - 3, zc + 1, w.b("black_concrete"))
    w.setze(0, H - 2, zc + 1, w.b("black_concrete"))
    kegeldach(w, 0, 0, H + 1, int(r) + 1, Dachmat(w, ["mcw:orange_terracotta", "brick"]), form="glocke")
    for k in range(6):
        a = k / 6 * 6.283 + 0.5
        x, z = round(math.cos(a) * 8 * s), round(math.sin(a) * 8 * s)
        w.setze(x, 1, z, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False))
        w.setze(x + 1, 1, z, treppe(w, "spruce", "east"))
    return w


def strohkorbsiedlung(seed, g=1):
    """Strohkorb-Siedlung: eine Siedlung aus riesigen, geflochtenen Bienenkörben mit Flugloch-Türen und kleinen
    Fenstern, verbunden durch Wege aus Wabenplatten, Blumen dazwischen."""
    w = _neu(seed)
    s = S[g]
    zl = garten(w, 12 * s + 4, seed=seed)
    n = 3 + g
    for k in range(n):
        a = k / n * 6.283
        cx, cz = round(math.cos(a) * 6 * s), round(math.sin(a) * 6 * s)
        R = 2.4 * s + 1.4
        H = 4 * s + 2
        zellen = form(w, lambda X, Y, Z, cx=cx, cz=cz, R=R, H=H: ((X - cx) ** 2 + (Z - cz) ** 2) <= (R * (
            1 - ((Y - 1) / (H + 1.5)) ** 2)) ** 2 * 1.0 + 0.0 + 0 * Y, (cx - int(R) - 1, 1, cz - int(R) - 1),
                      (cx + int(R) + 1, int(H) + 2, cz + int(R) + 1),
                      lambda x, y, z: w.b("hay_block", axis="y") if y % 2 else w.b("yellow_terracotta"))
        fenster_rund(w, zellen, 2, 2, int(H - 1), licht=False)
        tuer_rein(w, cx, 1, max([z for (x, y, z) in zellen if x == cx and y <= 2] or [cz + int(R)]), "south")
    return w


def honigbahn(seed, g=2):
    """Honigbahn: eine kleine Schmalspurbahn mit Waggons voller Honigtöpfe schlängelt sich auf Holzbrücken durch
    eine Blumenwiese zu einem Wabenbahnhof mit Dach."""
    w = _neu(seed)
    s = S[g]
    zl = garten(w, 14 * s + 4, seed=seed)
    L = int(12 * s + 6)
    pts = [(x, round(3 * s * math.sin(x / (3 * s + 2)))) for x in range(-L, L + 1)]
    for (x, z) in pts:
        w.setze(x, 1, z, w.b("rail", shape="east_west", waterlogged=False))
        w.setze(x, 0, z, w.b("spruce_planks"))
    for k in range(3):
        x, z = pts[L // 2 + k * 3]
        for dz in (-1, 0, 1):
            w.setze(x, 1, z + dz, w.b("barrel", facing="up", open=False) if dz == 0 else w.b("honey_block"))
    hexprisma(w, -L - 3, 0, 1, 4, 3.5, honig(w))
    return w


def sonnenblumenallee(seed, g=1):
    """Sonnenblumen-Allee: ein Weg zwischen zwei Reihen riesiger Sonnenblumen mit schweren, nickenden Köpfen, an
    denen Bienen sammeln, Bänke und Laternen dazwischen."""
    w = _neu(seed)
    s = S[g]
    garten(w, 13 * s + 4, seed=seed, dichte=0.2)
    L = int(11 * s + 4)
    for x in range(-L, L + 1, int(3 * s) + 2):
        for sz in (-1, 1):
            z = sz * 3
            H = int((7 + (x % 3)) * s + 3)
            rohr(w, bez((x, 0, z), (x, H * 0.6, z), (x, H, z + sz)), 0.5 * s + 0.3, 0.4, w.b("green_terracotta"))
            R = 1.8 * s + 1
            for dx in range(-int(R) - 2, int(R) + 3):
                for dy in range(-int(R) - 2, int(R) + 3):
                    d = math.hypot(dx, dy)
                    if d <= R + 1.2:
                        w.setze(x + dx, H + dy, z + sz * 2, w.b("brown_concrete" if d <= R else "yellow_concrete"),
                                False)
    for x in range(-L, L + 1):
        w.setze(x, 0, 0, w.b("dirt_path"))
    return w


def insektenhotel(seed, g=1):
    """Insektenhotel: ein großes Holzregal mit Giebeldach, gefüllt mit Bambusröhren, Tannenzapfen, Ziegeln mit
    Löchern, Rinde und Stroh – ein Zuhause für Wildbienen."""
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 3, seed=seed)
    B, H = int(4 * s + 2), int(6 * s + 4)
    for x in range(-B, B + 1):
        for y in range(1, H + 1):
            rand = abs(x) == B or y in (1, H) or (y - 1) % int(2 * s + 2) == 0 or x == 0
            fach = (abs(x) // 2 + (y - 1) // int(2 * s + 2)) % 5
            w.setze(x, y, 0, w.b("spruce_log", axis="y") if rand else w.b(
                ["bamboo_block", "hay_block", "bricks", "spruce_wood", "brown_mushroom_block"][fach],
                **({"axis": "z"} if fach in (0, 1, 3) else {} if fach == 2 else
                   {"up": True, "down": True, "north": True, "south": True, "east": True, "west": True})))
            w.setze(x, y, -1, w.b("spruce_planks"))
    satteldach(w, -B, -1, B, 0, H + 1, Dachmat(w, ["dark_oak", "spruce"]), first_x=True, ue=1, traufe="spruce")
    for k in range(2):
        w.setze(-B + 1 + k * 2 * B - k * 2, 1, 2, w.b("dandelion"))
    biene(w, B + 2, H, 2, max(0.5, s * 0.5))
    return w


def hummelflugplatz(seed, g=2):
    """Hummel-Flugplatz: Landeplattformen auf großen Blütenkelchen in verschiedenen Höhen, ein Kontrollturm aus
    Waben mit Windsack und eine große Hummel im Landeanflug."""
    w = _neu(seed)
    s = S[g]
    garten(w, 13 * s + 4, seed=seed)
    for k in range(3 + g):
        a = k / (3 + g) * 6.283
        x, z = round(math.cos(a) * 7 * s), round(math.sin(a) * 7 * s)
        H = int((4 + k % 3 * 2) * s + 2)
        stiel_bluete(w, x, z, H, ["pink_concrete", "light_blue_concrete", "white_concrete", "orange_concrete"][k % 4],
                     2.4 * s + 1)
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                w.setze(x + dx, H + 1, z + dz, w.b("yellow_concrete") if (dx or dz) else w.b("ochre_froglight",
                                                                                          axis="y"))
    hexprisma(w, 0, 0, 1, int(8 * s) + 3, 2 * s + 1.2, honig(w))
    w.setze(0, int(8 * s) + 4, 0, zaun(w, "spruce"))
    w.setze(1, int(8 * s) + 4, 0, w.b("orange_wool"))
    w.setze(2, int(8 * s) + 4, 0, w.b("white_wool"))
    biene(w, int(4 * s), int(10 * s) + 4, int(4 * s), max(0.8, s))
    return w


def geleekammer(seed, g=2):
    """Gelée-Kammer: eine prachtvolle Wabenhalle mit goldenem Kuppeldach, in der Mitte ein Becken mit weiß
    schimmerndem Gelée Royale, Säulen aus Honig und Wachskerzen."""
    w = _neu(seed)
    s = S[g]
    hexpflaster(w, 10 * s + 3)
    r = 5 * s + 2.5
    hexprisma(w, 0, 0, 1, int(4 * s) + 3, r, honig(w))
    kegeldach(w, 0, 0, int(4 * s) + 4, int(r), Dachmat(w, ["mcw:yellow_terracotta", "smooth_sandstone"]),
              form="glocke", eckig=True)
    for x in range(-int(r * 0.4), int(r * 0.4) + 1):
        for z in range(-int(r * 0.4), int(r * 0.4) + 1):
            if im_hex(x, z, r * 0.4):
                w.setze(x, 1, z, w.b("white_concrete_powder" if False else "white_concrete") if not im_hex(
                    x, z, r * 0.4 - 1) else w.b("pearlescent_froglight", axis="y"))
    for y in range(1, 4):
        for x in range(-1, 2):
            w.bloecke.pop((x, y, int(r * W3)), None)
    return w


def tanzbuehne(seed, g=1):
    """Tanzbühne der Bienen: eine runde Bühne aus Wabenplatten, auf der Bienen-Figuren den Schwänzeltanz zeigen,
    ein Wegweiser-Bogen aus Blüten und Zuschauerränge aus Heuballen."""
    w = _neu(seed)
    s = S[g]
    zl = garten(w, 11 * s + 4, seed=seed)
    R = 5 * s + 2
    for x in range(-int(R), int(R) + 1):
        for z in range(-int(R), int(R) + 1):
            if math.hypot(x, z) <= R:
                w.setze(x, 1, z, w.b("honeycomb_block" if (x + z) % 2 else "yellow_terracotta"))
    for i in range(int(R * 1.5)):
        t = i / (R * 1.5)
        x = round((t - 0.5) * R * 1.4)
        z = round(math.sin(t * 6.283 * 2) * 1.5)
        w.setze(x, 2, z, w.b("black_concrete" if i % 2 else "yellow_concrete"), False)
    biene(w, 0, 3, 0, max(0.6, s * 0.7))
    for k in range(int(10 * s) + 4):
        a = math.pi * (0.2 + 0.6 * k / (int(10 * s) + 3))
        x, z = round(math.cos(a) * (R + 3)), round(math.sin(a) * (R + 3))
        w.setze(x, 1, z, w.b("hay_block", axis="y"))
    return w


def honigtopfhaus(seed, g=1):
    """Honigtopf-Haus: ein dicker, bauchiger Tontopf mit Honig, der über den Rand läuft, ist ein Wohnhaus mit
    Rundfenstern, der Deckel ist das Dach, der Honiglöffel dient als Schornstein."""
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 3, seed=seed)
    R = 4.5 * s + 1.5
    H = 7 * s + 3

    def topf(X, Y, Z):
        import numpy as np
        t = np.clip((Y - 1) / H, 0, 1)
        r = R * (0.75 + 0.35 * np.sin(np.pi * t))
        return (np.hypot(X, Z) <= r) & (Y >= 1) & (Y <= H)
    zellen = form(w, topf, (-int(R * 1.15) - 1, 1, -int(R * 1.15) - 1), (int(R * 1.15) + 1, int(H), int(R * 1.15) + 1),
                  lambda x, y, z: w.b("orange_terracotta" if y < H - 1 else "terracotta"))
    rng = w.rng
    for (x, y, z) in zellen:
        if y >= H - 2 and rng.random() < 0.35:
            L = int(rng.random() * 3) + 1
            for k in range(L):
                if (x, y - k, z) in w.bloecke:
                    w.setze(x, y - k, z, w.b("honey_block"))
    for x in range(-int(R * 0.85), int(R * 0.85) + 1):
        for z in range(-int(R * 0.85), int(R * 0.85) + 1):
            d = math.hypot(x, z)
            if d <= R * 0.85:
                w.setze(x, int(H) + 1 + (1 if d < R * 0.4 else 0), z, w.b("brown_terracotta"))
    w.setze(0, int(H) + 3, 0, w.b("brown_terracotta"))
    for k in range(int(4 * s) + 2):
        w.setze(int(R * 0.4) + k // 3, int(H) + 1 + k, 0, w.b("spruce_planks"))
    fenster_rund(w, zellen, int(4 * s), 3, int(H - 2))
    tuer_rein(w, 0, 1, max([z for (x, y, z) in zellen if x == 0 and y <= 2] or [int(R)]), "south")
    return w


def wabentor(seed, g=2):
    """Wabentor: ein prächtiges Stadttor aus zwei sechseckigen Wabentürmen mit Honig-Zinnen, verbunden durch einen
    Bogen mit Bienenwappen, davor eine Allee aus Blumenkübeln."""
    w = _neu(seed)
    s = S[g]
    hexpflaster(w, 11 * s + 4)
    D = int(5 * s + 3)
    H = int(9 * s + 5)
    for sx in (-1, 1):
        hexprisma(w, sx * D, 0, 1, H, 2.4 * s + 1.4, honig(w), deckel=True)
        kegeldach(w, sx * D, 0, H + 1, int(2.4 * s + 1.4), Dachmat(w, ["mcw:orange_terracotta", "brick"]),
                  form="kegel", eckig=True)
    for x in range(-D, D + 1):
        y = round(H * 0.7 + math.sqrt(max(0, D * D - x * x)) * 0.3)
        for dz in (-1, 0, 1):
            w.setze(x, y, dz, w.b("honeycomb_block"))
            w.setze(x, y + 1, dz, w.b("honey_block")) if dz == 0 else None
    biene(w, 0, round(H * 0.7 + D * 0.3) + 3, 0, max(0.6, s * 0.7))
    for k in range(4):
        for sx in (-1, 1):
            w.setze(sx * 3, 1, int(4 * s) + 3 + k * 3, w.b("decorated_pot", facing="north", waterlogged=False,
                                                           cracked=False))
    return w


BIENEN3 = {
    "imkerhof": ("Imkerhof", imkerhof),
    "honigschleuder": ("Honigschleuder-Werkstatt", honigschleuder),
    "wabenkuppel": ("Wabenkuppel", wabenkuppel),
    "kerzenzieherei": ("Kerzenzieherei", kerzenzieherei),
    "honigsee": ("Honigsee", honigsee),
    "pollenlager": ("Pollenlager", pollenlager),
    "kinderstube": ("Brutwaben-Kinderstube", kinderstube),
    "nektarfontaene": ("Nektar-Fontäne", nektarfontaene),
    "lavendelfeld": ("Lavendelfeld", lavendelfeld),
    "wabenleuchtturm": ("Waben-Leuchtturm", wabenleuchtturm),
    "sechseckplatz": ("Sechseck-Platz mit Uhrturm", sechseckplatz),
    "strohkorbsiedlung": ("Strohkorb-Siedlung", strohkorbsiedlung),
    "honigbahn": ("Honigbahn", honigbahn),
    "sonnenblumenallee": ("Sonnenblumen-Allee", sonnenblumenallee),
    "insektenhotel": ("Insektenhotel", insektenhotel),
    "hummelflugplatz": ("Hummel-Flugplatz", hummelflugplatz),
    "geleekammer": ("Gelée-Kammer", geleekammer),
    "tanzbuehne": ("Tanzbühne der Bienen", tanzbuehne),
    "honigtopfhaus": ("Honigtopf-Haus", honigtopfhaus),
    "wabentor": ("Wabentor", wabentor),
}

"""Kathedralen & Tempel II – zwanzig weitere Sakralbauten: Zwiebelturm-Kirche, Stabkirche, Backsteinkathedrale,
Rundkirche, Felsenkapelle, Doppelturm-Fassade, Inselkloster, Kartause, Gipfelkapelle, Oktogon-Kapelle, Tempel des
Lichts, Mondtempel, Waldkathedrale, Kristallkathedrale, Vierungsdom, Glockenspielturm, Feuertempel, Quellheiligtum,
Fischerkirche und Hallenkirche."""

from __future__ import annotations

import math

import wald2
from fantasie2 import garten
from feinbau import Dachmat, Mix, fenster, kegeldach, laterne, mauer, platte, satteldach, stamm, treppe, tuer, zaun
from flora import _neu
from himmelsstadt2 import eckturm, rundturm
from lib import einfuegen

S = [0.6, 1.0, 1.6, 2.5]


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


MAT = {"stein": [("stone_bricks", 3), ("andesite", 1), ("cracked_stone_bricks", 1)],
       "hell": [("calcite", 3), ("smooth_quartz", 1), ("diorite", 1)],
       "ziegel": [("bricks", 4), ("mud_bricks", 1)],
       "sand": [("smooth_sandstone", 3), ("cut_sandstone", 1)],
       "dunkel": [("deepslate_bricks", 2), ("polished_deepslate", 1)]}
DACH = {"schiefer": ["deepslate_tile", "cobbled_deepslate"], "kupfer": ["waxed_oxidized_cut_copper",
                                                                      "waxed_weathered_cut_copper"],
        "rot": ["mcw:red_terracotta", "brick"], "holz": ["dark_oak", "spruce"], "gold": ["gold_block"]}
GLAS = ["blue_stained_glass_pane", "red_stained_glass_pane", "yellow_stained_glass_pane", "purple_stained_glass_pane"]


def schiff(w, x0, z0, x1, z1, y0, H, st, glas=GLAS, dach="schiefer", strebe=True, steil=2):
    """Kirchenschiff entlang z (Westen = z1 vorne). Gibt Firsthöhe zurück."""
    mauer(w, x0, z0, x1, z1, y0, y0 + H, st)
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            w.setze(x, y0 - 1, z, w.b("polished_andesite") if (x + z) % 2 else w.b("smooth_stone"))
    k = 0
    for z in range(z0 + 2, z1 - 1, 3):
        for x, sname in ((x0, "west"), (x1, "east")):
            g_ = glas[k % len(glas)]
            fenster(w, x, y0 + 2, z, sname, holz="spruce", hoehe=max(2, H - 3), laeden=False, blumen=0, glas=g_,
                    bogen=True)
            if strebe:
                d = -1 if sname == "west" else 1
                for y in range(y0, y0 + H - 1):
                    w.setze(x + d, y, z + 1, st(x, y, z), False)
                    if y < y0 + H // 2:
                        w.setze(x + 2 * d, y, z + 1, st(x, y, z), False)
            k += 1
    return satteldach(w, x0, z0, x1, z1, y0 + H + 1, Dachmat(w, DACH[dach]), first_x=False, ue=1, giebel=st,
                      traufe="dark_oak", steil=steil)


def apsis(w, cx, cz, y0, r, H, st, dach="schiefer"):
    for y in range(y0, y0 + H + 1):
        for x in range(cx - r - 1, cx + r + 2):
            for z in range(cz - r - 1, cz + 1):
                d = math.hypot(x - cx, z - cz)
                if r - 0.8 < d <= r + 0.3:
                    w.setze(x, y, z, st(x, y, z))
    kegeldach(w, cx, cz, y0 + H + 1, r, Dachmat(w, DACH[dach]), form="kegel")


def rosette(w, cx, cy, z, r, mat="yellow_stained_glass"):
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            d = math.hypot(dx, dy)
            if d <= r + 0.3:
                farbe = ["red_stained_glass", "blue_stained_glass", "yellow_stained_glass", "purple_stained_glass"][
                    int(math.atan2(dy, dx) / 6.283 * 8 + 8) % 4] if d > 1 else mat
                w.setze(cx + dx, cy + dy, z, w.b("stone_bricks") if r - 0.6 < d else w.b(farbe))


def zwiebel(w, cx, cz, y, r, mat="gold_block", mat2="waxed_oxidized_cut_copper"):
    H = int(r * 3.2)
    for k in range(H + 1):
        t = k / H
        rr = r * (math.sin(math.pi * min(1, t * 1.35)) * 1.25 if t < 0.74 else (1 - t) * 1.9)
        for x in range(cx - int(r * 1.3) - 1, cx + int(r * 1.3) + 2):
            for z in range(cz - int(r * 1.3) - 1, cz + int(r * 1.3) + 2):
                d = math.hypot(x - cx, z - cz)
                if d <= rr + 0.3 and (d > rr - 1.2 or k == 0):
                    w.setze(x, y + k, z, w.b(mat if (k + x) % 3 else mat2))
    w.setze(cx, y + H + 1, cz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return y + H


# ============================================================================ Bauten

def zwiebelturmkirche(seed, g=2):
    """Zwiebelturm-Kirche: eine weiße Kirche mit fünf goldenen und grünen Zwiebelkuppeln auf Tamboursockeln,
    bunten Ornamentbändern und einem Glockenturm mit eigener Zwiebel."""
    w = _neu(seed)
    s = S[g]
    zl = garten(w, 11 * s + 4, seed=seed, baeume=2)
    st = M(w, MAT["hell"])
    B = int(5 * s + 4)
    H = int(6 * s + 5)
    mauer(w, -B, -B, B, B, 1, H, st)
    for y in (H // 2, H):
        for x in range(-B, B + 1):
            for z in (-B, B):
                w.setze(x, y, z, w.b("red_terracotta" if x % 2 else "blue_terracotta"))
    for x in range(-B, B + 1):
        for z in range(-B, B + 1):
            w.setze(x, H + 1, z, w.b("smooth_quartz"))
    for (dx, dz, r) in ((0, 0, int(2 * s + 2)), (-B + 2, -B + 2, int(s + 1)), (B - 2, -B + 2, int(s + 1)),
                        (-B + 2, B - 2, int(s + 1)), (B - 2, B - 2, int(s + 1))):
        for y in range(H + 2, H + 2 + int(2 * s) + 1):
            for x in range(dx - r, dx + r + 1):
                for z in range(dz - r, dz + r + 1):
                    if r - 0.8 < math.hypot(x - dx, z - dz) <= r + 0.3:
                        w.setze(x, y, z, st(x, y, z))
        zwiebel(w, dx, dz, H + 3 + int(2 * s), r, "gold_block" if dx == 0 else "lime_terracotta",
                "yellow_concrete" if dx == 0 else "green_terracotta")
    tuer(w, 0, 1, B, "south", holz="dark_oak")
    return w


def stabkirche(seed, g=2):
    """Stabkirche: eine dunkle Holzkirche mit mehrfach gestaffelten, steilen Schindeldächern, Drachenköpfen an den
    Firstenden, einem umlaufenden Laubengang und einem kleinen Dachreiter."""
    w = _neu(seed)
    s = S[g]
    garten(w, 10 * s + 4, seed=seed, baeume=3)
    holz = M(w, [("dark_oak_planks", 2), ("stripped_dark_oak_log", 1), ("spruce_planks", 1)])
    B, L = int(3 * s + 2), int(6 * s + 4)
    for x in range(-B - 2, B + 3):
        for z in range(-L - 2, L + 3):
            if abs(x) == B + 2 or abs(z) == L + 2:
                for y in range(1, 3):
                    w.setze(x, y, z, stamm(w, "dark_oak") if (x + z) % 3 == 0 else w.b("air"))
    satteldach(w, -B - 2, -L - 2, B + 2, L + 2, 3, Dachmat(w, DACH["holz"]), first_x=False, ue=1, traufe="dark_oak")
    mauer(w, -B, -L, B, L, 1, int(5 * s) + 4, holz)
    y = int(5 * s) + 5
    for k in range(3):
        b = B - k
        l = L - k * 2
        if b < 1:
            break
        top = satteldach(w, -b, -l, b, l, y, Dachmat(w, DACH["holz"]), first_x=False, ue=1, traufe="dark_oak",
                         steil=2)
        y = (top or y + 3) - 1
        if k < 2:
            mauer(w, -b + 1, -l + 2, b - 1, l - 2, y, y + 2, holz)
            y += 3
    for z in (-L - 1, L + 1):
        w.setze(0, y - 2, z, w.b("bone_block", axis="z"), False)
    tuer(w, 0, 1, L, "south", holz="dark_oak", laternen=False)
    return w


def backsteinkathedrale(seed, g=3):
    """Backsteinkathedrale: eine gewaltige Kirche aus rotem Backstein mit weißen Blendfenstern, hohen Spitzbogen-
    fenstern, Strebepfeilern, einem schlanken Westturm mit grünem Kupferhelm und Chorumgang."""
    w = _neu(seed)
    s = S[g]
    garten(w, 14 * s + 4, seed=seed, baeume=2)
    st = M(w, MAT["ziegel"])
    B, L, H = int(5 * s + 3), int(14 * s + 6), int(9 * s + 6)
    schiff(w, -B, -L, B, L, 1, H, st, dach="kupfer")
    apsis(w, 0, -L, 1, B, H, st, "kupfer")
    eckturm(w, 0, L + 3, 1, int(2 * s + 2), int(H * 2.1), st, Dachmat(w, DACH["kupfer"]), form="nadel")
    tuer(w, 0, 1, L + 3 + int(2 * s + 2), "south", holz="dark_oak")
    for y in range(H, H + 4):
        for x in range(-1, 2):
            w.setze(x, y, L + 3 + int(2 * s + 2), w.b("white_concrete"), False)
    return w


def rundkirche(seed, g=2):
    """Rundkirche: ein runder Zentralbau mit Säulenumgang, einem Kuppeldach mit Laterne obenauf, kleinen Rundfenstern
    und einer Vorhalle mit Dreiecksgiebel."""
    w = _neu(seed)
    s = S[g]
    garten(w, 10 * s + 4, seed=seed, baeume=2)
    st = M(w, MAT["hell"])
    R = int(5 * s + 3)
    H = int(5 * s + 4)
    for y in range(1, H + 1):
        for x in range(-R - 3, R + 4):
            for z in range(-R - 3, R + 4):
                d = math.hypot(x, z)
                if R - 0.8 < d <= R + 0.3:
                    fen = y == H - 2 and (x == 0 or z == 0 or abs(x) == abs(z))
                    w.setze(x, y, z, w.b("yellow_stained_glass") if fen else st(x, y, z))
                elif abs(d - (R + 2)) < 0.5 and int(math.degrees(math.atan2(z, x))) % 30 < 10 and y < H:
                    w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    for x in range(-R - 3, R + 4):
        for z in range(-R - 3, R + 4):
            if math.hypot(x, z) <= R + 2.5:
                w.setze(x, H + 1, z, w.b("smooth_quartz"))
    kegeldach(w, 0, 0, H + 2, R, Dachmat(w, DACH["kupfer"]), form="glocke")
    tuer(w, 0, 1, R, "south", holz="birch")
    return w


def felsenkapelle(seed, g=1):
    """Felsenkapelle: eine winzige Kapelle, halb in einen moosigen Felsblock gebaut, mit Glockengiebel, Holztür,
    einem Kerzenaltar in der Felsnische und Bänken davor."""
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 4, seed=seed, baeume=2)
    rng = w.rng
    R = 6 * s + 3
    for x in range(-int(R), int(R) + 1):
        for z in range(-int(R), 1):
            for y in range(1, int(R) + 2):
                if x * x + (y * 0.9) ** 2 + (z * 1.2) ** 2 <= R * R:
                    w.setze(x, y, z - 1, w.b(["stone", "mossy_cobblestone", "andesite", "tuff"][int(rng.random() * 4)]))
    st = M(w, MAT["hell"])
    B = int(2 * s + 2)
    mauer(w, -B, -2, B, int(4 * s) + 2, 1, int(3 * s) + 3, st)
    satteldach(w, -B, -2, B, int(4 * s) + 2, int(3 * s) + 4, Dachmat(w, DACH["rot"]), first_x=False, ue=1,
               traufe="spruce", steil=2)
    tuer(w, 0, 1, int(4 * s) + 2, "south", holz="spruce")
    w.setze(0, int(3 * s) + 8, int(4 * s) + 2, w.b("bell", attachment="floor", facing="south", powered=False), False)
    return w


def doppelturmfassade(seed, g=3):
    """Doppelturm-Fassade: eine Kathedrale mit mächtiger Westfassade aus zwei gleichen Türmen mit Maßwerkhelmen,
    dazwischen Rosettenfenster und drei Portale, ein langes Schiff dahinter."""
    w = _neu(seed)
    s = S[g]
    garten(w, 14 * s + 4, seed=seed, baeume=2)
    st = M(w, MAT["stein"])
    B, L, H = int(5 * s + 3), int(12 * s + 6), int(8 * s + 6)
    schiff(w, -B, -L, B, L, 1, H, st)
    apsis(w, 0, -L, 1, B, H, st)
    for sx in (-1, 1):
        eckturm(w, sx * (B + 2), L + 2, 1, int(2 * s + 1), int(H * 2.0), st, Dachmat(w, DACH["schiefer"]),
                form="nadel")
    for x in range(-B, B + 1):
        for y in range(1, H + 4):
            w.setze(x, y, L + 1, st(x, y, L))
    rosette(w, 0, H, L + 1, int(2 * s + 1))
    for x in (-B + 2, 0, B - 2):
        for y in (1, 2, 3):
            w.bloecke.pop((x, y, L + 1), None)
            w.bloecke.pop((x, y, L), None)
    return w


def inselkloster(seed, g=2):
    """Inselkloster: ein Kloster auf einer kleinen Insel im See – Kirche mit Turm, Kreuzgang, Gemüsegarten und ein
    Bootssteg, von Weiden gesäumt."""
    from himmelsstadt2 import haus
    w = _neu(seed)
    s = S[g]
    R = int(16 * s + 6)
    rng = w.rng
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d <= R:
                if d < R * 0.6:
                    w.setze(x, 0, z, w.b("grass_block", snowy=False))
                    w.setze(x, -1, z, w.b("dirt"))
                else:
                    w.setze(x, 0, z, w.b("water", level=0))
                    w.setze(x, -1, z, w.b("water", level=0))
                    w.setze(x, -2, z, w.b("gravel"))
    st = M(w, MAT["stein"])
    B, L = int(3 * s + 2), int(7 * s + 3)
    schiff(w, -B, -L, B, L, 1, int(5 * s + 4), st)
    eckturm(w, 0, L + 2, 1, 2, int(10 * s + 6), st, Dachmat(w, DACH["schiefer"]), form="kegel")
    haus(w, B + 6, 0, 5, int(L * 1.5) | 1, 1, "stein", geschosse=1, tuer_s="west")
    for z in range(int(R * 0.6), R + 1):
        w.setze(-B - 3, 1, z, w.b("spruce_planks"))
    for k in range(3):
        a = k * 2.1
        x, z = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        if w.frei(x, 1, z):
            einfuegen(w, wald2.weide(seed + k), x, 0, z)
    return w


def kartause(seed, g=2):
    """Kartause: ein strenges Kloster mit großem Kreuzgang, um den sich die kleinen Häuschen der Mönche mit eigenen
    Gärtchen reihen, eine schlichte Kirche mit Dachreiter an der Stirnseite."""
    from himmelsstadt2 import haus
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    garten(w, R + 5, seed=seed, baeume=0)
    st = M(w, MAT["hell"])
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if max(abs(x), abs(z)) in (R - 4, R - 3):
                for y in range(1, 4):
                    if max(abs(x), abs(z)) == R - 4 and (x + z) % 3 == 0:
                        w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
                    elif max(abs(x), abs(z)) == R - 3:
                        w.setze(x, y, z, st(x, y, z))
                w.setze(x, 4, z, w.b("mcw:red_terracotta_roof" if False else "granite"))
    for k in range(-R + 3, R - 2, int(5 * s + 2)):
        for (cx, cz, sd) in ((k, -R - 1, "south"), (-R - 1, k, "east"), (R + 1, k, "west")):
            haus(w, cx, cz, 4 | 1, 4 | 1, 1, "hell" if False else "kupfer", geschosse=1, tuer_s=sd, schorn=False)
    schiff(w, -3, R, 3, R + int(8 * s), 1, int(5 * s + 3), st, strebe=False)
    return w


def gipfelkapelle(seed, g=1):
    """Gipfelkapelle: eine kleine Steinkapelle mit Holzschindeldach auf einem felsigen Berggipfel, ein schmaler
    Pfad schlängelt sich hinauf, daneben eine Rastbank und ein Glockenstuhl."""
    w = _neu(seed)
    s = S[g]
    R = 10 * s + 5
    rng = w.rng
    H = 9 * s + 4
    for x in range(-int(R), int(R) + 1):
        for z in range(-int(R), int(R) + 1):
            d = math.hypot(x, z) / R
            if d <= 1:
                h = int(H * (1 - d) ** 1.3)
                for y in range(-1, h + 1):
                    w.setze(x, y, z, w.b(["stone", "andesite", "tuff"][int(rng.random() * 3)]) if y < h else
                            w.b("grass_block", snowy=False) if rng.random() < 0.6 else w.b("stone"))
    y = int(H) + 1
    for x in range(-3, 4):
        for z in range(-4, 5):
            for yy in range(y - 3, y):
                w.setze(x, yy, z, w.b("stone"))
    st = M(w, MAT["stein"])
    mauer(w, -2, -3, 2, 3, y, y + 3, st)
    satteldach(w, -2, -3, 2, 3, y + 4, Dachmat(w, DACH["holz"]), first_x=False, ue=1, traufe="spruce", steil=2)
    tuer(w, 0, y, 3, "south", holz="spruce", laternen=False)
    for i in range(int(H * 2)):
        a = i * 0.4
        r = R * (1 - i / (H * 2)) * 0.85
        yy = int(H * (1 - r / R) ** 1.3) + 1
        w.setze(round(math.cos(a) * r), yy, round(math.sin(a) * r), w.b("dirt_path"), True)
    return w


def oktogonkapelle(seed, g=2):
    """Oktogon-Kapelle: eine achteckige Kapelle mit hohen Fenstern auf jeder Seite, einem achteckigen Zeltdach mit
    Laterne und einem kleinen Umgang, auf einer Stufenplattform."""
    w = _neu(seed)
    s = S[g]
    garten(w, 10 * s + 4, seed=seed, baeume=2)
    st = M(w, MAT["sand"])
    R = int(4 * s + 3)
    H = int(6 * s + 4)
    for k in range(2):
        for x in range(-R - 3 + k, R + 4 - k):
            for z in range(-R - 3 + k, R + 4 - k):
                if abs(x) + abs(z) <= (R + 3 - k) * 1.4 and max(abs(x), abs(z)) <= R + 3 - k:
                    w.setze(x, 1 + k, z, w.b("smooth_sandstone"))
    for y in range(3, 3 + H):
        for x in range(-R, R + 1):
            for z in range(-R, R + 1):
                inn = abs(x) + abs(z) <= R * 1.4 and max(abs(x), abs(z)) <= R
                rand = inn and not (abs(x) + abs(z) <= (R - 1) * 1.4 and max(abs(x), abs(z)) <= R - 1)
                if rand:
                    fen = 4 < y < 2 + H and (x == 0 or z == 0 or abs(x) == abs(z))
                    w.setze(x, y, z, w.b("light_blue_stained_glass") if fen else st(x, y, z))
    kegeldach(w, 0, 0, 3 + H, R, Dachmat(w, DACH["rot"]), form="kegel", eckig=True)
    tuer(w, 0, 3, R, "south", holz="birch")
    return w


def lichttempel(seed, g=2):
    """Tempel des Lichts: ein strahlend weißer Tempel aus Quarz und Glas, dessen Dach eine gläserne Kuppel ist,
    goldene Säulen tragen Lichtkristalle, ein Lichtstrahl steigt aus der Mitte auf."""
    w = _neu(seed)
    s = S[g]
    garten(w, 11 * s + 4, seed=seed, baeume=0)
    R = int(6 * s + 3)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) <= R + 2:
                w.setze(x, 1, z, w.b("smooth_quartz"))
    n = 8
    for k in range(n):
        a = k / n * 6.283
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        for y in range(2, 2 + int(5 * s + 3)):
            w.setze(x, y, z, w.b("gold_block" if y % 3 == 0 else "quartz_pillar", **({} if y % 3 == 0 else
                                                                                   {"axis": "y"})))
        w.setze(x, 2 + int(5 * s + 3), z, w.b("sea_lantern"))
    yk = 3 + int(5 * s + 3)
    for x in range(-R - 1, R + 2):
        for y in range(0, R + 1):
            for z in range(-R - 1, R + 2):
                d = math.sqrt(x * x + y * y + z * z)
                if R - 0.9 < d <= R + 0.2:
                    w.setze(x, yk + y, z, w.b("white_stained_glass" if (x + z) % 3 else "yellow_stained_glass"))
    w.setze(0, 2, 0, w.b("beacon"))
    for x in range(-1, 2):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("gold_block"))
    return w


def mondtempel(seed, g=2):
    """Mondtempel: ein dunkler Tempel aus Tiefenschiefer mit silbernen Mondsicheln auf den Dachspitzen, einem
    Spiegelbecken im Hof, in dem der Mond liegt, und blassen Säulen."""
    w = _neu(seed)
    s = S[g]
    garten(w, 11 * s + 4, seed=seed, baeume=1)
    st = M(w, MAT["dunkel"])
    B, L = int(5 * s + 3), int(7 * s + 4)
    mauer(w, -B, -L, B, L, 1, int(5 * s + 4), st)
    for z in range(-L, L + 1, 3):
        for sx in (-1, 1):
            for y in range(1, int(5 * s + 4)):
                w.setze(sx * (B + 1), y, z, w.b("calcite"))
    satteldach(w, -B - 1, -L, B + 1, L, int(5 * s + 5), Dachmat(w, DACH["schiefer"]), first_x=False, steil=1,
               traufe="dark_oak", giebel=st)
    for x in range(-2, 3):
        for z in range(L + 2, L + 7):
            w.setze(x, 0, z, w.b("water", level=0))
    w.setze(0, 0, L + 4, w.b("sea_lantern"))
    tuer(w, 0, 1, L, "south", holz="dark_oak")
    return w


def waldkathedrale(seed, g=2):
    """Waldkathedrale: zwei Reihen hoher, schlanker Birken neigen sich zueinander und bilden mit ihren Kronen ein
    lebendes Kirchenschiff, am Ende ein Altarstein mit Moos und Kerzen, Lichtungen wie Fenster."""
    w = _neu(seed)
    s = S[g]
    L = int(14 * s + 6)
    garten(w, L + 2, seed=seed, baeume=0)
    from leuchtwald2 import bez, rohr, laubball
    for z in range(-L, L + 1, int(3 * s + 2)):
        for sx in (-1, 1):
            x0 = sx * int(4 * s + 3)
            H = 12 * s + 6
            pts = bez((x0, 0, z), (x0, H * 0.7, z), (sx * 1.5, H, z))
            rohr(w, pts, 0.7 * s + 0.4, 0.4, w.b("birch_wood", axis="y"))
            laubball(w, sx * 1.5, H, z, 2.5 * s + 1, ("birch_leaves", "oak_leaves", "azalea_leaves"))
    for x in range(-1, 2):
        w.setze(x, 1, -L, w.b("mossy_cobblestone"))
    w.setze(0, 2, -L, w.b("candle", candles=4, lit=True, waterlogged=False))
    for z in range(-L, L + 1):
        w.setze(0, 0, z, w.b("moss_block"))
    return w


def kristallkathedrale(seed, g=3):
    """Kristallkathedrale: eine Kathedrale ganz aus Amethyst und farbigem Glas, deren Türme als riesige Kristall-
    spitzen in den Himmel wachsen, im Inneren leuchtet violettes Licht."""
    from kristall import kristall
    w = _neu(seed)
    s = S[g]
    garten(w, 12 * s + 4, seed=seed, baeume=0)
    st = M(w, [("amethyst_block", 3), ("purple_stained_glass", 1), ("calcite", 1)])
    B, L, H = int(4 * s + 3), int(9 * s + 4), int(7 * s + 5)
    schiff(w, -B, -L, B, L, 1, H, st, glas=["magenta_stained_glass_pane", "purple_stained_glass_pane"],
           dach="schiefer", strebe=False)
    rng = w.rng
    for (x, z, f) in ((-B, L, 1.0), (B, L, 1.0), (0, -L, 1.3)):
        kristall(w, (x, 1, z), (0, 1, 0), (H * 2.0) * f, (1.6 * s + 1) * f, art="amethyst")
    for k in range(6 + g * 2):
        kristall(w, (rng.integers(-B, B + 1), H, rng.integers(-L, L + 1)),
                 ((rng.random() - 0.5) * 0.6, 1, (rng.random() - 0.5) * 0.6), 3 * s + 2, 0.8 * s + 0.4,
                 art="amethyst")
    return w


def vierungsdom(seed, g=3):
    """Vierungsdom: ein kreuzförmiger Dom mit Langhaus und Querhaus, über der Vierung ein mächtiger achteckiger
    Turm mit Spitzhelm, Treppentürmchen an den Ecken und Apsis im Osten."""
    w = _neu(seed)
    s = S[g]
    garten(w, 14 * s + 4, seed=seed, baeume=2)
    st = M(w, MAT["sand"])
    B, L, H = int(4 * s + 3), int(12 * s + 6), int(8 * s + 5)
    schiff(w, -B, -L, B, L, 1, H, st, dach="schiefer")
    satteldach(w, -L // 2 - 2, -B, L // 2 + 2, B, H + 1, Dachmat(w, DACH["schiefer"]), first_x=True, ue=1,
               traufe="dark_oak", steil=2, giebel=st)
    mauer(w, -L // 2 - 2, -B, L // 2 + 2, B, 1, H, st)
    apsis(w, 0, -L, 1, B, H, st)
    rundturm(w, 0, 0, H + 2, B, int(5 * s + 3), st, Dachmat(w, DACH["schiefer"]), form="nadel")
    for sx in (-1, 1):
        eckturm(w, sx * (B + 1), L + 1, 1, 1, H + 4, st, Dachmat(w, DACH["schiefer"]), form="nadel")
    tuer(w, 0, 1, L, "south", holz="dark_oak")
    return w


def glockenspielturm(seed, g=2):
    """Glockenspielturm: ein schlanker Turm mit einer offenen Glockenstube voller Glocken in verschiedenen Größen,
    darunter eine Uhr mit beweglichen Figuren, an einem kleinen Platz mit Brunnen."""
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 4, seed=seed, baeume=1)
    st = M(w, MAT["ziegel"])
    r = int(2 * s + 2)
    H = int(16 * s + 8)
    for y in range(1, H):
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                rand = abs(x) == r or abs(z) == r
                offen = y > H - int(4 * s) - 3 and not (abs(x) == r and abs(z) == r)
                if rand and not offen:
                    w.setze(x, y, z, st(x, y, z))
    yg = H - int(4 * s) - 2
    for x in range(-r + 1, r):
        for z in range(-r + 1, r):
            if (x + z) % 2 == 0:
                w.setze(x, yg + 2 + (x % 2), z, w.b("bell", attachment="ceiling", facing="north", powered=False))
    for x in range(-r, r + 1):
        for z in range(-r, r + 1):
            w.setze(x, H, z, st(x, H, z))
    kegeldach(w, 0, 0, H + 1, r, Dachmat(w, DACH["kupfer"]), form="nadel", eckig=True)
    yc = int(H * 0.55)
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx * dx + dy * dy <= 5:
                w.setze(dx, yc + dy, r + 1, w.b("white_concrete" if dx * dx + dy * dy < 4 else "gold_block"), False)
    tuer(w, 0, 1, r, "south", holz="dark_oak")
    return w


def feuertempel(seed, g=2):
    """Feuertempel: ein Tempel aus schwarzem Stein mit Kupferdach, in dessen offener Mitte auf einem Altar ein
    ewiges Feuer brennt, vier Feuerschalen an den Ecken und Rauchabzüge im Dach."""
    w = _neu(seed)
    s = S[g]
    garten(w, 10 * s + 4, seed=seed, baeume=1)
    st = M(w, [("polished_blackstone_bricks", 2), ("blackstone", 1), ("gilded_blackstone", 0.2)])
    B = int(5 * s + 3)
    H = int(5 * s + 4)
    for x in range(-B, B + 1):
        for z in range(-B, B + 1):
            rand = abs(x) == B or abs(z) == B
            if rand:
                for y in range(1, H + 1):
                    if (x + z) % 4 or y > H - 1:
                        w.setze(x, y, z, st(x, y, z))
    satteldach(w, -B, -B, B, B, H + 1, Dachmat(w, DACH["kupfer"]), first_x=True, ue=1, traufe="dark_oak")
    for x in range(-1, 2):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("gilded_blackstone"))
    w.setze(0, 2, 0, w.b("magma_block"))
    w.setze(0, 3, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    for (x, z) in ((-B - 2, -B - 2), (B + 2, -B - 2), (-B - 2, B + 2), (B + 2, B + 2)):
        w.setze(x, 1, z, w.b("polished_blackstone"))
        w.setze(x, 2, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    tuer(w, 0, 1, B, "south", holz="crimson")
    return w


def quellheiligtum(seed, g=2):
    """Quellheiligtum: ein kleiner offener Rundtempel über einer sprudelnden Quelle, das Wasser fließt in Rinnen
    zwischen Blumenbeeten in ein Becken mit Seerosen, Weiden ringsum."""
    w = _neu(seed)
    s = S[g]
    zl = garten(w, 11 * s + 4, seed=seed, baeume=0)
    R = int(3 * s + 2)
    for k in range(8):
        a = k / 8 * 6.283
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        for y in range(1, int(4 * s) + 4):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    kegeldach(w, 0, 0, int(4 * s) + 4, R, Dachmat(w, DACH["kupfer"]), form="glocke")
    for x in range(-R + 1, R):
        for z in range(-R + 1, R):
            if math.hypot(x, z) < R - 0.5:
                w.setze(x, 0, z, w.b("water", level=0))
    w.setze(0, 1, 0, w.b("water", level=0))
    for z in range(R, int(9 * s + 3)):
        w.setze(0, 0, z, w.b("water", level=0))
        w.bloecke.pop((0, 1, z), None)
    for x in range(-3, 4):
        for z in range(int(9 * s + 3), int(9 * s + 7)):
            w.setze(x, 0, z, w.b("water", level=0))
            w.bloecke.pop((x, 1, z), None)
    for k in range(2):
        einfuegen(w, wald2.weide(seed + k), (k * 2 - 1) * int(7 * s + 2), 0, -2)
    return w


def fischerkirche(seed, g=2):
    """Fischerkirche: eine weiß gekalkte Kirche am Hafen mit blauem Dach, einem Leuchtfeuer im Turm, Schiffsmodellen
    über dem Portal, Netzen am Zaun und Ruderbooten davor."""
    from boote import ruderboot
    w = _neu(seed)
    s = S[g]
    zl = garten(w, 11 * s + 4, seed=seed, baeume=0)
    for (x, z) in zl:
        if z > 8 * s + 2:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("water", level=0))
            w.bloecke.pop((x, 1, z), None)
    st = M(w, [("white_concrete", 2), ("calcite", 1)])
    B, L = int(3 * s + 2), int(6 * s + 3)
    schiff(w, -B, -L, B, L, 1, int(4 * s + 3), st, glas=["light_blue_stained_glass_pane"], dach="rot",
           strebe=False)
    eckturm(w, 0, -L - 2, 1, 2, int(10 * s + 5), st, Dachmat(w, ["mcw:blue_terracotta", "deepslate_tile"]),
            form="nadel")
    w.setze(0, int(10 * s + 5) - 1, -L - 2, w.b("sea_lantern"))
    tuer(w, 0, 1, L, "south", holz="birch")
    einfuegen(w, ruderboot(seed, 0), 3, 0, int(10 * s + 3))
    return w


def hallenkirche(seed, g=3):
    """Hallenkirche: eine weite Kirche mit drei gleich hohen Schiffen unter einem einzigen, riesigen Satteldach,
    langen Fensterreihen und einem breiten Westbau mit Spitzhelm."""
    w = _neu(seed)
    s = S[g]
    garten(w, 14 * s + 4, seed=seed, baeume=2)
    st = M(w, MAT["stein"])
    B, L, H = int(8 * s + 4), int(12 * s + 6), int(7 * s + 5)
    schiff(w, -B, -L, B, L, 1, H, st, dach="rot", steil=1)
    for x in (-B // 3, B // 3):
        for z in range(-L + 2, L - 1, 3):
            for y in range(1, H + 1):
                w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    eckturm(w, 0, L + 3, 1, int(3 * s + 2), int(H * 2.2), st, Dachmat(w, DACH["schiefer"]), form="nadel")
    return w


KATHEDRALEN3 = {
    "zwiebelturmkirche": ("Zwiebelturm-Kirche", zwiebelturmkirche),
    "stabkirche": ("Stabkirche", stabkirche),
    "backsteinkathedrale": ("Backsteinkathedrale", backsteinkathedrale),
    "rundkirche": ("Rundkirche", rundkirche),
    "felsenkapelle": ("Felsenkapelle", felsenkapelle),
    "doppelturmfassade": ("Doppelturm-Fassade", doppelturmfassade),
    "inselkloster": ("Inselkloster", inselkloster),
    "kartause": ("Kartause", kartause),
    "gipfelkapelle": ("Gipfelkapelle", gipfelkapelle),
    "oktogonkapelle": ("Oktogon-Kapelle", oktogonkapelle),
    "lichttempel": ("Tempel des Lichts", lichttempel),
    "mondtempel": ("Mondtempel", mondtempel),
    "waldkathedrale": ("Waldkathedrale", waldkathedrale),
    "kristallkathedrale": ("Kristallkathedrale", kristallkathedrale),
    "vierungsdom": ("Vierungsdom", vierungsdom),
    "glockenspielturm": ("Glockenspielturm", glockenspielturm),
    "feuertempel": ("Feuertempel", feuertempel),
    "quellheiligtum": ("Quellheiligtum", quellheiligtum),
    "fischerkirche": ("Fischerkirche", fischerkirche),
    "hallenkirche": ("Hallenkirche", hallenkirche),
}

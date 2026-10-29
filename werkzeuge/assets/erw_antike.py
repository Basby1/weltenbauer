"""Antike Monumente II – zwanzig weitere Bauten der Antike (eigene Entwürfe): Bibliothek, Akropolis, Siegessäule,
Agora, Odeon, Palästra, Brunnenhaus, Antiker Hafen, Gräberstraße, Felsentempel, Stufentempel, Peristylhaus,
Reiterstandbild, Römerbrücke, Labyrinth, Löwentor, Kuppelgrab, Amphorenkontor, Säulenfeld und Götterthron."""

from __future__ import annotations

import math

import wald2
from feinbau import Dachmat, Mix, platte, satteldach, treppe
from flora import _neu
from lib import einfuegen

S = [0.6, 1.0, 1.6, 2.5]


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def marmor(w):
    return M(w, [("smooth_quartz", 3), ("quartz_block", 2), ("calcite", 2), ("diorite", 1)])


def boden(w, R, rund=True, mat=None, gras_rand=3):
    mat = mat or M(w, [("smooth_stone", 2), ("polished_andesite", 1), ("calcite", 1)], zelle=1.2)
    rng = w.rng
    zellen = []
    for x in range(-R - gras_rand, R + gras_rand + 1):
        for z in range(-R - gras_rand, R + gras_rand + 1):
            d = math.hypot(x, z) if rund else max(abs(x), abs(z))
            if d <= R + gras_rand + rng.random():
                w.setze(x, -1, z, w.b("dirt"))
                if d <= R:
                    w.setze(x, 0, z, mat(x, 0, z))
                else:
                    w.setze(x, 0, z, w.b("grass_block", snowy=False))
                    if rng.random() < 0.3:
                        w.setze(x, 1, z, w.b("grass" if rng.random() < 0.7 else "poppy"))
                zellen.append((x, z, d > R))
    return zellen


def zypressen(w, zellen, n, seed):
    rng = w.rng
    gras = [(x, z) for (x, z, g) in zellen if g]
    rng.shuffle(gras)
    gesetzt = []
    for (x, z) in gras:
        if len(gesetzt) >= n:
            break
        if any(math.hypot(x - a, z - b) < 4 for a, b in gesetzt) or not w.frei(x, 1, z):
            continue
        einfuegen(w, wald2.fichte(seed + x * 7 + z, schmal=0.35), x, 0, z)
        gesetzt.append((x, z))


def saeule(w, x, y, z, H, r=0, mat="quartz_pillar", kapitell="chiseled_quartz_block", basis="smooth_quartz"):
    for yy in range(y, y + H):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r + 0.5:
                    blk = w.b(basis) if yy == y and r > 0 else w.b(kapitell) if yy == y + H - 1 else \
                        w.b(mat, axis="y") if "pillar" in mat else w.b(mat)
                    w.setze(x + dx, yy, z + dz, blk)
    if r == 0:
        w.setze(x, y, z, w.b(basis))
        w.setze(x, y + H - 1, z, w.b(kapitell))


def stufen(w, x0, z0, x1, z1, n, mat="smooth_quartz", y0=1):
    for k in range(n):
        for x in range(x0 - n + k, x1 + n - k + 1):
            for z in range(z0 - n + k, z1 + n - k + 1):
                w.setze(x, y0 + k, z, w.b(f"{mat}_block" if mat == "quartz" else mat))
    return y0 + n


def giebeldach(w, x0, z0, x1, z1, y, first_x=True, mat=("quartz", "smooth_quartz"), steil=1):
    return satteldach(w, x0, z0, x1, z1, y, Dachmat(w, list(mat)), first_x=first_x, ue=1, ue_giebel=1,
                      giebel=marmor(w), traufe="birch", steil=steil, knick=False, firstzier=False,
                      giebelfenster=False)


def tempel(w, cx, cz, B, T, y, H, r=0, dach=("mcw:orange_terracotta", "brick", "granite"), cella=True):
    x0, z0, x1, z1 = cx - B // 2, cz - T // 2, cx + B // 2, cz + T // 2
    abst = 2 + r * 2
    for x in range(x0, x1 + 1, abst):
        for z in (z0, z1):
            saeule(w, x, y, z, H, r)
    for z in range(z0 + abst, z1, abst):
        for x in (x0, x1):
            saeule(w, x, y, z, H, r)
    for x in range(x0 - r, x1 + r + 1):
        for z in range(z0 - r, z1 + r + 1):
            w.setze(x, y + H, z, w.b("smooth_quartz"))
    if cella:
        mm = marmor(w)
        for x in range(x0 + abst, x1 - abst + 1):
            for z in range(z0 + abst, z1 - abst + 1):
                if x in (x0 + abst, x1 - abst) or z in (z0 + abst, z1 - abst):
                    for yy in range(y, y + H):
                        w.setze(x, yy, z, mm(x, yy, z))
        for yy in range(y, y + 3):
            w.bloecke.pop((cx, yy, z1 - abst), None)
    return giebeldach(w, x0 - r, z0 - r, x1 + r, z1 + r, y + H + 1, first_x=False, mat=dach)


def relief(w, x0, x1, y, z, mat="chiseled_quartz_block"):
    for x in range(x0, x1 + 1):
        w.setze(x, y, z, w.b(mat if x % 2 else "quartz_bricks"))


# ============================================================================ Bauten

def bibliothek(seed, g=1):
    """Bibliothek: ein breiter Säulenbau mit Freitreppe, hinter der Säulenhalle stehen Regale voller Schriftrollen,
    zwei Löwenstatuen bewachen den Eingang, im Giebel ein Relief."""
    w = _neu(seed)
    s = S[g]
    B, T, H = int(14 * s + 8), int(9 * s + 6), int(5 * s + 4)
    zl = boden(w, int(max(B, T) * 0.75))
    y = stufen(w, -B // 2, -T // 2, B // 2, T // 2, 2 + (g > 1))
    tempel(w, 0, 0, B, T, y, H, r=1 if g >= 2 else 0, dach=("quartz", "smooth_quartz"))
    for x in range(-B // 2 + 3, B // 2 - 2):
        for yy in range(y, y + H - 1):
            if (x % 3) != 0:
                w.setze(x, yy, -T // 2 + 3, w.b("bookshelf"))
    for sx in (-1, 1):
        x = sx * (B // 2 - 1)
        z = T // 2 + 4
        for yy in range(1, 3):
            w.setze(x, yy, z, w.b("smooth_quartz"))
        w.setze(x, 3, z, w.b("yellow_terracotta"))
        w.setze(x, 3, z + 1, w.b("yellow_terracotta"))
        w.setze(x, 4, z + 1, w.b("orange_terracotta"))
    zypressen(w, zl, 4 + g, seed)
    return w


def akropolis(seed, g=2):
    """Akropolis: ein felsiger Tafelberg mit Stützmauern, auf dem ein großer Säulentempel, ein kleiner
    Rundtempel und ein Torbau thronen, eine Rampe führt hinauf."""
    w = _neu(seed)
    s = S[g]
    R = int(18 * s + 8)
    rng = w.rng
    H = int(6 * s + 4)
    for x in range(-R - 3, R + 4):
        for z in range(-R - 3, R + 4):
            d = math.hypot(x, z * 1.3)
            if d <= R + 3:
                top = H if d <= R else int(H * (1 - (d - R) / 3))
                for y in range(-1, top + 1):
                    w.setze(x, y, z, w.b(["stone", "andesite", "tuff", "calcite"][int(rng.random() * 4)]) if
                            d > R - 1 or y < top else w.b("smooth_stone"))
    for i in range(R + 3):
        for q in range(-1, 2):
            w.setze(R + 2 - i, int(H * i / (R + 3)), q + R // 2, w.b("smooth_quartz_slab", type="bottom",
                                                                      waterlogged=False))
    B, T = int(12 * s + 6), int(7 * s + 5)
    tempel(w, -int(R * 0.15), -2, B, T, H + 1, int(5 * s + 4), r=1 if g >= 2 else 0)
    rx, rz = int(R * 0.55), int(R * 0.3)
    for k in range(8):
        a = k / 8 * 6.283
        saeule(w, rx + round(math.cos(a) * 3), H + 1, rz + round(math.sin(a) * 3), int(4 * s + 3))
    from feinbau import kegeldach
    kegeldach(w, rx, rz, H + 1 + int(4 * s + 3), 3, Dachmat(w, ["quartz", "smooth_quartz"]), form="kegel",
              spitze="end_rod")
    return w


def siegessaeule(seed, g=2):
    """Siegessäule: eine hohe Säule mit spiralförmig umlaufendem Reliefband auf einem Sockel mit Inschrift, oben
    eine goldene Statue mit erhobenem Kranz, ringsum ein Platz mit Bänken."""
    from skulptur import Skulptur, ell, kap
    w = _neu(seed)
    s = S[g]
    zl = boden(w, int(9 * s + 5))
    for x in range(-3, 4):
        for z in range(-3, 4):
            for y in range(1, 4):
                w.setze(x, y, z, w.b("chiseled_quartz_block" if y == 2 and (abs(x) == 3 or abs(z) == 3) else
                                     "quartz_bricks"))
    H = int(18 * s + 8)
    r = 1.6 * s + 0.6
    for y in range(4, 4 + H):
        for x in range(-3, 4):
            for z in range(-3, 4):
                d = math.hypot(x, z)
                if d <= r + 0.4:
                    a = math.atan2(z, x)
                    band = int((a / 6.283 * 8 + y * 0.5)) % 4 == 0
                    w.setze(x, y, z, w.b("chiseled_quartz_block" if band else "quartz_pillar", **({} if band else
                                                                                                {"axis": "y"})))
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, 4 + H, z, w.b("smooth_quartz"))
    Sk = Skulptur(w, s * 0.8)
    Sk.mat("g", w.b("gold_block"))
    Sk.plus(kap((0, 0, 0), (0, 5, 0), 1.0, 0.8), "g")
    Sk.plus(ell(0, 6, 0, 0.7, 0.8, 0.7), "g")
    Sk.plus(kap((0.6, 4.6, 0), (1.6, 7.6, 0.4), 0.35), "g")
    Sk.plus(ell(1.8, 8.2, 0.4, 0.7, 0.3, 0.7), "g")
    Sk.rendern((-3, 0, -3), (3, 10, 3), versatz=(0.5, 5 + H, 0.5))
    zypressen(w, zl, 4 + g, seed)
    return w


def agora(seed, g=2):
    """Agora: ein weiter Marktplatz, an zwei Seiten von Säulenhallen mit Ziegeldach gesäumt, Marktstände mit
    Sonnensegeln, Amphoren, ein Brunnen und eine Rednertribüne."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 8)
    zl = boden(w, R, rund=False)
    H = int(4 * s + 3)
    for sz in (-1, 1):
        z = sz * (R - 2)
        for x in range(-R + 2, R - 1, 3):
            saeule(w, x, 1, z, H)
        for x in range(-R + 2, R - 1):
            for dz in range(0, 4):
                w.setze(x, 1 + H, z + sz * dz, w.b("smooth_quartz"))
            w.setze(x, 1 + H + 1, z + sz * 3, w.b("smooth_quartz"))
            for yy in range(1, 1 + H):
                w.setze(x, yy, z + sz * 3, w.b("quartz_bricks"))
        giebeldach(w, -R + 2, min(z, z + sz * 3), R - 2, max(z, z + sz * 3), 2 + H,
                   mat=("mcw:orange_terracotta", "brick", "granite"))
    rng = w.rng
    farben = ["red_wool", "white_wool", "yellow_wool", "blue_wool"]
    for k in range(3 + g * 2):
        cx, cz = int((rng.random() - 0.5) * R * 1.2), int((rng.random() - 0.5) * R * 0.8)
        for (x, z) in ((cx - 1, cz - 1), (cx + 1, cz - 1), (cx - 1, cz + 1), (cx + 1, cz + 1)):
            for yy in range(1, 3):
                w.setze(x, yy, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                      waterlogged=False))
        for x in range(cx - 1, cx + 2):
            for z in range(cz - 1, cz + 2):
                w.setze(x, 3, z, w.b(farben[k % 4]))
        w.setze(cx, 1, cz, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False))
    for x in range(-1, 2):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("water", level=0) if not (x or z) else w.b("smooth_quartz_slab", type="bottom",
                                                                         waterlogged=False))
    return w


def odeon(seed, g=1):
    """Odeon: ein kleines, überdachtes Halbrund-Theater mit ansteigenden Sitzreihen, einer Bühnenwand mit
    Säulennischen und einem hölzernen Dach auf Mauern."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zl = boden(w, R + 2)
    st = "smooth_sandstone"
    for x in range(-R, R + 1):
        for z in range(0, R + 1):
            d = math.hypot(x, z)
            if 3 < d <= R:
                h = int((d - 3) / (R - 3) * (5 * s + 3)) + 1
                for y in range(1, h + 1):
                    w.setze(x, y, z, w.b("smooth_sandstone"))
                a = math.atan2(z, x)
                f = "north" if abs(math.sin(a)) > 0.7 else ("west" if math.cos(a) > 0 else "east")
                w.setze(x, h + 1, z, treppe(w, st, {"north": "south", "west": "east", "east": "west"}[f]))
            if R - 0.8 < d <= R + 0.4:
                for y in range(1, int(5 * s + 3) + 4):
                    w.setze(x, y, z, w.b("sandstone"))
    for x in range(-R, R + 1):
        for y in range(1, int(5 * s + 6)):
            w.setze(x, y, -3, w.b("cut_sandstone") if (x % 4) else w.b("quartz_pillar", axis="y"))
    for x in range(-R, R + 1):
        for z in range(-3, R + 1):
            if math.hypot(x, max(0, z)) <= R + 0.5:
                w.setze(x, int(5 * s + 6) + 2, z, w.b("spruce_planks") if (x + z) % 3 else
                        w.b("stripped_spruce_log", axis="x"))
    return w


def palaestra(seed, g=2):
    """Palästra: ein quadratischer Säulenhof als Sportstätte, in der Mitte eine Sandfläche für Ringkämpfe, an einer
    Seite ein Becken, Statuen von Athleten in den Ecken."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zl = boden(w, R + 2, rund=False)
    H = int(4 * s + 3)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            rand = max(abs(x), abs(z))
            if rand == R and (x + z) % 3 == 0:
                saeule(w, x, 1, z, H)
            if rand >= R - 2:
                w.setze(x, H + 1, z, w.b("smooth_quartz"))
                if rand == R - 2:
                    for yy in range(1, H + 1):
                        w.setze(x, yy, z, w.b("quartz_bricks"))
            elif rand < R - 5:
                w.setze(x, 0, z, w.b("sand"))
    for x in range(-int(R * 0.4), int(R * 0.4)):
        for z in range(R - 4, R - 2):
            w.setze(x, 0, z, w.b("water", level=0))
    for (x, z) in ((R - 4, R - 4), (-R + 4, R - 4), (R - 4, -R + 4), (-R + 4, -R + 4)):
        w.setze(x, 1, z, w.b("chiseled_quartz_block"))
        for yy in range(2, 5):
            w.setze(x, yy, z, w.b("calcite"))
        w.setze(x, 5, z, w.b("smooth_quartz"))
    return w


def brunnenhaus(seed, g=1):
    """Brunnenhaus: ein offener Säulenpavillon mit Ziegeldach, unter dem Wasser aus Löwenköpfen in ein langes
    Marmorbecken sprudelt, Krüge stehen bereit."""
    w = _neu(seed)
    s = S[g]
    B, T = int(10 * s + 5), int(6 * s + 4)
    zl = boden(w, int(B * 0.8))
    H = int(4 * s + 3)
    tempel(w, 0, 0, B, T, 1, H, cella=False)
    for x in range(-B // 2 + 2, B // 2 - 1):
        for z in range(-T // 2 + 2, T // 2 - 1):
            w.setze(x, 1, z, w.b("quartz_bricks") if z in (-T // 2 + 2, T // 2 - 2) or x in (-B // 2 + 2,
                                                                                            B // 2 - 2) else
                    w.b("water", level=0))
    for x in range(-B // 2 + 3, B // 2 - 2, 3):
        w.setze(x, 3, -T // 2 + 1, w.b("gold_block"))
        w.setze(x, 2, -T // 2 + 2, w.b("water", level=0))
    for k in range(3):
        w.setze(-B // 2 + 1 + k, 1, T // 2 + 1, w.b("decorated_pot", facing="north", waterlogged=False,
                                                    cracked=False))
    zypressen(w, zl, 3 + g, seed)
    return w


def antikerhafen(seed, g=2):
    """Antiker Hafen: ein runder Kriegshafen mit steinerner Mole, Schiffshäusern unter Ziegeldächern, zwei
    Trieren mit Rudern und einem kleinen Leuchtfeuer an der Hafeneinfahrt."""
    from boote import kogge
    w = _neu(seed)
    s = S[g]
    R = int(16 * s + 8)
    for x in range(-R - 4, R + 5):
        for z in range(-R - 4, R + 5):
            d = math.hypot(x, z)
            if d <= R + 4:
                for y in range(-3, 1):
                    w.setze(x, y, z, w.b("water", level=0) if d < R - 2 and y > -3 else w.b("stone_bricks"))
                if d >= R - 2:
                    w.setze(x, 1, z, w.b("smooth_stone"))
    for x in range(-2, 3):
        for z in range(R - 3, R + 5):
            for y in range(-3, 2):
                w.setze(x, y, z, w.b("water", level=0) if y < 1 else w.b("air"))
            w.bloecke.pop((x, 1, z), None)
    for k in range(6 + g):
        a = math.pi + k / (6 + g) * math.pi
        x, z = round(math.cos(a) * (R - 1)), round(math.sin(a) * (R - 1))
        for yy in range(2, 5):
            w.setze(x, yy, z, w.b("quartz_pillar", axis="y"))
        w.setze(x, 5, z, w.b("mcw:orange_terracotta_roof" if False else "granite"))
    for sx in (-3, 3):
        for yy in range(2, int(6 * s) + 4):
            w.setze(sx, yy, R + 2, w.b("smooth_stone"))
        w.setze(sx, int(6 * s) + 4, R + 2, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                waterlogged=False))
    for k in range(2):
        einfuegen(w, kogge(seed + k, max(0, g - 1)), -int(R * 0.3) + k * int(R * 0.6), 0, -int(R * 0.2) + k * 4)
    return w


def graeberstrasse(seed, g=2):
    """Gräberstraße: eine gepflasterte Straße vor der Stadt, gesäumt von Grabmälern – kleine Tempel, Altäre,
    Rundgräber und Pinien, mit Inschriftentafeln."""
    w = _neu(seed)
    s = S[g]
    L = int(18 * s + 10)
    zl = boden(w, L, rund=False, mat=M(w, [("grass_block", 1)]))
    for x in range(-L, L + 1):
        for z in (-1, 0, 1):
            w.setze(x, 0, z, w.b(["cobblestone", "stone_bricks", "andesite"][(x * 3 + z) % 3]))
    rng = w.rng
    for k, x in enumerate(range(-L + 3, L - 2, int(6 * s + 4))):
        for sz in (-1, 1):
            z = sz * 5
            art = (k + (sz > 0)) % 3
            if art == 0:
                tempel(w, x, z, 5, 5, 1, 3, cella=True)
            elif art == 1:
                for yy in range(1, 4):
                    for dx in range(-2, 3):
                        for dz in range(-2, 3):
                            if math.hypot(dx, dz) <= 2.4:
                                w.setze(x + dx, yy, z + dz, w.b("smooth_stone" if yy < 3 else "mossy_cobblestone"))
            else:
                for yy in range(1, 3):
                    w.setze(x, yy, z, w.b("quartz_bricks"))
                w.setze(x, 3, z, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
    zypressen(w, zl, 4 + g * 2, seed)
    return w


def felsentempel(seed, g=2):
    """Felsentempel: in eine rote Sandsteinwand gemeißelte Prachtfassade mit zwei Säulengeschossen, Giebel und
    Rundtempelchen in der Mitte, davor ein schmaler Schluchtenboden."""
    w = _neu(seed)
    s = S[g]
    B, H = int(14 * s + 8), int(18 * s + 8)
    rng = w.rng
    for x in range(-B - 4, B + 5):
        for y in range(-1, H + 6):
            for z in range(-6, 1):
                w.setze(x, y, z, w.b(["red_sandstone", "smooth_red_sandstone", "orange_terracotta", "terracotta"]
                                     [int((y + 2 * math.sin(x * 0.3)) / 2) % 4]))
    for x in range(-B - 4, B + 5):
        for z in range(1, 8):
            w.setze(x, 0, z, w.b("red_sand"))
    rs = "smooth_sandstone"
    for x in range(-B // 2, B // 2 + 1):
        for y in range(1, H):
            w.setze(x, y, 0, w.b("cut_red_sandstone"))
    for x in range(-B // 2, B // 2 + 1, 3):
        for y in range(1, H // 2):
            w.setze(x, y, 1, w.b(rs))
        for y in range(H // 2 + 2, H - 2):
            w.setze(x, y, 1, w.b(rs)) if abs(x) > B // 4 or abs(x) < 2 else None
    for x in range(-B // 2 - 1, B // 2 + 2):
        w.setze(x, H // 2, 1, w.b("chiseled_sandstone"))
        w.setze(x, H // 2 + 1, 1, w.b("cut_sandstone"))
    for k in range(B // 2):
        for x in range(-B // 2 + k, B // 2 - k + 1):
            w.setze(x, H // 2 + 2 + k // 2, 1, w.b("cut_sandstone")) if k < 4 else None
    for y in range(1, 4):
        for x in range(-1, 2):
            w.bloecke.pop((x, y, 0), None)
            w.bloecke.pop((x, y, -1), None)
    for k in range(5):
        a = k / 5 * 3.14
        saeule(w, round(math.cos(a) * 2), H // 2 + 2, 2 + round(math.sin(a)), int(4 * s + 2), mat="smooth_sandstone",
               kapitell="chiseled_sandstone", basis="cut_sandstone")
    return w


def stufentempel(seed, g=2):
    """Stufentempel: eine steile Stufenpyramide mit Freitreppe auf jeder Seite, oben ein Tempelhaus mit
    Federschmuck-Kamm, Feuerschalen an den Treppen und Dschungelpflanzen am Fuß."""
    w = _neu(seed)
    s = S[g]
    n = 5 + g
    R0 = int(12 * s + 6)
    st = M(w, [("mossy_stone_bricks", 2), ("stone_bricks", 2), ("cracked_stone_bricks", 1), ("tuff", 1)])
    zl = boden(w, R0 + 2, rund=False, mat=M(w, [("grass_block", 1)]))
    h = 2
    stp = max(1, (R0 - 4) // n)
    for k in range(n):
        r = R0 - k * stp
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                for y in range(1 + k * h, 1 + (k + 1) * h):
                    w.setze(x, y, z, st(x, y, z))
    top = 1 + n * h
    for (dx, dz, f) in ((0, 1, "north"), (0, -1, "south"), (1, 0, "west"), (-1, 0, "east")):
        for i in range(n * h):
            for q in (-1, 0, 1):
                d = R0 - i * stp / h
                x = round(dx * d + (q if dz else 0))
                z = round(dz * d + (q if dx else 0))
                w.setze(x, 1 + i, z, treppe(w, "stone_brick", f))
    r = max(2, R0 - n * stp)
    for x in range(-r + 1, r):
        for z in range(-r + 1, r):
            for y in range(top, top + 4):
                if abs(x) == r - 1 or abs(z) == r - 1:
                    w.setze(x, y, z, st(x, y, z))
    for x in range(-r + 1, r):
        w.setze(x, top + 4, 0, w.b("red_terracotta"))
        w.setze(x, top + 5, 0, w.b("lime_terracotta") if x % 2 else w.b("gold_block"))
    for k in range(4):
        a = k * 1.571 + 0.785
        x, z = round(math.cos(a) * (R0 + 1)), round(math.sin(a) * (R0 + 1))
        w.setze(x, 1, z, w.b("cauldron"))
        w.setze(x, 2, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    zypressen(w, zl, 2 + g, seed)
    return w


def peristylhaus(seed, g=1):
    """Peristylhaus: ein vornehmes Stadthaus mit rotem Ziegeldach um einen Säulengarten mit Wasserbecken,
    Rosenbeeten und Brunnenfigur, Mosaikboden im Atrium."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    zl = boden(w, R + 1, rund=False)
    mm = M(w, [("white_terracotta", 2), ("smooth_sandstone", 1), ("calcite", 1)])
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            rand = max(abs(x), abs(z))
            if rand == R or rand == R - 4:
                for y in range(1, 5):
                    if rand == R or (x + z) % 3:
                        w.setze(x, y, z, mm(x, y, z))
                    else:
                        w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
            elif rand < R - 4:
                inner = rand < R - 7
                w.setze(x, 0, z, w.b("water", level=0) if rand < 2 else w.b("grass_block", snowy=False) if inner
                        else w.b("orange_terracotta" if (x + z) % 2 else "white_terracotta"))
                if inner and rand >= 2 and w.rng.random() < 0.4:
                    w.setze(x, 1, z, w.b("rose_bush", half="lower"))
                    w.setze(x, 2, z, w.b("rose_bush", half="upper"))
    for (z0, z1, x0, x1, fx) in ((-R, -R + 4, -R, R, True), (R - 4, R, -R, R, True), (-R + 4, R - 4, -R, -R + 4, False),
                                 (-R + 4, R - 4, R - 4, R, False)):
        satteldach(w, x0, z0, x1, z1, 5, Dachmat(w, ["mcw:orange_terracotta", "brick", "granite"]), first_x=fx,
                   ue=1, traufe="birch", knick=False, giebelfenster=False, firstzier=False)
    for y in range(1, 4):
        w.bloecke.pop((0, y, R), None)
    w.setze(0, 1, 0, w.b("quartz_bricks"))
    w.setze(0, 2, 0, w.b("calcite"))
    return w


def reiterstandbild(seed, g=2):
    """Reiterstandbild: auf einem hohen Marmorsockel ein bronzener Reiter auf schreitendem Pferd, den Arm zum Gruß
    erhoben, der Sockel mit Girlanden und Inschrift."""
    from skulptur import Skulptur, ell, kap
    w = _neu(seed)
    s = S[g]
    zl = boden(w, int(8 * s + 5))
    B, T = int(3 * s + 2), int(5 * s + 3)
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            for y in range(1, int(4 * s) + 3):
                w.setze(x, y, z, w.b("quartz_bricks" if (abs(x) == B or abs(z) == T) else "smooth_quartz"))
    top = int(4 * s) + 3
    Sk = Skulptur(w, s)
    Sk.mat("b", lambda *a: w.b(["waxed_oxidized_copper", "waxed_weathered_copper", "waxed_oxidized_cut_copper"]
                               [(a[0] + a[1]) % 3]))
    Sk.plus(ell(0, 6, 0, 1.8, 1.8, 4.0), "b")
    for sz in (-1, 1):
        Sk.plus(kap((1.0, 5, sz * 2.8), (1.0, 0.3, sz * 3.0 + (1.2 if sz > 0 else 0)), 0.6, 0.45), "b")
        Sk.plus(kap((-1.0, 5, sz * 2.8), (-1.0, 0.3, sz * 3.0), 0.6, 0.45), "b")
    Sk.plus(kap((0, 7, 3.4), (0, 10, 4.6), 1.1, 0.8), "b")
    Sk.plus(kap((0, 10, 4.6), (0, 9.2, 6.4), 0.8, 0.5), "b")
    Sk.plus(kap((0, 7.6, 0), (0, 11.4, 0), 1.0, 0.8), "b")
    Sk.plus(ell(0, 12.4, 0, 0.7, 0.8, 0.7), "b")
    Sk.plus(kap((0.8, 10.6, 0), (1.6, 13.6, 0.8), 0.35), "b")
    for sx in (-1, 1):
        Sk.plus(kap((sx * 1.2, 8, 0), (sx * 1.6, 5.6, 0.6), 0.4), "b")
    Sk.plus(kap((0, 6.5, -3.8), (0, 3.5, -5), 0.4, 0.2), "b")
    Sk.rendern((-4, 0, -6), (4, 15, 8), versatz=(0.5, top, 0.5))
    zypressen(w, zl, 4, seed)
    return w


def roemerbruecke(seed, g=2):
    """Römerbrücke: eine lange Steinbrücke mit mehreren halbrunden Bögen und Wellenbrechern an den Pfeilern spannt
    sich über einen breiten Fluss, oben ein Pflasterweg mit Brüstung."""
    w = _neu(seed)
    s = S[g]
    n = 3 + g
    sp = int(6 * s + 4)
    L = n * sp
    for x in range(-L // 2 - 6, L // 2 + 7):
        for z in range(-int(8 * s + 6), int(8 * s + 7)):
            ufer = abs(x) > L // 2 - 1
            for y in range(-3, 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if ufer and y == 0 else w.b("dirt") if ufer else
                        w.b("water", level=0) if y > -3 else w.b("gravel"))
    st = M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 1), ("andesite", 1)])
    Hb = sp // 2 + 2
    for x in range(-L // 2, L // 2 + 1):
        t = (x + L // 2) % sp
        for z in (-2, -1, 0, 1, 2):
            for y in range(-2, Hb + 1):
                bogen = math.hypot(t - sp / 2, y) < sp / 2 - 0.6 and t != 0
                if not bogen:
                    w.setze(x, y, z, st(x, y, z))
            if abs(z) == 2:
                w.setze(x, Hb + 1, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="low",
                                          west="low", waterlogged=False))
            else:
                w.setze(x, Hb, z, w.b(["cobblestone", "andesite", "stone_bricks"][(x + z) % 3]))
        if t == 0:
            for sz in (-1, 1):
                for k in range(1, 3):
                    for y in range(-2, 2):
                        w.setze(x, y, sz * (2 + k), st(x, y, k))
    return w


def labyrinth(seed, g=2):
    """Labyrinth: ein verschlungener Irrgarten aus hohen, bemoosten Steinmauern auf quadratischem Grundriss, in
    der Mitte ein kleiner Altar mit Stierkopf-Relief, Fackeln an den Wänden."""
    w = _neu(seed)
    s = S[g]
    n = int(6 + 4 * s) | 1
    zelle = 3
    R = n * zelle // 2
    rng = w.rng
    boden(w, R + 2, rund=False, mat=M(w, [("gravel", 2), ("coarse_dirt", 1), ("dirt_path", 1)]))
    wand = [[True] * (2 * n + 1) for _ in range(2 * n + 1)]
    stack = [(0, 0)]
    besucht = {(0, 0)}
    wand[1][1] = False
    while stack:
        cx, cz = stack[-1]
        nb = [(cx + dx, cz + dz, dx, dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= cx + dx < n and 0 <= cz + dz < n and (cx + dx, cz + dz) not in besucht]
        if not nb:
            stack.pop()
            continue
        nx, nz, dx, dz = nb[int(rng.random() * len(nb))]
        wand[2 * cx + 1 + dx][2 * cz + 1 + dz] = False
        wand[2 * nx + 1][2 * nz + 1] = False
        besucht.add((nx, nz))
        stack.append((nx, nz))
    wand[0][1] = False
    m = n // 2
    for i in range(2 * m, 2 * m + 3):
        for j in range(2 * m, 2 * m + 3):
            wand[i][j] = False
    st = M(w, [("mossy_stone_bricks", 3), ("stone_bricks", 2), ("cracked_stone_bricks", 1)])
    H = int(3 + s)
    k = 1.5
    for i in range(2 * n + 1):
        for j in range(2 * n + 1):
            if wand[i][j]:
                x0, z0 = int(i * k) - R, int(j * k) - R
                for x in range(x0, x0 + 2):
                    for z in range(z0, z0 + 2):
                        for y in range(1, H + 1):
                            w.setze(x, y, z, st(x, y, z))
    c = int((2 * m + 1) * k) - R
    w.setze(c, 1, c, w.b("chiseled_stone_bricks"))
    w.setze(c, 2, c, w.b("skeleton_skull", rotation=0) if False else w.b("bone_block", axis="y"))
    return w


def loewentor(seed, g=2):
    """Löwentor: ein mächtiges Tor aus Zyklopenmauerwerk, über dem Sturz ein dreieckiges Relief mit zwei Löwen um
    eine Säule, beidseitig dicke Mauern und ein Rampenweg."""
    w = _neu(seed)
    s = S[g]
    B, H = int(14 * s + 8), int(8 * s + 5)
    zl = boden(w, B, rund=False, mat=M(w, [("coarse_dirt", 1), ("gravel", 1)]))
    rng = w.rng
    for x in range(-B, B + 1):
        for z in range(-2, 3):
            for y in range(1, H + 1):
                w.setze(x, y, z, w.b(["stone", "andesite", "tuff", "cobblestone"][int(rng.random() * 4)]) if
                        (x + y * 3 + z) % 5 else w.b("smooth_stone"))
    tb = int(2 * s + 1)
    for x in range(-tb, tb + 1):
        for z in range(-3, 4):
            for y in range(1, int(H * 0.6)):
                w.bloecke.pop((x, y, z), None)
    for x in range(-tb - 1, tb + 2):
        w.setze(x, int(H * 0.6), 3, w.b("smooth_stone"))
    hr = int(H * 0.35)
    for k in range(hr):
        for x in range(-hr + k, hr - k + 1):
            w.setze(x, int(H * 0.6) + 1 + k, 3, w.b("smooth_sandstone"))
    w.setze(0, int(H * 0.6) + 1, 4, w.b("chiseled_sandstone"))
    w.setze(0, int(H * 0.6) + 2, 4, w.b("chiseled_sandstone"))
    for sx in (-1, 1):
        for k in range(min(3, hr)):
            w.setze(sx * (2 + k // 2), int(H * 0.6) + 1 + k, 4, w.b("yellow_terracotta"))
    return w


def kuppelgrab(seed, g=2):
    """Kuppelgrab: ein in den Hügel gebautes Bienenkorbgrab mit falschem Gewölbe aus Steinringen, ein langer
    ummauerter Gang führt zum hohen Portal mit Entlastungsdreieck."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 4)
    zl = boden(w, R + 6, mat=M(w, [("grass_block", 1)]))
    for x in range(-R - 4, R + 5):
        for z in range(-R - 4, R + 5):
            d = math.hypot(x, z)
            if d <= R + 4:
                h = int((R + 1) * math.sqrt(max(0, 1 - (d / (R + 4)) ** 2)) * 1.1)
                for y in range(1, h + 1):
                    w.setze(x, y, z, w.b("dirt") if y < h else w.b("grass_block", snowy=False))
    for y in range(1, int(R * 1.3)):
        r = R * math.sqrt(max(0, 1 - (y / (R * 1.3)) ** 2))
        for x in range(-R - 1, R + 2):
            for z in range(-R - 1, R + 2):
                d = math.hypot(x, z)
                if d <= r:
                    w.setze(x, y, z, w.b("stone_bricks") if d > r - 1 else w.b("air"))
    for z in range(R - 1, R + 8):
        for x in range(-2, 3):
            for y in range(1, 5):
                if abs(x) == 2:
                    w.setze(x, y, z, w.b("stone_bricks"))
                else:
                    w.bloecke.pop((x, y, z), None)
    for k in range(3):
        for x in range(-1 + k // 2, 2 - k // 2):
            w.setze(x, 5 + k, R, w.b("cobbled_deepslate"))
    return w


def amphorenkontor(seed, g=1):
    """Amphorenkontor: ein Handelshaus mit offener Lagerhalle, in der hunderte Amphoren in Reihen lagern, davor ein
    Kai mit Kran, Waagen und Ballen."""
    from feinbau import kram
    w = _neu(seed)
    s = S[g]
    B, T = int(12 * s + 6), int(7 * s + 4)
    zl = boden(w, int(B * 0.8), rund=False)
    mm = M(w, [("white_terracotta", 2), ("smooth_sandstone", 1)])
    x0, z0, x1, z1 = -B // 2, -T // 2, B // 2, T // 2
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if x in (x0, x1) or z == z0:
                for y in range(1, 5):
                    w.setze(x, y, z, mm(x, y, z))
            elif z == z1 and x % 3 == 0:
                saeule(w, x, 1, z, 4, mat="smooth_sandstone", kapitell="cut_sandstone", basis="smooth_sandstone")
            elif z < z1 - 1 and (x + z) % 2 == 0:
                w.setze(x, 1, z, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False))
    satteldach(w, x0, z0, x1, z1, 5, Dachmat(w, ["mcw:orange_terracotta", "brick", "granite"]), first_x=True,
               traufe="birch", knick=False)
    kram(w, 0, 1, z1 + 4, 6)
    return w


def saeulenfeld(seed, g=2):
    """Säulenfeld: die Ruinen eines riesigen Tempels – Reihen stehender und gestürzter Säulen, zerbrochene
    Trommeln, ein halbes Gebälk und Mohnblumen im Gras."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 8)
    zl = boden(w, R, rund=False, mat=M(w, [("grass_block", 3), ("smooth_stone", 1), ("coarse_dirt", 1)]))
    rng = w.rng
    H = int(8 * s + 5)
    for x in range(-R + 2, R - 1, 4):
        for z in (-R // 2, R // 2):
            r = rng.random()
            if r < 0.55:
                h = H if r < 0.3 else int(H * (0.3 + rng.random() * 0.5))
                saeule(w, x, 1, z, h, r=1 if g >= 2 else 0)
            elif r < 0.85:
                a = rng.random() * 3.14
                for k in range(H):
                    w.setze(x + round(math.cos(a) * k), 1, z + round(math.sin(a) * k), w.b("quartz_pillar",
                                                                                          axis="x"))
    for x in range(-R + 2, -R // 3):
        w.setze(x, H + 1, -R // 2, w.b("smooth_quartz"))
    for (x, z) in zl if False else []:
        pass
    for k in range(int(30 * s)):
        x, z = int((rng.random() - 0.5) * R * 2), int((rng.random() - 0.5) * R * 2)
        if w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("poppy" if rng.random() < 0.5 else "grass"))
    return w


def goetterthron(seed, g=2):
    """Götterthron: ein gewaltiger, leerer Marmorthron mit goldenen Armlehnen und Löwenfüßen auf einer
    Stufenplattform, flankiert von Feuerschalen – als warte er auf einen Riesen."""
    w = _neu(seed)
    s = S[g]
    zl = boden(w, int(10 * s + 6))
    y = stufen(w, -int(5 * s + 3), -int(4 * s + 2), int(5 * s + 3), int(4 * s + 2), 3)
    B = int(4 * s + 2)
    for x in range(-B, B + 1):
        for z in range(-B, B + 1):
            for yy in range(y, y + int(3 * s + 2)):
                w.setze(x, yy, z, w.b("smooth_quartz"))
    ys = y + int(3 * s + 2)
    for x in range(-B, B + 1):
        for yy in range(ys, ys + int(8 * s + 4)):
            w.setze(x, yy, -B, w.b("quartz_bricks" if abs(x) < B else "quartz_pillar", **({} if abs(x) < B else
                                                                                     {"axis": "y"})))
    for x in range(-B, B + 1):
        w.setze(x, ys + int(8 * s + 4), -B, w.b("gold_block"))
    for sx in (-1, 1):
        for z in range(-B, B + 1):
            for yy in range(ys, ys + int(2 * s + 2)):
                w.setze(sx * B, yy, z, w.b("gold_block" if yy == ys + int(2 * s + 1) else "smooth_quartz"))
    for sx in (-1, 1):
        x = sx * (B + 4)
        w.setze(x, y, B, w.b("gold_block"))
        w.setze(x, y + 1, B, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    zypressen(w, zl, 4 + g, seed)
    return w


ANTIKE3 = {
    "bibliothek": ("Bibliothek", bibliothek),
    "akropolis": ("Akropolis", akropolis),
    "siegessaeule": ("Siegessäule", siegessaeule),
    "agora": ("Agora", agora),
    "odeon": ("Odeon", odeon),
    "palaestra": ("Palästra", palaestra),
    "brunnenhaus": ("Brunnenhaus", brunnenhaus),
    "antikerhafen": ("Antiker Hafen", antikerhafen),
    "graeberstrasse": ("Gräberstraße", graeberstrasse),
    "felsentempel": ("Prachtfassade im Fels", felsentempel),
    "stufentempel": ("Treppenpyramide", stufentempel),
    "peristylhaus": ("Peristylhaus", peristylhaus),
    "reiterstandbild": ("Reiterstandbild", reiterstandbild),
    "roemerbruecke": ("Römerbrücke", roemerbruecke),
    "labyrinth": ("Labyrinth", labyrinth),
    "loewentor": ("Löwentor", loewentor),
    "kuppelgrab": ("Kuppelgrab", kuppelgrab),
    "amphorenkontor": ("Amphorenkontor", amphorenkontor),
    "saeulenfeld": ("Säulenfeld", saeulenfeld),
    "goetterthron": ("Götterthron", goetterthron),
}

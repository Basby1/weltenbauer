"""Hexenwerk II – zwanzig weitere verwunschene Orte: Besenmacherei, Spiegelhütte, Verdrehter Hexenturm,
Kräuterscheune, Kristallkugel-Pavillon, Katzenhaus, Hexenbrücke, Mondsichel-Hütte, Bücherstapel-Turm, Kesselhaus,
Flaschenbaum, Dornentor, Walpurgisfeuer, Schicksalsweberei, Kürbiswagen, Eulenturm, Mondspiegel-Brunnen,
Giftgarten, Sternstaub-Destille und Wurzelhöhle."""

from __future__ import annotations

import math

import numpy as np

from erw_basis import M, S, baumrand, figur, haus, hoehe, wiese
from feinbau import Dachmat, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, laubball, rohr
from lib import Rauschen
from skulptur import ell, kap, kasten, kegel, kreisrand


def hexenboden(w, R, huegel=0.4):
    zellen = wiese(w, R, huegel, art="moor", blumen=0.0)
    rng = w.rng
    for (x, z), h in zellen.items():
        q = rng.random()
        if q < 0.02:
            w.setze(x, h + 1, z, w.b("red_mushroom"))
        elif q < 0.035:
            w.setze(x, h + 1, z, w.b("brown_mushroom"))
        elif q < 0.06:
            w.setze(x, h + 1, z, w.b("fern"))
    return zellen


def krumm(w, cx, cz, y0, B, T, H, wand, dach=("dark_oak", "mossy_cobblestone"), neig=0.25, tuer_s="south"):
    """Schiefes Hexenhaus: Wände neigen sich mit der Höhe, Hexenhut-Dach."""
    x0, z0, x1, z1 = cx - B // 2, cz - T // 2, cx + B // 2, cz + T // 2
    for y in range(y0, y0 + H):
        o = round((y - y0) * neig)
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if x in (x0, x1) or z in (z0, z1):
                    fen = y == y0 + 1 and (x + z) % 3 == 0 and not (x in (x0, x1) and z in (z0, z1))
                    w.setze(x + o, y, z, w.b("purple_stained_glass_pane") if fen else wand(x, y, z))
                else:
                    w.bloecke.pop((x + o, y, z), None)
    d = {"south": (cx, z1), "north": (cx, z0), "east": (x1, cz), "west": (x0, cz)}[tuer_s]
    for y in (y0, y0 + 1):
        w.bloecke.pop((d[0] + round((y - y0) * neig), y, d[1]), None)
    o = round(H * neig)
    r = max(B, T) / 2 + 0.5
    top = kegeldach(w, cx + o, cz, y0 + H, int(r), Dachmat(w, list(dach)), h=int(r * 3), form="nadel",
                    spitze="lightning_rod")
    return top


def holzwand(w):
    return M(w, [("dark_oak_planks", 3), ("spruce_planks", 1), ("mossy_cobblestone", 1)])


def katze(w, fell="black_wool", auge="lime_concrete"):
    f = w.b(fell)
    return [(ell(0, 1.0, 0, 0.6, 0.9, 0.55), f), (ell(0.1, 2.2, 0, 0.5, 0.5, 0.5), f),
            (kegel(0.1, 0.25, 2.5, 3.1, 0.18, 0.02), f), (kegel(0.1, -0.25, 2.5, 3.1, 0.18, 0.02), f),
            (ell(0.5, 2.3, 0.2, 0.08, 0.12, 0.1), w.b(auge)), (ell(0.5, 2.3, -0.2, 0.08, 0.12, 0.1), w.b(auge)),
            (kap((-0.5, 0.3, 0), (-0.9, 1.6, 0), 0.15), f)]


# ============================================================================ Bauten

def besenmacherei(seed, g=1):
    """Besenmacherei: eine krumme Hütte, an deren Wänden Reisigbesen lehnen, Birkenreisig in Bündeln, ein
    Probierflug-Gestell mit schwebenden Besen an Ketten und ein Haufen Stiele."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    zellen = hexenboden(w, R)
    krumm(w, 0, -int(R * 0.25), 1, int(3 * s + 5) | 1, int(2 * s + 5) | 1, int(2 * s + 4), holzwand(w))
    for k in range(3 + g):
        x = -int(R * 0.5) + k * 3
        z = int(R * 0.25)
        for y in range(1, 4):
            w.setze(x, y, z, w.b("birch_fence"))
        w.setze(x, 1, z, w.b("hay_block", axis="y"))
    for k in range(3):
        x = int(R * 0.4)
        for y in range(1, 6):
            w.setze(x, y, -2 + k * 2, w.b("dark_oak_fence"))
    for k in range(3):
        y = 3 + k
        w.setze(int(R * 0.4) - 1, y, -2 + k * 2, w.b("chain", axis="y", waterlogged=False))
        for dx in range(-3, 0):
            w.setze(int(R * 0.4) - 1 + dx, y - 1, -2 + k * 2, w.b("birch_fence") if dx > -3 else
                    w.b("hay_block", axis="x"))
    for k in range(4):
        w.setze(-int(R * 0.5), 1, -2 + k, w.b("stripped_birch_log", axis="x"))
    _ = zellen
    return w


def spiegelhuette(seed, g=1):
    """Spiegelhütte: eine sechseckige Hütte, deren Wände aus Spiegelscherben (getöntes und klares Glas) bestehen, mit
    Silberrahmen, einem großen Zauberspiegel davor und Kerzen auf Ständern."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    hexenboden(w, R)
    r = 2.5 * s + 2.5
    H = int(2 * s + 4)
    for y in range(1, H + 1):
        for x, z in kreisrand(r):
            ang = math.atan2(z, x)
            kante = int((ang + math.pi) / (math.pi / 3) * 1.0 + 0.5) % 1 == 0 and abs(((ang + math.pi) % (math.pi / 3))
                                                                                    - 0.05) < 0.2
            w.setze(x, y, z, w.b("iron_block") if kante or y in (1, H) else
                    w.b(["glass", "tinted_glass", "light_gray_stained_glass"][(x + y + z) % 3]))
    kegeldach(w, 0, 0, H + 1, int(r), Dachmat(w, ["deepslate_tile", "polished_blackstone"]), form="nadel",
              eckig=True, spitze="end_rod")
    for y in (1, 2):
        w.bloecke.pop((0, y, round(r)), None)
    mz = round(r) + 3
    for y in range(1, int(4 + 2 * s)):
        for x in range(-2, 3):
            rand = abs(x) == 2 or y in (1, int(3 + 2 * s))
            w.setze(x, y, mz, w.b("gold_block") if rand else w.b("light_blue_stained_glass"))
    for sx in (-4, 4):
        for y in (1, 2):
            w.setze(sx, y, mz, w.b("dark_oak_fence"))
        w.setze(sx, 3, mz, w.b("candle", candles=3, lit=True, waterlogged=False))
    return w


def verdrehter_turm(seed, g=2):
    """Verdrehter Hexenturm: ein hoher, korkenzieherartig verdrehter Turm aus dunklem Holz und Stein, mit
    vorspringenden Erkern, schiefen Fenstern, einer Spitzhaube und einem Raben-Wetterfahnen-Hut."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    hexenboden(w, R)
    H = int(16 * s + 10)
    r0 = 2.6 * s + 2
    wand = holzwand(w)
    for y in range(1, H):
        t = y / H
        cx = round(math.sin(t * math.pi * 1.5) * 2.5 * s)
        cz = round(math.cos(t * math.pi * 1.5) * 1.5 * s - 1.5 * s)
        r = r0 * (1 - 0.35 * t)
        for x, z in kreisrand(r, cx, cz):
            fen = y % 5 == 2 and (x - cx) * 2 > r
            w.setze(x, y, z, w.b("orange_stained_glass_pane") if fen else wand(x, y, z) if y > 2 else
                    w.b("cobblestone"))
        if y % 7 == 4:
            for dx in range(round(r), round(r) + 3):
                for dz in (-1, 0, 1):
                    w.setze(cx + dx, y - 1, cz + dz, w.b("dark_oak_planks"))
                    w.setze(cx + dx, y + 2, cz + dz, w.b("dark_oak_slab", type="bottom", waterlogged=False))
            w.setze(cx + round(r) + 2, y, cz, w.b("dark_oak_fence"))
            w.setze(cx + round(r) + 2, y + 1, cz, w.b("purple_stained_glass_pane"))
    t = 1
    cx = round(math.sin(t * math.pi * 1.5) * 2.5 * s)
    cz = round(math.cos(t * math.pi * 1.5) * 1.5 * s - 1.5 * s)
    top = kegeldach(w, cx, cz, H, int(r0 * 0.7), Dachmat(w, ["dark_oak", "polished_blackstone"]),
                    h=int(r0 * 3), form="nadel", spitze="black_wool")
    w.setze(cx + 1, top, cz, w.b("black_wool"))
    for y in (1, 2):
        w.bloecke.pop((0, y, round(r0) - round(1.5 * s)), None)
    return w


def kraeuterscheune(seed, g=1):
    """Kräuterscheune: eine alte Scheune, unter deren Dachbalken Hunderte Kräuterbündel (Blätterblöcke, Blüten)
    zum Trocknen hängen, mit Mörsern, Kräutertruhen und einem Beet mit Heilkräutern davor."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = hexenboden(w, R)
    B, T = int(5 * s + 6) | 1, int(3 * s + 5) | 1
    top = haus(w, 0, -int(R * 0.25), B, T, 1, holzwand(w), holz="dark_oak", H=4, dach=("dark_oak", "spruce"),
               tuer_s="south", schorn=False, steil=2)
    rng = w.rng
    for x in range(-B // 2 + 1, B // 2):
        for z in range(-int(R * 0.25) - T // 2 + 1, -int(R * 0.25) + T // 2):
            if rng.random() < 0.5:
                w.setze(x, 4, z, w.b("chain", axis="y", waterlogged=False))
                w.setze(x, 3, z, w.b(["azalea_leaves", "flowering_azalea_leaves", "oak_leaves", "dark_oak_leaves"]
                                     [int(rng.integers(4))], persistent=True, distance=1, waterlogged=False))
    gz = -int(R * 0.25) + T // 2 + 2
    for x in range(-B // 2, B // 2 + 1):
        for z in range(gz, gz + 3):
            w.setze(x, zellen.get((x, z), 0), z, w.b("farmland", moisture=7))
            w.setze(x, zellen.get((x, z), 0) + 1, z, w.b(["allium", "lily_of_the_valley", "blue_orchid",
                                                          "azure_bluet"][(x + z) % 4]))
    _ = top
    return w


def kristallkugel_pavillon(seed, g=1):
    """Kristallkugel-Pavillon: ein runder Pavillon mit violetten Vorhängen und Sternenstoff-Dach, in der Mitte auf
    einem Tischchen eine große leuchtende Kristallkugel, ringsum Kissen und Räucherschalen."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    hexenboden(w, R)
    r = 3 * s + 2.5
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        for y in range(1, 5):
            w.setze(x, y, z, w.b("dark_oak_fence"))
        if i % 2:
            for y in range(2, 5):
                w.setze(round(math.cos(a + 0.2) * r), y, round(math.sin(a + 0.2) * r), w.b("purple_wool"), False)
    for k in range(int(r * 1.5) + 1):
        rr = (r + 1) * (1 - k / (r * 1.5 + 1))
        for x, z in kreisrand(max(0.4, rr)):
            w.setze(x, 5 + k, z, w.b("blue_wool") if (x + z + k) % 5 else w.b("yellow_wool"))
    for x in range(-int(r) + 1, int(r)):
        for z in range(-int(r) + 1, int(r)):
            if math.hypot(x, z) < r - 0.5:
                w.setze(x, 0, z, w.b("purple_carpet") if False else w.b("purple_terracotta"))
    w.setze(0, 1, 0, w.b("dark_oak_fence"))
    kugel(w, 0, 2.6, 0, 0.9 + 0.3 * s, w.b("light_blue_stained_glass"))
    w.setze(0, 2, 0, w.b("sea_lantern"))
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        w.setze(round(math.cos(a) * 2), 1, round(math.sin(a) * 2), w.b(["red_wool", "purple_wool"][i % 2]))
    return w


def katzenhaus(seed, g=1):
    """Katzenhaus: ein windschiefes Häuschen mit Katzenklappen und Kratzbalken, auf Dach, Fensterbänken und Zaun
    sitzen schwarze, graue und rote Katzen-Figuren mit leuchtenden Augen, Milchschalen davor."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    zellen = hexenboden(w, R)
    top = krumm(w, 0, -1, 1, int(3 * s + 4) | 1, int(2 * s + 4) | 1, int(2 * s + 3), holzwand(w), neig=0.2)
    felle = ["black_wool", "gray_wool", "orange_wool", "black_wool", "white_wool"]
    rng = w.rng
    pos = [(0, top - 1, -1), (-int(R * 0.4), 1, int(R * 0.3)), (int(R * 0.4), 1, int(R * 0.2)),
           (int(R * 0.3), 1, -int(R * 0.45)), (-int(R * 0.45), 1, -int(R * 0.3))]
    for k, (x, y, z) in enumerate(pos[:3 + g]):
        yy = hoehe(w, x, z, top + 5) + 1 if k else y
        figur(w, 0.6 * s + 0.4, katze(w, felle[k % 5], "yellow_concrete" if k % 2 else "lime_concrete"),
              (-1, -1, -1), (1, 4, 1), pos=(x, yy, z), winkel=rng.random() * 6.28)
    for x in range(-int(R * 0.6), int(R * 0.6)):
        w.setze(x, hoehe(w, x, int(R * 0.6), 5) + 1, int(R * 0.6), zaun(w, "dark_oak"))
    for k in range(3):
        w.setze(-2 + k * 2, 1, int(R * 0.15), w.b("cauldron") if k % 2 else w.b("white_carpet"))
    _ = zellen
    return w


def hexenbruecke(seed, g=2):
    """Hexenbrücke: eine buckelige, schiefe Holzbrücke mit krummem Geländer über einen dunklen Moorbach, behängt mit
    Laternen, Knochen-Mobiles und Kräuterbündeln, an einem Ende ein kleiner Wegschrein."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = hexenboden(w, R)
    for z in range(-R - 2, R + 3):
        for dx in range(-int(2 * s + 2), int(2 * s + 3)):
            x = dx + round(math.sin(z / 4) * 1.5)
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
    L = int(2 * s + 2) + 4
    for x in range(-L, L + 1):
        y = 1 + round(2 * s * math.cos(math.pi * x / (2 * L)))
        for z in (-1, 0, 1):
            w.setze(x, y, z + round(math.sin(x / 2) * 0.6), w.b("dark_oak_planks") if (x + z) % 3 else
                    w.b("spruce_planks"))
        for z in (-2, 2):
            w.setze(x, y + 1, z + round(math.sin(x / 2) * 0.6), w.b("dark_oak_fence"))
        if x % 3 == 0:
            for z in (-2, 2):
                w.setze(x, y + 2, z, w.b("dark_oak_fence"))
                w.setze(x, y + 3, z, w.b("lantern", hanging=False, waterlogged=False) if x % 2 else
                        w.b("bone_block", axis="y"))
    sx = L + 3
    for y in range(1, 4):
        w.setze(sx, y, 3, w.b("dark_oak_log", axis="y"))
    w.setze(sx, 4, 3, w.b("dark_oak_slab", type="bottom", waterlogged=False))
    w.setze(sx - 1, 2, 3, w.b("candle", candles=2, lit=True, waterlogged=False))
    return w


def mondsichelhuette(seed, g=2):
    """Mondsichel-Hütte: ein Haus in Form einer liegenden, nach oben offenen Mondsichel aus hellem Stein und blauen
    Schindeln, mit runden Fenstern, Sternen-Laternen an Ketten und einer Leiter zur oberen Spitze."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    hexenboden(w, R)
    Ra = 6 * s + 4
    Ri = Ra * 0.62
    dz = Ra * 0.45
    D = int(2 * s + 3)
    for x in range(-int(Ra) - 1, int(Ra) + 2):
        for y in range(0, int(Ra * 2) + 2):
            yy = y - Ra
            aus = x * x + yy * yy <= Ra * Ra
            inn = x * x + (yy - dz) ** 2 <= Ri * Ri
            if aus and not inn and y >= 1:
                for z in range(-D, D + 1):
                    rand = abs(z) == D or not (x * x + yy * yy <= (Ra - 1) ** 2 and
                                               not x * x + (yy - dz) ** 2 <= (Ri + 1) ** 2)
                    if rand:
                        w.setze(x, y, z, w.b("calcite") if (x + y) % 5 else w.b("light_blue_terracotta"))
                    else:
                        w.bloecke.pop((x, y, z), None)
    for k in range(4):
        a = -math.pi / 2 + (k - 1.5) * 0.45
        x, y = round(math.cos(a) * (Ra - 1.5)), round(Ra + math.sin(a) * (Ra - 1.5))
        if y >= 1:
            w.setze(x, y, D, w.b("light_blue_stained_glass"))
    for y in (1, 2):
        w.bloecke.pop((0, y, D), None)
    for k in range(5):
        x = round((k - 2) * Ri * 0.4)
        y = int(Ra * 2) - 1
        w.setze(x, y + 1, 0, w.b("chain", axis="y", waterlogged=False), False)
        w.setze(x, y, 0, w.b("end_rod", facing="down"), False)
    return w


def buecherturm(seed, g=2):
    """Bücherstapel-Turm: ein Turm aus riesigen, schief gestapelten Büchern in verschiedenen Farben mit hellen
    Seitenkanten, ganz oben ein aufgeschlagenes Buch als Dach und eine Leiter am Buchrücken."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    hexenboden(w, R)
    farben = ["red_terracotta", "blue_terracotta", "green_terracotta", "purple_terracotta", "brown_terracotta",
              "cyan_terracotta"]
    y = 1
    n = int(5 + 3 * s)
    rng = w.rng
    ox = 0
    for k in range(n):
        B = int((4 - k * 0.15) * s + 3)
        T = int((3 - k * 0.1) * s + 2)
        h = 1 + int(rng.random() * 1.5 * s + 1)
        ox += int((rng.random() - 0.5) * 2)
        drehung = k % 2
        for x in range(-B, B + 1):
            for z in range(-T, T + 1):
                xx, zz = (x, z) if drehung == 0 else (z, x)
                for yy in range(y, y + h):
                    seite = abs(z) == T and abs(x) < B
                    w.setze(xx + ox, yy, zz, w.b("white_concrete") if seite and x % 3 else
                            w.b(farben[k % 6]) if abs(x) == B or yy in (y, y + h - 1) else w.b("white_concrete"))
        y += h
    for x in range(-int(3 * s + 2), int(3 * s + 3)):
        for z in range(-int(2 * s + 2), int(2 * s + 3)):
            yy = y + round(abs(x) * 0.5)
            w.setze(x + ox, yy, z, w.b("white_concrete") if x != 0 else w.b("red_terracotta"))
    for yy in range(1, y):
        w.setze(int(4 * s + 4), yy, 0, w.b("ladder", facing="east", waterlogged=False), False)
    return w


def kesselhaus(seed, g=2):
    """Kesselhaus: ein Wohnhaus im Inneren eines riesigen, schwarzen Hexenkessels auf drei Füßen, mit Fenstern in der
    Bauchwand, einem Dach aus grünem Gebräu-Schaum (Schleimblöcke) und einem Schornstein als Kochlöffel."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    hexenboden(w, R)
    rk = 4.5 * s + 3
    yc = rk * 0.9 + 2
    for x in range(-int(rk) - 1, int(rk) + 2):
        for y in range(1, int(yc + rk * 0.7) + 1):
            for z in range(-int(rk) - 1, int(rk) + 2):
                d = math.sqrt(x * x + ((y - yc) / 0.9) ** 2 + z * z)
                if y - yc > rk * 0.6:
                    continue
                if rk - 1.1 < d <= rk:
                    fen = abs(y - yc) < 1 and (abs(x) < 1 or abs(z) < 1)
                    w.setze(x, y, z, w.b("orange_stained_glass") if fen else w.b("black_concrete") if (x + z) % 4 else
                            w.b("gray_concrete"))
                elif d <= rk - 1.1:
                    w.bloecke.pop((x, y, z), None)
    ytop = int(yc + rk * 0.6)
    rr = math.sqrt(max(0, rk * rk - (rk * 0.6 / 0.9) ** 2 * 0.81))
    for x, z in kreisrand(rr + 0.5):
        w.setze(x, ytop + 1, z, w.b("black_concrete"))
    for x in range(-int(rr), int(rr) + 1):
        for z in range(-int(rr), int(rr) + 1):
            if math.hypot(x, z) < rr:
                w.setze(x, ytop + (1 if (x * z) % 3 == 0 else 0), z, w.b("slime_block"))
    kugel(w, rr * 0.4, ytop + 1.5, 0, 1.0 + 0.4 * s, w.b("lime_stained_glass"))
    rohr(w, bez((rr * 0.3, ytop, -rr * 0.3), (rr * 0.6, ytop + 4 * s, -rr * 0.5), (rr * 0.8, ytop + 7 * s, -rr * 0.6)),
         0.5 + 0.2 * s, 0.5, mat=w.b("stripped_oak_log", axis="y"))
    for i in range(3):
        a = i / 3 * 2 * math.pi
        for y in range(0, 3):
            w.setze(round(math.cos(a) * rk * 0.7), y, round(math.sin(a) * rk * 0.7), w.b("black_concrete"))
    for y in range(0, int(yc - rk * 0.6)):
        for x, z in kreisrand(1.5):
            w.setze(x, y, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)
                    if y == 0 else w.b("air"), False)
    w.setze(0, int(yc - rk * 0.9) + 1, round(rk) - 1, w.b("air"))
    w.setze(0, int(yc - rk * 0.9) + 2, round(rk) - 1, w.b("air"))
    return w


def flaschenbaum(seed, g=2):
    """Flaschenbaum: ein knorriger, kahler Baum, an dessen Ästen Hunderte bunte Glasflaschen, Amulette und Kerzen-
    laternen hängen und klirren, umgeben von einem Steinkreis mit Opfergaben."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    hexenboden(w, R)
    H = int(8 * s + 6)
    rohr(w, bez((0, 0, 0), (1, H * 0.5, -0.5), (0, H, 0)), 1.2 * s + 0.8, 0.6 * s + 0.4,
         mat=w.b("dark_oak_log", axis="y"), rauh=0.15)
    rng = w.rng
    farben = ["lime_stained_glass", "blue_stained_glass", "purple_stained_glass", "orange_stained_glass",
              "cyan_stained_glass", "red_stained_glass"]
    for k in range(int(6 + 3 * s)):
        a = k / (6 + 3 * s) * 2 * math.pi
        yb = H * (0.5 + rng.random() * 0.45)
        L = (3 + rng.random() * 3) * s + 2
        pts = bez((0, yb, 0), (math.cos(a) * L * 0.5, yb + L * 0.5, math.sin(a) * L * 0.5),
                  (math.cos(a) * L, yb + L * 0.3, math.sin(a) * L))
        for i, (px, py, pz, t) in enumerate(pts):
            p = (round(px), round(py), round(pz))
            w.setze(*p, w.b("dark_oak_wood", axis="y"), False)
            if i % 3 == 2 and t > 0.3:
                L2 = 1 + int(rng.random() * 3)
                for d in range(1, L2):
                    w.setze(p[0], p[1] - d, p[2], w.b("chain", axis="y", waterlogged=False), False)
                w.setze(p[0], p[1] - L2, p[2], w.b(farben[int(rng.integers(6))]) if rng.random() < 0.8 else
                        w.b("soul_lantern", hanging=True, waterlogged=False), False)
    for i in range(10):
        a = i / 10 * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        w.setze(x, hoehe(w, x, z, 4) + 1, z, w.b("mossy_cobblestone"))
    return w


def dornentor(seed, g=2):
    """Dornentor: ein gewaltiges Tor aus ineinander verschlungenen, dornigen Ranken (dunkles Holz, Beerenbüsche),
    das den Weg zu einem verwunschenen Garten versperrt, mit verwelkten Rosen und einem Schloss aus Eisen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = hexenboden(w, R)
    H = int(8 * s + 6)
    rng = w.rng
    for k in range(int(8 + 4 * s)):
        sx = -1 if k % 2 else 1
        x0 = sx * (3 + rng.random() * 4 * s)
        pts = bez((x0, 0, rng.random() - 0.5), (sx * (5 * s + 2), H * 0.7, rng.random() * 2 - 1),
                  (-sx * rng.random() * 2 * s, H + rng.random() * 3, rng.random() - 0.5))
        rohr(w, pts, 0.8 * s + 0.4, 0.3, mat=lambda x, y, z, *a: w.b("dark_oak_wood", axis="y") if (x + y) % 4
             else w.b("sweet_berry_bush", age=1), rauh=0.2)
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 1 and rng.random() < 0.04 and w.frei(x, y + 1, z):
            w.setze(x, y + 1, z, w.b("wither_rose") if rng.random() < 0.5 else w.b("rose_bush", half="lower"))
    for y in range(1, 4):
        for x in (-1, 0, 1):
            w.bloecke.pop((x, y, 0), None)
    w.setze(0, 2, 0, w.b("iron_bars", waterlogged=False))
    w.setze(0, 1, 0, w.b("iron_bars", waterlogged=False))
    for z in range(1, R):
        for x in (-1, 0, 1):
            if (x, z) in zellen:
                w.setze(x, zellen[(x, z)], z, w.b("dirt_path"))
    return w


def walpurgisfeuer(seed, g=2):
    """Walpurgisfeuer: auf einer kahlen Bergkuppe ein riesiger, lodernder Scheiterhaufen in einem Kreis aus Menhiren,
    geschmückte Besen, Hexenhüte auf Pfählen und Trommeln für den nächtlichen Tanz."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 5)
    H = 4 * s + 3
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 2 * rn(x, 0, z):
                continue
            h = int(H * max(0, 1 - (d / R) ** 2) + rn(x, 3, z) * 2)
            for y in range(-2, h + 1):
                w.setze(x, y, z, w.b("coarse_dirt" if y == h and rn(x * 2, 5, z * 2) > 0.5 else "grass_block"
                                     if y == h else "stone", **({"snowy": False} if y == h and
                                                                 rn(x * 2, 5, z * 2) <= 0.5 else {})))
    top = hoehe(w, 0, 0, int(H) + 4)
    for k in range(int(4 * s + 4)):
        rr = (2.5 * s + 2) * (1 - k / (4 * s + 4))
        for x, z in kreisrand(max(0.4, rr)):
            w.setze(x, top + 1 + k, z, w.b("spruce_log", axis="y") if (x + z + k) % 3 else w.b("oak_log", axis="y"))
    for x, z in kreisrand(1.5):
        w.setze(x, top + 1, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    w.setze(0, top + int(4 * s + 5), 0, w.b("fire", age=0, north=False, south=False, east=False, west=False,
                                            up=False))
    n = 8
    for i in range(n):
        a = i / n * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        y = hoehe(w, x, z, int(H) + 4) + 1
        for k in range(int(2 + 2 * s)):
            w.setze(x, y + k, z, w.b("stone" if k % 2 else "andesite"))
        if i % 2:
            hx, hz = round(math.cos(a + 0.4) * R * 0.45), round(math.sin(a + 0.4) * R * 0.45)
            hy = hoehe(w, hx, hz, int(H) + 4) + 1
            w.setze(hx, hy, hz, w.b("dark_oak_fence"))
            w.setze(hx, hy + 1, hz, w.b("dark_oak_fence"))
            w.setze(hx, hy + 2, hz, w.b("black_carpet"))
            w.setze(hx, hy + 3, hz, w.b("black_wool"))
    return w


def schicksalsweberei(seed, g=1):
    """Schicksalsweberei: eine runde Hütte mit drei großen Spinnrädern davor, von denen leuchtende Fäden (Ketten,
    Endstäbe) zu einem riesigen Webrahmen laufen, in dem ein schimmerndes Tuch aus buntem Glas entsteht."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    hexenboden(w, R)
    r = 2.5 * s + 2
    for y in range(1, int(2 * s + 4)):
        for x, z in kreisrand(r, 0, -int(R * 0.4)):
            w.setze(x, y, z, holzwand(w)(x, y, z))
    kegeldach(w, 0, -int(R * 0.4), int(2 * s + 4), int(r), Dachmat(w, ["mcw:thatch", "spruce"]), form="kegel",
              spitze=None)
    for k in range(3):
        x = -4 + k * 4
        z = -int(R * 0.4) + int(r) + 3
        for dy in range(-1, 2):
            for dz in range(-1, 2):
                if abs(dy) + abs(dz) == 1:
                    w.setze(x, 2 + dy, z + dz, w.b("spruce_planks"))
        w.setze(x, 2, z, w.b("spruce_log", axis="x"))
        w.setze(x, 1, z, w.b("spruce_fence"))
    fz = int(R * 0.4)
    B = int(3 * s + 3)
    H = int(3 * s + 4)
    farben = ["purple_stained_glass", "magenta_stained_glass", "light_blue_stained_glass", "yellow_stained_glass"]
    for x in range(-B, B + 1):
        for y in range(1, H + 1):
            rand = abs(x) == B or y in (1, H)
            w.setze(x, y, fz, w.b("dark_oak_log", axis="y") if rand else
                    w.b(farben[(x + y) % 4]) if y > H // 2 else w.b("chain", axis="y", waterlogged=False))
    return w


def kuerbiswagen(seed, g=2):
    """Kürbiswagen: eine Kutsche aus einem riesigen, ausgehöhlten Kürbis mit Rankenrädern, Laternenfenstern und einem
    Kutschbock aus Wurzelholz, davor zwei Rattenpferd-Figuren auf einer Lichtung."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = hexenboden(w, R)
    rk = 3.2 * s + 2.4
    yc = rk + 1.5
    for x in range(-int(rk * 1.2) - 1, int(rk * 1.2) + 2):
        for y in range(1, int(yc + rk) + 2):
            for z in range(-int(rk) - 1, int(rk) + 2):
                d = math.sqrt((x / 1.2) ** 2 + ((y - yc) / 0.95) ** 2 + z * z)
                if rk - 1.1 < d <= rk:
                    ang = math.atan2(z, x / 1.2)
                    rippe = abs(math.sin(ang * 5)) < 0.25
                    fen = abs(y - yc) < 1.2 and abs(z) > rk * 0.8 and abs(x) < rk * 0.5
                    w.setze(x, y, z, w.b("orange_stained_glass") if fen else
                            w.b("orange_terracotta") if rippe else w.b("orange_concrete"))
                elif d <= rk - 1.1:
                    w.bloecke.pop((x, y, z), None)
    w.setze(0, int(yc + rk) + 1, 0, w.b("green_terracotta"))
    w.setze(0, int(yc + rk) + 2, 0, w.b("green_terracotta"))
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * round(rk * 0.8), sz * (round(rk) + 1)
            for k in range(12):
                a = k / 12 * 2 * math.pi
                w.setze(cx + round(math.cos(a) * 1.5), 2 + round(math.sin(a) * 1.5), cz, w.b("dark_oak_fence"))
            w.setze(cx, 2, cz, w.b("dark_oak_log", axis="z"))
    for y in range(2, 4):
        w.setze(round(rk * 1.2) + 1, y, 0, w.b("dark_oak_log", axis="y"))
    gr = w.b("gray_wool")
    for sz in (-1, 1):
        teile = [(ell(0, 2.0, 0, 1.6, 0.9, 0.8), gr), (ell(1.6, 2.3, 0, 0.7, 0.55, 0.5), gr),
                 (ell(2.3, 2.2, 0, 0.3, 0.2, 0.2), w.b("pink_wool")), (ell(1.3, 3.0, 0.4, 0.2, 0.3, 0.1), w.b("pink_wool")),
                 (ell(1.3, 3.0, -0.4, 0.2, 0.3, 0.1), w.b("pink_wool")),
                 (kap((-1.6, 1.8, 0), (-3.2, 0.8, 0), 0.15), w.b("pink_wool"))] + \
                [(kap((dx, 1.5, dz), (dx, 0, dz), 0.25), gr) for dx in (-1.0, 1.0) for dz in (-0.4, 0.4)]
        figur(w, 0.7 * s + 0.4, teile, (-4, -1, -2), (3, 4, 2), pos=(round(rk * 1.2) + round(4 * s + 3), 1,
                                                                       sz * round(1.5 * s + 1)))
    _ = zellen
    return w


def eulenturm(seed, g=2):
    """Eulenturm: ein hohler, uralter Baumstumpf-Turm mit vielen Rundfenstern, auf dessen Spitze eine riesige
    Eulenstatue mit gelben Augen thront, kleine Eulen in den Astlöchern und eine Wendeltreppe außen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    hexenboden(w, R)
    H = int(10 * s + 8)
    r = 3 * s + 2.5
    for y in range(1, H):
        rr = r * (1 - 0.2 * y / H) + (0.6 if y < 3 else 0)
        for x, z in kreisrand(rr):
            loch = y % 5 == 3 and (x + z) % 4 == 0
            w.setze(x, y, z, w.b("black_concrete") if loch else w.b("dark_oak_wood", axis="y") if (x + y) % 4 else
                    w.b("stripped_dark_oak_wood", axis="y"))
    for k in range(H * 3):
        a = k / 3 * 0.35
        y = 1 + k // 3
        if y >= H:
            break
        w.setze(round(math.cos(a) * (r + 1)), y, round(math.sin(a) * (r + 1)), w.b("dark_oak_slab", type="top",
                                                                                    waterlogged=False), False)
    br = w.b("brown_wool")
    hell = w.b("white_terracotta")
    ge = w.b("yellow_concrete")
    teile = [(ell(0, 2.8, 0, 2.2, 2.8, 2.0), br), (ell(0.8, 2.6, 0, 1.6, 2.2, 1.6), hell),
             (ell(0, 5.8, 0, 1.9, 1.6, 1.9), br), (ell(1.4, 6.0, 0.7, 0.55, 0.55, 0.45), ge),
             (ell(1.4, 6.0, -0.7, 0.55, 0.55, 0.45), ge), (ell(1.8, 6.0, 0.7, 0.2, 0.2, 0.15), w.b("black_concrete")),
             (ell(1.8, 6.0, -0.7, 0.2, 0.2, 0.15), w.b("black_concrete")),
             (kegel(0.2, 1.0, 7.0, 8.4, 0.5, 0.05), br), (kegel(0.2, -1.0, 7.0, 8.4, 0.5, 0.05), br),
             (kap((1.6, 5.4, 0), (2.0, 4.8, 0), 0.25, 0.1), w.b("orange_concrete")),
             (ell(-0.3, 3.0, 1.9, 1.2, 2.2, 0.4), br), (ell(-0.3, 3.0, -1.9, 1.2, 2.2, 0.4), br)]
    figur(w, 0.75 * s + 0.4, teile, (-3, -1, -3), (3, 9, 3), pos=(0, H, 0), winkel=0.5)
    return w


def mondspiegel_brunnen(seed, g=1):
    """Mondspiegel-Brunnen: ein runder Brunnen aus weißem Stein, dessen Wasserfläche den Mond spiegelt (leuchtende
    Scheibe unter Wasser), mit Mondsichel-Bogen darüber, silbernen Kerzen und Mondblumen ringsum."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    hexenboden(w, R)
    rb = 2.5 * s + 2
    for x in range(-int(rb) - 1, int(rb) + 2):
        for z in range(-int(rb) - 1, int(rb) + 2):
            d = math.hypot(x, z)
            if d <= rb:
                w.setze(x, -1, z, w.b("sea_lantern") if d < rb * 0.5 else w.b("calcite"))
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, 1, z, w.b("water", level=0)) if False else None
            elif d <= rb + 1.2:
                w.setze(x, 0, z, w.b("calcite"))
                w.setze(x, 1, z, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
    Rb = rb + 1.5
    for k in range(int(Rb * 10)):
        a = math.pi * 0.15 + math.pi * 0.7 * k / (Rb * 10)
        x, y = round(math.cos(a) * Rb), round(math.sin(a) * Rb * 1.4)
        w.setze(x, y + 1, 0, w.b("smooth_quartz"))
        w.setze(x, y + 1, 1, w.b("smooth_quartz"))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * (rb + 3)), round(math.sin(a) * (rb + 3))
        w.setze(x, 1, z, w.b("white_candle", candles=3, lit=True, waterlogged=False))
        w.setze(round(math.cos(a + 0.3) * (rb + 4)), 1, round(math.sin(a + 0.3) * (rb + 4)), w.b("lily_of_the_valley"))
    return w


def giftgarten(seed, g=2):
    """Giftgarten: ein ummauerter Garten mit Totenkopf-Tor, in dem in strengen Beeten nur giftige Pflanzen
    wachsen – Wither-Rosen, Fliegenpilze, Tollkirschen (Beerenbüsche), Schierling (Weißblüher) – und ein Giftbrunnen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = hexenboden(w, R)
    A = int(R * 0.7)
    st = M(w, [("mossy_stone_bricks", 2), ("stone_bricks", 1), ("cracked_stone_bricks", 1)])
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            if max(abs(x), abs(z)) == A:
                for y in range(1, 4):
                    w.setze(x, y, z, st(x, y, z))
            else:
                w.setze(x, 0, z, w.b("podzol") if (x + z) % 3 else w.b("coarse_dirt"))
                w.bloecke.pop((x, 1, z), None)
    pflanzen = [w.b("wither_rose"), w.b("red_mushroom"), w.b("sweet_berry_bush", age=3), w.b("lily_of_the_valley"),
                w.b("brown_mushroom")]
    for x in range(-A + 2, A - 1):
        for z in range(-A + 2, A - 1):
            if abs(x) < 2 or abs(z) < 2:
                w.setze(x, 0, z, w.b("gravel"))
                continue
            w.setze(x, 1, z, pflanzen[((x + A) // 3 + (z + A) // 3) % 5])
    for y in (1, 2):
        w.bloecke.pop((0, y, A), None)
    w.setze(0, 4, A, w.b("skeleton_skull", rotation=0))
    w.setze(-1, 4, A, w.b("mossy_stone_bricks"))
    w.setze(1, 4, A, w.b("mossy_stone_bricks"))
    w.setze(0, 1, 0, w.b("water_cauldron", level=3))
    w.setze(0, 0, 0, w.b("lime_concrete"))
    _ = zellen
    return w


def destille(seed, g=1):
    """Sternstaub-Destille: ein offener Schuppen mit großem Kupferkessel, gewundener Kupferschlange und Glasballons in
    Strohkörben, in denen leuchtende Tinkturen schimmern, dazu Regale mit Fläschchen."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    hexenboden(w, R)
    B, T = int(3 * s + 5), int(2 * s + 4)
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            w.setze(x, 0, z, w.b("spruce_planks"))
            if abs(x) == B and abs(z) == T:
                for y in range(1, 5):
                    w.setze(x, y, z, w.b("dark_oak_log", axis="y"))
    satteldach(w, -B, -T, B, T, 5, Dachmat(w, ["dark_oak", "spruce"]), first_x=True, ue=1, giebel=None,
               traufe="dark_oak")
    kugel(w, -B // 2, 2.2, 0, 1.6 + 0.4 * s, w.b("waxed_cut_copper"), ry=1.8 + 0.4 * s)
    w.setze(-B // 2, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    pts = [(-B // 2 + math.cos(t * 12) * 1.2 + t * B, 4 - t * 3, math.sin(t * 12) * 1.2, t)
           for t in np.linspace(0, 1, 60)]
    for x, y, z, t in pts:
        w.setze(round(x), round(y), round(z), w.b("waxed_cut_copper"), False)
    farben = ["lime_stained_glass", "purple_stained_glass", "light_blue_stained_glass", "pink_stained_glass"]
    for k in range(3 + g):
        x = B // 2 + (k % 2) * 2 - 1
        z = -T + 1 + k
        w.setze(x, 1, z, w.b("hay_block", axis="y"))
        w.setze(x, 2, z, w.b(farben[k % 4]))
    for x in range(-B + 1, B):
        w.setze(x, 2, -T, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x, 3, -T, w.b(farben[x % 4]) if x % 2 else w.b("air"))
    return w


def wurzelhoehle(seed, g=2):
    """Wurzelhöhle: unter den mächtigen, freigespülten Wurzeln einer uralten Eiche liegt die Wohnhöhle einer Kräuter-
    hexe, mit einer runden Tür, Fenstern zwischen den Wurzeln, Laternen und einem Pilzgarten."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = hexenboden(w, R)
    kugel(w, 0, 0, 0, 5 * s + 3, M(w, [("dirt", 2), ("rooted_dirt", 2), ("moss_block", 1)]), ry=3 * s + 2)
    H = int(10 * s + 6)
    hb = int(3 * s + 2)
    rohr(w, bez((0, hb - 1, 0), (0.5, hb + H * 0.5, 0.3), (0, hb + H, 0)), 1.6 * s + 1, 0.9 * s + 0.6,
         mat=w.b("oak_log", axis="y"), rauh=0.1)
    for k in range(7):
        a = k / 7 * 2 * math.pi
        rohr(w, bez((0, hb, 0), (math.cos(a) * 3 * s, hb + 0.5, math.sin(a) * 3 * s),
                    (math.cos(a) * (6 * s + 3), 0, math.sin(a) * (6 * s + 3))), 0.8 * s + 0.4, 0.4,
             mat=w.b("oak_wood", axis="y"))
    laubball(w, 0, hb + H + 2, 0, 4 * s + 2.5, arten=("oak_leaves", "dark_oak_leaves"), dicht=0.85)
    tz = round(5 * s + 3) - 1
    for x in (-1, 0, 1):
        for y in (1, 2, 3):
            if abs(x) + max(0, y - 2) <= 1 or y < 3:
                w.bloecke.pop((x, y, tz), None)
    w.setze(0, 1, tz, w.b("spruce_door", facing="south", half="lower", hinge="left", open=False, powered=False))
    w.setze(0, 2, tz, w.b("spruce_door", facing="south", half="upper", hinge="left", open=False, powered=False))
    for sx in (-3, 3):
        w.setze(sx, 2, tz - 1, w.b("glass_pane"))
    laterne(w, 2, 4, tz + 1, kette=1)
    rng = w.rng
    for k in range(int(8 * s + 4)):
        x, z = int((rng.random() - 0.5) * 6) , tz + 2 + int(rng.random() * 4)
        if (x, z) in zellen:
            w.setze(x, zellen[(x, z)] + 1, z, w.b("red_mushroom" if k % 2 else "brown_mushroom"), False)
    return w


HEXEN3 = {
    "besenmacherei": ("Besenmacherei", besenmacherei),
    "spiegelhuette": ("Spiegelhütte", spiegelhuette),
    "verdrehter_turm": ("Verdrehter Hexenturm", verdrehter_turm),
    "kraeuterscheune": ("Kräuterscheune", kraeuterscheune),
    "kristallkugel_pavillon": ("Kristallkugel-Pavillon", kristallkugel_pavillon),
    "katzenhaus": ("Katzenhaus", katzenhaus),
    "hexenbruecke": ("Hexenbrücke", hexenbruecke),
    "mondsichelhuette": ("Mondsichel-Hütte", mondsichelhuette),
    "buecherturm": ("Bücherstapel-Turm", buecherturm),
    "kesselhaus": ("Kesselhaus", kesselhaus),
    "flaschenbaum": ("Flaschenbaum", flaschenbaum),
    "dornentor": ("Dornentor", dornentor),
    "walpurgisfeuer": ("Walpurgisfeuer", walpurgisfeuer),
    "schicksalsweberei": ("Schicksalsweberei", schicksalsweberei),
    "kuerbiswagen": ("Kürbiswagen", kuerbiswagen),
    "eulenturm": ("Eulenturm", eulenturm),
    "mondspiegel_brunnen": ("Mondspiegel-Brunnen", mondspiegel_brunnen),
    "giftgarten": ("Giftgarten", giftgarten),
    "destille": ("Sternstaub-Destille", destille),
    "wurzelhoehle": ("Wurzelhöhle", wurzelhoehle),
}

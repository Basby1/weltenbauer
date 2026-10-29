"""Gärten & Parks II – zwanzig weitere Parkanlagen: Landschaftsgarten mit Monopteros, Gartenruine, Orangerie,
Muschelgrotte, Sonnenuhr-Rondell, Formschnittgarten, Lindenallee, Wasserspiel-Platz, Minigolfplatz,
Aussichtsturm, Steingarten, Tulpenbeete, Wassertretstelle, Bootsverleih am Parksee, Parkcafé, Rosenbogengang,
Entenhaus am Teich, Picknickwiese, Bienenweide mit Insektenhotel und Mondbrücke."""

from __future__ import annotations

import math

from erw_basis import M, S, baum, baumrand, figur, haus, hoehe, wiese
from feinbau import Dachmat, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, laubball, rohr
from lib import Rauschen
from skulptur import ell, kap, kasten, kegel, kreisrand
from wueste_eis import kuppel


def kies(w, pts, breite=1.2, zellen=None, blk="gravel"):
    for (a, b) in zip(pts, pts[1:]):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for k in range(n + 1):
            t = k / n
            x, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if math.hypot(dx, dz) <= breite:
                        p = (round(x + dx), round(z + dz))
                        y = zellen.get(p, 0) if zellen else 0
                        w.setze(p[0], y, p[1], w.b(blk))
                        for yy in range(y + 1, y + 3):
                            if w.hole(p[0], yy, p[1]) is not None and "grass" in w.P.name(w.hole(p[0], yy, p[1])):
                                w.bloecke.pop((p[0], yy, p[1]), None)


def teich(w, cx, cz, rx, rz, zellen=None, rand="stone_bricks"):
    rn = Rauschen(w, 4)
    for x in range(int(cx - rx) - 2, int(cx + rx) + 3):
        for z in range(int(cz - rz) - 2, int(cz + rz) + 3):
            d = ((x - cx) / rx) ** 2 + ((z - cz) / rz) ** 2
            if d <= 1 + 0.15 * rn(x, 0, z):
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("clay"))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
                if zellen is not None:
                    zellen[(x, z)] = -1


def hecke(w, x, z, y0, h, art="oak_leaves"):
    for y in range(y0, y0 + h):
        w.setze(x, y, z, w.b(art, persistent=True, distance=1, waterlogged=False))


def bank(w, x, y, z, richtung="north", holz="spruce"):
    quer = richtung in ("north", "south")
    for k in (-1, 0, 1):
        p = (x + k, y, z) if quer else (x, y, z + k)
        w.setze(*p, treppe(w, holz, richtung))


def laternenpfahl(w, x, y, z, h=3):
    for k in range(h):
        w.setze(x, y + k, z, w.b("dark_oak_fence"))
    w.setze(x, y + h, z, w.b("lantern", hanging=False, waterlogged=False))


def saeule(w, x, y0, z, h, mat="quartz_pillar"):
    w.setze(x, y0, z, w.b("chiseled_quartz_block"))
    for y in range(y0 + 1, y0 + h):
        w.setze(x, y, z, w.b(mat, axis="y"))
    w.setze(x, y0 + h, z, w.b("chiseled_quartz_block"))


# ============================================================================ Bauten

def monopteros(seed, g=2):
    """Landschaftsgarten mit Monopteros: ein runder Säulentempel mit Kuppel auf einer Insel in einem geschwungenen
    See, sanfte Hügel, Baumgruppen, eine Holzbrücke und ein Kiesweg, der um das Wasser führt."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = wiese(w, R, 0.8)
    teich(w, 0, 0, R * 0.55, R * 0.4, zellen)
    ri = 3 * s + 2.5
    for x in range(-int(ri) - 1, int(ri) + 2):
        for z in range(-int(ri) - 1, int(ri) + 2):
            if math.hypot(x, z) <= ri:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
                w.setze(x, 1, z, w.b("smooth_quartz") if math.hypot(x, z) < ri - 1 else w.b("air"))
    rt = ri - 1.5
    H = int(3 * s + 4)
    for i in range(8):
        a = i / 8 * 2 * math.pi
        saeule(w, round(math.cos(a) * rt), 1, round(math.sin(a) * rt), H)
    for x, z in kreisrand(rt + 0.6):
        w.setze(x, H + 2, z, w.b("smooth_quartz"))
    kuppel(w, lambda x, y, z, t: w.b("waxed_oxidized_copper"), 0, 0, H + 2, rt + 0.5, form="rund", spitze="gold_block")
    bx = round(R * 0.4)
    for k in range(int(R * 0.6)):
        x = bx - k
        if math.hypot(x, 0) < ri:
            break
        y = 1 + round(1.2 * math.sin(math.pi * k / (R * 0.6 - ri)))
        for dz in (-1, 0, 1):
            w.setze(x, y, dz, w.b("spruce_planks") if dz == 0 else w.b("spruce_slab", type="bottom",
                                                                         waterlogged=False))
        w.setze(x, y + 1, -2, w.b("spruce_fence"))
        w.setze(x, y + 1, 2, w.b("spruce_fence"))
    pts = [(R * math.cos(a) * 0.8, R * math.sin(a) * 0.62) for a in [i * 0.4 for i in range(17)]]
    kies(w, pts, 1.0, zellen)
    baumrand(w, zellen, R, 6 + 2 * g, seed, innen=0.85)
    return w


def gartenruine(seed, g=2):
    """Gartenruine: eine absichtlich als Ruine erbaute gotische Kapellenfassade mit Spitzbogenfenster, umgestürzten
    Säulen und Efeu, malerisch an einem Hang zwischen alten Bäumen gelegen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.6, art="wald")
    st = M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 2), ("cracked_stone_bricks", 1)])
    B = int(4 * s + 4)
    H = int(8 * s + 6)
    rn = Rauschen(w, 3)
    for x in range(-B, B + 1):
        hx = H * (1 - (abs(x) / (B + 1)) ** 2) + rn(x, 0, 0) * 3
        for y in range(1, int(hx) + 1):
            fen = abs(x) < B * 0.45 and 3 <= y <= H * 0.75 and (x / (B * 0.45)) ** 2 + ((y - H * 0.5) / (H * 0.3)) ** 2 < 1.4
            if fen and (abs(x) > 0.6 or y % 3):
                continue
            w.setze(x, y, 0, st(x, y, 0))
            if abs(x) == B or abs(x) == 0:
                w.setze(x, y, 1, st(x, y, 1))
    for k in range(3):
        x0 = -B + k * B
        for i in range(int(3 * s + 2)):
            w.setze(x0 + i, 1, 4 + k, w.b("quartz_pillar", axis="x"))
    from feinbau import efeu
    efeu(w, 0.12, 0.4)
    baumrand(w, zellen, R, 5 + 2 * g, seed, innen=0.7)
    return w


def orangerie(seed, g=2):
    """Orangerie: ein langgestrecktes, klassizistisches Gartenhaus mit hohen Rundbogenfenstern, hinter denen
    Orangenbäumchen in Kübeln stehen; davor ein Parterre mit Kübelpflanzen und Kieswegen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.05)
    L, T = int(8 * s + 7), int(2 * s + 4)
    z0 = -int(R * 0.35)
    H = int(3 * s + 5)
    for x in range(-L, L + 1):
        for z in range(z0 - T, z0 + T + 1):
            w.setze(x, 0, z, w.b("smooth_quartz"))
            for y in range(1, H + 1):
                rand = abs(x) == L or abs(z - z0) == T
                if rand:
                    fen = z == z0 + T and x % 3 != 0 and abs(x) < L and y < H - 1
                    w.setze(x, y, z, w.b("glass") if fen else w.b("smooth_quartz") if x % 3 else
                            w.b("quartz_pillar", axis="y"))
                else:
                    w.bloecke.pop((x, y, z), None)
            w.setze(x, H + 1, z, w.b("smooth_quartz_slab", type="bottom", waterlogged=False) if abs(z - z0) == T
                    else w.b("glass"))
    for x in range(-L + 2, L - 1, 3):
        w.setze(x, 1, z0, w.b("barrel", facing="up", open=False))
        laubball(w, x, 3, z0, 1.2 + 0.3 * s, arten=("oak_leaves",), dicht=0.9)
        w.setze(x, 2, z0, w.b("oak_log", axis="y"))
        w.setze(x, 3, z0 + 1, w.b("orange_concrete"), False)
    for k in range(int(4 + 2 * s)):
        for sx in (-1, 1):
            x, z = sx * (3 + k * 3), int(R * 0.15)
            if abs(x) > R - 2:
                continue
            w.setze(x, 1, z, w.b("terracotta"))
            w.setze(x, 2, z, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False))
    kies(w, [(-L, int(R * 0.05)), (L, int(R * 0.05))], 1.0, zellen)
    kies(w, [(0, z0 + T + 1), (0, R)], 1.2, zellen)
    baumrand(w, zellen, R, 3 + g, seed, innen=0.9)
    return w


def muschelgrotte(seed, g=2):
    """Muschelgrotte: eine künstliche Grotte aus Tuffstein im Park, das Innere mit Muscheln (Perlmutt-Froschlicht,
    Korallenblöcke), Kristallen und einem Wasserbecken mit Brunnenfigur ausgekleidet."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.3)
    rg = 4 * s + 3
    tf = M(w, [("tuff", 3), ("calcite", 1), ("mossy_cobblestone", 1), ("dripstone_block", 1)])
    for x in range(-int(rg) - 2, int(rg) + 3):
        for z in range(-int(rg) - 2, int(rg) + 3):
            for y in range(0, int(rg * 1.1) + 3):
                d = math.sqrt(x * x + ((y - 0.5) / 1.1) ** 2 + z * z)
                if rg - 1.6 < d <= rg + 0.3:
                    w.setze(x, y, z, tf(x, y, z))
                elif d <= rg - 1.6 and y > 0:
                    w.bloecke.pop((x, y, z), None)
    for x in range(-2, 3):
        for y in range(1, 4):
            w.bloecke.pop((x, y, round(rg)), None)
            w.bloecke.pop((x, y, round(rg) - 1), None)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 0 and math.sqrt(x * x + z * z) < rg - 1 and rng.random() < 0.3 and b == tf(x, y, z):
            if any(w.frei(x + dx, y + dy, z + dz) for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0),
                                                                     (0, 0, 1), (0, 0, -1))):
                w.setze(x, y, z, w.b(["pearlescent_froglight", "brain_coral_block", "horn_coral_block",
                                      "calcite"][int(rng.integers(4))], **({"axis": "y"} if False else {})))
    for x in range(-2, 3):
        for z in range(-2, 3):
            if math.hypot(x, z) <= 2.3:
                w.setze(x, 0, z, w.b("water", level=0))
    w.setze(0, 1, 0, w.b("calcite"))
    w.setze(0, 2, 0, w.b("pearlescent_froglight", axis="y"))
    baumrand(w, zellen, R, 3 + g, seed, innen=0.85)
    return w


def sonnenuhr_rondell(seed, g=1):
    """Sonnenuhr-Rondell: ein rundes Beet mit Stunden-Zahlen aus Steinplatten, in der Mitte ein schräger Schatten-
    stab auf Sockel, eingefasst von Buchsbaum und Lavendel, Bänke an den vier Himmelsrichtungen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, 0.05)
    rr = R * 0.65
    for x in range(-int(rr) - 1, int(rr) + 2):
        for z in range(-int(rr) - 1, int(rr) + 2):
            d = math.hypot(x, z)
            if d <= rr:
                w.setze(x, 0, z, w.b("grass_block", snowy=False) if d < rr - 2 else w.b("gravel"))
                w.bloecke.pop((x, 1, z), None)
            elif d <= rr + 1:
                hecke(w, x, z, 1, 1)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        x, z = round(math.cos(a) * (rr - 3)), round(math.sin(a) * (rr - 3))
        w.setze(x, 0, z, w.b("smooth_stone"))
        if i % 3 == 0:
            w.setze(x, 1, z, w.b("allium"))
    w.setze(0, 1, 0, w.b("chiseled_stone_bricks"))
    for k in range(int(3 + 2 * s)):
        w.setze(0, 2 + k, -k // 2, w.b("iron_bars", waterlogged=False) if k else w.b("gold_block"))
    for i, f in enumerate(("north", "east", "south", "west")):
        a = i * math.pi / 2 - math.pi / 2
        x, z = round(math.cos(a) * (rr + 3)), round(math.sin(a) * (rr + 3))
        bank(w, x, 1, z, f)
    _ = zellen
    return w


def formschnitt(seed, g=2):
    """Formschnittgarten: geometrisch geschnittene Buchsfiguren – Kugeln, Kegel, Spiralen, ein Pfau und ein Bär
    aus Laub – auf Rasenfeldern zwischen Kieswegen, mit einer Statue in der Mitte."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.05)
    kies(w, [(-R, 0), (R, 0)], 1.2, zellen)
    kies(w, [(0, -R), (0, R)], 1.2, zellen)
    lb = w.b("oak_leaves", persistent=True, distance=1, waterlogged=False)
    db = w.b("dark_oak_leaves", persistent=True, distance=1, waterlogged=False)
    n = 0
    for gx in (-1, 1):
        for gz in (-1, 1):
            cx, cz = gx * int(R * 0.45), gz * int(R * 0.45)
            art = n % 4
            if art == 0:
                kugel(w, cx, 2.5 * s + 1.5, cz, 1.8 * s + 1.2, lb)
                for y in range(1, int(1.5 * s + 1)):
                    w.setze(cx, y, cz, w.b("oak_log", axis="y"))
            elif art == 1:
                for y in range(1, int(6 * s + 4)):
                    r = (2.2 * s + 1.2) * (1 - y / (6 * s + 4))
                    for x, z in kreisrand(max(0.4, r), cx, cz):
                        w.setze(x, y, z, db)
                    for x in range(cx - int(r), cx + int(r) + 1):
                        for z in range(cz - int(r), cz + int(r) + 1):
                            if math.hypot(x - cx, z - cz) <= r:
                                w.setze(x, y, z, db)
            elif art == 2:
                teile = [(ell(0, 2.2, 0, 1.4, 1.4, 1.2), lb), (kap((0.8, 3.0, 0), (1.4, 5.2, 0), 0.5, 0.35), lb),
                         (ell(1.6, 5.6, 0, 0.6, 0.55, 0.5), lb),
                         (lambda X, Y, Z: ((X + 1.2) ** 2 / 4 + (Y - 4.5) ** 2 / 9 <= 1) & (abs(Z) < 3.2) &
                          (X < -0.2), db)]
                figur(w, 0.9 * s + 0.4, teile, (-4, -1, -4), (3, 8, 4), pos=(cx, 1, cz), winkel=0.4)
            else:
                teile = [(ell(0, 2.4, 0, 2.0, 1.6, 1.4), db), (ell(1.8, 3.6, 0, 0.9, 0.9, 0.9), db),
                         (ell(2.3, 4.4, 0.6, 0.35, 0.35, 0.3), db), (ell(2.3, 4.4, -0.6, 0.35, 0.35, 0.3), db)] + \
                        [(kap((sx, 1.6, sz), (sx, 0, sz), 0.55), db) for sx in (-1.2, 1.2) for sz in (-0.7, 0.7)]
                figur(w, 0.9 * s + 0.4, teile, (-3, -1, -3), (4, 6, 3), pos=(cx, 1, cz), winkel=-0.7)
            n += 1
    w.setze(0, 1, 0, w.b("chiseled_quartz_block"))
    for y in range(2, 5):
        w.setze(0, y, 0, w.b("quartz_pillar", axis="y"))
    w.setze(0, 5, 0, w.b("white_concrete"))
    for x, z in kreisrand(R * 0.9):
        if (x + z) % 2 == 0:
            hecke(w, x, z, hoehe(w, x, z, 5) + 1, 2)
    return w


def lindenallee(seed, g=2):
    """Lindenallee: eine schnurgerade, von zwei Reihen gleichmäßiger, rund geschnittener Linden gesäumte Allee
    mit Kiesweg, Bänken zwischen den Stämmen, Laternen und einem Brunnen am Ende."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = wiese(w, R, 0.1)
    L = int(R * 0.9)
    kies(w, [(0, -L), (0, L)], 2.2, zellen)
    for z in range(-L + 2, L - 1, int(4 + s)):
        for sx in (-1, 1):
            x = sx * 5
            y = zellen.get((x, z), 0) + 1
            H = int(5 + 2 * s)
            for yy in range(y, y + H):
                w.setze(x, yy, z, w.b("oak_log", axis="y"))
            laubball(w, x, y + H + 1, z, 2.2 + s * 0.9, arten=("oak_leaves",), dicht=0.95)
            if (z // int(4 + s)) % 2:
                bank(w, sx * 3, 1, z + 2, "east" if sx > 0 else "west")
            else:
                laternenpfahl(w, sx * 3, 1, z + 2)
    for x in range(-2, 3):
        for z in range(L - 2, L + 3):
            if math.hypot(x, z - L) <= 2.3:
                w.setze(x, 0, z, w.b("water", level=0) if math.hypot(x, z - L) < 1.6 else w.b("stone_bricks"))
    w.setze(0, 1, L, w.b("stone_brick_wall"))
    w.setze(0, 2, L, w.b("water", level=0))
    return w


def wasserspiele(seed, g=1):
    """Wasserspiel-Platz: ein Platz aus hellen Platten mit Rastern aus Bodenfontänen (Wassersäulen), einem flachen
    Planschbecken, Sitzstufen und einer Wasserwand aus Stein."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.05)
    A = int(R * 0.6)
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            w.setze(x, 0, z, w.b("smooth_stone") if (x + z) % 2 else w.b("polished_diorite"))
            for y in range(1, 3):
                w.bloecke.pop((x, y, z), None)
    for x in range(-A + 2, A - 1, 3):
        for z in range(-A + 2, 0, 3):
            w.setze(x, 0, z, w.b("water", level=0))
            h = 1 + (x + z) % 3
            for y in range(1, h + 1):
                w.setze(x, y, z, w.b("water", level=0))
    for x in range(-A + 2, A - 1):
        for z in range(2, A - 1):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("light_blue_terracotta"))
    for x in range(-A, A + 1):
        for y in range(1, int(3 * s + 3)):
            w.setze(x, y, -A - 1, w.b("stone_bricks"))
        w.setze(x, int(3 * s + 3), -A, w.b("water", level=0))
    for k in range(3):
        for z in range(-A, A + 1):
            w.setze(A + 1 + k, 1 + k // 2, z, treppe(w, "stone_brick", "west"))
    _ = zellen
    return w


def minigolf(seed, g=1):
    """Minigolfplatz: neun kleine Bahnen mit Banden aus Holz, Hindernissen (Brücke, Mühle, Rampe, Tunnel), Loch-
    Fähnchen und einem Kassenhäuschen mit Schlägerständer."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.05)
    n = 4 + g
    for k in range(n):
        x0 = -int(R * 0.7) + (k % 3) * int(R * 0.5)
        z0 = -int(R * 0.6) + (k // 3) * 6
        L = int(R * 0.4)
        for x in range(x0, x0 + L):
            for z in range(z0, z0 + 3):
                rand = z in (z0, z0 + 2) or x in (x0, x0 + L - 1)
                w.setze(x, 0, z, w.b("lime_concrete") if not rand else w.b("grass_block", snowy=False))
                if rand:
                    w.setze(x, 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
        hx = x0 + L - 3
        w.setze(hx, 0, z0 + 1, w.b("black_concrete"))
        w.setze(hx, 1, z0 + 1, w.b("spruce_fence"))
        w.setze(hx, 2, z0 + 1, w.b("red_wool"))
        mitte = x0 + L // 2
        art = k % 4
        if art == 0:
            w.setze(mitte, 1, z0 + 1, w.b("spruce_slab", type="bottom", waterlogged=False))
        elif art == 1:
            for y in range(1, 4):
                w.setze(mitte, y, z0, w.b("oak_planks"))
                w.setze(mitte, y, z0 + 2, w.b("oak_planks"))
            w.setze(mitte, 3, z0 + 1, w.b("oak_planks"))
            w.setze(mitte, 4, z0 + 1, w.b("red_terracotta"))
        elif art == 2:
            w.setze(mitte, 1, z0 + 1, w.b("water", level=0))
        else:
            for dx in range(-1, 2):
                w.setze(mitte + dx, 1, z0 + 1, w.b("stone_brick_stairs", facing="east", half="bottom",
                                                    shape="straight", waterlogged=False) if dx == -1 else
                        w.b("stone_brick_slab", type="bottom", waterlogged=False))
    haus(w, int(R * 0.45), int(R * 0.5), 5, 4, 1, M(w, [("white_terracotta", 1)]), holz="spruce", H=3,
         dach=("mcw:red_terracotta", "brick"), tuer_s="west", schorn=False)
    _ = zellen
    return w


def aussichtsturm(seed, g=2):
    """Aussichtsturm: ein schlanker, achteckiger Holzturm mit außen umlaufender Treppe auf einem Parkhügel, oben
    eine überdachte Plattform mit Fernrohr und Wimpel."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.2)
    kugel(w, 0, 0, 0, R * 0.55, w.b("grass_block", snowy=False), ry=3 * s + 2)
    yb = int(3 * s + 2)
    H = int(12 * s + 8)
    r = 1.8 * s + 1.4
    for y in range(yb, yb + H):
        for x, z in kreisrand(r):
            w.setze(x, y, z, w.b("spruce_log", axis="y") if (x + z) % 2 == 0 or y % 4 == 0 else w.b("air"))
    for k in range(H * 3):
        a = k / 3 * 0.4
        y = yb + k // 3
        if y >= yb + H:
            break
        x, z = round(math.cos(a) * (r + 1.2)), round(math.sin(a) * (r + 1.2))
        w.setze(x, y, z, w.b("spruce_slab", type="top", waterlogged=False), False)
    top = yb + H
    P = int(r + 2)
    for x in range(-P, P + 1):
        for z in range(-P, P + 1):
            if math.hypot(x, z) <= P + 0.3:
                w.setze(x, top, z, w.b("spruce_planks"))
            if abs(math.hypot(x, z) - P) < 0.6:
                w.setze(x, top + 1, z, w.b("spruce_fence"))
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        for y in range(top + 1, top + 4):
            w.setze(round(math.cos(a) * (P - 0.5)), y, round(math.sin(a) * (P - 0.5)), w.b("spruce_log", axis="y"))
    kegeldach(w, 0, 0, top + 4, P, Dachmat(w, ["spruce", "dark_oak"]), form="glocke", spitze="spruce_fence")
    w.setze(0, top + 1, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    baumrand(w, zellen, R, 4 + 2 * g, seed, innen=0.8)
    return w


def steingarten(seed, g=1):
    """Steingarten: ein terrassierter Hang aus verwitterten Kalk- und Granitbrocken mit Polsterpflanzen, Hauswurz,
    Zwergkiefern, einem kleinen Bachlauf mit Staustufen und Trittsteinen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.3)
    rng = w.rng
    for k in range(int(14 * s + 8)):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.75
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        h = (1 - d / R) * 4 * s + 1
        kugel(w, x, zellen.get((x, z), 0) + h * 0.3, z, 0.8 + rng.random() * 1.4 * s,
              w.b(["calcite", "granite", "diorite", "andesite", "tuff"][k % 5]), ueber=False, ry=h * 0.6 + 0.5)
    for (x, y, z), b in list(w.bloecke.items()):
        if w.frei(x, y + 1, z) and y > 0 and rng.random() < 0.18:
            w.setze(x, y + 1, z, w.b(["moss_carpet", "allium", "azure_bluet", "white_tulip", "fern"][int(rng.integers(5))]))
    for z in range(-R, R):
        x = round(math.sin(z / 4) * 2)
        if (x, z) in zellen:
            y = hoehe(w, x, z, 10)
            w.setze(x, y, z, w.b("water", level=0))
    for k in range(2 + g):
        a = rng.random() * 6.28
        x, z = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        from erw_basis import fichte
        fichte(w, x, hoehe(w, x, z, 10) + 1, z, seed, 4 + 2 * s)
    return w


def tulpenbeete(seed, g=2):
    """Tulpenbeete: lange, schnurgerade Streifen in Rot, Gelb, Weiß, Rosa und Orange wie ein Farbteppich, dazwischen
    schmale Wege, eine kleine Windmühle und ein Aussichtspodest am Rand."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = wiese(w, R, 0.0, blumen=0.0)
    farben = ["red_tulip", "orange_tulip", "white_tulip", "pink_tulip", "dandelion", "allium"]
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if (x, z) not in zellen or math.hypot(x, z) > R * 0.85:
                continue
            reihe = (z + R) // 3
            if (z + R) % 3 == 0:
                w.setze(x, zellen[(x, z)], z, w.b("dirt_path"))
                w.bloecke.pop((x, zellen[(x, z)] + 1, z), None)
            else:
                w.setze(x, zellen[(x, z)] + 1, z, w.b(farben[reihe % 6]))
    mx, mz = int(R * 0.6), -int(R * 0.55)
    for y in range(1, int(5 * s + 5)):
        for x, z in kreisrand(1.6 * (1 - y / (5 * s + 8)) + 1, mx, mz):
            w.setze(x, y, z, w.b("bricks"))
    top = int(5 * s + 5)
    kegeldach(w, mx, mz, top, 2, Dachmat(w, ["mcw:thatch"]), form="kegel", spitze=None)
    for k in range(int(4 * s + 3)):
        for sgn in (-1, 1):
            w.setze(mx + 2, top + sgn * k, mz + sgn * k, w.b("spruce_planks"))
            w.setze(mx + 2, top + sgn * k, mz - sgn * k, w.b("white_wool"))
    return w


def wassertretstelle(seed, g=1):
    """Wassertretstelle: ein länglich gemauertes Becken mit klarem Bachwasser und Handlauf, ein Armbecken, eine
    Liegewiese mit Holzliegen und ein Schild mit Hinweisen, unter alten Weiden."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, 0.1)
    L = int(4 * s + 4)
    for x in range(-L, L + 1):
        for z in range(-2, 3):
            rand = abs(z) == 2 or abs(x) == L
            w.setze(x, 0, z, w.b("stone_bricks") if rand else w.b("water", level=0))
            w.setze(x, -1, z, w.b("stone_bricks"))
            if not rand:
                w.setze(x, -1, z, w.b("gravel"))
        w.setze(x, 2, 0, w.b("iron_bars", waterlogged=False)) if x % 4 == 0 and False else None
    for x in range(-L, L + 1):
        w.setze(x, 2, -2, w.b("spruce_fence"))
    for k in range(3):
        w.setze(-L + 1 + k * 3, 1, int(R * 0.45), w.b("spruce_slab", type="bottom", waterlogged=False))
        w.setze(-L + 1 + k * 3, 1, int(R * 0.45) + 1, w.b("spruce_slab", type="bottom", waterlogged=False))
    for x in (L + 3, L + 4):
        w.setze(x, 1, 0, w.b("stone_bricks"))
    w.setze(L + 3, 2, 0, w.b("water_cauldron", level=3))
    for k in range(2):
        x, z = -int(R * 0.5) + k * int(R), -int(R * 0.45)
        from erw_basis import einfuegen
        import wald2
        einfuegen(w, wald2.weide(seed + k, H=int(7 + 3 * s)), x, zellen.get((x, z), 0) + 1, z)
    return w


def bootsverleih(seed, g=2):
    """Bootsverleih am Parksee: ein Holzsteg mit kleinem Kassenhäuschen, bunte Ruderboote und Schwanen-Tretboote am
    Anleger, ein Seerosenfeld und eine Insel mit Trauerweide."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.1)
    teich(w, 0, int(R * 0.15), R * 0.75, R * 0.5, zellen)
    for z in range(-int(R * 0.35), int(R * 0.15)):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
    for x in range(-int(4 * s + 3), int(4 * s + 4)):
        w.setze(x, 1, int(R * 0.15), w.b("spruce_planks"))
    farben = ["red_terracotta", "blue_terracotta", "yellow_terracotta", "white_terracotta"]
    for k in range(3 + g):
        x = -int(4 * s + 2) + k * 3
        z = int(R * 0.15) + 3
        for i in (-1, 0, 1):
            w.setze(x, 0, z + i, w.b(farben[k % 4]))
        w.setze(x, 1, z - 1, w.b(farben[k % 4]))
    for k in range(2):
        x, z = int(R * 0.35) + k * 4, int(R * 0.3)
        teile = [(ell(0, 0.8, 0, 1.4, 0.7, 0.9), w.b("white_concrete")),
                 (kap((1.0, 1.0, 0), (1.3, 2.6, 0), 0.3), w.b("white_concrete")),
                 (ell(1.6, 2.7, 0, 0.45, 0.3, 0.3), w.b("white_concrete")),
                 (ell(2.1, 2.6, 0, 0.3, 0.15, 0.15), w.b("orange_concrete"))]
        figur(w, 0.6 * s + 0.5, teile, (-2, -1, -2), (3, 4, 2), pos=(x, 0, z), winkel=2.5)
    haus(w, -3, -int(R * 0.45), 4, 4, 1, M(w, [("white_terracotta", 1)]), holz="spruce", H=3,
         dach=("mcw:blue_terracotta", "prismarine_brick"), tuer_s="south", schorn=False)
    ix, iz = -int(R * 0.35), int(R * 0.3)
    for x in range(ix - 3, ix + 4):
        for z in range(iz - 3, iz + 4):
            if math.hypot(x - ix, z - iz) < 3.2:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
    import wald2
    from lib import einfuegen
    einfuegen(w, wald2.weide(seed, H=int(7 + 3 * s)), ix, 1, iz)
    for k in range(8):
        a = k * 0.8
        x, z = round(R * 0.2 + math.cos(a) * 3), round(R * 0.45 + math.sin(a) * 2)
        if w.hole(x, 0, z) == w.b("water", level=0):
            w.setze(x, 1, z, w.b("lily_pad"))
    return w


def parkcafe(seed, g=1):
    """Parkcafé: ein Gartenpavillon aus weißem Gusseisen-Gitterwerk (Eisengitter) mit Glasdach, Tische mit
    Sonnenschirmen auf einer Terrasse, Blumenkübel und ein Kuchenbuffet hinter dem Tresen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.05)
    A = int(3 * s + 3)
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            w.setze(x, 0, z, w.b("smooth_quartz"))
            if max(abs(x), abs(z)) == A:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("iron_bars", waterlogged=False) if (x + z) % 2 else w.b("white_concrete"))
    from wueste_eis import kuppel as kup
    kup(w, lambda x, y, z, t: w.b("glass") if (x + z) % 3 else w.b("white_concrete"), 0, 0, 4, A + 0.5,
        form="rund", spitze="gold_block")
    for x in range(-A + 1, A):
        w.setze(x, 1, -A + 1, w.b("smooth_quartz_slab", type="top", waterlogged=False))
        w.setze(x, 2, -A + 1, w.b("cake") if x % 2 else w.b("air"))
    for y in (1, 2, 3):
        w.bloecke.pop((0, y, A), None)
    tz = A + 3
    for k in range(3 + g):
        x = -int(R * 0.45) + k * 4
        for dz in (0, 4):
            z = tz + dz
            w.setze(x, 0, z, w.b("smooth_stone"))
            w.setze(x, 1, z, w.b("white_concrete") if False else w.b("spruce_fence"))
            w.setze(x, 2, z, w.b("white_carpet"))
            for y in (3, 4):
                w.setze(x, y, z, w.b("spruce_fence"))
            for dx in (-1, 0, 1):
                for dzz in (-1, 0, 1):
                    w.setze(x + dx, 5, z + dzz, w.b(["red_wool", "white_wool"][(dx + dzz + 2) % 2]))
            w.setze(x - 1, 1, z, treppe(w, "spruce", "east"))
            w.setze(x + 1, 1, z, treppe(w, "spruce", "west"))
    _ = zellen
    return w


def rosenbogengang(seed, g=2):
    """Rosenbogengang: ein langer Tunnel aus aneinandergereihten Eisenbögen, überwachsen von Kletterrosen in Rot,
    Rosa und Weiß, mit einem Brunnen in der Mitte und Bänken an den Enden."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.05)
    L = int(R * 0.85)
    kies(w, [(0, -L), (0, L)], 1.8, zellen)
    H = int(2 * s + 4)
    rng = w.rng
    for z in range(-L, L + 1, 2):
        for k in range(17):
            a = math.pi * k / 16
            x, y = round(math.cos(a) * 3), 1 + round(math.sin(a) * H)
            w.setze(x, y, z, w.b("iron_bars", waterlogged=False))
            if rng.random() < 0.6:
                w.setze(x + (1 if x > 0 else -1 if x < 0 else 0), y + (1 if abs(x) < 2 else 0), z,
                        w.b("azalea_leaves" if rng.random() < 0.4 else "flowering_azalea_leaves", persistent=True,
                            distance=1, waterlogged=False), False)
            if rng.random() < 0.25:
                w.setze(x, y, z + 1, w.b(["red_wool", "pink_wool", "white_wool"][int(rng.integers(3))]), False)
    for x in range(-2, 3):
        for z in range(-2, 3):
            if math.hypot(x, z) <= 2.3:
                w.setze(x, 0, z, w.b("water", level=0) if math.hypot(x, z) < 1.6 else w.b("stone_bricks"))
    w.setze(0, 1, 0, w.b("stone_brick_wall"))
    for z in (-L - 2, L + 2):
        bank(w, 0, 1, z, "north" if z > 0 else "south")
    _ = zellen
    return w


def entenhaus(seed, g=1):
    """Entenhaus am Teich: ein kleines Fachwerk-Entenhäuschen auf einer Plattform mitten im Teich, Enten-Figuren
    (Erpel mit grünem Kopf, braune Weibchen) im Wasser, eine Rampe, Schilf und eine Futterstelle am Ufer."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.1)
    teich(w, 0, 0, R * 0.65, R * 0.5, zellen)
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, 1, z, w.b("spruce_planks"))
            w.setze(x, 0, z, w.b("spruce_log", axis="y")) if abs(x) == 2 and abs(z) == 2 else None
    for x in range(-1, 2):
        for z in range(-1, 2):
            for y in range(2, 4):
                if abs(x) == 1 or abs(z) == 1:
                    w.setze(x, y, z, w.b("white_terracotta") if (x + z + y) % 2 else w.b("spruce_log", axis="y"))
    w.bloecke.pop((0, 2, 1), None)
    satteldach(w, -1, -1, 1, 1, 4, Dachmat(w, ["mcw:red_terracotta", "brick"]), first_x=True, ue=1,
               giebel=M(w, [("white_terracotta", 1)]), traufe="spruce")
    for k in range(3):
        w.setze(0, 1 - k // 2, 3 + k, w.b("spruce_slab", type="bottom", waterlogged=False))
    rng = w.rng
    for k in range(4 + 2 * g):
        a = rng.random() * 6.28
        d = 3.5 + rng.random() * (R * 0.4)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d * 0.7)
        erpel = k % 2 == 0
        kopf = w.b("green_concrete" if erpel else "brown_wool")
        koerper = w.b("light_gray_wool" if erpel else "brown_wool")
        teile = [(ell(0, 0.6, 0, 0.9, 0.5, 0.55), koerper), (ell(0.7, 1.2, 0, 0.35, 0.35, 0.3), kopf),
                 (ell(1.1, 1.15, 0, 0.25, 0.1, 0.15), w.b("yellow_concrete"))]
        figur(w, 0.7 * s + 0.4, teile, (-1, -1, -1), (2, 2, 1), pos=(x, 0, z), winkel=rng.random() * 6.28)
    for k in range(int(10 * s)):
        a = rng.random() * 6.28
        x, z = round(math.cos(a) * R * 0.68), round(math.sin(a) * R * 0.52)
        w.setze(x, 1, z, w.b("sugar_cane"), False)
        w.setze(x, 2, z, w.b("sugar_cane"), False)
    return w


def picknickwiese(seed, g=1):
    """Picknickwiese: eine sonnige Wiese mit karierten Picknickdecken, Körben, Kuchen und Melonen, einem Spielplatz-
    schaukelgerüst, Drachen am Himmel und einer großen Linde als Schattenspender."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.3, blumen=0.1)
    baum(w, 0, zellen.get((0, 0), 0) + 1, 0, seed, 8 + 4 * s)
    rng = w.rng
    for k in range(3 + g):
        a = k / (3 + g) * 2 * math.pi + 0.5
        cx, cz = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        f = [("red_carpet", "white_carpet"), ("blue_carpet", "white_carpet"), ("lime_carpet", "white_carpet")][k % 3]
        for x in range(cx - 1, cx + 2):
            for z in range(cz - 1, cz + 2):
                w.setze(x, zellen.get((x, z), 0) + 1, z, w.b(f[(x + z + 10) % 2]))
        w.setze(cx + 2, zellen.get((cx + 2, cz), 0) + 1, cz, w.b("composter", level=3))
        w.setze(cx, zellen.get((cx, cz + 2), 0) + 1, cz + 2, w.b("cake") if k % 2 else w.b("melon"))
    sx, sz = -int(R * 0.55), int(R * 0.3)
    for y in range(1, 6):
        w.setze(sx, y, sz, w.b("oak_fence"))
        w.setze(sx + 4, y, sz, w.b("oak_fence"))
    for x in range(sx, sx + 5):
        w.setze(x, 6, sz, w.b("oak_log", axis="x"))
    for x in (sx + 1, sx + 3):
        for y in (3, 4, 5):
            w.setze(x, y, sz, w.b("chain", axis="y", waterlogged=False))
        w.setze(x, 2, sz, w.b("oak_slab", type="bottom", waterlogged=False))
    for k in range(2):
        dx, dy, dz = int(R * 0.3) - k * 6, int(10 * s + 8) + k * 3, -int(R * 0.3)
        for i in range(3):
            for j in range(3):
                if abs(i - 1) + abs(j - 1) <= 1:
                    w.setze(dx + i, dy + j, dz, w.b(["red_wool", "yellow_wool"][k]))
        for t in range(int(dy * 0.8)):
            w.setze(dx + 1 - t // 4, dy - t, dz + t // 3, w.b("white_wool") if t % 3 == 0 else w.b("air"), False)
    _ = rng
    return w


def insektenhotel(seed, g=1):
    """Bienenweide mit Insektenhotel: eine bunte Wildblumenwiese, in der Mitte ein großes Insektenhotel mit
    Satteldach und vielen Fächern (Bienennester, Schilf, Holzscheite, Ziegel), dazu Bienenstöcke am Rand."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.2, blumen=0.45)
    B = int(2 * s + 3)
    H = int(3 * s + 4)
    fach = ["bee_nest", "bamboo_block", "oak_log", "bricks", "hay_block", "stripped_birch_log", "mud_bricks"]
    for x in range(-B, B + 1):
        for y in range(1, H + 1):
            for z in (0, 1):
                f = fach[(x // 2 + y // 2 * 3) % len(fach)]
                pr = {"bee_nest": dict(facing="south", honey_level=0)}.get(f, {"axis": "z"} if "log" in f or
                                                                            "block" in f and "bamboo" in f or
                                                                            f == "hay_block" else {})
                w.setze(x, y, z, w.b(f, **pr) if (x % 2 and y % 2) or z == 0 else w.b("spruce_planks"))
        w.setze(x, 0, 0, w.b("spruce_planks"))
    satteldach(w, -B, -1, B, 2, H + 1, Dachmat(w, ["spruce", "dark_oak"]), first_x=True, ue=1, giebel=None,
               traufe="spruce")
    for k in range(3 + g):
        a = k / (3 + g) * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.65), round(math.sin(a) * R * 0.65)
        y = zellen.get((x, z), 0) + 1
        w.setze(x, y, z, w.b("spruce_fence"))
        w.setze(x, y + 1, z, w.b("beehive", facing="south", honey_level=3))
    return w


def mondbruecke(seed, g=2):
    """Mondbrücke: eine hohe, halbkreisförmige Steinbrücke spannt sich über einen Parkteich, so dass sie sich mit
    ihrem Spiegelbild zu einem vollen Kreis ergänzt; Laternen an den Enden und Uferbepflanzung."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.1)
    teich(w, 0, 0, R * 0.7, R * 0.45, zellen)
    rb = 4 * s + 3
    for k in range(int(rb * 10) + 1):
        a = math.pi * k / (rb * 10)
        x, y = round(-math.cos(a) * rb), round(math.sin(a) * rb)
        for z in (-1, 0, 1):
            w.setze(x, y + 1, z, w.b("white_concrete") if z == 0 else w.b("smooth_quartz"))
            w.setze(x, y + 2, z, w.b("quartz_stairs", facing="east" if x < 0 else "west", half="bottom",
                                     shape="straight", waterlogged=False) if abs(x) > 1 else
                    w.b("quartz_slab", type="bottom", waterlogged=False))
        for z in (-2, 2):
            if k % 3 == 0:
                w.setze(x, y + 3, z, w.b("quartz_slab", type="bottom", waterlogged=False))
    for sx in (-1, 1):
        x = sx * (round(rb) + 2)
        laternenpfahl(w, x, 1, 2)
        laternenpfahl(w, x, 1, -2)
        for z in (-1, 0, 1):
            w.setze(sx * (round(rb) + 1), 1, z, w.b("smooth_quartz"))
    rng = w.rng
    for k in range(int(12 * s)):
        a = rng.random() * 6.28
        x, z = round(math.cos(a) * R * 0.72), round(math.sin(a) * R * 0.47)
        if (x, z) in zellen and zellen[(x, z)] >= 0:
            w.setze(x, zellen[(x, z)] + 1, z, w.b(["blue_orchid", "azure_bluet", "lily_of_the_valley"][k % 3]))
    baumrand(w, zellen, R, 3 + 2 * g, seed, innen=0.85)
    return w


PARKS3 = {
    "monopteros": ("Landschaftsgarten mit Monopteros", monopteros),
    "gartenruine": ("Gartenruine", gartenruine),
    "orangerie": ("Orangerie", orangerie),
    "muschelgrotte": ("Muschelgrotte", muschelgrotte),
    "sonnenuhr_rondell": ("Sonnenuhr-Rondell", sonnenuhr_rondell),
    "formschnitt": ("Formschnittgarten", formschnitt),
    "lindenallee": ("Lindenallee", lindenallee),
    "wasserspiele": ("Wasserspiel-Platz", wasserspiele),
    "minigolf": ("Minigolfplatz", minigolf),
    "aussichtsturm": ("Aussichtsturm", aussichtsturm),
    "steingarten": ("Steingarten", steingarten),
    "tulpenbeete": ("Tulpenbeete", tulpenbeete),
    "wassertretstelle": ("Wassertretstelle", wassertretstelle),
    "bootsverleih": ("Bootsverleih am Parksee", bootsverleih),
    "parkcafe": ("Parkcafé", parkcafe),
    "rosenbogengang": ("Rosenbogengang", rosenbogengang),
    "entenhaus": ("Entenhaus am Teich", entenhaus),
    "picknickwiese": ("Picknickwiese", picknickwiese),
    "insektenhotel": ("Bienenweide mit Insektenhotel", insektenhotel),
    "mondbruecke": ("Mondbrücke", mondbruecke),
}

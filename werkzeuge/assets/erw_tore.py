"""Brücken & Tore II – zwanzig weitere Brücken und Tore: Kettenbrücke, Dreibogenbrücke, Drehbrücke, Hubbrücke,
Stadttor mit Uhrturm, Vierbogentor, Laternensteg, Seebrücke mit Pavillon, Schmiedeeisentor, Wasserfallbrücke,
Glasbrücke, Brückenturm, Regenbogenbrücke, Blumenbrücke, Lebendes Weidentor, Selbsttragende Holzbrücke, Trogbrücke,
Schlangenbrücke, Walknochenbogen und Baumwipfelpfad."""

from __future__ import annotations

import math

from erw_basis import M, S, baum, figur, haus, hoehe, wiese
from erw_gewaesser import baeume, landschaft
from feinbau import Dachmat, kegeldach, laterne, satteldach
from flora import _neu
from leuchtwald2 import baum_aeste, bez, kugel, laubball, rohr
from lib import Rauschen
from skulptur import ell, kap


def flusstal(w, s, R, breite, ufer=2.0, tief=-2, wy=0, steil=0.0):
    rn = Rauschen(w, 5)

    def hf(x, z):
        d = abs(z - math.sin(x / 8) * 1.5)
        if d < breite:
            return tief
        return ufer + (d - breite) * steil + rn(x, 2, z) * 1.2

    return landschaft(w, R, hf, wy=wy)


def mauer(w):
    return M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 1), ("cracked_stone_bricks", 0.6)])


def wand(w, x, y, z, blk="stone_brick_wall"):
    w.setze(x, y, z, w.b(blk, up=True, north="none", south="none", east="none", west="none", waterlogged=False))


def bogenpfeiler(w, x0, x1, z0, z1, y_unten, y_deck, st, spannweiten, achse="z"):
    """Massiver Brückenkörper mit Bögen zwischen y_unten und y_deck entlang z (Breite x0..x1)."""
    L0, L1 = z0, z1
    piers = []
    pos = L0
    for sp in spannweiten:
        piers.append((pos, pos + sp))
        pos += sp + 2
    for z in range(L0, L1 + 1):
        oben = y_deck
        unten = y_unten
        for (a, b) in piers:
            if a < z < b:
                u = (z - (a + b) / 2) / ((b - a) / 2)
                unten = y_unten + round((y_deck - 2 - y_unten) * math.sqrt(max(0, 1 - u * u)))
        for x in range(x0, x1 + 1):
            for y in range(unten if unten > y_unten else y_unten, oben + 1):
                p = (x, y, z) if achse == "z" else (z, y, x)
                w.setze(*p, st(*p))


# ============================================================================ Brücken

def kettenbruecke(seed, g=2):
    """Kettenbrücke: zwei wuchtige Steinpylone mit Rundbogendurchfahrt tragen an schweren Eisenketten eine lange
    Fahrbahn über einen breiten Fluss; die Hänger fallen senkrecht von den durchhängenden Ketten."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rw = int(R * 0.45)
    hs = flusstal(w, s, R, rw, ufer=2, tief=-3)
    yd = int(4 + s)
    L = R
    for z in range(-L, L + 1):
        for x in range(-2, 3):
            if math.hypot(x, z) <= R + 1:
                w.setze(x, yd, z, w.b("spruce_planks") if abs(x) < 2 else w.b("stone_bricks"))
                w.setze(x, yd + 1, z, w.b("iron_bars", north=True, south=True, east=False, west=False,
                                          waterlogged=False)) if abs(x) == 2 else None
    st = mauer(w)
    Hp = int(10 * s + 7)
    for zp in (-rw - 1, rw + 1):
        for x in (-4, -3, 3, 4):
            for dz in (-1, 0, 1):
                for y in range(-3, yd + Hp):
                    w.setze(x, y, zp + dz, st(x, y, zp + dz))
        for x in range(-4, 5):
            for dz in (-1, 0, 1):
                for y in range(yd + Hp - 3, yd + Hp):
                    w.setze(x, y, zp + dz, st(x, y, zp + dz))
                w.setze(x, yd + Hp, zp + dz, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    for sx in (-2, 2):
        pts = []
        for z in range(-L, L + 1):
            if abs(z) <= rw + 1:
                t = z / (rw + 1)
                y = yd + 2 + (Hp - 3) * t * t
            else:
                t = (abs(z) - rw - 1) / max(1, L - rw - 1)
                y = yd + Hp - 1 - (Hp - 2) * t
            pts.append((z, round(y)))
            w.setze(sx, round(y), z, w.b("chain", axis="z", waterlogged=False), False)
        for (z, y) in pts:
            if abs(z) < rw and z % 2 == 0:
                for yy in range(yd + 1, y):
                    w.setze(sx, yy, z, w.b("chain", axis="y", waterlogged=False), False)
    return w


def dreibogenbruecke(seed, g=2):
    """Dreibogenbrücke: eine schwere Steinbrücke mit drei halbrunden Bögen und spitzen Wellenbrechern an den Pfeilern,
    gepflasterter Fahrbahn, Brüstung mit Nischen und einer Heiligenfigur in der Mitte."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rw = int(R * 0.5)
    flusstal(w, s, R, rw, ufer=1, tief=-3)
    st = mauer(w)
    yd = int(5 + 2 * s)
    sp = int((2 * rw - 4) / 3)
    bogenpfeiler(w, -2, 2, -rw - 4, rw + 4, -3, yd, st, [4, sp, sp, sp, 4])
    for z in range(-rw - 6, rw + 7):
        for x in range(-1, 2):
            w.setze(x, yd, z, w.b("cobblestone") if (x + z) % 3 else w.b("andesite"))
        for x in (-2, 2):
            if abs(z) <= rw + 4:
                wand(w, x, yd + 1, z)
    for zp in (-rw + 4 + sp - 1, -rw + 4 + 2 * sp + 1):
        for x in (-3, 3):
            w.setze(x, -1, zp, w.b("stone_brick_stairs", facing="north", half="bottom", shape="straight",
                                   waterlogged=True))
    figur(w, 0.32 * s + 0.25, [(kap((0, 0, 0), (0, 3, 0), 0.6, 0.45), w.b("smooth_stone")),
                               (ell(0, 3.6, 0, 0.45, 0.5, 0.45), w.b("smooth_stone"))], (-2, -1, -2), (2, 5, 2),
          pos=(2, yd + 2, 0))
    return w


def drehbruecke(seed, g=2):
    """Drehbrücke: eine eiserne Fachwerkbrücke ruht auf einem runden Drehpfeiler mitten im Kanal und ist gerade quer
    gestellt, damit ein Segelschiff passieren kann; ein Wärterhäuschen sitzt auf dem Drehteller."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rw = int(R * 0.4)
    hs = flusstal(w, s, R, rw, ufer=2, tief=-3)
    yd = 3
    for x in range(-2, 3):
        for z in range(-2, 3):
            if math.hypot(x, z) <= 2.5:
                for y in range(-3, yd):
                    w.setze(x, y, z, w.b("stone_bricks"))
    L = int(rw * 0.9)
    for x in range(-L, L + 1):
        for z in (-1, 0, 1):
            w.setze(x, yd, z, w.b("iron_block") if abs(z) == 1 else w.b("spruce_planks"))
        for z in (-1, 1):
            h = max(1, 3 - abs(x) * 3 // L)
            for y in range(yd + 1, yd + 1 + h):
                w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
            if (x + L) % 3 == 0:
                w.setze(x, yd + h, z, w.b("iron_block"))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            for y in range(yd + 1, yd + 3):
                if abs(dx) == 1 or abs(dz) == 1:
                    w.setze(dx, y + 3, dz, w.b("white_concrete") if y != yd + 2 else w.b("glass"))
        w.setze(dx, yd + 6, 0, w.b("red_concrete"))
    for sz in (-1, 1):
        zz = sz * (rw + 1)
        for z in range(zz, sz * (R + 1), sz):
            for x in range(-1, 2):
                if (x, z) in hs:
                    w.setze(x, yd, z, w.b("cobblestone"))
    for x in range(-int(R * 0.6), -int(R * 0.6) + 8):
        for dz in (-1, 0, 1):
            w.setze(x, -1, int(rw * 0.5) + dz, w.b("dark_oak_planks"))
    for y in range(0, int(8 + 3 * s)):
        w.setze(-int(R * 0.6) + 4, y, int(rw * 0.5), w.b("dark_oak_log", axis="y"))
    return w


def hubbruecke(seed, g=2):
    """Hubbrücke: zwischen zwei hohen Stahltürmen mit Gegengewichten hängt ein Brückenfeld, das an Seilen ganz nach
    oben gezogen ist, damit Schiffe darunter hindurchfahren; Rollen und Maschinenhäuser auf den Turmspitzen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rw = int(R * 0.4)
    flusstal(w, s, R, rw, ufer=2, tief=-3)
    Ht = int(12 * s + 8)
    for zt in (-rw - 1, rw + 1):
        for x in (-3, 3):
            for dz in (-1, 1):
                for y in range(-3, Ht):
                    w.setze(x, y, zt + dz, w.b("iron_block") if (y % 4 == 0) else w.b("gray_concrete"))
            for y in range(0, Ht, 4):
                for dz in (-1, 0, 1):
                    w.setze(x, y, zt + dz, w.b("iron_block"))
        for x in range(-3, 4):
            for dz in (-1, 0, 1):
                for y in range(Ht, Ht + 3):
                    w.setze(x, y, zt + dz, w.b("light_gray_concrete") if y < Ht + 2 else w.b("gray_concrete"))
        for x in (-3, 3):
            for y in range(int(Ht * 0.4), int(Ht * 0.4) + 3):
                w.setze(x + (1 if x > 0 else -1), y, zt, w.b("stone"))
    yh = Ht - 4
    for z in range(-rw, rw + 1):
        for x in range(-2, 3):
            w.setze(x, yh, z, w.b("iron_block") if abs(x) == 2 else w.b("gray_concrete"))
    for zt in (-rw - 1, rw + 1):
        for x in (-2, 2):
            for y in range(yh + 1, Ht):
                w.setze(x, y, zt - (1 if zt > 0 else -1), w.b("chain", axis="y", waterlogged=False), False)
    for sz in (-1, 1):
        for z in range(sz * (rw + 3), sz * (R + 1), sz):
            for x in range(-2, 3):
                w.setze(x, 2, z, w.b("gray_concrete"))
    return w


# ============================================================================ Tore

def stadttor_uhr(seed, g=2):
    """Stadttor mit Uhrturm: ein hohes, schlankes Tortor mit spitzbogiger Durchfahrt, auf dem ein Uhrturm mit
    großem Zifferblatt, Laterne und Wetterfahne sitzt; seitlich Reste der Stadtmauer mit Wehrgang."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.1)
    st = mauer(w)
    B = int(3 + s)
    H = int(10 * s + 8)
    for x in range(-B, B + 1):
        for z in range(-2, 3):
            for y in range(1, H + 1):
                innen = abs(x) <= B - 2 and y <= int(4 + s) + (0 if abs(x) < B - 2 else -1)
                if innen:
                    continue
                if abs(x) == B or abs(z) == 2 or y in (H,):
                    w.setze(x, y, z, st(x, y, z))
    for z in (-2, 2):
        for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)):
            w.setze(dx, H - 4 + dy, z + (1 if z > 0 else -1), w.b("white_concrete") if (dx, dy) != (0, 0) else
                    w.b("gold_block"))
        w.setze(0, H - 3, z + (1 if z > 0 else -1), w.b("black_concrete"))
        w.setze(1, H - 4, z + (1 if z > 0 else -1), w.b("black_concrete"))
    kegeldach(w, 0, 0, H + 1, B, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]), form="nadel", eckig=True)
    for sx in (-1, 1):
        for x in range(sx * (B + 1), sx * R, sx):
            for z in (-1, 0, 1):
                if math.hypot(x, z) < R:
                    for y in range(1, 6):
                        w.setze(x, y, z, st(x, y, z))
                    if (x + z) % 2 == 0 and z != 0:
                        w.setze(x, 6, z, st(x, 6, z))
    return w


def vierbogentor(seed, g=2):
    """Vierbogentor: auf einer Straßenkreuzung steht ein quadratischer Torbau mit vier gleichen Rundbögen, einer flachen
    Kuppel darüber, Säulen an den Ecken, Reliefbändern und einer Figurengruppe auf dem Dach."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, huegel=0.0)
    for (x, z), h in zellen.items():
        if abs(x) <= 2 or abs(z) <= 2:
            w.setze(x, 0, z, w.b("smooth_stone") if (x + z) % 2 else w.b("polished_andesite"))
            w.bloecke.pop((x, 1, z), None)
    st = M(w, [("smooth_quartz", 2), ("quartz_bricks", 1), ("calcite", 1)])
    A = int(4 + 1.5 * s)
    H = int(8 + 3 * s)
    hb = int(4 + 2 * s)
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            for y in range(1, H + 1):
                ax, az = abs(x), abs(z)
                durch = (ax <= 2 or az <= 2) and y <= hb + (1 if min(ax, az) <= 1 else 0)
                if durch:
                    continue
                if ax == A or az == A or y == H:
                    w.setze(x, y, z, st(x, y, z))
            if abs(x) == A and abs(z) == A:
                for y in range(1, H):
                    w.setze(x + (1 if x > 0 else -1), y, z + (1 if z > 0 else -1), w.b("quartz_pillar", axis="y"))
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            if max(abs(x), abs(z)) == A and (x + z) % 2:
                w.setze(x, H - 2, z, w.b("chiseled_quartz_block"))
    from wueste_eis import kuppel
    kuppel(w, w.b("waxed_oxidized_cut_copper"), 0, 0, H + 1, A - 1, spitze=None)
    figur(w, 0.4 * s + 0.3, [(kap((0, 0, 0), (0, 3, 0), 0.7, 0.5), w.b("gold_block")),
                             (ell(0, 3.6, 0, 0.5, 0.5, 0.5), w.b("gold_block")),
                             (kap((0, 2.5, 0), (0.8, 4.8, 0), 0.2), w.b("gold_block"))], (-2, -1, -2), (2, 6, 2),
          pos=(0, H + A, 0))
    return w


def laternensteg(seed, g=2):
    """Laternensteg: ein langer, schmaler Holzsteg auf Pfählen zieht sich im Zickzack über einen nächtlichen Teich,
    an jedem Knick ein hoher Pfosten mit roter Papierlaterne, Seerosen und Lichtspiegelungen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)

    def hf(x, z):
        return -2 if math.hypot(x, z) + rn(x, 1, z) * 2 < R * 0.8 else 1

    hs = landschaft(w, R, hf, wy=0)
    rng = w.rng
    for (x, z), h in hs.items():
        if h < 0 and rng.random() < 0.05:
            w.setze(x, 1, z, w.b("lily_pad"))
    pts = []
    n = int(4 + 2 * s)
    for k in range(n + 1):
        t = k / n
        pts.append((round(-R * 0.75 + 1.5 * R * t), round((k % 2 * 2 - 1) * R * 0.2)))
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        m = max(abs(bx - ax), abs(bz - az))
        for k in range(m + 1):
            x, z = round(ax + (bx - ax) * k / m), round(az + (bz - az) * k / m)
            for dz in (0, 1):
                w.setze(x, 1, z + dz, w.b("dark_oak_slab", type="top", waterlogged=False))
            if k % 3 == 0:
                w.setze(x, 0, z, w.b("dark_oak_log", axis="y"))
    for (x, z) in pts:
        for y in range(2, 6):
            w.setze(x - 1, y, z, w.b("dark_oak_fence"))
        w.setze(x, 5, z, w.b("dark_oak_fence"))
        w.setze(x, 4, z, w.b("red_wool"))
        w.setze(x, 3, z, w.b("shroomlight"))
    return w


def seebruecke(seed, g=2):
    """Seebrücke mit Pavillon: eine lange, weiße Holzbrücke führt auf Stelzen weit ins Meer, gesäumt von Bänken und
    Laternen, an ihrem Ende ein achteckiger Pavillon mit Kuppeldach und eine Bootsanlegestelle."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 4)

    def hf(x, z):
        return 1 if z < -R * 0.55 + rn(x, 1, 0) * 2 else -3

    landschaft(w, R, hf, wy=0)
    yd = 3
    L = int(R * 0.6)
    for z in range(-int(R * 0.7), L):
        for x in range(-1, 2):
            w.setze(x, yd, z, w.b("birch_planks"))
        for x in (-2, 2):
            w.setze(x, yd + 1, z, w.b("birch_fence"))
        if z % 3 == 0:
            for x in (-2, 2):
                for y in range(-3, yd):
                    w.setze(x, y, z, w.b("birch_log", axis="y"))
        if z % 6 == 0:
            laterne(w, 2, yd + 3, z, kette=0)
            w.setze(2, yd + 2, z, w.b("birch_fence"))
    rp = int(3 + s)
    for x in range(-rp - 1, rp + 2):
        for z in range(L - 1, L + 2 * rp + 2):
            if max(abs(x), abs(z - L - rp), (abs(x) + abs(z - L - rp)) / 1.42) <= rp:
                w.setze(x, yd, z, w.b("birch_planks"))
                if (x + z) % 2 == 0 and max(abs(x), abs(z - L - rp)) >= rp - 0.5:
                    for y in range(yd + 1, yd + 4):
                        w.setze(x, y, z, w.b("white_concrete"))
    kegeldach(w, 0, L + rp, yd + 4, rp + 0.5, Dachmat(w, ["mcw:green_terracotta", "mcw:cyan_terracotta"]),
              eckig=True, form="glocke", spitze="lightning_rod")
    for k in range(3):
        w.setze(-rp - 2, 0, L + 2 + k, w.b("spruce_planks"))
    return w


def schmiedeeisentor(seed, g=1):
    """Schmiedeeisentor: ein prächtiges, zweiflügeliges Parktor aus schwarzem Schmiedeeisen mit goldenen Spitzen und
    Ranken, zwischen zwei Steinpfeilern mit Vasen, flankiert von Eisenzäunen und Hecken, dahinter eine Allee."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, huegel=0.0)
    B = int(2 + s)
    H = int(5 + 2 * s)
    for z in range(-R, R + 1):
        for x in range(-B, B + 1):
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("gravel"))
                w.bloecke.pop((x, 1, z), None)
    for sx in (-B - 1, B + 1):
        for y in range(1, H + 2):
            for dx in (0, sx // abs(sx)):
                w.setze(sx + dx, y, 0, w.b("stone_bricks") if y < H + 1 else w.b("chiseled_stone_bricks"))
        w.setze(sx, H + 2, 0, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False))
    for x in range(-B, B + 1):
        hb = H - round(abs(x) / B * 1.5) + (1 if x == 0 else 0)
        for y in range(1, hb + 1):
            w.setze(x, y, 0, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False)
                    if (x + y) % 4 else w.b("black_concrete"))
        w.setze(x, hb + 1, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
        w.setze(x, hb, 0, w.b("gold_block")) if x % 2 == 0 else None
    for sx in (-1, 1):
        for x in range(sx * (B + 3), sx * R, sx):
            if (x, 0) in zellen:
                w.setze(x, 1, 0, w.b("stone_bricks"))
                w.setze(x, 2, 0, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
                w.setze(x, 3, 0, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
                for z in (-1,):
                    for y in (1, 2, 3):
                        w.setze(x, y, z, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
    for k in range(int(2 + s)):
        z = -4 - k * 5
        for sx in (-B - 2, B + 2):
            if (sx, z) in zellen:
                baum(w, sx, 1, z, seed + k, 5 + 2 * s)
    return w


def wasserfallbruecke(seed, g=2):
    """Wasserfallbrücke: eine schmale Steinbogenbrücke spannt sich direkt über die Kante eines Wasserfalls, das Wasser
    stürzt unter dem Bogen in die Tiefe; Gischt, Moos und Farne an den Felsen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    H = int(8 * s + 6)

    def hf(x, z):
        bach = abs(x) < 2.5 + s
        if z < 0:
            return H - (2 if bach else -rn(x, 2, z) * 2)
        return (-1 if bach else 2 + rn(x, 3, z) * 2)

    hs = landschaft(w, R, hf, wy=None)
    for (x, z), h in hs.items():
        if abs(x) < 2.5 + s:
            w.setze(x, h + 1, z, w.b("water", level=0)) if z < 0 else w.setze(x, 0, z, w.b("water", level=0))
    for x in range(-int(2.5 + s), int(2.5 + s) + 1):
        for y in range(0, H):
            w.setze(x, y, 1, w.b("water", level=0))
    st = mauer(w)
    for x in range(-int(5 + s), int(5 + s) + 1):
        t = x / (5 + s)
        y = H + 1 + round((1 - t * t) * 2)
        for z in (-1, 0):
            w.setze(x, y, z, st(x, y, z))
            w.setze(x, y - 1, z, st(x, y - 1, z)) if abs(x) > 2 + s else None
        wand(w, x, y + 1, -1)
    return w


def glasbruecke(seed, g=2):
    """Glasbrücke: eine moderne, gläserne Fußgängerbrücke mit schlankem Stahlbogen spannt sich hoch über eine Schlucht;
    der Boden ist durchsichtig, Leuchtstreifen säumen die Ränder."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    H = int(10 * s + 6)
    sp = 4 + 2 * s

    def hf(x, z):
        d = abs(z - math.sin(x / 6) * 1.5)
        return -2 if d < sp else (H if z < 0 else H * 0.4) + rn(x, 2, z) * 2

    landschaft(w, R, hf, wy=-1)
    yd = int(H * 0.4) + 1
    L = int(sp + 3)
    for z in range(-L, L + 1):
        for x in (-1, 0, 1):
            w.setze(x, yd, z, w.b("light_blue_stained_glass") if x == 0 else w.b("glass"))
        for x in (-2, 2):
            w.setze(x, yd, z, w.b("iron_block"))
            w.setze(x, yd + 1, z, w.b("glass_pane"))
            if z % 3 == 0:
                w.setze(x, yd, z, w.b("sea_lantern"))
    for k in range(int(2 * L * 2)):
        t = k / (2 * L * 2)
        z = -L + 2 * L * t
        y = yd - 1 - math.sin(t * math.pi) * (yd + 1) * 0.8
        for x in (-1, 1):
            w.setze(x, round(y), round(z), w.b("white_concrete"), False)
    return w


def brueckenturm(seed, g=2):
    """Brückenturm: in der Mitte einer zweibogigen Steinbrücke erhebt sich ein Wehrturm mit Durchfahrt, Erkern und
    spitzem Dach; die Brücke führt über einen Fluss zwischen zwei Ufern mit Häusern."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rw = int(R * 0.45)
    flusstal(w, s, R, rw, ufer=1, tief=-3)
    st = mauer(w)
    yd = int(4 + s)
    bogenpfeiler(w, -2, 2, -rw - 3, rw + 3, -3, yd, st, [rw, rw])
    for z in range(-rw - 6, rw + 7):
        for x in range(-1, 2):
            w.setze(x, yd, z, w.b("cobblestone"))
        for x in (-2, 2):
            wand(w, x, yd + 1, z)
    B = 3
    Ht = int(8 * s + 6)
    for x in range(-B, B + 1):
        for z in range(-B, B + 1):
            for y in range(yd + 1, yd + Ht):
                if max(abs(x), abs(z)) == B and not (abs(x) <= 1 and y <= yd + 3):
                    w.setze(x, y, z, st(x, y, z))
    kegeldach(w, 0, 0, yd + Ht, B, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]), form="kegel", eckig=True)
    for sz in (-1, 1):
        haus(w, 0, sz * (rw + 8), 6, 5, 2, M(w, [("white_terracotta", 2), ("calcite", 1)]), holz="dark_oak", H=3,
             dach=("mcw:red_terracotta", "brick"), tuer_s="north" if sz > 0 else "south")
    return w


def regenbogenbruecke(seed, g=2):
    """Regenbogenbrücke: eine hoch gewölbte Bogenbrücke, deren Fahrbahn aus sieben farbigen Streifen in Regenbogen-
    farben besteht, spannt sich über einen Wolkensee; an beiden Enden kleine Wolkeninseln."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    from himmel import wolke
    farben = ["red", "orange", "yellow", "lime", "light_blue", "blue", "purple"]
    L = R * 0.8
    H = 6 + 4 * s
    for k in range(int(L * 4)):
        t = k / (L * 4)
        z = -L + 2 * L * t
        y = 4 + math.sin(t * math.pi) * H
        for j, f in enumerate(farben):
            x = j - 3
            w.setze(x, round(y), round(z), w.b(f"{f}_stained_glass") if j % 2 else w.b(f"{f}_concrete"), False)
    for sz in (-1, 1):
        wolke(w, 0, 2, round(sz * (L + 1)), 3 + 1.5 * s, flach=0.5, dichte=6, seed_off=sz)
    wolke(w, -int(R * 0.5), 0, 0, 2.5 + s, flach=0.5, dichte=5, seed_off=3)
    wolke(w, int(R * 0.5), 1, 2, 2 + s, flach=0.5, dichte=5, seed_off=4)
    return w


def blumenbruecke(seed, g=2):
    """Blumenbrücke: eine alte, überdachte Holzbrücke über einen Bach, deren Brüstungen über die ganze Länge mit
    Blumenkästen voller roter und rosa Geranien behängt sind; Efeu klettert an den Pfosten."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    rw = int(R * 0.35)
    flusstal(w, s, R, rw, ufer=1, tief=-2)
    yd = 2
    L = rw + 3
    B = 2
    for z in range(-L, L + 1):
        for x in range(-B, B + 1):
            w.setze(x, yd, z, w.b("spruce_planks"))
        for x in (-B - 1, B + 1):
            w.setze(x, yd + 1, z, w.b("spruce_planks"))
            w.setze(x, yd + 2, z, w.b("spruce_fence"))
            sx = 1 if x > 0 else -1
            w.setze(x + sx, yd + 1, z, w.b("spruce_trapdoor", facing="east" if sx > 0 else "west", half="top",
                                           open=True, powered=False, waterlogged=False))
            w.setze(x + sx, yd + 2, z, w.b(["red_wool", "pink_wool", "red_terracotta"][z % 3]), False)
            if z % 3 == 0:
                for y in range(yd + 1, yd + 5):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
            if z % 2 == 0:
                w.setze(x, yd + 3, z, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
    satteldach(w, -B - 2, -L, B + 2, L, yd + 5, Dachmat(w, ["spruce", "dark_oak"]), first_x=False, ue=0)
    for z in range(-L, L + 1, 4):
        for y in range(-2, yd):
            w.setze(0, y, z, w.b("stone_bricks"))
    return w


def weidentor(seed, g=1):
    """Lebendes Weidentor: aus lebenden Weidenruten wurde ein hoher Spitzbogen geflochten, durch den ein Gartenweg
    führt; zu beiden Seiten setzt sich ein geflochtener Weidenzaun fort, Blüten wachsen am Fuß."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    zellen = wiese(w, R, huegel=0.05, blumen=0.05)
    for z in range(-R, R + 1):
        for x in (-1, 0, 1):
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("dirt_path"))
                w.bloecke.pop((x, 1, z), None)
    B = int(2 + s)
    H = int(5 + 2 * s)
    for k in range(3):
        for sx in (-1, 1):
            pts = bez((sx * (B + k * 0.3), 0, (k - 1) * 0.7), (sx * (B + 0.5), H * 0.7, (k - 1) * 0.5),
                      (-sx * 0.5, H + 0.5, (k - 1) * 0.3))
            rohr(w, pts, 0.4, 0.3, w.b("stripped_oak_log", axis="y"), rauh=0.0)
    for y in range(int(H * 0.5), H + 2):
        for x in range(-B - 1, B + 2):
            if abs(x) >= B - 1 or y >= H:
                w.setze(x, y, 0, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False), False)
    for sx in (-1, 1):
        for x in range(sx * (B + 2), sx * R, sx):
            for y in (1, 2):
                if (x, 0) in zellen:
                    w.setze(x, y, 0, w.b("stripped_oak_log", axis="x") if (x + y) % 2 else w.b("oak_fence"))
    return w


def holzbogenbruecke(seed, g=2):
    """Selbsttragende Holzbrücke: eine Bogenbrücke, die nur aus ineinander verkeilten Holzbalken besteht – ohne Nägel
    oder Seile –, spannt sich in einem eleganten Bogen über einen Bach."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    rw = int(R * 0.35)
    flusstal(w, s, R, rw, ufer=1, tief=-2)
    L = rw + 3
    H = 3 + 2 * s
    n = int(6 + 2 * s)
    for k in range(n):
        t0 = k / n
        t1 = (k + 1.6) / n
        for sx in (-2, 0, 2) if k % 2 == 0 else (-1, 1):
            z0, z1 = -L + 2 * L * t0, -L + 2 * L * min(1, t1)
            y0, y1 = 1 + math.sin(t0 * math.pi) * H, 1 + math.sin(min(1, t1) * math.pi) * H
            m = int(abs(z1 - z0) * 2) + 1
            for j in range(m + 1):
                q = j / m
                w.setze(sx, round(y0 + (y1 - y0) * q + (0.5 if k % 2 else 0)), round(z0 + (z1 - z0) * q),
                        w.b("spruce_log", axis="z"), False)
        for x in range(-2, 3):
            zq = -L + 2 * L * t0
            w.setze(x, round(1 + math.sin(t0 * math.pi) * H) + 1, round(zq), w.b("dark_oak_log", axis="x"), False)
    return w


def trogbruecke(seed, g=2):
    """Trogbrücke: ein schiffbarer Kanal überquert auf einer gemauerten Bogenbrücke in einem wassergefüllten Trog ein
    tiefer liegendes Flusstal; ein Lastkahn fährt gerade über den Fluss hinweg."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 5)
    H = int(6 + 3 * s)

    def hf(x, z):
        d = abs(x - math.sin(z / 8) * 1.5)
        return -2 if d < 3 + s else min(H, 1 + (d - 3 - s) * 0.8) + rn(x, 2, z)

    hs = landschaft(w, R, hf, wy=0)
    st = mauer(w)
    sp = int(4 + 2 * s)
    bogenpfeiler(w, -R, R, -3, 3, -2, H, st, [R // 2, sp, sp, R // 2], achse="x")
    for x in range(-R, R + 1):
        for z in range(-2, 3):
            if math.hypot(x, z) > R + 1:
                continue
            if abs(z) == 2:
                w.setze(x, H + 1, z, st(x, H + 1, z))
                w.setze(x, H + 2, z, st(x, H + 2, z))
            else:
                w.setze(x, H + 1, z, w.b("water", level=0))
                w.setze(x, H + 2, z, w.b("water", level=0))
        w.setze(x, H + 3, 3, w.b("gravel")) if math.hypot(x, 3) < R else None
    for x in range(-2, 4):
        w.setze(x, H + 2, 0, w.b("spruce_planks"))
        w.setze(x, H + 3, 0, w.b("barrel", facing="up", open=False)) if x % 2 else None
    return w


def schlangenbruecke(seed, g=2):
    """Schlangenbrücke: eine Brücke in Gestalt einer riesigen steinernen Schlange, deren gewundener Leib in Bögen aus dem
    Wasser taucht und die Fahrbahn trägt; am Ufer der Kopf mit offenem Maul als Torbogen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rw = int(R * 0.45)
    flusstal(w, s, R, rw, ufer=1, tief=-3)
    st = M(w, [("mossy_stone_bricks", 2), ("stone_bricks", 2), ("green_terracotta", 1)])
    L = rw + 4
    pts = []
    n = int(L * 6)
    for k in range(n + 1):
        t = k / n
        z = -L + 2 * L * t
        y = 1 + abs(math.sin(t * math.pi * 3)) * (3 + 1.5 * s)
        pts.append((0, y, z, t))
    rohr(w, pts, 1.3 + 0.4 * s, 1.0 + 0.3 * s, st, rauh=0.05)
    yd = round(4 + 1.5 * s + 1.3 + 0.4 * s)
    for z in range(-L, L + 1):
        for x in (-1, 0, 1):
            w.setze(x, yd, z, w.b("smooth_stone_slab", type="bottom", waterlogged=False), False)
    kz = -L - 2
    kugel(w, 0, yd - 1, kz, 2.5 + s, st, ry=2 + 0.6 * s)
    for x in (-1, 0, 1):
        for y in range(yd - 2, yd + 1):
            for z in range(kz - 3, kz + 3):
                w.bloecke.pop((x, y + 1, z), None)
    for sx in (-1, 1):
        w.setze(sx * 2, yd + 1, kz - 1, w.b("sea_lantern"))
    return w


def walknochenbogen(seed, g=1):
    """Walknochenbogen: zwei riesige, gebogene Walkieferknochen stehen als Spitzbogen über dem Weg zu einem
    Fischerdorf, mit Seilen und Glasbojen behängt; Dünengras und Treibholz am Fuß."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    zellen = wiese(w, R, huegel=0.1, art="strand", blumen=0.0)
    for z in range(-R, R + 1):
        for x in (-1, 0, 1):
            if (x, z) in zellen:
                w.setze(x, zellen[(x, z)], z, w.b("gravel"))
    H = 6 + 3 * s
    for sx in (-1, 1):
        pts = bez((sx * (3 + s), 0, 0), (sx * (3 + s), H * 0.8, 0), (sx * 0.4, H, 0))
        rohr(w, pts, 0.8 + 0.3 * s, 0.4, w.b("bone_block", axis="y"), rauh=0.05)
    for k in range(4):
        y = round(H * (0.3 + 0.15 * k))
        for sx in (-1, 1):
            w.setze(sx * round(3 + s - k * 0.6), y, 1, w.b(["light_blue_stained_glass", "lime_stained_glass"][k % 2]),
                    False)
    rng = w.rng
    for (x, z), h in zellen.items():
        if rng.random() < 0.08 and abs(x) > 2:
            w.setze(x, h + 1, z, w.b("grass") if rng.random() < 0.7 else w.b("dead_bush"))
    for t in range(3):
        w.setze(4 + t, 1, 3, w.b("stripped_oak_log", axis="x"))
    return w


def baumwipfelpfad(seed, g=2):
    """Baumwipfelpfad: ein Netz aus Hängebrücken und Holzplattformen verbindet die Kronen mehrerer hoher Bäume, eine
    Wendeltreppe führt um einen Stamm hinauf, Seilgeländer und Laternen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, huegel=0.15, art="wald")
    rng = w.rng
    yp = int(7 + 3 * s)
    pos = []
    n = int(3 + s)
    for k in range(n):
        a = k / n * 2 * math.pi + 0.3
        x, z = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        H = yp + 5 + 2 * s
        rohr(w, bez((x, -1, z), (x, H * 0.5, z), (x, H, z)), 1.0 + 0.3 * s, 0.6, w.b("oak_log", axis="y"))
        laubball(w, x, H + 1, z, 3 + s, arten=("oak_leaves", "birch_leaves"))
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if math.hypot(dx, dz) <= 2.5 and (abs(dx) > 1 or abs(dz) > 1):
                    w.setze(x + dx, yp, z + dz, w.b("spruce_planks"))
        pos.append((x, z))
    for (a, b) in zip(pos, pos[1:] + pos[:1]):
        m = int(math.hypot(b[0] - a[0], b[1] - a[1]))
        for k in range(m + 1):
            t = k / m
            x, z = round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t)
            y = round(yp - math.sin(t * math.pi) * 1.5)
            w.setze(x, y, z, w.b("spruce_slab", type="top", waterlogged=False), False)
            w.setze(x, y + 1, z + 1, w.b("spruce_fence"), False) if k % 2 == 0 else None
    x0, z0 = pos[0]
    for k in range(yp * 3):
        a = k * 0.5
        y = 1 + k // 3
        if y >= yp:
            break
        w.setze(round(x0 + math.cos(a) * 2.5), y, round(z0 + math.sin(a) * 2.5), w.b("spruce_slab", type="top",
                                                                                   waterlogged=False), False)
    return w


TORE3 = {
    "kettenbruecke": ("Kettenbrücke", kettenbruecke),
    "dreibogenbruecke": ("Dreibogenbrücke", dreibogenbruecke),
    "drehbruecke": ("Drehbrücke", drehbruecke),
    "hubbruecke": ("Hubbrücke", hubbruecke),
    "stadttor_uhr": ("Stadttor mit Uhrturm", stadttor_uhr),
    "vierbogentor": ("Vierbogentor", vierbogentor),
    "laternensteg": ("Laternensteg", laternensteg),
    "seebruecke": ("Seebrücke mit Pavillon", seebruecke),
    "schmiedeeisentor": ("Schmiedeeisentor", schmiedeeisentor),
    "wasserfallbruecke": ("Wasserfallbrücke", wasserfallbruecke),
    "glasbruecke": ("Glasbrücke", glasbruecke),
    "brueckenturm": ("Brückenturm", brueckenturm),
    "regenbogenbruecke": ("Regenbogenbrücke", regenbogenbruecke),
    "blumenbruecke": ("Blumenbrücke", blumenbruecke),
    "weidentor": ("Lebendes Weidentor", weidentor),
    "holzbogenbruecke": ("Selbsttragende Holzbrücke", holzbogenbruecke),
    "trogbruecke": ("Trogbrücke", trogbruecke),
    "schlangenbruecke": ("Schlangenbrücke", schlangenbruecke),
    "walknochenbogen": ("Walknochenbogen", walknochenbogen),
    "baumwipfelpfad": ("Baumwipfelpfad", baumwipfelpfad),
}

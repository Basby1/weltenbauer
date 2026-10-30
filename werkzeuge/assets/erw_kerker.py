"""Kerker & Gefängnis II – zwanzig weitere Bauten: Rundgefängnis, Gefängnisschiff, Klippengefängnis, Brückenzellen,
Steinbruch-Strafkolonie, Käfigsäule, Zellenschacht, Wachkaserne, Kanalverlies, Eiskerker, Glutverlies, Kasematten,
Schluchtkäfige, Asservatenkammer, Fallgatter-Torhaus, Gefängnisküche, Leuchtwachturm, Kerkerkapelle, Versunkenes
Verlies und Baumkerker."""

from __future__ import annotations

import math

from erw_basis import M, S, figur, haus, hoehe, wiese, fichte
from erw_burgen import rundturm_einfach, fahne
from erw_markt import mensch
from feinbau import Dachmat, kegeldach, laterne, satteldach
from flora import _neu
from leuchtwald2 import bez, rohr, laubball, baum_aeste
from lib import Rauschen
from skulptur import ell, kap


def kmauer(w):
    return M(w, [("stone_bricks", 3), ("cobblestone", 2), ("mossy_stone_bricks", 1), ("cracked_stone_bricks", 1)])


def gitter(w, nass=False):
    return w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=nass)


def zaun_(w, holz="spruce"):
    return w.b(f"{holz}_fence", north=False, south=False, east=False, west=False, waterlogged=False)


def waechter(w, rock="blue_wool"):
    return mensch(w, rock) + [(ell(0, 4.75, 0, 0.6, 0.35, 0.6), w.b("iron_block")),
                              (kap((0.9, 0, 0.3), (0.9, 5.6, 0.3), 0.22), w.b("spruce_planks")),
                              (kap((0.9, 5.6, 0.3), (0.9, 6.4, 0.3), 0.2, 0.05), w.b("iron_block"))]


def gefangener(w):
    return mensch(w, "light_gray_wool", haar="black_wool")


def zelle(w, cx, cz, B, T, y0, H, offen="south", st=None, innen=True, nass=False):
    """Zelle: Mauerkasten, Front aus Gittern mit Eisentür, innen Strohlager, Kette und Eimer."""
    st = st or kmauer(w)
    bu = B // 2

    def P(u, v):
        return {"south": (cx + u, cz - v), "north": (cx - u, cz + v), "east": (cx - v, cz + u),
                "west": (cx + v, cz - u)}[offen]

    for u in range(-bu, bu + 1):
        for v in range(T):
            x, z = P(u, v)
            w.setze(x, y0 - 1, z, st(x, y0 - 1, z))
            w.setze(x, y0 + H, z, st(x, y0 + H, z))
            rand = abs(u) == bu or v == T - 1
            for y in range(y0, y0 + H):
                if rand:
                    w.setze(x, y, z, st(x, y, z))
                elif v == 0:
                    if u == 0 and y < y0 + 2:
                        w.setze(x, y, z, w.b("iron_door", facing=offen, half="lower" if y == y0 else "upper",
                                             hinge="left", open=False, powered=False))
                    else:
                        w.setze(x, y, z, gitter(w, nass))
                else:
                    w.bloecke.pop((x, y, z), None)
    if innen and bu >= 1 and T >= 3:
        x, z = P(-bu + 1, T - 2)
        w.setze(x, y0, z, w.b("hay_block", axis="y"))
        x, z = P(bu - 1, T - 2)
        if (bu - 1, T - 2) != (-bu + 1, T - 2):
            w.setze(x, y0, z, w.b("cauldron"))
        for y in range(y0 + 1, y0 + H):
            w.setze(x, y, z, w.b("chain", axis="y", waterlogged=nass))


def kaefig(w, cx, y, cz, holz="dark_oak", nass=False):
    """3×3-Käfig mit Boden, Gittern und Deckel."""
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(cx + dx, y, cz + dz, w.b(f"{holz}_planks"))
            w.setze(cx + dx, y + 3, cz + dz, w.b(f"{holz}_slab", type="bottom", waterlogged=nass))
            if abs(dx) == 1 or abs(dz) == 1:
                for yy in (y + 1, y + 2):
                    w.setze(cx + dx, yy, cz + dz, w.b(f"{holz}_fence", waterlogged=nass) if abs(dx) == abs(dz)
                            else gitter(w, nass))
            else:
                for yy in (y + 1, y + 2):
                    w.bloecke.pop((cx + dx, yy, cz + dz), None)


def kette(w, x, y0, y1, z, nass=False):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        w.setze(x, y, z, w.b("chain", axis="y", waterlogged=nass), False)


def wasserflaeche(w, R, y=0, tief=3, cx=0, cz=0, boden="gravel"):
    rn = Rauschen(w, 4)
    for x in range(cx - R - 2, cx + R + 3):
        for z in range(cz - R - 2, cz + R + 3):
            if math.hypot(x - cx, z - cz) <= R + 2 * rn(x, 0, z):
                for yy in range(y - tief + 1, y + 1):
                    w.setze(x, yy, z, w.b("water", level=0))
                w.setze(x, y - tief, z, w.b(boden) if rn(x, 2, z) < 0.6 else w.b("sand"))


# ============================================================================ Bauten

def rundgefaengnis(seed, g=2):
    """Rundgefängnis: ein runder, mehrstöckiger Zellenring um einen Innenhof, alle Zellen mit Gittern zur Mitte hin,
    umlaufende Galerien mit Geländern, im Zentrum ein schlanker Wachturm mit Rundumsicht und Leuchtfeuer."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 7)
    wiese(w, R + 2, huegel=0.2, art="kies", blumen=0.0)
    st = kmauer(w)
    Ra = R - 1
    Ri = Ra - 4
    n = 2 + (g >= 2) + (g >= 3)
    N = max(8, int(2 * math.pi * Ri / 4))
    for x in range(-Ra - 1, Ra + 2):
        for z in range(-Ra - 1, Ra + 2):
            d = math.hypot(x, z)
            if d > Ra + 0.5 or d < Ri - 2.6:
                continue
            a = math.atan2(z, x) % (2 * math.pi)
            sek = a / (2 * math.pi) * N
            trenn = abs(sek - round(sek)) * 2 * math.pi / N * d < 0.55
            mitte = abs(sek - math.floor(sek) - 0.5) * 2 * math.pi / N * d < 0.6
            for k in range(n):
                y0 = 1 + 4 * k
                w.setze(x, y0 - 1, z, w.b("polished_andesite") if d < Ri - 0.5 else st(x, y0 - 1, z))
                for y in range(y0, y0 + 3):
                    if d > Ra - 0.6:
                        fen = y == y0 + 1 and mitte
                        w.setze(x, y, z, gitter(w) if fen else st(x, y, z))
                    elif Ri - 0.5 < d <= Ri + 0.5:
                        if trenn:
                            w.setze(x, y, z, st(x, y, z))
                        elif mitte and y < y0 + 2:
                            w.setze(x, y, z, w.b("iron_door", facing="north", half="lower" if y == y0 else "upper",
                                                 hinge="left", open=False, powered=False))
                        else:
                            w.setze(x, y, z, gitter(w))
                    elif d > Ri + 0.5:
                        if trenn:
                            w.setze(x, y, z, st(x, y, z))
                        else:
                            w.bloecke.pop((x, y, z), None)
                    elif d < Ri - 1.6 and y == y0 and k > 0:
                        w.setze(x, y, z, w.b("iron_bars", north=True, south=True, east=True, west=True,
                                             waterlogged=False))
                if d > Ri + 0.5 and not trenn and mitte and d > Ra - 2:
                    w.setze(x, y0, z, w.b("hay_block", axis="y"))
                w.setze(x, y0 + 3, z, st(x, y0 + 3, z))
            if d < Ri - 0.5 and d >= Ri - 2.6:
                w.bloecke.pop((x, 0, z), None) if False else None
            ytop = 1 + 4 * n
            if d > Ra - 0.6 and (x + z) % 2 == 0:
                w.setze(x, ytop, z, st(x, ytop, z))
    for x in range(-Ri + 3, Ri - 2):
        for z in range(-Ri + 3, Ri - 2):
            if math.hypot(x, z) < Ri - 2.6:
                for k in range(1, n):
                    w.bloecke.pop((x, 4 * k, z), None)
    Ht = 4 * n + 6
    rundturm_einfach(w, 0, 0, 1, 2, Ht, st, None)
    for y in (Ht - 2, Ht - 1):
        for x, z in ((3, 0), (-3, 0), (0, 3), (0, -3)):
            w.bloecke.pop((x if abs(x) < 3 else int(math.copysign(2, x)), y, z if abs(z) < 3 else
                           int(math.copysign(2, z))), None)
    w.setze(0, Ht, 0, w.b("glowstone"))
    w.setze(0, Ht + 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    yb = 4 * n - 3
    for x in range(3, Ri - 1):
        w.setze(x, yb, 0, w.b("spruce_planks"))
        w.setze(x, yb + 1, 1, zaun_(w))
        w.setze(x, yb + 1, -1, zaun_(w))
    for k in range(3 + g):
        a = k * 2.1
        figur(w, 0.35 * s + 0.25, gefangener(w), (-2, -1, -2), (2, 6, 2),
              pos=(round(math.cos(a) * (Ri - 5)), 1, round(math.sin(a) * (Ri - 5))), winkel=a)
    figur(w, 0.35 * s + 0.25, waechter(w), (-2, -1, -2), (2, 7, 2), pos=(Ri - 2, yb + 1, 0), winkel=math.pi)
    return w


def gefaengnisschiff(seed, g=2):
    """Gefängnisschiff: ein abgetakelter, vor Anker liegender Schiffsrumpf mit vergitterten Stückpforten, einem
    Zellenhaus an Deck, abgebrochenen Mastenstümpfen, Ankerketten und einem Steg zum Ufer."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wasserflaeche(w, R, y=0, tief=3)
    rn = Rauschen(w, 4)
    for x in range(-R - 2, R + 3):
        for z in range(int(R * 0.65), R + 3):
            if math.hypot(x, z) <= R + 2 * rn(x, 0, z):
                for y in range(-2, 2):
                    w.setze(x, y, z, w.b("sand") if y < 1 else w.b("grass_block", snowy=False))
    L = int(R * 0.7)
    Bw = 2.2 * s + 2.5
    hull = M(w, [("dark_oak_planks", 4), ("spruce_planks", 1), ("mossy_cobblestone", 0.3)])
    yd = int(2 * s + 3)
    for x in range(-L, L + 1):
        t = x / L
        b = Bw * max(0.0, 1 - abs(t) ** (1.6 if t > 0 else 3.0)) ** 0.5
        for y in range(-2, yd + 1):
            bb = b * (0.55 + 0.45 * (y + 2) / (yd + 2))
            for z in range(-int(bb) - 1, int(bb) + 2):
                if abs(z) > bb + 0.4:
                    continue
                aussen = abs(z) > bb - 1 or y == -2
                if y == yd:
                    w.setze(x, y, z, w.b("spruce_planks") if not aussen else w.b("dark_oak_log", axis="x"))
                elif aussen:
                    port = y == yd - 2 and x % 3 == 0 and abs(t) < 0.8
                    w.setze(x, y, z, gitter(w) if port else w.b("stripped_dark_oak_log", axis="x") if y == yd - 1
                            else hull(x, y, z))
                else:
                    w.bloecke.pop((x, y, z), None)
            if abs(t) < 0.95:
                for z in (-int(b * 0.98 - 0.5), int(b * 0.98 - 0.5)):
                    w.setze(x, yd + 1, z, zaun_(w, "dark_oak"))
    hx0, hx1 = -int(L * 0.65), -int(L * 0.15)
    hb = int(Bw * 0.55)
    for x in range(hx0, hx1 + 1):
        for z in range(-hb, hb + 1):
            for y in range(yd + 1, yd + 4):
                rand = x in (hx0, hx1) or abs(z) == hb
                if rand:
                    w.setze(x, y, z, gitter(w) if y == yd + 2 and (x + z) % 2 == 0 and abs(z) == hb else
                            w.b("spruce_planks"))
                else:
                    w.bloecke.pop((x, y, z), None)
            w.setze(x, yd + 4, z, w.b("dark_oak_slab", type="bottom", waterlogged=False))
    for xm, hm in ((int(L * 0.15), int(4 * s + 3)), (int(L * 0.55), int(2 * s + 2))):
        for y in range(yd + 1, yd + 1 + hm):
            w.setze(xm, y, 0, w.b("dark_oak_log", axis="y"))
        w.setze(xm, yd + hm, 1, w.b("dark_oak_fence"))
    for k in range(int(4 * s)):
        w.setze(L - 1 + 0, yd - k, int(Bw * 0.5), w.b("chain", axis="y", waterlogged=False), False)
    zs = int(Bw) + 1
    for z in range(zs, int(R * 0.8)):
        for x in (-2, -1, 0):
            w.setze(x, yd - 1 if z < zs + 2 else 1, z, w.b("spruce_planks"))
        if z % 3 == 0:
            for y in range(-2, 2):
                w.setze(-3, y, z, w.b("spruce_log", axis="y"))
                w.setze(1, y, z, w.b("spruce_log", axis="y"))
            laterne(w, 1, 3, z, kette=0)
            w.setze(1, 2, z, w.b("spruce_fence"))
    for z in (zs, zs + 1):
        for x in (-2, -1, 0):
            w.setze(x, yd - 1 - (z - zs) * 2 + 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    for k, x in enumerate((int(L * 0.3), int(-L * 0.8))):
        figur(w, 0.32 * s + 0.25, waechter(w, "red_wool"), (-2, -1, -2), (2, 7, 2), pos=(x, yd + 1, 0),
              winkel=k * 2.0)
    return w


def klippengefaengnis(seed, g=2):
    """Klippengefängnis: auf einem steil aus dem Meer ragenden Felsen thront ein Rundturm-Gefängnis mit Mauerring,
    ein in den Fels gehauener Treppenweg windet sich hinab zu einer kleinen Anlegestelle."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wasserflaeche(w, R, y=0, tief=3)
    rn = Rauschen(w, 3)
    Rr = R * 0.5
    Hc = int(10 * s + 6)
    f = M(w, [("stone", 3), ("andesite", 2), ("diorite", 0.5), ("cobblestone", 1)])
    for x in range(-int(Rr) - 3, int(Rr) + 4):
        for z in range(-int(Rr) - 3, int(Rr) + 4):
            d = math.hypot(x, z) + rn(x, 0, z) * 2.5
            if d > Rr:
                continue
            h = Hc if d < Rr * 0.7 else int(Hc * (1 - (d - Rr * 0.7) / (Rr * 0.3)) ** 0.5)
            h += int(rn(x, 5, z) * 2)
            for y in range(-3, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h and d < Rr * 0.72 else f(x, y, z))
    st = kmauer(w)
    rt = int(2 + s)
    Ht = int(7 * s + 6)
    rundturm_einfach(w, 0, 0, Hc + 1, rt, Ht, st, None)
    kegeldach(w, 0, 0, Hc + Ht, rt + 1, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]))
    rw = Rr * 0.6
    for x in range(-int(rw) - 2, int(rw) + 3):
        for z in range(-int(rw) - 2, int(rw) + 3):
            d = math.hypot(x, z)
            if rw - 0.5 < d <= rw + 0.5:
                for y in range(Hc + 1, Hc + 4):
                    w.setze(x, y, z, st(x, y, z))
                if (x + z) % 2 == 0:
                    w.setze(x, Hc + 4, z, st(x, Hc + 4, z))
    for k in range(int(6 + 4 * s)):
        a = k * 0.8
        zellx, zellz = round(math.cos(a) * (rt + 3)), round(math.sin(a) * (rt + 3))
        if k < 3 and rw > rt + 4:
            w.setze(zellx, Hc + 1, zellz, w.b("hay_block", axis="y"))
    steps = int(Hc * 1.6)
    for k in range(steps):
        t = k / steps
        a = math.pi * 0.5 + t * math.pi * 1.6
        r = Rr * (0.98 - 0.2 * t)
        y = 1 + int(t * Hc)
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        for dx in (-1, 0):
            for dz in (-1, 0):
                w.setze(x + dx, y - 1, z + dz, w.b("stone_bricks"))
                for yy in range(y, y + 3):
                    w.bloecke.pop((x + dx, yy, z + dz), None)
    for z in range(int(Rr), int(Rr) + 6):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
        if z % 2 == 0:
            w.setze(2, 1, z, w.b("spruce_log", axis="y"))
            w.setze(2, 2, z, w.b("spruce_fence"))
    laterne(w, 2, 3, int(Rr) + 4, kette=0)
    return w


def brueckenzellen(seed, g=2):
    """Brückenzellen: eine alte Bogenbrücke aus Stein überspannt einen Fluss; unter jedem Bogen hängt an Ketten ein
    Gitterkäfig über dem Wasser, oben auf der Brücke Brüstungen, Laternen und ein Wächter."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, huegel=0.3)
    rw = int(R * 0.55)
    for x in range(-R - 2, R + 3):
        for z in range(-rw, rw + 1):
            if (x, z) in zellen or math.hypot(x, z) <= R + 1:
                for y in range(-3, 4):
                    w.bloecke.pop((x, y, z), None)
                for y in range(-2, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -3, z, w.b("gravel"))
    st = kmauer(w)
    Hb = int(4 * s + 5)
    sp = int(4 * s + 4)
    piers = list(range(-rw, rw + 1, sp))
    for z in range(-rw - 4, rw + 5):
        nah = min(abs(z - p) for p in piers)
        for x in range(-2, 3):
            arc = math.sqrt(max(0, (sp / 2) ** 2 - (sp / 2 - nah) ** 2)) / (sp / 2)
            ybog = (-3 + int(arc * (Hb + 1))) if abs(z) <= rw and arc > 0.2 else -3
            for y in range(-3, Hb + 1):
                if y < ybog and ybog > -3:
                    continue
                w.setze(x, y, z, st(x, y, z) if y < Hb else w.b("polished_andesite"))
            if abs(x) == 2:
                w.setze(x, Hb + 1, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                          west="none", waterlogged=False) if z % 4 else w.b("chiseled_stone_bricks"))
        if z % 8 == 0:
            laterne(w, 2, Hb + 3, z, kette=0)
            w.setze(2, Hb + 2, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                      west="none", waterlogged=False))
    for a, b in zip(piers, piers[1:]):
        zc = (a + b) // 2
        kaefig(w, 0, 1, zc)
        kette(w, 0, 5, Hb - 3, zc)
    figur(w, 0.32 * s + 0.25, waechter(w), (-2, -1, -2), (2, 7, 2), pos=(0, Hb + 1, -rw // 2), winkel=0.5)
    return w


def strafkolonie(seed, g=2):
    """Steinbruch-Strafkolonie: ein terrassierter Steinbruch, in dem Gefangene Steinblöcke brechen, ein hölzerner
    Lastkran, Loren auf Schienen, gestapelte Quader, ein Wachturm am Rand und eine Baracke."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 4)
    Hp = int(6 * s + 4)
    Rp = R * 0.62
    f = M(w, [("stone", 4), ("andesite", 2), ("cobblestone", 1), ("diorite", 0.4)])
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d0 = math.hypot(x, z)
            if d0 > R + 2 * rn(x, 0, z):
                continue
            d = math.hypot(x * 1.0, (z + R * 0.08) * 1.25)
            if d < Rp:
                h = max(1, Hp - 2 * int(math.ceil((Rp - d) / 2.4)))
            else:
                h = Hp
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h == Hp and rn(x, 3, z) < 0.75 else
                        w.b("gravel") if y == h and rn(x, 6, z) < 0.25 else f(x, y, z))
    rng = w.rng
    for k in range(int(6 * s + 4)):
        a = rng.random() * 6.28
        r = rng.random() * Rp * 0.8
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        y = hoehe(w, x, z, Hp + 2) + 1
        if rng.random() < 0.5:
            figur(w, 0.3 * s + 0.25, gefangener(w), (-2, -1, -2), (2, 6, 2), pos=(x, y, z), winkel=a)
        else:
            for dy in range(int(1 + rng.random() * 2)):
                w.setze(x, y + dy, z, w.b("stone_bricks") if dy % 2 == 0 else w.b("smooth_stone"))
    for x in range(-int(Rp * 0.5), int(Rp * 0.5)):
        y = hoehe(w, x, 0, Hp + 2)
        w.setze(x, y + 1, 0, w.b("rail", shape="east_west", waterlogged=False))
    kx, kz = int(Rp * 0.7), -int(Rp * 0.5)
    for y in range(Hp + 1, Hp + int(8 * s + 4)):
        w.setze(kx, y, kz, w.b("spruce_log", axis="y"))
    yk = Hp + int(8 * s + 3)
    for t in range(int(Rp * 0.6)):
        w.setze(kx - t, yk, kz + t // 2, w.b("spruce_log", axis="x"), False)
    tx, tz = kx - int(Rp * 0.6) + 1, kz + int(Rp * 0.3)
    kette(w, tx, yk - int(4 * s + 2), yk - 1, tz)
    w.setze(tx, yk - int(4 * s + 3), tz, w.b("stone_bricks"))
    wx, wz = -int(Rp * 0.85), -int(Rp * 0.6)
    Hw = int(5 * s + 5)
    for dx in (-1, 1):
        for dz in (-1, 1):
            for y in range(Hp + 1, Hp + Hw):
                w.setze(wx + dx, y, wz + dz, w.b("spruce_log", axis="y"))
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            w.setze(wx + dx, Hp + Hw, wz + dz, w.b("spruce_planks"))
            w.setze(wx + dx, Hp + Hw + 3, wz + dz, w.b("spruce_slab", type="bottom", waterlogged=False))
            if abs(dx) == 2 or abs(dz) == 2:
                w.setze(wx + dx, Hp + Hw + 1, wz + dz, zaun_(w))
    for y in range(Hp + 1, Hp + Hw):
        w.setze(wx, y, wz - 1, w.b("ladder", facing="south", waterlogged=False))
    w.setze(wx, Hp + Hw + 2, wz, w.b("bell", attachment="ceiling", facing="north", powered=False))
    haus(w, int(R * 0.15), -int(R * 0.82), 7, 4, Hp + 1, M(w, [("spruce_planks", 3), ("stripped_spruce_log", 1)]),
         holz="spruce", H=3, dach=("spruce", "dark_oak"), tuer_s="south")
    figur(w, 0.3 * s + 0.25, waechter(w), (-2, -1, -2), (2, 7, 2), pos=(wx, Hp + Hw + 1, wz + 1))
    return w


def kaefigsaeule(seed, g=2):
    """Käfigsäule: eine hohe Steinsäule, um die sich eine Wendeltreppe windet; an Auslegern hängen auf allen Höhen
    Gitterkäfige an Ketten, oben brennt ein Feuerbecken unter einer Fahne."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.3, art="kies", blumen=0.0)
    st = kmauer(w)
    Hs = int(14 * s + 8)
    for y in range(-1, Hs):
        for x in range(-2, 3):
            for z in range(-2, 3):
                if math.hypot(x, z) <= 1.6 + (0.6 if y < 2 else 0):
                    w.setze(x, y, z, st(x, y, z))
    steps = Hs * 2
    for k in range(steps):
        a = k * 0.42
        y = 1 + k // 2
        if y >= Hs:
            break
        x, z = round(math.cos(a) * 2.6), round(math.sin(a) * 2.6)
        w.setze(x, y, z, w.b("stone_brick_slab", type="bottom" if k % 2 == 0 else "top", waterlogged=False), False)
    n = int(4 + 3 * s)
    for k in range(n):
        a = k * 2.4
        y = 3 + int(k * (Hs - 6) / n)
        r = 5.5
        cx, cz = round(math.cos(a) * r), round(math.sin(a) * r)
        for t in range(2, int(r) + 1):
            w.setze(round(math.cos(a) * t), y + 6, round(math.sin(a) * t),
                    w.b("dark_oak_log", axis="x" if abs(math.cos(a)) > 0.7 else "z"), False)
        kette(w, cx, y + 4, y + 5, cz)
        kaefig(w, cx, y, cz)
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, Hs, z, w.b("chiseled_stone_bricks") if abs(x) == 2 or abs(z) == 2 else st(x, Hs, z))
    w.setze(0, Hs + 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    fahne(w, 2, Hs + 1, 2, ("black_wool", "red_wool"))
    return w


def zellenschacht(seed, g=2):
    """Zellenschacht: ein runder Schacht senkt sich in einen grasigen Hügel; in seine Wand sind auf mehreren
    Ebenen vergitterte Zellen gehauen, ein Rampenweg windet sich hinab, oben steht ein Seilwinden-Gerüst."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 5)
    H = int(10 * s + 6)
    f = M(w, [("stone", 3), ("andesite", 1), ("dirt", 1)])
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 2 * rn(x, 0, z):
                continue
            h = int(H * min(1.0, max(0.0, (R - d) / (R * 0.45))) ** 0.7 + rn(x, 3, z) * 1.5)
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else f(x, y, z))
    st = kmauer(w)
    rs = 3 + 1.5 * s
    for x in range(-int(rs) - 3, int(rs) + 4):
        for z in range(-int(rs) - 3, int(rs) + 4):
            d = math.hypot(x, z)
            for y in range(0, H + 3):
                if d <= rs:
                    w.bloecke.pop((x, y, z), None)
                elif d <= rs + 1.2:
                    w.setze(x, y, z, st(x, y, z))
            if d <= rs:
                w.setze(x, -1, z, w.b("cobblestone"))
                if d < rs * 0.5:
                    w.setze(x, 0, z, w.b("water", level=0))
    ebenen = list(range(1, H - 2, 4))
    for e, y0 in enumerate(ebenen):
        for k in range(5):
            a = k / 5 * 2 * math.pi + e * 0.6
            cx, cz = round(math.cos(a) * (rs + 3)), round(math.sin(a) * (rs + 3))
            seite = "east" if abs(math.cos(a)) > abs(math.sin(a)) and math.cos(a) < 0 else \
                "west" if abs(math.cos(a)) > abs(math.sin(a)) else "south" if math.sin(a) < 0 else "north"
            fx, fz = round(math.cos(a) * (rs + 1)), round(math.sin(a) * (rs + 1))
            zelle(w, fx, fz, 3, 3, y0, 3, offen={"east": "west", "west": "east", "south": "north",
                                                   "north": "south"}[seite], st=st)
            _ = (cx, cz)
    steps = int(2 * math.pi * rs * len(ebenen))
    for k in range(steps):
        t = k / steps
        a = t * 2 * math.pi * len(ebenen) * 0.9
        y = H - int(t * (H - 1))
        x, z = round(math.cos(a) * (rs - 0.6)), round(math.sin(a) * (rs - 0.6))
        w.setze(x, y, z, w.b("spruce_slab", type="top", waterlogged=False), False)
    for dx in (-int(rs) - 1, int(rs) + 1):
        for y in range(H, H + 5):
            w.setze(dx, y, 0, w.b("spruce_log", axis="y"))
    for x in range(-int(rs) - 1, int(rs) + 2):
        w.setze(x, H + 5, 0, w.b("spruce_log", axis="x"))
    kette(w, 0, H - 1, H + 4, 0)
    w.setze(0, H - 2, 0, w.b("lantern", hanging=True, waterlogged=False))
    haus(w, int(rs) + 6, -int(rs) - 3, 5, 4, hoehe(w, int(rs) + 6, -int(rs) - 3, H + 4) + 1,
         M(w, [("stone_bricks", 2), ("cobblestone", 1)]), holz="spruce", H=3, dach=("deepslate_tile",),
         tuer_s="west", schorn=False)
    return w


def wachkaserne(seed, g=2):
    """Wachkaserne: ein ummauerter Kasernenhof mit zwei Mannschaftshäusern, Torbau mit Flaggen, Übungspuppen aus
    Heu, Zielscheiben, Waffengestellen und einem Brunnen in der Mitte."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wiese(w, R + 1, huegel=0.2)
    st = kmauer(w)
    A = int(R * 0.72)
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            if max(abs(x), abs(z)) == A:
                tor = z == A and abs(x) <= 1
                for y in range(1, 5):
                    if not (tor and y < 4):
                        w.setze(x, y, z, st(x, y, z))
                if (x + z) % 2 == 0:
                    w.setze(x, 5, z, st(x, 5, z))
            elif max(abs(x), abs(z)) < A:
                w.setze(x, 0, z, w.b("gravel") if (x * 7 + z * 3) % 5 else w.b("coarse_dirt"))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
    for sx in (-1, 1):
        for y in range(1, 8):
            for dx in (0, 1):
                for dz in (0, 1):
                    w.setze(sx * 2 + dx * sx, y, A + dz, st(0, y, 0))
        fahne(w, sx * 3, 8, A, ("blue_wool", "white_wool"))
    wand = M(w, [("stone_bricks", 2), ("spruce_planks", 1)])
    haus(w, 0, -A + 3, 2 * A - 4, 5, 1, wand, holz="spruce", H=4, dach=("deepslate_tile", "cobbled_deepslate"),
         tuer_s="south")
    haus(w, -A + 3, 1, 5, int(A * 0.9), 1, wand, holz="spruce", H=3, dach=("deepslate_tile", "cobbled_deepslate"),
         tuer_s="east", schorn=False)
    for k in range(int(2 + s)):
        x, z = A - 3, -2 + k * 3
        w.setze(x, 1, z, w.b("spruce_fence"))
        w.setze(x, 2, z, w.b("hay_block", axis="y"))
        w.setze(x, 3, z, w.b("carved_pumpkin", facing="west"))
    for k in range(2):
        w.setze(2 + k * 2, 1, A - 2, w.b("target", power=0))
        w.setze(2 + k * 2, 2, A - 2, w.b("target", power=0))
    for z in range(-1, 2):
        w.setze(-2, 1, z + 4, w.b("spruce_fence"))
        w.setze(-2, 2, z + 4, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for x in range(-1, 2):
        for z in range(-1, 2):
            if abs(x) + abs(z) > 0:
                w.setze(x + 2, 1, z, w.b("stone_bricks"))
            else:
                w.setze(x + 2, 0, z, w.b("water", level=0))
                w.bloecke.pop((x + 2, 1, z), None)
    for dx in (-1, 1):
        w.setze(2 + dx, 2, 0, w.b("spruce_fence"))
        w.setze(2 + dx, 3, 0, w.b("spruce_fence"))
    for x in range(1, 4):
        w.setze(x, 4, 0, w.b("spruce_slab", type="bottom", waterlogged=False))
    figur(w, 0.32 * s + 0.25, waechter(w), (-2, -1, -2), (2, 7, 2), pos=(0, 1, A - 4), winkel=0.3)
    figur(w, 0.32 * s + 0.25, waechter(w, "light_blue_wool"), (-2, -1, -2), (2, 7, 2), pos=(A - 5, 1, 1),
          winkel=-1.2)
    return w


def kanalverlies(seed, g=2):
    """Kanalverlies: ein gemauerter Kanal schneidet sich durch einen gepflasterten Platz; in seine Seitenwände sind
    vergitterte Nischen gebaut, deren Bodengitter von oben sichtbar sind, Bogenbrücken queren das Wasser,
    ein kleiner Kahn liegt am Laufsteg."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 3)
    st = kmauer(w)
    pfl = M(w, [("cobblestone", 3), ("stone_bricks", 2), ("andesite", 1), ("mossy_cobblestone", 1)])
    wc = int(2 + s * 0.6)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            for y in range(-5, 2):
                w.setze(x, y, z, pfl(x, y, z) if y == 1 else st(x, y, z))
            if abs(z) <= wc:
                for y in range(-3, 2):
                    w.bloecke.pop((x, y, z), None)
                w.setze(x, -3, z, w.b("water", level=0))
                w.setze(x, -4, z, w.b("water", level=0))
            elif abs(z) == wc + 1:
                for y in range(-2, 2):
                    w.bloecke.pop((x, y, z), None)
                w.setze(x, -3, z, w.b("polished_andesite"))
    for sz in (-1, 1):
        for x in range(-R + 4, R - 3, 4):
            if math.hypot(x, sz * (wc + 4)) > R - 1:
                continue
            for dx in (-1, 0, 1):
                for dz in range(2, 5):
                    z = sz * (wc + dz)
                    for y in range(-2, 1):
                        if dz == 2:
                            w.setze(x + dx, y, z, gitter(w) if dx != 0 or y > -1 else w.b(
                                "iron_door", facing="north" if sz < 0 else "south", half="lower", hinge="left",
                                open=False, powered=False) if y == -2 else gitter(w))
                        else:
                            w.bloecke.pop((x + dx, y, z), None)
                    w.setze(x + dx, -3, z, w.b("cobblestone"))
                    if dz >= 3:
                        w.setze(x + dx, 1, z, gitter(w))
            w.setze(x, -1, sz * (wc + 1), w.b("wall_torch", facing="north" if sz > 0 else "south"))
            w.setze(x, -2, sz * (wc + 4), w.b("hay_block", axis="y"))
    for x in range(-R + 2, R - 1, 9):
        for z in range(-wc - 1, wc + 2):
            yb = 1 - (1 if abs(z) < wc - 0 else 0)
            for dx in (-1, 0, 1):
                w.setze(x + dx, 1, z, w.b("stone_bricks"))
                if abs(z) <= wc - 1:
                    w.setze(x + dx, 0, z, w.b("stone_brick_stairs", facing="north" if z > 0 else "south",
                                              half="top", shape="straight", waterlogged=False)) if abs(z) == wc - 1 \
                        else None
            _ = yb
        for z in (-wc - 1, wc + 1):
            w.setze(x - 1, 2, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                     west="none", waterlogged=False))
            w.setze(x + 1, 2, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                     west="none", waterlogged=False))
    bx = int(R * 0.3)
    for dx in range(-2, 3):
        w.setze(bx + dx, -2, wc - 1, w.b("spruce_slab", type="bottom", waterlogged=True))
    w.setze(bx - 2, -2, wc - 1, w.b("spruce_stairs", facing="east", half="bottom", shape="straight",
                                    waterlogged=True))
    w.setze(bx + 2, -2, wc - 1, w.b("spruce_stairs", facing="west", half="bottom", shape="straight",
                                    waterlogged=True))
    for x in range(-R, R + 1, 6):
        if math.hypot(x, wc + 6) < R - 1:
            laterne(w, x, 4, wc + 6, kette=0)
            w.setze(x, 2, wc + 6, w.b("dark_oak_fence"))
            w.setze(x, 3, wc + 6, w.b("dark_oak_fence"))
    figur(w, 0.3 * s + 0.25, waechter(w), (-2, -1, -2), (2, 7, 2), pos=(-int(R * 0.3), -2, wc + 1), winkel=1.5)
    return w


def eiskerker(seed, g=2):
    """Eiskerker: in eine Gletscherwand aus Packeis sind zwei Reihen vergitterter Zellen gehauen, ein vereister
    Holzsteg mit Leitern verbindet die obere Reihe, davor Schnee, Fichten, ein Kohlebecken und Wächter in Pelz."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 5)
    H = int(12 * s + 8)
    eis = M(w, [("packed_ice", 4), ("blue_ice", 1), ("snow_block", 1)])
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 2 * rn(x, 0, z):
                continue
            if z <= 0:
                h = int(H * (0.8 + 0.2 * (1 - (d / (R + 2)) ** 4)) + rn(x, 3, z) * 3)
            else:
                h = int(rn(x, 3, z) * 1.3)
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("snow_block") if y == h else eis(x, y, z) if h > 2 else w.b("dirt"))
            if h <= 1:
                w.setze(x, h, z, w.b("grass_block", snowy=True))
                w.setze(x, h + 1, z, w.b("snow", layers=1 + int(rn(x, 9, z) * 2)))
    st = M(w, [("deepslate_bricks", 2), ("polished_deepslate", 1), ("cracked_deepslate_bricks", 1)])
    L = int(R * 0.6)
    for reihe, y0 in enumerate((1, 6)):
        for x in range(-L + 2, L - 1, 4):
            zelle(w, x, 0, 3, 4, y0, 3, offen="south", st=st)
    for x in range(-L, L + 1):
        w.setze(x, 5, 1, w.b("spruce_planks"))
        w.setze(x, 6, 2, zaun_(w))
    for x in (-L, L):
        for y in range(1, 6):
            w.setze(x, y, 1, w.b("ladder", facing="south", waterlogged=False)) if False else \
                w.setze(x, y, 2, w.b("spruce_log", axis="y"))
    for y in range(1, 6):
        w.setze(L - 1, y, 2, w.b("ladder", facing="west", waterlogged=False)) if False else None
    for y in range(1, 5):
        w.setze(L + 1, y, 1, w.b("ladder", facing="east", waterlogged=False)) if False else None
    for x in range(-L, L + 1, 3):
        w.setze(x, 4, 1, w.b("spruce_log", axis="y"))
        w.setze(x, 3, 1, w.b("spruce_log", axis="y"))
        w.setze(x, 2, 1, w.b("spruce_log", axis="y")) if x % 6 == 0 else None
    w.setze(0, 1, 5, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        w.setze(dx, 1, 5 + dz, w.b("cobblestone_slab", type="bottom", waterlogged=False))
    for k in range(3 + g):
        a = 0.6 + k * 0.5
        x, z = round(math.cos(a) * R * 0.75), round(R * 0.55 + math.sin(a * 3) * 2)
        if math.hypot(x, z) < R - 1:
            fichte(w, x, 1, z, seed + k, 6 + 3 * s, schnee=True)
    figur(w, 0.32 * s + 0.25, waechter(w, "brown_wool"), (-2, -1, -2), (2, 7, 2), pos=(3, 1, 6), winkel=0.8)
    return w


def glutverlies(seed, g=2):
    """Glutverlies: eine Insel aus Schwarzstein in einem Lavasee, auf der ein Zellengeviert um einen Hof mit Seelen-
    feuer steht; eine Kettenbrücke führt hinüber, Basaltsäulen mit Seelenlaternen ragen aus der Glut."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 2 * rn(x, 0, z):
                continue
            for y in range(-3, 0):
                w.setze(x, y, z, w.b("basalt", axis="y") if y < -1 else w.b("magma_block"))
            if d > R - 1.5:
                w.setze(x, 0, z, w.b("blackstone"))
                w.setze(x, 1, z, w.b("basalt", axis="y") if rn(x, 4, z) < 0.5 else w.b("blackstone"))
            else:
                w.setze(x, 0, z, w.b("lava", level=0))
    st = M(w, [("polished_blackstone_bricks", 3), ("cracked_polished_blackstone_bricks", 1), ("blackstone", 1)])
    A = int(R * 0.45)
    for x in range(-A - 1, A + 2):
        for z in range(-A - 1, A + 2):
            w.setze(x, 0, z, st(x, 0, z))
    for x in range(-A + 1, A, 4):
        zelle(w, x, -A + 3, 3, 4, 1, 3, offen="south", st=st)
        zelle(w, x, A - 3, 3, 4, 1, 3, offen="north", st=st)
    for x in range(-1, 2):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("polished_blackstone") if abs(x) + abs(z) else w.b("soul_soil"))
    w.setze(0, 2, 0, w.b("soul_campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for x in range(A + 1, int(R) + 1):
        w.setze(x, 1, 0, w.b("polished_blackstone_slab", type="bottom", waterlogged=False))
        if x % 2 == 0:
            for dz in (-1, 1):
                w.setze(x, 1, dz, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                                      west="none", waterlogged=False))
                w.setze(x, 2, dz, w.b("chain", axis="y", waterlogged=False))
    rng = w.rng
    for k in range(int(4 + 3 * s)):
        a = rng.random() * 6.28
        r = A + 3 + rng.random() * (R - A - 5)
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        if abs(z) < 2 and x > 0:
            continue
        hh = int(3 + rng.random() * 5 * s)
        for y in range(0, hh):
            for dx, dz in ((0, 0), (1, 0), (0, 1)):
                w.setze(x + dx, y, z + dz, w.b("basalt", axis="y"))
        w.setze(x, hh, z, w.b("soul_lantern", hanging=False, waterlogged=False))
    return w


def kasematten(seed, g=2):
    """Kasematten: eine dicke, winkelförmige Festungsmauer mit Eckturm, in deren Fuß vergitterte Gewölbezellen
    auf Höhe des Wassergrabens liegen; oben Wehrgang mit Zinnen, dahinter ein Hof."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    wiese(w, R + 1, huegel=0.2)
    st = kmauer(w)
    zw = int(R * 0.15)
    Hw = int(6 * s + 6)
    xe = int(R * 0.45)
    D = 4

    def mauerzug(x0, x1, z0, z1):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if math.hypot(x, z) > R:
                    continue
                for y in range(-1, Hw + 1):
                    w.setze(x, y, z, st(x, y, z))

    mauerzug(-R, xe, zw - D + 1, zw)
    mauerzug(xe - D + 1, xe, -R, zw)
    for x in range(-R, xe + 1):
        if math.hypot(x, zw) > R:
            continue
        if (x + 100) % 2 == 0:
            w.setze(x, Hw + 1, zw, st(x, Hw + 1, zw))
        if (x + 100) % 4 == 1 and x < xe - D:
            for y in (1, 2, 3):
                for z in range(zw - D + 2, zw):
                    w.bloecke.pop((x, y, z), None)
                    w.bloecke.pop((x + 1, y, z), None)
            w.setze(x, 2, zw, gitter(w))
            w.setze(x + 1, 2, zw, gitter(w))
            w.setze(x, 1, zw - D + 2, w.b("hay_block", axis="y"))
    for z in range(-R, zw + 1):
        if (z + 100) % 2 == 0 and math.hypot(xe, z) <= R:
            w.setze(xe, Hw + 1, z, st(xe, Hw + 1, z))
    for x in range(-R - 2, R + 3):
        for z in range(zw + 1, zw + 5):
            if math.hypot(x, z) <= R + 1 and x < xe + 5:
                for y in range(-1, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.bloecke.pop((x, 1, z), None)
                w.setze(x, -2, z, w.b("gravel"))
    for z in range(-R, zw + 5):
        for x in range(xe + 1, xe + 5):
            if math.hypot(x, z) <= R + 1:
                for y in range(-1, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.bloecke.pop((x, 1, z), None)
                w.setze(x, -2, z, w.b("gravel"))
    rt = int(2 + s)
    rundturm_einfach(w, xe - 1, zw - 1, 1, rt + 1, Hw + 4, st, "schiefer")
    for x in range(-R, xe - D + 1):
        for z in range(-R, zw - D + 1):
            if math.hypot(x, z) < R and w.frei(x, 1, z):
                w.setze(x, 0, z, w.b("gravel") if (x + z) % 3 else w.b("coarse_dirt"))
    figur(w, 0.32 * s + 0.25, waechter(w), (-2, -1, -2), (2, 7, 2), pos=(-int(R * 0.3), Hw + 1, zw - 2),
          winkel=0.0)
    return w


def schluchtkaefige(seed, g=2):
    """Schluchtkäfige: eine schwankende Hängebrücke spannt sich über eine tiefe Schlucht mit Wildwasser; an ihr hängen
    an langen Ketten Käfige über dem Abgrund, an der Kante eine Seilwinde und eine Wachhütte."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    H = int(12 * s + 8)
    f = M(w, [("stone", 3), ("andesite", 2), ("granite", 0.6), ("tuff", 1)])
    sp = 3 + s
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            mz = math.sin(x / 5) * 1.5
            if abs(z - mz) < sp:
                w.setze(x, -3, z, w.b("water", level=0))
                w.setze(x, -4, z, w.b("gravel"))
                continue
            Hz = H if z < mz else int(H * 0.55)
            hh = Hz + int(rn(x, 3, z) * 2)
            for y in range(-4, hh + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == hh else f(x, y, z))
    yb0, yb1 = H, int(H * 0.55)
    z0, z1 = -int(sp) - 3, int(sp) + 3
    for z in range(z0, z1 + 1):
        t = (z - z0) / (z1 - z0)
        y = round(yb0 + (yb1 - yb0) * t - math.sin(t * math.pi) * 1.5) + 1
        for x in (-1, 0, 1):
            w.setze(x, y, z, w.b("spruce_slab", type="bottom", waterlogged=False), False)
        for x in (-2, 2):
            w.setze(x, y + 1, z, w.b("spruce_fence"), False)
        if z % 3 == 0 and abs(z) < sp:
            hk = int(3 + (abs(z) % 2) * 2 + s * 2)
            kx = 3 if z % 2 else -3
            for xx in range(min(0, kx), max(0, kx) + 1):
                w.setze(xx, y, z, w.b("spruce_slab", type="bottom", waterlogged=False), False)
            kette(w, kx, y - hk + 3, y, z)
            kaefig(w, kx, y - hk - 1, z, holz="spruce")
    for sz, yy in ((z0 - 1, yb0 + 1), (z1 + 1, yb1 + 1)):
        for x in (-2, 2):
            for k in range(3):
                w.setze(x, yy + k, sz, w.b("spruce_log", axis="y"))
    w.setze(-4, yb0 + 1, z0 - 2, w.b("spruce_log", axis="x"))
    w.setze(-3, yb0 + 1, z0 - 2, w.b("spruce_log", axis="x"))
    haus(w, 5, z0 - 5, 5, 4, hoehe(w, 5, z0 - 5, H + 4) + 1, M(w, [("spruce_planks", 2), ("stripped_spruce_log", 1)]),
         holz="spruce", H=3, dach=("spruce", "dark_oak"), tuer_s="west", schorn=False)
    return w


def asservatenkammer(seed, g=1):
    """Asservatenkammer: ein festes, zweistöckiges Steinhaus mit vergitterten Fenstern und Eisentür, in dessen Hof
    versiegelte Truhen, Kisten und Fässer gestapelt sind, ein Wagen mit Beschlagnahmtem und ein Wächter."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.2)
    wand = M(w, [("stone_bricks", 3), ("polished_andesite", 1), ("cracked_stone_bricks", 0.5)])
    B, T = int(5 * s + 5) | 1, int(3 * s + 5)
    haus(w, 0, -int(R * 0.25), B, T, 1, wand, holz="dark_oak", H=7, dach=("deepslate_tile", "cobbled_deepslate"),
         tuer_s="south", schorn=False)
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if "glass_pane" in n:
            w.setze(x, y, z, gitter(w))
        elif n.endswith("_door") and "dark_oak" in n:
            st = w.P.zustand(b) if hasattr(w.P, "zustand") else None
            _ = st
    zt = -int(R * 0.25) + T // 2 + 1
    for x in range(-int(R * 0.7), int(R * 0.7) + 1):
        for z in (int(R * 0.65),):
            if math.hypot(x, z) < R:
                w.setze(x, 1, z, w.b("dark_oak_fence")) if abs(x) > 1 else None
    rng = w.rng
    for k in range(int(6 + 4 * s)):
        x = int((rng.random() - 0.5) * R * 1.2)
        z = zt + 2 + int(rng.random() * R * 0.3)
        if abs(x) < 2:
            continue
        hh = int(1 + rng.random() * 2)
        for y in range(1, 1 + hh):
            w.setze(x, y, z, w.b(["barrel", "chest", "spruce_planks"][(k + y) % 3],
                                 **({"facing": "up", "open": False} if (k + y) % 3 == 0 else
                                    {"facing": "south", "type": "single", "waterlogged": False} if (k + y) % 3 == 1
                                    else {})))
    cx, cz = int(R * 0.45), zt + 3
    for x in range(cx - 1, cx + 2):
        for z in range(cz - 2, cz + 2):
            w.setze(x, 2, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    for z in (cz - 2, cz + 1):
        for x in (cx - 2, cx + 2):
            w.setze(x, 1, z, w.b("dark_oak_log", axis="x"))
    w.setze(cx, 3, cz, w.b("chest", facing="west", type="single", waterlogged=False))
    w.setze(cx, 3, cz - 1, w.b("barrel", facing="up", open=False))
    figur(w, 0.32 * s + 0.25, waechter(w), (-2, -1, -2), (2, 7, 2), pos=(2, 1, zt + 1), winkel=0.0)
    return w


def fallgatter_torhaus(seed, g=2):
    """Fallgatter-Torhaus: ein wuchtiges Torhaus zwischen zwei Rundtürmen mit halb herabgelassenem Fallgatter,
    Pechnasen, Zinnen, abgehenden Mauerstücken und einer heruntergelassenen Zugbrücke über den Graben."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wiese(w, R + 1, huegel=0.2)
    st = kmauer(w)
    gw = int(1 + s)
    rt = int(2 + s * 0.8)
    Ht = int(7 * s + 6)
    T = 6
    for x in range(-gw - rt, gw + rt + 1):
        for z in range(-T // 2, T // 2 + 1):
            for y in range(-1, Ht + 1):
                if abs(x) <= gw and y in range(1, 1 + int(3 + s)) and abs(x) < gw + 1:
                    if abs(x) < gw or y < int(2 + s):
                        w.bloecke.pop((x, y, z), None)
                        continue
                w.setze(x, y, z, st(x, y, z))
        if (x + 100) % 2 == 0:
            for z in (-T // 2, T // 2):
                w.setze(x, Ht + 1, z, st(x, Ht + 1, z))
    for x in range(-gw + 1, gw):
        w.setze(x, 0, 0, w.b("cobblestone"))
    for x in range(-gw + 1, gw):
        for y in range(int(2 + s) - 1, int(3 + s) + 1):
            w.setze(x, y, T // 2 - 1, w.b("iron_bars", north=False, south=False, east=True, west=True,
                                           waterlogged=False))
    for x in range(-gw - 1, gw + 2):
        w.setze(x, Ht - 1, T // 2 + 1, w.b("stone_brick_slab", type="top", waterlogged=False))
        w.setze(x, Ht, T // 2 + 1, st(x, Ht, T // 2 + 1) if x % 2 else w.b("stone_brick_wall", up=True, north="none",
                                                                          south="none", east="none", west="none",
                                                                          waterlogged=False))
    for sx in (-1, 1):
        rundturm_einfach(w, sx * (gw + rt + 1), 0, 1, rt, Ht + 4, st, "schiefer")
        for x in range(sx * (gw + 2 * rt + 2), sx * R, sx):
            for z in range(-1, 2):
                if math.hypot(x, z) < R:
                    for y in range(1, Ht - 2):
                        w.setze(x, y, z, st(x, y, z))
                    if (x + z) % 2 == 0:
                        w.setze(x, Ht - 2, z, st(x, Ht - 2, z))
    for x in range(-R - 2, R + 3):
        for z in range(T // 2 + 2, T // 2 + 6):
            if math.hypot(x, z) <= R + 1:
                for y in range(-1, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.bloecke.pop((x, 1, z), None)
    for z in range(T // 2 + 1, T // 2 + 7):
        for x in range(-gw + 1, gw):
            w.setze(x, 1, z, w.b("spruce_planks"))
    for sx in (-gw, gw):
        for k in range(1, Ht - 3):
            t = k / (Ht - 3)
            w.setze(sx, round(1 + (Ht - 3) * (1 - t)), round(T // 2 + 1 + 5 * t), w.b("chain", axis="y",
                                                                                     waterlogged=False), False)
    fahne(w, 0, Ht + 1, 0, ("red_wool", "yellow_wool"))
    return w


def gefaengniskueche(seed, g=1):
    """Gefängnisküche: ein steinernes Küchenhaus mit mächtigem Schornstein, davor ein überdachter Speisehof mit
    langen Tischen und Bänken, dampfende Kessel über Feuern, Holzstapel, Fässer und ein Gemüsebeet."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.2)
    B, T = int(4 * s + 5) | 1, int(2 * s + 5)
    zh = -int(R * 0.45)
    haus(w, 0, zh, B, T, 1, M(w, [("cobblestone", 2), ("stone_bricks", 2)]), holz="spruce", H=4,
         dach=("spruce", "dark_oak"), tuer_s="south")
    z0 = zh + T // 2 + 2
    L = int(B * 0.9)
    for x in range(-L // 2, L // 2 + 1):
        for z in range(z0, z0 + 6):
            w.setze(x, 0, z, w.b("spruce_planks"))
            w.setze(x, 4, z, w.b("spruce_slab", type="bottom", waterlogged=False))
        for z in (z0, z0 + 5):
            if (x + L // 2) % 3 == 0:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
    for z in (z0 + 2, z0 + 3):
        for x in range(-L // 2 + 1, L // 2):
            if z == z0 + 2:
                w.setze(x, 1, z, w.b("spruce_fence"))
                w.setze(x, 2, z, w.b("spruce_pressure_plate", powered=False)) if False else None
            w.setze(x, 1, z0 + 2, w.b("spruce_slab", type="top", waterlogged=False)) if False else None
    for x in range(-L // 2 + 1, L // 2):
        w.setze(x, 1, z0 + 2, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x, 1, z0 + 3, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x, 1, z0 + 1, w.b("spruce_stairs", facing="south", half="bottom", shape="straight",
                                  waterlogged=False))
        w.setze(x, 1, z0 + 4, w.b("spruce_stairs", facing="north", half="bottom", shape="straight",
                                  waterlogged=False))
    for k, x in enumerate((-int(R * 0.6), -int(R * 0.6) + 3)):
        z = z0 + 8
        w.setze(x, 1, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
        w.setze(x, 2, z, w.b("water_cauldron", level=3))
        for dx in (-1, 1):
            w.setze(x + dx, 1, z, w.b("cobblestone_wall", up=True, north="none", south="none", east="none",
                                      west="none", waterlogged=False))
    for y in range(1, 3):
        for z in range(zh - 1, zh + 3):
            w.setze(B // 2 + 2, y, z, w.b("spruce_log", axis="z"))
    for k in range(3):
        w.setze(-B // 2 - 2, 1, zh + k, w.b("barrel", facing="up", open=False))
    for x in range(int(R * 0.35), int(R * 0.35) + 4):
        for z in range(z0 + 7, z0 + 10):
            if z == z0 + 8:
                w.setze(x, 0, z, w.b("water", level=0))
                continue
            w.setze(x, 0, z, w.b("farmland", moisture=7))
            w.setze(x, 1, z, w.b(["potatoes", "carrots", "beetroots"][(x + z) % 3], age=7 if (x + z) % 3 < 2 else 3))
    figur(w, 0.3 * s + 0.25, mensch(w, "white_wool"), (-2, -1, -2), (2, 6, 2), pos=(-int(R * 0.6) + 1, 1, z0 + 9),
          winkel=1.0)
    return w


def leuchtwachturm(seed, g=2):
    """Leuchtwachturm: ein hoher Holzturm auf vier Stämmen mit Kreuzverstrebungen, Leitern und Zwischenböden, oben
    eine Kanzel mit Glocke und einem großen Leuchtfeuer hinter Glas, umgeben von einer Palisade mit Toren."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, huegel=0.25)
    Ht = int(10 * s + 8)
    a = 2 + int(s * 0.5)
    for dx in (-a, a):
        for dz in (-a, a):
            for y in range(1, Ht + 1):
                w.setze(dx, y, dz, w.b("spruce_log", axis="y"))
    for y0 in range(4, Ht, 5):
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                if abs(x) == a or abs(z) == a:
                    w.setze(x, y0, z, w.b("stripped_spruce_log", axis="x" if abs(z) == a else "z"))
        for k in range(1, 2 * a):
            t = k / (2 * a)
            yy = round(y0 - 4 + 4 * t)
            for sx in (-a, a):
                w.setze(sx, yy, -a + k, w.b("spruce_fence"), False)
                w.setze(-a + k, yy, sx, w.b("spruce_fence"), False)
    for y in range(1, Ht + 1):
        w.setze(0, y, a, w.b("ladder", facing="south", waterlogged=False), False)
        w.setze(0, y, a - 1, w.b("spruce_planks"))
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            w.setze(x, Ht + 1, z, w.b("spruce_planks"))
            if abs(x) == a + 1 or abs(z) == a + 1:
                w.setze(x, Ht + 2, z, zaun_(w))
            w.setze(x, Ht + 5, z, w.b("spruce_planks"))
    for dx in (-a - 1, a + 1):
        for dz in (-a - 1, a + 1):
            for y in range(Ht + 2, Ht + 5):
                w.setze(dx, y, dz, w.b("spruce_log", axis="y"))
    kegeldach(w, 0, 0, Ht + 6, a + 2, Dachmat(w, ["spruce", "dark_oak"]), eckig=True)
    for x in (-1, 0, 1):
        for z in (-1, 0, 1):
            for y in (Ht + 2, Ht + 3):
                w.setze(x, y, z, w.b("glowstone") if (x, z) == (0, 0) else w.b("yellow_stained_glass"))
    w.setze(a, Ht + 4, 0, w.b("bell", attachment="ceiling", facing="east", powered=False))
    rp = R * 0.82
    for k in range(int(2 * math.pi * rp)):
        t = k / (2 * math.pi * rp) * 2 * math.pi
        x, z = round(math.cos(t) * rp), round(math.sin(t) * rp)
        if abs(x) <= 1 and z > 0:
            continue
        y0 = zellen.get((x, z), 0) + 1
        for y in range(y0, y0 + 3 + (k % 2)):
            w.setze(x, y, z, w.b("spruce_log", axis="y"))
        w.setze(x, y0 + 3 + (k % 2), z, w.b("spruce_fence"))
    haus(w, -int(R * 0.45), int(R * 0.3), 5, 4, 1, M(w, [("spruce_planks", 2), ("stripped_spruce_log", 1)]),
         holz="spruce", H=3, dach=("spruce", "dark_oak"), tuer_s="east", schorn=False)
    figur(w, 0.3 * s + 0.25, waechter(w), (-2, -1, -2), (2, 7, 2), pos=(-a, Ht + 2, 0), winkel=0.0)
    return w


def kerkerkapelle(seed, g=1):
    """Kerkerkapelle: eine kleine, strenge Steinkapelle innerhalb einer Gefängnismauer, mit vergitterten Spitzfenstern,
    Rosette über dem Portal, Glockentürmchen, Bänken im Hof und einem Brunnen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R + 1, huegel=0.15)
    st = kmauer(w)
    B, T = int(3 * s + 5) | 1, int(5 * s + 7)
    first = haus(w, 0, -int(R * 0.2), B, T, 1, st, holz="dark_oak", H=5, dach=("deepslate_tile", "cobbled_deepslate"),
                 tuer_s="south", schorn=False, steil=2)
    for (x, y, z), b in list(w.bloecke.items()):
        if "glass_pane" in w.P.name(b):
            w.setze(x, y, z, gitter(w))
    zf = -int(R * 0.2) + T // 2 - (T % 2 == 0)
    zf = max(z for (x, y, z) in w.bloecke if x == 0 and y == 3 and abs(z - zf) < 3)
    for dx, dy in ((0, 7), (-1, 7), (1, 7), (0, 8), (0, 6)):
        w.setze(dx, dy, zf, w.b("purple_stained_glass") if (dx, dy) == (0, 7) else w.b("red_stained_glass"))
    zt = zf + 1
    for x in (-1, 0, 1):
        for z in (zt, zt + 1):
            for y in range(1, first + 2):
                if y > first - 2 and x == 0 and z == zt:
                    w.bloecke.pop((x, y, z), None)
                else:
                    w.setze(x, y, z, st(x, y, z))
    w.bloecke.pop((0, first - 1, zt), None)
    w.setze(0, first, zt, w.b("bell", attachment="ceiling", facing="south", powered=False))
    for x in (-1, 0, 1):
        for z in (zt, zt + 1):
            w.setze(x, first + 2, z, w.b("deepslate_tile_slab", type="bottom", waterlogged=False))
    w.setze(0, first + 3, zt, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for y in (1, 2):
        w.bloecke.pop((0, y, zt), None)
        w.bloecke.pop((0, y, zt + 1), None)
    A = int(R * 0.8)
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            if max(abs(x), abs(z)) == A and math.hypot(x, z) < R + 1.5:
                if z == A and abs(x) <= 1:
                    continue
                for y in range(1, 4):
                    w.setze(x, y, z, st(x, y, z))
    for k, x in enumerate((-A + 2, A - 2)):
        for z in range(zt + 2, zt + 5):
            w.setze(x, 1, z, w.b("dark_oak_stairs", facing="east" if k == 0 else "west", half="bottom",
                                 shape="straight", waterlogged=False))
    return w


def versunkenes_verlies(seed, g=2):
    """Versunkenes Verlies: auf dem Meeresgrund liegen die Reste eines Kerkers – halb eingestürzte Zellenreihen mit
    verrosteten Gittern, ein umgestürzter Wachturm, Ketten, Truhen, Korallen, Seetang und Meereslaternen."""
    from elemente import korallenbewuchs
    from erw_unterwasser import grund
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    grund(w, R, dichte=1.0, felsen=int(3 + 2 * s))
    st = M(w, [("mossy_stone_bricks", 3), ("cracked_stone_bricks", 2), ("stone_bricks", 1), ("prismarine", 0.5)])
    rng = w.rng
    L = int(R * 0.55)
    for reihe, (zc, off) in enumerate(((-int(R * 0.3), "south"), (int(R * 0.25), "north"))):
        for x in range(-L + 2, L - 1, 4):
            zelle(w, x, zc, 3, 4, 1, 4, offen=off, st=st, nass=True)
    for (x, y, z), b in list(w.bloecke.items()):
        if y >= 3 and rng.random() < 0.08 + 0.07 * y:
            n = w.P.name(b)
            if any(k in n for k in ("stone_brick", "iron_bars", "prismarine", "iron_door", "chain")):
                w.bloecke.pop((x, y, z), None)
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if "iron_door" in n:
            w.bloecke.pop((x, y, z), None)
    tx, tz = int(R * 0.5), -int(R * 0.05)
    for k in range(int(8 * s + 4)):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dy) + abs(dz) == 2:
                    continue
                w.setze(tx - k, 1 + dy + 1, tz + dz, st(tx - k, dy, dz))
    w.setze(tx - int(8 * s + 4), 2, tz, w.b("sea_lantern"))
    for k in range(int(3 + 2 * s)):
        x, z = int((rng.random() - 0.5) * R * 1.3), int((rng.random() - 0.5) * R * 0.4)
        y = hoehe(w, x, z, 12) + 1
        w.setze(x, y, z, w.b("chest", facing="south", type="single", waterlogged=True) if k % 2 else
                w.b("sea_lantern"))
    for k in range(int(4 * s)):
        x, z = int((rng.random() - 0.5) * R * 1.4), int((rng.random() - 0.5) * R * 1.4)
        y = hoehe(w, x, z, 12)
        for d in range(1, int(2 + rng.random() * 3)):
            w.setze(x, y + d, z, w.b("chain", axis="x" if d % 2 else "y", waterlogged=True), False)
    korallenbewuchs(w, 0.3)
    return w


def baumkerker(seed, g=2):
    """Baumkerker: eine uralte Rieseneiche, an deren weit ausladenden Ästen Holzkäfige an Ketten baumeln, eine
    Plattform mit Wachhütte umschließt den Stamm, ein Strickleiterweg führt hinauf."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wiese(w, R, huegel=0.3, art="wald")
    rng = w.rng
    H = 12 * s + 6
    enden = baum_aeste(w, 0, 0, H, 5 + g, 7 * s + 3, "dark_oak", 1.4 * s + 0.8, rng, steigung=0.15, start=0.6)
    for (x, y, z) in enden:
        laubball(w, x, y + 1.5, z, 2.5 * s + 1.5, arten=("dark_oak_leaves", "oak_leaves"))
    for (x, y, z) in enden[1:]:
        hx, hz = round(x * 1.05), round(z * 1.05)
        yb = int(y) - 1
        hk = int(5 + rng.random() * 3 * s)
        kette(w, hx, yb - hk + 3, yb, hz)
        kaefig(w, hx, yb - hk - 1, hz, holz="spruce")
    yp = int(H * 0.45)
    rp = 1.4 * s + 2.5
    for x in range(-int(rp) - 2, int(rp) + 3):
        for z in range(-int(rp) - 2, int(rp) + 3):
            d = math.hypot(x, z)
            if d <= rp + 1.5 and w.frei(x, yp, z):
                w.setze(x, yp, z, w.b("spruce_planks"))
                if d > rp + 0.6:
                    w.setze(x, yp + 1, z, zaun_(w))
    hx = int(rp) + 1
    for x in range(hx - 1, hx + 3):
        for z in range(-1, 2):
            for y in range(yp + 1, yp + 4):
                if x in (hx - 1, hx + 2) or abs(z) == 1:
                    w.setze(x, y, z, w.b("spruce_planks") if y < yp + 3 or (x + z) % 2 else w.b("spruce_fence"))
                else:
                    w.bloecke.pop((x, y, z), None)
            w.setze(x, yp + 4, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    for y in range(1, yp):
        w.setze(-int(rp) - 1, y, 0, w.b("ladder", facing="west", waterlogged=False), False) if False else \
            w.setze(-int(rp) - 1, y, 0, w.b("spruce_fence"), False)
    figur(w, 0.3 * s + 0.25, waechter(w, "green_wool"), (-2, -1, -2), (2, 7, 2), pos=(0, yp + 1, int(rp)),
          winkel=0.0)
    return w


KERKER3 = {
    "rundgefaengnis": ("Rundgefängnis", rundgefaengnis),
    "gefaengnisschiff": ("Gefängnisschiff", gefaengnisschiff),
    "klippengefaengnis": ("Klippengefängnis", klippengefaengnis),
    "brueckenzellen": ("Brückenzellen", brueckenzellen),
    "strafkolonie": ("Steinbruch-Strafkolonie", strafkolonie),
    "kaefigsaeule": ("Käfigsäule", kaefigsaeule),
    "zellenschacht": ("Zellenschacht", zellenschacht),
    "wachkaserne": ("Wachkaserne", wachkaserne),
    "kanalverlies": ("Kanalverlies", kanalverlies),
    "eiskerker": ("Eiskerker", eiskerker),
    "glutverlies": ("Glutverlies", glutverlies),
    "kasematten": ("Kasematten", kasematten),
    "schluchtkaefige": ("Schluchtkäfige", schluchtkaefige),
    "asservatenkammer": ("Asservatenkammer", asservatenkammer),
    "fallgatter_torhaus": ("Fallgatter-Torhaus", fallgatter_torhaus),
    "gefaengniskueche": ("Gefängnisküche", gefaengniskueche),
    "leuchtwachturm": ("Leuchtwachturm", leuchtwachturm),
    "kerkerkapelle": ("Kerkerkapelle", kerkerkapelle),
    "versunkenes_verlies": ("Versunkenes Verlies", versunkenes_verlies),
    "baumkerker": ("Baumkerker", baumkerker),
}

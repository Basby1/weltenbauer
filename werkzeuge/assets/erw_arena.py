"""Arena & Turnierplatz II – zwanzig weitere Bauten: Ringstechbahn, Bogenturnierwiese, Kraterarena, Schwebende Arena,
Gladiatorenschule, Hochlandspiele-Wiese, Heroldsstand mit Punktetafel, Turnierstallungen, Turnierschmiede, Erdtribüne
am Hang, Eisarena, Wüstenarena mit Sonnensegeln, Kletterturm-Wettkampf, Duellbrücke, Kampfrichter-Pavillon,
Waldlichtungs-Arena, Quintana-Platz, Regattastrecke, Ballspielplatz mit Steinringen und Seearena auf Pfählen."""

from __future__ import annotations

import math

import wald2
from arena import bannerreihe, ovaltribuene, sand, tribuene, waffenstaender, zelt, zf
from erw_basis import M, S, baumrand, figur, fichte, haus, hoehe, wiese
from erw_burgen import fahne
from erw_markt import mensch
from feinbau import Dachmat, kegeldach, laterne
from flora import _neu
from himmel import insel
from leuchtwald2 import kugel
from lib import Rauschen, einfuegen
from skulptur import ell, kap

FARBEN = ["red", "blue", "yellow", "green", "purple", "orange", "white", "black", "cyan", "lime"]


def pferd(w, decke="red_wool", fell="brown_terracotta", reiter=None, lanze=False):
    t = [(ell(0, 3.0, 0, 2.2, 1.0, 0.9), w.b(decke)), (ell(0, 3.4, 0, 2.0, 0.8, 0.75), w.b(fell)),
         (kap((1.7, 3.4, 0), (2.5, 4.9, 0), 0.5, 0.4), w.b(fell)), (ell(2.9, 4.8, 0, 0.9, 0.42, 0.38), w.b(fell)),
         (kap((-2.0, 3.6, 0), (-2.6, 1.6, 0), 0.25), w.b("black_wool"))]
    for sx in (-1.4, 1.4):
        for sz in (-0.5, 0.5):
            t.append((kap((sx, 2.6, sz), (sx, 0, sz), 0.3), w.b(fell)))
    if reiter:
        t += [(kap((0, 3.9, 0), (0, 5.6, 0), 0.6, 0.5), w.b(reiter)), (ell(0, 6.2, 0, 0.5, 0.55, 0.5),
                                                                       w.b("iron_block")),
              (kap((0, 4.2, 0.6), (0.6, 2.8, 1.0), 0.28), w.b(reiter)),
              (kap((0, 4.2, -0.6), (0.6, 2.8, -1.0), 0.28), w.b(reiter))]
        if lanze:
            t += [(kap((-0.5, 5.0, 0.8), (4.8, 5.6, 0.8), 0.2), w.b("spruce_planks")),
                  (ell(0.6, 5.1, 0.8, 0.3, 0.6, 0.6), w.b("white_wool"))]
    return t


def leute(w, s, punkte, seed=0):
    for k, (x, y, z, wnk) in enumerate(punkte):
        figur(w, 0.3 * s + 0.22, mensch(w, f"{FARBEN[(k + seed) % len(FARBEN)]}_wool",
                                        haar=["brown_wool", "black_wool", "yellow_wool"][k % 3]),
              (-2, -1, -2), (2, 6, 2), pos=(x, y, z), winkel=wnk)


def galgenrahmen(w, x, z, H, breite=3, holz="spruce", richtung="x"):
    for d in (-breite, breite):
        px, pz = (x + d, z) if richtung == "x" else (x, z + d)
        for y in range(1, H + 1):
            w.setze(px, y, pz, w.b(f"{holz}_log", axis="y"))
    for d in range(-breite, breite + 1):
        px, pz = (x + d, z) if richtung == "x" else (x, z + d)
        w.setze(px, H + 1, pz, w.b(f"{holz}_log", axis="x" if richtung == "x" else "z"))


def pfostenwand(w, pts, H, holz="spruce", farben=("red", "white")):
    for k, (x, z) in enumerate(pts):
        for y in range(1, H + 1):
            w.setze(x, y, z, w.b(f"{holz}_planks") if y < H else w.b(f"{farben[k // 2 % 2]}_wool"))


# ============================================================================ Bauten

def ringstechbahn(seed, g=2):
    """Ringstechbahn: eine lange Sandbahn, über der an drei Holzgalgen kleine Ringe an Ketten hängen, die ein
    galoppierender Ritter mit der Lanze aufspießen muss; Schranken, eine Tribüne und Zelte an den Enden."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    wiese(w, R, huegel=0.15)
    L = int(R * 0.85)
    sand(w, -L, -2, L, 2)
    for x in range(-L, L + 1):
        for z in (-3, 3):
            w.setze(x, 1, z, zf(w, "spruce", east=True, west=True))
            if x % 4 == 0:
                w.setze(x, 2, z, w.b(f"{FARBEN[(x // 4) % 2]}_wool"))
    for k in range(3):
        x = -L // 2 + k * L // 2
        galgenrahmen(w, x, 0, 5, breite=3, richtung="z")
        w.setze(x, 5, 0, w.b("chain", axis="y", waterlogged=False))
        w.setze(x, 4, 0, w.b("iron_bars", north=True, south=True, east=False, west=False, waterlogged=False))
    tribuene(w, -L // 2, L // 2, -6, stufen=int(2 + s), richtung=1, farben=("blue", "white"))
    for sx in (-1, 1):
        zelt(w, sx * (L - 1), int(R * 0.5), int(1.5 + s), farben=("red", "white") if sx < 0 else ("blue", "yellow"))
    figur(w, 0.35 * s + 0.3, pferd(w, "red_wool", reiter="red_wool", lanze=True), (-4, -1, -2), (6, 8, 2),
          pos=(-L // 2 - 4, 1, 0), winkel=0.0)
    leute(w, s, [(-L // 2 + 2 + k * 4, int(2 + s) + 1, -6 - int(1 + s * 0.5), math.pi / 2) for k in range(3)])
    return w


def bogenwiese(seed, g=1):
    """Bogenturnierwiese: eine Blumenwiese mit einer Reihe Zielscheiben auf Strohballen in gestaffelten Entfernungen,
    Schusslinie mit Bogengestell, farbigen Entfernungspfosten, Punktetafel und einem Schiedsrichterzelt."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.15, blumen=0.015)
    n = 3 + g
    zl = int(R * 0.6)
    for k in range(n):
        x = -int(R * 0.6) + k * int(1.2 * R / max(1, n - 1))
        zt = -int(R * 0.6) + (k % 2) * 3
        for dx in (-1, 0, 1):
            w.setze(x + dx, 1, zt, w.b("hay_block", axis="x"))
            for y in (2, 3, 4):
                w.setze(x + dx, y, zt, w.b("target", power=0) if (dx, y) == (0, 3) else
                        w.b("red_wool") if abs(dx) + abs(y - 3) == 1 else w.b("white_wool"))
        w.setze(x - 1, 2, zt - 1, w.b("spruce_fence"))
        w.setze(x + 1, 2, zt - 1, w.b("spruce_fence"))
        for j, z in enumerate(range(zt + 6, zl - 2, 6)):
            w.setze(x + 2, 1, z, w.b("spruce_fence"))
            w.setze(x + 2, 2, z, w.b(["white_wool", "yellow_wool", "red_wool", "blue_wool"][j % 4]))
    for x in range(-int(R * 0.7), int(R * 0.7) + 1):
        w.setze(x, 0, zl, w.b("white_concrete"))
    for k in range(2):
        waffenstaender(w, -int(R * 0.5) + k * int(R * 0.6), zl + 2)
    for x in range(int(R * 0.35), int(R * 0.35) + 5):
        for y in range(1, 4):
            w.setze(x, y, zl + 4, w.b("black_wool") if 1 < y and x not in (int(R * 0.35), int(R * 0.35) + 4) else
                    w.b("spruce_planks"))
    w.setze(int(R * 0.35) + 1, 3, zl + 3, w.b("white_wool"))
    w.setze(int(R * 0.35) + 3, 2, zl + 3, w.b("yellow_wool"))
    zelt(w, -int(R * 0.6), zl + 4, int(1.5 + s), farben=("green", "white"))
    w.setze(0, 1, zl + 3, w.b("barrel", facing="up", open=False))
    leute(w, s, [(-2 + k * 3, 1, zl + 1, math.pi) for k in range(2 + g)], seed=2)
    return w


def kraterarena(seed, g=2):
    """Kraterarena: der Kampfplatz liegt im Grund eines erloschenen Vulkankraters; in die Innenhänge sind Sitzränge
    aus Basalt gehauen, Glutadern leuchten im Fels, ein Tunnel führt durch den Kraterrand hinein."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 4)
    H = int(6 * s + 5)
    Rf = R * 0.38
    f = M(w, [("basalt", 2), ("blackstone", 2), ("tuff", 1), ("smooth_basalt", 1)], axis="y")
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 2 * rn(x, 0, z):
                continue
            if d < Rf:
                h = 0
            else:
                t = (d - Rf) / (R * 0.82 - Rf)
                h = int(H * min(1.0, t) if t <= 1 else H * max(0.0, 1 - (t - 1) * 3)) + int(rn(x, 3, z) * 1.5)
            for y in range(-2, h + 1):
                w.setze(x, y, z, f(x, y, z))
            if d < Rf:
                w.setze(x, 0, z, w.b("sand") if rn(x, 5, z) < 0.7 else w.b("red_sand"))
            elif h > 1 and rn(x, 8, z) < 0.12:
                w.setze(x, h, z, w.b("magma_block"))
            elif h >= H - 1:
                w.setze(x, h, z, w.b("grass_block", snowy=False) if rn(x, 9, z) < 0.4 else w.b("coarse_dirt"))
    for k in range(1, H):
        r = Rf + k * (R * 0.82 - Rf) / H
        n = int(2 * math.pi * r * 1.2)
        for j in range(n):
            a = j / n * 2 * math.pi
            if abs(math.atan2(math.sin(a - math.pi / 2), math.cos(a - math.pi / 2))) < 0.25:
                continue
            x, z = round(math.cos(a) * r), round(math.sin(a) * r)
            w.setze(x, k, z, w.b("polished_blackstone_brick_slab", type="bottom", waterlogged=False))
            for y in range(k + 1, k + 3):
                if not w.frei(x, y, z) and math.hypot(x, z) < r + 0.6:
                    w.bloecke.pop((x, y, z), None)
    for z in range(int(Rf) - 1, R + 3):
        for x in range(-2, 3):
            for y in range(1, 5):
                w.bloecke.pop((x, y, z), None)
            w.setze(x, 0, z, w.b("polished_blackstone"))
        if z % 3 == 0:
            for sx in (-3, 3):
                for y in range(1, 5):
                    w.setze(sx, y, z, w.b("polished_blackstone_bricks"))
            for x in range(-3, 4):
                w.setze(x, 5, z, w.b("polished_blackstone_bricks"))
    for k in range(6):
        a = k / 6 * 2 * math.pi + 0.3
        x, z = round(math.cos(a) * (Rf - 1)), round(math.sin(a) * (Rf - 1))
        w.setze(x, 1, z, w.b("polished_blackstone"))
        w.setze(x, 2, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    leute(w, s, [(round(math.cos(a) * (Rf + 3)), 2, round(math.sin(a) * (Rf + 3)), a + math.pi)
                 for a in (0.4, 1.4, 2.6, 3.8)], seed=4)
    return w


def schwebende_arena(seed, g=2):
    """Schwebende Arena: ein runder Kampfplatz aus poliertem Stein mit goldenem Ring liegt auf einer schwebenden
    Insel; Kettenbrücken führen zu kleineren Inseln mit Tribünen, Bannern und Leuchtfeuern."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 5)
    yi = int(10 * s + 8)
    top = insel(w, 0, yi, 0, R)
    yt = top if isinstance(top, int) else yi
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d <= R - 1.5:
                w.setze(x, yt, z, w.b("gold_block") if abs(d - (R - 3)) < 0.5 else
                        w.b("polished_andesite") if (x + z) % 2 else w.b("smooth_stone"))
                w.bloecke.pop((x, yt + 1, z), None)
            elif d <= R - 0.5 and (round(math.atan2(z, x) * 6) % 2 == 0):
                w.setze(x, yt + 1, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                          west="none", waterlogged=False))
    sats = []
    for k in range(3):
        a = k / 3 * 2 * math.pi + 0.5
        d = R + int(5 * s + 4)
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        rs = int(3 * s + 3)
        ys = yi + 2 + k
        t2 = insel(w, cx, ys, cz, rs)
        ys = t2 if isinstance(t2, int) else ys
        for kk in range(3):
            rr = rs - 1 - kk
            for j in range(int(2 * math.pi * rr * 1.3)):
                b = j / (2 * math.pi * rr * 1.3) * 2 * math.pi
                if math.cos(b - (a + math.pi)) > 0.3:
                    continue
                x, z = cx + round(math.cos(b) * rr), cz + round(math.sin(b) * rr)
                w.setze(x, ys + 1 + kk, z, w.b("quartz_stairs", facing="north", half="bottom", shape="straight",
                                              waterlogged=False) if kk < 2 else w.b("quartz_block"))
        fahne(w, cx, ys + 1, cz, (f"{FARBEN[k]}_wool", "white_wool"))
        sats.append((cx, ys, cz))
    for (cx, ys, cz) in sats:
        n = int(math.hypot(cx, cz))
        for k in range(n):
            t = k / n
            x, z = round(cx * (1 - t)), round(cz * (1 - t))
            y = round(ys + (yt - ys) * t - math.sin(t * math.pi) * 1.2)
            w.setze(x, y, z, w.b("spruce_slab", type="bottom", waterlogged=False), False)
            if k % 2 == 0:
                w.setze(x, y + 1, z, w.b("chain", axis="y", waterlogged=False), False)
    for k in range(4):
        a = k / 4 * 2 * math.pi
        x, z = round(math.cos(a) * (R - 2)), round(math.sin(a) * (R - 2))
        w.setze(x, yt + 1, z, w.b("chiseled_stone_bricks"))
        w.setze(x, yt + 2, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    leute(w, s, [(-2, yt + 1, 0, 0.0), (2, yt + 1, 0, math.pi)], seed=1)
    return w


def gladiatorenschule(seed, g=2):
    """Gladiatorenschule: ein ummauerter Übungshof mit Sandplatz, Holzpfählen zum Schlagtraining, Waffengestellen,
    einem Säulengang vor den Unterkünften, einem kleinen Übungsring und der Statue eines siegreichen Kämpfers."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wiese(w, R + 1, huegel=0.1)
    A = int(R * 0.75)
    st = M(w, [("sandstone", 2), ("cut_sandstone", 1), ("smooth_sandstone", 1)])
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            if max(abs(x), abs(z)) == A:
                if z == A and abs(x) <= 1:
                    continue
                for y in range(1, 5):
                    w.setze(x, y, z, st(x, y, z))
                w.setze(x, 5, z, w.b("cut_sandstone_slab", type="bottom", waterlogged=False))
    sand(w, -A + 1, -A + 7, A - 1, A - 1)
    wand = M(w, [("smooth_sandstone", 2), ("terracotta", 1)])
    haus(w, 0, -A + 3, 2 * A - 3, 5, 1, wand, holz="spruce", H=4, dach=("mcw:red_terracotta", "granite"),
         tuer_s="south", schorn=False)
    for x in range(-A + 2, A - 1, 3):
        for y in range(1, 5):
            w.setze(x, y, -A + 7, w.b("quartz_pillar", axis="y") if y < 4 else w.b("cut_sandstone"))
    for x in range(-A + 1, A):
        w.setze(x, 5, -A + 7, w.b("cut_sandstone_slab", type="bottom", waterlogged=False))
        w.setze(x, 5, -A + 6, w.b("cut_sandstone_slab", type="bottom", waterlogged=False))
    for k in range(int(3 + 2 * s)):
        x, z = -A + 3 + k * 3, A - 4
        if x > A - 2:
            break
        w.setze(x, 1, z, w.b("stripped_oak_log", axis="y"))
        w.setze(x, 2, z, w.b("stripped_oak_log", axis="y"))
    for k in range(2):
        waffenstaender(w, A - 5, -2 + k * 3)
    rr = int(2 + s)
    for k in range(int(2 * math.pi * rr * 1.4)):
        a = k / (2 * math.pi * rr * 1.4) * 2 * math.pi
        x, z = round(-A * 0.35 + math.cos(a) * rr), round(math.sin(a) * rr + 2)
        w.setze(x, 1, z, w.b("oak_fence"))
    figur(w, 0.45 * s + 0.35, mensch(w, "red_wool") + [(kap((0.9, 2.8, 0), (1.2, 6.0, 0), 0.2), w.b("iron_block")),
                                                        (ell(-0.9, 3.2, 0, 0.2, 1.0, 0.9), w.b("gold_block"))],
          (-2, -1, -2), (2, 7, 2), pos=(int(A * 0.4), 2, 2), winkel=-0.5)
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(int(A * 0.4) + dx, 1, 2 + dz, w.b("chiseled_sandstone"))
    leute(w, s, [(-int(A * 0.35) - 1, 1, 2, 0.0), (-int(A * 0.35) + 1, 1, 2, math.pi)], seed=5)
    return w


def hochlandspiele(seed, g=2):
    """Hochlandspiele-Wiese: eine Bergwiese mit Baumstämmen zum Werfen, Steinkugeln für das Steinstoßen, einem
    Seilziehen zweier Mannschaften, einem Hammerwurfkreis, karierten Decken, Zelten und Fahnenmasten."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, huegel=0.5, blumen=0.06)
    rng = w.rng
    for k in range(3):
        x0, z0 = -int(R * 0.5) + k * 4, -int(R * 0.45)
        y = zellen.get((x0, z0), 0) + 1
        for d in range(int(5 + 2 * s)):
            w.setze(x0 + d // 3, y, z0 + d, w.b("spruce_log", axis="z"), False)
    xs, zs = -int(R * 0.6), 0
    for y in range(1, int(7 + 3 * s)):
        w.setze(xs, zellen.get((xs, zs), 0) + y, zs, w.b("stripped_spruce_log", axis="y"))
    for k in range(4):
        x, z = int(R * 0.35) + (k % 2) * 3, -int(R * 0.45) + (k // 2) * 3
        y = zellen.get((x, z), 0) + 1
        kugel(w, x, y + 0.5, z, 0.6 + 0.3 * k, w.b("cobblestone"))
    yr = 1
    for x in range(-int(R * 0.3), int(R * 0.3) + 1):
        y = zellen.get((x, int(R * 0.35)), 0) + 2
        w.setze(x, y, int(R * 0.35), w.b("chain", axis="x", waterlogged=False), False)
        yr = max(yr, y)
    w.setze(0, yr + 1, int(R * 0.35), w.b("red_wool"))
    leute(w, s, [(x, zellen.get((x, int(R * 0.35) + 1), 0) + 1, int(R * 0.35) + 1, math.pi / 2 if x < 0 else
                  -math.pi / 2) for x in (-int(R * 0.25), -int(R * 0.15), int(R * 0.15), int(R * 0.25))], seed=3)
    hx, hz = int(R * 0.45), int(R * 0.05)
    for k in range(16):
        a = k / 16 * 2 * math.pi
        x, z = round(hx + math.cos(a) * 2.5), round(hz + math.sin(a) * 2.5)
        w.setze(x, zellen.get((x, z), 0), z, w.b("white_concrete"))
    for k in range(3):
        x0, z0 = -int(R * 0.1) + k * 4, -int(R * 0.1)
        for dx in range(3):
            for dz in range(2):
                x, z = x0 + dx, z0 + dz
                w.setze(x, zellen.get((x, z), 0) + 1, z,
                        w.b(f"{['red', 'green', 'blue'][k]}_carpet") if (dx + dz) % 2 else w.b("black_carpet"))
    zelt(w, int(R * 0.1), -int(R * 0.6), int(1.5 + s), farben=("green", "blue"))
    for k in range(3):
        fahne(w, -int(R * 0.7) + k * int(R * 0.7), zellen.get((-int(R * 0.7) + k * int(R * 0.7), int(R * 0.65)), 0)
              + 1, int(R * 0.65), (["blue", "green", "red"][k] + "_wool", "white_wool"))
    _ = rng
    return w


def heroldsstand(seed, g=1):
    """Heroldsstand mit Punktetafel: ein erhöhter Holzstand mit Baldachin, von dem der Herold verkündet, daneben eine
    große Tafel mit Wappenschilden und Punktmarken, Fanfarenbanner, eine Glocke und ein Podest."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    Hs = 3
    for x in range(-3, 4):
        for z in range(-2, 3):
            w.setze(x, Hs, z, w.b("spruce_planks"))
            if abs(x) == 3 or z == -2:
                w.setze(x, Hs + 1, z, zf(w, "spruce"))
            w.setze(x, Hs + 4, z, w.b(f"{['blue', 'yellow'][(x + 10) % 2]}_wool"))
    for x in (-3, 3):
        for z in (-2, 2):
            for y in range(1, Hs + 4):
                w.setze(x, y, z, w.b("spruce_log", axis="y"))
    for k in range(Hs):
        for x in (-1, 0, 1):
            w.setze(x, 1 + k, 3 + Hs - k - 1, w.b("spruce_stairs", facing="north", half="bottom", shape="straight",
                                                  waterlogged=False))
    w.setze(0, Hs + 3, 1, w.b("bell", attachment="ceiling", facing="north", powered=False))
    xt = int(R * 0.35) + 3
    Bt, Ht = int(5 + 3 * s), int(5 + 2 * s)
    for x in range(xt, xt + Bt + 1):
        for y in range(1, Ht + 2):
            rand = x in (xt, xt + Bt) or y in (1, Ht + 1)
            w.setze(x, y, -1, w.b("dark_oak_planks") if rand else w.b("black_wool"))
    for k in range(min(4, Bt // 2)):
        x = xt + 1 + k * 2
        f = FARBEN[k]
        w.setze(x, Ht, 0, w.b(f"{f}_wool"))
        w.setze(x, Ht - 1, 0, w.b(f"{f}_wool"))
        for p in range(1 + (k * 3 + seed) % 3):
            w.setze(x, Ht - 3 - p, 0, w.b("white_wool"))
    bannerreihe(w, -int(R * 0.6), -4, -3, h=5, farben=("blue", "yellow"))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(-int(R * 0.4) + dx, 1, 4 + dz, w.b("polished_andesite"))
    w.setze(-int(R * 0.4), 2, 4, w.b("gold_block"))
    figur(w, 0.3 * s + 0.22, mensch(w, "purple_wool"), (-2, -1, -2), (2, 6, 2), pos=(0, Hs + 1, 0), winkel=math.pi / 2)
    leute(w, s, [(k * 2 - 3, 1, int(R * 0.55), -math.pi / 2) for k in range(3 + g)], seed=6)
    return w


def turnierstall(seed, g=2):
    """Turnierstallungen: ein langer Stall mit offenen Boxen, Heuraufen und Satteltruhen, davor Pferde mit bunten
    Schabracken, eine Wassertränke, Heuhaufen und eine eingezäunte Koppel."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, huegel=0.15)
    L = int(R * 0.75)
    z0 = -int(R * 0.45)
    for x in range(-L, L + 1):
        for z in range(z0 - 3, z0 + 2):
            w.setze(x, 0, z, w.b("spruce_planks") if z > z0 - 3 else w.b("cobblestone"))
            for y in range(1, 5):
                w.bloecke.pop((x, y, z), None)
        for y in range(1, 4):
            w.setze(x, y, z0 - 3, w.b("spruce_planks") if y < 3 else w.b("stripped_spruce_log", axis="x"))
        if (x + L) % 4 == 0:
            for z in range(z0 - 2, z0 + 1):
                for y in range(1, 3):
                    w.setze(x, y, z, w.b("spruce_planks"))
            for y in range(1, 4):
                w.setze(x, y, z0 + 1, w.b("spruce_log", axis="y"))
        else:
            w.setze(x, 1, z0 + 1, w.b("spruce_fence_gate", facing="south", in_wall=False, open=False,
                                      powered=False))
            w.setze(x, 1, z0 - 2, w.b("hay_block", axis="y") if x % 2 else w.b("composter", level=3))
    for x in range(-L - 1, L + 2):
        for k, z in enumerate(range(z0 - 4, z0 + 3)):
            y = 4 + (k if k < 4 else 6 - k) // 2
            w.setze(x, y, z, w.b("dark_oak_slab", type="bottom" if k % 2 == 0 else "top", waterlogged=False))
    for k in range(2 + g):
        x = -L + 3 + k * int(2 * L / (2 + g))
        figur(w, 0.32 * s + 0.25, pferd(w, f"{FARBEN[k]}_wool", ["brown_terracotta", "white_terracotta",
                                                                 "black_terracotta", "light_gray_terracotta"][k % 4]),
              (-4, -1, -2), (5, 6, 2), pos=(x, 1, z0 + 4), winkel=0.0)
    for x in range(-2, 3):
        w.setze(x, 1, z0 + 8, w.b("cauldron") if x % 2 else w.b("water_cauldron", level=3))
    kp = int(R * 0.35)
    for k in range(int(2 * math.pi * kp * 1.2)):
        a = k / (2 * math.pi * kp * 1.2) * 2 * math.pi
        x, z = round(math.cos(a) * kp * 1.4), round(int(R * 0.45) + math.sin(a) * kp * 0.6)
        if math.hypot(x, z) < R - 1:
            w.setze(x, zellen.get((x, z), 0) + 1, z, w.b("oak_fence"))
    for k in range(3):
        x, z = L - 2 - k, z0 + 6 + (k % 2)
        w.setze(x, 1, z, w.b("hay_block", axis="y"))
        if k == 1:
            w.setze(x, 2, z, w.b("hay_block", axis="y"))
    return w


def turnierschmiede(seed, g=1):
    """Turnierschmiede: ein offener Schmiedepavillon am Turnierplatz mit gemauerter Esse und Schornstein, Ambossen,
    Schleifstein, Löschtrog, Gestellen voller Lanzen und Schilde sowie einem Haufen Holzkohle."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1, art="kies")
    B, T = int(4 * s + 5), int(3 * s + 4)
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            w.setze(x, 0, z, w.b("cobblestone") if (x + z) % 3 else w.b("stone_bricks"))
            if abs(x) == B and abs(z) == T or (abs(x) == B and z == 0):
                for y in range(1, 5):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
    for x in range(-B - 1, B + 2):
        for k, z in enumerate(range(-T - 1, T + 2)):
            y = 5 + min(k, 2 * T + 2 - k) // 2
            w.setze(x, y, z, w.b("spruce_slab", type="bottom" if k % 2 == 0 else "top", waterlogged=False))
    ex, ez = -B + 2, -T + 1
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            for y in range(1, 3):
                w.setze(ex + dx, y, ez + dz, w.b("bricks"))
    w.setze(ex, 2, ez + 1, w.b("magma_block"))
    w.setze(ex, 3, ez, w.b("blast_furnace", facing="south", lit=True))
    for y in range(3, int(10 + 2 * s)):
        w.setze(ex, y + 1, ez - 1, w.b("bricks"))
    w.setze(ex, int(11 + 2 * s), ez - 1, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                             waterlogged=False))
    w.setze(0, 1, -1, w.b("anvil", facing="east"))
    w.setze(2, 1, 1, w.b("chipped_anvil", facing="north"))
    w.setze(-2, 1, 2, w.b("grindstone", face="floor", facing="north"))
    for x in range(B - 3, B):
        w.setze(x, 1, -T + 1, w.b("water_cauldron", level=3))
    for k in range(int(3 + s)):
        x = -B + 1 + k * 2
        w.setze(x, 1, T, w.b("spruce_fence"))
        for y in range(2, 5):
            w.setze(x, y, T, w.b("stripped_spruce_log", axis="y") if y < 4 else w.b("iron_bars", north=False,
                                                                                     south=False, east=False,
                                                                                     west=False,
                                                                                     waterlogged=False))
    for k in range(3):
        x = B - 1 - k * 2
        w.setze(x, 2, T, w.b(f"{FARBEN[k]}_wool"))
        w.setze(x, 1, T, w.b("spruce_fence"))
    kugel(w, B + 3, 0.5, 2, 1.5, w.b("coal_block"))
    figur(w, 0.3 * s + 0.25, mensch(w, "brown_wool"), (-2, -1, -2), (2, 6, 2), pos=(1, 1, -1), winkel=math.pi)
    return w


def erdtribuene(seed, g=2):
    """Erdtribüne am Hang: ein natürlicher Hang wurde zu einem grasbewachsenen Halbrund mit Sitzterrassen und Holz-
    bänken geformt, unten ein Sandplatz mit Bühne, Fackelpfähle und Bäume auf der Hangkante."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 5)
    H = int(6 * s + 4)
    Rf = R * 0.35
    zc = int(R * 0.25)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            d = math.hypot(x, z - zc)
            if z - zc > 0 or d < Rf:
                h = 0
            else:
                h = min(H, int((d - Rf) / 1.5) + 1)
            h += 0 if h else int(rn(x, 3, z) * 1.2)
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else w.b("dirt"))
            if 0 < h < H and int((d - Rf) / 1.5) == (d - Rf) / 1.5 // 1 and (d - Rf) % 1.5 < 0.8 and \
                    z - zc < -1 and (x + z) % 5:
                w.setze(x, h + 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    sand(w, -int(Rf) + 1, zc - int(Rf) + 1, int(Rf) - 1, zc + int(Rf * 0.6))
    for x in range(-3, 4):
        for z in range(zc + int(Rf * 0.6) + 1, zc + int(Rf * 0.6) + 4):
            w.setze(x, 1, z, w.b("spruce_planks"))
    for sx in (-4, 4):
        for y in range(2, 6):
            w.setze(sx, y, zc + int(Rf * 0.6) + 3, w.b("spruce_log", axis="y"))
    for x in range(-4, 5):
        w.setze(x, 6, zc + int(Rf * 0.6) + 3, w.b(f"{FARBEN[(x + 10) % 2]}_wool"))
    for k in range(6):
        a = math.pi + k / 5 * math.pi
        x, z = round(math.cos(a) * (Rf + 0.5)), round(zc + math.sin(a) * (Rf + 0.5))
        for y in range(1, 4):
            w.setze(x, y, z, w.b("spruce_fence"))
        w.setze(x, 4, z, w.b("lantern", hanging=False, waterlogged=False))
    zellen = {}
    for (x, y, z) in list(w.bloecke):
        zellen[(x, z)] = max(zellen.get((x, z), -9), y)
    for k in range(4 + g):
        a = math.pi * 1.1 + k / (3 + g) * math.pi * 0.8
        x, z = round(math.cos(a) * R * 0.85), round(zc + math.sin(a) * R * 0.85)
        if (x, z) in zellen and math.hypot(x, z) < R - 1:
            einfuegen(w, wald2.laubbaum(seed + k * 7, holz="oak", H=int(7 + 3 * s)), x, zellen[(x, z)] + 1, z)
    leute(w, s, [(round(math.cos(a) * (Rf + 3)), 2, round(zc + math.sin(a) * (Rf + 3)), a + math.pi)
                 for a in (3.5, 4.2, 5.0, 5.8)], seed=7)
    return w


def eisarena(seed, g=2):
    """Eisarena: ein zugefrorener See, auf dem eine ovale Spielfläche mit Holzbande und zwei Toren abgesteckt ist;
    rundherum Schneeränge, Fichten, Kohlebecken und eine Schlittschuhhütte."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 4)
    rx, rz = R * 0.6, R * 0.38
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            e = (x / (rx + 3)) ** 2 + (z / (rz + 3)) ** 2
            if e <= 1:
                w.setze(x, 0, z, w.b("ice") if rn(x, 5, z) < 0.7 else w.b("packed_ice"))
                w.setze(x, -1, z, w.b("water", level=0))
                w.setze(x, -2, z, w.b("gravel"))
            else:
                h = min(3, int((math.sqrt(e) - 1) * 6))
                for y in range(-2, h + 1):
                    w.setze(x, y, z, w.b("snow_block") if y == h else w.b("dirt"))
                if h >= 1 and rn(x, 7, z) < 0.3:
                    w.setze(x, h + 1, z, w.b("snow", layers=1))
    n = int((rx + rz) * 6)
    for k in range(n):
        a = k / n * 2 * math.pi
        x, z = round(math.cos(a) * rx), round(math.sin(a) * rz)
        w.setze(x, 1, z, w.b("white_concrete") if k % 6 else w.b("red_concrete"))
        w.setze(x, 2, z, zf(w, "spruce"))
    for sx in (-1, 1):
        gx = sx * (int(rx) - 3)
        for dz in (-1, 0, 1):
            w.setze(gx, 3, dz, w.b("red_concrete"))
            w.setze(gx + sx, 1, dz, w.b("iron_bars", north=True, south=True, east=False, west=False,
                                        waterlogged=False))
            w.setze(gx + sx, 2, dz, w.b("iron_bars", north=True, south=True, east=False, west=False,
                                        waterlogged=False))
        for y in (1, 2):
            w.setze(gx, y, -1, w.b("red_concrete"))
            w.setze(gx, y, 1, w.b("red_concrete"))
    for x in range(-int(rx) + 2, int(rx) - 1):
        w.setze(x, 0, 0, w.b("blue_ice")) if x == 0 else None
    for k in range(int(4 + 2 * s)):
        a = 0.3 + k * 1.1
        x, z = round(math.cos(a) * R * 0.85), round(math.sin(a) * R * 0.85)
        if math.hypot(x, z) < R - 1 and (x / (rx + 4)) ** 2 + (z / (rz + 4)) ** 2 > 1.2:
            fichte(w, x, hoehe(w, x, z, 6) + 1, z, seed + k, 6 + 3 * s, schnee=True)
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.78
        x, z = round(math.cos(a) * (rx + 4)), round(math.sin(a) * (rz + 4))
        y = hoehe(w, x, z, 6) + 1
        w.setze(x, y, z, w.b("cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
                             waterlogged=False))
        w.setze(x, y + 1, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    haus(w, 0, -int(rz) - 6, 5, 4, hoehe(w, 0, -int(rz) - 6, 6) + 1, M(w, [("spruce_planks", 2),
                                                                            ("stripped_spruce_log", 1)]),
         holz="spruce", H=3, dach=("spruce", "dark_oak"), tuer_s="south")
    leute(w, s, [(-3, 1, -2, 0.3), (2, 1, 1, 2.6), (5, 1, -1, 1.2)], seed=8)
    return w


def wuestenarena(seed, g=2):
    """Wüstenarena mit Sonnensegeln: ein ovales Rund aus Sandstein mit gestuften Rängen, über denen farbige
    Sonnensegel an Masten gespannt sind; Säulentor, Palmen und Wasserkrüge."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    wiese(w, R, huegel=0.3, art="strand", blumen=0.0)
    rx, rz = R * 0.45, R * 0.32
    sand(w, -int(rx), -int(rz), int(rx), int(rz), rund=True)
    stn = M(w, [("sandstone", 2), ("smooth_sandstone", 2), ("cut_sandstone", 1)])
    st = int(2 + 1.5 * s)
    ovaltribuene(w, 0, 0, rx + 1, rz + 1, st, lambda x, y, z, t: stn(x, y, z), oeffnungen=(math.pi / 2,
                                                                                          -math.pi / 2))
    ro_x, ro_z = rx + st + 1, rz + st + 1
    for k in range(10):
        a = k / 10 * 2 * math.pi
        if abs(math.cos(a)) < 0.2:
            continue
        x, z = round(math.cos(a) * ro_x), round(math.sin(a) * ro_z)
        for y in range(1, st + 6):
            w.setze(x, y, z, w.b("stripped_acacia_log", axis="y"))
        xi, zi = round(math.cos(a) * (rx + 1)), round(math.sin(a) * (rz + 1))
        n = int(math.hypot(x - xi, z - zi)) + 1
        for j in range(n + 1):
            t = j / n
            for b in (-1, 0, 1):
                px = round(x + (xi - x) * t - math.sin(a) * b)
                pz = round(z + (zi - z) * t + math.cos(a) * b)
                w.setze(px, st + 5 - int(t * 2), pz, w.b(f"{['red', 'white', 'orange'][k % 3]}_wool"), False)
    for sz in (-1, 1):
        z = sz * round(ro_z)
        for sx in (-2, 2):
            for y in range(1, 7):
                w.setze(sx, y, z, w.b("chiseled_sandstone") if y in (1, 6) else w.b("cut_sandstone"))
        for x in range(-2, 3):
            w.setze(x, 7, z, w.b("smooth_sandstone_slab", type="bottom", waterlogged=False))
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.5
        x, z = round(math.cos(a) * R * 0.85), round(math.sin(a) * R * 0.85)
        if math.hypot(x, z) < R - 1:
            einfuegen(w, wald2.palme(seed + k * 11, H=int(7 + 3 * s)), x, hoehe(w, x, z, 6) + 1, z)
    for k in range(3):
        w.setze(int(rx) - 1 - k, 1, 0, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False))
    figur(w, 0.32 * s + 0.25, pferd(w, "yellow_wool", "white_terracotta", reiter="orange_wool"), (-4, -1, -2),
          (5, 8, 2), pos=(-2, 1, 0), winkel=0.5)
    return w


def kletterturm(seed, g=2):
    """Kletterturm-Wettkampf: ein hoher Holzturm, dessen vier Wände mit bunten Klettergriffen übersät sind, oben
    eine Plattform mit Siegesglocke und Fahne, unten Strohballen als Polster und Zuschauerbänke."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    Ht = int(10 * s + 8)
    a = int(2 + s)
    rng = w.rng
    farben = ["red_terracotta", "yellow_terracotta", "blue_terracotta", "lime_terracotta", "orange_terracotta"]
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if max(abs(x), abs(z)) != a:
                continue
            for y in range(1, Ht + 1):
                ecke = abs(x) == a and abs(z) == a
                w.setze(x, y, z, w.b("spruce_log", axis="y") if ecke else w.b("spruce_planks"))
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            if max(abs(x), abs(z)) != a + 1:
                continue
            if abs(x) == a + 1 and abs(z) == a + 1:
                continue
            for y in range(2, Ht):
                if rng.random() < 0.22:
                    w.setze(x, y, z, w.b(farben[int(rng.integers(len(farben)))]), False)
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            w.setze(x, Ht + 1, z, w.b("spruce_planks"))
            if max(abs(x), abs(z)) == a + 1:
                w.setze(x, Ht + 2, z, zf(w, "spruce"))
    galgenrahmen(w, 0, 0, Ht + 4, breite=1)
    w.setze(0, Ht + 4, 0, w.b("bell", attachment="ceiling", facing="north", powered=False))
    fahne(w, a, Ht + 2, a, ("red_wool", "yellow_wool"))
    for x in range(-a - 3, a + 4):
        for z in range(-a - 3, a + 4):
            if a + 2 <= max(abs(x), abs(z)) <= a + 3 and rng.random() < 0.7:
                w.setze(x, 1, z, w.b("hay_block", axis="y"))
    for k in range(2):
        for x in range(-a - 2, a + 3):
            w.setze(x, 1, int(R * 0.6) + k * 2, w.b("spruce_stairs", facing="north", half="bottom",
                                                     shape="straight", waterlogged=False))
    leute(w, s, [(-a - 1, int(Ht * 0.4), a + 2, -math.pi / 2), (a + 2, int(Ht * 0.65), 0, math.pi)], seed=9)
    leute(w, s, [(x, 1, int(R * 0.6) + 1, -math.pi / 2) for x in (-3, 0, 3)], seed=2)
    return w


def duellbruecke(seed, g=2):
    """Duellbrücke: über einer tiefen Schlucht mit Wildbach spannt sich eine schmale Steinbrücke ohne Geländer mit
    einer runden Kampfplattform in der Mitte; an beiden Enden Bannertore und Zuschauerbalkone am Fels."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    H = int(12 * s + 8)
    Hn = int(H * 0.55)
    f = M(w, [("stone", 3), ("andesite", 2), ("granite", 0.5)])
    sp = 3 + 1.5 * s
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            mz = math.sin(x / 5) * 1.5
            if abs(z - mz) < sp:
                w.setze(x, -4, z, w.b("water", level=0))
                w.setze(x, -5, z, w.b("gravel"))
                continue
            hh = (H if z < mz else Hn) + int(rn(x, 3, z) * 2)
            for y in range(-5, hh + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == hh else f(x, y, z))
    yb = Hn + 1
    for z in range(-int(sp) - 4, int(sp) + 4):
        w.setze(0, yb, z, w.b("stone_bricks"))
        w.setze(0, yb - 1, z, w.b("stone_brick_slab", type="top", waterlogged=False))
        for x in (-1, 0, 1):
            for y in range(yb + 1, yb + 4):
                w.bloecke.pop((x, y, z), None)
    for z in range(-int(sp) - 7, -int(sp) - 3):
        for x in range(-2, 3):
            w.setze(x, yb, z, w.b("polished_andesite"))
            for y in range(yb + 1, yb + 5):
                w.bloecke.pop((x, y, z), None)
    rp = 1.5 + s * 0.6
    for x in range(-3, 4):
        for z in range(-3, 4):
            if math.hypot(x, z) <= rp + 0.4:
                w.setze(x, yb, z, w.b("chiseled_stone_bricks") if (x, z) == (0, 0) else w.b("polished_andesite"))
                w.setze(x, yb - 1, z, w.b("stone_bricks"))
    for y in range(-4, yb - 1):
        w.setze(0, y, 0, w.b("stone_bricks"))
        w.setze(1, y, 0, w.b("stone_bricks")) if y < yb - 3 else None
    for sz in (-1, 1):
        ze = sz * (int(sp) + 3)
        for dx in (-2, 2):
            for y in range(yb + 1, yb + 6):
                w.setze(dx, y, ze, w.b("stone_bricks"))
        for dx in range(-2, 3):
            w.setze(dx, yb + 6, ze, w.b("chiseled_stone_bricks"))
        f2 = "red_wool" if sz < 0 else "blue_wool"
        w.setze(0, yb + 5, ze, w.b(f2))
        w.setze(0, yb + 4, ze, w.b(f2))
    leute(w, s, [(0, yb + 1, -1, math.pi / 2), (0, yb + 1, 1, -math.pi / 2)], seed=0)
    for k, x in enumerate((-int(R * 0.5), int(R * 0.5))):
        zb = -int(sp) - 1
        y0 = yb + 3 + k * 3
        for dx in range(-2, 3):
            for dz in range(0, 3):
                w.setze(x + dx, y0, zb + dz - 2, w.b("spruce_planks"))
                for y in range(y0 + 1, y0 + 4):
                    if dz < 2:
                        w.bloecke.pop((x + dx, y, zb + dz - 2), None)
            w.setze(x + dx, y0 + 1, zb, zf(w, "spruce"))
        leute(w, s, [(x - 1, y0 + 1, zb - 1, -math.pi / 2), (x + 1, y0 + 1, zb - 1, -math.pi / 2)], seed=3 + k)
    return w


def kampfrichterpavillon(seed, g=1):
    """Kampfrichter-Pavillon: ein sechseckiger, erhöhter Pavillon mit Zeltdach, in dem drei Kampfrichter hinter
    einem langen Tisch mit Sanduhr und Urkunden sitzen, davor ein kleiner Kampfring mit Seilen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    rp = int(3 + s)
    zp = -int(R * 0.4)
    for x in range(-rp - 1, rp + 2):
        for z in range(zp - rp - 1, zp + rp + 2):
            if math.hypot(x, z - zp) <= rp + 0.5:
                for y in range(1, 3):
                    w.setze(x, y, z, w.b("stone_bricks") if y == 1 else w.b("dark_oak_planks"))
    for k in range(6):
        a = k / 6 * 2 * math.pi
        x, z = round(math.cos(a) * rp), round(zp + math.sin(a) * rp)
        for y in range(3, 7):
            w.setze(x, y, z, w.b("dark_oak_log", axis="y"))
    kegeldach(w, 0, zp, 7, rp + 0.5, Dachmat(w, ["mcw:red_terracotta", "brick"]), eckig=True)
    for x in range(-2, 3):
        w.setze(x, 3, zp + 1, w.b("dark_oak_slab", type="top", waterlogged=False))
    w.setze(0, 4, zp + 1, w.b("brewing_stand", has_bottle_0=False, has_bottle_1=False, has_bottle_2=False))
    w.setze(-2, 4, zp + 1, w.b("lectern", facing="south", has_book=True, powered=False))
    for k in range(3):
        figur(w, 0.27 * s + 0.2, mensch(w, ["black_wool", "purple_wool", "black_wool"][k]), (-2, -1, -2), (2, 6, 2),
              pos=(-2 + k * 2, 3, zp - 1), winkel=-math.pi / 2)
    for k in range(3):
        for x in (-1, 0, 1):
            w.setze(x, 1 + k, zp + rp + 3 - k, w.b("stone_brick_stairs", facing="north", half="bottom",
                                                   shape="straight", waterlogged=False))
    rr = int(3 + s)
    zr = int(R * 0.4)
    for x in range(-rr, rr + 1):
        for z in range(zr - rr, zr + rr + 1):
            w.setze(x, 0, z, w.b("sand"))
            if max(abs(x), abs(z - zr)) == rr:
                w.setze(x, 1, z, w.b("spruce_log", axis="y") if abs(x) == rr and abs(z - zr) == rr else
                        zf(w, "spruce"))
    leute(w, s, [(-1, 1, zr, 0.0), (1, 1, zr, math.pi)], seed=4)
    return w


def waldlichtung_arena(seed, g=2):
    """Waldlichtungs-Arena: mitten in einem dichten Wald liegt eine runde Lichtung mit einem Erdring, eingefasst von
    Seilpfosten, rundum Sitzreihen aus gefällten Stämmen, Fackelpfähle und eine Feuerstelle am Rand."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, huegel=0.3, art="wald")
    rr = R * 0.32
    for x in range(-int(rr) - 1, int(rr) + 2):
        for z in range(-int(rr) - 1, int(rr) + 2):
            if math.hypot(x, z) <= rr:
                w.setze(x, zellen.get((x, z), 0), z, w.b("coarse_dirt") if (x + z) % 3 else w.b("rooted_dirt"))
                w.bloecke.pop((x, zellen.get((x, z), 0) + 1, z), None)
    n = int(2 * math.pi * (rr + 1) * 1.2)
    for k in range(n):
        a = k / n * 2 * math.pi
        x, z = round(math.cos(a) * (rr + 1)), round(math.sin(a) * (rr + 1))
        y = zellen.get((x, z), 0) + 1
        w.setze(x, y, z, w.b("spruce_fence") if k % 3 else w.b("spruce_log", axis="y"))
    for ring in (rr + 3, rr + 5):
        n = int(2 * math.pi * ring)
        for k in range(n):
            a = k / n * 2 * math.pi
            if k % 7 == 0:
                continue
            x, z = round(math.cos(a) * ring), round(math.sin(a) * ring)
            y = zellen.get((x, z), 0) + 1
            w.setze(x, y + (1 if ring > rr + 4 else 0), z,
                    w.b("oak_log", axis="x" if abs(math.sin(a)) > 0.7 else "z"), False)
    for k in range(6):
        a = k / 6 * 2 * math.pi + 0.25
        x, z = round(math.cos(a) * (rr + 7)), round(math.sin(a) * (rr + 7))
        y = zellen.get((x, z), 0) + 1
        for d in range(3):
            w.setze(x, y + d, z, w.b("spruce_fence"))
        w.setze(x, y + 3, z, w.b("lantern", hanging=False, waterlogged=False))
    w.setze(int(rr) + 9, zellen.get((int(rr) + 9, 0), 0) + 1, 0, w.b("campfire", lit=True, signal_fire=False,
                                                                    facing="north", waterlogged=False))
    baumrand(w, zellen, R, int(12 + 8 * s), seed, innen=0.72, H=(8, 12 + 3 * s), art="misch")
    leute(w, s, [(-1, zellen.get((-1, 0), 0) + 1, 0, 0.0), (1, zellen.get((1, 0), 0) + 1, 0, math.pi)], seed=6)
    return w


def quintana(seed, g=2):
    """Quintana-Platz: ein gepflasterter Platz mit Sandbahn, an deren Ende die drehbare Quintana-Puppe steht – ein
    Pfahl mit Querarm, Schild auf der einen und Sandsack auf der anderen Seite; Arkaden und Wappenbanner."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wiese(w, R, huegel=0.1)
    A = int(R * 0.72)
    pfl = M(w, [("stone_bricks", 2), ("cobblestone", 2), ("andesite", 1)])
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            w.setze(x, 0, z, pfl(x, 0, z))
            w.bloecke.pop((x, 1, z), None)
    sand(w, -A + 2, -2, A - 2, 2)
    qx = A - 5
    for y in range(1, 6):
        w.setze(qx, y, 0, w.b("stripped_oak_log", axis="y"))
    for z in range(-3, 4):
        w.setze(qx, 5, z, w.b("oak_log", axis="z"))
    for dy in (2, 3, 4):
        w.setze(qx, dy, -3, w.b("red_wool") if dy != 3 else w.b("yellow_wool"))
        w.setze(qx, dy, -4, w.b("red_wool"))
    kette_y = (4, 3)
    for y in kette_y:
        w.setze(qx, y, 3, w.b("chain", axis="y", waterlogged=False))
    w.setze(qx, 2, 3, w.b("brown_wool"))
    figur(w, 0.4 * s + 0.3, mensch(w, "red_wool") + [(ell(0, 4.75, 0, 0.6, 0.35, 0.6), w.b("iron_block"))],
          (-2, -1, -2), (2, 7, 2), pos=(qx, 6, 0), winkel=math.pi)
    for sz in (-1, 1):
        z0 = sz * (A - 2)
        for x in range(-A + 1, A):
            if (x + A) % 3 == 0:
                for y in range(1, 5):
                    w.setze(x, y, z0, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                          west="none", waterlogged=False) if 1 < y < 4 else w.b("stone_bricks"))
            for dz in (0, sz):
                w.setze(x, 5, z0 + dz, w.b("stone_bricks"))
            w.setze(x, 6, z0 + sz, w.b("mcw:red_terracotta", ersatz="bricks") if False else w.b("brick_slab",
                                                                                             type="bottom",
                                                                                             waterlogged=False))
            w.setze(x, 5, z0 + 2 * sz, w.b("brick_stairs", facing="north" if sz > 0 else "south", half="bottom",
                                           shape="straight", waterlogged=False))
        for x in range(-A + 2, A - 1, 4):
            w.setze(x, 4, z0 - sz, w.b(f"{FARBEN[(x // 4) % 4]}_wool"))
            w.setze(x, 3, z0 - sz, w.b(f"{FARBEN[(x // 4) % 4]}_wool"))
    figur(w, 0.35 * s + 0.3, pferd(w, "blue_wool", reiter="blue_wool", lanze=True), (-4, -1, -2), (6, 8, 2),
          pos=(-A + 5, 1, 0), winkel=0.0)
    leute(w, s, [(x, 1, -A + 4, math.pi / 2) for x in range(-A + 4, A - 6, int(4 + s))], seed=1)
    return w


def regatta(seed, g=2):
    """Regattastrecke: ein langer See mit durch Bojen markierten Bahnen, einem Startsteg mit Fahnen, einem über das
    Wasser gespannten Zielbogen, Ruderbooten und einer Zuschauerwiese mit Zelten."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, huegel=0.2)
    zw = int(R * 0.35)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, zw + 1):
            if (x, z) in zellen and z > -R * 0.75:
                for y in range(-2, 3):
                    w.bloecke.pop((x, y, z), None)
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("water", level=0))
                w.setze(x, -2, z, w.b("sand"))
    L = int(R * 0.85)
    bahnen = [int(-R * 0.6) + k * 4 for k in range(int(3 + s))]
    for zb in bahnen[1:]:
        for x in range(-L, L + 1, 3):
            if (x, zb - 2) in zellen:
                w.setze(x, 0, zb - 2, w.b(["red_wool", "yellow_wool"][(x // 3) % 2]))
    for k, zb in enumerate(bahnen):
        bx = -L + 4 + k * 2
        for dx in range(-2, 3):
            w.setze(bx + dx, 0, zb, w.b("spruce_slab", type="top", waterlogged=True))
        w.setze(bx - 3, 0, zb, w.b("spruce_stairs", facing="east", half="top", shape="straight", waterlogged=True))
        w.setze(bx + 3, 0, zb, w.b("spruce_stairs", facing="west", half="top", shape="straight", waterlogged=True))
        figur(w, 0.25 * s + 0.2, mensch(w, f"{FARBEN[k]}_wool"), (-2, -1, -2), (2, 6, 2), pos=(bx, 1, zb),
              winkel=0.0)
    xs = -L
    for z in range(bahnen[0] - 2, zw + 2):
        for dx in (-1, 0):
            w.setze(xs + dx, 1, z, w.b("spruce_planks"))
        if z % 3 == 0:
            w.setze(xs - 2, 1, z, w.b("spruce_fence"))
            w.setze(xs - 2, 2, z, w.b(f"{FARBEN[z % 4]}_wool"))
    xf = L
    for zz in (bahnen[0] - 3, bahnen[-1] + 3):
        for y in range(0, 8):
            w.setze(xf, y, zz, w.b("spruce_log", axis="y"))
    for z in range(bahnen[0] - 3, bahnen[-1] + 4):
        w.setze(xf, 8, z, w.b("spruce_log", axis="z"))
        w.setze(xf, 7, z, w.b("black_wool" if (z % 2) else "white_wool"))
    for k in range(2 + g // 2):
        x = -int(R * 0.4) + k * int(R * 0.5)
        zelt(w, x, zw + 4, int(1.5 + s * 0.6), farben=[("red", "white"), ("blue", "white"), ("green", "yellow")][k % 3])
    leute(w, s, [(x, zellen.get((x, zw + 2), 0) + 1, zw + 2, -math.pi / 2) for x in (-6, -2, 3, 7)], seed=4)
    return w


def ballspielplatz(seed, g=2):
    """Ballspielplatz mit Steinringen: ein langgestreckter Spielplatz zwischen zwei schrägen, bemalten Steinwänden,
    hoch oben an jeder Wand ein steinerner Ring; an den Enden Querfelder und Treppenpodeste mit Altären."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    wiese(w, R, huegel=0.2)
    L = int(R * 0.6)
    B = int(2 + s)
    Hw = int(4 + 2 * s)
    st = M(w, [("mossy_stone_bricks", 1), ("stone_bricks", 2), ("chiseled_stone_bricks", 0.3), ("andesite", 1)])
    for x in range(-L, L + 1):
        for z in range(-B, B + 1):
            w.setze(x, 0, z, w.b("smooth_stone") if (x + z) % 4 else w.b("polished_andesite"))
        for sz in (-1, 1):
            for k in range(Hw):
                for d in range(Hw - k):
                    z = sz * (B + 1 + k + d // 2)
                    w.setze(x, 1 + k, sz * (B + 1 + k), st(x, k, z))
                for yy in range(1, k + 1):
                    w.setze(x, yy, sz * (B + 1 + k), st(x, yy, k))
            for k in range(3):
                for y in range(1, Hw + 3):
                    w.setze(x, y, sz * (B + Hw + 1 + k), st(x, y, k))
            if x % 4 == 0:
                w.setze(x, 1, sz * (B + 1), w.b("red_terracotta"))
    for sz in (-1, 1):
        z = sz * (B + Hw - 1)
        y = Hw + 1
        for dx, dy in ((-1, 0), (1, 0), (0, 1), (0, -1), (-1, 1), (1, 1), (-1, -1), (1, -1)):
            w.setze(dx, y + dy, z, w.b("chiseled_stone_bricks"))
        w.bloecke.pop((0, y, z), None)
    for sx in (-1, 1):
        for x in range(sx * (L + 1), sx * (L + 5), sx):
            for z in range(-B - 3, B + 4):
                w.setze(x, 0, z, w.b("polished_andesite"))
        for k in range(3):
            for z in range(-2, 3):
                for x in range(sx * (L + 6 + k), sx * (L + 9), sx):
                    w.setze(x, 1 + k, z, st(x, k, z))
        w.setze(sx * (L + 8), 4, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    leute(w, s, [(-3, 1, 0, 0.0), (3, 1, 1, math.pi), (0, 1, -1, 1.2)], seed=5)
    return w


def seearena(seed, g=2):
    """Seearena auf Pfählen: auf Holzpfählen im See steht eine quadratische Kampfplattform mit Geländer und
    Flaggen; ein Bohlensteg führt vom Ufer hinaus, ringsum schwimmen Zuschauerflöße mit Laternen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 4)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            if z > R * 0.6 + rn(x, 3, 0) * 2:
                for y in range(-3, 1):
                    w.setze(x, y, z, w.b("grass_block", snowy=False) if y == 0 else w.b("dirt"))
            else:
                for y in range(-2, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -3, z, w.b("sand") if rn(x, 5, z) < 0.5 else w.b("gravel"))
    A = int(3 * s + 3)
    yp = 2
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            w.setze(x, yp, z, w.b("spruce_planks") if (x + z) % 5 else w.b("stripped_spruce_log", axis="x"))
            if max(abs(x), abs(z)) == A:
                w.setze(x, yp + 1, z, zf(w, "spruce"))
            if (abs(x) == A or abs(x) % 3 == 0) and (abs(z) == A or abs(z) % 3 == 0):
                for y in range(-2, yp):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
    for sx in (-A, A):
        for sz in (-A, A):
            for y in range(yp + 1, yp + 6):
                w.setze(sx, y, sz, w.b("spruce_log", axis="y"))
            fahne(w, sx, yp + 6, sz, ("blue_wool", "white_wool") if sx < 0 else ("red_wool", "white_wool"))
    for z in range(A + 1, int(R * 0.7)):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
        if z % 3 == 0:
            for sx in (-2, 2):
                for y in range(-2, 3):
                    w.setze(sx, y, z, w.b("spruce_log", axis="y"))
            laterne(w, 2, 4, z, kette=0)
            w.setze(2, 3, z, w.b("spruce_fence"))
    for z in (A, A + 1):
        for x in (-1, 0, 1):
            w.setze(x, yp - (z - A), z + 0, w.b("spruce_slab", type="bottom", waterlogged=False))
    for k in range(int(3 + s)):
        a = math.pi + k / (2 + s) * math.pi
        cx, cz = round(math.cos(a) * (A + 6 + s * 2)), round(math.sin(a) * (A + 5 + s * 2))
        for dx in range(-2, 3):
            for dz in range(-1, 2):
                w.setze(cx + dx, 0, cz + dz, w.b("spruce_log", axis="x"))
                w.setze(cx + dx, 1, cz + dz, w.b("spruce_slab", type="bottom", waterlogged=False)) if dz == -1 else None
        w.setze(cx + 2, 1, cz + 1, w.b("spruce_fence"))
        w.setze(cx + 2, 2, cz + 1, w.b("lantern", hanging=False, waterlogged=False))
        leute(w, s, [(cx, 1, cz, math.atan2(-cz, -cx))], seed=k)
    leute(w, s, [(-1, yp + 1, 0, 0.0), (1, yp + 1, 0, math.pi)], seed=3)
    return w


ARENA3 = {
    "ringstechbahn": ("Ringstechbahn", ringstechbahn),
    "bogenwiese": ("Bogenturnierwiese", bogenwiese),
    "kraterarena": ("Kraterarena", kraterarena),
    "schwebende_arena": ("Schwebende Arena", schwebende_arena),
    "gladiatorenschule": ("Gladiatorenschule", gladiatorenschule),
    "hochlandspiele": ("Hochlandspiele-Wiese", hochlandspiele),
    "heroldsstand": ("Heroldsstand mit Punktetafel", heroldsstand),
    "turnierstall": ("Turnierstallungen", turnierstall),
    "turnierschmiede": ("Turnierschmiede", turnierschmiede),
    "erdtribuene": ("Erdtribüne am Hang", erdtribuene),
    "eisarena": ("Eisarena", eisarena),
    "wuestenarena": ("Wüstenarena mit Sonnensegeln", wuestenarena),
    "kletterturm": ("Kletterturm-Wettkampf", kletterturm),
    "duellbruecke": ("Duellbrücke", duellbruecke),
    "kampfrichterpavillon": ("Kampfrichter-Pavillon", kampfrichterpavillon),
    "waldlichtung_arena": ("Waldlichtungs-Arena", waldlichtung_arena),
    "quintana": ("Quintana-Platz", quintana),
    "regatta": ("Regattastrecke", regatta),
    "ballspielplatz": ("Ballspielplatz mit Steinringen", ballspielplatz),
    "seearena": ("Seearena auf Pfählen", seearena),
}

"""Leuchtwald II – zwanzig weitere leuchtende Fantasiegewächse (eigene Entwürfe): Laternenbaum, Quallenbaum,
Leuchtfarn, Sternblumen, Glimmerbogen, Seelenlichtbaum, Kristallblätterbaum, Leuchtschwamm-Säulen, Spiralbaum,
Leuchtmoos-Lichtung, Schirmbaum, Perlenbaum, Leuchtkelche, Lichtorgel, Seerosenteich, Nachtblütenbusch,
Pilzturm, Tentakelpflanze, Lampionblumen und Herz des Waldes."""

from __future__ import annotations

import math

import numpy as np

from bogen2 import koerper, setzen
from leuchtwald import _boden, _welt
from lib import Rauschen

S = [0.6, 1.0, 1.6, 2.5]
GLAS = ["light_blue_stained_glass", "cyan_stained_glass", "purple_stained_glass", "magenta_stained_glass"]


# ============================================================================ Werkzeuge

def bez(p0, p1, p2, p3=None, n=None):
    p0, p1, p2 = np.array(p0, float), np.array(p1, float), np.array(p2, float)
    p3 = None if p3 is None else np.array(p3, float)
    L = np.linalg.norm(p2 - p0) + (0 if p3 is None else np.linalg.norm(p3 - p2))
    n = n or max(4, int(L * 3))
    pts = []
    for i in range(n + 1):
        t = i / n
        if p3 is None:
            p = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2
        else:
            p = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3
        pts.append((p[0], p[1], p[2], t))
    return pts


def rohr(w, pts, r0, r1=None, mat=None, rauh=0.15, ueber=True):
    r1 = r0 if r1 is None else r1
    m = mat if callable(mat) else (lambda *_: mat)
    lo, occ, tg = koerper(w, pts, lambda t: r0 + (r1 - r0) * t, rz=1.0, rauh=rauh)
    return setzen(w, lo, occ, tg, m, ab_y=-3, ueber=ueber)


def kugel(w, cx, cy, cz, r, blk, hohl=False, ueber=True, ry=None):
    ry = ry or r
    for dx in range(-int(r) - 1, int(r) + 2):
        for dy in range(-int(ry) - 1, int(ry) + 2):
            for dz in range(-int(r) - 1, int(r) + 2):
                d = (dx / r) ** 2 + (dy / ry) ** 2 + (dz / r) ** 2
                if d <= 1 and (not hohl or d > (1 - 1.6 / max(r, 1.6)) ** 2):
                    p = (round(cx + dx), round(cy + dy), round(cz + dz))
                    w.setze(*p, blk(*p) if callable(blk) else blk, ueber)


def strang(w, x, y, z, L, farben, perle=5):
    for k in range(1, L + 1):
        if not w.frei(x, y - k, z) or y - k < 1:
            return
        if k % perle == 0 or k == L:
            art = int(w.rng.random() * 3)
            blk = froschlicht(w, ["pearlescent", "verdant"][art]) if art < 2 else w.b("sea_lantern")
        else:
            blk = w.b(farben[int(w.rng.random() * len(farben))])
        w.setze(x, y - k, z, blk)


def froschlicht(w, art="pearlescent"):
    return w.b(f"{art}_froglight", axis="y")


def laubball(w, cx, cy, cz, r, arten=("azalea_leaves", "flowering_azalea_leaves"), dicht=0.85):
    rng = w.rng
    for dx in range(-int(r) - 1, int(r) + 2):
        for dy in range(-int(r * 0.7) - 1, int(r * 0.7) + 2):
            for dz in range(-int(r) - 1, int(r) + 2):
                if dx * dx + (dy / 0.7) ** 2 + dz * dz <= r * r and rng.random() < dicht:
                    w.setze(round(cx + dx), round(cy + dy), round(cz + dz),
                            w.b(arten[int(rng.random() * len(arten))], persistent=True, distance=1,
                                waterlogged=False), False)


def holz(w, art, ax="y"):
    return w.b(f"{art}_wood", axis=ax) if art not in ("warped", "crimson") else w.b(f"{art}_hyphae", axis=ax)


def baum_aeste(w, x, z, H, n, laenge, art, r0, rng, steigung=0.4, start=0.55):
    """Stamm mit Ästen; gibt Astenden zurück."""
    top = (x + (rng.random() - 0.5) * 2, H, z + (rng.random() - 0.5) * 2)
    rohr(w, bez((x, -1, z), (x, H * 0.5, z), top), r0, r0 * 0.5, holz(w, art))
    enden = [top]
    for k in range(n):
        a = k / n * 6.283 + rng.random() * 0.6
        y0 = H * (start + (1 - start) * rng.random())
        L = laenge * (0.7 + 0.5 * rng.random())
        e = (x + math.cos(a) * L, y0 + L * steigung, z + math.sin(a) * L)
        m = (x + math.cos(a) * L * 0.5, y0 + L * steigung * 1.2, z + math.sin(a) * L * 0.5)
        rohr(w, bez((x, y0, z), m, e), r0 * 0.5, max(0.5, r0 * 0.2), holz(w, art))
        enden.append(e)
    return enden


# ============================================================================ Gewächse

def laternenbaum(seed, g=1):
    """Laternenbaum: ein knorriger Baum mit weit ausladenden Ästen, an denen an Ketten leuchtende Frucht-
    Laternen hängen, dazu Azaleenlaub und leuchtende Flechten am Stamm."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 9 * s + 3)
    enden = baum_aeste(w, 0, 0, 12 * s + 4, 5 + g, 8 * s + 2, "dark_oak", 1.6 * s + 0.6, rng, steigung=0.25)
    for (x, y, z) in enden:
        laubball(w, x, y + 1, z, 2.5 * s + 1.2)
        for k in range(2 + g):
            hx, hz = round(x + (rng.random() - 0.5) * 4 * s), round(z + (rng.random() - 0.5) * 4 * s)
            hy = round(y) - 1
            L = 2 + int(rng.random() * 4 * s)
            for i in range(L):
                if w.frei(hx, hy - i, hz):
                    w.setze(hx, hy - i, hz, w.b("chain", axis="y", waterlogged=False), False)
            art = ["ochre", "pearlescent", "verdant"][int(rng.random() * 3)]
            if w.frei(hx, hy - L, hz):
                w.setze(hx, hy - L, hz, froschlicht(w, art), False)
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) == "minecraft:dark_oak_wood" and rng.random() < 0.08 and w.frei(x + 1, y, z):
            w.setze(x + 1, y, z, w.b("glow_lichen", west=True, east=False, north=False, south=False, up=False,
                                     down=False, waterlogged=False))
    return w


def quallenbaum(seed, g=1):
    """Quallenbaum: aus einem bleichen, verdrehten Stamm wachsen Stiele mit glockenförmigen Glasschirmen wie
    Quallen, in jedem ein Leuchtkern, darunter hängen schimmernde Fangfäden."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 8 * s + 3)
    enden = baum_aeste(w, 0, 0, 10 * s + 4, 3 + g, 6 * s + 2, "birch", 1.2 * s + 0.5, rng, steigung=0.8)
    for (x, y, z) in enden:
        r = 2.5 * s + 1.5
        f = GLAS[2 + int(rng.random() * 2)]
        for dx in range(-int(r) - 1, int(r) + 2):
            for dy in range(0, int(r) + 2):
                for dz in range(-int(r) - 1, int(r) + 2):
                    d = math.sqrt(dx * dx + (dy * 1.25) ** 2 + dz * dz)
                    if r - 1.1 < d <= r:
                        w.setze(round(x + dx), round(y + dy), round(z + dz), w.b(f), False)
        kugel(w, x, y + r * 0.35, z, max(0.8, r * 0.3), froschlicht(w, "pearlescent"))
        for k in range(int(5 + 4 * s)):
            a = rng.random() * 6.283
            rr = r * (0.6 + 0.35 * rng.random())
            hx, hz = round(x + math.cos(a) * rr), round(z + math.sin(a) * rr)
            strang(w, hx, round(y), hz, int(2 + rng.random() * 5 * s), ["magenta_stained_glass", "pink_stained_glass"],
                   perle=4)
    return w


def leuchtfarn(seed, g=1):
    """Leuchtfarn-Riese: ein Kranz riesiger, eingerollter Farnwedel aus grünem Glas und Laub, die Spitzen und
    Fiederenden leuchten hellgrün."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 9 * s + 3)
    n = 9 + g * 2
    for k in range(n):
        a = k / n * 6.283 + rng.random() * 0.3
        L = (8 + rng.random() * 4) * s + 2
        ca, sa = math.cos(a), math.sin(a)
        p0 = (0, 0, 0)
        p1 = (ca * L * 0.3, L * 0.9, sa * L * 0.3)
        p2 = (ca * L * 0.9, L * 0.75, sa * L * 0.9)
        p3 = (ca * L * 1.1, L * 0.35, sa * L * 1.1)
        pts = bez(p0, p1, p2, p3)
        rohr(w, pts, 0.6 * s + 0.4, 0.3 * s + 0.3, w.b("green_terracotta"))
        for (x, y, z, t) in pts[::2]:
            if t < 0.15:
                continue
            l = (1 - t) * 2.5 * s + 0.8
            for sg in (-1, 1):
                for i in range(1, int(l) + 1):
                    px, pz = round(x - sa * sg * i), round(z + ca * sg * i)
                    w.setze(px, round(y) - (i > l * 0.6), pz,
                            w.b("lime_stained_glass" if i < l else "verdant_froglight", **({"axis": "y"} if i >= l
                                                                                            else {})), False)
        x, y, z, _ = pts[-1]
        kugel(w, x, y, z, 0.8 * s + 0.4, froschlicht(w, "verdant"))
    return w


def sternblumen(seed, g=1):
    """Sternblumen-Hain: riesige Blumen auf geschwungenen Stielen mit fünf weißen, rosa und hellblauen
    Blütenblättern und leuchtend gelbem Herz, Leuchtgras dazwischen."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 10 * s + 3)
    farben = [("white_concrete", "white_terracotta"), ("pink_concrete", "pink_terracotta"),
              ("light_blue_concrete", "light_blue_terracotta")]
    n = 4 + g * 2
    for k in range(n):
        a = rng.random() * 6.283
        d = 0 if k == 0 else (3 + rng.random() * 7) * s
        bx, bz = math.cos(a) * d, math.sin(a) * d
        H = (6 + rng.random() * 8) * s + 3
        top = (bx + (rng.random() - 0.5) * 3 * s, H, bz + (rng.random() - 0.5) * 3 * s)
        rohr(w, bez((bx, 0, bz), (bx, H * 0.6, bz + 2 * s), top), 0.5 * s + 0.4, 0.4 * s + 0.3,
             w.b("lime_terracotta"))
        f = farben[k % 3]
        R = 2.6 * s + 1.4
        for p in range(5):
            pa = p / 5 * 6.283 + rng.random()
            for i in range(int(R * 3)):
                t = i / (R * 3)
                rr = R * t
                breit = math.sin(math.pi * t) * R * 0.45 + 0.4
                for q in np.arange(-breit, breit + 0.01, 0.5):
                    x = top[0] + math.cos(pa) * rr - math.sin(pa) * q
                    z = top[2] + math.sin(pa) * rr + math.cos(pa) * q
                    y = top[1] + t * t * R * 0.4
                    w.setze(round(x), round(y), round(z), w.b(f[0] if abs(q) < breit * 0.6 else f[1]), False)
        kugel(w, top[0], top[1] + 0.5, top[2], 0.8 * s + 0.5, froschlicht(w, "ochre"))
    return w


def glimmerbogen(seed, g=1):
    """Glimmerbogen: zwei bemooste Rankenstränge winden sich zu einem Torbogen, aus dem leuchtende Beerenranken
    und Glasperlen-Schnüre herabhängen."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 9 * s + 3)
    B = 10 * s + 4
    for k in range(2):
        pts = []
        for i in range(int(B * 8)):
            t = i / (B * 8)
            x = -B / 2 + B * t
            y = math.sin(math.pi * t) * B * 0.85
            ph = t * 6.283 * 2 + k * math.pi
            pts.append((x, y + math.sin(ph) * 0.9 * s, math.cos(ph) * 0.9 * s, t))
        rohr(w, pts, 0.8 * s + 0.4, 0.8 * s + 0.4, lambda *_: w.b("moss_block" if rng.random() < 0.6 else
                                                                   "mangrove_wood", axis="y"))
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 3 and w.frei(x, y - 1, z) and rng.random() < 0.07 and w.P.name(b) in ("minecraft:moss_block",
                                                                                      "minecraft:mangrove_wood"):
            L = 1 + int(rng.random() * 3 * s)
            for i in range(1, L + 1):
                if not w.frei(x, y - i, z) or y - i < 1:
                    break
                w.setze(x, y - i, z, w.b("cave_vines", age=25, berries=True) if i == L else
                        w.b("cave_vines_plant", berries=rng.random() < 0.5))
    return w


def seelenlichtbaum(seed, g=1):
    """Seelenlichtbaum: ein türkisblättriger Baum mit wirrem Stamm, an seinen Ästen hängen Seelenlaternen, im
    Kreis um die Wurzeln brennen blaue Seelenfeuer."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 9 * s + 3)
    enden = baum_aeste(w, 0, 0, 11 * s + 4, 4 + g, 6 * s + 2, "warped", 1.4 * s + 0.6, rng, steigung=0.5)
    for (x, y, z) in enden:
        laubball(w, x, y + 1, z, 2.6 * s + 1.2, ("warped_wart_block", "warped_wart_block", "shroomlight"))
        for k in range(2 + g):
            hx, hz = round(x + (rng.random() - 0.5) * 4 * s), round(z + (rng.random() - 0.5) * 4 * s)
            hy = round(y - 1)
            while hy > 2 and not w.frei(hx, hy, hz):
                hy -= 1
            if hy > 3:
                w.setze(hx, hy, hz, w.b("chain", axis="y", waterlogged=False), False)
                w.setze(hx, hy - 1, hz, w.b("soul_lantern", hanging=True, waterlogged=False), False)
    R = 6 * s + 2
    for k in range(int(10 * s) + 6):
        a = k / (int(10 * s) + 6) * 6.283
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        w.setze(x, 0, z, w.b("soul_soil"))
        w.setze(x, 1, z, w.b("soul_fire"))
    return w


def kristallblaetterbaum(seed, g=1):
    """Kristallblätterbaum: ein weißer Baum, dessen Blätterwolken aus hell- und türkisblauem Glas bestehen, in
    jeder Wolke glimmt ein Meereslaternen-Kern."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 8 * s + 3)
    enden = baum_aeste(w, 0, 0, 11 * s + 4, 4 + g, 6 * s + 2, "birch", 1.3 * s + 0.6, rng, steigung=0.6)
    for (x, y, z) in enden:
        r = 2.6 * s + 1.3
        laubball(w, x, y + 1, z, r, ("light_blue_stained_glass", "cyan_stained_glass", "white_stained_glass"), 0.9)
        kugel(w, x, y + 1, z, max(0.7, r * 0.3), w.b("sea_lantern"))
    return w


def schwammsaeulen(seed, g=1):
    """Leuchtschwamm-Säulen: eine Gruppe hohler, poröser Röhren in Gelb und Orange wie Meeresschwämme an Land,
    oben glühen ihre Ränder."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 8 * s + 3)
    n = 5 + g * 2
    for k in range(n):
        a = rng.random() * 6.283
        d = 0 if k == 0 else (2 + rng.random() * 5) * s
        cx, cz = math.cos(a) * d, math.sin(a) * d
        H = (5 + rng.random() * 9) * s + 2
        r = (1.2 + rng.random() * 1.2) * s + 0.8
        for y in range(0, int(H) + 1):
            rr = r * (1 + 0.15 * math.sin(y * 0.8))
            for dx in range(-int(rr) - 1, int(rr) + 2):
                for dz in range(-int(rr) - 1, int(rr) + 2):
                    dd = math.hypot(dx, dz)
                    if rr - 1.1 < dd <= rr and rng.random() < 0.92:
                        top = y >= int(H) - 0
                        w.setze(round(cx + dx), y, round(cz + dz),
                                w.b("shroomlight") if top else
                                w.b(["sponge", "wet_sponge", "orange_terracotta", "yellow_terracotta"]
                                    [int(rng.random() * 4)]))
    return w


def spiralbaum(seed, g=1):
    """Spiralbaum: zwei Mangrovenstränge drehen sich spiralförmig zum Himmel, an den Kreuzungen sitzen leuchtende
    Perlknoten, oben eine schraubig gewundene Laubkrone."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 7 * s + 3)
    H = 14 * s + 5
    for k in range(2):
        pts = []
        for i in range(int(H * 4)):
            t = i / (H * 4)
            a = t * 6.283 * 2.2 + k * math.pi
            rr = (2.2 * s + 1.2) * (1 - 0.45 * t)
            pts.append((math.cos(a) * rr, t * H, math.sin(a) * rr, t))
        rohr(w, pts, 0.6 * s + 0.35, 0.3 * s + 0.3, holz(w, "mangrove"))
        for i in range(0, len(pts), int(H * 4 / 9)):
            x, y, z, t = pts[i]
            w.setze(round(x), round(y), round(z), froschlicht(w, "pearlescent"))
    for i in range(int(H * 2)):
        t = i / (H * 2)
        a = t * 6.283 * 2
        rr = (5 * s + 2) * math.sin(math.pi * t)
        laubball(w, math.cos(a) * rr, H + t * 5 * s - 1, math.sin(a) * rr, 1.2 * s + 0.6,
                 ("mangrove_leaves", "azalea_leaves", "flowering_azalea_leaves"))
    return w


def leuchtmooslichtung(seed, g=1):
    """Leuchtmoos-Lichtung: eine kleine Waldlichtung mit moosigen Findlingen voller Leuchtflechten, umgestürzten
    Baumstämmen, kleinen Leuchtpilzen und Birken am Rand."""
    import wald2
    from lib import einfuegen
    w = _welt(seed)
    s, rng = S[g], w.rng
    R = 10 * s + 4
    _boden(w, R)
    for k in range(4 + g * 2):
        a = rng.random() * 6.283
        d = rng.random() * R * 0.7
        cx, cz = math.cos(a) * d, math.sin(a) * d
        r = (1 + rng.random() * 1.5) * s + 0.6
        kugel(w, cx, 0.5, cz, r, lambda *_: w.b(["mossy_cobblestone", "stone", "moss_block"]
                                               [int(rng.random() * 3)]), ry=r * 0.7)
    for (x, y, z), b in list(w.bloecke.items()):
        if y >= 1 and rng.random() < 0.35:
            for (dx, dz, sname, gs) in ((1, 0, "west", "east"), (-1, 0, "east", "west"), (0, 1, "north", "south"),
                                        (0, -1, "south", "north")):
                if w.frei(x + dx, y, z + dz) and rng.random() < 0.4:
                    w.setze(x + dx, y, z + dz, w.b("glow_lichen", **{k: k == sname for k in
                                                                     ("north", "south", "east", "west")},
                                                   up=False, down=False, waterlogged=False), False)
    for k in range(1 + g):
        a = rng.random() * 3.14
        L = (5 + rng.random() * 4) * s
        x0, z0 = (rng.random() - 0.5) * R, (rng.random() - 0.5) * R
        rohr(w, bez((x0, 1, z0), (x0 + math.cos(a) * L / 2, 1.3, z0 + math.sin(a) * L / 2),
                    (x0 + math.cos(a) * L, 1, z0 + math.sin(a) * L)), 0.8 * s + 0.4, 0.7 * s + 0.4,
             w.b("oak_wood", axis="x"), ueber=False)
    for k in range(int(8 * s) + 4):
        x, z = round((rng.random() - 0.5) * R * 1.4), round((rng.random() - 0.5) * R * 1.4)
        if w.frei(x, 1, z) and not w.frei(x, 0, z):
            w.setze(x, 1, z, w.b("mushroom_stem", up=False, down=False, north=True, south=True, east=True, west=True))
            w.setze(x, 2, z, w.b("shroomlight"))
    for k in range(3 + g * 2):
        a = k / (3 + g * 2) * 6.283
        x, z = round(math.cos(a) * R * 0.95), round(math.sin(a) * R * 0.95)
        if w.frei(x, 1, z):
            einfuegen(w, wald2.birke(seed + k), x, 0, z)
    return w


def schirmbaum(seed, g=1):
    """Schirmbaum: ein schlanker, hoher Stamm trägt ein flaches, weit gespanntes Blätterdach, dessen Unterseite mit
    leuchtenden Punkten übersät ist, Leuchtfäden hängen vom Rand."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 9 * s + 3)
    H = 14 * s + 5
    rohr(w, bez((0, -1, 0), (1 * s, H * 0.5, -1 * s), (0, H, 0)), 1.1 * s + 0.5, 0.6 * s + 0.4, holz(w, "acacia"))
    R = 8 * s + 3
    for k in range(5):
        a = k / 5 * 6.283
        rohr(w, bez((0, H - 2, 0), (math.cos(a) * R * 0.4, H, math.sin(a) * R * 0.4),
                    (math.cos(a) * R * 0.8, H + 0.5, math.sin(a) * R * 0.8)), 0.5 * s + 0.3, 0.3, holz(w, "acacia"))
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            d = math.hypot(x, z)
            if d <= R:
                y = round(H + 1 + (1 - (d / R) ** 2) * 1.5 * s)
                w.setze(x, y, z, w.b("acacia_leaves" if rng.random() < 0.8 else "azalea_leaves", persistent=True,
                                     distance=1, waterlogged=False), False)
                w.setze(x, y + 1, z, w.b("acacia_leaves", persistent=True, distance=1, waterlogged=False), False) \
                    if d < R * 0.7 else None
                if rng.random() < 0.08 and w.frei(x, y - 1, z):
                    w.setze(x, y - 1, z, froschlicht(w, "ochre"), False)
                if d > R - 1.2 and rng.random() < 0.2:
                    strang(w, x, y, z, int(2 + rng.random() * 5 * s), ["yellow_stained_glass", "orange_stained_glass"],
                           perle=3)
    return w


def perlenbaum(seed, g=1):
    """Perlenbaum: ein feingliedriger, silbriger Baum, an dessen Zweigspitzen schimmernde Perlenkugeln in
    verschiedenen Größen hängen."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 8 * s + 3)
    enden = baum_aeste(w, 0, 0, 10 * s + 4, 6 + g * 2, 6 * s + 2, "birch", 1.0 * s + 0.5, rng, steigung=0.7,
                       start=0.4)
    for (x, y, z) in enden:
        for k in range(2):
            a = rng.random() * 6.283
            e = (x + math.cos(a) * 2 * s, y + 1.5 * s, z + math.sin(a) * 2 * s)
            rohr(w, bez((x, y, z), (x, y + 2 * s, z), e), 0.4, 0.4, w.b("stripped_birch_wood", axis="y"))
            kugel(w, e[0], e[1] - 0.5, e[2], (0.7 + rng.random() * 0.9) * s + 0.4,
                  froschlicht(w, "pearlescent") if rng.random() < 0.7 else w.b("white_stained_glass"))
    return w


def leuchtkelche(seed, g=1):
    """Leuchtkelche: hohe, trichterförmige Pflanzenkelche aus Prismarin und Türkis, in ihren Schalen steht
    leuchtendes Wasser, unten wachsen Leuchtgräser."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 8 * s + 3)
    for k in range(3 + g * 2):
        a = rng.random() * 6.283
        d = 0 if k == 0 else (3 + rng.random() * 5) * s
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        H = int((5 + rng.random() * 8) * s + 3)
        for y in range(0, H):
            w.setze(cx, y, cz, w.b("dark_prismarine"))
        R = int((2 + rng.random() * 1.5) * s + 1.5)
        for k2 in range(R + 1):
            rr = k2 + 0.5
            for dx in range(-R - 1, R + 2):
                for dz in range(-R - 1, R + 2):
                    dd = math.hypot(dx, dz)
                    y = H + k2
                    if rr - 1 < dd <= rr:
                        w.setze(cx + dx, y, cz + dz, w.b("prismarine" if k2 < R else "cyan_terracotta"))
                    elif dd <= rr - 1 and k2 == 0:
                        w.setze(cx + dx, y, cz + dz, w.b("sea_lantern"))
                    elif dd <= rr - 1 and k2 > 0:
                        w.setze(cx + dx, y, cz + dz, w.b("water", level=0))
    return w


def lichtorgel(seed, g=1):
    """Lichtorgel: dicht stehende, unterschiedlich hohe Röhren aus Amethyst und Purpur wie Orgelpfeifen in einem
    Bogen, auf jeder Röhre ein leuchtender Stab."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 8 * s + 3)
    n = 9 + g * 3
    for k in range(n):
        a = math.pi * (0.15 + 0.7 * k / (n - 1))
        R = 5 * s + 2
        cx, cz = round(math.cos(a) * R), round(-math.sin(a) * R * 0.6)
        H = int((4 + 10 * math.sin(math.pi * k / (n - 1)) + rng.random() * 2) * s + 2)
        r = 0.9 * s + 0.6
        for y in range(0, H):
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    dd = math.hypot(dx, dz)
                    if dd <= r:
                        w.setze(cx + dx, y, cz + dz, w.b("amethyst_block" if (y // 3 + k) % 2 else "purpur_block")
                                if dd > r - 1 else w.b("air"))
        w.setze(cx, H, cz, w.b("end_rod", facing="up"))
        w.setze(cx, H - 1, cz, w.b("pearlescent_froglight", axis="y"))
    return w


def seerosenteich(seed, g=1):
    """Leuchtender Seerosenteich: in einem dunklen Teich treiben riesige, eingekerbte Seerosenblätter, auf einigen
    sitzen rosa Glasknospen mit Leuchtkern, Leuchtschilf am Ufer."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    R = 9 * s + 3
    _boden(w, R + 3)
    for x in range(-int(R), int(R) + 1):
        for z in range(-int(R), int(R) + 1):
            if math.hypot(x, z) <= R:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("water", level=0))
                w.setze(x, -2, z, w.b("mud"))
                w.bloecke.pop((x, 1, z), None)
    for k in range(3 + g * 2):
        a = rng.random() * 6.283
        d = rng.random() * R * 0.6
        cx, cz = math.cos(a) * d, math.sin(a) * d
        r = (1.5 + rng.random() * 1.5) * s + 1
        kerbe = rng.random() * 6.283
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                dd = math.hypot(x, z)
                ang = (math.atan2(z, x) - kerbe) % 6.283
                if dd <= r and not (ang < 0.5 and dd > 0.6):
                    w.setze(round(cx + x), 1, round(cz + z), w.b("lime_carpet" if dd < r - 0.8 else "green_carpet"))
        if rng.random() < 0.7:
            kugel(w, cx, 2.5 * s + 1.2, cz, 1.0 * s + 0.6, w.b("pink_stained_glass"), hohl=True)
            w.setze(round(cx), round(2.5 * s + 1.2), round(cz), froschlicht(w, "pearlescent"))
    for k in range(int(10 * s) + 6):
        a = rng.random() * 6.283
        x, z = round(math.cos(a) * (R + 1)), round(math.sin(a) * (R + 1))
        if w.frei(x, 1, z):
            for y in range(1, 2 + int(rng.random() * 3)):
                w.setze(x, y, z, w.b("sugar_cane", age=0))
            w.setze(x, 4, z, w.b("end_rod", facing="up")) if rng.random() < 0.3 else None
    return w


def nachtbluetenbusch(seed, g=1):
    """Nachtblütenbusch: ein großer, kuppelförmiger Busch aus dunklem Laub, über und über mit leuchtenden Blüten in
    Rosa, Violett und Grün besetzt, Blütenblätter am Boden."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 8 * s + 3)
    for k in range(1 + g):
        a = rng.random() * 6.283
        d = 0 if k == 0 else 5 * s
        cx, cz = math.cos(a) * d, math.sin(a) * d
        R = (4 + rng.random() * 2) * s + 1.5
        laubball(w, cx, R * 0.4, cz, R, ("dark_oak_leaves", "azalea_leaves", "dark_oak_leaves"), 0.95)
        for (x, y, z), b in list(w.bloecke.items()):
            if w.P.name(b).endswith("_leaves") and w.frei(x, y + 1, z) and rng.random() < 0.18:
                w.setze(x, y, z, [froschlicht(w, "pearlescent"), froschlicht(w, "verdant"), w.b("pink_stained_glass"),
                                  w.b("magenta_stained_glass")][int(rng.random() * 4)])
    for (x, y, z), b in list(w.bloecke.items()):
        if y == 0 and w.frei(x, 1, z) and rng.random() < 0.2:
            w.setze(x, 1, z, w.b("pink_petals", facing="north", flower_amount=1 + int(rng.random() * 4)))
    return w


def pilzturm(seed, g=1):
    """Pilzturm: ein abgestorbener, hoher Baumstumpf, an dem sich spiralförmig leuchtende Konsolenpilze bis zur
    Spitze emporwinden, oben ein Schopf aus Pilzlicht."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 7 * s + 3)
    H = 12 * s + 4
    rohr(w, bez((0, -1, 0), (0.5, H * 0.5, 0.5), (0, H, 0)), 1.8 * s + 0.6, 1.2 * s + 0.5, holz(w, "spruce"))
    n = int(8 + 6 * s)
    for k in range(n):
        t = k / n
        a = t * 6.283 * 2.2
        y = 2 + t * (H - 3)
        rr = (1.8 * s + 0.6) * (1 - 0.35 * t) + 0.5
        cx, cz = math.cos(a) * rr, math.sin(a) * rr
        R = (1.6 - 0.6 * t) * s + 1
        for x in range(-int(R) - 1, int(R) + 2):
            for z in range(-int(R) - 1, int(R) + 2):
                if math.hypot(x, z) <= R and (x * math.cos(a) + z * math.sin(a)) >= -0.3:
                    w.setze(round(cx + x + math.cos(a) * R * 0.6), round(y), round(cz + z + math.sin(a) * R * 0.6),
                            w.b("shroomlight") if math.hypot(x, z) > R - 0.8 else
                            w.b("brown_mushroom_block", up=True, down=False, north=True, south=True, east=True,
                                west=True), False)
    kugel(w, 0, H + 1, 0, 1.5 * s + 0.8, w.b("shroomlight"))
    return w


def tentakelpflanze(seed, g=1):
    """Tentakelpflanze: aus einer violetten Knolle schwingen sich acht lange, sich verjüngende Fangarme empor,
    gesäumt von leuchtenden Saugnäpfen, die Spitzen glühen magentafarben."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 8 * s + 3)
    kugel(w, 0, 1.5 * s, 0, 2.5 * s + 1, lambda *_: w.b(["purple_terracotta", "magenta_terracotta"]
                                                       [int(rng.random() * 2)]), ry=2 * s + 1)
    for k in range(8):
        a = k / 8 * 6.283
        L = (9 + rng.random() * 6) * s + 3
        ca, sa = math.cos(a), math.sin(a)
        pts = bez((ca * s, 2 * s, sa * s), (ca * L * 0.2, L * 0.8, sa * L * 0.2),
                  (ca * L * 0.7, L * 0.9, sa * L * 0.7), (ca * L * 0.8 - sa * 2, L * 0.5, sa * L * 0.8 + ca * 2))
        rohr(w, pts, 0.9 * s + 0.4, 0.3, lambda x, y, z, t: w.b("purple_concrete" if t < 0.85 else
                                                               "magenta_stained_glass"))
        for (x, y, z, t) in pts[::3]:
            if 0.15 < t < 0.9:
                w.setze(round(x + ca * 0.6), round(y), round(z + sa * 0.6), froschlicht(w, "pearlescent"), False)
        x, y, z, _ = pts[-1]
        w.setze(round(x), round(y), round(z), froschlicht(w, "pearlescent"))
    return w


def lampionblumen(seed, g=1):
    """Lampionblumen: geschwungene Stängel tragen hängende, laternenförmige Blüten aus orangem Glas, in jeder
    glimmt ein warmes Licht – wie ein Feld voller Papierlaternen."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 9 * s + 3)
    for k in range(5 + g * 3):
        a = rng.random() * 6.283
        d = rng.random() * 6 * s
        bx, bz = math.cos(a) * d, math.sin(a) * d
        H = (4 + rng.random() * 5) * s + 3
        b2 = rng.random() * 6.283
        ende = (bx + math.cos(b2) * 3 * s, H, bz + math.sin(b2) * 3 * s)
        pts = bez((bx, 0, bz), (bx, H * 1.1, bz), ende)
        rohr(w, pts, 0.4 * s + 0.3, 0.3, w.b("green_terracotta"))
        x, y, z = ende
        r = 1.1 * s + 0.8
        kugel(w, x, y - r - 1, z, r, lambda *_: w.b("orange_stained_glass" if rng.random() < 0.7 else
                                                    "red_stained_glass"), hohl=True, ry=r * 1.3)
        w.setze(round(x), round(y - r - 1), round(z), w.b("shroomlight"))
        w.setze(round(x), round(y - 1), round(z), w.b("green_terracotta"))
    return w


def herz_des_waldes(seed, g=1):
    """Herz des Waldes: gewaltige Wurzeln wachsen aus dem Boden und umklammern ein riesiges, pulsierend leuchtendes
    Kristallherz aus rosa und rotem Glas."""
    w = _welt(seed)
    s, rng = S[g], w.rng
    _boden(w, 10 * s + 3)
    R = 4 * s + 2
    yc = R + 3 * s + 2
    for dx in range(-int(R) - 2, int(R) + 3):
        for dy in range(-int(R * 1.3) - 2, int(R) + 3):
            for dz in range(-int(R) - 2, int(R) + 3):
                x, y = dx / R, dy / R
                herz = (x * x + y * y - 1) ** 3 - x * x * y ** 3 * 1.0 <= 0 and abs(dz / R) <= 0.65 * (1 - y * y * 0.2)
                if herz:
                    innen = (x * x + y * y + (dz / R / 0.65) ** 2) < 0.35
                    w.setze(dx, round(yc + dy), dz, w.b("shroomlight") if innen else
                            w.b("pink_stained_glass" if rng.random() < 0.6 else "red_stained_glass"))
    for k in range(6 + g):
        a = k / (6 + g) * 6.283
        p0 = (math.cos(a) * R * 2.2, -1, math.sin(a) * R * 1.4)
        p1 = (math.cos(a) * R * 1.8, yc * 0.6, math.sin(a) * R * 1.2)
        p2 = (math.cos(a) * R * 0.9, yc + R * 0.4, math.sin(a) * R * 0.7)
        p3 = (math.cos(a) * R * 0.2, yc + R * 1.0, math.sin(a) * R * 0.3)
        rohr(w, bez(p0, p1, p2, p3), 0.9 * s + 0.5, 0.3, holz(w, "dark_oak"), ueber=False)
    return w


LEUCHTWALD2 = {
    "laternenbaum": ("Froschlicht-Laternenbaum", laternenbaum),
    "quallenbaum": ("Quallenbaum", quallenbaum),
    "leuchtfarn": ("Leuchtfarn-Riese", leuchtfarn),
    "sternblumen": ("Sternblumen-Hain", sternblumen),
    "glimmerbogen": ("Glimmerbogen", glimmerbogen),
    "seelenlichtbaum": ("Seelenlichtbaum", seelenlichtbaum),
    "kristallblaetterbaum": ("Kristallblätterbaum", kristallblaetterbaum),
    "schwammsaeulen": ("Leuchtschwamm-Säulen", schwammsaeulen),
    "spiralbaum": ("Spiralbaum", spiralbaum),
    "leuchtmooslichtung": ("Leuchtmoos-Lichtung", leuchtmooslichtung),
    "schirmbaum": ("Schirmbaum", schirmbaum),
    "perlenbaum": ("Perlenbaum", perlenbaum),
    "leuchtkelche": ("Leuchtkelche", leuchtkelche),
    "lichtorgel": ("Lichtorgel", lichtorgel),
    "seerosenteich": ("Leuchtender Seerosenteich", seerosenteich),
    "nachtbluetenbusch": ("Nachtblütenbusch", nachtbluetenbusch),
    "pilzturm": ("Pilzturm", pilzturm),
    "tentakelpflanze": ("Tentakelpflanze", tentakelpflanze),
    "lampionblumen": ("Lampionblumen", lampionblumen),
    "herz_des_waldes": ("Herz des Waldes", herz_des_waldes),
}

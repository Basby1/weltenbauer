"""Pilzwelten – Riesenpilze aller Formen (Fliegenpilz, Steinpilz, Parasol, Pfifferling, Morchel, Tintling …),
Pilzbauten (Wirtshaus, Pilzturm, Pilzdorf, Brücke, Thron) und kombinierbare Pilzwälder.
Fuß auf y = 1 (Boden y = 0)."""

from __future__ import annotations

import math

from flora import SZ, _neu, _r, _stil, linie
from lib import Rauschen
from wald import Stueck, _fertig, hohes, leuchtflechte

ALLE = dict(up=True, down=True, north=True, south=True, east=True, west=True)


def pblk(w, name):
    if name in ("red_mushroom_block", "brown_mushroom_block", "mushroom_stem"):
        return w.b(name, **ALLE)
    if name in ("crimson_stem", "warped_stem", "bone_block", "stripped_birch_log", "birch_log"):
        return w.b(name, axis="y")
    return w.b(name)


# ============================================================================ Bausteine

def stiel(w, x0, z0, y0, H, r0, r1=None, mat="mushroom_stem", krumm=0.0, richtung=0.0, knolle=0.0, ring=None,
          ring_farbe="white_wool", rauh=None):
    """Pilzstiel (verjüngt, leicht gebogen) mit Knolle und Ring. Gibt Spitze (x, y, z) zurück."""
    r1 = r0 * 0.8 if r1 is None else r1
    rn = rauh or Rauschen(w, 1.5)
    cx = cz = 0.0
    for k in range(H):
        t = k / max(1, H - 1)
        cx = x0 + math.cos(richtung) * krumm * math.sin(t * math.pi * 0.5) * H * 0.25
        cz = z0 + math.sin(richtung) * krumm * math.sin(t * math.pi * 0.5) * H * 0.25
        r = r0 + (r1 - r0) * t + knolle * max(0, 1 - t * 5)
        y = y0 + k
        for dx in range(-int(r) - 1, int(r) + 2):
            for dz in range(-int(r) - 1, int(r) + 2):
                if (dx + cx - round(cx)) ** 2 + (dz + cz - round(cz)) ** 2 <= r * r + 0.25:
                    m = mat(dx, y, dz) if callable(mat) else mat
                    w.setze(round(cx) + dx, y, round(cz) + dz, pblk(w, m))
        if ring is not None and abs(t - ring) < 0.5 / H:
            for dx in range(-int(r) - 3, int(r) + 4):
                for dz in range(-int(r) - 3, int(r) + 4):
                    d = math.hypot(dx, dz)
                    if r < d <= r + 1.6:
                        w.setze(round(cx) + dx, y, round(cz) + dz, pblk(w, ring_farbe))
                    elif r + 1.6 < d <= r + 2.2:
                        w.setze(round(cx) + dx, y - 1, round(cz) + dz, pblk(w, ring_farbe))
    return (round(cx), y0 + H, round(cz))


def hut(w, cx, cy, cz, R, H, form="kuppel", farbe="red_mushroom_block", punkte=None, punkt_dichte=0.18,
        lamellen="white_terracotta", rand_farbe=None, dicke=1.5, wellig=0.0, rn=None):
    """Pilzhut als Schale. form: kuppel, flach (Parasol), kegel (Tintling), trichter (Pfifferling), polster (Steinpilz).
    Unterseite mit radialen Lamellen."""
    rn = rn or Rauschen(w, 1.3)
    rp = Rauschen(w, 0.7)
    for x in range(-int(R) - 2, int(R) + 3):
        for z in range(-int(R) - 2, int(R) + 3):
            d = math.hypot(x, z)
            a = math.atan2(z, x)
            Rw = R * (1 + wellig * math.sin(a * 7) * 0.08)
            if d > Rw:
                continue
            s = d / Rw
            if form == "kuppel":
                oben = H * math.sqrt(max(0, 1 - s * s))
                unten = oben - dicke - H * 0.25 * (1 - s)
            elif form == "polster":
                oben = H * (1 - s ** 3) ** 0.5
                unten = -H * 0.15 * (1 - s) ** 0.5
            elif form == "flach":
                oben = H * (1 - s) ** 0.7 * 0.5 + H * 0.15 * max(0, 1 - s * 4)
                unten = oben - dicke
            elif form == "kegel":
                oben = H * (1 - s)
                unten = oben - dicke - 1
            else:
                oben = H * s ** 1.6
                unten = oben - dicke - (1 - s) * H * 0.2
            yo = cy + round(oben)
            yu = cy + round(unten)
            for y in range(yu, yo + 1):
                if y == yo or y == yu or s > 0.9:
                    if y == yu and lamellen and s < 0.95 and form != "trichter":
                        blk = lamellen if (math.degrees(a) % 12) < 6 or rand_farbe is None else rand_farbe
                    elif punkte and y == yo and rp(cx + x, y, cz + z) > 1 - punkt_dichte:
                        blk = punkte
                    elif rand_farbe and s > 0.85:
                        blk = rand_farbe
                    else:
                        blk = farbe(x, y, z, s) if callable(farbe) else farbe
                    w.setze(cx + x, y, cz + z, pblk(w, blk))
    return cy + round(H)


def boden_pilz(st, dichte=0.5, art="wald"):
    if art == "nether":
        belag = [("crimson_nylium", 3), ("warped_nylium", 3), ("netherrack", 1), ("soul_soil", 1)]
        pfl = [("crimson_roots", 3), ("warped_roots", 3), ("crimson_fungus", 1), ("warped_fungus", 1),
               ("nether_sprouts", 2)]
    elif art == "myzel":
        belag = [("mycelium", 6), ("podzol", 2), ("moss_block", 1)]
        pfl = [("brown_mushroom", 3), ("red_mushroom", 2), ("grass", 1), (leuchtflechte, 0.5)]
    else:
        belag = [("podzol", 4), ("grass_block_s", 3), ("moss_block", 2), ("coarse_dirt", 1), ("mycelium", 1)]
        pfl = [("brown_mushroom", 2), ("red_mushroom", 2), ("fern", 3), ("grass", 3), (hohes("large_fern"), 1),
               ("moss_carpet", 1)]
    st.boden(belag, pfl, dichte=dichte)


def einzeln(pilz, R_extra=3, dichte=0.45, art="wald"):
    def f(seed, g=1):
        st = Stueck(seed, g)
        p = pilz(int(seed), SZ[g], _stil(seed))
        xs = [q[0] for q in p.bloecke] + [0]
        zs = [q[2] for q in p.bloecke] + [0]
        st.R = max(4, int(max(-min(xs), max(xs), -min(zs), max(zs)) * 0.85) + R_extra)
        st.stempel(p, 0, 0)
        boden_pilz(st, dichte, art)
        return _fertig(st.w)
    f.__doc__ = pilz.__doc__
    return f


def kleine(w, n, R, rng, arten=("red_mushroom", "brown_mushroom")):
    for k in range(n):
        a = rng.random() * 6.28
        d = R * (0.5 + 0.5 * rng.random())
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if w.frei(x, 1, z):
            w.setze(x, 1, z, w.b(arten[k % len(arten)]))


# ============================================================================ Riesenpilze

def fliegenpilz(seed, s=1.0, stil=0):
    """Fliegenpilz: leuchtend roter, weiß getupfter Hut, weißer Stiel mit hängendem Ring und knolliger Basis,
    dazu zwei junge Fliegenpilze."""
    w = _neu(seed)
    rng = w.rng
    H = _r(10 * s + 3)
    top = stiel(w, 0, 0, 1, H, 1.4 * s + 0.4, 1.0 * s + 0.3, mat="mushroom_stem", krumm=0.4, richtung=rng.random() * 6,
                knolle=1.0 * s, ring=0.75)
    farbe = "red_mushroom_block" if stil == 0 else "orange_concrete"
    hut(w, top[0], top[1] - 1, top[2], 6 * s + 2, 3.5 * s + 1.2, "kuppel", farbe, punkte="white_concrete",
        punkt_dichte=0.2)
    for k in range(2):
        a = k * 2.6 + 1
        x, z = round(math.cos(a) * 5 * s), round(math.sin(a) * 5 * s)
        t = stiel(w, x, z, 1, _r(3 * s + 1), 0.6 * s + 0.2)
        hut(w, t[0], t[1] - 1, t[2], 2 * s + 0.8, 1.8 * s + 0.6, "kuppel", farbe, punkte="white_concrete",
            punkt_dichte=0.25)
    return w


def steinpilz(seed, s=1.0, stil=0):
    """Steinpilz: ein dicker, bauchiger Stiel mit feiner Netzzeichnung und ein mächtiger, polsterförmiger
    kastanienbrauner Hut mit gelblichen Röhren."""
    w = _neu(seed)
    H = _r(7 * s + 2)
    rn = Rauschen(w, 0.8)
    top = stiel(w, 0, 0, 1, H, 2.6 * s + 0.6, 1.6 * s + 0.4,
                mat=lambda x, y, z: "white_terracotta" if rn(x, y, z) > 0.55 else "mushroom_stem", knolle=0.8 * s)
    farbe = "brown_terracotta" if stil == 0 else "brown_mushroom_block"
    hut(w, top[0], top[1] - 1, top[2], 5.5 * s + 2, 3.5 * s + 1, "polster",
        lambda x, y, z, s_: "brown_concrete" if s_ < 0.5 and (x + z) % 3 else farbe, lamellen="yellow_terracotta",
        rand_farbe="brown_mushroom_block")
    return w


def parasol(seed, s=1.0, stil=0):
    """Parasol: ein sehr hoher, schlanker, getigerter Stiel mit beweglichem Ring und ein riesiger, flacher,
    schuppiger Schirm mit dunklem Buckel in der Mitte."""
    w = _neu(seed)
    rn = Rauschen(w, 0.9)
    H = _r(16 * s + 4)
    top = stiel(w, 0, 0, 1, H, 0.9 * s + 0.4, 0.6 * s + 0.3,
                mat=lambda x, y, z: "brown_terracotta" if (y // 2) % 2 else "mushroom_stem", knolle=1.2 * s,
                ring=0.8, ring_farbe="white_terracotta", krumm=0.2)
    hut(w, top[0], top[1] - 1, top[2], 8 * s + 2, 3 * s + 1, "flach",
        lambda x, y, z, s_: "brown_concrete" if s_ < 0.18 else ("brown_terracotta" if rn(x, y, z) > 0.62 else
                                                                 "white_terracotta"),
        lamellen="white_concrete", dicke=1.2)
    return w


def pfifferling(seed, s=1.0, stil=0):
    """Pfifferlinge: drei goldgelbe, trichterförmige Pilze mit gewelltem Rand und herablaufenden Leisten."""
    w = _neu(seed)
    rng = w.rng
    gelb = ["orange_terracotta", "yellow_terracotta", "orange_concrete"] if stil == 0 else \
        ["yellow_concrete", "yellow_terracotta", "white_terracotta"]
    for i in range(3):
        a = i * 2.1
        d = 3.5 * s * (i > 0)
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        H = _r((6 - i * 1.5) * s + 2)
        top = stiel(w, x0, z0, 1, H, 0.7 * s + 0.4, 1.5 * s + 0.5, mat=gelb[1])
        hut(w, top[0], top[1] - 1, top[2], (4.5 - i) * s + 1.5, 2.5 * s + 0.8, "trichter",
            lambda x, y, z, s_: gelb[int(s_ * 2.99)], lamellen=None, wellig=1.0, dicke=1.0)
    return w


def morchel(seed, s=1.0, stil=0):
    """Speisemorchel: ein hoher, wabenartig gekammerter Hut mit tiefen Gruben auf einem hohlen, cremeweißen
    Stiel."""
    w = _neu(seed)
    H = _r(5 * s + 2)
    top = stiel(w, 0, 0, 1, H, 1.8 * s + 0.5, 1.6 * s + 0.4, mat="white_terracotta")
    Hh = _r(10 * s + 3)
    R = 3.0 * s + 1.2
    for y in range(Hh):
        t = y / Hh
        r = R * math.sqrt(max(0, 1 - (t * 1.05) ** 2.2)) * (1 + 0.2 * (1 - t))
        for k in range(int(r * 8) + 6):
            a = k / (r * 8 + 6) * 6.28
            for dr in (0, 1):
                rr = r - dr
                x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
                grube = (math.sin(a * 6 + (y // 2) * 1.3) > 0.35) and ((y // 2) % 2 == 0)
                blk = ("brown_terracotta" if grube else "yellow_terracotta") if stil == 0 else \
                    ("black_terracotta" if grube else "brown_terracotta")
                w.setze(x + top[0], top[1] - 1 + y, z + top[2], w.b(blk if dr == 0 else "brown_terracotta"))
    return w


def tintling(seed, s=1.0, stil=0):
    """Schopftintling: mehrere hohe, walzenförmige Hüte mit zotteligen weißen Schuppen, deren Rand sich in
    schwarze Tinte auflöst und heruntertropft."""
    w = _neu(seed)
    rng = w.rng
    for i in range(3):
        a = i * 2.3 + 0.5
        d = 3 * s * (i > 0)
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        H = _r((5 - i) * s + 2)
        top = stiel(w, x0, z0, 1, H, 0.7 * s + 0.3, 0.6 * s + 0.3, mat="mushroom_stem")
        Hh = _r((9 - i * 2) * s + 3)
        for y in range(-1, Hh):
            t = y / Hh
            r = (1.8 * s + 0.8) * (1 - t ** 3)
            for k in range(int(r * 8) + 6):
                a2 = k / (r * 8 + 6) * 6.28
                x, z = top[0] + round(math.cos(a2) * r), top[2] + round(math.sin(a2) * r)
                if y < 2:
                    blk = "black_concrete"
                elif (k + y) % 4 == 0:
                    blk = "light_gray_wool"
                else:
                    blk = "white_wool"
                w.setze(x, top[1] + y - 2, z, w.b(blk))
        for k in range(int(4 * s)):
            a2 = rng.random() * 6.28
            r = 1.8 * s + 0.8
            x, z = top[0] + round(math.cos(a2) * r), top[2] + round(math.sin(a2) * r)
            for d2 in range(1, 3):
                w.setze(x, top[1] - 3 - d2, z, w.b("black_concrete"), False)
    return w


def hallimasch(seed, s=1.0, stil=0):
    """Hallimasch-Büschel: Dutzende honiggelbe Pilze wachsen dicht gedrängt aus einem moosigen Baumstumpf."""
    w = _neu(seed)
    rng = w.rng
    R = 2.6 * s + 1
    for y in range(1, _r(3 * s + 2) + 1):
        for x in range(-int(R) - 1, int(R) + 2):
            for z in range(-int(R) - 1, int(R) + 2):
                if x * x + z * z <= R * R:
                    w.setze(x, y, z, w.b("oak_log", axis="y") if x * x + z * z > (R - 1.2) ** 2 else
                            w.b("stripped_oak_log", axis="y"))
    ytop = _r(3 * s + 2)
    for k in range(int(10 + 8 * s)):
        a = rng.random() * 6.28
        d = R * (0.4 + 0.9 * rng.random())
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        y0 = ytop + 1 if d < R else 1 + int(rng.integers(0, ytop))
        top = stiel(w, x0, z0, y0, _r((2 + rng.random() * 3) * s), 0.3 * s + 0.2, mat="yellow_terracotta",
                    krumm=0.8, richtung=a)
        hut(w, top[0], top[1] - 1, top[2], (1.2 + rng.random()) * s + 0.5, (0.8 + rng.random() * 0.5) * s + 0.5,
            "kuppel", "orange_terracotta" if stil == 0 else "brown_mushroom_block", punkte="brown_terracotta",
            punkt_dichte=0.15, lamellen="white_terracotta")
    return w


def baumpilze(seed, s=1.0, stil=0):
    """Baumpilze: ein alter abgestorbener Stamm, an dem riesige Zunderschwämme und Schwefelporlinge wie
    Treppenstufen wachsen."""
    w = _neu(seed)
    rng = w.rng
    H = _r(16 * s + 4)
    R = 1.6 * s + 0.8
    for y in range(1, H + 1):
        for x in range(-2, 3):
            for z in range(-2, 3):
                if x * x + z * z <= R * R:
                    w.setze(x, y, z, w.b("dark_oak_log", axis="y") if y < H - 1 else w.b("stripped_dark_oak_log",
                                                                                          axis="y"))
    for k in range(int(6 + 4 * s)):
        y = 2 + int(k * (H - 3) / (6 + 4 * s))
        a = k * 2.2
        L = (2 + rng.random() * 2) * s + 1
        farbe = ["yellow_terracotta", "orange_terracotta", "orange_concrete"] if (k + stil) % 2 else \
            ["brown_terracotta", "light_gray_terracotta", "white_terracotta"]
        for dx in range(-int(L) - 2, int(L) + 3):
            for dz in range(-int(L) - 2, int(L) + 3):
                px = math.cos(a) * dx + math.sin(a) * dz
                pz = -math.sin(a) * dx + math.cos(a) * dz
                if px < 0:
                    continue
                if (px / (L + R)) ** 2 + (pz / (L * 1.2)) ** 2 <= 1:
                    s_ = min(2, int(px / (L + R) * 3))
                    w.setze(dx, y, dz, w.b(farbe[s_]), False)
                    if px > L * 0.3 and (dx + dz) % 2 == 0:
                        w.setze(dx, y - 1, dz, w.b(farbe[-1]), False)
    return w


def leuchtpilz(seed, s=1.0, stil=0):
    """Leuchtpilze: eine Gruppe biolumineszenter Pilze mit von innen glühenden Hüten in Türkis und Grün, deren
    Sporen wie Funken in der Luft schweben."""
    w = _neu(seed)
    rng = w.rng
    glut = ["verdant_froglight", "sea_lantern", "light_blue_concrete"] if stil == 0 else \
        ["pearlescent_froglight", "magenta_concrete", "purple_concrete"]
    for i in range(4):
        a = i * 1.8
        d = 3.2 * s * (i > 0)
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        H = _r((9 - i * 2) * s + 2)
        top = stiel(w, x0, z0, 1, H, 0.8 * s + 0.3, 0.6 * s + 0.2, mat="warped_stem" if stil == 0 else
                    "mushroom_stem", krumm=0.6, richtung=a)
        hut(w, top[0], top[1] - 1, top[2], (4.5 - i) * s + 1, (2.5 - i * 0.4) * s + 1, "kuppel",
            lambda x, y, z, s_: glut[0] if s_ < 0.6 else glut[2], punkte=glut[1], punkt_dichte=0.3,
            lamellen="light_blue_stained_glass" if stil == 0 else "magenta_stained_glass")
    for k in range(int(8 * s)):
        a = rng.random() * 6.28
        d = rng.random() * 6 * s
        w.setze(round(math.cos(a) * d), round(4 + rng.random() * 8 * s), round(math.sin(a) * d),
                w.b("end_rod", facing="up") if stil == 0 else w.b("pearlescent_froglight", axis="y"), False)
    return w


def schleierdame(seed, s=1.0, stil=0):
    """Schleierdame: ein spitzer, olivbrauner Hut, unter dem ein zarter weißer Netzschleier bis zum Boden
    herabfällt."""
    w = _neu(seed)
    H = _r(12 * s + 3)
    top = stiel(w, 0, 0, 1, H, 0.9 * s + 0.3, 0.7 * s + 0.3, mat="mushroom_stem")
    hut(w, top[0], top[1] - 1, top[2], 3 * s + 1, 4 * s + 1.5, "kegel",
        "green_terracotta" if stil == 0 else "brown_terracotta", lamellen=None)
    R0 = 3 * s + 1
    for y in range(2, top[1] - 1):
        t = (top[1] - 1 - y) / (top[1] - 3)
        r = R0 * (0.7 + 0.5 * t)
        for k in range(int(r * 7)):
            a = k / (r * 7) * 6.28
            if (k + y) % 2 == 0:
                w.setze(round(math.cos(a) * r), y, round(math.sin(a) * r),
                        w.b("white_stained_glass_pane", north=True, south=True, east=True, west=True,
                            waterlogged=False) if (k + y) % 4 else w.b("cobweb"))
    return w


def korallenpilz(seed, s=1.0, stil=0):
    """Korallenpilz: ein riesiger, verästelter Ziegenbart in Gold- und Lachstönen, wie eine Koralle am
    Waldboden."""
    w = _neu(seed)
    rng = w.rng
    farbe = ["yellow_terracotta", "orange_terracotta", "yellow_concrete"] if stil == 0 else \
        ["pink_terracotta", "pink_concrete", "white_terracotta"]

    def ast(p, richtung, L, tiefe):
        if tiefe == 0 or L < 1:
            return
        end = (p[0] + richtung[0] * L, p[1] + richtung[1] * L, p[2] + richtung[2] * L)
        linie(w, p, end, w.b(farbe[min(2, 3 - tiefe)]), 0.5 if tiefe >= 3 and s > 1.2 else 0)
        for k in range(2 + (tiefe > 2)):
            a = rng.random() * 6.28
            nr = (richtung[0] * 0.6 + math.cos(a) * 0.5, 0.8, richtung[2] * 0.6 + math.sin(a) * 0.5)
            n = math.sqrt(sum(c * c for c in nr))
            ast(end, tuple(c / n for c in nr), L * 0.7, tiefe - 1)

    for k in range(5):
        a = k / 5 * 6.28
        ast((0, 1, 0), (math.cos(a) * 0.4, 0.9, math.sin(a) * 0.4), 4 * s + 1, 4)
    return w


def bovist(seed, s=1.0, stil=0):
    """Riesenbovist: eine kugelrunde, cremeweiße Pilzkugel so groß wie ein Haus, daneben aufgeplatzte alte
    Boviste, aus denen braune Sporenwolken stäuben."""
    w = _neu(seed)
    rng = w.rng
    R = 5 * s + 1.5
    for x in range(-int(R) - 1, int(R) + 2):
        for y in range(0, int(R * 1.7) + 2):
            for z in range(-int(R) - 1, int(R) + 2):
                if x * x + ((y - R * 0.85) / 0.85) ** 2 + z * z <= R * R and y >= 1:
                    w.setze(x, y, z, w.b("white_terracotta" if (x * 3 + y + z * 5) % 7 else "white_concrete"))
    for k in range(2):
        a = k * 2.5 + 0.8
        cx, cz = round(math.cos(a) * (R + 3 * s)), round(math.sin(a) * (R + 3 * s))
        r = 2 * s + 0.8
        for x in range(-int(r) - 1, int(r) + 2):
            for y in range(0, int(r * 1.5) + 2):
                for z in range(-int(r) - 1, int(r) + 2):
                    d = math.sqrt(x * x + ((y - r * 0.7) / 0.75) ** 2 + z * z)
                    if r - 1.2 < d <= r and y >= 1 and y < r * 1.2:
                        w.setze(cx + x, y, cz + z, w.b("brown_terracotta" if (x + y) % 2 else "brown_concrete"))
        for k2 in range(int(6 * s)):
            p = (cx + rng.integers(-2, 3), round(r * 1.4 + rng.random() * 4 * s), cz + rng.integers(-2, 3))
            w.setze(int(p[0]), int(p[1]), int(p[2]), w.b("brown_stained_glass"), False)
    return w


def giftpilz(seed, s=1.0, stil=0):
    """Giftpilz-Gruppe: violette, glänzende Hüte mit leuchtend grünen Tupfen und giftgrüne Sporentropfen – lieber
    nicht anfassen."""
    w = _neu(seed)
    rng = w.rng
    for i in range(3):
        a = i * 2.1 + 0.4
        d = 3.5 * s * (i > 0)
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        H = _r((8 - i * 2) * s + 2)
        top = stiel(w, x0, z0, 1, H, 0.9 * s + 0.3, 0.6 * s + 0.3,
                    mat="purple_terracotta" if stil == 0 else "black_terracotta", krumm=0.6, richtung=a + 1)
        hut(w, top[0], top[1] - 1, top[2], (4 - i * 0.8) * s + 1.5, (2.8 - i * 0.4) * s + 1, "kuppel",
            "purple_concrete" if stil == 0 else "black_concrete", punkte="lime_concrete", punkt_dichte=0.22,
            lamellen="magenta_terracotta")
        for k in range(2):
            w.setze(top[0] + round((4 - i) * s * 0.7), top[1] - 2 - k, top[2], w.b("lime_stained_glass"), False)
    return w


# ============================================================================ Pilzbauten

def pilzwirtshaus(seed, s=1.0, stil=0):
    """Steinpilz-Wirtshaus: ein riesiger Steinpilz als Gasthaus – Tür und Rundfenster im Stiel, Wirtshausschild,
    Tische unter dem Hut, Laternen an den Lamellen und eine Außentreppe."""
    w = _neu(seed)
    H = _r(9 * s + 5)
    R = 3.5 * s + 2
    top = stiel(w, 0, 0, 1, H, R, R * 0.8, mat="mushroom_stem", knolle=0.8 * s)
    hut(w, top[0], top[1] - 1, top[2], 8 * s + 3, 4 * s + 1.5, "polster",
        lambda x, y, z, s_: "brown_mushroom_block" if (x + z) % 5 else "brown_terracotta",
        lamellen="yellow_terracotta", rand_farbe="brown_mushroom_block")
    ri = int(R) - 1
    for y in range(1, H):
        for x in range(-ri, ri + 1):
            for z in range(-ri, ri + 1):
                if x * x + z * z < (R - 1.2) ** 2:
                    w.bloecke.pop((x, y, z), None)
    for y in (1, 2):
        w.bloecke.pop((0, y, int(R)), None)
        w.setze(0, y, int(R) - 1 if y == 3 else int(R), w.b("spruce_door", facing="south", half="lower" if y == 1
                                                            else "upper", hinge="left", open=False, powered=False))
    for k in range(4):
        a = k * 1.57 + 0.78
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        w.setze(x, 4, z, w.b("glass"))
    w.setze(1, 4, int(R) + 1, w.b("spruce_wall_sign", facing="south", waterlogged=False))
    for k in range(4):
        a = k * 1.57
        x, z = round(math.cos(a) * (R + 3)), round(math.sin(a) * (R + 3))
        w.setze(x, 1, z, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
        w.setze(x, 2, z, w.b("spruce_pressure_plate", powered=False))
        w.setze(x, top[1] - 2, z, w.b("lantern", hanging=True, waterlogged=False), False)
    for k in range(H - 2):
        a = k * 0.5
        x, z = round(math.cos(a) * (R + 0.6)), round(math.sin(a) * (R + 0.6))
        w.setze(x, 1 + k, z, w.b("spruce_slab", type="top", waterlogged=False), False)
    return w


def pilzturm(seed, s=1.0, stil=0):
    """Pilzturm: ein hoher, gewundener Stiel, an dem fünf versetzte Pilzhüte wie Stockwerke sitzen, verbunden
    durch Leitern und Stege, mit Fenstern und Laternen."""
    w = _neu(seed)
    rng = w.rng
    H = _r(26 * s + 6)
    top = stiel(w, 0, 0, 1, H, 1.8 * s + 0.6, 1.2 * s + 0.4, mat="mushroom_stem", krumm=0.25)
    farben = ["red_mushroom_block", "brown_mushroom_block", "orange_terracotta", "red_mushroom_block",
              "brown_mushroom_block"]
    for k in range(5):
        y = round(H * (0.25 + k * 0.17))
        a = k * 2.4
        d = 2 * s + 1
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        R = (5 - k * 0.6) * s + 1.5
        linie(w, (0, y - 2, 0), (x, y, z), w.b("mushroom_stem", **ALLE), 0.6)
        hut(w, x, y, z, R, (2 - k * 0.2) * s + 1, "kuppel", farben[(k + stil) % 5],
            punkte="white_concrete" if farben[(k + stil) % 5].startswith("red") else None, lamellen="white_terracotta")
        w.setze(x, y - 1, z, w.b("lantern", hanging=True, waterlogged=False), False)
    hut(w, top[0], top[1] - 1, top[2], 3 * s + 1, 2.5 * s + 1, "kegel", "red_mushroom_block",
        punkte="white_concrete")
    for y in range(1, H, 5):
        w.setze(0, y, -round(1.8 * s + 1), w.b("glass"), True)
    return w


def pilzdorf(seed, s=1.0, stil=0):
    """Pilzdorf: sechs Wohnpilze unterschiedlicher Größe mit Türen und Fenstern, ein Brunnen in der Mitte,
    Trittsteinwege und Gärten mit kleinen Pilzen."""
    w = _neu(seed)
    rng = w.rng
    n = 6
    R = 11 * s + 4
    for i in range(n):
        a = i / n * 6.28 + 0.3
        cx, cz = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        h = _r((5 + (i % 3) * 2) * s + 2)
        r = (1.6 + (i % 2) * 0.6) * s + 1.2
        top = stiel(w, cx, cz, 1, h, r, r * 0.9, mat="mushroom_stem")
        farbe = ["red_mushroom_block", "brown_mushroom_block", "orange_terracotta"][i % 3]
        hut(w, top[0], top[1] - 1, top[2], r * 2.3 + 1, r * 1.3 + 0.8, "kuppel", farbe,
            punkte="white_concrete" if i % 3 == 0 else None)
        dx, dz = -math.cos(a), -math.sin(a)
        tx, tz = round(cx + dx * r), round(cz + dz * r)
        for y in (1, 2):
            w.setze(tx, y, tz, w.b("spruce_planks"))
        w.setze(round(cx + dx * (r + 0.6)), 3, round(cz + dz * (r + 0.6)), w.b("lantern", hanging=False,
                                                                                waterlogged=False), False)
        w.setze(round(cx - dz * r), 3, round(cz + dx * r), w.b("glass"))
        for k in range(1, int(R * 0.6 - r)):
            x, z = round(cx + dx * (r + k)), round(cz + dz * (r + k))
            if k % 2:
                w.setze(x, 0, z, w.b("cobblestone"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            if x * x + z * z <= 5:
                w.setze(x, 1, z, w.b("stone_bricks") if x * x + z * z > 2 else w.b("water", level=0))
    return w


def hexenring(seed, s=1.0, stil=0):
    """Hexenring: ein perfekter Kreis aus Pilzen auf einer Lichtung, in der Mitte dunkleres Gras, ein moosiger
    Stein und schwebende Glühwürmchen – ein Tor ins Feenreich."""
    w = _neu(seed)
    rng = w.rng
    R = 7 * s + 3
    for k in range(int(R * 5)):
        a = k / (R * 5) * 6.28
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        if k % 2 == 0:
            h = _r((1.2 + rng.random() * 1.2) * s)
            top = stiel(w, x, z, 1, h, 0.25 * s + 0.2, mat="mushroom_stem")
            hut(w, top[0], top[1] - 1, top[2], (0.9 + rng.random() * 0.6) * s + 0.4, 0.8 * s + 0.4, "kuppel",
                "brown_mushroom_block" if stil == 0 else "red_mushroom_block",
                punkte=None if stil == 0 else "white_concrete", lamellen="white_terracotta")
    for y in range(1, 3):
        w.setze(0, y, 0, w.b("mossy_cobblestone"))
    w.setze(0, 3, 0, w.b("moss_carpet"))
    for k in range(int(6 * s)):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.8
        w.setze(round(math.cos(a) * d), round(3 + rng.random() * 4), round(math.sin(a) * d),
                w.b("ochre_froglight" if stil == 0 else "verdant_froglight", axis="y"), False)
    return w


def pilzbruecke(seed, s=1.0, stil=0):
    """Pilzbrücke: über eine Schlucht spannen sich die Hüte flacher Riesenpilze als Trittflächen, verbunden
    durch Ranken-Geländer."""
    w = _neu(seed)
    L = _r(14 * s + 5)
    for x in range(-L - 4, L + 5):
        for z in range(-4, 5):
            if abs(x) > L:
                for y in range(1, _r(6 * s) + 2):
                    w.setze(x, y, z, w.b(["stone", "mossy_cobblestone", "andesite", "moss_block"][(x + y + z) % 4]))
    n = 4
    for k in range(n):
        x = round(-L + (k + 0.5) * 2 * L / n)
        hy = _r(6 * s) + 1 - abs(k - 1.5) * 0.3
        top = stiel(w, x, 0, -6, round(hy) + 6, 0.8 * s + 0.3, mat="mushroom_stem")
        hut(w, top[0], top[1] - 1, top[2], L / n + 1.2, 1.0, "flach",
            "brown_mushroom_block" if (k + stil) % 2 else "red_mushroom_block", lamellen="white_terracotta",
            dicke=1.0)
    for x in range(-L, L + 1):
        for z in (-3, 3):
            y = _r(6 * s) + 3 + round(math.sin(x * 0.4) * 0.6)
            w.setze(x, y, z, w.b("vine", north=False, south=False, east=True, west=False, up=False), False)
    return w


def sporenhoehle(seed, s=1.0, stil=0):
    """Sporenhöhle: ein halboffenes Felsgewölbe, in dem leuchtende Pilze von Decke und Wänden wachsen,
    Myzelteppich am Boden und ein kleiner Teich, der das Licht spiegelt."""
    w = _neu(seed)
    rng = w.rng
    R = 9 * s + 3
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            d = math.hypot(x, z)
            if d > R:
                continue
            w.setze(x, 0, z, w.b("mycelium", snowy=False) if d > 2.5 else w.b("water", level=0))
            for y in range(1, int(R * 0.9) + 2):
                if d > R - 1.5 - 0.15 * y and z < R * 0.3 or (y > R * 0.75 - 0.1 * d and z < R * 0.3):
                    if (x * x + z * z + (y * 1.1) ** 2) <= (R + 1) ** 2:
                        w.setze(x, y, z, w.b(["stone", "deepslate", "tuff", "mossy_cobblestone"][(x + y + z) % 4]))
    for k in range(int(10 * s)):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.8
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if d > 3:
            top = stiel(w, x, z, 1, _r((1 + rng.random() * 3) * s), 0.3 * s + 0.2, mat="mushroom_stem")
            hut(w, top[0], top[1] - 1, top[2], (1 + rng.random()) * s + 0.5, 0.8 * s + 0.5, "kuppel",
                "verdant_froglight" if k % 2 else "shroomlight", lamellen="light_blue_stained_glass")
    for k in range(int(20 * s)):
        x, z = int(rng.integers(-int(R), int(R))), int(rng.integers(-int(R), 0))
        y = max([p[1] for p in w.bloecke if p[0] == x and p[2] == z] + [0])
        if y > 3:
            w.setze(x, y - 1, z, w.b("shroomlight") if k % 3 == 0 else w.b("weeping_vines_plant"), False)
    return w


def pilzzucht(seed, s=1.0, stil=0):
    """Pilzzucht: eine Waldgärtnerei mit gestapelten Zuchtstämmen voller Austernpilze, Strohbeeten mit
    Champignons, Erntekörben und einem Schuppen."""
    import pracht as P
    w = _neu(seed)
    rng = w.rng
    L = _r(8 * s + 4)
    for k in range(4):
        z0 = -L + k * 3
        for x in range(-L, 2):
            for y in (1, 2):
                if (x + y) % 2 == 0 or y == 1:
                    w.setze(x, y, z0, w.b("oak_log", axis="x"))
            if x % 2 == 0:
                w.setze(x, 2, z0 - 1, w.b("white_terracotta"), False)
                w.setze(x, 1, z0 + 1, w.b("light_gray_terracotta"), False)
    for x in range(3, L + 1):
        for z in range(-L, 0):
            w.setze(x, 1, z, w.b("hay_block", axis="y") if (x + z) % 4 else w.b("mycelium", snowy=False))
            if (x * 3 + z) % 3 == 0:
                w.setze(x, 2, z, w.b("brown_mushroom" if (x + z) % 2 else "red_mushroom"))
    st = P.Stil(w, wand=["spruce_planks", "dark_oak_planks", "stripped_spruce_log"], sockel="holz_dunkel",
                gesims="stone_brick", dach="mcw_holz", holz="spruce", laeden=True, blumen=0)
    P.gebaeude(w, st, -3, 3, 3, 7, y0=1, etagen=1, eh=3, dach="sattel", tuer="north", gauben=False, kamine=0)
    for k in range(3):
        w.setze(5 + k, 1, 4, w.b("barrel", facing="up", open=True))
    return w


def pilzthron(seed, s=1.0, stil=0):
    """Pilzthron: ein Thron aus verwachsenen Pilzstielen unter einem riesigen Baldachin-Hut, Stufen aus
    Baumpilzen und eine Krone aus kleinen leuchtenden Pilzen."""
    w = _neu(seed)
    H = _r(11 * s + 4)
    top = stiel(w, 0, -2, 1, H, 1.0 * s + 0.5, 0.8 * s + 0.4, mat="mushroom_stem", krumm=0.8, richtung=-1.57)
    hut(w, top[0], top[1] - 1, top[2] + 1, 7 * s + 2, 3 * s + 1.5, "kuppel",
        "red_mushroom_block" if stil == 0 else "purple_concrete", punkte="white_concrete" if stil == 0 else
        "pearlescent_froglight", lamellen="pink_terracotta")
    for x in range(-2, 3):
        for y in range(1, 4):
            w.setze(x, y, -1, w.b("mushroom_stem", **ALLE))
    for x in (-2, 2):
        w.setze(x, 2, 0, w.b("mushroom_stem", **ALLE))
        w.setze(x, 3, 0, w.b("shroomlight"))
    for x in range(-1, 2):
        w.setze(x, 1, 0, w.b("red_wool" if stil == 0 else "purple_wool"))
    for k in range(3):
        for x in range(-2 - k, 3 + k):
            w.setze(x, 0, 1 + k, w.b(["brown_terracotta", "orange_terracotta", "yellow_terracotta"][k]))
    for k in range(5):
        a = k / 5 * 3.14
        w.setze(round(math.cos(a) * 2), 4, -1 - round(math.sin(a)), w.b("ochre_froglight", axis="y"))
    return w


# ============================================================================ Kombinierbare Pilzwälder

def _pilz_zufall(st, s, arten):
    def wahl(x, z, rd, art):
        f = arten[int(st.rng.integers(len(arten)))]
        k = s * (0.5 + 0.6 * st.rng.random())
        return f(int(st.rng.integers(1, 10 ** 7)), k, st.stil), 4.5 * k + 1.5
    return wahl


def riesenpilzhain(seed, g=1):
    """Riesenpilzhain: ein Wald aus Fliegenpilzen, Parasolen, Steinpilzen und Tintlingen in Baumgröße über
    Moos und Farnen – nahtlos kombinierbar."""
    st = Stueck(seed, g)
    st.verteile(6, int(150 * (g + 1) ** 2), _pilz_zufall(st, 0.6 + 0.2 * g,
                                                         [fliegenpilz, parasol, steinpilz, tintling, hallimasch]))
    boden_pilz(st, 0.55)
    return st


def leuchtpilzwald(seed, g=1):
    """Leuchtpilzwald: ein dunkler Wald aus biolumineszenten Pilzen, Leuchtflechten und schwebenden Sporen –
    nachts ein Lichtermeer."""
    st = Stueck(seed, g)
    st.verteile(6, int(140 * (g + 1) ** 2), _pilz_zufall(st, 0.6 + 0.2 * g, [leuchtpilz, giftpilz, leuchtpilz]))
    boden_pilz(st, 0.6, "myzel")
    return st


def netherpilzwald(seed, g=1):
    """Netherpilzwald: Karmesin- und Wirrpilze in Riesengröße mit Warzenhüten, Schroomlichtern und Ranken auf
    Nyzel – passt in jede Netherlandschaft."""
    st = Stueck(seed, g)

    def nether(sd, k, stil):
        w = _neu(sd)
        rng = w.rng
        warped = rng.random() < 0.5
        H = _r((8 + rng.random() * 6) * k + 3)
        top = stiel(w, 0, 0, 1, H, 0.9 * k + 0.4, 0.7 * k + 0.3, mat="warped_stem" if warped else "crimson_stem",
                    krumm=0.5, richtung=rng.random() * 6)
        hut(w, top[0], top[1] - 2, top[2], 4 * k + 2, 3 * k + 1.5, "kuppel",
            lambda x, y, z, s_: ("warped_wart_block" if warped else "nether_wart_block"),
            punkte="shroomlight", punkt_dichte=0.12, lamellen=None, dicke=2)
        for j in range(int(5 * k)):
            a = rng.random() * 6.28
            r = 4 * k + 1.5
            x, z = top[0] + round(math.cos(a) * r), top[2] + round(math.sin(a) * r)
            for d in range(int(2 + rng.integers(4))):
                w.setze(x, top[1] - 3 - d, z, w.b("twisting_vines_plant" if warped else "weeping_vines_plant"),
                        False)
        return w

    st.verteile(7, int(120 * (g + 1) ** 2), _pilz_zufall(st, 0.6 + 0.2 * g, [nether]))
    boden_pilz(st, 0.5, "nether")
    return st


def myzelwiese(seed, g=1):
    """Myzelwiese: eine offene Fläche mit Myzel und Moos, übersät von kleinen und mittleren Pilzen in Gruppen und
    Hexenringen – Übergang zwischen Pilzwald und Wiese."""
    st = Stueck(seed, g)
    st.verteile(5, int(80 * (g + 1) ** 2), _pilz_zufall(st, 0.3 + 0.08 * g,
                                                        [fliegenpilz, steinpilz, pfifferling, giftpilz, hallimasch]))
    boden_pilz(st, 0.6, "myzel")
    return st


def _wrap(f):
    def g(seed, groesse=1):
        st = f(seed, groesse)
        return _fertig(st.w if isinstance(st, Stueck) else st)
    g.__doc__ = f.__doc__
    return g


PILZE = {
    "fliegenpilz": ("Riesen-Fliegenpilz", einzeln(fliegenpilz)),
    "steinpilz": ("Riesen-Steinpilz", einzeln(steinpilz)),
    "parasol": ("Parasol", einzeln(parasol)),
    "pfifferling": ("Pfifferlinge", einzeln(pfifferling)),
    "morchel": ("Morchel", einzeln(morchel)),
    "tintling": ("Schopftintlinge", einzeln(tintling)),
    "hallimasch": ("Hallimasch-Büschel", einzeln(hallimasch)),
    "baumpilze": ("Baumpilze", einzeln(baumpilze)),
    "leuchtpilz": ("Leuchtpilze", einzeln(leuchtpilz, art="myzel")),
    "schleierdame": ("Schleierdame", einzeln(schleierdame)),
    "korallenpilz": ("Korallenpilz", einzeln(korallenpilz)),
    "bovist": ("Riesenbovist", einzeln(bovist)),
    "giftpilz": ("Giftpilze", einzeln(giftpilz, art="myzel")),
    "pilzwirtshaus": ("Steinpilz-Wirtshaus", einzeln(pilzwirtshaus)),
    "pilzturm": ("Pilzturm", einzeln(pilzturm)),
    "pilzdorf": ("Pilzdorf", einzeln(pilzdorf, R_extra=2)),
    "hexenring": ("Hexenring", einzeln(hexenring, dichte=0.3)),
    "pilzbruecke": ("Pilzbrücke", einzeln(pilzbruecke, R_extra=1, dichte=0.2)),
    "sporenhoehle": ("Sporenhöhle", einzeln(sporenhoehle, art="myzel")),
    "pilzzucht": ("Pilzzucht", einzeln(pilzzucht)),
    "pilzthron": ("Pilzthron", einzeln(pilzthron)),
    "riesenpilzhain": ("Riesenpilzhain", _wrap(riesenpilzhain)),
    "leuchtpilzwald": ("Leuchtpilzwald", _wrap(leuchtpilzwald)),
    "netherpilzwald": ("Netherpilzwald", _wrap(netherpilzwald)),
    "myzelwiese": ("Myzelwiese", _wrap(myzelwiese)),
}

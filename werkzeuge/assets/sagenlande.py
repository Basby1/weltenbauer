"""Sagenlande – eigene epische Fantasy-Bauwerke. Größen 0 klein · 1 mittel · 2 riesig · 3 gigantisch,
je zwei Stile (Variante 1 / 2)."""

from __future__ import annotations

import math

import numpy as np

from lib import Verlauf, Welt, laub, ueberwuchern
from skulptur import (Skulptur, ell, kap, kegel, kreisrand, laterne, pfosten, platte, scheibe, treppe, verbinde,
                      zur_mitte)

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _welle(X, Y, Z, k=1.0):
    """Billiges, glattes Pseudo-Rauschen für Masken (-1..1)."""
    return (np.sin(X * 0.31 * k + Z * 0.17 * k) * np.cos(Z * 0.29 * k - Y * 0.13 * k)
            + 0.5 * np.sin(X * 0.71 * k - Y * 0.37 * k + Z * 0.53 * k)) / 1.5


def _feuer(w, x, y, z, seele=False, signal=True):
    w.setze(x, y, z, w.b("soul_campfire" if seele else "campfire", lit=True, signal_fire=signal, facing="north",
                         waterlogged=False))


# ============================================================================ Schwarzfeste

def _spitze(cx, cz, H, R, lx, lz, drall, zacken=4, y0=0.0):
    def f(X, Y, Z):
        t = np.clip((Y - y0) / H, 0, 1)
        dx, dz = X - (cx + lx * t * t), Z - (cz + lz * t * t)
        a = np.arctan2(dz, dx)
        r = R * (1 - t) ** 0.75 * (0.76 + 0.24 * np.cos(zacken * (a - drall * t)))
        r = r * (1 + 0.45 * np.clip(1 - (Y - y0) / (0.14 * H), 0, 1))
        return (Y >= y0) & (Y <= y0 + H) & (dx * dx + dz * dz <= r * r)
    return f


def schwarzfeste(seed, g=1):
    """Finstere Zitadelle aus schwarzem Stein: Felsplateau mit Glutadern, sechseckige Zackenmauer mit
    Ecktürmen und Fallgitter, im Kern ein Bündel verdrehter Sternspitzen mit glühenden Fensterschlitzen,
    Himmelsbrücken, Ketten und Bannern."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        stein = Verlauf(w, "Schwarzstein", ["blackstone", "polished_blackstone", "polished_blackstone_bricks",
                                            "deepslate_tiles", "polished_deepslate"])
        fels = Verlauf(w, "Fels", ["blackstone", "basalt", "smooth_basalt", "cobbled_deepslate"])
        glut, ader, seele, banner = "shroomlight", "magma_block", False, ["red_wool", "nether_wart_block"]
    else:
        stein = Verlauf(w, "Frostfeste", ["deepslate_tiles", "polished_deepslate", "deepslate_bricks",
                                          "cobbled_deepslate", "tuff"])
        fels = Verlauf(w, "Fels", ["deepslate", "cobbled_deepslate", "tuff", "packed_ice"])
        glut, ader, seele, banner = "sea_lantern", "blue_ice", True, ["blue_wool", "blue_terracotta"]
    Rp, Hp = 15 * u + 3, _r(3 * u, 2)
    # Plateau mit Glutadern
    n = int(Rp * 1.25) + 2
    for x in range(-n, n + 1):
        for z in range(-n, n + 1):
            a = math.atan2(z, x)
            rand = Rp * (1 + 0.12 * math.sin(5 * a + 1) + 0.07 * math.sin(11 * a))
            d = math.hypot(x, z)
            if d > rand:
                continue
            h = Hp if d < rand - 2 else max(0, int(Hp * (rand - d) / 2))
            for y in range(0, h + 1):
                w.setze(x, y, z, fels(0.3 + 2.5 * y / max(1, Hp) + w.rng.random() * 0.8, x, y, z))
            if abs(math.sin(x * 0.33 + math.sin(z * 0.2) * 2) * math.cos(z * 0.27 - x * 0.05)) < 0.07:
                w.setze(x, h, z, w.b(ader))
    y0 = Hp + 1
    S = Skulptur(w, u)

    def turmmat(x, y, z, lx, ly, lz):
        if y % _r(4 * u, 3) == 0 and (x + 2 * z) % 4 == 0:
            return w.b(glut)
        if (x * 7 + z * 13) % 29 == 0:
            return w.b(ader)
        return stein(0.6 + 3.2 * ly / 40 + w.rng.random() * 0.7, x, y, z)
    S.mat("t", turmmat)
    S.mat("m", stein, basis=1.0, steigung=0.08, rausch=1.0)
    # Sechseckmauer mit Zinnen
    Rw, Hw, dick = 11.0, 6.0, max(0.8, 1.0)
    ecken = [(Rw * math.cos(i * math.pi / 3), Rw * math.sin(i * math.pi / 3))
             for i in range(6)]
    for i in range(6):
        (ax, az), (bx, bz) = ecken[i], ecken[(i + 1) % 6]

        def mauer(X, Y, Z, ax=ax, az=az, bx=bx, bz=bz):
            dx, dz = bx - ax, bz - az
            L2 = dx * dx + dz * dz
            t = np.clip(((X - ax) * dx + (Z - az) * dz) / L2, 0, 1)
            qx, qz = X - ax - t * dx, Z - az - t * dz
            entlang = t * math.sqrt(L2)
            zinne = np.where(np.mod(entlang, 2.4) < 1.2, 1.3, 0)
            return (qx * qx + qz * qz <= dick * dick) & (Y >= 0) & (Y <= Hw + zinne)
        S.plus(mauer, "m")
    for (ex, ez) in ecken:
        S.plus(_spitze(ex, ez, Hw + 9, 2.2, ex * 0.08, ez * 0.08, 1.5, 4), "t")
    # Kern: Bündel verdrehter Sternspitzen
    S.plus(_spitze(0, 0, 40, 4.6, 0, 0, 2.2, 4), "t")
    teile = [(0.66, 0.6), (0.52, 2.1), (0.44, 3.4), (0.36, 4.7)]
    for k, (f, a) in enumerate(teile):
        cx, cz = math.cos(a) * 4.2, math.sin(a) * 4.2
        S.plus(_spitze(cx, cz, 40 * f, 2.9, math.cos(a) * 3, math.sin(a) * 3, -1.8, 3 + k % 2), "t")
    # Himmelsbrücken zwischen den Spitzen
    for k, (f, a) in enumerate(teile[:2]):
        ya = 40 * f * 0.62
        S.plus(kap((0, ya, 0), (math.cos(a) * 4.2 + math.cos(a) * 3 * 0.38, ya - 1.5, math.sin(a) * 4.2 +
                                math.sin(a) * 3 * 0.38), 0.75), "m")
    # Tor in der Mauer (Seite +z)
    S.minus(lambda X, Y, Z: (np.abs(X) <= 1.6) & (Y <= 4.2) & (Z > Rw * 0.6))
    S.rendern((-16, 0, -16), (16, 42, 16), versatz=(0.5, y0, 0.5))
    # Fallgitter, Feuerschalen, Banner, Ketten
    zt = int(Rw * math.cos(math.pi / 6) * u)
    gitter = [(x, y0 + y, zt) for x in range(-int(1.6 * u), int(1.6 * u) + 1) for y in range(_r(3.4 * u, 2), _r(4.2 * u, 3))]
    verbinde(w, gitter, "iron_bars")
    for s in (-1, 1):
        x = s * (int(1.6 * u) + 2)
        pfosten(w, x, y0, y0 + _r(u, 1), zt + 2, "polished_blackstone_wall")
        _feuer(w, x, y0 + _r(u, 1) + 1, zt + 2, seele)
    for i in range(6):
        a = i * math.pi / 3 + math.pi / 6
        r = Rw * math.cos(math.pi / 6) * u + dick * u + 0.6
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        if z > zt - 2 and abs(x) < 4 * u:
            continue
        for y in range(y0 + _r(1.5 * u), y0 + _r(Hw * u) - 1):
            w.setze(x, y, z, w.b(banner[(y // 2) % 2]), ueberschreiben=False)
    for k in range(2 + g):
        a = w.rng.random() * 2 * math.pi
        x, z = round(math.cos(a) * 3 * u), round(math.sin(a) * 3 * u)
        y_hoch = y0 + int(25 * u)
        hoehen = [p[1] for p in w.bloecke if p[0] == x and p[2] == z and y0 + 8 * u < p[1] < y_hoch]
        if hoehen:
            unten = min(hoehen)
            for y in range(unten - _r(4 * u, 2), unten):
                w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False), ueberschreiben=False)
    return w


# ============================================================================ Glutfeld

def glutfeld(seed, g=1):
    """Vulkanische Ödnis: zerklüfteter Boden mit Glutrissen, rauchende Kegel, Basaltsäulen,
    tote Bäume, umgestürzte Säulen und das Gerippe eines Ungeheuers."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        boden = Verlauf(w, "Asche", ["blackstone", "basalt", "smooth_basalt", "tuff", "cobbled_deepslate"])
        ader, glut, seele = "magma_block", "shroomlight", False
    else:
        boden = Verlauf(w, "Seelenasche", ["soul_soil", "soul_sand", "basalt", "smooth_basalt", "tuff"])
        ader, glut, seele = "soul_soil", "sea_lantern", True
    R = 16 * u + 4
    n = int(R) + 2
    hoehe = {}
    for x in range(-n, n + 1):
        for z in range(-n, n + 1):
            d = math.hypot(x, z)
            a = math.atan2(z, x)
            if d > R * (1 + 0.1 * math.sin(4 * a + 2)):
                continue
            h = int(1 + 1.6 * u * (0.5 + 0.5 * math.sin(x * 0.21 / u + 1) * math.cos(z * 0.17 / u)) * (1 - d / (R * 1.1)))
            hoehe[(x, z)] = h
            for y in range(0, h + 1):
                w.setze(x, y, z, boden(1 + 3 * w.rng.random() * (y / max(1, h)), x, y, z))
            riss = abs(math.sin(x * 0.4 / u + math.sin(z * 0.25 / u) * 2.2) * math.cos(z * 0.33 / u)) < 0.06
            if riss:
                w.setze(x, h, z, w.b(ader))
                if not seele:
                    w.setze(x, h - 1, z, w.b(glut))
    # Rauchende Kegel
    for i in range(1 + g):
        a = w.rng.random() * 2 * math.pi
        d = R * (0.35 + 0.4 * w.rng.random())
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        rk, hk = 3.5 * u + 1, _r(4 * u, 3)
        for x, z in scheibe(rk):
            dd = math.hypot(x, z) / rk
            hh = hoehe.get((cx + x, cz + z), 0) + int(hk * (1 - dd))
            for y in range(0, hh + 1):
                w.setze(cx + x, y, cz + z, boden(0.5 + 2.5 * y / (hh + 1) + w.rng.random(), cx + x, y, cz + z))
        top = hoehe.get((cx, cz), 0) + hk
        w.setze(cx, top, cz, w.b(ader))
        _feuer(w, cx, top + 1, cz, seele)
    # Basaltsäulen-Gruppen
    for i in range(2 + g):
        a = w.rng.random() * 2 * math.pi
        d = R * w.rng.random() * 0.8
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        for x, z in scheibe(1.6 * u + 0.6):
            if w.rng.random() < 0.8:
                h0 = hoehe.get((cx + x, cz + z), 0)
                for y in range(h0, h0 + int((2 + w.rng.random() * 6) * u) + 1):
                    w.setze(cx + x, y, cz + z, w.b("polished_basalt", axis="y"))
    # Tote Bäume
    for i in range(2 + 2 * g):
        a = w.rng.random() * 2 * math.pi
        d = R * (0.2 + 0.7 * w.rng.random())
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        y = hoehe.get((x0, z0), 0) + 1
        H = int((4 + 3 * w.rng.random()) * u) + 2
        holz = w.b("stripped_dark_oak_log", axis="y")
        for k in range(H):
            w.setze(x0, y + k, z0, holz)
        for b in range(3):
            ab = w.rng.random() * 2 * math.pi
            yb = y + int(H * (0.45 + 0.4 * w.rng.random()))
            lang = (2 + 2 * w.rng.random()) * u + 1
            for t in np.linspace(0, 1, int(lang * 2) + 2):
                w.setze(round(x0 + math.cos(ab) * lang * t), round(yb + lang * 0.6 * t),
                        round(z0 + math.sin(ab) * lang * t), w.b("dark_oak_fence", north=False, south=False,
                                                                 east=False, west=False, waterlogged=False))
    # Umgestürzte Säulen und Gerippe
    for i in range(1 + g):
        a = w.rng.random() * 2 * math.pi
        d = R * (0.3 + 0.5 * w.rng.random())
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        y = hoehe.get((x0, z0), 0) + 1
        hs = int((3 + 3 * w.rng.random()) * u) + 1
        for k in range(hs):
            w.setze(x0, y + k, z0, w.b("chiseled_polished_blackstone" if k == hs - 1 else "polished_blackstone_bricks"))
        for k in range(int(4 * u) + 2):
            w.setze(x0 + 2 + k, y, z0 + 1, w.b("polished_basalt", axis="x"))
    S = Skulptur(w, u)
    S.mat("k", w.b("bone_block", axis="y"))
    bx, bz = -R * 0.35, R * 0.25
    S.plus(kap((bx - 7, 1.2, bz), (bx + 7, 2.2, bz), max(0.55, 0.6)), "k")
    for k in range(6):
        x = bx - 5 + k * 2
        for s in (-1, 1):
            S.plus(kap((x, 2, bz), (x + 0.6, 3.6, bz + s * 2.4), 0.45), "k")
            S.plus(kap((x + 0.6, 3.6, bz + s * 2.4), (x + 1, 0.2, bz + s * 3.6), 0.4), "k")
    S.plus(ell(bx + 8.5, 2.2, bz, 2.0, 1.2, 1.3), "k")
    S.rendern((bx - 9, -1, bz - 6), (bx + 11, 6, bz + 6), versatz=(0.5, 1, 0.5), ueberschreiben=False)
    return w


# ============================================================================ Hügelhof

def huegelhof(seed, g=1):
    """Gemütlicher Hof in einem Grashügel: Fachwerkfront mit Vordach, Blumenkästen, rauchender Kamin
    im Hügel, Gemüsegarten mit Zaun, Weg, Teich mit Seerosen, Bienenstock und Obstbaum."""
    w = _welt(seed)
    u = U[g]
    herbst = _stil(seed) == 1
    rahmen = "spruce" if herbst else "dark_oak"
    fuellung = Verlauf(w, "Putz", ["bricks", "terracotta", "bricks"] if herbst else
                       ["white_terracotta", "calcite", "smooth_quartz"])
    Rx, Rz, Hh = 10 * u + 3, 8 * u + 2.5, 6 * u + 2
    zf = int(Rz * 0.45)
    bw, bh = _r(4.5 * u, 3), _r(3.2 * u, 3)
    gras, erde = w.b("grass_block", snowy=False), w.b("dirt")
    oben = {}
    for x in range(-int(Rx) - 1, int(Rx) + 2):
        for z in range(-int(Rz) - 1, int(Rz) + 2):
            d = (x / Rx) ** 2 + (z / Rz) ** 2
            if d > 1:
                continue
            h = int(Hh * (1 - d) ** 0.7)
            innen = abs(x) <= bw - 1 and zf - _r(5 * u, 3) <= z < zf and True
            for y in range(0, h + 1):
                if innen and 1 <= y <= bh:
                    continue
                if z > zf and y <= bh + 1 and abs(x) <= bw + 1:
                    continue
                w.setze(x, y, z, gras if y == h else erde)
            oben[(x, z)] = h
    # Fachwerkfront
    for x in range(-bw, bw + 1):
        for y in range(0, bh + 2):
            pfosten_ = x in (-bw, bw) or (x % 3 == 0 and y <= bh)
            if y == 0 or y == bh + 1:
                blk = w.b(f"stripped_{rahmen}_log", axis="x")
            elif pfosten_:
                blk = w.b(f"stripped_{rahmen}_log", axis="y")
            elif y in (2, 3) and abs(x) in (2, bw - 2) and bw >= 4:
                blk = w.b("glass_pane", east=True, west=True, north=False, south=False, waterlogged=False)
            else:
                blk = fuellung(1 + w.rng.random() * 1.5, x, y, zf)
            w.setze(x, y, zf, blk)
        if bw >= 4 and abs(x) in (2, bw - 2):
            w.setze(x, 1, zf + 1, w.b("flowering_azalea_leaves", persistent=True, distance=7, waterlogged=False))
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(0, y, zf, w.b(f"{rahmen}_door", facing="south", half=half, hinge="left", open=False, powered=False))
    # Vordach mit Pfosten und Laterne
    for x in (-1, 1):
        for y in range(1, 4):
            w.setze(x, y, zf + 2, w.b(f"{rahmen}_fence", north=y == 3, south=False, east=False, west=False,
                                      waterlogged=False))
    for x in range(-2, 3):
        for z in range(zf + 1, zf + 3):
            w.setze(x, 4, z, platte(w, rahmen))
    w.setze(0, 3, zf + 1, w.b("lantern", hanging=True, waterlogged=False))
    # Dach-Überstand: Gras über der Front
    for x in range(-bw - 1, bw + 2):
        w.setze(x, bh + 2, zf, gras)
    for x in range(-bw + 1, bw):
        for z in range(zf - _r(5 * u, 3), zf):
            w.setze(x, 0, z, w.b(f"{rahmen}_planks"))
    w.setze(bw - 2, 1, zf - 2, w.b("lantern", hanging=False, waterlogged=False))
    w.setze(-bw + 2, 1, zf - 2, w.b("barrel", facing="up", open=False))
    # Kamin
    kx, kz = bw - 1, zf - _r(3 * u, 2)
    for y in range(1, oben.get((kx, kz), Hh) + _r(2 * u, 2)):
        w.setze(kx, y, kz, w.b("cobblestone" if y % 3 else "mossy_cobblestone"))
    _feuer(w, kx, oben.get((kx, kz), Hh) + _r(2 * u, 2), kz, signal=False)
    # Garten
    gz0, gz1 = int(Rz) + 1, int(Rz) + 1 + _r(6 * u, 4)
    gx = _r(6 * u, 4)
    zaun = [(x, 1, z) for x in range(-gx, gx + 1) for z in (gz0, gz1)] + \
           [(x, 1, z) for x in (-gx, gx) for z in range(gz0, gz1 + 1)]
    zaun = [p for p in zaun if not (abs(p[0]) <= 1 and p[2] == gz1)]
    verbinde(w, zaun, f"{rahmen}_fence")
    frucht = ["pumpkin", "carrots", "wheat"] if herbst else ["wheat", "carrots", "potatoes"]
    for z in range(gz0 + 1, gz1):
        for x in range(-gx + 1, gx):
            if abs(x) <= 1:
                w.setze(x, 0, z, w.b("dirt_path"))
                continue
            reihe = (x + 100) // 2 % 3
            if x % 2 == 0:
                w.setze(x, 0, z, w.b("farmland", moisture=7))
                f = frucht[reihe]
                w.setze(x, 1, z, w.b(f) if f == "pumpkin" else w.b(f, age=7))
            else:
                w.setze(x, 0, z, w.b("water", level=0) if z % 4 == 0 else w.b("coarse_dirt"))
    for z in range(zf + 1, gz0 + 1):
        for x in (-1, 0, 1):
            w.setze(x, 0, z, w.b("dirt_path"))
    # Teich
    px, pz, pr = -int(Rx) - _r(2 * u, 1), int(Rz * 0.6), 2.5 * u + 1
    for x, z in scheibe(pr):
        w.setze(px + x, 0, pz + z, w.b("water", level=0))
        if w.rng.random() < 0.12:
            w.setze(px + x, 1, pz + z, w.b("lily_pad"))
    for x, z in kreisrand(pr + 1):
        w.setze(px + x, 0, pz + z, w.b("mud" if w.rng.random() < 0.5 else "grass_block", snowy=False)
                if False else w.b("grass_block", snowy=False))
        if w.rng.random() < 0.3:
            w.setze(px + x, 1, pz + z, w.b("tall_grass", half="lower"))
            w.setze(px + x, 2, pz + z, w.b("tall_grass", half="upper"))
    # Obstbaum und Bienenstock
    tx, tz = int(Rx) + _r(2 * u, 1), int(Rz * 0.4)
    th = _r(4 * u, 3)
    for y in range(1, th + 1):
        w.setze(tx, y, tz, w.b("oak_log", axis="y"))
    S = Skulptur(w, u)
    blatt = [laub(w, "oak"), laub(w, "oak"), laub(w, "azalea"), laub(w, "flowering_azalea")] if not herbst else \
        [laub(w, "acacia"), laub(w, "jungle"), laub(w, "oak"), laub(w, "dark_oak")]
    S.mat("l", lambda x, y, z, *_: blatt[int(w.rng.integers(len(blatt)))])
    S.plus(lambda X, Y, Z: (X / 2.8) ** 2 + (Y / 2.2) ** 2 + (Z / 2.8) ** 2 <= 1 + 0.18 * _welle(X * 3, Y * 3, Z * 3), "l")
    S.rendern((-4, -3, -4), (4, 3, 4), versatz=(tx + 0.5, th + 1.5 * u, tz + 0.5), ueberschreiben=False)
    w.setze(tx, th - 1, tz + 1, w.b("bee_nest", facing="south", honey_level=3))
    if herbst:
        for k in range(3):
            w.setze(tx - 2 + k, 1, tz - 3, w.b("hay_block", axis="x"))
        w.setze(tx - 1, 2, tz - 3, w.b("hay_block", axis="z"))
        w.setze(-gx - 2, 1, gz0, w.b("carved_pumpkin", facing="south"))
    ueberwuchern(w, None, ranken=0.0, moos_oben=0.0, pflanzen=0.45, buesche=0.05)
    return w


# ============================================================================ Felsterrassenstadt

def felsenstadt(seed, g=1):
    """Stadt in Stufen an einer Felswand: Häuser mit Bogentüren und Kuppeln, Treppen im Zickzack,
    hängende Gärten, Laternen und ein Wasserfall, der in ein Becken stürzt."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        fels = Verlauf(w, "Sandfels", ["terracotta", "orange_terracotta", "cut_red_sandstone", "smooth_red_sandstone",
                                       "smooth_sandstone"])
        haus = Verlauf(w, "Haus", ["sandstone", "cut_sandstone", "smooth_sandstone", "end_stone"])
        kuppel = Verlauf(w, "Kuppel", ["waxed_copper_block", "waxed_exposed_copper", "waxed_weathered_copper",
                                       "waxed_oxidized_copper"])
        hm = "smooth_sandstone"
    else:
        fels = Verlauf(w, "Weißfels", ["andesite", "stone", "diorite", "polished_diorite", "calcite"])
        haus = Verlauf(w, "Haus", ["calcite", "smooth_quartz", "white_concrete", "quartz_bricks"])
        kuppel = Verlauf(w, "Kuppel", ["blue_terracotta", "light_blue_terracotta", "cyan_terracotta",
                                       "light_blue_concrete"])
        hm = "smooth_quartz"
    W = _r(14 * u + 4, 8)
    stufen = [3, 4, 5, 6][g]
    Hs, Ts = _r(5 * u, 4), _r(5 * u, 4)
    D = stufen * Ts + _r(3 * u, 2)
    gras = w.b("grass_block", snowy=False)
    # Fels: Stufenpyramide gegen die Wand (Front bei z = 0, Wand nach -z)
    for x in range(-W, W + 1):
        for z in range(-D, 1):
            tief = -z
            k = min(stufen, tief // Ts + 1)
            h = k * Hs + int(1.2 * u * math.sin(x * 0.4 / u + z * 0.2))
            if abs(x) > W - 3:
                h = int(h * (1 - (abs(x) - (W - 3)) / 4))
            for y in range(0, max(0, h) + 1):
                w.setze(x, y, z, fels(0.5 + 3.5 * y / (stufen * Hs) + w.rng.random() * 0.6, x, y, z))
            if tief % Ts == Ts - 1 or tief == 0:
                pass
    # Häuser auf jeder Terrasse (hinten an der Wand), vorn ein Weg
    glas = "orange_stained_glass" if _stil(seed) == 0 else "light_blue_stained_glass"
    zier = "chiseled_sandstone" if _stil(seed) == 0 else "chiseled_quartz_block"
    for k in range(stufen):
        yb = (k + 1) * Hs + 1
        zfront = -k * Ts
        hb = max(3, Ts - 2)
        zhaus = zfront - Ts + hb
        x = -W + 6
        nr = 0
        while True:
            breite = _r((3 + w.rng.random() * 2) * u, 3)
            if x + breite > W - 6:
                break
            hh = min(Hs + _r(2 * u, 1), _r((3 + w.rng.random() * 2) * u, 3))
            x0, x1 = x, x + breite
            for xx in range(x0, x1 + 1):
                for zz in range(zhaus - hb + 1, zhaus + 1):
                    for yy in range(yb, yb + hh):
                        if not (xx in (x0, x1) or zz in (zhaus - hb + 1, zhaus)):
                            continue
                        fenster = zz == zhaus and yy == yb + hh - 2 and (xx - x0) % 2 == 1 and xx not in (x0, x1)
                        w.setze(xx, yy, zz, w.b(glas) if fenster else haus(1 + 2 * w.rng.random(), xx, yy, zz))
                    w.setze(xx, yb + hh, zz, w.b(hm))
            mx = (x0 + x1) // 2
            for yy, half in ((yb, "lower"), (yb + 1, "upper")):
                w.setze(mx, yy, zhaus, w.b("spruce_door", facing="south", half=half, hinge="left", open=False,
                                           powered=False))
            w.setze(mx, yb + 2, zhaus, w.b(zier))
            if nr % 2 == 0:                       # Kuppel
                rk = (x1 - x0) / 2
                zc = zhaus - hb // 2
                for dx in range(-int(rk) - 1, int(rk) + 2):
                    for dz in range(-int(rk) - 1, int(rk) + 2):
                        for dy in range(0, int(rk * 1.1) + 2):
                            if (dx / rk) ** 2 + (dz / rk) ** 2 + (dy / (rk * 1.1)) ** 2 <= 1:
                                w.setze(mx + dx, yb + hh + 1 + dy, zc + dz,
                                        kuppel(3 * dy / (rk + 1) + w.rng.random() * 0.5, mx + dx, yb + hh + dy, zc + dz))
                w.setze(mx, yb + hh + int(rk * 1.1) + 2, zc, w.b("lightning_rod", facing="up", powered=False,
                                                                  waterlogged=False))
            else:                                  # Dachgarten
                for xx in range(x0, x1 + 1):
                    w.setze(xx, yb + hh + 1, zhaus, w.b("flowering_azalea_leaves", persistent=True, distance=7,
                                                        waterlogged=False))
            laterne(w, x1 + 1, yb, zhaus + 1)
            nr += 1
            x = x1 + _r(2 * u, 2)
        # Treppe hinauf zur nächsten Terrasse (abwechselnd links/rechts)
        if k < stufen - 1:
            seite = 1 if k % 2 == 0 else -1
            for s_ in range(Hs):
                z = zfront - Ts + (Hs - s_)
                for b in range(2):
                    xs = seite * (W - 4 - b)
                    for y in range(yb, yb + s_):
                        w.setze(xs, y, z, w.b(hm))
                    w.setze(xs, yb + s_, z, treppe(w, hm, "north"))
        # Hängende Gärten an der Terrassenkante
        for xx in range(-W + 3, W - 2):
            if w.rng.random() < 0.35:
                for y in range(yb - 1 - _r(2.5 * u, 1), yb - 1):
                    w.setze(xx, y, zfront + 1, w.b("vine", north=True, east=False, south=False, west=False, up=False),
                            ueberschreiben=False)
    # Treppe vom Boden und Becken mit Brunnen davor
    for s_ in range(Hs + 1):
        for b in range(3):
            x = -1 + b
            for y in range(0, s_):
                w.setze(x, y, 1 + Hs - s_, w.b(hm))
            w.setze(x, s_, 1 + Hs - s_, treppe(w, hm, "north"))
    bz = Hs + 4 + int(2 * u)
    for x, z in scheibe(2.5 * u + 1, 0, bz):
        w.setze(x, 0, z, w.b("water", level=0))
    for x, z in kreisrand(2.5 * u + 2, 0, bz):
        w.setze(x, 0, z, w.b(hm))
        w.setze(x, 1, z, platte(w, hm))
    for y in range(0, _r(2 * u, 2) + 1):
        w.setze(0, y, bz, w.b(zier))
    w.setze(0, _r(2 * u, 2) + 1, bz, w.b("water", level=0))
    return w


# ============================================================================ Elfen-Baumstadt

def elfenbaum(seed, g=1):
    """Riesenbaum mit Brettwurzeln, Plattformringen mit Geländern, Wendeltreppe aus Stufen, Pavillon
    mit Kuppel, Hängelaternen und einer leuchtenden Krone."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        rinde = Verlauf(w, "Silberrinde", ["stripped_birch_log", "birch_log", "calcite", "smooth_quartz"])
        blatt = [laub(w, "cherry"), laub(w, "cherry"), laub(w, "birch"), laub(w, "flowering_azalea")]
        holz, licht, dach = "spruce", "pearlescent_froglight", "smooth_quartz"
    else:
        rinde = Verlauf(w, "Dunkelrinde", ["dark_oak_log", "spruce_log", "stripped_dark_oak_log"])
        blatt = [laub(w, "dark_oak"), laub(w, "jungle"), laub(w, "azalea"), laub(w, "dark_oak")]
        holz, licht, dach = "birch", "ochre_froglight", "waxed_oxidized_cut_copper"
    H = 34.0
    S = Skulptur(w, u)
    S.mat("r", rinde, basis=0.3, steigung=2.5 / H, rausch=0.8)

    def blattwahl(x, y, z, *_):
        if w.rng.random() < 0.025:
            return w.b(licht)
        return blatt[int(w.rng.integers(len(blatt)))]
    S.mat("l", blattwahl)
    S.plus(kegel(0, 0, 0, H * 0.78, 2.6, 1.3), "r")
    for i in range(6):
        a = i * math.pi / 3 + 0.3
        S.plus(kap((math.cos(a) * 1.6, 4.5, math.sin(a) * 1.6), (math.cos(a) * 6.5, 0.2, math.sin(a) * 6.5), 1.3, 0.6),
               "r")
    kronen = []
    for i in range(5):
        a = i * 2 * math.pi / 5 + 0.5
        y0 = H * (0.58 + 0.06 * (i % 3))
        ende = (math.cos(a) * 9.5, H * 0.86 + (i % 2) * 2, math.sin(a) * 9.5)
        S.plus(kap((0, y0, 0), ende, 1.1, 0.5), "r")
        kronen.append(ende)
    kronen.append((0, H * 0.98, 0))
    for (cx, cy, cz) in kronen:
        S.plus(lambda X, Y, Z, cx=cx, cy=cy, cz=cz: ((X - cx) / 6.5) ** 2 + ((Y - cy) / 3.6) ** 2 + ((Z - cz) / 6.5) ** 2
               <= 1 + 0.22 * _welle(X * 2, Y * 2, Z * 2), "l")
    S.rendern((-18, 0, -18), (18, H + 5, 18), versatz=(0.5, 0, 0.5))
    # Plattformringe
    for k, f in enumerate((0.26, 0.44, 0.6)):
        y = int(H * f * u)
        rt = (2.6 - 1.3 * f / 0.78) * u
        rp = rt + 3.2 * u + 1
        for x, z in scheibe(rp):
            if math.hypot(x, z) > rt - 0.3:
                w.setze(x, y, z, w.b(f"{holz}_planks"), ueberschreiben=False)
        for x, z in kreisrand(rp + 0.9):
            w.setze(x, y - 1, z, treppe(w, holz, zur_mitte(x, z), "top"), ueberschreiben=False)
        verbinde(w, [(x, y + 1, z) for x, z in kreisrand(rp) if w.frei(x, y + 1, z)], f"{holz}_fence")
        for i, (x, z) in enumerate(kreisrand(rp)):
            if i % max(6, int(8 * u)) == 0:
                w.setze(x, y - 2, z, w.b("chain", axis="y", waterlogged=False), ueberschreiben=False)
                w.setze(x, y - 3, z, w.b("lantern", hanging=True, waterlogged=False), ueberschreiben=False)
        if k == 1:                                   # Pavillon
            a = 0.8
            px, pz = round(math.cos(a) * (rp - 2 * u)), round(math.sin(a) * (rp - 2 * u))
            ph = _r(3 * u, 3)
            for dx in (-1, 1):
                for dz in (-1, 1):
                    for yy in range(y + 1, y + 1 + ph):
                        w.setze(px + dx * _r(u), yy, pz + dz * _r(u), w.b(f"{holz}_fence", north=False, south=False,
                                                                           east=False, west=False, waterlogged=False))
            for dy in range(0, _r(1.5 * u) + 2):
                rr = (_r(u) + 1) * (1 - dy / (_r(1.5 * u) + 2))
                for x, z in scheibe(rr):
                    w.setze(px + x, y + 1 + ph + dy, pz + z, w.b(dach))
    # Wendeltreppe aus Stufen von unten bis zur obersten Plattform
    y_end = int(H * 0.6 * u)
    schritte = int(y_end * 2)
    for s in range(schritte):
        yf = s * 0.5
        a = s * 0.22
        t = yf / (H * 0.78 * u)
        rt = (2.6 - 1.3 * t) * u
        for d in (1.0, 2.0):
            x, z = round(math.cos(a) * (rt + d)), round(math.sin(a) * (rt + d))
            w.setze(x, int(yf), z, platte(w, holz, "top" if yf % 1 >= 0.5 else "bottom"), ueberschreiben=False)
    return w


# ============================================================================ Berghallen-Tor

def berghalle(seed, g=1):
    """Monumentales Tor in einer Bergflanke: Freitreppe, kantige Säulen mit Kapitellen, gestufter Torbogen,
    Goldband mit Muster, geöffnete Torflügel, beleuchtete Halle, Feuerschalen und Schneegipfel."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        berg = Verlauf(w, "Berg", ["deepslate", "cobbled_deepslate", "andesite", "stone", "calcite", "snow_block"])
        bau = Verlauf(w, "Bau", ["polished_deepslate", "deepslate_bricks", "deepslate_tiles"])
        zier, saeule, akzent = "chiseled_deepslate", "polished_deepslate", "gold_block"
    else:
        berg = Verlauf(w, "Berg", ["granite", "terracotta", "andesite", "stone", "calcite", "snow_block"])
        bau = Verlauf(w, "Bau", ["polished_granite", "polished_granite", "bricks"])
        zier, saeule, akzent = "chiseled_stone_bricks", "polished_granite", "waxed_cut_copper"
    W = _r(16 * u + 4, 10)
    H = _r(24 * u + 4, 14)
    Dp = _r(12 * u, 8)
    yg = _r(3 * u, 2)
    tw, th = _r(3 * u, 2), _r(9 * u, 6)
    tief = _r(10 * u, 6)
    for x in range(-W, W + 1):
        top_x = H * (1 - (abs(x) / W) ** 1.4) + 2 * u * math.sin(x * 0.5 / u)
        for z in range(-Dp, 1):
            fz = z + 1.2 * u * (math.sin(x * 0.3 / u) + 1) * 0.5
            h = int(top_x * (1 - 0.15 * (z / -Dp))) if fz <= 0.5 else 0
            for y in range(0, h + 1):
                if abs(x) <= tw and yg <= y <= yg + th and z > -tief:
                    continue                                   # Torgang / Halle
                w.setze(x, y, z, berg(0.4 + 4.8 * (y / H) ** 1.3 + w.rng.random() * 0.6, x, y, z))
    # Freitreppe
    for s in range(yg):
        for x in range(-tw - 2, tw + 3):
            z = yg - s
            for y in range(0, s):
                w.setze(x, y, z, bau(1, x, y, z))
            w.setze(x, s, z, treppe(w, "deepslate_brick" if _stil(seed) == 0 else "polished_granite", "north"))
    for x in range(-tw - 2, tw + 3):
        for z in range(-tief + 1, 1):
            w.setze(x, yg - 1, z, bau(1 + (x + z) % 2, x, yg - 1, z))
    # Säulen mit Kapitellen
    for s in (-1, 1):
        x0 = s * (tw + 1)
        for dx in range(0, _r(2 * u, 2)):
            x = x0 + s * dx
            for y in range(yg, yg + th + _r(3 * u, 2)):
                w.setze(x, y, 1, w.b(saeule))
                w.setze(x, y, 2, w.b(zier) if y % 3 == 0 else w.b(saeule))
            w.setze(x, yg + th + _r(3 * u, 2), 2, w.b(akzent))
        _feuer(w, x0 + s * (_r(2 * u, 2) + 1), yg, 3)
    # Gestufter Bogen und Schmuckband
    for x in range(-tw - 1, tw + 2):
        stufe = (tw + 1 - abs(x))
        for y in range(yg + th - min(stufe, 3) + 1, yg + th + 2):
            w.setze(x, y, 1, w.b(zier) if (x + y) % 2 == 0 else bau(2, x, y, 1))
        for y in (yg + th + 3, yg + th + 4):
            w.setze(x, y, 1, w.b(akzent) if (x + y) % 3 == 0 else w.b(zier))
    # Offene Torflügel an den Seitenwänden des Gangs
    for s in (-1, 1):
        for z in range(-tw, 0):
            for y in range(yg, yg + th - 1):
                w.setze(s * tw, y, z, w.b(akzent) if (y + z) % 4 == 0 else w.b("polished_blackstone_bricks"))
    # Halle: Laternen an den Wänden, Glut am Ende
    for z in range(-tief + 2, -tw, 3):
        for s in (-1, 1):
            w.setze(s * (tw - 1), yg + 2, z, w.b("lantern", hanging=False, waterlogged=False))
    for x in range(-tw + 1, tw):
        w.setze(x, yg, -tief + 1, w.b("shroomlight"))
    return w


# ============================================================================ Wachturm mit Signalfeuer

def wachturm(seed, g=1):
    """Runder Wachturm auf einer Felsnadel: Pechnasen-Kranz, Zinnen, hölzerne Plattform mit
    großem Signalfeuer, Banner und eine Hütte am Fuß."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        fels = Verlauf(w, "Fels", ["tuff", "andesite", "stone", "calcite"])
        mauer = Verlauf(w, "Mauer", ["mossy_stone_bricks", "stone_bricks", "cracked_stone_bricks", "polished_andesite"])
        banner = ["red_wool", "yellow_wool"]
    else:
        fels = Verlauf(w, "Fels", ["deepslate", "cobbled_deepslate", "tuff", "andesite"])
        mauer = Verlauf(w, "Mauer", ["cobbled_deepslate", "deepslate_bricks", "polished_deepslate", "deepslate_tiles"])
        banner = ["blue_wool", "white_wool"]
    Hf = _r(10 * u, 5)
    Rb = 6 * u + 2
    for x in range(-int(Rb) - 2, int(Rb) + 3):
        for z in range(-int(Rb) - 2, int(Rb) + 3):
            a = math.atan2(z, x)
            d = math.hypot(x, z)
            for y in range(0, Hf + 1):
                t = y / Hf
                r = Rb * (1 - 0.45 * t) * (1 + 0.15 * math.sin(5 * a + y * 0.3))
                if d <= r:
                    w.setze(x, y, z, fels(0.5 + 2.5 * t + w.rng.random() * 0.7, x, y, z))
    R = 3 * u + 1
    Ht = _r(13 * u, 7)
    y0 = Hf + 1
    for y in range(y0, y0 + Ht):
        for x, z in kreisrand(R):
            schiess = (y - y0) % 4 == 2 and (x == 0 or z == 0)
            w.setze(x, y, z, w.b("air") if schiess and False else (w.b("iron_bars", north=False, south=False, east=False,
                                                                                  west=False, waterlogged=False)
                                                                  if schiess else mauer(1 + 2 * (y - y0) / Ht +
                                                                                        w.rng.random() * 0.7, x, y, z)))
    yt = y0 + Ht
    for x, z in kreisrand(R + 1):
        w.setze(x, yt, z, treppe(w, "stone_brick", zur_mitte(x, z), "top"))
    for x, z in scheibe(R + 1):
        w.setze(x, yt + 1, z, w.b("spruce_planks"))
    for i, (x, z) in enumerate(kreisrand(R + 1)):
        w.setze(x, yt + 2, z, mauer(2, x, yt + 2, z))
        if i % 2 == 0:
            w.setze(x, yt + 3, z, mauer(2.5, x, yt + 3, z))
    # Signalfeuer
    for x, z in scheibe(max(1, R - 1.5)):
        w.setze(x, yt + 2, z, w.b("hay_block", axis="y") if (x + z) % 2 else w.b("campfire", lit=True,
                                                                                   signal_fire=True, facing="north",
                                                                                   waterlogged=False))
    _feuer(w, 0, yt + 2, 0)
    # Banner am Turm
    for y in range(yt - _r(5 * u, 3), yt):
        w.setze(0, y, int(R) + 1, w.b(banner[(y // 2) % 2]))
    # Hütte am Fuß
    hx, hz = int(Rb) + 2, 0
    for x in range(hx, hx + _r(4 * u, 3) + 1):
        for z in range(-_r(2 * u, 2), _r(2 * u, 2) + 1):
            for y in range(1, _r(2.5 * u, 2) + 1):
                if x in (hx, hx + _r(4 * u, 3)) or abs(z) == _r(2 * u, 2):
                    w.setze(x, y, z, w.b("spruce_planks") if (x + y) % 3 else w.b("stripped_spruce_log", axis="y"))
            w.setze(x, _r(2.5 * u, 2) + 1, z, platte(w, "spruce"))
    laterne(w, hx - 1, 1, 2)
    return w


SAGENLANDE = {
    "schwarzfeste": ("Schwarzfeste", schwarzfeste),
    "glutfeld": ("Glutfeld", glutfeld),
    "huegelhof": ("Hügelhof", huegelhof),
    "felsenstadt": ("Felsterrassenstadt", felsenstadt),
    "elfenbaum": ("Baumstadt", elfenbaum),
    "berghalle": ("Berghallen-Tor", berghalle),
    "wachturm": ("Wachturm mit Signalfeuer", wachturm),
}


from sagen2 import NEU as _NEU  # noqa: E402

SAGENLANDE.update(_NEU)

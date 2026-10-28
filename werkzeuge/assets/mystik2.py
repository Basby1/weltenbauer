"""Mystik – Erweiterung auf 20: Obeliskenring, Portalruine, Runenkreis, Orakelquelle, Schwebende Monolithen,
Astrolabium, Lebensbaum-Schrein, Geisterspiegel, Elementaraltar, Kristallgarten, Zeitturm, Feenring."""

from __future__ import annotations

import math

import numpy as np

import pracht as P
from lib import Rauschen, einfuegen, laub
from mystik import Magie, U, _gras, _plattform, _r, _stil, _welt
from pracht import Mat
from skulptur import Skulptur, ell, kap, kreisrand, scheibe, torus
from spuk import kerze, knorrbaum
from weltwunder import bl, hohl, sk


def _s(m, w, x, y, z, t=None):
    return m.stein(1 + 2 * w.rng.random() if t is None else t, x, y, z)


def obeliskenring(seed, g=2):
    """Obeliskenring: sieben schlanke Obelisken mit leuchtenden Runenbändern im Kreis um eine Sternplattform,
    in der Mitte ein schwebender Kristall."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 8 * u + 5
    _gras(w, R + 4)
    _plattform(w, m, R * 0.45, 2)
    n = 7
    for i in range(n):
        a = i / n * 2 * math.pi
        x0, z0 = round(math.cos(a) * R), round(math.sin(a) * R)
        H = _r(8 * u + 5 + (i % 2) * 2)
        b = 1 if u >= 1.5 else 0
        for y in range(1, H + 1):
            for dx in range(-b, b + 1):
                for dz in range(-b, b + 1):
                    if y > H - 2 and (dx or dz):
                        continue
                    w.setze(x0 + dx, y, z0 + dz, m.rune if y % 4 == 2 and (dx == 0 or dz == 0) and b else
                            _s(m, w, x0 + dx, y, z0 + dz))
        w.setze(x0, H + 1, z0, m.metall(2.5, x0, H + 1, z0))
        w.setze(x0, H + 2, z0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    S = Skulptur(w, 1.0)
    S.mat("k", lambda x, y, z, *_: m.kristall if (x + y + z) % 3 else m.licht)
    yk = 5 + 2 * u
    S.plus(lambda X, Y, Z: np.abs(X) + np.abs(Z) + np.abs(Y - yk) * 0.6 < 1.5 + u, "k")
    S.rendern((-5, 0, -5), (5, 14, 5), versatz=(0.5, 2, 0.5))
    hohl(w, 2)
    return w


def portalruine(seed, g=2):
    """Portalruine: zerfallener Torbogen aus uralten Steinen, im Bogen wabert ein Portal aus Glas und
    weinendem Obsidian, Ranken, umgestürzte Säulen und Splitter."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    B = 3 * u + 2
    H = 7 * u + 4
    _gras(w, _r(B + 8))
    S = Skulptur(w, 1.0)
    S.mat("s", lambda x, y, z, *_: _s(m, w, x, y, z))
    S.mat("g", lambda x, y, z, *_: m.g() if (x * 3 + y) % 5 else m.rune)
    bogen = lambda X, Y, Z: (np.abs(Z) < 1.5) & ((X / (B + 1.8)) ** 2 + (Y / (H + 1.5)) ** 2 < 1) & (Y >= 0)
    innen = lambda X, Y, Z: ((X / B) ** 2 + (Y / H) ** 2 < 1)
    S.plus(lambda X, Y, Z: bogen(X, Y, Z) & ~innen(X, Y, Z), "s")
    S.plus(lambda X, Y, Z: innen(X, Y, Z) & (np.abs(Z) < 0.5) & (Y >= 0), "g")
    S.minus(lambda X, Y, Z: (X > B * 0.3) & (Y > H * 0.75) & (X + Y * 0.3 > B * 0.3 + H * 0.8))
    S.rendern((-B - 3, 0, -2), (B + 3, H + 3, 2), versatz=(0.5, 1, 0.5))
    rng = w.rng
    for i in range(3 + g):
        a = rng.random() * 2 * math.pi
        d = B + 3 + rng.random() * 3
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        L = 3 + int(rng.integers(0, 3))
        ax = "x" if i % 2 else "z"
        for k in range(L):
            w.setze(x + (k if ax == "x" else 0), 1, z + (k if ax == "z" else 0), w.b("quartz_pillar", axis=ax)
                    if m.mond else w.b("polished_basalt", axis=ax))
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 2 and rng.random() < 0.06 and w.frei(x, y - 1, z):
            w.setze(x, y - 1, z, w.b("cave_vines", age=0, berries=rng.random() < 0.3))
    return w


def runenkreis(seed, g=1):
    """Runenkreis: in den Boden eingelassene Ringe aus leuchtenden Runensteinen, konzentrische Symbole aus Glas,
    Steinsitze und ein Pult mit Zauberbuch."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 7 * u + 4
    _gras(w, _r(R + 3))
    for x, z in scheibe(R):
        d = math.hypot(x, z)
        a = math.atan2(z, x)
        if abs(d - R + 0.8) < 0.7 or abs(d - R * 0.6) < 0.6:
            w.setze(x, 0, z, m.rune if int((a + math.pi) * 6) % 3 == 0 else _s(m, w, x, 0, z, 2.0))
        elif abs(d - R * 0.8) < 0.6 and int((a + math.pi) * 8) % 4 == 0:
            w.setze(x, 0, z, m.g())
        else:
            w.setze(x, 0, z, _s(m, w, x, 0, z, 1.2))
    for k in range(6):
        a1, a2 = k / 6 * 2 * math.pi, (k + 2) / 6 * 2 * math.pi
        for t in np.linspace(0, 1, int(R * 2)):
            x = round(math.cos(a1) * R * 0.6 * (1 - t) + math.cos(a2) * R * 0.6 * t)
            z = round(math.sin(a1) * R * 0.6 * (1 - t) + math.sin(a2) * R * 0.6 * t)
            w.setze(x, 0, z, m.licht)
    for i in range(6):
        a = (i + 0.5) / 6 * 2 * math.pi
        x, z = round(math.cos(a) * (R + 1.5)), round(math.sin(a) * (R + 1.5))
        w.setze(x, 1, z, w.b("polished_deepslate_stairs" if m.mond else "polished_blackstone_stairs",
                             facing=("west" if x > 0 else "east") if abs(x) > abs(z) else ("north" if z > 0 else "south"),
                             half="bottom", shape="straight", waterlogged=False))
    w.setze(0, 1, 0, w.b("lectern", facing="south", has_book=True, powered=False))
    return w


def orakelquelle(seed, g=2):
    """Orakelquelle: eine Felsgrotte, aus der eine leuchtende Quelle in ein Stufenbecken fließt, darüber ein
    steinernes Gesicht, Säulenreste und Opferschalen."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 7 * u + 4
    H = 6 * u + 4
    _gras(w, _r(R + 4))
    r_n = Rauschen(w, 3)
    for x in range(-_r(R), _r(R) + 1):
        for z in range(-_r(R), -1):
            d = math.hypot(x, z * 1.3) / R
            hh = int(H * max(0, 1 - d * d) * (0.8 + 0.4 * r_n(x, 0, z)))
            for y in range(1, hh + 1):
                w.setze(x, y, z, _s(m, w, x, y, z, 0.5 + y / H * 2))
            if hh > 0:
                w.setze(x, hh + 1, z, w.b("moss_block") if (x + z) % 3 else w.b("grass_block", snowy=False))
    for k in range(3):
        for x, z in scheibe(R * 0.5 - k * 1.2, 0, round(R * 0.4)):
            w.setze(x, k, z, _s(m, w, x, k, z, 2.0))
        for x, z in scheibe(R * 0.5 - k * 1.2 - 1, 0, round(R * 0.4)):
            w.setze(x, k + 1, z, w.b("water", level=0))
            w.setze(x, k, z, m.licht if (x + z) % 4 == 0 else w.b("prismarine_bricks"))
    S = Skulptur(w, 0.4 * u + 0.25)
    S.mat("k", lambda x, y, z, *_: _s(m, w, x, y, z, 2.5))
    S.mat("g", bl(w, "sea_lantern" if m.mond else "shroomlight"))
    S.plus(ell(0, 6, 0, 4, 5.5, 2.5), "k")
    for sx in (-1, 1):
        S.minus(ell(sx * 1.6, 7.2, 2.2, 0.9, 0.6, 0.6))
        S.plus(ell(sx * 1.6, 7.2, 1.6, 0.6, 0.45, 0.4), "g")
    S.plus(ell(0, 5.5, 2.4, 0.7, 1.4, 0.8), "k")
    S.minus(ell(0, 3.3, 2.4, 1.6, 0.6, 1.0))
    S.rendern((-5, 0, -4), (5, 12, 4), versatz=(0.5, H * 0.4, -1.5))
    for y in range(round(H * 0.4) + 1, 0, -1):
        w.setze(0, y, 0, w.b("water", level=0 if y == round(H * 0.4) + 1 else 8))
    for sx in (-1, 1):
        x = sx * round(R * 0.6)
        for y in range(1, 4 + g):
            w.setze(x, y, round(R * 0.4), w.b("quartz_pillar", axis="y") if m.mond else w.b("polished_basalt", axis="y"))
        w.setze(x, 4 + g, round(R * 0.4), w.b("soul_campfire" if m.mond else "campfire", lit=True, signal_fire=False,
                                             facing="north", waterlogged=False))
    hohl(w, 2)
    return w


def schwebende_monolithen(seed, g=2):
    """Schwebende Monolithen: mächtige Steinquader schweben in einem Ring über einer Runenplattform, verbunden
    durch leuchtende Ketten; in der Mitte eine Säule aus Licht."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 7 * u + 4
    _gras(w, _r(R + 4))
    _plattform(w, m, R * 0.6, 2)
    n = 5 + g
    for i in range(n):
        a = i / n * 2 * math.pi
        x0, z0 = round(math.cos(a) * R), round(math.sin(a) * R)
        y0 = _r(3 * u + 3 + 2 * math.sin(i * 1.7))
        h = _r(5 * u + 3)
        bq = 1 + (u > 1.2)
        for y in range(y0, y0 + h):
            for dx in range(-bq, bq + 1):
                for dz in range(-bq, bq + 1):
                    w.setze(x0 + dx, y, z0 + dz, m.rune if (y - y0) == h // 2 and (dx == 0 or dz == 0) else
                            _s(m, w, x0 + dx, y, z0 + dz))
        for t in np.linspace(0.1, 0.9, int(R)):
            w.setze(round(x0 * (1 - t)), round(y0 + h // 2 + 2 * t), round(z0 * (1 - t)),
                    w.b("chain", axis="x" if abs(x0) > abs(z0) else "z", waterlogged=False))
    for y in range(3, _r(10 * u + 6)):
        w.setze(0, y, 0, m.licht if y % 2 else m.g())
    hohl(w, 2)
    return w


def astrolabium(seed, g=2):
    """Großes Astrolabium: ineinander verschränkte Messing- und Kupferringe in verschiedenen Neigungen um eine
    leuchtende Sonnenkugel, auf einem Sockel mit Sternbildern."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 5 * u + 3
    _gras(w, _r(R + 4))
    _plattform(w, m, R * 0.7, 3)
    S = Skulptur(w, 1.0)
    S.mat("r", lambda x, y, z, *_: m.metall(1 + 2 * w.rng.random(), x, y, z))
    S.mat("g", lambda x, y, z, *_: w.b("gold_block") if (x + y + z) % 2 else w.b("raw_gold_block"))
    S.mat("l", bl(w, "shroomlight" if not m.mond else "sea_lantern"))
    yc = R + 3.5
    for k, (kx, kz) in enumerate(((0.0, 0.0), (0.9, 0.0), (0.0, 0.9), (0.5, -0.5))):
        rr = R * (1 - k * 0.12)

        def ring(X, Y, Z, kx=kx, kz=kz, rr=rr):
            Yr = Y - yc
            ca, sa = math.cos(kx), math.sin(kx)
            Y2 = Yr * ca - Z * sa
            Z2 = Yr * sa + Z * ca
            cb, sb = math.cos(kz), math.sin(kz)
            X3 = X * cb - Y2 * sb
            Y3 = X * sb + Y2 * cb
            return (np.abs(np.sqrt(X3 * X3 + Z2 * Z2) - rr) < 0.6) & (np.abs(Y3) < 0.6)
        S.plus(ring, "r" if k % 2 else "g")
    S.plus(ell(0, yc, 0, 1.6 + u * 0.4, 1.6 + u * 0.4, 1.6 + u * 0.4), "l")
    S.plus(kap((0, 3, 0), (0, yc - 1.5, 0), 0.5, 0.5), "r")
    S.rendern((-R - 2, 0, -R - 2), (R + 2, yc + R + 2, R + 2), versatz=(0.5, 0.01, 0.5))
    return w


def lebensbaum(seed, g=2):
    """Schrein des Lebensbaums: ein uralter weißer Baum mit leuchtenden Blättern auf einer Insel in einem
    Wasserring, Wurzeln schlingen sich um einen Altar."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 8 * u + 4
    _gras(w, _r(R + 3))
    for x, z in scheibe(R):
        d = math.hypot(x, z)
        if R * 0.55 < d < R * 0.8:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("prismarine_bricks"))
    holz = "birch" if m.mond else "cherry"
    enden = knorrbaum(w, 0, 0, 7 * u + 5, holz)
    blatt = "flowering_azalea" if not m.mond else "azalea"
    rng = w.rng
    for (ex, ey, ez) in enden:
        for xx, zz in scheibe(2.2, ex, ez):
            for yy in (ey, ey + 1):
                if rng.random() < 0.75:
                    w.setze(xx, yy, zz, laub(w, "cherry" if not m.mond else blatt) if rng.random() < 0.85 else
                            m.licht)
    for x, z in kreisrand(1.5, 0, round(R * 0.35)):
        w.setze(x, 1, z, _s(m, w, x, 1, z, 2.0))
    w.setze(0, 1, round(R * 0.35), m.rune)
    w.setze(0, 2, round(R * 0.35), w.b("amethyst_cluster", facing="up", waterlogged=False))
    for z in range(round(R * 0.5), round(R * 0.85) + 1):
        w.setze(0, 1, z, w.b(f"{holz}_slab", type="bottom", waterlogged=False))
    return w


def geisterspiegel(seed, g=1):
    """Geisterspiegel: ein hoher, verzierter Spiegelrahmen aus dunklem Stein und Gold steht allein auf einer
    Lichtung, die Spiegelfläche aus getöntem Glas, davor Kerzen und ein Kniekissen."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    B = _r(2 * u + 2, 2)
    H = _r(5 * u + 4)
    _gras(w, _r(B + 7))
    for x in range(-B - 1, B + 2):
        for y in range(1, H + 2):
            rand = abs(x) == B + 1 or y in (1, H + 1)
            if rand:
                w.setze(x, y, 0, m.metall(2.5, x, y, 0) if (x + y) % 3 else _s(m, w, x, y, 0))
            else:
                w.setze(x, y, 0, w.b("tinted_glass") if (x + y) % 4 else m.g())
    for k in range(B + 2):
        w.setze(k - (B + 1) // 2, H + 2 + min(k, B + 1 - k) // 2, 0, m.metall(2.5, 0, 0, 0))
    for sx in (-1, 1):
        w.setze(sx * (B + 2), 1, 1, _s(m, w, 0, 0, 0))
        w.setze(sx * (B + 2), 1, -1, _s(m, w, 0, 0, 0))
    for x in range(-B, B + 1):
        w.setze(x, 1, 2, kerze(w, "white" if m.mond else "purple")) if x % 2 == 0 else None
    w.setze(0, 1, 3, w.b("purple_carpet" if not m.mond else "light_blue_carpet"))
    return w


def elementaraltar(seed, g=2):
    """Elementaraltar: vier Säulen der Elemente – Feuer (Magma, Lagerfeuer), Wasser (Prismarin, Wasserfall),
    Erde (Moos, Wurzeln), Luft (Glas, Endstäbe) – um einen Altar mit schwebender Kugel."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 6 * u + 4
    _gras(w, _r(R + 4))
    _plattform(w, m, R, 2)
    H = _r(6 * u + 4)
    elemente = [("magma_block", "campfire"), ("prismarine_bricks", "sea_lantern"),
                ("moss_block", "flowering_azalea_leaves"), ("white_stained_glass", "end_rod")]
    for i, (mat, top) in enumerate(elemente):
        a = i / 4 * 2 * math.pi + math.pi / 4
        x0, z0 = round(math.cos(a) * R * 0.75), round(math.sin(a) * R * 0.75)
        for y in range(3, 3 + H):
            for x, z in scheibe(1.2, x0, z0):
                w.setze(x, y, z, w.b(mat) if (y + x + z) % 3 else _s(m, w, x, y, z))
        if top == "campfire":
            w.setze(x0, 3 + H, z0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
        elif top == "sea_lantern":
            w.setze(x0, 3 + H, z0, w.b("sea_lantern"))
            for y in range(3, 3 + H):
                w.setze(x0 + 2 * (1 if x0 > 0 else -1), y, z0, w.b("water", level=0 if y == 3 + H - 1 else 8))
        elif top == "end_rod":
            w.setze(x0, 3 + H, z0, w.b("end_rod", facing="up"))
        else:
            for x, z in scheibe(1.8, x0, z0):
                w.setze(x, 3 + H, z, w.b(top, persistent=True, distance=7, waterlogged=False))
    for x, z in scheibe(1.5):
        w.setze(x, 3, z, m.metall(2.5, x, 3, z))
    S = Skulptur(w, 1.0)
    S.mat("k", lambda x, y, z, *_: m.g() if (x + y + z) % 2 else m.licht)
    S.plus(ell(0, 0, 0, 1.4 + u * 0.4, 1.4 + u * 0.4, 1.4 + u * 0.4), "k")
    S.rendern((-4, -4, -4), (4, 4, 4), versatz=(0.5, 6 + u * 1.5, 0.5))
    hohl(w, 2)
    return w


def kristallgarten(seed, g=2):
    """Kristallgarten: ein Feld aus riesigen, schräg aus dem Boden brechenden Kristallen in zwei Farben, dazwischen
    Kristallknospen, leuchtende Flechten und Geodenbrocken."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 10 * u + 5
    _gras(w, R + 2)
    rng = w.rng
    farben = (["light_blue_stained_glass", "cyan_stained_glass", "white_stained_glass", "sea_lantern"] if m.mond else
              ["purple_stained_glass", "magenta_stained_glass", "amethyst_block", "pink_stained_glass"])
    S = Skulptur(w, 1.0)
    S.mat("k", lambda x, y, z, *_: w.b(farben[(x * 3 + y * 5 + z) % len(farben)]))
    n = 6 + 4 * g
    for i in range(n):
        a = i * 2.39996
        d = R * 0.85 * math.sqrt((i + 0.5) / n)
        x0, z0 = math.cos(a) * d, math.sin(a) * d
        L = (5 + 8 * rng.random()) * (0.6 + 0.5 * u)
        rr = 0.9 + 0.9 * u * rng.random() + 0.4
        ka = rng.random() * 2 * math.pi
        nei = 0.2 + 0.5 * rng.random()
        spitze = (x0 + math.cos(ka) * L * nei, L, z0 + math.sin(ka) * L * nei)
        S.plus(kap((x0, -1, z0), spitze, rr, 0.2), "k")
    S.rendern((-R - 3, -1, -R - 3), (R + 3, 12 * u + 6, R + 3), versatz=(0.5, 0.01, 0.5))
    for x, z in scheibe(R):
        if w.frei(x, 1, z) and rng.random() < 0.06:
            w.setze(x, 1, z, w.b("amethyst_cluster", facing="up", waterlogged=False) if not m.mond else
                     w.b("glow_lichen", down=True, up=False, north=False, south=False, east=False, west=False,
                         waterlogged=False))
    return w


def zeitturm(seed, g=2):
    """Turm der Zeit: schlanker Turm mit einer gewaltigen Sanduhr aus Glas an der Spitze (oben Sand, unten
    Sand rieselnd), Zahnräder an den Seiten und Zifferblatt-Fenster."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 2.4 * u + 2
    H = _r(12 * u + 6)
    _gras(w, _r(R + 7))
    for y in range(1, H + 1):
        for x, z in kreisrand(R):
            w.setze(x, y, z, _s(m, w, x, y, z, 0.5 + 2 * y / H))
    for k in range(-round(R) + 1, round(R)):
        for j in range(-round(R) + 1, round(R)):
            if k * k + j * j < (R - 1) ** 2:
                pass
    yc = round(H * 0.7)
    for x, z in scheibe(R - 0.4, 0, 0):
        pass
    for dx in range(-round(R) + 1, round(R)):
        for dy in range(-round(R) + 1, round(R)):
            if dx * dx + dy * dy <= (R - 1) ** 2:
                w.setze(dx, yc + dy, round(R), w.b("white_concrete") if dx * dx + dy * dy < (R - 1.5) ** 2 else
                        m.metall(2.5, dx, yc + dy, 0))
    w.setze(0, yc, round(R) + 1, w.b("black_concrete"))
    for k in range(round(R) - 1):
        w.setze(0, yc + k, round(R) + 1, w.b("black_concrete"))
        w.setze(k, yc, round(R) + 1, w.b("black_concrete")) if k < round(R) - 2 else None
    S = Skulptur(w, 1.0)
    S.mat("g", bl(w, "glass"))
    S.mat("s", bl(w, "sand"))
    S.mat("r", lambda x, y, z, *_: m.metall(2.5, x, y, z))
    Hs = 6 * u + 4
    Rs = 2.5 * u + 1.5

    def huelle(X, Y, Z):
        t = np.abs(Y - Hs / 2) / (Hs / 2)
        rr = 0.6 + (Rs - 0.6) * t ** 1.2
        return (np.sqrt(X * X + Z * Z) <= rr) & (Y >= 0) & (Y <= Hs)
    S.plus(lambda X, Y, Z: huelle(X, Y, Z) & (np.sqrt(X * X + Z * Z) > (0.6 + (Rs - 0.6) *
                                                                         (np.abs(Y - Hs / 2) / (Hs / 2)) ** 1.2) - 1.0),
           "g")
    S.plus(lambda X, Y, Z: huelle(X, Y, Z) & (Y > Hs * 0.62) & (Y < Hs * 0.85), "s")
    S.plus(lambda X, Y, Z: huelle(X, Y, Z) & (Y < Hs * 0.2), "s")
    S.plus(lambda X, Y, Z: (np.sqrt(X * X + Z * Z) < 0.5) & (Y > Hs * 0.2) & (Y < Hs * 0.62), "s")
    for yy in (-0.5, Hs + 0.5):
        S.plus(lambda X, Y, Z, yy=yy: (np.sqrt(X * X + Z * Z) < Rs + 0.8) & (np.abs(Y - yy) < 0.6), "r")
    for a in range(4):
        px, pz = math.cos(a * math.pi / 2 + 0.78) * (Rs + 0.3), math.sin(a * math.pi / 2 + 0.78) * (Rs + 0.3)
        S.plus(kap((px, 0, pz), (px, Hs, pz), 0.4, 0.4), "r")
    S.rendern((-Rs - 2, -1, -Rs - 2), (Rs + 2, Hs + 2, Rs + 2), versatz=(0.5, H + 1.01, 0.5))
    import modbloecke as MB
    for sx in (-1, 1):
        w.setze(sx * round(R + 1), round(H * 0.45), 0, MB.zahnrad(w, "x", gross=True))
        w.setze(sx * round(R + 1), round(H * 0.3), 1, MB.zahnrad(w, "x", gross=False))
    hohl(w, 2)
    return w


def feenring(seed, g=1):
    """Feenring: ein Kreis aus leuchtenden Pilzen und Froschlichtern auf moosigem Grund, Glühwürmchen
    (Endstäbe), ein kleiner Steinsitz und schwebende Lichtkugeln."""
    w = _welt(seed)
    m = Magie(w, seed)
    u = U[g]
    R = 5 * u + 3
    _gras(w, _r(R + 5))
    rng = w.rng
    for x, z in scheibe(R + 3):
        if math.hypot(x, z) < R + 1:
            w.setze(x, 0, z, w.b("moss_block"))
    for x, z in kreisrand(R):
        r = rng.random()
        if r < 0.35:
            w.setze(x, 1, z, w.b("red_mushroom") if rng.random() < 0.5 else w.b("brown_mushroom"))
        elif r < 0.6:
            hh = 1 + int(rng.integers(0, 2 + g))
            for y in range(1, hh + 1):
                w.setze(x, y, z, w.b("mushroom_stem", up=True, down=True, north=True, south=True, east=True,
                                     west=True))
            w.setze(x, hh + 1, z, w.b("shroomlight") if rng.random() < 0.5 else
                    w.b(["ochre_froglight", "verdant_froglight", "pearlescent_froglight"][int(rng.integers(3))],
                        axis="y"))
    for i in range(8 + 4 * g):
        a = rng.random() * 2 * math.pi
        d = rng.random() * R * 1.4
        w.setze(round(math.cos(a) * d), 2 + int(rng.integers(0, 4 + g)), round(math.sin(a) * d),
                w.b("end_rod", facing="up") if rng.random() < 0.7 else m.licht)
    w.setze(0, 1, 0, w.b("mossy_cobblestone_slab", type="bottom", waterlogged=False))
    for x, z in scheibe(R - 1):
        if w.frei(x, 1, z) and rng.random() < 0.15:
            w.setze(x, 1, z, w.b(["lily_of_the_valley", "azure_bluet", "fern", "pink_petals"][int(rng.integers(3))]))
    return w


NEU = {
    "obeliskenring": ("Obeliskenring", obeliskenring),
    "portalruine": ("Portalruine", portalruine),
    "runenkreis": ("Runenkreis", runenkreis),
    "orakelquelle": ("Orakelquelle", orakelquelle),
    "schwebende_monolithen": ("Schwebende Monolithen", schwebende_monolithen),
    "astrolabium": ("Großes Astrolabium", astrolabium),
    "lebensbaum": ("Schrein des Lebensbaums", lebensbaum),
    "geisterspiegel": ("Geisterspiegel", geisterspiegel),
    "elementaraltar": ("Elementaraltar", elementaraltar),
    "kristallgarten": ("Kristallgarten", kristallgarten),
    "zeitturm": ("Turm der Zeit", zeitturm),
    "feenring": ("Feenring", feenring),
}

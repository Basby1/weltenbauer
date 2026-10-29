"""Zukunftsstadt – gläserne Wolkenkratzer, Spiraltürme, Biodome, Magnetschwebebahn, Raumhafen, Solar- und
Windparks, vertikale Gärten, Neonstraßen, Wohnwaben, Fusionskraftwerk, Teleporter und Weltraumlift.
Boden y = 0."""

from __future__ import annotations

import math

import numpy as np

from flora import _lv, _neu, _r, _stil, linie
from lib import Rauschen

U = [0.6, 1.0, 1.7, 2.8]

NEON = [["cyan_stained_glass", "light_blue_concrete", "sea_lantern"],
        ["magenta_stained_glass", "pink_concrete", "pearlescent_froglight"]]


def neon(w, seed, k=0):
    n = NEON[_stil(seed)][k]
    return w.b(n, axis="y") if n.endswith("froglight") else w.b(n)


def boden(w, R, rund=True, muster=True):
    """Glatter Stadtboden mit Fugenraster und Leuchtpunkten."""
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if rund and math.hypot(x, z) > R:
                continue
            if muster and x % 8 == 0 and z % 8 == 0:
                blk = "sea_lantern"
            elif muster and (x % 8 == 0 or z % 8 == 0):
                blk = "light_gray_concrete"
            else:
                blk = "smooth_stone" if (x // 4 + z // 4) % 2 else "polished_andesite"
            w.setze(x, 0, z, w.b(blk))


def strasse(w, x0, x1, z, breite=3, achse="x", lampen=True):
    for a in range(x0, x1 + 1):
        for d in range(-breite, breite + 1):
            x, zz = (a, z + d) if achse == "x" else (z + d, a)
            if abs(d) == breite:
                blk = "light_gray_concrete"
            elif d == 0 and a % 4 < 2:
                blk = "white_concrete"
            else:
                blk = "gray_concrete" if (a + d) % 7 else "black_concrete"
            w.setze(x, 0, zz, w.b(blk))
        if lampen and a % 8 == 0:
            for s in (-1, 1):
                x, zz = (a, z + s * (breite + 1)) if achse == "x" else (z + s * (breite + 1), a)
                for y in range(1, 5):
                    w.setze(x, y, zz, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                          waterlogged=False) if y < 4 else w.b("end_rod", facing="up"))


def glasturm(w, cx, cz, y0, B, T, H, seed, rahmen="white_concrete", glas="light_blue_stained_glass", band=4,
             krone=True, abstufung=0):
    """Rechteckiger Glasturm mit weißen Eckrahmen, Geschossbändern, optional zurückgestuft."""
    stufen = [(B, T, H)]
    if abstufung:
        stufen = [(B - k * abstufung, T - k * abstufung, H * (1 - k * 0.25)) for k in range(3)]
    y = y0
    for (b, t, h) in stufen:
        b, t = max(2, round(b)), max(2, round(t))
        h = max(4, round(h - (y - y0)))
        for yy in range(y, y + h):
            for x in range(cx - b, cx + b + 1):
                for z in range(cz - t, cz + t + 1):
                    rand_x, rand_z = x in (cx - b, cx + b), z in (cz - t, cz + t)
                    if not (rand_x or rand_z):
                        if (yy - y0) % band == 0:
                            w.setze(x, yy, z, w.b("light_gray_concrete"))
                        continue
                    if rand_x and rand_z:
                        blk = rahmen
                    elif (yy - y0) % band == 0:
                        blk = rahmen if (yy - y0) % (band * 3) else "sea_lantern"
                    else:
                        blk = glas
                    w.setze(x, yy, z, w.b(blk))
        y += h
        if y >= y0 + H:
            break
    if krone:
        for x in range(cx - 1, cx + 2):
            for z in range(cz - 1, cz + 2):
                w.setze(x, y, z, w.b("iron_block"))
        for k in range(_r(H * 0.15) + 2):
            w.setze(cx, y + 1 + k, cz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False)
                    if k < _r(H * 0.15) + 1 else w.b("redstone_lamp", lit=True))
    return y


def spiralturm(w, cx, cz, y0, R, H, seed, drehung=1.4, glas="light_blue_stained_glass"):
    """Verdrehter Turm: Grundriss ein abgerundetes Quadrat, das sich mit der Höhe dreht."""
    for y in range(y0, y0 + H):
        t = (y - y0) / H
        a0 = t * drehung
        r = R * (1 - 0.25 * t)
        punkte = set()
        for k in range(int(r * 10)):
            a = k / (r * 10) * 6.28
            # Superellipse
            c, s = math.cos(a), math.sin(a)
            rr = r / ((abs(c) ** 4 + abs(s) ** 4) ** 0.25)
            x = c * rr * math.cos(a0) - s * rr * math.sin(a0)
            z = c * rr * math.sin(a0) + s * rr * math.cos(a0)
            punkte.add((cx + round(x), cz + round(z)))
        for (x, z) in punkte:
            ecke = (y - y0) % 4 == 0
            w.setze(x, y, z, w.b("white_concrete" if ecke else glas))
        if (y - y0) % 4 == 0:
            for x in range(cx - int(r), cx + int(r) + 1):
                for z in range(cz - int(r), cz + int(r) + 1):
                    if (x - cx) ** 2 + (z - cz) ** 2 < (r - 1) ** 2:
                        w.setze(x, y, z, w.b("light_gray_concrete"), False)
    yt = y0 + H
    for k in range(_r(H * 0.2)):
        w.setze(cx, yt + k, cz, w.b("end_rod", facing="up") if k % 3 else w.b("iron_block"))


def glaskuppel(w, cx, cz, y0, R, rahmen="white_concrete", glas="glass", innen_gruen=False):
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            for y in range(0, int(R) + 2):
                d = math.sqrt(x * x + y * y + z * z)
                if R - 1 < d <= R:
                    a = math.atan2(z, x)
                    gitter = abs(math.sin(a * 6)) < 0.18 or y % 4 == 0
                    w.setze(cx + x, y0 + y, cz + z, w.b(rahmen if gitter else glas))
                elif innen_gruen and d < R - 1 and y == 0:
                    w.setze(cx + x, y0, cz + z, w.b("grass_block", snowy=False))


def schwebebahn(w, x0, x1, z, y, achse="x", stuetzen=8):
    for a in range(x0, x1 + 1):
        for d in (-1, 0, 1):
            x, zz = (a, z + d) if achse == "x" else (z + d, a)
            w.setze(x, y, zz, w.b("white_concrete" if d else "light_gray_concrete"))
            if d == 0:
                w.setze(x, y + 1, zz, w.b("iron_block") if a % 2 else w.b("polished_blackstone_slab",
                                                                             type="bottom", waterlogged=False))
        if a % stuetzen == 0:
            x, zz = (a, z) if achse == "x" else (z, a)
            for yy in range(1, y):
                w.setze(x, yy, zz, w.b("white_concrete") if yy % 4 else w.b("sea_lantern"))


def zug(w, x0, z, y, L, achse="x", farbe="white_concrete"):
    for a in range(x0, x0 + L):
        for d in (-1, 0, 1):
            for yy in range(y, y + 3):
                x, zz = (a, z + d) if achse == "x" else (z + d, a)
                rand = abs(d) == 1 or yy == y + 2 or a in (x0, x0 + L - 1)
                if not rand:
                    continue
                fenster = yy == y + 1 and abs(d) == 1 and a % 3
                w.setze(x, yy, zz, w.b("light_blue_stained_glass" if fenster else farbe))
    w.setze(x0 + L, y + 1, z, w.b("light_blue_stained_glass")) if achse == "x" else None


# ============================================================================ Bauten

def glaswolkenkratzer(seed, g=2):
    """Gläserner Wolkenkratzer: ein hoher, zurückgestufter Turm mit weißen Rahmen, Leuchtbändern, Dachgarten und
    Antenne auf einer Plaza mit Brunnen."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    boden(w, R)
    glasturm(w, 0, 0, 1, 5 * u + 2, 4 * u + 2, _r(40 * u + 10), seed, abstufung=_r(1.5 * u, 1),
             glas="light_blue_stained_glass" if _stil(seed) == 0 else "tinted_glass")
    for x in range(-2, 3):
        for z in range(R - 6, R - 2):
            w.setze(x, 0, z, w.b("water", level=0) if abs(x) < 2 and R - 6 < z < R - 3 else w.b("smooth_quartz"))
    return w


def spiralturm_bau(seed, g=2):
    """Spiralturm: ein verdrehter Turm, dessen Geschosse sich Stockwerk für Stockwerk drehen, mit Glasfassade und
    Lichtspitze."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    boden(w, R)
    spiralturm(w, 0, 0, 1, 5 * u + 2.5, _r(44 * u + 10), seed, glas="light_blue_stained_glass" if _stil(seed) == 0
               else "cyan_stained_glass")
    return w


def biodome(seed, g=2):
    """Biodome: drei verbundene Glaskuppeln mit Regenwald, Wüste und Bergwiese im Inneren, Verbindungsröhren und
    Eingangshalle."""
    import wald2
    from lib import einfuegen
    w = _neu(seed)
    u = U[g]
    R = _r(20 * u + 6)
    boden(w, R)
    kuppeln = [(-R * 0.45, -R * 0.2, 7 * u + 3, "jungle"), (R * 0.45, -R * 0.2, 6 * u + 3, "wueste"),
               (0, R * 0.4, 5 * u + 3, "wiese")]
    for cx, cz, r, art in kuppeln:
        cx, cz = round(cx), round(cz)
        glaskuppel(w, cx, cz, 0, r, innen_gruen=True)
        if art == "jungle":
            einfuegen(w, wald2.dschungelriese(seed, H=_r(r * 1.1)), cx, 0, cz)
        elif art == "wueste":
            for x in range(-int(r) + 2, int(r) - 1):
                for z in range(-int(r) + 2, int(r) - 1):
                    if x * x + z * z < (r - 2) ** 2:
                        w.setze(cx + x, 0, cz + z, w.b("sand"))
            for k in range(4):
                a = k * 1.57
                for y in range(1, 4):
                    w.setze(cx + round(math.cos(a) * r * 0.4), y, cz + round(math.sin(a) * r * 0.4), w.b("cactus", age=0))
        else:
            einfuegen(w, wald2.birke(seed, H=_r(r * 0.8)), cx, 0, cz)
    for (ax, az, _, _), (bx, bz, _, _) in ((kuppeln[0], kuppeln[1]), (kuppeln[0], kuppeln[2]),
                                           (kuppeln[1], kuppeln[2])):
        linie(w, (ax, 2, az), (bx, 2, bz), w.b("glass"), 1.2)
    return w


def magnetbahnhof(seed, g=2):
    """Magnetbahnhof: ein geschwungenes Bahnhofsdach aus Glas und Stahl über erhöhten Gleisen, ein Zug am Bahnsteig,
    Aufzüge und Anzeigetafeln."""
    w = _neu(seed)
    u = U[g]
    L = _r(20 * u + 8)
    boden(w, L, rund=False)
    y = _r(6 * u + 3)
    for z in (-3, 3):
        schwebebahn(w, -L, L, z, y)
    for x in range(-L // 2, L // 2 + 1):
        for z in range(-7, 8):
            if abs(z) >= 5:
                w.setze(x, y, z, w.b("smooth_quartz"))
        for k in range(15):
            z = -7 + k
            hb = y + 6 + round(2 * math.cos(z / 7 * 1.4))
            w.setze(x, hb, z, w.b("glass") if x % 4 else w.b("white_concrete"))
    for x in range(-L // 2, L // 2 + 1, 6):
        for z in (-7, 7):
            for yy in range(1, y + 7):
                w.setze(x, yy, z, w.b("white_concrete"))
    zug(w, -L // 3, -3, y + 2, _r(16 * u + 4), farbe="white_concrete" if _stil(seed) == 0 else "red_concrete")
    for x in (-L // 2 - 2, L // 2 + 2):
        for yy in range(1, y + 1):
            for d in (-1, 0, 1):
                w.setze(x, yy, 6 + d, w.b("glass") if d else w.b("iron_block"))
    return w


def schwebebahnstrecke(seed, g=1):
    """Schwebebahnstrecke: ein gerades Stück aufgeständerte Magnetbahn mit Leuchtstützen über einer Straße –
    kachelbar für lange Strecken."""
    w = _neu(seed)
    u = U[g]
    L = [12, 18, 28, 40][g]
    strasse(w, -L, L, 0, breite=3)
    schwebebahn(w, -L, L, 0, _r(7 * u + 4))
    return w


def raumhafen(seed, g=2):
    """Raumhafen: kreisrunde Landeplattformen mit Leuchtmarkierungen, ein Kontrollturm mit Glaskanzel, ein
    startbereites Shuttle und Treibstofftanks."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    boden(w, R)
    for k, (cx, cz) in enumerate(((-R * 0.4, -R * 0.3), (R * 0.4, -R * 0.3), (0, R * 0.4))):
        cx, cz = round(cx), round(cz)
        rp = 6 * u + 3
        for x in range(-int(rp), int(rp) + 1):
            for z in range(-int(rp), int(rp) + 1):
                d = math.hypot(x, z)
                if d <= rp:
                    blk = "yellow_concrete" if abs(d - rp * 0.7) < 0.6 else "sea_lantern" if d > rp - 1 and \
                        (x + z) % 3 == 0 else "gray_concrete"
                    w.setze(cx + x, 1, cz + z, w.b(blk))
        if k == 0:
            _shuttle(w, cx, cz, 2, u, seed)
    glasturm(w, round(R * 0.6), round(R * 0.5), 1, 2, 2, _r(16 * u + 5), seed, krone=False)
    yt = _r(16 * u + 5) + 1
    for x in range(-4, 5):
        for z in range(-4, 5):
            if x * x + z * z <= 16:
                for y in (yt, yt + 1, yt + 2):
                    if y == yt or x * x + z * z > 9:
                        w.setze(round(R * 0.6) + x, y, round(R * 0.5) + z,
                                w.b("white_concrete" if y == yt else "light_blue_stained_glass"))
    for k in range(3):
        x = -round(R * 0.7) + k * 4
        for y in range(1, _r(6 * u + 2)):
            for d in range(-1, 2):
                for e in range(-1, 2):
                    if abs(d) + abs(e) < 2:
                        w.setze(x + d, y, round(R * 0.6) + e, w.b("white_concrete" if y % 3 else "orange_concrete"))
    return w


def _shuttle(w, cx, cz, y0, u, seed):
    H = _r(18 * u + 6)
    for y in range(y0, y0 + H):
        t = (y - y0) / H
        r = (2.2 * u + 1) * (1 if t < 0.75 else (1 - (t - 0.75) / 0.25) ** 0.6)
        for x in range(-4, 5):
            for z in range(-4, 5):
                if x * x + z * z <= r * r:
                    blk = "white_concrete" if not (y - y0) % 5 == 2 else "black_concrete"
                    if t > 0.9:
                        blk = "red_concrete" if _stil(seed) == 0 else "blue_concrete"
                    w.setze(cx + x, y, cz + z, w.b(blk))
    for k in range(3):
        a = k / 3 * 6.28
        for j in range(_r(5 * u + 2)):
            x = cx + round(math.cos(a) * (2.2 * u + 1 + j * 0.5))
            z = cz + round(math.sin(a) * (2.2 * u + 1 + j * 0.5))
            w.setze(x, y0 + j // 2, z, w.b("light_gray_concrete"))
    for x in range(-1, 2):
        for z in range(-1, 2):
            w.setze(cx + x, y0, cz + z, w.b("magma_block"))


def shuttle(seed, g=2):
    """Raumfähre: eine startbereite Rakete mit Finnen und Spitze auf einer Startrampe mit Versorgungsturm,
    Schläuchen und Flutlicht."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    boden(w, R)
    for x in range(-int(4 * u) - 2, int(4 * u) + 3):
        for z in range(-int(4 * u) - 2, int(4 * u) + 3):
            w.setze(x, 1, z, w.b("gray_concrete") if (x + z) % 4 else w.b("yellow_concrete"))
    _shuttle(w, 0, 0, 2, u, seed)
    tx = round(4 * u) + 3
    for y in range(1, _r(20 * u + 6)):
        for dx in (0, 2):
            for dz in (-1, 1):
                w.setze(tx + dx, y, dz, w.b("red_concrete" if (y // 3) % 2 else "white_concrete"))
        if y % 5 == 0:
            for x in range(round(2.2 * u + 1), tx + 3):
                w.setze(x, y, 0, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
    return w


def solarpark(seed, g=1):
    """Solarpark: lange Reihen schräg gestellter Solarpaneele auf Stelzen, ein Wechselrichterhaus und
    Wartungswege."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            w.setze(x, 0, z, w.b("grass_block", snowy=False) if z % 6 else w.b("gravel"))
    for z in range(-R + 2, R - 1, 6):
        for x in range(-R + 2, R - 1):
            if x % 4 == 0:
                w.setze(x, 1, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
            for d in range(3):
                w.setze(x, 2 + d // 2, z - 1 + d, w.b("daylight_detector", inverted=False, power=0) if d == 0 else
                        w.b("blue_stained_glass") if d == 1 else w.b("light_blue_stained_glass"))
    glasturm(w, R - 4, -R + 4, 1, 2, 2, 4, seed, krone=False)
    return w


def windpark(seed, g=2):
    """Windpark: hohe weiße Windräder mit drei schlanken Rotorblättern auf einem Hügel, Umspannstation und
    Wartungsweg."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
    n = 3
    for i in range(n):
        cx = round(-R * 0.6 + i * R * 0.6)
        cz = round(math.sin(i * 2) * R * 0.3)
        H = _r(20 * u + 8)
        for y in range(1, H):
            r = 1.0 if y < H * 0.5 else 0.6
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if dx * dx + dz * dz <= r * r + 0.1:
                        w.setze(cx + dx, y, cz + dz, w.b("white_concrete"))
        for dz in (-1, 0, 1, 2):
            w.setze(cx, H, cz + dz, w.b("white_concrete"))
        w.setze(cx, H, cz + 3, w.b("light_gray_concrete"))
        L = _r(10 * u + 4)
        for k in range(3):
            a = k / 3 * 6.28 + i
            for j in range(1, L):
                x = cx + round(math.cos(a) * j)
                y = H + round(math.sin(a) * j)
                w.setze(x, y, cz + 3, w.b("white_concrete" if j < L - 2 else "red_concrete"))
    return w


def vertikaler_garten(seed, g=2):
    """Vertikaler Garten: ein Wohnturm, dessen Balkone über und über mit Bäumen, Sträuchern und Ranken bepflanzt
    sind – ein senkrechter Wald mitten in der Stadt."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    boden(w, R)
    B = _r(4 * u + 2)
    H = _r(36 * u + 8)
    glasturm(w, 0, 0, 1, B, B, H, seed, glas="glass")
    rng = w.rng
    for y in range(4, H, 4):
        versatz = (y // 4) % 4
        for k in range(-B - 2, B + 3):
            for (x, z) in ((k, B + 1 + (versatz == 0)), (k, -B - 1 - (versatz == 1)),
                           (B + 1 + (versatz == 2), k), (-B - 1 - (versatz == 3), k)):
                w.setze(x, y, z, w.b("smooth_quartz_slab", type="top", waterlogged=False), False)
                if rng.random() < 0.6:
                    w.setze(x, y + 1, z, _lv(w, ["oak", "azalea", "flowering_azalea", "birch"][int(rng.integers(4))]),
                            False)
                if rng.random() < 0.15:
                    for d in range(1, 3):
                        w.setze(x, y + 1 + d, z, _lv(w, "oak"), False)
                if rng.random() < 0.1:
                    for d in range(1, 4):
                        w.setze(x, y - d, z, w.b("vine", north=z < 0, south=z > 0, east=False, west=False, up=False)
                                if abs(z) > abs(x) else w.b("vine", east=x > 0, west=x < 0, north=False, south=False,
                                                            up=False), False)
    return w


def hydrokultur(seed, g=1):
    """Hydrokultur-Farm: ein Gewächshaus aus Glas mit gestapelten, beleuchteten Pflanzregalen, Wassertanks und
    Rohrleitungen."""
    w = _neu(seed)
    u = U[g]
    L, B = _r(10 * u + 4), _r(6 * u + 3)
    boden(w, L + 3, rund=False)
    H = _r(7 * u + 3)
    for x in range(-L, L + 1):
        for z in range(-B, B + 1):
            for y in range(1, H + 1):
                if abs(x) == L or abs(z) == B or y == H:
                    w.setze(x, y, z, w.b("white_concrete" if (x % 4 == 0 and abs(z) == B) or (y == H and x % 4 == 0)
                                         else "glass"))
    for z in range(-B + 2, B - 1, 3):
        for x in range(-L + 2, L - 1):
            for y in range(1, H - 1, 2):
                w.setze(x, y, z, w.b("white_concrete") if y % 4 == 1 else w.b("light_gray_concrete"))
                w.setze(x, y + 1, z, w.b(["wheat", "carrots", "beetroots", "potatoes"][(x + y) % 4],
                                         age=3 if (x + y) % 4 == 2 else 7) if False else
                        _lv(w, ["oak", "azalea", "jungle"][(x + y) % 3]))
            w.setze(x, H - 1, z, w.b("sea_lantern")) if x % 3 == 0 else None
    for k in range(2):
        for y in range(1, H):
            for d in (-1, 0, 1):
                w.setze(L + 3 + k * 3, y, d, w.b("light_blue_stained_glass") if d else w.b("water", level=0)
                        if y < H - 1 else w.b("iron_block"))
    return w


def holoplaza(seed, g=2):
    """Holo-Plaza: ein kreisrunder Platz mit Lichtsäulen, einer schwebenden Hologramm-Kugel über einem Wasserbecken,
    Sitzbänken aus Glas und Leuchtringen im Boden."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    boden(w, R)
    for k in range(3):
        r = R * (0.3 + k * 0.2)
        for j in range(int(r * 7)):
            a = j / (r * 7) * 6.28
            w.setze(round(math.cos(a) * r), 0, round(math.sin(a) * r), neon(w, seed, 2))
    for x in range(-4, 5):
        for z in range(-4, 5):
            if x * x + z * z <= 16:
                w.setze(x, 0, z, w.b("water", level=0))
    rk = 2.5 * u + 1.5
    yk = _r(8 * u + 4)
    for x in range(-int(rk) - 1, int(rk) + 2):
        for y in range(-int(rk) - 1, int(rk) + 2):
            for z in range(-int(rk) - 1, int(rk) + 2):
                d = math.sqrt(x * x + y * y + z * z)
                if rk - 1 < d <= rk and (abs(math.sin(math.atan2(z, x) * 5)) < 0.3 or y % 2 == 0):
                    w.setze(x, yk + y, z, neon(w, seed, 0))
    w.setze(0, yk, 0, neon(w, seed, 2))
    for k in range(8):
        a = k / 8 * 6.28
        x, z = round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8)
        for y in range(1, _r(6 * u + 3)):
            w.setze(x, y, z, w.b("white_concrete") if y % 3 else neon(w, seed, 2))
    return w


def neonstrasse(seed, g=2):
    """Neonstraße: eine nächtliche Häuserschlucht mit leuchtenden Schildern in Pink und Cyan, Läden mit
    Glasfronten, Kabeln und Lampen über der Straße."""
    w = _neu(seed)
    u = U[g]
    L = _r(18 * u + 6)
    strasse(w, -L, L, 0, breite=3, lampen=False)
    rng = w.rng
    for s in (-1, 1):
        x = -L
        while x < L:
            b = int(rng.integers(3, 6))
            h = _r((8 + rng.random() * 14) * u + 4)
            z0 = s * 5
            for xx in range(x, min(L, x + b * 2)):
                for z in range(z0, z0 + s * 7, s):
                    for y in range(1, h + 1):
                        rand = xx in (x, min(L, x + b * 2) - 1) or z in (z0, z0 + s * 6) or y == h
                        if rand:
                            front = z == z0
                            if y == h:
                                blk = "gray_concrete"
                            elif front:
                                blk = "light_blue_stained_glass" if y < 4 else "gray_concrete" if y % 3 else \
                                    "tinted_glass"
                            else:
                                blk = ("yellow_stained_glass" if (xx + z) % 5 == 0 else "tinted_glass") \
                                    if y % 3 == 2 else ["gray_concrete", "cyan_terracotta", "light_gray_concrete"][
                                        (x // 3) % 3]
                            w.setze(xx, y, z, w.b(blk))
            for y in range(5, h - 1, 4):
                w.setze(x + b, y, z0 - s, neon(w, seed, int(rng.integers(2))) if rng.random() < 0.6 else
                        w.b(["magenta_stained_glass", "lime_stained_glass", "yellow_stained_glass"][
                            int(rng.integers(3))]))
            x += b * 2 + 1
    for x in range(-L, L + 1, 6):
        for z in range(-4, 5):
            w.setze(x, _r(9 * u + 4), z, w.b("chain", axis="z", waterlogged=False))
        w.setze(x, _r(9 * u + 4) - 1, 0, w.b("lantern", hanging=True, waterlogged=False))
    return w


def wohnwaben(seed, g=2):
    """Wohnwaben: ein Gebirge aus gestapelten, sechseckigen Wohnkapseln mit runden Fenstern, Balkonen und Pflanzen,
    verbunden durch Treppen und Aufzüge."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    boden(w, R)
    rng = w.rng
    r = _r(2.5 * u + 1.5, 2)
    h = _r(3 * u + 2, 3)
    for ebene in range(int(3 + 2 * u)):
        n = int(6 - ebene)
        for i in range(max(1, n)):
            a = i / max(1, n) * 6.28 + ebene * 0.5
            d = (R * 0.55) * (1 - ebene / (4 + 2 * u))
            cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
            y0 = 1 + ebene * h
            for y in range(y0, y0 + h):
                for k in range(6):
                    a1 = k / 6 * 6.28
                    a2 = (k + 1) / 6 * 6.28
                    for t in np.linspace(0, 1, r * 2 + 2):
                        x = cx + round(r * (math.cos(a1) * (1 - t) + math.cos(a2) * t))
                        z = cz + round(r * (math.sin(a1) * (1 - t) + math.sin(a2) * t))
                        fenster = y == y0 + h // 2 and k % 2 == 0
                        w.setze(x, y, z, w.b("light_blue_stained_glass" if fenster else
                                             ["white_concrete", "light_gray_concrete", "white_terracotta"][
                                                 (ebene + i) % 3]))
            for x in range(cx - r, cx + r + 1):
                for z in range(cz - r, cz + r + 1):
                    if (x - cx) ** 2 + (z - cz) ** 2 <= r * r:
                        w.setze(x, y0 + h, z, w.b("smooth_quartz_slab", type="bottom", waterlogged=False), False)
            if rng.random() < 0.5:
                w.setze(cx, y0 + h, cz, _lv(w, "azalea"), False)
    for y in range(1, int(3 + 2 * u) * h):
        w.setze(0, y, 0, w.b("glass") if y % 4 else w.b("iron_block"))
    return w


def forschungslabor(seed, g=2):
    """Forschungslabor: ein flaches, ringförmiges Laborgebäude mit Glasdach um einen Innenhof mit Teilchenring,
    Antennenschüssel auf dem Dach und Laborgärten."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    boden(w, R)
    Ri, Ra = R * 0.45, R * 0.75
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if Ri <= d <= Ra:
                for y in range(1, 6):
                    aussen = d > Ra - 1 or d < Ri + 1
                    if y == 5:
                        w.setze(x, y, z, w.b("glass") if not aussen else w.b("white_concrete"))
                    elif aussen:
                        w.setze(x, y, z, w.b("white_concrete" if y in (1, 4) else "light_blue_stained_glass"))
    for k in range(int(Ri * 7)):
        a = k / (Ri * 7) * 6.28
        r = Ri * 0.6
        w.setze(round(math.cos(a) * r), 1, round(math.sin(a) * r), w.b("iron_block"))
        w.setze(round(math.cos(a) * r), 2, round(math.sin(a) * r), neon(w, seed, 0) if k % 3 else w.b("sea_lantern"))
    sx = round(Ra * 0.85)
    for y in range(6, 9):
        w.setze(sx, y, 0, w.b("iron_block"))
    for x in range(-3, 4):
        for z in range(-3, 4):
            d = math.hypot(x, z)
            if d <= 3:
                w.setze(sx + x, 9 + round(d * d * 0.15), z, w.b("white_concrete"))
    return w


def fusionskraftwerk(seed, g=2):
    """Fusionskraftwerk: eine gewaltige Kugel in einem Ring aus Magnetspulen, leuchtende Plasmaadern,
    Kühltürme mit Dampf und Hochspannungsleitungen."""
    w = _neu(seed)
    u = U[g]
    R = _r(20 * u + 6)
    boden(w, R)
    rk = 7 * u + 3
    cy = rk + 2
    for x in range(-int(rk) - 1, int(rk) + 2):
        for y in range(-int(rk) - 1, int(rk) + 2):
            for z in range(-int(rk) - 1, int(rk) + 2):
                d = math.sqrt(x * x + y * y + z * z)
                if rk - 1.2 < d <= rk:
                    band = abs(y) < 1 or abs(math.sin(math.atan2(z, x) * 4)) < 0.12
                    w.setze(x, cy + y, z, w.b("sea_lantern" if band else "light_gray_concrete" if (x + y + z) % 5
                                              else "iron_block"))
    for k in range(int(rk * 8)):
        a = k / (rk * 8) * 6.28
        for dy in (-1, 0, 1):
            w.setze(round(math.cos(a) * (rk + 2)), cy + dy, round(math.sin(a) * (rk + 2)),
                    w.b("copper_block" if dy == 0 else "waxed_cut_copper"))
    for k in range(2):
        cx = round(R * 0.65) * (1 if k else -1)
        cz = -round(R * 0.5)
        H = _r(12 * u + 5)
        for y in range(1, H + 1):
            t = y / H
            r = (3 * u + 1.5) * (1 - 0.35 * math.sin(t * math.pi))
            for j in range(int(r * 7) + 4):
                a = j / (r * 7 + 4) * 6.28
                w.setze(cx + round(math.cos(a) * r), y, cz + round(math.sin(a) * r), w.b("light_gray_concrete"))
        for j in range(int(6 * u)):
            w.setze(cx + int(w.rng.integers(-2, 3)), H + 1 + int(w.rng.integers(0, 4)), cz + int(w.rng.integers(-2, 3)),
                    w.b("white_stained_glass"), False)
    return w


def roboterstatue(seed, g=2):
    """Roboterstatue: ein riesiger, glänzender Roboter mit kantigem Kopf, leuchtendem Visier, Gelenkarmen und
    Schulterlampen, der über die Stadt wacht."""
    from kreaturen import SICHT, glied
    from skulptur import Skulptur, ell, kap, kasten
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    boden(w, R)
    S = Skulptur(w, u)
    S.mat("m", lambda x, y, z, *_: w.b("iron_block") if (x + y) % 5 else w.b("light_gray_concrete"))
    S.mat("w", w.b("white_concrete"))
    S.mat("l", neon(w, seed, 2))
    S.mat("g", neon(w, seed, 0))
    for sx in (-1, 1):
        S.plus(kasten(sx * 2.8 - 1.2, 0, -1.2, sx * 2.8 + 1.2, 8, 1.4), "m")
        S.plus(kasten(sx * 2.8 - 1.5, 0, -1.6, sx * 2.8 + 1.5, 1.2, 2.2), "w")
        S.plus(ell(sx * 2.8, 8.5, 0, 1.4, 1.2, 1.4), "w")
        glied(S, [(sx * 5.5, 16, 0), (sx * 6.8, 12, 1.5), (sx * 6.0, 9, 3.5)], [1.3, 1.1, 1.0], "m")
        S.plus(kasten(sx * 6.0 - 1, 7.5, 3.0, sx * 6.0 + 1, 9.5, 4.5), "w")
        S.plus(ell(sx * 5.5, 17, 0, 1.8, 1.4, 1.8), "w")
        S.plus(ell(sx * 5.5, 18.6, 0, 0.5, 0.5, 0.5), "l")
    S.plus(kasten(-4, 9, -2.5, 4, 17.5, 2.5), "m")
    S.plus(kasten(-2.5, 12, 2.4, 2.5, 15, 2.8), "g")
    S.plus(kasten(-2.2, 18, -2.2, 2.2, 22, 2.2), "w")
    S.plus(kasten(-1.8, 19.6, 2.1, 1.8, 20.4, 2.5), "l")
    S.plus(kap((0, 22, 0), (0, 25, 0), 0.25), "m")
    S.plus(ell(0, 25.3, 0, 0.5, 0.5, 0.5), "l")
    S.rendern((-9, -1, -5), (9, 27, 7), versatz=(0.5, 1.01, 0.5), dreh=SICHT)
    return w


def flugtaxiturm(seed, g=2):
    """Flugtaxi-Turm: ein schlanker Turm mit auskragenden runden Landeplattformen in verschiedenen Höhen, an
    denen schwebende Flugtaxis andocken."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    boden(w, R)
    H = _r(36 * u + 8)
    spiralturm(w, 0, 0, 1, 2.5 * u + 1.5, H, seed, drehung=0.3)
    for k in range(4):
        y = round(H * (0.3 + k * 0.17))
        a = k * 1.9
        cx, cz = round(math.cos(a) * (5 * u + 3)), round(math.sin(a) * (5 * u + 3))
        rp = 2.5 * u + 1.5
        linie(w, (0, y, 0), (cx, y, cz), w.b("white_concrete"), 0.6)
        for x in range(-int(rp), int(rp) + 1):
            for z in range(-int(rp), int(rp) + 1):
                d = math.hypot(x, z)
                if d <= rp:
                    w.setze(cx + x, y, cz + z, w.b("sea_lantern" if d > rp - 1 and (x + z) % 2 else "gray_concrete"))
        if k % 2 == 0:
            for x in range(-1, 2):
                for z in range(-2, 3):
                    w.setze(cx + x, y + 1, cz + z, w.b("yellow_concrete" if abs(z) < 2 else "black_concrete"))
            w.setze(cx, y + 2, cz, w.b("light_blue_stained_glass"))
    return w


def skybridge(seed, g=2):
    """Skybridge: zwei Glastürme, hoch oben verbunden durch eine gläserne Brücke mit Café, darunter eine begrünte
    Plaza."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    boden(w, R)
    H = _r(34 * u + 8)
    B = _r(3 * u + 2)
    for sx in (-1, 1):
        glasturm(w, sx * round(R * 0.5), 0, 1, B, B, H - (sx > 0) * 4, seed,
                 glas="light_blue_stained_glass" if sx < 0 else "cyan_stained_glass")
    yb = round(H * 0.7)
    for x in range(-round(R * 0.5) + B, round(R * 0.5) - B + 1):
        for z in range(-2, 3):
            for y in range(yb, yb + 4):
                if abs(z) == 2 or y in (yb, yb + 3):
                    w.setze(x, y, z, w.b("white_concrete" if y == yb else "glass"))
    import wald2
    from lib import einfuegen
    for k in range(3):
        einfuegen(w, wald2.laubbaum(int(w.rng.integers(1, 10 ** 6)), "oak", H=_r(5 * u + 3)), -4 + k * 4, 0, R // 2)
    return w


def arkologie(seed, g=3):
    """Arkologie: eine gewaltige Stufenpyramide als Stadt in einem Gebäude – Terrassen mit Gärten, Glasfassaden,
    Lichtbänder und ein Gipfelobservatorium."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    boden(w, R + 2, rund=False)
    stufen = int(5 + 2 * u)
    sh = _r(2.5 * u + 2)
    rng = w.rng
    for k in range(stufen):
        r = R - k * (R / stufen)
        y0 = 1 + k * sh
        for x in range(-int(r), int(r) + 1):
            for z in range(-int(r), int(r) + 1):
                rand = max(abs(x), abs(z)) >= int(r) - 1
                for y in range(y0, y0 + sh):
                    if rand:
                        w.setze(x, y, z, w.b("light_blue_stained_glass" if (y - y0) % sh else "white_concrete"))
                if max(abs(x), abs(z)) == int(r) - 2 and rng.random() < 0.5:
                    w.setze(x, y0 + sh, z, _lv(w, "azalea" if rng.random() < 0.6 else "flowering_azalea"))
                else:
                    if max(abs(x), abs(z)) >= int(r) - 3:
                        w.setze(x, y0 + sh - 1, z, w.b("smooth_quartz"), False)
    glaskuppel(w, 0, 0, 1 + stufen * sh, 3 * u + 1.5)
    return w


def teleporter(seed, g=1):
    """Teleporter: ein senkrechter Ring aus Stahl und Leuchtsegmenten, darin ein schimmerndes Feld, auf einer
    Plattform mit Steuerpult und Energiekabeln."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    boden(w, R)
    rr = 4 * u + 2.5
    yc = rr + 2
    for k in range(int(rr * 10)):
        a = k / (rr * 10) * 6.28
        for dr in (0, 1):
            x, y = round(math.cos(a) * (rr + dr)), round(yc + math.sin(a) * (rr + dr))
            w.setze(x, y, 0, w.b("iron_block") if k % 6 else neon(w, seed, 2))
            w.setze(x, y, 1, w.b("light_gray_concrete"))
    for x in range(-int(rr) + 1, int(rr)):
        for y in range(round(yc - rr) + 1, round(yc + rr)):
            if x * x + (y - yc) ** 2 < (rr - 1) ** 2:
                w.setze(x, y, 0, w.b("purple_stained_glass" if (x + y) % 3 else "magenta_stained_glass")
                        if _stil(seed) else w.b("light_blue_stained_glass" if (x + y) % 3 else "cyan_stained_glass"))
    for x in range(-2, 3):
        w.setze(x, 1, 4, w.b("polished_blackstone_slab", type="bottom", waterlogged=False))
    w.setze(0, 2, 4, w.b("lectern", facing="north", has_book=False, powered=False))
    return w


def datenzentrum(seed, g=1):
    """Datenzentrum: ein fensterloser Block mit Reihen blinkender Serverschränke im Inneren (aufgeschnitten),
    Kühlaggregaten auf dem Dach und Glasfaserkanälen."""
    w = _neu(seed)
    u = U[g]
    L, B = _r(10 * u + 4), _r(7 * u + 3)
    boden(w, L + 3, rund=False)
    H = _r(5 * u + 3)
    for x in range(-L, L + 1):
        for z in range(-B, B + 1):
            for y in range(1, H + 1):
                if (abs(x) == L or abs(z) == B or y == H) and not (x > 0 and z > 0 and y > 1):
                    w.setze(x, y, z, w.b("gray_concrete" if y < H else "light_gray_concrete"))
    for z in range(-B + 2, B - 1, 3):
        for x in range(-L + 2, L - 1):
            for y in range(1, H - 1):
                w.setze(x, y, z, w.b("black_concrete") if (x + y) % 3 else neon(w, seed, 0) if (x + y + z) % 2
                        else w.b("lime_stained_glass"))
    for x in range(-L + 2, L - 1, 4):
        for z in (-B + 2, B - 3):
            w.setze(x, H + 1, z, w.b("iron_block"))
            w.setze(x, H + 2, z, w.b("iron_trapdoor", facing="north", half="bottom", open=False, powered=False,
                                     waterlogged=False))
    return w


def zukunftspark(seed, g=2):
    """Park der Zukunft: geschwungene Wege mit Leuchtkanten, geometrische Hecken, Bäume in Glaskugeln,
    Lichtskulpturen und ein Spiegelteich."""
    import wald2
    from lib import einfuegen
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
    for k in range(int(R * 8)):
        t = k / (R * 8)
        a = t * 6.28 * 1.5
        r = R * (0.2 + 0.7 * t)
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        for d in (-1, 0, 1):
            w.setze(x + d, 0, z, w.b("smooth_quartz"))
        w.setze(x + 2, 0, z, neon(w, seed, 2)) if k % 5 == 0 else None
    for k in range(3):
        a = k * 2.1
        cx, cz = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        einfuegen(w, wald2.laubbaum(int(w.rng.integers(1, 10 ** 6)), "oak", H=_r(4 * u + 2), breit=0.6), cx, 0, cz)
        glaskuppel(w, cx, cz, 0, 4 * u + 2.5)
    for x in range(-3, 4):
        for z in range(-3, 4):
            if x * x + z * z < 10:
                w.setze(x, 0, z, w.b("water", level=0))
    for k in range(4):
        a = k * 1.57 + 0.8
        x, z = round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8)
        for y in range(1, _r(4 * u + 2)):
            w.setze(x + (y % 2), y, z, neon(w, seed, k % 2))
    return w


def weltraumlift(seed, g=3):
    """Weltraumlift: die Basisstation eines Weltraumaufzugs – ein massiver Ankerturm, aus dem ein Kabel mit
    Kabinen senkrecht in den Himmel führt, umgeben von Hangars."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    boden(w, R)
    H = _r(20 * u + 8)
    for y in range(1, H + 1):
        r = (4 * u + 2) * (1 - 0.6 * y / H)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(x, z)
                if r - 1 < d <= r:
                    w.setze(x, y, z, w.b("white_concrete" if y % 5 else "sea_lantern"))
    for y in range(H, H + _r(40 * u + 20)):
        w.setze(0, y, 0, w.b("chain", axis="y", waterlogged=False))
        if y % _r(12 * u + 6) == 0:
            for x in range(-1, 2):
                for z in range(-1, 2):
                    for yy in (y, y + 1):
                        w.setze(x, yy, z, w.b("light_blue_stained_glass" if yy == y + 1 and (x or z) else
                                              "white_concrete"))
    for k in range(3):
        a = k / 3 * 6.28 + 0.5
        cx, cz = round(math.cos(a) * R * 0.7), round(math.sin(a) * R * 0.7)
        for x in range(-4, 5):
            for z in range(-3, 4):
                for y in range(1, 6):
                    if abs(x) == 4 or abs(z) == 3 or y == 5:
                        hb = 5 - round((x / 4.5) ** 2 * 2)
                        if y <= hb:
                            w.setze(cx + x, y, cz + z, w.b("light_gray_concrete"))
    return w


def schwebeplattform(seed, g=2):
    """Schwebende Stadtplattform: eine runde Plattform mit Glastürmen und Garten schwebt auf Antigrav-Düsen über dem
    Boden, darunter leuchtende Triebwerke."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    Y = _r(10 * u + 5)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z)
            if d <= R:
                w.setze(x, Y, z, w.b("smooth_quartz" if d < R - 1 else "white_concrete"))
                tief = int((1 - d / R) * 4 * u)
                for y in range(Y - tief, Y):
                    w.setze(x, y, z, w.b("light_gray_concrete"))
    for k in range(6):
        a = k / 6 * 6.28
        x, z = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        tief = int((1 - 0.6) * 4 * u)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                w.setze(x + dx, Y - tief - 1, z + dz, neon(w, seed, 2))
    glasturm(w, -round(R * 0.3), 0, Y + 1, 2, 2, _r(14 * u + 4), seed)
    glasturm(w, round(R * 0.35), round(R * 0.2), Y + 1, 2, 3, _r(9 * u + 3), seed, glas="cyan_stained_glass")
    for x in range(-R // 2, R // 2):
        for z in range(R // 3, R - 1):
            if math.hypot(x, z) < R - 1:
                w.setze(x, Y, z, w.b("grass_block", snowy=False))
    return w


def strassenkreuzung(seed, g=1):
    """Straßenkreuzung: eine Kreuzung zweier Stadtstraßen mit Zebrastreifen, Leuchtpollern und Lampen –
    kachelbar mit der Schwebebahnstrecke."""
    w = _neu(seed)
    L = [12, 18, 28, 40][g]
    boden(w, L, rund=False)
    strasse(w, -L, L, 0, breite=3)
    strasse(w, -L, L, 0, breite=3, achse="z")
    for d in range(-2, 3):
        for k in range(-3, 4, 2):
            for e in (4, 5):
                w.setze(k, 0, e, w.b("white_concrete"))
                w.setze(k, 0, -e, w.b("white_concrete"))
                w.setze(e, 0, k, w.b("white_concrete"))
                w.setze(-e, 0, k, w.b("white_concrete"))
    return w


ZUKUNFT = {
    "glaswolkenkratzer": ("Gläserner Wolkenkratzer", glaswolkenkratzer),
    "spiralturm": ("Spiralturm", spiralturm_bau),
    "biodome": ("Biodome", biodome),
    "magnetbahnhof": ("Magnetbahnhof", magnetbahnhof),
    "schwebebahnstrecke": ("Schwebebahnstrecke", schwebebahnstrecke),
    "raumhafen": ("Raumhafen", raumhafen),
    "shuttle": ("Raumfähre auf Startrampe", shuttle),
    "solarpark": ("Solarpark", solarpark),
    "windpark": ("Windpark", windpark),
    "vertikaler_garten": ("Vertikaler Garten", vertikaler_garten),
    "hydrokultur": ("Hydrokultur-Farm", hydrokultur),
    "holoplaza": ("Holo-Plaza", holoplaza),
    "neonstrasse": ("Neonstraße", neonstrasse),
    "wohnwaben": ("Wohnwaben", wohnwaben),
    "forschungslabor": ("Forschungslabor", forschungslabor),
    "fusionskraftwerk": ("Fusionskraftwerk", fusionskraftwerk),
    "roboterstatue": ("Roboterstatue", roboterstatue),
    "flugtaxiturm": ("Flugtaxi-Turm", flugtaxiturm),
    "skybridge": ("Skybridge", skybridge),
    "arkologie": ("Arkologie", arkologie),
    "teleporter": ("Teleporter", teleporter),
    "datenzentrum": ("Datenzentrum", datenzentrum),
    "zukunftspark": ("Park der Zukunft", zukunftspark),
    "weltraumlift": ("Weltraumlift", weltraumlift),
    "schwebeplattform": ("Schwebende Stadtplattform", schwebeplattform),
    "strassenkreuzung": ("Straßenkreuzung", strassenkreuzung),
}

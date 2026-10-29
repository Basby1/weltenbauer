"""Sumpf & Moor – Moorseen, Sumpfzypressen, Pfahlhütten, Knüppeldämme, Irrlichter, versunkene Ruinen,
Biberdamm und kombinierbare Sumpfstücke. Boden/Wasserspiegel y = 0."""

from __future__ import annotations

import math

import pracht as P
import wald2
from flora import SZ, _lv, _neu, _r, _stil, bogen, linie
from lib import Rauschen, einfuegen
from wald import Stueck, _fertig, hohes, zuckerrohr

U = [0.6, 1.0, 1.7, 2.8]


def _zaun(w, art="spruce"):
    return w.b(f"{art}_fence", north=False, south=False, east=False, west=False, waterlogged=False)


# ============================================================================ Bausteine

def sumpfgrund(w, R, cx=0, cz=0, wasser=0.45, zelle=5.0, rand=True, moor=False, rauh=None):
    """Mosaik aus offenem Wasser, Schlamm, Moos und Gras bei y = 0. Gibt {(x, z): 'w'|'m'|'l'} zurück."""
    rn = rauh or Rauschen(w, zelle)
    rf = Rauschen(w, 1.5)
    karte = {}
    for x in range(int(cx - R) - 2, int(cx + R) + 3):
        for z in range(int(cz - R) - 2, int(cz + R) + 3):
            d = math.hypot(x - cx, z - cz) / R
            if d > 1.0 + 0.12 * rf(x, 0, z):
                continue
            v = rn(x, 0, z) * 0.8 + rf(x, 0, z) * 0.2
            if rand:
                v += max(0, d - 0.75) * 1.2
            if v < wasser:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud") if (x + z) % 3 else w.b("clay"))
                karte[(x, z)] = "w"
            elif v < wasser + 0.1:
                w.setze(x, 0, z, w.b("mud"))
                karte[(x, z)] = "m"
            else:
                if moor:
                    blk = ["moss_block", "grass_block", "podzol", "moss_block", "rooted_dirt"][int(rf(x, 3, z) * 4.99)]
                else:
                    blk = ["grass_block", "grass_block", "moss_block", "podzol", "coarse_dirt"][int(rf(x, 3, z) * 4.99)]
                w.setze(x, 0, z, w.b(blk, snowy=False) if blk in ("grass_block", "podzol") else w.b(blk))
                karte[(x, z)] = "l"
            w.setze(x, -1, z, w.b("mud") if karte[(x, z)] != "l" else w.b("dirt"), False)
    return karte


def bewachsen(w, karte, dichte=0.45, moor=False):
    """Schilf, Rohrkolben, Gras, Farne, Wollgras, Seerosen und Tropfblatt auf dem Sumpfgrund."""
    rng = w.rng
    if not hasattr(w, "folgen"):
        w.folgen = {}
    for (x, z), t in karte.items():
        if not w.frei(x, 1, z):
            continue
        r = rng.random()
        if t == "w":
            if r < 0.06:
                w.setze(x, 1, z, w.b("lily_pad"))
            elif r < 0.09:
                w.setze(x, 0, z, w.b("seagrass") if False else w.b("water", level=0))
        elif t == "m":
            if r < 0.25:
                zuckerrohr(w, x, 1, z)
            elif r < 0.45:
                w.setze(x, 1, z, w.b("big_dripleaf", facing=["north", "east", "south", "west"][int(r * 40) % 4],
                                     tilt="none", waterlogged=False))
        else:
            if r < dichte * 0.3:
                hohes("tall_grass")(w, x, 1, z)
            elif r < dichte * 0.6:
                w.setze(x, 1, z, w.b("grass"))
            elif r < dichte * 0.75:
                w.setze(x, 1, z, w.b("fern"))
            elif r < dichte * 0.85:
                w.setze(x, 1, z, w.b("white_wool") if moor and rng.random() < 0.3 else w.b("moss_carpet"))
            elif r < dichte * 0.9:
                w.setze(x, 1, z, w.b(["blue_orchid", "brown_mushroom", "dandelion"][int(r * 97) % 3],
                                     **({"facing": "north", "half": "lower", "waterlogged": False}
                                        if int(r * 97) % 3 == 2 else {})))
    return w


def zypresse(w, x0, z0, H, y0=1, moos=True):
    """Sumpfzypresse: verbreiterter Stammfuß mit Kniewurzeln, schmaler Stamm, flache Schirmkrone in Etagen,
    lange Bartflechten."""
    rng = w.rng
    for y in range(y0 - 1, y0 + H):
        r = 1.6 if y < y0 + 2 else (1.0 if y < y0 + 4 else 0.5)
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if dx * dx + dz * dz <= r * r:
                    w.setze(x0 + dx, y, z0 + dz, w.b("spruce_wood" if y < y0 + 2 else "spruce_log", axis="y"))
    for k in range(5):
        a = rng.random() * 6.28
        d = 2.5 + rng.random() * 2
        x, z = round(x0 + math.cos(a) * d), round(z0 + math.sin(a) * d)
        for y in range(y0 - 1, y0 + 1 + (k % 2)):
            w.setze(x, y, z, w.b("spruce_wood", axis="y"))
    for e in range(3):
        y = y0 + H - 1 - e * max(2, H // 6)
        rk = 2.5 + e * 1.4 + H * 0.08
        for k in range(4):
            a = k * 1.57 + e * 0.6
            linie(w, (x0, y - 1, z0), (x0 + math.cos(a) * rk * 0.8, y, z0 + math.sin(a) * rk * 0.8),
                  w.b("spruce_log", axis="y"))
        for dx in range(-int(rk) - 1, int(rk) + 2):
            for dz in range(-int(rk) - 1, int(rk) + 2):
                for dy in (0, 1):
                    if (dx * dx + dz * dz) <= rk * rk * (1 - dy * 0.45) and rng.random() < 0.85:
                        w.setze(x0 + dx, y + dy, z0 + dz, _lv(w, "spruce" if (dx + dz) % 3 else "dark_oak"),
                                False)
                if moos and dx * dx + dz * dz <= rk * rk and rng.random() < 0.07:
                    for d in range(int(2 + rng.integers(int(3 + H * 0.15)))):
                        w.setze(x0 + dx, y - 1 - d, z0 + dz, w.b("vine", north=True, south=False, east=False,
                                                                 west=False, up=False), False)


def totbaum(w, x0, z0, H, y0=1, holz="dark_oak"):
    """Abgestorbener, kahler Baum mit verdrehten Ästen."""
    rng = w.rng
    for y in range(y0, y0 + H):
        w.setze(x0, y, z0, w.b(f"{holz}_log", axis="y"))
    for k in range(int(3 + H / 4)):
        y = y0 + H // 3 + int(rng.random() * H * 0.65)
        a = rng.random() * 6.28
        L = 2 + rng.random() * H * 0.35
        end = (x0 + math.cos(a) * L, y + L * 0.6, z0 + math.sin(a) * L)
        linie(w, (x0, y, z0), end, w.b(f"{holz}_log", axis="y"))
        if rng.random() < 0.5:
            a2 = a + 0.8
            linie(w, end, (end[0] + math.cos(a2) * 2, end[1] + 1.5, end[2] + math.sin(a2) * 2),
                  w.b(f"{holz}_fence", north=False, south=False, east=False, west=False, waterlogged=False))


def hoehe(w, x, z):
    return max([p[1] for p in w.bloecke if p[0] == x and p[2] == z] + [0])


def pfahlhaus(w, cx, cz, a, b, y0, stil, etagen=1, dach="mcw_stroh", tuer="south"):
    for x in range(cx - a - 1, cx + a + 2):
        for z in range(cz - b - 1, cz + b + 2):
            w.setze(x, y0 - 1, z, w.b("spruce_planks") if (x + z) % 4 else w.b("stripped_spruce_log", axis="x"))
            if (x - cx) % 2 == 0 and (z - cz) % 2 == 0 and (abs(x - cx) >= a or abs(z - cz) >= b):
                for y in range(-1, y0 - 1):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
    for x in range(cx - a - 1, cx + a + 2):
        for z in (cz - b - 1, cz + b + 1):
            w.setze(x, y0, z, _zaun(w), False)
    wand = ["spruce_planks", "dark_oak_planks", "stripped_spruce_log", "mud_bricks"] if stil == 0 else \
        ["mangrove_planks", "spruce_planks", "stripped_mangrove_log", "packed_mud"]
    st = P.Stil(w, wand=wand, sockel="holz_dunkel", gesims="stone_brick", dach=dach, holz="spruce", laeden=True,
                blumen=0.3)
    P.gebaeude(w, st, cx - a, cz - b, cx + a, cz + b, y0=y0, etagen=etagen, eh=4, dach="sattel", tuer=tuer,
               gauben=False, kamine=1, sockel_h=0, steil=True)


def steg(w, pts, y=1, holz="spruce", breite=1):
    """Bohlensteg entlang Punkte (x, z), Pfosten alle paar Blöcke."""
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        n = max(abs(bx - ax), abs(bz - az), 1)
        for k in range(n + 1):
            x, z = round(ax + (bx - ax) * k / n), round(az + (bz - az) * k / n)
            for d in range(-breite + 1, breite):
                if abs(bx - ax) >= abs(bz - az):
                    w.setze(x, y, z + d, w.b(f"{holz}_slab", type="bottom", waterlogged=False))
                else:
                    w.setze(x + d, y, z, w.b(f"{holz}_slab", type="bottom", waterlogged=False))
            if k % 3 == 0:
                w.setze(x, y - 1, z, w.b(f"{holz}_log", axis="y"))
                w.setze(x, y - 2, z, w.b(f"{holz}_log", axis="y"))


def irrlicht(w, x, y, z):
    w.setze(x, y, z, w.b("soul_lantern", hanging=False, waterlogged=False) if (x + z) % 2 else
            w.b("verdant_froglight", axis="y"))


# ============================================================================ Bauten

def moorsee(seed, g=2):
    """Moorsee: ein dunkler, runder See in einem Hochmoor aus Torfmoos, Wollgras und Heide, Krüppelkiefern und
    ein umgestürzter Stamm am Ufer."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    rn = Rauschen(w, 4)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z) / R
            if d > 1.05:
                continue
            if d < 0.55 + 0.1 * rn(x, 0, z):
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
                w.setze(x, -2, z, w.b("mud"))
            else:
                w.setze(x, 0, z, w.b(["moss_block", "moss_block", "podzol", "rooted_dirt", "grass_block"][
                    int(rn(x, 5, z) * 4.99)], **({"snowy": False} if int(rn(x, 5, z) * 4.99) in (2, 4) else {})))
                r = w.rng.random()
                if r < 0.12:
                    w.setze(x, 1, z, w.b("white_wool") if r < 0.05 else w.b("cobweb"))
                elif r < 0.3:
                    w.setze(x, 1, z, w.b("moss_carpet"))
                elif r < 0.42:
                    w.setze(x, 1, z, w.b(["sweet_berry_bush", "fern", "dead_bush"][int(r * 50) % 3],
                                         **({"age": 2} if int(r * 50) % 3 == 0 else {})))
    for k in range(3 + g):
        a = k / (3 + g) * 6.28 + 0.4
        x, z = round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8)
        einfuegen(w, wald2.jungbaum(int(w.rng.integers(1, 10 ** 6)), "spruce", H=_r(4 * u + 2)), x, 0, z)
    einfuegen(w, wald2.totholz(int(w.rng.integers(1, 10 ** 6)), "dark_oak"), round(R * 0.5), 0, -round(R * 0.2))
    return w


def sumpfhuette(seed, g=1):
    """Sumpfhütte: eine kleine Pfahlhütte mit steilem Strohdach über dem Wasser, Steg, Netze, Krebsreusen und ein
    Einbaum am Pfahl."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    karte = sumpfgrund(w, R, wasser=0.62)
    bewachsen(w, karte)
    a, b = _r(2 * u + 1, 2), _r(2 * u + 1, 2)
    pfahlhaus(w, 0, 0, a, b, 3, _stil(seed))
    steg(w, [(0, b + 2), (0, R - 1)], y=2)
    for k in range(3):
        w.setze(a + 2, 2, -b + k * 2, w.b("barrel", facing="up", open=False))
    for y in range(3, 6):
        w.setze(-a - 2, y, b + 1, w.b("cobweb"))
    for x in range(-2, 3):
        w.setze(x + a + 3, 0, b + 3, w.b("spruce_log", axis="x") if abs(x) < 2 else w.b("spruce_slab",
                                                                                          type="bottom",
                                                                                          waterlogged=True))
    return w


def schilfkate(seed, g=1):
    """Fischerkate im Schilf: ein langes Reetdachhaus auf einer Insel im Schilfgürtel, Trockengestelle mit
    Fischen, Kähne am Ufer und ein Räucherofen."""
    w = _neu(seed)
    u = U[g]
    R = _r(13 * u + 6)
    karte = sumpfgrund(w, R, wasser=0.5, zelle=7)
    for x in range(-R // 2, R // 2 + 1):
        for z in range(-R // 3, R // 3 + 1):
            if (x / (R / 2)) ** 2 + (z / (R / 3)) ** 2 < 1:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
                karte[(x, z)] = "l"
    for (x, z), t in karte.items():
        if t != "l" and w.rng.random() < 0.55 and math.hypot(x, z) > R * 0.45:
            for y in range(1, 3 + (x + z) % 2):
                w.setze(x, y, z, w.b("sugar_cane", age=0), False)
    a, b = _r(4 * u + 1, 3), _r(2 * u + 1, 2)
    st = P.Stil(w, wand=["mud_bricks", "packed_mud", "stripped_oak_log", "mud_bricks"], sockel="graustein",
                gesims="stone_brick", dach="mcw_stroh", holz="oak", laeden=True, blumen=0.4)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=4, dach="sattel", tuer="south", gauben=False, kamine=1,
               steil=True)
    for x in range(a + 2, a + 6):
        for y in (3,):
            w.setze(x, y, -1, w.b("spruce_fence", north=False, south=False, east=True, west=True, waterlogged=False))
        if x % 2:
            w.setze(x, 2, -1, w.b("cod" if False else "salmon_bucket" if False else "orange_terracotta"))
    for y in (1, 2):
        w.setze(a + 6, y, -1, _zaun(w))
        w.setze(a + 1, y, -1, _zaun(w))
    w.setze(-a - 2, 1, 0, w.b("smoker", facing="west", lit=True))
    w.setze(-a - 2, 2, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


def totbaumsumpf(seed, g=2):
    """Totbaumsumpf: graues Wasser, aus dem kahle, abgestorbene Bäume ragen, Nebel aus Spinnweben, bemooste
    Baumstümpfe und ein paar Irrlichter."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    karte = sumpfgrund(w, R, wasser=0.55)
    bewachsen(w, karte, 0.3)
    rng = w.rng
    for i in range(int(5 + 6 * u)):
        a = i * 2.39996
        d = R * 0.85 * math.sqrt((i + 0.5) / (5 + 6 * u))
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        totbaum(w, x, z, _r((6 + rng.random() * 6) * u + 2), y0=0, holz=["dark_oak", "spruce", "oak"][i % 3])
    for k in range(int(10 * u)):
        x, z = int(rng.integers(-R, R)), int(rng.integers(-R, R))
        if karte.get((x, z)) and w.frei(x, 2, z):
            w.setze(x, 2 + int(rng.integers(0, 3)), z, w.b("cobweb"))
    for k in range(int(3 * u)):
        x, z = int(rng.integers(-R // 2, R // 2)), int(rng.integers(-R // 2, R // 2))
        irrlicht(w, x, 3 + int(rng.integers(0, 3)), z)
    return w


def sumpfzypressen(seed, g=2):
    """Zypressensumpf: mächtige Sumpfzypressen mit Kniewurzeln stehen im schwarzen Wasser, von ihren
    Schirmkronen hängen lange Bartflechten; Seerosen und Rohrkolben."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    karte = sumpfgrund(w, R, wasser=0.6)
    bewachsen(w, karte, 0.4)
    n = int(2 + 3 * u)
    for i in range(n):
        a = i * 2.39996
        d = R * 0.7 * math.sqrt((i + 0.5) / n)
        zypresse(w, round(math.cos(a) * d), round(math.sin(a) * d), _r((10 + 6 * w.rng.random()) * u + 3), y0=1)
    return w


def torfstich(seed, g=1):
    """Torfstich: stufenweise abgestochene Torfwände, aufgeschichtete Torfsoden zum Trocknen, Spaten, Schubkarre
    und ein mit Wasser vollgelaufener alter Stich."""
    w = _neu(seed)
    u = U[g]
    L, B = _r(16 * u + 6), _r(11 * u + 5)
    for x in range(-L, L + 1):
        for z in range(-B, B + 1):
            tief = 0
            if -L * 0.6 < x < L * 0.2 and abs(z) < B * 0.5:
                tief = 1 + int((x + L * 0.6) / (L * 0.8) * 2)
            for y in range(-3, 1 - tief):
                w.setze(x, y, z, w.b("mud") if y < -2 else w.b("packed_mud") if y < 0 else
                        w.b(["moss_block", "grass_block", "podzol"][(x + z) % 3],
                            **({"snowy": False} if (x + z) % 3 else {})))
            if x < -L * 0.4 and tief:
                for y in range(1 - tief, 0):
                    w.setze(x, y, z, w.b("water", level=0))
    rng = w.rng
    for k in range(int(4 + 3 * u)):
        x0 = round(L * 0.35 + (k % 3) * 3)
        z0 = round(-B * 0.7 + (k // 3) * 4)
        for dx in (0, 1):
            for dz in (0, 1):
                for y in range(1, 4):
                    if not (y == 3 and (dx + dz) % 2):
                        w.setze(x0 + dx, y, z0 + dz, w.b("mud_bricks" if (x0 + y) % 2 else "packed_mud"))
    st = P.Stil(w, wand=["spruce_planks", "dark_oak_planks", "stripped_spruce_log"], sockel="graustein",
                gesims="stone_brick", dach="mcw_stroh", holz="spruce", laeden=True, blumen=0)
    P.gebaeude(w, st, round(L * 0.45), round(B * 0.3), round(L * 0.45) + 4, round(B * 0.3) + 3, y0=1, etagen=1,
               eh=3, dach="sattel", tuer="north", gauben=False, kamine=0)
    w.setze(0, 1, B - 1, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(0, 2, B - 1, w.b("iron_trapdoor", facing="north", half="top", open=True, powered=False,
                             waterlogged=False))
    w.setze(2, 1, B - 1, w.b("composter", level=6))
    return w


def knueppeldamm(seed, g=1):
    """Knüppeldamm: ein Weg aus quer gelegten Rundhölzern führt schnurgerade durchs Moor, mit Pfählen,
    Wegmarken aus Steinen und einem Rastplatz in der Mitte."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    karte = sumpfgrund(w, R, wasser=0.5, moor=True)
    bewachsen(w, karte, 0.4, moor=True)
    for x in range(-R - 1, R + 2):
        for z in (-1, 0, 1):
            w.setze(x, 1 if karte.get((x, z)) == "l" else 0, z, w.b("spruce_log", axis="z") if (x % 3) else
                    w.b("dark_oak_log", axis="z"))
            if karte.get((x, z)) != "l":
                w.bloecke.pop((x, 1, z), None)
                w.setze(x, 0, z, w.b("spruce_log", axis="z"))
        if x % 5 == 0:
            for sz in (-2, 2):
                w.setze(x, 0, sz, w.b("spruce_log", axis="y"))
                w.setze(x, 1, sz, w.b("spruce_log", axis="y"))
                w.setze(x, 2, sz, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                      waterlogged=False))
    for x in range(-2, 3):
        for z in range(2, 6):
            w.setze(x, 1, z, w.b("spruce_planks"))
    w.setze(0, 2, 4, w.b("campfire", lit=False, signal_fire=False, facing="north", waterlogged=False))
    for x in (-2, 2):
        w.setze(x, 2, 4, w.b("spruce_stairs", facing="east" if x < 0 else "west", half="bottom", shape="straight",
                             waterlogged=False))
    return w


def irrlichter(seed, g=1):
    """Irrlichterfeld: über einem nebligen Moor schweben grünlich und blau glimmende Lichter, ein verrotteter
    Wegweiser zeigt in alle Richtungen."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    karte = sumpfgrund(w, R, wasser=0.5, moor=True)
    bewachsen(w, karte, 0.3, moor=True)
    rng = w.rng
    for k in range(int(10 * u + 4)):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.85
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = 4 + int(rng.integers(0, 5))
        kern = w.b(["verdant_froglight", "pearlescent_froglight", "sea_lantern"][k % 3], axis="y") \
            if k % 3 != 2 else w.b("sea_lantern")
        w.setze(x, y, z, kern)
        glas = w.b(["lime_stained_glass", "light_blue_stained_glass", "cyan_stained_glass"][k % 3])
        ro = 1 + 0.6 * u
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                for dz in range(-2, 3):
                    dd = dx * dx + dy * dy + dz * dz
                    if 0 < dd <= ro * ro:
                        w.setze(x + dx, y + dy, z + dz, kern if dd <= 1 and u > 1.2 else glas, False)
        for dy in range(1, y):
            if rng.random() < 0.3:
                w.setze(x, dy, z, w.b("cobweb"), False)
    for k in range(7):
        a = k / 7 * 6.28
        x, z = round(math.cos(a) * 5 * u), round(math.sin(a) * 5 * u)
        for y in range(0, 3 + k % 2):
            w.setze(x, y, z, w.b("mossy_cobblestone" if y < 2 else "mossy_stone_bricks"))
    for y in range(1, 5):
        w.setze(0, y, 0, w.b("dark_oak_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    for f, (dx, dz) in (("east", (1, 0)), ("west", (-1, 0)), ("south", (0, 1))):
        w.setze(dx, 4 - (dz != 0), dz, w.b("dark_oak_wall_sign", facing=f, waterlogged=False))
    return w


def versunkener_turm(seed, g=2):
    """Versunkener Turm: ein schiefer, halb im Moor versunkener Magierturm mit eingesunkener Tür, zerbrochener
    Spitze, Ranken und einem Steg zum Fenster."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 6)
    karte = sumpfgrund(w, R, wasser=0.6)
    bewachsen(w, karte, 0.4)
    H = _r(20 * u + 6)
    Rt = 3 * u + 2
    M = P.Mat(w, ["mossy_stone_bricks", "cracked_stone_bricks", "stone_bricks", "mossy_cobblestone", "andesite"])
    neig = 0.18
    for y in range(-3, H):
        ox = round(y * neig)
        for k in range(int(Rt * 8)):
            a = k / (Rt * 8) * 6.28
            x, z = ox + round(math.cos(a) * Rt), round(math.sin(a) * Rt)
            if y > H * 0.75 and math.sin(a * 3 + y) > 0.3:
                continue
            fenster = y % 6 == 3 and k % int(Rt * 2) == 0
            w.setze(x, y, z, w.b("glass_pane", north=True, south=True, east=False, west=False, waterlogged=False)
                    if fenster else M(x, y, z, y / H))
        if y % 7 == 0:
            for x in range(-int(Rt), int(Rt) + 1):
                for z in range(-int(Rt), int(Rt) + 1):
                    if x * x + z * z < Rt * Rt:
                        w.setze(ox + x, y, z, w.b("spruce_planks"), False)
    from veredeln import bewuchs
    bewuchs(w, moos=0.05, ranken=0.08)
    steg(w, [(R - 1, 0), (round(Rt) + 2, 0)], y=2)
    return w


def sumpftempel(seed, g=2):
    """Sumpftempel: eine halb versunkene Stufenpyramide aus grünem Stein, überwuchert von Wurzeln und Lianen,
    Schlangenstatuen am Eingang und ein schwarzer Tümpel davor."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    karte = sumpfgrund(w, R, wasser=0.5)
    bewachsen(w, karte, 0.4)
    M = P.Mat(w, ["mossy_stone_bricks", "mossy_cobblestone", "green_terracotta", "cracked_stone_bricks",
                  "moss_block"])
    S = _r(9 * u + 4)
    for k in range(_r(5 * u + 2)):
        r = S - k * 1.6
        if r < 2:
            break
        for x in range(-int(r), int(r) + 1):
            for z in range(-int(r), int(r) + 1):
                for y in range(k * 2 - 1, k * 2 + 1):
                    w.setze(x, y, z, M(x, y, z, k / 5))
    top = 2 * _r(5 * u + 2)
    for x in range(-1, 2):
        for y in range(1, 4):
            w.bloecke.pop((x, y, S), None)
    for k in range(S):
        for x in range(-1, 2):
            w.bloecke.pop((x, k, S + 1 - k + S), None)
    for sx in (-3, 3):
        for y in range(1, 4):
            w.setze(sx, y, S + 2, w.b("mossy_stone_bricks") if y < 3 else w.b("green_terracotta"))
        w.setze(sx, 4, S + 2, w.b("green_concrete"))
        w.setze(sx, 4, S + 3, w.b("lime_concrete"))
    rng = w.rng
    for k in range(int(10 * u)):
        a = rng.random() * 6.28
        y = int(rng.random() * top)
        r = S - y * 0.8 + 0.5
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        for d in range(int(3 + rng.integers(3))):
            w.setze(x, y - d, z, w.b("vine", north=True, south=False, east=False, west=False, up=False), False)
    return w


def schilfguertel(seed, g=1):
    """Schilfgürtel: ein offener Weiher, umgeben von einem dichten Gürtel aus Schilf und Rohrkolben, mit einem
    Entenhäuschen auf einem Pfahl und einem Bootssteg."""
    w = _neu(seed)
    u = U[g]
    R = _r(13 * u + 6)
    rng = w.rng
    for x in range(-R - 1, R + 2):
        for z in range(-R - 1, R + 2):
            d = math.hypot(x, z) / R
            if d > 1.05:
                continue
            if d < 0.55:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
            elif d < 0.85:
                w.setze(x, 0, z, w.b("water", level=0) if (x + z) % 3 else w.b("mud"))
                w.setze(x, -1, z, w.b("mud"))
                if rng.random() < 0.7:
                    h = 2 + int(rng.integers(0, 3))
                    for y in range(1, h + 1):
                        w.setze(x, y, z, w.b("sugar_cane", age=0) if y < h or rng.random() < 0.6 else
                                w.b("brown_terracotta"))
            else:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
                if rng.random() < 0.4:
                    w.setze(x, 1, z, w.b("grass"))
    for y in range(0, 4):
        w.setze(0, y, 0, w.b("spruce_log", axis="y"))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(dx, 4, dz, w.b("spruce_planks"))
            if abs(dx) + abs(dz) == 2:
                w.setze(dx, 5, dz, w.b("spruce_planks"))
    w.bloecke.pop((0, 5, 1), None)
    for dx in (-1, 0, 1):
        w.setze(dx, 6, 0, w.b("spruce_slab", type="bottom", waterlogged=False))
        for dz in (-1, 1):
            w.setze(dx, 6, dz, w.b("spruce_stairs", facing="south" if dz < 0 else "north", half="bottom",
                                   shape="straight", waterlogged=False))
    steg(w, [(R, 2), (round(R * 0.4), 2)], y=1)
    return w


def froschteich(seed, g=1):
    """Froschteich: ein flacher Tümpel mit Froschlaich, Seerosen, Tropfblättern und großen bemoosten Steinen zum
    Sonnen, umrahmt von Sumpfdotterblumen."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    karte = sumpfgrund(w, R, wasser=0.6, zelle=6)
    rng = w.rng
    for (x, z), t in karte.items():
        if t == "w":
            r = rng.random()
            if r < 0.08:
                w.setze(x, 1, z, w.b("frogspawn"))
            elif r < 0.2:
                w.setze(x, 1, z, w.b("lily_pad"))
        elif t == "l" and rng.random() < 0.2:
            w.setze(x, 1, z, w.b(["dandelion", "big_dripleaf", "fern"][int(rng.integers(3))],
                                 **({"facing": "north", "tilt": "none", "waterlogged": False}
                                    if rng.random() < 0 else {})) if rng.random() < 0.6 else w.b("dandelion"))
    for k in range(int(3 + 2 * u)):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.6
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        r = 1.8 + rng.random() * 2 * u
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for z in range(int(cz - r) - 1, int(cz + r) + 2):
                for y in range(0, int(r) + 1):
                    if (x - cx) ** 2 + (z - cz) ** 2 + (y * 1.6) ** 2 <= r * r:
                        w.setze(x, y, z, w.b("mossy_cobblestone" if (x + y) % 2 else "moss_block"))
    return w


def sumpfkrokodil(seed, g=2):
    """Sumpfkrokodil: ein riesiges, steinernes Krokodil liegt halb untergetaucht im Morast, nur Rücken mit
    Panzerhöckern, Augen und das offene Maul ragen heraus."""
    from skulptur import Skulptur, ell, kap
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    karte = sumpfgrund(w, R, wasser=0.65)
    bewachsen(w, karte, 0.3)
    S = Skulptur(w, u)
    from lib import Verlauf
    S.mat("h", Verlauf(w, "Kroko", ["green_terracotta", "mossy_cobblestone", "moss_block", "lime_terracotta"]),
          basis=0.5, steigung=0.2, rausch=1.4)
    S.mat("z", w.b("bone_block", axis="y"))
    S.mat("e", w.b("yellow_concrete"))
    S.mat("r", w.b("red_terracotta"))
    S.plus(ell(0, -1, 0, 3.4, 2.4, 9), "h")
    for k in range(12):
        S.plus(ell((k % 2 * 2 - 1) * 1.4, 1.0, -7 + k * 1.2, 0.5, 0.6, 0.5), "h")
    S.plus(kap((0, -0.5, 8), (0, -0.2, 14), 2.0, 1.4), "h")
    S.plus(kap((0, 1.2, 9), (0, 2.6, 14), 1.8, 1.1), "h")
    S.plus(kap((0, -0.3, 9), (0, -0.3, 14), 1.0, 0.7), "r")
    for sx in (-1, 1):
        S.plus(ell(sx * 1.2, 2.2, 8.6, 0.6, 0.6, 0.6), "e")
        for k in range(5):
            S.plus(kap((sx * 1.3, 0.5, 10 + k), (sx * 1.4, -0.3, 10 + k), 0.25, 0.1), "z")
    S.plus(kap((0, -0.6, -9), (2, -0.3, -18), 1.8, 0.4), "h")
    S.rendern((-6, -4, -20), (6, 6, 16), versatz=(0.5, 1.2 * u, 0.5))
    return w


def sumpfdorf(seed, g=2):
    """Sumpfdorf: Pfahlhütten mit Stroh- und Holzdächern, verbunden durch Bohlenstege, ein Versammlungshaus,
    Fischreusen, Kähne und Laternen an Pfählen."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    karte = sumpfgrund(w, R, wasser=0.7, zelle=8)
    bewachsen(w, karte, 0.3)
    n = 3 + 2 * g
    pos = [(0, 0)]
    pfahlhaus(w, 0, 0, _r(3 * u + 1, 3), _r(2 * u + 1, 2), 3, _stil(seed), etagen=1, dach="mcw_holz")
    for i in range(n):
        a = i / n * 6.28 + 0.4
        d = R * 0.6
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        pfahlhaus(w, cx, cz, 2, 2, 3, (_stil(seed) + i) % 2, dach=["mcw_stroh", "mcw_holz", "mcw_braun"][i % 3],
                  tuer="north" if cz > 0 else "south")
        pos.append((cx, cz))
    for (cx, cz) in pos[1:]:
        steg(w, [(0, 0), (cx, cz)], y=2)
    for (cx, cz) in pos[1:]:
        w.setze(cx + 4, 2, cz, _zaun(w))
        w.setze(cx + 4, 3, cz, _zaun(w))
        w.setze(cx + 4, 4, cz, w.b("lantern", hanging=False, waterlogged=False))
    return w


def moorkate(seed, g=1):
    """Moorkate: eine geduckte Kate mit Grassodendach auf einer Torfinsel, Kräuterbeete in Holzrahmen, ein
    Kessel über dem Feuer und getrocknete Kräuterbüschel am Vordach."""
    w = _neu(seed)
    u = U[g]
    R = _r(11 * u + 5)
    karte = sumpfgrund(w, R, wasser=0.45, moor=True)
    for x in range(-R // 2, R // 2 + 1):
        for z in range(-R // 2, R // 2 + 1):
            if x * x + z * z < (R / 2) ** 2:
                w.setze(x, 0, z, w.b("podzol", snowy=False) if (x + z) % 3 else w.b("rooted_dirt"))
                karte[(x, z)] = "l"
    bewachsen(w, {k: v for k, v in karte.items() if math.hypot(*k) > R / 2}, 0.4, moor=True)
    a, b = _r(2.5 * u + 1, 2), _r(2 * u + 1, 2)
    st = P.Stil(w, wand=["mud_bricks", "packed_mud", "spruce_planks", "mud_bricks"], sockel="graustein",
                gesims="stone_brick", dach="mcw_gruen", holz="spruce", laeden=True, blumen=0.5)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=3, dach="sattel", tuer="south", gauben=False, kamine=1,
               steil=False)
    for k in range(3):
        x0 = -a + k * 3
        z0 = b + 3
        for dx in range(2):
            for dz in range(2):
                w.setze(x0 + dx, 1, z0 + dz, w.b("farmland", moisture=7))
                w.setze(x0 + dx, 2, z0 + dz, w.b(["beetroots", "carrots", "potatoes"][k], age=3 if k == 0 else 7))
    w.setze(a + 3, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    w.setze(a + 3, 2, 0, w.b("cauldron"))
    return w


def haengebruecke(seed, g=2):
    """Moorbrücke: eine durchhängende Seilbrücke spannt sich über einen tiefen, schwarzen Moorkanal zwischen zwei
    knorrigen Weiden."""
    w = _neu(seed)
    u = U[g]
    L = _r(12 * u + 5)
    R = L + 6
    karte = sumpfgrund(w, R, wasser=0.4)
    for x in range(-L + 2, L - 1):
        for z in range(-R, R + 1):
            if (x, z) in karte:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
    for sx in (-1, 1):
        einfuegen(w, wald2.weide(int(w.rng.integers(1, 10 ** 6)), H=_r(9 * u + 3)), sx * (L + 1), 0, -4)
        for z in (-1, 1):
            for y in range(1, 5):
                w.setze(sx * L, y, z, w.b("spruce_log", axis="y"))
    for x in range(-L, L + 1):
        t = (x + L) / (2 * L)
        y = round(3 - math.sin(t * math.pi) * 2 * u)
        w.setze(x, y, 0, w.b("spruce_slab", type="bottom", waterlogged=False))
        for z in (-1, 1):
            w.setze(x, y + 1, z, w.b("spruce_fence", north=False, south=False, east=True, west=True,
                                     waterlogged=False))
    bewachsen(w, karte, 0.4)
    return w


def moorquelle(seed, g=1):
    """Moorquelle: ein dampfender Tümpel mit aufsteigenden Blasen und rostrotem Rand aus Eisenocker, umgeben von
    Torfmoos und uralten Steinen mit Runen."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    karte = sumpfgrund(w, R, wasser=0.35, moor=True)
    bewachsen(w, karte, 0.3, moor=True)
    r = 3 * u + 1.5
    for x in range(-int(r) - 2, int(r) + 3):
        for z in range(-int(r) - 2, int(r) + 3):
            d = math.hypot(x, z)
            if d < r:
                for y in range(-3, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -4, z, w.b("magma_block") if (x + z) % 3 == 0 else w.b("mud"))
                w.bloecke.pop((x, 1, z), None)
            elif d < r + 1.5:
                w.setze(x, 0, z, w.b(["orange_terracotta", "red_terracotta", "brown_terracotta"][(x + z) % 3]))
    for k in range(7):
        a = k / 7 * 6.28
        x, z = round(math.cos(a) * (r + 3)), round(math.sin(a) * (r + 3))
        for y in range(1, _r(3 * u) + 2 + k % 2):
            for dx in range(2):
                w.setze(x + dx, y, z, w.b("mossy_cobblestone" if y % 3 else "chiseled_stone_bricks"))
    for k in range(int(12 * u)):
        a = w.rng.random() * 6.28
        d = w.rng.random() * r * 0.8
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        for y in range(1, 2 + int(w.rng.integers(1, 4))):
            w.setze(x, y, z, w.b("white_stained_glass"), False)
    return w


def wurzelhoehle(seed, g=2):
    """Wurzelhöhle: ein umgestürzter Riesenbaum hat seinen Wurzelteller aufgestellt, darunter eine Höhle im
    Moor mit Wasserloch, Pilzen und Leuchtflechten."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    karte = sumpfgrund(w, R, wasser=0.4)
    bewachsen(w, karte, 0.4)
    Rw = 5 * u + 2
    for y in range(0, int(Rw * 2) + 1):
        for z in range(-int(Rw), int(Rw) + 1):
            d = math.hypot(y - Rw, z)
            if d <= Rw and w.rng.random() < 0.85:
                w.setze(0, y, z, w.b("rooted_dirt") if d < Rw - 1.5 else w.b("mangrove_roots", waterlogged=False))
                if d < Rw - 1:
                    w.setze(1, y, z, w.b("dirt") if (y + z) % 3 else w.b("mud"))
    for k in range(int(10 * u)):
        a = w.rng.random() * 6.28
        linie(w, (0, Rw, 0), (-2, Rw + math.sin(a) * Rw * 1.4, math.cos(a) * Rw * 1.4),
              w.b("mangrove_roots", waterlogged=False))
    L = _r(14 * u + 4)
    for x in range(2, L):
        for y in range(int(Rw) - 2, int(Rw) + 2):
            for z in range(-2, 3):
                if (y - Rw) ** 2 + z * z <= 4.5:
                    w.setze(x, y - int(x * 0.15), z, w.b("spruce_log", axis="x"))
    for z in range(-int(Rw) + 1, int(Rw)):
        for x in range(-4, 0):
            w.setze(x, 0, z, w.b("water", level=0) if abs(z) < 2 else w.b("mud"))
    for k in range(6):
        w.setze(-1 - k % 3, 1, -3 + k, w.b(["brown_mushroom", "red_mushroom", "glow_lichen"][k % 3],
                                           **({"down": True, "up": False, "north": False, "south": False,
                                               "east": False, "west": False, "waterlogged": False}
                                              if k % 3 == 2 else {})), False)
    return w


def sumpfwachturm(seed, g=1):
    """Sumpfwachturm: ein hoher Holzturm auf Pfählen mit überdachter Plattform, Leiter, Signalhorn und Laternen,
    ein Steg führt hinaus zum Wasser."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    karte = sumpfgrund(w, R, wasser=0.55)
    bewachsen(w, karte, 0.4)
    H = _r(14 * u + 5)
    for sx in (-2, 2):
        for sz in (-2, 2):
            for y in range(-1, H):
                w.setze(sx, y, sz, w.b("spruce_log", axis="y"))
    for y in range(3, H, 4):
        for k in range(-2, 3):
            for sx, sz in ((k, -2), (k, 2), (-2, k), (2, k)):
                w.setze(sx, y, sz, w.b("spruce_fence", north=False, south=False, east=True, west=True,
                                       waterlogged=False), False)
    for x in range(-3, 4):
        for z in range(-3, 4):
            w.setze(x, H, z, w.b("spruce_planks"))
            if abs(x) == 3 or abs(z) == 3:
                w.setze(x, H + 1, z, _zaun(w))
            w.setze(x, H + 4, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    for sx in (-3, 3):
        for sz in (-3, 3):
            for y in range(H + 1, H + 4):
                w.setze(sx, y, sz, _zaun(w))
    w.setze(0, H + 5, 0, w.b("spruce_slab", type="bottom", waterlogged=False))
    for y in range(0, H):
        w.setze(0, y, -3, w.b("ladder", facing="north", waterlogged=False))
    w.setze(1, H + 1, 1, w.b("bell", attachment="floor", facing="north", powered=False))
    for sx in (-3, 3):
        w.setze(sx, H + 3, 0, w.b("lantern", hanging=True, waterlogged=False))
    steg(w, [(0, 3), (0, R)], y=1)
    return w


def versunkenes_boot(seed, g=1):
    """Versunkenes Boot: ein alter Kahn steckt schräg im Schlamm, voll Wasser und Entengrütze, daneben ein
    abgebrochenes Ruder, Reusen und eine Laterne auf einem Pfahl."""
    w = _neu(seed)
    u = U[g]
    R = _r(9 * u + 5)
    karte = sumpfgrund(w, R, wasser=0.55)
    bewachsen(w, karte, 0.4)
    from boote import ruderboot
    from piraten import einfuegen_gedreht
    from skulptur import dreh_x, dreh_y
    b = ruderboot(seed, min(3, g + 2))
    einfuegen_gedreht(w, b, dreh_y(0.6) @ dreh_x(0.25), (0, 0.6, 0))
    for (x, y, z), blk in list(w.bloecke.items()):
        if y == 0 and w.P.name(blk).endswith("planks") and w.rng.random() < 0.3:
            w.setze(x, 1, z, w.b("moss_carpet"), False)
    for y in range(0, 4):
        w.setze(R // 2, y, -R // 3, w.b("spruce_log", axis="y"))
    w.setze(R // 2, 4, -R // 3, w.b("lantern", hanging=False, waterlogged=False))
    linie(w, (-R // 2, 0, R // 3), (-R // 2 + 4, 1, R // 3 + 1), _zaun(w))
    return w


def laternenweg(seed, g=1):
    """Laternenweg: ein Bohlenpfad schlängelt sich durch nächtliches Moor, alle paar Schritte eine
    Seelenlaterne an krummem Pfahl, damit niemand den Irrlichtern folgt."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    karte = sumpfgrund(w, R, wasser=0.5, moor=True)
    bewachsen(w, karte, 0.4, moor=True)
    pts = []
    for k in range(9):
        t = k / 8
        pts.append((round(-R + 2 * R * t), round(math.sin(t * 5) * R * 0.35)))
    steg(w, pts, y=1, breite=2)
    for i, (x, z) in enumerate(pts[1:-1]):
        zz = z + 2
        for y in range(0, 4):
            w.setze(x + (y == 3), y, zz, w.b("dark_oak_fence", north=False, south=False, east=y == 3, west=False,
                                             waterlogged=False))
        w.setze(x + 1, 2, zz, w.b("soul_lantern", hanging=True, waterlogged=False))
    return w


def biberdamm(seed, g=2):
    """Biberdamm: ein Bachlauf wird von einem gewaltigen Damm aus Ästen und Schlamm gestaut, dahinter ein
    Teich mit der kuppelförmigen Biberburg, angenagte Baumstümpfe am Ufer."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    rng = w.rng
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z) / R
            if d > 1:
                continue
            w.setze(x, -1, z, w.b("dirt"))
            if z < 0 and abs(x) < R * 0.75 * math.sqrt(max(0, 1 - (z / R) ** 2)):
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
            elif z > 2 and abs(x - math.sin(z * 0.3) * 2) < 1.8:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel"))
            else:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
    holz = ["spruce_log", "oak_log", "dark_oak_log", "stripped_oak_log", "mud", "packed_mud"]
    for x in range(-round(R * 0.8), round(R * 0.8) + 1):
        for y in range(0, 3 - round(abs(x) / R * 2)):
            for z in (0, 1, 2):
                n = holz[(x * 7 + y * 3 + z) % 6]
                w.setze(x, y, z, w.b(n, axis="x") if "log" in n else w.b(n))
        if rng.random() < 0.4:
            linie(w, (x, 2, 0), (x + rng.integers(-2, 3), 3, -1), w.b("spruce_fence", north=False, south=False,
                                                                       east=False, west=False, waterlogged=False))
    cx, cz = 0, -round(R * 0.45)
    rb = 3 * u + 1.5
    for x in range(-int(rb) - 1, int(rb) + 2):
        for z in range(-int(rb) - 1, int(rb) + 2):
            for y in range(0, int(rb) + 1):
                if x * x + z * z + (y * 1.3) ** 2 <= rb * rb:
                    n = holz[(x * 5 + y * 11 + z * 3) % 6]
                    w.setze(cx + x, y, cz + z, w.b(n, axis="y") if "log" in n else w.b(n))
    for k in range(5):
        a = rng.random() * 6.28
        x, z = round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8)
        if w.P.name(w.bloecke.get((x, 0, z), 0)) == "minecraft:grass_block":
            w.setze(x, 1, z, w.b("stripped_birch_log", axis="y"))
            w.setze(x, 2, z, w.b("birch_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    return w


def reiherkolonie(seed, g=2):
    """Reiherkolonie: auf abgestorbenen Bäumen im Sumpf sitzen große Reisignester mit Eiern, darunter weißer
    Vogelkot auf den Ästen und flaches Wasser mit Fischen."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    karte = sumpfgrund(w, R, wasser=0.6)
    bewachsen(w, karte, 0.3)
    rng = w.rng
    n = int(3 + 2 * u)
    for i in range(n):
        a = i * 2.39996
        d = R * 0.7 * math.sqrt((i + 0.5) / n)
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        H = _r((8 + rng.random() * 5) * u + 2)
        totbaum(w, x0, z0, H, y0=0, holz="spruce")
        for k in range(2):
            nx, nz = x0 + (k * 2 - 1) * 2, z0
            ny = H - 2 - k * 3
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    w.setze(nx + dx, ny, nz + dz, w.b("spruce_fence", north=dz < 0, south=dz > 0, east=dx > 0,
                                                      west=dx < 0, waterlogged=False) if abs(dx) + abs(dz) else
                            w.b("hay_block", axis="y"))
            w.setze(nx, ny + 1, nz, w.b("turtle_egg", eggs=2, hatch=0) if False else w.b("white_carpet"))
            w.setze(nx, ny - 2, nz, w.b("white_concrete_powder"), False)
    return w


# ============================================================================ Kombinierbare Stücke

def sumpfstueck(seed, g=1):
    """Sumpfstück: verzweigte Wasserläufe zwischen Schlamm- und Mooshügeln, Zypressen, Weiden, Totbäume und
    Schilf – nahtlos aneinandersetzbar."""
    st = Stueck(seed, g)
    w = st.w
    karte = sumpfgrund(w, st.R * 1.1, wasser=0.5, rand=False)
    for (x, z) in list(karte):
        if st.rand(x, z) > 1.0:
            for y in (-1, 0):
                w.bloecke.pop((x, y, z), None)
            del karte[(x, z)]
    rng = st.rng
    n = int(3 + 3 * (g + 1))
    for i in range(n):
        x = int(rng.integers(-st.R, st.R))
        z = int(rng.integers(-st.R, st.R))
        if st.rand(x, z) > 0.85:
            continue
        r = rng.random()
        if r < 0.45:
            zypresse(w, x, z, _r((8 + rng.random() * 5) * (0.7 + 0.25 * g)), y0=1)
        elif r < 0.7:
            totbaum(w, x, z, _r((5 + rng.random() * 4) * (0.7 + 0.25 * g)), y0=0)
        else:
            einfuegen(w, wald2.weide(int(rng.integers(1, 10 ** 6)), H=_r(7 + 2 * g)), x, 0, z)
    bewachsen(w, karte, 0.5)
    for p in w.bloecke:
        w.folgen.setdefault(p, -1)
    return st


def moorwiese(seed, g=1):
    """Moorwiese: offenes Hochmoor mit Torfmoospolstern, Wollgras, Heidekraut, Moosbeeren, einzelnen
    Krüppelkiefern und kleinen Moorlöchern – kombinierbar."""
    st = Stueck(seed, g)
    w = st.w
    karte = sumpfgrund(w, st.R * 1.1, wasser=0.25, rand=False, moor=True)
    for (x, z) in list(karte):
        if st.rand(x, z) > 1.0:
            for y in (-1, 0):
                w.bloecke.pop((x, y, z), None)
            del karte[(x, z)]
    bewachsen(w, karte, 0.65, moor=True)
    st.verteile(7, int(20 * (g + 1) ** 2), lambda x, z, rd, a: (
        wald2.jungbaum(int(st.rng.integers(1, 10 ** 6)), "spruce", H=int(3 + st.rng.integers(3))), 3)
        if karte.get((x, z)) == "l" else None)
    for p in w.bloecke:
        w.folgen.setdefault(p, -1)
    return st


def sumpfpfad(seed, g=1):
    """Sumpfpfad: ein Bohlensteg mit Geländerpfosten zieht sich quer durch ein Sumpfstück mit Zypressen und
    Schilf – passt an andere Sumpfstücke an."""
    st = sumpfstueck(seed, g)
    w = st.w
    pts = wald2.wegpunkte(st, "kurve", 2.0)
    for (x, z) in pts:
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for y in range(1, 4):
                    p = (x + dx, y, z + dz)
                    if p in w.bloecke and not w.P.name(w.bloecke[p]).endswith(("_log", "_wood")):
                        del w.bloecke[p]
    steg(w, pts, y=1, breite=2)
    for p in w.bloecke:
        w.folgen.setdefault(p, -1)
    return st


# ============================================================================ Tabelle

def _wrap(f):
    def g(seed, groesse=1):
        r = f(seed, groesse)
        if isinstance(r, Stueck):
            return _fertig(r.w)
        if hasattr(r, "folgen") and not hasattr(r, "folge_anker"):
            del r.folgen
        return r
    g.__doc__ = f.__doc__
    return g


SUMPF = {k: (n, _wrap(f)) for k, (n, f) in {
    "moorsee": ("Moorsee", moorsee),
    "sumpfhuette": ("Sumpfhütte auf Pfählen", sumpfhuette),
    "schilfkate": ("Fischerkate im Schilf", schilfkate),
    "totbaumsumpf": ("Totbaumsumpf", totbaumsumpf),
    "sumpfzypressen": ("Zypressensumpf", sumpfzypressen),
    "torfstich": ("Torfstich", torfstich),
    "knueppeldamm": ("Knüppeldamm", knueppeldamm),
    "irrlichter": ("Irrlichterfeld", irrlichter),
    "versunkener_turm": ("Versunkener Turm", versunkener_turm),
    "sumpftempel": ("Sumpftempel", sumpftempel),
    "schilfguertel": ("Schilfgürtel", schilfguertel),
    "froschteich": ("Froschteich", froschteich),
    "sumpfkrokodil": ("Sumpfkrokodil", sumpfkrokodil),
    "sumpfdorf": ("Sumpfdorf", sumpfdorf),
    "moorkate": ("Moorkate", moorkate),
    "haengebruecke": ("Moorbrücke", haengebruecke),
    "moorquelle": ("Moorquelle", moorquelle),
    "wurzelhoehle": ("Wurzelhöhle", wurzelhoehle),
    "sumpfwachturm": ("Sumpfwachturm", sumpfwachturm),
    "versunkenes_boot": ("Versunkenes Boot", versunkenes_boot),
    "laternenweg": ("Laternenweg", laternenweg),
    "biberdamm": ("Biberdamm", biberdamm),
    "reiherkolonie": ("Reiherkolonie", reiherkolonie),
    "sumpfstueck": ("Sumpfstück", sumpfstueck),
    "moorwiese": ("Moorwiese", moorwiese),
    "sumpfpfad": ("Sumpfpfad", sumpfpfad),
}.items()}

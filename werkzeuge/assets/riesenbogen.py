"""Riesenbogen: ein gewaltiger, leicht verdrehter Felsbogen mit terrassierten Füßen, Tropfsteinen,
Fantasiehäusern obendrauf und Hängehäusern an Ketten.

Eigene Umsetzung im Stil bekannter „Giant Archway“-Bauten – kein Nachbau.
Varianten: "pur" (nur der Bogen) und "dorf" (mit allen Häusern). Dazu Einzelvorlagen der Häuser.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.ndimage import binary_erosion, gaussian_filter, map_coordinates
from scipy.spatial import cKDTree

from lib import Verlauf, Welt, ist_massiv, laub, ueberwuchern

GEGEN = {"north": "south", "south": "north", "east": "west", "west": "east"}


def _rauschfeld(rng, n=40, glatt=1.2):
    g = gaussian_filter(rng.random((n, n, n)), glatt, mode="wrap")
    g = (g - g.min()) / (g.max() - g.min())
    return g


def _abtasten(feld, X, Y, Z, sx, sy, sz):
    return map_coordinates(feld, [X / sx, Y / sy, Z / sz], order=1, mode="wrap")


# ============================================================================ Bausteine


def kette(w: Welt, x, y_oben, y_unten, z):
    for y in range(y_unten, y_oben + 1):
        w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False))


def haengelaterne(w: Welt, x, y, z, laenge=1, seele=False):
    """Laterne an einer Kette, die vom Block (x, y+1, z) herabhängt."""
    for k in range(laenge):
        w.setze(x, y - k, z, w.b("chain", axis="y", waterlogged=False))
    w.setze(x, y - laenge, z, w.b("soul_lantern" if seele else "lantern", hanging=True, waterlogged=False))


def zahnrad(w: Welt, cx, cy, cz, R, ebene="xy", material="polished_andesite", nabe="stone_bricks"):
    """Großes Steinzahnrad mit Zähnen, Speichen und Nabe."""
    m, n = w.b(material), w.b(nabe)
    for a in range(-R - 2, R + 3):
        for b in range(-R - 2, R + 3):
            d = math.hypot(a, b)
            ang = math.atan2(b, a)
            zahn = (int((ang + math.pi) / (2 * math.pi) * (R * 2)) % 2) == 0
            blk = None
            if R - 0.6 <= d <= R + 0.4:
                blk = m
            elif R + 0.4 < d <= R + 1.4 and zahn:
                blk = m
            elif d <= 1.2:
                blk = n
            elif d < R - 0.6 and (abs(a) == 0 or abs(b) == 0 or abs(a) == abs(b) and R > 4):
                blk = m
            if blk is not None:
                if ebene == "xy":
                    w.setze(cx + a, cy + b, cz, blk)
                else:
                    w.setze(cx, cy + b, cz + a, blk)


# ---------------------------------------------------------------------------- Fantasiehaus

STILE = {
    "kupfer": dict(rahmen="dark_oak", wand="stripped_dark_oak_log", fuellung="spruce_planks",
                   dach=["dark_prismarine", "waxed_oxidized_cut_copper", "prismarine_bricks",
                         "waxed_weathered_cut_copper"],
                   kante="smooth_sandstone", kante_treppe="smooth_sandstone_stairs", steil=2, rund=True, turm=True,
                   spitzen=False, sockel=["stone_bricks", "cobblestone", "mossy_cobblestone"]),
    "stein": dict(rahmen="spruce", wand="deepslate_bricks", fuellung="polished_deepslate",
                  dach=["deepslate_tiles", "cobbled_deepslate", "polished_deepslate", "deepslate_bricks"],
                  kante="stone_bricks", kante_treppe="stone_brick_stairs", steil=2, rund=False, turm=False,
                  spitzen=True, sockel=["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks"]),
    "terrakotta": dict(rahmen="spruce", wand="white_terracotta", fuellung="spruce_planks",
                       dach=["brown_terracotta", "terracotta", "granite", "polished_granite"],
                       kante="polished_granite", kante_treppe="polished_granite_stairs", steil=1, rund=True,
                       turm=False, spitzen=False, sockel=["cobblestone", "stone_bricks", "andesite"]),
    "holz": dict(rahmen="spruce", wand="spruce_planks", fuellung="stripped_spruce_log",
                 dach=["dark_oak_planks", "spruce_planks", "stripped_spruce_log", "spruce_planks"],
                 kante="dark_oak_planks", kante_treppe="dark_oak_stairs", steil=1, rund=False, turm=False,
                 spitzen=False, sockel=["spruce_planks", "spruce_planks", "stripped_spruce_log"]),
}


def fantasiehaus(w: Welt, x0, y0, z0, B=9, T=7, H=5, stil="kupfer", fundament=20, tuer="south", rad=False,
                 sockel_bloecke=None):
    """Fantasiehaus mit steilem Satteldach (First entlang x), abgesetzten Dachkanten, hochgezogenen
    Ecken, runden Fenstern, Laternen und je nach Stil Türmchen, Spitzen oder Zahnrad.
    (x0, y0, z0) = nordwestliche Bodenecke. Gibt die Firsthöhe zurück."""
    s = STILE[stil]
    rahmen = {a: w.b(f"{s['rahmen']}_log", axis=a) for a in "xyz"}
    wand = w.b(s["wand"], **({"axis": "y"} if s["wand"].endswith("_log") else {}))
    fuell = w.b(s["fuellung"], **({"axis": "x"} if s["fuellung"].endswith("_log") else {}))
    dach = Verlauf(w, "Dach", s["dach"])
    kante = w.b(s["kante"])
    sockel = [w.b(n) for n in (sockel_bloecke or s["sockel"])]
    x1, z1 = x0 + B - 1, z0 + T - 1

    # Fundament bis zum Untergrund (Pfeiler, die in den Fels greifen)
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            for y in range(y0, y0 - fundament - 1, -1):
                if y < y0 and not w.frei(x, y, z):
                    break
                rand = x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1)
                if y == y0 and not rand:
                    w.setze(x, y, z, w.b(f"{s['rahmen']}_planks"))
                else:
                    w.setze(x, y, z, sockel[int(w.rng.random() * len(sockel))])
    # Wände
    for y in range(y0 + 1, y0 + H + 1):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if not (x in (x0, x1) or z in (z0, z1)):
                    w.setze(x, y, z, 0)
                    continue
                ecke = x in (x0, x1) and z in (z0, z1)
                stuetze = (x - x0) % 4 == 0 if z in (z0, z1) else (z - z0) % 3 == 0
                if ecke or stuetze:
                    w.setze(x, y, z, rahmen["y"])
                elif y == y0 + H:
                    w.setze(x, y, z, rahmen["x" if z in (z0, z1) else "z"])
                else:
                    w.setze(x, y, z, wand if y > y0 + 1 else fuell)
    # Fenster
    yf = y0 + 2 + (H - 4) // 2
    for z, seite in ((z1, "south"), (z0, "north")):
        for xm in range(x0 + 2, x1 - 1, 4):
            xm2 = xm + 1 if xm + 1 < x1 else xm
            if seite == tuer and abs(xm2 - (x0 + B // 2)) < 2:
                continue
            if s["rund"]:
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    w.setze(xm2 + dx, yf + 1 + dy, z, w.b("glass_pane", east=True, west=True, north=False,
                                                         south=False, waterlogged=False))
            else:
                for dy in (0, 1):
                    w.setze(xm2, yf + dy, z, w.b("glass_pane", east=True, west=True, north=False, south=False,
                                                 waterlogged=False))
            dz = 1 if seite == "south" else -1
            w.setze(xm2, yf - 1, z + dz, w.b(f"{s['rahmen']}_trapdoor", facing=seite, half="top", open=False,
                                              powered=False, waterlogged=False), ueberschreiben=False)
    # Tür
    tx = x0 + B // 2
    tz = z1 if tuer == "south" else z0
    for half, dy in (("lower", 1), ("upper", 2)):
        w.setze(tx, y0 + dy, tz, w.b(f"{s['rahmen']}_door", facing=tuer, half=half, hinge="left", open=False,
                                     powered=False))
    dz = 1 if tuer == "south" else -1
    w.setze(tx + 1, y0 + 3, tz + dz, w.b("lantern", hanging=False, waterlogged=False), ueberschreiben=False)
    w.setze(tx + 1, y0 + 2, tz + dz, w.b(f"{s['rahmen']}_fence", north=False, south=False, east=False, west=False,
                                         waterlogged=False), ueberschreiben=False)

    # Steiles Satteldach mit Kanten
    yd = y0 + H + 1
    steil = s["steil"]
    k = 0
    zm = (z0 + z1) / 2
    first = yd
    while True:
        zs, zn = z0 - 1 + k, z1 + 1 - k
        if zs > zn:
            break
        for lage in range(steil):
            y = yd + k * steil + lage
            first = y
            for x in range(x0 - 2, x1 + 3):
                ende = x in (x0 - 2, x1 + 2)
                for z in ((zs, zn) if zs != zn else (zs,)):
                    if ende or k == 0:
                        blk = kante
                    else:
                        blk = dach(1.0 + 2.6 * k / max(1, (T + 2) / 2) + (w.rng.random() - 0.5) * 0.8, x, y, z)
                    w.setze(x, y, z, blk)
                if zs == zn:
                    continue
                # Giebelwand füllen
                for z in range(zs + 1, zn):
                    for xg in (x0, x1):
                        w.setze(xg, y, z, rahmen["y"] if abs(z - zm) < 0.6 else wand)
                    for xg in range(x0 + 1, x1):
                        w.setze(xg, y, z, 0)
        k += 1
    # Firstkante
    for x in range(x0 - 2, x1 + 3):
        w.setze(x, first + 1, int(round(zm)), w.b(s["kante_treppe"].replace("_stairs", "_slab")
                                                    if "stairs" in s["kante_treppe"] else s["kante"],
                                                    type="bottom", waterlogged=False))
    # hochgezogene Dachecken (geschwungen)
    for x, dx in ((x0 - 2, -1), (x1 + 2, 1)):
        for z, dzz in ((z0 - 1, -1), (z1 + 1, 1)):
            w.setze(x + dx, yd, z + dzz, kante)
            w.setze(x + dx, yd + 1, z + dzz, kante)
            w.setze(x + 2 * dx, yd + 2, z + dzz, kante)
            haengelaterne(w, x + dx, yd - 1, z + dzz, 1)
        # Giebelspitze
        w.setze(x, first + 2, int(round(zm)), kante)
        w.setze(x + dx, first + 3, int(round(zm)), kante)
    # Schornstein mit Rauch
    cx, cz = x1 - 2, z0 + 1
    for y in range(y0 + 1, first + 3):
        w.setze(cx, y, cz, w.b("cobblestone") if w.rng.random() < 0.7 else w.b("mossy_cobblestone"))
    w.setze(cx, first + 3, cz, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))

    if s["turm"]:
        # Türmchen auf dem Dach mit eigenem Spitzdach
        tx0, tz0 = x0 + 1, int(zm) - 1
        for y in range(yd + 1, first + 5):
            for x in range(tx0, tx0 + 3):
                for z in range(tz0, tz0 + 3):
                    rand = x in (tx0, tx0 + 2) or z in (tz0, tz0 + 2)
                    if not rand:
                        w.setze(x, y, z, 0)
                    elif x in (tx0, tx0 + 2) and z in (tz0, tz0 + 2):
                        w.setze(x, y, z, rahmen["y"])
                    elif y in (first + 2, first + 3) and z == tz0 + 2:
                        w.setze(x, y, z, w.b("glass_pane", east=True, west=True, north=False, south=False,
                                             waterlogged=False))
                    else:
                        w.setze(x, y, z, wand)
        yt = first + 5
        for k2, r in enumerate((2, 2, 1, 1, 0)):
            for x in range(tx0 + 1 - r, tx0 + 2 + r):
                for z in range(tz0 + 1 - r, tz0 + 2 + r):
                    rand = abs(x - tx0 - 1) == r or abs(z - tz0 - 1) == r
                    if rand or r == 0:
                        w.setze(x, yt + k2, z, kante if k2 == 0 else dach(2.5, x, yt + k2, z))
        w.setze(tx0 + 1, yt + 5, tz0 + 1, kante)
        w.setze(tx0 + 1, yt + 6, tz0 + 1, w.b("lantern", hanging=False, waterlogged=False))
    if s["spitzen"]:
        for x in (x0 - 1, x1 + 1):
            for y in range(first - 1, first + 4):
                w.setze(x, y, int(round(zm)), w.b("deepslate_brick_wall", east="none", west="none", north="none",
                                                  south="none", up=True, waterlogged=False))
            w.setze(x, first + 4, int(round(zm)), w.b("end_rod", facing="up"))
    if rad:
        zahnrad(w, x0 + B // 2, y0 + H - 1, z1 + 1, 3)
    return first


# ---------------------------------------------------------------------------- Hängehäuser


def haengehuette(w: Welt, cx, y_dach, cz, stil="holz", B=7, T=6):
    """Hütte mit Balkon, deren Dachfirst bei y_dach liegt. Gibt die Firsthöhe zurück."""
    st = STILE[stil]
    y0 = y_dach - (4 + ((T + 2) // 2) * st["steil"]) - (11 if st["turm"] else 0)
    x0, z0 = cx - B // 2, cz - T // 2
    first = fantasiehaus(w, x0, y0, z0, B=B, T=T, H=4, stil=stil, fundament=0)
    # Balkon-Plattform rundherum und Unterbau
    planke = w.b("spruce_planks")
    for x in range(x0 - 2, x0 + B + 2):
        for z in range(z0 - 2, z0 + T + 2):
            if w.frei(x, y0, z):
                w.setze(x, y0, z, planke)
            rand = x in (x0 - 2, x0 + B + 1) or z in (z0 - 2, z0 + T + 1)
            if rand and w.frei(x, y0 + 1, z):
                w.setze(x, y0 + 1, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                          waterlogged=False))
    _zaeune(w)
    # kegelförmiger Unterbau mit Bewuchs
    for k in range(1, 4):
        for x in range(x0 + k - 1, x0 + B - k + 1):
            for z in range(z0 + k - 1, z0 + T - k + 1):
                w.setze(x, y0 - k, z, w.b("stripped_spruce_log", axis="y") if (x + z) % 3 else w.b("spruce_planks"))
    blatt = laub(w, "azalea")
    for _ in range(10):
        x = int(w.rng.integers(x0 - 1, x0 + B + 1))
        z = int(w.rng.integers(z0 - 1, z0 + T + 1))
        for k in range(1, int(2 + w.rng.random() * 4)):
            if w.frei(x, y0 - k, z):
                w.setze(x, y0 - k, z, blatt)
    for x, z in ((x0 - 2, z0 - 2), (x0 + B + 1, z0 + T + 1), (x0 + B + 1, z0 - 2), (x0 - 2, z0 + T + 1)):
        haengelaterne(w, x, y0 - 1, z, 1 + int(w.rng.random() * 2))
    return first


def kugelgondel(w: Welt, cx, y_oben, cz, R=5):
    """Kugelförmige Holzgondel mit Fenstern und Reling. Oberster Punkt bei y_oben."""
    cy = y_oben - R
    holz = [w.b("spruce_planks"), w.b("dark_oak_planks"), w.b("stripped_spruce_log", axis="y"),
            w.b("spruce_planks")]
    for x in range(cx - R - 2, cx + R + 3):
        for y in range(cy - R - 1, cy + R + 1):
            for z in range(cz - R - 2, cz + R + 3):
                d = math.sqrt((x - cx) ** 2 + ((y - cy) * 1.15) ** 2 + (z - cz) ** 2)
                if d <= R:
                    huelle = d > R - 1.3
                    fenster = huelle and y in (cy, cy + 1) and (abs(x - cx) <= 1 or abs(z - cz) <= 1)
                    if huelle and not fenster:
                        w.setze(x, y, z, holz[int(w.rng.random() * 4)])
                    else:
                        w.setze(x, y, z, 0)
    # Deck-Ring
    for x in range(cx - R - 2, cx + R + 3):
        for z in range(cz - R - 2, cz + R + 3):
            d = math.hypot(x - cx, z - cz)
            if R - 0.5 < d <= R + 1.6:
                w.setze(x, cy - 1, z, w.b("dark_oak_slab", type="top", waterlogged=False))
    w.setze(cx, cy - 1, cz, w.b("lantern", hanging=False, waterlogged=False))
    haengelaterne(w, cx, cy - R - 2, cz, 1)


def tuermchenhaus(w: Welt, cx, y_oben, cz):
    """Kleines Türmchen-Haus mit hohem Kupferdach."""
    y0 = y_oben - 15
    first = fantasiehaus(w, cx - 2, y0, cz - 2, B=5, T=5, H=6, stil="kupfer", fundament=0)
    for k in range(1, 3):
        for x in range(cx - 2 + k, cx + 3 - k):
            for z in range(cz - 2 + k, cz + 3 - k):
                w.setze(x, y0 - k, z, w.b("dark_oak_planks"))
    haengelaterne(w, cx, y0 - 3, cz, 2)
    return first


def _zaeune(w: Welt):
    for (x, y, z), b in list(w.bloecke.items()):
        name = w.P.name(b)
        if not name.endswith("_fence"):
            continue
        verb = {}
        for k, (dx, dz) in {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}.items():
            n = w.hole(x + dx, y, z + dz)
            verb[k] = n is not None and n != 0 and (w.P.name(n).endswith("_fence") or
                                                    w.P.name(n).endswith("_log") or w.P.name(n).endswith("_planks"))
        w.bloecke[(x, y, z)] = w.b(name, waterlogged=False, **verb)


# ============================================================================ Der Bogen


def riesenbogen(seed, groesse=1, dorf=True):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    rng = w.rng
    S = [46, 72][groesse]
    H = [38, 60][groesse]
    r_fuss, r_oben = [7.0, 10.5][groesse], [4.5, 6.8][groesse]
    Rm, hm = [12, 18][groesse], [9, 14][groesse]

    # Mittellinie (kubische Bézierkurve) mit leichter Verdrehung aus der Ebene
    P = np.array([[-S / 2, 0], [-S / 2 + 0.08 * S, 1.15 * H], [S / 2 - 0.2 * S, 1.42 * H], [S / 2, 0]])
    t = np.linspace(0, 1, 500)
    bern = np.stack([(1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3], axis=1)
    xy = bern @ P
    zc = 0.09 * S * np.sin(np.pi * t) - 0.05 * S * (t - 0.5)
    C = np.stack([xy[:, 0], xy[:, 1], zc], axis=1)
    radius = r_oben + (r_fuss - r_oben) * np.abs(2 * t - 1) ** 2.0

    # Raster
    x_lo, x_hi = int(-S / 2 - Rm - 3), int(S / 2 + Rm + 3)
    y_lo, y_hi = -2, int(xy[:, 1].max() + r_oben + 4)
    z_lo, z_hi = int(zc.min() - r_fuss - Rm - 2), int(zc.max() + r_fuss + Rm + 2)
    X, Y, Z = np.meshgrid(np.arange(x_lo, x_hi + 1), np.arange(y_lo, y_hi + 1), np.arange(z_lo, z_hi + 1),
                          indexing="ij")
    pts = np.stack([X.ravel() + 0.5, Y.ravel() + 0.5, Z.ravel() + 0.5], axis=1)
    baum = cKDTree(C)
    dist, idx = baum.query(pts, workers=-1)
    feld1 = _rauschfeld(rng)
    rausch = _abtasten(feld1, pts[:, 0], pts[:, 1], pts[:, 2], 6, 6, 6)
    fest = dist < radius[idx] * (0.8 + 0.42 * rausch)
    fest = fest.reshape(X.shape)

    # Terrassierte Füße
    feld2 = _rauschfeld(rng, glatt=1.5)
    for fx, fz in ((C[0, 0], C[0, 2]), (C[-1, 0], C[-1, 2])):
        xs = np.arange(x_lo, x_hi + 1)[:, None]
        zs = np.arange(z_lo, z_hi + 1)[None, :]
        d = np.hypot(xs - fx, zs - fz)
        n2 = map_coordinates(feld2, [np.broadcast_to(xs, d.shape).ravel() / 5.0, np.zeros(d.size),
                                     np.broadcast_to(zs, d.shape).ravel() / 5.0], order=1, mode="wrap").reshape(d.shape)
        h = hm * np.clip(1 - d / (Rm * (0.8 + 0.4 * n2)), 0, 1) ** 1.3
        h = np.floor(h / 2) * 2
        for yi, y in enumerate(range(y_lo, y_hi + 1)):
            if y > hm + 1:
                break
            fest[:, yi, :] |= (y <= h) & (h > 0) & (y >= 0)
    fest[:, :2, :] &= False  # unter y=0 nichts (y_lo=-2 -> Index 0,1)

    # Nur eine Hülle behalten (innen hohl, spart Blöcke)
    innen = binary_erosion(fest, iterations=3)
    huelle = fest & ~innen
    oben_frei = fest & ~np.concatenate([fest[:, 1:, :], np.zeros_like(fest[:, :1, :])], axis=1)
    unten_frei = fest & ~np.concatenate([np.zeros_like(fest[:, :1, :]), fest[:, :-1, :]], axis=1)

    # Farben: senkrechte Gesteinsadern, Terrakotta-Verlauf
    fels = Verlauf(w, "Bogen", ["brown_terracotta", "coarse_dirt", "dirt", "terracotta", "granite"])
    stein = Verlauf(w, "Gesteinsadern", ["tuff", "cobblestone", "andesite", "stone"])
    gras, moos = w.b("grass_block", snowy=False), w.b("moss_block")
    feld3 = _rauschfeld(rng, glatt=1.0)
    ix, iy, iz = np.nonzero(huelle)
    wx, wy, wz = ix + x_lo, iy + y_lo, iz + z_lo
    ader = _abtasten(feld3, wx.astype(float), wy.astype(float), wz.astype(float), 2.5, 16.0, 2.5)
    hell = _abtasten(feld1, wx.astype(float) + 50, wy.astype(float), wz.astype(float), 4.0, 4.0, 4.0)
    oben = oben_frei[ix, iy, iz]
    for k in range(len(ix)):
        x, y, z = int(wx[k]), int(wy[k]), int(wz[k])
        if oben[k] and (y <= hm + 1 or rng.random() < 0.55):
            blk = gras if rng.random() < 0.9 else moos
        elif ader[k] < 0.36:
            blk = stein(ader[k] / 0.36 * 3.0, x, y, z)
        else:
            blk = fels(0.3 + 3.6 * hell[k] + (y / H) * 0.6 - 0.3, x, y, z)
        w.bloecke[(x, y, z)] = blk

    # Tropfsteine und Wurzeln an der Unterseite des Bogens
    def tropfstein(x, y, z, n):
        teile = (["base"] + ["middle"] * max(0, n - 3) + ["frustum", "tip"]) if n >= 3 else ["frustum", "tip"]
        for i, dicke in enumerate(teile):
            if not w.frei(x, y - i, z):
                return
            w.setze(x, y - i, z, w.b("pointed_dripstone", thickness=dicke, vertical_direction="down",
                                     waterlogged=False))

    jx, jy, jz = np.nonzero(unten_frei & (np.arange(y_lo, y_hi + 1)[None, :, None] > hm + 4))
    for k in range(len(jx)):
        x, y, z = int(jx[k] + x_lo), int(jy[k] + y_lo), int(jz[k] + z_lo)
        u = rng.random()
        if u < 0.09:
            tropfstein(x, y - 1, z, 2 + int(rng.random() * 4))
        elif u < 0.13:
            w.setze(x, y - 1, z, w.b("hanging_roots", waterlogged=False))
    ueberwuchern(w, None, ranken=0.08, pflanzen=0.45, buesche=0.03, max_ranke=6)

    def oberkante(x, z):
        for y in range(y_hi, y_lo, -1):
            if ist_massiv(w, w.hole(x, y, z)):
                return y
        return None

    def unterkante(x, z, ab):
        for y in range(y_lo, y_hi):
            if y > ab and (x, y, z) in w.bloecke and w.P.name(w.bloecke[(x, y, z)]) not in (
                    "minecraft:pointed_dripstone", "minecraft:hanging_roots", "minecraft:vine"):
                return y
        return None

    if dorf:
        # Unterkanten vorab bestimmen (bevor Häuser im Weg sind)
        haengend = [(0.33, "huette", -2), (0.45, "kugel", 3), (0.56, "tuerm", -3), (0.67, "huette2", 2)]
        if groesse == 0:
            haengend = [(0.38, "huette", 0), (0.58, "kugel", 0)]
        unterkanten = []
        for tt, art, dz in haengend:
            i = int(tt * (len(t) - 1))
            cx, cz = int(C[i, 0]), int(round(C[i, 2])) + dz
            unterkanten.append((cx, cz, art, unterkante(cx, cz, hm + 4)))
        # Häuser obendrauf
        haeuser = [(0.36, "kupfer", 11, 8, 6, False), (0.52, "stein", 9, 7, 5, False),
                   (0.68, "terrakotta", 8, 7, 5, True)]
        if groesse == 0:
            haeuser = [(0.4, "kupfer", 9, 7, 5, False), (0.62, "terrakotta", 7, 6, 4, True)]
        for tt, stil, B, T, Hh, rad in haeuser:
            i = int(tt * (len(t) - 1))
            cx, cz = int(C[i, 0]), int(round(C[i, 2]))
            spalten = [(x, z) for x in range(cx - B // 2, cx - B // 2 + B) for z in range(cz - T // 2, cz - T // 2 + T)]
            hoehen = [h for h in (oberkante(x, z) for x, z in spalten) if h is not None]
            y0 = (max(hoehen) if hoehen else int(C[i, 1] + r_oben)) + 1
            fantasiehaus(w, cx - B // 2, y0, cz - T // 2, B=B, T=T, H=Hh, stil=stil, fundament=14, rad=rad,
                         sockel_bloecke=["terracotta", "coarse_dirt", "andesite", "granite", "cobblestone"])
        # Zahnrad an der Seite
        i = int(0.6 * (len(t) - 1))
        gx, gy = int(C[i, 0]), int(C[i, 1])
        zs = [z for z in range(z_hi, z_lo, -1) if (gx, gy, z) in w.bloecke]
        if zs:
            zahnrad(w, gx, gy, zs[0] + 1, [4, 5][groesse])
        # Hängehäuser
        hoehe_haus = {"huette": 13, "huette2": 24, "kugel": 12, "tuerm": 20}
        for cx, cz, art, yb in unterkanten:
            if yb is None:
                continue
            laenge = int(3 + rng.random() * [4, 8][groesse])
            laenge = min(laenge, yb - 1 - hoehe_haus[art] - 8)
            if laenge < 1:
                continue
            y_haus = yb - 1 - laenge
            if art.startswith("huette"):
                haengehuette(w, cx, y_haus, cz, stil="holz" if art == "huette" else "kupfer", B=7, T=6)
            elif art == "kugel":
                kugelgondel(w, cx, y_haus, cz, R=[4, 5][groesse])
            else:
                tuermchenhaus(w, cx, y_haus, cz)
            # Kette exakt bis zum höchsten Punkt des Hängehauses führen
            spitze = max((y for (x, y, z) in w.bloecke if x == cx and z == cz and y < yb - 1 and
                          w.P.name(w.bloecke[(x, y, z)]) != "minecraft:chain"), default=y_haus)
            kette(w, cx, yb - 1, spitze + 1, cz)
        _zaeune(w)
    return w


# ============================================================================ Vorlagen

def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def vorlage_kupferhaus(seed, groesse=1):
    w = _welt(seed)
    fantasiehaus(w, -5, 0, -4, B=[9, 11][groesse], T=[7, 8][groesse], H=[5, 6][groesse], stil="kupfer", fundament=2)
    return w


def vorlage_steinhaus(seed, groesse=1):
    w = _welt(seed)
    fantasiehaus(w, -4, 0, -3, B=[8, 10][groesse], T=[7, 8][groesse], H=[5, 6][groesse], stil="stein", fundament=2)
    ueberwuchern(w, None, ranken=0.2, pflanzen=0.2, buesche=0.02)
    return w


def vorlage_terrakottahaus(seed, groesse=1):
    w = _welt(seed)
    fantasiehaus(w, -4, 0, -3, B=[7, 9][groesse], T=[6, 7][groesse], H=[4, 5][groesse], stil="terrakotta",
                 fundament=2, rad=True)
    return w


def vorlage_haengehuette(seed, groesse=1):
    w = _welt(seed)
    oben = [20, 26][groesse]
    kette(w, 0, oben + 6, oben + 1, 0)
    haengehuette(w, 0, oben, 0, stil=["holz", "kupfer"][seed % 2], B=[7, 9][groesse], T=[6, 7][groesse])
    w.anker = (0, 0, 0)
    return w


def vorlage_kugelgondel(seed, groesse=1):
    w = _welt(seed)
    kette(w, 0, 26, 21, 0)
    kugelgondel(w, 0, 20, 0, R=[4, 6][groesse])
    return w


RIESENBOGEN = {
    "riesenbogen_pur": ("Riesenbogen (pur)", lambda s, g: riesenbogen(s, g, False)),
    "riesenbogen_dorf": ("Riesenbogen mit Häusern", lambda s, g: riesenbogen(s, g, True)),
}

FANTASIEHAEUSER = {
    "kupferdachhaus": ("Kupferdach-Haus", vorlage_kupferhaus),
    "steinhaus": ("Steinhaus mit Spitzen", vorlage_steinhaus),
    "terrakottahaus": ("Terrakotta-Haus mit Zahnrad", vorlage_terrakottahaus),
    "haengehuette": ("Hängehütte", vorlage_haengehuette),
    "kugelgondel": ("Kugel-Gondel", vorlage_kugelgondel),
}

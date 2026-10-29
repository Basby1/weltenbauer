"""Felsen & Berge – Erweiterung der Kategorie „Felsen & Natur“: Felsnadeln, Tafelberg, Klamm, Bergkette, Steinwald,
Hoodoos, Basaltsäulen, Wackelstein, Brandungspfeiler, Überhang, Höhlenberg, Gipfelkreuz, Geröllhalde, Doppelbogen,
Pilzfelsen, Schichtfelsen, Schneegipfel, Monolith, Felsenkessel, Drei Zinnen, Horn, Passweg, Steinmännchen und
Felslabyrinth. Boden y = 0."""

from __future__ import annotations

import math

import numpy as np

import wald2
from flora import _neu, _r, _stil
from gewaesser import FELS, Land
from lib import Rauschen, einfuegen

U = [0.6, 1.0, 1.7, 2.8]
GRANIT = ["stone", "andesite", "stone", "cobblestone", "diorite", "andesite", "tuff"]
SANDST = ["red_sandstone", "orange_terracotta", "terracotta", "smooth_red_sandstone", "red_terracotta",
          "white_terracotta"]
KALK = ["calcite", "diorite", "stone", "andesite", "smooth_stone", "tuff"]


def vol(w, lo, hi, f, mat, rn=None):
    """Füllt alle Punkte im Quader lo..hi, für die f(X, Y, Z) wahr ist (numpy), mit mat(x, y, z) -> Name."""
    X, Y, Z = np.mgrid[lo[0]:hi[0] + 1, lo[1]:hi[1] + 1, lo[2]:hi[2] + 1]
    m = f(X.astype(float), Y.astype(float), Z.astype(float))
    for x, y, z in zip(X[m], Y[m], Z[m]):
        n = mat(int(x), int(y), int(z))
        w.setze(int(x), int(y), int(z), w.b(n, axis="y") if n in ("basalt", "polished_basalt") else w.b(n))


def gestein(liste, rn, schicht=0):
    def m(x, y, z):
        if schicht:
            return liste[int((y / schicht + rn(x, y, z) * 0.6)) % len(liste)]
        return liste[int(rn(x, y, z) * (len(liste) - 0.01))]
    return m


def bepflanzt(w, L, baeume, arten=("fichte", "kiefer"), dichte=0.35):
    L.bepflanzen(dichte, baeume=baeume, arten=arten, ufer_schilf=False)


# ============================================================================ Formationen

def felsnadel(seed, g=2):
    """Felsnadel: eine schlanke, hohe Steinsäule mit Rissen und Grasbändern, auf deren Spitze eine einsame Kiefer
    wächst, am Fuß Geröll und Farne."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    L = Land(w, R)
    L.heben(lambda x, z, h: max(0, 2 * u * (1 - math.hypot(x, z) / R)) + L.rn(x, 0, z))
    L.bauen(fels=GRANIT)
    bepflanzt(w, L, 2, ("busch",))
    H = _r(26 * u + 8)
    rn = Rauschen(w, 2.5)
    r0 = 3 * u + 1.5
    vol(w, (-int(r0) - 3, 1, -int(r0) - 3), (int(r0) + 3, H, int(r0) + 3),
        lambda X, Y, Z: np.hypot(X - np.sin(Y * 0.12) * 1.5, Z) < r0 * (1 - 0.35 * Y / H) *
        (0.85 + 0.3 * np.sin(Y * 0.7 + X * 0.3)), gestein(GRANIT, rn))
    einfuegen(w, wald2.kiefer(seed, H=_r(4 * u + 3)), round(math.sin(H * 0.12) * 1.5), H, 0)
    return w


def tafelberg(seed, g=2):
    """Tafelberg: ein Berg mit senkrechten, gebänderten Felswänden und völlig flachem, begrüntem Gipfelplateau,
    am Fuß eine Geröllschürze und Büsche."""
    w = _neu(seed)
    u = U[g]
    R = _r(20 * u + 6)
    L = Land(w, R)
    H = _r(16 * u + 5)
    L.heben(lambda x, z, h: H if math.hypot(x, z) < R * 0.55 * (0.9 + 0.2 * L.rn(x, 0, z)) else
            max(0, int((1 - (math.hypot(x, z) - R * 0.55) / (R * 0.45)) * 3 * u)))
    L.bauen(fels=SANDST if _stil(seed) == 0 else KALK, fels_ab=4)
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if y > 2 and ("terracotta" in n or "sandstone" in n):
            w.bloecke[(x, y, z)] = w.b(SANDST[(y // 2) % len(SANDST)] if _stil(seed) == 0 else KALK[(y // 2) % 6])
    bepflanzt(w, L, 3 + g, ("busch", "kiefer"))
    return w


def klamm(seed, g=2):
    """Klamm: eine tiefe, enge Schlucht mit glatt geschliffenen Wänden, unten ein grüner Wildbach, ein Holzsteg an
    der Wand entlang und Moos in den Ritzen."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    L = Land(w, R, form="quadrat")
    H = _r(16 * u + 5)
    L.heben(lambda x, z, h: H + 2 * L.rn(x, 0, z))
    pts = [(round(math.sin(k * 0.7) * 3 * u), -R + k * 2 * R // 8) for k in range(9)]
    L.fluss(pts, lambda t: 2.0 * u + 1, 0, tiefe=1, ufer=0)
    for (x, z) in list(L.h):
        d = min(math.hypot(x - a, z - b) for a, b in pts)
        if (x, z) not in L.wasser and d < 2.0 * u + 3:
            L.h[(x, z)] = min(L.h[(x, z)], int((d - 2.0 * u - 1) * 6) + 1)
    L.bauen(fels=["stone", "smooth_stone", "andesite", "mossy_cobblestone", "stone"])
    for z in range(-R, R + 1):
        k = (z + R) / (2 * R) * 8
        x = round(math.sin(min(8, k) * 0.7) * 3 * u + 2.0 * u + 2)
        w.setze(x, _r(H * 0.4), z, w.b("spruce_slab", type="bottom", waterlogged=False), False)
    bepflanzt(w, L, 4 + g, ("fichte",))
    return w


def bergkette(seed, g=2):
    """Bergkette: eine Reihe von drei Gipfeln unterschiedlicher Höhe mit Graten, Schnee auf den Spitzen,
    Felsbändern und Bergwald an den Hängen."""
    w = _neu(seed)
    u = U[g]
    R = _r(24 * u + 8)
    L = Land(w, R)
    gipfel = [(-R * 0.5, -R * 0.1, 18 * u + 6), (0, R * 0.05, 26 * u + 8), (R * 0.5, -R * 0.15, 15 * u + 5)]

    def h(x, z, _):
        v = 0
        for gx, gz, gh in gipfel:
            d = math.hypot(x - gx, z - gz) / (R * 0.45)
            v = max(v, gh * max(0, 1 - d) ** 1.4)
        return v * (0.85 + 0.3 * L.rn(x, 0, z))
    L.heben(h)
    L.bauen(fels=GRANIT, fels_ab=_r(10 * u + 3), schnee_ab=_r(18 * u + 5))
    bepflanzt(w, L, 6 + 3 * g, ("fichte", "fichte", "kiefer"))
    return w


def steinwald(seed, g=2):
    """Steinwald: ein Labyrinth aus hunderten scharfkantigen Kalksteinspitzen, dicht an dicht wie ein versteinerter
    Wald, dazwischen schmale Pfade und Büsche."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    L = Land(w, R)
    L.bauen()
    rng = w.rng
    rn = Rauschen(w, 2)
    for k in range(int(30 * u * u + 10)):
        a = rng.random() * 6.28
        d = R * 0.9 * math.sqrt(rng.random())
        cx, cz = math.cos(a) * d, math.sin(a) * d
        H = (6 + rng.random() * 10) * u
        r = (1.2 + rng.random()) * u
        vol(w, (int(cx - r) - 1, 1, int(cz - r) - 1), (int(cx + r) + 1, int(H) + 1, int(cz + r) + 1),
            lambda X, Y, Z, cx=cx, cz=cz, r=r, H=H: (np.abs(X - cx) + np.abs(Z - cz)) * 0.8 < r * np.clip(1 - Y / H, 0, 1) ** 0.7,
            gestein(["stone", "andesite", "smooth_stone", "diorite", "tuff"], rn))
    return w


def hoodoos(seed, g=2):
    """Hoodoos: rote und weiße Sandsteintürme mit dunklen Steinhüten wie Zipfelmützen, in Reihen auf einem Hang,
    bizarr gebändert."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    L = Land(w, R)
    L.heben(lambda x, z, h: max(0, -z / R) * 4 * u + L.rn(x, 0, z))
    L.bauen(gras="red_sand", fels=SANDST)
    rng = w.rng
    rn = Rauschen(w, 1.5)
    for k in range(int(12 * u + 6)):
        a = rng.random() * 6.28
        d = R * 0.85 * math.sqrt(rng.random())
        cx, cz = math.cos(a) * d, math.sin(a) * d
        y0 = L.h.get((round(cx), round(cz)), 0)
        H = (6 + rng.random() * 8) * u
        r = (0.9 + rng.random() * 0.6) * u + 0.4
        vol(w, (int(cx - r) - 2, y0, int(cz - r) - 2), (int(cx + r) + 2, y0 + int(H), int(cz + r) + 2),
            lambda X, Y, Z, cx=cx, cz=cz, r=r: np.hypot(X - cx, Z - cz) < r * (1 + 0.35 * np.sin((Y - y0) * 1.1)),
            lambda x, y, z: SANDST[(y // 2) % len(SANDST)])
        for dx in range(-int(r) - 1, int(r) + 2):
            for dz in range(-int(r) - 1, int(r) + 2):
                if dx * dx + dz * dz <= (r + 0.8) ** 2:
                    w.setze(round(cx) + dx, y0 + int(H) + 1, round(cz) + dz, w.b("brown_terracotta"))
    return w


def basaltsaeulen(seed, g=2):
    """Basaltsäulen: ein Damm aus tausenden sechseckigen Säulen, die wie Treppenstufen ins Meer laufen,
    unterschiedlich hoch, mit Tümpeln dazwischen."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    rng = w.rng
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) > R:
                continue
            q = round((x * 2 / 3) / 2)
            rr = round((-x / 3 + z * math.sqrt(3) / 3) / 2)
            hv = int(((q * 7919 + rr * 104729) % 97) / 97 * 4 * u) + int(max(0, -z / R) * 6 * u)
            if z > R * 0.4:
                hv = -2
            for y in range(-2, hv + 1):
                w.setze(x, y, z, w.b("basalt", axis="y") if (x + z) % 5 else w.b("smooth_basalt"))
            if z > R * 0.3:
                for y in range(hv + 1, 1):
                    w.setze(x, y, z, w.b("water", level=0))
    return w


def wackelstein(seed, g=1):
    """Wackelstein: ein riesiger, runder Findling balanciert scheinbar unmöglich auf einer schmalen Felsspitze, am
    Fuß Heide und kleinere Steine."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    L = Land(w, R)
    L.heben(lambda x, z, h: L.rn(x, 0, z) * 1.5)
    L.bauen()
    bepflanzt(w, L, 1, ("busch",))
    rn = Rauschen(w, 2)
    H = 6 * u + 3
    vol(w, (-4, 1, -4), (4, int(H), 4), lambda X, Y, Z: np.hypot(X, Z) < 2.5 * u * (1 - Y / H * 0.75) + 0.6,
        gestein(GRANIT, rn))
    rb = 4 * u + 2
    cy = H + rb - 1
    vol(w, (-int(rb) - 1, int(H) - 1, -int(rb) - 1), (int(rb) + 1, int(cy + rb) + 1, int(rb) + 1),
        lambda X, Y, Z: (X / rb) ** 2 + ((Y - cy) / (rb * 0.85)) ** 2 + (Z / (rb * 1.1)) ** 2 < 1,
        gestein(["granite", "polished_granite", "stone", "andesite"], rn))
    return w


def meeresstack(seed, g=2):
    """Brandungspfeiler: steile, freistehende Felstürme im Meer vor einer Klippe, von der Brandung umspült, mit
    Seevogelkolonien (Weiß) und Grasmützen."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                for y in (-2, -1, 0):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -3, z, w.b("sand"))
    rn = Rauschen(w, 2)
    for i, (cx, cz, H, r) in enumerate(((-R * 0.4, -R * 0.2, 20 * u + 6, 3.2 * u + 1.2),
                                        (R * 0.25, R * 0.1, 14 * u + 5, 2.4 * u + 1),
                                        (R * 0.05, -R * 0.55, 10 * u + 4, 2 * u + 1))):
        vol(w, (int(cx - r) - 3, -3, int(cz - r) - 3), (int(cx + r) + 3, int(H), int(cz + r) + 3),
            lambda X, Y, Z, cx=cx, cz=cz, r=r, H=H: np.hypot(X - cx, Z - cz) < r * (1 - 0.25 * Y / H) *
            (0.8 + 0.35 * np.sin(Y * 0.5 + X)),
            lambda x, y, z: "white_concrete" if rn(x, y, z) > 0.88 and y > 3 else GRANIT[int(rn(x, y, z) * 6.99)])
        for dx in range(-int(r), int(r) + 1):
            for dz in range(-int(r), int(r) + 1):
                if dx * dx + dz * dz < r * r * 0.6:
                    w.setze(round(cx) + dx, int(H) + 1, round(cz) + dz, w.b("grass_block", snowy=False), False)
    return w


def ueberhang(seed, g=2):
    """Felsüberhang: eine Felswand, deren oberer Teil weit über den Boden hinausragt und ein natürliches Dach bildet,
    darunter ein trockener Lagerplatz mit Feuerstelle."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    L = Land(w, R)
    L.heben(lambda x, z, h: L.rn(x, 0, z))
    L.bauen()
    bepflanzt(w, L, 3, ("kiefer", "busch"))
    H = 12 * u + 5
    rn = Rauschen(w, 2.5)
    vol(w, (-R, 1, -R), (R, int(H), 0),
        lambda X, Y, Z: (Z < -R * 0.2 + (Y / H) ** 2 * R * 0.7 + 1.5 * np.sin(X * 0.3)) & (np.abs(X) < R * 0.8),
        gestein(GRANIT, rn))
    w.setze(0, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for (x, z) in ((-2, 1), (2, 1)):
        w.setze(x, 1, z, w.b("oak_log", axis="x"))
    return w


def hoehlenberg(seed, g=2):
    """Höhlenberg: ein grüner Berg mit mehreren Höhleneingängen übereinander, Felsbändern, einem Pfad im Zickzack und
    einem Wasserfall aus der obersten Höhle."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    L = Land(w, R)
    H = 18 * u + 5
    L.heben(lambda x, z, h: H * max(0, 1 - math.hypot(x, z * 1.2) / R) ** 1.1 * (0.85 + 0.3 * L.rn(x, 0, z)))
    L.bauen(fels_ab=_r(H * 0.5))
    bepflanzt(w, L, 5 + 2 * g, ("fichte", "oak"))
    for k, (y, x) in enumerate(((2, -R * 0.2), (round(H * 0.35), R * 0.15), (round(H * 0.6), -R * 0.05))):
        hr = 2 * u + 1.5
        for xx in range(int(x - hr) - 1, int(x + hr) + 2):
            for yy in range(y, y + int(hr * 1.4) + 1):
                for z in range(0, R):
                    if ((xx - x) / hr) ** 2 + ((yy - y) / (hr * 1.4)) ** 2 < 1 and z < R * 0.6:
                        w.bloecke.pop((xx, yy, z), None)
        if k == 2:
            for yy in range(1, y + 1):
                p = (round(x), yy, round(R * 0.6))
                w.setze(*p, w.b("water", level=0 if yy == y else 8))
    return w


def gipfelkreuz(seed, g=2):
    """Gipfel mit Kreuz: ein felsiger Berggipfel mit Gipfelkreuz aus Holz, Gipfelbuch-Kästchen, Steinmännchen und
    einem schmalen Grat, über den der Weg heraufführt."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    L = Land(w, R)
    H = 20 * u + 6
    L.heben(lambda x, z, h: H * max(0, 1 - math.hypot(x, z) / R) ** 1.3 * (0.9 + 0.2 * L.rn(x, 0, z)))
    L.bauen(fels=GRANIT, fels_ab=_r(H * 0.35), schnee_ab=_r(H * 0.85))
    top = L.h.get((0, 0), int(H))
    for y in range(top + 1, top + 6):
        w.setze(0, y, 0, w.b("dark_oak_log", axis="y"))
    for x in (-1, 1):
        w.setze(x, top + 4, 0, w.b("dark_oak_log", axis="x"))
    w.setze(0, top + 2, 1, w.b("dark_oak_trapdoor", facing="south", half="top", open=False, powered=False,
                               waterlogged=False))
    for k in range(3):
        w.setze(2, top + 1 + k, 2, w.b("cobblestone" if k < 2 else "stone_slab", **(
            {"type": "bottom", "waterlogged": False} if k == 2 else {})))
    bepflanzt(w, L, 3 + g, ("fichte", "kiefer"))
    return w


def geroellhalde(seed, g=2):
    """Kar mit Geröllhalde: unter einer Felswand ergießt sich ein Fächer aus Schutt und Blöcken, unten ein kleiner
    Karsee, verkrüppelte Latschen am Rand."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    L = Land(w, R)
    H = 16 * u + 5
    L.heben(lambda x, z, h: H if z < -R * 0.45 else max(0, (-z / R + 0.45) * H * 0.8 + L.rn(x, 0, z)))
    L.see(0, round(R * 0.55), R * 0.25, 0, tiefe=2)
    L.bauen(fels=GRANIT)
    rng = w.rng
    for (x, z), h in L.h.items():
        if -R * 0.45 <= z < R * 0.2 and (x, z) not in L.wasser:
            w.setze(x, h, z, w.b(["gravel", "cobblestone", "andesite", "gravel", "stone"][int(rng.integers(5))]))
            if rng.random() < 0.04:
                w.setze(x, h + 1, z, w.b("cobblestone"))
    L.steine(5 + 3 * g, 1.2 * u, im_wasser=False, mat=GRANIT)
    bepflanzt(w, L, 2 + g, ("busch", "kiefer"))
    return w


def doppelbogen(seed, g=2):
    """Doppelbogen: zwei natürliche Felsbögen aus rotem Sandstein, die sich einen gemeinsamen Pfeiler teilen, darunter
    Wüstenbüsche und ein ausgetretener Pfad."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    L = Land(w, R)
    L.heben(lambda x, z, h: L.rn(x, 0, z))
    L.bauen(gras="red_sand", fels=SANDST)
    rn = Rauschen(w, 2)
    for sx in (-1, 1):
        cx = sx * 7 * u
        Rb, rb = 7 * u + 2, 2.2 * u + 1
        vol(w, (int(cx - Rb - rb) - 1, 0, -int(rb) - 3), (int(cx + Rb + rb) + 1, int(Rb + rb) + 2, int(rb) + 3),
            lambda X, Y, Z, cx=cx, Rb=Rb, rb=rb: ((np.hypot(X - cx, Y) - Rb) ** 2 + (Z / 1.3) ** 2 < rb * rb) & (Y >= 0),
            lambda x, y, z: SANDST[(y // 2) % len(SANDST)])
    return w


def pilzfelsen(seed, g=1):
    """Pilzfelsen: vom Wind ausgeschliffene Felsen mit dünnem Stiel und breitem, schwerem Kopf, in einer kargen
    Ebene."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    L = Land(w, R)
    L.bauen(gras="sand" if _stil(seed) == 0 else "coarse_dirt", fels=SANDST)
    rng = w.rng
    for k in range(3 + g):
        a = k / (3 + g) * 6.28 + 0.3
        cx, cz = math.cos(a) * R * 0.5, math.sin(a) * R * 0.5
        H = (4 + rng.random() * 3) * u + 2
        rk = (2.5 + rng.random()) * u + 1
        vol(w, (int(cx - rk) - 2, 1, int(cz - rk) - 2), (int(cx + rk) + 2, int(H + rk) + 1, int(cz + rk) + 2),
            lambda X, Y, Z, cx=cx, cz=cz, H=H, rk=rk: (np.hypot(X - cx, Z - cz) < 0.35 * rk + 0.8) & (Y < H) |
            (((X - cx) / rk) ** 2 + ((Y - H - rk * 0.3) / (rk * 0.55)) ** 2 + ((Z - cz) / rk) ** 2 < 1),
            lambda x, y, z: SANDST[(y // 2) % len(SANDST)])
    return w


def schichtfelsen(seed, g=2):
    """Schichtfelsen: eine wellenförmig geschwungene Felswand aus fein gebänderten Sandsteinschichten in Rot, Orange
    und Creme – wie eine erstarrte Welle."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    L = Land(w, R)
    L.bauen(gras="red_sand", fels=SANDST)
    H = 12 * u + 4
    farben = ["red_terracotta", "orange_terracotta", "white_terracotta", "terracotta", "red_sandstone",
              "yellow_terracotta", "orange_terracotta"]
    vol(w, (-R, 1, -R), (R, int(H), R),
        lambda X, Y, Z: (Z < -R * 0.1 + (Y / H) ** 1.5 * R * 0.6 - 0.5 * np.sin(X * 0.2) * R * 0.15) &
        (Z > -R * 0.9) & (np.hypot(X, Z) < R),
        lambda x, y, z: farben[int(y * 0.8 + math.sin(x * 0.2) * 2) % len(farben)])
    return w


def schneegipfel(seed, g=3):
    """Schneegipfel: ein mächtiger, vergletscherter Berg mit Eisrinnen, Schneefeldern, Felsrippen und einem
    blauen Gletscher, der in ein Geröllfeld ausläuft."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    L = Land(w, R)
    H = 26 * u + 8
    L.heben(lambda x, z, h: H * max(0, 1 - math.hypot(x, z) / R) ** 1.5 * (0.85 + 0.3 * L.rn(x, 0, z)))
    L.bauen(fels=GRANIT, fels_ab=_r(H * 0.3), schnee_ab=_r(H * 0.55))
    for (x, z), h in L.h.items():
        if abs(x - z * 0.3) < 2 + h * 0.05 and h > H * 0.2:
            w.setze(x, h, z, w.b("blue_ice" if (x + h) % 3 else "packed_ice"))
    bepflanzt(w, L, 4 + g, ("fichte",))
    return w


def monolith(seed, g=3):
    """Monolith: ein einziger, gewaltiger rotbrauner Inselberg mit gerundeten Flanken und senkrechten
    Wasserrinnen, der aus einer flachen Steppe aufragt."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    L = Land(w, R)
    L.bauen(gras="coarse_dirt", fels=SANDST)
    rn = Rauschen(w, 3)
    a, b = R * 0.7, R * 0.4
    H = 12 * u + 5
    vol(w, (-int(a) - 1, 1, -int(b) - 1), (int(a) + 1, int(H), int(b) + 1),
        lambda X, Y, Z: (X / a) ** 4 + (Z / b) ** 4 + (Y / H) ** 2.5 < 1 - 0.06 * np.abs(np.sin(X * 0.6)),
        lambda x, y, z: ["red_terracotta", "orange_terracotta", "terracotta", "red_sandstone"][
            int(rn(x, y, z) * 3.99)])
    L.bepflanzen(0.15, baeume=3, arten=("busch",), blumen=False)
    return w


def felsenkessel(seed, g=2):
    """Felsenkessel: ein halbrunder Talschluss mit senkrechten Wänden, von denen dünne Rinnsale fallen, unten eine
    Almwiese mit Blumen und Steinblöcken."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    L = Land(w, R)
    H = 18 * u + 5
    L.heben(lambda x, z, h: H + 2 * L.rn(x, 0, z) if math.hypot(x, z + R * 0.1) > R * 0.65 and z < R * 0.35 else
            L.rn(x, 3, z))
    L.bauen(fels=GRANIT)
    for k in range(3):
        a = -math.pi / 2 + (k - 1) * 0.6
        x, z = round(math.cos(a) * R * 0.65), round(math.sin(a) * R * 0.65 - R * 0.1)
        for y in range(1, int(H) + 1):
            w.setze(x, y, z + 1, w.b("water", level=0 if y == int(H) else 8))
    L.bepflanzen(0.6, baeume=2, arten=("fichte",))
    L.steine(4, 1.5 * u, im_wasser=False, mat=GRANIT)
    return w


def drei_zinnen(seed, g=3):
    """Drei Zinnen: drei mächtige, senkrechte Felstürme nebeneinander auf einem Geröllsockel, der höchste in der
    Mitte, mit Schneeresten in den Rinnen."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    L = Land(w, R)
    L.heben(lambda x, z, h: max(0, 3 * u * (1 - math.hypot(x, z) / R)) + L.rn(x, 0, z))
    L.bauen(fels=KALK)
    rn = Rauschen(w, 2)
    for i, (cx, H, r) in enumerate(((-R * 0.4, 18 * u + 6, 3 * u + 1.5), (0, 26 * u + 8, 3.6 * u + 1.5),
                                    (R * 0.35, 15 * u + 5, 2.6 * u + 1.2))):
        vol(w, (int(cx - r) - 2, 1, -int(r) - 2), (int(cx + r) + 2, int(H), int(r) + 2),
            lambda X, Y, Z, cx=cx, r=r, H=H: (np.abs(X - cx) * 0.9 + np.abs(Z) * 0.6 < r * (1 - 0.2 * Y / H)) &
            (Y < H - np.abs(X - cx) * 1.2),
            lambda x, y, z: "snow_block" if rn(x, y, z) > 0.9 else KALK[int(rn(x, y, z) * 5.99)])
    return w


def horn(seed, g=3):
    """Horn: eine pyramidenförmige, scharfkantige Bergspitze mit vier Graten und steilen Flanken, gekrönt von
    Schnee – das Wahrzeichen jedes Gebirges."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    L = Land(w, R)
    H = 30 * u + 8
    L.heben(lambda x, z, h: H * max(0, 1 - (abs(x) + abs(z) * 0.9) / R) ** 1.3 * (0.92 + 0.16 * L.rn(x, 0, z)))
    L.bauen(fels=GRANIT, fels_ab=_r(H * 0.2), schnee_ab=_r(H * 0.6))
    bepflanzt(w, L, 3 + g, ("fichte",))
    return w


def passweg(seed, g=2):
    """Bergpass: ein Saumpfad windet sich in Serpentinen zu einem Sattel zwischen zwei Bergen hinauf, oben eine
    Passhütte mit Wegweiser und Steinmännchen."""
    import pracht as P
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    L = Land(w, R)
    H = 14 * u + 5
    L.heben(lambda x, z, h: (H * 0.5 * max(0, 1 - abs(z) / R) + H * 0.6 * (abs(x) / R) ** 1.5) *
            (0.9 + 0.2 * L.rn(x, 0, z)))
    L.bauen(fels=GRANIT, fels_ab=_r(H * 0.7))
    for k in range(int(R * 3)):
        t = k / (R * 3)
        z = round(R - 2 * R * t)
        x = round(math.sin(t * 6 * math.pi) * R * 0.15)
        if (x, z) in L.h:
            w.setze(x, L.h[(x, z)], z, w.b("dirt_path" if k % 3 else "gravel"))
    top = L.h.get((0, 0), 0)
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="mcw_holz", holz="spruce")
    P.gebaeude(w, st, 3, -2, 7, 2, y0=top + 1, etagen=1, eh=3, dach="sattel", tuer="west", gauben=False, kamine=1)
    bepflanzt(w, L, 3 + g, ("fichte", "kiefer"))
    return w


def steinmaennchen(seed, g=1):
    """Steinmännchen-Feld: auf einem windigen Hochplateau stehen dutzende aufgeschichtete Steintürmchen von
    Wanderern, zwischen Flechten und Grasbüscheln."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    L = Land(w, R)
    L.heben(lambda x, z, h: L.rn(x, 0, z) * 2)
    L.bauen(gras="moss_block")
    rng = w.rng
    for k in range(int(12 * u + 6)):
        a = rng.random() * 6.28
        d = R * 0.85 * math.sqrt(rng.random())
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = L.h.get((x, z), 0) + 1
        for j in range(int(2 + rng.integers(3))):
            w.setze(x, y + j, z, w.b(["cobblestone", "andesite", "stone", "mossy_cobblestone"][j % 4]) if j < 2 else
                    w.b("stone_slab", type="bottom", waterlogged=False))
    L.bepflanzen(0.25, baeume=0)
    return w


def felslabyrinth(seed, g=2):
    """Felslabyrinth: riesige, wollsackartig gerundete Granitblöcke liegen kreuz und quer übereinander, dazwischen
    Spalten, Durchschlupfe und Farne."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    L = Land(w, R)
    L.bauen()
    rng = w.rng
    rn = Rauschen(w, 2)
    for k in range(int(10 * u + 6)):
        a = rng.random() * 6.28
        d = R * 0.85 * math.sqrt(rng.random())
        cx, cz = math.cos(a) * d, math.sin(a) * d
        rx, ry, rz = (2 + rng.random() * 3) * u, (1.5 + rng.random() * 2) * u, (2 + rng.random() * 3) * u
        cy = ry * 0.7 + (rng.random() < 0.3) * ry
        vol(w, (int(cx - rx) - 1, 0, int(cz - rz) - 1), (int(cx + rx) + 1, int(cy + ry) + 1, int(cz + rz) + 1),
            lambda X, Y, Z, cx=cx, cy=cy, cz=cz, rx=rx, ry=ry, rz=rz:
            ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 + ((Z - cz) / rz) ** 2 < 1,
            gestein(["granite", "polished_granite", "stone", "andesite", "mossy_cobblestone"], rn))
    L.bepflanzen(0.4, baeume=2, arten=("birke",))
    return w


def granitkuppe(seed, g=2):
    """Granitkuppe: ein glatt geschliffener, kahler Granitdom mit abblätternden Schalen, in dessen Ritzen Kiefern
    wurzeln, umgeben von lichtem Wald."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    L = Land(w, R)
    H = 14 * u + 5
    L.heben(lambda x, z, h: H * max(0, 1 - (math.hypot(x, z * 1.3) / (R * 0.75)) ** 2) ** 0.8)
    L.bauen(fels=["smooth_stone", "stone", "andesite", "polished_andesite", "diorite"], fels_ab=2)
    for (x, z), h in L.h.items():
        if h > 2 and (int(math.hypot(x, z * 1.3)) % 5 == 0):
            w.setze(x, h, z, w.b("polished_andesite"))
    bepflanzt(w, L, 5 + 2 * g, ("kiefer", "birke"))
    return w


BERGE = {
    "felsnadel": ("Felsnadel", felsnadel),
    "tafelberg": ("Tafelberg", tafelberg),
    "klamm": ("Klamm", klamm),
    "bergkette": ("Bergkette", bergkette),
    "steinwald": ("Steinwald", steinwald),
    "hoodoos": ("Hoodoos", hoodoos),
    "basaltsaeulen": ("Basaltsäulen", basaltsaeulen),
    "wackelstein": ("Wackelstein", wackelstein),
    "meeresstack": ("Brandungspfeiler", meeresstack),
    "ueberhang": ("Felsüberhang", ueberhang),
    "hoehlenberg": ("Höhlenberg", hoehlenberg),
    "gipfelkreuz": ("Gipfel mit Kreuz", gipfelkreuz),
    "geroellhalde": ("Kar mit Geröllhalde", geroellhalde),
    "doppelbogen": ("Doppelbogen", doppelbogen),
    "pilzfelsen": ("Pilzfelsen", pilzfelsen),
    "schichtfelsen": ("Schichtfelsen", schichtfelsen),
    "schneegipfel": ("Schneegipfel", schneegipfel),
    "monolith": ("Monolith", monolith),
    "felsenkessel": ("Felsenkessel", felsenkessel),
    "drei_zinnen": ("Drei Zinnen", drei_zinnen),
    "horn": ("Horn", horn),
    "passweg": ("Bergpass", passweg),
    "steinmaennchen": ("Steinmännchen-Feld", steinmaennchen),
    "felslabyrinth": ("Felslabyrinth", felslabyrinth),
    "granitkuppe": ("Granitkuppe", granitkuppe),
}

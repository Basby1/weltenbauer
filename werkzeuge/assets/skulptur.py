"""Bildhauer-Werkzeuge: Formen aus Grundkörpern zusammensetzen (vereinigen / abziehen) und mit
Farbverläufen schattieren, dazu Bausteine wie gestufte Sockel, Zaunringe und Treppenkränze."""

from __future__ import annotations

import math

import numpy as np

from lib import Verlauf, Welt


# --------------------------------------------------------------------------- Grundkörper (lokale Einheiten)

def ell(cx, cy, cz, rx, ry, rz):
    return lambda X, Y, Z: ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 + ((Z - cz) / rz) ** 2 <= 1


def kap(a, b, ra, rb=None, zf=1.0):
    """Kapsel / Kegelstumpf mit runden Enden von a nach b."""
    rb = ra if rb is None else rb
    a = np.asarray(a, float)
    d = np.asarray(b, float) - a
    L2 = max(float(d @ d), 1e-9)

    def f(X, Y, Z):
        px, py, pz = X - a[0], Y - a[1], Z - a[2]
        t = np.clip((px * d[0] + py * d[1] + pz * d[2]) / L2, 0, 1)
        qx, qy, qz = px - t * d[0], py - t * d[1], pz - t * d[2]
        r = ra + (rb - ra) * t
        return qx * qx + qy * qy + (qz / zf) ** 2 <= r * r
    return f


def kasten(x0, y0, z0, x1, y1, z1):
    return lambda X, Y, Z: (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1) & (Z >= z0) & (Z <= z1)


def kegel(cx, cz, y0, y1, r0, r1, zf=1.0):
    def f(X, Y, Z):
        t = (Y - y0) / (y1 - y0)
        r = r0 + (r1 - r0) * t
        return (Y >= y0) & (Y <= y1) & ((X - cx) ** 2 + ((Z - cz) / zf) ** 2 <= r * r)
    return f


def torus(cx, cy, cz, R, r, achse="y"):
    def f(X, Y, Z):
        x, y, z = X - cx, Y - cy, Z - cz
        if achse == "y":
            q = np.sqrt(x * x + z * z) - R
            return q * q + y * y <= r * r
        if achse == "z":
            q = np.sqrt(x * x + y * y) - R
            return q * q + z * z <= r * r
        q = np.sqrt(y * y + z * z) - R
        return q * q + x * x <= r * r
    return f


def und(*fs):
    def f(X, Y, Z):
        m = fs[0](X, Y, Z)
        for g in fs[1:]:
            m = m & g(X, Y, Z)
        return m
    return f


def ohne(f, g):
    return lambda X, Y, Z: f(X, Y, Z) & ~g(X, Y, Z)


def spiegel_x(f):
    """Form und ihr Spiegelbild an der Ebene x = 0."""
    return lambda X, Y, Z: f(X, Y, Z) | f(-X, Y, Z)


def dreh_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def dreh_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def dreh_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


# --------------------------------------------------------------------------- Skulptur

class Skulptur:
    """Sammelt Grundkörper mit Material-Etikett; spätere Teile überdecken frühere, None schneidet aus."""

    def __init__(self, w: Welt, u: float = 1.0):
        self.w = w
        self.u = u
        self.teile = []
        self.mats = {}

    def mat(self, etikett, quelle, basis=0.0, steigung=0.0, rausch=0.4):
        """quelle: Verlauf, Block-ID oder Funktion (x, y, z, lx, ly, lz) -> Block-ID."""
        self.mats[etikett] = (quelle, basis, steigung, rausch)

    def plus(self, form, etikett):
        self.teile.append((form, etikett))

    def minus(self, form):
        self.teile.append((form, None))

    def dicke(self, d):
        """Mindestdicke in lokalen Einheiten, damit dünne Teile auch klein lückenlos bleiben."""
        return max(d, 0.62 / self.u)

    def rendern(self, lo, hi, versatz=(0, 0, 0), dreh=None, ueberschreiben=True):
        u = self.u
        R = np.eye(3) if dreh is None else np.asarray(dreh, float)
        ecken = np.array([[a, b, c] for a in (lo[0], hi[0]) for b in (lo[1], hi[1]) for c in (lo[2], hi[2])]) * u
        welt = ecken @ R.T + np.asarray(versatz, float)
        wlo = np.floor(welt.min(0)).astype(int) - 1
        whi = np.ceil(welt.max(0)).astype(int) + 1
        X, Y, Z = np.mgrid[wlo[0]:whi[0] + 1, wlo[1]:whi[1] + 1, wlo[2]:whi[2] + 1]
        px = X + 0.5 - versatz[0]
        py = Y + 0.5 - versatz[1]
        pz = Z + 0.5 - versatz[2]
        lx = (R[0, 0] * px + R[1, 0] * py + R[2, 0] * pz) / u
        ly = (R[0, 1] * px + R[1, 1] * py + R[2, 1] * pz) / u
        lz = (R[0, 2] * px + R[1, 2] * py + R[2, 2] * pz) / u
        lab = np.full(X.shape, -1, dtype=np.int16)
        namen = []
        for form, etikett in self.teile:
            m = form(lx, ly, lz)
            if etikett is None:
                lab[m] = -1
            else:
                if etikett not in namen:
                    namen.append(etikett)
                lab[m] = namen.index(etikett)
        rng = self.w.rng
        for i, j, k in np.argwhere(lab >= 0):
            x, y, z = int(X[i, j, k]), int(Y[i, j, k]), int(Z[i, j, k])
            quelle, basis, steigung, rausch = self.mats[namen[lab[i, j, k]]]
            if isinstance(quelle, Verlauf):
                blk = quelle(basis + steigung * ly[i, j, k] + (rng.random() - 0.5) * rausch, x, y, z)
            elif callable(quelle):
                blk = quelle(x, y, z, lx[i, j, k], ly[i, j, k], lz[i, j, k])
            else:
                blk = quelle
            self.w.setze(x, y, z, blk, ueberschreiben)


# --------------------------------------------------------------------------- Blöcke mit Zuständen

def treppe(w, mat, facing, half="bottom"):
    return w.b(f"{mat}_stairs", facing=facing, half=half, shape="straight", waterlogged=False)


def platte(w, mat, typ="bottom"):
    return w.b(f"{mat}_slab", type=typ, waterlogged=False)


def zur_mitte(x, z, cx=0, cz=0):
    dx, dz = cx - x, cz - z
    if abs(dx) >= abs(dz):
        return "east" if dx > 0 else "west"
    return "south" if dz > 0 else "north"


def laterne(w, x, y, z, seele=False):
    w.setze(x, y, z, w.b("soul_lantern" if seele else "lantern", hanging=False, waterlogged=False))


def pfosten(w, x, y0, y1, z, mat):
    for y in range(y0, y1 + 1):
        w.setze(x, y, z, w.b(mat, up=True, north="none", south="none", east="none", west="none", waterlogged=False))


def verbinde(w, menge, mat, art="fence"):
    """Setzt Zäune oder Glasscheiben und verbindet sie untereinander."""
    menge = set(menge)
    for (x, y, z) in menge:
        n, s = (x, y, z - 1) in menge, (x, y, z + 1) in menge
        e, o = (x + 1, y, z) in menge, (x - 1, y, z) in menge
        w.setze(x, y, z, w.b(mat, north=n, south=s, east=e, west=o, waterlogged=False))


def kreisrand(r, cx=0, cz=0):
    """Lückenloser (4-zusammenhängender) Rand einer Kreisscheibe."""
    R = r + 0.5
    n = int(R) + 2

    def innen(x, z):
        return math.hypot(x, z) < R
    return [(x + cx, z + cz) for x in range(-n, n + 1) for z in range(-n, n + 1)
            if innen(x, z) and any(not innen(x + a, z + b) for a in (-1, 0, 1) for b in (-1, 0, 1))]


def scheibe(r, cx=0, cz=0):
    n = int(r) + 2
    return [(x + cx, z + cz) for x in range(-n, n + 1) for z in range(-n, n + 1) if math.hypot(x, z) < r + 0.5]


def linie(w, a, b, blk, dicke=0):
    a, b = np.asarray(a, float), np.asarray(b, float)
    n = int(np.abs(b - a).max() * 2) + 1
    for t in np.linspace(0, 1, n):
        p = a + (b - a) * t
        for dx in range(-dicke, dicke + 1):
            for dz in range(-dicke, dicke + 1):
                w.setze(round(p[0]) + dx, round(p[1]), round(p[2]) + dz, blk)


# --------------------------------------------------------------------------- Sockel

SOCKEL = {
    "schiefer": dict(voll="polished_deepslate", treppe="polished_deepslate", saeule="deepslate_bricks",
                     ecke="chiseled_deepslate", akzent="gold_block", pfosten="deepslate_brick_wall", seele=False),
    "stein": dict(voll="stone_bricks", treppe="stone_brick", saeule="polished_andesite",
                  ecke="chiseled_stone_bricks", akzent="gold_block", pfosten="stone_brick_wall", seele=False),
    "sandstein": dict(voll="smooth_sandstone", treppe="smooth_sandstone", saeule="cut_sandstone",
                      ecke="chiseled_sandstone", akzent="gold_block", pfosten="sandstone_wall", seele=False),
    "schwarz": dict(voll="polished_blackstone", treppe="polished_blackstone", saeule="polished_blackstone_bricks",
                    ecke="chiseled_polished_blackstone", akzent="gold_block", pfosten="polished_blackstone_brick_wall",
                    seele=True),
    "quarz": dict(voll="smooth_quartz", treppe="smooth_quartz", saeule="quartz_bricks",
                  ecke="chiseled_quartz_block", akzent="gold_block", pfosten="diorite_wall", seele=False),
    "purpur": dict(voll="purpur_block", treppe="purpur", saeule="end_stone_bricks", ecke="purpur_pillar",
                   akzent="crying_obsidian", pfosten="end_stone_brick_wall", seele=True),
}


def _randtreppe(w, mat, x, z, hx, hz, half="bottom"):
    if abs(x) == hx:
        return treppe(w, mat, "east" if x < 0 else "west", half)
    return treppe(w, mat, "south" if z < 0 else "north", half)


def sockel(w, m, rx, rz, stufen, sx, sz, hs, lichter=True):
    """Gestufter, rechteckiger Sockel mit Profil, Kranzgesims, Zierfeldern und Laternen.
    Gibt die erste freie Höhe über dem Sockel zurück."""
    voll, ecke = w.b(m["voll"]), w.b(m["ecke"])
    for k in range(stufen):
        hx, hz = rx - k, rz - k
        for x in range(-hx, hx + 1):
            for z in range(-hz, hz + 1):
                ax, az = abs(x) == hx, abs(z) == hz
                w.setze(x, k, z, ecke if ax and az else _randtreppe(w, m["treppe"], x, z, hx, hz) if ax or az else voll)
    y0 = stufen
    for x in range(-sx - 1, sx + 2):
        for z in range(-sz - 1, sz + 2):
            ax, az = abs(x) == sx + 1, abs(z) == sz + 1
            if ax or az:
                w.setze(x, y0, z, voll if ax and az else _randtreppe(w, m["treppe"], x, z, sx + 1, sz + 1))
    for y in range(y0, y0 + hs):
        for x in range(-sx, sx + 1):
            for z in range(-sz, sz + 1):
                w.setze(x, y, z, ecke if abs(x) == sx and abs(z) == sz else w.b(m["saeule"]))
    ym = y0 + hs // 2
    for (x, z, tx, tz) in ((0, -sz, 1, 0), (0, sz, 1, 0), (-sx, 0, 0, 1), (sx, 0, 0, 1)):
        w.setze(x, ym, z, w.b(m["akzent"]))
        if hs >= 3:
            for d in (-1, 1):
                w.setze(x + d * tx, ym, z + d * tz, ecke)
                w.setze(x, ym + d, z, ecke)
    top = y0 + hs
    for x in range(-sx - 1, sx + 2):
        for z in range(-sz - 1, sz + 2):
            ax, az = abs(x) == sx + 1, abs(z) == sz + 1
            w.setze(x, top, z, _randtreppe(w, m["treppe"], x, z, sx + 1, sz + 1, "top") if (ax or az) and not (ax and az)
                    else voll)
    cx, cz = rx - stufen + 1, rz - stufen + 1
    if lichter and cx >= sx + 3 and cz >= sz + 3:
        for a in (-1, 1):
            for b in (-1, 1):
                pfosten(w, a * cx, stufen, stufen + 1, b * cz, m["pfosten"])
                laterne(w, a * cx, stufen + 2, b * cz, m["seele"])
    return top + 1

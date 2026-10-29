"""Antike Monumente (neu) – 20 Bauten mit verwittertem Marmor, Travertin, Terrakottadächern, Zypressen,
Ölbäumen, Statuen und Mosaikplätzen. Stil 1 prächtig erhalten, Stil 2 verwitterte Ruine."""

from __future__ import annotations

import math

import numpy as np

import pracht as P
from lib import Rauschen, einfuegen, laub
from motive import figur
from pracht import Mat, gelaende
from skulptur import Skulptur, dreh_y, ell, kap, kreisrand, scheibe
from veredeln import bewuchs
from weltwunder import bl, hohl, platz, sk
from wueste_eis import kuppel

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    from lib import Welt
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


class Ant:
    def __init__(self, w, seed):
        self.w = w
        self.ruine = _stil(seed) == 1
        if not self.ruine:
            self.M = Mat(w, ["polished_andesite", "diorite", "polished_diorite", "calcite", "quartz_bricks",
                             "smooth_quartz", "smooth_quartz"], kontrast=0.9)
        else:
            self.M = Mat(w, ["mossy_cobblestone", "andesite", "sandstone", "cut_sandstone", "smooth_sandstone",
                             "calcite", "diorite"], kontrast=1.1)
        self.saeule = "quartz_pillar" if not self.ruine else "smooth_sandstone"
        self.kap = "chiseled_quartz_block" if not self.ruine else "chiseled_sandstone"
        self.basis = "quartz_bricks" if not self.ruine else "cut_sandstone"
        self.treppe = "quartz" if not self.ruine else "sandstone"
        self.platte = "smooth_quartz" if not self.ruine else "smooth_sandstone"
        self.dach = P.Dach(w, "ziegel" if not self.ruine else "mcw_ziegel")
        self.gold = "gold_block"
        self.rand = w.rng

    def m(self, x, y, z, t=0.5):
        return self.M(x, y, z, t)


def treppe_b(w, mat, facing, half="bottom"):
    return w.b(f"{mat}_stairs", facing=facing, half=half, shape="straight", waterlogged=False)


def stylobat(w, A, x0, z0, x1, z1, stufen=3, y0=0):
    for k in range(stufen):
        for x in range(x0 - stufen + k, x1 + stufen - k + 1):
            for z in range(z0 - stufen + k, z1 + stufen - k + 1):
                rand = x in (x0 - stufen + k, x1 + stufen - k) or z in (z0 - stufen + k, z1 + stufen - k)
                if rand:
                    f = "south" if z == z0 - stufen + k else "north" if z == z1 + stufen - k else \
                        "east" if x == x0 - stufen + k else "west"
                    w.setze(x, y0 + k, z, treppe_b(w, A.treppe, f))
                else:
                    w.setze(x, y0 + k, z, A.m(x, y0 + k, z, 0.2))
    return y0 + stufen


def saeule(w, A, x, z, y0, H, dick=False):
    """Säule mit Basis, Schaft (bei Ruine evtl. abgebrochen) und Kapitell. Gibt Oberkante zurück."""
    h = H
    if A.ruine and A.rand.random() < 0.35:
        h = max(2, int(H * (0.3 + 0.5 * A.rand.random())))
    pts = [(0, 0)] + ([(1, 0), (0, 1), (1, 1)] if dick else [])
    for dx, dz in pts:
        w.setze(x + dx, y0, z + dz, w.b(A.basis))
        for y in range(y0 + 1, y0 + h):
            w.setze(x + dx, y, z + dz, w.b(A.saeule, axis="y") if A.saeule.endswith("pillar") else w.b(A.saeule))
        if h == H:
            w.setze(x + dx, y0 + H, z + dz, w.b(A.kap))
    if h < H:
        for k in range(2):
            px, pz = x + int(A.rand.integers(-3, 4)), z + int(A.rand.integers(-3, 4))
            if w.frei(px, y0, pz):
                w.setze(px, y0, pz, w.b(A.saeule, axis="x") if A.saeule.endswith("pillar") else w.b(A.saeule))
    return y0 + H if h == H else None


def gebaelk(w, A, x0, z0, x1, z1, y, fries=True):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if x in (x0, x1) or z in (z0, z1):
                w.setze(x, y, z, A.m(x, y, z, 0.8))
                if fries:
                    w.setze(x, y + 1, z, w.b(A.kap) if (x + z) % 3 == 0 else A.m(x, y + 1, z, 0.9))
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            if x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1):
                f = "south" if z == z0 - 1 else "north" if z == z1 + 1 else "east" if x == x0 - 1 else "west"
                w.setze(x, y + 2, z, treppe_b(w, A.treppe, f, "top"))
    return y + 3


def satteldach_giebel(w, A, x0, z0, x1, z1, y, first_x=False):
    """Flaches antikes Satteldach mit dreieckigem Giebelfeld (Tympanon) und Akroterien."""
    if first_x:
        n = (z1 - z0) // 2 + 1
        for k in range(n):
            for x in range(x0 - 1, x1 + 2):
                for z in (z0 + k, z1 - k):
                    w.setze(x, y + k // 2, z, A.dach.treppe(x, y + k // 2, z, "south" if z == z0 + k else "north")
                            if k % 2 == 0 else A.dach.voll(x, y + k // 2, z))
            for z in range(z0 + k, z1 - k + 1):
                for x in (x0, x1):
                    w.setze(x, y + k // 2, z, A.m(x, y, z, 0.9))
        for x in (x0, x1):
            w.setze(x, y + n // 2 + 1, (z0 + z1) // 2, w.b(A.gold))
    else:
        n = (x1 - x0) // 2 + 1
        for k in range(n):
            for z in range(z0 - 1, z1 + 2):
                for x in (x0 + k, x1 - k):
                    w.setze(x, y + k // 2, z, A.dach.treppe(x, y + k // 2, z, "east" if x == x0 + k else "west")
                            if k % 2 == 0 else A.dach.voll(x, y + k // 2, z))
            for x in range(x0 + k, x1 - k + 1):
                for z in (z0, z1):
                    w.setze(x, y + k // 2, z, A.m(x, y, z, 0.9))
        for z in (z0, z1):
            w.setze((x0 + x1) // 2, y + n // 2 + 1, z, w.b(A.gold))


def zypresse(w, x, z, H=None, y0=1):
    H = H or int(7 + w.rng.integers(5))
    for y in range(y0, y0 + 2):
        w.setze(x, y, z, w.b("spruce_log", axis="y"))
    for y in range(y0 + 1, y0 + H):
        t = (y - y0) / H
        r = 1.3 * math.sin(min(1, t * 1.3) * math.pi) ** 0.7
        for xx, zz in scheibe(max(0.4, r), x, z):
            w.setze(xx, y, zz, laub(w, "spruce"), ueberschreiben=False)
    w.setze(x, y0 + H, z, laub(w, "spruce"))


def oelbaum(w, x, z):
    import wald2
    einfuegen(w, wald2.laubbaum(int(w.rng.integers(1, 10 ** 6)), "oak", H=6 + int(w.rng.integers(3)),
                                blaetter=[("azalea", 0.5), ("oak", 0.3), ("birch", 0.2)], breit=1.1), x, 0, z)


def statue(w, A, x, y, z, s=0.4, art="mensch", pose="stab", dreh=0.0):
    S = Skulptur(w, s)
    S.mat("k", sk(Mat(w, ["calcite", "smooth_quartz", "polished_diorite", "diorite"] if not A.ruine else
                      ["sandstone", "smooth_sandstone", "calcite", "mossy_cobblestone"]), y, y + 22 * s))
    S.mat("a", bl(w, "gold_block" if not A.ruine else "calcite"))
    S.mat("d", bl(w, "light_gray_concrete"))
    S.mat("g", bl(w, "shroomlight" if not A.ruine else "calcite"))
    figur(S, art, pose)
    S.rendern((-7, -1, -5), (7, 26, 7), versatz=(x + 0.5, y + 0.01, z + 0.5), dreh=dreh_y(dreh))


def sockel(w, A, x, z, y0=1, r=1, h=2):
    for y in range(y0, y0 + h):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                w.setze(x + dx, y, z + dz, A.m(x, y, z, 0.4) if y < y0 + h - 1 else w.b(A.platte))
    return y0 + h


def mosaik(w, A, x0, z0, x1, z1, y=0):
    farben = ["white_terracotta", "terracotta", "orange_terracotta", "red_terracotta", "black_terracotta",
              "light_gray_terracotta"]
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            d = max(abs(x - cx), abs(z - cz))
            ring = int(d) % 4
            w.setze(x, y, z, w.b(farben[(ring + (1 if (x + z) % 2 else 0)) % len(farben)]) if not A.ruine or
                    A.rand.random() > 0.25 else w.b("grass_block", snowy=False))


def ruinieren(w, A, ab_y=6, anteil=0.25):
    if not A.ruine:
        return
    rng = A.rand
    for (x, y, z) in list(w.bloecke):
        if y >= ab_y and rng.random() < anteil * (y - ab_y + 1) / 8:
            w.bloecke.pop((x, y, z), None)
    bewuchs(w, moos=0.05, ranken=0.03)


def _ende(w, A, art="wiese", R=None):
    xs = [p[0] for p in w.bloecke]
    zs = [p[2] for p in w.bloecke]
    cx, cz = round((min(xs) + max(xs)) / 2), round((min(zs) + max(zs)) / 2)
    R = R or int(max(max(xs) - min(xs), max(zs) - min(zs)) / 2 + 5)
    gelaende(w, R, cx, cz, art="wiese", dichte=0.35)
    hohl(w, 2)
    return w


# ============================================================================ Bauten


def tempel(seed, g=1):
    """Dorischer Tempel: Säulenumgang auf dreistufigem Sockel, Gebälk mit Triglyphenfries, flaches Ziegeldach mit
    Giebelfeld und goldenen Akroterien, Kultstatue in der Cella, Zypressen und Ölbäume."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    a, b = _r(5 * u + 3), _r(9 * u + 4)
    y = stylobat(w, A, -a, -b, a, b, 3)
    H = _r(7 * u + 3)
    for x in range(-a, a + 1, 2):
        for z in (-b, b):
            saeule(w, A, x, z, y, H)
    for z in range(-b + 2, b, 2):
        for x in (-a, a):
            saeule(w, A, x, z, y, H)
    for x in range(-a + 2, a - 1):
        for z in range(-b + 3, b - 2):
            if x in (-a + 2, a - 2) or z in (-b + 3, b - 3):
                for yy in range(y, y + H):
                    w.setze(x, yy, z, A.m(x, yy, z, 0.6))
    for yy in range(y, y + 3):
        w.bloecke.pop((0, yy, b - 3), None)
    ye = gebaelk(w, A, -a, -b, a, b, y + H + 1)
    satteldach_giebel(w, A, -a, -b, a, b, ye, first_x=False)
    statue(w, A, 0, y, 0, 0.3 * u + 0.12, "elf", "stab")
    for sz in (-1, 1):
        zypresse(w, -a - 6, sz * (b - 2))
        zypresse(w, a + 6, sz * (b - 2))
    oelbaum(w, a + 9, 0)
    ruinieren(w, A, y + 4)
    return _ende(w, A)


def tempelruine(seed, g=1):
    """Tempelruine: eingestürzter Säulentempel – nur noch Säulenstümpfe, ein stehendes Eckstück mit Gebälk,
    Trommeln im Gras, Moos und Efeu."""
    w = _welt(seed)
    A = Ant(w, seed)
    A.ruine = True
    A.M = Mat(w, ["mossy_cobblestone", "andesite", "diorite", "calcite", "smooth_quartz"], kontrast=1.1)
    u = U[g]
    a, b = _r(5 * u + 3), _r(8 * u + 4)
    y = stylobat(w, A, -a, -b, a, b, 2)
    H = _r(7 * u + 3)
    for x in range(-a, a + 1, 2):
        for z in (-b, b):
            saeule(w, A, x, z, y, H)
    for z in range(-b + 2, b, 2):
        for x in (-a, a):
            saeule(w, A, x, z, y, H)
    for x in range(-a, -a + 5):
        for z in range(-b, -b + 1):
            for yy in range(y, y + H + 1):
                w.setze(x, yy, z, w.b(A.saeule, axis="y") if x % 2 == 0 and yy < y + H else A.m(x, yy, z, 0.8))
    gebaelk(w, A, -a, -b, -a + 4, -b, y + H + 1)
    bewuchs(w, moos=0.08, ranken=0.06)
    return _ende(w, A)


def rundtempel(seed, g=1):
    """Rundtempel (Tholos): kreisrunder Säulenkranz auf Stufen um eine Cella, Kuppel aus Kupfer oder Ziegel,
    vergoldeter Abschluss, Opferaltar davor."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    R = 5 * u + 3
    for k in range(3):
        for x, z in scheibe(R + 3 - k):
            w.setze(x, k, z, A.m(x, k, z, 0.2))
    y = 3
    H = _r(6 * u + 3)
    n = max(10, int(R * 2.5))
    for i in range(n):
        a = i / n * 2 * math.pi
        saeule(w, A, round(math.cos(a) * R), round(math.sin(a) * R), y, H)
    for yy in range(y, y + H):
        for x, z in kreisrand(R * 0.6):
            w.setze(x, yy, z, A.m(x, yy, z, 0.6))
    for x, z in kreisrand(R + 0.5):
        w.setze(x, y + H + 1, z, A.m(x, y + H + 1, z, 0.9))
    kuppel(w, w.b("waxed_oxidized_copper") if not A.ruine else w.b("terracotta"), 0, 0, y + H + 2, R + 0.5,
           spitze="gold_block")
    sockel(w, A, 0, round(R) + 5, 1, 1, 2)
    w.setze(0, 3, round(R) + 5, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    ruinieren(w, A, y + 3)
    return _ende(w, A)


def triumphbogen(seed, g=1):
    """Triumphbogen: drei Durchgänge mit kassettierten Gewölben, vorgestellte Säulen, Reliefbänder, Attika mit
    Inschrift und eine goldene Quadriga obenauf."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    B = _r(10 * u + 5)
    T = _r(3 * u + 2)
    H = _r(12 * u + 6)
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            for y in range(0, H):
                haupt = abs(x) <= _r(B * 0.25) and y < H * 0.7 and (x / (B * 0.25 + 0.5)) ** 2 + \
                    ((y - H * 0.45) / (H * 0.28)) ** 2 < 1 or (abs(x) <= _r(B * 0.25) and y < H * 0.45)
                seite = abs(abs(x) - B * 0.65) <= _r(B * 0.12) and (y < H * 0.35 or
                                                                    ((abs(x) - B * 0.65) / (B * 0.13)) ** 2 +
                                                                    ((y - H * 0.35) / (H * 0.12)) ** 2 < 1)
                if haupt or seite:
                    continue
                relief = z in (-T, T) and y % 5 == 3 and abs(x) > B * 0.3
                w.setze(x, y, z, w.b(A.kap) if relief else A.m(x, y, z, y / H))
    for x in range(-B, B + 1, max(2, B // 3)):
        if abs(x) > B * 0.27:
            for z in (-T - 1, T + 1):
                for y in range(1, int(H * 0.75)):
                    w.setze(x, y, z, w.b(A.saeule, axis="y") if A.saeule.endswith("pillar") else w.b(A.saeule))
    for x in range(-B - 1, B + 2):
        for z in range(-T - 1, T + 2):
            w.setze(x, H, z, A.m(x, H, z, 1.0))
            if z in (-T - 1, T + 1) and abs(x) < B * 0.6:
                w.setze(x, H + 1, z, w.b("gold_block") if x % 2 else A.m(x, H, z, 1.0))
    S = Skulptur(w, 0.4 * u + 0.2)
    S.mat("g", bl(w, "gold_block"))
    for k in range(4):
        dx = (k - 1.5) * 2.8
        S.plus(ell(dx, 5, 0, 1.0, 1.4, 3.0), "g")
        S.plus(kap((dx, 6, 2.5), (dx, 9, 3.5), 0.7, 0.6), "g")
        for lx, lz in ((-0.6, -2), (0.6, -2), (-0.6, 2), (0.6, 2)):
            S.plus(kap((dx + lx, 4, lz), (dx + lx, 0, lz), 0.35, 0.3), "g")
    S.plus(lambda X, Y, Z: (np.abs(X) < 3.5) & (np.abs(Y - 3) < 1.4) & (Z < -2.5) & (Z > -6), "g")
    S.rendern((-8, -1, -8), (8, 12, 6), versatz=(0.5, H + 1.01, 0.5))
    ruinieren(w, A, int(H * 0.6))
    return _ende(w, A)


def aquaedukt(seed, g=1):
    """Aquädukt: zwei Bogenreihen übereinander, oben der Wasserkanal, Pfeiler aus gemischtem Stein mit Moos,
    unten ein Fluss und Zypressen."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    L = _r(22 * u + 8)
    sp = 6
    h1 = _r(6 * u + 4)
    h2 = _r(4 * u + 3)
    for x in range(-L, L + 1):
        for z in (-1, 0, 1):
            for y in range(0, h1 + h2 + 2):
                p = (x + L) % sp
                stufe1 = y < h1
                if stufe1:
                    bog = 1 <= p <= sp - 1 and (y < h1 - 2 or ((p - sp / 2) / (sp / 2 - 0.5)) ** 2 +
                                                  ((y - (h1 - 2)) / 2.0) ** 2 < 1)
                else:
                    q = (x + L) % (sp // 2)
                    bog = y < h1 + h2 - 1 and 1 <= q <= sp // 2 - 1 and y > h1
                if not bog:
                    w.setze(x, y, z, A.m(x, y, z, y / (h1 + h2)))
        w.setze(x, h1 + h2 + 1, 0, w.b("water", level=0))
    for x in range(-L, L + 1):
        for z in range(-6, 7):
            if abs(z) <= 3 and (x, 0, z) not in w.bloecke:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel"))
    for i in range(4):
        zypresse(w, -L + 4 + i * (2 * L - 8) // 3, 7)
    bewuchs(w, moos=0.04, ranken=0.03 if A.ruine else 0.01)
    return _ende(w, A)


def theater(seed, g=1):
    """Griechisches Theater: halbrunde Sitzränge in den Hang gebaut, Orchestra mit Mosaik, Bühnenhaus mit
    zweistöckiger Säulenfassade und Statuen in den Nischen."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    R = _r(14 * u + 6)
    for x, z in scheibe(R):
        if z <= 0:
            d = math.hypot(x, z)
            if d > R * 0.3:
                h = int((d - R * 0.3) / (R * 0.7) * R * 0.45) + 1
                for y in range(0, h + 1):
                    w.setze(x, y, z, A.m(x, y, z, 0.4) if y < h else treppe_b(w, A.treppe,
                                                                               "south" if abs(z) > abs(x) else
                                                                               ("east" if x < 0 else "west")))
    mosaik(w, A, -_r(R * 0.25), -_r(R * 0.25), _r(R * 0.25), _r(R * 0.15))
    B = _r(R * 0.75)
    Hb = _r(7 * u + 4)
    for x in range(-B, B + 1):
        for z in (4, 5):
            for y in range(0, Hb):
                nische = z == 4 and y in (2, 3, 4) and x % 4 == 0 and abs(x) < B - 1
                if not nische:
                    w.setze(x, y, z, A.m(x, y, z, y / Hb))
        for y in range(1, Hb):
            if x % 2 == 0:
                w.setze(x, y, 3, w.b(A.saeule, axis="y") if A.saeule.endswith("pillar") else w.b(A.saeule))
        w.setze(x, Hb, 3, A.m(x, Hb, 3, 0.9))
        w.setze(x, Hb, 4, A.m(x, Hb, 4, 0.9))
    for x in range(-B + 2, B - 1, 8):
        statue(w, A, x, 1, 1, 0.22 * u + 0.08, "mensch", "arme_hoch" if x % 16 else "denker")
    ruinieren(w, A, 4)
    return _ende(w, A)


def forum(seed, g=2):
    """Forum: großer gepflasterter Platz, an drei Seiten Säulenhallen, eine Rednertribüne, Ehrensäule, Brunnen und
    Reiterstatue in der Mitte."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    a, b = _r(12 * u + 6), _r(9 * u + 5)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.setze(x, 0, z, w.b(A.platte) if (x + z) % 3 else A.m(x, 0, z, 0.3))
    H = _r(5 * u + 3)
    for x in range(-a, a + 1, 2):
        for z in (-b, -b + 3):
            saeule(w, A, x, z, 1, H)
    for z in range(-b, b + 1, 2):
        for x in (-a, -a + 3, a, a - 3):
            saeule(w, A, x, z, 1, H)
    for x in range(-a - 1, a + 2):
        for z in range(-b - 1, b + 2):
            if z <= -b + 3 or abs(x) >= a - 3:
                w.setze(x, H + 2, z, A.m(x, H + 2, z, 0.9))
    for x in range(-3, 4):
        for z in range(b - 3, b + 1):
            for y in range(1, 3):
                w.setze(x, y, z, A.m(x, y, z, 0.5))
    for y in range(1, _r(12 * u + 6)):
        w.setze(-a // 2, y, 0, w.b(A.saeule, axis="y") if A.saeule.endswith("pillar") else w.b(A.saeule))
    statue(w, A, -a // 2, _r(12 * u + 6), 0, 0.2, "mensch", "arme_hoch")
    for x, z in scheibe(2.5, a // 2, 0):
        w.setze(x, 1, z, A.m(x, 1, z, 0.5))
    for x, z in scheibe(1.6, a // 2, 0):
        w.setze(x, 1, z, w.b("water", level=0))
    statue(w, A, 0, sockel(w, A, 0, 0, 1, 2, 3), 0, 0.3 * u + 0.1, "ritter", "schwert")
    ruinieren(w, A, 3)
    return _ende(w, A)


def pharos(seed, g=2):
    """Pharos: dreistufiger Leuchtturm – quadratischer Sockelbau, achteckiger Mittelteil, runder Laternenturm mit
    Feuer und Bronzestatue, auf einer Mole im Hafenbecken."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    R = _r(16 * u + 8)
    for x, z in scheibe(R + 4):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("sand"))
    a = _r(5 * u + 3)
    H1 = _r(12 * u + 6)
    for y in range(0, H1):
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                if max(abs(x), abs(z)) == a or y == 0:
                    fen = y % 5 == 3 and abs(x + z) % 3 == 0 and max(abs(x), abs(z)) == a
                    w.setze(x, y, z, w.b("glass_pane", north=True, south=True, east=True, west=True,
                                         waterlogged=False) if fen else A.m(x, y, z, y / H1))
    H2 = _r(8 * u + 4)
    r2 = a * 0.75
    for y in range(H1, H1 + H2):
        for x, z in kreisrand(r2):
            w.setze(x, y, z, A.m(x, y, z, 0.7))
    r3 = r2 * 0.6
    H3 = _r(5 * u + 3)
    for y in range(H1 + H2, H1 + H2 + H3):
        for x, z in kreisrand(r3):
            w.setze(x, y, z, w.b(A.saeule, axis="y") if (x + z) % 2 and A.saeule.endswith("pillar") else
                    A.m(x, y, z, 0.9))
    yt = H1 + H2 + H3
    w.setze(0, yt - 2, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    w.setze(0, yt - 3, 0, w.b("magma_block"))
    kuppel(w, w.b("waxed_copper_block"), 0, 0, yt, r3 + 0.5, spitze=None)
    statue(w, A, 0, yt + _r(r3) + 1, 0, 0.2 * u + 0.1, "mensch", "arme_hoch")
    for z in range(a + 1, R + 3):
        for x in (-2, -1, 0, 1, 2):
            w.setze(x, 0, z, A.m(x, 0, z, 0.3))
    return _ende(w, A, R=R + 3) if False else (hohl(w, 2) or w)


def pyramide(seed, g=2):
    """Pyramide: glatte Kalksteinverkleidung über Stufenkern, goldene Spitze, Totentempel mit Säulen und eine Allee
    aus Sphingen zum Eingang."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    R = _r(16 * u + 8)
    M = Mat(w, ["sandstone", "cut_sandstone", "smooth_sandstone", "smooth_sandstone", "chiseled_sandstone"],
            kontrast=0.8)
    for y in range(0, R + 1):
        r = R - y
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                if max(abs(x), abs(z)) >= r - 1:
                    if max(abs(x), abs(z)) == r and r > 0:
                        f = "south" if z == -r and abs(x) < r else "north" if z == r and abs(x) < r else \
                            "east" if x == -r else "west"
                        w.setze(x, y, z, w.b("smooth_sandstone_stairs", facing=f, half="bottom", shape="straight",
                                             waterlogged=False) if not A.ruine or w.rng.random() < 0.85 else
                                M(x, y, z, 0.5))
                    else:
                        w.setze(x, y, z, M(x, y, z, y / R))
    for y in range(R - 3, R + 1):
        for x in range(-(R - y), R - y + 1):
            for z in range(-(R - y), R - y + 1):
                w.setze(x, y, z, w.b("gold_block"))
    zt = R + 4
    for x in range(-4, 5):
        for z in range(zt, zt + 7):
            w.setze(x, 0, z, w.b("smooth_sandstone"))
    for x in (-4, -2, 2, 4):
        for z in (zt, zt + 6):
            for y in range(1, 5):
                w.setze(x, y, z, w.b("smooth_sandstone") if y < 4 else w.b("chiseled_sandstone"))
    for x in range(-4, 5):
        for z in range(zt, zt + 7):
            w.setze(x, 5, z, M(x, 5, z, 0.9))
    for k in range(3 + g):
        for sx in (-1, 1):
            z = zt + 9 + k * 5
            S = Skulptur(w, 0.3 * u + 0.15)
            S.mat("k", sk(M, 0, 10))
            S.plus(ell(0, 2, 0, 3, 2, 1.6), "k")
            S.plus(ell(3, 4, 0, 1.4, 2.0, 1.4), "k")
            S.plus(kap((2.5, 1, 1), (5, 1, 1), 0.6), "k")
            S.plus(kap((2.5, 1, -1), (5, 1, -1), 0.6), "k")
            S.rendern((-4, 0, -3), (6, 7, 3), versatz=(sx * 6 + 0.5, 1.01, z + 0.5),
                      dreh=dreh_y(math.pi / 2 * (1 if sx < 0 else -1) * -1 + (0 if sx < 0 else math.pi)))
    hohl(w, 3)
    w2 = w
    gelaende(w2, R + 12 + 5 * (3 + g), 0, 0, art="sand", dichte=0.15)
    return w2


def thermen(seed, g=2):
    """Thermen: Badeanlage mit großem Warmbad unter einer Kuppel, Becken mit Prismarin, Säulenhof (Palästra),
    kleine Kuppeln über den Kalt- und Lauwarmbädern."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    a, b = _r(12 * u + 6), _r(8 * u + 5)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.setze(x, 0, z, A.m(x, 0, z, 0.2))
    H = _r(6 * u + 4)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            if x in (-a, a) or z in (-b, b):
                for y in range(1, H):
                    fen = y in (3, 4) and (x + z) % 4 == 0 and not (x in (-a, a) and z in (-b, b))
                    w.setze(x, y, z, w.b("glass_pane", north=True, south=True, east=True, west=True,
                                         waterlogged=False) if fen else w.b("bricks") if (y + x) % 7 == 0 else
                            A.m(x, y, z, y / H))
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.setze(x, H, z, A.m(x, H, z, 0.9))
    Rk = min(a, b) * 0.6
    kuppel(w, lambda x, y, z, t: w.b("terracotta") if (x + y) % 3 else w.b("bricks"), 0, 0, H + 1, Rk,
           spitze="gold_block")
    for sx in (-1, 1):
        kuppel(w, w.b("terracotta"), sx * round(a * 0.7), 0, H + 1, Rk * 0.45, spitze=None)
    for x, z in scheibe(Rk * 0.7):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("prismarine_bricks"))
    for x in range(-a, a + 1, 2):
        for z in range(b + 2, b + 9):
            w.setze(x, 0, z, w.b(A.platte))
    for x in range(-a, a + 1, 3):
        for z in (b + 2, b + 8):
            saeule(w, A, x, z, 1, 4)
    ruinieren(w, A, H - 1)
    return _ende(w, A)


def villa(seed, g=1):
    """Römische Villa: Atrium mit Regenbecken, rote Ziegeldächer um einen Peristyl-Garten mit Säulengang und
    Brunnen, Weinlaube und Ölbäume."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    a, b = _r(8 * u + 5), _r(7 * u + 4)
    H = 4
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.setze(x, 0, z, w.b("smooth_stone") if (x + z) % 2 else w.b("polished_andesite"))
            innen = abs(x) < a - 4 and abs(z) < b - 4
            rand = (abs(x) in (a, a - 4) and abs(z) <= b) or (abs(z) in (b, b - 4) and abs(x) <= a)
            if rand and not innen:
                for y in range(1, H):
                    w.setze(x, y, z, w.b("white_terracotta") if (x + y + z) % 5 else w.b("terracotta"))
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            if not (abs(x) < a - 4 and abs(z) < b - 4):
                d = min(a - abs(x), b - abs(z))
                if d <= 4:
                    y = H + min(d, 4 - d) // 1
                    w.setze(x, H + (2 - abs(2 - d)) // 1, z, A.dach.voll(x, H, z) if d == 2 else
                            A.dach.treppe(x, H, z, "south" if z < 0 and abs(z) >= abs(x) * b / a else
                                          "north" if z > 0 and abs(z) >= abs(x) * b / a else
                                          "east" if x < 0 else "west"))
    for x in range(-a + 5, a - 4, 2):
        for z in (-b + 5, b - 5):
            saeule(w, A, x, z, 1, H - 1)
    mosaik(w, A, -a + 6, -b + 6, a - 6, b - 6)
    for x, z in scheibe(1.5):
        w.setze(x, 1, z, w.b("water", level=0))
    for y in (1, 2):
        w.bloecke.pop((0, y, b), None)
    for x in range(-a, a + 1, 3):
        for y in (1, 2, 3):
            w.setze(x, y, b + 3, w.b("oak_fence", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
    for x in range(-a, a + 1):
        w.setze(x, 4, b + 3, laub(w, "jungle") if x % 2 else laub(w, "oak"))
    oelbaum(w, a + 6, -b)
    oelbaum(w, -a - 6, b - 2)
    return _ende(w, A)


def stoa(seed, g=1):
    """Stoa: lange zweischiffige Säulenhalle mit Pultdach und Läden an der Rückwand, davor ein gepflasterter Platz
    mit Bänken und Statuen."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    L = _r(14 * u + 6)
    T = 5
    y = stylobat(w, A, -L, -T, L, T, 2)
    H = _r(5 * u + 3)
    for x in range(-L, L + 1, 2):
        saeule(w, A, x, T, y, H)
        saeule(w, A, x, 0, y, H + 1)
    for x in range(-L, L + 1):
        for yy in range(y, y + H + 2):
            w.setze(x, yy, -T, A.m(x, yy, -T, 0.6) if not (yy in (y, y + 1) and x % 4 == 0) else
                    w.b("dark_oak_door", facing="south", half="lower" if yy == y else "upper", hinge="left",
                        open=False, powered=False))
        for z in range(-T, T + 2):
            yy = y + H + 2 + (T - z) // 3
            w.setze(x, yy, z, A.dach.treppe(x, yy, z, "south"))
    for x in range(-L + 3, L - 2, 6):
        statue(w, A, x, 1, T + 6, 0.2 * u + 0.08, "mensch", "denker", dreh=math.pi)
    ruinieren(w, A, y + 3)
    return _ende(w, A)


def obelisk(seed, g=1):
    """Obelisk: schlanker Monolith mit Hieroglyphenbändern und goldener Spitze auf einem Sockel inmitten eines
    runden Mosaikplatzes mit vier Löwen."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    R = _r(8 * u + 5)
    yp = platz(w, R, A.M, rand=A.treppe)
    H = _r(18 * u + 8)
    for y in range(yp, yp + 3):
        for x in range(-2, 3):
            for z in range(-2, 3):
                w.setze(x, y, z, A.m(x, y, z, 0.3))
    b = 1
    for y in range(yp + 3, yp + 3 + H):
        for x in range(-b, b + 1):
            for z in range(-b, b + 1):
                glyph = (y + x * 2 + z) % 4 == 0 and (y - yp) % 7 > 1 and (abs(x) == b or abs(z) == b)
                w.setze(x, y, z, w.b("black_terracotta") if glyph else w.b("red_granite" if False else
                                                                           "polished_granite"))
    w.setze(0, yp + 3 + H, 0, w.b("gold_block"))
    for i in range(4):
        a = i / 4 * 2 * math.pi + math.pi / 4
        x, z = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        S = Skulptur(w, 0.25 * u + 0.1)
        S.mat("k", sk(Mat(w, ["sandstone", "smooth_sandstone", "gold_block"]), 0, 10))
        S.plus(ell(0, 2, 0, 3, 2, 1.6), "k")
        S.plus(ell(3, 4, 0, 1.6, 2.2, 1.6), "k")
        S.rendern((-4, 0, -3), (6, 7, 3), versatz=(x + 0.5, yp + 0.01, z + 0.5), dreh=dreh_y(-a + math.pi))
    hohl(w, 2)
    gelaende(w, R + 5, art="wiese", dichte=0.3)
    return w


def mausoleum_antik(seed, g=2):
    """Prunkmausoleum: hoher Sockelbau, darauf ein Säulenkranz, eine Stufenpyramide als Dach und eine goldene
    Quadriga an der Spitze; Löwenstatuen an den Stufen."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    a = _r(7 * u + 4)
    H1 = _r(8 * u + 4)
    y = stylobat(w, A, -a, -a, a, a, 2)
    for yy in range(y, y + H1):
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                if max(abs(x), abs(z)) == a:
                    w.setze(x, yy, z, A.m(x, yy, z, yy / (H1 + 10)) if yy % 4 else w.b(A.kap))
    y2 = y + H1
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            w.setze(x, y2, z, A.m(x, y2, z, 0.8))
    H2 = _r(6 * u + 3)
    for x in range(-a + 1, a, 2):
        for z in (-a + 1, a - 1):
            saeule(w, A, x, z, y2 + 1, H2)
    for z in range(-a + 1, a, 2):
        for x in (-a + 1, a - 1):
            saeule(w, A, x, z, y2 + 1, H2)
    y3 = y2 + H2 + 2
    for k in range(a + 1):
        for x in range(-a + k, a - k + 1):
            for z in range(-a + k, a - k + 1):
                if max(abs(x), abs(z)) == a - k:
                    w.setze(x, y3 + k, z, treppe_b(w, A.treppe, "south" if z == -(a - k) else "north" if z == a - k
                                                   else "east" if x == -(a - k) else "west"))
                elif k == a or max(abs(x), abs(z)) < a - k:
                    w.setze(x, y3 + k, z, A.m(x, y3 + k, z, 0.9))
    statue(w, A, 0, y3 + a + 1, 0, 0.25 * u + 0.1, "ritter", "arme_hoch")
    ruinieren(w, A, y2)
    return _ende(w, A)


def saeulenstrasse(seed, g=2):
    """Säulenstraße: gepflasterte Prachtstraße zwischen zwei Säulenreihen mit Gebälk, an beiden Enden ein
    Torbogen, Laternen, Statuen auf Konsolen und Läden hinter den Säulen."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    L = _r(20 * u + 8)
    B = 4
    H = _r(5 * u + 4)
    for z in range(-L, L + 1):
        for x in range(-B - 4, B + 5):
            w.setze(x, 0, z, w.b("polished_andesite") if abs(x) <= B and (x + z) % 2 else A.m(x, 0, z, 0.3))
        if z % 3 == 0:
            for sx in (-B - 1, B + 1):
                saeule(w, A, sx, z, 1, H)
        for sx in (-B - 1, B + 1):
            w.setze(sx, H + 1, z, A.m(sx, H + 1, z, 0.9))
            w.setze(sx + (1 if sx > 0 else -1), H + 1, z, A.m(sx, H + 1, z, 0.9))
        for sx in (-B - 4, B + 4):
            for y in range(1, H + 2):
                w.setze(sx, y, z, A.m(sx, y, z, y / H))
    for sz in (-1, 1):
        z = sz * L
        for x in range(-B - 4, B + 5):
            for y in range(1, H + 5):
                if abs(x) > B - 1 or y > H + 1:
                    w.setze(x, y, z, A.m(x, y, z, y / (H + 5)))
    for z in range(-L + 6, L - 5, 9):
        statue(w, A, 0, sockel(w, A, 0, z, 1, 1, 2), z, 0.18 * u + 0.08, "mensch", "stab")
    ruinieren(w, A, 3)
    return _ende(w, A)


def orakel(seed, g=2):
    """Orakelstätte: am Hang gestaffelte Terrassen mit Schatzhäuschen, eine heilige Quelle, ein Apollontempel
    auf der obersten Terrasse und ein kleines Theater darüber."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    n = 3
    a = _r(12 * u + 6)
    for k in range(n):
        z0 = -k * 8
        for x in range(-a, a + 1):
            for z in range(z0 - 8, z0 + 1):
                for y in range(0, k * 4 + 1):
                    w.setze(x, y, z, A.m(x, y, z, 0.2) if y < k * 4 else w.b("grass_block", snowy=False)
                            if (x + z) % 4 else w.b(A.platte))
        for x in range(-a, a + 1):
            w.setze(x, k * 4 - 1 if k else 0, z0 + 1, A.m(x, 0, z0, 0.5))
    for k in range(n * 4):
        for x in (-1, 0, 1):
            w.setze(x, k // 2 + 1 if False else min(k, n * 4), -k * 2 // 1 if False else -k * 2, treppe_b(w, A.treppe, "south"))
    sti = P.Stil(w, wand=A.M, sockel=A.M, gesims=A.treppe, dach="ziegel", holz="oak", laeden=False, blumen=0)
    for i, x in enumerate((-a + 3, a - 7)):
        P.gebaeude(w, sti, x, -6, x + 4, -2, y0=1, etagen=1, eh=4, dach="sattel", tuer="south", gauben=False,
                   kamine=0)
    yt = (n - 1) * 4 + 1
    zt = -(n - 1) * 8 - 4
    for x in range(-4, 5, 2):
        for z in (zt - 3, zt + 3):
            saeule(w, A, x, z, yt, 5)
    for x in range(-5, 6):
        for z in range(zt - 4, zt + 5):
            w.setze(x, yt + 6, z, A.m(x, yt + 6, z, 0.9))
    satteldach_giebel(w, A, -5, zt - 4, 5, zt + 4, yt + 7, first_x=True)
    for x, z in scheibe(2.0, a - 4, 4):
        w.setze(x, 0, z, w.b("water", level=0))
    ruinieren(w, A, yt + 2)
    return _ende(w, A)


def nymphaeum(seed, g=1):
    """Nymphäum: prächtige Brunnenfassade mit zwei Säulengeschossen, Nischen mit Nymphenstatuen, Wasser fällt aus
    Masken in ein langes Becken mit Seerosen."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    B = _r(9 * u + 5)
    H = _r(9 * u + 5)
    for x in range(-B, B + 1):
        for z in (-2, -1):
            for y in range(0, H):
                nische = z == -1 and 1 <= y <= 4 and x % 4 == 0 and abs(x) < B
                if not nische:
                    w.setze(x, y, z, A.m(x, y, z, y / H))
        if x % 2 == 0:
            for y in range(1, H // 2):
                w.setze(x, y, 0, w.b(A.saeule, axis="y") if A.saeule.endswith("pillar") else w.b(A.saeule))
            for y in range(H // 2 + 1, H - 1):
                w.setze(x, y, 0, w.b(A.saeule, axis="y") if A.saeule.endswith("pillar") else w.b(A.saeule))
        w.setze(x, H // 2, 0, A.m(x, 0, 0, 0.9))
        w.setze(x, H - 1, 0, A.m(x, 0, 0, 0.9))
    for x in range(-B + 4, B - 3, 8):
        statue(w, A, x, 1, -1, 0.15 * u + 0.06, "elf", "arme_hoch")
    for x in range(-B, B + 1):
        for z in range(1, 6):
            w.setze(x, 0, z, w.b("water", level=0) if abs(x) < B and z < 5 else A.m(x, 0, z, 0.3))
            w.setze(x, -1, z, w.b("prismarine_bricks"))
            if z == 3 and x % 5 == 0:
                w.setze(x, 1, z, w.b("lily_pad"))
    for x in range(-B + 2, B - 1, 4):
        for y in range(1, 4):
            w.setze(x, y, 1, w.b("water", level=0 if y == 3 else 8))
    ruinieren(w, A, H // 2)
    return _ende(w, A)


def hippodrom(seed, g=2):
    """Hippodrom: langgestreckte Rennbahn mit Sitzrängen auf beiden Seiten, einer Mittelmauer (Spina) mit
    Obelisken, Wendesäulen und einem Kaiserloge-Pavillon."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    L, B = _r(30 * u + 10), _r(8 * u + 5)
    for x in range(-L - 6, L + 7):
        for z in range(-B - 6, B + 7):
            d = (max(0, abs(x) - (L - B)) / B) ** 2 + (z / B) ** 2 if abs(x) > L - B else (z / B) ** 2
            if d <= 1:
                w.setze(x, 0, z, w.b("sand") if (x + z) % 9 else w.b("gravel"))
            elif d <= 1.9:
                h = int((math.sqrt(d) - 1) * 9) + 1
                for y in range(0, h + 1):
                    w.setze(x, y, z, A.m(x, y, z, 0.4))
    for x in range(-L + B, L - B + 1):
        for y in (1, 2):
            w.setze(x, y, 0, A.m(x, y, 0, 0.6))
    for x in (-L + B, 0, L - B):
        for y in range(3, 3 + _r(8 * u + 4)):
            w.setze(x, y, 0, w.b("polished_granite"))
        w.setze(x, 3 + _r(8 * u + 4), 0, w.b("gold_block"))
    P.gebaeude(w, P.Stil(w, wand=A.M, sockel=A.M, gesims=A.treppe, dach="ziegel", holz="oak", laeden=False,
                         blumen=0), -4, B + 4, 4, B + 8, y0=4, etagen=1, eh=4, dach="walm", tuer="north", gauben=False,
               kamine=0)
    hohl(w, 2)
    return w


def goettinnenstatue(seed, g=2):
    """Göttinnenstatue: eine gewaltige stehende Göttin mit Speer und Schild aus Marmor und Gold auf einem
    Stufensockel, flankiert von Feuerschalen und Lorbeerbäumen."""
    w = _welt(seed)
    A = Ant(w, seed)
    u = U[g]
    s = 0.8 * u + 0.3
    yp = platz(w, _r(10 * s + 6), A.M, rand=A.treppe)
    ys = sockel(w, A, 0, 0, yp, _r(3 * s), _r(3 * s))
    S = Skulptur(w, s)
    S.mat("k", sk(Mat(w, ["calcite", "smooth_quartz", "polished_diorite", "white_concrete"]), ys, ys + 24 * s))
    S.mat("a", bl(w, "gold_block"))
    S.mat("d", bl(w, "gold_block"))
    S.mat("g", bl(w, "gold_block"))
    figur(S, "elf", "stab")
    S.plus(lambda X, Y, Z: (((X + 3.2) / 0.6) ** 2 + ((Y - 9) / 3.0) ** 2 + ((Z - 1) / 3.0) ** 2 < 1), "a")
    S.rendern((-8, -1, -5), (8, 26, 7), versatz=(0.5, ys + 0.01, 0.5))
    for sx in (-1, 1):
        for y in range(yp, yp + 3):
            w.setze(sx * (_r(3 * s) + 3), y, 2, A.m(0, y, 0, 0.5))
        w.setze(sx * (_r(3 * s) + 3), yp + 3, 2, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                      waterlogged=False))
        oelbaum(w, sx * (_r(10 * s) + 2), -3)
    hohl(w, 2)
    return w


def kolosseum_k(seed, g=2):
    """Amphitheater: elliptische Arena mit drei Arkadengeschossen, Sitzrängen, Sandarena und Gladiatorenstatuen."""
    from weltwunder5 import kolosseum
    return kolosseum(seed, {0: 0, 1: 1, 2: 2, 3: 2}[g] if False else g)


ANTIKE2 = {
    "tempel": ("Säulentempel", tempel),
    "tempelruine": ("Tempelruine", tempelruine),
    "rundtempel": ("Rundtempel", rundtempel),
    "triumphbogen": ("Triumphbogen", triumphbogen),
    "aquaedukt": ("Aquädukt", aquaedukt),
    "theater": ("Theater", theater),
    "forum": ("Forum", forum),
    "pharos": ("Pharos-Leuchtturm", pharos),
    "pyramide": ("Pyramide", pyramide),
    "thermen": ("Thermen", thermen),
    "villa": ("Römische Villa", villa),
    "stoa": ("Stoa", stoa),
    "obelisk": ("Obelisk", obelisk),
    "mausoleum": ("Prunkmausoleum", mausoleum_antik),
    "saeulenstrasse": ("Säulenstraße", saeulenstrasse),
    "orakel": ("Orakelstätte", orakel),
    "nymphaeum": ("Nymphäum", nymphaeum),
    "hippodrom": ("Hippodrom", hippodrom),
    "goettin": ("Göttinnenstatue", goettinnenstatue),
}


def _kolosseum_alt(seed, g=2):
    """Kolosseum: elliptisches Amphitheater mit drei Arkadengeschossen, Attika, Sitzrängen und Sandarena."""
    import antike
    from veredeln import veredle
    return veredle(antike.ANTIKE["kolosseum"][1](seed, g), art="wiese", moos=0.02, ranken=0.01)


ANTIKE2["kolosseum"] = ("Kolosseum", _kolosseum_alt)

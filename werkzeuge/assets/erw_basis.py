"""Gemeinsame Bausteine für die Erweiterungen (erw_*.py): Boden, Bäume, Figuren, einfache Häuser."""

from __future__ import annotations

import math

import wald2
from feinbau import Dachmat, Mix, fensterreihe, kamin, satteldach, treppe, tuer
from lib import Rauschen, einfuegen
from skulptur import Skulptur, dreh_y, kreisrand

S = [0.6, 1.0, 1.6, 2.5]


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


BLUMEN = ["poppy", "dandelion", "oxeye_daisy", "azure_bluet", "cornflower", "allium", "red_tulip", "white_tulip"]


def wiese(w, R, huegel=0.5, cx=0, cz=0, dichte=1.0, blumen=0.04, art="wiese"):
    """Lebendiger Wiesenboden; gibt Höhen je Zelle zurück. art: wiese · wald · kies · strand · moor"""
    rn = Rauschen(w, 6)
    rf = Rauschen(w, 2)
    rng = w.rng
    zellen = {}
    oben = {"wiese": [("grass_block", 0.72), ("coarse_dirt", 0.82), ("moss_block", 0.9), ("grass_block", 1.01)],
            "wald": [("podzol", 0.35), ("grass_block", 0.7), ("moss_block", 0.85), ("coarse_dirt", 1.01)],
            "kies": [("gravel", 0.4), ("grass_block", 0.8), ("cobblestone", 0.9), ("coarse_dirt", 1.01)],
            "strand": [("sand", 0.6), ("gravel", 0.75), ("sand", 1.01)],
            "moor": [("mud", 0.16), ("grass_block", 0.62), ("moss_block", 0.85), ("podzol", 1.01)]}[art]
    for x in range(cx - int(R) - 2, cx + int(R) + 3):
        for z in range(cz - int(R) - 2, cz + int(R) + 3):
            if math.hypot(x - cx, z - cz) <= R + 2 * rn(x, 0, z):
                h = int(huegel * 2 * rn(x * 0.7, 3, z * 0.7))
                v = rf(x, 4, z)
                b = next(n for n, t in oben if v < t)
                for y in range(-2, h):
                    w.setze(x, y, z, w.b("dirt" if art != "strand" else "sand"))
                w.setze(x, h, z, w.b(b, snowy=False) if b in ("grass_block", "podzol") else w.b(b))
                zellen[(x, z)] = h
                if b == "grass_block":
                    q = rng.random() / max(0.01, dichte)
                    if q < blumen:
                        w.setze(x, h + 1, z, w.b(BLUMEN[int(rng.integers(len(BLUMEN)))]))
                    elif q < 0.18:
                        w.setze(x, h + 1, z, w.b("grass"))
    return zellen


def baum(w, x, y, z, seed, H, holz="oak"):
    einfuegen(w, wald2.laubbaum(seed + x * 13 + z * 7, holz=holz, H=int(H)), x, y, z)


def fichte(w, x, y, z, seed, H, schnee=False):
    einfuegen(w, wald2.fichte(seed + x * 31 + z * 7, H=int(H), schnee=schnee), x, y, z)


def birke(w, x, y, z, seed, H):
    einfuegen(w, wald2.birke(seed + x * 17 + z * 5, H=int(H)), x, y, z)


def baumrand(w, zellen, R, n, seed, innen=0.78, H=(8, 14), art="laub"):
    rng = w.rng
    for i in range(n):
        a = rng.random() * 6.28
        r = R * (innen + rng.random() * (0.98 - innen))
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        y = zellen.get((x, z), 0) + 1
        hh = H[0] + rng.random() * (H[1] - H[0])
        if art == "fichte" or (art == "misch" and i % 2):
            fichte(w, x, y, z, seed, hh)
        elif art == "birke":
            birke(w, x, y, z, seed, hh)
        else:
            baum(w, x, y, z, seed, hh, holz="oak" if i % 3 else "birch")


def figur(w, u, teile, lo, hi, pos=(0, 0, 0), winkel=0.0):
    """teile: [(Form, Block oder Funktion oder None=ausschneiden)]"""
    Sk = Skulptur(w, u)
    for i, (form, blk) in enumerate(teile):
        if blk is None:
            Sk.minus(form)
            continue
        Sk.mat(str(i), blk)
        Sk.plus(form, str(i))
    Sk.rendern(lo, hi, versatz=(pos[0] + 0.5, pos[1], pos[2] + 0.5), dreh=dreh_y(winkel))


def hoehe(w, x, z, bis=60, ab=-3):
    for y in range(bis, ab - 1, -1):
        if not w.frei(x, y, z):
            return y
    return ab


def haus(w, cx, cz, B, T, y0, wand, holz="spruce", H=4, dach=("spruce", "dark_oak"), tuer_s="south", schorn=True,
         steil=1, sockel=None, fenster=True, eckpfosten=True, giebel=None):
    """Einfaches, aber detailliertes Haus: Sockel, Wände (Mix oder Funktion), Eckpfosten, Fenster mit Läden,
    Tür mit Vordach, Satteldach, Kamin. Gibt die Firsthöhe zurück."""
    x0, z0 = cx - B // 2, cz - T // 2
    x1, z1 = x0 + B - 1, z0 + T - 1
    sockel = sockel or M(w, [("cobblestone", 3), ("mossy_cobblestone", 1), ("stone", 1)])
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            w.setze(x, y0 - 1, z, sockel(x, y0 - 1, z) if x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1)
                    else w.b(f"{holz}_planks"))
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            for y in range(y0, y0 + H):
                rand = x in (x0, x1) or z in (z0, z1)
                if rand:
                    ecke = x in (x0, x1) and z in (z0, z1)
                    w.setze(x, y, z, w.b(f"{holz}_log", axis="y") if ecke and eckpfosten else wand(x, y, z))
                else:
                    w.bloecke.pop((x, y, z), None)
    if fenster:
        fensterreihe(w, x0, z0, x1, z1, y0 + 1, ("north", "south", "east", "west"), abstand=3, holz=holz,
                     blumen=0.3)
    d = {"south": (cx, z1), "north": (cx, z0), "east": (x1, cz), "west": (x0, cz)}[tuer_s]
    tuer(w, d[0], y0, d[1], tuer_s, holz=holz, stufen=0)
    first = satteldach(w, x0, z0, x1, z1, y0 + H, Dachmat(w, list(dach)), first_x=B >= T, ue=1,
                       giebel=giebel or wand, traufe=holz, steil=steil)
    if schorn:
        kamin(w, x1 - 1, z0 + 1, y0, (first or y0 + H + 3) + 1, M(w, [("cobblestone", 2), ("stone_bricks", 1)]))
    return first or y0 + H + 3


def grasdach(w, x0, z0, x1, z1, y, first_x=True, ue=1):
    """Grassodendach: gestufte Satteldach-Form aus Erde mit Grasdecke und herabhängendem Moos."""
    if first_x:
        a0, a1, b0, b1 = z0 - ue, z1 + ue, x0 - ue, x1 + ue
    else:
        a0, a1, b0, b1 = x0 - ue, x1 + ue, z0 - ue, z1 + ue
    mitte = (a0 + a1) / 2
    halb = (a1 - a0) / 2
    top = y
    for a in range(a0, a1 + 1):
        h = int(round((halb - abs(a - mitte)) * 0.9))
        for b in range(b0, b1 + 1):
            x, z = (b, a) if first_x else (a, b)
            for k in range(h + 1):
                w.setze(x, y + k, z, w.b("dirt") if k < h else w.b("grass_block", snowy=False))
            top = max(top, y + h)
            if a in (a0, a1) and (b % 3 == 0):
                w.setze(x, y - 1, z, w.b("moss_carpet") if False else w.b("vine", north=a == a1 and first_x,
                                                                          south=a == a0 and first_x,
                                                                          east=a == a0 and not first_x,
                                                                          west=a == a1 and not first_x, up=False),
                        False)
    return top


def ring(w, r, cx=0, cz=0):
    return kreisrand(r, cx, cz)


def zaunreihe(w, pts, blk, zellen=None):
    for (a, b) in zip(pts, pts[1:]):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for k in range(n + 1):
            t = k / n
            x, z = round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t)
            y = (zellen.get((x, z), 0) if zellen else 0) + 1
            w.setze(x, y, z, blk, False)

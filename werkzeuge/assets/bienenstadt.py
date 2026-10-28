"""Bienenstadt – Paket: Stockhäuser (Bienenkorb-Form), Wabentürme, Königinnen-Palast, Honigbrunnen,
Wabenmarkt, Riesenblumen, Bienenstatuen und eine ganze Bienenstadt.
Stil 1 Goldstock (Stroh, Honig, Birke), Stil 2 Wildstock (Moos, dunkles Holz, Bernstein, Glimmlicht)."""

from __future__ import annotations

import math

import numpy as np

from lib import Welt, laub
from skulptur import Skulptur, ell, kap, kreisrand, platte, scheibe, spiegel_x, verbinde

U = [0.6, 1.0, 1.7, 2.8]
W3 = math.sqrt(3)


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def hexd(x, z):
    """Abstandsmaß eines Sechsecks mit flacher Ober-/Unterkante (in z)."""
    return max(abs(z), (abs(x) * W3 + abs(z)) / 2)


class Bienen:
    def __init__(self, w, seed):
        self.w = w
        self.wild = _stil(seed) == 1
        b = w.b
        self.wabe = b("honeycomb_block")
        self.honig = b("honey_block")
        self.gold = b("gold_block")
        self.dunkel = b("black_wool")
        self.gelb = b("yellow_wool")
        if not self.wild:
            self.stroh = [b("hay_block", axis="y"), b("yellow_terracotta"), b("hay_block", axis="y")]
            self.band = b("orange_terracotta")
            self.holz = "birch"
            self.glas = b("orange_stained_glass")
            self.licht = b("ochre_froglight")
            self.boden = [b("grass_block", snowy=False), b("grass_block", snowy=False), b("moss_block")]
            self.blumen = ["dandelion", "poppy", "oxeye_daisy", "azure_bluet", "cornflower", "allium"]
            self.bluete = [b("pink_wool"), b("white_wool"), b("light_blue_wool"), b("magenta_wool")]
        else:
            self.stroh = [b("moss_block"), b("brown_terracotta"), b("mud_bricks")]
            self.band = b("dark_oak_planks")
            self.holz = "dark_oak"
            self.glas = b("yellow_stained_glass")
            self.licht = b("verdant_froglight")
            self.boden = [b("moss_block"), b("grass_block", snowy=False), b("podzol", snowy=False)]
            self.blumen = ["blue_orchid", "allium", "lily_of_the_valley", "red_tulip", "orange_tulip"]
            self.bluete = [b("orange_wool"), b("red_wool"), b("purple_wool"), b("yellow_wool")]

    def ein(self, liste):
        return liste[int(self.w.rng.integers(len(liste)))]


def _boden(w, f, r, cx=0, cz=0):
    for x, z in scheibe(r, cx, cz):
        w.setze(x, 0, z, f.ein(f.boden), ueberschreiben=False)


def _streu(w, f, r, dichte=0.14, cx=0, cz=0):
    for x, z in scheibe(r, cx, cz):
        if w.frei(x, 1, z) and w.hole(x, 0, z) in f.boden and w.rng.random() < dichte:
            if w.rng.random() < 0.08:
                w.setze(x, 1, z, w.b("bee_nest", facing="south", honey_level=5))
            elif w.rng.random() < 0.5:
                w.setze(x, 1, z, w.b("pink_petals", facing="north", flower_amount=4))
            else:
                w.setze(x, 1, z, w.b(f.ein(f.blumen)))


# ============================================================================ Teile

def korb(w, f, cx, cz, y0, R, H):
    """Strohkorb-Kuppel aus gestapelten Ringen (hohl). Gibt die oberste Höhe zurück."""
    for y in range(0, H + 1):
        t = y / H
        r = R * (1 - t ** 2.2) ** 0.55
        ring = f.band if y % 3 == 2 else f.stroh[y % len(f.stroh)]
        for x, z in scheibe(r + 0.4, cx, cz):
            d = math.hypot(x - cx, z - cz)
            if d > r - 1.2 or y == H or r < 1.5:
                w.setze(x, y0 + y, z, ring)
    return y0 + H


def stockhaus(w, f, cx, cz, u, gross=1.0):
    """Wohnhaus in Bienenkorbform mit Tür, Rundfenstern, Blumenkästen, Flugbrett und Wabenknauf."""
    R, H = (4 * u + 1.5) * gross, _r((6 * u + 2) * gross, 4)
    top = korb(w, f, cx, cz, 1, R, H)
    for x, z in scheibe(R, cx, cz):
        w.setze(x, 0, z, w.b(f"{f.holz}_planks"))
    zt = cz + int(R * 0.98)
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(cx, y, zt, w.b(f"{f.holz}_door", facing="south", half=half, hinge="left", open=False, powered=False))
    w.setze(cx, 3, zt, f.wabe)
    for dx in (-1, 1):
        w.setze(cx + dx, 3, zt + 1, platte(w, f.holz, "top"))
    for a in (0.0, math.pi * 0.5, math.pi, math.pi * 1.5):
        if abs(a - math.pi / 2) < 0.1:
            continue
        rr = R * 0.92
        x, z = round(cx + math.cos(a) * rr), round(cz + math.sin(a) * rr)
        w.setze(x, 3, z, f.glas)
        w.setze(x, 2, z + (1 if math.sin(a) > 0.5 else 0), w.b("flowering_azalea_leaves", persistent=True,
                                                                 distance=7, waterlogged=False), ueberschreiben=False)
    w.setze(cx, top + 1, cz, f.wabe)
    w.setze(cx, top + 2, cz, f.honig)
    w.setze(cx + _r(R * 0.6), 4, cz - _r(R * 0.6), w.b("bee_nest", facing="south", honey_level=5), ueberschreiben=True)
    w.setze(cx - 2, 1, zt + 1, w.b("lantern", hanging=False, waterlogged=False))
    return top


def wabenturm(w, f, cx, cz, u):
    """Sechseckiger Turm aus Waben mit Fensterwaben, Balkonen, Honigtropfen und spitzem Wabendach."""
    R = 3.2 * u + 1.6
    H = _r(16 * u + 6, 10)
    etage = _r(4 * u + 1, 4)
    n = int(R) + 3
    for y in range(0, H):
        for x in range(cx - n, cx + n + 1):
            for z in range(cz - n, cz + n + 1):
                d = hexd(x - cx, z - cz)
                if d > R + 0.3:
                    continue
                if d > R - 1.0:
                    fenster = y % etage in (2, 3) and ((x - cx) % 3 == 0 or (z - cz) == 0) and y > 1
                    blk = f.glas if fenster else (f.honig if (x + 2 * y + z) % 7 == 0 else f.wabe)
                    w.setze(x, y, z, blk)
                elif y % etage == 0:
                    w.setze(x, y, z, w.b(f"{f.holz}_planks"))
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(cx, y, cz + int(R), w.b(f"{f.holz}_door", facing="south", half=half, hinge="left", open=False,
                                       powered=False))
    # Balkone
    for k, yb in enumerate(range(etage * 2, H - 2, etage * 2)):
        ring = []
        for x in range(cx - n - 2, cx + n + 3):
            for z in range(cz - n - 2, cz + n + 3):
                d = hexd(x - cx, z - cz)
                if R < d <= R + 2:
                    w.setze(x, yb, z, platte(w, f.holz))
                    if d > R + 1:
                        ring.append((x, yb + 1, z))
                        if w.rng.random() < 0.18:
                            for k2 in range(1, _r(2 * u, 1) + 1):
                                w.setze(x, yb - k2, z, f.honig)
        verbinde(w, ring, f"{f.holz}_fence")
    # Wabendach
    hd = _r(5 * u + 2, 3)
    for k in range(hd + 1):
        rr = (R + 1) * (1 - k / (hd + 1))
        for x in range(cx - n - 1, cx + n + 2):
            for z in range(cz - n - 1, cz + n + 2):
                if hexd(x - cx, z - cz) <= rr:
                    w.setze(x, H + k, z, f.honig if k % 2 else f.wabe)
    w.setze(cx, H + hd + 1, cz, f.gold)
    w.setze(cx, H + hd + 2, cz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return H + hd


def biene(w, f, cx, cy, cz, u, drehung=0.0, schwebend=False):
    """Bienen-Skulptur: pelziger Brustkorb, gestreifter Hinterleib, Facettenaugen, Fühler, sechs Beine,
    gläserne Flügel und Stachel."""
    S = Skulptur(w, u)
    gelb = [w.b("yellow_wool"), w.b("yellow_concrete"), w.b("orange_wool")]
    S.mat("streifen", lambda x, y, z, lx, ly, lz: w.b("black_wool") if int((lx + 20) / 1.1) % 2 == 0
          else gelb[(x + y + z) % len(gelb)])
    S.mat("schwarz", w.b("black_concrete"))
    S.mat("pelz", lambda x, y, z, *_: gelb[(x * 3 + y + z) % 3] if (x + z) % 4 else w.b("brown_wool"))
    S.mat("fluegel", lambda x, y, z, lx, ly, lz: w.b("white_stained_glass") if (abs(lz) > 1.5 or lx < -0.5)
          else w.b("light_blue_stained_glass"))
    S.mat("auge", w.b("black_concrete"))
    S.mat("glanz", w.b("white_concrete"))
    S.plus(ell(0, 0, 0, 1.9, 1.7, 1.7), "pelz")                                 # Brustkorb
    S.plus(ell(-3.6, -0.4, 0, 3.1, 2.2, 2.2), "streifen")                       # Hinterleib
    S.plus(kap((-6.0, -1.0, 0), (-7.0, -1.3, 0), 0.4, 0.12), "schwarz")         # Stachel
    S.plus(ell(2.3, 0.3, 0, 1.3, 1.3, 1.4), "schwarz")                          # Kopf
    S.plus(spiegel_z(ell(2.7, 0.6, 0.9, 0.8, 0.9, 0.55)), "auge")
    S.plus(spiegel_z(ell(3.1, 1.0, 0.95, 0.2, 0.2, 0.2)), "glanz")
    S.plus(spiegel_z(kap((3.0, 1.2, 0.45), (3.9, 2.9, 0.9), 0.22)), "schwarz")  # Fühler
    S.plus(spiegel_z(kap((3.9, 2.9, 0.9), (4.6, 2.7, 1.0), 0.22)), "schwarz")
    for bx in (-0.9, 0.0, 0.9):                                                 # Beine
        S.plus(spiegel_z(kap((bx, -0.8, 1.0), (bx + 0.3, -1.9, 2.0), 0.24)), "schwarz")
        S.plus(spiegel_z(kap((bx + 0.3, -1.9, 2.0), (bx - 0.2, -2.9, 2.2), 0.2)), "schwarz")
    S.plus(spiegel_z(lambda X, Y, Z: (((X + 1.2) / 2.0) ** 2 + ((Z - 2.4) / 2.1) ** 2 <= 1)
                     & (np.abs(Y - 2.1 - 0.35 * (Z - 1.2)) <= S.dicke(0.25))), "fluegel")
    from skulptur import dreh_y
    S.rendern((-8, -4, -7), (6, 5, 7), versatz=(cx + 0.5, cy, cz + 0.5), dreh=dreh_y(drehung))


def spiegel_z(form):
    return lambda X, Y, Z: form(X, Y, Z) | form(X, Y, -Z)


def wabensockel(w, f, cx, cz, R, H):
    for y in range(H):
        for x in range(cx - int(R) - 1, cx + int(R) + 2):
            for z in range(cz - int(R) - 1, cz + int(R) + 2):
                d = hexd(x - cx, z - cz)
                if d <= R - (0 if y < H - 1 else 0.6):
                    w.setze(x, y, z, f.gold if (y == H - 1 and d > R - 1.6) else f.honig if y == 1 else f.wabe)


def bienenstatue(w, f, cx, cz, u):
    """Goldgefasster Wabensockel mit einer großen Bienen-Skulptur."""
    H = _r(2.5 * u + 1, 2)
    wabensockel(w, f, cx, cz, 4.5 * u + 1.5, H)
    biene(w, f, cx, H + 3.4 * u, cz, u, drehung=0.5)


def riesenblume(w, f, cx, cz, u, farbe=None, hoehe=1.0):
    """Riesenblume mit geschwungenem Stängel, Blättern, Blütenblattkranz und Pollenkorb."""
    S = Skulptur(w, u)
    S.mat("g", w.b("green_concrete"))
    S.mat("b", lambda x, y, z, *_: w.b("lime_concrete") if (x + z) % 3 == 0 else w.b("green_concrete"))
    farbe = farbe if farbe is not None else f.ein(f.bluete)
    S.mat("p", farbe)
    S.mat("m", lambda x, y, z, *_: f.wabe if (x + y + z) % 2 else w.b("yellow_concrete"))
    H = 12 * hoehe
    S.plus(kap((0, 0, 0), (0.8, H * 0.5, 0.3), 0.55, 0.5), "g")
    S.plus(kap((0.8, H * 0.5, 0.3), (0, H, 0), 0.5, 0.45), "g")
    for a, yb in ((0.4, H * 0.25), (3.3, H * 0.45)):
        S.plus(lambda X, Y, Z, a=a, yb=yb: (((X * math.cos(a) + Z * math.sin(a) - 2.2) / 2.4) ** 2
                                            + ((-X * math.sin(a) + Z * math.cos(a)) / 0.9) ** 2 <= 1)
               & (np.abs(Y - yb - 0.35 * (X * math.cos(a) + Z * math.sin(a))) <= 0.55), "b")
    for i in range(8):
        a = i * math.pi / 4
        S.plus(lambda X, Y, Z, a=a: (((X * math.cos(a) + Z * math.sin(a) - 2.6) / 2.2) ** 2
                                     + ((-X * math.sin(a) + Z * math.cos(a)) / 1.1) ** 2 <= 1)
               & (np.abs(Y - H - 0.25 * (X * math.cos(a) + Z * math.sin(a))) <= 0.6), "p")
    S.plus(ell(0, H + 0.4, 0, 1.6, 0.8, 1.6), "m")
    S.rendern((-6, 0, -6), (6, H + 3, 6), versatz=(cx + 0.5, 1, cz + 0.5), ueberschreiben=False)
    return 1 + (H + 1) * u


def honigbrunnen(w, f, cx, cz, u):
    """Sechseckiger Brunnen mit Honigbecken, gestuften Wabenschalen und einer kleinen Biene obenauf."""
    R = 4.5 * u + 2
    n = int(R) + 2
    for x in range(cx - n, cx + n + 1):
        for z in range(cz - n, cz + n + 1):
            d = hexd(x - cx, z - cz)
            if d <= R:
                w.setze(x, 0, z, f.wabe)
                if d > R - 1:
                    w.setze(x, 1, z, f.gold if (x + z) % 3 == 0 else f.wabe)
                else:
                    w.setze(x, 1, z, f.honig)
    y = 2
    for k, rr in enumerate((R * 0.45, R * 0.28)):
        for yy in range(y, y + _r(2 * u, 2)):
            w.setze(cx, yy, cz, f.wabe)
        y += _r(2 * u, 2)
        for x in range(cx - int(rr) - 1, cx + int(rr) + 2):
            for z in range(cz - int(rr) - 1, cz + int(rr) + 2):
                d = hexd(x - cx, z - cz)
                if d <= rr:
                    w.setze(x, y, z, f.honig if d < rr - 0.8 else f.wabe)
                    if rr - 0.8 <= d and w.rng.random() < 0.3:
                        w.setze(x, y - 1, z, f.honig, ueberschreiben=False)
        y += 1
    if u >= 1:
        biene(w, f, cx, y + 1.5 * u, cz, u * 0.45, drehung=1.2)
    else:
        w.setze(cx, y, cz, w.b("bee_nest", facing="south", honey_level=5))


def koeniginpalast(w, f, cx, cz, u):
    """Königinnen-Palast: zwei gestapelte Riesenkörbe mit Goldkrone, Galerie, Wimpeln und Nebenkörben."""
    R1, H1 = 8 * u + 3, _r(9 * u + 3, 5)
    top = korb(w, f, cx, cz, 1, R1, H1)
    for x, z in scheibe(R1, cx, cz):
        w.setze(x, 0, z, f.wabe)
    yg = int(H1 * 0.45) + 1
    rg = R1 * (1 - (yg / H1) ** 2.2) ** 0.55 + 1.5
    for x, z in kreisrand(rg, cx, cz):
        w.setze(x, yg, z, platte(w, f.holz))
    verbinde(w, [(x, yg + 1, z) for x, z in kreisrand(rg + 0.6, cx, cz)], f"{f.holz}_fence")
    R2, H2 = R1 * 0.5, _r(H1 * 0.65, 3)
    top2 = korb(w, f, cx, cz, top - 1, R2, H2)
    for i in range(7):
        a = i * 2 * math.pi / 7
        x, z = round(cx + math.cos(a) * 1.6 * u), round(cz + math.sin(a) * 1.6 * u)
        for k in range(_r(2 * u, 2)):
            w.setze(x, top2 + 1 + k, z, f.gold)
    w.setze(cx, top2 + 1, cz, f.licht)
    for y, half in ((1, "lower"), (2, "upper")):
        w.setze(cx, y, cz + int(R1 * 0.98), w.b(f"{f.holz}_door", facing="south", half=half, hinge="left",
                                                 open=False, powered=False))
    for i in range(6):
        a = i * math.pi / 3
        x, z = round(cx + math.cos(a) * R1 * 0.75), round(cz + math.sin(a) * R1 * 0.75)
        w.setze(x, yg + 2, z, f.glas)
        w.setze(x, yg + 3, z, f.glas)
    for s in (-1, 1):
        stockhaus(w, f, cx + s * round(R1 + 3 * u + 3), cz + round(R1 * 0.3), u * 0.55)
    for a in (0.3, 2.0, 3.8, 5.2):
        x, z = round(cx + math.cos(a) * (R1 + 1.5)), round(cz + math.sin(a) * (R1 + 1.5))
        for y in range(1, _r(5 * u, 3) + 1):
            w.setze(x, y, z, w.b(f"{f.holz}_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False))
        for k in range(_r(2 * u, 2)):
            w.setze(x + 1 + k, _r(5 * u, 3) - k // 2, z, f.gelb if k % 2 == 0 else f.dunkel)


def wabenmarkt(w, f, cx, cz, u):
    """Offene Markthalle auf Wabensäulen mit Strohdach, Ständen, Fässern, Honigtöpfen und Blumen."""
    bx, bz = _r(7 * u + 3, 5), _r(5 * u + 2, 4)
    H = _r(4 * u + 2, 4)
    for x in range(cx - bx, cx + bx + 1):
        for z in range(cz - bz, cz + bz + 1):
            w.setze(x, 0, z, f.wabe if (x + z) % 2 else w.b(f"{f.holz}_planks"))
    for x in range(cx - bx, cx + bx + 1, 3):
        for z in (cz - bz, cz + bz):
            for y in range(1, H + 1):
                w.setze(x, y, z, f.wabe if y % 2 else f.honig)
    for k in range(bz + 2):
        for x in range(cx - bx - 1, cx + bx + 2):
            for s in (-1, 1):
                w.setze(x, H + 1 + k, cz + s * (bz + 1 - k), f.stroh[k % len(f.stroh)] if k < bz + 1 else f.band)
    for x in range(cx - bx + 2, cx + bx - 1, 4):
        for dz in (-1, 1):
            w.setze(x, 1, cz + dz * (bz - 2), w.b("barrel", facing="up", open=False))
            w.setze(x + 1, 1, cz + dz * (bz - 2), f.honig)
            w.setze(x + 1, 2, cz + dz * (bz - 2), w.b("flower_pot"))
        w.setze(x, H, cz, w.b("lantern", hanging=True, waterlogged=False))


def bienenblume(w, f, cx, cz, u):
    """Biene, die auf einer Riesenblume landet."""
    top = riesenblume(w, f, cx, cz, u, hoehe=1.0)
    biene(w, f, cx, top + 2.2 * u, cz, u * 0.7, drehung=2.2)


# ============================================================================ Vorlagen

def _einzel(fn, radius, streu=True):
    def vorlage(seed, g=1):
        w = _welt(seed)
        f = Bienen(w, seed)
        u = U[g]
        _boden(w, f, radius * u + 3)
        fn(w, f, u)
        if streu:
            _streu(w, f, radius * u + 3)
        return w
    return vorlage


def bienenstadt(seed, g=2):
    """Ganze Bienenstadt: Königinnen-Palast, Wabentürme, Stockhäuser, Markt, Honigbrunnen, Riesenblumen,
    Bienenstatuen und Wege aus Waben."""
    w = _welt(seed)
    f = Bienen(w, seed)
    u = U[g] * 0.7
    R = 34 * u + 10
    _boden(w, f, R)
    koeniginpalast(w, f, 0, round(-R * 0.35), u)
    honigbrunnen(w, f, 0, round(R * 0.12), u * 0.8)
    wabenturm(w, f, round(-R * 0.6), round(-R * 0.05), u * 0.8)
    wabenturm(w, f, round(R * 0.6), round(-R * 0.15), u * 0.7)
    wabenmarkt(w, f, round(R * 0.4), round(R * 0.45), u * 0.7)
    for fx, fz, gg in ((-0.55, 0.45, 0.7), (-0.25, 0.7, 0.6), (0.75, 0.25, 0.55), (-0.8, -0.5, 0.55)):
        stockhaus(w, f, round(fx * R), round(fz * R), u * gg)
    for fx, fz in ((0.25, -0.05), (-0.3, 0.25), (0.65, -0.6), (-0.1, 0.85)):
        riesenblume(w, f, round(fx * R), round(fz * R), u * 0.8, hoehe=0.8 + 0.4 * w.rng.random())
    bienenstatue(w, f, round(-R * 0.15), round(R * 0.45), u * 0.7)
    for i in range(int(R * 4)):
        t = i / (R * 4)
        x, z = round(math.sin(t * 6.3) * R * 0.25), round(-R * 0.1 + t * R * 0.9)
        if w.hole(x, 0, z) in f.boden:
            w.setze(x, 0, z, f.wabe)
    _streu(w, f, R, 0.1)
    return w


BIENENSTADT = {
    "bienenstadt": ("Bienenstadt (komplett)", bienenstadt),
    "stockhaus": ("Stockhaus", _einzel(lambda w, f, u: stockhaus(w, f, 0, 0, u), 6)),
    "wabenturm": ("Wabenturm", _einzel(lambda w, f, u: wabenturm(w, f, 0, 0, u), 7)),
    "koeniginpalast": ("Königinnen-Palast", _einzel(lambda w, f, u: koeniginpalast(w, f, 0, 0, u), 18)),
    "honigbrunnen": ("Honigbrunnen", _einzel(lambda w, f, u: honigbrunnen(w, f, 0, 0, u), 7)),
    "wabenmarkt": ("Wabenmarkt", _einzel(lambda w, f, u: wabenmarkt(w, f, 0, 0, u), 10)),
    "bienenstatue": ("Bienenstatue", _einzel(lambda w, f, u: bienenstatue(w, f, 0, 0, u), 7)),
    "bienenblume": ("Biene auf Riesenblume", _einzel(lambda w, f, u: bienenblume(w, f, 0, 0, u), 7)),
    "riesenblume": ("Riesenblume", _einzel(lambda w, f, u: riesenblume(w, f, 0, 0, u), 6)),
}

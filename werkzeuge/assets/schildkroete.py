"""Schildkröten-Insel: eine riesige Meeresschildkröte, auf deren Panzer eine Insel wächst.

Variante "natur": Felsklippen, Terrassen, Wasserfall, Palmen, Kirschbäume.
Variante "dorf":  zusätzlich Fachwerkhäuser, Leuchtturm, Bootssteg, Boot und Laternen.

y = 0 ist die Wasseroberfläche (Anker): die Vorlage auf die oberste Wasserschicht des Meeres setzen.
Der Kopf zeigt nach +x (Osten).
"""

from __future__ import annotations

import math

import numpy as np

from baeume import kirschbaum
from gebaeude import Holzstil, boot, haus, leuchtturm, palme, steg
from lib import Rauschen, Verlauf, Welt, einfuegen, laub


class Farben:
    def __init__(self, w: Welt):
        b = w.b
        # Panzer: dunkle Fugen, Ring, helle Mitte
        self.fuge = b("dark_prismarine")
        self.ring = b("prismarine")
        self.mitte = b("waxed_oxidized_copper")
        self.mitte_hell = b("waxed_weathered_copper")
        self.moos = b("moss_block")
        self.randplatte = b("prismarine_bricks")
        self.lippe = b("smooth_sandstone")
        self.lippe_dunkel = b("sandstone")
        self.innen = b("dark_prismarine")
        # Haut
        self.haut = b("waxed_oxidized_copper")
        self.haut_fleck = b("waxed_weathered_copper")
        self.haut_dunkel = b("prismarine")
        self.bauch = b("smooth_sandstone")
        self.bauch_rand = b("sandstone")
        self.auge = b("black_concrete")
        self.glanz = b("white_concrete")
        self.maul = b("black_terracotta")
        # Abgestimmte Verläufe (dunkel -> hell)
        self.v_panzer = Verlauf(w, "Panzer", ["dark_prismarine", "prismarine", "waxed_oxidized_copper",
                                              "waxed_oxidized_cut_copper", "waxed_weathered_copper"])
        self.v_rand = Verlauf(w, "Panzerrand", ["dark_prismarine", "prismarine_bricks", "prismarine"])
        self.v_haut = Verlauf(w, "Haut", ["dark_prismarine", "prismarine", "waxed_oxidized_copper",
                                          "waxed_weathered_copper"])
        self.v_bauch = Verlauf(w, "Bauch & Lippe", ["sandstone", "cut_sandstone", "smooth_sandstone", "end_stone"])
        self.v_fels = Verlauf(w, "Klippen", ["mossy_cobblestone", "tuff", "andesite", "stone", "calcite"])
        self.verlaeufe = [self.v_panzer, self.v_rand, self.v_haut, self.v_bauch, self.v_fels]


def _schuppen(x, y, z):
    """Regelmäßiges Fleckenmuster für die Haut."""
    return (x + y) % 3 == 0 and (z + y) % 3 == 0


def schildkroete(seed, groesse=1, dorf=False):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    f = Farben(w)
    rs = Rauschen(w, 5)
    L = [40, 60][groesse]
    a, b, c = L / 2, 0.38 * L, 0.27 * L

    # ================================================================ Panzer
    # Platten (Voronoi): Wirbelplatten in der Mitte, Rippenplatten seitlich
    zentren = [(u * a, 0.0) for u in (-0.66, -0.34, -0.02, 0.3, 0.6)]
    for s in (-1, 1):
        zentren += [(u * a, s * 0.52 * b) for u in (-0.52, -0.17, 0.18, 0.5)]
    zentren = np.array(zentren)
    oben_y = {}
    n_rand = int(2 * math.pi * (a + b) / 2 / 3.6)
    for x in range(int(-a) - 1, int(a) + 2):
        for z in range(int(-b) - 1, int(b) + 2):
            q = (x / a) ** 2 + (z / b) ** 2
            if q >= 1:
                continue
            top = int(round(c * (1 - q) ** 0.5))
            unten = int(-c * 0.4 * (1 - q) ** 0.5) - 1
            oben_y[(x, z)] = top
            if q > 0.8:
                # Randplatten: radial unterteilt, unten eine helle Lippe
                ang = math.atan2(z / b, x / a)
                seg = (ang / (2 * math.pi) * n_rand) % 1
                naht = seg < 0.16 or q < 0.815
                for y in range(unten, top + 1):
                    if y <= 0 and q > 0.9:
                        blk = f.v_bauch(1.2 + y * 0.8, x, y, z)
                    elif naht:
                        blk = f.fuge
                    else:
                        blk = f.v_rand(1.0 + min(1.0, (y + 1) / 4), x, y, z)
                    w.setze(x, y, z, blk)
                continue
            dd = np.hypot(zentren[:, 0] - x, (zentren[:, 1] - z) * 1.1)
            o = np.argsort(dd)[:2]
            abstand = dd[o[1]] - dd[o[0]]
            moos = abstand >= 1.5 and rs(x * 0.7, 3, z * 0.7) > 0.8
            for y in range(unten, top + 1):
                if y < top - 1:
                    blk = f.innen
                elif abstand < 1.5:
                    blk = f.fuge
                elif moos:
                    blk = f.moos
                else:
                    # Platte: am Rand dunkler, zur Mitte und nach oben heller
                    wert = 1.0 + 2.2 * min(1.0, (abstand - 1.5) / 5.0) + 0.9 * max(0, top) / c
                    blk = f.v_panzer(wert, x, y, z)
                w.setze(x, y, z, blk)

    # ================================================================ Insel auf dem hinteren Panzer
    stein = [w.b("stone"), w.b("andesite"), w.b("cobblestone"), w.b("mossy_cobblestone"), w.b("stone")]
    gras, erde = w.b("grass_block", snowy=False), w.b("dirt")
    xi, zi = -0.28 * a, -0.05 * b
    ri_x, ri_z = 0.62 * a, 0.62 * b
    hx, hz = -0.42 * a, -0.25 * b          # Gipfel hinten links
    Hh = [13, 20][groesse]
    insel = {}
    for (x, z), top in oben_y.items():
        e = ((x - xi) / ri_x) ** 2 + ((z - zi) / ri_z) ** 2
        if e > 1 + 0.25 * (rs(x, 0, z) - 0.5):
            continue
        d = math.hypot((x - hx) / (ri_x * 1.15), (z - hz) / (ri_z * 1.1))
        roh = Hh * max(0.0, 1 - d) ** 0.9 * (0.85 + 0.3 * rs(x, 20, z))
        stufe = int(roh / 4) * 4 if roh > 2 else 0
        y_ob = top + 1 + stufe + (1 if e < 0.6 else 0)
        insel[(x, z)] = y_ob
        for y in range(top + 1, y_ob + 1):
            if y == y_ob:
                blk = gras
            elif y >= y_ob - 1 and stufe == 0:
                blk = erde
            else:
                anteil = (y - top) / max(1, y_ob - top)
                blk = f.v_fels(0.4 + 3.2 * anteil + (rs(x * 2, y * 2, z * 2) - 0.5), x, y, z)
            w.setze(x, y, z, blk)

    # Wasserfall: Rinne vom Gipfel nach Süden, über die Klippen und den Panzer ins Meer
    wasser = w.b("water", level=0)
    w.vorschau_extra = {}
    wx = int(hx + 3)
    vorher = None
    for z in range(int(hz) - 1, int(b) + 2):
        ende = None
        for dx in (0, 1, 2):
            x = wx + dx
            if (x, z) in insel:
                y = insel[(x, z)]
                w.setze(x, y, z, wasser)
                w.setze(x, y - 1, z, stein[0])
                if vorher is not None and vorher > y:
                    for yy in range(y + 1, vorher + 1):
                        w.vorschau_extra[(x, yy, z)] = wasser
                ende = y
            elif (x, z) in oben_y:
                y = oben_y[(x, z)]
                for yy in range(y + 1, (vorher or y) + 1):
                    w.vorschau_extra[(x, yy, z)] = wasser
                ende = y
            else:
                for yy in range(0, (vorher or 1) + 1):
                    w.vorschau_extra[(x, yy, z)] = wasser
        if ende is None:
            break
        vorher = ende
    # Uferkanten neben der Rinne
    for (x, z), y in insel.items():
        if x in (wx - 1, wx + 3) and w.hole(x, y, z) == gras and w.hole(wx if x < wx else wx + 2, y, z) == wasser:
            w.setze(x, y + 1, z, stein[3] if w.rng.random() < 0.5 else stein[1])

    # Ranken an den Klippen
    for (x, z), y in insel.items():
        for dx, dz, s in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
            nx, nz = x + dx, z + dz
            nachbar = insel.get((nx, nz), oben_y.get((nx, nz), -9))
            if nachbar < y - 1 and w.rng.random() < 0.35:
                ranke = w.b("vine", **{k: (k == s) for k in ("north", "east", "south", "west")}, up=False)
                for k in range(int(1 + w.rng.random() * (y - nachbar))):
                    if not w.frei(nx, y - k, nz):
                        break
                    w.setze(nx, y - k, nz, ranke)

    # ================================================================ Dorf
    belegt = set()
    if dorf:
        stile = [Holzstil(w, rahmen="spruce", wand="smooth_sandstone", dach="spruce"),
                 Holzstil(w, rahmen="dark_oak", wand="birch_planks", dach="dark_oak")]
        plaetze = [(-0.05 * a, 0.18 * b, 7, 6, 0, "south"), (-0.55 * a, 0.3 * b, 7, 6, 1, "south")]
        if groesse:
            plaetze.append((-0.1 * a, -0.38 * b, 7, 6, 1, "east"))
        for (px, pz, B, T, st, tuer) in plaetze:
            x0, z0 = int(px - B / 2), int(pz - T / 2)
            fuss = [insel.get((x, z), oben_y.get((x, z), 0)) for x in range(x0, x0 + B) for z in range(z0, z0 + T)]
            haus(w, x0, max(fuss), z0, B=B, T=T, stockwerke=1, stil=stile[st], fundament=14, tuer=tuer)
            belegt |= {(x, z) for x in range(x0 - 2, x0 + B + 2) for z in range(z0 - 2, z0 + T + 2)}
        lx, lz = int(hx), int(hz)
        leuchtturm(w, lx, insel.get((lx, lz), 10) + 1, lz, H=[10, 15][groesse], R=2)
        belegt |= {(x, z) for x in range(lx - 5, lx + 6) for z in range(lz - 5, lz + 6)}
        sx = int(-0.12 * a)
        sz = int(b * math.sqrt(max(0, 1 - (sx / a) ** 2))) - 1
        steg(w, sx, 1, sz, laenge=[9, 13][groesse], richtung="south", tiefe=7)
        boot(w, sx + 12, 0, sz + [7, 9][groesse], "east")

    # ================================================================ Bäume und Bewuchs
    flaechen = sorted(insel.items(), key=lambda kv: w.rng.random())
    palmen = kirschen = 0
    for (x, z), y in flaechen:
        if (x, z) in belegt or w.hole(x, y, z) != gras or not all(w.frei(x, y + k, z) for k in range(1, 9)):
            continue
        e = ((x - xi) / ri_x) ** 2 + ((z - zi) / ri_z) ** 2
        if e > 0.45 and palmen < [5, 9][groesse]:
            palme(w, x, y, z, hoehe=6 + int(w.rng.random() * [4, 6][groesse]),
                  neigung=math.atan2(z - zi, x - xi) + (w.rng.random() - 0.5) * 0.7)
            palmen += 1
            belegt |= {(x + i, z + j) for i in range(-3, 4) for j in range(-3, 4)}
        elif e < 0.5 and kirschen < [2, 3][groesse]:
            einfuegen(w, kirschbaum(seed + kirschen, 0), x, y, z)
            kirschen += 1
            belegt |= {(x + i, z + j) for i in range(-5, 6) for j in range(-5, 6)}
    busch = [laub(w, "azalea"), laub(w, "flowering_azalea")]
    blumen = [w.b(n) for n in ("poppy", "dandelion", "azure_bluet", "oxeye_daisy", "cornflower", "allium")]
    for (x, z), y in insel.items():
        if w.hole(x, y, z) != gras or not w.frei(x, y + 1, z):
            continue
        u = w.rng.random()
        if u < 0.05:
            w.setze(x, y + 1, z, busch[int(w.rng.random() * 2)])
        elif u < 0.2:
            w.setze(x, y + 1, z, w.b("grass"))
        elif u < 0.3:
            w.setze(x, y + 1, z, blumen[int(w.rng.random() * len(blumen))])

    # ================================================================ Kopf
    def haut_farbe(lippe, cy=None, ry=None):
        def fn(x, y, z):
            ny = 0.0 if cy is None else max(-1.0, min(1.0, (y + 0.5 - cy) / ry))
            if y < lippe:
                return f.v_bauch(1.0 + 2.0 * (ny + 1) / 2, x, y, z)
            if y == lippe:
                return f.v_bauch(0.3, x, y, z)
            wert = 1.2 + 1.5 * (ny + 1) / 2 + (0.9 if _schuppen(x, y, z) else 0.0)
            return f.v_haut(wert, x, y, z)
        return fn

    def ellipsoid(c0, r, farbe):
        cx, cy, cz = c0
        rx, ry, rz = r
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
                for z in range(int(cz - rz) - 1, int(cz + rz) + 2):
                    if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 + ((z + 0.5 - cz) / rz) ** 2 <= 1:
                        w.setze(x, y, z, farbe(x, y, z))

    kx, ky = a + 0.15 * L, 0.13 * L
    lippe_y = int(ky - 0.035 * L)
    for i in range(12):  # Hals
        t = i / 11
        px = a * 0.78 + (kx - a * 0.78) * t
        py = 0.4 + (ky - 0.4) * t * 0.8
        ellipsoid((px, py, 0), (0.06 * L, 0.085 * L, 0.095 * L), haut_farbe(int(py - 0.03 * L), py, 0.085 * L))
    ellipsoid((kx, ky, 0), (0.14 * L, 0.115 * L, 0.125 * L), haut_farbe(lippe_y, ky, 0.115 * L))
    ellipsoid((kx + 0.1 * L, ky - 0.025 * L, 0), (0.085 * L, 0.075 * L, 0.095 * L),
              haut_farbe(lippe_y, ky - 0.025 * L, 0.075 * L))
    # Lächeln entlang der Lippenlinie vorne
    for (x, y, z), blk in list(w.bloecke.items()):
        if y == lippe_y and x > kx - 0.02 * L and blk == f.bauch_rand:
            if any(w.frei(x + dx, y, z + dz) for dx, dz in ((1, 0), (0, 1), (0, -1))):
                w.setze(x, y, z, f.maul)
    # Nasenlöcher
    nxs = [x for (x, y, z) in w.bloecke if y == int(ky) and abs(z) <= 1]
    if nxs:
        for z in (-1, 1):
            w.setze(max(nxs), int(ky) - 1, z, f.maul)
    # Augen mit Glanzpunkt und Braue
    ex0, ey0 = int(kx + 0.03 * L), int(ky + 0.02 * L)
    ga = [2, 3][groesse]
    breite = int(0.2 * L) + 2

    def aussen_z(x, y, s):
        zs = [z for z in range(-breite, breite + 1) if (x, y, z) in w.bloecke]
        return (max(zs) if s > 0 else min(zs)) if zs else None

    for s in (1, -1):
        for dx in range(ga):
            for dy in range(ga):
                z = aussen_z(ex0 + dx, ey0 + dy, s)
                if z is not None:
                    w.setze(ex0 + dx, ey0 + dy, z, f.glanz if (dx == ga - 1 and dy == ga - 1) else f.auge)
        for dx in range(-1, ga + 1):
            z = aussen_z(ex0 + dx, ey0 + ga, s)
            if z is not None:
                w.setze(ex0 + dx, ey0 + ga, z, f.haut_dunkel)

    # ================================================================ Flossen
    def flosse(basis, richtung, laenge, breite_f, dicke, schwung):
        d = np.array(richtung, dtype=float)
        d /= np.linalg.norm(d)
        quer = np.cross([0, 1, 0], d)
        quer /= np.linalg.norm(quer)
        zurueck = np.array([-1.0, 0, 0])
        schritte = int(laenge / 0.4)
        for i in range(schritte + 1):
            t = i / schritte
            mitte = np.array(basis, dtype=float) + d * laenge * t + zurueck * schwung * laenge * t * t
            mitte[1] = basis[1] - 1.6 * t * t
            br = max(0.8, breite_f * (0.45 + 2.4 * t * (1 - t)) * (1 - t ** 3))
            for qv in np.arange(-br, br + 0.01, 0.4):
                rel = abs(qv) / br
                di = max(1, round(dicke * (1 - rel ** 2)))
                p = mitte + quer * qv
                x, z = math.floor(p[0]), math.floor(p[2])
                y0 = math.floor(p[1])
                hinten = (quer * qv)[0] < 0
                for k in range(di):
                    if k == 0:
                        if rel > 0.8 and hinten:
                            blk = f.v_bauch(2.5, x, y0, z)
                        else:
                            wert = 1.3 + 1.2 * (1 - rel) + (0.9 if _schuppen(x, 0, z) and rel < 0.75 else 0)
                            blk = f.v_haut(wert, x, y0, z)
                    else:
                        blk = f.v_bauch(0.8, x, y0 - k, z)
                    w.setze(x, y0 - k, z, blk)

    for s in (1, -1):
        flosse((0.4 * a, 1.0, s * 0.72 * b), (0.35, 0, s * 1.0), 0.5 * L, 0.075 * L, [2, 3][groesse], 0.35)
        flosse((-0.62 * a, 0.5, s * 0.62 * b), (-0.55, 0, s * 0.8), 0.24 * L, 0.06 * L, 2, 0.1)
    ellipsoid((-a - 0.03 * L, 0, 0), (0.08 * L, 0.035 * L + 0.6, 0.04 * L), haut_farbe(0, 0, 0.035 * L + 0.6))
    w.paletten = f.verlaeufe
    return w


SCHILDKROETE = {
    "schildkroeten_insel": ("Schildkröten-Insel (Natur)", lambda s, g: schildkroete(s, g, False)),
    "schildkroeten_dorf": ("Schildkröten-Insel (Dorf)", lambda s, g: schildkroete(s, g, True)),
}

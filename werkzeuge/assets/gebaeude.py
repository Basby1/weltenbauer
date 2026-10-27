"""Gebäude-Bausteine: Palme, Fachwerkhaus, Leuchtturm, Bootssteg, Boot.

Alle Bausteine zeichnen in eine bestehende Welt (mit Versatz), damit sie sich zu größeren
Szenen (z. B. der Schildkröten-Insel) kombinieren lassen. Unten stehen Einzel-Vorlagen.
Koordinaten: +x = Osten, +z = Süden, y nach oben.
"""

from __future__ import annotations

import math

import numpy as np

from lib import Welt, laub

GEGEN = {"north": "south", "south": "north", "east": "west", "west": "east"}
VEKTOR = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}


# --------------------------------------------------------------------------- Palme

def palme(w: Welt, x0, y0, z0, hoehe=9, neigung=None):
    """Palme mit gebogenem Stamm und hängenden Wedeln. (x0, y0, z0) = Block unter dem Stamm."""
    stamm = {a: w.b("jungle_log", axis=a) for a in "xyz"}
    blatt = laub(w, "jungle")
    az = w.rng.random() * 2 * math.pi if neigung is None else neigung
    dx, dz = math.cos(az), math.sin(az)
    x, z = x0 + 0.5, z0 + 0.5
    top = None
    for i in range(1, hoehe + 1):
        t = i / hoehe
        versatz = 2.6 * t * t
        px, pz = x + dx * versatz, z + dz * versatz
        bx, bz = math.floor(px), math.floor(pz)
        if top is not None and (bx, bz) != (top[0], top[2]):
            w.setze(bx, y0 + i - 1, bz, stamm["y"], ueberschreiben=False)  # Verbindung ohne Eckkontakt
        w.setze(bx, y0 + i, bz, stamm["y"])
        top = (bx, y0 + i, bz)
    tx, ty, tz = top
    w.setze(tx, ty + 1, tz, blatt)
    n = 7 + int(w.rng.random() * 2)
    for k in range(n):
        a = k * 2 * math.pi / n + w.rng.random() * 0.4
        laenge = 4 + int(w.rng.random() * 2)
        for s in range(1, laenge + 1):
            fx = tx + round(math.cos(a) * s)
            fz = tz + round(math.sin(a) * s)
            fy = ty + 1 + (1 if s <= 2 else 0) - max(0, s - 3)
            w.setze(fx, fy, fz, blatt, ueberschreiben=False)
            if s == laenge:
                w.setze(fx, fy - 1, fz, blatt, ueberschreiben=False)
    # Kokosnüsse
    for ddx, ddz, f in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
        if w.rng.random() < 0.5:
            w.setze(tx + ddx, ty - 1, tz + ddz, w.b("cocoa", age=2, facing=f), ueberschreiben=False)


# --------------------------------------------------------------------------- Haus

class Holzstil:
    def __init__(self, w: Welt, rahmen="spruce", wand="smooth_sandstone", dach="spruce", sockel="cobblestone"):
        self.w = w
        self.rahmen = rahmen
        self.log = {a: w.b(f"{rahmen}_log", axis=a) for a in "xyz"}
        self.balken = {a: w.b(f"stripped_{rahmen}_log", axis=a) for a in "xyz"}
        self.wand = w.b(wand)
        self.planke = w.b(f"{rahmen}_planks")
        self.dach = dach
        self.sockel = [w.b(sockel), w.b("mossy_cobblestone"), w.b("stone_bricks")]

    def dachtreppe(self, facing, half="bottom"):
        return self.w.b(f"{self.dach}_stairs", facing=facing, half=half, shape="straight", waterlogged=False)

    def dachstufe(self, typ="bottom"):
        return self.w.b(f"{self.dach}_slab", type=typ, waterlogged=False)


def scheibe(w: Welt, achse_x: bool):
    return w.b("glass_pane", east=achse_x, west=achse_x, north=not achse_x, south=not achse_x, waterlogged=False)


def zaun(w: Welt, holz, verbindungen=()):
    return w.b(f"{holz}_fence", **{k: (k in verbindungen) for k in ("north", "south", "east", "west")},
               waterlogged=False)


def haus(w: Welt, x0, y0, z0, B=7, T=6, stockwerke=1, stil: Holzstil | None = None, fundament=6, tuer="south",
         schornstein=True):
    """Fachwerkhaus mit Satteldach (First entlang x). (x0, y0, z0) = nordwestliche Ecke des Bodens.
    Gibt die Grundfläche zurück."""
    s = stil or Holzstil(w)
    H = 4 * stockwerke
    x1, z1 = x0 + B - 1, z0 + T - 1
    # Fundament bis zum Untergrund
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            rand = x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1)
            for y in range(y0, y0 - fundament - 1, -1):
                if y < y0 and not w.frei(x, y, z):
                    break
                if rand and y == y0:
                    w.setze(x, y, z, s.sockel[int(w.rng.random() * 3)])
                elif not rand or y < y0:
                    w.setze(x, y, z, s.sockel[int(w.rng.random() * 3)] if y < y0 else s.planke)
    # Wände mit Fachwerk
    for y in range(y0 + 1, y0 + H + 1):
        lokal = (y - y0 - 1) % 4
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                wand = x in (x0, x1) or z in (z0, z1)
                if not wand:
                    w.setze(x, y, z, 0)
                    continue
                ecke = x in (x0, x1) and z in (z0, z1)
                if ecke:
                    w.setze(x, y, z, s.log["y"])
                elif lokal == 3:  # Deckenbalken
                    w.setze(x, y, z, s.balken["x" if z in (z0, z1) else "z"])
                else:
                    w.setze(x, y, z, s.wand)
    # Zwischendecken
    for st in range(1, stockwerke):
        for x in range(x0 + 1, x1):
            for z in range(z0 + 1, z1):
                w.setze(x, y0 + 4 * st, z, s.planke)
    # Fenster mit Fensterläden und Blumenkasten
    for st in range(stockwerke):
        yb = y0 + 2 + 4 * st
        for seite in ("south", "north", "east", "west"):
            if seite in ("south", "north"):
                z = z1 if seite == "south" else z0
                plaetze = [(x, z) for x in range(x0 + 2, x1 - 1, 3)]
            else:
                x = x1 if seite == "east" else x0
                plaetze = [(x, z) for z in range(z0 + 2, z1 - 1, 3)]
            vx, vz = VEKTOR[seite]
            for (fx, fz) in plaetze:
                if st == 0 and seite == tuer and (fx == x0 + B // 2 if seite in ("south", "north")
                                                  else fz == z0 + T // 2):
                    continue
                pane = scheibe(w, seite in ("south", "north"))
                w.setze(fx, yb, fz, pane)
                w.setze(fx, yb + 1, fz, pane)
                # Läden links/rechts
                for q in (-1, 1):
                    lx, lz = (fx + q, fz + vz) if seite in ("south", "north") else (fx + vx, fz + q)
                    if seite in ("east", "west"):
                        lx = fx + vx
                    else:
                        lz = fz + vz
                    w.setze(lx, yb, lz, w.b(f"{s.rahmen}_trapdoor", facing=seite, half="bottom", open=True,
                                             powered=False, waterlogged=False), ueberschreiben=False)
                    w.setze(lx, yb + 1, lz, w.b(f"{s.rahmen}_trapdoor", facing=seite, half="top", open=True,
                                                 powered=False, waterlogged=False), ueberschreiben=False)
                # Blumenkasten unter dem Fenster
                bx, bz = fx + vx, fz + vz
                w.setze(bx, yb - 1, bz, w.b(f"{s.rahmen}_trapdoor", facing=GEGEN[seite], half="top", open=False,
                                            powered=False, waterlogged=False), ueberschreiben=False)
                if w.frei(bx, yb, bz):
                    blume = ["potted_poppy", "potted_azure_bluet", "potted_red_tulip", "potted_cornflower",
                             "potted_allium"][int(w.rng.random() * 5)]
                    w.setze(bx, yb, bz, w.b(blume))
    # Tür
    vx, vz = VEKTOR[tuer]
    if tuer in ("south", "north"):
        tx, tz = x0 + B // 2, (z1 if tuer == "south" else z0)
    else:
        tx, tz = (x1 if tuer == "east" else x0), z0 + T // 2
    for half, dy in (("lower", 1), ("upper", 2)):
        w.setze(tx, y0 + dy, tz, w.b(f"{s.rahmen}_door", facing=tuer, half=half, hinge="left", open=False,
                                     powered=False))
    # Vordach-Laterne und Treppenstufe vor der Tür
    w.setze(tx + vx, y0, tz + vz, s.dachtreppe(GEGEN[tuer]), ueberschreiben=False)
    w.setze(tx + vx + (1 if tuer in ("south", "north") else 0), y0 + 3, tz + vz + (0 if tuer in ("south", "north") else 1),
            w.b("lantern", hanging=False, waterlogged=False), ueberschreiben=False)
    # Satteldach mit Überstand, First entlang x
    yd = y0 + H + 1
    k = 0
    while True:
        zs, zn = z0 - 1 + k, z1 + 1 - k
        y = yd + k
        if zs > zn:
            break
        for x in range(x0 - 1, x1 + 2):
            if zs == zn:
                w.setze(x, y, zs, s.dachstufe())
            else:
                w.setze(x, y, zs, s.dachtreppe("south"))
                w.setze(x, y, zn, s.dachtreppe("north"))
        # Giebelwände
        for z in range(zs + 1, zn):
            for x in (x0, x1):
                w.setze(x, y, z, s.balken["y"] if z == (z0 + z1) // 2 else s.wand)
            for x in range(x0 + 1, x1):
                w.setze(x, y, z, 0)
        k += 1
    first = yd + k - 1
    # hängende Laternen an den Giebelenden
    for x in (x0 - 1, x1 + 1):
        zm = (z0 + z1) // 2
        unter = first - 2
        if w.frei(x, unter, zm):
            w.setze(x, unter, zm, w.b("lantern", hanging=True, waterlogged=False))
    # Schornstein
    if schornstein:
        cx, cz = x1 - 1, z0 + 1
        for y in range(y0 + 1, first + 3):
            w.setze(cx, y, cz, w.b("cobblestone") if w.rng.random() < 0.7 else w.b("mossy_cobblestone"))
        w.setze(cx, first + 3, cz, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    # Licht innen
    w.setze(x0 + 1, y0 + 1, z0 + 1, w.b("lantern", hanging=False, waterlogged=False), ueberschreiben=False)
    return first


# --------------------------------------------------------------------------- Leuchtturm

def leuchtturm(w: Welt, cx, y0, cz, H=18, R=3):
    """Runder Leuchtturm mit Galerie, Laternenraum und spitzem Dach. (cx, y0, cz) = Mitte des Bodens."""
    weiss = [w.b("calcite"), w.b("smooth_quartz"), w.b("white_terracotta")]
    rot = w.b("red_terracotta")
    sockel = [w.b("stone_bricks"), w.b("mossy_stone_bricks"), w.b("cobblestone")]
    leiter = {f: w.b("ladder", facing=f, waterlogged=False) for f in ("north", "south", "east", "west")}
    for y in range(y0 - 4, y0 + H + 1):
        r = R + (1 if y <= y0 + 1 else 0)
        for x in range(cx - r - 1, cx + r + 2):
            for z in range(cz - r - 1, cz + r + 2):
                d = math.hypot(x - cx, z - cz)
                if d > r + 0.4:
                    continue
                aussen = d > r - 0.8
                if y < y0:
                    if w.frei(x, y, z):
                        w.setze(x, y, z, sockel[int(w.rng.random() * 3)])
                    continue
                if not aussen:
                    w.setze(x, y, z, 0)
                    continue
                if y <= y0 + 1:
                    w.setze(x, y, z, sockel[int(w.rng.random() * 3)])
                elif (y - y0) % 7 in (5, 6) and H - (y - y0) > 3:
                    w.setze(x, y, z, rot)
                else:
                    w.setze(x, y, z, weiss[0] if w.rng.random() < 0.8 else weiss[1])
    # Fensterschlitze und Leiter innen
    for y in range(y0 + 4, y0 + H - 2, 4):
        ang = (y - y0) * 0.9
        fx, fz = cx + round(math.cos(ang) * R), cz + round(math.sin(ang) * R)
        w.setze(fx, y, fz, w.b("glass"))
    for y in range(y0 + 1, y0 + H + 1):
        w.setze(cx, y, cz - R + 1, leiter["south"])
    w.setze(cx, y0 + 1, cz + R, 0)
    w.setze(cx, y0 + 2, cz + R, 0)
    w.setze(cx, y0 + 1, cz + R, w.b("spruce_door", facing="south", half="lower", hinge="left", open=False, powered=False))
    w.setze(cx, y0 + 2, cz + R, w.b("spruce_door", facing="south", half="upper", hinge="left", open=False, powered=False))
    # Galerie
    yg = y0 + H + 1
    for x in range(cx - R - 2, cx + R + 3):
        for z in range(cz - R - 2, cz + R + 3):
            d = math.hypot(x - cx, z - cz)
            if d <= R + 1.6:
                w.setze(x, yg, z, w.b("spruce_planks"))
                if d > R + 0.6:
                    w.setze(x, yg + 1, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                              waterlogged=False))
    _zaeune_verbinden(w)
    w.setze(cx, yg, cz - R + 1, w.b("spruce_trapdoor", facing="south", half="top", open=False, powered=False,
                                    waterlogged=False))
    # Laternenraum
    for y in range(yg + 1, yg + 5):
        for x in range(cx - 2, cx + 3):
            for z in range(cz - 2, cz + 3):
                ecke = abs(x - cx) == 2 and abs(z - cz) == 2
                rand = abs(x - cx) == 2 or abs(z - cz) == 2
                if ecke:
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
                elif rand:
                    w.setze(x, y, z, scheibe(w, abs(z - cz) == 2))
    for y in range(yg + 1, yg + 4):
        w.setze(cx, y, cz, w.b("sea_lantern") if y == yg + 2 else w.b("glowstone"))
    # Dach
    for k, r in enumerate((3, 2, 1, 0)):
        y = yg + 5 + k
        for x in range(cx - r, cx + r + 1):
            for z in range(cz - r, cz + r + 1):
                if r == 0:
                    w.setze(x, y, z, w.b("dark_oak_planks"))
                    continue
                rx, rz = x - cx, z - cz
                if abs(rx) == r or abs(rz) == r:
                    f = "south" if rz == -r else "north" if rz == r else "east" if rx == -r else "west"
                    w.setze(x, y, z, w.b("dark_oak_stairs", facing=f, half="bottom", shape="straight",
                                         waterlogged=False))
                else:
                    w.setze(x, y, z, w.b("dark_oak_planks"))
    w.setze(cx, yg + 9, cz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))


def _zaeune_verbinden(w: Welt):
    """Setzt bei allen Holzzäunen die Verbindungen zu Nachbarzäunen/-blöcken."""
    for (x, y, z), b in list(w.bloecke.items()):
        name = w.P.name(b)
        if not name.endswith("_fence"):
            continue
        verb = {}
        for k, (dx, dz) in VEKTOR.items():
            n = w.hole(x + dx, y, z + dz)
            verb[k] = n is not None and n != 0 and (w.P.name(n).endswith("_fence") or w.P.name(n).endswith("_log"))
        w.bloecke[(x, y, z)] = w.b(name, waterlogged=False, **verb)


# --------------------------------------------------------------------------- Steg & Boot

def steg(w: Welt, x0, y0, z0, laenge=10, richtung="south", breite=3, tiefe=6):
    """Holzsteg über dem Wasser. (x0, y0, z0) = Startpunkt (Mitte) auf Laufhöhe y0."""
    vx, vz = VEKTOR[richtung]
    qx, qz = vz, vx  # quer
    planke = w.b("spruce_planks")
    stufe = w.b("spruce_slab", type="top", waterlogged=False)
    pfosten = w.b("spruce_log", axis="y")
    for i in range(laenge):
        for q in range(-(breite // 2), breite // 2 + 1):
            x, z = x0 + vx * i + qx * q, z0 + vz * i + qz * q
            w.setze(x, y0, z, planke if (i + q) % 4 else stufe)
        for q in (-(breite // 2) - 1, breite // 2 + 1):
            x, z = x0 + vx * i + qx * q, z0 + vz * i + qz * q
            if i % 3 == 0:
                for y in range(y0 - tiefe, y0 + 2):
                    w.setze(x, y, z, pfosten)
                if i % 6 == 0:
                    w.setze(x, y0 + 2, z, w.b("lantern", hanging=False, waterlogged=False))
            else:
                w.setze(x, y0 + 1, z, zaun(w, "spruce"))
    _zaeune_verbinden(w)


def boot(w: Welt, x0, y0, z0, richtung="east"):
    """Kleines Segelboot mit Laterne. (x0, y0, z0) = Mitte auf Wasserhöhe."""
    vx, vz = VEKTOR[richtung]
    qx, qz = vz, vx
    planke = w.b("spruce_planks")
    for i in range(-3, 4):
        breite = 1 if abs(i) == 3 else 2 if abs(i) == 2 else 2
        for q in range(-breite, breite + 1):
            x, z = x0 + vx * i + qx * q, z0 + vz * i + qz * q
            w.setze(x, y0, z, planke)
            rand = abs(q) == breite or abs(i) == 3
            if rand:
                w.setze(x, y0 + 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
        w.setze(x0 + vx * i, y0 - 1, z0 + vz * i, w.b("dark_oak_planks"))
    for y in range(y0 + 1, y0 + 7):
        w.setze(x0, y, z0, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    for y in range(y0 + 2, y0 + 7):
        for i in range(1, 4 if y < y0 + 5 else 3):
            if i > 7 - (y - y0):
                continue
            w.setze(x0 - vx * i, y, z0 - vz * i, w.b("white_wool"))
    w.setze(x0 + vx * 3, y0 + 1, z0 + vz * 3, w.b("lantern", hanging=False, waterlogged=False))


# --------------------------------------------------------------------------- Einzel-Vorlagen

def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def vorlage_haus(seed, groesse=1):
    w = _welt(seed)
    stile = [("spruce", "smooth_sandstone", "spruce"), ("dark_oak", "birch_planks", "dark_oak"),
             ("oak", "white_terracotta", "spruce"), ("spruce", "stripped_birch_log", "dark_oak")]
    r, wand, dach = stile[seed % len(stile)]
    stil = Holzstil(w, rahmen=r, wand=wand, dach=dach)
    haus(w, -4, 0, -3, B=[7, 9][groesse], T=[6, 7][groesse], stockwerke=[1, 2][groesse], stil=stil, fundament=2)
    # kleiner Vorgarten
    for _ in range(10):
        x, z = int(w.rng.integers(-5, 6)), int(w.rng.integers(5, 8))
        w.setze(x, 1, z, w.b(["poppy", "dandelion", "azure_bluet", "oxeye_daisy"][int(w.rng.random() * 4)]))
    return w


def vorlage_leuchtturm(seed, groesse=1):
    w = _welt(seed)
    leuchtturm(w, 0, 0, 0, H=[14, 22][groesse], R=[2, 3][groesse])
    return w


def vorlage_steg(seed, groesse=1):
    w = _welt(seed)
    steg(w, 0, 1, 0, laenge=[9, 15][groesse], richtung="south")
    if groesse:
        boot(w, 6, 0, 10, "south")
    return w


def vorlage_palmen(seed, groesse=1):
    w = _welt(seed)
    n = [3, 5][groesse]
    for i in range(n):
        a = i * 2 * math.pi / n + w.rng.random()
        d = 0 if i == 0 else 3 + w.rng.random() * 3
        palme(w, round(math.cos(a) * d), 0, round(math.sin(a) * d), hoehe=7 + int(w.rng.random() * 5),
              neigung=a + math.pi * (w.rng.random() - 0.5) * 0.6)
    for (x, y, z) in [(x, 0, z) for x in range(-6, 7) for z in range(-6, 7) if math.hypot(x, z) < 5.5]:
        if w.frei(x, y, z):
            w.setze(x, y, z, w.b("sand"))
    return w


GEBAEUDE = {
    "fachwerkhaus": ("Fachwerkhaus", vorlage_haus),
    "leuchtturm": ("Leuchtturm", vorlage_leuchtturm),
    "bootssteg": ("Bootssteg", vorlage_steg),
    "palmengruppe": ("Palmengruppe", vorlage_palmen),
}

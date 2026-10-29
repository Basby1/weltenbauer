"""Piraten – Erweiterung (inkl. „Piratenbucht 2“): Piratenstadt, Schmugglerhöhle, Strandräuber-Feuer, Taverne
„Rostiger Anker“, Kanonenbatterie, Kielholstrand, Gestrandeter, Schatzkammer, Ausguckpalme, Flaggenfels,
versunkene Galeone, Beutemarkt, Kapitänsvilla, Rumbrennerei, Baumhausdorf, Riffturm, Piratenfriedhof, Anlegesteg.
Meeresspiegel bei y = 0."""

from __future__ import annotations

import math

import pracht as P
import wald2
from boote import piratenschiff, ruderboot
from drachen import felsen
from lib import Rauschen, Verlauf, einfuegen, ueberwuchern
from piraten import _insel, einfuegen_gedreht
from pracht import Mat
from skulptur import Skulptur, dreh_x, dreh_y, dreh_z, ell, kap, kreisrand, scheibe

U = [0.6, 1.0, 1.7, 2.8]

PASTELL = [["light_blue_terracotta", "light_blue_concrete", "white_terracotta"],
           ["yellow_terracotta", "yellow_concrete", "white_terracotta"],
           ["pink_terracotta", "pink_concrete", "white_terracotta"],
           ["lime_terracotta", "lime_concrete", "white_terracotta"],
           ["orange_terracotta", "orange_concrete", "white_terracotta"],
           ["cyan_terracotta", "cyan_concrete", "white_terracotta"]]


def _welt(seed):
    from lib import Welt
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _zaun(w, art="spruce"):
    return w.b(f"{art}_fence", north=False, south=False, east=False, west=False, waterlogged=False)


def _hoehe(w, x, z):
    return max([p[1] for p in w.bloecke if p[0] == x and p[2] == z] + [-1])


def steg(w, x0, z0, x1, z1, y=1, holz="spruce", pfahl=3):
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for z in range(min(z0, z1), max(z0, z1) + 1):
            w.setze(x, y, z, w.b(f"{holz}_planks") if (x + z) % 5 else w.b(f"stripped_{holz}_log", axis="x"))
            rand = x in (x0, x1) or z in (z0, z1)
            if rand and (x + z) % pfahl == 0:
                for yy in range(-3, y):
                    w.setze(x, yy, z, w.b(f"{holz}_log", axis="y"), ueberschreiben=False)


def palme(w, x, z, y=None, H=None):
    if y is None:
        y = _hoehe(w, x, z) + 1
    einfuegen(w, wald2.palme(int(w.rng.integers(1, 10 ** 6)), H=H), x, y, z)


def piratenflagge(w, x, y, z, L=5, achse="x"):
    """Schwarze Flagge mit weißem Totenkopf (L Blöcke lang, nach -x bzw. -z wehend)."""
    H = max(3, int(L * 0.7))
    for k in range(L):
        for d in range(H):
            px, pz = (x - 1 - k, z) if achse == "x" else (x, z - 1 - k)
            u, v = (k + 0.5) / L - 0.5, (d + 0.5) / H - 0.45
            weiss = (u * u + (v + 0.1) ** 2 < 0.06) or (abs(abs(u) - abs(v - 0.3)) < 0.09 and v > 0.18)
            w.setze(px, y - d + int(0.6 * math.sin(k * 0.9)), pz, w.b("white_wool" if weiss else "black_wool"))


def kanone(w, x, y, z, richtung="east"):
    dx, dz = {"east": (1, 0), "west": (-1, 0), "south": (0, 1), "north": (0, -1)}[richtung]
    ach = "x" if dx else "z"
    w.setze(x, y, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    w.setze(x + dx, y, z + dz, w.b("polished_basalt", axis=ach))
    w.setze(x, y + 1, z, w.b("polished_basalt", axis=ach))
    w.setze(x + dx, y + 1, z + dz, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                                       west="none", waterlogged=False))
    w.setze(x - dx, y, z - dz, w.b("black_concrete_powder" if False else "cobbled_deepslate_slab", type="bottom",
                                   waterlogged=False))


def fass(w, x, y, z):
    w.setze(x, y, z, w.b("barrel", facing="up", open=False))


def haus(w, cx, cz, y0, a, b, farbe, etagen=1, dach="mcw_ziegel", tuer="south", holz="dark_oak"):
    st = P.Stil(w, wand=farbe, sockel="graustein" if y0 <= 1 else "holz_dunkel", gesims="stone_brick", dach=dach,
                holz=holz, laeden=True, blumen=0.6)
    P.gebaeude(w, st, cx - a, cz - b, cx + a, cz + b, y0=y0, etagen=etagen, eh=4, dach="sattel", tuer=tuer,
               gauben=False, kamine=1, sockel_h=0 if y0 > 1 else 1)


def pfahlhaus(w, cx, cz, a, b, farbe, y0=2, **kw):
    for x in range(cx - a, cx + a + 1):
        for z in range(cz - b, cz + b + 1):
            w.setze(x, y0 - 1, z, w.b("spruce_planks"))
            if (x - cx) % 2 == 0 and (z - cz) % 2 == 0 and (abs(x - cx) == a or abs(z - cz) == b):
                for y in range(-3, y0 - 1):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"), ueberschreiben=False)
    haus(w, cx, cz, y0, a, b, farbe, **kw)


# ============================================================================ Bauten

def piratenstadt(seed, g=2):
    """Piratenstadt: bunte Häuser in Pastellfarben an einer Hafenbucht, Stege mit Ruderbooten, eine vor Anker
    liegende Brigg, Taverne, Galgen-Wachturm am Kai und Palmen."""
    w = _welt(seed)
    u = U[g]
    R = _r(22 * u + 8)
    hoehe = _insel(w, R, sand_breite=4, hoehe=_r(3 * u, 2), rauh=0.12)
    for (x, z), h in list(hoehe.items()):
        if x > R * 0.25 and math.hypot(x - R * 0.9, z) < R * 0.75:
            for y in range(-2, h + 1):
                w.bloecke.pop((x, y, z), None)
            w.setze(x, -3, z, w.b("sand"))
    rng = w.rng
    n = 6 + 4 * g
    for i in range(n):
        a = math.pi * 0.55 + i / n * math.pi * 0.9
        d = R * (0.35 + 0.35 * ((i * 7) % 3) / 2)
        cx, cz = round(-math.cos(a) * d * 0.4 - R * 0.25), round(math.sin(a) * d * 1.2)
        cx = round(-R * 0.1 - abs(cx) * 0.6) - (i % 3) * 3
        cz = round((i - n / 2) * (2 * R / n) * 0.85)
        y = max(1, _hoehe(w, cx, cz) + 1)
        haus(w, cx, cz, y, 2 + (i % 2), 2, PASTELL[i % len(PASTELL)], etagen=1 + (i % 3 == 1),
             dach=["mcw_ziegel", "mcw_rot", "mcw_braun"][i % 3], tuer="east")
    for k in range(3):
        z0 = round((k - 1) * R * 0.5)
        steg(w, round(R * 0.2), z0 - 1, round(R * 0.55), z0 + 1)
        einfuegen(w, ruderboot(seed + k, 0), round(R * 0.4), 0, z0 + 3)
    einfuegen(w, piratenschiff(seed, max(0, g - 1)), round(R * 0.95), 0, 0)
    for z in (-R // 2, R // 2):
        for x in (round(R * 0.05), round(-R * 0.6)):
            if (x, z) in hoehe:
                palme(w, x, z + 2)
    hx, hz = round(R * 0.15), -round(R * 0.7)
    for y in range(1, _r(8 * u, 5)):
        w.setze(hx, y, hz, w.b("spruce_log", axis="y"))
    piratenflagge(w, hx, _r(8 * u, 5), hz, _r(4 * u, 3))
    return w


def schmugglerhoehle(seed, g=2):
    """Schmugglerhöhle: ein Meeresarm führt in eine überhängende Felshöhle mit Anlegesteg, Kisten- und
    Fassstapeln, Laternen an Ketten, einem Kran und einer versteckten Treppe nach oben."""
    w = _welt(seed)
    u = U[g]
    R = _r(16 * u + 6)
    fm = Mat(w, ["stone", "andesite", "tuff", "cobblestone", "mossy_cobblestone", "diorite"], kontrast=1.3)
    H = _r(12 * u + 6)
    rn = Rauschen(w, 4)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z) / R
            if d > 1:
                continue
            top = int(H * (1 - d ** 3) * (0.8 + 0.4 * rn(x, 0, z)))
            for y in range(-4, top + 1):
                hoehle = (x / (R * 0.7)) ** 2 + ((y - 1) / (H * 0.6)) ** 2 + (z / (R * 0.55)) ** 2 < 1
                kanal = abs(z) < R * 0.3 and x > 0 and y < H * 0.55 - (x / R) * H * 0.1
                kanal = kanal or (x + z > R * 0.9 and y < H * 0.6 - (x + z - R * 0.9) * 0.15 and y < H * 0.6)
                if hoehle or kanal:
                    if y <= -1:
                        w.setze(x, y, z, w.b("gravel") if y == -4 else w.b("water", level=0))
                    continue
                w.setze(x, y, z, fm(x, y, z, (y + 4) / (H + 4)))
    for x in range(-round(R * 0.55), round(R * 0.3)):
        for z in range(-round(R * 0.4), -round(R * 0.18)):
            w.setze(x, 0, z, w.b("spruce_planks"))
    rng = w.rng
    for i in range(10 + 6 * g):
        x = int(rng.integers(-round(R * 0.5), round(R * 0.25)))
        z = int(rng.integers(-round(R * 0.38), -round(R * 0.2)))
        for y in range(1, 1 + int(rng.integers(1, 3))):
            w.setze(x, y, z, w.b("barrel", facing="up", open=False) if (x + y) % 2 else
                    w.b("chest", facing="south", type="single", waterlogged=False), ueberschreiben=False)
    for i in range(4 + g):
        x = round(-R * 0.5 + i * R * 0.8 / (4 + g))
        ytop = round(H * 0.55)
        for y in range(ytop - 2, ytop):
            w.setze(x, y, 0, w.b("chain", axis="y", waterlogged=False))
        w.setze(x, ytop - 3, 0, w.b("lantern", hanging=True, waterlogged=False))
    einfuegen(w, ruderboot(seed, 0), -2, 0, 2)
    for k in range(_r(H * 0.6)):
        w.setze(-round(R * 0.6) + k // 2, 1 + k, -round(R * 0.3) - (k % 2), w.b("stone_brick_stairs",
                                                                               facing="east", half="bottom",
                                                                               shape="straight", waterlogged=False))
    return w


def strandraeuber(seed, g=1):
    """Strandräuber-Feuer: auf einer Klippe über einem Riff brennt ein falsches Leuchtfeuer in einem Eisenkorb,
    unten liegen die Trümmer eines Schiffes, eine Hütte der Strandräuber und Beutekisten."""
    w = _welt(seed)
    u = U[g]
    R = _r(16 * u + 6)
    _insel(w, R, sand_breite=R * 0.5, hoehe=1, gras=True)
    fm = Mat(w, ["stone", "andesite", "tuff", "cobblestone", "diorite"], kontrast=1.3)
    hoehe = felsen(w, R * 0.45, 12 * u + 5, cx=-round(R * 0.35), cz=0, mat=fm, spitz=0.9, rauh=0.25)
    top = max(hoehe.values())
    cx = -round(R * 0.35)
    for y in range(top + 1, top + 4):
        w.setze(cx, y, 0, w.b("spruce_log", axis="y"))
    for x, z in kreisrand(1.5, cx, 0):
        w.setze(x, top + 4, z, w.b("iron_bars", north=True, south=True, east=True, west=True, waterlogged=False))
    w.setze(cx, top + 4, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    w.setze(cx, top + 5, 0, w.b("fire", age=0, north=False, south=False, east=False, west=False, up=False))
    for x in range(round(R * 0.3), round(R * 0.8)):
        for y in range(-3, 1):
            if (x + y) % 3:
                w.setze(x, y, round(math.sin(x) * 2), fm(x, y, 0, 0.3))
    wrack = piratenschiff(seed, max(0, g - 1))
    for p, b in list(wrack.bloecke.items()):
        if wrack.P.name(b).endswith("_wool") or (p[1] > 6 and w.rng.random() < 0.7) or (p[2] > 0 and p[0] > 0):
            del wrack.bloecke[p]
    einfuegen_gedreht(w, wrack, dreh_y(0.8) @ dreh_z(0.25), (round(R * 0.55), -1.5, round(R * 0.2)))
    haus(w, round(R * 0.05), -round(R * 0.5), 2, 2, 2, ["spruce_planks", "dark_oak_planks", "stripped_spruce_log"],
         dach="mcw_holz", tuer="east")
    for i in range(5):
        fass(w, round(R * 0.15) + i % 3, 2, -round(R * 0.3) + i // 3)
    return w


def taverne(seed, g=1):
    """Taverne „Zum Rostigen Anker“: zweistöckiges Holzhaus auf Pfählen über dem Wasser, Veranda mit Tischen,
    riesiger Anker an der Fassade, Fässer, Laternenketten und ein Ruderboot am Steg."""
    w = _welt(seed)
    u = U[g]
    a, b = _r(5 * u + 2), _r(4 * u + 2)
    _insel(w, a + b + 4, sand_breite=4, hoehe=1)
    for x in range(-a - 3, a + 4):
        for z in range(b + 1, b + 5 + round(u * 2)):
            if abs(x) <= a + 3:
                w.bloecke.pop((x, 0, z), None)
                w.bloecke.pop((x, -1, z), None)
    pfahlhaus(w, 0, 0, a, b, ["spruce_planks", "dark_oak_planks", "stripped_spruce_log", "spruce_planks"], y0=2,
              etagen=2, dach="mcw_braun")
    steg(w, -a - 2, b + 1, a + 2, b + 4, y=1)
    for x in range(-a, a + 1, 3):
        w.setze(x, 2, b + 3, _zaun(w))
        w.setze(x, 3, b + 3, w.b("spruce_pressure_plate", powered=False))
        w.setze(x + 1, 2, b + 3, w.b("spruce_stairs", facing="west", half="bottom", shape="straight",
                                     waterlogged=False))
    S = Skulptur(w, 0.5 * u + 0.25)
    S.mat("e", lambda *_: w.b("anvil", facing="north") if False else w.b("iron_block"))
    S.plus(kap((0, 1, 0), (0, 7, 0), 0.5, 0.5), "e")
    S.plus(kap((-2.5, 6, 0), (2.5, 6, 0), 0.4, 0.4), "e")
    for s in (-1, 1):
        S.plus(kap((0, 1, 0), (s * 2.5, 2.5, 0), 0.5, 0.4), "e")
        S.plus(kap((s * 2.5, 2.5, 0), (s * 3.1, 3.6, 0), 0.4, 0.2), "e")
    S.plus(lambda X, Y, Z: ((X ** 2 + (Y - 8) ** 2 - 1.0) ** 2 < 0.4) & (abs(Z) < 0.5), "e")
    S.rendern((-4, 0, -1), (4, 10, 1), versatz=(0.5, 3.01, b + 1.5))
    einfuegen(w, ruderboot(seed, 0), a + 4, 0, b + 7)
    for x in (-a - 1, a + 1):
        w.setze(x, 6, b + 1, w.b("lantern", hanging=True, waterlogged=False))
        w.setze(x, 7, b + 1, w.b("chain", axis="y", waterlogged=False))
    return w


def kanonenbatterie(seed, g=2):
    """Kanonenbatterie: eine gemauerte, halbrunde Geschützplattform auf einer Klippe, sechs Kanonen hinter
    Schießscharten, Kugelpyramiden, Pulverhaus und Fahnenmast mit Piratenflagge."""
    w = _welt(seed)
    u = U[g]
    R = _r(14 * u + 6)
    _insel(w, R + 4, sand_breite=2, hoehe=1)
    fm = Mat(w, ["stone", "andesite", "tuff", "cobblestone"], kontrast=1.2)
    hoehe = felsen(w, R, 6 * u + 3, mat=fm, spitz=1.8, rauh=0.15)
    top = int(6 * u + 3) + 1
    M = Mat(w, ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "cobblestone", "andesite"])
    Rb = R * 0.7
    for x, z in scheibe(Rb):
        if x < -Rb * 0.2:
            continue
        w.setze(x, top, z, M(x, top, z, 0.3) if (x + z) % 4 else w.b("cobblestone"))
    for x, z in kreisrand(Rb):
        if x < -Rb * 0.2:
            continue
        for y in range(top + 1, top + 3):
            w.setze(x, y, z, M(x, y, z, 0.6))
    n = 6
    for i in range(n):
        a = -math.pi / 2 + (i + 0.5) / n * math.pi
        x, z = round(math.cos(a) * (Rb - 2)), round(math.sin(a) * (Rb - 2))
        kanone(w, x, top + 1, z, "east" if abs(math.sin(a)) < 0.7 else ("south" if z > 0 else "north"))
        xr, zr = round(math.cos(a) * Rb), round(math.sin(a) * Rb)
        w.bloecke.pop((xr, top + 2, zr), None)
    for i in range(3):
        x, z = round(-Rb * 0.1) + i * 2, round(Rb * 0.3) - i * 4
        for k, (dx, dz) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):
            w.setze(x + dx, top + 1, z + dz, w.b("black_concrete" if False else "coal_block"))
        w.setze(x, top + 2, z, w.b("coal_block"))
    haus(w, -round(R * 0.5), 0, top + 1, 2, 2, ["stone_bricks", "cobblestone", "mossy_cobblestone"],
         dach="mcw_schiefer", tuer="east")
    for y in range(top + 1, top + _r(10 * u, 6)):
        w.setze(round(Rb * 0.3), y, 0, w.b("spruce_log", axis="y"))
    piratenflagge(w, round(Rb * 0.3), top + _r(10 * u, 6) - 1, 0, _r(4 * u, 3))
    return w


def kielholstrand(seed, g=2):
    """Kielholstrand: eine Brigg liegt zum Reparieren auf der Seite am Strand, Gerüste, Flaschenzüge, Teerkessel
    mit Feuer, Planken- und Fassstapel, Zelte der Mannschaft."""
    w = _welt(seed)
    u = U[g]
    R = _r(20 * u + 8)
    _insel(w, R, sand_breite=R * 0.7, hoehe=_r(2 * u, 1))
    schiff = piratenschiff(seed, max(0, g - 1))
    for p, b in list(schiff.bloecke.items()):
        if schiff.P.name(b).endswith("_wool"):
            del schiff.bloecke[p]
    einfuegen_gedreht(w, schiff, dreh_x(1.05), (0, 2, round(R * 0.15)))
    for x in range(-round(R * 0.5), round(R * 0.5), 4):
        for y in range(1, _r(8 * u, 4)):
            w.setze(x, y, -round(R * 0.2), _zaun(w))
        w.setze(x, _r(8 * u, 4), -round(R * 0.2), w.b("spruce_planks"))
    for x in range(-round(R * 0.5), round(R * 0.5)):
        w.setze(x, _r(8 * u, 4), -round(R * 0.2), w.b("spruce_slab", type="bottom", waterlogged=False),
                ueberschreiben=False)
    for i in range(3):
        x, z = -round(R * 0.4) + i * round(R * 0.35), -round(R * 0.55)
        y = _hoehe(w, x, z) + 1
        w.setze(x, y, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
        w.setze(x, y + 1, z, w.b("cauldron"))
    for i in range(4 + g):
        x, z = -round(R * 0.6) + i * 3, -round(R * 0.75)
        y = _hoehe(w, x, z) + 1
        for k in range(2):
            for s in (-1, 1):
                w.setze(x + s * (1 - k), y + k, z, w.b("white_wool" if i % 2 else "brown_wool"))
    for i in range(6):
        fass(w, round(R * 0.4) + i % 3, _hoehe(w, round(R * 0.4) + i % 3, -round(R * 0.5)) + 1, -round(R * 0.5))
    palme(w, -round(R * 0.7), round(R * 0.3))
    palme(w, round(R * 0.6), -round(R * 0.6))
    return w


def gestrandeter(seed, g=0):
    """Gestrandeter: eine winzige Sandinsel mit einer Palme, einer Hütte aus Treibholz und Palmwedeln, SOS aus
    Steinen, Flaschenpost, Feuerstelle und Strichliste an der Palme."""
    w = _welt(seed)
    u = U[g]
    R = _r(7 * u + 4)
    _insel(w, R, sand_breite=R, hoehe=1, gras=False)
    palme(w, 1, 1)
    for x in range(-3, 0):
        for k in range(3):
            w.setze(x, 2 + k, -2 + k, w.b("spruce_slab", type="bottom", waterlogged=False))
        for y in range(2, 4):
            w.setze(x, y, -3, _zaun(w, "spruce"))
    for x in range(-4, 1):
        w.setze(x, 5, 0, w.b("jungle_leaves", persistent=True, distance=1, waterlogged=False))
    w.setze(3, 2, -2, w.b("campfire", lit=False, signal_fire=False, facing="north", waterlogged=False))
    sos = ["111 111 111", "100 101 100", "111 101 111", "001 101 001", "111 111 111"]
    for i, zeile in enumerate(sos):
        for j, c in enumerate(zeile):
            if c == "1":
                x, z = -5 + j, R - 4 - i
                if (x, 1, z) in w.bloecke or _hoehe(w, x, z) >= 0:
                    w.setze(x, _hoehe(w, x, z) + 1, z, w.b("cobblestone_slab", type="bottom", waterlogged=False))
    w.setze(R - 1, 0, 0, w.b("glass_bottle" if False else "potted_dead_bush"))
    return w


def schatzkammer(seed, g=2):
    """Schatzkammer im Fels: ein gewölbter Raum hinter einem Felsportal mit Totenkopf, Goldberge, Truhen,
    Kronen, Edelsteinsäulen, Skelettwächter mit Säbeln und Fackeln."""
    w = _welt(seed)
    u = U[g]
    R = _r(13 * u + 6)
    _insel(w, R + 3, sand_breite=3, hoehe=1)
    fm = Mat(w, ["stone", "andesite", "tuff", "deepslate", "cobblestone"], kontrast=1.3)
    H = _r(10 * u + 5)
    for x, z in scheibe(R * 0.85):
        d = math.hypot(x, z) / (R * 0.85)
        top = int(H * (1 - d ** 2.5)) + 1
        for y in range(1, top + 1):
            innen = (x / (R * 0.6)) ** 2 + ((y - 1) / (H * 0.7)) ** 2 + (z / (R * 0.6)) ** 2 < 1
            if innen and not (x < -R * 0.55):
                continue
            if x + z > R * 0.55 and y < H * 0.75 - (x + z - R * 0.55) * 0.25:
                continue
            w.setze(x, y, z, fm(x, y, z, y / H))
    for x in range(round(R * 0.4), round(R * 0.9)):
        for y in range(1, 1 + _r(4 * u, 3)):
            for z in range(-1, 2):
                w.bloecke.pop((x, y, z), None)
    gold = Verlauf(w, "Gold", ["raw_gold_block", "gold_block", "gold_block", "yellow_concrete"])
    rn = Rauschen(w, 2)
    for x, z in scheibe(R * 0.5):
        hh = int((1 - math.hypot(x, z) / (R * 0.5)) * 3 * u * (0.6 + 0.6 * rn(x, 0, z)))
        for y in range(1, hh + 1):
            w.setze(x, y, z, gold(1 + rn(x, y, z) * 2, x, y, z))
    for i in range(6 + 2 * g):
        a = i / (6 + 2 * g) * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)
        w.setze(x, _hoehe(w, x, z) + 1 if _hoehe(w, x, z) < H * 0.5 else 1, z,
                w.b("chest", facing="south", type="single", waterlogged=False))
    for s in (-1, 1):
        for y in range(1, _r(H * 0.6)):
            w.setze(-round(R * 0.2), y, s * round(R * 0.35), w.b("amethyst_block") if y % 3 else
                    w.b("emerald_block"))
        w.setze(round(R * 0.35), 1, s * 2, w.b("skeleton_skull", rotation=4))
    for y in range(1, _r(4 * u, 3) + 3):
        for s in (-1, 1):
            w.setze(round(R * 0.85), y, s * 2, fm(0, y, 0, 0.8))
    w.setze(round(R * 0.85), _r(4 * u, 3) + 2, 0, w.b("skeleton_skull", rotation=4))
    return w


def ausguckpalme(seed, g=1):
    """Ausguckpalme: eine gewaltige schiefe Palme mit einem Krähennest in der Krone, Strickleiter, Fernrohr,
    Hängematte zwischen zwei kleineren Palmen und ein Papageiensitz."""
    w = _welt(seed)
    u = U[g]
    R = _r(10 * u + 5)
    _insel(w, R, sand_breite=R * 0.5, hoehe=1)
    H = _r(18 * u + 8)
    s = 0.0
    for y in range(1, H):
        t = y / H
        x = round(math.sin(t * 1.4) * H * 0.18)
        r = 1.2 * u * (1 - t * 0.4) + 0.4
        for xx, zz in scheibe(r, x, 0):
            w.setze(xx, y, zz, w.b("jungle_log", axis="y") if (y // 2) % 2 else w.b("stripped_jungle_log", axis="y"))
    xt = round(math.sin(1.4) * H * 0.18)
    for xx, zz in scheibe(2.5 * u + 1.2, xt, 0):
        w.setze(xx, H, zz, w.b("spruce_planks"))
    for xx, zz in kreisrand(2.5 * u + 1.2, xt, 0):
        w.setze(xx, H + 1, zz, _zaun(w))
    for k in range(8):
        a = k / 8 * 2 * math.pi
        for d in range(1, _r(8 * u + 3)):
            y = H + 2 + int(1.5 * u) - int(d * d * 0.06 / u)
            w.setze(xt + round(math.cos(a) * d), y, round(math.sin(a) * d),
                    w.b("jungle_leaves", persistent=True, distance=1, waterlogged=False))
    w.setze(xt + 1, H + 2, 0, w.b("spyglass" if False else "lightning_rod", facing="east", powered=False,
                                  waterlogged=False))
    for y in range(1, H):
        w.setze(round(math.sin(y / H * 1.4) * H * 0.18) + 2, y, 1, w.b("ladder", facing="east", waterlogged=False),
                ueberschreiben=False)
    for x in (-round(R * 0.6), -round(R * 0.6) + 6):
        palme(w, x, -round(R * 0.4), H=_r(6 * u + 4))
    for x in range(-round(R * 0.6) + 1, -round(R * 0.6) + 6):
        w.setze(x, 3, -round(R * 0.4), w.b("white_wool" if x % 2 else "red_wool"))
    return w


def flaggenfels(seed, g=2):
    """Flaggenfels: eine schroffe Felsnadel im Meer mit einem riesigen Mast und einer wehenden Piratenflagge,
    darunter ein Felsentor, durch das Boote fahren."""
    w = _welt(seed)
    u = U[g]
    fm = Mat(w, ["stone", "andesite", "tuff", "cobblestone", "diorite", "calcite"], kontrast=1.4)
    R = _r(10 * u + 4)
    for x, z in scheibe(R + 6):
        w.setze(x, -3, z, w.b("sand"))
    hoehe = felsen(w, R, 18 * u + 8, y0=-3, mat=fm, spitz=0.5, rauh=0.3)
    for x in range(-R - 2, R + 3):
        for y in range(-3, _r(4 * u, 3)):
            for z in range(-1, 2):
                w.bloecke.pop((x, y, z), None)
    top = max(hoehe.values())
    mh = _r(10 * u, 6)
    for y in range(top - 2, top + mh):
        w.setze(0, y, 0, w.b("spruce_log", axis="y"))
    L = _r(8 * u, 4)
    piratenflagge(w, 0, top + mh - 1, 0, L)
    return w


def versunkene_galeone(seed, g=2):
    """Versunkene Galeone: ein schief auf dem Meeresgrund liegendes Wrack, überwachsen mit Korallen, Seetang und
    Seegras, offene Schatztruhen, Seelaternen im Rumpf und ein Skelettkapitän am Steuer."""
    w = _welt(seed)
    u = U[g]
    R = _r(18 * u + 6)
    tief = _r(10 * u + 4)
    boden = {}
    for x, z in scheibe(R):
        y = -tief - int(1.5 * math.sin(x * 0.3) * math.cos(z * 0.25))
        boden[(x, z)] = y
        w.setze(x, y, z, w.b("sand") if (x + z) % 5 else w.b("gravel"))
        w.setze(x, y - 1, z, w.b("sandstone"))
    schiff = piratenschiff(seed, max(0, g - 1))
    for p, b in list(schiff.bloecke.items()):
        n = schiff.P.name(b)
        if n.endswith("_wool") and w.rng.random() < 0.85:
            del schiff.bloecke[p]
        elif p[1] > 8 and w.rng.random() < 0.5:
            del schiff.bloecke[p]
    einfuegen_gedreht(w, schiff, dreh_y(0.5) @ dreh_x(0.35), (0, -tief + 2, 0))
    rng = w.rng
    kor = ["tube_coral_block", "brain_coral_block", "bubble_coral_block", "fire_coral_block", "horn_coral_block"]
    for i in range(int(60 * u)):
        x, z = int(rng.integers(-R + 1, R)), int(rng.integers(-R + 1, R))
        if math.hypot(x, z) > R - 1:
            continue
        y = boden.get((x, z), -tief) + 1
        if (x, y, z) in w.bloecke:
            continue
        if rng.random() < 0.4:
            for k in range(int(rng.integers(2, 6))):
                w.setze(x, y + k, z, w.b("kelp_plant") if k < 4 else w.b("kelp", age=5))
        else:
            w.setze(x, y, z, w.b(kor[i % 5]))
    for i in range(6 + 3 * g):
        x, z = int(rng.integers(-R // 3, R // 3)), int(rng.integers(-3, 4))
        w.setze(x, boden.get((x, z), -tief) + 1, z, w.b("sea_lantern"), ueberschreiben=False)
    w.setze(2, -tief + 1, R // 2, w.b("chest", facing="north", type="single", waterlogged=True))
    return w


def beutemarkt(seed, g=1):
    """Beutemarkt: auf einem sandigen Platz zwischen Palmen bunte Marktstände mit Planen, Waffenständer,
    Teppiche, Gewürzsäcke, Käfige mit Papageien und eine Auktionsbühne."""
    w = _welt(seed)
    u = U[g]
    R = _r(14 * u + 6)
    _insel(w, R, sand_breite=R * 0.6, hoehe=1)
    planen = ["red_wool", "yellow_wool", "blue_wool", "green_wool", "orange_wool", "purple_wool"]
    n = 5 + 3 * g
    for i in range(n):
        a = i / n * 2 * math.pi
        cx, cz = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        y = _hoehe(w, cx, cz) + 1
        for dx in (-1, 1):
            for dz in (-1, 1):
                for yy in range(y, y + 3):
                    w.setze(cx + dx, yy, cz + dz, _zaun(w, "dark_oak"))
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                w.setze(cx + dx, y + 3 + (abs(dz) < 2), cz + dz, w.b(planen[i % 6] if (dx + 10) % 2 else
                                                                      "white_wool"))
        for dx in (-1, 0, 1):
            w.setze(cx + dx, y, cz, w.b("barrel", facing="up", open=False) if dx else
                    w.b(["chest", "composter", "hay_block"][i % 3]) if i % 3 != 0 else
                    w.b("chest", facing="south", type="single", waterlogged=False))
    for x, z in scheibe(2.5):
        w.setze(x, 2, z, w.b("spruce_planks"))
    w.setze(0, 3, 0, w.b("lectern", facing="south", has_book=False, powered=False))
    for i in range(4):
        a = i / 4 * 2 * math.pi + 0.4
        palme(w, round(math.cos(a) * R * 0.82), round(math.sin(a) * R * 0.82))
    return w


def kapitaensvilla(seed, g=2):
    """Kapitänsvilla: ein Kolonialhaus mit umlaufender Säulenveranda und Walmdach auf einem Hügel über der Bucht,
    Kanonen am Gartentor, Palmengarten, Fahnenmast und Fernrohrturm."""
    w = _welt(seed)
    u = U[g]
    R = _r(16 * u + 6)
    _insel(w, R, sand_breite=4, hoehe=_r(4 * u, 2))
    top = _hoehe(w, 0, 0) + 1
    a, b = _r(6 * u + 2), _r(4 * u + 2)
    farbe = PASTELL[seed % len(PASTELL)]
    for x in range(-a - 2, a + 3):
        for z in range(-b - 2, b + 3):
            w.setze(x, top - 1, z, w.b("white_terracotta") if (x + z) % 2 else w.b("smooth_quartz"))
            if (abs(x) == a + 2 or abs(z) == b + 2) and (x + z) % 2 == 0:
                for y in range(top, top + 4):
                    w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    st = P.Stil(w, wand=farbe, sockel="marmor", gesims="quartz", dach="mcw_rot" if _stil(seed) else "mcw_gruen",
                holz="dark_oak", laeden=True, blumen=0.8)
    P.gebaeude(w, st, -a, -b, a, b, y0=top, etagen=2, eh=4, dach="walm", tuer="south", gauben=True, kamine=2)
    for x in range(-a - 3, a + 4):
        for z in range(-b - 3, b + 4):
            if abs(x) == a + 2 or abs(z) == b + 2:
                w.setze(x, top + 4, z, w.b("dark_oak_slab", type="bottom", waterlogged=False), ueberschreiben=False)
    for s in (-1, 1):
        kanone(w, s * 3, top, b + 5, "south")
    for i in range(6):
        a2 = i / 6 * 2 * math.pi + 0.3
        palme(w, round(math.cos(a2) * R * 0.7), round(math.sin(a2) * R * 0.7))
    for y in range(top + 8, top + 8 + _r(6 * u, 4)):
        w.setze(0, y + 2 * a // 3, 0, w.b("spruce_log", axis="y"), ueberschreiben=False)
    return w


def rumbrennerei(seed, g=1):
    """Rumbrennerei: Zuckerrohrfelder, ein Brennhaus mit kupfernen Destillierblasen und Schornstein, Lager mit
    Fassreihen, Ochsenkarren und Steg zur Verladung."""
    w = _welt(seed)
    u = U[g]
    R = _r(16 * u + 6)
    _insel(w, R, sand_breite=3, hoehe=1)
    for x in range(-round(R * 0.7), -round(R * 0.1)):
        for z in range(-round(R * 0.6), round(R * 0.2)):
            if math.hypot(x, z) < R - 4:
                if x % 3 == 0:
                    w.setze(x, 1, z, w.b("water", level=0))
                else:
                    w.setze(x, 1, z, w.b("sand"))
                    for y in range(2, 4):
                        w.setze(x, y, z, w.b("sugar_cane", age=0))
    a, b = _r(4 * u + 2), _r(3 * u + 2)
    st = P.Stil(w, wand="backstein", sockel="graustein", gesims="stone_brick", dach="mcw_braun", holz="spruce")
    P.gebaeude(w, st, round(R * 0.15) - a, -b, round(R * 0.15) + a, b, y0=2, etagen=1, eh=5, dach="sattel",
               tuer="south", gauben=False, kamine=0)
    for y in range(2, 2 + _r(12 * u, 8)):
        w.setze(round(R * 0.15) + a - 1, y, -b + 1, w.b("bricks"))
    w.setze(round(R * 0.15) + a - 1, 2 + _r(12 * u, 8), -b + 1, w.b("campfire", lit=True, signal_fire=True,
                                                                     facing="north", waterlogged=False))
    for k in range(2):
        cx = round(R * 0.15) - a + 2 + k * 3
        w.setze(cx, 3, 0, w.b("waxed_copper_block"))
        w.setze(cx, 4, 0, w.b("waxed_cut_copper"))
        w.setze(cx, 5, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for x in range(round(R * 0.0), round(R * 0.45)):
        for z in (b + 3, b + 4):
            for y in (2, 3):
                if (x + y) % 2 == 0 or y == 2:
                    w.setze(x, y, z, w.b("barrel", facing="east", open=False))
    steg(w, round(R * 0.65), -2, R + 3, 2)
    return w


def baumhausdorf(seed, g=2):
    """Baumhausdorf der Piraten: Hütten in den Kronen großer Dschungelbäume, verbunden durch Hängebrücken,
    Strickleitern, Ausguck mit Flagge und eine Seilrutsche zum Strand."""
    w = _welt(seed)
    u = U[g]
    R = _r(18 * u + 6)
    _insel(w, R, sand_breite=4, hoehe=2)
    n = 3 + g
    pos = []
    for i in range(n):
        a = i / n * 2 * math.pi
        cx, cz = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        H = _r(10 * u + 6 + (i % 2) * 3)
        y0 = _hoehe(w, cx, cz) + 1
        for y in range(y0, y0 + H):
            for x, z in scheibe(1.2 * u + 0.4, cx, cz):
                w.setze(x, y, z, w.b("jungle_log", axis="y"))
        yb = y0 + H
        for x, z in scheibe(3 * u + 1, cx, cz):
            w.setze(x, yb, z, w.b("spruce_planks"))
        for x, z in kreisrand(3 * u + 1, cx, cz):
            w.setze(x, yb + 1, z, _zaun(w))
        haus(w, cx, cz, yb + 1, 2, 2, ["spruce_planks", "jungle_planks", "stripped_jungle_log"],
             dach="mcw_stroh", tuer="south", holz="jungle")
        for x, z in scheibe(4 * u + 2, cx, cz):
            if math.hypot(x - cx, z - cz) > 3 * u + 1.5:
                w.setze(x, yb + 6, z, w.b("jungle_leaves", persistent=True, distance=1, waterlogged=False),
                        ueberschreiben=False)
        pos.append((cx, yb, cz))
    for (ax, ay, az), (bx, by, bz) in zip(pos, pos[1:] + pos[:1]):
        L = max(abs(bx - ax), abs(bz - az))
        for k in range(L + 1):
            t = k / L
            x, z = round(ax + (bx - ax) * t), round(az + (bz - az) * t)
            y = round(ay + (by - ay) * t - math.sin(t * math.pi) * L * 0.08)
            w.setze(x, y, z, w.b("spruce_slab", type="bottom", waterlogged=False), ueberschreiben=False)
    cx, yb, cz = pos[0]
    piratenflagge(w, cx, yb + 11, cz, _r(3 * u, 3))
    for y in range(yb + 6, yb + 12):
        w.setze(cx, y, cz, w.b("spruce_log", axis="y"))
    return w


def riffturm(seed, g=1):
    """Riffturm: ein runder Steinturm auf einem Korallenriff mitten im Meer, Kanonen auf der Plattform, ein
    Kettenbaum versperrt die Durchfahrt, Ruderboot am Fuß."""
    w = _welt(seed)
    u = U[g]
    R = _r(10 * u + 5)
    kor = ["tube_coral_block", "brain_coral_block", "fire_coral_block", "horn_coral_block", "bubble_coral_block"]
    rn = Rauschen(w, 3)
    for x, z in scheibe(R + 4):
        hh = int(-3 + 2.5 * rn(x, 0, z) * (1 - math.hypot(x, z) / (R + 4)))
        for y in range(-4, hh + 1):
            w.setze(x, y, z, w.b(kor[(x * 3 + z) % 5]) if y == hh and rn(x, 5, z) > 0.62 else
                    w.b("sand") if (x + z) % 4 else w.b("gravel"))
    M = Mat(w, ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "cobblestone"])
    H = _r(14 * u + 6)
    Rt = 3 * u + 2
    for y in range(-3, H):
        for x, z in kreisrand(Rt):
            w.setze(x, y, z, M(x, y, z, (y + 3) / (H + 3)))
    for x, z in scheibe(Rt + 1):
        w.setze(x, H, z, M(x, H, z, 0.9))
    for i, (x, z) in enumerate(kreisrand(Rt + 1)):
        if i % 2 == 0:
            w.setze(x, H + 1, z, M(x, H + 1, z, 0.95))
    kanone(w, 0, H + 1, 0, "east")
    kanone(w, 0, H + 1, -1, "west")
    for x in range(round(Rt), R + 6):
        w.setze(x, 0, 0, w.b("chain", axis="x", waterlogged=False))
    einfuegen(w, ruderboot(seed, 0), 0, 0, round(Rt) + 3)
    piratenflagge(w, 0, H + 6, 1, _r(3 * u, 3))
    for y in range(H + 1, H + 7):
        w.setze(0, y, 1, w.b("spruce_log", axis="y"))
    return w


def piratenfriedhof(seed, g=1):
    """Piratenfriedhof: auf einer windigen Landzunge schiefe Holzkreuze und in den Sand gerammte Säbel, Gräber
    mit Dreispitz-Hüten, ein kaputtes Beiboot als Grabstein und eine Laterne am Pfahl."""
    from spuk import knorrbaum
    w = _welt(seed)
    u = U[g]
    R = _r(12 * u + 5)
    _insel(w, R, sand_breite=R * 0.4, hoehe=2)
    rng = w.rng
    n = 8 + 6 * g
    for i in range(n):
        a = i * 2.39996
        d = R * 0.7 * math.sqrt((i + 0.5) / n)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = _hoehe(w, x, z) + 1
        art = i % 3
        if art == 0:
            for k in range(3):
                w.setze(x, y + k, z, _zaun(w, "spruce" if i % 2 else "dark_oak"))
            w.setze(x, y + 1, z + 1, w.b("spruce_trapdoor", facing="south", half="top", open=True, powered=False,
                                         waterlogged=False))
        elif art == 1:
            w.setze(x, y, z, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
            w.setze(x, y + 1, z, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
        else:
            w.setze(x, y, z, w.b("cobblestone_slab", type="bottom", waterlogged=False))
            w.setze(x, y, z + 1, w.b("black_carpet"))
        for k in range(2):
            w.setze(x, y - 1, z - 1 - k, w.b("coarse_dirt"))
    for y in range(1, 5):
        w.setze(R // 2, _hoehe(w, R // 2, 0) + 1 if y == 1 else y + 2, 0, _zaun(w), ueberschreiben=False)
    w.setze(R // 2, 7, 0, w.b("lantern", hanging=False, waterlogged=False))
    return w


def anlegesteg(seed, g=0):
    """Anlegesteg: ein langer Holzsteg mit Pollern und Tauen, zwei Ruderboote, Fischkörbe, Kisten, eine
    Glocke am Ende und ein kleiner Schuppen am Strand."""
    w = _welt(seed)
    u = U[g]
    L = _r(14 * u + 8)
    _insel(w, 6, sand_breite=3, hoehe=1)
    steg(w, 3, -1, L, 1)
    for x in range(4, L + 1, 4):
        for s in (-1, 1):
            w.setze(x, 2, s, w.b("spruce_log", axis="y"))
    for k, x in enumerate((L // 2, L - 2)):
        einfuegen(w, ruderboot(seed + k, 0), x, 0, 4 if k else -4)
    for x in (6, 7):
        fass(w, x, 2, 1)
    w.setze(L, 2, 0, _zaun(w))
    w.setze(L, 3, 0, w.b("bell", attachment="floor", facing="north", powered=False))
    haus(w, -1, 0, 2, 2, 2, ["spruce_planks", "dark_oak_planks", "stripped_spruce_log"], dach="mcw_holz",
         tuer="east")
    return w


NEU = {
    "piratenstadt": ("Piratenstadt", piratenstadt),
    "schmugglerhoehle": ("Schmugglerhöhle", schmugglerhoehle),
    "strandraeuber": ("Strandräuber-Feuer", strandraeuber),
    "taverne": ("Taverne „Rostiger Anker“", taverne),
    "kanonenbatterie": ("Kanonenbatterie", kanonenbatterie),
    "kielholstrand": ("Kielholstrand", kielholstrand),
    "gestrandeter": ("Gestrandeter", gestrandeter),
    "schatzkammer": ("Schatzkammer", schatzkammer),
    "ausguckpalme": ("Ausguckpalme", ausguckpalme),
    "flaggenfels": ("Flaggenfels", flaggenfels),
    "versunkene_galeone": ("Versunkene Galeone", versunkene_galeone),
    "beutemarkt": ("Beutemarkt", beutemarkt),
    "kapitaensvilla": ("Kapitänsvilla", kapitaensvilla),
    "rumbrennerei": ("Rumbrennerei", rumbrennerei),
    "baumhausdorf": ("Baumhausdorf", baumhausdorf),
    "riffturm": ("Riffturm", riffturm),
    "piratenfriedhof": ("Piratenfriedhof", piratenfriedhof),
    "anlegesteg": ("Anlegesteg", anlegesteg),
}

"""Burgen & Festungen (neu) – 20 verschiedene Bauwerke im Pracht-Stil.

Jede Burg wählt zwei eigene Materialwelten (Stil 1 / Stil 2) aus einem Pool – Wände aus 6–8 Blocksorten
mit fleckigem Höhenverlauf und Moos am Fuß, Dächer aus gemischten Treppen, Gesimse, Kragsteine,
Schießscharten, Wehrgänge, Banner, Höfe mit Leben (Fässer, Heu, Brunnen, Wagen, Stände).
"""

from __future__ import annotations

import math

import pracht as P
from lib import Rauschen, einfuegen, laub, zerfall
from pracht import Mat, gelaende, treppe
from skulptur import kreisrand, scheibe, verbinde, zur_mitte
from weltwunder import hohl

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


GEGEN = {"north": "south", "south": "north", "east": "west", "west": "east"}

# ============================================================================ Stilpool

POOL = {
    "nord": dict(wand="graustein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="spruce",
                 banner=["red_wool", "yellow_wool"], mauer="stone_brick"),
    "kalk": dict(wand="kalkstein", sockel="graustein", gesims="stone_brick", dach="kupfer", holz="spruce",
                 banner=["blue_wool", "white_wool"], mauer="stone_brick"),
    "backstein": dict(wand="backstein", sockel="graustein", gesims="brick", dach="schiefer", holz="dark_oak",
                      banner=["white_wool", "red_wool"], mauer="brick"),
    "sand": dict(wand="sandstein", sockel="sandstein", gesims="sandstone", dach="ziegel", holz="jungle",
                 banner=["orange_wool", "white_wool"], mauer="sandstone"),
    "schwarz": dict(wand="schwarzstein", sockel="schwarzstein", gesims="polished_blackstone_brick", dach="schwarz",
                    holz="dark_oak", banner=["purple_wool", "black_wool"], mauer="polished_blackstone_brick"),
    "tief": dict(wand="tiefenschiefer", sockel="tiefenschiefer", gesims="deepslate_brick", dach="schiefer",
                 holz="dark_oak", banner=["cyan_wool", "light_gray_wool"], mauer="deepslate_brick"),
    "maerchen": dict(wand="putz", sockel="kalkstein", gesims="stone_brick", dach="blau", holz="birch",
                     banner=["light_blue_wool", "white_wool"], mauer="stone_brick"),
    "rot": dict(wand="rotsandstein", sockel="rotsandstein", gesims="red_sandstone", dach="dunkelholz",
                holz="acacia", banner=["red_wool", "black_wool"], mauer="red_sandstone"),
    "moos": dict(wand="moosstein", sockel="graustein", gesims="mossy_stone_brick", dach="moos", holz="spruce",
                 banner=["green_wool", "brown_wool"], mauer="mossy_stone_brick"),
    "marmor": dict(wand="marmor", sockel="kalkstein", gesims="quartz", dach="kupfer", holz="birch",
                   banner=["yellow_wool", "white_wool"], mauer="stone_brick"),
}

WAENDE_MAUER = {"stone_brick", "mossy_stone_brick", "deepslate_brick", "polished_blackstone_brick", "nether_brick",
                "red_nether_brick", "end_stone_brick", "sandstone", "red_sandstone", "brick", "mud_brick"}


class Burgstil:
    def __init__(self, w, name, **extra):
        d = dict(POOL[name])
        d.update(extra)
        self.w = w
        self.name = name
        self.banner = d.pop("banner")
        self.mauer = d.pop("mauer")
        self.st = P.Stil(w, wand=d["wand"], sockel=d["sockel"], gesims=d["gesims"], dach=d["dach"],
                         holz=d["holz"], laeden=d.get("laeden", True), fachwerk=d.get("fachwerk", False),
                         fenster=d.get("fenster", "glass_pane"), licht=d.get("licht", "lantern"))
        self.wand = self.st.wand
        self.sockel = self.st.sockel
        self.holz = d["holz"]
        self.gesims = d["gesims"]
        self.dach = self.st.dach

    def mauerwand(self):
        m = self.mauer if self.mauer in WAENDE_MAUER else "stone_brick"
        return self.w.b(f"{m}_wall", up=True, north="none", south="none", east="none", west="none",
                        waterlogged=False)


def stile(w, seed, a, b):
    return Burgstil(w, a if _stil(seed) == 0 else b)


# ============================================================================ Bauteile


def mauer(w, B, a, b, H, dick=3, y0=0, mitte=(0, 0), scharten=True, wehrgang_dach=False):
    """Wehrmauer von a nach b: Mauerkörper mit Anlauf, Wehrgang, Zinnen außen, Kragsteine darunter,
    Brüstung innen, Schießscharten. mitte: Punkt im Burginneren (bestimmt außen/innen)."""
    (ax, az), (bx, bz) = a, b
    n = int(max(abs(bx - ax), abs(bz - az)))
    if n == 0:
        return
    dx, dz = (bx - ax) / n, (bz - az) / n
    nx, nz = -dz, dx
    mx, mz = (ax + bx) / 2 - mitte[0], (az + bz) / 2 - mitte[1]
    if nx * mx + nz * mz < 0:
        nx, nz = -nx, -nz          # n zeigt nach außen
    aus = "east" if abs(nx) >= abs(nz) and nx > 0 else "west" if abs(nx) >= abs(nz) else \
        "south" if nz > 0 else "north"
    halb = dick / 2
    for k in range(n + 1):
        cx, cz = ax + dx * k, az + dz * k
        for t10 in range(int(-halb * 10) - 5, int(halb * 10) + 6, 5):
            t = t10 / 10
            x, z = round(cx + nx * t), round(cz + nz * t)
            for y in range(y0, y0 + H):
                if t > halb - 0.6 and scharten and (y - y0) % 6 == 3 and k % 5 == 2 and y > y0 + 2:
                    w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                         waterlogged=False))
                else:
                    w.setze(x, y, z, B.wand(x, y, z, (y - y0) / max(1, H + 3)))
            # Anlauf (Sockelschräge) außen
            if t > halb - 0.6:
                ox, oz = round(cx + nx * (halb + 1)), round(cz + nz * (halb + 1))
                w.setze(ox, y0, oz, treppe(w, B.gesims, GEGEN[aus]), ueberschreiben=False)
        # Wehrgang (Laufebene) und Zinnen
        ox, oz = round(cx + nx * (halb + 0.8)), round(cz + nz * (halb + 0.8))
        w.setze(ox, y0 + H - 1, oz, treppe(w, B.gesims, GEGEN[aus], "top"), ueberschreiben=False)
        w.setze(ox, y0 + H, oz, B.wand(ox, y0 + H, oz, 0.9))
        if k % 2 == 0:
            w.setze(ox, y0 + H + 1, oz, B.wand(ox, y0 + H + 1, oz, 0.95))
        else:
            w.setze(ox, y0 + H + 1, oz, w.b(f"{B.mauer}_slab" if B.mauer in WAENDE_MAUER else "stone_brick_slab",
                                            type="bottom", waterlogged=False))
        ix, iz = round(cx - nx * (halb + 0.2)), round(cz - nz * (halb + 0.2))
        if w.frei(ix, y0 + H, iz):
            w.setze(ix, y0 + H, iz, B.mauerwand())
        if wehrgang_dach and k % 3 == 0:
            pass


def eckturm(w, B, x, z, y0, H, R, dach="kegel", form="rund", fahne=True):
    return P.turm(w, B.st, x, z, y0, H, R, form=form, dach=dach, fahne=B.banner if fahne else None)


def tor(w, B, x, z, y0, breite, hoehe, achse="z", tiefe=4, gitter=True):
    """Toröffnung (achse: Durchgangsrichtung) mit Spitzbogen, Fallgitter und Laternen."""
    hb = breite // 2
    for q in range(-hb, hb + 1):
        hq = hoehe - (1 if abs(q) == hb and hb > 0 else 0)
        for y in range(y0, y0 + hq):
            for d in range(-tiefe, tiefe + 1):
                p = (x + q, y, z + d) if achse == "z" else (x + d, y, z + q)
                w.bloecke.pop(p, None)
        for d in range(-tiefe, tiefe + 1):
            p = (x + q, y0 - 1, z + d) if achse == "z" else (x + d, y0 - 1, z + q)
            w.setze(*p, w.b("cobblestone") if (q + d) % 3 else w.b("gravel"))
    if gitter:
        for q in range(-hb, hb + 1):
            for y in range(y0 + hoehe - 3, y0 + hoehe - 1 + (0 if abs(q) == hb else 1)):
                p = (x + q, y, z + tiefe) if achse == "z" else (x + tiefe, y, z + q)
                w.setze(*p, w.b("iron_bars", north=achse != "z", south=achse != "z", east=achse == "z",
                                west=achse == "z", waterlogged=False))
    for s in (-1, 1):
        p = (x + s * (hb + 1), y0 + hoehe - 2, z + tiefe + 1) if achse == "z" else \
            (x + tiefe + 1, y0 + hoehe - 2, z + s * (hb + 1))
        w.setze(*p, w.b("lantern", hanging=False, waterlogged=False))
    # Wappen über dem Tor
    p = (x, y0 + hoehe + 1, z + tiefe + 1) if achse == "z" else (x + tiefe + 1, y0 + hoehe + 1, z)
    for k in range(3):
        w.setze(p[0], p[1] + k, p[2], w.b(B.banner[k % 2]))


def graben(w, pts_innen, breite, tiefe=2):
    """Wassergraben entlang eines Rechtecks oder Kreises (pts_innen: Funktion (x, z) -> Abstand zur Mauer)."""
    pass


def wasserflaeche(w, felder, tiefe=2):
    for (x, z) in felder:
        for y in range(-tiefe + 1, 1):
            w.setze(x, y, z, w.b("water", level=0))
        w.setze(x, -tiefe, z, w.b("gravel") if (x + z) % 3 else w.b("clay"))


def hofleben(w, B, felder, dichte=0.05):
    """Fässer, Heu, Kisten-Stapel, Brennholz, Wagen, Laternenpfähle auf freien Hofzellen."""
    rng = w.rng
    for (x, y, z) in felder:
        if not w.frei(x, y, z):
            continue
        r = rng.random()
        if r < dichte * 0.3:
            w.setze(x, y, z, w.b("barrel", facing="up", open=False))
            if rng.random() < 0.4:
                w.setze(x, y + 1, z, w.b("barrel", facing="up", open=False))
        elif r < dichte * 0.55:
            w.setze(x, y, z, w.b("hay_block", axis="y"))
        elif r < dichte * 0.7:
            w.setze(x, y, z, w.b(f"stripped_{B.holz}_log", axis="x"))
        elif r < dichte * 0.8:
            w.setze(x, y, z, w.b(f"{B.holz}_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False))
            w.setze(x, y + 1, z, w.b("lantern", hanging=False, waterlogged=False))
        elif r < dichte * 0.9:
            w.setze(x, y, z, w.b("composter", level=0) if rng.random() < 0.5 else w.b("cauldron"))
        elif r < dichte:
            w.setze(x, y, z, w.b("smithing_table") if rng.random() < 0.5 else w.b("grindstone", face="floor",
                                                                                   facing="north"))


def hofboden(w, felder, art="pflaster"):
    r = Rauschen(w, 2.5)
    for (x, z) in felder:
        v = r(x, 0, z)
        if art == "pflaster":
            b = "cobblestone" if v < 0.35 else "stone_bricks" if v < 0.55 else "gravel" if v < 0.68 else \
                "andesite" if v < 0.8 else "coarse_dirt" if v < 0.9 else "mossy_cobblestone"
        elif art == "sand":
            b = "sandstone" if v < 0.4 else "smooth_sandstone" if v < 0.6 else "sand" if v < 0.85 else "cut_sandstone"
        else:
            b = "dirt_path" if v < 0.4 else "coarse_dirt" if v < 0.6 else "gravel" if v < 0.75 else "grass_block"
        w.setze(x, 0, z, w.b(b, snowy=False) if b == "grass_block" else w.b(b))


def brunnen(w, B, x, z, y=1):
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if dx == 0 and dz == 0:
                w.setze(x, y - 1, z, w.b("water", level=0))
                w.setze(x, y - 2, z, w.b("water", level=0))
            else:
                w.setze(x + dx, y, z + dz, B.mauerwand() if abs(dx) + abs(dz) == 2 else
                        w.b(f"{B.mauer}_slab" if B.mauer in WAENDE_MAUER else "stone_brick_slab", type="bottom",
                            waterlogged=False))
    for dx, dz in ((-1, -1), (1, 1), (-1, 1), (1, -1)):
        if abs(dx) == 1 and dx == dz:
            for k in range(1, 3):
                w.setze(x + dx, y + k, z + dz, w.b(f"{B.holz}_fence", north=False, south=False, east=False,
                                                   west=False, waterlogged=False))
    for q in (-1, 0, 1):
        w.setze(x + q, y + 3, z + q, w.b(f"{B.holz}_slab", type="bottom", waterlogged=False))
    w.setze(x, y + 2, z, w.b("chain", axis="y", waterlogged=False))


def fahne_haengend(w, B, x, y, z, laenge):
    for k in range(laenge):
        w.setze(x, y - k, z, w.b(B.banner[(k // 2) % 2]))


def rechteck(x0, z0, x1, z1):
    return [(x, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)]


# ============================================================================ 1 Bergfried


def bergfried(seed, g=1):
    """Bergfried: wuchtiger viereckiger Turm mit Eckerkern auf Kragsteinen, Wehrplattform mit Zinnen,
    Hocheingang über eine Holztreppe, Banner und ein kleiner Wirtschaftshof."""
    w = _welt(seed)
    B = stile(w, seed, "nord", "tief")
    u = U[g]
    h = _r(4 * u + 2, 3)
    H = _r(22 * u + 6, 12)
    gelaende(w, h + _r(10 * u, 6), art="wiese", wege=[((0, h + 2), (0, h + _r(10 * u, 6)))])
    spitze = P.turm(w, B.st, 0, 0, 1, H, h, form="eckig", dach="pyramide" if _stil(seed) == 0 else "platt",
                    fenster=7, fahne=B.banner if _stil(seed) == 1 else None)
    # Eckerker auf Kragsteinen
    for sx in (-1, 1):
        for sz in (-1, 1):
            ex, ez = sx * (h + 1), sz * (h + 1)
            y0 = H - _r(6 * u, 3)
            for k in range(3):
                w.setze(ex - sx * k // 2, y0 - 3 + k, ez - sz * k // 2, treppe(w, B.gesims, "north" if sz > 0 else
                                                                            "south", "top"), ueberschreiben=False)
            P.turm(w, B.st, ex, ez, y0, _r(7 * u, 4), max(1.2, 1.4 * u), dach="kegel", fenster=4, krone=False,
                   fahne=None, schiessscharten=False)
    # Hocheingang mit Holztreppe
    ye = _r(5 * u, 3)
    for y, half in ((ye, "lower"), (ye + 1, "upper")):
        w.setze(0, y, h, w.b(f"{B.holz}_door", facing="south", half=half, hinge="left", open=False, powered=False))
    for k in range(ye):
        for x in (-1, 0, 1):
            w.setze(x, ye - 1 - k + 0, h + 1 + k, w.b(f"{B.holz}_stairs", facing="north", half="bottom",
                                                      shape="straight", waterlogged=False))
        for x in (-2, 2):
            w.setze(x, ye - k, h + 1 + k, w.b(f"{B.holz}_fence", north=True, south=True, east=False, west=False,
                                             waterlogged=False))
    for x in range(-1, 2):
        w.setze(x, ye - 1, h + 1, w.b(f"{B.holz}_planks"))
    # Banner an den Seiten
    for x, z in ((-h - 1, 0), (h + 1, 0)):
        fahne_haengend(w, B, x, H - 4, z, _r(6 * u, 3))
    # Wirtschaftshof: Zaun, Heu, Fässer
    hofleben(w, B, [(x, 1, z) for x in range(-h - 5, h + 6) for z in range(-h - 6, -h - 1)], 0.12)
    hohl(w, 2)
    return w


# ============================================================================ 2 Torburg


def torburg(seed, g=1):
    """Torburg: Torhaus zwischen zwei runden Flankentürmen, Fallgitter, Zugbrücke an Ketten über einen
    Wassergraben, Wehrgang mit Zinnen und Mauerstümpfe zu beiden Seiten."""
    w = _welt(seed)
    B = stile(w, seed, "kalk", "backstein")
    u = U[g]
    R = 2.4 * u + 1.6
    H = _r(13 * u + 6, 9)
    br = _r(1.6 * u + 1.5, 3) | 1
    ht = _r(3.5 * u + 2.5, 4)
    abst = br // 2 + int(R) + 2
    gw = _r(4 * u + 2, 3)
    gelaende(w, abst + R + _r(14 * u, 8), art="wiese", wege=[((0, 0), (0, abst + 20))])
    wasserflaeche(w, [(x, z) for x in range(-abst - int(R) - 14, abst + int(R) + 15)
                      for z in range(int(R) + 3, int(R) + 3 + gw)])
    for sx in (-1, 1):
        mauer(w, B, (sx * (abst + 1), 0), (sx * (abst + int(R) + 12), 0), H - 4, dick=3, y0=1, mitte=(0, -10))
    for s in (-1, 1):
        eckturm(w, B, s * abst, 0, 1, H, R, dach="kegel" if _stil(seed) == 0 else "glocke")
    # Torhaus
    P.gebaeude(w, B.st, -abst + 1, -int(R) - 1, abst - 1, int(R) + 1, y0=1, etagen=2, eh=_r((H - 4) / 2, 4),
               dach="sattel", first_x=True, tuer="north", gauben=False, kamine=0)
    tor(w, B, 0, 0, 1, br, ht, achse="z", tiefe=int(R) + 2)
    # Zugbrücke
    for x in range(-br // 2, br // 2 + 1):
        for z in range(int(R) + 3, int(R) + 3 + gw + 1):
            w.setze(x, 1, z, w.b(f"{B.holz}_planks") if (z % 3) else w.b(f"stripped_{B.holz}_log", axis="x"))
    for s in (-1, 1):
        for k in range(gw):
            w.setze(s * (br // 2 + 1), 2 + (gw - k) * (ht - 1) // gw, int(R) + 3 + k,
                    w.b("chain", axis="y", waterlogged=False))
    hohl(w, 2)
    return w


# ============================================================================ 3 Ringburg


def ringburg(seed, g=2):
    """Ringburg: runde Ringmauer mit Rundtürmen und Torbau, im Hof Bergfried, Palas mit Fachwerk,
    Brunnen, Ställe und Lagerplätze."""
    w = _welt(seed)
    B = stile(w, seed, "nord", "marmor")
    u = U[g]
    R = _r(17 * u + 4, 12)
    H = _r(7 * u + 3, 5)
    gelaende(w, R + _r(10 * u, 6), art="wiese", wege=[((0, R), (0, R + 14))])
    hofboden(w, scheibe(R - 2), "pflaster")
    n = 6 if u < 1.5 else 8
    pts = [(round(math.cos(i / n * 2 * math.pi + math.pi / 2) * R), round(math.sin(i / n * 2 * math.pi + math.pi / 2) * R))
           for i in range(n)]
    for i in range(n):
        mauer(w, B, pts[i], pts[(i + 1) % n], H, dick=3, y0=1, mitte=(0, 0))
    for i, (x, z) in enumerate(pts):
        if i == 0:
            continue
        eckturm(w, B, x, z, 1, H + _r(5 * u, 3), max(1.6, 2.2 * u), dach="kegel")
    # Torbau (Süd)
    tx, tz = pts[0]
    P.turm(w, B.st, tx, tz, 1, H + _r(7 * u, 4), max(2.2, 3.0 * u), form="eckig", dach="pyramide",
           fahne=B.banner)
    tor(w, B, tx, tz, 1, 3 if u < 1.5 else 5, _r(3 * u + 2, 4), achse="z", tiefe=_r(3 * u + 1, 2))
    # Bergfried
    P.turm(w, B.st, -_r(R * 0.35), -_r(R * 0.3), 1, _r(26 * u + 6), max(2.5, 3.6 * u), form="eckig",
           dach="platt" if _stil(seed) == 0 else "pyramide", fahne=B.banner)
    # Palas (Fachwerk oben)
    pst = P.Stil(w, wand=B.st.wand, sockel=B.st.sockel, gesims=B.gesims, dach=B.dach, holz=B.holz,
                 fachwerk=_stil(seed) == 0)
    P.gebaeude(w, pst, _r(R * 0.05), -_r(R * 0.65), _r(R * 0.7), -_r(R * 0.2), y0=1, etagen=2,
               eh=_r(3 * u + 2, 4), dach="sattel", tuer="south")
    # Stall
    P.gebaeude(w, P.Stil(w, wand="holz_dunkel", sockel="graustein", gesims=B.holz if False else "stone_brick",
                         dach="schindel", holz=B.holz, laeden=False),
               -_r(R * 0.75), _r(R * 0.1), -_r(R * 0.35), _r(R * 0.5), y0=1, etagen=1, eh=_r(3 * u + 1, 3),
               dach="sattel", tuer="east", gauben=False, kamine=0)
    brunnen(w, B, _r(R * 0.25), _r(R * 0.25))
    hofleben(w, B, [(x, 1, z) for x, z in scheibe(R - 3)], 0.03)
    hohl(w, 2)
    return w


# ============================================================================ 4 Wehrmauer


def wehrmauer(seed, g=1):
    """Stück Stadtmauer zum Aneinanderreihen: hohe Mauer mit Wehrgang, zwei Halbschalentürmen, Pforte und
    Aufgangstreppe auf der Innenseite."""
    w = _welt(seed)
    B = stile(w, seed, "nord", "sand")
    u = U[g]
    L = _r(20 * u + 8, 14)
    H = _r(9 * u + 4, 6)
    gelaende(w, L + 6, art="wiese")
    mauer(w, B, (-L, 0), (L, 0), H, dick=3, y0=1, mitte=(0, -10))
    for sx in (-1, 1):
        x = sx * _r(L * 0.55)
        P.turm(w, B.st, x, 2, 1, H + _r(5 * u, 3), max(2.0, 2.8 * u), form="rund",
               dach="kegel" if _stil(seed) == 0 else "platt", fahne=B.banner)
    tor(w, B, 0, 0, 1, 3, _r(3 * u + 1, 3), achse="z", tiefe=2, gitter=False)
    for y, half in ((1, "lower"), (2, "upper")):
        pass
    # Treppe innen
    for k in range(H):
        for t in (-2, -3):
            w.setze(-_r(L * 0.3) + k, 1 + k, t, treppe(w, B.gesims, "east"))
            for y in range(1, 1 + k):
                w.setze(-_r(L * 0.3) + k, y, t, B.wand(-_r(L * 0.3) + k, y, t, 0.3))
    hohl(w, 2)
    return w


# ============================================================================ 5 Wasserburg


def wasserburg(seed, g=2):
    """Wasserburg: quadratische Anlage auf einer Insel im breiten Graben, vier Ecktürme, Torbau mit Brücke,
    Innenhof mit Kapelle und Herrenhaus."""
    w = _welt(seed)
    B = stile(w, seed, "backstein", "kalk")
    u = U[g]
    h = _r(13 * u + 4, 9)
    H = _r(7 * u + 3, 5)
    gw = _r(6 * u + 2, 4)
    gelaende(w, h + gw + _r(8 * u, 5), art="wiese")
    wasserflaeche(w, [(x, z) for x in range(-h - gw - 2, h + gw + 3) for z in range(-h - gw - 2, h + gw + 3)
                      if max(abs(x), abs(z)) > h + 2])
    hofboden(w, rechteck(-h + 2, -h + 2, h - 2, h - 2), "pflaster")
    for x in range(-h - 2, h + 3):
        for z in range(-h - 2, h + 3):
            if max(abs(x), abs(z)) > h - 1:
                w.setze(x, 0, z, B.sockel(x, 0, z, 0.0))
    ecken = [(-h, -h), (h, -h), (h, h), (-h, h)]
    for i in range(4):
        mauer(w, B, ecken[i], ecken[(i + 1) % 4], H, dick=3, y0=1, mitte=(0, 0))
    for (x, z) in ecken:
        eckturm(w, B, x, z, 1, H + _r(7 * u, 4), max(2.0, 3.0 * u), dach="glocke" if _stil(seed) else "kegel")
    P.turm(w, B.st, 0, h, 1, H + _r(6 * u, 3), max(2.0, 2.6 * u), form="eckig", dach="pyramide", fahne=B.banner)
    tor(w, B, 0, h, 1, 3, _r(3 * u + 1, 3), achse="z", tiefe=_r(2.6 * u + 1, 2))
    for z in range(h + 3, h + gw + 3):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b(f"{B.holz}_planks"))
        w.setze(-2, 2, z, w.b(f"{B.holz}_fence", north=True, south=True, east=False, west=False, waterlogged=False))
        w.setze(2, 2, z, w.b(f"{B.holz}_fence", north=True, south=True, east=False, west=False, waterlogged=False))
    # Herrenhaus und Kapelle
    P.gebaeude(w, B.st, -h + 3, -h + 3, h - 3, -h + 3 + _r(6 * u + 2, 5), y0=1, etagen=2, eh=_r(3 * u + 2, 4),
               dach="walm", tuer="south")
    kx = -h + 3 + _r(3 * u, 2)
    P.gebaeude(w, B.st, kx - 2, _r(h * 0.15), kx + 2, _r(h * 0.15) + _r(6 * u + 2, 5), y0=1, etagen=1,
               eh=_r(5 * u + 2, 5), dach="sattel", first_x=False, tuer="east", gauben=False, kamine=0)
    P.turm(w, B.st, kx, _r(h * 0.15), 1, _r(10 * u + 6), 1.3, form="eckig", dach="nadel", krone=False,
           fahne=None)
    brunnen(w, B, _r(h * 0.35), _r(h * 0.35))
    hofleben(w, B, [(x, 1, z) for x in range(-h + 2, h - 1) for z in range(-h + 2, h - 1)], 0.03)
    hohl(w, 2)
    return w


# ============================================================================ 6 Bergfeste


def bergfeste(seed, g=2):
    """Bergfeste auf einem schroffen Felssporn: Mauern folgen der Felskante, Türme an den Spitzen, ein
    Serpentinenweg führt hinauf, oben Hauptturm und Hallen."""
    w = _welt(seed)
    B = stile(w, seed, "tief", "nord")
    u = U[g]
    rng = w.rng
    R = 16 * u + 6
    Hf = _r(14 * u + 5)
    fels = Mat(w, ["stone", "andesite", "tuff", "cobblestone", "stone", "gravel", "diorite"], kontrast=1.4)
    r_n = Rauschen(w, 4)
    oben = {}
    for x in range(-int(R) - 5, int(R) + 6):
        for z in range(-int(R) - 5, int(R) + 6):
            d = math.hypot(x * 0.8, z * 1.1)
            Rr = R * (0.85 + 0.3 * r_n(x, 0, z))
            if d > Rr + 6:
                continue
            if d <= Rr:
                hh = Hf
            else:
                hh = Hf * (1 - (d - Rr) / 6) ** 0.6 * (0.7 + 0.5 * r_n(x, 3, z))
            for y in range(0, int(hh) + 1):
                w.setze(x, y, z, fels(x, y, z, y / Hf))
            if d <= Rr:
                oben[(x, z)] = Hf
            elif hh > 1 and rng.random() < 0.3:
                w.setze(x, int(hh) + 1, z, w.b("grass") if rng.random() < 0.6 else w.b("fern"))
    # Mauer entlang des Randes
    n = 9
    pts = []
    for i in range(n):
        a = i / n * 2 * math.pi
        rr = R * (0.85 + 0.3 * r_n(math.cos(a) * R, 0, math.sin(a) * R)) - 2
        pts.append((round(math.cos(a) * rr / 0.8), round(math.sin(a) * rr / 1.1)))
    H = _r(6 * u + 3, 4)
    for i in range(n):
        mauer(w, B, pts[i], pts[(i + 1) % n], H, dick=3, y0=Hf + 1, mitte=(0, 0))
    for i, (x, z) in enumerate(pts):
        if i % 2 == 0:
            eckturm(w, B, x, z, Hf + 1, H + _r(5 * u, 3), max(1.6, 2.3 * u), dach="kegel")
    hofboden(w, [(x, z) for (x, z) in oben if math.hypot(x, z) < R * 0.6])
    for (x, z) in [(x, z) for (x, z) in oben if math.hypot(x, z) < R * 0.6]:
        w.bloecke[(x, Hf, z)] = w.bloecke.pop((x, 0, z), w.b("cobblestone"))
    P.turm(w, B.st, 0, -_r(R * 0.2), Hf + 1, _r(20 * u + 6), max(2.4, 3.4 * u), form="rund", dach="nadel",
           fahne=B.banner)
    P.gebaeude(w, B.st, _r(R * 0.05), _r(R * 0.0), _r(R * 0.55), _r(R * 0.35), y0=Hf + 1, etagen=2,
               eh=_r(3 * u + 2, 4), dach="sattel", tuer="west")
    # Serpentinenweg
    x, z, y = round(R * 1.15), 0, 1
    for k in range(Hf * 3):
        if y >= Hf + 1:
            break
        for d in (-1, 0, 1):
            w.setze(x, y - 1, z + d, w.b("cobblestone") if (k + d) % 4 else w.b("gravel"))
            for yy in range(y, y + 3):
                if (x, yy, z + d) in w.bloecke and yy < Hf + 1:
                    w.bloecke.pop((x, yy, z + d), None)
        if k % 2 == 0:
            y += 1
        x -= 1 if (k // (Hf // 2 + 1)) % 2 == 0 else -1
        x = max(-int(R), min(int(R * 1.2), x))
        z += 0
    hohl(w, 3)
    return w


# ============================================================================ 7 Märchenschloss


def maerchenschloss(seed, g=2):
    """Märchenschloss: weiße Mauern, viele schlanke Türme verschiedener Höhe mit spitzen Hauben,
    Erker, Brücken zwischen den Türmen, Hauptbau mit Mansarddach und ein Schlossgarten."""
    w = _welt(seed)
    B = stile(w, seed, "maerchen", "rot")
    u = U[g]
    rng = w.rng
    h = _r(9 * u + 3, 6)
    gelaende(w, h + _r(16 * u, 8), art="wiese", wege=[((0, h), (0, h + 18))], dichte=1.4)
    P.gebaeude(w, B.st, -h, -h // 2, h, h // 2, y0=1, etagen=3, eh=_r(3 * u + 2, 4), dach="mansarde", tuer="south",
               pilaster=3)
    tuerme = [(-h - 2, -h // 2 - 2, 1.0, 26), (h + 2, -h // 2 - 2, 1.0, 30), (-h - 2, h // 2 + 2, 0.8, 20),
              (h + 2, h // 2 + 2, 0.8, 22), (0, -h // 2 - 3, 1.3, 40), (-h // 2, h // 2 + 2, 0.6, 16),
              (h // 2, -h // 2 - 4, 0.6, 34)]
    for (x, z, rf, hh) in tuerme:
        P.turm(w, B.st, x, z, 1, _r(hh * u * 0.9 + 4), max(1.3, 2.2 * u * rf), dach="nadel",
               fahne=B.banner if rng.random() < 0.7 else None, gauben=True)
    # Erker an den Seiten
    for x in (-h + 2, h - 2):
        P.turm(w, B.st, x, h // 2 + 1, _r(5 * u + 3), _r(6 * u + 3), max(1.0, 1.2 * u), dach="kegel", krone=False,
               fahne=None, schiessscharten=False)
    # Garten mit Hecken und Brunnen
    gz = h // 2 + _r(5 * u, 3)
    for x in range(-h, h + 1):
        for z in range(gz, gz + _r(10 * u, 6)):
            if (x + z) % 7 == 0 or abs(x) == h:
                w.setze(x, 1, z, laub(w, "oak"))
            elif (x * 3 + z) % 11 == 0:
                w.setze(x, 1, z, w.b(["rose_bush" if False else "poppy", "allium", "azure_bluet"][abs(x) % 3]))
    brunnen(w, B, 0, gz + _r(5 * u, 3))
    hohl(w, 2)
    return w


# ============================================================================ 8 Wachturm


def wachturm(seed, g=1):
    """Wachturm: hoher schlanker Turm mit hölzernem Wehrerker (Hurde) oben, Signalfeuer, Leiter und
    kleiner Wachstube am Fuß."""
    w = _welt(seed)
    B = stile(w, seed, "moos", "rot")
    u = U[g]
    R = max(1.8, 2.5 * u)
    H = _r(24 * u + 8)
    gelaende(w, _r(R + 9 * u, 6), art="wiese")
    top = P.turm(w, B.st, 0, 0, 1, H, R, form="achteck", dach="platt", krone=False, fenster=8)
    # Holz-Hurde rundum
    for x, z in kreisrand(R + 1.5):
        for y in range(H - 1, H + 3):
            if y == H - 1:
                w.setze(x, y, z, w.b(f"{B.holz}_planks"))
            elif y == H + 2:
                w.setze(x, y, z, w.b(f"{B.holz}_slab", type="bottom", waterlogged=False))
            elif (x + z) % 3 == 0:
                w.setze(x, y, z, w.b(f"stripped_{B.holz}_log", axis="y"))
            elif y == H:
                w.setze(x, y, z, w.b(f"{B.holz}_planks"))
    for x, z in kreisrand(R + 2.5):
        w.setze(x, H - 2, z, w.b(f"{B.holz}_stairs", facing=GEGEN[zur_mitte(x, z)], half="top", shape="straight",
                                 waterlogged=False) if False else w.b(f"{B.holz}_fence", north=False, south=False,
                                                                     east=False, west=False, waterlogged=False))
    # Dach der Hurde
    for k in range(int(R) + 3):
        for x, z in kreisrand(R + 2.5 - k):
            w.setze(x, H + 3 + k, z, B.dach.voll(x, H + 3 + k, z))
    w.setze(0, H + 3 + int(R) + 3, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    # Wachstube
    P.gebaeude(w, P.Stil(w, wand="holz_dunkel", sockel="graustein", gesims="stone_brick", dach="schindel",
                         holz=B.holz, laeden=True), int(R) + 1, -2, int(R) + 6, 2, y0=1, etagen=1, eh=4,
               dach="sattel", first_x=False, tuer="south", gauben=False)
    hofleben(w, B, [(x, 1, z) for x in range(-int(R) - 5, -int(R) - 1) for z in range(-3, 4)], 0.25)
    hohl(w, 2)
    return w


# ============================================================================ 9 Sternfestung


def sternfestung(seed, g=2):
    """Sternfestung: fünfeckiger Wall mit spitzen Bastionen, Graben, Kasematten und Zitadelle mit Kommandantur
    und Glockenturm in der Mitte."""
    w = _welt(seed)
    B = stile(w, seed, "backstein", "sand")
    u = U[g]
    R = _r(22 * u + 6, 14)
    H = _r(5 * u + 3, 4)
    n = 5
    gelaende(w, R + _r(14 * u, 8), art="wiese")
    aussen = []
    for i in range(n * 2):
        a = i / (n * 2) * 2 * math.pi - math.pi / 2
        rr = R * (1.0 if i % 2 == 0 else 0.68)
        aussen.append((round(math.cos(a) * rr), round(math.sin(a) * rr)))
    # Graben um den Stern (einfacher Ring)
    wasserflaeche(w, [(x, z) for x, z in scheibe(R + 5) if math.hypot(x, z) > R + 1])
    for i in range(len(aussen)):
        mauer(w, B, aussen[i], aussen[(i + 1) % len(aussen)], H, dick=4, y0=1, mitte=(0, 0), scharten=False)
    # Erdwall innen
    for x, z in scheibe(R * 0.62):
        w.setze(x, 0, z, w.b("grass_block", snowy=False))
    for i in range(0, len(aussen), 2):
        x, z = aussen[i]
        w.setze(x, H + 2, z, w.b("lantern", hanging=False, waterlogged=False))
    # Zitadelle
    hz = _r(5 * u + 2, 4)
    P.gebaeude(w, B.st, -hz * 2, -hz, hz * 2, hz, y0=1, etagen=2, eh=_r(3 * u + 2, 4), dach="walm", tuer="south",
               pilaster=3)
    P.turm(w, B.st, 0, -hz - 2, 1, _r(16 * u + 8), max(1.6, 2.0 * u), form="eckig", dach="zwiebel", krone=False,
           fahne=B.banner)
    # Kanonen-Stellungen (Kessel mit Fass)
    for i in range(0, len(aussen), 2):
        x, z = aussen[i]
        mx, mz = round(x * 0.85), round(z * 0.85)
        w.setze(mx, H + 1, mz, w.b("anvil", facing="north"))
    tor(w, B, 0, R - _r(R * 0.32), 1, 3, _r(3 * u + 1, 3), achse="z", tiefe=3, gitter=True)
    hohl(w, 2)
    return w


# ============================================================================ 10 Palas


def palas(seed, g=1):
    """Palas: prächtiger Wohn- und Saalbau der Burg – hohe Spitzbogenfenster, Freitreppe, Erkertürmchen,
    steiles Dach mit Gauben und Kaminen, davor ein Paradeplatz."""
    w = _welt(seed)
    B = stile(w, seed, "kalk", "schwarz")
    u = U[g]
    L = _r(10 * u + 4, 7)
    T = _r(5 * u + 3, 4)
    gelaende(w, L + _r(10 * u, 6), art="wiese", wege=[((0, T), (0, L + 10))])
    hofboden(w, rechteck(-L, T + 2, L, T + _r(8 * u, 4)))
    pst = P.Stil(w, wand=B.st.wand, sockel=B.st.sockel, gesims=B.gesims, dach=B.dach, holz=B.holz,
                 laeden=False, fensterart="bogen")
    top = P.gebaeude(w, pst, -L, -T, L, T, y0=1, etagen=2, eh=_r(4 * u + 2, 5), dach="sattel", steil=True,
                     tuer="south", sockel_h=2, pilaster=3, kamine=2)
    for sx in (-1, 1):
        P.turm(w, B.st, sx * (L + 1), T + 1, 1, top - 2, max(1.3, 1.8 * u), dach="nadel", krone=False,
               fahne=B.banner)
    for x in range(-L, L + 1, 4):
        fahne_haengend(w, B, x, _r(4 * u + 2, 5) * 2, T + 1, _r(4 * u, 2))
    hohl(w, 2)
    return w


# ============================================================================ 11 Motte (Holzburg)


def motte(seed, g=1):
    """Turmhügelburg: aufgeschütteter Hügel mit Holzturm und Palisade, davor die Vorburg mit Hütten,
    Gatter und Brücke über den Graben."""
    w = _welt(seed)
    B = stile(w, seed, "moos", "nord")
    u = U[g]
    rng = w.rng
    Rh = _r(9 * u + 3, 6)
    Hh = _r(6 * u + 2, 4)
    gelaende(w, Rh * 2 + _r(10 * u, 5), art="wiese")
    for x, z in scheibe(Rh + 3):
        d = math.hypot(x, z)
        hh = Hh * max(0.0, min(1.0, (Rh + 2 - d) / 4))
        for y in range(0, int(hh) + 1):
            w.setze(x, y, z, w.b("grass_block", snowy=False) if y == int(hh) else w.b("dirt"))
    holz = B.holz
    # Palisade auf dem Hügel
    for x, z in kreisrand(Rh - 1):
        for y in range(Hh + 1, Hh + 4 + (x + z) % 2):
            w.setze(x, y, z, w.b(f"{holz}_log", axis="y"))
        w.setze(x, Hh + 4 + (x + z) % 2, z, w.b(f"{holz}_fence", north=False, south=False, east=False, west=False,
                                                 waterlogged=False))
    # Holzturm
    T = _r(3 * u + 1, 2)
    Ht = _r(12 * u + 4, 8)
    for y in range(Hh + 1, Hh + 1 + Ht):
        for x in range(-T, T + 1):
            for z in range(-T, T + 1):
                if max(abs(x), abs(z)) == T:
                    if abs(x) == T and abs(z) == T:
                        w.setze(x, y, z, w.b(f"{holz}_log", axis="y"))
                    elif (y - Hh) % 5 == 0:
                        w.setze(x, y, z, w.b(f"stripped_{holz}_log", axis="x" if abs(z) == T else "z"))
                    else:
                        w.setze(x, y, z, w.b(f"{holz}_planks"))
    P.walmdach(w, P.Dach(w, "schindel"), -T, -T, T, T, Hh + Ht, ue=2, steil=True)
    # Vorburg (Bailey)
    vz = Rh + _r(8 * u + 4, 6)
    for x, z in kreisrand(_r(8 * u + 4, 6), 0, vz):
        if z < Rh:
            continue
        for y in range(1, 4):
            w.setze(x, y, z, w.b(f"{holz}_log", axis="y"))
    for (hx, hz) in ((-4, vz), (3, vz + 2)):
        P.gebaeude(w, P.Stil(w, wand="lehm", sockel="graustein", gesims="stone_brick", dach="schindel", holz=holz,
                             fachwerk=True), hx - 2, hz - 2, hx + 2, hz + 1, y0=1, etagen=1, eh=3, dach="sattel",
                   tuer="south", gauben=False)
    hofleben(w, B, [(x, 1, z) for x, z in scheibe(_r(7 * u + 3, 5), 0, vz)], 0.08)
    hohl(w, 2)
    return w


# ============================================================================ 12 Ordensburg


def ordensburg(seed, g=2):
    """Backstein-Ordensburg: gewaltiger Konventbau um einen Kreuzganghof, Treppengiebel, Ecktürmchen,
    hoher Glockenturm und Wehrgang mit Zinnen."""
    w = _welt(seed)
    B = stile(w, seed, "backstein", "rot")
    u = U[g]
    h = _r(11 * u + 4, 8)
    gelaende(w, h + _r(10 * u, 6), art="wiese")
    hofboden(w, rechteck(-h + 5, -h + 5, h - 5, h - 5), "wiese")
    eh = _r(4 * u + 2, 4)
    for (x0, z0, x1, z1) in ((-h, -h, h, -h + 4), (-h, h - 4, h, h), (-h, -h + 5, -h + 4, h - 5),
                             (h - 4, -h + 5, h, h - 5)):
        P.gebaeude(w, B.st, x0, z0, x1, z1, y0=1, etagen=2, eh=eh, dach="sattel", tuer="south" if z0 > 0 else
                   "north", gauben=False, kamine=0)
    # Kreuzgang-Arkaden
    for x in range(-h + 5, h - 4):
        for z in (-h + 5, h - 5):
            if x % 3 == 0:
                for y in range(1, 4):
                    w.setze(x, y, z, B.wand(x, y, z, 0.3))
            w.setze(x, 4, z, w.b(f"{B.gesims}_slab" if B.gesims in WAENDE_MAUER else "stone_brick_slab",
                                 type="bottom", waterlogged=False))
    # Treppengiebel an den Ecken
    for sx in (-1, 1):
        for sz in (-1, 1):
            P.turm(w, B.st, sx * h, sz * h, 1, 2 * eh + 6, max(1.4, 1.8 * u), form="achteck", dach="nadel",
                   krone=False, fahne=None)
    P.turm(w, B.st, 0, -h - 2, 1, _r(28 * u + 10), max(2.2, 3.0 * u), form="eckig", dach="nadel", fahne=B.banner)
    brunnen(w, B, 0, 0)
    hohl(w, 2)
    return w


# ============================================================================ 13 Klippenburg


def klippenburg(seed, g=2):
    """Klippenburg: auf einer Meeresklippe, mit Leuchtturm-Bergfried, Brandungsfelsen, Bootssteg
    und Treppe hinab zum Wasser."""
    w = _welt(seed)
    B = stile(w, seed, "nord", "kalk")
    u = U[g]
    rng = w.rng
    Hk = _r(14 * u + 4)
    R = 14 * u + 5
    fels = Mat(w, ["stone", "andesite", "tuff", "diorite", "stone", "cobblestone", "mossy_cobblestone"], kontrast=1.4)
    r_n = Rauschen(w, 3)
    for x in range(-int(R) - 10, int(R) + 11):
        for z in range(-int(R) - 4, int(R) + 16):
            d = math.hypot(x, z * 0.9)
            land = d < R * (0.85 + 0.3 * r_n(x, 0, z))
            if not land:
                if z > 0 or d < R + 10:
                    w.setze(x, 0, z, w.b("water", level=0))
                    w.setze(x, -1, z, w.b("sand") if rng.random() < 0.7 else w.b("gravel"))
                continue
            hh = Hk if d < R * 0.75 else Hk * (0.6 + 0.4 * r_n(x, 5, z))
            for y in range(-1, int(hh) + 1):
                w.setze(x, y, z, fels(x, y, z, max(0, y) / Hk))
            w.setze(x, int(hh), z, w.b("grass_block", snowy=False) if rng.random() < 0.7 else fels(x, int(hh), z, 1))
    yo = Hk + 1
    h = _r(R * 0.45)
    ecken = [(-h, -h), (h, -h), (h, h), (-h, h)]
    for i in range(4):
        mauer(w, B, ecken[i], ecken[(i + 1) % 4], _r(5 * u + 3, 4), dick=3, y0=yo, mitte=(0, 0))
    P.turm(w, B.st, h, h, yo, _r(22 * u + 6), max(2.4, 3.2 * u), form="rund", dach="platt")
    # Leuchtfeuer
    for dy in range(2):
        w.setze(h, yo + _r(22 * u + 6) + 1 + dy, h, w.b("glowstone" if dy == 0 else "sea_lantern"))
    for (x, z) in ecken[:3]:
        eckturm(w, B, x, z, yo, _r(8 * u + 4), max(1.6, 2.2 * u), dach="kegel")
    P.gebaeude(w, B.st, -h + 2, -h + 2, h - 3, -h + 2 + _r(4 * u + 2, 4), y0=yo, etagen=2, eh=_r(3 * u + 2, 4),
               dach="sattel", tuer="south")
    # Steg und Treppe
    for z in range(int(R), int(R) + 10):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b(f"{B.holz}_planks"))
        if z % 3 == 0:
            w.setze(-2, 1, z, w.b(f"{B.holz}_log", axis="y"))
            w.setze(2, 1, z, w.b(f"{B.holz}_log", axis="y"))
            w.setze(2, 2, z, w.b("lantern", hanging=False, waterlogged=False))
    x, y, z = 0, 1, int(R) - 1
    while y < yo and z > 0:
        for d in (-1, 0, 1):
            w.setze(x + d, y, z, treppe(w, B.gesims, "south"))
            for yy in range(y + 1, y + 4):
                w.bloecke.pop((x + d, yy, z), None)
        y += 1
        z -= 1
    hohl(w, 3)
    return w


# ============================================================================ 14 Burgruine


def burgruine(seed, g=2):
    """Burgruine: zerfallene Ringmauern, eingestürzter Bergfried, Mauerreste des Palas, alles von Moos,
    Ranken, Farnen und jungen Bäumen überwuchert, dazwischen Schutthalden."""
    import baeume as Bm
    w = _welt(seed)
    B = stile(w, seed, "moos", "tief")
    u = U[g]
    rng = w.rng
    R = _r(15 * u + 4, 10)
    H = _r(7 * u + 3, 5)
    n = 6
    pts = [(round(math.cos(i / n * 2 * math.pi) * R), round(math.sin(i / n * 2 * math.pi) * R)) for i in range(n)]
    for i in range(n):
        mauer(w, B, pts[i], pts[(i + 1) % n], H, dick=3, y0=1, mitte=(0, 0))
    for (x, z) in pts[::2]:
        eckturm(w, B, x, z, 1, H + _r(5 * u, 3), max(1.6, 2.2 * u), dach="kegel", fahne=False)
    P.turm(w, B.st, -_r(R * 0.3), 0, 1, _r(22 * u + 6), max(2.4, 3.4 * u), form="eckig", dach="platt", fahne=None)
    P.gebaeude(w, B.st, 0, -_r(R * 0.5), _r(R * 0.6), -_r(R * 0.1), y0=1, etagen=2, eh=_r(3 * u + 2, 4),
               dach="flach", gauben=False, kamine=0)
    betroffen = set(b for b in w.bloecke.values() if b)
    zerfall(w, betroffen, Rauschen(w, 3), _r(26 * u + 8), staerke=0.75, boden=2)
    gelaende(w, R + _r(8 * u, 5), art="wald", dichte=1.3)
    # Schutthalden
    r_s = Rauschen(w, 2)
    for x, z in scheibe(R + 3):
        if r_s(x, 0, z) > 0.68 and w.frei(x, 1, z):
            for y in range(1, 1 + int((r_s(x, 0, z) - 0.68) * 12)):
                w.setze(x, y, z, w.b(["cobblestone", "mossy_cobblestone", "gravel", "stone_bricks"][(x * 7 + y + z) % 4]))
    # Moos und Ranken
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 1 and w.frei(x, y + 1, z) and rng.random() < 0.35:
            w.setze(x, y + 1, z, w.b("moss_carpet"))
        if y > 3 and rng.random() < 0.04:
            for dx, dz, sd in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
                if w.frei(x + dx, y, z + dz):
                    for k in range(int(2 + rng.random() * 6)):
                        if not w.frei(x + dx, y - k, z + dz) or y - k < 1:
                            break
                        w.setze(x + dx, y - k, z + dz, w.b("vine", **{q: q == sd for q in ("north", "east", "south",
                                                                                           "west")}, up=False))
                    break
    for i in range(int(4 * u) + 1):
        a = rng.random() * 2 * math.pi
        d = rng.random() * R * 0.8
        einfuegen(w, Bm.ARTEN["birke" if rng.random() < 0.5 else "eiche"][1](int(rng.integers(1, 10 ** 6)), 0),
                  round(math.cos(a) * d), 0, round(math.sin(a) * d))
    hohl(w, 2)
    return w


# ============================================================================ 15 Barbakane


def barbakane(seed, g=1):
    """Barbakane: runder Vorbau vor dem Haupttor mit eigenem Tor, Wehrgang, Schießscharten-Kranz und
    Pechnasen, dahinter ein Stück Hauptmauer mit Torturm."""
    w = _welt(seed)
    B = stile(w, seed, "backstein", "schwarz")
    u = U[g]
    R = _r(8 * u + 4, 6)
    H = _r(7 * u + 4, 5)
    gelaende(w, R + _r(14 * u, 8), art="wiese", wege=[((0, R), (0, R + 16))])
    for x, z in scheibe(R):
        d = math.hypot(x, z)
        for y in range(1, H + 1):
            if d > R - 2.5:
                w.setze(x, y, z, B.wand(x, y, z, y / (H + 3)))
    for x, z in kreisrand(R + 1):
        w.setze(x, H, z, treppe(w, B.gesims, zur_mitte(x, z), "top"))
        w.setze(x, H + 1, z, B.wand(x, H + 1, z, 0.9))
        if (x + z) % 2 == 0:
            w.setze(x, H + 2, z, B.wand(x, H + 2, z, 0.95))
    for x, z in kreisrand(R):
        a = math.atan2(z, x)
        for y in (3, 6):
            if y < H and abs(math.sin(a * 6)) < 0.15:
                w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
    for x, z in scheibe(R - 2.5):
        w.bloecke.pop((x, 1, z), None)
    hofboden(w, scheibe(R - 2), "pflaster")
    tor(w, B, 0, R - 1, 1, 3, _r(3 * u + 2, 4), achse="z", tiefe=2)
    # Hauptmauer mit Torturm dahinter
    mauer(w, B, (-R - 10, -R - 2), (R + 10, -R - 2), H + 3, dick=3, y0=1, mitte=(0, -50))
    P.turm(w, B.st, 0, -R - 2, 1, H + _r(9 * u, 5), max(2.5, 3.4 * u), form="eckig", dach="pyramide", fahne=B.banner)
    tor(w, B, 0, -R - 2, 1, 3, _r(3 * u + 2, 4), achse="z", tiefe=_r(3.4 * u + 1, 3))
    hohl(w, 2)
    return w


# ============================================================================ 16 Brückenburg


def brueckenburg(seed, g=2):
    """Brückenburg: steinerne Bogenbrücke über einen Fluss, in der Mitte ein Torturm mit Fallgitter,
    an beiden Enden Brückentore, Pfeiler mit Eisbrechern."""
    w = _welt(seed)
    B = stile(w, seed, "kalk", "tief")
    u = U[g]
    L = _r(24 * u + 8)
    fb = _r(14 * u + 4, 8)
    Hb = _r(6 * u + 3, 5)
    gelaende(w, L + 6, art="wiese")
    for x in range(-L - 4, L + 5):
        for z in range(-fb, fb + 1):
            for y in range(-2, 1):
                w.setze(x, y, z, w.b("water", level=0))
            w.setze(x, -3, z, w.b("gravel") if (x + z) % 4 else w.b("sand"))
    br = 3
    boegen = max(2, int(fb * 2 / 8))
    for z in range(-fb - 3, fb + 4):
        for x in range(-br - 1, br + 2):
            # Bogenform: zwischen Pfeilern ausgespart
            t = (z + fb) / (2 * fb) * boegen
            fr = t - math.floor(t)
            unter = Hb - 1 - int(max(0, math.sin(fr * math.pi)) * (Hb - 2)) if abs(z) <= fb else 0
            for y in range(-2 if abs(z) <= fb else 0, Hb + 1):
                if y >= unter or abs(z) > fb or fr < 0.12 or fr > 0.88:
                    w.setze(x, y, z, B.wand(x, y, z, (y + 2) / (Hb + 6)))
            if abs(x) == br + 1:
                w.setze(x, Hb + 1, z, B.mauerwand())
            else:
                w.setze(x, Hb, z, w.b("cobblestone") if (x + z) % 3 else w.b("stone_bricks"))
    # Torturm in der Mitte und Brückentore
    P.turm(w, B.st, 0, 0, Hb + 1, _r(14 * u + 6), br + 1.6, form="eckig", dach="pyramide", fahne=B.banner)
    tor(w, B, 0, 0, Hb + 1, 3, _r(3 * u + 2, 4), achse="z", tiefe=br + 2)
    for sz in (-1, 1):
        z = sz * (fb + 3)
        for sx in (-1, 1):
            P.turm(w, B.st, sx * (br + 2), z, Hb + 1, _r(6 * u + 4), 1.3, form="rund", dach="kegel", krone=False,
                   fahne=None)
    for z in range(-fb, fb + 1, 4):
        w.setze(br, Hb + 2, z, w.b("lantern", hanging=False, waterlogged=False))
    hohl(w, 2)
    return w


# ============================================================================ 17 Stadttor


def stadttor(seed, g=1):
    """Stadttor: hohes Torgebäude mit Uhr und Glockentürmchen, flankiert von zwei Rundtürmen,
    Mauerstümpfe, Wachhäuschen und Marktstand davor."""
    w = _welt(seed)
    B = stile(w, seed, "sand", "nord")
    u = U[g]
    hb = _r(5 * u + 2, 4)
    H = _r(16 * u + 6, 10)
    gelaende(w, hb + _r(18 * u, 10), art="wiese", wege=[((0, -20), (0, 20))])
    P.gebaeude(w, B.st, -hb, -_r(3 * u + 2, 3), hb, _r(3 * u + 2, 3), y0=1, etagen=3, eh=_r(H / 3, 4),
               dach="walm", tuer="south", gauben=False, kamine=0)
    tor(w, B, 0, 0, 1, 3 if u < 1.5 else 5, _r(4 * u + 2, 4), achse="z", tiefe=_r(3 * u + 2, 3))
    # Uhr
    yu = 1 + 2 * _r(H / 3, 4) + 1
    zf = _r(3 * u + 2, 3) + 1
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if abs(dx) + abs(dy) <= 3:
                w.setze(dx, yu + dy, zf, w.b("gold_block") if abs(dx) + abs(dy) == 3 or (dx == 0 and dy >= 0) or
                        (dy == 0 and dx >= 0) else w.b("smooth_quartz"))
    for sx in (-1, 1):
        eckturm(w, B, sx * (hb + 3), 0, 1, H + _r(6 * u, 4), max(2.2, 3.0 * u), dach="kegel")
        mauer(w, B, (sx * (hb + 6), 0), (sx * (hb + _r(16 * u, 10)), 0), _r(H * 0.55), dick=3, y0=1, mitte=(0, -20))
    hohl(w, 2)
    return w


# ============================================================================ 18 Wohnturm


def wohnturm(seed, g=1):
    """Wohnturm (Tower House): L-förmiger Turm mit verputzten Wänden, Treppengiebeln, Ecktürmchen auf
    Kragsteinen, schmalen Fenstern und ummauertem Garten."""
    w = _welt(seed)
    B = stile(w, seed, "maerchen", "kalk")
    u = U[g]
    a = _r(4 * u + 2, 3)
    H = _r(14 * u + 6, 9)
    gelaende(w, a + _r(12 * u, 7), art="wiese")
    pst = P.Stil(w, wand="putz" if _stil(seed) == 0 else "kalkstein", sockel="graustein", gesims=B.gesims,
                 dach="schiefer", holz=B.holz, laeden=False)
    eh = _r(H / 4, 3)
    P.gebaeude(w, pst, -a, -a, a, a, y0=1, etagen=4, eh=eh, dach="sattel", steil=True, tuer="south", gauben=False,
               kamine=1, fenster_abstand=4)
    P.gebaeude(w, pst, a + 1, -a, a + 1 + a, 0, y0=1, etagen=3, eh=eh, dach="sattel", steil=True, tuer="east",
               gauben=False, kamine=0, fenster_abstand=4)
    for sx in (-1, 1):
        x = sx * (a + 1) if sx < 0 else a + 1 + a + 1
        P.turm(w, B.st, x, a + 1, 1 + 4 * eh - _r(4 * u, 2), _r(5 * u + 3), max(1.0, 1.3 * u), dach="kegel",
               krone=False, fahne=None, schiessscharten=False)
    # Gartenmauer
    for x in range(-a - 6, 2 * a + 8):
        for z in (a + 7, -a - 5):
            for y in range(1, 3):
                w.setze(x, y, z, B.sockel(x, y, z, 0.3))
    for z in range(-a - 5, a + 8):
        for x in (-a - 6, 2 * a + 7):
            for y in range(1, 3):
                w.setze(x, y, z, B.sockel(x, y, z, 0.3))
    for x in range(-1, 2):
        for y in (1, 2):
            w.bloecke.pop((x, y, a + 7), None)
    hohl(w, 2)
    return w


# ============================================================================ 19 Belagerungslager


def belagerungslager(seed, g=2):
    """Belagerungslager: Zelte in Wappenfarben, ein großes Trebuchet, Palisaden, Lagerfeuer, Waffenständer,
    Vorratswagen und ein Kommandozelt mit Bannern."""
    w = _welt(seed)
    B = stile(w, seed, "nord", "rot")
    u = U[g]
    rng = w.rng
    R = _r(18 * u + 6, 12)
    gelaende(w, R + 4, art="wiese", dichte=0.6)
    # Zelte
    def zelt(cx, cz, r, h, farben):
        for y in range(1, h + 1):
            rr = r * (1 - (y - 1) / h)
            for x, z in kreisrand(max(0.4, rr), cx, cz):
                w.setze(x, y, z, w.b(farben[(int(math.atan2(z - cz, x - cx) * 3) + 10) % 2]))
        w.setze(cx, h + 1, cz, w.b(f"{B.holz}_fence", north=False, south=False, east=False, west=False,
                                   waterlogged=False))
        w.setze(cx, h + 2, cz, w.b(farben[0]))
        for k in range(2):
            w.bloecke.pop((cx, 1 + k, cz + int(r)), None)
    plaetze = []
    for i in range(int(8 * u) + 3):
        for _ in range(30):
            a = rng.random() * 2 * math.pi
            d = R * (0.35 + 0.55 * rng.random())
            x, z = round(math.cos(a) * d), round(math.sin(a) * d)
            r = 2.2 + rng.random() * 1.3
            if all(math.hypot(x - px, z - pz) > r + pr + 1.5 for px, pz, pr in plaetze):
                plaetze.append((x, z, r))
                zelt(x, z, r, int(r * 1.6), [B.banner[i % 2], "white_wool"])
                break
    zelt(0, -_r(R * 0.25), 4.5 * min(u, 1.6), int(6 * min(u, 1.6)), [B.banner[0], B.banner[1]])
    # Trebuchet
    tx, tz = 0, _r(R * 0.35)
    hh = _r(7 * u + 4, 6)
    for sx in (-2, 2):
        for k in range(hh):
            w.setze(sx, 1 + k, tz - k // 3, w.b(f"{B.holz}_log", axis="y"))
            w.setze(sx, 1 + k, tz + k // 3, w.b(f"{B.holz}_log", axis="y"))
        for z in range(tz - 3, tz + 4):
            w.setze(sx, 1, z, w.b(f"stripped_{B.holz}_log", axis="z"))
    for x in range(-2, 3):
        w.setze(x, hh, tz, w.b(f"stripped_{B.holz}_log", axis="x"))
    for k in range(-hh // 2, hh + 3):
        w.setze(0, hh + k // 2, tz - k, w.b(f"{B.holz}_log", axis="z"))
    for dx in (-1, 0, 1):
        for dy in (0, 1):
            w.setze(dx, hh - 2 + dy, tz + hh // 2 + 1, w.b("cobblestone"))
    w.setze(0, hh + (hh + 2) // 2 - 1, tz - hh - 2, w.b("chain", axis="y", waterlogged=False))
    # Palisade (halber Ring) und Lagerfeuer
    for x, z in kreisrand(R):
        if z < R * 0.3:
            for y in range(1, 4):
                w.setze(x, y, z, w.b(f"{B.holz}_log", axis="y"))
            w.setze(x, 4, z, w.b(f"{B.holz}_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False))
    for i in range(int(3 * u) + 1):
        a = rng.random() * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        if w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if w.frei(x + 2 * dx, 1, z + 2 * dz):
                    w.setze(x + 2 * dx, 1, z + 2 * dz, w.b(f"stripped_{B.holz}_log", axis="x" if dx else "z"))
    hofleben(w, B, [(x, 1, z) for x, z in scheibe(R - 2)], 0.025)
    hohl(w, 2)
    return w


# ============================================================================ 20 Schlosshof


def schlosshof(seed, g=2):
    """Renaissance-Schloss: vier Flügel mit Mansarddächern um einen Ehrenhof, Arkadengänge, Eckpavillons
    mit Kuppelhauben, Mittelrisalit mit Uhrturm und ein Brunnen im Hof."""
    w = _welt(seed)
    B = stile(w, seed, "marmor", "backstein")
    u = U[g]
    h = _r(14 * u + 5, 10)
    t = _r(3 * u + 2, 3)
    eh = _r(3 * u + 2, 4)
    gelaende(w, h + _r(12 * u, 7), art="wiese", wege=[((0, h), (0, h + 16))], dichte=1.2)
    hofboden(w, rechteck(-h + t + 1, -h + t + 1, h - t - 1, h - t - 1), "pflaster")
    pst = P.Stil(w, wand=B.st.wand, sockel=B.st.sockel, gesims=B.gesims, dach=B.dach, holz=B.holz,
                 laeden=True, fensterart="bogen")
    for (x0, z0, x1, z1, tuer) in ((-h, -h, h, -h + t, "south"), (-h, h - t, -2, h, "north"),
                                   (2, h - t, h, h, "north"), (-h, -h + t + 1, -h + t, h - t - 1, "east"),
                                   (h - t, -h + t + 1, h, h - t - 1, "west")):
        P.gebaeude(w, pst, x0, z0, x1, z1, y0=1, etagen=2, eh=eh, dach="mansarde", tuer=tuer, gauben=True,
                   kamine=1, pilaster=3)
    for sx in (-1, 1):
        for sz in (-1, 1):
            P.turm(w, B.st, sx * h, sz * h, 1, 2 * eh + 3, max(1.8, 2.6 * u), form="eckig", dach="kuppel",
                   krone=False, fahne=None)
    P.turm(w, B.st, 0, -h, 1, 2 * eh + _r(8 * u, 4), max(1.6, 2.2 * u), form="eckig", dach="zwiebel", krone=False,
           fahne=B.banner)
    # Arkaden innen
    for x in range(-h + t + 1, h - t):
        for z in (-h + t + 1,):
            if (x % 3) == 0:
                for y in range(1, eh + 1):
                    w.setze(x, y, z, B.wand(x, y, z, 0.3))
            w.setze(x, eh + 1, z, w.b(f"{B.gesims}_slab" if B.gesims in WAENDE_MAUER else "quartz_slab",
                                      type="bottom", waterlogged=False))
    brunnen(w, B, 0, 0)
    hohl(w, 2)
    return w


BURGEN = {
    "bergfried": ("Bergfried", bergfried),
    "torburg": ("Torburg mit Zugbrücke", torburg),
    "ringburg": ("Ringburg", ringburg),
    "wehrmauer": ("Stadtmauer-Stück", wehrmauer),
    "wasserburg": ("Wasserburg", wasserburg),
    "bergfeste": ("Bergfeste", bergfeste),
    "maerchenschloss": ("Märchenschloss", maerchenschloss),
    "wachturm": ("Wachturm", wachturm),
    "sternfestung": ("Sternfestung", sternfestung),
    "palas": ("Palas", palas),
    "motte": ("Turmhügelburg", motte),
    "ordensburg": ("Ordensburg", ordensburg),
    "klippenburg": ("Klippenburg", klippenburg),
    "burgruine": ("Burgruine", burgruine),
    "barbakane": ("Barbakane", barbakane),
    "brueckenburg": ("Brückenburg", brueckenburg),
    "stadttor": ("Stadttor", stadttor),
    "wohnturm": ("Wohnturm", wohnturm),
    "belagerungslager": ("Belagerungslager", belagerungslager),
    "schlosshof": ("Renaissance-Schloss", schlosshof),
}

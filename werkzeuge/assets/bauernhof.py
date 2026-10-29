"""Bauernhof & Landleben – Höfe, Scheunen, Ställe, Felder, Gärten, Obst, Wein, Hopfen, Bienen, Kornspeicher,
Käserei, Hofladen, Erntefest, Maibaum, Taubenschlag, Gutshof und Schäferkarren. Boden y = 0."""

from __future__ import annotations

import math

import pracht as P
import wald2
from flora import _neu, _r, _stil, linie
from haeuser2 import (POOL2, fassstapel, heuhaufen, karren, kisten, koppel, misthaufen, obstbaum, vordach,
                      waescheleine, werkbank, ziehbrunnen)
from lib import einfuegen
from pracht import gelaende

U = [0.6, 1.0, 1.7, 2.8]


def st_(w, seed, a, b=None, **kw):
    d = dict(POOL2[a if _stil(seed) == 0 or b is None else b])
    d.update(kw)
    return P.Stil(w, **d)


def zf(w, holz="oak", **v):
    d = dict(north=False, south=False, east=False, west=False, waterlogged=False)
    d.update(v)
    return w.b(f"{holz}_fence", **d)


def feld(w, x0, z0, x1, z1, frucht="wheat", alter=7, wasser=True, rand=True):
    """Acker mit Furchen, Bewässerungsgraben und Feldrand."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if wasser and (z - z0) % 9 == 4:
                w.setze(x, 0, z, w.b("water", level=0))
                continue
            w.setze(x, 0, z, w.b("farmland", moisture=7))
            if frucht == "gemischt":
                f = ["wheat", "carrots", "potatoes", "beetroots"][((x - x0) // 3) % 4]
            else:
                f = frucht
            a = 3 if f == "beetroots" else alter
            if f in ("pumpkin", "melon"):
                if (x + z) % 3 == 0:
                    w.setze(x, 1, z, w.b(f))
                else:
                    w.setze(x, 1, z, w.b(f"{f}_stem", age=7))
            else:
                w.setze(x, 1, z, w.b(f, age=a))
    if rand:
        for x in range(x0 - 1, x1 + 2):
            for z in (z0 - 1, z1 + 1):
                w.setze(x, 0, z, w.b("dirt_path") if (x + z) % 3 else w.b("coarse_dirt"))
        for z in range(z0 - 1, z1 + 2):
            for x in (x0 - 1, x1 + 1):
                w.setze(x, 0, z, w.b("dirt_path") if (x + z) % 3 else w.b("coarse_dirt"))


def garbe(w, x, z):
    """Getreidegarben, zu einer Hocke gestellt."""
    for dx, dz in ((0, 0), (1, 0), (0, 1), (1, 1)):
        w.setze(x + dx, 1, z + dz, w.b("hay_block", axis="y"))
    w.setze(x, 2, z, w.b("hay_block", axis="y"))


def tier_futter(w, x, z):
    w.setze(x, 1, z, w.b("hay_block", axis="y"))
    w.setze(x + 1, 1, z, w.b("water_cauldron", level=3))


def zaunzug(w, pts, holz="oak"):
    alle = []
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        n = max(abs(bx - ax), abs(bz - az), 1)
        for k in range(n + 1):
            alle.append((round(ax + (bx - ax) * k / n), round(az + (bz - az) * k / n)))
    s = set(alle)
    for (x, z) in s:
        w.setze(x, 1, z, zf(w, holz, north=(x, z - 1) in s, south=(x, z + 1) in s, east=(x + 1, z) in s,
                            west=(x - 1, z) in s))


def hofpflaster(w, x0, z0, x1, z1):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, 0, z, w.b(["cobblestone", "gravel", "mossy_cobblestone", "coarse_dirt", "dirt_path"][
                (x * 7 + z * 3) % 5]))
            w.bloecke.pop((x, 1, z), None)


def scheunenbau(w, seed, x0, z0, x1, z1, H=6, farbe="holz_rot"):
    """Große Scheune mit Steinsockel, Holzwänden, hohem Satteldach und Tennentor."""
    st = st_(w, seed, farbe, "holz_blau", laeden=False, blumen=0)
    P.gebaeude(w, st, x0, z0, x1, z1, y0=1, etagen=1, eh=H, dach="sattel", first_x=(x1 - x0) >= (z1 - z0),
               tuer="south", gauben=False, kamine=0, steil=True)
    cx = (x0 + x1) // 2
    for x in range(cx - 1, cx + 2):
        for y in range(1, 5):
            w.bloecke.pop((x, y, z1), None)
    for x in (cx - 2, cx + 2):
        for y in range(1, 5):
            w.setze(x, y, z1 + 1, w.b("spruce_trapdoor", facing="south", half="bottom", open=True, powered=False,
                                      waterlogged=False))
    for x in range(cx - 1, cx + 2):
        w.setze(x, H + 1, z1, w.b("hay_block", axis="y"))
    w.setze(cx, H + 2, z1 + 1, w.b("lantern", hanging=True, waterlogged=False))


def weide_deko(w, x0, z0, x1, z1, baum=True):
    """Belebt eine Weide: Heuballen, Futtertröge, Feldsteine, Disteln, ein Schattenbaum."""
    rng = w.rng
    for k in range(max(2, (x1 - x0) * (z1 - z0) // 40)):
        x, z = int(rng.integers(x0 + 1, x1)), int(rng.integers(z0 + 1, z1))
        r = rng.random()
        if r < 0.35:
            w.setze(x, 1, z, w.b("hay_block", axis="x" if k % 2 else "z"))
        elif r < 0.55:
            w.setze(x, 1, z, w.b("mossy_cobblestone" if k % 2 else "cobblestone"))
        elif r < 0.75:
            w.setze(x, 1, z, w.b("sweet_berry_bush", age=1))
        else:
            hohes_gras = w.b("tall_grass", half="lower")
            w.setze(x, 1, z, hohes_gras)
            w.setze(x, 2, z, w.b("tall_grass", half="upper"))
    if baum:
        einfuegen(w, wald2.laubbaum(int(rng.integers(1, 10 ** 6)), "oak", H=6 + int(rng.integers(3))),
                  (x0 + x1) // 2 + 2, 0, (z0 + z1) // 2)
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            if (x * 7 + z * 13) % 11 == 0:
                w.setze(x, 0, z, w.b("coarse_dirt"))
            elif (x * 5 + z * 3) % 17 == 0:
                w.setze(x, 0, z, w.b("dirt_path"))


# ============================================================================ Höfe & Gebäude

def bauernhof(seed, g=2):
    """Bauernhof: Wohnhaus, Scheune und Stall um einen gepflasterten Hof mit Misthaufen, Brunnen, Karren und
    Wäscheleine, dahinter Felder und eine Koppel."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    gelaende(w, R, art="wiese", dichte=0.35)
    hofpflaster(w, -8, -6, 8, 6)
    st = st_(w, seed, "fachwerk_weiss", "stroh_lehm")
    P.gebaeude(w, st, -8, -14, 0, -7, y0=1, etagen=2, eh=4, dach="sattel", tuer="south", gauben=True, kamine=1)
    scheunenbau(w, seed, 3, -16, 13, -7, H=7)
    stb = st_(w, seed, "holz_rot", "bruchstein", laeden=False)
    P.gebaeude(w, stb, -16, -4, -9, 6, y0=1, etagen=1, eh=4, dach="sattel", first_x=False, tuer="east",
               gauben=False, kamine=0)
    misthaufen(w, 5, 3)
    ziehbrunnen(w, 0, 0)
    karren(w, 3, -3)
    waescheleine(w, -7, 8, 5)
    feld(w, 10, 4, R - 3, R - 4, "gemischt")
    koppel(w, -R + 3, 9, -8, R - 4)
    for k in range(3):
        obstbaum(w, -4 + k * 5, R - 3)
    return w


def scheune(seed, g=2):
    """Große Scheune: eine rote Holzscheune mit Steinsockel und Heuboden, offenes Tennentor mit Heuwagen,
    Hühner-Leiter, Wetterhahn und Heuballen davor."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.35)
    a, b = _r(5 * u + 2), _r(7 * u + 3)
    scheunenbau(w, seed, -a, -b, a, b, H=_r(6 * u + 2))
    karren(w, -1, b + 3)
    for k in range(3):
        heuhaufen(w, a + 4, -b + 3 + k * 4)
    w.setze(0, _r(6 * u + 2) + a + 4, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False), False)
    return w


def kuhstall(seed, g=1):
    """Kuhstall: ein langer Stall mit Halbtüren und Futterraufen, eine Weide mit Tränke, Melkschemel und
    Milchkannen."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.4)
    st = st_(w, seed, "bruchstein", "holz_blau", laeden=False)
    a = _r(6 * u + 2)
    P.gebaeude(w, st, -a, -R + 2, a, -R + 8, y0=1, etagen=1, eh=4, dach="sattel", tuer="south", gauben=False,
               kamine=0)
    for x in range(-a + 1, a, 2):
        w.setze(x, 2, -R + 8, w.b("spruce_trapdoor", facing="south", half="top", open=False, powered=False,
                                  waterlogged=False))
    koppel(w, -R + 2, -R + 10, R - 2, R - 2)
    weide_deko(w, -R + 2, -R + 10, R - 2, R - 2)
    for k in range(3):
        w.setze(-3 + k, 1, -R + 9, w.b("cauldron") if k % 2 else w.b("water_cauldron", level=3))
    w.setze(a + 2, 1, -R + 9, w.b("oak_slab", type="bottom", waterlogged=False))
    return w


def schweinestall(seed, g=1):
    """Schweinestall: eine niedrige Hütte mit Schlammsuhle, Futtertrog aus Holz, Zaun aus Latten und ein Haufen
    Möhren und Rüben."""
    w = _neu(seed)
    u = U[g]
    R = _r(11 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.3)
    st = st_(w, seed, "stroh_lehm", "holz_rot", laeden=False)
    P.gebaeude(w, st, -4, -R + 2, 3, -R + 6, y0=1, etagen=1, eh=3, dach="sattel", tuer="south", gauben=False,
               kamine=0)
    koppel(w, -R + 2, -R + 7, R - 2, R - 2, tier_futter=False)
    weide_deko(w, -R + 2, -R + 7, R - 2, -R + 10, baum=False)
    for x in range(-R // 2, R // 2):
        for z in range(0, R // 2):
            if math.hypot(x, z - R // 4) < R * 0.3:
                w.setze(x, 0, z, w.b("mud") if (x + z) % 4 else w.b("water", level=0))
    for x in range(-R + 3, -R + 8):
        w.setze(x, 1, -R + 8, w.b("spruce_slab", type="bottom", waterlogged=False))
    for k in range(4):
        w.setze(R - 4, 1, -R + 9 + k, w.b(["carrots", "beetroots", "potatoes", "carrots"][k], age=3 if k == 1 else 7))
    return w


def huehnerhof(seed, g=1):
    """Hühnerhof: ein Hühnerhaus auf Stelzen mit Hühnerleiter, Legenester, eingezäunter Auslauf mit Sandbad,
    Körnerfutter und ein Hahn auf dem Zaunpfahl (als Wetterfahne)."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.3)
    for x in range(-2, 3):
        for z in range(-2, 3):
            if abs(x) == 2 and abs(z) == 2:
                w.setze(x, 1, z, w.b("spruce_log", axis="y"))
            w.setze(x, 2, z, w.b("spruce_planks"))
    st = st_(w, seed, "holz_rot", "holz_blau", laeden=False, blumen=0)
    P.gebaeude(w, st, -2, -2, 2, 2, y0=3, etagen=1, eh=3, dach="sattel", tuer="south", gauben=False, kamine=0,
               sockel_h=0)
    for k in range(3):
        w.setze(0, 1 + k // 2, 3 + (2 - k), w.b("spruce_slab", type="bottom" if k % 2 else "top", waterlogged=False))
    zaunzug(w, [(-R + 2, -R + 2), (R - 2, -R + 2), (R - 2, R - 2), (-R + 2, R - 2), (-R + 2, -R + 2)], "birch")
    for x in range(R // 3, R // 3 + 3):
        for z in range(R // 3, R // 3 + 3):
            w.setze(x, 0, z, w.b("sand"))
    for k in range(4):
        w.setze(-R // 2 + k, 1, R // 2, w.b("composter", level=3))
    w.setze(R - 2, 2, R - 2, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return w


def schafweide(seed, g=2):
    """Schafweide: eine hügelige Weide mit Trockenmauern, einem offenen Unterstand, Pferch zum Scheren, Wollballen
    und einem Hirtenstab am Gatter."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.4)
    for x in range(-R + 2, R - 1):
        for z in (-R + 2, R - 2):
            for y in (1, 2):
                if (x + y) % 7:
                    w.setze(x, y, z, w.b("mossy_cobblestone" if (x + z) % 3 else "cobblestone"))
    for z in range(-R + 2, R - 1):
        for x in (-R + 2, R - 2):
            for y in (1, 2):
                w.setze(x, y, z, w.b("mossy_cobblestone" if (x + z) % 3 else "cobblestone"))
    for x in range(-2, 3):
        w.bloecke.pop((x, 1, R - 2), None)
        w.bloecke.pop((x, 2, R - 2), None)
    st = st_(w, seed, "bruchstein", "stroh_lehm", laeden=False)
    P.gebaeude(w, st, -4, -R + 3, 4, -R + 7, y0=1, etagen=1, eh=3, dach="sattel", tuer="south", gauben=False,
               kamine=0)
    for x in range(-3, 4):
        for y in range(1, 4):
            w.bloecke.pop((x, y, -R + 7), None)
    koppel(w, R // 3, -R // 3, R - 4, R // 4, tier_futter=True)
    weide_deko(w, -R + 3, -R + 9, R // 3 - 2, R - 3)
    for k in range(4):
        w.setze(-R // 2 + k, 1, R // 2, w.b("white_wool"))
        w.setze(-R // 2 + k, 2, R // 2, w.b("white_wool")) if k % 2 else None
    return w


def pferdestall(seed, g=2):
    """Pferdestall: ein Stall mit Boxen, Sattelkammer und Heuboden, davor ein Reitplatz mit Sand, Hindernissen und
    Tränke."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.3)
    st = st_(w, seed, "fachwerk_gruen", "holz_blau", laeden=True)
    a = _r(7 * u + 2)
    P.gebaeude(w, st, -a, -R + 2, a, -R + 8, y0=1, etagen=1, eh=4, dach="sattel", tuer="south", gauben=True,
               kamine=0)
    for x in range(-a + 1, a, 3):
        w.setze(x, 1, -R + 8, w.b("oak_fence_gate", facing="south", in_wall=False, open=False, powered=False))
    for x in range(-R + 3, R - 2):
        for z in range(-R + 11, R - 2):
            w.setze(x, 0, z, w.b("sand") if (x + z) % 5 else w.b("coarse_dirt"))
            w.bloecke.pop((x, 1, z), None)
    zaunzug(w, [(-R + 3, -R + 11), (R - 3, -R + 11), (R - 3, R - 3), (-R + 3, R - 3), (-R + 3, -R + 11)], "spruce")
    for k in range(3):
        x = -R // 2 + k * R // 2
        for dx in (-1, 1):
            w.setze(x + dx, 1, 2, zf(w, "spruce"))
        w.setze(x, 2, 2, w.b("spruce_slab", type="bottom", waterlogged=False))
        w.setze(x - 1, 2, 2, zf(w, "spruce", east=True))
        w.setze(x + 1, 2, 2, zf(w, "spruce", west=True))
    tier_futter(w, R - 6, -R + 12)
    for k in range(3):
        einfuegen(w, wald2.laubbaum(int(w.rng.integers(1, 10 ** 6)), "oak", H=6), -R - 1 + k * R, 0, R)
    return w


def kornspeicher(seed, g=1):
    """Kornspeicher: ein Holzspeicher auf pilzförmigen Steinstelzen gegen Mäuse, mit Außentreppe, Säcken und
    Getreidegarben ringsum."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.35)
    a, b = _r(3 * u + 1, 2), _r(2.5 * u + 1, 2)
    for x in (-a, a):
        for z in (-b, b):
            w.setze(x, 1, z, w.b("cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
                                 waterlogged=False))
            w.setze(x, 2, z, w.b("stone_slab", type="bottom", waterlogged=False))
    st = st_(w, seed, "holz_rot", "stroh_lehm", laeden=False, blumen=0)
    P.gebaeude(w, st, -a, -b, a, b, y0=3, etagen=1, eh=4, dach="sattel", tuer="south", gauben=False, kamine=0,
               sockel_h=0)
    for k in range(3):
        w.setze(0, 1 + k, b + 3 - k, w.b("spruce_stairs", facing="north", half="bottom", shape="straight",
                                         waterlogged=False))
    for k in range(4):
        garbe(w, -R + 3 + k * 3, R - 4)
    return w


def heuschober(seed, g=1):
    """Heuschober: eine abgemähte Wiese mit großen, spitz aufgesetzten Heuschobern auf Stangen, Heurechen und
    einem hölzernen Heuwagen."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.1)
    rng = w.rng
    n = int(4 + 4 * u)
    for i in range(n):
        a = i * 2.39996
        d = R * 0.75 * math.sqrt((i + 0.5) / n)
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        h = _r(4 * u + 2)
        for y in range(1, h + 1):
            r = 1.8 * u * (1 - (y - 1) / h) ** 0.8 + 0.5
            for dx in range(-3, 4):
                for dz in range(-3, 4):
                    if dx * dx + dz * dz <= r * r:
                        w.setze(cx + dx, y, cz + dz, w.b("hay_block", axis="y"))
        w.setze(cx, h + 1, cz, zf(w, "spruce"))
    karren(w, 0, 0)
    return w


def kaeserei(seed, g=1):
    """Käserei: ein Steinhaus mit Kühlkeller, Käselaiben auf Regalen, Butterfass, Milchkannen und einer Almbank vor
    dem Haus."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.4)
    st = st_(w, seed, "bruchstein", "fachwerk_weiss")
    a, b = _r(4 * u + 1, 3), _r(3 * u + 1, 2)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=4, dach="sattel", tuer="south", gauben=False, kamine=1)
    vordach(w, st, -a, a, b, 4, "south", 2)
    for x in range(-a + 1, a):
        w.setze(x, 1, b + 2, w.b("yellow_terracotta") if x % 2 else w.b("barrel", facing="up", open=False))
    w.setze(-a - 2, 1, 0, w.b("cauldron"))
    w.setze(a + 2, 1, 0, w.b("spruce_stairs", facing="west", half="bottom", shape="straight", waterlogged=False))
    return w


def hofladen(seed, g=1):
    """Hofladen: ein kleiner Verkaufsstand mit Markise, Körben voller Kürbisse, Äpfel und Gemüse, Honiggläser,
    Kreidetafel und Blumen."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.35)
    st = st_(w, seed, "holz_rot", "holz_blau", laeden=True, blumen=0.8)
    P.gebaeude(w, st, -3, -4, 3, 0, y0=1, etagen=1, eh=3, dach="sattel", tuer="south", gauben=False, kamine=0)
    for x in range(-3, 4):
        w.setze(x, 4, 1, w.b("red_wool" if x % 2 else "white_wool"))
        w.setze(x, 3, 2, w.b("red_wool" if x % 2 else "white_wool"))
    ware = ["pumpkin", "melon", "hay_block", "honey_block", "carved_pumpkin", "barrel"]
    for k, x in enumerate(range(-3, 4)):
        n = ware[k % len(ware)]
        w.setze(x, 1, 2, w.b(n, axis="y") if n == "hay_block" else w.b(n, facing="south") if n == "carved_pumpkin"
                else w.b("barrel", facing="up", open=True) if n == "barrel" else w.b(n))
    for x in (-4, 4):
        for y in (1, 2):
            w.setze(x, y, 2, zf(w, "spruce"))
    w.setze(0, 1, 4, w.b("oak_sign", rotation=8, waterlogged=False))
    return w


def ententeich(seed, g=1):
    """Ententeich: ein runder Dorfteich mit Entenhaus auf dem Wasser, Schilf, Trauerweide, Bank und Steg."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.35)
    r = R * 0.6
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            if math.hypot(x, z) < r:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("clay"))
                w.bloecke.pop((x, 1, z), None)
            elif math.hypot(x, z) < r + 1.2 and (x + z) % 2:
                w.setze(x, 1, z, w.b("sugar_cane", age=0))
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            w.setze(dx, 1, dz, w.b("spruce_planks"))
    w.setze(0, 2, 0, w.b("spruce_planks"))
    for dx in (-1, 1):
        w.setze(dx, 2, 0, w.b("spruce_stairs", facing="east" if dx < 0 else "west", half="bottom", shape="straight",
                              waterlogged=False))
    einfuegen(w, wald2.weide(seed, H=_r(6 * u + 3)), round(r + 3), 0, -round(r * 0.6))
    for z in range(round(r * 0.3), round(r) + 2):
        w.setze(0, 1, z, w.b("oak_slab", type="bottom", waterlogged=False))
    return w


def erntefest(seed, g=2):
    """Erntefest: lange Festtafeln mit Bänken, ein Erntekranz auf Stangen, Kürbis-Laternen, Fässer mit Most,
    Strohballen zum Sitzen und Wimpelketten."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.2)
    for k in range(3):
        z = -R // 2 + k * R // 2
        for x in range(-R // 2, R // 2):
            w.setze(x, 1, z, w.b("spruce_fence", north=False, south=False, east=True, west=True, waterlogged=False))
            w.setze(x, 2, z, w.b("spruce_pressure_plate", powered=False) if x % 3 else
                    w.b("candle", candles=2, lit=True, waterlogged=False))
            for dz in (-1, 1):
                w.setze(x, 1, z + dz, w.b("spruce_slab", type="bottom", waterlogged=False))
    for y in range(1, _r(8 * u + 3)):
        w.setze(R // 2 + 3, y, 0, w.b("spruce_log", axis="y"))
    for k in range(10):
        a = k / 10 * 6.28
        w.setze(R // 2 + 3 + round(math.cos(a) * 2), _r(8 * u + 3) - 1, round(math.sin(a) * 2),
                w.b(["hay_block", "orange_wool", "yellow_wool", "red_wool"][k % 4], **({"axis": "y"} if k % 4 == 0
                                                                                     else {})))
    for x in range(-R // 2, R // 2, 4):
        w.setze(x, 1, R // 2 + 3, w.b("jack_o_lantern", facing="south"))
        w.setze(x + 2, 1, R // 2 + 3, w.b("hay_block", axis="x"))
    fassstapel(w, -R // 2 - 4, -2, 3)
    for x in range(-R // 2, R // 2 + 1):
        if x % 2:
            w.setze(x, 5, -R // 2 - 2, w.b(["red_wool", "yellow_wool", "blue_wool", "lime_wool"][x % 4]))
    for x in (-R // 2 - 1, R // 2 + 1):
        for y in range(1, 6):
            w.setze(x, y, -R // 2 - 2, w.b("spruce_log", axis="y"))
    return w


def maibaum(seed, g=1):
    """Maibaum: ein hoher, blau-weiß geringelter Baum mit Kranz, Zunftschildern und Bändern auf dem Dorfplatz, darum
    Bänke und eine Tanzfläche."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.2)
    for x in range(-R + 2, R - 1):
        for z in range(-R + 2, R - 1):
            if math.hypot(x, z) < R * 0.6:
                w.setze(x, 0, z, w.b("cobblestone" if (x + z) % 3 else "gravel"))
    H = _r(18 * u + 6)
    for y in range(1, H):
        w.setze(0, y, 0, w.b("blue_concrete" if (y // 2) % 2 else "white_concrete") if stil_farbe(seed) else
                w.b("stripped_spruce_log", axis="y") if y % 3 else w.b("green_wool"))
    for k in range(12):
        a = k / 12 * 6.28
        w.setze(round(math.cos(a) * 2), H - 2, round(math.sin(a) * 2), w.b("spruce_leaves", persistent=True,
                                                                           distance=1, waterlogged=False))
        linie(w, (0, H - 2, 0), (math.cos(a) * R * 0.55, 1, math.sin(a) * R * 0.55),
              w.b(["red_wool", "yellow_wool", "blue_wool", "white_wool"][k % 4]))
    for k in range(4):
        y = round(H * (0.4 + k * 0.12))
        w.setze(1, y, 0, w.b("oak_wall_sign", facing="east", waterlogged=False))
        w.setze(-1, y, 0, w.b("oak_wall_sign", facing="west", waterlogged=False))
    w.setze(0, H, 0, w.b("spruce_leaves", persistent=True, distance=1, waterlogged=False))
    return w


def stil_farbe(seed):
    return _stil(seed) == 0


def hofbrunnen(seed, g=0):
    """Hofbrunnen: ein Laufbrunnen mit hölzernem Röhrentrog, Schwengelpumpe, Eimern und einer Linde als
    Schattenspender."""
    w = _neu(seed)
    u = U[g]
    R = _r(7 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.3)
    for x in range(-2, 3):
        for z in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_planks") if abs(x) == 2 or abs(z) == 1 else w.b("water", level=0))
    for y in range(1, 4):
        w.setze(-3, y, 0, w.b("spruce_log", axis="y"))
    w.setze(-2, 3, 0, w.b("spruce_trapdoor", facing="east", half="top", open=False, powered=False, waterlogged=False))
    w.setze(-2, 2, 0, w.b("water", level=0))
    w.setze(3, 1, 1, w.b("cauldron"))
    einfuegen(w, wald2.laubbaum(seed, "oak", H=_r(7 * u + 4)), -R + 3, 0, -R + 3)
    return w


def taubenschlag(seed, g=1):
    """Taubenschlag: ein runder Turm aus Bruchstein mit Fluglöchern in Reihen, spitzem Schindeldach und einer
    Taubenwetterfahne, umgeben von Bauerngarten."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.4)
    st = st_(w, seed, "bruchstein", "fachwerk_weiss", laeden=False)
    H = _r(9 * u + 4)
    r = _r(2.5 * u + 1.5, 2)
    P.turm(w, st, 0, 0, 1, H, r, dach="kegel", krone=False, fenster=99, spitze="lightning_rod", schiessscharten=False)
    for y in range(4, H, 2):
        for k in range(int(r * 6)):
            a = k / (r * 6) * 6.28
            if k % 2 == (y // 2) % 2:
                w.setze(round(math.cos(a) * r), y, round(math.sin(a) * r), w.b("spruce_trapdoor", facing="north",
                                                                                 half="top", open=False,
                                                                                 powered=False, waterlogged=False))
    return w


def gutshof(seed, g=2):
    """Gutshof: ein stattliches Herrenhaus mit Freitreppe und Walmdach, zwei Wirtschaftsflügel um einen
    Ehrenhof, Torhaus mit Uhr, Lindenallee und Gemüsegarten."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    gelaende(w, R, art="wiese", dichte=0.25)
    sth = st_(w, seed, "patrizier", "backstein_rot")
    a = _r(7 * u + 3)
    P.gebaeude(w, sth, -a, -R + 4, a, -R + 4 + _r(5 * u + 3), y0=1, etagen=2, eh=4, dach="walm", tuer="south",
               gauben=True, kamine=2, pilaster=2)
    stw = st_(w, seed, "fachwerk_weiss", "bruchstein")
    for sx in (-1, 1):
        P.gebaeude(w, stw, sx * (a + 2) - (4 if sx > 0 else 0) * 0 + (0 if sx > 0 else -4),
                   -R + 4 + _r(5 * u + 3) + 2, sx * (a + 2) + (4 if sx > 0 else 0), 4, y0=1, etagen=1, eh=4,
                   dach="sattel", first_x=False, tuer="east" if sx < 0 else "west", gauben=False, kamine=0)
    hofpflaster(w, -a, -R + 4 + _r(5 * u + 3) + 1, a, 4)
    ziehbrunnen(w, 0, -R // 4)
    for z in range(6, R - 1, 4):
        for sx in (-3, 3):
            einfuegen(w, wald2.laubbaum(int(w.rng.integers(1, 10 ** 6)), "oak", H=_r(6 * u + 3), breit=0.7), sx, 0,
                      z)
    feld(w, a + 8, 6, R - 2, R - 2, "gemischt")
    return w


def schaeferkarren(seed, g=0):
    """Schäferkarren: ein kleiner gewölbter Wohnwagen auf eisernen Rädern mit Ofenrohr, Treppe und Hütehunde-
    Napf, auf einer Bergwiese."""
    w = _neu(seed)
    u = U[g]
    R = _r(7 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.45)
    L = _r(3 * u + 2)
    for x in range(-L, L + 1):
        for z in (-1, 0, 1):
            w.setze(x, 2, z, w.b("spruce_planks"))
            for y in (3, 4):
                if abs(z) == 1 or abs(x) == L:
                    w.setze(x, y, z, w.b("green_terracotta" if _stil(seed) == 0 else "blue_terracotta") if y == 3
                            or (x + z) % 3 else w.b("glass_pane", north=False, south=False, east=True, west=True,
                                                     waterlogged=False))
        w.setze(x, 5, 0, w.b("dark_oak_planks"))
        for z in (-1, 1):
            w.setze(x, 5, z, w.b("dark_oak_stairs", facing="south" if z < 0 else "north", half="bottom",
                                 shape="straight", waterlogged=False))
    for x in (-L + 1, L - 1):
        for z in (-2, 2):
            w.setze(x, 1, z, w.b("polished_basalt", axis="z"))
    w.setze(L - 1, 6, 0, w.b("cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
                             waterlogged=False))
    w.setze(L - 1, 7, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for k in range(2):
        w.setze(-L - 1 - k, 1 + (1 - k), 0, w.b("spruce_slab", type="bottom", waterlogged=False))
    return w


# ============================================================================ Felder & Gärten

def getreidefeld(seed, g=2):
    """Getreidefeld: reifer Weizen in Reihen mit Bewässerungsgraben, ein abgeernteter Streifen mit Garbenhocken,
    Mohn und Kornblumen am Feldrand, eine Vogelscheuche."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    gelaende(w, R + 2, art="wiese", dichte=0.25)
    feld(w, -R, -R, R, round(R * 0.2), "wheat")
    for x in range(-R, R + 1):
        for z in range(round(R * 0.2) + 2, R):
            w.setze(x, 0, z, w.b("farmland", moisture=2) if (x + z) % 3 else w.b("coarse_dirt"))
            w.bloecke.pop((x, 1, z), None)
    for x in range(-R + 2, R - 1, 4):
        garbe(w, x, round(R * 0.6))
    for x in range(-R, R + 1, 2):
        w.setze(x, 1, -R - 1, w.b("poppy" if x % 4 else "cornflower"), False)
    for y in range(1, 4):
        w.setze(0, y, -R // 2, zf(w, "spruce"))
    w.setze(0, 4, -R // 2, w.b("carved_pumpkin", facing="south"))
    for dx in (-1, 1):
        w.setze(dx, 3, -R // 2, zf(w, "spruce", east=dx < 0, west=dx > 0))
    return w


def gemuesegarten(seed, g=1):
    """Gemüsegarten: Hochbeete mit Möhren, Kartoffeln, Roter Bete, Kohl und Kürbis, Rankgitter mit Bohnen, ein
    Geräteschuppen, Regentonne und Komposthaufen."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.3)
    fr = ["carrots", "potatoes", "beetroots", "wheat", "carrots", "pumpkin"]
    for i in range(6):
        x0 = -R + 3 + (i % 3) * (2 * R // 3)
        z0 = -R + 3 + (i // 3) * R
        bx, bz = max(2, R // 3 - 2), max(2, R // 2 - 2)
        for x in range(x0 - 1, x0 + bx + 1):
            for z in range(z0 - 1, z0 + bz + 1):
                if x in (x0 - 1, x0 + bx) or z in (z0 - 1, z0 + bz):
                    w.setze(x, 1, z, w.b("spruce_planks"))
        feld(w, x0, z0, x0 + bx - 1, z0 + bz - 1, fr[i], wasser=False, rand=False)
        for x in range(x0, x0 + bx):
            for z in range(z0, z0 + bz):
                b = w.bloecke.pop((x, 1, z), None)
                w.setze(x, 1, z, w.b("farmland", moisture=7))
                if b is not None:
                    w.setze(x, 2, z, b)
    st = st_(w, seed, "holz_blau", "holz_rot", laeden=False)
    P.gebaeude(w, st, R - 5, -R + 1, R - 1, -R + 4, y0=1, etagen=1, eh=3, dach="sattel", tuer="west",
               gauben=False, kamine=0)
    w.setze(R - 6, 1, -R + 1, w.b("water_cauldron", level=3))
    misthaufen(w, -R + 2, R - 2)
    return w


def obstgarten(seed, g=2):
    """Obstgarten: Reihen von Apfel- und Kirschbäumen in Blüte oder voller Früchte, Leitern an den Stämmen,
    Erntekisten, Bienenstöcke und eine Mostpresse."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.45)
    for x in range(-R + 3, R - 2, 7):
        for z in range(-R + 3, R - 2, 7):
            obstbaum(w, x, z, bluete=_stil(seed) == 1)
            if (x + z) % 2 == 0:
                w.setze(x + 2, 1, z, w.b("barrel", facing="up", open=True))
    for k in range(3):
        w.setze(-R + 2, 1, -R + 4 + k * 3, w.b("beehive", facing="east", honey_level=3))
    werkbank(w, R - 4, R - 3, gegenstaende=("barrel", "composter", "barrel"))
    return w


def weinberg(seed, g=2):
    """Weinberg: ein Südhang mit Terrassen aus Trockenmauern, Rebzeilen an Pfählen mit Trauben, ein Winzerhaus mit
    Kelter und Fässern."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    n = 4
    sh = _r(2 * u + 1)
    for k in range(n):
        z0 = -R + k * (2 * R // n)
        y0 = (n - 1 - k) * sh
        for x in range(-R, R + 1):
            for z in range(z0, z0 + 2 * R // n):
                for y in range(-1, y0 + 1):
                    w.setze(x, y, z, w.b("grass_block", snowy=False) if y == y0 else w.b("dirt"))
                if z == z0 + 2 * R // n - 1 and k < n - 1:
                    for y in range(0, y0 + 1):
                        w.setze(x, y, z, w.b("mossy_cobblestone" if (x + y) % 3 else "cobblestone"))
            for z in range(z0 + 1, z0 + 2 * R // n - 1, 2):
                if x % 4 == 0:
                    for yy in range(y0 + 1, y0 + 3):
                        w.setze(x, yy, z, zf(w, "spruce"))
                else:
                    w.setze(x, y0 + 2, z, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
                    if (x + z) % 3 == 0:
                        w.setze(x, y0 + 1, z, w.b("purple_concrete" if _stil(seed) == 0 else "lime_concrete"))
    st = st_(w, seed, "ocker_blau", "fachwerk_weiss")
    P.gebaeude(w, st, R - 7, R - 8, R - 1, R - 2, y0=1, etagen=2, eh=4, dach="sattel", tuer="west", gauben=False,
               kamine=1)
    fassstapel(w, R - 11, R - 3, 4)
    return w


def hopfengarten(seed, g=1):
    """Hopfengarten: hohe Stangen mit Drahtgerüst, an denen grüne Hopfenranken emporklettern, eine Darre zum
    Trocknen und ein Fuhrwerk mit Säcken."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.25)
    H = _r(8 * u + 4)
    for x in range(-R + 2, R - 1, 3):
        for z in range(-R + 2, R // 2, 3):
            for y in range(1, H + 1):
                w.setze(x, y, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
                if 2 <= y <= H - 1:
                    for dx, dz, f in ((1, 0, "west"), (0, 1, "north")):
                        if (y + x) % 2:
                            w.setze(x + dx, y, z + dz, w.b("vine", **{s: s == f for s in ("north", "south", "east",
                                                                                         "west")}, up=False))
            w.setze(x, H + 1, z, w.b("tripwire", attached=False, disarmed=False, east=True, west=True, north=False,
                                     south=False, powered=False))
    st = st_(w, seed, "backstein_rot", "bruchstein")
    P.turm(w, st, 0, R - 5, 1, _r(5 * u + 3), 2.5, form="eckig", dach="pyramide", krone=False, fenster=2)
    karren(w, -R // 2, R - 3, ladung="white_wool")
    return w


def kuerbisfeld(seed, g=1):
    """Kürbisfeld: Kürbisse und Melonen zwischen Ranken auf dem Acker, ein Stapel geschnitzter Kürbislaternen,
    Strohballen und ein Leiterwagen – Herbststimmung."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R + 2, art="wiese", dichte=0.2)
    feld(w, -R, -R, R, R // 2, "pumpkin")
    for x in range(-R // 2, R // 2, 3):
        w.setze(x, 1, R // 2 + 3, w.b("carved_pumpkin", facing="south") if x % 2 else
                w.b("jack_o_lantern", facing="south"))
        w.setze(x + 1, 1, R // 2 + 3, w.b("hay_block", axis="x"))
    karren(w, R // 2, R // 2 + 5, ladung="pumpkin")
    return w


def kartoffelacker(seed, g=1):
    """Kartoffelacker: lange Dammreihen mit Kartoffelkraut, ein Feldweg, Kartoffelsäcke, Körbe und ein Feuer, in
    dem die ersten Kartoffeln garen."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R + 2, art="wiese", dichte=0.2)
    feld(w, -R, -R, R, R // 2, "potatoes")
    for x in range(-R, R + 1):
        for z in range(R // 2 + 2, R // 2 + 4):
            w.setze(x, 0, z, w.b("dirt_path"))
    for k in range(4):
        w.setze(-3 + k, 1, R // 2 + 5, w.b("brown_wool"))
    w.setze(3, 1, R // 2 + 6, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


def bienenhaus(seed, g=1):
    """Bienenhaus: ein offenes Holzhäuschen mit Regalen voller bunt bemalter Bienenkästen, davor eine
    Blumenwiese, Honigschleuder und Wachskerzen."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    from blumen import WIESENBLUMEN
    gelaende(w, R, art="wiese", dichte=0.6)
    L = _r(4 * u + 2)
    for x in range(-L, L + 1):
        for z in (-2, -1):
            w.setze(x, 0, z, w.b("spruce_planks"))
        for y in (1, 2):
            w.setze(x, y, -2, w.b(["yellow_terracotta", "light_blue_terracotta", "red_terracotta",
                                   "lime_terracotta"][(x + y) % 4]) if x % 2 else w.b("beehive", facing="south",
                                                                                      honey_level=5))
        w.setze(x, 3, -2, w.b("spruce_planks"))
        w.setze(x, 4, -2, w.b("spruce_slab", type="bottom", waterlogged=False))
        w.setze(x, 3, -1, w.b("spruce_slab", type="top", waterlogged=False))
    for x in (-L - 1, L + 1):
        for y in range(1, 4):
            w.setze(x, y, -2, w.b("spruce_log", axis="y"))
    w.setze(0, 1, 2, w.b("cauldron"))
    w.setze(2, 1, 2, w.b("candle", candles=4, lit=True, waterlogged=False))
    return w


BAUERNHOF = {
    "bauernhof": ("Bauernhof", bauernhof),
    "scheune": ("Große Scheune", scheune),
    "kuhstall": ("Kuhstall mit Weide", kuhstall),
    "schweinestall": ("Schweinestall", schweinestall),
    "huehnerhof": ("Hühnerhof", huehnerhof),
    "schafweide": ("Schafweide", schafweide),
    "pferdestall": ("Pferdestall mit Reitplatz", pferdestall),
    "kornspeicher": ("Kornspeicher", kornspeicher),
    "heuschober": ("Heuschober", heuschober),
    "kaeserei": ("Käserei", kaeserei),
    "hofladen": ("Hofladen", hofladen),
    "ententeich": ("Ententeich", ententeich),
    "erntefest": ("Erntefest", erntefest),
    "maibaum": ("Maibaum", maibaum),
    "hofbrunnen": ("Hofbrunnen", hofbrunnen),
    "taubenschlag": ("Taubenschlag", taubenschlag),
    "gutshof": ("Gutshof", gutshof),
    "schaeferkarren": ("Schäferkarren", schaeferkarren),
    "getreidefeld": ("Getreidefeld", getreidefeld),
    "gemuesegarten": ("Gemüsegarten", gemuesegarten),
    "obstgarten": ("Obstgarten", obstgarten),
    "weinberg": ("Weinberg", weinberg),
    "hopfengarten": ("Hopfengarten", hopfengarten),
    "kuerbisfeld": ("Kürbisfeld", kuerbisfeld),
    "kartoffelacker": ("Kartoffelacker", kartoffelacker),
    "bienenhaus": ("Bienenhaus", bienenhaus),
}

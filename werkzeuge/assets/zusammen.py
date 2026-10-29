"""Zusammengelegte Erweiterungen bestehender Kategorien:
HAFEN (→ Küste & Leuchttürme), BASAR (→ Wüstenreich), WINTERDORF (→ Eisreich), TOTENREICH (→ Friedhof & Spuk)."""

from __future__ import annotations

import math

import pracht as P
import wald2
from flora import _lv, _neu, _r, _stil, linie
from haeuser import HAUSPOOL
from lib import Rauschen, einfuegen
from pracht import Mat, gelaende
from wueste_eis import _wueste, flachhaus, kuppel, markise, palme, zelt

U = [0.6, 1.0, 1.7, 2.8]


def zf(w, holz="oak", **v):
    d = dict(north=False, south=False, east=False, west=False, waterlogged=False)
    d.update(v)
    return w.b(f"{holz}_fence", **d)


def stil_haus(w, pool, **kw):
    d = dict(HAUSPOOL[pool])
    d.update(kw)
    return P.Stil(w, **d)


def wasserflaeche(w, x0, z0, x1, z1, tief=2, grund="gravel"):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            for y in range(-tief + 1, 1):
                w.setze(x, y, z, w.b("water", level=0))
            w.setze(x, -tief, z, w.b(grund))
            w.bloecke.pop((x, 1, z), None)


def kaimauer(w, x0, x1, z, M, h=1):
    for x in range(x0, x1 + 1):
        for y in range(-2, h + 1):
            w.setze(x, y, z, M(x, y, z, 0.5))
        if x % 4 == 0:
            w.setze(x, h + 1, z, w.b("cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
                                     waterlogged=False))


# ============================================================================ HAFENSTADT → Küste

def hafenviertel(seed, g=2):
    """Hafenviertel: schmale, hohe Giebelhäuser dicht an dicht am Kai, mit Ladeluken und Seilwinden unter dem First,
    davor Fässer, Netze und ein vertäutes Boot."""
    from boote import fischerboot
    w = _neu(seed)
    u = U[g]
    L = _r(16 * u + 6)
    gelaende(w, L + 4, art="wiese", dichte=0.1)
    M = Mat(w, ["stone_bricks", "cobblestone", "mossy_stone_bricks", "andesite"])
    wasserflaeche(w, -L - 3, 4, L + 3, L + 3)
    kaimauer(w, -L, L, 3, M)
    for x in range(-L, L + 1):
        for z in range(-2, 3):
            w.setze(x, 0, z, w.b("cobblestone" if (x + z) % 3 else "gravel"))
    pools = ["fachwerk_rot", "backstein", "fachwerk_ocker", "putz_blau", "stein_schiefer", "kalk_kupfer"]
    x = -L
    i = 0
    while x + 4 <= L:
        b = 2 + (i % 2)
        st = stil_haus(w, pools[(seed + i) % len(pools)])
        etagen = 2 + (i % 3 == 1)
        P.gebaeude(w, st, x, -10, x + b * 2, -3, y0=1, etagen=etagen, eh=4, dach="sattel", first_x=False,
                   tuer="south", gauben=False, kamine=1, steil=True)
        yt = 1 + etagen * 4
        w.setze(x + b, yt + 1, -2, zf(w, "spruce", north=True))
        w.setze(x + b, yt, -2, w.b("chain", axis="y", waterlogged=False))
        x += b * 2 + 1
        i += 1
    for k in range(4):
        w.setze(-L + 3 + k * 5, 1, 1, w.b("barrel", facing="up", open=False))
    einfuegen(w, fischerboot(seed, max(0, g - 1)), 0, 0, 7)
    return w


def kontorhaus(seed, g=2):
    """Kontorhaus: ein stattliches Handelshaus aus Backstein mit Treppengiebel, Kranbalken, Warenlager im Erdgeschoss
    und Schreibstube darüber, davor Kisten mit Handelsware."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.1)
    st = stil_haus(w, "backstein")
    a, b = _r(4 * u + 2), _r(4 * u + 2)
    et = 3
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=et, eh=4, dach="sattel", first_x=False, tuer="south", gauben=False,
               kamine=1, steil=True)
    yt = 1 + et * 4
    for k in range(a + 1):
        for x in (-a + k, a - k):
            for y in range(yt, yt + (a - k) * 2 // 2 * 2 // 2 + 1):
                w.setze(x, y, b + 1, w.b("bricks"))
        if k % 2 == 0:
            w.setze(-a + k, yt + (a - k) + 1, b + 1, w.b("brick_slab", type="bottom", waterlogged=False))
            w.setze(a - k, yt + (a - k) + 1, b + 1, w.b("brick_slab", type="bottom", waterlogged=False))
    for k in range(3):
        w.setze(0, yt + 1 - k, b + 2 + k, w.b("spruce_log", axis="z")) if k == 0 else None
    w.setze(0, yt - 1, b + 2, w.b("spruce_log", axis="z"))
    w.setze(0, yt - 2, b + 3, w.b("chain", axis="y", waterlogged=False))
    for k in range(4):
        w.setze(-2 + k, 1, b + 3, w.b("barrel", facing="up", open=False) if k % 2 else w.b("chest", facing="south",
                                                                                           type="single",
                                                                                           waterlogged=False))
    return w


def speicherkanal(seed, g=2):
    """Speicherkanal: hohe Lagerhäuser aus rotem Backstein ragen direkt aus einem Kanal, mit Ladeluken und Winden,
    Stegen und einer Bogenbrücke."""
    w = _neu(seed)
    u = U[g]
    L = _r(16 * u + 6)
    gelaende(w, L + 3, art="wiese", dichte=0.0)
    B = _r(3 * u + 2)
    wasserflaeche(w, -L - 3, -B, L + 3, B, tief=3)
    M = Mat(w, ["bricks", "bricks", "mud_bricks", "granite"])
    for sz in (-1, 1):
        x = -L
        while x < L - 3:
            bb = 4 + (x % 3)
            H = _r((9 + (x * 7) % 5) * u * 0.8 + 4)
            z0 = sz * (B + 1)
            z1 = sz * (B + 7)
            for xx in range(x, x + bb):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    for y in range(-2, H):
                        rand = xx in (x, x + bb - 1) or z in (z0, z1)
                        if rand:
                            luke = z == z0 and xx == x + bb // 2 and y % 4 == 2
                            fen = (y % 4 == 2) and not luke and (xx + z) % 2 == 0
                            w.setze(xx, y, z, w.b("spruce_trapdoor", facing="north" if sz > 0 else "south",
                                                  half="top", open=False, powered=False, waterlogged=False) if luke
                                    else w.b("glass_pane", north=True, south=True, east=True, west=True,
                                             waterlogged=False) if fen and False else
                                    w.b("dark_oak_planks") if fen else M(xx, y, z, y / H))
                    w.setze(xx, H, z, w.b("waxed_oxidized_cut_copper"))
            w.setze(x + bb // 2, H - 1, z0 - sz, w.b("spruce_log", axis="z"))
            x += bb + 1
    for x in range(-2, 3):
        for k in range(2 * B + 3):
            z = -B - 1 + k
            y = 1 + round(math.sin(k / (2 * B + 2) * math.pi) * 2)
            w.setze(x, y, z, M(x, y, z, 0.5))
    return w


def zollhaus(seed, g=1):
    """Zollhaus: ein Fachwerkhaus mit Turmzimmer an der Hafeneinfahrt, Schlagbaum, Waage für Waren, Zollkisten und
    Wappenschild."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.15)
    st = stil_haus(w, "fachwerk_ocker")
    a, b = _r(3 * u + 2), _r(3 * u + 1)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="walm", tuer="south", gauben=True, kamine=1)
    P.turm(w, st, a + 1, -b, 1, _r(12 * u + 4), 2, dach="kegel", krone=False)
    for x in range(-R + 1, -a - 1):
        w.setze(x, 2, b + 3, w.b("stripped_spruce_log", axis="x") if x % 2 else w.b("red_wool"))
    w.setze(-a - 2, 1, b + 3, w.b("spruce_log", axis="y"))
    w.setze(-a - 2, 2, b + 3, w.b("spruce_log", axis="y"))
    w.setze(a, 1, b + 3, w.b("anvil", facing="north"))
    for k in range(3):
        w.setze(-1 + k, 1, b + 4, w.b("barrel", facing="up", open=True))
    return w


def hafenmole(seed, g=2):
    """Hafenmole: eine lange, steinerne Mole mit Bollwerk und Kanonenstellung schützt das Hafenbecken, an ihrer
    Spitze ein kleines Leuchtfeuer, Poller und Ringe."""
    w = _neu(seed)
    u = U[g]
    L = _r(20 * u + 6)
    wasserflaeche(w, -L - 4, -L // 2, L + 4, L // 2, tief=3, grund="sand")
    M = Mat(w, ["stone_bricks", "mossy_stone_bricks", "cobblestone", "andesite"])
    for x in range(-L, L + 1):
        for z in range(-2, 3):
            for y in range(-3, 2):
                w.setze(x, y, z, M(x, y, z, 0.5))
        for z in (-3, 3):
            w.setze(x, 2, z, M(x, 2, z, 0.8) if x % 2 else w.b("stone_brick_slab", type="bottom",
                                                               waterlogged=False))
        if x % 5 == 0:
            w.setze(x, 2, 0, w.b("cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
                                 waterlogged=False))
    for x in range(L - 3, L + 3):
        for z in range(-4, 5):
            for y in range(-3, 2):
                w.setze(x, y, z, M(x, y, z, 0.5))
    H = _r(10 * u + 4)
    for y in range(2, H):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) + abs(dz) < 2:
                    w.setze(L + dx, y, dz, w.b("white_concrete" if (y // 3) % 2 else "red_concrete"))
    w.setze(L, H, 0, w.b("glowstone"))
    w.setze(L, H + 1, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    from boote import ruderboot
    for k in range(3):
        einfuegen(w, ruderboot(seed + k, 0), -L // 2 + k * L // 2, 0, 6 + (k % 2) * 3)
    return w


def seilerei(seed, g=1):
    """Seilerei: eine lange, niedrige Reeperbahn mit offenem Dach, Spinnrädern, aufgespannten Tauen und
    Hanfballen – hier entstehen die Taue der Schiffe."""
    w = _neu(seed)
    u = U[g]
    L = _r(18 * u + 6)
    gelaende(w, L + 3, art="wiese", dichte=0.1)
    for x in range(-L, L + 1):
        for z in (-2, 2):
            if x % 3 == 0:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
        for z in range(-3, 4):
            w.setze(x, 4, z, w.b("spruce_slab", type="bottom", waterlogged=False) if abs(z) < 3 else
                    w.b("spruce_stairs", facing="south" if z < 0 else "north", half="bottom", shape="straight",
                        waterlogged=False))
        for z in (-1, 0, 1):
            w.setze(x, 2, z, w.b("tripwire", attached=False, disarmed=False, powered=False, east=True, west=True,
                                 north=False, south=False))
    for z in (-1, 0, 1):
        w.setze(-L - 1, 2, z, w.b("grindstone", face="floor", facing="east"))
    for k in range(4):
        w.setze(L + 2, 1, -3 + k * 2, w.b("hay_block", axis="y"))
    return w


HAFEN = {
    "hafenviertel": ("Hafenviertel", hafenviertel),
    "kontorhaus": ("Kontorhaus", kontorhaus),
    "speicherkanal": ("Speicherkanal", speicherkanal),
    "zollhaus": ("Zollhaus", zollhaus),
    "hafenmole": ("Hafenmole", hafenmole),
    "seilerei": ("Seilerei", seilerei),
}


# ============================================================================ BASAR → Wüstenreich

def basargasse(seed, g=2):
    """Überdachte Basargasse: eine lange Gasse unter einem Gewölbe aus Lehmbögen mit Lichtöffnungen, beidseitig
    Läden mit Teppichen, Kupfergeschirr, Gewürzsäcken und Lampen."""
    w = _neu(seed)
    d = _wueste(w, seed)
    u = U[g]
    L = _r(14 * u + 6)
    gelaende(w, L + 4, art="sand", dichte=0.1)
    M = d["lehm"]
    for z in range(-L, L + 1):
        for x in range(-6, 7):
            w.setze(x, 0, z, w.b("smooth_sandstone" if abs(x) < 3 else "sandstone"))
            if abs(x) == 6:
                for y in range(1, 6):
                    w.setze(x, y, z, M(x, y, z, y / 6))
        for k in range(13):
            a = k / 12 * math.pi
            x, y = round(math.cos(a) * 6), round(5 + math.sin(a) * 3)
            if not (z % 4 == 0 and abs(x) < 2):
                w.setze(x, y, z, M(x, y, z, 0.8))
        if z % 4 == 0:
            w.setze(0, 7, z, w.b("lantern", hanging=True, waterlogged=False))
        if z % 4 == 2:
            for sx in (-1, 1):
                for k in range(3):
                    w.setze(sx * (5 - k), 1, z, w.b(["red_wool", "orange_wool", "yellow_wool", "brown_wool",
                                                     "barrel", "copper_block"][(z + k) % 6]) if k else
                            w.b(f"{d['farben'][z % len(d['farben'])]}_carpet"))
    return w


def gewuerzmarkt(seed, g=1):
    """Gewürzmarkt: offene Stände mit kegelförmig aufgehäuften Gewürzen in Rot, Gelb, Orange und Braun, Säcke,
    Waagen und Sonnensegel über einem Platz."""
    w = _neu(seed)
    d = _wueste(w, seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R, art="sand", dichte=0.1)
    gewuerz = ["red_concrete_powder", "yellow_concrete_powder", "orange_concrete_powder", "brown_concrete_powder",
               "lime_concrete_powder", "white_concrete_powder"]
    n = 4 + 2 * g
    for i in range(n):
        a = i / n * 6.28
        cx, cz = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                w.setze(cx + dx, 1, cz + dz, w.b("spruce_slab", type="top", waterlogged=False) if abs(dx) + abs(dz)
                        else w.b(gewuerz[i % 6]))
        w.setze(cx, 2, cz, w.b(gewuerz[i % 6]))
        for dx in (-2, 2):
            for dz in (-2, 2):
                for y in range(1, 4):
                    w.setze(cx + dx, y, cz + dz, zf(w, d["holz"]))
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                w.setze(cx + dx, 4, cz + dz, w.b(f"{d['farben'][(i + dx) % len(d['farben'])]}_wool"))
    palme(w, 0, 0)
    return w


def teppichhaendler(seed, g=1):
    """Teppichhändler: ein Hof, in dem prächtig gemusterte Teppiche über Holzgestellen hängen und am Boden ausgelegt
    sind, Kissen, Teekanne und Wasserpfeife."""
    w = _neu(seed)
    d = _wueste(w, seed)
    u = U[g]
    R = _r(9 * u + 5)
    gelaende(w, R, art="sand", dichte=0.05)
    farben = ["red", "orange", "yellow", "blue", "purple", "white", "cyan"]
    for k in range(3):
        z = -R // 2 + k * (R // 2)
        for x in range(-R // 2, R // 2 + 1):
            w.setze(x, 4, z, w.b(f"{d['holz']}_log", axis="x"))
            for y in range(1, 4):
                f = farben[(abs(x) // 2 + y + k * 2) % len(farben)]
                w.setze(x, y, z, w.b(f"{f}_wool"))
        for x in (-R // 2 - 1, R // 2 + 1):
            for y in range(1, 5):
                w.setze(x, y, z, w.b(f"{d['holz']}_log", axis="y"))
    for x in range(-3, 4):
        for z in range(R // 2 + 2, R // 2 + 6):
            w.setze(x, 1, z, w.b(f"{farben[(x * x + z) % len(farben)]}_carpet"))
    w.setze(0, 1, R // 2 + 4, w.b("brewing_stand", has_bottle_0=True, has_bottle_1=False, has_bottle_2=True))
    return w


def hammam(seed, g=2):
    """Hammam: ein Badehaus mit Sterngewölbe-Kuppeln voller Lichtöffnungen, Wasserbecken im aufgeschnittenen
    Inneren, Säulenhof mit Brunnen und Türkis-Kacheln."""
    w = _neu(seed)
    d = _wueste(w, seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R, art="sand", dichte=0.05)
    a = _r(6 * u + 3)
    flachhaus(w, d["lehm"], -a, -a, a, a, 1, 4, d["holz"], zinnen=False)
    for x in range(-a + 1, a):
        for z in range(-a + 1, a):
            if x > 0 and z > 0:
                for y in range(1, 6):
                    w.bloecke.pop((x, y, z), None)
            if math.hypot(x, z) < a * 0.5:
                w.setze(x, 1, z, w.b("water", level=0) if math.hypot(x, z) < a * 0.4 else w.b("cyan_terracotta"))
    yk = kuppel(w, d["kuppel"], 0, 0, 6, a * 0.7, form="rund", spitze=d["gold"])
    for k in range(10):
        ang = k / 10 * 6.28
        w.setze(round(math.cos(ang) * a * 0.4), 6 + round(a * 0.55), round(math.sin(ang) * a * 0.4), w.b("glass"))
    for k in range(4):
        x = -a - 4
        z = -a + k * (2 * a) // 3
        for y in range(1, 5):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    return w


def brunnenplatz(seed, g=1):
    """Brunnenplatz: ein achteckiger Prunkbrunnen mit Türkiskacheln und Messinghähnen in der Medina, Wasserträger-
    Krüge, Palmen und ein Teehaus mit Markise."""
    w = _neu(seed)
    d = _wueste(w, seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R, art="sand", dichte=0.05)
    for x in range(-R + 2, R - 1):
        for z in range(-R + 2, R - 1):
            if math.hypot(x, z) < R * 0.6:
                w.setze(x, 0, z, w.b("smooth_sandstone" if (x + z) % 2 else "cut_sandstone"))
    r = 3 * u + 1.5
    for k in range(8):
        a1, a2 = k / 8 * 6.28, (k + 1) / 8 * 6.28
        linie(w, (math.cos(a1) * r, 1, math.sin(a1) * r), (math.cos(a2) * r, 1, math.sin(a2) * r),
              w.b("cyan_terracotta"))
        linie(w, (math.cos(a1) * r, 2, math.sin(a1) * r), (math.cos(a2) * r, 2, math.sin(a2) * r),
              w.b("smooth_sandstone_slab", type="bottom", waterlogged=False))
    for x in range(-int(r) + 1, int(r)):
        for z in range(-int(r) + 1, int(r)):
            if math.hypot(x, z) < r - 0.8:
                w.setze(x, 1, z, w.b("water", level=0))
    for y in range(1, 4):
        w.setze(0, y, 0, w.b("cyan_terracotta" if y < 3 else "gold_block"))
    for k in range(3):
        a = k * 2.1 + 0.4
        palme(w, round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8))
    flachhaus(w, d["lehm"], R // 3, -R + 2, R - 2, -R // 3, 1, 4, d["holz"])
    markise(w, R // 3, R - 2, -R // 3 + 1, 4, d["farben"])
    return w


def karawanenlager(seed, g=2):
    """Karawanenlager: Zelte der Händler um ein Lagerfeuer, angebundene Lasttiere (Heuballen und Tränken),
    aufgestapelte Warenballen und ein Wachposten auf einer Düne."""
    w = _neu(seed)
    d = _wueste(w, seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R, art="sand", dichte=0.05)
    n = 4 + g
    for i in range(n):
        a = i / n * 6.28
        zelt(w, round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6), 2.5 * u + 1, _r(3 * u + 2),
             [f"{f}_wool" for f in d["farben"]])
    w.setze(0, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for k in range(4):
        x = -2 + k
        w.setze(x, 1, R // 3, w.b("hay_block", axis="y"))
        w.setze(x, 1, R // 3 + 1, w.b("water_cauldron", level=3) if k % 2 else w.b(f"{d['farben'][k % 4]}_wool"))
    return w


BASAR = {
    "basargasse": ("Überdachte Basargasse", basargasse),
    "gewuerzmarkt": ("Gewürzmarkt", gewuerzmarkt),
    "teppichhaendler": ("Teppichhändler", teppichhaendler),
    "hammam": ("Hammam", hammam),
    "brunnenplatz": ("Brunnenplatz der Medina", brunnenplatz),
    "karawanenlager": ("Karawanenlager", karawanenlager),
}


# ============================================================================ WINTERDORF → Eisreich

def _schnee_auf(w, dichte=0.8):
    oben = {}
    for (x, y, z) in w.bloecke:
        if y > oben.get((x, z), -99):
            oben[(x, z)] = y
    rng = w.rng
    for (x, z), y in oben.items():
        n = w.P.name(w.bloecke[(x, y, z)])
        if any(k in n for k in ("stairs", "slab", "fence", "lantern", "chain", "wall", "door", "glass", "water",
                                "campfire", "bell", "ice")):
            continue
        if rng.random() < dichte:
            w.setze(x, y + 1, z, w.b("snow", layers=1 + int(rng.random() * 2)))


def winterhaeuser(seed, g=2):
    """Winterdorf: dick verschneite Holzhäuser mit steilen Dächern, rauchenden Kaminen und warmem Licht in den
    Fenstern, Holzstapel unter den Vordächern und ein Schneemann."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="schnee", dichte=0.2)
    n = 3 + g
    for i in range(n):
        a = i / n * 6.28 + 0.3
        cx, cz = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        st = stil_haus(w, ["holz_dunkel", "holz_hell", "stein_schiefer"][i % 3])
        P.gebaeude(w, st, cx - 3, cz - 2, cx + 3, cz + 2, y0=1, etagen=1 + (i % 2), eh=4, dach="sattel",
                   tuer="south", gauben=False, kamine=1, steil=True)
        for k in range(3):
            w.setze(cx - 3 + k, 1, cz + 3, w.b("spruce_log", axis="x"))
    for y, r in ((1, 1.5), (3, 1.1), (5, 0.8)):
        for dx in range(-2, 3):
            for dy in range(-1, 2):
                for dz in range(-2, 3):
                    if dx * dx + dy * dy + dz * dz <= r * r + 0.3:
                        w.setze(dx, y + dy, dz, w.b("snow_block"))
    w.setze(0, 6, 1, w.b("carved_pumpkin", facing="south"))
    _schnee_auf(w)
    return w


def wintermarkt(seed, g=2):
    """Wintermarkt: verschneite Holzbuden mit Lichterketten um einen geschmückten Tannenbaum, Glühweinfässer,
    Bänke und Laternen – ein Wintermarkt im Eisreich."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R, art="schnee", dichte=0.1)
    einfuegen(w, wald2.fichte(seed, H=_r(10 * u + 5)), 0, 0, 0)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if "leaves" in w.P.name(b) and rng.random() < 0.08 and w.frei(x, y, z + 1):
            w.setze(x, y, z + 1, w.b(["red_wool", "yellow_concrete", "glowstone", "light_blue_wool"][
                int(rng.integers(4))]))
    n = 5 + g
    for i in range(n):
        a = i / n * 6.28
        cx, cz = round(math.cos(a) * R * 0.65), round(math.sin(a) * R * 0.65)
        for dx in range(-2, 3):
            for dz in range(-1, 2):
                for y in range(1, 4):
                    if abs(dx) == 2 or dz == -1:
                        w.setze(cx + dx, y, cz + dz, w.b("spruce_planks"))
                w.setze(cx + dx, 4, cz + dz, w.b("spruce_slab", type="bottom", waterlogged=False))
            w.setze(cx + dx, 3, cz + 2, w.b(["red_wool", "yellow_wool", "white_wool"][(dx + i) % 3]))
        w.setze(cx, 1, cz + 1, w.b("barrel", facing="up", open=False))
    _schnee_auf(w, 0.6)
    return w


def schlittschuhteich(seed, g=1):
    """Schlittschuhteich: ein zugefrorener Teich mit glatter Eisfläche, Holzbänken und Feuerkörben am Ufer, eine
    Eisstockbahn und verschneite Weiden."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R + 3, art="schnee", dichte=0.1)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) < R * 0.8:
                w.setze(x, 0, z, w.b("ice" if (x + z) % 7 else "packed_ice"))
                w.setze(x, -1, z, w.b("water", level=0))
                w.bloecke.pop((x, 1, z), None)
    for k in range(4):
        a = k / 4 * 6.28 + 0.4
        x, z = round(math.cos(a) * R * 0.9), round(math.sin(a) * R * 0.9)
        w.setze(x, 1, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for x in range(-R // 2, R // 2):
        w.setze(x, 0, 0, w.b("blue_ice"))
    _schnee_auf(w, 0.5)
    return w


def hundeschlittenstation(seed, g=1):
    """Hundeschlittenstation: ein Blockhaus mit Hundezwingern, ein beladener Schlitten mit Kufen, Geschirrstangen,
    Fischtrockengestelle und Fellballen."""
    w = _neu(seed)
    u = U[g]
    R = _r(11 * u + 5)
    gelaende(w, R, art="schnee", dichte=0.1)
    st = stil_haus(w, "holz_dunkel")
    P.gebaeude(w, st, -4, -R + 2, 3, -R + 7, y0=1, etagen=1, eh=4, dach="sattel", tuer="south", gauben=False,
               kamine=1, steil=True)
    for k in range(4):
        x = -R + 3 + k * 3
        for dx in (0, 1):
            for dz in (0, 1):
                w.setze(x + dx, 1, 2 + dz, w.b("spruce_planks"))
        w.setze(x, 2, 2, w.b("spruce_slab", type="bottom", waterlogged=False))
    for x in range(3, 8):
        w.setze(x, 1, 4, w.b("spruce_slab", type="bottom", waterlogged=False))
        w.setze(x, 2, 4, w.b("brown_wool") if x % 2 else w.b("barrel", facing="up", open=False))
    for z in (3, 5):
        w.setze(8, 1, z, w.b("spruce_stairs", facing="east", half="bottom", shape="straight", waterlogged=False))
    _schnee_auf(w)
    return w


def raeucherhuette(seed, g=0):
    """Räucherhütte: eine kleine Steinhütte mit dickem Kamin, aus dem Rauch steigt, Fische an Stangen, Holzscheite und
    ein Eisloch mit Angel auf dem nahen Bach."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    gelaende(w, R, art="schnee", dichte=0.1)
    st = stil_haus(w, "stein_schiefer")
    P.gebaeude(w, st, -2, -2, 2, 2, y0=1, etagen=1, eh=3, dach="sattel", tuer="south", gauben=False, kamine=0)
    for y in range(1, 8):
        w.setze(3, y, 0, w.b("cobblestone"))
    w.setze(3, 8, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    for x in range(-3, 4):
        w.setze(x, 3, 4, w.b("spruce_fence", north=False, south=False, east=True, west=True, waterlogged=False))
        if x % 2:
            w.setze(x, 2, 4, w.b("orange_terracotta"))
    _schnee_auf(w)
    return w


def winterkapelle(seed, g=1):
    """Winterkapelle: eine kleine Steinkapelle mit spitzem Turm und Glocke auf einem verschneiten Hügel, Kerzen in
    den Fenstern und Laternen entlang des Wegs."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R, art="schnee", dichte=0.1)
    st = stil_haus(w, "stein_schiefer", fensterart="bogen")
    P.gebaeude(w, st, -3, -5, 3, 2, y0=1, etagen=1, eh=5, dach="sattel", first_x=False, tuer="south", gauben=False,
               kamine=0, steil=True)
    P.turm(w, st, 0, -6, 1, _r(10 * u + 5), 2, form="eckig", dach="pyramide", krone=False)
    for z in range(3, R):
        w.setze(0, 0, z, w.b("gravel"))
        if z % 3 == 0:
            for sx in (-2, 2):
                w.setze(sx, 1, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                      waterlogged=False))
                w.setze(sx, 2, z, w.b("lantern", hanging=False, waterlogged=False))
    _schnee_auf(w)
    return w


WINTERDORF = {
    "winterhaeuser": ("Winterdorf", winterhaeuser),
    "wintermarkt": ("Wintermarkt", wintermarkt),
    "schlittschuhteich": ("Schlittschuhteich", schlittschuhteich),
    "hundeschlittenstation": ("Hundeschlittenstation", hundeschlittenstation),
    "raeucherhuette": ("Räucherhütte", raeucherhuette),
    "winterkapelle": ("Winterkapelle", winterkapelle),
}


# ============================================================================ TOTENREICH → Friedhof & Spuk

def _totenboden(w, R):
    rn = Rauschen(w, 3)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                w.setze(x, 0, z, w.b(["soul_soil", "soul_sand", "coarse_dirt", "basalt", "soul_soil"][
                    int(rn(x, 0, z) * 4.99)], **({"axis": "y"} if int(rn(x, 0, z) * 4.99) == 3 else {})))


def totenfaehre(seed, g=2):
    """Totenfähre: ein schwarzer, nebliger Fluss, über den ein Fährmann seinen schmalen Kahn stakt, am Ufer ein
    Anleger mit Seelenlaternen und ein Tor aus Knochen."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    _totenboden(w, R)
    for x in range(-R, R + 1):
        for z in range(-R // 3, R // 3):
            if math.hypot(x, z) <= R:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("water", level=0))
                w.setze(x, -2, z, w.b("soul_soil"))
    for x in range(-4, 5):
        for z in range(-1, 2):
            w.setze(x, 1, z, w.b("dark_oak_slab", type="bottom", waterlogged=False) if abs(x) < 4 or z == 0 else None) \
                if abs(x) < 4 else None
    for x in (-4, 4):
        w.setze(x, 1, 0, w.b("dark_oak_planks"))
    for y in range(1, 6):
        w.setze(1, y, 0, w.b("dark_oak_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    for z in range(R // 3, R // 3 + 4):
        w.setze(0, 1, z, w.b("dark_oak_planks"))
    for sx in (-2, 2):
        for y in range(1, 6):
            w.setze(sx, y, R // 3 + 4, w.b("bone_block", axis="y"))
        w.setze(sx, 6, R // 3 + 4, w.b("soul_lantern", hanging=False, waterlogged=False))
    for x in range(-2, 3):
        w.setze(x, 6, R // 3 + 4, w.b("bone_block", axis="x"))
    for k in range(int(8 * u)):
        w.setze(int(w.rng.integers(-R, R)), 1 + int(w.rng.integers(0, 2)), int(w.rng.integers(-R // 3, R // 3)),
                w.b("cobweb"), False)
    return w


def knochenthron(seed, g=2):
    """Knochenthron: auf einem Podest aus Schädeln und Gebeinen thront ein leerer Thron mit hoher Lehne aus
    Rippen, flankiert von Seelenfeuer-Schalen."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    _totenboden(w, R)
    for k in range(3):
        r = 4 - k
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                w.setze(x, 1 + k, z, w.b("bone_block", axis="y") if (x + z) % 3 else w.b("skeleton_skull",
                                                                                          rotation=8) if k == 2
                        else w.b("bone_block", axis="x"))
    for x in (-1, 0, 1):
        w.setze(x, 4, 0, w.b("polished_blackstone"))
    H = _r(6 * u + 4)
    for k in range(5):
        x = -2 + k
        for y in range(4, 4 + H - abs(x)):
            w.setze(x, y, -1, w.b("bone_block", axis="y") if x % 2 == 0 else w.b("bone_block", axis="x"))
    for sx in (-4, 4):
        w.setze(sx, 4, 2, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                                west="none", waterlogged=False))
        w.setze(sx, 5, 2, w.b("soul_campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    return w


def seelentor(seed, g=2):
    """Seelentor: ein gewaltiges Portal aus schwarzem Stein mit eingemeißelten Gesichtern, durch das ein bläulicher
    Schleier weht, davor eine Allee aus Grabsäulen."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    _totenboden(w, R)
    B, H = _r(3 * u + 2), _r(9 * u + 5)
    M = Mat(w, ["polished_blackstone_bricks", "cracked_polished_blackstone_bricks", "blackstone",
                "chiseled_polished_blackstone"])
    for sx in (-B - 2, B + 2):
        for y in range(1, H + 1):
            for dx in (-1, 0, 1):
                for z in (-1, 0, 1):
                    w.setze(sx + dx, y, z, M(sx + dx, y, z, y / H))
    for x in range(-B - 3, B + 4):
        for y in range(H + 1, H + 3):
            for z in (-1, 0, 1):
                w.setze(x, y, z, M(x, y, z, 0.9))
    for x in range(-B - 1, B + 2):
        for y in range(1, H + 1):
            w.setze(x, y, 0, w.b("light_blue_stained_glass") if (x + y) % 3 else w.b("cyan_stained_glass"))
    for z in range(3, R, 3):
        for sx in (-B - 2, B + 2):
            for y in range(1, 4):
                w.setze(sx, y, z, M(sx, y, z, 0.5))
            w.setze(sx, 4, z, w.b("soul_lantern", hanging=False, waterlogged=False))
    return w


def nekropole(seed, g=2):
    """Nekropole: eine Totenstadt aus kleinen Grabhäusern mit Spitzdächern in engen Gassen, Säulen, Statuen und
    Laternen, alles in grauem Stein und von Moos überzogen."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    _totenboden(w, R)
    M = Mat(w, ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "andesite", "polished_andesite"])
    for i in range(-R + 2, R - 3, 6):
        for j in range(-R + 2, R - 3, 6):
            if math.hypot(i, j) > R - 4 or (abs(i) < 3 and abs(j) < 3):
                continue
            for x in range(i, i + 3):
                for z in range(j, j + 4):
                    for y in range(1, 4):
                        rand = x in (i, i + 2) or z in (j, j + 3)
                        if rand:
                            w.setze(x, y, z, M(x, y, z, y / 4))
            for k in range(2):
                for z in range(j, j + 4):
                    w.setze(i + k, 4 + k, z, w.b("stone_brick_stairs", facing="east", half="bottom",
                                                 shape="straight", waterlogged=False))
                    w.setze(i + 2 - k, 4 + k, z, w.b("stone_brick_stairs", facing="west", half="bottom",
                                                     shape="straight", waterlogged=False)) if k == 0 else None
            w.setze(i + 1, 5, j, w.b("chiseled_stone_bricks"))
    for y in range(1, 6):
        w.setze(0, y, 0, w.b("stone_bricks" if y < 5 else "soul_lantern", **({} if y < 5 else {"hanging": False,
                                                                                               "waterlogged": False})))
    from veredeln import bewuchs
    bewuchs(w, moos=0.08, ranken=0.05)
    return w


def schattenbaum(seed, g=2):
    """Schattenbaum: ein riesiger, schwarzer, blattloser Baum mit weit ausgreifenden Ästen, an denen Seelenlaternen
    hängen, die Wurzeln umklammern Grabsteine."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    _totenboden(w, R)
    H = _r(14 * u + 6)
    for y in range(1, H):
        r = 1.6 * u * (1 - y / H * 0.6) + 0.5
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                if dx * dx + dz * dz <= r * r:
                    w.setze(dx, y, dz, w.b("crimson_hyphae" if False else "dark_oak_wood", axis="y")
                            if (y + dx) % 4 else w.b("blackstone"))
    rng = w.rng
    for k in range(7):
        a = k / 7 * 6.28 + rng.random() * 0.4
        y0 = round(H * (0.55 + 0.35 * rng.random()))
        L = (6 + rng.random() * 4) * u
        end = (math.cos(a) * L, y0 + L * 0.5, math.sin(a) * L)
        linie(w, (0, y0, 0), end, w.b("dark_oak_log", axis="y"))
        linie(w, end, (end[0] * 1.2, end[1] + 2, end[2] * 1.2), w.b("dark_oak_fence", north=False, south=False,
                                                                     east=False, west=False, waterlogged=False))
        p = (round(end[0] * 0.7), round(end[1]) - 1, round(end[2] * 0.7))
        w.setze(p[0], p[1], p[2], w.b("chain", axis="y", waterlogged=False), False)
        w.setze(p[0], p[1] - 1, p[2], w.b("soul_lantern", hanging=True, waterlogged=False), False)
    for k in range(6):
        a = k / 6 * 6.28
        x, z = round(math.cos(a) * 4 * u), round(math.sin(a) * 4 * u)
        linie(w, (0, 1, 0), (x, 0, z), w.b("dark_oak_wood", axis="y"))
        w.setze(x, 1, z, w.b("cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
                             waterlogged=False))
        w.setze(x, 2, z, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    return w


def unterweltpalast(seed, g=3):
    """Palast der Unterwelt: ein düsterer Palast aus Schwarzstein mit spitzen Türmen und Seelenfeuer-Zinnen über einem
    Abgrund, ein Steg aus Knochen führt hinein."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    _totenboden(w, R)
    st = P.Stil(w, wand="schwarzstein", sockel="schwarzstein", gesims="polished_blackstone_brick", dach="schwarz",
                holz="dark_oak", fensterart="bogen")
    a, b = _r(6 * u + 3), _r(5 * u + 2)
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=5, dach="walm", tuer="south", gauben=False, kamine=0,
               pilaster=2)
    for sx in (-1, 1):
        for sz in (-1, 1):
            P.turm(w, st, sx * (a + 1), sz * (b + 1), 1, _r(14 * u + 5), 2.5, dach="nadel", krone=True)
    for x in range(-a - 2, a + 3):
        w.setze(x, 12, b + 1, w.b("soul_campfire", lit=True, signal_fire=False, facing="north", waterlogged=False)) \
            if x % 3 == 0 else None
    for z in range(b + 1, R):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("bone_block", axis="z"))
    return w


TOTENREICH = {
    "totenfaehre": ("Totenfähre", totenfaehre),
    "knochenthron": ("Knochenthron", knochenthron),
    "seelentor": ("Seelentor", seelentor),
    "nekropole": ("Nekropole", nekropole),
    "schattenbaum": ("Schattenbaum", schattenbaum),
    "unterweltpalast": ("Palast der Unterwelt", unterweltpalast),
}

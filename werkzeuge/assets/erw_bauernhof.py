"""Bauernhof & Landleben II – zwanzig weitere Bauten: Ziegenalm, Milchkammer, Kaninchengehege, Gänseweide, Most-
presse, Vogelscheuchen-Feld, Hofbackofen, Ochsenkarren am Feld, Fischteiche, Lavendelfeld, Sonnenblumenfeld,
Reisterrassen, Reetdachkate, Gewächshaus, Wagenremise, Göpelmühle, Lamaweide, Teeplantage am Hang, Dreschtenne und
Hochsilo."""

from __future__ import annotations

import math

from bauernhof import feld, garbe, hofpflaster, zaunzug, zf
from erw_basis import M, S, baum, figur, haus, hoehe, wiese
from erw_markt import mensch
from feinbau import Dachmat, kegeldach, laterne, satteldach
from flora import _neu
from leuchtwald2 import kugel, laubball
from lib import Rauschen
from skulptur import ell, kap, kasten


def tier(w, fell="white_wool", kopf=None, beine=None, hoerner=None, L=1.6, hals=0.8, ohren=None, schwanz=None):
    kopf = kopf or fell
    beine = beine or fell
    t = [(ell(0, 2.2, 0, L, 0.9, 0.75), w.b(fell)),
         (kap((L * 0.8, 2.5, 0), (L * 0.8 + 0.6, 2.5 + hals * 1.6, 0), 0.45, 0.35), w.b(fell)),
         (ell(L * 0.8 + 1.0, 2.6 + hals * 1.6, 0, 0.7, 0.42, 0.38), w.b(kopf))]
    for sx in (-L * 0.65, L * 0.65):
        for sz in (-0.4, 0.4):
            t.append((kap((sx, 1.8, sz), (sx, 0, sz), 0.25), w.b(beine)))
    if hoerner:
        for sz in (-0.25, 0.25):
            t.append((kap((L * 0.8 + 0.7, 3.0 + hals * 1.6, sz), (L * 0.8 + 0.1, 3.6 + hals * 1.6, sz * 2.4), 0.13),
                      w.b(hoerner)))
    if ohren:
        for sz in (-0.2, 0.2):
            t.append((kap((L * 0.8 + 0.8, 3.0 + hals * 1.6, sz), (L * 0.8 + 0.6, 4.2 + hals * 1.6, sz * 1.5), 0.17),
                      w.b(ohren)))
    if schwanz:
        t.append((kap((-L, 2.4, 0), (-L - 0.4, 1.4, 0), 0.15), w.b(schwanz)))
    return t


def gans(w):
    return [(ell(0, 1.0, 0, 0.9, 0.6, 0.55), w.b("white_wool")), (kap((0.6, 1.3, 0), (0.9, 2.4, 0), 0.22),
                                                                 w.b("white_wool")),
            (ell(1.1, 2.5, 0, 0.35, 0.25, 0.22), w.b("white_wool")), (ell(1.5, 2.45, 0, 0.25, 0.1, 0.12),
                                                                      w.b("orange_wool"))]


def herde(w, s, punkte, teile, u=None):
    for (x, y, z, a) in punkte:
        figur(w, u or (0.3 * s + 0.25), teile, (-3, -1, -2), (4, 6, 2), pos=(x, y, z), winkel=a)


def streu(w, zellen, R, n, frei=0.0, seed=0):
    rng = w.rng
    pts = []
    for _ in range(n * 4):
        if len(pts) >= n:
            break
        a = rng.random() * 6.28
        r = R * (frei + rng.random() * (0.85 - frei))
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        if (x, z) in zellen and w.frei(x, zellen[(x, z)] + 1, z):
            pts.append((x, zellen[(x, z)] + 1, z, rng.random() * 6.28))
    return pts


def holzwand(w):
    return M(w, [("spruce_planks", 3), ("stripped_spruce_log", 1)], axis="y")


# ============================================================================ Bauten

def ziegenalm(seed, g=2):
    """Ziegenalm: ein steiler Almhang mit Felsen, einer niedrigen Steinhütte mit Schindeldach und Holzbalkon, einem
    Ziegenpferch aus Trockenmauer, kletternden Ziegen auf den Felsen und einem Brunnentrog."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 5)
    H = int(8 * s + 5)
    f = M(w, [("stone", 3), ("andesite", 2), ("cobblestone", 1)])
    zellen = {}
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            h = int(max(0, min(H, (-z + R * 0.3) / (R * 1.2) * H)) + rn(x, 3, z) * 2.5)
            fels = rn(x, 8, z) > 0.68
            for y in range(-1, h + 1):
                w.setze(x, y, z, f(x, y, z) if fels or y < h - 1 else w.b("grass_block", snowy=False) if y == h
                        else w.b("dirt"))
            zellen[(x, z)] = h
            if not fels and rn(x, 9, z) < 0.12:
                w.setze(x, h + 1, z, w.b(["grass", "dandelion", "azure_bluet", "cornflower"][int(rn(x, 2, z) * 3.99)]))
    hx, hz = -int(R * 0.25), -int(R * 0.3)
    y0 = zellen.get((hx, hz), 3) + 1
    haus(w, hx, hz, 7, 5, y0, M(w, [("cobblestone", 2), ("stone", 1), ("mossy_cobblestone", 1)]), holz="spruce",
         H=3, dach=("spruce", "dark_oak"), tuer_s="south")
    px, pz, pr = int(R * 0.3), int(R * 0.15), int(3 + s)
    for k in range(int(2 * math.pi * pr * 1.4)):
        a = k / (2 * math.pi * pr * 1.4) * 2 * math.pi
        if abs(a - math.pi / 2) < 0.3:
            continue
        x, z = round(px + math.cos(a) * pr), round(pz + math.sin(a) * pr)
        y = zellen.get((x, z), 0)
        w.setze(x, y + 1, z, w.b("cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
                                 waterlogged=False))
    w.setze(px, zellen.get((px, pz), 0) + 1, pz, w.b("water_cauldron", level=3))
    ziege = tier(w, "white_wool", kopf="white_terracotta", beine="light_gray_wool", hoerner="gray_terracotta", L=1.2,
                 hals=0.6)
    herde(w, s, streu(w, zellen, R, int(4 + 2 * s), 0.2), ziege)
    return w


def milchkammer(seed, g=1):
    """Milchkammer: ein kühles Steinhaus am Bach mit Butterfass, Milchkannen und Käseregalen, daneben ein Melkplatz
    mit Kühen, Melkschemeln und Eimern, ein Brunnentrog und Weidezaun."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, huegel=0.1)
    for x in range(-R - 2, R + 3):
        z = int(R * 0.6 + math.sin(x / 3) * 1.2)
        for dz in (0, 1):
            if (x, z + dz) in zellen:
                w.setze(x, 0, z + dz, w.b("water", level=0))
                w.setze(x, -1, z + dz, w.b("gravel"))
                w.bloecke.pop((x, 1, z + dz), None)
    haus(w, -int(R * 0.3), -int(R * 0.25), 7, 5, 1, M(w, [("smooth_stone", 2), ("calcite", 1), ("stone", 1)]),
         holz="spruce", H=3, dach=("mcw:gray_terracotta", "deepslate_tile"), tuer_s="south")
    for k in range(3):
        x = -int(R * 0.3) - 2 + k * 2
        w.setze(x, 1, -int(R * 0.25) + 4, w.b("barrel", facing="up", open=False) if k != 1 else
                w.b("cauldron"))
    hofpflaster(w, int(R * 0.05), -2, int(R * 0.6), 3)
    kuh = tier(w, "white_wool", kopf="black_wool", beine="white_wool", hoerner="white_terracotta", L=1.8, hals=0.3,
               schwanz="black_wool")
    kuh_flecken = kuh + [(ell(0.3, 2.6, 0.3, 0.6, 0.5, 0.6), w.b("black_wool")),
                         (ell(-0.8, 2.3, -0.4, 0.5, 0.5, 0.5), w.b("black_wool"))]
    for k in range(int(1 + s)):
        x = int(R * 0.15) + k * 4
        herde(w, s, [(x, 1, 0, 0.0)], kuh_flecken)
        w.setze(x, 1, 2, w.b("spruce_slab", type="bottom", waterlogged=False))
        w.setze(x + 1, 1, 2, w.b("cauldron"))
    zaunzug(w, [(int(R * 0.05), -3), (int(R * 0.65), -3), (int(R * 0.65), 4)])
    return w


def kaninchengehege(seed, g=1):
    """Kaninchengehege: ein eingezäunter Grasauslauf mit Holzhäuschen auf Stelzen, Rampen, Erdhügeln mit Bau-
    eingängen, Möhrenbeet, Futterraufe und vielen grauen, braunen und weißen Kaninchen."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    zellen = wiese(w, R, huegel=0.2, blumen=0.04)
    A = int(R * 0.7)
    zaunzug(w, [(-A, -A), (A, -A), (A, A), (-A, A), (-A, -A)])
    for k in range(int(1 + s)):
        hx, hz = -A + 3 + k * 6, -A + 3
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                w.setze(hx + dx, 2, hz + dz, w.b("spruce_planks"))
                if abs(dx) == 1 or abs(dz) == 1:
                    w.setze(hx + dx, 3, hz + dz, w.b("spruce_planks") if (dx, dz) != (0, 1) else w.b("air")
                            if False else w.b("spruce_planks"))
            w.setze(hx + dx, 4, hz - 1, w.b("spruce_stairs", facing="south", half="bottom", shape="straight",
                                            waterlogged=False))
            w.setze(hx + dx, 4, hz, w.b("spruce_slab", type="bottom", waterlogged=False))
            w.setze(hx + dx, 4, hz + 1, w.b("spruce_stairs", facing="north", half="bottom", shape="straight",
                                            waterlogged=False))
        for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            w.setze(hx + dx, 1, hz + dz, w.b("spruce_fence"))
        w.bloecke.pop((hx, 3, hz + 1), None)
        w.setze(hx, 1, hz + 2, w.b("spruce_slab", type="bottom", waterlogged=False))
    for k in range(2):
        cx, cz = A - 4 - k * 5, A - 4
        kugel(w, cx, 0, cz, 2 + 0.3 * s, w.b("dirt"), ry=1.5)
        w.setze(cx, zellen.get((cx, cz), 0) + 2, cz, w.b("grass_block", snowy=False))
        w.bloecke.pop((cx, 1, cz + 2), None)
    for x in range(-2, 3):
        w.setze(x, 0, 2, w.b("farmland", moisture=7))
        w.setze(x, 1, 2, w.b("carrots", age=7))
    hase = tier(w, "light_gray_wool", L=0.9, hals=0.2, ohren="light_gray_wool", schwanz="white_wool")
    hase_b = tier(w, "brown_wool", L=0.9, hals=0.2, ohren="brown_wool", schwanz="white_wool")
    pts = streu(w, zellen, A, int(5 + 3 * s), 0.0)
    for i, p in enumerate(pts):
        herde(w, s, [p], hase if i % 2 else hase_b, u=0.18 * s + 0.15)
    return w


def gaenseweide(seed, g=1):
    """Gänseweide: eine feuchte Wiese mit Tümpel, auf der eine Gänseschar unter Aufsicht einer Hirtin mit Stab
    grast; ein kleiner Stall mit Strohdach, Weidenbäume und ein Futtertrog."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, huegel=0.15, blumen=0.03)
    rn = Rauschen(w, 3)
    for (x, z), h in zellen.items():
        if math.hypot(x + R * 0.3, z - R * 0.2) + rn(x, 0, z) * 2 < R * 0.3:
            w.setze(x, h, z, w.b("water", level=0))
            w.setze(x, h - 1, z, w.b("mud"))
            w.bloecke.pop((x, h + 1, z), None)
    haus(w, int(R * 0.4), -int(R * 0.4), 5, 4, 1, holzwand(w), holz="spruce", H=2, dach=("mcw:thatch", "spruce"),
         tuer_s="west", schorn=False)
    pts = streu(w, zellen, R, int(6 + 4 * s), 0.1)
    for p in pts:
        if w.P.name(w.bloecke.get((p[0], p[1] - 1, p[2]), 0) or 0) != "water" if False else True:
            herde(w, s, [p], gans(w), u=0.25 * s + 0.2)
    figur(w, 0.3 * s + 0.25, mensch(w, "blue_wool", haar="yellow_wool") +
          [(kap((0.8, 0, 0.3), (0.9, 6.0, 0.3), 0.18), w.b("spruce_planks"))], (-2, -1, -2), (2, 7, 2),
          pos=(0, 1, int(R * 0.3)), winkel=0.6)
    w.setze(-2, 1, -int(R * 0.4), w.b("spruce_slab", type="top", waterlogged=False))
    w.setze(-1, 1, -int(R * 0.4), w.b("composter", level=6))
    return w


def mostpresse(seed, g=1):
    """Mostpresse: unter einem offenen Schutzdach steht eine große Spindelpresse aus Eichenbalken, davor Körbe voller
    Äpfel, Fässer für den Most, ein Apfelbaum und eine Bank für die Pause."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    wiese(w, R, huegel=0.1)
    A, B = int(3 + s), int(2 + s)
    hofpflaster(w, -A - 1, -B - 1, A + 1, B + 1)
    for sx in (-A, A):
        for sz in (-B, B):
            for y in range(1, 5):
                w.setze(sx, y, sz, w.b("oak_log", axis="y"))
    satteldach(w, -A - 1, -B - 1, A + 1, B + 1, 5, Dachmat(w, ["spruce", "dark_oak"]), first_x=True, ue=0)
    for x in (-1, 1):
        for y in range(1, 4):
            w.setze(x, y, 0, w.b("dark_oak_log", axis="y"))
    for x in (-1, 0, 1):
        w.setze(x, 4, 0, w.b("dark_oak_log", axis="x"))
    w.setze(0, 3, 0, w.b("oak_log", axis="y"))
    w.setze(0, 2, 0, w.b("dark_oak_slab", type="top", waterlogged=False))
    w.setze(0, 1, 0, w.b("barrel", facing="up", open=True))
    for k in range(int(2 + s)):
        x = -A + 1 + k * 2
        w.setze(x, 1, B + 2, w.b("barrel", facing="east", open=False))
        w.setze(x, 1, -B + 1, w.b("composter", level=8))
    for k in range(3):
        w.setze(A + 2, 1, -1 + k, w.b("red_wool") if k % 2 else w.b("lime_wool"))
    baum(w, -A - 5, 1, B + 4, seed, 6 + 2 * s)
    w.setze(A + 3, 1, B + 2, w.b("oak_stairs", facing="west", half="bottom", shape="straight", waterlogged=False))
    return w


def vogelscheuchenfeld(seed, g=2):
    """Vogelscheuchen-Feld: ein Weizen- und Maisfeld, in dessen Mitte eine große Vogelscheuche mit Kürbiskopf,
    Hut und flatterndem Hemd steht; Krähen hocken auf dem Zaun, Garben am Rand."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.05, blumen=0.02)
    A = int(R * 0.6)
    feld(w, -A, -A, A, A, frucht="wheat")
    for z in range(-A, A + 1):
        if (z + A) % 9 == 4:
            continue
        for x in range(-A, -A + 4):
            for y in (1, 2):
                w.setze(x, y, z, w.b("sugar_cane", age=0))
    for y in range(1, 5):
        w.setze(0, y, 0, w.b("spruce_fence"))
    for x in range(-2, 3):
        w.setze(x, 4, 0, w.b("spruce_fence", east=x < 2, west=x > -2, north=False, south=False, waterlogged=False))
    w.setze(0, 5, 0, w.b("carved_pumpkin", facing="south"))
    for x in range(-1, 2):
        w.setze(x, 6, 0, w.b("brown_carpet"))
    for x in (-1, 0, 1):
        w.setze(x, 3, 0, w.b("red_wool") if x == 0 else w.b("blue_wool"))
    w.setze(0, 2, 0, w.b("hay_block", axis="y"))
    for k in range(int(3 + s)):
        x = -A - 1 + k * 3
        w.setze(x, 2, -A - 1, w.b("black_wool"))
    for k in range(int(2 + s)):
        garbe(w, A + 2, -A + k * 4)
    return w


def hofbackofen(seed, g=1):
    """Hofbackofen: ein freistehender Lehmbackofen mit gewölbter Kuppel unter einem Holzdach, davor ein Arbeitstisch
    mit Teigtrögen, ein Reisigstapel, Brotkörbe und ein Kaminrohr."""
    w = _neu(seed)
    s = S[g]
    R = int(8 * s + 6)
    wiese(w, R, huegel=0.1)
    hofpflaster(w, -4, -4, 4, 4)
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, 1, z, w.b("bricks"))
    from wueste_eis import kuppel
    kuppel(w, lambda x, y, z, t: w.b("terracotta") if (x + y) % 3 else w.b("mud_bricks"), 0, 0, 2, 2.4,
           spitze=None)
    w.setze(0, 2, 2, w.b("furnace", facing="south", lit=True))
    w.setze(0, 3, 2, w.b("bricks"))
    for y in range(4, 7):
        w.setze(0, y, -1, w.b("bricks"))
    w.setze(0, 7, -1, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for sx in (-3, 3):
        for sz in (-3, 3):
            for y in range(1, 6):
                w.setze(sx, y, sz, w.b("spruce_log", axis="y"))
    satteldach(w, -4, -4, 4, 4, 6, Dachmat(w, ["spruce", "dark_oak"]), first_x=True, ue=0)
    for x in range(-2, 3):
        w.setze(x, 1, 4, w.b("spruce_slab", type="top", waterlogged=False))
    w.setze(-1, 2, 4, w.b("cauldron"))
    for k in range(3):
        for y in (1, 2):
            w.setze(5, y, -2 + k, w.b("oak_log", axis="z") if y == 1 else w.b("birch_log", axis="z"))
    w.setze(-5, 1, 2, w.b("composter", level=4))
    return w


def ochsenkarren(seed, g=2):
    """Ochsenkarren am Feld: zwei gehörnte Ochsen im Joch ziehen einen schweren Karren voller Rüben über einen Feldweg
    zwischen frisch gepflügtem Acker und Kartoffelfeld; der Bauer geht nebenher."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.05)
    A = int(R * 0.7)
    feld(w, -A, -A, A, -3, frucht="potatoes")
    for x in range(-A, A + 1):
        for z in range(3, A + 1):
            if math.hypot(x, z) < R:
                w.setze(x, 0, z, w.b("farmland", moisture=0) if x % 2 else w.b("coarse_dirt"))
                w.bloecke.pop((x, 1, z), None)
    for x in range(-R, R + 1):
        for z in (-1, 0, 1):
            if math.hypot(x, z) < R:
                w.setze(x, 0, z, w.b("dirt_path") if (x + z) % 4 else w.b("coarse_dirt"))
    ochse = tier(w, "brown_wool", kopf="brown_terracotta", beine="brown_terracotta", hoerner="white_terracotta",
                 L=2.0, hals=0.3, schwanz="black_wool")
    for dz in (-1, 1):
        herde(w, s, [(2, 1, dz * round(0.9 + 0.5 * s), 0.0)], ochse, u=0.33 * s + 0.25)
    for z in range(-2, 3):
        w.setze(round(1 + 1.4 * s), round(3 + s), z, w.b("dark_oak_log", axis="z"), False)
    cx = -int(3 + 2 * s)
    for x in range(cx - 3, cx + 2):
        for z in (-1, 0, 1):
            w.setze(x, 2, z, w.b("spruce_planks"))
            w.setze(x, 3, z, w.b("beetroots", age=3) if False else w.b("red_terracotta") if (x + z) % 2 else
                    w.b("hay_block", axis="x"))
        for z in (-2, 2):
            w.setze(x, 3, z, w.b("spruce_fence"))
    for sz in (-2, 2):
        for x in (cx - 2, cx):
            w.setze(x, 1, sz, w.b("dark_oak_log", axis="z"))
    for x in range(cx + 2, 1):
        w.setze(x, 2, 0, w.b("spruce_fence"))
    figur(w, 0.3 * s + 0.25, mensch(w, "brown_wool"), (-2, -1, -2), (2, 6, 2), pos=(0, 1, 3), winkel=0.0)
    return w


def fischteiche(seed, g=2):
    """Fischteiche: mehrere rechteckige, durch Dämme und Holzschleusen getrennte Teiche mit Seerosen und Schilf,
    ein Fischerhaus mit Netzen, Reusen am Steg und ein Bottich voller Fische."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, huegel=0.05)
    n = int(2 + s)
    B = int(R * 1.4 / n)
    rng = w.rng
    for i in range(n):
        x0 = -int(R * 0.7) + i * B
        for x in range(x0 + 1, x0 + B - 1):
            for z in range(-int(R * 0.5), int(R * 0.3)):
                if (x, z) in zellen:
                    w.setze(x, 0, z, w.b("water", level=0))
                    w.setze(x, -1, z, w.b("water", level=0))
                    w.setze(x, -2, z, w.b("mud"))
                    w.bloecke.pop((x, 1, z), None)
                    if rng.random() < 0.05:
                        w.setze(x, 1, z, w.b("lily_pad"))
        for z in (-1, 0, 1):
            w.setze(x0 + B - 1, 1, z, w.b("spruce_trapdoor", facing="east", half="bottom", open=True, powered=False,
                                          waterlogged=False))
        for k in range(3):
            z = -int(R * 0.5) + 1 + k * 3
            for y in (1, 2):
                if (x0 + 1, z) in zellen:
                    w.setze(x0 + 1, y, z, w.b("sugar_cane", age=0))
    haus(w, 0, int(R * 0.6), 6, 4, 1, holzwand(w), holz="spruce", H=3, dach=("mcw:thatch", "spruce"),
         tuer_s="north", schorn=True)
    for x in range(-1, 2):
        for z in range(int(R * 0.3), int(R * 0.3) + 3):
            w.setze(x, 1, z, w.b("spruce_planks"))
    w.setze(3, 1, int(R * 0.35), w.b("water_cauldron", level=3))
    w.setze(-3, 1, int(R * 0.35), w.b("barrel", facing="up", open=True))
    for k in range(3):
        w.setze(-4 - k, 2, int(R * 0.6) - 3, w.b("cobweb"))
    return w


def lavendelfeld(seed, g=2):
    """Lavendelfeld: lange, gewölbte Reihen violetter Blüten ziehen sich über einen sanften Hang, dazwischen helle
    Erdwege; ein Steinhaus mit Destille, Bienenkästen und ein Leiterwagen voller Bündel."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, huegel=0.3, blumen=0.0)
    for (x, z), h in zellen.items():
        if math.hypot(x, z) > R * 0.85:
            continue
        if z % 3 == 0:
            w.setze(x, h, z, w.b("dirt_path"))
        else:
            w.setze(x, h + 1, z, w.b("lilac", half="lower") if (x + z) % 5 == 0 else w.b("allium"))
            if (x + z) % 5 == 0:
                w.setze(x, h + 2, z, w.b("lilac", half="upper"))
    haus(w, -int(R * 0.45), -int(R * 0.6), 7, 5, 1, M(w, [("smooth_sandstone", 2), ("cobblestone", 1),
                                                           ("calcite", 1)]),
         holz="spruce", H=3, dach=("mcw:red_terracotta", "granite"), tuer_s="south")
    w.setze(-int(R * 0.45) + 4, 1, -int(R * 0.6) + 3, w.b("brewing_stand", has_bottle_0=True, has_bottle_1=False,
                                                          has_bottle_2=True))
    for k in range(3):
        w.setze(int(R * 0.5) + k * 2, zellen.get((int(R * 0.5) + k * 2, -int(R * 0.65)), 0) + 1, -int(R * 0.65),
                w.b("beehive", facing="south", honey_level=3))
    return w


def sonnenblumenfeld(seed, g=2):
    """Sonnenblumenfeld: ein dichtes Feld hoher Sonnenblumen mit einem gemähten Pfad zu einer Holzplattform mit
    Aussicht, ein Holzschild, Erntekörbe und ein Feldkreuz am Rand."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, huegel=0.15, blumen=0.0)
    for (x, z), h in zellen.items():
        if math.hypot(x, z) > R * 0.85 or abs(x - round(math.sin(z / 4) * 2)) <= 1:
            continue
        if (x + z) % 2 == 0:
            w.setze(x, h + 1, z, w.b("sunflower", half="lower"))
            w.setze(x, h + 2, z, w.b("sunflower", half="upper"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, 3, z, w.b("spruce_planks"))
            if max(abs(x), abs(z)) == 2:
                w.setze(x, 4, z, zf(w, "spruce"))
    for sx in (-2, 2):
        for sz in (-2, 2):
            for y in range(1, 3):
                w.setze(sx, y, sz, w.b("spruce_log", axis="y"))
    for k in range(3):
        w.setze(0, 1 + k, 3 + k, w.b("spruce_stairs", facing="north", half="bottom", shape="straight",
                                     waterlogged=False))
    w.bloecke.pop((0, 4, 2), None)
    for k in range(3):
        w.setze(int(R * 0.6) + k, 1, int(R * 0.5), w.b("barrel", facing="up", open=True))
    return w


def reisterrassen(seed, g=2):
    """Reisterrassen: ein Hang aus geschwungenen, gefluteten Terrassen mit jungem Reis (Gras im Wasser), schmale
    Erddämme dazwischen, eine Stelzenhütte mit Strohdach und Wasserrinnen aus Bambus."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 5)
    n = int(4 + 2 * s)
    rng = w.rng
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            v = (-z + R) / (2 * R) + math.sin(x / 5) * 0.05
            stufe = max(0, min(n - 1, int(v * n)))
            h = stufe
            rand = abs(v * n - round(v * n)) < 0.2
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("dirt"))
            if rand:
                w.setze(x, h, z, w.b("grass_block", snowy=False))
            else:
                w.setze(x, h, z, w.b("water", level=0))
                w.setze(x, h - 1, z, w.b("mud"))
                if rng.random() < 0.35:
                    w.setze(x, h + 1, z, w.b("lily_pad")) if rng.random() < 0.05 else None
                    w.setze(x, h, z, w.b("seagrass")) if rng.random() < 0.6 else None
    hx, hz = int(R * 0.5), int(R * 0.3)
    yh = hoehe(w, hx, hz, n + 2) + 1
    for dx in (-2, 2):
        for dz in (-2, 2):
            for y in range(yh - 1, yh + 2):
                w.setze(hx + dx, y, hz + dz, w.b("bamboo_block", axis="y"))
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            w.setze(hx + dx, yh + 2, hz + dz, w.b("bamboo_planks"))
            if max(abs(dx), abs(dz)) == 2:
                w.setze(hx + dx, yh + 3, hz + dz, w.b("bamboo_planks") if (dx + dz) % 2 else w.b("bamboo_fence"))
    satteldach(w, hx - 3, hz - 3, hx + 3, hz + 3, yh + 5, Dachmat(w, ["mcw:thatch", "spruce"]), first_x=True)
    return w


def reetdachkate(seed, g=1):
    """Reetdachkate: ein niedriges Fachwerkhaus mit tief heruntergezogenem Reetdach und Gauben, Bauerngarten mit
    Staketenzaun, Rosen am Eingang, Hühner, ein Ziehbrunnen und ein Holzstapel."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, huegel=0.1, blumen=0.05)
    B, T = int(5 + 2 * s) | 1, int(5 + s)
    haus(w, 0, -2, B, T, 1, M(w, [("white_terracotta", 2), ("calcite", 1)]), holz="dark_oak", H=3,
         dach=("mcw:thatch", "spruce"), tuer_s="south", steil=2)
    A = int(R * 0.7)
    zaunzug(w, [(-A, 1), (-A, A), (A, A), (A, 1)], holz="birch")
    for x in range(-A + 1, A):
        for z in range(3, A):
            if (x + z) % 3 == 0 and abs(x) > 1:
                w.setze(x, 0, z, w.b("farmland", moisture=7))
                w.setze(x, 1, z, w.b(["carrots", "potatoes", "beetroots"][(x // 3) % 3], age=7 if (x // 3) % 3 < 2
                                     else 3))
    for x in range(-1, 2):
        for z in range(1, A + 1):
            w.setze(x, 0, z, w.b("gravel"))
            w.bloecke.pop((x, 1, z), None)
    w.setze(-2, 1, -2 + T // 2 + 1, w.b("rose_bush", half="lower"))
    w.setze(-2, 2, -2 + T // 2 + 1, w.b("rose_bush", half="upper"))
    huhn = tier(w, "white_wool", kopf="white_wool", L=0.6, hals=0.2)
    herde(w, s, streu(w, zellen, R, int(2 + s), 0.75), huhn, u=0.15 * s + 0.12)
    return w


def gewaechshaus(seed, g=1):
    """Gewächshaus: ein langes Glashaus mit Satteldach aus Glas, darin Pflanztische mit Tomaten (Beeren), Melonen und
    Blumen in Töpfen, Regenwassertonnen, ein Kompost und Frühbeetkästen davor."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.05)
    A, B = int(4 + 2 * s), int(2 + s)
    H = 3
    for x in range(-A, A + 1):
        for z in range(-B, B + 1):
            w.setze(x, 0, z, w.b("gravel") if abs(z) < 1 else w.b("farmland", moisture=7))
            if abs(x) == A or abs(z) == B:
                for y in range(1, H + 1):
                    w.setze(x, y, z, w.b("white_concrete") if (abs(x) == A and abs(z) == B) or (x % 3 == 0 and y == H)
                            else w.b("glass"))
            elif abs(z) >= 1:
                r = (x + z) % 4
                w.setze(x, 1, z, w.b("sweet_berry_bush", age=3) if r == 0 else w.b("melon_stem", age=7) if r == 1
                        else w.b("potted_red_tulip") if False else w.b("carrots", age=7))
    for k in range(B + 1):
        for x in range(-A, A + 1):
            for sz in (-1, 1):
                w.setze(x, H + 1 + k, sz * (B - k), w.b("glass") if x % 3 else w.b("white_concrete"))
    for y in (1, 2):
        w.bloecke.pop((0, y, B), None)
    w.setze(A + 1, 1, B, w.b("water_cauldron", level=3))
    w.setze(A + 1, 1, -B, w.b("composter", level=5))
    for k in range(2):
        x0 = -A + k * 5
        for x in range(x0, x0 + 3):
            w.setze(x, 1, B + 3, w.b("glass_pane"))
            w.setze(x, 0, B + 3, w.b("farmland", moisture=7))
    return w


def wagenremise(seed, g=1):
    """Wagenremise: ein offener Holzschuppen mit drei Toren, darin ein Heuwagen, ein Pflug und eine Egge, an der Wand
    Sensen und Rechen, davor ein Pflasterhof mit Wagenrad an der Mauer."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.05)
    A, B = int(5 + 2 * s), int(3 + s)
    hofpflaster(w, -A - 1, B + 1, A + 1, B + 5)
    for x in range(-A, A + 1):
        for z in range(-B, B + 1):
            w.setze(x, 0, z, w.b("coarse_dirt"))
            if z == -B or abs(x) == A:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("spruce_planks") if (x + y) % 4 else w.b("stripped_spruce_log", axis="y"))
            elif z == B and (x + A) % int(4 + s) == 0:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
    satteldach(w, -A - 1, -B - 1, A + 1, B + 1, 4, Dachmat(w, ["spruce", "dark_oak"]), first_x=True)
    for x in range(-A + 2, -A + 5):
        for z in (-1, 0):
            w.setze(x, 2, z, w.b("spruce_planks"))
            w.setze(x, 3, z, w.b("hay_block", axis="x"))
    for x in (-A + 2, -A + 4):
        w.setze(x, 1, 1, w.b("dark_oak_log", axis="z"))
    w.setze(0, 1, 0, w.b("iron_block"))
    w.setze(1, 1, 0, w.b("dark_oak_fence"))
    w.setze(-1, 1, 1, w.b("anvil", facing="east"))
    for x in range(A - 3, A):
        for z in (-1, 1):
            w.setze(x, 1, z, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
    for x in range(-A + 1, A, 2):
        w.setze(x, 2, -B + 1, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return w


def goepelmuehle(seed, g=1):
    """Göpelmühle: in einem runden, offenen Mühlhaus dreht ein Pferd an einem langen Göpelbalken den schweren
    Mahlstein; ringsum Mehlsäcke, Kornfässer und ein kegelförmiges Schindeldach auf Pfosten."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.05)
    rr = 4 + 1.5 * s
    for x in range(-int(rr) - 1, int(rr) + 2):
        for z in range(-int(rr) - 1, int(rr) + 2):
            d = math.hypot(x, z)
            if d <= rr:
                w.setze(x, 0, z, w.b("dirt_path") if d > rr - 2.5 else w.b("cobblestone"))
                w.bloecke.pop((x, 1, z), None)
    n = 8
    for k in range(n):
        a = k / n * 2 * math.pi
        x, z = round(math.cos(a) * (rr + 0.5)), round(math.sin(a) * (rr + 0.5))
        for y in range(1, 5):
            w.setze(x, y, z, w.b("spruce_log", axis="y"))
    kegeldach(w, 0, 0, 5, rr + 0.5, Dachmat(w, ["spruce", "dark_oak"]), form="kegel", spitze=None)
    for x in (-1, 0, 1):
        for z in (-1, 0, 1):
            w.setze(x, 1, z, w.b("smooth_stone"))
            w.setze(x, 2, z, w.b("stone") if (x, z) != (0, 0) else w.b("grindstone", face="floor",
                                                                       facing="north"))
    for y in range(3, 5):
        w.setze(0, y, 0, w.b("oak_log", axis="y"))
    for t in range(1, int(rr) - 1):
        w.setze(t, 3, 0, w.b("oak_log", axis="x"))
    from erw_arena import pferd
    figur(w, 0.3 * s + 0.25, pferd(w, "brown_wool", "brown_terracotta"), (-4, -1, -2), (5, 6, 2),
          pos=(int(rr) - 2, 1, 1), winkel=-math.pi / 2)
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.4
        w.setze(round(math.cos(a) * (rr - 0.5)), 1, round(math.sin(a) * (rr - 0.5)), w.b("white_wool") if k % 2
                else w.b("barrel", facing="up", open=False))
    return w


def lamaweide(seed, g=2):
    """Lamaweide: eine hügelige Weide mit Lamas in Cremeweiß, Braun und Grau, bunten Satteldecken, einem Unterstand
    mit Heuraufe, Steinmauer statt Zaun und einem Hirten mit Poncho."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, huegel=0.6)
    A = R * 0.8
    for k in range(int(2 * math.pi * A * 1.3)):
        a = k / (2 * math.pi * A * 1.3) * 2 * math.pi
        x, z = round(math.cos(a) * A), round(math.sin(a) * A)
        if (x, z) in zellen and abs(a - math.pi / 2) > 0.15:
            w.setze(x, zellen[(x, z)] + 1, z, w.b("cobblestone_wall", up=True, north="none", south="none", east="none",
                                                 west="none", waterlogged=False))
    sx, sz = -int(R * 0.4), -int(R * 0.4)
    y0 = zellen.get((sx, sz), 0) + 1
    for dx in (-2, 2):
        for dz in (-1, 1):
            for y in range(y0, y0 + 3):
                w.setze(sx + dx, y, sz + dz, w.b("spruce_log", axis="y"))
    for dx in range(-3, 4):
        for dz in range(-2, 3):
            w.setze(sx + dx, y0 + 3, sz + dz, w.b("spruce_slab", type="bottom", waterlogged=False))
    w.setze(sx, y0, sz, w.b("hay_block", axis="y"))
    farben = [("white_wool", "red_wool"), ("brown_wool", "yellow_wool"), ("light_gray_wool", "blue_wool"),
              ("white_terracotta", "lime_wool")]
    pts = streu(w, zellen, A, int(4 + 2 * s), 0.0)
    for i, p in enumerate(pts):
        fell, decke = farben[i % 4]
        lama = tier(w, fell, L=1.3, hals=1.3, ohren=fell) + [(ell(0, 3.0, 0, 0.9, 0.3, 0.8), w.b(decke))]
        herde(w, s, [p], lama)
    figur(w, 0.3 * s + 0.25, mensch(w, "orange_wool") + [(ell(0, 3.4, 0, 1.0, 0.35, 1.0), w.b("red_wool"))],
          (-2, -1, -2), (2, 6, 2), pos=(2, zellen.get((2, 2), 0) + 1, 2), winkel=0.0)
    return w


def teeplantage(seed, g=2):
    """Teeplantage am Hang: geschwungene Reihen runder Teebüsche ziehen sich in Terrassen einen Hang hinauf, Pflücker
    mit Körben arbeiten darin, oben steht ein Trockenhaus mit offenen Lattenwänden."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 5)
    H = int(6 * s + 4)
    zellen = {}
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            v = max(0.0, min(1.0, (-z + R * 0.6) / (R * 1.4)))
            h = int(v * H)
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else w.b("dirt"))
            zellen[(x, z)] = h
            reihe = (z + int(math.sin(x / 5) * 2)) % 3
            if reihe == 0 and math.hypot(x, z) < R - 1:
                w.setze(x, h + 1, z, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False)
                        if (x % 5) else w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
            elif reihe == 1:
                w.setze(x, h, z, w.b("dirt_path"))
    for k in range(int(3 + s)):
        x, z = -int(R * 0.5) + k * int(R * 0.35), int(R * 0.2) - k * 3
        y = zellen.get((x, z), 0) + 1
        if w.frei(x, y, z):
            figur(w, 0.28 * s + 0.22, mensch(w, ["red_wool", "yellow_wool", "pink_wool"][k % 3]) +
                  [(ell(-0.6, 3.0, 0, 0.5, 0.6, 0.5), w.b("barrel"))], (-2, -1, -2), (2, 6, 2), pos=(x, y, z),
                  winkel=k)
    hx, hz = 0, -int(R * 0.75)
    y0 = zellen.get((hx, hz), H) + 1
    for x in range(hx - 4, hx + 5):
        for z in range(hz - 2, hz + 3):
            w.setze(x, y0 - 1, z, w.b("bamboo_planks"))
            if max(abs(x - hx) / 4, abs(z - hz) / 2) >= 1:
                for y in range(y0, y0 + 3):
                    w.setze(x, y, z, w.b("bamboo_fence") if (x + y) % 2 else w.b("bamboo_block", axis="y"))
    satteldach(w, hx - 5, hz - 3, hx + 5, hz + 3, y0 + 3, Dachmat(w, ["mcw:thatch", "spruce"]), first_x=True)
    return w


def dreschtenne(seed, g=1):
    """Dreschtenne: eine große, offene Tenne mit Lehmboden, auf dem Garben gedroschen werden, Dreschflegel an der Wand,
    Säcke voller Korn, eine Windfege und ein Spreuhaufen vor dem Tor."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.05)
    A, B = int(5 + 2 * s), int(4 + s)
    for x in range(-A, A + 1):
        for z in range(-B, B + 1):
            w.setze(x, 0, z, w.b("packed_mud") if (x + z) % 3 else w.b("coarse_dirt"))
            if abs(x) == A and abs(z) < B - 1 and abs(z) > 1:
                for y in range(1, 5):
                    w.setze(x, y, z, w.b("spruce_planks"))
            if abs(z) == B:
                for y in range(1, 5):
                    w.setze(x, y, z, w.b("spruce_log", axis="y") if (x + A) % 4 == 0 else w.b("spruce_planks"))
    satteldach(w, -A - 1, -B - 1, A + 1, B + 1, 5, Dachmat(w, ["spruce", "dark_oak"]), first_x=True)
    for k in range(int(3 + s)):
        garbe(w, -A + 2 + k * 3, -B + 2)
    for k in range(4):
        w.setze(-2 + k, 1, 1, w.b("hay_block", axis="x"))
    for k in range(3):
        w.setze(A - 2, 1, -1 + k, w.b("white_wool"))
    w.setze(A - 2, 2, 0, w.b("white_wool"))
    for x in range(A + 2, A + 5):
        for z in (-1, 0, 1):
            w.setze(x, 1, z, w.b("hay_block", axis="y") if (x + z) % 2 else w.b("yellow_carpet"))
    w.setze(2, 1, -2, w.b("loom", facing="south"))
    figur(w, 0.3 * s + 0.25, mensch(w, "brown_wool") + [(kap((0.9, 2.6, 0), (1.5, 4.6, 0), 0.18),
                                                         w.b("spruce_planks"))],
          (-2, -1, -2), (2, 6, 2), pos=(0, 1, -1), winkel=0.5)
    return w


def hochsilo(seed, g=2):
    """Hochsilo: ein hoher, runder Futtersilo aus Ziegeln mit Kupferhaube und Außenleiter neben einer roten
    Stallscheune, verbunden durch ein Förderrohr; davor Heuballen und ein Wagen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.05)
    rs = int(2 + s)
    H = int(10 * s + 8)
    sx = int(R * 0.35)
    for y in range(1, H + 1):
        for x in range(sx - rs - 1, sx + rs + 2):
            for z in range(-rs - 1, rs + 2):
                d = math.hypot(x - sx, z)
                if rs - 0.6 < d <= rs + 0.4:
                    w.setze(x, y, z, w.b("bricks") if y % 6 else w.b("iron_block"))
    kegeldach(w, sx, 0, H + 1, rs, Dachmat(w, ["waxed_oxidized_cut_copper", "waxed_weathered_cut_copper"]),
              form="glocke")
    for y in range(1, H + 1):
        w.setze(sx - rs - 1, y, 0, w.b("ladder", facing="west", waterlogged=False), False)
    rot = M(w, [("red_terracotta", 3), ("red_concrete", 1)])
    haus(w, -int(R * 0.3), 0, int(8 + 2 * s), int(6 + s), 1, rot, holz="dark_oak", H=4,
         dach=("dark_oak", "spruce"), tuer_s="south", schorn=False)
    from steampunk2 import zylinder
    zylinder(w, (sx - rs, H - 2, 0), (-int(R * 0.3) + 3, 7, 0), 0.6, w.b("iron_block"))
    for k in range(int(3 + s)):
        x = -int(R * 0.6) + k * 2
        w.setze(x, 1, int(R * 0.45), w.b("hay_block", axis="y"))
        if k % 2:
            w.setze(x, 2, int(R * 0.45), w.b("hay_block", axis="y"))
    return w


BAUERNHOF3 = {
    "ziegenalm": ("Ziegenalm", ziegenalm),
    "milchkammer": ("Milchkammer", milchkammer),
    "kaninchengehege": ("Kaninchengehege", kaninchengehege),
    "gaenseweide": ("Gänseweide", gaenseweide),
    "mostpresse": ("Mostpresse", mostpresse),
    "vogelscheuchenfeld": ("Vogelscheuchen-Feld", vogelscheuchenfeld),
    "hofbackofen": ("Hofbackofen", hofbackofen),
    "ochsenkarren": ("Ochsenkarren am Feld", ochsenkarren),
    "fischteiche": ("Fischteiche", fischteiche),
    "lavendelfeld": ("Lavendelfeld", lavendelfeld),
    "sonnenblumenfeld": ("Sonnenblumenfeld", sonnenblumenfeld),
    "reisterrassen": ("Reisterrassen", reisterrassen),
    "reetdachkate": ("Reetdachkate", reetdachkate),
    "gewaechshaus": ("Gewächshaus", gewaechshaus),
    "wagenremise": ("Wagenremise", wagenremise),
    "goepelmuehle": ("Göpelmühle", goepelmuehle),
    "lamaweide": ("Lamaweide", lamaweide),
    "teeplantage": ("Teeplantage am Hang", teeplantage),
    "dreschtenne": ("Dreschtenne", dreschtenne),
    "hochsilo": ("Hochsilo", hochsilo),
}

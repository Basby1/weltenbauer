"""Brücken & Tore – Erweiterung der Kategorie „Brücken“: überdachte Holzbrücke, Viadukt, Häuserbrücke,
Brückenkapelle, Baumstammbrücke, Pontonbrücke, Klappbrücke, Eisbogen, Zollbrücke, Buckelbrücke, Fachwerkträger-
brücke, Mühlenbrücke, Steinplattenbrücke, Schluchtbrücke, Stufenbrücke am Kanal, Seilfähre, Zickzacksteg,
moderner Bogensteg sowie Palisadentor, Parktor, Lehmtor, Sternentor, Schleuse, Wassertor und Grenzposten.
Flüsse laufen entlang z, Brücken entlang x. Boden y = 0 (Ufer liegen höher)."""

from __future__ import annotations

import math

import pracht as P
import wald2
from flora import _neu, _r, _stil, linie
from gewaesser import Land
from haeuser import HAUSPOOL
from lib import Rauschen, einfuegen
from pracht import Mat, gelaende
from veredeln import bewuchs

U = [0.6, 1.0, 1.7, 2.8]


# ============================================================================ Hilfen

def zaun(w, name, ax="x"):
    return w.b(name, east=ax == "x", west=ax == "x", north=ax == "z", south=ax == "z", waterlogged=False)


def mauer(w, name, ax="x", up=False):
    a, b = ("low", "none") if ax == "x" else ("none", "low")
    return w.b(name, east=a, west=a, north=b, south=b, up=up, waterlogged=False)


def gitter(w, ax="x", name="iron_bars"):
    return w.b(name, east=ax == "x", west=ax == "x", north=ax == "z", south=ax == "z", waterlogged=False)


def treppe(w, name, facing, half="bottom"):
    return w.b(name, facing=facing, half=half, shape="straight", waterlogged=False)


def platte(w, name, typ="bottom"):
    return w.b(name, type=typ, waterlogged=False)


def laterne(w, haengend=False):
    return w.b("lantern", hanging=haengend, waterlogged=False)


def stil_haus(w, pool, **kw):
    d = dict(HAUSPOOL[pool])
    d.update(kw)
    return P.Stil(w, **d)


def flusstal(w, R, B, hb=2, steil=2, gras="grass_block", tiefe=2, W=2, baeume=3, arten=("oak", "birch"),
             dichte=0.35, weg="dirt_path", schilf=True):
    """Fluss entlang z (Halbbreite B) zwischen Ufern der Höhe hb; Weg entlang x (Halbbreite W) auf Uferhöhe.
    Gibt das Land zurück."""
    L = Land(w, R)
    if hb:
        L.heben(lambda x, z, h: min(hb, max(0, (abs(x) - B - 1) * steil)))
    L.fluss([(0, -R - 3), (0, R + 3)], B, 0, tiefe=tiefe, ufer=1.2)
    L.bauen(gras=gras, unten=-3)
    L.bepflanzen(dichte=dichte, baeume=0, ufer_schilf=schilf)
    rng = w.rng
    for (x, z), h in L.h.items():
        if abs(z) <= W and (x, z) not in L.wasser and h == hb:
            for y in range(h + 1, h + 4):
                w.bloecke.pop((x, y, z), None)
            if weg and rng.random() < 0.85:
                w.setze(x, h, z, w.b(weg))
    baeume_weg(w, L, baeume, W, arten)
    return L


def baeume_weg(w, L, n, W, arten=("oak", "birch")):
    rng = w.rng
    zellen = [p for p, h in L.h.items() if abs(p[1]) > W + 4 and p not in L.wasser and h >= 0 and
              not any((p[0] + dx, p[1] + dz) in L.wasser for dx in (-3, 0, 3) for dz in (-3, 0, 3))]
    gesetzt = []
    rng.shuffle(zellen)
    for (x, z) in zellen:
        if len(gesetzt) >= n:
            break
        if any(math.hypot(x - a, z - b) < 7 for a, b in gesetzt):
            continue
        art = arten[len(gesetzt) % len(arten)]
        sd = int(rng.integers(1, 10 ** 6))
        b = {"birke": wald2.birke, "fichte": wald2.fichte, "kiefer": wald2.kiefer, "weide": wald2.weide,
             "palme": wald2.palme, "kirsche": wald2.kirschbaum}.get(art)
        b = b(sd) if b else wald2.laubbaum(sd, art)
        einfuegen(w, b, x, L.h[(x, z)], z)
        gesetzt.append((x, z))


def spannweite(L, B):
    """Erstes x, ab dem das Ufer seine volle Höhe hat."""
    hb = max(L.h.values())
    for x in range(B, B + 40):
        if L.h.get((x, 0), hb) >= hb:
            return x
    return B + 3


def bogen_offen(x, y, S, n, y0, Ha, rand=1.0):
    """Liegt (x, y) in einer der n Bogenöffnungen zwischen -S und S? Bögen stehen auf y0, Scheitel y0 + Ha."""
    sp = 2 * S / n
    k = min(n - 1, int((x + S) / sp))
    m = -S + (k + 0.5) * sp
    a = sp / 2 - rand
    if a <= 0:
        return False
    if y < y0:
        return abs(x - m) < a
    return ((x - m) / a) ** 2 + ((y - y0) / Ha) ** 2 < 1


def steinbogen(w, S, W, D, M, n, y0=-2, Ha=None, gel="stone_brick_wall", gel_hoch=True, pfeilerkopf=True):
    """Gemauerte Bogenbrücke von -S bis S, Fahrbahn auf y = D, n Bögen, Brüstung, Wellenbrecher."""
    Ha = Ha or (D - y0 - 1.5)
    for x in range(-S, S + 1):
        for z in range(-W, W + 1):
            for y in range(y0, D + 1):
                if bogen_offen(x, y, S, n, y0, Ha):
                    continue
                w.setze(x, y, z, M(x, y, z, (y - y0) / max(1, D - y0)))
        for z in (-W - 1, W + 1):
            w.setze(x, D, z, M(x, D, z, 0.95))
            if gel_hoch:
                w.setze(x, D + 1, z, mauer(w, gel, "x", up=(x % 4 == 0)))
    sp = 2 * S / n
    if pfeilerkopf:
        for k in range(1, n):
            xm = round(-S + k * sp)
            for z0 in (-1, 1):
                for d in range(1, 4):
                    for x in range(xm - 2 + d, xm + 3 - d):
                        for y in range(y0, 2):
                            w.setze(x, y, z0 * (W + d), M(x, y, 0, 0.3))
                w.setze(xm, 2, z0 * (W + 1), platte(w, "stone_brick_slab"))


# ============================================================================ Brücken

def ueberdachte_bruecke(seed, g=2):
    """Überdachte Holzbrücke: ein langer Holztunnel mit Satteldach überspannt den Fluss auf Steinpfeilern, mit
    Brettwänden, Fensterband, hängenden Laternen und Giebeln an beiden Enden."""
    w = _neu(seed)
    u = U[g]
    B = _r(4 * u + 2)
    hb = _r(1.5 * u + 2)
    W = _r(1 * u + 1)
    R = B + _r(10 * u + 8)
    L = flusstal(w, R, B, hb=hb, W=W, baeume=2 + g)
    S = spannweite(L, B) + 2
    holz = ["spruce", "dark_oak", "oak", "spruce"][seed % 4]
    Ms = Mat(w, ["stone_bricks", "cobblestone", "mossy_cobblestone", "andesite"])
    D = hb
    for x in list(range(-S, -S + 3)) + list(range(S - 2, S + 1)) + ([-1, 0, 1] if B > 5 else []):
        for z in range(-W - 2, W + 3):
            for y in range(-3, D):
                w.setze(x, y, z, Ms(x, y, z, 0.5))
    for x in range(-S, S + 1):
        for z in range(-W - 1, W + 2):
            w.setze(x, D, z, w.b(f"{holz}_planks" if abs(z) <= W else f"stripped_{holz}_log", axis="x")
                    if abs(z) > W else w.b(f"{holz}_planks"))
        for z in (-W - 1, W + 1):
            pfosten = x % 3 == 0
            for y in range(D + 1, D + 5):
                if pfosten:
                    w.setze(x, y, z, w.b(f"stripped_{holz}_log", axis="y"))
                elif y in (D + 1, D + 4):
                    w.setze(x, y, z, w.b(f"{holz}_planks"))
                elif y == D + 2:
                    w.setze(x, y, z, zaun(w, f"{holz}_fence", "x"))
        for z in range(-W - 2, W + 3):
            hz = W + 2 - abs(z)
            y = D + 5 + hz
            if z == 0 or (W % 2 == 0 and False):
                w.setze(x, y, z, platte(w, f"{holz}_slab"))
            else:
                w.setze(x, y, z, treppe(w, f"{holz}_stairs", "south" if z < 0 else "north"))
            if abs(z) <= W + 1 and hz >= 1:
                w.setze(x, y - 1, z, w.b(f"{holz}_planks"), False) if abs(x) == S else None
        if x % 5 == 0:
            w.setze(x, D + 4 + W, 0, laterne(w, True))
            for y in range(D + 5, D + 5 + W + 2):
                pass
    for xe in (-S, S):
        for z in range(-W - 1, W + 2):
            for y in range(D + 5, D + 6 + W + 1 - abs(z)):
                w.setze(xe, y, z, w.b(f"{holz}_planks"))
        w.setze(xe, D + 6, 0, w.b("glass_pane", north=True, south=True, east=False, west=False, waterlogged=False))
        for y in range(D + 1, D + 5):
            pass
    bewuchs(w, moos=0.03)
    return w


def viadukt(seed, g=3):
    """Viadukt: ein hohes, zweigeschossiges Bogenviadukt aus Backstein oder Naturstein spannt sich über ein Tal mit
    Bach, oben verläuft ein Schienenstrang zwischen Brüstungen, Pfeiler mit Gesimsband."""
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 8)
    B = _r(1.5 * u + 1)
    H = _r(12 * u + 6)
    L = Land(w, R)
    L.heben(lambda x, z, h: H * min(1.0, (abs(x) / (R * 0.95)) ** 1.6))
    L.fluss([(0, -R - 3), (0, R + 3)], B, 0, tiefe=1, ufer=1.0)
    L.bauen(unten=-2)
    L.bepflanzen(dichte=0.35, baeume=0)
    baeume_weg(w, L, 4 + 2 * g, 3)
    M = Mat(w, ["bricks", "bricks", "mud_bricks", "packed_mud", "bricks"]) if _stil(seed) else \
        Mat(w, ["stone_bricks", "andesite", "cobblestone", "stone_bricks", "mossy_stone_bricks"])
    D = H + 1
    W = _r(1.2 * u + 1)
    sp = _r(3.2 * u + 3)
    mitte = round(D * 0.5)
    for x in range(-R, R + 1):
        ph = (x + R) % sp
        boden = L.h.get((x, 0), 0)
        for z in range(-W, W + 1):
            for y in range(boden + 1 if boden > -1 else -2, D + 1):
                if ph >= 2:
                    a = (sp - 2) / 2
                    t = (ph - 2 + 0.5 - a) / a
                    oben = math.sqrt(max(0.0, 1 - t * t)) * a * 0.9
                    if y < mitte - 1 - oben + a * 0.9 - 1 and y < mitte - 1:
                        continue
                    if mitte + 1 <= y < D - 1 - oben + a * 0.9 - 1 - 1 and y < D - 2:
                        continue
                w.setze(x, y, z, M(x, y, z, y / D))
            if ph < 2 and boden < mitte:
                for y in range(boden + 1, mitte):
                    for zz in (-W - 1, W + 1):
                        w.setze(x, y, zz, M(x, y, zz, 0.3))
        for zz in (-W - 1, W + 1):
            w.setze(x, mitte, zz, platte(w, "stone_brick_slab"))
            w.setze(x, D, zz, M(x, D, zz, 0.9))
            w.setze(x, D + 1, zz, mauer(w, "brick_wall" if _stil(seed) else "stone_brick_wall", "x",
                                        up=(x % sp == 0)))
        for z in range(-W, W + 1):
            w.setze(x, D, z, w.b("gravel"))
        w.setze(x, D + 1, 0, w.b("rail", shape="east_west", waterlogged=False))
        if x % (2 * sp) == 0:
            w.setze(x, D + 2, -W - 1, laterne(w))
    for (x, z), h in list(L.h.items()):
        if abs(z) <= W + 1 and abs(x) <= R and h >= D - 1:
            for y in range(h + 1, D + 3):
                if (x, y, z) in w.bloecke and y > D + 1:
                    w.bloecke.pop((x, y, z))
    return w


def haeuserbruecke(seed, g=2):
    """Häuserbrücke: eine breite steinerne Bogenbrücke, auf der beidseits schmale Fachwerkläden stehen, die auf
    Kragsteinen über das Wasser auskragen; in der Mitte ein freier Aussichtsplatz mit Brunnen."""
    w = _neu(seed)
    u = U[g]
    B = _r(6 * u + 2)
    hb = _r(1.5 * u + 2)
    W = _r(1.2 * u + 1)
    R = B + _r(9 * u + 8)
    L = flusstal(w, R, B, hb=hb, W=W, baeume=2 + g, weg="cobblestone")
    S = spannweite(L, B) + 1
    M = Mat(w, ["stone_bricks", "cobblestone", "andesite", "stone_bricks", "mossy_stone_bricks"])
    n = 3 if u > 0.9 else 2
    tz = 4 + (1 if u > 1.5 else 0)
    steinbogen(w, S, W + tz, hb, M, n, gel_hoch=False)
    for x in range(-S, S + 1):
        for z in range(-W, W + 1):
            w.setze(x, hb, z, w.b("cobblestone" if (x + z) % 3 else "polished_andesite"))
    pools = ["fachwerk_rot", "fachwerk_ocker", "putz_blau", "fachwerk_rot", "holz_dunkel"]
    lw = 5 if u < 2 else 6
    frei = 2 if u > 0.9 else 0
    i = 0
    x = -S + 1
    while x + lw - 1 <= S - 1:
        if abs(x + lw / 2) <= frei + lw / 2 and frei:
            x += 2 * frei + 1
            continue
        for sz in (-1, 1):
            z0, z1 = (W + 1, W + tz + 1) if sz > 0 else (-W - tz - 1, -W - 1)
            st = stil_haus(w, pools[(i + (sz > 0)) % len(pools)])
            P.gebaeude(w, st, x, z0, x + lw - 1, z1, y0=hb + 1, etagen=1 + (i % 2 if u > 1 else 0), eh=4,
                       dach="sattel", first_x=False, tuer="north" if sz > 0 else "south", sockel_h=0, gauben=False,
                       kamine=1 if i % 2 else 0)
            for xx in range(x, x + lw):
                w.setze(xx, hb, z1 + sz, treppe(w, "stone_brick_stairs", "north" if sz > 0 else "south", "top"))
        i += 1
        x += lw
    if frei:
        w.setze(0, hb + 1, 0, w.b("cauldron"))
        for z in (-W, W):
            w.setze(0, hb + 1, z, laterne(w))
    bewuchs(w, moos=0.03)
    return w


def brueckenkapelle(seed, g=2):
    """Brückenkapelle: eine dreibogige Steinbrücke, auf dem verbreiterten Mittelpfeiler steht eine kleine Kapelle
    mit Dachreiter, Statuen auf der Brüstung und Laternen."""
    w = _neu(seed)
    u = U[g]
    B = _r(6 * u + 2)
    hb = _r(1.5 * u + 2)
    W = _r(0.8 * u + 1)
    R = B + _r(9 * u + 8)
    L = flusstal(w, R, B, hb=hb, W=W, baeume=2 + g, weg="cobblestone")
    S = spannweite(L, B) + 1
    M = Mat(w, ["stone_bricks", "stone_bricks", "cracked_stone_bricks", "andesite", "mossy_stone_bricks"])
    steinbogen(w, S, W, hb, M, 3)
    for x in range(-S, S + 1):
        for z in range(-W, W + 1):
            w.setze(x, hb, z, w.b("stone_bricks" if (x + z) % 2 else "polished_andesite"))
    k = _r(1.6 * u + 2)
    for x in range(-k, k + 1):
        for z in range(-W - 2 * k, -W):
            for y in range(-2, hb + 1):
                w.setze(x, y, z, M(x, y, z, 0.5))
    st = P.Stil(w, wand="kalkstein" if "kalkstein" in P.WAENDE else "marmor", sockel="graustein",
                gesims="stone_brick", dach="schiefer", holz="spruce")
    P.gebaeude(w, st, -k + 1, -W - 2 * k + 1, k - 1, -W - 1, y0=hb + 1, etagen=1, eh=_r(3 * u + 2), dach="sattel",
               first_x=False, tuer="south", sockel_h=0, gauben=False, kamine=0, steil=True)
    for xs in range(-S + 3, S - 2, max(5, S // 2)):
        if abs(xs) <= k + 1:
            continue
        for z in (-W - 1, W + 1):
            w.setze(xs, hb + 1, z, w.b("chiseled_stone_bricks"))
            w.setze(xs, hb + 2, z, w.b("andesite_wall", east="none", west="none", north="none", south="none",
                                       up=True, waterlogged=False))
            w.setze(xs, hb + 3, z, w.b("polished_andesite"))
    for z in (-W - 1, W + 1):
        for xs in (-S + 1, S - 1):
            w.setze(xs, hb + 2, z, laterne(w))
    bewuchs(w, moos=0.05)
    return w


def baumstammbruecke(seed, g=2):
    """Baumstammbrücke: ein umgestürzter Urwaldriese liegt über einer Felsschlucht, mit Wurzelteller, Aststummeln,
    Moos auf dem Rücken, Pilzen und einem Seilgeländer an Pflöcken."""
    w = _neu(seed)
    u = U[g]
    B = _r(2 * u + 1)
    hb = _r(6 * u + 3)
    R = B + _r(10 * u + 8)
    L = flusstal(w, R, B, hb=hb, steil=3, W=1, baeume=3 + g, arten=("fichte", "oak", "birch"), weg=None,
                 dichte=0.45)
    S = spannweite(L, B) + 3
    r = 1.2 * u + 0.8
    yc = hb + r - 0.4
    rn = Rauschen(w, 2)
    for x in range(-S - 2, S + 3):
        rr = r * (1 - 0.15 * (x + S) / (2 * S))
        for y in range(int(yc - rr) - 1, int(yc + rr) + 2):
            for z in range(-int(rr) - 1, int(rr) + 2):
                d = math.hypot(y - yc, z)
                if d <= rr:
                    aussen = d > rr - 1.1
                    if aussen and y > yc + rr * 0.5 and rn(x, y, z) < 0.6:
                        b = w.b("moss_block")
                    elif aussen:
                        b = w.b("spruce_wood" if (x + z) % 5 else "dark_oak_wood", axis="x")
                    else:
                        b = w.b("stripped_spruce_log", axis="x")
                    w.setze(x, y, z, b)
    xe = -S - 3
    rw = r * 2.2
    for y in range(int(yc - rw), int(yc + rw) + 1):
        for z in range(-int(rw), int(rw) + 1):
            d = math.hypot(y - yc, z)
            if d < rw and rn(xe, y * 2, z * 2) < 0.8:
                w.setze(xe, y, z, w.b("rooted_dirt" if d < rw * 0.6 else "mangrove_roots"))
                if d > rw * 0.6:
                    w.setze(xe - 1, y, z, w.b("mangrove_roots"), False)
    rng = w.rng
    for k in range(int(4 * u) + 2):
        x = int(rng.integers(-S, S))
        sz = 1 if k % 2 else -1
        linie(w, (x, yc, sz * r), (x + 2, yc + 2 + rng.random() * 2, sz * (r + 2 + rng.random() * 2)),
              w.b("spruce_wood", axis="y"), 0.0)
    top = round(yc + r)
    for x in range(-S - 1, S + 2):
        if (x, top + 1, 0) not in w.bloecke:
            w.setze(x, top + 1, 0, w.b("moss_carpet") if rng.random() < 0.5 else w.b("grass"))
        if x % 3 == 0 and abs(x) > B + 1:
            for zz in (-round(r) - 1, round(r) + 1):
                for y in range(hb + 1, top + 3):
                    w.setze(x, y, zz, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                          waterlogged=False), False)
        if rng.random() < 0.08:
            w.setze(x, top + 1, 1, w.b("red_mushroom" if rng.random() < 0.5 else "brown_mushroom"), False)
    for zz in (-round(r) - 1, round(r) + 1):
        for x in range(-S - 1, S + 2):
            if (x, top + 2, zz) not in w.bloecke:
                w.setze(x, top + 2, zz, w.b("chain", axis="x", waterlogged=False))
    return w


def pontonbruecke(seed, g=2):
    """Pontonbrücke: eine Reihe vertäuter Holzkähne trägt einen Bohlenweg über einen breiten Strom, mit
    Seilgeländer, Laternenpfählen und Rampen an beiden Ufern."""
    w = _neu(seed)
    u = U[g]
    B = _r(8 * u + 3)
    W = _r(0.8 * u + 1)
    R = B + _r(8 * u + 8)
    L = flusstal(w, R, B, hb=1, W=W, baeume=2 + g, arten=("weide", "oak"), tiefe=3)
    S = spannweite(L, B) + 1
    holz = ["spruce", "dark_oak", "oak"][seed % 3]
    for x in range(-S, S + 1):
        boot = (x + S) % 4 in (1, 2) and abs(x) < B
        if boot:
            for z in range(-W - 2, W + 3):
                rand = abs(z) == W + 2
                w.setze(x, 0, z, w.b(f"{holz}_planks") if not rand else
                        treppe(w, f"{holz}_stairs", "south" if z < 0 else "north"))
                w.setze(x, -1, z, w.b(f"stripped_{holz}_log", axis="z"))
        for z in range(-W, W + 1):
            w.setze(x, 1, z, platte(w, f"{holz}_slab") if abs(x) < B - 1 else w.b(f"{holz}_planks"))
        for z in (-W - 1, W + 1):
            if x % 4 == 0:
                w.setze(x, 1, z, w.b(f"{holz}_fence", north=False, south=False, east=False, west=False,
                                     waterlogged=abs(x) < B))
                w.setze(x, 2, z, w.b(f"{holz}_fence", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
                if x % 12 == 0:
                    w.setze(x, 3, z, laterne(w))
            else:
                w.setze(x, 2, z, w.b("chain", axis="x", waterlogged=False))
    for sx in (-1, 1):
        x = sx * (B - 2)
        for zz in (-W - 4, W + 4):
            for y in range(-2, 3):
                w.setze(x, y, zz, w.b(f"{holz}_log", axis="y"))
    return w


def klappbruecke(seed, g=1):
    """Klappbrücke: eine weiß gestrichene, hölzerne Zugbrücke über einen ummauerten Kanal – zwei Portale tragen die
    Waagebalken, Ketten führen hinab zur Fahrbahn; ein Kahn liegt im Kanal."""
    w = _neu(seed)
    u = U[g]
    B = _r(3 * u + 2)
    R = B + _r(10 * u + 8)
    W = _r(0.8 * u + 1)
    gelaende(w, R, art="wiese", dichte=0.3)
    Mk = Mat(w, ["bricks", "stone_bricks", "bricks", "mud_bricks"])
    D = 2
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) > R:
                continue
            if abs(x) <= B:
                for y in range(-2, D):
                    w.bloecke.pop((x, y, z), None)
                for y in range(-2, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -3, z, w.b("mud"))
            elif abs(x) <= B + 1:
                for y in range(-2, D):
                    w.setze(x, y, z, Mk(x, y, z, 0.5))
                w.setze(x, D, z, platte(w, "smooth_stone_slab"))
            elif abs(x) <= B + 3:
                w.bloecke.pop((x, 1, z), None)
                for y in range(1, D):
                    w.setze(x, y, z, w.b("dirt"))
                w.setze(x, D - 1, z, w.b("grass_block", snowy=False))
    for x in range(-R, R + 1):
        for z in range(-W, W + 1):
            if abs(x) > B + 1 and math.hypot(x, z) <= R:
                w.bloecke.pop((x, 1, z), None)
                w.setze(x, 0, z, w.b("cobblestone" if (x + z) % 2 else "stone_bricks"))
    for x in range(-B - 1, B + 2):
        for z in range(-W, W + 1):
            w.setze(x, D, z, w.b("birch_planks"))
        for z in (-W - 1, W + 1):
            w.setze(x, D + 1, z, w.b("birch_fence", east=True, west=True, north=False, south=False,
                                     waterlogged=False))
            w.setze(x, D, z, w.b("white_concrete"))
    H = _r(4 * u + 5)
    for sx in (-1, 1):
        xp = sx * (B + 2)
        for z in (-W - 1, W + 1):
            for y in range(D, D + H):
                w.setze(xp, y, z, w.b("white_concrete"))
        for z in range(-W - 1, W + 2):
            w.setze(xp, D + H, z, w.b("white_concrete"))
        lang = B + 4
        for z in (-W - 1, W + 1):
            for d in range(-3, lang):
                w.setze(xp - sx * d, D + H + 1, z, w.b("white_concrete"))
            for y in range(D + 1, D + H + 1):
                w.setze(xp - sx * (lang - 1), y, z, w.b("chain", axis="y", waterlogged=False), False)
            w.setze(xp + sx * 3, D + H + 2, z, w.b("black_concrete"))
    from boote import ruderboot
    try:
        b = ruderboot(seed, 0)
        einfuegen(w, b, 0, -1, W + 4 + _r(2 * u))
    except Exception:
        pass
    return w


def eisbruecke(seed, g=2):
    """Eisbogen: ein natürlicher Bogen aus Packeis und Blaueis spannt sich über einen zugefrorenen Fluss, mit
    Eiszapfen an der Unterseite, Schneewehen auf dem Rücken und verschneiten Fichten."""
    w = _neu(seed)
    u = U[g]
    B = _r(5 * u + 2)
    hb = _r(1 * u + 1)
    R = B + _r(10 * u + 8)
    W = _r(1 * u + 1)
    L = flusstal(w, R, B, hb=hb, gras="snow_block", W=W, baeume=3 + g, arten=("fichte", "kiefer"), weg=None,
                 schilf=False, dichte=0.0)
    for (x, z), sp in L.wasser.items():
        w.setze(x, sp, z, w.b("ice" if (x * 3 + z) % 7 else "packed_ice"))
    S = spannweite(L, B) + 2
    Hb = _r(5 * u + 3)
    rn = Rauschen(w, 3)
    for x in range(-S, S + 1):
        t = x / S
        top = hb + Hb * (1 - t * t) + 1
        dick = 1.6 + 1.2 * t * t + 0.8 * rn(x, 0, 0)
        for z in range(-W, W + 1):
            zz = abs(z) / (W + 0.5)
            obern = top - zz * zz * 1.2
            for y in range(int(obern - dick), int(obern) + 1):
                if y < 0:
                    continue
                k = rn(x, y, z)
                w.setze(x, y, z, w.b("blue_ice" if k < 0.3 else "packed_ice" if k < 0.8 else "ice"))
            w.setze(x, int(obern) + 1, z, w.b("snow", layers=1 + int(rn(x, 5, z) * 3)), False)
            if w.rng.random() < 0.18:
                yy = int(obern - dick) - 1
                for k in range(int(1 + w.rng.integers(3))):
                    if yy - k > 0:
                        w.setze(x, yy - k, z, w.b("ice"), False)
    return w


def zollbruecke(seed, g=2):
    """Zollbrücke: eine gemauerte Brücke mit einem trutzigen Brückenturm über der Fahrbahn am einen Ende, einem
    Schlagbaum und einem kleinen Zollhäuschen am anderen."""
    w = _neu(seed)
    u = U[g]
    B = _r(5 * u + 2)
    hb = _r(1.5 * u + 2)
    W = _r(0.8 * u + 1)
    R = B + _r(11 * u + 8)
    L = flusstal(w, R, B, hb=hb, W=W, baeume=2 + g, weg="cobblestone")
    S = spannweite(L, B) + 1
    M = Mat(w, ["stone_bricks", "cobblestone", "stone_bricks", "andesite", "mossy_stone_bricks"])
    steinbogen(w, S, W, hb, M, 2 if u < 1.5 else 3)
    for x in range(-S, S + 1):
        for z in range(-W, W + 1):
            w.setze(x, hb, z, w.b("cobblestone"))
    a = W + 2
    H = _r(9 * u + 6)
    x0 = S + 1
    x1 = x0 + 2 * a
    for x in range(x0, x1 + 1):
        for z in range(-a, a + 1):
            for y in range(-1, hb + H):
                rand = x in (x0, x1) or abs(z) == a
                if not rand and y > hb:
                    if (y - hb) % 5 == 0:
                        w.setze(x, y, z, w.b("spruce_planks"))
                    continue
                durchgang = abs(z) <= W and hb < y <= hb + 4 + (1 if abs(z) < W else 0)
                if durchgang:
                    continue
                fenster = rand and (y - hb) % 5 == 3 and y > hb + 5 and (z == 0 or (x - x0) == a)
                w.setze(x, y, z, w.b("glass_pane", north=True, south=True, east=False, west=False,
                                     waterlogged=False) if fenster and abs(z) == a else M(x, y, z, y / H))
        for z in range(-a, a + 1):
            if (x + z) % 2 == 0 and (x in (x0, x1) or abs(z) == a):
                w.setze(x, hb + H, z, M(x, 0, z, 0.9))
    for k in range(a + 1):
        for x in range(x0 + k, x1 - k + 1):
            for z in (-a + k, a - k):
                w.setze(x, hb + H + 1 + k, z, treppe(w, "deepslate_tile_stairs", "south" if z < 0 else "north"))
        for z in range(-a + k, a - k + 1):
            for x in (x0 + k, x1 - k):
                w.setze(x, hb + H + 1 + k, z, treppe(w, "deepslate_tile_stairs", "east" if x == x0 + k else
                                                     "west"))
    w.setze(x0 + a, hb + H + 2 + a, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for z in range(-W, W + 1):
        w.setze(-S - 1, hb + 2, z, w.b("red_wool" if z % 2 else "white_wool"))
    for y in range(hb + 1, hb + 3):
        w.setze(-S - 1, y, -W - 1, w.b("spruce_log", axis="y"))
    st = stil_haus(w, "holz_dunkel")
    P.gebaeude(w, st, -S - 6, W + 2, -S - 2, W + 5, y0=hb + 1, etagen=1, eh=3, dach="sattel", tuer="north",
               sockel_h=0, gauben=False, kamine=0)
    return w


def buckelbruecke(seed, g=1):
    """Buckelbrücke: eine schmale, steile Saumpfadbrücke mit einem einzigen Halbkreisbogen aus Bruchstein über einen
    Wildbach, niedrige bemooste Brüstung, Farne in den Fugen."""
    w = _neu(seed)
    u = U[g]
    B = _r(2.5 * u + 1)
    R = B + _r(10 * u + 6)
    L = flusstal(w, R, B, hb=1, W=1, baeume=3 + g, arten=("birke", "fichte"), weg="coarse_dirt", tiefe=1)
    S = spannweite(L, B) + 1
    M = Mat(w, ["cobblestone", "mossy_cobblestone", "stone", "andesite", "mossy_cobblestone"])
    Hb = _r(2.4 * u + 2)
    for x in range(-S - 2, S + 3):
        t = min(1.0, abs(x) / (S + 2))
        top = 1 + round(Hb * math.cos(t * math.pi / 2))
        for z in (-1, 0, 1):
            for y in range(-1, top + 1):
                if abs(x) < S - 0.5 and y < top - 1 and (x / (S - 0.5)) ** 2 + ((y + 1) / (Hb + 0.5)) ** 2 < 1:
                    continue
                w.setze(x, y, z, M(x, y, z, 0.5))
        for z in (-2, 2):
            w.setze(x, top, z, M(x, top, z, 0.6))
            w.setze(x, top + 1, z, mauer(w, "mossy_cobblestone_wall", "x") if w.rng.random() < 0.8 else
                    w.b("fern"))
    bewuchs(w, moos=0.15, ranken=0.15)
    return w


def eisenbruecke(seed, g=2):
    """Fachwerkträgerbrücke: zwei grün gestrichene Stahlträger mit Diagonalen und Querverstrebungen über einem Strom,
    Bohlenfahrbahn, Nietenleisten und Steinwiderlager mit Laternen."""
    w = _neu(seed)
    u = U[g]
    B = _r(6 * u + 2)
    hb = _r(1.5 * u + 2)
    W = _r(1 * u + 1)
    R = B + _r(9 * u + 8)
    L = flusstal(w, R, B, hb=hb, W=W, baeume=2 + g)
    S = spannweite(L, B) + 1
    Ms = Mat(w, ["stone_bricks", "andesite", "cobblestone", "stone_bricks"])
    st = "waxed_weathered_cut_copper" if _stil(seed) else "waxed_oxidized_cut_copper"
    H = _r(3 * u + 3)
    for x in list(range(-S - 2, -S + 1)) + list(range(S, S + 3)):
        for z in range(-W - 2, W + 3):
            for y in range(-3, hb + 1):
                w.setze(x, y, z, Ms(x, y, z, 0.5))
    if B > 6:
        for x in (-1, 0, 1):
            for z in range(-W - 2, W + 3):
                for y in range(-3, hb):
                    w.setze(x, y, z, Ms(x, y, z, 0.5))
    for x in range(-S, S + 1):
        for z in range(-W, W + 1):
            w.setze(x, hb, z, w.b("spruce_planks"))
        for z in (-W - 1, W + 1):
            w.setze(x, hb, z, w.b(st))
            w.setze(x, hb + H, z, w.b(st))
    feld = max(3, H)
    for z in (-W - 1, W + 1):
        for x in range(-S, S + 1, feld):
            for y in range(hb, hb + H + 1):
                w.setze(x, y, z, w.b(st))
            nx = min(S, x + feld)
            if x < 0:
                linie(w, (x, hb + H, z), (nx, hb, z), w.b(st))
            else:
                linie(w, (x, hb, z), (nx, hb + H, z), w.b(st))
    for x in range(-S, S + 1, feld):
        for z in range(-W, W + 1):
            w.setze(x, hb + H, z, w.b(st))
    for x in (-S - 1, S + 1):
        for z in (-W - 2, W + 2):
            w.setze(x, hb + 1, z, laterne(w))
    return w


def muehlenbruecke(seed, g=2):
    """Mühlenbrücke: eine zweibogige Steinbrücke, an deren Flanke eine Wassermühle über dem Fluss steht – mit
    großem Wasserrad im Strom, Mühlgerinne und Mehlsäcken."""
    w = _neu(seed)
    u = U[g]
    B = _r(5 * u + 2)
    hb = _r(1.5 * u + 2)
    W = _r(0.8 * u + 1)
    R = B + _r(9 * u + 8)
    L = flusstal(w, R, B, hb=hb, W=W, baeume=2 + g)
    S = spannweite(L, B) + 1
    M = Mat(w, ["stone_bricks", "cobblestone", "mossy_cobblestone", "andesite"])
    steinbogen(w, S, W, hb, M, 2)
    a = _r(2.2 * u + 2)
    x0, x1 = 2, 2 + 2 * a
    z0, z1 = W + 2, W + 2 + 2 * a
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            for y in range(-2, hb + 1):
                if (x in (x0, x1) or z in (z0, z1)) or y == hb:
                    w.setze(x, y, z, M(x, y, z, 0.4))
    st = stil_haus(w, "fachwerk_ocker")
    P.gebaeude(w, st, x0, z0, x1, z1, y0=hb + 1, etagen=1 + (g > 1), eh=4, dach="sattel", tuer="north",
               sockel_h=0, gauben=False, kamine=1)
    rr = _r(2.2 * u + 2)
    xr = x0 - 2
    zc = (z0 + z1) // 2
    for k in range(int(rr * 10)):
        t = k / (rr * 10) * 6.283
        for d in (rr, rr - 0.5):
            w.setze(xr, round(1 + math.sin(t) * d), round(zc + math.cos(t) * d), w.b("spruce_planks"))
    for k in range(8):
        t = k / 8 * 6.283
        linie(w, (xr, 1, zc), (xr, 1 + math.sin(t) * rr, zc + math.cos(t) * rr), w.b("stripped_spruce_log",
                                                                                     axis="x"))
    w.setze(xr + 1, 1, zc, w.b("spruce_log", axis="x"))
    for k in range(3):
        w.setze(x1 - 1 - k, hb + 1, z1 + 1, w.b("white_wool" if k % 2 else "barrel", **(
            {} if k % 2 else {"facing": "up", "open": False})), False)
    return w


def steinplattenbruecke(seed, g=1):
    """Steinplattenbrücke: uralte, grob gestapelte Steinpfeiler im seichten Bach, darüber liegen mächtige
    Granitplatten – Moos, Farn und Bachkiesel drumherum."""
    w = _neu(seed)
    u = U[g]
    B = _r(4 * u + 2)
    R = B + _r(9 * u + 6)
    L = flusstal(w, R, B, hb=1, W=1, baeume=2 + g, arten=("birke", "oak"), weg="coarse_dirt", tiefe=1)
    L.steine(int(4 * u) + 2, 0.9)
    S = spannweite(L, B) + 1
    M = Mat(w, ["stone", "andesite", "tuff", "cobblestone", "mossy_cobblestone"])
    pf = 4
    xs = list(range(-S, S + 1, pf))
    for x in xs:
        for dx in (0, 1):
            for z in (-1, 0, 1):
                for y in range(-2, 1):
                    w.setze(x + dx, y, z, M(x, y, z, 0.5))
    for x in range(-S, S + 2):
        for z in (-1, 0, 1):
            w.setze(x, 1, z, w.b("smooth_stone" if (x // pf) % 2 else "stone"))
        if x % pf == 0:
            w.setze(x, 1, 2, w.b("stone_slab", type="bottom", waterlogged=False))
    bewuchs(w, moos=0.25)
    return w


def schluchtbruecke(seed, g=3):
    """Schluchtbrücke: ein kühner, schlanker Steinbogen spannt sich hoch über eine enge Felsschlucht, tief unten
    rauscht der Fluss; Brüstung mit Laternen, Felswände mit Moos und Kiefern am Rand."""
    w = _neu(seed)
    u = U[g]
    B = _r(2 * u + 1)
    hb = _r(10 * u + 6)
    W = _r(0.8 * u + 1)
    R = B + _r(9 * u + 8)
    L = flusstal(w, R, B, hb=hb, steil=4, W=W, baeume=3 + g, arten=("kiefer", "fichte"), weg="gravel")
    S = spannweite(L, B) + 1
    M = Mat(w, ["stone_bricks", "stone_bricks", "cracked_stone_bricks", "andesite"])
    for x in range(-S - 1, S + 2):
        t = x / (S + 0.5)
        unten = hb - 2 - (hb - 3) * math.sqrt(max(0.0, 1 - t * t)) * 0.75
        for z in range(-W, W + 1):
            for y in range(int(unten), hb + 1):
                if y >= L.h.get((x, z), 0) - 0 or abs(x) <= S:
                    w.setze(x, y, z, M(x, y, z, 0.5))
        for z in (-W - 1, W + 1):
            w.setze(x, hb, z, M(x, hb, z, 0.8))
            w.setze(x, hb + 1, z, mauer(w, "stone_brick_wall", "x", up=x % 4 == 0))
            if x % 8 == 0:
                w.setze(x, hb + 2, z, laterne(w))
        for z in range(-W, W + 1):
            w.setze(x, hb, z, w.b("gravel" if (x + z) % 3 else "cobblestone"))
    bewuchs(w, moos=0.08, ranken=0.1)
    return w


def stufenbruecke(seed, g=2):
    """Stufenbrücke am Kanal: zwischen hohen Stadthäusern führt eine steile Bogenbrücke mit Treppenstufen und
    weißer Balustrade über einen Kanal; eine Gondel liegt am Pfahl."""
    w = _neu(seed)
    u = U[g]
    B = _r(2.5 * u + 2)
    R = B + _r(10 * u + 8)
    W = _r(0.8 * u + 1)
    Mk = Mat(w, ["stone_bricks", "polished_andesite", "stone_bricks"])
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if abs(x) <= B:
                for y in range(-2, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -3, z, w.b("mud"))
            else:
                for y in range(-2, 2):
                    w.setze(x, y, z, Mk(x, y, z, 0.5) if abs(x) == B + 1 else w.b("dirt"))
                w.setze(x, 2, z, w.b("smooth_stone" if abs(x) == B + 1 else
                                     ("stone_bricks" if (x + z) % 2 else "polished_andesite")))
    pools = ["putz_blau", "fachwerk_ocker", "kalk_kupfer", "rot", "putz_blau", "sand"]
    i = 0
    for sx in (-1, 1):
        for z0 in range(-R + 1, R - 5, 7):
            if -W - 2 <= z0 + 5 and z0 <= W + 2:
                continue
            xa = sx * (B + 2)
            xb = sx * (B + 2 + _r(3 * u + 4))
            st = stil_haus(w, pools[i % len(pools)])
            P.gebaeude(w, st, min(xa, xb), z0, max(xa, xb), z0 + 5, y0=3, etagen=2 + (i % 2), eh=4, dach="sattel",
                       first_x=False, tuer="east" if sx < 0 else "west", sockel_h=0, gauben=False, kamine=1)
            i += 1
    S = B + 2
    Hb = _r(1.2 * u + 2)
    for x in range(-S - Hb, S + Hb + 1):
        d = abs(x)
        stufe = max(0, min(Hb, S + Hb - d))
        top = 2 + stufe
        for z in range(-W, W + 1):
            for y in range(-2, top + 1):
                if abs(x) <= B and y < top - 1 and (x / (B + 0.3)) ** 2 + ((y + 2) / (Hb + 3)) ** 2 < 1:
                    continue
                w.setze(x, y, z, w.b("stone_bricks"))
            if d > S - 1 and stufe > 0 and stufe < Hb + 1:
                w.setze(x, top + 1, z, treppe(w, "stone_brick_stairs", "east" if x < 0 else "west"), False) \
                    if False else None
        for z in (-W - 1, W + 1):
            w.setze(x, top, z, w.b("smooth_quartz"))
            w.setze(x, top + 1, z, w.b("quartz_slab", type="bottom", waterlogged=False) if x % 2 else
                    w.b("quartz_pillar", axis="y"))
    for z in range(W + 3, W + 6):
        w.setze(0, 1, z, w.b("black_concrete"))
    w.setze(0, 2, W + 3, w.b("black_concrete"))
    for y in range(-1, 4):
        w.setze(1, y, W + 7, w.b("stripped_spruce_log", axis="y"))
    w.setze(1, 4, W + 7, w.b("red_wool"))
    return w


def seilfaehre(seed, g=2):
    """Seilfähre: ein Floß mit Geländer hängt an einem über den Strom gespannten Seil zwischen zwei hohen Pfosten,
    Anlegestege an beiden Ufern, ein Fährhaus mit Glocke."""
    w = _neu(seed)
    u = U[g]
    B = _r(8 * u + 3)
    R = B + _r(8 * u + 8)
    L = flusstal(w, R, B, hb=1, W=1, baeume=2 + g, arten=("weide", "oak"), tiefe=3)
    S = spannweite(L, B)
    H = _r(4 * u + 5)
    for sx in (-1, 1):
        x = sx * (S + 1)
        for y in range(1, H + 1):
            w.setze(x, y, 2, w.b("spruce_log", axis="y"))
        for xs in range(sx * (B - 2), sx * (S + 1), sx):
            for z in (-1, 0, 1):
                w.setze(xs, 1, z, w.b("spruce_planks"))
            w.setze(xs, 0, -2, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                   waterlogged=True)) if xs % 3 == 0 and abs(xs) < B else None
    for x in range(-S - 1, S + 2):
        w.setze(x, H, 2, w.b("chain", axis="x", waterlogged=False), False)
    fx = round(B * 0.3)
    for x in range(fx - 3, fx + 4):
        for z in range(-2, 3):
            w.setze(x, 0, z, w.b("spruce_log", axis="z") if abs(x - fx) == 3 else w.b("spruce_planks"))
        for z in (-2, 2):
            w.setze(x, 1, z, zaun(w, "spruce_fence", "x"))
    for y in range(1, H):
        w.setze(fx, y, 2, w.b("chain", axis="y", waterlogged=False))
    st = stil_haus(w, "holz_dunkel")
    P.gebaeude(w, st, -S - 7, -6, -S - 2, -2, y0=2, etagen=1, eh=3, dach="sattel", tuer="east", sockel_h=0,
               gauben=False, kamine=1)
    w.setze(-S - 1, 3, 0, w.b("bell", attachment="floor", facing="east", powered=False))
    return w


def zickzacksteg(seed, g=2):
    """Zickzacksteg: ein rot lackierter Holzsteg windet sich in scharfen Knicken über einen Seerosenteich, mit
    Laternen an den Ecken, Lotusblättern, Schilf und Trauerweiden am Ufer."""
    w = _neu(seed)
    u = U[g]
    R = _r(13 * u + 6)
    L = Land(w, R)
    L.see(0, 0, R * 0.72, 0, tiefe=2)
    L.bauen(unten=-3)
    L.bepflanzen(dichte=0.4, baeume=0)
    baeume_weg(w, L, 2 + g, 0, ("weide", "kirsche"))
    rng = w.rng
    for (x, z), sp in L.wasser.items():
        if rng.random() < 0.08:
            w.setze(x, 1, z, w.b("lily_pad"))
    n = 5 + g
    pts = []
    for k in range(n + 1):
        x = round(-R * 0.85 + k * (1.7 * R / n))
        z = round((1 if k % 2 else -1) * R * 0.18)
        pts.append((x, z))
    for (a, b) in zip(pts, pts[1:]):
        steps = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
        for i in range(steps + 1):
            t = i / steps
            x, z = round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t)
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    w.setze(x + dx, 1, z + dz, w.b("dark_oak_planks"))
            if i % 3 == 0:
                w.setze(x, 0, z, w.b("dark_oak_log", axis="y"))
    for (x, z) in pts:
        for y in (2, 3):
            w.setze(x + 1, y, z + 1, w.b("red_concrete" if y == 2 else "stone_brick_wall", **(
                {} if y == 2 else {"east": "none", "west": "none", "north": "none", "south": "none", "up": True,
                                   "waterlogged": False})))
        w.setze(x + 1, 4, z + 1, laterne(w))
    return w


def bogensteg(seed, g=2):
    """Moderner Bogensteg: ein schräg gestellter weißer Stahlbogen trägt an Seilen einen schlanken Steg über einen
    Fluss, Glasgeländer, Lichtbänder und Treppen an den Ufern."""
    w = _neu(seed)
    u = U[g]
    B = _r(7 * u + 2)
    hb = _r(1 * u + 2)
    W = _r(0.6 * u + 1)
    R = B + _r(9 * u + 8)
    L = flusstal(w, R, B, hb=hb, W=W, baeume=2 + g, arten=("birke", "oak"), weg="smooth_stone")
    S = spannweite(L, B) + 1
    H = _r(6 * u + 4)
    zb = W + 3
    for x in range(-S, S + 1):
        for z in range(-W, W + 1):
            w.setze(x, hb, z, platte(w, "smooth_stone_slab", "top") if abs(z) < W else w.b("white_concrete"))
        for z in (-W - 1, W + 1):
            w.setze(x, hb, z, w.b("sea_lantern" if x % 6 == 0 else "white_concrete"))
            w.setze(x, hb + 1, z, w.b("glass_pane", east=True, west=True, north=False, south=False,
                                      waterlogged=False))
    pk = []
    for x in range(-S, S + 1):
        t = x / S
        y = hb + H * (1 - t * t)
        z = zb - (y - hb) * 0.25
        pk.append((x, y, z))
        for dy in (0, 1):
            w.setze(x, round(y) + dy, round(z), w.b("white_concrete"))
    for (x, y, z) in pk[2:-2:3]:
        linie(w, (x, y, z), (x, hb + 1, W + 1), w.b("chain", axis="y", waterlogged=False), 0.0, False)
    return w


# ============================================================================ Tore

def palisadentor(seed, g=2):
    """Palisadentor: eine Wand aus angespitzten Stämmen mit einem schweren Doppeltor, flankiert von zwei hölzernen
    Wachtürmen mit Plattform und Schindeldach, Fackeln und roten Wimpeln."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.35)
    H = _r(5 * u + 4)
    T = _r(1.2 * u + 1)
    rng = w.rng
    for z in range(-R, R + 1):
        if math.hypot(0, z) > R:
            continue
        if abs(z) <= T:
            continue
        h = H + int(rng.integers(0, 2))
        for y in range(1, h + 1):
            w.setze(0, y, z, w.b("spruce_log" if (z % 3) else "dark_oak_log", axis="y"))
        w.setze(0, h + 1, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                  waterlogged=False))
        w.setze(-1, H - 1, z, w.b("spruce_planks"))
    for x in range(-R, R + 1):
        for z in range(-T, T + 1):
            w.bloecke.pop((x, 1, z), None)
            w.setze(x, 0, z, w.b("dirt_path" if rng.random() < 0.8 else "coarse_dirt"))
    for z in range(-T, T + 1):
        w.setze(0, H + 1, z, w.b("spruce_log", axis="z"))
        for y in (1, 2, 3):
            w.setze(1 + (1 if z < 0 else 1), y, z, w.b("spruce_planks")) if abs(z) == T and False else None
    for z in (-T, T):
        for y in range(1, H):
            w.setze(1 + abs(z) - T + T, y, z + (1 if z < 0 else -1) * 0, w.b("dark_oak_planks")) if False else None
    for dz in range(T):
        for y in range(1, H - 1):
            w.setze(1 + dz, y, -T, w.b("dark_oak_planks"))
            w.setze(1 + dz, y, T, w.b("dark_oak_planks"))
    a = _r(1.5 * u + 1)
    Ht = H + _r(3 * u + 2)
    for sz in (-1, 1):
        zc = sz * (T + a + 1)
        for x in (-a, a):
            for z in (zc - a, zc + a):
                for y in range(1, Ht + 1):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
        for x in range(-a - 1, a + 2):
            for z in range(zc - a - 1, zc + a + 2):
                w.setze(x, Ht - 3, z, w.b("spruce_planks"))
                if abs(x) == a + 1 or abs(z - zc) == a + 1:
                    w.setze(x, Ht - 2, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                              waterlogged=False))
        for k in range(a + 2):
            for x in range(-a - 1 + k, a + 2 - k):
                for z in range(zc - a - 1 + k, zc + a + 2 - k):
                    if abs(x) == a + 1 - k or abs(z - zc) == a + 1 - k:
                        w.setze(x, Ht + 1 + k, z, w.b("spruce_planks" if k == a + 1 else "dark_oak_planks"))
        w.setze(0, Ht + a + 3, zc, w.b("red_wool"))
        for y in range(1, Ht - 3):
            w.setze(a, y, zc, w.b("ladder", facing="east", waterlogged=False), False) if False else None
    for z in (-T - 1, T + 1):
        w.setze(1, H - 1, z, w.b("wall_torch", facing="east"))
    return w


def parktor(seed, g=1):
    """Parktor: zwei Steinpfeiler mit Vasen tragen ein schmiedeeisernes Doppeltor mit Bogenaufsatz, links und rechts
    ein Eisengitter auf niedriger Mauer, eine Kiesallee mit Bäumen führt in den Park."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.3)
    T = _r(1.2 * u + 1)
    M = Mat(w, ["stone_bricks", "polished_andesite", "stone_bricks", "chiseled_stone_bricks"])
    Hp = _r(3 * u + 4)
    for z in range(-R, R + 1):
        if abs(z) <= T + 1:
            continue
        w.setze(0, 1, z, M(0, 1, z, 0.3))
        w.setze(0, 2, z, w.b("iron_bars", north=True, south=True, east=False, west=False, waterlogged=False))
        if z % 5 == 0:
            for y in (2, 3):
                w.setze(0, y, z, M(0, y, z, 0.5))
            w.setze(0, 4, z, w.b("stone_brick_slab", type="bottom", waterlogged=False))
        else:
            w.setze(0, 3, z, w.b("iron_bars", north=True, south=True, east=False, west=False, waterlogged=False))
    for sz in (-1, 1):
        zc = sz * (T + 1)
        for y in range(1, Hp + 1):
            w.setze(0, y, zc, M(0, y, zc, y / Hp))
        w.setze(0, Hp + 1, zc, w.b("flower_pot"))
        w.setze(0, Hp + 1, zc, w.b("decorated_pot", facing="east", waterlogged=False, cracked=False))
        w.setze(1, Hp - 1, zc, laterne(w))
    for z in range(-T, T + 1):
        hh = Hp - 1 + round(1.5 * math.cos(z / (T + 1) * math.pi / 2))
        for y in range(1, hh + 1):
            w.setze(0, y, z, w.b("iron_bars", north=True, south=True, east=False, west=False, waterlogged=False))
        w.setze(0, hh + 1, z, w.b("chain", axis="z", waterlogged=False))
    for x in range(-R, R + 1):
        for z in range(-T, T + 1):
            w.bloecke.pop((x, 1, z), None)
            w.setze(x, 0, z, w.b("gravel"))
        if x > 6 and x % 7 == 0:
            for sz in (-1, 1):
                einfuegen(w, wald2.laubbaum(seed + x + sz, "oak", H=_r(4 * u + 4)), x, 0, sz * (T + 6))
    for x in range(2, R):
        for sz in (-1, 1):
            w.setze(x, 1, sz * (T + 1), w.b("oak_leaves", persistent=True, distance=1, waterlogged=False), False)
    return w


def lehmtor(seed, g=2):
    """Lehmtor: ein mächtiges Wüstentor aus Lehmziegeln mit hohem Spitzbogen, Zinnenkranz, Holzbalken, die aus der
    Wand ragen, einem Band blauer Fliesen und Palmen an der Karawanenstraße."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="sand", dichte=0.2)
    M = Mat(w, ["mud_bricks", "packed_mud", "mud_bricks", "terracotta"])
    T = _r(1.3 * u + 1)
    H = _r(8 * u + 6)
    D = _r(1.5 * u + 2)
    Bt = T + _r(3 * u + 3)
    for x in range(-D, D + 1):
        for z in range(-Bt, Bt + 1):
            for y in range(1, H + 1):
                a = abs(z) / (T + 0.5)
                bogen_h = H * 0.55 + (1 - a) * H * 0.25 if a < 1 else 0
                if abs(z) <= T and y < bogen_h:
                    continue
                anlauf = abs(z) > Bt - 1 - (H - y) / H * 1.5
                w.setze(x, y, z, M(x, y, z, y / H) if not (y == round(H * 0.82) and abs(x) == D) else
                        w.b("light_blue_terracotta" if z % 2 else "cyan_terracotta"))
            if (x + z) % 2 == 0 and abs(x) == D:
                w.setze(x, H + 1, z, M(x, H + 1, z, 0.9))
        for z in range(-Bt, Bt + 1, 3):
            w.setze(x, round(H * 0.65), z, w.b("stripped_spruce_log", axis="x")) if abs(x) == D and abs(z) > T \
                else None
    for z in range(-Bt, Bt + 1, 3):
        if abs(z) > T:
            for sx in (-1, 1):
                w.setze(sx * (D + 1), round(H * 0.65), z, w.b("stripped_spruce_log", axis="x"))
    for x in range(-R, R + 1):
        for z in range(-T, T + 1):
            w.bloecke.pop((x, 1, z), None)
            w.setze(x, 0, z, w.b("smooth_sandstone" if (x + z) % 3 else "sandstone"))
    tr = _r(1.6 * u + 1.5)
    for sz in (-1, 1):
        zc = sz * (Bt + tr - 1)
        for x in range(-tr - 1, tr + 2):
            for z in range(zc - tr - 1, zc + tr + 2):
                d = math.hypot(x, z - zc)
                if d <= tr + 0.4:
                    Ht = H + _r(2 * u + 2)
                    for y in range(1, Ht + 1):
                        w.setze(x, y, z, M(x, y, z, y / Ht) if y != round(H * 0.82) else
                                w.b("light_blue_terracotta" if (x + z) % 2 else "cyan_terracotta"))
                    if d > tr - 0.8 and (x + z) % 2 == 0:
                        w.setze(x, Ht + 1, z, M(x, Ht + 1, z, 0.9))
        for y in (round(H * 0.4), round(H * 0.6)):
            w.setze(tr + 1, y, zc, w.b("spruce_trapdoor", facing="east", half="bottom", open=True, powered=False,
                                       waterlogged=False))
    for k in range(2 + g):
        x = (k // 2 + 1) * 6 * (1 if k % 2 else -1)
        einfuegen(w, wald2.palme(seed + k), x, 0, (Bt + 2 * tr + 3) * (1 if k % 3 else -1))
    return w


def sternentor(seed, g=2):
    """Sternentor: ein senkrechter Steinring auf einer Stufenplattform, dessen innerer Rand in Seelaternen- und
    Amethystlicht glimmt, umgeben von Runensteinen und einem Kreis aus Leuchtpfosten."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.3)
    M = Mat(w, ["polished_deepslate", "deepslate_bricks", "deepslate_tiles", "polished_blackstone_bricks"])
    Rr = 3.5 * u + 2.5
    r = 0.9 + 0.25 * u
    for s in range(3):
        rp = Rr + 3 - s
        for x in range(-int(rp) - 1, int(rp) + 2):
            for z in range(-int(rp * 0.6) - 1, int(rp * 0.6) + 2):
                if (x / rp) ** 2 + (z / (rp * 0.6)) ** 2 <= 1:
                    w.setze(x, 1 + s, z, w.b("smooth_quartz" if s == 2 else "calcite" if s == 1 else "polished_andesite"))
    yc = 4 + Rr
    for x in range(-int(Rr + r) - 1, int(Rr + r) + 2):
        for y in range(3, int(yc + Rr + r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(x, y - yc)
                q = (d - Rr) ** 2 + z * z
                if q <= r * r:
                    innen = d < Rr - r * 0.4
                    k = math.atan2(y - yc, x)
                    if innen and abs(z) < 1:
                        w.setze(x, y, z, w.b("sea_lantern" if int(k * 6) % 2 else "amethyst_block"))
                    else:
                        w.setze(x, y, z, w.b("chiseled_polished_blackstone") if int((k + 3.2) * 4) % 3 == 0 else
                                M(x, y, z, 0.5))
    for k in range(10):
        a = k / 10 * 6.283
        x, z = round(math.cos(a) * R * 0.75), round(math.sin(a) * R * 0.75)
        for y in range(1, 4):
            w.setze(x, y, z, w.b("chiseled_deepslate" if y == 2 else "deepslate_bricks"))
        w.setze(x, 4, z, w.b("end_rod", facing="up"))
    return w


def schleuse(seed, g=2):
    """Schleuse: ein gemauerter Kanal mit Schleusenkammer, zwei hölzerne Stemmtorpaare mit langen Schwenkbalken,
    oben höherer Wasserspiegel als unten, ein Schleusenwärterhaus mit Kurbelwinde."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    B = _r(1.5 * u + 2)
    gelaende(w, R, art="wiese", dichte=0.3)
    M = Mat(w, ["stone_bricks", "cobblestone", "stone_bricks", "mossy_stone_bricks"])
    K = _r(5 * u + 4)
    for x in range(-R, R + 1):
        oben = x < -K
        kammer = -K <= x <= K
        sp = 1 if oben else (0 if kammer else -1)
        for z in range(-B - 1, B + 2):
            for y in range(-3, 3):
                w.bloecke.pop((x, y, z), None)
            if abs(z) == B + 1:
                for y in range(-3, 3):
                    w.setze(x, y, z, M(x, y, z, 0.5))
                w.setze(x, 3, z, platte(w, "smooth_stone_slab"))
            else:
                w.setze(x, -3, z, w.b("gravel"))
                for y in range(-2, sp + 1):
                    w.setze(x, y, z, w.b("water", level=0))
    for z in range(-R, R + 1):
        for x in range(-R, R + 1):
            if abs(z) > B + 1 and math.hypot(x, z) <= R:
                if (x, 0, z) in w.bloecke:
                    for y in (1, 2):
                        w.bloecke.pop((x, y + 1, z), None)
                        w.setze(x, y, z, w.b("dirt"))
                    w.setze(x, 2, z, w.b("grass_block", snowy=False))
    for xg in (-K, K):
        for z in range(-B, B + 1):
            for y in range(-2, 3):
                w.setze(xg + (0 if abs(z) > 0 else 1 if xg > 0 else -1), y, z, w.b("dark_oak_planks"))
        for sz in (-1, 1):
            for k in range(_r(2 * u + 3)):
                w.setze(xg - (1 if xg < 0 else -1) * 0 + (k if xg > 0 else -k), 4, sz * (B + 1 + k // 2),
                        w.b("spruce_log", axis="x"))
    st = stil_haus(w, "backstein")
    P.gebaeude(w, st, -3, B + 4, 3, B + 9, y0=3, etagen=1, eh=4, dach="sattel", tuer="north", sockel_h=0,
               gauben=False, kamine=1)
    w.setze(0, 3, B + 2, w.b("grindstone", face="floor", facing="north"))
    return w


def wassertor(seed, g=2):
    """Wassertor: eine Stadtmauer überspannt einen Kanal mit einem hohen Torbogen, darin ein halb hochgezogenes
    Fallgatter, zwei Rundtürme mit Kegeldach flankieren die Einfahrt."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    B = _r(1.8 * u + 2)
    gelaende(w, R, art="wiese", dichte=0.3)
    for x in range(-R, R + 1):
        for z in range(-B, B + 1):
            for y in range(1, 3):
                w.bloecke.pop((x, y, z), None)
            for y in range(-2, 1):
                w.setze(x, y, z, w.b("water", level=0))
            w.setze(x, -3, z, w.b("gravel"))
        for z in (-B - 1, B + 1):
            for y in range(-3, 1):
                w.setze(x, y, z, w.b("stone_bricks"))
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="spruce")
    M = Mat(w, ["stone_bricks", "cobblestone", "stone_bricks", "andesite", "mossy_stone_bricks"])
    H = _r(8 * u + 6)
    D = 2
    for x in range(-D, D + 1):
        for z in range(-R, R + 1):
            if abs(z) > R * 0.95:
                continue
            for y in range(-3, H + 1):
                if abs(z) <= B and y < H * 0.5 + math.sqrt(max(0, 1 - (z / (B + 0.5)) ** 2)) * B * 0.8:
                    continue
                w.setze(x, y, z, M(x, y, z, y / H))
            if abs(x) == D and z % 2 == 0:
                w.setze(x, H + 1, z, M(x, H + 1, z, 0.9))
    for z in range(-B, B + 1):
        for y in range(round(H * 0.3), round(H * 0.5 + B * 0.8)):
            w.setze(0, y, z, w.b("iron_bars", north=True, south=True, east=False, west=False, waterlogged=False)
                    if z % 2 or y % 2 else w.b("dark_oak_fence", north=True, south=True, east=False, west=False,
                                                waterlogged=False))
    for sz in (-1, 1):
        P.turm(w, st, 0, sz * (B + _r(2 * u + 2)), 1, H + _r(3 * u + 2), _r(1.8 * u + 1.5), dach="kegel",
               krone=False, fenster=4)
    return w


def grenzposten(seed, g=1):
    """Grenzposten: eine Straße mit rot-weißem Schlagbaum, ein Wachhäuschen, ein Fahnenmast, Grenzsteine im Gras,
    ein Wegweiser und ein Holzzaun entlang der Grenze."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.35)
    T = _r(1 * u + 1)
    for x in range(-R, R + 1):
        for z in range(-T, T + 1):
            w.bloecke.pop((x, 1, z), None)
            w.setze(x, 0, z, w.b("gravel" if (x + z) % 4 else "cobblestone"))
    for z in range(-R, R + 1):
        if abs(z) > T + 1 and abs(z) <= R:
            w.setze(0, 1, z, zaun(w, "spruce_fence", "z"))
    for y in (1, 2):
        w.setze(0, y, -T - 1, w.b("stripped_spruce_log", axis="y"))
    for k in range(2 * T + 4):
        w.setze(0, 2, -T + k, w.b("red_wool" if (k // 2) % 2 else "white_wool"))
    w.setze(0, 1, T + 3, w.b("stone_bricks"))
    st = stil_haus(w, "holz_dunkel")
    P.gebaeude(w, st, 2, -T - 6, 5, -T - 2, y0=1, etagen=1, eh=3, dach="sattel", tuer="south", sockel_h=0,
               gauben=False, kamine=0)
    for y in range(1, _r(5 * u + 5)):
        w.setze(-3, y, -T - 3, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                   waterlogged=False))
    hy = _r(5 * u + 5) - 1
    for k in range(3):
        for y in range(hy - 2, hy):
            w.setze(-3 + k + 1, y, -T - 3, w.b(["black_wool", "red_wool", "yellow_wool"][k] if seed % 2 else
                                               ["blue_wool", "white_wool", "red_wool"][k]))
    for z in (-R + 3, R - 3):
        w.setze(0, 1, z, w.b("chiseled_stone_bricks"))
    w.setze(-2, 1, T + 2, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(-2, 2, T + 2, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(-2, 3, T + 2, w.b("spruce_planks"))
    return w


BRUECKEN2 = {
    "ueberdachte_bruecke": ("Überdachte Holzbrücke", ueberdachte_bruecke),
    "viadukt": ("Viadukt", viadukt),
    "haeuserbruecke": ("Häuserbrücke", haeuserbruecke),
    "brueckenkapelle": ("Brücke mit Kapelle", brueckenkapelle),
    "baumstammbruecke": ("Baumstammbrücke", baumstammbruecke),
    "pontonbruecke": ("Pontonbrücke", pontonbruecke),
    "klappbruecke": ("Klappbrücke", klappbruecke),
    "eisbruecke": ("Eisbogen", eisbruecke),
    "zollbruecke": ("Zollbrücke", zollbruecke),
    "buckelbruecke": ("Buckelbrücke", buckelbruecke),
    "eisenbruecke": ("Fachwerkträgerbrücke", eisenbruecke),
    "muehlenbruecke": ("Mühlenbrücke", muehlenbruecke),
    "steinplattenbruecke": ("Steinplattenbrücke", steinplattenbruecke),
    "schluchtbruecke": ("Schluchtbrücke", schluchtbruecke),
    "stufenbruecke": ("Stufenbrücke am Kanal", stufenbruecke),
    "seilfaehre": ("Seilfähre", seilfaehre),
    "zickzacksteg": ("Zickzacksteg", zickzacksteg),
    "bogensteg": ("Moderner Bogensteg", bogensteg),
    "palisadentor": ("Palisadentor", palisadentor),
    "parktor": ("Parktor", parktor),
    "lehmtor": ("Lehmtor", lehmtor),
    "sternentor": ("Sternentor", sternentor),
    "schleuse": ("Schleuse", schleuse),
    "wassertor": ("Wassertor", wassertor),
    "grenzposten": ("Grenzposten", grenzposten),
}

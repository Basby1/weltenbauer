"""Elfenreich II – zwanzig weitere Elfenbauten: Sängerhain, Blattkuppelhaus, Lichtbogenbrücke, Silberschmiede,
Sternlauschturm, Wurzelhalle, Hängende Gärten, Weidenlaubengang, Ratskreis, Blütenbrunnen, Seidenweberei,
Leuchtkäferlichtung, Hirschstall, Harfenpavillon, Tor der Jahreszeiten, Beerenkelterei, Seerosenpavillon, Uferturm,
Wächterallee und Elfenaquädukt."""

from __future__ import annotations

import math

from erw_basis import M, S, baumrand, birke, figur, hoehe, wiese
from erw_markt import mensch
from feinbau import Dachmat, kegeldach, laterne
from flora import _neu
from leuchtwald2 import baum_aeste, bez, kugel, laubball, rohr
from lib import Rauschen
from skulptur import ell, kap, torus

WEISS = M if False else None
LAUB = ("birch_leaves", "azalea_leaves", "flowering_azalea_leaves")


def stein(w):
    return M(w, [("calcite", 3), ("smooth_quartz", 2), ("diorite", 1)])


def elfe(w, robe="green_wool", haar="yellow_wool"):
    return [(kap((0, 0, 0), (0, 3.2, 0), 0.7, 0.4), w.b(robe)), (kap((0, 3.2, 0), (0, 4.0, 0), 0.4, 0.35), w.b(robe)),
            (ell(0, 4.6, 0, 0.42, 0.5, 0.42), w.b("white_terracotta")), (ell(0, 4.9, -0.15, 0.48, 0.4, 0.48),
                                                                          w.b(haar)),
            (kap((0, 4.4, 0.4), (0, 5.0, 0.75), 0.1), w.b("white_terracotta")),
            (kap((0, 4.4, -0.4), (0, 5.0, -0.75), 0.1), w.b("white_terracotta"))]


def spitzbogen(w, x0, x1, z, y0, H, mat, achse="x", dicke=1):
    """Spitzbogen zwischen x0 und x1 (bzw. z), Scheitel bei y0+H."""
    B = (x1 - x0) / 2
    cx = (x0 + x1) / 2
    for a in range(x0, x1 + 1):
        u = abs(a - cx) / max(0.5, B)
        y = y0 + round(H * 0.45 + H * 0.55 * max(0.0, 1 - u ** 1.6) ** 0.6)
        for d in range(dicke):
            for yy in range(y0, max(y, y0 + H) + 1 if a in (x0, x1) else y + 1):
                if a in (x0, x1) or yy == y:
                    p = (a, yy, z + d) if achse == "x" else (z + d, yy, a)
                    w.setze(*p, mat(*p) if callable(mat) else mat)


def schlanker_turm(w, cx, cz, y0, r, H, dach="mcw:light_blue_terracotta", fenster=True):
    st = stein(w)
    for y in range(y0, y0 + H):
        for x in range(cx - r - 1, cx + r + 2):
            for z in range(cz - r - 1, cz + r + 2):
                d = math.hypot(x - cx, z - cz)
                if r - 0.8 < d <= r + 0.4:
                    fen = fenster and (y - y0) % 5 == 3 and (x == cx or z == cz)
                    w.setze(x, y, z, w.b("light_green_stained_glass" if False else "lime_stained_glass") if fen
                            else st(x, y, z))
                elif d <= r - 0.8:
                    w.bloecke.pop((x, y, z), None)
    for x in range(cx - r - 2, cx + r + 3):
        for z in range(cz - r - 2, cz + r + 3):
            if math.hypot(x - cx, z - cz) <= r + 1.5:
                w.setze(x, y0 + H, z, w.b("smooth_quartz_slab", type="bottom", waterlogged=False)
                        if math.hypot(x - cx, z - cz) > r + 0.5 else w.b("birch_planks"))
    return kegeldach(w, cx, cz, y0 + H + 1, r + 0.5, Dachmat(w, [dach, "mcw:cyan_terracotta", "birch"]),
                     form="nadel", spitze="lightning_rod")


def elfenbaum(w, x, y, z, seed, H, r=1.2, laub=LAUB):
    rng = w.rng
    enden = baum_aeste(w, x, z, H, 4, H * 0.45, "birch", r, rng, steigung=0.5, start=0.5)
    for (ex, ey, ez) in enden:
        laubball(w, ex, ey + y, ez, 2 + H * 0.12, arten=laub)
    return enden


def lichter(w, zellen, R, n, frei=0.0):
    rng = w.rng
    for _ in range(n):
        a = rng.random() * 6.28
        r = R * (frei + rng.random() * (0.9 - frei))
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        if (x, z) in zellen:
            y = zellen[(x, z)] + 2 + int(rng.random() * 4)
            if w.frei(x, y, z):
                w.setze(x, y, z, w.b("pearlescent_froglight", axis="y") if rng.random() < 0.3 else
                        w.b("end_rod", facing="up"), False)


# ============================================================================ Bauten

def saengerhain(seed, g=2):
    """Sängerhain: ein natürliches Amphitheater aus moosbewachsenen Calcitstufen im Halbrund, darüber spannen alte
    Birken ihr Blätterdach; unten eine Bühne mit Blütenbogen und schwebenden Lichtern."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, huegel=0.1, blumen=0.05)
    rb = R * 0.25
    st = stein(w)
    for k in range(int(3 + 2 * s)):
        r = rb + 2 + k * 1.5
        n = int(math.pi * r * 1.5)
        for j in range(n + 1):
            a = math.pi + j / n * math.pi
            x, z = round(math.cos(a) * r), round(math.sin(a) * r * 0.9)
            for y in range(1, k + 2):
                w.setze(x, y, z, st(x, y, z) if y < k + 1 else w.b("moss_block") if (x + z) % 3 == 0 else
                        w.b("calcite"))
    for x in range(-int(rb), int(rb) + 1):
        for z in range(0, int(rb) + 1):
            if math.hypot(x, z) <= rb:
                w.setze(x, 1, z, w.b("birch_planks"))
    spitzbogen(w, -int(rb) + 1, int(rb) - 1, int(rb) - 1, 2, int(4 + 2 * s), w.b("birch_log", axis="y"))
    for x in range(-int(rb) + 1, int(rb)):
        y = hoehe(w, x, int(rb) - 1, 20)
        w.setze(x, y + 1, int(rb) - 1, w.b("flowering_azalea_leaves", persistent=True, distance=1,
                                            waterlogged=False), False)
    for k in range(int(3 + s)):
        a = math.pi * (1.1 + k * 0.8 / (2 + s))
        x, z = round(math.cos(a) * R * 0.8), round(math.sin(a) * R * 0.8)
        elfenbaum(w, x, 0, z, seed + k, 10 + 4 * s)
    lichter(w, zellen, R * 0.5, int(10 + 6 * s))
    figur(w, 0.3 * s + 0.22, elfe(w, "white_wool"), (-2, -1, -2), (2, 6, 2), pos=(0, 2, int(rb * 0.4)),
          winkel=-math.pi / 2)
    return w


def blattkuppelhaus(seed, g=1):
    """Blattkuppelhaus: ein rundes Elfenhaus, dessen Dach eine Kuppel aus übereinandergelegten, riesigen Blättern ist;
    weiße Wände mit runden Fenstern, eine geschwungene Tür und ein Kräutergarten."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, huegel=0.1, blumen=0.06)
    r = int(3 + 1.5 * s)
    st = stein(w)
    H = int(3 + s)
    for y in range(1, H + 1):
        for x in range(-r - 1, r + 2):
            for z in range(-r - 1, r + 2):
                d = math.hypot(x, z)
                if r - 0.8 < d <= r + 0.4:
                    fen = y == 2 and abs(math.sin(math.atan2(z, x) * 3)) < 0.2
                    w.setze(x, y, z, w.b("lime_stained_glass") if fen else st(x, y, z))
                elif d <= r - 0.8:
                    w.bloecke.pop((x, y, z), None)
                    w.setze(x, 0, z, w.b("birch_planks"))
    for k in range(8):
        a = k / 8 * 2 * math.pi
        pts = bez((math.cos(a) * (r + 1.5), H + 0.5, math.sin(a) * (r + 1.5)),
                  (math.cos(a) * r * 0.9, H + r * 1.2, math.sin(a) * r * 0.9), (0, H + r * 1.1, 0))
        for (x, y, z, t) in pts:
            b = a + math.pi / 2
            for q in range(-int((1 - t) * r * 0.7) - 1, int((1 - t) * r * 0.7) + 2):
                w.setze(round(x + math.cos(b) * q * 0.7), round(y), round(z + math.sin(b) * q * 0.7),
                        w.b("moss_block") if q == 0 else w.b(["azalea_leaves", "oak_leaves"][k % 2], persistent=True,
                                                               distance=1, waterlogged=False), False)
    for y in (1, 2):
        w.bloecke.pop((0, y, r), None)
    w.setze(0, 3, r + 1, w.b("lantern", hanging=True, waterlogged=False)) if False else None
    for x in range(-2, 3):
        for z in range(r + 3, r + 6):
            if (x, z) in zellen:
                w.setze(x, zellen[(x, z)] + 1, z, w.b(["allium", "lily_of_the_valley", "azure_bluet", "fern"]
                                                      [(x + z) % 4]))
    return w


def lichtbogenbruecke(seed, g=2):
    """Lichtbogenbrücke: eine kühn geschwungene, schmale Bogenbrücke aus weißem Stein überspannt eine Schlucht mit
    Bach; ihr Geländer ist ein Geflecht aus Birkenästen mit Blüten und Laternen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    H = int(6 * s + 5)
    sp = 3 + 1.5 * s
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            mz = math.sin(x / 5) * 1.5
            d = abs(z - mz)
            h = -2 if d < sp else int(min(H, (d - sp) * 2.5) + rn(x, 3, z) * 2)
            for y in range(-3, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h and h > -2 else w.b("stone"))
            if h == -2:
                w.setze(x, -1, z, w.b("water", level=0))
    L = int(sp) + 4
    st = stein(w)
    for z in range(-L, L + 1):
        t = z / L
        y = round(H + 1 + (1 - t * t) * (2 + s))
        for x in (-1, 0, 1):
            w.setze(x, y, z, st(x, y, z))
        w.setze(0, y - 1, z, st(0, y - 1, z))
        for x in (-2, 2):
            w.setze(x, y + 1, z, w.b("birch_fence"))
            if z % 3 == 0:
                w.setze(x, y + 2, z, w.b("flowering_azalea_leaves", persistent=True, distance=1, waterlogged=False))
        if z % 6 == 0:
            laterne(w, 2, y + 3, z, kette=0)
    return w


def silberschmiede(seed, g=1):
    """Silberschmiede: eine offene, säulengetragene Werkstatt mit geschwungenem Blätterdach, in der Elfen Silber und
    Mondstein verarbeiten – Esse mit blauer Seelenglut, Amboss, Gussformen und Klingen an der Wand."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    A, B = int(4 + 1.5 * s), int(3 + s)
    st = stein(w)
    for x in range(-A, A + 1):
        for z in range(-B, B + 1):
            w.setze(x, 0, z, w.b("polished_diorite") if (x + z) % 2 else w.b("calcite"))
            if abs(x) == A and abs(z) == B or (abs(x) == A and z == 0):
                for y in range(1, 5):
                    w.setze(x, y, z, w.b("birch_log", axis="y"))
    for x in range(-A - 1, A + 2):
        for z in range(-B - 1, B + 2):
            y = 5 + round(1.5 * math.cos(z / (B + 1) * math.pi / 2))
            w.setze(x, y, z, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False) if (x + z) % 3 else
                    w.b("flowering_azalea_leaves", persistent=True, distance=1, waterlogged=False))
    ex = -A + 2
    for dx in (-1, 0, 1):
        for dz in (-1, 0):
            w.setze(ex + dx, 1, -B + 1 + dz, st(ex + dx, 1, 0))
    w.setze(ex, 2, -B + 1, w.b("soul_campfire", lit=True, signal_fire=False, facing="south", waterlogged=False))
    for y in range(3, 8):
        w.setze(ex, y, -B, w.b("calcite"))
    w.setze(0, 1, 0, w.b("anvil", facing="east"))
    w.setze(2, 1, -1, w.b("smithing_table"))
    w.setze(2, 1, 1, w.b("grindstone", face="floor", facing="north"))
    for x in range(-A + 1, A, 2):
        w.setze(x, 2, B, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
        w.setze(x, 3, B, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    figur(w, 0.3 * s + 0.22, elfe(w, "light_gray_wool", "white_wool"), (-2, -1, -2), (2, 6, 2), pos=(1, 1, 1),
          winkel=math.pi)
    return w


def sternlauschturm(seed, g=2):
    """Sternlauschturm: ein extrem schlanker, weißer Turm mit spiralförmig aufsteigenden Balkonen, auf dessen
    Spitze ein offener Kuppelpavillon mit Kristall steht; Ranken klettern die Wände hinauf."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, huegel=0.1, blumen=0.05)
    H = int(14 * s + 10)
    r = int(2 + s * 0.5)
    top = schlanker_turm(w, 0, 0, 1, r, H, dach="mcw:light_blue_terracotta")
    for k in range(int(H / 4)):
        a = k * 1.3
        y = 3 + k * 4
        cx, cz = round(math.cos(a) * (r + 2)), round(math.sin(a) * (r + 2))
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                w.setze(cx + dx, y, cz + dz, w.b("smooth_quartz_slab", type="top", waterlogged=False), False)
        w.setze(cx, y + 1, cz, w.b("birch_fence"), False)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 2 and math.hypot(x, z) > r - 0.5 and math.hypot(x, z) < r + 0.6 and rng.random() < 0.1:
            nx, nz = (x + (1 if x > 0 else -1), z) if abs(x) >= abs(z) else (x, z + (1 if z > 0 else -1))
            if w.frei(nx, y, nz):
                w.setze(nx, y, nz, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False), False)
    _ = top
    birke(w, int(R * 0.5), 1, int(R * 0.3), seed, 7 + 3 * s)
    lichter(w, zellen, R, int(6 + 4 * s), 0.3)
    return w


def wurzelhalle(seed, g=2):
    """Wurzelhalle: unter einem uralten Baum, dessen gewaltige Wurzeln sich bogenförmig über den Boden spannen,
    liegt eine offene Halle mit Bänken, Laternen und einem Wurzeltisch – ein Versammlungsort der Elfen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, huegel=0.1, art="wald")
    H = 6 + 3 * s
    rng = w.rng
    for k in range(int(6 + 2 * s)):
        a = k / (6 + 2 * s) * 2 * math.pi
        e = (math.cos(a) * R * 0.7, 0, math.sin(a) * R * 0.7)
        m = (math.cos(a) * R * 0.35, H * 0.9, math.sin(a) * R * 0.35)
        rohr(w, bez((0, H, 0), m, e), 1.0 + 0.3 * s, 0.5, w.b("dark_oak_wood", axis="y"), rauh=0.2)
    rohr(w, bez((0, H, 0), (0.5, H * 2, 0), (1, H * 3, 0.5)), 2 + 0.8 * s, 1.2, w.b("dark_oak_wood", axis="y"))
    enden = baum_aeste(w, 1, 0.5, H * 3.2, 5, 5 + 3 * s, "dark_oak", 1.0 + 0.3 * s, rng, steigung=0.3)
    for (x, y, z) in enden:
        laubball(w, x, y + 1, z, 2.5 + s, arten=("dark_oak_leaves", "azalea_leaves", "flowering_azalea_leaves"))
    for x in range(-int(R * 0.4), int(R * 0.4) + 1):
        for z in range(-int(R * 0.4), int(R * 0.4) + 1):
            if math.hypot(x, z) < R * 0.4 and w.frei(x, 1, z):
                w.setze(x, 0, z, w.b("moss_block") if (x + z) % 3 else w.b("birch_planks"))
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.4
        x, z = round(math.cos(a) * 3), round(math.sin(a) * 3)
        if w.frei(x, 1, z):
            w.setze(x, 1, z, w.b("birch_stairs", facing="north", half="bottom", shape="straight", waterlogged=False))
    lichter(w, zellen, R * 0.45, int(6 + 4 * s))
    return w


def haengende_gaerten(seed, g=2):
    """Hängende Gärten: an einem weißen Stufenturm hängen auf jeder Ebene Pflanzschalen über, aus denen Ranken,
    Blüten und Moos in langen Vorhängen herabfallen; Wasser rinnt von Schale zu Schale."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.1, blumen=0.04)
    st = stein(w)
    n = int(3 + 1.5 * s)
    A0 = int(3 + 2 * s)
    y = 1
    rng = w.rng
    for k in range(n):
        A = A0 + (n - k)
        h = 4
        for x in range(-A, A + 1):
            for z in range(-A, A + 1):
                rr = max(abs(x), abs(z))
                if rr == A:
                    for yy in range(y, y + 2):
                        w.setze(x, yy, z, st(x, yy, z))
                    w.setze(x, y + 2, z, w.b("moss_block"))
                    if rng.random() < 0.5:
                        L = int(1 + rng.random() * (k + 2) * 1.5)
                        dx = (1 if x == A else -1 if x == -A else 0)
                        dz = (1 if z == A else -1 if z == -A else 0)
                        for d in range(L):
                            yy = y + 1 - d
                            if yy < 1:
                                break
                            w.setze(x + dx, yy, z + dz, w.b("azalea_leaves", persistent=True, distance=1,
                                                            waterlogged=False) if d % 3 else
                                    w.b("flowering_azalea_leaves", persistent=True, distance=1, waterlogged=False),
                                    False)
                elif rr < A - 1:
                    w.setze(x, y + h - 1, z, st(x, y, z))
                elif rr == A - 1:
                    w.setze(x, y + 2, z, w.b("grass_block", snowy=False))
                    if rng.random() < 0.4:
                        w.setze(x, y + 3, z, w.b(["allium", "azure_bluet", "lily_of_the_valley", "fern"]
                                                 [int(rng.integers(4))]))
            if k < n - 1:
                for yy in range(y, y + h):
                    w.setze(x, yy, -A + 2, st(x, yy, 0)) if abs(x) <= A - 2 and False else None
        for yy in range(y, y + h):
            for x in range(-A + 2, A - 1):
                for z in range(-A + 2, A - 1):
                    if max(abs(x), abs(z)) == A - 2:
                        w.setze(x, yy, z, st(x, yy, z) if (x + yy) % 4 else w.b("lime_stained_glass"))
        w.setze(0, y + 2, A, w.b("water", level=0))
        y += h
    kegeldach(w, 0, 0, y, A0, Dachmat(w, ["mcw:light_blue_terracotta", "birch"]), form="glocke")
    return w


def weidenlaubengang(seed, g=1):
    """Weidenlaubengang: ein langer, gewölbter Gang aus gebogenen Weidenruten, über den Laub und Blüten wachsen; am
    Ende eine kleine Rundbank um eine Quelle, Leuchtkäfer schweben im grünen Halbdunkel."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, huegel=0.1, blumen=0.05)
    L = int(R * 0.75)
    B = 2 + int(s * 0.5)
    H = 4 + int(s)
    for z in range(-L, L + 1):
        for x in range(-B + 1, B):
            w.setze(x, 0, z, w.b("moss_block") if (x + z) % 3 else w.b("calcite"))
            w.bloecke.pop((x, 1, z), None)
        for k in range(int(math.pi * B * 2) + 2):
            a = k / (math.pi * B * 2 + 2) * math.pi
            x, y = round(math.cos(a) * (B + 0.5)), round(math.sin(a) * H)
            if y < 1:
                y = 1
            if z % 2 == 0:
                w.setze(x, y, z, w.b("stripped_birch_log", axis="y"), False)
            else:
                w.setze(x, y, z, w.b("flowering_azalea_leaves" if (x + z) % 4 == 1 else "azalea_leaves",
                                     persistent=True, distance=1, waterlogged=False), False)
    for x in range(-2, 3):
        for z in range(L + 1, L + 5):
            d = math.hypot(x, z - L - 3)
            if d < 1.5:
                w.setze(x, 0, z, w.b("water", level=0))
            elif d < 2.6:
                w.setze(x, 1, z, w.b("birch_slab", type="bottom", waterlogged=False))
    for k in range(int(5 + 3 * s)):
        z = -L + k * int(2 * L / (5 + 3 * s))
        w.setze((k % 3) - 1, 2 + k % 2, z, w.b("end_rod", facing="up"), False)
    return w


def ratskreis(seed, g=2):
    """Ratskreis: auf einer Lichtung steht ein Kreis aus hohen, verzierten Steinsitzen mit Rückenlehnen in Blattform um
    einen Mondsteintisch, umgeben von einem Ring aus Birken; Banner hängen an den Lehnen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, huegel=0.1, blumen=0.04)
    st = stein(w)
    rk = R * 0.4
    n = int(7 + 2 * s)
    for k in range(n):
        a = k / n * 2 * math.pi
        x, z = round(math.cos(a) * rk), round(math.sin(a) * rk)
        rx, rz = round(math.cos(a) * (rk + 1)), round(math.sin(a) * (rk + 1))
        f = {0: "west", 1: "north"}
        face = "west" if abs(math.cos(a)) > abs(math.sin(a)) and math.cos(a) > 0 else \
            "east" if abs(math.cos(a)) > abs(math.sin(a)) else "north" if math.sin(a) > 0 else "south"
        w.setze(x, 1, z, w.b("quartz_stairs", facing={"west": "east", "east": "west", "north": "south",
                                                      "south": "north"}[face], half="bottom", shape="straight",
                             waterlogged=False))
        for y in range(1, int(4 + s)):
            w.setze(rx, y, rz, st(rx, y, rz))
        w.setze(rx, int(4 + s), rz, w.b("flowering_azalea_leaves", persistent=True, distance=1, waterlogged=False))
        w.setze(rx, int(3 + s), rz, w.b(["green_wool", "white_wool", "light_blue_wool"][k % 3]))
        _ = f
    for x in range(-2, 3):
        for z in range(-2, 3):
            if math.hypot(x, z) <= 2.2:
                w.setze(x, 1, z, w.b("calcite") if math.hypot(x, z) > 1 else w.b("pearlescent_froglight", axis="y"))
    baumrand(w, zellen, R, int(8 + 5 * s), seed, innen=0.75, H=(8, 12 + 3 * s), art="birke")
    return w


def bluetenbrunnen(seed, g=1):
    """Blütenbrunnen: ein Brunnen in Form einer sich öffnenden Blüte aus weißem Stein und Quarz, aus deren Mitte Wasser
    aufsteigt und über die Blütenblätter in ein Seerosenbecken rinnt."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1, blumen=0.04)
    rb = R * 0.5
    for x in range(-int(rb) - 1, int(rb) + 2):
        for z in range(-int(rb) - 1, int(rb) + 2):
            d = math.hypot(x, z)
            if d <= rb:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("calcite"))
                w.bloecke.pop((x, 1, z), None)
            elif d <= rb + 1:
                w.setze(x, 1, z, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
    for y in range(1, 3):
        w.setze(0, y, 0, w.b("calcite"))
    nb = 6
    rp = 2 + 1.2 * s
    for k in range(nb):
        a = k / nb * 2 * math.pi
        pts = bez((0, 3, 0), (math.cos(a) * rp * 0.7, 3.2, math.sin(a) * rp * 0.7),
                  (math.cos(a) * rp, 5 + s, math.sin(a) * rp))
        for (x, y, z, t) in pts:
            bw = math.sin(t * math.pi) * (0.8 + 0.4 * s)
            b = a + math.pi / 2
            for q in range(-int(bw) - 1, int(bw) + 2):
                if abs(q) <= bw:
                    w.setze(round(x + math.cos(b) * q), round(y), round(z + math.sin(b) * q),
                            w.b("smooth_quartz") if abs(q) < bw * 0.5 else w.b("pink_stained_glass"), False)
    w.setze(0, 3, 0, w.b("gold_block"))
    w.setze(0, 4, 0, w.b("water", level=0))
    rng = w.rng
    for k in range(int(4 + 2 * s)):
        a = rng.random() * 6.28
        r = rb * (0.5 + rng.random() * 0.4)
        w.setze(round(math.cos(a) * r), 1, round(math.sin(a) * r), w.b("lily_pad"))
    return w


def seidenweberei(seed, g=1):
    """Seidenweberei: ein langes, luftiges Elfenhaus mit offener Säulenfront, in dem Webstühle stehen; außen hängen
    Bahnen schimmernder Seide in Blau, Grün und Silber zum Trocknen zwischen Birkenstämmen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    A, B = int(4 + 2 * s), int(2 + s)
    st = stein(w)
    zh = -int(R * 0.3)
    for x in range(-A, A + 1):
        for z in range(zh - B, zh + B + 1):
            w.setze(x, 0, z, w.b("birch_planks"))
            if z == zh - B or abs(x) == A:
                for y in range(1, 5):
                    w.setze(x, y, z, st(x, y, z))
            elif z == zh + B and x % 3 == 0:
                for y in range(1, 5):
                    w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    from feinbau import satteldach
    satteldach(w, -A - 1, zh - B - 1, A + 1, zh + B + 1, 5, Dachmat(w, ["mcw:light_blue_terracotta", "birch"]),
               first_x=True)
    for k in range(int(2 + s)):
        w.setze(-A + 2 + k * 3, 1, zh, w.b("loom", facing="south"))
    farben = ["light_blue", "lime", "white", "cyan", "light_gray"]
    for k in range(int(3 + s)):
        x0 = -A + 1 + k * 4
        for sx in (x0, x0 + 3):
            for y in range(1, 6):
                w.setze(sx, y, int(R * 0.4), w.b("birch_log", axis="y"))
        for x in range(x0 + 1, x0 + 3):
            for y in range(2, 5):
                w.setze(x, y, int(R * 0.4), w.b(f"{farben[k % 5]}_stained_glass"))
    return w


def leuchtkaeferlichtung(seed, g=2):
    """Leuchtkäferlichtung: eine nächtliche Waldlichtung mit hohem Gras, Farnen und einem kleinen Teich, über der
    hunderte Leuchtkäfer schweben; zwischen den Bäumen hängen Lampions an Fäden."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, huegel=0.2, art="wald")
    rng = w.rng
    for (x, z), h in zellen.items():
        d = math.hypot(x, z)
        if d < R * 0.6 and rng.random() < 0.35 and w.frei(x, h + 1, z):
            if rng.random() < 0.3:
                w.setze(x, h + 1, z, w.b("tall_grass", half="lower"))
                w.setze(x, h + 2, z, w.b("tall_grass", half="upper"))
            else:
                w.setze(x, h + 1, z, w.b("fern") if rng.random() < 0.5 else w.b("grass"))
        if math.hypot(x - R * 0.2, z + R * 0.15) < R * 0.18:
            w.setze(x, h, z, w.b("water", level=0))
            w.bloecke.pop((x, h + 1, z), None)
            w.bloecke.pop((x, h + 2, z), None)
    baumrand(w, zellen, R, int(10 + 6 * s), seed, innen=0.72, H=(9, 13 + 3 * s), art="misch")
    for k in range(int(30 + 25 * s)):
        a = rng.random() * 6.28
        r = rng.random() * R * 0.65
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        y = zellen.get((x, z), 0) + 2 + int(rng.random() * (3 + 3 * s))
        if w.frei(x, y, z):
            w.setze(x, y, z, w.b("pearlescent_froglight", axis="y") if rng.random() < 0.2 else
                    w.b("ochre_froglight", axis="y") if rng.random() < 0.15 else w.b("end_rod", facing="up"), False)
    for k in range(int(4 + 2 * s)):
        a = k / (4 + 2 * s) * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.66), round(math.sin(a) * R * 0.66)
        y = zellen.get((x, z), 0) + 5
        for d in range(2):
            w.setze(x, y - d, z, w.b("chain", axis="y", waterlogged=False), False)
        w.setze(x, y - 2, z, w.b("lantern", hanging=True, waterlogged=False), False)
    return w


def hirschstall(seed, g=2):
    """Hirschstall: ein eleganter Stall mit geschwungenem Blätterdach und offenen Boxen, in dem weiße Reithirsche mit
    weit ausladenden Geweihen stehen, davor eine Koppel aus Birkenzaun und eine Tränke."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, huegel=0.1)
    A = int(5 + 2 * s)
    zs = -int(R * 0.4)
    st = stein(w)
    for x in range(-A, A + 1):
        for z in range(zs - 2, zs + 2):
            w.setze(x, 0, z, w.b("birch_planks"))
        for y in range(1, 4):
            w.setze(x, y, zs - 2, st(x, y, zs - 2))
        if (x + A) % 3 == 0:
            for z in range(zs - 2, zs + 2):
                for y in range(1, 3):
                    w.setze(x, y, z, w.b("birch_planks"))
            for y in range(1, 5):
                w.setze(x, y, zs + 2, w.b("birch_log", axis="y"))
        else:
            w.setze(x, 1, zs + 2, w.b("birch_fence_gate", facing="south", in_wall=False, open=False, powered=False))
    for x in range(-A - 1, A + 2):
        for k, z in enumerate(range(zs - 3, zs + 4)):
            y = 4 + round(1.6 * math.sin(k / 6 * math.pi))
            w.setze(x, y, z, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False) if (x + z) % 4 else
                    w.b("flowering_azalea_leaves", persistent=True, distance=1, waterlogged=False))
    from erw_bauernhof import tier, zaunzug
    hirsch = tier(w, "white_wool", kopf="white_wool", beine="white_terracotta", L=1.6, hals=1.0) + [
        (kap((2.4, 4.6, 0.25), (1.6, 6.6, 1.2), 0.15), w.b("gold_block")),
        (kap((2.4, 4.6, -0.25), (1.6, 6.6, -1.2), 0.15), w.b("gold_block")),
        (kap((1.9, 5.8, 0.8), (2.6, 6.8, 1.0), 0.12), w.b("gold_block")),
        (kap((1.9, 5.8, -0.8), (2.6, 6.8, -1.0), 0.12), w.b("gold_block"))]
    for k in range(int(2 + s)):
        figur(w, 0.32 * s + 0.25, hirsch, (-3, -1, -2), (4, 8, 2),
              pos=(-A + 3 + k * 4, 1, int(R * 0.15) + (k % 2) * 3), winkel=k * 0.8)
    zaunzug(w, [(-A, 2), (-A, int(R * 0.65)), (A, int(R * 0.65)), (A, 2)], holz="birch")
    w.setze(0, 1, int(R * 0.5), w.b("water_cauldron", level=3))
    return w


def harfenpavillon(seed, g=1):
    """Harfenpavillon: ein runder, offener Pavillon aus schlanken weißen Säulen mit einer Kuppel aus Laub, darin eine
    riesige goldene Harfe mit Saiten aus Licht; Elfen lauschen auf Bänken ringsum."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1, blumen=0.05)
    r = 3 + 1.5 * s
    H = int(5 + 2 * s)
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            if math.hypot(x, z) <= r + 0.5:
                w.setze(x, 1, z, w.b("smooth_quartz") if math.hypot(x, z) < r - 0.5 else w.b("calcite"))
    n = 8
    for k in range(n):
        a = k / n * 2 * math.pi
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        for y in range(2, H + 2):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            for y in range(0, int(r) + 1):
                d = math.sqrt(x * x + z * z + (y * 1.3) ** 2)
                if r - 0.7 < d <= r + 0.5:
                    w.setze(x, H + 2 + y, z, w.b("flowering_azalea_leaves" if (x + z + y) % 3 == 0 else
                                                 "azalea_leaves", persistent=True, distance=1, waterlogged=False))
    hh = int(3 + 1.5 * s)
    for y in range(2, 2 + hh + 1):
        w.setze(-1, y, 0, w.b("gold_block"))
    for k in range(int(hh * 1.2)):
        t = k / (hh * 1.2)
        w.setze(round(-1 + t * (1.5 + s)), round(2 + hh + 0.5 - t * hh * 0.4), 0, w.b("gold_block"), False)
    w.setze(round(0.5 + s), 2, 0, w.b("gold_block"))
    for x in range(0, round(1 + s)):
        for y in range(3, round(2 + hh - x * 0.4)):
            w.setze(x, y, 0, w.b("end_rod", facing="up"), False)
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.78
        x, z = round(math.cos(a) * (r + 2.5)), round(math.sin(a) * (r + 2.5))
        figur(w, 0.27 * s + 0.2, elfe(w, ["green_wool", "white_wool", "light_blue_wool", "lime_wool"][k]),
              (-2, -1, -2), (2, 6, 2), pos=(x, 1, z), winkel=a + math.pi)
    return w


def tor_der_jahreszeiten(seed, g=2):
    """Tor der Jahreszeiten: vier Bäume – Frühlingsblüte, Sommergrün, Herbstrot und Winterweiß – neigen sich über
    einem Steinweg zu einem gemeinsamen Torbogen zusammen; der Boden wechselt unter ihnen mit."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, huegel=0.1)
    zeiten = [("cherry_leaves", "pink_petals", "cherry_log"), ("oak_leaves", "grass", "oak_log"),
              ("mcw:orange", "red_tulip", "dark_oak_log"), ("snow_block", "snow", "birch_log")]
    import modbloecke as MB
    H = 7 + 3 * s
    for k, (laub, boden, holz) in enumerate(zeiten):
        sx = -1 if k % 2 == 0 else 1
        sz = -1 if k < 2 else 1
        x0, z0 = sx * (3 + s), sz * (2 + s)
        for (x, z), h in zellen.items():
            if (x * sx > 0) and (z * sz > 0) and math.hypot(x, z) < R * 0.8:
                if boden == "snow":
                    w.setze(x, h + 1, z, w.b("snow", layers=1))
                elif boden == "pink_petals" and (x + z) % 3 == 0:
                    w.setze(x, h + 1, z, w.b("pink_petals", facing="north", flower_amount=3))
                elif boden == "red_tulip" and (x + z) % 5 == 0:
                    w.setze(x, h + 1, z, w.b("red_tulip"))
        pts = bez((x0, 0, z0), (x0, H * 0.6, z0), (0, H, 0))
        rohr(w, pts, 0.9 + 0.3 * s, 0.5, w.b(holz.replace("_log", "_wood"), axis="y"))
        cx, cy, cz = x0 * 0.6, H * 0.85, z0 * 0.8
        if laub == "mcw:orange":
            arten = None
            blk = MB.herbstlaub(w, "orange_autumn")
            for dx in range(-3, 4):
                for dy in range(-2, 3):
                    for dz in range(-3, 4):
                        if dx * dx + (dy / 0.7) ** 2 + dz * dz <= (2.5 + s) ** 2:
                            w.setze(round(cx + dx), round(cy + dy), round(cz + dz), blk, False)
        elif laub == "snow_block":
            for dx in range(-3, 4):
                for dy in range(-2, 3):
                    for dz in range(-3, 4):
                        if dx * dx + (dy / 0.7) ** 2 + dz * dz <= (2.5 + s) ** 2:
                            w.setze(round(cx + dx), round(cy + dy), round(cz + dz),
                                    w.b("snow_block") if dy > 0 else w.b("birch_leaves", persistent=True, distance=1,
                                                                         waterlogged=False), False)
        else:
            laubball(w, cx, cy, cz, 2.5 + s, arten=(laub,))
    for z in range(-R, R + 1):
        for x in (-1, 0, 1):
            if (x, z) in zellen:
                w.setze(x, zellen[(x, z)], z, w.b("calcite") if (x + z) % 2 else w.b("polished_diorite"))
                w.bloecke.pop((x, zellen[(x, z)] + 1, z), None)
    return w


def beerenkelterei(seed, g=1):
    """Beerenkelterei: eine kleine Elfenkelterei mit runder Bottichpresse unter einem Blätterdach, Körben voller
    Beeren, Fässern mit Beerenwein, einer Laube aus Beerensträuchern und einem Verkostungstisch."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    zellen = wiese(w, R, huegel=0.1)
    r = 2 + s
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            d = math.hypot(x, z)
            if d <= r:
                w.setze(x, 1, z, w.b("birch_planks") if d > r - 1 else w.b("red_wool"))
                if d > r - 1:
                    w.setze(x, 2, z, w.b("stripped_birch_log", axis="y"))
    for y in range(3, 6):
        w.setze(0, y, 0, w.b("birch_log", axis="y"))
    for x in range(-int(r), int(r) + 1):
        w.setze(x, 5, 0, w.b("birch_log", axis="x"))
    for k in range(int(3 + s)):
        w.setze(int(r) + 3, 1, -2 + k, w.b("barrel", facing="east", open=False))
    for k in range(int(4 + 2 * s)):
        a = k / (4 + 2 * s) * 2 * math.pi
        x, z = round(math.cos(a) * (R * 0.7)), round(math.sin(a) * (R * 0.7))
        if (x, z) in zellen:
            w.setze(x, zellen[(x, z)] + 1, z, w.b("sweet_berry_bush", age=3))
    for x in range(-2, 3):
        w.setze(x, 1, -int(r) - 3, w.b("birch_slab", type="top", waterlogged=False))
    w.setze(0, 2, -int(r) - 3, w.b("decorated_pot", facing="north", waterlogged=False, cracked=False))
    for x in range(-int(r) - 2, int(r) + 3):
        for z in range(-int(r) - 2, int(r) + 3):
            if math.hypot(x, z) <= r + 2:
                w.setze(x, 7, z, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False), False)
    for sx in (-int(r) - 2, int(r) + 2):
        for y in range(1, 7):
            w.setze(sx, y, 0, w.b("birch_log", axis="y"))
    return w


def seerosenpavillon(seed, g=2):
    """Seerosenpavillon: ein filigraner Pavillon auf einer runden Plattform mitten in einem Seerosenteich, erreichbar
    über geschwungene Trittsteine; sein Dach gleicht einer umgedrehten Seerosenblüte."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, huegel=0.1)
    rng = w.rng
    rt = R * 0.7
    for (x, z), h in zellen.items():
        if math.hypot(x, z) < rt:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("water", level=0))
            w.setze(x, -2, z, w.b("clay"))
            w.bloecke.pop((x, 1, z), None)
            if rng.random() < 0.08:
                w.setze(x, 1, z, w.b("lily_pad"))
    rp = 2.5 + s
    for x in range(-int(rp) - 1, int(rp) + 2):
        for z in range(-int(rp) - 1, int(rp) + 2):
            if math.hypot(x, z) <= rp:
                w.setze(x, 1, z, w.b("smooth_quartz"))
                w.setze(x, 0, z, w.b("calcite"))
    for k in range(6):
        a = k / 6 * 2 * math.pi
        x, z = round(math.cos(a) * (rp - 0.5)), round(math.sin(a) * (rp - 0.5))
        for y in range(2, 6):
            w.setze(x, y, z, w.b("birch_fence"))
    for k in range(10):
        a = k / 10 * 2 * math.pi
        for t in range(int(rp + 2)):
            y = 6 + round(abs(t - rp * 0.5) * 0.4)
            w.setze(round(math.cos(a) * t), y, round(math.sin(a) * t),
                    w.b("pink_stained_glass") if t > rp * 0.5 else w.b("white_stained_glass"), False)
    w.setze(0, 7, 0, w.b("gold_block"))
    for k in range(int(rt - rp)):
        t = rp + 1 + k
        w.setze(round(math.sin(t * 0.4) * 2), 1, round(t), w.b("calcite"))
    return w


def uferturm(seed, g=2):
    """Uferturm: ein schlanker, weißer Turm mit Blätterdachhaube steht am Ufer eines Sees, mit einem Bootssteg, einem
    schwanenförmigen Boot und einer Laternenreihe am Wasser."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, huegel=0.1)
    for (x, z), h in zellen.items():
        if z > R * 0.1 + math.sin(x / 4):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("water", level=0))
            w.setze(x, -2, z, w.b("sand"))
            w.bloecke.pop((x, 1, z), None)
    schlanker_turm(w, -int(R * 0.2), -int(R * 0.25), 1, int(2 + s * 0.6), int(10 * s + 8),
                   dach="mcw:green_terracotta")
    for z in range(int(R * 0.05), int(R * 0.7)):
        for x in (int(R * 0.2), int(R * 0.2) + 1):
            w.setze(x, 1, z, w.b("birch_planks"))
        if z % 3 == 0:
            laterne(w, int(R * 0.2) + 2, 3, z, kette=0)
            w.setze(int(R * 0.2) + 2, 2, z, w.b("birch_fence"))
    bx, bz = int(R * 0.2) - 3, int(R * 0.45)
    for dz in range(-2, 3):
        for dx in (-1, 0, 1):
            w.setze(bx + dx, 0, bz + dz, w.b("white_wool"))
    for y in range(1, 4):
        w.setze(bx, y, bz - 2 - (1 if y == 3 else 0), w.b("white_wool"))
    w.setze(bx, 3, bz - 4, w.b("orange_wool"))
    return w


def waechterallee(seed, g=2):
    """Wächterallee: ein langer Prozessionsweg, flankiert von hohen Statuen elfischer Wächter mit Speeren und
    Umhängen auf Sockeln, zwischen ihnen Birken und Laternen, am Ende ein Spitzbogentor."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, huegel=0.1)
    L = int(R * 0.85)
    for z in range(-L, L + 1):
        for x in range(-2, 3):
            if (x, z) in zellen:
                w.setze(x, zellen[(x, z)], z, w.b("calcite") if (x + z) % 2 else w.b("polished_diorite"))
                w.bloecke.pop((x, zellen[(x, z)] + 1, z), None)
    st = stein(w)
    for k, z in enumerate(range(-L + 2, L - 3, int(5 + 2 * s))):
        for sx in (-1, 1):
            x = sx * 4
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    w.setze(x + dx, 1, z + dz, st(x, 1, z))
            figur(w, 0.55 * s + 0.4, elfe(w, "light_gray_concrete", "white_concrete") +
                  [(kap((0, 0, 0.9), (0, 7.0, 0.9), 0.15), w.b("smooth_quartz")),
                   (kap((0, 7.0, 0.9), (0, 7.8, 0.9), 0.18, 0.02), w.b("gold_block"))],
                  (-2, -1, -2), (2, 9, 2), pos=(x, 2, z), winkel=-math.pi / 2 * sx)
            if k % 2:
                laterne(w, sx * 6, 3, z, kette=0)
                w.setze(sx * 6, 1, z, w.b("birch_fence"))
                w.setze(sx * 6, 2, z, w.b("birch_fence"))
    spitzbogen(w, -3, 3, -L - 1, 1, int(6 + 3 * s), st, dicke=2)
    return w


def elfenaquaedukt(seed, g=2):
    """Elfenaquädukt: eine Reihe schlanker, weißer Spitzbögen trägt eine offene Wasserrinne über ein Tal; an den Pfeilern
    rankt Efeu, am Ende stürzt das Wasser in ein Becken mit Seerosen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, huegel=0.4)
    st = stein(w)
    L = int(R * 0.85)
    H = int(6 + 3 * s)
    sp = int(3 + s)
    for x in range(-L, L + 1):
        w.setze(x, H, -1, st(x, H, -1))
        w.setze(x, H, 1, st(x, H, 1))
        w.setze(x, H - 1, 0, st(x, H - 1, 0))
        w.setze(x, H, 0, w.b("water", level=0))
    for x0 in range(-L, L - sp + 1, sp):
        spitzbogen(w, x0, x0 + sp, -1, 0, H - 1, st, dicke=3)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if 1 <= y < H and abs(z) <= 1 and rng.random() < 0.05:
            nz = z + (2 if z >= 0 else -2)
            if w.frei(x, y, nz):
                w.setze(x, y, nz, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False), False)
    for x in range(L + 1, L + 5):
        for z in range(-2, 3):
            if math.hypot(x, z) < R:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("calcite"))
                w.bloecke.pop((x, 1, z), None)
    return w


ELFEN3 = {
    "saengerhain": ("Sängerhain", saengerhain),
    "blattkuppelhaus": ("Blattkuppelhaus", blattkuppelhaus),
    "lichtbogenbruecke": ("Lichtbogenbrücke", lichtbogenbruecke),
    "silberschmiede": ("Silberschmiede", silberschmiede),
    "sternlauschturm": ("Sternlauschturm", sternlauschturm),
    "wurzelhalle": ("Wurzelhalle", wurzelhalle),
    "haengende_gaerten": ("Hängende Gärten", haengende_gaerten),
    "weidenlaubengang": ("Weidenlaubengang", weidenlaubengang),
    "ratskreis": ("Ratskreis", ratskreis),
    "bluetenbrunnen": ("Blütenbrunnen", bluetenbrunnen),
    "seidenweberei": ("Seidenweberei", seidenweberei),
    "leuchtkaeferlichtung": ("Leuchtkäferlichtung", leuchtkaeferlichtung),
    "hirschstall": ("Hirschstall", hirschstall),
    "harfenpavillon": ("Harfenpavillon", harfenpavillon),
    "tor_der_jahreszeiten": ("Tor der Jahreszeiten", tor_der_jahreszeiten),
    "beerenkelterei": ("Beerenkelterei", beerenkelterei),
    "seerosenpavillon": ("Seerosenpavillon", seerosenpavillon),
    "uferturm": ("Uferturm", uferturm),
    "waechterallee": ("Wächterallee", waechterallee),
    "elfenaquaedukt": ("Elfenaquädukt", elfenaquaedukt),
}

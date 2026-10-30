"""Deko & Wege II – zwanzig weitere Gestaltungsstücke: Steinbogenbrücke über den Bach, Rosenbogen mit Bank,
Gartenpavillon, Hofeinfahrt mit Briefkasten, Schubkarre im Kürbisbeet, Ziehbrunnen, Wäscheleine, Steingarten,
Seerosenteich mit Steg, Kräuterspirale, Bienenstöcke am Wiesenrand, Hochbeete, Gartenschuppen, Blumentreppe,
Bachkaskaden, Sonnenuhr-Platz, Kompostecke, Hängematte zwischen Bäumen, Leiterwagen und Insektenhotel."""

from __future__ import annotations

import math

from deko import bank, laternenpfahl, zf
from erw_basis import BLUMEN, M, S, baum, birke, figur, haus, hoehe, wiese
from feinbau import Dachmat, kegeldach, laterne, satteldach
from flora import _neu
from leuchtwald2 import kugel, laubball
from lib import Rauschen

KRAEUTER = ["fern", "grass", "allium", "azure_bluet", "oxeye_daisy", "cornflower", "lily_of_the_valley"]


def boden(w, s, R=None, **kw):
    R = R or int(6 * s + 5)
    return R, wiese(w, R, **{"huegel": 0.15, **kw})


def wasser(w, x, z, tief=2):
    for y in range(1 - tief, 1):
        w.setze(x, y, z, w.b("water", level=0))
    w.setze(x, -tief, z, w.b("gravel") if (x + z) % 3 else w.b("sand"))
    w.bloecke.pop((x, 1, z), None)


def hoch(w, x, z, y, name, **pr):
    w.setze(x, y, z, w.b(name, half="lower", **pr))
    w.setze(x, y + 1, z, w.b(name, half="upper", **pr))


def topf(w, x, y, z, pflanze=None):
    w.setze(x, y, z, w.b(f"potted_{pflanze}") if pflanze else w.b("flower_pot"))


# ============================================================================ Stücke

def bogenbruecke(seed, g=1):
    """Steinbogenbrücke über den Bach: ein kleiner Bach mit Kieselufer, Schilf und Seerosen, überspannt von einer
    buckligen Steinbrücke mit Brüstung und Laternen an beiden Enden."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(7 * s + 5))
    bw = 1.5 + s * 0.6
    rn = Rauschen(w, 3)
    rng = w.rng
    for x in range(-R - 2, R + 3):
        mz = math.sin(x / 4) * 1.2
        for z in range(-R - 2, R + 3):
            if (x, z) not in zellen:
                continue
            d = abs(z - mz)
            if d < bw:
                wasser(w, x, z, 2)
                if rng.random() < 0.06:
                    w.setze(x, 1, z, w.b("lily_pad"))
            elif d < bw + 1.2:
                w.setze(x, 0, z, w.b("gravel") if rn(x, 1, z) < 0.5 else w.b("mossy_cobblestone"))
                w.bloecke.pop((x, 1, z), None)
                if rng.random() < 0.15:
                    for y in range(1, 3):
                        w.setze(x, y, z, w.b("sugar_cane", age=0))
    st = M(w, [("stone_bricks", 3), ("mossy_stone_bricks", 1), ("cobblestone", 1)])
    L = int(bw) + 3
    Hb = int(1 + s)
    for z in range(-L, L + 1):
        t = abs(z) / L
        y = round(Hb * (1 - t * t)) + 1
        for x in (-1, 0, 1):
            w.setze(x, y, z, w.b("stone_brick_slab", type="bottom", waterlogged=False) if t > 0.85 else
                    st(x, y, z))
            for yy in range(-1, y):
                if abs(z) > bw - 0.5 or yy < -1:
                    w.setze(x, yy, z, st(x, yy, z))
        for x in (-2, 2):
            w.setze(x, y, z, st(x, y, z))
            w.setze(x, y + 1, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none",
                                     west="none", waterlogged=False))
    for sz in (-L - 1, L + 1):
        laternenpfahl(w, 2, sz, h=2, haengend=False)
    return w


def rosenbogen(seed, g=1):
    """Rosenbogen mit Bank: ein mit Laub und Rosen überwucherter Holzbogen über einem Kiesweg, darunter eine Bank,
    seitlich Rosenbüsche, Pfingstrosen und Flieder."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(5 * s + 5))
    n = 1 + int(s)
    for z in range(-R, R + 1):
        for x in (-1, 0, 1):
            if (x, z) in zellen:
                w.setze(x, zellen[(x, z)], z, w.b("gravel"))
                w.bloecke.pop((x, zellen[(x, z)] + 1, z), None)
    for k in range(n):
        z = -(n - 1) * 2 + k * 4
        for sx in (-2, 2):
            for y in range(1, 5):
                w.setze(sx, y, z, w.b("oak_fence"))
        for x in range(-2, 3):
            w.setze(x, 5, z, w.b("oak_planks") if abs(x) == 2 else w.b("oak_slab", type="bottom", waterlogged=False))
        for (x, y) in ((-2, 6), (-1, 6), (0, 6), (1, 6), (2, 6), (-3, 5), (3, 5), (-3, 4), (3, 4), (-3, 2), (3, 3)):
            w.setze(x, y, z, w.b("flowering_azalea_leaves", persistent=True, distance=1, waterlogged=False), False)
        for sx in (-3, 3):
            hoch(w, sx, z + 1, 1, "rose_bush")
    bank(w, 3, 0, richtung="west") if False else None
    for dz in (-1, 0, 1):
        w.setze(-3, 1, dz + (n - 1) * 2 + 3, w.b("oak_stairs", facing="east", half="bottom", shape="straight",
                                                 waterlogged=False))
    rng = w.rng
    for k in range(int(6 * s + 4)):
        x = int((rng.random() - 0.5) * R * 1.4)
        z = int((rng.random() - 0.5) * R * 1.4)
        if abs(x) > 3 and (x, z) in zellen:
            hoch(w, x, z, zellen[(x, z)] + 1, ["rose_bush", "peony", "lilac"][k % 3])
    return w


def gartenpavillon(seed, g=1):
    """Gartenpavillon: ein achteckiger, erhöhter Holzpavillon mit geschwungenem Dach, Geländer, Tisch und Stühlen,
    umgeben von Blumenrabatten und einem Plattenweg."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(6 * s + 6), blumen=0.02)
    r = 2.5 + s
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            d = max(abs(x), abs(z), (abs(x) + abs(z)) / 1.42)
            if d <= r:
                w.setze(x, 1, z, w.b("spruce_planks"))
                w.setze(x, 0, z, w.b("stone_bricks"))
                if d > r - 1:
                    w.setze(x, 2, z, zf(w, "spruce"))
    for k in range(8):
        a = k / 8 * 2 * math.pi
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        for y in range(2, 6):
            w.setze(x, y, z, w.b("stripped_spruce_log", axis="y"))
    for z in (round(r),):
        w.bloecke.pop((0, 2, z), None)
        w.setze(0, 1, z + 1, w.b("spruce_stairs", facing="north", half="bottom", shape="straight",
                                 waterlogged=False))
    kegeldach(w, 0, 0, 6, r, Dachmat(w, ["mcw:green_terracotta", "mcw:light_blue_terracotta", "deepslate_tile"]),
              eckig=True, form="glocke", spitze="lantern")
    w.setze(0, 2, 0, w.b("spruce_fence"))
    w.setze(0, 3, 0, w.b("spruce_pressure_plate", powered=False))
    for dx, dz, f in ((1, 0, "west"), (-1, 0, "east"), (0, -1, "south")):
        w.setze(dx, 2, dz, w.b("spruce_stairs", facing=f, half="bottom", shape="straight", waterlogged=False))
    for z in range(int(r) + 2, R):
        for x in (-1, 0, 1):
            if (x, z) in zellen:
                w.setze(x, zellen[(x, z)], z, w.b("smooth_stone") if (z % 2) else w.b("polished_andesite"))
    rng = w.rng
    for k in range(int(2 * math.pi * (r + 2))):
        a = k / (2 * math.pi * (r + 2)) * 2 * math.pi
        x, z = round(math.cos(a) * (r + 2)), round(math.sin(a) * (r + 2))
        if abs(x) <= 1 and z > 0:
            continue
        w.setze(x, 1, z, w.b(BLUMEN[int(rng.integers(len(BLUMEN)))]))
    return w


def hofeinfahrt(seed, g=1):
    """Hofeinfahrt mit Briefkasten: zwei gemauerte Torpfeiler mit Laternen und offenem Holztor, eine Kieseinfahrt,
    Hecken links und rechts, ein Briefkasten auf einem Pfosten und ein Namensschild."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(6 * s + 5), blumen=0.03)
    B = int(1 + s)
    for z in range(-R, R + 1):
        for x in range(-B, B + 1):
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("gravel") if (x * 3 + z) % 4 else w.b("coarse_dirt"))
                w.bloecke.pop((x, 1, z), None)
    st = M(w, [("bricks", 2), ("stone_bricks", 1)])
    for sx in (-B - 1, B + 1):
        for y in range(1, 4):
            w.setze(sx, y, 0, st(sx, y, 0))
        w.setze(sx, 4, 0, w.b("stone_brick_slab", type="bottom", waterlogged=False))
        w.setze(sx, 5, 0, w.b("lantern", hanging=False, waterlogged=False)) if False else \
            w.setze(sx, 4, 0, w.b("lantern", hanging=False, waterlogged=False))
        for x in range(sx + (1 if sx > 0 else -1), (R + 2) * (1 if sx > 0 else -1), 1 if sx > 0 else -1):
            if (x, 0) in zellen:
                for y in range(1, 3):
                    w.setze(x, y, 0, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
    for k, x in enumerate(range(-B, B + 1)):
        w.setze(x, 1, -1 - (abs(x) // 1 if False else 0), w.b("oak_fence_gate", facing="west" if x < 0 else "east",
                                                             in_wall=False, open=True, powered=False)) \
            if abs(x) == B else None
    mx = B + 2
    w.setze(mx, 1, 1, w.b("spruce_fence"))
    w.setze(mx, 2, 1, w.b("barrel", facing="south", open=False))
    w.setze(mx, 3, 1, w.b("red_wool")) if False else None
    w.setze(mx, 2, 2, w.b("oak_wall_sign", facing="south", waterlogged=False)) if False else None
    w.setze(-B - 1, 2, 1, w.b("oak_wall_sign", facing="south", waterlogged=False))
    rng = w.rng
    for k in range(int(4 * s + 2)):
        x = int((rng.random() - 0.5) * R * 1.6)
        z = -int(rng.random() * R * 0.8) - 2
        if abs(x) > B + 1 and (x, z) in zellen:
            w.setze(x, zellen[(x, z)] + 1, z, w.b(BLUMEN[k % len(BLUMEN)]))
    return w


def schubkarre(seed, g=0):
    """Schubkarre im Kürbisbeet: eine hölzerne Schubkarre voller Kürbisse und Melonen steht in einem Beet mit
    Kürbisranken, daneben eine Gießkanne, Heuballen und ein Rechen am Zaun."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(5 * s + 5), blumen=0.02)
    rng = w.rng
    A = int(R * 0.7)
    for x in range(-A, A + 1):
        for z in range(-A, 0):
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("farmland", moisture=7) if (x + z) % 3 else w.b("coarse_dirt"))
                w.bloecke.pop((x, 1, z), None)
                r = rng.random()
                if r < 0.15:
                    w.setze(x, 1, z, w.b("pumpkin"))
                elif r < 0.22:
                    w.setze(x, 1, z, w.b("melon"))
                elif r < 0.5 and (x + z) % 3:
                    w.setze(x, 1, z, w.b("pumpkin_stem", age=7))
    for x in range(-A - 1, A + 2):
        w.setze(x, 1, -A - 1, zf(w, "spruce", east=True, west=True))
    w.setze(1, 2, -A - 1, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    cx, cz = 0, 2
    for x in (-1, 0, 1):
        for z in (cz, cz + 1):
            w.setze(x, 1, z, w.b("spruce_slab", type="top", waterlogged=False))
            w.setze(x, 2, z, w.b("pumpkin") if (x + z) % 2 else w.b("melon"))
    w.setze(2, 1, cz, w.b("dark_oak_log", axis="x"))
    for z in (cz + 2, cz + 3):
        for x in (-1, 1):
            w.setze(x, 1, z, w.b("spruce_fence"))
    w.setze(-2, 1, cz + 3, w.b("cauldron"))
    for k in range(2):
        w.setze(3 + k, 1, cz + 2, w.b("hay_block", axis="x"))
    w.setze(3, 2, cz + 2, w.b("hay_block", axis="x"))
    return w


def ziehbrunnen(seed, g=1):
    """Ziehbrunnen: ein runder Feldsteinbrunnen mit Wasser, zwei Holzpfosten, kleinem Schindeldach, Kurbelwelle mit
    Kette und Eimer, ringsum ein Pflasterkranz, Blumen und ein Trog."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(5 * s + 5))
    r = 1.5 + s * 0.6
    st = M(w, [("cobblestone", 3), ("mossy_cobblestone", 2), ("stone", 1)])
    for x in range(-int(r) - 3, int(r) + 4):
        for z in range(-int(r) - 3, int(r) + 4):
            d = math.hypot(x, z)
            if d <= r - 0.5:
                for y in range(-4, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.bloecke.pop((x, 1, z), None)
            elif d <= r + 0.6:
                for y in range(-4, 3):
                    w.setze(x, y, z, st(x, y, z))
            elif d <= r + 2.5:
                w.setze(x, 0, z, w.b("cobblestone") if (x + z) % 2 else w.b("gravel"))
                w.bloecke.pop((x, 1, z), None)
    rr = int(r) + 1
    for sx in (-rr, rr):
        for y in range(3, 6):
            w.setze(sx, y, 0, w.b("spruce_log", axis="y"))
    for x in range(-rr, rr + 1):
        w.setze(x, 5, 0, w.b("spruce_log", axis="x"))
    satteldach(w, -rr - 1, -1, rr + 1, 1, 6, Dachmat(w, ["spruce", "dark_oak"]), first_x=True, ue=0)
    for y in range(2, 5):
        w.setze(0, y, 0, w.b("chain", axis="y", waterlogged=False))
    w.setze(0, 1, 0, w.b("cauldron"))
    w.setze(rr + 1, 4, 0, w.b("lever", face="wall", facing="east", powered=False))
    for x in range(int(r) + 3, int(r) + 6):
        w.setze(x, 1, 2, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    w.setze(int(r) + 4, 1, 2, w.b("water_cauldron", level=3))
    return w


def waescheleine(seed, g=0):
    """Wäscheleine: zwischen zwei T-Pfosten hängt eine Leine mit bunter Wäsche, darunter ein Wäschekorb, ein
    Holzschemel und eine Blumenwiese."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(5 * s + 5), blumen=0.04)
    L = int(3 * s + 4)
    for sx in (-L, L):
        for y in range(1, 5):
            w.setze(sx, y, 0, w.b("spruce_fence"))
        for dz in (-1, 0, 1):
            w.setze(sx, 5, dz, w.b("spruce_slab", type="bottom", waterlogged=False))
    farben = ["white", "light_blue", "pink", "yellow", "white", "lime", "red"]
    for line in (-1, 1):
        for x in range(-L + 1, L):
            w.setze(x, 4, line, w.b("tripwire", attached=True, disarmed=False, powered=False, east=True, west=True,
                                    north=False, south=False))
        for k, x in enumerate(range(-L + 2, L - 1, 2)):
            f = farben[(k + (line > 0) * 3) % len(farben)]
            w.setze(x, 3, line, w.b(f"{f}_wool"))
            if k % 2 == 0:
                w.setze(x, 2, line, w.b(f"{f}_wool"))
                w.setze(x + 1, 3, line, w.b(f"{f}_wool"))
    w.setze(2, 1, 2, w.b("barrel", facing="up", open=True))
    w.setze(-2, 1, 2, w.b("spruce_slab", type="bottom", waterlogged=False))
    return w


def steingarten(seed, g=1):
    """Steingarten: moosbedeckte Findlinge in geharktem Kies, Polster aus Moos und Farn, Zwergkiefern, eine
    Steinlaterne und ein kleines Wasserbecken mit Bambusrohr."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(6 * s + 5), art="kies", blumen=0.0)
    rng = w.rng
    for (x, z), h in zellen.items():
        w.setze(x, h, z, w.b("gravel") if (x + 2 * z) % 3 else w.b("light_gray_concrete_powder"))
        w.bloecke.pop((x, h + 1, z), None)
    f = M(w, [("stone", 2), ("andesite", 2), ("mossy_cobblestone", 1), ("tuff", 1)])
    for k in range(int(3 + 3 * s)):
        a = rng.random() * 6.28
        d = R * (0.2 + rng.random() * 0.6)
        x, z = math.cos(a) * d, math.sin(a) * d
        r = 0.9 + rng.random() * (0.8 + 0.6 * s)
        kugel(w, x, 0.5, z, r, f, ry=r * 0.8)
        top = hoehe(w, round(x), round(z), 8)
        w.setze(round(x), top + 1, round(z), w.b("moss_carpet"), False)
    for k in range(int(4 + 3 * s)):
        a = rng.random() * 6.28
        d = R * (0.2 + rng.random() * 0.7)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if w.frei(x, 1, z):
            w.setze(x, 0, z, w.b("moss_block"))
            w.setze(x, 1, z, w.b("fern") if k % 2 else w.b("azalea"))
    for k in range(int(1 + s)):
        x, z = -int(R * 0.5) + k * 3, int(R * 0.4)
        for y in range(1, 3):
            w.setze(x, y, z, w.b("spruce_log", axis="y"))
        laubball(w, x, 3.5, z, 1.6, arten=("spruce_leaves",))
    lx, lz = int(R * 0.4), -int(R * 0.3)
    w.setze(lx, 1, lz, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                           waterlogged=False))
    w.setze(lx, 2, lz, w.b("lantern", hanging=False, waterlogged=False))
    w.setze(lx, 3, lz, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    for dx in (-1, 0):
        for dz in (0, 1):
            w.setze(dx, 0, dz, w.b("water", level=0))
            w.bloecke.pop((dx, 1, dz), None)
    w.setze(1, 1, 0, w.b("bamboo", age=0, leaves="none", stage=0))
    w.setze(1, 2, 0, w.b("bamboo", age=0, leaves="none", stage=0))
    return w


def seerosenteich(seed, g=1):
    """Seerosenteich mit Steg: ein natürlicher Teich mit Seerosen, Schilf, Rohrkolben-Optik aus Zuckerrohr, Großem
    Tropfblatt, Ufersteinen und einem kleinen Holzsteg mit Laterne."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(7 * s + 5), blumen=0.02)
    rn = Rauschen(w, 3)
    rng = w.rng
    rt = R * 0.6
    for (x, z), h in zellen.items():
        d = math.hypot(x, z * 1.2) + rn(x, 0, z) * 2.5
        if d < rt:
            wasser(w, x, z, 2 if d < rt * 0.6 else 1)
            if rng.random() < 0.1:
                w.setze(x, 1, z, w.b("lily_pad"))
        elif d < rt + 1.3:
            w.setze(x, 0, z, w.b("mud") if rng.random() < 0.4 else w.b("mossy_cobblestone"))
            w.bloecke.pop((x, 1, z), None)
            r = rng.random()
            if r < 0.2:
                for y in range(1, 3 + int(rng.random() * 2)):
                    w.setze(x, y, z, w.b("sugar_cane", age=0))
            elif r < 0.28:
                w.setze(x, 1, z, w.b("big_dripleaf", facing="north", tilt="none", waterlogged=False))
    for z in range(int(rt) + 1, int(rt * 0.2), -1):
        for x in (0, 1):
            w.setze(x, 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
        if z % 2 == 0:
            w.setze(-1, 0, z, w.b("spruce_log", axis="y"))
            w.setze(2, 0, z, w.b("spruce_log", axis="y"))
    w.setze(2, 1, int(rt * 0.2) + 1, w.b("spruce_fence"))
    w.setze(2, 2, int(rt * 0.2) + 1, w.b("lantern", hanging=False, waterlogged=False))
    return w


def kraeuterspirale(seed, g=0):
    """Kräuterspirale: eine spiralförmig ansteigende Trockensteinmauer, gefüllt mit Erde und bepflanzt mit Kräutern,
    Farnen und Blüten, am Fuß ein kleines Wasserbecken mit Seerose."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(5 * s + 5), blumen=0.02)
    Rs = 2.5 + 1.2 * s
    H = int(2 + 1.5 * s)
    rng = w.rng
    st = M(w, [("cobblestone", 2), ("mossy_cobblestone", 2), ("stone", 1)])
    for x in range(-int(Rs) - 1, int(Rs) + 2):
        for z in range(-int(Rs) - 1, int(Rs) + 2):
            d = math.hypot(x, z)
            if d > Rs:
                continue
            a = (math.atan2(z, x) + math.pi) / (2 * math.pi)
            t = (Rs - d) / Rs
            h = 1 + int((t * 0.6 + a * 0.4) * H)
            wand = abs(((d + a * 1.6) % 1.6) - 0.8) < 0.35
            for y in range(1, h + 1):
                w.setze(x, y, z, st(x, y, z) if wand or y < h else w.b("grass_block", snowy=False))
            if not wand:
                w.setze(x, h + 1, z, w.b(KRAEUTER[int(rng.integers(len(KRAEUTER)))]))
    for x in range(int(Rs), int(Rs) + 3):
        for z in (-1, 0, 1):
            wasser(w, x, z, 1)
    w.setze(int(Rs) + 1, 1, 0, w.b("lily_pad"))
    return w


def bienenstoecke(seed, g=1):
    """Bienenstöcke am Wiesenrand: eine Reihe Bienenkästen auf Holzböcken vor einer üppigen Blumenwiese mit Flieder,
    Sonnenblumen und Lavendelfarben, dazu ein Imkerhäuschen und Honigtöpfe."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(6 * s + 5), blumen=0.3)
    rng = w.rng
    n = int(3 + 2 * s)
    zb = -int(R * 0.3)
    for k in range(n):
        x = -n + 1 + k * 2
        w.setze(x, 1, zb, w.b("spruce_fence"))
        w.setze(x, 2, zb, w.b("beehive", facing="south", honey_level=int(rng.integers(6))))
        w.setze(x, 3, zb, w.b("spruce_slab", type="bottom", waterlogged=False))
    for k in range(int(5 * s + 3)):
        x = int((rng.random() - 0.5) * R * 1.4)
        z = int(rng.random() * R * 0.7)
        if (x, z) in zellen:
            hoch(w, x, z, zellen[(x, z)] + 1, ["sunflower", "lilac", "peony"][k % 3])
    haus(w, int(R * 0.45), -int(R * 0.55), 4, 3, 1, M(w, [("spruce_planks", 2), ("stripped_spruce_log", 1)]),
         holz="spruce", H=3, dach=("spruce", "dark_oak"), tuer_s="south", schorn=False)
    for k in range(3):
        w.setze(-n - 1, 1, zb + 2 + k, w.b("honey_block") if k % 2 else w.b("decorated_pot", facing="north",
                                                                              waterlogged=False, cracked=False))
    return w


def hochbeete(seed, g=1):
    """Hochbeete: mehrere hüfthohe Holzkästen mit Möhren, Kartoffeln, Roter Bete und Weizen, Kieswege dazwischen,
    eine Regentonne, Werkzeug am Zaun und eine kleine Bank."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(6 * s + 5), blumen=0.02)
    nx, nz = 1 + int(s), 2
    pfl = ["carrots", "potatoes", "beetroots", "wheat"]
    for i in range(nx):
        for j in range(nz):
            x0 = -nx * 3 + 1 + i * 6
            z0 = -4 + j * 5
            for x in range(x0, x0 + 5):
                for z in range(z0, z0 + 3):
                    rand = x in (x0, x0 + 4) or z in (z0, z0 + 2)
                    w.setze(x, 1, z, w.b("spruce_planks") if rand else w.b("dirt"))
                    if rand:
                        w.setze(x, 2, z, w.b("spruce_slab", type="bottom", waterlogged=False))
                    else:
                        w.setze(x, 2, z, w.b("farmland", moisture=7))
                        p = pfl[(i * 2 + j) % 4]
                        w.setze(x, 3, z, w.b(p, age=7 if p != "beetroots" else 3))
            for x in range(x0 - 1, x0 + 6):
                w.setze(x, 0, z0 + 3, w.b("gravel"))
    w.setze(nx * 3 + 1, 1, -4, w.b("water_cauldron", level=3))
    w.setze(nx * 3 + 1, 1, -3, w.b("barrel", facing="up", open=False))
    bank(w, 0, 7, richtung="north")
    return w


def gartenschuppen(seed, g=1):
    """Gartenschuppen: ein kleiner Holzschuppen mit Pultdach, Blumenkästen unter dem Fenster, Werkzeugwand, Regen-
    tonne, Brennholzstapel und einer Schubkarre davor."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(5 * s + 5), blumen=0.03)
    B, T = int(3 + 2 * s) | 1, int(3 + s)
    haus(w, 0, -1, B, T, 1, M(w, [("spruce_planks", 3), ("stripped_spruce_log", 1)]), holz="spruce", H=3,
         dach=("spruce", "dark_oak"), tuer_s="south", schorn=False)
    zf_ = -1 + T // 2 + 1
    for x in range(-B // 2 + 1, B // 2):
        if x % 2:
            topf(w, x, 3, zf_ + 0, ["red_tulip", "dandelion", "poppy", "blue_orchid"][(x + 4) % 4])
    for k in range(3):
        w.setze(-B // 2 - 1, 1 + k // 2, k % 2, w.b("oak_log", axis="z"))
    w.setze(B // 2 + 1, 1, 0, w.b("water_cauldron", level=3))
    w.setze(B // 2 + 1, 1, -1, w.b("composter", level=5))
    for x in (2, 3):
        w.setze(x, 1, zf_ + 3, w.b("spruce_slab", type="top", waterlogged=False))
    w.setze(4, 1, zf_ + 3, w.b("dark_oak_log", axis="x"))
    w.setze(2, 2, zf_ + 3, w.b("dirt"))
    return w


def blumentreppe(seed, g=1):
    """Blumentreppe: eine breite Steintreppe einen Hang hinauf, deren Wangen mit Blumenkästen und Töpfen voller
    Blüten besetzt sind, oben eine Laterne und eine Bank mit Aussicht."""
    w = _neu(seed)
    s = S[g]
    R = int(6 * s + 5)
    rn = Rauschen(w, 4)
    H = int(3 + 3 * s)
    rng = w.rng
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            h = int(max(0, min(H, (-z + R * 0.4) / (R * 0.9) * H)))
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else w.b("dirt"))
            if rng.random() < 0.05:
                w.setze(x, h + 1, z, w.b(BLUMEN[int(rng.integers(len(BLUMEN)))]))
    st = M(w, [("stone_bricks", 2), ("mossy_stone_bricks", 1)])
    for k in range(H + 1):
        z = int(R * 0.4) - 1 - int(k * R * 0.9 / H)
        for dz in range(int(R * 0.9 / H) + 1):
            for x in range(-2, 3):
                for y in range(0, k + 1):
                    w.setze(x, y, z - dz, st(x, y, z))
                for y in range(k + 1, k + 4):
                    w.bloecke.pop((x, y, z - dz), None)
                w.setze(x, k + 1, z - dz + 0, w.b("stone_brick_stairs", facing="north", half="bottom",
                                                  shape="straight", waterlogged=False)) if dz == 0 else None
            for sx in (-3, 3):
                for y in range(0, k + 2):
                    w.setze(sx, y, z - dz, st(sx, y, z))
                if dz == 0:
                    topf(w, sx, k + 2, z, ["red_tulip", "orange_tulip", "pink_tulip", "allium", "cornflower"][k % 5])
    zt = int(R * 0.4) - 1 - int(H * R * 0.9 / H) - 2
    laterne(w, 3, H + 4, zt, kette=0)
    w.setze(3, H + 2, zt, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                              waterlogged=False))
    w.setze(3, H + 3, zt, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                              waterlogged=False))
    return w


def kaskaden(seed, g=1):
    """Bachkaskaden: ein Bach stürzt über mehrere moosige Steinstufen in kleine Becken, gesäumt von Farnen, Moos,
    Azaleen und Trittsteinen."""
    w = _neu(seed)
    s = S[g]
    R = int(6 * s + 5)
    rn = Rauschen(w, 4)
    n = int(3 + s)
    rng = w.rng
    st = M(w, [("mossy_cobblestone", 2), ("stone", 2), ("mossy_stone_bricks", 1)])
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            stufe = min(n - 1, max(0, int((-z + R) / (2 * R / n))))
            h = stufe * 2
            bach = abs(x - math.sin(z / 3)) < 1.6 + s * 0.4
            for y in range(-1, h + 1):
                w.setze(x, y, z, st(x, y, z) if (bach or abs(x) < 4) else w.b("dirt"))
            if bach:
                w.setze(x, h, z, w.b("water", level=0))
            else:
                w.setze(x, h, z, w.b("moss_block") if abs(x) < 4 else w.b("grass_block", snowy=False))
                if rng.random() < 0.12:
                    w.setze(x, h + 1, z, w.b(["fern", "azalea", "grass", "moss_carpet"][int(rng.integers(4))]))
    return w


def sonnenuhr(seed, g=1):
    """Sonnenuhr-Platz: ein runder Plattenplatz mit Stundensteinen im Kreis, in der Mitte eine Säule mit Schatten-
    zeiger, ringsum Bänke und Blumenbeete."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(6 * s + 5), blumen=0.02)
    rp = R * 0.6
    for (x, z), h in zellen.items():
        d = math.hypot(x, z)
        if d <= rp:
            w.setze(x, h, z, w.b("smooth_stone") if int(d) % 2 else w.b("polished_andesite"))
            w.bloecke.pop((x, h + 1, z), None)
        elif d <= rp + 1.5 and (x + z) % 2:
            w.setze(x, h + 1, z, w.b(BLUMEN[(x * 3 + z) % len(BLUMEN)]))
    for k in range(12):
        a = k / 12 * 2 * math.pi
        x, z = round(math.cos(a) * (rp - 1)), round(math.sin(a) * (rp - 1))
        w.setze(x, 1, z, w.b("chiseled_stone_bricks") if k % 3 == 0 else w.b("stone_brick_slab", type="bottom",
                                                                                waterlogged=False))
    for y in range(1, 3):
        w.setze(0, y, 0, w.b("quartz_pillar", axis="y"))
    w.setze(0, 3, 0, w.b("chiseled_quartz_block"))
    for k in range(int(2 + s)):
        w.setze(0, 4 + k, -k, w.b("lightning_rod", facing="up", powered=False, waterlogged=False), False)
    for k in range(4):
        a = k / 4 * 2 * math.pi + math.pi / 4
        x, z = round(math.cos(a) * (rp + 2)), round(math.sin(a) * (rp + 2))
        bank(w, x, z, richtung=["north", "west", "south", "east"][k] if False else "south") if abs(z) > abs(x) \
            else None
    return w


def kompostecke(seed, g=0):
    """Kompostecke: drei hölzerne Kompostboxen mit Erde, Laub und Grasschnitt in verschiedenen Stadien, Komposter,
    eine Mistgabel, ein Laubhaufen und Brennnesseln am Rand."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(5 * s + 4), blumen=0.02)
    fueller = [("podzol", "dirt"), ("rooted_dirt", "coarse_dirt"), ("oak_leaves", "moss_block")]
    for k in range(3):
        x0 = -4 + k * 3
        for x in range(x0, x0 + 3):
            for z in range(-1, 2):
                rand = x in (x0, x0 + 2) or z == -1
                for y in range(1, 3):
                    if rand:
                        w.setze(x, y, z, w.b("spruce_planks") if y == 1 else zf(w, "spruce"))
                    elif y <= 1 + (k % 2):
                        f = fueller[k][y % 2]
                        w.setze(x, y, z, w.b(f, persistent=True, distance=1, waterlogged=False) if "leaves" in f
                                else w.b(f))
    w.setze(5, 1, 0, w.b("composter", level=7))
    w.setze(5, 1, 1, w.b("composter", level=3))
    laubball(w, -6, 1, 3, 1.5, arten=("oak_leaves", "birch_leaves", "dark_oak_leaves"))
    w.setze(2, 1, 3, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return w


def haengematte(seed, g=1):
    """Hängematte zwischen Bäumen: zwischen zwei schattigen Laubbäumen schwingt eine gestreifte Hängematte, darunter
    ein Beistelltisch mit Laterne, ein Buch und weiches Moos."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(6 * s + 5), blumen=0.04)
    L = int(3 + 1.5 * s)
    baum(w, -L - 1, 1, 0, seed, 7 + 2 * s)
    birke(w, L + 1, 1, 0, seed + 3, 7 + 2 * s)
    for sx in (-L - 1, L + 1):
        for y in range(1, 5):
            w.setze(sx, y, 0, w.b("oak_log" if sx < 0 else "birch_log", axis="y"))
    for x in range(-L, L + 1):
        t = (x + L) / (2 * L)
        y = round(4 - math.sin(t * math.pi) * 2)
        for dz in (0,):
            w.setze(x, y, dz, w.b(["white_wool", "red_wool", "white_wool", "blue_wool"][abs(x) % 4]))
        w.setze(x, y, 1, w.b("white_carpet")) if False else None
    w.setze(1, 1, 2, w.b("spruce_fence"))
    w.setze(1, 2, 2, w.b("spruce_pressure_plate", powered=False))
    w.setze(0, 1, 2, w.b("lantern", hanging=False, waterlogged=False))
    for x in range(-2, 3):
        w.setze(x, 1, -2, w.b("moss_carpet"))
    return w


def leiterwagen(seed, g=1):
    """Leiterwagen: ein hölzerner Bauernwagen mit Leitergittern, Speichenrädern und Deichsel, hoch beladen mit Heu,
    daneben Heuballen, eine Heugabel und eine Kiste mit Äpfeln."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(6 * s + 5), blumen=0.02)
    L = int(3 + s)
    for x in range(-L, L + 1):
        for z in (-1, 0, 1):
            w.setze(x, 2, z, w.b("spruce_planks"))
            w.setze(x, 3, z, w.b("hay_block", axis="x"))
            if abs(x) < L - 1 and z == 0:
                w.setze(x, 4, z, w.b("hay_block", axis="x"))
        for z in (-2, 2):
            w.setze(x, 3, z, w.b("spruce_fence") if x % 2 else w.b("spruce_log", axis="y"))
    for sx in (-L + 1, L - 1):
        for sz in (-2, 2):
            for dy, dx in ((0, 0), (1, 0), (2, 0), (1, -1), (1, 1)):
                w.setze(sx + dx, dy, sz, w.b("dark_oak_log", axis="z") if (dx, dy) == (0, 1) else
                        w.b("spruce_planks"))
    for k in range(3):
        w.setze(L + 1 + k, 1, 0, w.b("spruce_fence"))
    for k in range(3):
        w.setze(-L - 2, 1, -1 + k, w.b("hay_block", axis="y"))
    w.setze(-L - 2, 2, 0, w.b("hay_block", axis="y"))
    w.setze(2, 1, 3, w.b("barrel", facing="up", open=True))
    w.setze(0, 1, 3, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return w


def insektenhotel(seed, g=0):
    """Insektenhotel: ein hausförmiges Holzgestell mit Satteldach, dessen Fächer mit Bambus, Stammscheiben,
    Ziegeln, Heu und Bienennestern gefüllt sind, auf einem Pfosten zwischen Wildblumen."""
    w = _neu(seed)
    s = S[g]
    R, zellen = boden(w, s, int(5 * s + 4), blumen=0.3)
    B = int(2 + s) | 1
    Hh = int(3 + s)
    fueller = ["bamboo_block", "oak_log", "bricks", "hay_block", "bee_nest", "birch_log", "mud_bricks"]
    for x in range(-B // 2 - 1, B // 2 + 2):
        for y in range(2, 2 + Hh + 1):
            rand = abs(x) == B // 2 + 1 or y in (2, 2 + Hh)
            f = fueller[(x * 3 + y * 5) % len(fueller)]
            pr = {"axis": "z"} if f.endswith(("_log", "_block")) and f not in ("bricks",) and f != "mud_bricks" else {}
            if f == "bee_nest":
                pr = {"facing": "south", "honey_level": 0}
            if f == "hay_block":
                pr = {"axis": "z"}
            w.setze(x, y, 0, w.b("spruce_planks") if rand else w.b(f, **pr))
    satteldach(w, -B // 2 - 1, -1, B // 2 + 1, 1, 3 + Hh, Dachmat(w, ["spruce", "dark_oak"]), first_x=False, ue=1)
    w.setze(0, 1, 0, w.b("spruce_fence"))
    return w


DEKO3 = {
    "bogenbruecke": ("Steinbogenbrücke", bogenbruecke),
    "rosenbogen": ("Rosenbogen mit Bank", rosenbogen),
    "gartenpavillon": ("Gartenpavillon", gartenpavillon),
    "hofeinfahrt": ("Hofeinfahrt", hofeinfahrt),
    "schubkarre": ("Kürbisbeet mit Karre", schubkarre),
    "ziehbrunnen": ("Ziehbrunnen", ziehbrunnen),
    "waescheleine": ("Wäscheleine", waescheleine),
    "steingarten": ("Steingarten", steingarten),
    "seerosenteich": ("Seerosenteich mit Steg", seerosenteich),
    "kraeuterspirale": ("Kräuterspirale", kraeuterspirale),
    "bienenstoecke": ("Bienenstöcke", bienenstoecke),
    "hochbeete": ("Hochbeete", hochbeete),
    "gartenschuppen": ("Gartenschuppen", gartenschuppen),
    "blumentreppe": ("Blumentreppe", blumentreppe),
    "kaskaden": ("Bachkaskaden", kaskaden),
    "sonnenuhr": ("Sonnenuhr-Platz", sonnenuhr),
    "kompostecke": ("Kompostecke", kompostecke),
    "haengematte": ("Hängematte", haengematte),
    "leiterwagen": ("Leiterwagen", leiterwagen),
    "insektenhotel": ("Insektenhotel", insektenhotel),
}

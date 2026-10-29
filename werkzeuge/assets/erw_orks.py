"""Orklager II – zwanzig weitere Bauten der Orkstämme: Rammbock, Ballista, Gefangenenkäfige, Bannerhügel,
Grogbrauerei, Wildschweinpferch, Felsenfestung, Spähfels, Orkhafen, Erzmine, Kochgrube, Schamanenaltar,
Übungsplatz, Riesenkessel, Sumpfhütten, Schädelberg, Beutelager, Stachelbarrikade, Ork-Kriegsschiff und
Versammlungsplatz."""

from __future__ import annotations

import math

from feinbau import Mix, kram, platte, treppe
from lib import einfuegen
from orklager import Pal, _boden, _r, _schaedel, _stil, _welt, kriegszelt, orkhuette, totempfahl
from skulptur import kreisrand, scheibe

U = [0.6, 1.0, 1.7, 2.8]


def basis(seed, g, r_f=10):
    w = _welt(seed)
    p = Pal(w, seed)
    u = U[g]
    R = _r(r_f * u + 5, 6)
    _boden(w, p, R)
    for x, z in scheibe(R, 0, 0):
        w.setze(x, -1, z, w.b("dirt"), False)
    return w, p, u, R


def spitzpfahl(w, p, x, z, h, y0=1):
    for y in range(y0, y0 + h):
        w.setze(x, y, z, p.h(x, y, z))
    w.setze(x, y0 + h, z, p.zaun())


def banner(w, p, x, y, z, H=5, lang=3):
    for yy in range(y, y + H):
        w.setze(x, yy, z, p.h(x, yy, z, 0.2))
    for k in range(lang):
        for dy in range(2):
            w.setze(x + 1 + k, y + H - 1 - dy - k // 2, z, w.b(p.banner[(k + dy) % 2]))
    _schaedel(w, x, y + H, z, 0.6)


def rad(w, cx, cy, cz, R, achse="z"):
    for a in range(-R - 1, R + 2):
        for b in range(-R - 1, R + 2):
            d = math.hypot(a, b)
            if R - 0.7 <= d <= R + 0.4 or (d < R - 0.6 and (a == 0 or b == 0)):
                p = (cx + a, cy + b, cz) if achse == "z" else (cx, cy + b, cz + a)
                w.setze(*p, w.b("dark_oak_log", axis="y") if d > R - 0.7 else w.b("dark_oak_planks"))


# ============================================================================ Bauten

def rammbock(seed, g=1):
    """Rammbock: ein schwerer Baumstamm mit eiserner Widderspitze hängt an Ketten unter einem fellbespannten
    Schutzdach auf vier großen Holzrädern."""
    w, p, u, R = basis(seed, g)
    L, B = _r(10 * u + 4, 6), _r(2.4 * u + 1.5, 2)
    Rr = _r(1.4 * u + 0.6, 1)
    for sx in (-1, 1):
        for sz in (-B - 1, B + 1):
            rad(w, sx * (L // 2 - 1), Rr + 1, sz, Rr)
    yb = 2 * Rr + 2
    for x in range(-L // 2, L // 2 + 1):
        for z in range(-B, B + 1):
            w.setze(x, yb, z, p.h(x, yb, z) if abs(z) == B else w.b("dark_oak_planks"))
    for x in range(-L // 2, L // 2 + 1):
        for k in range(B + 1):
            for sz in (-1, 1):
                w.setze(x, yb + 1 + k, sz * (B - k), w.b(p.fell[(x + k) % len(p.fell)]))
    yr = yb - 1 if yb > 3 else yb
    for x in range(-L // 2 - 2, L // 2 + 1):
        w.setze(x, yr + _r(1.5 * u, 1), 0, w.b("dark_oak_log", axis="x"))
    for k in range(3):
        w.setze(L // 2 + 1 + k, yr + _r(1.5 * u, 1), 0, w.b("polished_blackstone" if k < 2 else "iron_block"))
    for x in (-L // 4, L // 4):
        for y in range(yr + _r(1.5 * u, 1) + 1, yb + B):
            w.setze(x, y, 0, w.b("chain", axis="y", waterlogged=False))
    return w


def ballista(seed, g=1):
    """Ballista: eine riesige Pfeilschleuder auf einem drehbaren Holzgestell mit gespannten Bogenarmen, Seilen
    und einem eisenbeschlagenen Speer, daneben ein Stapel Riesenpfeile."""
    w, p, u, R = basis(seed, g)
    L = _r(8 * u + 4, 5)
    y = _r(2 * u + 2, 3)
    for x in range(-2, 3):
        for z in range(-2, 3):
            for yy in range(1, y):
                if abs(x) == 2 and abs(z) == 2:
                    w.setze(x, yy, z, p.h(x, yy, z))
            w.setze(x, y, z, w.b("dark_oak_planks"))
    for x in range(-L // 2, L // 2 + 1):
        w.setze(x, y + 1, 0, w.b("dark_oak_log", axis="x"))
    S = _r(4 * u + 2, 3)
    for k in range(S + 1):
        bz = k
        bx = L // 2 - 1 - round((k / S) ** 2 * 2)
        for sz in (-1, 1):
            w.setze(bx, y + 1, sz * bz, w.b("dark_oak_log", axis="z"))
    for k in range(S + 1):
        t = k / S
        for sz in (-1, 1):
            w.setze(round(L // 2 - 3 - t * (L // 2 - 2)), y + 2, sz * round(S * (1 - t)), w.b("white_wool"), False)
    for x in range(-L // 2 + 1, L // 2 + 3):
        w.setze(x, y + 2, 0, w.b("spruce_fence", north=False, south=False, east=True, west=True, waterlogged=False))
    w.setze(L // 2 + 3, y + 2, 0, w.b("iron_block"))
    for k in range(3):
        for x in range(-L // 2, L // 2 - 2):
            w.setze(x, 1 + k // 2, R // 2 + k, w.b("spruce_fence", north=False, south=False, east=True, west=True,
                                                   waterlogged=False))
    return w


def kaefige(seed, g=1):
    """Gefangenenkäfige: an einem Galgengerüst aus dicken Stämmen hängen runde Eisenkäfige an Ketten über einer
    Grube, Fackeln und Knochen am Boden."""
    w, p, u, R = basis(seed, g)
    H = _r(9 * u + 5, 7)
    L = _r(10 * u + 4, 6)
    for x in (-L // 2, L // 2):
        for y in range(1, H + 1):
            w.setze(x, y, 0, p.h(x, y, 0))
    for x in range(-L // 2, L // 2 + 1):
        w.setze(x, H + 1, 0, p.h(x, H + 1, 0, 0.3))
    n = 2 + g
    for k in range(n):
        x = -L // 2 + 2 + k * max(2, (L - 3) // n)
        lk = 2 + (k % 3)
        for y in range(H - lk + 1, H + 1):
            w.setze(x, y, 0, w.b("chain", axis="y", waterlogged=False))
        yk = H - lk
        for y in range(yk - 3, yk + 1):
            for (dx, dz) in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                w.setze(x + dx, y, dz, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                           waterlogged=False) if y > yk - 3 else w.b("polished_blackstone"))
        w.setze(x, yk, 0, w.b("polished_blackstone"))
    for x in range(-L // 2 + 1, L // 2):
        for z in range(-2, 3):
            w.setze(x, 0, z, w.b("mud"))
    for k in range(3):
        w.setze(-L // 2 + 2 + k * 3, 1, 3, p.knochen("x"))
    return w


def bannerhuegel(seed, g=1):
    """Bannerhügel: ein Erdhügel, auf dem die Kriegsbanner aller Stämme an hohen Stangen wehen, rund um einen
    großen Schädelstein, Feuerschalen an den Hängen."""
    w, p, u, R = basis(seed, g)
    for x, z in scheibe(R, 0, 0):
        h = int(4 * u * (1 - (math.hypot(x, z) / R) ** 2)) + 1
        for y in range(1, h + 1):
            w.setze(x, y, z, p.boden(w.rng.random() * 3.5, x, y, z))
    ytop = int(4 * u) + 1
    farben = [("red_wool", "black_wool"), ("black_wool", "white_wool"), ("brown_wool", "red_wool"),
              ("gray_wool", "yellow_wool"), ("green_wool", "black_wool")]
    n = 4 + g * 2
    for k in range(n):
        a = k / n * 6.283
        x, z = round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)
        y = int(4 * u * (1 - 0.45 ** 2)) + 2
        H = _r(7 * u + 4, 5)
        for yy in range(y, y + H):
            w.setze(x, yy, z, p.h(x, yy, z, 0.2))
        f = farben[k % 5]
        for kk in range(3):
            for dy in range(3):
                w.setze(x + 1 + kk, y + H - 1 - dy, z, w.b(f[(kk + dy) % 2]))
    for y in range(ytop + 1, ytop + 4):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                w.setze(dx, y, dz, p.stein(1.5, dx, y, dz))
    _schaedel(w, 0, ytop + 4, 0, max(1.0, u))
    return w


def grogbrauerei(seed, g=1):
    """Grogbrauerei: offene Hütte mit großen Holzbottichen voller brodelndem Gebräu, Rohre aus Baumstämmen,
    ein Feuer unter dem Sudkessel und Fässer bis unters Dach."""
    w, p, u, R = basis(seed, g)
    B, T = _r(5 * u + 3, 4), _r(4 * u + 2, 3)
    for (x, z) in ((-B, -T), (B, -T), (-B, T), (B, T)):
        for y in range(1, 6):
            w.setze(x, y, z, p.h(x, y, z))
    for x in range(-B - 1, B + 2):
        for z in range(-T - 1, T + 2):
            w.setze(x, 6 + (T + 1 - abs(z)) // 2, z, w.b(p.fell[(x + z) % len(p.fell)]))
    for k, (cx, cz) in enumerate(((-B // 2, -T // 2), (B // 2, -T // 2), (0, T // 2))):
        r = _r(1.5 * u + 0.5, 1)
        for y in range(1, 4):
            for x, z in kreisrand(r + 0.5, cx, cz):
                w.setze(x, y, z, w.b("spruce_planks" if y != 2 else "stripped_spruce_log", **({} if y != 2 else
                                                                                           {"axis": "y"})))
        for x, z in scheibe(r - 0.5, cx, cz):
            w.setze(x, 3, z, w.b("water", level=0) if k else w.b("lava", level=0) if False else w.b("water", level=0))
        if k == 0:
            w.setze(cx, 0, cz, p.feuerblock(True))
    kram(w, B - 1, 1, T - 1, 6)
    return w


def wildschweinpferch(seed, g=1):
    """Wildschweinpferch: ein Gehege aus Spitzpfählen mit Schlammkuhle, Futtertrögen und einem Unterstand, darin
    die Statue eines riesigen Kampfkeilers mit Hauern."""
    from skulptur import Skulptur, ell, kap
    w, p, u, R = basis(seed, g)
    r = R - 2
    for x, z in kreisrand(r, 0, 0):
        if not (z > r - 1.5 and abs(x) <= 1):
            spitzpfahl(w, p, x, z, 3)
    for x, z in scheibe(r * 0.5, -2, -2):
        w.setze(x, 0, z, w.b("mud"))
    for k in range(3):
        w.setze(r - 3, 1, -2 + k, w.b("composter", level=6))
    S = Skulptur(w, u)
    S.mat("f", w.b("brown_terracotta"))
    S.mat("k", w.b("bone_block", axis="y"))
    S.plus(ell(0, 3, 0, 2.2, 2.0, 3.4), "f")
    S.plus(ell(0, 3.3, 3.2, 1.4, 1.4, 1.6), "f")
    for sx in (-1, 1):
        for sz in (-1, 1):
            S.plus(kap((sx * 1.2, 2, sz * 2), (sx * 1.2, 0.2, sz * 2.2), 0.5), "f")
        S.plus(kap((sx * 0.7, 2.8, 4.4), (sx * 1.2, 4.2, 4.6), 0.25, 0.1), "k")
    S.rendern((-4, 0, -5), (4, 6, 6), versatz=(2.5, 1, 2.5))
    return w


def felsenfestung(seed, g=2):
    """Felsenfestung: in einen schwarzen Felsen gehauene Festung mit gezackten Zinnen, schmalen Schießscharten,
    einem Tor zwischen Stoßzahn-Säulen und Bannern über dem Eingang."""
    w, p, u, R = basis(seed, g, 12)
    rng = w.rng
    H = _r(10 * u + 5, 7)
    for x, z in scheibe(R * 0.75, 0, -2):
        d = math.hypot(x, z + 2) / (R * 0.75)
        h = int(H * (1 - d ** 3)) + 1
        for y in range(1, h + 1):
            w.setze(x, y, z, p.stein(rng.random() * 3.5, x, y, z))
        if d > 0.8 and (x + z) % 2 == 0:
            w.setze(x, h + 1, z, p.stein(1.5, x, h + 1, z))
    zt = int(R * 0.75) - 2
    for y in range(1, _r(4 * u + 2, 3)):
        for x in range(-1, 2):
            for z in range(zt - 3, zt + 2):
                w.bloecke.pop((x, y, z), None)
    for sx in (-2, 2):
        for k in range(_r(5 * u + 2, 3)):
            w.setze(sx + (1 if sx > 0 else -1) * (k // 3), 1 + k, zt + 1, p.knochen())
    for y in range(3, H - 1, 3):
        for x in range(-int(R * 0.5), int(R * 0.5), 3):
            p_ = (x, y, max(z for z in range(-R, R) if (x, y, z) in w.bloecke) if any(
                (x, y, z) in w.bloecke for z in range(-R, R)) else zt)
            w.setze(*p_, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
    banner(w, p, -1, _r(4 * u + 2, 3) + 1, zt + 1, 3)
    return w


def spaehfels(seed, g=1):
    """Spähfels: eine schmale Felsnadel mit einer hölzernen Plattform obendrauf, Leitern und Seilwinden führen
    hinauf, ein Horn und ein Signalfeuer warnen das Lager."""
    w, p, u, R = basis(seed, g, 6)
    rng = w.rng
    H = _r(14 * u + 6, 9)
    for y in range(1, H + 1):
        r = 2.5 * u + 1.5 - y / H * 1.2 * u
        for x, z in scheibe(max(1.2, r), 0, 0):
            w.setze(x, y, z, p.stein(rng.random() * 3.5, x, y, z))
    P = _r(2.5 * u + 2, 3)
    for x in range(-P, P + 1):
        for z in range(-P, P + 1):
            w.setze(x, H + 1, z, w.b("dark_oak_planks"))
            if abs(x) == P or abs(z) == P:
                w.setze(x, H + 2, z, p.zaun())
    w.setze(P - 1, H + 2, P - 1, p.feuerblock(True))
    for y in range(1, H + 1):
        w.setze(0, y, int(2.5 * u + 2), w.b("ladder", facing="south", waterlogged=False), False)
    return w


def orkhafen(seed, g=2):
    """Orkhafen: ein grober Steg aus Baumstämmen ragt ins Wasser, daran ein schwarzes Ork-Langboot mit
    Knochenbug, am Ufer Fellzelte und Fischreusen."""
    from boote import langschiff
    w, p, u, R = basis(seed, g, 12)
    for x, z in scheibe(R, 0, 0):
        if z > R * 0.2:
            for y in range(-2, 1):
                w.setze(x, y, z, w.b("water", level=0))
    for z in range(int(R * 0.2), int(R * 0.9)):
        for x in range(-1, 2):
            w.setze(x, 1, z, w.b("dark_oak_log", axis="z"))
        if z % 3 == 0:
            for sx in (-2, 2):
                for y in range(-2, 3):
                    w.setze(sx, y, z, p.h(sx, y, z))
    einfuegen(w, langschiff(seed, max(0, g - 1)), int(R * 0.45), 0, int(R * 0.6))
    kriegszelt(w, p, -int(R * 0.4), -int(R * 0.3), u * 0.8)
    return w


def erzmine(seed, g=1):
    """Erzmine: ein Stolleneingang mit Holzstützen in einem Erzhügel, Schienen führen heraus zu Loren voller Erz,
    eine Schmelzgrube glüht, Spitzhacken und Haufen von Abraum."""
    w, p, u, R = basis(seed, g)
    rng = w.rng
    for x, z in scheibe(R * 0.8, 0, -int(R * 0.3)):
        d = math.hypot(x, z + R * 0.3) / (R * 0.8)
        h = int((7 * u + 3) * (1 - d ** 2)) + 1
        for y in range(1, h + 1):
            r = rng.random()
            w.setze(x, y, z, w.b("iron_ore" if r < 0.05 else "coal_ore" if r < 0.1 else "gold_ore" if r < 0.12 else
                                 "stone" if r < 0.7 else "andesite"))
    for z in range(-int(R * 0.6), int(R * 0.3)):
        for y in range(1, 4):
            for x in range(-1, 2):
                w.bloecke.pop((x, y, z), None)
        w.setze(0, 1, z, w.b("rail", shape="north_south", waterlogged=False))
        if z % 3 == 0:
            for x in (-2, 2):
                for y in range(1, 4):
                    w.setze(x, y, z, p.h(x, y, z))
            for x in range(-2, 3):
                w.setze(x, 4, z, w.b("dark_oak_log", axis="x"))
    for z in range(int(R * 0.3), int(R * 0.8)):
        w.setze(0, 1, z, w.b("rail", shape="north_south", waterlogged=False))
    w.setze(3, 1, int(R * 0.6), w.b("iron_ore"))
    w.setze(3, 2, int(R * 0.6), w.b("raw_iron_block"))
    for x, z in scheibe(1.5, -4, int(R * 0.5)):
        w.setze(x, 0, z, w.b("magma_block"))
    return w


def kochgrube(seed, g=1):
    """Kochgrube: um eine steingefasste Feuergrube mit einem riesigen Bratspieß stehen Baumstamm-Bänke, Kessel,
    Fässer und ein Holztisch mit Knochen und Krügen."""
    w, p, u, R = basis(seed, g)
    r = _r(2 * u + 1.5, 2)
    for x, z in kreisrand(r + 0.5, 0, 0):
        w.setze(x, 1, z, p.stein(1, x, 1, z))
    for x, z in scheibe(r, 0, 0):
        w.setze(x, 0, z, w.b("magma_block"))
        w.setze(x, 1, z, p.feuerblock(False)) if (x + z) % 2 == 0 else None
    for sx in (-1, 1):
        for y in range(1, 5):
            w.setze(sx * (r + 1), y, 0, p.h(sx * (r + 1), y, 0))
    for x in range(-r - 1, r + 2):
        w.setze(x, 4, 0, w.b("dark_oak_log", axis="x"))
    for x in range(-r + 1, r):
        w.setze(x, 3, 0, w.b("brown_terracotta"))
    for k in range(4):
        a = k * 1.571 + 0.4
        x, z = round(math.cos(a) * (r + 4)), round(math.sin(a) * (r + 4))
        for t in range(-2, 3):
            px = x + (t if abs(math.sin(a)) > 0.5 else 0)
            pz = z + (t if abs(math.cos(a)) > 0.5 else 0)
            w.setze(px, 1, pz, w.b("dark_oak_log", axis="x" if abs(math.sin(a)) > 0.5 else "z"))
    kram(w, R - 3, 1, 0, 5)
    return w


def schamanenaltar(seed, g=1):
    """Schamanenaltar: ein Ring aus Schädelpfählen und knochenbehangenen Stäben um einen flachen Opferstein mit
    grün leuchtenden Kesseln, Rauch und Kräuterbündeln."""
    w, p, u, R = basis(seed, g)
    rng = w.rng
    n = 6 + g * 2
    r = R * 0.6
    for k in range(n):
        a = k / n * 6.283
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        h = 3 + int(rng.random() * 2)
        for y in range(1, h + 1):
            w.setze(x, y, z, p.h(x, y, z, 0.2))
        _schaedel(w, x, h + 1, z, 0.6)
    for x in range(-2, 3):
        for z in range(-1, 2):
            w.setze(x, 1, z, p.stein(1.5, x, 1, z))
    for (x, z) in ((-3, 0), (3, 0)):
        w.setze(x, 1, z, w.b("cauldron"))
        w.setze(x, 0, z, w.b("soul_campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    w.setze(0, 2, 0, w.b("verdant_froglight", axis="y"))
    totempfahl(w, p, 0, -int(r) - 3, u, hoehe=5)
    return w


def uebungsplatz(seed, g=1):
    """Übungsplatz: ein festgestampfter Platz mit Strohpuppen auf Pfählen, Zielscheiben, Waffenständern mit Äxten
    und Speeren, einer Hantelbank aus Stämmen und Zuschauerfässern."""
    w, p, u, R = basis(seed, g)
    rng = w.rng
    for k in range(3 + g):
        a = rng.random() * 6.283
        x, z = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        w.setze(x, 1, z, p.zaun())
        w.setze(x, 2, z, w.b("hay_block", axis="y"))
        w.setze(x, 3, z, w.b("carved_pumpkin", facing="south"))
        w.setze(x - 1, 2, z, p.zaun())
        w.setze(x + 1, 2, z, p.zaun())
    for k in range(2):
        x = -R // 2 + k * R
        for y in range(1, 4):
            w.setze(x, y, -R // 2, w.b("target") if y == 2 else p.zaun())
    for x in range(-2, 3):
        w.setze(x, 1, R // 2, w.b("spruce_fence", north=False, south=False, east=True, west=True, waterlogged=False))
        if x % 2 == 0:
            w.setze(x, 2, R // 2, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                      waterlogged=False))
    for k in range(4):
        w.setze(R - 2, 1, -2 + k, w.b("barrel", facing="up", open=False))
    return w


def riesenkessel(seed, g=2):
    """Riesenkessel: ein gewaltiger schwarzer Eisenkessel auf drei Steinfüßen über einer Feuergrube, darin
    brodelt grünes Gebräu, eine Holztreppe führt zum Rand, Rührpaddel lehnt daran."""
    w, p, u, R = basis(seed, g)
    r = _r(4 * u + 2, 3)
    H = _r(4 * u + 2, 3)
    y0 = 3
    for y in range(y0, y0 + H):
        rr = r * (1 - ((y - y0 - H * 0.6) / H) ** 2 * 0.4)
        for x, z in kreisrand(rr, 0, 0):
            w.setze(x, y, z, w.b("polished_blackstone" if y < y0 + H - 1 else "iron_block"))
    for x, z in scheibe(r * 0.8, 0, 0):
        w.setze(x, y0 - 1, z, w.b("polished_blackstone"))
        w.setze(x, y0 + H - 2, z, w.b("lime_stained_glass" if (x + z) % 3 else "verdant_froglight",
                                      **({} if (x + z) % 3 else {"axis": "y"})))
    for k in range(3):
        a = k * 2.094
        x, z = round(math.cos(a) * r * 0.7), round(math.sin(a) * r * 0.7)
        for y in range(1, y0 - 1):
            w.setze(x, y, z, p.stein(1, x, y, z))
    for x, z in scheibe(r * 0.5, 0, 0):
        w.setze(x, 1, z, p.feuerblock(False)) if (x + z) % 2 == 0 else None
    for k in range(y0 + H - 1):
        w.setze(r + 2 + (y0 + H - 1 - k), k + 1, 0, treppe(w, "spruce", "west"))
    return w


def sumpfhuetten(seed, g=2):
    """Sumpfhütten: Orkhütten auf Pfählen über einem schlammigen Sumpf, verbunden durch wackelige Stege,
    Mangroven und tote Bäume, Schädel auf Pfählen als Warnung."""
    import wald2
    w, p, u, R = basis(seed, g)
    rng = w.rng
    for x, z in scheibe(R, 0, 0):
        if rng.random() < 0.55:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("mud"))
        else:
            w.setze(x, 0, z, w.b("mud" if rng.random() < 0.5 else "moss_block"))
    n = 2 + g
    pos = []
    for k in range(n):
        a = k / n * 6.283 + 0.4
        cx, cz = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        for (dx, dz) in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
            for y in range(-1, 3):
                w.setze(cx + dx, y, cz + dz, p.h(cx + dx, y, cz + dz))
        for x in range(cx - 3, cx + 4):
            for z in range(cz - 3, cz + 4):
                w.setze(x, 2, z, w.b("dark_oak_planks"))
        w2 = orkhuette.__wrapped__ if hasattr(orkhuette, "__wrapped__") else None
        from lib import Welt
        t = Welt(seed + k)
        orkhuette(t, Pal(t, seed), 0, 0, u * 0.7)
        einfuegen(w, t, cx, 2, cz)
        pos.append((cx, cz))
    for (a, b) in zip(pos, pos[1:]):
        nn = int(math.dist(a, b) * 1.5)
        for i in range(nn + 1):
            t = i / nn
            w.setze(round(a[0] + (b[0] - a[0]) * t), 2, round(a[1] + (b[1] - a[1]) * t), w.b("spruce_slab",
                                                                                              type="bottom",
                                                                                              waterlogged=False),
                    False)
    for k in range(2):
        x, z = round((rng.random() - 0.5) * R), round((rng.random() - 0.5) * R)
        einfuegen(w, wald2.totholz(seed + k, "dark_oak"), x, 0, z)
    return w


def schaedelberg(seed, g=2):
    """Schädelberg: ein dunkler Felsen in Form eines riesigen Schädels mit leeren Augenhöhlen, in denen Feuer
    brennen, das Maul ist der Eingang zur Höhle, Pfähle davor."""
    from skulptur import Skulptur, ell, kasten
    w, p, u, R = basis(seed, g, 12)
    S = Skulptur(w, u * 1.3)
    S.mat("s", lambda x, y, z, *_: p.stein(w.rng.random() * 3.5, x, y, z))
    S.plus(ell(0, 6, 0, 6.0, 6.2, 5.6), "s")
    S.plus(kasten(-3.8, 0, 0.5, 3.8, 3.2, 5.2), "s")
    for sx in (-1, 1):
        S.minus(ell(sx * 2.4, 6.5, 4.8, 1.4, 1.4, 1.6))
    S.minus(kasten(-2.2, 0.5, 2.0, 2.2, 2.6, 6.5))
    S.rendern((-7, 0, -7), (7, 13, 7), versatz=(0.5, 1, 0.5))
    for sx in (-1, 1):
        x, y, z = round(sx * 2.4 * u * 1.3), round(6.5 * u * 1.3) + 1, round(4.4 * u * 1.3)
        w.setze(x, y - 1, z, p.stein(1, x, y, z))
        w.setze(x, y, z, p.feuerblock(True))
    for k in range(-2, 3):
        spitzpfahl(w, p, k * 3, R - 2, 3)
    return w


def beutelager(seed, g=1):
    """Beutelager: unter einem Fellsegel türmen sich erbeutete Schätze – Truhen, Fässer, Waffen, Rüstungsständer,
    Goldhaufen und fremde Banner, bewacht von zwei Totems."""
    w, p, u, R = basis(seed, g)
    B = _r(4 * u + 3, 4)
    for (x, z) in ((-B, -B), (B, -B), (-B, B), (B, B)):
        for y in range(1, 6):
            w.setze(x, y, z, p.h(x, y, z))
    for x in range(-B, B + 1):
        for z in range(-B, B + 1):
            w.setze(x, 6 - abs(z) // 3, z, w.b(p.fell[(x + z) % len(p.fell)]))
    rng = w.rng
    for x in range(-B + 1, B):
        for z in range(-B + 1, B):
            r = rng.random()
            if r < 0.25:
                w.setze(x, 1, z, w.b("chest", facing="south", type="single", waterlogged=False))
            elif r < 0.45:
                w.setze(x, 1, z, w.b("gold_block"))
                if rng.random() < 0.5:
                    w.setze(x, 2, z, w.b("raw_gold_block"))
            elif r < 0.6:
                w.setze(x, 1, z, w.b("barrel", facing="up", open=False))
    for sx in (-1, 1):
        totempfahl(w, p, sx * (B + 3), B + 2, u, hoehe=4)
    for (x, z, f) in ((-B, B + 1, "white_wool"), (B, B + 1, "blue_wool")):
        w.setze(x, 4, z, w.b(f))
        w.setze(x, 3, z, w.b(f))
    return w


def barrikade(seed, g=1):
    """Stachelbarrikade: eine Sperre aus schräg gestellten, angespitzten Pfählen und Stacheldraht aus Eisengittern
    quer über einen Weg, ein Schlagbaum-Tor mit Wachfeuer und Schädeln."""
    w, p, u, R = basis(seed, g)
    for x in range(-R + 1, R):
        if abs(x) <= 1:
            continue
        for k in range(3):
            y = 1 + k
            w.setze(x, y, k - 1, p.h(x, y, k)) if x % 2 == 0 else None
            w.setze(x, y + 1, k, p.zaun()) if x % 2 == 0 and k == 2 else None
        w.setze(x, 1, -2, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
    for sx in (-2, 2):
        for y in range(1, 5):
            w.setze(sx, y, 0, p.h(sx, y, 0))
    for x in range(-2, 3):
        w.setze(x, 4, 0, w.b("dark_oak_log", axis="x"))
    _schaedel(w, -2, 5, 0, 0.6)
    _schaedel(w, 2, 5, 0, 0.6)
    w.setze(3, 1, 3, p.feuerblock(True))
    return w


def orkkriegsschiff(seed, g=2):
    """Ork-Kriegsschiff: ein plumpes, schwarz geteertes Kriegsschiff mit Stachelplatten, einem riesigen
    Hornschädel als Bug, zerfetzten roten Segeln und einem Rammsporn."""
    from boote import _dh, _holz, rumpf2
    from schiffe import mast
    from skulptur import Skulptur, ell, kap
    w = _welt(seed)
    u = U[g] * 0.8
    mat = _holz(w, "dark_oak", wand=["black_terracotta", "dark_oak_planks", "blackstone"], streifen="red_terracotta",
                deck="spruce")
    L, B, D, F = 24 * u + 8, 4 * u + 1.6, 2.2 * u + 1, 2.6 * u + 1
    r = rumpf2(w, L, B, D, F, mat, achter=1, vorn=1)
    yb = _dh(r, 0) + 1
    hm = _r(16 * u, 7)
    mast(w, 0, yb - 1, hm + 1, False, "dark_oak_log")
    for y in range(yb + 3, yb + hm - 1):
        hz = int(B * 1.2)
        for z in range(-hz, hz + 1):
            if w.rng.random() < 0.82:
                w.setze(1, y, z, w.b("red_wool" if (y + z) % 5 else "black_wool"))
    xb = int(L / 2)
    S = Skulptur(w, max(0.8, u))
    S.mat("k", w.b("bone_block", axis="y"))
    S.mat("d", w.b("black_concrete"))
    S.plus(ell(0, 0, 0, 1.6, 1.4, 1.6), "k")
    S.plus(ell(0.9, 0.2, 0.8, 0.4, 0.4, 0.3), "d")
    S.plus(ell(0.9, 0.2, -0.8, 0.4, 0.4, 0.3), "d")
    S.plus(kap((0, 1.0, 1.2), (-1.2, 2.6, 2.6), 0.4, 0.12), "k")
    S.plus(kap((0, 1.0, -1.2), (-1.2, 2.6, -2.6), 0.4, 0.12), "k")
    S.rendern((-3, -2, -4), (3, 4, 4), versatz=(xb + 0.5, _dh(r, xb - 1) + 0.5, 0.5))
    for k in range(3):
        w.setze(xb + 1 + k, 0, 0, w.b("iron_block"))
    for x, y, z in r["oben"]:
        if abs(z) >= int(B) and x % 3 == 0:
            w.setze(x, y + 1, z, w.b("pointed_dripstone", vertical_direction="up", thickness="tip",
                                     waterlogged=False), False)
    return w


def versammlungsplatz(seed, g=2):
    """Versammlungsplatz: ein großer Kreis aus Steinen und Stammbänken um eine Feuergrube, an der Kopfseite der
    erhöhte Sitz des Kriegsherrn unter einem Knochenbogen, Trommeln und Banner ringsum."""
    w, p, u, R = basis(seed, g, 12)
    r = R * 0.65
    for x, z in kreisrand(r, 0, 0):
        w.setze(x, 1, z, p.stein(1.5, x, 1, z))
    for x, z in kreisrand(r - 2, 0, 0):
        w.setze(x, 1, z, w.b("dark_oak_log", axis="y")) if (x + z) % 2 else None
    for x, z in scheibe(2, 0, 0):
        w.setze(x, 0, z, w.b("magma_block"))
        w.setze(x, 1, z, p.feuerblock(True)) if (x, z) == (0, 0) else None
    zt = -int(r) + 1
    for x in range(-2, 3):
        for z in range(zt - 1, zt + 2):
            for y in range(1, 3):
                w.setze(x, y, z, p.stein(1.2, x, y, z))
    w.setze(0, 3, zt, treppe(w, "dark_oak", "south"))
    for sx in (-1, 1):
        for k in range(7):
            w.setze(sx * (3 - k // 3), 1 + k, zt - 1 + (k // 4), p.knochen())
    for k in range(4):
        a = k * 1.571 + 0.785
        x, z = round(math.cos(a) * (r + 2)), round(math.sin(a) * (r + 2))
        banner(w, p, x, 1, z, 5, 2)
        w.setze(x + 1, 1, z + 1, w.b("note_block", instrument="basedrum", note=0, powered=False))
    return w


ORKS3 = {
    "rammbock": ("Rammbock", rammbock),
    "ballista": ("Ballista", ballista),
    "kaefige": ("Gefangenenkäfige", kaefige),
    "bannerhuegel": ("Bannerhügel", bannerhuegel),
    "grogbrauerei": ("Grogbrauerei", grogbrauerei),
    "wildschweinpferch": ("Wildschweinpferch", wildschweinpferch),
    "felsenfestung": ("Ork-Felsenfestung", felsenfestung),
    "spaehfels": ("Spähfels", spaehfels),
    "orkhafen": ("Orkhafen", orkhafen),
    "erzmine": ("Erzmine", erzmine),
    "kochgrube": ("Kochgrube", kochgrube),
    "schamanenaltar": ("Schamanenaltar", schamanenaltar),
    "uebungsplatz": ("Übungsplatz", uebungsplatz),
    "riesenkessel": ("Riesenkessel", riesenkessel),
    "sumpfhuetten": ("Sumpfhütten", sumpfhuetten),
    "schaedelberg": ("Schädelberg", schaedelberg),
    "beutelager": ("Beutelager", beutelager),
    "barrikade": ("Stachelbarrikade", barrikade),
    "orkkriegsschiff": ("Ork-Kriegsschiff", orkkriegsschiff),
    "versammlungsplatz": ("Versammlungsplatz", versammlungsplatz),
}

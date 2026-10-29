"""Boote & Schiffe – Erweiterung: Galeere, Karavelle, Hausboot, Einbaum, Lastkahn, Prunkbarke, Walfänger,
Drachenboot, Katamaran, Kriegsfregatte. Wasserlinie y = 0."""

from __future__ import annotations

import math

from boote import U, _dh, _holz, _r, _rahsegel_mast, _ruder, _stil, _welt, _zaun, rumpf2
from lib import Verlauf
from schiffe import dreieckssegel, flagge, mast
from skulptur import Skulptur, ell, kap, kreisrand, platte


def _deckkram(w, r, B, dichte=0.05, ausser=()):
    for x, y, z in r["oben"]:
        if any(a <= x <= b for a, b in ausser):
            continue
        if abs(z) < B - 1.5 and w.rng.random() < dichte:
            w.setze(x, y + 1, z, w.b(["barrel", "barrel", "chest"][int(w.rng.integers(3))], facing="up", open=False)
                    if w.rng.random() < 0.7 else w.b("hay_block", axis="y"), ueberschreiben=False)


def _lateinersegel(w, xm, yb, h, lang, tuch, z=0):
    """Dreieckiges Lateinersegel an schräger Rah."""
    for k in range(lang):
        t = k / lang
        x, y = xm + int(lang * 0.4) - k, yb + int(h * 0.35 + h * 0.65 * t)
        w.setze(x, y, z, w.b("spruce_log", axis="x"))
        for yy in range(yb + 2, y):
            if (y - yy) < (h * 0.9) * (1 - abs(t - 0.4)):
                w.setze(x, yy, z, w.b(tuch[(k // 3) % len(tuch)]))


def galeere(seed, g=1):
    """Kriegsgaleere: langer schlanker Rumpf mit zwei Ruderreihen, Rammsporn aus Bronze, Lateinersegel,
    Schildreihe und überdachtes Heckzelt."""
    w = _welt(seed)
    u = U[g]
    mat = _holz(w, "dark_oak", streifen="red_terracotta" if _stil(seed) == 0 else "blue_terracotta", deck="spruce")
    L, B, D, F = 30 * u + 8, 3 * u + 1.2, 1.4 * u + 0.8, 2 * u + 1
    r = rumpf2(w, L, B, D, F, mat, form="spitz", achter=_r(1.5 * u, 1), sheer=0.3, enden=1.5 * u)
    half = r["half"]
    _ruder(w, r, range(-int(half * 0.6), int(half * 0.6) + 1, 2), F, B, _r(3 * u, 2))
    _ruder(w, r, range(-int(half * 0.6) + 1, int(half * 0.6) + 1, 2), F - 1, B, _r(2.5 * u, 2))
    for k in range(_r(3 * u, 2)):
        w.setze(int(half) + k, -1 + k // 3, 0, w.b("waxed_cut_copper" if k < 2 else "waxed_exposed_cut_copper"))
    xm = int(half * 0.1)
    yb = _dh(r, xm) + 1
    tuch = ["white_wool", "red_wool"] if _stil(seed) == 0 else ["white_wool", "light_blue_wool"]
    mast(w, xm, yb - 1, _r(14 * u, 6) + 1, g >= 2)
    _lateinersegel(w, xm, yb, _r(14 * u, 6), _r(14 * u, 6), tuch)
    for x in range(-int(half * 0.55), int(half * 0.55), 2):
        hb = int(B * 0.95)
        for s in (-1, 1):
            w.setze(x, _dh(r, x) + 1, s * hb, w.b(["red_banner", "white_banner", "blue_banner"][(x // 2) % 3],
                                                  rotation=0 if s > 0 else 8), ueberschreiben=False)
    xh = -int(half * 0.8)
    ya = _dh(r, xh) + 1
    for x in range(xh - 1, xh + _r(4 * u, 3)):
        for z in range(-int(B * 0.6), int(B * 0.6) + 1):
            w.setze(x, ya + _r(2.5 * u, 2), z, w.b(tuch[1] if (x + z) % 2 else tuch[0]))
        for s in (-1, 1):
            if x % 2 == 0:
                for y in range(ya, ya + _r(2.5 * u, 2)):
                    w.setze(x, y, s * int(B * 0.6), _zaun(w, "dark_oak_fence"))
    flagge(w, xm, yb + _r(14 * u, 6) + 1, 0, 3, tuch)
    return w


def karavelle(seed, g=1):
    """Entdeckerkaravelle: kompakter Rumpf mit hohem Achterkastell, drei Masten mit Lateinersegeln und
    Kreuzwappen, Laternen am Heck und ein Kompasshaus."""
    w = _welt(seed)
    u = U[g]
    mat = _holz(w, "oak", wand=["spruce_planks", "oak_planks", "stripped_oak_log"], streifen="yellow_terracotta",
                deck="birch")
    L, B, D, F = 22 * u + 6, 4 * u + 1.2, 2 * u + 1, 2.8 * u + 1
    r = rumpf2(w, L, B, D, F, mat, achter=_r(3 * u, 2), sheer=0.25, heckfenster=True)
    half = r["half"]
    tuch = ["white_wool"]
    for fx, fh in ((0.3, 0.8), (-0.05, 1.0), (-0.38, 0.65)):
        xm = int(half * fx * 2)
        yb = _dh(r, xm) + 1
        h = _r(18 * u * fh, 6)
        mast(w, xm, yb - 1, h + 1, g >= 2)
        _lateinersegel(w, xm, yb, h, _r(h * 0.9, 4), tuch)
        yk = yb + int(h * 0.6)
        if fh == 1.0:
            for d in range(-_r(1.5 * u, 1), _r(1.5 * u, 1) + 1):
                w.setze(xm - int(h * 0.25), yk + d, 1, w.b("red_wool"))
                w.setze(xm - int(h * 0.25) + d, yk, 1, w.b("red_wool"))
        flagge(w, xm, yb + h + 1, 0, 2, ["red_wool", "white_wool"])
    xh = -int(half) + 1
    for s in (-1, 1):
        w.setze(xh, _dh(r, xh) + 1, s * int(B * 0.5), _zaun(w, "oak_fence"))
        w.setze(xh, _dh(r, xh) + 2, s * int(B * 0.5), w.b("lantern", hanging=False, waterlogged=False))
    xk = -int(half * 0.5)
    w.setze(xk, _dh(r, xk) + 1, 0, w.b("lodestone"))
    _deckkram(w, r, B, 0.04)
    return w


def hausboot(seed, g=1):
    """Hausboot: ein breiter flacher Kahn mit einem kleinen Fachwerkhaus samt Ziegeldach, Blumenkästen, Kamin,
    Wäscheleine und Sonnendeck mit Liegestühlen."""
    import pracht as P
    from haeuser import HAUSPOOL
    w = _welt(seed)
    u = U[g] * 0.8
    mat = _holz(w, "spruce", wand=["green_terracotta", "lime_terracotta", "white_terracotta"] if _stil(seed) == 0
                else ["blue_terracotta", "light_blue_terracotta", "white_terracotta"], streifen="white_terracotta",
                deck="oak")
    L, B, D, F = 20 * u + 6, 4 * u + 1.6, 1 * u + 0.6, 1.4 * u + 0.8
    r = rumpf2(w, L, B, D, F, mat, form="flach", sheer=0.08)
    half = r["half"]
    yb = _dh(r, 0) + 1
    d = dict(HAUSPOOL["fachwerk_rot" if _stil(seed) == 0 else "putz_blau"])
    d["blumen"] = 0.9
    st = P.Stil(w, **d)
    hx = int(half * 0.5)
    hz = int(B * 0.65)
    P.gebaeude(w, st, -hx, -hz, hx // 3, hz, y0=yb, etagen=1, eh=_r(3.5 * u, 3), dach="sattel", tuer="east",
               gauben=False, kamine=1, sockel_h=0)
    xs = hx // 3 + 2
    for x in range(xs, int(half * 0.8)):
        for z in (-int(B * 0.5), int(B * 0.5)):
            if x % 3 == 0:
                w.setze(x, yb, z, w.b("white_bed", facing="east", part="foot", occupied=False))
    w.setze(int(half * 0.7), yb, 0, w.b("potted_flowering_azalea_bush"))
    for x in range(-hx, hx // 3 + 1):
        w.setze(x, yb + 2, -int(B) - 0, w.b("tripwire", attached=False, disarmed=False, powered=False,
                                            north=False, south=False, east=True, west=True), ueberschreiben=False)
    return w


def einbaum(seed, g=0):
    """Einbaum-Kanu: aus einem Stamm gehöhlt, mit Paddeln, Angel, Fischkorb und Federschmuck am Bug."""
    w = _welt(seed)
    u = U[g] * 0.6
    art = "jungle" if _stil(seed) == 0 else "spruce"
    mat = dict(unten=Verlauf(w, "u", [f"{art}_log"] * 2), wand=Verlauf(w, "w", [f"{art}_log", f"stripped_{art}_log"]),
               streifen=None, leiste=f"stripped_{art}_log", zaun=f"{art}_fence",
               deck=Verlauf(w, "d", [f"stripped_{art}_log"] * 2), gold=False)
    L, B, D, F = 14 * u + 6, 1.6 * u + 1, 0.8 * u + 0.6, 1 * u + 0.6
    r = rumpf2(w, L, B, D, F, mat, form="spitz", enden=0.8 * u, reling=False, offen=True)
    half = r["half"]
    for x, y, z in r["oben"]:
        if abs(x) < half * 0.8 and abs(z) < B - 0.8:
            for yy in range(1, y + 1):
                w.bloecke.pop((x, yy, z), None)
            w.setze(x, 0, z, w.b(f"stripped_{art}_log", axis="x"))
    for s in (-1, 1):
        x = s * int(half * 0.3)
        for k in range(3):
            w.setze(x + k * s, 1, s * (int(B) + 1), _zaun(w, f"{art}_fence"))
        w.setze(x + 3 * s, 1, s * (int(B) + 1), w.b(f"{art}_trapdoor", facing="north" if s > 0 else "south",
                                                    half="bottom", open=True, powered=False, waterlogged=False))
    xb = int(half) - 1
    w.setze(xb, _dh(r, xb) + 1, 0, w.b("red_wool") if _stil(seed) == 0 else w.b("white_wool"))
    w.setze(xb, _dh(r, xb) + 2, 0, w.b("feather" if False else "white_carpet"))
    w.setze(0, 0, 0, w.b("barrel", facing="up", open=False))
    return w


def lastkahn(seed, g=1):
    """Fluss-Lastkahn: flacher breiter Kahn, hoch beladen mit Kisten, Fässern, Heu und Holzstämmen unter Planen,
    kleines Steuerhaus, Treidelmast und Bootshaken."""
    w = _welt(seed)
    u = U[g]
    mat = _holz(w, "spruce", streifen="black_terracotta", deck="spruce")
    L, B, D, F = 24 * u + 6, 4.5 * u + 1.5, 1 * u + 0.6, 1.5 * u + 0.8
    r = rumpf2(w, L, B, D, F, mat, form="flach", sheer=0.1)
    half = r["half"]
    yb = _dh(r, 0) + 1
    rng = w.rng
    ladung = ["barrel", "chest", "hay_block", "spruce_log", "oak_log", "barrel", "white_wool", "brown_wool"]
    for x in range(-int(half * 0.5), int(half * 0.7)):
        for z in range(-int(B * 0.75), int(B * 0.75) + 1):
            hh = int(1 + 2 * u * (1 - abs(z) / (B * 0.8)) * (0.6 + 0.4 * math.sin(x * 0.7)))
            for y in range(yb, yb + hh):
                n = ladung[((x // 3) * 7 + (z // 2) * 3 + y) % len(ladung)]
                if "log" in n:
                    blk = w.b(n, axis="x")
                elif n in ("barrel", "chest"):
                    blk = w.b("barrel", facing="up", open=False) if n == "barrel" else w.b("chest", facing="south",
                                                                                          type="single",
                                                                                          waterlogged=False)
                elif n == "hay_block":
                    blk = w.b(n, axis="y")
                else:
                    blk = w.b(n)
                w.setze(x, y, z, blk)
    xh = -int(half * 0.75)
    for x in range(xh - 1, xh + 2):
        for z in (-1, 0, 1):
            for y in range(yb, yb + _r(2.5 * u, 2)):
                if abs(x - xh) == 1 or abs(z) == 1:
                    w.setze(x, y, z, w.b("spruce_planks") if y < yb + _r(2.5 * u, 2) - 1 else w.b("glass_pane",
                                                                                                    north=False,
                                                                                                    south=False,
                                                                                                    east=False,
                                                                                                    west=False,
                                                                                                    waterlogged=False))
            w.setze(x, yb + _r(2.5 * u, 2), z, w.b("spruce_slab", type="bottom", waterlogged=False))
    xm = int(half * 0.8)
    for y in range(yb, yb + _r(8 * u, 4)):
        w.setze(xm, y, 0, w.b("spruce_log", axis="y"))
    w.setze(xm, yb + _r(8 * u, 4), 0, w.b("lantern", hanging=False, waterlogged=False))
    return w


def prunkbarke(seed, g=1):
    """Königliche Prunkbarke: vergoldeter Rumpf, purpurner Baldachin auf Säulen über einem Thron, Ruderer,
    Schwanenhals-Steven, Laternen und Fahnen."""
    w = _welt(seed)
    u = U[g]
    mat = dict(unten=Verlauf(w, "u", ["dark_oak_planks", "dark_oak_planks", "spruce_planks"]),
               wand=Verlauf(w, "w", ["purple_terracotta", "magenta_terracotta", "purple_concrete"] if _stil(seed) == 0
                            else ["blue_terracotta", "blue_concrete", "light_blue_terracotta"]),
               streifen="gold_block", leiste="stripped_dark_oak_log", zaun="dark_oak_fence",
               deck=Verlauf(w, "d", ["dark_oak_planks", "spruce_planks", "stripped_dark_oak_log"]), gold=True)
    L, B, D, F = 22 * u + 6, 3.4 * u + 1.2, 1.2 * u + 0.8, 2 * u + 1
    r = rumpf2(w, L, B, D, F, mat, form="spitz", enden=3 * u + 1, sheer=0.2)
    half = r["half"]
    _ruder(w, r, range(-int(half * 0.5), int(half * 0.5) + 1, 3), F, B, _r(2.5 * u, 2), "dark_oak_fence")
    yb = _dh(r, 0) + 1
    farbe = "purple_wool" if _stil(seed) == 0 else "blue_wool"
    bx, bz = _r(3 * u, 2), int(B * 0.7)
    hh = _r(4 * u, 3)
    for sx in (-bx, bx):
        for sz in (-bz, bz):
            for y in range(yb, yb + hh):
                w.setze(sx, y, sz, w.b("gold_block") if y == yb else _zaun(w, "dark_oak_fence"))
    for x in range(-bx - 1, bx + 2):
        for z in range(-bz - 1, bz + 2):
            k = max(abs(x) / (bx + 1), abs(z) / (bz + 1))
            w.setze(x, yb + hh + int((1 - k) * 2 * u), z, w.b(farbe if (x + z) % 3 else "yellow_wool"))
    w.setze(0, yb + hh + int(2 * u) + 1, 0, w.b("gold_block"))
    w.setze(0, yb, 0, w.b("dark_oak_stairs", facing="east", half="bottom", shape="straight", waterlogged=False))
    w.setze(-1, yb, 0, w.b("gold_block"))
    w.setze(-1, yb + 1, 0, w.b(farbe.replace("wool", "banner").replace("purple", "purple"), rotation=4))
    xb = int(half) - 1
    S = Skulptur(w, 0.5 * u + 0.2)
    S.mat("g", lambda *a: w.b("gold_block"))
    S.plus(kap((0, 0, 0), (1, 4, 0), 0.6, 0.5), "g")
    S.plus(kap((1, 4, 0), (2.2, 4.2, 0), 0.6, 0.3), "g")
    S.rendern((-2, -1, -2), (4, 6, 2), versatz=(xb + 0.5, _dh(r, xb) + 1.01, 0.5))
    for x in (-int(half) + 2, int(half) - 3):
        w.setze(x, _dh(r, x) + 1, 0, _zaun(w, "dark_oak_fence"))
        w.setze(x, _dh(r, x) + 2, 0, w.b("lantern", hanging=False, waterlogged=False))
    return w


def walfaenger(seed, g=1):
    """Walfänger: robuster Dreimaster mit Tranofen aus Ziegeln an Deck, Fangbooten an Davits, Harpunen,
    Ausguckkorb und wettergegerbten Segeln."""
    w = _welt(seed)
    u = U[g]
    mat = _holz(w, "spruce", wand=["spruce_planks", "dark_oak_planks", "stripped_spruce_log"],
                streifen="white_terracotta" if _stil(seed) == 0 else "black_terracotta", deck="oak")
    L, B, D, F = 24 * u + 6, 4.2 * u + 1.4, 2.4 * u + 1, 2.8 * u + 1
    r = rumpf2(w, L, B, D, F, mat, achter=_r(1.5 * u, 1), sheer=0.18)
    half = r["half"]
    tuch = Verlauf(w, "Segel", ["light_gray_wool", "white_wool"])
    for fx, fh in ((0.3, 0.85), (0.0, 1.0), (-0.32, 0.75)):
        xm = int(half * fx * 2)
        _rahsegel_mast(w, xm, _dh(r, xm) + 1, _r(18 * u * fh, 6), B * 0.85, tuch, stufen=(0.45, 0.8),
                       bauch=max(1, 1.2 * u), dick=g >= 2)
    xo = int(half * 0.25)
    yb = _dh(r, xo) + 1
    for x in range(xo - 1, xo + 2):
        for z in (-1, 0, 1):
            w.setze(x, yb, z, w.b("bricks"))
            w.setze(x, yb + 1, z, w.b("bricks") if abs(x - xo) + abs(z) > 0 else w.b("campfire", lit=True,
                                                                                    signal_fire=False,
                                                                                    facing="north",
                                                                                    waterlogged=False))
    for s in (-1, 1):
        zb = s * (int(B) + 1)
        for x in range(-int(half * 0.4), -int(half * 0.4) + _r(5 * u, 3)):
            w.setze(x, int(F) + 1, zb, w.b("white_terracotta"))
        for x in (-int(half * 0.4) - 1, -int(half * 0.4) + _r(5 * u, 3)):
            w.setze(x, int(F) + 2, zb - s, _zaun(w, "spruce_fence"))
            w.setze(x, int(F) + 3, zb - s, _zaun(w, "spruce_fence"))
    xb = int(half) - 1
    for k in range(_r(3 * u, 2)):
        w.setze(xb - k, _dh(r, xb) + 1, int(B * 0.4), w.b("lightning_rod", facing="east", powered=False,
                                                          waterlogged=False))
    _deckkram(w, r, B, 0.04, ausser=((xo - 2, xo + 2),))
    return w


def drachenboot(seed, g=1):
    """Fernöstliches Drachenboot: langes schmales Rennboot mit Drachenkopf und Schwanz, geschuppter Rumpf, Trommel
    in der Mitte, Paddler-Bänke und bunte Wimpel."""
    w = _welt(seed)
    u = U[g]
    farbe = ["red_terracotta", "orange_terracotta", "yellow_terracotta"] if _stil(seed) == 0 else \
        ["green_terracotta", "lime_terracotta", "yellow_terracotta"]
    mat = dict(unten=Verlauf(w, "u", [farbe[0], farbe[0], farbe[1]]),
               wand=Verlauf(w, "w", farbe), streifen="gold_block", leiste="stripped_jungle_log",
               zaun="jungle_fence", deck=Verlauf(w, "d", ["jungle_planks", "bamboo_planks", "jungle_planks"]),
               gold=False)
    L, B, D, F = 28 * u + 8, 2 * u + 1, 0.8 * u + 0.6, 1.2 * u + 0.8
    r = rumpf2(w, L, B, D, F, mat, form="spitz", enden=1.2 * u, reling=False, offen=True)
    half = r["half"]
    for x in range(-int(half * 0.6), int(half * 0.6) + 1, 2):
        for z in range(-int(B * 0.7), int(B * 0.7) + 1):
            w.setze(x, int(F) - 1 if F > 1.5 else 0, z, platte(w, "bamboo"), ueberschreiben=False)
    _ruder(w, r, range(-int(half * 0.6), int(half * 0.6) + 1, 2), F, B, _r(1.8 * u, 1), "bamboo_fence")
    w.setze(0, _dh(r, 0) + 1, 0, w.b("note_block", instrument="basedrum", note=0, powered=False))
    s = 0.7 * u + 0.3
    S = Skulptur(w, s)
    S.mat("k", lambda x, y, z, *_: w.b(farbe[0]) if (x + y) % 2 else w.b(farbe[1]))
    S.mat("g", lambda *a: w.b("gold_block"))
    S.mat("a", lambda *a: w.b("lime_concrete"))
    S.plus(kap((0, 0, 0), (1.5, 4, 0), 1.0, 0.8), "k")
    S.plus(ell(2.5, 4.4, 0, 2.0, 1.2, 1.0), "k")
    S.plus(kap((3.5, 3.8, 0), (5, 3.6, 0), 0.6, 0.4), "k")
    for sz in (-1, 1):
        S.plus(kap((1.8, 5.2, sz * 0.5), (0.2, 6.6, sz * 1.0), 0.3, 0.15), "g")
        S.plus(ell(3.0, 4.9, sz * 0.75, 0.3, 0.3, 0.3), "a")
    S.rendern((-2, -1, -4), (7, 8, 4), versatz=(int(half) - 1 + 0.5, _dh(r, int(half) - 1) + 0.01, 0.5))
    T = Skulptur(w, s)
    T.mat("k", lambda x, y, z, *_: w.b(farbe[0]) if (x + y) % 2 else w.b(farbe[1]))
    T.plus(kap((0, 0, 0), (-1.5, 3, 0), 0.8, 0.3), "k")
    T.plus(kap((-1.5, 3, 0), (-0.5, 4.5, 0), 0.3, 0.15), "k")
    T.rendern((-3, -1, -2), (2, 6, 2), versatz=(-int(half) + 1 + 0.5, _dh(r, -int(half) + 1) + 0.01, 0.5))
    return w


def katamaran(seed, g=1):
    """Insel-Katamaran: zwei schlanke Rümpfe, verbunden durch ein Bambusdeck mit Palmdach-Hütte, großes
    Krabbenscheren-Segel, Paddel und Netze."""
    w = _welt(seed)
    u = U[g]
    mat = dict(unten=Verlauf(w, "u", ["jungle_planks", "jungle_planks", "stripped_jungle_log"]),
               wand=Verlauf(w, "w", ["jungle_planks", "stripped_jungle_log", "bamboo_planks"]),
               streifen="white_terracotta", leiste="stripped_jungle_log", zaun="bamboo_fence",
               deck=Verlauf(w, "d", ["bamboo_planks", "bamboo_mosaic", "bamboo_planks"]), gold=False)
    L, B, D, F = 18 * u + 6, 1.4 * u + 0.8, 1 * u + 0.6, 1.2 * u + 0.8
    abst = _r(4 * u + 2, 3)
    from lib import Welt
    for s in (-1, 1):
        t = Welt(seed)
        t.P = w.P
        rumpf2(t, L, B, D, F, mat, form="spitz", enden=0.6 * u, reling=False)
        for (x, y, z), b in t.bloecke.items():
            w.setze(x, y, z + s * abst, b)
    yd = int(F) + 1
    for x in range(-int(L * 0.3), int(L * 0.3) + 1):
        for z in range(-abst, abst + 1):
            w.setze(x, yd, z, w.b("bamboo_planks") if x % 3 else w.b("stripped_bamboo_block", axis="z"))
    for x in range(-int(L * 0.25), -int(L * 0.25) + _r(4 * u, 3)):
        for z in range(-abst + 1, abst):
            k = abs(z) / abst
            w.setze(x, yd + _r(2.5 * u, 2) + int((1 - k) * 1.5 * u), z, w.b("hay_block", axis="x"))
    for x in (-int(L * 0.25), -int(L * 0.25) + _r(4 * u, 3) - 1):
        for z in (-abst + 1, abst - 1):
            for y in range(yd + 1, yd + _r(2.5 * u, 2)):
                w.setze(x, y, z, w.b("bamboo_fence", north=False, south=False, east=False, west=False,
                                     waterlogged=False))
    xm = int(L * 0.15)
    h = _r(14 * u, 6)
    mast(w, xm, yd, h, False, "stripped_bamboo_block")
    tuch = w.b("orange_wool" if _stil(seed) == 0 else "white_wool")
    for y in range(yd + 2, yd + h):
        t = (y - yd) / h
        breit = int(h * 0.5 * math.sin(t * math.pi) ** 0.6)
        for x in range(xm - breit, xm):
            w.setze(x, y, 0, tuch)
    return w


def fregatte(seed, g=2):
    """Kriegsfregatte: zwei Kanonendecks mit Pforten, drei vollgetakelte Masten mit Rahsegeln, Klüverbaum mit
    Vorsegeln, prunkvolles Heck mit Galerie und Laternen."""
    w = _welt(seed)
    u = U[g]
    mat = _holz(w, "dark_oak", streifen="yellow_terracotta" if _stil(seed) == 0 else "white_terracotta",
                deck="spruce")
    mat["fenster"] = "orange_stained_glass"
    L, B, D, F = 30 * u + 8, 4.8 * u + 1.6, 2.8 * u + 1, 4 * u + 1.4
    r = rumpf2(w, L, B, D, F, mat, achter=_r(2.5 * u, 2), vorn=_r(1.2 * u, 1), sheer=0.16, kanonen=True,
               heckfenster=True)
    half = r["half"]
    gp = _r(F * 0.5, 1)
    for x in range(-int(half * 0.7), int(half * 0.7), 3):
        for s in (-1, 1):
            for yy in (gp, gp + _r(1.5 * u, 2)):
                if yy < F:
                    zz = s * (int(B * 0.98) + 1)
                    w.setze(x, yy, zz, w.b("black_terracotta"), ueberschreiben=True)
    tuch = Verlauf(w, "Segel", ["white_wool", "white_wool"])
    for fx, fh in ((0.3, 0.9), (0.0, 1.0), (-0.3, 0.8)):
        xm = int(half * fx * 2)
        _rahsegel_mast(w, xm, _dh(r, xm) + 1, _r(24 * u * fh, 8), B * 0.9, tuch, stufen=(0.35, 0.62, 0.86),
                       bauch=max(1, 1.5 * u), dick=g >= 2, flaggen=["blue_wool", "white_wool"])
    xb = int(half)
    yk = _dh(r, xb - 1) + 1
    lk = _r(8 * u, 3)
    for k in range(lk):
        w.setze(xb + k, yk + k // 2, 0, w.b("spruce_log", axis="x"))
    xm0 = int(half * 0.6)
    ym0 = _dh(r, xm0) + _r(20 * u, 8)
    dreieckssegel(w, (xm0, ym0), (xm0, _dh(r, xm0) + 3), (xb + lk - 1, yk + lk // 2), 0, w.b("white_wool"))
    xh = -int(half) + 1
    yh = _dh(r, xh)
    for z in range(-int(B * 0.6), int(B * 0.6) + 1):
        w.setze(xh - 1, yh - 2, z, w.b("dark_oak_slab", type="top", waterlogged=False))
        if z % 2 == 0:
            w.setze(xh - 1, yh - 1, z, _zaun(w, "dark_oak_fence"))
    for s in (-1, 1):
        w.setze(xh, yh + 1, s * int(B * 0.6), _zaun(w, "dark_oak_fence"))
        w.setze(xh, yh + 2, s * int(B * 0.6), w.b("lantern", hanging=False, waterlogged=False))
    _deckkram(w, r, B, 0.025)
    return w


NEU = {
    "galeere": ("Kriegsgaleere", galeere),
    "karavelle": ("Karavelle", karavelle),
    "hausboot": ("Hausboot", hausboot),
    "einbaum": ("Einbaum-Kanu", einbaum),
    "lastkahn": ("Lastkahn", lastkahn),
    "prunkbarke": ("Prunkbarke", prunkbarke),
    "walfaenger": ("Walfänger", walfaenger),
    "drachenboot": ("Drachenboot", drachenboot),
    "katamaran": ("Katamaran", katamaran),
    "fregatte": ("Kriegsfregatte", fregatte),
}

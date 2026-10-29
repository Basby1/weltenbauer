"""Schwebeberge II – zwanzig weitere schwebende Felsberge: Kristall-, Schnee-, Tafel-, Kirschblüten- und
Herbstberg, Zwillingsberge mit Hängebrücke, Wasserfallberg, Tempel-, Burg- und Klosterberg, Pilz-, Lava-, End-,
Nether-, Basalt- und Moosberg, Ringberg, Nadelkranz, Kettenberg und Weltenbaum-Berg."""

from __future__ import annotations

import math

import modbloecke as MB
import wald2
from feinbau import Dachmat, Mix, kegeldach, laterne, mauer, platte, satteldach, stamm, tuer, zaun
from himmelsstadt import _berg, _dschungel, _lianen, _wasserfall, _welt, haengebruecke_teil
from himmelsstadt2 import eckturm, haus
from lib import Rauschen, Verlauf, einfuegen

HG = [24, 40, 64, 100]
RG = [6, 9, 14, 21]
LG = [8, 12, 18, 26]


def berg(seed, g, fels, gras="grass_block", moos="moss_block", cx=0, cz=0, hf=1.0, rf=1.0, y_u=None, w=None):
    w = w or _welt(seed)
    rs = Rauschen(w, 5)
    F = Verlauf(w, "Fels", fels)
    gb = w.b(gras, snowy=False) if gras == "grass_block" else w.b(gras)
    mb = w.b(moos)
    H, R = HG[g] * hf, RG[g] * rf
    y_u = LG[g] if y_u is None else y_u
    oben = _berg(w, rs, cx, cz, y_u, H, R, F, mb, gb, None)
    return w, oben, (cx, cz, y_u, H, R), set(F.ids) | {mb, gb}


def gipfelplatz(w, oben, cx, cz, r, gras="grass_block"):
    """Ebnet den Gipfel um (cx, cz) auf die mittlere Höhe; gibt y (Bodenhöhe) zurück."""
    zellen = [p for p in oben if math.hypot(p[0] - cx, p[1] - cz) <= r]
    if not zellen:
        return max(oben.values())
    ys = sorted(oben[p] for p in zellen)
    y = ys[len(ys) // 2]
    unter = w.bloecke.get((round(cx), y - 1, round(cz)), w.b("stone"))
    for p in zellen:
        y0 = oben[p]
        for yy in range(min(y0, y) - 6, y):
            if (p[0], yy, p[1]) not in w.bloecke:
                w.setze(p[0], yy, p[1], unter)
        for yy in range(y + 1, y0 + 1):
            w.bloecke.pop((p[0], yy, p[1]), None)
        w.setze(p[0], y, p[1], w.b(gras, snowy=False) if gras == "grass_block" else w.b(gras))
        oben[p] = y
    return y


def streuen(w, oben, chance, fn):
    rng = w.rng
    for (x, z), y in list(oben.items()):
        if w.frei(x, y + 1, z) and rng.random() < chance:
            fn(x, y, z)


def baeume(w, oben, n, macher, abstand=5, rand=0.0, cx=0, cz=0):
    rng = w.rng
    pos = sorted(oben.items(), key=lambda kv: rng.random())
    gesetzt = []
    for (x, z), y in pos:
        if len(gesetzt) >= n:
            break
        if any(math.hypot(x - a, z - b) < abstand for a, b in gesetzt):
            continue
        if not all(w.frei(x, y + h, z) for h in (1, 3, 6)):
            continue
        einfuegen(w, macher(int(rng.integers(1, 10 ** 6))), x, y, z)
        gesetzt.append((x, z))


def kleinkram(w, oben, dichte=0.35, blumen=("poppy", "dandelion", "azure_bluet", "oxeye_daisy", "cornflower")):
    gras = w.b("grass_block", snowy=False)
    rng = w.rng
    for (x, z), y in oben.items():
        if w.bloecke.get((x, y, z)) != gras or not w.frei(x, y + 1, z):
            continue
        r = rng.random()
        if r < dichte * 0.55:
            w.setze(x, y + 1, z, w.b("grass"))
        elif r < dichte * 0.68:
            w.setze(x, y + 1, z, w.b("fern"))
        elif blumen and r < dichte * 0.8:
            w.setze(x, y + 1, z, w.b(blumen[int(rng.random() * len(blumen))]))


def haengend(w, traeger, art="cave", anteil=0.06, lmax=8):
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        if b not in traeger or not w.frei(x, y - 1, z) or rng.random() > anteil:
            continue
        L = 1 + int(rng.random() * lmax)
        for k in range(1, L + 1):
            if not w.frei(x, y - k, z) or y - k < 2:
                break
            ende = k == L
            if art == "cave":
                blk = w.b("cave_vines", age=25, berries=True) if ende else w.b("cave_vines_plant",
                                                                               berries=rng.random() < 0.25)
            elif art == "wurzel":
                blk = w.b("hanging_roots", waterlogged=False) if ende else w.b("mangrove_roots", waterlogged=False)
            elif art == "weeping":
                blk = w.b("weeping_vines", age=25) if ende else w.b("weeping_vines_plant")
            elif art == "eis":
                blk = w.b("pointed_dripstone", vertical_direction="down", thickness="tip", waterlogged=False) \
                    if ende else w.b("packed_ice")
            else:
                blk = w.b(art)
            w.setze(x, y - k, z, blk)


def begleiter(w, n, g, fels, gras="grass_block", moos="moss_block"):
    rng = w.rng
    for k in range(n):
        a = rng.random() * 6.283
        d = RG[g] * (1.7 + rng.random() * 1.3)
        berg(0, g, fels, gras, moos, cx=math.cos(a) * d, cz=math.sin(a) * d, hf=0.18 + rng.random() * 0.15,
             rf=0.25 + rng.random() * 0.15, y_u=LG[g] + HG[g] * (0.2 + 0.5 * rng.random()), w=w)


def gipfel(oben):
    (x, z), y = max(oben.items(), key=lambda kv: kv[1])
    return x, y, z


# ============================================================================ Berge

def kristallberg(seed, g=1):
    """Kristallberg: dunkler Fels mit hellen Kalzitbändern, aus Gipfel und Unterseite wachsen riesige
    Amethystkristalle, Moos und Leuchtflechten in den Spalten."""
    from kristall import kristall
    fels = ["deepslate", "tuff", "calcite", "smooth_basalt", "calcite"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels)
    rng = w.rng
    s = HG[g] / 40
    for k in range(4 + g * 2):
        (x, z), y = list(oben.items())[int(rng.random() * len(oben))]
        kristall(w, (x, y, z), (rng.normal() * 0.35, 1, rng.normal() * 0.35), (4 + rng.random() * 6) * s,
                 (1 + rng.random()) * s, art="amethyst")
    for k in range(3 + g):
        a = rng.random() * 6.283
        kristall(w, (cx + math.cos(a) * R * 0.2, y_u + H * 0.1, cz + math.sin(a) * R * 0.2),
                 (math.cos(a) * 0.3, -1, math.sin(a) * 0.3), (5 + rng.random() * 6) * s, (1.2 + rng.random()) * s,
                 art="amethyst" if k % 2 else "saphir")
    kleinkram(w, oben, 0.3)
    begleiter(w, 2 + g, g, fels)
    return w


def schneegipfel(seed, g=1):
    """Schneegipfel: ein schwebender Hochgebirgsberg mit Schneekappe, verschneiten Fichten und einer kleinen
    Berghütte, unten hängen Eiszapfen."""
    fels = ["deepslate", "stone", "andesite", "diorite", "calcite"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels, "snow_block", "packed_ice")
    baeume(w, oben, 3 + g * 2, lambda s: wald2.fichte(s, schnee=True), abstand=4)
    if g >= 1:
        y = gipfelplatz(w, oben, cx, cz, 4, "snow_block")
        haus(w, round(cx), round(cz), 6, 5, y + 1, "stein", geschosse=1 + (g > 1), tuer_s="south")
    streuen(w, oben, 0.4, lambda x, y, z: w.setze(x, y + 1, z, w.b("snow", layers=1 + int(w.rng.random() * 2))))
    haengend(w, tr, "eis", 0.05, 4)
    return w


def tafelberg(seed, g=1):
    """Tafelberg: ein schwebender Mesa-Berg mit roten, orangen und gelben Gesteinsschichten, oben Sand, Kakteen,
    tote Büsche und eine Lehmhütte."""
    fels = ["red_terracotta", "orange_terracotta", "terracotta", "yellow_terracotta", "smooth_sandstone"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels, "sand", "red_sand", rf=1.15)
    rng = w.rng

    def kaktus(x, y, z):
        for k in range(1, 2 + int(rng.random() * 3)):
            w.setze(x, y + k, z, w.b("cactus", age=0))
    streuen(w, oben, 0.025, kaktus)
    streuen(w, oben, 0.04, lambda x, y, z: w.setze(x, y + 1, z, w.b("dead_bush")))
    if g >= 1:
        y = gipfelplatz(w, oben, cx, cz, 4, "sand")
        haus(w, round(cx), round(cz), 6, 6, y + 1, "terrakotta", geschosse=1, tuer_s="south")
    begleiter(w, 1 + g, g, fels, "sand", "red_sand")
    return w


def kirschberg(seed, g=1):
    """Kirschblütenberg: ein grüner Schwebeberg voller blühender Kirschbäume, rosa Blütenteppich und ein kleiner
    Schrein auf dem Gipfel."""
    fels = ["deepslate", "tuff", "andesite", "stone", "calcite"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels)
    baeume(w, oben, 2 + g * 2, wald2.kirschbaum, abstand=6)
    rng = w.rng
    streuen(w, oben, 0.3, lambda x, y, z: w.setze(x, y + 1, z, w.b("pink_petals", facing="north",
                                                                   flower_amount=1 + int(rng.random() * 4)))
            if w.P.name(w.bloecke.get((x, y, z), 0)) == "minecraft:grass_block" else None)
    haengend(w, tr, "cave", 0.04, int(4 + 3 * g))
    begleiter(w, 1 + g, g, fels)
    return w


def herbstberg(seed, g=1):
    """Herbstberg: ein Schwebeberg mit rot, orange und golden gefärbten Laubbäumen, Laubteppich und Kürbissen."""
    fels = ["deepslate", "tuff", "andesite", "stone", "calcite"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels)
    rng = w.rng
    arten = ["maple", "orange_autumn", "yellow_autumn"]

    def macher(sd):
        t = wald2.laubbaum(sd, "oak" if sd % 3 else "birch", H=6 + g)
        f = MB.herbstlaub(t, arten[sd % 3])
        for p, b in list(t.bloecke.items()):
            if t.P.name(b).endswith("_leaves"):
                t.bloecke[p] = f
        return t
    baeume(w, oben, 3 + g * 2, macher, abstand=5)
    streuen(w, oben, 0.02, lambda x, y, z: w.setze(x, y + 1, z, w.b("pumpkin")))
    streuen(w, oben, 0.15, lambda x, y, z: w.setze(x, y + 1, z, w.b("orange_carpet" if rng.random() < 0.5 else
                                                                   "red_carpet" if rng.random() < 0.5 else
                                                                   "yellow_carpet")))
    begleiter(w, 1 + g, g, fels)
    return w


def zwillingsberge(seed, g=1):
    """Zwillingsberge: zwei schwebende Gipfel, verbunden durch eine lange Hängebrücke mit Laternen, auf jedem ein
    Wachhäuschen, dazwischen Lianen."""
    fels = ["deepslate", "tuff", "andesite", "stone", "calcite"]
    d = RG[g] * 1.5
    w, o1, k1, tr = berg(seed, g, fels, cx=-d, rf=0.8)
    _, o2, k2, _ = berg(seed, g, fels, cx=d, rf=0.8, hf=0.85, w=w, y_u=LG[g] + HG[g] * 0.1)
    yb = int(min(k1[2] + k1[3], k2[2] + k2[3]) * 0.8)
    x0 = max(x for (x, z) in o1 if abs(z) <= 1)
    for x in range(round(-d), x0 + 2):
        pass
    xa = max(x for (x, y, z), b in w.bloecke.items() if abs(z) <= 0 and y == yb and x < 0)
    xb = min(x for (x, y, z), b in w.bloecke.items() if abs(z) <= 0 and y == yb and x > 0)
    haengebruecke_teil(w, xa, yb, 0, xb - xa, durchhang=2 + g)
    for o, k in ((o1, k1), (o2, k2)):
        _dschungel(w, o, seed, 0.6, g)
    haengend(w, tr, "cave", 0.04, 4 + g * 2)
    return w


def wasserfallberg(seed, g=1):
    """Wasserfallberg: von einem grünen Gipfelplateau mit Teichen stürzen gleich mehrere Wasserfälle in alle
    Richtungen über die Felskanten in die Tiefe."""
    fels = ["deepslate", "tuff", "andesite", "stone", "calcite"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels, rf=1.1)
    for k in range(3 + g):
        _wasserfall(w, oben, cx, cz, y_u)
    rng = w.rng
    for (x, z), y in list(oben.items()):
        if math.hypot(x - cx, z - cz) < R * 0.25 and rng.random() < 0.9:
            w.setze(x, y, z, w.b("water", level=0))
    _dschungel(w, oben, seed, 0.5, g)
    haengend(w, tr, "cave", 0.04, 6)
    return w


def tempelberg(seed, g=1):
    """Tempelberg: auf dem geebneten Gipfel steht ein offener Säulentempel mit goldener Kuppel, Kerzen und
    Weihrauchschalen, ringsum Zypressen."""
    fels = ["deepslate", "tuff", "andesite", "smooth_sandstone", "calcite"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels)
    r = 3 + (g > 1)
    y = gipfelplatz(w, oben, cx, cz, r + 2)
    cx, cz = round(cx), round(cz)
    for x in range(cx - r - 1, cx + r + 2):
        for z in range(cz - r - 1, cz + r + 2):
            w.setze(x, y, z, w.b("smooth_quartz" if (x + z) % 2 else "chiseled_quartz_block"))
    for dx in (-r, 0, r):
        for dz in (-r, 0, r):
            if dx or dz:
                for yy in range(y + 1, y + 5):
                    w.setze(cx + dx, yy, cz + dz, w.b("quartz_pillar", axis="y"))
    for x in range(cx - r - 1, cx + r + 2):
        for z in range(cz - r - 1, cz + r + 2):
            w.setze(x, y + 5, z, w.b("smooth_quartz"))
    for x in range(-r, r + 1):
        for k in range(0, r + 1):
            for z in range(-r, r + 1):
                dd = math.sqrt(x * x + (k * 1.2) ** 2 + z * z)
                if r - 1 < dd <= r:
                    w.setze(cx + x, y + 6 + k, cz + z, w.b("gold_block"))
    w.setze(cx, y + 1, cz, w.b("enchanting_table"))
    for (dx, dz) in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
        w.setze(cx + dx, y + 1, cz + dz, w.b("candle", candles=4, lit=True, waterlogged=False))
    baeume(w, oben, 2 + g, lambda s: wald2.fichte(s, schmal=0.5), abstand=4)
    kleinkram(w, oben, 0.3)
    begleiter(w, 1 + g, g, fels)
    return w


def burgberg(seed, g=1):
    """Burgberg: auf dem Gipfel thront eine kleine Burg mit Ringmauer, Zinnen, vier Ecktürmen mit Helmen und einem
    Bergfried, Fahnen wehen über den Wolken."""
    fels = ["deepslate", "cobbled_deepslate", "andesite", "stone", "calcite"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels, rf=1.1)
    a = max(3, int(RG[g] * 0.5))
    y = gipfelplatz(w, oben, cx, cz, a + 2) + 1
    cx, cz = round(cx), round(cz)
    st = Mix(w, [("stone_bricks", 3), ("cobblestone", 1), ("mossy_stone_bricks", 1)])
    for x in range(cx - a, cx + a + 1):
        for z in range(cz - a, cz + a + 1):
            if abs(x - cx) == a or abs(z - cz) == a:
                for yy in range(y - 2, y + 3 + g):
                    w.setze(x, yy, z, st(x, yy, z))
                if (x + z) % 2 == 0:
                    w.setze(x, y + 3 + g, z, st(x, y, z))
    dm = Dachmat(w, ["deepslate_tile", "cobbled_deepslate"])
    for (dx, dz) in ((-a, -a), (a, -a), (-a, a), (a, a)):
        eckturm(w, cx + dx, cz + dz, y, 1, 6 + g * 2, st, dm, form="kegel")
    eckturm(w, cx, cz, y, 2, 9 + g * 3, st, dm, form="glocke")
    w.setze(cx, y + 9 + g * 3 + 7, cz, w.b("red_wool"), False)
    for yy in (y, y + 1):
        w.bloecke.pop((cx, yy, cz + a), None)
    haengend(w, tr, "cave", 0.03, 5)
    begleiter(w, 1 + g, g, fels)
    return w


def klosterberg(seed, g=1):
    """Klosterberg: ein Bergkloster mit Kirche, Glockenturm und Zellenhaus klammert sich an den Gipfel, Gärten auf
    den Simsen, Gebetsfahnen zwischen den Dächern."""
    fels = ["deepslate", "tuff", "andesite", "stone", "calcite"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels, rf=1.15)
    y = gipfelplatz(w, oben, cx, cz, RG[g] * 0.6) + 1
    cx, cz = round(cx), round(cz)
    haus(w, cx - 2, cz, 7, 6, y, "stein", geschosse=1 + (g > 0), tuer_s="south")
    if g >= 1:
        haus(w, cx + 4, cz - 3, 5, 5, y, "fachwerk", geschosse=2, tuer_s="east")
        eckturm(w, cx + 4, cz + 3, y, 1, 8 + g * 2, Mix(w, [("stone_bricks", 3), ("andesite", 1)]),
                Dachmat(w, ["mcw:red_terracotta", "red_nether_brick", "brick"]), form="nadel")
    farben = ["red_wool", "yellow_wool", "blue_wool", "white_wool", "lime_wool"]
    for k in range(8):
        w.setze(cx - 5 + k, y + 7, cz + 3, w.b(farben[k % 5]), False)
    kleinkram(w, oben, 0.4)
    baeume(w, oben, 1 + g, lambda s: wald2.fichte(s), abstand=4)
    haengend(w, tr, "cave", 0.03, 5)
    return w


def pilzberg(seed, g=1):
    """Pilzberg: ein Myzel-Gipfel, auf dem riesige rote und braune Pilze wachsen, kleine Pilze und Leuchtflechten
    überall, Pilzlampen unter den Hüten."""
    fels = ["deepslate", "tuff", "mud_bricks", "packed_mud", "calcite"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels, "mycelium", "moss_block")
    rng = w.rng
    pos = sorted(oben.items(), key=lambda kv: rng.random())
    n, gesetzt = 0, []
    for (x, z), y in pos:
        if n >= 2 + g * 2:
            break
        if any(math.hypot(x - a, z - b) < 6 for a, b in gesetzt):
            continue
        h = 4 + int(rng.random() * (3 + g * 2))
        r = 2 + int(rng.random() * (1 + g))
        rot = n % 2 == 0
        for k in range(1, h + 1):
            w.setze(x, y + k, z, w.b("mushroom_stem", up=False, down=False, north=True, south=True, east=True,
                                     west=True))
        for dx in range(-r - 1, r + 2):
            for dz in range(-r - 1, r + 2):
                d = math.hypot(dx, dz)
                if d <= r + 0.5:
                    dy = 1 if d < r - 0.8 else 0
                    w.setze(x + dx, y + h + dy, z + dz, w.b("red_mushroom_block" if rot else "brown_mushroom_block",
                                                            up=True, down=False, north=True, south=True, east=True,
                                                            west=True))
                    if rot and dy == 0 and d > r - 0.3:
                        w.setze(x + dx, y + h - 1, z + dz, w.b("red_mushroom_block", up=True, down=False, north=True,
                                                               south=True, east=True, west=True))
        w.setze(x + 1, y + h - 1, z, w.b("shroomlight"))
        gesetzt.append((x, z))
        n += 1
    streuen(w, oben, 0.12, lambda x, y, z: w.setze(x, y + 1, z, w.b("red_mushroom" if rng.random() < 0.5 else
                                                                   "brown_mushroom")))
    haengend(w, tr, "cave", 0.04, 5)
    return w


def lavaberg(seed, g=1):
    """Lavaberg: ein schwarzer Schwebeberg aus Schwarzstein und Basalt mit glühenden Magmaadern, aus dem Gipfel
    quillt Lava und fällt in feurigen Strömen über die Kanten."""
    fels = ["blackstone", "basalt", "magma_block", "smooth_basalt", "polished_blackstone"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels, "blackstone", "magma_block")
    rng = w.rng
    for k in range(2 + g):
        a = rng.random() * 6.283
        rand = max(oben, key=lambda p: (p[0] - cx) * math.cos(a) + (p[1] - cz) * math.sin(a))
        x, z = rand
        y = oben[rand]
        nx, nz = x + round(math.cos(a)), z + round(math.sin(a))
        for yy in range(y_u, y + 1):
            if w.frei(nx, yy, nz):
                w.setze(nx, yy, nz, w.b("lava", level=0))
    for (x, z), y in list(oben.items()):
        if math.hypot(x - cx, z - cz) < RG[g] * 0.2:
            w.setze(x, y, z, w.b("lava", level=0))
    haengend(w, tr, "pointed_dripstone", 0.0, 1)
    begleiter(w, 1 + g, g, fels, "blackstone", "magma_block")
    return w


def endberg(seed, g=1):
    """End-Berg: ein bleicher Schwebeberg aus Endstein mit Purpur-Adern, auf dem Chorusgewächse wuchern und
    Endstäbe leuchten, umkreist von Obsidianbrocken."""
    fels = ["obsidian", "end_stone_bricks", "end_stone", "purpur_block", "end_stone"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels, "end_stone", "end_stone_bricks")
    rng = w.rng

    def chorus(x, y, z):
        h = 2 + int(rng.random() * (2 + g))
        for k in range(1, h + 1):
            w.setze(x, y + k, z, w.b("chorus_plant", up=k < h, down=True, north=False, south=False, east=False,
                                     west=False))
        w.setze(x, y + h + 1, z, w.b("chorus_flower", age=5))
    streuen(w, oben, 0.04, chorus)
    streuen(w, oben, 0.01, lambda x, y, z: w.setze(x, y + 1, z, w.b("end_rod", facing="up")))
    begleiter(w, 2 + g, g, ["obsidian", "crying_obsidian", "obsidian", "end_stone", "obsidian"], "obsidian",
              "crying_obsidian")
    return w


def netherberg(seed, g=1):
    """Nether-Berg: ein roter Schwebeberg aus Netherrack mit Netherziegel-Bändern, oben Karmesinwald mit
    Riesenpilzen, darunter hängen Trauerranken bis tief hinab."""
    fels = ["blackstone", "netherrack", "nether_bricks", "netherrack", "red_nether_bricks"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels, "crimson_nylium", "nether_wart_block")
    rng = w.rng
    pos = sorted(oben.items(), key=lambda kv: rng.random())
    n = 0
    for (x, z), y in pos:
        if n >= 2 + g * 2:
            break
        if not all(w.frei(x, y + h, z) for h in (1, 4, 7)):
            continue
        h = 5 + int(rng.random() * (3 + g))
        for k in range(1, h + 1):
            w.setze(x, y + k, z, w.b("crimson_stem", axis="y"))
        r = 2 + int(rng.random() * 2)
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                for dy in range(0, 3):
                    if dx * dx + dz * dz + dy * dy * 2 <= r * r + 1:
                        w.setze(x + dx, y + h - 1 + dy, z + dz, w.b("shroomlight" if rng.random() < 0.08 else
                                                                    "nether_wart_block"), False)
        n += 1
    streuen(w, oben, 0.2, lambda x, y, z: w.setze(x, y + 1, z, w.b("crimson_roots" if rng.random() < 0.7 else
                                                                  "crimson_fungus")))
    haengend(w, tr, "weeping", 0.06, 6 + g * 3)
    return w


def basaltberg(seed, g=1):
    """Basaltberg: ein Schwebeberg aus senkrechten Basaltsäulen in Grautönen, oben Moos und Farn, aus den Flanken
    ragen Säulenstümpfe."""
    fels = ["basalt", "polished_basalt", "smooth_basalt", "tuff", "polished_basalt"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels, "moss_block", "moss_block")
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if n in ("minecraft:basalt", "minecraft:polished_basalt"):
            w.bloecke[(x, y, z)] = w.b(n.split(":")[1], axis="y")
    rng = w.rng
    for (x, z), y in list(oben.items()):
        if rng.random() < 0.05:
            for k in range(1, 2 + int(rng.random() * 3)):
                w.setze(x, y + k, z, w.b("basalt", axis="y"))
        elif rng.random() < 0.2 and w.frei(x, y + 1, z):
            w.setze(x, y + 1, z, w.b("fern" if rng.random() < 0.5 else "moss_carpet"))
    haengend(w, tr, "cave", 0.03, 4)
    begleiter(w, 2 + g, g, fels, "moss_block", "moss_block")
    return w


def moosberg(seed, g=1):
    """Moosberg: ein dicht bewachsener Berg mit dunklen Eichen, Moospolstern, Azaleen und langen, leuchtenden
    Beerenranken an der Unterseite."""
    fels = ["deepslate", "tuff", "mossy_cobblestone", "moss_block", "mossy_stone_bricks"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels, "moss_block", "moss_block")
    baeume(w, oben, 3 + g * 2, lambda s: wald2.laubbaum(s, "dark_oak", H=6 + g), abstand=5)
    rng = w.rng
    streuen(w, oben, 0.3, lambda x, y, z: w.setze(x, y + 1, z, w.b(["moss_carpet", "azalea", "flowering_azalea",
                                                                   "fern"][int(rng.random() * 4)])))
    haengend(w, tr, "cave", 0.09, 8 + g * 4)
    _lianen(w, tr, 0.03, 8 + g * 4, 2)
    return w


def ringberg(seed, g=1):
    """Ringberg: ein mächtiger Schwebeberg, durch den ein riesiges rundes Felsentor führt – man kann mitten
    hindurchfliegen, Lianen hängen in die Öffnung."""
    fels = ["deepslate", "tuff", "andesite", "stone", "calcite"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels, rf=1.25)
    yc = y_u + H * 0.6
    rr = R * 0.45
    for (x, y, z) in list(w.bloecke):
        if (y - yc) ** 2 + (z - cz) ** 2 < rr * rr:
            del w.bloecke[(x, y, z)]
    _dschungel(w, oben, seed, 0.8, g)
    _lianen(w, tr, 0.05, 6 + g * 3, 2)
    return w


def nadelkranz(seed, g=1):
    """Nadelkranz: ein Ring aus sechs schlanken, unterschiedlich hohen Felsnadeln schwebt um eine Mittelnadel,
    jede trägt einen kleinen grünen Schopf, Hängebrücken verbinden einige."""
    fels = ["deepslate", "tuff", "andesite", "stone", "calcite"]
    w, o0, k0, tr = berg(seed, g, fels, rf=0.45, hf=1.0)
    rng = w.rng
    n = 6
    D = RG[g] * 1.4
    spitzen = []
    for k in range(n):
        a = k / n * 6.283
        _, o, kk, _ = berg(seed + k, g, fels, cx=math.cos(a) * D, cz=math.sin(a) * D, rf=0.3 + rng.random() * 0.12,
                           hf=0.5 + rng.random() * 0.35, y_u=LG[g] + HG[g] * rng.random() * 0.3, w=w)
        _dschungel(w, o, seed + k, 0.6, 0)
    _dschungel(w, o0, seed, 0.6, g)
    _lianen(w, tr, 0.04, 6 + g * 3, 2)
    return w


def kettenberg(seed, g=1):
    """Kettenberg: ein schwebender Berg, an vier riesigen Eisenketten gefesselt, die zu Steinankern am Boden führen –
    als hätte man ihn eingefangen."""
    fels = ["deepslate", "tuff", "andesite", "stone", "calcite"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels)
    _dschungel(w, oben, seed, 0.6, g)
    for k in range(4):
        a = k * 1.571 + 0.785
        sx, sy, sz = cx + math.cos(a) * R * 0.7, y_u + H * 0.35, cz + math.sin(a) * R * 0.7
        ex, ez = cx + math.cos(a) * (R * 1.8 + 4), cz + math.sin(a) * (R * 1.8 + 4)
        n = int(math.dist((sx, sy, sz), (ex, 1, ez)) * 1.5)
        for i in range(n + 1):
            t = i / n
            x, y, z = sx + (ex - sx) * t, sy + (1 - sy) * t - 3 * math.sin(math.pi * t), sz + (ez - sz) * t
            w.setze(round(x), round(y), round(z), w.b("chain", axis="y", waterlogged=False) if i % 2 else
                    w.b("iron_block") if i % 6 == 0 else w.b("chain", axis="x" if abs(math.cos(a)) > 0.7 else "z",
                                                                waterlogged=False), False)
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                for y in range(0, 3):
                    w.setze(round(ex) + dx, y, round(ez) + dz, w.b("polished_blackstone_bricks" if y < 2 else
                                                                   "chiseled_polished_blackstone"))
    _lianen(w, tr, 0.03, 6, 2)
    return w


def weltenbaumberg(seed, g=1):
    """Weltenbaum-Berg: auf einem Schwebeberg wächst ein gewaltiger Baum, dessen Wurzeln den ganzen Berg umklammern
    und lang aus der Unterseite hängen."""
    fels = ["deepslate", "tuff", "andesite", "stone", "calcite"]
    w, oben, (cx, cz, y_u, H, R), tr = berg(seed, g, fels, hf=0.7)
    x, y, z = gipfel(oben)
    y = gipfelplatz(w, oben, x, z, 3)
    einfuegen(w, wald2.laubbaum(seed, "oak", H=14 + g * 6, dick=True), x, y, z)
    rng = w.rng
    for k in range(6 + g * 2):
        a = k / (6 + g * 2) * 6.283
        pts = []
        px, py, pz = x, y, z
        for i in range(int(H * 1.3)):
            t = i / (H * 1.3)
            rr = R * (0.9 + 0.3 * math.sin(t * 3)) * min(1, t * 4)
            px = cx + math.cos(a + t * 0.8) * rr * (1 - t * 0.6)
            pz = cz + math.sin(a + t * 0.8) * rr * (1 - t * 0.6)
            py = y - t * (H * 1.25)
            w.setze(round(px), round(py), round(pz), w.b("oak_wood", axis="y"), False)
            if i % 3 == 0:
                w.setze(round(px) + 1, round(py), round(pz), w.b("oak_wood", axis="y"), False)
        for kk in range(int(4 + rng.random() * 8)):
            if w.frei(round(px), round(py) - kk - 1, round(pz)):
                w.setze(round(px), round(py) - kk - 1, round(pz), w.b("hanging_roots", waterlogged=False) if kk > 2
                        else w.b("mangrove_roots", waterlogged=False))
    kleinkram(w, oben, 0.4)
    return w


SCHWEBEBERGE2 = {
    "kristallberg": ("Kristallberg", kristallberg),
    "schneegipfel": ("Schneegipfel", schneegipfel),
    "tafelberg": ("Schwebender Tafelberg", tafelberg),
    "kirschberg": ("Kirschblütenberg", kirschberg),
    "herbstberg": ("Herbstberg", herbstberg),
    "zwillingsberge": ("Zwillingsberge mit Hängebrücke", zwillingsberge),
    "wasserfallberg": ("Wasserfallberg", wasserfallberg),
    "tempelberg": ("Tempelberg", tempelberg),
    "burgberg": ("Burgberg", burgberg),
    "klosterberg": ("Klosterberg", klosterberg),
    "pilzberg": ("Pilzberg", pilzberg),
    "lavaberg": ("Lavaberg", lavaberg),
    "endberg": ("End-Berg", endberg),
    "netherberg": ("Nether-Berg", netherberg),
    "basaltberg": ("Basaltberg", basaltberg),
    "moosberg": ("Moosberg", moosberg),
    "ringberg": ("Ringberg", ringberg),
    "nadelkranz": ("Nadelkranz", nadelkranz),
    "kettenberg": ("Kettenberg", kettenberg),
    "weltenbaumberg": ("Weltenbaum-Berg", weltenbaumberg),
}

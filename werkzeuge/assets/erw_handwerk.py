"""Mühlen & Handwerk II – zwanzig weitere Werkstätten: Seilerei, Fassbinderei, Göpel-Ölmühle, Papiermühle,
Korbflechterei, Drechslerei, Walkmühle, Salzsiederei, Kalkofen, Teerschwelerei, Glockengießerei, Wagnerei,
Leinenweberei, Steinbruch mit Tretkran, Kelterei, Zimmerplatz, Seifensiederei, Schindelmacherei, Hopfengarten mit
Darre und Kerzenmanufaktur."""

from __future__ import annotations

import math

from erw_basis import M, S, baumrand, figur, haus, hoehe, wiese
from feinbau import Dachmat, fachwerk, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen
from skulptur import ell, kap, kasten, kegel, kreisrand


def fw(w):
    return M(w, [("white_terracotta", 3), ("calcite", 2), ("smooth_sandstone", 1)])


def bretter(w, holz="spruce"):
    return M(w, [(f"{holz}_planks", 3), (f"stripped_{holz}_log", 1)])


def bruch(w):
    return M(w, [("cobblestone", 3), ("mossy_cobblestone", 1), ("stone", 1)])


def bach(w, zellen, R, x_off=0, breite=2.0, achse="z"):
    for a in range(-R - 2, R + 3):
        for d in range(-int(breite) - 1, int(breite) + 2):
            if achse == "z":
                x, z = d + x_off + round(math.sin(a / 5) * 1.5), a
            else:
                x, z = a, d + x_off + round(math.sin(a / 5) * 1.5)
            if (x, z) in zellen and abs(d) <= breite:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel"))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
                zellen[(x, z)] = -1


def wasserrad(w, cx, cz, yc, r, achse="x", holz="spruce"):
    for k in range(int(r * 8)):
        a = k / (r * 8) * 2 * math.pi
        for d in (-1, 1):
            p = (cx + d, yc + round(math.sin(a) * r), cz + round(math.cos(a) * r)) if achse == "x" else \
                (cx + round(math.cos(a) * r), yc + round(math.sin(a) * r), cz + d)
            w.setze(*p, w.b(f"{holz}_planks"))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        for k in range(int(r) + 1):
            p = (cx, yc + round(math.sin(a) * k), cz + round(math.cos(a) * k)) if achse == "x" else \
                (cx + round(math.cos(a) * k), yc + round(math.sin(a) * k), cz)
            w.setze(*p, w.b(f"{holz}_log", axis="y"), False)
        p = (cx, yc + round(math.sin(a) * (r + 1)), cz + round(math.cos(a) * (r + 1))) if achse == "x" else \
            (cx + round(math.cos(a) * (r + 1)), yc + round(math.sin(a) * (r + 1)), cz)
        w.setze(*p, w.b(f"{holz}_slab", type="bottom", waterlogged=False), False)


# ============================================================================ Bauten

def seilerei(seed, g=1):
    """Seilerei: eine lange, schmale Reeperbahn unter einem Pultdach auf Pfosten, Seilstränge zwischen Drehrad
    und Schlitten, aufgerollte Taue, Hanfballen und das Haus des Seilermeisters am Kopfende."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.05)
    L = int(R * 0.8)
    for x in range(-L, L + 1):
        for z in (-2, -1, 0, 1, 2):
            w.setze(x, 0, z, w.b("dirt_path"))
        if x % 4 == 0:
            for z in (-2, 2):
                for y in range(1, 4 + (z > 0)):
                    w.setze(x, y, z, w.b("spruce_fence"))
        for z in range(-3, 4):
            w.setze(x, 4 + (z > 0) if z != 0 else 4, z, w.b("spruce_slab", type="bottom", waterlogged=False))
        for z in (-1, 1):
            w.setze(x, 2, z, w.b("tripwire", attached=False, disarmed=False, east=True, west=True, north=False,
                                 south=False, powered=False))
    for z in (-1, 1):
        w.setze(-L + 1, 2, z, w.b("tripwire_hook", facing="east", attached=True, powered=False))
    for dy in range(-1, 2):
        for dz in range(-1, 2):
            if abs(dy) + abs(dz) == 1:
                w.setze(-L, 2 + dy, dz, w.b("spruce_planks"))
    w.setze(-L, 2, 0, w.b("spruce_log", axis="x"))
    haus(w, L + 4, 0, 5, int(2 * s + 5) | 1, 1, fw(w), holz="dark_oak", H=4, tuer_s="west")
    for k in range(3 + g):
        w.setze(-L + 2 + k * 2, 1, 3, w.b("hay_block", axis="x"))
    for k in range(3):
        w.setze(L - 2 - k, 1, -3, w.b("brown_wool"))
    baumrand(w, zellen, R, 3 + g, seed, innen=0.9)
    return w


def fassbinderei(seed, g=1):
    """Fassbinderei: eine Werkstatt mit offener Front, darin halbfertige Fässer und Dauben, davor ein Feuerkorb
    zum Biegen der Dauben, ein Hof voller gestapelter Fässer und Eisenreifen an der Wand."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    zellen = wiese(w, R, 0.05)
    B, T = int(4 * s + 5) | 1, int(2 * s + 5) | 1
    haus(w, 0, -int(R * 0.3), B, T, 1, bretter(w), holz="spruce", H=4, tuer_s="south")
    z1 = -int(R * 0.3) + T // 2
    for x in range(-B // 2 + 1, B // 2):
        for y in (1, 2):
            w.setze(x, y, z1, w.b("air"))
    for k in range(int(6 * s + 4)):
        x = -int(R * 0.5) + (k % 5) * 2
        z = int(R * 0.2) + (k // 5) * 2
        for y in range(1, 1 + 1 + (k % 3 == 0)):
            w.setze(x, y, z, w.b("barrel", facing="up" if y == 1 else "east", open=False))
    w.setze(int(R * 0.4), 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for k in range(4):
        w.setze(int(R * 0.4) + 1, 1 + k // 2, 1 + k % 2, w.b("stripped_spruce_log", axis="y"))
    for x in range(-B // 2 + 1, B // 2, 2):
        w.setze(x, 3, z1 + 1, w.b("chain", axis="x", waterlogged=False))
    baumrand(w, zellen, R, 2 + g, seed, innen=0.88)
    return w


def rossmuehle(seed, g=1):
    """Göpel-Ölmühle: ein achteckiges Mühlenhaus mit Zeltdach, davor ein Göpel – ein Pferd zieht im Kreis einen
    Balken, der über Zahnräder den Kollergang mit dem großen Mühlstein antreibt; Ölfässer und Saatsäcke."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.05)
    hz = -int(R * 0.35)
    r = 2.5 * s + 2.5
    for y in range(1, 5):
        for x, z in kreisrand(r, 0, hz):
            w.setze(x, y, z, fw(w)(x, y, z) if y > 1 else w.b("cobblestone"))
    kegeldach(w, 0, hz, 5, int(r), Dachmat(w, ["spruce", "dark_oak"]), form="kegel", eckig=True,
              spitze="spruce_fence")
    for y in (1, 2):
        w.bloecke.pop((0, y, hz + round(r)), None)
    gz = int(R * 0.25)
    rg = 4 * s + 3
    for x, z in kreisrand(rg, 0, gz):
        w.setze(x, 0, z, w.b("dirt_path"))
    for y in range(1, 4):
        w.setze(0, y, gz, w.b("spruce_log", axis="y"))
    for k in range(int(rg)):
        w.setze(k, 3, gz, w.b("spruce_log", axis="x"))
    kugel(w, -2, 1.5, gz, 1.4, w.b("smooth_stone"), ry=1.4)
    br = w.b("brown_terracotta")
    teile = [(ell(0, 3.4, 0, 2.0, 1.1, 0.9), br), (kap((1.6, 3.8, 0), (2.6, 5.4, 0), 0.6, 0.5), br),
             (ell(3.0, 5.4, 0, 0.9, 0.5, 0.45), br), (kap((-2.0, 3.8, 0), (-2.6, 2.2, 0), 0.3, 0.2), w.b("black_wool"))] + \
            [(kap((sx, 3.0, sz), (sx, 0, sz), 0.3), br) for sx in (-1.3, 1.3) for sz in (-0.45, 0.45)]
    figur(w, 0.5 * s + 0.35, teile, (-3, -1, -2), (4, 7, 2), pos=(round(rg) - 1, 1, gz + 1), winkel=-math.pi / 2)
    for k in range(4):
        w.setze(int(R * 0.45), 1 + k // 2, -1 + k % 2, w.b("barrel", facing="up", open=False))
    baumrand(w, zellen, R, 2 + g, seed, innen=0.88)
    return w


def papiermuehle(seed, g=2):
    """Papiermühle: ein hohes Fachwerkhaus am Bach mit großem Wasserrad, Stampfwerk-Hämmern unter einem Vordach,
    Trockenböden mit Lüftungsklappen unter dem Dach und Bütten mit Papierbrei."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.05)
    bach(w, zellen, R, x_off=int(R * 0.35))
    B, T = int(4 * s + 5) | 1, int(5 * s + 6) | 1
    hx = int(R * 0.35) - int(2 + 1.4 * s) - B // 2 - 1
    top = haus(w, hx, 0, B, T, 1, fw(w), holz="dark_oak", H=int(3 * s + 5), tuer_s="west", steil=2)
    for y in range(4, int(3 * s + 5)):
        for z in range(-T // 2 + 1, T // 2, 2):
            w.setze(hx - B // 2, y, z, w.b("dark_oak_trapdoor", facing="west", half="bottom", open=True,
                                           powered=False, waterlogged=False), True)
    wasserrad(w, int(R * 0.35), 0, int(2 * s + 2), 2 * s + 2, achse="x")
    for k in range(3):
        x = hx - B // 2 - 2
        z = -2 + k * 2
        w.setze(x, 1, z, w.b("water_cauldron", level=3))
    for k in range(2):
        w.setze(hx - B // 2 - 4, 3, -1 + k * 2, w.b("spruce_log", axis="x"))
        w.setze(hx - B // 2 - 4, 2, -1 + k * 2, w.b("anvil", facing="north"))
    _ = top
    baumrand(w, zellen, R, 3 + g, seed, innen=0.88)
    return w


def korbflechterei(seed, g=1):
    """Korbflechterei: eine Hütte mit Schilfdach am Weidenufer, Bündel geschnittener Weidenruten in Wasser-
    becken, Stapel fertiger Körbe (Komposter) und eine Kopfweiden-Reihe."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.05)
    bach(w, zellen, R, x_off=-int(R * 0.45), achse="z")
    haus(w, int(R * 0.15), -int(R * 0.2), int(3 * s + 5) | 1, int(2 * s + 5) | 1, 1, bretter(w, "oak"), holz="oak",
         H=3, dach=("mcw:thatch", "oak"), tuer_s="south")
    for k in range(int(4 * s + 3)):
        x, z = int(R * 0.15) - 3 + k, int(R * 0.25)
        w.setze(x, 1, z, w.b("composter", level=k % 4))
        if k % 2:
            w.setze(x, 2, z, w.b("composter", level=0))
    for k in range(3 + g):
        x = -int(R * 0.25)
        z = -int(R * 0.6) + k * 4
        for y in range(1, 4):
            w.setze(x, y, z, w.b("oak_log", axis="y"))
        kugel(w, x, 4.5, z, 1.6 + 0.4 * s, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
    for k in range(3):
        w.setze(-int(R * 0.45) + 2, 1, k * 2 - 2, w.b("bamboo_block", axis="y"))
    baumrand(w, zellen, R, 2 + g, seed, innen=0.9)
    return w


def drechslerei(seed, g=1):
    """Drechslerei: eine Werkstatt mit Wippdrehbank unter einem Vordach, Holzschalen, Spindeln und Stuhlbeinen
    auf Regalen, ein Haufen Späne und Rundhölzer zum Trocknen."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    zellen = wiese(w, R, 0.05)
    B, T = int(3 * s + 5) | 1, int(2 * s + 5) | 1
    haus(w, 0, -int(R * 0.25), B, T, 1, fw(w), holz="oak", H=4, tuer_s="south")
    z1 = -int(R * 0.25) + T // 2
    for x in range(-B // 2, B // 2 + 1):
        for z in range(z1 + 1, z1 + 4):
            w.setze(x, 4, z, w.b("oak_slab", type="bottom", waterlogged=False))
    for x in (-B // 2, B // 2):
        for y in range(1, 4):
            w.setze(x, y, z1 + 3, w.b("oak_fence"))
    w.setze(-1, 1, z1 + 2, w.b("oak_log", axis="x"))
    w.setze(0, 1, z1 + 2, w.b("oak_fence"))
    w.setze(1, 1, z1 + 2, w.b("oak_log", axis="x"))
    w.setze(0, 3, z1 + 2, w.b("chain", axis="y", waterlogged=False))
    for x in range(-B // 2 + 1, B // 2):
        w.setze(x, 2, z1 + 1, w.b("flower_pot") if x % 2 else w.b("oak_trapdoor", facing="south", half="top",
                                                                      open=False, powered=False, waterlogged=False))
    for k in range(3 + g):
        w.setze(B // 2 + 2, 1 + k // 3, -1 + k % 3, w.b("stripped_oak_log", axis="z"))
    w.setze(-B // 2 - 2, 1, z1 + 2, w.b("brown_carpet"))
    w.setze(-B // 2 - 3, 1, z1 + 2, w.b("brown_carpet"))
    baumrand(w, zellen, R, 2 + g, seed, innen=0.88)
    return w


def walkmuehle(seed, g=2):
    """Walkmühle: ein Steinhaus am Fluss mit unterschlächtigem Wasserrad, Walkhämmern und Holztrögen; draußen
    Spannrahmen (Tuchrahmen), auf denen nasses Wolltuch in Bahnen trocknet."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.05)
    bach(w, zellen, R, x_off=int(R * 0.4), breite=2.5)
    B, T = int(4 * s + 5) | 1, int(4 * s + 5) | 1
    hx = int(R * 0.4) - int(2 + 1.4 * s) - B // 2 - 2
    haus(w, hx, 0, B, T, 1, bruch(w), holz="spruce", H=4, tuer_s="west", fenster=True)
    wasserrad(w, int(R * 0.4), 0, int(1.5 * s + 1), 1.6 * s + 2, achse="x")
    for k in range(2 + g):
        z0 = -int(R * 0.6) + k * 4
        x0 = -int(R * 0.6)
        for x in range(x0, x0 + int(5 * s + 4)):
            for y in (1, 3):
                w.setze(x, y, z0, w.b("spruce_fence"))
            w.setze(x, 2, z0, w.b(["white_wool", "light_blue_wool", "red_wool"][k % 3]))
        for x in (x0 - 1, x0 + int(5 * s + 4)):
            for y in range(1, 4):
                w.setze(x, y, z0, w.b("spruce_log", axis="y"))
    baumrand(w, zellen, R, 2 + g, seed, innen=0.9)
    return w


def salzsiederei(seed, g=2):
    """Salzsiederei: ein Siedehaus mit großen Pfannen über Feuerstellen, hoher Dampfschlot, ein Gradierwerk aus
    Reisigwänden, über die Sole rieselt, und Salzhaufen in einer Lagerhalle."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.05)
    B, T = int(4 * s + 6) | 1, int(3 * s + 5) | 1
    hx, hz = -int(R * 0.3), -int(R * 0.3)
    top = haus(w, hx, hz, B, T, 1, bruch(w), holz="spruce", H=4, tuer_s="south", schorn=False)
    for x in range(hx - B // 2 + 1, hx + B // 2):
        for z in range(hz - T // 2 + 1, hz + T // 2):
            if (x + z) % 3 == 0:
                w.setze(x, 1, z, w.b("magma_block"))
    for y in range(1, top + int(4 * s + 3)):
        for dx in (0, 1):
            for dz in (0, 1):
                w.setze(hx + B // 2 - 1 + dx, y, hz + dz, w.b("bricks"))
    w.setze(hx + B // 2 - 1, top + int(4 * s + 3), hz, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                           waterlogged=False))
    L = int(R * 0.7)
    gz = int(R * 0.35)
    H = int(4 * s + 4)
    for x in range(-L, L + 1):
        for y in range(1, H + 1):
            w.setze(x, y, gz, w.b("dark_oak_leaves", persistent=True, distance=1, waterlogged=False) if y < H else
                    w.b("spruce_planks"))
        if x % 4 == 0:
            for y in range(1, H + 1):
                for dz in (-1, 1):
                    w.setze(x, y, gz + dz, w.b("spruce_log", axis="y"))
        w.setze(x, H + 1, gz, w.b("water", level=0) if x % 2 else w.b("spruce_planks"))
    for k in range(3):
        kugel(w, int(R * 0.4) + k * 2, 0.5, -int(R * 0.4), 1.3 + 0.3 * s, w.b("white_concrete_powder"), ry=1.2)
    baumrand(w, zellen, R, 2 + g, seed, innen=0.9)
    return w


def kalkofen(seed, g=1):
    """Kalkofen: ein gedrungener Schachtofen aus Bruchstein mit Rampe zur Beschickung oben, Feueröffnung unten,
    Kalkstein-Haufen, gebrannte Kalkfässer und eine Löschgrube mit weißem Kalkbrei."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    zellen = wiese(w, R, 0.1)
    r = 2.5 * s + 2.5
    H = int(5 * s + 5)
    st = bruch(w)
    for y in range(1, H + 1):
        rr = r * (1 - 0.2 * y / H)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(x, z)
                if d <= rr:
                    w.setze(x, y, z, st(x, y, z) if d > rr - 1.5 or y < 2 else w.b("magma_block") if y < H else
                            w.b("calcite"))
    for y in (1, 2):
        w.setze(0, y, round(r), w.b("air"))
    w.setze(0, 1, round(r) - 1, w.b("campfire", lit=True, signal_fire=False, facing="south", waterlogged=False))
    for k in range(H):
        for x in (-1, 0, 1):
            w.setze(x, 1 + k, -round(r) - H + k, w.b("cobblestone"))
            if k == H - 1:
                pass
    for k in range(2 + g):
        kugel(w, int(R * 0.45), 0.5, -2 + k * 3, 1.2 + 0.3 * s, w.b("diorite"), ry=1.0)
    for x in range(-int(R * 0.5), -int(R * 0.5) + 4):
        for z in range(2, 5):
            w.setze(x, 0, z, w.b("white_concrete_powder"))
    for k in range(3):
        w.setze(-int(R * 0.5) + k, 1, -1, w.b("barrel", facing="up", open=False))
    baumrand(w, zellen, R, 2 + g, seed, innen=0.88)
    return w


def teerschwelerei(seed, g=1):
    """Teerschwelerei: im Kiefernwald ein qualmender Teerofen aus Lehm, Auffangrinnen, Teerfässer und ein Holz-
    lager aus harzigen Kiefernstümpfen; eine rußgeschwärzte Köhlerhütte daneben."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.2, art="wald")
    kugel(w, 0, 0, 0, 2.5 * s + 2.5, M(w, [("packed_mud", 2), ("mud_bricks", 1), ("coarse_dirt", 1)]), ry=2 * s + 2)
    w.setze(0, int(2 * s + 2), 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    for k in range(int(3 * s + 3)):
        w.setze(int(2.5 * s + 3) + k, 0, 0, w.b("black_concrete"))
    for k in range(3 + g):
        w.setze(int(2.5 * s + 4) + k % 2, 1 + k // 2, 2, w.b("barrel", facing="up", open=False))
    for k in range(5):
        w.setze(-int(R * 0.4) + k, 1, -int(R * 0.3), w.b("spruce_log", axis="x"))
        w.setze(-int(R * 0.4) + k, 2, -int(R * 0.3), w.b("spruce_log", axis="x") if k % 2 else w.b("air"))
    hx, hz = -int(R * 0.35), int(R * 0.35)
    for x in range(hx - 2, hx + 3):
        for z in range(hz - 2, hz + 3):
            for y in range(1, 3):
                if abs(x - hx) == 2 or abs(z - hz) == 2:
                    w.setze(x, y, z, w.b("dark_oak_log", axis="y"))
    for k in range(4):
        for x in range(hx - 3 + k, hx + 4 - k):
            for z in range(hz - 3, hz + 4):
                if x in (hx - 3 + k, hx + 3 - k):
                    w.setze(x, 3 + k, z, w.b("dark_oak_planks"))
    baumrand(w, zellen, R, 5 + 2 * g, seed, innen=0.7, art="fichte")
    return w


def glockengiesserei(seed, g=2):
    """Glockengießerei: eine hohe Halle mit offenem Tor, eine Gießgrube mit halb ausgegrabener Glocke im Lehmmantel,
    ein Schmelzofen mit Kupferkessel, ein Kran und eine fertige Glocke im Probestuhl."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 5)
    zellen = wiese(w, R, 0.05)
    B, T = int(5 * s + 6) | 1, int(4 * s + 6) | 1
    haus(w, 0, -int(R * 0.15), B, T, 1, fw(w), holz="dark_oak", H=int(3 * s + 5), tuer_s="south", steil=1)
    z1 = -int(R * 0.15) + T // 2
    for x in (-1, 0, 1):
        for y in range(1, 5):
            w.bloecke.pop((x, y, z1), None)
    kugel(w, 0, 0, -int(R * 0.15), 1.5 * s + 1.2, w.b("waxed_cut_copper"), ry=2 * s + 1)
    for k in range(int(2 * s + 2)):
        w.setze(-B // 2 + 2, 1 + k, -int(R * 0.15) - T // 2 + 2, w.b("bricks"))
    w.setze(-B // 2 + 2, int(2 * s + 3), -int(R * 0.15) - T // 2 + 2, w.b("blast_furnace", facing="south", lit=True))
    gx = B // 2 + 4
    for y in range(1, 7):
        for dx in (-2, 2):
            w.setze(gx + dx, y, 4, w.b("dark_oak_log", axis="y"))
    for dx in range(-2, 3):
        w.setze(gx + dx, 7, 4, w.b("dark_oak_log", axis="x"))
    w.setze(gx, 6, 4, w.b("bell", attachment="ceiling", facing="north", powered=False))
    w.setze(gx, 5, 4, w.b("waxed_cut_copper"))
    w.setze(gx, 4, 4, w.b("waxed_cut_copper"))
    baumrand(w, zellen, R, 2 + g, seed, innen=0.9)
    return w


def wagnerei(seed, g=1):
    """Wagnerei: eine Werkstatt für Räder und Wagen – ein Speichenrad auf dem Richtbock, fertige Räder an der Wand,
    ein halb gebauter Leiterwagen, Felgenholz-Stapel und eine Esse für die Eisenreifen."""
    w = _neu(seed)
    s = S[g]
    R = int(8 * s + 5)
    zellen = wiese(w, R, 0.05)
    B, T = int(4 * s + 5) | 1, int(2 * s + 5) | 1
    haus(w, 0, -int(R * 0.3), B, T, 1, bretter(w, "oak"), holz="oak", H=4, tuer_s="south")
    z1 = -int(R * 0.3) + T // 2
    for k, x in enumerate((-B // 2 + 1, B // 2 - 1)):
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if (dx, dy) != (0, 0):
                    w.setze(x + dx, 3 + dy, z1 + 1, w.b("oak_planks") if abs(dx) + abs(dy) == 1 else w.b("oak_fence"))
        w.setze(x, 3, z1 + 1, w.b("oak_log", axis="z"))
    wx, wz = int(R * 0.15), int(R * 0.3)
    for x in range(wx - 2, wx + 3):
        for z in (wz - 1, wz, wz + 1):
            w.setze(x, 2, z, w.b("oak_planks") if z == wz else w.b("oak_fence"))
    for x in (wx - 2, wx + 2):
        for z in (wz - 2, wz + 2):
            for dy in (-1, 0, 1):
                w.setze(x + dy * 0, 2 + dy, z, w.b("oak_planks") if dy else w.b("oak_log", axis="z"))
    w.setze(wx + 3, 1, wz, w.b("oak_fence"))
    w.setze(wx + 4, 1, wz, w.b("oak_fence"))
    for k in range(4):
        w.setze(-int(R * 0.5), 1 + k // 2, k % 2, w.b("stripped_oak_log", axis="x"))
    w.setze(-int(R * 0.35), 1, int(R * 0.35), w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                  waterlogged=False))
    w.setze(-int(R * 0.35) + 1, 1, int(R * 0.35), w.b("anvil", facing="east"))
    baumrand(w, zellen, R, 2 + g, seed, innen=0.9)
    return w


def leinenweberei(seed, g=1):
    """Leinenweberei: ein Flachsfeld mit blauen Blüten, eine Rösteteich-Grube, Bündel auf Trockengestellen, eine
    Brechel und ein Weberhaus mit großem Webstuhl hinter dem Fenster; weiße Leinenbahnen bleichen auf der Wiese."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.05)
    for x in range(-R, 0):
        for z in range(-R, -2):
            if (x, z) in zellen and math.hypot(x, z) < R - 1:
                w.setze(x, zellen[(x, z)], z, w.b("farmland", moisture=7))
                w.setze(x, zellen[(x, z)] + 1, z, w.b("cornflower") if (x + z) % 3 == 0 else w.b("wheat", age=5))
    for x in range(2, 2 + int(4 * s + 3)):
        for z in range(-int(R * 0.6), -int(R * 0.6) + 3):
            w.setze(x, 0, z, w.b("water", level=0))
    haus(w, int(R * 0.35), int(R * 0.05), int(3 * s + 5) | 1, int(2 * s + 5) | 1, 1, fw(w), holz="spruce", H=4,
         tuer_s="west")
    w.setze(int(R * 0.35), 1, int(R * 0.05), w.b("loom", facing="west"))
    for k in range(3 + g):
        x0, z0 = -int(R * 0.6) + k * 3, int(R * 0.45)
        for x in range(x0, x0 + 2):
            w.setze(x, zellen.get((x, z0), 0) + 1, z0, w.b("white_carpet"))
            w.setze(x, zellen.get((x, z0 + 1), 0) + 1, z0 + 1, w.b("white_carpet"))
    for k in range(3):
        w.setze(-2, 1 + k % 2, int(R * 0.15) + k, w.b("hay_block", axis="x"))
    baumrand(w, zellen, R, 2 + g, seed, innen=0.9)
    return w


def steinbruch(seed, g=2):
    """Steinbruch mit Tretkran: eine abgestufte Abbauwand aus hellem Stein, ein großer hölzerner Tretradkran hebt
    einen Quader, Rampen, behauene Blöcke, Keile und die Hütte des Steinmetzmeisters."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.05)
    st = M(w, [("stone", 3), ("diorite", 1), ("andesite", 1), ("calcite", 1)])
    for x in range(-R, R + 1):
        for z in range(-R, -int(R * 0.1)):
            if math.hypot(x, z) > R:
                continue
            stufe = int((-z - R * 0.1) / (2.5 * s + 1))
            h = min(4, stufe) * int(2 * s + 1) + 1
            for y in range(1, h + 1):
                w.setze(x, y, z, st(x, y, z))
    kx, kz = int(R * 0.25), int(R * 0.15)
    rr = 2 * s + 2
    for k in range(int(rr * 8)):
        a = k / (rr * 8) * 2 * math.pi
        for dz in (-1, 1):
            w.setze(kx + round(math.cos(a) * rr), int(rr) + 2 + round(math.sin(a) * rr), kz + dz, w.b("spruce_planks"))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        for k in range(int(rr)):
            w.setze(kx + round(math.cos(a) * k), int(rr) + 2 + round(math.sin(a) * k), kz, w.b("spruce_log", axis="y"),
                    False)
    H = int(8 * s + 6)
    for y in range(1, H):
        w.setze(kx - int(rr) - 2, y, kz, w.b("spruce_log", axis="y"))
    for k in range(int(6 * s + 4)):
        w.setze(kx - int(rr) - 2 - k, H - k // 3, kz, w.b("spruce_log", axis="x"))
    tx = kx - int(rr) - 2 - int(6 * s + 3)
    for y in range(3, H - 2):
        w.setze(tx, y, kz, w.b("chain", axis="y", waterlogged=False))
    w.setze(tx, 2, kz, w.b("smooth_stone"))
    w.setze(tx, 1, kz, w.b("smooth_stone"))
    for k in range(4 + g):
        w.setze(int(R * 0.5) + k % 3, 1 + k // 3, int(R * 0.45), w.b("smooth_stone"))
    haus(w, -int(R * 0.45), int(R * 0.4), 5, 5, 1, bruch(w), holz="spruce", H=3, tuer_s="east")
    return w


def kelterei(seed, g=1):
    """Kelterei: eine große Baumpresse mit langem Pressbaum aus Eichenstamm in einem offenen Kelterhaus, Bottiche
    voller Äpfel und Trauben, Fasslager und Obstbäume ringsum."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.1)
    B, T = int(5 * s + 6) | 1, int(3 * s + 5) | 1
    for x in range(-B // 2, B // 2 + 1):
        for z in range(-T // 2, T // 2 + 1):
            w.setze(x, 0, z, w.b("spruce_planks"))
            if abs(x) == B // 2 and abs(z) == T // 2:
                for y in range(1, 5):
                    w.setze(x, y, z, w.b("oak_log", axis="y"))
    satteldach(w, -B // 2, -T // 2, B // 2, T // 2, 5, Dachmat(w, ["mcw:red_terracotta", "brick", "mud_brick"]),
               first_x=True, ue=1, giebel=fw(w), traufe="oak")
    for x in range(-B // 2 + 1, B // 2):
        w.setze(x, 3, 0, w.b("oak_log", axis="x"))
    w.setze(0, 1, 0, w.b("oak_planks"))
    w.setze(0, 2, 0, w.b("oak_planks"))
    for x in (-1, 1):
        for z in (-1, 1):
            w.setze(x, 1, z, w.b("oak_slab", type="bottom", waterlogged=False))
    w.setze(B // 2 - 1, 1, 0, w.b("oak_log", axis="y"))
    w.setze(B // 2 - 1, 2, 0, w.b("oak_log", axis="y"))
    for k in range(3):
        w.setze(-B // 2 + 1 + k, 1, -T // 2 + 1, w.b("composter", level=8))
        w.setze(-B // 2 + 1 + k, 1, T // 2 - 1, w.b("barrel", facing="up", open=False))
    rng = w.rng
    for k in range(4 + 2 * g):
        a = k / (4 + 2 * g) * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.7), round(math.sin(a) * R * 0.7)
        from leuchtwald2 import laubball
        y0 = zellen.get((x, z), 0) + 1
        for y in range(y0, y0 + 3):
            w.setze(x, y, z, w.b("oak_log", axis="y"))
        laubball(w, x, y0 + 3, z, 2 + s * 0.6, arten=("oak_leaves", "flowering_azalea_leaves"), dicht=0.85)
        for _ in range(3):
            w.setze(x + int((rng.random() - 0.5) * 3), y0 + 2, z + int((rng.random() - 0.5) * 3),
                    w.b("red_concrete"), False)
    return w


def zimmerplatz(seed, g=2):
    """Zimmerplatz: ein Abbundplatz, auf dem das Fachwerkgerüst eines Hauses vormontiert steht, daneben behauene
    Balken auf Böcken, eine Säge, ein Richtkranz auf dem Dachfirst und eine Bauhütte."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.05)
    B, T = int(4 * s + 5), int(3 * s + 4)
    H = 4
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            rand_x = abs(x) == B
            rand_z = abs(z) == T
            if rand_x or rand_z:
                for y in range(1, H * 2 + 1):
                    pfosten = (x % 3 == 0 or rand_x) and (z % 3 == 0 or rand_z)
                    riegel = y in (1, H, 2 * H)
                    if pfosten:
                        w.setze(x, y, z, w.b("oak_log", axis="y"))
                    elif riegel:
                        w.setze(x, y, z, w.b("oak_log", axis="x" if rand_z else "z"))
    for k in range(T + 1):
        for x in range(-B, B + 1, 3):
            for sz in (-1, 1):
                w.setze(x, 2 * H + 1 + k, sz * (T - k), w.b("oak_log", axis="y"))
    for x in range(-B, B + 1):
        w.setze(x, 2 * H + T + 1, 0, w.b("oak_log", axis="x"))
    w.setze(0, 2 * H + T + 2, 0, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
    w.setze(0, 2 * H + T + 3, 0, w.b("red_wool"))
    for k in range(3):
        z = T + 3 + k * 2
        for x in range(-4, 5):
            w.setze(x, 2, z, w.b("stripped_oak_log", axis="x"))
        for x in (-3, 3):
            w.setze(x, 1, z, w.b("oak_fence"))
    haus(w, B + 5, -T, 5, 5, 1, bretter(w), holz="spruce", H=3, tuer_s="west", schorn=False)
    _ = zellen
    return w


def seifensiederei(seed, g=1):
    """Seifensiederei: ein kleines Steinhaus mit großem Siedekessel über offenem Feuer, Formen mit bunten
    Seifenblöcken zum Trocknen (rosa, gelb, grün), Laugenfässer und ein Kräuterbeet für Duftstoffe."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    zellen = wiese(w, R, 0.05)
    haus(w, 0, -int(R * 0.3), int(3 * s + 5) | 1, int(2 * s + 5) | 1, 1, bruch(w), holz="spruce", H=3,
         tuer_s="south")
    cx, cz = int(R * 0.3), int(R * 0.15)
    w.setze(cx, 1, cz, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    w.setze(cx, 2, cz, w.b("water_cauldron", level=3))
    for dx in (-1, 1):
        for y in range(1, 4):
            w.setze(cx + dx, y, cz, w.b("spruce_fence"))
    w.setze(cx - 1, 4, cz, w.b("spruce_log", axis="x"))
    w.setze(cx, 4, cz, w.b("spruce_log", axis="x"))
    w.setze(cx + 1, 4, cz, w.b("spruce_log", axis="x"))
    farben = ["pink_terracotta", "yellow_terracotta", "lime_terracotta", "white_terracotta"]
    for k in range(int(6 * s + 4)):
        x, z = -int(R * 0.5) + k % 4, int(R * 0.3) + k // 4
        w.setze(x, 1, z, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x, 2, z, w.b(farben[k % 4]))
    for k in range(3):
        w.setze(int(R * 0.5), 1, -1 + k, w.b("barrel", facing="up", open=False))
    for x in range(-2, 3):
        w.setze(x, zellen.get((x, R // 2), 0) + 1, R // 2, w.b(["allium", "lilac", "azure_bluet"][x % 3],
                                                                  **({"half": "lower"} if x % 3 == 1 else {})))
    return w


def schindelmacher(seed, g=1):
    """Schindelmacherei: Stapel frisch gespaltener Holzschindeln, ein Spaltbock, Rundholz-Abschnitte und ein Schuppen,
    dessen Dach als Musterfläche halb mit alten, halb mit neuen Schindeln gedeckt ist."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    zellen = wiese(w, R, 0.05)
    B, T = int(4 * s + 5) | 1, int(3 * s + 4) | 1
    for x in range(-B // 2, B // 2 + 1):
        for z in range(-T // 2, T // 2 + 1):
            if abs(x) == B // 2 and abs(z) == T // 2:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
    satteldach(w, -B // 2, -T // 2, B // 2, T // 2, 4, Dachmat(w, ["spruce", "oak", "dark_oak"]), first_x=True,
               ue=1, giebel=bretter(w), traufe="spruce")
    for k in range(int(5 * s + 3)):
        x, z = -B // 2 + 1 + k % 4, -T // 2 + 1 + (k // 4) % 2
        w.setze(x, 1 + k // 8, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    for k in range(3 + g):
        x, z = B // 2 + 2 + k % 2 * 2, -2 + k // 2 * 2
        w.setze(x, 1, z, w.b("spruce_log", axis="y"))
    w.setze(0, 1, T // 2 + 2, w.b("oak_log", axis="y"))
    w.setze(0, 2, T // 2 + 2, w.b("tripwire_hook", facing="north", attached=False, powered=False))
    _ = zellen
    return w


def hopfengarten(seed, g=2):
    """Hopfengarten mit Darre: hohe Stangen mit Drahtgerüst, an denen grüne Hopfenranken emporwachsen, Erntekörbe
    und eine Darre mit spitzem, belüftetem Kegeldach zum Trocknen der Dolden."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.05)
    H = int(5 * s + 5)
    for x in range(-int(R * 0.7), int(R * 0.1), 3):
        for z in range(-int(R * 0.6), int(R * 0.6), 3):
            if math.hypot(x, z) > R * 0.8:
                continue
            y0 = zellen.get((x, z), 0) + 1
            for y in range(y0, y0 + H):
                w.setze(x, y, z, w.b("spruce_fence"))
                if y > y0:
                    for dx, f in ((1, "west"), (-1, "east")):
                        if (y + x) % 2 == 0:
                            w.setze(x + dx, y, z, w.b("vine", north=False, south=False, east=f == "east",
                                                      west=f == "west", up=False), False)
            w.setze(x, y0 + H, z, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
    dx, dz = int(R * 0.45), 0
    r = 2 * s + 2
    for y in range(1, 5):
        for x, z in kreisrand(r, dx, dz):
            w.setze(x, y, z, w.b("bricks") if y < 3 else fw(w)(x, y, z))
    kegeldach(w, dx, dz, 5, int(r), Dachmat(w, ["mcw:red_terracotta", "brick"]), form="kegel", spitze=None)
    top = 5 + int((r + 1.2) * 2.4)
    for k in range(3):
        w.setze(dx + (k == 1), top + k - 1, dz, w.b("white_terracotta"))
    w.setze(dx + 1, top + 2, dz, w.b("white_terracotta"))
    for k in range(3):
        w.setze(dx - int(r) - 2, 1, -1 + k, w.b("composter", level=6))
    return w


def kerzenmanufaktur(seed, g=1):
    """Kerzenmanufaktur: ein Fachwerkhaus mit Ziehrad, an dem Bündel von Kerzen in Wachströgen hängen, Regale mit
    farbigen Kerzen in Reihen, Bienenwachs-Blöcke und eine Laterne aus hundert Kerzen über dem Eingang."""
    w = _neu(seed)
    s = S[g]
    R = int(7 * s + 5)
    zellen = wiese(w, R, 0.05)
    B, T = int(3 * s + 5) | 1, int(2 * s + 5) | 1
    haus(w, 0, -int(R * 0.25), B, T, 1, fw(w), holz="dark_oak", H=4, tuer_s="south")
    z1 = -int(R * 0.25) + T // 2
    farben = ["white", "yellow", "red", "lime", "light_blue", "purple"]
    for x in range(-B // 2 - 3, -B // 2):
        w.setze(x, 1, z1 + 2, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x, 2, z1 + 2, w.b(f"{farben[x % 6]}_candle", candles=4, lit=True, waterlogged=False))
    cx, cz = B // 2 + 3, z1 + 2
    for y in range(1, 5):
        w.setze(cx, y, cz, w.b("dark_oak_fence"))
    for dx in (-1, 1):
        w.setze(cx + dx, 4, cz, w.b("dark_oak_log", axis="x"))
        w.setze(cx + dx, 3, cz, w.b("chain", axis="y", waterlogged=False))
        w.setze(cx + dx, 2, cz, w.b("white_candle", candles=4, lit=False, waterlogged=False))
        w.setze(cx + dx, 1, cz, w.b("cauldron"))
    for k in range(3):
        w.setze(-B // 2 - 1, 1, -int(R * 0.25) - 1 + k, w.b("honeycomb_block"))
    w.setze(0, 4, z1 + 1, w.b("lantern", hanging=False, waterlogged=False))
    _ = zellen
    return w


HANDWERK3 = {
    "seilerei": ("Seilerei", seilerei),
    "fassbinderei": ("Fassbinderei", fassbinderei),
    "rossmuehle": ("Göpel-Ölmühle", rossmuehle),
    "papiermuehle": ("Papiermühle", papiermuehle),
    "korbflechterei": ("Korbflechterei", korbflechterei),
    "drechslerei": ("Drechslerei", drechslerei),
    "walkmuehle": ("Walkmühle", walkmuehle),
    "salzsiederei": ("Salzsiederei", salzsiederei),
    "kalkofen": ("Kalkofen", kalkofen),
    "teerschwelerei": ("Teerschwelerei", teerschwelerei),
    "glockengiesserei": ("Glockengießerei", glockengiesserei),
    "wagnerei": ("Wagnerei", wagnerei),
    "leinenweberei": ("Leinenweberei", leinenweberei),
    "steinbruch": ("Steinbruch mit Tretkran", steinbruch),
    "kelterei": ("Kelterei", kelterei),
    "zimmerplatz": ("Zimmerplatz", zimmerplatz),
    "seifensiederei": ("Seifensiederei", seifensiederei),
    "schindelmacher": ("Schindelmacherei", schindelmacher),
    "hopfengarten": ("Hopfengarten mit Darre", hopfengarten),
    "kerzenmanufaktur": ("Kerzenmanufaktur", kerzenmanufaktur),
}

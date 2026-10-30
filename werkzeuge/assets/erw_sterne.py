"""Sternwarte & Astronomie II – zwanzig weitere Bauten: Gipfelobservatorium, Riesensextant, Astrolab-Brunnen,
Mondsicheltor, Reflektorhalle, Finsternis-Monument, Sterngucker-Steg, Himmelsglobus, Sternkarten-Bibliothek,
Mondstation, Nebelskulptur, Galaxie-Mosaik, Pendelrotunde, Sonnenturm, Tierkreisplatz, Kalender-Obelisk, Mondgarten,
Orrery-Turm, Wolkenobservatorium und Sternenlager."""

from __future__ import annotations

import math

from arena import zelt
from erw_basis import M, S, birke, figur, haus, hoehe, wiese
from erw_markt import mensch
from feinbau import Dachmat, kegeldach, laterne
from flora import _neu
from himmel import wolke
from leuchtwald2 import kugel
from lib import Rauschen
from skulptur import Skulptur, dreh_x, dreh_y, ell, kap, kasten, torus
from steampunk2 import zylinder
from wueste_eis import kuppel

GLAS = ["purple_stained_glass", "magenta_stained_glass", "blue_stained_glass", "pink_stained_glass",
        "light_blue_stained_glass", "cyan_stained_glass"]


def teleskop(w, x, y, z, yaw, pitch, L, r=0.7, mat="waxed_cut_copper", stativ=True):
    """Fernrohr auf Dreibein; yaw um y, pitch nach oben."""
    if stativ:
        for k in range(3):
            a = k / 3 * 2 * math.pi
            for t in range(3):
                w.setze(round(x + math.cos(a) * (2 - t) * 0.6), y + t, round(z + math.sin(a) * (2 - t) * 0.6),
                        w.b("dark_oak_fence"), False)
        y += 3
    d = (math.cos(yaw) * math.cos(pitch), math.sin(pitch), math.sin(yaw) * math.cos(pitch))
    a = (x - d[0] * L * 0.35, y - d[1] * L * 0.35, z - d[2] * L * 0.35)
    b = (x + d[0] * L * 0.65, y + d[1] * L * 0.65, z + d[2] * L * 0.65)
    zylinder(w, a, b, r, w.b(mat))
    w.setze(round(b[0]), round(b[1]), round(b[2]), w.b("glass"))
    return b


def sternwarte(w, cx, cz, y0, R, H, wand=None, dach="white_concrete", schlitz=math.pi / 2):
    """Runder Turm mit Kuppel und Spaltöffnung; gibt die Kuppelbasis zurück."""
    wand = wand or M(w, [("stone_bricks", 2), ("polished_andesite", 1)])
    for y in range(y0, y0 + H):
        for x in range(cx - R - 1, cx + R + 2):
            for z in range(cz - R - 1, cz + R + 2):
                d = math.hypot(x - cx, z - cz)
                if d <= R + 0.4:
                    if d > R - 0.8:
                        fen = (y - y0) % 4 == 2 and (x == cx or z == cz)
                        w.setze(x, y, z, w.b("glass_pane") if fen else wand(x, y, z))
                    else:
                        w.bloecke.pop((x, y, z), None)
                        if y == y0:
                            w.setze(x, y - 1, z, w.b("polished_andesite"))
    yk = y0 + H
    for x, z in [(x, z) for x in range(cx - R - 1, cx + R + 2) for z in range(cz - R - 1, cz + R + 2)
                 if math.hypot(x - cx, z - cz) <= R + 1.4]:
        w.setze(x, yk, z, w.b("polished_andesite") if math.hypot(x - cx, z - cz) > R else w.b("spruce_planks"))
    kuppel(w, lambda x, y, z, t: w.b(dach) if (x + z) % 5 else w.b("light_gray_concrete"), cx, cz, yk + 1, R + 1,
           spitze=None)
    ux, uz = math.cos(schlitz), math.sin(schlitz)
    for x in range(cx - R - 2, cx + R + 3):
        for z in range(cz - R - 2, cz + R + 3):
            dx, dz = x - cx, z - cz
            quer = abs(-uz * dx + ux * dz)
            if quer <= 0.9 and (ux * dx + uz * dz) > -0.5:
                for y in range(yk + 1 + int(R * 0.15), yk + R + 3):
                    w.bloecke.pop((x, y, z), None)
    return yk


def sternhimmel(w, R, y0, n, seed_off=0, hoch=6):
    """Verstreute Endstäbe als Sterne über dem Bau."""
    rng = w.rng
    for k in range(n):
        x, z = int((rng.random() - 0.5) * R * 1.6), int((rng.random() - 0.5) * R * 1.6)
        y = y0 + int(rng.random() * hoch)
        if w.frei(x, y, z):
            w.setze(x, y, z, w.b("end_rod", facing="up"))


# ============================================================================ Bauten

def gipfelobservatorium(seed, g=2):
    """Gipfelobservatorium: auf dem schneebedeckten Gipfel eines schroffen Berges steht eine Kuppelsternwarte mit
    geöffnetem Spalt und herausragendem Fernrohr, ein Serpentinenpfad mit Geländer führt hinauf."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    H = int(12 * s + 6)
    f = M(w, [("stone", 3), ("andesite", 2), ("cobblestone", 1)])
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z)
            if d > R + 2 * rn(x, 0, z):
                continue
            h = int(H * max(0.0, 1 - (d / R) ** 0.9) + rn(x, 3, z) * 3.5)
            h = min(h, H - 2)
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("snow_block") if y == h and h > H * 0.6 else
                        w.b("grass_block", snowy=False) if y == h and h < H * 0.3 else f(x, y, z))
    yt = H - 1
    Rt = int(2.5 + 1.5 * s)
    for x in range(-Rt - 3, Rt + 4):
        for z in range(-Rt - 3, Rt + 4):
            if math.hypot(x, z) <= Rt + 2.5:
                for y in range(yt - 3, yt):
                    w.setze(x, y, z, f(x, y, z))
                for y in range(yt, H + 4):
                    w.bloecke.pop((x, y, z), None)
                w.setze(x, yt - 1, z, w.b("polished_andesite"))
    yk = sternwarte(w, 0, 0, yt, Rt, int(3 + s), wand=M(w, [("smooth_quartz", 2), ("white_concrete", 1)]),
                    dach="waxed_oxidized_cut_copper", schlitz=math.pi / 2)
    teleskop(w, 0, yk + 1, 0, math.pi / 2, 0.7, int(4 + 2 * s), r=0.6, stativ=False)
    steps = int(H * 3)
    for k in range(steps):
        t = k / steps
        a = math.pi / 2 + t * math.pi * 3
        r = R * 0.85 - t * (R * 0.85 - Rt - 3)
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        y = hoehe(w, x, z, H + 2)
        w.setze(x, y, z, w.b("gravel"))
        w.setze(x + 1, y, z, w.b("gravel"), True)
        for yy in range(y + 1, y + 3):
            w.bloecke.pop((x, yy, z), None)
    return w


def riesensextant(seed, g=2):
    """Riesensextant: ein haushohes Messinginstrument auf einem Steinsockel – ein Gradbogen mit Skala, zwei
    Speichenarme, ein Schwenkarm mit Spiegel und ein kleines Fernrohr, umgeben von einem Kompassrosen-Pflaster."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    rp = R * 0.6
    for x in range(-int(rp) - 1, int(rp) + 2):
        for z in range(-int(rp) - 1, int(rp) + 2):
            d = math.hypot(x, z)
            if d <= rp:
                a = math.atan2(z, x)
                stern = abs(math.sin(a * 4)) < 0.15 * (1 - d / rp) * 4
                w.setze(x, 0, z, w.b("gold_block") if stern and d < rp * 0.8 else
                        w.b("polished_andesite") if int(d) % 3 else w.b("smooth_stone"))
                w.bloecke.pop((x, 1, z), None)
    for x in range(-3, 4):
        for z in range(-2, 3):
            for y in range(1, 3):
                w.setze(x, y, z, w.b("stone_bricks") if y == 1 else w.b("polished_andesite"))
    L = 9 * s + 6
    y0 = 3
    gold, kup = w.b("gold_block"), w.b("waxed_cut_copper")
    for k in range(int(L * 2.2)):
        a = math.radians(-30) + k / (L * 2.2) * math.radians(60)
        x, y = round(math.sin(a) * L), round(y0 + L - math.cos(a) * L * 0.95)
        w.setze(x, y, 0, gold)
        w.setze(x, y - 1, 0, kup)
        if k % 3 == 0:
            w.setze(round(math.sin(a) * (L - 1.5)), round(y0 + L - math.cos(a) * (L - 1.5) * 0.95), 0,
                    w.b("chain", axis="y", waterlogged=False), False)
    top = (0, int(y0 + L))
    for a in (-30, 30, 0):
        ar = math.radians(a)
        n = int(L)
        for k in range(n):
            t = k / n
            x = round(math.sin(ar) * L * t)
            y = round(top[1] - math.cos(ar) * L * 0.95 * t)
            w.setze(x, y, 0, kup if a else w.b("iron_block"), False)
    for y in range(top[1] - 2, top[1] + 2):
        for x in (-1, 0, 1):
            w.setze(x, y, 1, w.b("glass"))
    teleskop(w, 2, top[1] - int(L * 0.5), 1, 0.0, 0.0, int(3 + s), r=0.5, stativ=False)
    return w


def astrolabbrunnen(seed, g=1):
    """Astrolab-Brunnen: ein rundes Brunnenbecken, aus dessen Mitte ein großes, aufrecht stehendes Astrolabium aus
    Gold und Kupfer mit filigranem Sternennetz und Zeigerlineal ragt; Wasser speit aus seinem Scheitel."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    wiese(w, R, huegel=0.1)
    rb = R * 0.55
    st = M(w, [("smooth_stone", 2), ("polished_diorite", 1)])
    for x in range(-int(rb) - 2, int(rb) + 3):
        for z in range(-int(rb) - 2, int(rb) + 3):
            d = math.hypot(x, z)
            if d <= rb:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("prismarine_bricks"))
                w.bloecke.pop((x, 1, z), None)
            elif d <= rb + 1:
                w.setze(x, 1, z, st(x, 1, z))
                w.setze(x, 0, z, st(x, 0, z))
            elif d <= rb + 3:
                w.setze(x, 0, z, w.b("polished_andesite"))
    u = 1.0 * s + 0.6
    Sk = Skulptur(w, u)
    Sk.mat("g", w.b("gold_block"))
    Sk.mat("k", w.b("waxed_cut_copper"))
    Sk.mat("s", w.b("polished_andesite"))
    Sk.plus(kap((0, 0, 0), (0, 2.2, 0), 1.2, 0.7), "s")
    Sk.plus(torus(0, 6.5, 0, 4.0, 0.45, achse="z"), "g")
    Sk.plus(torus(0, 6.5, 0, 2.6, 0.25, achse="z"), "k")
    Sk.plus(kap((-3.6, 6.5, 0), (3.6, 6.5, 0), 0.2), "k")
    Sk.plus(kap((0, 2.9, 0), (0, 10.1, 0), 0.2), "k")
    Sk.plus(kap((-2.5, 4.0, 0), (2.5, 9.0, 0), 0.3), "g")
    Sk.plus(ell(0, 10.9, 0, 0.6, 0.6, 0.6), "g")
    Sk.plus(kap((0, 2.0, 0), (0, 2.9, 0), 0.5), "g")
    Sk.rendern((-5, -1, -2), (5, 12, 2), versatz=(0.5, 1, 0.5))
    ytop = 1 + int(11.6 * u)
    w.setze(0, ytop, 0, w.b("water", level=0))
    for k in range(8):
        a = k / 8 * 2 * math.pi
        x, z = round(math.cos(a) * (rb + 2)), round(math.sin(a) * (rb + 2))
        if k % 2:
            laterne(w, x, 3, z, kette=0)
            w.setze(x, 1, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                                 waterlogged=False))
            w.setze(x, 2, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                                 waterlogged=False))
    return w


def mondsicheltor(seed, g=2):
    """Mondsicheltor: über einen silbernen Pfad wölbt sich eine gewaltige Mondsichel aus Quarz und Seelaternen, um
    sie herum schweben Sterne aus Endstäben; der Pfad ist von weißen Blumen gesäumt."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, huegel=0.15, blumen=0.0)
    rng = w.rng
    for z in range(-R, R + 1):
        for x in (-1, 0, 1):
            if (x, z) in zellen:
                w.setze(x, zellen[(x, z)], z, w.b("polished_diorite") if (x + z) % 2 else w.b("calcite"))
                w.bloecke.pop((x, zellen[(x, z)] + 1, z), None)
        for x in (-2, 2):
            if (x, z) in zellen and rng.random() < 0.6:
                w.setze(x, zellen[(x, z)] + 1, z, w.b(["lily_of_the_valley", "white_tulip", "oxeye_daisy",
                                                         "azure_bluet"][int(rng.integers(4))]))
    Rm = 6 * s + 4
    yc = Rm + 1
    for x in range(-int(Rm) - 2, int(Rm) + 3):
        for y in range(0, int(2 * Rm) + 3):
            d1 = math.hypot(x, y - yc)
            d2 = math.hypot(x - Rm * 0.45, y - yc - Rm * 0.15)
            if d1 <= Rm and d2 > Rm * 0.82:
                rand = d1 > Rm - 1 or d2 < Rm * 0.82 + 1
                for z in (0, 1):
                    w.setze(x, y, z, w.b("sea_lantern") if rand and (x + y) % 3 == 0 else
                            w.b("quartz_block") if rand else w.b("smooth_quartz"))
    for x in range(-2, 3):
        for y in range(1, 5):
            for z in (0, 1):
                if abs(x) <= 1:
                    w.bloecke.pop((x, y, z), None)
    sternhimmel(w, R, int(Rm), int(8 + 6 * s), hoch=int(Rm))
    return w


def reflektorhalle(seed, g=2):
    """Reflektorhalle: ein rechteckiges Teleskophaus, dessen Rolldach in zwei Hälften zur Seite gefahren ist; darin
    ein großes Spiegelteleskop auf einer Gabelmontierung, Arbeitsplattformen und Messinstrumente."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.1)
    A, B = int(4 * s + 5), int(3 * s + 5)
    H = int(3 * s + 5)
    wand = M(w, [("white_concrete", 3), ("light_gray_concrete", 1)])
    for x in range(-A, A + 1):
        for z in range(-B, B + 1):
            w.setze(x, 0, z, w.b("polished_andesite"))
            if abs(x) == A or abs(z) == B:
                for y in range(1, H + 1):
                    w.setze(x, y, z, wand(x, y, z) if not (y == H - 1 and (x + z) % 3 == 0) else w.b("glass"))
    for sx in (-1, 1):
        for x in range(sx * A, sx * (2 * A + 1), sx):
            if math.hypot(x, 0) > R - 1:
                break
            for z in range(-B, B + 1):
                w.setze(x, H + 1 + (abs(z) < B) * 0, z, w.b("light_gray_concrete") if abs(z) < B else
                        w.b("iron_block"))
            if abs(x) > A:
                for z in (-B, B):
                    for y in range(1, H + 1):
                        w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=True, west=True,
                                             waterlogged=False)) if y == H else None
                for z in (-B, B):
                    w.setze(x, 0, z, w.b("rail", shape="east_west", waterlogged=False))
    for x in (-2, 2):
        for y in range(1, int(3 + s)):
            w.setze(x, y, 0, w.b("iron_block"))
    for x in range(-2, 3):
        w.setze(x, 1, 0, w.b("iron_block"))
    L = int(6 + 4 * s)
    teleskop(w, 0, int(3 + s), 0, math.pi / 2, 0.9, L, r=1.4 + 0.4 * s, mat="white_concrete", stativ=False)
    for x in range(-A + 1, -A + 4):
        for z in range(-B + 1, B):
            w.setze(x, int(H * 0.5), z, w.b("spruce_planks"))
    w.setze(-A + 2, int(H * 0.5) + 1, 0, w.b("lectern", facing="east", has_book=True, powered=False))
    return w


def finsternismonument(seed, g=2):
    """Finsternis-Monument: auf einem Stufensockel steht eine goldene Sonnenscheibe, vor die sich ein schwarzer
    Mond schiebt; ein Strahlenkranz aus gelbem Glas und Endstäben bildet die Korona."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    for k in range(3):
        rr = R * 0.55 - k * 1.5
        for x in range(-int(rr) - 1, int(rr) + 2):
            for z in range(-int(rr) - 1, int(rr) + 2):
                if max(abs(x), abs(z)) <= rr:
                    w.setze(x, k + 1, z, w.b("polished_blackstone_bricks") if k < 2 else w.b("polished_blackstone"))
    Rs = 4 * s + 3
    yc = int(Rs + 5)
    for x in range(-int(Rs) - 5, int(Rs) + 6):
        for y in range(4, int(yc + Rs) + 6):
            d = math.hypot(x, y - yc)
            if d <= Rs:
                w.setze(x, y, -1, w.b("gold_block") if d > Rs * 0.35 else w.b("glowstone"))
            elif d <= Rs + 4:
                a = math.atan2(y - yc, x)
                if abs(math.sin(a * 8)) < 0.25:
                    w.setze(x, y, -1, w.b("yellow_stained_glass") if d < Rs + 2.5 else
                            w.b("end_rod", facing="up"))
            dm = math.hypot(x - Rs * 0.35, y - yc - Rs * 0.1)
            if dm <= Rs * 0.92:
                w.setze(x, y, 0, w.b("black_concrete") if dm < Rs * 0.92 - 1 else w.b("polished_blackstone"))
    for y in range(4, yc):
        w.setze(0, y, -2, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                              west="none", waterlogged=False))
    return w


def sternguckersteg(seed, g=2):
    """Sterngucker-Steg: ein langer Holzsteg führt auf einen stillen See hinaus zu einer runden Plattform mit drei
    Fernrohren auf Dreibeinen, Bänken und Laternen; im Wasser spiegeln sich Leuchtpunkte wie Sterne."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    rng = w.rng
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            if z > R * 0.55 + rn(x, 4, 0) * 2:
                for y in range(-3, 1):
                    w.setze(x, y, z, w.b("grass_block", snowy=False) if y == 0 else w.b("dirt"))
            else:
                for y in range(-2, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -3, z, w.b("sea_lantern") if rng.random() < 0.03 else w.b("mud"))
    rp = 2.5 + s
    zp = -int(R * 0.25)
    for x in range(-int(rp) - 1, int(rp) + 2):
        for z in range(zp - int(rp) - 1, zp + int(rp) + 2):
            d = math.hypot(x, z - zp)
            if d <= rp:
                w.setze(x, 1, z, w.b("spruce_planks"))
                if d > rp - 1:
                    w.setze(x, 2, z, w.b("spruce_fence"))
                if (x + z) % 3 == 0:
                    w.setze(x, 0, z, w.b("spruce_log", axis="y"))
    for z in range(zp + int(rp), int(R * 0.7)):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
        if z % 3 == 0:
            for sx in (-2, 2):
                w.setze(sx, 0, z, w.b("spruce_log", axis="y"))
                w.setze(sx, 1, z, w.b("spruce_log", axis="y"))
            laterne(w, 2, 3, z, kette=0)
            w.setze(2, 2, z, w.b("spruce_fence"))
    for k in range(3):
        a = -math.pi / 2 + (k - 1) * 0.9
        x, z = round(math.cos(a) * (rp - 2)), round(zp + math.sin(a) * (rp - 2))
        teleskop(w, x, 2, z, a, 0.6, int(3 + s), r=0.5)
    return w


def himmelsglobus(seed, g=2):
    """Himmelsglobus: in einem offenen Säulenrund steht ein riesiger, schräg gestellter Sternenglobus aus tiefblauem
    Stein mit leuchtenden Sternen, umschlossen von goldenem Meridianring und Horizontreif."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.1)
    rr = R * 0.65
    for x in range(-int(rr) - 1, int(rr) + 2):
        for z in range(-int(rr) - 1, int(rr) + 2):
            d = math.hypot(x, z)
            if d <= rr:
                w.setze(x, 0, z, w.b("smooth_quartz") if int(d) % 2 else w.b("polished_diorite"))
                w.bloecke.pop((x, 1, z), None)
    n = int(8 + 2 * s)
    Hs = int(5 * s + 6)
    for k in range(n):
        a = k / n * 2 * math.pi
        x, z = round(math.cos(a) * (rr - 1)), round(math.sin(a) * (rr - 1))
        for y in range(1, Hs):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
        w.setze(x, Hs, z, w.b("chiseled_quartz_block"))
    for k in range(int(2 * math.pi * (rr - 1) * 1.3)):
        a = k / (2 * math.pi * (rr - 1) * 1.3) * 2 * math.pi
        w.setze(round(math.cos(a) * (rr - 1)), Hs + 1, round(math.sin(a) * (rr - 1)), w.b("smooth_quartz_slab",
                                                                                          type="bottom",
                                                                                          waterlogged=False))
    rg = 3 * s + 2.5
    yc = rg + 3
    u = 1.0
    Sk = Skulptur(w, u)
    rng = w.rng
    Sk.mat("b", lambda x, y, z, *a: w.b("glowstone") if rng.random() < 0.06 else
           w.b("blue_concrete") if (x + y + z) % 4 else w.b("lapis_block"))
    Sk.mat("g", w.b("gold_block"))
    Sk.plus(ell(0, 0, 0, rg, rg, rg), "b")
    Sk.plus(torus(0, 0, 0, rg + 0.9, 0.35, achse="z"), "g")
    Sk.plus(kap((0, -rg - 1.5, 0), (0, rg + 1.5, 0), 0.3), "g")
    Sk.rendern((-rg - 2, -rg - 2, -rg - 2), (rg + 2, rg + 2, rg + 2), versatz=(0.5, yc, 0.5), dreh=dreh_x(0.4))
    for k in range(int(2 * math.pi * (rg + 1.5) * 1.3)):
        a = k / (2 * math.pi * (rg + 1.5) * 1.3) * 2 * math.pi
        w.setze(round(math.cos(a) * (rg + 1.5)), int(yc), round(math.sin(a) * (rg + 1.5)), w.b("waxed_cut_copper"),
                False)
    for y in range(1, int(yc - rg + 1)):
        w.setze(0, y, 0, w.b("polished_andesite"))
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.78
        for y in range(1, int(yc)):
            w.setze(round(math.cos(a) * (rg + 1.5)), y, round(math.sin(a) * (rg + 1.5)), w.b("waxed_cut_copper"))
    return w


def sternkartenbibliothek(seed, g=2):
    """Sternkarten-Bibliothek: ein gelehrter Kuppelbau mit tiefblauer, goldgesternter Kuppel, großen Rundfenstern,
    Säulenvorhalle und einer Freitreppe; drinnen Regale, Kartentische und ein Globus."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.1)
    A = int(4 * s + 4)
    H = int(3 * s + 5)
    wand = M(w, [("smooth_sandstone", 2), ("cut_sandstone", 1)])
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            w.setze(x, 0, z, w.b("polished_andesite"))
            if max(abs(x), abs(z)) == A:
                for y in range(1, H + 1):
                    rund = math.hypot(x if abs(z) == A else z, y - H * 0.55) < 1.8 + s * 0.4
                    w.setze(x, y, z, w.b("blue_stained_glass") if rund and abs(x if abs(z) == A else z) < A - 1
                            else wand(x, y, z))
            elif max(abs(x), abs(z)) == A - 1 and (x + z) % 2 == 0:
                for y in range(1, H - 1):
                    w.setze(x, y, z, w.b("bookshelf"))
    for x in range(-A - 1, A + 2):
        for z in range(-A - 1, A + 2):
            w.setze(x, H + 1, z, w.b("cut_sandstone_slab", type="bottom", waterlogged=False) if
                    max(abs(x), abs(z)) == A + 1 else w.b("smooth_sandstone"))
    kuppel(w, lambda x, y, z, t: w.b("gold_block") if (x * 7 + y * 3 + z * 5) % 13 == 0 else
           w.b("lapis_block") if (x + y) % 3 else w.b("blue_concrete"), 0, 0, H + 2, A, spitze="gold_block")
    for x in range(-A + 1, A, 2):
        for y in range(1, H):
            w.setze(x, y, A + 3, w.b("quartz_pillar", axis="y"))
    for x in range(-A, A + 1):
        for z in range(A + 1, A + 4):
            w.setze(x, H, z, w.b("smooth_sandstone"))
            w.setze(x, H + 1, z, w.b("cut_sandstone_slab", type="bottom", waterlogged=False))
    for k in range(2):
        for x in range(-2, 3):
            w.setze(x, 1 + k, A + 5 - k, w.b("sandstone_stairs", facing="north", half="bottom", shape="straight",
                                             waterlogged=False)) if k == 0 else None
    for y in (1, 2):
        w.bloecke.pop((0, y, A), None)
    kugel(w, 0, 2.5, 0, 1.3, w.b("light_blue_concrete"))
    w.setze(0, 1, 0, w.b("dark_oak_fence"))
    return w


def mondstation(seed, g=2):
    """Mondstation: auf grauem Kraterboden stehen weiße Wohnmodule, durch Röhren verbunden, ein Landefahrzeug auf
    Stelzbeinen, Solarflügel, eine Funkantenne und Spuren eines Rovers."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    rng = w.rng
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            h = int(rn(x, 2, z) * 2)
            for y in range(-2, h + 1):
                w.setze(x, y, z, w.b("light_gray_concrete_powder") if y == h and rn(x, 6, z) < 0.6 else
                        w.b("andesite") if y == h else w.b("stone"))
    for k in range(int(3 + 2 * s)):
        cx, cz = (rng.random() - 0.5) * R * 1.4, (rng.random() - 0.5) * R * 1.4
        rk = 1.5 + rng.random() * 2 * s
        for x in range(int(cx - rk) - 2, int(cx + rk) + 3):
            for z in range(int(cz - rk) - 2, int(cz + rk) + 3):
                d = math.hypot(x - cx, z - cz)
                if d < rk:
                    for y in range(0, 3):
                        w.bloecke.pop((x, y, z), None)
                    w.setze(x, -1 if d < rk * 0.6 else 0, z, w.b("gray_concrete_powder"))
                elif d < rk + 1 and (x, 0, z) in w.bloecke:
                    w.setze(x, 1, z, w.b("light_gray_concrete_powder"))
    mods = [(-int(R * 0.3), -int(R * 0.2)), (int(R * 0.2), -int(R * 0.25)), (0, int(R * 0.15))]
    rm = 2 + s * 0.6
    for (mx, mz) in mods:
        zylinder(w, (mx - 3 - s, 2 + rm, mz), (mx + 3 + s, 2 + rm, mz), rm, w.b("white_concrete"), hohl=True,
                 nieten=w.b("light_gray_concrete"), abstand=3)
        for dx in (-2, 2):
            w.setze(mx + dx, 1, mz, w.b("iron_block"))
        w.setze(mx, round(2 + rm), mz + round(rm), w.b("light_blue_stained_glass"))
    for (a, b) in zip(mods, mods[1:]):
        zylinder(w, (a[0], 2 + rm, a[1]), (b[0], 2 + rm, b[1]), 0.8, w.b("light_gray_concrete"))
    lx, lz = int(R * 0.5), int(R * 0.4)
    for dx, dz in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        for k in range(3):
            w.setze(lx + dx + (1 if dx < 0 else -1) * (k // 2), 1 + k, lz + dz, w.b("iron_bars", north=False,
                                                                                     south=False, east=False,
                                                                                     west=False, waterlogged=False))
    kugel(w, lx, 5, lz, 2.0 + s * 0.4, w.b("gold_block"), ry=1.6)
    w.setze(lx, 7, lz, w.b("white_concrete"))
    for k in range(int(4 + 2 * s)):
        for z in range(-1, 2):
            w.setze(-int(R * 0.6) + k, 3, int(R * 0.3) + z, w.b("daylight_detector", inverted=False, power=0))
    w.setze(-int(R * 0.6) + 2, 1, int(R * 0.3), w.b("iron_bars", north=False, south=False, east=False, west=False,
                                                    waterlogged=False))
    w.setze(-int(R * 0.6) + 2, 2, int(R * 0.3), w.b("iron_bars", north=False, south=False, east=False, west=False,
                                                    waterlogged=False))
    ax, az = int(R * 0.15), -int(R * 0.6)
    for y in range(1, int(6 + 3 * s)):
        w.setze(ax, y, az, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(ax, int(6 + 3 * s), az, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    for z in range(-R, R):
        for x in (int(R * 0.05), int(R * 0.05) + 2):
            if (x, 0, z) in w.bloecke and z % 2:
                w.setze(x, hoehe(w, x, z, 4), z, w.b("gray_concrete_powder"))
    w.setze(int(R * 0.05) + 1, 1, R // 2, w.b("white_concrete"))
    return w


def nebelskulptur(seed, g=2):
    """Nebelskulptur: über einem dunklen Steinsockel schwebt eine wirbelnde Wolke aus farbigem Glas – ein Sternen-
    nebel in Violett, Rosa und Blau, in dem junge Sterne als Leuchtsteine glimmen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    rn = Rauschen(w, 2.5)
    rng = w.rng
    for x in range(-3, 4):
        for z in range(-3, 4):
            if math.hypot(x, z) <= 3.2:
                for y in range(1, 3):
                    w.setze(x, y, z, w.b("polished_blackstone") if y == 2 else w.b("blackstone"))
    for y in range(3, 7):
        w.setze(0, y, 0, w.b("polished_blackstone_wall", up=True, north="none", south="none", east="none",
                             west="none", waterlogged=False))
    rx, ry = 5 * s + 4, 2.5 * s + 2.5
    yc = 7 + ry
    for x in range(-int(rx) - 1, int(rx) + 2):
        for y in range(int(yc - ry) - 1, int(yc + ry) + 2):
            for z in range(-int(rx) - 1, int(rx) + 2):
                a = math.atan2(z, x)
                r = math.hypot(x, z) / rx
                arm = math.sin(a * 2 + r * 6)
                e = r * r + ((y - yc) / ry) ** 2
                if e < 1 and arm + rn(x, y, z) * 1.2 > 0.6 + e * 0.5:
                    w.setze(x, y, z, w.b("glowstone") if rng.random() < 0.03 else
                            w.b(GLAS[int((a + math.pi) / (2 * math.pi) * 3 + r * 3) % len(GLAS)]))
    return w


def galaxiemosaik(seed, g=2):
    """Galaxie-Mosaik: ein großer, leicht gewölbter Platz zeigt eine Spiralgalaxie aus Beton – leuchtender Kern,
    zwei geschwungene Arme aus Weiß, Hellblau und Violett vor schwarzem Grund – mit Bänken ringsum."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wiese(w, R, huegel=0.1)
    rg = R * 0.78
    rng = w.rng
    for x in range(-int(rg) - 1, int(rg) + 2):
        for z in range(-int(rg) - 1, int(rg) + 2):
            d = math.hypot(x, z)
            if d > rg:
                continue
            r = d / rg
            a = math.atan2(z, x)
            arm = min(abs(math.sin((a - math.log(r + 0.05) * 2.2))), 1)
            y = 1 if r < 0.25 else 0
            if r < 0.15:
                b = "glowstone"
            elif r < 0.25:
                b = "shroomlight" if (x + z) % 2 else "yellow_concrete"
            elif arm < 0.3:
                b = ["white_concrete", "light_blue_concrete", "purple_concrete"][int(r * 3) % 3]
            else:
                b = "black_concrete" if rng.random() > 0.04 else "sea_lantern"
            w.setze(x, y, z, w.b(b))
            w.bloecke.pop((x, y + 1, z), None)
    for k in range(8):
        a = k / 8 * 2 * math.pi
        x, z = round(math.cos(a) * (rg + 2)), round(math.sin(a) * (rg + 2))
        w.setze(x, 1, z, w.b("polished_blackstone_stairs", facing="north", half="bottom", shape="straight",
                             waterlogged=False))
    return w


def pendelrotunde(seed, g=2):
    """Pendelrotunde: ein offener Säulenrundbau mit flacher Kuppel, aus deren Scheitel ein langes Kettenpendel mit
    goldener Kugel über einer Kompassrose schwingt, ringsum ein Kranz aus kleinen Stelen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    rr = R * 0.6
    H = int(8 * s + 6)
    for x in range(-int(rr) - 1, int(rr) + 2):
        for z in range(-int(rr) - 1, int(rr) + 2):
            d = math.hypot(x, z)
            if d <= rr:
                a = math.atan2(z, x)
                rose = abs(math.sin(a * 4)) * d < 0.8 and d < rr * 0.7
                w.setze(x, 0, z, w.b("gold_block") if rose else w.b("polished_andesite") if int(d) % 2 else
                        w.b("smooth_stone"))
                w.bloecke.pop((x, 1, z), None)
    n = int(10 + 2 * s)
    for k in range(n):
        a = k / n * 2 * math.pi
        x, z = round(math.cos(a) * (rr - 1)), round(math.sin(a) * (rr - 1))
        for y in range(1, H):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
    for x in range(-int(rr) - 1, int(rr) + 2):
        for z in range(-int(rr) - 1, int(rr) + 2):
            d = math.hypot(x, z)
            if d <= rr:
                w.setze(x, H, z, w.b("smooth_quartz") if d > rr - 2 else w.b("quartz_bricks"))
    kuppel(w, w.b("waxed_oxidized_cut_copper"), 0, 0, H + 1, int(rr * 0.7), spitze="gold_block")
    for x in range(-int(rr * 0.7) + 1, int(rr * 0.7)):
        for z in range(-int(rr * 0.7) + 1, int(rr * 0.7)):
            if math.hypot(x, z) < rr * 0.7 - 1:
                for y in range(H, H + int(rr * 0.7)):
                    w.bloecke.pop((x, y, z), None)
    for y in range(3, H + int(rr * 0.7) - 1):
        w.setze(0, y, 0, w.b("chain", axis="y", waterlogged=False))
    kugel(w, 0, 2.2, 0, 1.0 + 0.3 * s, w.b("gold_block"))
    for k in range(16):
        a = k / 16 * 2 * math.pi
        x, z = round(math.cos(a) * 3.5), round(math.sin(a) * 3.5)
        w.setze(x, 1, z, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return w


def sonnenturm(seed, g=2):
    """Sonnenturm: ein schlanker, quadratischer Turm mit Außentreppe, auf dessen Spitze zwei schräg gestellte
    Spiegel in Rahmen das Sonnenlicht in den Schacht lenken; am Fuß ein Laborhaus."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    a = int(2 + s * 0.6)
    H = int(12 * s + 10)
    wand = M(w, [("white_concrete", 3), ("light_gray_concrete", 1)])
    for y in range(1, H + 1):
        for x in range(-a, a + 1):
            for z in range(-a, a + 1):
                if max(abs(x), abs(z)) == a:
                    w.setze(x, y, z, w.b("glass") if (y % 6 == 3 and abs(x) + abs(z) == a) else wand(x, y, z))
                else:
                    w.bloecke.pop((x, y, z), None)
    seiten = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    for k in range(H):
        sx, sz = seiten[(k // (2 * a + 2)) % 4]
        t = k % (2 * a + 2) - a - 1
        x = sx * (a + 1) + (-sz) * t if sx else -sz * 0 + t * (1 if sz > 0 else -1)
        z = sz * (a + 1) + sx * t if sz else t * (-1 if sx > 0 else 1)
        if sx:
            x, z = sx * (a + 1), t * sx
        else:
            x, z = -t * sz, sz * (a + 1)
        w.setze(x, k + 1, z, w.b("iron_block") if k % 4 == 0 else w.b("smooth_stone_slab", type="top",
                                                                         waterlogged=False), False)
    for x in range(-a - 1, a + 2):
        for z in range(-a - 1, a + 2):
            w.setze(x, H + 1, z, w.b("iron_block") if max(abs(x), abs(z)) == a + 1 else w.b("smooth_stone"))
    for k, (ox, oz) in enumerate(((-1, 0), (1, 0))):
        for t in range(int(3 + s)):
            for dz in range(-1, 2):
                w.setze(ox * (1 + t // 2) , H + 2 + t, dz + oz, w.b("white_stained_glass") if t % 2 == 0 else
                        w.b("light_gray_stained_glass"), False)
    haus(w, int(R * 0.45), int(R * 0.3), 6, 4, 1, M(w, [("white_concrete", 2), ("light_gray_concrete", 1)]),
         holz="spruce", H=3, dach=("deepslate_tile",), tuer_s="west", schorn=False)
    return w


def tierkreisplatz(seed, g=2):
    """Tierkreisplatz: ein runder Platz, in zwölf farbige Felder aus glasierter Keramik geteilt, mit einem Sternen-
    mosaik in der Mitte und zwölf Stelen mit farbigen Laternen am Rand."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.1)
    rp = R * 0.75
    farben = ["red", "orange", "yellow", "lime", "green", "cyan", "light_blue", "blue", "purple", "magenta", "pink",
              "white"]
    for x in range(-int(rp) - 1, int(rp) + 2):
        for z in range(-int(rp) - 1, int(rp) + 2):
            d = math.hypot(x, z)
            if d > rp:
                continue
            a = (math.atan2(z, x) + math.pi) / (2 * math.pi) * 12
            sek = int(a) % 12
            if d < rp * 0.25:
                b = w.b("gold_block") if abs(math.sin(math.atan2(z, x) * 4)) * d < 1 else w.b("lapis_block")
            elif abs(a - round(a)) * 2 * math.pi / 12 * d < 0.5 or abs(d - rp * 0.25) < 0.6:
                b = w.b("polished_blackstone")
            elif d > rp - 1:
                b = w.b("smooth_quartz")
            else:
                b = w.b(f"{farben[sek]}_glazed_terracotta", facing=["north", "east", "south", "west"][sek % 4])
            w.setze(x, 0, z, b)
            w.bloecke.pop((x, 1, z), None)
    for k in range(12):
        a = (k + 0.5) / 12 * 2 * math.pi - math.pi
        x, z = round(math.cos(a) * (rp + 1)), round(math.sin(a) * (rp + 1))
        for y in range(1, 3):
            w.setze(x, y, z, w.b("quartz_pillar", axis="y"))
        w.setze(x, 3, z, w.b(f"{farben[k]}_stained_glass"))
        w.setze(x, 4, z, w.b("lantern", hanging=False, waterlogged=False))
    return w


def kalenderobelisk(seed, g=2):
    """Kalender-Obelisk: ein hoher, spitz zulaufender Obelisk mit goldenem Pyramidion inmitten eines Platzes, über den
    Schattenlinien aus dunklem Stein laufen; an jeder Linie ein Monatsstein."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.1)
    rp = R * 0.8
    for x in range(-int(rp) - 1, int(rp) + 2):
        for z in range(-int(rp) - 1, int(rp) + 2):
            d = math.hypot(x, z)
            if d <= rp:
                a = math.atan2(z, x)
                linie = z <= 0 and abs(math.sin(a * 6)) * d < 0.6
                w.setze(x, 0, z, w.b("polished_blackstone") if linie else w.b("smooth_sandstone") if int(d) % 3
                        else w.b("cut_sandstone"))
                w.bloecke.pop((x, 1, z), None)
    for k in range(7):
        a = -math.pi + k / 6 * math.pi
        x, z = round(math.cos(a) * (rp - 1)), round(math.sin(a) * (rp - 1))
        w.setze(x, 1, z, w.b("chiseled_sandstone"))
    H = int(12 * s + 8)
    for y in range(1, H + 1):
        b = 2.0 * (1 - y / H * 0.55) + 0.3
        for x in range(-2, 3):
            for z in range(-2, 3):
                if max(abs(x), abs(z)) <= b:
                    w.setze(x, y, z, w.b("quartz_bricks") if y > 3 else w.b("smooth_quartz"))
    for k in range(3):
        for x in range(-1 + k, 2 - k):
            for z in range(-1 + k, 2 - k):
                w.setze(x, H + 1 + k, z, w.b("gold_block"))
    for x in range(-3, 4):
        for z in range(-3, 4):
            if max(abs(x), abs(z)) == 3:
                w.setze(x, 1, z, w.b("smooth_sandstone_slab", type="bottom", waterlogged=False))
    return w


def mondgarten(seed, g=1):
    """Mondgarten: ein Nachtgarten aus weißen Blumen und Birken um einen runden Teich, auf dem eine Mondscheibe aus
    Quarz schwimmt, betreten durch ein kreisrundes Mondtor in einer weißen Mauer; leuchtende Laternen im Gras."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    zellen = wiese(w, R, huegel=0.1, blumen=0.0)
    rng = w.rng
    for (x, z), h in zellen.items():
        if rng.random() < 0.25:
            w.setze(x, h + 1, z, w.b(["lily_of_the_valley", "white_tulip", "oxeye_daisy", "azure_bluet"]
                                     [int(rng.integers(4))]))
    rt = R * 0.35
    for x in range(-int(rt) - 1, int(rt) + 2):
        for z in range(-int(rt) - 1, int(rt) + 2):
            d = math.hypot(x, z + 1)
            if d <= rt:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("water", level=0))
                w.setze(x, -2, z, w.b("calcite"))
                w.bloecke.pop((x, 1, z), None)
            elif d <= rt + 1:
                w.setze(x, 0, z, w.b("calcite"))
                w.bloecke.pop((x, 1, z), None)
    rm = max(1.2, rt * 0.4)
    for x in range(-int(rm) - 1, int(rm) + 2):
        for z in range(-int(rm) - 1, int(rm) + 2):
            if math.hypot(x, z) <= rm:
                w.setze(x, 1, z - 1, w.b("smooth_quartz_slab", type="bottom", waterlogged=True))
    zm = int(R * 0.6)
    rg = 2 + s
    for x in range(-R, R + 1):
        if (x, zm) not in zellen:
            continue
        for y in range(1, int(2 * rg) + 3):
            if math.hypot(x, y - rg - 1) <= rg:
                continue
            w.setze(x, y, zm, w.b("white_concrete") if y < int(2 * rg) + 2 else w.b("smooth_quartz_slab",
                                                                                   type="bottom",
                                                                                   waterlogged=False))
    for k in range(int(2 + s)):
        x = -int(R * 0.6) + k * int(R * 0.6)
        if x == 0:
            x = int(R * 0.5)
        birke(w, x, 1, -int(R * 0.55), seed + k, 6 + 2 * s)
    for k in range(int(4 + 2 * s)):
        a = k / (4 + 2 * s) * 2 * math.pi
        x, z = round(math.cos(a) * (rt + 2.5)), round(math.sin(a) * (rt + 2.5) - 1)
        w.setze(x, 1, z, w.b("sea_pickle", pickles=3, waterlogged=False)) if False else \
            w.setze(x, 1, z, w.b("lantern", hanging=False, waterlogged=False))
    return w


def orrery_turm(seed, g=2):
    """Orrery-Turm: auf einem runden Steinturm dreht sich ein gewaltiges Planetenmodell – eine leuchtende Sonne im
    Zentrum, an Messingarmen kreisen Planeten verschiedener Größe und Farbe, einer davon mit Ring."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.1)
    rt = int(2 + s * 0.6)
    H = int(6 * s + 6)
    st = M(w, [("stone_bricks", 2), ("polished_andesite", 1)])
    for y in range(1, H + 1):
        for x in range(-rt - 1, rt + 2):
            for z in range(-rt - 1, rt + 2):
                d = math.hypot(x, z)
                if d <= rt + 0.4:
                    w.setze(x, y, z, st(x, y, z) if d > rt - 0.8 or y == H else w.b("air") if False else
                            st(x, y, z))
    for x in range(-rt - 2, rt + 3):
        for z in range(-rt - 2, rt + 3):
            if math.hypot(x, z) <= rt + 1.5:
                w.setze(x, H + 1, z, w.b("waxed_cut_copper"))
    ys = H + 3 + int(1.5 * s)
    for y in range(H + 2, ys):
        w.setze(0, y, 0, w.b("waxed_cut_copper"))
    kugel(w, 0, ys + 1.5 * s, 0, 1.5 * s + 1.2, w.b("glowstone"))
    planeten = [("gray_concrete", 0.6), ("orange_terracotta", 0.9), ("blue_concrete", 1.0), ("red_terracotta", 0.8),
                ("brown_terracotta", 1.6), ("yellow_terracotta", 1.4)]
    n = 3 + g
    for k in range(min(n, len(planeten))):
        mat, gr = planeten[k]
        a = k * 2.2
        r = 3 * s + 3 + k * (2 * s + 1.5)
        if r > R - 2:
            break
        yy = H + 2 + k % 2
        for t in range(int(r)):
            w.setze(round(math.cos(a) * t), yy, round(math.sin(a) * t), w.b("waxed_cut_copper"), False)
        px, pz = math.cos(a) * r, math.sin(a) * r
        rp = gr * (0.5 + 0.35 * s)
        for y in range(yy, int(yy + rp + 2)):
            w.setze(round(px), y, round(pz), w.b("waxed_cut_copper"), False)
        kugel(w, px, yy + rp + 2, pz, rp, w.b(mat))
        if k == 5 or (k == n - 1 and k >= 4):
            for j in range(int(2 * math.pi * (rp + 1.5) * 1.3)):
                b = j / (2 * math.pi * (rp + 1.5) * 1.3) * 2 * math.pi
                w.setze(round(px + math.cos(b) * (rp + 1.5)), round(yy + rp + 2), round(pz + math.sin(b) * (rp + 1.5)),
                        w.b("smooth_sandstone_slab", type="bottom", waterlogged=False), False)
    return w


def wolkenobservatorium(seed, g=2):
    """Wolkenobservatorium: auf einer großen, bauschigen Wolke thront eine kleine Sternwarte mit Kuppel und Fernrohr,
    eine Strickleiter baumelt nach unten, Sterne funkeln ringsum."""
    w = _neu(seed)
    s = S[g]
    R = int(8 * s + 6)
    yc = int(8 * s + 8)
    wolke(w, 0, yc, 0, R * 0.9, flach=0.45, dichte=9)
    yt = hoehe(w, 0, 0, yc + R) + 1
    for x in range(-3, 4):
        for z in range(-3, 4):
            if math.hypot(x, z) <= 3.5:
                w.setze(x, yt - 1, z, w.b("white_wool"))
    rt = int(2 + s * 0.6)
    yk = sternwarte(w, 0, 0, yt, rt, int(3 + s), wand=M(w, [("white_concrete", 2), ("smooth_quartz", 1)]),
                    dach="light_blue_concrete", schlitz=math.pi / 2)
    teleskop(w, 0, yk + 1, 0, math.pi / 2, 0.8, int(3 + 2 * s), r=0.5, mat="gold_block", stativ=False)
    xl = int(R * 0.6)
    yb = hoehe(w, xl, 0, yc + R)
    for y in range(max(1, yb - int(6 + 4 * s)), yb):
        w.setze(xl, y, 0, w.b("chain", axis="y", waterlogged=False) if y % 3 else w.b("spruce_fence"), False)
    sternhimmel(w, R, yt, int(10 + 6 * s), hoch=int(6 + 4 * s))
    return w


def sternenlager(seed, g=2):
    """Sternenlager: eine nächtliche Wiese mit Zelten, einem Lagerfeuer im Steinkreis, ausgebreiteten Decken zum
    Sterneschauen, Fernrohren auf Dreibeinen und Laternenpfählen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, huegel=0.3, blumen=0.03)
    for k in range(int(2 + s)):
        a = k / (2 + s) * 2 * math.pi + 0.4
        x, z = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        zelt(w, x, z, int(1.5 + s * 0.4), farben=[("blue", "white"), ("green", "yellow"), ("orange", "white"),
                                                   ("purple", "white")][k % 4])
    for k in range(8):
        a = k / 8 * 2 * math.pi
        w.setze(round(math.cos(a) * 1.6), 1, round(math.sin(a) * 1.6), w.b("cobblestone"))
    w.setze(0, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for k in range(3):
        x0, z0 = -4 + k * 4, 4
        for dx in range(2):
            for dz in range(3):
                x, z = x0 + dx, z0 + dz
                w.setze(x, zellen.get((x, z), 0) + 1, z,
                        w.b(f"{['blue', 'red', 'green'][k]}_carpet") if (dx + dz) % 2 else w.b("white_carpet"))
    for k in range(2 + g // 2):
        x, z = -int(R * 0.3) + k * int(R * 0.3), -int(R * 0.3)
        teleskop(w, x, zellen.get((x, z), 0) + 1, z, -math.pi / 2, 0.8, int(3 + s), r=0.45)
    for k in range(3):
        a = k * 2.1 + 1
        x, z = round(math.cos(a) * R * 0.75), round(math.sin(a) * R * 0.75)
        y = zellen.get((x, z), 0)
        for d in range(1, 4):
            w.setze(x, y + d, z, w.b("spruce_fence"))
        w.setze(x, y + 4, z, w.b("lantern", hanging=False, waterlogged=False))
    figur(w, 0.3 * s + 0.22, mensch(w, "blue_wool"), (-2, -1, -2), (2, 6, 2), pos=(-3, 1, 2), winkel=1.0)
    return w


STERNE3 = {
    "gipfelobservatorium": ("Gipfelobservatorium", gipfelobservatorium),
    "riesensextant": ("Riesensextant", riesensextant),
    "astrolabbrunnen": ("Astrolab-Brunnen", astrolabbrunnen),
    "mondsicheltor": ("Mondsicheltor", mondsicheltor),
    "reflektorhalle": ("Reflektorhalle", reflektorhalle),
    "finsternismonument": ("Finsternis-Monument", finsternismonument),
    "sternguckersteg": ("Sterngucker-Steg", sternguckersteg),
    "himmelsglobus": ("Himmelsglobus", himmelsglobus),
    "sternkartenbibliothek": ("Sternkarten-Bibliothek", sternkartenbibliothek),
    "mondstation": ("Mondstation", mondstation),
    "nebelskulptur": ("Nebelskulptur", nebelskulptur),
    "galaxiemosaik": ("Galaxie-Mosaik", galaxiemosaik),
    "pendelrotunde": ("Pendelrotunde", pendelrotunde),
    "sonnenturm": ("Sonnenturm", sonnenturm),
    "tierkreisplatz": ("Tierkreisplatz", tierkreisplatz),
    "kalenderobelisk": ("Kalender-Obelisk", kalenderobelisk),
    "mondgarten": ("Mondgarten", mondgarten),
    "orrery_turm": ("Orrery-Turm", orrery_turm),
    "wolkenobservatorium": ("Wolkenobservatorium", wolkenobservatorium),
    "sternenlager": ("Sternenlager", sternenlager),
}

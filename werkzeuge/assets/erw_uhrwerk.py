"""Uhrwerk & Maschinen II – zwanzig weitere Maschinenbauten: Dampftraktor, Balancier-Pumpwerk, Zahnrad-Klappbrücke,
Standseilbahn, Orrery-Pavillon, Mechanischer Riesenkäfer, Gasometer, Wasserturm, Semaphor-Signalmast, Druckerei mit
Dampfpresse, Zeche mit Förderturm, Dampforgel, Rohrpost-Station, Luftschiff-Ankermast, Uhrwerk-Garten, Lokschuppen
mit Drehscheibe, Glockenspiel-Turm, Dampfkran am Kai, Dampf-Kettenkarussell und Zahnrad-Denkmal."""

from __future__ import annotations

import math

import numpy as np

from erw_basis import M, S, figur, haus, hoehe, wiese
from feinbau import Dachmat, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen
from skulptur import ell, kap, kasten, kegel, kreisrand
from steampunk2 import gleis, huelle, schornstein, zylinder


def industrie(w, R, cx=0, cz=0):
    zellen = wiese(w, R, 0.05, art="kies", cx=cx, cz=cz)
    rng = w.rng
    for (x, z), h in zellen.items():
        if rng.random() < 0.3:
            w.setze(x, h, z, w.b("cobblestone") if rng.random() < 0.5 else w.b("gravel"))
    return zellen


def ziegel(w):
    return M(w, [("bricks", 4), ("mud_bricks", 1), ("granite", 0.5)])


def kupfer(w):
    return M(w, [("waxed_cut_copper", 3), ("waxed_exposed_cut_copper", 1), ("waxed_copper_block", 1)])


def zahnrad(w, cx, cy, cz, R, ebene="xy", mat="waxed_cut_copper", zahn=None, nabe="iron_block"):
    zahn = zahn or mat
    n = max(8, int(R * 2.2))
    for a in range(-int(R) - 2, int(R) + 3):
        for b in range(-int(R) - 2, int(R) + 3):
            d = math.hypot(a, b)
            ang = math.atan2(b, a)
            zahnig = math.cos(ang * n) > 0.2
            blk = None
            if R - 1.2 <= d <= R + 0.3:
                blk = w.b(mat)
            elif R + 0.3 < d <= R + 1.3 and zahnig:
                blk = w.b(zahn)
            elif d <= 1.1:
                blk = w.b(nabe)
            elif d < R - 1.2 and (abs(a) < 0.6 or abs(b) < 0.6 or (abs(abs(a) - abs(b)) < 0.6 and R > 4)):
                blk = w.b(mat)
            if blk is None:
                continue
            p = (cx + a, cy + b, cz) if ebene == "xy" else (cx, cy + b, cz + a) if ebene == "zy" else (cx + a, cy, cz + b)
            w.setze(*p, blk)


def traeger(w, a, b, mat="iron_bars"):
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]), abs(b[2] - a[2]))) + 1
    for k in range(n + 1):
        t = k / n
        w.setze(round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t), round(a[2] + (b[2] - a[2]) * t),
                w.b(mat, waterlogged=False) if mat in ("iron_bars", "chain") else w.b(mat))


# ============================================================================ Bauten

def dampftraktor(seed, g=1):
    """Dampftraktor: eine schwere Zugmaschine mit liegendem Kessel, hohem Schornstein, riesigen genieteten Hinter-
    rädern, Schwungrad und Führerstand, die einen Holzwagen voller Fässer über einen Feldweg zieht."""
    w = _neu(seed)
    s = S[g]
    u = 0.9 * s + 0.5
    R = int(10 * u + 6)
    zellen = wiese(w, R, 0.05)
    for x in range(-R, R + 1):
        for z in (-2, -1, 0, 1, 2):
            if (x, z) in zellen:
                w.setze(x, zellen[(x, z)], z, w.b("dirt_path"))
    y0 = int(2 * u) + 1
    zylinder(w, (-2 * u, y0 + 1.5 * u, 0), (5 * u, y0 + 1.5 * u, 0), 1.4 * u, w.b("black_concrete"),
             nieten=w.b("waxed_cut_copper"), abstand=3)
    for sz in (-1, 1):
        for a in range(-int(2.4 * u) - 1, int(2.4 * u) + 2):
            for b in range(-int(2.4 * u) - 1, int(2.4 * u) + 2):
                d = math.hypot(a, b)
                if 2.4 * u - 0.8 <= d <= 2.4 * u + 0.4 or d < 0.8 or (d < 2.4 * u and (a == 0 or b == 0)):
                    for dz in (0, 1):
                        w.setze(-round(2 * u) + a, y0 + b, sz * (round(1.6 * u) + 1 + dz), w.b("polished_blackstone"
                                                                                               if d > 1 else "iron_block"))
        for a in range(-int(1.2 * u) - 1, int(1.2 * u) + 2):
            for b in range(-int(1.2 * u) - 1, int(1.2 * u) + 2):
                if math.hypot(a, b) <= 1.2 * u + 0.3:
                    w.setze(round(4 * u) + a, round(1.2 * u) + 1 + b, sz * (round(1.6 * u) + 1),
                            w.b("polished_blackstone"))
    schornstein(w, round(4.5 * u), y0 + round(2.8 * u), 0, int(4 * u), r=0, mat="black_concrete")
    for x in range(-round(4 * u), -round(2 * u)):
        for z in range(-round(1.4 * u), round(1.4 * u) + 1):
            w.setze(x, y0 + round(0.5 * u), z, w.b("spruce_planks"))
            if abs(z) == round(1.4 * u) or x == -round(4 * u):
                w.setze(x, y0 + round(0.5 * u) + 1, z, w.b("iron_bars", waterlogged=False))
        for z in range(-round(1.4 * u), round(1.4 * u) + 1):
            w.setze(x, y0 + round(3.5 * u), z, w.b("black_concrete"))
    wx = -round(7 * u)
    for x in range(wx - round(3 * u), wx + 1):
        for z in range(-2, 3):
            w.setze(x, 2, z, w.b("spruce_planks"))
            if abs(z) == 2:
                w.setze(x, 3, z, w.b("spruce_fence"))
        if (x - wx) % 2 == 0:
            w.setze(x, 3, 0, w.b("barrel", facing="up", open=False))
    for sx in (wx - round(3 * u) + 1, wx - 1):
        for sz in (-3, 3):
            w.setze(sx, 1, sz, w.b("dark_oak_log", axis="z"))
    return w


def balancierpumpe(seed, g=2):
    """Balancier-Pumpwerk: ein hohes Backsteinhaus mit Rundbogenfenstern, aus dessen Giebel ein gewaltiger, wippender
    Balancierbalken ragt, der das Pumpgestänge über einem Brunnenschacht bewegt; ein Schornstein daneben."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    industrie(w, R)
    B, T = int(4 * s + 5) | 1, int(4 * s + 5) | 1
    H = int(6 * s + 6)
    zg = ziegel(w)
    for x in range(-B // 2, B // 2 + 1):
        for z in range(-T // 2, T // 2 + 1):
            for y in range(1, H + 1):
                if abs(x) == B // 2 or abs(z) == T // 2:
                    fen = 3 <= y <= H - 2 and (x + z) % 3 == 0 and not (abs(x) == B // 2 and abs(z) == T // 2)
                    w.setze(x, y, z, w.b("glass_pane") if fen else zg(x, y, z))
    satteldach(w, -B // 2, -T // 2, B // 2, T // 2, H + 1, Dachmat(w, ["deepslate_tile", "cobbled_deepslate"]),
               first_x=False, ue=1, giebel=zg, traufe="dark_oak")
    L = int(6 * s + 5)
    yb = H - 1
    for x in range(-2, L + 1):
        y = yb + round((x - 2) * 0.12)
        for dz in (0, 1):
            w.setze(x + B // 2, y, dz, w.b("iron_block") if x % 3 else w.b("polished_blackstone"))
    for y in range(1, yb):
        w.setze(B // 2 + L, y, 0, w.b("chain", axis="y", waterlogged=False))
    for x in range(B // 2 + L - 1, B // 2 + L + 2):
        for z in (-1, 0, 1):
            w.setze(x, 0, z, w.b("water", level=0) if (x, z) != (B // 2 + L, 0) else w.b("water", level=0))
            w.setze(x, 1, z, w.b("cobblestone_wall") if abs(x - B // 2 - L) == 1 or abs(z) == 1 else w.b("air"))
    schornstein(w, -B // 2 - 3, 1, -T // 2, int(12 * s + 8), r=1, mat="bricks")
    return w


def klappbruecke(seed, g=2):
    """Zahnrad-Klappbrücke: eine stählerne Klappbrücke über einen Kanal, deren Klappe von riesigen, offen liegenden
    Zahnrädern in zwei Brückenhäusern hochgezogen wird – eine Hälfte steht schräg in der Luft."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = industrie(w, R)
    for x in range(-R - 2, R + 3):
        for z in range(-int(4 * s + 3), int(4 * s + 4)):
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("stone_bricks"))
            w.setze(x, 0, -int(4 * s + 4), w.b("stone_bricks"))
            w.setze(x, 0, int(4 * s + 4), w.b("stone_bricks"))
    zr = int(4 * s + 4)
    for z in range(-zr - int(4 * s), -zr + 1):
        for x in (-2, -1, 0, 1, 2):
            w.setze(x, 2, z, w.b("polished_andesite"))
    for k in range(zr + 1):
        z = -zr + k
        y = 2 + round(k * 0.9)
        for x in (-2, -1, 0, 1, 2):
            w.setze(x, y, z, w.b("iron_block") if abs(x) == 2 else w.b("spruce_planks"))
    for k in range(zr + 1):
        z = zr - k
        for x in (-2, -1, 0, 1, 2):
            w.setze(x, 2, z, w.b("iron_block") if abs(x) == 2 else w.b("spruce_planks"))
    for sz in (-1, 1):
        zh = sz * (zr + 3)
        for x in range(-4, -2):
            for z in range(zh - 2, zh + 3):
                for y in range(1, int(6 + 2 * s)):
                    if x == -4 or abs(z - zh) == 2:
                        w.setze(x, y, z, w.b("bricks"))
        zahnrad(w, -3, int(4 + s), zh, 2.2 * s + 1.5, ebene="zy", mat="waxed_cut_copper")
        kegeldach(w, -3, zh, int(6 + 2 * s), 2, Dachmat(w, ["deepslate_tile"]), form="kegel", eckig=True,
                  spitze="lightning_rod")
    return w


def standseilbahn(seed, g=2):
    """Standseilbahn: eine steile Bahnstrecke auf einem Viadukt den Hang hinauf, mit zwei schrägen, rot-gelben
    Wagen in Stufenform, einer Talstation und einer Bergstation mit Seilrad unter einem Glasdach."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    rn = Rauschen(w, 4)
    H = int(12 * s + 8)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            h = int(H * max(0, min(1, (-z + R * 0.6) / (R * 1.4))) + rn(x, 3, z) * 2)
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else w.b("stone"))
    zs = int(R * 0.8)
    for z in range(-zs, zs + 1):
        hh = int(H * max(0, min(1, (-z + R * 0.6) / (R * 1.4)))) + 2
        for x in (-1, 0, 1):
            w.setze(x, hh, z, w.b("rail", shape="north_south", waterlogged=False) if x == 0 else w.b("stone_bricks"))
            w.setze(x, hh - 1, z, w.b("stone_bricks"))
            for y in range(hh + 1, hh + 4):
                w.bloecke.pop((x, y, z), None)
    for k, zw in enumerate((-int(zs * 0.4), int(zs * 0.4))):
        hh = int(H * max(0, min(1, (-zw + R * 0.6) / (R * 1.4)))) + 3
        for dz in range(-2, 3):
            for y in range(0, 3):
                for x in (-1, 0, 1):
                    rand = abs(x) == 1 or abs(dz) == 2
                    if rand or y == 2:
                        w.setze(x, hh + y - round(dz * 0.6), zw + dz, w.b("red_concrete" if y < 2 else "yellow_concrete")
                                if not (rand and y == 1 and (dz % 2)) else w.b("glass_pane"))
    for zz, hh in ((zs + 2, 2), (-zs - 2, H + 2)):
        for x in range(-3, 4):
            for z in range(zz - 2, zz + 3):
                w.setze(x, hh - 1, z, w.b("stone_bricks"))
                if abs(x) == 3 and abs(z - zz) == 2:
                    for y in range(hh, hh + 4):
                        w.setze(x, y, z, w.b("iron_block"))
                w.setze(x, hh + 4, z, w.b("glass"))
    zahnrad(w, 0, H + 4, -zs - 3, 2 * s + 1, ebene="xz", mat="waxed_cut_copper")
    return w


def orrery(seed, g=2):
    """Orrery-Pavillon: ein offener Messingpavillon, unter dessen Kuppel ein riesiges Planetenmodell schwebt – eine
    glühende Sonne in der Mitte, Planeten aus farbigen Kugeln auf Messingarmen in Kreisbahnen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    industrie(w, R)
    rp = 6 * s + 5
    H = int(8 * s + 6)
    for x in range(-int(rp) - 1, int(rp) + 2):
        for z in range(-int(rp) - 1, int(rp) + 2):
            if math.hypot(x, z) <= rp + 0.5:
                w.setze(x, 1, z, w.b("polished_andesite") if (x + z) % 2 else w.b("smooth_stone"))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x, z = round(math.cos(a) * rp), round(math.sin(a) * rp)
        for y in range(2, H):
            w.setze(x, y, z, w.b("waxed_cut_copper"))
    from wueste_eis import kuppel
    kuppel(w, lambda x, y, z, t: w.b("waxed_cut_copper") if (x + z) % 3 == 0 else w.b("glass"), 0, 0, H, rp + 0.5,
           form="rund", spitze="gold_block")
    yc = int(H * 0.55)
    kugel(w, 0, yc, 0, 1.5 + 0.6 * s, w.b("shroomlight"))
    for y in range(2, yc - 1):
        w.setze(0, y, 0, w.b("waxed_cut_copper"))
    farben = ["gray_concrete", "orange_terracotta", "blue_concrete", "red_concrete", "yellow_terracotta",
              "light_blue_concrete"]
    for i, f in enumerate(farben):
        rb = 2.5 + i * (rp - 3) / len(farben)
        a = i * 1.7
        px, pz = round(math.cos(a) * rb), round(math.sin(a) * rb)
        traeger(w, (0, yc, 0), (px, yc, pz), "chain")
        kugel(w, px, yc, pz, 0.6 + (i % 3) * 0.35 * s, w.b(f))
        for k in range(int(rb * 6)):
            aa = k / (rb * 6) * 2 * math.pi
            if k % 4 == 0:
                w.setze(round(math.cos(aa) * rb), yc - 2, round(math.sin(aa) * rb), w.b("chain", axis="x",
                                                                                          waterlogged=False), False)
    return w


def mechkaefer(seed, g=2):
    """Mechanischer Riesenkäfer: ein gewaltiger Käfer aus Kupferplatten, Messingnieten und Glasflügeldecken mit sechs
    gelenkigen Beinen, Zangen und leuchtenden Augen, aus dessen Rücken ein kleiner Schornstein raucht."""
    w = _neu(seed)
    s = S[g]
    u = 0.9 * s + 0.5
    R = int(10 * u + 6)
    industrie(w, R)
    ku = kupfer(w)
    teile = [(ell(0, 3.4, 0, 4.0, 2.2, 3.0), lambda x, y, z, *a: ku(x, y, z)),
             (ell(4.2, 3.2, 0, 1.6, 1.4, 1.8), w.b("waxed_exposed_copper")),
             (ell(0.5, 4.6, 1.1, 3.2, 1.0, 1.4), w.b("light_blue_stained_glass")),
             (ell(0.5, 4.6, -1.1, 3.2, 1.0, 1.4), w.b("light_blue_stained_glass")),
             (ell(5.2, 3.6, 0.8, 0.35, 0.35, 0.3), w.b("redstone_lamp")),
             (ell(5.2, 3.6, -0.8, 0.35, 0.35, 0.3), w.b("redstone_lamp"))]
    for sz in (-1, 1):
        teile.append((kap((5.4, 3.0, sz * 0.8), (7.2, 2.8, sz * 1.8), 0.4, 0.25), w.b("iron_block")))
        teile.append((kap((7.2, 2.8, sz * 1.8), (7.8, 2.6, sz * 0.6), 0.3, 0.15), w.b("iron_block")))
        for lx in (-2.5, 0, 2.5):
            knie = (lx + 0.5, 4.0, sz * 4.8)
            teile.append((kap((lx, 2.6, sz * 2.4), knie, 0.45, 0.35), w.b("polished_blackstone")))
            teile.append((kap(knie, (lx + 1.0, 0, sz * 6.0), 0.35, 0.2), w.b("polished_blackstone")))
    figur(w, u, teile, (-5, -1, -7), (9, 7, 7), pos=(0, 1, 0), winkel=0.4)
    schornstein(w, round(-1.5 * u), round(5.5 * u) + 1, 0, int(2 + s), r=0, mat="black_concrete")
    return w


def gasometer(seed, g=2):
    """Gasometer: ein riesiger, runder Gasbehälter in einem filigranen Stahlgerüst aus Säulen und Ringen, daneben ein
    Gaswerk mit Retortenhaus, Rohrleitungen und Kohlenhaufen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    industrie(w, R)
    rg = 6 * s + 4
    H = int(10 * s + 8)
    cx = -int(R * 0.2)
    for y in range(1, H):
        for x, z in kreisrand(rg, cx, 0):
            w.setze(x, y, z, w.b("light_gray_concrete") if y % 4 else w.b("gray_concrete"))
    for x in range(cx - int(rg), cx + int(rg) + 1):
        for z in range(-int(rg), int(rg) + 1):
            if math.hypot(x - cx, z) <= rg:
                w.setze(x, H, z, w.b("gray_concrete"))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        x, z = round(cx + math.cos(a) * (rg + 2)), round(math.sin(a) * (rg + 2))
        for y in range(1, H + 4):
            w.setze(x, y, z, w.b("iron_block") if y % 5 else w.b("iron_bars", waterlogged=False))
    for y in (H // 2, H + 3):
        for x, z in kreisrand(rg + 2, cx, 0):
            w.setze(x, y, z, w.b("iron_bars", waterlogged=False), False)
    hx = int(R * 0.45)
    haus(w, hx, 0, 7, int(4 * s + 5) | 1, 1, ziegel(w), holz="dark_oak", H=5, dach=("deepslate_tile",),
         tuer_s="west", schorn=False)
    schornstein(w, hx + 2, 1, -int(2 * s + 3), int(10 * s + 6), r=1)
    zylinder(w, (cx + rg + 2, 3, 0), (hx - 4, 3, 0), 0.8, w.b("waxed_exposed_copper"))
    kugel(w, hx, 0, int(R * 0.55), 2 + s, w.b("coal_block"), ry=1.5 + s)
    return w


def wasserturm(seed, g=2):
    """Wasserturm: ein hoher Turm aus Backstein mit achteckigem Schaft, auf dem ein großer, genieteter Stahltank mit
    Kegeldach sitzt, außen eine Wendeltreppe, unten ein Pumpenhäuschen und Rohre."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    industrie(w, R)
    H = int(12 * s + 8)
    r = 2.5 * s + 2
    zg = ziegel(w)
    for y in range(1, H):
        for x, z in kreisrand(r):
            fen = y % 6 == 3 and (x == 0 or z == 0)
            w.setze(x, y, z, w.b("glass_pane") if fen else zg(x, y, z))
    rt = 4.5 * s + 3
    Ht = int(4 * s + 4)
    zylinder(w, (0, H, 0), (0, H + Ht, 0), rt, w.b("waxed_oxidized_copper"), hohl=True,
             nieten=w.b("waxed_weathered_cut_copper"), abstand=2)
    kegeldach(w, 0, 0, H + Ht + 1, int(rt), Dachmat(w, ["deepslate_tile"]), form="kegel", spitze="lightning_rod")
    for x, z in kreisrand(rt + 1.2):
        w.setze(x, H, z, w.b("iron_bars", waterlogged=False))
    for k in range(H * 3):
        a = k / 3 * 0.35
        y = 1 + k // 3
        if y >= H:
            break
        w.setze(round(math.cos(a) * (r + 1.2)), y, round(math.sin(a) * (r + 1.2)), w.b("iron_bars", waterlogged=False)
                if k % 3 else w.b("polished_blackstone_slab", type="top", waterlogged=False), False)
    haus(w, int(R * 0.5), 0, 5, 5, 1, ziegel(w), holz="dark_oak", H=3, dach=("deepslate_tile",), tuer_s="west",
         schorn=False)
    return w


def semaphor(seed, g=1):
    """Semaphor-Signalmast: ein hoher, schlanker Gittermast auf einem Hügel mit zwei schwenkbaren Signalarmen und
    Lampen, daneben das Telegrafenhäuschen mit Fernrohr und Signalbüchern."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, 0.4)
    H = int(12 * s + 8)
    top0 = hoehe(w, 0, 0, 10)
    for y in range(top0 + 1, top0 + H):
        for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            if y < top0 + H * 0.6 or (dx, dz) == (1, 1):
                w.setze(dx, y, dz, w.b("iron_bars", waterlogged=False))
        if y % 4 == 0:
            for dx in (-1, 0, 1):
                w.setze(dx, y, -1, w.b("iron_bars", waterlogged=False))
                w.setze(dx, y, 1, w.b("iron_bars", waterlogged=False))
    for y in range(top0 + int(H * 0.6), top0 + H + 2):
        w.setze(0, y, 0, w.b("iron_block"))
    ya = top0 + H
    for k in range(1, int(4 * s + 3)):
        w.setze(k, ya + k // 2, 0, w.b("red_concrete") if k % 2 else w.b("white_concrete"))
        w.setze(-k, ya - k // 2, 0, w.b("red_concrete") if k % 2 else w.b("white_concrete"))
    w.setze(0, ya + 2, 0, w.b("redstone_lamp"))
    hx, hz = int(R * 0.45), int(R * 0.2)
    haus(w, hx, hz, 5, 5, hoehe(w, hx, hz, 10) + 1, M(w, [("white_terracotta", 1)]), holz="spruce", H=3,
         tuer_s="west", schorn=False)
    _ = zellen
    return w


def druckerei(seed, g=1):
    """Druckerei mit Dampfpresse: eine Werkhalle mit Sheddach, darin eine große Rotationspresse mit Walzen und
    Schwungrad, Papierrollen, Setzkästen und Stapel bedruckter Bögen; ein Schornstein raucht."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    industrie(w, R)
    B, T = int(5 * s + 6), int(3 * s + 5)
    zg = ziegel(w)
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            w.setze(x, 0, z, w.b("smooth_stone"))
            for y in range(1, 5):
                if abs(x) == B or abs(z) == T:
                    fen = y == 2 and x % 3 == 0 and abs(x) < B
                    w.setze(x, y, z, w.b("glass_pane") if fen else zg(x, y, z))
    for x in range(-B, B + 1):
        k = (x + B) % 4
        for z in range(-T, T + 1):
            w.setze(x, 5 + k, z, w.b("glass") if k == 3 else w.b("deepslate_tiles"))
    for x in range(-2, 3):
        for z in (-1, 1):
            w.setze(x, 2, z, w.b("black_concrete"))
        w.setze(x, 1, 0, w.b("iron_block"))
    zahnrad(w, 3, 3, 0, 1.6 + 0.4 * s, ebene="xy", mat="iron_block")
    for k in range(3):
        w.setze(-B + 1 + k, 1, -T + 1, w.b("white_wool"))
        w.setze(-B + 1 + k, 2, -T + 1, w.b("white_wool") if k % 2 else w.b("air"))
    schornstein(w, B + 2, 1, 0, int(8 * s + 6), r=1)
    for y in (1, 2):
        w.bloecke.pop((0, y, T), None)
    return w


def zeche(seed, g=2):
    """Zeche mit Förderturm: ein hohes, stählernes Fördergerüst mit zwei großen Seilscheiben über dem Schacht, ein
    Maschinenhaus mit Fördermaschine, Kohlehalden, Loren auf Gleisen und ein Lohnhaus."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    industrie(w, R)
    H = int(14 * s + 10)
    B = int(2 * s + 2)
    for y in range(1, H):
        for sx in (-B, B):
            for sz in (-B, B):
                w.setze(sx, y, sz, w.b("iron_block") if y % 4 else w.b("polished_blackstone"))
        if y % 4 == 0:
            for d in range(-B, B + 1):
                for (x, z) in ((d, -B), (d, B), (-B, d), (B, d)):
                    w.setze(x, y, z, w.b("iron_bars", waterlogged=False), False)
    for k in range(H):
        w.setze(-B - round(k * 0.5), H - k, 0, w.b("iron_block"), False)
    for dz in (-1, 1):
        zahnrad(w, 0, H + int(2 * s + 1), dz * 1, 2 * s + 1.5, ebene="xy", mat="red_concrete", zahn="red_concrete")
    for y in range(1, H):
        w.setze(0, y, 0, w.b("chain", axis="y", waterlogged=False), False)
    mx = -int(R * 0.5)
    haus(w, mx, 0, int(4 * s + 5) | 1, int(3 * s + 5) | 1, 1, ziegel(w), holz="dark_oak", H=5,
         dach=("deepslate_tile",), tuer_s="east", schorn=False)
    traeger(w, (mx + 3, 6, 0), (-B, H, 0), "chain")
    for k in range(2 + g):
        kugel(w, int(R * 0.45), 0, -int(R * 0.4) + k * 4, 1.8 + s, w.b("coal_block"), ry=1.5 + 0.8 * s, ueber=False)
    gleis(w, -B, int(R * 0.7), B + 3, y=1)
    for k in range(2):
        w.setze(int(R * 0.3) + k * 3, 1, B + 3, w.b("rail", shape="east_west", waterlogged=False))
        w.setze(int(R * 0.3) + k * 3, 2, B + 3, w.b("coal_block"))
    return w


def dampforgel(seed, g=1):
    """Dampforgel: eine prunkvoll bemalte Jahrmarktsorgel mit Messingpfeifen, Trommeln, Glockenspiel und kleinen
    Figuren mit Taktstöcken, auf einem Wagen mit Speichenrädern, aus den Pfeifen steigt Dampf."""
    w = _neu(seed)
    s = S[g]
    R = int(9 * s + 6)
    wiese(w, R, 0.05)
    B = int(4 * s + 4)
    T = int(1.5 * s + 2)
    H = int(5 * s + 5)
    for x in range(-B, B + 1):
        for z in range(-T, T + 1):
            w.setze(x, 2, z, w.b("dark_oak_planks"))
            for y in range(3, H):
                if z == -T or abs(x) == B or y == H - 1:
                    w.setze(x, y, z, w.b("red_terracotta") if (x + y) % 4 else w.b("gold_block"))
    for i in range(-B + 1, B):
        h = H - 2 - abs(i) // 2
        for y in range(4, 4 + h):
            w.setze(i, y, -T + 1, w.b("gold_block") if i % 2 else w.b("waxed_cut_copper"))
        if i % 3 == 0:
            w.setze(i, 4 + h, -T + 1, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for k, x in enumerate((-B + 2, B - 2)):
        w.setze(x, 3, 0, w.b("note_block", instrument="basedrum", note=0, powered=False))
        w.setze(x, 4, 0, w.b("white_terracotta"))
        w.setze(x, 5, 0, w.b("yellow_terracotta"))
    for sx in (-B + 1, B - 1):
        for sz in (-T - 1, T + 1):
            for a in range(-1, 2):
                for b in range(-1, 2):
                    if abs(a) + abs(b) == 1:
                        w.setze(sx + a, 1 + b, sz, w.b("dark_oak_fence"))
            w.setze(sx, 1, sz, w.b("dark_oak_log", axis="z"))
    return w


def rohrpost(seed, g=2):
    """Rohrpost-Station: ein Postamt mit gläsernem Kuppeldach, aus dem ein Gewirr kupferner Röhren in alle Richtungen
    führt, über Stützen und Bögen zu kleinen Empfangstürmchen; Kapseln sausen hindurch."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    industrie(w, R)
    rb = 3 * s + 3
    H = int(3 * s + 4)
    for y in range(1, H):
        for x, z in kreisrand(rb):
            w.setze(x, y, z, w.b("bricks") if y % 3 else w.b("smooth_stone"))
    from wueste_eis import kuppel
    kuppel(w, lambda x, y, z, t: w.b("glass") if (x + z) % 3 else w.b("waxed_cut_copper"), 0, 0, H, rb + 0.5,
           form="rund", spitze="gold_block")
    rng = w.rng
    for i in range(int(5 + 2 * s)):
        a = i / (5 + 2 * s) * 2 * math.pi
        ex, ez = round(math.cos(a) * R * 0.75), round(math.sin(a) * R * 0.75)
        hy = int(2 + rng.random() * 3 * s)
        pts = bez((math.cos(a) * rb, H - 1, math.sin(a) * rb), (math.cos(a) * R * 0.4, H + 3 * s, math.sin(a) * R * 0.4),
                  (ex, hy + 2, ez))
        rohr(w, pts, 0.7 + 0.2 * s, 0.7 + 0.2 * s, mat=w.b("waxed_cut_copper"), rauh=0.0)
        for y in range(1, hy + 2):
            w.setze(ex, y, ez, w.b("bricks"))
        w.setze(ex, hy + 2, ez, w.b("waxed_exposed_copper"))
        k = len(pts) // 2
        w.setze(round(pts[k][0]), round(pts[k][1]) - 2, round(pts[k][2]), w.b("iron_bars", waterlogged=False), False)
    for y in (1, 2):
        w.bloecke.pop((0, y, round(rb)), None)
    return w


def ankermast(seed, g=2):
    """Luftschiff-Ankermast: ein hoher Gittermast mit Plattform, an dessen Spitze ein langes, silbernes Luftschiff mit
    Gondel und Propellern festgemacht ist, Fahrstuhl im Mast und Wartehalle am Fuß."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    industrie(w, R)
    H = int(16 * s + 10)
    for y in range(1, H):
        r = 2.2 * (1 - y / (H * 1.4))
        for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            w.setze(round(dx * r), y, round(dz * r), w.b("iron_block") if y % 4 else w.b("iron_bars",
                                                                                       waterlogged=False))
        w.setze(0, y, 0, w.b("chain", axis="y", waterlogged=False), False)
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, H, z, w.b("smooth_stone_slab", type="top", waterlogged=False))
    L = 18 * s + 10
    Rl = 3 * s + 2.5
    from steampunk2 import propeller
    huelle(w, -L / 2 - 2, H + 1, 0, L, Rl, lambda x, y, z: w.b("light_gray_concrete") if (x // 3) % 2 else
           w.b("white_concrete"))
    gx = round(-L / 2 - 2)
    for x in range(gx - 3, gx + 4):
        for z in (-1, 0, 1):
            w.setze(x, H + 1 - round(Rl) - 2, z, w.b("waxed_cut_copper"))
            if abs(z) == 1:
                w.setze(x, H + 1 - round(Rl) - 1, z, w.b("glass_pane"))
    for sz in (-1, 1):
        propeller(w, round(-L - 2), H + 1, sz * round(Rl + 1), int(1 + s), achse="x")
    haus(w, int(R * 0.5), int(R * 0.4), int(4 * s + 5) | 1, 5, 1, M(w, [("white_terracotta", 1)]), holz="spruce",
         H=4, dach=("mcw:blue_terracotta", "prismarine_brick"), tuer_s="west", schorn=False)
    return w


def uhrwerkgarten(seed, g=1):
    """Uhrwerk-Garten: ein Garten voller mechanischer Blumen aus Kupfer und Glas auf Messingstängeln, mit Zahnrad-
    blüten, einem Springbrunnen mit Pumpwerk und einer Bank unter einem Zahnradbogen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, 0.05, blumen=0.0)
    rng = w.rng
    farben = ["red_stained_glass", "orange_stained_glass", "yellow_stained_glass", "light_blue_stained_glass",
              "magenta_stained_glass"]
    for k in range(int(10 * s + 6)):
        a = rng.random() * 6.28
        d = 3 + rng.random() * (R * 0.75 - 3)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        h = int(2 + rng.random() * 4 * s)
        for y in range(1, h + 1):
            w.setze(x, y, z, w.b("waxed_cut_copper") if y < h else w.b("waxed_copper_block"))
        f = farben[k % 5]
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            w.setze(x + dx, h, z + dz, w.b(f))
        if h > 3:
            w.setze(x + 1, h // 2, z, w.b("waxed_exposed_copper"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            if math.hypot(x, z) <= 2.3:
                w.setze(x, 0, z, w.b("water", level=0) if math.hypot(x, z) < 1.6 else w.b("waxed_cut_copper"))
    w.setze(0, 1, 0, w.b("waxed_copper_block"))
    w.setze(0, 2, 0, w.b("water", level=0))
    zahnrad(w, 0, int(4 + s), int(R * 0.7), 2.5 + s, ebene="xy", mat="waxed_cut_copper")
    for x in (-1, 0, 1):
        w.setze(x, 1, int(R * 0.7) - 1, treppe(w, "spruce", "south"))
    return w


def drehscheibe(seed, g=2):
    """Lokschuppen mit Drehscheibe: eine runde Drehscheibe mit Brücke in einer Grube, von der Gleise strahlenförmig in
    einen halbrunden Ringlokschuppen mit vielen Toren führen, eine Dampflok steht auf der Scheibe."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    industrie(w, R)
    rd = 4 * s + 3
    for x in range(-int(rd) - 1, int(rd) + 2):
        for z in range(-int(rd) - 1, int(rd) + 2):
            d = math.hypot(x, z)
            if d <= rd:
                w.setze(x, 0, z, w.b("gravel") if d < rd - 1 else w.b("stone_bricks"))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
    gleis(w, -int(rd), int(rd), 0, y=1)
    n = 7
    rs = R * 0.8
    for i in range(n):
        a = math.pi + math.pi * i / (n - 1)
        for t in range(int(rd), int(rs)):
            x, z = round(math.cos(a) * t), round(math.sin(a) * t)
            w.setze(x, 1, z, w.b("rail", shape="east_west" if abs(math.cos(a)) > 0.7 else "north_south",
                                 waterlogged=False))
    zg = ziegel(w)
    for k in range(int(rs * 4)):
        a = math.pi + math.pi * k / (rs * 4)
        for r in (rs - 1, rs + 4):
            x, z = round(math.cos(a) * r), round(math.sin(a) * r)
            tor = r == rs - 1 and any(abs(a - (math.pi + math.pi * i / (n - 1))) < 0.06 for i in range(n))
            for y in range(1, 6):
                if not (tor and y < 4):
                    w.setze(x, y, z, zg(x, y, z))
        for r in np.arange(rs - 1, rs + 4.5, 0.7):
            x, z = round(math.cos(a) * r), round(math.sin(a) * r)
            w.setze(x, 6, z, w.b("deepslate_tiles"))
    from steampunk2 import zylinder as zyl
    zyl(w, (-3, 3, 0), (2, 3, 0), 1.2, w.b("black_concrete"))
    w.setze(2, 5, 0, w.b("black_concrete"))
    w.setze(2, 6, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    for x in range(-5, -2):
        for z in (-1, 0, 1):
            for y in range(2, 5):
                if abs(z) == 1 or y == 4:
                    w.setze(x, y, z, w.b("black_concrete"))
    return w


def glockenspiel(seed, g=2):
    """Glockenspiel-Turm: ein verspielter Uhrturm mit großem Zifferblatt, darunter eine Bühne mit Türen, aus denen
    zur vollen Stunde Figuren (Ritter, Bäckerin, Narr) auf einem Drehteller herausfahren; Glocken im offenen Helm."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, 0.05, art="kies")
    B = int(2.5 * s + 3)
    H = int(14 * s + 10)
    for y in range(1, H):
        for x in range(-B, B + 1):
            for z in range(-B, B + 1):
                if max(abs(x), abs(z)) == B:
                    w.setze(x, y, z, w.b("white_terracotta") if (y // 4) % 2 else w.b("calcite"))
    yu = int(H * 0.7)
    for x in range(-B + 1, B):
        for y in range(yu - B + 1, yu + B):
            d = math.hypot(x, y - yu)
            if d < B - 0.3:
                w.setze(x, y, B, w.b("gold_block") if d > B - 1.3 else w.b("white_concrete"))
    for k in range(int(B * 0.8)):
        w.setze(0, yu + k, B + 1, w.b("black_concrete"), False)
        w.setze(k // 2 + 1, yu - k // 2, B + 1, w.b("black_concrete"), False)
    yb = int(H * 0.35)
    for x in range(-B + 1, B):
        for y in range(yb, yb + 4):
            w.bloecke.pop((x, y, B), None)
            w.bloecke.pop((x, y, B - 1), None)
        w.setze(x, yb - 1, B + 1, w.b("spruce_slab", type="top", waterlogged=False))
    from erw_markt import mensch
    for k, rock in enumerate(("iron_block", "white_wool", "red_wool")):
        figur(w, 0.35 * s + 0.25, mensch(w, rock), (-2, -1, -2), (2, 6, 2), pos=(-B + 2 + k * B // 1.5, yb, B))
    for y in range(H, H + 4):
        for dx, dz in ((-B, -B), (-B, B), (B, -B), (B, B)):
            w.setze(dx, y, dz, w.b("white_terracotta"))
    w.setze(0, H + 3, 0, w.b("bell", attachment="ceiling", facing="north", powered=False))
    kegeldach(w, 0, 0, H + 4, B, Dachmat(w, ["mcw:blue_terracotta", "prismarine_brick"]), form="glocke", eckig=True,
              spitze="gold_block")
    return w


def dampfkran(seed, g=2):
    """Dampfkran am Kai: ein mächtiger, drehbarer Portalkran auf Schienen mit Kesselhaus, langem Ausleger aus
    Stahlgitter und Haken, der gerade eine Kiste aus einem Frachtkahn hebt."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = industrie(w, R)
    for x in range(-R - 2, R + 3):
        for z in range(int(R * 0.25), R + 3):
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("stone"))
        w.setze(x, 0, int(R * 0.25) - 1, w.b("stone_bricks"))
    gleis(w, -R + 2, R - 2, -1, y=1)
    gleis(w, -R + 2, R - 2, int(R * 0.2), y=1)
    Hp = int(4 * s + 4)
    for sx in (-2, 2):
        for sz in (-1, int(R * 0.2)):
            for y in range(2, Hp + 2):
                w.setze(sx, y, sz, w.b("iron_block") if y % 3 else w.b("iron_bars", waterlogged=False))
    for x in range(-3, 4):
        for z in range(-2, int(R * 0.2) + 2):
            w.setze(x, Hp + 2, z, w.b("polished_blackstone"))
    for x in range(-2, 3):
        for z in range(0, int(R * 0.2)):
            for y in range(Hp + 3, Hp + 6):
                if abs(x) == 2 or z in (0, int(R * 0.2) - 1):
                    w.setze(x, y, z, w.b("black_concrete"))
    schornstein(w, -1, Hp + 3, 1, int(4 + s), r=0, mat="black_concrete")
    L = int(10 * s + 6)
    for k in range(L):
        y = Hp + 5 + round(k * 0.45)
        z = int(R * 0.1) + k
        w.setze(0, y, z, w.b("iron_block"))
        w.setze(0, y - 1, z, w.b("iron_bars", waterlogged=False))
    ez = int(R * 0.1) + L - 1
    ey = Hp + 5 + round((L - 1) * 0.45)
    for y in range(3, ey):
        w.setze(0, y, ez, w.b("chain", axis="y", waterlogged=False))
    w.setze(0, 2, ez, w.b("barrel", facing="up", open=False))
    for i in range(-4, 5):
        for q in (-2, -1, 0, 1, 2):
            if abs(q) <= 2 * math.sqrt(max(0, 1 - (i / 4.5) ** 2)):
                w.setze(i, 0, ez + 1 + q, w.b("spruce_planks"))
                if abs(q) == 2 or abs(i) == 4:
                    w.setze(i, 1, ez + 1 + q, w.b("spruce_planks"))
    return w


def kettenkarussell(seed, g=1):
    """Dampf-Kettenkarussell: ein buntes Karussell mit gestreiftem Schirmdach, an dessen Rand Sitze an langen Ketten
    hängen, angetrieben von einer kleinen Dampfmaschine mit Schwungrad im Mittelmast."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, 0.05)
    H = int(8 * s + 6)
    for y in range(1, H):
        for x, z in kreisrand(1.2):
            w.setze(x, y, z, w.b("red_concrete") if y % 3 else w.b("gold_block"))
    rd = 5 * s + 3
    for k in range(int(rd) + 2):
        rr = rd + 1 - k
        for x, z in kreisrand(max(0.5, rr)):
            ang = math.atan2(z, x)
            w.setze(x, H + k // 2, z, w.b("red_wool") if int((ang + math.pi) * 6 / math.pi) % 2 else w.b("white_wool"))
    for i in range(int(8 + 4 * s)):
        a = i / (8 + 4 * s) * 2 * math.pi
        x, z = round(math.cos(a) * (rd + 1.5)), round(math.sin(a) * (rd + 1.5))
        for y in range(3, H):
            w.setze(x, y, z, w.b("chain", axis="y", waterlogged=False))
        w.setze(x, 2, z, w.b("spruce_slab", type="top", waterlogged=False))
    zylinder(w, (-1, 1, 2), (1, 1, 2), 1.0, w.b("black_concrete"))
    w.setze(0, 2, 2, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for x in range(-int(rd), int(rd) + 1):
        for z in range(-int(rd), int(rd) + 1):
            if math.hypot(x, z) <= rd:
                w.setze(x, 0, z, w.b("smooth_stone") if (x + z) % 2 else w.b("polished_andesite"))
    return w


def zahnrad_denkmal(seed, g=2):
    """Zahnrad-Denkmal: ein monumentales Ensemble aus fünf ineinandergreifenden Riesenzahnrädern in Kupfer, Messing
    und Eisen, schräg aufgestellt auf einem Sockel, mit einer Gedenktafel an die Erfinder."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wiese(w, R, 0.05, art="kies")
    for x in range(-int(R * 0.6), int(R * 0.6) + 1):
        for z in range(-3, 4):
            w.setze(x, 1, z, w.b("polished_andesite"))
            w.setze(x, 2, z, w.b("smooth_stone_slab", type="bottom", waterlogged=False))
    raeder = [(-5, 9, 5, "waxed_cut_copper"), (3, 8, 3.5, "gold_block"), (8.5, 12, 2.6, "iron_block"),
              (-1, 17, 3.2, "waxed_exposed_cut_copper"), (5.5, 18, 2.2, "gold_block")]
    for (x, y, r, mat) in raeder:
        zahnrad(w, round(x * s), round(y * s), 0, r * s, ebene="xy", mat=mat)
        zahnrad(w, round(x * s), round(y * s), 1, r * s, ebene="xy", mat=mat)
    for y in range(3, round(9 * s) - round(5 * s)):
        w.setze(round(-5 * s), y, 0, w.b("iron_block"))
    w.setze(0, 3, 3, w.b("gold_block"))
    w.setze(1, 3, 3, w.b("gold_block"))
    return w


UHRWERK3 = {
    "dampftraktor": ("Dampftraktor", dampftraktor),
    "balancierpumpe": ("Balancier-Pumpwerk", balancierpumpe),
    "klappbruecke": ("Zahnrad-Klappbrücke", klappbruecke),
    "standseilbahn": ("Standseilbahn", standseilbahn),
    "orrery": ("Orrery-Pavillon", orrery),
    "mechkaefer": ("Mechanischer Riesenkäfer", mechkaefer),
    "gasometer": ("Gasometer", gasometer),
    "wasserturm": ("Wasserturm", wasserturm),
    "semaphor": ("Semaphor-Signalmast", semaphor),
    "druckerei": ("Druckerei mit Dampfpresse", druckerei),
    "zeche": ("Zeche mit Förderturm", zeche),
    "dampforgel": ("Dampforgel", dampforgel),
    "rohrpost": ("Rohrpost-Station", rohrpost),
    "ankermast": ("Luftschiff-Ankermast", ankermast),
    "uhrwerkgarten": ("Uhrwerk-Garten", uhrwerkgarten),
    "drehscheibe": ("Lokschuppen mit Drehscheibe", drehscheibe),
    "glockenspiel": ("Glockenspiel-Turm", glockenspiel),
    "dampfkran": ("Dampfkran am Kai", dampfkran),
    "kettenkarussell": ("Dampf-Kettenkarussell", kettenkarussell),
    "zahnrad_denkmal": ("Zahnrad-Denkmal", zahnrad_denkmal),
}

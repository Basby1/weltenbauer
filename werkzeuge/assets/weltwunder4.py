"""Weltwunder, Teil 4: Hängende Gärten, Uhrwerkturm, Himmelspagode, Titanenschädel, Himmelsbrunnen."""

from __future__ import annotations

import math

import numpy as np

from lib import Rauschen, Verlauf, einfuegen, laub
import pracht as P
from pracht import Mat, gelaende, treppe
from skulptur import Skulptur, dreh_x, dreh_y, dreh_z, ell, kap, kasten, kegel, kreisrand, ohne, scheibe, spiegel_x, \
    torus, verbinde, zur_mitte
from motive import figur
from weltwunder import U, _r, _stil, bl, hohl, platz, sk, welt


def _wand(w, name):
    return w.b(name, up=True, north="none", south="none", east="none", west="none", waterlogged=False)


def _richtung(x, z, h):
    return "east" if x == -h else "west" if x == h else "south" if z == -h else "north"


# ============================================================================ 16 Hängende Gärten


def haengende_gaerten(seed, g=2):
    """Hängende Gärten: eine gestufte Tempelpyramide aus Terrassen mit Bogengängen, überquellenden
    Pflanzkästen, Bäumen, herabfallenden Ranken und Wasserfällen in ein großes Becken.
    Stil 1 Lehmziegel und Türkis, Stil 2 weißer Marmor mit Gold."""
    import baeume as B
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    rng = w.rng
    if st == 0:
        M = Mat(w, ["mud_bricks", "packed_mud", "bricks", "mud_bricks", "terracotta", "smooth_sandstone"],
                kontrast=0.9)
        akz, akz2, rand = "cyan_terracotta", "gold_block", "mud_brick"
        saeule = "cut_sandstone"
        baeume = ["akazie", "kirschbaum", "azaleenbaum"]
    else:
        M = Mat(w, ["polished_diorite", "calcite", "smooth_quartz", "quartz_bricks", "diorite"], kontrast=0.8)
        akz, akz2, rand = "gold_block", "light_blue_terracotta", "quartz"
        saeule = "quartz_pillar"
        baeume = ["kirschbaum", "trauerweide", "azaleenbaum"]
    stufen = 5
    B0 = _r(34 * u)
    sh = _r(8 * u, 6)
    schritt = _r(6 * u, 4)
    # Wasserbecken rundum
    for x in range(-B0 - 8, B0 + 9):
        for z in range(-B0 - 8, B0 + 9):
            m = max(abs(x), abs(z))
            if m > B0 + 1:
                if m == B0 + 8:
                    w.setze(x, 0, z, M(x, 0, z, 0.2))
                    w.setze(x, 1, z, treppe(w, rand, _richtung(x, z, B0 + 8), "bottom"))
                else:
                    w.setze(x, 0, z, w.b("water", level=0))
                    w.setze(x, -1, z, w.b("prismarine_bricks" if st == 0 else "light_blue_terracotta"))
    for k in range(stufen):
        h = B0 - k * schritt
        y0 = k * sh
        H = sh
        for y in range(y0, y0 + H):
            t = y / (stufen * sh)
            for x in range(-h, h + 1):
                for z in range(-h, h + 1):
                    m = max(abs(x), abs(z))
                    if m < h - 2:
                        if y == y0 + H - 1:
                            w.setze(x, y, z, M(x, y, z, t))
                        continue
                    if m == h:
                        ox = x if abs(x) == h else z
                        lang = z if abs(x) == h else x
                        # Bogengang: Pfeiler alle 4, dazwischen Bogen
                        pfeiler = lang % 4 == 0
                        hb = y - y0
                        bogen_frei = (not pfeiler) and hb < H - 3 and hb >= 0 and not (k == 0 and hb < 0)
                        if bogen_frei and hb < H - 3 - (1 if abs(lang % 4 - 2) == 1 else 0):
                            continue
                        if pfeiler and hb < H - 2:
                            w.setze(x, y, z, w.b(saeule, axis="y") if saeule.endswith("pillar") else w.b(saeule))
                        elif hb == H - 2:
                            w.setze(x, y, z, w.b(akz) if lang % 2 == 0 else M(x, y, z, t))
                        else:
                            w.setze(x, y, z, M(x, y, z, t))
                    elif m == h - 2:
                        w.setze(x, y, z, M(x, y, z, t))
        # Pflanzkasten an der Terrassenkante
        yt = y0 + H
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                m = max(abs(x), abs(z))
                if m == h:
                    w.setze(x, yt, z, treppe(w, rand, _richtung(x, z, h), "top") if not (abs(x) == h and abs(z) == h)
                            else w.b(akz2))
                elif m == h - 1:
                    w.setze(x, yt, z, laub(w, "azalea" if rng.random() < 0.5 else "flowering_azalea") if rng.random() < 0.7
                            else laub(w, "oak"))
                    w.setze(x, yt - 1, z, w.b("rooted_dirt"))
                elif h - schritt < m < h - 1 and k < stufen - 1:
                    w.setze(x, yt - 1, z, w.b("grass_block", snowy=False))
                    r = rng.random()
                    if r < 0.25:
                        w.setze(x, yt, z, w.b("grass"))
                    elif r < 0.35:
                        w.setze(x, yt, z, w.b(["poppy", "allium", "azure_bluet", "cornflower", "pink_tulip",
                                               "oxeye_daisy"][int(rng.integers(6))]))
        # Ranken über die Kante
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                if max(abs(x), abs(z)) == h and rng.random() < 0.35:
                    dx, dz = (1 if x == h else -1 if x == -h else 0), (1 if z == h else -1 if z == -h else 0)
                    if dx and dz:
                        continue
                    seite = {(1, 0): "west", (-1, 0): "east", (0, 1): "north", (0, -1): "south"}[(dx, dz)]
                    for kk in range(1, int(2 + rng.random() * sh * 0.8)):
                        p = (x + dx, yt - kk, z + dz)
                        if not w.frei(*p) or p[1] < 1:
                            break
                        w.setze(*p, w.b("vine", **{s: s == seite for s in ("north", "east", "south", "west")},
                                        up=False))
        # Bäume auf jeder Terrasse
        for i in range(4):
            a = i / 4 * 2 * math.pi + math.pi / 4
            d = (h - schritt / 2 - 0.5)
            tx, tz = round(math.cos(a) * d * 1.3) , round(math.sin(a) * d * 1.3)
            tx = max(-h + 2, min(h - 2, tx))
            tz = max(-h + 2, min(h - 2, tz))
            if k < stufen - 1:
                einfuegen(w, B.ARTEN[baeume[(k + i) % 3]][1](int(rng.integers(1, 10 ** 6)), 0), tx, yt - 1, tz)
    # Krone: Tempelchen mit Kuppel
    ytop = stufen * sh
    hk = B0 - (stufen - 1) * schritt - 3
    for x in range(-hk, hk + 1):
        for z in range(-hk, hk + 1):
            if max(abs(x), abs(z)) == hk and (x + z) % 2 == 0:
                for y in range(ytop, ytop + 5):
                    w.setze(x, y, z, w.b(saeule, axis="y") if saeule.endswith("pillar") else w.b(saeule))
    for x, z in scheibe(hk + 1):
        if max(abs(x), abs(z)) <= hk + 1:
            w.setze(x, ytop + 5, z, M(x, ytop + 5, z, 0.9))
    for y in range(0, hk + 2):
        r = math.sqrt(max(0, (hk + 1) ** 2 - y * y))
        for x, z in kreisrand(r):
            w.setze(x, ytop + 6 + y, z, w.b(akz) if st else w.b("waxed_oxidized_cut_copper"))
    # Wasserfälle von der obersten Terrasse
    for (x, z) in ((0, B0 - (stufen - 1) * schritt), (0, -(B0 - (stufen - 1) * schritt)),
                   (B0 - (stufen - 1) * schritt, 0), (-(B0 - (stufen - 1) * schritt), 0)):
        w.setze(x, (stufen - 1) * sh + sh, z, w.b("water", level=0))
    # Prunktreppe Süd
    for k in range(stufen * sh):
        z = B0 + 7 - k * (schritt * stufen) // (stufen * sh) if False else None
    for k in range(sh * 2):
        for x in range(-3, 4):
            w.setze(x, k, B0 + 1 + (sh * 2 - k) // 2 * 0 + 0, w.b("air")) if False else None
    hohl(w, 3)
    return w


# ============================================================================ 17 Uhrwerkturm


def _zahnrad(S, cx, cy, R, zaehne, dicke, etikett, achse="z"):
    """Zahnrad in der x-y-Ebene (achse z) bei (cx, cy), lokale z-Dicke ±dicke."""
    def f(X, Y, Z):
        dx, dy = X - cx, Y - cy
        r = np.hypot(dx, dy)
        a = np.arctan2(dy, dx)
        zahn = (np.cos(a * zaehne) > 0.2) & (r < R + 1.2) & (r > R - 0.4)
        kranz = (r < R) & (r > R * 0.72)
        nabe = r < R * 0.28
        speiche = (r < R) & ((np.abs(np.sin(a * 3)) < 0.18) | (np.abs(np.cos(a * 3)) < 0.18 * 0)) & (r > R * 0.2)
        return (np.abs(Z) <= dicke) & (zahn | kranz | nabe | speiche)
    S.plus(f, etikett)


def uhrwerkturm(seed, g=2):
    """Uhrwerkturm: schlanker Riesenturm mit vier Zifferblättern, offen liegendem Getriebe aus Zahnrädern an
    den Flanken, Glockenstube und Kupferhelm. Stil 1 Backstein und Messing, Stil 2 Schwarzeisen und Gold."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    if st == 0:
        stil = P.Stil(w, wand="backstein", sockel="graustein", gesims="stone_brick", dach="kupfer", holz="spruce",
                      laeden=False, ecke=["polished_andesite", "stone_bricks"])
        zif, zahl, zeiger = "smooth_quartz", "black_concrete", "gold_block"
        zahnr = Mat(w, ["waxed_cut_copper", "waxed_exposed_cut_copper", "gold_block", "waxed_copper_block"])
        boden = Mat(w, "graustein")
        muster = ["polished_andesite", "bricks", "gold_block"]
    else:
        stil = P.Stil(w, wand="schwarzstein", sockel="tiefenschiefer", gesims="polished_blackstone_brick",
                      dach="schwarz", holz="dark_oak", laeden=False, ecke=["gilded_blackstone", "polished_blackstone"])
        zif, zahl, zeiger = "white_concrete", "gold_block", "gold_block"
        zahnr = Mat(w, ["gold_block", "raw_gold_block", "waxed_cut_copper", "gold_block"])
        boden = Mat(w, "schwarzstein")
        muster = ["polished_blackstone", "polished_blackstone_bricks", "gold_block"]
    h = _r(7 * u)
    H = _r(62 * u)
    y0 = platz(w, _r(22 * u), boden, rand="stone_brick" if st == 0 else "polished_blackstone_brick", muster=muster,
               akzent="chiseled_stone_bricks" if st == 0 else "chiseled_polished_blackstone", lichter="lantern",
               pfosten="stone_brick_wall" if st == 0 else "polished_blackstone_wall")
    # Schaft in drei Abschnitten mit Gesimsen
    P.gebaeude(w, stil, -h - 2, -h - 2, h + 2, h + 2, y0=y0, etagen=2, eh=6, dach="flach", gauben=False, kamine=0,
               pilaster=3)
    yb = y0 + 1 + 12 + 1
    for y in range(yb, yb + H):
        t = (y - yb) / H
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                m = max(abs(x), abs(z))
                if m == h:
                    ecke = abs(x) == h and abs(z) == h
                    lang = z if abs(x) == h else x
                    fen = abs(lang) <= 1 and (y - yb) % 9 in (3, 4, 5) and t < 0.7
                    if ecke:
                        w.setze(x, y, z, w.b(stil.ecke[(y // 2) % 2]))
                    elif fen:
                        w.setze(x, y, z, w.b("glass_pane", north=abs(x) == h, south=abs(x) == h, east=abs(z) == h,
                                             west=abs(z) == h, waterlogged=False))
                    else:
                        w.setze(x, y, z, stil.wand(x, y, z, t))
                elif (y - yb) % 9 == 0:
                    w.setze(x, y, z, w.b(f"{stil.holz}_planks"))
        if (y - yb) % 18 == 17:
            for x in range(-h - 1, h + 2):
                for z in range(-h - 1, h + 2):
                    if max(abs(x), abs(z)) == h + 1 and not (abs(x) == h + 1 and abs(z) == h + 1):
                        w.setze(x, y, z, treppe(w, stil.gesims, _richtung(x, z, h + 1), "top"))
    # Uhrgeschoss (breiter)
    yu = yb + H
    hu = h + 2
    Hu = 2 * hu + 3
    for y in range(yu, yu + Hu):
        for x in range(-hu, hu + 1):
            for z in range(-hu, hu + 1):
                if max(abs(x), abs(z)) == hu:
                    w.setze(x, y, z, w.b(stil.ecke[0]) if abs(x) == hu and abs(z) == hu else stil.wand(x, y, z, 0.8))
    for x in range(-hu - 1, hu + 2):
        for z in range(-hu - 1, hu + 2):
            if max(abs(x), abs(z)) == hu + 1 and not (abs(x) == hu + 1 and abs(z) == hu + 1):
                w.setze(x, yu, z, treppe(w, stil.gesims, _richtung(x, z, hu + 1)))
                w.setze(x, yu + Hu - 1, z, treppe(w, stil.gesims, _richtung(x, z, hu + 1), "top"))
    cy = yu + Hu // 2
    Rz = hu - 1.2
    for seite in range(4):
        for a in range(-hu + 1, hu):
            for y in range(yu + 1, yu + Hu - 1):
                lx, ly = a, y - cy
                r = math.hypot(lx, ly)
                if r > Rz + 0.5:
                    continue
                if seite == 0:
                    p = (a, y, hu + 1)
                elif seite == 1:
                    p = (a, y, -hu - 1)
                elif seite == 2:
                    p = (hu + 1, y, a)
                else:
                    p = (-hu - 1, y, a)
                ang = math.atan2(ly, lx)
                marke = r > Rz - 1.6 and abs(math.sin(ang * 6)) < 0.25
                rand = r > Rz - 0.5
                zeig1 = (abs(lx) < 0.6 and 0 <= ly <= Rz * 0.8)
                zeig2 = (abs(ly + lx * 0.2) < 0.6 and 0 <= lx <= Rz * 0.55)
                if rand:
                    b = w.b(zeiger)
                elif zeig1 or zeig2 or r < 1:
                    b = w.b(zeiger if st == 1 else "black_concrete")
                elif marke:
                    b = w.b(zahl)
                else:
                    b = w.b(zif)
                w.setze(*p, b)
    # Glockenstube mit Bögen und Glocke
    yg = yu + Hu
    for y in range(yg, yg + _r(8 * u)):
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                if max(abs(x), abs(z)) == h and (abs(x) == h and abs(z) == h or y == yg or (abs(x if abs(z) == h else z) % 3 == 0)):
                    w.setze(x, y, z, w.b(stil.ecke[0]))
    w.setze(0, yg + _r(8 * u) - 2, 0, w.b("bell", attachment="ceiling", facing="north", powered=False))
    for x in range(-h, h + 1):
        for z in range(-h, h + 1):
            w.setze(x, yg - 1, z, w.b(f"{stil.holz}_planks"))
    P.walmdach(w, stil.dach, -h, -h, h, h, yg + _r(8 * u) - 1, ue=1, steil=True)
    spitze = yg + _r(8 * u) + h * 2 + 1
    for k in range(_r(8 * u)):
        w.setze(0, spitze + k, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False) if k == _r(8 * u) - 1
                else w.b(zeiger) if k % 3 == 0 else _wand(w, "stone_brick_wall" if st == 0 else "polished_blackstone_wall"))
    # Zahnräder an Ost- und Westflanke
    rng = w.rng
    for sx in (-1, 1):
        S = Skulptur(w, 1.0)
        S.mat("z", sk(zahnr, yb, yb + H))
        S.mat("a", bl(w, "chain" if False else (stil.ecke[1])))
        raeder = [(0, H * 0.25, 6.0 * u, 14), (5.5 * u, H * 0.42, 4.0 * u, 10), (-4 * u, H * 0.58, 5.0 * u, 12),
                  (2 * u, H * 0.75, 3.2 * u, 8)]
        for (cx, cyr, R, n) in raeder:
            _zahnrad(S, cx, yb + cyr, R, n, 0.5, "z")
        if sx > 0:
            S.rendern((-10 * u - 2, yb, -1), (10 * u + 2, yb + H, 1), versatz=(sx * (h + 1.5), 0, 0),
                      dreh=dreh_y(math.pi / 2))
        else:
            S.rendern((-10 * u - 2, yb, -1), (10 * u + 2, yb + H, 1), versatz=(sx * (h + 1.5), 0, 0),
                      dreh=dreh_y(-math.pi / 2))
    hohl(w, 2)
    return w


# ============================================================================ 18 Himmelspagode


def himmelspagode(seed, g=2):
    """Himmelspagode: neun Geschosse mit Holzgalerien und geschwungenen Dächern mit hochgezogenen Ecken,
    gekrönt von einer goldenen Spitze mit Ringen. Stil 1 Rot und Grün, Stil 2 Schwarz, Gold und Jade."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    if st == 0:
        wand = Mat(w, ["white_terracotta", "smooth_quartz", "white_terracotta", "calcite"], kontrast=0.5)
        saeule = "red_concrete" if False else "stripped_mangrove_log"
        dach = P.Dach(w, ["dark_prismarine", "prismarine_brick", "deepslate_tile"]) if False else \
            P.Dach(w, ["deepslate_tile", "deepslate_tile", "polished_blackstone_brick"])
        trim, gold, holz = "red_terracotta", "gold_block", "dark_oak"
        sockel = Mat(w, "graustein")
        laterne = "lantern"
    else:
        wand = Mat(w, ["black_terracotta", "gray_terracotta", "black_terracotta", "polished_blackstone"], kontrast=0.5)
        saeule = "stripped_dark_oak_log"
        dach = P.Dach(w, ["waxed_oxidized_cut_copper", "waxed_weathered_cut_copper", "waxed_oxidized_cut_copper"])
        trim, gold, holz = "gold_block", "gold_block", "dark_oak"
        sockel = Mat(w, "schwarzstein")
        laterne = "soul_lantern"
    stock = 9
    h0 = _r(12 * u)
    eh = _r(6 * u, 5)
    # Sockel-Terrasse
    T = h0 + _r(7 * u)
    for k in range(3):
        for x in range(-T + k, T - k + 1):
            for z in range(-T + k, T - k + 1):
                if max(abs(x), abs(z)) == T - k:
                    w.setze(x, k, z, treppe(w, "stone_brick" if st == 0 else "polished_blackstone_brick",
                                            _richtung(x, z, T - k)))
                else:
                    w.setze(x, k, z, sockel(x, k, z, 0.3))
    y = 3
    for s in range(stock):
        h = max(3, h0 - round(s * (h0 - 3) / (stock - 1)))
        hh = eh if s else eh + 2
        for yy in range(y, y + hh):
            for x in range(-h, h + 1):
                for z in range(-h, h + 1):
                    m = max(abs(x), abs(z))
                    if m == h:
                        lang = z if abs(x) == h else x
                        if abs(x) == h and abs(z) == h or lang % 3 == 0:
                            w.setze(x, yy, z, w.b(saeule, axis="y"))
                        elif yy == y + hh - 1:
                            w.setze(x, yy, z, w.b(trim))
                        elif yy - y in (1, 2) and abs(lang) % 3 == 1 + (s % 2):
                            w.setze(x, yy, z, w.b(f"{holz}_trapdoor", facing="north", half="bottom", open=True,
                                                  powered=False, waterlogged=False) if False else
                                    w.b("glass_pane", north=abs(x) == h, south=abs(x) == h, east=abs(z) == h,
                                        west=abs(z) == h, waterlogged=False))
                        else:
                            w.setze(x, yy, z, wand(x, yy, z, 0.5))
                    elif yy == y:
                        w.setze(x, yy, z, w.b(f"{holz}_planks"))
        # Galerie mit Geländer
        for x in range(-h - 1, h + 2):
            for z in range(-h - 1, h + 2):
                if max(abs(x), abs(z)) == h + 1:
                    w.setze(x, y - 1, z, w.b(f"{holz}_slab", type="top", waterlogged=False))
                    if s:
                        w.setze(x, y, z, w.b(f"{holz}_fence", north=abs(x) == h + 1, south=abs(x) == h + 1,
                                             east=abs(z) == h + 1, west=abs(z) == h + 1, waterlogged=False))
        # geschwungenes Dach: flach auslaufend (Neigung 1:2), Ecken hochgezogen mit Goldspitze
        ue = 4 if s < stock - 1 else 3
        yd = y + hh
        A = h + ue
        k = 0
        while A - 2 * k >= (h if s < stock - 1 else 0):
            for a in (A - 2 * k, A - 2 * k - 1):
                if a < 0:
                    continue
                for x in range(-a, a + 1):
                    for z in range(-a, a + 1):
                        if max(abs(x), abs(z)) != a:
                            continue
                        if a == 0 or (abs(x) == a and abs(z) == a):
                            w.setze(x, yd + k, z, dach.voll(x, yd + k, z))
                        elif a == A - 2 * k:
                            w.setze(x, yd + k, z, dach.platte(x, yd + k, z))
                        else:
                            w.setze(x, yd + k, z, dach.treppe(x, yd + k, z, _richtung(x, z, a)))
            k += 1
        for sx in (-1, 1):
            for sz in (-1, 1):
                for q in range(2):
                    w.setze(sx * (A - q), yd + q, sz * (A - q), dach.voll(sx * (A - q), yd + q, sz * (A - q)))
                w.setze(sx * A, yd + 1, sz * A, dach.voll(sx * A, yd + 1, sz * A))
                w.setze(sx * A, yd + 2, sz * A, w.b(gold))
        # Traufunterseite
        for x in range(-A, A + 1):
            for z in range(-A, A + 1):
                if max(abs(x), abs(z)) == A and not (abs(x) == A and abs(z) == A):
                    w.setze(x, yd - 1, z, w.b(f"{holz}_slab", type="top", waterlogged=False), ueberschreiben=False)
        # Laternen an den Ecken
        for sx in (-1, 1):
            for sz in (-1, 1):
                w.setze(sx * (A - 1), yd - 1, sz * (A - 1), w.b(laterne, hanging=True, waterlogged=False))
        y = yd + (k if s < stock - 1 else k + 1)
    # Goldene Spitze mit Ringen
    for k in range(_r(12 * u)):
        w.setze(0, y + k, 0, w.b(gold) if k % 3 else w.b("chain", axis="y", waterlogged=False))
        if k % 3 == 0 and k < _r(9 * u):
            for x, z in kreisrand(1.4):
                w.setze(x, y + k, z, w.b(gold))
    w.setze(0, y + _r(12 * u), 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    hohl(w, 2)
    return w


# ============================================================================ 19 Titanenschädel


def titanenschaedel(seed, g=2):
    """Titanenschädel: ein riesiger Schädel ragt aus dem Boden, das offene Maul ist der Eingang zu einer Höhle,
    in den Augenhöhlen glimmt es. Stil 1 bemooster Stein im Dschungel, Stil 2 gebleichter Knochen in der Wüste."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    rng = w.rng
    if st == 0:
        K = Mat(w, ["mossy_cobblestone", "mossy_stone_bricks", "stone", "andesite", "cobblestone", "tuff"],
                kontrast=1.2)
        auge, boden_art = "shroomlight", "wald"
    else:
        K = Mat(w, ["bone_block", "calcite", "bone_block", "smooth_sandstone", "diorite"], kontrast=0.9)
        auge, boden_art = "magma_block", "sand"
    s = 2.4 * u
    S = Skulptur(w, s)
    S.mat("k", sk(K, 0, 26 * s))
    S.mat("a", bl(w, auge))
    S.mat("z", sk(Mat(w, ["bone_block", "calcite", "smooth_quartz"]), 0, 10))
    # Hirnschale, Wangenknochen, Oberkiefer
    schale = ell(0, 12, -2, 10, 9.5, 11)
    S.plus(schale, "k")
    S.plus(spiegel_x(ell(6.2, 6.5, 4.5, 3.4, 3.0, 4.0)), "k")
    S.plus(ell(0, 4.5, 6.0, 6.0, 3.6, 4.6), "k")
    # Unterkiefer, halb im Boden
    S.plus(ell(0, -1.2, 5.0, 7.0, 2.2, 6.0), "k")
    # Zähne
    for i in range(-4, 5):
        x = i * 1.25
        z = 9.4 - abs(i) * 0.35
        S.plus(kap((x, 3.1, z), (x, 1.2, z + 0.1), 0.55, 0.35), "z")
        S.plus(kap((x, 0.0, z - 0.2), (x, 1.6, z), 0.5, 0.3), "z")
    S.minus(ell(0, 1.8, 7.5, 4.2, 1.8, 3.4))                           # Maul (Höhleneingang)
    S.minus(kap((0, 1.8, 6.0), (0, 2.2, -6.0), 3.4, 3.0))                # Höhle
    S.mat("d", bl(w, "black_concrete" if st == 0 else "blackstone"))
    S.plus(spiegel_x(kap((-6.5, 12.6, 7.6), (-1.2, 12.0, 8.6), 1.3, 1.1)), "k")   # Brauenwulst
    for sx in (-1, 1):
        S.plus(ell(sx * 3.9, 10.0, 5.6, 3.0, 2.7, 2.0), "d")             # dunkler Grund
        S.minus(ell(sx * 3.9, 10.0, 8.0, 2.9, 2.6, 2.6))                 # Augenhöhlen
        S.plus(ell(sx * 3.9, 9.8, 5.9, 1.0, 1.0, 0.7), "a")
    S.plus(lambda X, Y, Z: (np.abs(X) < 1.5 - (Y - 5.6) * 0.3) & (Y > 5.6) & (Y < 8.6) & (Z > 7.4) & (Z < 9.2), "d")
    S.minus(lambda X, Y, Z: (np.abs(X) < 1.5 - (Y - 5.6) * 0.3) & (Y > 5.6) & (Y < 8.6) & (Z > 8.4))   # Nase
    S.rendern((-12, -3, -14), (12, 23, 12))
    # Boden
    gelaende(w, _r(42 * u), art=boden_art, dichte=0.9)
    if st == 0:
        import baeume as B
        # Bewuchs auf dem Schädel
        oben = {}
        for (x, y, z) in list(w.bloecke):
            if y > oben.get((x, z), -1):
                oben[(x, z)] = y
        for (x, z), y in oben.items():
            if y > 8 and rng.random() < 0.5:
                w.setze(x, y + 1, z, w.b("moss_carpet") if rng.random() < 0.7 else laub(w, "jungle"))
            if y > 20 * u and rng.random() < 0.004:
                einfuegen(w, B.ARTEN["dschungelriese"][1](int(rng.integers(1, 10 ** 6)), 0), x, y, z)
        B.ranken(w, set(w.bloecke.values()) - {0}, 0.04, 8, min_y=3) if False else None
        for (x, y, z), b in list(w.bloecke.items()):
            if y > 4 and rng.random() < 0.015:
                for dx, dz, sd in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
                    if w.frei(x + dx, y, z + dz):
                        for k in range(int(2 + rng.random() * 8)):
                            if not w.frei(x + dx, y - k, z + dz):
                                break
                            w.setze(x + dx, y - k, z + dz, w.b("vine", **{q: q == sd for q in
                                                                         ("north", "east", "south", "west")}, up=False))
                        break
    else:
        r_n = Rauschen(w, 7)
        for x, z in scheibe(40 * u):
            hh = (r_n(x, 0, z) - 0.45) * 9 * u
            for y in range(1, int(hh) + 1):
                w.setze(x, y, z, w.b("sand"), ueberschreiben=False)
    # Fackeln am Eingang
    for sx in (-1, 1):
        x, z = round(sx * 6 * s), round(10.5 * s)
        for y in range(1, 4):
            w.setze(x, y, z, _wand(w, "cobblestone_wall" if st == 0 else "sandstone_wall") if y < 3 else
                    w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    hohl(w, 2)
    return w


# ============================================================================ 20 Himmelsbrunnen


def himmelsbrunnen(seed, g=2):
    """Himmelsbrunnen: ein monumentaler Kaskadenbrunnen – großes Becken, drei Schalen übereinander,
    vier Statuen mit erhobenen Armen und ein Säulenkranz. Stil 1 Marmor und Gold, Stil 2 Prismarin und Kupfer."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    if st == 0:
        M = Mat(w, "marmor")
        K = Mat(w, ["smooth_quartz", "calcite", "polished_diorite", "quartz_bricks"], kontrast=0.6)
        gold, rand, saeule = "gold_block", "quartz", "quartz_pillar"
        muster = ["polished_diorite", "quartz_bricks", "gold_block"]
        licht = "lantern"
    else:
        M = Mat(w, "prismarin")
        K = Mat(w, ["waxed_oxidized_copper", "waxed_weathered_copper", "waxed_oxidized_cut_copper"], kontrast=1.0)
        gold, rand, saeule = "waxed_cut_copper", "prismarine_brick", "prismarine_bricks"
        muster = ["dark_prismarine", "prismarine_bricks", "sea_lantern"]
        licht = "sea_lantern"
    Rb = 32 * u
    Rp = _r(Rb + 10 * u)
    y0 = platz(w, Rp, M, rand=rand, muster=muster, akzent="chiseled_quartz_block" if st == 0 else "sea_lantern",
               lichter="lantern", pfosten="diorite_wall" if st == 0 else "prismarine_wall", strahlen=10)
    # Hauptbecken
    for x, z in scheibe(Rb + 1):
        d = math.hypot(x, z)
        if d > Rb - 1:
            for y in range(y0, y0 + 2):
                w.setze(x, y, z, M(x, y, z, 0.5))
            w.setze(x, y0 + 2, z, w.b(f"{rand}_slab", type="bottom", waterlogged=False))
        else:
            w.setze(x, y0, z, w.b("water", level=0))
            w.setze(x, y0 - 1, z, w.b(muster[1]) if int(d) % 4 else w.b(muster[2]))
    # Säule mit drei Schalen
    yy = y0
    S = Skulptur(w, 1.0)
    S.mat("m", sk(M, y0, y0 + 40 * u))
    S.mat("g", bl(w, gold))
    S.mat("l", bl(w, licht))
    hs = [15 * u, 12 * u, 10 * u]
    rs = [17 * u, 12 * u, 7 * u]
    y = y0
    schalen = []
    for i in range(3):
        S.plus(kap((0, y, 0), (0, y + hs[i], 0), 2.6 * u - i * 0.5, 2.0 * u - i * 0.4), "m")
        S.plus(torus(0, y + hs[i] * 0.5, 0, 2.6 * u - i * 0.5, 0.5, achse="y"), "g")
        y += hs[i]
        S.plus(ohne(lambda X, Y, Z, y=y, r=rs[i]: (Y >= y - r * 0.35) & (Y <= y + 1) &
                    (X * X + Z * Z <= (r * (1 - (y + 1 - Y) / (r * 0.6))) ** 2 + 4),
                    lambda X, Y, Z, y=y, r=rs[i]: (Y > y - 0.2) & (X * X + Z * Z < (r - 1.2) ** 2)), "m")
        S.plus(torus(0, y + 0.6, 0, rs[i] - 0.4, 0.6, achse="y"), "g")
        schalen.append((y, rs[i]))
    S.plus(ell(0, y + 2.5, 0, 2.2 * u, 2.2 * u, 2.2 * u), "l")
    S.rendern((-rs[0] - 2, y0, -rs[0] - 2), (rs[0] + 2, y + 6 * u, rs[0] + 2))
    # Wasser in den Schalen und Überlauf
    for (ys, r) in schalen:
        for x, z in scheibe(r - 1.7):
            w.setze(x, int(ys) + 0, z, w.b("water", level=0))
        for a in range(8):
            ang = a / 8 * 2 * math.pi
            x, z = round(math.cos(ang) * (r + 0.2)), round(math.sin(ang) * (r + 0.2))
            w.setze(x, int(ys) + 1, z, w.b("water", level=0))
    # Statuen auf Sockeln im Becken
    for i in range(4):
        a = i / 4 * 2 * math.pi + math.pi / 4
        cx, cz = math.cos(a) * Rb * 0.62, math.sin(a) * Rb * 0.62
        for x in range(round(cx) - 2, round(cx) + 3):
            for z in range(round(cz) - 2, round(cz) + 3):
                for yy in range(y0, y0 + 4):
                    w.setze(x, yy, z, w.b(gold) if yy == y0 + 3 and (abs(x - round(cx)) == 2 or abs(z - round(cz)) == 2)
                            else M(x, yy, z, 0.6))
        Sf = Skulptur(w, 1.25 * u)
        Sf.mat("k", sk(K, y0, y0 + 25 * u))
        Sf.mat("a", bl(w, gold))
        Sf.mat("d", bl(w, gold))
        Sf.mat("g", bl(w, licht))
        figur(Sf, "elf", "arme_hoch")
        Sf.rendern((-6, -1, -4), (6, 26, 4), versatz=(round(cx) + 0.5, y0 + 4.01, round(cz) + 0.5),
                   dreh=dreh_y(-a - math.pi / 2))
    # Säulenkranz
    n = 20
    Rk = Rb + 5 * u
    Hs = _r(15 * u)
    for i in range(n):
        a = i / n * 2 * math.pi
        x, z = round(math.cos(a) * Rk), round(math.sin(a) * Rk)
        for yy in range(y0, y0 + Hs):
            w.setze(x, yy, z, w.b(saeule, axis="y") if saeule.endswith("pillar") else w.b(saeule))
        w.setze(x, y0 + Hs, z, w.b(gold))
        w.setze(x, y0 + Hs + 1, z, w.b(licht, hanging=False, waterlogged=False) if licht == "lantern" else w.b(licht))
    hohl(w, 2)
    return w


TEIL4 = {
    "haengende_gaerten": ("Hängende Gärten", haengende_gaerten),
    "uhrwerkturm": ("Uhrwerkturm", uhrwerkturm),
    "himmelspagode": ("Himmelspagode", himmelspagode),
    "titanenschaedel": ("Titanenschädel", titanenschaedel),
    "himmelsbrunnen": ("Himmelsbrunnen", himmelsbrunnen),
}


def _alle():
    from weltwunder import WELTWUNDER as T1
    from weltwunder2 import TEIL2
    from weltwunder3 import TEIL3
    return {**T1, **TEIL2, **TEIL3, **TEIL4}


WELTWUNDER_ALLE = _alle()

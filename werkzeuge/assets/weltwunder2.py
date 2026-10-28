"""Weltwunder, Teil 2: Sonnenpyramide, Titanenhand, Frostkristall, Vulkanfeste, Drachengebein."""

from __future__ import annotations

import math

import numpy as np

from lib import Rauschen, Verlauf, laub
from pracht import Mat, gelaende, treppe
from skulptur import Skulptur, dreh_x, dreh_y, dreh_z, ell, kap, kasten, kegel, kreisrand, scheibe, spiegel_x, torus, \
    zur_mitte
from weltwunder import U, _r, _stil, bl, hohl, mix, platz, sk, welt


# ============================================================================ 6 Sonnenpyramide


def _loewe(w, S, x0, z0, y0, s, blick):
    """Liegender Wächterlöwe (Skulptur in lokalen Einheiten, Blick in +z)."""
    S.plus(ell(0, 2.2, -2.0, 2.6, 2.2, 5.2), "k")              # Leib
    S.plus(ell(0, 4.8, 3.2, 2.4, 2.6, 2.2), "k")               # Brust/Mähne
    S.plus(ell(0, 6.6, 4.4, 1.8, 1.9, 1.9), "m")               # Mähne
    S.plus(ell(0, 6.3, 5.6, 1.25, 1.35, 1.5), "k")             # Kopf
    S.plus(kap((0, 5.9, 6.6), (0, 5.6, 7.3), 0.7), "k")         # Schnauze
    S.plus(spiegel_x(kap((1.4, 0.7, 2.6), (1.3, 0.7, 7.0), 0.75)), "k")   # Vorderpranken
    S.plus(spiegel_x(ell(1.8, 1.4, -4.8, 1.4, 1.4, 2.0)), "k")  # Hinterläufe
    S.plus(kap((0, 0.8, -7.0), (2.6, 0.7, -8.6), 0.45), "k")    # Schwanz
    S.plus(spiegel_x(ell(0.55, 6.8, 6.75, 0.25, 0.25, 0.2)), "a")   # Augen
    S.plus(kasten(-3.4, -0.6, -9.5, 3.4, 0.0, 8.6), "s")        # Postament


def sonnenpyramide(seed, g=2):
    """Sonnenpyramide: glatte Riesenpyramide mit Farbbändern, goldenem Schlussstein, Prunktreppe zu einem
    Säulenportal, Obelisken und Wächterlöwen. Stil 1 Sandstein und Gold, Stil 2 Nachtpyramide aus Obsidian."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    if st == 0:
        M = Mat(w, ["sandstone", "cut_sandstone", "smooth_sandstone", "sandstone", "smooth_sandstone", "end_stone"],
                kontrast=1.0)
        tr = ["sandstone", "smooth_sandstone", "sandstone", "smooth_sandstone"]
        band = ["red_sandstone", "smooth_red_sandstone"]
        band_voll, band2 = "blue_terracotta", "orange_terracotta"
        gold, spitze, licht = "gold_block", "raw_gold_block", "lantern"
        boden = Mat(w, "sandstein")
        saeule = "cut_sandstone"
        kat = ["chiseled_sandstone", "cut_sandstone"]
    else:
        M = Mat(w, ["obsidian", "polished_blackstone", "blackstone", "polished_blackstone_bricks",
                    "polished_deepslate"], kontrast=1.0)
        tr = ["polished_blackstone", "polished_blackstone_brick", "blackstone", "polished_deepslate"]
        band = ["prismarine_brick", "dark_prismarine"]
        band_voll, band2 = "lapis_block", "gold_block"
        gold, spitze, licht = "gold_block", "crying_obsidian", "soul_lantern"
        boden = Mat(w, "schwarzstein")
        saeule = "polished_blackstone_bricks"
        kat = ["chiseled_polished_blackstone", "gilded_blackstone"]
    Bh = _r(36 * u, 22)
    r_t = Rauschen(w, 3)
    # Platz
    P = Bh + _r(16 * u)
    for x in range(-P, P + 1):
        for z in range(-P, P + 1):
            rnd = max(abs(x), abs(z))
            b = boden(x, 0, z, 0.3) if rnd < P else w.b(kat[1])
            if rnd % 6 == 0 and rnd > Bh:
                b = w.b(kat[0])
            w.setze(x, 0, z, b)
    # Pyramide
    gold_ab = int(Bh * 0.86)
    for k in range(Bh + 1):
        y = 1 + k
        h = Bh - k
        bandreihe = k % 8 in (5, 6) and k < gold_ab
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                rnd = max(abs(x), abs(z)) == h
                if not rnd:
                    if max(abs(x), abs(z)) >= h - 2:
                        w.setze(x, y, z, M(x, y, z, k / Bh))
                    continue
                if k >= gold_ab:
                    mat = None
                    if abs(x) == h and abs(z) == h:
                        w.setze(x, y, z, w.b(gold))
                        continue
                    f = "east" if x == -h else "west" if x == h else "south" if z == -h else "north"
                    w.setze(x, y, z, treppe(w, "smooth_quartz" if st == 0 else "polished_blackstone_brick", f)
                            if False else w.b(gold) if h == 0 else treppe(w, "cut_copper" if False else
                                                                             ("smooth_sandstone" if st == 0
                                                                              else "polished_blackstone"), f))
                    continue
                if abs(x) == h and abs(z) == h:
                    w.setze(x, y, z, w.b(band_voll) if bandreihe else M(x, y, z, k / Bh))
                    continue
                f = "east" if x == -h else "west" if x == h else "south" if z == -h else "north"
                if bandreihe:
                    m = band[k % 2]
                else:
                    m = tr[min(len(tr) - 1, int((r_t(x, y, z) * 0.7 + k / Bh * 0.5) * len(tr) * 0.8))]
                w.setze(x, y, z, treppe(w, m, f))
    # Goldschicht: Stufen der Spitze vergolden
    for (x, y, z), b in list(w.bloecke.items()):
        if y > gold_ab and w.P.name(b).endswith("_stairs"):
            props = dict(w.P.eintraege[b][1])
            w.setze(x, y, z, w.b("gold_block") if (x + z + y) % 5 == 0 else
                    treppe(w, "smooth_sandstone" if st == 0 else "polished_blackstone", props["facing"]))
    w.setze(0, Bh + 2, 0, w.b(spitze))
    w.setze(0, Bh + 3, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    # Prunktreppe an der Südseite bis zum Portal
    yp = int(Bh * 0.33)
    bt = _r(3 * u, 2)
    for k in range(yp + 1):
        z = Bh - k + 1
        for x in range(-bt - 1, bt + 2):
            if abs(x) == bt + 1:
                w.setze(x, k + 1, z, M(x, k + 1, z, 0.5))
                if k % 4 == 0:
                    w.setze(x, k + 2, z, w.b(licht, hanging=False, waterlogged=False))
            else:
                w.setze(x, k + 1, z, treppe(w, tr[1], "north"))
            for y in range(1, k + 1):
                if w.frei(x, y, z):
                    w.setze(x, y, z, M(x, y, z, 0.2))
    # Säulenportal
    zp = Bh - yp + 1
    for x in range(-bt - 2, bt + 3):
        for y in range(yp + 1, yp + 1 + _r(9 * u)):
            for z in range(zp - 2, zp + 1):
                innen = abs(x) <= bt and y < yp + 1 + _r(7 * u)
                if innen and z >= zp - 1:
                    w.bloecke.pop((x, y, z), None)
                elif z == zp and (abs(x) == bt + 2 or abs(x) == bt + 1):
                    w.setze(x, y, z, w.b(saeule))
                elif not innen:
                    w.setze(x, y, z, w.b(kat[0]) if (x + y) % 3 == 0 else M(x, y, z, 0.6))
        for z in range(zp - 2, zp + 2):
            w.setze(x, yp + 1 + _r(9 * u), z, w.b(band_voll) if abs(x) % 2 == 0 else w.b(gold))
    for y in range(yp + 1, yp + 1 + _r(7 * u)):
        for x in range(-bt, bt + 1):
            w.setze(x, y, zp - 3, w.b("black_concrete") if st == 0 else w.b("crying_obsidian"))
    # Obelisken
    for sx in (-1, 1):
        ox, oz = sx * (bt + _r(8 * u)), Bh + _r(8 * u)
        Ho = _r(22 * u)
        for y in range(1, Ho + 1):
            r = 1 if y < Ho - 2 else 0
            for x in range(ox - r, ox + r + 1):
                for z in range(oz - r, oz + r + 1):
                    w.setze(x, y, z, w.b(kat[0]) if y % 5 == 0 and r else M(x, y, z, y / Ho))
        w.setze(ox, Ho + 1, oz, w.b(gold))
        for x in range(ox - 2, ox + 3):
            for z in range(oz - 2, oz + 3):
                w.setze(x, 1, z, w.b(band_voll) if max(abs(x - ox), abs(z - oz)) == 2 else M(x, 1, z, 0.1))
    # Wächterlöwen
    for sx in (-1, 1):
        S = Skulptur(w, 1.0 * u + 0.2)
        S.mat("k", sk(M, 0, 12))
        S.mat("m", bl(w, band2))
        S.mat("a", bl(w, gold))
        S.mat("s", sk(boden, 0, 4))
        _loewe(w, S, 0, 0, 0, 1, "s")
        S.rendern((-4, -1, -10), (4, 9, 9), versatz=(sx * (bt + _r(4 * u)) + 0.5, 1.6, Bh + _r(18 * u)))
    hohl(w, 2)
    return w


# ============================================================================ 7 Titanenhand


def titanenhand(seed, g=2):
    """Titanenhand: eine gewaltige Hand bricht aus dem Boden und hält eine leuchtende Sphäre empor.
    Stil 1 bemooster Fels mit Amethystkugel, Stil 2 Bronze mit Feuerkugel."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    if st == 0:
        K = Mat(w, ["mossy_cobblestone", "mossy_stone_bricks", "stone", "andesite", "tuff", "stone", "calcite"],
                kontrast=1.1)
        kugel = ["amethyst_block", "purple_stained_glass", "magenta_stained_glass", "pink_stained_glass"]
        kern = "pearlescent_froglight"
        nagel = "polished_diorite"
    else:
        K = Mat(w, ["waxed_oxidized_copper", "waxed_weathered_copper", "waxed_exposed_copper",
                    "waxed_copper_block", "waxed_cut_copper"], kontrast=1.0)
        kugel = ["shroomlight", "orange_stained_glass", "red_stained_glass", "yellow_stained_glass"]
        kern = "ochre_froglight"
        nagel = "gold_block"
    s = 2.4 * u
    S = Skulptur(w, s)
    S.mat("k", sk(K, 0, 34 * s))
    S.mat("n", bl(w, nagel))
    v = Verlauf(w, "Kugel", kugel)
    S.mat("c", bl(w, kern))
    oc = (0.0, 27.8, 0.4)
    S.mat("o", lambda x, y, z, lx, ly, lz: v(min(3, math.sqrt((lx - oc[0]) ** 2 + (ly - oc[1]) ** 2 + (lz - oc[2]) ** 2)
                                                 / 5.4 * 3), x, y, z))
    # Unterarm (leicht geneigt), Handgelenk, Handteller (nach oben offen)
    S.plus(kap((0.8, -3, -1.0), (0, 15, 0), 4.9, 3.9, zf=0.85), "k")
    for xx in (-1.8, 0, 1.8):
        S.plus(kap((xx, 3, 3.0), (xx * 0.8, 14, 2.8), 0.6, 0.45), "k")
    S.plus(ell(0, 17.0, 0, 4.3, 2.2, 3.5), "k")
    S.plus(ell(0, 19.6, 0.3, 5.4, 2.0, 4.6), "k")
    # Finger: offen gespreizt und gekrümmt, sie umfassen die Sphäre
    for i, fx in enumerate((-3.6, -1.2, 1.2, 3.6)):
        L = (0.9, 1.05, 1.0, 0.85)[i]
        a = (fx, 20.5, 3.6)
        b = (fx * 1.18, 20.5 + 3.4 * L, 5.8)
        c = (fx * 1.25, 20.5 + 6.6 * L, 6.0)
        d = (fx * 1.15, 20.5 + 8.8 * L, 4.6)
        S.plus(kap(a, b, 1.3, 1.2), "k")
        S.plus(kap(b, c, 1.2, 1.05), "k")
        S.plus(kap(c, d, 1.05, 0.85), "k")
        S.plus(ell(d[0], d[1] + 0.2, d[2] + 0.3, 0.8, 0.6, 0.8), "n")
    # Daumen und Handballen
    S.plus(ell(-3.6, 19.8, -1.2, 2.2, 1.8, 2.0), "k")
    S.plus(kap((-4.8, 20.5, -1.8), (-7.2, 23.6, -0.4), 1.5, 1.3), "k")
    S.plus(kap((-7.2, 23.6, -0.4), (-6.6, 26.6, 1.0), 1.3, 1.0), "k")
    S.plus(ell(-6.5, 27.1, 1.1, 0.8, 0.6, 0.8), "n")
    # Sphäre mit Leuchtkern und Lichtfunken
    S.plus(ell(*oc, 5.4, 5.4, 5.4), "o")
    S.plus(ell(*oc, 1.9, 1.9, 1.9), "c")
    S.rendern((-10, -4, -8), (10, 35, 10))
    # aufgebrochener Boden, Geröll und Risse
    gelaende(w, _r(24 * u), art="stein" if st == 0 else "asche", dichte=0.5)
    rng = w.rng
    r_n = Rauschen(w, 2)
    for x, z in scheibe(16 * u):
        d = math.hypot(x, z)
        if d < 8 * u:
            continue
        hhoch = max(0.0, 4.2 * u * (1 - (d - 8 * u) / (8 * u)) * r_n(x, 0, z) * 1.6 - 0.6)
        for y in range(1, int(hhoch) + 1):
            w.setze(x, y, z, w.b(["cobblestone", "andesite", "stone", "tuff", "cracked_stone_bricks",
                                  "gravel"][int(r_n(x, y, z * 3) * 5.99)]) if st == 0 else
                    w.b(["blackstone", "basalt", "tuff", "cobbled_deepslate", "magma_block", "smooth_basalt"]
                        [int(r_n(x, y, z * 3) * 5.99)]), ueberschreiben=False)
    for i in range(7):
        a = i / 7 * 2 * math.pi + rng.random()
        for k in range(int(10 * u), int(22 * u)):
            x, z = round(math.cos(a) * k), round(math.sin(a) * k)
            w.setze(x, 0, z, w.b("cracked_deepslate_tiles") if st == 0 else w.b("magma_block"))
            a += (rng.random() - 0.5) * 0.12
    hohl(w, 2)
    return w


# ============================================================================ 8 Frostkristall


def _kristall(S, a, b, r, etikett):
    """Sechseckiges Prisma mit Spitze von a nach b (lokale Einheiten)."""
    a = np.asarray(a, float)
    d = np.asarray(b, float) - a
    L = float(np.linalg.norm(d))
    e = d / L
    hilf = np.array([1.0, 0, 0]) if abs(e[1]) > 0.5 else np.array([0, 1.0, 0])
    q1 = np.cross(e, hilf)
    q1 /= np.linalg.norm(q1)
    q2 = np.cross(e, q1)

    def f(X, Y, Z):
        px, py, pz = X - a[0], Y - a[1], Z - a[2]
        t = px * e[0] + py * e[1] + pz * e[2]
        u1 = px * q1[0] + py * q1[1] + pz * q1[2]
        u2 = px * q2[0] + py * q2[1] + pz * q2[2]
        hx = np.maximum(np.abs(u1), np.abs(u1) * 0.5 + np.abs(u2) * 0.866)
        spitze = np.where(t > L * 0.78, r * (1 - (t - L * 0.78) / (L * 0.22)), r)
        return (t >= 0) & (t <= L) & (hx <= spitze)
    S.plus(f, etikett)


def frostkristall(seed, g=2):
    """Frostkristall: ein Bündel turmhoher Sechseck-Kristalle wächst aus einem verschneiten Felsen.
    Stil 1 Eis in allen Blautönen, Stil 2 Amethyst-Geode mit Calcit und Basalt."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    rng = w.rng
    if st == 0:
        kr = ["blue_ice", "packed_ice", "light_blue_stained_glass", "ice", "white_stained_glass"]
        fels = Mat(w, ["stone", "andesite", "packed_ice", "snow_block", "snow_block", "powder_snow" if False else
                       "snow_block"], kontrast=1.2)
        boden_art = "schnee"
    else:
        kr = ["amethyst_block", "budding_amethyst", "purple_stained_glass", "amethyst_block",
              "magenta_stained_glass"]
        fels = Mat(w, ["smooth_basalt", "calcite", "tuff", "calcite", "smooth_basalt", "deepslate"], kontrast=1.2)
        boden_art = "stein"
    v = Verlauf(w, "Kr", kr)
    r_n = Rauschen(w, 1.3)
    S = Skulptur(w, 1.0)
    S.mat("k", lambda x, y, z, lx, ly, lz: v(min(4, max(0, (r_n(x, y, z) * 2.2 + ly / (60 * u) * 2.4))), x, y, z))
    H = 62 * u
    _kristall(S, (0, -4, 0), (0.5, H, 0.3), 5.2 * u, "k")
    for i in range(9):
        a = i / 9 * 2 * math.pi + rng.random() * 0.4
        nei = 0.25 + rng.random() * 0.35
        L = H * (0.35 + rng.random() * 0.4)
        r = (2.0 + rng.random() * 2.2) * u
        b = (math.cos(a) * math.sin(nei) * L, L * math.cos(nei), math.sin(a) * math.sin(nei) * L)
        st0 = (math.cos(a) * 3 * u, -2, math.sin(a) * 3 * u)
        _kristall(S, st0, (st0[0] + b[0], b[1], st0[2] + b[2]), r, "k")
    for i in range(16):
        a = rng.random() * 2 * math.pi
        d = (9 + rng.random() * 12) * u
        L = (4 + rng.random() * 9) * u
        nei = 0.3 + rng.random() * 0.6
        st0 = (math.cos(a) * d, -1, math.sin(a) * d)
        _kristall(S, st0, (st0[0] + math.cos(a) * math.sin(nei) * L, L * math.cos(nei),
                           st0[2] + math.sin(a) * math.sin(nei) * L), (0.8 + rng.random()) * u, "k")
    ext = 30 * u
    S.rendern((-ext, -5, -ext), (ext, H + 3, ext))
    # Felssockel
    r_f = Rauschen(w, 5)
    for x, z in scheibe(22 * u):
        d = math.hypot(x, z) / (22 * u)
        hh = (1 - d ** 1.5) * 7 * u * (0.6 + 0.8 * r_f(x, 0, z))
        for y in range(0, int(hh) + 1):
            w.setze(x, y, z, fels(x, y, z, y / max(1, hh)), ueberschreiben=False)
    gelaende(w, _r(30 * u), art=boden_art, dichte=0.4)
    # Kleine Knospen/Eiszapfen auf dem Fels
    for (x, y, z), b in list(w.bloecke.items()):
        if w.frei(x, y + 1, z) and rng.random() < 0.02 and y > 0:
            w.setze(x, y + 1, z, w.b("amethyst_cluster", facing="up", waterlogged=False) if st else w.b("snow", layers=2))
    hohl(w, 2)
    return w


# ============================================================================ 9 Vulkanfeste


def vulkanfeste(seed, g=2):
    """Vulkanfeste: ein rauchender Vulkan mit Lavasee im Krater, glühenden Magmaadern, Basaltsäulen und einer
    in die Flanke gebauten Festung mit Torbau. Stil 1 Feuer und Lava, Stil 2 Seelenfeuer-Vulkan."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    rng = w.rng
    R = 40 * u
    H = 50 * u
    if st == 0:
        G = Mat(w, ["basalt", "blackstone", "smooth_basalt", "tuff", "cobbled_deepslate", "magma_block"],
                kontrast=1.3)
        ader, see, glut = "magma_block", "lava", "shroomlight"
        feuer = "campfire"
    else:
        G = Mat(w, ["basalt", "smooth_basalt", "soul_soil", "blackstone", "soul_sand", "polished_basalt"],
                kontrast=1.3)
        ader, see, glut = "crying_obsidian", "soul_fire_n", "sea_lantern"
        feuer = "soul_campfire"
    r_n = Rauschen(w, 7)
    r_a = Rauschen(w, 3)
    kr = R * 0.24
    hoehe = {}
    for x in range(-int(R) - 6, int(R) + 7):
        for z in range(-int(R) - 6, int(R) + 7):
            d = math.hypot(x, z)
            Rr = R * (0.85 + 0.3 * r_n(x, 0, z))
            if d > Rr:
                continue
            t = d / Rr
            if d < kr:
                hh = H * 0.86 - (kr - d) * 0.8
            else:
                hh = H * (1 - ((d - kr) / (Rr - kr)) ** 0.75) + (r_a(x, 0, z) - 0.5) * 3 * u
            hoehe[(x, z)] = int(hh)
            for y in range(0, int(hh) + 1):
                adern = abs(math.sin(math.atan2(z, x) * 7 + r_a(x, y, z) * 2.5)) < 0.06 and y > 2
                w.setze(x, y, z, w.b(ader) if adern and y >= int(hh) - 1 else G(x, y, z, y / H))
    # Kratersee
    yk = int(H * 0.86 - kr * 0.8) + 1
    for x, z in scheibe(kr * 0.85):
        for y in range(hoehe.get((x, z), 0) + 1, yk + 1):
            if st == 0:
                w.setze(x, y, z, w.b("lava", level=0) if y == yk else w.b("magma_block"))
            else:
                w.setze(x, y, z, w.b("soul_soil") if y < yk else w.b("soul_fire"))
    # Glühende Lavarinnen vom Kraterrand hinab
    for i in range(6):
        a = i / 6 * 2 * math.pi + rng.random() * 0.6
        if abs(math.sin(a) - 1) < 0.35:
            continue
        for k in range(int(kr), int(R * 0.95)):
            a += (rng.random() - 0.5) * 0.08
            for dd in (-1, 0, 1):
                x = round(math.cos(a) * k - math.sin(a) * dd)
                z = round(math.sin(a) * k + math.cos(a) * dd)
                if (x, z) in hoehe:
                    y = hoehe[(x, z)]
                    w.setze(x, y, z, w.b(glut if (dd == 0 and k % 5 == 0) else ader))
                    if dd != 0 and rng.random() < 0.5:
                        w.setze(x, y, z, w.b("magma_block" if st == 0 else "soul_soil"))
    # Basaltsäulen am Fuß
    for i in range(40):
        a = rng.random() * 2 * math.pi
        d = R * (0.85 + rng.random() * 0.35)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        hh = int((2 + rng.random() * 9) * u)
        for y in range(0, hh):
            w.setze(x, y, z, w.b("basalt", axis="y") if rng.random() < 0.8 else w.b("polished_basalt", axis="y"))
    # Rauch: Lagerfeuer am Kraterrand
    for x, z in kreisrand(kr + 1):
        if rng.random() < 0.18:
            y = hoehe.get((x, z), 0)
            w.setze(x, y + 1, z, w.b(feuer, lit=True, signal_fire=True, facing="north", waterlogged=False))
    # Festung in der Südflanke
    fz = int(R * 0.55)
    fh = hoehe.get((0, fz), 10)
    sto = Mat(w, "schwarzstein")
    bw = _r(9 * u)
    for x in range(-bw, bw + 1):
        for z in range(fz - 6, fz + 3):
            for y in range(0, fh + 6):
                aussen = z == fz + 2
                if aussen:
                    w.setze(x, y, z, sto(x, y, z, y / (fh + 6)))
                elif y < fh + 6 and z > fz - 6:
                    w.setze(x, y, z, sto(x, y, z, 0.5), ueberschreiben=False)
        if x % 2 == 0:
            w.setze(x, fh + 6, fz + 2, sto(x, fh + 6, fz + 2, 0.9))
    th = _r(7 * u, 5)
    for x in range(-2, 3):
        for y in range(1, th + 1):
            for z in range(fz - 6, fz + 3):
                if abs(x) < 2 or y < th:
                    w.bloecke.pop((x, y, z), None)
    for x in range(-2, 3):
        w.setze(x, th, fz + 2, w.b("iron_bars", north=False, south=False, east=True, west=True, waterlogged=False))
        w.setze(x, 0, fz + 3, w.b("polished_blackstone_bricks"))
    for sx in (-1, 1):
        tx = sx * (bw + 2)
        for y in range(0, fh + 12):
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if abs(dx) + abs(dz) <= 3:
                        fen = (y % 6 == 3) and (abs(dx) + abs(dz) == 3) and dz == 0
                        w.setze(tx + dx, y, fz + dz, w.b(glut) if fen else sto(tx + dx, y, fz + dz, y / (fh + 12)))
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                if abs(dx) + abs(dz) == 4 or (abs(dx) == 3 and abs(dz) == 1) or (abs(dx) == 1 and abs(dz) == 3):
                    w.setze(tx + dx, fh + 12, fz + dz, sto(tx + dx, fh + 12, fz + dz, 1))
        w.setze(tx, fh + 12, fz, w.b(feuer, lit=True, signal_fire=False, facing="north", waterlogged=False))
    hohl(w, 3)
    return w


# ============================================================================ 10 Drachengebein


def drachengebein(seed, g=2):
    """Drachengebein: das halb versunkene Skelett eines urzeitlichen Drachen – Wirbelsäule im Bogen,
    Rippenkäfig, gehörnter Schädel, Flügelknochen. Stil 1 bleiche Knochen im Gras, Stil 2 schwarzes
    Gebein in einer Aschewüste mit glühenden Augen."""
    w = welt(seed)
    u = U[g]
    st = _stil(seed)
    rng = w.rng
    if st == 0:
        Kn = Mat(w, ["bone_block", "calcite", "bone_block", "diorite", "smooth_quartz", "bone_block"], kontrast=0.8)
        auge = "redstone_block"
        boden = "wiese"
    else:
        Kn = Mat(w, ["blackstone", "polished_blackstone", "basalt", "polished_basalt", "obsidian"], kontrast=0.8)
        auge = "shroomlight"
        boden = "asche"
    s = 1.35 * u
    S = Skulptur(w, s)
    S.mat("k", sk(Kn, 0, 40 * s))
    S.mat("a", bl(w, auge))
    L = 70.0

    def ruecken(t):
        """Wirbelsäule: x von -L/2..L/2, gewölbt, Schwanz am Ende in den Boden."""
        x = -L / 2 + t * L
        y = 14 * math.sin(math.pi * min(1, t * 1.15)) + 2 - 6 * max(0, t - 0.85) / 0.15
        z = 6 * math.sin(t * math.pi * 1.6)
        return np.array([x, y, z])

    n = 46
    for i in range(n):
        t = i / (n - 1)
        p = ruecken(t)
        r = 1.9 * (1 - t * 0.7) + 0.5
        S.plus(ell(p[0], p[1], p[2], r * 0.7, r, r), "k")
        if i % 2 == 0:
            S.plus(kap(tuple(p), (p[0], p[1] + r * 1.6 + 1.2 * (1 - t), p[2]), r * 0.35, 0.15), "k")   # Dornfortsatz
    # Rippenkäfig
    for i in range(10, 26, 2):
        t = i / (n - 1)
        p = ruecken(t)
        rr = 9.0 * math.sin(math.pi * (i - 8) / 20)
        for sz in (-1, 1):
            pts = []
            for k in range(9):
                a = k / 8 * math.pi * 0.95
                pts.append((p[0] + 0.6 * k * 0.1, p[1] - math.sin(a) * rr * 0.9 + 0.2, p[2] + sz * math.cos(a - math.pi / 2) * 0
                            + sz * math.sin(a) * rr * 0.75 + sz * (1 - math.cos(a)) * 0.4))
            for k in range(8):
                S.plus(kap(pts[k], pts[k + 1], 0.55, 0.5), "k")
    # Schädel am Anfang (Hals hebt sich)
    p0 = ruecken(0.0)
    hals = [p0 + np.array([-3 - k * 2.4, 2 + k * 1.6 - k * k * 0.12, 0]) for k in range(7)]
    for k in range(6):
        S.plus(kap(tuple(hals[k]), tuple(hals[k + 1]), 1.3, 1.2), "k")
    kopf = hals[-1] + np.array([-4, 0.5, 0])
    S.plus(ell(kopf[0], kopf[1], kopf[2], 4.5, 2.6, 2.8), "k")
    S.plus(kap(tuple(kopf + [-2, 0, 0]), tuple(kopf + [-9, -1.2, 0]), 1.9, 1.0), "k")        # Oberkiefer
    S.plus(kap(tuple(kopf + [-1, -2.6, 0]), tuple(kopf + [-8.5, -4.2, 0]), 1.2, 0.7), "k")   # Unterkiefer
    for sz in (-1, 1):
        S.plus(ell(kopf[0] - 1.2, kopf[1] + 0.6, kopf[2] + sz * 2.2, 0.9, 0.8, 0.5), "a")    # Augenhöhlen
        S.plus(kap(tuple(kopf + [1.5, 1.5, sz * 1.6]), tuple(kopf + [7.5, 5.5, sz * 3.6]), 0.9, 0.2), "k")
        S.plus(kap(tuple(kopf + [2.0, 0.4, sz * 2.2]), tuple(kopf + [6.0, -0.8, sz * 4.0]), 0.6, 0.15), "k")
        for k in range(4):
            S.plus(kap(tuple(kopf + [-3 - k * 1.6, -1.6, sz * 0.9]), tuple(kopf + [-3.2 - k * 1.6, -2.8, sz * 0.9]),
                       0.3, 0.1), "k")
    # Beine (Knochen, im Boden steckend)
    for (t, sz) in ((0.22, -1), (0.22, 1), (0.6, -1), (0.6, 1)):
        p = ruecken(t)
        knie = p + np.array([1.5, -6, sz * 5])
        fuss = p + np.array([-1, -p[1] - 1, sz * 7])
        S.plus(kap(tuple(p + [0, -1, sz * 2]), tuple(knie), 1.2, 1.0), "k")
        S.plus(kap(tuple(knie), tuple(fuss), 1.0, 0.8), "k")
    # Flügelknochen (gespreizt nach oben)
    for sz in (-1, 1):
        sch = ruecken(0.25) + np.array([0, 1, sz * 2])
        ell_b = sch + np.array([4, 12, sz * 10])
        S.plus(kap(tuple(sch), tuple(ell_b), 1.3, 1.0), "k")
        for k in range(4):
            spitze = ell_b + np.array([6 + k * 4, 10 - k * 6, sz * (6 + k * 3)])
            S.plus(kap(tuple(ell_b), tuple(spitze), 0.8, 0.35), "k")
    S.rendern((-L / 2 - 30, -3, -32), (L / 2 + 6, 42, 32))
    # Erdhügel, die das Gerippe halb verschlucken
    r_n = Rauschen(w, 6)
    gelaende(w, _r(55 * u), art=boden, dichte=0.6)
    hm = "sand" if False else ("grass_block" if st == 0 else "blackstone")
    for x in range(int(-L / 2 * s) - 25, int(L / 2 * s) + 10):
        for z in range(-int(35 * u), int(35 * u) + 1):
            if math.hypot(x, z) > 52 * u:
                continue
            hh = (r_n(x, 0, z) - 0.58) * 12 * u
            for y in range(1, int(hh) + 1):
                w.setze(x, y, z, w.b("dirt") if st == 0 and y < int(hh) else
                        (w.b("grass_block", snowy=False) if st == 0 else w.b(["blackstone", "basalt", "tuff"]
                                                                            [int(r_n(x, y, z * 2) * 2.99)])),
                        ueberschreiben=False)
    if st == 0:
        for (x, y, z), b in list(w.bloecke.items()):
            if y > 1 and w.frei(x, y + 1, z) and rng.random() < 0.06 and w.P.name(b) in ("minecraft:bone_block",
                                                                                         "minecraft:calcite"):
                w.setze(x, y + 1, z, w.b("moss_carpet"))
    hohl(w, 2)
    return w


TEIL2 = {
    "sonnenpyramide": ("Sonnenpyramide", sonnenpyramide),
    "titanenhand": ("Titanenhand", titanenhand),
    "frostkristall": ("Frostkristall", frostkristall),
    "vulkanfeste": ("Vulkanfeste", vulkanfeste),
    "drachengebein": ("Drachengebein", drachengebein),
}

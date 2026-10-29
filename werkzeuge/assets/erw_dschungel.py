"""Dschungeltempel II – zwanzig weitere Bauten im Regenwald: Baumkronenpfad, Pfeilgiftfrosch-Statue, Papageien-
Voliere, Schneckenturm-Sternwarte, Überwucherter Aquädukt, Kakao-Plantage, Riesenseerosen-Teich, Schamanenhütte,
Krokodil-Wächter, Expeditionslager, Cenote, Affenfelsen, Wurzeltor, Sonnenstein, Maisterrassen, Orchideen-
Pavillon, Einbaum-Werft, Adlerhorst im Urwaldriesen, Jade-Maske und Fruchthain."""

from __future__ import annotations

import math

import numpy as np

import wald2
from dorf1 import moos_oben, ranken
from feinbau import Dachmat, Mix, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, laubball, rohr
from lib import Rauschen, einfuegen
from skulptur import Skulptur, dreh_y, ell, kap, kasten, kegel, kreisrand

S = [0.6, 1.0, 1.6, 2.5]


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def moosstein(w):
    return M(w, [("mossy_stone_bricks", 3), ("stone_bricks", 2), ("mossy_cobblestone", 2), ("cracked_stone_bricks", 1)])


def boden(w, R, huegel=0.5, cx=0, cz=0, dichte=1.0):
    rn = Rauschen(w, 6)
    rf = Rauschen(w, 2)
    rng = w.rng
    zellen = {}
    for x in range(cx - int(R) - 2, cx + int(R) + 3):
        for z in range(cz - int(R) - 2, cz + int(R) + 3):
            if math.hypot(x - cx, z - cz) <= R + 2 * rn(x, 0, z):
                h = int(huegel * 2 * rn(x * 0.7, 3, z * 0.7))
                v = rf(x, 4, z)
                for y in range(-2, h + 1):
                    b = ("moss_block" if v > 0.7 else "podzol" if v < 0.25 else "grass_block") if y == h else "dirt"
                    w.setze(x, y, z, w.b(b, snowy=False) if b in ("grass_block", "podzol") else w.b(b))
                zellen[(x, z)] = h
                q = rng.random() * dichte
                if q > 0.86:
                    w.setze(x, h + 1, z, w.b("fern") if q < 0.93 else w.b("grass"))
                elif q > 0.84:
                    w.setze(x, h + 1, z, w.b("large_fern", half="lower"))
                    w.setze(x, h + 2, z, w.b("large_fern", half="upper"))
    return zellen


def riese(w, x, y, z, seed, H):
    einfuegen(w, wald2.dschungelriese(seed + x * 31 + z * 7, H=int(H)), x, y, z)


def baum(w, x, y, z, seed, H):
    einfuegen(w, wald2.laubbaum(seed + x * 13 + z, holz="jungle", H=int(H)), x, y, z)


def baumrand(w, zellen, R, n, seed, innen=0.75, H=(10, 18), riesen=0):
    rng = w.rng
    for i in range(n):
        a = rng.random() * 6.28
        r = R * (innen + rng.random() * (0.98 - innen))
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        hh = H[0] + rng.random() * (H[1] - H[0])
        if i < riesen:
            riese(w, x, zellen.get((x, z), 0) + 1, z, seed, hh * 1.4)
        else:
            baum(w, x, zellen.get((x, z), 0) + 1, z, seed, hh)


def figur(w, u, teile, lo, hi, pos=(0, 0, 0), winkel=0.0):
    Sk = Skulptur(w, u)
    for i, (form, blk) in enumerate(teile):
        if blk is None:
            Sk.minus(form)
            continue
        Sk.mat(str(i), blk)
        Sk.plus(form, str(i))
    Sk.rendern(lo, hi, versatz=(pos[0] + 0.5, pos[1], pos[2] + 0.5), dreh=dreh_y(winkel))


def strohdach_rund(w, cx, cz, y, r, h=None):
    h = h or int(r * 1.3) + 1
    for k in range(h + 1):
        rr = (r + 1.2) * (1 - k / (h + 0.5))
        for x, z in kreisrand(max(0.4, rr), cx, cz):
            w.setze(x, y + k, z, w.b("hay_block", axis="y") if (x + z + k) % 4 else w.b("bamboo_block", axis="y"))
    return y + h


# ============================================================================ Bauten

def baumkronenpfad(seed, g=2):
    """Baumkronenpfad: vier Urwaldriesen tragen Plattformen in den Kronen, verbunden durch schwankende Hänge-
    brücken aus Bambus mit Seilgeländern; eine Strickleiter und eine Wendeltreppe führen hinauf."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 7)
    zellen = boden(w, R, 0.3)
    yp = int(10 * s + 6)
    pos = []
    for i in range(4):
        a = i / 4 * 2 * math.pi + 0.4
        cx, cz = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        riese(w, cx, zellen.get((cx, cz), 0) + 1, cz, seed + i, yp * 1.7)
        pr = 2 + int(s)
        for x in range(cx - pr - 1, cx + pr + 2):
            for z in range(cz - pr - 1, cz + pr + 2):
                d = math.hypot(x - cx, z - cz)
                if d <= pr + 0.5:
                    w.setze(x, yp, z, w.b("jungle_planks"))
                elif d <= pr + 1.3:
                    w.setze(x, yp, z, w.b("jungle_planks"))
                    w.setze(x, yp + 1, z, w.b("jungle_fence"))
        pos.append((cx, cz))
    for (a, b) in zip(pos, pos[1:] + pos[:1]):
        L = int(math.hypot(b[0] - a[0], b[1] - a[1]))
        nx, nz = (b[1] - a[1]) / max(1, L), -(b[0] - a[0]) / max(1, L)
        for k in range(L + 1):
            t = k / L
            x = a[0] + (b[0] - a[0]) * t
            z = a[1] + (b[1] - a[1]) * t
            y = yp - round(1.5 * s * math.sin(math.pi * t))
            w.setze(round(x), y, round(z), w.b("bamboo_mosaic") if False else w.b("bamboo_planks"), False)
            for q in (-1, 1):
                w.setze(round(x + nx * q), y + 1, round(z + nz * q), w.b("bamboo_fence"), False)
    x0, z0 = pos[0]
    for y in range(1, yp):
        w.setze(x0 + 3 + int(s), y, z0, w.b("ladder", facing="east", waterlogged=False), False)
    return w


def pfeilgiftfrosch(seed, g=2):
    """Pfeilgiftfrosch-Statue: ein riesiger, leuchtend blauer Frosch mit schwarzen Flecken und gelbem Rücken
    hockt auf einem bemoosten Felsen zwischen Farnen und Bromelien."""
    w = _neu(seed)
    s = S[g]
    u = 0.9 * s + 0.4
    R = int(9 * u + 6)
    boden(w, R, 0.3)
    kugel(w, 0, 0, 0, 4.5 * u, moosstein(w), ry=2.2 * u)
    bl = w.b("blue_concrete")
    lb = w.b("light_blue_concrete")
    ge = w.b("yellow_concrete")
    sch = w.b("black_concrete")

    def haut(x, y, z, lx, ly, lz):
        if (x * 7 + y * 3 + z * 5) % 11 < 2:
            return sch
        return ge if ly > 5.0 else bl
    Sk = Skulptur(w, u)
    Sk.mat("h", haut)
    Sk.mat("l", lb)
    Sk.mat("a", sch)
    Sk.mat("w", w.b("white_concrete"))
    Sk.plus(ell(0, 4.2, 0, 3.0, 2.0, 2.4), "h")
    Sk.plus(ell(2.2, 5.0, 0, 1.8, 1.4, 2.0), "h")
    Sk.plus(ell(2.2, 3.8, 0, 1.4, 0.6, 1.6), "l")
    for sz in (-1, 1):
        Sk.plus(ell(2.6, 6.2, sz * 1.2, 0.7, 0.7, 0.7), "a")
        Sk.plus(ell(2.9, 6.4, sz * 1.25, 0.25, 0.25, 0.2), "w")
        Sk.plus(kap((-1.5, 3.6, sz * 2.0), (-0.2, 3.0, sz * 3.4), 0.9, 0.7), "h")
        Sk.plus(kap((-0.2, 3.0, sz * 3.4), (-2.0, 2.4, sz * 3.6), 0.6), "l")
        Sk.plus(ell(-2.4, 2.4, sz * 3.8, 1.0, 0.25, 0.8), "l")
        Sk.plus(kap((2.0, 3.8, sz * 1.6), (3.4, 2.4, sz * 2.2), 0.45), "l")
        Sk.plus(ell(3.8, 2.3, sz * 2.4, 0.7, 0.2, 0.6), "l")
    Sk.rendern((-5, 1, -5), (5, 8, 5), versatz=(0.5, 0, 0.5))
    rng = w.rng
    for _ in range(int(8 * s + 4)):
        a = rng.random() * 6.28
        d = R * (0.55 + rng.random() * 0.35)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = max([yy for yy in range(-2, 8) if not w.frei(x, yy, z)] or [0]) + 1
        f = ["red_tulip", "orange_tulip", "pink_tulip", "allium"][int(rng.integers(4))]
        w.setze(x, y, z, w.b(f))
    return w


def papageienvoliere(seed, g=2):
    """Papageien-Voliere: eine hohe, kuppelförmige Voliere aus Bambusgittern um einen Tropenbaum, auf dessen Ästen
    bunte Papageien-Figuren in Rot, Blau, Grün und Gelb sitzen, mit Futterstellen und Wasserschalen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = boden(w, R, 0.2)
    rv = 6 * s + 4
    H = int(9 * s + 7)
    for k in range(H + 1):
        t = k / H
        r = rv * math.sqrt(max(0, 1 - t ** 2.5))
        for x, z in kreisrand(max(0.5, r)):
            ang = math.atan2(z, x)
            if k % 3 == 0 or int((ang + math.pi) * rv / 2) % 2 == 0:
                w.setze(x, 1 + k, z, w.b("bamboo_fence") if k % 3 else w.b("bamboo_block", axis="y"))
    for y in (1, 2, 3):
        for x in (-1, 0, 1):
            w.bloecke.pop((x, y, round(rv)), None)
    baum(w, 0, 1, 0, seed, H * 0.85)
    farben = [("red_concrete", "blue_concrete", "yellow_concrete"), ("blue_concrete", "yellow_concrete", "cyan_concrete"),
              ("lime_concrete", "red_concrete", "yellow_concrete"), ("yellow_concrete", "blue_concrete", "red_concrete")]
    rng = w.rng
    for k in range(5 + 2 * g):
        a = rng.random() * 6.28
        d = rv * (0.2 + rng.random() * 0.5)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = int(3 + rng.random() * H * 0.7)
        c1, c2, c3 = farben[k % 4]
        teile = [(ell(0, 1.4, 0, 0.6, 1.0, 0.6), w.b(c1)), (ell(0.2, 2.6, 0, 0.55, 0.55, 0.55), w.b(c1)),
                 (ell(0.75, 2.5, 0, 0.3, 0.25, 0.2), w.b("black_concrete")),
                 (ell(-0.1, 1.5, 0.55, 0.3, 0.8, 0.2), w.b(c2)), (ell(-0.1, 1.5, -0.55, 0.3, 0.8, 0.2), w.b(c2)),
                 (kap((-0.3, 0.6, 0), (-0.8, -1.2, 0), 0.25, 0.1), w.b(c3))]
        figur(w, 0.6 * s + 0.4, teile, (-2, -2, -2), (2, 4, 2), pos=(x, y, z), winkel=rng.random() * 6.28)
        for dx in (-1, 0, 1):
            w.setze(x + dx, y, z, w.b("jungle_fence"), False)
    for k in range(3):
        a = k * 2.1
        x, z = round(math.cos(a) * rv * 0.6), round(math.sin(a) * rv * 0.6)
        w.setze(x, 1, z, w.b("water_cauldron", level=3) if k % 2 else w.b("composter", level=6))
    _ = zellen
    return w


def schneckenturm(seed, g=2):
    """Schneckenturm-Sternwarte: ein runder Turm mit innerer Wendeltreppe auf einer zweistufigen Plattform aus
    Kalkstein, oben eine Beobachtungskammer mit schmalen Sichtschlitzen, alles von Lianen überwuchert."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = boden(w, R, 0.2)
    st = M(w, [("smooth_sandstone", 2), ("calcite", 2), ("mossy_cobblestone", 1), ("cut_sandstone", 1)])
    A1, A2 = int(8 * s + 6), int(5 * s + 4)
    h1 = int(2 * s + 2)
    for (A, y0, h) in ((A1, 1, h1), (A2, 1 + h1, h1)):
        for x in range(-A, A + 1):
            for z in range(-A, A + 1):
                for y in range(y0, y0 + h):
                    w.setze(x, y, z, st(x, y, z))
        for k in range(h):
            for x in (-1, 0, 1):
                w.setze(x, y0 + k, A + h - k, treppe(w, "sandstone", "north"))
                for kk in range(k + 1, h):
                    w.setze(x, y0 + kk, A + h - k, w.b("air"))
    y0 = 1 + 2 * h1
    rt = 2.5 * s + 2.5
    H = int(8 * s + 6)
    for y in range(y0, y0 + H):
        for x, z in kreisrand(rt):
            schlitz = y > y0 + H - 4 and (abs(x) < 1 or abs(z) < 1) and y % 2 == 0
            if not schlitz:
                w.setze(x, y, z, st(x, y, z))
    for k in range(H * 2):
        ang = k * 0.5
        y = y0 + k // 2
        if y >= y0 + H - 1:
            break
        x, z = round(math.cos(ang) * (rt - 1.5)), round(math.sin(ang) * (rt - 1.5))
        w.setze(x, y, z, w.b("smooth_sandstone_slab", type="top", waterlogged=False))
    kegeldach(w, 0, 0, y0 + H, int(rt), Dachmat(w, ["sandstone", "mossy_cobblestone"]), form="kegel", ue=0.5,
              spitze=None)
    for y in (y0, y0 + 1):
        w.bloecke.pop((0, y, round(rt)), None)
    ranken(w, 0.05)
    moos_oben(w, 0.25)
    baumrand(w, zellen, R, 4 + 2 * g, seed, innen=0.85)
    return w


def aquaedukt(seed, g=2):
    """Überwucherter Aquädukt: eine lange Bogenreihe aus bemoostem Stein, auf der noch Wasser in einer Rinne
    fließt, an einem Ende ein Wasserfall in ein Becken; Würgefeigen umschlingen die Pfeiler."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = boden(w, R, 0.4)
    st = moosstein(w)
    H = int(6 * s + 5)
    L = int(R * 0.9)
    sp = int(2 * s + 3)
    for x in range(-L, L + 1):
        for z in (-1, 0, 1):
            for y in range(1, H + 2):
                im_bogen = (x % (2 * sp + 2)) != 0 and y < H - 1 and \
                    ((x % (2 * sp + 2)) - (sp + 1)) ** 2 / (sp + 0.3) ** 2 + ((y - 1) / (H - 2)) ** 2 < 1.0
                if not im_bogen:
                    w.setze(x, y, z, st(x, y, z))
        w.setze(x, H + 1, 0, w.b("water", level=0))
        w.setze(x, H + 2, -1, st(x, H + 2, -1))
        w.setze(x, H + 2, 1, st(x, H + 2, 1))
    for y in range(1, H + 2):
        w.setze(L + 1, y, 0, w.b("water", level=0) if y > 0 else w.b("stone"))
    for x in range(L - 1, L + 5):
        for z in range(-3, 4):
            if math.hypot(x - L - 1, z) < 3.5:
                w.setze(x, 0, z, w.b("water", level=0))
    rng = w.rng
    for x in range(-L, L + 1, 2 * sp + 2):
        for k in range(int(H * 0.8)):
            ang = k * 0.8
            w.setze(x + round(math.cos(ang) * 1.5), 1 + k, round(math.sin(ang) * 1.8), w.b("jungle_log", axis="y"),
                    False)
    ranken(w, 0.06)
    moos_oben(w, 0.4)
    baumrand(w, zellen, R, 3 + 2 * g, seed, innen=0.85)
    _ = rng
    return w


def kakaoplantage(seed, g=1):
    """Kakao-Plantage: Reihen junger Dschungelbäume mit Kakaoschoten an den Stämmen, Trockengestelle mit Matten,
    eine Fermentierkiste, ein Schuppen mit Bambusdach und ein Pfad aus Trittsteinen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = boden(w, R, 0.1, dichte=0.4)
    rng = w.rng
    for x in range(-R + 3, R - 2, 5):
        for z in range(-R + 3, int(R * 0.3), 5):
            if math.hypot(x, z) > R - 3:
                continue
            H = int(4 + rng.random() * 3 * s)
            y0 = zellen.get((x, z), 0) + 1
            for y in range(y0, y0 + H):
                w.setze(x, y, z, w.b("jungle_log", axis="y"))
            laubball(w, x, y0 + H, z, 1.8 + s * 0.6, arten=("jungle_leaves",), dicht=0.9)
            for y in range(y0 + 1, y0 + H - 1, 2):
                for dx, dz, f in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
                    if rng.random() < 0.5:
                        w.setze(x + dx, y, z + dz, w.b("cocoa", age=2, facing=f))
    for k in range(3 + g):
        x0, z0 = -int(R * 0.5) + k * 4, int(R * 0.55)
        for x in range(x0, x0 + 3):
            w.setze(x, 2, z0, w.b("brown_carpet"))
            w.setze(x, 1, z0, w.b("bamboo_fence"))
    hx, hz = int(R * 0.45), int(R * 0.5)
    for x in range(hx - 2, hx + 3):
        for z in range(hz - 2, hz + 3):
            if abs(x - hx) == 2 and abs(z - hz) == 2:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("bamboo_block", axis="y"))
            w.setze(x, 4, z, w.b("bamboo_mosaic_slab", type="bottom", waterlogged=False))
    w.setze(hx, 1, hz, w.b("barrel", facing="up", open=False))
    w.setze(hx + 1, 1, hz, w.b("composter", level=7))
    return w


def seerosenteich(seed, g=2):
    """Riesenseerosen-Teich: ein dunkler Urwaldteich, auf dem kreisrunde Riesenseerosen mit aufgebogenem Rand
    treiben, dazwischen rosa Blüten auf Stielen, am Ufer Mangrovenwurzeln und ein Bambussteg."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = boden(w, R, 0.3)
    rn = Rauschen(w, 5)
    rt = R * 0.7
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) < rt + rn(x, 2, z) * 3:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
                for y in range(1, 4):
                    w.bloecke.pop((x, y, z), None)
                zellen[(x, z)] = -1
    rng = w.rng
    for k in range(5 + 3 * g):
        a = rng.random() * 6.28
        d = rng.random() * rt * 0.8
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        r = (1.2 + rng.random() * 1.8) * s + 1
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for z in range(int(cz - r) - 1, int(cz + r) + 2):
                dd = math.hypot(x - cx, z - cz)
                if dd <= r and w.hole(x, 0, z) == w.b("water", level=0):
                    rand = dd > r - 1
                    w.setze(x, 1, z, w.b("lime_wool" if not rand else "green_wool") if not rand or rng.random() < 0.9
                            else w.b("lily_pad"))
                    if rand and (x + z) % 2 == 0:
                        w.setze(x, 2, z, w.b("green_carpet"))
        if rng.random() < 0.6:
            bx, bz = cx + 1, cz
            w.setze(bx, 2, bz, w.b("pink_wool"))
            w.setze(bx, 3, bz, w.b("pink_stained_glass"))
            w.setze(bx, 4, bz, w.b("white_wool"))
    for x in range(-int(rt) - 2, 0):
        for z in (-1, 0, 1):
            w.setze(x, 1, z, w.b("bamboo_planks"))
        if x % 3 == 0:
            for z in (-1, 1):
                w.setze(x, 2, z, w.b("bamboo_fence"))
                w.setze(x, 0, z, w.b("bamboo_block", axis="y"))
    baumrand(w, zellen, R, 4 + 2 * g, seed, innen=0.85)
    return w


def schamanenhuette(seed, g=1):
    """Schamanenhütte: eine runde Hütte auf Pfählen mit spitzem Strohdach, bemalten Masken an den Wänden,
    Federbüscheln am Giebel, einem Kräutergestell und einem rauchenden Ritualfeuer davor."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = boden(w, R, 0.2)
    r = 2.5 * s + 2.5
    y0 = int(2 * s + 1)
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            d = math.hypot(x, z)
            if d <= r + 0.5:
                w.setze(x, y0, z, w.b("jungle_planks"))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x, z = round(math.cos(a) * (r - 0.5)), round(math.sin(a) * (r - 0.5))
        for y in range(1, y0):
            w.setze(x, y, z, w.b("jungle_log", axis="y"))
    H = int(2 * s + 3)
    for y in range(y0 + 1, y0 + H + 1):
        for x, z in kreisrand(r):
            w.setze(x, y, z, w.b("bamboo_block", axis="y") if (x + z) % 3 else w.b("stripped_jungle_log", axis="y"))
    masken = ["red_glazed_terracotta", "orange_glazed_terracotta", "yellow_glazed_terracotta", "lime_glazed_terracotta"]
    for i in range(4):
        a = i / 4 * 2 * math.pi + 0.4
        x, z = round(math.cos(a) * (r + 0.6)), round(math.sin(a) * (r + 0.6))
        w.setze(x, y0 + 2, z, w.b(masken[i], facing="north"))
    top = strohdach_rund(w, 0, 0, y0 + H + 1, r)
    for k in range(3):
        w.setze(0, top + k, 0, w.b(["red_wool", "yellow_wool", "blue_wool"][k]))
    for y in (y0 + 1, y0 + 2):
        w.bloecke.pop((0, y, round(r)), None)
    for k in range(y0):
        w.setze(0, y0 - k, round(r) + 1 + k, treppe(w, "jungle", "north"))
    fz = round(r) + y0 + 4
    w.setze(0, zellen.get((0, fz), 0) + 1, fz, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                   waterlogged=False))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        x, z = round(math.cos(a) * 2.5), fz + round(math.sin(a) * 2.5)
        w.setze(x, zellen.get((x, z), 0) + 1, z, w.b("mossy_cobblestone_slab", type="bottom", waterlogged=False))
    for x in (-int(r) - 3, -int(r) - 1):
        for y in range(1, 4):
            w.setze(x, y, 0, w.b("bamboo_fence"))
    for x in range(-int(r) - 3, -int(r)):
        w.setze(x, 4, 0, w.b("bamboo_block", axis="x"))
        w.setze(x, 3, 0, w.b("flowering_azalea_leaves", persistent=True, distance=1, waterlogged=False))
    baumrand(w, zellen, R, 3 + 2 * g, seed, innen=0.85)
    return w


def krokodilwaechter(seed, g=2):
    """Krokodil-Wächter: eine alte Steinbrücke über einen trägen Urwaldfluss, darunter liegen riesige, moosgrüne
    Krokodil-Statuen mit aufgesperrten Mäulern im Wasser, Brückenpfeiler mit Fackeln."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = boden(w, R, 0.2)
    for x in range(-R - 2, R + 3):
        for dz in range(-int(4 * s + 3), int(4 * s + 4)):
            z = dz + round(math.sin(x / 6) * 2)
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
    st = moosstein(w)
    bw = int(4 * s + 3) + 3
    yb = int(2 * s + 3)
    for z in range(-bw, bw + 1):
        y = yb + round(1.2 * s * math.cos(math.pi * z / (2 * bw)))
        for x in (-2, -1, 0, 1, 2):
            w.setze(x, y, z, st(x, y, z))
            if abs(x) == 2:
                w.setze(x, y + 1, z, w.b("mossy_stone_brick_wall"))
        if abs(z) == bw // 2:
            for yy in range(0, y):
                for x in (-2, -1, 0, 1, 2):
                    w.setze(x, yy, z, st(x, yy, z))
    gr = w.b("green_terracotta")
    hell = w.b("lime_terracotta")
    za = w.b("white_concrete")
    for k, (px, ang) in enumerate(((-int(R * 0.45), 0.3), (int(R * 0.45), math.pi + 0.2))):
        teile = [(ell(0, 0.8, 0, 6, 1.2, 1.6), gr), (ell(0.5, 0.3, 0, 5, 0.6, 1.3), hell),
                 (kap((5, 0.9, 0), (9, 0.9, 0), 1.1, 0.7), gr), (kap((-5, 0.8, 0), (-12, 0.6, 0), 1.2, 0.3), gr),
                 (kap((5.5, 0.6, 0), (9.5, 2.2, 0), 0.7, 0.5), gr), (kasten(6, 1.0, -0.6, 9.4, 1.6, 0.6), None)]
        for i in range(-4, 5):
            teile.append((kegel(i * 1.2, 0, 1.6, 2.4, 0.35, 0.05), gr))
        for sz in (-1, 1):
            teile.append((ell(6.2, 2.0, sz * 0.7, 0.35, 0.35, 0.3), w.b("yellow_concrete")))
            teile.append((kap((3, 0.6, sz * 1.4), (3.5, -0.3, sz * 2.6), 0.4), gr))
            teile.append((kap((-3, 0.6, sz * 1.4), (-3.5, -0.3, sz * 2.6), 0.4), gr))
            for i in range(4):
                teile.append((kegel(6.8 + i * 0.7, sz * 0.75, 1.0, 1.5, 0.15, 0.03), za))
        figur(w, 0.9 * s + 0.5, teile, (-13, -1, -4), (11, 4, 4), pos=(px, 0, round(math.sin(px / 6) * 2)),
              winkel=ang)
    for z in (-bw, bw):
        for x in (-2, 2):
            w.setze(x, yb + 2, z, w.b("torch"))
    ranken(w, 0.04)
    baumrand(w, zellen, R, 4 + 2 * g, seed, innen=0.8)
    return w


def expeditionslager(seed, g=1):
    """Expeditionslager: Segeltuchzelte, ein Kartentisch unter einem Sonnensegel, Kisten mit Fundstücken, ein
    Funkmast aus Bambus, Hängematten zwischen den Bäumen und ein freigelegter Steinkopf im Hintergrund."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = boden(w, R, 0.15)
    for k in range(2 + g):
        cx, cz = -int(R * 0.45) + k * int(4 * s + 3), -int(R * 0.35)
        L = int(2 * s + 3)
        for x in range(cx - L, cx + L + 1):
            for h in range(3):
                for z in (cz - 2 + h, cz + 2 - h):
                    w.setze(x, 1 + h, z, w.b("white_wool" if k % 2 else "light_gray_wool"))
        w.setze(cx - L, 1, cz, w.b("air"))
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, 4, z, w.b("white_carpet") if (x + z) % 2 else w.b("light_gray_carpet"))
            if abs(x) == 2 and abs(z) == 2:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("bamboo_fence"))
    w.setze(0, 1, 0, w.b("cartography_table"))
    w.setze(1, 1, 0, w.b("jungle_fence"))
    w.setze(1, 2, 0, w.b("lantern", hanging=False, waterlogged=False))
    for k in range(3 + g):
        w.setze(int(R * 0.3) + k % 2, 1 + k // 2, int(R * 0.1), w.b("barrel", facing="up", open=False) if k % 2 else
                w.b("chest", facing="west", type="single", waterlogged=False))
    mx = -int(R * 0.2)
    for y in range(1, int(8 * s + 6)):
        w.setze(mx, y, int(R * 0.35), w.b("bamboo_block", axis="y"))
    w.setze(mx, int(8 * s + 6), int(R * 0.35), w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    hx = int(R * 0.45)
    for x in (hx, hx + 6):
        baum(w, x, 1, -int(R * 0.1), seed, 8 + 2 * s)
    for x in range(hx + 1, hx + 6):
        w.setze(x, 3 - (1 if 2 <= x - hx <= 4 else 0), -int(R * 0.1), w.b("green_wool"))
    st = moosstein(w)
    teile = [(ell(0, 3.5, 0, 2.6, 3.4, 2.4), w.b("mossy_cobblestone")), (kasten(-1.6, 3.6, 2.0, -0.4, 4.4, 2.6), None),
             (kasten(0.4, 3.6, 2.0, 1.6, 4.4, 2.6), None), (kasten(-1.2, 1.4, 2.0, 1.2, 2.0, 2.6), None),
             (ell(0, 2.8, 2.2, 0.8, 1.2, 0.6), w.b("stone"))]
    figur(w, 0.8 * s + 0.4, teile, (-4, -1, -4), (4, 8, 4), pos=(int(R * 0.1), 0, int(R * 0.65)), winkel=math.pi)
    _ = (st, zellen)
    baumrand(w, zellen, R, 3 + 2 * g, seed, innen=0.85)
    return w


def cenote(seed, g=2):
    """Cenote: ein kreisrundes, tiefes Erdloch im Urwald mit senkrechten Kalksteinwänden, türkisem Wasser am
    Grund, herabhängenden Luftwurzeln und Lianen sowie einer in den Fels gehauenen Treppe."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 7)
    zellen = boden(w, R, 0.3)
    rc = R * 0.45
    D = int(8 * s + 6)
    kalk = M(w, [("calcite", 2), ("smooth_sandstone", 1), ("diorite", 1), ("mossy_cobblestone", 1)])
    for x in range(-int(rc) - 4, int(rc) + 5):
        for z in range(-int(rc) - 4, int(rc) + 5):
            d = math.hypot(x, z)
            if d <= rc:
                for y in range(-D + 2, 4):
                    w.bloecke.pop((x, y, z), None)
                w.setze(x, -D, z, w.b("water", level=0))
                w.setze(x, -D + 1, z, w.b("water", level=0))
                w.setze(x, -D - 1, z, w.b("sand"))
            elif d <= rc + 3:
                for y in range(-D - 1, 1):
                    w.setze(x, y, z, kalk(x, y, z))
    rng = w.rng
    for i in range(int(rc * 6)):
        a = i / (rc * 6) * 2 * math.pi
        x, z = round(math.cos(a) * (rc - 0.2)), round(math.sin(a) * (rc - 0.2))
        if rng.random() < 0.35:
            L = int(2 + rng.random() * D * 0.8)
            for k in range(L):
                w.setze(x, -k, z, w.b("hanging_roots") if k > L - 2 else w.b("vine", north=z < 0, south=z > 0,
                                                                            east=x > 0, west=x < 0, up=False), False)
    for k in range(D):
        ang = k * 0.35
        x, z = round(math.cos(ang) * (rc - 0.5)), round(math.sin(ang) * (rc - 0.5))
        w.setze(x, -k, z, w.b("smooth_sandstone_slab", type="bottom", waterlogged=False))
        w.setze(x, -k - 1, z, kalk(x, -k - 1, z))
    baumrand(w, zellen, R, 5 + 2 * g, seed, innen=0.8, riesen=1)
    return w


def affenfelsen(seed, g=2):
    """Affenfelsen: ein zerklüfteter, moosbedeckter Fels mit Nischen und einem eingestürzten Tempelportal, auf
    dem eine Horde brauner Affen-Figuren sitzt, klettert und an Lianen hängt."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = boden(w, R, 0.2)
    rn = Rauschen(w, 3)
    H = 8 * s + 5
    fels = M(w, [("stone", 2), ("mossy_cobblestone", 2), ("andesite", 1), ("moss_block", 1)])
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z * 1.3)
            if d < R * 0.6:
                h = int(H * (1 - (d / (R * 0.6)) ** 1.5) + rn(x, 0, z) * 3)
                for y in range(1, h + 1):
                    w.setze(x, y, z, fels(x, y, z))
    st = moosstein(w)
    for x in range(-3, 4):
        for y in range(1, 6):
            if abs(x) == 3 or y == 5:
                w.setze(x, y, round(R * 0.6 / 1.3), st(x, y, 0))
            else:
                for z in range(round(R * 0.6 / 1.3) - 4, round(R * 0.6 / 1.3) + 1):
                    w.bloecke.pop((x, y, z), None)
    br = w.b("brown_wool")
    hell = w.b("white_terracotta")
    rng = w.rng
    for k in range(5 + 2 * g):
        a = rng.random() * 6.28
        d = rng.random() * R * 0.5
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y = max([yy for yy in range(0, int(H) + 5) if not w.frei(x, yy, z)] or [0]) + 1
        teile = [(ell(0, 1.4, 0, 0.8, 1.0, 0.7), br), (ell(0, 2.8, 0.1, 0.6, 0.6, 0.6), br),
                 (ell(0, 2.7, 0.55, 0.4, 0.35, 0.2), hell), (ell(0.55, 2.9, 0, 0.2, 0.25, 0.15), br),
                 (ell(-0.55, 2.9, 0, 0.2, 0.25, 0.15), br),
                 (kap((0.6, 2.0, 0.2), (0.9, 0.8, 0.6), 0.22), br), (kap((-0.6, 2.0, 0.2), (-0.9, 0.8, 0.6), 0.22), br),
                 (kap((0, 0.8, -0.6), (0, 2.0, -1.6), 0.15), br)]
        figur(w, 0.6 * s + 0.4, teile, (-2, -1, -2), (2, 4, 2), pos=(x, y, z), winkel=rng.random() * 6.28)
    ranken(w, 0.06)
    baumrand(w, zellen, R, 3 + 2 * g, seed, innen=0.82)
    return w


def wurzeltor(seed, g=2):
    """Wurzeltor: ein uralter Urwaldriese, dessen gewaltige Brettwurzeln ein natürliches Tor bilden, durch das ein
    gepflasterter Weg führt; in der Wurzelhöhle steht ein kleiner Schrein mit Laterne."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 7)
    zellen = boden(w, R, 0.2)
    H = int(18 * s + 10)
    yb = int(4 * s + 4)
    for sx in (-1, 1):
        pts = bez((sx * (3 * s + 3), 0, 0), (sx * (2 * s + 2), yb * 0.8, 0), (sx * 1.0, yb + 1, 0))
        rohr(w, pts, 1.6 * s + 1, 1.4 * s + 0.8, mat=w.b("jungle_wood", axis="y"), rauh=0.12)
    rohr(w, bez((0, yb, 0), (0.3, (yb + H) / 2, 0.2), (0, H, 0)), 1.8 * s + 1, 1.0 * s + 0.6,
         mat=w.b("jungle_log", axis="y"), rauh=0.08)
    for k in range(6):
        a = k / 6 * 2 * math.pi + 0.5
        if abs(math.cos(a)) > 0.85:
            continue
        pts = bez((0, yb, 0), (math.cos(a) * 3 * s, yb * 0.6, math.sin(a) * 3 * s),
                  (math.cos(a) * (6 * s + 3), 0, math.sin(a) * (6 * s + 3)))
        rohr(w, pts, 0.9 * s + 0.4, 0.4, mat=w.b("jungle_wood", axis="y"))
    for k in range(5):
        a = k / 5 * 2 * math.pi
        rohr(w, bez((0, H * 0.8, 0), (math.cos(a) * 4 * s, H, math.sin(a) * 4 * s),
                    (math.cos(a) * (7 * s + 2), H + 1, math.sin(a) * (7 * s + 2))), 0.6 * s + 0.3, 0.3,
             mat=w.b("jungle_log", axis="y"))
        laubball(w, math.cos(a) * (7 * s + 2), H + 2, math.sin(a) * (7 * s + 2), 3 * s + 1.5,
                 arten=("jungle_leaves",), dicht=0.85)
    laubball(w, 0, H + 3, 0, 4 * s + 2, arten=("jungle_leaves",), dicht=0.85)
    for z in range(-R + 2, R - 1):
        for x in (-1, 0, 1):
            if w.frei(x, 1, z):
                w.setze(x, zellen.get((x, z), 0), z, w.b("mossy_cobblestone" if (x + z) % 3 else "cobblestone"))
    w.setze(0, 1, -2, w.b("mossy_stone_bricks"))
    w.setze(0, 2, -2, w.b("lantern", hanging=False, waterlogged=False))
    ranken(w, 0.05)
    return w


def sonnenstein(seed, g=2):
    """Sonnenstein: eine riesige, aufrecht stehende Steinscheibe mit konzentrischen Ringen, Strahlenzacken und
    einem Gesicht in der Mitte, in Ocker, Türkis und Rot bemalt, auf einem Sockel mit Treppe."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = boden(w, R, 0.2)
    rs = 6 * s + 4
    yc = int(rs) + 3
    for k in range(2):
        a = int(rs * 0.6) + 2 - k
        for x in range(-a, a + 1):
            for z in range(-3 - k, 4 - k):
                w.setze(x, 1 + k, z, w.b("smooth_sandstone" if k else "cut_sandstone"))
    for x in range(-int(rs) - 2, int(rs) + 3):
        for y in range(-int(rs) - 2, int(rs) + 3):
            d = math.hypot(x, y)
            ang = math.atan2(y, x)
            if d <= rs:
                ring = int(d / (rs / 5))
                farbe = ["yellow_terracotta", "smooth_sandstone", "cyan_terracotta", "smooth_sandstone",
                         "red_terracotta", "smooth_sandstone"][min(5, ring)]
                if ring == 0:
                    gesicht = (abs(x) == 1 and y == 1) or (y == -1 and abs(x) <= 1)
                    farbe = "black_terracotta" if gesicht else "orange_terracotta"
                if ring == 3 and int((ang + math.pi) * 16 / (2 * math.pi)) % 2 == 0:
                    farbe = "chiseled_sandstone"
                w.setze(x, yc + y, 0, w.b(farbe))
                w.setze(x, yc + y, 1, w.b("cut_sandstone"))
            elif d <= rs + 2 and int((ang + math.pi) * 8 / (2 * math.pi) * 2) % 2 == 0 and d <= rs + 2 - \
                    abs(((ang + math.pi) * 16 / (2 * math.pi)) % 2 - 1) * 2:
                w.setze(x, yc + y, 0, w.b("yellow_terracotta"))
    moos_oben(w, 0.15)
    baumrand(w, zellen, R, 4 + 2 * g, seed, innen=0.85)
    return w


def maisterrassen(seed, g=2):
    """Maisterrassen: ein Hang mit Terrassenfeldern hinter Stützmauern aus Bruchstein, bepflanzt mit Mais (hohen
    Bambus-Stauden), Bohnen und Kürbissen, verbunden durch Treppen und eine Bewässerungsrinne."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    st = M(w, [("cobblestone", 2), ("mossy_cobblestone", 2), ("stone", 1)])
    n = 4 + g
    rng = w.rng
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) > R:
                continue
            k = min(n - 1, max(0, int((z + R) / (2 * R) * n)))
            h = (n - 1 - k) * 2
            for y in range(-2, h + 1):
                rand = (z + R) % max(1, int(2 * R / n)) == 0 and y >= h - 1
                w.setze(x, y, z, st(x, y, z) if rand else w.b("dirt"))
            obenauf = w.b("farmland", moisture=7) if x % 6 else w.b("water", level=0)
            w.setze(x, h, z, obenauf)
            if x % 6:
                q = rng.random()
                if k % 3 == 0:
                    w.setze(x, h + 1, z, w.b("bamboo", age=0, leaves="large", stage=0))
                    w.setze(x, h + 2, z, w.b("bamboo", age=0, leaves="small", stage=0))
                elif k % 3 == 1:
                    w.setze(x, h + 1, z, w.b("wheat", age=7) if q < 0.8 else w.b("pumpkin"))
                else:
                    w.setze(x, h + 1, z, w.b("carrots", age=7) if q < 0.7 else w.b("melon"))
    for k in range(n * 2):
        z = -R + k * R // n
        w.setze(0, (n - 1) * 2 - k + 1, z, treppe(w, "cobblestone", "north"))
    return w


def orchideenpavillon(seed, g=1):
    """Orchideen-Pavillon: ein erhöhter, offener Pavillon aus Dschungelholz mit geschwungenem Dach, an dessen
    Pfosten und Balken bunte Orchideen in Töpfen und Blütenranken hängen, darunter ein Seerosenbecken."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = boden(w, R, 0.15)
    A = int(3 * s + 3)
    y0 = 3
    for x in range(-A - 2, A + 3):
        for z in range(-A - 2, A + 3):
            if max(abs(x), abs(z)) <= A + 2:
                w.setze(x, 0, z, w.b("water", level=0) if max(abs(x), abs(z)) <= A + 1 else w.b("mossy_stone_bricks"))
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            w.setze(x, y0, z, w.b("jungle_planks"))
            if max(abs(x), abs(z)) == A and (x + z) % 2 == 0:
                w.setze(x, y0 + 1, z, w.b("jungle_fence"))
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in range(0, y0 + 5):
                w.setze(sx * A, y, sz * A, w.b("stripped_jungle_log", axis="y"))
    satteldach(w, -A, -A, A, A, y0 + 5, Dachmat(w, ["jungle", "mangrove"]), first_x=True, ue=2, giebel=None,
               traufe="jungle", steil=1)
    blueten = ["potted_allium", "potted_pink_tulip", "potted_azure_bluet", "potted_red_tulip", "potted_blue_orchid"]
    rng = w.rng
    for k in range(int(8 * s + 4)):
        x, z = int((rng.random() - 0.5) * 2 * A), int((rng.random() - 0.5) * 2 * A)
        if max(abs(x), abs(z)) == A - 1 or rng.random() < 0.3:
            w.setze(x, y0 + 1, z, w.b(blueten[k % 5]), False)
    for (x, y, z), b in list(w.bloecke.items()):
        if y > y0 + 3 and w.frei(x, y - 1, z) and rng.random() < 0.05:
            for k in range(1, 3):
                w.setze(x, y - k, z, w.b("flowering_azalea_leaves", persistent=True, distance=1, waterlogged=False),
                        False)
    for k in range(y0):
        w.setze(0, y0 - k, A + 1 + k, treppe(w, "jungle", "north"))
    for x in range(-A, A + 1, 2):
        w.setze(x, 1, -A - 1, w.b("lily_pad"))
    baumrand(w, zellen, R, 3 + 2 * g, seed, innen=0.85)
    return w


def einbaumwerft(seed, g=1):
    """Einbaum-Werft: am Ufer eines Flusses werden Kanus aus ganzen Stämmen gefertigt – ein halb ausgehöhlter
    Stamm auf Böcken, fertige Einbäume am Steg, Paddel, Schnitzwerkzeug und ein Bootsdach aus Palmwedeln."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = boden(w, R, 0.1)
    for x in range(-R - 2, R + 3):
        for z in range(int(R * 0.3), R + 3):
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
    L = int(4 * s + 4)
    for x in range(-L, L + 1):
        for z in (-1, 0, 1):
            for y in (2, 3):
                hohl = abs(x) < L - 1 and z == 0 and y == 3 and x < L * 0.3
                if not hohl:
                    w.setze(x, y, z, w.b("jungle_log", axis="x"))
    for x in (-L + 1, L - 1):
        w.setze(x, 1, -1, w.b("jungle_fence"))
        w.setze(x, 1, 1, w.b("jungle_fence"))
    for k in range(2 + g):
        z0 = int(R * 0.45) + k * 3
        for x in range(-L, L + 1):
            for z in (z0 - 1, z0 + 1):
                if abs(x) < L - 1 or z == z0:
                    w.setze(x, 1, z, w.b("stripped_jungle_log", axis="x"))
            w.setze(x, 0, z0, w.b("stripped_jungle_log", axis="x"))
        w.setze(0, 1, z0, w.b("jungle_trapdoor", facing="north", half="bottom", open=False, powered=False,
                              waterlogged=True))
    for z in range(int(R * 0.3), int(R * 0.3) + int(5 * s + 3)):
        for x in (L + 2, L + 3):
            w.setze(x, 1, z, w.b("jungle_planks"))
    for x in range(-L - 2, L + 3):
        for z in range(-3, 4):
            if abs(x) == L + 2 and abs(z) == 3:
                for y in range(1, 6):
                    w.setze(x, y, z, w.b("bamboo_block", axis="y"))
            w.setze(x, 6, z, w.b("jungle_leaves", persistent=True, distance=1, waterlogged=False))
    baumrand(w, {k: v for k, v in zellen.items() if k[1] < R * 0.3}, R, 3 + 2 * g, seed, innen=0.85)
    return w


def adlerhorst(seed, g=2):
    """Adlerhorst im Urwaldriesen: ein einzelner, weit herausragender Urwaldriese trägt in seiner Krone ein
    riesiges Nest aus Ästen, in dem ein mächtiger Harpyien-Adler mit Federhaube wacht."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = boden(w, R, 0.2)
    H = int(26 * s + 14)
    rohr(w, bez((0, 0, 0), (1.0, H * 0.5, 0.6), (0, H, 0)), 1.6 * s + 1.2, 0.8 * s + 0.6,
         mat=w.b("jungle_log", axis="y"), rauh=0.1)
    for k in range(4):
        a = k / 4 * 2 * math.pi
        rohr(w, bez((0, 1, 0), (math.cos(a) * 3 * s, 0.5, math.sin(a) * 3 * s),
                    (math.cos(a) * (5 * s + 2), -1, math.sin(a) * (5 * s + 2))), 1.0 * s + 0.5, 0.4,
             mat=w.b("jungle_wood", axis="y"))
    rn = 3.5 * s + 2.5
    for k in range(int(2 * s + 2)):
        for x, z in kreisrand(rn - k * 0.3):
            w.setze(x, H + k, z, w.b("stripped_jungle_wood", axis="y") if (x + z + k) % 3 else w.b("jungle_wood",
                                                                                                     axis="y"))
    for x in range(-int(rn), int(rn) + 1):
        for z in range(-int(rn), int(rn) + 1):
            if math.hypot(x, z) < rn - 1:
                w.setze(x, H, z, w.b("hay_block", axis="y"))
    for k in range(5):
        a = k / 5 * 2 * math.pi + 0.3
        laubball(w, math.cos(a) * (rn + 3), H - 2, math.sin(a) * (rn + 3), 2.5 * s + 1.5, arten=("jungle_leaves",),
                 dicht=0.85)
    gr = w.b("light_gray_wool")
    dk = w.b("gray_wool")
    sch = w.b("black_wool")
    we = w.b("white_wool")
    teile = [(ell(0, 2.4, 0, 1.4, 2.0, 1.2), dk), (ell(0.4, 2.2, 0, 1.0, 1.6, 0.9), we),
             (ell(0.3, 4.6, 0, 1.0, 1.0, 1.0), gr), (kap((1.1, 4.5, 0), (1.7, 3.9, 0), 0.35, 0.15), sch),
             (ell(0.9, 4.9, 0.55, 0.2, 0.2, 0.15), sch), (ell(0.9, 4.9, -0.55, 0.2, 0.2, 0.15), sch),
             (kap((-0.3, 5.4, 0), (-1.0, 6.3, 0), 0.4, 0.15), dk), (kap((-0.2, 5.5, 0.4), (-0.8, 6.2, 0.9), 0.3, 0.1), dk),
             (kap((-0.2, 5.5, -0.4), (-0.8, 6.2, -0.9), 0.3, 0.1), dk),
             (ell(-0.5, 2.8, 1.3, 1.0, 1.6, 0.35), dk), (ell(-0.5, 2.8, -1.3, 1.0, 1.6, 0.35), dk),
             (kap((-1.2, 1.4, 0), (-2.4, 0.4, 0), 0.6, 0.3), dk),
             (kap((0.4, 0.8, 0.5), (0.6, 0, 0.6), 0.25), w.b("yellow_concrete")),
             (kap((0.4, 0.8, -0.5), (0.6, 0, -0.6), 0.25), w.b("yellow_concrete"))]
    figur(w, 0.8 * s + 0.4, teile, (-3, -1, -3), (3, 7, 3), pos=(0, H + 1, 0), winkel=0.6)
    baumrand(w, zellen, R, 5 + 2 * g, seed, innen=0.6, H=(8, 14))
    return w


def jademaske(seed, g=2):
    """Jade-Maske: eine gewaltige Mosaikmaske aus grünen und türkisen Steinen mit Augen aus Perlmutt und
    Obsidian, Ohrpflöcken und Federkrone, eingelassen in eine bemooste Tempelwand am Hang."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = boden(w, R, 0.2)
    st = moosstein(w)
    Hm = 7 * s + 5
    Bm = 5 * s + 4
    wz = -int(R * 0.2)
    Bw = int(Bm + 4 * s + 3)
    for x in range(-Bw, Bw + 1):
        for y in range(1, int(Hm * 2 + 4)):
            for z in range(wz - 3, wz + 1):
                w.setze(x, y, z, st(x, y, z))
    jade = M(w, [("emerald_block", 1), ("green_terracotta", 2), ("lime_terracotta", 1), ("cyan_terracotta", 2),
                 ("prismarine", 1)], zelle=1.0)
    yc = Hm + 2
    for x in range(-int(Bm) - 1, int(Bm) + 2):
        for y in range(-int(Hm) - 1, int(Hm) + 2):
            if (x / Bm) ** 2 + (y / Hm) ** 2 > 1:
                continue
            z = wz + 1 + round(1.5 * s * math.sqrt(max(0, 1 - (x / Bm) ** 2 - (y / Hm) ** 2)))
            for zz in range(wz + 1, z + 1):
                w.setze(x, yc + y, zz, jade(x, y, zz))
            auge = abs(abs(x) - Bm * 0.42) < Bm * 0.2 and abs(y - Hm * 0.25) < Hm * 0.1
            pupille = abs(abs(x) - Bm * 0.42) < Bm * 0.07 and abs(y - Hm * 0.25) < Hm * 0.1
            mund = abs(x) < Bm * 0.35 and abs(y + Hm * 0.45) < Hm * 0.07
            if auge:
                w.setze(x, yc + y, z, w.b("obsidian" if pupille else "white_concrete"))
            elif mund:
                w.setze(x, yc + y, z, w.b("red_terracotta"))
            elif abs(x) < 1 and -Hm * 0.25 < y < Hm * 0.15:
                w.setze(x, yc + y, z + 1, jade(x, y, z))
    for sx in (-1, 1):
        kugel(w, sx * (Bm + 1.2), yc, wz + 2, 1.0 + 0.5 * s, w.b("gold_block"))
    for k in range(9):
        a = math.pi * (0.15 + 0.7 * k / 8)
        for t in range(int(4 * s + 3)):
            x = round(math.cos(a) * (Hm * 0.9 + t))
            y = round(yc + math.sin(a) * (Hm * 0.9 + t))
            w.setze(x, y, wz + 1, w.b(["red_wool", "lime_wool", "cyan_wool", "yellow_wool"][k % 4]))
    ranken(w, 0.04)
    moos_oben(w, 0.2)
    baumrand(w, zellen, R, 3 + 2 * g, seed, innen=0.85)
    return w


def fruchthain(seed, g=1):
    """Fruchthain: ein Hain aus niedrigen Fruchtbäumen mit Kakaoschoten, Melonen- und Kürbisbeeten, Beeren-
    büschen und einer Saftpresse unter einem Blätterdach, dazwischen gewundene Trampelpfade."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = boden(w, R, 0.2, dichte=0.5)
    rng = w.rng
    for k in range(5 + 3 * g):
        a = rng.random() * 6.28
        d = R * (0.25 + rng.random() * 0.6)
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y0 = zellen.get((x, z), 0) + 1
        H = int(5 + rng.random() * 4 * s)
        for y in range(y0, y0 + H):
            w.setze(x, y, z, w.b("jungle_log", axis="y"))
        laubball(w, x, y0 + H, z, 2.5 + s, arten=("jungle_leaves", "flowering_azalea_leaves"), dicht=0.85)
        for _ in range(int(4 * s + 2)):
            fx, fy, fz = x + int((rng.random() - 0.5) * 4 * s), y0 + H - 1 - int(rng.random() * 2), \
                z + int((rng.random() - 0.5) * 4 * s)
            w.setze(fx, fy, fz, w.b("orange_concrete" if rng.random() < 0.5 else "yellow_concrete"))
        for dx, dz, f in ((1, 0, "west"), (-1, 0, "east")):
            w.setze(x + dx, y0 + 1, z + dz, w.b("cocoa", age=2, facing=f))
    for _ in range(int(16 * s + 8)):
        x, z = int((rng.random() - 0.5) * R * 1.6), int((rng.random() - 0.5) * R * 1.6)
        if (x, z) in zellen and w.frei(x, zellen[(x, z)] + 1, z):
            q = rng.random()
            w.setze(x, zellen[(x, z)] + 1, z, w.b("melon") if q < 0.3 else w.b("pumpkin") if q < 0.45 else
                    w.b("sweet_berry_bush", age=3))
    for x in range(-2, 3):
        for z in range(-2, 3):
            if abs(x) == 2 and abs(z) == 2:
                for y in range(1, 4):
                    w.setze(x, y, z, w.b("jungle_fence"))
            w.setze(x, 4, z, w.b("jungle_leaves", persistent=True, distance=1, waterlogged=False))
    w.setze(0, 1, 0, w.b("barrel", facing="up", open=False))
    w.setze(1, 1, 0, w.b("piston", facing="down", extended=False))
    return w


DSCHUNGEL3 = {
    "baumkronenpfad": ("Baumkronenpfad", baumkronenpfad),
    "pfeilgiftfrosch": ("Pfeilgiftfrosch-Statue", pfeilgiftfrosch),
    "papageienvoliere": ("Papageien-Voliere", papageienvoliere),
    "schneckenturm": ("Schneckenturm-Sternwarte", schneckenturm),
    "aquaedukt": ("Überwucherter Aquädukt", aquaedukt),
    "kakaoplantage": ("Kakao-Plantage", kakaoplantage),
    "riesenseerosen": ("Riesenseerosen-Teich", seerosenteich),
    "schamanenhuette": ("Schamanenhütte", schamanenhuette),
    "krokodilwaechter": ("Krokodil-Wächter", krokodilwaechter),
    "expeditionslager": ("Expeditionslager", expeditionslager),
    "cenote": ("Cenote", cenote),
    "affenfelsen": ("Affenfelsen", affenfelsen),
    "wurzeltor": ("Wurzeltor", wurzeltor),
    "sonnenstein": ("Sonnenstein", sonnenstein),
    "maisterrassen": ("Maisterrassen", maisterrassen),
    "orchideenpavillon": ("Orchideen-Pavillon", orchideenpavillon),
    "einbaumwerft": ("Einbaum-Werft", einbaumwerft),
    "adlerhorst": ("Adlerhorst im Urwaldriesen", adlerhorst),
    "jademaske": ("Jade-Maske", jademaske),
    "fruchthain": ("Fruchthain", fruchthain),
}

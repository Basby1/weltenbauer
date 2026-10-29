"""Ruinen & Vergessenes – Erweiterung der Kategorie „Ruinen“: Burgruine, Klosterruine, Aquädukt, versunkene Stadt,
überwucherte Stadt, Turmstumpf, Säulenfeld, gestürzter Koloss, Ruinentor, eingestürzte Brücke, Mühlenruine,
Kaminruine, verlassene Mine, Schiff im Wald, Observatoriumsruine, Steinkreis, Amphitheater, Bibliothek, Pyramidenstumpf,
verlassenes Dorf, Thronsaal, Brunnen, Wachturm, gefallener Riese, vergessener Garten und Portalruine. Boden y = 0."""

from __future__ import annotations

import math

import numpy as np

import pracht as P
import wald2
from flora import _lv, _neu, _r, _stil, linie
from haeuser import HAUSPOOL
from lib import Rauschen, einfuegen
from pracht import Mat, gelaende
from veredeln import bewuchs

U = [0.6, 1.0, 1.7, 2.8]


def stein(w, seed):
    if _stil(seed) == 0:
        return Mat(w, ["stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "cobblestone",
                       "mossy_cobblestone", "andesite"])
    return Mat(w, ["sandstone", "cut_sandstone", "smooth_sandstone", "chiseled_sandstone", "mossy_cobblestone"])


def verfallen(w, staerke=0.5, ab_y=3, moos=0.08, ranken=0.08, schutt=True, rn=None):
    """Lässt einen Bau verfallen: oben bröckelt mehr ab (rauschgesteuert), Schutt am Boden, Moos und Ranken."""
    rn = rn or Rauschen(w, 3)
    rng = w.rng
    ys = [p[1] for p in w.bloecke]
    ymax = max(ys) if ys else 1
    entfernt = []
    for (x, y, z) in list(w.bloecke):
        if y < ab_y:
            continue
        t = (y - ab_y) / max(1, ymax - ab_y)
        if rn(x, y, z) * 0.6 + rng.random() * 0.4 < staerke * (0.35 + t):
            n = w.P.name(w.bloecke[(x, y, z)])
            if "grass_block" in n or "dirt" in n:
                continue
            entfernt.append((x, y, z, w.bloecke.pop((x, y, z))))
    if schutt:
        for (x, y, z, b) in entfernt[::7]:
            n = w.P.name(b)
            if not any(k in n for k in ("stone", "brick", "cobble", "sandstone", "andesite", "quartz")):
                continue
            dx, dz = int(rng.integers(-3, 4)), int(rng.integers(-3, 4))
            yy = 1
            while (x + dx, yy, z + dz) in w.bloecke and yy < 4:
                yy += 1
            w.setze(x + dx, yy, z + dz, b, False)
    schwebend_entfernen(w)
    bewuchs(w, moos=moos, ranken=ranken)
    return w


def schwebend_entfernen(w):
    """Entfernt Blöcke ohne Verbindung zum Boden (Flutfüllung von y <= 1 aus), damit nichts in der Luft hängt."""
    from collections import deque
    pos = set(w.bloecke)
    gesehen = {p for p in pos if p[1] <= 1}
    q = deque(gesehen)
    while q:
        x, y, z = q.popleft()
        for n in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
            if n in pos and n not in gesehen:
                gesehen.add(n)
                q.append(n)
    for p in pos - gesehen:
        del w.bloecke[p]
    return w


def stil_haus(w, pool, **kw):
    d = dict(HAUSPOOL[pool])
    d.update(kw)
    return P.Stil(w, **d)


def baeume(w, n, R, arten=("birke", "oak")):
    rng = w.rng
    for k in range(n):
        a = rng.random() * 6.28
        d = R * (0.3 + 0.6 * rng.random())
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        art = arten[k % len(arten)]
        sd = int(rng.integers(1, 10 ** 6))
        b = wald2.birke(sd, H=6 + int(rng.integers(4))) if art == "birke" else \
            wald2.laubbaum(sd, art, H=6 + int(rng.integers(5)))
        einfuegen(w, b, x, 0, z)


# ============================================================================ Bauten

def burgruine(seed, g=2):
    """Burgruine: ein zerfallener Bergfried mit leeren Fensterhöhlen, Reste der Ringmauer mit Turmstümpfen, ein
    zugewachsener Graben und Bäume im Burghof."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R + 4, art="wiese", dichte=0.35)
    st = P.Stil(w, wand="graustein" if _stil(seed) == 0 else "sandstein", sockel="graustein", gesims="stone_brick",
                dach="schiefer", holz="spruce")
    P.turm(w, st, 0, -R // 4, 1, _r(18 * u + 6), _r(3.5 * u + 2), form="eckig", dach="platt", krone=True)
    M = stein(w, seed)
    for k in range(int(R * 7)):
        a = k / (R * 7) * 6.28
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        for y in range(1, _r(6 * u + 3)):
            w.setze(x, y, z, M(x, y, z, y / 8))
    for k in range(4):
        a = k * 1.57 + 0.78
        P.turm(w, st, round(math.cos(a) * R), round(math.sin(a) * R), 1, _r(9 * u + 4), 2.5 * u + 1, dach="platt",
               krone=True)
    verfallen(w, 0.75, ab_y=2)
    baeume(w, 2 + g, R * 0.7)
    return w


def klosterruine(seed, g=2):
    """Klosterruine: ein Kreuzgang aus Rundbögen um einen verwilderten Garten, die Kirchenwand mit großem leeren
    Maßwerkfenster steht noch, Efeu überall."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R + 3, art="wiese", dichte=0.4)
    M = stein(w, seed)
    a = _r(7 * u + 3)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if max(abs(x), abs(z)) in (a, a - 3):
                for y in range(1, 6):
                    aussen = max(abs(x), abs(z)) == a
                    bogen = not aussen and ((x if abs(z) >= abs(x) else z) % 3 != 0) and y < 4
                    if not bogen:
                        w.setze(x, y, z, M(x, y, z, y / 6))
            if max(abs(x), abs(z)) == a - 2 or max(abs(x), abs(z)) == a - 1:
                w.setze(x, 6, z, M(x, 6, z, 0.9))
    H = _r(14 * u + 5)
    for x in range(-a, a + 1):
        for y in range(1, H):
            fenster = abs(x) < a * 0.4 and H * 0.25 < y < H * 0.85
            if not fenster or (x % 3 == 0 and y < H * 0.8):
                w.setze(x, y, -a - 4, M(x, y, -a - 4, y / H))
    verfallen(w, 0.55, ab_y=3, ranken=0.2)
    baeume(w, 1 + g // 2, 3)
    return w


def aquaedukt(seed, g=2):
    """Aquäduktruine: eine Reihe hoher Doppelbögen trägt die Wasserrinne über ein Tal, mittendrin sind mehrere Bögen
    eingestürzt und liegen als Trümmer im Gras."""
    w = _neu(seed)
    u = U[g]
    L = _r(22 * u + 8)
    gelaende(w, L + 3, art="wiese", dichte=0.35)
    M = stein(w, seed)
    H1 = _r(8 * u + 4)
    H2 = _r(4 * u + 3)
    bw = _r(1.6 * u + 1.5)
    per = 2 * bw + 2

    def bogenreihe(y0, y1, per, bw, tiefe):
        for x in range(-L, L + 1):
            ph = (x + L) % per
            for z in range(-tiefe, tiefe + 1):
                for y in range(y0, y1 + 1):
                    if ph >= 2:
                        t = (ph - 2 + 0.5) / bw - 1
                        if y < y1 - 1 - (1 - math.sqrt(max(0, 1 - t * t))) * bw * 0.9 - 0.5 and y < y1 - 1:
                            continue
                    w.setze(x, y, z, M(x, y, z, y / (H1 + H2)))
    bogenreihe(1, H1, per, bw, 1)
    bogenreihe(H1 + 1, H1 + H2, bw + 1, max(1, (bw - 1) // 2 + 1), 1)
    for x in range(-L, L + 1):
        for z in (-1, 1):
            w.setze(x, H1 + H2 + 1, z, M(x, 0, z, 0.9))
        w.setze(x, H1 + H2 + 1, 0, w.b("moss_block" if x % 3 else "grass_block"))
    luecke = range(-round(L * 0.18), round(L * 0.12))
    for x in luecke:
        for y in range(1, H1 + H2 + 3):
            for z in (-1, 0, 1):
                w.bloecke.pop((x, y, z), None)
    rng = w.rng
    for k in range(int(30 * u)):
        x = int(rng.integers(luecke.start - 2, luecke.stop + 2))
        z = int(rng.integers(-4, 5))
        yy = 1
        while (x, yy, z) in w.bloecke:
            yy += 1
        if yy < 4:
            w.setze(x, yy, z, M(x, yy, z, 0.5))
    verfallen(w, 0.25, ab_y=H1, ranken=0.12, schutt=False)
    return w


def versunkene_stadt(seed, g=2):
    """Versunkene Stadt: Dächer, Turmspitzen und Säulen einer alten Stadt ragen aus einem stillen See, Seerosen und
    Schilf zwischen den Mauern."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                for y in range(-5, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -6, z, w.b("mud"))
    rng = w.rng
    pools = ["stein_schiefer", "fachwerk_rot", "kalk_kupfer"]
    for i in range(4 + 2 * g):
        a = i * 2.39996
        d = R * 0.7 * math.sqrt((i + 0.5) / (4 + 2 * g))
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        st = stil_haus(w, pools[i % 3])
        P.gebaeude(w, st, cx - 2, cz - 2, cx + 2, cz + 2, y0=-5, etagen=1 + (i % 2), eh=4, dach="sattel",
                   tuer="south", gauben=False, kamine=0)
    st = stil_haus(w, "stein_schiefer")
    P.turm(w, st, 0, 0, -5, _r(14 * u + 6), 2.5, dach="kegel", krone=False)
    for (x, y, z), b in list(w.bloecke.items()):
        if y == 0 and w.P.name(b) == "minecraft:water" and rng.random() < 0.04:
            w.setze(x, 1, z, w.b("lily_pad"))
    verfallen(w, 0.3, ab_y=0, moos=0.1, ranken=0.05, schutt=False)
    return w


def ueberwucherte_stadt(seed, g=2):
    """Überwucherte Stadt: dachlose Steinhäuser in Gassen, aus denen Bäume wachsen, Ranken an den Mauern, ein
    zerbrochener Brunnen auf dem Platz."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    gelaende(w, R, art="wald", dichte=0.5)
    pools = ["stein_schiefer", "fachwerk_ocker", "backstein", "fachwerk_rot"]
    for i in range(5 + 2 * g):
        a = i / (5 + 2 * g) * 6.28
        cx, cz = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        st = stil_haus(w, pools[i % 4])
        P.gebaeude(w, st, cx - 3, cz - 2, cx + 3, cz + 2, y0=1, etagen=1 + (i % 2), eh=4, dach="sattel",
                   tuer="south", gauben=False, kamine=1)
    from haeuser2 import ziehbrunnen
    ziehbrunnen(w, 0, 0)
    verfallen(w, 0.7, ab_y=3, moos=0.1, ranken=0.2)
    baeume(w, 4 + 2 * g, R * 0.8)
    return w


def turmstumpf(seed, g=1):
    """Turmstumpf: ein runder Wehrturm, nur noch halb so hoch wie einst, mit offener Wendeltreppe im aufgerissenen
    Mauerwerk und einem Baum, der oben herauswächst."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.35)
    M = stein(w, seed)
    r = _r(4 * u + 2)
    H = _r(12 * u + 5)
    rn = Rauschen(w, 2)
    for y in range(1, H + 1):
        for k in range(int(r * 8)):
            a = k / (r * 8) * 6.28
            x, z = round(math.cos(a) * r), round(math.sin(a) * r)
            riss = math.cos(a - 0.8) > 0.6 and y > H * (0.3 + 0.4 * rn(x, 0, z))
            if not riss:
                w.setze(x, y, z, M(x, y, z, y / H))
        a = y * 0.6
        w.setze(round(math.cos(a) * (r - 1)), y, round(math.sin(a) * (r - 1)), w.b("stone_brick_slab", type="top",
                                                                                  waterlogged=False))
    verfallen(w, 0.4, ab_y=H // 2)
    einfuegen(w, wald2.birke(seed, H=_r(5 * u + 3)), 0, H // 3, 0)
    return w


def saeulenfeld(seed, g=2):
    """Säulenfeld: Reste eines Tempels auf gestuftem Unterbau – stehende Säulen mit Kapitellen, ein Stück Gebälk,
    gestürzte Säulen in einzelne Trommeln zerbrochen, Moos und hohes Gras."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.5)
    rng = w.rng
    marmor = _stil(seed) == 0
    M = Mat(w, ["smooth_quartz", "calcite", "quartz_bricks", "diorite"] if marmor else
            ["smooth_sandstone", "cut_sandstone", "sandstone", "smooth_sandstone"])
    saeule = (lambda: w.b("quartz_pillar", axis="y")) if marmor else (lambda: w.b("cut_sandstone"))
    liegend = (lambda ax: w.b("quartz_pillar", axis=ax)) if marmor else (lambda ax: w.b("smooth_sandstone"))
    kapitell = w.b("chiseled_quartz_block" if marmor else "chiseled_sandstone")
    a, b = _r(8 * u + 3), _r(4.5 * u + 2)
    for s in range(3):
        for x in range(-a - 3 + s, a + 4 - s):
            for z in range(-b - 3 + s, b + 4 - s):
                w.setze(x, 1 + s, z, M(x, s, z, 0.3 + 0.2 * s))
    y0 = 4
    H = _r(8 * u + 4)
    stehend = []
    for x in range(-a, a + 1, 3):
        for z in (-b, b):
            r = rng.random()
            if r < 0.55:
                h = H if r < 0.3 else int(H * (0.25 + 0.5 * rng.random()))
                for y in range(y0, y0 + h):
                    w.setze(x, y, z, saeule())
                if h == H:
                    w.setze(x, y0 + H, z, kapitell)
                    stehend.append((x, z))
            elif r < 0.85:
                w.setze(x, y0, z, saeule())
                d = 1 if z > 0 else -1
                k = 0
                for k in range(1, int(H * 0.9)):
                    if k % 4 == 0:
                        continue
                    zz = z + d * (k + 1)
                    yy = y0 if abs(zz) <= b + 3 - 2 else 1
                    while (x, yy, zz) in w.bloecke and yy < y0 + 1:
                        yy += 1
                    w.setze(x + (k // 5), yy, zz, liegend("z"))
            else:
                w.setze(x, y0, z, saeule())
    # Gebälk über der längsten Reihe stehender Säulen
    for z in (-b, b):
        xs = sorted(x for (x, zz) in stehend if zz == z)
        for i in range(len(xs) - 1):
            if xs[i + 1] - xs[i] == 3:
                for x in range(xs[i], xs[i + 1] + 1):
                    w.setze(x, y0 + H + 1, z, M(x, 0, z, 0.8))
                    w.setze(x, y0 + H + 2, z, w.b("quartz_slab" if marmor else "smooth_sandstone_slab",
                                                  type="bottom", waterlogged=False))
    # gestürztes Gebälkstück und Statuenkopf
    for x in range(a // 2, a // 2 + 4):
        w.setze(x, y0, 0, M(x, 0, 0, 0.8))
    for p in ((-2, 0, -1), (-2, 0, 0), (-3, 0, 0), (-2, 1, 0)):
        w.setze(p[0], y0 + p[1], p[2], kapitell if p[1] else M(0, 0, 0, 0.5))
    verfallen(w, 0.1, ab_y=y0 + 2, moos=0.08, ranken=0.08, schutt=False)
    return w


def gestuerzter_koloss(seed, g=3):
    """Gestürzter Koloss: von einer Riesenstatue stehen nur noch die Beine auf dem Sockel, Torso und Kopf liegen
    zerbrochen und halb versunken daneben im Sand."""
    from motive import figur
    from skulptur import Skulptur
    from weltwunder import bl, sk
    w = _neu(seed)
    u = U[g]
    R = _r(20 * u + 6)
    sand = _stil(seed) != 0
    M = Mat(w, ["sandstone", "smooth_sandstone", "cut_sandstone", "chiseled_sandstone"] if sand else
            ["stone", "andesite", "stone_bricks", "mossy_stone_bricks", "cobblestone"])
    s = 0.9 * u + 0.4
    S = Skulptur(w, s)
    S.mat("k", sk(M, 0, 30))
    S.mat("a", bl(w, "gold_block" if sand else "oxidized_copper"))
    S.mat("d", bl(w, "sandstone" if sand else "stone"))
    S.mat("g", bl(w, "sandstone" if sand else "andesite"))
    figur(S, "ritter", "stehend")
    S.rendern((-7, -1, -5), (7, 26, 7), versatz=(0.5, 4.01, 0.5))
    schnitt = 4 + 10 * s
    rn = Rauschen(w, 2)
    alles = dict(w.bloecke)
    w.bloecke = {}
    gelaende(w, R, art="sand" if sand else "wiese", dichte=0.25)
    for x in range(-round(3 * s) - 1, round(3 * s) + 2):
        for z in range(-round(2.5 * s) - 1, round(2.5 * s) + 2):
            for y in (1, 2, 3):
                w.setze(x, y, z, M(x, y, z, 0.5))
    oben = {}
    for (x, y, z), b in alles.items():
        grenze = schnitt + 3 * rn(x, 0, z)
        if y <= grenze:
            w.setze(x, y, z, b)
        else:
            oben[(x, y, z)] = b
    if oben:
        ymin = min(p[1] for p in oben)
        zmin = min(p[2] for p in oben)
        x0 = round(4 * s) + 4
        for (x, y, z), b in oben.items():
            ny = (z - zmin) - 1
            if ny >= 1:
                w.setze(x0 + (y - ymin), ny, x + 3, b, True)
    rng = w.rng
    for k in range(int(25 * u)):
        x, z = int(rng.integers(-R // 2, R // 2)), int(rng.integers(-R // 2, R // 2))
        if (x, 1, z) not in w.bloecke or w.P.name(w.bloecke[(x, 1, z)]) in ("minecraft:grass", "minecraft:dead_bush"):
            w.setze(x, 1, z, M(x, 1, z, 0.5))
    verfallen(w, 0.08, ab_y=4, schutt=False, moos=0.03 if sand else 0.1)
    return w


def ruinentor(seed, g=1):
    """Ruinentor: ein einsames, hohes Torhaus ohne Mauern ringsum, mit leerem Bogen, abgebrochenen Zinnen und einem
    Weg, der hindurch ins Nichts führt."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.4)
    M = stein(w, seed)
    B, H = _r(2 * u + 1, 2), _r(9 * u + 4)
    for x in range(-B - 3, B + 4):
        for z in (-2, -1, 0, 1, 2):
            for y in range(1, H + 1):
                if abs(x) <= B and y <= H * 0.6 + math.sqrt(max(0, B * B - x * x)) * 0.6:
                    continue
                w.setze(x, y, z, M(x, y, z, y / H))
    for z in range(-R, R + 1):
        for x in range(-1, 2):
            w.setze(x, 0, z, w.b("gravel" if (x + z) % 3 else "cobblestone"))
    verfallen(w, 0.35, ab_y=H // 2)
    return w


def luftschiffwrack(seed, g=2):
    """Luftschiffwrack: ein abgestürztes Luftschiff liegt schräg in der Wiese – die Hülle aus geflickten Stoffbahnen
    ist hinten aufgerissen und zeigt die Holzspanten, die Gondel hat sich mit dem Bug in die Erde gebohrt, der
    Propeller hängt schief, Kisten liegen verstreut."""
    w = _neu(seed)
    u = U[g]
    A = _r(12 * u + 5)
    Bq = _r(3.6 * u + 2)
    R = A + 6
    gelaende(w, R, art="wiese", dichte=0.45)
    rn = Rauschen(w, 3)
    rng = w.rng
    stoff = ["white_wool", "white_wool", "light_gray_wool", "white_terracotta", "white_wool"]
    neig = 0.22

    def yc(x):
        return Bq + 4 - (x + A) * neig * 0.5

    for x in range(-A, A + 1):
        r = Bq * math.sqrt(max(0.0, 1 - (x / (A + 0.5)) ** 2)) + 0.3
        n = max(8, int(r * 8))
        for k in range(n):
            t = k / n * 6.2832
            y = round(yc(x) + r * math.sin(t))
            z = round(r * math.cos(t))
            if y < 1:
                continue
            offen = x < -A * 0.15 and math.sin(t) > -0.3 and rn(x, y, z) < 0.75
            if offen:
                if (x + A) % 3 == 0:
                    w.setze(x, y, z, w.b("stripped_spruce_log", axis="x"))
                continue
            w.setze(x, y, z, w.b(stoff[int(rn(x * 2, y, z * 2) * 5) % 5]))
        if (x + A) % 3 == 0 and x >= -A * 0.15:
            pass
    for x in range(-A, A + 1, 2):
        y = round(yc(x))
        w.setze(x, y, 0, w.b("stripped_spruce_log", axis="x"), False)
    gl = round(A * 0.45)
    for x in range(-gl, gl + 1):
        yb = round(yc(x) - Bq - 3)
        for z in range(-2, 3):
            for y in range(yb, yb + 3):
                if y < 1:
                    continue
                rand = abs(z) == 2 or y == yb or x in (-gl, gl)
                if rand:
                    fenster = y == yb + 1 and abs(z) == 2 and x % 3 == 0
                    w.setze(x, y, z, w.b("glass_pane", north=False, south=False, east=True, west=True,
                                         waterlogged=False) if fenster else w.b("dark_oak_planks"))
        if x % 4 == 0:
            for y in range(yb + 3, round(yc(x) - Bq * 0.8)):
                if y >= 1:
                    w.setze(x, y, 2, w.b("chain", axis="y", waterlogged=False), False)
                    w.setze(x, y, -2, w.b("chain", axis="y", waterlogged=False), False)
    px = -A - 1
    py = round(yc(-A))
    for d in range(-2, 3):
        w.setze(px, py + d, round(d * 0.4), w.b("spruce_planks"))
        w.setze(px, py, d, w.b("spruce_planks"))
    w.setze(px, py, 0, w.b("iron_block"))
    for k in range(int(8 * u)):
        x, z = int(rng.integers(-R // 2, R // 2)), int(rng.integers(-R // 2, R // 2))
        if (x, 1, z) not in w.bloecke or w.P.name(w.bloecke[(x, 1, z)]) in ("minecraft:grass", "minecraft:fern"):
            w.setze(x, 1, z, w.b(["barrel", "spruce_planks", "white_wool", "chest"][k % 4],
                                 **({"facing": "up", "open": False} if k % 4 == 0 else
                                    {"facing": "north", "type": "single", "waterlogged": False} if k % 4 == 3 else {})))
    for x in range(A - 4, A + 3):
        for z in range(-3, 4):
            if rng.random() < 0.5:
                w.setze(x, 0, z, w.b("coarse_dirt" if rng.random() < 0.6 else "rooted_dirt"))
    schwebend_entfernen(w)
    bewuchs(w, moos=0.0, ranken=0.0)
    return w


def muehlenruine(seed, g=1):
    """Mühlenruine: der steinerne Turm einer Windmühle ohne Dach, ein gebrochener Flügel lehnt an der Wand, der
    Mahlstein liegt im Gras."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.45)
    M = stein(w, seed)
    r = _r(3.5 * u + 1.5)
    H = _r(11 * u + 4)
    for y in range(1, H + 1):
        rr = r * (1 - 0.25 * y / H)
        for k in range(int(rr * 8)):
            a = k / (rr * 8) * 6.28
            w.setze(round(math.cos(a) * rr), y, round(math.sin(a) * rr), M(0, y, 0, y / H))
    for k in range(_r(8 * u + 3)):
        w.setze(r + 1, 1 + k, 2 + k // 2, w.b("spruce_log", axis="y"))
        w.setze(r + 2, 1 + k, 2 + k // 2, w.b("white_wool" if k % 2 else "spruce_fence", **(
            {} if k % 2 else {"north": False, "south": False, "east": False, "west": False, "waterlogged": False})))
    for x in range(-1, 2):
        for z in range(-1, 2):
            w.setze(x - r - 3, 1, z, w.b("smooth_stone_slab", type="bottom", waterlogged=False))
    verfallen(w, 0.3, ab_y=H // 2)
    return w


def kaminruine(seed, g=0):
    """Kaminruine: von einem abgebrannten Haus steht nur noch der gemauerte Kamin mit Feuerstelle, ringsum Reste der
    Grundmauern, verkohlte Balken und Brennnesseln."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.5)
    M = Mat(w, ["bricks", "cobblestone", "mossy_cobblestone", "stone_bricks"])
    a, b = _r(4 * u + 2), _r(3 * u + 2)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            if abs(x) == a or abs(z) == b:
                for y in range(1, 1 + int(w.rng.integers(0, 3))):
                    w.setze(x, y, z, M(x, y, z, 0.3))
            elif w.rng.random() < 0.08:
                w.setze(x, 1, z, w.b("dark_oak_log", axis="x" if (x + z) % 2 else "z")
                        if w.rng.random() < 0.8 else w.b("coal_block"))
    for y in range(1, _r(9 * u + 4)):
        for dx in (0, 1):
            for dz in (0, 1):
                w.setze(-a + dx, y, dz, M(dx, y, dz, y / 8))
    w.setze(-a + 1, 1, 1, w.b("campfire", lit=False, signal_fire=False, facing="east", waterlogged=False))
    bewuchs(w, moos=0.1, ranken=0.1)
    return w


def verlassene_mine(seed, g=2):
    """Verlassene Mine: ein eingestürzter Stolleneingang mit morschem Holzverbau, verrostete Schienen und eine
    umgekippte Lore, Abraumhalde und eine verfallene Hütte."""
    from drachen import felsen
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.3)
    felsen(w, R * 0.6, 10 * u + 4, cz=-round(R * 0.4), spitz=1.0, rauh=0.25)
    for y in range(1, 5):
        for x in range(-2, 3):
            for z in range(-round(R * 0.4), round(R * 0.3)):
                w.bloecke.pop((x, y, z), None)
    for z in range(-round(R * 0.4), round(R * 0.3), 3):
        for x in (-2, 2):
            for y in range(1, 4):
                w.setze(x, y, z, w.b("dark_oak_log", axis="y"))
        for x in range(-2, 3):
            if w.rng.random() < 0.7:
                w.setze(x, 4, z, w.b("dark_oak_log", axis="x"))
    for x in range(-2, 3):
        for y in range(1, 3):
            w.setze(x, y, -round(R * 0.4) + 2, w.b("gravel"))
    for y in range(1, 6):
        for x in (-3, 3):
            w.setze(x, y, round(R * 0.3), w.b("dark_oak_log", axis="y"))
    for x in range(-3, 4):
        w.setze(x, 5, round(R * 0.3), w.b("dark_oak_log", axis="x"))
    w.setze(1, 4, round(R * 0.3) + 1, w.b("lantern", hanging=True, waterlogged=False))
    for z in range(-round(R * 0.35), R // 2):
        if w.rng.random() < 0.8:
            w.setze(0, 1, z, w.b("rail", shape="north_south", waterlogged=False))
    w.setze(2, 1, R // 4, w.b("iron_trapdoor", facing="north", half="bottom", open=True, powered=False,
                              waterlogged=False))
    for k in range(int(8 * u)):
        x, z = R // 2 + int(w.rng.integers(-3, 4)), int(w.rng.integers(-3, 4))
        w.setze(x, 1, z, w.b("gravel"))
    st = stil_haus(w, "holz_dunkel")
    P.gebaeude(w, st, -R + 2, R // 4, -R + 6, R // 4 + 4, y0=1, etagen=1, eh=3, dach="sattel", tuer="east",
               gauben=False, kamine=0)
    verfallen(w, 0.3, ab_y=3, moos=0.05, ranken=0.05, schutt=False)
    return w


def schiff_im_wald(seed, g=2):
    """Schiff im Wald: ein uraltes Segelschiff liegt fernab jedes Meeres zwischen Bäumen, bemoost, mit
    eingewachsenen Ästen und einem Baum, der durch das Deck wächst."""
    from boote import kogge
    from piraten import einfuegen_gedreht
    from skulptur import dreh_x, dreh_y
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wald", dichte=0.5)
    s = kogge(seed, max(0, g - 1))
    for p, b in list(s.bloecke.items()):
        if s.P.name(b).endswith("_wool") and w.rng.random() < 0.85:
            del s.bloecke[p]
    einfuegen_gedreht(w, s, dreh_y(0.6) @ dreh_x(0.15), (0, 1.5, 0))
    verfallen(w, 0.3, ab_y=4, moos=0.15, ranken=0.2, schutt=False)
    einfuegen(w, wald2.laubbaum(seed, "oak", H=_r(10 * u + 4)), 1, 2, 0)
    baeume(w, 3 + g, R * 0.85)
    return w


def observatoriumsruine(seed, g=2):
    """Observatoriumsruine: ein runder Turm, dessen Kuppel zur Hälfte eingestürzt ist, das verrostete Fernrohr zeigt
    noch immer in den Himmel."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.4)
    M = stein(w, seed)
    r = _r(4 * u + 2)
    H = _r(8 * u + 4)
    for y in range(1, H + 1):
        for k in range(int(r * 8)):
            a = k / (r * 8) * 6.28
            w.setze(round(math.cos(a) * r), y, round(math.sin(a) * r), M(0, y, 0, y / H))
    for x in range(-r, r + 1):
        for z in range(-r, r + 1):
            for y in range(0, r + 1):
                d = math.sqrt(x * x + y * y + z * z)
                if r - 1 < d <= r and x < 1:
                    w.setze(x, H + y, z, w.b("weathered_copper" if (x + y) % 3 else "oxidized_copper"))
    linie(w, (0, H + 1, 0), (r * 1.4, H + r * 1.5, 0), w.b("oxidized_cut_copper"), 0.6)
    verfallen(w, 0.3, ab_y=H)
    return w


def steinkreis_verfallen(seed, g=1):
    """Verfallener Steinkreis: mächtige, schiefe und umgestürzte Menhire im Kreis, zwei Trilithen mit
    Decksteinen, ein flechtenbewachsener Altarstein in der Mitte und ein Ring aus Heide und Farn."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R + 4, art="wiese", dichte=0.45)
    M = Mat(w, ["stone", "andesite", "tuff", "mossy_cobblestone", "cobblestone", "stone"])
    rng = w.rng
    n = 12

    def menhir(x, z, H, neig, dicke):
        for y in range(1, H + 1):
            ox = round(neig[0] * y)
            oz = round(neig[1] * y)
            for dx in range(dicke):
                for dz in range(dicke if y < H * 0.8 else max(1, dicke - 1)):
                    w.setze(x + ox + dx, y, z + oz + dz, M(x + dx, y, z + dz, y / H))

    for k in range(n):
        a = k / n * 6.28
        x, z = round(math.cos(a) * R * 0.7), round(math.sin(a) * R * 0.7)
        H = _r((4 + rng.random() * 3) * u + 2)
        d = 2 if u > 0.9 else 1
        r = rng.random()
        if k in (0, n // 2):
            tx, tz = round(-math.sin(a) * 2.5), round(math.cos(a) * 2.5)
            menhir(x - tx, z - tz, H, (0, 0), d)
            menhir(x + tx, z + tz, H, (0, 0), d)
            from flora import linie as _lin
            _lin(w, (x - tx, H + 1, z - tz), (x + tx + d - 1, H + 1, z + tz + d - 1), M(x, H, z, 0.8), 0.9)
        elif r < 0.3:
            for j in range(H):
                for dd in range(d):
                    w.setze(x + round(math.cos(a + 1.57) * j), 1, z + round(math.sin(a + 1.57) * j) + dd,
                            M(x, 1, z, 0.4))
        else:
            menhir(x, z, H, ((rng.random() - 0.5) * 0.35, (rng.random() - 0.5) * 0.35), d)
    for x in range(-2, 3):
        for z in range(-1, 2):
            w.setze(x, 1, z, M(x, 1, z, 0.5))
    w.setze(0, 2, 0, w.b("lichen" if False else "moss_carpet"))
    for k in range(int(R * 7)):
        a = k / (R * 7) * 6.28
        x, z = round(math.cos(a) * R * 0.95), round(math.sin(a) * R * 0.95)
        if (x, 1, z) not in w.bloecke:
            w.setze(x, 1, z, w.b("fern" if rng.random() < 0.6 else "sweet_berry_bush", **(
                {} if rng.random() < 0.6 else {"age": 2})), False)
    schwebend_entfernen(w)
    bewuchs(w, moos=0.2)
    return w

def amphitheaterruine(seed, g=2):
    """Amphitheater-Ruine: halbrunde Sitzreihen aus Stein in einen Hang gebaut, zum Teil abgesackt, die Bühnenwand
    nur noch als Säulenstümpfe, Gras zwischen den Stufen."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 5)
    gelaende(w, R + 3, art="wiese", dichte=0.4)
    M = stein(w, seed)
    for k in range(_r(6 * u + 3)):
        r = R * 0.4 + k * 1.2
        for j in range(int(r * 5)):
            a = math.pi + j / (r * 5) * math.pi
            x, z = round(math.cos(a) * r), round(math.sin(a) * r)
            for y in range(1, k + 2):
                w.setze(x, y, z, M(x, y, z, y / 8))
    for x in range(-round(R * 0.5), round(R * 0.5) + 1, 3):
        for y in range(1, 1 + int(w.rng.integers(1, 6))):
            w.setze(x, y, 3, w.b("quartz_pillar", axis="y") if _stil(seed) else M(x, y, 3, 0.5))
    verfallen(w, 0.35, ab_y=2, schutt=True)
    return w


def bibliotheksruine(seed, g=2):
    """Bibliotheksruine: ein Saal ohne Dach, an dessen Wänden noch Bücherregale stehen, umgestürzte Lesepulte,
    Bücherhaufen im Gras und ein Baum mitten im Raum."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.3)
    M = stein(w, seed)
    a, b = _r(7 * u + 3), _r(5 * u + 2)
    H = _r(6 * u + 3)
    for x in range(-a, a + 1):
        for z in range(-b, b + 1):
            w.setze(x, 0, z, w.b("dark_oak_planks" if (x + z) % 2 else "spruce_planks"))
            if abs(x) == a or abs(z) == b:
                for y in range(1, H + 1):
                    w.setze(x, y, z, M(x, y, z, y / H))
            elif abs(x) == a - 1 or abs(z) == b - 1:
                for y in range(1, H - 1):
                    w.setze(x, y, z, w.b("bookshelf"))
    for k in range(3):
        w.setze(-2 + k * 2, 1, 0, w.b("lectern", facing="north", has_book=k == 1, powered=False))
    verfallen(w, 0.55, ab_y=2, ranken=0.15)
    einfuegen(w, wald2.laubbaum(seed, "oak", H=_r(8 * u + 4)), 2, 0, 1)
    return w


def pyramidenstumpf(seed, g=2):
    """Überwucherter Pyramidenstumpf: eine gestufte Pyramide ohne Spitze, vom Dschungel zurückerobert – Moos auf
    den Stufen, Lianen an den Kanten, eine Freitreppe hinauf zu einem einsamen Altar, Bäume auf den Absätzen."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 5)
    gelaende(w, R + 5, art="wald", dichte=0.45)
    M = Mat(w, ["mossy_stone_bricks", "mossy_cobblestone", "cracked_stone_bricks", "stone_bricks", "moss_block",
                "mossy_stone_bricks"])
    stufen = _r(4.5 * u + 3)
    rr = []
    for k in range(stufen):
        r = int(R - k * R / (stufen + 2))
        rr.append(r)
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                for y in (2 * k + 1, 2 * k + 2):
                    w.setze(x, y, z, M(x, y, z, k / stufen))
                if max(abs(x), abs(z)) == r and w.rng.random() < 0.3:
                    w.setze(x, 2 * k + 3, z, w.b("moss_carpet"), False)
    for k in range(2 * stufen):
        for x in range(-2, 3):
            zz = rr[0] + 1 - k
            if zz >= rr[min(stufen - 1, k // 2)] - 1 or True:
                w.setze(x, k + 1, rr[0] - k + 1 if k < 2 * stufen else 0,
                        w.b("mossy_stone_brick_stairs", facing="north", half="bottom", shape="straight",
                            waterlogged=False) if abs(x) < 2 else M(x, k, 0, 0.5))
    top = 2 * stufen + 1
    for x in range(-1, 2):
        for z in range(-1, 2):
            w.setze(x, top, z, w.b("chiseled_stone_bricks" if x == z == 0 else "mossy_stone_bricks"))
    w.setze(0, top + 1, 0, w.b("cracked_stone_bricks"))
    rng = w.rng
    for i in range(3 + g):
        k = int(rng.integers(0, stufen - 1))
        a = rng.random() * 6.28
        r = rr[k] - 1
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        x = max(-r, min(r, x))
        z = max(-r, min(r, z))
        if abs(x) <= 2 and z > 0:
            continue
        einfuegen(w, wald2.laubbaum(int(rng.integers(1, 10 ** 6)), "jungle" if i % 2 else "oak",
                                    H=_r(5 * u + 3)), x, 2 * k + 3, z)
    verfallen(w, 0.12, ab_y=4, moos=0.2, ranken=0.35, schutt=False)
    baeume(w, 2 + g, R * 1.15, arten=("oak", "jungle"))
    return w

def verlassenes_dorf(seed, g=2):
    """Verlassenes Dorf: eine Handvoll Fachwerkhäuser mit eingesunkenen Dächern, leere Fensterhöhlen, ein umgekippter
    Karren, ein vertrockneter Brunnen und wucherndes Gestrüpp."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.6)
    pools = ["fachwerk_rot", "fachwerk_ocker", "holz_dunkel", "stein_schiefer"]
    for i in range(4 + g):
        a = i / (4 + g) * 6.28
        cx, cz = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55)
        st = stil_haus(w, pools[i % 4])
        P.gebaeude(w, st, cx - 3, cz - 2, cx + 3, cz + 2, y0=1, etagen=1, eh=4, dach="sattel", tuer="south",
                   gauben=False, kamine=1)
    from haeuser2 import karren, ziehbrunnen
    ziehbrunnen(w, 0, 0)
    w.setze(0, 1, 0, w.b("dirt"))
    karren(w, 3, 4)
    verfallen(w, 0.6, ab_y=3, moos=0.05, ranken=0.15)
    return w


def thronsaalruine(seed, g=2):
    """Thronsaal-Ruine: ein Saal ohne Dach mit zwei Reihen gebrochener Bündelpfeiler, geborstenem Schachbrettboden,
    einem Podest mit dem steinernen Thron und einer Rückwand mit leerem Rosettenfenster und zerrissenem Banner."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.35)
    M = stein(w, seed)
    rng = w.rng
    L = _r(10 * u + 4)
    B = _r(4 * u + 3)
    H = _r(9 * u + 4)
    for z in range(-L, L + 1):
        for x in range(-B, B + 1):
            w.setze(x, 0, z, w.b("polished_andesite" if (x + z) % 2 else "polished_deepslate"))
            if rng.random() < 0.06:
                w.setze(x, 0, z, w.b("grass_block"))
        for sx in (-B, B):
            w.setze(sx, 1, z, M(sx, 1, z, 0.2))
            w.setze(sx, 2, z, M(sx, 2, z, 0.2)) if rng.random() < 0.6 else None
        if z % 4 == 0 and z > -L + 3:
            for sx in (-B + 2, B - 3):
                h = H if rng.random() < 0.35 else int(H * (0.3 + 0.5 * rng.random()))
                for y in range(1, h + 1):
                    for dx in (0, 1):
                        for dz in (0, 1):
                            w.setze(sx + dx, y, z + dz, M(sx, y, z, y / H))
    for k in range(3):
        for x in range(-3 + k, 4 - k):
            for z in range(-L + 1, -L + 5 - k):
                w.setze(x, 1 + k, z, w.b("smooth_stone"))
    for x in (-1, 0, 1):
        w.setze(x, 4, -L + 2, w.b("stone_brick_stairs", facing="south", half="bottom", shape="straight",
                                  waterlogged=False) if x == 0 else w.b("stone_brick_wall", up=True, north="none",
                                                                        south="none", east="none", west="none",
                                                                        waterlogged=False))
    for y in range(4, 8):
        w.setze(0, y, -L + 1, w.b("chiseled_stone_bricks" if y < 7 else "gold_block"))
    for x in range(-B, B + 1):
        for y in range(1, H + 4):
            d = math.hypot(x, y - H * 0.65)
            if 1.2 < d < H * 0.25 and not (abs(x) < 1 or abs(y - H * 0.65) < 1):
                continue
            if d <= 1.2:
                w.setze(x, y, -L - 1, w.b("red_stained_glass"))
                continue
            w.setze(x, y, -L - 1, M(x, y, -L, y / H))
    for y in range(2, 6):
        for x in (B - 2,):
            w.setze(x, y, -L, w.b("red_wool") if y != 3 else w.b("yellow_wool"))
    verfallen(w, 0.35, ab_y=4)
    return w

def ruinenbrunnen(seed, g=0):
    """Ruinenbrunnen: ein achteckiges Brunnenbecken mit gebrochener Figurensäule, das Wasser ist zu einem
    Seerosentümpel geworden, Moos und Blumen in den Fugen."""
    w = _neu(seed)
    u = U[g]
    R = _r(6 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.5)
    M = stein(w, seed)
    r = 3 * u + 1.5
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            d = math.hypot(x, z)
            if d <= r:
                w.setze(x, 1, z, w.b("water", level=0) if d < r - 1 else M(x, 1, z, 0.5))
                w.setze(x, 0, z, M(x, 0, z, 0.2))
                if d < r - 1 and w.rng.random() < 0.15:
                    w.setze(x, 2, z, w.b("lily_pad"))
    for y in range(1, _r(3 * u + 2)):
        w.setze(0, y, 0, M(0, y, 0, 0.6))
    bewuchs(w, moos=0.2, ranken=0.0)
    return w


def wachturmruine(seed, g=1):
    """Wachturm-Ruine am Weg: ein viereckiger Turm mit eingestürztem Obergeschoss, die Treppe führt ins Leere, am Fuß
    ein verwitterter Wegstein."""
    w = _neu(seed)
    u = U[g]
    R = _r(8 * u + 4)
    gelaende(w, R, art="wiese", dichte=0.4)
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="schiefer", holz="spruce")
    P.turm(w, st, 0, 0, 1, _r(12 * u + 5), _r(2.5 * u + 1.5), form="eckig", dach="platt", krone=True)
    verfallen(w, 0.6, ab_y=_r(5 * u + 2))
    for z in range(-R, R + 1):
        w.setze(R // 2 + 2, 0, z, w.b("dirt_path"))
    w.setze(R // 2, 1, 2, w.b("mossy_cobblestone"))
    return w


def gefallener_riese(seed, g=3):
    """Gefallener Riese: das gewaltige Skelett eines Riesen liegt ausgestreckt in einer Wiese, Rippen wie Torbögen,
    der Schädel halb im Boden, Blumen wachsen zwischen den Knochen."""
    from skulptur import Skulptur, ell, kap
    from weltwunder import bl
    w = _neu(seed)
    u = U[g]
    R = _r(22 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.6)
    S = Skulptur(w, u)
    S.mat("k", lambda *a: w.b("bone_block", axis="y"))
    S.mat("d", bl(w, "black_concrete"))
    S.plus(kap((-12, 1, 0), (6, 1, 0), 0.9), "k")
    for k in range(7):
        x = -8 + k * 2.2
        for sz in (-1, 1):
            S.plus(kap((x, 1, 0), (x + 0.5, 4.5, sz * 3.5), 0.45, 0.35), "k")
            S.plus(kap((x + 0.5, 4.5, sz * 3.5), (x + 1, 1, sz * 5.5), 0.35, 0.3), "k")
    S.plus(ell(10, 2.5, 0, 3.5, 3.0, 3.0), "k")
    S.plus(ell(11, 3, 1.6, 0.8, 0.8, 0.5), "d")
    S.plus(ell(11, 3, -1.6, 0.8, 0.8, 0.5), "d")
    for sz in (-1, 1):
        S.plus(kap((-12, 1, sz * 1.5), (-20, 1, sz * 3), 0.7), "k")
        S.plus(kap((4, 1.5, sz * 3), (8, 1, sz * 9), 0.6), "k")
    S.rendern((-22, -1, -11), (15, 8, 11), versatz=(0.5, 0, 0.5))
    bewuchs(w, moos=0.05)
    return w


def vergessener_garten(seed, g=2):
    """Vergessener Garten: ein verwilderter Schlossgarten mit zugewachsenen Heckenrändern, umgestürzten Statuen,
    leerem Wasserbecken, Rosenbögen voller Ranken und alten Bänken."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    gelaende(w, R, art="wiese", dichte=0.6)
    M = stein(w, seed)
    rng = w.rng
    for k in range(int(R * 6)):
        a = k / (R * 6) * 6.28
        for r in (R * 0.4, R * 0.75):
            x, z = round(math.cos(a) * r), round(math.sin(a) * r)
            if rng.random() < 0.75:
                for y in (1, 2, 3) if r > R * 0.5 else (1, 2):
                    if y == 3 and rng.random() < 0.4:
                        continue
                    w.setze(x, y, z, _lv(w, "oak" if rng.random() < 0.7 else "azalea"), False)
                if rng.random() < 0.05:
                    w.setze(x, 3, z, w.b("rose_bush", half="lower"), False)
                    w.setze(x, 4, z, w.b("rose_bush", half="upper"), False)
    for x in range(-3, 4):
        for z in range(-3, 4):
            if x * x + z * z <= 9:
                w.setze(x, 0, z, M(x, 0, z, 0.3))
                if x * x + z * z > 6:
                    w.setze(x, 1, z, M(x, 1, z, 0.5))
    for k in range(4):
        a = k * 1.57 + 0.78
        x, z = round(math.cos(a) * R * 0.58), round(math.sin(a) * R * 0.58)
        w.setze(x, 1, z, M(x, 1, z, 0.5))
        w.setze(x + 1, 1, z, w.b("quartz_pillar", axis="x"))
        w.setze(x + 2, 1, z, w.b("chiseled_quartz_block"))
    for k in range(2):
        a = k * 3.14 + 1.2
        x, z = round(math.cos(a) * R * 0.88), round(math.sin(a) * R * 0.88)
        einfuegen(w, wald2.laubbaum(seed + k, "oak", H=_r(6 * u + 4)), x, 0, z)
    for k in range(4):
        a = k * 1.57
        x, z = round(math.cos(a) * R * 0.25), round(math.sin(a) * R * 0.25)
        for y in range(1, 5):
            w.setze(x, y, z, w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                                 waterlogged=False) if y < 4 else M(x, y, z, 0.6))
            w.setze(x, y, z + (1 if z >= 0 else -1), w.b("vine", north=z >= 0, south=z < 0, east=False, west=False,
                                                          up=False), False) if y < 4 and rng.random() < 0.6 else None
    bewuchs(w, moos=0.15, ranken=0.2)
    return w


def portalruine(seed, g=1):
    """Portalruine: ein schiefer, halb zerbrochener Rahmen aus Obsidian und weinendem Obsidian auf einem Fleck
    verbrannten Netherracks, Magmarisse, Goldblöcke, Ketten und eine umgestürzte Steinsäule – ein vergessenes Tor."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 5)
    gelaende(w, R, art="wiese", dichte=0.35)
    rng = w.rng
    rn = Rauschen(w, 3)
    rf = R * 0.6
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z * 1.3) + 3 * rn(x, 0, z)
            if d < rf:
                w.setze(x, 0, z, w.b(["netherrack", "netherrack", "blackstone", "magma_block", "soul_soil",
                                      "netherrack"][int(rng.integers(6))]))
                w.bloecke.pop((x, 1, z), None)
                if rng.random() < 0.06:
                    w.setze(x, 1, z, w.b("fire", age=0, north=False, south=False, east=False, west=False, up=False))
    bw, hh = _r(1.5 * u + 1.5), _r(2.5 * u + 3)
    rahmen = []
    for y in range(0, hh + 2):
        rahmen += [(-bw - 1, y), (bw + 1, y)]
    for x in range(-bw - 1, bw + 2):
        rahmen += [(x, 0), (x, hh + 1)]
    for (x, y) in rahmen:
        if y > hh * 0.6 and x > bw * 0.3 and rn(x, y, 0) < 0.45:
            continue
        for z in (0, 1):
            b = w.b("crying_obsidian" if rng.random() < 0.3 else "obsidian")
            w.setze(x + round(y * 0.12), y + 1, z, b)
    for k in range(int(6 * u)):
        x, z = int(rng.integers(-rf + 1, rf)), int(rng.integers(-3, 4))
        w.setze(x, 1, z, w.b("obsidian" if k % 3 else "gold_block"), False)
    for k in range(3):
        w.setze(-bw - 3, 1 + k, 2, w.b("stone_bricks" if k < 2 else "cracked_stone_bricks"))
        w.setze(-bw - 3, 1 + k, 3 + k, w.b("chain", axis="z", waterlogged=False)) if k == 2 else None
    for j in range(_r(4 * u + 2)):
        w.setze(bw + 3 + j, 1, -3, w.b("stone_bricks" if j % 3 else "mossy_stone_bricks"), False)
    schwebend_entfernen(w)
    bewuchs(w, moos=0.05, ranken=0.25)
    return w

RUINEN2 = {
    "burgruine": ("Burgruine", burgruine),
    "klosterruine": ("Klosterruine", klosterruine),
    "aquaedukt": ("Aquäduktruine", aquaedukt),
    "versunkene_stadt": ("Versunkene Stadt", versunkene_stadt),
    "ueberwucherte_stadt": ("Überwucherte Stadt", ueberwucherte_stadt),
    "turmstumpf": ("Turmstumpf", turmstumpf),
    "saeulenfeld": ("Säulenfeld", saeulenfeld),
    "gestuerzter_koloss": ("Gestürzter Koloss", gestuerzter_koloss),
    "ruinentor": ("Ruinentor", ruinentor),
    "luftschiffwrack": ("Luftschiffwrack", luftschiffwrack),
    "muehlenruine": ("Mühlenruine", muehlenruine),
    "kaminruine": ("Kaminruine", kaminruine),
    "verlassene_mine": ("Verlassene Mine", verlassene_mine),
    "schiff_im_wald": ("Schiff im Wald", schiff_im_wald),
    "observatoriumsruine": ("Observatoriumsruine", observatoriumsruine),
    "steinkreis_verfallen": ("Verfallener Steinkreis", steinkreis_verfallen),
    "amphitheaterruine": ("Amphitheater-Ruine", amphitheaterruine),
    "bibliotheksruine": ("Bibliotheksruine", bibliotheksruine),
    "pyramidenstumpf": ("Überwucherter Pyramidenstumpf", pyramidenstumpf),
    "verlassenes_dorf": ("Verlassenes Dorf", verlassenes_dorf),
    "thronsaalruine": ("Thronsaal-Ruine", thronsaalruine),
    "ruinenbrunnen": ("Ruinenbrunnen", ruinenbrunnen),
    "wachturmruine": ("Wachturm-Ruine", wachturmruine),
    "gefallener_riese": ("Gefallener Riese", gefallener_riese),
    "vergessener_garten": ("Vergessener Garten", vergessener_garten),
    "portalruine": ("Portalruine", portalruine),
}

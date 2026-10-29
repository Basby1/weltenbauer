"""Wald (neu) – elegante, einzeln erkennbare Bäume und Waldstücke mit Wegen.

Grundsätze:
- Jeder Baum hat eine eigene Silhouette: sichtbarer Stamm mit Wurzelanlauf, Äste, Krone aus mehreren
  lockeren Laubballen mit Lücken; Bäume stehen mit Abstand, so dass Kronen sich nur berühren.
- Darunter Unterholz in Gruppen (Sträucher, Farne, Jungbäume), Totholz, Findlinge.
- Wege aus Erde, Kies, Bruchstein, Moos, Schlamm mit Pfützen, Wurzeln, Trittsteinen und Bohlenstegen.
- Geländefolgend wie bisher: Stammfuß jedes Baumes als Anker, Boden und Pflanzen folgen ihrer Spalte.
"""

from __future__ import annotations

import math

import numpy as np

import modbloecke as MB
from lib import LUFT, Rauschen, Welt, laub
from wald import (Stueck, _fertig, _kum, _wahl, beeren, bluetenblaetter, hohes, leuchtflechte, schneeschicht,
                  zuckerrohr, bambus, findling)

GROESSEN_R = [11, 18, 29, 44]


def _neu(seed):
    w = Welt(int(seed))
    w.anker = (0, 0, 0)
    return w


def _s(st):
    return int(st.rng.integers(1, 10 ** 8))


def _achse(dx, dy, dz):
    a = (abs(dx), abs(dy), abs(dz))
    return "xyz"[a.index(max(a))]


# ============================================================================ Bausteine


def ast(w, p0, p1, holz, dicke=1, wood=False):
    """Ast von p0 nach p1 aus Stämmen in Richtung der Achse (dicke 1 oder 2)."""
    n = int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1]), abs(p1[2] - p0[2]))) + 1
    ax = _achse(p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    blk = w.b(f"{holz}_wood" if wood else f"{holz}_log", axis=ax) if not holz.endswith("_stem") else \
        w.b(holz, axis=ax)
    for i in range(n + 1):
        t = i / n
        x, y, z = (round(p0[k] + (p1[k] - p0[k]) * t) for k in range(3))
        w.setze(x, y, z, blk)
        if dicke >= 2 and t < 0.6:
            w.setze(x + 1, y, z, blk)
            w.setze(x, y, z + 1, blk)


def ballen(w, cx, cy, cz, rx, ry, blaetter, dichte=0.8, flach_unten=1.6, loecher=0.12):
    """Lockerer Laubballen mit ausgefranstem Rand und kleinen Löchern; blaetter: [(block_id, gewicht)]."""
    rng = w.rng
    k = _kum(blaetter)
    ri = int(math.ceil(max(rx, ry))) + 1
    for x in range(int(cx) - ri, int(cx) + ri + 1):
        for y in range(int(cy) - ri, int(cy) + ri + 1):
            for z in range(int(cz) - ri, int(cz) + ri + 1):
                dx, dy, dz = (x - cx) / rx, (y - cy) / ry, (z - cz) / rx
                if dy < 0:
                    dy *= flach_unten
                d = math.sqrt(dx * dx + dy * dy + dz * dz)
                if d > 1.0 + (rng.random() - 0.5) * 0.5:
                    continue
                if d > 0.65 and rng.random() > dichte:
                    continue
                if d < 0.8 and rng.random() < loecher:
                    continue
                w.setze(x, y, z, _wahl(k, rng.random()), ueberschreiben=False)


def wurzeln(w, x, z, holz, n=4, laenge=2, dick=False):
    rng = w.rng
    for i in range(n):
        a = i / n * 2 * math.pi + rng.random() * 0.6
        L = laenge + int(rng.integers(0, 2))
        for k in range(1, L + 1):
            px, pz = x + round(math.cos(a) * (k + (0.5 if dick else 0))), z + round(math.sin(a) * (k + (0.5 if dick else 0)))
            w.setze(px, 1 if k == 1 and rng.random() < 0.6 else 0, pz,
                    w.b(f"{holz}_log", axis="x" if abs(math.cos(a)) > 0.7 else "z") if not holz.endswith("_stem")
                    else w.b(holz, axis="y"))


def _laub(w, liste):
    """liste: [(art|'=block'|'mod:...', gewicht)] → [(id, gewicht)]"""
    erg = []
    for art, g in liste:
        if isinstance(art, int):
            erg.append((art, g))
        elif art.startswith("="):
            erg.append((w.b(art[1:]), g))
        elif art.startswith("herbst:"):
            erg.append((MB.herbstlaub(w, art[7:]), g))
        else:
            erg.append((laub(w, art), g))
    return erg


# ============================================================================ Bäume


def laubbaum(seed, holz="oak", H=None, blaetter=None, breit=1.0, aeste=None, dick=None):
    """Eleganter Laubbaum (Eiche/Buche/Ahorn): Wurzelanlauf, Stamm, 3–5 Hauptäste mit Zweigen, Krone aus
    mehreren getrennten Laubballen an den Astenden plus Kronenmitte."""
    w = _neu(seed)
    rng = w.rng
    H = H or int(9 + rng.integers(6))
    dick = (H >= 14) if dick is None else dick
    bl = _laub(w, blaetter or [(holz, 0.85), ("azalea", 0.08), ("dark_oak", 0.07)])
    ht = int(H * (0.42 + 0.1 * rng.random()))
    lean = (rng.random() - 0.5) * 0.6, (rng.random() - 0.5) * 0.6
    for y in range(0, ht + 1):
        x, z = round(lean[0] * y / ht), round(lean[1] * y / ht)
        w.setze(x, y, z, w.b(f"{holz}_log", axis="y"))
        if dick and y < ht * 0.7:
            for dx, dz in ((1, 0), (0, 1), (1, 1)):
                w.setze(x + dx, y, z + dz, w.b(f"{holz}_log", axis="y"))
    wurzeln(w, 0, 0, holz, n=4 + dick * 2, laenge=1 + dick + H // 12, dick=dick)
    tx, tz = round(lean[0]), round(lean[1])
    n = aeste or int(3 + rng.integers(3))
    enden = []
    for i in range(n):
        a = i / n * 2 * math.pi + rng.random() * 0.8
        y0 = ht - int(rng.integers(0, 3))
        L = (H * 0.2 + rng.random() * H * 0.1) * breit
        steig = 0.55 + rng.random() * 0.35
        p1 = (tx + math.cos(a) * L, y0 + L * steig, tz + math.sin(a) * L)
        ast(w, (tx, y0, tz), p1, holz, dicke=2 if dick and L > 5 else 1)
        enden.append(p1)
        if L > 3.5:
            a2 = a + (rng.random() - 0.5) * 1.6
            L2 = L * 0.4
            p2 = (p1[0] + math.cos(a2) * L2, p1[1] + L2 * 0.4, p1[2] + math.sin(a2) * L2)
            ast(w, p1, p2, holz)
            enden.append(p2)
    for (x, y, z) in enden:
        r = (1.6 + rng.random() * 0.9) * (0.7 + H / 30) * breit
        ballen(w, x, y + 0.6, z, r, r * 0.6, bl)
    ballen(w, tx, ht + H * 0.38, tz, (1.8 + H * 0.09) * breit, (1.5 + H * 0.05), bl)
    return w


def kronen_r(H, breit=1.0):
    return (H * 0.3 + 2.4) * breit


def birke(seed, H=None, blaetter=None):
    """Schlanke Birke: weißer, leicht geneigter Stamm, kleine Zweige, schmale lockere Krone in Etagen."""
    w = _neu(seed)
    rng = w.rng
    H = H or int(9 + rng.integers(6))
    bl = _laub(w, blaetter or [("birch", 0.9), ("oak", 0.1)])
    lx, lz = (rng.random() - 0.5) * 2.2, (rng.random() - 0.5) * 2.2
    for y in range(0, H):
        w.setze(round(lx * (y / H) ** 2), y, round(lz * (y / H) ** 2), w.b("birch_log", axis="y"))
    wurzeln(w, 0, 0, "birch", n=3, laenge=1)
    for k in range(4 + H // 4):
        t = 0.45 + 0.5 * k / (4 + H // 4)
        y = H * t
        cx, cz = lx * t * t, lz * t * t
        a = rng.random() * 2 * math.pi
        r = 1.4 + (1 - abs(t - 0.75) * 2) * 1.2
        ballen(w, cx + math.cos(a) * 0.8, y, cz + math.sin(a) * 0.8, r, 1.3, bl, dichte=0.75)
    return w


def fichte(seed, H=None, art="spruce", schnee=False, schmal=1.0):
    """Klassische Fichte/Tanne: gerader Stamm, nach unten weiter werdende, gezackte Nadelkränze in Etagen,
    lange Spitze; unten frei sichtbarer Stamm."""
    w = _neu(seed)
    rng = w.rng
    H = H or int(12 + rng.integers(10))
    nadel = laub(w, art)
    for y in range(0, H):
        w.setze(0, y, 0, w.b(f"{art}_log", axis="y"))
    wurzeln(w, 0, 0, art, n=4, laenge=1 + H // 16)
    y0 = int(H * (0.18 + 0.1 * rng.random()))
    Rm = (1.6 + H * 0.13) * schmal
    y = y0
    while y < H:
        t = (y - y0) / max(1, H - y0)
        r = Rm * (1 - t) ** 0.9 + 0.4
        for k, rr in enumerate((r, r * 0.65)):
            for x in range(-int(rr) - 1, int(rr) + 2):
                for z in range(-int(rr) - 1, int(rr) + 2):
                    d = math.hypot(x, z)
                    zack = 0.6 * math.cos(math.atan2(z, x) * (5 + k) + y)
                    if d <= rr + zack * 0.5 and (d < rr - 0.8 or rng.random() < 0.8):
                        w.setze(x, y + k, z, nadel, ueberschreiben=False)
        y += 2 if H < 18 else 3
    for k in range(3):
        w.setze(0, H + k, 0, nadel)
    if schnee:
        oben = {}
        for (x, yy, z), b in w.bloecke.items():
            if b == nadel and yy > oben.get((x, z), -1):
                oben[(x, z)] = yy
        for (x, z), yy in oben.items():
            if rng.random() < 0.7:
                w.setze(x, yy + 1, z, w.b("snow", layers=1))
    return w


def kiefer(seed, H=None):
    """Kiefer: hoher, leicht geschwungener rötlicher Stamm, oben ein paar ausladende Äste mit flachen,
    zerzausten Nadelpolstern."""
    w = _neu(seed)
    rng = w.rng
    H = H or int(14 + rng.integers(8))
    bl = _laub(w, [("spruce", 0.7), ("jungle", 0.0001), ("oak", 0.3)])
    phase = rng.random() * 6
    for y in range(0, H):
        x = round(math.sin(y * 0.25 + phase) * 0.8)
        w.setze(x, y, 0, w.b("spruce_log", axis="y") if y % 5 else w.b("stripped_spruce_log", axis="y"))
    top = (round(math.sin(H * 0.25 + phase) * 0.8), H, 0)
    wurzeln(w, 0, 0, "spruce", n=3, laenge=1)
    for i in range(3 + int(rng.integers(3))):
        a = rng.random() * 2 * math.pi
        y0 = int(H * (0.65 + 0.3 * rng.random()))
        L = 2 + rng.random() * 3
        p1 = (top[0] + math.cos(a) * L, y0 + L * 0.35, math.sin(a) * L)
        ast(w, (top[0], y0, 0), p1, "spruce")
        ballen(w, p1[0], p1[1] + 0.6, p1[2], 2.2 + rng.random(), 0.9, bl, dichte=0.7)
    ballen(w, top[0], H + 0.5, 0, 2.5, 1.1, bl, dichte=0.75)
    return w


def dunkeleiche(seed, H=None):
    """Dunkeleiche: 2×2-Stamm mit mächtigen Wurzeln, knorrige Äste, breite, tiefe Schirmkrone."""
    w = laubbaum(seed, "dark_oak", H=H or int(10 + _neu(seed).rng.integers(5)),
                 blaetter=[("dark_oak", 0.85), ("oak", 0.15)], breit=1.25, aeste=5, dick=True)
    return w


def kirschbaum(seed, H=None):
    """Kirschbaum: geschwungener dunkler Stamm, weit ausladende Äste, rosa Blütenwolken mit Lücken."""
    return laubbaum(seed, "cherry", H=H or int(7 + _neu(seed).rng.integers(5)),
                    blaetter=[("cherry", 0.9), ("flowering_azalea", 0.1)], breit=1.3, aeste=4)


def herbstbaum(seed, H=None, stil=0):
    """Ahorn im Herbst: Laub in Rot, Orange und Gold."""
    farben = [[("herbst:maple", 0.5), ("herbst:orange_autumn", 0.3), ("oak", 0.2)],
              [("herbst:yellow_autumn", 0.5), ("herbst:orange_autumn", 0.3), ("birch", 0.2)],
              [("herbst:orange_autumn", 0.6), ("herbst:maple", 0.2), ("herbst:yellow_autumn", 0.2)]]
    return laubbaum(seed, "oak", H=H, blaetter=farben[stil % 3], breit=1.0)


def weide(seed, H=None):
    """Trauerweide: kurzer dicker Stamm, ausladende Äste, von denen lange Laubvorhänge bis fast zum Boden
    hängen, durchsetzt mit Ranken."""
    w = _neu(seed)
    rng = w.rng
    H = H or int(9 + rng.integers(4))
    bl = _laub(w, [("oak", 0.4), ("jungle", 0.0001), ("mangrove", 0.6)])
    ht = int(H * 0.45)
    for y in range(0, ht + 1):
        for dx, dz in ((0, 0), (1, 0), (0, 1), (1, 1)) if H > 10 else ((0, 0),):
            w.setze(dx, y, dz, w.b("oak_log", axis="y"))
    wurzeln(w, 0, 0, "oak", n=5, laenge=2)
    for i in range(5):
        a = i / 5 * 2 * math.pi + rng.random() * 0.5
        L = H * 0.4
        p1 = (math.cos(a) * L, ht + L * 0.7, math.sin(a) * L)
        ast(w, (0, ht, 0), p1, "oak")
        ballen(w, p1[0], p1[1] + 0.5, p1[2], 2.6, 1.4, bl, dichte=0.8)
        for k in range(14):
            aa = a + (rng.random() - 0.5) * 1.6
            rr = L * (0.6 + 0.6 * rng.random())
            x, z = round(math.cos(aa) * rr), round(math.sin(aa) * rr)
            yt = int(p1[1])
            lang = int(H * (0.4 + 0.4 * rng.random()))
            for y in range(yt, max(2, yt - lang), -1):
                w.setze(x, y, z, _wahl(_kum(bl), rng.random()) if rng.random() < 0.75 else
                        w.b("vine", north=True, south=False, east=False, west=False, up=False),
                        ueberschreiben=False)
    return w


def mammutbaum(seed, H=None):
    """Mammutbaum: gewaltiger 3×3-Stamm mit Rindenrippen, breiter Wurzelfuß, hoch angesetzte, schmale
    kegelförmige Krone aus Nadelpolstern."""
    w = _neu(seed)
    rng = w.rng
    H = H or int(26 + rng.integers(12))
    nadel = _laub(w, [("spruce", 0.8), ("jungle", 0.0001), ("dark_oak", 0.2)])
    for y in range(0, H):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) + abs(dz) == 2 and y > H * 0.3:
                    continue
                w.setze(dx, y, dz, w.b("spruce_wood", axis="y") if (dx + dz + y) % 4 else w.b("spruce_log", axis="y"))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        for k in range(1, 4):
            for y in range(0, 4 - k):
                w.setze(round(math.cos(a) * (1 + k)), y, round(math.sin(a) * (1 + k)), w.b("spruce_wood", axis="y"))
    y0 = int(H * 0.5)
    y = y0
    while y < H + 3:
        t = (y - y0) / (H + 3 - y0)
        r = 4.5 * (1 - t) + 1
        for i in range(5):
            a = i / 5 * 2 * math.pi + y
            px, pz = math.cos(a) * r * 0.7, math.sin(a) * r * 0.7
            ast(w, (0, y, 0), (px, y + 1, pz), "spruce")
            ballen(w, px, y + 1, pz, 1.8 + (1 - t) * 1.2, 1.0, nadel, dichte=0.75)
        y += 3
    return w


def akazie(seed, H=None):
    """Schirmakazie: schräger, gegabelter Stamm, flache, weit gespannte Laubschirme auf zwei Ebenen."""
    w = _neu(seed)
    rng = w.rng
    H = H or int(7 + rng.integers(4))
    bl = _laub(w, [("acacia", 1.0)])
    a = rng.random() * 2 * math.pi
    p1 = (math.cos(a) * 2, H * 0.55, math.sin(a) * 2)
    ast(w, (0, 0, 0), p1, "acacia")
    for k in (-1, 1):
        a2 = a + k * 1.0
        p2 = (p1[0] + math.cos(a2) * 3, H, p1[2] + math.sin(a2) * 3)
        ast(w, p1, p2, "acacia")
        ballen(w, p2[0], p2[1] + 0.5, p2[2], 3.5, 0.7, bl, dichte=0.85, loecher=0.05)
    return w


def dschungelriese(seed, H=None):
    """Urwaldriese: 2×2-Stamm mit Brettwurzeln, hoch oben eine breite Krone, Lianen, Kakaofrüchte."""
    w = laubbaum(seed, "jungle", H=H or int(18 + _neu(seed).rng.integers(8)),
                 blaetter=[("jungle", 0.85), ("oak", 0.15)], breit=1.1, aeste=4, dick=True)
    rng = w.rng
    for i in range(4):
        a = i / 4 * 2 * math.pi + 0.4
        for k in range(1, 4):
            for y in range(0, 5 - k):
                w.setze(round(0.5 + math.cos(a) * (0.5 + k)), y, round(0.5 + math.sin(a) * (0.5 + k)),
                        w.b("jungle_wood", axis="y"))
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) == "minecraft:jungle_leaves" and rng.random() < 0.05:
            for k in range(1, 3 + int(rng.integers(0, 6))):
                if w.frei(x, y - k, z):
                    w.setze(x, y - k, z, w.b("vine", north=True, south=False, east=False, west=False, up=False))
    return w


def palme(seed, H=None):
    """Palme: geschwungener Stamm, Kokosnüsse (Kakao-Optik), sternförmige, herabhängende Wedel."""
    w = _neu(seed)
    rng = w.rng
    H = H or int(8 + rng.integers(5))
    a = rng.random() * 2 * math.pi
    pts = []
    for y in range(0, H):
        t = y / H
        x, z = round(math.cos(a) * 3 * t * t), round(math.sin(a) * 3 * t * t)
        w.setze(x, y, z, w.b("jungle_log", axis="y") if y % 3 else w.b("stripped_jungle_log", axis="y"))
        pts.append((x, y, z))
    tx, ty, tz = pts[-1]
    bl = laub(w, "jungle")
    for i in range(7):
        b = i / 7 * 2 * math.pi + rng.random() * 0.3
        for k in range(1, 6):
            y = ty + 1 - (k * k) // 8
            w.setze(tx + round(math.cos(b) * k), y, tz + round(math.sin(b) * k), bl)
    w.setze(tx, ty + 1, tz, bl)
    return w


def jungbaum(seed, art="oak", H=None):
    w = _neu(seed)
    rng = w.rng
    H = H or int(3 + rng.integers(3))
    for y in range(0, H):
        w.setze(0, y, 0, w.b(f"{art}_log", axis="y"))
    ballen(w, 0, H, 0, 1.6, 1.4, [(laub(w, art), 1)], dichte=0.8)
    return w


def busch(seed, art="oak", r=None, blueten=False):
    w = _neu(seed)
    rng = w.rng
    r = r or 1.2 + rng.random() * 1.0
    bl = [(laub(w, art), 0.8), (laub(w, "flowering_azalea" if blueten else art), 0.2)]
    w.setze(0, 0, 0, w.b(f"{art}_log" if art not in ("azalea", "flowering_azalea") else "oak_log", axis="y"))
    ballen(w, 0, 1, 0, r, r * 0.75, bl, dichte=0.85, flach_unten=3.0, loecher=0.05)
    return w


def totholz(seed, art="oak"):
    """Umgestürzter Stamm mit Moos, Pilzen und Wurzelteller."""
    w = _neu(seed)
    rng = w.rng
    L = 4 + int(rng.integers(5))
    ax = "x" if rng.random() < 0.5 else "z"
    for k in range(L):
        p = (k, 1, 0) if ax == "x" else (0, 1, k)
        w.setze(*p, w.b(f"{art}_log", axis=ax))
        if rng.random() < 0.35:
            w.setze(p[0], 2, p[2], w.b("moss_carpet") if rng.random() < 0.6 else
                    w.b(["brown_mushroom", "red_mushroom"][int(rng.integers(2))]))
    for d in (-1, 0, 1):
        for y in (1, 2, 3):
            if rng.random() < 0.6:
                p = (-1, y, d) if ax == "x" else (d, y, -1)
                w.setze(*p, w.b("rooted_dirt") if y < 3 else w.b("dirt"))
    return w


def baumstumpf(seed, art="oak"):
    w = _neu(seed)
    rng = w.rng
    for y in range(0, 2 + int(rng.integers(0, 2))):
        w.setze(0, y, 0, w.b(f"{art}_log", axis="y"))
    w.setze(0, 2 if rng.random() < 0.5 else 3, 0, w.b("moss_carpet") if rng.random() < 0.5 else w.b("brown_mushroom"))
    wurzeln(w, 0, 0, art, n=3, laenge=1)
    return w


# ============================================================================ Wege


def wegpunkte(st, art="kurve", breite=2.0):
    """Liefert eine Liste (x, z) entlang eines geschwungenen Weges quer durch das Waldstück."""
    R = st.R
    rng = st.rng
    pts = []
    a = rng.random() * math.pi
    amp = R * (0.15 + 0.15 * rng.random())
    ph = rng.random() * 6
    n = int(R * 4)
    for i in range(n + 1):
        t = i / n * 2 - 1
        s = t * R * 1.3
        q = math.sin(t * 2.2 + ph) * amp
        x = math.cos(a) * s - math.sin(a) * q
        z = math.sin(a) * s + math.cos(a) * q
        pts.append((x, z))
    if art == "kreuz":
        b = a + math.pi / 2 + (rng.random() - 0.5) * 0.4
        for i in range(n + 1):
            t = i / n * 2 - 1
            s = t * R * 1.3
            q = math.sin(t * 1.7 + ph * 2) * amp * 0.6
            pts.append((math.cos(b) * s - math.sin(b) * q, math.sin(b) * s + math.cos(b) * q))
    return pts


WEGBELAG = {
    "erde": [("dirt_path", 5), ("coarse_dirt", 2), ("rooted_dirt", 1), ("podzol", 1)],
    "kies": [("gravel", 5), ("coarse_dirt", 1.5), ("dirt_path", 1.5), ("andesite", 0.6), ("cobblestone", 0.4)],
    "stein": [("cobblestone", 3), ("mossy_cobblestone", 2.5), ("stone", 1), ("andesite", 1), ("gravel", 1),
              ("dirt_path", 1)],
    "matsch": [("mud", 3), ("packed_mud", 2), ("coarse_dirt", 2), ("dirt_path", 1.5), ("rooted_dirt", 1)],
    "moos": [("moss_block", 3), ("dirt_path", 2), ("mossy_cobblestone", 1.5), ("coarse_dirt", 1)],
    "sand": [("sand", 4), ("dirt_path", 1), ("gravel", 1), ("coarse_dirt", 0.5)],
}


def weg(st, pts, breite=2.0, belag="erde", pfuetzen=0.0, trittsteine=False, wurzelquer=0.0, rand_steine=0.06,
        bohlen_bei=None):
    """Weg entlang pts: gemischter Belag, ausgefranster Rand, Pfützen, Trittsteine, querliegende Wurzeln,
    Kiesel am Rand; räumt Bäume/Pflanzen auf dem Weg weg. bohlen_bei(x, z) -> True: Bohlensteg statt Belag."""
    w = st.w
    rng = st.rng
    bk = _kum([(w.b(n, snowy=False) if n in ("podzol", "grass_block") else w.b(n), g) for n, g in WEGBELAG[belag]])
    r_n = Rauschen(w, 2.5)
    feld = {}
    for (px, pz) in pts:
        b = breite * (0.8 + 0.5 * r_n(px, 7, pz))
        for x in range(int(px - b) - 1, int(px + b) + 2):
            for z in range(int(pz - b) - 1, int(pz + b) + 2):
                d = math.hypot(x - px, z - pz)
                if d <= b:
                    feld[(x, z)] = min(feld.get((x, z), 9), d / b)
    for (x, z), d in feld.items():
        if st.rand(x, z) > 1.1:
            continue
        for y in range(1, 4):
            p = (x, y, z)
            if p in w.bloecke:
                n = w.P.name(w.bloecke[p])
                if not n.endswith(("_log", "_wood")) or y == 1:
                    w.bloecke.pop(p, None)
                    w.folgen.pop(p, None)
        if bohlen_bei and bohlen_bei(x, z):
            continue
        if d > 0.85 and rng.random() < 0.5:
            continue
        v = r_n(x, 0, z) * 0.6 + rng.random() * 0.4
        blk = _wahl(bk, v)
        if pfuetzen and d < 0.6 and r_n(x + 50, 3, z) > 1 - pfuetzen:
            blk = w.b("water", level=0) if r_n(x + 50, 3, z) > 1 - pfuetzen * 0.6 else w.b("mud")
        w.setze(x, 0, z, blk)
        w.folgen[(x, 0, z)] = -1
        if trittsteine and d < 0.5 and (x * 7 + z * 13) % 5 == 0:
            w.setze(x, 0, z, w.b("polished_andesite") if rng.random() < 0.5 else w.b("stone"))
        if 0.75 < d <= 1.0 and rng.random() < rand_steine:
            w.setze(x, 1, z, MB.kiesel(w) if rng.random() < 0.6 else w.b("fern"))
            w.folgen[(x, 1, z)] = -1
    if wurzelquer:
        for i, (px, pz) in enumerate(pts[::6]):
            if rng.random() < wurzelquer:
                a = rng.random() * math.pi
                for k in range(-int(breite) - 1, int(breite) + 2):
                    x, z = round(px + math.cos(a) * k), round(pz + math.sin(a) * k)
                    w.setze(x, 0, z, w.b("rooted_dirt"))
                    w.folgen[(x, 0, z)] = -1
                    if abs(k) <= breite:
                        w.setze(x, 1, z, w.b("mangrove_roots", waterlogged=False)) if rng.random() < 0.25 else None
                        w.folgen[(x, 1, z)] = -1
    return feld


def bohlensteg(st, feld, holz="spruce"):
    """Bohlensteg auf Pfosten über Feld-Zellen (x, z): Dielen, gelegentlich Pfosten mit Laterne."""
    w = st.w
    for (x, z), d in feld.items():
        if d <= 0.7:
            w.setze(x, 1, z, w.b(f"{holz}_slab", type="bottom", waterlogged=False))
            w.folgen[(x, 1, z)] = -1
            if (x + z) % 4 == 0:
                w.setze(x, 0, z, w.b(f"{holz}_log", axis="y"))
                w.folgen[(x, 0, z)] = -1


def wegdeko(st, pts, art="wald"):
    """Wegweiser, Bänke, Laternenpfähle, Holzstapel am Wegrand."""
    w = st.w
    rng = st.rng
    for i in range(0, len(pts), max(12, len(pts) // 4)):
        px, pz = pts[i]
        if i + 1 >= len(pts):
            continue
        qx, qz = pts[i + 1]
        nx, nz = -(qz - pz), (qx - px)
        ln = math.hypot(nx, nz) or 1
        sx, sz = round(px + nx / ln * 3), round(pz + nz / ln * 3)
        if st.rand(sx, sz) > 0.9:
            continue
        for y in range(1, 4):
            w.bloecke.pop((sx, y, sz), None)
        r = rng.random()
        if r < 0.35:
            for y in (1, 2):
                w.setze(sx, y, sz, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                       waterlogged=False))
            w.setze(sx, 3, sz, w.b("lantern", hanging=False, waterlogged=False))
        elif r < 0.6:
            w.setze(sx, 1, sz, w.b("spruce_stairs", facing="north", half="bottom", shape="straight",
                                   waterlogged=False))
            w.setze(sx + 1, 1, sz, w.b("spruce_stairs", facing="north", half="bottom", shape="straight",
                                       waterlogged=False))
        elif r < 0.8:
            for k in range(3):
                w.setze(sx + k, 1, sz, w.b("spruce_log", axis="x"))
                if k < 2:
                    w.setze(sx + k, 2, sz, w.b("spruce_log", axis="x"))
        else:
            w.setze(sx, 1, sz, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                   waterlogged=False))
            w.setze(sx, 2, sz, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                   waterlogged=False))
            w.setze(sx, 3, sz, w.b("spruce_wall_sign" if False else "spruce_trapdoor", facing="north", half="top",
                                   open=True, powered=False, waterlogged=False))
        for y in range(1, 4):
            if (sx, y, sz) in w.bloecke:
                w.folgen[(sx, y, sz)] = -1
            if (sx + 1, y, sz) in w.bloecke:
                w.folgen[(sx + 1, y, sz)] = -1
            if (sx + 2, y, sz) in w.bloecke:
                w.folgen[(sx + 2, y, sz)] = -1


def bach(st, pts, breite=1.6):
    """Bachlauf: Wasser auf Kies, Uferkiesel, Schilf und Farne am Rand."""
    w = st.w
    rng = st.rng
    feld = {}
    for (px, pz) in pts:
        for x in range(int(px - breite) - 2, int(px + breite) + 3):
            for z in range(int(pz - breite) - 2, int(pz + breite) + 3):
                d = math.hypot(x - px, z - pz) / breite
                feld[(x, z)] = min(feld.get((x, z), 9), d)
    for (x, z), d in feld.items():
        if st.rand(x, z) > 1.1:
            continue
        for y in range(1, 4):
            p = (x, y, z)
            if p in w.bloecke and (d < 1.0 or not w.P.name(w.bloecke[p]).endswith(("_log", "_wood"))):
                if d < 1.0:
                    w.bloecke.pop(p, None)
                    w.folgen.pop(p, None)
        if d < 1.0:
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("gravel") if rng.random() < 0.6 else w.b("sand"))
            w.folgen[(x, 0, z)] = -1
            w.folgen[(x, -1, z)] = -1
        elif d < 1.6:
            w.setze(x, 0, z, w.b(["gravel", "mossy_cobblestone", "coarse_dirt", "mud"][int(rng.integers(4))]))
            w.folgen[(x, 0, z)] = -1
            if w.frei(x, 1, z) and rng.random() < 0.3:
                (hohes("tall_grass") if rng.random() < 0.5 else (lambda w_, a, b, c: (w_.setze(a, b, c, w_.b("fern")),
                                                                                      w_.folgen.__setitem__((a, b, c),
                                                                                                            -1))))(
                    w, x, 1, z)
    return feld


def holzbruecke(st, pts, bach_feld, holz="spruce"):
    """Kleine Holzbrücke dort, wo der Weg den Bach kreuzt."""
    w = st.w
    for (x, z) in [(round(px), round(pz)) for (px, pz) in pts]:
        if bach_feld.get((x, z), 9) < 1.4:
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    w.setze(x + dx, 1, z + dz, w.b(f"{holz}_planks"))
                    w.folgen[(x + dx, 1, z + dz)] = -1


# ============================================================================ Waldstücke


def _verteilen(st, baumwahl, abstand, menge, **kw):
    st.verteile(abstand, int(menge * (st.g + 1) ** 2), baumwahl, **kw)


def _unterwuchs(st, arten, menge=1.0, blueten=False):
    st.verteile(2, int(260 * menge * (st.g + 1) ** 2),
                lambda x, z, rd, a: (busch(_s(st), arten[int(a * len(arten) * 0.999)], blueten=blueten and
                                           st.rng.random() < 0.3), 1.6))


def _totholz(st, art, menge=1.0):
    st.verteile(4, int(18 * menge * (st.g + 1) ** 2),
                lambda x, z, rd, a: (totholz(_s(st), art), 3) if st.rng.random() < 0.5 else
                ((baumstumpf(_s(st), art), 1.5) if st.rng.random() < 0.6 else (findling(_s(st)), 2.2)))


BODEN_LAUB = [("grass_block_s", 4), ("podzol", 2), ("coarse_dirt", 1), ("moss_block", 1.2), ("rooted_dirt", 0.5)]
PFL_LAUB = [("grass", 6), ("fern", 3), (hohes("large_fern"), 1), (hohes("tall_grass"), 1.2),
            ("lily_of_the_valley", 0.5), ("poppy", 0.3), ("dandelion", 0.3), ("brown_mushroom", 0.25),
            ("oxeye_daisy", 0.2), (beeren, 0.15)]


def eichenwald(seed, g=1, wegart=None):
    """Lichter Eichenwald: einzelne mächtige Eichen mit klarer Krone, Haselbüsche, Farne, Totholz."""
    st = Stueck(seed, g)

    def baum(x, z, rd, a):
        H = int(10 + st.rng.integers(5) + st.g * 2 - rd * 4)
        if st.rng.random() < 0.15:
            return birke(_s(st), H=H - 1), 5
        return laubbaum(_s(st), "oak", H=H), kronen_r(H) * 1.75
    _verteilen(st, baum, 9, 220)
    st.verteile(4, 80 * (st.g + 1) ** 2, lambda x, z, rd, a: (jungbaum(_s(st), "oak"), 2.5))
    _unterwuchs(st, ["oak", "azalea", "birch"], 0.8)
    _totholz(st, "oak")
    st.boden(BODEN_LAUB, PFL_LAUB, dichte=0.45)
    return st


def buchenwald(seed, g=1):
    """Hallenartiger Buchenwald: hohe glatte Stämme, hoch angesetzte Kronen, fast kein Unterwuchs,
    Laubteppich mit Moos."""
    st = Stueck(seed, g)

    def baum(x, z, rd, a):
        H = int(14 + st.rng.integers(5) + st.g * 2 - rd * 5)
        w = laubbaum(_s(st), "birch" if st.stil else "oak", H=H, blaetter=[("oak", 0.7), ("birch", 0.3)],
                     breit=0.85)
        return w, kronen_r(H, 0.85) * 1.7
    _verteilen(st, baum, 9, 200)
    _totholz(st, "oak", 0.6)
    st.boden([("podzol", 4), ("coarse_dirt", 2), ("moss_block", 1), ("grass_block_s", 1)],
             [("fern", 2), ("brown_mushroom", 0.6), ("lily_of_the_valley", 0.4), ("grass", 2)], dichte=0.18,
             belag_dichte=0.9)
    return st


def birkenhain(seed, g=1):
    """Heller Birkenhain: viele schlanke, weiße Birken in Gruppen, Farn- und Blumenteppich."""
    st = Stueck(seed, g)
    _verteilen(st, lambda x, z, rd, a: (birke(_s(st), H=int(9 + st.rng.integers(6) + st.g - rd * 3)), 5.2), 5, 400)
    _unterwuchs(st, ["birch", "azalea"], 0.4, blueten=True)
    st.boden([("grass_block_s", 6), ("moss_block", 0.6), ("coarse_dirt", 0.4)],
             [("grass", 6), ("fern", 4), (hohes("large_fern"), 1.5), ("lily_of_the_valley", 1), ("azure_bluet", 0.6),
              ("oxeye_daisy", 0.5), ("allium", 0.2)], dichte=0.55, belag_dichte=0.3)
    return st


def fichtenwald(seed, g=1):
    """Fichtenwald: hohe Fichten unterschiedlichen Alters, Moospolster, Heidelbeeren, Pilze; Stil 2 verschneit."""
    st = Stueck(seed, g)
    schnee = st.stil == 1
    st.schnee = False

    def baum(x, z, rd, a):
        H = int(12 + st.rng.integers(8) + st.g * 3 - rd * 6)
        return fichte(_s(st), H=H, schnee=schnee), (1.6 + H * 0.13) * 1.9 + 0.5
    _verteilen(st, baum, 6, 380)
    st.verteile(3, 140 * (st.g + 1) ** 2, lambda x, z, rd, a: (jungbaum(_s(st), "spruce"), 2))
    _totholz(st, "spruce")
    if schnee:
        st.boden([("snow_block", 4), ("podzol", 1), ("powder_snow_n", 0.3)],
                 [(schneeschicht, 6), ("fern", 0.5), (beeren, 0.3)], dichte=0.6)
    else:
        st.boden([("podzol", 4), ("moss_block", 2), ("coarse_dirt", 1), ("grass_block_s", 1)],
                 [("fern", 4), (hohes("large_fern"), 1.5), (beeren, 1), ("brown_mushroom", 0.5), ("moss_carpet", 2),
                  ("red_mushroom", 0.2)], dichte=0.5)
    return st


def kiefernwald(seed, g=1):
    """Lichter Kiefernwald: hohe rötliche Stämme mit Schirmkronen, sandiger Boden mit Heidekraut und Gras."""
    st = Stueck(seed, g)
    _verteilen(st, lambda x, z, rd, a: (kiefer(_s(st), H=int(13 + st.rng.integers(8) + st.g * 2)), 7.5), 8, 260)
    _unterwuchs(st, ["spruce", "oak"], 0.4)
    st.boden([("coarse_dirt", 2), ("sand", 1), ("grass_block_s", 3), ("podzol", 2)],
             [("grass", 5), ("fern", 1.5), (hohes("tall_grass"), 2), ("dead_bush", 0.3), (beeren, 0.4),
              ("allium", 0.2)], dichte=0.45)
    return st


def mischwald(seed, g=1):
    """Bunter Mischwald: Eichen, Buchen, Birken und Fichten in Gruppen, dazwischen Jungwuchs und Lichtungen."""
    st = Stueck(seed, g)

    def baum(x, z, rd, a):
        H = int(10 + st.rng.integers(6) + st.g * 2 - rd * 4)
        if a < 0.3:
            return fichte(_s(st), H=H + 3), 6.5
        if a < 0.5:
            return birke(_s(st), H=H), 5
        return laubbaum(_s(st), "oak", H=H, breit=0.9), kronen_r(H, 0.9) * 1.7
    _verteilen(st, baum, 7, 300)
    _unterwuchs(st, ["oak", "spruce", "azalea"], 0.7)
    _totholz(st, "oak")
    st.boden(BODEN_LAUB, PFL_LAUB, dichte=0.45)
    return st


def herbstwald(seed, g=1):
    """Leuchtender Herbstwald: Ahorne in Rot, Orange und Gold mit Laubteppich, dazwischen dunkle Fichten."""
    st = Stueck(seed, g)

    def baum(x, z, rd, a):
        H = int(9 + st.rng.integers(5) + st.g * 2 - rd * 3)
        if a < 0.2:
            return fichte(_s(st), H=H + 4), 6
        return herbstbaum(_s(st), H=H, stil=int(a * 7)), kronen_r(H) * 1.7
    _verteilen(st, baum, 8, 260)
    _unterwuchs(st, ["oak", "dark_oak"], 0.5)
    _totholz(st, "oak")
    st.boden([("podzol", 3), ("coarse_dirt", 2), ("grass_block_s", 2), ("rooted_dirt", 0.6)],
             [("fern", 2), ("grass", 3), ("brown_mushroom", 0.6), ("red_mushroom", 0.3), ("dead_bush", 0.3),
              (lambda w, x, y, z: (w.setze(x, y, z, w.b("orange_carpet") if w.rng.random() < 0.5 else
                                           w.b("red_carpet")), w.folgen.__setitem__((x, y, z), -1)), 2.5)],
             dichte=0.5)
    return st


def kirschhain(seed, g=1):
    """Kirschblütenhain: ausladende Kirschbäume mit rosa Wolken, Blütenteppich, Steinlaternen am Rand."""
    st = Stueck(seed, g)
    _verteilen(st, lambda x, z, rd, a: (kirschbaum(_s(st), H=int(7 + st.rng.integers(5) + st.g)), 9), 9, 240)
    _unterwuchs(st, ["azalea", "flowering_azalea"], 0.3)
    st.boden([("grass_block_s", 5), ("moss_block", 1)],
             [(bluetenblaetter, 6), ("grass", 3), ("allium", 0.3), ("pink_tulip", 0.4), ("lily_of_the_valley", 0.3)],
             dichte=0.6, belag_dichte=0.3)
    return st


def dunkelwald(seed, g=1):
    """Finsterer Dunkelwald: mächtige Dunkeleichen mit tiefen Kronen, Riesenpilze, Moos, Totholz."""
    from wald import riesenpilz
    st = Stueck(seed, g)

    def baum(x, z, rd, a):
        if a > 0.75 and st.rng.random() < 0.4:
            return riesenpilz(_s(st), rot=st.rng.random() < 0.5), 4
        H = int(10 + st.rng.integers(5) + st.g * 2)
        return dunkeleiche(_s(st), H=H), kronen_r(H, 1.25) * 1.6
    _verteilen(st, baum, 9, 220)
    _totholz(st, "dark_oak", 1.3)
    st.boden([("podzol", 3), ("moss_block", 3), ("coarse_dirt", 1), ("rooted_dirt", 1)],
             [("fern", 3), ("moss_carpet", 3), ("brown_mushroom", 1), ("red_mushroom", 0.6), (hohes("large_fern"), 1)],
             dichte=0.5)
    return st


def mammutwald(seed, g=1):
    """Mammutwald: gewaltige Mammutbäume weit auseinander, darunter Farnteppich und junge Fichten."""
    st = Stueck(seed, g)
    _verteilen(st, lambda x, z, rd, a: (mammutbaum(_s(st), H=int(24 + st.rng.integers(10) + st.g * 4)), 9), 12, 120)
    st.verteile(4, 120 * (st.g + 1) ** 2, lambda x, z, rd, a: (fichte(_s(st), H=int(7 + st.rng.integers(5))), 3))
    _totholz(st, "spruce", 1.2)
    st.boden([("podzol", 4), ("moss_block", 2), ("coarse_dirt", 1)],
             [("fern", 5), (hohes("large_fern"), 3), ("moss_carpet", 1), (beeren, 0.3)], dichte=0.6)
    return st


def weidenaue(seed, g=1):
    """Flussaue mit Bach: Trauerweiden am Ufer, Erlen und Schilf, Seerosen und Wildblumen."""
    st = Stueck(seed, g)
    pts = wegpunkte(st)
    bf = bach(st, pts, breite=1.3 + st.g * 0.5)
    _verteilen(st, lambda x, z, rd, a: (weide(_s(st), H=int(8 + st.rng.integers(4) + st.g)), 9)
               if bf.get((x, z), 9) > 2.2 else None, 9, 220)
    st.verteile(4, 120 * (st.g + 1) ** 2, lambda x, z, rd, a: (laubbaum(_s(st), "oak", H=int(7 + st.rng.integers(3)),
                                                                        breit=0.7), 3.5)
                if bf.get((x, z), 9) > 2.5 else None)
    st.boden([("grass_block_s", 5), ("mud", 0.6), ("moss_block", 0.6)],
             [("grass", 5), (hohes("tall_grass"), 3), ("blue_orchid", 0.4), ("azure_bluet", 0.4), (zuckerrohr, 0.5),
              ("oxeye_daisy", 0.3)], dichte=0.55, belag_dichte=0.3)
    return st


def zauberwald(seed, g=1):
    """Zauberwald: blühende Azaleen- und Kirschbäume, Leuchtpilze, glimmende Flechten, Sporenblüten."""
    st = Stueck(seed, g)

    def baum(x, z, rd, a):
        H = int(9 + st.rng.integers(5) + st.g)
        if a < 0.4:
            return kirschbaum(_s(st), H=H), 8.5
        return laubbaum(_s(st), "oak", H=H, blaetter=[("flowering_azalea", 0.5), ("azalea", 0.3), ("oak", 0.2)]), \
            kronen_r(H) * 1.7
    _verteilen(st, baum, 8, 240)
    _unterwuchs(st, ["flowering_azalea", "azalea"], 0.6, blueten=True)
    st.boden([("moss_block", 4), ("grass_block_s", 2), ("rooted_dirt", 0.5)],
             [("moss_carpet", 3), ("fern", 2), (leuchtflechte, 1), ("allium", 0.5), ("blue_orchid", 0.5),
              ("lily_of_the_valley", 0.6), (lambda w, x, y, z: (w.setze(x, y, z, w.b("shroomlight")),
                                                                 w.folgen.__setitem__((x, y, z), -1)), 0.15)],
             dichte=0.55)
    return st


def spukwald(seed, g=1):
    """Spukwald: kahle, verdrehte Bäume mit Spinnweben, Nebelfelder, Seelensand und Knochen."""
    from spuk import knorrbaum
    st = Stueck(seed, g)

    def baum(x, z, rd, a):
        w = _neu(_s(st))
        w.folgen = {}
        knorrbaum(w, 0, 0, 6 + st.rng.integers(5) + st.g * 2, "dark_oak" if a > 0.4 else "spruce", y0=0)
        return w, 6
    _verteilen(st, baum, 7, 240)
    _totholz(st, "dark_oak", 1.2)
    st.boden([("podzol", 3), ("coarse_dirt", 2), ("soul_soil", 1), ("mud", 0.6)],
             [("dead_bush", 3), ("cobweb", 0.8), ("fern", 1), ("wither_rose", 0.3), ("brown_mushroom", 0.5)],
             dichte=0.35)
    return st


def sumpfwald(seed, g=1):
    """Sumpfwald: Mangroven auf Stelzwurzeln im Schlamm, Wasserlöcher mit Seerosen, Schilf und ein Bohlensteg."""
    from wald import mangrovensumpf
    st = Stueck(seed, g)
    w = st.w
    r_n = Rauschen(w, 3)
    for x in range(-st.R - 6, st.R + 7):
        for z in range(-st.R - 6, st.R + 7):
            if st.rand(x, z) < 0.95 and r_n(x, 0, z) < 0.35:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
                w.folgen[(x, 0, z)] = -1
                w.folgen[(x, -1, z)] = -1
                if st.rng.random() < 0.15:
                    w.setze(x, 1, z, w.b("lily_pad"))
                    w.folgen[(x, 1, z)] = -1
    _verteilen(st, lambda x, z, rd, a: (weide(_s(st), H=int(7 + st.rng.integers(4))), 8) if a < 0.4 else
               (laubbaum(_s(st), "mangrove", H=int(8 + st.rng.integers(5)), blaetter=[("mangrove", 1)]), 7.5), 8, 220)
    pts = wegpunkte(st)
    feld = weg(st, pts, 1.2, "matsch", bohlen_bei=lambda x, z: True)
    bohlensteg(st, feld, "mangrove")
    st.boden([("mud", 3), ("grass_block_s", 2), ("moss_block", 1), ("packed_mud", 0.5)],
             [("grass", 3), (zuckerrohr, 1), ("fern", 1), ("blue_orchid", 0.4), ("brown_mushroom", 0.3)], dichte=0.45)
    return st


def urwald(seed, g=1):
    """Dschungel-Urwald: Urwaldriesen mit Brettwurzeln und Lianen, Palmen, Bambus und dichte Farne."""
    st = Stueck(seed, g)

    def baum(x, z, rd, a):
        if a < 0.25:
            return palme(_s(st)), 6
        H = int(16 + st.rng.integers(8) + st.g * 3 - rd * 5)
        if st.rng.random() < 0.45:
            return dschungelriese(_s(st), H=H), kronen_r(H, 1.1) * 1.6
        return laubbaum(_s(st), "jungle", H=H - 6, blaetter=[("jungle", 1)]), kronen_r(H - 6) * 1.6
    _verteilen(st, baum, 8, 260)
    _unterwuchs(st, ["jungle", "oak"], 0.9)
    st.boden([("grass_block_s", 4), ("podzol", 2), ("moss_block", 2), ("rooted_dirt", 0.6)],
             [("fern", 4), (hohes("large_fern"), 3), (bambus, 0.6), ("grass", 3), (hohes("tall_grass"), 1)],
             dichte=0.65)
    return st


def palmenhain(seed, g=1):
    """Palmenhain: schiefe Palmen auf Sand, Farne und Zuckerrohr, Muscheln und Treibholz."""
    st = Stueck(seed, g)
    _verteilen(st, lambda x, z, rd, a: (palme(_s(st), H=int(7 + st.rng.integers(5) + st.g)), 7), 7, 260)
    st.boden([("sand", 5), ("grass_block_s", 1), ("coarse_dirt", 0.3)],
             [("dead_bush", 0.4), (zuckerrohr, 0.6), ("fern", 1), ("grass", 1),
              (lambda w, x, y, z: (w.setze(x, y, z, MB.muschel(w)), w.folgen.__setitem__((x, y, z), -1)), 0.4)],
             dichte=0.25, belag_dichte=0.9)
    return st


def savanne(seed, g=1):
    """Savanne: weit verstreute Schirmakazien, Dornbüsche, hohes goldenes Gras und rote Erde."""
    st = Stueck(seed, g)
    _verteilen(st, lambda x, z, rd, a: (akazie(_s(st), H=int(7 + st.rng.integers(4) + st.g)), 7), 10, 160)
    _unterwuchs(st, ["acacia", "oak"], 0.3)
    st.boden([("grass_block_s", 4), ("coarse_dirt", 2), ("red_sand", 0.5)],
             [("grass", 6), (hohes("tall_grass"), 4), ("dead_bush", 0.5)], dichte=0.6, belag_dichte=0.5)
    return st


def bergwald(seed, g=1):
    """Bergwald zwischen Felsen: Fichten und Kiefern auf Felsrippen, Geröll, Moospolster."""
    st = Stueck(seed, g)
    st.verteile(5, 14 * (st.g + 1) ** 2, lambda x, z, rd, a: (findling(_s(st), moosig=a < 0.6), 2.5))
    _verteilen(st, lambda x, z, rd, a: (fichte(_s(st), H=int(9 + st.rng.integers(8) + st.g * 2), schmal=0.85), 6)
               if a < 0.6 else (kiefer(_s(st), H=int(10 + st.rng.integers(6) + st.g)), 7), 7, 260)
    st.boden([("stone", 1.5), ("andesite", 1), ("gravel", 1), ("moss_block", 1.5), ("podzol", 2), ("coarse_dirt", 1),
              ("grass_block_s", 1)],
             [("fern", 3), ("grass", 2), (beeren, 0.4), ("moss_carpet", 2)], dichte=0.4, belag_dichte=0.85)
    return st


def lichtung(seed, g=1):
    """Waldlichtung: Ring aus Bäumen um eine blühende Wiese mit einem einzelnen alten Baum in der Mitte."""
    st = Stueck(seed, g)
    st.plaetze.append((0, 0, 0))
    st.stempel(laubbaum(_s(st), "oak", H=int(13 + st.g * 3), breit=1.2, dick=True), 0, 0)
    st.plaetze.append((0, 0, st.R * 0.45))
    _verteilen(st, lambda x, z, rd, a: (laubbaum(_s(st), "oak", H=int(9 + st.rng.integers(4) + st.g)), 9) if a > 0.3
               else (birke(_s(st)), 5), 7, 200, rand_min=0.55)
    _unterwuchs(st, ["oak", "azalea"], 0.4, blueten=True)
    st.boden([("grass_block_s", 6), ("coarse_dirt", 0.3)],
             [("grass", 6), (hohes("tall_grass"), 3), ("poppy", 1), ("dandelion", 1), ("cornflower", 0.8),
              ("oxeye_daisy", 0.8), ("azure_bluet", 0.6), (hohes("lilac"), 0.3), (hohes("rose_bush"), 0.3),
              (hohes("peony"), 0.3)], dichte=0.6, belag_dichte=0.2)
    return st


def unterholz(seed, g=1):
    """Unterholz & Waldrand: Büsche, Jungbäume, Farne, Brombeeren – füllt Lücken und Übergänge zur Wiese."""
    st = Stueck(seed, g)
    st.verteile(3, 300 * (st.g + 1) ** 2, lambda x, z, rd, a: (jungbaum(_s(st), ["oak", "birch", "spruce"][int(a * 2.99)]),
                                                               2.2) if st.rng.random() < 0.3 else
                (busch(_s(st), ["oak", "azalea", "spruce", "birch"][int(a * 3.99)], r=1.2 + st.rng.random() * 1.2,
                       blueten=st.rng.random() < 0.2), 2))
    st.boden(BODEN_LAUB, PFL_LAUB + [(beeren, 0.8), (hohes("large_fern"), 1.5)], dichte=0.6)
    return st


# ---------------------------------------------------------------------------- Wälder mit Wegen


def waldweg(seed, g=1):
    """Waldweg: ein geschwungener Erdweg mit Wurzeln, Pfützen und Kieselrand durch einen Eichen-Mischwald,
    Bänke und Holzstapel am Rand."""
    st = mischwald(seed, g)
    pts = wegpunkte(st)
    weg(st, pts, 1.5 + st.g * 0.3, "erde", pfuetzen=0.12, wurzelquer=0.3)
    wegdeko(st, pts)
    return st


def waldkreuzung(seed, g=1):
    """Wegkreuzung im Wald: zwei Kieswege kreuzen sich auf einer kleinen Lichtung mit Wegweiser, Laterne
    und Bank, ringsum Buchen und Eichen."""
    st = Stueck(seed, g)
    pts = wegpunkte(st, "kreuz")
    st.plaetze.append((0, 0, 6))
    st.plaetze += [(round(x), round(z), 2.5) for (x, z) in pts[::3]]
    _verteilen(st, lambda x, z, rd, a: (laubbaum(_s(st), "oak", H=int(11 + st.rng.integers(4) + st.g * 2)), 10)
               if a > 0.35 else (birke(_s(st)), 5), 8, 260)
    _unterwuchs(st, ["oak", "azalea"], 0.6)
    st.boden(BODEN_LAUB, PFL_LAUB, dichte=0.45)
    weg(st, pts, 1.6 + st.g * 0.3, "kies", wurzelquer=0.15)
    w = st.w
    for y in range(1, 4):
        w.setze(0, y, 0, w.b("spruce_fence", north=False, south=False, east=False, west=False, waterlogged=False)
                if y < 3 else w.b("spruce_log", axis="y"))
        w.folgen[(0, y, 0)] = -1
    for (x, z, f) in ((1, 0, "east"), (-1, 0, "west"), (0, 1, "south")):
        w.setze(x, 3, z, w.b("spruce_trapdoor", facing=f, half="top", open=True, powered=False, waterlogged=False))
        w.folgen[(x, 3, z)] = -1
    wegdeko(st, pts)
    return st


def bohlenweg(seed, g=1):
    """Bohlenweg durchs Moor: ein Steg aus Brettern auf Pfählen führt durch einen nassen Birken- und Weidenwald
    mit Wasserlöchern, Torfmoos und Wollgras."""
    st = Stueck(seed, g)
    w = st.w
    r_n = Rauschen(w, 3)
    for x in range(-st.R - 6, st.R + 7):
        for z in range(-st.R - 6, st.R + 7):
            if st.rand(x, z) < 0.95 and r_n(x, 0, z) < 0.4:
                w.setze(x, 0, z, w.b("water", level=0) if r_n(x, 0, z) < 0.3 else w.b("mud"))
                w.folgen[(x, 0, z)] = -1
    _verteilen(st, lambda x, z, rd, a: (birke(_s(st), H=int(7 + st.rng.integers(5))), 5) if a > 0.4 else
               (weide(_s(st), H=int(7 + st.rng.integers(3))), 8), 7, 240)
    pts = wegpunkte(st)
    feld = weg(st, pts, 1.2, "matsch", bohlen_bei=lambda x, z: True)
    bohlensteg(st, feld, "spruce")
    st.boden([("moss_block", 3), ("mud", 2), ("grass_block_s", 2)],
             [("grass", 3), ("fern", 1), (zuckerrohr, 0.5), ("lily_of_the_valley", 0.4), ("moss_carpet", 2)],
             dichte=0.5)
    return st


def bachtal(seed, g=1):
    """Bachtal: ein klarer Bach mit Kiesbett windet sich durch einen Laubwald, ein Weg folgt ihm und quert ihn
    über eine Holzbrücke; moosige Steine, Farne und Erlen am Ufer."""
    st = Stueck(seed, g)
    pts_b = wegpunkte(st)
    bf = bach(st, pts_b, breite=1.2 + st.g * 0.4)
    pts_w = wegpunkte(st)
    for (x, z) in pts_w[::4]:
        st.plaetze.append((round(x), round(z), 2.5))
    _verteilen(st, lambda x, z, rd, a: (laubbaum(_s(st), "oak", H=int(10 + st.rng.integers(5) + st.g * 2)), 10)
               if bf.get((x, z), 9) > 2.5 else None, 8, 260)
    _unterwuchs(st, ["oak", "azalea"], 0.5)
    st.verteile(4, 40 * (st.g + 1) ** 2, lambda x, z, rd, a: (findling(_s(st)), 2.5) if bf.get((x, z), 9) < 4 else None)
    st.boden(BODEN_LAUB, PFL_LAUB, dichte=0.45)
    weg(st, pts_w, 1.3 + st.g * 0.2, "erde", pfuetzen=0.08)
    holzbruecke(st, pts_w, bf)
    return st


def hohlweg(seed, g=1):
    """Hohlweg: ein tief eingeschnittener alter Weg zwischen bewachsenen Erdwällen, aus denen Wurzeln ragen,
    oben schließen sich die Kronen; matschiger Grund mit Steinen."""
    st = eichenwald(seed, g)
    w = st.w
    pts = wegpunkte(st)
    feld = weg(st, pts, 2.0 + st.g * 0.4, "matsch", pfuetzen=0.15, trittsteine=True)
    for (x, z), d in list(feld.items()):
        if 1.0 < d:
            continue
    rand = {}
    for (px, pz) in pts:
        b = 2.0 + st.g * 0.4
        for x in range(int(px - b) - 4, int(px + b) + 5):
            for z in range(int(pz - b) - 4, int(pz + b) + 5):
                d = math.hypot(x - px, z - pz) - b
                if 0 < d < 3.5:
                    rand[(x, z)] = min(rand.get((x, z), 9), d)
    rng = st.rng
    for (x, z), d in rand.items():
        if (x, z) in feld and feld[(x, z)] <= 1.0:
            continue
        if st.rand(x, z) > 1.0:
            continue
        hh = int(3 - d * 0.7)
        for y in range(1, hh + 1):
            if w.frei(x, y, z):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == hh else
                        w.b("rooted_dirt") if rng.random() < 0.3 else w.b("dirt"))
                w.folgen[(x, y, z)] = -1
        if hh > 0 and rng.random() < 0.08 and w.frei(x, hh + 1, z):
            w.setze(x, hh + 1, z, w.b("fern"))
            w.folgen[(x, hh + 1, z)] = -1
    return st


def steinpfad(seed, g=1):
    """Steinpfad im Bergwald: ein Pfad aus Bruchstein und moosigen Platten mit Trittstufen windet sich zwischen
    Fichten und Felsblöcken, Geländer aus Holz an steilen Stellen."""
    st = bergwald(seed, g)
    pts = wegpunkte(st)
    weg(st, pts, 1.3 + st.g * 0.2, "stein", trittsteine=True, rand_steine=0.12)
    wegdeko(st, pts)
    return st


def forstweg(seed, g=1):
    """Forstweg: breiter Kiesweg durch einen Fichtenforst mit Holzpoltern (gestapelte Stämme), Hochsitz
    und Schlagflächen mit Baumstümpfen."""
    st = fichtenwald(seed, g)
    w = st.w
    pts = wegpunkte(st)
    weg(st, pts, 2.2 + st.g * 0.4, "kies", pfuetzen=0.1)
    rng = st.rng
    for i in range(0, len(pts), max(15, len(pts) // 3)):
        px, pz = pts[i]
        bx, bz = round(px) + 4, round(pz)
        if st.rand(bx, bz) > 0.85:
            continue
        for k in range(5):
            for h in range(3 - k // 2):
                for y in range(1, 5):
                    w.bloecke.pop((bx + k, y, bz + h), None)
                w.setze(bx + k, 1 + h // 2 + (k // 3), bz + h, w.b("spruce_log", axis="z")) if False else None
        for z in range(3):
            for y in (1, 2):
                for k in range(4 - y):
                    w.setze(bx + k + y - 1, y, bz + z, w.b("spruce_log", axis="z"))
                    w.folgen[(bx + k + y - 1, y, bz + z)] = -1
    hx, hz = round(pts[len(pts) // 2][0]) - 5, round(pts[len(pts) // 2][1])
    for y in range(1, 6):
        for dx, dz in ((0, 0), (2, 0), (0, 2), (2, 2)):
            w.setze(hx + dx, y, hz + dz, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                             waterlogged=False))
            w.folgen[(hx + dx, y, hz + dz)] = -1
    for dx in range(3):
        for dz in range(3):
            w.setze(hx + dx, 6, hz + dz, w.b("spruce_planks"))
            w.setze(hx + dx, 8, hz + dz, w.b("spruce_slab", type="bottom", waterlogged=False))
            w.folgen[(hx + dx, 6, hz + dz)] = -1
            w.folgen[(hx + dx, 8, hz + dz)] = -1
    for y in range(1, 6):
        w.setze(hx + 1, y, hz - 1, w.b("ladder", facing="north", waterlogged=False))
        w.folgen[(hx + 1, y, hz - 1)] = -1
    return st


def rastplatz(seed, g=1):
    """Rastplatz auf einer Waldlichtung: Feuerstelle mit Baumstamm-Bänken, Unterstand, Holzstapel, Brunnen
    und ein Weg, der hindurchführt."""
    st = lichtung(seed, g)
    w = st.w
    pts = wegpunkte(st)
    weg(st, pts, 1.4, "erde", wurzelquer=0.1)
    cx, cz = round(st.R * 0.25), round(-st.R * 0.2)
    for x in range(cx - 3, cx + 4):
        for z in range(cz - 3, cz + 4):
            for y in range(1, 8):
                if (x, y, z) in w.bloecke and not w.P.name(w.bloecke[(x, y, z)]).endswith("_log"):
                    w.bloecke.pop((x, y, z), None)
    w.setze(cx, 1, cz, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for (dx, dz, ax) in ((-2, 0, "z"), (2, 0, "z"), (0, 2, "x")):
        for k in (-1, 0, 1):
            p = (cx + dx + (k if ax == "x" else 0), 1, cz + dz + (k if ax == "z" else 0))
            w.setze(*p, w.b("stripped_oak_log", axis=ax))
            w.folgen[p] = -1
    w.folgen[(cx, 1, cz)] = -1
    for x, z in ((cx - 3, cz - 3), (cx - 3, cz - 1), (cx - 1, cz - 3)):
        pass
    return st


def _wrap(f):
    def g(seed, groesse=1):
        st = f(seed, groesse)
        return _fertig(st.w if isinstance(st, Stueck) else st)
    g.__doc__ = f.__doc__
    return g


WALD = {k: (n, _wrap(f)) for k, (n, f) in {
    "eichenwald": ("Eichenwald", eichenwald),
    "buchenwald": ("Buchenwald", buchenwald),
    "birkenhain": ("Birkenhain", birkenhain),
    "fichtenwald": ("Fichtenwald", fichtenwald),
    "kiefernwald": ("Kiefernwald", kiefernwald),
    "mischwald": ("Mischwald", mischwald),
    "herbstwald": ("Herbstwald", herbstwald),
    "kirschhain": ("Kirschblütenhain", kirschhain),
    "dunkelwald": ("Dunkelwald", dunkelwald),
    "mammutwald": ("Mammutwald", mammutwald),
    "weidenaue": ("Weidenaue mit Bach", weidenaue),
    "zauberwald": ("Zauberwald", zauberwald),
    "spukwald": ("Spukwald", spukwald),
    "sumpfwald": ("Sumpfwald mit Steg", sumpfwald),
    "urwald": ("Dschungel-Urwald", urwald),
    "palmenhain": ("Palmenhain", palmenhain),
    "savanne": ("Savanne", savanne),
    "bergwald": ("Bergwald", bergwald),
    "lichtung": ("Waldlichtung", lichtung),
    "unterholz": ("Unterholz & Waldrand", unterholz),
    "waldweg": ("Waldweg", waldweg),
    "waldkreuzung": ("Wegkreuzung im Wald", waldkreuzung),
    "bohlenweg": ("Bohlenweg durchs Moor", bohlenweg),
    "bachtal": ("Bachtal mit Brücke", bachtal),
    "hohlweg": ("Hohlweg", hohlweg),
    "steinpfad": ("Steinpfad im Bergwald", steinpfad),
    "forstweg": ("Forstweg mit Holzpolter", forstweg),
    "rastplatz": ("Rastplatz auf der Lichtung", rastplatz),
}.items()}

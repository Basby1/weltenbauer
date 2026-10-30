"""Zukunftsstadt II – zwanzig weitere Bauten: Stelzen-Kuppelhäuser, Energie-Ladestation, Drohnenhafen, Meereskuppel-
Labor, Algenreaktor-Turm, Schwebekugel-Brunnen, Leuchtbaum-Allee, Turbinenbrücke, Ringhabitat, Kapselturm,
Recyclingzentrum, Hoverball-Arena, Kaskadenturm, Aussichtsnadel, Solarblumen-Platz, Robotik-Werkstatt,
Terrassenpyramide, Luftschiff-Terminal, Saatgutbunker und Röhrenbahn."""

from __future__ import annotations

import math

from erw_basis import M, S, baum, figur, hoehe, wiese
from erw_markt import mensch
from flora import _neu
from leuchtwald2 import bez, kugel, laubball
from lib import Rauschen
from skulptur import Skulptur, dreh_x, ell, kap, kasten, torus
from steampunk2 import huelle, zylinder
from zukunft import boden, glaskuppel, glasturm, strasse

WEISS = "white_concrete"


def leuchte(w, x, y, z):
    w.setze(x, y, z, w.b("end_rod", facing="up"))


def mast(w, x, z, h, y0=1):
    for y in range(y0, y0 + h):
        w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
    leuchte(w, x, y0 + h, z)


def scheibe(w, cx, y, cz, r, blk, rand=None):
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            d = math.hypot(x - cx, z - cz)
            if d <= r:
                w.setze(x, y, z, rand if rand is not None and d > r - 1 else blk)


def gleiter(w, u, farbe="white_concrete"):
    """Kleines Schwebefahrzeug als Figur."""
    return [(ell(0, 1.2, 0, 2.2, 0.7, 1.1), w.b(farbe)), (ell(0.3, 1.8, 0, 1.1, 0.6, 0.8),
                                                         w.b("light_blue_stained_glass")),
            (kasten(-2.0, 0.4, -0.9, 2.0, 0.6, 0.9), w.b("cyan_concrete"))]


def roboter(w, farbe="light_gray_concrete"):
    return [(kasten(-0.7, 0, -0.4, -0.2, 2.0, 0.4), w.b("iron_block")), (kasten(0.2, 0, -0.4, 0.7, 2.0, 0.4),
                                                                         w.b("iron_block")),
            (kasten(-1.0, 2.0, -0.6, 1.0, 4.0, 0.6), w.b(farbe)), (kasten(-0.6, 4.2, -0.5, 0.6, 5.2, 0.5),
                                                                   w.b("white_concrete")),
            (kasten(-0.4, 4.5, 0.45, 0.4, 4.8, 0.6), w.b("sea_lantern")),
            (kap((1.2, 3.8, 0), (1.6, 2.0, 0.4), 0.3), w.b("iron_block")),
            (kap((-1.2, 3.8, 0), (-1.6, 2.0, 0.4), 0.3), w.b("iron_block"))]


# ============================================================================ Bauten

def stelzenkuppel(seed, g=2):
    """Stelzen-Kuppelhäuser: runde Wohnkuppeln aus Glas und weißem Rahmenwerk stehen auf schlanken Stelzen über einem
    Teich, umlaufende Balkone, Wendeltreppen und Stege verbinden sie."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, huegel=0.15)
    rn = Rauschen(w, 4)
    for (x, z), h in zellen.items():
        if math.hypot(x, z) + rn(x, 0, z) * 3 < R * 0.55:
            for y in range(-1, 2):
                w.bloecke.pop((x, y, z), None)
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("water", level=0))
            w.setze(x, -2, z, w.b("sand"))
    n = 2 + (g >= 2)
    pos = []
    for k in range(n):
        a = k / n * 2 * math.pi + 0.4
        cx, cz = round(math.cos(a) * R * 0.38), round(math.sin(a) * R * 0.38)
        rk = 2.5 + 1.2 * s
        yb = int(4 + 2 * s + k)
        for j in range(6):
            b = j / 6 * 2 * math.pi
            px, pz = round(cx + math.cos(b) * rk * 0.6), round(cz + math.sin(b) * rk * 0.6)
            for y in range(-1, yb):
                w.setze(px, y, pz, w.b(WEISS))
        scheibe(w, cx, yb, cz, rk + 1.5, w.b("smooth_quartz"), rand=w.b("light_gray_concrete"))
        for x in range(int(cx - rk) - 3, int(cx + rk) + 4):
            for z in range(int(cz - rk) - 3, int(cz + rk) + 4):
                if rk + 0.5 < math.hypot(x - cx, z - cz) <= rk + 1.5:
                    w.setze(x, yb + 1, z, w.b("glass_pane"))
        glaskuppel(w, cx, cz, yb + 1, rk, rahmen=WEISS, glas="light_blue_stained_glass")
        steps = int(yb * 3)
        for t in range(steps):
            b = t * 0.5
            y = t // 3
            w.setze(round(cx + math.cos(b) * (rk + 2.5)), y + 1, round(cz + math.sin(b) * (rk + 2.5)),
                    w.b("smooth_quartz_slab", type="bottom", waterlogged=False), False)
        pos.append((cx, yb, cz))
    for (a, b) in zip(pos, pos[1:]):
        n2 = int(math.hypot(b[0] - a[0], b[2] - a[2]))
        for t in range(n2 + 1):
            q = t / max(1, n2)
            w.setze(round(a[0] + (b[0] - a[0]) * q), round(a[1] + (b[1] - a[1]) * q), round(a[2] + (b[2] - a[2]) * q),
                    w.b("smooth_quartz_slab", type="bottom", waterlogged=False), False)
    return w


def ladestation(seed, g=1):
    """Energie-Ladestation: ein geschwungenes Solardach auf Y-förmigen Stützen überspannt Ladebuchten mit leuchtenden
    Ladesäulen; darunter parken Schwebegleiter, daneben ein gläserner Kiosk."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.1)
    boden(w, int(R * 0.85), rund=True, muster=True)
    A, B = int(5 * s + 4), int(3 * s + 3)
    H = int(4 + s)
    for x in range(-A, A + 1):
        for z in range(-B, B + 1):
            y = H + round(1.5 * math.cos(x / A * math.pi / 2))
            w.setze(x, y, z, w.b(WEISS) if abs(z) == B or abs(x) == A else w.b("daylight_detector", inverted=False,
                                                                                power=0))
            w.setze(x, y - 1, z, w.b("light_gray_concrete")) if (x + z) % 4 == 0 else None
    for x in range(-A + 2, A - 1, 4):
        for y in range(1, H - 1):
            w.setze(x, y, 0, w.b(WEISS))
        for d in (-1, 1):
            w.setze(x, H - 1, d, w.b(WEISS))
            w.setze(x, H, d * 2, w.b(WEISS))
    for k, x in enumerate(range(-A + 1, A, 3)):
        for sz in (-B + 1, B - 1):
            w.setze(x, 1, sz, w.b("iron_block"))
            w.setze(x, 2, sz, w.b("cyan_stained_glass") if k % 2 else w.b("lime_stained_glass"))
            w.setze(x, 0, sz - (1 if sz > 0 else -1), w.b("cyan_concrete"))
    for k in range(int(1 + s)):
        figur(w, 0.6 * s + 0.5, gleiter(w, u=1, farbe=["white_concrete", "red_concrete", "blue_concrete"][k % 3]),
              (-3, -1, -2), (3, 3, 2), pos=(-A + 3 + k * 6, 1, -B + 3 if k % 2 else B - 3), winkel=0.0)
    kx = A + 4
    for x in range(kx - 2, kx + 3):
        for z in range(-2, 3):
            for y in range(1, 4):
                if max(abs(x - kx), abs(z)) == 2:
                    w.setze(x, y, z, w.b(WEISS) if abs(x - kx) == 2 and abs(z) == 2 else w.b("glass"))
            w.setze(x, 4, z, w.b(WEISS))
    return w


def drohnenhafen(seed, g=2):
    """Drohnenhafen: ein schlanker Logistikturm, an dem versetzt runde Landeplattformen mit Leuchtringen auskragen;
    Lieferdrohnen schweben an und ab, unten ein Paketzentrum mit Förderband."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.1)
    boden(w, int(R * 0.8))
    H = int(14 * s + 10)
    glasturm(w, 0, 0, 1, 2, 2, H, seed, glas="gray_stained_glass", band=3)
    n = int(3 + 1.5 * s)
    rp = 2 + s
    for k in range(n):
        a = k * 2.0
        y = 5 + int(k * (H - 6) / n)
        cx, cz = round(math.cos(a) * (rp + 3)), round(math.sin(a) * (rp + 3))
        scheibe(w, cx, y, cz, rp, w.b("light_gray_concrete"), rand=w.b("sea_lantern"))
        w.setze(cx, y, cz, w.b("yellow_concrete"))
        for t in range(1, int(rp + 3)):
            w.setze(round(math.cos(a) * t), y - 1, round(math.sin(a) * t), w.b(WEISS), False)
    rng = w.rng
    for k in range(int(4 + 3 * s)):
        x, z = int((rng.random() - 0.5) * R * 1.4), int((rng.random() - 0.5) * R * 1.4)
        y = int(6 + rng.random() * H)
        if math.hypot(x, z) < 4:
            continue
        w.setze(x, y, z, w.b("iron_block"))
        for dx, dz in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            w.setze(x + dx, y, z + dz, w.b("black_concrete"), False)
        w.setze(x, y - 1, z, w.b("brown_concrete"), False)
    bx = int(R * 0.45)
    for x in range(bx - 3, bx + 4):
        for z in range(-4, 5):
            for y in range(1, 4):
                if max(abs(x - bx), abs(z)) in (3, 4) and (abs(x - bx) == 3 or abs(z) == 4):
                    w.setze(x, y, z, w.b(WEISS) if y != 2 else w.b("light_blue_stained_glass"))
            w.setze(x, 4, z, w.b("light_gray_concrete"))
    for z in range(-int(R * 0.6), -4):
        w.setze(bx, 1, z, w.b("black_concrete"))
        if z % 3 == 0:
            w.setze(bx, 2, z, w.b("brown_concrete"))
    return w


def meereslabor(seed, g=2):
    """Meereskuppel-Labor: am Meeresgrund stehen gläserne Forschungskuppeln, verbunden durch Röhrengänge, mit
    Schleusenturm, Scheinwerfern, Seetanggärten und Korallen ringsum."""
    from elemente import korallenbewuchs
    from erw_unterwasser import grund
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    grund(w, R, dichte=1.0, felsen=int(2 + 2 * s))
    kuppeln = [(0, 0, 3 + 1.6 * s), (-int(R * 0.45), int(R * 0.2), 2 + s), (int(R * 0.4), -int(R * 0.25), 2 + s)]
    for (cx, cz, rk) in kuppeln:
        y0 = hoehe(w, cx, cz, 8) + 1
        scheibe(w, cx, y0 - 1, cz, rk + 1, w.b("light_gray_concrete"), rand=w.b("sea_lantern"))
        glaskuppel(w, cx, cz, y0, rk, rahmen=WEISS, glas="glass")
        for x in range(int(cx - rk), int(cx + rk) + 1):
            for z in range(int(cz - rk), int(cz + rk) + 1):
                for y in range(y0, y0 + int(rk)):
                    if math.sqrt((x - cx) ** 2 + (y - y0) ** 2 + (z - cz) ** 2) < rk - 1:
                        w.bloecke.pop((x, y, z), None)
    for (a, b) in ((kuppeln[0], kuppeln[1]), (kuppeln[0], kuppeln[2])):
        ya = hoehe(w, a[0], a[1], 4) + 2
        zylinder(w, (a[0], ya, a[1]), (b[0], ya, b[1]), 1.4, w.b("glass"), hohl=True, nieten=w.b(WEISS), abstand=3)
    for y in range(int(3 + 1.6 * s) + 1, int(3 + 1.6 * s) + int(6 + 3 * s)):
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            w.setze(dx, y, dz, w.b(WEISS) if y % 3 else w.b("sea_lantern"))
    korallenbewuchs(w, 0.25)
    return w


def algenturm(seed, g=2):
    """Algenreaktor-Turm: ein runder Turm aus spiralförmig gewundenen, grün leuchtenden Glasröhren zwischen weißen
    Ringen, oben eine Verarbeitungskanzel, unten ein Technikgebäude mit Leitungen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    boden(w, int(R * 0.7))
    rt = 3 + s
    H = int(12 * s + 10)
    n = int(10 + 4 * s)
    for k in range(n):
        for y in range(1, H):
            a = k / n * 2 * math.pi + y * 0.08
            x, z = round(math.cos(a) * rt), round(math.sin(a) * rt)
            w.setze(x, y, z, w.b(["lime_stained_glass", "green_stained_glass"][k % 2]))
    for y in range(1, H, 4):
        for x in range(-int(rt) - 2, int(rt) + 3):
            for z in range(-int(rt) - 2, int(rt) + 3):
                if rt - 0.5 < math.hypot(x, z) <= rt + 1.2:
                    w.setze(x, y, z, w.b(WEISS))
    for y in range(1, H):
        w.setze(0, y, 0, w.b("light_gray_concrete") if y % 4 else w.b("sea_lantern"))
    scheibe(w, 0, H, 0, rt + 2, w.b("light_gray_concrete"), rand=w.b(WEISS))
    glaskuppel(w, 0, 0, H + 1, rt + 1, rahmen=WEISS, glas="lime_stained_glass")
    for x in range(int(rt) + 3, int(rt) + 9):
        for z in range(-3, 4):
            for y in range(1, 4):
                if x in (int(rt) + 3, int(rt) + 8) or abs(z) == 3:
                    w.setze(x, y, z, w.b(WEISS) if y != 2 else w.b("glass"))
            w.setze(x, 4, z, w.b("light_gray_concrete"))
    zylinder(w, (int(rt) + 1, 2, 0), (int(rt) + 3, 2, 0), 0.6, w.b("iron_block"))
    return w


def schwebekugelbrunnen(seed, g=2):
    """Schwebekugel-Brunnen: über einem runden Wasserbecken schweben, von leuchtenden Stäben gehalten, gläserne Kugeln
    mit leuchtendem Kern und schräg gestellte Quarzringe – ein Brunnen ohne Schwerkraft."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    boden(w, int(R * 0.85))
    rb = R * 0.5
    for x in range(-int(rb) - 1, int(rb) + 2):
        for z in range(-int(rb) - 1, int(rb) + 2):
            d = math.hypot(x, z)
            if d <= rb:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("sea_lantern") if (x + z) % 5 == 0 else w.b("light_blue_concrete"))
            elif d <= rb + 1:
                w.setze(x, 1, z, w.b("smooth_quartz_slab", type="bottom", waterlogged=False))
    kugeln = [(0, 6 + 3 * s, 0, 1.6 + 0.8 * s), (-rb * 0.5, 4 + 2 * s, rb * 0.3, 1 + 0.5 * s),
              (rb * 0.45, 5 + 2.5 * s, -rb * 0.35, 1.1 + 0.5 * s), (rb * 0.2, 3 + s, rb * 0.5, 0.8 + 0.3 * s)]
    for (x, y, z, r) in kugeln:
        kugel(w, x, y, z, r, w.b("light_blue_stained_glass"))
        w.setze(round(x), round(y), round(z), w.b("sea_lantern"))
        for yy in range(1, int(y - r)):
            w.setze(round(x), yy, round(z), w.b("end_rod", facing="up"), False)
    u = 1.0
    Sk = Skulptur(w, u)
    Sk.mat("q", w.b("smooth_quartz"))
    Sk.plus(torus(0, 0, 0, 3 + 1.5 * s, 0.4, achse="y"), "q")
    Sk.rendern((-6 - 2 * s, -3, -6 - 2 * s), (6 + 2 * s, 3, 6 + 2 * s), versatz=(0.5, 6 + 3 * s, 0.5),
               dreh=dreh_x(0.5), ueberschreiben=False)
    return w


def leuchtbaumallee(seed, g=2):
    """Leuchtbaum-Allee: ein breiter Boulevard, gesäumt von künstlichen Bäumen aus weißen Stämmen mit Kronen aus
    farbigem Glas und Leuchtpunkten, dazwischen Bänke, Wasserrinnen und Schwebegleiter."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wiese(w, R, huegel=0.1)
    strasse(w, -R, R, 0, breite=int(2 + s), achse="x", lampen=False)
    farben = ["cyan_stained_glass", "light_blue_stained_glass", "magenta_stained_glass", "lime_stained_glass"]
    for sz in (-1, 1):
        zb = sz * int(4 + s * 1.5)
        for x in range(-R + 2, R - 1):
            if math.hypot(x, zb) > R - 1:
                continue
            w.setze(x, 0, zb, w.b("smooth_stone"))
            w.setze(x, 0, zb + sz, w.b("water", level=0) if x % 6 else w.b("smooth_stone"))
        for k, x in enumerate(range(-R + 4, R - 3, int(5 + s))):
            if math.hypot(x, zb) > R - 3:
                continue
            Hb = int(5 + 2 * s)
            for y in range(1, Hb):
                w.setze(x, y, zb, w.b(WEISS))
            for d in range(int(2 + s)):
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    w.setze(x + dx * (d + 1), Hb + d // 2, zb + dz * (d + 1), w.b(WEISS), False)
            f = farben[(k + (sz > 0)) % len(farben)]
            for dx in range(-int(2 + s), int(3 + s)):
                for dz in range(-int(2 + s), int(3 + s)):
                    if math.hypot(dx, dz) <= 2 + s:
                        w.setze(x + dx, Hb + 1 + int(s), zb + dz, w.b(f) if (dx + dz) % 3 else w.b("sea_lantern"),
                                False)
            w.setze(x + 2, 1, zb + sz * 2, w.b("quartz_stairs", facing="south" if sz < 0 else "north",
                                                half="bottom", shape="straight", waterlogged=False))
    figur(w, 0.55 * s + 0.4, gleiter(w, 1, "red_concrete"), (-3, -1, -2), (3, 3, 2), pos=(-R // 3, 2, 1))
    figur(w, 0.55 * s + 0.4, gleiter(w, 1, "white_concrete"), (-3, -1, -2), (3, 3, 2), pos=(R // 3, 2, -1),
          winkel=math.pi)
    return w


def turbinenbruecke(seed, g=2):
    """Turbinenbrücke: eine schlanke Schrägseilbrücke über einen Fluss, auf deren Pylonen sich gewendelte Vertikal-
    Windturbinen drehen; Leuchtstreifen säumen die Fahrbahn."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, huegel=0.1)
    rw = int(R * 0.5)
    for (x, z), h in list(zellen.items()):
        if abs(x) <= rw:
            for y in range(-2, 3):
                w.bloecke.pop((x, y, z), None)
            for y in range(-2, 1):
                w.setze(x, y, z, w.b("water", level=0))
            w.setze(x, -3, z, w.b("gravel"))
    yb = int(3 + s)
    for x in range(-R, R + 1):
        for z in range(-2, 3):
            if math.hypot(x, z) > R:
                continue
            w.setze(x, yb, z, w.b("gray_concrete") if abs(z) < 2 else w.b(WEISS))
        for z in (-2, 2):
            w.setze(x, yb + 1, z, w.b("glass_pane"))
        if x % 4 == 0:
            w.setze(x, yb - 1, 0, w.b("sea_lantern"))
    Hp = int(10 * s + 8)
    for px in (-rw // 2, rw // 2):
        for y in range(-2, yb + Hp):
            w.setze(px, y, 0, w.b(WEISS))
        for t in range(1, int(rw * 0.45)):
            for sx in (-1, 1):
                yy = yb + Hp - 1 - int(t * (Hp - 2) / (rw * 0.45))
                for z in (-2, 2):
                    w.setze(px + sx * t, yy, z, w.b("chain", axis="y", waterlogged=False), False)
        ht = int(4 + 2 * s)
        for y in range(yb + Hp, yb + Hp + ht):
            a = y * 0.6
            for k in range(3):
                b = a + k * 2.09
                w.setze(px + round(math.cos(b) * 1.6), y, round(math.sin(b) * 1.6), w.b("smooth_quartz"))
            w.setze(px, y, 0, w.b("iron_block"))
        w.setze(px, yb + Hp + ht, 0, w.b("end_rod", facing="up"))
    return w


def ringhabitat(seed, g=2):
    """Ringhabitat: auf einem Platz steht aufrecht ein riesiger Ring wie eine Raumstation – mit umlaufendem Fenster-
    band, Speichen zur leuchtenden Nabe und Andockmodulen – auf einem schräg aufragenden Träger."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wiese(w, R, huegel=0.1)
    boden(w, int(R * 0.85))
    Rr = 5 * s + 4
    rr = 1.0 + 0.5 * s
    yc = Rr + rr + 3
    Sk = Skulptur(w, 1.0)
    Sk.mat("w", lambda x, y, z, lx, ly, lz: w.b("light_blue_stained_glass") if abs(lz) < 0.6 else w.b(WEISS))
    Sk.mat("g", w.b("light_gray_concrete"))
    Sk.mat("n", w.b("sea_lantern"))
    Sk.plus(torus(0, 0, 0, Rr, rr, achse="z"), "w")
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.4
        Sk.plus(kap((0, 0, 0), (math.cos(a) * Rr, math.sin(a) * Rr, 0), 0.45), "g")
    Sk.plus(ell(0, 0, 0, 1.6 + 0.4 * s, 1.6 + 0.4 * s, 1.2 + 0.4 * s), "n")
    Sk.plus(kap((0, 0, 0), (0, 0, 2.5 + s), 0.7), "g")
    Sk.rendern((-Rr - 3, -Rr - 3, -3 - s), (Rr + 3, Rr + 3, 3 + s), versatz=(0.5, yc, 0.5))
    for y in range(1, int(yc - Rr - rr) + 1):
        for x in (-1, 0, 1):
            w.setze(x, y, 0, w.b(WEISS))
    for x in range(-3, 4):
        for z in range(-2, 3):
            w.setze(x, 1, z, w.b("light_gray_concrete"))
    return w


def kapselturm(seed, g=2):
    """Kapselturm: um einen schlanken Kern stapeln sich dutzende abgerundete Wohnkapseln mit runden Fenstern, in alle
    Richtungen auskragend, oben ein Dachgarten mit Antennen."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    boden(w, int(R * 0.7))
    H = int(12 * s + 10)
    for y in range(1, H + 1):
        for x in (-1, 0, 1):
            for z in (-1, 0, 1):
                w.setze(x, y, z, w.b("light_gray_concrete") if y % 3 else w.b("gray_concrete"))
    rng = w.rng
    farben = [WEISS, WEISS, "light_gray_concrete", "orange_concrete", "cyan_concrete"]
    for y0 in range(2, H - 2, 3):
        for k in range(4):
            if rng.random() < 0.25:
                continue
            a = k * math.pi / 2 + (y0 % 2) * math.pi / 4
            dx, dz = round(math.cos(a)), round(math.sin(a))
            L = int(3 + rng.random() * 2 * s)
            f = farben[int(rng.integers(len(farben)))]
            for t in range(2, 2 + L):
                for q in (-1, 0, 1):
                    for y in (y0, y0 + 1):
                        x, z = dx * t + (-dz) * q, dz * t + dx * q
                        rund = (t == 1 + L) and abs(q) == 1
                        if rund:
                            continue
                        w.setze(x, y, z, w.b("light_blue_stained_glass") if (t == 1 + L and q == 0 and y == y0 + 1)
                                else w.b(f))
    scheibe(w, 0, H + 1, 0, 3, w.b("moss_block"), rand=w.b(WEISS))
    laubball(w, 1, H + 3, 1, 1.5, arten=("azalea_leaves", "flowering_azalea_leaves"))
    mast(w, -2, -2, int(3 + s), y0=H + 2)
    return w


def recyclingzentrum(seed, g=2):
    """Recyclingzentrum: eine helle Werkshalle mit Solardach, davor farbige Sortiercontainer, Förderbänder, Trichter
    und ein Filterschornstein mit Leuchtringen."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wiese(w, R, huegel=0.1)
    boden(w, int(R * 0.85))
    A, B = int(5 * s + 4), int(3 * s + 4)
    H = int(3 * s + 5)
    zh = -int(R * 0.3)
    for x in range(-A, A + 1):
        for z in range(zh - B, zh + B + 1):
            if abs(x) == A or abs(z - zh) == B:
                for y in range(1, H + 1):
                    w.setze(x, y, z, w.b("light_blue_stained_glass") if y == H - 1 and x % 3 else w.b(WEISS))
            w.setze(x, H + 1, z, w.b("daylight_detector", inverted=False, power=0) if (x + z) % 2 else
                    w.b("light_gray_concrete"))
    for y in range(1, 4):
        for x in (-1, 0, 1):
            w.bloecke.pop((x, y, zh + B), None)
    farben = ["green_concrete", "blue_concrete", "yellow_concrete", "gray_concrete", "brown_concrete"]
    for k in range(int(3 + s)):
        x0 = -A + k * 4
        for x in range(x0, x0 + 3):
            for z in range(zh + B + 3, zh + B + 6):
                for y in range(1, 3):
                    w.setze(x, y, z, w.b(farben[k % 5]))
        w.setze(x0 + 1, 3, zh + B + 4, w.b("hopper", facing="down", enabled=True))
    for z in range(zh + B + 1, int(R * 0.7)):
        w.setze(A - 2, 1, z, w.b("black_concrete"))
        w.setze(A - 2, 2, z, w.b("gray_concrete")) if z % 3 == 0 else None
    sx, sz = A + 2, zh
    for y in range(1, int(12 * s + 6)):
        for dx, dz in ((0, 0), (1, 0), (0, 1), (1, 1)):
            w.setze(sx + dx, y, sz + dz, w.b("sea_lantern") if y % 5 == 0 else w.b("light_gray_concrete"))
    return w


def hoverball_arena(seed, g=2):
    """Hoverball-Arena: ein ovales Stadion mit gläserner Bande, hellblauem Spielfeld mit Leuchtlinien, an beiden
    Enden schwebende Torringe, darüber leuchtende Anzeigetafeln, ringsum weiße Ränge."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    wiese(w, R, huegel=0.1)
    rx, rz = R * 0.55, R * 0.35
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            e = (x / rx) ** 2 + (z / rz) ** 2
            if e <= 1:
                w.setze(x, 0, z, w.b("sea_lantern") if x == 0 or abs(e - 0.3) < 0.04 else w.b("light_blue_concrete"))
                w.bloecke.pop((x, 1, z), None)
    n = int((rx + rz) * 6)
    for k in range(n):
        a = k / n * 2 * math.pi
        x, z = round(math.cos(a) * (rx + 0.5)), round(math.sin(a) * (rz + 0.5))
        w.setze(x, 1, z, w.b(WEISS))
        w.setze(x, 2, z, w.b("glass"))
        for t in range(int(2 + 1.5 * s)):
            xx, zz = round(math.cos(a) * (rx + 1.5 + t)), round(math.sin(a) * (rz + 1.5 + t))
            for y in range(1, t + 3):
                w.setze(xx, y, zz, w.b(WEISS) if y < t + 2 else w.b("quartz_stairs", facing="north", half="bottom",
                                                                      shape="straight", waterlogged=False)
                        if False else w.b("smooth_quartz_slab", type="bottom", waterlogged=False) if y == t + 2
                        else w.b(WEISS))
    yr = int(5 + 2 * s)
    for sx in (-1, 1):
        Sk = Skulptur(w, 1.0)
        Sk.mat("r", w.b("orange_concrete") if sx < 0 else w.b("purple_concrete"))
        Sk.plus(torus(0, 0, 0, 1.6 + 0.6 * s, 0.4, achse="x"), "r")
        Sk.rendern((-1, -4, -4), (1, 4, 4), versatz=(sx * (rx - 3) + 0.5, yr, 0.5))
        for y in range(1, int(yr - 2 - 0.6 * s)):
            w.setze(int(sx * (rx - 3)), y, 0, w.b("end_rod", facing="up"))
    for sz in (-1, 1):
        z = sz * round(rz + 4 + 1.5 * s)
        for x in range(-3, 4):
            for y in range(int(4 + 1.5 * s), int(7 + 1.5 * s)):
                w.setze(x, y, z, w.b("black_concrete") if abs(x) < 3 and int(4 + 1.5 * s) < y < int(6 + 1.5 * s)
                        else w.b("light_gray_concrete"))
        w.setze(-1, int(5 + 1.5 * s), z, w.b("orange_concrete"))
        w.setze(1, int(5 + 1.5 * s), z, w.b("purple_concrete"))
    return w


def kaskadenturm(seed, g=2):
    """Kaskadenturm: ein terrassiertes Hochhaus, über dessen begrünte Stufen Wasserfälle in ein Becken am Fuß
    hinabstürzen; jede Terrasse mit Bäumen und Glasfront."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.1)
    n = int(3 + s)
    A0 = int(R * 0.6)
    y = 1
    for k in range(n):
        A = A0 - k * int(1.5 + s)
        h = int(4 + s)
        for x in range(-A, A + 1):
            for z in range(-A, A + 1):
                for yy in range(y, y + h):
                    if max(abs(x), abs(z)) == A:
                        w.setze(x, yy, z, w.b("light_blue_stained_glass") if (yy - y) % 4 else w.b(WEISS))
                w.setze(x, y + h, z, w.b("grass_block", snowy=False) if max(abs(x), abs(z)) > A - int(1.5 + s)
                        else w.b(WEISS))
        if k:
            for dz in (-1, 0, 1):
                w.setze(A + int(1.5 + s) - 1, y, dz, w.b("water", level=0)) if False else None
        for x in range(-1, 2):
            w.setze(x, y + h, A, w.b("water", level=0))
            w.setze(x, y + h, A - 1, w.b("water", level=0))
        if k < n - 1 and A > 4:
            baum(w, -A + 1, y + h + 1, -A + 1, seed + k, 4 + s)
        y += h
    for x in range(-2, 3):
        for z in range(A0 + 1, A0 + 4):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("light_blue_concrete"))
    return w


def aussichtsnadel(seed, g=2):
    """Aussichtsnadel: ein extrem schlanker Turm, der hoch oben eine flache, untertassenförmige Aussichtskanzel mit
    umlaufendem Glasband trägt, darüber eine leuchtende Antennenspitze; unten eine gläserne Eingangshalle."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    wiese(w, R, huegel=0.1)
    boden(w, int(R * 0.7))
    H = int(18 * s + 12)
    for y in range(1, H):
        for x in range(-1, 2):
            for z in range(-1, 2):
                if abs(x) + abs(z) < 2:
                    w.setze(x, y, z, w.b(WEISS) if y % 6 else w.b("sea_lantern"))
    rs = 3 + 2 * s
    for dy in range(-2, 3):
        r = rs * math.sqrt(max(0, 1 - (dy / 2.6) ** 2))
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(x, z)
                if d <= r:
                    w.setze(x, H + dy, z, w.b("light_blue_stained_glass") if dy == 0 and d > r - 1 else
                            w.b(WEISS) if d > r - 1 or abs(dy) == 2 else w.b("light_gray_concrete"))
    for y in range(H + 3, H + int(5 + 3 * s)):
        w.setze(0, y, 0, w.b("iron_block") if y < H + 5 else w.b("lightning_rod", facing="up", powered=False,
                                                                   waterlogged=False))
    w.setze(0, H + int(5 + 3 * s), 0, w.b("redstone_lamp", lit=True))
    glaskuppel(w, 0, 0, 1, 3 + s, rahmen=WEISS, glas="glass")
    return w


def solarblumen(seed, g=2):
    """Solarblumen-Platz: auf einem Platz recken sich riesige Blumen-Skulpturen mit weißen Stielen und schräg
    gestellten Blütenblättern aus Solarzellen und blauem Glas der Sonne entgegen, dazwischen Wasserspiele."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.1)
    boden(w, int(R * 0.85))
    n = int(3 + s)
    for k in range(n):
        a = k / n * 2 * math.pi + 0.3
        cx, cz = round(math.cos(a) * R * 0.45), round(math.sin(a) * R * 0.45)
        if k == 0:
            cx, cz = 0, 0
        Hs = int((5 + (k % 3) * 2) * s + 4)
        for y in range(1, Hs):
            w.setze(cx, y, cz, w.b(WEISS))
        rb = 2 + 1.2 * s
        for x in range(int(cx - rb) - 1, int(cx + rb) + 2):
            for z in range(int(cz - rb) - 1, int(cz + rb) + 2):
                d = math.hypot(x - cx, z - cz)
                if d <= rb:
                    b = math.atan2(z - cz, x - cx)
                    blatt = abs(math.sin(b * 3)) > 0.35
                    if d < 1.2:
                        w.setze(x, Hs, z, w.b("yellow_concrete"))
                    elif blatt:
                        w.setze(x, Hs + int(d * 0.5), z, w.b("daylight_detector", inverted=False, power=0)
                                if (x + z) % 2 else w.b("blue_stained_glass"))
    for k in range(6):
        a = k / 6 * 2 * math.pi
        x, z = round(math.cos(a) * R * 0.25), round(math.sin(a) * R * 0.25)
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("sea_lantern"))
    return w


def robotikwerkstatt(seed, g=2):
    """Robotik-Werkstatt: eine offene Halle mit großen Glasfronten, in der Roboter an Ladeplätzen stehen, ein
    mehrgliedriger Industriearm über einer Werkbank arbeitet und Ersatzteile in Regalen lagern."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    wiese(w, R, huegel=0.1)
    boden(w, int(R * 0.85))
    A, B = int(5 * s + 4), int(3 * s + 4)
    H = int(3 * s + 5)
    for x in range(-A, A + 1):
        for z in range(-B, B + 1):
            rand = abs(x) == A or abs(z) == B
            if rand and z != B:
                for y in range(1, H + 1):
                    w.setze(x, y, z, w.b(WEISS) if abs(x) == A and abs(z) == B or y == H else w.b("glass"))
            if z == B and abs(x) == A:
                for y in range(1, H + 1):
                    w.setze(x, y, z, w.b(WEISS))
    for x in range(-A, A + 1):
        for z in range(-B, int(B * 0.2)):
            w.setze(x, H + 1, z, w.b("light_gray_concrete") if (x + z) % 3 else w.b("glass"))
    for k in range(int(2 + s)):
        x = -A + 2 + k * 3
        w.setze(x, 0, -B + 2, w.b("cyan_concrete"))
        figur(w, 0.45 * s + 0.35, roboter(w, ["light_gray_concrete", "orange_concrete", WEISS][k % 3]),
              (-2, -1, -1), (2, 6, 1), pos=(x, 1, -B + 2), winkel=-math.pi / 2)
    bx = int(A * 0.4)
    for x in range(bx - 2, bx + 3):
        w.setze(x, 1, 0, w.b("iron_block"))
    w.setze(bx, 2, 0, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    pts = [(bx + 3, 1, -2), (bx + 3, 4 + s, -2), (bx + 1, 5 + s, 0), (bx, 3, 0)]
    for a, b in zip(pts, pts[1:]):
        zylinder(w, a, b, 0.6, w.b("orange_concrete"))
    for p in pts[1:3]:
        kugel(w, p[0], p[1], p[2], 0.9, w.b("gray_concrete"))
    for z in range(-B + 1, B - 1, 2):
        for y in range(1, H - 1):
            w.setze(A - 1, y, z, w.b("chiseled_bookshelf", facing="west", slot_0_occupied=False,
                                     slot_1_occupied=False, slot_2_occupied=False, slot_3_occupied=False,
                                     slot_4_occupied=False, slot_5_occupied=False) if False else
                    w.b("iron_block") if y % 2 else w.b("light_gray_concrete"))
    return w


def terrassenpyramide(seed, g=2):
    """Terrassenpyramide: ein gestufter Wohnberg aus weißen Geschossen mit Glasfronten, jede Stufe ein grüner
    Dachgarten mit Bäumen und Hecken, oben ein gläsernes Atrium."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    wiese(w, R, huegel=0.1)
    n = int(3 + 1.5 * s)
    A0 = int(R * 0.72)
    y = 1
    rng = w.rng
    for k in range(n):
        A = A0 - k * 2
        if A < 3:
            break
        for x in range(-A, A + 1):
            for z in range(-A, A + 1):
                rand = max(abs(x), abs(z)) == A
                for yy in range(y, y + 3):
                    if rand:
                        w.setze(x, yy, z, w.b(WEISS) if (abs(x) == A and abs(z) == A) or yy == y + 2 else
                                w.b("light_blue_stained_glass"))
                rr = max(abs(x), abs(z))
                w.setze(x, y + 3, z, w.b("grass_block", snowy=False) if rr > A - 2 else w.b(WEISS))
                if rr == A - 1 and rng.random() < 0.3:
                    w.setze(x, y + 4, z, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False))
                elif rr == A and (x + z) % 2 == 0:
                    w.setze(x, y + 4, z, w.b("glass_pane"))
        y += 3
    glaskuppel(w, 0, 0, y + 1, 2.5 + s, rahmen=WEISS, glas="glass")
    return w


def luftschiffterminal(seed, g=2):
    """Luftschiff-Terminal: ein schlanker Ankermast mit gläsernem Steg, an dem ein weißes Luftschiff mit cyan-
    farbenen Flossen und Gondel festgemacht ist; unten das Terminal mit Glasfront."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    wiese(w, R, huegel=0.1)
    boden(w, int(R * 0.8))
    H = int(10 * s + 8)
    mx = -int(R * 0.6)
    for y in range(1, H + 2):
        for x in (mx - 1, mx, mx + 1):
            if x == mx or y % 4 == 0:
                w.setze(x, y, 0, w.b(WEISS) if x == mx else w.b("iron_bars", north=False, south=False, east=True,
                                                                     west=True, waterlogged=False))
    scheibe(w, mx, H + 2, 0, 2, w.b("light_gray_concrete"), rand=w.b(WEISS))
    L = int(R * 1.1)
    Rh = 2.5 + 1.5 * s
    cx = mx + 2 + L // 2
    huelle(w, cx, H + 2, 0, L, Rh, lambda x, y, z: w.b(WEISS) if (x // 3) % 4 else w.b("light_gray_concrete"))
    for k, (dy, dz) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
        for t in range(int(2 + s)):
            for q in range(int(3 + s) - t):
                w.setze(cx + L // 2 - 2 - q, H + 2 + dy * (round(Rh * 0.7) + t), dz * (round(Rh * 0.7) + t),
                        w.b("cyan_concrete"), False)
    yg = H + 2 - round(Rh) - 1
    for x in range(cx - 3, cx + 4):
        for z in (-1, 0, 1):
            w.setze(x, yg, z, w.b("light_blue_stained_glass") if abs(z) == 1 else w.b(WEISS))
    A = int(4 + 2 * s)
    tz = int(R * 0.45)
    for x in range(-A, A + 1):
        for z in range(tz - 3, tz + 4):
            for y in range(1, 5):
                if abs(x) == A or abs(z - tz) == 3:
                    w.setze(x, y, z, w.b("glass") if y < 4 and abs(x) < A else w.b(WEISS))
            w.setze(x, 5, z, w.b(WEISS))
    return w


def saatgutbunker(seed, g=2):
    """Saatgutbunker: aus einem verschneiten Hang ragt keilförmig ein Betonportal mit leuchtendem Lichtband über
    dem Eingang, Stahltor, Lüftungsschächten oben und einem gefrorenen Vorplatz."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    rn = Rauschen(w, 5)
    H = int(9 * s + 6)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            h = int(max(0, min(H, (-z + R * 0.1) * 0.9)) + rn(x, 3, z) * 2)
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("snow_block") if y == h else w.b("stone"))
            if h <= 1:
                w.setze(x, h, z, w.b("packed_ice") if rn(x, 7, z) < 0.3 else w.b("snow_block"))
    B = int(2 + s)
    L = int(6 + 3 * s)
    Hp = int(4 + 2 * s)
    for z in range(-L, 3):
        t = (z + L) / (L + 3)
        hz = int(Hp * (0.4 + 0.6 * t))
        for x in range(-B - 1, B + 2):
            for y in range(0, hz + 1):
                aussen = abs(x) == B + 1 or y == hz
                if aussen:
                    w.setze(x, y, z, w.b("gray_concrete") if (x + y) % 5 else w.b("light_gray_concrete"))
                else:
                    w.bloecke.pop((x, y, z), None)
    for x in range(-B, B + 1):
        w.setze(x, Hp, 3, w.b("light_blue_stained_glass") if x % 2 else w.b("sea_lantern"))
        for y in range(1, Hp - 1):
            w.setze(x, y, 1, w.b("iron_block") if (x + y) % 3 else w.b("light_gray_concrete"))
    for x in range(-B - 3, B + 4):
        for z in range(4, int(R * 0.6)):
            if math.hypot(x, z) < R:
                w.setze(x, 0, z, w.b("smooth_stone") if (x + z) % 4 else w.b("packed_ice"))
    for k in range(3):
        x, z = -4 + k * 4, -L - 2
        y = hoehe(w, x, z, H + 4)
        for d in range(1, 3):
            w.setze(x, y + d, z, w.b("iron_block"))
        w.setze(x, y + 3, z, w.b("iron_trapdoor", facing="north", half="top", open=False, powered=False,
                                 waterlogged=False))
    return w


def roehrenbahn(seed, g=2):
    """Röhrenbahn: eine durchsichtige Röhre schwingt sich auf schlanken Stützen in einer weiten Kurve über die Land-
    schaft, darin eine stromlinienförmige Kapsel; an beiden Enden gläserne Stationen."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    wiese(w, R, huegel=0.2)
    y = int(5 + 2 * s)
    pts = bez((-R * 0.75, y, R * 0.3), (0, y + 2, -R * 1.0), (R * 0.75, y, R * 0.3))
    rr = 1.4 + 0.3 * s
    for (a, b) in zip(pts[::3], pts[3::3]):
        zylinder(w, a[:3], b[:3], rr, w.b("glass"), hohl=True, nieten=w.b(WEISS), abstand=4)
    for i, p in enumerate(pts[::9]):
        x, yy, z = round(p[0]), round(p[1]), round(p[2])
        for h in range(1, int(yy - rr)):
            w.setze(x, h, z, w.b(WEISS))
    mid = pts[len(pts) // 2]
    zylinder(w, (mid[0] - 2.5, mid[1], mid[2]), (mid[0] + 2.5, mid[1], mid[2]), max(0.6, rr - 0.9),
             w.b("cyan_concrete"))
    for p in (pts[0], pts[-1]):
        cx, cz = round(p[0]), round(p[2])
        for x in range(cx - 3, cx + 4):
            for z in range(cz - 3, cz + 4):
                w.setze(x, 0, z, w.b("smooth_stone"))
                if max(abs(x - cx), abs(z - cz)) == 3:
                    for yy in range(1, y + 3):
                        w.setze(x, yy, z, w.b(WEISS) if (abs(x - cx) == 3 and abs(z - cz) == 3) or yy % 4 == 0
                                else w.b("light_blue_stained_glass"))
                w.setze(x, y + 3, z, w.b(WEISS))
    return w


ZUKUNFT3 = {
    "stelzenkuppel": ("Stelzen-Kuppelhäuser", stelzenkuppel),
    "ladestation": ("Energie-Ladestation", ladestation),
    "drohnenhafen": ("Drohnenhafen", drohnenhafen),
    "meereslabor": ("Meereskuppel-Labor", meereslabor),
    "algenturm": ("Algenreaktor-Turm", algenturm),
    "schwebekugelbrunnen": ("Schwebekugel-Brunnen", schwebekugelbrunnen),
    "leuchtbaumallee": ("Leuchtbaum-Allee", leuchtbaumallee),
    "turbinenbruecke": ("Turbinenbrücke", turbinenbruecke),
    "ringhabitat": ("Ringhabitat", ringhabitat),
    "kapselturm": ("Kapselturm", kapselturm),
    "recyclingzentrum": ("Recyclingzentrum", recyclingzentrum),
    "hoverball_arena": ("Hoverball-Arena", hoverball_arena),
    "kaskadenturm": ("Kaskadenturm", kaskadenturm),
    "aussichtsnadel": ("Aussichtsnadel", aussichtsnadel),
    "solarblumen": ("Solarblumen-Platz", solarblumen),
    "robotikwerkstatt": ("Robotik-Werkstatt", robotikwerkstatt),
    "terrassenpyramide": ("Terrassenpyramide", terrassenpyramide),
    "luftschiffterminal": ("Luftschiff-Terminal", luftschiffterminal),
    "saatgutbunker": ("Saatgutbunker", saatgutbunker),
    "roehrenbahn": ("Röhrenbahn", roehrenbahn),
}

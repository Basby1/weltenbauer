"""Riesenblumen & Zauberwiesen II – zwanzig weitere Riesenblumen: Orchidee, Krokusse im Schnee, Narzissen, Kornblume,
Akelei, Calla, Passionsblume, Distel, Löwenmäulchen, Vergissmeinnicht-Polster, Dahlie, Pfingstrose, Kamillenwiese,
Enzian, Edelweiß, Schneeglöckchen, Glyzinienbogen, Kaktusblüte, Magnolienbaum und Blumenuhr. Fuß auf y = 1."""

from __future__ import annotations

import math

from blumen import blaetter_am_stiel, bluete, kugel, stiel
from erw_basis import BLUMEN, M, S, wiese
from flora import _neu, blatt, bogen, linie
from leuchtwald2 import baum_aeste, laubball
from lib import Rauschen

GRUEN = ["green_terracotta", "lime_terracotta", "green_concrete"]


def wiese_klein(w, s, R=None, art="wiese", blumen=0.04):
    R = R or int(5 * s + 4)
    return wiese(w, R, huegel=0.1, art=art, blumen=blumen)


def grasblaetter(w, x, z, n, L, rng, farben=None):
    for k in range(n):
        a = k / n * 2 * math.pi + rng.random()
        blatt(w, (x, 1, z), a, L * (0.7 + rng.random() * 0.5), max(0.5, L * 0.08), steig=1.6, haeng=0.5,
              farben=farben or GRUEN, mitte="lime_terracotta", form="lanze", kipp=0.1)


# ============================================================================ Blumen

def orchidee(seed, g=1):
    """Riesenorchidee: ein überhängender Rispenstängel mit mehreren großen Blüten aus weißen Kelchblättern und einer
    magenta gezeichneten Lippe, darunter breite, glänzende Blätter."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    wiese_klein(w, s)
    H = int(10 * s + 4)
    pts = bogen(w, (0, 1, 0), (7 * s, H, 0), H * 0.3, w.b("green_terracotta"), 0.0, n=14)
    for k, idx in enumerate((7, 10, 13)):
        px, py, pz = pts[min(idx, len(pts) - 1)]
        c = (px, py - 1.5 * s, pz + (k - 1) * 1.6 * s)
        L = (1.6 + 0.3 * k) * s + 0.8
        bluete(w, c, (0, 0.3, 1), 5, L, L * 0.5, cup=-0.2, farben=["white_concrete", "white_wool", "pink_wool"],
               innen="yellow_concrete")
        bluete(w, (c[0], c[1] - L * 0.4, c[2] + 0.5), (0, -0.4, 1), 1, L * 0.8, L * 0.45, cup=0.8,
               farben=["magenta_concrete", "purple_wool"], dreh=-math.pi / 2)
    for k in range(3):
        blatt(w, (0, 1, 0), k * 2.1, (4 + rng.random()) * s, 1.4 * s, steig=0.2, haeng=0.6,
              farben=["green_concrete", "green_terracotta"], mitte="lime_concrete", form="paddel", kipp=0.1)
    return w


def krokusse(seed, g=1):
    """Krokusse im Schnee: auf einer schmelzenden Schneedecke öffnen sich riesige Krokuskelche in Violett, Weiß und
    Gelb mit orangen Narben, umgeben von schmalen, gestreiften Blättern."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    zellen = wiese_klein(w, s, blumen=0.0)
    rn = Rauschen(w, 3)
    for (x, z), h in zellen.items():
        if rn(x, 0, z) < 0.55:
            w.setze(x, h + 1, z, w.b("snow", layers=1 + int(rn(x, 2, z) * 2)))
    farben = [["purple_concrete", "purple_wool", "magenta_wool"], ["white_concrete", "white_wool", "light_gray_wool"],
              ["yellow_concrete", "yellow_wool", "orange_wool"]]
    n = int(4 + 2 * s)
    for k in range(n):
        a = k / n * 2 * math.pi + 0.3
        r = 0 if k == 0 else (2 + rng.random() * 2) * s
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        H = int((3 + rng.random() * 2) * s + 2)
        linie(w, (x, 1, z), (x, H, z), w.b("white_terracotta"))
        L = 1.6 * s + 0.6
        bluete(w, (x, H + 1, z), (0, 1, 0), 6, L, L * 0.45, cup=2.2 / (s + 0.4), farben=farben[k % 3],
               innen="yellow_wool", form="spitz")
        w.setze(x, H + 1 + round(L * 0.6), z, w.b("orange_concrete"))
        grasblaetter(w, x, z, 3, 2.5 * s, rng, ["green_concrete", "white_terracotta"])
    return w


def narzissen(seed, g=1):
    """Narzissen: drei hohe Osterglocken, deren seitlich geneigte Blüten aus sechs blassgelben Blütenblättern und
    einer tiefgelben, gekrausten Trompete bestehen, dazu lange, blaugrüne Blätter."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    wiese_klein(w, s)
    for i in range(3):
        a = i * 2.1 + 0.5
        d = 2.5 * s * (i > 0)
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        H = int((10 - 2 * i) * s + 4)
        linie(w, (x0, 1, z0), (x0, H, z0), w.b("lime_terracotta"))
        n = (math.cos(a + 1.2), -0.2, math.sin(a + 1.2))
        c = (x0 + n[0] * 1.2, H, z0 + n[2] * 1.2)
        L = 2.4 * s + 0.8
        bluete(w, c, n, 6, L, L * 0.45, cup=-0.1, farben=["yellow_wool", "white_wool", "yellow_concrete"],
               form="spitz")
        for t in range(int(1.6 * s + 2)):
            r = 0.8 * s + 0.4 + t * 0.1
            cc = (c[0] + n[0] * t, c[1] + n[1] * t, c[2] + n[2] * t)
            for k in range(int(r * 7) + 4):
                b = k / (r * 7 + 4) * 2 * math.pi
                e1 = (-n[2], 0, n[0])
                p = (cc[0] + e1[0] * math.cos(b) * r, cc[1] + math.sin(b) * r, cc[2] + e1[2] * math.cos(b) * r)
                w.setze(round(p[0]), round(p[1]), round(p[2]), w.b("orange_concrete") if t == int(1.6 * s + 1)
                        else w.b("yellow_concrete"))
        for k in range(2):
            blatt(w, (x0, 1, z0), a + k * 3.1, (5 + rng.random()) * s, 0.9 * s, steig=1.4, haeng=0.8,
                  farben=["green_terracotta", "cyan_terracotta"], mitte="lime_terracotta", form="lanze", kipp=0.2)
    return w


def kornblume(seed, g=1):
    """Kornblume: auf drahtigen, verzweigten Stängeln sitzen große, leuchtend blaue Blütenköpfe aus gefransten
    Trichterblüten mit dunkelviolettem Herz, zwischen Weizenhalmen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    zellen = wiese_klein(w, s, blumen=0.0)
    for (x, z), h in zellen.items():
        if rng.random() < 0.25:
            w.setze(x, h + 1, z, w.b("wheat", age=7)) if False else w.b("grass")
    for i in range(int(2 + s)):
        a = i * 2.4
        d = 2.5 * s * (i > 0)
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        H = int((9 - 1.5 * i) * s + 4)
        linie(w, (x0, 1, z0), (x0, H, z0), w.b("light_gray_terracotta"))
        for j in range(2):
            b = a + j * 2.5
            top = (x0 + math.cos(b) * 2 * s, H - 2 * s * (j + 1) * 0.6, z0 + math.sin(b) * 2 * s)
            linie(w, (x0, H * 0.6, z0), top, w.b("light_gray_terracotta"))
            bluete(w, (top[0], top[1] + 0.5, top[2]), (0, 1, 0), 9, 1.2 * s + 0.6, 0.6 * s + 0.3, cup=0.5,
                   farben=["blue_concrete", "light_blue_concrete", "blue_wool"], innen="purple_concrete",
                   kraeusel=0.8)
        bluete(w, (x0, H + 1, z0), (0, 1, 0), 10, 2.0 * s + 0.8, 0.9 * s + 0.4, cup=0.6,
               farben=["blue_concrete", "light_blue_concrete", "blue_wool"], innen="purple_concrete", kraeusel=0.9)
    return w


def akelei(seed, g=1):
    """Akelei: nickende, glockige Blüten mit fünf langen, nach hinten geschwungenen Spornen in Violett und Weiß,
    an einem fein verzweigten Stängel über dreiteiligen, blaugrünen Blättern."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    wiese_klein(w, s)
    H = int(11 * s + 4)
    pts = bogen(w, (0, 1, 0), (2 * s, H, 0), H * 0.1, w.b("green_terracotta"), 0.0, n=12)
    for k in range(3):
        a = k * 2.1
        top = (math.cos(a) * 3 * s, H - k * 1.5 * s, math.sin(a) * 3 * s)
        linie(w, (pts[-3][0], pts[-3][1], pts[-3][2]), top, w.b("green_terracotta"))
        L = 1.8 * s + 0.6
        c = (top[0], top[1] - 1, top[2])
        bluete(w, c, (0, -1, 0), 5, L, L * 0.5, cup=1.2, farben=["purple_concrete", "purple_wool"],
               innen="white_wool", rand="white_concrete")
        for j in range(5):
            b = j / 5 * 2 * math.pi
            linie(w, c, (c[0] + math.cos(b) * L * 0.5, c[1] + L * 1.1, c[2] + math.sin(b) * L * 0.5),
                  w.b("magenta_concrete"))
    blaetter_am_stiel(w, s, rng, 3, 0.12, 3.0, farben=["cyan_terracotta", "green_terracotta"], form="herz")
    return w


def calla(seed, g=1):
    """Calla: elegante, trichterförmig eingerollte weiße Hochblätter mit gelbem Kolben auf hohen, glatten Stielen,
    darunter große, pfeilförmige Blätter mit weißen Sprenkeln."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    wiese_klein(w, s)
    for i in range(3):
        a = i * 2.1 + 0.4
        d = 2.2 * s * (i > 0)
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        H = int((10 - 2 * i) * s + 4)
        linie(w, (x0, 1, z0), (x0, H, z0), w.b("lime_terracotta"))
        n = (math.cos(a) * 0.4, 1, math.sin(a) * 0.4)
        L = 3.0 * s + 1
        for t in range(int(L * 1.4)):
            r = 0.3 + t * 0.35
            for k in range(int(r * 6) + 4):
                b = k / (r * 6 + 4) * 2 * math.pi
                if math.cos(b) > 0.7 and t > L * 0.6:
                    continue
                w.setze(round(x0 + math.cos(b) * r + n[0] * t), round(H + t), round(z0 + math.sin(b) * r + n[2] * t),
                        w.b("white_concrete") if t > 1 else w.b("lime_concrete"))
        linie(w, (x0, H, z0), (x0 + n[0] * L * 0.7, H + L * 0.7, z0 + n[2] * L * 0.7), w.b("yellow_concrete"))
        blatt(w, (x0, 1, z0), a + 2.5, (4 + rng.random()) * s, 1.8 * s, steig=0.8, haeng=0.8,
              farben=["green_concrete", "green_terracotta"], mitte="lime_concrete", form="herz", kipp=0.15)
    return w


def passionsblume(seed, g=1):
    """Passionsblume: eine kletternde Ranke an einem Holzrahmen trägt große, flache Blüten mit zehn weißen
    Blütenblättern, einem Strahlenkranz in Violett, Weiß und Blau und einem grünen Narbenkreuz."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    wiese_klein(w, s)
    H = int(9 * s + 5)
    B = int(3 + 2 * s)
    for sx in (-B, B):
        for y in range(1, H + 1):
            w.setze(sx, y, 0, w.b("spruce_fence"))
    for x in range(-B, B + 1):
        w.setze(x, H + 1, 0, w.b("spruce_planks"))
    for k in range(int(30 * s)):
        x = round((rng.random() - 0.5) * 2 * B)
        y = 1 + round(rng.random() * H)
        w.setze(x, y, 0, w.b("oak_leaves", persistent=True, distance=1, waterlogged=False), False)
    for k in range(int(1 + s)):
        c = (-B * 0.5 + k * B, H * 0.6 + (k % 2) * 2, 1.5)
        L = 2.2 * s + 1
        bluete(w, c, (0, 0, 1), 10, L, L * 0.25, cup=0.0, farben=["white_concrete", "white_wool"])
        for r, f in ((L * 0.7, "purple_concrete"), (L * 0.55, "white_wool"), (L * 0.4, "blue_concrete")):
            for j in range(int(r * 7) + 6):
                b = j / (r * 7 + 6) * 2 * math.pi
                w.setze(round(c[0] + math.cos(b) * r), round(c[1] + math.sin(b) * r), round(c[2] + 1), w.b(f))
        w.setze(round(c[0]), round(c[1]), round(c[2] + 2), w.b("lime_concrete"))
        for dx, dy in ((1, 0), (-1, 0), (0, 1)):
            w.setze(round(c[0]) + dx, round(c[1]) + dy, round(c[2] + 3), w.b("green_concrete"))
    return w


def distel(seed, g=1):
    """Distel: eine stachelige Riesendistel mit silbrig-grünen, gezackten Blättern, auf deren kugeligem, dornig
    beschupptem Köpfchen ein dichter Pinsel violetter Blüten steht; daneben Samen-Wolle."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    wiese_klein(w, s)
    H = int(10 * s + 4)
    stiel(w, (0, H, 0), s, "green_terracotta", 0.4 * s)
    kugel(w, (0, H + 1, 0), 1.3 * s + 0.6, lambda x, y, z: w.b("green_concrete") if (x + y + z) % 2 else
          w.b("lime_terracotta"))
    r = 1.2 * s + 0.6
    for k in range(int(40 * s + 20)):
        a = rng.random() * 2 * math.pi
        el = rng.random() * 0.8
        L = r + 1 + rng.random() * s
        linie(w, (0, H + 1 + r * 0.5, 0), (math.cos(a) * math.sin(el) * L, H + 1 + r * 0.5 + math.cos(el) * L,
                                           math.sin(a) * math.sin(el) * L),
              w.b(["purple_concrete", "magenta_wool", "purple_wool"][k % 3]))
    for k in range(3):
        blatt(w, (0, 1 + k * 2 * s, 0), k * 2.4, (4 + rng.random()) * s, 1.2 * s, steig=0.5, haeng=0.5,
              farben=["light_gray_terracotta", "green_terracotta"], mitte="white_terracotta", form="lanze",
              schlitze=4, kipp=0.2)
    kugel(w, (3 * s, 2, 2 * s), 0.8 * s + 0.4, w.b("white_wool"))
    return w


def loewenmaeulchen(seed, g=1):
    """Löwenmäulchen: drei hohe Blütenähren, an denen dicht übereinander zweilippige Blüten in Pink, Gelb und
    Orange sitzen, zur Spitze hin kleiner werdend, mit schmalen Blättern."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    wiese_klein(w, s)
    farben = [("pink_concrete", "yellow_concrete"), ("yellow_concrete", "orange_concrete"),
              ("red_concrete", "yellow_wool")]
    for i in range(3):
        a = i * 2.1
        d = 2.3 * s * (i > 0)
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        H = int((11 - 2 * i) * s + 4)
        linie(w, (x0, 1, z0), (x0, H, z0), w.b("green_terracotta"))
        f1, f2 = farben[i]
        for y in range(int(H * 0.45), H + 1):
            t = (y - H * 0.45) / (H * 0.55)
            r = (1.6 - t) * (0.6 * s + 0.4)
            for k in range(4):
                b = k * math.pi / 2 + y * 0.8
                bx, bz = x0 + math.cos(b) * r, z0 + math.sin(b) * r
                w.setze(round(bx), y, round(bz), w.b(f1))
                if (y + k) % 2 == 0:
                    w.setze(round(bx + math.cos(b) * 0.8), y - 1, round(bz + math.sin(b) * 0.8), w.b(f2), False)
        for k in range(3):
            blatt(w, (x0, 2 + k * 2, z0), a + k * 2, 2.5 * s, 0.5 * s + 0.3, steig=0.6, haeng=0.4,
                  farben=GRUEN, mitte="lime_terracotta", form="lanze", kipp=0.1)
    return w


def vergissmeinnicht(seed, g=1):
    """Vergissmeinnicht-Polster: ein weiches, kniehohes Kissen aus hunderten großen, himmelblauen Blüten mit gelbem
    Auge, über einen Bachrand und Steine geflossen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    zellen = wiese_klein(w, s, R=int(6 * s + 5), blumen=0.0)
    for (x, z), h in zellen.items():
        if abs(z - math.sin(x / 3) * 1.5 - 3 * s) < 1.2:
            w.setze(x, h, z, w.b("water", level=0))
            w.bloecke.pop((x, h + 1, z), None)
    rn = Rauschen(w, 2.5)
    for (x, z), h in zellen.items():
        if rn(x, 0, z) < 0.6 and w.P.name(w.bloecke.get((x, h, z), 0)) != "water":
            hh = 1 + int(rn(x, 3, z) * (1.5 * s))
            for y in range(h + 1, h + hh):
                w.setze(x, y, z, w.b("green_terracotta"))
            w.setze(x, h + hh, z, w.b("yellow_concrete") if (x * 3 + z * 7) % 9 == 0 else
                    w.b("light_blue_concrete") if (x + z) % 3 else w.b("light_blue_wool"))
    return w


def dahlie(seed, g=1):
    """Dahlie: eine riesige Pompon-Dahlie – eine nahezu perfekte Kugel aus röhrenförmig eingerollten Blütenblättern in
    Pink mit violetten Spitzen – auf einem kräftigen Stiel, dazu kleinere Schwestern."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    wiese_klein(w, s)
    for i in range(int(1 + s)):
        a = i * 2.3
        d = 3 * s * (i > 0)
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        H = int((9 - 2 * i) * s + 4)
        r = (2.2 - 0.4 * i) * s + 0.8
        linie(w, (x0, 1, z0), (x0, H, z0), w.b("green_terracotta"), 0.4 if s > 1.3 else 0)
        f = [("pink_concrete", "magenta_concrete"), ("orange_concrete", "red_concrete"),
             ("white_concrete", "pink_wool")][i % 3]
        kugel(w, (x0, H + r, z0), r, lambda x, y, z: w.b(f[1]) if (x * 3 + y * 5 + z * 7) % 4 == 0 else w.b(f[0]))
    blaetter_am_stiel(w, s, rng, 4, 0.12, 3.5, form="herz")
    return w


def pfingstrose(seed, g=1):
    """Pfingstrose: ein ausladender Busch mit dunkelgrünem, geschlitztem Laub, aus dem riesige, schwere, gefüllte
    Blüten in Rosa und Weiß quellen, manche noch als runde Knospe."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    wiese_klein(w, s)
    laubball(w, 0, 2 + s, 0, 3 + 1.5 * s, arten=("dark_oak_leaves", "oak_leaves"))
    for k in range(int(2 + 2 * s)):
        a = k * 2.4
        r = (1.5 + rng.random() * 2) * s
        c = (math.cos(a) * r, 3 + 2 * s + rng.random() * s, math.sin(a) * r)
        if k == int(1 + 2 * s):
            kugel(w, c, 0.8 * s + 0.4, w.b("lime_terracotta"))
            continue
        for lage in range(3):
            L = (1.8 - lage * 0.4) * s + 0.8
            bluete(w, (c[0], c[1] + lage * 0.4 * s, c[2]), (math.cos(a) * 0.3, 1, math.sin(a) * 0.3), 6 + lage, L,
                   L * 0.7, cup=1.2 + lage * 0.3, farben=["pink_concrete", "pink_wool", "white_wool"], dreh=lage,
                   kraeusel=0.5)
    return w


def kamillenwiese(seed, g=1):
    """Kamillenwiese: ein Feld aus riesigen Kamillenblüten auf unterschiedlich hohen Stängeln – weiße, nach unten
    geklappte Zungenblüten um hoch gewölbte, gelbe Köpfchen – über gefiedertem Laub."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    zellen = wiese_klein(w, s, R=int(6 * s + 5))
    n = int(4 + 4 * s)
    for k in range(n):
        a = rng.random() * 6.28
        r = rng.random() * (5 * s + 3)
        x0, z0 = round(math.cos(a) * r), round(math.sin(a) * r)
        H = int((3 + rng.random() * 5) * s + 2)
        linie(w, (x0, 1, z0), (x0, H, z0), w.b("lime_terracotta"))
        L = (1.0 + rng.random() * 0.6) * s + 0.5
        bluete(w, (x0, H + 1, z0), (0, 1, 0), 12, L, L * 0.2, cup=-0.6, farben=["white_concrete", "white_wool"])
        kugel(w, (x0, H + 1 + L * 0.2, z0), L * 0.4, w.b("yellow_concrete"))
    for (x, z), h in zellen.items():
        if rng.random() < 0.2:
            w.setze(x, h + 1, z, w.b("fern"))
    return w


def enzian(seed, g=1):
    """Enzian: aus einem Polster zwischen Alpenfelsen recken sich tiefblaue, aufrechte Trompetenblüten mit
    grünlich gefleckten Schlund, ringsum Moos, Steinbrech und kleine Schneefelder."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    zellen = wiese_klein(w, s, art="kies", blumen=0.0)
    from leuchtwald2 import kugel as kugel2
    f = M(w, [("stone", 2), ("andesite", 1), ("mossy_cobblestone", 1)])
    for k in range(int(2 + s)):
        a = rng.random() * 6.28
        kugel2(w, math.cos(a) * 4 * s, 0.5, math.sin(a) * 4 * s, 1.2 + s * 0.8, f, ry=1)
    for k in range(int(3 + 2 * s)):
        a = k * 2.4
        r = 0 if k == 0 else (1.5 + rng.random() * 1.5) * s
        x0, z0 = math.cos(a) * r, math.sin(a) * r
        H = int(2 * s + 2)
        linie(w, (x0, 1, z0), (x0, H, z0), w.b("green_terracotta"))
        L = 2.2 * s + 1
        for t in range(int(L * 1.3)):
            rr = 0.4 + t * 0.32
            for j in range(int(rr * 6) + 4):
                b = j / (rr * 6 + 4) * 2 * math.pi
                w.setze(round(x0 + math.cos(b) * rr), H + t, round(z0 + math.sin(b) * rr),
                        w.b("lime_terracotta") if t < 1 else w.b("blue_concrete") if (j + t) % 4 else
                        w.b("blue_wool"))
        blaetter_am_stiel(w, 0.6 * s, rng, 2, 0.1, 2.0)
    return w


def edelweiss(seed, g=1):
    """Edelweiß: auf einem schroffen Felsblock wachsen riesige, filzig-weiße Sternblüten mit gelblichen Köpfchen in
    der Mitte, die wollig graugrünen Blätter liegen dicht am Fels."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    wiese_klein(w, s, art="kies", blumen=0.0)
    from leuchtwald2 import kugel as kugel2
    f = M(w, [("stone", 3), ("andesite", 2), ("diorite", 1)])
    kugel2(w, 0, 1, 0, 3 + 1.5 * s, f, ry=2 + s)
    top = int(3 + 2 * s)
    for k in range(int(2 + s)):
        a = k * 2.2
        c = (math.cos(a) * 1.5 * s, top + 1 + k, math.sin(a) * 1.5 * s)
        linie(w, (c[0], top - 1, c[2]), c, w.b("light_gray_terracotta"))
        L = 2.0 * s + 0.8
        bluete(w, (c[0], c[1] + 0.5, c[2]), (0, 1, 0), 8, L, L * 0.3, cup=0.1, farben=["white_wool", "white_concrete",
                                                                                      "light_gray_wool"], form="spitz")
        for dx, dz in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)):
            w.setze(round(c[0]) + dx, round(c[1]) + 1, round(c[2]) + dz, w.b("yellow_terracotta"))
    return w


def schneegloeckchen(seed, g=1):
    """Schneeglöckchen: aus einer Schneedecke wachsen schlanke Stängel, an deren Ende sich weiße, nickende Glöckchen
    mit grünen Herzzeichen neigen, dazu schmale graugrüne Blätter."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    zellen = wiese_klein(w, s, blumen=0.0)
    for (x, z), h in zellen.items():
        w.setze(x, h + 1, z, w.b("snow", layers=2))
    for k in range(int(3 + 2 * s)):
        a = k * 2.4
        r = 0 if k == 0 else (1.5 + rng.random() * 2) * s
        x0, z0 = round(math.cos(a) * r), round(math.sin(a) * r)
        H = int((6 + rng.random() * 3) * s + 3)
        pts = bogen(w, (x0, 1, z0), (x0 + math.cos(a + 1) * 1.5 * s, H, z0 + math.sin(a + 1) * 1.5 * s), 1,
                    w.b("lime_terracotta"), 0.0, n=8)
        px, py, pz = pts[-1]
        L = 1.6 * s + 0.6
        bluete(w, (px, py - 0.5, pz), (0, -1, 0), 3, L, L * 0.5, cup=0.9, farben=["white_concrete", "white_wool"],
               innen="lime_concrete")
        grasblaetter(w, x0, z0, 2, 3 * s, rng, ["cyan_terracotta", "green_terracotta"])
    return w


def glyzinienbogen(seed, g=2):
    """Glyzinienbogen: ein langer Laubengang aus Holzbögen, über den sich Glyzinien ranken, deren meterlange,
    violette Blütentrauben in dichten Vorhängen herabhängen; darunter ein Kiesweg."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    zellen = wiese_klein(w, s, R=int(9 * s + 5))
    L = int(6 * s + 4)
    B = int(2 + s)
    H = int(4 + 1.5 * s)
    for z in range(-L, L + 1):
        for x in range(-B + 1, B):
            w.setze(x, 0, z, w.b("gravel"))
            w.bloecke.pop((x, 1, z), None)
        if z % 3 == 0:
            for sx in (-B, B):
                for y in range(1, H + 1):
                    w.setze(sx, y, z, w.b("dark_oak_log", axis="y"))
            for x in range(-B, B + 1):
                w.setze(x, H + 1 + (1 if abs(x) < B - 1 else 0), z, w.b("dark_oak_log", axis="x"))
        for x in range(-B - 1, B + 2):
            if rng.random() < 0.7:
                w.setze(x, H + 2 + (1 if abs(x) < B - 1 else 0), z, w.b("oak_leaves", persistent=True, distance=1,
                                                                        waterlogged=False), False)
            if rng.random() < 0.35:
                Lt = int(1 + rng.random() * (H - 1))
                for d in range(Lt):
                    w.setze(x, H + 1 - d, z, w.b(["purple_wool", "magenta_wool", "purple_concrete", "lilac" if False
                                                  else "light_blue_wool"][min(3, d * 4 // max(1, Lt))]), False)
    return w


def kaktusbluete(seed, g=1):
    """Kaktusblüte: ein runder, gerippter Riesenkaktus mit hellen Dornen in einer Wüstensenke, auf dessen Scheitel
    eine einzige, riesige, leuchtend pinke Blüte mit vielen Blütenblättern aufgegangen ist."""
    w = _neu(seed)
    s = S[g]
    zellen = wiese_klein(w, s, art="strand", blumen=0.0)
    r = 2.5 + 1.5 * s
    for x in range(-int(r) - 1, int(r) + 2):
        for y in range(0, int(r * 2) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.sqrt(x * x + ((y - r) / 1.0) ** 2 + z * z)
                a = math.atan2(z, x)
                rr = r * (1 + 0.08 * math.cos(a * 10))
                if d <= rr:
                    w.setze(x, y + 1, z, w.b("green_concrete") if math.cos(a * 10) > 0.6 else w.b("green_terracotta"))
                if rr - 0.5 < d <= rr + 0.6 and (y + round(a * 5)) % 3 == 0 and d > rr:
                    w.setze(x, y + 1, z, w.b("white_terracotta"), False)
    L = 2.5 * s + 1
    top = int(r * 2) + 1
    for lage in range(2):
        bluete(w, (0, top + lage * 0.6, 0), (0, 1, 0), 10 + lage * 2, L - lage * 0.7, (L - lage * 0.7) * 0.3,
               cup=0.8, farben=["pink_concrete", "magenta_concrete", "pink_wool"], innen="yellow_concrete",
               dreh=lage * 0.3)
    for k in range(3):
        a = k * 2.1
        w.setze(round(math.cos(a) * (r + 3)), 1, round(math.sin(a) * (r + 3)), w.b("dead_bush"))
    return w


def magnolienbaum(seed, g=2):
    """Magnolienbaum: ein knorriger Baum ohne Laub, über und über bedeckt mit riesigen, tulpenförmigen Blüten in
    Weiß und Rosa, deren abgefallene Blätter den Boden tupfen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    zellen = wiese_klein(w, s, R=int(8 * s + 5))
    enden = baum_aeste(w, 0, 0, 6 + 3 * s, 6 + g, 4 + 3 * s, "dark_oak", 0.9 + 0.4 * s, rng, steigung=0.6,
                       start=0.35)
    for (x, y, z) in enden:
        for k in range(int(2 + s)):
            c = (x + (rng.random() - 0.5) * 3, y + rng.random() * 2, z + (rng.random() - 0.5) * 3)
            L = 1.1 * s + 0.5
            bluete(w, c, (0, 1, 0), 6, L, L * 0.45, cup=1.6, farben=["white_concrete", "pink_wool", "pink_concrete"],
                   innen="purple_terracotta", form="oval")
    for (x, z), h in zellen.items():
        if rng.random() < 0.08:
            w.setze(x, h + 1, z, w.b("pink_petals", facing="north", flower_amount=1 + int(rng.random() * 3)))
    return w


def blumenuhr(seed, g=2):
    """Blumenuhr: ein großes, rundes Blumenbeet in Form eines Zifferblatts mit zwölf Stundenfeldern aus verschieden-
    farbigen Blumen, steinernen Ziffernmarken und zwei mächtigen Zeigern aus Stein und Gold."""
    w = _neu(seed)
    s = S[g]
    R = int(10 * s + 6)
    zellen = wiese(w, R, huegel=0.0, blumen=0.0)
    ru = R * 0.75
    blumen = ["poppy", "dandelion", "cornflower", "allium", "oxeye_daisy", "orange_tulip", "azure_bluet",
              "pink_tulip", "blue_orchid", "red_tulip", "white_tulip", "lily_of_the_valley"]
    for (x, z), h in zellen.items():
        d = math.hypot(x, z)
        if d > ru:
            continue
        a = (math.atan2(z, x) + math.pi) / (2 * math.pi) * 12
        sek = int(a) % 12
        if abs(d - ru) < 0.8:
            w.setze(x, h, z, w.b("smooth_stone"))
            w.bloecke.pop((x, h + 1, z), None)
        elif abs(a - round(a)) * 2 * math.pi / 12 * d < 0.5:
            w.setze(x, h, z, w.b("gravel"))
            w.bloecke.pop((x, h + 1, z), None)
        else:
            w.setze(x, h, z, w.b("grass_block", snowy=False))
            w.setze(x, h + 1, z, w.b(blumen[sek]))
    for k in range(12):
        a = (k + 0.5) / 12 * 2 * math.pi - math.pi
        x, z = round(math.cos(a) * (ru - 2)), round(math.sin(a) * (ru - 2))
        w.setze(x, 1, z, w.b("chiseled_stone_bricks") if k % 3 == 0 else w.b("stone_brick_slab", type="bottom",
                                                                                waterlogged=False))
    for (L, a) in ((ru * 0.55, -math.pi / 2 - 0.5), (ru * 0.85, 0.6)):
        for t in range(int(L)):
            x, z = round(math.cos(a) * t), round(math.sin(a) * t)
            w.setze(x, 1, z, w.b("gold_block") if t > L - 2 else w.b("polished_andesite"))
    w.setze(0, 2, 0, w.b("gold_block"))
    return w


BLUMEN3 = {
    "orchidee": ("Riesenorchidee", orchidee),
    "krokusse": ("Krokusse im Schnee", krokusse),
    "narzissen": ("Riesennarzissen", narzissen),
    "kornblume": ("Riesenkornblume", kornblume),
    "akelei": ("Akelei", akelei),
    "calla": ("Calla", calla),
    "passionsblume": ("Passionsblume", passionsblume),
    "distel": ("Riesendistel", distel),
    "loewenmaeulchen": ("Löwenmäulchen", loewenmaeulchen),
    "vergissmeinnicht": ("Vergissmeinnicht-Polster", vergissmeinnicht),
    "dahlie": ("Pompon-Dahlie", dahlie),
    "pfingstrose": ("Pfingstrose", pfingstrose),
    "kamillenwiese": ("Kamillenwiese", kamillenwiese),
    "enzian": ("Enzian", enzian),
    "edelweiss": ("Edelweiß", edelweiss),
    "schneegloeckchen": ("Schneeglöckchen", schneegloeckchen),
    "glyzinienbogen": ("Glyzinienbogen", glyzinienbogen),
    "kaktusbluete": ("Kaktusblüte", kaktusbluete),
    "magnolienbaum": ("Magnolienbaum", magnolienbaum),
    "blumenuhr": ("Blumenuhr", blumenuhr),
}

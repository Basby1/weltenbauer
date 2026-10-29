"""Riesenblumen & Zauberwiesen – haushohe Blumen (Rose, Tulpe, Sonnenblume, Pusteblume, Glockenblume …),
magische Leuchtblumen und kombinierbare Blumenwiesen. Fuß auf y = 1 (Boden y = 0)."""

from __future__ import annotations

import math

import numpy as np

from flora import SZ, _lv, _neu, _r, _stil, blatt, bogen, linie, laubfarben
from lib import Rauschen
from wald import Stueck, _fertig, bluetenblaetter, hohes


def _n(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v) + 1e-9)


def _basis(n):
    n = _n(n)
    a = np.array([0, 1, 0]) if abs(n[1]) < 0.9 else np.array([1, 0, 0])
    e1 = _n(np.cross(n, a))
    e2 = np.cross(n, e1)
    return n, e1, e2


def bluete(w, c, n, blaetter, L, B, cup=0.4, farben=("red_concrete",), innen=None, form="oval", dreh=0.0,
           rand=None, punkte=None, rn=None, kraeusel=0.0):
    """Blütenkranz um Mittelpunkt c mit Blickrichtung n. cup > 0: Blätter biegen nach vorn (Kelch),
    cup < 0: nach hinten (Lilie). form: oval, spitz, breit (Mohn), herz (Klee)."""
    n, e1, e2 = _basis(n)
    c = np.asarray(c, float)
    ids = [w.b(f) for f in farben]
    iid = w.b(innen) if innen else None
    rid = w.b(rand) if rand else None
    pid = w.b(punkte) if punkte else None
    rn = rn or Rauschen(w, 1.2)
    gesetzt = set()
    for k in range(blaetter):
        a = dreh + k / blaetter * 2 * math.pi
        d = math.cos(a) * e1 + math.sin(a) * e2
        q = -math.sin(a) * e1 + math.cos(a) * e2
        ns = max(5, int(L / 0.3))
        nt = max(3, int(2 * B / 0.3))
        for i in range(ns + 1):
            s = i / ns
            if form == "spitz":
                br = B * math.sin(math.pi * s ** 0.8)
            elif form == "breit":
                br = B * math.sqrt(max(0, 1 - (1 - s) ** 2)) * (0.6 + 0.4 * s)
            elif form == "herz":
                br = B * (math.sin(math.pi * s) ** 0.6) * (1 - 0.35 * max(0, s - 0.75) * 4 * (1 - abs(0)))
            else:
                br = B * math.sin(math.pi * min(1, s ** 0.7))
            br = max(br, 0.3)
            for j in range(nt + 1):
                t = -1 + 2 * j / nt
                if abs(t) * B > br:
                    continue
                if form == "herz" and s > 0.8 and abs(t * B) < (s - 0.8) * B * 2.5:
                    continue
                vor = cup * L * s * s + kraeusel * math.sin(t * 5 + s * 7) * 0.6
                p = c + d * (L * s) + q * (t * B) + n * vor
                pi = (int(round(p[0])), int(round(p[1])), int(round(p[2])))
                if pi in gesetzt:
                    continue
                gesetzt.add(pi)
                if iid is not None and s < 0.25:
                    blk = iid
                elif rid is not None and (s > 0.88 or abs(t * B) > br - 0.6):
                    blk = rid
                elif pid is not None and 0.25 < s < 0.6 and rn(*pi) > 0.7:
                    blk = pid
                else:
                    v = s * 0.55 + rn(*pi) * 0.5
                    blk = ids[min(len(ids) - 1, int(v * len(ids)))]
                w.setze(*pi, blk)


def kugel(w, c, r, blk, hohl=False, n=None):
    for x in range(int(c[0] - r) - 1, int(c[0] + r) + 2):
        for y in range(int(c[1] - r) - 1, int(c[1] + r) + 2):
            for z in range(int(c[2] - r) - 1, int(c[2] + r) + 2):
                d = math.dist((x, y, z), c)
                if d <= r and (not hohl or d > r - 1.1):
                    if n is not None and np.dot(np.subtract((x, y, z), c), n) < -0.3:
                        continue
                    w.setze(x, y, z, blk(x, y, z) if callable(blk) else blk)


def stiel(w, top, s, blk="green_terracotta", krumm=0.0, rng=None, dicke=None):
    """Stängel vom Boden zur Blüte; leicht geschwungen."""
    dicke = (0.6 if s > 1.3 else 0.0) if dicke is None else dicke
    mitte = (top[0] * 0.4 + krumm, top[1] * 0.5, top[2] * 0.4 - krumm * 0.5)
    linie(w, (0, 1, 0), mitte, w.b(blk), dicke)
    linie(w, mitte, top, w.b(blk), dicke)


def blaetter_am_stiel(w, s, rng, n=3, hoch=0.35, L=5.0, farben=None, form="lanze", B=None):
    for k in range(n):
        yaw = k * 2.39996 + rng.random()
        y = 1 + hoch * (k + 1) * 3 * s
        blatt(w, (0, y, 0), yaw, L * s, (B or L * 0.22) * s, steig=0.5, haeng=0.7, farben=farben or laubfarben(rng),
              mitte="lime_concrete", form=form, kipp=0.1)


# ============================================================================ Riesenblumen

def rose(seed, s=1.0, stil=0):
    """Riesenrose: gefüllte Blüte aus eng gewickelten Blütenblättern, Dornenstiel und gezähnte Blätter."""
    w = _neu(seed)
    rng = w.rng
    H = _r(12 * s + 3)
    top = (0.8 * s, H, 0)
    stiel(w, top, s, "green_terracotta", 1.0 * s)
    for k in range(int(5 * s)):
        y = 2 + k * H / (5 * s)
        w.setze(round(0.3 * s) + (1 if k % 2 else -1), round(y), 0, w.b("lime_terracotta"))
    blaetter_am_stiel(w, s, rng, 3, 0.3, 4.0, form="herz", B=1.6)
    rot = [["red_terracotta", "red_concrete", "red_wool", "red_wool"],
           ["pink_terracotta", "pink_concrete", "pink_wool", "white_wool"]][stil]
    for lage in range(4):
        r = (1 + lage * 1.1) * s
        bluete(w, (top[0], H + 1 + lage * 0.3 * s, 0), (0, 1, 0), 5 + lage, r, r * 0.65, cup=1.5 - lage * 0.3,
               farben=rot, dreh=lage * 0.7)
    for k in range(5):
        a = k / 5 * 2 * math.pi
        linie(w, (top[0], H, 0), (top[0] + math.cos(a) * 2 * s, H - 1.2 * s, math.sin(a) * 2 * s),
              w.b("green_concrete"))
    return w


def tulpe(seed, s=1.0, stil=0):
    """Riesentulpe: drei hohe Tulpen mit becherförmigen Blüten und breiten blaugrünen Blättern."""
    w = _neu(seed)
    rng = w.rng
    farbsets = [["red_concrete", "red_wool", "orange_concrete"], ["yellow_concrete", "yellow_wool", "orange_wool"],
                ["pink_concrete", "pink_wool", "white_wool"], ["purple_concrete", "magenta_wool", "purple_wool"]]
    for i in range(3):
        a = i * 2.1 + 0.3
        d = 2.2 * s * (i > 0)
        H = _r((10 - 2 * i) * s + 3)
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        linie(w, (x0, 1, z0), (x0, H, z0), w.b("lime_terracotta"), 0.6 if s > 1.3 else 0)
        f = farbsets[(i + stil * 2) % 4]
        bluete(w, (x0, H + 1, z0), (0, 1, 0), 6, 3.0 * s + 0.8, 1.5 * s + 0.5, cup=1.8 / (s + 0.3), farben=f,
               innen="black_concrete", form="spitz")
        for k in range(2):
            blatt(w, (x0, 1, z0), a + k * 3.1 + 0.4, (5 + rng.random()) * s, 1.3 * s, steig=1.2, haeng=0.8,
                  farben=["green_terracotta", "lime_terracotta", "green_concrete"], mitte="lime_terracotta",
                  form="lanze", kipp=0.2)
    return w


def sonnenblume(seed, s=1.0, stil=0):
    """Riesensonnenblume: ein kräftiger Stängel mit herzförmigen Blättern, die große Blütenscheibe mit
    Kernen-Spirale zur Sonne geneigt, umrahmt von goldenen Zungenblüten."""
    w = _neu(seed)
    rng = w.rng
    H = _r(16 * s + 4)
    top = (0, H, 0.6 * s)
    stiel(w, top, s, "green_terracotta", 0, dicke=0.7 if s > 1.0 else 0.0)
    for k in range(int(3 + 2 * s)):
        blatt(w, (0, 2 + k * H / (3 + 2 * s), 0), k * 2.39996, (3.5 + rng.random()) * s, 1.8 * s, steig=0.3,
              haeng=0.6, farben=laubfarben(rng), mitte="lime_concrete", form="herz", kipp=0.2)
    n = _n((0.0, 0.55, 1.0))
    R = 2.6 * s + 0.8
    c = np.array([0, H + R * 0.6, 0.6 * s + 0.5])
    _, e1, e2 = _basis(n)
    for i in range(-int(R) - 1, int(R) + 2):
        for j in range(-int(R) - 1, int(R) + 2):
            if i * i + j * j <= R * R:
                for dd in (0, -0.6):
                    p = c + e1 * i + e2 * j + n * dd
                    a = math.atan2(j, i)
                    rr = math.hypot(i, j)
                    spiral = (a * 3 + rr * 1.6) % (2 * math.pi) < math.pi
                    blk = ("brown_terracotta" if spiral else "black_terracotta") if stil == 0 else \
                        ("brown_concrete" if spiral else "orange_terracotta")
                    w.setze(int(round(p[0])), int(round(p[1])), int(round(p[2])), w.b(blk))
    bluete(w, c, n, int(16 + 4 * s), R * 0.9 + 1.2, 0.8 * s + 0.3, cup=0.05,
           farben=["orange_concrete", "yellow_concrete", "yellow_wool"] if stil == 0 else
           ["red_concrete", "orange_concrete", "yellow_concrete"], form="spitz")
    return w


def loewenzahn(seed, s=1.0, stil=0):
    """Löwenzahn & Pusteblume: eine leuchtend gelbe Blüte und daneben eine weiße Samenkugel, aus der einzelne
    Schirmchen davonfliegen; gezackte Blattrosette am Boden."""
    w = _neu(seed)
    rng = w.rng
    for k in range(9):
        blatt(w, (0, 1, 0), k * 0.7, (5 + rng.random() * 2) * s, 1.2 * s, steig=0.15, haeng=0.2,
              farben=laubfarben(rng, hell=1), mitte="lime_concrete", form="lanze", fieder=int(4 + s), kipp=0.0)
    H1 = _r(9 * s + 3)
    linie(w, (0, 1, 0), (-2 * s, H1, 0), w.b("lime_terracotta"))
    c = np.array([-2 * s, H1 + 1.5 * s, 0])
    kugel(w, c, 2.0 * s + 0.5, lambda x, y, z: w.b("yellow_concrete" if (x + y + z) % 3 else "yellow_wool"),
          n=np.array([0, 1, 0]))
    w.setze(round(c[0]), round(c[1] - 2 * s), round(c[2]), w.b("green_concrete"))
    H2 = _r(13 * s + 3)
    linie(w, (0, 1, 0), (2.5 * s, H2, 0.5 * s), w.b("lime_terracotta"))
    c2 = np.array([2.5 * s, H2 + 3.5 * s, 0.5 * s])
    R = 3.5 * s + 1
    for k in range(int(140 * s * s + 40)):
        v = _n(rng.normal(size=3))
        if v[1] < -0.7:
            continue
        p = c2 + v * R * (0.95 + 0.1 * rng.random())
        linie(w, c2 + v * 0.8, p, w.b("white_stained_glass"))
        w.setze(int(round(p[0])), int(round(p[1])), int(round(p[2])), w.b("white_wool"))
    kugel(w, c2, 0.9 * s + 0.4, w.b("brown_terracotta"))
    for k in range(int(4 + 3 * s)):
        p = c2 + np.array([4 + rng.random() * 8, rng.random() * 6, rng.random() * 6 - 3]) * s
        w.setze(int(round(p[0])), int(round(p[1])), int(round(p[2])), w.b("white_wool"))
        w.setze(int(round(p[0])), int(round(p[1])) - 1, int(round(p[2])), w.b("white_stained_glass"))
    return w


def glockenblume(seed, s=1.0, stil=0):
    """Glockenblume: ein überhängender Bogenstängel, an dem große blaue Glocken mit gezacktem Saum und
    Staubgefäßen nach unten hängen."""
    w = _neu(seed)
    rng = w.rng
    H = _r(12 * s + 3)
    pts = bogen(w, (0, 1, 0), (6 * s, H * 1.0, 0), H * 0.35, w.b("green_terracotta"), 0.0, n=14)
    blau = [["blue_concrete", "blue_wool", "light_blue_concrete"], ["purple_concrete", "purple_wool",
                                                                     "magenta_wool"]][stil]
    for k, idx in enumerate((6, 9, 12, 14)):
        px, py, pz = pts[min(idx, len(pts) - 1)]
        top = (px + (k % 2) * 0.8, py - 1, pz + (k - 1.5) * 1.2 * s)
        linie(w, (px, py, pz), top, w.b("green_terracotta"))
        L = (2.0 + 0.4 * k) * s + 0.8
        bluete(w, top, (0, -1, 0), 5, L, L * 0.6, cup=1.6 / (s + 0.4), farben=blau, innen="lime_concrete",
               rand="light_blue_wool" if stil == 0 else "pink_wool")
        w.setze(round(top[0]), round(top[1] - L * 0.9), round(top[2]), w.b("yellow_concrete"))
    blaetter_am_stiel(w, s, rng, 3, 0.2, 3.5)
    return w


def mohn(seed, s=1.0, stil=0):
    """Riesenmohn: vier knittrige, seidige Blütenblätter in Rot mit schwarzem Fleck, eine dicke Samenkapsel
    in der Mitte, haarige Stängel und eine nickende Knospe."""
    w = _neu(seed)
    rng = w.rng
    H = _r(11 * s + 3)
    stiel(w, (0, H, 0), s, "lime_terracotta", 0.8 * s)
    rot = [["red_concrete", "red_wool", "red_concrete"], ["orange_concrete", "orange_wool", "yellow_wool"]][stil]
    bluete(w, (0, H + 1, 0), (0, 1, 0), 4, 4.0 * s + 1, 2.8 * s + 1, cup=0.6 / (s + 0.2), farben=rot,
           innen="black_concrete", form="breit", kraeusel=0.6)
    kugel(w, (0, H + 2, 0), 0.9 * s + 0.4, w.b("lime_terracotta"))
    w.setze(0, H + 2 + round(s), 0, w.b("purple_terracotta"))
    bogen(w, (0, 1, 0), (-3 * s, H * 0.6, 1), 2, w.b("lime_terracotta"))
    kugel(w, (-3 * s, H * 0.6 - 1, 1), 0.8 * s + 0.3, w.b("green_concrete"))
    blaetter_am_stiel(w, s, rng, 4, 0.12, 3.5, form="lanze")
    return w


def gaensebluemchen(seed, s=1.0, stil=0):
    """Gänseblümchen-Strauß: drei riesige Margeriten mit vielen schmalen weißen Strahlenblüten und gelber
    Mitte, zur Sonne geneigt."""
    w = _neu(seed)
    rng = w.rng
    for i in range(3):
        a = i * 2.1
        d = 3 * s * (i > 0)
        H = _r((10 - i * 2) * s + 3)
        x0, z0 = math.cos(a) * d, math.sin(a) * d
        top = (x0 * 1.2, H, z0 * 1.2)
        linie(w, (x0, 1, z0), top, w.b("green_terracotta"))
        n = _n((x0 * 0.2, 1, z0 * 0.2 + 0.5))
        R = 1.0 * s + 0.6
        kugel(w, np.array(top) + n * 1.0, R, w.b("yellow_concrete"), n=n)
        weiss = ["white_concrete", "white_wool", "white_wool"] if stil == 0 else ["white_wool", "pink_wool",
                                                                                   "pink_concrete"]
        bluete(w, np.array(top) + n * 1.0, n, int(18 + 4 * s), 3.2 * s + 1.0, 0.45 * s + 0.3, cup=0.05,
               farben=weiss, form="spitz")
    blaetter_am_stiel(w, s, rng, 5, 0.06, 3.0)
    return w


def lilie(seed, s=1.0, stil=0):
    """Tigerlilie: sechs weit zurückgebogene, gepunktete Blütenblätter mit langen Staubfäden, mehrere Blüten
    und Knospen an einem hohen Stängel mit Quirlblättern."""
    w = _neu(seed)
    rng = w.rng
    H = _r(13 * s + 3)
    linie(w, (0, 1, 0), (0, H, 0), w.b("green_terracotta"), 0.6 if s > 1.3 else 0)
    for k in range(int(4 + 3 * s)):
        y = 2 + k * (H - 4) / (4 + 3 * s)
        for j in range(4):
            yaw = j * 1.57 + k * 0.5
            linie(w, (0, y, 0), (math.cos(yaw) * 2 * s, y + 0.8, math.sin(yaw) * 2 * s), w.b("green_concrete"))
    f = [["orange_concrete", "orange_wool", "orange_concrete"], ["white_concrete", "white_wool", "pink_wool"]][stil]
    for k in range(3):
        yaw = k * 2.1
        top = (math.cos(yaw) * 2.5 * s, H + 1 + k * s, math.sin(yaw) * 2.5 * s)
        linie(w, (0, H - 1, 0), top, w.b("green_terracotta"))
        n = _n((math.cos(yaw), 0.4, math.sin(yaw)))
        bluete(w, top, n, 6, 3.4 * s + 0.8, 0.8 * s + 0.4, cup=-0.5 / (s + 0.2), farben=f,
               punkte="brown_concrete" if stil == 0 else "magenta_concrete", form="spitz")
        for j in range(5):
            a = j / 5 * 2 * math.pi
            _, e1, e2 = _basis(n)
            end = np.array(top) + n * 2.5 * s + (math.cos(a) * e1 + math.sin(a) * e2) * 0.8 * s
            linie(w, top, end, w.b("lime_terracotta"))
            w.setze(int(round(end[0])), int(round(end[1])), int(round(end[2])), w.b("red_terracotta"))
    return w


def lotus(seed, s=1.0, stil=0):
    """Lotusteich: rosa Lotusblüten mit spitzen, gestaffelten Blütenblättern und gelben Samenkapseln über
    großen runden Schwimmblättern im Teich."""
    w = _neu(seed)
    rng = w.rng
    R = 7 * s + 3
    rn = Rauschen(w, 3)
    for x in range(-int(R) - 3, int(R) + 4):
        for z in range(-int(R) - 3, int(R) + 4):
            d = math.hypot(x, z) / (R * (0.85 + 0.3 * rn(x, 0, z)))
            if d < 1:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud"))
            elif d < 1.2:
                w.setze(x, 0, z, w.b("mud" if d < 1.08 else "grass_block", **({} if d < 1.08 else {"snowy": False})))
    rosa = [["pink_terracotta", "pink_concrete", "pink_wool", "white_wool"],
            ["white_terracotta", "white_concrete", "white_wool", "light_blue_wool"]][stil]
    for i in range(int(2 + 2 * s)):
        a = i * 2.39996
        d = R * 0.6 * math.sqrt((i + 0.5) / (2 + 2 * s))
        cx, cz = math.cos(a) * d, math.sin(a) * d
        H = _r((2 + rng.random() * 3) * s + 1)
        linie(w, (cx, 0, cz), (cx, H, cz), w.b("lime_terracotta"))
        for lage in range(3):
            L = (2.4 - lage * 0.5) * s + 0.8
            bluete(w, (cx, H + 1 + lage * 0.4 * s, cz), (0, 1, 0), 8 - lage, L, L * 0.4, cup=0.9 + lage * 0.5,
                   farben=rosa, form="spitz", dreh=lage * 0.4)
        w.setze(round(cx), H + 2, round(cz), w.b("yellow_concrete"))
        rb = (1.5 + rng.random()) * s + 0.8
        bx, bz = cx + math.cos(a + 1) * (rb + 1), cz + math.sin(a + 1) * (rb + 1)
        for x in range(int(bx - rb) - 1, int(bx + rb) + 2):
            for z in range(int(bz - rb) - 1, int(bz + rb) + 2):
                if math.hypot(x - bx, z - bz) <= rb:
                    w.setze(x, 1, z, w.b("green_concrete" if (x + z) % 4 else "lime_concrete"), False)
    return w


def hortensie(seed, s=1.0, stil=0):
    """Hortensienbusch: ein runder Busch mit großen Blütenbällen aus vierblättrigen Einzelblüten, die von Blau
    über Violett zu Rosa verlaufen."""
    w = _neu(seed)
    rng = w.rng
    R = 4 * s + 1.5
    for x in range(-int(R) - 1, int(R) + 2):
        for y in range(0, int(R * 1.3) + 2):
            for z in range(-int(R) - 1, int(R) + 2):
                if (x / R) ** 2 + ((y - R * 0.6) / (R * 0.75)) ** 2 + (z / R) ** 2 < 1 and y >= 1 and rng.random() < 0.9:
                    w.setze(x, y, z, _lv(w, "azalea" if (x + z) % 3 else "oak"))
    farben = [["light_blue_concrete", "light_blue_wool", "blue_wool", "purple_wool", "magenta_wool"],
              ["pink_concrete", "pink_wool", "magenta_wool", "white_wool", "purple_wool"]][stil]
    for k in range(int(6 + 4 * s)):
        v = _n(rng.normal(size=3) * np.array([1, 0.6, 1]) + np.array([0, 0.7, 0]))
        c = np.array([0, R * 0.6, 0]) + v * R * 0.9
        rb = 1.3 * s + 0.6
        idx = min(4, int((c[0] + R) / (2 * R) * 5))
        kugel(w, c, rb, lambda x, y, z: w.b(farben[min(4, max(0, idx + ((x + y * 2 + z) % 3 == 0)))]))
    return w


def fingerhut(seed, s=1.0, stil=0):
    """Fingerhut: hohe Blütenkerzen mit dicht hängenden, gefleckten Röhrenglocken – purpur und weiß."""
    w = _neu(seed)
    rng = w.rng
    for i in range(3):
        a = i * 2.1 + 0.5
        d = 2.5 * s * (i > 0)
        x0, z0 = round(math.cos(a) * d), round(math.sin(a) * d)
        H = _r((14 - i * 3) * s + 4)
        linie(w, (x0, 1, z0), (x0, H, z0), w.b("green_terracotta"))
        farbe = ["magenta_concrete", "purple_concrete", "white_concrete"][(i + stil) % 3]
        for y in range(round(H * 0.4), H):
            for k in range(3):
                yaw = y * 1.1 + k * 2.1
                r = 1 + round(0.6 * s * (1 - (y - H * 0.4) / (H * 0.6)))
                x, z = x0 + round(math.cos(yaw) * r), z0 + round(math.sin(yaw) * r)
                w.setze(x, y, z, w.b(farbe if (y + k) % 4 else "white_wool"))
                w.setze(x, y - 1, z, w.b(farbe.replace("concrete", "wool")), False)
        for k in range(4):
            blatt(w, (x0, 1, z0), k * 1.6 + a, (3 + rng.random()) * s, 1.2 * s, steig=0.4, haeng=0.5,
                  farben=laubfarben(rng), mitte="lime_concrete", form="lanze", kipp=0.0)
    return w


def lavendel(seed, s=1.0, stil=0):
    """Lavendelbusch: ein dichter, halbkugeliger Horst aus graugrünen Blättern mit Dutzenden duftender
    violetter Blütenähren."""
    w = _neu(seed)
    rng = w.rng
    R = 4 * s + 1.5
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            d = math.hypot(x, z) / R
            if d < 1:
                h = round((1 - d * d) * R * 0.5) + 1
                for y in range(1, h + 1):
                    w.setze(x, y, z, w.b("moss_block" if (x + y + z) % 3 else "green_terracotta") if y < h else
                            _lv(w, "azalea"))
                if rng.random() < 0.7:
                    lang = _r((2 + rng.random() * 2) * s + 1)
                    lila = ["purple_concrete", "purple_wool", "magenta_wool", "blue_wool"] if stil == 0 else \
                        ["light_blue_wool", "blue_wool", "purple_wool", "white_wool"]
                    for k in range(lang):
                        w.setze(x, h + 1 + k, z, w.b(lila[(k + x) % 4]) if k > 0 else w.b("green_terracotta"))
    return w


def kleeblatt(seed, s=1.0, stil=0):
    """Glücksklee: ein riesiges vierblättriges Kleeblatt mit hellem Winkelmuster, daneben dreiblättrige Klees
    und eine runde Kleeblüte."""
    w = _neu(seed)
    rng = w.rng
    H = _r(7 * s + 2)
    linie(w, (0, 1, 0), (0, H, 0), w.b("lime_terracotta"))
    bluete(w, (0, H, 0), (0, 1, 0), 4, 4.5 * s + 1, 2.4 * s + 0.8, cup=-0.05,
           farben=["green_concrete", "green_concrete", "lime_concrete"], rand="green_terracotta", form="herz",
           dreh=0.4)
    for k in range(3):
        a = k * 2.1 + 1
        x0, z0 = round(math.cos(a) * 6 * s), round(math.sin(a) * 6 * s)
        h = _r((3 + rng.random() * 2) * s)
        linie(w, (x0, 1, z0), (x0, h, z0), w.b("lime_terracotta"))
        bluete(w, (x0, h, z0), (0, 1, 0), 3, 2.5 * s + 0.6, 1.4 * s + 0.4, cup=-0.05,
               farben=["green_concrete", "lime_concrete"], form="herz", dreh=a)
    x0, z0 = round(math.cos(4) * 4 * s), round(math.sin(4) * 4 * s)
    linie(w, (x0, 1, z0), (x0, H + 2, z0), w.b("lime_terracotta"))
    kugel(w, (x0, H + 3, z0), 1.4 * s + 0.4, lambda x, y, z: w.b("pink_wool" if (x + y + z) % 2 else "white_wool")
          if stil == 0 else w.b("white_wool" if (x + y + z) % 2 else "light_gray_wool"))
    return w


def iris(seed, s=1.0, stil=0):
    """Schwertlilie: drei aufrechte Domblätter und drei herabfallende Hängeblätter mit gelbem Bart, schwertförmige
    Blätter."""
    w = _neu(seed)
    rng = w.rng
    for i in range(2):
        a = i * 3.1
        d = 2 * s * i
        x0, z0 = math.cos(a) * d, math.sin(a) * d
        H = _r((11 - i * 3) * s + 3)
        linie(w, (x0, 1, z0), (x0, H, z0), w.b("green_terracotta"))
        f = [["purple_concrete", "purple_wool", "blue_wool"], ["blue_concrete", "light_blue_wool", "white_wool"]][
            (stil + i) % 2]
        bluete(w, (x0, H + 1, z0), (0, 1, 0), 3, 3 * s + 0.8, 1.3 * s + 0.4, cup=2.0 / (s + 0.4), farben=f,
               form="oval")
        bluete(w, (x0, H + 1, z0), (0, 1, 0), 3, 3.5 * s + 1, 1.6 * s + 0.5, cup=-0.9 / (s + 0.3), farben=f,
               innen="yellow_concrete", form="oval", dreh=1.05)
    for k in range(7):
        blatt(w, (0, 1, 0), k * 0.9, (7 + rng.random() * 2) * s, 0.9 * s, steig=1.6, haeng=0.6,
              farben=["green_terracotta", "lime_terracotta", "green_concrete"], mitte="lime_terracotta",
              form="lanze", kipp=0.0)
    return w


def hibiskus(seed, s=1.0, stil=0):
    """Hibiskusstrauch: ein glänzend grüner Busch mit riesigen trichterförmigen Blüten und langen Staubgriffeln."""
    w = _neu(seed)
    rng = w.rng
    R = 4 * s + 1.5
    for x in range(-int(R) - 1, int(R) + 2):
        for y in range(0, int(R * 1.6) + 2):
            for z in range(-int(R) - 1, int(R) + 2):
                if (x / R) ** 2 + ((y - R * 0.8) / (R * 0.85)) ** 2 + (z / R) ** 2 < 1 and y >= 1 and \
                        rng.random() < 0.85:
                    w.setze(x, y, z, _lv(w, "jungle" if (x + y) % 3 else "azalea"))
    f = [["red_concrete", "red_wool", "red_concrete"], ["yellow_concrete", "orange_wool", "yellow_wool"],
         ["pink_concrete", "pink_wool", "white_wool"]]
    for k in range(int(4 + 2 * s)):
        v = _n(rng.normal(size=3) * np.array([1, 0.5, 1]) + np.array([0, 0.5, 0]))
        c = np.array([0, R * 0.8, 0]) + v * R
        bluete(w, c, v, 5, 1.4 * s + 0.6, 0.9 * s + 0.4, cup=0.4, farben=f[(k + stil) % 3],
               innen="magenta_concrete" if k % 2 else "red_terracotta", form="breit")
        end = c + v * (2.2 * s + 1)
        linie(w, c, end, w.b("pink_terracotta"))
        w.setze(int(round(end[0])), int(round(end[1])), int(round(end[2])), w.b("yellow_concrete"))
    return w


# ============================================================================ Zauberblumen

def leuchtblume(seed, s=1.0, stil=0):
    """Leuchtblume: eine Zauberblume, deren Blütenblätter und Knospen von innen glühen – schimmert nachts wie
    eine Laterne."""
    w = _neu(seed)
    rng = w.rng
    H = _r(10 * s + 3)
    bogen(w, (0, 1, 0), (2 * s, H, 0), 1.5, w.b("warped_stem", axis="y") if stil else w.b("green_terracotta"), 0.0)
    f = [["ochre_froglight", "shroomlight", "yellow_concrete"], ["verdant_froglight", "sea_lantern",
                                                                 "light_blue_concrete"]][stil]
    farben = f
    bluete(w, (2 * s, H + 1, 0), (0.3, 1, 0), 6, 3.2 * s + 1, 1.4 * s + 0.5, cup=1.0 / (s + 0.3), farben=farben,
           innen="glowstone" if stil == 0 else "sea_lantern", form="spitz")
    for k in range(int(3 + 2 * s)):
        a = rng.random() * 6.28
        y = round(H * (0.3 + 0.5 * rng.random()))
        x, z = round(math.cos(a) * 2 * s), round(math.sin(a) * 2 * s)
        linie(w, (s * 0.5, y, 0), (x, y + 1, z), w.b("green_terracotta"))
        w.setze(x, y + 1, z, w.b("pearlescent_froglight" if stil == 0 else "verdant_froglight", axis="y"))
    for k in range(int(4 * s)):
        a = rng.random() * 6.28
        d = (2 + rng.random() * 4) * s
        w.setze(round(math.cos(a) * d), 1, round(math.sin(a) * d), w.b("glow_lichen", down=True, up=False,
                                                                      north=False, south=False, east=False,
                                                                      west=False, waterlogged=False))
    blaetter_am_stiel(w, s, rng, 3, 0.2, 3.5)
    return w


def kristallblume(seed, s=1.0, stil=0):
    """Kristallblume: aus einem Amethystsockel wächst eine Blüte aus Kristallblättern und Glas, umgeben von
    funkelnden Knospen."""
    w = _neu(seed)
    rng = w.rng
    for x in range(-3, 4):
        for z in range(-3, 4):
            if x * x + z * z < 9 * s:
                w.setze(x, 1, z, w.b("amethyst_block" if (x + z) % 2 else "calcite"))
    H = _r(9 * s + 3)
    linie(w, (0, 2, 0), (0, H, 0), w.b("amethyst_block"), 0.5 if s > 1.2 else 0)
    f = [["purple_stained_glass", "amethyst_block", "magenta_stained_glass"],
         ["light_blue_stained_glass", "cyan_stained_glass", "white_stained_glass"]][stil]
    bluete(w, (0, H + 1, 0), (0, 1, 0), 6, 3.6 * s + 1, 1.3 * s + 0.4, cup=1.2 / (s + 0.3), farben=f,
           innen="amethyst_block", rand="purple_stained_glass" if stil == 0 else "light_blue_stained_glass",
           form="spitz")
    w.setze(0, H + 2, 0, w.b("amethyst_cluster", facing="up", waterlogged=False))
    for k in range(int(6 + 4 * s)):
        a = rng.random() * 6.28
        d = (2 + rng.random() * 3) * s
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        w.setze(x, 1, z, w.b("amethyst_block"), False)
        w.setze(x, 2, z, w.b(["amethyst_cluster", "large_amethyst_bud", "medium_amethyst_bud"][k % 3],
                             facing="up", waterlogged=False), False)
    return w


def mondblume(seed, s=1.0, stil=0):
    """Mondblume: silbrig-weiße Blüten, die sich nur bei Nacht öffnen, mit leuchtendem Kern; der Stängel aus
    Birkenholz, Glühwürmchen-Laternen ringsum."""
    w = _neu(seed)
    rng = w.rng
    H = _r(12 * s + 3)
    stiel(w, (0, H, 0), s, "stripped_birch_log", 1.0 * s)
    for lage in range(2):
        L = (4.2 - lage * 1.4) * s + 1
        bluete(w, (0, H + 1 + lage, 0), (0, 1, 0), 8 - lage * 2, L, L * 0.35, cup=0.4 + lage * 0.6,
               farben=["white_concrete", "white_wool", "light_blue_wool"] if stil == 0 else
               ["white_wool", "light_gray_wool", "white_concrete"], form="spitz", dreh=lage * 0.4)
    kugel(w, (0, H + 2, 0), 0.8 * s + 0.4, w.b("sea_lantern"))
    for k in range(int(3 + 2 * s)):
        a = k / (3 + 2 * s) * 6.28
        x, z = round(math.cos(a) * 5 * s), round(math.sin(a) * 5 * s)
        for y in range(1, 3):
            w.setze(x, y, z, w.b("birch_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False))
        w.setze(x, 3, z, w.b("pearlescent_froglight", axis="y"))
    blaetter_am_stiel(w, s, rng, 3, 0.25, 3.5, farben=["green_terracotta", "light_gray_concrete", "white_terracotta"])
    return w


def feuerblume(seed, s=1.0, stil=0):
    """Feuerblume: eine glühende Blume aus Magma und Lavafarben, deren Blätter wie Flammen züngeln, auf
    verbrannter Erde mit Glutnestern."""
    w = _neu(seed)
    rng = w.rng
    for x in range(-int(4 * s) - 1, int(4 * s) + 2):
        for z in range(-int(4 * s) - 1, int(4 * s) + 2):
            if x * x + z * z < (4 * s + 1) ** 2:
                w.setze(x, 0, z, w.b(["blackstone", "basalt", "magma_block", "coarse_dirt"][(x * 3 + z) % 4],
                                     **({"axis": "y"} if (x * 3 + z) % 4 == 1 else {})))
    H = _r(10 * s + 3)
    stiel(w, (0, H, 0), s, "crimson_stem" if stil == 0 else "warped_stem", 0.5 * s)
    f = [["red_concrete", "orange_concrete", "yellow_concrete", "shroomlight"],
         ["blue_concrete", "cyan_concrete", "light_blue_concrete", "sea_lantern"]][stil]
    bluete(w, (0, H + 1, 0), (0, 1, 0), 7, 4 * s + 1, 1.0 * s + 0.4, cup=1.6 / (s + 0.3), farben=f, form="spitz",
           kraeusel=0.8)
    w.setze(0, H + 1, 0, w.b("magma_block"))
    for k in range(int(3 * s)):
        a = rng.random() * 6.28
        y = round(H * (0.3 + 0.4 * rng.random()))
        blatt(w, (0, y, 0), a, 3 * s, 0.8 * s, steig=1.0, haeng=0.3, farben=f[:3], mitte="red_terracotta",
              form="lanze", kipp=0.0)
    return w


# ============================================================================ Wiesen & Felder (kombinierbar)

def _blume_zufall(st, s, arten):
    def wahl(x, z, rd, art):
        f = arten[int(st.rng.integers(len(arten)))]
        k = s * (0.5 + 0.5 * st.rng.random())
        return f(int(st.rng.integers(1, 10 ** 7)), k, st.stil), 4 * k + 1
    return wahl


WIESENBLUMEN = [("poppy", 2), ("dandelion", 2), ("oxeye_daisy", 2), ("azure_bluet", 1.5), ("cornflower", 1.5),
                ("allium", 1), ("pink_tulip", 0.8), ("red_tulip", 0.8), ("orange_tulip", 0.6), ("white_tulip", 0.6),
                ("lily_of_the_valley", 0.6), ("grass", 6), (hohes("tall_grass"), 2), (hohes("peony"), 0.5),
                (hohes("lilac"), 0.5), (hohes("rose_bush"), 0.5), (bluetenblaetter, 1)]


def zauberwiese(seed, g=1):
    """Zauberwiese: zwischen Riesenblumen aller Art ein Teppich aus Wildblumen, Blütenblättern und hohem Gras –
    lässt sich aneinanderreihen."""
    st = Stueck(seed, g)
    arten = [rose, tulpe, sonnenblume, loewenzahn, mohn, gaensebluemchen, glockenblume, lilie, fingerhut]
    st.verteile(6, int(140 * (g + 1) ** 2), _blume_zufall(st, 0.6 + 0.15 * g, arten))
    st.boden([("grass_block_s", 8), ("moss_block", 1)], WIESENBLUMEN, dichte=0.75, belag_dichte=0.4)
    return st


def blumenmeer(seed, g=1):
    """Blumenmeer: geschwungene Bänder aus roten, gelben, blauen und weißen Blumen wie ein Farbverlauf über eine
    sanfte Wiese, dazwischen einzelne Riesentulpen."""
    st = Stueck(seed, g)
    w = st.w
    baender = ["poppy", "orange_tulip", "dandelion", "oxeye_daisy", "azure_bluet", "cornflower", "allium",
               "pink_tulip"]
    st.verteile(9, int(40 * (g + 1) ** 2), _blume_zufall(st, 0.5 + 0.12 * g, [tulpe, mohn]))
    for x in range(-int(st.R * 1.3), int(st.R * 1.3) + 1):
        for z in range(-int(st.R * 1.3), int(st.R * 1.3) + 1):
            rd = st.rand(x, z)
            if rd > 1.0:
                continue
            if w.frei(x, 0, z):
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
                w.folgen[(x, 0, z)] = -1
            band = int(((x + z * 0.6 + 6 * math.sin(z * 0.15)) / 5)) % len(baender)
            if w.frei(x, 1, z) and st.rng.random() < 0.8 * (1.1 - rd):
                w.setze(x, 1, z, w.b(baender[band] if st.rng.random() < 0.85 else "grass"))
                w.folgen[(x, 1, z)] = -1
    return st


def lavendelfeld(seed, g=1):
    """Lavendelfeld: lange Reihen runder Lavendelbüsche auf heller Erde, ein Feldweg und ein paar Bienenstöcke
    am Rand."""
    st = Stueck(seed, g)
    w = st.w
    abst = 5
    for x in range(-int(st.R * 1.2), int(st.R * 1.2) + 1, abst):
        for z in range(-int(st.R * 1.2), int(st.R * 1.2) + 1, 3):
            if st.rand(x, z) < 0.92 and abs(x - 2) > 1:
                st.stempel(lavendel(int(st.rng.integers(1, 10 ** 6)), 0.5, st.stil), x, z)
    for x in range(-int(st.R * 1.3), int(st.R * 1.3) + 1):
        for z in range(-int(st.R * 1.3), int(st.R * 1.3) + 1):
            if st.rand(x, z) < 1.0 and w.frei(x, 0, z):
                w.setze(x, 0, z, w.b("coarse_dirt" if (x % abst) in (2, 3) else "grass_block",
                                     **({} if (x % abst) in (2, 3) else {"snowy": False})))
                w.folgen[(x, 0, z)] = -1
    for k in range(2 + g):
        z = -int(st.R * 0.8) + k * 3
        w.setze(int(st.R * 0.8), 1, z, w.b("beehive", facing="west", honey_level=3))
        w.folgen[(int(st.R * 0.8), 1, z)] = -1
    return st


def sonnenblumenfeld(seed, g=1):
    """Sonnenblumenfeld: dicht stehende, alle zur Sonne gewandte Riesensonnenblumen unterschiedlicher Höhe auf
    einem Acker, dazwischen Mohn und eine Vogelscheuche."""
    st = Stueck(seed, g)
    w = st.w
    st.verteile(4, int(120 * (g + 1) ** 2), _blume_zufall(st, 0.35 + 0.08 * g, [sonnenblume]))
    st.boden([("farmland", 3), ("coarse_dirt", 1), ("grass_block_s", 2)],
             [("poppy", 1), ("grass", 3), ("cornflower", 0.5), ("wheat", 1)], dichte=0.3, belag_dichte=0.9)
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) == "minecraft:wheat":
            w.bloecke[(x, y, z)] = w.b("wheat", age=7)
        if w.P.name(b) == "minecraft:farmland":
            w.bloecke[(x, y, z)] = w.b("farmland", moisture=7)
    return st


def bluetenpfad(seed, g=1):
    """Blütenpfad: ein Trittsteinweg schlängelt sich durch eine Wiese, gesäumt von Glockenblumen, Lilien,
    Fingerhut und Leuchtblumen."""
    import wald2
    st = Stueck(seed, g)
    pts = wald2.wegpunkte(st, "kurve", 2.0)
    for x, z in pts:
        st.plaetze.append((x, z, 3.0))
    st.verteile(5, int(160 * (g + 1) ** 2), _blume_zufall(st, 0.55 + 0.12 * g,
                                                          [glockenblume, lilie, fingerhut, leuchtblume, iris, mohn]))
    wald2.weg(st, pts, breite=2.0, belag="kies", trittsteine=True, rand_steine=0.1)
    st.boden([("grass_block_s", 8), ("moss_block", 1)], WIESENBLUMEN, dichte=0.65, belag_dichte=0.4)
    return st


def bluetenbogen(seed, s=1.0, stil=0):
    """Blütenbogen: ein Rundbogen aus Rankgitter, völlig überwuchert von Rosen, Glyzinien-Trauben und
    Kletterpflanzen – ein Tor in die Zauberwiese."""
    w = _neu(seed)
    rng = w.rng
    B = _r(4 * s + 2)
    H = _r(6 * s + 3)
    for sz in (-1, 1):
        for k in range(int(math.pi * B * 1.5) + 1):
            a = k / (math.pi * B * 1.5) * math.pi
            x = round(math.cos(a) * B)
            y = round(H + math.sin(a) * B * 0.8)
            w.setze(x, y, sz, w.b("oak_fence", north=False, south=False, east=False, west=False, waterlogged=False))
        for sx in (-B, B):
            for y in range(1, H + 1):
                w.setze(sx, y, sz, w.b("oak_fence", north=False, south=False, east=False, west=False,
                                       waterlogged=False))
    for (x, y, z) in list(w.bloecke):
        for dz in (-1, 0, 1):
            if rng.random() < 0.55:
                w.setze(x + int(rng.integers(-1, 2)), y, z + dz, _lv(w, "flowering_azalea" if rng.random() < 0.4
                                                                    else "azalea"), False)
    rosen = ["red_wool", "pink_wool", "white_wool"] if stil == 0 else ["purple_wool", "magenta_wool", "light_blue_wool"]
    for k in range(int(25 * s)):
        a = rng.random() * math.pi
        x = round(math.cos(a) * B + rng.integers(-1, 2))
        y = round(H + math.sin(a) * B * 0.8)
        z = int(rng.integers(-2, 3))
        w.setze(x, y, z, w.b(rosen[k % 3]))
        if stil == 1 and k % 2:
            for d in range(1, 4):
                w.setze(x, y - d, z, w.b("purple_wool" if d < 3 else "magenta_wool"), False)
    for x in range(-B + 1, B):
        w.setze(x, 0, 0, w.b("mossy_stone_bricks" if x % 2 else "stone_bricks"))
    return w


# ============================================================================ Tabelle

def _einzeln(pflanze, R_extra=3, dichte=0.5):
    def f(seed, g=1):
        st = Stueck(seed, g)
        p = pflanze(int(seed), SZ[g], _stil(seed))
        xs = [q[0] for q in p.bloecke] + [0]
        zs = [q[2] for q in p.bloecke] + [0]
        st.R = max(4, int(max(-min(xs), max(xs), -min(zs), max(zs)) * 0.85) + R_extra)
        st.stempel(p, 0, 0)
        st.boden([("grass_block_s", 8), ("moss_block", 1), ("coarse_dirt", 0.4)], WIESENBLUMEN, dichte=dichte,
                 belag_dichte=0.5)
        return _fertig(st.w)
    f.__doc__ = pflanze.__doc__
    return f


def _wrap(f):
    def g(seed, groesse=1):
        st = f(seed, groesse)
        return _fertig(st.w if isinstance(st, Stueck) else st)
    g.__doc__ = f.__doc__
    return g


BLUMEN = {
    "rose": ("Riesenrose", _einzeln(rose)),
    "tulpe": ("Riesentulpen", _einzeln(tulpe)),
    "sonnenblume": ("Riesensonnenblume", _einzeln(sonnenblume)),
    "loewenzahn": ("Löwenzahn & Pusteblume", _einzeln(loewenzahn)),
    "glockenblume": ("Glockenblume", _einzeln(glockenblume)),
    "mohn": ("Riesenmohn", _einzeln(mohn)),
    "gaensebluemchen": ("Riesen-Margeriten", _einzeln(gaensebluemchen)),
    "lilie": ("Tigerlilie", _einzeln(lilie)),
    "lotus": ("Lotusteich", _einzeln(lotus, R_extra=1, dichte=0.2)),
    "hortensie": ("Hortensienbusch", _einzeln(hortensie)),
    "fingerhut": ("Fingerhut", _einzeln(fingerhut)),
    "lavendel": ("Lavendelbusch", _einzeln(lavendel)),
    "kleeblatt": ("Glücksklee", _einzeln(kleeblatt)),
    "iris": ("Schwertlilie", _einzeln(iris)),
    "hibiskus": ("Hibiskus", _einzeln(hibiskus)),
    "leuchtblume": ("Leuchtblume", _einzeln(leuchtblume)),
    "kristallblume": ("Kristallblume", _einzeln(kristallblume)),
    "mondblume": ("Mondblume", _einzeln(mondblume)),
    "feuerblume": ("Feuerblume", _einzeln(feuerblume, dichte=0.2)),
    "bluetenbogen": ("Blütenbogen", _einzeln(bluetenbogen)),
    "zauberwiese": ("Zauberwiese", _wrap(zauberwiese)),
    "blumenmeer": ("Blumenmeer", _wrap(blumenmeer)),
    "lavendelfeld": ("Lavendelfeld", _wrap(lavendelfeld)),
    "sonnenblumenfeld": ("Sonnenblumenfeld", _wrap(sonnenblumenfeld)),
    "bluetenpfad": ("Blütenpfad", _wrap(bluetenpfad)),
}

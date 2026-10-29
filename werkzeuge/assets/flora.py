"""Riesenpflanzen & Dschungelflora – riesige Einzelpflanzen (Monstera, Elefantenohr, Bananenstaude, Baumfarn …)
und kombinierbare Dschungelstücke. Pflanzen stehen mit dem Fuß auf y = 1 (Boden y = 0), wie die Bäume im Wald.
Größen 0 klein · 1 mittel · 2 riesig · 3 gigantisch, je zwei Stile."""

from __future__ import annotations

import math

import numpy as np

import wald2
from lib import Rauschen, Welt
from wald import Stueck, _fertig, bambus, hohes

SZ = [0.6, 1.0, 1.6, 2.4]

GRUEN = ["green_terracotta", "green_concrete", "green_wool", "lime_terracotta", "lime_concrete"]
DUNKEL = ["black_terracotta", "green_terracotta", "green_concrete", "green_wool"]
HELL = ["green_concrete", "green_wool", "lime_concrete", "lime_wool"]


def _neu(seed):
    w = Welt(int(seed))
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


LAUB = [["green_terracotta", "green_concrete", "green_concrete", "moss_block"],
        ["green_concrete", "moss_block", "green_wool", "lime_concrete"],
        ["green_wool", "moss_block", "lime_concrete", "lime_wool"]]


def laubfarben(rng, stil=0, hell=0):
    k = min(2, int(rng.random() * 3 * 0.999) + hell)
    return LAUB[k]


def _lv(w, art="jungle"):
    return w.b(f"{art}_leaves", persistent=True, distance=1, waterlogged=False)


# ============================================================================ Bausteine

def linie(w, a, b, blk, dicke=0.0, ueber=True):
    """Gerade aus Blöcken von a nach b (optional mit Radius)."""
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]), abs(b[2] - a[2])) * 1.6) + 1
    r = int(math.ceil(dicke))
    for i in range(n + 1):
        t = i / n
        x, y, z = (a[k] + (b[k] - a[k]) * t for k in range(3))
        if r == 0:
            w.setze(round(x), round(y), round(z), blk, ueber)
        else:
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if dx * dx + dz * dz <= dicke * dicke + 0.3:
                        w.setze(round(x) + dx, round(y), round(z) + dz, blk, ueber)


def bogen(w, a, b, hub, blk, dicke=0.0, n=8):
    """Gebogener Stiel von a nach b, Mitte um hub angehoben."""
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(tuple(a[k] + (b[k] - a[k]) * t + (hub * 4 * t * (1 - t) if k == 1 else 0) for k in range(3)))
    for p, q in zip(pts, pts[1:]):
        linie(w, p, q, blk, dicke)
    return pts


def blatt(w, p0, yaw, L, B, steig=0.3, haeng=0.5, farben=None, mitte=None, form="herz", schlitze=0, loecher=0.0,
          kipp=0.25, spitze=0.75, rauschen=None, rand=None, fieder=0):
    """Großes Blatt als gewölbte Fläche.
    p0 Ansatz, yaw Richtung (Bogenmaß), L Länge, B halbe Breite. steig/haeng: Anstieg und Durchhang.
    form: herz (breiter Grund), lanze (schmal, Mitte breit), paddel (lang & gleich breit), rund (Seerose).
    schlitze: Monstera-Einschnitte, loecher: Anteil Fenster, fieder: Fiederblatt (Farn/Palmfarn) mit n Paaren."""
    farben = farben or GRUEN
    ids = [w.b(f) for f in farben]
    mid = w.b(mitte) if mitte else ids[-1]
    rnd = w.b(rand) if rand else None
    rn = rauschen or Rauschen(w, 2.0)
    dx, dz = math.cos(yaw), math.sin(yaw)
    sx, sz = -dz, dx
    ns = max(6, int(L / 0.35))
    nt = max(4, int(2 * B / 0.35))
    gesetzt = set()
    for i in range(ns + 1):
        s = i / ns
        if form == "herz":
            breite = B * (math.sin(math.pi * min(1, s ** spitze)) ** 0.7 if s > 0.04 else 0.3)
            breite = max(breite, B * 0.55 * (1 - s / 0.18)) if s < 0.18 else breite
        elif form == "lanze":
            breite = B * math.sin(math.pi * s) ** 0.9
        elif form == "paddel":
            breite = B * min(1, s * 6) * min(1, (1 - s) * 5)
        else:
            breite = B * math.sqrt(max(0, 1 - (2 * s - 1) ** 2))
        if breite < 0.25:
            breite = 0.25
        for j in range(nt + 1):
            t = -1 + 2 * j / nt
            if abs(t) * B > breite + 0.2:
                continue
            tt = t * B / max(breite, 1e-6) if breite > 0 else 0
            tt = max(-1.0, min(1.0, t * B / breite))
            if schlitze and abs(tt) > 0.32 and s > 0.08 and math.sin(s * math.pi * schlitze) > 0.55:
                continue
            if fieder and abs(tt) > 0.15 and math.sin(s * math.pi * fieder * 2) > 0.1:
                continue
            if loecher and 0.3 < abs(tt) < 0.65 and math.sin(s * math.pi * schlitze * 1.0 + 1.5) > 1 - loecher:
                continue
            q = t * B if abs(t * B) <= breite else math.copysign(breite, t)
            x = p0[0] + dx * L * s + sx * q
            z = p0[2] + dz * L * s + sz * q
            y = p0[1] + steig * L * s - haeng * L * s * s - kipp * abs(q) ** 1.5 / max(1.0, B ** 0.5)
            p = (round(x), round(y), round(z))
            if p in gesetzt:
                continue
            gesetzt.add(p)
            if abs(tt) < 0.12 and s < 0.95:
                blk = mid
            elif rnd is not None and abs(tt) > 0.88:
                blk = rnd
            else:
                v = 0.55 * (1 - abs(tt)) * 0.6 + 0.45 * s * 0.6 + rn(*p) * 0.55
                blk = ids[min(len(ids) - 1, int(v * len(ids)))]
            w.setze(*p, blk)
    return (p0[0] + dx * L, p0[1] + steig * L - haeng * L, p0[2] + dz * L)


def boden_dschungel(st, dichte=0.6, nass=False):
    belag = [("grass_block_s", 4), ("podzol", 2), ("moss_block", 2.5), ("rooted_dirt", 0.8), ("coarse_dirt", 0.6)]
    if nass:
        belag += [("mud", 2)]
    st.boden(belag, [("fern", 4), (hohes("large_fern"), 3), ("grass", 3), (hohes("tall_grass"), 1),
                     ("moss_carpet", 1.5), (bambus, 0.25), ("blue_orchid", 0.3)], dichte=dichte)


def einzeln(pflanze, R_extra=3, dichte=0.45):
    """Macht aus einer Pflanzenfunktion pflanze(seed, s) eine Vorlage mit kleinem Dschungelboden."""
    def f(seed, g=1):
        st = Stueck(seed, g)
        p = pflanze(int(seed), SZ[g], _stil(seed))
        xs = [q[0] for q in p.bloecke] + [0]
        zs = [q[2] for q in p.bloecke] + [0]
        st.R = max(4, int(max(-min(xs), max(xs), -min(zs), max(zs)) * 0.85) + R_extra)
        st.stempel(p, 0, 0)
        boden_dschungel(st, dichte)
        return _fertig(st.w)
    f.__doc__ = pflanze.__doc__
    return f


# ============================================================================ Riesenpflanzen

def monstera(seed, s=1.0, stil=0):
    """Riesen-Monstera: herzförmige, tief geschlitzte und gefensterte Blätter auf langen Stielen, Luftwurzeln."""
    w = _neu(seed)
    rng = w.rng
    n = int(6 + 2 * s)
    farben = ["green_terracotta", "green_wool", "green_concrete", "green_concrete", "lime_concrete"] if stil == 0 \
        else ["green_wool", "green_concrete", "white_concrete", "green_concrete", "white_wool"]
    for i in range(n):
        yaw = i * 2.39996 + rng.random() * 0.4
        hoehe = (4 + 7 * (i % 3) / 2 + 2 * rng.random()) * s
        weit = (1.5 + 3 * rng.random()) * s
        a = (0, 1, 0)
        b = (math.cos(yaw) * weit, 1 + hoehe, math.sin(yaw) * weit)
        bogen(w, a, b, 1.5 * s, w.b("lime_terracotta" if i % 2 else "green_terracotta"), 0.0)
        L = (6 + 3 * rng.random()) * s
        blatt(w, b, yaw + (rng.random() - 0.5) * 0.6, L, L * 0.45, steig=0.75, haeng=1.15,
              farben=farben if stil else laubfarben(rng), rand="green_terracotta",
              mitte="lime_concrete", form="herz", schlitze=int(5 + 2 * s), loecher=0.35, kipp=0.45)
    for k in range(int(3 * s)):
        yaw = rng.random() * 6.28
        x0, z0 = math.cos(yaw) * s, math.sin(yaw) * s
        linie(w, (x0, 1 + 3 * s, z0), (x0 * 3, 1, z0 * 3), w.b("brown_terracotta"))
    return w


def elefantenohr(seed, s=1.0, stil=0):
    """Elefantenohr (Alocasia): riesige aufrechte Pfeilblätter mit hellen Adern auf dicken Stielen."""
    w = _neu(seed)
    rng = w.rng
    n = int(5 + 2 * s)
    if stil == 0:
        farben, mitte, rand = ["green_wool", "green_concrete", "green_concrete", "lime_concrete"], "lime_concrete", None
    else:
        farben, mitte, rand = ["black_terracotta", "green_terracotta", "green_concrete", "green_terracotta"], \
            "white_concrete", "white_terracotta"
    for i in range(n):
        yaw = i * 2.39996
        hoehe = (6 + 4 * rng.random()) * s
        weit = (1.5 + 2 * rng.random()) * s
        b = (math.cos(yaw) * weit, 1 + hoehe, math.sin(yaw) * weit)
        bogen(w, (0, 1, 0), b, 0.8 * s, w.b("lime_terracotta"), 0.6 if s > 1.2 else 0.0)
        L = (8 + 3 * rng.random()) * s
        blatt(w, b, yaw, L, L * 0.4, steig=1.15, haeng=0.85, farben=farben if stil else laubfarben(rng), mitte=mitte,
              rand=rand, form="herz",
              spitze=0.55, kipp=0.3)
    return w


def bananenstaude(seed, s=1.0, stil=0):
    """Bananenstaude: dicker Scheinstamm, lange zerschlissene Paddelblätter, hängender Fruchtstand mit
    Bananen und lila Blütenknospe."""
    w = _neu(seed)
    rng = w.rng
    H = _r(7 * s + 2)
    for y in range(1, H + 1):
        for dx in range(-1, 1 + (s > 1.3)):
            for dz in range(-1, 1 + (s > 1.3)):
                if abs(dx) + abs(dz) <= 1 + (s > 1.3):
                    w.setze(dx, y, dz, w.b(["lime_terracotta", "green_terracotta", "brown_terracotta"][(y + dx) % 3]
                                           if y < H - 1 else "lime_terracotta"))
    n = int(6 + 2 * s)
    for i in range(n):
        yaw = i * 2.39996
        L = (9 + 3 * rng.random()) * s
        blatt(w, (0, H, 0), yaw, L, L * 0.17, steig=0.9, haeng=1.0, farben=laubfarben(rng, hell=1),
              mitte="lime_terracotta", form="paddel", schlitze=int(9 * s) if i % 2 else 0, kipp=0.1)
    yaw = rng.random() * 6.28
    bx, bz = round(math.cos(yaw) * 2 * s), round(math.sin(yaw) * 2 * s)
    linie(w, (0, H, 0), (bx, H - 1, bz), w.b("lime_terracotta"))
    gelb = "yellow_concrete" if stil == 0 else "lime_concrete"
    for k in range(_r(3 * s)):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) + abs(dz) == 1 or (k % 2 and abs(dx) + abs(dz) == 2):
                    w.setze(bx + dx, H - 2 - k, bz + dz, w.b(gelb))
        w.setze(bx, H - 2 - k, bz, w.b("lime_terracotta"))
    for k in range(_r(2 * s)):
        w.setze(bx, H - 3 - _r(3 * s) - k, bz, w.b("purple_concrete" if k else "magenta_terracotta"))
    return w


def baumfarn(seed, s=1.0, stil=0):
    """Baumfarn: schlanker, zotteliger Stamm, oben eine Krone aus langen, gefiederten, überhängenden Wedeln und
    eingerollten jungen Trieben."""
    w = _neu(seed)
    rng = w.rng
    H = _r(9 * s + 3)
    neig = rng.random() * 6.28
    for y in range(1, H + 1):
        x = round(math.cos(neig) * y * 0.08)
        z = round(math.sin(neig) * y * 0.08)
        w.setze(x, y, z, w.b(["brown_terracotta", "dark_oak_log", "spruce_log"][y % 3], **({} if y % 3 == 0 else
                                                                                            {"axis": "y"})))
        if s > 1.2:
            for dx, dz in ((1, 0), (0, 1)):
                w.setze(x + dx, y, z + dz, w.b("brown_terracotta" if (y + dx) % 2 else "dark_oak_log",
                                               **({} if (y + dx) % 2 else {"axis": "y"})))
    tx, tz = round(math.cos(neig) * H * 0.08), round(math.sin(neig) * H * 0.08)
    n = int(11 + 3 * s)
    farben = ["green_terracotta", "green_concrete", "green_wool", "lime_concrete"] if stil == 0 else \
        ["green_terracotta", "green_concrete", "lime_terracotta", "lime_concrete"]
    for i in range(n):
        yaw = i * 2.39996
        L = (7 + 3 * rng.random()) * s
        blatt(w, (tx, H + 1, tz), yaw, L, L * 0.2, steig=0.5 + 0.3 * rng.random(), haeng=1.0,
              farben=farben if stil else laubfarben(rng, hell=1),
              mitte="brown_terracotta", form="lanze", fieder=int(7 + 2 * s), kipp=0.05)
    for k in range(3):
        yaw = k * 2.1
        x, z = tx + round(math.cos(yaw)), tz + round(math.sin(yaw))
        w.setze(x, H + 2, z, w.b("lime_concrete"))
        w.setze(x + round(math.cos(yaw)), H + 3, z + round(math.sin(yaw)), w.b("lime_concrete"))
    return w


def strelitzie(seed, s=1.0, stil=0):
    """Paradiesvogelblume: ein Horst aus steifen Paddelblättern, dazwischen große Blüten wie Vogelköpfe mit
    orangen Federn und blauer Zunge."""
    w = _neu(seed)
    rng = w.rng
    for i in range(int(8 + 3 * s)):
        yaw = i * 2.39996
        h = (3 + 3 * rng.random()) * s
        b = (math.cos(yaw) * s, 1 + h, math.sin(yaw) * s)
        linie(w, (0, 1, 0), b, w.b("green_terracotta"))
        blatt(w, b, yaw, (5 + 2 * rng.random()) * s, 1.6 * s, steig=0.9, haeng=0.6,
              farben=["green_terracotta", "green_concrete", "lime_terracotta"], mitte="lime_terracotta",
              form="lanze", kipp=0.0)
    feder = ["orange_concrete", "orange_wool", "yellow_concrete"] if stil == 0 else \
        ["white_concrete", "white_wool", "light_gray_concrete"]
    for k in range(int(3 + 2 * s)):
        yaw = k * 2.6 + 0.5
        d = 1.5 * s
        top = (math.cos(yaw) * d, 1 + (8 + 2 * rng.random()) * s, math.sin(yaw) * d)
        linie(w, (0, 1, 0), top, w.b("green_terracotta"))
        dx, dz = math.cos(yaw + 1.2), math.sin(yaw + 1.2)
        L = 3 * s + 1
        for j in range(_r(L)):
            x, y, z = top[0] + dx * j, top[1] + j * 0.15, top[2] + dz * j
            w.setze(round(x), round(y), round(z), w.b("purple_terracotta" if j < L * 0.7 else "red_terracotta"))
            if j > L * 0.3:
                for f in range(_r(1.5 * s)):
                    w.setze(round(x - dx * 0.3 * f), round(y + 1 + f), round(z - dz * 0.3 * f),
                            w.b(feder[(j + f) % 3]))
        w.setze(round(top[0] + dx * L * 0.6), round(top[1] + 1), round(top[2] + dz * L * 0.6),
                w.b("blue_concrete"))
    return w


def heliconie(seed, s=1.0, stil=0):
    """Hummerschere (Heliconia): hohe Bananenblätter und hängende Zickzack-Blütenstände in Rot und Gelb."""
    w = _neu(seed)
    rng = w.rng
    for i in range(int(5 + 2 * s)):
        yaw = i * 2.39996
        h = (5 + 3 * rng.random()) * s
        b = (math.cos(yaw) * 1.2 * s, 1 + h, math.sin(yaw) * 1.2 * s)
        linie(w, (0, 1, 0), b, w.b("green_terracotta"))
        blatt(w, b, yaw, (6 + 2 * rng.random()) * s, 1.5 * s, steig=1.1, haeng=0.9,
              farben=laubfarben(rng, hell=1), mitte="lime_terracotta", form="paddel")
    rot, gelb = ("red_concrete", "yellow_concrete") if stil == 0 else ("pink_concrete", "lime_concrete")
    for k in range(int(2 + 2 * s)):
        yaw = k * 2.3 + 1
        d = 2.2 * s
        top = (round(math.cos(yaw) * d), round(1 + (7 + rng.random() * 2) * s), round(math.sin(yaw) * d))
        linie(w, (0, 1, 0), top, w.b("green_terracotta"))
        for j in range(_r(5 * s)):
            seite = 1 if j % 2 else -1
            x = top[0] + round(math.cos(yaw + 1.57) * seite)
            z = top[2] + round(math.sin(yaw + 1.57) * seite)
            w.setze(top[0], top[1] - j, top[2], w.b(rot))
            w.setze(x, top[1] - j, z, w.b(rot))
            w.setze(x, top[1] - j + 1, z, w.b(gelb))
    return w


def kannenpflanze(seed, s=1.0, stil=0):
    """Kannenpflanze: Ranken klettern an einem Totholzpfahl empor, große hängende Fallkannen mit Deckel und
    rotem Mundrand, gefüllt mit Wasser."""
    w = _neu(seed)
    rng = w.rng
    H = _r(10 * s + 3)
    for y in range(1, H + 1):
        w.setze(0, y, 0, w.b("dark_oak_log", axis="y") if y % 4 else w.b("mossy_cobblestone"))
    for k in range(int(4 + 3 * s)):
        yaw = k * 2.39996
        y0 = 2 + rng.random() * (H - 3)
        r = (2 + 2 * rng.random()) * s
        cx, cz = round(math.cos(yaw) * r), round(math.sin(yaw) * r)
        cy = round(y0 - 2 * s)
        bogen(w, (0, y0, 0), (cx, cy + 3 * s, cz), 1.5, w.b("green_terracotta"))
        rk = max(1, round(0.6 * s))
        hk = _r(1.5 * s + 1)
        koerper = "lime_terracotta" if stil == 0 else "red_terracotta"
        for y in range(cy, cy + hk):
            for dx in range(-rk, rk + 1):
                for dz in range(-rk, rk + 1):
                    d = math.hypot(dx, dz)
                    if d <= rk + 0.3:
                        innen = d < rk - 0.5 and y > cy
                        if innen:
                            if y < cy + hk - 1:
                                w.setze(cx + dx, y, cz + dz, w.b("water", level=0))
                        else:
                            w.setze(cx + dx, y, cz + dz, w.b(koerper if (y + dx) % 3 else "red_concrete"))
        for dx in range(-rk, rk + 1):
            for dz in range(-rk, rk + 1):
                if rk - 0.6 <= math.hypot(dx, dz) <= rk + 0.4:
                    w.setze(cx + dx, cy + hk, cz + dz, w.b("red_concrete"))
        w.setze(cx, cy + hk + 1 + rk, cz, w.b("lime_terracotta"))
        for dx in range(-rk, rk + 1):
            w.setze(cx + dx, cy + hk + rk, cz - rk, w.b("lime_terracotta"))
    return w


def bromelie(seed, s=1.0, stil=0):
    """Riesen-Bromelie: Rosette aus steifen, glänzenden Blättern mit Wasser in der Mitte und einem leuchtenden
    Blütenkolben."""
    w = _neu(seed)
    rng = w.rng
    farben = ["green_terracotta", "green_concrete", "lime_terracotta"] if stil == 0 else \
        ["purple_terracotta", "magenta_terracotta", "pink_terracotta"]
    for i in range(int(12 + 4 * s)):
        yaw = i * 2.39996
        lag = i / (12 + 4 * s)
        blatt(w, (0, 1 + lag * 2 * s, 0), yaw, (4 + 2 * (1 - lag)) * s, 1.0 * s, steig=0.9 - lag * 0.4,
              haeng=0.5, farben=farben, mitte="lime_concrete" if stil == 0 else "white_terracotta", form="lanze",
              kipp=0.0)
    r = max(1, round(0.8 * s))
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            if dx * dx + dz * dz <= r * r:
                w.setze(dx, 1 + round(s), dz, w.b("water", level=0))
    bluete = ["red_concrete", "orange_concrete", "red_concrete", "yellow_concrete"] if stil == 0 else \
        ["red_concrete", "pink_concrete", "red_concrete", "blue_concrete"]
    for y in range(round(2 * s), round(7 * s) + 2):
        w.setze(0, y, 0, w.b(bluete[y % 4]))
        if y > 3 * s:
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (y + dx + dz) % 2 == 0:
                    w.setze(dx, y, dz, w.b(bluete[(y + 1) % 4]))
    return w


def rafflesia(seed, s=1.0, stil=0):
    """Rafflesia: riesige fleischige Bodenblüte mit fünf gepunkteten Blütenblättern und einem tiefen Kelch."""
    w = _neu(seed)
    R = 5 * s + 1.5
    rot, punkt = ("red_terracotta", "white_terracotta") if stil == 0 else ("orange_terracotta", "yellow_terracotta")
    rn = Rauschen(w, 0.9)
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            d = math.hypot(x, z)
            a = math.atan2(z, x)
            blattr = R * (0.72 + 0.28 * abs(math.cos(a * 2.5)))
            if d > blattr:
                continue
            y = 1 + round(0.25 * d * (1 - d / blattr) * 2) if d > R * 0.45 else 1
            if d < R * 0.42:
                if d > R * 0.28:
                    for yy in range(1, 2 + round(1.5 * s)):
                        w.setze(x, yy, z, w.b("red_concrete" if stil == 0 else "orange_concrete"))
                else:
                    w.setze(x, 1, z, w.b("black_terracotta"))
                    if (x + z) % 2 == 0:
                        w.setze(x, 2, z, w.b("brown_terracotta"))
                continue
            blk = punkt if rn(x, 0, z) > 0.72 else rot
            w.setze(x, y, z, w.b(blk))
            if abs(math.sin(a * 5)) < 0.12 and d > R * 0.5:
                w.setze(x, y, z, w.b("brown_terracotta"))
    return w


def titanwurz(seed, s=1.0, stil=0):
    """Titanwurz: ein mannshoher gelber Kolben steckt in einem gekräuselten, außen grünen und innen purpurnen
    Hochblatt – die größte Blüte des Dschungels."""
    w = _neu(seed)
    H = _r(13 * s + 3)
    for y in range(1, H + 1):
        t = y / H
        rk = 1.6 * s * (1 - t) ** 0.6 + 0.4 if t > 0.25 else 1.0 * s + 0.4
        for x in range(-3, 4):
            for z in range(-3, 4):
                if x * x + z * z <= rk * rk:
                    w.setze(x, y, z, w.b("yellow_terracotta" if (x + y + z) % 3 else "yellow_concrete"))
    Hs = _r(H * 0.5)
    for y in range(1, Hs + 1):
        t = y / Hs
        R = (2.5 + 4.5 * s) * (0.4 + 0.6 * math.sin(t * math.pi * 0.75))
        for k in range(int(R * 8)):
            a = k / (R * 8) * 2 * math.pi
            rr = R * (1 + 0.12 * math.sin(a * 9 + y))
            x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
            innen = (stil == 0 and "purple_terracotta") or "red_terracotta"
            w.setze(x, y, z, w.b(innen if y > Hs * 0.15 and (y > Hs - 2 or (x + z) % 2) else "green_terracotta"))
            ri = rr - 1
            w.setze(round(math.cos(a) * ri), y, round(math.sin(a) * ri), w.b("magenta_terracotta" if stil == 0 else
                                                                             "red_concrete"), False)
    return w


def venusfalle(seed, s=1.0, stil=0):
    """Riesen-Venusfliegenfallen: mehrere offene Fangblätter mit roten Innenseiten und langen Zähnen auf
    kriechenden Stielen; eine hat gerade zugeschnappt."""
    w = _neu(seed)
    rng = w.rng
    for i in range(int(4 + 2 * s)):
        yaw = i * 2.39996
        d = (2.5 + 2 * rng.random()) * s
        cx, cz = math.cos(yaw) * d, math.sin(yaw) * d
        cy = 1 + (1.5 + rng.random() * 1.5) * s
        linie(w, (0, 1, 0), (cx, 1, cz), w.b("lime_terracotta"))
        linie(w, (cx, 1, cz), (cx, cy, cz), w.b("lime_terracotta"))
        offen = i % 3 != 0
        R = 2.2 * s + 0.6
        fx, fz = math.cos(yaw), math.sin(yaw)
        for seite in (-1, 1):
            winkel = (0.75 if offen else 0.15) * seite
            for a in range(-int(R * 4), int(R * 4) + 1):
                u = a / (R * 4)
                for r_ in range(1, int(R) + 2):
                    rr = r_ / (R + 1)
                    if abs(u) > math.sqrt(max(0, 1 - rr * rr)) * 1.0:
                        continue
                    lx = u * R
                    ly = math.cos(winkel) * rr * R
                    lq = math.sin(winkel) * rr * R
                    x = cx + fx * lx + (-fz) * lq
                    z = cz + fz * lx + fx * lq
                    y = cy + ly
                    w.setze(round(x), round(y), round(z), w.b("red_concrete" if r_ < R * 0.7 else "lime_concrete"))
                rr = 1.15
                ly = math.cos(winkel) * rr * R
                lq = math.sin(winkel) * rr * R
                if a % 2 == 0:
                    w.setze(round(cx + fx * u * R + (-fz) * lq), round(cy + ly + 1), round(cz + fz * u * R + fx * lq),
                            w.b("lime_concrete" if stil == 0 else "white_concrete"))
    return w


def palmfarn(seed, s=1.0, stil=0):
    """Palmfarn (Cycas): kurzer, geschuppter Stamm, eine dichte Rosette aus steifen gefiederten Wedeln und ein
    goldener Zapfen in der Mitte."""
    w = _neu(seed)
    rng = w.rng
    H = _r(3 * s + 1)
    for y in range(1, H + 1):
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                if abs(dx) + abs(dz) <= 1 + (s > 1.4):
                    w.setze(dx, y, dz, w.b("brown_terracotta" if (y + dx + dz) % 2 else "mud_bricks"))
    for i in range(int(11 + 3 * s)):
        yaw = i * 2.39996
        blatt(w, (0, H + 1, 0), yaw, (5 + 2 * rng.random()) * s, 1.4 * s, steig=1.0, haeng=0.8,
              farben=laubfarben(rng), mitte="green_terracotta",
              form="lanze", fieder=int(5 + 2 * s), kipp=0.0)
    for y in range(H + 1, H + 1 + _r(2 * s)):
        w.setze(0, y, 0, w.b("yellow_terracotta" if stil == 0 else "orange_terracotta"))
    return w


# ============================================================================ Bäume & große Pflanzen

def kapokbaum(seed, s=1.0, stil=0):
    """Kapokbaum: ein gewaltiger glatter Stamm mit Brettwurzeln wie Wände, schirmförmige Krone, Lianen und
    Epiphyten auf den Ästen."""
    w = _neu(seed)
    rng = w.rng
    H = _r(20 * s + 6)
    R = 1.6 * s + 0.8
    holz = "stripped_jungle_log" if stil == 0 else "stripped_birch_log"
    for y in range(1, H + 1):
        r = R * (1 - y / H * 0.35)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                if x * x + z * z <= r * r + 0.3:
                    w.setze(x, y, z, w.b(holz, axis="y"))
    for k in range(5 + (s > 1.2)):
        a = k / (5 + (s > 1.2)) * 2 * math.pi + rng.random() * 0.4
        L = (5 + 2 * rng.random()) * s
        hb = (5 + 2 * rng.random()) * s
        for j in range(int(L * 2) + 1):
            t = j / (L * 2)
            x, z = round(math.cos(a) * (R + t * L)), round(math.sin(a) * (R + t * L))
            for y in range(1, round(1 + hb * (1 - t) ** 1.6) + 1):
                w.setze(x, y, z, w.b(holz, axis="y"))
    top = H
    for k in range(6):
        a = k / 6 * 2 * math.pi + 0.3
        L = (8 + 3 * rng.random()) * s
        end = (math.cos(a) * L, top + 2 * s + rng.random() * 2, math.sin(a) * L)
        linie(w, (0, top - 2, 0), end, w.b("jungle_log", axis="y"), dicke=0.6 if s > 1.2 else 0)
        rk = (3 + rng.random() * 1.5) * s
        for x in range(-int(rk) - 1, int(rk) + 2):
            for z in range(-int(rk) - 1, int(rk) + 2):
                for y in range(-2, 3):
                    if (x / rk) ** 2 + (z / rk) ** 2 + (y / (1.2 * s + 0.5)) ** 2 < 1 and rng.random() < 0.9:
                        w.setze(round(end[0]) + x, round(end[1]) + y, round(end[2]) + z,
                                _lv(w, "jungle" if (x + z) % 4 else "oak"), False)
        if k % 2 == 0:
            for d in range(_r(6 * s)):
                p = (round(end[0] * 0.6), round(end[1] - 2 - d), round(end[2] * 0.6))
                w.setze(*p, w.b("vine", north=True, south=False, east=False, west=False, up=False), False)
    for k in range(int(6 * s)):
        y = round(H * 0.4 + rng.random() * H * 0.5)
        a = rng.random() * 6.28
        r = R * (1 - y / H * 0.35) + 1
        w.setze(round(math.cos(a) * r), y, round(math.sin(a) * r), w.b(["moss_block", "fern", "moss_block"][k % 3]),
                False)
    return w


def wuergefeige(seed, s=1.0, stil=0):
    """Würgefeige: ein Netz aus Luftwurzeln umschlingt eine alte Tempelsäule, oben eine dichte Krone, unten
    Moos und eingestürzte Steinblöcke."""
    w = _neu(seed)
    rng = w.rng
    H = _r(14 * s + 4)
    R = 1.5 * s + 1
    stein = ["mossy_stone_bricks", "cracked_stone_bricks", "stone_bricks", "mossy_cobblestone", "chiseled_stone_bricks"]
    for y in range(1, round(H * 0.8)):
        for x in range(-int(R), int(R) + 1):
            for z in range(-int(R), int(R) + 1):
                if x * x + z * z <= R * R:
                    w.setze(x, y, z, w.b(stein[(x * 3 + y + z * 7) % 5]))
    for k in range(int(9 + 4 * s)):
        a0 = k / (9 + 4 * s) * 2 * math.pi
        dr = 1 if k % 2 else -1
        pts = []
        for j in range(H + 1):
            t = j / H
            a = a0 + dr * t * 2.2
            r = R + 0.8 + (1 - t) ** 3 * 3 * s
            pts.append((math.cos(a) * r, 1 + j, math.sin(a) * r))
        for p, q in zip(pts, pts[1:]):
            linie(w, p, q, w.b("jungle_wood", axis="y") if stil == 0 else w.b("mangrove_wood", axis="y"))
    for x in range(-int(6 * s) - 1, int(6 * s) + 2):
        for z in range(-int(6 * s) - 1, int(6 * s) + 2):
            for y in range(-2, 4):
                if (x / (6 * s + 1)) ** 2 + (z / (6 * s + 1)) ** 2 + (y / (2.5 * s + 1)) ** 2 < 1 and \
                        rng.random() < 0.88:
                    w.setze(x, H + 1 + y, z, _lv(w, "jungle"), False)
    for k in range(int(3 + 2 * s)):
        a = rng.random() * 6.28
        d = R + 2 + rng.random() * 3 * s
        w.setze(round(math.cos(a) * d), 1, round(math.sin(a) * d), w.b(stein[k % 5]))
    return w


def mangroven(seed, s=1.0, stil=0):
    """Mangroveninsel: Mangroven auf hohen Stelzwurzeln im flachen Wasser, Schlamm, hängende Wurzeln und
    Moos."""
    w = _neu(seed)
    rng = w.rng
    R = 7 * s + 3
    for x in range(-int(R) - 2, int(R) + 3):
        for z in range(-int(R) - 2, int(R) + 3):
            if x * x + z * z <= (R + 2) ** 2:
                w.setze(x, 0, z, w.b("water", level=0) if (x * x + z * z) > (R * 0.4) ** 2 else w.b("mud"))
                w.setze(x, -1, z, w.b("mud"))
    for i in range(int(2 + 2 * s)):
        a = i * 2.39996
        d = R * 0.5 * math.sqrt((i + 0.5) / (2 + 2 * s))
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        H = _r((7 + 3 * rng.random()) * s)
        y0 = _r(3 * s)
        for k in range(int(5 + 2 * s)):
            aa = k / (5 + 2 * s) * 6.28
            rr = (2 + rng.random()) * s
            bogen(w, (cx + math.cos(aa) * rr, -1, cz + math.sin(aa) * rr), (cx, y0, cz), 1.2,
                  w.b("mangrove_roots", waterlogged=False))
        for y in range(y0, y0 + H):
            w.setze(cx, y, cz, w.b("mangrove_log", axis="y"))
        rk = 3 * s + 1.5
        for x in range(-int(rk) - 1, int(rk) + 2):
            for z in range(-int(rk) - 1, int(rk) + 2):
                for y in range(-2, 3):
                    if (x / rk) ** 2 + (z / rk) ** 2 + (y / (1.6 * s + 0.6)) ** 2 < 1 and rng.random() < 0.85:
                        w.setze(cx + x, y0 + H + y, cz + z, w.b("mangrove_leaves", persistent=True, distance=1,
                                                                waterlogged=False), False)
        for k in range(int(3 * s)):
            x, z = cx + int(rng.integers(-2, 3)), cz + int(rng.integers(-2, 3))
            for d in range(_r(3 * s)):
                w.setze(x, y0 + H - 2 - d, z, w.b("hanging_roots", waterlogged=False), False)
    return w


def kakaogarten(seed, s=1.0, stil=0):
    """Kakaobäume: kleine Bäume, an deren Stämmen die Kakaofrüchte hängen, dazwischen Kaffeesträucher mit roten
    Beeren und Bananenblätter."""
    w = _neu(seed)
    rng = w.rng
    n = int(3 + 2 * s)
    for i in range(n):
        a = i * 2.39996
        d = 4 * s * math.sqrt((i + 0.5) / n)
        cx, cz = round(math.cos(a) * d), round(math.sin(a) * d)
        H = _r((5 + 2 * rng.random()) * s)
        for y in range(1, H + 1):
            w.setze(cx, y, cz, w.b("jungle_log", axis="y"))
            if 2 <= y <= H - 1 and y % 2 == 0:
                for f, (dx, dz) in (("south", (0, -1)), ("north", (0, 1)), ("east", (-1, 0)), ("west", (1, 0))):
                    if rng.random() < 0.45:
                        w.setze(cx + dx, y, cz + dz, w.b("cocoa", age=int(rng.integers(1, 3)), facing=f), False)
        rk = 2.2 * s + 1
        for x in range(-int(rk) - 1, int(rk) + 2):
            for z in range(-int(rk) - 1, int(rk) + 2):
                for y in range(-1, 3):
                    if (x / rk) ** 2 + (z / rk) ** 2 + (y / 1.6) ** 2 < 1 and rng.random() < 0.85:
                        w.setze(cx + x, H + 1 + y, cz + z, _lv(w, "jungle"), False)
    for k in range(int(6 * s)):
        a = rng.random() * 6.28
        d = (2 + rng.random() * 4) * s
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        w.setze(x, 1, z, w.b("sweet_berry_bush", age=3), False)
        w.setze(x, 2, z, _lv(w, "azalea"), False)
    return w


def bambushain(seed, s=1.0, stil=0):
    """Bambushain: dicht stehender Riesenbambus mit dicken Halmen, Knoten und Blattbüscheln, dazwischen junge
    Schösslinge."""
    w = _neu(seed)
    rng = w.rng
    R = 5 * s + 2
    for i in range(int(18 * s * s + 8)):
        a = rng.random() * 6.28
        d = R * math.sqrt(rng.random())
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        if (x, 1, z) in w.bloecke:
            continue
        if rng.random() < 0.55:
            H = _r((10 + 6 * rng.random()) * s)
            for y in range(1, H + 1):
                w.setze(x, y, z, w.b("bamboo_block", axis="y") if stil == 0 and y % 5 else
                        w.b("stripped_bamboo_block", axis="y") if y % 5 else w.b("bamboo_planks"))
            for k in range(_r(3 * s)):
                yy = H - k * 2
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if rng.random() < 0.6:
                        w.setze(x + dx, yy, z + dz, _lv(w, "azalea" if stil else "jungle"), False)
        else:
            h = int(4 + rng.integers(int(6 * s) + 2))
            for k in range(h):
                blatt_ = "large" if k >= h - 2 else ("small" if k >= h - 4 else "none")
                w.setze(x, 1 + k, z, w.b("bamboo", age=1, leaves=blatt_, stage=0))
    return w


def lianenvorhang(seed, s=1.0, stil=0):
    """Lianenvorhang: zwei Urwaldbäume, zwischen denen ein dichter Vorhang aus Lianen, Leuchtbeeren und
    hängenden Wurzeln niederfällt."""
    w = _neu(seed)
    rng = w.rng
    D = _r(7 * s + 3)
    for sx in (-1, 1):
        b = wald2.laubbaum(int(rng.integers(1, 10 ** 6)), "jungle", H=_r(12 * s + 5),
                           blaetter=[("jungle", 1)], breit=0.8)
        from lib import einfuegen
        einfuegen(w, b, sx * D, 0, 0)
    H = _r(11 * s + 4)
    for x in range(-D + 1, D):
        top = H + round(math.sin((x + D) / (2 * D) * math.pi) * 1.5)
        for z in (-1, 0, 1):
            w.setze(x, top, z, _lv(w, "jungle"), False)
        laenge = int((3 + rng.random() * (H - 3)) * (0.5 + 0.5 * abs(math.sin(x * 0.7))))
        for d in range(laenge):
            y = top - 1 - d
            if y < 1:
                break
            if stil == 1 and d == laenge - 1:
                w.setze(x, y, 0, w.b("cave_vines", age=0, berries=True), False)
            elif stil == 1:
                w.setze(x, y, 0, w.b("cave_vines_plant", berries=(d % 3 == 0)), False)
            else:
                w.setze(x, y, 0, w.b("vine", north=True, south=False, east=False, west=False, up=False), False)
    return w


def wurzelbruecke(seed, s=1.0, stil=0):
    """Lebende Wurzelbrücke: zwei Feigenbäume an den Ufern eines Bachs, deren verflochtene Wurzeln eine
    begehbare Brücke mit Geländer bilden, darunter Steine und Farne."""
    w = _neu(seed)
    rng = w.rng
    L = _r(8 * s + 4)
    for x in range(-L - 3, L + 4):
        for z in range(-_r(2 * s + 1), _r(2 * s + 1) + 1):
            if abs(x) < L * 0.6 + math.sin(z) * 0.5:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel") if (x + z) % 3 else w.b("mossy_cobblestone"))
    for sx in (-1, 1):
        cx = sx * (L + 1)
        H = _r(10 * s + 4)
        for y in range(1, H + 1):
            for dx, dz in ((0, 0), (1, 0), (0, 1), (1, 1)) if s > 1.2 else ((0, 0),):
                w.setze(cx + dx, y, dz, w.b("jungle_log", axis="y"))
        rk = 4 * s + 1
        for x in range(-int(rk) - 1, int(rk) + 2):
            for z in range(-int(rk) - 1, int(rk) + 2):
                for y in range(-2, 3):
                    if (x / rk) ** 2 + (z / rk) ** 2 + (y / 2) ** 2 < 1 and rng.random() < 0.85:
                        w.setze(cx + x, H + y, z, _lv(w, "jungle"), False)
    for zr in (-1, 0, 1):
        pts = bogen(w, (-L - 1, 2, zr), (L + 1, 2, zr), 1.0 * s, w.b("mangrove_roots", waterlogged=False), n=16)
    for zr in (-2, 2):
        bogen(w, (-L - 1, 4, zr), (L + 1, 4, zr), 1.0 * s, w.b("mangrove_roots", waterlogged=False), n=16)
        for x in range(-L, L + 1, 3):
            t = (x + L + 1) / (2 * L + 2)
            yb = round(2 + 4 * t * (1 - t) * s)
            linie(w, (x, yb, zr), (x, yb + 2, zr), w.b("jungle_wood", axis="y"))
    for x in range(-L, L + 1):
        t = (x + L + 1) / (2 * L + 2)
        yb = round(2 + 4 * t * (1 - t) * s)
        for zr in (-1, 0, 1):
            if rng.random() < 0.3:
                w.setze(x, yb + 1, zr, w.b("moss_carpet"), False)
    return w


def riesenseerosen(seed, s=1.0, stil=0):
    """Riesenseerosen-Teich: tellergroße bis riesige Blätter mit hochgebogenem Rand (Victoria), weiße und rosa
    Blüten, Schilf am Ufer."""
    w = _neu(seed)
    rng = w.rng
    R = 8 * s + 4
    rn = Rauschen(w, 3)
    for x in range(-int(R) - 3, int(R) + 4):
        for z in range(-int(R) - 3, int(R) + 4):
            d = math.hypot(x, z) / (R * (0.85 + 0.3 * rn(x, 0, z)))
            if d < 1:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("mud") if (x + z) % 3 else w.b("clay"))
            elif d < 1.25:
                w.setze(x, 0, z, w.b("grass_block", snowy=False) if d > 1.08 else w.b("mud"))
                if d < 1.15 and rng.random() < 0.5:
                    w.setze(x, 1, z, w.b("sugar_cane", age=0))
                    w.setze(x, 2, z, w.b("sugar_cane", age=0))
    belegt = []
    for i in range(int(4 + 4 * s)):
        a = rng.random() * 6.28
        d = R * 0.7 * math.sqrt(rng.random())
        cx, cz = math.cos(a) * d, math.sin(a) * d
        rr = (1.6 + 1.6 * rng.random()) * s + 0.8
        if any(math.hypot(cx - bx, cz - bz) < rr + br for bx, bz, br in belegt):
            continue
        belegt.append((cx, cz, rr))
        for x in range(int(cx - rr) - 1, int(cx + rr) + 2):
            for z in range(int(cz - rr) - 1, int(cz + rr) + 2):
                d2 = math.hypot(x - cx, z - cz)
                if d2 <= rr:
                    schlitz = abs(math.atan2(z - cz, x - cx) - a) < 0.12
                    if schlitz:
                        continue
                    if d2 > rr - 0.9 and rr > 2:
                        w.setze(x, 1, z, w.b("red_terracotta" if stil == 0 else "lime_terracotta"))
                    w.setze(x, 0, z, w.b("lime_concrete" if (x + z) % 5 == 0 else "green_concrete"))
        if i % 2 == 0:
            fx, fz = round(cx + rr * 0.3), round(cz)
            w.setze(fx, 1, fz, w.b("white_concrete" if (i // 2) % 2 else "pink_concrete"))
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                w.setze(fx + dx, 1, fz + dz, w.b("white_wool" if (i // 2) % 2 else "pink_wool"))
            w.setze(fx, 2, fz, w.b("yellow_concrete"))
    return w


def bunte_blaetter(seed, s=1.0, stil=0):
    """Bunte Blattpflanzen: ein Beet aus Croton, Buntblatt und Kaladien mit roten, gelben, rosa und weiß
    gemusterten Blättern."""
    w = _neu(seed)
    rng = w.rng
    paletten = [["red_terracotta", "orange_concrete", "yellow_concrete", "green_terracotta"],
                ["pink_concrete", "white_concrete", "green_concrete", "pink_terracotta"],
                ["yellow_concrete", "lime_concrete", "green_terracotta", "yellow_terracotta"],
                ["magenta_terracotta", "purple_concrete", "pink_concrete", "green_terracotta"],
                ["white_terracotta", "green_concrete", "white_concrete", "lime_concrete"]]
    n = int(5 + 5 * s)
    for i in range(n):
        a = i * 2.39996
        d = 4.5 * s * math.sqrt((i + 0.5) / n)
        cx, cz = math.cos(a) * d, math.sin(a) * d
        pal = paletten[(i + stil * 2) % len(paletten)]
        for k in range(int(4 + 2 * s)):
            yaw = k * 2.39996 + i
            b = (cx, 1 + (1 + rng.random() * 1.5) * s, cz)
            linie(w, (cx, 1, cz), b, w.b("green_terracotta"))
            blatt(w, b, yaw, (2.5 + rng.random() * 1.5) * s, 1.1 * s, steig=0.4, haeng=0.5, farben=pal,
                  mitte=pal[0], form="herz", kipp=0.1, rand=pal[-1])
    return w


def orchideenast(seed, s=1.0, stil=0):
    """Orchideenast: ein umgestürzter, moosbewachsener Urwaldstamm voller Orchideen, Bromelien, Farne und
    Pilze."""
    w = _neu(seed)
    rng = w.rng
    L = _r(12 * s + 4)
    R = 1.2 * s + 0.6
    for x in range(-L, L + 1):
        yc = 1 + R + math.sin(x / L * 1.2) * 0.8
        for y in range(0, int(yc + R) + 2):
            for z in range(-int(R) - 1, int(R) + 2):
                if (y - yc) ** 2 + z * z <= R * R + 0.3 and y >= 1:
                    w.setze(x, y, z, w.b("jungle_log", axis="x") if (x + y) % 5 else w.b("mossy_cobblestone"))
        top = round(yc + R) + 1
        r = rng.random()
        if r < 0.25:
            w.setze(x, top, 0, w.b("moss_carpet"))
        elif r < 0.45:
            w.setze(x, top, 0, w.b(["blue_orchid", "allium", "pink_tulip", "azure_bluet"][int(rng.integers(4))]))
        elif r < 0.55:
            w.setze(x, top, 0, w.b("fern"))
        elif r < 0.6:
            w.setze(x, top, 0, w.b("red_mushroom"))
    for k in range(int(3 * s)):
        x = int(rng.integers(-L + 2, L - 1))
        b = bromelie(int(rng.integers(1, 10 ** 6)), 0.45 * s + 0.2, stil)
        from lib import einfuegen
        einfuegen(w, b, x, round(1 + 2 * R) - 1, 0)
    rd = _r(3 * s + 1)
    for y in range(0, 2 * rd + 1):
        for z in range(-rd, rd + 1):
            if (y - rd) ** 2 + z * z <= rd * rd:
                w.setze(-L - 1, y, z, w.b("rooted_dirt") if (y + z) % 3 else w.b("jungle_wood", axis="x"))
    return w


# ============================================================================ Dschungelstücke (kombinierbar)

def _pflanze_zufall(st, s, mit_baum=True):
    def wahl(x, z, rd, art):
        r = st.rng.random()
        sd = int(st.rng.integers(1, 10 ** 7))
        k = s * (0.6 + 0.5 * st.rng.random())
        if mit_baum and r < 0.07:
            H = int(16 + st.rng.integers(6) + st.g * 3)
            return wald2.dschungelriese(sd, H=H), wald2.kronen_r(H, 1.1) * 1.5
        if r < 0.32:
            return monstera(sd, k, st.stil), 5 * k
        if r < 0.45:
            return elefantenohr(sd, k, st.stil), 5 * k
        if r < 0.56:
            return bananenstaude(sd, k, st.stil), 5 * k
        if r < 0.68:
            return baumfarn(sd, k, st.stil), 5 * k
        if r < 0.76:
            return heliconie(sd, k * 0.8, st.stil), 4 * k
        if r < 0.84:
            return palmfarn(sd, k * 0.8, st.stil), 3.5 * k
        if r < 0.92:
            return bromelie(sd, k * 0.6, st.stil), 2.5 * k
        return strelitzie(sd, k * 0.7, st.stil), 3 * k
    return wahl


def dschungelstueck(seed, g=1):
    """Dschungelstück: dicht an dicht Riesenmonstera, Elefantenohren, Bananen, Baumfarne und einzelne
    Urwaldriesen über Farnen und Moos – lässt sich nahtlos aneinandersetzen."""
    st = Stueck(seed, g)
    _verteile(st, _pflanze_zufall(st, 0.8 + 0.15 * g), 5, 300)
    boden_dschungel(st, 0.7)
    return st


def _verteile(st, f, abstand, menge):
    st.verteile(abstand, int(menge * (st.g + 1) ** 2), f)


def dschungelpfad(seed, g=1):
    """Dschungelpfad: ein schlammiger Pfad mit Wurzeln, Trittsteinen und Pfützen windet sich durch mannshohe
    Blätter und Farne."""
    st = Stueck(seed, g)
    pts = wald2.wegpunkte(st, "kurve", 2.2)
    for x, z in pts:
        st.plaetze.append((x, z, 3.2))
    _verteile(st, _pflanze_zufall(st, 0.7 + 0.12 * g), 5, 280)
    wald2.weg(st, pts, breite=2.2, belag="matsch", pfuetzen=0.12, trittsteine=True, wurzelquer=0.08)
    boden_dschungel(st, 0.75, nass=True)
    return st


def dschungellichtung(seed, g=1):
    """Dschungellichtung: in der Mitte eine sonnige Wiese mit Blüten, Strelitzien und Rafflesia, ringsum ein
    Wall aus Riesenpflanzen und Urwaldriesen."""
    st = Stueck(seed, g)
    s = 0.8 + 0.15 * g
    for k in range(1 + g // 2):
        a = st.rng.random() * 6.28
        st.stempel(rafflesia(int(st.rng.integers(1, 10 ** 6)), 0.5 * s, st.stil),
                   round(math.cos(a) * st.R * 0.2), round(math.sin(a) * st.R * 0.2))
    st.plaetze.append((0, 0, st.R * 0.45))
    st.verteile(5, int(280 * (st.g + 1) ** 2), _pflanze_zufall(st, s), rand_min=0.45)
    st.boden([("grass_block_s", 6), ("moss_block", 1), ("podzol", 1)],
             [("grass", 4), (hohes("tall_grass"), 2), ("blue_orchid", 1), ("allium", 0.6), ("pink_tulip", 0.5),
              ("fern", 2), (hohes("peony"), 0.4), (hohes("rose_bush"), 0.4)], dichte=0.6)
    return st


def dschungelbach(seed, g=1):
    """Dschungelbach: ein klarer Bach mit Steinen und Seerosen, überhangen von Riesenblättern, Baumfarnen und
    Bambus an den Ufern."""
    st = Stueck(seed, g)
    pts = wald2.wegpunkte(st, "kurve", 2.0)
    for x, z in pts:
        st.plaetze.append((x, z, 3.0 + st.g))
    _verteile(st, _pflanze_zufall(st, 0.75 + 0.12 * g), 5, 260)
    wald2.bach(st, pts, breite=1.6 + 0.5 * st.g)
    for (x, y, z), b in list(st.w.bloecke.items()):
        if y == 0 and st.w.P.name(b) == "minecraft:water" and st.rng.random() < 0.05 and st.w.frei(x, 1, z):
            st.w.setze(x, 1, z, st.w.b("lily_pad"))
    boden_dschungel(st, 0.7, nass=True)
    return st


def _stueck_wrap(f):
    def g(seed, groesse=1):
        st = f(seed, groesse)
        return _fertig(st.w if isinstance(st, Stueck) else st)
    g.__doc__ = f.__doc__
    return g


FLORA = {k: (n, f) for k, (n, f) in {
    "monstera": ("Riesen-Monstera", einzeln(monstera)),
    "elefantenohr": ("Elefantenohr", einzeln(elefantenohr)),
    "bananenstaude": ("Bananenstaude", einzeln(bananenstaude)),
    "baumfarn": ("Baumfarn", einzeln(baumfarn)),
    "strelitzie": ("Paradiesvogelblume", einzeln(strelitzie)),
    "heliconie": ("Hummerschere", einzeln(heliconie)),
    "kannenpflanze": ("Kannenpflanze", einzeln(kannenpflanze)),
    "bromelie": ("Riesen-Bromelie", einzeln(bromelie)),
    "rafflesia": ("Rafflesia", einzeln(rafflesia, dichte=0.3)),
    "titanwurz": ("Titanwurz", einzeln(titanwurz)),
    "venusfalle": ("Venusfliegenfallen", einzeln(venusfalle)),
    "palmfarn": ("Palmfarn", einzeln(palmfarn)),
    "kapokbaum": ("Kapokbaum", einzeln(kapokbaum)),
    "wuergefeige": ("Würgefeige", einzeln(wuergefeige)),
    "mangroven": ("Mangroveninsel", einzeln(mangroven, R_extra=1, dichte=0.2)),
    "kakaogarten": ("Kakaobäume", einzeln(kakaogarten)),
    "bambushain": ("Riesenbambus", einzeln(bambushain)),
    "lianenvorhang": ("Lianenvorhang", einzeln(lianenvorhang)),
    "wurzelbruecke": ("Wurzelbrücke", einzeln(wurzelbruecke)),
    "riesenseerosen": ("Riesenseerosen", einzeln(riesenseerosen, R_extra=1, dichte=0.2)),
    "bunte_blaetter": ("Bunte Blattpflanzen", einzeln(bunte_blaetter)),
    "orchideenast": ("Orchideenast", einzeln(orchideenast)),
    "dschungelstueck": ("Dschungelstück", _stueck_wrap(dschungelstueck)),
    "dschungelpfad": ("Dschungelpfad", _stueck_wrap(dschungelpfad)),
    "dschungellichtung": ("Dschungellichtung", _stueck_wrap(dschungellichtung)),
    "dschungelbach": ("Dschungelbach", _stueck_wrap(dschungelbach)),
}.items()}

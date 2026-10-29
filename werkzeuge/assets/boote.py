"""Boote & Schiffe – Paket. Wasserlinie bei y = 0 (Vorlage auf die Wasseroberfläche setzen).
Größen 0 klein · 1 mittel · 2 riesig · 3 gigantisch, je zwei Stile."""

from __future__ import annotations

import math

import numpy as np

from lib import Verlauf, Welt, laub
from riesenbogen import zahnrad
from schiffe import dreieckssegel, flagge, mast, segel
from skulptur import Skulptur, ell, kap, kasten, kreisrand, platte, scheibe, treppe, verbinde

U = [0.6, 1.0, 1.7, 2.8]


def _welt(seed):
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


def _zaun(w, mat):
    return w.b(mat, north=False, south=False, east=False, west=False, waterlogged=False)


# ============================================================================ Rumpf (allgemein)

def rumpf2(w, L, B, D, F, mat, form="normal", achter=0, vorn=0, enden=0.0, sheer=0.12, kanonen=False,
           heckfenster=False, reling=True, offen=False, y0=0):
    """Rumpf entlang x (Bug +x), Wasserlinie y0.
    form: normal (spitzer Bug, breites Heck) · spitz (beide Enden spitz) · flach (Kahn / Raddampfer).
    enden: wie hoch Bug und Heck aufsteigen (Langschiff, Gondel). offen: kein Deck (Ruderboot)."""
    half = L / 2

    def kiel(x):
        uu = x / half
        if form == "spitz":
            return -D + 0.85 * D * np.clip((np.abs(uu) - 0.5) / 0.5, 0, 1) ** 2
        if form == "flach":
            return -D + 0.6 * D * np.clip((np.abs(uu) - 0.8) / 0.2, 0, 1)
        return -D + 0.9 * D * np.clip((uu - 0.45) / 0.55, 0, 1) ** 2 + 0.3 * D * np.clip((-uu - 0.8) / 0.2, 0, 1)

    def deck_haupt(x):
        uu = x / half
        return F + sheer * F * uu ** 2 + enden * np.clip((np.abs(uu) - 0.6) / 0.4, 0, 1) ** 2

    def deck_oben(x):
        uu = x / half
        return deck_haupt(x) + achter * (uu < -0.5) + vorn * (uu > 0.62)

    def halbbreite(x, y):
        uu = np.clip(x / half, -1, 1)
        if form == "spitz":
            px = np.clip(1 - np.abs(uu) ** 2, 0, 1) ** 0.6
        elif form == "flach":
            px = np.clip(1 - np.abs(uu) ** 8, 0, 1) ** 0.5
        else:
            px = np.where(uu >= 0, np.clip(1 - np.abs(uu) ** 2.2, 0, 1) ** 0.6,
                          np.clip(1 - np.abs(uu) ** 6, 0, 1) ** 0.5)
        v = (y - kiel(x)) / np.maximum(F + sheer * F * uu ** 2 - kiel(x), 0.5)
        if form == "flach":
            py = np.where(v < 1, np.clip(v, 0, 1) ** 0.15, 1 - 0.08 * (v - 1))
        else:
            py = np.where(v < 0.8, np.clip(v, 0, 1) ** 0.45, 0.8 ** 0.45 - 0.22 * (v - 0.8))
        return B * px * np.maximum(py, 0.12 if enden else 0)

    n = int(half) + 2
    ymax = int(F * (1 + sheer) + enden + max(achter, vorn)) + 2
    X, Y, Z = np.mgrid[-n:n + 1, -int(D) - 2:ymax + 1, -int(B) - 2:int(B) + 3]
    Xf = X.astype(float)
    fest = (Y >= kiel(Xf)) & (Y <= np.round(deck_oben(Xf))) & (np.abs(Z) <= halbbreite(Xf, Y.astype(float)) + 0.3) \
        & (np.abs(Xf) <= half)
    ox, oy, oz = X[0, 0, 0], Y[0, 0, 0], Z[0, 0, 0]
    idx = {tuple(p) for p in np.argwhere(fest)}

    def drin(x, y, z):
        return (x - ox, y - oy, z - oz) in idx

    gp = _r(F * 0.5, 1)
    rail, oben_punkte = [], []
    for i, j, k in idx:
        x, y, z = int(i + ox), int(j + oy), int(k + oz)
        oben = not drin(x, y + 1, z)
        seite = not (drin(x + 1, y, z) and drin(x - 1, y, z) and drin(x, y, z + 1) and drin(x, y, z - 1))
        unten = not drin(x, y - 1, z)
        dh = int(round(float(deck_haupt(x))))
        heck = not drin(x - 1, y, z)
        if oben:
            if seite:
                blk = w.b("gold_block") if heck and y > dh and mat.get("gold", True) else w.b(mat["leiste"], axis="x")
                if reling:
                    rail.append((x, y + 1 + y0, z))
            elif offen and y > int(kiel(x)) + 1:
                continue
            else:
                blk = mat["deck"](1 + 0.8 * math.sin(z * 1.7) + w.rng.random() * 0.6, x, y, z)
            oben_punkte.append((x, y, z))
        elif seite or unten:
            if y < 0:
                blk = mat["unten"](1.2 + y / max(1, D) + w.rng.random() * 0.5, x, y, z)
            elif (y == 0 or y == gp + 1) and mat.get("leiste"):
                blk = w.b(mat["leiste"], axis="x")
            elif y == gp and mat.get("streifen") and abs(x) < half * 0.75:
                blk = w.b("black_terracotta") if kanonen and x % 3 == 0 and F >= 4 else w.b(mat["streifen"])
            elif heckfenster and heck and y > dh and z % 2 == 0:
                blk = w.b(mat.get("fenster", "yellow_stained_glass"))
                w.setze(x + 1, y + y0, z, w.b("shroomlight"))
            else:
                blk = mat["wand"](1 + 1.5 * y / max(1, F) + w.rng.random() * 0.4, x, y, z)
        elif offen:
            continue
        elif y == dh:
            blk = mat["deck"](1.0, x, y, z)
        else:
            continue
        w.setze(x, y + y0, z, blk, ueberschreiben=False)
    if rail:
        verbinde(w, rail, mat["zaun"])
    return dict(half=half, deck_haupt=deck_haupt, deck_oben=deck_oben, kiel=kiel, oben=oben_punkte, B=B)


def _dh(r, x):
    return int(round(float(r["deck_oben"](x))))


def _holz(w, art="dark_oak", wand=None, streifen=None, deck="spruce", zaun=None, unten=None):
    return dict(unten=Verlauf(w, "Rumpf", unten or [f"{art}_planks", f"{art}_planks", "spruce_planks"]),
                wand=Verlauf(w, "Wand", wand or [f"{art}_planks", "spruce_planks", f"stripped_{art}_log"]),
                streifen=streifen, leiste=f"stripped_{art}_log", zaun=zaun or f"{art}_fence",
                deck=Verlauf(w, "Deck", [f"{deck}_planks", "oak_planks", f"stripped_{deck}_log"]),
                fenster="yellow_stained_glass")


def _ruder(w, r, xs, F, B, lang, holz="spruce_fence"):
    for x in xs:
        for s in (-1, 1):
            hb = int(r["B"] * max(0.2, 1 - (2 * x / (2 * r["half"])) ** 2) ** 0.5) + 1
            for k in range(lang):
                w.setze(x, int(F) - k // 2, s * (hb + k), _zaun(w, holz), ueberschreiben=False)


def _rahsegel_mast(w, xm, y0, h, B, tuch, stufen=(0.4, 0.75), wappen=None, bauch=1.5, dick=False, flaggen=None):
    mast(w, xm, y0 - 1, h + 1, dick)
    rahen = [y0 + int(h * f) for f in stufen]
    unten = y0 + 2
    for k, yr in enumerate(rahen):
        hz = int(B * (1.6 - 0.35 * k))
        for z in range(-hz, hz + 1):
            w.setze(xm + 1, yr, z, w.b("spruce_log", axis="z"))
        y_u = unten if k == 0 else rahen[k - 1] + 1
        hz_u = (B * (1.6 - 0.35 * (k - 1)) if k else B * 1.65) - 1
        segel(w, xm + 1, yr - 1, y_u, hz - 1, hz_u, bauch, tuch, wappen if k == 0 else None)
    if flaggen:
        flagge(w, xm, y0 + h + 2, 0, max(2, int(B)), flaggen)
        for k in range(2):
            w.setze(xm, y0 + h + k, 0, _zaun(w, "spruce_fence"))


# ============================================================================ Ruderboot

def ruderboot(seed, g=1):
    """Kleines offenes Ruderboot mit Sitzbänken, Riemen, Laterne und Tau-Rolle."""
    w = _welt(seed)
    u = U[g] * 0.55
    art = "oak" if _stil(seed) == 0 else "dark_oak"
    mat = _holz(w, art, streifen=None, deck=art,
                wand=["blue_terracotta", "light_blue_terracotta", "white_terracotta"] if _stil(seed) == 0 else None)
    L, B, D, F = 12 * u + 5, 2.2 * u + 1.2, 1 * u + 0.6, 1.2 * u + 0.8
    r = rumpf2(w, L, B, D, F, mat, form="spitz", enden=0.8 * u, reling=False, offen=True)
    for x in range(-int(L * 0.3), int(L * 0.3) + 1, _r(3 * u, 2)):
        hb = int(B * 0.8)
        for z in range(-hb, hb + 1):
            w.setze(x, int(F) - 1 if F > 1.5 else 0, z, platte(w, art), ueberschreiben=False)
    _ruder(w, r, [0], F, B, _r(3 * u, 2))
    xh = -int(L / 2) + 1
    w.setze(xh, _dh(r, xh) + 1, 0, _zaun(w, f"{art}_fence"))
    w.setze(xh, _dh(r, xh) + 2, 0, w.b("lantern", hanging=False, waterlogged=False))
    w.setze(int(L * 0.25), 0, 0, w.b("barrel", facing="up", open=False))
    return w


# ============================================================================ Fischerboot

def fischerboot(seed, g=1):
    """Fischkutter mit Ruderhaus, Gaffelsegel, Netzbaum mit hängendem Netz, Fässern und Laternen."""
    w = _welt(seed)
    u = U[g] * 0.8
    farbe = ["red_terracotta", "red_concrete", "white_terracotta"] if _stil(seed) == 0 else \
        ["cyan_terracotta", "light_blue_terracotta", "white_terracotta"]
    mat = _holz(w, "spruce", wand=farbe, streifen="white_concrete", deck="oak")
    L, B, D, F = 18 * u + 6, 3 * u + 1.2, 1.6 * u + 1, 2 * u + 1
    r = rumpf2(w, L, B, D, F, mat, sheer=0.2)
    # Ruderhaus
    x0, x1 = -int(L * 0.38), -int(L * 0.12)
    hz = max(1, int(B * 0.6))
    yb = _dh(r, 0) + 1
    hh = _r(2.5 * u, 2)
    for x in range(x0, x1 + 1):
        for z in range(-hz, hz + 1):
            for y in range(yb, yb + hh):
                if x in (x0, x1) or abs(z) == hz:
                    glas = y == yb + hh - 1 and not (x in (x0, x1) and abs(z) == hz)
                    w.setze(x, y, z, w.b("glass") if glas else w.b("white_concrete" if _stil(seed) == 0 else
                                                                      "white_terracotta"))
            w.setze(x, yb + hh, z, w.b(farbe[0]))
    w.setze(x1, yb + hh + 1, 0, w.b("lantern", hanging=False, waterlogged=False))
    for y in range(yb + hh + 1, yb + hh + _r(2 * u, 2) + 1):
        w.setze(x0 + 1, y, hz, w.b("bricks"))
    w.setze(x0 + 1, yb + hh + _r(2 * u, 2) + 1, hz, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                                         waterlogged=False))
    # Mast mit Gaffelsegel
    xm = int(L * 0.18)
    hm = _r(12 * u, 6)
    mast(w, xm, yb - 1, hm + 1, False)
    dreieckssegel(w, (xm - 1, yb + hm - 1), (xm - 1, yb + 2), (xm - int(L * 0.3), yb + 2), 0,
                  w.b("white_wool" if _stil(seed) == 0 else "light_gray_wool"))
    flagge(w, xm, yb + hm + 1, 0, 2, ["red_wool", "white_wool"] if _stil(seed) == 0 else ["blue_wool", "yellow_wool"])
    # Netzbaum mit Netz
    nz = int(B) + _r(3 * u, 2)
    for z in range(0, nz + 1):
        w.setze(xm, yb + _r(3 * u, 2), z, w.b("spruce_log", axis="z"))
    for y in range(1, yb + _r(3 * u, 2)):
        for x in (xm - 1, xm, xm + 1):
            if w.rng.random() < 0.75:
                w.setze(x, y, nz, w.b("cobweb"))
    for x, y, z in r["oben"]:
        if w.rng.random() < 0.05 and abs(z) < B - 1.5 and abs(x - xm) > 1 and not (x0 <= x <= x1):
            w.setze(x, y + 1, z, w.b("barrel", facing="up", open=False))
    xb = int(L / 2) - 1
    w.setze(xb, _dh(r, xb) + 1, 0, w.b("lantern", hanging=False, waterlogged=False))
    return w


# ============================================================================ Langschiff

def langschiff(seed, g=1):
    """Nordisches Langschiff: hoch geschwungener Steven mit Drachenkopf, Schildreihe, gestreiftes Rahsegel,
    Riemen auf beiden Seiten und eingerolltes Heck."""
    w = _welt(seed)
    u = U[g]
    mat = _holz(w, "spruce" if _stil(seed) == 0 else "dark_oak", streifen=None, deck="spruce")
    mat["gold"] = False
    L, B, D, F = 26 * u + 7, 3 * u + 1, 1.4 * u + 1, 1.8 * u + 1
    en = 4 * u + 2
    r = rumpf2(w, L, B, D, F, mat, form="spitz", enden=en, sheer=0.05)
    half = r["half"]
    farben = ["red_concrete", "yellow_concrete", "blue_concrete", "white_concrete"] if _stil(seed) == 0 else \
        ["black_concrete", "red_concrete", "white_concrete", "red_concrete"]
    # Schildreihe
    for x in range(-int(half * 0.55), int(half * 0.55) + 1, 2):
        hb = int(B * max(0.0, 1 - abs(2 * x / L) ** 2) ** 0.6 * 0.95) + 1
        y = int(round(float(r["deck_haupt"](x))))
        for s in (-1, 1):
            w.setze(x, y, s * hb, w.b(farben[(x // 2) % len(farben)]))
    # Riemen
    _ruder(w, r, range(-int(half * 0.5), int(half * 0.5) + 1, _r(3 * u, 2)), F - 1, B, _r(3 * u, 2))
    # Mast mit gestreiftem Segel
    yb = _dh(r, 0) + 1
    breite = max(1, int(u))
    _rahsegel_mast(w, 0, yb, _r(16 * u, 8), B, Verlauf(w, "Segel", ["white_wool", "white_wool"]), stufen=(0.85,),
                   wappen=lambda y, z: ("red_wool" if _stil(seed) == 0 else "black_wool")
                   if (z // breite) % 2 == 0 else None, bauch=max(1, 1.4 * u))
    # Drachenkopf am Bug, Schneckenheck
    xb = int(half) - 1
    yk = _dh(r, xb)
    S = Skulptur(w, u)
    S.mat("k", w.b("dark_oak_planks" if _stil(seed) == 0 else "spruce_planks"))
    S.mat("g", w.b("gold_block"))
    S.mat("a", w.b("red_wool"))
    S.plus(kap((0, 0, 0), (1.2, 2.2, 0), 0.7, 0.55), "k")
    S.plus(ell(1.9, 2.7, 0, 1.4, 0.75, 0.7), "k")
    S.plus(kap((1.6, 3.2, 0.35), (0.6, 4.4, 0.6), 0.25), "g")
    S.plus(kap((1.6, 3.2, -0.35), (0.6, 4.4, -0.6), 0.25), "g")
    S.plus(ell(2.2, 2.9, 0.5, 0.25, 0.25, 0.25), "a")
    S.plus(ell(2.2, 2.9, -0.5, 0.25, 0.25, 0.25), "a")
    S.rendern((-1, -1, -2), (4, 5, 2), versatz=(xb + 0.5, yk + 0.5, 0.5))
    xh = -int(half) + 1
    yh = _dh(r, xh)
    for k in range(10):
        a = k * 0.6
        rr = max(0.5, 1.6 * u * (1 - k / 12))
        w.setze(round(xh - math.sin(a) * rr), round(yh + 1 + math.cos(a) * rr - rr + k * 0.15 * u + 1), 0,
                w.b(mat["leiste"], axis="y"))
    return w


# ============================================================================ Dschunke

def dschunke(seed, g=1):
    """Dschunke mit hohem Heck, Fächersegeln mit Latten, roten Laternen und Augen am Bug."""
    w = _welt(seed)
    u = U[g]
    mat = _holz(w, "dark_oak", wand=["dark_oak_planks", "mangrove_planks", "spruce_planks"],
                streifen="red_terracotta" if _stil(seed) == 0 else "yellow_terracotta", deck="spruce")
    L, B, D, F = 22 * u + 6, 3.6 * u + 1.2, 1.8 * u + 1, 2.4 * u + 1
    r = rumpf2(w, L, B, D, F, mat, form="flach", achter=_r(4 * u, 2), vorn=_r(1.5 * u, 1), sheer=0.25,
               heckfenster=True)
    half = r["half"]
    tuch = ["red_wool", "orange_wool"] if _stil(seed) == 0 else ["light_gray_wool", "white_wool"]
    for i, (fx, fh) in enumerate(((0.32, 0.7), (-0.02, 0.95), (-0.36, 0.6))):
        xm = int(half * fx * 2)
        yb = _dh(r, xm) + 1
        h = _r(20 * u * fh, 6)
        mast(w, xm, yb - 1, h + 1, g >= 2)
        breit = _r(h * 0.5, 3)
        latte = _r(2.5 * u, 2)
        for y in range(yb + _r(2 * u, 2), yb + h):
            t = (y - yb) / h
            x_hinten = xm - 1 - int(breit * (0.55 + 0.45 * math.sin(t * math.pi * 0.9)))
            for x in range(x_hinten, xm):
                if (y - yb) % latte == 0:
                    blk = w.b("stripped_bamboo_block" if False else "stripped_spruce_log", axis="x")
                else:
                    blk = w.b(tuch[((x - xm) // max(2, int(2 * u))) % 2])
                w.setze(x, y, 0, blk)
        w.setze(xm, yb + h, 0, w.b("lantern", hanging=False, waterlogged=False))
    for x in range(-int(half * 0.6), int(half * 0.6), _r(4 * u, 3)):
        for s in (-1, 1):
            hb = int(B * 0.9)
            w.setze(x, _dh(r, x) + 1, s * hb, _zaun(w, "dark_oak_fence"))
            w.setze(x, _dh(r, x) + 2, s * hb, w.b("shroomlight"))
    xb = int(half) - 2
    for s in (-1, 1):
        hb = int(float(B) * 0.35) + 1
        w.setze(xb, int(F) - 1, s * hb, w.b("white_concrete"))
        w.setze(xb + 1, int(F) - 1, s * hb, w.b("black_concrete"))
    return w


# ============================================================================ Piratenschiff

def piratenschiff(seed, g=1):
    """Piratenbrigg: schwarzer Rumpf, Kanonen, zerrissene dunkle Segel mit Totenkopf, Ausguck und Laternen."""
    w = _welt(seed)
    u = U[g]
    mat = _holz(w, "dark_oak", wand=["black_concrete", "dark_oak_planks", "black_terracotta"],
                unten=["dark_oak_planks", "black_concrete", "dark_oak_planks"],
                streifen="red_concrete" if _stil(seed) == 0 else "yellow_terracotta", deck="spruce")
    L, B, D, F = 26 * u + 6, 3.4 * u + 1.2, 2.2 * u + 1, 3 * u + 1.2
    r = rumpf2(w, L, B, D, F, mat, achter=_r(2.4 * u, 2), vorn=_r(1.2 * u, 1), kanonen=True, heckfenster=True)
    half = r["half"]
    tuch = Verlauf(w, "Segel", ["black_wool", "gray_wool", "black_wool"]) if _stil(seed) == 0 else \
        Verlauf(w, "Segel", ["brown_wool", "light_gray_wool", "white_wool"])

    def schaedel(ym):
        def f(y, z):
            dy = y - ym
            if dy * dy / 4 + z * z / 4 <= max(1.0, u) ** 2 * 1.4 and dy >= -1:
                if dy == 0 and abs(z) == 1:
                    return "black_wool"
                return "white_wool"
            if dy == -2 and abs(z) <= max(1, int(u)):
                return "white_wool"
            if abs(dy + 3 + z * 0) <= 0 and abs(z) <= 2 * max(1, int(u)):
                return "white_wool"
            return None
        return f
    for i, (fx, fh) in enumerate(((0.3, 0.9), (-0.12, 1.1))):
        xm = int(half * fx * 2)
        yb = _dh(r, xm) + 1
        h = _r(18 * u * fh, 8)
        ym = yb + int(h * 0.4 / 2) + 2
        _rahsegel_mast(w, xm, yb, h, B, tuch, stufen=(0.42, 0.75), wappen=schaedel(ym) if i == 1 else None,
                       bauch=max(1, 1.5 * u), dick=g >= 2,
                       flaggen=["black_wool", "black_wool"] if _stil(seed) == 0 else ["red_wool", "black_wool"])
    # zerrissene Segel: Löcher
    for p, b in list(w.bloecke.items()):
        if w.P.name(b).endswith("_wool") and w.rng.random() < 0.06 and p[1] > F + 4:
            w.bloecke[p] = 0
    w.bloecke = {p: b for p, b in w.bloecke.items() if b != 0}
    # Kanonenrohre
    gp = _r(F * 0.5, 1)
    for x in range(-int(half * 0.5), int(half * 0.5) + 1):
        if x % 3 == 0 and F >= 4:
            hb = int(r["B"] * max(0.0, 1 - abs(2 * x / L) ** 2.2) ** 0.6) + 1
            for s in (-1, 1):
                w.setze(x, gp, s * hb, w.b("polished_blackstone_wall", up=True, north="none", south="none",
                                           east="none", west="none", waterlogged=False), ueberschreiben=False)
    xb = int(half) - 1
    for t in np.linspace(0, 1, int(half)):
        w.setze(round(xb + half * 0.4 * t), round(_dh(r, xb) + 1 + half * 0.18 * t), 0, w.b("spruce_log", axis="x"))
    xh = -int(half) + 1
    for z in (-int(B * 0.5), int(B * 0.5)):
        w.setze(xh, _dh(r, xh) + 1, z, _zaun(w, "dark_oak_fence"))
        w.setze(xh, _dh(r, xh) + 2, z, w.b("lantern", hanging=False, waterlogged=False))
    return w


# ============================================================================ Geisterschiff

def geisterschiff(seed, g=1):
    """Geisterschiff: verrotteter, bemooster Rumpf, gebrochener Mast, zerfetzte durchscheinende Segel,
    Spinnweben, Seelenlaternen und herabhängende Ranken."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        mat = _holz(w, "dark_oak", wand=["dark_prismarine", "dark_oak_planks", "mossy_cobblestone"],
                    unten=["dark_prismarine", "prismarine", "dark_oak_planks"], streifen="prismarine_bricks",
                    deck="spruce")
        tuch = ["light_blue_stained_glass", "cyan_stained_glass", "white_stained_glass"]
    else:
        mat = _holz(w, "spruce", wand=["gray_terracotta", "spruce_planks", "mossy_cobblestone"],
                    unten=["gray_terracotta", "mossy_cobblestone", "spruce_planks"], streifen="green_terracotta",
                    deck="spruce")
        tuch = ["light_gray_stained_glass", "white_stained_glass", "lime_stained_glass"]
    L, B, D, F = 26 * u + 6, 3.4 * u + 1.2, 2.2 * u + 1, 3 * u + 1.2
    r = rumpf2(w, L, B, D, F, mat, achter=_r(2.6 * u, 2), vorn=_r(1.2 * u, 1), heckfenster=True)
    mat["fenster"] = "cyan_stained_glass"
    half = r["half"]
    tuch_ids = [w.b(t) for t in tuch]

    class Geist:
        def __call__(self, wert, x, y, z):
            return tuch_ids[(x * 3 + y * 5 + z) % 3]
    for i, (fx, fh, bruch) in enumerate(((0.32, 0.85, 1.0), (-0.05, 1.1, 0.55), (-0.38, 0.75, 1.0))):
        xm = int(half * fx * 2)
        yb = _dh(r, xm) + 1
        h = _r(18 * u * fh * bruch, 6)
        _rahsegel_mast(w, xm, yb, h, B, Geist(), stufen=(0.45, 0.8) if bruch == 1.0 else (0.7,), bauch=max(1, 1.4 * u))
    for p, b in list(w.bloecke.items()):
        if b in tuch_ids:
            if w.rng.random() < 0.18:
                w.bloecke[p] = w.b("cobweb")
            elif w.rng.random() < 0.12:
                w.bloecke[p] = 0
    w.bloecke = {p: b for p, b in w.bloecke.items() if b != 0}
    for x, y, z in r["oben"]:
        if abs(z) >= int(B * 0.9) and w.rng.random() < 0.3:
            s = 1 if z > 0 else -1
            for k in range(_r(3 * u, 2)):
                w.setze(x, y - k, z + s, w.b("vine", north=s > 0, south=s < 0, east=False, west=False, up=False),
                        ueberschreiben=False)
        if w.rng.random() < 0.02:
            w.setze(x, y + 1, z, w.b("soul_lantern", hanging=False, waterlogged=False), ueberschreiben=False)
    return w


# ============================================================================ Raddampfer

def raddampfer(seed, g=1):
    """Raddampfer mit zwei Decks, Rundumbalkonen, Steuerhaus, zwei hohen Schornsteinen mit Goldkrone
    und großen Schaufelrädern mit Radkästen."""
    w = _welt(seed)
    u = U[g]
    mat = _holz(w, "dark_oak", wand=["white_terracotta", "white_concrete", "smooth_quartz"],
                unten=["red_terracotta", "red_concrete", "dark_oak_planks"], streifen="red_concrete", deck="oak")
    mat["gold"] = False
    L, B, D, F = 26 * u + 8, 4 * u + 1.5, 1 * u + 0.8, 1.6 * u + 1
    r = rumpf2(w, L, B, D, F, mat, form="flach", sheer=0.05)
    half = r["half"]
    akzent = "red_concrete" if _stil(seed) == 0 else "blue_concrete"
    yb = _dh(r, 0) + 1
    hd = _r(2.6 * u, 3)
    for stock, (lx, bz) in enumerate(((0.62, 0.78), (0.42, 0.6))):
        x0, x1 = -int(half * lx), int(half * lx * 0.8)
        hz = int(B * bz)
        y0 = yb + stock * (hd + 1)
        for x in range(x0, x1 + 1):
            for z in range(-hz, hz + 1):
                rand = x in (x0, x1) or abs(z) == hz
                for y in range(y0, y0 + hd):
                    if rand:
                        fenster = y == y0 + 1 and (x + z) % 2 == 0 and not (x in (x0, x1) and abs(z) == hz)
                        w.setze(x, y, z, w.b("glass_pane", east=True, west=True, north=False, south=False,
                                             waterlogged=False) if fenster and abs(z) == hz else
                                w.b("glass") if fenster else w.b("white_concrete"))
        for x in range(x0 - 1, x1 + 2):
            for z in range(-hz - 1, hz + 2):
                w.setze(x, y0 + hd, z, w.b(akzent) if x in (x0 - 1, x1 + 1) or abs(z) == hz + 1 else
                        w.b("white_concrete"))
        verbinde(w, [(x, y0 + hd + 1, z) for x in range(x0 - 1, x1 + 2) for z in range(-hz - 1, hz + 2)
                     if x in (x0 - 1, x1 + 1) or abs(z) == hz + 1], "dark_oak_fence")
    # Steuerhaus
    ys = yb + 2 * (hd + 1)
    for x in range(-1, 2):
        for z in range(-1, 2):
            for y in range(ys, ys + 2):
                w.setze(x, y, z, w.b("glass") if y == ys + 1 else w.b("white_concrete"))
            w.setze(x, ys + 2, z, w.b(akzent))
    # Schornsteine
    for z in (-int(B * 0.3) - 1, int(B * 0.3) + 1):
        xs = int(half * 0.25)
        hs = _r(12 * u, 6)
        for y in range(yb, ys + hs):
            w.setze(xs, y, z, w.b("black_concrete"))
            if u >= 1.6:
                w.setze(xs + 1, y, z, w.b("black_concrete"))
        for dx in (-1, 0, 1, 2) if u >= 1.6 else (-1, 0, 1):
            for dz in (-1, 0, 1):
                if abs(dx) + abs(dz) > 0:
                    w.setze(xs + dx, ys + hs, z + dz, w.b("gold_block"))
        w.setze(xs, ys + hs, z, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    # Schaufelräder mit Radkasten
    R = _r(3.5 * u + 1, 3)
    for s in (-1, 1):
        zr = s * (int(B) + 2)
        zahnrad(w, 0, 1, zr, R, material="red_terracotta" if _stil(seed) == 0 else "blue_terracotta",
                nabe="gold_block")
        for a in range(8):
            ang = a * math.pi / 4
            for k in range(1, R + 1):
                w.setze(round(math.cos(ang) * k), round(1 + math.sin(ang) * k), zr, w.b("dark_oak_planks"))
        for x in range(-R - 2, R + 3):
            for y in range(0, R + 3):
                if R + 1.3 < math.hypot(x, y - 1) <= R + 2.3 and y >= 1:
                    for dz in (0, s):
                        w.setze(x, y, zr + dz, w.b("white_concrete"))
        for z in range(int(B) * s, zr + s, s):
            w.setze(0, 1, z, w.b("gold_block"))
    flagge(w, -int(half) + 1, yb + _r(6 * u, 3), 0, _r(3 * u, 2), ["red_wool", "white_wool", "blue_wool"])
    for y in range(yb, yb + _r(6 * u, 3)):
        w.setze(-int(half) + 1, y, 0, _zaun(w, "dark_oak_fence"))
    return w


# ============================================================================ Schwanenschiff

def schwanenschiff(seed, g=1):
    """Elfisches Schwanenschiff: weißer Rumpf mit geschnitzten Flügeln, langer Hals mit Kopf und Schnabel
    am Bug, Goldzier, Segel mit Goldborte und Blütengirlanden."""
    w = _welt(seed)
    u = U[g]
    weiss = _stil(seed) == 0
    if weiss:
        mat = dict(unten=Verlauf(w, "Rumpf", ["calcite", "smooth_quartz", "white_concrete"]),
                   wand=Verlauf(w, "Wand", ["calcite", "smooth_quartz", "white_concrete"]), streifen="gold_block",
                   leiste="stripped_birch_log", zaun="birch_fence",
                   deck=Verlauf(w, "Deck", ["birch_planks", "stripped_birch_log", "birch_planks"]), gold=False)
        feder, kopf, schnabel = ["white_concrete", "smooth_quartz", "calcite"], "white_concrete", "orange_concrete"
    else:
        mat = dict(unten=Verlauf(w, "Rumpf", ["blackstone", "polished_blackstone", "black_concrete"]),
                   wand=Verlauf(w, "Wand", ["black_concrete", "polished_blackstone", "blackstone"]),
                   streifen="gold_block", leiste="stripped_dark_oak_log", zaun="dark_oak_fence",
                   deck=Verlauf(w, "Deck", ["dark_oak_planks", "stripped_dark_oak_log", "dark_oak_planks"]),
                   gold=False)
        feder, kopf, schnabel = ["black_concrete", "black_wool", "gray_concrete"], "black_concrete", "red_concrete"
    L, B, D, F = 22 * u + 6, 3.2 * u + 1, 1.6 * u + 1, 2.2 * u + 1
    r = rumpf2(w, L, B, D, F, mat, form="spitz", enden=1.5 * u, sheer=0.1)
    half = r["half"]
    # Flügel an den Bordwänden (gestaffelte Federreihen)
    fids = [w.b(f) for f in feder]
    for s in (-1, 1):
        for x in range(-int(half * 0.55), int(half * 0.45)):
            t = (x + half * 0.55) / (half)
            hoehe = int((1 - t) * 4 * u + 1)
            hb = int(B * max(0.0, 1 - abs(2 * x / L) ** 2) ** 0.6) + 1
            for k in range(hoehe):
                y = int(F) + 1 - k + int((1 - t) * 3 * u)
                w.setze(x, y, s * hb, fids[(k + x // 2) % 3], ueberschreiben=False)
    # Hals, Kopf, Schnabel
    S = Skulptur(w, u)
    S.mat("f", w.b(kopf))
    S.mat("s", w.b(schnabel))
    S.mat("a", w.b("gold_block"))
    S.mat("e", w.b("black_concrete" if weiss else "red_concrete"))
    pts = [(0, 0, 0), (1.8, 2.5, 0), (2.4, 5.5, 0), (1.6, 8.0, 0), (2.4, 9.6, 0)]
    for a, b in zip(pts, pts[1:]):
        S.plus(kap(a, b, 0.9, 0.7), "f")
    S.plus(ell(3.0, 9.8, 0, 1.3, 0.9, 0.85), "f")
    S.plus(kap((4.0, 9.7, 0), (5.4, 9.3, 0), 0.45, 0.25), "s")
    S.plus(ell(3.4, 10.2, 0.6, 0.22, 0.22, 0.22), "e")
    S.plus(ell(3.4, 10.2, -0.6, 0.22, 0.22, 0.22), "e")
    S.plus(kap((0.3, 1.0, 0), (1.9, 3.5, 0), 1.05, 0.2), "a") if False else None
    xb = int(half) - 1
    S.rendern((-2, -1, -2), (6, 11, 2), versatz=(xb + 0.5, _dh(r, xb) + 0.5, 0.5))
    # Mast und Segel mit Goldborte
    yb = _dh(r, 0) + 1
    h = _r(15 * u, 7)
    tuch = Verlauf(w, "Segel", ["white_wool", "white_wool"]) if weiss else Verlauf(w, "Segel", ["gray_wool",
                                                                                                "light_gray_wool"])
    _rahsegel_mast(w, 0, yb, h, B, tuch, stufen=(0.82,), bauch=max(1, 1.6 * u),
                   wappen=lambda y, z: "gold_block" if y == yb + 2 else None)
    w.setze(0, yb + h, 0, w.b("end_rod", facing="up"))
    # Blütengirlanden an der Reling
    for x, y, z in r["oben"]:
        if abs(z) >= int(B * 0.85) and (x % 3 == 0):
            w.setze(x, y + 1, z, laub(w, "flowering_azalea") if weiss else laub(w, "cherry"), ueberschreiben=False)
    return w


# ============================================================================ Kogge

def kogge(seed, g=1):
    """Hanse-Kogge: bauchiger Rumpf, Vorder- und Achterkastell mit Zinnen, großes Rahsegel mit Streifen oder
    Kreuz, Ausguck, Wimpel und Anker."""
    w = _welt(seed)
    u = U[g]
    mat = _holz(w, "spruce", streifen=None, deck="oak")
    mat["gold"] = False
    L, B, D, F = 18 * u + 6, 4.2 * u + 1.4, 2.2 * u + 1, 3 * u + 1.2
    r = rumpf2(w, L, B, D, F, mat, achter=_r(3 * u, 2), vorn=_r(2.4 * u, 2), sheer=0.25)
    half = r["half"]
    yb = _dh(r, 0) + 1
    h = _r(17 * u, 8)
    if _stil(seed) == 0:
        wappen = lambda y, z: "red_wool" if ((y - yb) // max(1, int(1.5 * u))) % 2 == 0 else None  # noqa: E731
    else:
        ym = yb + int(h * 0.5)
        wappen = lambda y, z: "red_wool" if abs(z) <= max(0, int(0.6 * u)) or abs(y - ym) <= max(0, int(0.6 * u)) \
            else None  # noqa: E731
    _rahsegel_mast(w, 0, yb, h, B, Verlauf(w, "Segel", ["white_wool", "white_wool"]), stufen=(0.88,),
                   wappen=wappen, bauch=max(1, 2 * u), dick=g >= 2, flaggen=["red_wool", "white_wool"])
    yn = yb + int(h * 0.92)
    for x, z in kreisrand(max(1, 1.3 * u)):
        w.setze(x, yn, z, w.b("spruce_planks"))
        w.setze(x, yn + 1, z, w.b("spruce_planks") if (x + z) % 2 == 0 else _zaun(w, "spruce_fence"))
    for x, y, z in r["oben"]:
        dh = int(round(float(r["deck_haupt"](x))))
        if y > dh and abs(z) >= int(B * 0.7) and (x + z) % 2 == 0:
            w.setze(x, y + 1, z, w.b("spruce_planks"), ueberschreiben=False)
    xb = int(half) - 1
    for y in range(0, int(F)):
        w.setze(xb, y, int(B * 0.3) + 1, w.b("chain", axis="y", waterlogged=False))
    w.setze(xb, 0, int(B * 0.3) + 2, w.b("anvil", facing="north"))
    return w


# ============================================================================ Floß

def floss(seed, g=1):
    """Floß aus Stämmen mit Zeltdach, Lagerfeuer, geflicktem Segel, Fässern und Laterne."""
    w = _welt(seed)
    u = U[g] * 0.7
    Lx, Lz = _r(8 * u + 3, 4), _r(5 * u + 2, 3)
    holz = "spruce_log" if _stil(seed) == 0 else "jungle_log"
    for x in range(-Lx, Lx + 1):
        for z in range(-Lz, Lz + 1):
            w.setze(x, 0, z, w.b(holz, axis="x"))
    for x in (-Lx + 1, 0, Lx - 1):
        for z in range(-Lz, Lz + 1):
            w.setze(x, 1, z, w.b(holz, axis="z"))
    # Zelt
    ht = _r(2.5 * u, 2)
    for x in range(-Lx + 2, -1):
        for k in range(ht + 1):
            for s in (-1, 1):
                w.setze(x, 1 + k, s * (ht - k), w.b("white_wool" if (x + k) % 2 else "brown_wool"))
    # Lagerfeuer
    w.setze(Lx - 3, 1, -Lz + 2, w.b("cobblestone_slab", type="bottom", waterlogged=False))
    w.setze(Lx - 3, 2, -Lz + 2, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    # Mast mit Flickensegel
    xm = Lx - 2
    hm = _r(9 * u, 5)
    for y in range(1, hm + 1):
        w.setze(xm, y, 0, w.b(holz, axis="y"))
    flicken = ["white_wool", "light_gray_wool", "brown_wool", "white_wool", "yellow_wool"]
    hz = _r(3 * u, 2)
    for y in range(3, hm):
        for z in range(-hz, hz + 1):
            w.setze(xm + 1, y, z, w.b(flicken[((y // 2) * 3 + (z + 10) // 2) % len(flicken)]))
    for k in range(3):
        w.setze(-Lx + 2 + k, 2, Lz - 1, w.b("barrel", facing="up", open=False))
    w.setze(Lx - 1, 2, Lz - 1, _zaun(w, "spruce_fence"))
    w.setze(Lx - 1, 3, Lz - 1, w.b("lantern", hanging=False, waterlogged=False))
    w.anker = (0, 0, 0)
    return w


# ============================================================================ Tauchboot

def tauchboot(seed, g=1):
    """Steampunk-Tauchboot: Kupferzigarre mit Spanten und Nieten, Bullaugen mit Goldringen, Turm mit
    Sehschlitzen und Periskop, Rammsporn, Flossen und Schraube. Halb aufgetaucht."""
    w = _welt(seed)
    u = U[g]
    if _stil(seed) == 0:
        haut = Verlauf(w, "Kupfer", ["waxed_copper_block", "waxed_cut_copper", "waxed_exposed_cut_copper",
                                     "waxed_weathered_cut_copper", "waxed_oxidized_cut_copper"])
    else:
        haut = Verlauf(w, "Eisen", ["polished_deepslate", "deepslate_tiles", "polished_andesite", "iron_block"])
    L, R = 24 * u + 6, 2.6 * u + 1
    cy = R * 0.15
    S = Skulptur(w, 1.0)
    rippe = max(3, int(3 * u))

    def mat(x, y, z, lx, ly, lz):
        if abs(ly - cy - R * 0.25) < 0.6 and lz > 0 and x % rippe == 1:
            return w.b("glass")
        if x % rippe == 0:
            return w.b("waxed_copper_block" if _stil(seed) == 0 else "polished_blackstone")
        return haut(1 + 2 * (ly - cy + R) / (2 * R) + w.rng.random() * 0.4, x, y, z)
    S.mat("h", mat)
    S.mat("g", w.b("gold_block"))
    S.mat("d", w.b("polished_blackstone"))

    def zigarre(X, Y, Z):
        uu = np.clip(X / (L / 2), -1, 1)
        r = R * np.clip(1 - np.abs(uu) ** 2.6, 0, 1) ** 0.5
        d = np.sqrt((Y - cy) ** 2 + Z ** 2)
        return (np.abs(X) <= L / 2) & (d <= r) & (d > r - 1.4)
    S.plus(zigarre, "h")
    S.plus(lambda X, Y, Z: (np.abs(X) <= 1.0) & (np.abs(Z) <= 0.5) & (Y > cy + R * 0.3)
           & (Y < cy + R + 1.5 + 2.2 * u * (1 - np.abs(X))), "d") if False else None
    tl, tb, th = 2.4 * u + 1, 1.2 * u + 0.6, 2.2 * u + 1
    S.plus(lambda X, Y, Z: ((X + L * 0.08) / tl) ** 2 + (Z / tb) ** 2 <= 1, "h") if False else None
    S.plus(lambda X, Y, Z: (((X + L * 0.08) / tl) ** 2 + (Z / tb) ** 2 <= 1) & (Y >= cy + R - 1) & (Y <= cy + R + th),
           "h")
    S.plus(lambda X, Y, Z: (((X + L * 0.08) / tl) ** 2 + (Z / tb) ** 2 <= 1) & (np.abs(Y - (cy + R + th * 0.6)) < 0.5)
           & (((X + L * 0.08) / tl) ** 2 + (Z / tb) ** 2 > 0.45), "g")
    S.plus(kap((L / 2 - 1, cy, 0), (L / 2 + 2.5 * u, cy - 0.2, 0), 0.7 * u + 0.3, 0.1), "d")
    for (dy, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        S.plus(lambda X, Y, Z, dy=dy, dz=dz: (X < -L * 0.33) & (X > -L / 2 - 0.5)
               & (np.abs((Y - cy) * dz - Z * dy) <= 0.55)
               & (((Y - cy) * dy + Z * dz) > 0) & (((Y - cy) * dy + Z * dz) < R * 0.5 + 2.5 * u * (-X - L * 0.33)
                                                    / (L * 0.17)), "h")
    S.rendern((-L / 2 - 4, cy - R - 5 * u - 2, -R - 5 * u - 2), (L / 2 + 4 * u + 2, cy + R + th + 2,
                                                                 R + 5 * u + 2))
    xt = round(-L * 0.08)
    yt = round(cy + R + th) + 1
    for y in range(yt, yt + _r(2 * u, 2)):
        w.setze(xt + 1, y, 0, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(xt + 1, yt + _r(2 * u, 2), 0, w.b("lantern", hanging=False, waterlogged=False))
    zahnrad(w, -int(L / 2) - 1, round(cy), 0, _r(1.8 * u, 2), ebene="zy", material="waxed_cut_copper",
            nabe="gold_block")
    return w


# ============================================================================ Gondel

def gondel(seed, g=1):
    """Schlanke Gondel mit hochgezogenen Enden, goldenem Bugbeschlag, kleiner Kabine mit Vorhängen und
    Laterne am Heck."""
    w = _welt(seed)
    u = U[g] * 0.6
    schwarz = _stil(seed) == 0
    mat = dict(unten=Verlauf(w, "Rumpf", ["black_concrete", "black_terracotta", "black_concrete"]),
               wand=Verlauf(w, "Wand", ["black_concrete", "black_terracotta", "black_concrete"]) if schwarz else
               Verlauf(w, "Wand", ["dark_oak_planks", "dark_oak_planks", "black_concrete"]),
               streifen="gold_block", leiste="stripped_dark_oak_log", zaun="dark_oak_fence",
               deck=Verlauf(w, "Deck", ["dark_oak_planks", "dark_oak_planks"]), gold=False)
    L, B, D, F = 18 * u + 6, 1.6 * u + 1, 0.8 * u + 0.6, 1 * u + 0.8
    r = rumpf2(w, L, B, D, F, mat, form="spitz", enden=2.6 * u + 1, reling=False, offen=True)
    half = r["half"]
    xb = int(half) - 1
    yb = _dh(r, xb)
    for k in range(_r(2.5 * u, 2) + 1):
        w.setze(xb + 1, yb + k, 0, w.b("gold_block"))
        if k % 2 == 1:
            w.setze(xb + 2, yb + k, 0, w.b("gold_block"))
    kx0, kx1 = -int(L * 0.12), int(L * 0.12)
    for x in range(kx0, kx1 + 1):
        for z in (-1, 0, 1):
            w.setze(x, int(F) + _r(2 * u, 2), z, w.b("red_wool" if schwarz else "blue_wool"))
        for z in (-1, 1):
            if x in (kx0, kx1):
                for y in range(int(F), int(F) + _r(2 * u, 2)):
                    w.setze(x, y, z, _zaun(w, "dark_oak_fence"))
    for x in range(kx0 + 1, kx1):
        w.setze(x, 0, 0, w.b("red_wool" if schwarz else "blue_wool"))
    xh = -int(half) + 2
    w.setze(xh, _dh(r, xh) + 1, 0, _zaun(w, "dark_oak_fence"))
    w.setze(xh, _dh(r, xh) + 2, 0, w.b("lantern", hanging=False, waterlogged=False))
    return w


BOOTE = {
    "ruderboot": ("Ruderboot", ruderboot),
    "fischerboot": ("Fischkutter", fischerboot),
    "langschiff": ("Langschiff", langschiff),
    "dschunke": ("Dschunke", dschunke),
    "piratenschiff": ("Piratenbrigg", piratenschiff),
    "geisterschiff": ("Geisterschiff", geisterschiff),
    "raddampfer": ("Raddampfer", raddampfer),
    "schwanenschiff": ("Schwanenschiff", schwanenschiff),
    "kogge": ("Kogge", kogge),
    "floss": ("Floß", floss),
    "tauchboot": ("Tauchboot", tauchboot),
    "gondel": ("Gondel", gondel),
}


from boote2 import NEU as _NEU  # noqa: E402

BOOTE.update(_NEU)

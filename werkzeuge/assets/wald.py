"""Wald – ganze Waldstücke zum Bewalden großer Flächen.

Jedes Waldstück hat einen organischen, ausfransenden Rand (dünner werdend, kleinere Bäume, Büsche),
damit mehrere Stücke nebeneinander nahtlos ineinander übergehen. Baumarten wachsen in Gruppen
(Rauschen), dazwischen Jungbäume, Sträucher, Totholz, Findlinge und ein dichter Bodenbewuchs.

Geländefolgend: Jeder Baum merkt sich seinen Stammfuß (folge_anker) – die Mod setzt ihn beim Platzieren
auf die echte Geländehöhe. Bodenblöcke und Pflanzen folgen ihrer eigenen Spalte (-1).
Kein Gras wird gesetzt, wo kein Bewuchs ist: am Rand bleibt der natürliche Boden der Welt sichtbar.
"""

from __future__ import annotations

import math

import numpy as np

import baeume as B
from lib import LUFT, Rauschen, Welt, laub

GROESSEN_R = [11, 18, 29, 44]


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


# ============================================================================ Waldstück


class Stueck:
    def __init__(self, seed, g):
        self.w = Welt(seed)
        self.w.anker = (0, 0, 0)
        self.rng = self.w.rng
        self.R = GROESSEN_R[g]
        self.g = g
        self.stil = _stil(seed)
        self.w.folgen = {}
        self.w.folge_anker = []
        self.r_form = Rauschen(self.w, 1.0, 32)
        self.r_art = Rauschen(self.w, 9.0)
        self.r_boden = Rauschen(self.w, 4.0)
        self.r_fein = Rauschen(self.w, 1.6)
        self.plaetze = []          # (x, z, r) belegte Stammplätze
        self.boden_platz = set()   # (x, z) mit Bodenbelag/Pflanzen
        self._form = [0.72 + 0.4 * self.r_form(math.cos(a) * 3 + 50, 0, math.sin(a) * 3 + 50)
                      for a in np.linspace(0, 2 * math.pi, 64, endpoint=False)]

    # ---- Form: 0 = Mitte, 1 = Rand, >1 = außerhalb
    def rand(self, x, z):
        a = math.atan2(z, x) % (2 * math.pi)
        i = a / (2 * math.pi) * 64
        i0 = int(i) % 64
        f = i - int(i)
        r = self.R * (self._form[i0] * (1 - f) + self._form[(i0 + 1) % 64] * f)
        return math.hypot(x, z) / r

    # ---- Bäume stempeln (Palette übersetzen, Stammfuß merken)
    def stempel(self, quelle, x0, z0, dy=0, schnee=False):
        w = self.w
        idx = len(w.folge_anker)
        w.folge_anker.append((x0, z0))
        karte = {}
        for i, (name, props) in enumerate(quelle.P.eintraege):
            karte[i] = w.b(name, **dict(props))
        for (x, y, z), s in quelle.bloecke.items():
            if s == LUFT:
                continue
            p = (x + x0, y + dy, z + z0)
            name = quelle.P.eintraege[s][0]
            hart = name.endswith(("_log", "_wood", "_stem", "_block", "roots")) or "mushroom" in name
            if not hart and not w.frei(*p):
                continue
            w.setze(*p, karte[s])
            w.folgen[p] = idx
        if schnee:
            self._beschneien(quelle, x0, z0, dy, idx)
        return idx

    def _beschneien(self, quelle, x0, z0, dy, idx):
        w = self.w
        sn = w.b("snow", layers=1)
        oben = {}
        for (x, y, z), s in quelle.bloecke.items():
            if s and quelle.P.eintraege[s][0].endswith("_leaves"):
                k = (x, z)
                if y > oben.get(k, -99):
                    oben[k] = y
        for (x, z), y in oben.items():
            p = (x + x0, y + dy + 1, z + z0)
            if w.frei(*p) and self.rng.random() < 0.6:
                w.setze(*p, sn)
                w.folgen[p] = idx

    def frei_fuer(self, x, z, r):
        for (px, pz, pr) in self.plaetze:
            if (px - x) ** 2 + (pz - z) ** 2 < (max(pr, r)) ** 2:
                return False
        return True

    def verteile(self, abstand, versuche, auswahl, rand_max=1.0, rand_min=0.0, art_schwelle=None):
        """Poisson-artige Verteilung. auswahl(x, z, rand, art) -> (quelle, r) oder None."""
        R = self.R
        for _ in range(versuche):
            x = int(round((self.rng.random() * 2 - 1) * R * 1.2))
            z = int(round((self.rng.random() * 2 - 1) * R * 1.2))
            rd = self.rand(x, z)
            if rd > rand_max or rd < rand_min:
                continue
            # zum Rand hin dünner
            if rd > 0.7 and self.rng.random() < (rd - 0.7) * 2.2:
                continue
            art = self.r_art(x, 0, z)
            if art_schwelle and not (art_schwelle[0] <= art <= art_schwelle[1]):
                continue
            if not self.frei_fuer(x, z, abstand):
                continue
            erg = auswahl(x, z, rd, art)
            if not erg:
                continue
            quelle, r = erg
            self.plaetze.append((x, z, r))
            self.stempel(quelle, x, z, schnee=getattr(self, "schnee", False))

    # ---- Boden & Unterwuchs
    def boden(self, belag, pflanzen, dichte=0.55, belag_dichte=0.75):
        """belag: [(block, gewicht)] für y=0; pflanzen: [(block|callable, gewicht)] für y=1."""
        w = self.w
        R = self.R
        bk = _kum(belag)
        pk = _kum(pflanzen)
        for x in range(-int(R * 1.3), int(R * 1.3) + 1):
            for z in range(-int(R * 1.3), int(R * 1.3) + 1):
                rd = self.rand(x, z)
                if rd > 1.05:
                    continue
                staerke = 1.0 if rd < 0.75 else max(0.0, 1 - (rd - 0.75) / 0.3)
                v = self.r_boden(x, 0, z) * 0.7 + self.r_fein(x, 0, z) * 0.3
                # Bodenbelag in Flecken, nach außen ausdünnend
                if belag and v * staerke > 1 - belag_dichte and w.frei(x, 0, z):
                    blk = _wahl(bk, (self.r_boden(x + 31, 5, z) * 0.6 + self.r_fein(x, 9, z) * 0.4))
                    w.setze(x, 0, z, blk(w) if callable(blk) else w.b(blk))
                    w.folgen[(x, 0, z)] = -1
                if pflanzen and w.frei(x, 1, z):
                    if self.rng.random() < dichte * staerke * (0.55 + 0.9 * self.r_fein(x, 3, z)):
                        blk = _wahl(pk, self.rng.random())
                        if callable(blk):
                            blk(w, x, 1, z)
                        else:
                            w.setze(x, 1, z, w.b(blk))
                            w.folgen[(x, 1, z)] = -1
        # alles, was die Pflanzen-Funktionen gesetzt haben, folgt der Spalte
        for p in list(w.bloecke):
            if p not in w.folgen and p[1] <= 2:
                w.folgen[p] = -1


def _kum(liste):
    s = sum(g for _, g in liste) or 1
    k = []
    a = 0
    for b, g in liste:
        a += g / s
        k.append((a, b))
    return k


def _wahl(kum, v):
    for grenze, b in kum:
        if v <= grenze:
            return b
    return kum[-1][1]


# ============================================================================ Pflanzen (y = 1, folgen der Spalte)


def hohes(name):
    def f(w, x, y, z):
        if w.frei(x, y + 1, z):
            w.setze(x, y, z, w.b(name, half="lower"))
            w.setze(x, y + 1, z, w.b(name, half="upper"))
            w.folgen[(x, y, z)] = -1
            w.folgen[(x, y + 1, z)] = -1
    return f


def bluetenblaetter(w, x, y, z):
    w.setze(x, y, z, w.b("pink_petals", flower_amount=int(1 + w.rng.integers(4)),
                         facing=["north", "south", "east", "west"][int(w.rng.integers(4))]))
    w.folgen[(x, y, z)] = -1


def beeren(w, x, y, z):
    w.setze(x, y, z, w.b("sweet_berry_bush", age=int(1 + w.rng.integers(3))))
    w.folgen[(x, y, z)] = -1


def bambus(w, x, y, z):
    h = int(4 + w.rng.integers(9))
    for k in range(h):
        blatt = "large" if k >= h - 2 else ("small" if k >= h - 4 else "none")
        w.setze(x, y + k, z, w.b("bamboo", age=1 if k < h - 3 else 0, leaves=blatt, stage=0))
        w.folgen[(x, y + k, z)] = -1


def zuckerrohr(w, x, y, z):
    for k in range(int(1 + w.rng.integers(3))):
        w.setze(x, y + k, z, w.b("sugar_cane", age=0))
        w.folgen[(x, y + k, z)] = -1


def schneeschicht(w, x, y, z):
    w.setze(x, y, z, w.b("snow", layers=int(1 + w.rng.integers(2))))
    w.folgen[(x, y, z)] = -1


def leuchtflechte(w, x, y, z):
    w.setze(x, y, z, w.b("glow_lichen", down=True, up=False, north=False, south=False, east=False, west=False,
                         waterlogged=False))
    w.folgen[(x, y, z)] = -1


# ============================================================================ Baum-Bausteine (eigene, leichte Formen)


def _neu(seed):
    w = Welt(int(seed))
    w.anker = (0, 0, 0)
    return w


def _blob(w, cx, cy, cz, rx, ry, blaetter, dichte=0.92, unten_flach=1.4):
    """Laubballen; blaetter: [(id, gewicht)]"""
    ri = int(math.ceil(max(rx, ry))) + 1
    k = _kum(blaetter)
    for x in range(int(cx) - ri, int(cx) + ri + 1):
        for y in range(int(cy) - ri, int(cy) + ri + 1):
            for z in range(int(cz) - ri, int(cz) + ri + 1):
                dx, dy, dz = (x - cx) / rx, (y - cy) / ry, (z - cz) / rx
                if dy < 0:
                    dy *= unten_flach
                d = math.sqrt(dx * dx + dy * dy + dz * dz)
                if d > 1.0 + (w.rng.random() - 0.5) * 0.45:
                    continue
                if d > 0.7 and w.rng.random() > dichte:
                    continue
                w.setze(x, y, z, _wahl(k, w.rng.random()), ueberschreiben=False)


def _saeule(w, x, z, y0, y1, blk):
    for y in range(y0, y1 + 1):
        w.setze(x, y, z, blk)


def kleiner_laubbaum(seed, art="oak", H=None, blaetter=None, breit=1.0):
    """Natürlicher kleiner Laubbaum: leicht schiefer Stamm, 1–3 Seitenäste, unregelmäßige Krone."""
    w = _neu(seed)
    rng = w.rng
    H = H or int(5 + rng.integers(4))
    log = lambda a="y": w.b(f"{art}_log", axis=a)
    bl = blaetter or [(laub(w, art), 1.0)]
    bl = [(b if isinstance(b, int) else (w.b(b[1:]) if b.startswith("=") else laub(w, b)), g) for b, g in bl]
    x = z = 0
    dx, dz = rng.choice([-1, 0, 0, 0, 1]), rng.choice([-1, 0, 0, 0, 1])
    for y in range(0, H):
        if y == int(H * 0.6) and (dx or dz):
            x += dx
            z += dz
        w.setze(x, y, z, log())
    top = (x, H, z)
    for _ in range(int(1 + rng.integers(3))):
        a = rng.random() * 2 * math.pi
        y = int(H * (0.5 + 0.3 * rng.random()))
        L = 1 + int(rng.integers(3))
        ax, az = x, z
        for k in range(1, L + 1):
            ax, az = x + round(math.cos(a) * k), z + round(math.sin(a) * k)
            w.setze(ax, y + (k // 2), az, log("x" if abs(math.cos(a)) > 0.7 else "z"))
        _blob(w, ax, y + L // 2 + 1, az, 2.0 * breit + rng.random(), 1.6, bl)
    _blob(w, top[0], top[1] - 0.5, top[2], (2.4 + rng.random() * 1.2) * breit, 2.0 + rng.random() * 0.8, bl)
    return w


def schlanke_fichte(seed, H=None, art="spruce", schnee=False):
    """Typische Fichte/Tanne: gerader Stamm, gestufte Nadelkränze, spitze Krone."""
    w = _neu(seed)
    rng = w.rng
    H = H or int(9 + rng.integers(10))
    log = w.b(f"{art}_log", axis="y")
    nad = laub(w, art)
    _saeule(w, 0, 0, 0, H - 1, log)
    unten = int(2 + rng.integers(3))
    rmax = 1.6 + H * 0.17
    y = H + 1
    stufe = 0
    while y >= unten:
        t = (H + 1 - y) / max(1, H + 1 - unten)
        r = 0.6 + rmax * t ** 0.9
        r *= 1.15 if stufe % 2 == 0 else 0.72
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(x, z)
                if d <= r + (rng.random() - 0.5) * 0.7 and not (x == 0 and z == 0 and y < H):
                    w.setze(x, y, z, nad, ueberschreiben=False)
        y -= 1
        stufe += 1
    w.setze(0, H + 2, 0, nad)
    return w


def kiefer(seed, H=None):
    """Kiefer: hoher, leicht gebogener kahler Stamm, flache zerzauste Schirmkrone."""
    w = _neu(seed)
    rng = w.rng
    H = H or int(13 + rng.integers(9))
    log = lambda a="y": w.b("spruce_log", axis=a)
    nad = [(laub(w, "spruce"), 0.8), (laub(w, "oak"), 0.2)]
    a = rng.random() * 2 * math.pi
    neig = 0.06 + rng.random() * 0.1
    x = z = 0.0
    for y in range(H):
        x += math.cos(a) * neig * (y / H)
        z += math.sin(a) * neig * (y / H)
        w.setze(round(x), y, round(z), log())
    tx, tz = round(x), round(z)
    for _ in range(int(3 + rng.integers(3))):
        b = rng.random() * 2 * math.pi
        y = int(H * (0.72 + 0.28 * rng.random()))
        L = 2 + int(rng.integers(3))
        for k in range(1, L + 1):
            w.setze(tx + round(math.cos(b) * k), y + k // 3, tz + round(math.sin(b) * k),
                    log("x" if abs(math.cos(b)) > 0.7 else "z"))
        _blob(w, tx + math.cos(b) * L, y + L // 3 + 1, tz + math.sin(b) * L, 1.5 + rng.random() * 0.8, 1.0, nad)
    _blob(w, tx, H, tz, 2.0 + rng.random() * 0.8, 1.3, nad)
    for k in range(int(rng.integers(3))):     # ein paar Aststummel weiter unten
        y = int(H * (0.35 + 0.3 * rng.random()))
        b = rng.random() * 2 * math.pi
        w.setze(round(x * y / H + math.cos(b)), y, round(z * y / H + math.sin(b)), w.b("spruce_fence", north=False,
                south=False, east=False, west=False, waterlogged=False))
    return w


def dunkeleiche(seed, H=None):
    """Dunkeleiche: 2×2-Stamm, knorrige Seitenäste, breite flache Krone."""
    w = _neu(seed)
    rng = w.rng
    H = H or int(6 + rng.integers(4))
    log = lambda a="y": w.b("dark_oak_log", axis=a)
    bl = [(laub(w, "dark_oak"), 0.85), (laub(w, "oak"), 0.15)]
    for dx in (0, 1):
        for dz in (0, 1):
            _saeule(w, dx, dz, -1, H - 1 - int(rng.integers(2)), log())
    for dx, dz in ((-1, 0), (2, 1), (0, 2), (1, -1)):
        if rng.random() < 0.6:
            w.setze(dx, 0, dz, w.b("dark_oak_wood", axis="y"))
    for _ in range(int(3 + rng.integers(3))):
        a = rng.random() * 2 * math.pi
        y = int(H * (0.55 + 0.4 * rng.random()))
        L = 2 + int(rng.integers(3))
        ex, ez = 0, 0
        for k in range(1, L + 1):
            ex, ez = round(0.5 + math.cos(a) * (k + 0.8)), round(0.5 + math.sin(a) * (k + 0.8))
            w.setze(ex, y + k // 2, ez, log("x" if abs(math.cos(a)) > 0.7 else "z"))
        _blob(w, ex, y + L // 2 + 1.2, ez, 2.6 + rng.random(), 1.4, bl, unten_flach=2.0)
    _blob(w, 0.5, H + 0.5, 0.5, 4.0 + rng.random() * 1.5, 1.7, bl, unten_flach=2.2)
    return w


def strauch(seed, art="oak", gross=False, blumen=False):
    w = _neu(seed)
    rng = w.rng
    bl = [(laub(w, art), 1.0)]
    if blumen:
        bl = [(laub(w, "flowering_azalea"), 0.5), (laub(w, "azalea"), 0.5)]
    stammart = {"azalea": "oak", "flowering_azalea": "oak"}.get(art, art)
    w.setze(0, 1, 0, w.b(f"{stammart}_log", axis="y"))
    r = (1.6 if gross else 1.1) + rng.random() * 0.6
    _blob(w, 0, 1.6 if gross else 1.3, 0, r, 1.1 + (0.5 if gross else 0), bl, dichte=0.85)
    return w


def riesenpilz(seed, rot=True, H=None):
    w = _neu(seed)
    rng = w.rng
    H = H or int(5 + rng.integers(5))
    st = w.b("mushroom_stem", up=False, down=False, north=True, south=True, east=True, west=True)
    _saeule(w, 0, 0, 1, H, st)
    kappe = w.b("red_mushroom_block" if rot else "brown_mushroom_block", up=True, down=False, north=True,
                south=True, east=True, west=True)
    if rot:
        R = 2.2 + rng.random()
        for x in range(-3, 4):
            for z in range(-3, 4):
                for y in range(0, 4):
                    d = math.sqrt(x * x + z * z + (y * 1.3) ** 2)
                    if R - 0.9 < d <= R + 0.5 and y + H - 1 > H - 2:
                        w.setze(x, H - 1 + y, z, kappe)
    else:
        R = 3.0 + rng.random() * 1.2
        for x in range(-4, 5):
            for z in range(-4, 5):
                if math.hypot(x, z) <= R:
                    w.setze(x, H + 1, z, kappe)
    return w


def liegender_stamm(seed, art="oak"):
    w = _neu(seed)
    rng = w.rng
    L = int(4 + rng.integers(6))
    ax = "x" if rng.random() < 0.5 else "z"
    for k in range(-L // 2, L - L // 2):
        p = (k, 1, 0) if ax == "x" else (0, 1, k)
        w.setze(*p, w.b(f"{art}_log", axis=ax))
        r = rng.random()
        if r < 0.45:
            w.setze(p[0], 2, p[2], w.b("moss_carpet"))
        elif r < 0.6:
            w.setze(p[0], 2, p[2], w.b("brown_mushroom" if rng.random() < 0.6 else "red_mushroom"))
    # Wurzelteller am einen Ende
    e = (-L // 2 - 1, 0) if ax == "x" else (0, -L // 2 - 1)
    for a in (-1, 0, 1):
        for y in (1, 2):
            p = (e[0], y, e[1] + a) if ax == "x" else (e[0] + a, y, e[1])
            if rng.random() < 0.7:
                w.setze(*p, w.b("rooted_dirt") if y == 1 else w.b("mangrove_roots", waterlogged=False))
    return w


def stumpf(seed, art="oak"):
    w = _neu(seed)
    rng = w.rng
    h = int(1 + rng.integers(2))
    for y in range(1, h + 1):
        w.setze(0, y, 0, w.b(f"{art}_log", axis="y"))
    w.setze(0, h + 1, 0, w.b("moss_carpet") if rng.random() < 0.6 else w.b("brown_mushroom"))
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if rng.random() < 0.35:
            w.setze(dx, 1, dz, w.b(f"{art}_wood", axis="y" if rng.random() < 0.5 else "x"))
    return w


def findling(seed, moosig=True, art="stein"):
    w = _neu(seed)
    rng = w.rng
    mats = {"stein": ["stone", "andesite", "cobblestone", "mossy_cobblestone", "tuff"],
            "fels": ["stone", "andesite", "tuff", "diorite", "gravel"],
            "dunkel": ["cobbled_deepslate", "tuff", "deepslate", "mossy_cobblestone"],
            "sand": ["sandstone", "smooth_sandstone", "terracotta", "orange_terracotta"],
            "schnee": ["stone", "andesite", "packed_ice", "snow_block"]}[art]
    r = 1.2 + rng.random() * 1.6
    r_n = Rauschen(w, 1.3)
    for x in range(-3, 4):
        for z in range(-3, 4):
            for y in range(0, 4):
                d = math.sqrt(x * x + z * z + ((y - 0.3) * 1.4) ** 2) + (r_n(x, y, z) - 0.5) * 1.2
                if d < r:
                    m = mats[int(r_n(x + 9, y, z) * len(mats) * 0.999)]
                    if moosig and y >= 1 and r_n(x, y + 5, z) > 0.55:
                        m = "moss_block" if y >= 2 else "mossy_cobblestone"
                    w.setze(x, y, z, w.b(m))
    for (x, y, z) in list(w.bloecke):
        if moosig and w.frei(x, y + 1, z) and rng.random() < 0.4 and y >= 1:
            w.setze(x, y + 1, z, w.b("moss_carpet"))
    return w


def palme(seed, H=None):
    w = _neu(seed)
    rng = w.rng
    H = H or int(7 + rng.integers(6))
    a = rng.random() * 2 * math.pi
    x = z = 0.0
    for y in range(H):
        x += math.cos(a) * 0.12 * (y / H) * 2.2
        z += math.sin(a) * 0.12 * (y / H) * 2.2
        w.setze(round(x), y, round(z), w.b("jungle_log", axis="y"))
    tx, ty, tz = round(x), H, round(z)
    bl = laub(w, "jungle")
    w.setze(tx, ty, tz, bl)
    for k in range(7):
        b = k * 2 * math.pi / 7 + rng.random() * 0.4
        L = 3 + int(rng.integers(3))
        for s in range(1, L + 1):
            px, pz = tx + round(math.cos(b) * s), tz + round(math.sin(b) * s)
            py = ty + (1 if s <= 1 else 0) - max(0, s - 2) // 2
            w.setze(px, py, pz, bl, ueberschreiben=False)
    for d in ((1, 0), (0, 1), (-1, 0)):
        if rng.random() < 0.6:
            w.setze(tx + d[0], ty - 1, tz + d[1], w.b("cocoa", age=2, facing={(1, 0): "west", (0, 1): "north",
                                                                              (-1, 0): "east"}[d]))
    return w


def herbstbaum(seed, farben, H=None):
    """Laubbaum mit Herbstfarben aus farbigen Laub-Ersatzblöcken."""
    return kleiner_laubbaum(seed, art="oak", H=H, blaetter=farben, breit=1.15)


# ============================================================================ Baumarten-Wahl


def _baum(seed, art, gross=0):
    """Fertige Bäume aus baeume.py (gross: 0/1) – fallweise mit Größe begrenzt."""
    return B.ARTEN[art][1](int(seed), gross)


def _s(st):
    return int(st.rng.integers(1, 10 ** 8))


# ============================================================================ Waldtypen


def eichenwald(seed, g=1):
    """Sommerlicher Eichen-Mischwald mit Birken, Jungbäumen, Haselsträuchern und Blumen am Rand."""
    st = Stueck(seed, g)
    w = st.w
    herbst = st.stil == 1

    def gross(x, z, rd, art):
        if rd < 0.6 and st.rng.random() < 0.12 + 0.05 * st.g:
            return _baum(_s(st), "eiche", 1 if st.g >= 2 else 0), 6
        if art > 0.62:
            return _baum(_s(st), "birke", 0), 3
        if herbst and st.rng.random() < 0.4:
            return herbstbaum(_s(st), _herbst_laub(w, st.rng)), 3.5
        return kleiner_laubbaum(_s(st), "oak", blaetter=[("oak", 0.85), ("birch", 0.15)]), 3.5

    st.verteile(4, 900 * (st.g + 1) ** 2, gross)
    st.verteile(2, 400 * (st.g + 1) ** 2, lambda x, z, rd, a: (strauch(_s(st), "oak" if a < 0.5 else "azalea",
                                                                       gross=st.rng.random() < 0.3), 1.5))
    st.verteile(5, 30 * (st.g + 1), lambda x, z, rd, a: (liegender_stamm(_s(st), "oak"), 3)
                if st.rng.random() < 0.5 else (findling(_s(st)), 2.5))
    st.boden([("podzol", 2), ("coarse_dirt", 1), ("moss_block", 1.5), ("rooted_dirt", 0.6), ("grass_block_s", 3)],
             [("grass", 6), ("fern", 3), (hohes("large_fern"), 1.2), (hohes("tall_grass"), 1.5), ("poppy", 0.4),
              ("dandelion", 0.3), ("lily_of_the_valley", 0.5), ("brown_mushroom", 0.3), ("oxeye_daisy", 0.2),
              (beeren, 0.2)] + ([("moss_carpet", 2)] if herbst else []),
             dichte=0.45)
    return w


def _herbst_laub(w, rng):
    """Herbstfarben: Namen mit "=" sind normale Blöcke statt Laub."""
    wahl = rng.random()
    if wahl < 0.33:
        return [("=nether_wart_block", 0.55), ("=red_mushroom_block", 0.15), ("oak", 0.3)]
    if wahl < 0.66:
        return [("=shroomlight", 0.08), ("=honeycomb_block", 0.45), ("oak", 0.27), ("=orange_wool", 0.2)]
    return [("birch", 0.35), ("=yellow_wool", 0.15), ("=honeycomb_block", 0.35), ("=orange_wool", 0.15)]


def birkenhain(seed, g=1):
    """Lichter Birkenhain: viele schlanke Birken, Farne, Maiglöckchen; Stil 2 mit hohen Altbirken."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        if st.stil == 1 and st.rng.random() < 0.35:
            return _baum(_s(st), "birke", 1), 3.5
        if st.rng.random() < 0.6:
            return _baum(_s(st), "birke", 0), 2.8
        return kleiner_laubbaum(_s(st), "birch", H=int(6 + st.rng.integers(4)),
                                blaetter=[("birch", 1.0)], breit=0.8), 2.8

    st.verteile(3, 1100 * (st.g + 1) ** 2, baum)
    st.verteile(2, 200 * (st.g + 1) ** 2, lambda x, z, rd, a: (strauch(_s(st), "birch"), 1.5))
    st.verteile(6, 20 * (st.g + 1), lambda x, z, rd, a: (liegender_stamm(_s(st), "birch"), 3))
    st.boden([("grass_block_s", 5), ("moss_block", 0.6), ("coarse_dirt", 0.4)],
             [("grass", 7), ("fern", 2), ("lily_of_the_valley", 1.2), ("oxeye_daisy", 0.8), ("azure_bluet", 0.6),
              (hohes("tall_grass"), 2), (hohes("lilac"), 0.2), ("allium", 0.15)],
             dichte=0.5, belag_dichte=0.4)
    return w


def fichtenwald(seed, g=1):
    """Dunkler Fichtenwald (Taiga) mit Moos und Beeren; Stil 2 tief verschneit."""
    st = Stueck(seed, g)
    w = st.w
    st.schnee = st.stil == 1

    def baum(x, z, rd, art):
        if st.g >= 1 and rd < 0.6 and st.rng.random() < 0.1:
            return _baum(_s(st), "fichte", 0), 4.5
        H = int(7 + st.rng.integers(12) * (1.2 - rd * 0.6))
        return schlanke_fichte(_s(st), H=H), 2.4 + H * 0.12

    st.verteile(3.5, 1100 * (st.g + 1) ** 2, baum)
    st.verteile(2, 160 * (st.g + 1) ** 2, lambda x, z, rd, a: (schlanke_fichte(_s(st), H=int(3 + st.rng.integers(3))), 1.5))
    st.verteile(5, 30 * (st.g + 1), lambda x, z, rd, a: (findling(_s(st), moosig=not st.schnee,
                                                                   art="schnee" if st.schnee else "stein"), 2.5)
                if st.rng.random() < 0.6 else (liegender_stamm(_s(st), "spruce"), 3))
    if st.schnee:
        st.boden([("snow_block", 4), ("podzol", 1), ("powder_snow_n", 0)],
                 [(schneeschicht, 10), ("fern", 0.5), (beeren, 0.3)], dichte=0.8, belag_dichte=0.6)
    else:
        st.boden([("podzol", 4), ("coarse_dirt", 1.2), ("moss_block", 1.5), ("grass_block_s", 1)],
                 [("fern", 5), ("grass", 2), (hohes("large_fern"), 2.2), (beeren, 1.0), ("brown_mushroom", 0.4),
                  ("moss_carpet", 1.5)], dichte=0.5)
    return w


def kiefernwald(seed, g=1):
    """Lichter Kiefernwald auf sandigem Boden; Stil 2 als Bergkiefern mit Felsen."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        if st.rng.random() < 0.18:
            return schlanke_fichte(_s(st), H=int(6 + st.rng.integers(6))), 2.5
        return kiefer(_s(st), H=int(12 + st.rng.integers(10) * (1.1 - rd * 0.5))), 5

    st.verteile(5, 900 * (st.g + 1) ** 2, baum)
    st.verteile(3, 120 * (st.g + 1) ** 2, lambda x, z, rd, a: (strauch(_s(st), "spruce"), 1.5))
    st.verteile(5, (60 if st.stil else 15) * (st.g + 1), lambda x, z, rd, a: (findling(_s(st), moosig=False, art="fels"), 2.5))
    st.boden([("coarse_dirt", 2), ("podzol", 2), ("gravel", 0.4 + st.stil), ("grass_block_s", 2),
              ("rooted_dirt", 0.5)] + ([("stone", 1), ("andesite", 0.8)] if st.stil else []),
             [("grass", 6), ("fern", 2), (hohes("tall_grass"), 2), ("dead_bush", 0.5), (beeren, 0.5),
              ("dandelion", 0.2)], dichte=0.35)
    return w


def dunkelwald(seed, g=1):
    """Finsterer Dunkeleichenwald: dichtes Kronendach, Riesenpilze, Moos und Totholz."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        if art > 0.68 and st.rng.random() < 0.6:
            return riesenpilz(_s(st), rot=st.rng.random() < 0.5), 3
        if st.stil == 1 and st.rng.random() < 0.18 and st.g >= 1:
            return _baum(_s(st), "schwarzeiche", 0), 5
        return dunkeleiche(_s(st)), 4.2

    st.verteile(4, 900 * (st.g + 1) ** 2, baum)
    st.verteile(2, 150 * (st.g + 1) ** 2, lambda x, z, rd, a: (strauch(_s(st), "dark_oak", gross=True), 1.5))
    st.verteile(5, 40 * (st.g + 1), lambda x, z, rd, a: (liegender_stamm(_s(st), "dark_oak"), 3)
                if st.rng.random() < 0.6 else (stumpf(_s(st), "dark_oak"), 1.5))
    st.boden([("podzol", 3), ("moss_block", 2.5), ("coarse_dirt", 1), ("rooted_dirt", 1), ("mycelium", 0.3 * st.stil)],
             [("fern", 3), ("grass", 2), ("brown_mushroom", 1.2), ("red_mushroom", 0.8), ("moss_carpet", 3),
              (hohes("large_fern"), 1)] + ([(leuchtflechte, 0.6)] if st.stil else []), dichte=0.45)
    return w


def kirschhain(seed, g=1):
    """Kirschblütenhain mit rosa Blütenteppich; Stil 2 mit Azaleen und Bambus dazwischen."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        if st.rng.random() < 0.65:
            return _baum(_s(st), "kirschbaum", 1 if (st.g >= 2 and st.rng.random() < 0.3) else 0), 4
        if st.stil == 1:
            return _baum(_s(st), "azaleenbaum", 0), 3
        return kleiner_laubbaum(_s(st), "cherry", blaetter=[("cherry", 1.0)]), 3.5

    st.verteile(5, 800 * (st.g + 1) ** 2, baum)
    st.verteile(2, 150 * (st.g + 1) ** 2, lambda x, z, rd, a: (strauch(_s(st), "azalea", blumen=True), 1.5))
    pfl = [(bluetenblaetter, 6), ("grass", 4), (hohes("tall_grass"), 1), ("allium", 0.3), ("pink_tulip", 0.4),
           ("white_tulip", 0.2)]
    if st.stil == 1:
        pfl += [(bambus, 0.25), ("lily_of_the_valley", 0.5)]
    st.boden([("grass_block_s", 6), ("moss_block", 0.6), ("rooted_dirt", 0.3)], pfl, dichte=0.6, belag_dichte=0.3)
    return w


def herbstwald(seed, g=1):
    """Leuchtender Herbstwald in Rot, Orange und Gold mit Laubteppich."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        if art > 0.65:
            return _baum(_s(st), "birke", 0), 3
        if st.rng.random() < 0.12:
            return schlanke_fichte(_s(st)), 2.5
        return herbstbaum(_s(st), _herbst_laub(w, st.rng), H=int(5 + st.rng.integers(5))), 3.5

    st.verteile(4, 900 * (st.g + 1) ** 2, baum)
    st.verteile(2, 150 * (st.g + 1) ** 2, lambda x, z, rd, a: (strauch(_s(st), "oak"), 1.5))
    st.verteile(5, 30 * (st.g + 1), lambda x, z, rd, a: (liegender_stamm(_s(st), "oak"), 3))
    teppich = [("red_carpet", 0.6), ("orange_carpet", 1.2), ("yellow_carpet", 0.8), ("brown_carpet", 0.8)]
    st.boden([("podzol", 3), ("coarse_dirt", 1.5), ("rooted_dirt", 0.8), ("grass_block_s", 2)],
             teppich + [("grass", 3), ("fern", 1.5), ("brown_mushroom", 0.4), (hohes("tall_grass"), 0.6)],
             dichte=0.55 if st.stil == 0 else 0.75)
    return w


def urwald(seed, g=1):
    """Dschungel-Urwald: Urwaldriesen, Palmen, Bambus, Ranken und dichtes Blattwerk."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        if rd < 0.65 and st.rng.random() < 0.18:
            return _baum(_s(st), "dschungelriese", 1 if st.g >= 2 else 0), 6
        if st.stil == 1 and st.rng.random() < 0.3:
            return palme(_s(st)), 3
        return kleiner_laubbaum(_s(st), "jungle", H=int(6 + st.rng.integers(7)),
                                blaetter=[("jungle", 0.8), ("oak", 0.2)], breit=1.1), 3.5

    st.verteile(4, 900 * (st.g + 1) ** 2, baum)
    st.verteile(2, 260 * (st.g + 1) ** 2, lambda x, z, rd, a: (strauch(_s(st), "jungle", gross=st.rng.random() < 0.5), 1.5))
    st.boden([("podzol", 2), ("moss_block", 2), ("rooted_dirt", 1), ("grass_block_s", 3), ("mud", 0.4)],
             [("fern", 4), (hohes("large_fern"), 3), ("grass", 2), (bambus, 0.6 + st.stil * 0.8),
              (hohes("tall_grass"), 1.5), ("melon", 0.05), ("moss_carpet", 1)], dichte=0.6)
    # Ranken an allen Dschungelstämmen/Blättern
    traeger = {w.b("jungle_log", axis=a) for a in "xyz"} | {laub(w, "jungle")}
    B.ranken(w, traeger, 0.18, 6)
    for p in w.bloecke:
        if p not in w.folgen:
            w.folgen[p] = _naechster_anker(w, p)
    return w


def mangrovensumpf(seed, g=1):
    """Mangrovensumpf auf Schlamm mit Wurzeln, Schilf und Seerosen-Tümpeln."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        if st.stil == 1 and st.rng.random() < 0.4:
            return _baum(_s(st), "trauerweide", 0), 4.5
        return _baum(_s(st), "mangrove", 1 if st.rng.random() < 0.25 else 0), 4

    st.verteile(5, 800 * (st.g + 1) ** 2, baum)
    st.boden([("mud", 4), ("mangrove_roots_b", 0.8), ("muddy_mangrove_roots", 1), ("grass_block_s", 1.5),
              ("moss_block", 1)],
             [("grass", 3), (zuckerrohr, 1), (hohes("tall_grass"), 1.5), ("fern", 1), ("blue_orchid", 0.5),
              ("brown_mushroom", 0.3), ("moss_carpet", 1.5)], dichte=0.45)
    return w


def savanne(seed, g=1):
    """Savanne: vereinzelte Schirmakazien, Dornbüsche, hohes trockenes Gras."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        if st.rng.random() < 0.7:
            return _baum(_s(st), "akazie", 1 if st.rng.random() < 0.35 else 0), 6
        return kleiner_laubbaum(_s(st), "acacia", H=int(4 + st.rng.integers(3)),
                                blaetter=[("acacia", 1.0)], breit=1.3), 4

    st.verteile(7, 500 * (st.g + 1) ** 2, baum)
    st.verteile(4, 90 * (st.g + 1) ** 2, lambda x, z, rd, a: (strauch(_s(st), "acacia"), 2))
    st.verteile(8, 12 * (st.g + 1), lambda x, z, rd, a: (findling(_s(st), moosig=False, art="sand"), 2.5))
    st.boden([("coarse_dirt", 2), ("grass_block_s", 3), ("red_sand", 0.4 * st.stil), ("terracotta", 0.2)],
             [("grass", 6), (hohes("tall_grass"), 4), ("dead_bush", 0.8), ("dandelion", 0.2),
              ("orange_tulip", 0.15 * st.stil)], dichte=0.5, belag_dichte=0.35)
    return w


def mammutwald(seed, g=1):
    """Ehrfurcht gebietender Mammutwald mit Riesenstämmen über Farnteppich."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        if rd < 0.75 and st.rng.random() < 0.35:
            return _baum(_s(st), "mammutbaum", 1 if st.g >= 2 and st.rng.random() < 0.5 else 0), 7
        return schlanke_fichte(_s(st), H=int(10 + st.rng.integers(10))), 3

    st.verteile(4, 700 * (st.g + 1) ** 2, baum)
    st.verteile(5, 30 * (st.g + 1), lambda x, z, rd, a: (liegender_stamm(_s(st), "spruce"), 3)
                if st.rng.random() < 0.5 else (findling(_s(st), art="dunkel"), 2.5))
    st.boden([("podzol", 4), ("moss_block", 2), ("coarse_dirt", 1), ("rooted_dirt", 1)],
             [("fern", 6), (hohes("large_fern"), 4), ("grass", 1), ("brown_mushroom", 0.5), ("moss_carpet", 2),
              (beeren, 0.3)], dichte=0.6)
    return w


def zauberwald(seed, g=1):
    """Zauberwald: blühende Azaleen, Leuchtpilze, glimmende Flechten und Amethyst-Funkeln."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        r = st.rng.random()
        if r < 0.35:
            return _baum(_s(st), "azaleenbaum", 1 if st.g >= 1 else 0), 3.5
        if r < 0.55:
            return riesenpilz(_s(st), rot=st.stil == 0), 3
        if r < 0.75 and st.stil == 1:
            return _baum(_s(st), "kirschbaum", 0), 4
        return kleiner_laubbaum(_s(st), "oak", blaetter=[("flowering_azalea", 0.5), ("azalea", 0.3),
                                                         ("oak", 0.2)], breit=1.1), 3.5

    st.verteile(4, 800 * (st.g + 1) ** 2, baum)
    st.verteile(2, 200 * (st.g + 1) ** 2, lambda x, z, rd, a: (strauch(_s(st), "azalea", blumen=st.rng.random() < 0.6), 1.5))
    st.boden([("moss_block", 4), ("rooted_dirt", 1), ("podzol", 1), ("grass_block_s", 2)],
             [("moss_carpet", 3), (leuchtflechte, 1.0), ("fern", 2), ("allium", 0.6), ("blue_orchid", 0.5),
              ("lily_of_the_valley", 0.6), (bluetenblaetter, 1.0 * st.stil), ("torchflower", 0.2),
              (hohes("large_fern"), 1), ("small_amethyst_bud_u", 0.2)], dichte=0.55)
    # glimmende Laternen in Bäumen
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 4 and w.frei(x, y - 1, z) and st.rng.random() < 0.004 and w.P.name(b).endswith("leaves"):
            w.setze(x, y - 1, z, w.b("shroomlight"))
            w.folgen[(x, y - 1, z)] = w.folgen.get((x, y, z), -1)
    return w


def spukwald(seed, g=1):
    """Toter, gespenstischer Wald: kahle verdrehte Bäume, Spinnweben, Knochen und Seelensand."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        if st.rng.random() < 0.65:
            return _baum(_s(st), "toter_baum", 1 if st.rng.random() < 0.5 else 0), 3.5
        if st.stil == 1:
            return dunkeleiche(_s(st)), 4
        return kleiner_laubbaum(_s(st), "dark_oak", blaetter=[("dark_oak", 0.7), ("=cobweb", 0.3)], breit=0.7), 3

    st.verteile(5.5, 800 * (st.g + 1) ** 2, baum)
    st.verteile(5, 40 * (st.g + 1), lambda x, z, rd, a: (stumpf(_s(st), "dark_oak"), 1.5)
                if st.rng.random() < 0.6 else (liegender_stamm(_s(st), "dark_oak"), 3))
    st.boden([("coarse_dirt", 3), ("podzol", 2), ("soul_soil", 0.8), ("gravel", 0.5), ("mud", 0.6)],
             [("dead_bush", 3), ("grass", 1.5), ("brown_mushroom", 1), ("cobweb", 0.6), ("bone_block_y", 0.15),
              ("wither_rose", 0.1 * st.stil), ("moss_carpet", 0.5)], dichte=0.35)
    # Spinnweben in den Ästen
    for (x, y, z), b in list(w.bloecke.items()):
        if y > 3 and st.rng.random() < 0.03 and w.P.name(b).endswith(("_log", "_wood")):
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if w.frei(x + dx, y - 1, z + dz):
                    w.setze(x + dx, y - 1, z + dz, w.b("cobweb"))
                    w.folgen[(x + dx, y - 1, z + dz)] = w.folgen.get((x, y, z), -1)
                    break
    return w


def weidenaue(seed, g=1):
    """Flussaue mit Trauerweiden, Erlen, Schilf und Wildblumen."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        if st.rng.random() < 0.45:
            return _baum(_s(st), "trauerweide", 1 if st.g >= 2 and st.rng.random() < 0.3 else 0), 5
        return kleiner_laubbaum(_s(st), "oak", blaetter=[("oak", 0.6), ("jungle", 0.25), ("azalea", 0.15)]), 3.5

    st.verteile(5, 700 * (st.g + 1) ** 2, baum)
    st.verteile(2, 150 * (st.g + 1) ** 2, lambda x, z, rd, a: (strauch(_s(st), "oak"), 1.5))
    st.boden([("grass_block_s", 4), ("moss_block", 1), ("mud", 0.6), ("clay", 0.3), ("rooted_dirt", 0.5)],
             [("grass", 5), (hohes("tall_grass"), 3), (zuckerrohr, 0.8), ("blue_orchid", 0.6), ("cornflower", 0.5),
              ("azure_bluet", 0.5), (hohes("peony"), 0.2), (hohes("rose_bush"), 0.15 + 0.2 * st.stil),
              ("fern", 1)], dichte=0.6, belag_dichte=0.35)
    return w


def waldrand(seed, g=1):
    """Waldrand und Lichtung: lockere Bäume, viele Büsche und Blumen – ideal als Übergang zur Wiese."""
    st = Stueck(seed, g)
    w = st.w
    nadel = st.stil == 1

    def baum(x, z, rd, art):
        if rd < 0.35:
            return None
        if nadel:
            return schlanke_fichte(_s(st), H=int(6 + st.rng.integers(8))), 3
        if st.rng.random() < 0.3:
            return _baum(_s(st), "birke", 0), 3
        return kleiner_laubbaum(_s(st), "oak"), 3.5

    st.verteile(6, 500 * (st.g + 1) ** 2, baum)
    st.verteile(3, 300 * (st.g + 1) ** 2, lambda x, z, rd, a: (strauch(_s(st), "spruce" if nadel else
                                                                       ("azalea" if a > 0.5 else "oak"),
                                                                       gross=st.rng.random() < 0.4,
                                                                       blumen=st.rng.random() < 0.2), 1.5))
    st.boden([("grass_block_s", 6), ("coarse_dirt", 0.4)],
             [("grass", 8), (hohes("tall_grass"), 3), ("poppy", 0.8), ("dandelion", 0.8), ("cornflower", 0.6),
              ("oxeye_daisy", 0.6), ("azure_bluet", 0.4), (hohes("lilac"), 0.2), (hohes("rose_bush"), 0.2),
              (beeren, 0.3)], dichte=0.55, belag_dichte=0.2)
    return w


def unterholz(seed, g=1):
    """Dichtes Unterholz ohne große Bäume: Büsche, Jungbäume, Farne – füllt Lücken und Waldränder."""
    st = Stueck(seed, g)
    w = st.w
    st.verteile(2, 700 * (st.g + 1) ** 2,
                lambda x, z, rd, a: (strauch(_s(st), ["oak", "azalea", "spruce", "birch", "dark_oak"][int(a * 4.99)],
                                             gross=st.rng.random() < 0.5,
                                             blumen=st.stil == 1 and st.rng.random() < 0.25), 1.5)
                if st.rng.random() < 0.8 else (kleiner_laubbaum(_s(st), "oak", H=int(3 + st.rng.integers(2)),
                                                                breit=0.6), 2))
    st.boden([("podzol", 1), ("moss_block", 1), ("grass_block_s", 3), ("coarse_dirt", 0.5)],
             [("grass", 5), ("fern", 4), (hohes("large_fern"), 2), (hohes("tall_grass"), 2), (beeren, 0.6),
              ("brown_mushroom", 0.2)], dichte=0.6)
    return w


def bergwald(seed, g=1):
    """Bergwald zwischen Felsen: Fichten und Kiefern, Moospolster, Geröll."""
    st = Stueck(seed, g)
    w = st.w
    st.schnee = st.stil == 1
    st.verteile(4, 60 * (st.g + 1) ** 2, lambda x, z, rd, a: (findling(_s(st), moosig=not st.schnee,
                                                                       art="schnee" if st.schnee else "fels"), 3))

    def baum(x, z, rd, art):
        if st.rng.random() < 0.3:
            return kiefer(_s(st), H=int(9 + st.rng.integers(7))), 3.5
        return schlanke_fichte(_s(st), H=int(6 + st.rng.integers(10))), 2.6

    st.verteile(3, 800 * (st.g + 1) ** 2, baum)
    belag = [("stone", 1.5), ("andesite", 1), ("gravel", 1), ("coarse_dirt", 1.5), ("podzol", 1.5), ("moss_block", 1)]
    if st.schnee:
        belag += [("snow_block", 4)]
        pfl = [(schneeschicht, 8), ("fern", 0.5)]
    else:
        pfl = [("fern", 4), ("grass", 3), ("moss_carpet", 2), (beeren, 0.4), (hohes("large_fern"), 1)]
    st.boden(belag, pfl, dichte=0.45, belag_dichte=0.85)
    return w


def pilzwald(seed, g=1):
    """Pilzwald: Riesenpilze in Rot und Braun über Myzel, dazwischen kleine Pilze und Moos."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        if st.stil == 1 and st.rng.random() < 0.2:
            return dunkeleiche(_s(st)), 4
        return riesenpilz(_s(st), rot=art > 0.5, H=int(4 + st.rng.integers(6 + st.g))), 3.5

    st.verteile(4, 700 * (st.g + 1) ** 2, baum)
    st.boden([("mycelium", 5), ("podzol", 1), ("moss_block", 0.8)],
             [("brown_mushroom", 3), ("red_mushroom", 2.5), ("moss_carpet", 1.5), (leuchtflechte, 0.3)],
             dichte=0.35, belag_dichte=0.85)
    return w


def palmenhain(seed, g=1):
    """Palmenhain am Strand oder in der Oase: schiefe Palmen, Farne und Zuckerrohr auf Sand."""
    st = Stueck(seed, g)
    w = st.w

    def baum(x, z, rd, art):
        if st.stil == 1 and st.rng.random() < 0.25:
            return kleiner_laubbaum(_s(st), "jungle", blaetter=[("jungle", 1.0)]), 3.5
        return palme(_s(st), H=int(6 + st.rng.integers(8))), 3.5

    st.verteile(4, 600 * (st.g + 1) ** 2, baum)
    st.verteile(3, 100 * (st.g + 1) ** 2, lambda x, z, rd, a: (strauch(_s(st), "jungle"), 1.5))
    st.boden([("sand", 5), ("sandstone", 0.3), ("grass_block_s", 1.5 * st.stil + 0.3), ("coarse_dirt", 0.4)],
             [("dead_bush", 1), (zuckerrohr, 1.5), ("fern", 1 + 2 * st.stil), (hohes("tall_grass"), 0.6 + st.stil),
              ("grass", 1 + 2 * st.stil)], dichte=0.3, belag_dichte=0.6)
    return w


# ============================================================================ Hilfen


def _naechster_anker(w, p):
    x, y, z = p
    if y <= 2:
        return -1
    best, bi = 1e9, -1
    for i, (ax, az) in enumerate(w.folge_anker):
        d = (ax - x) ** 2 + (az - z) ** 2
        if d < best:
            best, bi = d, i
    return bi


def _fertig(w):
    """Sonder-Bodenblöcke auflösen und jedem Block eine Folge-Gruppe geben."""
    ersatz = {
        "minecraft:grass_block_s": w.b("grass_block", snowy=False),
        "minecraft:mangrove_roots_b": w.b("mangrove_roots", waterlogged=False),
        "minecraft:bone_block_y": w.b("bone_block", axis="y"),
        "minecraft:powder_snow_n": w.b("snow_block"),
        "minecraft:small_amethyst_bud_u": w.b("small_amethyst_bud", facing="up", waterlogged=False),
        "minecraft:podzol": w.b("podzol", snowy=False),
        "minecraft:mycelium": w.b("mycelium", snowy=False),
    }
    karte = {}
    for name, idx in [(n, w.P.b(n)) for n in ersatz]:
        karte[idx] = ersatz[name]
    plain_podzol = w.P.index.get(("minecraft:podzol", ()))
    plain_myc = w.P.index.get(("minecraft:mycelium", ()))
    for p, b in list(w.bloecke.items()):
        if b in karte and karte[b] != b:
            w.bloecke[p] = karte[b]
        elif b == plain_podzol:
            w.bloecke[p] = ersatz["minecraft:podzol"]
        elif b == plain_myc:
            w.bloecke[p] = ersatz["minecraft:mycelium"]
        if p not in w.folgen:
            w.folgen[p] = _naechster_anker(w, p)
    return w


def _mit_fertig(f):
    def g(seed, groesse=1):
        return _fertig(f(seed, groesse))
    g.__doc__ = f.__doc__
    return g


WALD = {k: (n, _mit_fertig(f)) for k, (n, f) in {
    "eichenwald": ("Eichen-Mischwald", eichenwald),
    "birkenhain": ("Birkenhain", birkenhain),
    "fichtenwald": ("Fichtenwald", fichtenwald),
    "kiefernwald": ("Kiefernwald", kiefernwald),
    "dunkelwald": ("Dunkelwald", dunkelwald),
    "kirschhain": ("Kirschblütenhain", kirschhain),
    "herbstwald": ("Herbstwald", herbstwald),
    "urwald": ("Dschungel-Urwald", urwald),
    "mangrovensumpf": ("Mangrovensumpf", mangrovensumpf),
    "savanne": ("Savanne", savanne),
    "mammutwald": ("Mammutwald", mammutwald),
    "zauberwald": ("Zauberwald", zauberwald),
    "spukwald": ("Spukwald", spukwald),
    "weidenaue": ("Weidenaue", weidenaue),
    "waldrand": ("Waldrand & Lichtung", waldrand),
    "unterholz": ("Unterholz & Gebüsch", unterholz),
    "bergwald": ("Bergwald", bergwald),
    "pilzwald": ("Pilzwald", pilzwald),
    "palmenhain": ("Palmenhain", palmenhain),
}.items()}

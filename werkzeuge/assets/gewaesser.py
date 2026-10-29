"""Flüsse, Seen & Wasserfälle – Klippenfälle, Kaskaden, Bergseen, Flussbiegungen, Stromschnellen, Sinterterrassen,
Geysir, Regenbogenfall, schwebender Wasserfall und kachelbare Flussstücke (gerade, Kurve, Gabelung).
Grundebene y = 0, Seen und Flüsse reichen unter 0."""

from __future__ import annotations

import math

import numpy as np

import wald2
from flora import _neu, _r, _stil
from lib import Rauschen, einfuegen

U = [0.6, 1.0, 1.7, 2.8]

FELS = ["stone", "andesite", "stone", "cobblestone", "tuff", "diorite", "mossy_cobblestone"]


class Land:
    """Höhenfeld-Gelände mit Wasserflächen. h[(x,z)] Oberfläche, wasser[(x,z)] Wasserspiegel,
    fall[(x,z)] = (oben, unten) für Wasserfallspalten."""

    def __init__(self, w, R, form="rund"):
        self.w = w
        self.R = R
        self.form = form
        self.h = {}
        self.wasser = {}
        self.fall = {}
        self.boden = {}
        self.rn = Rauschen(w, 6)
        self.rf = Rauschen(w, 1.7)
        for x in range(-R, R + 1):
            for z in range(-R, R + 1):
                if form == "rund":
                    d = math.hypot(x, z) / R
                    if d > 1.0 + 0.08 * self.rf(x, 0, z) - 0.04:
                        continue
                self.h[(x, z)] = 0

    def zellen(self):
        return list(self.h)

    def heben(self, f):
        for p in self.h:
            self.h[p] = int(round(f(*p, self.h[p])))

    def fluss(self, pts, breite, spiegel, tiefe=2, ufer=1.5):
        """Flussbett entlang Polylinie pts [(x, z)] mit Wasserspiegel spiegel (int oder Funktion t->int)."""
        seg = []
        L = 0
        for a, b in zip(pts, pts[1:]):
            l = math.dist(a, b)
            seg.append((a, b, L, l))
            L += l
        for (x, z) in list(self.h):
            best = None
            for (a, b, l0, l) in seg:
                dx, dz = b[0] - a[0], b[1] - a[1]
                t = max(0, min(1, ((x - a[0]) * dx + (z - a[1]) * dz) / max(l * l, 1e-6)))
                d = math.hypot(x - a[0] - dx * t, z - a[1] - dz * t)
                if best is None or d < best[0]:
                    best = (d, (l0 + t * l) / max(L, 1e-6))
            d, tt = best
            br = breite(tt) if callable(breite) else breite
            sp = spiegel(tt) if callable(spiegel) else spiegel
            if d < br:
                tief = tiefe * (1 - (d / br) ** 2) + 0.6
                self.h[(x, z)] = min(self.h[(x, z)], int(sp - tief))
                self.wasser[(x, z)] = sp
            elif d < br + ufer and self.h[(x, z)] > sp:
                self.h[(x, z)] = min(self.h[(x, z)], sp + int((d - br) * 0.8))

    def see(self, cx, cz, r, spiegel, tiefe=3, rauh=0.25):
        for (x, z) in list(self.h):
            d = math.hypot(x - cx, z - cz) / (r * (1 + rauh * (self.rn(x, 9, z) - 0.5)))
            if d < 1:
                self.h[(x, z)] = min(self.h[(x, z)], int(spiegel - 1 - tiefe * (1 - d * d)))
                self.wasser[(x, z)] = spiegel

    def bauen(self, gras="grass_block", fels=None, bett=("gravel", "sand", "clay", "gravel"), unten=-4,
              fels_ab=None, schnee_ab=None):
        w = self.w
        fels = fels or FELS
        for (x, z), h in self.h.items():
            nb = [self.h.get((x + dx, z + dz), h) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            steil = max(abs(h - n) for n in nb) >= 2
            nass = (x, z) in self.wasser and self.wasser[(x, z)] > h
            for y in range(min(unten, h - 2), h + 1):
                if y == h:
                    if nass:
                        blk = bett[int(self.rf(x, 1, z) * 3.99)]
                    elif steil or (fels_ab is not None and h >= fels_ab):
                        blk = fels[int(self.rf(x, y, z) * (len(fels) - 0.01))]
                    elif schnee_ab is not None and h >= schnee_ab:
                        blk = "snow_block"
                    else:
                        blk = self.boden.get((x, z), gras)
                elif y > h - 3 and not steil and not nass:
                    blk = "dirt"
                else:
                    blk = fels[int(self.rf(x, y, z) * (len(fels) - 0.01))]
                w.setze(x, y, z, w.b(blk, snowy=False) if blk in ("grass_block", "podzol", "mycelium") else
                        w.b(blk))
            if nass:
                for y in range(h + 1, self.wasser[(x, z)] + 1):
                    w.setze(x, y, z, w.b("water", level=0))
        for (x, z), (oben, unten_) in self.fall.items():
            for y in range(unten_, oben + 1):
                w.setze(x, y, z, w.b("water", level=0 if y == oben else 8))

    def bepflanzen(self, dichte=0.3, baeume=0, arten=("oak", "birch"), blumen=True, ufer_schilf=True, seed=1):
        w = self.w
        rng = w.rng
        frei = [(x, z) for (x, z), h in self.h.items() if (x, z) not in self.wasser and h >= 0]
        for (x, z) in frei:
            h = self.h[(x, z)]
            if not w.frei(x, h + 1, z):
                continue
            top = w.P.name(w.bloecke.get((x, h, z), 0))
            if not top.endswith(("grass_block", "podzol", "moss_block")):
                continue
            nah_wasser = any((x + dx, z + dz) in self.wasser for dx in (-1, 0, 1) for dz in (-1, 0, 1))
            r = rng.random()
            if nah_wasser and ufer_schilf and r < 0.35:
                for y in range(h + 1, h + 2 + int(rng.integers(0, 3))):
                    w.setze(x, y, z, w.b("sugar_cane", age=0))
            elif r < dichte * 0.5:
                w.setze(x, h + 1, z, w.b("grass"))
            elif r < dichte * 0.65:
                w.setze(x, h + 1, z, w.b("fern"))
            elif blumen and r < dichte * 0.75:
                w.setze(x, h + 1, z, w.b(["poppy", "dandelion", "azure_bluet", "oxeye_daisy", "cornflower"][
                    int(rng.integers(5))]))
        rng.shuffle(frei)
        gesetzt = []
        for (x, z) in frei:
            if len(gesetzt) >= baeume:
                break
            if any(math.hypot(x - a, z - b) < 7 for a, b in gesetzt):
                continue
            if any((x + dx, z + dz) in self.wasser for dx in (-2, 0, 2) for dz in (-2, 0, 2)):
                continue
            h = self.h[(x, z)]
            art = arten[len(gesetzt) % len(arten)]
            sd = int(rng.integers(1, 10 ** 6))
            if art == "fichte":
                b = wald2.fichte(sd)
            elif art == "kiefer":
                b = wald2.kiefer(sd)
            elif art == "weide":
                b = wald2.weide(sd)
            elif art == "birke":
                b = wald2.birke(sd)
            elif art == "palme":
                b = wald2.palme(sd)
            elif art == "busch":
                b = wald2.busch(sd)
            else:
                b = wald2.laubbaum(sd, art)
            einfuegen(w, b, x, h, z)
            gesetzt.append((x, z))

    def steine(self, n, groesse=1.5, im_wasser=True, mat=None):
        w = self.w
        rng = w.rng
        mat = mat or ["mossy_cobblestone", "cobblestone", "andesite", "stone", "mossy_cobblestone"]
        zellen = [p for p in self.h if (p in self.wasser) == im_wasser]
        for k in range(n):
            if not zellen:
                return
            x, z = zellen[int(rng.integers(len(zellen)))]
            r = groesse * (0.6 + 0.8 * rng.random())
            y0 = self.h[(x, z)]
            for dx in range(-int(r) - 1, int(r) + 2):
                for dz in range(-int(r) - 1, int(r) + 2):
                    for dy in range(0, int(r * 1.3) + 2):
                        if dx * dx + dz * dz + (dy * 1.1) ** 2 <= r * r:
                            w.setze(x + dx, y0 + dy, z + dz, w.b(mat[(dx * 3 + dy + dz * 7) % len(mat)]))


def gischt(w, x, y, z, r=2.0):
    """Weiße Gischt am Fuß eines Falls (Wolle/Glas-Flocken knapp über dem Wasser)."""
    rng = w.rng
    for k in range(int(r * r * 4)):
        a = rng.random() * 6.28
        d = rng.random() * r
        p = (round(x + math.cos(a) * d), y + int(rng.random() * 2), round(z + math.sin(a) * d))
        if w.frei(*p):
            w.setze(*p, w.b("white_stained_glass") if rng.random() < 0.7 else w.b("white_carpet"))


def fall_spalten(land, x0, x1, z, oben, unten):
    for x in range(x0, x1 + 1):
        land.fall[(x, z)] = (oben, unten)


# ============================================================================ Wasserfälle

def klippenfall(seed, g=2):
    """Klippenwasserfall: ein Fluss stürzt über eine hohe, zerklüftete Felswand in ein tiefes, grünes Becken;
    Gischt, bemooste Felsen, Farne und Bäume am Rand."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 8)
    L = Land(w, R)
    H = _r(14 * u + 5)
    zc = -round(R * 0.15)
    L.heben(lambda x, z, h: H + 2 * L.rn(x, 0, z) if z < zc + 1.5 * math.sin(x * 0.3) else
            1.2 * L.rn(x, 3, z))
    B = max(2, _r(2.5 * u))
    L.fluss([(0, -R), (0, zc - 1)], B, H, tiefe=2)
    L.see(0, zc + R * 0.35, R * 0.4, 0, tiefe=_r(3 * u + 1))
    L.fluss([(0, zc + R * 0.5), (round(R * 0.3), R)], B, 0, tiefe=1)
    fall_spalten(L, -B + 1, B - 1, zc, H, 1)
    L.bauen()
    L.bepflanzen(0.4, baeume=3 + 3 * g, arten=("fichte", "oak", "birke"))
    L.steine(4 + 2 * g, 1.2 * u + 0.5, im_wasser=True)
    gischt(w, 0, 1, zc + 2, 2 + u)
    return w


def kaskaden(seed, g=2):
    """Kaskaden: ein Bach springt über fünf breite Felsstufen hinab, jede mit eigenem kleinen Becken, von
    Moos und Farnen gesäumt."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 7)
    L = Land(w, R)
    stufen = 5
    sh = _r(2.5 * u + 1)
    L.heben(lambda x, z, h: max(0, int((R * 0.7 - z) / (1.6 * R / stufen))) * sh + 1.5 * L.rn(x, 0, z))
    B = max(2, _r(2.2 * u))
    pts = [(round(math.sin(k * 0.9) * R * 0.15), round(-R + k * 2 * R / 8)) for k in range(9)]

    def spiegel(t):
        z = -R + t * 2 * R
        return max(0, int((R * 0.7 - z) / (1.6 * R / stufen))) * sh

    L.fluss(pts, B, spiegel, tiefe=1)
    for k in range(1, stufen + 1):
        zk = round(R * 0.7 - k * 1.6 * R / stufen)
        xk = round(math.sin((zk + R) / (2 * R / 8) * 0.9) * R * 0.15)
        for x in range(xk - B + 1, xk + B):
            if (x, zk) in L.h:
                L.fall[(x, zk)] = (k * sh, (k - 1) * sh + 1)
    L.bauen(gras="moss_block")
    L.bepflanzen(0.5, baeume=2 + 2 * g, arten=("birke", "oak", "busch"))
    L.steine(3 + g, 1.0 * u + 0.4, im_wasser=False)
    return w


def zwillingsfaelle(seed, g=2):
    """Zwillingsfälle: zwei Wasserfälle stürzen nebeneinander aus einer halbrunden Felswand in einen gemeinsamen
    See, dazwischen eine Felsnase mit einer Kiefer."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 8)
    L = Land(w, R)
    H = _r(16 * u + 5)
    L.heben(lambda x, z, h: H + 2 * L.rn(x, 0, z) if math.hypot(x, z + R * 0.2) > R * 0.55 and z < R * 0.25
            else 1.2 * L.rn(x, 3, z))
    L.see(0, -round(R * 0.2), R * 0.5, 0, tiefe=_r(3 * u + 1), rauh=0.1)
    B = max(2, _r(1.8 * u))
    for sx in (-1, 1):
        a = -math.pi / 2 + sx * 0.5
        rx, rz = round(math.cos(a) * R * 0.55), round(math.sin(a) * R * 0.55 - R * 0.2)
        L.fluss([(sx * R * 0.6, -R), (rx, rz - 1)], B, H, tiefe=2)
        for x in range(rx - B + 1, rx + B):
            L.fall[(x, rz)] = (H, 1)
    L.fluss([(0, R * 0.3), (0, R)], B + 1, 0, tiefe=1)
    L.bauen()
    L.bepflanzen(0.4, baeume=3 + 2 * g, arten=("kiefer", "fichte", "birke"))
    einfuegen(w, wald2.kiefer(seed), 0, L.h.get((0, -R + 2), H), -R + 2)
    return w


def schleierfall(seed, g=2):
    """Schleierfall: ein breiter, dünner Wasservorhang fällt über einen überhängenden Felsbogen; dahinter eine
    trockene Grotte mit Pfad, Laternen und Tropfsteinen."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 7)
    L = Land(w, R)
    H = _r(13 * u + 5)
    L.heben(lambda x, z, h: H + 1.5 * L.rn(x, 0, z) if z < 2 else 1.0 * L.rn(x, 3, z))
    B = _r(5 * u + 2)
    L.fluss([(0, -R), (0, -1)], B, H, tiefe=1)
    L.see(0, round(R * 0.35), R * 0.45, 0, tiefe=2)
    L.bauen()
    w_ = w
    gh = _r(5 * u + 2)
    for x in range(-B - 1, B + 2):
        for z in range(-_r(5 * u + 2), 2):
            for y in range(1, gh + 1):
                if (x / (B + 1.5)) ** 2 + ((y - 1) / gh) ** 2 < 1:
                    w_.bloecke.pop((x, y, z), None)
            w_.setze(x, 0, z, w_.b("gravel" if (x + z) % 3 else "cobblestone"))
    for x in range(-B + 1, B):
        for y in range(1, H + 1):
            w_.setze(x, y, 2, w_.b("water", level=0 if y == H else 8))
        w_.setze(x, H, 1, w_.b("water", level=0))
    for k in range(4):
        x = -B + 1 + k * (2 * B - 2) // 3
        w_.setze(x, 1, -_r(5 * u + 2) + 1, w_.b("lantern", hanging=False, waterlogged=False))
        w_.setze(x, gh, -2, w_.b("pointed_dripstone", vertical_direction="down", thickness="tip",
                                 waterlogged=False), False)
    L.bepflanzen(0.5, baeume=2 + g, arten=("oak", "birke"))
    return w


def regenbogenfall(seed, g=2):
    """Regenbogenfall: ein hoher Wasserfall, in dessen Gischt ein Regenbogen aus farbigem Glas steht, mit Blumen
    und Kristallen am Becken – ein Zauberort."""
    w = klippenfall(seed, g)
    u = U[g]
    R = _r(18 * u + 8)
    zc = -round(R * 0.15)
    farben = ["red_stained_glass", "orange_stained_glass", "yellow_stained_glass", "lime_stained_glass",
              "light_blue_stained_glass", "blue_stained_glass", "purple_stained_glass"]
    Rb = R * 0.55
    for i, f in enumerate(farben):
        r = Rb - i * 0.9
        for k in range(int(r * 4)):
            a = k / (r * 4) * math.pi
            x, y = round(math.cos(a) * r), round(math.sin(a) * r * 0.75)
            w.setze(x, y + 1, zc + round(R * 0.35), w.b(f), False)
    for k in range(10):
        a = w.rng.random() * 6.28
        x, z = round(math.cos(a) * R * 0.5), zc + round(R * 0.35) + round(math.sin(a) * R * 0.5)
        y = max([p[1] for p in w.bloecke if p[0] == x and p[2] == z] + [0])
        if not w.P.name(w.bloecke.get((x, y, z), 0)).endswith("water"):
            w.setze(x, y + 1, z, w.b("amethyst_cluster", facing="up", waterlogged=False), False)
    return w


def schwebender_fall(seed, g=2):
    """Schwebender Wasserfall: eine Felsinsel schwebt über einem See, aus ihrer Quelle stürzt ein Wasserfall
    durch die Luft hinab, Wurzeln und Ranken hängen herab."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    L = Land(w, R)
    L.see(0, 0, R * 0.75, 0, tiefe=_r(3 * u + 1))
    L.bauen()
    L.bepflanzen(0.4, baeume=2, arten=("birke",))
    Y = _r(16 * u + 6)
    r = 6 * u + 2
    rn = Rauschen(w, 2.5)
    unten = {}
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            d = math.hypot(x, z) / r
            if d > 1:
                continue
            tief = int((1 - d) ** 0.7 * r * 1.4 * (0.7 + 0.5 * rn(x, 0, z))) + 1
            unten[(x, z)] = Y - tief
            for y in range(Y - tief, Y + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == Y else w.b("dirt") if y > Y - 3 else
                        w.b(FELS[(x + y * 3 + z) % len(FELS)]))
    for x in range(-1, 2):
        for z in range(0, int(r) + 1):
            w.setze(x, Y, z, w.b("water", level=0))
            w.setze(x, Y - 1, z, w.b("gravel"))
    for x in range(-1, 2):
        zz = int(r) + 1
        for y in range(1, Y + 1):
            w.setze(x, y, zz, w.b("water", level=0 if y == Y else 8))
    for k in range(int(10 * u)):
        a = w.rng.random() * 6.28
        d = w.rng.random() * r * 0.8
        x, z = round(math.cos(a) * d), round(math.sin(a) * d)
        y0 = unten.get((x, z), Y)
        for k2 in range(int(2 + w.rng.integers(5))):
            w.setze(x, y0 - 1 - k2, z, w.b("hanging_roots", waterlogged=False), False)
    einfuegen(w, wald2.laubbaum(seed, "oak", H=_r(6 * u + 3)), -2, Y, -2)
    gischt(w, 0, 1, int(r) + 1, 2 + u)
    return w


# ============================================================================ Seen & Teiche

def bergsee(seed, g=2):
    """Bergsee: ein tiefblauer See zwischen Felshängen mit Geröll, Fichten am Ufer, einem kleinen Bootssteg und
    schneebedeckten Kuppen im Hintergrund."""
    w = _neu(seed)
    u = U[g]
    R = _r(20 * u + 8)
    L = Land(w, R)
    H = 12 * u + 4
    L.heben(lambda x, z, h: max(0, (math.hypot(x, z) / R - 0.45) * 2) * H * (0.7 + 0.6 * L.rn(x, 0, z)) +
            (H * 0.8 * max(0, -z / R - 0.3) * 2))
    L.see(0, round(R * 0.05), R * 0.45, 0, tiefe=_r(4 * u + 1))
    L.bauen(fels_ab=_r(H * 0.6), schnee_ab=_r(H * 1.1))
    L.bepflanzen(0.3, baeume=4 + 3 * g, arten=("fichte", "fichte", "kiefer"))
    zs = round(R * 0.5)
    for z in range(round(R * 0.25), zs + 1):
        for x in (0, 1):
            w.setze(x, 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
        if z % 3 == 0:
            w.setze(0, 0, z, w.b("spruce_log", axis="y"))
    L.steine(3 + g, 1.5 * u, im_wasser=False)
    return w


def kratersee(seed, g=2):
    """Kratersee: ein kreisrunder See in einem erloschenen Vulkankrater, schroffe Kraterränder aus dunklem
    Gestein, Basaltsäulen und eine kleine Insel in der Mitte."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 8)
    L = Land(w, R)
    H = 10 * u + 4
    L.heben(lambda x, z, h: H * math.exp(-((math.hypot(x, z) / R - 0.7) / 0.2) ** 2) * (0.7 + 0.5 * L.rn(x, 0, z)))
    L.see(0, 0, R * 0.55, 0, tiefe=_r(5 * u + 1), rauh=0.08)
    for (x, z) in list(L.h):
        if math.hypot(x, z) < R * 0.1:
            L.h[(x, z)] = 1
            L.wasser.pop((x, z), None)
    L.bauen(fels=["basalt", "blackstone", "tuff", "andesite", "smooth_basalt"], fels_ab=_r(H * 0.3))
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) == "minecraft:basalt":
            w.bloecke[(x, y, z)] = w.b("basalt", axis="y")
    L.bepflanzen(0.3, baeume=2 + g, arten=("birke", "busch"))
    einfuegen(w, wald2.laubbaum(seed, "oak", H=_r(5 * u + 3)), 0, 1, 0)
    return w


def weiher_insel(seed, g=1):
    """Weiher mit Insel: ein stiller Weiher, eine Bogenbrücke zur Insel mit Trauerweide und Bank, Seerosen und
    Schilf am Ufer."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    L = Land(w, R)
    L.see(0, 0, R * 0.7, 0, tiefe=2, rauh=0.15)
    ri = R * 0.22
    for (x, z) in list(L.h):
        if math.hypot(x - 2, z) < ri:
            L.h[(x, z)] = 1
            L.wasser.pop((x, z), None)
    L.bauen()
    L.bepflanzen(0.5, baeume=3 + 2 * g, arten=("oak", "birke", "busch"))
    einfuegen(w, wald2.weide(seed, H=_r(6 * u + 3)), 2, 1, 0)
    xb = round(2 + ri)
    for x in range(xb, round(R * 0.75) + 1):
        t = (x - xb) / max(1, round(R * 0.75) - xb)
        y = 1 + round(math.sin(t * math.pi) * 1.5 * u)
        for z in (-1, 0, 1):
            w.setze(x, y, z, w.b("oak_slab", type="bottom", waterlogged=False))
        for z in (-2, 2):
            w.setze(x, y + 1, z, w.b("oak_fence", north=False, south=False, east=True, west=True, waterlogged=False))
    for (x, z), sp in L.wasser.items():
        if w.rng.random() < 0.04:
            w.setze(x, sp + 1, z, w.b("lily_pad"), False)
    return w


def bootshaus_see(seed, g=1):
    """Seeufer mit Bootshaus: ein Holzbootshaus auf Pfählen über dem Wasser, ein Ruderboot darin, Steg mit Pollern,
    Kiesstrand und Badeleiter."""
    import pracht as P
    from boote import ruderboot
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    L = Land(w, R)
    L.see(0, round(R * 0.4), R * 0.9, 0, tiefe=_r(2 * u + 1), rauh=0.05)
    L.bauen(bett=("gravel", "sand", "gravel", "clay"))
    for (x, z), h in L.h.items():
        if (x, z) not in L.wasser and any((x + dx, z) in L.wasser for dx in (-2, 2)):
            w.setze(x, h, z, w.b("gravel"))
    L.bepflanzen(0.4, baeume=3 + 2 * g, arten=("birke", "fichte"))
    a, b = _r(2.5 * u + 1, 2), _r(4 * u + 2, 3)
    z0 = -round(R * 0.2)
    for x in range(-a, a + 1):
        for z in range(z0, z0 + 2 * b + 1):
            if abs(x) == a and (z - z0) % 2 == 0:
                for y in range(-2, 1):
                    w.setze(x, y, z, w.b("spruce_log", axis="y"))
            if abs(x) == a:
                w.setze(x, 1, z, w.b("spruce_planks"))
    st = P.Stil(w, wand=["spruce_planks", "dark_oak_planks", "stripped_spruce_log"], sockel="holz_dunkel",
                gesims="stone_brick", dach="mcw_holz", holz="spruce", laeden=False, blumen=0)
    P.gebaeude(w, st, -a, z0, a, z0 + 2 * b, y0=2, etagen=1, eh=4, dach="sattel", first_x=False, tuer="north",
               gauben=False, kamine=0, sockel_h=0)
    for x in range(-a + 1, a):
        for y in range(2, 6):
            w.bloecke.pop((x, y, z0 + 2 * b), None)
    einfuegen(w, ruderboot(seed, 0), 0, 0, z0 + b)
    return w


def sinterterrassen(seed, g=2):
    """Sinterterrassen: schneeweiße Kalkbecken stufen sich einen Hang hinab, jedes randvoll mit türkisblauem
    Wasser, mit überhängenden Tropfrändern."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    n = 5 + g
    sh = 2
    rng = w.rng
    for k in range(n):
        z0 = -R + k * (2 * R // n)
        y0 = (n - k) * sh
        for x in range(-R, R + 1):
            for z in range(z0, z0 + 2 * R // n + 1):
                if math.hypot(x, z) > R:
                    continue
                for y in range(-1, y0 + 1):
                    w.setze(x, y, z, w.b("calcite" if y > y0 - 2 else "diorite"))
        for j in range(int(2 + u)):
            cx = round(-R * 0.6 + j * R * 1.2 / max(1, int(1 + u)) + rng.random() * 2)
            cz = z0 + R // n
            r = (R / n) * 0.9 + rng.random()
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                for z in range(int(cz - r * 0.8) - 1, int(cz + r * 0.8) + 2):
                    d = ((x - cx) / r) ** 2 + ((z - cz) / (r * 0.8)) ** 2
                    if d < 1 and math.hypot(x, z) < R - 1:
                        w.setze(x, y0 + 1, z, w.b("water", level=0) if d < 0.8 else w.b("calcite"))
                        if d < 0.8:
                            w.setze(x, y0, z, w.b("light_blue_terracotta" if (x + z) % 3 else "diamond_block"
                                                  if False else "light_blue_concrete"))
                    elif d < 1.2 and math.hypot(x, z) < R - 1:
                        w.setze(x, y0 + 1, z, w.b("calcite"))
    return w


def geysir(seed, g=2):
    """Geysir: aus einem Sinterkegel schießt eine hohe Wasser- und Dampffontäne, ringsum bunte Mineralbecken in
    Orange und Türkis, Dampfschwaden und karger Boden."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    L = Land(w, R)
    L.heben(lambda x, z, h: max(0, 3 * u * (1 - math.hypot(x, z) / (R * 0.35))))
    L.bauen(gras="coarse_dirt", fels=["calcite", "tuff", "diorite", "calcite"])
    rng = w.rng
    for k in range(int(4 + 2 * u)):
        a = k / (4 + 2 * u) * 6.28 + 0.3
        cx, cz = math.cos(a) * R * 0.62, math.sin(a) * R * 0.62
        r = 1.6 * u + 1
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for z in range(int(cz - r) - 1, int(cz + r) + 2):
                d = math.hypot(x - cx, z - cz) / r
                if d < 1:
                    w.setze(x, 0, z, w.b("water", level=0))
                    w.setze(x, -1, z, w.b("light_blue_concrete" if d < 0.5 else "cyan_terracotta"))
                elif d < 1.4:
                    w.setze(x, 0, z, w.b(["orange_terracotta", "yellow_terracotta", "white_terracotta"][
                        int((d - 1) * 7) % 3]))
    top = max(L.h.get((0, 0), 0), 1)
    Hf = _r(18 * u + 6)
    for y in range(top, top + Hf):
        r = 0.6 + (y - top) / Hf * 1.8 * u
        for x in range(-3, 4):
            for z in range(-3, 4):
                if x * x + z * z <= r * r:
                    if x == 0 and z == 0:
                        w.setze(x, y, z, w.b("water", level=0 if y == top + Hf - 1 else 8))
                    elif rng.random() < 0.55:
                        w.setze(x, y, z, w.b("white_stained_glass"), False)
    w.setze(0, top + Hf, 0, w.b("water", level=0))
    return w


def heisse_quelle(seed, g=1):
    """Heiße Quelle: dampfende, terrassierte Steinbecken zwischen Felsen und Bambus, Holzstege, Laternen und
    Handtuchstangen – ein Badeplatz in den Bergen."""
    w = _neu(seed)
    u = U[g]
    R = _r(13 * u + 6)
    L = Land(w, R)
    L.heben(lambda x, z, h: max(0, -z / R) * 6 * u + 1.2 * L.rn(x, 0, z))
    L.bauen(gras="moss_block")
    rng = w.rng
    for k in range(3):
        cx, cz = round((k - 1) * R * 0.45), round(-R * 0.2 + k % 2 * R * 0.3)
        r = 2.5 * u + 1.5
        y0 = L.h.get((cx, cz), 0)
        for x in range(int(cx - r) - 2, int(cx + r) + 3):
            for z in range(int(cz - r) - 2, int(cz + r) + 3):
                d = math.hypot(x - cx, z - cz)
                if d < r:
                    for y in range(y0 - 1, y0 + 3):
                        w.bloecke.pop((x, y, z), None)
                    w.setze(x, y0 - 2, z, w.b("smooth_stone"))
                    w.setze(x, y0 - 1, z, w.b("water", level=0))
                    w.setze(x, y0, z, w.b("water", level=0))
                    if rng.random() < 0.15:
                        w.setze(x, y0 + 1 + int(rng.integers(0, 3)), z, w.b("white_stained_glass"))
                elif d < r + 1.3:
                    for y in range(y0 - 2, y0 + 1):
                        w.setze(x, y, z, w.b(["mossy_cobblestone", "andesite", "stone"][(x + z) % 3]))
        w.setze(round(cx + r + 1), y0 + 1, cz, w.b("lantern", hanging=False, waterlogged=False))
    for k in range(int(6 * u)):
        x, z = int(rng.integers(-R + 2, R - 2)), round(R * 0.6)
        if (x, z) in L.h:
            from wald import bambus
            w.folgen = {}
            bambus(w, x, L.h[(x, z)] + 1, z)
    if hasattr(w, "folgen"):
        del w.folgen
    return w


def tropfsteinsee(seed, g=2):
    """Tropfsteinsee: ein unterirdischer See unter einem offenen Felsgewölbe, Stalaktiten und Stalagmiten,
    leuchtende Flechten und ein schmaler Uferpfad."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    L = Land(w, R)
    L.see(0, 0, R * 0.7, 0, tiefe=_r(3 * u + 1))
    L.bauen(gras="stone", bett=("gravel", "dripstone_block", "gravel", "clay"))
    H = _r(10 * u + 5)
    rng = w.rng
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            d = math.hypot(x, z) / R
            if d > 1 or z > R * 0.4:
                continue
            dicke = int(2 + 2 * u)
            yb = H + int(3 * (1 - d * d))
            for y in range(yb, yb + dicke):
                w.setze(x, y, z, w.b(["dripstone_block", "stone", "tuff", "andesite"][(x + y + z) % 4]))
            if rng.random() < 0.12:
                ln = int(1 + rng.integers(int(2 + 3 * u)))
                for k in range(ln):
                    w.setze(x, yb - 1 - k, z, w.b("pointed_dripstone", vertical_direction="down",
                                                  thickness="tip" if k == ln - 1 else "frustum", waterlogged=False))
            elif rng.random() < 0.04:
                w.setze(x, yb - 1, z, w.b("glow_lichen", up=True, down=False, north=False, south=False,
                                          east=False, west=False, waterlogged=False))
    for sx in (-1, 1):
        for y in range(0, H + 4):
            for z in range(-R, round(R * 0.4)):
                x = sx * R + (0 if sx < 0 else 0)
                if (x, z) in L.h or True:
                    for dx in range(3):
                        p = (sx * (R - dx), y, z)
                        if math.hypot(p[0], z) <= R + 1:
                            w.setze(*p, w.b(["dripstone_block", "stone", "tuff"][(y + z + dx) % 3]))
    for (x, z), h in L.h.items():
        if (x, z) not in L.wasser and rng.random() < 0.06:
            for k in range(int(1 + rng.integers(3))):
                w.setze(x, h + 1 + k, z, w.b("pointed_dripstone", vertical_direction="up", thickness="tip" if k == 2
                                             else "frustum", waterlogged=False), False)
    return w


# ============================================================================ Flüsse

def flussbiegung(seed, g=2):
    """Flussbiegung: ein breiter Fluss schwingt in einer weiten Schleife, mit Kiesbank am Innenufer, Prallhang
    mit Abbruchkante, Weiden und Schilf."""
    w = _neu(seed)
    u = U[g]
    R = _r(20 * u + 8)
    L = Land(w, R)
    L.heben(lambda x, z, h: 2 * L.rn(x, 0, z) + 1)
    pts = [(-R - 2, -R * 0.4), (-R * 0.3, -R * 0.5), (R * 0.2, -R * 0.1), (R * 0.1, R * 0.4), (-R * 0.4, R * 0.6),
           (-R - 2, R * 0.6)]
    pts = [(round(a), round(b)) for a, b in pts]
    B = _r(3.5 * u + 1)
    L.fluss(pts, B, 0, tiefe=2)
    for (x, z) in list(L.h):
        if math.hypot(x + R * 0.05, z - R * 0.15) < R * 0.25 and (x, z) not in L.wasser:
            L.boden[(x, z)] = "gravel"
    L.bauen()
    L.bepflanzen(0.45, baeume=4 + 3 * g, arten=("weide", "oak", "birke"))
    return w


def stromschnellen(seed, g=2):
    """Stromschnellen: ein Fluss schießt durch ein enges, felsiges Bett mit großen Findlingen, kleinen Stufen
    und weißer Gischt."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 8)
    L = Land(w, R)
    L.heben(lambda x, z, h: 3 * u * L.rn(x, 0, z) + 2 * u * max(0, abs(x) / R - 0.2) * 4)

    def spiegel(t):
        return int(round((1 - t) * 4 * u))

    L.fluss([(round(math.sin(k * 0.7) * 3), -R + k * 2 * R // 8) for k in range(9)], max(2, _r(2.5 * u)), spiegel,
            tiefe=1)
    L.bauen()
    L.steine(int(8 + 6 * u), 1.0 * u + 0.6, im_wasser=True)
    rng = w.rng
    for k in range(int(20 * u)):
        cells = list(L.wasser)
        x, z = cells[int(rng.integers(len(cells)))]
        y = L.wasser[(x, z)] + 1
        if w.frei(x, y, z):
            w.setze(x, y, z, w.b("white_carpet") if rng.random() < 0.5 else w.b("white_stained_glass"))
    L.bepflanzen(0.3, baeume=3 + 2 * g, arten=("fichte", "kiefer"))
    return w


def flussdelta(seed, g=2):
    """Flussdelta: ein Fluss teilt sich in viele Arme, die zwischen Sandbänken, Schilfinseln und Treibholz ins
    Meer münden."""
    w = _neu(seed)
    u = U[g]
    R = _r(20 * u + 8)
    L = Land(w, R)
    L.heben(lambda x, z, h: 1 if z < R * 0.5 else 0)
    L.see(0, R + R * 0.3, R * 0.8, 0, tiefe=3, rauh=0.1)
    L.fluss([(0, -R), (0, -round(R * 0.2))], _r(3 * u + 1), 0, tiefe=2)
    rng = w.rng
    for k in range(5 + g):
        a = -0.9 + k * 1.8 / (4 + g)
        pts = [(0, -round(R * 0.2))]
        for j in range(1, 5):
            t = j / 4
            pts.append((round(math.sin(a) * R * t + rng.normal() * 2), round(-R * 0.2 + t * R * 1.2)))
        L.fluss(pts, max(1.4, 1.6 * u), 0, tiefe=1)
    for (x, z) in L.h:
        if (x, z) not in L.wasser and z > 0:
            L.boden[(x, z)] = "sand" if rng.random() < 0.6 else "grass_block"
    L.bauen()
    L.bepflanzen(0.6, baeume=2, arten=("weide",))
    for k in range(int(4 * u)):
        x, z = int(rng.integers(-R, R)), int(rng.integers(0, R))
        if (x, z) in L.h:
            for d in range(3):
                w.setze(x + d, L.h[(x, z)] + 1, z, w.b("stripped_oak_log", axis="x"), False)
    return w


def bachquelle(seed, g=1):
    """Bachquelle: aus einem bemoosten Felsspalt sprudelt eine Quelle, ein kleiner Bach plätschert über Steine
    durch Farne und Moos davon."""
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 5)
    L = Land(w, R)
    L.heben(lambda x, z, h: max(0, -z / R) * 5 * u + 1.2 * L.rn(x, 0, z))
    L.fluss([(0, -round(R * 0.45)), (2, 0), (-1, R)], max(1.2, 1.3 * u), lambda t: int(round((1 - t) * 2.5 * u)),
            tiefe=1)
    L.bauen(gras="moss_block")
    zq = -round(R * 0.5)
    hq = L.h.get((0, zq), 3)
    for x in range(-3, 4):
        for z in range(zq - 3, zq + 1):
            for y in range(hq, hq + _r(4 * u) + 2 - abs(x)):
                if not (abs(x) <= 0 and z == zq):
                    w.setze(x, y, z, w.b(["mossy_cobblestone", "mossy_stone_bricks", "stone", "moss_block"][
                        (x + y + z) % 4]))
    w.setze(0, hq + 1, zq, w.b("water", level=0))
    L.bepflanzen(0.6, baeume=2 + g, arten=("birke", "busch"))
    L.steine(4, 0.8 * u, im_wasser=True)
    return w


def gletscherbach(seed, g=2):
    """Gletscherbach: milchig-türkises Schmelzwasser schießt unter einer blauen Gletscherzunge hervor und fließt
    durch Moränengeröll und Schneereste."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 7)
    L = Land(w, R)
    L.heben(lambda x, z, h: max(0, -z / R) * 4 * u + 1.5 * L.rn(x, 0, z))
    L.fluss([(0, -R), (1, 0), (-2, R)], max(1.5, 1.8 * u), lambda t: int(round((1 - t) * 3 * u)), tiefe=1)
    L.bauen(gras="gravel", fels=["andesite", "stone", "diorite", "gravel", "cobblestone"])
    for (x, z), h in L.h.items():
        if (x, z) not in L.wasser and w.rng.random() < 0.15:
            w.setze(x, h + 1, z, w.b("snow", layers=int(1 + w.rng.integers(3))))
    for x in range(-R, R + 1):
        for z in range(-R, -round(R * 0.35)):
            if (x, z) not in L.h:
                continue
            hh = int((-z - R * 0.35) / R * 10 * u + 2)
            y0 = L.h[(x, z)]
            for y in range(y0 + 1, y0 + hh + 1):
                if (x, z) in L.wasser and y < y0 + 4:
                    continue
                w.setze(x, y, z, w.b(["blue_ice", "packed_ice", "packed_ice", "ice", "snow_block"][
                    min(4, (y - y0) // 3 + (x + z) % 2)]))
    L.steine(5 + 2 * g, 1.2 * u, im_wasser=False, mat=["andesite", "stone", "diorite", "cobblestone"])
    return w


def canyonfluss(seed, g=2):
    """Canyonfluss: ein grüner Fluss windet sich tief unten durch eine Schlucht aus rot gebänderten Felsen,
    Felsbänder, überhängende Kanten und Sträucher."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 8)
    L = Land(w, R)
    H = _r(14 * u + 5)
    L.heben(lambda x, z, h: H)
    pts = [(round(math.sin(k * 0.8) * R * 0.25), -R + k * 2 * R // 8) for k in range(9)]
    L.fluss(pts, lambda t: 3.5 * u + 1, 0, tiefe=2, ufer=0)
    for (x, z) in list(L.h):
        d = min(math.hypot(x - a, z - b) for a, b in pts)
        if (x, z) not in L.wasser:
            br = 3.5 * u + 1
            if d < br + H * 0.6:
                L.h[(x, z)] = min(H, int((d - br) * 1.3 + 1))
    L.bauen(fels=["red_terracotta", "orange_terracotta", "terracotta", "red_sandstone", "brown_terracotta",
                  "yellow_terracotta"], gras="red_sand")
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if "terracotta" in n or n.endswith("red_sandstone"):
            w.bloecke[(x, y, z)] = w.b(["red_terracotta", "orange_terracotta", "terracotta", "brown_terracotta",
                                        "white_terracotta", "yellow_terracotta"][(y // 2) % 6])
    L.bepflanzen(0.2, baeume=3, arten=("busch",), blumen=False)
    for (x, z), h in L.h.items():
        if h >= H - 1 and w.rng.random() < 0.05:
            w.setze(x, h + 1, z, w.b("dead_bush"))
    return w


def hoehlenfluss(seed, g=2):
    """Höhlenfluss: ein Fluss tritt aus einem großen Höhlenmaul in einer Felswand hervor, Tropfsteine am
    Eingang, ein Pfad aus Trittsteinen und Laternen."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 7)
    L = Land(w, R)
    H = _r(14 * u + 5)
    L.heben(lambda x, z, h: H + 2 * L.rn(x, 0, z) if z < -R * 0.1 else 1.2 * L.rn(x, 3, z))
    L.fluss([(0, -R), (0, R)], _r(2.5 * u + 1), 0, tiefe=2)
    L.bauen()
    hr = 5 * u + 2
    for x in range(-int(hr) - 1, int(hr) + 2):
        for y in range(0, int(hr * 1.2) + 2):
            for z in range(-R, -round(R * 0.1) + 1):
                if (x / hr) ** 2 + (y / (hr * 1.2)) ** 2 < 1:
                    p = (x, y, z)
                    if p in w.bloecke and not w.P.name(w.bloecke[p]).endswith("water"):
                        if y > 0:
                            del w.bloecke[p]
    for k in range(int(8 * u)):
        x = int(w.rng.integers(-int(hr), int(hr) + 1))
        ytop = int(hr * 1.2 * math.sqrt(max(0, 1 - (x / hr) ** 2)))
        z = -round(R * 0.1) - int(w.rng.integers(0, 4))
        for d in range(int(1 + w.rng.integers(3))):
            w.setze(x, ytop - d, z, w.b("pointed_dripstone", vertical_direction="down", thickness="tip",
                                        waterlogged=False), False)
    for z in range(0, R, 2):
        x = _r(2.5 * u + 1) + 2
        if (x, z) in L.h:
            w.setze(x, L.h[(x, z)], z, w.b("cobblestone"))
    for sx in (-1, 1):
        x = sx * (int(hr) + 2)
        z = -round(R * 0.1) + 2
        if (x, z) in L.h:
            w.setze(x, L.h[(x, z)] + 1, z, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                                waterlogged=False))
            w.setze(x, L.h[(x, z)] + 2, z, w.b("lantern", hanging=False, waterlogged=False))
    L.bepflanzen(0.4, baeume=2 + g, arten=("fichte", "birke"))
    return w


def gumpen(seed, g=1):
    """Gumpen: glasklare, tiefe Felsbecken in einem Bergbach, verbunden durch kleine Fälle über glatt
    geschliffenen Stein – zum Baden."""
    w = _neu(seed)
    u = U[g]
    R = _r(14 * u + 6)
    L = Land(w, R)
    L.heben(lambda x, z, h: max(0, -z / R + 0.3) * 6 * u + 1.5 * L.rn(x, 0, z))
    n = 3
    for k in range(n):
        cz = round(-R * 0.6 + k * R * 0.6)
        sp = int(max(0, -cz / R + 0.3) * 6 * u)
        L.see(round(math.sin(k) * 2), cz, R * 0.3, sp, tiefe=_r(3 * u + 1), rauh=0.15)
    L.bauen(gras="moss_block", fels=["smooth_stone", "stone", "andesite", "diorite", "polished_andesite"],
            bett=("smooth_stone", "gravel", "andesite", "sand"))
    L.bepflanzen(0.5, baeume=2 + g, arten=("fichte", "birke"))
    return w


def flussinsel(seed, g=2):
    """Flussinsel: eine bewaldete Insel teilt einen breiten Fluss, mit Kiesspitzen an beiden Enden, Treibholz
    und einer kleinen Anlegestelle."""
    w = _neu(seed)
    u = U[g]
    R = _r(18 * u + 8)
    L = Land(w, R)
    L.heben(lambda x, z, h: 1 + 1.5 * L.rn(x, 0, z))
    B = R * 0.6
    L.fluss([(-R - 2, 0), (R + 2, 0)], B, 0, tiefe=2, ufer=2)
    for (x, z) in list(L.h):
        d = ((x / (R * 0.55)) ** 2 + (z / (B * 0.5)) ** 2)
        if d < 1:
            L.h[(x, z)] = 1 + int((1 - d) * 2 * u)
            L.wasser.pop((x, z), None)
            if d > 0.75:
                L.boden[(x, z)] = "gravel"
    L.bauen()
    L.bepflanzen(0.5, baeume=4 + 2 * g, arten=("weide", "oak", "birke", "busch"))
    for x in range(round(R * 0.55), round(R * 0.55) + 4):
        for z in (-1, 0, 1):
            w.setze(x, 1, z, w.b("oak_slab", type="bottom", waterlogged=False))
    return w


def steinwehr(seed, g=2):
    """Steinwehr: ein gemauertes Wehr staut den Fluss zu einem stillen Becken, das Wasser fällt in breiter Bahn
    über die Krone, daneben eine Fischtreppe und ein Wärterhäuschen."""
    import pracht as P
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 7)
    L = Land(w, R)
    hw = _r(3 * u + 1)
    L.heben(lambda x, z, h: hw + 1 + 1.2 * L.rn(x, 0, z) if z < 0 else 1 + 1.2 * L.rn(x, 3, z))
    B = _r(4 * u + 2)
    L.fluss([(0, -R), (0, -1)], B, hw, tiefe=2)
    L.fluss([(0, 1), (0, R)], B, 0, tiefe=2)
    L.bauen()
    for x in range(-B - 2, B + 3):
        for y in range(-2, hw + 1):
            for z in (-1, 0):
                w.setze(x, y, z, w.b("stone_bricks" if (x + y) % 3 else "mossy_stone_bricks"))
        if abs(x) < B:
            for y in range(1, hw + 1):
                w.setze(x, y, 1, w.b("water", level=0 if y == hw else 8))
            w.setze(x, hw + 1, -1, w.b("water", level=0))
            w.setze(x, hw + 1, 0, w.b("water", level=0))
    for k in range(hw + 1):
        w.setze(B + 3, hw - k, -2 + k, w.b("water", level=0))
        w.setze(B + 4, hw - k + 1, -2 + k, w.b("stone_bricks"))
    st = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="mcw_schiefer", holz="spruce")
    P.gebaeude(w, st, B + 6, -4, B + 10, 0, y0=hw + 2, etagen=1, eh=3, dach="sattel", tuer="west", gauben=False,
               kamine=1)
    L.bepflanzen(0.4, baeume=2 + g, arten=("weide", "oak"))
    return w


# ============================================================================ Kachelbare Flussstücke

def _kachel(seed, g, form):
    w = _neu(seed)
    R = [12, 18, 28, 40][g]
    u = U[g]
    L = Land(w, R, form="quadrat")
    L.heben(lambda x, z, h: 1 + 1.5 * L.rn(x, 0, z) * (1 - 0.0))
    B = 2.5 * u + 1
    if form == "gerade":
        L.fluss([(-R - 1, 0), (R + 1, 0)], B, 0, tiefe=2)
    elif form == "kurve":
        pts = [(round(-R - 1), 0)] + [(round(-R + R * math.sin(a)), round(R - R * math.cos(a)))
                                      for a in np.linspace(0.15, math.pi / 2 - 0.15, 6)] + [(0, R + 1)]
        L.fluss(pts, B, 0, tiefe=2)
    else:
        L.fluss([(-R - 1, 0), (R + 1, 0)], B, 0, tiefe=2)
        L.fluss([(0, 0), (0, R + 1)], B * 0.8, 0, tiefe=2)
    for (x, z) in list(L.h):
        if abs(x) == R or abs(z) == R:
            L.h[(x, z)] = min(L.h[(x, z)], 1) if (x, z) not in L.wasser else L.h[(x, z)]
    L.bauen()
    L.bepflanzen(0.45, baeume=2 + 2 * g, arten=("weide", "oak", "birke", "busch"))
    return w


def fluss_gerade(seed, g=1):
    """Flussstück gerade: ein Flusslauf quer über eine quadratische Kachel – mehrere Kacheln ergeben einen langen
    Fluss (Ein- und Auslauf exakt mittig)."""
    return _kachel(seed, g, "gerade")


def fluss_kurve(seed, g=1):
    """Flussstück Kurve: der Fluss kommt von Westen und biegt nach Süden ab – passt an die gerade Kachel."""
    return _kachel(seed, g, "kurve")


def fluss_gabelung(seed, g=1):
    """Flussstück Gabelung: ein Nebenfluss mündet von Süden in den Hauptfluss – passt an gerade und Kurve."""
    return _kachel(seed, g, "gabel")


GEWAESSER = {
    "klippenfall": ("Klippenwasserfall", klippenfall),
    "kaskaden": ("Kaskaden", kaskaden),
    "zwillingsfaelle": ("Zwillingsfälle", zwillingsfaelle),
    "schleierfall": ("Schleierfall mit Grotte", schleierfall),
    "regenbogenfall": ("Regenbogenfall", regenbogenfall),
    "schwebender_fall": ("Schwebender Wasserfall", schwebender_fall),
    "bergsee": ("Bergsee", bergsee),
    "kratersee": ("Kratersee", kratersee),
    "weiher_insel": ("Weiher mit Insel", weiher_insel),
    "bootshaus_see": ("Seeufer mit Bootshaus", bootshaus_see),
    "sinterterrassen": ("Sinterterrassen", sinterterrassen),
    "geysir": ("Geysir", geysir),
    "heisse_quelle": ("Heiße Quelle", heisse_quelle),
    "tropfsteinsee": ("Tropfsteinsee", tropfsteinsee),
    "flussbiegung": ("Flussbiegung", flussbiegung),
    "stromschnellen": ("Stromschnellen", stromschnellen),
    "flussdelta": ("Flussdelta", flussdelta),
    "bachquelle": ("Bachquelle", bachquelle),
    "gletscherbach": ("Gletscherbach", gletscherbach),
    "canyonfluss": ("Canyonfluss", canyonfluss),
    "hoehlenfluss": ("Höhlenfluss", hoehlenfluss),
    "gumpen": ("Gumpen", gumpen),
    "flussinsel": ("Flussinsel", flussinsel),
    "steinwehr": ("Steinwehr", steinwehr),
    "fluss_gerade": ("Flussstück gerade", fluss_gerade),
    "fluss_kurve": ("Flussstück Kurve", fluss_kurve),
    "fluss_gabelung": ("Flussstück Gabelung", fluss_gabelung),
}

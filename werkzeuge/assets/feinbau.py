"""Feinbau – Bausteine für sehr detaillierte Einzelbauten (Instagram-Stil): Fachwerk mit Relief, Fenster mit
Läden, Sohlbank und Blumenkasten, geschwungene Satteldächer mit Traufbalken und Firstzier, Glockenhelme,
Kamine mit Rauch, Balkone, Kragsteine, Diorama-Sockel mit Wegen, Büschen, Steinen und Blumen.

Konventionen: Treppe facing = Richtung, in die die Stufe ansteigt. Seiten: north (-z), south (+z), west (-x),
east (+x)."""

from __future__ import annotations

import math

import numpy as np

from lib import Rauschen

D = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}
GEGEN = {"north": "south", "south": "north", "east": "west", "west": "east"}


# ============================================================================ Materialmischung

class Mix:
    """Fleckige Mischung aus Blöcken (gewichtete Liste), z. B. Mix(w, [("stone_bricks", 3), ("cobblestone", 1)])."""

    def __init__(self, w, liste, zelle=1.8, **props):
        self.w = w
        self.ids = [w.b(n, **props) if not isinstance(n, int) else n for n, _ in liste]
        g = np.array([g for _, g in liste], float)
        self.kum = np.cumsum(g / g.sum())
        self.r = Rauschen(w, zelle)
        self.r2 = Rauschen(w, 0.7)

    def __call__(self, x, y, z, *_):
        v = self.r(x, y, z) * 0.7 + self.r2(x, y, z) * 0.3
        v = min(0.999, max(0.0, (v - 0.15) / 0.7))
        return self.ids[int(np.searchsorted(self.kum, v))]


def treppe(w, mat, facing, half="bottom"):
    return w.b(f"{mat}_stairs", facing=facing, half=half, shape="straight", waterlogged=False)


def platte(w, mat, typ="bottom"):
    return w.b(f"{mat}_slab", type=typ, waterlogged=False)


def zaun(w, holz, ax=None):
    return w.b(f"{holz}_fence", east=ax == "x", west=ax == "x", north=ax == "z", south=ax == "z", waterlogged=False)


def stamm(w, holz, ax="y", geschaelt=True):
    return w.b(f"stripped_{holz}_log" if geschaelt else f"{holz}_log", axis=ax)


def laterne(w, x, y, z, kette=1, seele=False):
    for k in range(kette):
        w.setze(x, y - k, z, w.b("chain", axis="y", waterlogged=False), False)
    w.setze(x, y - kette, z, w.b("soul_lantern" if seele else "lantern", hanging=True, waterlogged=False), False)


VOLL = {"stone_brick": "stone_bricks", "brick": "bricks", "mud_brick": "mud_bricks", "deepslate_tile": "deepslate_tiles",
        "deepslate_brick": "deepslate_bricks", "polished_blackstone_brick": "polished_blackstone_bricks",
        "prismarine_brick": "prismarine_bricks", "nether_brick": "nether_bricks", "red_nether_brick": "red_nether_bricks",
        "mossy_stone_brick": "mossy_stone_bricks", "quartz": "quartz_block", "purpur": "purpur_block",
        "end_stone_brick": "end_stone_bricks", "cobbled_deepslate": "cobbled_deepslate",
        "waxed_oxidized_cut_copper": "waxed_oxidized_cut_copper", "waxed_weathered_cut_copper":
            "waxed_weathered_cut_copper", "waxed_exposed_cut_copper": "waxed_exposed_cut_copper",
        "waxed_cut_copper": "waxed_cut_copper"}
HOLZ = ("oak", "spruce", "dark_oak", "birch", "jungle", "acacia", "mangrove", "cherry", "crimson", "warped",
        "bamboo")


def voll(mat):
    if mat in VOLL:
        return VOLL[mat]
    if mat in HOLZ:
        return f"{mat}_planks"
    return mat


class Dachmat:
    """Dachmaterial: mehrere Treppensorten fleckig gemischt, zum Rand hin dunkler (letztes Material)."""

    def __init__(self, w, mats, rand=None, zelle=2.2):
        self.w, self.mats, self.rand = w, list(mats), rand
        self.r = Rauschen(w, zelle)
        self.r2 = Rauschen(w, 0.8)

    def mat(self, x, y, z, randnah=False):
        if randnah and self.rand:
            return self.rand
        v = self.r(x, y, z) * 0.75 + self.r2(x, y, z) * 0.25
        v = min(0.999, max(0.0, (v - 0.15) / 0.7))
        return self.mats[int(v * len(self.mats))]

    def treppe(self, x, y, z, facing, half="bottom", randnah=False):
        m = self.mat(x, y, z, randnah)
        if ":" in m:
            import modbloecke as MB
            return MB.dach_treppe(self.w, m, facing, half)
        return treppe(self.w, m, facing, half)

    def voll(self, x, y, z):
        m = self.mat(x, y, z)
        if ":" in m:
            import modbloecke as MB
            return MB.dach_voll(self.w, m)
        return self.w.b(voll(m))

    def platte(self, x, y, z, typ="bottom"):
        m = self.mat(x, y, z)
        if ":" in m:
            import modbloecke as MB
            return MB.dach_platte(self.w, m, typ)
        return platte(self.w, m, typ)


# ============================================================================ Wände

def sockel(w, x0, z0, x1, z1, y0, h, M, kante="stone_brick"):
    """Steinsockel, eine Zelle breiter als das Haus, oben mit Treppenkante."""
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            for y in range(y0, y0 + h):
                w.setze(x, y, z, M(x, y, z))
            rand = x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1)
            if rand:
                if x in (x0 - 1, x1 + 1) and z in (z0 - 1, z1 + 1):
                    w.setze(x, y0 + h, z, platte(w, kante))
                else:
                    s = "north" if z == z0 - 1 else "south" if z == z1 + 1 else "west" if x == x0 - 1 else "east"
                    w.setze(x, y0 + h, z, treppe(w, kante, GEGEN[s]))


def fachwerk(w, x0, z0, x1, z1, y0, y1, fuell, holz="spruce", abstand=3, diagonal=True, relief=True,
             boden=True):
    """Fachwerkgeschoss: Ständer, Rähm und Schwelle aus Holz, Gefache aus 'fuell', optional Streben (Andreaskreuz-
    artig aus Treppen), Ständer an den Ecken eine Zelle vorgesetzt (Relief)."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            rx, rz = x in (x0, x1), z in (z0, z1)
            if not (rx or rz):
                if boden:
                    w.setze(x, y0, z, w.b(f"{holz}_planks"))
                continue
            for y in range(y0, y1 + 1):
                ecke = rx and rz
                t = (x - x0) if rz else (z - z0)
                staender = ecke or t % abstand == 0
                if y in (y0, y1):
                    w.setze(x, y, z, stamm(w, holz, "x" if rz and not ecke else "z" if not ecke else "y"))
                elif staender:
                    w.setze(x, y, z, stamm(w, holz, "y"))
                else:
                    w.setze(x, y, z, fuell(x, y, z) if callable(fuell) else fuell)
    if relief:
        for (x, z) in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
            for y in range(y0, y1 + 1):
                for dx, dz in (((-1 if x == x0 else 1), 0), (0, (-1 if z == z0 else 1))):
                    pass
        # Rähm als vorspringender Balken
        for x in range(x0 - 1, x1 + 2):
            for z in (z0 - 1, z1 + 1):
                if x0 <= x <= x1:
                    s = "north" if z == z0 - 1 else "south"
                    w.setze(x, y1, z, treppe(w, holz, GEGEN[s], "top"), False)
        for z in range(z0, z1 + 1):
            for x in (x0 - 1, x1 + 1):
                s = "west" if x == x0 - 1 else "east"
                w.setze(x, y1, z, treppe(w, holz, GEGEN[s], "top"), False)
    if diagonal:
        h = y1 - y0 - 1
        if h >= 2:
            for (xs, zs, rz) in ((range(x0, x1 + 1), (z0, z1), True), ((x0, x1), range(z0, z1 + 1), False)):
                rng = w.rng
                if rz:
                    for z in zs:
                        for x in range(x0 + 1, x1, abstand):
                            if rng.random() < 0.5 and x + 1 < x1 and (x + 1 - x0) % abstand:
                                s = "south" if z == z1 else "north"
                                w.setze(x + 1, y0 + 1, z, treppe(w, holz, "east", "bottom") if (x // abstand) % 2
                                        else treppe(w, holz, "west", "bottom"))
                else:
                    for x in xs:
                        for z in range(z0 + 1, z1, abstand):
                            if rng.random() < 0.5 and z + 1 < z1 and (z + 1 - z0) % abstand:
                                w.setze(x, y0 + 1, z + 1, treppe(w, holz, "south", "bottom") if (z // abstand) % 2
                                        else treppe(w, holz, "north", "bottom"))


def mauer(w, x0, z0, x1, z1, y0, y1, M, ecke=None, gurt=None):
    """Massive Wand (Ring), Ecken optional aus anderem Material, optional Gurtgesims (Höhe)."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            rx, rz = x in (x0, x1), z in (z0, z1)
            if not (rx or rz):
                continue
            for y in range(y0, y1 + 1):
                if ecke and rx and rz:
                    w.setze(x, y, z, ecke(x, y, z) if callable(ecke) else ecke)
                else:
                    w.setze(x, y, z, M(x, y, z))
    if gurt:
        for x in range(x0 - 1, x1 + 2):
            for z in range(z0 - 1, z1 + 2):
                if (x in (x0 - 1, x1 + 1)) != (z in (z0 - 1, z1 + 1)):
                    s = "north" if z == z0 - 1 else "south" if z == z1 + 1 else "west" if x == x0 - 1 else "east"
                    w.setze(x, gurt, z, treppe(w, "stone_brick", GEGEN[s], "top"), False)


def boden(w, x0, z0, x1, z1, y, holz="spruce"):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, y, z, w.b(f"{holz}_planks"))


def fenster(w, x, y, z, seite, holz="spruce", hoehe=2, breite=1, laeden=True, blumen=0.5, glas="glass_pane",
            licht=False, bogen=False):
    """Fenster in einer Wand: Scheiben, Sohlbank, Sturz, Läden und Blumenkasten (außen)."""
    dx, dz = D[seite]
    sx, sz = (1, 0) if seite in ("north", "south") else (0, 1)
    rz = seite in ("north", "south")
    for b in range(breite):
        for k in range(hoehe):
            px, pz = x + sx * b, z + sz * b
            if glas.endswith("pane"):
                w.setze(px, y + k, pz, w.b(glas, east=rz, west=rz, north=not rz, south=not rz, waterlogged=False))
            else:
                w.setze(px, y + k, pz, w.b(glas))
        px, pz = x + sx * b, z + sz * b
        w.setze(px + dx, y - 1, pz + dz, treppe(w, holz, GEGEN[seite], "top"), False)
        w.setze(px + dx, y + hoehe, pz + dz, platte(w, holz, "bottom") if not bogen else treppe(w, holz, GEGEN[seite]),
                False)
        if blumen and w.rng.random() < blumen:
            w.setze(px + dx, y, pz + dz, w.b(["potted_red_tulip", "potted_azure_bluet", "potted_poppy",
                                               "potted_allium", "potted_cornflower"][int(w.rng.random() * 5)]), False)
    if laeden:
        for s, b in ((-1, -1), (1, breite)):
            for k in range(hoehe):
                w.setze(x + sx * b + dx, y + k, z + sz * b + dz,
                        w.b(f"{holz}_trapdoor", facing=seite, half="bottom", open=True, powered=False,
                            waterlogged=False), False)
    if licht:
        w.setze(x - dx, y + hoehe, z - dz, w.b("lantern", hanging=True, waterlogged=False), False)


def fensterreihe(w, x0, z0, x1, z1, y, seiten, abstand=3, **kw):
    for seite in seiten:
        if seite in ("north", "south"):
            z = z0 if seite == "north" else z1
            for x in range(x0 + 2, x1 - 1, abstand):
                fenster(w, x, y, z, seite, **kw)
        else:
            x = x0 if seite == "west" else x1
            for z in range(z0 + 2, z1 - 1, abstand):
                fenster(w, x, y, z, seite, **kw)


def tuer(w, x, y, z, seite, holz="spruce", vordach=True, laternen=True, stufen=0, mat_stufe="stone_brick"):
    for k, half in ((0, "lower"), (1, "upper")):
        w.setze(x, y + k, z, w.b(f"{holz}_door", facing=seite, half=half, hinge="left", open=False, powered=False))
    dx, dz = D[seite]
    sx, sz = (1, 0) if seite in ("north", "south") else (0, 1)
    if vordach:
        for s in (-1, 0, 1):
            w.setze(x + dx + s * sx, y + 2, z + dz + s * sz, treppe(w, holz, GEGEN[seite]), False)
            w.setze(x + 2 * dx + s * sx, y + 2, z + 2 * dz + s * sz, platte(w, holz, "top") if s == 0 else
                    treppe(w, holz, GEGEN[seite], "top"), False)
    if laternen:
        for s in (-1, 1):
            w.setze(x + dx + s * sx, y + 1, z + dz + s * sz, w.b("lantern", hanging=False, waterlogged=False), False) \
                if False else w.setze(x + dx + 2 * s * sx, y + 2, z + dz + 2 * s * sz,
                                      w.b("lantern", hanging=False, waterlogged=False), False)
    for k in range(stufen):
        for s in (-1, 0, 1):
            w.setze(x + dx * (k + 1) + s * sx, y - 1 - k, z + dz * (k + 1) + s * sz,
                    treppe(w, mat_stufe, GEGEN[seite]))


def kragsteine(w, x0, z0, x1, z1, y, holz="spruce", abstand=2):
    """Konsolen unter einem auskragenden Geschoss (umgedrehte Treppen)."""
    for x in range(x0, x1 + 1, abstand):
        w.setze(x, y, z0 - 1, treppe(w, holz, "south", "top"), False)
        w.setze(x, y, z1 + 1, treppe(w, holz, "north", "top"), False)
    for z in range(z0, z1 + 1, abstand):
        w.setze(x0 - 1, y, z, treppe(w, holz, "east", "top"), False)
        w.setze(x1 + 1, y, z, treppe(w, holz, "west", "top"), False)


# ============================================================================ Dächer

def satteldach(w, x0, z0, x1, z1, y, dm, first_x=True, ue=1, ue_giebel=1, giebel=None, traufe="spruce",
               knick=True, steil=1, firstzier=True, giebelfenster=True):
    """Satteldach mit Überstand, geschwungener Traufe (Knick), Traufbalken, gefüllten Giebeln, Ortgang-Brettern,
    Firstabdeckung und Giebelzier. Gibt die Firsthöhe zurück."""
    if first_x:
        a0, a1, b0, b1 = z0, z1, x0, x1
    else:
        a0, a1, b0, b1 = x0, x1, z0, z1

    def setze(a, yy, b, blk, ueber=True):
        if first_x:
            w.setze(b, yy, a, blk, ueber)
        else:
            w.setze(a, yy, b, blk, ueber)

    hin, her = ("south", "north") if first_x else ("east", "west")
    breite = a1 - a0 + 2 * ue
    stufen = (breite + 1) // 2
    ytop = y
    for k in range(stufen):
        lo, hi = a0 - ue + k, a1 + ue - k
        yy = y + k * steil
        for s in range(steil):
            for b in range(b0 - ue_giebel, b1 + ue_giebel + 1):
                rand = b in (b0 - ue_giebel, b1 + ue_giebel)
                if lo == hi:
                    setze(lo, yy + s, b, dm.platte(b, yy, lo) if s == steil - 1 else dm.voll(b, yy, lo))
                    continue
                if s == steil - 1:
                    setze(lo, yy + s, b, dm.treppe(b, yy, lo, hin, randnah=rand))
                    setze(hi, yy + s, b, dm.treppe(b, yy, hi, her, randnah=rand))
                else:
                    setze(lo, yy + s, b, dm.voll(b, yy, lo))
                    setze(hi, yy + s, b, dm.voll(b, yy, hi))
                if k > 0 and s == 0:
                    setze(lo, yy - 1, b, dm.voll(b, yy, lo), False)
                    setze(hi, yy - 1, b, dm.voll(b, yy, hi), False)
        # Giebelwand
        if giebel is not None and lo + 1 <= hi - 1 and k > 0:
            for a in range(max(lo + 1, a0), min(hi - 1, a1) + 1):
                for s in range(steil):
                    for b in (b0, b1):
                        setze(a, yy + s - 1, b, giebel(a, yy, b) if callable(giebel) else giebel)
        ytop = yy + steil
    # Traufe: Knick (Platten nach außen) und Traufbalken
    for b in range(b0 - ue_giebel, b1 + ue_giebel + 1):
        if knick:
            setze(a0 - ue - 1, y - 1, b, dm.platte(b, y, a0, "top"), False)
            setze(a1 + ue + 1, y - 1, b, dm.platte(b, y, a1, "top"), False)
        setze(a0 - ue, y - 1, b, treppe(w, traufe, hin, "top"), False)
        setze(a1 + ue, y - 1, b, treppe(w, traufe, her, "top"), False)
    # Ortgang (Giebelbretter unter dem Dachrand)
    for k in range(stufen):
        lo, hi = a0 - ue + k, a1 + ue - k
        yy = y + k * steil
        for b, f in ((b0 - ue_giebel, "east" if first_x else "south"), (b1 + ue_giebel, "west" if first_x else "north")):
            for a in (lo, hi):
                setze(a, yy - 1, b, treppe(w, traufe, f, "top"), False)
    # Giebelfenster
    if giebelfenster and giebel is not None:
        am = (a0 + a1) // 2
        hy = y + max(1, (stufen - 2) * steil // 2)
        for b in (b0, b1):
            setze(am, hy, b, w.b("glass_pane", north=first_x, south=first_x, east=not first_x, west=not first_x,
                                 waterlogged=False))
            if (a1 - a0) % 2 == 1:
                setze(am + 1, hy, b, w.b("glass_pane", north=first_x, south=first_x, east=not first_x,
                                         west=not first_x, waterlogged=False))
    # Firstzier
    if firstzier:
        am = (a0 + a1) / 2
        for b in (b0 - ue_giebel, b1 + ue_giebel):
            setze(round(am - 0.01), ytop, b, w.b(f"{traufe}_fence", north=False, south=False, east=False, west=False,
                                                 waterlogged=False), False)
            if (a1 - a0) % 2 == 1:
                setze(round(am + 0.49), ytop, b, w.b(f"{traufe}_fence", north=False, south=False, east=False,
                                                     west=False, waterlogged=False), False)
    return ytop


def kegeldach(w, cx, cz, y, r, dm, h=None, form="glocke", eckig=False, spitze="lightning_rod", ue=1.2):
    """Turmhelm: Glocke (unten ausschwingend), Kegel oder Nadel; rund oder achteckig. Gibt die Spitze zurück."""
    R0 = r + ue
    h = h or int(R0 * (3.2 if form == "nadel" else 2.4))
    for k in range(h + 1):
        t = k / h
        if form == "glocke":
            rr = R0 * (1 - t) ** 1.25 + (0.5 if t < 0.12 else 0) * (1 - t / 0.12)
        elif form == "nadel":
            rr = R0 * (1 - t) ** 1.1
        else:
            rr = R0 * (1 - t)
        n = int(rr) + 2
        for x in range(cx - n, cx + n + 1):
            for z in range(cz - n, cz + n + 1):
                dx, dz = x - cx, z - cz
                d = max(abs(dx), abs(dz), (abs(dx) + abs(dz)) / 1.42) if eckig else math.hypot(dx, dz)
                if rr - 1.15 < d <= rr + 0.35 or (k == 0 and d <= rr):
                    w.setze(x, y + k, z, dm.voll(x, y + k, z))
    top = y + h + 1
    if spitze:
        w.setze(cx, top, cz, w.b(spitze, facing="up", powered=False, waterlogged=False) if spitze == "lightning_rod"
                else w.b(spitze))
    return top


def kamin(w, x, z, y0, y1, M, rauch=True):
    for y in range(y0, y1 + 1):
        for dx in (0, 1):
            for dz in (0, 1):
                w.setze(x + dx, y, z + dz, M(x + dx, y, z + dz))
    for dx in (-1, 0, 1, 2):
        for dz in (-1, 0, 1, 2):
            if dx in (-1, 2) or dz in (-1, 2):
                w.setze(x + dx, y1 + 1, z + dz, platte(w, "stone_brick"), False)
    for dx in (0, 1):
        for dz in (0, 1):
            w.setze(x + dx, y1 + 1, z + dz, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                                 waterlogged=False) if rauch and dx == dz == 0 else
                    w.b("stone_brick_wall", up=True, north="none", south="none", east="none", west="none",
                        waterlogged=False))


def gaube(w, x, y, z, seite, dm, holz="spruce", fuell=None):
    """Dachgaube (3 breit) mit Fenster und kleinem Satteldach, Front zur Seite 'seite'."""
    dx, dz = D[seite]
    sx, sz = (1, 0) if seite in ("north", "south") else (0, 1)
    for s in (-1, 0, 1):
        for k in range(2):
            px, pz = x + s * sx, z + s * sz
            if s == 0:
                w.setze(px, y + k, pz, w.b("glass_pane", east=sx == 1, west=sx == 1, north=sz == 1, south=sz == 1,
                                           waterlogged=False))
            else:
                w.setze(px, y + k, pz, stamm(w, holz))
        for t in range(0, 3):
            w.setze(x + s * sx - dx * t, y - 1, z + s * sz - dz * t, w.b(f"{holz}_planks"), False)
    for t in range(-1, 3):
        px, pz = x - dx * t, z - dz * t
        w.setze(px - sx, y + 2, pz - sz, treppe(w, dm.mat(px, y, pz), "east" if sx else "south"))
        w.setze(px + sx, y + 2, pz + sz, treppe(w, dm.mat(px, y, pz), "west" if sx else "north"))
        w.setze(px, y + 3, pz, dm.platte(px, y, pz))
        if t >= 0:
            w.setze(px, y + 2, pz, w.b(f"{holz}_planks"))


# ============================================================================ Anbauten

def balkon(w, x0, x1, z, y, seite, holz="spruce", tiefe=2, dach=False):
    """Balkon entlang x vor der Seite north/south (oder entlang z wenn seite east/west: x0/x1 sind dann z)."""
    dx, dz = D[seite]
    for t in range(1, tiefe + 1):
        for a in range(x0, x1 + 1):
            px, pz = (a, z + dz * t) if dz else (z + dx * t, a)
            w.setze(px, y, pz, w.b(f"{holz}_planks") if t < tiefe else platte(w, holz, "top"))
            if t == tiefe or a in (x0, x1):
                w.setze(px, y + 1, pz, w.b(f"{holz}_fence", north=False, south=False, east=False, west=False,
                                           waterlogged=False))
        for a in (x0, x1):
            px, pz = (a, z + dz * t) if dz else (z + dx * t, a)
            w.setze(px, y - 1, pz, treppe(w, holz, GEGEN[seite], "top"), False)


def busch(w, x, y, z, r=1.4, art="oak", blueten=None):
    rng = w.rng
    for dx in range(-int(r) - 1, int(r) + 2):
        for dy in range(0, int(r) + 1):
            for dz in range(-int(r) - 1, int(r) + 2):
                if dx * dx + (dy * 1.3) ** 2 + dz * dz <= r * r + rng.random() * 0.6:
                    blk = w.b(f"{art}_leaves", persistent=True, distance=1, waterlogged=False)
                    if blueten and rng.random() < 0.25:
                        blk = w.b(blueten, persistent=True, distance=1, waterlogged=False) \
                            if blueten.endswith("leaves") else w.b(blueten)
                    w.setze(x + dx, y + dy, z + dz, blk, False)


def stein(w, x, y, z, r=1.2, mats=("stone", "andesite", "cobblestone", "mossy_cobblestone")):
    rng = w.rng
    for dx in range(-int(r) - 1, int(r) + 2):
        for dy in range(0, int(r) + 1):
            for dz in range(-int(r) - 1, int(r) + 2):
                if dx * dx + (dy * 1.4) ** 2 + dz * dz <= r * r + rng.random() * 0.5:
                    w.setze(x + dx, y + dy, z + dz, w.b(mats[int(rng.random() * len(mats))]))


def kram(w, x, y, z, n=3):
    """Häufchen aus Fässern, Kisten, Heuballen, Kürbissen."""
    rng = w.rng
    for k in range(n):
        dx, dz = int(rng.integers(-1, 2)), int(rng.integers(-1, 2))
        art = int(rng.random() * 5)
        blk = [w.b("barrel", facing="up", open=False), w.b("composter", level=0),
               w.b("hay_block", axis="y"), w.b("pumpkin"), w.b("chest", facing="south", type="single",
                                                                waterlogged=False)][art]
        yy = y
        while (x + dx, yy, z + dz) in w.bloecke and yy < y + 2:
            yy += 1
        w.setze(x + dx, yy, z + dz, blk, False)


def efeu(w, anteil=0.06, laub=0.4, bis=None):
    from veredeln import bewuchs
    bewuchs(w, moos=0.02, ranken=anteil, nur_unter=bis)
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) == "minecraft:vine" and w.rng.random() < laub * 0.3:
            w.bloecke[(x, y, z)] = w.b("oak_leaves" if w.rng.random() < 0.7 else "azalea_leaves", persistent=True,
                                       distance=1, waterlogged=False)


# ============================================================================ Sockel / Diorama

def diorama(w, R, tiefe=4, art="wiese", rund=True, rand_zacken=0.18, frei=None):
    """Erdsockel wie ein Diorama: unregelmäßiger Umriss, oben Gras, darunter Erde, Grobboden und Stein.
    Gibt die Menge der Oberflächenzellen zurück. frei: Funktion (x, z) -> True für Zellen ohne Boden (Wasser)."""
    rn = Rauschen(w, 4)
    zellen = set()
    oben_mix = {"wiese": [("grass_block", 8), ("moss_block", 1), ("grass_block", 3)],
                "wald": [("podzol", 3), ("grass_block", 4), ("moss_block", 2), ("coarse_dirt", 1)],
                "sand": [("sand", 6), ("sandstone", 1), ("sand", 3)],
                "herbst": [("grass_block", 5), ("podzol", 3), ("coarse_dirt", 1), ("rooted_dirt", 1)],
                "schnee": [("snow_block", 8), ("powder_snow", 1)]}[art]
    M = Mix(w, oben_mix, zelle=2.5)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            d = math.hypot(x, z) / R if rund else max(abs(x), abs(z)) / R
            if d > 1 - rand_zacken + rand_zacken * 2 * rn(x, 0, z):
                continue
            zellen.add((x, z))
            if frei and frei(x, z):
                continue
            t = int(tiefe * (0.6 + 0.6 * rn(x, 5, z)))
            for y in range(-t, 1):
                if y == 0:
                    b = M(x, 0, z)
                    w.setze(x, y, z, w.b(w.P.name(b).split(":")[1], snowy=False) if "grass" in w.P.name(b) or
                            "podzol" in w.P.name(b) else b)
                elif y > -2:
                    w.setze(x, y, z, w.b("dirt" if rn(x, y, z) < 0.7 else "coarse_dirt"))
                else:
                    w.setze(x, y, z, w.b(["dirt", "stone", "andesite", "gravel", "tuff"][int(rn(x, y * 3, z) * 4.99)]))
    return zellen


def bepflanzen(w, zellen, dichte=0.35, blumen=("poppy", "dandelion", "oxeye_daisy", "azure_bluet", "cornflower",
                                                "allium"), farn=True):
    rng = w.rng
    for (x, z) in zellen:
        if (x, 0, z) not in w.bloecke or (x, 1, z) in w.bloecke:
            continue
        n = w.P.name(w.bloecke[(x, 0, z)])
        if not any(k in n for k in ("grass_block", "moss_block", "podzol")):
            continue
        r = rng.random()
        if r < dichte * 0.55:
            w.setze(x, 1, z, w.b("grass"))
        elif r < dichte * 0.68 and farn:
            w.setze(x, 1, z, w.b("fern"))
        elif r < dichte * 0.8:
            w.setze(x, 1, z, w.b(blumen[int(rng.random() * len(blumen))]))
        elif r < dichte * 0.83:
            w.setze(x, 1, z, w.b("tall_grass", half="lower"))
            w.setze(x, 2, z, w.b("tall_grass", half="upper"))


def weg(w, punkte, breite=1.2, mats=(("coarse_dirt", 3), ("dirt_path", 4), ("gravel", 2), ("cobblestone", 1))):
    M = Mix(w, list(mats), zelle=1.2)
    for (a, b) in zip(punkte, punkte[1:]):
        n = int(math.dist(a, b) * 2) + 1
        for i in range(n + 1):
            t = i / n
            cx, cz = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            for dx in range(-int(breite) - 1, int(breite) + 2):
                for dz in range(-int(breite) - 1, int(breite) + 2):
                    if dx * dx + dz * dz <= breite * breite + w.rng.random() * 0.8:
                        x, z = round(cx + dx), round(cz + dz)
                        if (x, 0, z) in w.bloecke:
                            w.bloecke.pop((x, 1, z), None)
                            w.setze(x, 0, z, M(x, 0, z))


def treppe_gerade(w, x, y, z, richtung, n, breite=3, mat="stone_brick"):
    """Außentreppe: n Stufen in 'richtung' absteigend vom Punkt (x, y, z), breit 'breite'."""
    dx, dz = D[richtung]
    sx, sz = (1, 0) if richtung in ("north", "south") else (0, 1)
    for k in range(n):
        for s in range(-(breite // 2), breite - breite // 2):
            px, pz = x + dx * k + s * sx, z + dz * k + s * sz
            w.setze(px, y - k, pz, treppe(w, mat, GEGEN[richtung]))
            for yy in range(min(0, y - k - 4), y - k):
                if (px, yy, pz) not in w.bloecke and yy >= 0:
                    w.setze(px, yy, pz, w.b(voll(mat)))

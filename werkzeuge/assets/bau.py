"""Baukasten für Gebäude: Fundament, Wände mit Fachwerk und Fenstern, Satteldach, Walmdach, Treppengiebel,
runde und eckige Türme mit Kegel-/Pyramidendach, Kamine, Erker, Zäune. Wird von mehreren Paketen genutzt."""

from __future__ import annotations

import math

from lib import Verlauf
from skulptur import kreisrand, platte, scheibe, verbinde, zur_mitte


def _r(v, mind=1):
    return max(mind, int(round(v)))


class Stil:
    """Materialsatz eines Gebäudes.
    wand: Verlauf oder Blockname · holz: Holzart (oak, spruce, dark_oak …) für Balken, Türen, Böden
    dach: Name für Treppen/Stufen (z. B. 'dark_oak', 'deepslate_tile', 'brick') · dach_voll: voller Block
    sockel: Fundamentblock · glas: Fensterscheibe"""

    def __init__(self, w, wand, holz="spruce", dach="dark_oak", dach_voll=None, sockel="cobblestone",
                 glas="glass_pane", fachwerk=True, balken=None, akzent=None):
        self.w = w
        self.wand = wand if isinstance(wand, Verlauf) else Verlauf(w, wand, [wand])
        self.holz = holz
        self.dach = dach
        self.dach_voll = dach_voll or (f"{dach}_planks" if dach in ("oak", "spruce", "dark_oak", "birch", "acacia",
                                                                     "jungle", "mangrove", "cherry", "crimson",
                                                                     "warped") else dach)
        self.sockel = sockel
        self.glas = glas
        self.fachwerk = fachwerk
        self.balken = balken or (f"stripped_{holz}_log" if holz not in ("crimson", "warped") else f"stripped_{holz}_stem")
        self.akzent = akzent

    def treppe(self, facing, half="bottom"):
        if self.dach is None:
            return self.w.b(self.dach_voll)
        return self.w.b(f"{self.dach}_stairs", facing=facing, half=half, shape="straight", waterlogged=False)

    def wandblock(self, x, y, z, v=1.0):
        return self.wand(v + self.w.rng.random() * 1.2, x, y, z)


def _scheibe_blk(w, glas, ns):
    """Glasscheibe, die in der Wandebene verbunden ist (ns=True: Wand liegt in z-Richtung → Ost/West verbunden)."""
    if glas.endswith("_pane"):
        return w.b(glas, east=ns, west=ns, north=not ns, south=not ns, waterlogged=False)
    return w.b(glas)


def kasten_haus(w, st, x0, z0, x1, z1, y0, etagen, eh=4, fenster_abstand=3, tuer_seite="south", jetty=False,
                blumen=True, laternen=True):
    """Wände mehrerer Etagen mit Eckbalken, Geschossbalken, Fachwerk-Streben, Fenstern mit Blumenkästen
    und Tür. Gibt (yt, x0, z0, x1, z1) der obersten Etage zurück."""
    w.rng  # noqa
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            w.setze(x, y0, z, w.b(st.sockel))
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            w.setze(x, y0, z, w.b(f"{st.holz}_planks"))
    y = y0 + 1
    for e in range(etagen):
        if jetty and e > 0:
            x0, z0, x1, z1 = x0 - 1, z0 - 1, x1 + 1, z1 + 1
            for x in range(x0, x1 + 1):
                for z in range(z0, z1 + 1):
                    if x in (x0, x1) or z in (z0, z1):
                        w.setze(x, y - 1, z, w.b(st.balken, axis="x" if z in (z0, z1) else "z"))
                    else:
                        w.setze(x, y - 1, z, w.b(f"{st.holz}_planks"))
        for yy in range(y, y + eh):
            stufe = yy - y
            for x in range(x0, x1 + 1):
                for z in range(z0, z1 + 1):
                    rx, rz = x in (x0, x1), z in (z0, z1)
                    if not (rx or rz):
                        if stufe == eh - 1:
                            w.setze(x, yy, z, w.b(f"{st.holz}_planks"))
                        continue
                    if rx and rz:
                        blk = w.b(st.balken, axis="y")
                    elif stufe == eh - 1 and st.fachwerk:
                        blk = w.b(st.balken, axis="x" if rz else "z")
                    else:
                        t = (x - x0) if rz else (z - z0)
                        lang = (x1 - x0) if rz else (z1 - z0)
                        fenster = (stufe in (1, 2) if eh >= 4 else stufe == 1) and 1 < t < lang - 1 \
                            and t % fenster_abstand == fenster_abstand // 2 + 0
                        if fenster:
                            blk = _scheibe_blk(w, st.glas, rz)
                        elif st.fachwerk and (t % fenster_abstand == 0) and eh >= 3:
                            blk = w.b(st.balken, axis="y")
                        elif st.fachwerk and eh >= 4 and stufe == 0 and (t % fenster_abstand) in (1, 2) \
                                and (t // fenster_abstand) % 2 == 0:
                            blk = w.b(st.balken, axis="x" if rz else "z")
                        else:
                            blk = st.wandblock(x, yy, z, 1 + 2 * e / max(1, etagen))
                    w.setze(x, yy, z, blk)
        # Blumenkästen unter Fenstern
        if blumen:
            for x in range(x0, x1 + 1):
                for z in range(z0, z1 + 1):
                    rx, rz = x in (x0, x1), z in (z0, z1)
                    if rx == rz:
                        continue
                    t = (x - x0) if rz else (z - z0)
                    lang = (x1 - x0) if rz else (z1 - z0)
                    if 1 < t < lang - 1 and t % fenster_abstand == fenster_abstand // 2 and w.rng.random() < 0.7:
                        dx = (-1 if x == x0 else 1) if rx else 0
                        dz = (-1 if z == z0 else 1) if rz else 0
                        w.setze(x + dx, y + 1 - (0 if eh < 4 else 0), z + dz,
                                w.b("flowering_azalea_leaves", persistent=True, distance=7, waterlogged=False),
                                ueberschreiben=False)
        y += eh
    # Tür
    mx, mz = (x0 + x1) // 2, (z0 + z1) // 2
    tx, tz, fac = {"south": (mx, z1, "south"), "north": (mx, z0, "north"), "east": (x1, mz, "east"),
                   "west": (x0, mz, "west")}[tuer_seite]
    for yy, half in ((y0 + 1, "lower"), (y0 + 2, "upper")):
        w.setze(tx, yy, tz, w.b(f"{st.holz}_door", facing=fac, half=half, hinge="left", open=False, powered=False))
    if laternen:
        ox, oz = {"south": (1, 0), "north": (1, 0), "east": (0, 1), "west": (0, 1)}[tuer_seite]
        aus = {"south": (0, 1), "north": (0, -1), "east": (1, 0), "west": (-1, 0)}[tuer_seite]
        for s in (-1, 1):
            w.setze(tx + s * ox * 2 + aus[0], y0 + 1, tz + s * oz * 2 + aus[1],
                    w.b("lantern", hanging=False, waterlogged=False), ueberschreiben=False)
    return y - 1, x0, z0, x1, z1


def satteldach(w, st, x0, z0, x1, z1, yt, ue=1, first_x=None, giebelfenster=True):
    """Satteldach. first_x=True: First entlang x (Neigung nach Nord/Süd), sonst entlang z."""
    if first_x is None:
        first_x = (x1 - x0) >= (z1 - z0)
    k = 0
    while True:
        y = yt + 1 + k
        if first_x:
            a, b = z0 - ue + k, z1 + ue - k
            if a > b:
                break
            for x in range(x0 - ue, x1 + ue + 1):
                if a == b:
                    w.setze(x, y, a, w.b(st.dach_voll))
                else:
                    w.setze(x, y, a, st.treppe("south"))
                    w.setze(x, y, b, st.treppe("north"))
            for x in (x0, x1):
                for z in range(max(a + 1, z0), min(b, z1 + 1)):
                    mitte = (z0 + z1) // 2
                    w.setze(x, y, z, _scheibe_blk(w, st.glas, False) if giebelfenster and z == mitte and k == 1
                            else st.wandblock(x, y, z, 2.5))
        else:
            a, b = x0 - ue + k, x1 + ue - k
            if a > b:
                break
            for z in range(z0 - ue, z1 + ue + 1):
                if a == b:
                    w.setze(a, y, z, w.b(st.dach_voll))
                else:
                    w.setze(a, y, z, st.treppe("east"))
                    w.setze(b, y, z, st.treppe("west"))
            for z in (z0, z1):
                for x in range(max(a + 1, x0), min(b, x1 + 1)):
                    mitte = (x0 + x1) // 2
                    w.setze(x, y, z, _scheibe_blk(w, st.glas, True) if giebelfenster and x == mitte and k == 1
                            else st.wandblock(x, y, z, 2.5))
        k += 1
    return yt + k


def walmdach(w, st, x0, z0, x1, z1, yt, ue=1, steil=0):
    """Walmdach (alle vier Seiten geneigt). steil: so viele Lagen zuerst senkrecht (Mansarde)."""
    k = 0
    lage = 0
    while True:
        ax, bx = x0 - ue + k, x1 + ue - k
        az, bz = z0 - ue + k, z1 + ue - k
        if ax > bx or az > bz:
            break
        y = yt + 1 + lage
        for x in range(ax, bx + 1):
            for z in range(az, bz + 1):
                rand = x in (ax, bx) or z in (az, bz)
                if not rand:
                    continue
                if ax == bx or az == bz:
                    w.setze(x, y, z, w.b(st.dach_voll))
                elif lage < steil:
                    w.setze(x, y, z, w.b(st.dach_voll) if (x + z) % 4 else _scheibe_blk(w, st.glas, z in (az, bz)))
                elif z == az:
                    w.setze(x, y, z, st.treppe("south"))
                elif z == bz:
                    w.setze(x, y, z, st.treppe("north"))
                elif x == ax:
                    w.setze(x, y, z, st.treppe("east"))
                else:
                    w.setze(x, y, z, st.treppe("west"))
        if lage >= steil:
            k += 1
        lage += 1
    return yt + lage


def treppengiebel(w, st, x0, z, x1, yt, hoehe, mat):
    """Stufengiebel an einer Stirnseite (Wand in x-Richtung bei z)."""
    breite = x1 - x0
    stufen = max(2, breite // 2)
    for x in range(x0, x1 + 1):
        t = min(x - x0, x1 - x)
        h = min(hoehe, int((t + 1) / max(1, breite / 2) * hoehe) // 1)
        h = int(round((t // max(1, breite // stufen) + 1) * hoehe / (stufen // 2 + 1)))
        h = min(h, hoehe)
        for y in range(yt + 1, yt + 1 + h):
            w.setze(x, y, z, w.b(mat))
        w.setze(x, yt + 1 + h, z, platte(w, mat.replace("_bricks", "_brick") if mat.endswith("_bricks") else mat))


def kamin(w, x, z, y0, y1, mat="bricks", rauch=True):
    for y in range(y0, y1 + 1):
        w.setze(x, y, z, w.b(mat))
    if rauch:
        w.setze(x, y1 + 1, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))


def turm_rund(w, st, cx, cz, y0, R, H, dach_hoehe=None, dach_mat=None, fenster=4):
    """Runder Turm mit Fenstern und Kegeldach. Gibt die Spitzenhöhe zurück."""
    for y in range(y0, y0 + H):
        for x, z in kreisrand(R, cx, cz):
            a = math.atan2(z - cz, x - cx)
            fen = (y - y0) % fenster in (2,) and abs(math.sin(2 * a)) < 0.3 and y > y0 + 1
            w.setze(x, y, z, _scheibe_blk(w, st.glas, abs(z - cz) < abs(x - cx)) if fen
                    else st.wandblock(x, y, z, 1 + 2 * (y - y0) / H))
    dh = dach_hoehe or _r(R * 2.2, 3)
    dm = dach_mat or st.dach_voll
    yt = y0 + H
    for k in range(dh + 1):
        r = (R + 1) * (1 - k / (dh + 1))
        for x, z in kreisrand(max(0.2, r), cx, cz):
            w.setze(x, yt + k, z, w.b(dm))
    w.setze(cx, yt + dh + 1, cz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return yt + dh + 1


def zaun_rechteck(w, x0, z0, x1, z1, y, mat, luecke=None):
    pos = [(x, y, z) for x in range(x0, x1 + 1) for z in (z0, z1)] + \
          [(x, y, z) for x in (x0, x1) for z in range(z0 + 1, z1)]
    if luecke:
        pos = [p for p in pos if (p[0], p[2]) not in luecke]
    verbinde(w, pos, mat)


def garten(w, x0, z0, x1, z1, rng, blumen=("poppy", "dandelion", "oxeye_daisy", "azure_bluet", "cornflower")):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if rng.random() < 0.35:
                w.setze(x, 1, z, w.b(blumen[int(rng.integers(len(blumen)))]), ueberschreiben=False)


def wiese(w, r, rng, cx=0, cz=0, gras="grass_block"):
    for x, z in scheibe(r * 0.75 + 1, cx, cz):
        w.setze(x, 0, z, w.b(gras, snowy=False) if gras == "grass_block" else w.b(gras), ueberschreiben=False)

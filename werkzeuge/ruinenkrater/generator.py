"""Ruinen-Krater-Generator – überwucherte Terrassen-Ruine in einem Krater.

Erzeugt ein Minecraft-Strukturfile (.nbt, Format 1.20.1), das mit Create (Schematikkanone /
Schematic-Hologramm) oder mit /place template benutzt werden kann.

Aufbau (von außen nach innen):
  Rand aus Gras → hohe Säulenwand mit dunklen Bogennischen → Terrassenringe mit Stützmauern
  → Teich in der Mitte. Dazu: Säulenringe (teils eingestürzt), eine Treppe von der Mitte bis
  zur obersten Terrasse, ein Wandpfad hinauf zum Rand, Moos, Ranken, Büsche, Blumen und Bäume.

Leere Felder (-1) werden NICHT gespeichert – dort bleibt die Welt unverändert. Luft (0) wird
gespeichert und gräbt den Krater aus.
"""

from __future__ import annotations

import gzip
import math
import struct
import sys
from pathlib import Path

import numpy as np

DATA_VERSION = 3465  # Minecraft 1.20.1

# --------------------------------------------------------------------------- Palette

class Palette:
    def __init__(self):
        self.eintraege: list[tuple[str, tuple]] = []
        self.index: dict = {}
        self.b("minecraft:air")  # 0 = Luft

    def b(self, name: str, **props) -> int:
        schluessel = (name, tuple(sorted((k, str(v).lower()) for k, v in props.items())))
        if schluessel not in self.index:
            self.index[schluessel] = len(self.eintraege)
            self.eintraege.append(schluessel)
        return self.index[schluessel]


# --------------------------------------------------------------------------- Rauschen

def wertrauschen(rng, groesse: int, zelle: float) -> np.ndarray:
    """Weiches 2D-Rauschen 0..1 (bilinear interpoliertes Zufallsgitter)."""
    n = int(groesse / zelle) + 3
    gitter = rng.random((n, n))
    koord = np.arange(groesse) / zelle
    i0 = np.floor(koord).astype(int)
    f = koord - i0
    f = f * f * (3 - 2 * f)
    a = gitter[i0][:, i0]
    b = gitter[i0 + 1][:, i0]
    c = gitter[i0][:, i0 + 1]
    d = gitter[i0 + 1][:, i0 + 1]
    fx = f[:, None]
    fz = f[None, :]
    return (a * (1 - fx) * (1 - fz) + b * fx * (1 - fz) + c * (1 - fx) * fz + d * fx * fz)


def mehrlagig(rng, groesse, zelle):
    return 0.6 * wertrauschen(rng, groesse, zelle) + 0.4 * wertrauschen(rng, groesse, zelle / 2.7)


# --------------------------------------------------------------------------- Generator

def erzeuge(innenradius: int, tiefe: int, terrassen: int, seed: int = 1):
    rng = np.random.default_rng(seed)
    P = Palette()

    # Blöcke
    LUFT = 0
    STEINZIEGEL = P.b("minecraft:stone_bricks")
    MOOSZIEGEL = P.b("minecraft:mossy_stone_bricks")
    RISSZIEGEL = P.b("minecraft:cracked_stone_bricks")
    BRUCH = P.b("minecraft:cobblestone")
    MOOSBRUCH = P.b("minecraft:mossy_cobblestone")
    ANDESIT = P.b("minecraft:andesite")
    STEIN = P.b("minecraft:stone")
    DUNKEL = P.b("minecraft:deepslate_tiles")
    DUNKEL2 = P.b("minecraft:polished_deepslate")
    TUFF = P.b("minecraft:tuff")
    GRAS = P.b("minecraft:grass_block", snowy=False)
    ERDE = P.b("minecraft:dirt")
    GROBERDE = P.b("minecraft:coarse_dirt")
    WURZELERDE = P.b("minecraft:rooted_dirt")
    MOOS = P.b("minecraft:moss_block")
    MOOSTEPPICH = P.b("minecraft:moss_carpet")
    WASSER = P.b("minecraft:water", level=0)
    SEEROSE = P.b("minecraft:lily_pad")
    KURZGRAS = P.b("minecraft:grass")
    FARN = P.b("minecraft:fern")
    MOHN = P.b("minecraft:poppy")
    LOEWENZAHN = P.b("minecraft:dandelion")
    PORZELLAN = P.b("minecraft:azure_bluet")
    MARGERITE = P.b("minecraft:oxeye_daisy")
    KORNBLUME = P.b("minecraft:cornflower")
    STAMM = P.b("minecraft:oak_log", axis="y")
    LAUB = P.b("minecraft:oak_leaves", persistent=True, distance=7, waterlogged=False)
    AZALEE = P.b("minecraft:azalea_leaves", persistent=True, distance=7, waterlogged=False)
    BLUETENAZALEE = P.b("minecraft:flowering_azalea_leaves", persistent=True, distance=7, waterlogged=False)
    STUFE = {f: P.b("minecraft:stone_brick_stairs", facing=f, half="bottom", shape="straight", waterlogged=False)
             for f in ("north", "south", "east", "west")}
    MOOSSTUFE = {f: P.b("minecraft:mossy_stone_brick_stairs", facing=f, half="bottom", shape="straight", waterlogged=False)
                 for f in ("north", "south", "east", "west")}

    def ranke(n=False, e=False, s=False, w=False):
        return P.b("minecraft:vine", north=n, east=e, south=s, west=w, up=False)

    ZIEGEL_SOLIDE = {STEINZIEGEL, MOOSZIEGEL, RISSZIEGEL, BRUCH, MOOSBRUCH, ANDESIT, TUFF, DUNKEL, DUNKEL2}

    # Maße
    wand = 4
    rand = 3
    R = innenradius
    aussen = R + wand + rand
    W = 2 * aussen + 1
    c = aussen
    krone = 6
    y_teich = 3
    G = y_teich + tiefe                      # Bodenhöhe außen
    wandabfall = max(8, int(tiefe * 0.55))
    yT = G - wandabfall                      # oberste Terrasse
    H = G + krone + 2

    grid = np.full((W, H, W), -1, dtype=np.int16)

    xs = np.arange(W) - c
    X, Z = np.meshgrid(xs, xs, indexing="ij")
    r = np.sqrt(X ** 2 + Z ** 2)
    theta = np.arctan2(Z, X)  # -pi..pi

    moos = mehrlagig(rng, W, 7.0)
    huegel = mehrlagig(rng, W, 11.0)
    flecken = mehrlagig(rng, W, 4.0)
    bruch = mehrlagig(rng, W, 5.0)

    r_teich = 2.5 + R * 0.09
    r_start = r_teich + 1.6
    tw = (R - r_start) / terrassen

    def terrassenhoehe(k: int) -> int:
        # k = 0 innerste Terrasse
        return y_teich + 1 + int(round((k + 1) * (yT - y_teich - 1) / terrassen))

    def ziegel(x, z, y, mehr_moos=0.0):
        m = moos[x, z] + mehr_moos + (0.15 if y < yT else 0.0)
        u = rng.random()
        if u < 0.10:
            return RISSZIEGEL
        if u < 0.14:
            return ANDESIT
        if m > 0.62:
            return MOOSZIEGEL if rng.random() < 0.8 else MOOSBRUCH
        if m > 0.5 and rng.random() < 0.5:
            return MOOSZIEGEL
        return STEINZIEGEL

    def oberflaeche(x, z):
        f = flecken[x, z]
        u = rng.random()
        if f > 0.72:
            return MOOS
        if f < 0.2 and u < 0.5:
            return GROBERDE
        if u < 0.05:
            return WURZELERDE
        return GRAS

    oberkante = np.full((W, W), -1, dtype=int)   # Höhe der begehbaren Oberfläche im Krater
    ist_terrasse = np.zeros((W, W), dtype=bool)
    ist_wand = np.zeros((W, W), dtype=bool)

    # ---------------------------------------------------------------- Säulen
    nischen = max(8, int(round(2 * math.pi * R / 5.0)))

    for x in range(W):
        for z in range(W):
            rr = r[x, z]
            if rr > aussen + 0.5:
                continue
            if rr <= r_teich:
                # Teich: Boden, zwei Ebenen Wasser, darüber Luft
                grid[x, y_teich - 3:y_teich - 1, z] = STEIN
                grid[x, y_teich - 1:y_teich + 1, z] = WASSER
                grid[x, y_teich + 1:, z] = LUFT
                if rng.random() < 0.18:
                    grid[x, y_teich + 1, z] = SEEROSE
                oberkante[x, z] = y_teich
            elif rr <= r_start:
                # Teichrand
                h = y_teich + 1
                for y in range(h - 3, h + 1):
                    grid[x, y, z] = ziegel(x, z, y, 0.2)
                grid[x, h + 1:, z] = LUFT
                oberkante[x, z] = h
            elif rr < R:
                k = min(terrassen - 1, int((rr - r_start) / tw))
                h = terrassenhoehe(k)
                innenkante = (rr - r_start) - k * tw < 1.15
                if innenkante and k > 0:
                    # Stützmauer der Terrasse
                    unten = terrassenhoehe(k - 1) - 1
                    for y in range(unten, h + 1):
                        grid[x, y, z] = ziegel(x, z, y)
                    if bruch[x, z] > 0.72:  # niedrige Brüstung
                        grid[x, h + 1, z] = ziegel(x, z, h + 1)
                        oberkante[x, z] = h + 1
                    else:
                        oberkante[x, z] = h
                else:
                    for y in range(h - 5, h - 2):
                        grid[x, y, z] = STEIN
                    grid[x, h - 2:h, z] = ERDE
                    grid[x, h, z] = oberflaeche(x, z)
                    oberkante[x, z] = h
                    ist_terrasse[x, z] = True
                grid[x, oberkante[x, z] + 1:, z] = LUFT
            elif rr < R + wand:
                # Säulenwand mit Bogennischen
                ist_wand[x, z] = True
                spitze = G + int(round(krone * (0.35 + 0.65 * huegel[x, z])))
                if bruch[x, z] > 0.78:
                    spitze = G - int((bruch[x, z] - 0.78) * 30)  # eingestürzte Stelle
                u = ((theta[x, z] + math.pi) / (2 * math.pi) * nischen) % 1.0
                tiefe_in_wand = rr - R
                for y in range(yT - 4, spitze + 1):
                    blk = ziegel(x, z, y, 0.1)
                    if 0.16 < u < 0.84 and yT < y:
                        a = (u - 0.16) / 0.68
                        bogen = int(round(4 * (1 - math.sqrt(max(0.0, 1 - (2 * a - 1) ** 2)))))
                        nischen_oben = G - 2 - bogen
                        if y <= nischen_oben:
                            if tiefe_in_wand < 2.0:
                                blk = LUFT
                            elif tiefe_in_wand < 3.0:
                                blk = DUNKEL if rng.random() < 0.7 else DUNKEL2
                    grid[x, y, z] = blk
                # Bewuchs oben auf der Wand
                if spitze >= G and grid[x, spitze, z] in ZIEGEL_SOLIDE and moos[x, z] > 0.45:
                    grid[x, spitze, z] = MOOS if rng.random() < 0.6 else GRAS
                    if rng.random() < 0.25:
                        grid[x, spitze + 1, z] = AZALEE if rng.random() < 0.7 else BLUETENAZALEE
                oberkante[x, z] = spitze
            else:
                # Grasrand außen
                grid[x, G - 3:G, z] = ERDE
                grid[x, G, z] = oberflaeche(x, z) if rng.random() < 0.3 else GRAS
                oberkante[x, z] = G

    # ---------------------------------------------------------------- Säulenringe
    def saeulenring(k: int, schritt: float, hoehe: int, erhalten: float):
        h0 = terrassenhoehe(k)
        rc = r_start + (k + 0.55) * tw
        anzahl = max(6, int(round(2 * math.pi * rc / schritt)))
        winkel = [2 * math.pi * i / anzahl + rng.random() * 0.02 for i in range(anzahl)]
        hoehen = []
        for wkl in winkel:
            px = c + rc * math.cos(wkl)
            pz = c + rc * math.sin(wkl)
            ix, iz = int(round(px)), int(round(pz))
            ph = hoehe if rng.random() < 0.7 else int(hoehe * rng.uniform(0.3, 0.8))
            hoehen.append(ph)
            for y in range(h0 + 1, h0 + 1 + ph):
                if 0 <= ix < W and 0 <= iz < W and grid[ix, y, iz] == LUFT:
                    grid[ix, y, iz] = ziegel(ix, iz, y, 0.1)
        # Bögen/Balken zwischen intakten Säulen
        for i, wkl in enumerate(winkel):
            j = (i + 1) % anzahl
            if hoehen[i] < hoehe or hoehen[j] < hoehe or rng.random() > erhalten:
                continue
            w2 = winkel[j] if j > 0 else winkel[j] + 2 * math.pi
            schritte = int(rc * (w2 - wkl) * 2) + 2
            for t in range(schritte + 1):
                ww = wkl + (w2 - wkl) * t / schritte
                ix = int(round(c + rc * math.cos(ww)))
                iz = int(round(c + rc * math.sin(ww)))
                y = h0 + hoehe
                if 0 <= ix < W and 0 <= iz < W and grid[ix, y, iz] == LUFT:
                    grid[ix, y, iz] = ziegel(ix, iz, y, 0.1)
                # Bogenansatz unter dem Balken an den Säulen
                if (t == 1 or t == schritte - 1) and grid[ix, y - 1, iz] == LUFT:
                    grid[ix, y - 1, iz] = ziegel(ix, iz, y - 1, 0.1)

    ringe = sorted({max(1, terrassen // 3), terrassen - 2, max(1, (2 * terrassen) // 3)})
    for i, k in enumerate(ringe):
        if 0 < k < terrassen:
            saeulenring(k, schritt=5.0 + i, hoehe=5 + i + (1 if R > 30 else 0), erhalten=0.6)

    # ---------------------------------------------------------------- Treppe zur Mitte (Richtung Süden, +z)
    tx0, tx1 = c - 1, c + 1
    z_innen = c + int(math.ceil(r_start))
    z_aussen = c + R - 1
    laenge = max(1, z_aussen - z_innen)
    vorher = None
    for z in range(z_innen, z_aussen + 1):
        h = y_teich + 1 + int(round((z - z_innen) * (yT - y_teich - 1) / laenge))
        for x in range(tx0, tx1 + 1):
            for y in range(h - 3, h):
                grid[x, y, z] = ziegel(x, z, y, 0.15)
            if vorher is not None and h > vorher:
                grid[x, h, z] = (MOOSSTUFE if moos[x, z] > 0.55 else STUFE)["south"]
            else:
                grid[x, h, z] = ziegel(x, z, h, 0.15)
            grid[x, h + 1:, z] = LUFT
            oberkante[x, z] = h
            ist_terrasse[x, z] = False
        vorher = h

    # ---------------------------------------------------------------- Pfad an der Wand hinauf zum Rand
    th0 = math.pi * 0.62  # Startwinkel (südwestlich der Treppe)
    bogenlaenge = (G - yT) + 1
    for x in range(W):
        for z in range(W):
            rr = r[x, z]
            if not (R - 2.3 <= rr < R):
                continue
            dth = (theta[x, z] - th0) % (2 * math.pi)
            s = dth * R
            if s > bogenlaenge + 0.5:
                continue
            h = yT + int(s)
            for y in range(yT - 2, h):
                grid[x, y, z] = ziegel(x, z, y, 0.1)
            # Richtung des Anstiegs (Tangente)
            tx, tz = -math.sin(theta[x, z]), math.cos(theta[x, z])
            richtung = ("east" if tx > 0 else "west") if abs(tx) > abs(tz) else ("south" if tz > 0 else "north")
            grid[x, h, z] = STUFE[richtung] if s >= 1 else ziegel(x, z, h)
            grid[x, h + 1:, z] = LUFT
            oberkante[x, z] = h
            ist_terrasse[x, z] = False
    # Durchgang durch die Wandkrone am oberen Ende
    th1 = th0 + bogenlaenge / R
    for x in range(W):
        for z in range(W):
            if ist_wand[x, z] and abs(((theta[x, z] - th1 + math.pi) % (2 * math.pi)) - math.pi) * R < 1.6:
                grid[x, G + 1:, z] = np.where(grid[x, G + 1:, z] >= 0, LUFT, grid[x, G + 1:, z])
                grid[x, G, z] = ziegel(x, z, G)
                oberkante[x, z] = G

    # ---------------------------------------------------------------- Bäume
    def baum(x, z):
        h0 = oberkante[x, z]
        stamm = int(rng.integers(5, 8))
        if h0 + stamm + 3 >= H:
            return
        for y in range(h0 + 1, h0 + 1 + stamm):
            grid[x, y, z] = STAMM
        grid[x, h0, z] = ERDE
        mitte_y = h0 + stamm
        rad = rng.uniform(2.2, 3.2)
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                for dy in range(-2, 3):
                    d = math.sqrt(dx * dx + dz * dz + (dy * 1.4) ** 2)
                    if d > rad or rng.random() < 0.12:
                        continue
                    ax, ay, az = x + dx, mitte_y + dy, z + dz
                    if 0 <= ax < W and 0 <= az < W and 0 <= ay < H and grid[ax, ay, az] == LUFT:
                        grid[ax, ay, az] = LAUB if rng.random() < 0.85 else AZALEE

    kandidaten = np.argwhere(ist_terrasse & (r > r_start + 3) & (r < R - 3))
    rng.shuffle(kandidaten)
    gesetzt = []
    ziel_baeume = max(3, int(R / 4.5))
    for x, z in kandidaten:
        if len(gesetzt) >= ziel_baeume:
            break
        if abs(x - c) <= 3 and z > c:  # nicht auf die Treppe
            continue
        if all((x - a) ** 2 + (z - b) ** 2 > 64 for a, b in gesetzt):
            baum(int(x), int(z))
            gesetzt.append((x, z))

    # ---------------------------------------------------------------- Pflanzen auf den Terrassen
    for x in range(W):
        for z in range(W):
            if not ist_terrasse[x, z]:
                continue
            h = oberkante[x, z]
            if grid[x, h + 1, z] != LUFT:
                continue
            u = rng.random()
            unten = grid[x, h, z]
            if u < 0.05 and unten in (GRAS, MOOS):
                # kleiner Busch
                grid[x, h + 1, z] = AZALEE if rng.random() < 0.75 else BLUETENAZALEE
                if rng.random() < 0.4:
                    grid[x, h + 2, z] = AZALEE
            elif u < 0.30 and unten == GRAS:
                grid[x, h + 1, z] = KURZGRAS
            elif u < 0.35 and unten == GRAS:
                grid[x, h + 1, z] = FARN
            elif u < 0.45 and unten == GRAS:
                grid[x, h + 1, z] = [MOHN, MOHN, MOHN, LOEWENZAHN, PORZELLAN, MARGERITE, KORNBLUME][int(rng.integers(7))]
            elif u < 0.55 and unten == MOOS:
                grid[x, h + 1, z] = MOOSTEPPICH

    # Grasrand außen: etwas Bewuchs
    for x in range(W):
        for z in range(W):
            if r[x, z] >= R + wand and r[x, z] <= aussen + 0.5 and grid[x, G, z] == GRAS:
                u = rng.random()
                if u < 0.25:
                    grid[x, G + 1, z] = KURZGRAS
                elif u < 0.29:
                    grid[x, G + 1, z] = MOHN

    # ---------------------------------------------------------------- Ranken an Wänden
    massiv = np.isin(grid, list(ZIEGEL_SOLIDE | {MOOS, GRAS}))
    richtungen = [(1, 0, "e"), (-1, 0, "w"), (0, 1, "s"), (0, -1, "n")]
    for x in range(1, W - 1):
        for z in range(1, W - 1):
            if r[x, z] > R + 0.5:
                continue
            for dx, dz, seite in richtungen:
                nx, nz = x + dx, z + dz
                if not (ist_wand[nx, nz] or massiv[nx, :, nz].any()):
                    continue
                laenge_max = int(3 + 12 * moos[nx, nz]) if ist_wand[nx, nz] else int(2 + 4 * moos[nx, nz])
                if rng.random() > (0.55 if ist_wand[nx, nz] else 0.25):
                    continue
                # oberstes massives Feld des Nachbarn über dem eigenen Boden
                spalte = massiv[nx, :, nz]
                oben = None
                for y in range(H - 1, oberkante[x, z], -1):
                    if spalte[y]:
                        oben = y
                        break
                if oben is None:
                    continue
                laenge = int(rng.integers(2, max(3, laenge_max + 1)))
                for y in range(oben, max(oberkante[x, z], oben - laenge), -1):
                    if grid[x, y, z] == LUFT and spalte[y]:
                        grid[x, y, z] = ranke(n=seite == "n", e=seite == "e", s=seite == "s", w=seite == "w")
                    elif grid[x, y, z] != LUFT:
                        break

    info = {"breite": W, "hoehe": H, "tiefe": W, "boden_y": G, "teich_y": y_teich}
    return grid, P, info


# --------------------------------------------------------------------------- NBT (Strukturformat)

def _tstr(s: str) -> bytes:
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def strukturdatei(grid: np.ndarray, P: Palette, pfad: Path, mit_luft: bool = True):
    """Schreibt das Vanilla-Strukturformat (gzip-NBT): size, palette, blocks, entities, DataVersion."""
    W, H, Z = grid.shape
    teile = [b"\x0a", _tstr("")]
    # DataVersion
    teile += [b"\x03", _tstr("DataVersion"), struct.pack(">i", DATA_VERSION)]
    # size
    teile += [b"\x09", _tstr("size"), b"\x03", struct.pack(">i", 3), struct.pack(">iii", W, H, Z)]
    # palette
    teile += [b"\x09", _tstr("palette"), b"\x0a", struct.pack(">i", len(P.eintraege))]
    for name, props in P.eintraege:
        teile += [b"\x08", _tstr("Name"), _tstr(name)]
        if props:
            teile += [b"\x0a", _tstr("Properties")]
            for k, v in props:
                teile += [b"\x08", _tstr(k), _tstr(v)]
            teile.append(b"\x00")
        teile.append(b"\x00")
    # blocks
    maske = grid >= (0 if mit_luft else 1)
    pos = np.argwhere(maske)
    zust = grid[maske]
    teile += [b"\x09", _tstr("blocks"), b"\x0a", struct.pack(">i", len(pos))]
    kopf_pos = b"\x09" + _tstr("pos") + b"\x03" + struct.pack(">i", 3)
    kopf_state = b"\x03" + _tstr("state")
    for (x, y, z), s in zip(pos.tolist(), zust.tolist()):
        teile.append(kopf_pos + struct.pack(">iii", x, y, z) + kopf_state + struct.pack(">i", s) + b"\x00")
    # entities
    teile += [b"\x09", _tstr("entities"), b"\x00", struct.pack(">i", 0)]
    teile.append(b"\x00")
    with gzip.open(pfad, "wb", compresslevel=9) as f:
        f.write(b"".join(teile))
    return len(pos)


if __name__ == "__main__":
    R, D, T, seed = (int(a) for a in sys.argv[1:5])
    g, P, info = erzeuge(R, D, T, seed)
    print(info, "Palette:", len(P.eintraege))

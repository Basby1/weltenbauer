"""Fantasiehäuser II – zwanzig weitere verspielte Häuser in ungewöhnlichen Formen (eigene Entwürfe):
Teekannenhaus, Stiefelhaus, Kürbishaus, Baumstumpfhaus, Muschelhaus, Bücherturm, Laternenhaus, Flaschenhaus,
Krummes Haus, Hexenkate, Wolkenhaus, Uhrenhaus, Kerzenturm, Eichelhaus, Kugelhaus, Fasshaus, Stapelturm,
Vogelhaus, Gießkannenhaus und Zylinderhut-Haus."""

from __future__ import annotations

import math

import numpy as np

import wald2
from feinbau import Dachmat, Mix, fachwerk, fenster, kamin, kegeldach, laterne, mauer, platte, satteldach, stamm, \
    treppe, tuer, zaun
from flora import _neu
from lib import einfuegen

S = [1.0, 1.6]
SEITEN = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}


# ============================================================================ Werkzeuge

def form(w, test, lo, hi, mat, hohl=True, ueber=True):
    """Voxelisiert test(X, Y, Z) -> bool-Array im Kasten lo..hi; hohl: nur Hülle. Gibt Hüllzellen zurück."""
    X, Y, Z = np.mgrid[lo[0]:hi[0] + 1, lo[1]:hi[1] + 1, lo[2]:hi[2] + 1]
    m = test(X.astype(float), Y.astype(float), Z.astype(float))
    if hohl:
        p = np.pad(m, 1)
        innen = p[2:, 1:-1, 1:-1] & p[:-2, 1:-1, 1:-1] & p[1:-1, 2:, 1:-1] & p[1:-1, :-2, 1:-1] & \
            p[1:-1, 1:-1, 2:] & p[1:-1, 1:-1, :-2]
        huelle = m & ~innen
    else:
        huelle = m
        innen = np.zeros_like(m)
    zellen = []
    for i, j, k in np.argwhere(huelle):
        x, y, z = int(X[i, j, k]), int(Y[i, j, k]), int(Z[i, j, k])
        w.setze(x, y, z, mat(x, y, z) if callable(mat) else mat, ueber)
        zellen.append((x, y, z))
    if hohl:
        for i, j, k in np.argwhere(m & innen):
            w.bloecke.pop((int(X[i, j, k]), int(Y[i, j, k]), int(Z[i, j, k])), None)
    return zellen


def fenster_rund(w, zellen, n, y_min, y_max, glas="glass_pane", rahmen="spruce", rng=None, licht=True):
    """Setzt bis zu n Fenster in waagerecht nach außen zeigende Hüllzellen."""
    rng = rng or w.rng
    kand = []
    for (x, y, z) in zellen:
        if not (y_min <= y <= y_max):
            continue
        for s, (dx, dz) in SEITEN.items():
            if w.frei(x + dx, y, z + dz) and (x - dx, y, z - dz) not in w.bloecke and \
                    (x, y + 1, z) in w.bloecke and (x, y - 1, z) in w.bloecke:
                kand.append((x, y, z, s))
                break
    rng.shuffle(kand)
    gesetzt = []
    for (x, y, z, s) in kand:
        if len(gesetzt) >= n:
            break
        if any(abs(x - a) + abs(y - b) + abs(z - c) < 4 for a, b, c in gesetzt):
            continue
        dx, dz = SEITEN[s]
        rz = s in ("north", "south")
        w.setze(x, y, z, w.b(glas, east=rz, west=rz, north=not rz, south=not rz, waterlogged=False) if
                glas.endswith("pane") else w.b(glas))
        w.setze(x + dx, y - 1, z + dz, treppe(w, rahmen, {"north": "south", "south": "north", "east": "west",
                                                          "west": "east"}[s], "top"), False)
        if licht and w.frei(x - dx, y + 1, z - dz):
            w.setze(x - dx, y + 1, z - dz, w.b("lantern", hanging=True, waterlogged=False), False)
        gesetzt.append((x, y, z))
    return gesetzt


def tuer_rein(w, x, y, z, seite, holz="spruce"):
    dx, dz = SEITEN[seite]
    for k in (1, 2):
        for yy in (y, y + 1):
            w.bloecke.pop((x - dx * k, yy, z - dz * k), None)
    tuer(w, x, y, z, seite, holz=holz)


def garten(w, R, weg_seite="south", zaun_holz="spruce", dichte=0.45, baeume=1, seed=0):
    rng = w.rng
    zellen = []
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            if math.hypot(x, z) <= R + rng.random() * 0.8:
                w.setze(x, 0, z, w.b("grass_block", snowy=False))
                w.setze(x, -1, z, w.b("dirt"))
                zellen.append((x, z))
    dx, dz = SEITEN[weg_seite]
    for k in range(int(R) + 2):
        for q in (-1, 0, 1):
            x, z = dx * k + (q if dz else 0), dz * k + (q if dx else 0)
            w.setze(x, 0, z, w.b(["dirt_path", "gravel", "cobblestone"][int(rng.random() * 3)]))
    for (x, z) in zellen:
        d = math.hypot(x, z)
        if d > R - 0.6 and not (abs(x * dz - z * dx) <= 1 and (x * dx + z * dz) > 0):
            w.setze(x, 1, z, w.b(f"{zaun_holz}_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False))
    for (x, z) in zellen:
        if w.frei(x, 1, z) and w.P.name(w.bloecke.get((x, 0, z), 0)) == "minecraft:grass_block":
            r = rng.random()
            if r < dichte * 0.45:
                w.setze(x, 1, z, w.b("grass"))
            elif r < dichte * 0.8:
                w.setze(x, 1, z, w.b(["poppy", "dandelion", "azure_bluet", "oxeye_daisy", "cornflower", "allium",
                                      "pink_tulip"][int(rng.random() * 7)]))
            elif r < dichte * 0.9:
                w.setze(x, 1, z, w.b("azalea_leaves", persistent=True, distance=1, waterlogged=False))
    plaetze = [(x, z) for (x, z) in zellen if R * 0.65 < math.hypot(x, z) < R - 1.5]
    rng.shuffle(plaetze)
    for (x, z) in plaetze[:baeume]:
        if all(w.frei(x, h, z) for h in (1, 3, 5)):
            einfuegen(w, wald2.laubbaum(seed + x * 7 + z, "oak", H=5) if rng.random() < 0.5 else
                      wald2.kirschbaum(seed + x), x, 0, z)
    return zellen


def ring_wand(w, cx, cz, R, y0, y1, mat, mit_boden=True):
    for y in range(y0, y1 + 1):
        for x in range(cx - int(R) - 1, cx + int(R) + 2):
            for z in range(cz - int(R) - 1, cz + int(R) + 2):
                d = math.hypot(x - cx, z - cz)
                if R - 0.9 < d <= R + 0.3:
                    w.setze(x, y, z, mat(x, y, z) if callable(mat) else mat)
                elif d <= R - 0.9 and y == y0 and mit_boden:
                    w.setze(x, y - 1, z, w.b("spruce_planks"))


def M(w, liste, zelle=1.6, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


# ============================================================================ Häuser

def teekannenhaus(seed, g=0):
    """Teekannenhaus: eine riesige weiße Porzellan-Teekanne mit blauen Ornamentbändern, Tülle, Henkel und Deckel
    mit Knauf als Schornstein, runde Fenster und eine Tür im Bauch."""
    w = _neu(seed)
    s = S[g]
    R = 6 * s + 1
    garten(w, R + 5, seed=seed)
    porz = lambda x, y, z: w.b("blue_terracotta" if (y % 5 == 0) else "white_concrete" if (x + z) % 7 else
                               "light_blue_terracotta")
    yc = R * 0.95
    zellen = form(w, lambda X, Y, Z: (X ** 2 + ((Y - yc) / 0.85) ** 2 + Z ** 2 <= R * R) & (Y >= 1),
                  (-int(R) - 1, 1, -int(R) - 1), (int(R) + 1, int(yc + R) + 1, int(R) + 1), porz)
    for x in range(-int(R), int(R) + 1):
        for z in range(-int(R), int(R) + 1):
            if math.hypot(x, z) <= R - 1:
                w.setze(x, 0, z, w.b("spruce_planks"))
    ytop = int(yc + R * 0.85)
    for k in range(3):
        r = R * 0.55 - k * 0.8
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                if math.hypot(x, z) <= r:
                    w.setze(x, ytop + k, z, w.b("white_concrete" if k < 2 else "blue_terracotta"))
    kamin_y = ytop + 3
    w.setze(0, kamin_y, 0, w.b("gold_block"))
    w.setze(0, kamin_y + 1, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    from leuchtwald2 import bez, rohr
    rohr(w, bez((R - 1, yc - 1, 0), (R + 3 * s, yc, 0), (R + 4 * s, yc + 4 * s, 0)), 1.6 * s, 0.8 * s,
         w.b("white_concrete"))
    from skulptur import torus
    for (x, y, z) in [(x, y, z) for x in range(-int(R) - 5, -int(R) + 1) for y in range(int(yc - 4 * s),
                                                                                       int(yc + 5 * s))
                      for z in (-1, 0, 1)]:
        dd = math.hypot(x + R, y - yc) - 3.2 * s
        if abs(dd) < 0.8 and x < -R + 1 and abs(z) < 0.9 * s:
            w.setze(x, y, z, w.b("white_concrete"))
    fenster_rund(w, zellen, int(5 * s), 3, int(yc + 1))
    tuer_rein(w, 0, 1, int(R), "south")
    return w


def stiefelhaus(seed, g=0):
    """Stiefelhaus: ein gewaltiger, abgetragener Lederstiefel mit Schnürung ist zum Haus ausgebaut – Fenster im
    Schaft, Tür an der Spitze, ein kleines Dach und Schornstein oben im Schaft."""
    w = _neu(seed)
    s = S[g]
    garten(w, 10 * s + 3, "east", seed=seed)
    leder = M(w, [("brown_terracotta", 3), ("brown_concrete", 1), ("dark_oak_planks", 1)])
    H = 13 * s
    zs = form(w, lambda X, Y, Z: (((X + 2 * s) / (3.6 * s)) ** 2 + (Z / (3.4 * s)) ** 2 <= 1) & (Y >= 1) & (Y <= H),
              (int(-6 * s) - 2, 1, int(-4 * s) - 2), (int(2 * s) + 2, int(H), int(4 * s) + 2), leder)
    zf = form(w, lambda X, Y, Z: (((X - 2 * s) / (6.5 * s)) ** 2 + ((Y - 1) / (3.8 * s)) ** 2 + (Z / (3.4 * s)) ** 2
                                  <= 1) & (Y >= 1),
              (int(-5 * s), 1, int(-4 * s) - 2), (int(9 * s) + 2, int(5 * s) + 2, int(4 * s) + 2), leder)
    for x in range(int(-6 * s) - 1, int(9 * s) + 2):
        for z in range(int(-4 * s) - 1, int(4 * s) + 2):
            if (x, 1, z) in w.bloecke or (x, 2, z) in w.bloecke:
                w.setze(x, 0, z, w.b("black_concrete"))
    for y in range(3, int(H), 2):
        w.setze(int(1.6 * s) + 1, y, -1, w.b("white_wool"), False)
        w.setze(int(1.6 * s) + 1, y + 1, 1, w.b("white_wool"), False)
    satteldach(w, int(-6 * s), int(-4 * s), int(2 * s), int(4 * s), int(H) + 1,
               Dachmat(w, ["spruce", "dark_oak"]), first_x=False, ue=1, traufe="spruce")
    fenster_rund(w, zs + zf, int(6 * s), 3, int(H - 1))
    tuer_rein(w, int(8.4 * s), 1, 0, "east")
    return w


def kuerbishaus(seed, g=0):
    """Kürbishaus: ein riesiger orangefarbener Kürbis mit Rippen, dickem Stiel und Rankenblatt als Dach, Fenster mit
    Läden, eine Holztür und Laternen am Eingang."""
    w = _neu(seed)
    s = S[g]
    R = 6 * s + 1
    garten(w, R + 5, seed=seed)

    def kuerbis(X, Y, Z):
        a = np.arctan2(Z, X)
        r = R * (1 + 0.07 * np.cos(a * 10))
        return (X ** 2 + ((Y - R * 0.75) / 0.72) ** 2 + Z ** 2 <= r * r) & (Y >= 1)

    def mat(x, y, z):
        a = math.atan2(z, x)
        return w.b("orange_terracotta" if math.cos(a * 10) > 0.3 else "orange_concrete")
    zellen = form(w, kuerbis, (-int(R * 1.1) - 1, 1, -int(R * 1.1) - 1), (int(R * 1.1) + 1, int(R * 1.5) + 1,
                                                                         int(R * 1.1) + 1), mat)
    yt = int(R * 0.75 + R * 0.72)
    for y in range(yt, yt + int(3 * s) + 1):
        w.setze(0, y, 0, w.b("dark_oak_log" if y < yt + 2 else "green_terracotta", axis="y")
                if y < yt + 2 else w.b("green_terracotta"))
    for x in range(-int(3 * s), int(3 * s) + 1):
        for z in range(-int(2 * s), int(2 * s) + 1):
            if (x / (3 * s)) ** 2 + (z / (2 * s)) ** 2 <= 1:
                w.setze(x + int(2 * s), yt + 1 - abs(x) // 3, z, w.b("moss_block" if (x + z) % 3 else
                                                                      "green_concrete"))
    fenster_rund(w, zellen, int(5 * s), 3, int(R * 1.2))
    tuer_rein(w, 0, 1, int(R) + 1 if (0, 1, int(R) + 1) in w.bloecke else int(R), "south")
    return w


def baumstumpfhaus(seed, g=0):
    """Baumstumpfhaus: ein mächtiger, hohler Baumstumpf mit Rinde und Jahresringen auf dem Dach, Fenster zwischen
    Wurzeln, eine runde Tür, Pilze am Stamm und ein Moosdach mit Blumen."""
    w = _neu(seed)
    s = S[g]
    R = 5 * s + 1
    garten(w, R + 6, seed=seed)
    H = 7 * s + 3
    rinde = M(w, [("oak_wood", 2), ("dark_oak_wood", 2), ("spruce_wood", 1)], axis="y")
    ring_wand(w, 0, 0, R, 1, int(H), rinde)
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            d = math.hypot(x, z)
            if d <= R + 0.3:
                w.setze(x, int(H) + 1, z, w.b("stripped_oak_log", axis="y") if int(d) % 2 else
                        w.b("oak_planks"))
                if d <= R - 1 and w.rng.random() < 0.3:
                    w.setze(x, int(H) + 2, z, w.b(["moss_carpet", "red_mushroom", "brown_mushroom", "poppy"]
                                                  [int(w.rng.random() * 4)]))
    for k in range(7):
        a = k / 7 * 6.283
        for i in range(int(4 * s) + 2):
            x, z = round(math.cos(a) * (R + i * 0.8)), round(math.sin(a) * (R + i * 0.8))
            y = max(0, round(2.5 * s - i * 0.7))
            for yy in range(0, y + 1):
                w.setze(x, yy, z, w.b("dark_oak_wood", axis="y"))
    zellen = [(x, y, z) for (x, y, z), b in w.bloecke.items() if 2 <= y <= H - 1 and math.hypot(x, z) > R - 1]
    fenster_rund(w, zellen, int(5 * s), 3, int(H - 2))
    tuer_rein(w, 0, 1, int(R), "south", holz="spruce")
    for k in range(int(6 * s)):
        a = w.rng.random() * 6.283
        y = 2 + int(w.rng.random() * (H - 3))
        x, z = round(math.cos(a) * (R + 1)), round(math.sin(a) * (R + 1))
        if w.frei(x, y, z):
            w.setze(x, y, z, w.b("brown_mushroom_block", up=True, down=False, north=True, south=True, east=True,
                                 west=True))
    kamin(w, int(R) - 3, 0, int(H) + 1, int(H) + 3 + int(s), M(w, [("cobblestone", 1), ("mossy_cobblestone", 1)]))
    return w


def muschelhaus(seed, g=0):
    """Muschelhaus: eine große, rosa-weiß gerippte Jakobsmuschel steht aufrecht am Strand und ist zum Haus
    ausgebaut, mit Bullaugenfenstern, Perlenlampen und einem Steg."""
    w = _neu(seed)
    s = S[g]
    R = 7 * s + 1
    rng = w.rng
    for x in range(-int(R) - 6, int(R) + 7):
        for z in range(-int(R) - 4, int(R) + 8):
            w.setze(x, 0, z, w.b("water", level=0) if z > R + 3 else w.b("sand"))
            w.setze(x, -1, z, w.b("sandstone"))

    def schale(X, Y, Z):
        a = np.arctan2(Y, X)
        r = np.hypot(X, Y)
        rr = R * (0.92 + 0.08 * np.abs(np.cos(a * 9)))
        dick = 2.4 * s * (1 - (r / R) ** 2) + 1.2
        return (Y >= 0.5) & (r <= rr) & (np.abs(Z) <= dick)

    def mat(x, y, z):
        a = math.atan2(y, x)
        return w.b("pink_terracotta" if abs(math.sin(a * 9)) < 0.35 else "white_terracotta")
    zellen = form(w, schale, (-int(R) - 1, 1, -int(3 * s) - 3), (int(R) + 1, int(R) + 1, int(3 * s) + 3), mat)
    fenster_rund(w, zellen, int(6 * s), 3, int(R - 1), glas="light_blue_stained_glass_pane")
    tuer_rein(w, 0, 1, max(z for (x, y, z) in zellen if x == 0 and y == 1), "south")
    for k in range(int(R) + 5):
        for x in (-1, 0, 1):
            w.setze(x, 1, int(R) + k - 2, w.b("spruce_planks")) if k > 4 else None
    return w


def buecherturm(seed, g=0):
    """Bücherturm: ein Turm aus aufeinandergestapelten Riesenbüchern in Rot, Blau, Grün und Braun, leicht verdreht,
    mit goldenen Titelstreifen, Fenstern zwischen den Seiten und einer Leselampe obenauf."""
    w = _neu(seed)
    s = S[g]
    garten(w, 8 * s + 3, seed=seed)
    farben = ["red_terracotta", "blue_terracotta", "green_terracotta", "brown_terracotta", "purple_terracotta",
              "cyan_terracotta"]
    y = 1
    n = int(5 + 2 * s)
    rng = w.rng
    for k in range(n):
        B = int((6 - k * 0.35) * s + 2)
        T = int((4.5 - k * 0.25) * s + 2)
        h = int((1.6 + rng.random()) * s + 1)
        a = (rng.random() - 0.5) * 0.5
        ca, sa = math.cos(a), math.sin(a)
        for dx in range(-B - 2, B + 3):
            for dz in range(-B - 2, B + 3):
                u, v = dx * ca - dz * sa, dx * sa + dz * ca
                if abs(u) <= B and abs(v) <= T:
                    for yy in range(y, y + h):
                        rueck = u < -B + 1
                        if abs(u) > B - 1 or abs(v) > T - 1 or yy in (y, y + h - 1):
                            blk = w.b(farben[k % 6]) if rueck or yy in (y, y + h - 1) or abs(v) > T - 1 else \
                                w.b("white_concrete" if (yy + int(v)) % 2 else "white_terracotta")
                            if rueck and yy == y + h // 2:
                                blk = w.b("gold_block")
                            w.setze(dx, yy, dz, blk)
                        else:
                            w.bloecke.pop((dx, yy, dz), None)
        y += h
    zellen = [(x, yy, z) for (x, yy, z) in w.bloecke if 2 <= yy < y - 1]
    fenster_rund(w, zellen, int(6 * s), 2, y - 2)
    tuer_rein(w, 0, 1, max(z for (x, yy, z) in w.bloecke if x == 0 and yy == 1), "south")
    for yy in range(y, y + int(3 * s)):
        w.setze(0, yy, 0, w.b("iron_bars", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(0, y + int(3 * s), 0, w.b("lantern", hanging=False, waterlogged=False))
    return w


def laternenhaus(seed, g=0):
    """Laternenhaus: ein Haus in Form einer riesigen Laterne – schwarzes Eisengerippe, warm leuchtende Glaswände,
    ein spitzes Dach mit Ring, darin zwei Wohnetagen."""
    w = _neu(seed)
    s = S[g]
    garten(w, 8 * s + 3, seed=seed)
    B = int(3 * s + 2)
    H = int(9 * s + 3)
    for y in range(1, H + 1):
        for x in range(-B, B + 1):
            for z in range(-B, B + 1):
                rand = abs(x) == B or abs(z) == B
                ecke = abs(x) == B and abs(z) == B
                if y in (1, H) or ecke:
                    w.setze(x, y, z, w.b("polished_blackstone"))
                elif rand:
                    w.setze(x, y, z, w.b("polished_blackstone") if y % 4 == 0 else
                            w.b("orange_stained_glass" if (x + y + z) % 3 else "yellow_stained_glass"))
                elif y % 4 == 0:
                    w.setze(x, y, z, w.b("spruce_planks"))
    for x in range(-B + 1, B):
        for z in range(-B + 1, B):
            if w.rng.random() < 0.15:
                w.setze(x, 2, z, w.b("lantern", hanging=False, waterlogged=False))
    kegeldach(w, 0, 0, H + 1, B, Dachmat(w, ["polished_blackstone", "blackstone"]), form="kegel", eckig=True,
              spitze="chain")
    yt = H + 1 + int(B * 2.4 * 1.2) + 1
    for k in range(4):
        w.setze([1, -1, 0, 0][k], yt, [0, 0, 1, -1][k], w.b("polished_blackstone_wall", up=True, north="none",
                                                            south="none", east="none", west="none",
                                                            waterlogged=False))
    for (x, z) in ((-B, -B), (B, -B), (-B, B), (B, B)):
        w.setze(x, 0, z, w.b("polished_blackstone"))
    tuer_rein(w, 0, 2, B, "south")
    return w


def flaschenhaus(seed, g=0):
    """Flaschenhaus: eine riesige grüne Glasflasche liegt im Gras, darin steht ein kleines Fachwerkhaus mit
    Garten, der Korken ist die Tür."""
    w = _neu(seed)
    s = S[g]
    garten(w, 12 * s + 3, "east", baeume=2, seed=seed)
    R = 4.5 * s + 1
    L = 12 * s
    yc = R + 1

    def flasche(X, Y, Z):
        r = np.where(X < L / 2, R, np.maximum(1.6 * s, R - (X - L / 2) * 1.3))
        return (np.hypot(Y - yc, Z) <= r) & (X >= -L / 2) & (X <= L / 2 + 4 * s)
    form(w, flasche, (int(-L / 2) - 1, 1, -int(R) - 1), (int(L / 2 + 4 * s) + 1, int(yc + R) + 1, int(R) + 1),
         lambda x, y, z: w.b("lime_stained_glass" if (x + y) % 5 else "green_stained_glass"))
    for x in range(int(L / 2 + 4 * s) - 1, int(L / 2 + 4 * s) + 2):
        for y in range(int(yc) - 1, int(yc) + 2):
            for z in (-1, 0, 1):
                w.setze(x, y, z, w.b("stripped_oak_wood", axis="x"))
    for x in range(int(-L / 2) + 1, int(L / 2)):
        for z in range(-int(R * 0.7), int(R * 0.7) + 1):
            w.setze(x, int(yc - R * 0.7), z, w.b("grass_block", snowy=False))
    yb = int(yc - R * 0.7) + 1
    fachwerk(w, -2, -2, 2, 2, yb, yb + 2, M(w, [("white_terracotta", 1)]), holz="dark_oak", abstand=2,
             diagonal=False)
    satteldach(w, -2, -2, 2, 2, yb + 3, Dachmat(w, ["mcw:red_terracotta", "brick"]), first_x=True, ue=0,
               traufe="dark_oak")
    for x in (-int(L / 2) + 2, int(L / 2) - 2):
        w.setze(x, yb, 0, w.b("poppy"))
    return w


def krummes_haus(seed, g=0):
    """Krummes Haus: ein schmales, vielgeschossiges Fachwerkhaus, dessen Stockwerke sich in alle Richtungen
    verschieben und neigen, gekrönt von einem schiefen Spitzdach mit verbogenem Schornstein."""
    w = _neu(seed)
    s = S[g]
    garten(w, 8 * s + 3, seed=seed)
    B = int(2.5 * s + 2)
    n = int(3 + 2 * s)
    ox, oz = 0, 0
    rng = w.rng
    y = 1
    fuell = M(w, [("white_terracotta", 2), ("light_blue_terracotta", 1), ("yellow_terracotta", 1)])
    for k in range(n):
        h = 3 if k else 4
        fachwerk(w, ox - B, oz - B, ox + B, oz + B, y, y + h - 1, fuell, holz="dark_oak", abstand=2,
                 diagonal=k % 2 == 0)
        for (s_, dx, dz) in (("south", 0, B), ("east", B, 0), ("west", -B, 0)):
            fenster(w, ox + dx, y + 1, oz + dz, s_, holz="dark_oak", blumen=0.6, hoehe=1)
        y += h
        ox += int(rng.integers(-1, 2))
        oz += int(rng.integers(-1, 2))
    satteldach(w, ox - B - 1, oz - B, ox + B + 1, oz + B, y, Dachmat(w, ["mcw:purple_terracotta", "dark_oak",
                                                                         "deepslate_tile"]),
               first_x=False, ue=1, traufe="dark_oak", steil=2)
    tuer(w, 0, 1, B, "south", holz="dark_oak")
    for k in range(int(4 * s) + 3):
        w.setze(ox + B - 1 + (k // 3), y + 2 + k, oz - B + 1, w.b("bricks"))
    return w


def hexenkate(seed, g=0):
    """Hexenkate: eine windschiefe, dunkle Hütte auf Stelzen über einem Sumpftümpel, mit verdrehtem Spitzdach,
    Kesselfeuer, Kräuterbündeln, Laternen und einem Krähenkäfig."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    R = 9 * s + 3
    for x in range(-int(R), int(R) + 1):
        for z in range(-int(R), int(R) + 1):
            if math.hypot(x, z) <= R:
                w.setze(x, -1, z, w.b("mud"))
                w.setze(x, 0, z, w.b("water", level=0) if math.hypot(x, z) < R * 0.55 else
                        w.b("grass_block", snowy=False) if rng.random() < 0.6 else w.b("mud"))
                if w.P.name(w.bloecke[(x, 0, z)]) == "minecraft:water" and rng.random() < 0.08:
                    w.setze(x, 1, z, w.b("lily_pad"))
    B = int(2.5 * s + 2)
    yb = int(3 * s) + 1
    for (x, z) in ((-B, -B), (B, -B), (-B, B), (B, B)):
        for y in range(-1, yb):
            w.setze(x, y, z, stamm(w, "dark_oak", geschaelt=False))
    mauer(w, -B, -B, B, B, yb, yb + 3, M(w, [("dark_oak_planks", 2), ("spruce_planks", 1), ("mangrove_planks", 1)]))
    for x in range(-B, B + 1):
        for z in range(-B, B + 1):
            w.setze(x, yb - 1, z, w.b("dark_oak_planks"))
    for (sname, dx, dz) in (("east", B, 0), ("west", -B, 0)):
        fenster(w, dx, yb + 1, dz, sname, holz="dark_oak", blumen=0, glas="green_stained_glass_pane")
    tuer(w, 0, yb, B, "south", holz="dark_oak", laternen=False)
    for k in range(yb):
        w.setze(0, k, B + 1 + (yb - k), treppe(w, "dark_oak", "north"))
    kegeldach(w, 0, 0, yb + 4, B, Dachmat(w, ["mcw:black_terracotta", "deepslate_tile", "blackstone"]),
              form="nadel", eckig=True)
    w.setze(B + 2, 1, -B, w.b("cauldron"))
    w.setze(B + 2, 0, -B, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    laterne(w, B + 1, yb + 3, B + 1, 1, seele=True)
    return w


def wolkenhaus(seed, g=0):
    """Wolkenhaus: ein kleines weißes Häuschen mit blauem Dach sitzt auf einer dicken, flauschigen Wolke, aus der
    ein Regenbogen und ein feiner Regen fallen."""
    w = _neu(seed)
    s = S[g]
    rng = w.rng
    yw = int(8 * s + 4)
    R = 7 * s + 2
    for k in range(int(10 * s) + 6):
        a = rng.random() * 6.283
        d = rng.random() * R * 0.7
        cx, cz = math.cos(a) * d, math.sin(a) * d * 0.7
        r = (1.8 + rng.random() * 2.2) * s
        for dx in range(-int(r) - 1, int(r) + 2):
            for dy in range(-int(r) - 1, int(r) + 2):
                for dz in range(-int(r) - 1, int(r) + 2):
                    if dx * dx + (dy * 1.5) ** 2 + dz * dz <= r * r:
                        w.setze(round(cx + dx), yw + dy, round(cz + dz), w.b("white_wool" if rng.random() < 0.85
                                                                             else "white_concrete"))
    ytop = max(y for (x, y, z) in w.bloecke if abs(x) <= 2 and abs(z) <= 2)
    for x in range(-3, 4):
        for z in range(-3, 4):
            w.setze(x, ytop, z, w.b("white_wool"))
            for yy in range(ytop + 1, ytop + 12):
                w.bloecke.pop((x, yy, z), None)
    mauer(w, -2, -2, 2, 2, ytop + 1, ytop + 3, M(w, [("white_concrete", 2), ("calcite", 1)]))
    fenster(w, 2, ytop + 2, 0, "east", holz="birch", hoehe=1, blumen=0.8)
    fenster(w, -2, ytop + 2, 0, "west", holz="birch", hoehe=1, blumen=0.8)
    tuer(w, 0, ytop + 1, 2, "south", holz="birch", laternen=False)
    satteldach(w, -2, -2, 2, 2, ytop + 4, Dachmat(w, ["mcw:light_blue_terracotta", "mcw:blue_terracotta"]),
               first_x=True, ue=1, traufe="birch")
    farben = ["red_concrete", "orange_concrete", "yellow_concrete", "lime_concrete", "light_blue_concrete",
              "purple_concrete"]
    Rb = R * 0.9
    for i, f in enumerate(farben):
        r = Rb - i * 0.9
        for k in range(int(r * 10)):
            a = math.pi * k / (r * 10)
            x, y = round(R * 0.4 + r * math.cos(a) * -1), round(yw - 2 - r * math.sin(a) * 0.9)
            if y >= 0 and x > 0:
                w.setze(x, y, 0, w.b(f), False)
    for k in range(int(12 * s)):
        x, z = round((rng.random() - 0.5) * R * 1.2), round((rng.random() - 0.5) * R * 0.8)
        y0 = yw - int(2 * s) - 1
        for y in range(y0 - int(rng.random() * 4) - 1, y0):
            if w.frei(x, y, z) and (y % 2):
                w.setze(x, y, z, w.b("light_blue_stained_glass_pane", north=False, south=False, east=False,
                                     west=False, waterlogged=False))
    return w


def uhrenhaus(seed, g=0):
    """Uhrenhaus: ein schmales Giebelhaus, dessen ganze Front ein riesiges Zifferblatt mit goldenen Zeigern ist,
    darüber ein Kuckucks-Erker und Glockentürmchen, Pendel unten."""
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 3, seed=seed)
    B = int(4 * s + 2)
    T = int(4 * s + 2)
    H = int(9 * s + 3)
    mauer(w, -B, -T, B, T, 1, H, M(w, [("spruce_planks", 2), ("stripped_spruce_log", 1)]), ecke=stamm(w, "dark_oak"))
    satteldach(w, -B, -T, B, T, H + 1, Dachmat(w, ["dark_oak", "spruce"]), first_x=False, ue=1, traufe="dark_oak",
               steil=2)
    R = B - 0.6
    yc = H * 0.6
    for x in range(-B + 1, B):
        for y in range(1, H + 1):
            d = math.hypot(x, y - yc)
            if d <= R:
                w.setze(x, y, T + 1, w.b("gold_block") if d > R - 0.8 else w.b("white_concrete") if
                        not (abs(d - (R - 1.6)) < 0.5 and (round(math.degrees(math.atan2(y - yc, x))) % 30 < 8))
                        else w.b("black_concrete"))
    for k in range(int(R - 1)):
        w.setze(0, round(yc + k), T + 2, w.b("gold_block"))
    for k in range(int(R * 0.7)):
        w.setze(k, round(yc), T + 2, w.b("gold_block"))
    w.setze(0, round(yc), T + 2, w.b("black_concrete"))
    for y in range(1, int(yc - R)):
        w.setze(0, y, T + 2, w.b("chain", axis="y", waterlogged=False))
    w.setze(0, 1, T + 2, w.b("gold_block"))
    tuer(w, -B + 1, 1, T, "south", holz="dark_oak")
    for (sname, dx) in (("east", B), ("west", -B)):
        for y in range(2, H - 1, 3):
            fenster(w, dx, y, 0, sname, holz="dark_oak", blumen=0.6)
    return w


def kerzenturm(seed, g=0):
    """Kerzenturm: ein Wohnturm in Form einer dicken, weißen Kerze mit herabgelaufenem Wachs, oben brennt eine
    riesige Flamme, Fenster wie Wachstropfen, ein Kerzenständer als Sockel."""
    w = _neu(seed)
    s = S[g]
    garten(w, 8 * s + 3, seed=seed)
    R = 3.4 * s + 1
    H = int(12 * s + 4)
    for x in range(-int(R) - 2, int(R) + 3):
        for z in range(-int(R) - 2, int(R) + 3):
            if math.hypot(x, z) <= R + 2:
                w.setze(x, 1, z, w.b("gold_block") if math.hypot(x, z) > R + 1 else w.b("raw_gold_block"))
    zellen = form(w, lambda X, Y, Z: (np.hypot(X, Z) <= R) & (Y >= 2) & (Y <= H),
                  (-int(R) - 1, 2, -int(R) - 1), (int(R) + 1, H, int(R) + 1),
                  lambda x, y, z: w.b("white_concrete" if (x + z + y) % 6 else "white_terracotta"))
    rng = w.rng
    for k in range(int(10 * s)):
        a = rng.random() * 6.283
        x, z = round(math.cos(a) * (R + 0.8)), round(math.sin(a) * (R + 0.8))
        L = int(1 + rng.random() * 4 * s)
        for y in range(H - L, H + 1):
            w.setze(x, y, z, w.b("white_concrete"), False)
    w.setze(0, H + 1, 0, w.b("black_concrete"))
    for y in range(H + 2, H + 2 + int(4 * s) + 1):
        r = (1 - (y - H - 2) / (4 * s + 1)) * 1.5 * s
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if math.hypot(dx, dz) <= r:
                    w.setze(dx, y, dz, w.b("shroomlight" if math.hypot(dx, dz) < r - 0.7 else
                                           "orange_stained_glass"))
    fenster_rund(w, zellen, int(5 * s), 4, H - 2, glas="yellow_stained_glass_pane")
    tuer_rein(w, 0, 2, int(R), "south")
    return w


def eichelhaus(seed, g=0):
    """Eichelhaus: eine riesige Eichel mit glatter brauner Schale und schuppigem Hütchen als Dach, oben der kleine
    Stiel als Schornstein, Fenster mit Läden und eine Rundtür."""
    w = _neu(seed)
    s = S[g]
    garten(w, 8 * s + 3, seed=seed)
    R = 4.5 * s + 1
    yc = R * 1.2
    zellen = form(w, lambda X, Y, Z: (X ** 2 + ((Y - yc) / 1.3) ** 2 + Z ** 2 <= R * R) & (Y >= 1),
                  (-int(R) - 1, 1, -int(R) - 1), (int(R) + 1, int(yc + R * 1.3), int(R) + 1),
                  lambda x, y, z: w.b("orange_terracotta" if (x * 3 + z) % 5 else "brown_terracotta"))
    yk = int(yc + R * 0.5)
    Rk = R + 0.8
    for y in range(yk, int(yc + R * 1.35) + 1):
        r = Rk * math.sqrt(max(0, 1 - ((y - yk) / (R * 0.95)) ** 2))
        for x in range(-int(Rk) - 1, int(Rk) + 2):
            for z in range(-int(Rk) - 1, int(Rk) + 2):
                d = math.hypot(x, z)
                if d <= r and (d > r - 1.2 or y == int(yc + R * 1.35)):
                    w.setze(x, y, z, w.b("brown_concrete" if (x + y + z) % 2 else "dark_oak_planks"))
                elif d <= r - 1.2:
                    w.bloecke.pop((x, y, z), None)
    ytop = int(yc + R * 1.35)
    for y in range(ytop + 1, ytop + int(2 * s) + 2):
        w.setze(0, y, 0, w.b("dark_oak_log", axis="y"))
    w.setze(0, ytop + int(2 * s) + 2, 0, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                              waterlogged=False))
    fenster_rund(w, zellen, int(5 * s), 3, yk - 1)
    tuer_rein(w, 0, 1, max(z for (x, y, z) in zellen if x == 0 and y == 1), "south")
    return w


def kugelhaus(seed, g=0):
    """Kugelhaus: eine weiße Kugel mit Bullaugen ruht auf einem Ring aus Holzpfeilern, eine Wendeltreppe führt
    hinauf, auf dem Scheitel ein Sonnendeck mit Geländer."""
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 3, seed=seed)
    R = 5 * s + 1
    yc = R + 3 * s + 1
    zellen = form(w, lambda X, Y, Z: X ** 2 + (Y - yc) ** 2 + Z ** 2 <= R * R,
                  (-int(R) - 1, int(yc - R) - 1, -int(R) - 1), (int(R) + 1, int(yc + R) + 1, int(R) + 1),
                  lambda x, y, z: w.b("white_concrete" if (y % 4) else "light_gray_concrete"))
    for k in range(6):
        a = k / 6 * 6.283
        x, z = round(math.cos(a) * R * 0.6), round(math.sin(a) * R * 0.6)
        for y in range(1, int(yc - R * 0.8) + 1):
            if w.frei(x, y, z):
                w.setze(x, y, z, stamm(w, "spruce"))
    for i in range(int(yc - R) * 4):
        a = i / 4 * 0.9
        y = 1 + i // 4
        x, z = round(math.cos(a) * 2), round(math.sin(a) * 2)
        w.setze(x, y, z, w.b("spruce_slab", type="top", waterlogged=False), False)
    w.setze(0, int(yc - R), 0, w.b("air"))
    fenster_rund(w, zellen, int(7 * s), int(yc - R * 0.5), int(yc + R * 0.5), glas="light_blue_stained_glass_pane")
    yt = int(yc + R)
    for x in range(-2, 3):
        for z in range(-2, 3):
            w.setze(x, yt, z, w.b("spruce_planks"))
            if abs(x) == 2 or abs(z) == 2:
                w.setze(x, yt + 1, z, zaun(w, "spruce"))
    return w


def fasshaus(seed, g=0):
    """Fasshaus: ein riesiges, liegendes Holzfass mit Eisenreifen ist ein gemütliches Haus, vorne eine runde
    Tür mit Vordach, seitlich Fenster und ein Ofenrohr, davor Hocker und Laterne."""
    w = _neu(seed)
    s = S[g]
    garten(w, 10 * s + 3, "east", seed=seed)
    R = 4.5 * s + 1
    L = 9 * s + 2
    yc = R + 1

    def fass(X, Y, Z):
        bauch = R * (1 + 0.12 * (1 - (X / (L / 2)) ** 2))
        return (np.hypot(Y - yc, Z) <= bauch) & (np.abs(X) <= L / 2)
    zellen = form(w, fass, (int(-L / 2) - 1, 0, -int(R * 1.15) - 1), (int(L / 2) + 1, int(yc + R * 1.15) + 1,
                                                                     int(R * 1.15) + 1),
                  lambda x, y, z: w.b("polished_blackstone") if abs(x) in (int(L / 2) - 1, int(L / 5)) else
                  w.b("spruce_planks" if (z + y) % 3 else "stripped_spruce_log", **({} if (z + y) % 3 else
                                                                                    {"axis": "x"})))
    for x in range(int(-L / 2) + 1, int(L / 2)):
        for z in range(-int(R * 0.7), int(R * 0.7) + 1):
            w.setze(x, int(yc - R * 0.7), z, w.b("spruce_planks"))
    fenster_rund(w, zellen, int(4 * s), int(yc - 1), int(yc + 1))
    tuer_rein(w, int(L / 2), int(yc - R * 0.7) + 1, 0, "east")
    for y in range(int(yc + R * 0.8), int(yc + R * 1.15) + int(3 * s)):
        w.setze(int(-L / 4), y, 1, w.b("polished_blackstone"), False)
    return w


def stapelturm(seed, g=0):
    """Stapelturm: ein Turm aus vier verschiedenen kleinen Häusern, kreuz und quer aufeinandergestapelt – Steinhaus,
    Fachwerkhaus, blaues Holzhaus und ein Türmchen ganz oben, verbunden durch Leitern."""
    from himmelsstadt2 import haus
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 3, seed=seed)
    stile = ["stein", "fachwerk", "blau", "terrakotta"]
    y = 1
    rng = w.rng
    ox = 0
    for k in range(3 + (g > 0)):
        B = int(7 - k + s * 2)
        T = int(6 - k * 0.5 + s)
        first = haus(w, ox, 0, B, T, y + 2 if k else y, stile[k], geschosse=1, tuer_s="south", schorn=k == 2,
                     first_x=k % 2 == 0)
        y = (first or y + 6) - 1
        ox += int(rng.integers(-1, 2))
    kegeldach(w, ox, 0, y + 1, 1, Dachmat(w, ["mcw:red_terracotta", "brick"]), form="nadel", eckig=True)
    return w


def vogelhaus(seed, g=0):
    """Vogelhaus: ein riesiges Vogelhäuschen auf einem dicken Pfahl, mit großem Einflugloch als Tür, Sitzstange
    als Balkon, buntem Dach und einer Strickleiter."""
    w = _neu(seed)
    s = S[g]
    garten(w, 8 * s + 3, seed=seed)
    H = int(6 * s + 3)
    for y in range(1, H):
        for dx in (0, 1):
            for dz in (0, 1):
                w.setze(dx, y, dz, w.b("oak_log", axis="y"))
    B = int(3 * s + 2)
    yb = H
    for x in range(-B + 1, B + 1):
        for z in range(-B + 1, B + 1):
            w.setze(x, yb, z, w.b("oak_planks"))
    mauer(w, -B + 1, -B + 1, B, B, yb + 1, yb + int(4 * s) + 1, M(w, [("yellow_terracotta", 2), ("orange_terracotta",
                                                                                                1)]))
    R = 1.4 * s
    cy = yb + int(2 * s) + 1
    for x in range(-B, B + 1):
        for y in range(yb + 1, yb + int(5 * s)):
            if math.hypot(x - 0.5, y - cy) <= R:
                w.bloecke.pop((x, y, B), None)
    for x in range(-1, 3):
        w.setze(x, cy - int(R) - 1, B + 1, w.b("oak_fence", east=True, west=True, north=False, south=False,
                                                waterlogged=False))
    satteldach(w, -B + 1, -B + 1, B, B, yb + int(4 * s) + 2, Dachmat(w, ["mcw:red_terracotta", "mcw:green_terracotta"
                                                                           if False else "brick", "crimson"]),
               first_x=False, ue=1, traufe="oak")
    for y in range(1, H):
        w.setze(2, y, 1, w.b("ladder", facing="east", waterlogged=False))
    return w


def giesskannenhaus(seed, g=0):
    """Gießkannenhaus: eine riesige grüne Blechgießkanne mit Henkel und langer Tülle samt Brausekopf, aus dem
    echtes Wasser auf ein Blumenbeet rieselt, Fenster im Bauch."""
    w = _neu(seed)
    s = S[g]
    garten(w, 11 * s + 3, dichte=0.7, seed=seed)
    R = 4.5 * s + 1
    H = 8 * s + 2
    zellen = form(w, lambda X, Y, Z: (np.hypot(X, Z) <= R) & (Y >= 1) & (Y <= H),
                  (-int(R) - 1, 1, -int(R) - 1), (int(R) + 1, int(H), int(R) + 1),
                  lambda x, y, z: w.b("green_concrete" if y % 4 else "lime_concrete"))
    for x in range(-int(R) - 1, int(R) + 2):
        for z in range(-int(R) - 1, int(R) + 2):
            if math.hypot(x, z) <= R:
                w.setze(x, int(H) + 1, z, w.b("green_concrete"))
    from leuchtwald2 import bez, rohr
    rohr(w, bez((R - 1, 2, 0), (R + 4 * s, 3 * s, 0), (R + 7 * s, H + 1, 0)), 1.0 * s + 0.3, 0.6 * s + 0.3,
         w.b("green_concrete"))
    ex = round(R + 7 * s)
    for dy in range(-1, 2):
        for dz in range(-1, 2):
            w.setze(ex + 1, int(H) + 1 + dy, dz, w.b("waxed_cut_copper"))
    for y in range(1, int(H)):
        if y % 2:
            w.setze(ex + 2, y, 0, w.b("light_blue_stained_glass_pane", north=False, south=False, east=False,
                                      west=False, waterlogged=False), False)
    for y in range(int(H * 0.4), int(H) + 4):
        t = (y - H * 0.4) / (H * 0.6 + 4)
        x = -round(R + 2 * s * math.sin(math.pi * min(1, t)))
        w.setze(x, y, 0, w.b("green_concrete"))
    for x in range(-int(R) - int(2 * s), 0):
        w.setze(x, int(H) + 3, 0, w.b("green_concrete"))
    fenster_rund(w, zellen, int(4 * s), 3, int(H - 1))
    tuer_rein(w, 0, 1, int(R), "south")
    return w


def zylinderhaus(seed, g=0):
    """Zylinderhut-Haus: ein riesiger schwarzer Zylinderhut mit breiter Krempe und rotem Hutband ist ein Haus, die
    Krempe dient als Veranda, oben ragt eine Spielkarte als Wetterfahne heraus."""
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 3, seed=seed)
    R = 4 * s + 1
    H = 9 * s + 2
    Rk = R + 3 * s
    for x in range(-int(Rk) - 1, int(Rk) + 2):
        for z in range(-int(Rk) - 1, int(Rk) + 2):
            if math.hypot(x, z) <= Rk:
                w.setze(x, 1, z, w.b("black_concrete" if math.hypot(x, z) > R else "spruce_planks"))
                if Rk - 0.8 < math.hypot(x, z):
                    w.setze(x, 2, z, w.b("black_concrete"))
    zellen = form(w, lambda X, Y, Z: (np.hypot(X, Z) <= R * (1 + 0.04 * (Y - 2))) & (Y >= 2) & (Y <= H),
                  (-int(R * 1.5) - 1, 2, -int(R * 1.5) - 1), (int(R * 1.5) + 1, int(H), int(R * 1.5) + 1),
                  lambda x, y, z: w.b("red_concrete" if 3 <= y <= 4 else "black_concrete"))
    Rt = R * (1 + 0.04 * (H - 2))
    for x in range(-int(Rt) - 1, int(Rt) + 2):
        for z in range(-int(Rt) - 1, int(Rt) + 2):
            if math.hypot(x, z) <= Rt:
                w.setze(x, int(H) + 1, z, w.b("black_concrete"))
    for y in range(int(H) + 2, int(H) + 2 + int(3 * s)):
        w.setze(0, y, 0, w.b("white_concrete"))
        w.setze(1, y, 0, w.b("white_concrete" if y % 2 else "red_concrete"))
    fenster_rund(w, zellen, int(5 * s), 5, int(H - 1), glas="yellow_stained_glass_pane")
    tuer_rein(w, 0, 2, int(R), "south")
    return w


FANTASIE2 = {
    "teekannenhaus": ("Porzellankannen-Villa", teekannenhaus),
    "stiefelhaus": ("Wanderstiefel-Herberge", stiefelhaus),
    "kuerbishaus": ("Riesenkürbis-Haus", kuerbishaus),
    "baumstumpfhaus": ("Moosstumpf-Haus", baumstumpfhaus),
    "muschelhaus": ("Muschelhaus", muschelhaus),
    "buecherturm": ("Bücherturm", buecherturm),
    "laternenhaus": ("Laternenhaus", laternenhaus),
    "flaschenhaus": ("Flaschenhaus", flaschenhaus),
    "krummes_haus": ("Krummes Haus", krummes_haus),
    "hexenkate": ("Hexenkate am Tümpel", hexenkate),
    "wolkenhaus": ("Wolkenhaus", wolkenhaus),
    "uhrenhaus": ("Uhrenhaus", uhrenhaus),
    "kerzenturm": ("Kerzenturm", kerzenturm),
    "eichelhaus": ("Eichel-Wohnturm", eichelhaus),
    "kugelhaus": ("Kugelhaus", kugelhaus),
    "fasshaus": ("Fasshaus", fasshaus),
    "stapelturm": ("Stapelturm", stapelturm),
    "vogelhaus": ("Vogelhaus", vogelhaus),
    "giesskannenhaus": ("Gießkannenhaus", giesskannenhaus),
    "zylinderhaus": ("Zylinderhut-Haus", zylinderhaus),
}

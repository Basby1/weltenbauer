"""Feenstadt II – zwanzig weitere Bauten des kleinen Volks zwischen Riesenpflanzen: Fingerhut-Türme, Erdbeerhaus,
Haselnuss-Schänke, Kleeblatt-Windmühle, Mohnblüten-Pavillon, Spinnennetz-Brücke, Marienkäfer-Kutsche,
Glühwürmchen-Leuchtturm, Fingerhut-Brunnen, Blätterboot-Hafen, Pilzring-Markt, Wurzelhöhle, Schneeglöckchen-
Kapelle, Apfelhaus, Vogelnest-Dorf, Rosenpalast, Seifenblasen-Schloss, Mondblumen-Garten, Grashalm-Schaukeln und
Tannenzapfen-Turm."""

from __future__ import annotations

import math

import numpy as np

from fantasie2 import fenster_rund, form, garten, tuer_rein
from feinbau import Dachmat, Mix, kegeldach, laterne, platte, satteldach, stamm, treppe, tuer, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr

S = [0.6, 1.0, 1.6, 2.5]


def M(w, liste, zelle=1.4, **pr):
    return Mix(w, liste, zelle=zelle, **pr)


def stiel(w, x, z, H, r=0.6, mat="lime_terracotta", neig=(0, 0)):
    pts = bez((x, 0, z), (x, H * 0.6, z), (x + neig[0], H, z + neig[1]))
    rohr(w, pts, r, r * 0.8, w.b(mat))
    return (x + neig[0], H, z + neig[1])


def bluete(w, cx, cy, cz, R, farbe, mitte="yellow_concrete", n=6, schale=0.3):
    for k in range(n):
        a = k / n * 6.283
        for i in range(int(R * 3)):
            t = i / (R * 3)
            for q in np.arange(-math.sin(math.pi * t) * R * 0.4, math.sin(math.pi * t) * R * 0.4 + 0.01, 0.5):
                x = cx + math.cos(a) * R * t - math.sin(a) * q
                z = cz + math.sin(a) * R * t + math.cos(a) * q
                w.setze(round(x), round(cy + t * t * R * schale * 2), round(z), w.b(farbe), False)
    kugel(w, cx, cy + 0.5, cz, max(0.8, R * 0.22), w.b(mitte))


def blatt(w, cx, cy, cz, L, B, winkel, mat="green_terracotta", neig=0.25):
    ca, sa = math.cos(winkel), math.sin(winkel)
    for i in range(int(L * 2)):
        t = i / (L * 2)
        b = math.sin(math.pi * t) * B
        for q in np.arange(-b, b + 0.01, 0.5):
            x = cx + ca * L * t - sa * q
            z = cz + sa * L * t + ca * q
            y = cy + t * L * neig - (t * L * 0.15) ** 2 * 0.3
            w.setze(round(x), round(y), round(z), w.b(mat if abs(q) > 0.4 else "lime_terracotta"), False)


def vorne(zellen, ersatz):
    zs = [z for (x, y, z) in zellen if x == 0 and y <= 2]
    return max(zs) if zs else int(ersatz)


def haeuschen_rund(w, cx, cz, y, r, H, wand, dach, holz="spruce"):
    for yy in range(y, y + H):
        for x in range(cx - r - 1, cx + r + 2):
            for z in range(cz - r - 1, cz + r + 2):
                d = math.hypot(x - cx, z - cz)
                if r - 0.8 < d <= r + 0.3:
                    w.setze(x, yy, z, wand(x, yy, z) if callable(wand) else w.b(wand))
    kegeldach(w, cx, cz, y + H, r, dach, form="glocke")
    tuer(w, cx, y, cz + r, "south", holz=holz, laternen=False)
    fenster(w, cx + r, y + 1, cz, "east", holz)
    fenster(w, cx - r, y + 1, cz, "west", holz)


def fenster(w, x, y, z, seite, holz="spruce"):
    rz = seite in ("north", "south")
    w.setze(x, y, z, w.b("glass_pane", east=rz, west=rz, north=not rz, south=not rz, waterlogged=False))


# ============================================================================ Bauten

def fingerhuttuerme(seed, g=1):
    """Fingerhut-Türme: drei silberne Riesenfingerhüte mit gepunkteter Oberfläche sind zu Wohntürmen ausgebaut,
    mit Rundfenstern, Leitern und einem Nadelöhr-Tor aus einer riesigen Nähnadel."""
    w = _neu(seed)
    s = S[g]
    garten(w, 10 * s + 4, seed=seed)
    for k, (cx, cz) in enumerate(((0, 0), (round(-6 * s - 2), round(3 * s)), (round(6 * s + 2), round(2 * s)))):
        R = (3 - k * 0.5) * s + 1.5
        H = (6 - k) * s + 3
        zellen = form(w, lambda X, Y, Z, cx=cx, cz=cz, R=R, H=H: (np.hypot(X - cx, Z - cz) <= R * (1 - 0.15 * Y / H))
                      & (Y >= 1) & (Y <= H) | ((np.hypot(X - cx, Z - cz) <= R * 0.85) & (Y > H) &
                                                (np.hypot(X - cx, Z - cz) ** 2 + (Y - H) ** 2 <= (R * 0.85) ** 2)),
                      (cx - int(R) - 1, 1, cz - int(R) - 1), (cx + int(R) + 1, int(H + R) + 1, cz + int(R) + 1),
                      lambda x, y, z: w.b("iron_block" if (x + y * 2 + z) % 3 else "light_gray_concrete"))
        fenster_rund(w, zellen, int(3 * s), 3, int(H - 1), licht=False)
        tuer_rein(w, cx, 1, cz + int(R), "south")
    for y in range(1, int(8 * s) + 3):
        w.setze(0, y, int(6 * s + 4), w.b("iron_block" if y < int(8 * s) else "air"))
    return w


def erdbeerhaus(seed, g=1):
    """Erdbeerhaus: eine riesige rote Erdbeere mit gelben Samenpünktchen und grünem Blätterkranz als Dach, Fenster
    mit weißen Läden und eine runde Tür, Erdbeerpflanzen ringsum."""
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 3, seed=seed)
    R = 4 * s + 1.5
    H = 8 * s + 3

    def beere(X, Y, Z):
        t = np.clip((Y - 1) / H, 0, 1)
        r = R * np.sin(np.pi * np.clip(t * 0.85 + 0.15, 0, 1)) ** 0.6
        return (np.hypot(X, Z) <= r) & (Y >= 1) & (Y <= H)
    zellen = form(w, beere, (-int(R) - 1, 1, -int(R) - 1), (int(R) + 1, int(H) + 1, int(R) + 1),
                  lambda x, y, z: w.b("yellow_concrete" if (x * 3 + y * 5 + z * 7) % 11 == 0 else "red_concrete"))
    for k in range(6):
        blatt(w, 0, H, 0, R * 1.2, R * 0.4, k / 6 * 6.283, neig=-0.1)
    for y in range(int(H) + 1, int(H) + int(2 * s) + 2):
        w.setze(0, y, 0, w.b("green_terracotta"))
    fenster_rund(w, zellen, int(4 * s), 3, int(H - 2))
    tuer_rein(w, 0, 1, vorne(zellen, R), "south")
    return w


def haselnussschaenke(seed, g=1):
    """Haselnuss-Schänke: eine große, glänzend braune Haselnuss mit Fachwerkanbau, Wirtshausschild, Tischen aus
    Pilzhüten vor der Tür und Lampions an Grashalmen."""
    w = _neu(seed)
    s = S[g]
    garten(w, 10 * s + 3, seed=seed)
    R = 4.5 * s + 1.5
    yc = R + 0.5
    zellen = form(w, lambda X, Y, Z: (X ** 2 + ((Y - yc) / 0.95) ** 2 + Z ** 2 <= R * R) | (
        (X ** 2 + Z ** 2 <= (R * 0.45) ** 2) & (Y > yc) & (Y < yc + R * 1.25)),
                  (-int(R) - 1, 1, -int(R) - 1), (int(R) + 1, int(yc + R * 1.3) + 1, int(R) + 1),
                  lambda x, y, z: w.b("brown_concrete" if y < yc + R * 0.5 else "brown_terracotta" if (x + z) % 2 else
                                      "light_gray_terracotta"))
    fenster_rund(w, zellen, int(4 * s), 3, int(yc + 1))
    tuer_rein(w, 0, 1, vorne(zellen, R), "south")
    for k in range(3):
        x, z = round(-R - 3 + k * 3), round(R + 3)
        w.setze(x, 1, z, w.b("mushroom_stem", up=False, down=False, north=True, south=True, east=True, west=True))
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                w.setze(x + dx, 2, z + dz, w.b("red_mushroom_block", up=True, down=False, north=True, south=True,
                                               east=True, west=True))
    for k in range(4):
        x = round(R + 2 + k * 1.5)
        for y in range(1, 5 + k % 2):
            w.setze(x, y, -2 + k, w.b("lime_terracotta"))
        w.setze(x, 5 + k % 2, -2 + k, w.b("orange_stained_glass"))
    return w


def kleeblattmuehle(seed, g=1):
    """Kleeblatt-Windmühle: ein kleiner Holzturm, dessen Mühlenflügel aus vier grünen Kleeblättern bestehen,
    daneben Säcke aus Blütenstaub und ein Gärtchen mit Klee."""
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 3, seed=seed)
    H = int(7 * s + 4)
    r = int(1.5 * s + 1.5)
    haeuschen_rund(w, 0, 0, 1, r, H, M(w, [("spruce_planks", 2), ("birch_planks", 1)]),
                   Dachmat(w, ["mcw:red_terracotta", "brick"]))
    hz = r + 2
    yh = H - 1
    w.setze(0, yh, r + 1, w.b("dark_oak_log", axis="z"))
    for k in range(4):
        a = k * 1.571 + 0.4
        cx, cy = math.cos(a) * 3 * s + math.cos(a), yh + math.sin(a) * 3 * s + math.sin(a)
        for dx in range(-int(2 * s) - 1, int(2 * s) + 2):
            for dy in range(-int(2 * s) - 1, int(2 * s) + 2):
                for (ox, oy) in ((0.6, 0.6), (-0.6, 0.6), (0.6, -0.6), (-0.6, -0.6)):
                    if math.hypot(dx - ox * s, dy - oy * s) <= 1.2 * s:
                        w.setze(round(cx + dx), round(cy + dy), hz, w.b("green_concrete" if (dx + dy) % 3 else
                                                                        "lime_concrete"), False)
        for i in range(int(3 * s) + 1):
            w.setze(round(math.cos(a) * i), round(yh + math.sin(a) * i), hz, w.b("lime_terracotta"), False)
    for k in range(3):
        w.setze(r + 2, 1, -2 + k, w.b("white_wool"))
        w.setze(r + 2, 2, -2 + k, w.b("yellow_wool")) if k == 1 else None
    return w


def mohnpavillon(seed, g=1):
    """Mohnblüten-Pavillon: eine riesige rote Mohnblüte auf hohem Stängel überdacht einen runden Tanzboden aus
    Birkenholz, Laternen hängen an Spinnfäden, Bänke aus Rindenstücken."""
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 3, seed=seed)
    H = 10 * s + 4
    top = stiel(w, 0, 0, H, 0.8 * s + 0.4)
    R = 6 * s + 2
    bluete(w, top[0], top[1], top[2], R, "red_concrete", "black_concrete", n=4, schale=0.5)
    for x in range(-int(R * 0.8), int(R * 0.8) + 1):
        for z in range(-int(R * 0.8), int(R * 0.8) + 1):
            if math.hypot(x, z) <= R * 0.8:
                w.setze(x, 1, z, w.b("birch_planks") if math.hypot(x, z) > 1.2 else w.b("lime_terracotta"))
    for k in range(6):
        a = k / 6 * 6.283
        x, z = round(math.cos(a) * R * 0.7), round(math.sin(a) * R * 0.7)
        for y in range(2, int(H) - 1):
            w.setze(x, y, z, w.b("white_stained_glass_pane", north=False, south=False, east=False, west=False,
                                 waterlogged=False)) if y > int(H) - 4 else None
        w.setze(x, int(H) - 4, z, w.b("lantern", hanging=True, waterlogged=False))
    return w


def spinnennetzbruecke(seed, g=1):
    """Spinnennetz-Brücke: zwischen zwei hohen Grashalmbüscheln spannt sich ein riesiges Spinnennetz voller
    glitzernder Tautropfen, darüber führt ein Steg aus Zweigen mit Blüten-Geländer."""
    w = _neu(seed)
    s = S[g]
    garten(w, 12 * s + 3, "east", seed=seed)
    D = int(8 * s + 4)
    H = int(10 * s + 4)
    for sx in (-1, 1):
        for k in range(5):
            a = k / 5 * 6.283
            stiel(w, sx * D + round(math.cos(a) * 1.5), round(math.sin(a) * 1.5), H + k % 2 * 2, 0.5 * s + 0.3,
                  "green_terracotta", neig=(sx * 1.5 * math.cos(a), math.sin(a) * 1.5))
    yc = H * 0.55
    R = D - 1
    for k in range(12):
        a = k / 12 * 6.283
        for i in range(int(R * 3)):
            t = i / (R * 3)
            w.setze(round(math.cos(a) * R * t), round(yc + math.sin(a) * R * t * 0.8), 0, w.b("cobweb"), False)
    for ring in range(1, int(R), 2):
        for k in range(int(ring * 8)):
            a = k / (ring * 8) * 6.283
            x, y = round(math.cos(a) * ring), round(yc + math.sin(a) * ring * 0.8)
            w.setze(x, y, 0, w.b("light_blue_stained_glass") if (k % 7 == 0) else w.b("cobweb"), False)
    for x in range(-D, D + 1):
        w.setze(x, H - 1, 1, w.b("dark_oak_fence", east=True, west=True, north=False, south=False,
                                 waterlogged=False))
        w.setze(x, H - 2, 1, w.b("oak_planks"))
    return w


def marienkaeferkutsche(seed, g=1):
    """Marienkäfer-Kutsche: eine Kutsche in Form eines großen Marienkäfers mit roten, schwarz gepunkteten
    Flügeldecken als Dach, Rädern aus Löwenzahnblüten und einem Kutschbock mit Laterne."""
    from skulptur import Skulptur, ell, kap
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 3, "east", seed=seed)
    Sk = Skulptur(w, s)
    Sk.mat("r", lambda x, y, z, lx, ly, lz: w.b("black_concrete") if ((lx * 1.7) % 3 < 0.9 and (lz * 1.7) % 3 < 0.9)
           else w.b("red_concrete"))
    Sk.mat("d", w.b("black_concrete"))
    Sk.mat("w", w.b("white_concrete"))
    Sk.mat("y", w.b("yellow_concrete"))
    Sk.plus(ell(0, 5, 0, 5.0, 3.6, 3.8), "r")
    Sk.plus(lambda X, Y, Z: (np.abs(Z) < 0.35) & (Y > 4) & (X < 4.8) & (X > -4.8) & (
        (X / 5.0) ** 2 + ((Y - 5) / 3.6) ** 2 < 1.05), "d")
    Sk.plus(ell(5.2, 4.2, 0, 1.6, 1.4, 1.8), "d")
    Sk.plus(ell(6.0, 4.6, 0.9, 0.4, 0.4, 0.3), "w")
    Sk.plus(ell(6.0, 4.6, -0.9, 0.4, 0.4, 0.3), "w")
    for sx in (-3.0, 3.0):
        for sz in (-3.6, 3.6):
            Sk.plus(lambda X, Y, Z, sx=sx, sz=sz: (np.hypot(X - sx, Y - 1.6) < 1.6) & (np.abs(Z - sz) < 0.4), "y")
    Sk.plus(lambda X, Y, Z: (Y > 2.5) & (Y < 5.5) & (np.abs(Z) < 3.0) & (np.abs(X) < 2.0), None)
    Sk.rendern((-6, 0, -5), (8, 10, 5), versatz=(0.5, 1, 0.5))
    laterne(w, round(7 * s), round(7 * s), 0, 1)
    return w


def gluehwuermchenturm(seed, g=1):
    """Glühwürmchen-Leuchtturm: ein schlanker Turm aus Schilfrohr und Rinde, oben in einem Glaskäfig schwirren
    leuchtende Glühwürmchen, die den Weg über den Teich weisen."""
    w = _neu(seed)
    s = S[g]
    zl = garten(w, 10 * s + 3, seed=seed)
    for (x, z) in zl:
        if math.hypot(x - 4 * s, z - 3 * s) < 4 * s + 1:
            w.setze(x, 0, z, w.b("water", level=0))
            w.bloecke.pop((x, 1, z), None)
    H = int(10 * s + 5)
    r = int(1.2 * s + 1)
    for y in range(1, H):
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                if abs(x) == r or abs(z) == r:
                    w.setze(x, y, z, w.b("bamboo_block", axis="y") if (x + z) % 2 else w.b("spruce_wood", axis="y"))
    for x in range(-r - 1, r + 2):
        for z in range(-r - 1, r + 2):
            w.setze(x, H, z, w.b("spruce_planks"))
            for y in range(H + 1, H + 3):
                if abs(x) == r + 1 or abs(z) == r + 1:
                    w.setze(x, y, z, w.b("glass"))
                elif w.rng.random() < 0.3:
                    w.setze(x, y, z, w.b("ochre_froglight", axis="y"))
    kegeldach(w, 0, 0, H + 3, r + 1, Dachmat(w, ["mcw:green_terracotta", "jungle", "spruce"]), form="nadel")
    tuer(w, 0, 1, r, "south", holz="spruce", laternen=False)
    return w


def fingerhutbrunnen(seed, g=1):
    """Fingerhut-Brunnen: ein umgedrehter, zum Becken umgebauter Fingerhut voller Wasser, gespeist von einem
    Tautropfen-Röhrchen aus einem Blatt, ringsum Moospolster und Glockenblumen."""
    w = _neu(seed)
    s = S[g]
    garten(w, 8 * s + 3, seed=seed)
    R = 3 * s + 1.5
    for y in range(1, int(2.5 * s) + 3):
        for x in range(-int(R) - 1, int(R) + 2):
            for z in range(-int(R) - 1, int(R) + 2):
                d = math.hypot(x, z)
                if d <= R + 0.3:
                    w.setze(x, y, z, w.b("iron_block" if (x + y + z) % 3 else "light_gray_concrete") if d > R - 0.8
                            else w.b("water", level=0) if y > 1 else w.b("iron_block"))
    H = 8 * s + 3
    top = stiel(w, R + 3, 0, H, 0.5 * s + 0.3, neig=(-2 * s, 0))
    blatt(w, top[0], top[1], top[2], 4 * s + 2, 1.5 * s + 0.5, math.pi, neig=-0.3)
    for y in range(int(2.5 * s) + 3, int(H) - 1):
        w.setze(round(top[0] - 4 * s), y, 0, w.b("water", level=0), False)
    return w


def blaetterboothafen(seed, g=1):
    """Blätterboot-Hafen: in einer großen Pfütze schaukeln Boote aus gefalteten Blättern mit Zweigmasten und
    Blütenblatt-Segeln an einem Steg aus Zweigen, ein Hafenmeisterhaus aus Rinde."""
    w = _neu(seed)
    s = S[g]
    zl = garten(w, 12 * s + 3, seed=seed)
    for (x, z) in zl:
        if math.hypot(x, z + 2 * s) < 8 * s + 2:
            w.setze(x, 0, z, w.b("water", level=0))
            w.bloecke.pop((x, 1, z), None)
    rng = w.rng
    for k in range(3 + g):
        a = k / (3 + g) * 6.283
        cx, cz = round(math.cos(a) * 5 * s), round(-2 * s + math.sin(a) * 5 * s)
        L = 3 * s + 1.5
        for i in range(-int(L), int(L) + 1):
            b = math.sqrt(max(0, 1 - (i / L) ** 2)) * 1.4 * s
            for q in range(-int(b), int(b) + 1):
                y = 1 if abs(q) >= int(b) - 0 or abs(i) >= int(L) - 1 else 0
                w.setze(cx + i, 1 + (1 if abs(q) == int(b) and b >= 1 else 0), cz + q,
                        w.b("lime_terracotta" if abs(q) == int(b) else "green_terracotta"), False)
        for y in range(2, int(4 * s) + 3):
            w.setze(cx, y, cz, w.b("spruce_fence", north=False, south=False, east=False, west=False,
                                   waterlogged=False))
        for y in range(3, int(4 * s) + 2):
            for i in range(1, int(2 * s) + 1 - (y - 3) // 2):
                w.setze(cx + i, y, cz, w.b(["pink_wool", "white_wool", "yellow_wool"][k % 3]), False)
    for z in range(int(6 * s) + 2, int(10 * s) + 3):
        w.setze(0, 1, z, w.b("spruce_planks"), True)
    from fantasie2 import ring_wand
    ring_wand(w, 0, int(11 * s) + 3, 2, 1, 4, lambda *a: w.b("spruce_wood", axis="y"))
    kegeldach(w, 0, int(11 * s) + 3, 5, 2, Dachmat(w, ["mcw:green_terracotta", "jungle"]), form="glocke")
    return w


def pilzringmarkt(seed, g=1):
    """Pilzring-Markt: in einem Hexenring aus Pilzen stehen Marktstände auf Pilzhüten mit Waren in Eichelkappen,
    Bannern aus Blütenblättern und Lampions."""
    w = _neu(seed)
    s = S[g]
    garten(w, 11 * s + 3, seed=seed)
    R = 7 * s + 3
    n = 8 + g * 2
    for k in range(n):
        a = k / n * 6.283
        x, z = round(math.cos(a) * R), round(math.sin(a) * R)
        h = int(2 + (k % 3) * s)
        for y in range(1, h + 1):
            w.setze(x, y, z, w.b("mushroom_stem", up=False, down=False, north=True, south=True, east=True,
                                 west=True))
        r = 1 + int(s * (1 + k % 2))
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if math.hypot(dx, dz) <= r + 0.3:
                    w.setze(x + dx, h + 1, z + dz, w.b("red_mushroom_block" if k % 2 else "brown_mushroom_block",
                                                       up=True, down=False, north=True, south=True, east=True,
                                                       west=True))
        if k % 2 == 0:
            w.setze(x, h + 2, z, w.b(["melon", "pumpkin", "hay_block", "barrel"][k % 4],
                                     **({"axis": "y"} if k % 4 == 2 else {"facing": "up", "open": False} if k % 4 == 3
                                        else {})))
    for k in range(4):
        a = k * 1.571 + 0.785
        x, z = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        for y in range(1, 5):
            w.setze(x, y, z, w.b("lime_terracotta"))
        w.setze(x, 5, z, w.b(["pink_stained_glass", "orange_stained_glass", "yellow_stained_glass",
                              "magenta_stained_glass"][k]))
    return w


def wurzelhoehle(seed, g=1):
    """Wurzelhöhle: unter den mächtigen Wurzeln eines alten Baums liegt eine gemütliche Höhlenwohnung mit runder
    Tür, Fenstern zwischen den Wurzeln, Wäscheleine und Gemüsegarten."""
    import wald2
    from lib import einfuegen
    w = _neu(seed)
    s = S[g]
    garten(w, 11 * s + 3, seed=seed)
    R = 5 * s + 2
    for x in range(-int(R) - 2, int(R) + 3):
        for z in range(-int(R) - 2, int(R) + 3):
            d = math.hypot(x, z)
            if d <= R + 2:
                h = int((R * 0.7) * math.sqrt(max(0, 1 - (d / (R + 2)) ** 2)))
                for y in range(1, h + 1):
                    w.setze(x, y, z, w.b("dirt" if y < h else "grass_block", **({} if y < h else {"snowy": False})))
    einfuegen(w, wald2.laubbaum(seed, "oak", H=int(10 * s + 6), dick=True), 0, int(R * 0.7), 0)
    for k in range(6):
        a = k / 6 * 6.283
        pts = bez((0, R * 0.6, 0), (math.cos(a) * R * 0.8, R * 0.7, math.sin(a) * R * 0.8),
                  (math.cos(a) * (R + 2), 0, math.sin(a) * (R + 2)))
        rohr(w, pts, 0.9 * s + 0.4, 0.5, w.b("oak_wood", axis="y"))
    zd = int(R) + 1
    for y in range(1, 3):
        for z in range(zd - 3, zd + 1):
            w.bloecke.pop((0, y, z), None)
    tuer(w, 0, 1, zd, "south", holz="oak", laternen=True)
    fenster(w, -2, 2, zd - 1, "south")
    fenster(w, 2, 2, zd - 1, "south")
    for x in range(-int(R) - 4, -int(R)):
        for z in range(2, 5):
            w.setze(x, 0, z, w.b("farmland", moisture=7))
            w.setze(x, 1, z, w.b("carrots", age=7) if z % 2 else w.b("beetroots", age=3))
    return w


def schneegloeckchenkapelle(seed, g=1):
    """Schneeglöckchen-Kapelle: eine kleine weiße Kapelle unter drei riesigen, nickenden Schneeglöckchen, deren
    Blüten wie Glocken über dem Dach hängen, Eiskristalle am Weg."""
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 3, seed=seed)
    B, T = int(2 * s + 2), int(3 * s + 2)
    from feinbau import mauer
    mauer(w, -B, -T, B, T, 1, int(3 * s) + 3, M(w, [("calcite", 2), ("white_concrete", 1)]))
    satteldach(w, -B, -T, B, T, int(3 * s) + 4, Dachmat(w, ["mcw:light_blue_terracotta", "birch"]), first_x=False,
               ue=1, traufe="birch", steil=2)
    tuer(w, 0, 1, T, "south", holz="birch", laternen=False)
    for k in range(3):
        a = k * 2.094 + 0.5
        x0, z0 = round(math.cos(a) * (B + 3)), round(math.sin(a) * (T + 3))
        H = (12 + k * 2) * s
        top = stiel(w, x0, z0, H, 0.5 * s + 0.3, "green_terracotta", neig=(-math.cos(a) * 3 * s, -math.sin(a) * 3 * s))
        xb, yb, zb = top[0] - math.cos(a) * 1.5 * s, top[1] - 2 * s, top[2] - math.sin(a) * 1.5 * s
        for y in range(int(-2.5 * s), 1):
            r = 1.6 * s * math.sqrt(max(0, 1 - (y / (2.6 * s)) ** 2)) + 0.4
            for dx in range(-int(r) - 1, int(r) + 2):
                for dz in range(-int(r) - 1, int(r) + 2):
                    if r - 1 < math.hypot(dx, dz) <= r:
                        w.setze(round(xb + dx), round(yb + y), round(zb + dz), w.b("white_concrete"), False)
        w.setze(round(xb), round(yb + 1), round(zb), w.b("lime_concrete"), False)
    return w


def apfelhaus(seed, g=1):
    """Apfelhaus: ein großer, rotbackiger Apfel mit Stiel und Blatt, in den eine runde Tür und Fenster geschnitten
    sind, ein Wurm schaut aus einem Loch, Leiter zum Dachfenster."""
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 3, seed=seed)
    R = 5 * s + 1.5
    yc = R + 0.5

    def apfel(X, Y, Z):
        r = np.sqrt(X ** 2 + Z ** 2)
        dip = 0.35 * R * np.exp(-(r / (R * 0.35)) ** 2)
        return (X ** 2 + ((Y - yc) / 0.92) ** 2 + Z ** 2 <= R * R) & (Y < yc + R * 0.92 - dip) & (
            Y > yc - R * 0.92 + dip * 0.6)
    zellen = form(w, apfel, (-int(R) - 1, 1, -int(R) - 1), (int(R) + 1, int(yc + R) + 1, int(R) + 1),
                  lambda x, y, z: w.b("red_concrete" if (x + z) % 5 else "red_terracotta" if y > yc else
                                      "yellow_terracotta" if (x * z) % 7 == 0 else "red_concrete"))
    ytop = max(y for (x, y, z) in zellen if abs(x) <= 1 and abs(z) <= 1)
    for y in range(ytop, ytop + int(2 * s) + 2):
        w.setze(0, y, 0, w.b("dark_oak_log", axis="y"))
    blatt(w, 0, ytop + int(2 * s) + 1, 0, 3 * s + 1, 1.2 * s + 0.5, 0.6, neig=0.1)
    fenster_rund(w, zellen, int(4 * s), 3, int(yc + 1))
    tuer_rein(w, 0, 1, vorne(zellen, R), "south")
    x, y = int(R) , int(yc)
    w.setze(x + 1, y, 0, w.b("pink_terracotta"))
    w.setze(x + 2, y + 1, 0, w.b("pink_terracotta"))
    return w


def vogelnestdorf(seed, g=2):
    """Vogelnest-Dorf: in einem riesigen, aus Zweigen geflochtenen Nest stehen kleine Häuschen in Form von
    hellblauen und gesprenkelten Eiern, verbunden durch Stege, eine Feder als Fahne."""
    w = _neu(seed)
    s = S[g]
    garten(w, 10 * s + 4, seed=seed)
    R = 7 * s + 3
    rng = w.rng
    for k in range(int(R * 20)):
        a = rng.random() * 6.283
        r = R * (0.75 + rng.random() * 0.3)
        y = 1 + rng.random() * 3 * s
        x, z = math.cos(a) * r, math.sin(a) * r
        for i in range(3):
            w.setze(round(x + math.cos(a + 1.6) * i), round(y), round(z + math.sin(a + 1.6) * i),
                    w.b("spruce_log" if rng.random() < 0.5 else "dark_oak_log", axis="y"))
    for x in range(-int(R), int(R) + 1):
        for z in range(-int(R), int(R) + 1):
            if math.hypot(x, z) < R * 0.8:
                w.setze(x, 1, z, w.b("hay_block", axis="y") if rng.random() < 0.5 else w.b("brown_wool"))
    for k in range(3 + g):
        a = k / (3 + g) * 6.283
        cx, cz = round(math.cos(a) * R * 0.4), round(math.sin(a) * R * 0.4)
        r = 1.6 * s + 0.8
        f = ["light_blue_concrete", "white_concrete", "cyan_terracotta"][k % 3]
        zellen = form(w, lambda X, Y, Z, cx=cx, cz=cz, r=r: (X - cx) ** 2 + ((Y - 2 - r * 1.25) / 1.3) ** 2 +
                      (Z - cz) ** 2 <= r * r, (cx - int(r) - 1, 2, cz - int(r) - 1),
                      (cx + int(r) + 1, int(2 + r * 2.6) + 1, cz + int(r) + 1),
                      lambda x, y, z, f=f: w.b("brown_terracotta" if (x * 5 + y * 3 + z) % 9 == 0 else f))
        fenster_rund(w, zellen, 2, 3, int(2 + r * 2), licht=False)
    for y in range(2, int(8 * s) + 4):
        w.setze(int(R * 0.9), y, 0, w.b("white_concrete") if y > int(4 * s) else w.b("white_concrete"))
        if y > int(4 * s):
            w.setze(int(R * 0.9) + 1, y, 0, w.b("white_wool"))
    return w


def rosenpalast(seed, g=2):
    """Rosenpalast: im Kelch einer gewaltigen, halb geöffneten roten Rose steht ein kleiner weißer Feenpalast mit
    Türmchen, große Dornenranken bilden eine Treppe hinauf."""
    w = _neu(seed)
    s = S[g]
    garten(w, 11 * s + 4, seed=seed)
    H = 6 * s + 3
    stiel(w, 0, 0, H, 1.2 * s + 0.5, "green_concrete")
    R = 6 * s + 2
    for ring in range(3):
        n = 5 + ring
        for k in range(n):
            a = k / n * 6.283 + ring * 0.6
            rr = R * (0.45 + 0.28 * ring)
            for i in range(int(rr * 2.5)):
                t = i / (rr * 2.5)
                for q in np.arange(-math.sin(math.pi * t) * 2.2 * s, math.sin(math.pi * t) * 2.2 * s + 0.01, 0.5):
                    x = math.cos(a) * rr * (0.4 + 0.6 * t) - math.sin(a) * q
                    z = math.sin(a) * rr * (0.4 + 0.6 * t) + math.cos(a) * q
                    y = H + 1 + t * (2.5 + ring * 1.5) * s
                    w.setze(round(x), round(y), round(z), w.b("red_concrete" if ring < 2 else "red_terracotta"), False)
    for x in range(-int(R * 0.4), int(R * 0.4) + 1):
        for z in range(-int(R * 0.4), int(R * 0.4) + 1):
            if math.hypot(x, z) <= R * 0.4:
                w.setze(x, int(H) + 1, z, w.b("yellow_concrete"))
    y0 = int(H) + 2
    for (x, z) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        for y in range(y0, y0 + int(3 * s) + 3):
            w.setze(x, y, z, w.b("white_concrete"))
        kegeldach(w, x, z, y0 + int(3 * s) + 3, 0, Dachmat(w, ["mcw:pink_terracotta", "cherry"]), form="nadel",
                  ue=0.8)
    from feinbau import mauer
    mauer(w, -1, -1, 1, 1, y0, y0 + int(2 * s) + 2, M(w, [("white_concrete", 1)]))
    kegeldach(w, 0, 0, y0 + int(2 * s) + 3, 1, Dachmat(w, ["mcw:pink_terracotta", "cherry"]), form="glocke")
    return w


def seifenblasenschloss(seed, g=2):
    """Seifenblasen-Schloss: ein Schloss aus schillernden Glaskugeln verschiedener Größe, die aneinanderkleben und
    übereinander schweben, verbunden durch Röhren, im Inneren Möbel aus Blüten."""
    w = _neu(seed)
    s = S[g]
    garten(w, 10 * s + 4, seed=seed)
    farben = ["light_blue_stained_glass", "pink_stained_glass", "magenta_stained_glass", "cyan_stained_glass",
              "white_stained_glass", "purple_stained_glass"]
    rng = w.rng
    blasen = [(0, 4 * s + 2, 0, 4 * s + 1.5)]
    for k in range(5 + g * 2):
        bx, by, bz, br = blasen[int(rng.random() * len(blasen))]
        a = rng.random() * 6.283
        b = rng.random() * 1.2 - 0.2
        r = br * (0.45 + rng.random() * 0.3)
        d = br + r * 0.7
        blasen.append((bx + math.cos(a) * math.cos(b) * d, max(r + 1, by + math.sin(b) * d),
                       bz + math.sin(a) * math.cos(b) * d, r))
    for k, (x, y, z, r) in enumerate(blasen):
        kugel(w, x, y, z, r, lambda *a, k=k: w.b(farben[(k + a[0] + a[1]) % len(farben)] if (a[0] + a[2]) % 4 else
                                                farben[k % len(farben)]), hohl=True)
        w.setze(round(x), round(y - r) + 1, round(z), w.b("pink_wool"))
    return w


def mondblumengarten(seed, g=1):
    """Mondblumen-Garten: ein nächtlicher Garten mit großen weißen Mondblumen, deren Kelche sanft leuchten, ein
    Sternenpfad aus Leuchtsteinen und ein Mondtor aus Birkenzweigen."""
    w = _neu(seed)
    s = S[g]
    zl = garten(w, 11 * s + 3, seed=seed)
    rng = w.rng
    for k in range(4 + g * 2):
        a = rng.random() * 6.283
        d = 3 + rng.random() * 7 * s
        x, z = math.cos(a) * d, math.sin(a) * d
        H = (4 + rng.random() * 4) * s + 2
        top = stiel(w, round(x), round(z), H, 0.4 * s + 0.3, "green_terracotta")
        bluete(w, top[0], top[1], top[2], 2.5 * s + 1, "white_concrete", "pearlescent_froglight", n=5, schale=0.6)
    for i in range(int(10 * s) + 4):
        w.setze(0, 0, int(11 * s + 3) - i, w.b("sea_lantern") if i % 2 else w.b("smooth_quartz"))
    R = 3 * s + 2
    for k in range(int(R * 8)):
        a = k / (R * 8) * 6.283
        x, y = round(math.cos(a) * R), round(R + 1 + math.sin(a) * R)
        if y >= 1:
            w.setze(x, y, int(8 * s), w.b("birch_wood", axis="y"))
    return w


def grashalmschaukeln(seed, g=1):
    """Grashalm-Schaukeln: zwischen hohen, gebogenen Grashalmen hängen Schaukeln aus Blättern an Spinnenseide, ein
    Rutschbahn-Blatt führt hinab, Gänseblümchen als Sitzkissen."""
    w = _neu(seed)
    s = S[g]
    garten(w, 10 * s + 3, seed=seed)
    rng = w.rng
    for k in range(3 + g):
        x0 = round((k - (2 + g) / 2) * 5 * s)
        H = (10 + rng.random() * 4) * s + 3
        top = stiel(w, x0, -2, H, 0.6 * s + 0.3, "lime_terracotta", neig=(2 * s, 3 * s))
        yt = int(top[1]) - 1
        for y in range(3, yt):
            w.setze(round(top[0]) - 1, y, round(top[2]), w.b("white_stained_glass_pane", north=False, south=False,
                                                                east=False, west=False, waterlogged=False))
            w.setze(round(top[0]) + 1, y, round(top[2]), w.b("white_stained_glass_pane", north=False, south=False,
                                                                east=False, west=False, waterlogged=False))
        for dx in range(-1, 2):
            w.setze(round(top[0]) + dx, 2, round(top[2]), w.b("green_terracotta"))
    blatt(w, -6 * s, 6 * s, 4 * s, 7 * s + 2, 1.5 * s, -0.8, neig=-0.8)
    for k in range(5):
        w.setze(round((rng.random() - 0.5) * 12 * s), 1, round((rng.random() - 0.5) * 12 * s), w.b("oxeye_daisy"))
    return w


def tannenzapfenturm(seed, g=2):
    """Tannenzapfen-Turm: ein großer, aufrecht stehender Tannenzapfen, dessen Schuppen wie Dachziegel übereinander
    liegen, mit Fenstern zwischen den Schuppen und einem Balkon aus Rinde."""
    w = _neu(seed)
    s = S[g]
    garten(w, 9 * s + 3, seed=seed)
    H = 14 * s + 5
    R = 4 * s + 1.5
    rng = w.rng

    def zapfen(X, Y, Z):
        t = np.clip((Y - 1) / H, 0, 1)
        r = R * np.sin(np.pi * np.clip(t * 0.9 + 0.1, 0, 1)) ** 0.7
        return (np.hypot(X, Z) <= r) & (Y >= 1) & (Y <= H)
    zellen = form(w, zapfen, (-int(R) - 1, 1, -int(R) - 1), (int(R) + 1, int(H), int(R) + 1),
                  lambda x, y, z: w.b("brown_terracotta" if (y + int(math.atan2(z, x) * 3)) % 3 else "spruce_planks"))
    for (x, y, z) in zellen:
        if y % 3 == 0 and rng.random() < 0.35:
            a = math.atan2(z, x)
            p = (x + round(math.cos(a)), y, z + round(math.sin(a)))
            if w.frei(*p):
                f = "south" if abs(math.sin(a)) > abs(math.cos(a)) and math.sin(a) > 0 else "north" if abs(
                    math.sin(a)) > abs(math.cos(a)) else "east" if math.cos(a) > 0 else "west"
                w.setze(*p, treppe(w, "spruce", {"south": "north", "north": "south", "east": "west",
                                                 "west": "east"}[f], "top"), False)
    fenster_rund(w, zellen, int(5 * s), 3, int(H - 3))
    tuer_rein(w, 0, 1, vorne(zellen, R), "south")
    return w


FEEN3 = {
    "fingerhuttuerme": ("Fingerhut-Türme", fingerhuttuerme),
    "erdbeerhaus": ("Erdbeerhaus", erdbeerhaus),
    "haselnussschaenke": ("Haselnuss-Schänke", haselnussschaenke),
    "kleeblattmuehle": ("Kleeblatt-Windmühle", kleeblattmuehle),
    "mohnpavillon": ("Mohnblüten-Pavillon", mohnpavillon),
    "spinnennetzbruecke": ("Spinnennetz-Brücke", spinnennetzbruecke),
    "marienkaeferkutsche": ("Marienkäfer-Kutsche", marienkaeferkutsche),
    "gluehwuermchenturm": ("Glühwürmchen-Leuchtturm", gluehwuermchenturm),
    "fingerhutbrunnen": ("Fingerhut-Brunnen", fingerhutbrunnen),
    "blaetterboothafen": ("Blätterboot-Hafen", blaetterboothafen),
    "pilzringmarkt": ("Pilzring-Markt", pilzringmarkt),
    "wurzelhoehle": ("Wurzelhöhle", wurzelhoehle),
    "schneegloeckchenkapelle": ("Schneeglöckchen-Kapelle", schneegloeckchenkapelle),
    "apfelhaus": ("Apfelhaus", apfelhaus),
    "vogelnestdorf": ("Vogelnest-Dorf", vogelnestdorf),
    "rosenpalast": ("Rosenpalast", rosenpalast),
    "seifenblasenschloss": ("Seifenblasen-Schloss", seifenblasenschloss),
    "mondblumengarten": ("Mondblumen-Garten", mondblumengarten),
    "grashalmschaukeln": ("Grashalm-Schaukeln", grashalmschaukeln),
    "tannenzapfenturm": ("Tannenzapfen-Turm", tannenzapfenturm),
}

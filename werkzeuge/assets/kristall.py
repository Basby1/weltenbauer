"""Kristallhöhlen – Geoden, Riesenkristall-Grotten, Edelsteinhöhlen (Amethyst, Smaragd, Rubin, Saphir, Eis),
Kristallminen, Brücken, Bäume, Thron, Golem und Felder aus Kristallnadeln. Höhlen sind zur Vorschauseite hin
offen (Schnittansicht). Boden y = 0."""

from __future__ import annotations

import math

import numpy as np

import pracht as P
from flora import _neu, _r, _stil, linie
from lib import Rauschen

U = [0.6, 1.0, 1.7, 2.8]

EDEL = {
    "amethyst": ["amethyst_block", "purple_stained_glass", "magenta_stained_glass", "amethyst_block"],
    "smaragd": ["emerald_block", "lime_stained_glass", "green_stained_glass", "emerald_block"],
    "rubin": ["red_stained_glass", "redstone_block", "red_stained_glass", "pink_stained_glass"],
    "saphir": ["blue_stained_glass", "lapis_block", "light_blue_stained_glass", "blue_stained_glass"],
    "eis": ["packed_ice", "blue_ice", "light_blue_stained_glass", "white_stained_glass"],
    "quarz": ["quartz_block", "white_stained_glass", "smooth_quartz", "calcite"],
    "feuer": ["orange_stained_glass", "shroomlight", "yellow_stained_glass", "orange_stained_glass"],
    "obsidian": ["obsidian", "crying_obsidian", "purple_stained_glass", "obsidian"],
    "regenbogen": ["red_stained_glass", "orange_stained_glass", "yellow_stained_glass", "lime_stained_glass",
                   "light_blue_stained_glass", "purple_stained_glass"],
}
GESTEIN = ["stone", "deepslate", "tuff", "andesite", "cobbled_deepslate", "smooth_basalt"]


def _n(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v) + 1e-9)


# ============================================================================ Bausteine

def kristall(w, basis, richtung, L, r, art="amethyst", spitze=0.35, kern=None, ueber=True):
    """Sechseckiges Kristallprisma von basis in richtung, Länge L, Radius r, mit Spitze."""
    d = _n(richtung)
    a = np.array([0, 1, 0]) if abs(d[1]) < 0.9 else np.array([1, 0, 0])
    e1 = _n(np.cross(d, a))
    e2 = np.cross(d, e1)
    mats = EDEL[art]
    ids = [w.b(m) for m in mats]
    kid = (w.b(kern) if isinstance(kern, str) else kern) if kern else None
    b = np.asarray(basis, float)
    e = b + d * L
    lo = np.floor(np.minimum(b, e) - r - 1).astype(int)
    hi = np.ceil(np.maximum(b, e) + r + 1).astype(int)
    X, Y, Z = np.mgrid[lo[0]:hi[0] + 1, lo[1]:hi[1] + 1, lo[2]:hi[2] + 1]
    px, py, pz = X - b[0], Y - b[1], Z - b[2]
    t = px * d[0] + py * d[1] + pz * d[2]
    qx, qy, qz = px - d[0] * t, py - d[1] * t, pz - d[2] * t
    uu = qx * e1[0] + qy * e1[1] + qz * e1[2]
    vv = qx * e2[0] + qy * e2[1] + qz * e2[2]
    ang = np.arctan2(vv, uu)
    hexr = r * math.cos(math.pi / 6) / np.cos(np.mod(ang, math.pi / 3) - math.pi / 6)
    tt = t / L
    rr = hexr * np.where(tt < 1 - spitze, 1.0, (1 - tt) / spitze)
    rad = np.hypot(uu, vv)
    m = (t >= -0.5) & (t <= L) & (rad <= rr + 0.15)
    for (x, y, z), ti, ra, rri in zip(np.stack([X[m], Y[m], Z[m]], 1), tt[m], rad[m], rr[m]):
        if kid is not None and ra < rri * 0.4:
            blk = kid
        else:
            blk = ids[int((ti * 2 + (x + y + z) * 0.37) * 10) % len(ids)]
        w.setze(int(x), int(y), int(z), blk, ueber)


def buschel(w, c, n, L, r, art="amethyst", oben=True, streu=0.6):
    """Kristallbüschel: n Kristalle aus einem Punkt, nach oben (oder unten) gefächert."""
    rng = w.rng
    for k in range(n):
        a = rng.random() * 6.28
        neig = streu * (0.3 + 0.7 * rng.random())
        d = (math.cos(a) * neig, 1 if oben else -1, math.sin(a) * neig)
        kristall(w, c, d, L * (0.5 + 0.6 * rng.random()), r * (0.6 + 0.5 * rng.random()), art)


def hoehle(w, R, H, mat=None, offen=True, boden="stone", dicke=3, rn=None):
    """Kuppelförmige Höhle (Boden y = 0). offen: Viertel zur Vorschau-Seite (+x, +z) aufgeschnitten.
    Gibt Liste der Innenwand-Punkte (für Kristalle) zurück."""
    mat = mat or GESTEIN
    rn = rn or Rauschen(w, 4)
    rf = Rauschen(w, 1.3)
    innen = []
    for x in range(-int(R) - dicke - 1, int(R) + dicke + 2):
        for z in range(-int(R) - dicke - 1, int(R) + dicke + 2):
            for y in range(-1, int(H) + dicke + 2):
                d = math.sqrt((x / R) ** 2 + (z / R) ** 2 + (max(0, y) / H) ** 2) * (1 + 0.15 * (rn(x, y, z) - 0.5))
                if d > 1 + dicke / R:
                    continue
                if offen and x > -R * 0.15 and z > -R * 0.15 and y > 0:
                    if x + z > R * 0.2 - y * 0.15:
                        continue
                if y <= 0:
                    w.setze(x, y, z, w.b(boden if y == 0 and d < 1 else mat[int(rf(x, y, z) * (len(mat) - 0.01))]))
                    if y == 0 and d < 1:
                        innen.append((x, 0, z, "boden"))
                elif d >= 1:
                    w.setze(x, y, z, w.b(mat[int(rf(x, y, z) * (len(mat) - 0.01))]))
                    if d < 1 + 1.2 / R:
                        innen.append((x, y, z, "wand"))
    return innen


def auskleiden(w, innen, art, dichte=0.12, L=3.0, r=0.9, rng=None, nur=None):
    """Kristalle an Höhlenwänden und -boden, nach innen gerichtet."""
    rng = rng or w.rng
    for (x, y, z, typ) in innen:
        if nur and typ != nur:
            continue
        if rng.random() > dichte * (0.35 if typ == "boden" else 1.0):
            continue
        if typ == "boden":
            d = (rng.normal() * 0.3, 1, rng.normal() * 0.3)
        else:
            d = (-x, -y * 0.8 + 1, -z)
        kristall(w, (x, y, z), d, L * (0.5 + rng.random()), r * (0.6 + 0.6 * rng.random()), art, ueber=False)


def knospen(w, innen, dichte=0.15, art="amethyst"):
    rng = w.rng
    namen = ["small_amethyst_bud", "medium_amethyst_bud", "large_amethyst_bud", "amethyst_cluster"]
    for (x, y, z, typ) in innen:
        if typ == "boden" and rng.random() < dichte and w.frei(x, 1, z):
            if art == "amethyst":
                w.setze(x, 1, z, w.b(namen[int(rng.integers(4))], facing="up", waterlogged=False))
            else:
                w.setze(x, 1, z, w.b(EDEL[art][int(rng.integers(len(EDEL[art])))]))


def leuchten(w, innen, dichte=0.03, blk="glow_lichen"):
    rng = w.rng
    for (x, y, z, typ) in innen:
        if rng.random() < dichte:
            p = (x, y + 1, z) if typ == "boden" else (x - int(np.sign(x)), y, z - int(np.sign(z)))
            if w.frei(*p):
                if blk == "glow_lichen":
                    w.setze(*p, w.b("glow_lichen", down=typ == "boden", up=False, north=False, south=False,
                                    east=False, west=False, waterlogged=False))
                else:
                    w.setze(*p, w.b(blk))


# ============================================================================ Höhlen

def _edelhoehle(seed, g, art, H_f=1.0, dichte=0.12, extra=None):
    w = _neu(seed)
    u = U[g]
    R = _r(12 * u + 6)
    innen = hoehle(w, R, R * H_f)
    auskleiden(w, innen, art, dichte * 0.45, L=2.6 * u + 1.2, r=0.6 * u + 0.4)
    rng = w.rng
    for k in range(2 + g):
        a = rng.random() * 6.28
        d = R * 0.4 * rng.random()
        kristall(w, (math.cos(a) * d, 0, math.sin(a) * d), (rng.normal() * 0.25, 1, rng.normal() * 0.25),
                 (6 + 4 * rng.random()) * u + 2, (1.0 + 0.6 * rng.random()) * u + 0.6, art)
    leuchten(w, innen, 0.025)
    if extra:
        extra(w, u, R, innen)
    return w


def amethystgeode(seed, g=2):
    """Amethystgeode: eine aufgeschnittene Kugel mit Schichten aus glattem Basalt, Kalzit und Amethyst, innen
    funkelnde Knospen und Cluster – wie ein riesiger Edelstein im Fels."""
    w = _neu(seed)
    u = U[g]
    R = 9 * u + 4
    cy = R * 0.75
    rng = w.rng
    for x in range(-int(R) - 1, int(R) + 2):
        for y in range(-1, int(cy + R) + 2):
            for z in range(-int(R) - 1, int(R) + 2):
                d = math.sqrt(x * x + (y - cy) ** 2 + z * z)
                if d > R or (x > 0 and z > 0 and y > 1):
                    continue
                if d > R - 1:
                    blk = "smooth_basalt"
                elif d > R - 2:
                    blk = "calcite"
                elif d > R - 3.2:
                    blk = "amethyst_block" if rng.random() > 0.08 else "budding_amethyst"
                else:
                    if y >= 0 and y < 1 and d < R - 3.2:
                        w.setze(x, y, z, w.b("amethyst_block"))
                    continue
                w.setze(x, y, z, w.b(blk))
    for x in range(-int(R), int(R) + 1):
        for y in range(0, int(cy + R)):
            for z in range(-int(R), int(R) + 1):
                d = math.sqrt(x * x + (y - cy) ** 2 + z * z)
                if R - 4.2 < d <= R - 3.2 and rng.random() < 0.25 and w.frei(x, y, z):
                    nb = [(x + 1, y, z, "west"), (x - 1, y, z, "east"), (x, y + 1, z, "down"), (x, y - 1, z, "up"),
                          (x, y, z + 1, "north"), (x, y, z - 1, "south")]
                    for (a, b, c, f) in nb:
                        if not w.frei(a, b, c):
                            w.setze(x, y, z, w.b(["amethyst_cluster", "large_amethyst_bud", "medium_amethyst_bud"][
                                int(rng.integers(3))], facing=f, waterlogged=False))
                            break
    return w


def riesenkristallgrotte(seed, g=2):
    """Riesenkristallgrotte: mannshohe bis turmhohe, milchweiße Quarzkristalle kreuz und quer durch eine Höhle
    – wie die berühmte Kristallhöhle von Naica."""
    def extra(w, u, R, innen):
        rng = w.rng
        for k in range(int(4 + 3 * u)):
            a = rng.random() * 6.28
            p = (math.cos(a) * R * 0.7, rng.random() * R * 0.4, math.sin(a) * R * 0.7)
            d = (-p[0] + rng.normal() * 3, rng.normal() * 2, -p[2] + rng.normal() * 3)
            kristall(w, p, d, R * (0.9 + 0.5 * rng.random()), 1.2 * u + 0.6, "quarz", ueber=False)
    return _edelhoehle(seed, g, "quarz", dichte=0.06, extra=extra)


def eiskristallhoehle(seed, g=2):
    """Eiskristallhöhle: blau schimmernde Wände aus Gletschereis, Eiszapfen von der Decke, gefrorener See und
    Eiskristalle in Büscheln."""
    def extra(w, u, R, innen):
        rng = w.rng
        for (x, y, z, typ) in innen:
            if typ == "boden" and math.hypot(x, z) < R * 0.5:
                w.setze(x, 0, z, w.b("ice"))
            elif typ == "wand" and y > R * 0.5 and rng.random() < 0.08:
                for k in range(int(1 + rng.integers(int(2 + 2 * u)))):
                    p = (x - int(np.sign(x)), y - 1 - k, z - int(np.sign(z)))
                    if w.frei(*p):
                        w.setze(*p, w.b("pointed_dripstone", vertical_direction="down", thickness="tip",
                                        waterlogged=False) if False else w.b("packed_ice" if k == 0 else "ice"))
    w = _edelhoehle(seed, g, "eis", dichte=0.1, extra=extra)
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) in ("minecraft:deepslate", "minecraft:cobbled_deepslate", "minecraft:smooth_basalt"):
            w.bloecke[(x, y, z)] = w.b("packed_ice" if (x + y + z) % 3 else "snow_block")
    return w


def smaragdhoehle(seed, g=2):
    """Smaragdhöhle: tiefgrüne Kristalle in Moos und Gestein, Smaragdadern in den Wänden, grünes Leuchten über
    einem stillen Tümpel."""
    def extra(w, u, R, innen):
        rng = w.rng
        for (x, y, z, typ) in innen:
            if typ == "wand" and rng.random() < 0.05:
                w.setze(x, y, z, w.b("deepslate_emerald_ore" if y < R * 0.3 else "emerald_ore"))
            if typ == "boden" and math.hypot(x + R * 0.3, z + R * 0.3) < R * 0.25:
                w.setze(x, 0, z, w.b("water", level=0))
            elif typ == "boden" and rng.random() < 0.2:
                w.setze(x, 0, z, w.b("moss_block"))
    return _edelhoehle(seed, g, "smaragd", extra=extra)


def rubinhoehle(seed, g=2):
    """Rubinhöhle: blutrote Kristalle glühen im Schein von Redstone-Adern, rote Spiegel im dunklen Schiefer."""
    def extra(w, u, R, innen):
        rng = w.rng
        for (x, y, z, typ) in innen:
            if typ == "wand" and rng.random() < 0.06:
                w.setze(x, y, z, w.b("redstone_ore", lit=False) if rng.random() < 0.5 else w.b("redstone_block"))
    return _edelhoehle(seed, g, "rubin", extra=extra)


def saphirsee(seed, g=2):
    """Saphirsee: ein unterirdischer See, tiefblau beleuchtet von Saphirkristallen, die vom Seegrund und den
    Wänden wachsen, ein Steg führt zu einer Kristallinsel."""
    def extra(w, u, R, innen):
        rng = w.rng
        for (x, y, z, typ) in innen:
            if typ == "boden" and math.hypot(x, z) < R * 0.8:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("lapis_block" if rng.random() < 0.15 else "deepslate"))
        for z in range(round(R * 0.2), round(R * 0.9)):
            w.setze(0, 1, z, w.b("dark_oak_slab", type="bottom", waterlogged=False))
        buschel(w, (0, 0, 0), 6, 6 * u + 2, 0.8 * u + 0.5, "saphir")
    return _edelhoehle(seed, g, "saphir", dichte=0.1, extra=extra)


def obsidiankluft(seed, g=2):
    """Obsidiankluft: schwarze Glaswände, weinender Obsidian mit violett leuchtenden Tränen, scharfkantige
    schwarze Kristallsplitter."""
    w = _edelhoehle(seed, g, "obsidian", dichte=0.1)
    rng = w.rng
    for (x, y, z), b in list(w.bloecke.items()):
        n = w.P.name(b)
        if n in ("minecraft:stone", "minecraft:tuff", "minecraft:andesite") and rng.random() < 0.4:
            w.bloecke[(x, y, z)] = w.b("blackstone")
    return w


def lavakristallhoehle(seed, g=2):
    """Lavakristallhöhle: orange glühende Feuerkristalle über einem Lavasee, Magma-Adern in Basaltwänden."""
    def extra(w, u, R, innen):
        rng = w.rng
        for (x, y, z, typ) in innen:
            if typ == "boden" and math.hypot(x, z) < R * 0.45:
                w.setze(x, 0, z, w.b("lava", level=0) if math.hypot(x, z) < R * 0.38 else w.b("magma_block"))
            elif typ == "wand" and rng.random() < 0.08:
                w.setze(x, y, z, w.b("magma_block"))
    w = _edelhoehle(seed, g, "feuer", extra=extra)
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) in ("minecraft:stone", "minecraft:andesite", "minecraft:tuff"):
            w.bloecke[(x, y, z)] = w.b("basalt", axis="y") if (x + z) % 2 else w.b("blackstone")
    return w


def regenbogenkristalle(seed, g=2):
    """Regenbogengrotte: Kristalle in allen Farben des Regenbogens, die sich im Licht gegenseitig färben – der
    farbenprächtigste Ort unter Tage."""
    return _edelhoehle(seed, g, "regenbogen", dichte=0.16)


def tropfsteinkristall(seed, g=2):
    """Tropfstein-Kristallhöhle: Stalaktiten und Stalagmiten aus Tropfstein, dazwischen Amethyst-Büschel und
    leuchtende Flechten, Wasser tropft in kleine Becken."""
    def extra(w, u, R, innen):
        rng = w.rng
        for (x, y, z, typ) in innen:
            if typ == "wand" and y > R * 0.4 and rng.random() < 0.1:
                ln = int(1 + rng.integers(int(2 + 3 * u)))
                for k in range(ln):
                    p = (x - int(np.sign(x)), y - 1 - k, z - int(np.sign(z)))
                    if w.frei(*p):
                        w.setze(*p, w.b("pointed_dripstone", vertical_direction="down",
                                        thickness="tip" if k == ln - 1 else "frustum", waterlogged=False))
            if typ == "boden" and rng.random() < 0.06:
                ln = int(1 + rng.integers(int(2 + 2 * u)))
                for k in range(ln):
                    if w.frei(x, 1 + k, z):
                        w.setze(x, 1 + k, z, w.b("pointed_dripstone", vertical_direction="up",
                                                 thickness="tip" if k == ln - 1 else "frustum", waterlogged=False))
    w = _edelhoehle(seed, g, "amethyst", dichte=0.06, extra=extra)
    for (x, y, z), b in list(w.bloecke.items()):
        if w.P.name(b) in ("minecraft:stone", "minecraft:andesite") and (x + y) % 3:
            w.bloecke[(x, y, z)] = w.b("dripstone_block")
    return w


def leuchtkristallgarten(seed, g=2):
    """Leuchtkristallgarten: eine Höhle voller selbst leuchtender Kristalle, Leuchtbeeren-Ranken, Moos und Pilze –
    ein unterirdischer Zaubergarten."""
    def extra(w, u, R, innen):
        rng = w.rng
        for (x, y, z, typ) in innen:
            if typ == "boden" and rng.random() < 0.4:
                w.setze(x, 0, z, w.b("moss_block"))
                if rng.random() < 0.2 and w.frei(x, 1, z):
                    w.setze(x, 1, z, w.b(["red_mushroom", "brown_mushroom", "moss_carpet", "azalea"][
                        int(rng.integers(4))]))
            if typ == "wand" and y > R * 0.5 and rng.random() < 0.06:
                for k in range(int(1 + rng.integers(5))):
                    p = (x - int(np.sign(x)), y - 1 - k, z - int(np.sign(z)))
                    if w.frei(*p):
                        w.setze(*p, w.b("cave_vines_plant", berries=k % 2 == 0))
        for k in range(int(5 + 3 * u)):
            a = rng.random() * 6.28
            d = rng.random() * R * 0.6
            buschel(w, (math.cos(a) * d, 0, math.sin(a) * d), 3, 3 * u + 1.5, 0.5 * u + 0.4,
                    ["saphir", "smaragd", "amethyst"][k % 3])
            w.setze(round(math.cos(a) * d), 1, round(math.sin(a) * d), w.b("verdant_froglight", axis="y"))
    return _edelhoehle(seed, g, "amethyst", dichte=0.05, extra=extra)


def kristallsaeulenhalle(seed, g=2):
    """Kristallsäulenhalle: ein Wald aus sechseckigen, unterschiedlich hohen Quarz- und Amethystsäulen wie
    erstarrte Orgelpfeifen, in einer hohen Halle."""
    def extra(w, u, R, innen):
        rng = w.rng
        for k in range(int(14 * u + 6)):
            a = rng.random() * 6.28
            d = R * 0.75 * math.sqrt(rng.random())
            kristall(w, (math.cos(a) * d, 0, math.sin(a) * d), (0, 1, 0), (3 + rng.random() * 9) * u + 2,
                     (0.8 + rng.random() * 0.8) * u + 0.4, ["quarz", "amethyst"][k % 2], spitze=0.15, ueber=False)
    return _edelhoehle(seed, g, "quarz", H_f=1.1, dichte=0.03, extra=extra)


def kristallkugelschrein(seed, g=1):
    """Kristallkugel-Schrein: in einer kleinen Felsnische schwebt über einem Sockel eine leuchtende Glaskugel,
    umringt von Kerzen und Amethyst."""
    def extra(w, u, R, innen):
        for y in range(1, 3):
            for x in range(-1, 2):
                for z in range(-1, 2):
                    w.setze(x, y, z, w.b("polished_blackstone" if y == 1 else "chiseled_polished_blackstone"))
        c = (0, 4 + u, 0)
        r = 1.2 * u + 0.8
        for x in range(-3, 4):
            for y in range(-3, 4):
                for z in range(-3, 4):
                    d = math.sqrt(x * x + y * y + z * z)
                    if d <= r:
                        w.setze(x, round(c[1]) + y, z, w.b("sea_lantern" if d < r * 0.4 else "light_blue_stained_glass"))
        for k in range(8):
            a = k / 8 * 6.28
            w.setze(round(math.cos(a) * 3), 1, round(math.sin(a) * 3), w.b("candle", candles=3, lit=True,
                                                                           waterlogged=False))
    return _edelhoehle(seed, g, "amethyst", dichte=0.08, extra=extra)


def kristallherz(seed, g=2):
    """Kristallherz: in einer gewaltigen Kaverne schwebt ein riesiger, pulsierend leuchtender Kristall, gehalten von
    Ketten, darunter ein Ring aus Runensteinen."""
    def extra(w, u, R, innen):
        cy = R * 0.45
        kristall(w, (0, cy - 3 * u, 0), (0, 1, 0), 6 * u + 3, 1.6 * u + 0.8, "amethyst", spitze=0.4,
                 kern=w.b("pearlescent_froglight", axis="y"))
        kristall(w, (0, cy - 3 * u, 0), (0, -1, 0), 4 * u + 2, 1.6 * u + 0.8, "amethyst", spitze=0.6,
                 kern=w.b("pearlescent_froglight", axis="y"))
        for k in range(4):
            a = k * 1.57 + 0.6
            linie(w, (0, cy + 3 * u, 0), (math.cos(a) * R * 0.7, R * 0.75, math.sin(a) * R * 0.7),
                  w.b("chain", axis="y", waterlogged=False))
        for k in range(8):
            a = k / 8 * 6.28
            for y in range(1, 3):
                w.setze(round(math.cos(a) * R * 0.5), y, round(math.sin(a) * R * 0.5),
                        w.b("chiseled_deepslate" if y == 2 else "polished_deepslate"))
    return _edelhoehle(seed, g, "amethyst", H_f=1.0, dichte=0.06, extra=extra)


# ============================================================================ Draußen & Bauten

def kristallbruecke(seed, g=2):
    """Kristallbrücke: über einer tiefen Kluft spannt sich ein natürlicher Bogen aus Kristall, an den Klippen wachsen
    Kristallbüschel, unten leuchtet es violett."""
    w = _neu(seed)
    u = U[g]
    L = _r(12 * u + 5)
    D = _r(10 * u + 4)
    rf = Rauschen(w, 1.3)
    for x in range(-L - 6, L + 7):
        for z in range(-_r(6 * u + 3), _r(6 * u + 3) + 1):
            if abs(x) > L:
                for y in range(-D, 1):
                    w.setze(x, y, z, w.b(GESTEIN[int(rf(x, y, z) * 5.99)]))
            else:
                w.setze(x, -D, z, w.b("amethyst_block"))
    for x in range(-L, L + 1):
        t = (x + L) / (2 * L)
        y = round(math.sin(t * math.pi) * 4 * u)
        for z in (-1, 0, 1):
            for dy in range(0, 2):
                w.setze(x, y - dy, z, w.b(EDEL["amethyst"][(x + dy + z) % 4]))
    for sx in (-1, 1):
        for k in range(3):
            buschel(w, (sx * (L + 2), 0, (k - 1) * 3), 3, 4 * u + 2, 0.7 * u + 0.4, "amethyst")
        buschel(w, (sx * (L - 1), -D, 0), 4, 5 * u + 2, 0.8 * u + 0.4, "amethyst")
    return w


def kristallmine(seed, g=2):
    """Kristallmine: ein Stolleneingang mit Holzverbau in einer Felswand, Schienen mit Loren voller Kristalle,
    Förderturm, Werkzeughütte und ausgeschlagene Kristallbrocken."""
    from drachen import felsen
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    P.gelaende(w, R, art="wiese", dichte=0.2)
    hoehe = felsen(w, R * 0.6, 12 * u + 5, cx=0, cz=-round(R * 0.5), spitz=1.0, rauh=0.25)
    for y in range(1, 5):
        for x in range(-2, 3):
            for z in range(-round(R * 0.5) + 2, -round(R * 0.2)):
                w.bloecke.pop((x, y, z), None)
    for z in range(-round(R * 0.5) + 2, -round(R * 0.2), 3):
        for y in range(1, 5):
            for x in (-2, 2):
                w.setze(x, y, z, w.b("spruce_log", axis="y"))
        for x in range(-2, 3):
            w.setze(x, 5, z, w.b("spruce_log", axis="x"))
    for z in range(-round(R * 0.5) + 2, R):
        w.setze(0, 1, z, w.b("rail", shape="north_south", waterlogged=False))
    for k, z in enumerate((round(R * 0.1), round(R * 0.4))):
        w.setze(1, 1, z, w.b("rail", shape="north_south", waterlogged=False))
        w.setze(1, 2, z, w.b("amethyst_cluster", facing="up", waterlogged=False))
    for k in range(int(6 * u)):
        a = w.rng.random() * 6.28
        d = R * (0.3 + 0.5 * w.rng.random())
        buschel(w, (math.cos(a) * d, 1, math.sin(a) * d + R * 0.2), 2, 2 * u + 1, 0.5 * u + 0.4,
                ["amethyst", "smaragd", "saphir"][k % 3])
    st = P.Stil(w, wand=["spruce_planks", "dark_oak_planks", "stripped_spruce_log"], sockel="graustein",
                gesims="stone_brick", dach="mcw_holz", holz="spruce")
    P.gebaeude(w, st, round(R * 0.3), round(R * 0.1), round(R * 0.3) + 5, round(R * 0.1) + 4, y0=1, etagen=1, eh=3,
               dach="sattel", tuer="west", gauben=False, kamine=1)
    return w


def kristallnadeln(seed, g=2):
    """Kristallnadelfeld: auf einer kargen Ebene ragen Hunderte schräge Kristallnadeln aus dem Boden wie ein
    gefrorenes Feuerwerk."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                w.setze(x, 0, z, w.b(["calcite", "tuff", "gravel", "diorite"][(x * 3 + z) % 4]))
                w.setze(x, -1, z, w.b("stone"))
    rng = w.rng
    for k in range(int(25 * u * u + 10)):
        a = rng.random() * 6.28
        d = R * 0.9 * math.sqrt(rng.random())
        kristall(w, (math.cos(a) * d, 0, math.sin(a) * d), (rng.normal() * 0.5, 1, rng.normal() * 0.5),
                 (2 + rng.random() * 6) * u + 1, (0.4 + 0.5 * rng.random()) * u + 0.3,
                 ["quarz", "amethyst", "saphir"][_stil(seed) + (k % 2)])
    return w


def kristallbaum(seed, g=2):
    """Kristallbaum: ein Baum, dessen Stamm aus Amethyst gewachsen ist und dessen Äste in leuchtenden
    Kristallspitzen enden, an denen Glasblätter funkeln."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    P.gelaende(w, R, art="wiese", dichte=0.2)
    rng = w.rng
    H = _r(10 * u + 4)
    kristall(w, (0, 0, 0), (0, 1, 0), H + 2, 1.2 * u + 0.6, "amethyst", spitze=0.1)
    for k in range(int(6 + 2 * u)):
        a = k * 2.39996
        y = H * (0.5 + 0.4 * rng.random())
        d = (math.cos(a), 0.7 + rng.random() * 0.4, math.sin(a))
        kristall(w, (0, y, 0), d, (4 + 3 * rng.random()) * u + 1, 0.6 * u + 0.4, "amethyst")
        end = (math.cos(a) * 5 * u, y + 4 * u, math.sin(a) * 5 * u)
        for j in range(int(6 * u)):
            p = (round(end[0] + rng.normal() * 1.5 * u), round(end[1] + rng.normal() * u),
                 round(end[2] + rng.normal() * 1.5 * u))
            w.setze(*p, w.b(["pink_stained_glass", "magenta_stained_glass", "purple_stained_glass"][j % 3]), False)
    w.setze(0, H + 3, 0, w.b("pearlescent_froglight", axis="y"))
    return w


def hoehleneingang(seed, g=2):
    """Leuchtender Höhleneingang: ein großes Felsmaul in einem Hügel, aus dem violettes Licht dringt, Kristalle
    am Eingang, Tropfsteine und ein Pfad hinein."""
    from drachen import felsen
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    P.gelaende(w, R, art="wiese", dichte=0.3)
    hoehe = felsen(w, R * 0.8, 10 * u + 4, cz=-round(R * 0.2), spitz=1.4, rauh=0.25)
    hr = 4 * u + 2
    for x in range(-int(hr) - 1, int(hr) + 2):
        for y in range(1, int(hr * 1.3) + 2):
            for z in range(-R, R):
                if (x / hr) ** 2 + ((y - 1) / (hr * 1.3)) ** 2 < 1:
                    w.bloecke.pop((x, y, z), None)
    rng = w.rng
    for k in range(int(4 + 2 * u)):
        z = -int(rng.integers(0, int(R * 0.6)))
        sx = 1 if k % 2 else -1
        buschel(w, (sx * hr * 0.8, 1, z), 2, 2.5 * u + 1, 0.5 * u + 0.4, "amethyst")
    for z in range(-int(R * 0.7), 0, 3):
        w.setze(0, 1, z, w.b("pearlescent_froglight", axis="y"))
    for z in range(0, R):
        w.setze(0, 0, z, w.b("gravel") if z % 2 else w.b("cobblestone"))
    return w


def kristallthron(seed, g=2):
    """Kristallthron: auf einem gestuften Podest aus poliertem Schwarzstein steht ein Thron mit hoher Lehne aus
    gebündelten Kristallen, flankiert von Kristallsäulen."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    for k in range(3):
        rr = R - k * 2
        for x in range(-rr, rr + 1):
            for z in range(-rr, rr + 1):
                w.setze(x, k, z, w.b(["polished_blackstone", "polished_blackstone_bricks", "polished_deepslate"][k]))
    y0 = 3
    for x in range(-2, 3):
        for z in range(-1, 2):
            w.setze(x, y0, z, w.b("amethyst_block"))
    w.setze(0, y0 + 1, 0, w.b("purple_carpet"))
    for k in range(7):
        a = (k - 3) * 0.25
        kristall(w, ((k - 3) * 0.8, y0, -1.5), (math.sin(a), 1, -0.2), (6 + 3 * (1 - abs(k - 3) / 3)) * u + 2,
                 0.6 * u + 0.3, "amethyst")
    for sx in (-1, 1):
        kristall(w, (sx * (R - 2), 3, 0), (0, 1, 0), 8 * u + 3, 0.9 * u + 0.4, "quarz", spitze=0.25)
        kristall(w, (sx * (R - 2), 3, -R + 3), (0, 1, 0), 9 * u + 3, 0.9 * u + 0.4, "quarz", spitze=0.25)
    for x in range(-1, 2):
        for k in range(R - 2):
            w.setze(x, 2 - min(2, k // 2), 2 + k, w.b("purple_carpet") if k < 2 else w.b("purple_carpet"), False)
    return w


def kristallgolem(seed, g=2):
    """Kristallgolem: ein riesiger Wächter aus Fels, dem überall Kristalle aus Schultern, Rücken und Armen wachsen,
    mit leuchtendem Kristallherz."""
    from kreaturen import SICHT, glied
    from skulptur import Skulptur, ell, kap
    from weltwunder import bl
    w = _neu(seed)
    u = U[g]
    S = Skulptur(w, u)
    from lib import Verlauf
    S.mat("s", Verlauf(w, "Fels", ["tuff", "andesite", "stone", "calcite"]), basis=0.8, rausch=1.6)
    S.mat("k", bl(w, "pearlescent_froglight"))
    for sx in (-1, 1):
        glied(S, [(sx * 2.4, 8, 0), (sx * 3.0, 4, 0.8), (sx * 3.0, 1, 0)], [2.0, 1.7, 1.6], "s")
        S.plus(ell(sx * 3.0, 0.8, 0.6, 1.8, 0.9, 2.2), "s")
        glied(S, [(sx * 5.5, 15, 0), (sx * 7.2, 10, 1.5), (sx * 6.6, 5, 2.5)], [2.0, 1.8, 1.7], "s")
        S.plus(ell(sx * 6.6, 4, 2.8, 2.2, 2.0, 2.2), "s")
    S.plus(ell(0, 9, 0, 4.0, 3.0, 3.0), "s")
    S.plus(kap((0, 9, 0), (0, 15, 0.6), 4.2, 5.4), "s")
    S.plus(ell(0, 18.2, 1.6, 2.4, 2.2, 2.3), "s")
    S.plus(ell(0, 13, 4.4, 1.8, 1.8, 1.2), "k")
    S.plus(ell(0.9, 18.6, 3.8, 0.55, 0.45, 0.4), "k")
    S.plus(ell(-0.9, 18.6, 3.8, 0.55, 0.45, 0.4), "k")
    S.rendern((-10, -1, -7), (10, 22, 8), versatz=(0.5, 0, 0.5), dreh=SICHT)
    rng = w.rng
    oben = [p for p in w.bloecke if p[1] > 10 * u]
    for k in range(int(30 * u)):
        x, y, z = oben[int(rng.integers(len(oben)))]
        kristall(w, (x, y, z), (rng.normal() * 0.6, 1, rng.normal() * 0.6 - 0.3), (2 + rng.random() * 3) * u,
                 0.4 * u + 0.3, ["amethyst", "saphir"][_stil(seed)], ueber=False)
    return w


def kristallquelle(seed, g=1):
    """Kristallquelle: ein Quelltopf mit glasklarem Wasser, um den ein Ring aus aufrechten Kristallen steht wie ein
    Steinkreis aus Edelsteinen."""
    w = _neu(seed)
    u = U[g]
    R = _r(10 * u + 4)
    P.gelaende(w, R, art="wiese", dichte=0.35)
    r = 3 * u + 1.5
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            d = math.hypot(x, z)
            if d < r:
                for y in range(-3, 1):
                    w.setze(x, y, z, w.b("water", level=0))
                w.setze(x, -4, z, w.b("amethyst_block" if (x + z) % 2 else "calcite"))
                w.bloecke.pop((x, 1, z), None)
            elif d < r + 1:
                w.setze(x, 0, z, w.b("calcite"))
    for k in range(8):
        a = k / 8 * 6.28
        kristall(w, (math.cos(a) * (r + 2.5), 0, math.sin(a) * (r + 2.5)), (math.cos(a) * 0.15, 1, math.sin(a) * 0.15),
                 (4 + 2 * (k % 2)) * u + 1.5, 0.7 * u + 0.4, ["amethyst", "saphir", "smaragd", "quarz"][k % 4],
                 spitze=0.3)
    return w


def geodenfeld(seed, g=2):
    """Geodenfeld: mehrere halb freigelegte Geoden in einer Grabungsstelle, aufgebrochen und funkelnd, mit
    Werkzeug, Laternen und Kisten der Sammler."""
    w = _neu(seed)
    u = U[g]
    R = _r(16 * u + 6)
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z) <= R:
                w.setze(x, 0, z, w.b(["coarse_dirt", "gravel", "dirt", "tuff"][(x * 7 + z * 3) % 4]))
    rng = w.rng
    for k in range(3 + g):
        a = k / (3 + g) * 6.28 + 0.3
        cx, cz = math.cos(a) * R * 0.55, math.sin(a) * R * 0.55
        r = (2.5 + rng.random() * 1.5) * u + 1
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for y in range(-int(r), int(r) + 1):
                for z in range(int(cz - r) - 1, int(cz + r) + 2):
                    d = math.sqrt((x - cx) ** 2 + y * y + (z - cz) ** 2)
                    if d > r or y > r * 0.2:
                        continue
                    blk = "smooth_basalt" if d > r - 1 else "calcite" if d > r - 1.8 else \
                        "amethyst_block" if d > r - 2.6 else None
                    if blk:
                        w.setze(x, y, z, w.b(blk))
                    else:
                        w.bloecke.pop((x, y, z), None)
                        if y == round(-(r - 2.6)) + 1 and rng.random() < 0.3:
                            w.setze(x, y, z, w.b("amethyst_cluster", facing="up", waterlogged=False))
    for k in range(3):
        a = k * 2.1
        x, z = round(math.cos(a) * R * 0.15), round(math.sin(a) * R * 0.15)
        w.setze(x, 1, z, w.b("chest", facing="south", type="single", waterlogged=False) if k == 0 else
                w.b("lantern", hanging=False, waterlogged=False))
    return w


def kristallpilze(seed, g=1):
    """Kristallpilze: eine Höhle, in der Pilze mit durchscheinenden Glashüten wachsen, deren Stiele aus Amethyst
    sind und die von innen leuchten."""
    from pilze import hut, stiel
    def extra(w, u, R, innen):
        rng = w.rng
        for k in range(int(6 + 3 * u)):
            a = rng.random() * 6.28
            d = rng.random() * R * 0.65
            x, z = round(math.cos(a) * d), round(math.sin(a) * d)
            top = stiel(w, x, z, 1, _r((2 + rng.random() * 4) * u), 0.4 * u + 0.2, mat="amethyst_block")
            hut(w, top[0], top[1] - 1, top[2], (1.5 + rng.random()) * u + 0.6, 1.0 * u + 0.6, "kuppel",
                ["purple_stained_glass", "light_blue_stained_glass", "magenta_stained_glass"][k % 3],
                punkte="pearlescent_froglight", punkt_dichte=0.15, lamellen="amethyst_block")
    return _edelhoehle(seed, g, "amethyst", dichte=0.04, extra=extra)


def kristallwasserfall(seed, g=2):
    """Kristallwasserfall: in einer hohen Kristallhöhle stürzt ein Wasserfall aus einer Deckenöffnung in einen
    leuchtenden See, umgeben von Saphir- und Quarzkristallen."""
    def extra(w, u, R, innen):
        H = R * 0.9
        for (x, y, z, typ) in innen:
            if typ == "boden" and math.hypot(x + R * 0.2, z + R * 0.2) < R * 0.45:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("water", level=0))
                w.setze(x, -2, z, w.b("sea_lantern" if (x + z) % 5 == 0 else "deepslate"))
        for x in range(-round(R * 0.2) - 1, -round(R * 0.2) + 2):
            for y in range(1, int(H) + 4):
                w.setze(x, y, -round(R * 0.2), w.b("water", level=0 if y >= int(H) + 2 else 8))
    return _edelhoehle(seed, g, "saphir", H_f=0.95, dichte=0.08, extra=extra)


KRISTALL = {
    "amethystgeode": ("Amethystgeode", amethystgeode),
    "riesenkristallgrotte": ("Riesenkristallgrotte", riesenkristallgrotte),
    "eiskristallhoehle": ("Eiskristallhöhle", eiskristallhoehle),
    "smaragdhoehle": ("Smaragdhöhle", smaragdhoehle),
    "rubinhoehle": ("Rubinhöhle", rubinhoehle),
    "saphirsee": ("Saphirsee", saphirsee),
    "obsidiankluft": ("Obsidiankluft", obsidiankluft),
    "lavakristallhoehle": ("Lavakristallhöhle", lavakristallhoehle),
    "regenbogenkristalle": ("Regenbogengrotte", regenbogenkristalle),
    "tropfsteinkristall": ("Tropfstein-Kristallhöhle", tropfsteinkristall),
    "leuchtkristallgarten": ("Leuchtkristallgarten", leuchtkristallgarten),
    "kristallsaeulenhalle": ("Kristallsäulenhalle", kristallsaeulenhalle),
    "kristallkugelschrein": ("Kristallkugel-Schrein", kristallkugelschrein),
    "kristallherz": ("Kristallherz", kristallherz),
    "kristallbruecke": ("Kristallbrücke", kristallbruecke),
    "kristallmine": ("Kristallmine", kristallmine),
    "kristallnadeln": ("Kristallnadelfeld", kristallnadeln),
    "kristallbaum": ("Kristallbaum", kristallbaum),
    "hoehleneingang": ("Leuchtender Höhleneingang", hoehleneingang),
    "kristallthron": ("Kristallthron", kristallthron),
    "kristallgolem": ("Kristallgolem", kristallgolem),
    "kristallquelle": ("Kristallquelle", kristallquelle),
    "geodenfeld": ("Geodenfeld", geodenfeld),
    "kristallpilze": ("Kristallpilze", kristallpilze),
    "kristallwasserfall": ("Kristallwasserfall", kristallwasserfall),
}

"""Wikingerdorf II – zwanzig weitere Bauten aus dem Norden: Wikinger-Schmiede, Grassodenhaus, Webstube, Schiffs-
werft am Fjord, Stockfisch-Gestelle, Feuerbestattungs-Boot, Runenmetz-Platz, Wolfswächter-Paar, Fjordburg, Geweih-
halle, Dampfbad, Kampfübungsplatz, Metbrauerei, Ziegenhof, Strandmarkt, Warnfeuer am Kliff, Schatzhort im Hügel,
Galionsfigur-Denkmal, Runenbrücke und Rabenfels."""

from __future__ import annotations

import math

from erw_basis import M, S, baumrand, figur, fichte, grasdach, haus, hoehe, wiese
from feinbau import Dachmat, kegeldach, laterne, platte, satteldach, treppe, zaun
from flora import _neu
from leuchtwald2 import bez, kugel, rohr
from lib import Rauschen
from skulptur import ell, kap, kasten, kegel, kreisrand


def balken(w, holz="spruce"):
    return M(w, [(f"stripped_{holz}_log", 2), (f"{holz}_planks", 3), (f"{holz}_log", 1)])


def stein(w):
    return M(w, [("cobblestone", 3), ("mossy_cobblestone", 2), ("stone", 1), ("andesite", 1)])


def drachenkopf(w, x, y, z, richtung=1, holz="spruce"):
    for k in range(3):
        w.setze(x + richtung * k // 2, y + k, z, w.b(f"{holz}_log", axis="y"))
    w.setze(x + richtung, y + 3, z, w.b(f"{holz}_planks"))
    w.setze(x + richtung * 2, y + 3, z, w.b(f"{holz}_fence"))


def schild(w, x, y, z, farben=("red_wool", "white_wool")):
    w.setze(x, y, z, w.b(farben[(x + z) % 2]))


def langschiff(w, x0, z0, L, B, y0=0, holz="spruce", segel=("red_wool", "white_wool"), mast=True):
    """Ein kleines Langschiff entlang x mit Schildreihe, Drachensteven und Rahsegel."""
    for i in range(-L, L + 1):
        t = i / (L + 0.5)
        bw = B * math.sqrt(max(0, 1 - t ** 2))
        yh = y0 + round(abs(t) ** 3 * 2)
        for q in range(-int(bw) - 1, int(bw) + 2):
            if abs(q) <= bw:
                rand = abs(q) > bw - 1
                w.setze(x0 + i, yh, z0 + q, w.b(f"{holz}_planks"))
                if rand:
                    w.setze(x0 + i, yh + 1, z0 + q, w.b(f"{holz}_planks"))
                    if abs(t) < 0.75 and i % 2 == 0:
                        w.setze(x0 + i, yh + 1, z0 + q + (1 if q > 0 else -1), w.b(segel[(i // 2) % 2]), False)
    for sx in (-1, 1):
        for k in range(4):
            w.setze(x0 + sx * (L + k // 2), y0 + 2 + k, z0, w.b(f"{holz}_log", axis="y"))
        w.setze(x0 + sx * (L + 2), y0 + 5, z0, w.b(f"{holz}_fence"))
    if mast:
        H = int(L * 1.1) + 3
        for y in range(y0 + 1, y0 + H):
            w.setze(x0, y, z0, w.b(f"{holz}_log", axis="y"))
        sb = int(B) + 2
        for y in range(y0 + 4, y0 + H - 1):
            for q in range(-sb, sb + 1):
                w.setze(x0 + 1, y, z0 + q, w.b(segel[(q // 2 + 10) % 2]))
        for q in range(-sb - 1, sb + 2):
            w.setze(x0, y0 + H - 1, z0 + q, w.b(f"{holz}_log", axis="z"))


# ============================================================================ Bauten

def schmiede(seed, g=1):
    """Wikinger-Schmiede: ein offener Schmiedeschuppen mit Grasdach auf Stämmen, Esse aus Feldsteinen mit
    Blasebalg, Amboss, Löschtrog, Gestell mit Äxten und Schilden sowie ein Holzkohlenmeiler daneben."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.3)
    B, T = int(4 * s + 6), int(3 * s + 5)
    x0, z0, x1, z1 = -B // 2, -T // 2, B // 2, T // 2
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, 0, z, w.b("coarse_dirt" if (x + z) % 3 else "gravel"))
            for y in range(1, 5):
                w.bloecke.pop((x, y, z), None)
    for x in (x0, x1):
        for z in (z0, z1):
            for y in range(1, 4):
                w.setze(x, y, z, w.b("spruce_log", axis="y"))
    grasdach(w, x0, z0, x1, z1, 4, first_x=B >= T)
    st = stein(w)
    for x in range(x0 + 1, x0 + 4):
        for z in range(z0, z0 + 3):
            for y in range(1, 3):
                w.setze(x, y, z, st(x, y, z))
    w.setze(x0 + 2, 3, z0 + 1, w.b("campfire", lit=True, signal_fire=True, facing="south", waterlogged=False))
    w.setze(x0 + 4, 1, z0 + 1, w.b("brown_wool"))
    w.setze(0, 1, 0, w.b("anvil", facing="east"))
    w.setze(x1 - 1, 1, z1 - 1, w.b("water_cauldron", level=3))
    w.setze(x1 - 2, 1, z1 - 1, w.b("grindstone", face="floor", facing="north"))
    for k in range(3):
        w.setze(x1 - 1 - k, 2, z0, w.b(["red_wool", "white_wool", "blue_wool"][k]))
    mx, mz = x1 + 4, 0
    kugel(w, mx, 0, mz, 2.2 + s * 0.6, w.b("coarse_dirt"), ry=1.8 + s * 0.5)
    w.setze(mx, round(2.5 + s), mz, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    baumrand(w, zellen, R, 3 + 2 * g, seed, art="fichte")
    return w


def grassodenhaus(seed, g=1):
    """Grassodenhaus: ein niedriges Wohnhaus mit Wänden aus Feldsteinen und Torf, einem dicken Grasdach, auf dem
    Blumen wachsen, einer geschnitzten Holztür und einem kleinen Kräutergarten mit Flechtzaun."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.3)
    B, T = int(6 * s + 6) | 1, int(3 * s + 5) | 1
    x0, z0, x1, z1 = -B // 2, -T // 2, B // 2, T // 2
    wand = M(w, [("cobblestone", 2), ("mossy_cobblestone", 2), ("mud_bricks", 1), ("packed_mud", 1)])
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            for y in range(1, 4):
                if x in (x0, x1) or z in (z0, z1):
                    w.setze(x, y, z, wand(x, y, z))
                else:
                    w.bloecke.pop((x, y, z), None)
    top = grasdach(w, x0, z0, x1, z1, 4, first_x=True, ue=1)
    rng = w.rng
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            y = hoehe(w, x, z, top + 1)
            if rng.random() < 0.15:
                w.setze(x, y + 1, z, w.b(["poppy", "dandelion", "oxeye_daisy", "cornflower"][int(rng.integers(4))]))
    for y in (1, 2):
        w.setze(0, y, z1, w.b("spruce_door", facing="south", half="lower" if y == 1 else "upper", hinge="left",
                              open=False, powered=False))
    for x in (x0 + 2, x1 - 2):
        w.setze(x, 2, z1, w.b("spruce_trapdoor", facing="south", half="bottom", open=True, powered=False,
                              waterlogged=False))
    for y in range(4, top + 2):
        w.setze(x1 - 2, y, 0, w.b("cobblestone"))
    w.setze(x1 - 2, top + 2, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    gz = z1 + 3
    for x in range(-4, 5):
        for z in range(gz, gz + 4):
            w.setze(x, zellen.get((x, z), 0), z, w.b("farmland", moisture=7))
            w.setze(x, zellen.get((x, z), 0) + 1, z, w.b(["wheat", "carrots", "beetroots"][x % 3], age=3) if
                    x % 3 != 2 else w.b("beetroots", age=3))
        w.setze(x, 1, gz + 4, zaun(w, "spruce"))
    baumrand(w, zellen, R, 3 + 2 * g, seed, art="misch")
    return w


def webstube(seed, g=1):
    """Webstube: ein kleines Fachwerkhaus aus Spaltbohlen mit Webstuhl und Spinnrad, davor Gestelle mit bunt
    gefärbten Wollbahnen zum Trocknen, Färbebottiche und Schafe auf einer Koppel."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.2)
    haus(w, -int(R * 0.3), -int(R * 0.25), int(3 * s + 5) | 1, int(2 * s + 5) | 1, 1, balken(w), H=3,
         dach=("spruce", "dark_oak"), tuer_s="south")
    w.setze(-int(R * 0.3), 1, -int(R * 0.25), w.b("loom", facing="south"))
    farben = ["red_wool", "yellow_wool", "blue_wool", "green_wool", "purple_wool", "orange_wool"]
    for k in range(2 + g):
        x0, z0 = -int(R * 0.6), int(R * 0.15) + k * 3
        for x in (x0, x0 + 6):
            for y in range(1, 4):
                w.setze(x, y, z0, w.b("spruce_fence"))
        for x in range(x0, x0 + 7):
            w.setze(x, 4, z0, w.b("spruce_log", axis="x") if x in (x0, x0 + 6) else w.b("spruce_fence"))
            if x0 < x < x0 + 6:
                w.setze(x, 3, z0, w.b(farben[(x + k) % 6]))
                w.setze(x, 2, z0, w.b(farben[(x + k) % 6]) if (x + k) % 2 else w.b("air"))
    for k in range(3):
        w.setze(int(R * 0.1) + k * 2, 1, int(R * 0.1), w.b("water_cauldron", level=3))
    px, pz = int(R * 0.35), int(R * 0.3)
    for x in range(px - 4, px + 5):
        for z in (pz - 3, pz + 3):
            w.setze(x, zellen.get((x, z), 0) + 1, z, zaun(w, "spruce"))
    for z in range(pz - 3, pz + 4):
        for x in (px - 4, px + 4):
            w.setze(x, zellen.get((x, z), 0) + 1, z, zaun(w, "spruce"))
    we = w.b("white_wool")
    for k in range(2 + g):
        teile = [(ell(0, 1.6, 0, 1.2, 0.8, 0.8), we), (ell(1.2, 2.0, 0, 0.45, 0.45, 0.4), w.b("light_gray_wool"))] + \
                [(kap((sx, 1.0, sz), (sx, 0, sz), 0.2), w.b("light_gray_wool")) for sx in (-0.7, 0.7)
                 for sz in (-0.4, 0.4)]
        figur(w, 0.6 * s + 0.4, teile, (-2, -1, -2), (2, 3, 2), pos=(px - 2 + k * 2, 1, pz - 1 + (k % 2) * 2),
              winkel=k * 1.3)
    baumrand(w, zellen, R, 2 + 2 * g, seed, art="misch")
    return w


def werft(seed, g=2):
    """Schiffswerft am Fjord: ein Langschiff im Bau auf Holzböcken am Ufer, dahinter eine offene Werkhalle,
    Planken-Stapel, Teerfässer und ein fertiges Boot am Steg im Wasser."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = wiese(w, R, 0.2, art="kies")
    for x in range(-R - 2, R + 3):
        for z in range(int(R * 0.25), R + 3):
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel"))
                for y in range(1, 4):
                    w.bloecke.pop((x, y, z), None)
    L = int(6 * s + 5)
    for i in range(-L, L + 1):
        t = i / (L + 0.5)
        bw = (1.6 * s + 1.4) * math.sqrt(max(0, 1 - t * t))
        for q in range(-int(bw) - 1, int(bw) + 2):
            if abs(abs(q) - bw) < 0.8 and (i + q) % 3 != 0:
                w.setze(i, 3 + round(abs(t) ** 3 * 2) + (abs(q) > bw - 0.5), -2 + q, w.b("spruce_planks"))
        w.setze(i, 2, -2, w.b("spruce_log", axis="x"))
        if i % 3 == 0:
            for q in (-2, 2):
                w.setze(i, 1, -2 + q, w.b("spruce_fence"))
                w.setze(i, 2, -2 + q, w.b("spruce_fence"))
    for k in range(3):
        w.setze(L + k // 2, 4 + k, -2, w.b("spruce_log", axis="y"))
    hz = -int(R * 0.45)
    haus(w, 0, hz, int(8 * s + 6), int(3 * s + 4), 1, balken(w), H=3, tuer_s="south", schorn=False)
    for k in range(3 + g):
        for x in range(int(R * 0.45), int(R * 0.45) + 5):
            w.setze(x, 1 + k // 2, -int(R * 0.1) + k % 2, w.b("stripped_spruce_log", axis="x"))
    for k in range(3):
        w.setze(-int(R * 0.5) + k, 1, -int(R * 0.05), w.b("barrel", facing="up", open=False))
    for z in range(int(R * 0.25), int(R * 0.25) + int(5 * s + 4)):
        for x in (-1, 0, 1):
            w.setze(x - int(R * 0.4), 1, z, w.b("spruce_planks"))
    langschiff(w, -int(R * 0.4) + int(4 * s + 4), int(R * 0.25) + int(3 * s + 3), int(4 * s + 3), 1.2 * s + 1, y0=0)
    return w


def stockfisch(seed, g=1):
    """Stockfisch-Gestelle: lange A-förmige Holzgestelle am felsigen Ufer, behangen mit Reihen getrockneten Fischs,
    dazu Fischerboote auf dem Kies, Netze, Körbe und eine Salzhütte."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.2, art="kies")
    for x in range(-R - 2, R + 3):
        for z in range(int(R * 0.4), R + 3):
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("water", level=0))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
    n = 3 + g
    for k in range(n):
        z0 = -int(R * 0.6) + k * 4
        L = int(5 * s + 4)
        for x in range(-L, L + 1):
            if x % 3 == 0:
                for dz in (-1, 1):
                    for y in range(1, 4):
                        w.setze(x, y, z0 + dz * (1 if y < 3 else 0), w.b("spruce_fence"))
            w.setze(x, 4, z0, w.b("spruce_log", axis="x") if x % 3 == 0 else w.b("spruce_fence"))
            if x % 3:
                w.setze(x, 3, z0 - 1, w.b("dried_kelp_block") if (x + k) % 2 else w.b("brown_terracotta"))
                w.setze(x, 3, z0 + 1, w.b("dried_kelp_block") if (x + k) % 2 == 0 else w.b("brown_terracotta"))
    for k in range(1 + g):
        bx = -int(R * 0.4) + k * int(5 * s + 4)
        for i in range(-3, 4):
            bw = 1.4 * math.sqrt(max(0, 1 - (i / 3.5) ** 2))
            for q in (-1, 0, 1):
                if abs(abs(q) - bw) < 0.8:
                    w.setze(bx + i, 1, int(R * 0.3) + q, w.b("spruce_planks"))
    hx = int(R * 0.55)
    haus(w, hx, -int(R * 0.2), 5, 5, 1, balken(w), H=3, tuer_s="west", schorn=False)
    for k in range(3):
        w.setze(hx - 4, 1, -int(R * 0.2) + k - 1, w.b("barrel", facing="up", open=False))
    return w


def feuerbestattung(seed, g=2):
    """Feuerbestattungs-Boot: auf einem stillen See treibt ein mit Schilden geschmücktes Langschiff, auf dem ein
    Scheiterhaufen lodert; am Ufer stehen Fackelträger-Pfähle und ein Kreis aus Bautasteinen."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = wiese(w, R, 0.2)
    rn = Rauschen(w, 5)
    rs = R * 0.62
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            if math.hypot(x, z * 1.2) < rs + rn(x, 2, z) * 3:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel"))
                for y in range(1, 4):
                    w.bloecke.pop((x, y, z), None)
                zellen[(x, z)] = -1
    L = int(5 * s + 4)
    langschiff(w, 0, 0, L, 1.3 * s + 1.2, y0=0, mast=False)
    for x in range(-2, 3):
        for z in (-1, 0, 1):
            w.setze(x, 2, z, w.b("spruce_log", axis="x" if z else "z"))
    for x in range(-1, 2):
        w.setze(x, 3, 0, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
    w.setze(0, 3, 1, w.b("fire", age=0, north=False, south=False, east=False, west=False, up=False))
    for i in range(10):
        a = i / 10 * 2 * math.pi
        x, z = round(math.cos(a) * (rs + 3)), round(math.sin(a) * (rs + 3) / 1.2)
        y = zellen.get((x, z), 0) + 1
        if i % 2:
            for k in range(int(2 + s)):
                w.setze(x, y + k, z, w.b("stone" if k % 2 else "andesite"))
        else:
            for k in range(3):
                w.setze(x, y + k, z, w.b("spruce_fence"))
            w.setze(x, y + 3, z, w.b("torch"))
    baumrand(w, zellen, R, 3 + 2 * g, seed, innen=0.88, art="fichte")
    return w


def runenmetz(seed, g=1):
    """Runenmetz-Platz: ein Steinmetzplatz mit halbfertigen Runensteinen, Gerüsten, einem Arbeitstisch mit
    Steinsäge, Schutthaufen und einem fertig bemalten Bildstein mit roten Runen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.2, art="kies")
    rng = w.rng
    for k in range(3 + g):
        a = k / (3 + g) * 2 * math.pi + 0.3
        x, z = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.5)
        H = int((3 + rng.random() * 3) * s + 2)
        Bs = 1 + int(s * 0.7)
        for y in range(1, H + 1):
            for dx in range(-Bs, Bs + 1):
                breite = Bs if y < H - 1 else Bs - 1
                if abs(dx) <= breite:
                    rune = dx == 0 and y % 2 == 0 and y < H - 1
                    w.setze(x + dx, y, z, w.b("red_terracotta" if rune and k == 0 else "chiseled_stone_bricks"
                                              if rune else "stone"))
        if k == 1:
            for y in range(1, H + 2):
                for dx in (-Bs - 1, Bs + 1):
                    w.setze(x + dx, y, z + 1, w.b("scaffolding", distance=0, bottom=False, waterlogged=False))
    w.setze(0, 1, 0, w.b("stonecutter", facing="north"))
    w.setze(1, 1, 0, w.b("crafting_table"))
    for _ in range(int(6 * s + 3)):
        x, z = int((rng.random() - 0.5) * R), int((rng.random() - 0.5) * R)
        if (x, z) in zellen:
            w.setze(x, zellen[(x, z)] + 1, z, w.b("cobblestone_slab", type="bottom", waterlogged=False) if
                    rng.random() < 0.5 else w.b("gravel"))
    baumrand(w, zellen, R, 2 + 2 * g, seed, art="fichte")
    return w


def wolfswaechter(seed, g=2):
    """Wolfswächter-Paar: zwei mächtige, sitzende Wolfsstatuen aus grauem Stein mit aufgestellten Ohren flankieren
    einen Hohlweg, der zu einem Tor aus Baumstämmen führt."""
    w = _neu(seed)
    s = S[g]
    u = 0.9 * s + 0.4
    R = int(10 * u + 6)
    zellen = wiese(w, R, 0.3)
    gr = M(w, [("stone", 2), ("andesite", 2), ("cobblestone", 1)])
    hell = w.b("diorite")
    for sx in (-1, 1):
        teile = [(kasten(-2.2, 0, -2.6, 2.2, 1.4, 2.6), w.b("cobblestone")),
                 (ell(0, 4.4, -0.6, 1.9, 3.2, 1.8), lambda x, y, z, *a: gr(x, y, z)),
                 (ell(0, 3.8, 0.8, 1.4, 2.0, 1.3), hell),
                 (ell(0, 7.6, 0.6, 1.4, 1.3, 1.4), lambda x, y, z, *a: gr(x, y, z)),
                 (kap((0, 7.4, 1.4), (0, 7.0, 3.0), 0.75, 0.5), lambda x, y, z, *a: gr(x, y, z)),
                 (ell(0, 6.9, 3.1, 0.3, 0.3, 0.3), w.b("black_concrete")),
                 (kegel(-0.7, 0.2, 8.4, 10.0, 0.5, 0.05), lambda x, y, z, *a: gr(x, y, z)),
                 (kegel(0.7, 0.2, 8.4, 10.0, 0.5, 0.05), lambda x, y, z, *a: gr(x, y, z)),
                 (kap((-0.9, 3.0, 1.2), (-0.9, 1.4, 2.0), 0.45), lambda x, y, z, *a: gr(x, y, z)),
                 (kap((0.9, 3.0, 1.2), (0.9, 1.4, 2.0), 0.45), lambda x, y, z, *a: gr(x, y, z)),
                 (ell(-1.4, 2.0, -1.0, 0.9, 0.9, 1.6), lambda x, y, z, *a: gr(x, y, z)),
                 (ell(1.4, 2.0, -1.0, 0.9, 0.9, 1.6), lambda x, y, z, *a: gr(x, y, z)),
                 (kap((0.8, 1.6, -2.4), (2.2, 1.6, 0.4), 0.45), lambda x, y, z, *a: gr(x, y, z)),
                 (ell(-0.4, 7.2, 1.7, 0.2, 0.2, 0.15), w.b("yellow_concrete")),
                 (ell(0.4, 7.2, 1.7, 0.2, 0.2, 0.15), w.b("yellow_concrete"))]
        figur(w, u, teile, (-3, -1, -4), (3, 11, 4), pos=(sx * round(4 * u + 2), 1, 0), winkel=0.0)
    for z in range(-R, R + 1):
        for x in (-1, 0, 1):
            if (x, z) in zellen:
                w.setze(x, zellen[(x, z)], z, w.b("dirt_path"))
    gz = -int(R * 0.6)
    H = int(4 * s + 4)
    for sx in (-1, 1):
        for y in range(1, H + 1):
            w.setze(sx * 3, y, gz, w.b("spruce_log", axis="y"))
    for x in range(-4, 5):
        w.setze(x, H + 1, gz, w.b("spruce_log", axis="x"))
    for sx in (-1, 1):
        drachenkopf(w, sx * 4, H + 1, gz, sx)
    baumrand(w, zellen, R, 4 + 2 * g, seed, art="fichte")
    return w


def fjordburg(seed, g=2):
    """Fjordburg: eine Ringwallburg aus Erde und Palisaden auf einer Felsklippe über dem Wasser, mit Torturm,
    Wehrgang, Langhaus im Inneren und einer Treppe hinab zum Bootsanleger."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    rn = Rauschen(w, 5)
    H = int(6 * s + 4)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            if z > R * 0.45 + rn(x, 3, 0) * 3:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel"))
                continue
            h = H + int(rn(x, 4, z) * 2)
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else w.b("stone") if y < h - 2 else
                        w.b("dirt"))
    rb = R * 0.42
    for x, z in kreisrand(rb, 0, -int(R * 0.05)):
        y = hoehe(w, x, z, H + 4)
        w.setze(x, y + 1, z, w.b("coarse_dirt"))
        for k in range(2, int(3 + s)):
            w.setze(x, y + k, z, w.b("spruce_log", axis="y") if (x + z) % 3 else w.b("stripped_spruce_log", axis="y"))
        if (x + z) % 2 == 0:
            w.setze(x, y + int(3 + s), z, w.b("spruce_fence"))
    tz = -int(R * 0.05) - round(rb)
    for dx in (-2, 2):
        for y in range(H + 1, H + int(6 * s + 4)):
            w.setze(dx, y, tz, w.b("spruce_log", axis="y"))
    for x in range(-2, 3):
        for y in range(H + 1, H + 4):
            w.bloecke.pop((x, y, tz), None)
        w.setze(x, H + int(6 * s + 4), tz, w.b("spruce_planks"))
    kegeldach(w, 0, tz, H + int(6 * s + 4) + 1, 2, Dachmat(w, ["spruce", "dark_oak"]), form="kegel", eckig=True,
              spitze="spruce_fence")
    haus(w, 0, -int(R * 0.05), int(6 * s + 5) | 1, int(2 * s + 5) | 1, H + 1, balken(w), H=3, tuer_s="north",
         steil=2)
    for k in range(H):
        z = int(R * 0.35) + k
        for x in (int(R * 0.3), int(R * 0.3) + 1):
            w.setze(x, H - k, z, treppe(w, "cobblestone", "north"))
            for yy in range(H - k + 1, H + 3):
                w.bloecke.pop((x, yy, z), None)
    for z in range(int(R * 0.45), int(R * 0.45) + 5):
        for x in range(int(R * 0.25), int(R * 0.25) + 3):
            w.setze(x, 1, z, w.b("spruce_planks"))
    return w


def geweihhalle(seed, g=2):
    """Geweihhalle: eine prächtige Halle mit geschnitztem Portal, deren Giebel von einem riesigen Hirschgeweih
    aus Holz gekrönt wird; Schindeldach, Schilde an den Wänden und Fackeln am Eingang."""
    w = _neu(seed)
    s = S[g]
    R = int(13 * s + 6)
    zellen = wiese(w, R, 0.2)
    B, T = int(4 * s + 7) | 1, int(9 * s + 9) | 1
    top = haus(w, 0, 0, B, T, 1, balken(w, "dark_oak"), holz="dark_oak", H=int(2 * s + 4),
               dach=("dark_oak", "spruce"), tuer_s="south", schorn=False, steil=2)
    for z in range(-T // 2 + 2, T // 2 - 1, 3):
        for sx in (-1, 1):
            w.setze(sx * (B // 2 + 1), 3, z, w.b(["red_wool", "white_wool", "yellow_wool"][(z // 3) % 3]))
    zg = T // 2 + 2
    yb = top - 1
    for sx in (-1, 1):
        pts = bez((sx * 0.5, yb, zg), (sx * 3 * s, yb + 3 * s, zg), (sx * (5 * s + 2), yb + 6 * s + 2, zg))
        rohr(w, pts, 0.6 * s + 0.3, 0.3, mat=w.b("stripped_dark_oak_log", axis="y"))
        for t in (0.35, 0.6, 0.85):
            i = int(t * (len(pts) - 1))
            x, y, z, _ = pts[i]
            rohr(w, bez((x, y, z), (x + sx * s, y + 2 * s, z), (x + sx * 0.5 * s, y + 3.5 * s, z)), 0.4 * s + 0.2,
                 0.2, mat=w.b("stripped_dark_oak_log", axis="y"))
    for sx in (-2, 2):
        w.setze(sx, 3, T // 2 + 1, w.b("torch"))
    baumrand(w, zellen, R, 3 + 2 * g, seed, art="fichte")
    return w


def dampfbad(seed, g=1):
    """Dampfbad: eine kleine, halb in den Hang gebaute Badehütte aus Stein und Holz, aus deren Dachluke Dampf
    steigt, mit Holzbottich, Ruhebank, Holzstapel und einem Steg hinaus in einen kalten Teich."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.3)
    for x in range(-R, R + 1):
        for z in range(int(R * 0.25), R + 1):
            if math.hypot(x, z) < R * 0.9 and (x, z) in zellen:
                w.setze(x, zellen[(x, z)], z, w.b("water", level=0))
    B, T = int(3 * s + 5) | 1, int(3 * s + 5) | 1
    x0, z0, x1, z1 = -B // 2, -T // 2 - int(R * 0.15), B // 2, T // 2 - int(R * 0.15)
    st = stein(w)
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            for y in range(1, 4):
                if x in (x0, x1) or z in (z0, z1):
                    w.setze(x, y, z, st(x, y, z) if y == 1 else w.b("spruce_log", axis="y") if
                            x in (x0, x1) and z in (z0, z1) else w.b("stripped_spruce_log", axis="x" if z in (z0, z1)
                                                                    else "z"))
                else:
                    w.bloecke.pop((x, y, z), None)
    top = grasdach(w, x0, z0, x1, z1, 4, first_x=True)
    w.setze(0, top + 1, (z0 + z1) // 2, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                              waterlogged=False))
    w.setze(0, 1, (z0 + z1) // 2, w.b("magma_block"))
    w.setze(x0 + 1, 1, z0 + 1, w.b("water_cauldron", level=3))
    for y in (1, 2):
        w.bloecke.pop((0, y, z1), None)
    for z in range(z1 + 1, int(R * 0.7)):
        for x in (-1, 0, 1):
            w.setze(x, 1, z, w.b("spruce_slab", type="bottom", waterlogged=False))
    for x in range(x1 + 2, x1 + 5):
        w.setze(x, 1, 0, treppe(w, "spruce", "north"))
    for k in range(3):
        for x in range(x0 - 3, x0):
            w.setze(x, 1 + k // 2, z0 + k % 2, w.b("spruce_log", axis="x"))
    baumrand(w, {k: v for k, v in zellen.items() if k[1] < R * 0.25}, R, 3 + g, seed, art="birke")
    return w


def uebungsplatz(seed, g=1):
    """Kampfübungsplatz: ein umzäunter Sandplatz mit Strohpuppen, Zielscheiben, Waffengestellen, einem Holz-
    podest für den Ausbilder und Schildwänden zum Üben des Schildwalls."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.1)
    A = int(R * 0.65)
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            w.setze(x, 0, z, w.b("coarse_dirt" if (x + z) % 4 else "sand"))
            if max(abs(x), abs(z)) == A and not (z == A and abs(x) < 2):
                w.setze(x, 1, z, zaun(w, "spruce"))
    for k in range(3 + g):
        x, z = -A + 3 + k * 3, -A + 3
        w.setze(x, 1, z, w.b("spruce_fence"))
        w.setze(x, 2, z, w.b("hay_block", axis="y"))
        w.setze(x, 3, z, w.b("carved_pumpkin", facing="south"))
    for k in range(2 + g // 2):
        w.setze(A - 2, 1, -A + 3 + k * 3, w.b("target", power=0))
        w.setze(A - 2, 2, -A + 3 + k * 3, w.b("target", power=0))
    for k in range(5):
        w.setze(-2 + k, 1, A - 3, w.b("spruce_fence"))
        w.setze(-2 + k, 2, A - 3, w.b(["red_wool", "white_wool"][k % 2]))
    for x in range(-A + 2, -A + 5):
        for z in range(A - 4, A - 1):
            w.setze(x, 1, z, w.b("spruce_planks"))
    w.setze(-A + 3, 2, A - 3, w.b("spruce_fence"))
    w.setze(-A + 3, 3, A - 3, w.b("lantern", hanging=False, waterlogged=False))
    baumrand(w, zellen, R, 2 + 2 * g, seed, innen=0.88, art="fichte")
    return w


def metbrauerei(seed, g=1):
    """Metbrauerei: eine Brauhütte mit großen Bottichen und Fässern, davor eine Reihe Bienenkörbe aus Stroh
    zwischen Blumenbeeten, ein Kräuterbeet und ein Tisch mit Trinkhörnern."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.2, blumen=0.12)
    haus(w, 0, -int(R * 0.3), int(4 * s + 5) | 1, int(3 * s + 5) | 1, 1, balken(w), H=3, tuer_s="south")
    for k in range(3):
        w.setze(-2 + k * 2, 1, -int(R * 0.3), w.b("barrel", facing="up", open=False))
    for k in range(3 + g):
        x = -int(R * 0.5) + k * 3
        z = int(R * 0.35)
        w.setze(x, 1, z, w.b("spruce_slab", type="top", waterlogged=False))
        w.setze(x, 2, z, w.b("bee_nest", facing="south", honey_level=5))
        w.setze(x, 3, z, w.b("hay_block", axis="y"))
    for x in range(-2, 3):
        w.setze(x, 1, int(R * 0.1), w.b("spruce_fence") if abs(x) == 2 else w.b("spruce_slab", type="top",
                                                                                  waterlogged=False))
    w.setze(0, 2, int(R * 0.1), w.b("lantern", hanging=False, waterlogged=False))
    for x in range(int(R * 0.3), int(R * 0.3) + 4):
        for z in range(-2, 3):
            w.setze(x, zellen.get((x, z), 0) + 1, z, w.b(["allium", "cornflower", "lilac", "oxeye_daisy"][(x + z) % 4],
                                                         **({"half": "lower"} if (x + z) % 4 == 2 else {})))
    baumrand(w, zellen, R, 2 + 2 * g, seed, art="birke")
    return w


def ziegenhof(seed, g=1):
    """Ziegenhof: ein Hof mit Stall aus Feldsteinen und Grasdach, einer steinigen Weide mit Kletterfelsen für
    Ziegen, Melkschemel, Heuraufe und einem kleinen Käselager."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.4)
    B, T = int(5 * s + 6) | 1, int(3 * s + 5) | 1
    x0, z0 = -B // 2 - int(R * 0.3), -T // 2 - int(R * 0.3)
    x1, z1 = x0 + B - 1, z0 + T - 1
    st = stein(w)
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            for y in range(1, 4):
                if x in (x0, x1) or z in (z0, z1):
                    w.setze(x, y, z, st(x, y, z))
                else:
                    w.bloecke.pop((x, y, z), None)
            w.setze(x, 0, z, w.b("coarse_dirt"))
    grasdach(w, x0, z0, x1, z1, 4, first_x=B >= T)
    for y in (1, 2):
        w.bloecke.pop(((x0 + x1) // 2, y, z1), None)
    w.setze(x0 + 1, 1, z0 + 1, w.b("hay_block", axis="y"))
    px, pz = int(R * 0.25), int(R * 0.2)
    A = int(4 * s + 4)
    for x in range(px - A, px + A + 1):
        for z in (pz - A, pz + A):
            w.setze(x, hoehe(w, x, z, 6) + 1, z, zaun(w, "spruce"))
    for z in range(pz - A, pz + A + 1):
        for x in (px - A, px + A):
            w.setze(x, hoehe(w, x, z, 6) + 1, z, zaun(w, "spruce"))
    kugel(w, px, 0, pz, 2 + s, M(w, [("stone", 2), ("mossy_cobblestone", 1), ("andesite", 1)]), ry=2 + s)
    we = w.b("white_wool")
    br = w.b("brown_wool")
    for k in range(2 + g):
        f = we if k % 2 else br
        teile = [(ell(0, 1.6, 0, 1.0, 0.65, 0.55), f), (ell(1.0, 2.3, 0, 0.4, 0.4, 0.35), f),
                 (kap((0.9, 2.6, 0.2), (0.4, 3.2, 0.3), 0.1), w.b("gray_concrete")),
                 (kap((0.9, 2.6, -0.2), (0.4, 3.2, -0.3), 0.1), w.b("gray_concrete")),
                 (ell(1.3, 1.8, 0, 0.12, 0.3, 0.1), f)] + \
                [(kap((sx, 1.2, sz), (sx, 0, sz), 0.15), f) for sx in (-0.6, 0.6) for sz in (-0.3, 0.3)]
        x, z = px - A + 2 + k * 2, pz + (k % 3) - 1
        figur(w, 0.6 * s + 0.4, teile, (-2, -1, -2), (2, 4, 2), pos=(x, hoehe(w, x, z, 12) + 1, z), winkel=k * 1.7)
    baumrand(w, zellen, R, 2 + 2 * g, seed, innen=0.88, art="fichte")
    return w


def strandmarkt(seed, g=2):
    """Strandmarkt: Händler haben ihre Langschiffe auf den Strand gezogen und bieten unter gestreiften Zeltplanen
    Felle, Fässer, Bernstein und Waffen feil; ein Feuerplatz und Tauschwaagen in der Mitte."""
    w = _neu(seed)
    s = S[g]
    R = int(14 * s + 7)
    zellen = wiese(w, R, 0.1, art="strand")
    for x in range(-R - 2, R + 3):
        for z in range(int(R * 0.45), R + 3):
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("sand"))
    for k in range(1 + g // 2):
        langschiff(w, -int(R * 0.35) + k * int(R * 0.7), int(R * 0.45), int(4 * s + 3), 1.2 * s + 1, y0=1,
                   segel=(("red_wool", "white_wool"), ("blue_wool", "yellow_wool"))[k % 2], mast=k == 0)
    n = 4 + g
    waren = ["barrel", "brown_wool", "orange_stained_glass", "chest", "white_wool", "iron_block"]
    for i in range(n):
        a = math.pi * (0.1 + 0.8 * i / max(1, n - 1)) + math.pi
        cx, cz = round(math.cos(a) * R * 0.5), round(math.sin(a) * R * 0.45)
        for dx in (-2, 2):
            for dz in (-1, 1):
                for y in range(1, 4):
                    w.setze(cx + dx, y, cz + dz, w.b("spruce_fence"))
        for dx in range(-2, 3):
            for dz in range(-1, 2):
                w.setze(cx + dx, 4, cz + dz, w.b(["red_wool", "white_wool"][(dx + 10) % 2] if i % 2 else
                                                 ["blue_wool", "white_wool"][(dx + 10) % 2]))
        ware = waren[i % 6]
        pr = {"barrel": dict(facing="up", open=False), "chest": dict(facing="south", type="single",
                                                                      waterlogged=False)}.get(ware, {})
        w.setze(cx, 1, cz, w.b(ware, **pr))
        w.setze(cx + 1, 1, cz, w.b("spruce_slab", type="top", waterlogged=False))
    w.setze(0, 1, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        w.setze(round(math.cos(a) * 2.5), 1, round(math.sin(a) * 2.5), w.b("spruce_log", axis="x" if i % 2 else "z"))
    return w


def warnfeuer(seed, g=2):
    """Warnfeuer am Kliff: auf einer zerklüfteten Klippe über dem Meer steht ein hohes Holzgerüst mit Feuerkorb,
    daneben eine Wächterhütte mit Grasdach, ein Signalhorn auf einem Pfahl und ein Pfad hinauf."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    rn = Rauschen(w, 4)
    H = int(9 * s + 6)
    for x in range(-R - 2, R + 3):
        for z in range(-R - 2, R + 3):
            if math.hypot(x, z) > R + 2 * rn(x, 0, z):
                continue
            if z > R * 0.3 + rn(x, 3, 0) * 4:
                w.setze(x, 0, z, w.b("water", level=0))
                continue
            d = math.hypot(x, z + R * 0.15)
            h = max(1, int(H * max(0.0, 1 - (d / (R * 0.95)) ** 1.6) + rn(x, 5, z) * 3))
            for y in range(-1, h + 1):
                w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else w.b("stone") if (x + y) % 3 else
                        w.b("andesite"))
    top = hoehe(w, 0, -int(R * 0.15), H + 5)
    G = int(5 * s + 4)
    for dx in (-1, 1):
        for dz in (-1, 1):
            for y in range(top + 1, top + G):
                w.setze(dx, y, dz - int(R * 0.15), w.b("spruce_log", axis="y"))
    for x in range(-2, 3):
        for z in range(-2 - int(R * 0.15), 3 - int(R * 0.15)):
            w.setze(x, top + G, z, w.b("iron_bars", waterlogged=False) if max(abs(x), abs(z)) == 2 else
                    w.b("cobblestone"))
    for x in (-1, 0, 1):
        for z in (-1 - int(R * 0.15), -int(R * 0.15), 1 - int(R * 0.15)):
            w.setze(x, top + G + 1, z, w.b("campfire", lit=True, signal_fire=True, facing="north",
                                           waterlogged=False))
    hx, hz = -int(R * 0.35), -int(R * 0.3)
    ht = hoehe(w, hx, hz, H + 5)
    st = stein(w)
    for x in range(hx - 2, hx + 3):
        for z in range(hz - 2, hz + 3):
            for y in range(ht + 1, ht + 4):
                if abs(x - hx) == 2 or abs(z - hz) == 2:
                    w.setze(x, y, z, st(x, y, z))
                else:
                    w.bloecke.pop((x, y, z), None)
    grasdach(w, hx - 2, hz - 2, hx + 2, hz + 2, ht + 4)
    for y in range(top + 1, top + 4):
        w.setze(3, y, -2 - int(R * 0.15), w.b("spruce_fence"))
    w.setze(3, top + 4, -2 - int(R * 0.15), w.b("bone_block", axis="x"))
    return w


def schatzhort(seed, g=2):
    """Schatzhort im Hügel: ein grasbewachsener Grabhügel ist an einer Seite aufgebrochen und gibt den Blick frei
    auf eine Steinkammer voller Gold, Truhen, Waffen und einem aufgebahrten Helm."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.1)
    Rh = R * 0.6
    H = 5 * s + 4
    for x in range(-int(Rh) - 1, int(Rh) + 2):
        for z in range(-int(Rh) - 1, int(Rh) + 2):
            d = math.hypot(x, z)
            if d < Rh:
                h = int(H * math.sqrt(1 - (d / Rh) ** 2))
                for y in range(1, h + 1):
                    w.setze(x, y, z, w.b("grass_block", snowy=False) if y == h else w.b("dirt"))
    A = int(2 * s + 2)
    for x in range(-A, A + 1):
        for z in range(-A, A + 1):
            for y in range(1, A + 3):
                if max(abs(x), abs(z)) == A or y == A + 2:
                    w.setze(x, y, z, w.b("mossy_stone_bricks") if (x + y) % 3 else w.b("cobblestone"))
                else:
                    w.bloecke.pop((x, y, z), None)
    for x in range(-A + 1, A):
        for z in range(A, int(Rh) + 2):
            for y in range(1, A + 2):
                if abs(x) < A - 0 and y <= A:
                    w.bloecke.pop((x, y, z), None)
    rng = w.rng
    for x in range(-A + 1, A):
        for z in range(-A + 1, A):
            if rng.random() < 0.5:
                w.setze(x, 1, z, w.b("gold_block") if rng.random() < 0.6 else w.b("raw_gold_block"))
    w.setze(0, 1, -A + 1, w.b("chest", facing="south", type="single", waterlogged=False))
    w.setze(-A + 1, 2, -A + 1, w.b("iron_block"))
    w.setze(A - 1, 1, -A + 1, w.b("chest", facing="south", type="single", waterlogged=False))
    w.setze(0, 2, 0, w.b("gold_block"))
    w.setze(0, 3, 0, w.b("skeleton_skull", rotation=0))
    for k in range(4):
        x, z = int((rng.random() - 0.5) * R * 1.3), int((rng.random() - 0.5) * R * 1.3)
        if math.hypot(x, z) > Rh + 1:
            w.setze(x, zellen.get((x, z), 0) + 1, z, w.b("dirt"))
    baumrand(w, zellen, R, 2 + 2 * g, seed, innen=0.85, art="birke")
    return w


def galionsfigur(seed, g=2):
    """Galionsfigur-Denkmal: ein gewaltiger, geschnitzter Drachenkopf mit offenem Maul, Kamm und Ringelhals aus
    dunklem Holz erhebt sich auf einem Sockel aus Feldsteinen am Hafeneingang."""
    w = _neu(seed)
    s = S[g]
    u = 1.0 * s + 0.5
    R = int(9 * u + 6)
    zellen = wiese(w, R, 0.2, art="kies")
    st = stein(w)
    for x in range(-int(3 * u), int(3 * u) + 1):
        for z in range(-int(3 * u), int(3 * u) + 1):
            for y in range(1, int(2 * u) + 2):
                w.setze(x, y, z, st(x, y, z))
    holz = w.b("dark_oak_planks")
    hell = w.b("stripped_dark_oak_log")
    rot = w.b("red_terracotta")
    gelb = w.b("yellow_terracotta")
    teile = [(kap((0, 0, -1), (0, 6, 0), 1.6, 1.3), holz), (kap((0, 6, 0), (0, 9.5, 2.0), 1.3, 1.1), holz),
             (ell(0, 10.2, 3.0, 1.4, 1.3, 1.8), holz), (kap((0, 10.6, 4.2), (0, 10.4, 6.6), 0.9, 0.7), holz),
             (kap((0, 9.3, 4.0), (0, 8.8, 6.4), 0.7, 0.5), holz), (kasten(-0.6, 9.6, 4.6, 0.6, 10.0, 6.8), None),
             (ell(-0.8, 11.0, 4.0, 0.3, 0.3, 0.3), gelb), (ell(0.8, 11.0, 4.0, 0.3, 0.3, 0.3), gelb),
             (kegel(0, 3.2, 11.0, 13.4, 0.5, 0.05), rot), (kegel(0, 1.5, 9.5, 12.5, 0.5, 0.05), rot),
             (kegel(0, 0, 7.5, 10.5, 0.5, 0.05), rot)]
    for k in range(4):
        teile.append((lambda X, Y, Z, k=k: (abs((X ** 2 + (Z + 0.2 * k) ** 2) ** 0.5 - 1.5 + 0.05 * k) < 0.35) &
                      (abs(Y - (1.0 + k * 1.4)) < 0.3), hell))
    figur(w, u, teile, (-3, -1, -3), (3, 14, 8), pos=(0, int(2 * u) + 2, 0), winkel=0.0)
    for x in range(-R, R + 1):
        for z in range(int(R * 0.55), R + 1):
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("water", level=0))
    return w


def runenbruecke(seed, g=1):
    """Runenbrücke: eine flache Steinbogenbrücke über einen Bach, deren Brüstung aus aufrechten Runensteinen
    besteht; an beiden Enden stehen Bautasteine und Laternenpfähle, am Ufer Birken."""
    w = _neu(seed)
    s = S[g]
    R = int(12 * s + 6)
    zellen = wiese(w, R, 0.2)
    for z in range(-R - 2, R + 3):
        for dx in range(-int(2 * s + 2), int(2 * s + 3)):
            x = dx + round(math.sin(z / 5) * 1.5)
            if (x, z) in zellen:
                w.setze(x, 0, z, w.b("water", level=0))
                w.setze(x, -1, z, w.b("gravel"))
                for y in range(1, 3):
                    w.bloecke.pop((x, y, z), None)
    L = int(2 * s + 2) + 4
    st = stein(w)
    for x in range(-L, L + 1):
        y = 1 + round(1.2 * s * math.cos(math.pi * x / (2 * L)))
        for z in (-1, 0, 1):
            w.setze(x, y, z, w.b("stone_bricks") if z == 0 else st(x, y, z))
            for yy in range(1, y):
                if abs(x) > L - 2:
                    w.setze(x, yy, z, st(x, yy, z))
        for z in (-2, 2):
            if x % 2 == 0:
                w.setze(x, y + 1, z, w.b("chiseled_stone_bricks") if x % 4 == 0 else w.b("stone_brick_wall"))
    for sx in (-1, 1):
        x = sx * (L + 2)
        for y in range(1, 5):
            w.setze(x, y, -3, w.b("stone"))
        w.setze(x, 1, 3, w.b("spruce_fence"))
        w.setze(x, 2, 3, w.b("spruce_fence"))
        w.setze(x, 3, 3, w.b("lantern", hanging=False, waterlogged=False))
    baumrand(w, zellen, R, 4 + 2 * g, seed, art="birke")
    return w


def rabenfels(seed, g=2):
    """Rabenfels: ein einzelner, hoher Felsen mit verkrüppelter Kiefer, auf dem schwarze Rabenfiguren sitzen;
    an seinem Fuß ein Opferstein mit Kerzen und ein Kreis aus kleinen Steinsetzungen."""
    w = _neu(seed)
    s = S[g]
    R = int(11 * s + 6)
    zellen = wiese(w, R, 0.3)
    rn = Rauschen(w, 3)
    H = 12 * s + 6
    for y in range(1, int(H)):
        r = (3.5 * s + 2) * (1 - 0.5 * y / H) + 0.6 * rn(0, y, 0)
        for x in range(-int(r) - 1, int(r) + 2):
            for z in range(-int(r) - 1, int(r) + 2):
                if math.hypot(x, z) <= r + rn(x, y, z) * 1.2:
                    w.setze(x, y, z, w.b("stone" if (x + y) % 4 else "andesite") if rn(x * 2, y, z * 2) > 0.25
                            else w.b("mossy_cobblestone"))
    top = int(H)
    for k in range(int(3 + 2 * s)):
        w.setze(k // 2, top + k, 0, w.b("spruce_log", axis="y"))
    from leuchtwald2 import laubball
    laubball(w, 1, top + int(3 + 2 * s), 0, 2 + s, arten=("spruce_leaves",), dicht=0.8)
    sch = w.b("black_concrete")
    rng = w.rng
    for k in range(3 + g):
        a = rng.random() * 6.28
        r = (3.5 * s + 2) * 0.5
        x, z = round(math.cos(a) * r), round(math.sin(a) * r)
        y = hoehe(w, x, z, top + 3) + 1
        teile = [(ell(0, 1.0, 0, 0.8, 0.6, 0.5), sch), (ell(0.7, 1.6, 0, 0.4, 0.4, 0.35), sch),
                 (kap((1.0, 1.5, 0), (1.5, 1.3, 0), 0.15), w.b("gray_concrete")),
                 (kap((-0.6, 0.9, 0), (-1.4, 0.6, 0), 0.25, 0.1), sch)]
        figur(w, 0.7 * s + 0.4, teile, (-2, -1, -2), (2, 3, 2), pos=(x, y, z), winkel=a)
    ox = int(R * 0.45)
    w.setze(ox, 1, 0, w.b("stone_slab", type="bottom", waterlogged=False))
    w.setze(ox, 2, 0, w.b("candle", candles=3, lit=True, waterlogged=False))
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x, z = round(ox + math.cos(a) * 3), round(math.sin(a) * 3)
        w.setze(x, zellen.get((x, z), 0) + 1, z, w.b("cobblestone"))
    return w


WIKINGER3 = {
    "schmiede": ("Wikinger-Schmiede", schmiede),
    "grassodenhaus": ("Grassodenhaus", grassodenhaus),
    "webstube": ("Webstube", webstube),
    "werft": ("Schiffswerft am Fjord", werft),
    "stockfisch": ("Stockfisch-Gestelle", stockfisch),
    "feuerbestattung": ("Feuerbestattungs-Boot", feuerbestattung),
    "runenmetz": ("Runenmetz-Platz", runenmetz),
    "wolfswaechter": ("Wolfswächter-Paar", wolfswaechter),
    "fjordburg": ("Fjordburg", fjordburg),
    "geweihhalle": ("Geweihhalle", geweihhalle),
    "dampfbad": ("Dampfbad", dampfbad),
    "uebungsplatz": ("Kampfübungsplatz", uebungsplatz),
    "metbrauerei": ("Metbrauerei", metbrauerei),
    "ziegenhof": ("Ziegenhof", ziegenhof),
    "strandmarkt": ("Strandmarkt", strandmarkt),
    "warnfeuer": ("Warnfeuer am Kliff", warnfeuer),
    "schatzhort": ("Schatzhort im Hügel", schatzhort),
    "galionsfigur": ("Galionsfigur-Denkmal", galionsfigur),
    "runenbruecke": ("Runenbrücke", runenbruecke),
    "rabenfels": ("Rabenfels", rabenfels),
}

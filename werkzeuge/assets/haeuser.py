"""Häuser (neu) – 20 Wohn- und Dorfbauten im Pracht-Stil.

Jedes Haus hat zwei eigene Materialwelten, Fensterläden, Blumenkästen, Gesimse, gemischte Dächer mit Gauben
und Kaminen und ein liebevoll gestaltetes Grundstück: Zäune, Beete, Gemüsegarten, Bänke, Holzstapel,
Laternen, Bäume und Wege.
"""

from __future__ import annotations

import math

import pracht as P
from lib import Rauschen, einfuegen, laub
from pracht import Mat, gelaende, treppe
from skulptur import kreisrand, scheibe
from weltwunder import hohl

U = [0.6, 1.0, 1.7, 2.8]
GEGEN = {"north": "south", "south": "north", "east": "west", "west": "east"}


def _welt(seed):
    from lib import Welt
    w = Welt(seed)
    w.anker = (0, 0, 0)
    return w


def _stil(seed):
    return 0 if seed % 100 < 14 else 1


def _r(v, mind=1):
    return max(mind, int(round(v)))


HAUSPOOL = {
    "fachwerk_rot": dict(wand="putz", sockel="graustein", gesims="stone_brick", dach="ziegel", holz="dark_oak",
                         fachwerk=True),
    "fachwerk_ocker": dict(wand="ockerputz", sockel="graustein", gesims="stone_brick", dach="schiefer",
                           holz="spruce", fachwerk=True),
    "stein_schiefer": dict(wand="graustein", sockel="graustein", gesims="stone_brick", dach="schiefer",
                           holz="spruce"),
    "backstein": dict(wand="backstein", sockel="graustein", gesims="brick", dach="schiefer", holz="dark_oak"),
    "kalk_kupfer": dict(wand="kalkstein", sockel="graustein", gesims="stone_brick", dach="kupfer", holz="oak"),
    "holz_dunkel": dict(wand="holz_dunkel", sockel="graustein", gesims="stone_brick", dach="schindel",
                        holz="spruce"),
    "holz_hell": dict(wand="holz_hell", sockel="graustein", gesims="stone_brick", dach="dunkelholz", holz="oak"),
    "putz_blau": dict(wand="putz", sockel="kalkstein", gesims="stone_brick", dach="blau", holz="birch"),
    "sand": dict(wand="sandstein", sockel="sandstein", gesims="sandstone", dach="ziegel", holz="jungle"),
    "lehm": dict(wand="lehm", sockel="graustein", gesims="mud_brick", dach="schindel", holz="spruce",
                 fachwerk=True),
    "marmor": dict(wand="marmor", sockel="kalkstein", gesims="quartz", dach="schiefer", holz="birch"),
    "rot": dict(wand="rotsandstein", sockel="graustein", gesims="red_sandstone", dach="dunkelholz", holz="acacia"),
}


def stil(w, seed, a, b, **extra):
    d = dict(HAUSPOOL[a if _stil(seed) == 0 else b])
    d.update(extra)
    return P.Stil(w, **d)


# ============================================================================ Grundstück


def zaun(w, st, x0, z0, x1, z1, tor=None):
    pts = set()
    for x in range(x0, x1 + 1):
        pts.add((x, 1, z0))
        pts.add((x, 1, z1))
    for z in range(z0, z1 + 1):
        pts.add((x0, 1, z))
        pts.add((x1, 1, z))
    if tor:
        for t in tor:
            pts.discard(t)
    mat = f"{st.holz}_fence"
    for (x, y, z) in pts:
        n, s = (x, y, z - 1) in pts, (x, y, z + 1) in pts
        e, o = (x + 1, y, z) in pts, (x - 1, y, z) in pts
        w.setze(x, y, z, w.b(mat, north=n, south=s, east=e, west=o, waterlogged=False))
    for (x, y, z) in [(x0, 1, z0), (x1, 1, z0), (x0, 1, z1), (x1, 1, z1)]:
        w.setze(x, 2, z, w.b("lantern", hanging=False, waterlogged=False))


def beet(w, x0, z0, x1, z1, art="gemuese"):
    rng = w.rng
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if art == "gemuese":
                if (x - x0) % 3 == 1:
                    w.setze(x, 0, z, w.b("water", level=0))
                    continue
                w.setze(x, 0, z, w.b("farmland", moisture=7))
                w.setze(x, 1, z, w.b(["wheat", "carrots", "potatoes", "beetroots"][(x // 3) % 4],
                                     age=int(rng.integers(3, 8)) if (x // 3) % 4 != 3 else int(rng.integers(1, 4))))
            else:
                w.setze(x, 0, z, w.b("rooted_dirt") if rng.random() < 0.3 else w.b("grass_block", snowy=False))
                w.setze(x, 1, z, w.b(["poppy", "allium", "azure_bluet", "cornflower", "oxeye_daisy", "pink_tulip",
                                      "orange_tulip", "lily_of_the_valley"][int(rng.integers(8))]))


def bank(w, x, z, richtung, holz="spruce"):
    sx, sz = (1, 0) if richtung in ("north", "south") else (0, 1)
    for k in (0, 1):
        w.setze(x + sx * k, 1, z + sz * k, w.b(f"{holz}_stairs", facing=richtung, half="bottom", shape="straight",
                                               waterlogged=False))
    for k in (-1, 2):
        w.setze(x + sx * k, 1, z + sz * k, w.b(f"{holz}_trapdoor", facing=GEGEN[richtung] if False else
                                               ("east" if k < 0 else "west") if sx else ("south" if k < 0 else "north"),
                                               half="bottom", open=True, powered=False, waterlogged=False))


def holzstapel(w, x, z, laenge=3, holz="spruce", achse="x"):
    for k in range(laenge):
        for y in (1, 2):
            p = (x + k, y, z) if achse == "x" else (x, y, z + k)
            if y == 2 and k == laenge - 1:
                continue
            w.setze(*p, w.b(f"{holz}_log", axis="z" if achse == "x" else "x"))


def laternenpfahl(w, x, z, h=3, holz="spruce"):
    for y in range(1, h + 1):
        w.setze(x, y, z, w.b(f"{holz}_fence", north=False, south=False, east=False, west=False, waterlogged=False))
    w.setze(x, h + 1, z, w.b("lantern", hanging=False, waterlogged=False))


def baum(w, x, z, art="oak", H=None):
    import wald
    einfuegen(w, wald.kleiner_laubbaum(int(w.rng.integers(1, 10 ** 7)), art, H=H), x, 0, z)


def strauch(w, x, z, art="azalea"):
    w.setze(x, 1, z, laub(w, art))
    if w.rng.random() < 0.5:
        w.setze(x + 1, 1, z, laub(w, "flowering_azalea"))


def weg(w, a, b, breit=1):
    r = Rauschen(w, 2)
    (x0, z0), (x1, z1) = a, b
    n = max(abs(x1 - x0), abs(z1 - z0)) or 1
    for i in range(n + 1):
        x = round(x0 + (x1 - x0) * i / n)
        z = round(z0 + (z1 - z0) * i / n)
        for d in range(-breit, breit + 1):
            px, pz = (x + d, z) if abs(z1 - z0) >= abs(x1 - x0) else (x, z + d)
            v = r(px, 0, pz)
            w.setze(px, 0, pz, w.b("dirt_path") if v < 0.5 else w.b("gravel") if v < 0.7 else
                    w.b("cobblestone") if v < 0.85 else w.b("coarse_dirt"))


def schild(w, x, y, z, richtung, holz="spruce", text=None):
    w.setze(x, y, z, w.b(f"{holz}_wall_hanging_sign", facing=richtung, waterlogged=False))


def markise(w, x0, x1, z, y, farben, richtung="south"):
    dz = 1 if richtung == "south" else -1
    for x in range(x0, x1 + 1):
        w.setze(x, y, z + dz, w.b(f"{farben[(x - x0) % 2]}_carpet") if False else
                w.b(f"{farben[(x - x0) % 2]}_wool"))
        w.setze(x, y - 1, z + 2 * dz, w.b(f"{farben[(x - x0) % 2]}_carpet")) if False else None


# ============================================================================ Häuser


def fachwerkhaus(seed, g=1):
    """Fachwerkhaus mit auskragendem Obergeschoss, Blumenkästen, Gauben, Bauerngarten mit Zaun und Bank."""
    w = _welt(seed)
    st = stil(w, seed, "fachwerk_rot", "fachwerk_ocker")
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 9, art="wiese", wege=[((0, b + 1), (0, b + 9))])
    top = P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2 + (g >= 2), eh=4, dach="sattel", steil=True, tuer="south")
    zaun(w, st, -a - 4, -b - 4, a + 4, b + 6, tor=[(0, 1, b + 6), (-1, 1, b + 6), (1, 1, b + 6)])
    beet(w, -a - 3, b + 2, -2, b + 5, "blumen")
    beet(w, 2, b + 2, a + 3, b + 5, "gemuese")
    bank(w, -a + 1, b + 1, "south", st.holz)
    holzstapel(w, a + 1, -b - 3, 4, st.holz)
    baum(w, -a - 2, -b - 2, "oak")
    hohl(w, 2)
    return w


def turmhaus(seed, g=1):
    """Schmales Turmhaus mit Rundturm-Erker, spitzem Helm, Balkon und kleinem Hofgarten."""
    w = _welt(seed)
    st = stil(w, seed, "kalk_kupfer", "putz_blau")
    u = U[g]
    a = _r(3 * u + 2, 3)
    gelaende(w, a + 8, art="wiese", wege=[((0, a + 1), (0, a + 8))])
    top = P.gebaeude(w, st, -a, -a, a, a, y0=1, etagen=3 + (g >= 2), eh=4, dach="walm", tuer="south")
    P.turm(w, st, a + 1, -a - 1, 1, top - 3, max(1.4, 1.8 * u), dach="nadel", krone=False, fahne=None)
    for x in range(-a, a + 1):
        w.setze(x, 9, a + 1, w.b(f"{st.holz}_slab", type="top", waterlogged=False))
        w.setze(x, 10, a + 2, w.b(f"{st.holz}_fence", north=False, south=False, east=True, west=True, waterlogged=False))
        w.setze(x, 9, a + 2, w.b(f"{st.holz}_slab", type="top", waterlogged=False))
    beet(w, -a - 3, -a, -a - 2, a, "blumen")
    laternenpfahl(w, 2, a + 4, 3, st.holz)
    hohl(w, 2)
    return w


def bauernhof(seed, g=1):
    """Bauernhof: Wohnhaus, große Scheune mit Tor und Heuboden, Stall mit Koppel, Brunnen, Felder und Misthaufen."""
    w = _welt(seed)
    st = stil(w, seed, "fachwerk_ocker", "stein_schiefer")
    sch = P.Stil(w, wand="holz_dunkel", sockel="graustein", gesims="stone_brick", dach="schindel", holz="spruce",
                 laeden=False)
    u = U[g]
    a = _r(3 * u + 2, 3)
    gelaende(w, _r(16 * u + 8), art="wiese", wege=[((0, a + 1), (0, _r(16 * u + 8)))])
    P.gebaeude(w, st, -a - 8, -a, -8 + a, a, y0=1, etagen=2, eh=4, dach="sattel", tuer="south")
    hb = _r(5 * u + 3, 4)
    P.gebaeude(w, sch, 4, -hb, 4 + 2 * hb, hb, y0=1, etagen=1, eh=_r(5 * u + 2, 5), dach="sattel", first_x=False,
               tuer="west", gauben=False, kamine=0, fenster_abstand=4)
    for y in range(1, 5):
        for z in range(-1, 2):
            w.bloecke.pop((4, y, z), None)
    for z in range(-hb + 1, hb):
        for x in range(5, 4 + 2 * hb):
            if (x + z) % 3 == 0:
                w.setze(x, 1, z, w.b("hay_block", axis="y"))
    # Koppel
    kz = hb + 3
    zaun(w, sch, 4, kz, 4 + 2 * hb, kz + _r(6 * u + 3, 5))
    for x in range(-a - 8, -8 + a + 1):
        for z in range(a + 3, a + 3 + _r(6 * u + 3, 5)):
            pass
    beet(w, -a - 8, a + 3, -8 + a, a + 3 + _r(5 * u + 2, 4), "gemuese")
    w.setze(-2, 1, -a - 2, w.b("composter", level=6))
    holzstapel(w, -a - 8, -a - 3, 4, "spruce")
    for x, z in ((0, 0), (1, 1)):
        w.setze(x, 1, -hb - 2 + z, w.b("hay_block", axis="x"))
    hohl(w, 2)
    return w


def taverne(seed, g=1):
    """Taverne „Zum Goldenen Krug“: breiter Fachwerkbau mit Freisitz, Fässern, Schild, Laternen und Stall."""
    w = _welt(seed)
    st = stil(w, seed, "fachwerk_rot", "holz_dunkel")
    u = U[g]
    a, b = _r(6 * u + 3, 5), _r(4 * u + 2, 3)
    gelaende(w, a + 10, art="wiese", wege=[((0, b + 1), (0, b + 11))])
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="sattel", tuer="south", kamine=2)
    # Freisitz mit Tischen
    for x in range(-a, a + 1):
        for z in range(b + 2, b + 6):
            w.setze(x, 0, z, w.b(f"{st.holz}_planks") if (x + z) % 4 else w.b(f"stripped_{st.holz}_log", axis="x"))
    for x in range(-a + 2, a - 1, 4):
        w.setze(x, 1, b + 4, w.b(f"{st.holz}_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False))
        w.setze(x, 2, b + 4, w.b(f"{st.holz}_pressure_plate", powered=False))
        for dx in (-1, 1):
            w.setze(x + dx, 1, b + 4, w.b(f"{st.holz}_stairs", facing="east" if dx < 0 else "west", half="bottom",
                                          shape="straight", waterlogged=False))
    for x in range(-a - 3, -a):
        for k in range(2):
            w.setze(x, 1 + k, -b + 1, w.b("barrel", facing="east", open=False))
    schild(w, a + 1, 4, 0, "east", st.holz)
    for x in (-a, a):
        laternenpfahl(w, x, b + 7, 3, st.holz)
    hohl(w, 2)
    return w


def stadtvilla(seed, g=2):
    """Stadtvilla mit Mansarddach, Säulenportikus, Balkon, Erkern und symmetrischem Ziergarten."""
    w = _welt(seed)
    st = stil(w, seed, "marmor", "backstein", fensterart="bogen")
    u = U[g]
    a, b = _r(6 * u + 3, 5), _r(4 * u + 2, 4)
    gelaende(w, a + 12, art="wiese", wege=[((0, b + 1), (0, b + 13))])
    top = P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2 + (g >= 2), eh=5, dach="mansarde", tuer="south",
                     pilaster=3, sockel_h=2, kamine=2)
    # Portikus
    for sx in (-2, 2):
        for y in range(3, 8):
            w.setze(sx, y, b + 3, w.b("quartz_pillar", axis="y") if st.gesims == "quartz" else
                    w.b("polished_andesite"))
    for x in range(-3, 4):
        for z in range(b + 1, b + 4):
            w.setze(x, 8, z, w.b(f"{st.gesims}_slab" if st.gesims != "quartz" else "quartz_slab", type="bottom",
                                 waterlogged=False))
        w.setze(x, 9, b + 3, w.b("iron_bars", north=False, south=False, east=x < 3, west=x > -3, waterlogged=False))
    for sx in (-1, 1):
        P.turm(w, st, sx * (a + 1), b + 1, 1, top - 4, 1.6 * min(u, 1.7), dach="glocke", krone=False, fahne=None)
    # Ziergarten
    for x in range(-a, a + 1):
        for z in range(b + 5, b + 12):
            if abs(x) in (3, 7) or z in (b + 5, b + 11):
                w.setze(x, 1, z, laub(w, "oak"))
            elif abs(x) == 5 and z % 2:
                w.setze(x, 1, z, w.b(["red_tulip", "white_tulip", "allium"][z % 3]))
    w.setze(0, 1, b + 8, w.b("water", level=0))
    hohl(w, 2)
    return w


def pfahlhaus(seed, g=1):
    """Pfahlhaus über dem Wasser: Holzhaus auf Stelzen, umlaufender Steg, Leiter, Boot und Reusen."""
    w = _welt(seed)
    st = stil(w, seed, "holz_hell", "holz_dunkel", laeden=False)
    u = U[g]
    a = _r(3 * u + 2, 3)
    R = a + 8
    for x, z in scheibe(R):
        w.setze(x, 0, z, w.b("water", level=0))
        w.setze(x, -1, z, w.b("water", level=0))
        w.setze(x, -2, z, w.b("sand") if (x + z) % 3 else w.b("gravel"))
    ys = 4
    for x in range(-a - 2, a + 3):
        for z in range(-a - 2, a + 3):
            if max(abs(x), abs(z)) == a + 2 and (x + z) % 4 == 0 or (abs(x) == a + 2 and abs(z) == a + 2):
                for y in range(-2, ys):
                    w.setze(x, y, z, w.b(f"{st.holz}_log", axis="y"))
            w.setze(x, ys - 1, z, w.b(f"{st.holz}_planks") if max(abs(x), abs(z)) < a + 2 else
                    w.b(f"{st.holz}_slab", type="top", waterlogged=False))
    for x in range(-a - 2, a + 3):
        for z in range(-a - 2, a + 3):
            if max(abs(x), abs(z)) == a + 2:
                w.setze(x, ys, z, w.b(f"{st.holz}_fence", north=abs(x) == a + 2, south=abs(x) == a + 2,
                                      east=abs(z) == a + 2, west=abs(z) == a + 2, waterlogged=False))
    P.gebaeude(w, st, -a, -a, a, a, y0=ys, etagen=1, eh=4, dach="sattel", tuer="south", sockel_h=0, gauben=False)
    for y in range(0, ys):
        w.setze(0, y, a + 3, w.b("ladder", facing="south", waterlogged=False))
    w.bloecke.pop((0, ys, a + 2), None)
    for k in range(3):
        w.setze(-a + k, 1, a + 5, w.b(f"{st.holz}_slab", type="bottom", waterlogged=False))
    hohl(w, 2)
    return w


def blockhuette(seed, g=1):
    """Blockhütte aus Rundstämmen mit überstehenden Balkenköpfen, Steinkamin, Veranda, Holzplatz und Tannen."""
    w = _welt(seed)
    holz = "spruce" if _stil(seed) == 0 else "dark_oak"
    st = P.Stil(w, wand=[f"stripped_{holz}_log", f"{holz}_log", f"stripped_{holz}_log"], sockel="graustein",
                gesims="cobblestone", dach="schindel" if holz == "spruce" else "dunkelholz", holz=holz)
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 9, art="wald")
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1 + (g >= 2), eh=4, dach="sattel", ue=2, tuer="south", kamine=0,
               gauben=False)
    for y in range(1, 1 + 4 * (1 + (g >= 2))):
        if y % 2 == 0:
            for z in (-b, b):
                for x in (-a - 1, a + 1):
                    w.setze(x, y, z, w.b(f"{holz}_log", axis="x"))
    # Steinkamin außen
    for y in range(1, 12 + 4 * (g >= 2)):
        for dz in (0, 1):
            w.setze(-a - 1, y, dz, w.b(["cobblestone", "mossy_cobblestone", "stone", "andesite"][(y + dz) % 4]))
    w.setze(-a - 1, 12 + 4 * (g >= 2), 0, w.b("campfire", lit=True, signal_fire=False, facing="north",
                                              waterlogged=False))
    for x in range(-a, a + 1):
        w.setze(x, 1, b + 1, w.b(f"{holz}_planks"))
        w.setze(x, 1, b + 2, w.b(f"{holz}_slab", type="bottom", waterlogged=False))
        if x in (-a, a):
            for y in range(2, 5):
                w.setze(x, y, b + 2, w.b(f"{holz}_fence", north=False, south=False, east=False, west=False,
                                         waterlogged=False))
        w.setze(x, 5, b + 2, w.b(f"{holz}_slab", type="bottom", waterlogged=False))
    holzstapel(w, a + 2, -b, 4, holz, "z")
    import wald
    for i in range(3):
        einfuegen(w, wald.schlanke_fichte(int(w.rng.integers(1, 10 ** 6))), -a - 4 + i * 3, 0, -b - 5 - i % 2)
    hohl(w, 2)
    return w


def gildenhaus(seed, g=2):
    """Gildenhaus der Händler: hoher Giebelbau mit Lastkran, Speicherluken, Zunftzeichen und Warenlager."""
    w = _welt(seed)
    st = stil(w, seed, "backstein", "fachwerk_ocker")
    u = U[g]
    a, b = _r(4 * u + 2, 4), _r(5 * u + 3, 4)
    gelaende(w, b + 9, art="wiese", wege=[((0, b + 1), (0, b + 9))])
    top = P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=3 + (g >= 2), eh=4, dach="sattel", first_x=False, steil=True,
                     tuer="south")
    # Lastkran unterm Giebel
    yk = top - 3
    for k in range(3):
        w.setze(0, yk, b + 1 + k, w.b(f"stripped_{st.holz}_log", axis="z"))
    for k in range(yk - 3):
        w.setze(0, yk - 1 - k, b + 3, w.b("chain", axis="y", waterlogged=False))
    w.setze(0, 3, b + 3, w.b("barrel", facing="up", open=False))
    for y in range(5, yk, 4):
        w.setze(0, y, b, w.b(f"{st.holz}_trapdoor", facing="south", half="bottom", open=True, powered=False,
                             waterlogged=False))
    for i in range(6):
        x, z = a + 2 + i % 3, -b + i // 3 * 2
        w.setze(x, 1, z, w.b("barrel", facing="up", open=False) if i % 2 else w.b("hay_block", axis="y"))
    hohl(w, 2)
    return w


def reihenhaeuser(seed, g=1):
    """Zeile schmaler Stadthäuser, jedes mit eigener Farbe, Höhe, Dachform und Tür, mit Gehweg und Laternen."""
    w = _welt(seed)
    u = U[g]
    n = 3 + (g >= 1) + (g >= 3)
    breite = _r(2.5 * u + 2, 3)
    t = _r(4 * u + 2, 4)
    pool = ["fachwerk_rot", "putz_blau", "backstein", "kalk_kupfer", "fachwerk_ocker", "marmor", "stein_schiefer"]
    gelaende(w, n * (2 * breite + 1) // 2 + 6, art="wiese")
    x = -n * (2 * breite + 1) // 2
    for i in range(n):
        name = pool[(i + _stil(seed) * 3) % len(pool)]
        st = P.Stil(w, **HAUSPOOL[name])
        et = 2 + (i % 2) + (g >= 2)
        P.gebaeude(w, st, x, -t, x + 2 * breite, t, y0=1, etagen=et, eh=4, dach="sattel", first_x=False, steil=i % 2,
                   tuer="south", gauben=False, kamine=1)
        x += 2 * breite + 1
    weg(w, (-n * breite - 3, t + 3), (n * breite + 3, t + 3), 1)
    for xx in range(-n * breite, n * breite, 6):
        laternenpfahl(w, xx, t + 5, 3)
    hohl(w, 2)
    return w


def reetdachkate(seed, g=1):
    """Reetdachkate: niedriges Bauernhaus mit tief gezogenem Strohdach, Sprossenfenstern, Rosen und Feldsteinmauer."""
    w = _welt(seed)
    st = stil(w, seed, "putz_blau", "lehm", dach=["hay_block_dach"])
    st.dach = P.Dach(w, ["spruce", "oak", "spruce"])
    u = U[g]
    a, b = _r(5 * u + 3, 4), _r(3 * u + 2, 3)
    gelaende(w, a + 9, art="wiese", wege=[((0, b + 1), (0, b + 9))])
    top = P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=4, dach="walm", ue=2, steil=True, tuer="south",
                     kamine=1)
    # Stroh obenauf
    for (x, y, z), blk in list(w.bloecke.items()):
        if y > 5 and w.P.name(blk).endswith("_stairs") and w.frei(x, y + 1, z) and w.rng.random() < 0.6:
            w.setze(x, y, z, w.b("hay_block", axis="x" if w.rng.random() < 0.5 else "z"))
    for x in range(-a - 4, a + 5):
        for z in (b + 6,):
            if abs(x) > 1:
                w.setze(x, 1, z, w.b(["cobblestone", "mossy_cobblestone", "stone", "andesite"][(x * 7) % 4]))
    for x in range(-a, a + 1, 2):
        w.setze(x, 1, b + 1, w.b("rose_bush", half="lower"))
        w.setze(x, 2, b + 1, w.b("rose_bush", half="upper"))
    baum(w, a + 4, -b - 3, "oak")
    hohl(w, 2)
    return w


def baumhaus(seed, g=1):
    """Baumhaus in einer mächtigen Eiche: Plattformen, Hütte mit Spitzdach, Hängebrücke, Strickleiter."""
    import baeume as Bm
    w = _welt(seed)
    holz = "oak" if _stil(seed) == 0 else "spruce"
    st = P.Stil(w, wand="holz_hell" if holz == "oak" else "holz_dunkel", sockel=[f"{holz}_planks"],
                gesims=holz, dach="schindel" if holz == "oak" else "dunkelholz", holz=holz)
    u = U[g]
    baum_w = Bm.ARTEN["eiche"][1](int(w.rng.integers(1, 10 ** 6)), min(2, g))
    einfuegen(w, baum_w, 0, 0, 0)
    gelaende(w, _r(12 * u + 6), art="wald")
    hmax = max(y for (x, y, z) in baum_w.bloecke)
    yp = max(5, int(hmax * 0.42))
    a = _r(2.5 * u + 1.5, 3)
    for (x, y, z), blk in list(w.bloecke.items()):
        if yp - 1 <= y <= yp + 6 and max(abs(x), abs(z)) <= a + 2 and w.P.name(blk).endswith("leaves"):
            del w.bloecke[(x, y, z)]
    for x, z in scheibe(a + 2):
        w.setze(x, yp - 1, z, w.b(f"{holz}_planks"))
    for x, z in kreisrand(a + 2):
        w.setze(x, yp, z, w.b(f"{holz}_fence", north=True, south=True, east=True, west=True, waterlogged=False))
    P.gebaeude(w, st, -a, -a, a, a, y0=yp, etagen=1, eh=4, dach="walm", steil=True, tuer="south", sockel_h=0,
               gauben=False, kamine=0)
    for y in range(1, yp):
        w.setze(a + 3, y, 0, w.b("ladder", facing="east", waterlogged=False))
    w.setze(a + 2, yp - 1, 0, w.b(f"{holz}_planks"))
    w.bloecke.pop((a + 2, yp, 0), None)
    hohl(w, 2)
    return w


def kaufmannshaus(seed, g=1):
    """Kaufmannshaus mit Ladenfront: großes Schaufenster, Markise, Auslagen, Waren im Erdgeschoss, Wohnung oben."""
    w = _welt(seed)
    st = stil(w, seed, "kalk_kupfer", "fachwerk_rot")
    u = U[g]
    a, b = _r(4 * u + 2, 4), _r(3 * u + 2, 3)
    farben = ["red", "white"] if _stil(seed) == 0 else ["green", "yellow"]
    gelaende(w, a + 8, art="wiese", wege=[((-a, b + 3), (a, b + 3))])
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2 + (g >= 2), eh=4, dach="sattel", tuer="south", kamine=1)
    for x in range(-a + 1, a):
        if abs(x) > 1:
            for y in (2, 3):
                w.setze(x, y, b, w.b("glass_pane", north=False, south=False, east=True, west=True, waterlogged=False))
        w.setze(x, 4, b + 1, w.b(f"{farben[x % 2]}_wool"))
        w.setze(x, 4, b + 2, w.b(f"{farben[x % 2]}_carpet"))
    for x in (-a + 1, a - 1):
        w.setze(x, 1, b + 2, w.b("barrel", facing="up", open=True))
        w.setze(x - (1 if x > 0 else -1), 1, b + 2, w.b("melon") if _stil(seed) else w.b("pumpkin"))
    hohl(w, 2)
    return w


def schmiede(seed, g=1):
    """Dorfschmiede: offene Werkstatt mit Esse, Amboss, Wassertrog und Kohlen, dahinter das Wohnhaus."""
    w = _welt(seed)
    st = stil(w, seed, "stein_schiefer", "backstein")
    u = U[g]
    a, b = _r(3 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 12, art="wiese")
    P.gebaeude(w, st, -a - 6, -b, a - 6, b, y0=1, etagen=2, eh=4, dach="sattel", tuer="east", kamine=1)
    # offene Werkstatt mit Pultdach
    wx0, wx1 = a - 4, a + 5
    for x in range(wx0, wx1 + 1):
        for z in range(-b, b + 1):
            w.setze(x, 0, z, w.b("cobblestone") if (x + z) % 3 else w.b("gravel"))
            if (x in (wx0, wx1)) and z in (-b, b):
                for y in range(1, 5):
                    w.setze(x, y, z, w.b(f"stripped_{st.holz}_log", axis="y"))
            y = 5 + (wx1 - x) // 3
            w.setze(x, y, z, st.dach.treppe(x, y, z, "west"))
    for y in range(1, 9):
        for dx in (0, 1):
            w.setze(wx1 - dx, y, -b, w.b(["bricks", "stone_bricks", "cobblestone"][(y + dx) % 3]))
    w.setze(wx1 - 1, 1, -b + 1, w.b("blast_furnace", facing="south", lit=True))
    w.setze(wx1, 1, -b + 1, w.b("magma_block"))
    w.setze(wx1 - 1, 9, -b, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    w.setze(a, 1, 0, w.b("anvil", facing="north"))
    w.setze(a + 2, 1, 1, w.b("smithing_table"))
    w.setze(a + 2, 1, -1, w.b("grindstone", face="floor", facing="north"))
    for x in (a + 3, a + 4):
        w.setze(x, 1, b - 1, w.b("water_cauldron", level=3))
    w.setze(a - 1, 1, -b + 1, w.b("coal_block"))
    hohl(w, 2)
    return w


def baeckerei(seed, g=1):
    """Bäckerei mit großem Backofen-Anbau, rauchendem Schornstein, Brotauslage und Mehlsäcken."""
    w = _welt(seed)
    st = stil(w, seed, "fachwerk_ocker", "sand")
    u = U[g]
    a, b = _r(4 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 9, art="wiese", wege=[((0, b + 1), (0, b + 9))])
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="sattel", tuer="south", kamine=0)
    # Backofen (Kuppel aus Ziegeln)
    for x, z in scheibe(2.5, a + 3, 0):
        for y in range(1, 4):
            if math.hypot(x - a - 3, z) + (y - 1) * 0.6 < 2.8:
                w.setze(x, y, z, w.b(["bricks", "mud_bricks", "terracotta"][(x + y + z) % 3]))
    w.setze(a + 3, 1, 2, w.b("furnace", facing="south", lit=True))
    for y in range(4, 11):
        w.setze(a + 3, y, 0, w.b("bricks"))
    w.setze(a + 3, 11, 0, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for x in (-a + 1, -a + 2):
        w.setze(x, 1, b + 1, w.b("hay_block", axis="y"))
    w.setze(2, 1, b + 1, w.b("barrel", facing="up", open=True))
    w.setze(3, 1, b + 1, w.b("cake", bites=0) if False else w.b("composter", level=7))
    hohl(w, 2)
    return w


def kapelle(seed, g=1):
    """Dorfkapelle mit Dachreiter und Glocke, Spitzbogenfenstern, kleinem Friedhof mit Mauer und Linde."""
    w = _welt(seed)
    st = stil(w, seed, "kalk_kupfer", "stein_schiefer", fensterart="bogen", laeden=False, blumen=0)
    u = U[g]
    a, b = _r(2.5 * u + 2, 3), _r(5 * u + 3, 4)
    gelaende(w, b + 8, art="wiese", wege=[((0, b + 1), (0, b + 8))])
    top = P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1, eh=_r(6 * u + 2, 6), dach="sattel", first_x=False,
                     steil=True, tuer="south", gauben=False, kamine=0)
    P.turm(w, st, 0, b - 1, top - 2, _r(4 * u + 2, 3), 1.2, form="eckig", dach="nadel", krone=False, fahne=None)
    w.setze(0, top, b - 1, w.b("bell", attachment="ceiling", facing="north", powered=False))
    for x in range(-a - 6, a + 7):
        for z in (-b - 4,):
            w.setze(x, 1, z, w.b("mossy_cobblestone") if x % 2 else w.b("cobblestone"))
    for i in range(6):
        x, z = -a - 4 + (i % 3) * 2, -b + (i // 3) * 3
        w.setze(x, 1, z, w.b("cobblestone_wall", up=True, north="none", south="none", east="none", west="none",
                             waterlogged=False))
        w.setze(x, 0, z + 1, w.b("podzol", snowy=False))
    baum(w, a + 4, -b, "oak", H=8)
    hohl(w, 2)
    return w


def herrenhaus(seed, g=2):
    """Herrenhaus: Hauptbau mit zwei Seitenflügeln, Walmdächern, Freitreppe, Ehrenhof mit Brunnen, Allee."""
    w = _welt(seed)
    st = stil(w, seed, "marmor", "kalk_kupfer", fensterart="bogen")
    u = U[g]
    a, b = _r(6 * u + 3, 5), _r(3 * u + 2, 3)
    gelaende(w, a + 14, art="wiese", wege=[((0, b + 1), (0, a + 14))])
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2 + (g >= 2), eh=5, dach="walm", tuer="south", sockel_h=2,
               pilaster=3, kamine=2)
    for sx in (-1, 1):
        P.gebaeude(w, st, sx * (a + 1) if sx > 0 else -a - 1 - 2 * b, b + 1, sx * (a + 1 + 2 * b) if sx > 0 else -a - 1,
                   b + 2 + _r(6 * u + 3, 5), y0=1, etagen=2, eh=4, dach="walm", tuer="west" if sx > 0 else "east",
                   gauben=False)
    for z in range(b + 12, a + 14, 5):
        for sx in (-1, 1):
            baum(w, sx * 5, z, "oak", H=6)
    w.setze(0, 1, b + 8, w.b("water", level=0))
    for x, z in kreisrand(2, 0, b + 8):
        w.setze(x, 1, z, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    hohl(w, 2)
    return w


def chalet(seed, g=1):
    """Bergchalet: Steinsockel, Holzobergeschoss, weit überstehendes flaches Dach, Balkone mit Blumen."""
    w = _welt(seed)
    holz = "spruce" if _stil(seed) == 0 else "dark_oak"
    st_unten = P.Stil(w, wand="graustein", sockel="graustein", gesims="stone_brick", dach="schindel", holz=holz)
    st_oben = P.Stil(w, wand="holz_dunkel", sockel="graustein", gesims=holz, dach="schindel", holz=holz,
                     blumen=0.9)
    u = U[g]
    a, b = _r(4 * u + 3, 4), _r(3.5 * u + 2, 3)
    gelaende(w, a + 9, art="wiese")
    P.gebaeude(w, st_unten, -a, -b, a, b, y0=1, etagen=1, eh=4, dach="flach", tuer="south", gauben=False, kamine=0)
    P.gebaeude(w, st_oben, -a, -b, a, b, y0=5, etagen=1 + (g >= 2), eh=4, dach="sattel", ue=3, first_x=False,
               tuer="south", sockel_h=0, kamine=1)
    for x in range(-a - 1, a + 2):
        w.setze(x, 5, b + 1, w.b(f"{holz}_planks"))
        w.setze(x, 5, b + 2, w.b(f"{holz}_slab", type="top", waterlogged=False))
        w.setze(x, 6, b + 2, w.b(f"{holz}_fence", north=False, south=False, east=True, west=True, waterlogged=False))
        if x % 2 == 0:
            w.setze(x, 7, b + 2, laub(w, "flowering_azalea"))
    holzstapel(w, -a - 3, -b, 5, holz, "z")
    hohl(w, 2)
    return w


def fischerhaus(seed, g=1):
    """Fischerhaus am Wasser: Steg, Ruderboot, Fischernetz-Gestell, Fässer und Räucherkammer."""
    w = _welt(seed)
    st = stil(w, seed, "holz_hell", "putz_blau")
    u = U[g]
    a, b = _r(3 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 6, art="wiese")
    for x in range(-a - 10, a + 11):
        for z in range(b + 4, b + 16):
            w.setze(x, 0, z, w.b("water", level=0))
            w.setze(x, -1, z, w.b("sand"))
    for x in range(-a - 10, a + 11):
        for z in (b + 2, b + 3):
            w.setze(x, 0, z, w.b("sand"))
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=1 + (g >= 2), eh=4, dach="sattel", tuer="south", kamine=1)
    for z in range(b + 2, b + 12):
        for x in (2, 3, 4):
            w.setze(x, 1, z, w.b(f"{st.holz}_slab", type="bottom", waterlogged=False))
        if z % 3 == 0:
            w.setze(5, 0, z, w.b(f"{st.holz}_log", axis="y"))
            w.setze(5, 1, z, w.b(f"{st.holz}_fence", north=False, south=False, east=False, west=False,
                                 waterlogged=False))
    for x in range(-a - 4, -a - 1):
        w.setze(x, 1, 0, w.b(f"{st.holz}_fence", north=False, south=False, east=False, west=False, waterlogged=False))
        w.setze(x, 2, 0, w.b(f"{st.holz}_fence", north=False, south=False, east=False, west=False, waterlogged=False))
        w.setze(x, 3, 0, w.b("cobweb"))
    for k in range(2):
        w.setze(-a + k, 1, b + 2, w.b("barrel", facing="up", open=False))
    hohl(w, 2)
    return w


def rathaus(seed, g=2):
    """Rathaus mit Laubengang, Ratssaal-Fenstern, Uhrturm, Treppengiebel-Zier und Marktplatz mit Brunnen."""
    w = _welt(seed)
    st = stil(w, seed, "backstein", "kalk_kupfer", fensterart="bogen")
    u = U[g]
    a, b = _r(7 * u + 3, 5), _r(4 * u + 2, 4)
    gelaende(w, a + 10, art="wiese")
    from burgen import hofboden, rechteck
    hofboden(w, rechteck(-a - 4, b + 1, a + 4, b + 12), "pflaster")
    top = P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2 + (g >= 2), eh=5, dach="sattel", tuer="south", sockel_h=1,
                     pilaster=3, kamine=1)
    # Laubengang
    for x in range(-a, a + 1):
        if x % 3 == 0:
            for y in range(1, 5):
                w.setze(x, y, b + 3, st.sockel(x, y, b + 3, 0.5))
        for z in range(b + 1, b + 4):
            w.setze(x, 5, z, st.sockel(x, 5, z, 0.7))
    P.turm(w, st, 0, 0, top - 4, _r(10 * u + 4), max(1.6, 2.2 * u), form="eckig", dach="zwiebel", krone=False,
           fahne=None)
    w.setze(0, 1, b + 8, w.b("water", level=0))
    for x, z in kreisrand(2, 0, b + 8):
        w.setze(x, 1, z, w.b("stone_brick_slab", type="bottom", waterlogged=False))
    for x in (-a - 2, a + 2):
        laternenpfahl(w, x, b + 6, 3)
    hohl(w, 2)
    return w


def winzerhaus(seed, g=1):
    """Winzerhaus am Weinberg: Haus mit Kelterschuppen, Rebzeilen an Spalieren, Weinfässern und Laube."""
    w = _welt(seed)
    st = stil(w, seed, "sand", "fachwerk_rot")
    u = U[g]
    a, b = _r(3.5 * u + 2, 3), _r(3 * u + 2, 3)
    gelaende(w, a + 14, art="wiese")
    P.gebaeude(w, st, -a, -b, a, b, y0=1, etagen=2, eh=4, dach="walm", tuer="east", kamine=1)
    # Rebzeilen
    for i in range(_r(4 * u + 2, 3)):
        z = -b + i * 3
        for x in range(a + 4, a + 4 + _r(10 * u + 4, 8)):
            w.setze(x, 1, z, w.b(f"{st.holz}_fence", north=False, south=False, east=True, west=True, waterlogged=False))
            if w.rng.random() < 0.8:
                w.setze(x, 2, z, laub(w, "jungle" if (x + i) % 3 else "azalea"))
            if w.rng.random() < 0.15:
                w.setze(x, 1, z + 1, w.b("sweet_berry_bush", age=3))
            w.setze(x, 0, z + 1, w.b("coarse_dirt"))
    for k in range(4):
        w.setze(-a - 2, 1 + k // 2, -b + k % 2 * 2, w.b("barrel", facing="east", open=False))
    # Laube
    for x in range(-a, a + 1):
        for z in (b + 2, b + 5):
            if x in (-a, a):
                for y in (1, 2, 3):
                    w.setze(x, y, z, w.b(f"{st.holz}_fence", north=False, south=False, east=False, west=False,
                                         waterlogged=False))
        for z in range(b + 2, b + 6):
            w.setze(x, 4, z, laub(w, "flowering_azalea") if (x + z) % 2 else laub(w, "jungle"))
    bank(w, -1, b + 3, "south", st.holz)
    hohl(w, 2)
    return w


HAEUSER = {
    "fachwerkhaus": ("Fachwerkhaus", fachwerkhaus),
    "turmhaus": ("Turmhaus", turmhaus),
    "bauernhof": ("Bauernhof", bauernhof),
    "taverne": ("Taverne", taverne),
    "stadtvilla": ("Stadtvilla", stadtvilla),
    "pfahlhaus": ("Pfahlhaus", pfahlhaus),
    "blockhuette": ("Blockhütte", blockhuette),
    "gildenhaus": ("Gildenhaus", gildenhaus),
    "reihenhaeuser": ("Reihenhäuser", reihenhaeuser),
    "reetdachkate": ("Reetdachkate", reetdachkate),
    "baumhaus": ("Baumhaus", baumhaus),
    "kaufmannshaus": ("Kaufmannshaus", kaufmannshaus),
    "schmiede": ("Schmiede", schmiede),
    "baeckerei": ("Bäckerei", baeckerei),
    "kapelle": ("Dorfkapelle", kapelle),
    "herrenhaus": ("Herrenhaus", herrenhaus),
    "chalet": ("Bergchalet", chalet),
    "fischerhaus": ("Fischerhaus", fischerhaus),
    "rathaus": ("Rathaus", rathaus),
    "winzerhaus": ("Winzerhaus", winzerhaus),
}

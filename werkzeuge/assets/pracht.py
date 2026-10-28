"""Pracht-Baukasten: hochwertige Bauteile mit vielen Blocksorten, fleckigen Verläufen, Verwitterung und Tiefe.

- Mat: Wandmaterial aus 6–10 Blöcken; Auswahl über glattes 3D-Rauschen (Flecken statt Salz-und-Pfeffer),
  Höhenverlauf (unten dunkler/bemoost, oben heller) und seltene Akzentsteine.
- Dach: Treppen-Dächer aus mehreren Materialien (fleckig gemischt), mit Traufe, First und Giebelzier.
- gebaeude(): Fassaden mit Sockel, Eckquadern, Gesimsen, Fenstern mit Sohlbank, Verdachung und Läden,
  Pilastern, Kranzgesims, Sattel-/Walmdach, Gauben und Kamin.
- turm(): Rund-, Eck- oder Achteckturm mit Sockelanlauf, Gurtgesimsen, Fenstern, Kragsteinkranz, Zinnen
  und geschweiftem Helm mit Gauben, Spitze und Fahne.
- gelaende(): lebendiger Boden mit Wegen, Kies, Moos, Blumen-Inseln, Büschen und Findlingen.
"""

from __future__ import annotations

import math

from lib import Rauschen, Verlauf, laub
from skulptur import kreisrand, platte, scheibe, verbinde, zur_mitte


def _r(v, mind=1):
    return max(mind, int(round(v)))


# ============================================================================ Materialien

WAENDE = {
    "graustein": ["mossy_cobblestone", "cobblestone", "cracked_stone_bricks", "stone_bricks", "stone_bricks",
                  "stone", "andesite", "polished_andesite"],
    "tiefenschiefer": ["cobbled_deepslate", "cracked_deepslate_bricks", "deepslate_bricks", "deepslate_tiles",
                       "polished_deepslate", "deepslate_bricks", "tuff"],
    "sandstein": ["sandstone", "cut_sandstone", "sandstone", "smooth_sandstone", "cut_sandstone", "smooth_sandstone",
                  "end_stone"],
    "rotsandstein": ["red_sandstone", "cut_red_sandstone", "terracotta", "smooth_red_sandstone", "granite",
                     "red_sandstone", "polished_granite"],
    "kalkstein": ["tuff", "andesite", "diorite", "polished_diorite", "calcite", "smooth_quartz"],
    "marmor": ["polished_andesite", "diorite", "polished_diorite", "calcite", "smooth_quartz", "quartz_bricks",
               "white_concrete"],
    "backstein": ["mud_bricks", "packed_mud", "bricks", "bricks", "granite", "polished_granite", "bricks"],
    "schwarzstein": ["blackstone", "cracked_polished_blackstone_bricks", "polished_blackstone_bricks",
                     "polished_blackstone", "polished_blackstone_bricks", "basalt"],
    "putz": ["light_gray_terracotta", "white_terracotta", "white_terracotta", "diorite", "calcite", "smooth_quartz"],
    "ockerputz": ["brown_terracotta", "yellow_terracotta", "smooth_sandstone", "yellow_terracotta", "sandstone",
                  "end_stone"],
    "holz_dunkel": ["dark_oak_planks", "stripped_dark_oak_log", "spruce_planks", "dark_oak_planks",
                    "stripped_spruce_log"],
    "holz_hell": ["spruce_planks", "oak_planks", "stripped_oak_log", "oak_planks", "birch_planks"],
    "prismarin": ["dark_prismarine", "prismarine", "prismarine_bricks", "prismarine", "sea_lantern"],
    "netherziegel": ["nether_bricks", "cracked_nether_bricks", "nether_bricks", "red_nether_bricks",
                     "chiseled_nether_bricks"],
    "endstein": ["end_stone", "end_stone_bricks", "end_stone", "purpur_block", "end_stone_bricks"],
    "eis": ["blue_ice", "packed_ice", "packed_ice", "ice", "snow_block"],
    "moosstein": ["mossy_cobblestone", "cobblestone", "mossy_stone_bricks", "cracked_stone_bricks", "stone_bricks",
                  "andesite", "stone_bricks"],
    "lehm": ["packed_mud", "mud_bricks", "terracotta", "brown_terracotta", "mud_bricks"],
}

MOOS = {"graustein": ["mossy_cobblestone", "mossy_stone_bricks"], "tiefenschiefer": ["mossy_cobblestone"],
        "kalkstein": ["mossy_cobblestone"], "marmor": ["mossy_stone_bricks"], "backstein": ["mossy_stone_bricks"],
        "sandstein": [], "rotsandstein": [], "putz": ["mossy_cobblestone"]}

AKZENTE = {"graustein": ["chiseled_stone_bricks"], "tiefenschiefer": ["chiseled_deepslate"],
           "sandstein": ["chiseled_sandstone"], "rotsandstein": ["chiseled_red_sandstone"],
           "marmor": ["chiseled_quartz_block"], "schwarzstein": ["chiseled_polished_blackstone", "gilded_blackstone"],
           "netherziegel": ["chiseled_nether_bricks"], "kalkstein": ["chiseled_stone_bricks"],
           "backstein": ["chiseled_stone_bricks"]}

CHIPPED_BASIS = {"graustein": "stone_bricks", "tiefenschiefer": "deepslate_bricks", "sandstein": "sandstone",
                 "rotsandstein": "red_sandstone", "backstein": "bricks", "schwarzstein": "polished_blackstone_bricks",
                 "marmor": "quartz_bricks", "kalkstein": "stone_bricks", "moosstein": "mossy_stone_bricks",
                 "netherziegel": "nether_bricks", "endstein": "end_stone_bricks", "prismarin": "prismarine_bricks",
                 "lehm": "mud_bricks"}

# Treppen-Material → vollständiger Block
VOLL = {"brick": "bricks", "mud_brick": "mud_bricks", "deepslate_tile": "deepslate_tiles",
        "deepslate_brick": "deepslate_bricks", "stone_brick": "stone_bricks",
        "polished_blackstone_brick": "polished_blackstone_bricks", "prismarine_brick": "prismarine_bricks",
        "nether_brick": "nether_bricks", "red_nether_brick": "red_nether_bricks", "end_stone_brick": "end_stone_bricks",
        "mossy_stone_brick": "mossy_stone_bricks", "quartz": "quartz_block", "purpur": "purpur_block"}
HOELZER = ("oak", "spruce", "dark_oak", "birch", "jungle", "acacia", "mangrove", "cherry", "crimson", "warped",
           "bamboo")


def voll(mat):
    if mat in VOLL:
        return VOLL[mat]
    if mat in HOELZER:
        return f"{mat}_planks"
    return mat


DAECHER = {
    "schiefer": ["deepslate_tile", "deepslate_tile", "deepslate_brick", "cobbled_deepslate", "polished_deepslate"],
    "ziegel": ["brick", "brick", "mud_brick", "granite", "polished_granite"],
    "kupfer": ["waxed_oxidized_cut_copper", "waxed_weathered_cut_copper", "waxed_oxidized_cut_copper",
               "waxed_exposed_cut_copper"],
    "jungkupfer": ["waxed_cut_copper", "waxed_exposed_cut_copper", "waxed_cut_copper", "waxed_weathered_cut_copper"],
    "schindel": ["spruce", "dark_oak", "spruce", "oak"],
    "dunkelholz": ["dark_oak", "dark_oak", "spruce", "mangrove"],
    "blau": ["dark_prismarine", "prismarine_brick", "dark_prismarine", "prismarine"],
    "sand": ["smooth_sandstone", "sandstone", "smooth_sandstone"],
    "rotsand": ["smooth_red_sandstone", "red_sandstone", "smooth_red_sandstone"],
    "quarz": ["quartz", "smooth_quartz", "quartz"],
    "nether": ["nether_brick", "red_nether_brick", "nether_brick"],
    "schwarz": ["polished_blackstone", "polished_blackstone_brick", "blackstone"],
    "purpur": ["purpur", "purpur", "end_stone_brick"],
    "moos": ["mossy_cobblestone", "mossy_stone_brick", "cobblestone"],
    "grau": ["stone_brick", "cobblestone", "andesite", "polished_andesite", "stone"],
    # Macaw's Roofs (Mod) – fallen ohne Mod automatisch auf Vanilla-Treppen zurück
    "mcw_ziegel": ["mcw:red_terracotta", "mcw:red_terracotta", "mcw:brown_terracotta", "mcw:orange_terracotta"],
    "mcw_stroh": ["mcw:thatch"],
    "mcw_schiefer": ["mcw:deepslate", "mcw:gray_terracotta", "mcw:deepslate"],
    "mcw_gruen": ["mcw:green_terracotta", "mcw:green_terracotta", "mcw:lime_terracotta"],
    "mcw_blau": ["mcw:blue_terracotta", "mcw:light_blue_terracotta", "mcw:blue_terracotta"],
    "mcw_schwarz": ["mcw:black_terracotta", "mcw:blackstone", "mcw:black_terracotta"],
    "mcw_braun": ["mcw:brown_terracotta", "mcw:spruce", "mcw:brown_terracotta"],
    "mcw_holz": ["mcw:spruce", "mcw:dark_oak", "mcw:spruce"],
    "mcw_stein": ["mcw:stone_bricks", "mcw:cobblestone", "mcw:stone"],
    "mcw_weiss": ["mcw:white_terracotta", "mcw:white_concrete"],
    "mcw_gelb": ["mcw:yellow_terracotta", "mcw:orange_terracotta"],
    "mcw_rot": ["mcw:red_nether_bricks", "mcw:red_terracotta"],
    "mcw_lila": ["mcw:purple_terracotta", "mcw:magenta_terracotta", "mcw:purple_concrete", "mcw:purple_terracotta"],
    # Twigs-Schindeln (Mod)
    "schindel_rot": ["silt:red", "silt:brown", "silt:red", "silt:orange"],
    "schindel_blau": ["silt:blue", "silt:cyan", "silt:blue", "silt:light_blue"],
    "schindel_gruen": ["silt:green", "silt:lime", "silt:green"],
    "schindel_grau": ["silt:gray", "silt:light_gray", "silt:black"],
    "schindel_lila": ["silt:purple", "silt:magenta", "silt:purple", "silt:black"],
}


class Mat:
    """Wandmaterial mit fleckiger Mischung, Höhenverlauf, Moos unten und seltenen Akzenten."""

    def __init__(self, w, art, zelle=3.2, kontrast=1.0, moos=0.35, akzent=0.02, hell=0.0):
        self.w = w
        bl = WAENDE.get(art, [art]) if isinstance(art, str) else list(art)
        self.n = len(bl)
        self.v = Verlauf(w, f"W{id(self)}", bl)
        self.r1 = Rauschen(w, zelle)
        self.r2 = Rauschen(w, max(1.2, zelle * 0.38))
        self.kontrast = kontrast
        name = art if isinstance(art, str) else ""
        self.moos = [w.b(b) for b in MOOS.get(name, [])]
        self.moos_p = moos
        self.akz = [w.b(b) for b in AKZENTE.get(name, [])]
        self.akz_p = akzent
        # Zierblöcke aus Chipped (falls vorhanden) – mit dem Grundblock als Ersatz
        basis = CHIPPED_BASIS.get(name)
        if basis:
            import modbloecke as MB
            var = MB.chipped_varianten(basis)
            if var:
                wahl = [var[int(w.rng.integers(len(var)))] for _ in range(3)]
                self.akz += [MB.mod(w, n, basis) for n in wahl]
                self.akz_p = max(self.akz_p, 0.03)
        self.hell = hell

    def __call__(self, x, y, z, t=0.5):
        """t: 0 (unten) … 1 (oben) – steuert den Verlauf."""
        rng = self.w.rng
        if self.moos and t < 0.18 and rng.random() < self.moos_p * (1 - t / 0.18) * (0.5 + self.r1(x * 2, y, z * 2)):
            return self.moos[int(rng.integers(len(self.moos)))]
        if self.akz and rng.random() < self.akz_p:
            return self.akz[int(rng.integers(len(self.akz)))]
        v = (self.n - 1) * (0.12 + 0.62 * t + self.hell) + (self.r1(x, y, z) - 0.5) * 2.6 * self.kontrast \
            + (self.r2(x, y, z) - 0.5) * 1.1
        return self.v(v, x, y, z)


class Dach:
    """Dachmaterial aus mehreren Treppensorten, fleckig gemischt."""

    def __init__(self, w, art, zelle=2.6):
        self.w = w
        self.mats = DAECHER.get(art, [art]) if isinstance(art, str) else list(art)
        self.r = Rauschen(w, zelle)
        self.r2 = Rauschen(w, 1.1)

    def mat(self, x, y, z):
        v = self.r(x, y, z) * 0.75 + self.r2(x, y, z) * 0.25
        return self.mats[min(len(self.mats) - 1, int(v * len(self.mats) * 1.05))]

    def treppe(self, x, y, z, facing, half="bottom"):
        m = self.mat(x, y, z)
        if ":" in m:
            import modbloecke as MB
            return MB.dach_treppe(self.w, m, facing, half)
        return self.w.b(f"{m}_stairs", facing=facing, half=half, shape="straight", waterlogged=False)

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
        return self.w.b(f"{m}_slab", type=typ, waterlogged=False)


def treppe(w, mat, facing, half="bottom"):
    return w.b(f"{mat}_stairs", facing=facing, half=half, shape="straight", waterlogged=False)


def _aussen(x, z, x0, z0, x1, z1):
    """Richtung nach außen für eine Randzelle eines Rechtecks."""
    if z == z0:
        return 0, -1, "north"
    if z == z1:
        return 0, 1, "south"
    if x == x0:
        return -1, 0, "west"
    return 1, 0, "east"


GEGEN = {"north": "south", "south": "north", "east": "west", "west": "east"}


# ============================================================================ Stil-Paket

class Stil:
    """Alles, was ein Gebäude an Materialien braucht."""

    def __init__(self, w, wand="graustein", sockel=None, ecke=None, gesims="stone_brick", dach="schiefer",
                 holz="spruce", fenster="glass_pane", laeden=True, blumen=0.5, fachwerk=False, balken=None,
                 fensterart="rechteck", fensterrahmen=None, kamin="bricks", licht="lantern", zier=None):
        self.w = w
        self.wand = wand if isinstance(wand, Mat) else Mat(w, wand)
        self.sockel = sockel if isinstance(sockel, Mat) else Mat(w, sockel or "graustein", kontrast=0.8, hell=-0.1)
        self.ecke = ecke
        self.gesims = gesims
        self.dach = dach if isinstance(dach, Dach) else Dach(w, dach)
        self.holz = holz
        self.fenster = fenster
        self.laeden = laeden
        self.blumen = blumen
        self.fachwerk = fachwerk
        self.balken = balken or f"stripped_{holz}_log"
        self.fensterart = fensterart
        self.fensterrahmen = fensterrahmen
        self.kamin = kamin
        self.licht = licht
        self.zier = zier or gesims


def _glas(w, st, rz):
    if st.fenster.endswith("_pane"):
        return w.b(st.fenster, east=rz, west=rz, north=not rz, south=not rz, waterlogged=False)
    return w.b(st.fenster)


# ============================================================================ Gebäude

def gebaeude(w, st, x0, z0, x1, z1, y0=0, etagen=2, eh=4, dach="sattel", ue=1, first_x=None, tuer="south",
             sockel_h=1, pilaster=0, gauben=True, kamine=1, fenster_abstand=3, steil=False):
    """Prächtiges Gebäude. Gibt die Firsthöhe zurück."""
    rng = w.rng
    H = sockel_h + etagen * eh
    yt = y0 + H
    # Sockel mit Anlauf
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            rand = x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1)
            if rand:
                if (x in (x0 - 1, x1 + 1)) and (z in (z0 - 1, z1 + 1)):
                    w.setze(x, y0, z, st.sockel(x, y0, z, 0.0))
                else:
                    dx, dz, aus = _aussen(x, z, x0 - 1, z0 - 1, x1 + 1, z1 + 1)
                    w.setze(x, y0, z, treppe(w, st.gesims, GEGEN[aus]))
    for y in range(y0, yt):
        t = (y - y0) / max(1, H)
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                rx, rz = x in (x0, x1), z in (z0, z1)
                if not (rx or rz):
                    if y == y0 or (y - y0 - sockel_h) % eh == eh - 1:
                        w.setze(x, y, z, w.b(f"{st.holz}_planks"))
                    continue
                if y < y0 + sockel_h:
                    w.setze(x, y, z, st.sockel(x, y, z, 0.1))
                    continue
                stufe = (y - y0 - sockel_h) % eh
                ecke = rx and rz
                if ecke:
                    if st.ecke:
                        w.setze(x, y, z, w.b(st.ecke[(y // 1) % len(st.ecke)]))
                    elif st.fachwerk:
                        w.setze(x, y, z, w.b(st.balken, axis="y"))
                    else:
                        w.setze(x, y, z, st.wand(x, y, z, min(1, t + 0.15)))
                    continue
                tt = (x - x0) if rz else (z - z0)
                lang = (x1 - x0) if rz else (z1 - z0)
                if st.fachwerk and stufe == eh - 1:
                    w.setze(x, y, z, w.b(st.balken, axis="x" if rz else "z"))
                    continue
                if st.fachwerk and tt % fenster_abstand == 0:
                    w.setze(x, y, z, w.b(st.balken, axis="y"))
                    continue
                w.setze(x, y, z, st.wand(x, y, z, t))
        # Geschossgesims
        if y > y0 + sockel_h and (y - y0 - sockel_h) % eh == 0 and not st.fachwerk:
            for x in range(x0 - 1, x1 + 2):
                for z in range(z0 - 1, z1 + 2):
                    if (x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1)) and not (x in (x0 - 1, x1 + 1) and z in (z0 - 1, z1 + 1)):
                        dx, dz, aus = _aussen(x, z, x0 - 1, z0 - 1, x1 + 1, z1 + 1)
                        w.setze(x, y - 1, z, treppe(w, st.gesims, GEGEN[aus], "top"), ueberschreiben=False)
    # Fenster mit Sohlbank, Verdachung, Läden, Blumen
    for e in range(etagen):
        yb = y0 + sockel_h + e * eh + 1
        hoch = 2 if eh >= 4 else 1
        for (seite, xs, zs) in (("south", range(x0, x1 + 1), [z1]), ("north", range(x0, x1 + 1), [z0]),
                                ("west", [x0], range(z0, z1 + 1)), ("east", [x1], range(z0, z1 + 1))):
            rz = seite in ("north", "south")
            for x in xs:
                for z in zs:
                    tt = (x - x0) if rz else (z - z0)
                    lang = (x1 - x0) if rz else (z1 - z0)
                    if not (1 < tt < lang - 1) or tt % fenster_abstand != fenster_abstand // 2 + (fenster_abstand % 2 == 0):
                        continue
                    if e == 0 and seite == tuer and abs(tt - lang // 2) <= 1:
                        continue
                    dx, dz = {"south": (0, 1), "north": (0, -1), "west": (-1, 0), "east": (1, 0)}[seite]
                    for k in range(hoch):
                        w.setze(x, yb + k, z, _glas(w, st, rz))
                    if st.fensterart == "bogen" and eh >= 5:
                        w.setze(x, yb + hoch, z, _glas(w, st, rz))
                    oben = yb + hoch + (1 if st.fensterart == "bogen" and eh >= 5 else 0)
                    w.setze(x + dx, yb - 1, z + dz, treppe(w, st.gesims, GEGEN[seite], "top"), ueberschreiben=False)
                    if oben < y0 + sockel_h + (e + 1) * eh - 1 or not st.fachwerk:
                        w.setze(x + dx, oben, z + dz, treppe(w, st.gesims, GEGEN[seite]), ueberschreiben=False)
                    if st.fensterrahmen:
                        w.setze(x, oben, z, w.b(st.fensterrahmen))
                    if st.laeden:
                        sx, sz = (1, 0) if rz else (0, 1)
                        for s in (-1, 1):
                            for k in range(hoch):
                                w.setze(x + dx + s * sx, yb + k, z + dz + s * sz,
                                        w.b(f"{st.holz}_trapdoor", facing=seite, half="bottom", open=True,
                                            powered=False, waterlogged=False), ueberschreiben=False)
                    if st.blumen and rng.random() < st.blumen and e > 0:
                        w.setze(x + dx, yb - 1, z + dz, laub(w, "flowering_azalea"))
    # Pilaster
    if pilaster:
        for x in range(x0 + pilaster, x1, pilaster):
            for z, dz, f in ((z0 - 1, -1, "south"), (z1 + 1, 1, "north")):
                for y in range(y0 + sockel_h, yt):
                    if w.frei(x, y, z):
                        w.setze(x, y, z, st.sockel(x, y, z, 0.6))
                w.setze(x, yt, z, treppe(w, st.gesims, f), ueberschreiben=False)
    # Kranzgesims
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            if (x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1)) and not (x in (x0 - 1, x1 + 1) and z in (z0 - 1, z1 + 1)):
                dx, dz, aus = _aussen(x, z, x0 - 1, z0 - 1, x1 + 1, z1 + 1)
                w.setze(x, yt - 1, z, treppe(w, st.gesims, GEGEN[aus], "top"))
    # Tür mit Laternen und Vordach
    mx, mz = (x0 + x1) // 2, (z0 + z1) // 2
    tx, tz = {"south": (mx, z1), "north": (mx, z0), "east": (x1, mz), "west": (x0, mz)}[tuer]
    dx, dz = {"south": (0, 1), "north": (0, -1), "west": (-1, 0), "east": (1, 0)}[tuer]
    for yy, half in ((y0 + sockel_h, "lower"), (y0 + sockel_h + 1, "upper")):
        w.setze(tx, yy, tz, w.b(f"{st.holz}_door", facing=tuer, half=half, hinge="left", open=False, powered=False))
    w.setze(tx, y0 + sockel_h + 2, tz, w.b(st.zier if st.zier.startswith("chiseled") else "chiseled_stone_bricks"))
    sx, sz = (1, 0) if tuer in ("north", "south") else (0, 1)
    for s in (-1, 1):
        w.setze(tx + dx + s * sx * 2, y0 + sockel_h + 2, tz + dz + s * sz * 2,
                w.b(st.licht, hanging=False, waterlogged=False) if st.licht.endswith("lantern") else w.b(st.licht),
                ueberschreiben=False)
    if sockel_h > 0:
        for k in range(sockel_h):
            for s in (-1, 0, 1):
                w.setze(tx + dx * (k + 1) + s * sx, y0 + sockel_h - 1 - k, tz + dz * (k + 1) + s * sz,
                        treppe(w, st.gesims, GEGEN[tuer]))
    # Dach
    if dach == "sattel":
        top = satteldach(w, st.dach, x0, z0, x1, z1, yt, ue, first_x, st.wand, steil=steil)
    elif dach == "walm":
        top = walmdach(w, st.dach, x0, z0, x1, z1, yt, ue, steil=steil)
    elif dach == "mansarde":
        top = walmdach(w, st.dach, x0, z0, x1, z1, yt, ue, mansarde=2)
    else:
        top = flachdach(w, st, x0, z0, x1, z1, yt)
    # Gauben auf großen Dächern
    if gauben and dach in ("sattel", "walm", "mansarde") and max(x1 - x0, z1 - z0) >= 9:
        fx = first_x if first_x is not None else (x1 - x0) >= (z1 - z0)
        for i in range(x0 + 3, x1 - 2, 5) if fx else range(z0 + 3, z1 - 2, 5):
            for seite in (-1, 1):
                if fx:
                    z = z0 + 1 if seite < 0 else z1 - 1
                    gaube(w, st, i, yt + 1 + (1 if dach != "sattel" else 1), z, "north" if seite < 0 else "south")
                else:
                    x = x0 + 1 if seite < 0 else x1 - 1
                    gaube(w, st, x, yt + 2, i, "west" if seite < 0 else "east")
    for k in range(kamine):
        kx = x0 + 1 + k * max(1, (x1 - x0 - 2))
        kamin(w, st, kx, z0 + 1, yt - 1, top + 1)
    return top


def satteldach(w, D, x0, z0, x1, z1, yt, ue=1, first_x=None, wand=None, steil=False):
    if first_x is None:
        first_x = (x1 - x0) >= (z1 - z0)
    k = 0
    y = yt
    while True:
        if first_x:
            a, b = z0 - ue + k, z1 + ue - k
        else:
            a, b = x0 - ue + k, x1 + ue - k
        if a > b:
            break
        lagen = 2 if steil else 1
        for lage in range(lagen):
            y += 1
            reihe = range(x0 - ue, x1 + ue + 1) if first_x else range(z0 - ue, z1 + ue + 1)
            for q in reihe:
                pa = (q, y, a) if first_x else (a, y, q)
                pb = (q, y, b) if first_x else (b, y, q)
                if a == b:
                    w.setze(*pa, D.voll(*pa))
                    continue
                if steil and lage == 0:
                    w.setze(*pa, D.voll(*pa))
                    w.setze(*pb, D.voll(*pb))
                else:
                    w.setze(*pa, D.treppe(*pa, "south" if first_x else "east"))
                    w.setze(*pb, D.treppe(*pb, "north" if first_x else "west"))
            # Giebel füllen
            for q in ((x0, x1) if first_x else (z0, z1)):
                for r in range(a + 1, b):
                    p = (q, y, r) if first_x else (r, y, q)
                    lim = (z0 <= r <= z1) if first_x else (x0 <= r <= x1)
                    if lim and wand is not None:
                        w.setze(*p, wand(*p, 0.95))
        # Traufe unten: umgedrehte Treppen unter dem Überstand
        if k == 0 and ue > 0:
            reihe = range(x0 - ue, x1 + ue + 1) if first_x else range(z0 - ue, z1 + ue + 1)
            for q in reihe:
                for (r, f) in ((a, "north" if first_x else "west"), (b, "south" if first_x else "east")):
                    p = (q, yt, r) if first_x else (r, yt, q)
                    w.setze(*p, D.treppe(*p, GEGEN[f], "top"), ueberschreiben=False)
        k += 1
    # Giebelzier an beiden Enden
    if first_x:
        for xe in (x0 - ue, x1 + ue):
            zm = (z0 + z1) // 2
            w.setze(xe, y + 1, zm, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    else:
        for ze in (z0 - ue, z1 + ue):
            xm = (x0 + x1) // 2
            w.setze(xm, y + 1, ze, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
    return y


def walmdach(w, D, x0, z0, x1, z1, yt, ue=1, steil=False, mansarde=0):
    k = 0
    lage = 0
    y = yt
    while True:
        ax, bx, az, bz = x0 - ue + k, x1 + ue - k, z0 - ue + k, z1 + ue - k
        if ax > bx or az > bz:
            break
        y += 1
        for x in range(ax, bx + 1):
            for z in range(az, bz + 1):
                if not (x in (ax, bx) or z in (az, bz)):
                    continue
                if ax == bx or az == bz:
                    w.setze(x, y, z, D.voll(x, y, z))
                elif lage < mansarde:
                    w.setze(x, y, z, D.voll(x, y, z))
                elif z == az:
                    w.setze(x, y, z, D.treppe(x, y, z, "south"))
                elif z == bz:
                    w.setze(x, y, z, D.treppe(x, y, z, "north"))
                elif x == ax:
                    w.setze(x, y, z, D.treppe(x, y, z, "east"))
                else:
                    w.setze(x, y, z, D.treppe(x, y, z, "west"))
        if k == 0 and ue > 0:
            for x in range(ax, bx + 1):
                for z in range(az, bz + 1):
                    if (x in (ax, bx) or z in (az, bz)) and not (x in (ax, bx) and z in (az, bz)):
                        f = "north" if z == az else "south" if z == bz else "west" if x == ax else "east"
                        w.setze(x, yt, z, D.treppe(x, yt, z, GEGEN[f], "top"), ueberschreiben=False)
        if lage >= mansarde and not (steil and lage % 2 == 0):
            k += 1
        lage += 1
    return y


def flachdach(w, st, x0, z0, x1, z1, yt):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.setze(x, yt, z, st.sockel(x, yt, z, 0.7))
            if (x in (x0, x1) or z in (z0, z1)) and (x + z) % 2 == 0:
                w.setze(x, yt + 1, z, st.wand(x, yt + 1, z, 0.9))
    return yt + 1


def gaube(w, st, x, y, z, seite):
    """Dachgaube: kleines Fenster mit eigenem Mini-Satteldach."""
    dx, dz = {"south": (0, 1), "north": (0, -1), "west": (-1, 0), "east": (1, 0)}[seite]
    sx, sz = (1, 0) if seite in ("north", "south") else (0, 1)
    for s in (-1, 0, 1):
        for k in range(2):
            p = (x + s * sx, y + k, z + s * sz)
            w.setze(*p, _glas(w, st, seite in ("north", "south")) if s == 0 else st.wand(*p, 0.9))
        p = (x + s * sx + dx, y - 1, z + s * sz + dz)
        w.setze(*p, st.dach.treppe(*p, GEGEN[seite], "top"), ueberschreiben=False)
    for s in (-1, 1):
        p = (x + s * sx, y + 2, z + s * sz)
        w.setze(*p, st.dach.treppe(*p, {(-1, 1, 0): "east", (1, 1, 0): "west", (-1, 0, 1): "south",
                                        (1, 0, 1): "north"}[(s, sx, sz)]))
    w.setze(x, y + 2, z, st.dach.voll(x, y + 2, z))
    w.setze(x, y + 3, z, st.dach.platte(x, y + 3, z))


def kamin(w, st, x, z, y0, y1):
    kam = Mat(w, ["bricks", "mud_bricks", "bricks", "granite"] if st.kamin == "bricks" else [st.kamin], kontrast=0.6)
    for y in range(y0, y1 + 2):
        w.setze(x, y, z, kam(x, y, z, 0.5))
    w.setze(x, y1 + 2, z, w.b("campfire", lit=True, signal_fire=False, facing="north", waterlogged=False))
    for dx, dz, f in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
        w.setze(x + dx, y1 + 1, z + dz, treppe(w, "stone_brick", f, "top"), ueberschreiben=False)


# ============================================================================ Türme

def turm(w, st, cx, cz, y0, H, R, form="rund", dach="kegel", krone=True, fenster=6, dach_h=None,
         gauben=True, fahne=None, spitze="lightning_rod", schiessscharten=True):
    """Turm mit Sockelanlauf, Gurtgesimsen, Fenstern, Kragsteinkranz, Zinnen und Helm. Gibt die Spitze zurück."""

    def dist(x, z):
        dx, dz = x - cx, z - cz
        if form == "rund":
            return math.hypot(dx, dz)
        if form == "eckig":
            return max(abs(dx), abs(dz))
        return max(abs(dx), abs(dz), (abs(dx) + abs(dz)) / 1.42)

    def ring(r):
        n = int(r) + 2
        innen = [(x, z) for x in range(cx - n, cx + n + 1) for z in range(cz - n, cz + n + 1) if dist(x, z) <= r + 0.45]
        s = set(innen)
        return [(x, z) for (x, z) in innen if any((x + a, z + b) not in s for a in (-1, 0, 1) for b in (-1, 0, 1))], innen

    rand0, innen0 = ring(R)
    # Sockelanlauf
    for x, z in ring(R + 1)[0]:
        w.setze(x, y0, z, treppe(w, st.gesims, zur_mitte(x, z, cx, cz)))
    for y in range(y0, y0 + H):
        t = (y - y0) / max(1, H)
        for x, z in innen0:
            if (x, z) in set(rand0):
                a = math.atan2(z - cz, x - cx)
                hy = y - y0
                fen = fenster and hy % fenster in (fenster // 2, fenster // 2 + 1) and hy > 2 and \
                    abs(math.sin(2 * a)) < 0.16
                schlitz = schiessscharten and hy % fenster == 1 and hy > 3 and abs(math.cos(2 * a)) < 0.12
                if fen:
                    w.setze(x, y, z, _glas(w, st, abs(z - cz) >= abs(x - cx)))
                elif schlitz:
                    w.setze(x, y, z, w.b("iron_bars", north=False, south=False, east=False, west=False,
                                         waterlogged=False))
                else:
                    w.setze(x, y, z, st.wand(x, y, z, t) if y > y0 else st.sockel(x, y, z, 0.1))
            elif y == y0 or (y - y0) % 6 == 5:
                w.setze(x, y, z, w.b(f"{st.holz}_planks"))
        # Gurtgesims
        if (y - y0) % 8 == 7 and y < y0 + H - 3:
            for x, z in ring(R + 1)[0]:
                w.setze(x, y, z, treppe(w, st.gesims, zur_mitte(x, z, cx, cz), "top"), ueberschreiben=False)
    yt = y0 + H
    if krone:
        rk, _ = ring(R + 1)
        for x, z in rk:
            w.setze(x, yt - 1, z, treppe(w, st.gesims, zur_mitte(x, z, cx, cz), "top"))
        for x, z in ring(R + 1)[1]:
            w.setze(x, yt, z, st.sockel(x, yt, z, 0.7))
        for i, (x, z) in enumerate(rk):
            if i % 2 == 0:
                w.setze(x, yt + 1, z, st.wand(x, yt + 1, z, 0.9))
            else:
                w.setze(x, yt + 1, z, w.b(f"{st.gesims}_wall" if st.gesims in ("stone_brick", "mossy_stone_brick",
                                                                                 "deepslate_brick", "polished_blackstone_brick",
                                                                                 "nether_brick", "red_nether_brick",
                                                                                 "end_stone_brick", "sandstone",
                                                                                 "red_sandstone", "brick", "mud_brick")
                                          else "stone_brick_wall", up=True, north="none", south="none", east="none",
                                          west="none", waterlogged=False))
        yt += 1
    Rd = R + (1.3 if krone else 0.6)
    spitze_y = yt
    if dach in ("kegel", "glocke", "pyramide", "nadel"):
        dh = dach_h or _r(Rd * (3.2 if dach == "nadel" else 2.3), 3)
        for k in range(dh + 1):
            tt = k / (dh + 1)
            if dach == "glocke":
                r = Rd * (1 - tt) ** 0.75 + (0.8 if k == 0 else 0)
            elif dach == "nadel":
                r = Rd * (1 - tt) ** 1.4
            else:
                r = Rd * (1 - tt)
            if dach == "pyramide" or form == "eckig":
                rr = int(round(r))
                for x in range(cx - rr, cx + rr + 1):
                    for z in range(cz - rr, cz + rr + 1):
                        if max(abs(x - cx), abs(z - cz)) == rr:
                            p = (x, yt + k, z)
                            f = zur_mitte(x, z, cx, cz)
                            w.setze(*p, st.dach.treppe(*p, f) if rr > 0 and (abs(x - cx) != abs(z - cz)) else st.dach.voll(*p))
            else:
                for x, z in kreisrand(max(0.3, r), cx, cz):
                    p = (x, yt + k, z)
                    w.setze(*p, st.dach.voll(*p))
        spitze_y = yt + dh + 1
        if gauben and Rd >= 2.5 and dh >= 6:
            for a in (0.3, 2.4, 4.5):
                gx, gz = round(cx + math.cos(a) * Rd * 0.75), round(cz + math.sin(a) * Rd * 0.75)
                gy = yt + int(dh * 0.18)
                w.setze(gx, gy, gz, _glas(w, st, True))
                w.setze(gx, gy + 1, gz, st.dach.platte(gx, gy + 1, gz))
    elif dach == "kuppel":
        Rk = Rd
        for x in range(cx - int(Rk) - 1, cx + int(Rk) + 2):
            for z in range(cz - int(Rk) - 1, cz + int(Rk) + 2):
                for y in range(0, int(Rk) + 2):
                    d = ((x - cx) / (Rk + 0.4)) ** 2 + ((z - cz) / (Rk + 0.4)) ** 2 + (y / (Rk + 0.4)) ** 2
                    if 0.6 < d <= 1:
                        w.setze(x, yt + y, z, st.dach.voll(x, yt + y, z))
        spitze_y = yt + int(Rk) + 1
    elif dach == "zwiebel":
        Hz = Rd * 2.6
        for y in range(int(Hz) + 1):
            tt = y / Hz
            r = Rd * 1.2 * math.sin(math.pi * min(1, tt * 1.15)) ** 0.8 if tt < 0.87 else Rd * 0.25 * (1 - (tt - 0.87) / 0.13)
            for x, z in scheibe(max(0.3, r), cx, cz):
                if math.hypot(x - cx, z - cz) > r - 1.2:
                    w.setze(x, yt + y, z, st.dach.voll(x, yt + y, z))
        spitze_y = yt + int(Hz) + 1
    else:  # "platt": Wehrplattform mit Feuer
        w.setze(cx, yt, cz, w.b("campfire", lit=True, signal_fire=True, facing="north", waterlogged=False))
        spitze_y = yt
    if dach != "platt":
        if spitze == "lightning_rod":
            w.setze(cx, spitze_y, cz, w.b("lightning_rod", facing="up", powered=False, waterlogged=False))
        elif spitze:
            w.setze(cx, spitze_y, cz, w.b(spitze))
        if fahne:
            for k in range(2):
                w.setze(cx, spitze_y + 1 + k, cz, w.b(f"{st.holz}_fence", north=False, south=False, east=False,
                                                      west=False, waterlogged=False))
            for k in range(max(2, int(R))):
                for d in range(2):
                    w.setze(cx + 1 + k, spitze_y + 2 - d, cz, w.b(fahne[(k + d) % len(fahne)]))
    return spitze_y


# ============================================================================ Gelände & Kleinkram

def gelaende(w, R, cx=0, cz=0, art="wiese", wege=None, dichte=1.0):
    """Lebendiger Boden: Gras/Erde/Moos-Flecken, Kies, Blumeninseln, Büsche, Findlinge.
    wege: Liste von ((x0, z0), (x1, z1)) – gekieste/gepflasterte Wege."""
    r1 = Rauschen(w, 5)
    r2 = Rauschen(w, 2)
    rng = w.rng
    if art == "wiese":
        flaechen = [("grass_block", 0.62), ("podzol", 0.05), ("coarse_dirt", 0.03), ("moss_block", 0.05),
                    ("grass_block", 0.25)]
        blumen = ["poppy", "dandelion", "oxeye_daisy", "azure_bluet", "cornflower", "allium", "red_tulip"]
        streu = ["grass", "grass", "fern", "grass"]
    elif art == "wald":
        flaechen = [("podzol", 0.35), ("grass_block", 0.3), ("moss_block", 0.15), ("coarse_dirt", 0.1),
                    ("rooted_dirt", 0.1)]
        blumen = ["lily_of_the_valley", "fern", "brown_mushroom", "red_mushroom"]
        streu = ["fern", "grass", "large_fern" if False else "fern"]
    elif art == "sand":
        flaechen = [("sand", 0.6), ("sandstone", 0.1), ("red_sand", 0.1), ("gravel", 0.05), ("sand", 0.15)]
        blumen = ["dead_bush"]
        streu = ["dead_bush"]
    elif art == "schnee":
        flaechen = [("snow_block", 0.7), ("packed_ice", 0.08), ("powder_snow" if False else "snow_block", 0.12),
                    ("stone", 0.1)]
        blumen = []
        streu = []
    elif art == "asche":
        flaechen = [("blackstone", 0.3), ("basalt", 0.25), ("smooth_basalt", 0.2), ("tuff", 0.15), ("magma_block", 0.1)]
        blumen = []
        streu = []
    else:  # stein
        flaechen = [("stone", 0.3), ("andesite", 0.2), ("gravel", 0.15), ("cobblestone", 0.15), ("moss_block", 0.1),
                    ("tuff", 0.1)]
        blumen = []
        streu = ["grass"]
    kum = []
    s = 0
    for n, p in flaechen:
        s += p
        kum.append((s, n))
    wegzellen = set()
    for (a, b) in (wege or []):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for i in range(n + 1):
            t = i / n
            x, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            for d in (-1, 0, 1):
                wegzellen.add((round(x + d * 0.5), round(z + d * 0.5)))
    for x, z in scheibe(R, cx, cz):
        if not w.frei(x, 0, z):
            continue
        if (x, z) in wegzellen:
            v = r2(x, 0, z)
            w.setze(x, 0, z, w.b("dirt_path") if v < 0.45 else w.b("gravel") if v < 0.7 else w.b("cobblestone"))
            continue
        v = (r1(x, 0, z) * 0.7 + r2(x, 0, z) * 0.3) * s
        blk = kum[-1][1]
        for grenze, n in kum:
            if v <= grenze:
                blk = n
                break
        rand = math.hypot(x - cx, z - cz) / max(1, R)
        if rand > 0.85 and art == "wiese" and rng.random() < 0.5:
            blk = "grass_block"
        w.setze(x, 0, z, w.b(blk, snowy=False) if blk in ("grass_block", "podzol") else w.b(blk))
        if not w.frei(x, 1, z):
            continue
        if blk in ("grass_block", "moss_block", "podzol"):
            q = r2(x * 1.7, 3, z * 1.7)
            if blumen and q > 0.72 and rng.random() < 0.6 * dichte:
                w.setze(x, 1, z, w.b(blumen[int((r1(x, 9, z) * 997) % len(blumen))]))
            elif streu and rng.random() < 0.18 * dichte:
                w.setze(x, 1, z, w.b(streu[int(rng.integers(len(streu)))]))
            elif rng.random() < 0.012 * dichte:
                w.setze(x, 1, z, laub(w, "azalea" if rng.random() < 0.5 else "oak"))
                if rng.random() < 0.5:
                    w.setze(x + 1, 1, z, laub(w, "flowering_azalea"))
        if rng.random() < 0.004 * dichte:
            for dx, dz, dy in ((0, 0, 1), (1, 0, 1), (0, 1, 1), (0, 0, 2)):
                w.setze(x + dx, dy, z + dz, w.b(["mossy_cobblestone", "andesite", "cobblestone", "tuff"][int(rng.integers(4))]),
                        ueberschreiben=False)


def fahne_wand(w, x, y, z, laenge, farben, achse="x"):
    """Senkrechtes Banner aus Wolle an einer Wand."""
    for k in range(laenge):
        w.setze(x, y - k, z, w.b(farben[(k // 2) % len(farben)]) if k < laenge - 1 else w.b(farben[0]))


def wandlaterne(w, x, y, z, richtung, licht="lantern"):
    """Laterne an einem Ausleger aus Zaun – richtung: Wandseite, an der sie hängt (south/north/east/west)."""
    dx, dz = {"south": (0, 1), "north": (0, -1), "west": (-1, 0), "east": (1, 0)}[richtung]
    w.setze(x + dx, y, z + dz, w.b("spruce_fence", north=dz > 0, south=dz < 0, east=dx < 0, west=dx > 0,
                                   waterlogged=False), ueberschreiben=False)
    w.setze(x + dx, y - 1, z + dz, w.b(licht, hanging=True, waterlogged=False), ueberschreiben=False)

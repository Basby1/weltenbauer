"""Bäume III – zwanzig weitere Baumarten mit eigener Silhouette: Douglasie, Schirmkiefer, Säulenzypresse, Hainbuche,
Walnussbaum, Mandelbaum in Blüte, Trauerbirke, Korkeiche, Fächerahorn, Tulpenbaum, Esskastanie, Stechpalme, Bonsai-
Kiefer am Fels, Blutbuche, Robinie, Feigenbaum, Zitronenbaum, Wacholder, Latschenkiefer und Tausendjährige Eiche.

Stammfuß auf (0, 0, 0), groesse 0 klein · 1 mittel · 2 groß (wie Bäume II)."""

from __future__ import annotations

import math

from baeume import (Holzart, Pinsel, Wuchs, _laubbaum, abzweig, ast, blattwolke, bodenstreu, kugel_f, neue_welt,
                    richtung_aus_winkeln, stamm, verzweigen, wurzeln)
from baeume2 import HolzX, _flecken, _G, chipped, gelb_laub, orange_laub, rot_laub
from lib import laub


def _nadelbaum(w, holz, nadel, H, r, rmax, etage=3, unten=0.25, haengen=0.05, spitze=True, form=0.95):
    pinsel = Pinsel(w, holz)
    st = stamm(w, pinsel, H, r, 0.45, neigung=0, biegung=0.012, auftrieb=0.06)
    y = int(H * unten)
    while y < H - 1:
        t = (y - H * unten) / max(1, H - H * unten)
        rad = rmax * (1 - t) ** form + 0.8
        rad *= 0.82 + 0.3 * w.rng.random()
        mitte = st[min(len(st) - 1, int(y / H * (len(st) - 1)))][0]
        n = max(4, int(rad * 1.6))
        az0 = w.rng.random() * 360
        for k in range(n):
            d = richtung_aus_winkeln(az0 + k * 360 / n + (w.rng.random() - 0.5) * 25, 80)
            pkt = ast(w, pinsel, mitte, d, rad * 0.75, 0.45, 0.4, biegung=0.05, schwerkraft=haengen)
            for p, _, _ in pkt[1::2]:
                blattwolke(w, p + [0, 0.3, 0], 1.3, 0.9, nadel, schutz=pinsel.holz.alle, dichte=0.8)
        y += etage
    if spitze:
        blattwolke(w, st[-1][0] + [0, 0.5, 0], 1.2, 2.6, nadel, schutz=pinsel.holz.alle)
    return pinsel, st


def _schirm(w, holz, blaetter, H, r, n, L, wolke, flach=0.35, neigung=(45, 70), unterkante=0.8):
    pinsel = Pinsel(w, holz)
    st = stamm(w, pinsel, H, r, r * 0.7, neigung=6, biegung=0.08)
    enden, mitte = [], []
    cfg = Wuchs(kinder=2, spreizung=(25, 45), laenge=0.6, biegung=0.1, auftrieb=0.02)
    for i in range(n):
        d = abzweig(st[-1][1], neigung[0] + w.rng.random() * (neigung[1] - neigung[0]), i * 360 / n)
        verzweigen(w, pinsel, st[-1][0], d, L, max(0.5, r * 0.6), 1, cfg, enden, mitte)
    for p, t in enden:
        rw = wolke * (0.8 + 0.4 * w.rng.random())
        blattwolke(w, p + [0, 0.5, 0], rw, rw * flach, blaetter, schutz=pinsel.holz.alle, luecken=0.05,
                   min_y=int(H * unterkante))
    return pinsel, st


# ============================================================================ Nadelbäume

def douglasie(seed, groesse=1):
    """Douglasie: sehr hoher, gerader Stamm mit tief gefurchter, rotbrauner Rinde, kegelförmige, locker etagierte
    Krone mit leicht hängenden Zweigen und hellen Zapfen."""
    w = neue_welt(seed)
    nadel = [(laub(w, "spruce"), 0.7), (laub(w, "dark_oak"), 0.3)]
    holz = HolzX(w, "spruce_log", "spruce_wood")
    H = _G(groesse, [16, 26, 38])
    _nadelbaum(w, holz, nadel, H, _G(groesse, [0.6, 1.3, 2.0]), _G(groesse, [3.5, 5.5, 8.0]), etage=3, unten=0.3,
               haengen=0.12)
    _flecken(w, holz.alle, w.b("dark_oak_log", axis="y"), 0.25)
    bodenstreu(w, [w.b("fern"), w.b("brown_mushroom")], 3 + groesse * 3, 1, 4)
    return w


def schirmkiefer(seed, groesse=1):
    """Schirmkiefer: ein langer, leicht geneigter, rötlich geschuppter Stamm, der sich oben in mehrere Äste teilt und
    eine flache, weit ausladende, dunkelgrüne Schirmkrone trägt."""
    w = neue_welt(seed)
    bl = [(laub(w, "spruce"), 0.5), (laub(w, "dark_oak"), 0.3), (laub(w, "jungle"), 0.2)]
    holz = HolzX(w, "acacia_log", "acacia_wood")
    H = _G(groesse, [9, 15, 22])
    _schirm(w, holz, bl, H, _G(groesse, [0.5, 1.0, 1.5]), _G(groesse, [4, 6, 7]), _G(groesse, [4, 7, 10]),
            _G(groesse, [2.8, 3.6, 4.4]), flach=0.3)
    _flecken(w, holz.alle, w.b("spruce_log", axis="y"), 0.2)
    return w


def saeulenzypresse(seed, groesse=1):
    """Säulenzypresse: eine schmale, hohe, flammenförmige Säule aus dichtem, dunkelgrünem Laub, kaum breiter als ein
    Mensch, mit spitzer Krone – das Bild mediterraner Alleen."""
    w = neue_welt(seed)
    nadel = laub(w, "spruce")
    dunkel = laub(w, "dark_oak")
    H = _G(groesse, [10, 17, 25])
    rmax = _G(groesse, [1.3, 2.0, 2.8])
    for y in range(0, H + 1):
        t = y / H
        r = rmax * (math.sin(math.pi * min(1, t * 1.05)) ** 0.5) * (1 - 0.3 * t) + 0.3
        for x in range(-4, 5):
            for z in range(-4, 5):
                if math.hypot(x, z) <= r and (y > 1 or (x, z) == (0, 0)):
                    w.setze(x, y, z, w.b("spruce_log", axis="y") if (x, z) == (0, 0) and t < 0.8 else
                            nadel if (x + y + z) % 3 else dunkel)
    w.setze(0, H + 1, 0, nadel)
    return w


def wacholder(seed, groesse=1):
    """Wacholder: ein knorriger, mehrstämmiger Strauchbaum mit verdrehten Stämmen und dichten, bläulich-grünen
    Nadelpolstern, besetzt mit dunkelblauen Beeren, auf kargem Heideboden."""
    w = neue_welt(seed)
    bl = [(laub(w, "spruce"), 0.6), (laub(w, "azalea"), 0.4)]
    holz = HolzX(w, "stripped_spruce_log", "stripped_spruce_wood")
    pinsel = Pinsel(w, holz)
    H = _G(groesse, [5, 8, 12])
    for k in range(_G(groesse, [2, 3, 4])):
        d = richtung_aus_winkeln(k * 120 + w.rng.random() * 40, 12 + w.rng.random() * 15)
        pkt = ast(w, pinsel, [0.5, 0.5, 0.5], d, H, _G(groesse, [0.5, 0.7, 1.0]), 0.4, biegung=0.15)
        for p, _, _ in pkt[2::2]:
            blattwolke(w, p + [0, 0.3, 0], 1.6 + groesse * 0.4, 1.3, bl, schutz=holz.alle, dichte=0.85)
    for p, b in list(w.bloecke.items()):
        if b in (bl[0][0], bl[1][0]) and w.rng.random() < 0.04:
            w.bloecke[p] = w.b("blue_concrete")
    return w


def latschenkiefer(seed, groesse=1):
    """Latschenkiefer: eine niederliegende Bergkiefer, deren Äste wie Schlangen über Felsblöcke kriechen und sich an den
    Spitzen bürstenartig aufrichten – ein dichtes, grünes Polster im Gebirge."""
    w = neue_welt(seed)
    nadel = [(laub(w, "spruce"), 0.7), (laub(w, "jungle"), 0.3)]
    holz = HolzX(w, "spruce_log", "spruce_wood")
    pinsel = Pinsel(w, holz)
    for k in range(3 + groesse):
        kugel_f(w, ((w.rng.random() - 0.5) * 6 * (groesse + 1), 0, (w.rng.random() - 0.5) * 6 * (groesse + 1)),
                1.5 + w.rng.random() * (1 + groesse), w.b("stone"))
    for k in range(_G(groesse, [4, 6, 9])):
        d = richtung_aus_winkeln(k * 360 / (4 + groesse * 2) + w.rng.random() * 30, 72)
        pkt = ast(w, pinsel, [0.5, 1.0, 0.5], d, _G(groesse, [4, 7, 10]), 0.5, 0.4, biegung=0.2, auftrieb=0.05)
        for p, _, _ in pkt[1::2]:
            blattwolke(w, p + [0, 0.6, 0], 1.4, 0.9, nadel, schutz=holz.alle, dichte=0.85)
    return w


def bonsaikiefer(seed, groesse=1):
    """Bonsai-Kiefer am Fels: aus einer Felsspalte wächst eine vom Wind geformte Kiefer, deren Stamm sich in einer
    S-Kurve weit über den Abgrund neigt; die Nadelpolster liegen wie flache Wolkenschichten übereinander."""
    w = neue_welt(seed)
    bl = [(laub(w, "spruce"), 0.6), (laub(w, "dark_oak"), 0.4)]
    holz = HolzX(w, "dark_oak_log", "dark_oak_wood")
    pinsel = Pinsel(w, holz)
    R = _G(groesse, [3, 5, 7])
    kugel_f(w, (0, -R * 0.4, 0), R, w.b("stone"))
    kugel_f(w, (-R * 0.5, 0, 1), R * 0.7, w.b("andesite"))
    p0 = [0.5, R * 0.5, 0.5]
    d = richtung_aus_winkeln(90, 35)
    pkt = ast(w, pinsel, p0, d, _G(groesse, [5, 9, 13]), _G(groesse, [0.6, 0.9, 1.3]), 0.5, biegung=0.25)
    for i, (p, pd, _) in enumerate(pkt[2::2]):
        if i % 2 == 0:
            for s_ in (-1, 1):
                d2 = abzweig(pd, 70, 90 * s_ + 90)
                a2 = ast(w, pinsel, p, d2, _G(groesse, [2, 3, 5]), 0.45, 0.4, biegung=0.1)
                blattwolke(w, a2[-1][0] + [0, 0.6, 0], _G(groesse, [1.8, 2.6, 3.4]), 0.8, bl, schutz=holz.alle)
    blattwolke(w, pkt[-1][0] + [0, 0.8, 0], _G(groesse, [2.2, 3.0, 4.0]), 1.0, bl, schutz=holz.alle)
    return w


# ============================================================================ Laubbäume

def hainbuche(seed, groesse=1):
    """Hainbuche: ein Stamm mit typischen, gedrehten Längswülsten, eine dichte, eiförmige Krone aus frischgrünem Laub
    mit hängenden, hopfenartigen Fruchtständen."""
    w = neue_welt(seed)
    bl = [(laub(w, "oak"), 0.5), (laub(w, "birch"), 0.35), (laub(w, "azalea"), 0.15)]
    H = _G(groesse, [9, 15, 21])
    cfg = Wuchs(kinder=3, spreizung=(20, 38), laenge=0.62, biegung=0.08, auftrieb=0.06)
    holz = _laubbaum(w, "birch", bl, H, _G(groesse, [0.55, 1.0, 1.5]), 0.35, cfg, _G(groesse, [1, 2, 2]),
                     _G(groesse, [2.5, 3.0, 3.5]), wurzel_n=_G(groesse, [0, 4, 6]), wurzel_l=_G(groesse, [0, 2, 3]),
                     krone_aeste=_G(groesse, [3, 4, 5]), kronen_neigung=(15, 35), flach=1.1)
    _flecken(w, holz.alle, w.b("stripped_birch_log", axis="y"), 0.4)
    for p, b in list(w.bloecke.items()):
        if b == bl[0][0] and w.rng.random() < 0.02 and (p[0], p[1] - 1, p[2]) not in w.bloecke:
            w.setze(p[0], p[1] - 1, p[2], w.b("lime_wool"))
    return w


def walnussbaum(seed, groesse=1):
    """Walnussbaum: ein kurzer, dicker Stamm mit silbergrauer Rinde, wenige, sehr kräftige, weit ausladende Äste und
    eine lockere, breite Krone; grüne Nüsse und Nussschalen im Gras."""
    w = neue_welt(seed)
    bl = [(laub(w, "oak"), 0.55), (laub(w, "jungle"), 0.3), (laub(w, "birch"), 0.15)]
    H = _G(groesse, [9, 15, 21])
    cfg = Wuchs(kinder=2, spreizung=(30, 55), laenge=0.65, biegung=0.12, auftrieb=0.02)
    holz = _laubbaum(w, "birch", bl, H, _G(groesse, [0.7, 1.4, 2.0]), 0.32, cfg, _G(groesse, [1, 2, 2]),
                     _G(groesse, [2.8, 3.4, 4.0]), wurzel_n=_G(groesse, [0, 5, 7]), wurzel_l=_G(groesse, [0, 3, 5]),
                     krone_aeste=_G(groesse, [3, 4, 5]), kronen_neigung=(40, 65), flach=0.6, luecken=0.15)
    _flecken(w, holz.alle, w.b("stripped_dark_oak_log", axis="y"), 0.3)
    bodenstreu(w, [w.b("lime_carpet"), w.b("brown_carpet")], 6 + groesse * 6, 2, 5 + groesse * 2)
    return w


def mandelbaum(seed, groesse=1):
    """Mandelbaum in Blüte: ein knorriger, dunkler, kleiner Baum mit locker verzweigter Krone, über und über bedeckt mit
    zartweißen bis blassrosa Blüten, noch fast ohne Laub; ein Blütenteppich am Boden."""
    w = neue_welt(seed)
    bl = [(laub(w, "cherry"), 0.45), (laub(w, "flowering_azalea"), 0.15), (w.b("white_wool"), 0.25),
          (w.b("pink_wool"), 0.15)]
    H = _G(groesse, [7, 11, 16])
    cfg = Wuchs(kinder=3, spreizung=(30, 55), laenge=0.6, biegung=0.15, auftrieb=0.03)
    _laubbaum(w, "dark_oak", bl, H, _G(groesse, [0.45, 0.8, 1.2]), 0.35, cfg, _G(groesse, [1, 2, 2]),
              _G(groesse, [2.0, 2.6, 3.0]), neigung=8, krone_aeste=_G(groesse, [3, 4, 5]), kronen_neigung=(35, 60),
              flach=0.7, luecken=0.25)
    bodenstreu(w, [w.b("pink_petals", facing="north", flower_amount=2), w.b("pink_petals", facing="east",
                                                                             flower_amount=4)],
               10 + groesse * 12, 1, 4 + groesse * 2)
    return w


def trauerbirke(seed, groesse=1):
    """Trauerbirke: ein schlanker, weißer Stamm, von dessen bogig überhängenden Ästen lange, dünne Zweige mit kleinem,
    hellgrünem Laub wie ein Vorhang senkrecht herabfallen."""
    w = neue_welt(seed)
    blatt = laub(w, "birch")
    hell = laub(w, "azalea")
    pinsel = Pinsel(w, Holzart(w, "birch"))
    H = _G(groesse, [9, 14, 20])
    st = stamm(w, pinsel, H, _G(groesse, [0.5, 0.8, 1.1]), 0.4, neigung=4)
    for k in range(_G(groesse, [5, 7, 9])):
        d = abzweig(st[-1][1], 55 + w.rng.random() * 20, k * 360 / (5 + groesse * 2))
        pkt = ast(w, pinsel, st[-1 - int(w.rng.random() * 4)][0], d, _G(groesse, [3, 5, 7]), 0.45, 0.4,
                  biegung=0.1, schwerkraft=0.25)
        blattwolke(w, pkt[-1][0] + [0, 0.5, 0], 1.6, 1.0, [(blatt, 0.7), (hell, 0.3)], schutz=pinsel.holz.alle)
        for p, _, _ in pkt[1::2]:
            blattwolke(w, p + [0, 0.6, 0], 1.5, 0.9, [(blatt, 0.7), (hell, 0.3)], schutz=pinsel.holz.alle)
        for p, _, _ in pkt[2::2]:
            if w.rng.random() < 0.35:
                continue
            L = int(2 + w.rng.random() * (p[1] * 0.45))
            for dy in range(L):
                y = int(p[1]) - dy
                if y < 1:
                    break
                w.setze(int(p[0]), y, int(p[2]), blatt if (dy + int(p[0])) % 3 else hell, False)
    return w


def korkeiche(seed, groesse=1):
    """Korkeiche: ein knorriger, breiter Baum, dessen Stamm unten frisch geschält leuchtend rotbraun ist, oben mit dicker,
    grauer Korkborke; eine runde, dunkle, immergrüne Krone."""
    w = neue_welt(seed)
    bl = [(laub(w, "dark_oak"), 0.55), (laub(w, "oak"), 0.3), (laub(w, "jungle"), 0.15)]
    H = _G(groesse, [8, 13, 19])
    cfg = Wuchs(kinder=3, spreizung=(30, 55), laenge=0.62, biegung=0.15, auftrieb=0.02)
    holz = _laubbaum(w, "dark_oak", bl, H, _G(groesse, [0.6, 1.2, 1.8]), 0.38, cfg, _G(groesse, [1, 2, 2]),
                     _G(groesse, [2.6, 3.2, 3.8]), neigung=6, krone_aeste=_G(groesse, [3, 4, 5]),
                     kronen_neigung=(35, 60), flach=0.75)
    for p, b in list(w.bloecke.items()):
        if b in holz.alle:
            w.bloecke[p] = w.b("terracotta") if p[1] < H * 0.25 else w.b("light_gray_terracotta") if \
                (p[0] + p[1] + p[2]) % 3 else b
    return w


def faecherahorn(seed, groesse=1):
    """Fächerahorn: ein kleiner, vielstämmiger Zierbaum mit mehreren übereinanderliegenden, flachen Laubschichten in
    leuchtendem Purpurrot und Orange, wie in einem Teegarten."""
    w = neue_welt(seed)
    bl = [(rot_laub(w), 0.55), (chipped(w, "red_oak", "nether_wart_block"), 0.25), (orange_laub(w), 0.2)]
    holz = HolzX(w, "dark_oak_log", "dark_oak_wood")
    pinsel = Pinsel(w, holz)
    H = _G(groesse, [5, 8, 12])
    for k in range(_G(groesse, [2, 3, 4])):
        d = richtung_aus_winkeln(k * 360 / (2 + groesse) + w.rng.random() * 30, 25 + w.rng.random() * 15)
        pkt = ast(w, pinsel, [0.5, 0.5, 0.5], d, H, _G(groesse, [0.4, 0.6, 0.8]), 0.4, biegung=0.18)
        for i, (p, pd, _) in enumerate(pkt[2::2]):
            blattwolke(w, p + [0, 0.4, 0], 1.8 + groesse * 0.6, 0.7, bl, schutz=holz.alle, luecken=0.15)
    bodenstreu(w, [w.b("red_carpet"), w.b("orange_carpet")], 8 + groesse * 8, 1, 3 + groesse * 2)
    return w


def tulpenbaum(seed, groesse=1):
    """Tulpenbaum: ein kerzengerader, sehr hoher Stamm mit einer schmal-ovalen Krone aus großen, eckigen Blättern, in
    der tulpenförmige, gelbgrün-orange Blüten aufrecht stehen."""
    w = neue_welt(seed)
    bl = [(laub(w, "oak"), 0.55), (laub(w, "jungle"), 0.35), (w.b("orange_wool"), 0.05), (w.b("yellow_wool"), 0.05)]
    H = _G(groesse, [12, 20, 29])
    cfg = Wuchs(kinder=3, spreizung=(18, 35), laenge=0.6, biegung=0.06, auftrieb=0.08)
    _laubbaum(w, "oak", bl, H, _G(groesse, [0.55, 1.1, 1.6]), 0.5, cfg, _G(groesse, [1, 2, 2]),
              _G(groesse, [2.4, 2.9, 3.4]), neigung=1, krone_aeste=_G(groesse, [4, 5, 6]), kronen_neigung=(15, 30),
              flach=1.2, kronen_unterkante=0.95)
    return w


def esskastanie(seed, groesse=1):
    """Esskastanie: ein mächtiger, spiralig gedrehter Stamm mit tiefen Rindenfurchen, eine breite Krone mit langen,
    gezähnten Blättern und stacheligen, aufgeplatzten Fruchthüllen am Boden."""
    w = neue_welt(seed)
    bl = [(laub(w, "oak"), 0.45), (laub(w, "jungle"), 0.35), (laub(w, "dark_oak"), 0.2)]
    H = _G(groesse, [10, 16, 23])
    cfg = Wuchs(kinder=3, spreizung=(28, 50), laenge=0.63, biegung=0.12, auftrieb=0.03)
    holz = _laubbaum(w, "dark_oak", bl, H, _G(groesse, [0.7, 1.5, 2.2]), 0.4, cfg, _G(groesse, [1, 2, 2]),
                     _G(groesse, [2.8, 3.4, 4.0]), wurzel_n=_G(groesse, [0, 6, 8]), wurzel_l=_G(groesse, [0, 3, 5]),
                     krone_aeste=_G(groesse, [3, 5, 6]), kronen_neigung=(30, 55), flach=0.8)
    _flecken(w, holz.alle, w.b("stripped_spruce_log", axis="y"), 0.2)
    bodenstreu(w, [w.b("lime_wool"), w.b("brown_mushroom")], 6 + groesse * 6, 2, 5 + groesse * 2)
    return w


def stechpalme(seed, groesse=1):
    """Stechpalme: ein dichter, kegelförmiger, immergrüner Baum mit dunkel glänzendem, stacheligem Laub, übersät mit
    leuchtend roten Beeren – auch im Winter ein Farbtupfer."""
    w = neue_welt(seed)
    nadel = [(laub(w, "dark_oak"), 0.6), (laub(w, "jungle"), 0.25), (w.b("red_concrete"), 0.08),
             (laub(w, "oak"), 0.07)]
    holz = HolzX(w, "dark_oak_log", "dark_oak_wood")
    H = _G(groesse, [7, 12, 17])
    _nadelbaum(w, holz, nadel, H, _G(groesse, [0.4, 0.7, 1.0]), _G(groesse, [2.2, 3.5, 5.0]), etage=2, unten=0.1,
               haengen=0.0, form=0.8)
    return w


def blutbuche(seed, groesse=1):
    """Blutbuche: eine gewaltige, glattstämmige Buche mit tief herabreichender, kuppelförmiger Krone aus dunkel-
    purpurrotem Laub – ein Parkbaum von großer Würde."""
    w = neue_welt(seed)
    bl = [(rot_laub(w), 0.4), (w.b("purple_terracotta"), 0.0), (chipped(w, "red_oak", "nether_wart_block"), 0.35),
          (laub(w, "dark_oak"), 0.25)]
    bl = [b for b in bl if b[1] > 0]
    H = _G(groesse, [10, 17, 24])
    cfg = Wuchs(kinder=3, spreizung=(22, 42), laenge=0.66, biegung=0.08, auftrieb=0.04)
    holz = _laubbaum(w, "birch", bl, H, _G(groesse, [0.7, 1.4, 2.1]), 0.45, cfg, _G(groesse, [1, 2, 2]),
                     _G(groesse, [2.8, 3.4, 4.0]), wurzel_n=_G(groesse, [0, 5, 7]), wurzel_l=_G(groesse, [0, 3, 5]),
                     krone_aeste=_G(groesse, [4, 5, 7]), kronen_neigung=(30, 55), flach=0.65, kronen_unterkante=0.5)
    for p, b in list(w.bloecke.items()):
        if b in holz.alle:
            w.bloecke[p] = w.b("stripped_birch_wood", axis="y") if (p[0] + p[2]) % 3 else w.b("light_gray_concrete")
    return w


def robinie(seed, groesse=1):
    """Robinie: ein lockerer, unregelmäßiger Baum mit tief gefurchter Rinde, gefiedertem, hellgrünem Laub und langen,
    hängenden, weißen Blütentrauben, die nach Honig duften."""
    w = neue_welt(seed)
    bl = [(laub(w, "azalea"), 0.45), (laub(w, "oak"), 0.35), (laub(w, "birch"), 0.2)]
    H = _G(groesse, [10, 16, 22])
    cfg = Wuchs(kinder=3, spreizung=(28, 55), laenge=0.6, biegung=0.18, auftrieb=0.03)
    _laubbaum(w, "oak", bl, H, _G(groesse, [0.5, 1.0, 1.5]), 0.4, cfg, _G(groesse, [1, 2, 2]),
              _G(groesse, [2.2, 2.8, 3.2]), neigung=6, krone_aeste=_G(groesse, [3, 4, 5]), luecken=0.2, flach=0.7)
    for p, b in list(w.bloecke.items()):
        if b == bl[0][0] and w.rng.random() < 0.06:
            for d in range(1, 3 + groesse):
                q = (p[0], p[1] - d, p[2])
                if q in w.bloecke:
                    break
                w.setze(*q, w.b("white_wool"))
    return w


def feigenbaum(seed, groesse=1):
    """Feigenbaum: ein breiter, niedriger Baum mit silbergrauen, gewundenen Ästen, großen, gelappten Blättern und
    violetten Feigen, der sich über eine warme Steinmauer lehnt."""
    w = neue_welt(seed)
    bl = [(laub(w, "jungle"), 0.5), (laub(w, "oak"), 0.4), (w.b("purple_terracotta"), 0.1)]
    H = _G(groesse, [6, 10, 14])
    cfg = Wuchs(kinder=3, spreizung=(35, 65), laenge=0.65, biegung=0.18, auftrieb=0.0)
    holz = _laubbaum(w, "birch", bl, H, _G(groesse, [0.5, 0.9, 1.3]), 0.3, cfg, _G(groesse, [1, 2, 2]),
                     _G(groesse, [2.4, 3.0, 3.6]), neigung=10, krone_aeste=_G(groesse, [4, 5, 6]),
                     kronen_neigung=(45, 70), flach=0.6)
    _flecken(w, holz.alle, w.b("stripped_birch_wood", axis="y"), 0.5)
    L = _G(groesse, [5, 8, 11])
    for x in range(-L, L + 1):
        for y in range(0, 2 + groesse):
            if (x, y, -3 - groesse) not in w.bloecke:
                w.setze(x, y, -3 - groesse, w.b("sandstone") if (x + y) % 3 else w.b("smooth_sandstone"))
    return w


def zitronenbaum(seed, groesse=1):
    """Zitronenbaum: ein kleiner, runder Baum in einem großen Terrakottakübel mit dunkelgrünem, glänzendem Laub, voller
    leuchtend gelber Früchte und weißer Blüten zugleich."""
    w = neue_welt(seed)
    r = _G(groesse, [1.5, 2.5, 3.5])
    for x in range(-int(r) - 1, int(r) + 2):
        for z in range(-int(r) - 1, int(r) + 2):
            d = math.hypot(x, z)
            for y in range(0, _G(groesse, [2, 3, 4])):
                if d <= r + 0.2 * y:
                    w.setze(x, y, z, w.b("orange_terracotta") if d > r - 0.6 + 0.2 * y or y == 0 else w.b("podzol",
                                                                                                         snowy=False))
    bl = [(laub(w, "jungle"), 0.5), (laub(w, "dark_oak"), 0.3), (w.b("yellow_concrete"), 0.15),
          (w.b("white_wool"), 0.05)]
    pinsel = Pinsel(w, Holzart(w, "oak"))
    y0 = _G(groesse, [2, 3, 4])
    st = ast(w, pinsel, [0.5, y0, 0.5], [0, 1, 0], _G(groesse, [3, 5, 7]), _G(groesse, [0.4, 0.5, 0.7]), 0.4)
    blattwolke(w, st[-1][0] + [0, 1.5, 0], _G(groesse, [2.5, 3.5, 4.5]), _G(groesse, [2.2, 3.0, 3.8]), bl,
               schutz=pinsel.holz.alle, dichte=0.9)
    return w


def tausendjaehrige_eiche(seed, groesse=1):
    """Tausendjährige Eiche: ein uralter, hohler Baumriese mit gewaltigem, zerklüftetem Stamm, abgebrochenen Starkästen,
    Moos und Pilzen, dessen Krone dennoch weit und grün ausladend weiterlebt."""
    w = neue_welt(seed)
    bl = [(laub(w, "oak"), 0.65), (laub(w, "dark_oak"), 0.25), (laub(w, "azalea"), 0.1)]
    H = _G(groesse, [13, 21, 30])
    cfg = Wuchs(kinder=3, spreizung=(30, 60), laenge=0.62, biegung=0.18, auftrieb=0.0)
    holz = _laubbaum(w, "oak", bl, H, _G(groesse, [1.2, 2.4, 3.4]), 0.35, cfg, _G(groesse, [1, 2, 2]),
                     _G(groesse, [3.0, 3.8, 4.6]), wurzel_n=_G(groesse, [4, 8, 10]), wurzel_l=_G(groesse, [2, 5, 7]),
                     krone_aeste=_G(groesse, [4, 6, 7]), kronen_neigung=(40, 70), flach=0.65, luecken=0.12)
    r = _G(groesse, [1.2, 2.4, 3.4])
    for x in range(-int(r), int(r) + 1):
        for z in range(-int(r), int(r) + 1):
            if math.hypot(x, z) < r - 1:
                for y in range(1, int(H * 0.25)):
                    w.bloecke.pop((x, y, z), None)
    for y in (1, 2):
        w.bloecke.pop((int(r), y, 0), None)
        w.bloecke.pop((int(r) - 1, y, 0), None)
    _flecken(w, holz.alle, w.b("moss_block"), 0.08)
    for p, b in list(w.bloecke.items()):
        if b in holz.alle and w.rng.random() < 0.01:
            q = (p[0] + 1, p[1], p[2])
            if q not in w.bloecke:
                w.setze(*q, w.b("brown_mushroom_block", north=True, south=True, east=True, west=True, up=True,
                                down=True))
    return w


BAEUME3 = {
    "douglasie": ("Douglasie", douglasie),
    "schirmkiefer": ("Schirmkiefer", schirmkiefer),
    "saeulenzypresse": ("Säulenzypresse", saeulenzypresse),
    "hainbuche": ("Hainbuche", hainbuche),
    "walnussbaum": ("Walnussbaum", walnussbaum),
    "mandelbaum": ("Mandelbaum in Blüte", mandelbaum),
    "trauerbirke": ("Trauerbirke", trauerbirke),
    "korkeiche": ("Korkeiche", korkeiche),
    "faecherahorn": ("Fächerahorn", faecherahorn),
    "tulpenbaum": ("Tulpenbaum", tulpenbaum),
    "esskastanie": ("Esskastanie", esskastanie),
    "stechpalme": ("Stechpalme", stechpalme),
    "bonsaikiefer": ("Bonsai-Kiefer am Fels", bonsaikiefer),
    "blutbuche": ("Blutbuche", blutbuche),
    "robinie": ("Robinie", robinie),
    "feigenbaum": ("Feigenbaum", feigenbaum),
    "zitronenbaum": ("Zitronenbaum im Kübel", zitronenbaum),
    "wacholder": ("Wacholder", wacholder),
    "latschenkiefer": ("Latschenkiefer", latschenkiefer),
    "tausendjaehrige_eiche": ("Tausendjährige Eiche", tausendjaehrige_eiche),
}

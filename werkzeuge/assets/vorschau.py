"""Kontaktbögen: rendert viele Assets nebeneinander mit Beschriftung."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "/home/claude/Blaupause")
from blaupause.vorschau import iso_bild  # noqa: E402

from lib import farbe_von, als_raster  # noqa: E402

GROESSEN = ["klein", "mittel", "groß"]


def schrift(px):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, px)
    return ImageFont.load_default()


HG = (236, 232, 222)


def bild(welt, max_pixel=420, deko=True, boden=0, meer=False):
    """boden > 0: legt nur für die Vorschau eine Grasfläche mit diesem Rand unter das Asset."""
    extra = getattr(welt, "vorschau_extra", None)
    if boden or extra:
        import copy
        welt = copy.deepcopy(welt)
        for p, b in (extra or {}).items():
            welt.bloecke.setdefault(p, b)
        lo, hi = welt.grenzen()
        gras = welt.b("water", level=0) if meer else welt.b("grass_block", snowy=False)
        erde = welt.b("sand") if meer else welt.b("dirt")
        for x in range(lo[0] - boden, hi[0] + boden + 1):
            for z in range(lo[2] - boden, hi[2] + boden + 1):
                for y, b in ((0, gras), (-1, erde)):
                    if (x, y, z) not in welt.bloecke:
                        welt.bloecke[(x, y, z)] = b
        # alles unter der Erde für die Vorschau abschneiden
        for p in [p for p in welt.bloecke if p[1] < -1]:
            del welt.bloecke[p]
    idx, liste = als_raster(welt, deko_ausblenden=not deko)
    img = iso_bild(idx, liste, max_pixel=max_pixel, hintergrund=HG)
    # leeren Rand abschneiden
    from PIL import ImageChops
    diff = ImageChops.difference(img.convert("RGB"), Image.new("RGB", img.size, HG))
    box = diff.getbbox()
    return img.crop(box) if box else img


def bogen(eintraege, spalten, zelle=420, titel="", hintergrund=(236, 232, 222)):
    """eintraege: Liste von (Beschriftung, PIL-Bild). Zeilenhöhe richtet sich nach dem höchsten Bild."""
    bilder = []
    for text, img in eintraege:
        img = img.convert("RGBA")
        img.thumbnail((zelle - 16, int(zelle * 1.3)))
        bilder.append((text, img))
    zeilen = [bilder[i:i + spalten] for i in range(0, len(bilder), spalten)]
    kopf = 70 if titel else 0
    unter = 46
    hoehen = [max(im.height for _, im in z) + 20 for z in zeilen]
    B = Image.new("RGB", (spalten * zelle, kopf + sum(h + unter for h in hoehen)), hintergrund)
    d = ImageDraw.Draw(B)
    if titel:
        d.text((20, 18), titel, fill=(40, 40, 40), font=schrift(34))
    f = schrift(20)
    y0 = kopf
    for z, h in zip(zeilen, hoehen):
        for c, (text, img) in enumerate(z):
            x0 = c * zelle
            B.paste(img, (x0 + (zelle - img.width) // 2, y0 + (h - img.height)), img)
            w = d.textlength(text, font=f)
            d.text((x0 + (zelle - w) / 2, y0 + h + 8), text, fill=(50, 50, 50), font=f)
        y0 += h + unter
    return B


def paletten_bild(gruppen, titel="Blockpalette", feld=96):
    """gruppen: Liste von (Name, [Block-IDs]). Zeichnet Farbfelder mit leichter Pixel-Struktur und Namen."""
    import numpy as np
    from lib import FARBEN
    rand, abstand_zeile, beschriftung = 30, 64, 46
    spalten = max(len(g[1]) for g in gruppen)
    breite = rand * 2 + 230 + spalten * (feld + 14)
    hoehe = 90 + len(gruppen) * (feld + beschriftung + abstand_zeile - 30)
    B = Image.new("RGB", (breite, hoehe), HG)
    d = ImageDraw.Draw(B)
    d.text((rand, 22), titel, fill=(40, 40, 40), font=schrift(34))
    f_name, f_block = schrift(22), schrift(13)
    rng = np.random.default_rng(1)
    y = 90
    for eintrag in gruppen:
        name, bloecke = eintrag[0], eintrag[1]
        pfeile = eintrag[2] if len(eintrag) > 2 else True
        d.text((rand, y + feld // 2 - 12), name, fill=(50, 50, 50), font=f_name)
        x = rand + 230
        for i, blk in enumerate(bloecke):
            r, g, b = farbe_von(blk) or (200, 0, 200)
            # 16x16 "Textur": Helligkeitsrauschen wie bei Minecraft-Blöcken
            px = feld // 16
            tex = rng.normal(0, 9, (16, 16))
            for ty in range(16):
                for tx in range(16):
                    k = tex[ty, tx]
                    farbe = tuple(int(max(0, min(255, c + k))) for c in (r, g, b))
                    d.rectangle([x + tx * px, y + ty * px, x + (tx + 1) * px - 1, y + (ty + 1) * px - 1], fill=farbe)
            d.rectangle([x, y, x + feld - 1, y + feld - 1], outline=(60, 60, 60), width=2)
            if pfeile and i < len(bloecke) - 1:
                d.text((x + feld + 2, y + feld // 2 - 9), "›", fill=(120, 120, 120), font=f_name)
            text = blk.replace("waxed_", "w. ")
            zeilen = [text] if d.textlength(text, font=f_block) < feld + 10 else text.replace("_", "_\n", 1).split("\n")
            for k, z in enumerate(zeilen):
                tw = d.textlength(z, font=f_block)
                d.text((x + (feld - tw) / 2, y + feld + 6 + k * 15), z, fill=(60, 60, 60), font=f_block)
            x += feld + 14
        y += feld + beschriftung + abstand_zeile - 30
    return B

"""Erzeugt alle eingebauten Vorlagen für Weltenbauer.

Ausgabe:
  src/main/resources/data/weltenbauer/structures/<kategorie>/<id>.nbt   (auch mit /place template nutzbar)
  src/main/resources/data/weltenbauer/vorlagen.json                    (Liste für /wb vorlage)
  werkzeuge/assets/bilder/*.png                                        (Übersichtsbilder)

Aufruf:  python3 exportieren.py [--ohne-bilder] [--nur-pakete]

Kategorien in PAKET_KAT landen nicht im Mod-Jar, sondern als Zip-Paket in pakete/ (plus pakete.json).
Die Mod lädt sie im Menü über „Neue Vorlagen laden“ nach – ohne Neuinstallation.
"""

from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))

from baeume import ARTEN  # noqa: E402
from lib import exportieren, laden  # noqa: E402
from natur import NATUR  # noqa: E402
from ruinen import RUINEN  # noqa: E402
from spektakulaer import SPEKTAKULAER  # noqa: E402
from gebaeude import GEBAEUDE  # noqa: E402
from schildkroete import SCHILDKROETE  # noqa: E402
from schwebend import SCHWEBEND  # noqa: E402
from riesenbogen import FANTASIEHAEUSER, RIESENBOGEN  # noqa: E402
from himmelsstadt import GROESSEN as G4, HIMMELSSTADT, SCHWEBEBERGE  # noqa: E402
from leuchtwald import LEUCHTWALD  # noqa: E402
from bruecken import BRUECKEN, GAERTEN  # noqa: E402
from fantasie import FANTASIE, SCHIFFE  # noqa: E402
from sagenlande import SAGENLANDE  # noqa: E402
from boote import BOOTE  # noqa: E402
from piraten import MAHLSTROM, PIRATEN  # noqa: E402
from kreaturen import KREATUREN  # noqa: E402
from antike import ANTIKE  # noqa: E402
from orklager import ORKLAGER  # noqa: E402
from feenstadt import FEENSTADT  # noqa: E402
from bienenstadt import BIENENSTADT  # noqa: E402
from haeuser import HAEUSER  # noqa: E402
from mystik import HELIX, MYSTIK  # noqa: E402
from burgen import BURGEN  # noqa: E402
from kathedralen import KATHEDRALEN  # noqa: E402
from fernost import FERNOST  # noqa: E402
from wueste_eis import EISREICH, WUESTE  # noqa: E402
from elemente import END, NETHER, UNTERWASSER, VULKAN  # noqa: E402
from dorf1 import DSCHUNGEL, MARKT, WIKINGER  # noqa: E402


PROJEKT = HIER.parent.parent
VORSCHAU = PROJEKT / "src/main/resources/assets/weltenbauer/textures/gui/vorschau"
ZIEL = PROJEKT / "src/main/resources/data/weltenbauer"
BILDER = HIER / "bilder"
KRATER = Path("/home/claude/ruinenkrater/ausgabe")

# (Kategorie-ID, Anzeigename, Tabelle, Größen [(Index, Kürzel, Anzeige)], Varianten-Seeds)
GRUPPEN = [
    ("baeume", "Bäume", ARTEN, [(0, "klein", "klein"), (1, "mittel", "mittel"), (2, "gross", "groß")], [7, 21]),
    ("spektakulaer", "Spektakuläre Bäume", SPEKTAKULAER, [(0, "mittel", "mittel"), (1, "riesig", "riesig")], [7, 21]),
    ("ruinen", "Ruinen", RUINEN, [(0, "mittel", "mittel"), (1, "gross", "groß")], [7]),
    ("natur", "Felsen & Natur", NATUR, [(0, "mittel", "mittel"), (1, "gross", "groß")], [7]),
    ("schwebend", "Schwebende Strukturen", SCHWEBEND, [(0, "mittel", "mittel"), (1, "riesig", "riesig")], [7]),
    ("gebaeude", "Gebäude", GEBAEUDE, [(0, "mittel", "mittel"), (1, "gross", "groß")], [7, 21]),
    ("inseln", "Schildkröten-Inseln", SCHILDKROETE, [(0, "mittel", "mittel"), (1, "riesig", "riesig")], [7, 21]),
    ("bogen", "Riesenbögen", RIESENBOGEN, [(0, "mittel", "mittel"), (1, "riesig", "riesig")], [7, 21]),
    ("himmelsstadt", "Himmelsstadt", HIMMELSSTADT, G4, [7, 21]),
    ("schwebeberge", "Schwebeberge", SCHWEBEBERGE, G4, [7, 21]),
    ("leuchtwald", "Leuchtwald", LEUCHTWALD, G4, [7, 21]),
    ("bruecken", "Brücken", BRUECKEN, G4, [7]),
    ("gaerten", "Hängende Gärten", GAERTEN, G4, [7, 21]),
    ("statuen", "Statuen & Magie", FANTASIE, G4, [7, 21]),
    ("steampunk", "Schiffe & Steampunk", SCHIFFE, G4, [7, 21]),
    ("sagenlande", "Sagenlande", SAGENLANDE, G4, [7, 21]),
    ("boote", "Boote & Schiffe", BOOTE, G4, [7, 21]),
    ("piraten", "Piraten", PIRATEN, G4, [7, 21]),
    ("piraten", "Piraten", MAHLSTROM, [(3, "gigantisch", "gigantisch")], [7]),
    ("kreaturen", "Kreaturen", KREATUREN, G4, [7, 21]),
    ("antike", "Antike Monumente", ANTIKE, G4, [7, 21]),
    ("orklager", "Orklager", ORKLAGER, G4, [7, 21]),
    ("feenstadt", "Feenstadt", FEENSTADT, G4, [7, 21]),
    ("bienenstadt", "Bienenstadt", BIENENSTADT, G4, [7, 21]),
    ("haeuser", "Häuser", HAEUSER, G4, [7, 21]),
    ("mystik", "Mystik", MYSTIK, G4, [7, 21]),
    ("mystik", "Mystik", HELIX, [(2, "riesig", "riesig"), (3, "gigantisch", "gigantisch")], [7, 21]),
    ("burgen", "Burgen & Festungen", BURGEN, G4, [7, 21]),
    ("kathedralen", "Kathedralen & Tempel", KATHEDRALEN, G4, [7, 21]),
    ("fernost", "Fernost", FERNOST, G4, [7, 21]),
    ("wueste", "Wüstenreich", WUESTE, G4, [7, 21]),
    ("eisreich", "Eisreich", EISREICH, G4, [7, 21]),
    ("unterwasser", "Unterwasserwelt", UNTERWASSER, G4, [7, 21]),
    ("vulkan", "Vulkanreich", VULKAN, G4, [7, 21]),
    ("nether", "Nether-Reich", NETHER, G4, [7, 21]),
    ("endreich", "End-Reich", END, G4, [7, 21]),
    ("dschungel", "Dschungeltempel", DSCHUNGEL, G4, [7, 21]),
    ("wikinger", "Wikingerdorf", WIKINGER, G4, [7, 21]),
    ("markt", "Mittelaltermarkt", MARKT, G4, [7, 21]),
    ("fantasie", "Fantasiehäuser", FANTASIEHAEUSER, [(0, "mittel", "mittel"), (1, "gross", "groß")], [7, 21]),
]
MEER = {"inseln"}
GROSSBILD = {"inseln", "bogen"}

# Kategorie -> (Paket-ID, Paket-Name). Neue Kategorien kommen ab jetzt als Paket.
PAKET_KAT = {"sagenlande": ("sagenlande", "Sagenlande"), "boote": ("boote", "Boote & Schiffe"), "piraten": ("piraten", "Piraten"), "kreaturen": ("kreaturen", "Kreaturen"), "antike": ("antike", "Antike Monumente"), "orklager": ("orklager", "Orklager"), "feenstadt": ("feenstadt", "Feenstadt"), "bienenstadt": ("bienenstadt", "Bienenstadt"), "haeuser": ("haeuser", "Häuser"), "mystik": ("mystik", "Mystik"), "burgen": ("burgen", "Burgen & Festungen"), "kathedralen": ("kathedralen", "Kathedralen & Tempel"), "fernost": ("fernost", "Fernost"), "wueste": ("wueste", "Wüstenreich"), "eisreich": ("eisreich", "Eisreich"), "unterwasser": ("unterwasser", "Unterwasserwelt"), "vulkan": ("vulkan", "Vulkanreich"), "nether": ("nether", "Nether-Reich"), "endreich": ("endreich", "End-Reich"), "dschungel": ("dschungel", "Dschungeltempel"), "wikinger": ("wikinger", "Wikingerdorf"), "markt": ("markt", "Mittelaltermarkt")}
PAKETE = PROJEKT / "pakete"
PAKET_TMP = HIER / "_paket_tmp"

KRATER_DATEIEN = [
    ("ruinenkrater_klein", "klein", (25, 25, 25)),
    ("ruinenkrater_mittel", "mittel", (37, 35, 37)),
    ("ruinenkrater_gross", "gross", (51, 45, 51)),
]


def menue_bild(welt, name, meer=False, ziel=None):
    """128x128-Vorschau mit transparentem Hintergrund für das Menü im Spiel."""
    from PIL import Image
    from vorschau import HG, bild
    img = bild(welt, 360, boden=1, meer=meer).convert("RGBA")
    daten = img.getdata()
    img.putdata([(r, g, b, 0) if (r, g, b) == HG else (r, g, b, a) for r, g, b, a in daten])
    img.thumbnail((124, 124), Image.LANCZOS)
    karte = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    karte.paste(img, ((128 - img.width) // 2, (128 - img.height) // 2), img)
    ziel = ziel or VORSCHAU
    ziel.mkdir(parents=True, exist_ok=True)
    karte.save(ziel / f"{name}.png", optimize=True)


def pakete_bauen(paket_listen):
    """Schreibt pro Paket eine Zip (bitgleich reproduzierbar) und den Index pakete.json."""
    import gzip
    import hashlib
    import io
    import zipfile
    PAKETE.mkdir(exist_ok=True)
    for pid, (pname, eintraege) in paket_listen.items():
        wurzel = PAKET_TMP / pid
        puffer = io.BytesIO()
        with zipfile.ZipFile(puffer, "w", zipfile.ZIP_DEFLATED) as z:
            def dazu(name, daten):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, daten)
            dazu("paket.json", json.dumps({"name": pname, "vorlagen": eintraege}, ensure_ascii=False,
                                          indent=1).encode("utf-8"))
            for datei in sorted(p for p in wurzel.rglob("*") if p.is_file()):
                daten = datei.read_bytes()
                if datei.suffix == ".nbt":     # gzip ohne Zeitstempel -> gleiche Bytes bei gleichem Inhalt
                    roh = gzip.decompress(daten)
                    b = io.BytesIO()
                    with gzip.GzipFile(fileobj=b, mode="wb", compresslevel=9, mtime=0) as gz:
                        gz.write(roh)
                    daten = b.getvalue()
                dazu(datei.relative_to(wurzel).as_posix(), daten)
        (PAKETE / f"{pid}.zip").write_bytes(puffer.getvalue())
        print(f"Paket {pid}.zip: {len(eintraege)} Vorlagen, {len(puffer.getvalue()) / 1e6:.1f} MB")
    index = []
    for zp in sorted(PAKETE.glob("*.zip")):
        daten = zp.read_bytes()
        with zipfile.ZipFile(zp) as z:
            name = json.loads(z.read("paket.json"))["name"]
        index.append({"datei": zp.name, "name": name, "version": hashlib.sha1(daten).hexdigest()[:12],
                      "groesse": len(daten)})
    (PAKETE / "pakete.json").write_text(json.dumps({"pakete": index}, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    bilder = "--ohne-bilder" not in sys.argv
    nur_pakete = "--nur-pakete" in sys.argv or "--paket" in sys.argv
    nur_ids = set(sys.argv[sys.argv.index("--paket") + 1].split(",")) if "--paket" in sys.argv else None
    struktur = ZIEL / "structures"
    for alt in ((PAKET_TMP,) if nur_pakete else (struktur, VORSCHAU, PAKET_TMP)):
        if alt.exists():
            shutil.rmtree(alt)
    paket_listen = {}
    eintraege = []
    vorschau = {}  # Kategorie -> [(Beschriftung, Welt)]
    t0 = time.time()

    for kat, kat_name, tabelle, groessen, seeds in GRUPPEN:
        pk = PAKET_KAT.get(kat)
        if nur_pakete and not pk:
            continue
        if nur_ids is not None and pk[0] not in nur_ids:
            continue
        for art, (titel, funktion) in tabelle.items():
            for g, kuerzel, anzeige in groessen:
                for v, seed in enumerate(seeds, start=1):
                    welt = funktion(seed + 100 * g, g)
                    gruppe = f"{art}_{kuerzel}"
                    vid = f"{gruppe}_{v}" if len(seeds) > 1 else gruppe
                    pfad = (PAKET_TMP / pk[0] / "structures" if pk else struktur) / kat / f"{vid}.nbt"
                    info = exportieren(welt, pfad)
                    # Kontrolle: Datei wieder einlesen
                    zurueck = laden(pfad)
                    assert len(zurueck.bloecke) == sum(1 for b in welt.bloecke.values() if b != 0), (vid, len(zurueck.bloecke), info["bloecke"])
                    eintraege.append({
                        "id": vid, "gruppe": gruppe, "titel": titel, "kategorie": kat, "kategorie_name": kat_name,
                        "groesse": anzeige, "variante": v, "datei": f"structures/{kat}/{vid}.nbt",
                        "anker": info["anker"], "masse": info["groesse"], "bloecke": info["bloecke"],
                    })
                    if kat in MEER or kat in ("boote", "piraten") or art == "segelschiff":
                        eintraege[-1]["hinweis"] = "auf die Wasseroberfläche setzen"
                    if pk:
                        paket_listen.setdefault(pk[0], (pk[1], []))[1].append(eintraege.pop())
                        if v == 1:
                            menue_bild(welt, gruppe, meer=kat in MEER or kat in ("boote", "piraten"), ziel=PAKET_TMP / pk[0] / "bilder")
                        print(f"{vid:34s} {str(info['groesse']):16s} {info['bloecke']:7d} Blöcke  [Paket {pk[0]}]",
                              flush=True)
                        continue
                    if v == 1:
                        menue_bild(welt, gruppe, meer=kat in MEER)
                        vorschau.setdefault((kat, kat_name, anzeige), []).append((titel, welt, info["groesse"]))
                    if kat in MEER or kat in ("boote", "piraten") or art == "segelschiff":
                        eintraege[-1]["hinweis"] = "auf die Wasseroberfläche setzen"
                    print(f"{vid:34s} {str(info['groesse']):16s} {info['bloecke']:7d} Blöcke", flush=True)

    if paket_listen:
        pakete_bauen(paket_listen)
    if nur_pakete:
        return

    # Ruinenkrater (vorhandene Dateien übernehmen)
    for name, kuerzel, anker in KRATER_DATEIEN:
        quelle = KRATER / f"{name}.nbt"
        pfad = struktur / "ruinen" / f"{name}.nbt"
        pfad.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(quelle, pfad)
        w = laden(pfad)
        eintraege.append({
            "id": name, "gruppe": name, "titel": "Ruinenkrater", "kategorie": "ruinen", "kategorie_name": "Ruinen",
            "groesse": {"gross": "groß"}.get(kuerzel, kuerzel), "variante": 1, "datei": f"structures/ruinen/{name}.nbt",
            "anker": list(anker), "masse": list(w.groesse), "bloecke": len(w.bloecke),
        })
        vorschau.setdefault(("krater", "Ruinenkrater", "alle"), []).append((f"Ruinenkrater {kuerzel}", w, w.groesse))
        menue_bild(w, name)

    ZIEL.mkdir(parents=True, exist_ok=True)
    (ZIEL / "vorlagen.json").write_text(json.dumps({"version": 1, "vorlagen": eintraege}, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
    gesamt = sum(p.stat().st_size for p in struktur.rglob("*.nbt"))
    print(f"\n{len(eintraege)} Vorlagen, {gesamt / 1e6:.1f} MB, {time.time() - t0:.0f} s")

    if bilder:
        from vorschau import bild, bogen
        BILDER.mkdir(exist_ok=True)
        for (kat, kat_name, anzeige), liste in vorschau.items():
            gross = kat in GROSSBILD
            zellen = [(f"{t} ({m[1]} hoch)", bild(w, 1100 if gross else 640, boden=2, meer=kat in MEER))
                      for t, w, m in liste]
            spalten = 2 if gross else 4 if len(zellen) > 6 else 3
            titel = f"{kat_name} – {anzeige}" if anzeige != "alle" else kat_name
            bogen(zellen, spalten, zelle=900 if gross else 470, titel=titel).save(BILDER / f"{kat}_{anzeige}.png")
            print("Bild:", kat, anzeige, flush=True)


if __name__ == "__main__":
    main()

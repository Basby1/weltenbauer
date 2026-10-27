"""Erzeugt alle eingebauten Vorlagen für Weltenbauer.

Ausgabe:
  src/main/resources/data/weltenbauer/structures/<kategorie>/<id>.nbt   (auch mit /place template nutzbar)
  src/main/resources/data/weltenbauer/vorlagen.json                    (Liste für /wb vorlage)
  werkzeuge/assets/bilder/*.png                                        (Übersichtsbilder)

Aufruf:  python3 exportieren.py [--ohne-bilder]
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

PROJEKT = HIER.parent.parent
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
    ("fantasie", "Fantasiehäuser", FANTASIEHAEUSER, [(0, "mittel", "mittel"), (1, "gross", "groß")], [7, 21]),
]
MEER = {"inseln"}
GROSSBILD = {"inseln", "bogen"}

KRATER_DATEIEN = [
    ("ruinenkrater_klein", "klein", (25, 25, 25)),
    ("ruinenkrater_mittel", "mittel", (37, 35, 37)),
    ("ruinenkrater_gross", "gross", (51, 45, 51)),
]


def main():
    bilder = "--ohne-bilder" not in sys.argv
    struktur = ZIEL / "structures"
    if struktur.exists():
        shutil.rmtree(struktur)
    eintraege = []
    vorschau = {}  # Kategorie -> [(Beschriftung, Welt)]
    t0 = time.time()

    for kat, kat_name, tabelle, groessen, seeds in GRUPPEN:
        for art, (titel, funktion) in tabelle.items():
            for g, kuerzel, anzeige in groessen:
                for v, seed in enumerate(seeds, start=1):
                    welt = funktion(seed + 100 * g, g)
                    gruppe = f"{art}_{kuerzel}"
                    vid = f"{gruppe}_{v}" if len(seeds) > 1 else gruppe
                    pfad = struktur / kat / f"{vid}.nbt"
                    info = exportieren(welt, pfad)
                    # Kontrolle: Datei wieder einlesen
                    zurueck = laden(pfad)
                    assert len(zurueck.bloecke) == sum(1 for b in welt.bloecke.values() if b != 0), (vid, len(zurueck.bloecke), info["bloecke"])
                    eintraege.append({
                        "id": vid, "gruppe": gruppe, "titel": titel, "kategorie": kat, "kategorie_name": kat_name,
                        "groesse": anzeige, "variante": v, "datei": f"structures/{kat}/{vid}.nbt",
                        "anker": info["anker"], "masse": info["groesse"], "bloecke": info["bloecke"],
                    })
                    if v == 1:
                        vorschau.setdefault((kat, kat_name, anzeige), []).append((titel, welt, info["groesse"]))
                    if kat in MEER:
                        eintraege[-1]["hinweis"] = "auf die Wasseroberfläche setzen"
                    print(f"{vid:34s} {str(info['groesse']):16s} {info['bloecke']:7d} Blöcke", flush=True)

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

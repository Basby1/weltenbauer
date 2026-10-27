# Weltenbauer – Minecraft 1.20.1 (Forge)

Gelände formen, aufräumen und Vorlagen bauen. **Version 0.1** bringt die Aufräum-Befehle mit
Rückgängig-Funktion und den Terraforming-Stab zum Markieren von Bereichen. Pinsel, Werkzeugrad,
Landschaftsgenerator und Asset-Menü folgen in den nächsten Versionen.

## Installieren

1. **Sicherungskopie deiner Welt machen** (CurseForge → Profil → ⋮ → Ordner öffnen → `saves` → Weltordner kopieren).
2. Oben rechts auf dieser Seite unter **Releases** → „Weltenbauer – neueste Version“ die `.jar` herunterladen.
3. Die Datei in den Ordner `mods` deines CurseForge-Profils legen (Profil → ⋮ → Ordner öffnen → `mods`).
4. Minecraft starten.

## Befehle

Alle Befehle beginnen mit `/wb`. Statt eines Radius geht überall auch `auswahl` – dann wirkt der
Befehl nur im Bereich, den du mit dem Terraforming-Stab markiert hast.

| Befehl | Was passiert |
|---|---|
| `/wb schnee entfernen 500` | Schneeschichten und Pulverschnee im Umkreis von 500 Blöcken entfernen. Gras wird wieder grün. Verschneite Blöcke von *Snow! Real Magic!* werden in den Originalblock zurückverwandelt. |
| `/wb schnee entfernen 500 alles` | wie oben, zusätzlich Schneeblöcke |
| `/wb eis auftauen 500` | zugefrorenes Wasser wird wieder Wasser (Packeis/Blaueis bleiben) |
| `/wb laub aufraeumen 200` | schwebende Blätter ohne Baumstamm entfernen |
| `/wb entfernen minecraft:gravel 100` | eine Blocksorte entfernen |
| `/wb ersetzen minecraft:oak_stairs minecraft:spruce_stairs 100` | eine Blocksorte austauschen (Ausrichtung bleibt erhalten) |
| `/wb rueckgaengig` · `/wb wiederholen` | letzte Änderung zurücknehmen / erneut ausführen (bis zu 10 Schritte) |
| `/wb abbrechen` | laufende Aktion stoppen – schon Geändertes lässt sich rückgängig machen |
| `/wb status` | zeigt, was gerade läuft und wie viele Rückgängig-Schritte gespeichert sind |
| `/wb stab` | gibt dir den Terraforming-Stab |
| `/wb auswahl` · `/wb auswahl leeren` | markierten Bereich anzeigen / löschen |
| `/wb hilfe` | Übersicht im Spiel |

**Terraforming-Stab:** Rechtsklick auf einen Block = Ecke 1, Schleichen + Rechtsklick = Ecke 2.

## Sicherheit

- **Blöcke mit Inhalt** (Truhen, Öfen, Create-Maschinen …) werden nie angefasst.
- **Nie besuchte Gebiete werden nicht erzeugt.** Bearbeitet werden nur Chunks, die es schon gibt.
- Große Bereiche werden **Chunk für Chunk** abgearbeitet (höchstens 15 ms pro Tick), damit das Spiel nicht einfriert.
  Ab ca. 400 Chunks fragt Weltenbauer vorher nach.
- Der Rückgängig-Verlauf liegt im Weltordner unter `weltenbauer/verlauf` und bleibt auch nach einem Neustart erhalten.
- Im Einzelspieler darf der Besitzer der Welt die Befehle auch ohne Cheats benutzen.

## Selbst bauen

GitHub baut die Mod bei jeder Änderung automatisch (Reiter **Actions**). Lokal: Java 17 installieren und
`gradlew build` ausführen, die Datei liegt dann in `build/libs/`.

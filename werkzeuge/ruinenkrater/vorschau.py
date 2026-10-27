"""Rendert eine Iso-Vorschau des Ruinen-Kraters (nutzt den Renderer aus Blaupause)."""
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, "/home/claude/Blaupause")
from blaupause.vorschau import iso_bild, ansicht_bild  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from generator import erzeuge  # noqa: E402

FARBEN = {
    "stone_bricks": (122, 122, 122), "mossy_stone_bricks": (104, 121, 86), "cracked_stone_bricks": (118, 117, 118),
    "cobblestone": (128, 127, 128), "mossy_cobblestone": (101, 118, 89), "andesite": (136, 136, 137),
    "stone": (126, 126, 126), "deepslate_tiles": (54, 54, 55), "polished_deepslate": (72, 72, 73), "tuff": (108, 109, 103),
    "grass_block": (107, 150, 66), "dirt": (134, 96, 67), "coarse_dirt": (119, 85, 59), "rooted_dirt": (144, 104, 77),
    "moss_block": (89, 109, 45), "moss_carpet": (89, 109, 45), "water": (52, 90, 190), "lily_pad": (40, 120, 50),
    "grass": (95, 140, 60), "fern": (90, 130, 60), "poppy": (190, 40, 40), "dandelion": (230, 200, 40),
    "azure_bluet": (200, 210, 220), "oxeye_daisy": (220, 220, 210), "cornflower": (80, 110, 200),
    "oak_log": (109, 85, 50), "oak_leaves": (70, 120, 45), "azalea_leaves": (90, 125, 45),
    "flowering_azalea_leaves": (110, 120, 70), "stone_brick_stairs": (122, 122, 122),
    "mossy_stone_brick_stairs": (104, 121, 86), "vine": (60, 110, 35),
}


@dataclass
class B:
    rgb: tuple


def render(R, D, T, seed, ziel: Path):
    grid, P, info = erzeuge(R, D, T, seed)
    farben = []
    for name, _ in P.eintraege:
        kurz = name.split(":")[1]
        farben.append(B(FARBEN.get(kurz, (255, 0, 255))))
    idx = np.where(grid > 0, grid, 0).astype(np.int16)  # Luft/leer = 0
    # Pflanzen und Ranken sind keine vollen Blöcke – für die Vorschau weglassen,
    # Blumen färben stattdessen den Boden darunter leicht ein
    deko = {"grass", "fern", "poppy", "dandelion", "azure_bluet", "oxeye_daisy", "cornflower", "vine", "moss_carpet", "lily_pad"}
    deko_ids = [i for i, (n, _) in enumerate(P.eintraege) if n.split(":")[1] in deko]
    idx[np.isin(idx, deko_ids)] = 0
    # Index i>0 -> farben[i] ; Renderer erwartet liste[i-1]
    liste = farben[1:]
    iso_bild(idx, liste, max_pixel=1400).save(ziel / f"krater_{R}_iso.png")
    ansicht_bild(idx, liste, "oben", 4).save(ziel / f"krater_{R}_oben.png")
    schnitt = idx.copy()
    c = schnitt.shape[0] // 2
    schnitt[:, :, c + 1:] = 0
    iso_bild(schnitt, liste, max_pixel=1400).save(ziel / f"krater_{R}_schnitt.png")
    ansicht_bild(idx, liste, "vorne", 4).save(ziel / f"krater_{R}_vorne.png")
    return info, grid, P


if __name__ == "__main__":
    ziel = Path(sys.argv[5]) if len(sys.argv) > 5 else Path(".")
    ziel.mkdir(parents=True, exist_ok=True)
    info, grid, P = render(*(int(a) for a in sys.argv[1:5]), ziel)
    print(info, "Palette:", len(P.eintraege), "Blöcke (ohne Luft):", int((grid > 0).sum()))

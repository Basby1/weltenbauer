"""Blockzustände wie im Spiel berechnen, bevor eine Vorlage gespeichert wird.

Vorlagen werden ohne Nachbar-Updates gesetzt. Deshalb berechnet Minecraft Verbindungen und Formen nicht selbst:
Zäune, Glasscheiben, Eisengitter und Mauern würden sonst als einzelne Pfosten mit Lücken dastehen, und
Treppen an Dachecken bekämen keine Eckform. Laub wird dauerhaft gemacht, damit es nicht verrottet.
"""

from __future__ import annotations

RICHT = {"north": (0, 0, -1), "south": (0, 0, 1), "east": (1, 0, 0), "west": (-1, 0, 0)}
GEGEN = {"north": "south", "south": "north", "east": "west", "west": "east"}
UHR = {"north": "east", "east": "south", "south": "west", "west": "north"}
GEGENUHR = {v: k for k, v in UHR.items()}

NICHT_VOLL = ("slab", "stairs", "fence", "wall", "pane", "bars", "door", "trapdoor", "leaves", "carpet", "torch",
              "lantern", "chain", "rail", "sign", "banner", "button", "pressure_plate", "lever", "ladder", "vine",
              "flower", "sapling", "grass", "fern", "bush", "rose", "tulip", "poppy", "dandelion", "orchid", "allium",
              "bluet", "daisy", "cornflower", "lily", "mushroom", "snow", "water", "lava", "air", "bed", "candle",
              "pot", "head", "skull", "anvil", "cauldron", "hopper", "lectern", "bell", "campfire", "chest",
              "end_rod", "lightning_rod", "rod", "cobweb", "kelp", "seagrass", "coral", "pickle", "cake", "frame",
              "amethyst_cluster", "_bud", "pointed_dripstone", "dripleaf", "bamboo", "sugar_cane", "cactus",
              "scaffolding", "enchanting_table", "stonecutter", "grindstone", "brewing_stand", "composter",
              "daylight_detector", "petals", "roots", "string", "tripwire", "fire", "pumpkin", "melon", "glass",
              "ice", "barrier", "spawner", "beacon", "conduit", "sculk_sensor", "sculk_shrieker", "egg", "plate",
              "web", "hanging", "moss_carpet", "lichen", "spore", "azalea", "berry", "wart", "crop", "wheat",
              "carrots", "potatoes", "beetroots", "stem", "nylium_", "propagule", "frogspawn", "decorated_pot",
              "piston_head", "repeater", "comparator", "redstone_wire", "farmland", "dirt_path", "soul_sand",
              "honey_block", "mud", "chorus")
VOLL_AUSNAHMEN = ("glass", "ice", "farmland", "dirt_path", "soul_sand", "mud", "honey_block")


def _ist_wand(n):
    k = n[10:] if n.startswith("minecraft:") else n
    return k.endswith("_wall") and not any(t in k for t in ("_wall_", "wall_torch", "wall_sign", "wall_banner",
                                                            "wall_head", "wall_skull", "wall_hanging"))


def _ist_zaun(n):
    return n.endswith("_fence")


def _ist_tor(n):
    return n.endswith("_fence_gate")


def _ist_scheibe(n):
    return n.endswith("glass_pane") or n == "minecraft:iron_bars"


def _ist_treppe(n):
    return n.endswith("_stairs")


def _voll(n):
    """Hat der Block eine tragfähige volle Seite (Zäune/Scheiben/Mauern verbinden sich daran)?"""
    k = n[10:] if n.startswith("minecraft:") else n
    if k.endswith("_glass") or k == "glass" or k in ("ice", "packed_ice", "blue_ice"):
        return True
    if any(t in k for t in NICHT_VOLL):
        return False
    return True


def berechnen(w):
    if not getattr(w, "luecken_lassen", False):
        luecken_schliessen(w)
    schwerkraft(w)
    P = w.P
    B = w.bloecke
    ersatz = getattr(P, "ersatz", {})
    info = {}

    def art(idx):
        r = info.get(idx)
        if r is None:
            name, props = P.eintraege[idx]
            if idx in ersatz or not name.startswith("minecraft:"):
                r = ("mod", name, dict(props))
            elif _ist_tor(name):
                r = ("tor", name, dict(props))
            elif _ist_zaun(name):
                r = ("zaun", name, dict(props))
            elif _ist_scheibe(name):
                r = ("scheibe", name, dict(props))
            elif _ist_wand(name):
                r = ("wand", name, dict(props))
            elif _ist_treppe(name):
                r = ("treppe", name, dict(props))
            elif name.endswith("_leaves"):
                r = ("laub", name, dict(props))
            else:
                r = ("sonst", name, dict(props))
            info[idx] = r
        return r

    def nachbar(p, d):
        q = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
        i = B.get(q)
        return None if i is None else art(i)

    neu = {}
    for p, idx in B.items():
        typ, name, props = art(idx)
        if typ in ("mod", "sonst"):
            continue
        if typ == "laub":
            if props.get("persistent") != "true":
                q = dict(props)
                q["persistent"] = True
                q.setdefault("distance", 7)
                q.setdefault("waterlogged", False)
                neu[p] = P.b(name, **q)
            continue
        if typ in ("zaun", "scheibe", "wand"):
            holz = typ == "zaun" and "nether_brick" not in name
            q = {k: v for k, v in props.items()}
            verb = {}
            for s, d in RICHT.items():
                nb = nachbar(p, d)
                ok = False
                if nb is not None:
                    t2, n2, p2 = nb
                    if t2 == "tor":
                        f = p2.get("facing", "north")
                        ok = typ != "scheibe" and (f in ("north", "south")) == (s in ("east", "west"))
                    elif typ == "zaun":
                        ok = (t2 == "zaun" and (("nether_brick" not in n2) == holz)) or \
                             (t2 in ("sonst", "mod") and _voll(n2))
                    elif typ == "scheibe":
                        ok = t2 in ("scheibe", "wand") or (t2 in ("sonst", "mod") and _voll(n2))
                    else:
                        ok = t2 in ("wand", "scheibe") or (t2 in ("sonst", "mod") and _voll(n2))
                verb[s] = ok
            if typ == "wand":
                oben = B.get((p[0], p[1] + 1, p[2]))
                oben_art = art(oben) if oben is not None else None
                for s in RICHT:
                    if not verb[s]:
                        q[s] = "none"
                    else:
                        hoch = oben_art is not None and (oben_art[0] == "wand" or
                                                         (oben_art[0] in ("sonst", "mod") and _voll(oben_art[1])))
                        q[s] = "tall" if hoch else "low"
                gerade = (verb["north"] and verb["south"] and not verb["east"] and not verb["west"]) or \
                         (verb["east"] and verb["west"] and not verb["north"] and not verb["south"])
                post_oben = oben_art is not None and not (oben_art[0] in ("sonst", "mod") and _voll(oben_art[1])) \
                    and oben_art[0] != "wand"
                wand_oben = oben_art is not None and oben_art[0] == "wand" and \
                    str(oben_art[2].get("up", "true")) == "true"
                q["up"] = (not gerade) or post_oben or wand_oben
            else:
                for s in RICHT:
                    q[s] = verb[s]
            q.setdefault("waterlogged", False)
            if tuple(sorted((k, str(v).lower()) for k, v in q.items())) != tuple(sorted(props.items())):
                neu[p] = P.b(name, **q)
            continue
        if typ == "treppe":
            f = props.get("facing", "north")
            h = props.get("half", "bottom")
            form = "straight"
            vorn = nachbar(p, RICHT[f])
            if vorn and vorn[0] == "treppe" and vorn[2].get("half", "bottom") == h:
                f1 = vorn[2].get("facing", "north")
                if (RICHT[f1][0] == 0) != (RICHT[f][0] == 0) and _kann(nachbar(p, RICHT[GEGEN[f1]]), f, h):
                    form = "outer_left" if f1 == GEGENUHR[f] else "outer_right"
            if form == "straight":
                hinten = nachbar(p, RICHT[GEGEN[f]])
                if hinten and hinten[0] == "treppe" and hinten[2].get("half", "bottom") == h:
                    f2 = hinten[2].get("facing", "north")
                    if (RICHT[f2][0] == 0) != (RICHT[f][0] == 0) and _kann(nachbar(p, RICHT[f2]), f, h):
                        form = "inner_left" if f2 == GEGENUHR[f] else "inner_right"
            if props.get("shape", "straight") != form:
                q = dict(props)
                q["shape"] = form
                neu[p] = P.b(name, **q)
    B.update(neu)
    return len(neu)


def _kann(nb, f, h):
    if nb is None or nb[0] != "treppe":
        return True
    return nb[2].get("facing", "north") != f or nb[2].get("half", "bottom") != h


# ---------------------------------------------------------------------------- Lücken schließen

_FLACH_NICHT = ("pane", "fence", "door", "trapdoor", "bars", "chain", "torch", "lantern", "carpet", "vine", "rail",
                "flower", "grass", "fern", "sapling", "bush", "button", "pressure", "sign", "banner", "candle", "pot",
                "lever", "ladder", "snow", "water", "lava", "leaves", "rod", "rose", "tulip", "poppy", "dandelion",
                "lily", "kelp", "seagrass", "coral", "mushroom", "wall", "head", "skull", "bell", "campfire", "web",
                "bed", "lectern", "anvil", "cauldron", "chest", "barrel", "hopper", "dripleaf", "bamboo", "cane",
                "azure", "orchid", "allium", "daisy", "cornflower", "pickle", "egg", "cake", "frame", "cluster",
                "bud", "pointed", "hanging", "string", "tripwire", "end_rod", "fire", "air", "glass", "ice",
                "petals", "roots", "moss_carpet", "lichen", "chorus", "scaffolding")


def luecken_schliessen(w):
    """Schließt einzelne Durchblick-Löcher in dünnen Wänden, Decken und Dächern (eine fehlende Zelle, ringsum in
    der Fläche geschlossen, davor und dahinter Luft). Gibt die Anzahl gefüllter Zellen zurück."""
    P = w.P
    B = w.bloecke
    cache = {}

    def fl(p):
        b = B.get(p)
        if b is None:
            return None
        r = cache.get(b)
        if r is None:
            n = P.eintraege[b][0]
            r = not any(k in n for k in _FLACH_NICHT)
            cache[b] = r
        return b if r else None

    kand = set()
    for (x, y, z) in B:
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            q = (x + d[0], y + d[1], z + d[2])
            if q not in B and q[1] >= 1:
                kand.add(q)
    neu = {}
    for (x, y, z) in kand:
        ach = []
        for a in range(3):
            e = [0, 0, 0]
            e[a] = 1
            n1 = fl((x + e[0], y + e[1], z + e[2]))
            n2 = fl((x - e[0], y - e[1], z - e[2]))
            ach.append((n1, n2) if n1 is not None and n2 is not None else None)
        if sum(1 for v in ach if v) < 2:
            continue
        for c in range(3):
            if ach[c]:
                continue
            d = [0, 0, 0]
            d[c] = 1
            if (x + d[0], y + d[1], z + d[2]) in B or (x - d[0], y - d[1], z - d[2]) in B:
                continue
            duenn = 0
            for a in range(3):
                if a == c:
                    continue
                for sg in (-1, 1):
                    e = [0, 0, 0]
                    e[a] = sg
                    n = (x + e[0], y + e[1], z + e[2])
                    if (n[0] + d[0], n[1] + d[1], n[2] + d[2]) not in B or \
                            (n[0] - d[0], n[1] - d[1], n[2] - d[2]) not in B:
                        duenn += 1
            if duenn < 3:
                continue
            paare = [v for i, v in enumerate(ach) if v and i != c]
            # gleiche Nachbarn auf einer Achse bevorzugen (Treppenreihe im Dach, Wandmuster)
            wahl = None
            for (a1, a2) in paare:
                if a1 == a2:
                    wahl = a1
                    break
            if wahl is None:
                voll = [b for pr in paare for b in pr if not any(k in P.eintraege[b][0] for k in ("stairs", "slab"))]
                alle = voll or [b for pr in paare for b in pr]
                wahl = max(set(alle), key=alle.count)
            neu[(x, y, z)] = wahl
            break
    B.update(neu)
    return len(neu)


FALLEND = {"minecraft:sand": "sandstone", "minecraft:red_sand": "red_sandstone", "minecraft:gravel": "tuff",
           "minecraft:suspicious_sand": "sandstone", "minecraft:suspicious_gravel": "tuff"}


def schwerkraft(w):
    """Sand, Kies und Betonpulver ohne Block darunter würden im Spiel herabfallen: durch feste Blöcke ersetzen."""
    if not w.bloecke:
        return 0
    ymin = min(p[1] for p in w.bloecke)
    P = w.P
    ers = {}
    n = 0
    for (x, y, z), b in list(w.bloecke.items()):
        if y <= ymin or (x, y - 1, z) in w.bloecke:
            continue
        name = P.eintraege[b][0]
        ziel = FALLEND.get(name)
        if ziel is None and name.endswith("_concrete_powder"):
            ziel = name[10:].replace("_powder", "")
        if ziel:
            if ziel not in ers:
                ers[ziel] = P.b(ziel)
            w.bloecke[(x, y, z)] = ers[ziel]
            n += 1
    return n

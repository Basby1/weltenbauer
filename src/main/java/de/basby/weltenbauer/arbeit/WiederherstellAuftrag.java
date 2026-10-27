package de.basby.weltenbauer.arbeit;

import it.unimi.dsi.fastutil.ints.IntArrayList;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Spielt ein Protokoll zurück (für Rückgängig und Wiederholen). Dabei wird selbst wieder
 * mitgeschrieben, was vorher dort war – so lässt sich auch das Rückgängigmachen rückgängig machen.
 */
public class WiederherstellAuftrag extends Auftrag {

    public enum Richtung { RUECKGAENGIG, WIEDERHOLEN }

    private final Protokoll quelle;
    private final Long2ObjectOpenHashMap<IntArrayList> nachChunks;
    private final Richtung richtung;

    public WiederherstellAuftrag(ServerLevel level, UUID besitzer, Protokoll quelle, Richtung richtung) {
        this(level, besitzer, quelle, richtung, quelle.nachChunks());
    }

    private WiederherstellAuftrag(ServerLevel level, UUID besitzer, Protokoll quelle, Richtung richtung,
                                  Long2ObjectOpenHashMap<IntArrayList> nachChunks) {
        super(level, besitzer,
                (richtung == Richtung.RUECKGAENGIG ? "Rückgängig: " : "Wiederholen: ") + quelle.titel(),
                chunkListe(nachChunks), quelle.titel());
        this.quelle = quelle;
        this.nachChunks = nachChunks;
        this.richtung = richtung;
    }

    private static List<ChunkPos> chunkListe(Long2ObjectOpenHashMap<IntArrayList> karte) {
        List<ChunkPos> liste = new ArrayList<>(karte.size());
        for (long schluessel : karte.keySet()) {
            liste.add(new ChunkPos(schluessel));
        }
        return liste;
    }

    public Richtung richtung() {
        return richtung;
    }

    @Override
    protected void bearbeite(LevelChunk chunk) {
        IntArrayList eintraege = nachChunks.get(chunk.getPos().toLong());
        if (eintraege == null) {
            return;
        }
        BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
        for (int k = 0; k < eintraege.size(); k++) {
            int i = eintraege.getInt(k);
            pos.set(quelle.position(i));
            BlockState ziel = quelle.zustand(i);
            CompoundTag zielDaten = quelle.daten(i);

            BlockState jetzt = level.getBlockState(pos);
            CompoundTag jetztDaten = null;
            if (jetzt.hasBlockEntity()) {
                BlockEntity inhalt = level.getBlockEntity(pos);
                if (inhalt != null) {
                    jetztDaten = inhalt.saveWithFullMetadata();
                }
            }
            if (jetzt == ziel && zielDaten == null) {
                continue;
            }
            level.setBlock(pos, ziel, Block.UPDATE_CLIENTS);
            if (zielDaten != null) {
                BlockEntity inhalt = level.getBlockEntity(pos);
                if (inhalt != null) {
                    inhalt.load(zielDaten);
                    inhalt.setChanged();
                    level.sendBlockUpdated(pos, ziel, ziel, Block.UPDATE_CLIENTS);
                }
            }
            protokoll.merke(pos.asLong(), jetzt, jetztDaten);
            geaendert++;
        }
    }
}

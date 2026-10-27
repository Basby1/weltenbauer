package de.basby.weltenbauer.arbeit;

import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LevelChunkSection;

import java.util.UUID;

/** Ein Auftrag, der in einem Bereich bestimmte Blöcke findet und verändert. */
public class BlockAuftrag extends Auftrag {

    private final Bereich bereich;
    private final Aktion aktion;

    public BlockAuftrag(ServerLevel level, UUID besitzer, String titel, Bereich bereich, Aktion aktion) {
        super(level, besitzer, titel, bereich.chunks());
        this.bereich = bereich;
        this.aktion = aktion;
    }

    @Override
    protected void bearbeite(LevelChunk chunk) {
        int minX = chunk.getPos().getMinBlockX();
        int minZ = chunk.getPos().getMinBlockZ();
        LevelChunkSection[] abschnitte = chunk.getSections();
        BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();

        for (int i = 0; i < abschnitte.length; i++) {
            LevelChunkSection abschnitt = abschnitte[i];
            if (abschnitt == null || abschnitt.hasOnlyAir() || !abschnitt.maybeHas(aktion::betrifft)) {
                continue;
            }
            int basisY = SectionPos.sectionToBlockCoord(chunk.getSectionYFromSectionIndex(i));
            if (basisY + 15 < bereich.minY() || basisY > bereich.maxY()) {
                continue;
            }
            for (int y = 0; y < 16; y++) {
                for (int z = 0; z < 16; z++) {
                    for (int x = 0; x < 16; x++) {
                        BlockState alt = abschnitt.getBlockState(x, y, z);
                        if (!aktion.betrifft(alt)) {
                            continue;
                        }
                        int wx = minX + x, wy = basisY + y, wz = minZ + z;
                        if (!bereich.enthaelt(wx, wy, wz)) {
                            continue;
                        }
                        pos.set(wx, wy, wz);
                        if (alt.hasBlockEntity() && !aktion.darfBlockInhalt(alt)) {
                            geschuetzt++;
                            continue;
                        }
                        BlockState neu = aktion.neuerZustand(alt, level, pos);
                        if (neu == null) {
                            nichtWiederherstellbar++;
                            continue;
                        }
                        if (neu == alt) {
                            continue;
                        }
                        CompoundTag alteDaten = null;
                        if (alt.hasBlockEntity()) {
                            BlockEntity inhalt = level.getBlockEntity(pos);
                            if (inhalt != null) {
                                alteDaten = inhalt.saveWithFullMetadata();
                            }
                        }
                        if (level.setBlock(pos, neu, Block.UPDATE_CLIENTS)) {
                            protokoll.merke(pos.asLong(), alt, alteDaten);
                            geaendert++;
                        }
                    }
                }
            }
        }
    }

    /** Was mit einem gefundenen Block passieren soll. */
    public interface Aktion {
        /** Schnelle Vorprüfung nur anhand des Blockzustands. */
        boolean betrifft(BlockState zustand);

        /**
         * Der neue Zustand. {@code null} = konnte nicht umgewandelt werden (wird gezählt),
         * derselbe Zustand = nichts tun.
         */
        BlockState neuerZustand(BlockState alt, ServerLevel level, BlockPos pos);

        /** Darf diese Aktion Blöcke mit Inhalt (Truhen, Maschinen …) verändern? Standard: nein. */
        default boolean darfBlockInhalt(BlockState zustand) {
            return false;
        }
    }
}

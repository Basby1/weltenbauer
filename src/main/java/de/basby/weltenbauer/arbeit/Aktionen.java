package de.basby.weltenbauer.arbeit;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.SnowLayerBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;

import java.util.HashSet;
import java.util.Set;

/** Die Aktionen hinter den /wb-Befehlen. */
public final class Aktionen {

    private Aktionen() {
    }

    // ------------------------------------------------------------------ Schnee

    private static Set<Block> srmBloecke;

    /** Alle Blöcke der Mod „Snow! Real Magic!" (Namensraum snowrealmagic). */
    private static Set<Block> srmBloecke() {
        if (srmBloecke == null) {
            Set<Block> s = new HashSet<>();
            for (ResourceLocation id : BuiltInRegistries.BLOCK.keySet()) {
                if (id.getNamespace().equals("snowrealmagic")) {
                    s.add(BuiltInRegistries.BLOCK.get(id));
                }
            }
            srmBloecke = s;
        }
        return srmBloecke;
    }

    /**
     * Entfernt Schneeschichten und Pulverschnee. Verschneite Blöcke von „Snow! Real Magic!"
     * (z. B. verschneite Treppen, Zäune oder Pflanzen) werden in den Originalblock zurückverwandelt.
     *
     * @param alles auch Schneeblöcke entfernen
     */
    public static BlockAuftrag.Aktion schnee(boolean alles) {
        final Set<Block> srm = srmBloecke();
        return new BlockAuftrag.Aktion() {
            @Override
            public boolean betrifft(BlockState z) {
                Block b = z.getBlock();
                return b instanceof SnowLayerBlock || b == Blocks.POWDER_SNOW
                        || (alles && b == Blocks.SNOW_BLOCK) || srm.contains(b);
            }

            @Override
            public BlockState neuerZustand(BlockState alt, ServerLevel level, BlockPos pos) {
                Block b = alt.getBlock();
                if (srm.contains(b)) {
                    BlockState original = srmOriginal(level, pos);
                    if (original != null) {
                        return original;
                    }
                    if (b instanceof SnowLayerBlock) {
                        return Blocks.AIR.defaultBlockState();
                    }
                    return null; // unbekannter Aufbau – lieber nicht anfassen
                }
                return Blocks.AIR.defaultBlockState();
            }

            @Override
            public boolean darfBlockInhalt(BlockState z) {
                // Die verschneiten Blöcke von Snow! Real Magic speichern den Originalblock als Inhalt
                return srm.contains(z.getBlock());
            }
        };
    }

    /** Liest aus einem verschneiten Snow!-Real-Magic-Block den ursprünglichen Block aus. */
    private static BlockState srmOriginal(ServerLevel level, BlockPos pos) {
        BlockEntity inhalt = level.getBlockEntity(pos);
        if (inhalt == null) {
            return null;
        }
        return sucheZustand(inhalt.saveWithoutMetadata(), 0);
    }

    private static BlockState sucheZustand(CompoundTag tag, int tiefe) {
        for (String schluessel : tag.getAllKeys()) {
            Tag t = tag.get(schluessel);
            if (t instanceof CompoundTag c) {
                if (c.contains("Name", Tag.TAG_STRING) && c.getString("Name").contains(":")) {
                    BlockState s = NbtUtils.readBlockState(BuiltInRegistries.BLOCK.asLookup(), c);
                    if (!s.isAir() && !srmBloecke().contains(s.getBlock())) {
                        return s;
                    }
                }
                if (tiefe < 2) {
                    BlockState s = sucheZustand(c, tiefe + 1);
                    if (s != null) {
                        return s;
                    }
                }
            }
        }
        return null;
    }

    // ------------------------------------------------------------------ Eis

    /** Zugefrorenes Wasser wird wieder zu Wasser (Packeis und Blaueis bleiben, die sind meist gewollt). */
    public static BlockAuftrag.Aktion eisAuftauen() {
        return new BlockAuftrag.Aktion() {
            @Override
            public boolean betrifft(BlockState z) {
                return z.is(Blocks.ICE) || z.is(Blocks.FROSTED_ICE);
            }

            @Override
            public BlockState neuerZustand(BlockState alt, ServerLevel level, BlockPos pos) {
                return level.dimensionType().ultraWarm() ? Blocks.AIR.defaultBlockState()
                        : Blocks.WATER.defaultBlockState();
            }
        };
    }

    // ------------------------------------------------------------------ Laub

    /** Entfernt Blätter, die zu keinem Baumstamm mehr gehören (schwebende Blätterreste). */
    public static BlockAuftrag.Aktion laubAufraeumen() {
        return new BlockAuftrag.Aktion() {
            @Override
            public boolean betrifft(BlockState z) {
                return z.is(BlockTags.LEAVES)
                        && z.hasProperty(LeavesBlock.PERSISTENT) && !z.getValue(LeavesBlock.PERSISTENT)
                        && z.hasProperty(LeavesBlock.DISTANCE) && z.getValue(LeavesBlock.DISTANCE) >= 7;
            }

            @Override
            public BlockState neuerZustand(BlockState alt, ServerLevel level, BlockPos pos) {
                return Blocks.AIR.defaultBlockState();
            }
        };
    }

    // ------------------------------------------------------------------ Entfernen / Ersetzen

    /** Entfernt alle Blöcke einer Sorte (Eigenschaften wie Ausrichtung egal). */
    public static BlockAuftrag.Aktion entfernen(Block sorte) {
        return new BlockAuftrag.Aktion() {
            @Override
            public boolean betrifft(BlockState z) {
                return z.getBlock() == sorte;
            }

            @Override
            public BlockState neuerZustand(BlockState alt, ServerLevel level, BlockPos pos) {
                return Blocks.AIR.defaultBlockState();
            }
        };
    }

    /**
     * Ersetzt alle Blöcke einer Sorte durch einen anderen. Eigenschaften, die beide Blöcke haben
     * (z. B. Ausrichtung von Treppen), werden übernommen – außer sie wurden im Befehl ausdrücklich angegeben.
     */
    public static BlockAuftrag.Aktion ersetzen(Block von, BlockState zu, Set<Property<?>> festgelegt) {
        return new BlockAuftrag.Aktion() {
            @Override
            public boolean betrifft(BlockState z) {
                return z.getBlock() == von;
            }

            @Override
            public BlockState neuerZustand(BlockState alt, ServerLevel level, BlockPos pos) {
                BlockState neu = zu;
                for (Property<?> p : alt.getProperties()) {
                    if (neu.hasProperty(p) && !festgelegt.contains(p)) {
                        neu = uebernehme(alt, neu, p);
                    }
                }
                return neu;
            }
        };
    }

    private static <T extends Comparable<T>> BlockState uebernehme(BlockState von, BlockState zu, Property<T> p) {
        return zu.setValue(p, von.getValue(p));
    }
}

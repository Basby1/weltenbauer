package de.basby.weltenbauer.arbeit;

import it.unimi.dsi.fastutil.ints.Int2ObjectMap;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.ints.IntArrayList;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.longs.LongArrayList;
import it.unimi.dsi.fastutil.objects.Object2IntOpenHashMap;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.IntArrayTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.LongArrayTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Merkt sich, was eine Aktion verändert hat: Position, alter Blockzustand und – falls vorhanden –
 * die Daten des Block-Inhalts (Truhen usw.). Damit kann alles rückgängig gemacht werden.
 */
public class Protokoll {
    /** Ab dieser Größe wird nicht mehr mitgeschrieben (Schutz vor Speichermangel). */
    public static final int MAXIMUM = 20_000_000;

    private final ResourceKey<Level> dimension;
    private final String titel;
    private final List<BlockState> palette = new ArrayList<>();
    private final Object2IntOpenHashMap<BlockState> paletteIndex = new Object2IntOpenHashMap<>();
    private final LongArrayList positionen = new LongArrayList();
    private final IntArrayList zustaende = new IntArrayList();
    private final Int2ObjectOpenHashMap<CompoundTag> blockDaten = new Int2ObjectOpenHashMap<>();
    private boolean voll;

    public Protokoll(ResourceKey<Level> dimension, String titel) {
        this.dimension = dimension;
        this.titel = titel;
        paletteIndex.defaultReturnValue(-1);
    }

    public void merke(long pos, BlockState alterZustand, CompoundTag alteDaten) {
        if (positionen.size() >= MAXIMUM) {
            voll = true;
            return;
        }
        int idx = paletteIndex.getInt(alterZustand);
        if (idx < 0) {
            idx = palette.size();
            palette.add(alterZustand);
            paletteIndex.put(alterZustand, idx);
        }
        if (alteDaten != null) {
            blockDaten.put(positionen.size(), alteDaten);
        }
        positionen.add(pos);
        zustaende.add(idx);
    }

    public int groesse() {
        return positionen.size();
    }

    public boolean istVoll() {
        return voll;
    }

    public boolean istLeer() {
        return positionen.isEmpty();
    }

    public ResourceKey<Level> dimension() {
        return dimension;
    }

    public String titel() {
        return titel;
    }

    public long position(int i) {
        return positionen.getLong(i);
    }

    public BlockState zustand(int i) {
        return palette.get(zustaende.getInt(i));
    }

    public CompoundTag daten(int i) {
        return blockDaten.get(i);
    }

    /** Einträge nach Chunk sortiert (für die Wiederherstellung Chunk für Chunk). */
    public Long2ObjectOpenHashMap<IntArrayList> nachChunks() {
        Long2ObjectOpenHashMap<IntArrayList> karte = new Long2ObjectOpenHashMap<>();
        for (int i = 0; i < positionen.size(); i++) {
            long p = positionen.getLong(i);
            int x = net.minecraft.core.BlockPos.getX(p);
            int z = net.minecraft.core.BlockPos.getZ(p);
            long chunk = ChunkPos.asLong(x >> 4, z >> 4);
            karte.computeIfAbsent(chunk, k -> new IntArrayList()).add(i);
        }
        return karte;
    }

    // ------------------------------------------------------------------ Speichern / Laden

    public void speichern(File datei) throws IOException {
        CompoundTag t = new CompoundTag();
        t.putString("dim", dimension.location().toString());
        t.putString("titel", titel);
        ListTag pal = new ListTag();
        for (BlockState s : palette) {
            pal.add(NbtUtils.writeBlockState(s));
        }
        t.put("palette", pal);
        t.put("pos", new LongArrayTag(positionen.toLongArray()));
        t.put("zustand", new IntArrayTag(zustaende.toIntArray()));
        ListTag daten = new ListTag();
        for (Int2ObjectMap.Entry<CompoundTag> e : blockDaten.int2ObjectEntrySet()) {
            CompoundTag d = new CompoundTag();
            d.putInt("i", e.getIntKey());
            d.put("nbt", e.getValue());
            daten.add(d);
        }
        t.put("daten", daten);
        datei.getParentFile().mkdirs();
        NbtIo.writeCompressed(t, datei);
    }

    public static Protokoll laden(File datei) throws IOException {
        CompoundTag t = NbtIo.readCompressed(datei);
        ResourceKey<Level> dim = ResourceKey.create(Registries.DIMENSION, new ResourceLocation(t.getString("dim")));
        Protokoll p = new Protokoll(dim, t.getString("titel"));
        ListTag pal = t.getList("palette", Tag.TAG_COMPOUND);
        for (int i = 0; i < pal.size(); i++) {
            BlockState s = NbtUtils.readBlockState(BuiltInRegistries.BLOCK.asLookup(), pal.getCompound(i));
            p.palette.add(s);
        }
        long[] pos = t.getLongArray("pos");
        int[] zust = t.getIntArray("zustand");
        int n = Math.min(pos.length, zust.length);
        for (int i = 0; i < n; i++) {
            p.positionen.add(pos[i]);
            p.zustaende.add(zust[i]);
        }
        ListTag daten = t.getList("daten", Tag.TAG_COMPOUND);
        for (int i = 0; i < daten.size(); i++) {
            CompoundTag d = daten.getCompound(i);
            p.blockDaten.put(d.getInt("i"), d.getCompound("nbt"));
        }
        return p;
    }
}

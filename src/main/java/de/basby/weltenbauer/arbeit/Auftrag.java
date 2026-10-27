package de.basby.weltenbauer.arbeit;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.chunk.LevelChunk;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.Iterator;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/**
 * Ein länger laufender Auftrag, der Chunk für Chunk abgearbeitet wird – verteilt über viele
 * Server-Ticks, damit das Spiel nicht einfriert.
 *
 * Wichtig: Es werden nur Chunks bearbeitet, die schon existieren. Noch nie besuchte Gebiete werden
 * NICHT neu erzeugt. Nicht geladene Chunks werden kurz geladen und danach automatisch wieder entladen.
 */
public abstract class Auftrag {

    /** Ticket, mit dem Chunks kurz geladen werden; verfällt nach 200 Ticks (10 Sekunden) von selbst. */
    private static final TicketType<ChunkPos> TICKET =
            TicketType.create("weltenbauer", Comparator.comparingLong(ChunkPos::toLong), 200);

    /** So viele Chunks werden gleichzeitig vorbereitet (Existenz geprüft / geladen). */
    private static final int FENSTER = 16;

    protected final ServerLevel level;
    protected final UUID besitzer;
    protected final String titel;
    protected final Protokoll protokoll;

    private final List<ChunkPos> chunks;
    private final List<Eintrag> fenster = new ArrayList<>();
    private int naechster;

    protected long geaendert;
    protected long geschuetzt;
    protected long nichtWiederherstellbar;
    private int chunksFertig;
    private int chunksUebersprungen;
    private boolean abgebrochen;

    protected Auftrag(ServerLevel level, UUID besitzer, String titel, List<ChunkPos> chunks) {
        this(level, besitzer, titel, chunks, titel);
    }

    /** @param protokollTitel Name, unter dem die Änderung im Rückgängig-Verlauf steht */
    protected Auftrag(ServerLevel level, UUID besitzer, String titel, List<ChunkPos> chunks, String protokollTitel) {
        this.level = level;
        this.besitzer = besitzer;
        this.titel = titel;
        this.chunks = chunks;
        this.protokoll = new Protokoll(level.dimension(), protokollTitel);
    }

    /** Bearbeitet einen geladenen Chunk. Läuft auf dem Server-Thread. */
    protected abstract void bearbeite(LevelChunk chunk);

    /**
     * Dürfen fehlende (nie erzeugte) Chunks erzeugt werden? Standard: nein – Aufräum-Befehle sollen
     * keine neue Welt erzeugen. Beim Setzen einer Vorlage ist es aber nötig.
     */
    protected boolean erzeugeFehlende() {
        return false;
    }

    /** Arbeitet, bis die Frist (System.nanoTime) erreicht ist oder auf Ladevorgänge gewartet werden muss. */
    public void arbeite(long frist) {
        while (!abgebrochen && System.nanoTime() < frist) {
            while (fenster.size() < FENSTER && naechster < chunks.size()) {
                fenster.add(new Eintrag(chunks.get(naechster++)));
            }
            if (fenster.isEmpty()) {
                return;
            }
            boolean fortschritt = false;
            Iterator<Eintrag> it = fenster.iterator();
            while (it.hasNext() && System.nanoTime() < frist) {
                if (it.next().schritt()) {
                    it.remove();
                    fortschritt = true;
                }
            }
            if (!fortschritt) {
                return; // alles wartet auf die Festplatte – im nächsten Tick weiter
            }
        }
    }

    public boolean fertig() {
        return abgebrochen || (naechster >= chunks.size() && fenster.isEmpty());
    }

    public void abbrechen() {
        abgebrochen = true;
    }

    public boolean wurdeAbgebrochen() {
        return abgebrochen;
    }

    public int anteilProzent() {
        if (chunks.isEmpty()) {
            return 100;
        }
        return (int) Math.min(100, (chunksFertig + chunksUebersprungen) * 100L / chunks.size());
    }

    public int chunksGesamt() {
        return chunks.size();
    }

    public int chunksFertig() {
        return chunksFertig;
    }

    public int chunksUebersprungen() {
        return chunksUebersprungen;
    }

    public long geaendert() {
        return geaendert;
    }

    public long geschuetzt() {
        return geschuetzt;
    }

    public long nichtWiederherstellbar() {
        return nichtWiederherstellbar;
    }

    public String titel() {
        return titel;
    }

    public UUID besitzer() {
        return besitzer;
    }

    public Protokoll protokoll() {
        return protokoll;
    }

    public ServerLevel level() {
        return level;
    }

    // ------------------------------------------------------------------ Chunk-Lader

    private enum Zustand { NEU, PRUEFEN, LADEN }

    private final class Eintrag {
        final ChunkPos pos;
        Zustand zustand = Zustand.NEU;
        CompletableFuture<Optional<CompoundTag>> existenz;
        int ladeStart;

        Eintrag(ChunkPos pos) {
            this.pos = pos;
        }

        /** @return true, wenn dieser Chunk erledigt ist (bearbeitet oder übersprungen). */
        boolean schritt() {
            LevelChunk geladen = level.getChunkSource().getChunkNow(pos.x, pos.z);
            if (geladen != null) {
                bearbeite(geladen);
                chunksFertig++;
                return true;
            }
            switch (zustand) {
                case NEU -> {
                    if (erzeugeFehlende()) {
                        level.getChunkSource().addRegionTicket(TICKET, pos, 0, pos);
                        ladeStart = level.getServer().getTickCount();
                        zustand = Zustand.LADEN;
                        return false;
                    }
                    existenz = level.getChunkSource().chunkMap.read(pos);
                    zustand = Zustand.PRUEFEN;
                    return false;
                }
                case PRUEFEN -> {
                    if (!existenz.isDone()) {
                        return false;
                    }
                    Optional<CompoundTag> daten;
                    try {
                        daten = existenz.join();
                    } catch (RuntimeException fehler) {
                        chunksUebersprungen++;
                        return true;
                    }
                    if (daten.isEmpty() || !istFertigerChunk(daten.get())) {
                        // Gebiet wurde nie erzeugt – nichts zu tun, und vor allem nichts neu erzeugen
                        chunksFertig++;
                        return true;
                    }
                    level.getChunkSource().addRegionTicket(TICKET, pos, 0, pos);
                    ladeStart = level.getServer().getTickCount();
                    zustand = Zustand.LADEN;
                    return false;
                }
                case LADEN -> {
                    int gewartet = level.getServer().getTickCount() - ladeStart;
                    if (gewartet > (erzeugeFehlende() ? 2400 : 600)) {
                        chunksUebersprungen++;
                        return true;
                    }
                    if (gewartet > 0 && gewartet % 150 == 0) {
                        // Ticket auffrischen, falls das Laden länger dauert
                        level.getChunkSource().addRegionTicket(TICKET, pos, 0, pos);
                    }
                    return false;
                }
            }
            return false;
        }
    }

    private static boolean istFertigerChunk(CompoundTag daten) {
        String status = daten.getString("Status");
        return status.equals("minecraft:full") || status.equals("full");
    }
}

package de.basby.weltenbauer.vorlagen;

import de.basby.weltenbauer.Weltenbauer;
import de.basby.weltenbauer.arbeit.Auftragsverwaltung;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import org.jetbrains.annotations.Nullable;

import java.io.IOException;
import java.util.List;
import java.util.Random;

/**
 * Bauwerk-Stab: trägt eine ausgewählte Vorlage. Halten = Umriss-Vorschau, Rechtsklick = setzen,
 * Schleichen + Rechtsklick = drehen (0°, 90°, 180°, 270°, zufällig).
 */
public class BauwerkStab extends Item {

    public static final String VORLAGE = "vorlage";
    public static final String DREHUNG = "drehung";
    private static final String[] DREH_TEXT = {"0°", "90°", "180°", "270°", "zufällig"};
    private static final Random ZUFALL = new Random();

    public BauwerkStab(Properties eigenschaften) {
        super(eigenschaften);
    }

    public static String vorlage(ItemStack stack) {
        CompoundTag t = stack.getTag();
        return t != null && t.contains(VORLAGE) ? t.getString(VORLAGE) : null;
    }

    public static int drehung(ItemStack stack) {
        CompoundTag t = stack.getTag();
        return t != null ? Math.floorMod(t.getInt(DREHUNG), 5) : 0;
    }

    private static Rotation rotation(int d) {
        return switch (d == 4 ? ZUFALL.nextInt(4) : d) {
            case 1 -> Rotation.CLOCKWISE_90;
            case 2 -> Rotation.CLOCKWISE_180;
            case 3 -> Rotation.COUNTERCLOCKWISE_90;
            default -> Rotation.NONE;
        };
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player spieler, InteractionHand hand) {
        ItemStack stack = spieler.getItemInHand(hand);
        if (level.isClientSide || !(spieler instanceof ServerPlayer sp)) {
            return InteractionResultHolder.success(stack);
        }
        if (sp.isShiftKeyDown()) {
            int d = (drehung(stack) + 1) % 5;
            stack.getOrCreateTag().putInt(DREHUNG, d);
            sp.displayClientMessage(Component.literal("Drehung: " + DREH_TEXT[d]).withStyle(ChatFormatting.GOLD), true);
            return InteractionResultHolder.consume(stack);
        }
        String name = vorlage(stack);
        if (name == null) {
            sp.displayClientMessage(Component.literal("Noch keine Vorlage gewählt – Menü mit Taste B öffnen.")
                    .withStyle(ChatFormatting.YELLOW), true);
            return InteractionResultHolder.consume(stack);
        }
        if (Auftragsverwaltung.laeuft()) {
            sp.displayClientMessage(Component.literal("Es wird noch gebaut: " + Auftragsverwaltung.aktuell().titel())
                    .withStyle(ChatFormatting.YELLOW), true);
            return InteractionResultHolder.consume(stack);
        }
        Vorlagen.Eintrag e = Vorlagen.finden(name);
        if (e == null) {
            sp.displayClientMessage(Component.literal("Vorlage „" + name + "“ gibt es nicht mehr.")
                    .withStyle(ChatFormatting.RED), true);
            return InteractionResultHolder.consume(stack);
        }
        try {
            Vorlagen.Vorlage v = Vorlagen.laden(e, false);
            BlockPos ziel = VorlagenBefehle.ziel(sp);
            Auftragsverwaltung.starte(VorlageAuftrag.erstellen(sp.serverLevel(), sp.getUUID(), v, ziel,
                    rotation(drehung(stack)), Mirror.NONE));
        } catch (IOException | RuntimeException fehler) {
            sp.displayClientMessage(Component.literal("Vorlage konnte nicht gelesen werden: " + fehler.getMessage())
                    .withStyle(ChatFormatting.RED), false);
        }
        sp.getCooldowns().addCooldown(this, 10);
        return InteractionResultHolder.consume(stack);
    }

    /** Legt eine Vorlage auf den Stab in der Hand – oder gibt einen neuen Stab. */
    public static void waehlen(ServerPlayer sp, String name, Vorlagen.Eintrag e) {
        ItemStack stack = sp.getMainHandItem();
        if (!(stack.getItem() instanceof BauwerkStab)) {
            stack = sp.getOffhandItem();
        }
        if (!(stack.getItem() instanceof BauwerkStab)) {
            stack = new ItemStack(Weltenbauer.BAUWERK_STAB.get());
            stack.getOrCreateTag().putString(VORLAGE, name);
            if (sp.getMainHandItem().isEmpty()) {
                sp.setItemInHand(InteractionHand.MAIN_HAND, stack);
            } else if (!sp.getInventory().add(stack)) {
                sp.drop(stack, false);
            }
        } else {
            stack.getOrCreateTag().putString(VORLAGE, name);
        }
        sp.displayClientMessage(Component.literal("Bauwerk-Stab: " + e.titel() + " (" + e.groesse() + ") – "
                + "Rechtsklick setzt, Schleichen + Rechtsklick dreht.").withStyle(ChatFormatting.GOLD), true);
    }

    /** Live-Umriss, solange der Spieler den Stab mit einer Vorlage in der Hand hält. */
    public static void vorschau(ServerPlayer sp) {
        ItemStack stack = sp.getMainHandItem();
        if (!(stack.getItem() instanceof BauwerkStab)) {
            return;
        }
        String name = vorlage(stack);
        if (name == null) {
            return;
        }
        Vorlagen.Eintrag e = Vorlagen.erster(name);
        if (e == null) {
            return;
        }
        BlockPos[] m = Vorlagen.masse(e);
        if (m == null) {
            return;
        }
        int d = drehung(stack);
        BlockPos ziel = VorlagenBefehle.ziel(sp);
        BlockPos[] k = VorlageAuftrag.kasten(m[0], m[1], ziel, Mirror.NONE, d == 4 ? Rotation.NONE : rotation(d));
        Umriss.einmal(sp, k[0], k[1], ziel);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> zeilen, TooltipFlag flag) {
        String name = vorlage(stack);
        zeilen.add(Component.literal("Vorlage: " + (name == null ? "– (Taste B)" : name)).withStyle(ChatFormatting.AQUA));
        zeilen.add(Component.literal("Drehung: " + DREH_TEXT[drehung(stack)]).withStyle(ChatFormatting.GRAY));
        zeilen.add(Component.literal("Rechtsklick: setzen (rückgängig: /wb rueckgaengig)").withStyle(ChatFormatting.GRAY));
        zeilen.add(Component.literal("Schleichen + Rechtsklick: drehen").withStyle(ChatFormatting.GRAY));
        zeilen.add(Component.literal("Taste B: Vorlagen-Menü").withStyle(ChatFormatting.DARK_AQUA));
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return vorlage(stack) != null;
    }
}

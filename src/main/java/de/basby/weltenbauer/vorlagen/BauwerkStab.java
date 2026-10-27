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
        // Absetzen, Ausrichten und Bestätigen passieren auf dem Client (Geisterbild + Werkzeugleiste);
        // gebaut wird über /wb vorlage drucken.
        return InteractionResultHolder.consume(spieler.getItemInHand(hand));
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
                + "Rechtsklick: absetzen und ausrichten.").withStyle(ChatFormatting.GOLD), true);
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
        zeilen.add(Component.literal("Vorlage: " + (name == null ? "– (Rechtsklick öffnet das Menü)" : name))
                .withStyle(ChatFormatting.AQUA));
        zeilen.add(Component.literal("Rechtsklick: absetzen, nochmal: bauen / Blaupause").withStyle(ChatFormatting.GRAY));
        zeilen.add(Component.literal("Strg+Mausrad: Werkzeug · Mausrad: verstellen").withStyle(ChatFormatting.GRAY));
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return vorlage(stack) != null;
    }
}

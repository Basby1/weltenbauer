package de.basby.weltenbauer;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/**
 * Der Terraforming-Stab. In Version 0.1 markiert er Bereiche für die /wb-Befehle:
 * Rechtsklick = Ecke 1, Schleichen + Rechtsklick = Ecke 2.
 * Pinsel, Werkzeugrad und Asset-Menü folgen in den nächsten Versionen.
 */
public class TerraformingStab extends Item {

    public TerraformingStab(Properties eigenschaften) {
        super(eigenschaften);
    }

    @Override
    public InteractionResult useOn(UseOnContext kontext) {
        Level level = kontext.getLevel();
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        if (!(kontext.getPlayer() instanceof ServerPlayer spieler)) {
            return InteractionResult.PASS;
        }
        BlockPos pos = kontext.getClickedPos();
        boolean zweite = spieler.isShiftKeyDown();
        Auswahl.setze(spieler, pos, zweite);
        spieler.displayClientMessage(Component.literal((zweite ? "Ecke 2" : "Ecke 1") + " gesetzt: "
                        + pos.getX() + " / " + pos.getY() + " / " + pos.getZ() + "  ")
                .withStyle(ChatFormatting.GOLD)
                .append(Component.literal(Auswahl.beschreibung(spieler)).withStyle(ChatFormatting.GRAY)), true);
        return InteractionResult.CONSUME;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> zeilen, TooltipFlag flag) {
        zeilen.add(Component.literal("Rechtsklick: Ecke 1 markieren").withStyle(ChatFormatting.GRAY));
        zeilen.add(Component.literal("Schleichen + Rechtsklick: Ecke 2").withStyle(ChatFormatting.GRAY));
        zeilen.add(Component.literal("Dann z. B. /wb schnee entfernen auswahl").withStyle(ChatFormatting.DARK_GRAY));
        zeilen.add(Component.literal("Pinsel & Asset-Menü folgen bald").withStyle(ChatFormatting.DARK_AQUA));
    }
}

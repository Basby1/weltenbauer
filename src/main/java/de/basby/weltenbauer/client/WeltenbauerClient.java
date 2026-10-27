package de.basby.weltenbauer.client;

import com.mojang.blaze3d.platform.InputConstants;
import de.basby.weltenbauer.Weltenbauer;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.commands.Commands;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterClientCommandsEvent;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;

/** Nur auf dem Client: Taste B und /wbmenue öffnen das Vorlagen-Menü. */
public final class WeltenbauerClient {

    public static final KeyMapping MENUE_TASTE = new KeyMapping("key.weltenbauer.menue",
            InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_B, "key.categories.weltenbauer");

    private static boolean oeffnenImNaechstenTick;

    private WeltenbauerClient() {
    }

    @Mod.EventBusSubscriber(modid = Weltenbauer.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
    public static final class ModEvents {
        @SubscribeEvent
        public static void tasten(RegisterKeyMappingsEvent event) {
            event.register(MENUE_TASTE);
        }
    }

    @Mod.EventBusSubscriber(modid = Weltenbauer.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
    public static final class ForgeEvents {
        @SubscribeEvent
        public static void tick(TickEvent.ClientTickEvent event) {
            if (event.phase != TickEvent.Phase.END) {
                return;
            }
            Minecraft mc = Minecraft.getInstance();
            while (MENUE_TASTE.consumeClick()) {
                if (mc.screen == null && mc.player != null) {
                    mc.setScreen(new VorlagenMenue());
                }
            }
            if (oeffnenImNaechstenTick && mc.screen == null && mc.player != null) {
                oeffnenImNaechstenTick = false;
                mc.setScreen(new VorlagenMenue());
            }
        }

        @SubscribeEvent
        public static void befehle(RegisterClientCommandsEvent event) {
            event.getDispatcher().register(Commands.literal("wbmenue").executes(c -> {
                oeffnenImNaechstenTick = true;
                return 1;
            }));
        }
    }
}

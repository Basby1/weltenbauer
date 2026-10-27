package de.basby.weltenbauer.client;

import com.mojang.blaze3d.platform.InputConstants;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import de.basby.weltenbauer.Weltenbauer;
import de.basby.weltenbauer.vorlagen.BauwerkStab;
import de.basby.weltenbauer.vorlagen.VorlageAuftrag;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.InputEvent;
import net.minecraftforge.client.event.RegisterClientCommandsEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;

/** Nur auf dem Client: Taste B, Werkzeugleiste, Geisterbilder, Blaupausen und Client-Befehle. */
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

        @SubscribeEvent
        public static void overlays(RegisterGuiOverlaysEvent event) {
            event.registerAbove(VanillaGuiOverlay.HOTBAR.id(), "werkzeugleiste", Hud::zeichnen);
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
            Platzierung.tick();
            Blaupausen.tick();
        }

        @SubscribeEvent
        public static void mausrad(InputEvent.MouseScrollingEvent event) {
            Minecraft mc = Minecraft.getInstance();
            if (mc.screen != null || mc.player == null) {
                return;
            }
            boolean strg = Screen.hasControlDown();
            if (mc.player.getMainHandItem().getItem() instanceof BauwerkStab) {
                if (Platzierung.mausrad(event.getScrollDelta(), strg)) {
                    event.setCanceled(true);
                }
            } else if (strg && Blaupausen.schichtImBlick(event.getScrollDelta())) {
                event.setCanceled(true);
            }
        }

        @SubscribeEvent
        public static void klick(InputEvent.InteractionKeyMappingTriggered event) {
            Minecraft mc = Minecraft.getInstance();
            if (!event.isUseItem() || event.getHand() != InteractionHand.MAIN_HAND || mc.player == null) {
                return;
            }
            if (mc.player.getMainHandItem().getItem() instanceof BauwerkStab) {
                if (Platzierung.rechtsklick(mc.player.isShiftKeyDown())) {
                    event.setCanceled(true);
                    event.setSwingHand(false);
                }
            }
        }

        @SubscribeEvent
        public static void welt(RenderLevelStageEvent event) {
            if (event.getStage() != RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS) {
                return;
            }
            Minecraft mc = Minecraft.getInstance();
            PoseStack ps = event.getPoseStack();
            Vec3 kamera = event.getCamera().getPosition();
            Blaupausen.zeichnen(ps, event.getProjectionMatrix(), kamera);
            if (!Platzierung.sichtbar()) {
                return;
            }
            BlockPos ziel = Platzierung.ziel();
            Platzierung.geist().zeichnen(ps, event.getProjectionMatrix(), kamera, ziel);
            // Rahmen um die ganze Vorlage
            BlockPos[] k = VorlageAuftrag.kasten(Platzierung.vorlage.groesse(), Platzierung.vorlage.anker(), ziel,
                    Platzierung.spiegel(), Platzierung.drehung());
            MultiBufferSource.BufferSource quelle = mc.renderBuffers().bufferSource();
            VertexConsumer linien = quelle.getBuffer(RenderType.lines());
            ps.pushPose();
            ps.translate(-kamera.x, -kamera.y, -kamera.z);
            boolean ab = Platzierung.abgesetzt();
            LevelRenderer.renderLineBox(ps, linien, new AABB(k[0].getX(), k[0].getY(), k[0].getZ(),
                            k[1].getX() + 1, k[1].getY() + 1, k[1].getZ() + 1),
                    ab ? 0.91f : 0.6f, ab ? 0.69f : 0.8f, ab ? 0.29f : 1.0f, 1.0f);
            LevelRenderer.renderLineBox(ps, linien, new AABB(ziel), 1.0f, 0.4f, 0.2f, 1.0f);
            ps.popPose();
            quelle.endBatch(RenderType.lines());
        }

        @SubscribeEvent
        public static void befehle(RegisterClientCommandsEvent event) {
            event.getDispatcher().register(Commands.literal("wbmenue").executes(c -> {
                oeffnenImNaechstenTick = true;
                return 1;
            }));
            event.getDispatcher().register(Commands.literal("wbblaupause")
                    .then(Commands.literal("drucken").executes(c -> Blaupausen.drucken()))
                    .then(Commands.literal("entfernen").executes(c -> Blaupausen.entfernenNaechste()))
                    .then(Commands.literal("alle_entfernen").executes(c -> Blaupausen.alleEntfernen()))
                    .then(Commands.literal("schicht")
                            .then(Commands.argument("nummer", IntegerArgumentType.integer(0, 512))
                                    .executes(c -> {
                                        Blaupausen.Blaupause b = Blaupausen.naechste(96);
                                        if (b == null) {
                                            return 0;
                                        }
                                        b.schicht = IntegerArgumentType.getInteger(c, "nummer");
                                        b.signatur = Long.MIN_VALUE;
                                        return 1;
                                    }))));
        }
    }
}

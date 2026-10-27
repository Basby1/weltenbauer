package de.basby.weltenbauer.client;

import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexBuffer;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.blaze3d.vertex.VertexFormat;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.block.BlockRenderDispatcher;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockAndTintGetter;
import net.minecraft.world.level.ColorResolver;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.lighting.LevelLightEngine;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.client.model.data.ModelData;
import org.joml.Matrix4f;

import java.util.List;

/**
 * Durchsichtiges Geisterbild einer Vorlage. Wird einmal in einen Vertex-Puffer gebaut und dann jedes
 * Bild nur noch gezeichnet – so bleiben auch große Vorlagen flüssig.
 */
public class Geist {

    private VertexBuffer puffer;
    private int bloecke;

    /** Ein Block des Geisterbilds: Weltposition, Zustand und Färbung (0 = normal, 1 = falsch/rot). */
    public record Teil(BlockPos pos, BlockState zustand, int art) {
    }

    public int bloecke() {
        return bloecke;
    }

    public boolean leer() {
        return puffer == null;
    }

    /**
     * Baut das Geisterbild neu.
     *
     * @param teile    die zu zeichnenden Blöcke (Weltkoordinaten)
     * @param umgebung alle Blöcke der Vorlage (für das Ausblenden verdeckter Flächen)
     * @param ursprung Bezugspunkt; gespeichert wird relativ dazu (Genauigkeit)
     */
    public void bauen(List<Teil> teile, Long2ObjectOpenHashMap<BlockState> umgebung, BlockPos ursprung) {
        schliessen();
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || teile.isEmpty()) {
            return;
        }
        BlockRenderDispatcher renderer = mc.getBlockRenderer();
        BufferBuilder builder = new BufferBuilder(1 << 20);
        builder.begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.BLOCK);
        GeistWelt welt = new GeistWelt(umgebung);
        PoseStack ps = new PoseStack();
        RandomSource zufall = RandomSource.create();
        int gezeichnet = 0;
        for (Teil t : teile) {
            BlockState s = t.zustand();
            if (s.getRenderShape() != RenderShape.MODEL) {
                continue;
            }
            ps.pushPose();
            ps.translate(t.pos().getX() - ursprung.getX(), t.pos().getY() - ursprung.getY(),
                    t.pos().getZ() - ursprung.getZ());
            Faerber f = t.art() == 1 ? new Faerber(builder, 1.0f, 0.25f, 0.25f, 0.65f)
                    : new Faerber(builder, 0.75f, 0.9f, 1.0f, 0.5f);
            try {
                renderer.renderBatched(s, t.pos(), welt, ps, f, true, zufall, ModelData.EMPTY, null);
                gezeichnet++;
            } catch (RuntimeException ignoriert) {
                // einzelne exotische Modelle überspringen
            }
            ps.popPose();
        }
        BufferBuilder.RenderedBuffer fertig = builder.end();
        if (gezeichnet == 0) {
            fertig.release();
            return;
        }
        puffer = new VertexBuffer(VertexBuffer.Usage.STATIC);
        puffer.bind();
        puffer.upload(fertig);
        VertexBuffer.unbind();
        bloecke = gezeichnet;
    }

    /** Zeichnet das Geisterbild mit Ursprung an der angegebenen Weltposition. */
    public void zeichnen(PoseStack ps, Matrix4f projektion, Vec3 kamera, BlockPos ursprung) {
        if (puffer == null) {
            return;
        }
        ps.pushPose();
        ps.translate(ursprung.getX() - kamera.x, ursprung.getY() - kamera.y, ursprung.getZ() - kamera.z);
        RenderType typ = RenderType.translucent();
        typ.setupRenderState();
        puffer.bind();
        puffer.drawWithShader(ps.last().pose(), projektion, GameRenderer.getRendertypeTranslucentShader());
        VertexBuffer.unbind();
        typ.clearRenderState();
        ps.popPose();
    }

    public void schliessen() {
        if (puffer != null) {
            puffer.close();
            puffer = null;
        }
        bloecke = 0;
    }

    // ------------------------------------------------------------------ Hilfsklassen

    /** Färbt jeden Punkt ein, macht ihn durchsichtig und voll beleuchtet. */
    private static final class Faerber implements VertexConsumer {
        private final VertexConsumer ziel;
        private final float r, g, b, a;

        Faerber(VertexConsumer ziel, float r, float g, float b, float a) {
            this.ziel = ziel;
            this.r = r;
            this.g = g;
            this.b = b;
            this.a = a;
        }

        @Override
        public void vertex(float x, float y, float z, float rot, float gruen, float blau, float alpha, float u, float v,
                           int overlay, int licht, float nx, float ny, float nz) {
            ziel.vertex(x, y, z, rot * r, gruen * g, blau * b, a, u, v, overlay, LightTexture.FULL_BRIGHT, nx, ny, nz);
        }

        @Override
        public VertexConsumer vertex(double x, double y, double z) {
            return ziel.vertex(x, y, z);
        }

        @Override
        public VertexConsumer color(int rot, int gruen, int blau, int alpha) {
            return ziel.color((int) (rot * r), (int) (gruen * g), (int) (blau * b), (int) (255 * a));
        }

        @Override
        public VertexConsumer uv(float u, float v) {
            return ziel.uv(u, v);
        }

        @Override
        public VertexConsumer overlayCoords(int u, int v) {
            return ziel.overlayCoords(u, v);
        }

        @Override
        public VertexConsumer uv2(int u, int v) {
            return ziel.uv2(LightTexture.FULL_BRIGHT & 0xFFFF, LightTexture.FULL_BRIGHT >> 16);
        }

        @Override
        public VertexConsumer normal(float x, float y, float z) {
            return ziel.normal(x, y, z);
        }

        @Override
        public void endVertex() {
            ziel.endVertex();
        }

        @Override
        public void defaultColor(int rot, int gruen, int blau, int alpha) {
            ziel.defaultColor(rot, gruen, blau, alpha);
        }

        @Override
        public void unsetDefaultColor() {
            ziel.unsetDefaultColor();
        }
    }

    /** Eine Mini-Welt aus den Vorlagen-Blöcken, damit verdeckte Flächen nicht gezeichnet werden. */
    private static final class GeistWelt implements BlockAndTintGetter {
        private final Long2ObjectOpenHashMap<BlockState> bloecke;
        private final Minecraft mc = Minecraft.getInstance();

        GeistWelt(Long2ObjectOpenHashMap<BlockState> bloecke) {
            this.bloecke = bloecke;
        }

        @Override
        public float getShade(Direction richtung, boolean schatten) {
            return mc.level.getShade(richtung, schatten);
        }

        @Override
        public LevelLightEngine getLightEngine() {
            return mc.level.getLightEngine();
        }

        @Override
        public int getBlockTint(BlockPos pos, ColorResolver farbe) {
            return mc.level.getBlockTint(pos, farbe);
        }

        @Override
        public BlockEntity getBlockEntity(BlockPos pos) {
            return null;
        }

        @Override
        public BlockState getBlockState(BlockPos pos) {
            BlockState s = bloecke.get(pos.asLong());
            return s != null ? s : Blocks.AIR.defaultBlockState();
        }

        @Override
        public FluidState getFluidState(BlockPos pos) {
            return getBlockState(pos).getFluidState();
        }

        @Override
        public int getHeight() {
            return mc.level.getHeight();
        }

        @Override
        public int getMinBuildHeight() {
            return mc.level.getMinBuildHeight();
        }
    }
}

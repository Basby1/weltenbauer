package de.basby.weltenbauer;

import de.basby.weltenbauer.arbeit.Auftragsverwaltung;
import de.basby.weltenbauer.befehle.WbBefehle;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * Weltenbauer – Hauptklasse.
 *
 * Version 0.1: Aufräum-Befehle (/wb …) mit Rückgängig-Funktion und der Terraforming-Stab
 * zum Markieren von Bereichen.
 */
@Mod(Weltenbauer.MOD_ID)
public class Weltenbauer {
    public static final String MOD_ID = "weltenbauer";

    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, MOD_ID);
    public static final RegistryObject<Item> STAB = ITEMS.register("terraforming_stab",
            () -> new TerraformingStab(new Item.Properties().stacksTo(1)));

    public Weltenbauer() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        ITEMS.register(modBus);
        modBus.addListener(Weltenbauer::kreativTab);

        MinecraftForge.EVENT_BUS.addListener(Weltenbauer::befehle);
        MinecraftForge.EVENT_BUS.addListener(Weltenbauer::serverTick);
        MinecraftForge.EVENT_BUS.addListener(Weltenbauer::serverStopp);
    }

    private static void kreativTab(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.TOOLS_AND_UTILITIES) {
            event.accept(STAB);
        }
    }

    private static void befehle(RegisterCommandsEvent event) {
        WbBefehle.registrieren(event.getDispatcher(), event.getBuildContext());
    }

    private static void serverTick(TickEvent.ServerTickEvent event) {
        if (event.phase == TickEvent.Phase.END) {
            Auftragsverwaltung.tick();
        }
    }

    private static void serverStopp(ServerStoppingEvent event) {
        Auftragsverwaltung.serverStoppt();
    }
}

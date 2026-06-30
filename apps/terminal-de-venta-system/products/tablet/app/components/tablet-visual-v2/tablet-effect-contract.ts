export const TABLET_VISUAL_V2_EFFECTS = [
  {
    id: "softglass-surface",
    component: "PrismaSoftCard",
    cssHook: "data-prisma-effect~='softglass-surface'",
    intent: "Clear frosted panel with inner highlight and quiet depth."
  },
  {
    id: "inner-highlight",
    component: "PrismaSoftCard",
    cssHook: "prisma-v2-inner-highlight",
    intent: "Top edge reflection that keeps light surfaces legible."
  },
  {
    id: "rim-light",
    component: "PrismaLiquidAction",
    cssHook: "prisma-v2-rim-light",
    intent: "Cyan blue lavender action edge for the primary next step."
  },
  {
    id: "liquid-glow",
    component: "PrismaLiquidAction",
    cssHook: "data-prisma-effect~='liquid-glow'",
    intent: "Contained glow inside primary Tablet actions."
  },
  {
    id: "pressed-depth",
    component: "PrismaLiquidAction PrismaGlassControl PrismaSoftCard",
    cssHook: "data-prisma-effect~='pressed-depth'",
    intent: "Small tactile depression on press without layout shift."
  },
  {
    id: "selected-pulse",
    component: "PrismaStatusChip",
    cssHook: "data-state='selected'",
    intent: "Subtle selected state for payment method and dock items."
  },
  {
    id: "ticket-total-pulse",
    component: "PrismaSoftCard",
    cssHook: "data-prisma-effect~='ticket-total-pulse'",
    intent: "Total area feedback when ticket is ready to charge."
  },
  {
    id: "product-added-echo",
    component: "PrismaSoftCard",
    cssHook: "data-prisma-effect~='product-added-echo'",
    intent: "Product card echo after add interactions."
  },
  {
    id: "dock-active-glow",
    component: "PrismaCommandDock",
    cssHook: "data-prisma-effect~='dock-active-glow'",
    intent: "Bottom command dock active state without covering modals."
  },
  {
    id: "modal-depth-dim",
    component: "PrismaModalShell",
    cssHook: "data-prisma-effect~='modal-depth-dim'",
    intent: "Fixed overlay dim and blur that blocks background interaction."
  },
  {
    id: "method-selected-aura",
    component: "PrismaSoftCard",
    cssHook: "data-prisma-effect~='method-selected-aura'",
    intent: "Payment method selected aura."
  },
  {
    id: "focus-halo",
    component: "PrismaLiquidAction PrismaGlassControl PrismaModalShell",
    cssHook: ":focus-visible",
    intent: "Accessible focus halo with non-color-only edge."
  },
  {
    id: "success-sweep",
    component: "PrismaLiquidAction",
    cssHook: "data-status='success'",
    intent: "Short confirmation sweep."
  },
  {
    id: "disabled-frost",
    component: "PrismaLiquidAction PrismaGlassControl",
    cssHook: "data-status='disabled'",
    intent: "Disabled state remains clear and unmistakable."
  },
  {
    id: "surface-breathing-glow",
    component: "PrismaRouteSurface",
    cssHook: "data-prisma-effect~='surface-breathing-glow'",
    intent: "Subtle living light in route surfaces without distracting from operations."
  }
] as const;

export type TabletVisualV2Effect = (typeof TABLET_VISUAL_V2_EFFECTS)[number]["id"];

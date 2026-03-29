import { PITCH_VALUATION_ECONOMICS, type PitchScreenSlug } from "@hitech/contracts";
import {
  buildPitchDeckViewModel,
  buildScreen01ViewModel,
  buildScreen02ViewModel,
  buildScreen03ViewModel,
  buildScreen04ViewModel
} from "../../../lib/pitch/deck-view-model";
import type { PitchShellFrameModel } from "../shell/types";

const HERO_SUBTITLE_BY_SLUG: Partial<Record<PitchScreenSlug, string>> = {
  "01-double-engine":
    "Arquitectura híbrida para valor operativo y plataforma digital en una sola tesis.",
  "02-industrial-flow":
    "Flujo industrial recurrente, cobertura continua y disciplina de ejecución medible.",
  "03-hitech-os":
    "Infraestructura digital propietaria con trazabilidad y control de activos críticos.",
  "04-valuation":
    "Deal en 2 etapas: $100k → entrega 30d → +$200k con factura SRG → opción de equity.",
  "05-inventory-foundation":
    "Control room farmacéutico: RBAC, suppliers, SKU y vault en ejecución determinística.",
  "06-shipments-receiving":
    "Control room farmacéutico: customs pack, receiving y quarantine con compuertas de riesgo."
};

function createHeroMetrics() {
  const economics = PITCH_VALUATION_ECONOMICS;
  const stage1K = Math.round(economics.deal.stage1CashUsd / 1000);
  const stage2K = Math.round(economics.deal.stage2CashUsd / 1000);

  return [
    {
      id: "traction",
      label: "TRACTION",
      value: `${economics.params.tractionInvoicedModules} módulos facturados (histórico)`,
      tone: "teal" as const
    },
    {
      id: "today",
      label: "TODAY",
      value: `${economics.params.wedgeModules} módulos · entrega 30 días (Etapa 1: $${stage1K}k)`,
      tone: "cyan" as const
    },
    {
      id: "cash",
      label: "CASH",
      value: "Factura día 30 · pago net 60 (cash ~día 90)",
      tone: "teal" as const
    },
    {
      id: "stage-2",
      label: "STAGE 2",
      value: `+$${stage2K}k con factura SRG (habilita ${economics.params.monthlyCadenceModules}/mes → TARGET ${economics.params.targetModules})`,
      tone: "gold" as const
    }
  ];
}

export function buildPitchShellFrameModel(activeSlug?: PitchScreenSlug): PitchShellFrameModel {
  const deckModel = buildPitchDeckViewModel(undefined, activeSlug);

  return {
    hero: {
      kicker: "Keystone Pitch",
      title: activeSlug
        ? deckModel.indexRoutes.find((route) => route.slug === activeSlug)?.title ??
          "Keystone Pitch Deck"
        : "Keystone Pitch Deck",
      subtitle:
        (activeSlug ? HERO_SUBTITLE_BY_SLUG[activeSlug] : undefined) ??
        "Contracts-first investor narrative with deterministic execution and premium UX.",
      deckIdentity: {
        label: "Deck ID",
        value: `${deckModel.meta.deckId}@${deckModel.meta.version}`
      },
      metrics: createHeroMetrics()
    },
    nav: {
      links: deckModel.links,
      ...(activeSlug ? { activeSlug } : {})
    },
    progress: {
      current: deckModel.currentIndex,
      total: deckModel.totalScreens,
      label: deckModel.progressLabel,
      ...(deckModel.previous?.href ? { previousHref: deckModel.previous.href } : {}),
      ...(deckModel.next?.href ? { nextHref: deckModel.next.href } : {})
    },
    breadcrumbs: [
      {
        label: "Mission"
      },
      {
        label: "Pitch"
      },
      {
        label:
          activeSlug !== undefined
            ? deckModel.indexRoutes.find((route) => route.slug === activeSlug)?.title ?? "Screen"
            : "Overview"
      }
    ]
  };
}

export const PITCH_SCREEN_MODEL_CACHE = {
  screen01: buildScreen01ViewModel(),
  screen02: buildScreen02ViewModel(),
  screen03: buildScreen03ViewModel(),
  screen04: buildScreen04ViewModel()
} as const;

import type { PitchScreenSlug } from "@hitech/contracts";
import {
  buildPitchDeckViewModel,
  buildScreen01ViewModel,
  buildScreen02ViewModel,
  buildScreen03ViewModel,
  buildScreen04ViewModel,
  type PitchDeckViewModel
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
    "Narrativa de múltiplo superior con estructura financiera defendible para inversión.",
  "05-inventory-foundation":
    "Control room farmacéutico: RBAC, suppliers, SKU y vault en ejecución determinística.",
  "06-shipments-receiving":
    "Control room farmacéutico: customs pack, receiving y quarantine con compuertas de riesgo."
};

function createHeroMetrics(model: PitchDeckViewModel) {
  return [
    {
      id: "installed-base",
      label: "Installed Base",
      value: model.spotlight.installedBase,
      tone: "teal" as const
    },
    {
      id: "monthly-flow",
      label: "Monthly Flow",
      value: model.spotlight.monthlyFlow,
      tone: "cyan" as const
    },
    {
      id: "annual-utility",
      label: "Annual Utility",
      value: model.spotlight.annualUtility,
      tone: "gold" as const
    },
    {
      id: "valuation",
      label: "Valuation",
      value: model.spotlight.valuationRange,
      tone: "neutral" as const
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
      metrics: createHeroMetrics(deckModel)
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
        label: "Mission",
        href: "/"
      },
      {
        label: "Pitch",
        href: "/pitch"
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

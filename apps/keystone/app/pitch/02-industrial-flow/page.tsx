import { PITCH_DECK_FIXTURE, PITCH_SCREEN_FIXTURES } from "@hitech/contracts";
import { LayerFlagsProvider } from "@hitech/ui-kit";
import { PitchShell, ScreenIndustrialFlow } from "../../../components/pitch";
import { PitchLayerDevTools } from "../../../components/pitch/debug/pitch-layer-dev-tools";
import { buildPitchShellFrameModel } from "../../../components/pitch/view-model/pitch-shell-model";
import {
  resolvePitchSearchParams,
  resolvePitchLayerFlags,
  type PitchSearchParamsProps
} from "../../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default async function PitchIndustrialFlowPage({ searchParams }: PitchSearchParamsProps) {
  const resolved = resolvePitchLayerFlags(await resolvePitchSearchParams(searchParams));
  const debugVisible = resolved.debug && process.env.NODE_ENV !== "production";
  const deck = PITCH_DECK_FIXTURE;
  const screen = PITCH_SCREEN_FIXTURES["02-industrial-flow"];
  const shellModel = buildPitchShellFrameModel(screen.slug);
  const screenTitle = "CORE HITECH — OPERACIÓN INDUSTRIAL INSTITUCIONAL";
  const shellModelInstitutional = {
    ...shellModel,
    hero: {
      ...shellModel.hero,
      title: "CORE HITECH — OPERACIÓN INDUSTRIAL INSTITUCIONAL",
      subtitle:
        "Gobernanza + estándares + evidencia: operación repetible, auditable y escalable multi-sitio.",
      metrics: [
        {
          id: "standards-stack",
          label: "Standards Stack",
          value: "OSHA · ANSI · NFPA · NOM-STPS · ISO 45001/14001 (aligned)",
          tone: "teal" as const
        },
        {
          id: "governance-model",
          label: "Governance Model",
          value: "DG · HSE · Supervisión · Campo (accountability)",
          tone: "cyan" as const
        },
        {
          id: "audit-trail",
          label: "Audit Trail",
          value: "Version control · ID único · repositorio autorizado",
          tone: "teal" as const
        },
        {
          id: "digital-backbone",
          label: "Digital Backbone",
          value: "SmartService · ServiceLogix · HealthRadar · ConditionScore · FailMatrix",
          tone: "gold" as const
        }
      ]
    },
    nav: {
      ...shellModel.nav,
      links: deck.navigation.links.map((link) =>
        link.slug === screen.slug
          ? {
              ...link,
              title: screenTitle
            }
          : link
      )
    },
    breadcrumbs: shellModel.breadcrumbs.map((item, index) =>
      index === shellModel.breadcrumbs.length - 1
        ? {
            ...item,
            label: screenTitle
          }
        : item
    )
  };

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell model={shellModelInstitutional}>
        <ScreenIndustrialFlow screen={screen} />
      </PitchShell>
      <PitchLayerDevTools visible={debugVisible} />
    </LayerFlagsProvider>
  );
}

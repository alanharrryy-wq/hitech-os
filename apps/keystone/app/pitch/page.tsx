import Link from "next/link";
import { LayerFlagsProvider, GlassCard, InsetPanel } from "@hitech/ui-kit";
import { PITCH_DECK_FIXTURE } from "@hitech/contracts";
import { PitchLayerDevTools, PitchShell } from "../../components/pitch";
import {
  resolvePitchLayerFlags,
  type PitchSearchParamsProps
} from "../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default async function PitchIndexPage({ searchParams }: PitchSearchParamsProps) {
  const resolvedSearchParams = await Promise.resolve(searchParams ?? {});
  const resolved = resolvePitchLayerFlags(resolvedSearchParams as any);
  const deck = PITCH_DECK_FIXTURE;

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell
        title="Keystone Pitch Deck"
        subtitle="Contracts-first pitch module with deterministic screen fixtures"
        nav={{ links: deck.navigation.links }}
      >
        <GlassCard className="p-4" tone="default" backdrop="off">
          <InsetPanel title="Pantallas" description="Selecciona una ruta de pitch">
            <ul className="m-0 grid list-disc gap-2 pl-5">
              {deck.navigation.links.map((link) => (
                <li key={link.slug}>
                  <Link
                    href={link.href}
                    className="text-sm font-medium text-[hsl(var(--ui-accent))] underline-offset-4 hover:underline"
                  >
                    {link.title}
                  </Link>
                </li>
              ))}
            </ul>
          </InsetPanel>
        </GlassCard>
      </PitchShell>
      <PitchLayerDevTools visible={resolved.debug} />
    </LayerFlagsProvider>
  );
}

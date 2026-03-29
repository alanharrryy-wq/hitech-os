import { createMockProvider } from "@hitech/ui-kit";
import { NextResponse } from "next/server";
import { rejectIfProduction } from "../../../../../../lib/dev-kpi/dev-only";
import { listDatasets } from "../../../../../../lib/dev-kpi/vault";
import { validateDatasetResponse } from "../../../../../../lib/dev-kpi/validation";

interface SeedRouteContext {
  readonly params: Promise<{ seed: string }> | { seed: string };
}

async function resolveSeed(context: SeedRouteContext): Promise<string> {
  const params = await context.params;
  const seed = decodeURIComponent(params.seed ?? "").trim();
  if (seed.length === 0) {
    throw new Error("Seed parameter is required.");
  }
  return seed;
}

export async function GET(_request: Request, context: SeedRouteContext): Promise<Response> {
  const blocked = rejectIfProduction();
  if (blocked !== null) {
    return blocked;
  }

  try {
    const seed = await resolveSeed(context);
    const datasets = await listDatasets();
    const provider = createMockProvider({ defaultSeed: seed });

    const generated = await Promise.all(
      datasets.map(async (dataset) => {
        const output = await provider.query(
        {
          providerId: "mock",
          datasetId: dataset.datasetId,
          dataShapeId: dataset.dataShapeId,
          seed,
          perfProfile: "default"
        },
        {
          providerId: "mock",
          stableQueryKey: `${dataset.datasetId}:${seed}`,
          now: () => Date.now()
        }
      );

        const response = validateDatasetResponse({
          datasetId: dataset.datasetId,
          dataShapeId: dataset.dataShapeId,
          payload: output.data,
          semanticIntent: dataset.semanticIntent,
          recommendedWidgets: dataset.recommendedWidgets,
          tags: dataset.tags
        });

        return {
          ...response,
          determinism: output.determinism
        };
      })
    );

    return NextResponse.json(
      {
        seed,
        count: generated.length,
        datasets: generated
      },
      {
        status: 200
      }
    );
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Unknown seeded generation error."
      },
      {
        status: 400
      }
    );
  }
}




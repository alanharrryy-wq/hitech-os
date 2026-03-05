import { NextResponse } from "next/server";
import { rejectIfProduction } from "../../../../../lib/dev-kpi/dev-only";
import { loadDatasetRegistry } from "../../../../../lib/dev-kpi/vault";
import { validatePresetJSON } from "../../../../../lib/dev-kpi/validation";

export async function GET(): Promise<Response> {
  const blocked = rejectIfProduction();
  if (blocked !== null) {
    return blocked;
  }

  try {
    const registry = await loadDatasetRegistry();
    const preset = validatePresetJSON({ datasets: registry.datasets });

    if (!preset.ok) {
      return NextResponse.json(
        {
          error: "Dataset index failed validation.",
          details: preset.errors
        },
        {
          status: 500
        }
      );
    }

    return NextResponse.json(
      {
        version: registry.version,
        datasets: registry.datasets,
        count: registry.datasets.length
      },
      {
        status: 200
      }
    );
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Unknown error while loading dataset registry."
      },
      {
        status: 500
      }
    );
  }
}


import { NextResponse } from "next/server";
import { rejectIfProduction } from "../../../../../../lib/dev-kpi/dev-only";
import { loadDatasetById } from "../../../../../../lib/dev-kpi/vault";

interface DatasetRouteContext {
  readonly params: Promise<{ id: string }> | { id: string };
}

async function resolveDatasetId(context: DatasetRouteContext): Promise<string> {
  const params = await context.params;
  const id = decodeURIComponent(params.id ?? "").trim();
  if (id.length === 0) {
    throw new Error("Dataset id parameter is required.");
  }
  return id;
}

export async function GET(_request: Request, context: DatasetRouteContext): Promise<Response> {
  const blocked = rejectIfProduction();
  if (blocked !== null) {
    return blocked;
  }

  try {
    const datasetId = await resolveDatasetId(context);
    const payload = await loadDatasetById(datasetId);

    return NextResponse.json(payload, { status: 200 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown dataset retrieval error.";
    const status = message.includes("not registered") ? 404 : 400;

    return NextResponse.json(
      {
        error: message
      },
      {
        status
      }
    );
  }
}




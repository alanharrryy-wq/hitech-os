/* PRISMA_DARK_PACKSHOTS_197 */
import fs from "node:fs";
import { resolveManagedMediaFile } from "@/server/product-media/managed-library";

export const dynamic = "force-dynamic";

export async function GET(
  _request: Request,
  context: { params: { segments: string[] } | Promise<{ segments: string[] }> }
) {
  const params = await context.params;
  const file = resolveManagedMediaFile(params.segments);
  if (!file) return new Response("Not found", { status: 404 });

  const stat = fs.statSync(file);
  return new Response(fs.readFileSync(file), {
    status: 200,
    headers: {
      "content-type": "image/png",
      "content-length": String(stat.size),
      "cache-control": "public, max-age=31536000, immutable",
      etag: `"${stat.size}-${Math.trunc(stat.mtimeMs)}"`
    }
  });
}

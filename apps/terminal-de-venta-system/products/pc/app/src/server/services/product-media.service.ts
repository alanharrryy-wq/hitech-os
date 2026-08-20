/* PRISMA_DARK_PACKSHOTS_197 */
import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";
import { ProductMediaRepository } from "@/server/repositories/product-media.repository";
import { loadManagedPackshotCatalog } from "@/server/product-media/managed-library";

const repository = new ProductMediaRepository();

function portableMediaRef(value: unknown) {
  if (value === null || value === undefined || value === "") return null;
  if (typeof value !== "string") throw new Error("PRODUCT_MEDIA_REFERENCE_INVALID");
  const ref = value.trim().slice(0, 1_200);
  if (ref.startsWith("/product-media/") && !ref.startsWith("//")) return ref;
  try {
    const url = new URL(ref);
    if (url.protocol !== "https:") throw new Error("invalid protocol");
    return url.toString();
  } catch {
    throw new Error("PRODUCT_MEDIA_REFERENCE_INVALID");
  }
}

export function readProductMediaUpdate(body: unknown) {
  const raw = body && typeof body === "object" && !Array.isArray(body) ? body as Record<string, unknown> : {};
  const productId = typeof raw.productId === "string" ? raw.productId.trim().slice(0, 120) : "";
  const expectedUpdatedAt = typeof raw.expectedUpdatedAt === "string" ? raw.expectedUpdatedAt.trim() : "";
  if (!productId) throw new Error("PRODUCT_MEDIA_PRODUCT_REQUIRED");
  if (!expectedUpdatedAt || Number.isNaN(Date.parse(expectedUpdatedAt))) throw new Error("PRODUCT_MEDIA_VERSION_REQUIRED");
  return { productId, expectedUpdatedAt: new Date(expectedUpdatedAt).toISOString(), mediaRef: portableMediaRef(raw.mediaRef) };
}

export async function getProductMediaWorkspace() {
  try {
    const [products, library] = await Promise.all([
      repository.list(await resolvePcBusinessScope()),
      Promise.resolve(loadManagedPackshotCatalog())
    ]);
    return {
      products,
      library: library.items,
      meta: {
        source: "canonical_prisma" as const,
        warning: null as string | null,
        generatedAt: new Date().toISOString(),
        libraryId: library.libraryId,
        libraryCount: library.items.length
      }
    };
  } catch {
    return {
      products: [],
      library: [],
      meta: {
        source: "unavailable" as const,
        warning: "No fue posible cargar las referencias visuales del catálogo. Reintenta más tarde.",
        generatedAt: new Date().toISOString(),
        libraryId: "",
        libraryCount: 0
      }
    };
  }
}

export async function updateProductMedia(input: ReturnType<typeof readProductMediaUpdate>) {
  return repository.update({ businessId: await resolvePcBusinessScope(), ...input });
}

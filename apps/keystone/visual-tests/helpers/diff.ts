import { readFile, writeFile } from "node:fs/promises";
import pixelmatch from "pixelmatch";
import { PNG } from "pngjs";

export interface PixelDiffBoundingBox {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

export interface PixelDiffResult {
  readonly width: number;
  readonly height: number;
  readonly changedPixels: number;
  readonly totalPixels: number;
  readonly percentChanged: number;
  readonly changedBoundingBox: PixelDiffBoundingBox | null;
}

async function readPng(path: string): Promise<PNG> {
  const data = await readFile(path);
  const png = PNG.sync.read(data);
  return png;
}

function computeChangedBoundingBox(diff: PNG): PixelDiffBoundingBox | null {
  let minX = Number.POSITIVE_INFINITY;
  let minY = Number.POSITIVE_INFINITY;
  let maxX = Number.NEGATIVE_INFINITY;
  let maxY = Number.NEGATIVE_INFINITY;

  for (let y = 0; y < diff.height; y += 1) {
    for (let x = 0; x < diff.width; x += 1) {
      const index = (y * diff.width + x) * 4;
      const alpha = diff.data[index + 3] ?? 0;
      if (alpha === 0) {
        continue;
      }

      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x);
      maxY = Math.max(maxY, y);
    }
  }

  if (!Number.isFinite(minX) || !Number.isFinite(minY)) {
    return null;
  }

  return {
    x: minX,
    y: minY,
    width: maxX - minX + 1,
    height: maxY - minY + 1
  };
}

export async function createPixelDiff(
  beforePath: string,
  afterPath: string,
  diffPath: string
): Promise<PixelDiffResult> {
  const before = await readPng(beforePath);
  const after = await readPng(afterPath);

  if (before.width !== after.width || before.height !== after.height) {
    throw new Error(
      `Unable to diff scene images with different dimensions: before=${before.width}x${before.height}, after=${after.width}x${after.height}.`
    );
  }

  const diff = new PNG({ width: before.width, height: before.height });
  const changedPixels = pixelmatch(before.data, after.data, diff.data, before.width, before.height, {
    threshold: 0.1
  });

  await writeFile(diffPath, PNG.sync.write(diff));

  const totalPixels = before.width * before.height;
  const percentChanged = totalPixels === 0 ? 0 : (changedPixels / totalPixels) * 100;

  return {
    width: before.width,
    height: before.height,
    changedPixels,
    totalPixels,
    percentChanged,
    changedBoundingBox: computeChangedBoundingBox(diff)
  };
}

"use client";

import type { ExportSurface } from "@/lib/contextual-export-reports/contextual-export-contract";
import { ContextualExportActions } from "./contextual-export-actions";

type ContextualExportBandProps = {
  surface: ExportSurface;
};

export function ContextualExportBand({ surface }: ContextualExportBandProps) {
  return <ContextualExportActions surface={surface} />;
}

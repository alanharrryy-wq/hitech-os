from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ENGINE = Path(__file__).with_name("tablet_sync_wave2_apply_carrier.py")


def load_engine():
    spec = importlib.util.spec_from_file_location("wave2_engine", ENGINE)
    if spec is None or spec.loader is None:
        raise SystemExit("WAVE2_ENGINE_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    mod = load_engine()
    original = mod.replace_once

    def flex(text: str, old: str, new: str, label: str) -> str:
        if label == "SCREEN_RETRY_CAPTURE":
            pattern = re.compile(
                r'''      await requestJson<\{ updated: number; message: string \}>\("/api/pos/sync/retry", \{\n'''
                r'''        method: "POST",\n'''
                r'''        body: JSON\.stringify\(\{\n'''
                r'''          businessId: DEFAULT_SYNC_BUSINESS_ID,\n'''
                r'''          includeFailed: true,\n'''
                r'''          includePending: false\n'''
                r'''        \}\)\n'''
                r'''      \}\);'''
            )
            replacement = '''      const prepared = await requestJson<SyncRetryPreparationResult>("/api/pos/sync/retry", {\n        method: "POST",\n        body: JSON.stringify({\n          businessId: DEFAULT_SYNC_BUSINESS_ID,\n          includeFailed: true,\n          includePending: false\n        })\n      });\n      setRetryResult(prepared.data);'''
            updated, count = pattern.subn(replacement, text, count=1)
            if count != 1:
                raise SystemExit(f"PATCH_ANCHOR_{label}_COUNT_{count}")
            return updated

        if label == "SCREEN_OPERATION_DETAILS":
            pattern = re.compile(
                r'''                    <span>\{item\.statusLabel\}</span>\n'''
                r'''                    <h2>\{item\.title\}</h2>\n'''
                r'''                    <p>\{item\.description\}</p>\n'''
                r'''                  </div>'''
            )
            replacement = '''                    <span>{item.statusLabel}</span>\n                    <h2>{item.title}</h2>\n                    <p>{item.description}</p>\n                    <details>\n                      <summary>Detalles de operación</summary>\n                      <div className={styles.filterBar}>\n                        {item.provenance.source ? <span className={styles.metaPill}>Origen: {compactOperationalValue(item.provenance.source)}</span> : null}\n                        {item.provenance.storeId ? <span className={styles.metaPill}>Tienda: {compactOperationalValue(item.provenance.storeId)}</span> : null}\n                        {item.provenance.terminalId ? <span className={styles.metaPill}>Terminal: {compactOperationalValue(item.provenance.terminalId)}</span> : null}\n                        {item.provenance.deviceId ? <span className={styles.metaPill}>Dispositivo: {compactOperationalValue(item.provenance.deviceId)}</span> : null}\n                        {item.provenance.actorId ? <span className={styles.metaPill}>Operador: {compactOperationalValue(item.provenance.actorId)}</span> : null}\n                      </div>\n                      <p>\n                        {item.delivery.remoteLifecycleStatus\n                          ? `Estado PC: ${item.delivery.remoteLifecycleStatus}`\n                          : "Sin estado remoto persistido todavía."}\n                        {item.delivery.remoteLedgerId ? ` · Ledger: ${compactOperationalValue(item.delivery.remoteLedgerId)}` : ""}\n                      </p>\n                      {item.delivery.lastAttemptAt ? <p>Último intento: {operationTime(item.delivery.lastAttemptAt)}</p> : null}\n                      {item.delivery.ackedAt ? <p>Confirmado: {operationTime(item.delivery.ackedAt)}</p> : null}\n                      {item.delivery.conflictedAt ? <p>Conflicto detectado: {operationTime(item.delivery.conflictedAt)}</p> : null}\n                      {item.delivery.remoteConflictCode ? <p>Motivo de conflicto: {item.delivery.remoteConflictCode}</p> : null}\n                      {item.delivery.remoteRejectedReason ? <p>Último rechazo: {item.delivery.remoteRejectedReason}</p> : null}\n                      {item.resolutionLabel ? <p><strong>{item.resolutionLabel}.</strong> Tablet conserva la evidencia; no resuelve conflictos aquí.</p> : null}\n                    </details>\n                  </div>'''
            updated, count = pattern.subn(replacement, text, count=1)
            if count != 1:
                raise SystemExit(f"PATCH_ANCHOR_{label}_COUNT_{count}")
            return updated

        return original(text, old, new, label)

    mod.replace_once = flex
    mod.main()


if __name__ == "__main__":
    main()

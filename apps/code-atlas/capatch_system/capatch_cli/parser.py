#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from capatch_legacy import CAPATCH_PLUGIN_DEFAULT_TAIL_LINES, DEFAULT_ROOT_DIR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='capatch cli phase 0 facade. delega a engine/diagnostics/audit/policy sin meter lógica nueva en capatch.py.',
    )
    parser.add_argument('--root-dir', default=str(DEFAULT_ROOT_DIR), help='Carpeta raiz donde viven los archivos a tocar.')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--ops-file', help='Ruta a archivo JSON con la lista de operaciones.')
    group.add_argument('--ops-stdin', action='store_true', help='Lee la lista de operaciones como JSON desde stdin.')
    parser.add_argument('--checkpoint-label', help='Nombre legible del checkpoint de sesion. Ej: pre-2.1')
    parser.add_argument('--dry-run', action='store_true', help='Ejecuta validaciones y preview, pero no escribe cambios ni crea checkpoints.')
    parser.add_argument('--no-auto-support', action='store_true', help='Desactiva la capa de auto-soporte para desajustes minimos recuperables.')
    parser.add_argument('--self-test', action='store_true', help='Imprime un ejemplo minimo de operaciones y sale.')
    parser.add_argument('--smoke-test', action='store_true', help='Corre pruebas rapidas del motor y sale.')

    plugin_group = parser.add_argument_group('plugin runtime')
    plugin_group.add_argument('--plugin-list', action='store_true', help='Lista el registro actual de plugins y sale.')
    plugin_group.add_argument('--plugin-health', action='store_true', help='Carga plugins, imprime estado/health y sale.')
    plugin_group.add_argument('--plugin-retest', action='store_true', help='Alias de --plugin-health para revalidar plugins en una corrida limpia.')
    plugin_group.add_argument('--plugin-disable', help='Deshabilita un plugin por PLUGIN_ID y sale.')
    plugin_group.add_argument('--plugin-enable', help='Habilita un plugin por PLUGIN_ID y sale.')
    plugin_group.add_argument('--plugin-show-log', help='Imprime el tail del log de un plugin y sale.')
    plugin_group.add_argument('--plugin-tail-lines', type=int, default=CAPATCH_PLUGIN_DEFAULT_TAIL_LINES, help='Numero de lineas para --plugin-show-log.')

    diagnostic_group = parser.add_argument_group('diagnostic runtime')
    diagnostic_group.add_argument('--diagnose', action='store_true', help='Corre Diagnostic Runtime v1 y sale.')
    diagnostic_group.add_argument('--collect-only', action='store_true', help='Ejecuta solo recoleccion diagnostica.')
    diagnostic_group.add_argument('--verify-only', action='store_true', help='Ejecuta solo verificadores diagnosticos.')
    diagnostic_group.add_argument('--support-bundle', action='store_true', help='Genera bundle de soporte IA-first.')
    diagnostic_group.add_argument('--fix-plan', action='store_true', help='Genera plan de fix sin aplicar cambios.')
    diagnostic_group.add_argument('--apply-fixes', action='store_true', help='Ejecuta el puente conservador de fixers diagnósticos.')
    diagnostic_group.add_argument('--target-path', help='Ruta objetivo para el runtime diagnostico.')
    diagnostic_group.add_argument('--app-kind', default='auto', choices=['auto', 'python', 'node', 'web', 'desktop', 'mixed', 'unknown'], help='Tipo de app para el runtime diagnostico.')
    diagnostic_group.add_argument('--bundle-format', default='md', choices=['md', 'json', 'all'], help='Formato principal del support bundle.')
    diagnostic_group.add_argument('--include-logs', action='store_true', help='Incluye heuristicas de logs en el bundle.')
    diagnostic_group.add_argument('--include-processes', action='store_true', help='Fuerza la inclusión y el resumen de procesos en bundles/reportes avanzados.')
    diagnostic_group.add_argument('--include-ports', action='store_true', help='Fuerza la inclusión y el resumen de puertos en bundles/reportes avanzados.')
    diagnostic_group.add_argument('--include-git', action='store_true', help='Fuerza la inclusión y el resumen de git en bundles/reportes avanzados.')
    diagnostic_group.add_argument('--include-build', action='store_true', help='Fuerza la inclusión y el resumen de build en bundles/reportes avanzados.')
    diagnostic_group.add_argument('--include-tests', action='store_true', help='Fuerza la inclusión y el resumen de tests en bundles/reportes avanzados.')
    diagnostic_group.add_argument('--max-log-lines', type=int, default=200, help='Tail maximo por log para bundles.')
    diagnostic_group.add_argument('--max-log-bytes', type=int, default=262144, help='Bytes maximos por log para bundles.')
    diagnostic_group.add_argument('--command-timeout-seconds', type=int, default=45, help='Timeout maximo para probes de build/tests.')
    diagnostic_group.add_argument('--dry-diagnose', action='store_true', help='Corre diagnostico sin acciones mutantes.')
    diagnostic_group.add_argument('--rollback-checkpoint', help='Restaura manualmente un checkpoint previo del patch engine.')
    diagnostic_group.add_argument('--rollback-last', action='store_true', help='Restaura el checkpoint más reciente del patch engine.')
    diagnostic_group.add_argument('--list-checkpoints', action='store_true', help='Lista checkpoints disponibles del patch engine.')
    diagnostic_group.add_argument('--show-run', help='Muestra un patch run persistido por run_id.')
    diagnostic_group.add_argument('--show-rollback-command', help='Imprime el rollback command sugerido para un run_id persistido.')
    return parser


def diagnostic_args_requested(args: Any) -> bool:
    return any(
        [
            bool(getattr(args, 'diagnose', False)),
            bool(getattr(args, 'collect_only', False)),
            bool(getattr(args, 'verify_only', False)),
            bool(getattr(args, 'support_bundle', False)),
            bool(getattr(args, 'fix_plan', False)),
            bool(getattr(args, 'apply_fixes', False)),
        ]
    )

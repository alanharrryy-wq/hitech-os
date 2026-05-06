#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

VERTICALS = {
    'convenience','restaurant','pharmacy','beauty','hardware','apparel','repair','field_route','grocery_scale','food_truck'
}
REQUIRED_BLOCKS = {'00A_CORE_CONTRACTS','00B_VERTICAL_REGISTRY','00C_VERTICAL_DATA_MODELS','00D_VERTICAL_EVENTS_PERMISSIONS','00E_VERTICAL_UX_OPERATIONS'}
REQUIRED_STATES = {'empty','loading','ready','error','offline','sync_pending','success'}


def read_json(path: Path):
    if not path.exists():
        raise SystemExit(f'Falta archivo requerido: {path}')
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        raise SystemExit(f'JSON invalido: {path}: {exc}')


def fail(msg: str) -> None:
    raise SystemExit(msg)


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    base = root / 'shared' / 'verticals' / 'validation'
    registry = read_json(base / 'vertical-validation-fixture.registry.v0.json')
    fixtures_meta = registry.get('fixtures', [])
    seen = {item.get('verticalId') for item in fixtures_meta}
    if seen != VERTICALS:
        fail(f'Verticales inesperados en registry: {sorted(seen)}')

    scenario_count = 0
    acceptance_check_count = 0
    fixture_count = 0
    warnings = []
    for vid in sorted(VERTICALS):
        fixture_path = root / 'shared' / 'verticals' / 'validation' / 'fixtures' / f'{vid}.validation-fixture.json'
        fixture = read_json(fixture_path)
        fixture_count += 1
        if fixture.get('verticalId') != vid:
            fail(f'verticalId incorrecto en {fixture_path}')
        blocks = set(fixture.get('requiredBlocks', []))
        missing_blocks = REQUIRED_BLOCKS - blocks
        if missing_blocks:
            fail(f'{vid} no declara bloques requeridos: {sorted(missing_blocks)}')
        screens = fixture.get('screensUnderTest', [])
        flows = fixture.get('flowsUnderTest', [])
        scenarios = fixture.get('scenarios', [])
        checks = fixture.get('acceptanceChecks', [])
        if len(screens) < 6:
            fail(f'{vid} tiene pocas pantallas cubiertas')
        if len(flows) < 6:
            fail(f'{vid} tiene pocos flujos cubiertos')
        if len(scenarios) < 6:
            fail(f'{vid} tiene pocos escenarios')
        check_by_scenario = {item.get('scenarioId'): item for item in checks}
        for sc in scenarios:
            scenario_count += 1
            for field in ['id','verticalId','primaryScreen','flowKey','initialState','steps','expectedEvents','requiredPermissions','expectedResult']:
                if field not in sc:
                    fail(f'{vid} scenario sin {field}: {sc.get("id")}')
            if sc['verticalId'] != vid:
                fail(f'{vid} scenario con verticalId incorrecto: {sc["id"]}')
            if sc['primaryScreen'] not in screens:
                fail(f'{vid} scenario usa pantalla no declarada: {sc["primaryScreen"]}')
            if sc['flowKey'] not in flows:
                fail(f'{vid} scenario usa flujo no declarado: {sc["flowKey"]}')
            if not sc.get('expectedEvents'):
                fail(f'{vid} scenario sin evento: {sc["id"]}')
            if not sc.get('requiredPermissions'):
                fail(f'{vid} scenario sin permiso: {sc["id"]}')
            if len(sc.get('steps', [])) < 3:
                fail(f'{vid} scenario con pocos pasos: {sc["id"]}')
            if sc['id'] not in check_by_scenario:
                fail(f'{vid} scenario sin acceptanceChecks: {sc["id"]}')
            acceptance_check_count += len(check_by_scenario[sc['id']].get('checks', []))

    smoke = read_json(base / 'smoke' / 'vertical-smoke-suite.v0.json')
    if smoke.get('caseCount', 0) < scenario_count:
        fail('Smoke suite no cubre todos los escenarios')

    acceptance = read_json(base / 'acceptance' / 'vertical-acceptance-matrix.v0.json')
    if acceptance.get('rowCount', 0) < acceptance_check_count:
        fail('Acceptance matrix tiene menos filas que los checks declarados')

    coverage = read_json(base / 'coverage' / 'vertical-cross-coverage.v0.json')
    states = {row.get('state') for row in coverage.get('rows', [])}
    if not REQUIRED_STATES.issubset(states):
        fail(f'Coverage matrix no incluye todos los estados: {sorted(REQUIRED_STATES - states)}')
    if coverage.get('rowCount', 0) < scenario_count * len(REQUIRED_STATES):
        fail('Coverage matrix insuficiente para escenarios x estados')

    evidence = read_json(base / 'evidence' / 'vertical-fixture-evidence-corpus.v0.json')
    if len(evidence.get('records', [])) < 1000:
        fail('Evidence corpus demasiado chico')

    # Optional cross-package presence checks. Do not fail because 00F can be tested in isolation.
    optional_prior = [
        root / 'shared' / 'contracts' / 'verticals' / 'vertical-registry.contract.json',
        root / 'shared' / 'verticals' / 'ux' / 'vertical-ux-operation.registry.v0.json',
        root / 'shared' / 'verticals' / 'events-permissions' / 'vertical-events-permissions.registry.v0.json',
    ]
    for path in optional_prior:
        if not path.exists():
            warnings.append(f'WARN dependencia previa no encontrada para validacion cruzada opcional: {path}')

    for warning in warnings:
        print(warning)
    print(f'OK vertical validation fixtures: {fixture_count} verticals, {scenario_count} scenarios, {acceptance_check_count} acceptance checks, {coverage.get("rowCount")} coverage rows validated')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

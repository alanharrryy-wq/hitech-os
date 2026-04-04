from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CAPABILITY_CONTRACT_PATH = (
    Path(__file__).resolve().parents[1] / "contracts" / "premium_capabilities_100.md"
)


@dataclass(frozen=True, slots=True)
class PremiumCapability:
    capability_id: int
    pillar: str
    text: str
    before_status: str
    release_blocker: bool


def _entries() -> list[tuple[str, str]]:
    return [
        ("Base de interacción y control", "La app abre rápido y se siente viva desde el primer segundo"),
        ("Base de interacción y control", "La ventana completa se puede redimensionar por esquinas y bordes sin glitches"),
        ("Base de interacción y control", "Los paneles internos se pueden arrastrar cuando eso forma parte del producto"),
        ("Base de interacción y control", "Los paneles internos se pueden redimensionar con handles claros y consistentes"),
        ("Base de interacción y control", "Todo movimiento respeta límites del workspace y no se sale del canvas"),
        ("Base de interacción y control", "Los elementos interactivos responden igual con mouse, trackpad y touch si aplica"),
        ("Base de interacción y control", "No hay zonas muertas donde parece clickeable pero no pasa nada"),
        ("Base de interacción y control", "El foco visual siempre deja claro qué elemento está activo"),
        ("Base de interacción y control", "Los estados hover, pressed, selected y focused están bien diferenciados"),
        ("Base de interacción y control", "No hay acciones visibles que se sientan decorativas o inútiles"),
        ("Layout y composición", "El workspace principal domina visualmente la pantalla"),
        ("Layout y composición", "No hay contenedores inútiles dentro de contenedores inútiles"),
        ("Layout y composición", "Las barras laterales no roban espacio si no son necesarias"),
        ("Layout y composición", "El layout se adapta bien cuando ocultas o abres paneles secundarios"),
        ("Layout y composición", "Los márgenes y paddings se sienten intencionales, no acumulados"),
        ("Layout y composición", "El contenido importante nunca queda aplastado por chrome innecesario"),
        ("Layout y composición", "La jerarquía visual se entiende en 3 segundos"),
        ("Layout y composición", "El sistema soporta bien vistas vacías sin verse roto"),
        ("Layout y composición", "La app no colapsa feo en tamaños chicos o medianos"),
        ("Layout y composición", "Hay equilibrio entre densidad de información y aire visual"),
        ("Navegación premium", "Siempre sabes dónde estás dentro de la app"),
        ("Navegación premium", "Siempre sabes qué puedes hacer después"),
        ("Navegación premium", "Las rutas principales son pocas, claras y memorables"),
        ("Navegación premium", "Existe una forma rápida global de buscar o invocar cosas importantes"),
        ("Navegación premium", "Los cambios de vista no se sienten abruptos ni confusos"),
        ("Navegación premium", "El back / close / cancel siempre hace algo esperable"),
        ("Navegación premium", "La navegación no depende de aprenderte el truco oculto"),
        ("Navegación premium", "Hay accesos rápidos para usuarios intensivos"),
        ("Navegación premium", "Las herramientas avanzadas están accesibles sin dominar toda la UI"),
        ("Navegación premium", "La navegación secundaria no compite con la principal"),
        ("Flujo de trabajo y productividad", "Crear algo nuevo es obvio y no da miedo"),
        ("Flujo de trabajo y productividad", "Editar algo existente es directo y no te manda por tres menús"),
        ("Flujo de trabajo y productividad", "Reemplazar, mover, duplicar o borrar elementos es consistente"),
        ("Flujo de trabajo y productividad", "Los flujos comunes requieren pocos clics"),
        ("Flujo de trabajo y productividad", "Las acciones pesadas tienen confirmación clara"),
        ("Flujo de trabajo y productividad", "Las acciones frecuentes tienen shortcuts o paths rápidos"),
        ("Flujo de trabajo y productividad", "El sistema favorece continuidad, no reinicios pendejos"),
        ("Flujo de trabajo y productividad", "Puedes retomar trabajo sin perder contexto"),
        ("Flujo de trabajo y productividad", "La app tolera interrupciones sin romper el estado"),
        ("Flujo de trabajo y productividad", "El usuario siente progreso constante, no fricción constante"),
        ("Claridad de acciones", "Cada botón tiene una intención clara y específica"),
        ("Claridad de acciones", "Los CTAs principales se distinguen sin gritar"),
        ("Claridad de acciones", "Las acciones secundarias no roban protagonismo"),
        ("Claridad de acciones", "Las acciones destructivas están claramente separadas"),
        ("Claridad de acciones", "Si una acción no está disponible, la UI explica por qué"),
        ("Claridad de acciones", "Las acciones contextuales aparecen cuando importan, no siempre"),
        ("Claridad de acciones", "No hay duplicidad rara entre botones que hacen casi lo mismo"),
        ("Claridad de acciones", "El lenguaje de acciones es consistente en toda la app"),
        ("Claridad de acciones", "La app no te obliga a adivinar qué botón era el bueno"),
        ("Claridad de acciones", "Ningún flujo clave depende de un botón escondido en un panel oscuro"),
        ("Estados vacíos, loading y feedback", "Los empty states se ven premium, no como abandono"),
        ("Estados vacíos, loading y feedback", "Los empty states explican qué hacer después"),
        ("Estados vacíos, loading y feedback", "Los skeletons/loading states se sienten elegantes y útiles"),
        ("Estados vacíos, loading y feedback", "Nunca hay pantallas congeladas sin feedback"),
        ("Estados vacíos, loading y feedback", "Guardar, enviar, cargar o sincronizar muestran progreso entendible"),
        ("Estados vacíos, loading y feedback", "Los errores se explican con lenguaje humano"),
        ("Estados vacíos, loading y feedback", "Los éxitos confirman sin interrumpir de más"),
        ("Estados vacíos, loading y feedback", "Los warnings no parecen errores fatales"),
        ("Estados vacíos, loading y feedback", "El feedback temporal desaparece cuando debe desaparecer"),
        ("Estados vacíos, loading y feedback", "El sistema comunica claramente cuando una acción sigue corriendo"),
        ("Consistencia visual", "Hay un solo lenguaje visual dominante"),
        ("Consistencia visual", "Los bordes están controlados y no ensucian todo"),
        ("Consistencia visual", "Los radios, sombras y transparencias siguen reglas claras"),
        ("Consistencia visual", "La paleta no se siente accidental ni saturada"),
        ("Consistencia visual", "Los colores de estado tienen significado consistente"),
        ("Consistencia visual", "No hay componentes viejos mezclados con otros nuevos"),
        ("Consistencia visual", "Los íconos tienen el mismo estilo y peso visual"),
        ("Consistencia visual", "Los tabs, chips, cards y panels hablan el mismo idioma visual"),
        ("Consistencia visual", "El contraste está bien cuidado sin verse gritón"),
        ("Consistencia visual", "La UI se ve fina tanto en screenshot como en uso real"),
        ("Belleza percibida y delight", "La app tiene un wow factor sobrio, no cirquero"),
        ("Belleza percibida y delight", "Las animaciones son suaves y útiles, no mamadoras"),
        ("Belleza percibida y delight", "Hay profundidad visual sin ensuciar legibilidad"),
        ("Belleza percibida y delight", "El vidrio, blur o glow, si existen, se usan con disciplina"),
        ("Belleza percibida y delight", "El contenido importante siempre se ve más fuerte que los adornos"),
        ("Belleza percibida y delight", "La interfaz se siente moderna, no retro-utilitaria"),
        ("Belleza percibida y delight", "La estética aguanta muchas horas de uso sin cansar"),
        ("Belleza percibida y delight", "La app se siente cara aunque haga cosas simples"),
        ("Belleza percibida y delight", "La identidad visual es memorable"),
        ("Belleza percibida y delight", "La UI no parece plantilla genérica con maquillaje oscuro"),
        ("Datos, verdad y confianza", "Siempre está claro qué datos estás viendo"),
        ("Datos, verdad y confianza", "Siempre está claro de dónde vienen esos datos"),
        ("Datos, verdad y confianza", "Siempre está claro cuándo fueron actualizados"),
        ("Datos, verdad y confianza", "Las acciones sobre datos dejan rastro o confirmación visible"),
        ("Datos, verdad y confianza", "Los estados de sync/dispatch/error no están escondidos"),
        ("Datos, verdad y confianza", "Puedes distinguir entre draft, activo, fallido, pendiente, aprobado, etc."),
        ("Datos, verdad y confianza", "No hay ambigüedad entre preview, estado actual y estado guardado"),
        ("Datos, verdad y confianza", "La app evita que tomes decisiones con información vieja sin avisarte"),
        ("Datos, verdad y confianza", "Los cambios tienen persistencia clara o rollback claro"),
        ("Datos, verdad y confianza", "El usuario siente confianza operativa, no incertidumbre"),
        ("Robustez, accesibilidad y calidad total", "La app soporta bien sesiones largas sin degradarse culero"),
        ("Robustez, accesibilidad y calidad total", "Los componentes no se rompen al cambiar tamaño, zoom o densidad"),
        ("Robustez, accesibilidad y calidad total", "El teclado permite operar flujos importantes"),
        ("Robustez, accesibilidad y calidad total", "El foco accesible está bien resuelto"),
        ("Robustez, accesibilidad y calidad total", "El texto sigue siendo legible en todos los estados"),
        ("Robustez, accesibilidad y calidad total", "El sistema tolera errores parciales sin colapsar toda la experiencia"),
        ("Robustez, accesibilidad y calidad total", "Las funcionalidades chidas tienen protección contra regresión"),
        ("Robustez, accesibilidad y calidad total", "Hay tests o checks para interacción crítica, no solo para lógica interna"),
        ("Robustez, accesibilidad y calidad total", "El producto tiene un contrato claro de capacidades sagradas"),
        ("Robustez, accesibilidad y calidad total", "Cada release puede demostrar que no rompió lo que hacía amada a la app")
    ]


SOLID_BEFORE = {18, 21, 24, 31, 33, 34, 37, 41, 44, 47, 48, 51, 52, 55, 56, 61, 67, 81, 82, 84, 87, 98, 99}
MISSING_BEFORE = {3, 4, 5, 6, 7, 17, 53, 60, 83, 88, 91, 92, 96, 97, 100}

CAPABILITY_EVIDENCE_TAGS: dict[int, list[str]] = {
    1: ["session:startup_blank_workspace:pass"],
    2: ["check:test_catalog_workbench:pass"],
    3: ["session:drag_panel_cross_slot:pass"],
    4: ["session:resize_panel_and_clamp:pass"],
    5: ["session:resize_panel_and_clamp:pass", "session:drag_panel_cross_slot:pass"],
    6: ["check:test_catalog_workbench:pass"],
    7: ["session:picker_search_and_category:pass"],
    8: ["session:startup_blank_workspace:pass"],
    9: ["check:test_catalog_workbench:pass"],
    10: ["session:add_to_current_tab:pass"],
    11: ["session:startup_blank_workspace:pass"],
    12: ["check:test_catalog_workbench:pass"],
    13: ["session:startup_blank_workspace:pass"],
    14: ["session:open_in_new_tab:pass"],
    15: ["check:test_catalog_workbench:pass"],
    16: ["session:startup_blank_workspace:pass"],
    17: ["session:startup_blank_workspace:pass"],
    18: ["session:startup_blank_workspace:pass"],
    19: ["check:test_catalog_workbench:pass"],
    20: ["check:test_catalog_workbench:pass"],
    21: ["session:startup_blank_workspace:pass"],
    22: ["session:startup_blank_workspace:pass"],
    23: ["session:picker_search_and_category:pass"],
    24: ["session:picker_search_and_category:pass"],
    25: ["session:picker_search_and_category:pass"],
    26: ["session:open_in_new_tab:pass"],
    27: ["session:add_to_current_tab:pass"],
    28: ["session:picker_search_and_category:pass"],
    29: ["session:data_runtime_probe_states:pass"],
    30: ["session:open_in_new_tab:pass"],
    31: ["session:startup_blank_workspace:pass"],
    32: ["session:add_to_current_tab:pass"],
    33: ["session:drag_panel_cross_slot:pass"],
    34: ["session:add_to_current_tab:pass"],
    35: ["session:clone_reset_isolation:pass"],
    36: ["session:picker_search_and_category:pass"],
    37: ["session:clone_reset_isolation:pass"],
    38: ["session:clone_reset_isolation:pass"],
    39: ["session:clone_reset_isolation:pass"],
    40: ["session:open_in_new_tab:pass", "session:drag_panel_cross_slot:pass"],
    42: ["session:add_to_current_tab:pass"],
    43: ["check:test_catalog_workbench:pass"],
    45: ["session:add_to_current_tab:pass"],
    46: ["session:picker_search_and_category:pass"],
    49: ["session:picker_search_and_category:pass"],
    50: ["session:add_to_current_tab:pass"],
    53: ["session:data_runtime_probe_states:pass"],
    54: ["session:data_runtime_probe_states:pass"],
    57: ["check:test_catalog_workbench:pass"],
    58: ["check:test_catalog_workbench:pass"],
    59: ["check:test_catalog_workbench:pass"],
    60: ["session:data_runtime_probe_states:pass"],
    62: ["check:test_catalog_workbench:pass"],
    63: ["check:test_catalog_workbench:pass"],
    64: ["check:test_catalog_workbench:pass"],
    65: ["session:data_runtime_probe_states:pass"],
    66: ["check:test_theme_surface_opacity:pass"],
    68: ["check:test_catalog_workbench:pass"],
    69: ["check:test_catalog_workbench:pass"],
    70: ["check:test_catalog_workbench:pass"],
    72: ["check:test_catalog_workbench:pass"],
    73: ["check:test_catalog_workbench:pass"],
    74: ["check:test_catalog_workbench:pass"],
    81: ["session:data_runtime_probe_states:pass"],
    82: ["session:data_runtime_probe_states:pass"],
    83: ["session:data_runtime_probe_states:pass"],
    84: ["session:data_runtime_probe_states:pass"],
    85: ["session:data_runtime_probe_states:pass"],
    86: ["session:data_runtime_probe_states:pass"],
    87: ["session:clone_reset_isolation:pass"],
    88: ["session:data_runtime_probe_states:pass"],
    89: ["session:clone_reset_isolation:pass"],
    90: ["session:data_runtime_probe_states:pass"],
    91: ["check:test_ux_flight_recorder:pass"],
    92: ["check:test_catalog_workbench:pass"],
    93: ["check:test_catalog_workbench:pass"],
    94: ["check:test_catalog_workbench:pass"],
    95: ["check:test_catalog_workbench:pass"],
    96: ["session:data_runtime_probe_states:pass"],
    97: ["check:test_ux_flight_recorder:pass"],
    98: ["check:test_catalog_workbench:pass", "check:test_ux_flight_recorder:pass"],
    99: ["check:release_gate:pass"],
    100: ["check:proof_runner:pass", "check:session_suite_complete:pass", "check:compile:pass"],
}


def load_capability_contract() -> list[PremiumCapability]:
    rows: list[PremiumCapability] = []
    for index, (pillar, text) in enumerate(_entries(), start=1):
        before = "partial"
        if index in SOLID_BEFORE:
            before = "solid"
        if index in MISSING_BEFORE:
            before = "missing"
        rows.append(
            PremiumCapability(
                capability_id=index,
                pillar=pillar,
                text=text,
                before_status=before,
                release_blocker=bool(index <= 40),
            )
        )
    return rows


def _evidence_tags_for_capability(capability_id: int) -> list[str]:
    return list(CAPABILITY_EVIDENCE_TAGS.get(int(capability_id), []))


def _resolve_after_status(
    capability: PremiumCapability,
    evidence_tags: set[str],
) -> tuple[str, str]:
    required = _evidence_tags_for_capability(capability.capability_id)
    if not required:
        if capability.before_status == "missing":
            return "deferred", "deferred"
        return capability.before_status, "reused"
    matched = [tag for tag in required if tag in evidence_tags]
    coverage = float(len(matched)) / float(len(required)) if required else 0.0

    if coverage >= 1.0:
        if capability.before_status == "missing":
            return "solid", "newly_implemented"
        if capability.before_status == "solid":
            return "solid", "reused"
        return "solid", "improved"

    if coverage > 0.0:
        if capability.before_status == "solid":
            return "solid", "reused"
        if capability.before_status == "missing":
            return "improved_partial", "newly_implemented"
        return "improved_partial", "improved"

    if capability.before_status == "missing":
        return "deferred", "deferred"
    return capability.before_status, "reused"


def capability_matrix_delta(
    evidence_tags: Iterable[str],
) -> list[dict[str, object]]:
    tags = {str(item).strip() for item in evidence_tags if str(item).strip()}
    rows: list[dict[str, object]] = []
    for capability in load_capability_contract():
        after_status, implementation = _resolve_after_status(capability, tags)
        rows.append(
            {
                "capability_id": capability.capability_id,
                "pillar": capability.pillar,
                "capability": capability.text,
                "release_blocker": capability.release_blocker,
                "before_status": capability.before_status,
                "after_status": after_status,
                "implementation": implementation,
                "evidence_tags": _evidence_tags_for_capability(capability.capability_id),
            }
        )
    return rows

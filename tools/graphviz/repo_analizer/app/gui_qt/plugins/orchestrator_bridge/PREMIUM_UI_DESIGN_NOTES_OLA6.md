# PREMIUM UI DESIGN NOTES OLA 6

## Qué cambió visualmente
- El dock ahora usa una jerarquía visual por superficies, con header de estado, ejecución, resultado, historial, timeline y logs separados.
- El estado principal vive en un status chip con color semántico y micro-movimiento durante ejecución.
- El resultado usa affordances rápidas para copiar ruta, abrir ZIP y abrir carpeta, con feedback visual corto.
- La línea de tiempo muestra eventos de alto valor para operador sin mezclar todo el ruido del stream crudo.

## Tokens y lenguaje visual
- Fondo base oscuro sobrio para reducir fatiga visual en sesiones largas.
- Superficies elevadas con gradiente sutil y contraste controlado.
- Semántica de color:
  - ready/running: azul
  - success: verde
  - reused: cian suave
  - blocked: ámbar
  - failed: rojo
- Radios suaves, spacing consistente y tipografía de sistema Windows.

## Motion
- Feedback corto y no intrusivo en run, rerun, copy, open ZIP, open folder y errores.
- Pulso discreto del status chip mientras el proceso está activo.
- Barra de progreso visible sólo en ejecución para evitar parpadeo innecesario.

## Cómo mantener/extender sin romper coherencia
1. Cambiar primero `THEME_TOKENS` y `STATE_VISUALS`, no meter colores inline nuevos salvo excepciones.
2. Mantener los estados semánticos existentes: idle, ready, running, success, reused, blocked, failed.
3. Toda acción nueva del dock debe dejar feedback breve en timeline o banner, sin bloquear la UI.
4. Evitar widgets ornamentales extra. El acabado buscado es premium sobrio, no UI recargada.
5. El plugin sigue siendo bridge only: cualquier nueva acción visual debe seguir delegando la lógica real al runner externo.

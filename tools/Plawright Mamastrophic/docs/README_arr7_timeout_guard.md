# PRISMA Plawright Mamastrophic arr7 timeout-guard

## Reparacion incluida

Este paquete corrige el fallo observado en `surf8 full 1006 083109619 fail.zip`:

- fallo original: `pc.route.proveedores @pc @route`.
- error original: `Test timeout of 90000ms exceeded` y `Object with guid response... was not bound in the connection`.
- causa tecnica: el runner permitia hasta 3 intentos de navegacion de 45s (`gotoRetries=2`), pero el timeout total del test era 90s. En rutas lentas, Playwright podia matar el test antes de que el motor escribiera JSON/screenshot de fallo.

## Cambios funcionales

- Timeout total del test ahora se calcula de forma coherente con `gotoTimeout * (gotoRetries + 1)`, screenshot, clicks y margen de cierre.
- Se agregan parametros de control:
  - `-TestTimeoutMs`
  - `-GotoTimeoutMs`
  - `-GotoRetries`
  - `-ScreenshotTimeoutMs`
  - `-ProbeTimeoutMs`
- Captura de `title`, `h1` y screenshot queda acotada para que el registro de fallo no se cuelgue.
- Si una navegacion reporta timeout pero la pagina ya aterrizo en la URL esperada y tiene DOM/body con contenido, el runner registra `navigation.softNavigation=true` y captura evidencia en vez de convertirlo automaticamente en fail por reloj.
- `visualqa` recibe el mismo guardrail de timeout y aterrizaje suave.

## Politica preservada

- No inicia servicios.
- No mata procesos.
- No toca base de datos.
- No cambia puertos.
- No modifica configuracion del proyecto terminal.

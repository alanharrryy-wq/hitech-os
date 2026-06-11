# arr12 bridge no-0-tests fix

Corrección del harness Playwright para evitar `Total: 0 tests in 0 files` en Windows.

- El bridge spec ya no se pasa como filtro absoluto al CLI.
- Playwright descubre el bridge mediante `testDir` + `testMatch`.
- El bridge usa el mismo módulo `@playwright/test` que el CLI resuelto.
- El bridge registra directamente el engine de Surf8/VisualQA.

Esto separa la detección de superficies del montaje real de tests. Si discovery pasa y list falla, ahora el error debe ser real, no un falso negativo por regex/path.

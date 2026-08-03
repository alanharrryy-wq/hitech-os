# PRISMA Visual Family Atlas · Piloto 1

## Páginas

1. `index.html`
2. `a-fundamentos.html`
3. `g-tablas.html`
4. `m-overlays.html`
5. `z-gobierno.html`

## Alcance

- 418 elementos en el manifiesto.
- 26 secciones A–Z.
- 5 páginas públicas implementadas.
- 7 acentos semánticos.
- búsqueda global local;
- motion normal, reducido o apagado;
- sin servidor;
- sin dependencias externas;
- no modifica el repositorio.

## Abrir

`index.html`

## Fuente

- `source/atlasui.md`
- `assets/data/atlas.manifest.json`
- `assets/data/atlas.tokens.json`

Imagen canónica SHA-256:

`5fe81f9b981e881eaefe15284ab53f767f43ebfe9c8e771a5ce71e6074d647d4`


## Corrección V2

- Fondo exacto suministrado por el usuario.
- Logo PRISMA real en topbar y portada.
- Alcance visual: Tablet + PC + App.
- Smoke ajustable entre 0% y 100%.
- Valor smoke persistente en el navegador.

### Hashes de autoridad visual

- Fondo: `b78d7b4a33fb6cab1f0dafbd657f38d2929bb38bc7088d4a06138b1cadc2d346`
- Logo completo: `37554226f3e05cf65fc0e9588a7a6eb4910c493a4ee0db4c5a40009ce970ae8a`
- Isotipo: `51baaf426570d75f7ba7584e57674ac856bed59ee871dd1d7866e18ae5a01ccb`


## Corrección V3

El fondo estaba oculto por un contexto de apilamiento incorrecto:

- `.atlas-scene` pasó de `z-index: -3` a `z-index: 0`;
- `.atlas-shell` ahora ocupa `z-index: 1`;
- `body` es transparente;
- `html` conserva el color de respaldo;
- smoke predeterminado: 32%;
- superficies documentales ligeramente más transparentes;
- la preferencia smoke V3 se aplica a todas las páginas.


## Corrección V4

- Grafito es el acento predeterminado.
- Ocho acentos semánticos.
- Tres controles independientes:
  - smoke de escena;
  - opacidad del chrome global;
  - opacidad de superficies de contenido.
- Topbar y sidebar usan saturación del backdrop.
- Bordes de chrome con difracción prismática.
- Trazas especulares horizontales y verticales.
- Preferencias V4 aisladas de versiones anteriores.


## Lote 2

Páginas añadidas:

- `b-materiales.html`
- `c-acciones.html`
- `d-entrada-texto.html`
- `e-seleccion-filtros.html`
- `f-navegacion.html`

Total público: 10 páginas.

Incluye laboratorios interactivos de materiales, botones, campos, selección,
filtros y navegación. Conserva grafito, tres controles de transparencia,
difracción especular y el fondo canónico.


## Polish Pass 1

Embellecimiento incremental sobre A-G, M y Z:

- bloom gaussiano localizado;
- anillo de energía al presionar;
- progreso multicapa con brillo y punto energético;
- cards y laboratorios con reflejo localizado;
- foco premium;
- navegación y footer con mayor profundidad;
- scrollbar premium;
- sin reconstruir layouts ni añadir secciones.


## Interaction Refinement 1

- puntos/anillos de clic retirados;
- brillo de puntero reducido y limitado a botones;
- botones sólidos;
- rail izquierdo translúcido;
- cromatismo del rail reducido;
- layouts y secciones intactos.


## Batch 3 · H–L

Páginas añadidas:

- `h-listas.html`
- `i-paneles-cards.html`
- `j-expansion.html`
- `k-estados-feedback.html`
- `l-carga-progreso.html`

El lote conserva todo lo aprobado en `atlasb2r.zip`. Sólo actualiza la
navegación compartida y añade los contratos, estilos e interacciones necesarios
para H–L.

Total público después de la fusión: 15 páginas.


## Completion N–Y

Añade doce páginas:

N Operativos, O Patrones, P Movimiento, Q Responsive y accesibilidad,
R Contenido, S Analítica, T Archivos, U Calendario, V Comercio,
W Seguridad, X Diagnóstico y Y Internacionalización/impresión/offline.

Resultado final: 27 páginas, 26 secciones y 418 elementos.
Los cuerpos A–M y Z permanecen congelados; únicamente se refresca su navegación.

## Canonical visual control and exact Cobrar application

Atlasfin is the single canonical visual-control cabin. The Tablet POS → Cobrar pilot joins the certified UIMAP hierarchy, RIFAT binding and recipe, and the existing Code Atlas UI Bridge into one regenerable read-only projection.

- Open the control from `index.html`; its payload loads only on demand.
- The plan is paginated and uses precomputed scalar search text.
- The historical V1 pilot still has `runtimeMutationAllowed=false` and `productApplicationAllowed=false`.
- The separate current transaction projection is `assets/data/visual-application.cobrar.current.json`.
- The browser prepares/exports requests and reads BEFORE, patch, gates, rollback, result, and AFTER; it never writes product files.
- Only the existing UI Bridge exact Cobrar runner can validate/apply the one-file product transaction.
- Mamastrophic evidence records real state skips instead of fabricating loading or focus on a disabled control.

Regenerate only with an immutable certified UIMAP batch:

`py -3 generator/build_canonical_visual_control.py . --uimap-batch <batch.json> --mamastrophic-evidence <evidence.json> --application-result <result.json> --application-evidence <bundle.json>`

Validate without opening a browser:

`powershell -NoProfile -File RUN.ps1`

Run the fail-closed static browser layout gate without a server:

`powershell -NoProfile -File RUN.ps1 -VisualLayoutGate -EvidenceRoot <output-directory>`

The gate measures card collisions, parent containment, horizontal and vertical
overflow, and client/scroll dimensions at 1365x768, 1024x768, 900x768, and
640x900. It also injects long status labels in browser memory to exercise the
canonical wrapping rules without changing Atlasfin data.

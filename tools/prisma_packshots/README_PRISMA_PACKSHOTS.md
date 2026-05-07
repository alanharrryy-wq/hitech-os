# PRISMA Packshots - Registry Updater

Este README acompaña al script:

```text
F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py
```

La idea es simple: cuando agregues PNGs nuevos a las carpetas de packshots, corres el script, te detecta lo nuevo, genera una plantilla de revisión, y después de llenar esa plantilla actualiza el registro y organiza los archivos en:

```text
F:\light packshots
F:\dark packshots
```

No toca Tablet, no toca PC, no toca código del POS, no modifica imágenes, no convierte PNGs, no borra originales. Es una herramienta de catálogo de imágenes, no un duende con llaves del repo.

---

## 1. Ubicación recomendada dentro del repo

Crear esta carpeta:

```text
F:\repos\hitech-os\tools\prisma_packshots
```

Y poner ahí:

```text
F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py
F:\repos\hitech-os\tools\prisma_packshots\README_PRISMA_PACKSHOTS.md
```

El script crea/usa esta carpeta de datos:

```text
F:\repos\hitech-os\tools\prisma_packshots\data
```

Ahí mantiene el registry vivo:

```text
F:\repos\hitech-os\tools\prisma_packshots\data\prisma_packshot_registry.json
F:\repos\hitech-os\tools\prisma_packshots\data\prisma_packshot_registry.csv
```

Si todavía no existe ese registry, el script intenta arrancar desde:

```text
F:\descargasf\prisma_packshot_classification_manifest.json
```

---

## 2. Comando principal

Cada vez que agregues PNGs nuevos, corre:

```powershell
python "F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py" --run
```

Eso hace:

1. escanea carpetas fuente;
2. detecta PNGs ya conocidos por `sha256`;
3. copia los conocidos a `F:\light packshots` o `F:\dark packshots`;
4. genera inventario CSV/JSON en `F:\descargasf`;
5. genera `pending_review.csv` para PNGs nuevos;
6. escribe log único en `F:\descargasf`.

Modo seguro por defecto:

```text
--mode copy
```

O sea, copia. No mueve. Porque mover originales sin querer es como barrer la tienda y tirar la caja registradora junto con el polvo.

---

## 3. Carpetas fuente que escanea por defecto

El script busca PNGs en:

```text
F:\Imagenes packshot 1
F:\Imagenes packshot 2
F:\Imagenes packshot 3
F:\Imagenes packshot 4
F:\Imagenes packshot 5
F:\Imagenes packshot 6
F:\Imagenes packshot 7
F:\Imagenes packshot 8
F:\Imagenes packshot 9
F:\Imagenes packshot 10
```

Si quieres escanear otra carpeta:

```powershell
python "F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py" --run --source-root "F:\Imagenes packshot 11"
```

Puedes repetir `--source-root` varias veces.

---

## 4. Flujo para PNGs nuevos

### Paso A: agregar PNGs

Extrae o copia los PNGs nuevos a una carpeta tipo:

```text
F:\Imagenes packshot 3
```

### Paso B: correr scan

```powershell
python "F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py" --run
```

Si hay archivos nuevos, el script genera algo como:

```text
F:\descargasf\prisma_packshot_pending_review_20260506_153000.csv
```

### Paso C: llenar el CSV de revisión

Abre ese CSV y llena los campos humanos para cada PNG nuevo.

### Paso D: aplicar revisión

```powershell
python "F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py" --apply-review "F:\descargasf\prisma_packshot_pending_review_20260506_153000.csv"
```

Eso valida los campos y actualiza:

```text
F:\repos\hitech-os\tools\prisma_packshots\data\prisma_packshot_registry.json
F:\repos\hitech-os\tools\prisma_packshots\data\prisma_packshot_registry.csv
```

### Paso E: organizar otra vez

```powershell
python "F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py" --run
```

Ahora esos PNGs ya son conocidos y se copian al folder final correcto.

---

## 5. Qué se debe generar / llenar para cada PNG nuevo

Cada PNG nuevo necesita una fila de clasificación. El script genera automáticamente estos campos técnicos:

| Campo | Quién lo genera | Para qué sirve |
|---|---|---|
| `source_root` | script | carpeta fuente donde está el PNG |
| `relative_path` | script | ruta relativa dentro de la fuente |
| `original_filename` | script | nombre original del PNG |
| `size_bytes` | script | tamaño del archivo |
| `sha256` | script | huella única para empatar sin adivinar |
| `width` | script | ancho PNG si puede leerlo |
| `height` | script | alto PNG si puede leerlo |
| `skin_guess` | script | pista floja: `light`, `dark` o `unknown` |
| `skin_guess_confidence` | script | confianza de la pista, no verdad absoluta |

Y tú llenas estos campos humanos:

| Campo | Requerido | Ejemplo | Regla |
|---|---:|---|---|
| `product_name` | Sí | `Pan de caja` | Nombre genérico visible del producto |
| `brand` | No | vacío | En PRISMA genérico normalmente va vacío |
| `variant` | No | `multigrano fibra y semillas` | Sabor, tipo o variante visible |
| `size` | No, pero recomendado | `620g`, `600ml`, `1l` | Solo si se ve claro |
| `category` | Sí | `panaderia`, `bebidas`, `lacteos` | Categoría operativa |
| `skin` | Sí | `light` o `dark` | Según fondo/diseño visual |
| `confidence` | Sí | `0.98` | De `0.00` a `1.00` |
| `target_filename` | Sí | `pan-de-caja-multigrano-620g.png` | Nombre final en slug ASCII |
| `action` | Sí | `organize` | Usar `organize`, `review` o `skip` |
| `notes` | No | `Fondo claro, etiqueta visible.` | Ambigüedades o aclaraciones |

---

## 6. Reglas de nombres

Usar minúsculas, ASCII, guiones y extensión `.png`.

Patrón recomendado para productos genéricos:

```text
producto-variante-size.png
```

Ejemplos:

```text
pan-de-caja-multigrano-620g.png
cafe-soluble-200g.png
agua-purificada-600ml.png
leche-entera-1l.png
papas-fritas-original-45g.png
```

Si no hay variante:

```text
producto-size.png
```

Si no hay tamaño visible:

```text
producto-variante.png
```

Si hay dos archivos con el mismo destino dentro de la misma carpeta final, el script no sobrescribe. Crea sufijos:

```text
pan-de-caja-multigrano-620g.png
pan-de-caja-multigrano-620g-02.png
pan-de-caja-multigrano-620g-03.png
```

---

## 7. Reglas para `skin`

Usar:

```text
light
dark
unknown
```

### `light`

Cuando el packshot tiene fondo:

- blanco;
- crema;
- claro;
- limpio;
- high-key;
- pensado para PRISMA Light.

### `dark`

Cuando el packshot tiene fondo:

- negro;
- azul marino;
- oscuro;
- premium;
- low-key;
- pensado para PRISMA Black/Dark.

### `unknown`

Solo si no se puede decidir. Si usas `unknown`, por defecto no se organiza. Para incluir unknown:

```powershell
python "F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py" --run --include-unknown
```

---

## 8. Categorías sugeridas

Usa categorías cortas, consistentes y sin espacios. Ejemplos:

```text
abarrotes
bebidas
cafe
cereales
botanas
galletas
lacteos
panaderia
pastas
sopas
legumbres
granos_semillas
harinas_reposteria
endulzantes
jarabes
frutos_secos
limpieza
higiene
mascotas
congelados
refrigerados
```

No inventes una categoría nueva si una existente ya sirve. Luego esto se vuelve vecindad de etiquetas y nadie quiere administrar una vecindad de etiquetas.

---

## 9. Campos mínimos para que una fila pase validación

Para `action=organize`, cada fila necesita:

```text
product_name
category
skin
confidence
target_filename
sha256
```

También debe cumplir:

```text
skin = light | dark | unknown
action = organize | review | skip
confidence entre 0.00 y 1.00
target_filename termina en .png
```

---

## 10. Comandos útiles

### Escanear y organizar conocidos

```powershell
python "F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py" --run
```

### Hacer prueba sin copiar ni mover

```powershell
python "F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py" --run --dry-run
```

### Mover en lugar de copiar

```powershell
python "F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py" --run --mode move
```

### Aplicar CSV revisado

```powershell
python "F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py" --apply-review "F:\descargasf\prisma_packshot_pending_review_YYYYMMDD_HHMMSS.csv"
```

### Generar contact sheet opcional

Requiere Pillow:

```powershell
python -m pip install pillow
```

Luego:

```powershell
python "F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py" --run --contact-sheet
```

---

## 11. Qué archivos genera en `F:\descargasf`

Cada corrida genera evidencia:

```text
prisma_packshot_inventory_YYYYMMDD_HHMMSS.csv
prisma_packshot_inventory_YYYYMMDD_HHMMSS.json
prisma_packshot_operations_YYYYMMDD_HHMMSS.json
prisma_packshot_registry_snapshot_YYYYMMDD_HHMMSS.json
prisma_packshot_registry_snapshot_YYYYMMDD_HHMMSS.csv
prisma_packshot_update_YYYYMMDD_HHMMSS.log
```

Si hay PNGs nuevos:

```text
prisma_packshot_pending_review_YYYYMMDD_HHMMSS.csv
```

---

## 12. Estados finales

El resumen puede terminar como:

```text
READY
READY_WITH_REVIEW
READY_WITH_CAVEATS
```

### `READY`

Todo conocido, todo organizado, sin pendientes.

### `READY_WITH_REVIEW`

Hay PNGs nuevos que requieren llenar el CSV de revisión.

### `READY_WITH_CAVEATS`

Hubo errores de IO, validación o algo que necesita revisión.

---

## 13. Criterio de calidad

Para cada PNG nuevo:

- no inventar marca;
- no inventar tamaño;
- no usar OCR como juez final;
- revisar visualmente producto y piel;
- usar nombres genéricos estables;
- emparejar `light` y `dark` con el mismo nombre base cuando sea el mismo producto;
- dejar notas si algo se ve raro;
- si dudas, poner `action=review`, no `organize`.

En corto: el script carga los costales, pero tú decides qué producto es. Porque si el programa empieza a bautizar empaques como padrino borracho, luego el catálogo queda embrujado.

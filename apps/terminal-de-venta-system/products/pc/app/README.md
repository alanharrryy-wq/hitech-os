# Panel administrativo de inventario 6.1.1

Base saneada y chequeada para la app gemela de **inventario y backoffice en PC**.

## Qué trae
- Shell navegable con rutas: `/catalog`, `/stock`, `/counts`, `/purchasing`, `/receiving`, `/replenishment`, `/audit`, `/sync`
- `src/lib/utils.ts` y `src/lib/core/types.ts` ya presentes
- `module-registry.ts` corregido y tipado
- contrato gemelo en `shared/twin-kernel` como superficie compartida única
- `prisma/schema.prisma` y `prisma/dev.db` con dataset de desarrollo
- repositorios Prisma base y catálogo de eventos de sync
- instalador `install_pc.py`
- validador `tools/validate_package.py`

## Chequeos corridos antes de empacar
- JSON válido
- imports resueltos a archivos existentes
- naming limpio sin restos del template viejo
- `tsc --noEmit`
- sintaxis Python de instalador y herramientas
- resumen de DB SQLite

## Comandos sugeridos
```bash
npm install
npm run check:all
npm run dev
```

## Nota
Este ZIP ya no depende de `../../tsconfig.base.json` ni de `packages/` externos ausentes. Viene autocontenido.

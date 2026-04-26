# PRISMA UI Docs Modular Nivel Dios v3

Este paquete instala la documentacion modular de interfaces PRISMA para PC y Tablet.

## Que contiene

- Blueprints maestros PC y Tablet.
- Contratos compartidos para pantallas, plugins, eventos, permisos, offline, sync y auditoria.
- 20 pantallas base documentadas.
- Modulos base reutilizables.
- Target Atlas con familias operativas.
- Playbooks por vertical.
- Patrones de UI y comportamiento.
- Matrices de validacion para crecer sin romper.

## Filosofia

PRISMA no debe documentarse como coleccion de pantallas. Debe documentarse como plataforma modular. Las pantallas son vistas. Los modulos son capacidades. Los plugins son extensiones gobernadas. El core es sagrado, porque si el core se contamina, luego ni con incienso de Scrum se salva.

## Arbol recomendado

```text
docs/prisma/ui/
  README.md
  MANIFEST.md
  00_START_HERE.md
  blueprints/
    pc/master.md
    tablet/master.md
  apps/
    pc/screens/
    tablet/screens/
  shared/
    contracts/
    modules/
    policies/
  plugins/
    target-atlas/
    playbooks/
    examples/
  patterns/
  governance/
  implementation/
  qa/
  roadmap/
```

## Como usarlo

1. Leer `00_START_HERE.md`.
2. Abrir `blueprints/pc/master.md` y `blueprints/tablet/master.md`.
3. Revisar `shared/contracts/plugin-contract.md` antes de crear cualquier plugin.
4. Usar `plugins/target-atlas/index.md` para decidir familia operativa.
5. Crear extension usando las plantillas en `governance/`.

## Criterio de aceptacion

Una extension nueva solo entra si declara:

- modulos tocados
- pantallas PC afectadas
- pantallas Tablet afectadas
- permisos
- eventos
- offline
- sync
- auditoria
- rollback
- modo degradado

Si no declara eso, no es plugin. Es ocurrencia con corbata.

# PRISMA PC Suppliers UX CSS Import Bridge 08

## Objetivo

La v07 instaló estructura visual nueva para `/proveedores`, pero el navegador siguió mostrando texto plano porque `app/suppliers.css` no estaba importado por el árbol de Next.

Esta inyección corrige la causa real:

- agrega `app/suppliers-ux-v08.css`;
- importa ese CSS desde `app/layout.tsx`;
- mantiene el componente `SmartPurchaseWorkbench` con estructura v07;
- conserva alcance local PC, sin tocar Tablet ni `shared-kernel`.

## Resultado esperado

En `/proveedores` deben verse:

- cards de recomendación con productos separados;
- CTA dorado `¿POR QUÉ PRISMA LO RECOMIENDA?`;
- checklist visual de confianza;
- agenda/timeline;
- roadmap de trazabilidad;
- cero rutas API visibles en la interfaz.

## Validación visual

Abrir:

```text
http://127.0.0.1:3130/proveedores
```

Probar zoom 125% y 150%.

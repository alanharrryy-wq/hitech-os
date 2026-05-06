# PRISMA_BLACK_VISUAL_REFINEMENT_01G

## Propósito

Hacer que PRISMA se vea más nítido, premium y coherente sin romper autonomía funcional ni meter rediseño estructural.

## Superficies cubiertas

- **Tablet POS**: experiencia principal de venta standalone.
- **PC Backoffice**: asset administrativo y de control avanzado.
- **App móvil / Pulso**: asset companion de pulso, consulta y alertas, actualmente ubicado en `products/pc/app/app/pulso`.

## Invariantes

1. **Tablet vende sola**. Ningún cambio visual puede sugerir dependencia de PC o App móvil para operar la venta básica.
2. **Cobertura tri-superficie**. Todo refinement compartido debe declararse para Tablet, PC y Mobile.
3. **Sin rediseño funcional**. No se tocan rutas, datos, lógica ni layout estructural.
4. **Visual premium conservador**. Se permite limpiar contraste, profundidad, sombra, blur y acabado de superficies.

## Cambio introducido por 01G

- Refinamiento de tokens oscuros y claros.
- Vidrio más limpio y menos lechoso.
- Tarjetas con borde y sombra más nítidos.
- Shell Tablet y shell PC más consistentes.
- Pulso/Mobile alineado visualmente con el lenguaje Black.
- Guardian Python para validar contrato, cobertura y markers.

## Archivos visuales tocados

- `products/shared-ui/prisma/tokens/prisma-theme.css`
- `products/shared-ui/prisma/components/prisma-components.css`
- `products/tablet/app/app/globals.css`
- `products/tablet/app/components/pos/pos.module.css`
- `products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css`
- `products/pc/app/app/globals.css`
- `products/pc/app/app/pulso/prisma-pulso.module.css`

## Resultados esperados

- Mayor sensación de orden visual.
- Mejor profundidad en cards y shells.
- Menos “neblina” y más legibilidad.
- Coherencia entre Tablet, PC y Mobile.

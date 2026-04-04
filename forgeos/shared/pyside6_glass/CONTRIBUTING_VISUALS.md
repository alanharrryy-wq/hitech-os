# Contribuir cambios visuales

## Antes de tocar código

Decide primero si el cambio pertenece a una de estas capas:

- contrato semántico,
- normalización,
- adapter de contexto,
- runtime oficial del core,
- shell estructural,
- generator/tooling,
- validación y gobernanza.

Si no está claro, no mezcles todo en el mismo PR.

## Buenas prácticas

1. Declara intención, no estilo final.
2. Conserva `ui_baseline` delgado.
3. Documenta cambios de contrato o vocabulario.
4. Mantén generator y validator fuera de `runtime.py`.
5. Corre el validador antes de proponer merge.

## Malas prácticas

- Parchear screens con estilos incrustados.
- Duplicar coordinación visual del core.
- Acoplar el builder con decisiones de render final.
- Esconder bypass de tokens en helpers ambiguos.

## Recomendación operativa

Prefiere PRs pequeños por capa. Un diff ordenado se revisa como bisturí;
uno mezclado entra como licuadora sin tapa.

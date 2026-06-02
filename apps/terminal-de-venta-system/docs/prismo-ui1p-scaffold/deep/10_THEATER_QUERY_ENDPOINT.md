# 10 · Theater Query Endpoint

## Contrato recomendado
`POST /api/prismo/theater/query`

## Qué debe hacer internamente
- leer status learning;
- pedir protocolo recomendado;
- obtener evidencia top;
- consultar memorias;
- construir render_plan;
- seleccionar bloques Auto Render Ensemble;
- devolver contrato único para la UI.

## Por qué
Evita que el frontend haga veinte fetches desordenados. La UI recibe una escena lista para pintar.

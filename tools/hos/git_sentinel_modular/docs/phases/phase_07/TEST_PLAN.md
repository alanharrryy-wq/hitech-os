# Test plan for phase_07

- Happy path con todos los ZIPs
- ZIP faltante
- `phase_manifest.json` faltante
- archivo declarado en manifest pero ausente
- checksum incorrecto
- broken markdown link
- ruta objetivo que intente salirse del scaffold root
- scaffold no encontrado

## Resultado esperado
Cada error debe incluir:
- fase
- ruta exacta
- mensaje exacto

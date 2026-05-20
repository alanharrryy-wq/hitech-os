# PRISMA Control Center V40 UI/UX Theme Hardening

Patch para corregir placeholders visibles del reactor y reforzar UI/UX sin tocar backend, endpoints, auth, persistencia ni contratos. Tablet sigue operando independiente; PC gobierna si existe; Mobile supervisa; Core registra; Control audita.

## 50 mejoras UI

1. Corrected reactor default copy
2. Theme-aware quick rail
3. Theme pressed state
4. Operator status capsule
5. Command palette shell
6. Focus rings
7. Touch target floor
8. Card hover depth
9. Button sweep highlight
10. Bar sweep highlight
11. Tabular numerals
12. Reactor halo
13. Orb lens sheen
14. Panel hover border
15. Compact density mode
16. Theme-specific rail material
17. Theme-specific palette material
18. Pearl light contrast
19. Tactical angular compactness
20. Rose rail tint
21. Liquid cyan caustics
22. Readable selection color
23. Better section letter spacing
24. Improved body line height
25. State colors for pending
26. State colors for ok
27. State colors for warn
28. State colors for error
29. Visible skip link
30. Toast stack
31. Tooltip layer
32. Mobile sticky rail
33. Small-screen palette layout
34. Responsive rail actions
35. Safe-area aware controls
36. Reduced-motion support
37. Contain paint for charts
38. Active theme badges
39. Metric active press
40. Signal active press
41. Quality card transition
42. Node hover elevation
43. Command grid equalization
44. Mini chart stability
45. Reactor text shadow logic
46. Scroll margin for timeline
47. System accent color
48. No horizontal overflow aids
49. Densified panels
50. Densified cards

## 50 mejoras UX

1. Ctrl K command palette
2. Esc closes palette
3. Ctrl 1 theme Liquid
4. Ctrl 2 theme Tactical
5. Ctrl 3 theme Rose
6. Ctrl 4 theme Pearl
7. D cycles density
8. Question mark opens help
9. Quick jump to reactor
10. Quick jump to commands
11. Quick jump to status
12. Quick jump to topology
13. Quick jump to timeline
14. Quick switch to Quality Bay
15. Quick switch to Operation
16. Theme choice persisted
17. Density choice persisted
18. Online state reflected
19. Offline state reflected
20. ARIA live for reactor
21. ARIA live for queue
22. ARIA live for topology
23. Buttons get aria labels
24. Buttons get titles
25. Palette uses button roles
26. Palette search filters
27. Palette first result selection
28. Click outside closes palette
29. Skip link to main
30. Toast feedback
31. Helpful keyboard hints
32. Status capsule reports theme
33. Status capsule reports density
34. Health fetch mirrors runtime
35. No false green on health failure
36. No stale English placeholders
37. Queue wording localized
38. Topology wording localized
39. Health score updates bars
40. Warnings update queue card
41. Errors update risk
42. Latency is measured
43. Safe JSON parsing
44. Network failure is honest
45. Visual state mirrors data state
46. LocalStorage guarded
47. Progressive enhancement
48. Works if v24 is absent
49. Works if API is absent
50. No backend dependency for polish

## Archivos modificados/agregados

- internal/web/index.html
- internal/web/v24_cockpit.js
- internal/web/prisma_v40_uiux.css
- internal/web/prisma_v40_uiux.js
- internal/docs/README_V40_UIUX_THEMES.md
- internal/docs/MANIFEST_PRISMA_V40_UIUX.json

## Validacion local sugerida

1. Levantar Control Center con los wrappers existentes.
2. Abrir el panel.
3. Confirmar que el reactor ya muestra copy corregido en espanol y no placeholders viejos.
4. Probar Ctrl+K, Ctrl+1..4 y D.
5. Cambiar entre Liquid, Tactical, Rose y Pearl.

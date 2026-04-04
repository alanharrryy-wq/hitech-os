# Premium Capabilities Contract (100)

Authoritative full premium capability model for the pyside6_glass workbench/editor.

Status legend: `solid`, `partial`, `missing`, `improved_partial`, `deferred`.

## Base de interacción y control
1. La app abre rápido y se siente viva desde el primer segundo [release-blocker]
2. La ventana completa se puede redimensionar por esquinas y bordes sin glitches [release-blocker]
3. Los paneles internos se pueden arrastrar cuando eso forma parte del producto [release-blocker]
4. Los paneles internos se pueden redimensionar con handles claros y consistentes [release-blocker]
5. Todo movimiento respeta límites del workspace y no se sale del canvas [release-blocker]
6. Los elementos interactivos responden igual con mouse, trackpad y touch si aplica [release-blocker]
7. No hay zonas muertas donde parece clickeable pero no pasa nada [release-blocker]
8. El foco visual siempre deja claro qué elemento está activo [release-blocker]
9. Los estados hover, pressed, selected y focused están bien diferenciados [release-blocker]
10. No hay acciones visibles que se sientan decorativas o inútiles [release-blocker]
## Layout y composición
11. El workspace principal domina visualmente la pantalla [release-blocker]
12. No hay contenedores inútiles dentro de contenedores inútiles [release-blocker]
13. Las barras laterales no roban espacio si no son necesarias [release-blocker]
14. El layout se adapta bien cuando ocultas o abres paneles secundarios [release-blocker]
15. Los márgenes y paddings se sienten intencionales, no acumulados [release-blocker]
16. El contenido importante nunca queda aplastado por chrome innecesario [release-blocker]
17. La jerarquía visual se entiende en 3 segundos [release-blocker]
18. El sistema soporta bien vistas vacías sin verse roto [release-blocker]
19. La app no colapsa feo en tamaños chicos o medianos [release-blocker]
20. Hay equilibrio entre densidad de información y aire visual [release-blocker]
## Navegación premium
21. Siempre sabes dónde estás dentro de la app [release-blocker]
22. Siempre sabes qué puedes hacer después [release-blocker]
23. Las rutas principales son pocas, claras y memorables [release-blocker]
24. Existe una forma rápida global de buscar o invocar cosas importantes [release-blocker]
25. Los cambios de vista no se sienten abruptos ni confusos [release-blocker]
26. El back / close / cancel siempre hace algo esperable [release-blocker]
27. La navegación no depende de aprenderte el truco oculto [release-blocker]
28. Hay accesos rápidos para usuarios intensivos [release-blocker]
29. Las herramientas avanzadas están accesibles sin dominar toda la UI [release-blocker]
30. La navegación secundaria no compite con la principal [release-blocker]
## Flujo de trabajo y productividad
31. Crear algo nuevo es obvio y no da miedo [release-blocker]
32. Editar algo existente es directo y no te manda por tres menús [release-blocker]
33. Reemplazar, mover, duplicar o borrar elementos es consistente [release-blocker]
34. Los flujos comunes requieren pocos clics [release-blocker]
35. Las acciones pesadas tienen confirmación clara [release-blocker]
36. Las acciones frecuentes tienen shortcuts o paths rápidos [release-blocker]
37. El sistema favorece continuidad, no reinicios pendejos [release-blocker]
38. Puedes retomar trabajo sin perder contexto [release-blocker]
39. La app tolera interrupciones sin romper el estado [release-blocker]
40. El usuario siente progreso constante, no fricción constante [release-blocker]
## Claridad de acciones
41. Cada botón tiene una intención clara y específica
42. Los CTAs principales se distinguen sin gritar
43. Las acciones secundarias no roban protagonismo
44. Las acciones destructivas están claramente separadas
45. Si una acción no está disponible, la UI explica por qué
46. Las acciones contextuales aparecen cuando importan, no siempre
47. No hay duplicidad rara entre botones que hacen casi lo mismo
48. El lenguaje de acciones es consistente en toda la app
49. La app no te obliga a adivinar qué botón era el bueno
50. Ningún flujo clave depende de un botón escondido en un panel oscuro
## Estados vacíos, loading y feedback
51. Los empty states se ven premium, no como abandono
52. Los empty states explican qué hacer después
53. Los skeletons/loading states se sienten elegantes y útiles
54. Nunca hay pantallas congeladas sin feedback
55. Guardar, enviar, cargar o sincronizar muestran progreso entendible
56. Los errores se explican con lenguaje humano
57. Los éxitos confirman sin interrumpir de más
58. Los warnings no parecen errores fatales
59. El feedback temporal desaparece cuando debe desaparecer
60. El sistema comunica claramente cuando una acción sigue corriendo
## Consistencia visual
61. Hay un solo lenguaje visual dominante
62. Los bordes están controlados y no ensucian todo
63. Los radios, sombras y transparencias siguen reglas claras
64. La paleta no se siente accidental ni saturada
65. Los colores de estado tienen significado consistente
66. No hay componentes viejos mezclados con otros nuevos
67. Los íconos tienen el mismo estilo y peso visual
68. Los tabs, chips, cards y panels hablan el mismo idioma visual
69. El contraste está bien cuidado sin verse gritón
70. La UI se ve fina tanto en screenshot como en uso real
## Belleza percibida y delight
71. La app tiene un wow factor sobrio, no cirquero
72. Las animaciones son suaves y útiles, no mamadoras
73. Hay profundidad visual sin ensuciar legibilidad
74. El vidrio, blur o glow, si existen, se usan con disciplina
75. El contenido importante siempre se ve más fuerte que los adornos
76. La interfaz se siente moderna, no retro-utilitaria
77. La estética aguanta muchas horas de uso sin cansar
78. La app se siente cara aunque haga cosas simples
79. La identidad visual es memorable
80. La UI no parece plantilla genérica con maquillaje oscuro
## Datos, verdad y confianza
81. Siempre está claro qué datos estás viendo
82. Siempre está claro de dónde vienen esos datos
83. Siempre está claro cuándo fueron actualizados
84. Las acciones sobre datos dejan rastro o confirmación visible
85. Los estados de sync/dispatch/error no están escondidos
86. Puedes distinguir entre draft, activo, fallido, pendiente, aprobado, etc.
87. No hay ambigüedad entre preview, estado actual y estado guardado
88. La app evita que tomes decisiones con información vieja sin avisarte
89. Los cambios tienen persistencia clara o rollback claro
90. El usuario siente confianza operativa, no incertidumbre
## Robustez, accesibilidad y calidad total
91. La app soporta bien sesiones largas sin degradarse culero
92. Los componentes no se rompen al cambiar tamaño, zoom o densidad
93. El teclado permite operar flujos importantes
94. El foco accesible está bien resuelto
95. El texto sigue siendo legible en todos los estados
96. El sistema tolera errores parciales sin colapsar toda la experiencia
97. Las funcionalidades chidas tienen protección contra regresión
98. Hay tests o checks para interacción crítica, no solo para lógica interna
99. El producto tiene un contrato claro de capacidades sagradas
100. Cada release puede demostrar que no rompió lo que hacía amada a la app

This file is consumed by UX release proof tooling and documentation.
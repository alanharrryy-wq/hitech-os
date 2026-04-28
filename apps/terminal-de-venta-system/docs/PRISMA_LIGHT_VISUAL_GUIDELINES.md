# PRISMA Light POS — Visual Guidelines

## 0. Propósito

Este documento define las reglas de dirección visual para la versión blanca / Light de PRISMA POS.

Sirve para responder una pregunta simple:

> ¿Esto se ve como PRISMA Light o como otra app cualquiera vestida de blanco?

Si la respuesta es “otra app cualquiera”, se rechaza. Sin drama. Bueno, poquito drama sí, porque para eso estamos.

---

## 1. Personalidad visual

PRISMA Light debe sentirse:

- premium
- claro
- moderno
- táctil
- rápido
- elegante
- operacional
- confiable

Debe parecer una terminal de venta que vive en un negocio real, pero con una interfaz tan cuidada que hasta el lector de código de barras se endereza la espalda.

---

## 2. Palabras clave del estilo

Usar como guía:

```text
blanco cálido
vidrio suave
dorado sobrio
profundidad ligera
producto protagonista
carrito dominante
claridad de cobro
lujo funcional
```

No usar como guía:

```text
dashboard genérico
sistema contable plano
app médica
banca aburrida
bootstrap sin cariño
plantilla de marketplace
```

---

## 3. Identidad visual principal

### 3.1 La luz

La interfaz debe tener una luz ambiental suave.

No es blanco plano.
No es gris muerto.
Es un ambiente claro con capas.

Fondos recomendados:

- blanco cálido
- gris niebla
- marfil ligero
- gradientes apenas visibles

### 3.2 El dorado

El dorado debe ser la señal de valor, acción y marca.

Se usa en:

- item activo de sidebar
- categoría activa
- precio total
- botón COBRAR
- iconos de acciones secundarias
- focus states importantes

No se usa en:

- cada texto
- cada borde
- cada icono
- cada cosa que respira

El dorado debe mandar poquito, pero mandar bien. Como doña que no grita, pero todos le hacen caso.

---

## 4. Jerarquía visual

La pantalla debe leerse así:

1. `Ventas`
2. buscador / escaneo
3. categorías
4. productos
5. carrito
6. total
7. `COBRAR`

El usuario debe entender en menos de un segundo:

- dónde busca
- qué puede vender
- qué lleva el cliente
- cuánto debe pagar
- dónde cobrar

Si tiene que pensar demasiado, la UI perdió.

---

## 5. Reglas de layout

### 5.1 Tres zonas intocables

No romper:

- izquierda: navegación
- centro: productos
- derecha: carrito

No convertir la pantalla en:

- top nav solamente
- grid completo sin carrito
- dashboard de KPIs
- tabla administrativa

### 5.2 Aire visual

Debe haber espacio entre elementos.
El Light necesita respirar más que el Dark porque el blanco evidencia todo.

Reglas:

- no pegar cards entre sí
- no juntar labels con precios
- no comprimir el carrito
- no llenar todos los huecos por ansiedad humana

---

## 6. Superficies

### 6.1 Paneles

Deben ser:

- blancos
- ligeramente translúcidos si aplica
- con borde suave
- con sombra difusa

No usar:

- bordes negros
- sombras duras
- grises demasiado pesados

### 6.2 Cards de producto

Deben sentirse como vitrinas pequeñas.

Cada producto debe parecer exhibido, no aventado.

Reglas:

- imagen grande
- pedestal / sombra debajo
- texto limpio
- precio claro
- stock visible
- favorito discreto

---

## 7. Imaginería de productos

### 7.1 Tamaño

La imagen debe dominar la card.

Si el producto parece mini estampita, está mal.

### 7.2 Fondo del producto

Cada producto debe tener:

- sombra base
- pedestal suave
- halo muy leve opcional

No poner fondos de colores chillones dentro de la card.

### 7.3 Recorte

Los productos deben estar:

- limpios
- centrados
- con buena escala
- sin deformarse

---

## 8. Botones

### 8.1 Botón principal

Solo uno debe ser el rey: `COBRAR`.

Características:

- dorado
- ancho completo
- alto
- contraste fuerte
- shortcut visible

Si otro botón compite con COBRAR, bajarlo de peso.

### 8.2 Botones secundarios

Deben ser blancos, suaves, con icono dorado.

Ejemplos:

- Cotización
- Guardar
- Limpiar

Deben parecer útiles, no protagonistas.

---

## 9. Iconos

Estilo:

- lineal
- simple
- consistente
- stroke uniforme
- esquinas redondeadas

No mezclar:

- outline con 3D
- emojis
- filled random
- iconos de bibliotecas distintas sin ajustar peso

---

## 10. Tipografía

Debe ser clara y moderna.

Reglas:

- títulos grandes, no gigantes
- labels legibles
- precios fuertes
- meta discreta
- total enorme pero elegante

No usar:

- tipografías decorativas
- condensadas raras
- mayúsculas en todo
- pesos excesivos por todos lados

---

## 11. Color y contraste

### 11.1 Texto

Texto principal casi negro.
Texto secundario gris medio.
Placeholder gris suave.

### 11.2 Dorado

Dorado para jerarquía, no decoración compulsiva.

### 11.3 Estado en línea

Verde pequeño y claro.

### 11.4 Errores

Rojo suave pero inequívoco.

---

## 12. Estados operativos

### 12.1 Venta activa

Carrito visible y lleno.
Total claro.
COBRAR habilitado.

### 12.2 Carrito vacío

Carrito sigue existiendo.
Mostrar estado vacío elegante.

### 12.3 Producto agregado

Feedback suave:

- breve glow dorado
- toast
- cart item nuevo animado ligeramente

### 12.4 Escaneo exitoso

Agregar producto rápido.
Mostrar feedback corto.

### 12.5 Escaneo fallido

Mensaje claro.
No romper flujo.

---

## 13. Motion

Movimiento permitido:

- hover lift
- focus ring
- transición de chip activo
- actualización de carrito

Duraciones:

- 120–180ms para interacción
- 200–240ms para aparición de toast
- 160ms para product card hover

No usar:

- rebotes
- animaciones largas
- loaders teatrales
- efectos que hagan lenta la caja

---

## 14. Lo que jamás debe pasar

### 14.1 Que parezca dashboard SaaS

Si empiezan a meter tarjetas de KPI al centro en vez de productos, mal.

### 14.2 Que el carrito desaparezca

El carrito es persistente.

### 14.3 Que el dorado se vuelva amarillo barato

Debe ser champagne / oro cálido, no amarillo marcador.

### 14.4 Que las cards sean planas

Necesitan profundidad.

### 14.5 Que el botón COBRAR no destaque

COBRAR debe ser imposible de ignorar.

---

## 15. Comparación Light vs Dark

| Criterio | Dark | Light |
|---|---|---|
| Feeling | lujo nocturno | lujo diurno |
| Fondo | carbón / negro | blanco / gris niebla |
| Acento | dorado intenso | dorado limpio |
| Profundidad | glow atmosférico | sombra suave |
| Producto | spotlight dramático | vitrina limpia |
| Cart | panel oscuro premium | panel blanco premium |

---

## 16. Checklist de revisión visual

Aprobar solo si:

- [ ] Se ve PRISMA
- [ ] Se ve POS
- [ ] Se ve premium
- [ ] Se ve Light, no deslavado
- [ ] Hay dorado sobrio
- [ ] Productos dominan el centro
- [ ] Carrito domina el cierre
- [ ] COBRAR manda
- [ ] Las sombras son suaves
- [ ] La navegación es clara
- [ ] El resultado no parece plantilla genérica

---

## 17. Frase final de dirección

La versión Light debe sentirse como:

> una caja registradora premium de día, limpia, veloz, con productos bien exhibidos y un botón de cobrar que parece decir “aquí se hace la lana”.

No más, no menos.

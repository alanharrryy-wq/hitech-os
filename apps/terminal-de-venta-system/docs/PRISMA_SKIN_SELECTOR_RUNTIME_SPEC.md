# PRISMA Skin Selector Runtime Spec

**Propósito:** definir cómo cambiar entre PRISMA Dark POS y PRISMA Light POS sin romper layout ni flujo.

---

## 1. Nombre visible

Usar:

```text
Apariencia
```

Opciones visibles:

```text
Oscuro
Claro
Sistema
```

No usar “skin” en UI final. El usuario no pidió ponerse otra piel como villano raro; pidió cambiar apariencia.

---

## 2. Valores internos

```ts
type PrismaPosSkin = "dark" | "light" | "system";
```

Resolución final:

```ts
type ResolvedPrismaPosSkin = "dark" | "light";
```

---

## 3. Ubicación recomendada del selector

En el POS, el selector no debe estorbar la venta.

Ubicación recomendada:

```text
Top-right controls -> icono sol/luna -> popover Apariencia
```

También puede vivir en:

```text
Configuración -> Apariencia
```

Regla:

```text
Nunca debe tapar el botón COBRAR ni el carrito.
```

---

## 4. Persistencia

Storage key recomendada:

```text
prisma.pos.skin
```

Valores permitidos:

```text
dark
light
system
```

Si el valor guardado es inválido:

```text
fallback = light
```

---

## 5. Precedencia

```text
1. Config forzada del build/env si existe
2. Preferencia de usuario en localStorage
3. Sistema operativo si user eligió system
4. Default POS
5. Fallback seguro
```

Default recomendado para operación diaria:

```text
light
```

Default recomendado para demo premium:

```text
dark
```

---

## 6. Aplicación runtime

El resultado debe quedar en:

```html
<html data-prisma-skin="dark">
```

ó:

```html
<html data-prisma-skin="light">
```

Compatibilidad opcional:

```html
<html data-theme="prisma-dark">
<html data-theme="prisma-light">
```

Mapeo:

```text
prisma-dark -> dark
prisma-light -> light
```

---

## 7. Anti-FOUC

Para evitar parpadeo de tema:

1. Setear `data-prisma-skin` lo antes posible.
2. Usar un script inline mínimo antes del render visual si hace falta.
3. No esperar a que React hidrate para aplicar colores base.
4. Mantener un fallback CSS válido para ambos skins.

FOUC es cuando la pantalla amanece dark, se baña y sale light medio segundo después. Se ve barato, como anuncio de estética en lona vieja.

---

## 8. Pseudocódigo del resolver

```ts
const allowed = new Set(["dark", "light", "system"]);

function resolveSkin(): "dark" | "light" {
  const stored = localStorage.getItem("prisma.pos.skin");
  const selected = allowed.has(stored ?? "") ? stored : "light";

  if (selected === "system") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  return selected === "dark" ? "dark" : "light";
}

function applySkin(skin: "dark" | "light") {
  document.documentElement.dataset.prismaSkin = skin;
  document.documentElement.dataset.theme = skin === "dark" ? "prisma-dark" : "prisma-light";
}
```

---

## 9. QA del selector

Debe pasar:

- cambiar de dark a light sin recargar layout;
- recargar y conservar skin;
- usar `system` y resolver correcto;
- valor inválido vuelve a fallback;
- no tapa carrito;
- no mueve grid;
- no cambia textos;
- no rompe `COBRAR`.

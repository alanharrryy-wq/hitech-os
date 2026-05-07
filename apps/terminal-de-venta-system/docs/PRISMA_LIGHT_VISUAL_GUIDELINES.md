# PRISMA Light Visual Guidelines

**Purpose:** preserve the visual identity of PRISMA Light POS across prompts, design work and code implementation.

---

## 1. Visual statement

PRISMA Light POS is a premium clear point-of-sale interface for fast retail operation. It combines white frosted panels, blue operational actions, navy typography, realistic product cards and clean retail hierarchy.

It must look like serious business software in daylight, not like somebody made the dark screen pale and called it innovation. Humanidad, por favor.

---

## 2. What PRISMA Light is

| Trait | Meaning |
|---|---|
| Light premium | White, frosted, clean, soft depth |
| Blue operational | Main action, selected states, scan and focus |
| Product-first | Big product images with soft pedestal shadows |
| POS-first | Search, product selection, cart, total, charge |
| es-MX | Spanish Mexican operational copy |
| Spacious 4:3 | Wide composition, not cramped |
| Elegant utility | Good-looking but still practical |

---

## 3. What PRISMA Light is not

| Wrong direction | Why it fails |
|---|---|
| Generic fintech | Loses retail POS identity |
| Flat white dashboard | Loses premium depth |
| Green primary checkout | Breaks PRISMA action hierarchy |
| Random SaaS admin | Loses POS composition |
| Tiny product thumbnails | Kills catalog feel |
| English labels | Breaks es-MX product direction |
| Mobile phone layout | Reference is landscape 4:3 |
| Overloaded metrics | This is sales, not KPI soup |

---

## 4. Visual hierarchy

Users should read the screen in this order:

1. PRISMA brand and module.
2. `Ventas` screen title.
3. Search and scan.
4. Categories.
5. Product grid.
6. Cart items.
7. Total.
8. `COBRAR` button.
9. Secondary actions.

If the eye does not end at `COBRAR`, the screen is failing. Bonita pero perdida, como combi nueva sin ruta.

---

## 5. Color rules

### Use blue for

- active `Ventas` nav item,
- active `Todos` category,
- focus rings,
- scan action,
- add product buttons,
- total amount,
- `COBRAR` button,
- small operational highlights.

### Do not use blue for

- every label,
- every border,
- random decoration,
- huge background areas,
- low-priority metadata.

### White rules

Use layered light surfaces:

1. soft app background,
2. frosted sidebar/cart,
3. elevated cards,
4. inner highlights,
5. shadows and soft glows.

Never use one flat white for everything. That is not premium; that is a spreadsheet wearing perfume.

---

## 6. Lighting rules

### Background lighting

Must include:

- cool light near the top center,
- very soft blue tint,
- subtle warm white glow,
- mild edge vignette,
- no harsh gradients.

### Product lighting

Each product card should have a subtle color-specific shadow:

| Product | Glow direction |
|---|---|
| Coca Cola | red |
| Sabritas | yellow |
| Lala milk | cool white |
| Ciel water | blue |
| Nescafe | brown/red |
| Bimbo bread | amber |
| Ace detergent | orange |
| Zucaritas | blue |

The glow must be subtle and below the product, not a radioactive puddle from a sci-fi tiendita.

---

## 7. Layout rules

### Sidebar

- Fixed left.
- Full height.
- Logo at top.
- Navigation vertical.
- `Ventas` selected.
- Terminal card at bottom.

### Main sales area

- Title at top.
- Search row below.
- Categories below search.
- Product grid below categories.
- Pagination below grid.

### Cart area

- Fixed right.
- Taller than main grid.
- Contains ticket lines, totals, CTA and actions.
- `COBRAR` must visually dominate.

---

## 8. Product card rules

Every product card must have:

- frosted white card,
- subtle border,
- rounded corners,
- favorite star,
- large product image,
- product shadow/glow,
- product name,
- price,
- stock,
- blue add button.

Do not use table rows for products in the main selling screen. This is a POS catalog, not Excel con tenis.

---

## 9. Cart rules

The cart should feel like a clean premium ticket.

Each line needs:

- line number,
- thumbnail,
- product name,
- unit price,
- quantity stepper,
- line total,
- remove action.

Totals must be clear:

- subtotal,
- tax,
- total.

The button `COBRAR` must be large, blue and obvious.

---

## 10. Iconography rules

- Use line icons.
- Stroke 1.75-2px.
- Keep icon sizes consistent.
- Default icons in navy/gray.
- Active icons in blue or white on blue.
- Do not use cartoon filled icons.
- Do not mix multiple icon families unless visually normalized.

Recommended: `lucide-react` or `phosphor-icons`.

---

## 11. Language rules

Use Spanish Mexican UI copy.

Correct:

- `Ventas`
- `Buscar producto por codigo, nombre o SKU...`
- `ESCANEAR`
- `Carrito de venta`
- `4 articulos`
- `Subtotal`
- `Impuestos (IVA 16%)`
- `Total`
- `COBRAR`
- `COTIZACION`
- `GUARDAR`
- `LIMPIAR`
- `Terminal 01`
- `En linea`

Incorrect:

- `Sales`
- `Checkout`
- `Cart`
- `Pay now`
- `Inventory`
- `Submit`

---

## 12. Motion rules

Allowed:

- subtle hover lift,
- blue focus ring,
- smooth transitions 160-220ms,
- small active press feedback.

Not allowed:

- bounce animations,
- confetti,
- large scale jumps,
- neon pulse loops,
- particle effects.

A POS should not celebrate every click like a slot machine that owes rent.

---

## 13. Responsive rules

Primary target: 4:3 landscape.

If adapting:

- sidebar may compact,
- cart may become drawer under smaller widths,
- grid may go 3 columns,
- product images must remain large,
- search and pay button must never disappear.

Do not break the three-zone mental model unless the viewport truly forces it.

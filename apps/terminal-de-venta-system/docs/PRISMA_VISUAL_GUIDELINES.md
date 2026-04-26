# PRISMA Visual Guidelines

**Purpose:** preserve the visual identity of PRISMA Dark POS across prompts, design work and code implementation.

---

## 1. Visual statement

PRISMA Dark POS is a premium dark point-of-sale interface for fast retail operation. It combines dark cinematic depth, glass panels, warm gold accents and large illuminated product cards.

It must look like a serious intelligent sales terminal, not like somebody downloaded a random admin template and put a sombrero on it.

---

## 2. What PRISMA is

| Trait | Meaning |
|---|---|
| Dark premium | Deep blacks, smoke, blur, depth |
| Warm gold | Main action and selected states |
| Glass panels | Translucent panels with subtle borders |
| Product-first | Big product images with pedestal glow |
| POS-first | Search, product selection, cart, total, charge |
| es-MX | Spanish Mexican operational copy |
| Spacious 4:3 | Wide composition, not cramped |
| Elegant utility | Good-looking but still practical |

---

## 3. What PRISMA is not

| Wrong direction | Why it fails |
|---|---|
| Generic SaaS dashboard | Loses POS identity |
| Green primary checkout | Breaks gold reference language |
| Cyberpunk neon | Too noisy and gamer-like |
| Flat dark cards | Loses premium depth |
| Tiny product thumbnails | Kills catalog feel |
| English labels | Breaks es-MX product direction |
| Mobile phone layout | Reference is landscape 4:3 |
| Overloaded metrics | This is sales, not executive KPI dashboard |

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

If the eye does not end at `COBRAR`, the screen is failing its job. Bonito pero inútil, como paraguas de papel.

---

## 5. Color rules

### Use gold for

- active `Ventas` nav item,
- active `Todos` category,
- focus rings,
- important borders,
- total amount,
- `COBRAR` button,
- small premium icon highlights.

### Do not use gold for

- every label,
- every border,
- random decoration,
- huge background areas,
- low-priority metadata.

### Dark rules

Use layered dark surfaces:

1. deep background,
2. glass sidebar/cart,
3. product cards,
4. inner highlights,
5. shadows and glows.

Never use one flat black for everything. That is not premium; that is the UI equivalent of turning off the lights and calling it interior design.

---

## 6. Lighting rules

### Background lighting

Must include:

- warm light near top center,
- vignette on edges,
- subtle low red/blue reflections,
- soft haze.

### Product lighting

Each product card should have a color-specific glow:

| Product | Glow direction |
|---|---|
| Coca Cola | red |
| Sabritas | yellow/gold |
| Lala milk | cool white |
| Ciel water | blue |
| Nescafé | brown/red |
| Bimbo bread | amber |
| Ace detergent | orange |
| Zucaritas | blue |

The glow must be subtle and below the product, not a giant radioactive puddle.

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

- dark glass card,
- subtle border,
- rounded corners,
- favorite star,
- large product image,
- product pedestal/glow,
- product name,
- price,
- stock.

Do not use table rows for products in the main selling screen. This is a touch POS catalog, not a spreadsheet wearing eyeliner.

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

The button `COBRAR` must be large, gold and obvious.

---

## 10. Iconography rules

- Use line icons.
- Stroke 1.75-2px.
- Keep icon sizes consistent.
- Default icons in muted gray.
- Active icons in gold.
- Do not use cartoon filled icons.
- Do not mix multiple icon families unless visually normalized.

Recommended: `lucide-react` or `phosphor-icons`.

---

## 11. Language rules

Use Spanish Mexican UI copy.

Correct:

- `Ventas`
- `Buscar producto por código, nombre o SKU...`
- `ESCANEAR`
- `Carrito de venta`
- `4 artículos`
- `Subtotal`
- `Impuestos (IVA 16%)`
- `Total`
- `COBRAR`
- `COTIZACIÓN`
- `GUARDAR`
- `LIMPIAR`
- `Terminal 01`
- `En línea`

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

- subtle hover glow,
- slight card lift,
- focus ring,
- smooth transitions 160-220ms,
- small active press feedback.

Not allowed:

- bounce animations,
- confetti,
- large scale jumps,
- neon pulse loops,
- particle effects.

A POS should not celebrate every click like a slot machine with rent problems.

---

## 13. Responsive rules

Primary target: **4:3 landscape**.

If adapting:

- sidebar may compact,
- cart may become drawer under smaller widths,
- grid may go 3 columns,
- product images must remain large,
- search and pay button must never disappear.

Do not break the three-zone mental model unless the viewport truly forces it.

---

## 14. Prompt for image/model generation

Use this when asking another model to generate or interpret the visual target:

```text
High fidelity dark premium POS interface for PRISMA, 4:3 aspect ratio, Spanish Mexican UI, left fixed sidebar with PRISMA logo and vertical navigation, active Ventas item in warm gold, central sales catalog with large search input, ESCANEAR button, circular category icons, 4-column product card grid with realistic product images on glowing pedestals, right cart panel with subtle gold border, cart line items, quantity steppers, subtotal, IVA 16%, large golden Total, large golden COBRAR button with F2 shortcut, bottom action cards COTIZACIÓN F3, GUARDAR F4, LIMPIAR F5, cinematic dark glassmorphism, warm gold accents, soft atmospheric blur, premium intelligent retail terminal.
```

Negative prompt:

```text
Do not make it a generic SaaS dashboard. Do not use green as the primary CTA. Do not use bright cyberpunk neon. Do not flatten the cards. Do not remove product images. Do not change the three-column structure. Do not use English labels. Do not make it look like a phone app.
```

---

## 15. Codex instruction block

```text
Implement the PRISMA Dark POS screen according to the Golden Visual Specs. Match the reference layout, spacing, dark glass surfaces, warm gold accents, left sidebar, central 4-column product grid, right cart panel, and Spanish labels. Prioritize visual fidelity over creative reinterpretation.
```

Hard rules for Codex:

1. Build the layout first.
2. Add tokens second.
3. Add components third.
4. Add demo data exactly.
5. Compare screenshot against `negra.jpeg`.
6. Do not invent unrelated UI.

---

## 16. Visual review checklist

- [ ] Looks like PRISMA, not a generic POS.
- [ ] Dark background has atmosphere.
- [ ] Sidebar matches reference.
- [ ] `Ventas` is active and gold.
- [ ] Search row is prominent.
- [ ] Categories are circular.
- [ ] Product grid is 4 columns.
- [ ] Product images are large.
- [ ] Product glows exist.
- [ ] Cart is fixed right.
- [ ] Total is large and gold.
- [ ] `COBRAR` dominates.
- [ ] Secondary actions show F3/F4/F5.
- [ ] Text is es-MX.
- [ ] No neon trash.

---

## 17. Final rule

When in doubt, compare against `negra.jpeg`.

If it looks nice but not similar, it fails.

This is a governed visual replication, not a creativity buffet.

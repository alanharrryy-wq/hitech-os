# UI Visual System Map — PySide6 Glass Workbench

## 1. Visual Stack (Top → Bottom)

### 🧠 Window Layer
- Frameless / custom window chrome
- Rounded corners
- Subtle outer glow
- Dark translucent base

---

### 🌌 Background Layer
- Deep blue gradient (navy → midnight blue)
- Noise / starfield texture overlay
- Slight vignette
- Opacity stacking causing “blue wash”

---

### 🧊 Glass Panels (Primary Containers)
- Multiple nested QFrames / QWidget containers
- Each has:
  - Semi-transparent background (rgba blue-ish)
  - Border (1px light blue / cyan)
  - Border-radius (rounded corners)
  - Inner shadow / glow
- These stack → amplify blue tone

---

### 📦 Nested Containers (Problem Area)
Structure detected:
- Main Panel
  - Workspace Container
    - Inner Panel
      - Content Frame
        - Button Rows
          - Button Containers

👉 Result:
- Excess padding
- Multiple borders visible
- “Box inside box inside box” effect

---

### 🔘 Buttons
- Rounded pill style
- Semi-transparent background
- Light blue borders
- Hover glow (soft cyan)
- Icons are low contrast (grayish)

---

### 🧩 Tabs
- Floating pill tabs
- Active tab slightly brighter
- Background blur + border

---

### ✨ Effects Used
- QGraphicsBlurEffect (background feel)
- Opacity layering
- Border glow simulation via color
- Gradient stacking

---

## 🎨 Color Sources (Why everything looks blue)

| Element | Color Source |
|--------|-------------|
| Background | Gradient (dark blue tones) |
| Panels | RGBA blue transparency |
| Borders | Cyan / blue |
| Glow | Blue light |
| Text reflections | Slight blue tint |

👉 TODOS los layers empujan azul → acumulación brutal.

---

## 📐 Spacing & Layout Issues

- Padding duplicado en cada container
- Margins internos innecesarios
- Layouts anidados sin propósito
- Workspace no usa full stretch

---

## 🧠 Root Cause Summary

The UI is not one design…
It’s like 6 diseños apilados peleándose por atención 😅


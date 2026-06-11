# Library Use

Use available libraries where they actually help. Do not invent primitives if the repo already has a good library.

| Name | Detected | Role | Use | Restriction |
|---|---|---|---|---|
| @radix-ui/react-dialog | ^1.1.15 | dialog primitive | Use for modal/dialog interactions | Do not reimplement dialogs with raw div overlays |
| @radix-ui/react-dropdown-menu | ^2.1.16 | menu primitive | Use for menus/dropdowns | Do not create local ungoverned dropdowns |
| @radix-ui/react-scroll-area | ^1.2.10 | scroll primitive | Use for governed scroll areas | Do not hide content/background with custom scroll shells |
| @radix-ui/react-select | ^2.2.6 | select primitive | Use for accessible selects | Do not use custom select clones |
| @radix-ui/react-tabs | ^1.1.13 | tabs primitive | Use for tabs/navigation panels | No local tab state hacks if Radix fits |
| @radix-ui/react-tooltip | ^1.2.8 | tooltip primitive | Use for tooltips | Avoid hover-only inaccessible hints |
| @radix-ui/react-slot | ^1.2.4 | composition primitive | Use for asChild composition | Keep styling via tokens/adapters |
| ogl | ^1.0.11 | effects library | Use for atmospheric/background/visual lab effects | Not for buttons/cards/layout |
| ajv | not detected in root package | schema validator | Use for registries/schemas | Must support 2020-12 for current schemas |
| @playwright/test | not detected in root package | visual QA | Use for evidence/screenshots when available | Not a substitute for design approval |

## Library policy

- Radix handles accessible primitives and interaction shells.
- OGL is limited to atmosphere/background/effects/lab.
- Ajv validates VisualCat registries and schemas.
- Playwright captures evidence, not subjective approval.
- Storybook-style isolation is a future destination, not required in this audit.

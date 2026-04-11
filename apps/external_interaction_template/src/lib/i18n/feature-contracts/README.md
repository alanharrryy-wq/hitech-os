# Feature i18n contracts

Cada feature nueva debe declarar un archivo aquí para dejar explícito:

- namespace propietario
- si el copy es frontend-owned
- cómo se trata el schema dinámico
- qué enum maps reutiliza
- qué keys mínimas debe tener la feature

Ejemplo sugerido:

```ts
import { defineFeatureI18nContract } from "@/lib/i18n/feature-contracts";

export const paymentsI18nContract = defineFeatureI18nContract({
  namespace: "payments",
  ownsFrontendCopy: true,
  dynamicContentMode: "source-language",
  enumMaps: ["recordState", "syncStatus"],
  requiredKeys: [
    "payments.page.title",
    "payments.empty.title",
    "payments.filters.all"
  ]
});
```

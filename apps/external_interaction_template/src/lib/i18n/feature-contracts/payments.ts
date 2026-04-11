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

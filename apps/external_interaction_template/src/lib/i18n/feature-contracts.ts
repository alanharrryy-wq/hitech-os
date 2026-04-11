export type DynamicContentMode = "frontend-owned" | "source-language" | "bilingual-data";

export interface FeatureI18nContract {
  namespace: string;
  ownsFrontendCopy: boolean;
  dynamicContentMode: DynamicContentMode;
  enumMaps: string[];
  requiredKeys: string[];
}

export function defineFeatureI18nContract(contract: FeatureI18nContract): FeatureI18nContract {
  return contract;
}

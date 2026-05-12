export type PrismaChartVisualRecipe = {
  family: string;
  tokens: string[];
  defaults: Record<string, string | number | boolean>;
  surfaceOverrides: Record<string, Record<string, string | number | boolean>>;
  states: string[];
  tooltip: "compact" | "standard" | "rich";
  motion: "none" | "safe" | "subtle";
};


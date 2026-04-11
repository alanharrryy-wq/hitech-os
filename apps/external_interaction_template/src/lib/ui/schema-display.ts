import type { FlowAccessMode, RecordTypeSchema, SchemaCategory } from "@/lib/core/types";

type Translator = (key: string, values?: Record<string, string | number>) => string;

function isMissingTranslation(value: string, key: string): boolean {
  return value === key || value === `[[missing:${key}]]`;
}

function translateWithFallback(t: Translator, key: string, fallback: string): string {
  const translated = t(key);
  return isMissingTranslation(translated, key) ? fallback : translated;
}

export interface LocalizedSchemaDisplay {
  title: string;
  summary: string;
  category: string;
  accessMode: string;
  tags: string[];
}

export function localizeSchemaTitle(schema: Pick<RecordTypeSchema, "id" | "title">, t: Translator): string {
  return translateWithFallback(t, `schema.${schema.id}.title`, schema.title);
}

export function localizeSchemaSummary(schema: Pick<RecordTypeSchema, "id" | "summary">, t: Translator): string {
  return translateWithFallback(t, `schema.${schema.id}.summary`, schema.summary);
}

export function localizeSchemaCategory(category: SchemaCategory | string, t: Translator): string {
  return translateWithFallback(t, `schema.category.${category}`, category);
}

export function localizeSchemaAccessMode(accessMode: FlowAccessMode | string, t: Translator): string {
  return translateWithFallback(t, `schema.accessMode.${accessMode}`, accessMode);
}

export function localizeSchemaTag(tag: string, t: Translator): string {
  return translateWithFallback(t, `schema.tag.${tag}`, tag);
}

export function localizeSchemaActionLabel(
  schemaId: string,
  actionId: string,
  fallbackLabel: string,
  t: Translator
): string {
  return translateWithFallback(t, `schema.${schemaId}.action.${actionId}.label`, fallbackLabel);
}

export function localizeSchemaSectionTitle(
  schemaId: string,
  sectionId: string,
  fallbackTitle: string,
  t: Translator
): string {
  return translateWithFallback(t, `schema.${schemaId}.section.${sectionId}.title`, fallbackTitle);
}

export function localizeSchemaDisplay(schema: RecordTypeSchema, t: Translator): LocalizedSchemaDisplay {
  return {
    title: localizeSchemaTitle(schema, t),
    summary: localizeSchemaSummary(schema, t),
    category: localizeSchemaCategory(schema.category, t),
    accessMode: localizeSchemaAccessMode(schema.flow.accessMode, t),
    tags: schema.tags.map((tag) => localizeSchemaTag(tag, t))
  };
}

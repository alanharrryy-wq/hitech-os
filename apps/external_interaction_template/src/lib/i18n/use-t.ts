"use client";

import { useLanguage } from "@/lib/i18n/use-language";

export function useT() {
  return useLanguage().t;
}
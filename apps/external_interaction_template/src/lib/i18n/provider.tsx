"use client";

import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from "react";

import { DEFAULT_LOCALE, LOCALE_STORAGE_KEY, SUPPORTED_LOCALES, isLocale } from "@/lib/i18n/config";
import { translate } from "@/lib/i18n/dictionary";
import type { Locale } from "@/lib/i18n/types";

export interface LanguageContextValue {
  locale: Locale;
  setLocale: (nextLocale: Locale) => void;
  supportedLocales: readonly Locale[];
  t: (key: string, values?: Record<string, string | number>) => string;
}

export const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(DEFAULT_LOCALE);

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(LOCALE_STORAGE_KEY);
      if (isLocale(stored)) {
        setLocaleState(stored);
      }
    } catch {
      // noop
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = locale;
    try {
      window.localStorage.setItem(LOCALE_STORAGE_KEY, locale);
    } catch {
      // noop
    }
  }, [locale]);

  const setLocale = useCallback((nextLocale: Locale) => {
    setLocaleState(nextLocale);
  }, []);

  const t = useCallback((key: string, values?: Record<string, string | number>) => translate(locale, key, values), [locale]);

  const value = useMemo<LanguageContextValue>(
    () => ({ locale, setLocale, supportedLocales: SUPPORTED_LOCALES, t }),
    [locale, setLocale, t]
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

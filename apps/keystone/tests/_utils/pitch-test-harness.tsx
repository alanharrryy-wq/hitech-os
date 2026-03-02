import type { ReactElement, ReactNode } from "react";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { PITCH_ROUTES } from "@hitech/contracts";
import type { SearchParamsLike } from "@hitech/ui-kit";
import { expect, vi } from "vitest";
import PitchDoubleEnginePage from "../../app/pitch/01-double-engine/page";
import PitchIndustrialFlowPage from "../../app/pitch/02-industrial-flow/page";
import PitchHiTechOsPage from "../../app/pitch/03-hitech-os/page";
import PitchValuationPage from "../../app/pitch/04-valuation/page";
import PitchIndexPage from "../../app/pitch/page";

const navigationMockState = vi.hoisted(() => ({
  pathname: "/pitch",
  search: "",
  replaceCalls: [] as Array<{ href: string; options?: { scroll?: boolean } }>
}));

vi.mock("next/navigation", () => {
  return {
    useRouter: () => ({
      replace: (href: string, options?: { scroll?: boolean }) => {
        navigationMockState.replaceCalls.push(options ? { href, options } : { href });
      }
    }),
    usePathname: () => navigationMockState.pathname,
    useSearchParams: () => new URLSearchParams(navigationMockState.search)
  };
});

vi.mock("next/link", () => {
  return {
    default: ({
      href,
      children,
      ...rest
    }: {
      href: string | { readonly pathname?: string; toString(): string };
      children?: ReactNode;
      readonly [key: string]: unknown;
    }) => {
      const normalizedHref =
        typeof href === "string" ? href : (href.pathname ?? href.toString());
      return React.createElement("a", { href: normalizedHref, ...rest }, children);
    }
  };
});

export const PITCH_CANONICAL_ROUTES = [
  "/pitch",
  PITCH_ROUTES["01-double-engine"],
  PITCH_ROUTES["02-industrial-flow"],
  PITCH_ROUTES["03-hitech-os"],
  PITCH_ROUTES["04-valuation"]
] as const;

export type PitchCanonicalRoute = (typeof PITCH_CANONICAL_ROUTES)[number];

const ROUTE_RENDERERS: Record<
  PitchCanonicalRoute,
  (searchParams: SearchParamsLike) => ReactElement
> = {
  "/pitch": (searchParams) => PitchIndexPage({ searchParams }),
  "/pitch/01-double-engine": (searchParams) => PitchDoubleEnginePage({ searchParams }),
  "/pitch/02-industrial-flow": (searchParams) => PitchIndustrialFlowPage({ searchParams }),
  "/pitch/03-hitech-os": (searchParams) => PitchHiTechOsPage({ searchParams }),
  "/pitch/04-valuation": (searchParams) => PitchValuationPage({ searchParams })
};

export function resetNavigationMockState(): void {
  navigationMockState.pathname = "/pitch";
  navigationMockState.search = "";
  navigationMockState.replaceCalls.length = 0;
}

export function setNavigationMockState(pathname: string, query = ""): void {
  navigationMockState.pathname = pathname;
  navigationMockState.search = query;
  navigationMockState.replaceCalls.length = 0;
}

export function getNavigationReplaceCalls(): readonly { href: string; options?: { scroll?: boolean } }[] {
  return [...navigationMockState.replaceCalls];
}

function normalizeQueryString(raw: string): string {
  if (raw.length === 0) {
    return "";
  }

  if (raw.startsWith("?")) {
    return raw.slice(1);
  }

  return raw;
}

export function toSearchParamsLike(
  input: string | URLSearchParams | SearchParamsLike | undefined
): SearchParamsLike {
  if (!input) {
    return {};
  }

  if (typeof input === "string") {
    const params = new URLSearchParams(normalizeQueryString(input));
    return toSearchParamsLike(params);
  }

  if (input instanceof URLSearchParams) {
    const grouped = new Map<string, string[]>();
    input.forEach((value, key) => {
      const current = grouped.get(key) ?? [];
      grouped.set(key, [...current, value]);
    });

    const record: SearchParamsLike = {};
    for (const [key, values] of grouped.entries()) {
      if (values.length === 1) {
        record[key] = values[0];
      } else if (values.length > 1) {
        record[key] = values;
      }
    }
    return record;
  }

  const copy: SearchParamsLike = {};
  for (const [key, value] of Object.entries(input)) {
    if (Array.isArray(value)) {
      copy[key] = [...value];
      continue;
    }
    copy[key] = value;
  }
  return copy;
}

export function renderPitchRoute(
  route: PitchCanonicalRoute,
  input?: string | URLSearchParams | SearchParamsLike
): string {
  const query = input ? toSearchParamsLike(input) : {};
  const queryString = new URLSearchParams(
    Object.entries(query).flatMap(([key, value]) => {
      if (value === undefined) {
        return [];
      }
      if (Array.isArray(value)) {
        return value.map((entry) => [key, entry]);
      }
      return [[key, value]];
    })
  ).toString();

  setNavigationMockState(route, queryString);
  const element = ROUTE_RENDERERS[route](query);
  return renderToStaticMarkup(element);
}

export function renderElement(element: ReactElement): string {
  return renderToStaticMarkup(element);
}

export function normalizeHtml(html: string): string {
  return html.replace(/\s+/g, " ").trim();
}

export function countInHtml(html: string, needle: string): number {
  let from = 0;
  let count = 0;
  while (from < html.length) {
    const index = html.indexOf(needle, from);
    if (index < 0) {
      break;
    }
    count += 1;
    from = index + needle.length;
  }
  return count;
}

export function ensureContainsAll(html: string, required: readonly string[]): void {
  for (const item of required) {
    expect(html).toContain(item);
  }
}

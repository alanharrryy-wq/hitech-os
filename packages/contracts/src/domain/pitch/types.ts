import type {
  PitchDeck,
  PitchDeckResponse,
  PitchNavigation,
  PitchNavigationLink,
  PitchScreen,
  PitchScreen01,
  PitchScreen02,
  PitchScreen03,
  PitchScreen04,
  PitchScreenMap
} from "./schemas.js";

export type PitchDeckModel = PitchDeck;
export type PitchDeckResponseModel = PitchDeckResponse;
export type PitchNavigationModel = PitchNavigation;
export type PitchNavigationLinkModel = PitchNavigationLink;
export type PitchScreenModel = PitchScreen;
export type PitchScreen01Model = PitchScreen01;
export type PitchScreen02Model = PitchScreen02;
export type PitchScreen03Model = PitchScreen03;
export type PitchScreen04Model = PitchScreen04;
export type PitchScreenMapModel = PitchScreenMap;

export interface PitchTextFragment {
  readonly id: string;
  readonly text: string;
  readonly scope:
    | "title"
    | "heading"
    | "bullet"
    | "microcopy"
    | "strong-line"
    | "kpi"
    | "phase"
    | "table-header"
    | "table-cell";
  readonly screenSlug: string;
}

export interface PitchScreenSummary {
  readonly slug: string;
  readonly route: string;
  readonly order: number;
  readonly title: string;
  readonly fragmentCount: number;
}

export interface PitchDeckSummary {
  readonly deckId: string;
  readonly version: string;
  readonly locale: string;
  readonly screenCount: number;
  readonly bulletLikeCount: number;
  readonly totalTextFragments: number;
}

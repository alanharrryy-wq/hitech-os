import type { PitchNavigationLink, PitchScreenSlug } from "@hitech/contracts";

export interface PitchHeroMetric {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly tone?: "gold" | "teal" | "cyan" | "neutral";
}

export interface PitchHeroModel {
  readonly kicker: string;
  readonly title: string;
  readonly subtitle: string;
  readonly deckIdentity: {
    readonly label: string;
    readonly value: string;
  };
  readonly metrics: readonly PitchHeroMetric[];
}

export interface PitchShellNavModel {
  readonly links: readonly PitchNavigationLink[];
  readonly activeSlug?: PitchScreenSlug;
}

export interface PitchDeckProgressModel {
  readonly current: number;
  readonly total: number;
  readonly label: string;
  readonly previousHref?: string;
  readonly nextHref?: string;
}

export interface PitchShellFrameModel {
  readonly hero: PitchHeroModel;
  readonly nav: PitchShellNavModel;
  readonly progress: PitchDeckProgressModel;
  readonly breadcrumbs: ReadonlyArray<{
    readonly label: string;
    readonly href?: string;
  }>;
}

export interface PitchShellProps {
  readonly model: PitchShellFrameModel;
  readonly children: React.ReactNode;
  readonly className?: string;
  readonly showScrollAffordance?: boolean;
  readonly enableKeyboardNav?: boolean;
}

export interface PitchSectionMeta {
  readonly id: string;
  readonly label: string;
  readonly description?: string;
}

export interface PitchSectionContextValue {
  readonly activeSectionId: string | null;
  readonly setActiveSectionId: (value: string | null) => void;
}

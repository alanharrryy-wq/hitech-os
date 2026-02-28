import {
  PITCH_DECK_FIXTURE,
  PITCH_ROUTES,
  PITCH_SCREEN_FIXTURES,
  PITCH_SCREEN_ORDER,
  type PitchDeck,
  type PitchScreen,
  type PitchScreenSlug
} from "@hitech/contracts";

export function getPitchDeckFixture(): PitchDeck {
  return PITCH_DECK_FIXTURE;
}

export function getPitchScreenFixture(slug: PitchScreenSlug): PitchScreen {
  return PITCH_SCREEN_FIXTURES[slug];
}

export function getPitchScreenByRoute(route: string): PitchScreen | null {
  const slug = PITCH_SCREEN_ORDER.find((candidate) => PITCH_ROUTES[candidate] === route);
  if (!slug) {
    return null;
  }

  return PITCH_SCREEN_FIXTURES[slug];
}

export function getPitchNavLinks() {
  return PITCH_DECK_FIXTURE.navigation.links;
}

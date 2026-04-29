import { TABLET_NAV_ITEMS } from "@components/tablet-shell/tablet-nav";

export function getNavigation() {
  return TABLET_NAV_ITEMS.filter((item) => item.href !== "/").map((item) => ({
    href: item.href,
    title: item.label,
    description: item.description
  }));
}

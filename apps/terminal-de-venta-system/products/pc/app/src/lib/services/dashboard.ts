import {
  actionCards,
  alertStrip,
  categoryMix,
  lowStock,
  openOrders,
  pendingSync,
  signalPills,
  summaryCards
} from "@/lib/data/demo";
import { pcMessages } from "@/lib/i18n/messages/es";

export function getPcDashboard() {
  return {
    hero: {
      title: pcMessages.home.title,
      subtitle: pcMessages.home.subtitle,
      pills: signalPills
    },
    summaryCards,
    categoryMix,
    lowStock,
    openOrders,
    pendingSync,
    actionCards,
    alertStrip
  };
}

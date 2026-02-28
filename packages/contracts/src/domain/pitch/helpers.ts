import {
  MONTHS_PER_YEAR,
  PITCH_INDUSTRIAL_FLOW_ANNUAL_PROFIT_USD,
  PITCH_INDUSTRIAL_FLOW_MONTHLY_BILLING_USD,
  PITCH_INDUSTRIAL_FLOW_MONTHLY_MODULES,
  PITCH_INDUSTRIAL_FLOW_MONTHLY_PROFIT_USD,
  PITCH_INDUSTRIAL_FLOW_TOTAL_MODULES
} from "./constants.js";
import type {
  PitchCycleWidgetPoint,
  PitchIndustrialFlowKpis,
  PitchKpiWidget,
  PitchValuationRange
} from "./types.js";

const USD_COMPACT_FORMATTER = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  notation: "compact",
  maximumFractionDigits: 2
});

const USD_INTEGER_FORMATTER = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0
});

const NUMBER_FORMATTER = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 0
});

export function annualizeMonthlyValue(monthlyUsd: number): number {
  return monthlyUsd * MONTHS_PER_YEAR;
}

export function computeMonthlyMarginPercent(monthlyProfitUsd: number, monthlyBillingUsd: number): number {
  if (monthlyBillingUsd === 0) {
    return 0;
  }
  return (monthlyProfitUsd / monthlyBillingUsd) * 100;
}

export function normalizePitchText(text: string): string {
  return text.trim().replace(/\s+/g, " ");
}

export function computeMonthsToCoverModules(totalModules: number, monthlyModules: number): number {
  if (totalModules <= 0 || monthlyModules <= 0) {
    return 0;
  }
  return Math.ceil(totalModules / monthlyModules);
}

export function buildIndustrialKpis(input?: {
  totalModules?: number;
  monthlyModules?: number;
  monthlyBillingUsd?: number;
  monthlyProfitUsd?: number;
  annualProfitUsd?: number;
}): PitchIndustrialFlowKpis {
  const totalModules = input?.totalModules ?? PITCH_INDUSTRIAL_FLOW_TOTAL_MODULES;
  const monthlyModules = input?.monthlyModules ?? PITCH_INDUSTRIAL_FLOW_MONTHLY_MODULES;
  const monthlyBillingUsd = input?.monthlyBillingUsd ?? PITCH_INDUSTRIAL_FLOW_MONTHLY_BILLING_USD;
  const monthlyProfitUsd = input?.monthlyProfitUsd ?? PITCH_INDUSTRIAL_FLOW_MONTHLY_PROFIT_USD;
  const annualProfitUsd = input?.annualProfitUsd ?? annualizeMonthlyValue(monthlyProfitUsd);

  return {
    totalModules,
    monthlyModules,
    monthlyBillingUsd,
    monthlyProfitUsd,
    annualProfitUsd,
    annualProfitCompactText: formatCurrencyCompact(annualProfitUsd)
  };
}

export function buildKpiWidgets(kpis: PitchIndustrialFlowKpis): readonly PitchKpiWidget[] {
  return [
    {
      id: "totalModules",
      label: "Módulos totales",
      value: formatInteger(kpis.totalModules),
      numericValue: kpis.totalModules
    },
    {
      id: "monthlyModules",
      label: "Módulos mensuales",
      value: formatInteger(kpis.monthlyModules),
      numericValue: kpis.monthlyModules
    },
    {
      id: "monthlyBillingUsd",
      label: "Facturación mensual",
      value: formatCurrencyInteger(kpis.monthlyBillingUsd),
      numericValue: kpis.monthlyBillingUsd
    },
    {
      id: "monthlyProfitUsd",
      label: "Utilidad mensual",
      value: formatCurrencyInteger(kpis.monthlyProfitUsd),
      numericValue: kpis.monthlyProfitUsd
    },
    {
      id: "annualProfitUsd",
      label: "Utilidad anual",
      value: formatCurrencyCompact(kpis.annualProfitUsd),
      numericValue: kpis.annualProfitUsd
    }
  ] as const;
}

export function buildCycleWidgetPoints(input: {
  totalModules: number;
  monthlyModules: number;
  monthsToProject: number;
}): readonly PitchCycleWidgetPoint[] {
  const totalModules = Math.max(0, Math.floor(input.totalModules));
  const monthlyModules = Math.max(0, Math.floor(input.monthlyModules));
  const monthsToProject = Math.max(0, Math.floor(input.monthsToProject));

  if (totalModules === 0 || monthlyModules === 0 || monthsToProject === 0) {
    return [];
  }

  const cycleMonths = computeMonthsToCoverModules(totalModules, monthlyModules);
  const points: PitchCycleWidgetPoint[] = [];
  let servicedInCycle = 0;

  for (let monthIndex = 1; monthIndex <= monthsToProject; monthIndex += 1) {
    if (servicedInCycle >= totalModules) {
      servicedInCycle = 0;
    }

    const remainingBefore = totalModules - servicedInCycle;
    const modulesServicedThisMonth = Math.min(monthlyModules, remainingBefore);
    const servicedModulesInCycle = servicedInCycle + modulesServicedThisMonth;
    const remainingModulesInCycle = totalModules - servicedModulesInCycle;

    points.push({
      monthIndex,
      monthInCycle: ((monthIndex - 1) % cycleMonths) + 1,
      cycleNumber: Math.floor((monthIndex - 1) / cycleMonths) + 1,
      modulesServicedThisMonth,
      servicedModulesInCycle,
      remainingModulesInCycle,
      cycleCompleted: remainingModulesInCycle === 0
    });

    servicedInCycle = servicedModulesInCycle;
  }

  return points;
}

export function estimateValuationRangeFromAnnualProfit(
  annualProfitUsd: number,
  multipleLow = 2,
  multipleHigh = 3
): PitchValuationRange {
  return {
    low: annualProfitUsd * multipleLow,
    high: annualProfitUsd * multipleHigh,
    multipleLow,
    multipleHigh
  };
}

export function defaultIndustrialValuationRange(): PitchValuationRange {
  return estimateValuationRangeFromAnnualProfit(PITCH_INDUSTRIAL_FLOW_ANNUAL_PROFIT_USD, 2, 3);
}

export function formatCurrencyInteger(value: number): string {
  return USD_INTEGER_FORMATTER.format(value);
}

export function formatCurrencyCompact(value: number): string {
  return USD_COMPACT_FORMATTER.format(value);
}

export function formatInteger(value: number): string {
  return NUMBER_FORMATTER.format(value);
}

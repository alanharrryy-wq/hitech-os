"use client"

import * as Tabs from "@radix-ui/react-tabs"
import { motion } from "motion/react"
import { BarChart3, Blocks, Cpu, Factory, Sparkles } from "lucide-react"
import { ReactNode } from "react"

type PitchTabValue =
  | "overview"
  | "double-engine"
  | "industrial-flow"
  | "hitech-os"
  | "valuation"

type PitchTabItem = {
  value: PitchTabValue
  label: string
  icon: ReactNode
  hint?: string
}

const TAB_ITEMS: PitchTabItem[] = [
  {
    value: "overview",
    label: "Overview",
    icon: <Sparkles className="h-4 w-4" />,
    hint: "Vista general",
  },
  {
    value: "double-engine",
    label: "Double Engine",
    icon: <Cpu className="h-4 w-4" />,
    hint: "Arquitectura",
  },
  {
    value: "industrial-flow",
    label: "Industrial Flow",
    icon: <Factory className="h-4 w-4" />,
    hint: "Operación",
  },
  {
    value: "hitech-os",
    label: "Hitech OS",
    icon: <Blocks className="h-4 w-4" />,
    hint: "Sistema",
  },
  {
    value: "valuation",
    label: "Valuation",
    icon: <BarChart3 className="h-4 w-4" />,
    hint: "Valor",
  },
]

type PitchTabsProps = {
  value: PitchTabValue
  onValueChange: (value: PitchTabValue) => void
  className?: string
}

function cx(...parts: Array<string | undefined | false | null>) {
  return parts.filter(Boolean).join(" ")
}

export function PitchTabs({
  value,
  onValueChange,
  className,
}: PitchTabsProps) {
  return (
    <Tabs.Root
      value={value}
      onValueChange={(next) => onValueChange(next as PitchTabValue)}
      className={cx("w-full", className)}
    >
      <Tabs.List
        className={cx(
          "grid w-full grid-cols-2 gap-2 rounded-2xl border border-white/10",
          "bg-white/5 p-2 backdrop-blur-xl",
          "md:grid-cols-5"
        )}
        aria-label="Pitch sections"
      >
        {TAB_ITEMS.map((tab) => {
          const isActive = value === tab.value

          return (
            <Tabs.Trigger
              key={tab.value}
              value={tab.value}
              className={cx(
                "group relative overflow-hidden rounded-xl outline-none",
                "focus-visible:ring-2 focus-visible:ring-cyan-300/60",
                "data-[state=active]:text-white data-[state=inactive]:text-white/70"
              )}
            >
              <motion.div
                layout
                whileHover={{ y: -1 }}
                whileTap={{ scale: 0.985 }}
                className={cx(
                  "relative flex min-h-[68px] w-full flex-col items-start justify-center gap-1 px-4 py-3",
                  "border border-transparent transition-all duration-200",
                  isActive
                    ? "bg-cyan-400/12 shadow-[0_0_0_1px_rgba(103,232,249,0.22),0_8px_24px_rgba(34,211,238,0.10)]"
                    : "bg-transparent hover:bg-white/6"
                )}
              >
                {isActive ? (
                  <motion.div
                    layoutId="pitch-tab-active-pill"
                    className="absolute inset-0 rounded-xl border border-cyan-300/20 bg-gradient-to-br from-cyan-300/10 via-white/5 to-transparent"
                    transition={{ type: "spring", stiffness: 320, damping: 28 }}
                  />
                ) : null}

                <div className="relative z-10 flex items-center gap-2">
                  <span className={cx(isActive ? "text-cyan-200" : "text-white/60")}>
                    {tab.icon}
                  </span>
                  <span className="text-sm font-semibold tracking-[0.01em]">
                    {tab.label}
                  </span>
                </div>

                {tab.hint ? (
                  <span className="relative z-10 text-xs text-white/45">
                    {tab.hint}
                  </span>
                ) : null}
              </motion.div>
            </Tabs.Trigger>
          )
        })}
      </Tabs.List>
    </Tabs.Root>
  )
}

export type { PitchTabValue }

"use client"

import { useMemo, useState } from "react"
import { PitchTabs, type PitchTabValue } from "./PitchTabs"

function cx(...parts: Array<string | undefined | false | null>) {
  return parts.filter(Boolean).join(" ")
}

const CONTENT: Record<
  PitchTabValue,
  {
    eyebrow: string
    title: string
    body: string
  }
> = {
  overview: {
    eyebrow: "SYSTEM OVERVIEW",
    title: "Gobernable por diseño",
    body:
      "La capa pitch deja de ser presentación estática y se vuelve sistema navegable, coherente y trazable. Cada vista tiene intención, no relleno.",
  },
  "double-engine": {
    eyebrow: "DOUBLE ENGINE",
    title: "Narrativa + runtime",
    body:
      "La historia visual y el motor operativo coexisten sin mezclarse feo. El resultado es una experiencia premium que no se cae al primer cambio.",
  },
  "industrial-flow": {
    eyebrow: "INDUSTRIAL FLOW",
    title: "Operación visible",
    body:
      "El flujo se entiende como sistema. No son pantallas sueltas: es un recorrido con estados, lectura y control.",
  },
  "hitech-os": {
    eyebrow: "HITECH OS",
    title: "Capa de sistema",
    body:
      "Las escenas, tooling y runtime forman una base que se puede extender sin hacer Frankenstein. El diseño responde a arquitectura real.",
  },
  valuation: {
    eyebrow: "VALUATION",
    title: "La forma también comunica valor",
    body:
      "Cuando la interfaz transmite orden, control y trazabilidad, el producto deja de verse como prototipo y empieza a verse como activo serio.",
  },
}

export function PitchTabsDemo({ className }: { className?: string }) {
  const [value, setValue] = useState<PitchTabValue>("overview")

  const current = useMemo(() => CONTENT[value], [value])

  return (
    <section
      className={cx(
        "rounded-[28px] border border-white/10 bg-white/5 p-4 backdrop-blur-xl",
        "shadow-[0_20px_80px_rgba(0,0,0,0.22)] md:p-6",
        className
      )}
    >
      <div className="mb-5">
        <PitchTabs value={value} onValueChange={setValue} />
      </div>

      <div className="rounded-2xl border border-white/10 bg-black/20 px-5 py-6">
        <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.22em] text-cyan-200/80">
          {current.eyebrow}
        </p>
        <h3 className="mb-3 text-2xl font-semibold tracking-tight text-white">
          {current.title}
        </h3>
        <p className="max-w-3xl text-sm leading-7 text-white/70">
          {current.body}
        </p>
      </div>
    </section>
  )
}

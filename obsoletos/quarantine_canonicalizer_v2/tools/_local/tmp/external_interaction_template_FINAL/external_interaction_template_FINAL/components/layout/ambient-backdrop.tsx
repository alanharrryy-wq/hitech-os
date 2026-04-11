"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { ComponentType } from "react";

export function AmbientBackdrop() {
  const MotionDiv = motion.div as unknown as ComponentType<any>;
  const reduceMotion = useReducedMotion();

  const animate = reduceMotion ? undefined : { x: [0, 18, -10, 0], y: [0, 16, 8, 0] };

  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(113,168,255,0.14),transparent_26%),radial-gradient(circle_at_76%_12%,rgba(255,255,255,0.07),transparent_22%),linear-gradient(180deg,rgba(17,21,33,0.88),rgba(8,11,19,1))]" />
      <MotionDiv
        className="absolute -left-28 top-[-10rem] h-[34rem] w-[34rem] rounded-full bg-[radial-gradient(circle,rgba(113,168,255,0.16)_0%,rgba(113,168,255,0.02)_62%,transparent_100%)] blur-3xl"
        animate={animate}
        transition={{ duration: 24, repeat: Infinity, ease: "easeInOut" }}
      />
      <MotionDiv
        className="absolute right-[-12rem] top-[22%] h-[28rem] w-[28rem] rounded-full bg-[radial-gradient(circle,rgba(255,255,255,0.09)_0%,rgba(255,255,255,0.02)_58%,transparent_100%)] blur-3xl"
        animate={reduceMotion ? undefined : { x: [0, -20, 10, 0], y: [0, -14, 12, 0] }}
        transition={{ duration: 30, repeat: Infinity, ease: "easeInOut" }}
      />
      <div className="absolute inset-0 bg-[linear-gradient(180deg,transparent_0%,rgba(8,11,19,0.16)_40%,rgba(8,11,19,0.42)_100%)]" />
    </div>
  );
}

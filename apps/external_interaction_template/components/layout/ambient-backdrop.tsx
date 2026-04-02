"use client";

import { motion } from "framer-motion";
import type { ComponentType } from "react";

export function AmbientBackdrop() {
  const MotionDiv = motion.div as unknown as ComponentType<any>;
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,#162234_0%,#090e16_52%,#060a10_100%)]" />
      <MotionDiv
        className="absolute -left-20 top-[-8rem] h-[26rem] w-[26rem] rounded-full bg-[radial-gradient(circle,#9bdfff44_0%,#9bdfff05_65%,transparent_100%)] blur-2xl"
        animate={{ x: [0, 36, -12, 0], y: [0, 30, 14, 0] }}
        transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
      />
      <MotionDiv
        className="absolute right-[-8rem] top-[28%] h-[22rem] w-[22rem] rounded-full bg-[radial-gradient(circle,#f3f8ff2e_0%,#f3f8ff05_62%,transparent_100%)] blur-2xl"
        animate={{ x: [0, -42, 10, 0], y: [0, -22, 16, 0] }}
        transition={{ duration: 28, repeat: Infinity, ease: "easeInOut" }}
      />
      <MotionDiv
        className="absolute bottom-[-12rem] left-[24%] h-[24rem] w-[24rem] rounded-full bg-[radial-gradient(circle,#74dfff29_0%,#74dfff03_70%,transparent_100%)] blur-2xl"
        animate={{ x: [0, 24, -30, 0], y: [0, -14, 24, 0] }}
        transition={{ duration: 30, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
}

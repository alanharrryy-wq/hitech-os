import os from "node:os"
import { DEFAULT_PERFORMANCE_PROFILE, PERFORMANCE_PROFILES } from "./constants.mjs"

function resolveRequestedProfile(flags = {}) {
  if (flags.smoke === true || flags.mode === "smoke") {
    return PERFORMANCE_PROFILES.smoke
  }

  if (flags.lite === true || flags.profile === "lite") {
    return PERFORMANCE_PROFILES.lite
  }

  if (flags.full === true || flags.profile === "full" || flags.mode === "full") {
    return PERFORMANCE_PROFILES.full
  }

  return DEFAULT_PERFORMANCE_PROFILE
}

function shouldDegradeForResources(requestedProfile) {
  const totalMemoryGb = os.totalmem() / (1024 * 1024 * 1024)
  const cpuCount = os.cpus()?.length ?? 1

  const lowMemory = totalMemoryGb < 8
  const lowCpu = cpuCount < 4

  if (requestedProfile.name === "full" && (lowMemory || lowCpu)) {
    return {
      degrade: true,
      reason: `Resource guard: totalMemoryGb=${totalMemoryGb.toFixed(2)} cpuCount=${cpuCount}`
    }
  }

  return {
    degrade: false,
    reason: "No degradation needed"
  }
}

export function resolvePerformanceProfile(flags = {}, options = {}) {
  const requested = resolveRequestedProfile(flags)
  const forcedLite = options.forceLite === true || process.env.PITCH_ENGINE_FORCE_LITE === "1"

  if (forcedLite && requested.name !== "lite") {
    return {
      requested: requested.name,
      actual: PERFORMANCE_PROFILES.lite,
      degraded: true,
      reason: "Forced lite profile via flag or environment"
    }
  }

  const autoDegradeEnabled = options.disableAutoDegrade !== true

  if (autoDegradeEnabled) {
    const decision = shouldDegradeForResources(requested)
    if (decision.degrade) {
      return {
        requested: requested.name,
        actual: PERFORMANCE_PROFILES.lite,
        degraded: true,
        reason: decision.reason
      }
    }
  }

  return {
    requested: requested.name,
    actual: requested,
    degraded: false,
    reason: "Requested profile accepted"
  }
}

export function profileToReportEntry(profileDecision) {
  return {
    requested: profileDecision.requested,
    actual: profileDecision.actual.name,
    degraded: profileDecision.degraded,
    reason: profileDecision.reason,
    frameSettleMs: profileDecision.actual.frameSettleMs,
    sceneReadyTimeoutMs: profileDecision.actual.sceneReadyTimeoutMs,
    postGotoWaitMs: profileDecision.actual.postGotoWaitMs
  }
}

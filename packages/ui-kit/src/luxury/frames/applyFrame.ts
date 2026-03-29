import { cn } from "../../lib/cn.js";
import type { MotionProfile } from "../../motion/tokens.js";
import {
  FRAME_PRESET_BY_SURFACE,
  getFramePreset,
  resolveFramePreset,
  type FramePreset,
  type FramePresetId,
  type FrameStyleId,
  type FrameSurfaceId
} from "./frames.js";

export interface ApplyFrameOptions {
  readonly surface: FrameSurfaceId;
  readonly style?: FrameStyleId;
  readonly presetId?: FramePresetId;
  readonly perfProfile?: MotionProfile;
  readonly className?: string;
  readonly attrs?: Readonly<Record<string, string | undefined>>;
  readonly styleVars?: Readonly<Record<string, string | undefined>>;
}

export interface AppliedFrame {
  readonly preset: FramePreset;
  readonly className: string;
  readonly attrs: Record<string, string>;
  readonly style: Record<string, string>;
}

function resolvePreset(options: ApplyFrameOptions): FramePreset {
  if (options.presetId) {
    return getFramePreset(options.presetId);
  }

  if (options.style) {
    return resolveFramePreset(options.style, options.surface);
  }

  return getFramePreset(FRAME_PRESET_BY_SURFACE[options.surface]);
}

function mergeRecord(
  base: Record<string, string>,
  incoming?: Readonly<Record<string, string | undefined>>
): Record<string, string> {
  if (!incoming) {
    return base;
  }

  for (const [key, value] of Object.entries(incoming)) {
    if (value !== undefined) {
      base[key] = value;
    }
  }

  return base;
}

export function applyFrame(options: ApplyFrameOptions): AppliedFrame {
  const preset = resolvePreset(options);
  const perfProfile = options.perfProfile ?? "quality";

  const attrs = mergeRecord(
    {
      "data-ui-frame": "on",
      "data-ui-frame-preset": preset.id,
      "data-ui-frame-style": preset.frameStyleAttr,
      "data-ui-frame-surface": preset.frameSurfaceAttr,
      "data-ui-frame-signature-rows": String(preset.signatureRows),
      "data-ui-perf-profile": perfProfile
    },
    options.attrs
  );

  const style = mergeRecord({}, options.styleVars);

  return {
    preset,
    className: cn(preset.className, options.className),
    attrs,
    style
  };
}

export function applyFrameToSubtree(options: ApplyFrameOptions): {
  readonly wrapper: AppliedFrame;
  readonly contentAttrs: Record<string, string>;
} {
  const wrapper = applyFrame(options);

  return {
    wrapper,
    contentAttrs: {
      "data-ui-frame-content": "on"
    }
  };
}

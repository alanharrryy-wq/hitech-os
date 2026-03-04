export const SEQUENCE_SCHEMA_VERSION = 1 as const;

export const SEQUENCE_TRACKS = ["camera", "overlay", "motion", "layers"] as const;
export type SequenceTrack = (typeof SEQUENCE_TRACKS)[number];

export const SEQUENCE_EASINGS = ["linear", "easeIn", "easeOut", "easeInOut"] as const;
export type SequenceEasing = (typeof SEQUENCE_EASINGS)[number];

export const CAMERA_KEYS = ["zoom", "panX", "panY", "tilt", "focus"] as const;
export const OVERLAY_KEYS = ["opacity", "headline", "subhead", "cta", "tone"] as const;
export const MOTION_KEYS = ["heroEntrance", "parallax", "pulse", "drift", "shake"] as const;
export const LAYER_KEYS = ["visibility", "intensity", "highlight", "mask", "order"] as const;

export const HERO_MOTION_KEYS = ["heroEntrance", "parallax"] as const;

export type CameraKey = (typeof CAMERA_KEYS)[number];
export type OverlayKey = (typeof OVERLAY_KEYS)[number];
export type MotionKey = (typeof MOTION_KEYS)[number];
export type LayerKey = (typeof LAYER_KEYS)[number];
export type HeroMotionKey = (typeof HERO_MOTION_KEYS)[number];

export type SequenceKey = CameraKey | OverlayKey | MotionKey | LayerKey;

export type SequenceValue =
  | string
  | number
  | boolean
  | null
  | readonly string[]
  | { readonly value: string | number | boolean; readonly unit?: string };

const TRACK_KEY_MAP: Readonly<Record<SequenceTrack, readonly SequenceKey[]>> = {
  camera: CAMERA_KEYS,
  overlay: OVERLAY_KEYS,
  motion: MOTION_KEYS,
  layers: LAYER_KEYS
};

export function getAllowedTrackKeys(track: SequenceTrack): readonly SequenceKey[] {
  return TRACK_KEY_MAP[track];
}

export function isTrackKeyAllowed(track: SequenceTrack, key: string): key is SequenceKey {
  return TRACK_KEY_MAP[track].includes(key as SequenceKey);
}

export function isHeroMotionKey(key: string): key is HeroMotionKey {
  return HERO_MOTION_KEYS.includes(key as HeroMotionKey);
}

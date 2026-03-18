import { wiringTargets } from "./wiring-targets";

export function getComposerEntrypointMap(): Readonly<Record<string, string>> {
  return wiringTargets.reduce<Record<string, string>>((acc, target) => {
    acc[target.surface] = target.entrypoint;
    return acc;
  }, {});
}

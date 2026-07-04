/**
 * PRISMA Unified Command Center atmosphere for PC.
 *
 * Layer contract:
 * B0 lab-derived photographic tactical field
 * B1 low-opacity cyan/violet glow field
 * B2 readability vignette
 *
 * No lab runtime, local server lifecycle, client listeners, particles or extra overlay stack.
 */
export function PrismaAtmosphericBackground() {
  return (
    <div
      className="prisma-atmosphere"
      aria-hidden="true"
      data-prisma-background="unified-command-center-simon-spring-lab-v3"
      data-prisma-layer-budget="3"
    >
      <div className="prisma-bg-layer prisma-bg-base" />
      <div className="prisma-bg-layer prisma-bg-mist" />
      <div className="prisma-bg-layer prisma-bg-vignette" />
    </div>
  );
}

import { LiveRegion } from "@components/ui/live-region";
import { SegmentedMeter } from "@components/ui/segmented-meter";
import { Surface } from "@components/ui/surface";
import { SkeletonBlock } from "@components/ui/skeleton-block";

export interface PageLoadingProps {
  title?: string;
  subtitle?: string;
  variant?: "dashboard" | "flow" | "list" | "detail" | "split";
}

function SkeletonMetric() {
  return (
    <div className="rounded-2xl border border-white/10 bg-canvas/32 p-4">
      <SkeletonBlock className="h-3 w-24" />
      <SkeletonBlock className="mt-3 h-8 w-16" />
      <SkeletonBlock className="mt-2 h-3 w-28" />
    </div>
  );
}

export function PageLoading({
  title = "Loading",
  subtitle = "Preparing the next view.",
  variant = "dashboard"
}: PageLoadingProps) {
  return (
    <div className="grid gap-4">
      <LiveRegion message={`${title}. ${subtitle}`} clearAfterMs={1200} />
      <Surface title={title} subtitle={subtitle}>
        {variant === "flow" ? <SegmentedMeter label="Route shell" segments={4} active={2} className="mb-5" /> : null}
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <SkeletonMetric />
          <SkeletonMetric />
          <SkeletonMetric />
          <SkeletonMetric />
        </div>
      </Surface>

      {variant === "flow" ? (
        <div className="grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
          <Surface>
            <SkeletonBlock className="mb-5 h-1.5 w-full rounded-full" pulse="soft" />
            <SkeletonBlock lines={1} className="h-6 w-64" />
            <SkeletonBlock lines={1} className="mt-3 h-4 w-96 max-w-full" />
            <div className="mt-6 grid gap-4">
              {Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className="grid gap-2">
                  <SkeletonBlock className="h-3 w-40" />
                  <SkeletonBlock className="h-11 w-full rounded-xl" pulse="soft" />
                </div>
              ))}
            </div>
          </Surface>
          <Surface>
            <SkeletonBlock className="h-5 w-36" />
            <div className="mt-4 grid gap-3">
              {Array.from({ length: 4 }).map((_, index) => (
                <SkeletonBlock key={index} className="h-20 w-full rounded-2xl" pulse="soft" />
              ))}
            </div>
          </Surface>
        </div>
      ) : variant === "list" ? (
        <>
          <Surface>
            <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
              <SkeletonBlock className="h-11 w-full rounded-xl" pulse="soft" />
              <SkeletonBlock className="h-11 w-44 rounded-xl" pulse="soft" />
            </div>
          </Surface>
          <div className="grid gap-3">
            {Array.from({ length: 6 }).map((_, index) => (
              <Surface key={index}>
                <SkeletonBlock className="h-5 w-52" />
                <div className="mt-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
                  {Array.from({ length: 4 }).map((__, innerIndex) => (
                    <SkeletonBlock key={innerIndex} className="h-16 w-full rounded-xl" pulse="soft" />
                  ))}
                </div>
              </Surface>
            ))}
          </div>
        </>
      ) : variant === "detail" ? (
        <div className="grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
          <Surface>
            <SkeletonBlock className="h-7 w-72" />
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              {Array.from({ length: 4 }).map((_, index) => (
                <SkeletonBlock key={index} className="h-36 w-full rounded-2xl" pulse="soft" />
              ))}
            </div>
          </Surface>
          <div className="grid gap-4">
            <Surface>
              <div className="grid gap-2">
                {Array.from({ length: 4 }).map((_, index) => (
                  <SkeletonBlock key={index} className="h-10 w-full rounded-xl" pulse="soft" />
                ))}
              </div>
            </Surface>
            <Surface>
              <div className="grid gap-2">
                {Array.from({ length: 3 }).map((_, index) => (
                  <SkeletonBlock key={index} className="h-16 w-full rounded-xl" pulse="soft" />
                ))}
              </div>
            </Surface>
          </div>
        </div>
      ) : variant === "split" ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <Surface>
            <div className="grid gap-3">
              {Array.from({ length: 5 }).map((_, index) => (
                <SkeletonBlock key={index} className="h-16 w-full rounded-2xl" pulse="soft" />
              ))}
            </div>
          </Surface>
          <Surface>
            <div className="grid gap-3">
              {Array.from({ length: 5 }).map((_, index) => (
                <SkeletonBlock key={index} className="h-16 w-full rounded-2xl" pulse="soft" />
              ))}
            </div>
          </Surface>
        </div>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          <Surface>
            <div className="grid gap-3">
              {Array.from({ length: 4 }).map((_, index) => (
                <SkeletonBlock key={index} className="h-24 w-full rounded-2xl" pulse="soft" />
              ))}
            </div>
          </Surface>
          <Surface>
            <div className="grid gap-3">
              {Array.from({ length: 4 }).map((_, index) => (
                <SkeletonBlock key={index} className="h-24 w-full rounded-2xl" pulse="soft" />
              ))}
            </div>
          </Surface>
        </div>
      )}
    </div>
  );
}

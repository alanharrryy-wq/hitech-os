import { GlassCard, InsetPanel, cn } from "@hitech/ui-kit";

export interface ValuationBlockModel {
  readonly heading: string;
  readonly items: readonly string[];
  readonly phase1?: string;
  readonly phase2?: string;
}

export interface ValuationBlocksProps {
  readonly blocks: readonly ValuationBlockModel[];
  readonly className?: string;
}

function renderPhaseLine(text?: string) {
  if (!text) {
    return null;
  }

  return <li className="text-sm leading-6 text-[hsl(var(--ui-text-1))]">{text}</li>;
}

export function ValuationBlocks({ blocks, className }: ValuationBlocksProps) {
  return (
    <div className={cn("grid grid-cols-1 gap-3 lg:grid-cols-3", className)}>
      {blocks.map((block) => (
        <GlassCard key={block.heading} className="p-2" tone="default" backdrop="off">
          <InsetPanel title={block.heading} description="Estructura financiera">
            <ul className="m-0 grid list-disc gap-1 pl-5">
              {block.items.map((item) => (
                <li key={item} className="text-sm leading-6 text-[hsl(var(--ui-text-1))]">
                  {item}
                </li>
              ))}
              {renderPhaseLine(block.phase1)}
              {renderPhaseLine(block.phase2)}
            </ul>
          </InsetPanel>
        </GlassCard>
      ))}
    </div>
  );
}

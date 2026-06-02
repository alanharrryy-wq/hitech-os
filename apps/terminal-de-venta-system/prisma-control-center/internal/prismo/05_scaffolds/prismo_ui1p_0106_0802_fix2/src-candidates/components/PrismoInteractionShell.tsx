import React from 'react';
import { PrismoCrystalCommandPalette, CommandItem } from './PrismoCrystalCommandPalette';
export function PrismoInteractionShell({ children, commands = [], onCommand }: { children: React.ReactNode; commands?: CommandItem[]; onCommand?: (item: CommandItem)=>void }) {
  return <section className="prismo-interaction-shell" data-prismo-interaction="fx2">
    <div className="prismo-interaction-shell__aurora" aria-hidden="true" />
    <header className="prismo-interaction-shell__topbar"><strong>PRISMO Theater</strong><PrismoCrystalCommandPalette items={commands} onPick={onCommand} /></header>
    {children}
  </section>;
}

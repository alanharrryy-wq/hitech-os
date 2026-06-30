"use client";

import type { ReactNode } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import * as ScrollArea from "@radix-ui/react-scroll-area";
import * as Select from "@radix-ui/react-select";
import * as Tabs from "@radix-ui/react-tabs";
import * as Tooltip from "@radix-ui/react-tooltip";
import { Slot } from "@radix-ui/react-slot";

export function PremiumDrawer({
  trigger,
  title,
  children
}: {
  trigger: ReactNode;
  title: string;
  children: ReactNode;
}) {
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="premiumRadixOverlay" />
        <Dialog.Content className="premiumRadixDrawer">
          <Dialog.Title>{title}</Dialog.Title>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

export function PremiumActionMenu({
  trigger,
  children
}: {
  trigger: ReactNode;
  children: ReactNode;
}) {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>{trigger}</DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content className="premiumRadixMenu" align="end">
          {children}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}

export function PremiumScrollPane({ children }: { children: ReactNode }) {
  return (
    <ScrollArea.Root className="premiumRadixScrollPane">
      <ScrollArea.Viewport className="premiumRadixViewport">{children}</ScrollArea.Viewport>
      <ScrollArea.Scrollbar className="premiumRadixScrollbar" orientation="vertical">
        <ScrollArea.Thumb className="premiumRadixThumb" />
      </ScrollArea.Scrollbar>
    </ScrollArea.Root>
  );
}

export function PremiumTabs({ children, defaultValue }: { children: ReactNode; defaultValue: string }) {
  return <Tabs.Root defaultValue={defaultValue}>{children}</Tabs.Root>;
}

export function PremiumSelectRoot({ children, value }: { children: ReactNode; value?: string }) {
  return <Select.Root value={value}>{children}</Select.Root>;
}

export function PremiumTooltip({ label, children }: { label: string; children: ReactNode }) {
  return (
    <Tooltip.Provider delayDuration={180}>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <Slot>{children}</Slot>
        </Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content className="premiumRadixTooltip">{label}</Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}

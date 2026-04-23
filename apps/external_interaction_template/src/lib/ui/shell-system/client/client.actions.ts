import type { ActionDescriptor } from "@/lib/ui/shell-system/types";

export const CLIENT_ACTIONS: ActionDescriptor[] = [
  {
    id: "start-flow",
    labelKey: "shell.actions.startFlow",
    iconFamily: "system",
    iconName: "play",
    slot: "quickActionSlot",
    priority: 10,
    variant: "primary",
    href: "/flow/service_request",
    visibility: {
      requiredPermissions: ["flows.start"]
    },
    permissions: ["flows.start"],
    mobilePolicy: "show"
  },
  {
    id: "open-schemas",
    labelKey: "shell.actions.playground",
    iconFamily: "system",
    iconName: "schema",
    slot: "quickActionSlot",
    priority: 20,
    variant: "ghost",
    href: "/playground",
    visibility: {
      requiredPermissions: ["schemas.read"]
    },
    permissions: ["schemas.read"],
    mobilePolicy: "show"
  },
  {
    id: "open-sync",
    labelKey: "shell.actions.openSync",
    iconFamily: "system",
    iconName: "sync",
    slot: "contextActionSlot",
    priority: 10,
    variant: "secondary",
    href: "/sync",
    visibility: {
      requiredPermissions: ["sync.read"]
    },
    permissions: ["sync.read"],
    mobilePolicy: "show"
  },
  {
    id: "open-utilities",
    labelKey: "shell.actions.utilities",
    iconFamily: "system",
    iconName: "utilities",
    slot: "utilitySlot",
    priority: 20,
    variant: "ghost",
    href: "/playground",
    visibility: {
      requiredPermissions: ["utilities.open"]
    },
    permissions: ["utilities.open"],
    mobilePolicy: "drawer"
  }
];


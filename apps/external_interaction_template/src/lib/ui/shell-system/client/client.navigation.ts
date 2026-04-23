import type { NavItemDescriptor } from "@/lib/ui/shell-system/types";

export const CLIENT_NAV_ITEMS: NavItemDescriptor[] = [
  {
    id: "launcher",
    labelKey: "shell.nav.launcher",
    iconFamily: "system",
    iconName: "home",
    route: "/",
    group: "core",
    priority: 10,
    visibility: {
      requiredPermissions: ["workspace.read"]
    },
    permissions: ["workspace.read"],
    slot: "primaryNavSlot",
    mobilePolicy: "show",
    collapsedLabelPolicy: "tooltip",
    tooltip: "shell.nav.launcher"
  },
  {
    id: "inbox",
    labelKey: "shell.nav.inbox",
    iconFamily: "system",
    iconName: "inbox",
    route: "/inbox",
    group: "core",
    priority: 20,
    visibility: {
      requiredPermissions: ["records.read"]
    },
    permissions: ["records.read"],
    slot: "primaryNavSlot",
    badge: { resolverId: "records.pending", tone: "accent" },
    mobilePolicy: "show",
    collapsedLabelPolicy: "tooltip",
    tooltip: "shell.nav.inbox"
  },
  {
    id: "sync",
    labelKey: "shell.nav.sync",
    iconFamily: "system",
    iconName: "sync",
    route: "/sync",
    group: "ops",
    priority: 30,
    visibility: {
      requiredPermissions: ["sync.read"]
    },
    permissions: ["sync.read"],
    slot: "primaryNavSlot",
    badge: { resolverId: "sync.pending", tone: "warning" },
    mobilePolicy: "show",
    collapsedLabelPolicy: "tooltip",
    tooltip: "shell.nav.sync"
  },
  {
    id: "schemas",
    labelKey: "shell.nav.schemas",
    iconFamily: "system",
    iconName: "schema",
    route: "/playground",
    group: "system",
    priority: 40,
    visibility: {
      requiredPermissions: ["schemas.read"]
    },
    permissions: ["schemas.read"],
    slot: "primaryNavSlot",
    mobilePolicy: "show",
    collapsedLabelPolicy: "tooltip",
    tooltip: "shell.nav.schemas",
    children: [
      {
        id: "schemas-flows",
        labelKey: "shell.nav.flows",
        iconFamily: "system",
        iconName: "flows",
        route: "/flow/service_request",
        group: "system",
        priority: 41,
        visibility: {
          requiredPermissions: ["flows.start"]
        },
        permissions: ["flows.start"],
        slot: "primaryNavSlot",
        mobilePolicy: "drawer",
        collapsedLabelPolicy: "tooltip"
      }
    ]
  },
  {
    id: "utilities",
    labelKey: "shell.nav.utilities",
    iconFamily: "system",
    iconName: "utilities",
    route: "/sync",
    group: "support",
    priority: 80,
    visibility: {
      requiredPermissions: ["utilities.open"]
    },
    permissions: ["utilities.open"],
    slot: "secondaryNavSlot",
    mobilePolicy: "drawer",
    collapsedLabelPolicy: "tooltip"
  },
  {
    id: "help",
    labelKey: "shell.nav.help",
    iconFamily: "system",
    iconName: "help",
    route: "/playground",
    group: "support",
    priority: 90,
    visibility: {
      requiredPermissions: ["support.read"]
    },
    permissions: ["support.read"],
    slot: "secondaryNavSlot",
    mobilePolicy: "drawer",
    collapsedLabelPolicy: "tooltip"
  }
];


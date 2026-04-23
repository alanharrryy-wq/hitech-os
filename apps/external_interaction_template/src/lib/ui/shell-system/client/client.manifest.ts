import type { ClientManifest } from "@/lib/ui/shell-system/types";

export const CLIENT_MANIFEST: ClientManifest = {
  id: "external_interaction_template",
  label: "External Interaction Template",
  workspaceLabel: "External Interaction Workspace",
  workspaceDescription: "Reusable operational shell for schema-driven workflows, queue triage, and sync diagnostics.",
  slots: {
    brandSlot: {
      label: "EIT OS",
      subtitle: "External Interaction",
      href: "/",
      logo: {
        family: "system",
        name: "sparkle",
        alt: "Brand"
      },
      visibility: {
        requiredPermissions: ["workspace.read"]
      },
      slotVisibility: {
        desktop: "show",
        tablet: "show",
        mobile: "show"
      },
      emptyBehavior: "collapse",
      breakpoints: {
        desktop: "expanded",
        tablet: "compact",
        mobile: "stack"
      }
    },
    workspaceSlot: {
      title: "Ops Workspace",
      description: "Injectable shell for approvals, intake, support, and operations modules.",
      icon: {
        family: "system",
        name: "workflow"
      },
      visibility: {
        requiredPermissions: ["workspace.read"]
      },
      slotVisibility: {
        desktop: "show",
        tablet: "show",
        mobile: "show"
      },
      emptyBehavior: "collapse",
      breakpoints: {
        desktop: "expanded",
        tablet: "compact",
        mobile: "stack"
      }
    },
    footerSlot: {
      text: "EIT shell core",
      links: [
        { label: "Docs", href: "/playground" },
        { label: "Sync", href: "/sync" }
      ],
      visibility: {
        requiredPermissions: ["workspace.read"]
      },
      slotVisibility: {
        desktop: "show",
        tablet: "show",
        mobile: "hide"
      },
      emptyBehavior: "collapse",
      breakpoints: {
        desktop: "expanded",
        tablet: "compact",
        mobile: "hidden"
      }
    }
  }
};


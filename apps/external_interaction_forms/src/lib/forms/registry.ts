import { approvalPacketFormPlugin } from "@/lib/forms/plugins/approval-packet.plugin";
import { serviceRequestFormPlugin } from "@/lib/forms/plugins/service-request.plugin";
import type { FormPluginDefinition } from "@/lib/forms/contracts";

const FORM_PLUGINS: readonly FormPluginDefinition[] = [serviceRequestFormPlugin, approvalPacketFormPlugin];

function assertPluginRegistry(plugins: readonly FormPluginDefinition[]) {
  const formTypeIds = new Set<string>();

  for (const plugin of plugins) {
    if (formTypeIds.has(plugin.formTypeId)) {
      throw new Error(`Duplicate formTypeId registration: '${plugin.formTypeId}'`);
    }
    formTypeIds.add(plugin.formTypeId);

    if (plugin.steps.length === 0) {
      throw new Error(`Plugin '${plugin.formTypeId}' must register at least one step`);
    }

    const fieldIds = new Set<string>();
    for (const step of plugin.steps) {
      if (!step.id) {
        throw new Error(`Plugin '${plugin.formTypeId}' contains a step without id`);
      }
      if (step.fields.length === 0) {
        throw new Error(`Plugin '${plugin.formTypeId}' step '${step.id}' must define fields`);
      }
      for (const field of step.fields) {
        fieldIds.add(field.id);
      }
    }

    for (const rule of plugin.attachmentRules ?? []) {
      if (!fieldIds.has(rule.fieldId)) {
        throw new Error(
          `Plugin '${plugin.formTypeId}' attachment rule references unknown field '${rule.fieldId}'`
        );
      }
    }
  }
}

assertPluginRegistry(FORM_PLUGINS);

const PLUGIN_MAP = new Map(FORM_PLUGINS.map((plugin) => [plugin.formTypeId, plugin]));

export function listFormPlugins(): readonly FormPluginDefinition[] {
  return FORM_PLUGINS;
}

export function getFormPlugin(formTypeId: string): FormPluginDefinition {
  const plugin = PLUGIN_MAP.get(formTypeId);
  if (!plugin) {
    throw new Error(`Unknown form plugin '${formTypeId}'`);
  }
  return plugin;
}

export function resolveFormTypeId(candidate: string | undefined): string {
  if (candidate && PLUGIN_MAP.has(candidate)) {
    return candidate;
  }
  const firstPlugin = FORM_PLUGINS[0];
  if (!firstPlugin) {
    throw new Error("No form plugins registered");
  }
  return firstPlugin.formTypeId;
}

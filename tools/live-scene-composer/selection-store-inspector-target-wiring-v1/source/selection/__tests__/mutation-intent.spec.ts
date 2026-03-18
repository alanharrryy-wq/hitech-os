import { strict as assert } from "node:assert";
import { createSceneRef, createWidgetRef } from "../contracts";
import { buildUpdateSceneLookIntent, buildUpdateWidgetStyleIntent } from "../mutation-intent";

function test_widget_style_intent_has_explicit_target(): void {
  const intent = buildUpdateWidgetStyleIntent({
    target: createWidgetRef("scene-1", "widget-1", "slot-a"),
    patch: { color: "red" }
  });
  assert.equal(intent.type, "update-widget-style");
  assert.equal(intent.target.kind, "widget");
}

function test_scene_look_intent_has_explicit_target(): void {
  const intent = buildUpdateSceneLookIntent({
    target: createSceneRef("scene-1"),
    patch: { background: "gradient" }
  });
  assert.equal(intent.type, "update-scene-look");
  assert.equal(intent.target.kind, "scene");
}

function run(): void {
  test_widget_style_intent_has_explicit_target();
  test_scene_look_intent_has_explicit_target();
  console.log("mutation-intent.spec.ts passed");
}

run();

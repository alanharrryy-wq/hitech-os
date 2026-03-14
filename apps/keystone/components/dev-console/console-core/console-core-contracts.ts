"use client";

import type { DevConsoleToolId } from "../types";
import {
  DEV_CONSOLE_ACTION_RESULT_EVENT,
  DEV_CONSOLE_DIAGNOSTICS_EVENT,
  DEV_CONSOLE_OPEN_SCENE_EVENT,
  DEV_CONSOLE_REQUEST_DIAGNOSTICS_EVENT,
  DEV_CONSOLE_SCENE_LOOK_MODEL_EVENT,
  DEV_CONSOLE_SNAPSHOT_EVENT,
  DEV_CONSOLE_VALIDATE_SCENE_EVENT
} from "../dev-console-events";
import type { DevConsoleDomain } from "../types";

export interface ConsolePanelContract {
  readonly id: DevConsoleToolId;
  readonly domain: DevConsoleDomain;
  readonly file: string;
  readonly requiresSceneLookModel: boolean;
}

export interface ConsoleEventContract {
  readonly symbol:
    | "DEV_CONSOLE_REQUEST_DIAGNOSTICS_EVENT"
    | "DEV_CONSOLE_DIAGNOSTICS_EVENT"
    | "DEV_CONSOLE_ACTION_RESULT_EVENT"
    | "DEV_CONSOLE_SNAPSHOT_EVENT"
    | "DEV_CONSOLE_OPEN_SCENE_EVENT"
    | "DEV_CONSOLE_VALIDATE_SCENE_EVENT"
    | "DEV_CONSOLE_SCENE_LOOK_MODEL_EVENT";
  readonly eventName: string;
  readonly mustHaveEmitter: boolean;
  readonly mustHaveListener: boolean;
}

export const DEV_CONSOLE_EVENT_CONTRACTS: readonly ConsoleEventContract[] = [
  {
    symbol: "DEV_CONSOLE_REQUEST_DIAGNOSTICS_EVENT",
    eventName: DEV_CONSOLE_REQUEST_DIAGNOSTICS_EVENT,
    mustHaveEmitter: true,
    mustHaveListener: true
  },
  {
    symbol: "DEV_CONSOLE_DIAGNOSTICS_EVENT",
    eventName: DEV_CONSOLE_DIAGNOSTICS_EVENT,
    mustHaveEmitter: true,
    mustHaveListener: true
  },
  {
    symbol: "DEV_CONSOLE_ACTION_RESULT_EVENT",
    eventName: DEV_CONSOLE_ACTION_RESULT_EVENT,
    mustHaveEmitter: true,
    mustHaveListener: true
  },
  {
    symbol: "DEV_CONSOLE_SNAPSHOT_EVENT",
    eventName: DEV_CONSOLE_SNAPSHOT_EVENT,
    mustHaveEmitter: true,
    mustHaveListener: true
  },
  {
    symbol: "DEV_CONSOLE_OPEN_SCENE_EVENT",
    eventName: DEV_CONSOLE_OPEN_SCENE_EVENT,
    mustHaveEmitter: true,
    mustHaveListener: true
  },
  {
    symbol: "DEV_CONSOLE_VALIDATE_SCENE_EVENT",
    eventName: DEV_CONSOLE_VALIDATE_SCENE_EVENT,
    mustHaveEmitter: true,
    mustHaveListener: true
  },
  {
    symbol: "DEV_CONSOLE_SCENE_LOOK_MODEL_EVENT",
    eventName: DEV_CONSOLE_SCENE_LOOK_MODEL_EVENT,
    mustHaveEmitter: true,
    mustHaveListener: false
  }
];

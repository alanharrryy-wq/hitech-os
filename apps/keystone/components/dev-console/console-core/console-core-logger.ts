"use client";

export interface ConsoleCoreLogger {
  readonly scope: string;
  debug: (message: string, metadata?: unknown) => void;
  info: (message: string, metadata?: unknown) => void;
  warn: (message: string, metadata?: unknown) => void;
  error: (message: string, metadata?: unknown) => void;
}

function write(level: "debug" | "info" | "warn" | "error", scope: string, message: string, metadata?: unknown): void {
  const prefix = `[DevConsole/${scope}]`;
  if (metadata === undefined) {
    console[level](`${prefix} ${message}`);
    return;
  }
  console[level](`${prefix} ${message}`, metadata);
}

export function createConsoleCoreLogger(scope: string): ConsoleCoreLogger {
  return {
    scope,
    debug: (message, metadata) => write("debug", scope, message, metadata),
    info: (message, metadata) => write("info", scope, message, metadata),
    warn: (message, metadata) => write("warn", scope, message, metadata),
    error: (message, metadata) => write("error", scope, message, metadata)
  };
}

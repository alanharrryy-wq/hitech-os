#!/usr/bin/env node
const mode = process.argv.includes("--build") ? "build" : "dev";
console.log(`[demo-engine] placeholder running in ${mode} mode`);

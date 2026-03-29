/**
 * src/runner.ts — Agent run orchestrator (stub for T022, full implementation in T033)
 *
 * This module wires together the standard blueprint and executes a full agent run.
 * The CLI calls `runAgent(task, opts)` — the blueprint runner, config loading,
 * and all 9 blueprint nodes are wired here in T033.
 */

import type { CliOptions } from "./cli.js";

export interface RunResult {
  status: "succeeded" | "failed" | "error" | "timeout";
  error?: string;
}

/**
 * Execute a full agent run for the given task description.
 * Loads config, builds RunContext, runs the standard blueprint.
 *
 * @param task  Plain-text task description
 * @param opts  Parsed CLI options (overrides for config values)
 */
export async function runAgent(task: string, opts: CliOptions): Promise<RunResult> {
  // Full implementation wired in T033 (standard blueprint)
  void task;
  void opts;
  throw new Error("runAgent is not yet implemented — see T033");
}

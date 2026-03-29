/**
 * src/cli.ts — CLI entry point (FR-001, FR-012)
 *
 * Exposes a `run` command that accepts a plain-text task description and all
 * override options defined in contracts/cli-contract.md.
 *
 * Exports `createProgram()` so tests can instantiate a fresh Commander instance
 * without triggering process.exit (exitOverride() makes it throw instead).
 */

import { Command } from "commander";
import { runAgent } from "./runner.js";

// ─── Option types ─────────────────────────────────────────────────────────────

export interface CliOptions {
  config: string;
  provider?: string;
  model?: string;
  dryRun: boolean;
  maxRetries?: number;
  maxTokens?: number;
  timeout?: number;
  verbose: boolean;
  outputDir: string;
}

// ─── Program factory ──────────────────────────────────────────────────────────

/**
 * Build and return a configured Commander program.
 * Calls `.exitOverride()` so Commander throws on errors instead of calling
 * `process.exit()` — this makes the CLI unit-testable.
 */
export function createProgram(): Command {
  const program = new Command();

  program
    .name("duc-e2e-agent")
    .description("One-shot end-to-end coding agent powered by Pi SDK")
    .exitOverride();

  program
    .command("run")
    .description("Execute a coding task end-to-end")
    .argument("<task>", "Plain-text description of the coding task")
    .option("-c, --config <path>", "Path to configuration file", "./pi-agent.config.ts")
    .option("-p, --provider <provider>", "LLM provider override (anthropic | openai)")
    .option("-m, --model <model>", "Model name override")
    .option("--dry-run", "Show plan without executing changes", false)
    .option("--max-retries <n>", "Override max retry count", (v) => parseInt(v, 10))
    .option("--max-tokens <n>", "Override token budget", (v) => parseInt(v, 10))
    .option("--timeout <n>", "Override timeout in seconds", (v) => parseInt(v, 10))
    .option("-v, --verbose", "Enable verbose logging", false)
    .option("--output-dir <dir>", "Directory for run artifacts", "./runs/")
    .exitOverride()
    .action(async (task: string, opts: CliOptions) => {
      await runAgent(task, opts);
    });

  return program;
}

// ─── Entry point ──────────────────────────────────────────────────────────────

// Only parse when run directly (not imported by tests)
const isMain =
  typeof process !== "undefined" &&
  process.argv[1] !== undefined &&
  process.argv[1].endsWith("duc-e2e-agent.js") || process.argv[1].endsWith("cli.js");

if (isMain) {
  createProgram()
    .parseAsync(process.argv)
    .catch((err: unknown) => {
      if (err instanceof Error) {
        console.error(err.message);
      }
      process.exit(1);
    });
}

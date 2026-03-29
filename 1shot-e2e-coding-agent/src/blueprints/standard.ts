/**
 * src/blueprints/standard.ts — Standard 9-node workflow (FR-017)
 *
 * Wires all steps into a BlueprintRunner:
 *   setup → context_gather → plan → implement → lint_and_format
 *   → test → commit_and_push → report → END
 *
 * Conditional routing:
 *   test PASS  → commit_and_push
 *   test FAIL  → fix_failures → test (retry loop)
 *   fix_failures retryCount ≥ maxRetries → null (run ends as failed)
 *
 * The router functions are exported for unit testing without running the full pipeline.
 */

import { BlueprintRunner } from "../orchestrator.js";
import { setupStep } from "../steps/setup.js";
import { contextGatherStep } from "../steps/context-gather.js";
import { planStep } from "../steps/plan.js";
import { implementStep } from "../steps/implement.js";
import { lintFormatStep } from "../steps/lint-format.js";
import { testStep } from "../steps/test.js";
import { fixFailuresStep } from "../steps/fix-failures.js";
import { commitPushStep } from "../steps/commit-push.js";
import { reportStep } from "../steps/report.js";
import { createQualityToolsExtension } from "../../extensions/quality-tools.js";
import type { RunContext, StepResult } from "../types.js";

// ─── Routing functions (exported for unit testing) ────────────────────────────

export function routeAfterTest(result: StepResult): string {
  return result.status === "passed" ? "commit_and_push" : "fix_failures";
}

export function routeAfterFixFailures(ctx: RunContext, maxRetries: number): string | null {
  return ctx.retryCount < maxRetries ? "test" : null;
}

// ─── Blueprint factory ────────────────────────────────────────────────────────

/**
 * Create a wired-up BlueprintRunner for the standard 9-node workflow.
 * ctx is passed by reference — mutations (ctx.retryCount++, ctx.branch, etc.)
 * are visible to subsequent nodes via closure.
 */
export function createStandardBlueprint(ctx: RunContext): BlueprintRunner {
  const maxRetries = ctx.config.shiftLeft?.maxRetries ?? 2;

  // Capture last test output for fix_failures — updated by the test node's next()
  let lastTestOutput = "";

  // Quality-tools extension for the fix-failures node (run_test + run_lint)
  const qualityTools = createQualityToolsExtension({
    workspacePath: ctx.workspacePath,
    testCommand: ctx.config.repo.testCommand,
    lintCommand: ctx.config.repo.lintCommand,
  });

  const runner = new BlueprintRunner("standard", "setup");

  runner
    .addNode({
      id: "setup",
      type: "deterministic",
      execute: () => setupStep(ctx),
      next: () => "context_gather",
    })
    .addNode({
      id: "context_gather",
      type: "agent",
      execute: () => contextGatherStep(ctx),
      next: () => "plan",
    })
    .addNode({
      id: "plan",
      type: "agent",
      execute: () => planStep(ctx),
      next: () => "implement",
    })
    .addNode({
      id: "implement",
      type: "agent",
      execute: () => implementStep(ctx),
      next: () => "lint_and_format",
    })
    .addNode({
      id: "lint_and_format",
      type: "deterministic",
      execute: () => lintFormatStep(ctx),
      next: () => "test",
    })
    .addNode({
      id: "test",
      type: "deterministic",
      execute: () => testStep(ctx),
      next: (result) => {
        // Capture test output for fix_failures prompt
        lastTestOutput = String(result.data?.output ?? "");
        return routeAfterTest(result);
      },
    })
    .addNode({
      id: "fix_failures",
      type: "agent",
      execute: () => fixFailuresStep(ctx, lastTestOutput, qualityTools.toolDefinitions),
      // If fix_failures returned "failed" (oscillation or internal abort), route to null
      // to terminate the blueprint rather than looping back to "test".
      next: (result) => result.status === "passed" ? routeAfterFixFailures(ctx, maxRetries) : null,
    })
    .addNode({
      id: "commit_and_push",
      type: "deterministic",
      execute: () => commitPushStep(ctx),
      next: () => "report",
    })
    .addNode({
      id: "report",
      type: "deterministic",
      execute: () => reportStep(ctx),
      next: () => null,
    });

  return runner;
}

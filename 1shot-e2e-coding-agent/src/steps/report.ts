/**
 * src/steps/report.ts — Report step (FR-014)
 *
 * Summarises the completed run to the console and returns accumulated metrics.
 */
import type { RunContext, StepResult, TestResult } from "../types.js";

export async function reportStep(
  ctx: RunContext,
  accumulatedData?: Record<string, unknown>,
): Promise<StepResult> {
  const { task, branch, tokenBudget } = ctx;
  const totalTokens = tokenBudget.consumed;

  console.log("=== 1-Shot Coding Agent — Run Report ===");
  console.log(`Task   : ${task.description}`);
  console.log(`Branch : ${branch}`);
  console.log(`Tokens : ${totalTokens.toLocaleString()}`);

  if (accumulatedData?.testResult) {
    const tr = accumulatedData.testResult as TestResult;
    console.log(`Tests  : ${tr.passed} passed, ${tr.failed} failed, ${tr.skipped} skipped (${tr.duration}ms)`);
  }

  if (accumulatedData?.prUrl) {
    console.log(`PR     : ${accumulatedData.prUrl}`);
  }

  return {
    status: "passed",
    data: { totalTokens, branch },
  };
}

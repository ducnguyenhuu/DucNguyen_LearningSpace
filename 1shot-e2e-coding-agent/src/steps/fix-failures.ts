/**
 * src/steps/fix-failures.ts — Fix Failures step (FR-008)
 *
 * Seventh node in the standard blueprint (conditional — only reached on test failure).
 * Responsible for:
 *  1. Creating a Pi session with write tool access (read/write/edit/bash/grep)
 *  2. Injecting the error output (from test/lint) and ctx.plan as context
 *  3. Letting the LLM diagnose and fix the failures
 *  4. Incrementing ctx.retryCount so the blueprint can enforce the retry cap
 *
 * After this step, the blueprint routes back to the test step.
 * The retry loop is enforced by the blueprint's next() function — not here.
 *
 * Signature: fixFailuresStep(ctx, errorOutput) — errorOutput is the
 * combined stdout+stderr from the failed test/lint step.
 *
 * Returns a StepResult with:
 *  - data.summary — LLM's description of what it fixed
 *  - tokensUsed   — cumulative tokens consumed in this session
 */

import {
  createSession,
  runPrompt,
  getTokensUsed,
} from "../adapters/pi-sdk.js";
import type { RunContext, StepResult } from "../types.js";

// ─── Embedded system prompt ───────────────────────────────────────────────────

/**
 * Default system prompt for the fix-failures node.
 * T032 will replace this with prompts/fix-failures.md content.
 */
const DEFAULT_SYSTEM_PROMPT = `You are a software debugging agent. Your job is to fix failing
tests or lint errors by modifying source code.

You will be given:
- The original task description
- The change plan that was already executed
- The error output from a failed test or lint run

Analyze the errors carefully. Use the tools to read relevant files and understand
what went wrong. Then apply targeted fixes.

Use read/grep to investigate, write/edit to fix files, bash to verify locally.
Focus only on fixing the reported failures — do not make unrelated changes.
When done, briefly describe what you fixed and why.`.trim();

// ─── fixFailuresStep ──────────────────────────────────────────────────────────

export async function fixFailuresStep(
  ctx: RunContext,
  errorOutput: string,
): Promise<StepResult> {
  // ── 1. Resolve model from config ───────────────────────────────────────────
  const provider = ctx.config.provider.default;
  const model =
    provider === "anthropic"
      ? (ctx.config.provider.anthropicModel ?? "claude-sonnet-4-20250514")
      : (ctx.config.provider.openaiModel ?? "gpt-4.1");

  // ── 2. Build user prompt — inject error output + plan ─────────────────────
  const planSection = ctx.plan
    ? `\n\n## Original Change Plan\n${ctx.plan}`
    : "";

  const errorSection = errorOutput
    ? `\n\n## Error Output\n\`\`\`\n${errorOutput}\n\`\`\``
    : "";

  const userPrompt =
    `## Task\n${ctx.task.description}` +
    planSection +
    errorSection +
    `\n\nDiagnose the failures and apply targeted fixes. ` +
    `Read the failing files first, then edit only what is necessary.`;

  // ── 3. Create Pi session with write tool access ────────────────────────────
  let handle;
  try {
    handle = await createSession(
      {
        systemPrompt: DEFAULT_SYSTEM_PROMPT,
        tools: ["read", "write", "edit", "bash", "grep"],
        extensions: [],
        provider,
        model,
      },
      { cwd: ctx.workspacePath },
    );
  } catch (err) {
    return {
      status: "error",
      error: err instanceof Error ? err.message : String(err),
    };
  }

  // ── 4. Run prompt — LLM diagnoses and fixes ────────────────────────────────
  let output: string;
  try {
    output = await runPrompt(handle, userPrompt);
  } catch (err) {
    return {
      status: "error",
      error: err instanceof Error ? err.message : String(err),
    };
  }

  // ── 5. Increment retry count ───────────────────────────────────────────────
  ctx.retryCount += 1;

  // ── 6. Record token usage ──────────────────────────────────────────────────
  const tokensUsed = getTokensUsed(handle);

  return {
    status: "passed",
    tokensUsed,
    data: {
      summary: output,
    },
  };
}

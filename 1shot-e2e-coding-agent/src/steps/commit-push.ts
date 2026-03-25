/**
 * src/steps/commit-push.ts — Commit & Push step (FR-009)
 *
 * Eighth node in the standard blueprint. Responsible for:
 *  1. Checking git status — if clean, return noop (nothing to commit)
 *  2. Staging all changes: git add .
 *  3. Committing with a formatted message: "{prefix} {task description}"
 *  4. Optionally pushing to origin/{branch} if autoPush is enabled
 *
 * Returns a StepResult with:
 *  - data.branch  — current branch name
 *  - data.sha     — commit SHA (from simple-git response)
 *  - data.noop    — true if there was nothing to commit
 */

import simpleGit from "simple-git";
import type { RunContext, StepResult } from "../types.js";

const DEFAULT_COMMIT_PREFIX = "[agent]";

export async function commitPushStep(ctx: RunContext): Promise<StepResult> {
  const git = simpleGit(ctx.workspacePath);
  const prefix = ctx.config.git?.commitMessagePrefix ?? DEFAULT_COMMIT_PREFIX;
  const autoPush = ctx.config.git?.autoPush ?? true;
  const branch = ctx.branch;

  try {
    // ── 1. Check if there is anything to commit ────────────────────────────
    const status = await git.status();
    if (status.isClean()) {
      return {
        status: "passed",
        data: { branch, noop: true },
      };
    }

    // ── 2. Stage all changes ───────────────────────────────────────────────
    await git.add(".");

    // ── 3. Commit ──────────────────────────────────────────────────────────
    const commitMessage = `${prefix} ${ctx.task.description}`;
    const commitResult = await git.commit(commitMessage);
    const sha = commitResult.commit;

    // ── 4. Push (optional) ─────────────────────────────────────────────────
    if (autoPush) {
      await git.push("origin", branch, ["--set-upstream"]);
    }

    return {
      status: "passed",
      data: { branch, sha, noop: false },
    };
  } catch (err) {
    return {
      status: "error",
      error: err instanceof Error ? err.message : String(err),
    };
  }
}


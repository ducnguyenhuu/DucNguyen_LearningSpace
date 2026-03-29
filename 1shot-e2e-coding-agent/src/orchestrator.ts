/**
 * src/orchestrator.ts — BlueprintRunner (Architecture Decision D1)
 *
 * Sequences blueprint nodes by repeatedly:
 *   1. Executing the current node's execute(ctx) function
 *   2. Calling node.next(result) to get the next node ID (or null to stop)
 *
 * Each node is either:
 *  - "deterministic": a plain TypeScript function (lint, test, git, etc.)
 *  - "agent": a Pi SDK session (context-gather, plan, implement, fix-failures)
 *
 * Why a simple while-loop instead of a framework:
 *   The workflow has exactly one conditional branch (test pass/fail).
 *   A ~150 LOC while-loop is simpler, easier to debug, and has no external deps.
 *   See plan.md D1 for full rationale.
 */

import type { RunContext, BlueprintNode, StepResult, NodeResult } from "./types.js";

// ─── RunSummary ───────────────────────────────────────────────────────────────

export interface RunSummary {
  /** "succeeded" if the run completed without error, "failed" otherwise. */
  status: "succeeded" | "failed";
  /** Human-readable error message when status is "failed". */
  error?: string;
  /** Results for each node that was executed (in execution order). */
  nodeResults: NodeResult[];
  /** Total wall-clock duration of the run in milliseconds. */
  durationMs: number;
}

// ─── BlueprintRunner ──────────────────────────────────────────────────────────

export class BlueprintRunner {
  private readonly _name: string;
  private readonly _entryNodeId: string;
  private readonly _nodes = new Map<string, BlueprintNode>();

  constructor(name: string, entryNodeId: string) {
    this._name = name;
    this._entryNodeId = entryNodeId;
  }

  /**
   * Register a node with the runner.
   * Returns `this` for method chaining: runner.addNode(a).addNode(b).run(ctx)
   */
  addNode(node: BlueprintNode): this {
    this._nodes.set(node.id, node);
    return this;
  }

  /**
   * Execute the blueprint starting from the entry node.
   *
   * Execution model:
   *  1. Look up the current node. Throw if not found.
   *  2. Call execute(ctx) and record timing + result.
   *  3. If result.status is "error", stop immediately → failed.
   *  4. If execute() throws, catch, record, stop → failed.
   *  5. Call node.next(result) to get the next node ID.
   *  6. If next returns null, stop → succeeded.
   *  7. If next returns an unknown ID, throw.
   *  8. Repeat from step 1 with the new node ID.
   */
  async run(ctx: RunContext): Promise<RunSummary> {
    const runStart = Date.now();
    const nodeResults: NodeResult[] = [];

    // Validate entry node exists before starting
    if (!this._nodes.has(this._entryNodeId)) {
      throw new Error(
        `BlueprintRunner "${this._name}": entry node "${this._entryNodeId}" is not registered`,
      );
    }

    let currentNodeId: string | null = this._entryNodeId;

    while (currentNodeId !== null) {
      const node = this._nodes.get(currentNodeId);

      // Should not happen after initial validation, but guard for dynamic routing
      if (!node) {
        throw new Error(
          `BlueprintRunner "${this._name}": node "${currentNodeId}" is not registered`,
        );
      }

      const nodeStart = Date.now();
      let result: StepResult;

      try {
        result = await node.execute(ctx);
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        nodeResults.push({
          nodeId: node.id,
          type: node.type,
          status: "error",
          duration: Date.now() - nodeStart,
          tokensUsed: 0,
        });
        return {
          status: "failed",
          error: `Node "${node.id}" threw: ${msg}`,
          nodeResults,
          durationMs: Date.now() - runStart,
        };
      }

      nodeResults.push({
        nodeId: node.id,
        type: node.type,
        status: result.status,
        duration: Date.now() - nodeStart,
        tokensUsed: result.tokensUsed ?? 0,
      });

      // "error" status from a node means unrecoverable failure — stop immediately
      if (result.status === "error") {
        return {
          status: "failed",
          error: result.error ?? `Node "${node.id}" returned status "error"`,
          nodeResults,
          durationMs: Date.now() - runStart,
        };
      }

      // Ask the node where to go next
      const nextId = node.next(result);

      if (nextId === null) {
        // Routing ended — run is complete
        break;
      }

      if (!this._nodes.has(nextId)) {
        throw new Error(
          `BlueprintRunner "${this._name}": node "${node.id}" routed to unknown node "${nextId}"`,
        );
      }

      currentNodeId = nextId;
    }

    return {
      status: "succeeded",
      nodeResults,
      durationMs: Date.now() - runStart,
    };
  }
}

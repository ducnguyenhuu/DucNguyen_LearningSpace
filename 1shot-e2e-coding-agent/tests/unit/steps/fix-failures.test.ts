/**
 * tests/unit/steps/fix-failures.test.ts
 *
 * Tests the fix-failures step: Pi session with write tools, error output
 * injection into prompt, ctx.retryCount increment, and error handling.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import type { RunContext } from "../../../src/types.js";
import { DEFAULT_CONFIG } from "../../../src/config.js";
import { createLayerBudgets } from "../../../src/types.js";

// ─── Mocks ────────────────────────────────────────────────────────────────────

const { mockCreateSession, mockRunPrompt, mockGetTokensUsed } = vi.hoisted(() => ({
  mockCreateSession: vi.fn(),
  mockRunPrompt: vi.fn(),
  mockGetTokensUsed: vi.fn(),
}));

vi.mock("../../../src/adapters/pi-sdk.js", () => ({
  createSession: mockCreateSession,
  runPrompt: mockRunPrompt,
  getTokensUsed: mockGetTokensUsed,
}));

import { fixFailuresStep } from "../../../src/steps/fix-failures.js";

// ─── Helpers ──────────────────────────────────────────────────────────────────

const FAKE_HANDLE = { session: {} as never };

const SAMPLE_ERROR_OUTPUT = `
FAIL tests/auth/login.test.ts
  ● login › should reject wrong password

    expect(received).toBe(expected)
    Expected: false
    Received: true

Test Suites: 1 failed, 1 total
Tests:       1 failed, 9 passed, 10 total
`.trim();

function makeCtx(overrides: Partial<RunContext> = {}): RunContext {
  return {
    task: {
      description: "fix the login bug in auth module",
      slug: "fix-the-login-bug-in-auth-module",
      timestamp: "2026-03-16T00:00:00.000Z",
    },
    config: {
      ...DEFAULT_CONFIG,
      provider: {
        default: "anthropic",
        anthropicModel: "claude-sonnet-4-20250514",
        openaiModel: "gpt-4.1",
      },
      repo: { ...DEFAULT_CONFIG.repo, testCommand: "npm test", lintCommand: "npm run lint" },
    },
    workspacePath: "/workspace/test-repo",
    branch: "agent/fix-the-login-bug-in-auth-module",
    repoMap: "",
    relevantFiles: ["src/auth/login.ts", "tests/auth/login.test.ts"],
    understanding: "Bug is in bcrypt.compare argument order.",
    plan: "Fix validateCredentials() on line 42.",
    retryCount: 0,
    tokenBudget: {
      maxTokens: 200_000,
      consumed: 0,
      remaining: 200_000,
      layerBudgets: createLayerBudgets(200_000),
    },
    logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn() },
    ...overrides,
  };
}

// ─── Tests ────────────────────────────────────────────────────────────────────

describe("fixFailuresStep()", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockCreateSession.mockResolvedValue(FAKE_HANDLE);
    mockRunPrompt.mockResolvedValue("Fixed the failing test by correcting the assertion.");
    mockGetTokensUsed.mockReturnValue(3000);
  });

  // ─── Status ─────────────────────────────────────────────────────────────────

  it("returns passed status on success", async () => {
    const result = await fixFailuresStep(makeCtx(), SAMPLE_ERROR_OUTPUT);
    expect(result.status).toBe("passed");
  });

  it("returns error status when createSession throws", async () => {
    mockCreateSession.mockRejectedValueOnce(new Error("API key missing"));
    const result = await fixFailuresStep(makeCtx(), SAMPLE_ERROR_OUTPUT);
    expect(result.status).toBe("error");
    expect(result.error).toMatch(/API key missing/i);
  });

  it("returns error status when runPrompt throws", async () => {
    mockRunPrompt.mockRejectedValueOnce(new Error("rate limit exceeded"));
    const result = await fixFailuresStep(makeCtx(), SAMPLE_ERROR_OUTPUT);
    expect(result.status).toBe("error");
    expect(result.error).toMatch(/rate limit exceeded/i);
  });

  // ─── Session config — write tools ───────────────────────────────────────────

  it("creates session with write tools: read, write, edit, bash, grep", async () => {
    await fixFailuresStep(makeCtx(), SAMPLE_ERROR_OUTPUT);
    const [sessionConfig] = mockCreateSession.mock.calls[0] as [{ tools: string[] }];
    expect(sessionConfig.tools).toEqual(["read", "write", "edit", "bash", "grep"]);
  });

  it("creates session with provider from ctx.config", async () => {
    await fixFailuresStep(makeCtx(), SAMPLE_ERROR_OUTPUT);
    const [sessionConfig] = mockCreateSession.mock.calls[0] as [{ provider: string }];
    expect(sessionConfig.provider).toBe("anthropic");
  });

  it("creates session with anthropic model from ctx.config", async () => {
    await fixFailuresStep(makeCtx(), SAMPLE_ERROR_OUTPUT);
    const [sessionConfig] = mockCreateSession.mock.calls[0] as [{ model: string }];
    expect(sessionConfig.model).toBe("claude-sonnet-4-20250514");
  });

  it("creates session with openai model when provider is openai", async () => {
    const ctx = makeCtx();
    ctx.config.provider = { default: "openai", openaiModel: "gpt-4.1" };
    await fixFailuresStep(ctx, SAMPLE_ERROR_OUTPUT);
    const [sessionConfig] = mockCreateSession.mock.calls[0] as [{ model: string }];
    expect(sessionConfig.model).toBe("gpt-4.1");
  });

  it("passes workspacePath as cwd to createSession", async () => {
    await fixFailuresStep(makeCtx(), SAMPLE_ERROR_OUTPUT);
    const [, options] = mockCreateSession.mock.calls[0] as [unknown, { cwd: string }];
    expect(options?.cwd).toBe("/workspace/test-repo");
  });

  // ─── Prompt construction — error output injection ────────────────────────────

  it("user prompt contains the error output", async () => {
    await fixFailuresStep(makeCtx(), SAMPLE_ERROR_OUTPUT);
    const [, userPrompt] = mockRunPrompt.mock.calls[0] as [unknown, string];
    expect(userPrompt).toContain("should reject wrong password");
  });

  it("user prompt contains task description", async () => {
    await fixFailuresStep(makeCtx(), SAMPLE_ERROR_OUTPUT);
    const [, userPrompt] = mockRunPrompt.mock.calls[0] as [unknown, string];
    expect(userPrompt).toContain("fix the login bug in auth module");
  });

  it("user prompt contains ctx.plan for intent reference", async () => {
    await fixFailuresStep(makeCtx(), SAMPLE_ERROR_OUTPUT);
    const [, userPrompt] = mockRunPrompt.mock.calls[0] as [unknown, string];
    expect(userPrompt).toContain("Fix validateCredentials()");
  });

  it("works with empty error output string", async () => {
    const result = await fixFailuresStep(makeCtx(), "");
    expect(result.status).toBe("passed");
  });

  // ─── retryCount ──────────────────────────────────────────────────────────────

  it("increments ctx.retryCount", async () => {
    const ctx = makeCtx({ retryCount: 0 });
    await fixFailuresStep(ctx, SAMPLE_ERROR_OUTPUT);
    expect(ctx.retryCount).toBe(1);
  });

  it("increments ctx.retryCount from existing value", async () => {
    const ctx = makeCtx({ retryCount: 1 });
    await fixFailuresStep(ctx, SAMPLE_ERROR_OUTPUT);
    expect(ctx.retryCount).toBe(2);
  });

  // ─── Token usage ─────────────────────────────────────────────────────────────

  it("returns tokensUsed from getTokensUsed", async () => {
    const result = await fixFailuresStep(makeCtx(), SAMPLE_ERROR_OUTPUT);
    expect(result.tokensUsed).toBe(3000);
  });

  // ─── Result data ─────────────────────────────────────────────────────────────

  it("includes summary in result data", async () => {
    const result = await fixFailuresStep(makeCtx(), SAMPLE_ERROR_OUTPUT);
    expect(result.data?.summary).toBe("Fixed the failing test by correcting the assertion.");
  });
});

import { describe, expect, it } from "vitest";
import { runAction } from "../src/action.js";

describe("runAction", () => {
  it("reports a hit", async () => {
    const out = await runAction({ key: "k" }, { restore: async () => true });
    expect(out.cacheHit).toBe(true);
  });
});

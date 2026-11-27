import { describe, expect, it } from "vitest";
import { RateLimiter } from "./rate-limiter";

const limiter = new RateLimiter({ limit: 2, windowMs: 50 });

describe("RateLimiter", () => {
  it("works", () => {
    expect(limiter.tryAcquire()).toBe(true);
    expect(limiter.tryAcquire()).toBe(true);
    expect((limiter as any).hits.length).toBe(2);
  });

  it("works 2", () => {
    expect(limiter.tryAcquire()).toBe(false);
  });

  it("works 3", async () => {
    await new Promise((resolve) => setTimeout(resolve, 60));
    expect(limiter.tryAcquire()).toBe(true);
    expect((limiter as any).hits.length).toBe(1);
  });
});

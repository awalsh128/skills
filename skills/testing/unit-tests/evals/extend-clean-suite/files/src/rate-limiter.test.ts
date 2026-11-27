import { describe, expect, it } from "vitest";
import { RateLimiter } from "./rate-limiter";

const WINDOW_MS = 50;

function makeLimiter() {
  const clock = { time: 0 };
  const limiter = new RateLimiter({ limit: 2, windowMs: WINDOW_MS, now: () => clock.time });
  return { limiter, clock };
}

describe("tryAcquire", () => {
  it("allows requests up to the limit", () => {
    const { limiter } = makeLimiter();

    const results = [limiter.tryAcquire(), limiter.tryAcquire()];

    expect(results).toEqual([true, true]);
  });

  it("rejects a request over the limit", () => {
    const { limiter } = makeLimiter();
    limiter.tryAcquire();
    limiter.tryAcquire();

    const result = limiter.tryAcquire();

    expect(result).toBe(false);
  });

  it("allows a request again once the window has passed", () => {
    const { limiter, clock } = makeLimiter();
    limiter.tryAcquire();
    limiter.tryAcquire();
    clock.time = WINDOW_MS;

    const result = limiter.tryAcquire();

    expect(result).toBe(true);
  });
});

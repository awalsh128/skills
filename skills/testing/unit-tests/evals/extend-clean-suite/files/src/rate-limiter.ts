export interface RateLimiterOptions {
  limit: number;
  windowMs: number;
  /** Extra requests allowed within one window on top of limit. */
  burst?: number;
  now?: () => number;
}

export class RateLimiter {
  private hits: number[] = [];
  private readonly capacity: number;
  private readonly windowMs: number;
  private readonly now: () => number;

  constructor({ limit, windowMs, burst = 0, now = Date.now }: RateLimiterOptions) {
    if (!Number.isInteger(burst) || burst < 0) throw new RangeError("burst must be a non-negative integer");

    this.capacity = limit + burst;
    this.windowMs = windowMs;
    this.now = now;
  }

  tryAcquire(): boolean {
    const time = this.now();
    this.hits = this.hits.filter((hit) => time - hit < this.windowMs);
    if (this.hits.length >= this.capacity) return false;

    this.hits.push(time);
    return true;
  }
}

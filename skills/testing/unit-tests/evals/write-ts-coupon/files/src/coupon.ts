export interface Coupon {
  code: string;
  percentOff: number;
  expiresAt: Date;
  minSubtotalCents: number;
  maxDiscountCents?: number;
}

export type CouponRejection = "unknown" | "expired" | "below-minimum";

export class CouponError extends Error {
  constructor(readonly reason: CouponRejection) {
    super(`Coupon rejected: ${reason}`);
  }
}

/** Applies coupon codes to a cart subtotal. Amounts are integer cents. */
export class CouponValidator {
  private readonly coupons: Map<string, Coupon>;

  constructor(
    coupons: Coupon[],
    private readonly now: () => Date = () => new Date(),
  ) {
    this.coupons = new Map(coupons.map((c) => [c.code.toUpperCase(), c]));
  }

  /** Returns the discounted subtotal in cents, or throws CouponError. */
  apply(code: string, subtotalCents: number): number {
    const coupon = this.coupons.get(code.trim().toUpperCase());
    if (!coupon) throw new CouponError("unknown");
    if (this.isExpired(coupon)) throw new CouponError("expired");
    if (subtotalCents < coupon.minSubtotalCents) throw new CouponError("below-minimum");

    const discount = this.discountFor(coupon, subtotalCents);
    return subtotalCents - discount;
  }

  private isExpired(coupon: Coupon): boolean {
    return this.now().getTime() >= coupon.expiresAt.getTime();
  }

  private discountFor(coupon: Coupon, subtotalCents: number): number {
    const raw = Math.round((subtotalCents * coupon.percentOff) / 100);
    return coupon.maxDiscountCents === undefined ? raw : Math.min(raw, coupon.maxDiscountCents);
  }
}

export const BASE_FEE_CENTS = 500;
export const PER_KG_CENTS = 120;
export const FREE_SHIPPING_SUBTOTAL_CENTS = 5000;
export const HEAVY_KG = 20;
export const HEAVY_MULTIPLIER = 1.15;

export function shippingFeeCents(subtotalCents: number, weightKg: number): number {
  if (subtotalCents < 0 || weightKg <= 0) throw new RangeError("invalid shipment");

  const heavy = weightKg > HEAVY_KG;
  if (subtotalCents >= FREE_SHIPPING_SUBTOTAL_CENTS && !heavy) return 0;

  const fee = BASE_FEE_CENTS + Math.ceil(weightKg) * PER_KG_CENTS;
  return heavy ? Math.round(fee * HEAVY_MULTIPLIER) : fee;
}

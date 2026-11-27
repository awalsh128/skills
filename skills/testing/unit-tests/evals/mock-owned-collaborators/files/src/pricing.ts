export interface LineItem {
  unitCents: number;
  quantity: number;
}

const BULK_QUANTITY = 10;

export function totalCents(items: LineItem[]): number {
  return items.reduce((sum, item) => {
    const line = item.unitCents * item.quantity;
    return sum + (item.quantity >= BULK_QUANTITY ? Math.round(line * 0.9) : line);
  }, 0);
}

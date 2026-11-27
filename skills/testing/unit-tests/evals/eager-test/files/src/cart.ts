export interface CartItem {
  sku: string;
  unitCents: number;
  quantity: number;
}

export class Cart {
  private items: CartItem[] = [];
  private percentOff = 0;

  add(item: CartItem): void {
    if (item.quantity < 1) throw new RangeError("quantity must be at least 1");

    const existing = this.items.find((i) => i.sku === item.sku);
    if (existing) existing.quantity += item.quantity;
    else this.items.push({ ...item });
  }

  remove(sku: string): void {
    this.items = this.items.filter((i) => i.sku !== sku);
  }

  applyDiscount(percentOff: number): void {
    if (percentOff < 0 || percentOff > 100) throw new RangeError("discount out of range");

    this.percentOff = percentOff;
  }

  checkout(): number {
    if (this.items.length === 0) throw new Error("cart is empty");

    const subtotal = this.items.reduce((sum, i) => sum + i.unitCents * i.quantity, 0);
    this.items = [];
    return Math.round(subtotal * (1 - this.percentOff / 100));
  }
}

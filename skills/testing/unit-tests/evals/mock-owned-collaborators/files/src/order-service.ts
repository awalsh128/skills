import type { OrderRepository } from "./order-repository";
import type { PaymentClient } from "./payment-client";
import { totalCents, type LineItem } from "./pricing";

export class OrderService {
  constructor(
    private readonly repository: OrderRepository,
    private readonly payments: PaymentClient
  ) {}

  async placeOrder(orderId: string, items: LineItem[]): Promise<number> {
    if (items.length === 0) throw new Error("empty order");

    if (this.repository.find(orderId)) throw new Error("duplicate order");

    const amountCents = totalCents(items);
    const result = await this.payments.charge(orderId, amountCents);
    if (!result.approved) throw new Error("payment declined");

    this.repository.save({ id: orderId, amountCents });
    return amountCents;
  }
}

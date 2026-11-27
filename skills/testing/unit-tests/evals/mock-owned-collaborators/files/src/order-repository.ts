export interface Order {
  id: string;
  amountCents: number;
}

export class OrderRepository {
  private readonly orders = new Map<string, Order>();

  save(order: Order): void {
    this.orders.set(order.id, order);
  }

  find(id: string): Order | undefined {
    return this.orders.get(id);
  }
}

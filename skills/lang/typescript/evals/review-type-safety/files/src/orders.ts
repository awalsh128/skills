type Status = "pending" | "shipped" | "cancelled";

interface Order {
  id: string;
  status: Status;
  total: number;
}

export function label(order: Order) {
  switch (order.status) {
    case "pending":
      return "Waiting";
    case "shipped":
      return "On the way";
  }
}

export function load(raw: any): Order {
  return raw as Order;
}

export async function notify(order: Order): Promise<void> {
  console.log(`notify ${order.id}`);
}

export function submit(order: Order) {
  notify(order);
  return order.id!;
}

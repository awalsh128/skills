import { API_BASE, ORDER_URL_RE, PAGE_SIZE } from "./constants.js";
import type { Order, OrderQuery } from "./types.js";

export function orderIdFromUrl(url: string): string | undefined {
  const m = url.match(ORDER_URL_RE);
  return m ? m[2] : undefined;
}

export function listUrl(q: OrderQuery): string {
  let s = API_BASE + "/orders?limit=" + PAGE_SIZE;
  if (q.status) s += "&status=" + q.status;
  if (q.page) s += "&page=" + q.page;
  return s;
}

export function copyOrder(o: Order): Order {
  return JSON.parse(JSON.stringify(o));
}

export const total = (o: Order) => o.items.reduce((a, i) => a + i.qty * i.price, 0);

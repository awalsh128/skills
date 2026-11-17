export interface Order {
  id: string;
  items: { sku: string; qty: number; price: number }[];
  createdAt: string;
}

export interface OrderQuery {
  status?: string;
  page?: number;
}

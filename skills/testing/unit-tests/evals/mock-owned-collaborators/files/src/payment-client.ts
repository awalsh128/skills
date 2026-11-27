export interface PaymentClient {
  charge(orderId: string, amountCents: number): Promise<{ approved: boolean }>;
}

export class HttpPaymentClient implements PaymentClient {
  constructor(private readonly baseUrl: string) {}

  async charge(orderId: string, amountCents: number): Promise<{ approved: boolean }> {
    const response = await fetch(`${this.baseUrl}/charges`, {
      method: "POST",
      body: JSON.stringify({ orderId, amountCents }),
    });
    if (!response.ok) throw new Error(`payment service returned ${response.status}`);

    return (await response.json()) as { approved: boolean };
  }
}

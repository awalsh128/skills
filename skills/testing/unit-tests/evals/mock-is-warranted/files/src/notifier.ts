export interface EmailGateway {
  send(to: string, subject: string, body: string): Promise<void>;
}

export interface Receipt {
  email: string;
  orderId: string;
  amountCents: number;
}

export class Notifier {
  constructor(private readonly gateway: EmailGateway) {}

  async sendReceipt(receipt: Receipt): Promise<void> {
    if (!receipt.email.includes("@")) throw new Error("invalid email");

    const amount = (receipt.amountCents / 100).toFixed(2);
    await this.gateway.send(receipt.email, `Receipt for order ${receipt.orderId}`, `You paid $${amount}.`);
  }
}

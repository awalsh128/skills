import type { Customer } from "./types.js";

export function displayName(customer: Customer): string {
  return `${customer.name} <${customer.email}>`;
}

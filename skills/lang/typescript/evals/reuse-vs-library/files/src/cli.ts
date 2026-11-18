#!/usr/bin/env node
import { parseArgs } from "node:util";

const { positionals } = parseArgs({ allowPositionals: true });
const [command] = positionals;

switch (command) {
  case "list":
    console.log("installed plugins: (none)");
    break;
  default:
    console.log("usage: plugkit <list>");
}

import * as core from "@actions/core";
import { runAction, type ActionInputs } from "./action.js";

function getInputs(): ActionInputs {
  return { key: core.getInput("key", { required: true }) };
}

async function main(): Promise<void> {
  try {
    const cache = { restore: async () => false };
    const outputs = await runAction(getInputs(), cache);
    core.setOutput("cache-hit", String(outputs.cacheHit));
  } catch (error) {
    core.setFailed(error instanceof Error ? error.message : String(error));
  }
}

void main();

import * as core from "@actions/core";

async function main(): Promise<void> {
  const token = core.getInput("token");
  const res = await fetch("https://api.example.com/release", { headers: { Authorization: token } });
  if (!res.ok) throw new Error("failed");

  core.setOutput("released", "true");
  core.setOutput("work-dir", "./work");
}

void main();

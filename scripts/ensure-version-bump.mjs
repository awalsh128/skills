// Pre-commit check: if the commit changes anything besides the version itself,
// plugin.json's version must differ from HEAD's. If it was not bumped by hand,
// the patch version is bumped and staged automatically. Installs and updates
// of the plugin key off this version.
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";

const PLUGIN_JSON = ".claude-plugin/plugin.json";

const git = (...args) => execFileSync("git", args, { encoding: "utf8" }).trim();

const staged = git("diff", "--cached", "--name-only").split("\n").filter(Boolean);
if (staged.length === 0) process.exit(0);

const versionOf = (json) => JSON.parse(json).version;

let headVersion;
try {
  headVersion = versionOf(git("show", `HEAD:${PLUGIN_JSON}`));
} catch {
  process.exit(0); // first commit or no prior plugin.json: nothing to compare
}

const stagedVersion = versionOf(git("show", `:${PLUGIN_JSON}`));
if (stagedVersion !== headVersion) process.exit(0);

const raw = readFileSync(PLUGIN_JSON, "utf8");
const [major, minor, patch] = headVersion.split(".").map(Number);
const next = `${major}.${minor}.${patch + 1}`;
writeFileSync(PLUGIN_JSON, raw.replace(`"version": "${headVersion}"`, `"version": "${next}"`));
git("add", PLUGIN_JSON);
console.log(`pre-commit: bumped plugin version ${headVersion} -> ${next}`);

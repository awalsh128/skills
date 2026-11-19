// Pre-commit check: if the commit changes anything, plugin.json's version must differ from HEAD's. If it was
// not bumped by hand, the patch version is bumped and staged automatically. Then the plugin's entry in
// marketplace.json is set to the same version and staged, so the marketplace lists the version users get.
// Installs and updates of the plugin key off plugin.json's version, which wins over the entry's when they
// differ; scripts/validate.py fails if they do.
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";

const PLUGIN_JSON = ".claude-plugin/plugin.json";
const MARKETPLACE_JSON = ".claude-plugin/marketplace.json";

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

let version = versionOf(git("show", `:${PLUGIN_JSON}`));
if (version === headVersion) {
  const [major, minor, patch] = headVersion.split(".").map(Number);
  version = `${major}.${minor}.${patch + 1}`;
  const raw = readFileSync(PLUGIN_JSON, "utf8");
  writeFileSync(PLUGIN_JSON, raw.replace(`"version": "${headVersion}"`, `"version": "${version}"`));
  git("add", PLUGIN_JSON);
  console.log(`pre-commit: bumped plugin version ${headVersion} -> ${version}`);
}

const pluginName = JSON.parse(readFileSync(PLUGIN_JSON, "utf8")).name;
const marketplace = JSON.parse(readFileSync(MARKETPLACE_JSON, "utf8"));
const entry = marketplace.plugins.find((plugin) => plugin.name === pluginName);
if (entry && entry.version !== version) {
  entry.version = version;
  writeFileSync(MARKETPLACE_JSON, `${JSON.stringify(marketplace, null, 2)}\n`);
  git("add", MARKETPLACE_JSON);
  console.log(`pre-commit: set ${MARKETPLACE_JSON} entry ${pluginName} to ${version}`);
}

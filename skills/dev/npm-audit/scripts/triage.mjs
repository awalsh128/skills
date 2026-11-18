// Summarises `npm audit --json` in one pass: each vulnerable package with its severity, whether it is a
// production or dev dependency, its direct parent, and whether a non-breaking fix exists.
// Usage: node triage.mjs [--omit=dev]   (run in the project root)
import { spawnSync } from "node:child_process";

const result = spawnSync("npm", ["audit", "--json", ...process.argv.slice(2)], {
  encoding: "utf8",
  maxBuffer: 64 * 1024 * 1024,
});
const report = JSON.parse(result.stdout || "{}");
if (report.error) {
  console.error(report.error.summary ?? JSON.stringify(report.error));
  process.exit(2);
}

const rank = { critical: 4, high: 3, moderate: 2, low: 1, info: 0 };
const rows = Object.values(report.vulnerabilities ?? {})
  .map((v) => ({
    name: v.name,
    severity: v.severity,
    direct: v.isDirect,
    range: v.range,
    via: v.via
      .map((x) => (typeof x === "string" ? x : x.title))
      .join("; ")
      .slice(0, 120),
    fix:
      v.fixAvailable === true
        ? "npm audit fix"
        : v.fixAvailable
          ? `breaking: ${v.fixAvailable.name}@${v.fixAvailable.version}`
          : "none",
  }))
  .sort((a, b) => rank[b.severity] - rank[a.severity] || a.name.localeCompare(b.name));

if (rows.length === 0) {
  console.log("0 vulnerabilities");
} else {
  console.table(rows);
}

console.log(JSON.stringify(report.metadata?.vulnerabilities ?? {}));

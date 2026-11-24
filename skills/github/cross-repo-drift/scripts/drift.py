#!/usr/bin/env python3
"""cross-repo-drift: audit and apply. Standard library only; shells out to gh, git and multi-gitter.

Authentication is the gh CLI's: no token is set by hand. Detection, verification and aggregation are plain code, so a clean audit costs no tokens.
"""

import argparse
import hashlib
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

USAGE = """cross-repo-drift: keep your repos in line with a standards source.

  drift.py deps [--install]                           check dependencies; --install fetches what needs no root
  drift.py repos                                      checklist of in-scope repos (current repo pre-checked)
  drift.py audit [--repos a,b|1,3|all] [--out report.json]   read-only report; changes nothing
  drift.py apply --repos a,b | --report report.json   open PRs for fixable findings (explicit target required)
  drift.py verify DIR --rule RULE [--attempt N]       re-run check; exit 0 only when RULE has no open finding
  drift.py automerge --repo NAME --pr N --reviewed    enable auto-merge where the repo requires the check
  drift.py tier fast|balanced|deep                    print the model alias for a tier
  drift.py tokens log|summary --run ID ...            per-tier token log, to tune the tier mapping

A bare call prints this text. audit is safe to schedule; apply refuses to run unattended.
"""


def die(message, code=2):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def run(cmd, cwd=None, env=None):
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, env={**os.environ, **(env or {})}, check=False
    )


# --- dependencies ----------------------------------------------------------------------------------------

# name -> (why, needed by). A missing one stops only the commands that need it.
DEPENDENCIES = {
    "git": ("clones the repos", "audit, apply"),
    "gh": ("authentication, repo discovery and PRs", "audit, apply"),
    "multi-gitter": ("runs the fix across repos and opens the PRs", "apply"),
    "jq": ("builds and reads findings JSON", "the gh-dev-powerpack check and fix scripts"),
}
INSTALL_DIR = Path.home() / ".local" / "bin"


def have(name):
    return bool(shutil.which(name)) or (INSTALL_DIR / name).exists()


def install_hint(name):
    """The command a person runs to install name themselves, for this platform."""
    mac = platform.system() == "Darwin"
    if name == "gh":
        return "brew install gh" if mac else "https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    if name == "multi-gitter":
        return "brew install lindell/multi-gitter/multi-gitter"
    if mac:
        return f"brew install {name}"
    managers = {"apt-get": "sudo apt-get install", "dnf": "sudo dnf install", "pacman": "sudo pacman -S",
                "zypper": "sudo zypper install"}
    manager = next((m for m in managers if shutil.which(m)), None)
    return f"{managers[manager]} {name}" if manager else f"install {name} with your package manager"


def install_multi_gitter():
    """Download the release for this platform with gh, verify its sha256 and put the binary in ~/.local/bin."""
    osname = {"Linux": "Linux", "Darwin": "Darwin"}.get(platform.system())
    arch = {"x86_64": "x86_64", "amd64": "x86_64", "arm64": "ARM64", "aarch64": "ARM64"}.get(platform.machine())
    if not osname or not arch:
        die(f"no prebuilt multi-gitter for {platform.system()} {platform.machine()}; install it yourself")
    with tempfile.TemporaryDirectory(prefix="cross-repo-drift-dl-") as tmp:
        for pattern in (f"multi-gitter_*_{osname}_{arch}.tar.gz", "checksums.txt"):
            got = run(["gh", "release", "download", "-R", "lindell/multi-gitter", "--pattern", pattern, "--dir", tmp])
            if got.returncode:
                die(f"could not download {pattern}: {got.stderr.strip()}")
        archive = next(Path(tmp).glob("*.tar.gz"))
        sums = dict(reversed(line.split()) for line in (Path(tmp) / "checksums.txt").read_text().splitlines()
                    if len(line.split()) == 2)
        if sums.get(archive.name) != hashlib.sha256(archive.read_bytes()).hexdigest():
            die(f"checksum mismatch for {archive.name}; not installing")
        with tarfile.open(archive) as tar:
            member = next((m for m in tar.getmembers() if m.isfile() and Path(m.name).name == "multi-gitter"), None)
            if not member:
                die("the archive has no multi-gitter binary")
            INSTALL_DIR.mkdir(parents=True, exist_ok=True)
            dest = INSTALL_DIR / "multi-gitter"
            dest.write_bytes(tar.extractfile(member).read())
            dest.chmod(0o755)
    print(f"installed multi-gitter {archive.name.split('_')[1]} to {dest} (sha256 verified)")
    if str(INSTALL_DIR) not in os.environ.get("PATH", "").split(os.pathsep):
        print(f"note: {INSTALL_DIR} is not on PATH")


def deps(install):
    """Report each dependency. With install, fetch what needs no root; hand the rest back to the person."""
    missing = [n for n in DEPENDENCIES if not have(n)]
    for name, (why, needed_by) in DEPENDENCIES.items():
        print(f"  {'missing' if name in missing else 'ok     '}  {name:<13} {why} ({needed_by})")
    if install and "multi-gitter" in missing:
        install_multi_gitter()
        missing.remove("multi-gitter")
    for name in missing:
        print(f"install {name}: {install_hint(name)}")
    return 1 if missing else 0


def need(name):
    """The command to run for a dependency apply needs, or stop with a pointer to `deps`."""
    if not have(name):
        die(f"{name} is not installed. Run `drift.py deps --install`, or install it yourself: {install_hint(name)}")
    return name if shutil.which(name) else str(INSTALL_DIR / name)


# --- discovery and classification -------------------------------------------------------------------------


def owner():
    """DRIFT_OWNER if set, else the account gh is logged in as."""
    if C.OWNER:
        return C.OWNER
    out = run(["gh", "api", "user", "-q", ".login"])
    if out.returncode or not out.stdout.strip():
        die("not logged in to gh: run `gh auth login`, or set DRIFT_OWNER")
    C.OWNER = out.stdout.strip()
    return C.OWNER


def current_repo():
    """Name of the repo the working directory belongs to, if it is a GitHub repo owned by owner()."""
    out = run(["gh", "repo", "view", "--json", "name,owner", "-q", '.owner.login + "/" + .name'])
    if out.returncode or "/" not in out.stdout:
        return None
    who, name = out.stdout.strip().split("/", 1)
    return name if who.lower() == owner().lower() else None


def gh_token():
    """The token gh already holds, handed to multi-gitter for this process only."""
    out = run(["gh", "auth", "token"])
    return out.stdout.strip() if not out.returncode and out.stdout.strip() else die(
        "gh has no token: run `gh auth login`")


def checklist(repos):
    here = current_repo()
    lines = [f"Repos for {owner()} (public, non-fork, non-archived). Pick by number, name, or 'all':"]
    for i, r in enumerate(repos, 1):
        mark = "x" if r["name"] == here else " "
        desc = (r.get("description") or "").strip()[:60]
        lines.append(f"  {i:>2}. [{mark}] {r['name']:<32} {desc}")
    return "\n".join(lines)


def resolve_picks(spec, repos):
    """Turn 'all', numbers and names from the checklist into repo names."""
    if spec.strip() == "all":
        return [r["name"] for r in repos]
    names = []
    for token in (s.strip() for s in spec.split(",") if s.strip()):
        names.append(repos[int(token) - 1]["name"] if token.isdigit() and 0 < int(token) <= len(repos) else token)
    return names


def discover():
    """Public, non-fork, non-archived repos of the owner, through REST (GraphQL is not always available)."""
    out = run(["gh", "api", "--paginate", "--slurp", f"users/{owner()}/repos?type=owner&per_page=100"])
    if out.returncode:
        die(f"could not list repos: {out.stderr.strip()}")
    repos = [r for page in json.loads(out.stdout) for r in page]
    keep = [r for r in repos if not r["fork"] and not r["archived"] and not r["private"]]
    return sorted(keep, key=lambda r: r["name"])


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {}


def classify(root):
    """Return (profile kind, release model) from the files a repo has. 'unclassified' blocks apply."""
    root = Path(root)
    has = lambda *names: any((root / n).exists() for n in names)  # noqa: E731
    pkg = read_json(root / "package.json")
    if has("action.yml", "action.yaml"):
        kind = "github-action"
    elif "vscode" in (pkg.get("engines") or {}):
        kind = "vscode-extension"
    elif has(".claude-plugin"):
        kind = "agent-plugin"
    elif pkg.get("bin"):
        kind = "node-cli"
    elif pkg:
        kind = "node-package"
    elif has("pyproject.toml", "setup.py"):
        kind = "python"
    elif has("Cargo.toml"):
        kind = "rust"
    elif has("go.mod"):
        kind = "go"
    else:
        kind = "unclassified"
    releases = has("release.config.js", "release.config.cjs", "release.config.mjs", ".releaserc",
                   ".releaserc.json", ".releaserc.yml", ".releaserc.yaml") or "release" in pkg
    return kind, "semantic-release" if releases else "none"


def split_findings(findings, overrides):
    """Findings whose rule has a standing exception are reported separately and never acted on."""
    excepted = {e.get("rule") for e in overrides.get("exceptions", [])}
    open_ = [f for f in findings if f.get("rule") not in excepted]
    return open_, [f for f in findings if f.get("rule") in excepted]


def run_check(root):
    """Run the configured check in root. Returns (findings or None, error or None)."""
    if not C.CHECK_CMD:
        return None, "DRIFT_CHECK_CMD is not set"
    out = run(shlex.split(C.CHECK_CMD), cwd=root)
    try:
        return json.loads(out.stdout)["findings"], None
    except (ValueError, KeyError, TypeError):
        return None, f"check did not print findings JSON (exit {out.returncode}): {out.stderr.strip()[:200]}"


def base_branch(root, overrides, default_branch):
    if overrides.get("integrationBranch"):
        return overrides["integrationBranch"]
    heads = run(["git", "ls-remote", "--heads", "origin", C.INTEGRATION_BRANCH], cwd=root).stdout
    return C.INTEGRATION_BRANCH if heads.strip() else default_branch


def audit_repo(name, default_branch, workdir):
    """Shallow-clone one repo into workdir, classify it and run check. Reads only; nothing is pushed."""
    dest = Path(workdir) / name
    url = C.CLONE_URL.format(owner=owner(), name=name)
    cloned = run(["git", "clone", "--depth", "1", "--quiet", url, str(dest)])
    if cloned.returncode:
        return {"repo": name, "status": "clone-failed", "error": cloned.stderr.strip()[:200]}
    overrides = read_json(dest / C.OVERRIDES_FILE)
    kind, release_model = classify(dest)
    profile = overrides.get("profile") or kind
    findings, error = run_check(dest)
    open_, excepted = split_findings(findings or [], overrides)
    status = "unclassified" if profile == "unclassified" else ("no-check" if error else "ok")
    return {
        "repo": name,
        "status": status,
        "profile": profile,
        "release_model": release_model,
        "base_branch": base_branch(dest, overrides, default_branch),
        "findings": open_,
        "excepted": excepted,
        **({"error": error} if error else {}),
    }


def audit(repo_names=None):
    repos = discover()
    if repo_names:
        repo_names = resolve_picks(",".join(repo_names), repos)
        known = {r["name"] for r in repos}
        unknown = [n for n in repo_names if n not in known]
        if unknown:
            die(f"not in scope (public, non-fork, non-archived): {', '.join(unknown)}")
        repos = [r for r in repos if r["name"] in repo_names]
    with tempfile.TemporaryDirectory(prefix="cross-repo-drift-") as work:
        with ThreadPoolExecutor(C.PARALLELISM) as pool:
            results = list(pool.map(lambda r: audit_repo(r["name"], r["default_branch"], work), repos))
    return {"generated": datetime.now(timezone.utc).isoformat(), "owner": owner(), "repos": results}


def summarize(report):
    lines = [f"{report['owner']}: {len(report['repos'])} repo(s)"]
    for r in report["repos"]:
        note = r.get("error") or ""
        lines.append(
            f"  {r['repo']:<32} {r['status']:<13} {r.get('profile', '-'):<17}"
            f" open={len(r.get('findings', []))} excepted={len(r.get('excepted', []))} {note}"
        )
    return "\n".join(lines)


# --- apply -----------------------------------------------------------------------------------------------


def work_items(args):
    """Return (repo result, finding) pairs to act on. Needs named repos or an approved report."""
    if bool(args.repos) == bool(args.report):
        die("apply needs exactly one of --repos or --report")
    if args.report:
        report = read_json(args.report)
        approved = {(a["repo"], a["rule"]) for a in report.get("approved", [])}
        if not approved:
            die("the report has no 'approved' list; add the repo and rule pairs you approve")
        pairs = [(r, f) for r in report.get("repos", []) for f in r.get("findings", [])]
        return [(r, f) for r, f in pairs if (r["repo"], f["rule"]) in approved]
    report = audit(args.repos.split(","))
    return [(r, f) for r in report["repos"] for f in r.get("findings", [])]


def apply(args):
    if os.environ.get("DRIFT_UNATTENDED"):
        die("apply does not run unattended; scheduled runs are audit-only")
    if not C.FIX_CMD:
        die("DRIFT_FIX_CMD is not set")
    items = work_items(args)
    skipped, jobs = [], []
    for repo, finding in items:
        ctype = C.CATEGORY_COMMIT_TYPES.get(finding.get("category"))
        if repo["status"] == "unclassified" or not ctype or not finding.get("fixable", True):
            skipped.append((repo["repo"], finding["rule"]))
        else:
            jobs.append((repo, finding, ctype))
    for repo, rule in skipped:
        print(f"skipped {repo}: {rule} (unclassified repo, unmapped category or not fixable)")
    mg = need("multi-gitter") if jobs else None
    token = {} if args.dry_run or not jobs else {"GITHUB_TOKEN": gh_token()}
    for repo, finding, ctype in jobs:
        category = finding["category"]
        command = [
            mg, "run", shlex.join([sys.executable, os.path.abspath(__file__), "fix-and-verify"]),
            "--repo", f"{owner()}/{repo['repo']}",
            "--branch", f"{C.BRANCH_PREFIX}{category}",
            "--base-branch", repo["base_branch"],
            "--pr-title", f"{ctype}: {finding['message']}"[:120],
            "--pr-body", f"Rule `{finding['rule']}` from the standards source. Opened by cross-repo-drift.",
            "--labels", C.LABEL,
            "--conflict-strategy", "replace",
        ]
        if args.dry_run:
            command.append("--dry-run")
        print("+", shlex.join(command))
        subprocess.run(command, env={**os.environ, **token, "DRIFT_RULE": finding["rule"]}, check=False)


def verify(root, rule, attempt):
    """Re-run check; the applier loop ends here, never on the agent's own say-so."""
    findings, error = run_check(root)
    if findings is None:
        die(error, 1)
    open_, _ = split_findings(findings, read_json(Path(root) / C.OVERRIDES_FILE))
    remaining = [f for f in open_ if f.get("rule") == rule]
    if not remaining:
        print(f"ok: {rule} has no open finding")
        return 0
    if attempt >= C.MAX_APPLIER_ATTEMPTS:
        print(f"still failing after {attempt} attempt(s): report the repo and leave it unchanged")
        return 2
    print(f"{len(remaining)} open finding(s) for {rule}; attempt {attempt} of {C.MAX_APPLIER_ATTEMPTS}")
    return 1


def fix_and_verify():
    """What multi-gitter runs inside each clone: apply the fix, then keep the change only if check passes.

    The rule arrives in DRIFT_RULE because multi-gitter would read a --rule flag as its own.
    """
    rule = os.environ.get("DRIFT_RULE") or die("DRIFT_RULE is not set")
    result = run(shlex.split(C.FIX_CMD), cwd=".", env={"DRIFT_RULE": rule})
    if result.returncode:
        print(result.stderr.strip()[:300], file=sys.stderr)
        return 1
    return 0 if verify(".", rule, C.MAX_APPLIER_ATTEMPTS) == 0 else 1


def automerge(repo, pr, reviewed):
    if not reviewed:
        die("auto-merge is enabled only after the reviewer passes; add --reviewed")
    info = run(["gh", "api", f"repos/{owner()}/{repo}/pulls/{pr}"])
    if info.returncode:
        die(info.stderr.strip())
    base = json.loads(info.stdout)["base"]["ref"]
    rules = run(["gh", "api", f"repos/{owner()}/{repo}/rules/branches/{base}"])
    if C.RELEASE_IMPACT_CHECK not in rules.stdout:
        print(f"skipped: {repo} does not require the '{C.RELEASE_IMPACT_CHECK}' check on {base}")
        return 0
    done = run(["gh", "pr", "merge", str(pr), "--repo", f"{owner()}/{repo}", "--auto", "--squash"])
    print(done.stdout.strip() or done.stderr.strip())
    return done.returncode


# --- token log -------------------------------------------------------------------------------------------


def token_log(run_id):
    return Path(tempfile.gettempdir()) / "cross-repo-drift" / f"{run_id}.jsonl"


def tokens(args):
    path = token_log(args.run)
    if args.action == "log":
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as f:
            f.write(json.dumps({"tier": args.tier, "input": args.input, "output": args.output}) + "\n")
        return 0
    totals = {}
    for line in path.read_text().splitlines() if path.exists() else []:
        row = json.loads(line)
        t = totals.setdefault(row["tier"], {"calls": 0, "input": 0, "output": 0})
        t["calls"] += 1
        t["input"] += row["input"]
        t["output"] += row["output"]
    print(json.dumps(totals, indent=2))
    return 0


# --- entry point -----------------------------------------------------------------------------------------


def main(argv):
    if not argv:
        print(USAGE)
        return 0
    p = argparse.ArgumentParser(prog="drift.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    dp = sub.add_parser("deps")
    dp.add_argument("--install", action="store_true")
    sub.add_parser("repos")
    a = sub.add_parser("audit")
    a.add_argument("--repos")
    a.add_argument("--out")
    ap = sub.add_parser("apply")
    ap.add_argument("--repos")
    ap.add_argument("--report")
    ap.add_argument("--dry-run", action="store_true")
    v = sub.add_parser("verify")
    v.add_argument("dir")
    v.add_argument("--rule", required=True)
    v.add_argument("--attempt", type=int, default=1)
    sub.add_parser("fix-and-verify")
    m = sub.add_parser("automerge")
    m.add_argument("--repo", required=True)
    m.add_argument("--pr", required=True, type=int)
    m.add_argument("--reviewed", action="store_true")
    t = sub.add_parser("tier")
    t.add_argument("tier", choices=sorted(C.TIER_MODELS))
    k = sub.add_parser("tokens")
    k.add_argument("action", choices=["log", "summary"])
    k.add_argument("--run", required=True)
    k.add_argument("--tier", choices=sorted(C.TIER_MODELS))
    k.add_argument("--input", type=int, default=0)
    k.add_argument("--output", type=int, default=0)
    args = p.parse_args(argv)

    if args.cmd == "deps":
        return deps(args.install)
    if args.cmd == "repos":
        print(checklist(discover()))
        return 0
    if args.cmd == "audit":
        report = audit(args.repos.split(",") if args.repos else None)
        if args.out:
            Path(args.out).write_text(json.dumps(report, indent=2))
        print(summarize(report))
        return 0
    if args.cmd == "apply":
        apply(args)
        return 0
    if args.cmd == "verify":
        return verify(args.dir, args.rule, args.attempt)
    if args.cmd == "fix-and-verify":
        return fix_and_verify()
    if args.cmd == "automerge":
        return automerge(args.repo, args.pr, args.reviewed)
    if args.cmd == "tier":
        print(C.TIER_MODELS[args.tier])
        return 0
    return tokens(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Settings for cross-repo-drift. This is the only file that holds an owner, a branch name or a model alias.

Every value can be overridden by an environment variable, so the skill works for any owner and any
standards source without editing code.
"""

import os

# Whose repos are audited. Empty means "the account `gh` is logged in as" (resolved in drift.owner()).
# Public, non-fork, non-archived repos only; private repos are out of scope.
OWNER = os.environ.get("DRIFT_OWNER", "")

# Where a repo is cloned from. {owner} and {name} are filled in; tests point this at a local path.
CLONE_URL = os.environ.get("DRIFT_CLONE_URL", "https://github.com/{owner}/{name}.git")

# The standards source supplies these two commands. Both run with the target repo as the working directory.
#   check: prints {"findings": [{"rule", "category", "path", "message", "fixable"}]} as JSON on stdout.
#   fix:   changes the working tree for the rule named in the DRIFT_RULE environment variable.
CHECK_CMD = os.environ.get("DRIFT_CHECK_CMD", "")
FIX_CMD = os.environ.get("DRIFT_FIX_CMD", "")

# Per-repo file where a repo records its profile, branches and permanent exceptions.
OVERRIDES_FILE = ".agents/standards-overrides.json"

# Branch and label that make a re-run find its own PRs instead of duplicating them.
BRANCH_PREFIX = "cross-repo-drift/"
LABEL = "cross-repo-drift"

# Used when a repo's overrides file does not name an integration branch and the repo has no staging branch.
INTEGRATION_BRANCH = "staging"

# Each rule category maps to one fixed commit type. A category not listed here is never applied or auto-merged.
CATEGORY_COMMIT_TYPES = {
    "pin": "ci",
    "workflow-syntax": "ci",
    "reflow": "style",
    "agent-config": "chore",
}

# Types that never release. The repo's own release config has the last word; the repo's CI check enforces it.
NON_RELEASING_TYPES = ("ci", "chore", "style", "docs", "test", "refactor")

# A PR touching any of these is never eligible for auto-merge, whatever its title says.
AUTOMERGE_PATH_DENYLIST = (
    ".github/workflows/release.yml",
    ".github/workflows/promote.yml",
    ".github/chainguard",
    ".github/rulesets",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
)

# Name of the required status check each repo's CI provides. Auto-merge is enabled only where it is required.
RELEASE_IMPACT_CHECK = "release impact"

# The applier gets this many attempts; the loop ends when check passes, never when the agent says it is done.
MAX_APPLIER_ATTEMPTS = 2

# Tiers map to Claude Code model aliases here and nowhere else.
TIER_MODELS = {"fast": "haiku", "balanced": "sonnet", "deep": "opus"}

# How many repos are cloned and checked at once.
PARALLELISM = 8

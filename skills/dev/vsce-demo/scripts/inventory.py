#!/usr/bin/env python3
"""List every feature a VS Code extension contributes or registers, as stable ids.

usage: inventory.py [extension-dir] [--json]

The ids come from two sources that should agree: `contributes` and `activationEvents` in package.json, and the
vscode API calls in the source. Each id is a feature that needs a demo scene or an explicit "not demoed" reason
in demo/COVERAGE.md; `check-coverage.py` enforces that. Standard library only.
"""
import json
import re
import sys
from pathlib import Path

# Plumbing that is not a feature on its own: commands are covered by their `command:` ids, and the rest only
# report state to code that is already listed.
IGNORED = {"registerCommand", "registerTextEditorCommand", "onDidDispose", "onDidReceiveMessage",
           "onDidChangeViewState", "onDidChangeVisibility", "onDidChangeConfiguration"}

SKIP_DIRS = {"node_modules", "out", "dist", "demo", "test", "tests", "__tests__", ".vscode-test", ".git", "media"}

# API calls that put something in front of the user. Each becomes `source:<name>`.
CALLS = [
    "registerCommand", "registerTextEditorCommand", "createDiagnosticCollection", "createWebviewPanel",
    "registerWebviewViewProvider", "registerWebviewPanelSerializer", "createTreeView", "registerTreeDataProvider",
    "createStatusBarItem", "createTestController", "createTextEditorDecorationType", "registerCustomEditorProvider",
    "registerUriHandler", "registerFileSystemProvider", "registerTaskProvider", "registerTerminalLinkProvider",
    "registerTerminalProfileProvider", "registerNotebookCellStatusBarItemProvider", "createOutputChannel",
    "createTerminal", "createChatParticipant", "registerTool", "registerAuthenticationProvider", "createSourceControl",
    "showInformationMessage", "showWarningMessage", "showErrorMessage", "showQuickPick", "showInputBox",
    "showOpenDialog", "showSaveDialog", "withProgress",
]
CALL_RE = re.compile(r"\b(" + "|".join(CALLS) + r"|register[A-Z]\w*Provider|registerDebug\w+|onDid[A-Z]\w+)\s*\(")
COMMAND_RE = re.compile(r"\bregister(?:Text[Ee]ditor)?Command\(\s*([A-Za-z_][\w.]*|[\"'`][^\"'`]+[\"'`])")
CONST_RE = re.compile(r"\bconst\s+([A-Za-z_]\w*)\s*(?::\s*[\w.]+)?\s*=\s*[\"'`]([^\"'`]+)[\"'`]")


def source_files(root: Path):
    for path in sorted(root.rglob("*.ts")) + sorted(root.rglob("*.tsx")) + sorted(root.rglob("*.js")):
        parts = set(path.relative_to(root).parts[:-1])
        if parts & SKIP_DIRS or path.name.endswith((".test.ts", ".spec.ts", ".d.ts")) or ".min." in path.name:
            continue
        if path.relative_to(root).parts[0] in {"src", "lib", "extension"} or len(path.relative_to(root).parts) == 1:
            yield path


def manifest_features(pkg: dict) -> dict:
    found = {}
    contributes = pkg.get("contributes", {})

    def add(feature, detail):
        found.setdefault(feature, []).append(detail)

    for command in contributes.get("commands", []):
        add(f"command:{command['command']}", command.get("title", ""))
    for menu, items in contributes.get("menus", {}).items():
        for item in items:
            add(f"menu:{menu}:{item.get('command') or item.get('submenu')}", "")
    for item in contributes.get("keybindings", []):
        add(f"keybinding:{item.get('command')}", item.get("key", ""))
    for key in contributes.get("configuration", {}).get("properties", {}) if isinstance(
            contributes.get("configuration"), dict) else []:
        add(f"setting:{key}", "")
    if isinstance(contributes.get("configuration"), list):
        for block in contributes["configuration"]:
            for key in block.get("properties", {}):
                add(f"setting:{key}", "")
    for container, items in contributes.get("viewsContainers", {}).items():
        for item in items:
            add(f"viewContainer:{item['id']}", container)
    for container, items in contributes.get("views", {}).items():
        for item in items:
            add(f"view:{item['id']}", container)
    for item in contributes.get("viewsWelcome", []):
        add(f"viewWelcome:{item.get('view')}", "")
    named = {
        "languages": ("language", "id"), "grammars": ("grammar", "scopeName"), "snippets": ("snippets", "language"),
        "walkthroughs": ("walkthrough", "id"), "customEditors": ("customEditor", "viewType"),
        "notebooks": ("notebook", "type"), "notebookRenderer": ("notebookRenderer", "id"),
        "debuggers": ("debugger", "type"), "taskDefinitions": ("task", "type"),
        "problemMatchers": ("problemMatcher", "name"), "chatParticipants": ("chatParticipant", "id"),
        "languageModelTools": ("lmTool", "name"), "themes": ("theme", "label"), "iconThemes": ("iconTheme", "label"),
        "productIconThemes": ("productIconTheme", "label"), "colors": ("color", "id"),
        "terminal": ("terminal", "profiles"), "authentication": ("authentication", "id"),
    }
    for key, value in contributes.items():
        if key in {"commands", "menus", "keybindings", "configuration", "viewsContainers", "views", "viewsWelcome"}:
            continue
        if key in named and isinstance(value, list):
            label, field = named[key]
            for item in value:
                add(f"{label}:{item.get(field, item.get('label', '?')) if isinstance(item, dict) else item}", "")
        elif key not in {"jsonValidation", "configurationDefaults"}:
            add(f"contributes:{key}", "")
    for event in pkg.get("activationEvents", []):
        add(f"activation:{event}", "")
    return found


def source_features(root: Path):
    features, registered, constants = {}, {}, {}
    files = list(source_files(root))
    for path in files:
        for name, value in CONST_RE.findall(path.read_text(errors="replace")):
            constants.setdefault(name, value)
    for path in files:
        text = path.read_text(errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith(("//", "*", "/*")):
                continue
            for match in CALL_RE.finditer(line):
                if match.group(1) in IGNORED:
                    continue
                features.setdefault(f"source:{match.group(1)}", []).append(f"{path.relative_to(root)}:{number}")
            for match in COMMAND_RE.finditer(line):
                arg = match.group(1)
                if arg[0] in "\"'`":
                    registered[arg[1:-1]] = f"{path.relative_to(root)}:{number}"
                else:
                    registered[constants.get(arg.split(".")[-1], f"?{arg}")] = f"{path.relative_to(root)}:{number}"
    return features, registered


def inventory(root: Path) -> dict:
    pkg = json.loads((root / "package.json").read_text())
    manifest = manifest_features(pkg)
    sources, registered = source_features(root)
    contributed = {f.split(":", 1)[1] for f in manifest if f.startswith("command:")}
    findings = []
    for command in sorted(contributed - set(registered)):
        findings.append(f"command {command} is in the manifest but no registerCommand call was found for it")
    for command, where in sorted(registered.items()):
        if command.startswith("?"):
            findings.append(f"registerCommand at {where} uses {command[1:]}, which could not be resolved to a string")
        elif command not in contributed:
            findings.append(f"command {command} is registered at {where} but not contributed in package.json")
    return {"features": {**manifest, **sources}, "findings": findings}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0] if args else ".").resolve()
    if not (root / "package.json").is_file():
        print(f"{root}: no package.json; pass the extension's folder", file=sys.stderr)
        return 2
    result = inventory(root)
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
        return 0
    print("| Feature | Scene | Driven by | Reset |\n| --- | --- | --- | --- |")
    for feature, details in sorted(result["features"].items()):
        note = ", ".join(sorted({d for d in details if d}))[:60]
        print(f"| `{feature}` | TODO | | |" + (f" <!-- {note} -->" if note else ""))
    if result["findings"]:
        print("\nFindings (the manifest and the source disagree):")
        for finding in result["findings"]:
            print(f"- {finding}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

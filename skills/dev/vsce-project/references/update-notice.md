# Update notice

A small module that shows the editor's own toast when a newer version of the extension is published, with
**Update**, **Dismiss** and **Never** buttons. Put it in its own file, named for its job (`update-notice.ts`),
and call it from `activate` in the entry file, which should only wire modules together.

## Behaviour

- **Update** installs the newer version with the editor's install command and the toast is done.
- **Dismiss**, or closing the toast, hides it for that version only. The next newer version asks again.
- **Never** turns the notice off for good by writing a setting, so the user can turn it back on in Settings.
- It uses `vscode.window.showInformationMessage`, which works in VS Code and in forks such as Cursor and
  VSCodium. Don't use an operating system toast API: the extension host can't reach it, and it breaks in
  remote and web sessions.
- Any failure (offline, timeout, bad response) is silent. A failed update check must never surface as an error
  to the user.

## Where the latest version comes from

The module reads `https://open-vsx.org/api/<publisher>/<name>`, a public JSON endpoint whose `version` field
is the latest release. Both registries receive the same `.vsix`, so it also tells VS Code users what the
Marketplace has. It needs the extension to be published to Open VSX; if it isn't, use GitHub's
`/repos/<owner>/<repo>/releases/latest` and strip the leading `v` from `tag_name`. The extension then makes an
outbound request on startup, so say so in the README and keep the setting visible.

## Setting

Declare it in `package.json` so **Never** has somewhere to live and users can see it:

```json
"contributes": {
  "configuration": {
    "properties": {
      "<name>.updateNotice.enabled": {
        "type": "boolean",
        "default": true,
        "description": "Show a notice when a newer version of this extension is available."
      }
    }
  }
}
```

## Module

Uses the platform's `fetch` and the small `semver` package (`npm i semver`, `npm i -D @types/semver`) instead
of a hand-rolled comparison; the bundler inlines `semver`.

```ts
import * as semver from "semver";
import * as vscode from "vscode";

const SECTION = "updateNotice";
const DISMISSED_VERSION_KEY = "updateNotice.dismissedVersion";
const REQUEST_TIMEOUT_MS = 5000;

/** Shows a toast when a newer version is published, unless the user turned it off or dismissed it. */
export async function notifyIfUpdateAvailable(context: vscode.ExtensionContext): Promise<void> {
  const { name, publisher, displayName, version } = context.extension.packageJSON as {
    name: string;
    publisher: string;
    displayName: string;
    version: string;
  };
  const config = vscode.workspace.getConfiguration(name, null).inspect<boolean>(`${SECTION}.enabled`);
  if (config?.globalValue === false) {
    return;
  }

  const latest = await fetchLatestVersion(publisher, name);
  if (latest === undefined || !semver.gt(latest, version)) {
    return;
  }

  if (context.globalState.get<string>(DISMISSED_VERSION_KEY) === latest) {
    return;
  }

  const choice = await vscode.window.showInformationMessage(
    `${displayName} ${latest} is available (you have ${version}).`,
    "Update",
    "Dismiss",
    "Never"
  );
  if (choice === "Update") {
    await vscode.commands.executeCommand("workbench.extensions.installExtension", `${publisher}.${name}`);
  } else if (choice === "Never") {
    await vscode.workspace
      .getConfiguration(name)
      .update(`${SECTION}.enabled`, false, vscode.ConfigurationTarget.Global);
  } else {
    // "Dismiss" or the toast was closed: stay quiet until a newer version appears.
    await context.globalState.update(DISMISSED_VERSION_KEY, latest);
  }
}

async function fetchLatestVersion(publisher: string, name: string): Promise<string | undefined> {
  try {
    const response = await fetch(`https://open-vsx.org/api/${publisher}/${name}`, {
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });
    if (!response.ok) {
      return undefined;
    }

    const { version } = (await response.json()) as { version?: string };
    return semver.valid(version) ?? undefined;
  } catch {
    return undefined;
  }
}
```

Call it without `await`, because the promise resolves only when the toast is dismissed and would otherwise
hold up activation:

```ts
export function activate(context: vscode.ExtensionContext) {
  void notifyIfUpdateAvailable(context);
  // ...register commands
}
```

## Notes

- `workbench.extensions.installExtension` is an editor command that takes an extension ID and installs the
  latest version from the registry the editor uses. It exists in VS Code (checked in 1.147); forks are
  untested, and the editor may ask for a reload afterwards.
- The `.globalValue === false` check reads only the user-level value, so a workspace setting can't switch the
  notice off for a user who didn't ask.
- A user on a pre-release (odd minor) who sees a lower stable version gets no toast, because `semver.gt` is
  false.
- Test the behaviour: no toast when disabled, offline, or the latest is not newer; one toast when newer;
  Dismiss stores the version and a repeat run stays quiet; Never writes the setting; Update runs the install
  command. Fake `fetch`, `globalState`, the configuration and `showInformationMessage`, the external
  boundaries, and use the real `semver`.

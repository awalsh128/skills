# Feature recipes

Per kind of feature: what to seed in `demo/workspace/`, how to drive it as a user would, what to assert, and
what to reset. Command IDs are VS Code internals; when one fails, find the current ID in the Keyboard
Shortcuts editor. `run`, `typeText`, `waitFor`, `placeCursor` and `openFile` are in `driver.md`.

## Worked example: Regex Explain

A real extension covered end to end, from its `package.json` and source (awalsh128/vscode-regex-explain). Its
manifest has one command in the palette and the editor context menu, one hover provider registered for every
scheme, four `language-overridable` settings, a webview panel and a cursor-following listener, and it
activates on `onStartupFinished`. The inventory becomes:

| Feature (source of truth)                                            | Scene                                                                                  | Resets                               |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------ |
| Hover on a regex literal (`registerHoverProvider`)                   | open `sample.ts`, cursor on the literal, `editor.action.showHover`                     | none                                 |
| Hover on a string passed to a regex API, in other languages          | same with `sample.py` (`re.compile(...)`); one scene per language family, not all nine | none                                 |
| Explain a selection in any file                                      | select a pattern in a `.txt` file, then hover the selection                            | selection                            |
| Backtracking warning with a safe equivalent (`checkBacktracking`)    | seed a catastrophic pattern; assert the hover text contains the warning                | none                                 |
| Command `regexExplain.explain`, palette                              | `runFromPalette("Regex Explain: Explain Regex")`                                       | panel                                |
| Same command, editor context menu (`menus.editor/context`)           | `editor.action.showContextMenu`, then xdotool to pick the item                         | menu, panel                          |
| Input for "a pattern you type" when nothing is selected or at cursor | run the command in an empty line; type the pattern into the input                      | input, panel                         |
| Explanation panel, a webview (`createWebviewPanel`)                  | `waitFor` the tab, hold while the diagram renders; test text typed in with xdotool     | panel closed                         |
| Follow the cursor (`regexExplain.panel.follow`, debounced listener)  | panel open, move the cursor between two regexes, wait past the 200 ms delay, hold      | panel closed                         |
| Follow off                                                           | set the setting `false`, move the cursor, show the panel did not change                | **the setting**, back to `undefined` |
| `regexExplain.hover.enabled` and `hover.languages`                   | before and after, plus a `[python]` override                                           | **global and `[python]` values**     |
| Activation (`onStartupFinished`)                                     | not a scene: the extension is already active when the window settles                   | n/a                                  |

Three things this example shows about the inventory:

- A setting is a feature when it changes what is visible, so it gets a before and after scene, and the reset
  clears every key plus language overrides. The manifest lists the keys, so `resetState` finds them.
- The panel is a singleton with a debounce, so scenes wait on the panel tab, not on time, and always close it.
- Several rows share one fixture file. Seed one small file per language, not one file with everything.

## Commands and menus

- **Palette:** `runFromPalette(title)`. The title is `category: title` as the palette shows it. A command with
  a `when` clause only appears in the palette when the context holds, so seed the state first.
- **Context menus** (`editor/context`, `explorer/context`, `view/title`, `view/item/context`): the menu is
  native, so the API opens it (`editor.action.showContextMenu`) but cannot pick an item; use `xdotool`.
- **Keybindings:** `xdotool key ctrl+alt+r`, so the viewer sees the real shortcut. Without it, say the key in
  the README text, not the GIF.
- **Quick picks and input boxes the extension opens:** `workbench.action.quickOpenSelectNext` then
  `workbench.action.acceptSelectedQuickOpenItem` for picks; typing into an input box needs
  `xdotool type --delay 80`, because the `type` command targets editors, not the input widget.
- **Notifications and message buttons:** `showInformationMessage` appears in a toast the API cannot click.
  Hold on it, and use `xdotool` for a button. Clear with `notifications.clearAll`.

## Diagnostics, code actions, code lens

- **Diagnostics:** seed a file that triggers them. Assert with `vscode.languages.getDiagnostics(uri)`, show
  the squiggle, then `workbench.actions.view.problems`. Show the trigger the extension really uses: type a
  violation live, or save (`workbench.action.files.save` on the temp copy only).
- **Code actions and quick fixes:** put the cursor on the diagnostic, assert
  `vscode.executeCodeActionProvider`, open `editor.action.quickFix`, accept with `acceptSelectedCodeAction`,
  then assert the text changed. Refactors: `editor.action.refactor`; source actions:
  `editor.action.sourceAction`. Fix-on-save is a setting (`editor.codeActionsOnSave`), so set it and reset it.
- **Code lens and inlay hints:** visible once the file opens; assert `vscode.executeCodeLensProvider`. Run a
  lens by clicking with `xdotool`, or show the command's effect.

## Language providers

All of these are asserted with a `vscode.execute*Provider` command and shown through the user's own gesture.

- **Hover:** cursor on the symbol, `editor.action.showHover`, assert `vscode.executeHoverProvider`. Hover
  closes on any key or mouse move, so hold still. An open hover does not close when a setting turns it off, so
  a before-and-after scene hides it first (`editor.action.hideHover`); the provider assertion passes while the
  old widget is still on screen, so check the frame. Other extensions' hovers appear too; with only yours
  loaded (`--disable-extensions`) that is not a problem, and filter on text unique to yours when asserting.
- **Completion:** type the trigger characters; assert `vscode.executeCompletionItemProvider`; pick with
  `acceptSelectedSuggestion`, move with `selectNextSuggestion`. Inline completions:
  `editor.action.inlineSuggest.trigger` and `editor.action.inlineSuggest.commit`.
- **Signature help:** `editor.action.triggerParameterHints`.
- **Definition, references, rename:** `editor.action.revealDefinition`, `editor.action.goToReferences`,
  `editor.action.peekDefinition`, `editor.action.rename`. The rename box is an input; if `type` does not reach
  it, use `xdotool`.
- **Symbols and outline:** `workbench.action.gotoSymbol`, `workbench.action.showAllSymbols`, `outline.focus`.
- **Formatting:** `editor.action.formatDocument` or `editor.action.formatSelection`; assert the text changed.
- **Document links, highlights, folding, selection ranges:** `editor.action.openLink`, `editor.foldAll`,
  `editor.action.smartSelect.expand`.
- **Other languages' built-in noise:** opening a language the profile has a built-in extension for can raise
  its own toast (PHP says it cannot find an installation to validate with). Silence it in the profile
  (`php.validate.enable`) and look for it in the frames.
- **Language server:** the first request is slow. `waitFor` a real result, never a sleep, and start filming
  only after it is warm (the driver's ready file is written after reset and settle, so warm it in the runner
  before that if needed).

## Languages, grammars, themes, snippets

- **Language, grammar, semantic tokens:** open a sample of the language and hold on it; there is nothing to
  assert, so verify by frame. Comment toggling: `editor.action.commentLine`; bracket pairs are visible by
  typing an opener.
- **Snippets:** type the prefix, `acceptSelectedSuggestion` (or the `tab` command), then
  `jumpToNextSnippetPlaceholder`.
- **Themes and icon themes:** switch by updating `workbench.colorTheme` / `workbench.iconTheme`, then reset
  it. This is the one scene allowed to leave the fixed look, and it must put the look back.

## Views, panels and editors

- **Tree views and view containers:** `workbench.view.extension.<containerId>` opens the container,
  `<viewId>.focus` focuses a view. There is no API to read tree contents, so verify by frame; an effect (a
  command that adds an item) can be asserted through the state it changes.
- **Webview panels:** find the tab with `findWebviewTab(viewType)` (the tab's view type carries a prefix, so
  match with `includes`). The DOM is out of reach of the API, so choose by what the scene needs:
  - Render only (a diagram, a chart, a Markdown preview): wait for the tab, then give the page the time it
    takes to paint, and confirm by frame. Prefer a signal the extension already sends over a fixed sleep.
  - Interaction: send what the page would send through the extension's own message path, or click and type
    with `xdotool` at positions that stay stable because the window and layout are fixed.
  - Webviews use the theme's CSS variables, so the fixed theme is part of the result.
- **Webview views (sidebar):** `<viewId>.focus`. **Custom editors and notebooks:** `vscode.openWith` with the
  file and the view type; run a cell with `notebook.cell.execute`.
- **Status bar items:** always visible, so frame the scene on them and click through the command. **Editor
  decorations:** visible after the trigger; hold on them.
- **Settings:** `workbench.action.openSettings` with `@ext:<publisher>.<name>` shows the contributed UI. A
  setting that changes behavior gets its own before and after scene (see the worked example).
- **Walkthroughs:** `workbench.action.openWalkthrough` with `<publisher>.<name>#<walkthroughId>`.

## Workbench integrations

- **Tasks and problem matchers:** `workbench.action.tasks.runTask`; the Problems view shows the matches.
- **Terminal:** `workbench.action.terminal.new`; link providers need text printed to the terminal.
- **Debug:** `vscode.debug.addBreakpoints`, then `vscode.debug.startDebugging`; assert
  `vscode.debug.activeDebugSession`. Stop it in reset.
- **Testing:** `testing.runAll`, `workbench.view.testing.focus`.
- **Source control, file system providers:** open the SCM view with `workbench.view.scm`; add a custom scheme
  folder with `vscode.workspace.updateWorkspaceFolders`, and remove it in reset.
- **Output channels:** `workbench.action.output.toggleOutput`.
- **Chat participants and language model tools:** `workbench.action.chat.open` with `{ query: "@name ..." }`.
  They need a signed-in model, so they are normally "not demoed" in CI. Record locally or list the reason.
- **Authentication providers and anything needing credentials or an outside service:** list under "not demoed"
  with the reason. Never put a real token on screen.

## Reset reminders by feature

- Setting changed: clear the key and its `[language]` override.
- Webview or panel opened: close it, including singletons the extension keeps.
- Text edited: revert, never save, outside the temp copy.
- Cursor or selection moved: place it back so the next scene starts equal.
- Debug session, task, terminal or custom workspace folder started: stop or remove it.
- Notification or quick pick left open: `notifications.clearAll`, then `workbench.action.closeQuickOpen`.
- Extension state (`globalState`, `workspaceState`, secrets): nothing outside clears it, so a fresh profile
  per run is the reset. Seed the "returning user" state in the profile when that is the scene.
